from __future__ import annotations

import shutil
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge_state import BridgeState
from report_archive import ReportArchive


class ReportArchiveTests(unittest.TestCase):
    @contextmanager
    def _temporary_dir(self) -> Path:
        temp_dir = PROJECT_ROOT / f".tmp_reports_{uuid.uuid4().hex}"
        shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_report_archive_persists_entries_between_instances(self) -> None:
        with self._temporary_dir() as temp_dir:
            reports_root = temp_dir / "gallery" / "reports"
            archive = ReportArchive(reports_root, max_entries=8)
            archive.append_platform_entry(
                {
                    "event_id": "platform-00001",
                    "origin_node": "rpi-turret",
                    "origin_event_id": "platform-00001",
                    "mirrored": False,
                    "timestamp_ms": 120,
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
            )

            reloaded = ReportArchive(reports_root, max_entries=8)
            snapshot = reloaded.snapshot(limit=10)

            self.assertEqual("report_archive_v1", snapshot["source_kind"])
            self.assertEqual(1, snapshot["count"])
            self.assertEqual("scenario", snapshot["entries"][0]["entry_type"])
            self.assertEqual("accepted", snapshot["entries"][0]["result"])

    def test_report_archive_trims_to_configured_limit(self) -> None:
        with self._temporary_dir() as temp_dir:
            reports_root = temp_dir / "gallery" / "reports"
            archive = ReportArchive(reports_root, max_entries=3)

            for index in range(4):
                archive.append_platform_entry(
                    {
                        "event_id": f"platform-{index + 1:05d}",
                        "origin_node": "rpi-turret",
                        "origin_event_id": f"platform-{index + 1:05d}",
                        "mirrored": False,
                        "timestamp_ms": 100 + index,
                        "source": "system_shell",
                        "level": "info",
                        "type": "boot_finished",
                        "message": f"boot message {index}",
                        "details": {},
                    }
                )

            snapshot = archive.snapshot(limit=10)
            self.assertEqual(3, snapshot["count"])
            self.assertEqual("boot message 3", snapshot["entries"][0]["message"])
            self.assertEqual("boot message 1", snapshot["entries"][-1]["message"])

    def test_bridge_state_uses_report_archive_when_content_root_is_provided(self) -> None:
        with self._temporary_dir() as temp_dir:
            content_root = temp_dir / "content"
            state = BridgeState(
                node_id="rpi-turret",
                shell_version="0.1.0",
                local_shell_base_url="http://raspberrypi.local:8080",
                peer_shell_base_url="http://192.168.4.1",
                content_root=str(content_root),
            )

            state.run_turret_scenario("service_safe_idle")
            archive_path = content_root / "gallery" / "reports" / "report_feed.jsonl"

            self.assertTrue(archive_path.exists())
            reports = state.build_reports(limit=20)
            self.assertEqual("report_archive_v1", reports["source_kind"])
            self.assertTrue(any(entry["entry_type"] == "scenario" for entry in reports["entries"]))


if __name__ == "__main__":
    unittest.main()
