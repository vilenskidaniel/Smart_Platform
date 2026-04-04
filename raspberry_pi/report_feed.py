from __future__ import annotations

from typing import Any


_LABORATORY_SOURCES = {
    "turret_scenarios",
    "strobe_bench",
    "irrigation_service",
    "service_mode",
    "testcase_capture",
}
_TURRET_SOURCES = {"turret_runtime", "turret_driver_layer", "turret_bridge", "strobe"}
_IRRIGATION_SOURCES = {"irrigation"}
_SYSTEM_SOURCES = {"system_shell", "sync_core"}
_TESTCASE_RESULTS = {"pass", "fail", "warn"}


def build_reports_snapshot(platform_log: dict[str, Any], limit: int = 60) -> dict[str, Any]:
    clamped_limit = max(1, limit)
    raw_entries = list(platform_log.get("entries", []))[:clamped_limit]
    entries = [normalize_report_entry(entry) for entry in raw_entries]
    return build_reports_snapshot_from_entries(
        entries,
        count=int(platform_log.get("count", len(entries))),
        limit=clamped_limit,
        source_kind="platform_log_baseline",
    )


def build_reports_snapshot_from_entries(
    entries: list[dict[str, Any]],
    *,
    count: int | None = None,
    limit: int = 60,
    source_kind: str = "platform_log_baseline",
) -> dict[str, Any]:
    clamped_limit = max(1, limit)
    visible_entries = list(entries)[:clamped_limit]
    return {
        "schema_version": "reports-feed.v1",
        "source_kind": source_kind,
        "count": int(count if count is not None else len(visible_entries)),
        "limit": clamped_limit,
        "summary": _build_summary(visible_entries),
        "entries": visible_entries,
    }


def normalize_report_entry(entry: dict[str, Any]) -> dict[str, Any]:
    source = str(entry.get("source", ""))
    raw_type = str(entry.get("type", "event"))
    parameters = _normalize_parameters(entry.get("details"))
    source_surface = _infer_surface(source)
    entry_type = _infer_entry_type(source, raw_type, parameters)
    return {
        "report_id": f"report-{entry.get('event_id', 'unknown')}",
        "event_id": entry.get("event_id", ""),
        "timestamp_ms": int(entry.get("timestamp_ms", 0)),
        "origin_node": entry.get("origin_node", "unknown"),
        "mirrored": bool(entry.get("mirrored", False)),
        "source": source,
        "entry_type": entry_type,
        "source_surface": source_surface,
        "source_mode": _infer_source_mode(source_surface, parameters),
        "module_id": _infer_module_id(source, parameters),
        "title": _humanize_type(raw_type, parameters),
        "message": entry.get("message", ""),
        "severity": entry.get("level", "info"),
        "result": _infer_result(entry, parameters),
        "duration_ms": _infer_duration_ms(parameters),
        "parameters": parameters,
        "raw_type": raw_type,
    }


def _normalize_parameters(details: Any) -> dict[str, Any]:
    if isinstance(details, dict):
        return details
    if details in {"", None}:
        return {}
    return {"raw": details}


def _infer_surface(source: str) -> str:
    if source in _LABORATORY_SOURCES:
        return "laboratory"
    if source in _TURRET_SOURCES:
        return "turret"
    if source in _IRRIGATION_SOURCES:
        return "irrigation"
    if source in _SYSTEM_SOURCES:
        return "system"
    return "unknown"


def _infer_source_mode(source_surface: str, parameters: dict[str, Any]) -> str:
    for key in ("mode", "active_mode", "reported_mode"):
        value = parameters.get(key)
        if isinstance(value, str) and value:
            return value
    if source_surface == "laboratory":
        return "service_test"
    if source_surface in {"turret", "irrigation"}:
        return "product_runtime"
    if source_surface == "system":
        return "system"
    return "unknown"


def _infer_module_id(source: str) -> str:
    return _infer_module_id_from_parameters(source, {})


def _infer_module_id_from_parameters(source: str, parameters: dict[str, Any]) -> str:
    explicit_module = parameters.get("module_id")
    if isinstance(explicit_module, str) and explicit_module:
        return explicit_module
    if source in {"turret_runtime", "turret_scenarios", "turret_driver_layer", "turret_bridge"}:
        return "turret_bridge"
    if source in {"strobe", "strobe_bench"}:
        return source
    if source in {"irrigation", "irrigation_service"}:
        return source
    if source in {"system_shell", "sync_core", "service_mode"}:
        return source
    return source or "unknown"


def _infer_module_id(source: str, parameters: dict[str, Any]) -> str:
    return _infer_module_id_from_parameters(source, parameters)


def _infer_entry_type(source: str, raw_type: str, parameters: dict[str, Any]) -> str:
    if raw_type.startswith("testcase_") or (
        isinstance(parameters.get("case_id"), str) and isinstance(parameters.get("test_result"), str)
    ):
        return "testcase"
    if raw_type == "operator_note":
        return "operator_note"
    if raw_type.startswith("scenario_"):
        return "scenario"
    if "interlock" in raw_type:
        return "interlock"
    if "mode" in raw_type:
        return "mode_change"
    if source == "sync_core":
        return "sync"
    if any(token in raw_type for token in ("subsystem", "flag", "strobe_", "irrigation_", "driver_")):
        return "action"
    return "event"


def _infer_result(entry: dict[str, Any], parameters: dict[str, Any]) -> str:
    testcase_result = parameters.get("test_result")
    if isinstance(testcase_result, str):
        normalized = testcase_result.strip().lower()
        if normalized in _TESTCASE_RESULTS:
            return normalized

    accepted = parameters.get("accepted")
    if isinstance(accepted, bool):
        return "accepted" if accepted else "rejected"

    raw_type = str(entry.get("type", ""))
    severity = str(entry.get("level", "info"))

    if raw_type.endswith("_rejected"):
        return "rejected"
    if raw_type.endswith("_started"):
        return "started"
    if raw_type.endswith("_finished"):
        failed_steps = parameters.get("failed_steps")
        if isinstance(failed_steps, list) and failed_steps:
            return "completed_with_warnings"
        return "completed"
    if severity == "error":
        return "failed"
    if severity == "warning":
        return "attention"
    return "recorded"


def _infer_duration_ms(parameters: dict[str, Any]) -> int | None:
    for key in ("duration_ms", "runtime_ms", "active_time_ms"):
        value = parameters.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def _humanize_type(raw_type: str, parameters: dict[str, Any]) -> str:
    if not raw_type:
        return "Event"
    if raw_type == "testcase_result_recorded":
        case_id = parameters.get("case_id")
        if isinstance(case_id, str) and case_id:
            return f"Testcase {case_id}"
        return "Testcase Result"
    return " ".join(part.capitalize() for part in raw_type.split("_"))


def _build_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    surfaces: dict[str, int] = {}
    entry_types: dict[str, int] = {}
    warning_count = 0
    error_count = 0
    for entry in entries:
        surface = str(entry.get("source_surface", "unknown"))
        entry_type = str(entry.get("entry_type", "event"))
        surfaces[surface] = surfaces.get(surface, 0) + 1
        entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
        severity = entry.get("severity")
        if severity == "warning":
            warning_count += 1
        elif severity == "error":
            error_count += 1
    return {
        "warning_count": warning_count,
        "error_count": error_count,
        "surfaces": surfaces,
        "entry_types": entry_types,
    }
