from __future__ import annotations

from typing import Any


_READY = "ready"
_ATTENTION = "attention"
_BLOCKED = "blocked"
_ACTIVE_ACTUATORS = {"motion", "strobe", "water", "audio"}


def build_laboratory_readiness(
    *,
    current_node: dict[str, Any],
    peer_node: dict[str, Any],
    active_mode: str,
    runtime: dict[str, Any],
    reports_source_kind: str,
) -> dict[str, Any]:
    interlocks = runtime.get("interlocks", {})
    summary = runtime.get("summary", {})
    local_shell_ready = bool(current_node.get("shell_ready", True))
    emergency_latched = bool(interlocks.get("emergency_latched", False))
    fault_latched = bool(interlocks.get("fault_latched", False))
    peer_ready = _peer_ready(peer_node)
    active_actuators = [
        subsystem_id for subsystem_id in summary.get("active_subsystems", []) if subsystem_id in _ACTIVE_ACTUATORS
    ]
    reports_persistent = reports_source_kind == "report_archive_v1"

    preflight = [
        _item(
            "local_shell_ready",
            "Local shell is open",
            _READY if local_shell_ready else _BLOCKED,
            "This shell is open and ready for the next check."
            if local_shell_ready
            else "Open the current shell before starting the next test.",
            "Stay on the local shell and confirm the page is reachable before touching more hardware.",
        ),
        _item(
            "reports_archive",
            "Reports can be saved",
            _READY if reports_persistent else _ATTENTION,
            "Gallery > Reports already saves to persistent storage."
            if reports_persistent
            else "Reports still use a temporary local log on this node.",
            "You can continue, but move to Raspberry Pi persistent storage if the results must survive restart.",
        ),
        _item(
            "safe_start_mode",
            "System starts safely",
            _status_for_mode(active_mode, emergency_latched, fault_latched),
            _mode_summary(active_mode, emergency_latched, fault_latched),
            _mode_action(active_mode, emergency_latched, fault_latched),
        ),
        _item(
            "actuators_idle",
            "Sensitive outputs are idle",
            _BLOCKED if emergency_latched or fault_latched else (_ATTENTION if active_actuators else _READY),
            "Motion, strobe, water, and audio are idle."
            if not active_actuators and not emergency_latched and not fault_latched
            else "Some sensitive channels are still active: " + ", ".join(active_actuators)
            if active_actuators
            else "Emergency or fault is still latched, so the session is not in a clean start state.",
            "Return to safe idle and make sure motion, strobe, water, and audio are all inactive.",
        ),
        _item(
            "peer_owner_link",
            "ESP32 link is ready",
            _READY if peer_ready else _ATTENTION,
            "ESP32 is reachable, so peer-owned laboratory slices can open through owner handoff."
            if peer_ready
            else "ESP32 is not ready yet, so stay on local Raspberry Pi slices for now.",
            "You can keep testing local Raspberry Pi slices now. Bring ESP32 online before strobe bench or irrigation checks.",
        ),
    ]

    bringup_sequence = [
        _step(
            "shell_smoke",
            "Open shell and reports",
            "shared",
            "/",
            preflight[0]["status"],
            "Check that the shell opens, Laboratory is reachable, and Reports can be reviewed.",
            "Start every physical session by confirming the shell path before deeper hardware work.",
        ),
        _step(
            "rpi_display_checks",
            "Raspberry Pi / Displays",
            "rpi",
            "/service?tool=rpi_touch_display",
            _READY if local_shell_ready else _BLOCKED,
            "Run the owner-side screen pass: color patterns, fullscreen check, and touch grid.",
            "Use this step for the local display pass before or between deeper module checks.",
        ),
        _step(
            "peer_link_smoke",
            "Check peer link",
            "shared",
            "/service",
            _READY if peer_ready else _ATTENTION,
            "Verify heartbeat, sync, and owner-aware handoff before opening ESP32-owned slices.",
            "Use this step to confirm ESP32 really appears as the owner from the current shell.",
        ),
        _step(
            "esp32_strobe_bench",
            "ESP32 / Strobe Bench",
            "esp32",
            "/service?tool=strobe_bench",
            _READY if peer_ready else _BLOCKED,
            "Run the short pulse and preset pass before integrated turret tests.",
            "Start with the lowest-energy pulse and keep the emergency chain available.",
        ),
        _step(
            "esp32_irrigation_service",
            "ESP32 / Irrigation Service",
            "esp32",
            "/service?tool=irrigation_service",
            _READY if peer_ready else _BLOCKED,
            "Check zone commands, sensor simulation, and owner handoff without fake local irrigation ownership.",
            "Run dry and short-duration cases first, then move to water-path checks after service control looks stable.",
        ),
        _step(
            "turret_service_lane",
            "Raspberry Pi / Turret Service",
            "rpi",
            "/service?tool=turret_service",
            _status_for_turret_lane(active_mode, emergency_latched, fault_latched),
            "Check local turret runtime, interlock visibility, and service scenarios from the Raspberry Pi owner shell.",
            "Confirm emergency visibility, safe idle, and owner-side action gating before integrated turret IO tests.",
        ),
        _step(
            "reports_review",
            "Review reports",
            "shared",
            "/gallery?tab=reports",
            _READY if reports_persistent else _ATTENTION,
            "Review the saved evidence before moving to the next bundle of checks.",
            "Use Reports as the session history instead of relying only on the live log.",
        ),
    ]

    overall_status = _combine_statuses([item["status"] for item in preflight])
    next_action = _next_action(preflight, bringup_sequence)
    return {
        "schema_version": "laboratory-readiness.v1",
        "overall_status": overall_status,
        "summary": _overall_summary(overall_status, preflight),
        "active_mode": active_mode,
        "reports_source_kind": reports_source_kind,
        "next_action": next_action,
        "preflight": preflight,
        "bringup_sequence": bringup_sequence,
    }


