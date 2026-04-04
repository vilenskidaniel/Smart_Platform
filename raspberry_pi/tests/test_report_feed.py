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

    def test_reports_snapshot_parses_remote_key_value_details(self) -> None:
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
        self.assertEqual({"error_text": "timeout"}, entry["parameters"])
        self.assertEqual("attention", entry["result"])
        self.assertEqual(1, snapshot["summary"]["warning_count"])

    def test_reports_snapshot_maps_testcase_entries(self) -> None:
        snapshot = build_reports_snapshot(
            {
                "count": 1,
                "entries": [
                    {
                        "event_id": "platform-00011",
                        "timestamp_ms": 9100,
                        "origin_node": "rpi-turret",
                        "mirrored": False,
                        "source": "testcase_capture",
                        "level": "warning",
                        "type": "testcase_result_recorded",
                        "message": "testcase esp32-shell-smoke recorded for strobe_bench as warn",
                        "details": {
                            "case_id": "esp32-shell-smoke",
                            "module_id": "strobe_bench",
                            "board": "esp32",
                            "test_result": "warn",
                            "note": "top ribbon is readable but too dense",
                            "active_mode": "service_test",
                        },
                    }
                ],
            }
        )

        entry = snapshot["entries"][0]
        self.assertEqual("testcase", entry["entry_type"])
        self.assertEqual("laboratory", entry["source_surface"])
        self.assertEqual("service_test", entry["source_mode"])
        self.assertEqual("strobe_bench", entry["module_id"])
        self.assertEqual("warn", entry["result"])
        self.assertEqual("Testcase esp32-shell-smoke", entry["title"])
        self.assertEqual(1, snapshot["summary"]["entry_types"]["testcase"])

    def test_reports_snapshot_maps_operator_note_entries_and_filters(self) -> None:
        snapshot = build_reports_snapshot(
            {
                "count": 2,
                "entries": [
                    {
                        "event_id": "platform-00012",
                        "timestamp_ms": 9200,
                        "origin_node": "rpi-turret",
                        "mirrored": False,
                        "source": "testcase_capture",
                        "level": "info",
                        "type": "operator_note",
                        "message": "peer handoff feels clear, but pills are still dense",
                        "details": {
                            "case_id": "dual-home-smoke",
                            "module_id": "turret_bridge",
                            "board": "raspberry_pi",
                            "note": "peer handoff feels clear, but pills are still dense",
                        },
                    },
                    {
                        "event_id": "platform-00013",
                        "timestamp_ms": 9300,
                        "origin_node": "rpi-turret",
                        "mirrored": False,
                        "source": "sync_core",
                        "level": "warning",
                        "type": "peer_unreachable",
                        "message": "ESP32 peer marked as unreachable",
                        "details": {"error_text": "timeout"},
                    },
                ],
            },
            filters={"entry_type": "operator_note", "surface": "laboratory"},
        )

        self.assertEqual(1, snapshot["count"])
        self.assertEqual({"entry_type": "operator_note", "surface": "laboratory"}, snapshot["filters"])
        entry = snapshot["entries"][0]
        self.assertEqual("operator_note", entry["entry_type"])
        self.assertEqual("laboratory", entry["source_surface"])
        self.assertEqual("Operator Note / dual-home-smoke", entry["title"])
        self.assertEqual("rpi-turret", next(iter(snapshot["summary"]["origin_nodes"].keys())))


if __name__ == "__main__":
    unittest.main()
