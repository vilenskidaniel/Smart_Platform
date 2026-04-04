#include <Arduino.h>

#include "core/PlatformEventLog.h"
#include "core/SystemCore.h"
#include "modules/irrigation/IrrigationController.h"
#include "modules/strobe/StrobeBenchController.h"
#include "net/WiFiBootstrap.h"
#include "storage/StorageManager.h"
#include "web/WebShellServer.h"

using smart_platform::core::PlatformEventLog;
using smart_platform::core::SystemCore;
using smart_platform::modules::irrigation::IrrigationController;
using smart_platform::modules::strobe::StrobeBenchController;
using smart_platform::net::WiFiBootstrap;
using smart_platform::storage::StorageManager;
using smart_platform::web::WebShellServer;

namespace {

SystemCore gSystemCore;
PlatformEventLog gPlatformLog;
IrrigationController gIrrigationController;
StorageManager gStorageManager;
StrobeBenchController gStrobeBenchController(
    smart_platform::modules::strobe::kDefaultGatePin,
    smart_platform::modules::strobe::kDefaultActiveHigh);
WiFiBootstrap gWiFiBootstrap;
WebShellServer gWebShellServer(
    gSystemCore,
    gPlatformLog,
    gWiFiBootstrap,
    gStorageManager,
    gIrrigationController,
    gStrobeBenchController);
uint32_t gLastDumpMs = 0;

void drainIrrigationLogEvents() {
    smart_platform::modules::irrigation::ControllerLogEvent event {};
    while (gIrrigationController.pollLogEvent(event)) {
        gPlatformLog.addLocal("irrigation", event.level, event.type, event.message, event.details);
    }
}

void syncIrrigationModuleState() {
    const auto status = gIrrigationController.status();

    if (status.faultLatched) {
        gSystemCore.updateLocalOwnedModuleState(
            "irrigation",
            smart_platform::core::ModuleState::Fault,
            smart_platform::core::BlockReason::ModuleFault);
    } else if (status.sensorFaultPresent) {
        gSystemCore.updateLocalOwnedModuleState(
            "irrigation",
            smart_platform::core::ModuleState::Degraded,
            smart_platform::core::BlockReason::ModuleFault);
    } else {
        gSystemCore.updateLocalOwnedModuleState(
            "irrigation",
            smart_platform::core::ModuleState::Online,
            smart_platform::core::BlockReason::None);
    }

    if (status.faultLatched) {
        gSystemCore.updateLocalOwnedModuleState(
            "irrigation_service",
            smart_platform::core::ModuleState::Fault,
            smart_platform::core::BlockReason::ModuleFault);
        return;
    }

    if (gSystemCore.activeMode() == smart_platform::core::ActiveMode::ServiceTest) {
        gSystemCore.updateLocalOwnedModuleState(
            "irrigation_service",
            smart_platform::core::ModuleState::Service,
            smart_platform::core::BlockReason::None);
        return;
    }

    if (gSystemCore.activeMode() == smart_platform::core::ActiveMode::Emergency) {
        gSystemCore.updateLocalOwnedModuleState(
            "irrigation_service",
            smart_platform::core::ModuleState::Locked,
            smart_platform::core::BlockReason::EmergencyState);
        return;
    }

    if (gSystemCore.activeMode() == smart_platform::core::ActiveMode::Fault) {
        gSystemCore.updateLocalOwnedModuleState(
            "irrigation_service",
            smart_platform::core::ModuleState::Fault,
            smart_platform::core::BlockReason::ModuleFault);
        return;
    }

    gSystemCore.updateLocalOwnedModuleState(
        "irrigation_service",
        smart_platform::core::ModuleState::Locked,
        smart_platform::core::BlockReason::ServiceModeRequired);
}

}  // namespace

void setup() {
    Serial.begin(115200);
    delay(250);

    gPlatformLog.begin("esp32-main");
    gPlatformLog.addLocal("system_shell", "info", "boot_started", "esp32 setup started");

    // Стартуем ядро раньше сетевого слоя, чтобы shell с первой секунды знал,
    // какие модули вообще существуют и что нужно сразу заблокировать.
    gSystemCore.begin();
    gIrrigationController.begin();
    syncIrrigationModuleState();
    gStrobeBenchController.begin();
    const bool storageReady = gStorageManager.begin();
    gPlatformLog.addLocal("system_shell",
                          storageReady ? "info" : "warn",
                          "content_storage_bootstrap",
                          storageReady ? "sd content storage is ready"
                                       : "sd content storage is unavailable");

    const bool wifiReady = gWiFiBootstrap.begin();
    gSystemCore.setLocalWifiReady(wifiReady);
    if (wifiReady) {
        const String localShellBaseUrl = String("http://") + gWiFiBootstrap.accessPointIp().toString();
        gSystemCore.setLocalShellBaseUrl(localShellBaseUrl.c_str());
    }
    gPlatformLog.addLocal("system_shell",
                          wifiReady ? "info" : "warn",
                          "wifi_bootstrap",
                          wifiReady ? "esp32 softap started" : "esp32 softap failed");

    // Даже если web-сервер не поднимется, System Core останется жив и будет отдавать
    // диагностическое состояние в Serial. Это полезно для ранней отладки без браузера.
    const bool shellReady = gWebShellServer.begin();
    gSystemCore.setLocalShellReady(shellReady);
    gPlatformLog.addLocal("system_shell",
                          shellReady ? "info" : "warn",
                          "web_shell_bootstrap",
                          shellReady ? "esp32 web shell is ready" : "esp32 web shell failed to start");

    Serial.println();
    Serial.println("=== Smart Platform / ESP32 bootstrap ===");
    Serial.println(gSystemCore.buildHumanReadableSummary());
    Serial.println(gWiFiBootstrap.buildSummary());
    Serial.println("Open browser: http://192.168.4.1/");
    Serial.println("Irrigation:   http://192.168.4.1/irrigation");
    Serial.println("Strobe bench: http://192.168.4.1/service/strobe");
    Serial.println("Content API:  http://192.168.4.1/api/v1/content/status");
    Serial.println("Irrigation service: http://192.168.4.1/service/irrigation");
    Serial.println(gSystemCore.buildSystemSnapshotJson());
    gPlatformLog.addLocal("system_shell", "info", "boot_finished", "esp32 setup finished");
}

void loop() {
    gSystemCore.update();
    gIrrigationController.setAutomaticModeEnabled(
        gSystemCore.activeMode() == smart_platform::core::ActiveMode::Automatic);
    gIrrigationController.setServiceModeActive(
        gSystemCore.activeMode() == smart_platform::core::ActiveMode::ServiceTest);
    gIrrigationController.update();
    drainIrrigationLogEvents();
    syncIrrigationModuleState();
    gStrobeBenchController.update();
    gWiFiBootstrap.update();
    gWebShellServer.update();

    // Периодический дамп сохраняем и после появления web shell.
    // Это помогает видеть JSON-снимок даже если тест идет без браузера или по UART.
    if (millis() - gLastDumpMs >= 5000UL) {
        gLastDumpMs = millis();
        Serial.println(gSystemCore.buildSystemSnapshotJson());
    }
}