def _peer_ready(peer_node: dict[str, Any]) -> bool:
    return bool(
        peer_node.get("reachable")
        and peer_node.get("shell_ready")
        and peer_node.get("sync_ready")
        and peer_node.get("shell_base_url")
    )


def _status_for_mode(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return _BLOCKED
    if fault_latched or active_mode == "fault":
        return _BLOCKED
    if active_mode == "automatic":
        return _ATTENTION
    return _READY


def _mode_summary(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return "Emergency is latched. Stop physical bring-up until it is cleared."
    if fault_latched or active_mode == "fault":
        return "Fault is latched. Clear it before the next hardware test."
    if active_mode == "automatic":
        return "Automatic mode is active. Return to manual or service-safe mode first."
    if active_mode == "service_test":
        return "Service/test mode is active and suitable for isolated module checks."
    return "Manual mode is active, which is a good baseline for step-by-step testing."


def _mode_action(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return "Clear the emergency state before reconnecting any sensitive branch."
    if fault_latched or active_mode == "fault":
        return "Resolve the fault, clear the latch, and return to manual."
    if active_mode == "automatic":
        return "Switch back to manual before continuing with isolated tests."
    if active_mode == "service_test":
        return "Stay in service/test while you run isolated module slices."
    return "Stay in manual while you work through the bring-up order."


def _status_for_turret_lane(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return _BLOCKED
    if fault_latched or active_mode == "fault":
        return _BLOCKED
    if active_mode == "automatic":
        return _ATTENTION
    return _READY


def _combine_statuses(statuses: list[str]) -> str:
    if any(status == _BLOCKED for status in statuses):
        return _BLOCKED
    if any(status == _ATTENTION for status in statuses):
        return _ATTENTION
    return _READY


def _overall_summary(overall_status: str, preflight: list[dict[str, Any]]) -> str:
    if overall_status == _READY:
        return "Readiness looks good. Follow the bring-up order below."
    if overall_status == _BLOCKED:
        blockers = [item["title"] for item in preflight if item["status"] == _BLOCKED]
        return "Testing is blocked. Clear these items first: " + ", ".join(blockers)
    warnings = [item["title"] for item in preflight if item["status"] == _ATTENTION]
    return "You can continue, but watch these items: " + ", ".join(warnings)


def _next_action(preflight: list[dict[str, Any]], bringup_sequence: list[dict[str, Any]]) -> dict[str, Any]:
    for item in preflight:
        if item["status"] != _READY:
            return {
                "kind": "preflight",
                "id": item["id"],
                "title": item["title"],
                "status": item["status"],
                "action": item["action"],
            }
    for step in bringup_sequence:
        if step["status"] != _READY:
            return {
                "kind": "bringup",
                "id": step["id"],
                "title": step["title"],
                "status": step["status"],
                "action": step["action"],
                "route": step["route"],
            }
    first_step = bringup_sequence[0]
    return {
        "kind": "bringup",
        "id": first_step["id"],
        "title": first_step["title"],
        "status": first_step["status"],
        "action": first_step["action"],
        "route": first_step["route"],
    }


def _item(item_id: str, title: str, status: str, summary: str, action: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "title": title,
        "status": status,
        "summary": summary,
        "action": action,
    }


def _step(
    step_id: str,
    title: str,
    owner_scope: str,
    route: str,
    status: str,
    summary: str,
    action: str,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "title": title,
        "owner_scope": owner_scope,
        "route": route,
        "status": status,
        "summary": summary,
        "action": action,
    }
