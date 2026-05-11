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

private:
    String buildCurrentShellJson() const;
    String buildNodesJson() const;
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
    void appendJsonEscaped(String& target, const char* text) const;

    core::SystemCore& systemCore_;
    core::PlatformEventLog& platformLog_;
    storage::StorageManager& storageManager_;
};

}  // namespace smart_platform::web
