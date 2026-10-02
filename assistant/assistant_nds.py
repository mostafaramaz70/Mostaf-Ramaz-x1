"""
ASSISTANT-NDS — Deputy
Version: 2.0.0
"""

from typing import Dict, Any, List
from datetime import datetime
from agents.base_trainable_agent import BaseTrainableAgent


class AssistantNDS(BaseTrainableAgent):
    IDENTITY = {
        "agent_id": "ASSISTANT-NDS",
        "name": "Assistant NDS",
        "agent_type": "Assistant",
        "department": "Organization",
        "role": "Deputy Decision Engine",
        "version": "2.0.0",
        "status": "ACTIVE",
    }

    def __init__(self):
        super().__init__()
        self.department_reports: List[Dict[str, Any]] = []

    def receive_department_report(self, report: Dict[str, Any]) -> None:
        self.department_reports.append(report)
        self.memory_engine.add_working(
            report,
            meta={"type": "department_report", "from": report.get("agent_id"), "department": report.get("department")},
        )

    def compare_reports(self) -> Dict[str, Any]:
        recall = self.recall("final decision department comparison", top_k=3)

        if not self.department_reports:
            return {
                "status": "NO_REPORTS",
                "summary": "No department reports received",
                "conflicts": [],
                "confidence": 0.0,
                "memory_refs": [u.get("id") for u in recall.get("units", [])],
            }

        departments = {}
        confidences = []
        for report in self.department_reports:
            dept = report.get("department", "UNKNOWN")
            departments[dept] = report
            confidences.append(report.get("confidence", 0.0))

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "status": "COMPARED",
            "departments_received": list(departments.keys()),
            "report_count": len(self.department_reports),
            "average_confidence": avg_confidence,
            "conflicts": [],
            "summary": f"Compared {len(self.department_reports)} department report(s)",
            "memory_refs": [u.get("id") for u in recall.get("units", [])],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def decide(self, comparison: Dict[str, Any], mission_id: str) -> Dict[str, Any]:
        signal = "NO_TRADE"
        rationale = "Insufficient confirmed edge for trade entry."

        if comparison.get("status") == "NO_REPORTS":
            rationale = "No department reports available."
        elif comparison.get("average_confidence", 0) >= 0.7:
            rationale = "Reports received, but live confirmation / user-approved experience may still be limited."

        decision = {
            "decision_id": f"DECISION-{self.identity['agent_id']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "mission_id": mission_id,
            "agent_id": self.identity["agent_id"],
            "signal": signal,
            "confidence": comparison.get("average_confidence", 0.0),
            "rationale": rationale,
            "comparison": comparison,
            "departments_used": comparison.get("departments_received", []),
            "status": "COMPLETED",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # NOTE: do NOT auto-write experience. User approval path only.
        return decision

    def submit_to_user(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "from": self.identity["agent_id"],
            "to": "USER",
            "type": "FINAL_DECISION",
            "payload": decision,
            "timestamp": datetime.utcnow().isoformat(),
        }
