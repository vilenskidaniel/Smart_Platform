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


class LaboratorySessionTests(unittest.TestCase):
    @contextmanager
    def _temporary_dir(self) -> Path:
        temp_dir = PROJECT_ROOT / f".tmp_lab_session_{uuid.uuid4().hex}"
        shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_session_context_flows_into_report_entries(self) -> None:
        with self._temporary_dir() as temp_dir:
            state = BridgeState(
                node_id="rpi-turret",
                shell_version="shell-v1",
                local_shell_base_url="http://127.0.0.1:8090",
                peer_shell_base_url="http://192.168.4.1",
                content_root=str(temp_dir / "content"),
            )

            started = state.start_laboratory_session(
                operator="vilen",
                objective="display qualification",
                hardware_profile="rpi5 + 8-inch touch",
                external_module="hdmi-usb touch panel",
                power_context="bench_psu",
                view_mode="browser",
                active_tool="overview",
                module_id="overview",
            )
            state.update_laboratory_context(
                power_context="battery",
                view_mode="fullscreen",
                active_tool="rpi_touch_display",
                module_id="rpi_touch_display",
            )

            note_entry = state.record_operator_note(
                note="edge zones stay stable",
                module_id="rpi_touch_display",
                board="raspberry_pi",
            )
            testcase_entry = state.record_testcase_result(
                case_id="rpi-touch-display-smoke",
                module_id="rpi_touch_display",
                result="pass",
                note="checker and grid stayed clean",
                board="raspberry_pi",
            )

            session_id = started["session"]["active_session"]["session_id"]
            for entry in (note_entry, testcase_entry):
                parameters = entry["parameters"]
                self.assertEqual(session_id, parameters["lab_session_id"])
                self.assertEqual("vilen", parameters["lab_operator"])
                self.assertEqual("display qualification", parameters["lab_objective"])
                self.assertEqual("battery", parameters["lab_power_context"])
                self.assertEqual("fullscreen", parameters["lab_view_mode"])
                self.assertEqual("rpi_touch_display", parameters["lab_active_tool"])
                self.assertEqual("rpi_touch_display", parameters["lab_context_module"])

    def test_finish_session_keeps_last_completed_snapshot(self) -> None:
        state = BridgeState(
            node_id="rpi-turret",
            shell_version="shell-v1",
            local_shell_base_url="http://127.0.0.1:8090",
            peer_shell_base_url="http://192.168.4.1",
        )

        state.start_laboratory_session(
            operator="vilen",
            objective="owner handoff smoke",
            hardware_profile="phone + local shell",
            external_module="",
            power_context="bench_psu",
            view_mode="browser",
            active_tool="overview",
            module_id="overview",
        )
        finished = state.finish_laboratory_session(summary_note="display pass complete")
        snapshot = state.build_laboratory_session()

        self.assertEqual("idle", snapshot["status"])
        self.assertIsNone(snapshot["active_session"])
        self.assertEqual("completed", snapshot["last_completed_session"]["status"])
        self.assertEqual("display pass complete", snapshot["last_completed_session"]["summary_note"])
        self.assertEqual("session", finished["report_entry"]["entry_type"])

    def test_laboratory_event_uses_laboratory_surface_and_metadata_override(self) -> None:
        state = BridgeState(
            node_id="rpi-turret",
            shell_version="shell-v1",
            local_shell_base_url="http://127.0.0.1:8090",
            peer_shell_base_url="http://192.168.4.1",
        )

        entry = state.record_laboratory_event(
            module_id="rpi_touch_display",
            event_type="display_pattern_changed",
            message="display pattern changed to checker",
            value="checker",
            laboratory_metadata={
                "lab_power_context": "battery",
                "lab_view_mode": "fullscreen",
            },
        )

        self.assertEqual("laboratory", entry["source_surface"])
        self.assertEqual("event", entry["entry_type"])
        self.assertEqual("rpi_touch_display", entry["module_id"])
        self.assertEqual("checker", entry["parameters"]["value"])
        self.assertEqual("battery", entry["parameters"]["lab_power_context"])
        self.assertEqual("fullscreen", entry["parameters"]["lab_view_mode"])


if __name__ == "__main__":
    unittest.main()