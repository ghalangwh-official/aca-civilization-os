# ACA Roadmap and Contribution Plan

## Goal

Turn ACA from a strong blueprint into a credible open-source robotics platform with a clear path for outside contributors.

## Current State

- Documentation is strong and versioned.
- Cloud ingestion gateway is functional and tested.
- Edge logic exists for telemetry normalization and safety gating.
- ROS 2 runtime integration is still a scaffold.
- Community contribution flow is not yet formalized.

## Priority Gaps

1. Real ROS 2 launch and package wiring.
2. Live end-to-end demo from sensor mock to safety decision and telemetry packaging.
3. Stronger contribution onboarding for external collaborators.
4. Issue templates and workboard structure for community participation.
5. More integration tests around config and launch surface.

## 2-Week Roadmap

### Week 1

- finalize ROS 2 launch files
- add a runnable local demo pipeline
- keep secrets out of code and document env usage
- add issue templates and contribution guide

### Week 2

- expand tests around config and edge logic
- add a clearer release checklist
- define the first external collaboration milestones
- document open architecture questions for contributors

## 30-Day Roadmap

- connect launch files to a real ROS 2 package layout
- add a telemetry bridge subscriber/publisher path
- define a minimal command whitelist for safety_gate
- create reproducible demo data and example payloads
- publish a contributor-friendly project map

## Community Workstreams

### 1. Robotics and Edge

- ROS 2 launch integration
- sensor adapters
- motion safety enforcement
- hardware profile management

### 2. Cloud Kernel

- telemetry ingestion
- memory indexing
- audit logging
- validation flows

### 3. Documentation

- architecture diagrams
- onboarding guide
- contribution guide
- API and contract reference

### 4. Testing and CI

- unit tests
- integration tests
- config checks
- workflow automation

## Suggested GitHub Issue Labels

- `good first issue`
- `edge`
- `cloud`
- `docs`
- `tests`
- `ci`
- `safety`
- `roadmap`
- `research`

## Suggested Project Board Columns

- Backlog
- Ready
- In Progress
- Review
- Done

## First External Issues to Open

1. Implement real ROS 2 node wrappers for telemetry_bridge.
2. Implement a real ROS 2 safety_gate subscriber path.
3. Add example motion and telemetry payloads.
4. Add launch files and package entrypoints.
5. Add a minimal end-to-end demo runner.

## Contribution Message

ACA is open for contributors who want to work on durable memory systems, safe robotics, and multi-agent governance. The repo should make it easy to see where help is needed and how to verify progress.

