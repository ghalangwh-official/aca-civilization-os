"""Safety gate logic for ACA edge robots.

This module evaluates motion commands against hard-coded limits so unsafe
instructions can be rejected before they reach hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

DEFAULT_MAX_WHEEL_VELOCITY_RPS = 4.5
DEFAULT_MIN_BATTERY_PERCENT = 20.0
DEFAULT_MAX_HEADING_DELTA_DEG = 90.0


@dataclass(frozen=True)
class SafetyLimits:
    max_wheel_velocity_rps: float = DEFAULT_MAX_WHEEL_VELOCITY_RPS
    min_battery_percent: float = DEFAULT_MIN_BATTERY_PERCENT
    max_heading_delta_deg: float = DEFAULT_MAX_HEADING_DELTA_DEG


def _require_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    return float(value)


def clamp_motion_command(
    command: Mapping[str, Any], limits: SafetyLimits = SafetyLimits()
) -> dict[str, Any]:
    """Clamp a motion command to safe edge limits."""
    target_velocity_rps = _require_number(command["target_velocity_rps"], "target_velocity_rps")
    target_heading_deg = _require_number(command["target_heading_deg"], "target_heading_deg")
    battery_percent = _require_number(command.get("battery_percent", 100.0), "battery_percent")

    safe_velocity = max(min(target_velocity_rps, limits.max_wheel_velocity_rps), 0.0)
    safe_heading = max(min(target_heading_deg, limits.max_heading_delta_deg), -limits.max_heading_delta_deg)

    return {
        "target_velocity_rps": safe_velocity,
        "target_heading_deg": safe_heading,
        "battery_percent": battery_percent,
    }


def evaluate_motion_command(
    command: Mapping[str, Any], limits: SafetyLimits = SafetyLimits()
) -> dict[str, Any]:
    """Decide whether a motion command is safe to execute."""
    safe_command = clamp_motion_command(command, limits)
    reasons: list[str] = []

    requested_velocity = _require_number(command["target_velocity_rps"], "target_velocity_rps")
    requested_heading = _require_number(command["target_heading_deg"], "target_heading_deg")
    battery_percent = safe_command["battery_percent"]

    if requested_velocity > limits.max_wheel_velocity_rps:
        reasons.append("target velocity exceeds hardware limit")
    if abs(requested_heading) > limits.max_heading_delta_deg:
        reasons.append("target heading delta exceeds allowed range")
    if battery_percent < limits.min_battery_percent:
        reasons.append("battery below safety threshold")

    allowed = not reasons
    return {
        "allowed": allowed,
        "safe_state": "EXECUTE" if allowed else "SAFE_STATE_LOCK",
        "recommended_action": "proceed" if allowed else "dock_and_recover",
        "reasons": reasons,
        "clamped_command": safe_command,
    }


def load_motion_command(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ACA safety gate validator")
    parser.add_argument(
        "--input",
        help="JSON file with a motion command. If omitted, read JSON from stdin.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the safety decision",
    )
    args = parser.parse_args()

    raw_command = load_motion_command(args.input) if args.input else json.loads(sys.stdin.read())
    decision = evaluate_motion_command(raw_command)
    if args.pretty:
        print(json.dumps(decision, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(decision, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
