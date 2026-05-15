from __future__ import annotations

from copy import deepcopy
from typing import Any

from turret_driver_layer import TurretDriverLayer
from turret_event_log import TurretEventLog


class TurretRuntime:
    """Единая модель состояний турели на стороне Raspberry Pi.

    Этот слой пока не управляет реальным железом. Его задача на текущем этапе:
    - хранить понятное состояние подсистем турели;
    - применять базовые правила безопасности и приоритетов режимов;
    - писать события в журнал;
    - отдавать snapshot для shell, sync и будущего runtime-кода.
    """

    _VALID_MODES = {"manual", "automatic", "service_test", "fault", "emergency"}
    _VALID_INTERLOCKS = {"clear", "fault", "emergency"}
    _VALID_FLAGS = {"automation_ready", "target_locked", "vision_tracking"}
    _ACTUATOR_IDS = {"motion", "strobe", "water", "attack_audio", "voice_fx"}
    _AUTOMATION_ARM_REQUIRED_ACTUATORS = {"motion", "strobe", "water", "attack_audio"}
    _ENGAGEMENT_ACTUATOR_IDS = {"strobe", "water", "attack_audio"}

    def __init__(self, event_log: TurretEventLog, driver_layer: TurretDriverLayer) -> None:
        self._event_log = event_log
        self._driver_layer = driver_layer
        self._active_mode = "manual"
        self._service_session_active = False
        self._automation_ready = False
        self._target_locked = False
        self._vision_tracking = False
        self._emergency_latched = False
        self._fault_latched = False
        self._fault_reason = "none"
        self._subsystems = self._seed_subsystems()
        self._apply_rules()
        self._publish_runtime("runtime_initialized", "turret runtime initialized")

    @property
    def active_mode(self) -> str:
        return self._active_mode

    def _seed_subsystems(self) -> dict[str, dict[str, Any]]:
        return {
            "motion": self._subsystem("motion", "Motion", "actuator", "turret", False),
            "strobe": self._subsystem("strobe", "Strobe", "actuator", "turret", False),
            "water": self._subsystem("water", "Water Spray", "actuator", "turret", False),
            "attack_audio": self._subsystem(
                "attack_audio",
                "Attack Audio",
                "actuator",
                "attack_audio",
                False,
                profile_label="TPA3116D2 XH-M543",
                note="dual-channel directed contour for ultrasonic and horn attack scenarios",
                contour="attack_audio",
                channel_count=2,
                driver_profile="tpa3116d2_xh_m543",
                default_scenario_id="dual_channel_deterrence",
                channel_a_power_percent=60,
                channel_b_power_percent=60,
                load_groups=["ultrasonic_pair", "horn_pair"],
            ),
            "voice_fx": self._subsystem(
                "voice_fx",
                "Voice FX",
                "actuator",
                "voice_fx",
                False,
                simulated=True,
                profile_label="Soundcore Motion 300",
                note="bluetooth speaker and microphone path for talkback and effects",
                contour="voice_fx",
                transport="bluetooth",
                duplex="speaker_mic",
                device_name="Soundcore Motion 300",
                talkback_enabled=True,
                microphone_expected=True,
                effect_profile="natural",
            ),
            "camera": self._subsystem(
                "camera",
                "Primary Camera",
                "sensor",
                "camera",
                True,
                simulated=True,
                profile_label="IMX219",
                note="software-level camera availability profile",
            ),
            "range": self._subsystem(
                "range",
                "Primary Range",
                "sensor",
                "range",
                True,
                simulated=True,
                profile_label="TFmini Plus",
                note="software-level range availability profile",
            ),
            "vision": self._subsystem(
                "vision",
                "Vision Pipeline",
                "logic",
                "vision",
                True,
                simulated=True,
                profile_label="tracking baseline",
                note="logic-only tracking baseline without real camera stack",
            ),
        }

    def _subsystem(
        self,
        subsystem_id: str,
        title: str,
        kind: str,
        profile: str,
        enabled: bool,
        *,
        simulated: bool = False,
        profile_label: str = "",
        note: str = "",
        **extra: Any,
    ) -> dict[str, Any]:
        payload = {
            "id": subsystem_id,
            "title": title,
            "kind": kind,
            "profile": profile,
            "enabled": enabled,
            "state": "online",
            "block_reason": "none",
            "simulated": simulated,
            "profile_label": profile_label,
            "note": note,
        }
        payload.update(extra)
        return payload

    def apply_settings_profile(self, settings: dict[str, Any] | None) -> None:
        payload = settings if isinstance(settings, dict) else {}
        turret_audio = payload.get("turret_audio") if isinstance(payload.get("turret_audio"), dict) else {}
        attack_audio = turret_audio.get("attack_audio") if isinstance(turret_audio.get("attack_audio"), dict) else {}
        voice_fx = turret_audio.get("voice_fx") if isinstance(turret_audio.get("voice_fx"), dict) else {}

        attack_audio_state = self._subsystems["attack_audio"]
        voice_fx_state = self._subsystems["voice_fx"]

        driver_profile = str(attack_audio.get("driver_profile") or attack_audio_state.get("driver_profile") or "tpa3116d2_xh_m543")
        attack_audio_state["driver_profile"] = driver_profile
        attack_audio_state["profile_label"] = self._driver_profile_label(driver_profile)
        attack_audio_state["default_scenario_id"] = str(
            attack_audio.get("default_scenario_id") or attack_audio_state.get("default_scenario_id") or "dual_channel_deterrence"
        )
        attack_audio_state["channel_a_power_percent"] = self._clamp_percent(
            attack_audio.get("channel_a_power_percent"),
            int(attack_audio_state.get("channel_a_power_percent", 60) or 60),
        )
        attack_audio_state["channel_b_power_percent"] = self._clamp_percent(
            attack_audio.get("channel_b_power_percent"),
            int(attack_audio_state.get("channel_b_power_percent", 60) or 60),
        )

        device_name = str(voice_fx.get("device_name") or voice_fx_state.get("device_name") or "Soundcore Motion 300")
        voice_fx_state["device_name"] = device_name
        voice_fx_state["profile_label"] = device_name
        voice_fx_state["transport"] = str(voice_fx.get("transport") or voice_fx_state.get("transport") or "bluetooth")
        voice_fx_state["talkback_enabled"] = self._as_bool(
            voice_fx.get("talkback_enabled"),
            bool(voice_fx_state.get("talkback_enabled", True)),
        )
        voice_fx_state["microphone_expected"] = self._as_bool(
            voice_fx.get("microphone_expected"),
            bool(voice_fx_state.get("microphone_expected", True)),
        )
        voice_fx_state["effect_profile"] = str(voice_fx.get("effect_profile") or voice_fx_state.get("effect_profile") or "natural")

        self._apply_rules()

    def snapshot(self) -> dict[str, Any]:
        subsystems = [deepcopy(item) for item in self._subsystems.values()]
        return {
            "active_mode": self._active_mode,
            "service_session_active": self._service_session_active,
            "automation_ready": self._automation_ready,
            "target_locked": self._target_locked,
            "vision_tracking": self._vision_tracking,
            "interlocks": {
                "emergency_latched": self._emergency_latched,
                "fault_latched": self._fault_latched,
                "fault_reason": self._fault_reason,
            },
            "summary": {
                "active_subsystems": [item["id"] for item in subsystems if item["enabled"]],
                "actuator_count": len([item for item in subsystems if item["kind"] == "actuator"]),
                "has_blocked_subsystems": any(item["state"] == "locked" for item in subsystems),
                "camera_available": self._subsystems["camera"]["enabled"],
                "range_available": self._subsystems["range"]["enabled"],
                "attack_audio_ready": self._subsystems["attack_audio"]["block_reason"] == "none",
                "voice_fx_ready": self._subsystems["voice_fx"]["block_reason"] == "none",
                "automatic_engagement_ready": self._automatic_engagement_ready(),
            },
            "product_view": self._build_product_view(subsystems),
            "subsystems": subsystems,
        }

    def export_module_states(self) -> dict[str, dict[str, str]]:
        return {
            "turret_bridge": self._derive_turret_bridge_module(),
            "strobe": self._derive_strobe_module(),
        }

    def set_mode(self, mode: str) -> tuple[bool, str]:
        if mode not in self._VALID_MODES:
            self._event_log.add("warn", "runtime_mode_rejected", "unsupported mode requested", mode=mode)
            return False, "mode is not supported"

        if mode == "emergency":
            return self.set_interlock("emergency")

        if mode == "fault":
            return self.set_interlock("fault")

        if self._emergency_latched or self._fault_latched:
            self._event_log.add(
                "warn",
                "runtime_mode_rejected",
                "mode change rejected while interlock is latched",
                mode=mode,
                emergency_latched=self._emergency_latched,
                fault_latched=self._fault_latched,
            )
            return False, "clear interlock before switching mode"

        previous_mode = self._active_mode

        # При смене логического режима заранее снимаем исполнительные нагрузки.
        # Это упрощает переходы и не оставляет активные актуаторы в спорном состоянии.
        self._deactivate_actuators()
        self._active_mode = mode
        self._service_session_active = mode == "service_test"

        if mode != "automatic":
            self._automation_ready = False
            self._target_locked = False

        self._apply_rules()
        self._publish_runtime(
            "runtime_mode_changed",
            "turret mode changed",
            previous_mode=previous_mode,
            current_mode=mode,
        )
        return True, f"mode set to {mode}"

    def set_interlock(self, value: str) -> tuple[bool, str]:
        if value not in self._VALID_INTERLOCKS:
            self._event_log.add("warn", "runtime_interlock_rejected", "unsupported interlock requested", value=value)
            return False, "interlock value is not supported"

        if value == "clear":
            self._emergency_latched = False
            self._fault_latched = False
            self._fault_reason = "none"
            self._active_mode = "manual"
            self._service_session_active = False
            self._automation_ready = False
            self._target_locked = False
            self._vision_tracking = False
            self._deactivate_actuators()
            self._apply_rules()
            self._publish_runtime("runtime_interlock_cleared", "runtime interlocks cleared")
            return True, "interlocks cleared and mode returned to manual"

        if value == "emergency":
            self._emergency_latched = True
            self._fault_latched = False
            self._fault_reason = "emergency_state"
            self._active_mode = "emergency"
            self._service_session_active = False
            self._automation_ready = False
            self._target_locked = False
            self._vision_tracking = False
            self._deactivate_actuators()
            self._apply_rules()
            self._publish_runtime("runtime_emergency_latched", "emergency interlock latched")
            return True, "emergency interlock latched"

        self._fault_latched = True
        self._emergency_latched = False
        self._fault_reason = "module_fault"
        self._active_mode = "fault"
        self._service_session_active = False
        self._automation_ready = False
        self._target_locked = False
        self._vision_tracking = False
        self._deactivate_actuators()
        self._apply_rules()
        self._publish_runtime("runtime_fault_latched", "fault interlock latched")
        return True, "fault interlock latched"

    def set_flag(self, name: str, value: bool) -> tuple[bool, str]:
        if name not in self._VALID_FLAGS:
            self._event_log.add("warn", "runtime_flag_rejected", "unsupported flag requested", name=name, value=value)
            return False, "flag is not supported"

        if name == "automation_ready" and value and self._active_mode != "automatic":
            self._event_log.add(
                "warn",
                "runtime_flag_rejected",
                "automation_ready can be enabled only in automatic mode",
                name=name,
                mode=self._active_mode,
            )
            return False, "automation_ready can be enabled only in automatic mode"

        if name == "target_locked" and value and self._active_mode not in {"manual", "automatic"}:
            self._event_log.add(
                "warn",
                "runtime_flag_rejected",
                "target lock is available only in manual or automatic mode",
                name=name,
                mode=self._active_mode,
            )
            return False, "target lock is available only in manual or automatic mode"

        if name == "target_locked" and value and not self._camera_and_vision_ready():
            self._event_log.add(
                "warn",
                "runtime_flag_rejected",
                "camera and vision must be ready before target lock",
                name=name,
            )
            return False, "camera and vision must be ready before target lock"

        if name == "vision_tracking" and value and not self._camera_and_vision_ready():
            self._event_log.add(
                "warn",
                "runtime_flag_rejected",
                "camera and vision must be enabled before tracking",
                name=name,
            )
            return False, "camera and vision must be enabled before tracking"

        if name == "automation_ready":
            self._automation_ready = value
            if not value:
                self._target_locked = False
        elif name == "target_locked":
            self._target_locked = value
        elif name == "vision_tracking":
            self._vision_tracking = value

        self._apply_rules()
        self._publish_runtime("runtime_flag_changed", "runtime flag updated", name=name, value=value)
        return True, f"{name} updated"

    def set_subsystem_enabled(self, subsystem_id: str, enabled: bool) -> tuple[bool, str]:
        subsystem = self._subsystems.get(subsystem_id)
        if subsystem is None:
            self._event_log.add(
                "warn",
                "runtime_subsystem_rejected",
                "unknown subsystem requested",
                subsystem_id=subsystem_id,
                enabled=enabled,
            )
            return False, "subsystem is unknown"

        if subsystem_id == "vision" and enabled and not self._subsystems["camera"]["enabled"]:
            self._event_log.add(
                "warn",
                "runtime_subsystem_rejected",
                "vision pipeline requires camera availability",
                subsystem_id=subsystem_id,
            )
            return False, "vision pipeline requires camera availability"

        if subsystem_id in self._ACTUATOR_IDS and enabled:
            if self._emergency_latched:
                self._event_log.add(
                    "warn",
                    "runtime_subsystem_rejected",
                    "actuator is blocked by emergency interlock",
                    subsystem_id=subsystem_id,
                )
                return False, "actuators are blocked by emergency interlock"
            if self._fault_latched:
                self._event_log.add(
                    "warn",
                    "runtime_subsystem_rejected",
                    "actuator is blocked by fault interlock",
                    subsystem_id=subsystem_id,
                )
                return False, "actuators are blocked by fault interlock"
            if self._active_mode == "automatic" and subsystem_id in self._AUTOMATION_ARM_REQUIRED_ACTUATORS and not self._automation_ready:
                self._event_log.add(
                    "warn",
                    "runtime_subsystem_rejected",
                    "automatic mode is not armed yet",
                    subsystem_id=subsystem_id,
                )
                return False, "automatic mode is not armed yet"
            if self._active_mode == "automatic" and subsystem_id in self._ENGAGEMENT_ACTUATOR_IDS:
                sensor_gate_reason = self._automatic_sensor_gate_reason()
                if sensor_gate_reason != "none":
                    self._event_log.add(
                        "warn",
                        "runtime_subsystem_rejected",
                        "automatic sensing path is not ready",
                        subsystem_id=subsystem_id,
                        block_reason=sensor_gate_reason,
                    )
                    return False, "automatic sensing path is not ready"
                if not self._target_locked:
                    self._event_log.add(
                        "warn",
                        "runtime_subsystem_rejected",
                        "target must be locked before enabling subsystem in automatic mode",
                        subsystem_id=subsystem_id,
                    )
                    return False, "target must be locked before enabling this subsystem in automatic mode"

        subsystem["enabled"] = enabled

        if subsystem_id == "camera" and not enabled:
            self._vision_tracking = False
            self._target_locked = False
        elif subsystem_id == "range" and not enabled and self._active_mode == "automatic":
            self._target_locked = False
        elif subsystem_id == "vision" and not enabled:
            self._vision_tracking = False
            self._target_locked = False

        self._apply_rules()
        self._publish_runtime(
            "runtime_subsystem_changed",
            "subsystem state updated",
            subsystem_id=subsystem_id,
            enabled=enabled,
        )
        return True, f"{subsystem_id} updated"

    def _deactivate_actuators(self) -> None:
        for subsystem_id in self._ACTUATOR_IDS:
            self._subsystems[subsystem_id]["enabled"] = False

    def _camera_and_vision_ready(self) -> bool:
        return self._subsystems["camera"]["enabled"] and self._subsystems["vision"]["enabled"]

    def _automatic_sensor_gate_reason(self) -> str:
        if not self._subsystems["camera"]["enabled"]:
            return "camera_unavailable"
        if not self._subsystems["range"]["enabled"]:
            return "range_unavailable"
        if not self._subsystems["vision"]["enabled"]:
            return "vision_unavailable"
        return "none"

    def _automatic_engagement_ready(self) -> bool:
        return (
            self._active_mode == "automatic"
            and self._automation_ready
            and self._automatic_sensor_gate_reason() == "none"
            and self._target_locked
            and not self._fault_latched
            and not self._emergency_latched
        )

    def _apply_rules(self) -> None:
        if not self._camera_and_vision_ready():
            self._vision_tracking = False
            self._target_locked = False

        for subsystem in self._subsystems.values():
            subsystem["block_reason"] = "none"

            if subsystem["id"] in {"camera", "range"}:
                self._apply_sensor_rules(subsystem)
                continue

            if subsystem["id"] == "vision":
                self._apply_vision_rules(subsystem)
                continue

            self._apply_actuator_rules(subsystem)

    def _apply_actuator_rules(self, subsystem: dict[str, Any]) -> None:
        if self._emergency_latched:
            subsystem["enabled"] = False
            subsystem["state"] = "locked"
            subsystem["block_reason"] = "emergency_state"
            return

        if self._fault_latched:
            subsystem["enabled"] = False
            subsystem["state"] = "fault"
            subsystem["block_reason"] = self._fault_reason
            return

        if self._active_mode == "automatic" and subsystem["id"] in self._AUTOMATION_ARM_REQUIRED_ACTUATORS and not self._automation_ready:
            subsystem["enabled"] = False
            subsystem["state"] = "locked"
            subsystem["block_reason"] = "auto_not_ready"
            return

        if self._active_mode == "automatic" and subsystem["id"] in self._ENGAGEMENT_ACTUATOR_IDS:
            sensor_gate_reason = self._automatic_sensor_gate_reason()
            if sensor_gate_reason != "none":
                subsystem["enabled"] = False
                subsystem["state"] = "locked"
                subsystem["block_reason"] = sensor_gate_reason
                return
            if subsystem["enabled"] and not self._target_locked:
                subsystem["enabled"] = False
                subsystem["state"] = "locked"
                subsystem["block_reason"] = "target_not_locked"
                return

        if subsystem["enabled"]:
            subsystem["state"] = "active"
            subsystem["block_reason"] = "none"
            return

        subsystem["state"] = "service" if self._active_mode == "service_test" else "online"

    def _apply_sensor_rules(self, subsystem: dict[str, Any]) -> None:
        if self._emergency_latched:
            subsystem["state"] = "locked"
            subsystem["block_reason"] = "emergency_state"
            return

        if self._fault_latched:
            subsystem["state"] = "degraded"
            subsystem["block_reason"] = self._fault_reason
            return

        if not subsystem["enabled"]:
            subsystem["state"] = "service" if self._active_mode == "service_test" else "degraded"
            subsystem["block_reason"] = "sensor_unavailable"
            return

        if subsystem["id"] == "camera":
            subsystem["state"] = "active" if (self._vision_tracking or self._target_locked) else "online"
        else:
            subsystem["state"] = "active" if self._target_locked else "online"
        subsystem["block_reason"] = "none"

    def _apply_vision_rules(self, subsystem: dict[str, Any]) -> None:
        if self._emergency_latched:
            subsystem["state"] = "locked"
            subsystem["block_reason"] = "emergency_state"
            return

        if self._fault_latched:
            subsystem["state"] = "degraded"
            subsystem["block_reason"] = self._fault_reason
            return

        if not subsystem["enabled"]:
            self._vision_tracking = False
            self._target_locked = False
            subsystem["state"] = "service" if self._active_mode == "service_test" else "degraded"
            subsystem["block_reason"] = "vision_unavailable"
            return

        if not self._subsystems["camera"]["enabled"]:
            self._vision_tracking = False
            self._target_locked = False
            subsystem["state"] = "degraded"
            subsystem["block_reason"] = "camera_unavailable"
            return

        if not self._subsystems["range"]["enabled"] and self._active_mode == "automatic":
            subsystem["state"] = "degraded"
            subsystem["block_reason"] = "range_unavailable"
            return

        subsystem["state"] = "active" if self._vision_tracking else "online"
        subsystem["block_reason"] = "none"

    def _product_reason_message(self, reason: str) -> str:
        messages = {
            "none": "No blocking reason is active.",
            "auto_not_ready": "Automatic defense is waiting for arming.",
            "camera_unavailable": "Primary camera path is unavailable.",
            "range_unavailable": "Primary range path is unavailable.",
            "vision_unavailable": "Vision pipeline is unavailable.",
            "target_search": "Automatic defense is still searching for target.",
            "target_not_locked": "Target must be locked before engagement.",
            "module_fault": "Fault interlock is latched.",
            "emergency_state": "Emergency interlock is latched.",
            "sensor_unavailable": "Sensor channel is intentionally unavailable.",
        }
        return messages.get(reason, reason.replace("_", " "))

    def _driver_profile_label(self, driver_profile: str) -> str:
        if driver_profile == "tpa3116d2_xh_m543":
            return "TPA3116D2 XH-M543"
        return driver_profile.replace("_", " ").strip() or "Unknown driver"

    def _clamp_percent(self, value: Any, fallback: int) -> int:
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            numeric = fallback
        return max(0, min(100, numeric))

    def _as_bool(self, value: Any, fallback: bool) -> bool:
        if value is None:
            return fallback
        return bool(value)

    def _module_state_summary(self, state: str, block_reason: str) -> str:
        if state in {"fault", "locked", "degraded"}:
            return self._product_reason_message(block_reason)
        if state == "service":
            return "Turret owner is isolated in service/test."
        if self._active_mode == "automatic":
            return "Automatic defense baseline is ready."
        return "Turret owner is ready for manual control."

    def _build_product_view(self, subsystems: list[dict[str, Any]]) -> dict[str, Any]:
        by_id = {item["id"]: item for item in subsystems}
        module_state = self._derive_turret_bridge_module()
        ready_actions = [
            subsystem_id
            for subsystem_id in self._ACTUATOR_IDS
            if by_id[subsystem_id]["state"] in {"online", "service", "active"} and by_id[subsystem_id]["block_reason"] == "none"
        ]
        return {
            "overview": {
                "state": module_state["state"],
                "block_reason": module_state["block_reason"],
                "summary": self._module_state_summary(module_state["state"], module_state["block_reason"]),
                "ready_actions": ready_actions,
                "camera_available": by_id["camera"]["enabled"],
                "range_available": by_id["range"]["enabled"],
            },
            "manual_console": self._manual_console_view(by_id),
            "automatic_defense": self._automatic_defense_view(by_id),
            "service_lane": self._service_lane_view(),
            "engagement": {
                "active_mode": self._active_mode,
                "automation_ready": self._automation_ready,
                "target_locked": self._target_locked,
                "vision_tracking": self._vision_tracking,
                "automatic_engagement_ready": self._automatic_engagement_ready(),
            },
            "sensing": [self._sensor_view(by_id[sensor_id]) for sensor_id in ("camera", "range", "vision")],
            "actions": [self._action_view(by_id[action_id]) for action_id in ("motion", "attack_audio", "strobe", "water", "voice_fx")],
            "audio": self._audio_view(by_id),
        }

    def _manual_console_view(self, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
        if self._emergency_latched:
            state = "locked"
            block_reason = "emergency_state"
        elif self._fault_latched:
            state = "fault"
            block_reason = self._fault_reason
        elif self._active_mode == "service_test":
            state = "service"
            block_reason = "none"
        elif self._active_mode == "manual":
            state = "active"
            block_reason = "none"
        else:
            state = "online"
            block_reason = "none"

        return {
            "state": state,
            "block_reason": block_reason,
            "operator_control_ready": state in {"online", "active"},
            "fpv_available": by_id["camera"]["enabled"],
            "range_available": by_id["range"]["enabled"],
            "summary": self._module_state_summary(state, block_reason),
        }

    def _automatic_defense_view(self, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
        if self._emergency_latched:
            state = "locked"
            block_reason = "emergency_state"
        elif self._fault_latched:
            state = "fault"
            block_reason = self._fault_reason
        elif self._active_mode == "service_test":
            state = "service"
            block_reason = "none"
        elif self._active_mode != "automatic":
            state = "online"
            block_reason = "none"
        elif not self._automation_ready:
            state = "degraded"
            block_reason = "auto_not_ready"
        elif self._automatic_sensor_gate_reason() != "none":
            state = "degraded"
            block_reason = self._automatic_sensor_gate_reason()
        elif not self._target_locked:
            state = "degraded"
            block_reason = "target_search"
        else:
            state = "active"
            block_reason = "none"

        return {
            "state": state,
            "block_reason": block_reason,
            "armed": self._automation_ready,
            "target_locked": self._target_locked,
            "camera_available": by_id["camera"]["enabled"],
            "range_available": by_id["range"]["enabled"],
            "summary": self._module_state_summary(state, block_reason),
        }

    def _service_lane_view(self) -> dict[str, Any]:
        if self._emergency_latched:
            state = "locked"
            block_reason = "emergency_state"
        elif self._fault_latched:
            state = "locked"
            block_reason = self._fault_reason
        elif self._service_session_active:
            state = "active"
            block_reason = "none"
        else:
            state = "online"
            block_reason = "none"

        return {
            "state": state,
            "block_reason": block_reason,
            "session_active": self._service_session_active,
            "summary": "Service/test lane is active." if self._service_session_active else self._module_state_summary(state, block_reason),
        }

    def _sensor_view(self, subsystem: dict[str, Any]) -> dict[str, Any]:
        summary = self._product_reason_message(subsystem["block_reason"])
        if subsystem["state"] in {"online", "active"}:
            summary = (
                f"{subsystem['title']} is available via simulated profile {subsystem['profile_label']}."
                if subsystem.get("simulated")
                else f"{subsystem['title']} is available."
            )
        elif subsystem["state"] == "service":
            summary = f"{subsystem['title']} is isolated for service/test work."

        view = {
            "id": subsystem["id"],
            "title": subsystem["title"],
            "state": subsystem["state"],
            "enabled": subsystem["enabled"],
            "block_reason": subsystem["block_reason"],
            "profile_label": subsystem.get("profile_label", ""),
            "simulated": subsystem.get("simulated", False),
            "summary": summary,
            "note": subsystem.get("note", ""),
        }
        if subsystem["id"] == "range":
            view["reading_mm"] = 1850 if subsystem["enabled"] and self._target_locked else 3200 if subsystem["enabled"] else None
        return view

    def _action_view(self, subsystem: dict[str, Any]) -> dict[str, Any]:
        ready = subsystem["state"] in {"online", "service", "active"} and subsystem["block_reason"] == "none"
        summary = self._product_reason_message(subsystem["block_reason"])
        if subsystem["state"] == "active":
            summary = f"{subsystem['title']} channel is active."
        elif ready:
            summary = f"{subsystem['title']} channel is idle and ready."
        view = {
            "id": subsystem["id"],
            "title": subsystem["title"],
            "state": subsystem["state"],
            "enabled": subsystem["enabled"],
            "ready": ready,
            "block_reason": subsystem["block_reason"],
            "summary": summary,
        }
        if subsystem["id"] == "attack_audio":
            view.update(
                {
                    "contour": "attack_audio",
                    "channel_count": int(subsystem.get("channel_count", 0) or 0),
                    "driver_profile": str(subsystem.get("driver_profile", "") or ""),
                    "default_scenario_id": str(subsystem.get("default_scenario_id", "") or ""),
                    "channel_a_power_percent": int(subsystem.get("channel_a_power_percent", 0) or 0),
                    "channel_b_power_percent": int(subsystem.get("channel_b_power_percent", 0) or 0),
                    "load_groups": list(subsystem.get("load_groups", [])),
                }
            )
        elif subsystem["id"] == "voice_fx":
            view.update(
                {
                    "contour": "voice_fx",
                    "transport": str(subsystem.get("transport", "") or ""),
                    "duplex": str(subsystem.get("duplex", "") or ""),
                    "device_name": str(subsystem.get("device_name", "") or ""),
                    "talkback_enabled": bool(subsystem.get("talkback_enabled", True)),
                    "microphone_expected": bool(subsystem.get("microphone_expected", False)),
                    "effect_profile": str(subsystem.get("effect_profile", "natural") or "natural"),
                }
            )
        return view

    def _audio_view(self, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
        attack = self._action_view(by_id["attack_audio"])
        voice = self._action_view(by_id["voice_fx"])

        if attack["state"] == "fault" or voice["state"] == "fault":
            state = "fault"
            block_reason = attack["block_reason"] if attack["state"] == "fault" else voice["block_reason"]
        elif attack["state"] == "locked" and voice["state"] == "locked":
            state = "locked"
            block_reason = attack["block_reason"] if attack["block_reason"] != "none" else voice["block_reason"]
        elif attack["state"] == "active" or voice["state"] == "active":
            state = "active"
            block_reason = "none"
        elif attack["ready"] or voice["ready"]:
            state = "online"
            block_reason = "none"
        else:
            state = "degraded"
            block_reason = attack["block_reason"] if attack["block_reason"] != "none" else voice["block_reason"]

        if voice["state"] == "active":
            summary = "Voice FX talkback/playback path is active."
        elif attack["state"] == "active":
            summary = "Attack audio contour is active."
        elif attack["ready"] and voice["ready"]:
            summary = "Attack audio and Voice FX contours are ready."
        elif voice["ready"]:
            summary = "Voice FX contour is ready."
        elif attack["ready"]:
            summary = "Attack audio contour is ready."
        else:
            summary = self._product_reason_message(block_reason)

        return {
            "state": state,
            "block_reason": block_reason,
            "summary": summary,
            "attack_audio": attack,
            "voice_fx": voice,
        }

    def _derive_turret_bridge_module(self) -> dict[str, str]:
        if self._emergency_latched:
            return {"state": "locked", "block_reason": "emergency_state"}

        if self._fault_latched:
            return {"state": "fault", "block_reason": self._fault_reason}

        if self._active_mode == "service_test":
            return {"state": "service", "block_reason": "none"}

        if self._active_mode == "automatic" and not self._automation_ready:
            return {"state": "degraded", "block_reason": "auto_not_ready"}

        if self._active_mode == "automatic" and not self._subsystems["camera"]["enabled"]:
            return {"state": "degraded", "block_reason": "camera_unavailable"}

        if self._active_mode == "automatic" and not self._subsystems["range"]["enabled"]:
            return {"state": "degraded", "block_reason": "range_unavailable"}

        if self._active_mode == "automatic" and not self._subsystems["vision"]["enabled"]:
            return {"state": "degraded", "block_reason": "vision_unavailable"}

        if self._active_mode == "automatic" and not self._target_locked:
            return {"state": "degraded", "block_reason": "target_search"}

        return {"state": "online", "block_reason": "none"}

    def _derive_strobe_module(self) -> dict[str, str]:
        strobe = self._subsystems["strobe"]

        if self._emergency_latched:
            return {"state": "locked", "block_reason": "emergency_state"}

        if self._fault_latched:
            return {"state": "fault", "block_reason": self._fault_reason}

        if self._active_mode == "service_test":
            return {"state": "service", "block_reason": "none"}

        if strobe["state"] in {"locked", "fault"}:
            return {"state": strobe["state"], "block_reason": strobe["block_reason"]}

        sensor_gate_reason = self._automatic_sensor_gate_reason()
        if self._active_mode == "automatic" and sensor_gate_reason != "none":
            return {"state": "degraded", "block_reason": sensor_gate_reason}

        if self._active_mode == "automatic" and not self._target_locked:
            return {"state": "degraded", "block_reason": "target_search"}

        return {"state": "online", "block_reason": "none"}

    def _publish_runtime(self, event_type: str, message: str, **details: Any) -> None:
        snapshot = self.snapshot()
        self._event_log.add(
            "info",
            event_type,
            message,
            active_mode=snapshot["active_mode"],
            active_subsystems=snapshot["summary"]["active_subsystems"],
            **details,
        )
        self._driver_layer.apply_runtime(snapshot, reason=event_type)
