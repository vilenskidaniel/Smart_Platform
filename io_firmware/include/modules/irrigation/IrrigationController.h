#pragma once

#include <Arduino.h>
#include <stddef.h>
#include <stdint.h>

namespace smart_platform::modules::irrigation {

constexpr size_t kZoneCount = 5;
constexpr uint8_t kPumpPin = 26;
constexpr uint8_t kValvePins[kZoneCount] = {27, 14, 12, 13, 25};

// На первом этапе реальные выходы отключены специально.
// Это безопаснее, пока не зафиксированы конкретные драйверы клапанов, логика их активации
// и подтвержденная распайка нового Smart Platform стенда.
constexpr bool kEnableRealOutputsByDefault = false;
constexpr uint32_t kDefaultManualDurationMs = 15000;
constexpr uint32_t kDefaultServiceDurationMs = 5000;
constexpr uint32_t kMaxManualDurationMs = 120000;
constexpr uint32_t kControllerUpdateIntervalMs = 250;
constexpr uint32_t kAutomaticWateringDurationMs = 8000;
constexpr float kAutomaticTriggerMarginPercent = 6.0f;

enum class ZoneState : uint8_t {
    Idle = 0,
    Watering,
    Fault,
    Disabled
};

enum class ModuleState : uint8_t {
    Idle = 0,
    Watering,
    Fault
};

enum class RunSource : uint8_t {
    None = 0,
    Manual,
    Automatic,
    ServiceTest
};

enum class CommandResult : uint8_t {
    Accepted = 0,
    Busy,
    InvalidZone,
    InvalidArguments,
    FaultLatched,
    ZoneDisabled,
    SensorFault,
    ServiceModeRequired,
    IdleAlready
};

struct EnvironmentStatus {
    float airTemperatureC = 23.8f;
    float airHumidityPercent = 51.0f;
    float waterReservePercent = 82.0f;
    bool simulated = true;
};

struct ControllerLogEvent {
    char level[12];
    char type[32];
    char message[80];
    char details[128];
};

struct ZoneStatus {
    size_t index = 0;
    char id[16];
    char title[24];
    ZoneState state = ZoneState::Idle;
    float soilMoisturePercent = -1.0f;
    float targetMoisturePercent = 45.0f;
    uint32_t remainingMs = 0;
    bool valveOpen = false;
    bool enabled = true;
    bool autoEnabled = true;
    bool sensorFault = false;
    bool sensorSimulated = true;
    uint32_t lastReadingMs = 0;
};

struct ModuleStatus {
    ModuleState state = ModuleState::Idle;
    bool dryRun = true;
    bool outputsEnabled = false;
    bool pumpOn = false;
    bool faultLatched = false;
    bool automaticModeEnabled = false;
    bool serviceModeActive = false;
    bool sensorFaultPresent = false;
    int activeZoneIndex = -1;
    uint32_t activeZoneRemainingMs = 0;
    uint32_t uptimeMs = 0;
    uint32_t completedCycles = 0;
    int driestZoneIndex = -1;
    float driestMoisturePercent = -1.0f;
    RunSource activeRunSource = RunSource::None;
};

class IrrigationController {
public:
    IrrigationController();

    void begin();
    void update();

    void setAutomaticModeEnabled(bool enabled);
    void setServiceModeActive(bool active);

    CommandResult startManualZone(size_t zoneIndex, uint32_t durationMs);
    CommandResult startServiceZone(size_t zoneIndex, uint32_t durationMs);
    CommandResult stopAll();
    bool applyServiceSensorProfile(size_t zoneIndex, const char* profile);

    ModuleStatus status() const;
    const ZoneStatus* zoneAt(size_t index) const;
    size_t zoneCount() const;
    const EnvironmentStatus& environment() const;
    bool pollLogEvent(ControllerLogEvent& outEvent);

    static const char* zoneStateName(ZoneState value);
    static const char* moduleStateName(ModuleState value);
    static const char* runSourceName(RunSource value);
    static const char* commandResultName(CommandResult value);

private:
    static constexpr size_t kLogEventQueueSize = 8;

    CommandResult startZone(size_t zoneIndex,
                            uint32_t durationMs,
                            RunSource runSource,
                            bool allowSensorFault);
    void finishActiveRun(const char* stopReason);
    void seedZones();
    void applyOutputs();
    void resetOutputs();
    void updateDryRunSimulation(uint32_t deltaMs);
    void updateEnvironmentSimulation(uint32_t deltaMs);
    void updateAutomaticMode();
    void refreshZonePresentation(ZoneStatus& zone);
    void refreshAllZonePresentation();
    int findDriestAutoEligibleZone() const;
    void enqueueLogEvent(const char* level,
                         const char* type,
                         const char* message,
                         const char* details = nullptr);

    ZoneStatus zones_[kZoneCount];
    bool outputsEnabled_;
    bool dryRun_;
    bool pumpOn_;
    bool faultLatched_;
    bool automaticModeEnabled_;
    bool serviceModeActive_;
    int activeZoneIndex_;
    uint32_t wateringUntilMs_;
    uint32_t bootMs_;
    uint32_t lastUpdateMs_;
    uint32_t completedCycles_;
    RunSource activeRunSource_;
    EnvironmentStatus environment_;
    ControllerLogEvent eventQueue_[kLogEventQueueSize];
    size_t eventHead_;
    size_t eventCount_;
};

}  // namespace smart_platform::modules::irrigation
