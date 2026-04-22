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
        self.assertTrue(snapshot["nodes"]["current"]["shell_ready"])
        self.assertTrue(snapshot["nodes"]["current"]["wifi_ready"])
        self.assertTrue(snapshot["nodes"]["current"]["sync_ready"])

    def test_snapshot_can_include_runtime_profile_and_viewers(self) -> None:
        facade = ShellSnapshotFacade(
            self.state,
            PROJECT_ROOT / "content",
            runtime_profile="desktop_smoke",
            viewer_provider=lambda: [
                {
                    "viewer_id": "viewer-phone",
                    "viewer_kind": "phone",
                    "title": "Phone",
                    "value": "PH",
                    "page": "/",
                    "address": "192.168.1.52",
                },
                {
                    "viewer_id": "viewer-desktop",
                    "viewer_kind": "desktop",
                    "title": "Desktop",
                    "value": "PC",
                    "page": "/",
                    "address": "192.168.1.227",
                },
            ],
        )

        snapshot = facade.build_snapshot()

        self.assertEqual("desktop_smoke", snapshot["current_shell"]["runtime_profile"])
        self.assertEqual(2, len(snapshot["viewers"]))
        self.assertEqual("phone", snapshot["viewers"][0]["viewer_kind"])
        self.assertEqual("desktop", snapshot["viewers"][1]["viewer_kind"])

    def test_irrigation_card_is_blocked_without_peer_owner(self) -> None:
        snapshot = self.facade.build_snapshot()
        irrigation = next(card for card in snapshot["module_cards"] if card["id"] == "irrigation")
        irrigation_service = next(card for card in snapshot["module_cards"] if card["id"] == "irrigation_service")

        self.assertEqual("blocked", irrigation["route_mode"])
        self.assertFalse(irrigation["owner_available"])
        self.assertEqual("blocked", irrigation_service["route_mode"])
        self.assertFalse(irrigation_service["owner_available"])
        self.assertEqual("service_test", irrigation_service["product_block"])
        self.assertFalse(snapshot["nodes"]["peer"]["shell_ready"])
        self.assertFalse(snapshot["nodes"]["peer"]["wifi_ready"])

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
        self.assertTrue(snapshot["nodes"]["peer"]["shell_ready"])
        self.assertTrue(snapshot["nodes"]["peer"]["wifi_ready"])
        self.assertTrue(snapshot["nodes"]["peer"]["sync_ready"])


if __name__ == "__main__":
    unittest.main()
