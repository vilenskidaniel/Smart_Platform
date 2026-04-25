from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import build_content_status


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
        self.assertIn("paths", status)
        self.assertEqual(
            ["content_root", "gallery_reports", "assets", "audio", "animations", "libraries"],
            [entry["id"] for entry in status["paths"]],
        )
        self.assertTrue(all("file_count" in entry for entry in status["paths"]))

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
