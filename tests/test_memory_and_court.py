from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = REPO_ROOT / "aca-kernel-core" / "src" / "memory" / "store.py"
COURT_PATH = REPO_ROOT / "aca-kernel-core" / "src" / "court" / "judge.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


memory = load_module(MEMORY_PATH, "aca_memory_store")
court = load_module(COURT_PATH, "aca_court_judge")


class MemoryAndCourtTests(unittest.TestCase):
    def test_memory_store_search_orders_by_similarity(self):
        store = memory.MemoryStore(enable_qdrant=False)
        store.add("robot learned to avoid dead end corridor", kind="lesson")
        store.add("battery should dock below twenty percent", kind="policy")

        hits = store.search("avoid corridor dead end", limit=2)
        self.assertEqual(hits[0]["kind"], "lesson")

    def test_court_approves_supported_claim(self):
        store = memory.MemoryStore(enable_qdrant=False)
        store.add("the robot should avoid dead end corridor", kind="lesson")
        decision = court.CourtJudge(store).evaluate("robot should avoid dead end corridor")
        self.assertEqual(decision.verdict, "approve")
        self.assertGreaterEqual(decision.confidence, 0.72)

    def test_court_retains_dissent_or_rejection(self):
        store = memory.MemoryStore(enable_qdrant=False)
        decision = court.CourtJudge(store).evaluate("teleportation is a safe actuation method")
        self.assertIn(decision.verdict, {"dissent", "reject"})
        self.assertTrue(
            any(item.kind in {"dissenting_hypothesis", "rejected_claim"} for item in store.entries.values())
        )


if __name__ == "__main__":
    unittest.main()
