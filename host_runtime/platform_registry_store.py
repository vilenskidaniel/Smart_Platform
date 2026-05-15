from __future__ import annotations

import copy
import json
import re
import time
from pathlib import Path
from threading import Lock
from typing import Any


SCHEMA_VERSION = "platform_registry.v1"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _localized(en: str, ru: str) -> dict[str, str]:
    return {"en": en, "ru": ru}


DEFAULT_REGISTRY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "updated_at_ms": 0,
    "modules": [
        {
            "id": "turret",
            "title": _localized("Turret", "Турель"),
            "summary": _localized("Camera-guided manual and automatic deterrence module.", "Модуль наведения, наблюдения и безопасного отпугивания."),
            "owner_role": "compute_node",
            "runtime_module_id": "turret_bridge",
            "state": "disconnected",
            "component_ids": ["camera", "strobe", "ultrasonic_pair", "horn_pair", "attack_audio_driver", "voice_fx", "water_pump", "servo_pan_tilt", "lidar"],
        },
        {
            "id": "irrigation",
            "title": _localized("Irrigation", "Ирригация"),
            "summary": _localized("Watering logic, plant rules, valves, pumps, and moisture sensors.", "Полив, библиотека растений, клапаны, насосы и датчики влажности."),
            "owner_role": "io_node",
            "runtime_module_id": "irrigation",
            "state": "disconnected",
            "component_ids": ["soil_moisture", "air_temp_humidity", "drip_valves", "peristaltic_pump", "light_sensor"],
        },
        {
            "id": "power",
            "title": _localized("Power", "Питание"),
            "summary": _localized("Energy input, conversion, and battery monitoring.", "Питание, преобразование энергии и мониторинг батареи."),
            "owner_role": "shared",
            "runtime_module_id": "",
            "state": "disconnected",
            "component_ids": ["solar_panel", "converter", "battery_monitor"],
        },
        {
            "id": "cat_feeder",
            "title": _localized("Cat Feeder", "Кормушка для кота"),
            "summary": _localized(
                "Motion wakes the camera; video identification and optional meow/request signal can notify the owner or start feeding.",
                "Датчик движения будит камеру; видеоидентификация и сигнал запроса помогают уведомить владельца или начать кормление.",
            ),
            "owner_role": "compute_node",
            "runtime_module_id": "",
            "state": "simulated",
            "component_ids": ["cat_feeder_servo", "cat_feeder_motion_sensor", "cat_feeder_camera"],
        },
    ],
    "components": [
        {"id": "camera", "title": _localized("Raspberry Pi Camera", "Камера Raspberry Pi"), "kind": "sensor", "assigned_module": "turret", "power_profile": "5V / CSI", "pinout": "CSI ribbon", "tolerance": "stream check", "operating_modes": "preview, capture, evidence", "state": "not_detected"},
        {"id": "strobe", "title": _localized("Strobe", "Стробоскоп"), "kind": "actuator", "assigned_module": "turret", "power_profile": "12V driver", "pinout": "ESP32 GPIO TBD", "tolerance": "50-100%", "operating_modes": "pulse, deterrence", "state": "not_detected"},
        {"id": "ultrasonic_pair", "title": _localized("Ultrasonic pair", "Ультразвуковая пара"), "kind": "actuator", "assigned_module": "turret", "power_profile": "TPA3116D2 channel output", "pinout": "audio amp output TBD", "tolerance": "frequency and power profile", "operating_modes": "tone, sweep, deterrence", "state": "not_detected"},
        {"id": "horn_pair", "title": _localized("Horn pair / piezo stage", "Рупорная пара / пьезокаскад"), "kind": "actuator", "assigned_module": "turret", "power_profile": "TPA3116D2 channel output", "pinout": "audio amp output TBD", "tolerance": "volume and frequency profile", "operating_modes": "tone, sweep, deterrence", "state": "not_detected"},
        {"id": "attack_audio_driver", "title": _localized("Attack audio driver", "Драйвер атакующего звука"), "kind": "controller", "assigned_module": "turret", "power_profile": "12V/24V amplifier rail", "pinout": "TPA3116D2 XH-M543 dual-channel board", "tolerance": "thermal and power budget verification", "operating_modes": "dual-channel attack contour", "state": "not_detected"},
        {"id": "voice_fx", "title": _localized("Soundcore Motion 300", "Soundcore Motion 300"), "kind": "actuator", "assigned_module": "turret", "power_profile": "Bluetooth / USB-C charging", "pinout": "wireless duplex audio path", "tolerance": "reconnect, battery, microphone health", "operating_modes": "voice playback, talkback, effects", "state": "not_detected"},
        {"id": "water_pump", "title": _localized("Water cannon pump", "Насос водной пушки"), "kind": "actuator", "assigned_module": "turret", "power_profile": "12V pump", "pinout": "relay/MOSFET TBD", "tolerance": "50-100%", "operating_modes": "short burst", "state": "not_detected"},
        {"id": "servo_pan_tilt", "title": _localized("Pan/tilt servos", "Сервоприводы наведения"), "kind": "actuator", "assigned_module": "turret", "power_profile": "5-6V", "pinout": "PWM TBD", "tolerance": "angle limits TBD", "operating_modes": "manual aim", "state": "not_detected"},
        {"id": "lidar", "title": _localized("Lidar / range sensor", "Лидар / дальномер"), "kind": "sensor", "assigned_module": "turret", "power_profile": "5V UART/I2C", "pinout": "TBD", "tolerance": "range sanity", "operating_modes": "distance gate", "state": "not_detected"},
        {"id": "soil_moisture", "title": _localized("Soil moisture sensor", "Датчик влажности почвы"), "kind": "sensor", "assigned_module": "irrigation", "power_profile": "3.3V ADC", "pinout": "ESP32 ADC TBD", "tolerance": "calibration required", "operating_modes": "sample, average", "state": "not_detected"},
        {"id": "air_temp_humidity", "title": _localized("Air temp/humidity", "Температура и влажность воздуха"), "kind": "sensor", "assigned_module": "irrigation", "power_profile": "3.3V I2C/1-wire", "pinout": "TBD", "tolerance": "sensor health", "operating_modes": "sample", "state": "not_detected"},
        {"id": "drip_valves", "title": _localized("Drip valves", "Клапаны капельного полива"), "kind": "actuator", "assigned_module": "irrigation", "power_profile": "12V valves", "pinout": "relay board TBD", "tolerance": "zone timeout", "operating_modes": "zone open/close", "state": "not_detected"},
        {"id": "peristaltic_pump", "title": _localized("Peristaltic pump", "Перистальтический насос"), "kind": "actuator", "assigned_module": "irrigation", "power_profile": "12V pump", "pinout": "MOSFET TBD", "tolerance": "dose duration", "operating_modes": "dose", "state": "not_detected"},
        {"id": "light_sensor", "title": _localized("Light sensor", "Датчик освещённости"), "kind": "sensor", "assigned_module": "irrigation", "power_profile": "3.3V I2C/ADC", "pinout": "TBD", "tolerance": "day/night threshold", "operating_modes": "sample", "state": "not_detected"},
        {"id": "solar_panel", "title": _localized("Solar panel", "Солнечная панель"), "kind": "power", "assigned_module": "power", "power_profile": "input", "pinout": "charge controller", "tolerance": "voltage/current limits", "operating_modes": "charge", "state": "not_detected"},
        {"id": "converter", "title": _localized("DC/DC converter", "DC/DC конвертер"), "kind": "power", "assigned_module": "power", "power_profile": "5V/12V rails", "pinout": "power rail", "tolerance": "rail stability", "operating_modes": "supply", "state": "not_detected"},
        {"id": "battery_monitor", "title": _localized("Battery monitor", "Монитор батареи"), "kind": "sensor", "assigned_module": "power", "power_profile": "I2C/ADC", "pinout": "TBD", "tolerance": "voltage sanity", "operating_modes": "sample", "state": "not_detected"},
        {"id": "cat_feeder_servo", "title": _localized("Servo dispenser", "Сервопривод дозатора"), "kind": "actuator", "assigned_module": "cat_feeder", "power_profile": "5-6V", "pinout": "PWM TBD", "tolerance": "portion angle limits", "operating_modes": "dispense, calibrate", "state": "simulated"},
        {"id": "cat_feeder_motion_sensor", "title": _localized("Motion sensor", "Датчик движения"), "kind": "sensor", "assigned_module": "cat_feeder", "power_profile": "3.3V / GPIO", "pinout": "PIR GPIO TBD", "tolerance": "wake debounce", "operating_modes": "wake camera, notify owner", "state": "simulated"},
        {"id": "cat_feeder_camera", "title": _localized("Identification camera", "Камера идентификации"), "kind": "sensor", "assigned_module": "cat_feeder", "power_profile": "5V / CSI or USB", "pinout": "camera input TBD", "tolerance": "video identification confidence", "operating_modes": "identify cat, record request", "state": "simulated"},
    ],
    "assignments": [],
    "templates": {
        "modules": [
            {
                "id": "cat_feeder",
                "title": _localized("Cat Feeder", "Кормушка для кота"),
                "summary": _localized("Motion-triggered feeder with camera identification.", "Кормушка с пробуждением по движению и идентификацией по камере."),
                "owner_role": "compute_node",
            },
            {
                "id": "turret",
                "title": _localized("Turret", "Турель"),
                "summary": _localized("Camera-guided observation and deterrence.", "Наблюдение и безопасное воздействие с наведением."),
                "owner_role": "compute_node",
            },
            {
                "id": "irrigation",
                "title": _localized("Irrigation", "Ирригация"),
                "summary": _localized("Plant-aware watering module.", "Модуль полива с библиотекой растений."),
                "owner_role": "io_node",
            },
        ],
        "components": [
            {
                "id": "servo_dispenser",
                "title": _localized("Servo dispenser", "Сервопривод дозатора"),
                "kind": "actuator",
                "power_profile": "5-6V",
                "pinout": "PWM TBD",
                "tolerance": "portion angle limits",
                "operating_modes": "dispense, calibrate",
            },
            {
                "id": "motion_sensor",
                "title": _localized("Motion sensor", "Датчик движения"),
                "kind": "sensor",
                "power_profile": "3.3V / GPIO",
                "pinout": "PIR GPIO TBD",
                "tolerance": "wake debounce",
                "operating_modes": "wake camera, notify owner",
            },
            {
                "id": "identification_camera",
                "title": _localized("Identification camera", "Камера идентификации"),
                "kind": "sensor",
                "power_profile": "5V / CSI or USB",
                "pinout": "camera input TBD",
                "tolerance": "video identification confidence",
                "operating_modes": "identify cat, record request",
            },
        ],
    },
}


