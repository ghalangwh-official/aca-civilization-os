"""End-to-end ACA demo.

This demo stitches together the local edge logic and the cloud ingestion
contract without requiring a live ROS 2 runtime or a live Kafka cluster.

It is intended to prove the shape of the system:

sensor frame -> telemetry bridge -> safety gate -> gateway parsing
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gateway = load_module(REPO_ROOT / "aca-kernel-core" / "src" / "gateway" / "main.py", "demo_gateway")
telemetry = load_module(
    REPO_ROOT / "aca-edge-ros2" / "src" / "telemetry_bridge" / "node.py",
    "demo_telemetry_bridge",
)
safety = load_module(REPO_ROOT / "aca-edge-ros2" / "src" / "safety_gate" / "node.py", "demo_safety_gate")


def main() -> None:
    sensor_frame = {
        "battery_voltage": 24.2,
        "kinematics": {
            "current_velocity_rps": 2.6,
            "heading_deg": 12.0,
        },
        "spatial_anomaly": {
            "detected": True,
            "vector_embedding_clip": [0.15, 0.22, 0.31, 0.44],
        },
    }
    motion_command = {
        "target_velocity_rps": 2.6,
        "target_heading_deg": 12.0,
        "battery_percent": 84.0,
    }

    telemetry_payload = telemetry.emit_telemetry(
        sensor_frame,
        telemetry.TelemetryBridgeConfig(robot_id="DEMO-ROBOT-001"),
        timestamp_ms=1234567890,
    )
    safety_decision = safety.evaluate_motion_command(motion_command)
    measurements = gateway.extract_measurements(
        {
            "robot_id": telemetry_payload["robot_id"],
            "battery_voltage": telemetry_payload["battery_voltage"],
            "kinematics": telemetry_payload["kinematics"],
        }
    )
    parsed_payload = gateway.parse_payload(json.dumps(telemetry_payload))

    print("ACA end-to-end demo")
    print("===================")
    print("Telemetry payload:")
    print(json.dumps(telemetry_payload, indent=2, ensure_ascii=False))
    print()
    print("Safety decision:")
    print(json.dumps(safety_decision, indent=2, ensure_ascii=False))
    print()
    print("Gateway measurements:")
    print(measurements)
    print()
    print("Parsed payload robot_id:", parsed_payload["robot_id"])


if __name__ == "__main__":
    main()
