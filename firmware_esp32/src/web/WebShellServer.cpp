#include "web/WebShellServer.h"

#include <FS.h>
#include <LittleFS.h>

namespace smart_platform::web {

namespace {

const char kFallbackIndexHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform Shell</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f1f5ef; color: #203024; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    code, pre { font-family: Consolas, monospace; }
    pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
    a { color: #315d42; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Smart Platform Shell</h1>
      <p>Файлы shell в <code>LittleFS</code> пока не найдены, поэтому открыт безопасный fallback-экран из прошивки.</p>
      <p>Чтобы получить полноценный интерфейс, загрузи файловую систему командой <code>pio run -t uploadfs</code> для каталога <code>firmware_esp32</code>.</p>
      <p><a href="/irrigation">Открыть fallback-страницу Irrigation</a></p>
      <p><a href="/service/strobe">Открыть fallback-страницу Strobe Bench</a></p>
      <p><a href="/api/v1/system">Открыть /api/v1/system</a></p>
    </div>
  </div>
</body>
</html>
)HTML";

const char kFallbackIrrigationHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Irrigation</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f3f7f1; color: #1f2d23; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    a { color: #315d42; }
    pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Irrigation</h1>
      <p>Полная страница полива еще не загружена в <code>LittleFS</code>, поэтому открыт fallback-экран.</p>
      <p>На этом этапе контроллер уже работает в <code>dry-run</code> режиме и отдает живой API для тестирования shell и сценариев.</p>
      <pre>/api/v1/irrigation/status
/api/v1/irrigation/zones
/api/v1/irrigation/start?zone=0&amp;duration_ms=15000
/api/v1/irrigation/stop</pre>
      <p><a href="/">Вернуться в shell</a></p>
    </div>
  </div>
</body>
</html>
)HTML";

const char kFallbackIrrigationServiceHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Irrigation Service</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f3f7f1; color: #1f2d23; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    a { color: #315d42; }
    pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Irrigation Service</h1>
      <p>Laboratory page for irrigation is not loaded from <code>LittleFS</code> yet, so the firmware fallback screen is shown.</p>
      <pre>/api/v1/irrigation/status
/api/v1/irrigation/zones
/api/v1/irrigation/automatic?enabled=1
/api/v1/irrigation/service/zone?zone=0&amp;duration_ms=5000
/api/v1/irrigation/service/sensor?zone=0&amp;profile=dry</pre>
      <p><a href="/">Вернуться в shell</a></p>
    </div>
  </div>
</body>
</html>
)HTML";

const char kFallbackStrobeServiceHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Strobe Bench</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f3f7f1; color: #1f2d23; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    a { color: #315d42; }
    pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Strobe Bench</h1>
      <p>Полная сервисная страница еще не загружена в <code>LittleFS</code>, поэтому открыт fallback-экран.</p>
      <p>API уже доступен и может использоваться для теста:</p>
      <pre>/api/v1/strobe_bench/status
/api/v1/strobe_bench/presets
/api/v1/strobe_bench/arm
/api/v1/strobe_bench/disarm
/api/v1/strobe_bench/stop
/api/v1/strobe_bench/abort
/api/v1/strobe_bench/pulse
/api/v1/strobe_bench/burst
/api/v1/strobe_bench/loop
/api/v1/strobe_bench/continuous
/api/v1/strobe_bench/preset</pre>
      <p><a href="/">Вернуться в shell</a></p>
    </div>
  </div>
</body>
</html>
)HTML";

const char kFallbackFederatedHandoffHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Federated Handoff</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f3f7f1; color: #1f2d23; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    .meta { color: #5e6e61; }
    .mono { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; font-family: Consolas, monospace; font-size: 12px; }
    .actions a { display: inline-block; margin-right: 12px; color: #315d42; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Federated Handoff</h1>
      <p class="meta" id="summary">Подготовка маршрута owner-aware navigation...</p>
      <div class="actions" id="actions"></div>
      <pre class="mono" id="payload">waiting...</pre>
    </div>
  </div>
  <script>
    const params = new URLSearchParams(window.location.search);
    const moduleId = params.get('module_id') || '';

    async function run() {
      const response = await fetch(`/api/v1/federation/route?module_id=${encodeURIComponent(moduleId)}`);
      const payload = await response.json();
      document.getElementById('payload').textContent = JSON.stringify(payload, null, 2);

      const summary = document.getElementById('summary');
      const actions = document.getElementById('actions');

      if (!payload.module_found) {
        summary.textContent = 'Модуль не найден в registry текущего shell.';
        return;
      }

      if (!payload.owner_available) {
        summary.textContent = `Модуль ${payload.module_id} сейчас недоступен: owner еще не в сети или sync не завершен.`;
        return;
      }

      if (payload.canonical_url) {
        summary.textContent = `Переход к owner page модуля ${payload.module_id}. Если переход не сработает автоматически, открой ссылку вручную.`;
        actions.innerHTML = `<a href="${payload.canonical_url}">Открыть owner page</a><a href="/">Вернуться в shell</a>`;
        setTimeout(() => { window.location.href = payload.canonical_url; }, 1200);
        return;
      }

      summary.textContent = 'Для модуля нет canonical URL. Остаемся в текущем shell.';
    }

    run().catch((error) => {
      document.getElementById('summary').textContent = `Ошибка handoff: ${error}`;
    });
  </script>
</body>
</html>
)HTML";

