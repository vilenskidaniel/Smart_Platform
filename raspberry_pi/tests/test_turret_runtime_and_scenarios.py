from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge_state import BridgeState
from platform_event_log import PlatformEventLog
from turret_driver_layer import TurretDriverLayer
from turret_event_log import TurretEventLog
from turret_runtime import TurretRuntime
from turret_service_scenarios import TurretServiceScenarioRunner


class TurretRuntimeScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.platform_log = PlatformEventLog("rpi-turret")
        self.turret_log = TurretEventLog(
            forward_sink=lambda entry: self.platform_log.add(
                "turret_runtime",
                entry["level"],
                entry["type"],
                entry["message"],
                **entry["details"],
            )
        )
        self.driver_layer = TurretDriverLayer(self.turret_log)
        self.runtime = TurretRuntime(self.turret_log, self.driver_layer)
        self.scenarios = TurretServiceScenarioRunner(self.runtime, self.platform_log)

    def test_automatic_strobe_requires_target_lock_and_range(self) -> None:
        accepted, _ = self.runtime.set_interlock("clear")
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_mode("automatic")
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_flag("automation_ready", True)
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_subsystem_enabled("range", False)
        self.assertTrue(accepted)

        accepted, message = self.runtime.set_subsystem_enabled("strobe", True)
        self.assertFalse(accepted)
        self.assertIn("sensing", message)

        accepted, _ = self.runtime.set_subsystem_enabled("range", True)
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_flag("target_locked", True)
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_subsystem_enabled("strobe", True)
        self.assertTrue(accepted)

    def test_target_lock_requires_camera_and_vision(self) -> None:
        accepted, _ = self.runtime.set_mode("manual")
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_subsystem_enabled("camera", False)
        self.assertTrue(accepted)

        accepted, message = self.runtime.set_flag("target_locked", True)
        self.assertFalse(accepted)
        self.assertIn("camera and vision", message)

    def test_runtime_snapshot_contains_product_view(self) -> None:
        snapshot = self.runtime.snapshot()
        automatic = snapshot["product_view"]["automatic_defense"]
        sensing = {item["id"]: item for item in snapshot["product_view"]["sensing"]}

        self.assertEqual("active", snapshot["product_view"]["manual_console"]["state"])
        self.assertEqual("online", automatic["state"])
        self.assertTrue(sensing["camera"]["simulated"])
        self.assertTrue(sensing["range"]["enabled"])

    def test_emergency_locks_actuators(self) -> None:
        accepted, _ = self.runtime.set_mode("manual")
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_subsystem_enabled("motion", True)
        self.assertTrue(accepted)

        accepted, _ = self.runtime.set_interlock("emergency")
        self.assertTrue(accepted)

        snapshot = self.runtime.snapshot()
        motion = next(item for item in snapshot["subsystems"] if item["id"] == "motion")
        self.assertEqual("locked", motion["state"])
        self.assertFalse(motion["enabled"])

    def test_service_safe_idle_scenario_runs(self) -> None:
        result = self.scenarios.run("service_safe_idle")
        self.assertTrue(result["accepted"])
        self.assertEqual("service_test", result["runtime"]["active_mode"])

    def test_platform_log_receives_turret_events(self) -> None:
        self.runtime.set_mode("service_test")
        log_snapshot = self.platform_log.snapshot(limit=20)
        self.assertGreaterEqual(log_snapshot["count"], 1)
        self.assertTrue(any(entry["source"] == "turret_runtime" for entry in log_snapshot["entries"]))

    def test_remote_entries_are_deduplicated(self) -> None:
        first = self.platform_log.add_remote(
            "esp32-main",
            "esp32-00001",
            "sync_core",
            "info",
            "peer_heartbeat",
            "peer heartbeat accepted",
            "peer=rpi",
        )
        second = self.platform_log.add_remote(
            "esp32-main",
            "esp32-00001",
            "sync_core",
            "info",
            "peer_heartbeat",
            "peer heartbeat accepted",
            "peer=rpi",
        )
        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_bridge_state_reports_missing_peer_owner_for_irrigation(self) -> None:
        state = BridgeState(
            node_id="rpi-turret",
            shell_version="0.1.0",
            local_shell_base_url="http://raspberrypi.local:8080",
            peer_shell_base_url="http://192.168.4.1",
        )
        route = state.build_module_route_info("irrigation")
        self.assertTrue(route["module_found"])
        self.assertFalse(route["owner_available"])
        self.assertEqual("peer_owner_missing", route["federated_access"])

    def test_bridge_state_reports_peer_owner_url_after_snapshot(self) -> None:
        state = BridgeState(
            node_id="rpi-turret",
            shell_version="0.1.0",
            local_shell_base_url="http://raspberrypi.local:8080",
            peer_shell_base_url="http://192.168.4.1",
        )
        state.apply_esp32_snapshot(
            {
                "local_node": {
                    "node_id": "esp32-main",
                    "shell_base_url": "http://192.168.4.1",
                    "node_type": "esp32",
                    "reachable": True,
                    "shell_ready": True,
                    "wifi_ready": True,
                    "sync_ready": True,
                    "reported_mode": "manual",
                    "uptime_ms": 42,
                },
                "modules": [],
            }
        )
        route = state.build_module_route_info("irrigation")
        self.assertTrue(route["owner_available"])
        self.assertEqual("peer_owner_available", route["federated_access"])
        self.assertEqual("http://192.168.4.1/irrigation", route["canonical_url"])


if __name__ == "__main__":
    unittest.main()
