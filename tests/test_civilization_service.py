from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = REPO_ROOT / "aca-kernel-core" / "src" / "civilization" / "service.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


civilization = load_module(SERVICE_PATH, "aca_civilization_service")


class CivilizationServiceTests(unittest.TestCase):
    def test_state_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            previous_state_dir = os.environ.get("ACA_STATE_DIR")
            previous_enable_qdrant = os.environ.get("ACA_ENABLE_QDRANT")
            try:
                os.environ["ACA_STATE_DIR"] = tmpdir
                os.environ["ACA_ENABLE_QDRANT"] = "0"

                first = civilization.CivilizationService()
                entry = first.store_knowledge("the robot avoided the dead end corridor", kind="lesson")
                self.assertEqual(entry.kind, "lesson")

                second = civilization.CivilizationService()
                hits = second.search_memory("dead end corridor", limit=1)
                self.assertEqual(hits[0]["text"], "the robot avoided the dead end corridor")
            finally:
                if previous_state_dir is None:
                    os.environ.pop("ACA_STATE_DIR", None)
                else:
                    os.environ["ACA_STATE_DIR"] = previous_state_dir

                if previous_enable_qdrant is None:
                    os.environ.pop("ACA_ENABLE_QDRANT", None)
                else:
                    os.environ["ACA_ENABLE_QDRANT"] = previous_enable_qdrant

    def test_judge_creates_audit_event(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            previous_state_dir = os.environ.get("ACA_STATE_DIR")
            previous_enable_qdrant = os.environ.get("ACA_ENABLE_QDRANT")
            try:
                os.environ["ACA_STATE_DIR"] = tmpdir
                os.environ["ACA_ENABLE_QDRANT"] = "0"

                service = civilization.CivilizationService()
                decision = service.judge_claim("robot should avoid dead end corridor")
                audit_entries = service.recent_decisions()
                self.assertTrue(audit_entries)
                self.assertEqual(audit_entries[-1]["claim"], decision.claim)
                self.assertIn(decision.verdict, {"approve", "dissent", "reject"})
            finally:
                if previous_state_dir is None:
                    os.environ.pop("ACA_STATE_DIR", None)
                else:
                    os.environ["ACA_STATE_DIR"] = previous_state_dir

                if previous_enable_qdrant is None:
                    os.environ.pop("ACA_ENABLE_QDRANT", None)
                else:
                    os.environ["ACA_ENABLE_QDRANT"] = previous_enable_qdrant


if __name__ == "__main__":
    unittest.main()
