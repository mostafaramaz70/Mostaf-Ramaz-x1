"""
Ramaz X1 Knowledge Engine
Version: 1.0.0

Stores validated permanent knowledge.
Knowledge enters system only after approval.
Approved knowledge is immutable.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class KnowledgeEngine:
    """
    Central knowledge store for the organization.
    Rules:
    - Knowledge requires approval
    - Knowledge is versioned
    - Knowledge is immutable after approval
    - Deprecated knowledge is archived
    """

    def __init__(self):
        self.knowledge_base: Dict[str, Dict[str, Any]] = {}
        self.archived: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        content: Any,
        category: str,
        source: str,
        approved_by: str = "FOUNDER",
        version: str = "1.0"
    ) -> str:
        knowledge_id = f"KNOWLEDGE-{uuid.uuid4().hex[:8].upper()}"
        entry = {
            "id": knowledge_id,
            "content": content,
            "category": category,
            "source": source,
            "version": version,
            "status": "APPROVED",
            "approved_by": approved_by,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.knowledge_base[knowledge_id] = entry
        return knowledge_id

    def get(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        return self.knowledge_base.get(knowledge_id)

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [k for k in self.knowledge_base.values() if k["category"] == category]

    def search(self, query: str) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        for k in self.knowledge_base.values():
            content_str = str(k["content"]).lower()
            if query_lower in content_str:
                results.append(k)
        return results

    def deprecate(self, knowledge_id: str) -> bool:
        if knowledge_id not in self.knowledge_base:
            return False
        entry = self.knowledge_base.pop(knowledge_id)
        entry["status"] = "DEPRECATED"
        entry["updated_at"] = datetime.utcnow().isoformat()
        self.archived[knowledge_id] = entry
        return True

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self.knowledge_base.values())
