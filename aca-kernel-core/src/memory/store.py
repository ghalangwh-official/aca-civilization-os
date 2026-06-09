"""Minimal ACA memory store with optional Qdrant indexing.

This module keeps a local in-memory index for fast retrieval and mirrors
entries into Qdrant when the service is configured and reachable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import logging
import math
import os
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib import error, request

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from audit.ledger import append_jsonl, default_state_dir, ensure_state_dir, read_jsonl

log = logging.getLogger("aca.memory")

DEFAULT_DIMENSION = 64
DEFAULT_COLLECTION = "aca_civilization_memory"
DEFAULT_QDRANT_URL = "http://localhost:6333"


def _tokenize(text: str) -> list[str]:
    tokens = []
    current = []
    for char in text.lower():
        if char.isalnum() or char in {"_", "-"}:
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens


def build_embedding(text: str, dimensions: int = DEFAULT_DIMENSION) -> list[float]:
    """Build a deterministic bag-of-words style embedding."""
    vector = [0.0] * dimensions
    tokens = _tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        weight = 1.0 + (digest[4] / 255.0)
        vector[bucket] += weight

    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(l * r for l, r in zip(left, right))


def _json_request(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=5) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def _qdrant_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _ensure_qdrant_collection(base_url: str, collection_name: str, dimensions: int) -> None:
    payload = {
        "vectors": {
            "size": dimensions,
            "distance": "Cosine",
        }
    }
    try:
        _json_request("PUT", _qdrant_url(base_url, f"collections/{collection_name}"), payload)
    except Exception as exc:  # pragma: no cover - best effort integration
        log.warning("Qdrant collection setup skipped: %s", exc)


def _probe_qdrant(base_url: str) -> bool:
    try:
        _json_request("GET", _qdrant_url(base_url, "collections"))
        return True
    except Exception:
        return False


def _upsert_qdrant(
    base_url: str,
    collection_name: str,
    entry_id: str,
    embedding: list[float],
    payload: dict[str, Any],
) -> None:
    body = {
        "points": [
            {
                "id": entry_id,
                "vector": embedding,
                "payload": payload,
            }
        ]
    }
    _json_request("PUT", _qdrant_url(base_url, f"collections/{collection_name}/points"), body)


def _search_qdrant(
    base_url: str,
    collection_name: str,
    embedding: list[float],
    limit: int,
) -> list[dict[str, Any]]:
    body = {"vector": embedding, "limit": limit, "with_payload": True}
    response = _json_request("POST", _qdrant_url(base_url, f"collections/{collection_name}/points/search"), body)
    return response.get("result", [])


@dataclass(frozen=True)
class MemoryEntry:
    entry_id: str
    text: str
    kind: str
    source: str = "local"
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)


@dataclass
class MemoryStore:
    """Minimal durable-ish memory layer with optional Qdrant mirroring."""

    dimension: int = DEFAULT_DIMENSION
    collection_name: str = DEFAULT_COLLECTION
    qdrant_url: str = field(default_factory=lambda: os.getenv("ACA_QDRANT_URL", DEFAULT_QDRANT_URL))
    enable_qdrant: bool = field(default_factory=lambda: os.getenv("ACA_ENABLE_QDRANT", "1") != "0")
    state_dir: str | Path | None = None
    state_file_name: str = "memory_entries.jsonl"
    entries: dict[str, MemoryEntry] = field(default_factory=dict)
    state_path: Path = field(init=False)

    def __post_init__(self) -> None:
        resolved_state_dir = ensure_state_dir(self.state_dir or default_state_dir())
        self.state_dir = resolved_state_dir
        self.state_path = resolved_state_dir / self.state_file_name
        self._restore_state()
        if self.enable_qdrant and not _probe_qdrant(self.qdrant_url):
            log.warning("Qdrant not reachable; continuing in local-memory mode.")
            self.enable_qdrant = False
        if self.enable_qdrant:
            _ensure_qdrant_collection(self.qdrant_url, self.collection_name, self.dimension)

    def _restore_state(self) -> None:
        for record in read_jsonl(self.state_path):
            entry = MemoryEntry(
                entry_id=record["entry_id"],
                text=record["text"],
                kind=record["kind"],
                source=record.get("source", "local"),
                metadata=record.get("metadata", {}),
                embedding=record.get("embedding") or build_embedding(record["text"], self.dimension),
            )
            self.entries[entry.entry_id] = entry

    def _append_state(self, entry: MemoryEntry) -> None:
        append_jsonl(
            self.state_path,
            {
                "entry_id": entry.entry_id,
                "text": entry.text,
                "kind": entry.kind,
                "source": entry.source,
                "metadata": entry.metadata,
                "embedding": entry.embedding,
            },
        )

    def add(
        self,
        text: str,
        *,
        kind: str,
        source: str = "local",
        metadata: dict[str, Any] | None = None,
        entry_id: str | None = None,
    ) -> MemoryEntry:
        metadata = dict(metadata or {})
        entry_id = entry_id or hashlib.sha256(f"{kind}:{source}:{text}".encode("utf-8")).hexdigest()
        embedding = build_embedding(text, self.dimension)
        entry = MemoryEntry(
            entry_id=entry_id,
            text=text,
            kind=kind,
            source=source,
            metadata=metadata,
            embedding=embedding,
        )
        self.entries[entry_id] = entry
        self._append_state(entry)

        if self.enable_qdrant:
            payload = {
                "entry_id": entry.entry_id,
                "text": entry.text,
                "kind": entry.kind,
                "source": entry.source,
                **entry.metadata,
            }
            try:
                _upsert_qdrant(self.qdrant_url, self.collection_name, entry.entry_id, entry.embedding, payload)
            except error.URLError as exc:  # pragma: no cover - best effort integration
                log.warning("Qdrant upsert failed: %s", exc)
            except Exception as exc:  # pragma: no cover - best effort integration
                log.warning("Qdrant upsert skipped: %s", exc)

        return entry

    def search(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        embedding = build_embedding(query, self.dimension)
        local_results = [
            {
                "entry": entry,
                "score": _cosine_similarity(embedding, entry.embedding),
            }
            for entry in self.entries.values()
        ]
        local_results.sort(key=lambda item: item["score"], reverse=True)
        local_results = local_results[:limit]

        results = [
            {
                "entry_id": item["entry"].entry_id,
                "text": item["entry"].text,
                "kind": item["entry"].kind,
                "source": item["entry"].source,
                "metadata": item["entry"].metadata,
                "score": item["score"],
                "backend": "local",
            }
            for item in local_results
        ]

        if self.enable_qdrant:
            try:
                qdrant_hits = _search_qdrant(self.qdrant_url, self.collection_name, embedding, limit)
                for hit in qdrant_hits:
                    payload = hit.get("payload") or {}
                    results.append(
                        {
                            "entry_id": str(payload.get("entry_id", hit.get("id", ""))),
                            "text": payload.get("text", ""),
                            "kind": payload.get("kind", "unknown"),
                            "source": payload.get("source", "qdrant"),
                            "metadata": {
                                key: value
                                for key, value in payload.items()
                                if key not in {"entry_id", "text", "kind", "source"}
                            },
                            "score": hit.get("score", 0.0),
                            "backend": "qdrant",
                        }
                    )
            except error.URLError as exc:  # pragma: no cover - best effort integration
                log.warning("Qdrant search failed: %s", exc)
            except Exception as exc:  # pragma: no cover - best effort integration
                log.warning("Qdrant search skipped: %s", exc)

        deduped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in sorted(results, key=lambda entry: entry["score"], reverse=True):
            entry_id = item["entry_id"]
            if entry_id in seen:
                continue
            seen.add(entry_id)
            deduped.append(item)
        return deduped[:limit]

    def dump(self, path: str | Path) -> None:
        data = [
            {
                "entry_id": entry.entry_id,
                "text": entry.text,
                "kind": entry.kind,
                "source": entry.source,
                "metadata": entry.metadata,
            }
            for entry in self.entries.values()
        ]
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def load(self, path: str | Path) -> None:
        raw_path = Path(path)
        if raw_path.suffix == ".jsonl":
            records = read_jsonl(raw_path)
        else:
            records = json.loads(raw_path.read_text(encoding="utf-8"))

        self.entries.clear()
        for item in records:
            entry = MemoryEntry(
                entry_id=item["entry_id"],
                text=item["text"],
                kind=item["kind"],
                source=item.get("source", "local"),
                metadata=item.get("metadata", {}),
                embedding=item.get("embedding") or build_embedding(item["text"], self.dimension),
            )
            self.entries[entry.entry_id] = entry
