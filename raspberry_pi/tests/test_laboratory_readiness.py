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


@contextmanager
def _temporary_dir() -> Path:
    temp_dir = PROJECT_ROOT / f".tmp_reports_{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=False)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


class LaboratoryReadinessTests(unittest.TestCase):
    def test_readiness_marks_peer_owned_steps_blocked_until_peer_is_online(self) -> None:
        state = BridgeState(
            node_id="rpi-turret",
            shell_version="shell-v1",
            local_shell_base_url="http://127.0.0.1:8090",
            peer_shell_base_url="http://192.168.4.1",
        )

        readiness = state.build_laboratory_readiness()
        self.assertEqual("attention", readiness["overall_status"])

        peer_item = next(item for item in readiness["preflight"] if item["id"] == "peer_owner_link")
        display_step = next(step for step in readiness["bringup_sequence"] if step["id"] == "rpi_display_checks")
        strobe_step = next(step for step in readiness["bringup_sequence"] if step["id"] == "esp32_strobe_bench")
        session_step = next(step for step in readiness["bringup_sequence"] if step["id"] == "session_review")
        self.assertEqual("attention", peer_item["status"])
        self.assertIn("локальными срезами Raspberry Pi", peer_item["action"])
        self.assertEqual("ready", display_step["status"])
        self.assertEqual("/service?tool=rpi_touch_display", display_step["route"])
        self.assertEqual("blocked", strobe_step["status"])
        self.assertEqual("/service", session_step["route"])

    def test_readiness_turns_green_when_peer_and_archive_are_ready(self) -> None:
        with _temporary_dir() as temp_dir:
            state = BridgeState(
                node_id="rpi-turret",
                shell_version="shell-v1",
                local_shell_base_url="http://127.0.0.1:8090",
                peer_shell_base_url="http://192.168.4.1",
                content_root=str(temp_dir),
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
                        "uptime_ms": 3200,
                    },
                    "modules": [],
                }
            )

            readiness = state.build_laboratory_readiness()
            self.assertEqual("ready", readiness["overall_status"])
            reports_item = next(item for item in readiness["preflight"] if item["id"] == "reports_archive")
            display_step = next(step for step in readiness["bringup_sequence"] if step["id"] == "rpi_display_checks")
            peer_step = next(step for step in readiness["bringup_sequence"] if step["id"] == "peer_link_smoke")
            session_step = next(step for step in readiness["bringup_sequence"] if step["id"] == "session_review")
            self.assertEqual("ready", reports_item["status"])
            self.assertEqual("ready", display_step["status"])
            self.assertEqual("ready", peer_step["status"])
            self.assertEqual("ready", session_step["status"])

    def test_readiness_blocks_when_emergency_is_latched(self) -> None:
        state = BridgeState(
            node_id="rpi-turret",
            shell_version="shell-v1",
            local_shell_base_url="http://127.0.0.1:8090",
            peer_shell_base_url="http://192.168.4.1",
        )
        accepted, _ = state.update_turret_interlock("emergency")
        self.assertTrue(accepted)

        readiness = state.build_laboratory_readiness()
        self.assertEqual("blocked", readiness["overall_status"])

        mode_item = next(item for item in readiness["preflight"] if item["id"] == "safe_start_mode")
        turret_step = next(step for step in readiness["bringup_sequence"] if step["id"] == "turret_service_lane")
        self.assertEqual("blocked", mode_item["status"])
        self.assertEqual("blocked", turret_step["status"])


if __name__ == "__main__":
    unittest.main()
