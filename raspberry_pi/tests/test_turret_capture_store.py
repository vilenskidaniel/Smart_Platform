from __future__ import annotations

import sys
import unittest
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge_state import BridgeState
from turret_capture_store import create_capture_artifact, list_capture_artifacts


class TurretCaptureStoreTests(unittest.TestCase):
    def test_photo_and_video_artifacts_are_stored_in_content_slices(self) -> None:
        root = PROJECT_ROOT / f".tmp_turret_captures_{uuid4().hex}"

        try:
            photo = create_capture_artifact(root, kind="photo", phase="photo", power_percent=50)
            self.assertEqual("photo", photo["kind"])
            self.assertTrue((root / "gallery" / "captures" / "photos").is_dir())
            self.assertTrue(Path(photo["artifact_path"]).is_file())
            self.assertTrue(photo["artifact_url"].startswith("/gallery/captures/photos/"))

            started = create_capture_artifact(root, kind="video", phase="video_start", power_percent=100)
            self.assertEqual("recording", started["status"])
            self.assertTrue(started["artifact_url"].startswith("/video/captures/"))

            stopped = create_capture_artifact(
                root,
                kind="video",
                phase="video_stop",
                capture_id=started["capture_id"],
                duration_ms=1200,
            )
            self.assertEqual("captured", stopped["status"])
            self.assertEqual(1200, stopped["duration_ms"])

            snapshot = list_capture_artifacts(root, limit=10)
            self.assertEqual("turret-captures.v1", snapshot["schema_version"])
            self.assertEqual(2, snapshot["count"])
        finally:
            if root.exists():
                for child in sorted(root.rglob("*"), reverse=True):
                    if child.is_file() or child.is_symlink():
                        child.unlink()
                    elif child.is_dir():
                        child.rmdir()
                root.rmdir()

    def test_bridge_state_records_turret_capture_as_media_report(self) -> None:
        root = PROJECT_ROOT / f".tmp_turret_capture_reports_{uuid4().hex}"

        try:
            state = BridgeState(
                node_id="rpi-turret",
                shell_version="0.1.0",
                local_shell_base_url="http://127.0.0.1:8090",
                peer_shell_base_url="http://127.0.0.1:8091",
                content_root=str(root),
            )
            artifact = create_capture_artifact(root, kind="photo", phase="photo")
            entry = state.record_turret_capture(
                kind=artifact["kind"],
                phase=artifact["phase"],
                capture_id=artifact["capture_id"],
                artifact_path=artifact["artifact_path"],
                artifact_url=artifact["artifact_url"],
                gallery_url=artifact["gallery_url"],
                status=artifact["status"],
            )

            self.assertEqual("media_capture", entry["entry_type"])
            self.assertEqual("turret", entry["source_surface"])
            reports = state.build_reports(limit=5, filters={"entry_type": "media_capture"})
            self.assertEqual(1, reports["count"])
            self.assertEqual(artifact["capture_id"], reports["entries"][0]["parameters"]["capture_id"])
        finally:
            if root.exists():
                for child in sorted(root.rglob("*"), reverse=True):
                    if child.is_file() or child.is_symlink():
                        child.unlink()
                    elif child.is_dir():
                        child.rmdir()
                root.rmdir()


if __name__ == "__main__":
    unittest.main()