def _slug(value: str, fallback: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower())
    text = re.sub(r"_+", "_", text).strip("_")
    return text or fallback


def _unique_id(base: str, existing: set[str]) -> str:
    candidate = base
    index = 2
    while candidate in existing:
        candidate = f"{base}_{index}"
        index += 1
    return candidate


def _as_localized(value: Any, fallback: str = "") -> dict[str, str]:
    if isinstance(value, dict):
        en = str(value.get("en") or value.get("ru") or fallback).strip()
        ru = str(value.get("ru") or value.get("en") or fallback).strip()
        return {"en": en or fallback, "ru": ru or en or fallback}
    text = str(value or fallback).strip()
    return {"en": text, "ru": text}


def _component_assignment(component: dict[str, Any]) -> str:
    return str(component.get("assigned_module") or component.get("module") or "").strip()


def normalize_registry(raw: Any, *, updated_at_ms: int | None = None) -> dict[str, Any]:
    payload = copy.deepcopy(DEFAULT_REGISTRY)
    if isinstance(raw, dict):
        payload.update({key: copy.deepcopy(value) for key, value in raw.items() if key in {"modules", "components", "assignments", "templates"}})
        payload["updated_at_ms"] = int(raw.get("updated_at_ms") or 0)

    modules: list[dict[str, Any]] = []
    seen_modules: set[str] = set()
    for item in payload.get("modules", []):
        if not isinstance(item, dict):
            continue
        module_id = _slug(str(item.get("id") or item.get("title") or ""), "module")
        if module_id in seen_modules:
            continue
        seen_modules.add(module_id)
        modules.append(
            {
                "id": module_id,
                "title": _as_localized(item.get("title"), module_id),
                "summary": _as_localized(item.get("summary"), ""),
                "owner_role": str(item.get("owner_role") or item.get("owner") or "shared").strip() or "shared",
                "runtime_module_id": str(item.get("runtime_module_id") or "").strip(),
                "state": str(item.get("state") or "disconnected").strip(),
                "component_ids": [str(value).strip() for value in item.get("component_ids", []) if str(value).strip()],
            }
        )

    components: list[dict[str, Any]] = []
    seen_components: set[str] = set()
    for item in payload.get("components", []):
        if not isinstance(item, dict):
            continue
        component_id = _slug(str(item.get("id") or item.get("title") or ""), "component")
        if component_id in seen_components:
            continue
        seen_components.add(component_id)
        assigned_module = _slug(_component_assignment(item), "")
        components.append(
            {
                "id": component_id,
                "title": _as_localized(item.get("title"), component_id),
                "kind": str(item.get("kind") or "sensor").strip() or "sensor",
                "assigned_module": assigned_module,
                "power_profile": str(item.get("power_profile") or item.get("power") or "TBD").strip(),
                "pinout": str(item.get("pinout") or "TBD").strip(),
                "tolerance": str(item.get("tolerance") or "verification pending").strip(),
                "operating_modes": str(item.get("operating_modes") or item.get("modes") or "sample").strip(),
                "state": str(item.get("state") or "not_detected").strip(),
            }
        )

    assignments: list[dict[str, Any]] = []
    seen_assignments: set[tuple[str, str]] = set()
    for item in payload.get("assignments", []):
        if not isinstance(item, dict):
            continue
        module_id = _slug(str(item.get("module_id") or ""), "")
        component_id = _slug(str(item.get("component_id") or ""), "")
        if not module_id or not component_id or (module_id, component_id) in seen_assignments:
            continue
        seen_assignments.add((module_id, component_id))
        assignments.append(
            {
                "id": str(item.get("id") or f"{module_id}_{component_id}").strip(),
                "module_id": module_id,
                "component_id": component_id,
                "role": str(item.get("role") or "member").strip(),
            }
        )

    for component in components:
        module_id = _component_assignment(component)
        if not module_id:
            continue
        key = (module_id, component["id"])
        if key in seen_assignments:
            continue
        seen_assignments.add(key)
        assignments.append(
            {
                "id": f"{module_id}_{component['id']}",
                "module_id": module_id,
                "component_id": component["id"],
                "role": component["kind"],
            }
        )

    component_ids_by_module: dict[str, list[str]] = {}
    for assignment in assignments:
        component_ids_by_module.setdefault(assignment["module_id"], []).append(assignment["component_id"])
    for module in modules:
        merged: list[str] = []
        for component_id in [*module.get("component_ids", []), *component_ids_by_module.get(module["id"], [])]:
            if component_id and component_id not in merged:
                merged.append(component_id)
        module["component_ids"] = merged

    templates = payload.get("templates") if isinstance(payload.get("templates"), dict) else DEFAULT_REGISTRY["templates"]
    return {
        "schema_version": SCHEMA_VERSION,
        "updated_at_ms": int(updated_at_ms if updated_at_ms is not None else payload.get("updated_at_ms") or 0),
        "modules": modules,
        "components": components,
        "assignments": assignments,
        "templates": templates,
    }


class PlatformRegistryStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._lock = Lock()

    def load(self) -> dict[str, Any]:
        with self._lock:
            payload: Any = {}
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                payload = {}
            except (OSError, json.JSONDecodeError):
                payload = {}
            registry = normalize_registry(payload)
            if not self.path.exists() or payload != registry:
                registry["updated_at_ms"] = registry.get("updated_at_ms") or _now_ms()
                self._write_unlocked(registry)
            return registry

    def upsert_constructor_draft(self, draft: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(draft, dict):
            raise ValueError("constructor draft must be a JSON object")
        with self._lock:
            registry = normalize_registry(self._read_unlocked())
            module_name = str(draft.get("moduleName") or draft.get("module_name") or "Custom module").strip()
            component_name = str(draft.get("componentName") or draft.get("component_name") or "Custom component").strip()
            module_id = _slug(str(draft.get("moduleId") or draft.get("module_id") or module_name), "module")
            component_id_base = _slug(str(draft.get("componentId") or draft.get("component_id") or component_name), "component")
            module_by_id = {item["id"]: item for item in registry["modules"]}
            component_ids = {item["id"] for item in registry["components"]}

            if module_id not in module_by_id:
                registry["modules"].append(
                    {
                        "id": module_id,
                        "title": _as_localized(draft.get("moduleTitle") or module_name, module_name),
                        "summary": _as_localized(draft.get("moduleSummary") or "", ""),
                        "owner_role": str(draft.get("controllerNode") or draft.get("owner_role") or "shared").strip() or "shared",
                        "runtime_module_id": "",
                        "state": "simulated",
                        "component_ids": [],
                    }
                )
                module_by_id[module_id] = registry["modules"][-1]
            else:
                module_by_id[module_id]["owner_role"] = str(draft.get("controllerNode") or module_by_id[module_id].get("owner_role") or "shared").strip() or "shared"

            component_id = component_id_base if component_id_base in component_ids else _unique_id(component_id_base, component_ids)
            component = {
                "id": component_id,
                "title": _as_localized(draft.get("componentTitle") or component_name, component_name),
                "kind": str(draft.get("componentKind") or draft.get("kind") or "sensor").strip() or "sensor",
                "assigned_module": module_id,
                "power_profile": str(draft.get("powerProfile") or draft.get("power_profile") or "TBD").strip() or "TBD",
                "pinout": str(draft.get("pinout") or "TBD").strip() or "TBD",
                "tolerance": str(draft.get("tolerance") or "verification pending").strip() or "verification pending",
                "operating_modes": str(draft.get("operatingModes") or draft.get("operating_modes") or "sample").strip() or "sample",
                "state": "simulated",
            }
            if component_id in component_ids:
                registry["components"] = [component if item["id"] == component_id else item for item in registry["components"]]
            else:
                registry["components"].append(component)

            if component_id not in module_by_id[module_id].setdefault("component_ids", []):
                module_by_id[module_id]["component_ids"].append(component_id)

            assignment_key = (module_id, component_id)
            existing_assignments = {(item["module_id"], item["component_id"]) for item in registry["assignments"]}
            if assignment_key not in existing_assignments:
                registry["assignments"].append(
                    {
                        "id": f"{module_id}_{component_id}",
                        "module_id": module_id,
                        "component_id": component_id,
                        "role": component["kind"],
                    }
                )

            registry = normalize_registry(registry, updated_at_ms=_now_ms())
            self._write_unlocked(registry)
            return {
                "command": "platform_registry_constructor_save",
                "accepted": True,
                "module_id": module_id,
                "component_id": component_id,
                "registry": registry,
            }

    def _read_unlocked(self) -> Any:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_unlocked(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
