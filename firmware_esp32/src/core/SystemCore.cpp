#include "core/SystemCore.h"

#include <stdio.h>
#include <string.h>

namespace smart_platform::core {

namespace {

#ifndef SMART_PLATFORM_NODE_ID
#define SMART_PLATFORM_NODE_ID "esp32-main"
#endif

#ifndef SMART_PLATFORM_PEER_ID
#define SMART_PLATFORM_PEER_ID "rpi-turret"
#endif

#ifndef SMART_PLATFORM_UI_VERSION
#define SMART_PLATFORM_UI_VERSION "0.1.0"
#endif

#ifndef SMART_PLATFORM_PEER_TIMEOUT_MS
#define SMART_PLATFORM_PEER_TIMEOUT_MS 5000UL
#endif

void copyText(char* destination, size_t destinationSize, const char* source) {
    if (destination == nullptr || destinationSize == 0) {
        return;
    }

    if (source == nullptr) {
        destination[0] = '\0';
        return;
    }

    snprintf(destination, destinationSize, "%s", source);
}

bool sameText(const char* left, const char* right) {
    if (left == nullptr || right == nullptr) {
        return false;
    }

    return strcmp(left, right) == 0;
}

ModuleDescriptor makeModule(const char* id,
                            const char* title,
                            const char* owner,
                            const char* profile,
                            const char* uiGroup,
                            ModuleState state,
                            BlockReason blockReason,
                            uint32_t capabilities,
                            bool visible,
                            bool manualPage,
                            bool servicePage) {
    ModuleDescriptor descriptor {};
    copyText(descriptor.id, sizeof(descriptor.id), id);
    copyText(descriptor.title, sizeof(descriptor.title), title);
    copyText(descriptor.owner, sizeof(descriptor.owner), owner);
    copyText(descriptor.profile, sizeof(descriptor.profile), profile);
    copyText(descriptor.uiGroup, sizeof(descriptor.uiGroup), uiGroup);
    descriptor.state = state;
    descriptor.blockReason = blockReason;
    descriptor.capabilities = capabilities;
    descriptor.visible = visible;
    descriptor.manualPage = manualPage;
    descriptor.servicePage = servicePage;
    return descriptor;
}

bool capabilityEnabled(uint32_t mask, ModuleCapability capability) {
    return (mask & static_cast<uint32_t>(capability)) != 0u;
}

void appendJsonEscaped(String& target, const char* text) {
    target += "\"";
    if (text != nullptr) {
        target += text;
    }
    target += "\"";
}

void appendCapabilityArray(String& target, uint32_t mask) {
    bool first = true;
    target += "[";

    auto appendName = [&](const char* name) {
        if (!first) {
            target += ",";
        }

        appendJsonEscaped(target, name);
        first = false;
    };

    if (capabilityEnabled(mask, CapabilityStatusPage)) {
        appendName("status_page");
    }
    if (capabilityEnabled(mask, CapabilityManualPage)) {
        appendName("manual_page");
    }
    if (capabilityEnabled(mask, CapabilityServicePage)) {
        appendName("service_page");
    }
    if (capabilityEnabled(mask, CapabilityLogs)) {
        appendName("logs");
    }
    if (capabilityEnabled(mask, CapabilityCommandable)) {
        appendName("commandable");
    }
    if (capabilityEnabled(mask, CapabilityDiagnostics)) {
        appendName("diagnostics");
    }

    target += "]";
}

void appendNodeHealthJson(String& target, const NodeHealth& node) {
    target += "{";
    target += "\"node_id\":";
    appendJsonEscaped(target, node.nodeId);
    target += ",\"shell_base_url\":";
    appendJsonEscaped(target, node.shellBaseUrl);
    target += ",\"node_type\":";
    appendJsonEscaped(target, nodeTypeToString(node.nodeType));
    target += ",\"is_local\":";
    target += node.isLocal ? "true" : "false";
    target += ",\"reachable\":";
    target += node.reachable ? "true" : "false";
    target += ",\"shell_ready\":";
    target += node.shellReady ? "true" : "false";
    target += ",\"wifi_ready\":";
    target += node.wifiReady ? "true" : "false";
    target += ",\"sync_ready\":";
    target += node.syncReady ? "true" : "false";
    target += ",\"reported_mode\":";
    appendJsonEscaped(target, activeModeToString(node.reportedMode));
    target += ",\"last_seen_ms\":";
    target += String(node.lastSeenMs);
    target += ",\"uptime_ms\":";
    target += String(node.uptimeMs);
    target += "}";
}

const char* moduleCanonicalPath(const char* moduleId) {
    if (moduleId == nullptr) {
        return "/";
    }

    if (strcmp(moduleId, "irrigation") == 0) {
        return "/irrigation";
    }
    if (strcmp(moduleId, "turret_bridge") == 0) {
        return "/turret";
    }
    if (strcmp(moduleId, "strobe") == 0) {
        return "/turret#strobe";
    }
    if (strcmp(moduleId, "strobe_bench") == 0) {
        return "/service/strobe";
    }
    if (strcmp(moduleId, "irrigation_service") == 0) {
        return "/service/irrigation";
    }
    if (strcmp(moduleId, "logs") == 0) {
        return "/gallery?tab=reports";
    }
    if (strcmp(moduleId, "settings") == 0) {
        return "/settings";
    }
    if (strcmp(moduleId, "diagnostics") == 0) {
        return "/settings#diagnostics";
    }
    if (strcmp(moduleId, "service_mode") == 0) {
        return "/service";
    }

    return "/";
}

bool ownerAvailableForModule(const ModuleDescriptor& module,
                             const NodeHealth& localNode,
                             const NodeHealth& peerNode) {
    if (sameText(module.owner, "rpi")) {
        return peerNode.reachable && peerNode.shellReady && peerNode.syncReady &&
               peerNode.shellBaseUrl[0] != '\0';
    }

    return true;
}

const char* ownerNodeIdForModule(const ModuleDescriptor& module,
                                 const NodeHealth& localNode,
                                 const NodeHealth& peerNode) {
    if (sameText(module.owner, "rpi")) {
        return peerNode.nodeId;
    }

    return localNode.nodeId;
}

String canonicalUrlForModule(const ModuleDescriptor& module,
                             const NodeHealth& localNode,
                             const NodeHealth& peerNode) {
    const char* path = moduleCanonicalPath(module.id);

    if (sameText(module.owner, "rpi")) {
        if (!ownerAvailableForModule(module, localNode, peerNode)) {
            return "";
        }

        return String(peerNode.shellBaseUrl) + path;
    }

    if (localNode.shellBaseUrl[0] != '\0') {
        return String(localNode.shellBaseUrl) + path;
    }

    return String(path);
}

const char* federatedAccessForModule(const ModuleDescriptor& module,
                                     const NodeHealth& localNode,
                                     const NodeHealth& peerNode) {
    (void)localNode;

    if (sameText(module.owner, "rpi")) {
        return ownerAvailableForModule(module, localNode, peerNode)
                   ? "peer_owner_available"
                   : "peer_owner_missing";
    }

    if (sameText(module.owner, "shared")) {
        return "shared_local";
    }

    return "local_owner";
}

void appendModuleJson(String& target,
                      const ModuleDescriptor& module,
                      const NodeHealth& localNode,
                      const NodeHealth& peerNode) {
    const String canonicalUrl = canonicalUrlForModule(module, localNode, peerNode);

    target += "{";
    target += "\"id\":";
    appendJsonEscaped(target, module.id);
    target += ",\"title\":";
    appendJsonEscaped(target, module.title);
    target += ",\"owner\":";
    appendJsonEscaped(target, module.owner);
    target += ",\"profile\":";
    appendJsonEscaped(target, module.profile);
    target += ",\"ui_group\":";
    appendJsonEscaped(target, module.uiGroup);
    target += ",\"state\":";
    appendJsonEscaped(target, moduleStateToString(module.state));
    target += ",\"block_reason\":";
    appendJsonEscaped(target, blockReasonToString(module.blockReason));
    target += ",\"owner_node_id\":";
    appendJsonEscaped(target, ownerNodeIdForModule(module, localNode, peerNode));
    target += ",\"owner_available\":";
    target += ownerAvailableForModule(module, localNode, peerNode) ? "true" : "false";
    target += ",\"canonical_path\":";
    appendJsonEscaped(target, moduleCanonicalPath(module.id));
    target += ",\"canonical_url\":";
    appendJsonEscaped(target, canonicalUrl.c_str());
    target += ",\"federated_access\":";
    appendJsonEscaped(target, federatedAccessForModule(module, localNode, peerNode));
    target += ",\"visible\":";
    target += module.visible ? "true" : "false";
    target += ",\"manual_page\":";
    target += module.manualPage ? "true" : "false";
    target += ",\"service_page\":";
    target += module.servicePage ? "true" : "false";
    target += ",\"capabilities\":";
    appendCapabilityArray(target, module.capabilities);
    target += "}";
}

}  // namespace

const char* nodeTypeToString(NodeType value) {
    switch (value) {
        case NodeType::Esp32:
            return "esp32";
        case NodeType::RaspberryPi:
            return "raspberry_pi";
        case NodeType::Unknown:
        default:
            return "unknown";
    }
}

const char* activeModeToString(ActiveMode value) {
    switch (value) {
        case ActiveMode::Manual:
            return "manual";
        case ActiveMode::Automatic:
            return "automatic";
        case ActiveMode::ServiceTest:
            return "service_test";
        case ActiveMode::Fault:
            return "fault";
        case ActiveMode::Emergency:
            return "emergency";
        default:
            return "manual";
    }
}

const char* moduleStateToString(ModuleState value) {
    switch (value) {
        case ModuleState::Online:
            return "online";
        case ModuleState::Degraded:
            return "degraded";
        case ModuleState::Locked:
            return "locked";
        case ModuleState::Fault:
            return "fault";
        case ModuleState::Service:
            return "service";
        case ModuleState::Offline:
            return "offline";
        default:
            return "offline";
    }
}

const char* blockReasonToString(BlockReason value) {
    switch (value) {
        case BlockReason::None:
            return "none";
        case BlockReason::OwnerUnavailable:
            return "owner_unavailable";
        case BlockReason::PeerSyncPending:
            return "peer_sync_pending";
        case BlockReason::SafetyInterlock:
            return "safety_interlock";
        case BlockReason::ModuleFault:
            return "module_fault";
        case BlockReason::ServiceSessionActive:
            return "service_session_active";
        case BlockReason::ServiceModeRequired:
            return "service_mode_required";
        case BlockReason::EmergencyState:
            return "emergency_state";
        case BlockReason::ModuleOffline:
            return "module_offline";
        case BlockReason::Unknown:
        default:
            return "unknown";
    }
}

SystemCore::SystemCore()
    : activeMode_(ActiveMode::Manual),
      globalBlockReason_(BlockReason::None) {
    memset(&localNode_, 0, sizeof(localNode_));
    memset(&peerNode_, 0, sizeof(peerNode_));
}

void SystemCore::begin() {
    configureLocalNode();
    configurePeerNode();
    registry_.clear();
    seedDefaultModules();
    applyModeRules();
    applyPeerRules();
}

void SystemCore::update() {
    localNode_.uptimeMs = millis();
    localNode_.reportedMode = activeMode_;

    // Если heartbeat от peer-узла давно не приходил, система возвращается
    // в безопасное деградированное состояние и заново блокирует удаленные модули.
    if (peerNode_.reachable && (millis() - peerNode_.lastSeenMs > SMART_PLATFORM_PEER_TIMEOUT_MS)) {
        peerNode_.reachable = false;
        peerNode_.shellReady = false;
        peerNode_.wifiReady = false;
        peerNode_.syncReady = false;
        copyText(peerNode_.shellBaseUrl, sizeof(peerNode_.shellBaseUrl), "");
        applyPeerRules();
    }
}

const NodeHealth& SystemCore::localNode() const {
    return localNode_;
}

const NodeHealth& SystemCore::peerNode() const {
    return peerNode_;
}

const ModuleRegistry& SystemCore::registry() const {
    return registry_;
}

ActiveMode SystemCore::activeMode() const {
    return activeMode_;
}

BlockReason SystemCore::globalBlockReason() const {
    return globalBlockReason_;
}

void SystemCore::setActiveMode(ActiveMode mode) {
    activeMode_ = mode;
    localNode_.reportedMode = mode;
    applyModeRules();
    applyPeerRules();
}

void SystemCore::setLocalWifiReady(bool ready) {
    localNode_.wifiReady = ready;
}

void SystemCore::setLocalShellReady(bool ready) {
    localNode_.shellReady = ready;
}

void SystemCore::setLocalShellBaseUrl(const char* baseUrl) {
    copyText(localNode_.shellBaseUrl, sizeof(localNode_.shellBaseUrl), baseUrl);
}

void SystemCore::setPeerNodeStatus(const char* nodeId,
                                   const char* shellBaseUrl,
                                   bool reachable,
                                   bool wifiReady,
                                   bool shellReady,
                                   bool syncReady,
                                   ActiveMode reportedMode,
                                   uint32_t lastSeenMs) {
    if (nodeId != nullptr && nodeId[0] != '\0') {
        copyText(peerNode_.nodeId, sizeof(peerNode_.nodeId), nodeId);
    }
    copyText(peerNode_.shellBaseUrl, sizeof(peerNode_.shellBaseUrl), reachable ? shellBaseUrl : "");

    peerNode_.reachable = reachable;
    peerNode_.wifiReady = reachable ? wifiReady : false;
    peerNode_.shellReady = reachable ? shellReady : false;
    peerNode_.syncReady = reachable ? syncReady : false;
    peerNode_.reportedMode = reportedMode;
    peerNode_.lastSeenMs = lastSeenMs;
    applyPeerRules();
}

void SystemCore::setPeerReachable(bool reachable, uint32_t lastSeenMs) {
    setPeerNodeStatus(peerNode_.nodeId,
                      peerNode_.shellBaseUrl,
                      reachable,
                      reachable,
                      reachable,
                      false,
                      peerNode_.reportedMode,
                      lastSeenMs);
}

bool SystemCore::updatePeerOwnedModuleState(const char* moduleId, ModuleState state, BlockReason reason) {
    ModuleDescriptor* descriptor = registry_.findMutable(moduleId);
    if (descriptor == nullptr) {
        return false;
    }

    // На этом этапе разрешаем удаленно менять только те модули,
    // которые принадлежат Raspberry Pi. Это защищает локальные ESP32-модули
    // от случайного перетирания через sync API.
    if (!sameText(descriptor->owner, "rpi")) {
        return false;
    }

    descriptor->state = state;
    descriptor->blockReason = reason;
    return true;
}

bool SystemCore::updateLocalOwnedModuleState(const char* moduleId, ModuleState state, BlockReason reason) {
    ModuleDescriptor* descriptor = registry_.findMutable(moduleId);
    if (descriptor == nullptr) {
        return false;
    }

    // Локально здесь разрешаем менять только ESP32-owned и shared-модули.
    // Peer-owned записи должны продолжать жить под правилами sync/ownership.
    if (sameText(descriptor->owner, "rpi")) {
        return false;
    }

    descriptor->state = state;
    descriptor->blockReason = reason;
    return true;
}

String SystemCore::buildSystemSnapshotJson() const {
    String json;
    json.reserve(2600);

    json += "{";
    json += "\"ui_shell_version\":";
    appendJsonEscaped(json, SMART_PLATFORM_UI_VERSION);
    json += ",\"active_mode\":";
    appendJsonEscaped(json, activeModeToString(activeMode_));
    json += ",\"global_block_reason\":";
    appendJsonEscaped(json, blockReasonToString(globalBlockReason_));
    json += ",\"local_node\":";
    appendNodeHealthJson(json, localNode_);
    json += ",\"peer_node\":";
    appendNodeHealthJson(json, peerNode_);
    json += ",\"modules\":[";

    for (size_t index = 0; index < registry_.count(); ++index) {
        const ModuleDescriptor* module = registry_.at(index);
        if (module == nullptr) {
            continue;
        }

        if (index > 0) {
            json += ",";
        }

        appendModuleJson(json, *module, localNode_, peerNode_);
    }

    json += "]";
    json += "}";
    return json;
}

String SystemCore::buildHumanReadableSummary() const {
    String text;
    text.reserve(320);

    text += "Smart Platform / System Core\n";
    text += "Local node: ";
    text += localNode_.nodeId;
    text += " (";
    text += nodeTypeToString(localNode_.nodeType);
    text += ")\n";
    text += "Peer node: ";
    text += peerNode_.nodeId;
    text += " / reachable=";
    text += peerNode_.reachable ? "true" : "false";
    text += " / sync_ready=";
    text += peerNode_.syncReady ? "true" : "false";
    text += "\n";
    text += "Active mode: ";
    text += activeModeToString(activeMode_);
    text += "\n";
    text += "Registered modules: ";
    text += String(registry_.count());
    return text;
}

void SystemCore::configureLocalNode() {
    copyText(localNode_.nodeId, sizeof(localNode_.nodeId), SMART_PLATFORM_NODE_ID);
    copyText(localNode_.shellBaseUrl, sizeof(localNode_.shellBaseUrl), "");
    localNode_.nodeType = NodeType::Esp32;
    localNode_.isLocal = true;
    localNode_.reachable = true;
    localNode_.shellReady = true;
    localNode_.wifiReady = false;
    localNode_.syncReady = true;
    localNode_.reportedMode = activeMode_;
    localNode_.lastSeenMs = millis();
    localNode_.uptimeMs = millis();
}

void SystemCore::configurePeerNode() {
    copyText(peerNode_.nodeId, sizeof(peerNode_.nodeId), SMART_PLATFORM_PEER_ID);
    copyText(peerNode_.shellBaseUrl, sizeof(peerNode_.shellBaseUrl), "");
    peerNode_.nodeType = NodeType::RaspberryPi;
    peerNode_.isLocal = false;
    peerNode_.reachable = false;
    peerNode_.shellReady = false;
    peerNode_.wifiReady = false;
    peerNode_.syncReady = false;
    peerNode_.reportedMode = ActiveMode::Manual;
    peerNode_.lastSeenMs = 0;
    peerNode_.uptimeMs = 0;
}

void SystemCore::seedDefaultModules() {
    // Здесь задается системная карта модулей для shell и синхронизации.
    // Это не "список экранов", а единый реестр возможностей платформы.
    registry_.add(makeModule("system_shell", "System Shell", "shared", "core", "system",
                             ModuleState::Online, BlockReason::None,
                             CapabilityStatusPage | CapabilityDiagnostics, true, true, true));

    registry_.add(makeModule("sync_core", "Sync Core", "shared", "core", "system",
                             ModuleState::Degraded, BlockReason::OwnerUnavailable,
                             CapabilityStatusPage | CapabilityDiagnostics, true, false, true));

    registry_.add(makeModule("irrigation", "Irrigation", "esp32", "plant_care", "irrigation",
                             ModuleState::Online, BlockReason::None,
                             CapabilityStatusPage | CapabilityManualPage | CapabilityServicePage |
                                 CapabilityLogs | CapabilityCommandable | CapabilityDiagnostics,
                             true, true, true));

    registry_.add(makeModule("turret_bridge", "Turret", "rpi", "turret", "turret",
                             ModuleState::Locked, BlockReason::OwnerUnavailable,
                             CapabilityStatusPage | CapabilityManualPage | CapabilityDiagnostics,
                             true, true, false));

    registry_.add(makeModule("strobe", "Strobe", "rpi", "turret", "turret",
                             ModuleState::Locked, BlockReason::OwnerUnavailable,
                             CapabilityStatusPage | CapabilityManualPage | CapabilityServicePage |
                                 CapabilityCommandable | CapabilityDiagnostics,
                             true, true, true));

    registry_.add(makeModule("strobe_bench", "Strobe Bench", "esp32", "bench_service", "service",
                             ModuleState::Locked, BlockReason::ServiceModeRequired,
                             CapabilityStatusPage | CapabilityManualPage | CapabilityServicePage |
                                 CapabilityCommandable | CapabilityDiagnostics | CapabilityLogs,
                             true, true, true));

    registry_.add(makeModule("irrigation_service", "Irrigation Service", "esp32", "plant_care", "service",
                             ModuleState::Locked, BlockReason::ServiceModeRequired,
                             CapabilityStatusPage | CapabilityManualPage | CapabilityServicePage |
                                 CapabilityCommandable | CapabilityDiagnostics | CapabilityLogs,
                             true, true, true));

    registry_.add(makeModule("logs", "Logs", "shared", "core", "logs",
                             ModuleState::Online, BlockReason::None,
                             CapabilityStatusPage | CapabilityLogs | CapabilityDiagnostics,
                             true, false, true));

    registry_.add(makeModule("settings", "Settings", "shared", "core", "settings",
                             ModuleState::Online, BlockReason::None,
                             CapabilityStatusPage | CapabilityManualPage | CapabilityDiagnostics,
                             true, true, false));

    registry_.add(makeModule("diagnostics", "Diagnostics", "shared", "core", "system",
                             ModuleState::Online, BlockReason::None,
                             CapabilityStatusPage | CapabilityDiagnostics, true, false, true));

    registry_.add(makeModule("service_mode", "Service Mode", "shared", "core", "service",
                             ModuleState::Online, BlockReason::None,
                             CapabilityStatusPage | CapabilityServicePage | CapabilityDiagnostics,
                             true, false, true));
}

void SystemCore::applyModeRules() {
    switch (activeMode_) {
        case ActiveMode::ServiceTest:
            registry_.updateState("service_mode", ModuleState::Service, BlockReason::None);
            registry_.updateState("strobe_bench", ModuleState::Service, BlockReason::None);
            registry_.updateState("irrigation_service", ModuleState::Service, BlockReason::None);
            break;

        case ActiveMode::Emergency:
            registry_.updateState("service_mode", ModuleState::Locked, BlockReason::EmergencyState);
            registry_.updateState("strobe_bench", ModuleState::Locked, BlockReason::EmergencyState);
            registry_.updateState("irrigation_service", ModuleState::Locked, BlockReason::EmergencyState);
            break;

        case ActiveMode::Fault:
            registry_.updateState("service_mode", ModuleState::Locked, BlockReason::ModuleFault);
            registry_.updateState("strobe_bench", ModuleState::Fault, BlockReason::ModuleFault);
            registry_.updateState("irrigation_service", ModuleState::Fault, BlockReason::ModuleFault);
            break;

        case ActiveMode::Manual:
        case ActiveMode::Automatic:
        default:
            registry_.updateState("service_mode", ModuleState::Online, BlockReason::None);
            registry_.updateState("strobe_bench", ModuleState::Locked, BlockReason::ServiceModeRequired);
            registry_.updateState("irrigation_service", ModuleState::Locked, BlockReason::ServiceModeRequired);
            break;
    }
}

void SystemCore::applyPeerRules() {
    // Пока полноценного двустороннего merge еще нет, работаем по безопасной схеме:
    // 1. Нет heartbeat -> удаленные модули снова locked.
    // 2. Heartbeat есть, но sync еще не завершен -> удаленные модули degraded.
    // 3. Sync подтвержден -> sync_core online, а состояния turret-модулей
    //    уже могут обновляться отдельными push-сообщениями от Raspberry Pi.
    if (!peerNode_.reachable) {
        registry_.updateState("sync_core", ModuleState::Degraded, BlockReason::OwnerUnavailable);
        registry_.updateState("turret_bridge", ModuleState::Locked, BlockReason::OwnerUnavailable);
        registry_.updateState("strobe", ModuleState::Locked, BlockReason::OwnerUnavailable);
        return;
    }

    if (!peerNode_.syncReady) {
        registry_.updateState("sync_core", ModuleState::Degraded, BlockReason::PeerSyncPending);
        registry_.updateState("turret_bridge", ModuleState::Degraded, BlockReason::PeerSyncPending);
        registry_.updateState("strobe", ModuleState::Degraded, BlockReason::PeerSyncPending);
        return;
    }

    registry_.updateState("sync_core", ModuleState::Online, BlockReason::None);

    ModuleDescriptor* turretBridge = registry_.findMutable("turret_bridge");
    if (turretBridge != nullptr && turretBridge->blockReason == BlockReason::OwnerUnavailable) {
        turretBridge->state = ModuleState::Degraded;
        turretBridge->blockReason = BlockReason::PeerSyncPending;
    }

    ModuleDescriptor* strobe = registry_.findMutable("strobe");
    if (strobe != nullptr && strobe->blockReason == BlockReason::OwnerUnavailable) {
        strobe->state = ModuleState::Degraded;
        strobe->blockReason = BlockReason::PeerSyncPending;
    }
}

}  // namespace smart_platform::core
