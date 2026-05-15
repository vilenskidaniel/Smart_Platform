from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TurretPageStaticTests(unittest.TestCase):
    def test_turret_page_exposes_audio_profile_in_hud(self) -> None:
        html = (PROJECT_ROOT / "web" / "turret.html").read_text(encoding="utf-8")

        self.assertIn("function compactAudioLabel", html)
        self.assertIn("function audioTelemetryRows(productView)", html)
        self.assertIn("['ATK SCN'", html)
        self.assertIn("['ATK OUT'", html)
        self.assertIn("['VOICE FX'", html)
        self.assertIn("['VOICE IO'", html)
        self.assertIn("...audioTelemetryRows(productView)", html)


if __name__ == "__main__":
    unittest.main()