"""High-level ACA civilization service boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import sys
from pathlib import Path
from typing import Any

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from audit.ledger import default_state_dir
from court.judge import CourtDecision, CourtJudge
from memory.store import MemoryEntry, MemoryStore


@dataclass
class CivilizationService:
    """Bind memory and court into one minimal service boundary."""

    memory: MemoryStore = field(default_factory=MemoryStore)
    court: CourtJudge = field(init=False)

    def __post_init__(self) -> None:
        self.court = CourtJudge(memory=self.memory)

    @property
    def state_dir(self) -> Path:
        value = getattr(self.memory, "state_dir", None) or default_state_dir()
        return Path(value)

    def store_knowledge(
        self,
        text: str,
        *,
        kind: str,
        source: str = "service",
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        return self.memory.add(text, kind=kind, source=source, metadata=metadata)

    def judge_claim(self, claim: str) -> CourtDecision:
        return self.court.evaluate(claim)

    def search_memory(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        return self.memory.search(query, limit=limit)

    def recent_decisions(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.court.load_audit()[-limit:]

    def snapshot(self) -> dict[str, Any]:
        return {
            "state_dir": str(self.state_dir),
            "memory_entries": len(self.memory.entries),
            "court_audit_entries": len(self.court.load_audit()),
        }


def _render_decision(decision: CourtDecision) -> dict[str, Any]:
    return {
        "case_id": decision.case_id,
        "claim": decision.claim,
        "verdict": decision.verdict,
        "confidence": decision.confidence,
        "reasons": decision.reasons,
        "evidence": decision.evidence,
    }


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ACA civilization service")
    subcommands = parser.add_subparsers(dest="command", required=True)

    remember = subcommands.add_parser("remember", help="Store knowledge in memory")
    remember.add_argument("--kind", required=True)
    remember.add_argument("--text")
    remember.add_argument("--file")
    remember.add_argument("--pretty", action="store_true")

    judge = subcommands.add_parser("judge", help="Judge a claim")
    judge.add_argument("--claim")
    judge.add_argument("--file")
    judge.add_argument("--pretty", action="store_true")

    search = subcommands.add_parser("search", help="Search memory")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--pretty", action="store_true")

    snapshot = subcommands.add_parser("snapshot", help="Show service snapshot")
    snapshot.add_argument("--pretty", action="store_true")

    args = parser.parse_args()
    service = CivilizationService()

    if args.command == "remember":
        text = args.text if args.text is not None else Path(args.file).read_text(encoding="utf-8")
        entry = service.store_knowledge(text, kind=args.kind)
        output = {
            "entry_id": entry.entry_id,
            "kind": entry.kind,
            "source": entry.source,
            "metadata": entry.metadata,
        }
    elif args.command == "judge":
        claim = args.claim if args.claim is not None else Path(args.file).read_text(encoding="utf-8")
        decision = service.judge_claim(claim)
        output = _render_decision(decision)
    elif args.command == "search":
        output = service.search_memory(args.query, limit=args.limit)
    elif args.command == "snapshot":
        output = service.snapshot()
    else:  # pragma: no cover - parser enforces commands
        raise SystemExit(2)

    if getattr(args, "pretty", False):
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(output, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
