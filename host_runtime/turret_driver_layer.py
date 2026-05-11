from __future__ import annotations

from copy import deepcopy
from time import monotonic
from typing import Any

from turret_event_log import TurretEventLog


class TurretDriverLayer:
    """Каркас слоя драйверов турели.

    Пока здесь нет реальных GPIO, I2C, SPI или serial-драйверов. Вместо этого
    слой хранит будущее место подключения железа и показывает shell'у, какие
    подсистемы уже описаны, а какие пока работают через безопасную заглушку.
    """

    def __init__(self, event_log: TurretEventLog) -> None:
        self._event_log = event_log
        self._boot_time = monotonic()
        self._bindings = self._seed_bindings()
        self._last_runtime_mode = "manual"
        self._event_log.add(
            "info",
            "driver_layer_ready",
            "turret driver layer initialized in stub mode",
            subsystem_count=len(self._bindings),
        )

    def _timestamp_ms(self) -> int:
        return int((monotonic() - self._boot_time) * 1000)

    def _seed_bindings(self) -> dict[str, dict[str, Any]]:
        # Здесь намеренно только заглушки. Когда появится точная аппаратная карта,
        # мы заменим driver_kind и binding_state на реальные адаптеры.
        return {
            "motion": self._binding("motion", "Motion", "stub", "unbound", False, "awaiting motor driver map"),
            "strobe": self._binding("strobe", "Strobe", "stub", "unbound", False, "awaiting turret strobe wiring"),
            "water": self._binding("water", "Water Spray", "stub", "unbound", False, "awaiting pump/valve wiring"),
            "audio": self._binding("audio", "Piezo Audio", "stub", "unbound", False, "awaiting audio driver details"),
            "camera": self._binding("camera", "Primary Camera", "stub", "virtual", False, "simulated IMX219 profile"),
            "range": self._binding("range", "Primary Range", "stub", "virtual", False, "simulated TFmini Plus profile"),
            "vision": self._binding("vision", "Vision Pipeline", "stub", "virtual", True, "logic-only runtime placeholder"),
        }

    def _binding(
        self,
        subsystem_id: str,
        title: str,
        driver_kind: str,
        binding_state: str,
        hardware_ready: bool,
        note: str,
    ) -> dict[str, Any]:
        return {
            "id": subsystem_id,
            "title": title,
            "driver_kind": driver_kind,
            "binding_state": binding_state,
            "hardware_ready": hardware_ready,
            "last_apply_ms": 0,
            "last_enabled": False,
            "last_runtime_state": "unknown",
            "last_result": "not_applied",
            "note": note,
        }

    def describe_bindings(self) -> dict[str, Any]:
        return {
            "count": len(self._bindings),
            "bindings": [deepcopy(item) for item in self._bindings.values()],
        }

    def apply_runtime(self, runtime_snapshot: dict[str, Any], reason: str) -> None:
        mode = str(runtime_snapshot.get("active_mode", "manual"))
        if mode != self._last_runtime_mode:
            self._event_log.add(
                "info",
                "driver_runtime_mode_seen",
                "driver layer observed runtime mode change",
                previous_mode=self._last_runtime_mode,
                current_mode=mode,
                reason=reason,
            )
            self._last_runtime_mode = mode

        for subsystem in runtime_snapshot.get("subsystems", []):
            subsystem_id = subsystem.get("id")
            if subsystem_id not in self._bindings:
                continue

            binding = self._bindings[subsystem_id]
            enabled = bool(subsystem.get("enabled", False))
            runtime_state = str(subsystem.get("state", "unknown"))
            previous_enabled = binding["last_enabled"]
            previous_state = binding["last_runtime_state"]

            if previous_enabled == enabled and previous_state == runtime_state:
                continue

            binding["last_apply_ms"] = self._timestamp_ms()
            binding["last_enabled"] = enabled
            binding["last_runtime_state"] = runtime_state

            if binding["binding_state"] in {"unbound", "virtual"}:
                binding["last_result"] = "deferred"
                self._event_log.add(
                    "info",
                    "driver_stub_apply",
                    "runtime change stored without real hardware apply",
                    subsystem_id=subsystem_id,
                    enabled=enabled,
                    runtime_state=runtime_state,
                    reason=reason,
                    binding_state=binding["binding_state"],
                )
                continue

            # Заглушка для будущих реальных драйверов.
            # Когда появятся схемы и карта компонентов, сюда подключится фактический apply.
            binding["last_result"] = "accepted"
            self._event_log.add(
                "info",
                "driver_apply",
                "runtime change accepted by hardware binding",
                subsystem_id=subsystem_id,
                enabled=enabled,
                runtime_state=runtime_state,
                reason=reason,
            )
