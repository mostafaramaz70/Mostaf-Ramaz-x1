"""
TECH-NDS-01 — Raw Trainable Employee Agent
Technical Department
Version: 2.1.0
Status: RAW / Ready for Training

Rules:
- User teaches -> Training memory
- User exams are evaluation only
- Experience is created ONLY by explicit User approval
- Discoveries are proposed and stay pending until User decides
- Experience weight > Training weight at runtime
- No hardcoded domain concepts
"""

from typing import Dict, Any, List
from datetime import datetime
from memory.memory_engine import MemoryEngine


class TechNDS01:
    IDENTITY = {
        "agent_id": "TECH-NDS-01",
        "name": "NDS Worker",
        "agent_type": "Employee",
        "department": "Technical",
        "role": "Trainable Technical Analyst",
        "version": "2.1.0",
        "status": "RAW"
    }

    RESPONSIBILITIES = [
        "Receive training from User",
        "Store training in training memory",
        "Take User exams (evaluation only)",
        "Propose discoveries for User approval",
        "Use User-approved training + experience during analysis",
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
        self.exam_history: List[Dict[str, Any]] = []

    def receive_training(self, training_item: Dict[str, Any]) -> Dict[str, Any]:
        training_id = self.memory_engine.add_training(
            content=training_item.get("content", ""),
            title=training_item.get("title", "Untitled Training"),
            source=training_item.get("source", "USER"),
            tags=training_item.get("tags", [])
        )
        if self.identity["status"] == "RAW":
            self.identity["status"] = "TRAINING"
        return {"status": "STORED", "training_id": training_id}

    def list_training(self) -> List[Dict[str, Any]]:
        return self.memory_engine.get_training()

    def take_test(self, test_input: Dict[str, Any], user_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exam/evaluation only.
        Does NOT write to experience.
        User must explicitly approve transfer later.
        """
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

    def propose_discovery(self, content: Any, evidence: List = None, confidence: float = 0.0) -> Dict[str, Any]:
        discovery_id = self.memory_engine.propose_discovery(
            content=content,
            evidence=evidence or [],
            confidence=confidence
        )
        return {
            "status": "PENDING_USER_APPROVAL",
            "discovery_id": discovery_id,
            "message": "Discovery proposed. Waiting for USER decision."
        }

    def _retrieve_relevant_training(self, query: str) -> List[Dict[str, Any]]:
        items = self.memory_engine.get_training()
        q = (query or "").lower()
        if not q:
            return items[-5:]
        hits = []
        for item in items:
            blob = f"{item.get('title','')} {item.get('content','')} {' '.join(item.get('tags', []))}".lower()
            if q in blob:
                hits.append(item)
        return hits[-5:] if hits else items[-3:]

    def _retrieve_relevant_experience(self, query: str) -> List[Dict[str, Any]]:
        items = self.memory_engine.get_experience()
        q = (query or "").lower()
        if not q:
            return items[-5:]
        hits = []
        for exp in items:
            if q in str(exp.get("content", "")).lower():
                hits.append(exp)
        return hits[-5:] if hits else items[-3:]

    def analyze(self, mission_input: Dict[str, Any]) -> Dict[str, Any]:
        self.memory_engine.add_working(mission_input, meta={"type": "mission_input"})

        objective = str(mission_input.get("objective", ""))
        raw_input = mission_input.get("input", mission_input)
        query = f"{objective} {raw_input}"

        training_hits = self._retrieve_relevant_training(query)
        experience_hits = self._retrieve_relevant_experience(query)

        has_training = len(training_hits) > 0
        has_experience = len(experience_hits) > 0

        confidence = 0.0
        if has_training:
            confidence += 0.25
        if has_experience:
            scores = []
            for exp in experience_hits:
                content = exp.get("content", {})
                if isinstance(content, dict):
                    scores.append(float(content.get("score", exp.get("confidence", 0))))
                else:
                    scores.append(float(exp.get("confidence", 0)))
            avg_exp = sum(scores) / len(scores) if scores else 0.3
            confidence += min(0.65, 0.40 + avg_exp * 0.25)

        confidence = round(min(confidence, 0.95), 2)

        if not has_training and not has_experience:
            summary = "Agent is RAW. No training and no user-approved experience yet."
            recommendation = "NO_TRADE"
            basis = "NONE"
        elif has_experience and has_training:
            summary = "Prepared from training + user-approved experience. Experience weighted higher."
            recommendation = "WAIT_USER_VALIDATION"
            basis = "TRAINING+EXPERIENCE"
        elif has_experience:
            summary = "Prepared mainly from user-approved experience."
            recommendation = "WAIT_USER_VALIDATION"
            basis = "EXPERIENCE"
        else:
            summary = "Only training available. Experience requires explicit USER approval."
            recommendation = "WAIT_USER_VALIDATION"
            basis = "TRAINING_ONLY"

        result = {
            "agent_id": self.identity["agent_id"],
            "version": self.identity["version"],
            "mission_id": mission_input.get("mission_id"),
            "output_type": "Analysis",
            "agent_state": self.identity["status"],
            "analysis": {
                "method": "TRAINING_AND_USER_APPROVED_EXPERIENCE",
                "basis": basis,
                "training_used_count": len(training_hits),
                "experience_used_count": len(experience_hits),
                "training_refs": [t.get("id") for t in training_hits],
                "experience_refs": [e.get("id") for e in experience_hits],
                "summary": summary,
                "notes": [
                    "No hardcoded domain rules are embedded.",
                    "Experience must be explicitly approved by USER."
                ]
            },
            "confidence": confidence,
            "evidence": [
                f"Training items used: {len(training_hits)}",
                f"Experience items used: {len(experience_hits)}",
                "Experience weight > Training weight"
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
