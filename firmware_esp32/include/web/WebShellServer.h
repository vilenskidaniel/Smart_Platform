#pragma once

#include <Arduino.h>
#include <WebServer.h>

#include "core/PlatformEventLog.h"
#include "core/SystemCore.h"
#include "modules/irrigation/IrrigationController.h"
#include "modules/strobe/StrobeBenchController.h"
#include "net/WiFiBootstrap.h"
#include "storage/StorageManager.h"
#include "web/ShellSnapshotFacade.h"

namespace smart_platform::web {

class WebShellServer {
public:
    WebShellServer(core::SystemCore& systemCore,
                   core::PlatformEventLog& platformLog,
                   net::WiFiBootstrap& wifiBootstrap,
                   storage::StorageManager& storageManager,
                   modules::irrigation::IrrigationController& irrigationController,
                   modules::strobe::StrobeBenchController& strobeBenchController);

    bool begin();
    void update();

    bool isReady() const;
    uint16_t port() const;

private:
    void registerRoutes();
    void handleRoot();
    void handleFederatedHandoffPage();
    void handleServiceHubPage();
    void handleGalleryPage();
    void handleSettingsPage();
    void handleContentPage();
    void handleIrrigationPage();
    void handleIrrigationServicePage();
    void handleStrobeServicePage();
    void handleSystemSnapshot();
    void handleShellSnapshot();
    void handleModules();
    void handleFederatedRouteInfo();
    void handleLogs();
    void handleReports();
    void handleDiagnostics();
    void handleContentStatus();
    void handleSyncState();
    void handleSyncHeartbeat();
    void handleSyncModulePush();
    void handleSyncLogPush();
    void handleServiceMode();
    void handleIrrigationStatus();
    void handleIrrigationZones();
    void handleIrrigationAutomaticMode();
    void handleIrrigationStart();
    void handleIrrigationStop();
    void handleIrrigationServiceZone();
    void handleIrrigationServiceSensor();
    void handleStrobeStatus();
    void handleStrobePresets();
    void handleStrobeArm();
    void handleStrobeDisarm();
    void handleStrobeAbort();
    void handleStrobePulse();
    void handleStrobeBurst();
    void handleStrobePreset();
    void handleNotFound();

    bool beginFileSystem();
    bool sendFileFromFileSystem(const char* path, const char* contentType);
    String buildIndexHtml() const;
    String buildFederatedHandoffHtml() const;
    String buildServiceHubHtml() const;
    String buildGalleryHtml() const;
    String buildSettingsHtml() const;
    String buildContentHtml() const;
    String buildIrrigationHtml() const;
    String buildIrrigationServiceHtml() const;
    String buildStrobeServiceHtml() const;
    String buildModulesJson() const;
    String buildFederatedRouteInfoJson(const char* moduleId) const;
    String buildLogsJson(size_t limit) const;
    String buildReportsJson(size_t limit) const;
    String buildDiagnosticsJson() const;
    String buildSyncStateJson() const;
    String buildSyncCommandResponseJson(const char* command,
                                        bool accepted,
                                        const char* message) const;
    String buildIrrigationStatusJson() const;
    String buildIrrigationZonesJson() const;
    String buildIrrigationCommandResponseJson(
        const char* command,
        modules::irrigation::CommandResult result,
        const char* message) const;
    String buildStrobeStatusJson() const;
    String buildStrobePresetsJson() const;
    String buildCommandResponseJson(const char* command,
                                    modules::strobe::CommandResult result,
                                    const char* message) const;
    bool serviceModeActive() const;

    core::SystemCore& systemCore_;
    core::PlatformEventLog& platformLog_;
    net::WiFiBootstrap& wifiBootstrap_;
    storage::StorageManager& storageManager_;
    ShellSnapshotFacade shellSnapshotFacade_;
    modules::irrigation::IrrigationController& irrigationController_;
    modules::strobe::StrobeBenchController& strobeBenchController_;
    WebServer server_;
    bool fileSystemReady_;
    bool ready_;
};

}  // namespace smart_platform::web
