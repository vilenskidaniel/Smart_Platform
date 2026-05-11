#include "modules/irrigation/IrrigationController.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

namespace smart_platform::modules::irrigation {

namespace {

void copyText(char* destination, size_t destinationSize, const char* source) {
    if (destination == nullptr || destinationSize == 0) {
        return;
    }

    snprintf(destination, destinationSize, "%s", source != nullptr ? source : "");
}

bool sameText(const char* left, const char* right) {
    if (left == nullptr || right == nullptr) {
        return false;
    }

    return strcmp(left, right) == 0;
}

float clampPercent(float value) {
    if (value < 0.0f) {
        return 0.0f;
    }
    if (value > 100.0f) {
        return 100.0f;
    }
    return value;
}

}  // namespace

IrrigationController::IrrigationController()
    : outputsEnabled_(kEnableRealOutputsByDefault),
      dryRun_(!kEnableRealOutputsByDefault),
      pumpOn_(false),
      faultLatched_(false),
      automaticModeEnabled_(false),
      serviceModeActive_(false),
      activeZoneIndex_(-1),
      wateringUntilMs_(0),
      bootMs_(0),
      lastUpdateMs_(0),
      completedCycles_(0),
      activeRunSource_(RunSource::None),
      environment_ {},
      eventHead_(0),
      eventCount_(0) {
    memset(zones_, 0, sizeof(zones_));
    memset(eventQueue_, 0, sizeof(eventQueue_));
}

void IrrigationController::begin() {
    seedZones();
    bootMs_ = millis();
    lastUpdateMs_ = bootMs_;

    // В dry-run режиме аппаратные пины не трогаем.
    // Это намеренная мера безопасности, потому что в новой платформе еще не утверждены
    // драйверы клапанов и уровень активации реального железа.
    if (outputsEnabled_) {
        pinMode(kPumpPin, OUTPUT);
        digitalWrite(kPumpPin, LOW);

        for (size_t index = 0; index < kZoneCount; ++index) {
            pinMode(kValvePins[index], OUTPUT);
            digitalWrite(kValvePins[index], LOW);
        }
    }
}

void IrrigationController::update() {
    const uint32_t now = millis();
    const uint32_t deltaMs = now - lastUpdateMs_;

    if (deltaMs < kControllerUpdateIntervalMs) {
        return;
    }

    lastUpdateMs_ = now;

    if (activeZoneIndex_ >= 0 && static_cast<int32_t>(now - wateringUntilMs_) >= 0) {
        finishActiveRun("duration completed");
    }

    updateDryRunSimulation(deltaMs);
    updateEnvironmentSimulation(deltaMs);
    updateAutomaticMode();
    refreshAllZonePresentation();
    applyOutputs();
}

void IrrigationController::setAutomaticModeEnabled(bool enabled) {
    if (automaticModeEnabled_ == enabled) {
        return;
    }

    automaticModeEnabled_ = enabled;
    enqueueLogEvent("info",
                    "irrigation_auto_mode_changed",
                    enabled ? "automatic irrigation mode enabled"
                            : "automatic irrigation mode disabled",
                    enabled ? "auto_mode=enabled" : "auto_mode=disabled");
}

void IrrigationController::setServiceModeActive(bool active) {
    if (serviceModeActive_ == active) {
        return;
    }

    serviceModeActive_ = active;
    if (serviceModeActive_ && activeZoneIndex_ >= 0) {
        finishActiveRun("service mode entered");
    } else if (!serviceModeActive_ && activeRunSource_ == RunSource::ServiceTest) {
        finishActiveRun("service mode exited");
    }

    enqueueLogEvent("info",
                    "irrigation_service_mode_changed",
                    active ? "irrigation service mode enabled"
                           : "irrigation service mode disabled",
                    active ? "service_mode=enabled" : "service_mode=disabled");
}

CommandResult IrrigationController::startManualZone(size_t zoneIndex, uint32_t durationMs) {
    return startZone(zoneIndex, durationMs, RunSource::Manual, false);
}

CommandResult IrrigationController::startServiceZone(size_t zoneIndex, uint32_t durationMs) {
    if (!serviceModeActive_) {
        return CommandResult::ServiceModeRequired;
    }

    return startZone(zoneIndex, durationMs, RunSource::ServiceTest, true);
}

CommandResult IrrigationController::stopAll() {
    if (activeZoneIndex_ < 0) {
        return CommandResult::IdleAlready;
    }

    finishActiveRun("manual stop requested");
    return CommandResult::Accepted;
}

bool IrrigationController::applyServiceSensorProfile(size_t zoneIndex, const char* profile) {
    if (zoneIndex >= kZoneCount || profile == nullptr || profile[0] == '\0') {
        return false;
    }

    ZoneStatus& zone = zones_[zoneIndex];
    const uint32_t now = millis();

    if (sameText(profile, "dry")) {
        zone.sensorFault = false;
        zone.soilMoisturePercent = 18.0f;
    } else if (sameText(profile, "wet")) {
        zone.sensorFault = false;
        zone.soilMoisturePercent = 72.0f;
    } else if (sameText(profile, "nominal")) {
        zone.sensorFault = false;
        zone.soilMoisturePercent = 44.0f + static_cast<float>(zoneIndex);
    } else if (sameText(profile, "fault")) {
        zone.sensorFault = true;
        if (activeZoneIndex_ == static_cast<int>(zoneIndex)) {
            finishActiveRun("sensor fault injected");
        }
    } else if (sameText(profile, "restore")) {
        zone.sensorFault = false;
        if (zone.soilMoisturePercent < 0.0f) {
            zone.soilMoisturePercent = 42.0f;
        }
    } else {
        return false;
    }

    zone.sensorSimulated = true;
    zone.lastReadingMs = now;
    refreshZonePresentation(zone);

    char details[96];
    snprintf(details,
             sizeof(details),
             "zone=%u, profile=%s, soil_moisture=%.1f",
             static_cast<unsigned>(zoneIndex),
             profile,
             static_cast<double>(zone.soilMoisturePercent));
    enqueueLogEvent("info",
                    "irrigation_sensor_profile_applied",
                    "service sensor profile applied",
                    details);
    return true;
}

ModuleStatus IrrigationController::status() const {
    ModuleStatus moduleStatus;
    moduleStatus.outputsEnabled = outputsEnabled_;
    moduleStatus.dryRun = dryRun_;
    moduleStatus.pumpOn = pumpOn_;
    moduleStatus.faultLatched = faultLatched_;
    moduleStatus.automaticModeEnabled = automaticModeEnabled_;
    moduleStatus.serviceModeActive = serviceModeActive_;
    moduleStatus.activeZoneIndex = activeZoneIndex_;
    moduleStatus.uptimeMs = millis() - bootMs_;
    moduleStatus.completedCycles = completedCycles_;
    moduleStatus.activeRunSource = activeRunSource_;

    float driest = 101.0f;
    for (size_t index = 0; index < kZoneCount; ++index) {
        const ZoneStatus& zone = zones_[index];
        if (zone.sensorFault) {
            moduleStatus.sensorFaultPresent = true;
        }

        if (!zone.enabled || zone.sensorFault) {
            continue;
        }

        if (zone.soilMoisturePercent < driest) {
            driest = zone.soilMoisturePercent;
            moduleStatus.driestZoneIndex = static_cast<int>(index);
            moduleStatus.driestMoisturePercent = zone.soilMoisturePercent;
        }
    }

    if (faultLatched_) {
        moduleStatus.state = ModuleState::Fault;
    } else if (activeZoneIndex_ >= 0) {
        moduleStatus.state = ModuleState::Watering;
        moduleStatus.activeZoneRemainingMs = zones_[activeZoneIndex_].remainingMs;
    } else {
        moduleStatus.state = ModuleState::Idle;
        moduleStatus.activeZoneRemainingMs = 0;
    }

    return moduleStatus;
}

const ZoneStatus* IrrigationController::zoneAt(size_t index) const {
    if (index >= kZoneCount) {
        return nullptr;
    }

    return &zones_[index];
}

size_t IrrigationController::zoneCount() const {
    return kZoneCount;
}

const EnvironmentStatus& IrrigationController::environment() const {
    return environment_;
}

bool IrrigationController::pollLogEvent(ControllerLogEvent& outEvent) {
    if (eventCount_ == 0) {
        return false;
    }

    const size_t oldestIndex = (eventHead_ + kLogEventQueueSize - eventCount_) % kLogEventQueueSize;
    outEvent = eventQueue_[oldestIndex];
    --eventCount_;
    return true;
}

const char* IrrigationController::zoneStateName(ZoneState value) {
    switch (value) {
        case ZoneState::Idle:
            return "idle";
        case ZoneState::Watering:
            return "watering";
        case ZoneState::Fault:
            return "fault";
        case ZoneState::Disabled:
            return "disabled";
        default:
            return "idle";
    }
}

const char* IrrigationController::moduleStateName(ModuleState value) {
    switch (value) {
        case ModuleState::Idle:
            return "idle";
        case ModuleState::Watering:
            return "watering";
        case ModuleState::Fault:
            return "fault";
        default:
            return "idle";
    }
}

const char* IrrigationController::runSourceName(RunSource value) {
    switch (value) {
        case RunSource::Manual:
            return "manual";
        case RunSource::Automatic:
            return "automatic";
        case RunSource::ServiceTest:
            return "service_test";
        case RunSource::None:
        default:
            return "none";
    }
}

const char* IrrigationController::commandResultName(CommandResult value) {
    switch (value) {
        case CommandResult::Accepted:
            return "accepted";
        case CommandResult::Busy:
            return "busy";
        case CommandResult::InvalidZone:
            return "invalid_zone";
        case CommandResult::InvalidArguments:
            return "invalid_arguments";
        case CommandResult::FaultLatched:
            return "fault_latched";
        case CommandResult::ZoneDisabled:
            return "zone_disabled";
        case CommandResult::SensorFault:
            return "sensor_fault";
        case CommandResult::ServiceModeRequired:
            return "service_mode_required";
        case CommandResult::IdleAlready:
            return "idle_already";
        default:
            return "invalid_arguments";
    }
}

CommandResult IrrigationController::startZone(size_t zoneIndex,
                                              uint32_t durationMs,
                                              RunSource runSource,
                                              bool allowSensorFault) {
    if (faultLatched_) {
        return CommandResult::FaultLatched;
    }

    if (zoneIndex >= kZoneCount) {
        return CommandResult::InvalidZone;
    }

    ZoneStatus& zone = zones_[zoneIndex];
    if (!zone.enabled) {
        return CommandResult::ZoneDisabled;
    }

    if (zone.sensorFault && !allowSensorFault) {
        return CommandResult::SensorFault;
    }

    if (durationMs == 0 || durationMs > kMaxManualDurationMs) {
        return CommandResult::InvalidArguments;
    }

    if (activeZoneIndex_ >= 0 && static_cast<size_t>(activeZoneIndex_) != zoneIndex) {
        return CommandResult::Busy;
    }

    activeZoneIndex_ = static_cast<int>(zoneIndex);
    wateringUntilMs_ = millis() + durationMs;
    activeRunSource_ = runSource;
    zone.remainingMs = durationMs;
    zone.valveOpen = true;
    pumpOn_ = true;
    refreshZonePresentation(zone);

    char details[96];
    snprintf(details,
             sizeof(details),
             "zone=%u, duration_ms=%lu, source=%s",
             static_cast<unsigned>(zoneIndex),
             static_cast<unsigned long>(durationMs),
             runSourceName(runSource));
    enqueueLogEvent("info", "irrigation_zone_started", "irrigation cycle started", details);
    return CommandResult::Accepted;
}

void IrrigationController::finishActiveRun(const char* stopReason) {
    if (activeZoneIndex_ < 0) {
        return;
    }

    const int finishedZoneIndex = activeZoneIndex_;
    const RunSource finishedSource = activeRunSource_;

    for (size_t index = 0; index < kZoneCount; ++index) {
        zones_[index].remainingMs = 0;
        zones_[index].valveOpen = false;
    }

    activeZoneIndex_ = -1;
    activeRunSource_ = RunSource::None;
    wateringUntilMs_ = 0;
    pumpOn_ = false;
    ++completedCycles_;
    resetOutputs();
    refreshAllZonePresentation();

    char details[112];
    snprintf(details,
             sizeof(details),
             "zone=%d, source=%s, reason=%s",
             finishedZoneIndex,
             runSourceName(finishedSource),
             stopReason != nullptr ? stopReason : "stopped");
    enqueueLogEvent("info", "irrigation_zone_stopped", "irrigation cycle finished", details);
}

void IrrigationController::seedZones() {
    for (size_t index = 0; index < kZoneCount; ++index) {
        zones_[index] = ZoneStatus {};
        zones_[index].index = index;

        char zoneId[16];
        char title[24];
        snprintf(zoneId, sizeof(zoneId), "zone_%u", static_cast<unsigned>(index + 1));
        snprintf(title, sizeof(title), "Zone %u", static_cast<unsigned>(index + 1));

        copyText(zones_[index].id, sizeof(zones_[index].id), zoneId);
        copyText(zones_[index].title, sizeof(zones_[index].title), title);
        zones_[index].state = ZoneState::Idle;
        zones_[index].soilMoisturePercent = 38.0f + static_cast<float>(index) * 4.0f;
        zones_[index].targetMoisturePercent = 45.0f;
        zones_[index].remainingMs = 0;
        zones_[index].valveOpen = false;
        zones_[index].enabled = true;
        zones_[index].autoEnabled = true;
        zones_[index].sensorFault = false;
        zones_[index].sensorSimulated = true;
        zones_[index].lastReadingMs = millis();
    }
}

void IrrigationController::applyOutputs() {
    if (!outputsEnabled_) {
        return;
    }

    digitalWrite(kPumpPin, pumpOn_ ? HIGH : LOW);

    for (size_t index = 0; index < kZoneCount; ++index) {
        const bool valveOpen = activeZoneIndex_ == static_cast<int>(index) && pumpOn_;
        digitalWrite(kValvePins[index], valveOpen ? HIGH : LOW);
    }
}

void IrrigationController::resetOutputs() {
    if (!outputsEnabled_) {
        return;
    }

    digitalWrite(kPumpPin, LOW);
    for (size_t index = 0; index < kZoneCount; ++index) {
        digitalWrite(kValvePins[index], LOW);
    }
}

void IrrigationController::updateDryRunSimulation(uint32_t deltaMs) {
    // Это сознательная симуляция для первого продуктового контура.
    // Она нужна, чтобы зона, датчик и auto-mode уже жили как пользовательские сущности,
    // даже пока реальные сенсоры и водяной тракт не подключены к стенду.
    const float deltaSeconds = static_cast<float>(deltaMs) / 1000.0f;
    const uint32_t now = millis();

    for (size_t index = 0; index < kZoneCount; ++index) {
        ZoneStatus& zone = zones_[index];
        zone.lastReadingMs = now;

        if (activeZoneIndex_ == static_cast<int>(index) && zone.state == ZoneState::Watering) {
            if (!zone.sensorFault && zone.soilMoisturePercent < 99.0f) {
                zone.soilMoisturePercent = clampPercent(zone.soilMoisturePercent + 2.0f * deltaSeconds);
            }

            if (wateringUntilMs_ > now) {
                zone.remainingMs = wateringUntilMs_ - now;
            } else {
                zone.remainingMs = 0;
            }
            continue;
        }

        zone.remainingMs = 0;
        zone.valveOpen = false;

        if (!zone.sensorFault && zone.soilMoisturePercent > 25.0f) {
            zone.soilMoisturePercent = clampPercent(zone.soilMoisturePercent - 0.12f * deltaSeconds);
        }
    }
}

void IrrigationController::updateEnvironmentSimulation(uint32_t deltaMs) {
    const float deltaSeconds = static_cast<float>(deltaMs) / 1000.0f;

    if (pumpOn_) {
        environment_.airHumidityPercent =
            clampPercent(environment_.airHumidityPercent + 0.8f * deltaSeconds);
        environment_.airTemperatureC -= 0.05f * deltaSeconds;
        environment_.waterReservePercent =
            clampPercent(environment_.waterReservePercent - 0.35f * deltaSeconds);
        return;
    }

    const float humidityError = 49.0f - environment_.airHumidityPercent;
    environment_.airHumidityPercent =
        clampPercent(environment_.airHumidityPercent + humidityError * 0.04f * deltaSeconds);

    const float temperatureError = 24.0f - environment_.airTemperatureC;
    environment_.airTemperatureC += temperatureError * 0.05f * deltaSeconds;
}

void IrrigationController::updateAutomaticMode() {
    if (!automaticModeEnabled_ || serviceModeActive_ || faultLatched_ || activeZoneIndex_ >= 0) {
        return;
    }

    const int driestZoneIndex = findDriestAutoEligibleZone();
    if (driestZoneIndex < 0) {
        return;
    }

    startZone(static_cast<size_t>(driestZoneIndex),
              kAutomaticWateringDurationMs,
              RunSource::Automatic,
              false);
}

void IrrigationController::refreshZonePresentation(ZoneStatus& zone) {
    if (!zone.enabled) {
        zone.state = ZoneState::Disabled;
        return;
    }

    if (activeZoneIndex_ == static_cast<int>(zone.index) && pumpOn_) {
        zone.state = ZoneState::Watering;
        return;
    }

    if (zone.sensorFault) {
        zone.state = ZoneState::Fault;
        return;
    }

    zone.state = ZoneState::Idle;
}

void IrrigationController::refreshAllZonePresentation() {
    for (size_t index = 0; index < kZoneCount; ++index) {
        refreshZonePresentation(zones_[index]);
    }
}

int IrrigationController::findDriestAutoEligibleZone() const {
    int candidateIndex = -1;
    float candidateMoisture = 101.0f;

    for (size_t index = 0; index < kZoneCount; ++index) {
        const ZoneStatus& zone = zones_[index];
        if (!zone.enabled || !zone.autoEnabled || zone.sensorFault) {
            continue;
        }

        const float autoTrigger = zone.targetMoisturePercent - kAutomaticTriggerMarginPercent;
        if (zone.soilMoisturePercent > autoTrigger) {
            continue;
        }

        if (zone.soilMoisturePercent < candidateMoisture) {
            candidateMoisture = zone.soilMoisturePercent;
            candidateIndex = static_cast<int>(index);
        }
    }

    return candidateIndex;
}

void IrrigationController::enqueueLogEvent(const char* level,
                                           const char* type,
                                           const char* message,
                                           const char* details) {
    ControllerLogEvent event {};
    copyText(event.level, sizeof(event.level), level);
    copyText(event.type, sizeof(event.type), type);
    copyText(event.message, sizeof(event.message), message);
    copyText(event.details, sizeof(event.details), details);

    eventQueue_[eventHead_] = event;
    eventHead_ = (eventHead_ + 1) % kLogEventQueueSize;
    if (eventCount_ < kLogEventQueueSize) {
        ++eventCount_;
    }
}

}  // namespace smart_platform::modules::irrigation
