#pragma once

#include <Arduino.h>

#include "core/PlatformEventLog.h"
#include "core/SystemCore.h"
#include "storage/StorageManager.h"

namespace smart_platform::web {

class ShellSnapshotFacade {
public:
    ShellSnapshotFacade(core::SystemCore& systemCore,
                        core::PlatformEventLog& platformLog,
                        storage::StorageManager& storageManager);

    String buildShellSnapshotJson() const;
    void recordViewerHeartbeat(const char* viewerId,
                               const char* viewerKind,
                               const char* title,
                               const char* value,
                               const char* page,
                               const char* address);
    String buildViewerHeartbeatJson() const;

private:
    struct ViewerPresenceEntry {
        bool active;
        uint32_t lastSeenMs;
        char viewerId[40];
        char viewerKind[16];
        char title[32];
        char value[24];
        char page[96];
        char address[48];
    };

    static constexpr size_t kMaxViewerEntries = 6;
    static constexpr uint32_t kViewerTtlMs = 15000;

    String buildCurrentShellJson() const;
    String buildRuntimeJson() const;
    String buildViewersJson() const;
    String buildNodesJson() const;
    String buildSyncJson() const;
    String buildStorageJson() const;
    String buildModuleCardsJson() const;
    String buildNavigationJson() const;
    String buildSummariesJson() const;
    String buildFaultSummaryJson() const;
    String buildDiagnosticsSummaryJson() const;
    String buildLogSummaryJson() const;
    String buildContentSummaryJson() const;
    String buildModuleCardJson(const core::ModuleDescriptor& module) const;
    String buildModuleSummary(const core::ModuleDescriptor& module) const;
    String canonicalUrlForModule(const core::ModuleDescriptor& module) const;

    bool ownerAvailable(const core::ModuleDescriptor& module) const;
    bool ownerIsLocal(const core::ModuleDescriptor& module) const;

    const char* nodeTitle(const core::NodeHealth& node) const;
    const char* nodeHealth(const core::NodeHealth& node) const;
    const char* ownerScope(const core::ModuleDescriptor& module) const;
    const char* ownerTitle(const core::ModuleDescriptor& module) const;
    const char* ownerNodeId(const core::ModuleDescriptor& module) const;
    const char* productBlock(const core::ModuleDescriptor& module) const;
    const char* routeMode(const core::ModuleDescriptor& module) const;
    const char* canonicalPath(const core::ModuleDescriptor& module) const;
    const char* syncSummaryState() const;
    size_t activeViewerCount() const;
    void copyText(char* target, size_t size, const char* text) const;
    void appendJsonEscaped(String& target, const char* text) const;

    core::SystemCore& systemCore_;
    core::PlatformEventLog& platformLog_;
    storage::StorageManager& storageManager_;
    ViewerPresenceEntry viewers_[kMaxViewerEntries];
};

}  // namespace smart_platform::web
