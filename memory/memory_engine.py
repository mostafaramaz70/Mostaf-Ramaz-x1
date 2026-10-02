"""
Ramaz X1 Memory Engine
Version: 1.1.0

Every Agent owns independent memory.
Categories:
- Working
- Training (taught by User)
- Experience (from User tests / lived outcomes)
- Discoveries (pending approval)
- Mission History

Rules:
- Training comes from User teaching
- Experience comes from User tests / real outcomes
- Experience should weigh higher than Training at runtime
- No shared editing between agents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class MemoryEngine:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.working_memory: List[Dict[str, Any]] = []
        self.training_memory: List[Dict[str, Any]] = []
        self.experience: List[Dict[str, Any]] = []
        self.discoveries: List[Dict[str, Any]] = []
        self.mission_history: List[Dict[str, Any]] = []

    def add_working(self, content: Any, meta: Optional[Dict] = None) -> str:
        entry_id = f"WM-{uuid.uuid4().hex[:8]}"
        entry = {
            "id": entry_id,
            "content": content,
            "meta": meta or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.working_memory.append(entry)
        return entry_id

    def add_training(self, content: Any, title: str = "", source: str = "USER", tags: Optional[List[str]] = None) -> str:
        entry_id = f"TRAIN-{uuid.uuid4().hex[:8]}"
        entry = {
            "id": entry_id,
            "title": title or "Untitled Training",
            "content": content,
            "source": source,
            "tags": tags or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.training_memory.append(entry)
        return entry_id

    def get_training(self) -> List[Dict[str, Any]]:
        return self.training_memory

    def add_experience(self, content: Any, mission_id: str, confidence: float = 0.0) -> str:
        entry_id = f"EXP-{uuid.uuid4().hex[:8]}"
        entry = {
            "id": entry_id,
            "content": content,
            "mission_id": mission_id,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.experience.append(entry)
        return entry_id

    def get_experience(self) -> List[Dict[str, Any]]:
        return self.experience

    def add_discovery(self, content: Any, evidence: List, confidence: float = 0.0) -> str:
        entry_id = f"DISCOVERY-{uuid.uuid4().hex[:8]}"
        entry = {
            "id": entry_id,
            "content": content,
            "evidence": evidence,
            "confidence": confidence,
            "status": "PENDING",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.discoveries.append(entry)
        return entry_id

    def get_pending_discoveries(self) -> List[Dict[str, Any]]:
        return [d for d in self.discoveries if d["status"] == "PENDING"]

    def add_mission_history(self, mission_id: str, result: Dict[str, Any]) -> None:
        self.mission_history.append({
            "mission_id": mission_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

    def clear_working(self) -> None:
        self.working_memory.clear()
