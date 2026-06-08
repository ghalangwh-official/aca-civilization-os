# ACA Technical Whitepaper

## Abstract

ACA defines a cloud-to-edge architecture for multi-agent AI systems where memory persistence, verification, safety, and physical execution are separated into explicit layers.

## System Goals

- preserve knowledge across agent turnover
- separate reasoning from actuation
- support long-lived institutional memory
- enable safe robot integration
- make system behavior measurable and auditable

## Core Layers

### 1. Application Layer

- planner agents
- research agents
- engineer agents
- teacher agents
- governance agents
- judge agents

### 2. Knowledge Layer

- short-term memory
- project memory
- skill memory
- civilization memory
- provenance metadata

### 3. Validation Layer

- court review
- confidence scoring
- dissenting hypothesis retention
- reputation weighting

### 4. Infrastructure Layer

- Kafka for telemetry ingestion
- Qdrant for semantic and spatial memory
- TimescaleDB for audit and time-series history
- gVisor for runtime isolation

### 5. Edge Safety Layer

- ROS 2 node execution
- `safety_gate`
- local offline cache
- hard kinematic constraints

## Data Flow

1. Robot generates telemetry.
2. Telemetry is bridged to Kafka.
3. Gateway validates and stores the event.
4. Memory systems index the event for retrieval.
5. Judge or research agents convert the event into SOP or lessons learned.
6. Safe updates are distributed back to the edge.

## Design Principles

- never trust a single model output for hardware actuation
- never delete dissenting knowledge prematurely
- preserve original telemetry for audit
- keep a clean separation between reasoning and control
- make every important decision traceable

## Minimal Implementation Baseline

ACA becomes technically credible when the repo includes:

- a real ingestion gateway
- a durable data contract
- a memory store
- a safety gate
- a working edge bridge
- a reproducible demo

## Evaluation Metrics

- knowledge growth
- knowledge retention
- innovation rate
- teaching efficiency
- failure reduction
- safety rejection rate
- recovery time after outage

