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
            "Coordinator shell is reachable",
            _READY if bool(current_node.get("shell_ready", True)) else _BLOCKED,
            "Local shell is ready for the next test step."
            if bool(current_node.get("shell_ready", True))
            else "Current shell is not ready for coordinated testing yet.",
            "Open the current shell and confirm the local node is reachable before wiring the next board.",
        ),
        _item(
            "reports_archive",
            "Persistent reports history is available",
            _READY if reports_persistent else _ATTENTION,
            "Gallery > Reports already writes to persistent archive storage."
            if reports_persistent
            else "Reports still fall back to volatile platform-log baseline on this node.",
            "Use Raspberry Pi with content storage enabled so each test pass survives restart.",
        ),
        _item(
            "safe_start_mode",
            "System starts from safe mode",
            _status_for_mode(active_mode, emergency_latched, fault_latched),
            _mode_summary(active_mode, emergency_latched, fault_latched),
            _mode_action(active_mode, emergency_latched, fault_latched),
        ),
        _item(
            "actuators_idle",
            "Sensitive channels are idle before reconnect",
            _BLOCKED if emergency_latched or fault_latched else (_ATTENTION if active_actuators else _READY),
            "All sensitive turret channels are idle."
            if not active_actuators and not emergency_latched and not fault_latched
            else "Some turret channels are still active: " + ", ".join(active_actuators)
            if active_actuators
            else "Emergency or fault interlock is latched, so the session is not in clean bring-up state.",
            "Return the runtime to manual safe idle and make sure motion, strobe, water, and audio are inactive.",
        ),
        _item(
            "peer_owner_link",
            "Peer owner link is ready for ESP32-owned tests",
            _READY if peer_ready else _ATTENTION,
            "ESP32 peer is reachable and owner handoff can open peer-owned laboratory slices."
            if peer_ready
            else "ESP32 peer is not ready yet, so only local Raspberry Pi slices can be tested right now.",
            "Power the ESP32 node, wait for shell+sync readiness, then continue with strobe bench and irrigation.",
        ),
    ]

    bringup_sequence = [
        _step(
            "shell_smoke",
            "Shell And Reports Smoke",
            "shared",
            "/",
            preflight[0]["status"],
            "Confirm shell load, Gallery > Reports availability, and local activity summaries before hardware work.",
            "Start every physical session by verifying the shell, Laboratory entry, and report archive path.",
        ),
        _step(
            "peer_link_smoke",
            "Peer Link And Owner Handoff",
            "shared",
            "/service",
            _READY if peer_ready else _ATTENTION,
            "Verify peer heartbeat, sync readiness, and owner-aware handoff before touching ESP32-owned modules.",
            "Use this step to confirm the ESP32 owner shows as reachable from the coordinator shell.",
        ),
        _step(
            "esp32_strobe_bench",
            "ESP32 / Strobe Bench",
            "esp32",
            "/service?tool=strobe_bench",
            _READY if peer_ready else _BLOCKED,
            "Short pulse and preset bring-up for the bench strobe should happen before integrated turret tests.",
            "Begin with the lowest-energy pulse testcase and keep the hardware emergency chain available.",
        ),
        _step(
            "esp32_irrigation_service",
            "ESP32 / Irrigation Service",
            "esp32",
            "/service?tool=irrigation_service",
            _READY if peer_ready else _BLOCKED,
            "Validate zone service commands, sensor simulation, and owner handoff without Raspberry Pi pretending to own irrigation.",
            "Run dry and short-duration testcases first, then move to water-path checks only after service control is stable.",
        ),
        _step(
            "turret_service_lane",
            "Raspberry Pi / Turret Service",
            "rpi",
            "/service?tool=turret_service",
            _status_for_turret_lane(active_mode, emergency_latched, fault_latched),
            "Validate local turret runtime, interlock visibility, and service scenarios from the Raspberry Pi owner shell.",
            "Confirm emergency visibility, safe idle scenario, and owner-side action gating before integrated turret IO tests.",
        ),
        _step(
            "reports_review",
            "Gallery > Reports Review",
            "shared",
            "/gallery?tab=reports",
            _READY if reports_persistent else _ATTENTION,
            "Review chronological evidence after each board/module step before moving to the next testcase bundle.",
            "Use Reports as the canonical session history instead of relying on transient live-log text alone.",
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
        return "Emergency interlock is latched. Physical bring-up must stop until the chain is cleared."
    if fault_latched or active_mode == "fault":
        return "Fault interlock is latched. Resolve the fault before the next hardware testcase."
    if active_mode == "automatic":
        return "Automatic mode is active. Sequential hardware bring-up should return to manual or service-safe state first."
    if active_mode == "service_test":
        return "Service/test mode is active and already suitable for isolated module bring-up."
    return "Runtime starts from manual baseline, which is appropriate for sequential hardware testing."


def _mode_action(active_mode: str, emergency_latched: bool, fault_latched: bool) -> str:
    if emergency_latched or active_mode == "emergency":
        return "Clear the hardware/software emergency state before reconnecting any sensitive branch."
    if fault_latched or active_mode == "fault":
        return "Resolve the active fault, then clear the interlock and return to manual."
    if active_mode == "automatic":
        return "Switch back to manual before continuing with isolated module tests."
    if active_mode == "service_test":
        return "Stay in service/test while running isolated module slices."
    return "Manual baseline is fine for shell smoke and controlled bring-up."


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
        return "Testing readiness is green. The next board/module can be connected in the suggested bring-up order."
    if overall_status == _BLOCKED:
        blockers = [item["title"] for item in preflight if item["status"] == _BLOCKED]
        return "Testing is blocked until these items are cleared: " + ", ".join(blockers)
    warnings = [item["title"] for item in preflight if item["status"] == _ATTENTION]
    return "Testing can continue with caution. Attention is required for: " + ", ".join(warnings)


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
