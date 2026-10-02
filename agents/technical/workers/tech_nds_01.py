"""
TECH-NDS-01 — Raw Trainable Employee Agent
Technical Department
Version: 2.2.0

Uses AgentBrain (RAG + multi-model):
- Training/Experience recalled via top-k retrieval
- No full memory dump into prompts
- Experience only from USER approval path
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from memory.memory_engine import MemoryEngine
from core.brain_registry import get_agent_brain


class TechNDS01:
    IDENTITY = {
        "agent_id": "TECH-NDS-01",
        "name": "NDS Worker",
        "agent_type": "Employee",
        "department": "Technical",
        "role": "Trainable Technical Analyst",
        "version": "2.2.0",
        "status": "RAW"
    }

    RESPONSIBILITIES = [
        "Receive training from User",
        "Store training in training memory + RAG index",
        "Take User exams (evaluation only)",
        "Propose discoveries for User approval",
        "Recall relevant memory via RAG during analysis",
        "Submit report only to TECH-MANAGER"
    ]

    RESTRICTIONS = [
        "No hardcoded domain trading concepts",
        "Cannot auto-promote training/discovery to experience",
        "Cannot invent knowledge not taught or user-approved",
        "Cannot communicate with other employees",
        "Cannot communicate with Assistant",
        "Cannot execute trades",
        "Cannot modify architecture"
    ]

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
            tags=training_item.get("tags", [])
        )

        # Index into persistent RAG brain (chunked)
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

        if self.identity["status"] == "RAW":
            self.identity["status"] = "TRAINING"

        return {
            "status": "STORED",
            "training_id": training_id,
            "rag_units": len(units)
        }

    def list_training(self) -> List[Dict[str, Any]]:
        return self.memory_engine.get_training()

    def take_test(self, test_input: Dict[str, Any], user_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        exam = {
            "id": f"EXAM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "test_input": test_input,
            "agent_response": test_input.get("agent_response"),
            "user_evaluation": user_evaluation,
            "score": float(user_evaluation.get("score", 0)),
            "feedback": user_evaluation.get("feedback", ""),
            "auto_transferred_to_experience": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.exam_history.append(exam)
        self.memory_engine.add_working(exam, meta={"type": "exam_evaluation"})

        return {
            "status": "EXAM_RECORDED",
            "exam_id": exam["id"],
            "score": exam["score"],
            "message": "Exam stored. Experience transfer requires explicit USER approval."
        }

    def propose_discovery(self, content: Any, evidence: Optional[List] = None, confidence: float = 0.0) -> Dict[str, Any]:
        discovery_id = self.memory_engine.propose_discovery(
            content=content,
            evidence=evidence or [],
            confidence=confidence
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
            "message": "Discovery proposed. Waiting for USER decision."
        }

    def analyze(self, mission_input: Dict[str, Any]) -> Dict[str, Any]:
        self.memory_engine.add_working(mission_input, meta={"type": "mission_input"})

        objective = str(mission_input.get("objective", ""))
        raw_input = mission_input.get("input", mission_input)
        query = f"{objective} {raw_input}"

        # RAG recall instead of dumping full memory
        context_pack = self.brain.recall(
            query=query,
            top_k=5,
            kinds=["training", "experience"]
        )

        units = context_pack.get("units", [])
        training_hits = [u for u in units if u.get("kind") == "training"]
        experience_hits = [u for u in units if u.get("kind") == "experience"]

        has_training = len(training_hits) > 0
        has_experience = len(experience_hits) > 0

        confidence = 0.0
        if has_training:
            confidence += 0.25
        if has_experience:
            scores = [float(u.get("score", 0)) for u in experience_hits]
            avg = sum(scores) / len(scores) if scores else 0.3
            confidence += min(0.65, 0.40 + avg * 0.25)
        confidence = round(min(confidence, 0.95), 2)

        if not has_training and not has_experience:
            summary = "Agent is RAW. No relevant training/experience retrieved from memory brain."
            recommendation = "NO_TRADE"
            basis = "NONE"
        elif has_experience and has_training:
            summary = "Prepared from retrieved training + user-approved experience (RAG top-k)."
            recommendation = "WAIT_USER_VALIDATION"
            basis = "TRAINING+EXPERIENCE"
        elif has_experience:
            summary = "Prepared mainly from retrieved user-approved experience."
            recommendation = "WAIT_USER_VALIDATION"
            basis = "EXPERIENCE"
        else:
            summary = "Only training fragments retrieved. Experience requires USER approval."
            recommendation = "WAIT_USER_VALIDATION"
            basis = "TRAINING_ONLY"

        # Optional model prompt pack (for connected LLMs)
        prompt_pack = self.brain.build_model_prompt(
            task="Analyze mission using only retrieved training and user-approved experience.",
            query=query,
            top_k=5,
        )

        result = {
            "agent_id": self.identity["agent_id"],
            "version": self.identity["version"],
            "mission_id": mission_input.get("mission_id"),
            "output_type": "Analysis",
            "agent_state": self.identity["status"],
            "analysis": {
                "method": "RAG_TRAINING_AND_USER_APPROVED_EXPERIENCE",
                "basis": basis,
                "training_used_count": len(training_hits),
                "experience_used_count": len(experience_hits),
                "training_refs": [t.get("id") for t in training_hits],
                "experience_refs": [e.get("id") for e in experience_hits],
                "retrieved_memory": units,
                "summary": summary,
                "notes": [
                    "No hardcoded domain rules are embedded.",
                    "Only RAG top-k memory injected for efficiency.",
                    "Experience must be explicitly approved by USER."
                ]
            },
            "model_prompt_pack": {
                "selected_model": prompt_pack.get("selected_model"),
                "retrieved_count": context_pack.get("retrieved_count"),
                "embedder": context_pack.get("embedder"),
                "persistent": context_pack.get("persistent"),
            },
            "confidence": confidence,
            "evidence": [
                f"Training fragments used: {len(training_hits)}",
                f"Experience fragments used: {len(experience_hits)}",
                "RAG retrieval active"
            ],
            "limitations": [
                "Skill depends on User training quality",
                "Experience only includes USER-approved items",
                "No autonomous promotion to experience"
            ],
            "recommendation": {
                "action": recommendation,
                "reason": summary
            },
            "status": "COMPLETED",
            "timestamp": datetime.utcnow().isoformat()
        }

        self.memory_engine.add_mission_history(
            mission_id=mission_input.get("mission_id", "UNKNOWN"),
            result=result
        )
        return result

    def generate_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "report_id": f"REPORT-{self.identity['agent_id']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "mission_id": analysis_result.get("mission_id"),
            "agent_id": self.identity["agent_id"],
            "department": "Technical",
            "analysis": analysis_result.get("analysis"),
            "confidence": analysis_result.get("confidence", 0.0),
            "evidence": analysis_result.get("evidence", []),
            "limitations": analysis_result.get("limitations", []),
            "recommendation": analysis_result.get("recommendation"),
            "model_prompt_pack": analysis_result.get("model_prompt_pack"),
            "validation": "PENDING",
            "status": analysis_result.get("status"),
            "timestamp": datetime.utcnow().isoformat()
        }

    def submit_to_manager(self, report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "from": self.identity["agent_id"],
            "to": "TECH-MANAGER",
            "type": "REPORT",
            "payload": report,
            "timestamp": datetime.utcnow().isoformat()
        }
