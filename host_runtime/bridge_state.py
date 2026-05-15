from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from threading import RLock
from time import monotonic, time
from typing import Any

from laboratory_session import LaboratorySessionState
from laboratory_readiness import build_laboratory_readiness
from platform_event_log import PlatformEventLog
from report_archive import ReportArchive
from report_feed import build_reports_snapshot, normalize_report_entry
from turret_driver_layer import TurretDriverLayer
from turret_event_log import TurretEventLog
from turret_runtime import TurretRuntime
from turret_service_scenarios import TurretServiceScenarioRunner


class BridgeState:
    def __init__(
        self,
        node_id: str,
        shell_version: str,
        local_shell_base_url: str,
        peer_shell_base_url: str,
        content_root: str | None = None,
    ) -> None:
        self._lock = RLock()
        self._boot_time = monotonic()
        self._shell_version = shell_version
        self._active_mode = "manual"
        self._global_block_reason = "none"
        self._report_archive = (
            ReportArchive(Path(content_root) / "gallery" / "reports") if content_root else None
        )
        self._platform_log = PlatformEventLog(
            node_id,
            forward_sink=self._archive_platform_entry if self._report_archive is not None else None,
        )
        self._turret_event_log = TurretEventLog(forward_sink=self._forward_turret_event)
        self._turret_driver_layer = TurretDriverLayer(self._turret_event_log)
        self._turret_runtime = TurretRuntime(self._turret_event_log, self._turret_driver_layer)
        self._turret_scenarios = TurretServiceScenarioRunner(self._turret_runtime, self._platform_log)

        self._local_node: dict[str, Any] = {
            "node_id": node_id,
            "shell_base_url": local_shell_base_url,
            "node_type": "raspberry_pi",
            "is_local": True,
            "reachable": True,
            "shell_ready": True,
            "wifi_ready": True,
            "sync_ready": True,
            "reported_mode": self._active_mode,
            "last_seen_ms": 0,
            "uptime_ms": 0,
        }

        self._peer_node: dict[str, Any] = {
            "node_id": "esp32-main",
            "shell_base_url": peer_shell_base_url,
            "node_type": "esp32",
            "is_local": False,
            "reachable": False,
            "shell_ready": False,
            "wifi_ready": False,
            "sync_ready": False,
            "reported_mode": "manual",
            "last_seen_ms": 0,
            "uptime_ms": 0,
        }

        self._sync_status: dict[str, Any] = {
            "enabled": True,
            "last_push_ok": False,
            "last_sync_ms": 0,
            "last_error": "",
        }
        self._laboratory_session = LaboratorySessionState(
            node_id=self._local_node["node_id"],
            node_type=self._local_node["node_type"],
        )

        self._modules: dict[str, dict[str, Any]] = {}
        self._seed_default_modules()
        self._refresh_runtime_state()
        self._platform_log.add(
            "system_shell",
            "info",
            "bridge_state_ready",
            "raspberry pi bridge state initialized",
            node_id=node_id,
            shell_version=shell_version,
        )

    def _forward_turret_event(self, entry: dict[str, Any]) -> None:
        self._platform_log.add(
            "turret_runtime",
            entry.get("level", "info"),
            entry.get("type", "turret_event"),
            entry.get("message", "turret event mirrored to platform log"),
            turret_event_id=entry.get("event_id"),
            **entry.get("details", {}),
        )

    def _archive_platform_entry(self, entry: dict[str, Any]) -> None:
        if self._report_archive is not None:
            self._report_archive.append_platform_entry(entry)

    def _merged_laboratory_metadata(self, laboratory_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        merged = self._laboratory_session.report_metadata()
        if not laboratory_metadata:
            return merged

        for key, value in laboratory_metadata.items():
            text = str(value).strip()
            if text:
                merged[str(key)] = text
        return merged

    def _uptime_ms(self) -> int:
        return int((monotonic() - self._boot_time) * 1000)

    def _now_ms(self) -> int:
        return int(time() * 1000)

    def _seed_default_modules(self) -> None:
        # Каркас модулей должен повторять общую карту платформы.
        # Даже если часть логики здесь пока остается заглушкой, shell обязан видеть
        # те же сущности, что и на ESP32.
        # Product modules остаются top-level shell cards,
        # а laboratory/action slices остаются маршрутизируемыми внутренними контурами.
        self._modules = {
            "system_shell": self._module(
                "system_shell",
                "System Shell",
                "shared",
                "core",
                "system",
                "online",
                "none",
                ["status_page", "diagnostics", "logs"],
                True,
                True,
                True,
            ),
            "sync_core": self._module(
                "sync_core",
                "Sync Core",
                "shared",
                "core",
                "system",
                "degraded",
                "owner_unavailable",
                ["status_page", "diagnostics", "logs"],
                True,
                False,
                True,
            ),
            "irrigation": self._module(
                "irrigation",
                "Irrigation",
                "esp32",
                "plant_care",
                "irrigation",
                "locked",
                "owner_unavailable",
                ["status_page", "manual_page", "service_page", "logs", "commandable", "diagnostics"],
                True,
                True,
                True,
            ),
            "turret_bridge": self._module(
                "turret_bridge",
                "Turret",
                "rpi",
                "turret",
                "turret",
                "online",
                "none",
                ["status_page", "manual_page", "service_page", "diagnostics", "commandable", "logs"],
                True,
                True,
                True,
            ),
            "strobe": self._module(
                "strobe",
                "Turret / Strobe",
                "rpi",
                "turret",
                "turret",
                "online",
                "none",
                ["status_page", "manual_page", "service_page", "commandable", "diagnostics", "logs"],
                False,
                True,
                True,
            ),
            "strobe_bench": self._module(
                "strobe_bench",
                "Laboratory / Strobe",
                "esp32",
                "bench_service",
                "service",
                "locked",
                "owner_unavailable",
                ["status_page", "manual_page", "service_page", "commandable", "diagnostics", "logs"],
                False,
                True,
                True,
            ),
            "irrigation_service": self._module(
                "irrigation_service",
                "Laboratory / Irrigation",
                "esp32",
                "plant_care",
                "service",
                "locked",
                "owner_unavailable",
                ["status_page", "manual_page", "service_page", "commandable", "diagnostics", "logs"],
                False,
                True,
                True,
            ),
            "logs": self._module(
                "logs",
                "Logs",
                "shared",
                "core",
                "logs",
                "online",
                "none",
                ["status_page", "logs", "diagnostics"],
                True,
                False,
                True,
            ),
            "settings": self._module(
                "settings",
                "Settings",
                "shared",
                "core",
                "settings",
                "online",
                "none",
                ["status_page", "manual_page", "diagnostics"],
                True,
                True,
                False,
            ),
            "diagnostics": self._module(
                "diagnostics",
                "Diagnostics",
                "shared",
                "core",
                "system",
                "online",
                "none",
                ["status_page", "diagnostics", "logs"],
                True,
                False,
                True,
            ),
            "service_mode": self._module(
                "service_mode",
                "Laboratory",
                "shared",
                "core",
                "service",
                "online",
                "none",
                ["status_page", "service_page", "diagnostics", "logs"],
                False,
                False,
                True,
            ),
        }

    def _module(
        self,
        module_id: str,
        title: str,
        owner: str,
        profile: str,
        ui_group: str,
        state: str,
        block_reason: str,
        capabilities: list[str],
        visible: bool,
        manual_page: bool,
        service_page: bool,
    ) -> dict[str, Any]:
        return {
            "id": module_id,
            "title": title,
            "owner": owner,
            "profile": profile,
            "ui_group": ui_group,
            "state": state,
            "block_reason": block_reason,
            "visible": visible,
            "manual_page": manual_page,
            "service_page": service_page,
            "capabilities": capabilities,
        }

    def _canonical_path(self, module_id: str) -> str:
        routes = {
            "irrigation": "/irrigation",
            "turret_bridge": "/turret",
            "strobe": "/turret#strobe",
            "strobe_bench": "/service/strobe",
            "irrigation_service": "/service/irrigation",
            "logs": "/gallery?tab=reports",
            "settings": "/settings",
            "diagnostics": "/settings#diagnostics",
            "service_mode": "/service",
        }
        return routes.get(module_id, "/")

    def _owner_available(self, module: dict[str, Any]) -> bool:
        if module["owner"] == "shared":
            return True
        if module["owner"] == "esp32":
            return bool(
                self._peer_node["reachable"]
                and self._peer_node["shell_ready"]
                and self._peer_node["sync_ready"]
                and self._peer_node.get("shell_base_url")
            )
        return True

    def _owner_node_id(self, module: dict[str, Any]) -> str:
        if module["owner"] == "shared":
            return ""
        if module["owner"] == "esp32":
            return str(self._peer_node["node_id"])
        return str(self._local_node["node_id"])

    def _canonical_url(self, module: dict[str, Any]) -> str:
        path = self._canonical_path(module["id"])
        if module["owner"] == "esp32":
            if not self._owner_available(module):
                return ""
            return f"{self._peer_node['shell_base_url']}{path}"
        base_url = str(self._local_node.get("shell_base_url", "")).rstrip("/")
        return f"{base_url}{path}" if base_url else path

    def _federated_access(self, module: dict[str, Any]) -> str:
        if module["owner"] == "esp32":
            return "peer_owner_available" if self._owner_available(module) else "peer_owner_missing"
        if module["owner"] == "shared":
            return "shared_local"
        return "local_owner"

    def _enriched_module(self, module: dict[str, Any]) -> dict[str, Any]:
        snapshot = deepcopy(module)
        snapshot["owner_node_id"] = self._owner_node_id(module)
        snapshot["owner_available"] = self._owner_available(module)
        snapshot["canonical_path"] = self._canonical_path(module["id"])
        snapshot["canonical_url"] = self._canonical_url(module)
        snapshot["federated_access"] = self._federated_access(module)
        return snapshot

    def _refresh_runtime_state(self) -> None:
        self._active_mode = self._turret_runtime.active_mode
        self._local_node["reported_mode"] = self._active_mode

        if self._active_mode == "emergency":
            self._global_block_reason = "emergency_state"
        elif self._active_mode == "fault":
            self._global_block_reason = "module_fault"
        elif self._active_mode == "service_test":
            self._global_block_reason = "service_session_active"
        else:
            self._global_block_reason = "none"

        exported = self._turret_runtime.export_module_states()
        for module_id, module_state in exported.items():
            self._modules[module_id]["state"] = module_state["state"]
            self._modules[module_id]["block_reason"] = module_state["block_reason"]

        if self._active_mode == "service_test":
            self._modules["service_mode"]["state"] = "service"
            self._modules["service_mode"]["block_reason"] = "none"
        elif self._active_mode == "emergency":
            self._modules["service_mode"]["state"] = "locked"
            self._modules["service_mode"]["block_reason"] = "emergency_state"
        elif self._active_mode == "fault":
            self._modules["service_mode"]["state"] = "locked"
            self._modules["service_mode"]["block_reason"] = "module_fault"
        else:
            self._modules["service_mode"]["state"] = "online"
            self._modules["service_mode"]["block_reason"] = "none"

    def build_system_snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._local_node["uptime_ms"] = self._uptime_ms()
            self._local_node["reported_mode"] = self._active_mode
            self._local_node["last_seen_ms"] = self._now_ms()
            return {
                "ui_shell_version": self._shell_version,
                "active_mode": self._active_mode,
                "global_block_reason": self._global_block_reason,
                "local_node": deepcopy(self._local_node),
                "peer_node": deepcopy(self._peer_node),
                "modules": [self._enriched_module(module) for module in self._modules.values()],
            }

    def build_platform_log(self, limit: int = 60) -> dict[str, Any]:
        with self._lock:
            return self._platform_log.snapshot(limit=limit)

    def build_reports(self, limit: int = 60, *, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        with self._lock:
            if self._report_archive is not None:
                return self._report_archive.snapshot(limit=limit, filters=filters)
            return build_reports_snapshot(self._platform_log.snapshot(limit=limit), limit=limit, filters=filters)

    def build_laboratory_readiness(self) -> dict[str, Any]:
        with self._lock:
            reports_source_kind = "report_archive_v1" if self._report_archive is not None else "platform_log_baseline"
            return build_laboratory_readiness(
                current_node=deepcopy(self._local_node),
                peer_node=deepcopy(self._peer_node),
                active_mode=self._active_mode,
                runtime=self._turret_runtime.snapshot(),
                reports_source_kind=reports_source_kind,
            )

    def build_laboratory_session(self) -> dict[str, Any]:
        with self._lock:
            return self._laboratory_session.snapshot(self._uptime_ms())

    def update_laboratory_context(
        self,
        *,
        power_context: str = "",
        view_mode: str = "",
        active_tool: str = "",
        module_id: str = "",
    ) -> dict[str, Any]:
        with self._lock:
            return self._laboratory_session.update_context(
                now_ms=self._uptime_ms(),
                power_context=power_context,
                view_mode=view_mode,
                active_tool=active_tool,
                module_id=module_id,
            )

    def start_laboratory_session(
        self,
        *,
        operator: str = "",
        objective: str = "",
        hardware_profile: str = "",
        external_module: str = "",
        power_context: str = "",
        view_mode: str = "",
        active_tool: str = "",
        module_id: str = "",
    ) -> dict[str, Any]:
        with self._lock:
            active_session = self._laboratory_session.start_session(
                now_ms=self._uptime_ms(),
                operator=operator,
                objective=objective,
                hardware_profile=hardware_profile,
                external_module=external_module,
                power_context=power_context,
                view_mode=view_mode,
                active_tool=active_tool,
                module_id=module_id,
            )
            report_entry = self._platform_log.add(
                "laboratory_session",
                "info",
                "laboratory_session_started",
                f"laboratory session {active_session['session_id']} started",
                active_mode=self._active_mode,
                **self._merged_laboratory_metadata(),
            )
            return {
                "session": self._laboratory_session.snapshot(self._uptime_ms()),
                "report_entry": normalize_report_entry(report_entry),
            }

    def update_laboratory_session(
        self,
        *,
        operator: str = "",
        objective: str = "",
        hardware_profile: str = "",
        external_module: str = "",
    ) -> dict[str, Any]:
        with self._lock:
            self._laboratory_session.update_session(
                now_ms=self._uptime_ms(),
                operator=operator,
                objective=objective,
                hardware_profile=hardware_profile,
                external_module=external_module,
            )
            return self._laboratory_session.snapshot(self._uptime_ms())

    def finish_laboratory_session(self, *, summary_note: str = "") -> dict[str, Any]:
        with self._lock:
            finished = self._laboratory_session.finish_session(
                now_ms=self._uptime_ms(),
                summary_note=summary_note,
            )
            report_entry = self._platform_log.add(
                "laboratory_session",
                "info",
                "laboratory_session_finished",
                f"laboratory session {finished['session_id']} finished",
                duration_ms=finished.get("duration_ms", 0),
                summary_note=finished.get("summary_note", ""),
                active_mode=self._active_mode,
                **self._merged_laboratory_metadata(
                    {
                        "lab_session_id": finished.get("session_id", ""),
                        "lab_operator": finished.get("operator", ""),
                        "lab_objective": finished.get("objective", ""),
                        "lab_hardware_profile": finished.get("hardware_profile", ""),
                        "lab_external_module": finished.get("external_module", ""),
                        "lab_session_status": finished.get("status", "completed"),
                    }
                ),
            )
            return {
                "session": self._laboratory_session.snapshot(self._uptime_ms()),
                "finished_session": deepcopy(finished),
                "report_entry": normalize_report_entry(report_entry),
            }

    def record_testcase_result(
        self,
        *,
        case_id: str,
        module_id: str,
        result: str,
        note: str = "",
        board: str = "",
        laboratory_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_result = result.strip().lower()
        if normalized_result not in {"pass", "fail", "warn"}:
            raise ValueError("result must be pass, fail, or warn")

        case_id = case_id.strip()
        module_id = module_id.strip()
        if not case_id:
            raise ValueError("case_id is required")
        if not module_id:
            raise ValueError("module_id is required")

        normalized_board = board.strip() or str(self._local_node.get("node_type", "unknown"))
        severity = "info"
        if normalized_result == "warn":
            severity = "warning"
        elif normalized_result == "fail":
            severity = "error"

        entry = self._platform_log.add(
            "testcase_capture",
            severity,
            "testcase_result_recorded",
            f"testcase {case_id} recorded for {module_id} as {normalized_result}",
            case_id=case_id,
            module_id=module_id,
            board=normalized_board,
            test_result=normalized_result,
            note=note.strip(),
            active_mode=self._active_mode,
            **self._merged_laboratory_metadata(laboratory_metadata),
        )
        return normalize_report_entry(entry)

    def record_operator_note(
        self,
        *,
        note: str,
        module_id: str,
        board: str = "",
        case_id: str = "",
        laboratory_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        note = note.strip()
        module_id = module_id.strip()
        case_id = case_id.strip()
        if not note:
            raise ValueError("note is required")
        if not module_id:
            raise ValueError("module_id is required")

        normalized_board = board.strip() or str(self._local_node.get("node_type", "unknown"))
        entry = self._platform_log.add(
            "testcase_capture",
            "info",
            "operator_note",
            note,
            case_id=case_id,
            module_id=module_id,
            board=normalized_board,
            note=note,
            active_mode=self._active_mode,
            **self._merged_laboratory_metadata(laboratory_metadata),
        )
        return normalize_report_entry(entry)

    def record_laboratory_event(
        self,
        *,
        module_id: str,
        event_type: str,
        message: str,
        case_id: str = "",
        note: str = "",
        value: str = "",
        severity: str = "info",
        laboratory_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        module_id = module_id.strip()
        event_type = event_type.strip().lower() or "laboratory_event_recorded"
        message = message.strip()
        if not module_id:
            raise ValueError("module_id is required")
        if not message:
            raise ValueError("message is required")

        normalized_severity = severity.strip().lower()
        if normalized_severity not in {"info", "warning", "error"}:
            normalized_severity = "info"

        entry = self._platform_log.add(
            "laboratory_session",
            normalized_severity,
            event_type,
            message,
            case_id=case_id.strip(),
            module_id=module_id,
            note=note.strip(),
            value=value.strip(),
            active_mode=self._active_mode,
            **self._merged_laboratory_metadata(laboratory_metadata),
        )
        return normalize_report_entry(entry)

    def record_turret_capture(
        self,
        *,
        kind: str,
        phase: str,
        capture_id: str,
        artifact_path: str,
        artifact_url: str,
        gallery_url: str,
        duration_ms: int = 0,
        power_percent: int = 0,
        status: str = "",
    ) -> dict[str, Any]:
        normalized_kind = kind.strip().lower()
        normalized_phase = phase.strip().lower()
        if normalized_kind not in {"photo", "video"}:
            raise ValueError("kind must be photo or video")
        if normalized_phase not in {"photo", "video_start", "video_stop"}:
            raise ValueError("phase must be photo, video_start, or video_stop")
        if not capture_id.strip():
            raise ValueError("capture_id is required")

        message_kind = "photo" if normalized_kind == "photo" else "video"
        message_action = {
            "photo": "captured",
            "video_start": "recording started",
            "video_stop": "recording stopped",
        }[normalized_phase]
        entry = self._platform_log.add(
            "turret_runtime",
            "info",
            f"turret_{normalized_kind}_capture_{normalized_phase}",
            f"turret {message_kind} {message_action}",
            module_id="turret_bridge",
            capture_id=capture_id.strip(),
            capture_kind=normalized_kind,
            capture_phase=normalized_phase,
            capture_status=status.strip(),
            artifact_path=artifact_path.strip(),
            artifact_url=artifact_url.strip(),
            gallery_url=gallery_url.strip(),
            duration_ms=max(0, int(duration_ms or 0)),
            power_percent=max(0, int(power_percent or 0)),
            active_mode=self._active_mode,
        )
        return normalize_report_entry(entry)

    def build_module_route_info(self, module_id: str) -> dict[str, Any]:
        with self._lock:
            module = self._modules.get(module_id)
            if module is None:
                return {
                    "module_id": module_id,
                    "module_found": False,
                }

            enriched = self._enriched_module(module)
            return {
                "module_id": module_id,
                "module_found": True,
                "title": enriched["title"],
                "owner": enriched["owner"],
                "owner_node_id": enriched["owner_node_id"],
                "owner_available": enriched["owner_available"],
                "state": enriched["state"],
                "block_reason": enriched["block_reason"],
                "canonical_path": enriched["canonical_path"],
                "canonical_url": enriched["canonical_url"],
                "federated_access": enriched["federated_access"],
                "viewer_canonical_url_reachability": "not_verified",
                "viewer_reachability_summary": "Current shell can prove owner availability, but not whether this viewer can reach the canonical URL from its network.",
                "current_shell_node_id": self._local_node["node_id"],
                "current_shell_base_url": self._local_node["shell_base_url"],
            }

    def build_log_sync_payload(self, limit: int = 12) -> dict[str, Any]:
        with self._lock:
            return self._platform_log.export_local_entries(limit=limit)

    def build_turret_status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "active_mode": self._active_mode,
                "bridge": deepcopy(self._modules["turret_bridge"]),
                "strobe": deepcopy(self._modules["strobe"]),
                "runtime": self._turret_runtime.snapshot(),
                "drivers": self._turret_driver_layer.describe_bindings(),
                "event_log": self._turret_event_log.snapshot(),
                "platform_log": self._platform_log.snapshot(limit=20),
                "peer_node": deepcopy(self._peer_node),
                "sync_status": deepcopy(self._sync_status),
            }

    def build_turret_runtime(self) -> dict[str, Any]:
        with self._lock:
            return self._turret_runtime.snapshot()

    def apply_settings(self, settings: dict[str, Any] | None) -> None:
        with self._lock:
            self._turret_runtime.apply_settings_profile(settings)
            self._refresh_runtime_state()

    def build_turret_events(self, limit: int = 40) -> dict[str, Any]:
        with self._lock:
            return self._turret_event_log.snapshot(limit=limit)

    def build_turret_drivers(self) -> dict[str, Any]:
        with self._lock:
            return self._turret_driver_layer.describe_bindings()

    def build_turret_scenarios(self) -> dict[str, Any]:
        with self._lock:
            return self._turret_scenarios.list_scenarios()

    def run_turret_scenario(self, scenario_id: str) -> dict[str, Any]:
        with self._lock:
            result = self._turret_scenarios.run(scenario_id)
            self._refresh_runtime_state()
            return result

    def _sync_state_value(self) -> str:
        enabled = bool(self._sync_status.get("enabled"))
        peer_reachable = bool(self._peer_node.get("reachable"))
        peer_sync_ready = bool(self._peer_node.get("sync_ready"))
        last_sync_ms = int(self._sync_status.get("last_sync_ms", 0) or 0)
        last_error = str(self._sync_status.get("last_error", "") or "").strip()
        last_push_ok = bool(self._sync_status.get("last_push_ok"))

        if not enabled:
            return "local_only"
        if not peer_reachable:
            return "remote_unavailable"
        if peer_reachable and not last_sync_ms:
            return "never_synced"
        if peer_sync_ready and last_push_ok:
            return "ready"
        if last_error:
            return "error"
        return "pending"

    def _sync_summary(self, state_value: str) -> str:
        if state_value == "local_only":
            return "Background sync is disabled. This host is currently operating in local-only mode."
        if state_value == "remote_unavailable":
            return "Base node connectivity is unavailable because the remote node is offline."
        if state_value == "never_synced":
            return "Sync is enabled, but the first successful exchange has not completed yet."
        if state_value == "ready":
            return "Background sync is ready and the remote node is reachable."
        if state_value == "error":
            return "Background sync reported an error during the last exchange."
        return "Background sync is enabled, but the remote node is still pending."

    def _sync_domains(self, state_value: str) -> list[dict[str, Any]]:
        def domain_state(enabled: bool) -> str:
            if not enabled:
                return "local_only"
            if state_value in {"remote_unavailable", "never_synced", "pending", "ready", "error"}:
                return state_value
            return "local_only"

        transport_enabled = bool(self._sync_status.get("enabled"))
        transport_state = domain_state(transport_enabled)
        return [
            {
                "id": "service_link",
                "title": "Service Link",
                "enabled": transport_enabled,
                "state": transport_state,
                "summary": "Heartbeat and base node connectivity between platform owners.",
            },
            {
                "id": "module_state",
                "title": "Module State",
                "enabled": transport_enabled,
                "state": transport_state,
                "summary": "Owner-side module availability and route summaries.",
            },
            {
                "id": "reports_history",
                "title": "Reports And Logs",
                "enabled": transport_enabled,
                "state": transport_state,
                "summary": "Platform log mirroring and Gallery > Reports continuity.",
            },
            {
                "id": "shared_preferences",
                "title": "Shared Preferences",
                "enabled": False,
                "state": "local_only",
                "summary": "Preferences are currently stored per host. Cross-node preference sync is not enabled.",
            },
            {
                "id": "media_content",
                "title": "Media And Content",
                "enabled": False,
                "state": "local_only",
                "summary": "Heavy media/content mirroring is not enabled in this runtime yet.",
            },
        ]

    def build_sync_status(self) -> dict[str, Any]:
        with self._lock:
            payload = deepcopy(self._sync_status)
            state_value = self._sync_state_value()
            payload["peer_reachable"] = bool(self._peer_node.get("reachable"))
            payload["peer_sync_ready"] = bool(self._peer_node.get("sync_ready"))
            payload["state"] = state_value
            payload["summary"] = self._sync_summary(state_value)
            payload["domains"] = self._sync_domains(state_value)
            return payload

    def set_sync_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._sync_status["enabled"] = enabled
            self._platform_log.add(
                "sync_core",
                "info",
                "sync_enabled_changed",
                "background sync flag updated",
                enabled=enabled,
            )

    def set_active_mode(self, mode: str) -> bool:
        accepted, _ = self.update_turret_mode(mode)
        return accepted

    def update_turret_mode(self, mode: str) -> tuple[bool, str]:
        with self._lock:
            accepted, message = self._turret_runtime.set_mode(mode)
            if accepted:
                self._refresh_runtime_state()
            return accepted, message

    def update_turret_interlock(self, value: str) -> tuple[bool, str]:
        with self._lock:
            accepted, message = self._turret_runtime.set_interlock(value)
            if accepted:
                self._refresh_runtime_state()
            return accepted, message

    def update_turret_flag(self, name: str, value: bool) -> tuple[bool, str]:
        with self._lock:
            accepted, message = self._turret_runtime.set_flag(name, value)
            if accepted:
                self._refresh_runtime_state()
            return accepted, message

    def update_turret_subsystem(self, subsystem_id: str, enabled: bool) -> tuple[bool, str]:
        with self._lock:
            accepted, message = self._turret_runtime.set_subsystem_enabled(subsystem_id, enabled)
            if accepted:
                self._refresh_runtime_state()
            return accepted, message

    def build_sync_payload(self) -> dict[str, Any]:
        with self._lock:
            return {
                "heartbeat": {
                    "node_id": self._local_node["node_id"],
                    "shell_base_url": self._local_node["shell_base_url"],
                    "wifi_ready": "1" if self._local_node["wifi_ready"] else "0",
                    "shell_ready": "1" if self._local_node["shell_ready"] else "0",
                    "sync_ready": "1",
                    "reported_mode": self._active_mode,
                },
                "modules": [
                    {
                        "id": "turret_bridge",
                        "state": self._modules["turret_bridge"]["state"],
                        "block_reason": self._modules["turret_bridge"]["block_reason"],
                    },
                    {
                        "id": "strobe",
                        "state": self._modules["strobe"]["state"],
                        "block_reason": self._modules["strobe"]["block_reason"],
                    },
                ],
            }

    def apply_esp32_logs(self, snapshot: dict[str, Any]) -> None:
        with self._lock:
            for entry in snapshot.get("entries", []):
                self._platform_log.add_remote(
                    entry.get("origin_node", "esp32-main"),
                    entry.get("origin_event_id", entry.get("event_id", "")),
                    entry.get("source", "esp32"),
                    entry.get("level", "info"),
                    entry.get("type", "remote_log"),
                    entry.get("message", ""),
                    entry.get("details", ""),
                )

    def apply_esp32_snapshot(self, snapshot: dict[str, Any]) -> None:
        with self._lock:
            now_ms = self._now_ms()
            local = snapshot.get("local_node", {})
            if local:
                self._peer_node["node_id"] = local.get("node_id", self._peer_node["node_id"])
                self._peer_node["shell_base_url"] = local.get("shell_base_url", self._peer_node["shell_base_url"])
                self._peer_node["node_type"] = local.get("node_type", self._peer_node["node_type"])
                self._peer_node["reachable"] = bool(local.get("reachable", True))
                self._peer_node["shell_ready"] = bool(local.get("shell_ready", False))
                self._peer_node["wifi_ready"] = bool(local.get("wifi_ready", False))
                self._peer_node["sync_ready"] = bool(local.get("sync_ready", True))
                self._peer_node["reported_mode"] = local.get("reported_mode", "manual")
                self._peer_node["last_seen_ms"] = now_ms
                self._peer_node["uptime_ms"] = int(local.get("uptime_ms", 0))

            modules = snapshot.get("modules", [])
            for remote_module in modules:
                module_id = remote_module.get("id")
                if not module_id or module_id not in self._modules:
                    continue

                # Принимаем только peer-owned модули. Локальный runtime турели нельзя
                # перетирать внешним snapshot, иначе мы потеряем owner-модель.
                if self._modules[module_id]["owner"] == "rpi":
                    continue

                self._modules[module_id]["state"] = remote_module.get("state", self._modules[module_id]["state"])
                self._modules[module_id]["block_reason"] = remote_module.get(
                    "block_reason", self._modules[module_id]["block_reason"]
                )

            self._sync_status["last_push_ok"] = True
            self._sync_status["last_sync_ms"] = now_ms
            self._sync_status["last_error"] = ""

            if self._peer_node["reachable"] and self._peer_node["sync_ready"]:
                self._modules["sync_core"]["state"] = "online"
                self._modules["sync_core"]["block_reason"] = "none"
            else:
                self._modules["sync_core"]["state"] = "degraded"
                self._modules["sync_core"]["block_reason"] = "peer_sync_pending"

            self._platform_log.add(
                "sync_core",
                "info",
                "peer_snapshot_applied",
                "ESP32 snapshot applied on Raspberry Pi bridge",
                peer_node_id=self._peer_node["node_id"],
                peer_sync_ready=self._peer_node["sync_ready"],
            )
            self._refresh_runtime_state()

    def mark_peer_unreachable(self, error_text: str) -> None:
        with self._lock:
            self._peer_node["reachable"] = False
            self._peer_node["shell_ready"] = False
            self._peer_node["wifi_ready"] = False
            self._peer_node["sync_ready"] = False
            self._peer_node["reported_mode"] = "manual"
            self._sync_status["last_push_ok"] = False
            self._sync_status["last_error"] = error_text
            self._sync_status["last_sync_ms"] = self._now_ms()
            self._modules["sync_core"]["state"] = "degraded"
            self._modules["sync_core"]["block_reason"] = "owner_unavailable"

            # Пока нет живого snapshot от ESP32, ее модули должны честно уходить в блокировку.
            for module in self._modules.values():
                if module["owner"] == "esp32":
                    module["state"] = "locked"
                    module["block_reason"] = "owner_unavailable"

            self._platform_log.add(
                "sync_core",
                "warn",
                "peer_unreachable",
                "ESP32 peer marked as unreachable",
                error_text=error_text,
            )
            self._refresh_runtime_state()
