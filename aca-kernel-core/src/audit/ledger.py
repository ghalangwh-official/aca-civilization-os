"""Simple JSONL-backed audit helpers for ACA."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def default_state_dir() -> Path:
    base = os.getenv("ACA_STATE_DIR")
    if base:
        return Path(base)
    return Path(__file__).resolve().parents[3] / ".state"


def ensure_state_dir(path: str | Path | None = None) -> Path:
    state_dir = Path(path) if path is not None else default_state_dir()
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def append_jsonl(path: str | Path, event: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records
