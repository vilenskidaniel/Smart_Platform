from __future__ import annotations

from copy import deepcopy
from typing import Any


_ALLOWED_POWER_CONTEXTS = {"bench_psu", "battery"}
_ALLOWED_VIEW_MODES = {"browser", "fullscreen"}


def _clean_text(value: Any, *, max_length: int = 96) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text


class LaboratorySessionState:
    def __init__(self, *, node_id: str, node_type: str) -> None:
        self._node_id = _clean_text(node_id, max_length=48) or "unknown-node"
        self._node_type = _clean_text(node_type, max_length=24) or "unknown"
        self._next_session_number = 1
        self._active_session: dict[str, Any] | None = None
        self._last_completed_session: dict[str, Any] | None = None
        self._context: dict[str, Any] = {
            "owner_node_id": self._node_id,
            "owner_node_type": self._node_type,
            "power_context": "bench_psu",
            "view_mode": "browser",
            "active_tool": "overview",
            "module_id": "overview",
            "last_update_ms": 0,
        }

    def snapshot(self, now_ms: int) -> dict[str, Any]:
        return {
            "schema_version": "laboratory-session.v1",
            "status": "active" if self._active_session is not None else "idle",
            "timestamp_ms": max(0, int(now_ms)),
            "context": deepcopy(self._context),
            "active_session": deepcopy(self._active_session),
            "last_completed_session": deepcopy(self._last_completed_session),
        }

    def update_context(
        self,
        *,
        now_ms: int,
        power_context: str = "",
        view_mode: str = "",
        active_tool: str = "",
        module_id: str = "",
    ) -> dict[str, Any]:
        if power_context:
            normalized_power = _clean_text(power_context, max_length=24).lower()
            if normalized_power in _ALLOWED_POWER_CONTEXTS:
                self._context["power_context"] = normalized_power

        if view_mode:
            normalized_view = _clean_text(view_mode, max_length=24).lower()
            if normalized_view in _ALLOWED_VIEW_MODES:
                self._context["view_mode"] = normalized_view

        if active_tool:
            self._context["active_tool"] = _clean_text(active_tool, max_length=48) or self._context["active_tool"]

        if module_id:
            self._context["module_id"] = _clean_text(module_id, max_length=48) or self._context["module_id"]

        self._context["last_update_ms"] = max(0, int(now_ms))
        if self._active_session is not None:
            self._active_session["last_updated_ms"] = self._context["last_update_ms"]
        return self.snapshot(now_ms)

    def start_session(
        self,
        *,
        now_ms: int,
        operator: str = "",
        objective: str = "",
        hardware_profile: str = "",
        external_module: str = "",
        power_context: str = "",
        view_mode: str = "",
        active_tool: str = "",
        module_id: str = "",
    ) -> dict[str, Any]:
        if self._active_session is not None:
            raise ValueError("laboratory session is already active")

        self.update_context(
            now_ms=now_ms,
            power_context=power_context,
            view_mode=view_mode,
            active_tool=active_tool,
            module_id=module_id,
        )

        session_id = f"lab-{self._node_id}-{self._next_session_number:04d}"
        self._next_session_number += 1
        self._active_session = {
            "session_id": session_id,
            "status": "active",
            "operator": _clean_text(operator, max_length=40) or "local-operator",
            "objective": _clean_text(objective, max_length=80),
            "hardware_profile": _clean_text(hardware_profile, max_length=80),
            "external_module": _clean_text(external_module, max_length=80),
            "owner_node_id": self._node_id,
            "owner_node_type": self._node_type,
            "started_at_ms": max(0, int(now_ms)),
            "last_updated_ms": max(0, int(now_ms)),
        }
        return deepcopy(self._active_session)

    def update_session(
        self,
        *,
        now_ms: int,
        operator: str = "",
        objective: str = "",
        hardware_profile: str = "",
        external_module: str = "",
    ) -> dict[str, Any]:
        if self._active_session is None:
            raise ValueError("laboratory session is not active")

        if operator:
            self._active_session["operator"] = _clean_text(operator, max_length=40) or self._active_session["operator"]
        if objective or objective == "":
            self._active_session["objective"] = _clean_text(objective, max_length=80)
        if hardware_profile or hardware_profile == "":
            self._active_session["hardware_profile"] = _clean_text(hardware_profile, max_length=80)
        if external_module or external_module == "":
            self._active_session["external_module"] = _clean_text(external_module, max_length=80)

        self._active_session["last_updated_ms"] = max(0, int(now_ms))
        return deepcopy(self._active_session)

    def finish_session(self, *, now_ms: int, summary_note: str = "") -> dict[str, Any]:
        if self._active_session is None:
            raise ValueError("laboratory session is not active")

        finished = deepcopy(self._active_session)
        finished["status"] = "completed"
        finished["finished_at_ms"] = max(0, int(now_ms))
        finished["duration_ms"] = max(0, finished["finished_at_ms"] - int(finished.get("started_at_ms", 0)))
        finished["summary_note"] = _clean_text(summary_note, max_length=120)
        self._last_completed_session = finished
        self._active_session = None
        self._context["last_update_ms"] = max(0, int(now_ms))
        return deepcopy(finished)

    def report_metadata(self) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "lab_session_status": "active" if self._active_session is not None else "idle",
            "lab_power_context": self._context.get("power_context", "bench_psu"),
            "lab_view_mode": self._context.get("view_mode", "browser"),
            "lab_active_tool": self._context.get("active_tool", "overview"),
            "lab_context_module": self._context.get("module_id", "overview"),
            "lab_owner_node_id": self._context.get("owner_node_id", self._node_id),
            "lab_owner_node_type": self._context.get("owner_node_type", self._node_type),
        }
        if self._active_session is not None:
            metadata.update(
                {
                    "lab_session_id": self._active_session.get("session_id", ""),
                    "lab_operator": self._active_session.get("operator", ""),
                    "lab_objective": self._active_session.get("objective", ""),
                    "lab_hardware_profile": self._active_session.get("hardware_profile", ""),
                    "lab_external_module": self._active_session.get("external_module", ""),
                }
            )
        return {key: value for key, value in metadata.items() if value not in {"", None}}