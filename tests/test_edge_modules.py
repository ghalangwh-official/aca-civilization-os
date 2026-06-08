from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_PATH = REPO_ROOT / "aca-edge-ros2" / "src" / "telemetry_bridge" / "node.py"
SAFETY_PATH = REPO_ROOT / "aca-edge-ros2" / "src" / "safety_gate" / "node.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


telemetry = load_module(TELEMETRY_PATH, "aca_telemetry_bridge_node")
safety = load_module(SAFETY_PATH, "aca_safety_gate_node")


class EdgeModuleTests(unittest.TestCase):
    def test_normalize_telemetry_builds_contract(self):
        payload = telemetry.normalize_telemetry(
            {
                "battery_voltage": 24.1,
                "kinematics": {
                    "current_velocity_rps": 2.75,
                    "heading_deg": 90,
                },
                "spatial_anomaly": {
                    "detected": True,
                    "vector_embedding_clip": [0.1, 0.2, 0.3],
                },
            },
            telemetry.TelemetryBridgeConfig(robot_id="R1"),
            timestamp_ms=1234567890,
        )
        self.assertEqual(payload["robot_id"], "R1")
        self.assertEqual(payload["timestamp"], 1234567890)
        self.assertEqual(payload["kinematics"]["current_velocity_rps"], 2.75)
        self.assertTrue(payload["spatial_anomaly"]["detected"])

    def test_safety_gate_rejects_overspeed(self):
        decision = safety.evaluate_motion_command(
            {
                "target_velocity_rps": 9.0,
                "target_heading_deg": 10.0,
                "battery_percent": 90.0,
            }
        )
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["safe_state"], "SAFE_STATE_LOCK")

    def test_safety_gate_allows_safe_command(self):
        decision = safety.evaluate_motion_command(
            {
                "target_velocity_rps": 2.0,
                "target_heading_deg": 15.0,
                "battery_percent": 80.0,
            }
        )
        self.assertTrue(decision["allowed"])
        self.assertEqual(decision["safe_state"], "EXECUTE")


if __name__ == "__main__":
    unittest.main()
