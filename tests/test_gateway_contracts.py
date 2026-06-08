from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
GATEWAY_PATH = REPO_ROOT / "aca-kernel-core" / "src" / "gateway" / "main.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gateway = load_module(GATEWAY_PATH, "aca_gateway_main")


class GatewayContractTests(unittest.TestCase):
    def test_parse_payload_bytes(self):
        payload = gateway.parse_payload(b'{"robot_id":"R1","battery_voltage":12.5}')
        self.assertEqual(payload["robot_id"], "R1")

    def test_extract_measurements(self):
        robot_id, battery_voltage, velocity_rps = gateway.extract_measurements(
            {
                "robot_id": "R1",
                "battery_voltage": 12.5,
                "kinematics": {"current_velocity_rps": 2.25},
            }
        )
        self.assertEqual(robot_id, "R1")
        self.assertEqual(battery_voltage, 12.5)
        self.assertEqual(velocity_rps, 2.25)

    def test_settings_require_password(self):
        with self.assertRaises(RuntimeError):
            gateway.Settings.from_env()


if __name__ == "__main__":
    unittest.main()
