from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge_state import BridgeState
from shell_snapshot_facade import ShellSnapshotFacade


class ShellSnapshotFacadeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = BridgeState(
            node_id="rpi-turret",
            shell_version="0.1.0",
            local_shell_base_url="http://raspberrypi.local:8080",
            peer_shell_base_url="http://192.168.4.1",
        )
        self.facade = ShellSnapshotFacade(self.state, PROJECT_ROOT / "content")

    def test_snapshot_has_expected_top_level_sections(self) -> None:
        snapshot = self.facade.build_snapshot()

        self.assertEqual("shell-snapshot.v1", snapshot["schema_version"])
        self.assertIn("current_shell", snapshot)
        self.assertIn("nodes", snapshot)
        self.assertIn("module_cards", snapshot)
        self.assertIn("navigation", snapshot)
        self.assertIn("summaries", snapshot)
        self.assertEqual("raspberry_pi", snapshot["current_shell"]["node_type"])
        self.assertEqual("/gallery", snapshot["navigation"]["gallery"]["path"])
        self.assertEqual("reports", snapshot["navigation"]["gallery"]["default_tab"])
        self.assertEqual("/service", snapshot["navigation"]["laboratory"]["path"])
        self.assertEqual("Laboratory", snapshot["navigation"]["laboratory"]["user_facing_title"])
        self.assertEqual("/settings", snapshot["navigation"]["settings"])
        self.assertEqual("/service", snapshot["navigation"]["service"])
        self.assertEqual("/service", snapshot["navigation"]["service_test"]["path"])
        self.assertEqual("gallery.reports", snapshot["summaries"]["activity"]["primary_viewer"])

    def test_irrigation_card_is_blocked_without_peer_owner(self) -> None:
        snapshot = self.facade.build_snapshot()
        irrigation = next(card for card in snapshot["module_cards"] if card["id"] == "irrigation")
        irrigation_service = next(card for card in snapshot["module_cards"] if card["id"] == "irrigation_service")

        self.assertEqual("blocked", irrigation["route_mode"])
        self.assertFalse(irrigation["owner_available"])
        self.assertEqual("blocked", irrigation_service["route_mode"])
        self.assertFalse(irrigation_service["owner_available"])
        self.assertEqual("service_test", irrigation_service["product_block"])

    def test_irrigation_card_switches_to_handoff_when_peer_is_ready(self) -> None:
        self.state.apply_esp32_snapshot(
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

        snapshot = self.facade.build_snapshot()
        irrigation = next(card for card in snapshot["module_cards"] if card["id"] == "irrigation")
        irrigation_service = next(card for card in snapshot["module_cards"] if card["id"] == "irrigation_service")

        self.assertEqual("handoff", irrigation["route_mode"])
        self.assertTrue(irrigation["owner_available"])
        self.assertEqual("http://192.168.4.1/irrigation", irrigation["canonical_url"])
        self.assertEqual("handoff", irrigation_service["route_mode"])
        self.assertTrue(irrigation_service["owner_available"])
        self.assertEqual("http://192.168.4.1/service/irrigation", irrigation_service["canonical_url"])


if __name__ == "__main__":
    unittest.main()
