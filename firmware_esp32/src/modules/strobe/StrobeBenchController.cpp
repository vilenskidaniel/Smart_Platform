#include "modules/strobe/StrobeBenchController.h"

#include <string.h>

namespace smart_platform::modules::strobe {

namespace {

constexpr PresetDefinition kPresets[] = {
    {
        "bringup_safe",
        "Safe bring-up",
        "Очень короткий стартовый тест после переподключения",
        PatternType::Burst,
        3,
        20,
        980,
        PresetRisk::Low,
    },
    {
        "bench_safe",
        "Bench safe",
        "Консервативный пакет вспышек для проверки стенда",
        PatternType::Burst,
        10,
        50,
        950,
        PresetRisk::Low,
    },
    {
        "driver_check",
        "Driver check",
        "Одна заметная вспышка для проверки цепи управления",
        PatternType::Pulse,
        0,
        120,
        0,
        PresetRisk::Low,
    },
    {
        "thermal_probe",
        "Thermal probe",
        "Более теплая серия импульсов для наблюдения за охлаждением",
        PatternType::Burst,
        12,
        120,
        880,
        PresetRisk::Medium,
    },
};

}  // namespace

StrobeBenchController::StrobeBenchController(uint8_t gatePin, bool activeHigh)
    : gatePin_(gatePin),
      activeHigh_(activeHigh),
      ledOn_(false),
      phaseOn_(false),
      state_(BenchState::Boot),
      pattern_(PatternType::None),
      lastStopReason_(StopReason::None),
      faultCode_(FaultCode::None),
      stateEnteredMs_(0),
      runStartedMs_(0),
      lastChangeMs_(0),
      onDurationMs_(0),
      offDurationMs_(0),
      remainingBursts_(0),
      activeTimeAccumulatedMs_(0),
      cooldownUntilMs_(0),
      currentPresetId_("") {
}

void StrobeBenchController::begin() {
    // Пин переводим в безопасное состояние как можно раньше.
    // Даже если shell или Wi-Fi по какой-то причине не поднимутся, MOSFET должен оставаться закрыт.
    pinMode(gatePin_, OUTPUT);
    setLed(false);

    clearPatternState();
    faultCode_ = FaultCode::None;
    lastStopReason_ = StopReason::None;
    stateEnteredMs_ = millis();
    runStartedMs_ = stateEnteredMs_;
    lastChangeMs_ = stateEnteredMs_;
    cooldownUntilMs_ = stateEnteredMs_;
    setState(BenchState::SafeDisarmed);
}

void StrobeBenchController::update() {
    const uint32_t now = millis();

    if (state_ == BenchState::Cooldown) {
        if (static_cast<int32_t>(now - cooldownUntilMs_) >= 0) {
            setState(BenchState::SafeDisarmed);
        }
        return;
    }

    if (!isBusy()) {
        return;
    }

    const uint32_t elapsed = now - lastChangeMs_;

    switch (pattern_) {
        case PatternType::Pulse:
            if (elapsed >= onDurationMs_) {
                recordActivePhase(now);
                setLed(false);
                finishRun(StopReason::Completed, false);
            }
            return;

        case PatternType::Burst:
            if (phaseOn_) {
                if (elapsed >= onDurationMs_) {
                    recordActivePhase(now);
                    setLed(false);
                    phaseOn_ = false;
                    lastChangeMs_ = now;

                    if (remainingBursts_ > 0) {
                        --remainingBursts_;
                    }

                    if (remainingBursts_ == 0) {
                        finishRun(StopReason::Completed, false);
                    }
                }
            } else if (remainingBursts_ > 0 && elapsed >= offDurationMs_) {
                setLed(true);
                phaseOn_ = true;
                lastChangeMs_ = now;
            }
            return;

        case PatternType::None:
        default:
            setLed(false);
            faultCode_ = FaultCode::InvalidState;
            lastStopReason_ = StopReason::FaultLatched;
            setState(BenchState::Fault);
            return;
    }
}

CommandResult StrobeBenchController::arm(bool serviceModeActive) {
    if (!serviceModeActive) {
        return CommandResult::ServiceModeRequired;
    }

    if (hasFault()) {
        return CommandResult::FaultLatched;
    }

    if (isCoolingDown()) {
        return CommandResult::CoolingDown;
    }

    if (state_ == BenchState::Armed) {
        return CommandResult::AlreadyArmed;
    }

    if (isBusy()) {
        return CommandResult::Busy;
    }

    setLed(false);
    clearPatternState();
    setState(BenchState::Armed);
    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::disarm() {
    if (state_ == BenchState::SafeDisarmed && !isBusy()) {
        return CommandResult::AlreadyDisarmed;
    }

    if (isBusy() && ledOn_) {
        recordActivePhase(millis());
    }

    setLed(false);
    clearPatternState();
    lastStopReason_ = StopReason::UserDisarm;
    setState(BenchState::SafeDisarmed);
    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::abort() {
    if (!isBusy() && state_ == BenchState::SafeDisarmed) {
        return CommandResult::IdleAlready;
    }

    if (isBusy() && ledOn_) {
        recordActivePhase(millis());
    }

    setLed(false);
    clearPatternState();
    lastStopReason_ = StopReason::UserAbort;
    setState(BenchState::SafeDisarmed);
    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::forceServiceExit() {
    if (isBusy() && ledOn_) {
        recordActivePhase(millis());
    }

    setLed(false);
    clearPatternState();
    lastStopReason_ = StopReason::ServiceModeExited;
    setState(BenchState::SafeDisarmed);
    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::pulse(bool serviceModeActive, uint32_t durationMs) {
    const CommandResult validation = validatePulse(serviceModeActive, durationMs);
    if (validation != CommandResult::Accepted) {
        return validation;
    }

    currentPresetId_ = "";
    onDurationMs_ = durationMs;
    offDurationMs_ = 0;
    remainingBursts_ = 0;
    startPattern(PatternType::Pulse);
    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::burst(bool serviceModeActive,
                                           uint32_t count,
                                           uint32_t onMs,
                                           uint32_t offMs) {
    const CommandResult validation = validateBurst(serviceModeActive, count, onMs, offMs);
    if (validation != CommandResult::Accepted) {
        return validation;
    }

    currentPresetId_ = "";
    remainingBursts_ = count;
    onDurationMs_ = onMs;
    offDurationMs_ = offMs;
    startPattern(PatternType::Burst);
    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::runPreset(bool serviceModeActive, const char* presetId) {
    const PresetDefinition* preset = findPreset(presetId);
    if (preset == nullptr) {
        return CommandResult::InvalidArguments;
    }

    currentPresetId_ = preset->id;

    switch (preset->pattern) {
        case PatternType::Pulse:
            return pulse(serviceModeActive, preset->onMs);
        case PatternType::Burst:
            return burst(serviceModeActive, preset->count, preset->onMs, preset->offMs);
        case PatternType::None:
        default:
            currentPresetId_ = "";
            return CommandResult::InvalidArguments;
    }
}

bool StrobeBenchController::isOn() const {
    return ledOn_;
}

bool StrobeBenchController::isArmed() const {
    return state_ == BenchState::Armed || isBusy();
}

bool StrobeBenchController::isBusy() const {
    return state_ == BenchState::RunningPattern;
}

bool StrobeBenchController::isCoolingDown() const {
    return state_ == BenchState::Cooldown;
}

bool StrobeBenchController::hasFault() const {
    return state_ == BenchState::Fault;
}

StatusSnapshot StrobeBenchController::status() const {
    StatusSnapshot snapshot;
    snapshot.state = state_;
    snapshot.pattern = pattern_;
    snapshot.lastStopReason = lastStopReason_;
    snapshot.fault = faultCode_;
    snapshot.ledOn = ledOn_;
    snapshot.armed = isArmed();
    snapshot.phaseOn = phaseOn_;
    snapshot.onDurationMs = onDurationMs_;
    snapshot.offDurationMs = offDurationMs_;
    snapshot.remainingBursts = remainingBursts_;
    snapshot.runtimeMs = runtimeMs();
    snapshot.activeTimeMs = activeTimeMs();
    snapshot.cooldownRemainingMs = cooldownRemainingMs();
    snapshot.currentPresetId = currentPresetId_;
    return snapshot;
}

const char* StrobeBenchController::stateName(BenchState value) {
    switch (value) {
        case BenchState::Boot:
            return "boot";
        case BenchState::SafeDisarmed:
            return "safe_disarmed";
        case BenchState::Armed:
            return "armed";
        case BenchState::RunningPattern:
            return "running_pattern";
        case BenchState::Cooldown:
            return "cooldown";
        case BenchState::Fault:
            return "fault";
        default:
            return "fault";
    }
}

const char* StrobeBenchController::patternName(PatternType value) {
    switch (value) {
        case PatternType::Pulse:
            return "pulse";
        case PatternType::Burst:
            return "burst";
        case PatternType::None:
        default:
            return "none";
    }
}

const char* StrobeBenchController::stopReasonName(StopReason value) {
    switch (value) {
        case StopReason::Completed:
            return "completed";
        case StopReason::UserDisarm:
            return "user_disarm";
        case StopReason::UserAbort:
            return "user_abort";
        case StopReason::ServiceModeExited:
            return "service_mode_exited";
        case StopReason::FaultLatched:
            return "fault_latched";
        case StopReason::None:
        default:
            return "none";
    }
}

const char* StrobeBenchController::faultName(FaultCode value) {
    switch (value) {
        case FaultCode::InvalidState:
            return "invalid_state";
        case FaultCode::None:
        default:
            return "none";
    }
}

const char* StrobeBenchController::commandResultName(CommandResult value) {
    switch (value) {
        case CommandResult::Accepted:
            return "accepted";
        case CommandResult::AlreadyArmed:
            return "already_armed";
        case CommandResult::AlreadyDisarmed:
            return "already_disarmed";
        case CommandResult::IdleAlready:
            return "idle_already";
        case CommandResult::Busy:
            return "busy";
        case CommandResult::NotArmed:
            return "not_armed";
        case CommandResult::CoolingDown:
            return "cooling_down";
        case CommandResult::FaultLatched:
            return "fault_latched";
        case CommandResult::InvalidArguments:
            return "invalid_arguments";
        case CommandResult::ServiceModeRequired:
            return "service_mode_required";
        default:
            return "invalid_arguments";
    }
}

const char* StrobeBenchController::riskName(PresetRisk value) {
    switch (value) {
        case PresetRisk::Low:
            return "low";
        case PresetRisk::Medium:
            return "medium";
        case PresetRisk::High:
            return "high";
        default:
            return "low";
    }
}

bool StrobeBenchController::shouldCooldown() const {
    return activeTimeMs() >= kCooldownTriggerActiveMs;
}

uint32_t StrobeBenchController::runtimeMs() const {
    if (!isBusy()) {
        return 0;
    }

    return millis() - runStartedMs_;
}

uint32_t StrobeBenchController::activeTimeMs() const {
    uint32_t activeMs = activeTimeAccumulatedMs_;
    if (isBusy() && ledOn_) {
        activeMs += millis() - lastChangeMs_;
    }
    return activeMs;
}

uint32_t StrobeBenchController::cooldownRemainingMs() const {
    if (state_ != BenchState::Cooldown) {
        return 0;
    }

    const int32_t remaining = static_cast<int32_t>(cooldownUntilMs_ - millis());
    return remaining > 0 ? static_cast<uint32_t>(remaining) : 0;
}

void StrobeBenchController::setState(BenchState newState) {
    state_ = newState;
    stateEnteredMs_ = millis();
}

void StrobeBenchController::clearPatternState() {
    pattern_ = PatternType::None;
    phaseOn_ = false;
    onDurationMs_ = 0;
    offDurationMs_ = 0;
    remainingBursts_ = 0;
    activeTimeAccumulatedMs_ = 0;
    runStartedMs_ = millis();
    lastChangeMs_ = millis();
    currentPresetId_ = "";
}

void StrobeBenchController::setLed(bool on) {
    ledOn_ = on;
    const uint8_t level = (on == activeHigh_) ? HIGH : LOW;
    digitalWrite(gatePin_, level);
}

void StrobeBenchController::recordActivePhase(uint32_t now) {
    if (!phaseOn_) {
        return;
    }

    activeTimeAccumulatedMs_ += now - lastChangeMs_;
}

void StrobeBenchController::startPattern(PatternType pattern) {
    pattern_ = pattern;
    lastStopReason_ = StopReason::None;
    runStartedMs_ = millis();
    lastChangeMs_ = runStartedMs_;
    activeTimeAccumulatedMs_ = 0;
    phaseOn_ = true;
    setLed(true);
    setState(BenchState::RunningPattern);
}

void StrobeBenchController::finishRun(StopReason reason, bool forceDisarm) {
    const bool needCooldown = shouldCooldown();
    lastStopReason_ = reason;
    pattern_ = PatternType::None;
    phaseOn_ = false;
    onDurationMs_ = 0;
    offDurationMs_ = 0;
    remainingBursts_ = 0;

    if (needCooldown && !forceDisarm) {
        cooldownUntilMs_ = millis() + kCooldownDurationMs;
        setState(BenchState::Cooldown);
        return;
    }

    setState(BenchState::SafeDisarmed);
}

CommandResult StrobeBenchController::validateReadyForRun(bool serviceModeActive) const {
    if (!serviceModeActive) {
        return CommandResult::ServiceModeRequired;
    }

    if (hasFault()) {
        return CommandResult::FaultLatched;
    }

    if (isCoolingDown()) {
        return CommandResult::CoolingDown;
    }

    if (isBusy()) {
        return CommandResult::Busy;
    }

    if (state_ != BenchState::Armed) {
        return CommandResult::NotArmed;
    }

    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::validatePulse(bool serviceModeActive, uint32_t durationMs) const {
    const CommandResult base = validateReadyForRun(serviceModeActive);
    if (base != CommandResult::Accepted) {
        return base;
    }

    if (durationMs < kMinPulseMs || durationMs > kMaxPulseMs) {
        return CommandResult::InvalidArguments;
    }

    return CommandResult::Accepted;
}

CommandResult StrobeBenchController::validateBurst(bool serviceModeActive,
                                                   uint32_t count,
                                                   uint32_t onMs,
                                                   uint32_t offMs) const {
    const CommandResult base = validateReadyForRun(serviceModeActive);
    if (base != CommandResult::Accepted) {
        return base;
    }

    if (count == 0 || count > kMaxBurstCount) {
        return CommandResult::InvalidArguments;
    }

    if (onMs < kMinPulseMs || onMs > kMaxBurstOnMs) {
        return CommandResult::InvalidArguments;
    }

    if (offMs < kMinPatternOffMs || offMs > kMaxBurstOffMs) {
        return CommandResult::InvalidArguments;
    }

    return CommandResult::Accepted;
}

size_t presetCount() {
    return sizeof(kPresets) / sizeof(kPresets[0]);
}

const PresetDefinition* presetAt(size_t index) {
    if (index >= presetCount()) {
        return nullptr;
    }

    return &kPresets[index];
}

const PresetDefinition* findPreset(const char* id) {
    if (id == nullptr || *id == '\0') {
        return nullptr;
    }

    for (size_t index = 0; index < presetCount(); ++index) {
        if (strcmp(kPresets[index].id, id) == 0) {
            return &kPresets[index];
        }
    }

    return nullptr;
}

}  // namespace smart_platform::modules::strobe
