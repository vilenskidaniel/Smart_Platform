from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from time import time
from typing import Any


def _now_ms() -> int:
    return int(time() * 1000)


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _as_choice(value: Any, allowed: set[str], default: str) -> str:
    text = str(value or "").strip().lower()
    return text if text in allowed else default


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key, value in base.items():
        if isinstance(value, dict):
            merged[key] = _deep_merge(value, {})
        else:
            merged[key] = value

    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
            continue
        merged[key] = value
    return merged


def normalize_settings(raw: Any, *, updated_at_ms: int | None = None) -> dict[str, Any]:
    payload = raw if isinstance(raw, dict) else {}
    interface = payload.get("interface") if isinstance(payload.get("interface"), dict) else {}
    style = payload.get("style") if isinstance(payload.get("style"), dict) else {}
    synchronization = payload.get("synchronization") if isinstance(payload.get("synchronization"), dict) else {}
    turret = payload.get("turret_policies") if isinstance(payload.get("turret_policies"), dict) else {}
    irrigation = payload.get("irrigation") if isinstance(payload.get("irrigation"), dict) else {}

    return {
        "schema_version": "settings.v1",
        "updated_at_ms": updated_at_ms if updated_at_ms is not None else _as_int(payload.get("updated_at_ms"), _now_ms()),
        "interface": {
            "language": _as_choice(interface.get("language"), {"en", "ru"}, "en"),
            "desktop_controls_enabled": _as_bool(interface.get("desktop_controls_enabled"), True),
            "fullscreen_enabled": _as_bool(interface.get("fullscreen_enabled"), False),
            "show_advanced_diagnostics": _as_bool(interface.get("show_advanced_diagnostics"), False),
        },
        "style": {
            "theme": _as_choice(style.get("theme"), {"meadow", "dawn", "studio"}, "meadow"),
            "density": _as_choice(style.get("density"), {"comfortable", "compact"}, "comfortable"),
        },
        "synchronization": {
            "preferred_mode": _as_choice(synchronization.get("preferred_mode"), {"auto", "manual_review"}, "auto"),
            "prefer_peer_continuity": _as_bool(synchronization.get("prefer_peer_continuity"), True),
        },
        "turret_policies": {
            "silent_observation": _as_bool(turret.get("silent_observation"), True),
            "allow_animal_deterrence": _as_bool(turret.get("allow_animal_deterrence"), True),
            "allow_auto_water_action": _as_bool(turret.get("allow_auto_water_action"), False),
            "return_to_warm_standby": _as_bool(turret.get("return_to_warm_standby"), True),
            "do_not_target_people": True,
        },
        "irrigation": {
            "prefer_driest_zone": _as_bool(irrigation.get("prefer_driest_zone"), True),
            "block_automatic_during_service": _as_bool(irrigation.get("block_automatic_during_service"), True),
            "require_sensor_health": _as_bool(irrigation.get("require_sensor_health"), True),
        },
    }


class SettingsStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = Lock()

    def load(self) -> dict[str, Any]:
        with self._lock:
            raw = self._read_unlocked()
            return normalize_settings(raw)

    def update(self, patch: Any) -> dict[str, Any]:
        update_payload = patch if isinstance(patch, dict) else {}
        with self._lock:
            current = self._read_unlocked()
            merged = _deep_merge(current, update_payload)
            normalized = normalize_settings(merged, updated_at_ms=_now_ms())
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(normalized, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
            return normalized

    def _read_unlocked(self) -> dict[str, Any]:
        if not self._path.is_file():
            return normalize_settings({})
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return normalize_settings({})
        return normalize_settings(raw)