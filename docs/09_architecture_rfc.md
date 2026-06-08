# ACA Architecture RFC

## Title

ACA Cloud-to-Edge Civilizational Kernel

## Status

Proposed

## Motivation

The current codebase already expresses a useful direction:

- durable knowledge
- institutional roles
- robot-edge integration
- safety-first execution

This RFC defines the architecture as a set of stable modules so the project can grow without becoming a loose collection of notes and scripts.

## Proposed Modules

### `aca-kernel-core`

Responsibilities:

- ingest telemetry
- validate payloads
- write audit history
- index memory
- orchestrate research and governance logic

### `aca-edge-ros2`

Responsibilities:

- execute local robot nodes
- bridge telemetry to the cloud
- enforce safety constraints
- keep offline fallback state

### `docs`

Responsibilities:

- capture architecture intent
- define contracts
- describe security assumptions
- preserve version history

## Interface Contracts

### Telemetry Topic

- topic: `aca.builder.telemetry`
- payload: robot telemetry JSON
- minimum fields:
  - `robot_id`
  - `timestamp`
  - `battery_voltage`
  - `kinematics.current_velocity_rps`

### Safety Boundary

- all motion commands must pass the edge safety gate
- cloud output is advisory until validated locally
- unsafe or malformed commands must be rejected deterministically

## Operational Invariants

- cloud may reason, but edge decides final actuation safety
- memory must be durable and queryable
- rejected knowledge must remain recoverable
- no physical action is allowed without validation

## Migration Plan

### Phase 1

- finalize docs and contracts
- keep gateway and edge scaffold working

### Phase 2

- add real ROS 2 launch files
- add tests for ingestion and safety gate behavior

### Phase 3

- introduce a working demo with robot telemetry and memory updates

### Phase 4

- formalize governance, reputation, and teaching flows as services

## Open Questions

- what is the minimal safe command set for first deployment?
- what memory retention policy is acceptable for audit data?
- what should be synchronous versus asynchronous at the edge?
- how should dissenting hypotheses be versioned?

## Recommendation

Treat this RFC as the structural backbone of ACA. New code should map to one of these modules or justify why it does not.

