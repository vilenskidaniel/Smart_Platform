#pragma once

#include <Arduino.h>
#include <stdint.h>

namespace smart_platform::core {

// Эти размеры выбраны с запасом для первой версии платформы.
// Позже их можно пересмотреть, когда появятся реальные данные синхронизации.
constexpr size_t kNodeIdMaxLength = 24;
constexpr size_t kNodeUrlMaxLength = 96;
constexpr size_t kModuleIdMaxLength = 24;
constexpr size_t kModuleTitleMaxLength = 32;
constexpr size_t kModuleOwnerMaxLength = 16;
constexpr size_t kModuleProfileMaxLength = 16;
constexpr size_t kModuleUiGroupMaxLength = 16;

enum class NodeType : uint8_t {
    Unknown = 0,
    Esp32,
    RaspberryPi
};

enum class ActiveMode : uint8_t {
    Manual = 0,
    Automatic,
    ServiceTest,
    Fault,
    Emergency
};

enum class ModuleState : uint8_t {
    Online = 0,
    Degraded,
    Locked,
    Fault,
    Service,
    Offline
};

enum class BlockReason : uint8_t {
    None = 0,
    OwnerUnavailable,
    PeerSyncPending,
    SafetyInterlock,
    ModuleFault,
    ServiceSessionActive,
    ServiceModeRequired,
    EmergencyState,
    ModuleOffline,
    Unknown
};

enum ModuleCapability : uint32_t {
    CapabilityNone         = 0u,
    CapabilityStatusPage   = 1u << 0,
    CapabilityManualPage   = 1u << 1,
    CapabilityServicePage  = 1u << 2,
    CapabilityLogs         = 1u << 3,
    CapabilityCommandable  = 1u << 4,
    CapabilityDiagnostics  = 1u << 5
};

struct NodeHealth {
    char nodeId[kNodeIdMaxLength];
    char shellBaseUrl[kNodeUrlMaxLength];
    NodeType nodeType;
    bool isLocal;
    bool reachable;
    bool shellReady;
    bool wifiReady;
    bool syncReady;
    ActiveMode reportedMode;
    uint32_t lastSeenMs;
    uint32_t uptimeMs;
};

struct ModuleDescriptor {
    char id[kModuleIdMaxLength];
    char title[kModuleTitleMaxLength];
    char owner[kModuleOwnerMaxLength];
    char profile[kModuleProfileMaxLength];
    char uiGroup[kModuleUiGroupMaxLength];
    ModuleState state;
    BlockReason blockReason;
    uint32_t capabilities;
    bool visible;
    bool manualPage;
    bool servicePage;
};

const char* nodeTypeToString(NodeType value);
const char* activeModeToString(ActiveMode value);
const char* moduleStateToString(ModuleState value);
const char* blockReasonToString(BlockReason value);

}  // namespace smart_platform::core
