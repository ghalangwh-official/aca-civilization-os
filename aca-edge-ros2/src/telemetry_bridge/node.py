"""Telemetry bridge core for ACA edge robots.

The module normalizes robot sensor readings into the telemetry contract used by
the cloud ingestion gateway. It is intentionally independent from ROS 2 so it
can be unit-tested and reused in lightweight edge runtimes.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from pathlib import Path
from typing import Any, Iterable, Mapping

DEFAULT_TOPIC = "aca.builder.telemetry"
DEFAULT_MAX_EMBEDDING_ITEMS = 512


@dataclass(frozen=True)
class TelemetryBridgeConfig:
    robot_id: str
    topic: str = DEFAULT_TOPIC
    max_embedding_items: int = DEFAULT_MAX_EMBEDDING_ITEMS


def _require_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    return float(value)


def _normalize_embedding(values: Iterable[Any], max_items: int) -> list[float]:
    embedding: list[float] = []
    for value in values:
        if len(embedding) >= max_items:
            break
        embedding.append(_require_number(value, "vector_embedding_clip item"))
    return embedding


def normalize_telemetry(
    sensor_frame: Mapping[str, Any],
    config: TelemetryBridgeConfig,
    *,
    timestamp_ms: int | None = None,
) -> dict[str, Any]:
    """Convert raw sensor data into the ACA telemetry contract."""
    battery_voltage = _require_number(sensor_frame["battery_voltage"], "battery_voltage")
    kinematics = sensor_frame["kinematics"]
    if not isinstance(kinematics, Mapping):
        raise ValueError("kinematics must be a mapping")

    current_velocity_rps = _require_number(
        kinematics["current_velocity_rps"], "kinematics.current_velocity_rps"
    )
    heading_deg = _require_number(kinematics["heading_deg"], "kinematics.heading_deg")

    anomaly = sensor_frame.get("spatial_anomaly") or {}
    if not isinstance(anomaly, Mapping):
        raise ValueError("spatial_anomaly must be a mapping")

    detected = bool(anomaly.get("detected", False))
    embedding = anomaly.get("vector_embedding_clip", [])
    if embedding is None:
        embedding = []
    if not isinstance(embedding, Iterable) or isinstance(embedding, (str, bytes, bytearray)):
        raise ValueError("spatial_anomaly.vector_embedding_clip must be a sequence")

    payload = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "topic": config.topic,
        "robot_id": config.robot_id,
        "timestamp": int(timestamp_ms or (time.time() * 1000)),
        "battery_voltage": battery_voltage,
        "kinematics": {
            "current_velocity_rps": current_velocity_rps,
            "heading_deg": heading_deg,
        },
        "spatial_anomaly": {
            "detected": detected,
            "vector_embedding_clip": _normalize_embedding(embedding, config.max_embedding_items),
        },
    }
    return payload


def parse_sensor_json(raw_payload: str | bytes) -> dict[str, Any]:
    if isinstance(raw_payload, bytes):
        raw_payload = raw_payload.decode("utf-8")
    return json.loads(raw_payload)


def load_sensor_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def emit_telemetry(sensor_frame: Mapping[str, Any], config: TelemetryBridgeConfig) -> dict[str, Any]:
    """Build payload ready for cloud ingestion."""
    return normalize_telemetry(sensor_frame, config)


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ACA telemetry bridge helper")
    parser.add_argument("--robot-id", required=True, help="Stable robot identifier")
    parser.add_argument(
        "--input",
        help="JSON file with raw sensor data. If omitted, read JSON from stdin.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the normalized telemetry payload",
    )
    args = parser.parse_args()

    config = TelemetryBridgeConfig(robot_id=args.robot_id)
    raw_frame = load_sensor_payload(args.input) if args.input else parse_sensor_json(sys.stdin.read())
    payload = emit_telemetry(raw_frame, config)
    if args.pretty:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