const char kFallbackGalleryHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Gallery</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f3f7f1; color: #1f2d23; }
    .wrap { max-width: 980px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    a { color: #315d42; }
    pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Gallery</h1>
      <p>Gallery page is not loaded from <code>LittleFS</code> yet, so the firmware fallback screen is shown.</p>
      <pre>/gallery?tab=plants
/gallery?tab=media
/gallery?tab=reports
/api/v1/shell/snapshot
/api/v1/reports
/api/v1/logs</pre>
      <p><a href="/">Return to shell</a></p>
    </div>
  </div>
</body>
</html>
)HTML";

const char kFallbackSettingsHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Settings</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f3f7f1; color: #1f2d23; }
    .wrap { max-width: 980px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    a { color: #315d42; }
    pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Settings</h1>
      <p>Settings page is not loaded from <code>LittleFS</code> yet, so the firmware fallback screen is shown.</p>
      <pre>/settings
/settings#diagnostics
/api/v1/shell/snapshot
/api/v1/content/status</pre>
      <p><a href="/">Return to shell</a></p>
    </div>
  </div>
</body>
</html>
)HTML";

const char kFallbackContentHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Storage Diagnostics</title>
  <style>
    body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f3f7f1; color: #1f2d23; }
    .wrap { max-width: 980px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #ffffff; border-radius: 20px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
    h1 { margin-top: 0; }
    a { color: #315d42; }
    pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Storage Diagnostics</h1>
      <p>Этот fallback-экран показывает слой тяжелого контента платформы. Полный экран еще не загружен из <code>LittleFS</code>, но API уже доступен.</p>
      <pre>/api/v1/content/status
/libraries/plant_profiles.v1.json
/libraries/plant_state_rules.v1.json
/libraries/care_scenarios.v1.json</pre>
      <p><a href="/">Вернуться в shell</a></p>
    </div>
  </div>
</body>
</html>
)HTML";

const char kFallbackServiceHubHtml[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Platform / Laboratory</title>
  <style>
        body { font-family: "Segoe UI", sans-serif; margin: 0; background: #edf3ea; color: #1f2d23; }
        .wrap { max-width: 1080px; margin: 0 auto; padding: 28px 16px 36px; }
        .hero, .card { background: #ffffff; border-radius: 22px; padding: 22px; box-shadow: 0 12px 28px rgba(24, 38, 29, 0.08); }
        .hero { margin-bottom: 16px; background: linear-gradient(135deg, #234934, #4a7252); color: #f3faf4; }
        .hero p { color: rgba(243, 250, 244, 0.84); }
        .grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
        h1, h2 { margin-top: 0; }
        a { color: #315d42; }
        ul { margin: 10px 0 0; padding-left: 18px; }
        li { margin-bottom: 6px; }
        pre { background: #18221b; color: #e7f4e7; padding: 14px; border-radius: 16px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
        <div class="hero">
      <h1>Laboratory</h1>
            <p>LittleFS did not provide the full mobile Laboratory workspace, so this fallback keeps the new category-first structure visible instead of dropping back to a flat service launcher.</p>
            <p>Power context still matters: battery mode should avoid PSU-dependent bench calibration flows even when the full UI is missing.</p>
        </div>
        <div class="grid">
            <div class="card">
                <h2>Categories</h2>
                <ul>
                    <li>Light: Bench Strobe, Turret Strobe, LED Outputs</li>
                    <li>Drives: Servos, Stepper Drives</li>
                    <li>Water: Irrigation Chain, Sprayer / Turret Water</li>
                    <li>Audio: Audible Audio, Ultrasonic Tweeters</li>
                    <li>Sensors: Soil, Lidar, Air, Motion</li>
                    <li>Camera: owner-aware preview and readiness checks</li>
                    <li>Displays: Raspberry Pi touch-panel qualification stays owner-aware</li>
                    <li>Experimental stays visible even when incomplete</li>
                </ul>
            </div>
            <div class="card">
                <h2>Working Slices</h2>
                <pre>/service/strobe
/service/irrigation
/api/v1/shell/snapshot
/api/v1/logs?limit=24</pre>
            </div>
            <div class="card">
                <h2>Fallback Rules</h2>
                <ul>
                    <li>Keep blocked owner-owned slices visible.</li>
                    <li>Do not pretend peer-owned controls are local.</li>
                    <li>Keep Laboratory presets separate from product settings until explicit review.</li>
                    <li>Use Gallery &gt; Reports and the platform log as the evidence path.</li>
                </ul>
            </div>
    </div>
        <p><a href="/">Вернуться в shell</a></p>
  </div>
</body>
</html>
)HTML";

bool capabilityEnabled(uint32_t mask, core::ModuleCapability capability) {
    return (mask & static_cast<uint32_t>(capability)) != 0u;
}

const char* canonicalPathForModuleId(const char* moduleId) {
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

bool ownerAvailableForModule(const core::ModuleDescriptor& module,
                             const core::NodeHealth& localNode,
                             const core::NodeHealth& peerNode) {
    if (String(module.owner) == "rpi") {
        return peerNode.reachable && peerNode.shellReady && peerNode.syncReady &&
               peerNode.shellBaseUrl[0] != '\0';
    }

    return true;
}

String ownerNodeIdForModule(const core::ModuleDescriptor& module,
                            const core::NodeHealth& localNode,
                            const core::NodeHealth& peerNode) {
    if (String(module.owner) == "rpi") {
        return String(peerNode.nodeId);
    }

    return String(localNode.nodeId);
}

String canonicalUrlForModule(const core::ModuleDescriptor& module,
                             const core::NodeHealth& localNode,
                             const core::NodeHealth& peerNode) {
    const char* path = canonicalPathForModuleId(module.id);
    if (String(module.owner) == "rpi") {
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

String federatedAccessForModule(const core::ModuleDescriptor& module,
                                const core::NodeHealth& localNode,
                                const core::NodeHealth& peerNode) {
    (void)localNode;
    if (String(module.owner) == "rpi") {
        return ownerAvailableForModule(module, localNode, peerNode)
                   ? "peer_owner_available"
                   : "peer_owner_missing";
    }
    if (String(module.owner) == "shared") {
        return "shared_local";
    }
    return "local_owner";
}

core::ActiveMode parseActiveModeValue(const String& value) {
    if (value == "automatic") {
        return core::ActiveMode::Automatic;
    }
    if (value == "service_test") {
        return core::ActiveMode::ServiceTest;
    }
    if (value == "fault") {
        return core::ActiveMode::Fault;
    }
    if (value == "emergency") {
        return core::ActiveMode::Emergency;
    }
    return core::ActiveMode::Manual;
}

String sanitizeTestcaseField(String value, size_t maxLength) {
    value.replace('\r', ' ');
    value.replace('\n', ' ');
    value.replace(',', '/');
    value.replace('=', '-');
    value.trim();
    if (value.length() > maxLength) {
        value = value.substring(0, maxLength);
    }
    return value;
}

void appendDetailField(String& details, const char* key, const String& value, size_t maxLength) {
    if (value.length() == 0) {
        return;
    }
    details += ",";
    details += key;
    details += "=";
    details += sanitizeTestcaseField(value, maxLength);
}

String buildLaboratoryMetadataDetails(const String& sessionId,
                                      const String& sessionStatus,
                                      const String& operatorName,
                                      const String& objective,
                                      const String& hardwareProfile,
                                      const String& externalModule,
                                      const String& powerContext,
                                      const String& viewMode,
                                      const String& activeTool,
                                      const String& contextModule,
                                      const String& ownerNodeId,
                                      const String& ownerNodeType) {
    String details;
    details.reserve(220);
    appendDetailField(details, "lab_session_id", sessionId, 32);
    appendDetailField(details, "lab_session_status", sessionStatus, 16);
    appendDetailField(details, "lab_operator", operatorName, 40);
    appendDetailField(details, "lab_objective", objective, 40);
    appendDetailField(details, "lab_hardware_profile", hardwareProfile, 40);
    appendDetailField(details, "lab_external_module", externalModule, 40);
    appendDetailField(details, "lab_power_context", powerContext, 20);
    appendDetailField(details, "lab_view_mode", viewMode, 20);
    appendDetailField(details, "lab_active_tool", activeTool, 32);
    appendDetailField(details, "lab_context_module", contextModule, 32);
    appendDetailField(details, "lab_owner_node_id", ownerNodeId, 32);
    appendDetailField(details, "lab_owner_node_type", ownerNodeType, 20);
    return details;
}

bool parseTestcaseResultValue(const String& value, String& normalizedResult, const char*& level) {
    if (value == "pass") {
        normalizedResult = "pass";
        level = "info";
        return true;
    }
    if (value == "warn") {
        normalizedResult = "warn";
        level = "warning";
        return true;
    }
    if (value == "fail") {
        normalizedResult = "fail";
        level = "error";
        return true;
    }
    return false;
}

String buildTestcaseDetails(const String& caseId,
                            const String& moduleId,
                            const String& board,
                            const String& result,
                            const String& note,
                            const String& laboratoryMetadata) {
    String details;
    details.reserve(320);
    details += "case=";
    details += sanitizeTestcaseField(caseId, 24);
    details += ",module=";
    details += sanitizeTestcaseField(moduleId, 20);
    details += ",board=";
    details += sanitizeTestcaseField(board, 16);
    details += ",result=";
    details += sanitizeTestcaseField(result, 8);
    if (note.length() > 0) {
        details += ",note=";
        details += sanitizeTestcaseField(note, 20);
    }
    details += laboratoryMetadata;
    return details;
}

String buildOperatorNoteDetails(const String& caseId,
                                const String& moduleId,
                                const String& board,
                                const String& note,
                                const String& laboratoryMetadata) {
    String details;
    details.reserve(320);
    details += "case=";
    details += sanitizeTestcaseField(caseId, 24);
    details += ",module=";
    details += sanitizeTestcaseField(moduleId, 20);
    details += ",board=";
    details += sanitizeTestcaseField(board, 16);
    details += ",note=";
    details += sanitizeTestcaseField(note, 40);
    details += laboratoryMetadata;
    return details;
}

bool parseModuleStateValue(const String& value, core::ModuleState& outState) {
    if (value == "online") {
        outState = core::ModuleState::Online;
        return true;
    }
    if (value == "degraded") {
        outState = core::ModuleState::Degraded;
        return true;
    }
    if (value == "locked") {
        outState = core::ModuleState::Locked;
        return true;
    }
    if (value == "fault") {
        outState = core::ModuleState::Fault;
        return true;
    }
    if (value == "service") {
        outState = core::ModuleState::Service;
        return true;
    }
    if (value == "offline") {
        outState = core::ModuleState::Offline;
        return true;
    }
    return false;
}

core::BlockReason parseBlockReasonValue(const String& value) {
    if (value == "none") {
        return core::BlockReason::None;
    }
    if (value == "owner_unavailable") {
        return core::BlockReason::OwnerUnavailable;
    }
    if (value == "peer_sync_pending") {
        return core::BlockReason::PeerSyncPending;
    }
    if (value == "safety_interlock") {
        return core::BlockReason::SafetyInterlock;
    }
    if (value == "module_fault") {
        return core::BlockReason::ModuleFault;
    }
    if (value == "service_session_active") {
        return core::BlockReason::ServiceSessionActive;
    }
    if (value == "service_mode_required") {
        return core::BlockReason::ServiceModeRequired;
    }
    if (value == "emergency_state") {
        return core::BlockReason::EmergencyState;
    }
    if (value == "module_offline") {
        return core::BlockReason::ModuleOffline;
    }
    return core::BlockReason::Unknown;
}

}  // namespace

WebShellServer::WebShellServer(core::SystemCore& systemCore,
                               core::PlatformEventLog& platformLog,
                               net::WiFiBootstrap& wifiBootstrap,
                               storage::StorageManager& storageManager,
                               modules::irrigation::IrrigationController& irrigationController,
                               modules::strobe::StrobeBenchController& strobeBenchController)
    : systemCore_(systemCore),
      platformLog_(platformLog),
      wifiBootstrap_(wifiBootstrap),
      storageManager_(storageManager),
      shellSnapshotFacade_(systemCore, platformLog, storageManager),
      irrigationController_(irrigationController),
      strobeBenchController_(strobeBenchController),
      server_(80),
      fileSystemReady_(false),
      ready_(false) {
}

bool WebShellServer::begin() {
    fileSystemReady_ = beginFileSystem();
    registerRoutes();
    server_.begin();
    ready_ = true;
    return true;
}

void WebShellServer::update() {
    server_.handleClient();
}

bool WebShellServer::isReady() const {
    return ready_;
}

uint16_t WebShellServer::port() const {
    return 80;
}

void WebShellServer::registerRoutes() {
    server_.on("/", HTTP_GET, [this]() { handleRoot(); });
    server_.on("/federated/handoff", HTTP_GET, [this]() { handleFederatedHandoffPage(); });
    server_.on("/service", HTTP_GET, [this]() { handleServiceHubPage(); });
    server_.on("/gallery", HTTP_GET, [this]() { handleGalleryPage(); });
    server_.on("/settings", HTTP_GET, [this]() { handleSettingsPage(); });
    server_.on("/content", HTTP_GET, [this]() { handleContentPage(); });
    server_.on("/irrigation", HTTP_GET, [this]() { handleIrrigationPage(); });
    server_.on("/service/irrigation", HTTP_GET, [this]() { handleIrrigationServicePage(); });
    server_.on("/service/strobe", HTTP_GET, [this]() { handleStrobeServicePage(); });

    server_.on("/api/v1/system", HTTP_GET, [this]() { handleSystemSnapshot(); });
    server_.on("/api/v1/shell/snapshot", HTTP_GET, [this]() { handleShellSnapshot(); });
    server_.on("/api/v1/modules", HTTP_GET, [this]() { handleModules(); });
    server_.on("/api/v1/federation/route", HTTP_GET, [this]() { handleFederatedRouteInfo(); });
    server_.on("/api/v1/logs", HTTP_GET, [this]() { handleLogs(); });
    server_.on("/api/v1/reports", HTTP_GET, [this]() { handleReports(); });
    server_.on("/api/v1/reports/testcase", HTTP_POST, [this]() { handleTestcaseReport(); });
    server_.on("/api/v1/reports/note", HTTP_POST, [this]() { handleNoteReport(); });
    server_.on("/api/v1/diagnostics", HTTP_GET, [this]() { handleDiagnostics(); });
    server_.on("/api/v1/content/status", HTTP_GET, [this]() { handleContentStatus(); });
    server_.on("/api/v1/sync/state", HTTP_GET, [this]() { handleSyncState(); });
    server_.on("/api/v1/sync/heartbeat", HTTP_POST, [this]() { handleSyncHeartbeat(); });
    server_.on("/api/v1/sync/modules/push", HTTP_POST, [this]() { handleSyncModulePush(); });
    server_.on("/api/v1/sync/logs/push", HTTP_POST, [this]() { handleSyncLogPush(); });

    server_.on("/api/v1/mode/service", HTTP_POST, [this]() { handleServiceMode(); });

    server_.on("/api/v1/irrigation/status", HTTP_GET, [this]() { handleIrrigationStatus(); });
    server_.on("/api/v1/irrigation/zones", HTTP_GET, [this]() { handleIrrigationZones(); });
    server_.on("/api/v1/irrigation/automatic", HTTP_POST, [this]() { handleIrrigationAutomaticMode(); });
    server_.on("/api/v1/irrigation/start", HTTP_POST, [this]() { handleIrrigationStart(); });
    server_.on("/api/v1/irrigation/stop", HTTP_POST, [this]() { handleIrrigationStop(); });
    server_.on("/api/v1/irrigation/service/zone", HTTP_POST, [this]() { handleIrrigationServiceZone(); });
    server_.on("/api/v1/irrigation/service/sensor", HTTP_POST, [this]() { handleIrrigationServiceSensor(); });

    server_.on("/api/v1/strobe_bench/status", HTTP_GET, [this]() { handleStrobeStatus(); });
    server_.on("/api/v1/strobe_bench/presets", HTTP_GET, [this]() { handleStrobePresets(); });
    server_.on("/api/v1/strobe_bench/arm", HTTP_POST, [this]() { handleStrobeArm(); });
    server_.on("/api/v1/strobe_bench/disarm", HTTP_POST, [this]() { handleStrobeDisarm(); });
    server_.on("/api/v1/strobe_bench/stop", HTTP_POST, [this]() { handleStrobeStop(); });
    server_.on("/api/v1/strobe_bench/abort", HTTP_POST, [this]() { handleStrobeAbort(); });
    server_.on("/api/v1/strobe_bench/pulse", HTTP_POST, [this]() { handleStrobePulse(); });
    server_.on("/api/v1/strobe_bench/burst", HTTP_POST, [this]() { handleStrobeBurst(); });
    server_.on("/api/v1/strobe_bench/loop", HTTP_POST, [this]() { handleStrobeLoop(); });
    server_.on("/api/v1/strobe_bench/continuous", HTTP_POST, [this]() { handleStrobeContinuous(); });
    server_.on("/api/v1/strobe_bench/preset", HTTP_POST, [this]() { handleStrobePreset(); });

    server_.onNotFound([this]() { handleNotFound(); });
}

void WebShellServer::handleRoot() {
    if (!sendFileFromFileSystem("/index.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildIndexHtml());
    }
}

void WebShellServer::handleFederatedHandoffPage() {
    server_.send(200, "text/html; charset=utf-8", buildFederatedHandoffHtml());
}

void WebShellServer::handleServiceHubPage() {
    if (!sendFileFromFileSystem("/service/index.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildServiceHubHtml());
    }
}

void WebShellServer::handleGalleryPage() {
    if (!sendFileFromFileSystem("/gallery/index.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildGalleryHtml());
    }
}

void WebShellServer::handleSettingsPage() {
    if (!sendFileFromFileSystem("/settings/index.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildSettingsHtml());
    }
}

void WebShellServer::handleContentPage() {
    if (!sendFileFromFileSystem("/content/index.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildContentHtml());
    }
}

void WebShellServer::handleIrrigationPage() {
    if (!sendFileFromFileSystem("/irrigation/index.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildIrrigationHtml());
    }
}

void WebShellServer::handleIrrigationServicePage() {
    if (!sendFileFromFileSystem("/service/irrigation.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildIrrigationServiceHtml());
    }
}

void WebShellServer::handleStrobeServicePage() {
    if (!sendFileFromFileSystem("/service/strobe.html", "text/html; charset=utf-8")) {
        server_.send(200, "text/html; charset=utf-8", buildStrobeServiceHtml());
    }
}

void WebShellServer::handleSystemSnapshot() {
    server_.send(200, "application/json; charset=utf-8", systemCore_.buildSystemSnapshotJson());
}

void WebShellServer::handleShellSnapshot() {
    // Этот endpoint не заменяет продуктовые API.
    // Он нужен как короткая и понятная сводка для shell-страниц.
    server_.send(200, "application/json; charset=utf-8", shellSnapshotFacade_.buildShellSnapshotJson());
}

void WebShellServer::handleModules() {
    server_.send(200, "application/json; charset=utf-8", buildModulesJson());
}

void WebShellServer::handleFederatedRouteInfo() {
    server_.send(200,
                 "application/json; charset=utf-8",
                 buildFederatedRouteInfoJson(server_.arg("module_id").c_str()));
}

void WebShellServer::handleLogs() {
    size_t limit = 20;
    if (server_.hasArg("limit")) {
        const long value = server_.arg("limit").toInt();
        if (value > 0) {
            limit = static_cast<size_t>(value);
        }
    }
    server_.send(200, "application/json; charset=utf-8", buildLogsJson(limit));
}

void WebShellServer::handleReports() {
    size_t limit = 20;
    if (server_.hasArg("limit")) {
        const long value = server_.arg("limit").toInt();
        if (value > 0) {
            limit = static_cast<size_t>(value);
        }
    }
    server_.send(200,
                 "application/json; charset=utf-8",
                 buildReportsJson(limit,
                                  server_.arg("surface"),
                                  server_.arg("entry_type"),
                                  server_.arg("severity"),
                                  server_.arg("origin_node")));
}

void WebShellServer::handleTestcaseReport() {
    const String caseId = server_.arg("case_id");
    const String moduleId = server_.arg("module_id");
    String board = server_.arg("board");
    const String note = server_.arg("note");
    const String rawResult = server_.arg("result");
    const String laboratoryMetadata = buildLaboratoryMetadataDetails(server_.arg("lab_session_id"),
                                                                     server_.arg("lab_session_status"),
                                                                     server_.arg("lab_operator"),
                                                                     server_.arg("lab_objective"),
                                                                     server_.arg("lab_hardware_profile"),
                                                                     server_.arg("lab_external_module"),
                                                                     server_.arg("lab_power_context"),
                                                                     server_.arg("lab_view_mode"),
                                                                     server_.arg("lab_active_tool"),
                                                                     server_.arg("lab_context_module"),
                                                                     server_.arg("lab_owner_node_id"),
                                                                     server_.arg("lab_owner_node_type"));

    String normalizedResult;
    const char* level = "info";
    if (caseId.length() == 0 || moduleId.length() == 0 || !parseTestcaseResultValue(rawResult, normalizedResult, level)) {
        server_.send(200,
                     "application/json; charset=utf-8",
                     "{\"command\":\"reports_testcase\",\"accepted\":false,"
                     "\"message\":\"case_id, module_id, and result=pass|fail|warn are required\"}");
        return;
    }

    if (board.length() == 0) {
        board = core::nodeTypeToString(systemCore_.localNode().nodeType);
    }

    const String details = buildTestcaseDetails(caseId, moduleId, board, normalizedResult, note, laboratoryMetadata);
    String message = String("testcase ") + sanitizeTestcaseField(caseId, 24) +
                     " recorded for " + sanitizeTestcaseField(moduleId, 20) +
                     " as " + normalizedResult;
    if (message.length() > 79) {
        message = message.substring(0, 79);
    }

    platformLog_.addLocal("testcase_capture",
                          level,
                          "testcase_result_recorded",
                          message.c_str(),
                          details.c_str());
    server_.send(200,
                 "application/json; charset=utf-8",
                 "{\"command\":\"reports_testcase\",\"accepted\":true,\"message\":\"testcase result recorded\"}");
}

void WebShellServer::handleNoteReport() {
    const String note = server_.arg("note");
    const String moduleId = server_.arg("module_id");
    const String caseId = server_.arg("case_id");
    String board = server_.arg("board");
    const String laboratoryMetadata = buildLaboratoryMetadataDetails(server_.arg("lab_session_id"),
                                                                     server_.arg("lab_session_status"),
                                                                     server_.arg("lab_operator"),
                                                                     server_.arg("lab_objective"),
                                                                     server_.arg("lab_hardware_profile"),
                                                                     server_.arg("lab_external_module"),
                                                                     server_.arg("lab_power_context"),
                                                                     server_.arg("lab_view_mode"),
                                                                     server_.arg("lab_active_tool"),
                                                                     server_.arg("lab_context_module"),
                                                                     server_.arg("lab_owner_node_id"),
                                                                     server_.arg("lab_owner_node_type"));

    if (note.length() == 0 || moduleId.length() == 0) {
        server_.send(200,
                     "application/json; charset=utf-8",
                     "{\"command\":\"reports_note\",\"accepted\":false,"
                     "\"message\":\"note and module_id are required\"}");
        return;
    }

    if (board.length() == 0) {
        board = core::nodeTypeToString(systemCore_.localNode().nodeType);
    }

    const String sanitizedMessage = sanitizeTestcaseField(note, 79);
    const String details = buildOperatorNoteDetails(caseId, moduleId, board, note, laboratoryMetadata);
    platformLog_.addLocal("testcase_capture",
                          "info",
                          "operator_note",
                          sanitizedMessage.c_str(),
                          details.c_str());
    server_.send(200,
                 "application/json; charset=utf-8",
                 "{\"command\":\"reports_note\",\"accepted\":true,\"message\":\"operator note recorded\"}");
}

void WebShellServer::handleDiagnostics() {
    server_.send(200, "application/json; charset=utf-8", buildDiagnosticsJson());
}

void WebShellServer::handleContentStatus() {
    server_.send(200, "application/json; charset=utf-8", storageManager_.buildContentStatusJson());
}

void WebShellServer::handleSyncState() {
    server_.send(200, "application/json; charset=utf-8", buildSyncStateJson());
}

void WebShellServer::handleSyncHeartbeat() {
    const String nodeId = server_.arg("node_id");
    const String shellBaseUrl = server_.arg("shell_base_url");
    const bool reachable = true;
    const bool wifiReady = server_.arg("wifi_ready") != "0";
    const bool shellReady = server_.arg("shell_ready") != "0";
    const bool syncReady = server_.arg("sync_ready") == "1";
    const core::ActiveMode reportedMode = parseActiveModeValue(server_.arg("reported_mode"));

    systemCore_.setPeerNodeStatus(nodeId.c_str(),
                                  shellBaseUrl.c_str(),
                                  reachable,
                                  wifiReady,
                                  shellReady,
                                  syncReady,
                                  reportedMode,
                                  millis());
    const String detail = String("peer=") + nodeId + ", sync_ready=" + (syncReady ? "true" : "false");
    platformLog_.addLocal("sync_core", "info", "peer_heartbeat", "peer heartbeat accepted", detail.c_str());

    server_.send(200, "application/json; charset=utf-8",
                 buildSyncCommandResponseJson("sync_heartbeat", true, "peer heartbeat accepted"));
}

void WebShellServer::handleSyncModulePush() {
    if (!server_.hasArg("id") || !server_.hasArg("state")) {
        server_.send(200, "application/json; charset=utf-8",
                     buildSyncCommandResponseJson("sync_module_push", false,
                                                  "id and state arguments are required"));
        return;
    }

    core::ModuleState state = core::ModuleState::Offline;
    if (!parseModuleStateValue(server_.arg("state"), state)) {
        server_.send(200, "application/json; charset=utf-8",
                     buildSyncCommandResponseJson("sync_module_push", false,
                                                  "state value is not supported"));
        return;
    }

    const core::BlockReason reason = parseBlockReasonValue(server_.arg("block_reason"));
    const bool accepted = systemCore_.updatePeerOwnedModuleState(server_.arg("id").c_str(), state, reason);
    const String detail = String("module=") + server_.arg("id") + ", state=" + server_.arg("state");
    platformLog_.addLocal("sync_core",
                          accepted ? "info" : "warn",
                          "peer_module_push",
                          accepted ? "peer module state updated"
                                   : "peer module state rejected",
                          detail.c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildSyncCommandResponseJson(
                     "sync_module_push",
                     accepted,
                     accepted ? "peer module state updated"
                              : "module was rejected because it is unknown or not owned by peer"));
}

void WebShellServer::handleSyncLogPush() {
    if (!server_.hasArg("origin_node") || !server_.hasArg("origin_event_id")) {
        server_.send(200, "application/json; charset=utf-8",
                     buildSyncCommandResponseJson("sync_log_push", false,
                                                  "origin_node and origin_event_id are required"));
        return;
    }

    const bool accepted = platformLog_.ingestRemote(server_.arg("origin_node").c_str(),
                                                    server_.arg("origin_event_id").c_str(),
                                                    server_.arg("source").c_str(),
                                                    server_.arg("level").c_str(),
                                                    server_.arg("type").c_str(),
                                                    server_.arg("message").c_str(),
                                                    server_.arg("details").c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildSyncCommandResponseJson(
                     "sync_log_push",
                     accepted,
                     accepted ? "peer log entry mirrored" : "peer log entry already known or invalid"));
}

void WebShellServer::handleServiceMode() {
    const bool enable = server_.arg("enabled") == "1";
    if (enable) {
        systemCore_.setActiveMode(core::ActiveMode::ServiceTest);
        platformLog_.addLocal("service_mode", "info", "service_mode_changed", "service mode enabled");
        server_.send(200, "application/json; charset=utf-8",
                     buildCommandResponseJson("service_mode", modules::strobe::CommandResult::Accepted,
                                              "service mode enabled"));
        return;
    }

    strobeBenchController_.forceServiceExit();
    systemCore_.setActiveMode(core::ActiveMode::Manual);
    platformLog_.addLocal("service_mode", "info", "service_mode_changed", "service mode disabled");
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("service_mode", modules::strobe::CommandResult::Accepted,
                                          "service mode disabled"));
}

void WebShellServer::handleIrrigationStatus() {
    server_.send(200, "application/json; charset=utf-8", buildIrrigationStatusJson());
}

void WebShellServer::handleIrrigationZones() {
    server_.send(200, "application/json; charset=utf-8", buildIrrigationZonesJson());
}

void WebShellServer::handleIrrigationAutomaticMode() {
    const bool enable = server_.arg("enabled") == "1";
    if (enable && serviceModeActive()) {
        platformLog_.addLocal("irrigation",
                              "warn",
                              "irrigation_auto_mode",
                              "automatic irrigation mode rejected while service mode is active");
        server_.send(200,
                     "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_auto_mode",
                         modules::irrigation::CommandResult::ServiceModeRequired,
                         "automatic mode is blocked while service mode is active"));
        return;
    }

    systemCore_.setActiveMode(enable ? core::ActiveMode::Automatic : core::ActiveMode::Manual);
    platformLog_.addLocal("irrigation",
                          "info",
                          "irrigation_auto_mode",
                          enable ? "automatic irrigation mode enabled"
                                 : "automatic irrigation mode disabled");
    server_.send(200,
                 "application/json; charset=utf-8",
                 buildIrrigationCommandResponseJson(
                     "irrigation_auto_mode",
                     modules::irrigation::CommandResult::Accepted,
                     enable ? "automatic irrigation mode enabled"
                            : "automatic irrigation mode disabled"));
}

void WebShellServer::handleIrrigationStart() {
    if (!server_.hasArg("zone")) {
        server_.send(200, "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_start",
                         modules::irrigation::CommandResult::InvalidArguments,
                         "zone argument is required"));
        return;
    }

    const long zoneValue = server_.arg("zone").toInt();
    if (zoneValue < 0) {
        server_.send(200, "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_start",
                         modules::irrigation::CommandResult::InvalidArguments,
                         "zone must be non-negative"));
        return;
    }

    uint32_t durationMs = modules::irrigation::kDefaultManualDurationMs;
    if (server_.hasArg("duration_ms")) {
        durationMs = static_cast<uint32_t>(server_.arg("duration_ms").toInt());
    }

    const auto result = irrigationController_.startManualZone(static_cast<size_t>(zoneValue), durationMs);
    const String detail = String("zone=") + String(zoneValue) + ", duration_ms=" + String(durationMs);
    platformLog_.addLocal("irrigation",
                          result == modules::irrigation::CommandResult::Accepted ? "info" : "warn",
                          "irrigation_start",
                          "manual irrigation command processed",
                          detail.c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildIrrigationCommandResponseJson(
                     "irrigation_start", result, "manual irrigation command processed"));
}

void WebShellServer::handleIrrigationStop() {
    const auto result = irrigationController_.stopAll();
    platformLog_.addLocal("irrigation",
                          result == modules::irrigation::CommandResult::Accepted ? "info" : "warn",
                          "irrigation_stop",
                          "stop command processed");
    server_.send(200, "application/json; charset=utf-8",
                 buildIrrigationCommandResponseJson(
                     "irrigation_stop", result, "stop command processed"));
}

void WebShellServer::handleIrrigationServiceZone() {
    if (!server_.hasArg("zone")) {
        server_.send(200, "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_service_zone",
                         modules::irrigation::CommandResult::InvalidArguments,
                         "zone argument is required"));
        return;
    }

    const long zoneValue = server_.arg("zone").toInt();
    if (zoneValue < 0) {
        server_.send(200, "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_service_zone",
                         modules::irrigation::CommandResult::InvalidArguments,
                         "zone must be non-negative"));
        return;
    }

    uint32_t durationMs = modules::irrigation::kDefaultServiceDurationMs;
    if (server_.hasArg("duration_ms")) {
        durationMs = static_cast<uint32_t>(server_.arg("duration_ms").toInt());
    }

    const auto result =
        irrigationController_.startServiceZone(static_cast<size_t>(zoneValue), durationMs);
    const String detail = String("zone=") + String(zoneValue) + ", duration_ms=" + String(durationMs);
    platformLog_.addLocal("irrigation",
                          result == modules::irrigation::CommandResult::Accepted ? "info" : "warn",
                          "irrigation_service_zone",
                          "service zone command processed",
                          detail.c_str());
    server_.send(200,
                 "application/json; charset=utf-8",
                 buildIrrigationCommandResponseJson(
                     "irrigation_service_zone", result, "service zone command processed"));
}

void WebShellServer::handleIrrigationServiceSensor() {
    if (!server_.hasArg("zone") || !server_.hasArg("profile")) {
        server_.send(200, "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_service_sensor",
                         modules::irrigation::CommandResult::InvalidArguments,
                         "zone and profile arguments are required"));
        return;
    }

    const long zoneValue = server_.arg("zone").toInt();
    if (zoneValue < 0) {
        server_.send(200, "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_service_sensor",
                         modules::irrigation::CommandResult::InvalidArguments,
                         "zone must be non-negative"));
        return;
    }

    if (!serviceModeActive()) {
        server_.send(200, "application/json; charset=utf-8",
                     buildIrrigationCommandResponseJson(
                         "irrigation_service_sensor",
                         modules::irrigation::CommandResult::ServiceModeRequired,
                         "service sensor commands require service mode"));
        return;
    }

    const bool applied = irrigationController_.applyServiceSensorProfile(
        static_cast<size_t>(zoneValue), server_.arg("profile").c_str());
    const String detail = String("zone=") + String(zoneValue) + ", profile=" + server_.arg("profile");
    platformLog_.addLocal("irrigation",
                          applied ? "info" : "warn",
                          "irrigation_service_sensor",
                          applied ? "service sensor profile applied"
                                  : "service sensor profile rejected",
                          detail.c_str());
    server_.send(200,
                 "application/json; charset=utf-8",
                 buildIrrigationCommandResponseJson(
                     "irrigation_service_sensor",
                     applied ? modules::irrigation::CommandResult::Accepted
                             : modules::irrigation::CommandResult::InvalidArguments,
                     applied ? "service sensor profile applied"
                             : "service sensor profile rejected"));
}

void WebShellServer::handleStrobeStatus() {
    server_.send(200, "application/json; charset=utf-8", buildStrobeStatusJson());
}

void WebShellServer::handleStrobePresets() {
    server_.send(200, "application/json; charset=utf-8", buildStrobePresetsJson());
}

void WebShellServer::handleStrobeArm() {
    const auto result = strobeBenchController_.arm(serviceModeActive());
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_arm",
                          "arm command processed");
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_arm", result, "arm command processed"));
}

void WebShellServer::handleStrobeDisarm() {
    const auto result = strobeBenchController_.disarm();
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_disarm",
                          "disarm command processed");
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_disarm", result, "disarm command processed"));
}

void WebShellServer::handleStrobeStop() {
    const auto result = strobeBenchController_.stop();
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_stop",
                          "stop command processed");
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_stop", result, "stop command processed"));
}

void WebShellServer::handleStrobeAbort() {
    const auto result = strobeBenchController_.abort();
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_abort",
                          "abort command processed");
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_abort", result, "abort command processed"));
}

void WebShellServer::handleStrobePulse() {
    const uint32_t durationMs = static_cast<uint32_t>(server_.arg("duration_ms").toInt());
    const auto result = strobeBenchController_.pulse(serviceModeActive(), durationMs);
    const String detail = String("duration_ms=") + String(durationMs);
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_pulse",
                          "pulse command processed",
                          detail.c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_pulse", result, "pulse command processed"));
}

void WebShellServer::handleStrobeBurst() {
    const uint32_t count = static_cast<uint32_t>(server_.arg("count").toInt());
    const uint32_t onMs = static_cast<uint32_t>(server_.arg("on_ms").toInt());
    const uint32_t offMs = static_cast<uint32_t>(server_.arg("off_ms").toInt());
    const auto result = strobeBenchController_.burst(serviceModeActive(), count, onMs, offMs);
    const String detail = String("count=") + String(count) + ", on_ms=" + String(onMs) +
                          ", off_ms=" + String(offMs);
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_burst",
                          "burst command processed",
                          detail.c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_burst", result, "burst command processed"));
}

void WebShellServer::handleStrobeLoop() {
    const uint32_t onMs = static_cast<uint32_t>(server_.arg("on_ms").toInt());
    const uint32_t offMs = static_cast<uint32_t>(server_.arg("off_ms").toInt());
    const auto result = strobeBenchController_.loop(serviceModeActive(), onMs, offMs);
    const String detail = String("on_ms=") + String(onMs) + ", off_ms=" + String(offMs);
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_loop",
                          "loop command processed",
                          detail.c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_loop", result, "loop command processed"));
}

void WebShellServer::handleStrobeContinuous() {
    const uint32_t timeoutMs = static_cast<uint32_t>(server_.arg("timeout_ms").toInt());
    const auto result = strobeBenchController_.continuousOn(serviceModeActive(), timeoutMs);
    const String detail = String("timeout_ms=") + String(timeoutMs);
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_continuous",
                          "continuous-on command processed",
                          detail.c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_continuous",
                                          result,
                                          "continuous-on command processed"));
}

void WebShellServer::handleStrobePreset() {
    const String presetId = server_.arg("id");
    const auto result = strobeBenchController_.runPreset(serviceModeActive(), presetId.c_str());
    const String detail = String("preset_id=") + presetId;
    platformLog_.addLocal("strobe_bench",
                          result == modules::strobe::CommandResult::Accepted ? "info" : "warn",
                          "strobe_preset",
                          "preset command processed",
                          detail.c_str());
    server_.send(200, "application/json; charset=utf-8",
                 buildCommandResponseJson("strobe_preset", result, "preset command processed"));
}

void WebShellServer::handleNotFound() {
    const String requestPath = server_.uri();
    if (storageManager_.isManagedContentPath(requestPath)) {
        if (storageManager_.streamManagedContent(server_, requestPath)) {
            return;
        }

        server_.send(404,
                     "application/json; charset=utf-8",
                     "{\"error\":\"content_not_found\",\"message\":\"Managed content file is missing on SD storage\"}");
        return;
    }

    server_.send(404, "application/json; charset=utf-8",
                 "{\"error\":\"not_found\",\"message\":\"Route is not implemented in stage-sync-bootstrap\"}");
}

bool WebShellServer::beginFileSystem() {
    // Автоформатирование здесь специально не включаем.
    // Если файловая система отсутствует или еще не загружена, shell спокойно уйдет в fallback,
    // а инженер отдельно выполнит uploadfs без молчаливой потери данных.
    return LittleFS.begin(false);
}

bool WebShellServer::sendFileFromFileSystem(const char* path, const char* contentType) {
    if (!fileSystemReady_) {
        return false;
    }

    if (path == nullptr || !LittleFS.exists(path)) {
        return false;
    }

    File file = LittleFS.open(path, "r");
    if (!file) {
        return false;
    }

    server_.streamFile(file, contentType);
    file.close();
    return true;
}

String WebShellServer::buildIndexHtml() const {
    return String(kFallbackIndexHtml);
}

String WebShellServer::buildFederatedHandoffHtml() const {
    return String(kFallbackFederatedHandoffHtml);
}

String WebShellServer::buildServiceHubHtml() const {
    return String(kFallbackServiceHubHtml);
}

String WebShellServer::buildGalleryHtml() const {
    return String(kFallbackGalleryHtml);
}

String WebShellServer::buildSettingsHtml() const {
    return String(kFallbackSettingsHtml);
}

String WebShellServer::buildContentHtml() const {
    return String(kFallbackContentHtml);
}

String WebShellServer::buildIrrigationHtml() const {
    return String(kFallbackIrrigationHtml);
}

String WebShellServer::buildIrrigationServiceHtml() const {
    return String(kFallbackIrrigationServiceHtml);
}

String WebShellServer::buildStrobeServiceHtml() const {
    return String(kFallbackStrobeServiceHtml);
}

String WebShellServer::buildModulesJson() const {
    const core::ModuleRegistry& registry = systemCore_.registry();
    const core::NodeHealth& localNode = systemCore_.localNode();
    const core::NodeHealth& peerNode = systemCore_.peerNode();
    String json;
    json.reserve(2200);
    json += "[";

    for (size_t index = 0; index < registry.count(); ++index) {
        const core::ModuleDescriptor* module = registry.at(index);
        if (module == nullptr) {
            continue;
        }

        if (index > 0) {
            json += ",";
        }

        json += "{";
        json += "\"id\":\"";
        json += module->id;
        json += "\",\"title\":\"";
        json += module->title;
        json += "\",\"owner\":\"";
        json += module->owner;
        json += "\",\"profile\":\"";
        json += module->profile;
        json += "\",\"ui_group\":\"";
        json += module->uiGroup;
        json += "\",\"state\":\"";
        json += core::moduleStateToString(module->state);
        json += "\",\"block_reason\":\"";
        json += core::blockReasonToString(module->blockReason);
        json += "\",\"owner_node_id\":\"";
        json += ownerNodeIdForModule(*module, localNode, peerNode);
        json += "\",\"owner_available\":";
        json += ownerAvailableForModule(*module, localNode, peerNode) ? "true" : "false";
        json += ",\"canonical_path\":\"";
        json += canonicalPathForModuleId(module->id);
        json += "\",\"canonical_url\":\"";
        json += canonicalUrlForModule(*module, localNode, peerNode);
        json += "\",\"federated_access\":\"";
        json += federatedAccessForModule(*module, localNode, peerNode);
        json += "\",\"visible\":";
        json += module->visible ? "true" : "false";
        json += ",\"manual_page\":";
        json += module->manualPage ? "true" : "false";
        json += ",\"service_page\":";
        json += module->servicePage ? "true" : "false";
        json += ",\"capabilities\":[";

        bool firstCapability = true;
        auto appendCapability = [&](core::ModuleCapability capability, const char* name) {
            if (!capabilityEnabled(module->capabilities, capability)) {
                return;
            }

            if (!firstCapability) {
                json += ",";
            }

            json += "\"";
            json += name;
            json += "\"";
            firstCapability = false;
        };

        appendCapability(core::CapabilityStatusPage, "status_page");
        appendCapability(core::CapabilityManualPage, "manual_page");
        appendCapability(core::CapabilityServicePage, "service_page");
        appendCapability(core::CapabilityLogs, "logs");
        appendCapability(core::CapabilityCommandable, "commandable");
        appendCapability(core::CapabilityDiagnostics, "diagnostics");

        json += "]";
        json += "}";
    }

    json += "]";
    return json;
}

String WebShellServer::buildFederatedRouteInfoJson(const char* moduleId) const {
    const core::ModuleDescriptor* module = systemCore_.registry().find(moduleId);
    const core::NodeHealth& localNode = systemCore_.localNode();
    const core::NodeHealth& peerNode = systemCore_.peerNode();

    String json;
    json.reserve(720);
    json += "{";
    json += "\"module_id\":\"";
    json += moduleId != nullptr ? moduleId : "";
    json += "\",\"module_found\":";
    json += module != nullptr ? "true" : "false";

    if (module != nullptr) {
        json += ",\"title\":\"";
        json += module->title;
        json += "\",\"owner\":\"";
        json += module->owner;
        json += "\",\"owner_node_id\":\"";
        json += ownerNodeIdForModule(*module, localNode, peerNode);
        json += "\",\"owner_available\":";
        json += ownerAvailableForModule(*module, localNode, peerNode) ? "true" : "false";
        json += ",\"state\":\"";
        json += core::moduleStateToString(module->state);
        json += "\",\"block_reason\":\"";
        json += core::blockReasonToString(module->blockReason);
        json += "\",\"canonical_path\":\"";
        json += canonicalPathForModuleId(module->id);
        json += "\",\"canonical_url\":\"";
        json += canonicalUrlForModule(*module, localNode, peerNode);
        json += "\",\"federated_access\":\"";
        json += federatedAccessForModule(*module, localNode, peerNode);
        json += "\",\"current_shell_node_id\":\"";
        json += localNode.nodeId;
        json += "\",\"current_shell_base_url\":\"";
        json += localNode.shellBaseUrl;
        json += "\"";
    }

    json += "}";
    return json;
}

String WebShellServer::buildLogsJson(size_t limit) const {
    return platformLog_.buildSnapshotJson(limit);
}

String WebShellServer::buildReportsJson(size_t limit,
                                        const String& surfaceFilter,
                                        const String& entryTypeFilter,
                                        const String& severityFilter,
                                        const String& originNodeFilter) const {
    return platformLog_.buildReportsJson(limit,
                                         surfaceFilter.c_str(),
                                         entryTypeFilter.c_str(),
                                         severityFilter.c_str(),
                                         originNodeFilter.c_str());
}

String WebShellServer::buildDiagnosticsJson() const {
    const core::NodeHealth& peer = systemCore_.peerNode();

    String json;
    json.reserve(1100);

    json += "{";
    json += "\"shell_ready\":";
    json += ready_ ? "true" : "false";
    json += ",\"wifi_ready\":";
    json += wifiBootstrap_.isReady() ? "true" : "false";
    json += ",\"littlefs_ready\":";
    json += fileSystemReady_ ? "true" : "false";
    json += ",\"access_point_ssid\":\"";
    json += wifiBootstrap_.accessPointSsid();
    json += "\",\"access_point_ip\":\"";
    json += wifiBootstrap_.accessPointIp().toString();
    json += "\",\"local_shell_base_url\":\"";
    json += systemCore_.localNode().shellBaseUrl;
    json += "\",\"peer_shell_base_url\":\"";
    json += systemCore_.peerNode().shellBaseUrl;
    json += "\",\"server_port\":";
    json += String(port());
    json += ",\"log_count\":";
    json += String(platformLog_.count());
    json += ",\"peer_reachable\":";
    json += peer.reachable ? "true" : "false";
    json += ",\"peer_sync_ready\":";
    json += peer.syncReady ? "true" : "false";
    json += ",\"peer_reported_mode\":\"";
    json += core::activeModeToString(peer.reportedMode);
    json += "\",\"content_status\":";
    json += storageManager_.buildContentStatusJson();
    json += "}";

    return json;
}

String WebShellServer::buildSyncStateJson() const {
    const core::NodeHealth& peer = systemCore_.peerNode();
    const core::ModuleRegistry& registry = systemCore_.registry();

    String json;
    json.reserve(1200);
    json += "{";
    json += "\"peer_node_id\":\"";
    json += peer.nodeId;
    json += "\",\"peer_reachable\":";
    json += peer.reachable ? "true" : "false";
    json += ",\"peer_wifi_ready\":";
    json += peer.wifiReady ? "true" : "false";
    json += ",\"peer_shell_ready\":";
    json += peer.shellReady ? "true" : "false";
    json += ",\"peer_sync_ready\":";
    json += peer.syncReady ? "true" : "false";
    json += ",\"peer_reported_mode\":\"";
    json += core::activeModeToString(peer.reportedMode);
    json += "\",\"peer_shell_base_url\":\"";
    json += peer.shellBaseUrl;
    json += "\",\"remote_modules\":[";

    bool first = true;
    for (size_t index = 0; index < registry.count(); ++index) {
        const core::ModuleDescriptor* module = registry.at(index);
        if (module == nullptr) {
            continue;
        }

        if (String(module->owner) != "rpi") {
            continue;
        }

        if (!first) {
            json += ",";
        }

        json += "{";
        json += "\"id\":\"";
        json += module->id;
        json += "\",\"state\":\"";
        json += core::moduleStateToString(module->state);
        json += "\",\"block_reason\":\"";
        json += core::blockReasonToString(module->blockReason);
        json += "\"}";
        first = false;
    }

    json += "]}";
    return json;
}

String WebShellServer::buildSyncCommandResponseJson(const char* command,
                                                    bool accepted,
                                                    const char* message) const {
    const core::NodeHealth& peer = systemCore_.peerNode();

    String json;
    json.reserve(384);
    json += "{";
    json += "\"command\":\"";
    json += command != nullptr ? command : "";
    json += "\",\"accepted\":";
    json += accepted ? "true" : "false";
    json += ",\"message\":\"";
    json += message != nullptr ? message : "";
    json += "\",\"peer_reachable\":";
    json += peer.reachable ? "true" : "false";
    json += ",\"peer_sync_ready\":";
    json += peer.syncReady ? "true" : "false";
    json += "}";
    return json;
}

String WebShellServer::buildIrrigationStatusJson() const {
    const auto status = irrigationController_.status();
    const auto& environment = irrigationController_.environment();
    String json;
    json.reserve(960);

    json += "{";
    json += "\"state\":\"";
    json += modules::irrigation::IrrigationController::moduleStateName(status.state);
    json += "\",\"dry_run\":";
    json += status.dryRun ? "true" : "false";
    json += ",\"outputs_enabled\":";
    json += status.outputsEnabled ? "true" : "false";
    json += ",\"pump_on\":";
    json += status.pumpOn ? "true" : "false";
    json += ",\"fault_latched\":";
    json += status.faultLatched ? "true" : "false";
    json += ",\"automatic_mode_enabled\":";
    json += status.automaticModeEnabled ? "true" : "false";
    json += ",\"service_mode_active\":";
    json += status.serviceModeActive ? "true" : "false";
    json += ",\"sensor_fault_present\":";
    json += status.sensorFaultPresent ? "true" : "false";
    json += ",\"active_zone_index\":";
    json += String(status.activeZoneIndex);
    json += ",\"active_zone_remaining_ms\":";
    json += String(status.activeZoneRemainingMs);
    json += ",\"active_run_source\":\"";
    json += modules::irrigation::IrrigationController::runSourceName(status.activeRunSource);
    json += "\"";
    json += ",\"uptime_ms\":";
    json += String(status.uptimeMs);
    json += ",\"completed_cycles\":";
    json += String(status.completedCycles);
    json += ",\"zones_total\":";
    json += String(irrigationController_.zoneCount());
    json += ",\"driest_zone_index\":";
    json += String(status.driestZoneIndex);
    json += ",\"driest_moisture_percent\":";
    json += String(status.driestMoisturePercent, 1);
    json += ",\"environment\":{";
    json += "\"air_temperature_c\":";
    json += String(environment.airTemperatureC, 1);
    json += ",\"air_humidity_percent\":";
    json += String(environment.airHumidityPercent, 1);
    json += ",\"water_reserve_percent\":";
    json += String(environment.waterReservePercent, 1);
    json += ",\"simulated\":";
    json += environment.simulated ? "true" : "false";
    json += "}";
    json += "}";

    return json;
}

String WebShellServer::buildIrrigationZonesJson() const {
    String json;
    json.reserve(2600);
    json += "[";

    for (size_t index = 0; index < irrigationController_.zoneCount(); ++index) {
        const modules::irrigation::ZoneStatus* zone = irrigationController_.zoneAt(index);
        if (zone == nullptr) {
            continue;
        }

        if (index > 0) {
            json += ",";
        }

        json += "{";
        json += "\"index\":";
        json += String(zone->index);
        json += ",\"id\":\"";
        json += zone->id;
        json += "\",\"title\":\"";
        json += zone->title;
        json += "\",\"state\":\"";
        json += modules::irrigation::IrrigationController::zoneStateName(zone->state);
        json += "\",\"soil_moisture_percent\":";
        json += String(zone->soilMoisturePercent, 1);
        json += ",\"target_moisture_percent\":";
        json += String(zone->targetMoisturePercent, 1);
        json += ",\"remaining_ms\":";
        json += String(zone->remainingMs);
        json += ",\"valve_open\":";
        json += zone->valveOpen ? "true" : "false";
        json += ",\"enabled\":";
        json += zone->enabled ? "true" : "false";
        json += ",\"auto_enabled\":";
        json += zone->autoEnabled ? "true" : "false";
        json += ",\"sensor_fault\":";
        json += zone->sensorFault ? "true" : "false";
        json += ",\"sensor_simulated\":";
        json += zone->sensorSimulated ? "true" : "false";
        json += ",\"last_reading_ms\":";
        json += String(zone->lastReadingMs);
        json += "}";
    }

    json += "]";
    return json;
}

String WebShellServer::buildIrrigationCommandResponseJson(
    const char* command,
    modules::irrigation::CommandResult result,
    const char* message) const {
    const auto status = irrigationController_.status();

    String json;
    json.reserve(448);
    json += "{";
    json += "\"command\":\"";
    json += command != nullptr ? command : "";
    json += "\",\"result\":\"";
    json += modules::irrigation::IrrigationController::commandResultName(result);
    json += "\",\"accepted\":";
    json += result == modules::irrigation::CommandResult::Accepted ? "true" : "false";
    json += ",\"message\":\"";
    json += message != nullptr ? message : "";
    json += "\",\"dry_run\":";
    json += status.dryRun ? "true" : "false";
    json += ",\"automatic_mode_enabled\":";
    json += status.automaticModeEnabled ? "true" : "false";
    json += ",\"service_mode_active\":";
    json += status.serviceModeActive ? "true" : "false";
    json += ",\"active_zone_index\":";
    json += String(status.activeZoneIndex);
    json += ",\"active_run_source\":\"";
    json += modules::irrigation::IrrigationController::runSourceName(status.activeRunSource);
    json += "\"";
    json += "}";
    return json;
}

String WebShellServer::buildStrobeStatusJson() const {
    const auto status = strobeBenchController_.status();
    String json;
    json.reserve(768);

    json += "{";
    json += "\"service_mode_active\":";
    json += serviceModeActive() ? "true" : "false";
    json += ",\"state\":\"";
    json += modules::strobe::StrobeBenchController::stateName(status.state);
    json += "\",\"pattern\":\"";
    json += modules::strobe::StrobeBenchController::patternName(status.pattern);
    json += "\",\"last_stop_reason\":\"";
    json += modules::strobe::StrobeBenchController::stopReasonName(status.lastStopReason);
    json += "\",\"fault\":\"";
    json += modules::strobe::StrobeBenchController::faultName(status.fault);
    json += "\",\"led_on\":";
    json += status.ledOn ? "true" : "false";
    json += ",\"armed\":";
    json += status.armed ? "true" : "false";
    json += ",\"phase_on\":";
    json += status.phaseOn ? "true" : "false";
    json += ",\"on_duration_ms\":";
    json += String(status.onDurationMs);
    json += ",\"off_duration_ms\":";
    json += String(status.offDurationMs);
    json += ",\"remaining_bursts\":";
    json += String(status.remainingBursts);
    json += ",\"runtime_ms\":";
    json += String(status.runtimeMs);
    json += ",\"active_time_ms\":";
    json += String(status.activeTimeMs);
    json += ",\"cooldown_remaining_ms\":";
    json += String(status.cooldownRemainingMs);
    json += ",\"current_preset_id\":\"";
    json += status.currentPresetId;
    json += "\"}";

    return json;
}

String WebShellServer::buildStrobePresetsJson() const {
    String json;
    json.reserve(1024);
    json += "[";

    for (size_t index = 0; index < modules::strobe::presetCount(); ++index) {
        const modules::strobe::PresetDefinition* preset = modules::strobe::presetAt(index);
        if (preset == nullptr) {
            continue;
        }

        if (index > 0) {
            json += ",";
        }

        json += "{";
        json += "\"id\":\"";
        json += preset->id;
        json += "\",\"title\":\"";
        json += preset->title;
        json += "\",\"purpose\":\"";
        json += preset->purpose;
        json += "\",\"pattern\":\"";
        json += modules::strobe::StrobeBenchController::patternName(preset->pattern);
        json += "\",\"risk\":\"";
        json += modules::strobe::StrobeBenchController::riskName(preset->risk);
        json += "\",\"count\":";
        json += String(preset->count);
        json += ",\"on_ms\":";
        json += String(preset->onMs);
        json += ",\"off_ms\":";
        json += String(preset->offMs);
        json += "}";
    }

    json += "]";
    return json;
}

String WebShellServer::buildCommandResponseJson(const char* command,
                                                modules::strobe::CommandResult result,
                                                const char* message) const {
    String json;
    json.reserve(384);

    json += "{";
    json += "\"command\":\"";
    json += command != nullptr ? command : "";
    json += "\",\"result\":\"";
    json += modules::strobe::StrobeBenchController::commandResultName(result);
    json += "\",\"accepted\":";
    json += result == modules::strobe::CommandResult::Accepted ? "true" : "false";
    json += ",\"message\":\"";
    json += message != nullptr ? message : "";
    json += "\"}";

    return json;
}

bool WebShellServer::serviceModeActive() const {
    return systemCore_.activeMode() == core::ActiveMode::ServiceTest;
}

}  // namespace smart_platform::web
