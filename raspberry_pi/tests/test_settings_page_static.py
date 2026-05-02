from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SettingsPageStaticTests(unittest.TestCase):
    def test_normalize_settings_does_not_depend_on_later_ui_constants(self) -> None:
        html = (PROJECT_ROOT / "web" / "settings.html").read_text(encoding="utf-8")
        match = re.search(
            r"function normalizeSettings\(raw\) \{(?P<body>.*?)\n    function t\(key\)",
            html,
            flags=re.S,
        )
        self.assertIsNotNone(match)
        body = match.group("body")

        self.assertNotIn("SYNC_DOMAIN_OPTIONS", body)
        self.assertIn("DEFAULT_SETTINGS.synchronization.selected_domains", body)

    def test_tooltip_and_save_latency_contract_is_visible_in_settings_page(self) -> None:
        html = (PROJECT_ROOT / "web" / "settings.html").read_text(encoding="utf-8")

        self.assertIn("const TOOLTIP_HIDE_MS = 6000;", html)
        self.assertIn("const TOOLTIP_MOVE_TOLERANCE_PX = 3;", html)
        self.assertIn("const SETTINGS_SAVE_DEBOUNCE_MS = 500;", html)
        self.assertIn("function commitSettings", html)
        self.assertIn("function scheduleSettingsSave", html)

    def test_settings_page_restores_open_details_and_uses_dynamic_runtime_polling(self) -> None:
        html = (PROJECT_ROOT / "web" / "settings.html").read_text(encoding="utf-8")

        self.assertIn("function restoreOpenDetails(scope)", html)
        self.assertIn('document.addEventListener("toggle"', html)
        self.assertIn("restartRuntimeRefreshLoop();", html)
        self.assertIn('data-details-id="diagnostics-root"', html)
        self.assertIn('data-details-id="appearance-keyboard-map"', html)

    def test_smart_bar_uses_same_tooltip_timing(self) -> None:
        script = (PROJECT_ROOT / "web" / "static" / "smart_bar.js").read_text(encoding="utf-8")

        self.assertIn("const TOOLTIP_HIDE_MS = 6000;", script)
        self.assertIn("const TOOLTIP_MOVE_TOLERANCE_PX = 3;", script)
        self.assertIn("function positionTooltipNearPointer", script)

    def test_smart_bar_applies_global_theme_and_density(self) -> None:
        script = (PROJECT_ROOT / "web" / "static" / "smart_bar.js").read_text(encoding="utf-8")

        self.assertIn('const SETTINGS_THEME_KEY = "smart-platform.settings.theme";', script)
        self.assertIn('const SETTINGS_DENSITY_KEY = "smart-platform.settings.density";', script)
        self.assertIn("function applyShellAppearance()", script)
        self.assertIn('body[data-shell-theme="contrast"]', script)
        self.assertIn('body[data-shell-density="compact"]', script)


if __name__ == "__main__":
    unittest.main()
