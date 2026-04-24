from __future__ import annotations

import io
import json
import os
import platform
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from bridge_config import BridgeConfig
from bridge_state import BridgeState
from settings_store import SettingsStore
from shell_snapshot_facade import ShellSnapshotFacade
from shell_viewer_presence import ShellViewerPresence
from sync_client import SyncClient

try:
    import segno
except ImportError:
    segno = None


def build_content_status(content_root: Path) -> dict[str, object]:
    return {
        "storage": "filesystem",
        "content_root": str(content_root),
        "content_root_exists": content_root.exists(),
        "assets_ready": (content_root / "assets").is_dir(),
        "audio_ready": (content_root / "audio").is_dir(),
        "animations_ready": (content_root / "animations").is_dir(),
        "libraries_ready": (content_root / "libraries").is_dir(),
    }


def build_entry_qr_svg(target_url: str) -> bytes:
    if segno is None:
        raise RuntimeError("qr_dependency_missing")

    parsed = urlparse(target_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("target must be an absolute http or https URL")

    qr = segno.make(target_url, error="m", micro=False)
    buffer = io.BytesIO()
    qr.save(
        buffer,
        kind="svg",
        scale=7,
        border=3,
        dark="#234230",
        light="#ffffff",
    )
    return buffer.getvalue()


def build_federated_handoff_html() -> bytes:
    html = """<!DOCTYPE html>
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
    <script src="/static/smart_bar.js"></script>
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
</html>"""
    return html.encode("utf-8")


def _detect_runtime_profile(config: BridgeConfig) -> str:
    explicit = os.getenv("SMART_PLATFORM_RUNTIME_PROFILE", "").strip().lower()
    if explicit:
        return explicit

    hostname = ""
    try:
        hostname = (urlparse(config.public_base_url).hostname or "").strip().lower()
    except ValueError:
        hostname = ""

    if hostname in {"127.0.0.1", "localhost"}:
        return "desktop_smoke"

    system_name = platform.system().strip().lower()
    if system_name in {"windows", "darwin"}:
        return "desktop_smoke"

    return "owner_device"


def build_server(config: BridgeConfig, state: BridgeState, sync_client: SyncClient) -> ThreadingHTTPServer:
    web_root = Path(__file__).resolve().parent / "web"
    content_root = Path(config.content_root)
    content_root_resolved = content_root.resolve()
    runtime_profile = _detect_runtime_profile(config)
    viewer_presence = ShellViewerPresence()
    settings_store = SettingsStore(content_root / ".system" / "settings_state.json")
    shell_snapshot_facade = ShellSnapshotFacade(
        state,
        content_root,
        runtime_profile=runtime_profile,
        viewer_provider=viewer_presence.active_viewers,
    )

    class RequestHandler(BaseHTTPRequestHandler):
        # Отключаем стандартный шум в stderr, чтобы логика платформы
        # не терялась в потоке служебных строк http.server.
        def log_message(self, format: str, *args: object) -> None:  # noqa: A003
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query, keep_blank_values=True)
            requested_path = Path(parsed.path.lstrip("/"))

            if requested_path.parts and requested_path.parts[0] in {"assets", "audio", "animations", "libraries"}:
                resolved_path = (content_root / requested_path).resolve()
                try:
                    resolved_path.relative_to(content_root_resolved)
                except ValueError:
                    self._json_response(
                        {"error": "invalid_path", "message": "Requested content path escapes content root"},
                        HTTPStatus.BAD_REQUEST,
                    )
                    return

                self._serve_file(resolved_path, self._content_type_for_path(requested_path))
                return

            if parsed.path == "/":
                self._serve_file(web_root / "index.html", "text/html; charset=utf-8")
                return
            if requested_path.parts and requested_path.parts[0] == "static":
                static_root = (web_root / "static").resolve()
                resolved_path = (web_root / requested_path).resolve()
                try:
                    resolved_path.relative_to(static_root)
                except ValueError:
                    self._json_response(
                        {"error": "invalid_path", "message": "Requested static path escapes web root"},
                        HTTPStatus.BAD_REQUEST,
                    )
                    return

                self._serve_file(resolved_path, self._content_type_for_path(requested_path))
                return
            if parsed.path == "/federated/handoff":
                self._raw_response(build_federated_handoff_html(), "text/html; charset=utf-8")
                return
            if parsed.path == "/irrigation":
                self._redirect("/federated/handoff?module_id=irrigation")
                return
            if parsed.path == "/service":
                self._serve_file(web_root / "service.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/service/irrigation":
                self._redirect("/federated/handoff?module_id=irrigation_service")
                return
            if parsed.path == "/service/strobe":
                self._redirect("/federated/handoff?module_id=strobe_bench")
                return
            if parsed.path == "/gallery":
                self._serve_file(web_root / "gallery.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/settings":
                self._serve_file(web_root / "settings.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/content":
                self._serve_file(web_root / "content.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/turret":
                self._serve_file(web_root / "turret.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/service/turret":
                self._serve_file(web_root / "service_turret.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/service/displays":
                self._serve_file(web_root / "service_displays.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/api/v1/system":
                self._json_response(state.build_system_snapshot())
                return
            if parsed.path == "/api/v1/shell/snapshot":
                self._json_response(shell_snapshot_facade.build_snapshot())
                return
            if parsed.path == "/api/v1/entry/qr.svg":
                target = self._param(params, "target").strip()
                if not target:
                    self._json_response(
                        {
                            "error": "target_required",
                            "message": "target query parameter is required",
                        },
                        HTTPStatus.BAD_REQUEST,
                    )
                    return
                try:
                    self._raw_response(build_entry_qr_svg(target), "image/svg+xml; charset=utf-8")
                except RuntimeError:
                    self._json_response(
                        {
                            "error": "qr_dependency_missing",
                            "message": "Install the segno package to enable QR entry generation.",
                        },
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                except ValueError as error:
                    self._json_response(
                        {
                            "error": "invalid_target",
                            "message": str(error),
                        },
                        HTTPStatus.BAD_REQUEST,
                    )
                return
            if parsed.path == "/api/v1/modules":
                self._json_response(state.build_system_snapshot()["modules"])
                return
            if parsed.path == "/api/v1/federation/route":
                self._json_response(state.build_module_route_info(self._param(params, "module_id")))
                return
            if parsed.path == "/api/v1/logs":
                limit = self._int_param(params, "limit", 60)
                self._json_response(state.build_platform_log(limit=limit))
                return
            if parsed.path == "/api/v1/reports":
                limit = self._int_param(params, "limit", 60)
                filters = {
                    "surface": self._param(params, "surface"),
                    "entry_type": self._param(params, "entry_type"),
                    "severity": self._param(params, "severity"),
                    "origin_node": self._param(params, "origin_node"),
                }
                self._json_response(state.build_reports(limit=limit, filters=filters))
                return
            if parsed.path == "/api/v1/laboratory/readiness":
                self._json_response(state.build_laboratory_readiness())
                return
            if parsed.path == "/api/v1/laboratory/session":
                self._json_response(state.build_laboratory_session())
                return
            if parsed.path == "/api/v1/content/status":
                self._json_response(build_content_status(content_root))
                return
            if parsed.path == "/api/v1/settings":
                self._json_response(settings_store.load())
                return
            if parsed.path == "/api/v1/turret/status":
                self._json_response(state.build_turret_status())
                return
            if parsed.path == "/api/v1/turret/runtime":
                self._json_response(state.build_turret_runtime())
                return
            if parsed.path == "/api/v1/turret/events":
                limit = self._int_param(params, "limit", 40)
                self._json_response(state.build_turret_events(limit=limit))
                return
            if parsed.path == "/api/v1/turret/drivers":
                self._json_response(state.build_turret_drivers())
                return
            if parsed.path == "/api/v1/turret/scenarios":
                self._json_response(state.build_turret_scenarios())
                return
            if parsed.path == "/api/v1/sync/status":
                self._json_response(state.build_sync_status())
                return

            self._json_response(
                {"error": "not_found", "message": "Route is not implemented in stage-rpi-platform-log-and-scenarios"},
                HTTPStatus.NOT_FOUND,
            )

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query, keep_blank_values=True)

            if parsed.path in {"/api/v1/turret/mode", "/api/v1/turret/runtime/mode"}:
                value = self._param(params, "value")
                accepted, message = state.update_turret_mode(value)
                self._json_response(
                    {
                        "command": "turret_mode",
                        "accepted": accepted,
                        "message": message,
                        "runtime": state.build_turret_runtime(),
                    }
                )
                return

            if parsed.path == "/api/v1/turret/runtime/subsystem":
                subsystem_id = self._param(params, "id")
                enabled = self._bool_param(params, "enabled", False)
                accepted, message = state.update_turret_subsystem(subsystem_id, enabled)
                self._json_response(
                    {
                        "command": "turret_subsystem",
                        "accepted": accepted,
                        "message": message,
                        "runtime": state.build_turret_runtime(),
                    }
                )
                return

            if parsed.path == "/api/v1/turret/runtime/flag":
                name = self._param(params, "name")
                value = self._bool_param(params, "value", False)
                accepted, message = state.update_turret_flag(name, value)
                self._json_response(
                    {
                        "command": "turret_flag",
                        "accepted": accepted,
                        "message": message,
                        "runtime": state.build_turret_runtime(),
                    }
                )
                return

            if parsed.path == "/api/v1/turret/runtime/interlock":
                value = self._param(params, "value")
                accepted, message = state.update_turret_interlock(value)
                self._json_response(
                    {
                        "command": "turret_interlock",
                        "accepted": accepted,
                        "message": message,
                        "runtime": state.build_turret_runtime(),
                    }
                )
                return

            if parsed.path == "/api/v1/turret/scenarios/run":
                scenario_id = self._param(params, "id")
                self._json_response(state.run_turret_scenario(scenario_id))
                return

            if parsed.path == "/api/v1/sync/refresh":
                sync_client.sync_once()
                self._json_response(
                    {
                        "command": "sync_refresh",
                        "accepted": True,
                        "sync_status": state.build_sync_status(),
                    }
                )
                return

            if parsed.path == "/api/v1/settings":
                try:
                    settings_payload = self._read_json_object()
                except ValueError as error:
                    self._json_response(
                        {
                            "command": "settings_update",
                            "accepted": False,
                            "message": str(error),
                            "settings": settings_store.load(),
                        },
                        HTTPStatus.BAD_REQUEST,
                    )
                    return

                self._json_response(
                    settings_store.update(settings_payload)
                )
                return

            if parsed.path == "/api/v1/laboratory/session/context":
                session = state.update_laboratory_context(
                    power_context=self._param(params, "power_context"),
                    view_mode=self._param(params, "view_mode"),
                    active_tool=self._param(params, "active_tool"),
                    module_id=self._param(params, "module_id"),
                )
                self._json_response(
                    {
                        "command": "laboratory_session_context",
                        "accepted": True,
                        "message": "laboratory context updated",
                        "session": session,
                    }
                )
                return

            if parsed.path == "/api/v1/laboratory/session/start":
                try:
                    result = state.start_laboratory_session(
                        operator=self._param(params, "operator"),
                        objective=self._param(params, "objective"),
                        hardware_profile=self._param(params, "hardware_profile"),
                        external_module=self._param(params, "external_module"),
                        power_context=self._param(params, "power_context"),
                        view_mode=self._param(params, "view_mode"),
                        active_tool=self._param(params, "active_tool"),
                        module_id=self._param(params, "module_id"),
                    )
                except ValueError as error:
                    self._json_response(
                        {
                            "command": "laboratory_session_start",
                            "accepted": False,
                            "message": str(error),
                            "session": state.build_laboratory_session(),
                        }
                    )
                    return

                self._json_response(
                    {
                        "command": "laboratory_session_start",
                        "accepted": True,
                        "message": "laboratory session started",
                        "session": result["session"],
                        "report_entry": result["report_entry"],
                    }
                )
                return

            if parsed.path == "/api/v1/laboratory/session/update":
                try:
                    session = state.update_laboratory_session(
                        operator=self._param(params, "operator"),
                        objective=self._param(params, "objective"),
                        hardware_profile=self._param(params, "hardware_profile"),
                        external_module=self._param(params, "external_module"),
                    )
                except ValueError as error:
                    self._json_response(
                        {
                            "command": "laboratory_session_update",
                            "accepted": False,
                            "message": str(error),
                            "session": state.build_laboratory_session(),
                        }
                    )
                    return

                self._json_response(
                    {
                        "command": "laboratory_session_update",
                        "accepted": True,
                        "message": "laboratory session updated",
                        "session": session,
                    }
                )
                return

            if parsed.path == "/api/v1/laboratory/session/finish":
                try:
                    result = state.finish_laboratory_session(
                        summary_note=self._param(params, "summary_note"),
                    )
                except ValueError as error:
                    self._json_response(
                        {
                            "command": "laboratory_session_finish",
                            "accepted": False,
                            "message": str(error),
                            "session": state.build_laboratory_session(),
                        }
                    )
                    return

                self._json_response(
                    {
                        "command": "laboratory_session_finish",
                        "accepted": True,
                        "message": "laboratory session finished",
                        "session": result["session"],
                        "finished_session": result["finished_session"],
                        "report_entry": result["report_entry"],
                    }
                )
                return

            if parsed.path == "/api/v1/laboratory/event":
                try:
                    report_entry = state.record_laboratory_event(
                        module_id=self._param(params, "module_id"),
                        event_type=self._slug_param(params, "event_type", "laboratory_event_recorded"),
                        message=self._param(params, "message"),
                        case_id=self._param(params, "case_id"),
                        note=self._param(params, "note"),
                        value=self._param(params, "value"),
                        severity=self._param(params, "severity", "info"),
                        laboratory_metadata=self._laboratory_metadata(params),
                    )
                except ValueError as error:
                    self._json_response(
                        {
                            "command": "laboratory_event",
                            "accepted": False,
                            "message": str(error),
                        }
                    )
                    return

                self._json_response(
                    {
                        "command": "laboratory_event",
                        "accepted": True,
                        "message": "laboratory event recorded",
                        "report_entry": report_entry,
                    }
                )
                return

            if parsed.path == "/api/v1/reports/testcase":
                case_id = self._param(params, "case_id").strip()
                module_id = self._param(params, "module_id").strip()
                result = self._param(params, "result").strip().lower()
                note = self._param(params, "note")
                board = self._param(params, "board")

                if not case_id or not module_id or result not in {"pass", "fail", "warn"}:
                    self._json_response(
                        {
                            "command": "reports_testcase",
                            "accepted": False,
                            "message": "case_id, module_id, and result=pass|fail|warn are required",
                        }
                    )
                    return

                report_entry = state.record_testcase_result(
                    case_id=case_id,
                    module_id=module_id,
                    result=result,
                    note=note,
                    board=board,
                    laboratory_metadata=self._laboratory_metadata(params),
                )
                self._json_response(
                    {
                        "command": "reports_testcase",
                        "accepted": True,
                        "message": "testcase result recorded",
                        "report_entry": report_entry,
                        "reports_source_kind": state.build_reports(limit=1).get("source_kind", "unknown"),
                    }
                )
                return

            if parsed.path == "/api/v1/reports/note":
                note = self._param(params, "note")
                module_id = self._param(params, "module_id").strip()
                board = self._param(params, "board")
                case_id = self._param(params, "case_id")

                if not note.strip() or not module_id:
                    self._json_response(
                        {
                            "command": "reports_note",
                            "accepted": False,
                            "message": "note and module_id are required",
                        }
                    )
                    return

                report_entry = state.record_operator_note(
                    note=note,
                    module_id=module_id,
                    board=board,
                    case_id=case_id,
                    laboratory_metadata=self._laboratory_metadata(params),
                )
                self._json_response(
                    {
                        "command": "reports_note",
                        "accepted": True,
                        "message": "operator note recorded",
                        "report_entry": report_entry,
                        "reports_source_kind": state.build_reports(limit=1).get("source_kind", "unknown"),
                    }
                )
                return

            if parsed.path == "/api/v1/shell/viewer-heartbeat":
                viewer_id = self._param(params, "viewer_id").strip()
                viewer_kind = self._param(params, "viewer_kind", "desktop")
                title = self._param(params, "title")
                value = self._param(params, "value")
                page = self._param(params, "page", "/")

                if not viewer_id:
                    self._json_response(
                        {
                            "command": "viewer_heartbeat",
                            "accepted": False,
                            "message": "viewer_id is required",
                        },
                        HTTPStatus.BAD_REQUEST,
                    )
                    return

                viewers = viewer_presence.heartbeat(
                    viewer_id,
                    viewer_kind=viewer_kind,
                    title=title,
                    value=value,
                    page=page,
                    address=self.client_address[0],
                    user_agent=self.headers.get("User-Agent", ""),
                )
                self._json_response(
                    {
                        "command": "viewer_heartbeat",
                        "accepted": True,
                        "message": "viewer heartbeat recorded",
                        "viewers": viewers,
                        "runtime_profile": runtime_profile,
                    }
                )
                return

            self._json_response(
                {"error": "not_found", "message": "Route is not implemented in stage-rpi-platform-log-and-scenarios"},
                HTTPStatus.NOT_FOUND,
            )

        def _serve_file(self, path: Path, content_type: str) -> None:
            if not path.exists():
                self._json_response({"error": "file_not_found", "path": str(path)}, HTTPStatus.NOT_FOUND)
                return

            raw = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self._send_no_cache_headers()
            self.end_headers()
            self.wfile.write(raw)

        def _redirect(self, location: str, status: HTTPStatus = HTTPStatus.TEMPORARY_REDIRECT) -> None:
            self.send_response(status)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _json_response(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._raw_response(raw, "application/json; charset=utf-8", status)

        def _raw_response(
            self,
            raw: bytes,
            content_type: str,
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self._send_no_cache_headers()
            self.end_headers()
            self.wfile.write(raw)

        def _send_no_cache_headers(self) -> None:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")

        def _param(self, params: dict[str, list[str]], name: str, default: str = "") -> str:
            values = params.get(name)
            if not values:
                return default
            return values[0]

        def _read_json_object(self) -> dict[str, object]:
            raw_length = self.headers.get("Content-Length", "0").strip()
            try:
                content_length = max(0, int(raw_length))
            except ValueError as error:
                raise ValueError("invalid content length") from error

            raw = self.rfile.read(content_length) if content_length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ValueError("request body must be valid JSON") from error

            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")

            return payload

        def _slug_param(self, params: dict[str, list[str]], name: str, default: str = "") -> str:
            raw = self._param(params, name, default).strip().lower().replace("-", "_")
            normalized = "".join(ch for ch in raw if ch.isalnum() or ch == "_")
            return normalized or default

        def _laboratory_metadata(self, params: dict[str, list[str]]) -> dict[str, str]:
            keys = (
                "lab_session_id",
                "lab_session_status",
                "lab_operator",
                "lab_objective",
                "lab_hardware_profile",
                "lab_external_module",
                "lab_power_context",
                "lab_view_mode",
                "lab_active_tool",
                "lab_context_module",
                "lab_owner_node_id",
                "lab_owner_node_type",
            )
            metadata: dict[str, str] = {}
            for key in keys:
                value = self._param(params, key).strip()
                if value:
                    metadata[key] = value
            return metadata

        def _bool_param(self, params: dict[str, list[str]], name: str, default: bool) -> bool:
            raw = self._param(params, name, "1" if default else "0").strip().lower()
            return raw in {"1", "true", "yes", "on"}

        def _int_param(self, params: dict[str, list[str]], name: str, default: int) -> int:
            raw = self._param(params, name, str(default)).strip()
            try:
                return max(1, int(raw))
            except ValueError:
                return default

        def _content_type_for_path(self, path: Path) -> str:
            suffix = path.suffix.lower()
            if suffix == ".html":
                return "text/html; charset=utf-8"
            if suffix == ".css":
                return "text/css; charset=utf-8"
            if suffix == ".js":
                return "application/javascript; charset=utf-8"
            if suffix == ".json":
                return "application/json; charset=utf-8"
            if suffix == ".svg":
                return "image/svg+xml"
            if suffix == ".png":
                return "image/png"
            if suffix in {".jpg", ".jpeg"}:
                return "image/jpeg"
            if suffix == ".gif":
                return "image/gif"
            if suffix == ".webp":
                return "image/webp"
            if suffix == ".mp3":
                return "audio/mpeg"
            if suffix == ".wav":
                return "audio/wav"
            if suffix == ".ogg":
                return "audio/ogg"
            if suffix == ".webm":
                return "video/webm"
            return "application/octet-stream"

    return ThreadingHTTPServer((config.bind_host, config.bind_port), RequestHandler)
