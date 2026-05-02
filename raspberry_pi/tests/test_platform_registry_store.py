from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from platform_registry_store import PlatformRegistryStore, normalize_registry


class PlatformRegistryStoreTests(unittest.TestCase):
    def test_default_registry_uses_motion_sensor_for_cat_feeder(self) -> None:
        registry = normalize_registry({})
        cat_feeder = next(item for item in registry["modules"] if item["id"] == "cat_feeder")
        component_ids = set(cat_feeder["component_ids"])

        self.assertIn("cat_feeder_motion_sensor", component_ids)
        self.assertNotIn("light_sensor", component_ids)

    def test_constructor_save_adds_module_component_and_assignment(self) -> None:
        test_path = PROJECT_ROOT / "content" / ".system" / "test_platform_registry_store.tmp.json"
        test_path.unlink(missing_ok=True)
        try:
            store = PlatformRegistryStore(test_path)
            payload = store.upsert_constructor_draft(
                {
                    "moduleName": "Garden Gate",
                    "controllerNode": "io_node",
                    "componentName": "Gate servo",
                    "componentKind": "actuator",
                    "powerProfile": "5-6V",
                    "pinout": "PWM TBD",
                    "tolerance": "angle limits TBD",
                    "operatingModes": "open, close",
                }
            )

            registry = payload["registry"]
            self.assertTrue(payload["accepted"])
            self.assertIn("garden_gate", {item["id"] for item in registry["modules"]})
            self.assertIn(payload["component_id"], {item["id"] for item in registry["components"]})
            self.assertIn(
                ("garden_gate", payload["component_id"]),
                {(item["module_id"], item["component_id"]) for item in registry["assignments"]},
            )
        finally:
            test_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
