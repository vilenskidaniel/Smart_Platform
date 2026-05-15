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


def _clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, _as_int(value, default)))


def _string_options(value: Any, defaults: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    raw_values = value if isinstance(value, list) else []
    for item in [*raw_values, *defaults]:
        text = str(item or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(text[:80])
        if len(result) >= 18:
            break
    return result


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
    interface_audio = interface.get("audio") if isinstance(interface.get("audio"), dict) else {}
    style = payload.get("style") if isinstance(payload.get("style"), dict) else {}
    synchronization = payload.get("synchronization") if isinstance(payload.get("synchronization"), dict) else {}
    selected_domains = (
        synchronization.get("selected_domains")
        if isinstance(synchronization.get("selected_domains"), dict)
        else {}
    )
    keyboard = payload.get("keyboard") if isinstance(payload.get("keyboard"), dict) else {}
    keyboard_bindings = keyboard.get("bindings") if isinstance(keyboard.get("bindings"), dict) else {}
    component_options = payload.get("component_field_options") if isinstance(payload.get("component_field_options"), dict) else {}
    assigned_module_options = component_options.get("assigned_module")
    if not isinstance(assigned_module_options, list):
        assigned_module_options = component_options.get("module_owner")
    node_role_options = component_options.get("node_role")
    turret_audio = payload.get("turret_audio") if isinstance(payload.get("turret_audio"), dict) else {}
    attack_audio = turret_audio.get("attack_audio") if isinstance(turret_audio.get("attack_audio"), dict) else {}
    voice_fx = turret_audio.get("voice_fx") if isinstance(turret_audio.get("voice_fx"), dict) else {}
    turret = payload.get("turret_policies") if isinstance(payload.get("turret_policies"), dict) else {}
    irrigation = payload.get("irrigation") if isinstance(payload.get("irrigation"), dict) else {}
    languages = {"en", "ru", "he", "de", "fr", "es", "zh", "ar"}
    themes = {"meadow", "dawn", "studio", "midnight", "sunlit", "night", "minimal", "contrast"}
    sync_domain_ids = [
        "service_link",
        "module_state",
        "shared_preferences",
        "reports_history",
        "plant_library",
        "media_content",
        "component_registry",
        "software_versions",
    ]
    preferred_mode = _as_choice(synchronization.get("preferred_mode"), {"auto", "manual_review"}, "auto")
    normalized_selected = {
        domain_id: (_as_bool(selected_domains.get(domain_id), True))
        for domain_id in sync_domain_ids
    }
    if preferred_mode == "auto":
        normalized_selected = {domain_id: True for domain_id in sync_domain_ids}

    attack_audio_binding = str(keyboard_bindings.get("attack_audio") or keyboard_bindings.get("piezo") or "KeyQ")

    return {
        "schema_version": "settings.v1",
        "updated_at_ms": updated_at_ms if updated_at_ms is not None else _as_int(payload.get("updated_at_ms"), _now_ms()),
        "interface": {
            "language": _as_choice(interface.get("language"), languages, "en"),
            "desktop_controls_enabled": _as_bool(interface.get("desktop_controls_enabled"), True),
            "fullscreen_enabled": _as_bool(interface.get("fullscreen_enabled"), False),
            "show_advanced_diagnostics": _as_bool(interface.get("show_advanced_diagnostics"), False),
            "audio": {
                "volume_percent": _clamp_int(interface_audio.get("volume_percent"), 60, 0, 100),
                "muted": _as_bool(interface_audio.get("muted"), False),
                "silent_mode": _as_bool(interface_audio.get("silent_mode"), False),
            },
        },
        "style": {
            "theme": _as_choice(style.get("theme"), themes, "meadow"),
            "density": _as_choice(style.get("density"), {"comfortable", "compact"}, "comfortable"),
        },
        "synchronization": {
            "preferred_mode": preferred_mode,
            "prefer_peer_continuity": _as_bool(synchronization.get("prefer_peer_continuity"), True),
            "poll_interval_seconds": _clamp_int(synchronization.get("poll_interval_seconds"), 30, 5, 300),
            "selected_domains": normalized_selected,
        },
        "component_field_options": {
            "component_kind": _string_options(component_options.get("component_kind"), ["sensor", "actuator", "power", "controller"]),
            "assigned_module": _string_options(assigned_module_options, ["turret", "irrigation", "power"]),
            "node_role": _string_options(node_role_options, ["compute_node", "io_node", "shared"]),
            "power_profile": _string_options(component_options.get("power_profile"), ["3.3V", "5V", "5-6V", "12V", "PWM", "I2C/ADC"]),
            "pinout": _string_options(component_options.get("pinout"), ["TBD", "CSI ribbon", "ESP32 GPIO TBD", "PWM TBD", "relay/MOSFET TBD", "I2C/ADC TBD"]),
            "tolerance": _string_options(component_options.get("tolerance"), ["50-100%", "sensor health", "calibration required", "angle limits TBD", "voltage/current limits"]),
            "operating_modes": _string_options(component_options.get("operating_modes"), ["sample", "manual aim", "preview, capture, evidence", "pulse, deterrence", "zone open/close"]),
        },
        "keyboard": {
            "turret_manual_enabled": _as_bool(keyboard.get("turret_manual_enabled"), True),
            "base_power_percent": _clamp_int(keyboard.get("base_power_percent"), 50, 1, 100),
            "shift_power_percent": _clamp_int(keyboard.get("shift_power_percent"), 100, 1, 100),
            "bindings": {
                "aim_up": str(keyboard_bindings.get("aim_up") or "ArrowUp"),
                "aim_down": str(keyboard_bindings.get("aim_down") or "ArrowDown"),
                "aim_left": str(keyboard_bindings.get("aim_left") or "ArrowLeft"),
                "aim_right": str(keyboard_bindings.get("aim_right") or "ArrowRight"),
                "irrigation_zone_1": str(keyboard_bindings.get("irrigation_zone_1") or "Digit1"),
                "irrigation_zone_2": str(keyboard_bindings.get("irrigation_zone_2") or "Digit2"),
                "irrigation_zone_3": str(keyboard_bindings.get("irrigation_zone_3") or "Digit3"),
                "irrigation_zone_4": str(keyboard_bindings.get("irrigation_zone_4") or "Digit4"),
                "irrigation_zone_5": str(keyboard_bindings.get("irrigation_zone_5") or "Digit5"),
                "attack_audio": attack_audio_binding,
                "piezo": attack_audio_binding,
                "strobe": str(keyboard_bindings.get("strobe") or "KeyW"),
                "water": str(keyboard_bindings.get("water") or "KeyE"),
                "voice_fx_talk": str(keyboard_bindings.get("voice_fx_talk") or "KeyV"),
                "capture": str(keyboard_bindings.get("capture") or "Space"),
                "power_modifier": str(keyboard_bindings.get("power_modifier") or "Shift"),
            },
        },
        "turret_audio": {
            "attack_audio": {
                "driver_profile": _as_choice(attack_audio.get("driver_profile"), {"tpa3116d2_xh_m543"}, "tpa3116d2_xh_m543"),
                "default_scenario_id": str(attack_audio.get("default_scenario_id") or "dual_channel_deterrence")[:80],
                "channel_a_power_percent": _clamp_int(attack_audio.get("channel_a_power_percent"), 60, 0, 100),
                "channel_b_power_percent": _clamp_int(attack_audio.get("channel_b_power_percent"), 60, 0, 100),
            },
            "voice_fx": {
                "device_name": str(voice_fx.get("device_name") or "Soundcore Motion 300")[:80],
                "transport": _as_choice(voice_fx.get("transport"), {"bluetooth"}, "bluetooth"),
                "talkback_enabled": _as_bool(voice_fx.get("talkback_enabled"), True),
                "microphone_expected": _as_bool(voice_fx.get("microphone_expected"), True),
                "effect_profile": _as_choice(voice_fx.get("effect_profile"), {"natural", "filtered", "robotic", "pitch_shift"}, "natural"),
            },
        },
        "turret_policies": {
            "silent_observation": _as_bool(turret.get("silent_observation"), True),
            "allow_animal_deterrence": _as_bool(turret.get("allow_animal_deterrence"), True),
            "allow_auto_water_action": _as_bool(turret.get("allow_auto_water_action"), False),
            "allow_auto_capture": _as_bool(turret.get("allow_auto_capture"), True),
            "return_to_warm_standby": _as_bool(turret.get("return_to_warm_standby"), True),
            "max_recording_seconds": _clamp_int(turret.get("max_recording_seconds"), 30, 5, 36000),
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
