"""
Ramaz X1 Model Router
Version: 2.0.0

Goals:
- Each agent can connect to multiple AI APIs/models
- User can switch active model/API at any time
- Automatic failover when capacity/tokens/errors occur
- Memory/RAG stays independent from which API is used
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
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
    ):
        self.id = f"MODEL-{uuid.uuid4().hex[:8].upper()}"
        self.name = name
        self.provider = provider  # openai | anthropic | google | local | custom
        self.model_id = model_id
        self.role = role          # primary | secondary | fallback
        self.enabled = enabled
        self.api_key_ref = api_key_ref  # reference name, NOT raw secret storage ideal
        self.meta = meta or {}
        self.status = "READY"     # READY | RATE_LIMITED | QUOTA_EXCEEDED | ERROR | DISABLED
        self.last_error: Optional[str] = None
        self.failure_count = 0
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at

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
    """
    Per-agent multi-API registry + switch + failover.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.models: Dict[str, ModelEndpoint] = {}
        self.active_model_id: Optional[str] = None

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

        if set_active or self.active_model_id is None:
            self.active_model_id = endpoint.id

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
        return model.to_dict() if model else None

    def switch_model(self, model_ref_id: str) -> Dict[str, Any]:
        """User-driven hard switch to another attached API/model."""
        model = self.models.get(model_ref_id)
        if not model:
            return {"status": "NOT_FOUND", "model_id": model_ref_id}
        if not model.enabled:
            return {"status": "DISABLED", "model_id": model_ref_id}

        self.active_model_id = model.id
        model.status = "READY"
        model.updated_at = datetime.utcnow().isoformat()
        return {
            "status": "SWITCHED",
            "agent_id": self.agent_id,
            "active_model": model.to_dict(),
        }

    def set_enabled(self, model_ref_id: str, enabled: bool) -> bool:
        model = self.models.get(model_ref_id)
        if not model:
            return False
        model.enabled = enabled
        model.status = "READY" if enabled else "DISABLED"
        model.updated_at = datetime.utcnow().isoformat()
        if not enabled and self.active_model_id == model_ref_id:
            # auto-pick another enabled model
            alt = self._next_available(exclude=model_ref_id)
            self.active_model_id = alt.id if alt else None
        return True

    def mark_failure(self, model_ref_id: str, error: str, error_type: str = "ERROR") -> Dict[str, Any]:
        """
        Mark API/model unhealthy.
        error_type: RATE_LIMITED | QUOTA_EXCEEDED | ERROR
        """
        model = self.models.get(model_ref_id)
        if not model:
            return {"status": "NOT_FOUND"}

        model.failure_count += 1
        model.last_error = error
        model.status = error_type if error_type in {"RATE_LIMITED", "QUOTA_EXCEEDED", "ERROR"} else "ERROR"
        model.updated_at = datetime.utcnow().isoformat()

        return {"status": "MARKED", "model": model.to_dict()}

    def mark_success(self, model_ref_id: str) -> None:
        model = self.models.get(model_ref_id)
        if not model:
            return
        model.status = "READY"
        model.last_error = None
        model.updated_at = datetime.utcnow().isoformat()

    def _next_available(self, exclude: Optional[str] = None) -> Optional[ModelEndpoint]:
        # preference: primary -> secondary -> fallback -> any enabled READY
        order = ["primary", "secondary", "fallback"]
        candidates = [m for m in self.models.values() if m.enabled and m.id != exclude and m.status in {"READY", "ERROR"}]
        # Prefer READY over ERROR
        ready = [m for m in candidates if m.status == "READY"]
        pool = ready or candidates

        for role in order:
            for m in pool:
                if m.role == role:
                    return m
        return pool[0] if pool else None

    def select(self, prefer_role: str = "primary", allow_failover: bool = True) -> Optional[Dict[str, Any]]:
        # 1) active model if healthy
        if self.active_model_id and self.active_model_id in self.models:
            active = self.models[self.active_model_id]
            if active.enabled and active.status == "READY":
                d = active.to_dict()
                d["is_active"] = True
                d["selection_mode"] = "ACTIVE"
                return d

            # active exhausted -> failover
            if allow_failover and active.status in {"RATE_LIMITED", "QUOTA_EXCEEDED", "ERROR"}:
                alt = self._next_available(exclude=active.id)
                if alt:
                    self.active_model_id = alt.id
                    d = alt.to_dict()
                    d["is_active"] = True
                    d["selection_mode"] = "AUTO_FAILOVER"
                    d["failover_from"] = active.id
                    return d

        # 2) role preference
        enabled = [m for m in self.models.values() if m.enabled and m.status == "READY"]
        preferred = [m for m in enabled if m.role == prefer_role]
        chosen = preferred[0] if preferred else (enabled[0] if enabled else None)
        if not chosen:
            return None
        self.active_model_id = chosen.id
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
