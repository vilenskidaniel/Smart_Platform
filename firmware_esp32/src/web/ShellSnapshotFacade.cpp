#include "web/ShellSnapshotFacade.h"

#ifndef SMART_PLATFORM_UI_VERSION
#define SMART_PLATFORM_UI_VERSION "0.1.0"
#endif

namespace smart_platform::web {

namespace {

bool sameText(const char* left, const char* right) {
    if (left == nullptr || right == nullptr) {
        return false;
    }

    return strcmp(left, right) == 0;
}

bool isFaultState(core::ModuleState state) {
    return state == core::ModuleState::Fault;
}

bool isDegradedShellState(core::ModuleState state) {
    return state == core::ModuleState::Degraded || state == core::ModuleState::Locked;
}

}  // namespace

ShellSnapshotFacade::ShellSnapshotFacade(core::SystemCore& systemCore,
                                         core::PlatformEventLog& platformLog,
                                         storage::StorageManager& storageManager)
    : systemCore_(systemCore),
      platformLog_(platformLog),
      storageManager_(storageManager) {
}

String ShellSnapshotFacade::buildShellSnapshotJson() const {
    String json;
    json.reserve(4096);
    json += "{";
    json += "\"schema_version\":\"shell-snapshot.v1\",";
    json += "\"generated_by\":";
    appendJsonEscaped(json, systemCore_.localNode().nodeId);
    json += ",\"generated_at_ms\":";
    json += String(millis());
    json += ",\"current_shell\":";
    json += buildCurrentShellJson();
    json += ",\"nodes\":";
    json += buildNodesJson();
    json += ",\"module_cards\":";
    json += buildModuleCardsJson();
    json += ",\"navigation\":";
    json += buildNavigationJson();
    json += ",\"summaries\":";
    json += buildSummariesJson();
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildCurrentShellJson() const {
    const core::NodeHealth& localNode = systemCore_.localNode();

    String json;
    json.reserve(256);
    json += "{";
    json += "\"node_id\":";
    appendJsonEscaped(json, localNode.nodeId);
    json += ",\"node_type\":\"esp32\"";
    json += ",\"shell_base_url\":";
    appendJsonEscaped(json, localNode.shellBaseUrl);
    json += ",\"ui_shell_version\":";
    appendJsonEscaped(json, SMART_PLATFORM_UI_VERSION);
    json += ",\"active_mode\":";
    appendJsonEscaped(json, core::activeModeToString(systemCore_.activeMode()));
    json += ",\"service_mode\":";
    json += systemCore_.activeMode() == core::ActiveMode::ServiceTest ? "true" : "false";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildNodesJson() const {
    const core::NodeHealth& localNode = systemCore_.localNode();
    const core::NodeHealth& peerNode = systemCore_.peerNode();

    String json;
    json.reserve(512);
    json += "{";
    json += "\"current\":{";
    json += "\"node_id\":";
    appendJsonEscaped(json, localNode.nodeId);
    json += ",\"title\":";
    appendJsonEscaped(json, nodeTitle(localNode));
    json += ",\"reachable\":true";
    json += ",\"health\":";
    appendJsonEscaped(json, nodeHealth(localNode));
    json += ",\"summary\":\"Local shell is active\"";
    json += "},";
    json += "\"peer\":{";
    json += "\"node_id\":";
    appendJsonEscaped(json, peerNode.nodeId);
    json += ",\"title\":";
    appendJsonEscaped(json, nodeTitle(peerNode));
    json += ",\"reachable\":";
    json += peerNode.reachable ? "true" : "false";
    json += ",\"health\":";
    appendJsonEscaped(json, nodeHealth(peerNode));
    json += ",\"sync_ready\":";
    json += peerNode.syncReady ? "true" : "false";
    json += ",\"reported_mode\":";
    appendJsonEscaped(json, core::activeModeToString(peerNode.reportedMode));
    json += ",\"shell_base_url\":";
    appendJsonEscaped(json, peerNode.shellBaseUrl);
    json += ",\"summary\":";
    if (peerNode.reachable) {
        appendJsonEscaped(json, peerNode.syncReady ? "Peer owner is ready" : "Peer is visible but sync is pending");
    } else {
        appendJsonEscaped(json, "Peer owner is offline");
    }
    json += "}";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildModuleCardsJson() const {
    String json;
    json.reserve(2048);
    json += "[";

    bool first = true;
    for (size_t index = 0; index < systemCore_.registry().count(); ++index) {
        const core::ModuleDescriptor* module = systemCore_.registry().at(index);
        if (module == nullptr || !module->visible) {
            continue;
        }

        if (!first) {
            json += ",";
        }

        json += buildModuleCardJson(*module);
        first = false;
    }

    json += "]";
    return json;
}

String ShellSnapshotFacade::buildNavigationJson() const {
    String json;
    json.reserve(512);
    json += "{";
    json += "\"home\":\"/\",";
    json += "\"gallery\":{\"path\":\"/gallery\",\"route_mode\":\"virtual\",\"owner_scope\":\"shared\",\"tabs\":[\"plants\",\"media\",\"reports\"],\"default_tab\":\"reports\"},";
    json += "\"laboratory\":{\"available\":true,\"route_mode\":\"local\",\"path\":\"/service\",\"user_facing_title\":\"Laboratory\",\"internal_stage_name\":\"Service/Test v1\"},";
    json += "\"settings\":\"/settings\",";
    json += "\"service\":\"/service\",";
    json += "\"content\":\"/content\",";
    json += "\"diagnostics\":\"/settings#diagnostics\",";
    json += "\"logs\":\"/gallery?tab=reports\",";
    json += "\"service_test\":{\"available\":true,\"route_mode\":\"local\",\"path\":\"/service\"}";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildSummariesJson() const {
    String json;
    json.reserve(512);
    json += "{";
    json += "\"faults\":";
    json += buildFaultSummaryJson();
    json += ",\"diagnostics\":";
    json += buildDiagnosticsSummaryJson();
    json += ",\"activity\":";
    json += buildLogSummaryJson();
    json += ",\"logs\":";
    json += buildLogSummaryJson();
    json += ",\"content\":";
    json += buildContentSummaryJson();
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildFaultSummaryJson() const {
    bool hasFault = systemCore_.globalBlockReason() != core::BlockReason::None;
    bool hasDegraded = false;

    for (size_t index = 0; index < systemCore_.registry().count(); ++index) {
        const core::ModuleDescriptor* module = systemCore_.registry().at(index);
        if (module == nullptr || !module->visible) {
            continue;
        }

        if (isFaultState(module->state)) {
            hasFault = true;
        }
        if (isDegradedShellState(module->state)) {
            hasDegraded = true;
        }
    }

    String json;
    json.reserve(192);
    json += "{";
    json += "\"has_fault\":";
    json += hasFault ? "true" : "false";
    json += ",\"has_degraded\":";
    json += hasDegraded ? "true" : "false";
    json += ",\"message\":";

    if (hasFault) {
        appendJsonEscaped(json, "Some modules require attention");
    } else if (hasDegraded) {
        appendJsonEscaped(json, "Some modules are degraded or blocked");
    } else {
        appendJsonEscaped(json, "System shell is healthy");
    }

    json += "}";
    return json;
}

String ShellSnapshotFacade::buildDiagnosticsSummaryJson() const {
    String json;
    json.reserve(256);
    json += "{";
    json += "\"sync_state\":";
    appendJsonEscaped(json, syncSummaryState());
    json += ",\"ownership_summary\":\"ESP32 owns irrigation, Raspberry Pi owns turret\"";
    json += ",\"content_ready\":";
    json += storageManager_.sdReady() ? "true" : "false";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildLogSummaryJson() const {
    String json;
    json.reserve(224);
    json += "{";
    json += "\"recent_visible\":";
    json += String(platformLog_.count());
    json += ",\"total_visible\":";
    json += String(platformLog_.count());
    json += ",\"warning_count\":";
    json += String(platformLog_.countLevel("warning"));
    json += ",\"error_count\":";
    json += String(platformLog_.countLevel("error"));
    json += ",\"primary_viewer\":\"gallery.reports\"";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildContentSummaryJson() const {
    String json;
    json.reserve(192);
    json += "{";
    json += "\"storage_kind\":\"sd\",";
    json += "\"ready\":";
    json += storageManager_.sdReady() ? "true" : "false";
    json += ",\"libraries_ready\":";
    json += storageManager_.librariesReady() ? "true" : "false";
    json += ",\"assets_ready\":";
    json += storageManager_.assetsReady() ? "true" : "false";
    json += ",\"audio_ready\":";
    json += storageManager_.audioReady() ? "true" : "false";
    json += ",\"animations_ready\":";
    json += storageManager_.animationsReady() ? "true" : "false";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildModuleCardJson(const core::ModuleDescriptor& module) const {
    String json;
    json.reserve(384);
    json += "{";
    json += "\"id\":";
    appendJsonEscaped(json, module.id);
    json += ",\"title\":";
    appendJsonEscaped(json, module.title);
    json += ",\"product_block\":";
    appendJsonEscaped(json, productBlock(module));
    json += ",\"owner_node_id\":";
    appendJsonEscaped(json, ownerNodeId(module));
    json += ",\"owner_available\":";
    json += ownerAvailable(module) ? "true" : "false";
    json += ",\"state\":";
    appendJsonEscaped(json, core::moduleStateToString(module.state));
    json += ",\"block_reason\":";
    appendJsonEscaped(json, core::blockReasonToString(module.blockReason));
    json += ",\"canonical_path\":";
    appendJsonEscaped(json, canonicalPath(module));
    json += ",\"canonical_url\":";
    appendJsonEscaped(json, canonicalUrlForModule(module).c_str());
    json += ",\"route_mode\":";
    appendJsonEscaped(json, routeMode(module));
    json += ",\"summary\":";
    appendJsonEscaped(json, buildModuleSummary(module).c_str());
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildModuleSummary(const core::ModuleDescriptor& module) const {
    if (module.state == core::ModuleState::Fault) {
        return String("Module fault: ") + core::blockReasonToString(module.blockReason);
    }
    if (module.state == core::ModuleState::Locked) {
        return String("Module is locked: ") + core::blockReasonToString(module.blockReason);
    }
    if (module.state == core::ModuleState::Degraded) {
        return String("Module is degraded: ") + core::blockReasonToString(module.blockReason);
    }
    if (!ownerIsLocal(module)) {
        return ownerAvailable(module) ? "Peer-owned page is available" : "Peer owner is not available";
    }
    return "Local module is ready";
}

String ShellSnapshotFacade::canonicalUrlForModule(const core::ModuleDescriptor& module) const {
    const core::NodeHealth& localNode = systemCore_.localNode();
    const core::NodeHealth& peerNode = systemCore_.peerNode();
    const char* path = canonicalPath(module);

    if (!ownerIsLocal(module)) {
        if (!ownerAvailable(module)) {
            return "";
        }
        return String(peerNode.shellBaseUrl) + path;
    }

    if (localNode.shellBaseUrl[0] != '\0') {
        return String(localNode.shellBaseUrl) + path;
    }

    return String(path);
}

bool ShellSnapshotFacade::ownerAvailable(const core::ModuleDescriptor& module) const {
    if (ownerIsLocal(module)) {
        return true;
    }

    const core::NodeHealth& peerNode = systemCore_.peerNode();
    return peerNode.reachable && peerNode.shellReady && peerNode.syncReady &&
           peerNode.shellBaseUrl[0] != '\0';
}

bool ShellSnapshotFacade::ownerIsLocal(const core::ModuleDescriptor& module) const {
    return !sameText(module.owner, "rpi");
}

const char* ShellSnapshotFacade::nodeTitle(const core::NodeHealth& node) const {
    if (node.nodeType == core::NodeType::Esp32) {
        return "ESP32";
    }
    if (node.nodeType == core::NodeType::RaspberryPi) {
        return "Raspberry Pi";
    }
    return "Node";
}

const char* ShellSnapshotFacade::nodeHealth(const core::NodeHealth& node) const {
    if (!node.reachable) {
        return "offline";
    }
    if (!node.wifiReady || !node.shellReady || (!node.isLocal && !node.syncReady)) {
        return "degraded";
    }
    return "online";
}

const char* ShellSnapshotFacade::ownerNodeId(const core::ModuleDescriptor& module) const {
    return ownerIsLocal(module) ? systemCore_.localNode().nodeId : systemCore_.peerNode().nodeId;
}

const char* ShellSnapshotFacade::productBlock(const core::ModuleDescriptor& module) const {
    if (sameText(module.id, "irrigation")) {
        return "irrigation";
    }
    if (sameText(module.id, "turret_bridge") || sameText(module.id, "strobe")) {
        return "turret";
    }
    if (sameText(module.id, "strobe_bench") || sameText(module.id, "service_mode")) {
        return "service_test";
    }
    if (sameText(module.id, "irrigation_service")) {
        return "service_test";
    }
    return "system_shell";
}

const char* ShellSnapshotFacade::routeMode(const core::ModuleDescriptor& module) const {
    if (ownerIsLocal(module)) {
        return "local";
    }
    return ownerAvailable(module) ? "handoff" : "blocked";
}

const char* ShellSnapshotFacade::canonicalPath(const core::ModuleDescriptor& module) const {
    if (sameText(module.id, "irrigation")) {
        return "/irrigation";
    }
    if (sameText(module.id, "turret_bridge")) {
        return "/turret";
    }
    if (sameText(module.id, "strobe")) {
        return "/turret#strobe";
    }
    if (sameText(module.id, "strobe_bench")) {
        return "/service/strobe";
    }
    if (sameText(module.id, "irrigation_service")) {
        return "/service/irrigation";
    }
    if (sameText(module.id, "logs")) {
        return "/gallery?tab=reports";
    }
    if (sameText(module.id, "settings")) {
        return "/settings";
    }
    if (sameText(module.id, "diagnostics")) {
        return "/settings#diagnostics";
    }
    if (sameText(module.id, "service_mode")) {
        return "/service";
    }
    return "/";
}

const char* ShellSnapshotFacade::syncSummaryState() const {
    const core::NodeHealth& peerNode = systemCore_.peerNode();
    if (!peerNode.reachable) {
        return "peer_offline";
    }
    if (!peerNode.syncReady) {
        return "pending";
    }
    return "ready";
}

void ShellSnapshotFacade::appendJsonEscaped(String& target, const char* text) const {
    target += "\"";
    if (text != nullptr) {
        target += text;
    }
    target += "\"";
}

}  // namespace smart_platform::web
