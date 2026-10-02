"""
TECH-NDS-01 — Raw Trainable Employee Agent
Technical Department
Version: 2.0.0
Status: RAW / Ready for Training

Important:
- This agent starts RAW.
- Domain knowledge (e.g. market structure concepts) must be taught by User.
- User training becomes Training Memory.
- User tests convert into Experience.
- At runtime agent relies on Training + Experience, with higher weight on Experience.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from memory.memory_engine import MemoryEngine


class TechNDS01:
    """
    Raw employee agent.

    Lifecycle intended by project design:
    1. User teaches (Training)
    2. User tests agent
    3. Test outcomes become Experience
    4. Agent later answers using Training + Experience
       (Experience has higher weight)
    """

    IDENTITY = {
        "agent_id": "TECH-NDS-01",
        "name": "NDS Worker",
        "agent_type": "Employee",
        "department": "Technical",
        "role": "Trainable Technical Analyst",
        "version": "2.0.0",
        "status": "RAW"
    }

    RESPONSIBILITIES = [
        "Receive training materials from User through Manager path",
        "Store approved training in training memory",
        "Take user tests and convert results into experience",
        "Use training + experience during analysis",
        "Weight experience higher than pure training",
        "Submit structured report only to TECH-MANAGER"
    ]

    RESTRICTIONS = [
        "No hardcoded domain trading concepts",
        "Cannot invent knowledge not taught or experienced",
        "Cannot communicate with other employees",
        "Cannot communicate with Assistant",
        "Cannot execute trades",
        "Cannot modify architecture"
    ]

    def __init__(self):
        self.identity = self.IDENTITY.copy()
        self.memory_engine = MemoryEngine(agent_id=self.identity["agent_id"])
        self.training_memory: List[Dict[str, Any]] = []

    # -----------------------------
    # Training (by User)
    # -----------------------------
    def receive_training(self, training_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a training item taught by User.

        Expected example:
        {
          "title": "...",
          "content": "...",
          "source": "USER",
          "tags": ["..."]
        }
        """
        entry = {
            "id": f"TRAIN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "title": training_item.get("title", "Untitled Training"),
            "content": training_item.get("content", ""),
            "source": training_item.get("source", "USER"),
            "tags": training_item.get("tags", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.training_memory.append(entry)
        self.memory_engine.add_working(entry, meta={"type": "training"})
        return {"status": "STORED", "training_id": entry["id"]}

    def list_training(self) -> List[Dict[str, Any]]:
        return self.training_memory

    # -----------------------------
    # Testing by User -> Experience
    # -----------------------------
    def take_test(self, test_input: Dict[str, Any], user_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        User tests the agent.
        User evaluation is converted into Experience.

        test_input: the question / case given by user
        user_evaluation: {
            "score": 0..1,
            "correct": true/false,
            "feedback": "...",
            "expected": "..."
        }
        """
        experience = {
            "test_input": test_input,
            "agent_response": test_input.get("agent_response"),
            "user_evaluation": user_evaluation,
            "score": float(user_evaluation.get("score", 0)),
            "feedback": user_evaluation.get("feedback", ""),
            "timestamp": datetime.utcnow().isoformat()
        }

        exp_id = self.memory_engine.add_experience(
            content=experience,
            mission_id=test_input.get("mission_id", "USER-TEST"),
            confidence=float(user_evaluation.get("score", 0))
        )

        return {
            "status": "EXPERIENCE_CREATED",
            "experience_id": exp_id,
            "score": experience["score"]
        }

    # -----------------------------
    # Runtime usage of memory
    # -----------------------------
    def _retrieve_relevant_training(self, query: str) -> List[Dict[str, Any]]:
        q = (query or "").lower()
        if not q:
            return self.training_memory[-5:]
        hits = []
        for item in self.training_memory:
            blob = f"{item.get('title','')} {item.get('content','')} {' '.join(item.get('tags', []))}".lower()
            if q in blob:
                hits.append(item)
        return hits[-5:] if hits else self.training_memory[-3:]

    def _retrieve_relevant_experience(self, query: str) -> List[Dict[str, Any]]:
        experiences = self.memory_engine.get_experience()
        q = (query or "").lower()
        if not q:
            return experiences[-5:]
        hits = []
        for exp in experiences:
            blob = str(exp.get("content", "")).lower()
            if q in blob:
                hits.append(exp)
        return hits[-5:] if hits else experiences[-3:]

    def analyze(self, mission_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze using only taught training + lived experience.
        No hardcoded market concepts.
        Experience is weighted higher than training.
        """
        self.memory_engine.add_working(mission_input, meta={"type": "mission_input"})

        objective = str(mission_input.get("objective", ""))
        raw_input = mission_input.get("input", mission_input)
        query = f"{objective} {raw_input}"

        training_hits = self._retrieve_relevant_training(query)
        experience_hits = self._retrieve_relevant_experience(query)

        has_training = len(training_hits) > 0
        has_experience = len(experience_hits) > 0

        # Confidence model: experience-heavy
        confidence = 0.0
        if has_training:
            confidence += 0.25
        if has_experience:
            # higher weight
            avg_exp = 0.0
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
            summary = (
                "Agent is RAW. No training and no experience available yet. "
                "User must teach and test this agent before reliable analysis."
            )
            recommendation = "NO_TRADE"
            basis = "NONE"
        elif has_experience and has_training:
            summary = (
                "Response prepared from relevant training and prior experience. "
                "Experience weighted higher than training."
            )
            recommendation = "WAIT_USER_VALIDATION"
            basis = "TRAINING+EXPERIENCE"
        elif has_experience:
            summary = "Response prepared mainly from prior experience."
            recommendation = "WAIT_USER_VALIDATION"
            basis = "EXPERIENCE"
        else:
            summary = (
                "Only training is available. Experience is still weak. "
                "User testing is required to strengthen decisions."
            )
            recommendation = "WAIT_USER_VALIDATION"
            basis = "TRAINING_ONLY"

        result = {
            "agent_id": self.identity["agent_id"],
            "version": self.identity["version"],
            "mission_id": mission_input.get("mission_id"),
            "output_type": "Analysis",
            "agent_state": self.identity["status"],
            "analysis": {
                "method": "TRAINING_AND_EXPERIENCE",
                "basis": basis,
                "training_used_count": len(training_hits),
                "experience_used_count": len(experience_hits),
                "training_refs": [t.get("id") for t in training_hits],
                "experience_refs": [e.get("id") for e in experience_hits],
                "summary": summary,
                "notes": [
                    "No hardcoded domain rules are embedded in this agent.",
                    "Knowledge must come from User training and tested experience."
                ]
            },
            "confidence": confidence,
            "evidence": [
                f"Training items used: {len(training_hits)}",
                f"Experience items used: {len(experience_hits)}",
                "Experience weight > Training weight"
            ],
            "limitations": [
                "Domain skill depends on User training quality",
                "Without tests, experience remains weak",
                "No autonomous concept invention allowed"
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
