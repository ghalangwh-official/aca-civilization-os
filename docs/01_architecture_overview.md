# Architecture Overview

ACA Civilization OS is organized as a cloud-to-edge monorepo.

## Layers

- Cloud kernel core handles ingestion, memory, audit, and orchestration.
- Edge ROS 2 stack handles local control, safety filtering, and offline resilience.
- Network bridge links both sides through a lossy or intermittent transport layer.

## Core Services

- Kafka: telemetry ingestion and event streaming.
- Qdrant: semantic and spatial memory retrieval.
- TimescaleDB: time-series audit ledger and anomaly history.
- gVisor: runtime isolation for dynamic cloud-side agents.

## Edge Services

- ROS 2 nodes: sensor adapters, motion control, and bridge publishers.
- `safety_gate`: hard safety limits for kinematics and actuation.
- Redis cache: local fallback state when cloud access is unavailable.

## Repository Layout

- `docs/`: architecture, math, security, and contracts.
- `aca-kernel-core/`: cloud-side logic and infrastructure composition.
- `aca-edge-ros2/`: embedded edge modules and configuration.
