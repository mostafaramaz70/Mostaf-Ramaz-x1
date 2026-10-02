"""
Base Trainable Agent
Shared behavior for raw agents:
- User training
- Exam evaluation only
- Discovery proposals
- RAG recall via AgentBrain
- Experience only after USER approval (external API/memory path)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from memory.memory_engine import MemoryEngine
from core.brain_registry import get_agent_brain


class BaseTrainableAgent:
    IDENTITY: Dict[str, Any] = {}

    def __init__(self):
        self.identity = self.IDENTITY.copy()
        self.memory_engine = MemoryEngine(agent_id=self.identity["agent_id"])
        self.brain = get_agent_brain(self.identity["agent_id"])
        self.exam_history: List[Dict[str, Any]] = []

    def receive_training(self, training_item: Dict[str, Any]) -> Dict[str, Any]:
        training_id = self.memory_engine.add_training(
            content=training_item.get("content", ""),
            title=training_item.get("title", "Untitled Training"),
            source=training_item.get("source", "USER"),
            tags=training_item.get("tags", []),
        )

        units = self.brain.remember_training(
            title=training_item.get("title", "Untitled Training"),
            content=str(training_item.get("content", "")),
            source_id=training_id,
            meta={
                "source": training_item.get("source", "USER"),
                "tags": training_item.get("tags", []),
                "source_ref": training_item.get("source_ref"),
            },
        )

        if self.identity.get("status") == "RAW":
            self.identity["status"] = "TRAINING"

        return {"status": "STORED", "training_id": training_id, "rag_units": len(units)}

    def take_test(self, test_input: Dict[str, Any], user_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        exam = {
            "id": f"EXAM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "test_input": test_input,
            "agent_response": test_input.get("agent_response"),
            "user_evaluation": user_evaluation,
            "score": float(user_evaluation.get("score", 0)),
            "feedback": user_evaluation.get("feedback", ""),
            "auto_transferred_to_experience": False,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.exam_history.append(exam)
        self.memory_engine.add_working(exam, meta={"type": "exam_evaluation"})
        return {
            "status": "EXAM_RECORDED",
            "exam_id": exam["id"],
            "score": exam["score"],
            "message": "Exam stored. Experience requires explicit USER approval.",
        }

    def propose_discovery(self, content: Any, evidence: Optional[List] = None, confidence: float = 0.0) -> Dict[str, Any]:
        discovery_id = self.memory_engine.propose_discovery(
            content=content,
            evidence=evidence or [],
            confidence=confidence,
        )
        self.brain.remember_discovery_pending(
            title=f"Discovery {discovery_id}",
            content=str(content),
            source_id=discovery_id,
            meta={"confidence": confidence, "evidence": evidence or []},
        )
        return {
            "status": "PENDING_USER_APPROVAL",
            "discovery_id": discovery_id,
            "message": "Discovery proposed. Waiting for USER decision.",
        }

    def recall(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        return self.brain.recall(query=query, top_k=top_k, kinds=["training", "experience"])
