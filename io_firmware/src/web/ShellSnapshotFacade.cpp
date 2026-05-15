#include "web/ShellSnapshotFacade.h"

#include <cstring>

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

const char* shellStateName(core::ModuleState state) {
    if (state == core::ModuleState::Fault) {
        return "fault";
    }
    if (state == core::ModuleState::Degraded) {
        return "degraded";
    }
    if (state == core::ModuleState::Locked) {
        return "locked";
    }
    return nullptr;
}

}  // namespace

ShellSnapshotFacade::ShellSnapshotFacade(core::SystemCore& systemCore,
                                         core::PlatformEventLog& platformLog,
                                         storage::StorageManager& storageManager)
    : systemCore_(systemCore),
      platformLog_(platformLog),
      storageManager_(storageManager) {
    memset(viewers_, 0, sizeof(viewers_));
}

String ShellSnapshotFacade::buildShellSnapshotJson() const {
    String json;
    json.reserve(6144);
    json += "{";
    json += "\"schema_version\":\"shell-snapshot.v1\",";
    json += "\"generated_by\":";
    appendJsonEscaped(json, systemCore_.localNode().nodeId);
    json += ",\"generated_at_ms\":";
    json += String(millis());
    json += ",\"current_shell\":";
    json += buildCurrentShellJson();
    json += ",\"runtime\":";
    json += buildRuntimeJson();
    json += ",\"viewers\":";
    json += buildViewersJson();
    json += ",\"nodes\":";
    json += buildNodesJson();
    json += ",\"sync\":";
    json += buildSyncJson();
    json += ",\"storage\":";
    json += buildStorageJson();
    json += ",\"module_cards\":";
    json += buildModuleCardsJson();
    json += ",\"navigation\":";
    json += buildNavigationJson();
    json += ",\"summaries\":";
    json += buildSummariesJson();
    json += "}";
    return json;
}

void ShellSnapshotFacade::recordViewerHeartbeat(const char* viewerId,
                                                const char* viewerKind,
                                                const char* title,
                                                const char* value,
                                                const char* page,
                                                const char* address) {
    if (viewerId == nullptr || viewerId[0] == '\0') {
        return;
    }

    const uint32_t nowMs = millis();
    size_t targetIndex = kMaxViewerEntries;
    size_t oldestIndex = 0;

    for (size_t index = 0; index < kMaxViewerEntries; ++index) {
        ViewerPresenceEntry& entry = viewers_[index];
        const bool active = entry.active && static_cast<uint32_t>(nowMs - entry.lastSeenMs) <= kViewerTtlMs;
        if (active && strcmp(entry.viewerId, viewerId) == 0) {
            targetIndex = index;
            break;
        }

        if (!active) {
            targetIndex = index;
            break;
        }

        if (entry.lastSeenMs < viewers_[oldestIndex].lastSeenMs) {
            oldestIndex = index;
        }
    }

    if (targetIndex == kMaxViewerEntries) {
        targetIndex = oldestIndex;
    }

    ViewerPresenceEntry& entry = viewers_[targetIndex];
    entry.active = true;
    entry.lastSeenMs = nowMs;
    copyText(entry.viewerId, sizeof(entry.viewerId), viewerId);
    copyText(entry.viewerKind, sizeof(entry.viewerKind),
             viewerKind != nullptr && viewerKind[0] != '\0' ? viewerKind : "viewer");
    copyText(entry.title, sizeof(entry.title), title != nullptr && title[0] != '\0' ? title : entry.viewerKind);
    copyText(entry.value, sizeof(entry.value), value != nullptr ? value : "");
    copyText(entry.page, sizeof(entry.page), page != nullptr && page[0] != '\0' ? page : "/");
    copyText(entry.address, sizeof(entry.address), address != nullptr ? address : "");
}

