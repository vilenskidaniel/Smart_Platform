from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from settings_store import normalize_settings


class SettingsStoreTests(unittest.TestCase):
    def test_sync_poll_interval_is_normalized_and_auto_selects_all_domains(self) -> None:
        payload = normalize_settings(
            {
                "synchronization": {
                    "preferred_mode": "auto",
                    "prefer_peer_continuity": False,
                    "poll_interval_seconds": 999,
                    "selected_domains": {
                        "service_link": False,
                        "module_state": False,
                    },
                }
            }
        )

        self.assertFalse(payload["synchronization"]["prefer_peer_continuity"])
        self.assertEqual(300, payload["synchronization"]["poll_interval_seconds"])
        self.assertTrue(all(payload["synchronization"]["selected_domains"].values()))

    def test_sync_poll_interval_has_safe_default_and_minimum(self) -> None:
        default_payload = normalize_settings({})
        low_payload = normalize_settings({"synchronization": {"poll_interval_seconds": 1}})

        self.assertEqual(30, default_payload["synchronization"]["poll_interval_seconds"])
        self.assertEqual(5, low_payload["synchronization"]["poll_interval_seconds"])

    def test_component_field_options_accept_legacy_module_owner_alias(self) -> None:
        payload = normalize_settings(
            {
                "component_field_options": {
                    "module_owner": ["custom_module"],
                }
            }
        )

        self.assertEqual(["custom_module", "turret", "irrigation", "power"], payload["component_field_options"]["assigned_module"])
        self.assertEqual(["compute_node", "io_node", "shared"], payload["component_field_options"]["node_role"])

    def test_turret_recording_limit_is_clamped(self) -> None:
        default_payload = normalize_settings({})
        low_payload = normalize_settings({"turret_policies": {"max_recording_seconds": 1}})
        high_payload = normalize_settings({"turret_policies": {"max_recording_seconds": 99999}})

        self.assertEqual(30, default_payload["turret_policies"]["max_recording_seconds"])
        self.assertEqual(5, low_payload["turret_policies"]["max_recording_seconds"])
        self.assertEqual(36000, high_payload["turret_policies"]["max_recording_seconds"])

    def test_automatic_fpv_capture_policy_defaults_enabled(self) -> None:
        default_payload = normalize_settings({})
        disabled_payload = normalize_settings({"turret_policies": {"allow_auto_capture": False}})

        self.assertTrue(default_payload["turret_policies"]["allow_auto_capture"])
        self.assertFalse(disabled_payload["turret_policies"]["allow_auto_capture"])


if __name__ == "__main__":
    unittest.main()
