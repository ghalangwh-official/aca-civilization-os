# ACA Edge ROS 2

Embedded edge stack for telemetry bridging and safety filtering.

## Modules

- `telemetry_bridge`: normalizes raw sensor frames into the ACA telemetry contract.
- `safety_gate`: validates and clamps motion commands before they reach hardware.

## Local Configuration

- Copy `config/robot_profile.example.yaml` to `config/robot_profile.yaml`
- Set robot-specific hardware limits per unit
- Keep safety thresholds tighter than the physical hardware maximums

## Runtime Notes

- The Python modules are intentionally usable without a full ROS 2 runtime for testing.
- When integrating with ROS 2, wire the same normalization and safety logic into publishers and subscribers.
