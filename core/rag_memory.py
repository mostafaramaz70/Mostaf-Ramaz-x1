"""
Ramaz X1 RAG Memory Brain
Version: 1.0.0

Goal:
- Store Training / Experience / Discoveries as retrievable memory units
- Avoid reloading full history into every model call
- New connected models reuse the same memory brain
- Human-like recall: retrieve only relevant fragments

Design:
1) Memory units are chunked and indexed
2) Query retrieves top-k relevant units
3) Only those units are injected into model context
4) Vector backend is pluggable (local hash baseline now, FAISS/Chroma later)
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import math
import re


def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    return re.findall(r"[\w\u0600-\u06FF]+", text)


def _bow_vector(tokens: List[str]) -> Dict[str, float]:
    vec: Dict[str, float] = {}
    for t in tokens:
        vec[t] = vec.get(t, 0.0) + 1.0
    # l2 normalize
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {k: v / norm for k, v in vec.items()}


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    # iterate smaller
    if len(a) > len(b):
        a, b = b, a
    score = 0.0
    for k, v in a.items():
        if k in b:
            score += v * b[k]
    return score


class MemoryUnit:
    def __init__(
        self,
        agent_id: str,
        kind: str,
        content: str,
        title: str = "",
        meta: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
    ):
        self.id = f"MEM-{uuid.uuid4().hex[:10].upper()}"
        self.agent_id = agent_id
        self.kind = kind  # training | experience | discovery | working
        self.title = title
        self.content = content
        self.meta = meta or {}
        self.source_id = source_id
        self.created_at = datetime.utcnow().isoformat()
        tokens = _tokenize(f"{title} {content}")
        self.vector = _bow_vector(tokens)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "kind": self.kind,
            "title": self.title,
            "content": self.content,
            "meta": self.meta,
            "source_id": self.source_id,
            "created_at": self.created_at,
        }


class RAGMemoryBrain:
    """
    Per-agent memory brain.

    Why this saves tokens:
    - Model does not read all memories every time
    - Only top-k relevant units are retrieved
    - Switching model does not require re-ingesting history
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.units: Dict[str, MemoryUnit] = {}

    def upsert(
        self,
        kind: str,
        content: str,
        title: str = "",
        meta: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        unit = MemoryUnit(
            agent_id=self.agent_id,
            kind=kind,
            content=content,
            title=title,
            meta=meta,
            source_id=source_id,
        )
        self.units[unit.id] = unit
        return unit.to_dict()

    def delete(self, unit_id: str) -> bool:
        return self.units.pop(unit_id, None) is not None

    def list_units(self, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        items = list(self.units.values())
        if kind:
            items = [u for u in items if u.kind == kind]
        return [u.to_dict() for u in items]

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        kinds: Optional[List[str]] = None,
        min_score: float = 0.05,
    ) -> List[Dict[str, Any]]:
        qvec = _bow_vector(_tokenize(query))
        scored: List[Tuple[float, MemoryUnit]] = []

        for unit in self.units.values():
            if kinds and unit.kind not in kinds:
                continue
            score = _cosine(qvec, unit.vector)

            # Experience gets mild priority boost (policy, not auto-approval)
            if unit.kind == "experience":
                score *= 1.15

            if score >= min_score:
                scored.append((score, unit))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, unit in scored[:top_k]:
            item = unit.to_dict()
            item["score"] = round(score, 4)
            results.append(item)
        return results

    def build_context_pack(
        self,
        query: str,
        top_k: int = 5,
        kinds: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build compact context for any model.
        This is what gets sent instead of full memory dump.
        """
        hits = self.retrieve(query=query, top_k=top_k, kinds=kinds)
        compact_blocks = []
        for h in hits:
            compact_blocks.append(
                f"[{h['kind'].upper()}] {h.get('title') or h['id']}\n{h['content'][:1200]}"
            )

        return {
            "agent_id": self.agent_id,
            "query": query,
            "retrieved_count": len(hits),
            "units": hits,
            "context_text": "\n\n---\n\n".join(compact_blocks),
            "token_saving_policy": "top_k_retrieval_only",
            "created_at": datetime.utcnow().isoformat(),
        }
