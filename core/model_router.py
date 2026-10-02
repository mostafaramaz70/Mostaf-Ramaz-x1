"""
Ramaz X1 Model Router
Version: 2.1.0

Persistent multi-API routing per agent.
- Models/API attachments saved in SQLite
- User can switch active model
- Failover on quota/rate-limit/error
- Memory/RAG remains independent from API provider
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import uuid


class ModelEndpoint:
    def __init__(
        self,
        name: str,
        provider: str,
        model_id: str,
        role: str = "primary",
        enabled: bool = True,
        api_key_ref: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        endpoint_id: Optional[str] = None,
        status: str = "READY",
        last_error: Optional[str] = None,
        failure_count: int = 0,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        now = datetime.utcnow().isoformat()
        self.id = endpoint_id or f"MODEL-{uuid.uuid4().hex[:8].upper()}"
        self.name = name
        self.provider = provider
        self.model_id = model_id
        self.role = role
        self.enabled = enabled
        self.api_key_ref = api_key_ref
        self.meta = meta or {}
        self.status = status
        self.last_error = last_error
        self.failure_count = failure_count
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "model_id": self.model_id,
            "role": self.role,
            "enabled": self.enabled,
            "api_key_ref": self.api_key_ref,
            "status": self.status,
            "last_error": self.last_error,
            "failure_count": self.failure_count,
            "meta": self.meta,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AgentModelRouter:
    def __init__(self, agent_id: str, db_path: Optional[str] = None):
        self.agent_id = agent_id
        root = Path(__file__).resolve().parent.parent / "data" / "models"
        root.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or str(root / "agent_models.sqlite3")
        self.models: Dict[str, ModelEndpoint] = {}
        self.active_model_id: Optional[str] = None
        self._init_db()
        self._load()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_models (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    enabled INTEGER NOT NULL,
                    api_key_ref TEXT,
                    status TEXT NOT NULL,
                    last_error TEXT,
                    failure_count INTEGER NOT NULL DEFAULT 0,
                    meta_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_active_model (
                    agent_id TEXT PRIMARY KEY,
                    model_ref_id TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_models_agent ON agent_models(agent_id)")
            conn.commit()

    def _load(self) -> None:
        self.models = {}
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_models WHERE agent_id = ?",
                (self.agent_id,),
            ).fetchall()
            for r in rows:
                endpoint = ModelEndpoint(
                    name=r["name"],
                    provider=r["provider"],
                    model_id=r["model_id"],
                    role=r["role"],
                    enabled=bool(r["enabled"]),
                    api_key_ref=r["api_key_ref"],
                    meta=json.loads(r["meta_json"] or "{}"),
                    endpoint_id=r["id"],
                    status=r["status"],
                    last_error=r["last_error"],
                    failure_count=int(r["failure_count"] or 0),
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                )
                self.models[endpoint.id] = endpoint

            active = conn.execute(
                "SELECT model_ref_id FROM agent_active_model WHERE agent_id = ?",
                (self.agent_id,),
            ).fetchone()
            if active and active["model_ref_id"] in self.models:
                self.active_model_id = active["model_ref_id"]
            elif self.models:
                # fallback to first enabled model
                for m in self.models.values():
                    if m.enabled:
                        self.active_model_id = m.id
                        self._save_active()
                        break

    def _save_model(self, model: ModelEndpoint) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_models (
                    id, agent_id, name, provider, model_id, role, enabled,
                    api_key_ref, status, last_error, failure_count, meta_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    provider=excluded.provider,
                    model_id=excluded.model_id,
                    role=excluded.role,
                    enabled=excluded.enabled,
                    api_key_ref=excluded.api_key_ref,
                    status=excluded.status,
                    last_error=excluded.last_error,
                    failure_count=excluded.failure_count,
                    meta_json=excluded.meta_json,
                    updated_at=excluded.updated_at
                """,
                (
                    model.id,
                    self.agent_id,
                    model.name,
                    model.provider,
                    model.model_id,
                    model.role,
                    1 if model.enabled else 0,
                    model.api_key_ref,
                    model.status,
                    model.last_error,
                    model.failure_count,
                    json.dumps(model.meta, ensure_ascii=False),
                    model.created_at,
                    model.updated_at,
                ),
            )
            conn.commit()

    def _save_active(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_active_model (agent_id, model_ref_id, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    model_ref_id=excluded.model_ref_id,
                    updated_at=excluded.updated_at
                """,
                (self.agent_id, self.active_model_id, datetime.utcnow().isoformat()),
            )
            conn.commit()

    def attach_model(
        self,
        name: str,
        provider: str,
        model_id: str,
        role: str = "primary",
        enabled: bool = True,
        api_key_ref: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        set_active: bool = False,
    ) -> Dict[str, Any]:
        endpoint = ModelEndpoint(
            name=name,
            provider=provider,
            model_id=model_id,
            role=role,
            enabled=enabled,
            api_key_ref=api_key_ref,
            meta=meta,
        )
        self.models[endpoint.id] = endpoint
        self._save_model(endpoint)

        if set_active or self.active_model_id is None:
            self.active_model_id = endpoint.id
            self._save_active()

        return endpoint.to_dict()

    def list_models(self) -> List[Dict[str, Any]]:
        items = []
        for m in self.models.values():
            d = m.to_dict()
            d["is_active"] = (m.id == self.active_model_id)
            items.append(d)
        return items

    def get_active(self) -> Optional[Dict[str, Any]]:
        if not self.active_model_id:
            return None
        model = self.models.get(self.active_model_id)
        if not model:
            return None
        d = model.to_dict()
        d["is_active"] = True
        return d

    def switch_model(self, model_ref_id: str) -> Dict[str, Any]:
        model = self.models.get(model_ref_id)
        if not model:
            return {"status": "NOT_FOUND", "model_id": model_ref_id}
        if not model.enabled:
            return {"status": "DISABLED", "model_id": model_ref_id}

        self.active_model_id = model.id
        model.status = "READY"
        model.updated_at = datetime.utcnow().isoformat()
        self._save_model(model)
        self._save_active()

        return {
            "status": "SWITCHED",
            "agent_id": self.agent_id,
            "active_model": model.to_dict(),
            "persistent": True,
            "db_path": self.db_path,
        }

    def set_enabled(self, model_ref_id: str, enabled: bool) -> bool:
        model = self.models.get(model_ref_id)
        if not model:
            return False
        model.enabled = enabled
        model.status = "READY" if enabled else "DISABLED"
        model.updated_at = datetime.utcnow().isoformat()
        self._save_model(model)

        if not enabled and self.active_model_id == model_ref_id:
            alt = self._next_available(exclude=model_ref_id)
            self.active_model_id = alt.id if alt else None
            self._save_active()
        return True

    def mark_failure(self, model_ref_id: str, error: str, error_type: str = "ERROR") -> Dict[str, Any]:
        model = self.models.get(model_ref_id)
        if not model:
            return {"status": "NOT_FOUND"}

        model.failure_count += 1
        model.last_error = error
        model.status = error_type if error_type in {"RATE_LIMITED", "QUOTA_EXCEEDED", "ERROR"} else "ERROR"
        model.updated_at = datetime.utcnow().isoformat()
        self._save_model(model)
        return {"status": "MARKED", "model": model.to_dict(), "persistent": True}

    def mark_success(self, model_ref_id: str) -> None:
        model = self.models.get(model_ref_id)
        if not model:
            return
        model.status = "READY"
        model.last_error = None
        model.updated_at = datetime.utcnow().isoformat()
        self._save_model(model)

    def _next_available(self, exclude: Optional[str] = None) -> Optional[ModelEndpoint]:
        order = ["primary", "secondary", "fallback"]
        candidates = [
            m for m in self.models.values()
            if m.enabled and m.id != exclude and m.status in {"READY", "ERROR"}
        ]
        ready = [m for m in candidates if m.status == "READY"]
        pool = ready or candidates

        for role in order:
            for m in pool:
                if m.role == role:
                    return m
        return pool[0] if pool else None

    def select(self, prefer_role: str = "primary", allow_failover: bool = True) -> Optional[Dict[str, Any]]:
        if self.active_model_id and self.active_model_id in self.models:
            active = self.models[self.active_model_id]
            if active.enabled and active.status == "READY":
                d = active.to_dict()
                d["is_active"] = True
                d["selection_mode"] = "ACTIVE"
                return d

            if allow_failover and active.status in {"RATE_LIMITED", "QUOTA_EXCEEDED", "ERROR"}:
                alt = self._next_available(exclude=active.id)
                if alt:
                    self.active_model_id = alt.id
                    self._save_active()
                    d = alt.to_dict()
                    d["is_active"] = True
                    d["selection_mode"] = "AUTO_FAILOVER"
                    d["failover_from"] = active.id
                    return d

        enabled = [m for m in self.models.values() if m.enabled and m.status == "READY"]
        preferred = [m for m in enabled if m.role == prefer_role]
        chosen = preferred[0] if preferred else (enabled[0] if enabled else None)
        if not chosen:
            return None

        self.active_model_id = chosen.id
        self._save_active()
        d = chosen.to_dict()
        d["is_active"] = True
        d["selection_mode"] = "ROLE_SELECT"
        return d

    def select_ensemble(self, roles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        roles = roles or ["primary", "secondary"]
        out = []
        for role in roles:
            for m in self.models.values():
                if m.enabled and m.role == role and m.status == "READY":
                    item = m.to_dict()
                    item["is_active"] = (m.id == self.active_model_id)
                    out.append(item)
        return out
