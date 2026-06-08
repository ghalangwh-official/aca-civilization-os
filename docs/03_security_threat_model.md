# Security Threat Model

ACA OS assumes that cloud reasoning and physical execution can fail in different ways.

## Threats

- Prompt injection against cloud agents.
- Memory poisoning through untrusted vector writes.
- Unsafe motion commands reaching real hardware.
- Replay or tampering on telemetry transport.
- Runtime escape from dynamic containers.

## Mitigations

- Dual-LLM gating for validation before execution.
- Signed provenance for memory records.
- `safety_gate` firmware to enforce mechanical limits.
- Runtime sandboxing with gVisor for dynamic workloads.
- Offline caches to keep safety-critical state available when disconnected.

## Security Principles

- Never trust a single model output for physical actuation.
- Never allow unsafe commands to bypass the edge safety layer.
- Keep audit logs immutable and time-indexed.
- Treat network transport as unreliable by default.
