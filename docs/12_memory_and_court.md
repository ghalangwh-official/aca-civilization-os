# Memory and Court Modules

## Purpose

These modules close one of the biggest gaps between ACA's blueprint and its implementation.

- `memory` preserves knowledge in a local index and mirrors it into Qdrant when available.
- `court` evaluates claims against memory, then decides whether to approve, reject, or retain them as dissent.

## Memory Module

### Responsibilities

- store knowledge entries locally
- build deterministic embeddings
- rank knowledge by similarity
- mirror entries into Qdrant when configured
- fall back to local mode when Qdrant is unavailable

### Design Notes

- local index keeps the system useful even without external services
- Qdrant integration is best-effort and optional at runtime
- deterministic embeddings keep the implementation reproducible and testable

## Court Module

### Responsibilities

- evaluate claims against memory evidence
- approve supported claims
- retain ambiguous claims as dissenting hypotheses
- reject unsupported claims while preserving auditability

### Decision Behavior

- high similarity to memory: `approve`
- moderate similarity: `dissent`
- low similarity: `reject`

## Why This Matters

- the blueprint talks about memory, dissent, and digital institutions
- the implementation now has a minimal version of both
- this makes the project feel like an actual system instead of only a manifesto

## Next Up

- connect court decisions to a more formal audit trail
- add persistence beyond process lifetime
- expose memory and court operations through a service/API boundary

