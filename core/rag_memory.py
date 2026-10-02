"""
Ramaz X1 RAG Memory Brain
Version: 2.0.0

Upgrades:
- Persistent SQLite storage
- Pluggable embeddings (local hash default, OpenAI optional)
- Chunking for long documents
- Top-k retrieval for token-efficient prompts
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import uuid

from core.chunking import chunk_text
from core.embeddings import get_embedder, cosine_similarity


class RAGMemoryBrain:
    def __init__(self, agent_id: str, db_path: Optional[str] = None, embedder_provider: Optional[str] = None):
        self.agent_id = agent_id
        root = Path(__file__).resolve().parent.parent / "data" / "rag"
        root.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or str(root / f"{agent_id}.sqlite3")
        self.embedder = get_embedder(embedder_provider)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_units (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    meta_json TEXT,
                    source_id TEXT,
                    chunk_index INTEGER DEFAULT 0,
                    embedding_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_agent_kind ON memory_units(agent_id, kind)")
            conn.commit()

    def upsert(
        self,
        kind: str,
        content: str,
        title: str = "",
        meta: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
        chunk_size: int = 800,
        overlap: int = 120,
    ) -> List[Dict[str, Any]]:
        """
        Store one logical document as one or more chunked memory units.
        Returns list of stored units.
        """
        chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)
        if not chunks:
            return []

        stored: List[Dict[str, Any]] = []
        with self._connect() as conn:
            for ch in chunks:
                unit_id = f"MEM-{uuid.uuid4().hex[:10].upper()}"
                emb = self.embedder.embed(f"{title}\n{ch['content']}")
                created_at = datetime.utcnow().isoformat()
                conn.execute(
                    """
                    INSERT INTO memory_units
                    (id, agent_id, kind, title, content, meta_json, source_id, chunk_index, embedding_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        unit_id,
                        self.agent_id,
                        kind,
                        title,
                        ch["content"],
                        json.dumps(meta or {}, ensure_ascii=False),
                        source_id,
                        int(ch["index"]),
                        json.dumps(emb),
                        created_at,
                    ),
                )
                stored.append({
                    "id": unit_id,
                    "agent_id": self.agent_id,
                    "kind": kind,
                    "title": title,
                    "content": ch["content"],
                    "meta": meta or {},
                    "source_id": source_id,
                    "chunk_index": ch["index"],
                    "created_at": created_at,
                })
            conn.commit()
        return stored

    def delete(self, unit_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM memory_units WHERE id = ? AND agent_id = ?", (unit_id, self.agent_id))
            conn.commit()
            return cur.rowcount > 0

    def list_units(self, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if kind:
                rows = conn.execute(
                    "SELECT * FROM memory_units WHERE agent_id = ? AND kind = ? ORDER BY created_at DESC",
                    (self.agent_id, kind),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM memory_units WHERE agent_id = ? ORDER BY created_at DESC",
                    (self.agent_id,),
                ).fetchall()

        return [self._row_to_unit(r) for r in rows]

    def _row_to_unit(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "agent_id": row["agent_id"],
            "kind": row["kind"],
            "title": row["title"],
            "content": row["content"],
            "meta": json.loads(row["meta_json"] or "{}"),
            "source_id": row["source_id"],
            "chunk_index": row["chunk_index"],
            "created_at": row["created_at"],
            "embedding": json.loads(row["embedding_json"] or "[]"),
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        kinds: Optional[List[str]] = None,
        min_score: float = 0.05,
    ) -> List[Dict[str, Any]]:
        qvec = self.embedder.embed(query)

        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM memory_units WHERE agent_id = ?",
                (self.agent_id,),
            ).fetchall()

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for row in rows:
            unit = self._row_to_unit(row)
            if kinds and unit["kind"] not in kinds:
                continue

            score = cosine_similarity(qvec, unit.get("embedding") or [])

            # Mild priority for approved experience
            if unit["kind"] == "experience":
                score *= 1.15

            if score >= min_score:
                item = dict(unit)
                item.pop("embedding", None)
                item["score"] = round(float(score), 4)
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def build_context_pack(
        self,
        query: str,
        top_k: int = 5,
        kinds: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        hits = self.retrieve(query=query, top_k=top_k, kinds=kinds)
        compact_blocks = []
        for h in hits:
            title = h.get("title") or h["id"]
            compact_blocks.append(
                f"[{h['kind'].upper()}#{h.get('chunk_index', 0)}] {title}\n{h['content'][:1200]}"
            )

        return {
            "agent_id": self.agent_id,
            "query": query,
            "retrieved_count": len(hits),
            "units": hits,
            "context_text": "\n\n---\n\n".join(compact_blocks),
            "token_saving_policy": "top_k_retrieval_only",
            "embedder": getattr(self.embedder, "name", "unknown"),
            "persistent": True,
            "db_path": self.db_path,
            "created_at": datetime.utcnow().isoformat(),
        }
