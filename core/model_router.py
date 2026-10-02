"""
Ramaz X1 Model Router
Version: 1.0.0

Each agent can connect to one or more AI models.
Routing is configurable by User / system policy.
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
        meta: Optional[Dict[str, Any]] = None,
    ):
        self.id = f"MODEL-{uuid.uuid4().hex[:8].upper()}"
        self.name = name
        self.provider = provider          # openai | anthropic | google | local
        self.model_id = model_id          # gpt-4.1 | claude | gemini | ...
        self.role = role                  # primary | secondary | fallback
        self.enabled = enabled
        self.meta = meta or {}
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "model_id": self.model_id,
            "role": self.role,
            "enabled": self.enabled,
            "meta": self.meta,
            "created_at": self.created_at,
        }


class AgentModelRouter:
    """
    Per-agent model registry and selector.
    Allows multi-model attachment without rewriting agent memory.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.models: Dict[str, ModelEndpoint] = {}

    def attach_model(
        self,
        name: str,
        provider: str,
        model_id: str,
        role: str = "primary",
        enabled: bool = True,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        endpoint = ModelEndpoint(
            name=name,
            provider=provider,
            model_id=model_id,
            role=role,
            enabled=enabled,
            meta=meta,
        )
        self.models[endpoint.id] = endpoint
        return endpoint.to_dict()

    def list_models(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.models.values()]

    def set_enabled(self, model_ref_id: str, enabled: bool) -> bool:
        model = self.models.get(model_ref_id)
        if not model:
            return False
        model.enabled = enabled
        return True

    def select(self, prefer_role: str = "primary") -> Optional[Dict[str, Any]]:
        enabled = [m for m in self.models.values() if m.enabled]
        if not enabled:
            return None

        preferred = [m for m in enabled if m.role == prefer_role]
        chosen = preferred[0] if preferred else enabled[0]
        return chosen.to_dict()

    def select_ensemble(self, roles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        roles = roles or ["primary", "secondary"]
        out = []
        for role in roles:
            for m in self.models.values():
                if m.enabled and m.role == role:
                    out.append(m.to_dict())
        return out
