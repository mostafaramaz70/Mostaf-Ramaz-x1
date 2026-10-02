"""
Ramaz X1 Memory Engine
Version: 1.2.0

Rules:
- Training is stored when User teaches
- Experience is stored ONLY when User approves transfer
- Discoveries stay PENDING until User approves/rejects
- Agents never auto-promote training/discovery into experience
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

    def propose_discovery(self, content: Any, evidence: Optional[List] = None, confidence: float = 0.0) -> str:
        """Agent can only PROPOSE discovery. User decides later."""
        entry_id = f"DISCOVERY-{uuid.uuid4().hex[:8]}"
        entry = {
            "id": entry_id,
            "content": content,
            "evidence": evidence or [],
            "confidence": confidence,
            "status": "PENDING_USER_APPROVAL",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.discoveries.append(entry)
        return entry_id

    def get_pending_discoveries(self) -> List[Dict[str, Any]]:
        return [d for d in self.discoveries if d["status"] == "PENDING_USER_APPROVAL"]

    def approve_discovery_to_experience(self, discovery_id: str, approved_by: str = "USER") -> Dict[str, Any]:
        """User-only action: discovery -> experience."""
        for d in self.discoveries:
            if d["id"] == discovery_id:
                if d["status"] != "PENDING_USER_APPROVAL":
                    return {"status": "INVALID_STATE", "discovery_id": discovery_id}

                d["status"] = "APPROVED_TO_EXPERIENCE"
                d["approved_by"] = approved_by
                d["approved_at"] = datetime.utcnow().isoformat()

                exp_id = self.add_experience(
                    content={
                        "from_discovery": discovery_id,
                        "content": d["content"],
                        "evidence": d.get("evidence", []),
                        "approved_by": approved_by
                    },
                    mission_id="USER-APPROVED-DISCOVERY",
                    confidence=float(d.get("confidence", 0))
                )
                return {"status": "APPROVED", "discovery_id": discovery_id, "experience_id": exp_id}

        return {"status": "NOT_FOUND", "discovery_id": discovery_id}

    def reject_discovery(self, discovery_id: str, reason: str = "", rejected_by: str = "USER") -> Dict[str, Any]:
        for d in self.discoveries:
            if d["id"] == discovery_id:
                d["status"] = "REJECTED"
                d["rejected_by"] = rejected_by
                d["reject_reason"] = reason
                d["rejected_at"] = datetime.utcnow().isoformat()
                return {"status": "REJECTED", "discovery_id": discovery_id}
        return {"status": "NOT_FOUND", "discovery_id": discovery_id}

    def promote_training_to_experience(
        self,
        training_id: str,
        exam_record: Optional[Dict[str, Any]] = None,
        approved_by: str = "USER"
    ) -> Dict[str, Any]:
        """User-only action: selected training (+ optional exam) -> experience."""
        training = None
        for t in self.training_memory:
            if t["id"] == training_id:
                training = t
                break

        if not training:
            return {"status": "NOT_FOUND", "training_id": training_id}

        exp_id = self.add_experience(
            content={
                "from_training": training_id,
                "training": training,
                "exam_record": exam_record or {},
                "approved_by": approved_by
            },
            mission_id="USER-APPROVED-TRAINING",
            confidence=float((exam_record or {}).get("score", 0))
        )
        return {"status": "APPROVED", "training_id": training_id, "experience_id": exp_id}

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

    def add_mission_history(self, mission_id: str, result: Dict[str, Any]) -> None:
        self.mission_history.append({
            "mission_id": mission_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

    def clear_working(self) -> None:
        self.working_memory.clear()
