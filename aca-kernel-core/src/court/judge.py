"""ACA court and judge logic.

The court reviews claims against memory evidence and decides whether the claim
should be accepted, rejected, or retained as a dissenting hypothesis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import logging
from pathlib import Path
import sys
from typing import Any, Iterable

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from memory.store import MemoryStore

log = logging.getLogger("aca.court")

DEFAULT_APPROVAL_THRESHOLD = 0.72
DEFAULT_DISSENT_THRESHOLD = 0.45


@dataclass(frozen=True)
class CourtDecision:
    case_id: str
    claim: str
    verdict: str
    confidence: float
    reasons: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class CourtJudge:
    """Minimal judge that scores claims against memory evidence."""

    memory: MemoryStore
    approval_threshold: float = DEFAULT_APPROVAL_THRESHOLD
    dissent_threshold: float = DEFAULT_DISSENT_THRESHOLD

    def evaluate(self, claim: str, *, case_id: str | None = None) -> CourtDecision:
        case_id = case_id or hashlib.sha256(claim.encode("utf-8")).hexdigest()[:16]
        evidence = self.memory.search(claim, limit=5)
        top_score = evidence[0]["score"] if evidence else 0.0
        reasons: list[str] = []

        if top_score >= self.approval_threshold:
            verdict = "approve"
            reasons.append("claim is strongly supported by existing memory")
        elif top_score >= self.dissent_threshold:
            verdict = "dissent"
            reasons.append("claim is plausible but not yet strong enough for approval")
            self.memory.add(
                claim,
                kind="dissenting_hypothesis",
                source="court",
                metadata={"case_id": case_id, "status": "retained_for_review"},
            )
        else:
            verdict = "reject"
            reasons.append("claim is not supported by current memory")
            self.memory.add(
                claim,
                kind="rejected_claim",
                source="court",
                metadata={"case_id": case_id, "status": "retained_for_review"},
            )

        return CourtDecision(
            case_id=case_id,
            claim=claim,
            verdict=verdict,
            confidence=round(top_score, 4),
            reasons=reasons,
            evidence=evidence,
        )

    def review_many(self, claims: Iterable[str]) -> list[CourtDecision]:
        return [self.evaluate(claim) for claim in claims]


def evaluate_claim(claim: str, memory: MemoryStore | None = None) -> CourtDecision:
    memory = memory or MemoryStore()
    judge = CourtJudge(memory=memory)
    return judge.evaluate(claim)


def load_claim(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ACA court judge")
    parser.add_argument("--claim", help="Claim text to review. If omitted, read from stdin.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the decision")
    args = parser.parse_args()

    claim = args.claim if args.claim is not None else sys.stdin.read()
    decision = evaluate_claim(claim)
    output = {
        "case_id": decision.case_id,
        "claim": decision.claim,
        "verdict": decision.verdict,
        "confidence": decision.confidence,
        "reasons": decision.reasons,
        "evidence": decision.evidence,
    }
    if args.pretty:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(output, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
