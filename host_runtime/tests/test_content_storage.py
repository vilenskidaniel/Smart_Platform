from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from storage_status import build_content_status, cleanup_host_path_target


class ContentStorageTests(unittest.TestCase):
    def test_content_status_reports_expected_directories(self) -> None:
        root = PROJECT_ROOT / "content"
        status = build_content_status(root)

        self.assertEqual("filesystem", status["storage"])
        self.assertTrue(status["content_root_exists"])
        self.assertEqual("ready", status["content_root_state"])
        self.assertTrue(status["assets_ready"])
        self.assertTrue(status["audio_ready"])
        self.assertTrue(status["animations_ready"])
        self.assertTrue(status["libraries_ready"])
        self.assertIn("total_bytes", status)
        self.assertIn("paths", status)
        self.assertEqual(
            [
                "project_root",
                "libraries",
                "video",
                "audio",
                "gallery_reports",
                "gallery",
                "assets",
                "animations",
                "content_root",
            ],
            [entry["id"] for entry in status["paths"]],
        )
        self.assertTrue(all("file_count" in entry for entry in status["paths"]))
        self.assertTrue(all("total_bytes" in entry for entry in status["paths"]))
        libraries = next(entry for entry in status["paths"] if entry["id"] == "libraries")
        self.assertEqual("/irrigation?library=plants", libraries["app_url"])
        self.assertIn("plant_profile_count", libraries["metadata"])

    def test_cleanup_preview_and_confirm_stay_inside_content_root(self) -> None:
        root = PROJECT_ROOT / ".tmp_test_content_cleanup"
        target = root / "audio"
        target.mkdir(parents=True, exist_ok=True)
        (target / "sample.txt").write_text("hello", encoding="utf-8")

        try:
            preview = cleanup_host_path_target(
                "audio",
                project_root=PROJECT_ROOT,
                runtime_root=PROJECT_ROOT,
                content_root=root,
                confirm=False,
            )
            self.assertTrue(preview["accepted"])
            self.assertTrue(preview["preview"])
            self.assertEqual(1, preview["file_count"])
            self.assertTrue((target / "sample.txt").exists())

            result = cleanup_host_path_target(
                "audio",
                project_root=PROJECT_ROOT,
                runtime_root=PROJECT_ROOT,
                content_root=root,
                confirm=True,
            )
            self.assertTrue(result["accepted"])
            self.assertFalse(result["preview"])
            self.assertFalse((target / "sample.txt").exists())

            protected = cleanup_host_path_target(
                "project_root",
                project_root=PROJECT_ROOT,
                runtime_root=PROJECT_ROOT,
                content_root=root,
                confirm=True,
            )
            self.assertFalse(protected["accepted"])
        finally:
            if root.exists():
                for child in sorted(root.rglob("*"), reverse=True):
                    if child.is_file() or child.is_symlink():
                        child.unlink()
                    elif child.is_dir():
                        child.rmdir()
                root.rmdir()

    def test_reference_library_files_are_valid_json(self) -> None:
        library_root = PROJECT_ROOT / "content" / "libraries"
        expected = {
            "plant_profiles.v1.json": "plant_profiles",
            "plant_state_rules.v1.json": "plant_state_rules",
            "care_scenarios.v1.json": "care_scenarios",
        }

        for file_name, library_type in expected.items():
            payload = json.loads((library_root / file_name).read_text(encoding="utf-8"))
            self.assertEqual("1.0", payload["schema_version"])
            self.assertEqual(library_type, payload["library_type"])
            self.assertIsInstance(payload["entries"], list)


if __name__ == "__main__":
    unittest.main()
