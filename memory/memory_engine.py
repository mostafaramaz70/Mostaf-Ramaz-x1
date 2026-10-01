"""
Ramaz X1 Memory Engine
Version: 1.0.0

Every Agent owns independent memory.
Memory categories: Working, Long-Term, Knowledge, Experience, Discoveries, Mission History.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class MemoryEngine:
    """
    Independent memory system for each agent.
    Rules:
    - No shared editing
    - No automatic overwrite
    - Approved Knowledge is immutable
    - Experience accumulates
    - Discoveries remain pending until approval
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.working_memory: List[Dict[str, Any]] = []
        self.long_term_memory: List[Dict[str, Any]] = []
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

    def add_mission_history(self, mission_id: str, result: Dict[str, Any]) -> None:
        self.mission_history.append({
            "mission_id": mission_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_experience(self) -> List[Dict[str, Any]]:
        return self.experience

    def get_pending_discoveries(self) -> List[Dict[str, Any]]:
        return [d for d in self.discoveries if d["status"] == "PENDING"]

    def clear_working(self) -> None:
        self.working_memory.clear()
