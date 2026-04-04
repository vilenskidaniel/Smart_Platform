from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from platform_event_log import PlatformEventLog
from turret_runtime import TurretRuntime


class TurretServiceScenarioRunner:
    """Каталог и запуск dry-run service сценариев для турели.

    Сценарии пока не касаются реального железа. Они нужны, чтобы:
    - тестировщики могли гонять типовые проверки из web UI;
    - мы проверяли режимы и interlock без ручной последовательности кликов;
    - позже можно было заменить шаги на реальные driver actions.
    """

    def __init__(self, runtime: TurretRuntime, platform_log: PlatformEventLog) -> None:
        self._runtime = runtime
        self._platform_log = platform_log
        self._catalog = self._build_catalog()

    def _build_catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "service_safe_idle",
                "title": "Service Safe Idle",
                "category": "service",
                "description": "Переводит turret runtime в безопасный сервисный idle и очищает interlock.",
            },
            {
                "id": "auto_target_gate_probe",
                "title": "Auto Target Gate Probe",
                "category": "diagnostic",
                "description": "Проверяет, что automatic не включает strobe до arm, sensing-ready и target lock.",
            },
            {
                "id": "emergency_recovery_probe",
                "title": "Emergency Recovery Probe",
                "category": "diagnostic",
                "description": "Проверяет, что emergency снимает актуаторы и после clear возвращает runtime в manual.",
            },
        ]

    def list_scenarios(self) -> dict[str, Any]:
        return {"count": len(self._catalog), "scenarios": deepcopy(self._catalog)}

    def run(self, scenario_id: str) -> dict[str, Any]:
        scenario = next((item for item in self._catalog if item["id"] == scenario_id), None)
        if scenario is None:
            self._platform_log.add(
                "turret_scenarios",
                "warn",
                "scenario_rejected",
                "unknown turret scenario requested",
                scenario_id=scenario_id,
            )
            return {
                "accepted": False,
                "message": "scenario is unknown",
                "scenario_id": scenario_id,
                "steps": [],
            }

        self._platform_log.add(
            "turret_scenarios",
            "info",
            "scenario_started",
            "turret service scenario started",
            scenario_id=scenario_id,
        )

        steps: list[dict[str, Any]] = []
        if scenario_id == "service_safe_idle":
            self._scenario_service_safe_idle(steps)
        elif scenario_id == "auto_target_gate_probe":
            self._scenario_auto_target_gate_probe(steps)
        elif scenario_id == "emergency_recovery_probe":
            self._scenario_emergency_recovery_probe(steps)

        accepted = all(step["passed"] for step in steps)
        result = {
            "accepted": accepted,
            "message": "scenario completed" if accepted else "scenario completed with failed expectations",
            "scenario_id": scenario_id,
            "runtime": self._runtime.snapshot(),
            "steps": steps,
        }

        self._platform_log.add(
            "turret_scenarios",
            "info" if accepted else "warn",
            "scenario_finished",
            "turret service scenario finished",
            scenario_id=scenario_id,
            accepted=accepted,
            failed_steps=[step["id"] for step in steps if not step["passed"]],
        )
        return result

    def _scenario_service_safe_idle(self, steps: list[dict[str, Any]]) -> None:
        self._step(steps, "clear_interlock", "Clear interlock", self._runtime.set_interlock, "clear", expected=True)
        self._step(steps, "mode_service", "Switch to service_test", self._runtime.set_mode, "service_test", expected=True)
        self._step(steps, "disable_motion", "Disable motion", self._runtime.set_subsystem_enabled, "motion", False, expected=True)
        self._step(steps, "disable_strobe", "Disable strobe", self._runtime.set_subsystem_enabled, "strobe", False, expected=True)
        self._step(steps, "disable_water", "Disable water", self._runtime.set_subsystem_enabled, "water", False, expected=True)
        self._step(steps, "disable_audio", "Disable audio", self._runtime.set_subsystem_enabled, "audio", False, expected=True)
        self._step(steps, "enable_vision", "Enable vision", self._runtime.set_subsystem_enabled, "vision", True, expected=True)
        self._step(steps, "stop_tracking", "Disable vision tracking", self._runtime.set_flag, "vision_tracking", False, expected=True)

    def _scenario_auto_target_gate_probe(self, steps: list[dict[str, Any]]) -> None:
        self._step(steps, "clear_interlock", "Clear interlock", self._runtime.set_interlock, "clear", expected=True)
        self._step(steps, "mode_auto", "Switch to automatic", self._runtime.set_mode, "automatic", expected=True)
        self._step(
            steps,
            "enable_strobe_without_arm",
            "Try enabling strobe before automation_ready",
            self._runtime.set_subsystem_enabled,
            "strobe",
            True,
            expected=False,
        )
        self._step(
            steps,
            "arm_automatic",
            "Enable automation_ready",
            self._runtime.set_flag,
            "automation_ready",
            True,
            expected=True,
        )
        self._step(
            steps,
            "disable_range",
            "Disable primary range",
            self._runtime.set_subsystem_enabled,
            "range",
            False,
            expected=True,
        )
        self._step(
            steps,
            "enable_strobe_without_range",
            "Try enabling strobe while range is unavailable",
            self._runtime.set_subsystem_enabled,
            "strobe",
            True,
            expected=False,
        )
        self._step(
            steps,
            "restore_range",
            "Restore primary range",
            self._runtime.set_subsystem_enabled,
            "range",
            True,
            expected=True,
        )
        self._step(
            steps,
            "enable_strobe_without_target",
            "Try enabling strobe before target lock",
            self._runtime.set_subsystem_enabled,
            "strobe",
            True,
            expected=False,
        )
        self._step(
            steps,
            "set_target_lock",
            "Enable target lock",
            self._runtime.set_flag,
            "target_locked",
            True,
            expected=True,
        )
        self._step(
            steps,
            "enable_strobe_after_target",
            "Enable strobe after target lock",
            self._runtime.set_subsystem_enabled,
            "strobe",
            True,
            expected=True,
        )

    def _scenario_emergency_recovery_probe(self, steps: list[dict[str, Any]]) -> None:
        self._step(steps, "clear_interlock", "Clear interlock", self._runtime.set_interlock, "clear", expected=True)
        self._step(steps, "mode_manual", "Switch to manual", self._runtime.set_mode, "manual", expected=True)
        self._step(steps, "enable_motion", "Enable motion", self._runtime.set_subsystem_enabled, "motion", True, expected=True)
        self._step(steps, "emergency", "Latch emergency", self._runtime.set_interlock, "emergency", expected=True)
        self._step(
            steps,
            "enable_motion_under_emergency",
            "Try enabling motion under emergency",
            self._runtime.set_subsystem_enabled,
            "motion",
            True,
            expected=False,
        )
        self._step(steps, "clear_after_emergency", "Clear emergency", self._runtime.set_interlock, "clear", expected=True)

    def _step(
        self,
        steps: list[dict[str, Any]],
        step_id: str,
        title: str,
        fn: Callable[..., tuple[bool, str]],
        *args: Any,
        expected: bool,
    ) -> None:
        accepted, message = fn(*args)
        steps.append(
            {
                "id": step_id,
                "title": title,
                "expected": expected,
                "accepted": accepted,
                "passed": accepted == expected,
                "message": message,
            }
        )
