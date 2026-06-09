# Memory, Court, and Audit Trail

## What Changed

ACA now has a minimal persistence layer for:

- memory entries
- court decisions
- service-level orchestration

## Memory Persistence

- local memory entries are saved as JSONL under the state directory
- memory is restored automatically when the store starts
- Qdrant remains optional and best-effort

## Court Audit Trail

- every court decision is appended to a JSONL audit log
- decisions remain readable after process restart
- memory and court can now be replayed as evidence-bearing artifacts

## Service Boundary

The `CivilizationService` class provides a compact interface for:

- storing knowledge
- judging claims
- searching memory
- listing recent court decisions
- inspecting service state

## Why This Matters

- it closes the biggest gap between the blueprint and the implementation
- it makes ACA feel like a system with history, not only a transient runtime
- it gives contributors a clear place to attach future APIs, CLI tools, or HTTP services

## Next Layer

- expose the service boundary over a local API
- index court decisions into TimescaleDB
- add retention policies and export tools

