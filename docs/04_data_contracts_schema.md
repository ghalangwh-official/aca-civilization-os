# Data Contracts Schema

This document defines the telemetry and event payloads used by the system.

## Telemetry Payload

- `robot_id`: unique robot identifier.
- `timestamp`: unix timestamp in milliseconds or seconds, depending on the transport.
- `battery_voltage`: current power state.
- `kinematics.current_velocity_rps`: movement speed.
- `kinematics.heading_deg`: current heading.
- `spatial_anomaly.detected`: whether the edge detector sees an anomaly.
- `spatial_anomaly.vector_embedding_clip`: optional embedding vector for memory indexing.

## Contract Rules

- All required fields must be present before ingestion.
- Embedded edge can reject unsafe or malformed messages.
- Cloud ingestion should preserve the original payload and timestamp.
- Vector embeddings should be treated as optional but structured data.

## Suggested Topics

- `aca.builder.telemetry`
- `aca.builder.safety`
- `aca.builder.memory`
- `aca.builder.audit`