String ShellSnapshotFacade::buildViewerHeartbeatJson() const {
    String json;
    json.reserve(640);
    json += "{";
    json += "\"runtime_profile\":\"owner_device\",";
    json += "\"viewers\":";
    json += buildViewersJson();
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
    json += ",\"identity_scope\":\"shell_surface\"";
    json += ",\"shell_base_url\":";
    appendJsonEscaped(json, localNode.shellBaseUrl);
    json += ",\"ui_shell_version\":";
    appendJsonEscaped(json, SMART_PLATFORM_UI_VERSION);
    json += ",\"active_mode\":";
    appendJsonEscaped(json, core::activeModeToString(systemCore_.activeMode()));
    json += ",\"service_mode\":";
    json += systemCore_.activeMode() == core::ActiveMode::ServiceTest ? "true" : "false";
    json += ",\"runtime_profile\":\"owner_device\"";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildRuntimeJson() const {
    const core::NodeHealth& localNode = systemCore_.localNode();
    const size_t viewerCount = activeViewerCount();

    String json;
    json.reserve(768);
    json += "{";
    json += "\"profile\":\"owner_device\",";
    json += "\"host\":{";
    json += "\"kind\":\"esp32_fallback\",";
    json += "\"title\":\"ESP32 fallback shell\",";
    json += "\"platform\":\"ESP32\",";
    json += "\"is_owner_device\":true,";
    json += "\"server_status\":\"online\",";
    json += "\"server_url\":";
    appendJsonEscaped(json, localNode.shellBaseUrl);
    json += ",\"summary\":\"The Smart Platform shell is currently hosted by the ESP32 fallback surface.\",";
    json += "\"paths\":[],";
    json += "\"viewer_count\":";
    json += String(static_cast<unsigned long>(viewerCount));
    json += ",\"open_supported\":false},";
    json += "\"viewer_count\":";
    json += String(static_cast<unsigned long>(viewerCount));
    json += ",\"viewer_hint\":\"Resolve the current viewer by matching the local viewer_id against viewers[].\"";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildViewersJson() const {
    const uint32_t nowMs = millis();

    String json;
    json.reserve(960);
    json += "[";

    bool first = true;
    for (size_t index = 0; index < kMaxViewerEntries; ++index) {
        const ViewerPresenceEntry& entry = viewers_[index];
        const bool active = entry.active && static_cast<uint32_t>(nowMs - entry.lastSeenMs) <= kViewerTtlMs;
        if (!active) {
            continue;
        }

        if (!first) {
            json += ",";
        }

        json += "{";
        json += "\"viewer_id\":";
        appendJsonEscaped(json, entry.viewerId);
        json += ",\"viewer_kind\":";
        appendJsonEscaped(json, entry.viewerKind);
        json += ",\"title\":";
        appendJsonEscaped(json, entry.title);
        json += ",\"value\":";
        appendJsonEscaped(json, entry.value);
        json += ",\"page\":";
        appendJsonEscaped(json, entry.page);
        json += ",\"address\":";
        appendJsonEscaped(json, entry.address);
        json += "}";
        first = false;
    }

    json += "]";
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
    json += ",\"wifi_ready\":";
    json += localNode.wifiReady ? "true" : "false";
    json += ",\"shell_ready\":";
    json += localNode.shellReady ? "true" : "false";
    json += ",\"sync_ready\":";
    json += localNode.syncReady ? "true" : "false";
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
    json += ",\"wifi_ready\":";
    json += peerNode.wifiReady ? "true" : "false";
    json += ",\"shell_ready\":";
    json += peerNode.shellReady ? "true" : "false";
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

String ShellSnapshotFacade::buildSyncJson() const {
    const core::NodeHealth& peerNode = systemCore_.peerNode();
    const char* syncState = syncSummaryState();

    String json;
    json.reserve(416);
    json += "{";
    json += "\"enabled\":true,";
    json += "\"state\":";
    appendJsonEscaped(json, syncState);
    json += ",\"peer_reachable\":";
    json += peerNode.reachable ? "true" : "false";
    json += ",\"peer_sync_ready\":";
    json += peerNode.syncReady ? "true" : "false";
    json += ",\"last_sync_ms\":";
    json += String(peerNode.lastSeenMs);
    json += ",\"last_error\":\"\",";
    json += "\"summary\":";
    if (!peerNode.reachable) {
        appendJsonEscaped(json, "Base node connectivity is unavailable because the remote node is offline.");
    } else if (!peerNode.syncReady) {
        appendJsonEscaped(json, "Background sync is enabled, but the remote node is still pending.");
    } else {
        appendJsonEscaped(json, "Background sync is ready and the remote node is reachable.");
    }
    json += ",\"domains\":[\"modules\",\"logs\"]";
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildStorageJson() const {
    const bool ready = storageManager_.sdReady();

    String json;
    json.reserve(512);
    json += "{";
    json += "\"storage\":\"sd\",";
    json += "\"storage_kind\":\"sd\",";
    json += "\"content_root\":\"sd:/\",";
    json += "\"content_root_exists\":";
    json += ready ? "true" : "false";
    json += ",\"content_root_state\":";
    appendJsonEscaped(json, ready ? "ready" : "missing");
    json += ",\"assets_ready\":";
    json += storageManager_.assetsReady() ? "true" : "false";
    json += ",\"audio_ready\":";
    json += storageManager_.audioReady() ? "true" : "false";
    json += ",\"animations_ready\":";
    json += storageManager_.animationsReady() ? "true" : "false";
    json += ",\"libraries_ready\":";
    json += storageManager_.librariesReady() ? "true" : "false";
    json += ",\"video_ready\":false,";
    json += "\"total_bytes\":0,";
    json += "\"paths\":[],";
    json += "\"summary\":";
    appendJsonEscaped(json,
                      ready ? "SD-backed storage is available for shell content and libraries."
                            : "SD-backed storage is not available on the current host.");
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
    json += "\"laboratory\":{\"available\":true,\"route_mode\":\"local\",\"path\":\"/service\",\"user_facing_title\":\"Laboratory\",\"internal_stage_name\":\"Laboratory\"},";
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
    const core::BlockReason globalBlockReason = systemCore_.globalBlockReason();
    bool hasFault = globalBlockReason != core::BlockReason::None;
    bool hasDegraded = false;

    String activeFailures;
    activeFailures.reserve(640);
    activeFailures += "[";
    bool firstFailure = true;

    if (globalBlockReason != core::BlockReason::None) {
        activeFailures += "{";
        activeFailures += "\"id\":";
        appendJsonEscaped(activeFailures, "global_block");
        activeFailures += ",\"shell_state\":";
        appendJsonEscaped(activeFailures, "fault");
        activeFailures += ",\"reason\":";
        appendJsonEscaped(activeFailures, core::blockReasonToString(globalBlockReason));
        activeFailures += "}";
        firstFailure = false;
    }

    for (size_t index = 0; index < systemCore_.registry().count(); ++index) {
        const core::ModuleDescriptor* module = systemCore_.registry().at(index);
        if (module == nullptr || !module->visible) {
            continue;
        }

        const char* stateName = shellStateName(module->state);
        if (stateName == nullptr) {
            continue;
        }

        if (isFaultState(module->state)) {
            hasFault = true;
        } else if (isDegradedShellState(module->state)) {
            hasDegraded = true;
        }

        if (!firstFailure) {
            activeFailures += ",";
        }
        activeFailures += "{";
        activeFailures += "\"id\":";
        appendJsonEscaped(activeFailures, module->id);
        activeFailures += ",\"shell_state\":";
        appendJsonEscaped(activeFailures, stateName);
        activeFailures += ",\"reason\":";
        appendJsonEscaped(activeFailures, core::blockReasonToString(module->blockReason));
        activeFailures += "}";
        firstFailure = false;
    }

    activeFailures += "]";

    String json;
    json.reserve(832);
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

    json += ",\"active_failures\":";
    json += activeFailures;
    json += "}";
    return json;
}

String ShellSnapshotFacade::buildDiagnosticsSummaryJson() const {
    String json;
    json.reserve(256);
    json += "{";
    json += "\"sync_state\":";
    appendJsonEscaped(json, syncSummaryState());
    json += ",\"ownership_summary\":\"I/O node owns irrigation, compute node owns turret\"";
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
    json.reserve(448);
    json += "{";
    json += "\"id\":";
    appendJsonEscaped(json, module.id);
    json += ",\"title\":";
    appendJsonEscaped(json, module.title);
    json += ",\"product_block\":";
    appendJsonEscaped(json, productBlock(module));
    json += ",\"owner_scope\":";
    appendJsonEscaped(json, ownerScope(module));
    json += ",\"owner_title\":";
    appendJsonEscaped(json, ownerTitle(module));
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
    if (sameText(ownerScope(module), "shared")) {
        return "Shared platform service is available on the current host.";
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
    return !sameText(ownerScope(module), "compute_node");
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

const char* ShellSnapshotFacade::ownerScope(const core::ModuleDescriptor& module) const {
    if (sameText(module.owner, "esp32") || sameText(module.owner, "io_node")) {
        return "io_node";
    }
    if (sameText(module.owner, "rpi") || sameText(module.owner, "raspberry_pi") || sameText(module.owner, "compute_node")) {
        return "compute_node";
    }
    return "shared";
}

const char* ShellSnapshotFacade::ownerTitle(const core::ModuleDescriptor& module) const {
    const char* scope = ownerScope(module);
    if (sameText(scope, "io_node")) {
        return "I/O node";
    }
    if (sameText(scope, "compute_node")) {
        return "Compute node";
    }
    return "Platform Service";
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
        return "laboratory";
    }
    if (sameText(module.id, "irrigation_service")) {
        return "laboratory";
    }
    return "platform_shell";
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
        return "remote_unavailable";
    }
    if (!peerNode.syncReady) {
        return "pending";
    }
    return "ready";
}

size_t ShellSnapshotFacade::activeViewerCount() const {
    const uint32_t nowMs = millis();
    size_t count = 0;

    for (size_t index = 0; index < kMaxViewerEntries; ++index) {
        const ViewerPresenceEntry& entry = viewers_[index];
        if (entry.active && static_cast<uint32_t>(nowMs - entry.lastSeenMs) <= kViewerTtlMs) {
            count += 1;
        }
    }

    return count;
}

void ShellSnapshotFacade::copyText(char* target, size_t size, const char* text) const {
    if (target == nullptr || size == 0) {
        return;
    }

    if (text == nullptr) {
        target[0] = '\0';
        return;
    }

    strncpy(target, text, size - 1);
    target[size - 1] = '\0';
}

void ShellSnapshotFacade::appendJsonEscaped(String& target, const char* text) const {
    target += "\"";
    if (text != nullptr) {
        for (const char* cursor = text; *cursor != '\0'; ++cursor) {
            switch (*cursor) {
                case '\\':
                    target += "\\\\";
                    break;
                case '"':
                    target += "\\\"";
                    break;
                case '\n':
                    target += "\\n";
                    break;
                case '\r':
                    target += "\\r";
                    break;
                case '\t':
                    target += "\\t";
                    break;
                default:
                    target += *cursor;
                    break;
            }
        }
    }
    target += "\"";
}

}  // namespace smart_platform::web
