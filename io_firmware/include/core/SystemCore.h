#pragma once

#include <Arduino.h>

#include "core/ModuleRegistry.h"

namespace smart_platform::core {

class SystemCore {
public:
    SystemCore();

    void begin();
    void update();

    const NodeHealth& localNode() const;
    const NodeHealth& peerNode() const;
    const ModuleRegistry& registry() const;
    ActiveMode activeMode() const;
    BlockReason globalBlockReason() const;

    void setActiveMode(ActiveMode mode);
    void setLocalWifiReady(bool ready);
    void setLocalShellReady(bool ready);
    void setLocalShellBaseUrl(const char* baseUrl);
    void setPeerNodeStatus(const char* nodeId,
                           const char* shellBaseUrl,
                           bool reachable,
                           bool wifiReady,
                           bool shellReady,
                           bool syncReady,
                           ActiveMode reportedMode,
                           uint32_t lastSeenMs);
    void setPeerReachable(bool reachable, uint32_t lastSeenMs);
    bool updateLocalOwnedModuleState(const char* moduleId, ModuleState state, BlockReason reason);
    bool updatePeerOwnedModuleState(const char* moduleId, ModuleState state, BlockReason reason);

    String buildSystemSnapshotJson() const;
    String buildHumanReadableSummary() const;

private:
    void configureLocalNode();
    void configurePeerNode();
    void seedDefaultModules();
    void applyModeRules();
    void applyPeerRules();

    NodeHealth localNode_;
    NodeHealth peerNode_;
    ActiveMode activeMode_;
    BlockReason globalBlockReason_;
    ModuleRegistry registry_;
};

}  // namespace smart_platform::core
