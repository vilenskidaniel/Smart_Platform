#pragma once

#include <Arduino.h>
#include <stddef.h>
#include <stdint.h>

namespace smart_platform::modules::strobe {

constexpr uint8_t kDefaultGatePin = 23;
constexpr bool kDefaultActiveHigh = true;

constexpr uint32_t kMinPulseMs = 1;
constexpr uint32_t kMaxPulseMs = 5000;
constexpr uint32_t kMinPatternOffMs = 10;
constexpr uint32_t kMaxBurstCount = 1000;
constexpr uint32_t kMaxBurstOnMs = 5000;
constexpr uint32_t kMaxBurstOffMs = 60000;
constexpr uint32_t kMaxLoopOnMs = 5000;
constexpr uint32_t kMaxLoopOffMs = 60000;
constexpr uint32_t kDefaultContinuousOnMs = 1500;
constexpr uint32_t kMaxContinuousOnMs = 5000;
constexpr uint32_t kMaxLoopRuntimeMs = 120000;
constexpr uint32_t kMaxLoopDutyPercent = 80;
constexpr uint32_t kMaxBurstDutyPercent = 90;
constexpr uint32_t kCooldownTriggerActiveMs = 1500;
constexpr uint32_t kCooldownTriggerDutyPercent = 60;
constexpr uint32_t kCooldownDurationMs = 3000;

enum class BenchState : uint8_t {
    Boot = 0,
    SafeDisarmed,
    Armed,
    RunningPattern,
    Cooldown,
    Fault
};

enum class PatternType : uint8_t {
    None = 0,
    Pulse,
    Burst,
    Loop,
    ContinuousOn
};

enum class StopReason : uint8_t {
    None = 0,
    Completed,
    UserStop,
    UserDisarm,
    UserAbort,
    ContinuousTimeout,
    LoopTimeout,
    ServiceModeExited,
    FaultLatched
};

enum class FaultCode : uint8_t {
    None = 0,
    InvalidState
};

enum class CommandResult : uint8_t {
    Accepted = 0,
    AlreadyArmed,
    AlreadyDisarmed,
    IdleAlready,
    Busy,
    NotArmed,
    CoolingDown,
    FaultLatched,
    InvalidArguments,
    UnsafeTiming,
    ServiceModeRequired
};

enum class PresetRisk : uint8_t {
    Low = 0,
    Medium,
    High
};

struct PresetDefinition {
    const char* id;
    const char* title;
    const char* purpose;
    PatternType pattern;
    uint32_t count;
    uint32_t onMs;
    uint32_t offMs;
    PresetRisk risk;
};

struct StatusSnapshot {
    BenchState state = BenchState::Boot;
    PatternType pattern = PatternType::None;
    StopReason lastStopReason = StopReason::None;
    FaultCode fault = FaultCode::None;
    bool ledOn = false;
    bool armed = false;
    bool phaseOn = false;
    uint32_t onDurationMs = 0;
    uint32_t offDurationMs = 0;
    uint32_t remainingBursts = 0;
    uint32_t runtimeMs = 0;
    uint32_t activeTimeMs = 0;
    uint32_t cooldownRemainingMs = 0;
    const char* currentPresetId = "";
};

class StrobeBenchController {
public:
    StrobeBenchController(uint8_t gatePin, bool activeHigh);

    void begin();
    void update();

    CommandResult arm(bool serviceModeActive);
    CommandResult disarm();
    CommandResult stop();
    CommandResult abort();
    CommandResult forceServiceExit();
    CommandResult pulse(bool serviceModeActive, uint32_t durationMs);
    CommandResult burst(bool serviceModeActive, uint32_t count, uint32_t onMs, uint32_t offMs);
    CommandResult loop(bool serviceModeActive, uint32_t onMs, uint32_t offMs);
    CommandResult continuousOn(bool serviceModeActive, uint32_t timeoutMs);
    CommandResult runPreset(bool serviceModeActive, const char* presetId);

    bool isOn() const;
    bool isArmed() const;
    bool isBusy() const;
    bool isCoolingDown() const;
    bool hasFault() const;
    StatusSnapshot status() const;

    static const char* stateName(BenchState value);
    static const char* patternName(PatternType value);
    static const char* stopReasonName(StopReason value);
    static const char* faultName(FaultCode value);
    static const char* commandResultName(CommandResult value);
    static const char* riskName(PresetRisk value);

private:
    bool shouldCooldown() const;
    uint32_t runtimeMs() const;
    uint32_t activeTimeMs() const;
    uint32_t cooldownRemainingMs() const;
    void setState(BenchState newState);
    void clearPatternState();
    void setLed(bool on);
    void recordActivePhase(uint32_t now);
    void startPattern(PatternType pattern);
    void finishRun(StopReason reason, bool forceDisarm);
    CommandResult validateReadyForRun(bool serviceModeActive) const;
    CommandResult validatePulse(bool serviceModeActive, uint32_t durationMs) const;
    CommandResult validateBurst(bool serviceModeActive, uint32_t count, uint32_t onMs, uint32_t offMs) const;
    CommandResult validateLoop(bool serviceModeActive, uint32_t onMs, uint32_t offMs) const;
    CommandResult validateContinuousOn(bool serviceModeActive, uint32_t timeoutMs) const;

    uint8_t gatePin_;
    bool activeHigh_;
    bool ledOn_;
    bool phaseOn_;
    BenchState state_;
    PatternType pattern_;
    StopReason lastStopReason_;
    FaultCode faultCode_;
    uint32_t stateEnteredMs_;
    uint32_t runStartedMs_;
    uint32_t lastChangeMs_;
    uint32_t onDurationMs_;
    uint32_t offDurationMs_;
    uint32_t remainingBursts_;
    uint32_t continuousTimeoutMs_;
    uint32_t activeTimeAccumulatedMs_;
    uint32_t cooldownUntilMs_;
    const char* currentPresetId_;
};

size_t presetCount();
const PresetDefinition* presetAt(size_t index);
const PresetDefinition* findPreset(const char* id);

}  // namespace smart_platform::modules::strobe
