from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from report_feed import build_reports_snapshot


class ReportFeedTests(unittest.TestCase):
    def test_reports_snapshot_maps_scenario_entries(self) -> None:
        snapshot = build_reports_snapshot(
            {
                "count": 2,
                "entries": [
                    {
                        "event_id": "platform-00002",
                        "timestamp_ms": 1200,
                        "origin_node": "rpi-turret",
                        "mirrored": False,
                        "source": "turret_scenarios",
                        "level": "info",
                        "type": "scenario_finished",
                        "message": "turret service scenario finished",
                        "details": {
                            "scenario_id": "service_safe_idle",
                            "accepted": True,
                            "failed_steps": [],
                        },
                    }
                ],
            }
        )

        entry = snapshot["entries"][0]
        self.assertEqual("reports-feed.v1", snapshot["schema_version"])
        self.assertEqual("scenario", entry["entry_type"])
        self.assertEqual("laboratory", entry["source_surface"])
        self.assertEqual("service_test", entry["source_mode"])
        self.assertEqual("turret_bridge", entry["module_id"])
        self.assertEqual("accepted", entry["result"])
        self.assertEqual("Scenario Finished", entry["title"])

    def test_reports_snapshot_preserves_remote_raw_details(self) -> None:
        snapshot = build_reports_snapshot(
            {
                "count": 1,
                "entries": [
                    {
                        "event_id": "platform-00007",
                        "timestamp_ms": 6400,
                        "origin_node": "esp32-main",
                        "mirrored": True,
                        "source": "sync_core",
                        "level": "warning",
                        "type": "peer_unreachable",
                        "message": "ESP32 peer marked as unreachable",
                        "details": "error_text=timeout",
                    }
                ],
            }
        )

        entry = snapshot["entries"][0]
        self.assertTrue(entry["mirrored"])
        self.assertEqual("sync", entry["entry_type"])
        self.assertEqual("system", entry["source_surface"])
        self.assertEqual({"raw": "error_text=timeout"}, entry["parameters"])
        self.assertEqual("attention", entry["result"])
        self.assertEqual(1, snapshot["summary"]["warning_count"])


if __name__ == "__main__":
    unittest.main()
