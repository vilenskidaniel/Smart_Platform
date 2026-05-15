from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class LaboratoryPageStaticTests(unittest.TestCase):
    def test_laboratory_page_is_unified_workspace(self) -> None:
        html = (PROJECT_ROOT / "web" / "service.html").read_text(encoding="utf-8")

        self.assertIn('href="/static/operator_hud.css"', html)
        self.assertIn('class="lab-page operator-hud"', html)
        self.assertIn('id: "turret_service"', html)
        self.assertIn('id: "rpi_touch_display"', html)
        self.assertIn('function resolveTool(toolId)', html)
        self.assertIn('turret_service', html)
        self.assertIn('rpi_touch_display', html)

    def test_laboratory_page_does_not_use_old_iframe_launcher_model(self) -> None:
        html = (PROJECT_ROOT / "web" / "service.html").read_text(encoding="utf-8").lower()

        self.assertNotIn("<iframe", html)
        self.assertNotIn("open-direct-link", html)
        self.assertNotIn("module-shell", html)

    def test_laboratory_page_keeps_reports_and_session_contracts(self) -> None:
        html = (PROJECT_ROOT / "web" / "service.html").read_text(encoding="utf-8")

        self.assertIn("/api/v1/laboratory/session", html)
        self.assertIn("/api/v1/laboratory/session/context", html)
        self.assertIn("/api/v1/laboratory/session/start", html)
        self.assertIn("/api/v1/laboratory/session/update", html)
        self.assertIn("/api/v1/laboratory/session/finish", html)
        self.assertIn("/api/v1/laboratory/event", html)
        self.assertIn("/api/v1/reports/testcase", html)
        self.assertIn("/api/v1/reports/note", html)

    def test_laboratory_page_uses_russian_core_labels(self) -> None:
        html = (PROJECT_ROOT / "web" / "service.html").read_text(encoding="utf-8")

        self.assertIn("<h1>Лаборатория</h1>", html)
        self.assertIn('id="active-category-chip">Обзор</span>', html)
        self.assertIn('title: "Обзор"', html)
        self.assertIn('title: "Свидетельства"', html)
        self.assertIn("<h3>Каркас сессии</h3>", html)
        self.assertIn("<h3>Готовность</h3>", html)
        self.assertIn('data-evidence-result="pass">Пройдено</button>', html)

    def test_laboratory_page_exposes_audio_baseline_and_local_draft(self) -> None:
        html = (PROJECT_ROOT / "web" / "service.html").read_text(encoding="utf-8")

        self.assertIn('fetchJson("/api/v1/settings", { cache: "no-store" })', html)
        self.assertIn('function renderAttackAudioWorkspace()', html)
        self.assertIn('function renderVoiceFxWorkspace()', html)
        self.assertIn('Saved baseline', html)
        self.assertIn('Local draft', html)
        self.assertIn('data-audio-slice="attack_audio"', html)
        self.assertIn('data-audio-slice="voice_fx"', html)
        self.assertIn('Взять baseline', html)


if __name__ == "__main__":
    unittest.main()
