"""
Ramaz X1 Agent Brain
Version: 2.0.0
"""

from typing import Dict, Any, List, Optional
from core.model_router import AgentModelRouter
from core.rag_memory import RAGMemoryBrain


class AgentBrain:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.models = AgentModelRouter(agent_id=agent_id)
        self.rag = RAGMemoryBrain(agent_id=agent_id)

    def attach_model(self, name: str, provider: str, model_id: str, role: str = "primary", meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.models.attach_model(
            name=name,
            provider=provider,
            model_id=model_id,
            role=role,
            meta=meta,
        )

    def list_models(self) -> List[Dict[str, Any]]:
        return self.models.list_models()

    def remember_training(self, title: str, content: str, source_id: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self.rag.upsert(
            kind="training",
            title=title,
            content=content,
            source_id=source_id,
            meta=meta or {"source": "USER"},
        )

    def remember_experience(self, title: str, content: str, source_id: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self.rag.upsert(
            kind="experience",
            title=title,
            content=content,
            source_id=source_id,
            meta=meta or {"approved_by": "USER"},
        )

    def remember_discovery_pending(self, title: str, content: str, source_id: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        meta = meta or {}
        meta["status"] = "PENDING_USER_APPROVAL"
        return self.rag.upsert(
            kind="discovery",
            title=title,
            content=content,
            source_id=source_id,
            meta=meta,
        )

    def recall(self, query: str, top_k: int = 5, kinds: Optional[List[str]] = None) -> Dict[str, Any]:
        return self.rag.build_context_pack(query=query, top_k=top_k, kinds=kinds)

    def build_model_prompt(self, task: str, query: str, top_k: int = 5) -> Dict[str, Any]:
        context_pack = self.recall(query=query, top_k=top_k, kinds=["training", "experience"])
        selected = self.models.select(prefer_role="primary")
        ensemble = self.models.select_ensemble()

        prompt = (
            f"TASK:\n{task}\n\n"
            f"RELEVANT MEMORY (retrieved, not full history):\n{context_pack.get('context_text') or '[no relevant memory]'}\n\n"
            f"QUERY:\n{query}\n"
        )

        return {
            "agent_id": self.agent_id,
            "selected_model": selected,
            "ensemble_models": ensemble,
            "context_pack": context_pack,
            "prompt": prompt,
            "note": "Full memory is NOT injected. Only retrieved top-k units are used."
        }
