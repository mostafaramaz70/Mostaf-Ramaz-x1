"""
ASSISTANT-NDS — Deputy / معاون
Version: 1.0.0
Status: Active

Role in Blueprint:
User
  └── Assistant (NDS)
        ├── Technical Department Manager
        └── Fundamental Department Manager
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from memory.memory_engine import MemoryEngine


class AssistantNDS:
    """
    Assistant (معاون) — Deputy Decision Engine.

    Responsibilities:
    - Receive department reports from Managers only
    - Compare and resolve conflicts between departments
    - Perform independent final analysis
    - Issue final signal: Buy / Sell / No Trade
    - Send final decision only to User (Founder)

    Rules:
    - Communicates with Department Managers
    - Communicates with User
    - Never communicates with Employees directly
    - Never executes trades automatically
    - Final operational authority after departments
    """

    IDENTITY = {
        "agent_id": "ASSISTANT-NDS",
        "name": "Assistant NDS",
        "agent_type": "Assistant",
        "department": "Organization",
        "role": "Deputy Decision Engine",
        "version": "1.0.0",
        "status": "ACTIVE"
    }

    RESPONSIBILITIES = [
        "Receive reports from Technical and Fundamental Managers",
        "Compare department findings and resolve conflicts",
        "Perform independent final synthesis",
        "Issue final signal: Buy / Sell / No Trade",
        "Send final decision only to User",
        "Maintain decision rationale and confidence"
    ]

    RESTRICTIONS = [
        "Cannot communicate with Employees directly",
        "Cannot execute trades",
        "Cannot modify architecture or knowledge without User approval",
        "Cannot override User final authority",
        "Cannot create autonomous missions without User request"
    ]

    def __init__(self):
        self.identity = self.IDENTITY.copy()
        self.memory_engine = MemoryEngine(agent_id=self.identity["agent_id"])
        self.department_reports: List[Dict[str, Any]] = []

    def receive_department_report(self, report: Dict[str, Any]) -> None:
        """Receive report from a Department Manager."""
        self.department_reports.append(report)
        self.memory_engine.add_working(
            content=report,
            meta={
                "type": "department_report",
                "from": report.get("agent_id"),
                "department": report.get("department")
            }
        )

    def compare_reports(self) -> Dict[str, Any]:
        """Compare department reports and detect conflicts."""
        if not self.department_reports:
            return {
                "status": "NO_REPORTS",
                "summary": "No department reports received",
                "conflicts": [],
                "confidence": 0.0
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
            "timestamp": datetime.utcnow().isoformat()
        }

    def decide(self, comparison: Dict[str, Any], mission_id: str) -> Dict[str, Any]:
        """
        Produce final decision signal.
        Current version is structural (no live market model yet).
        """
        signal = "NO_TRADE"
        rationale = "Insufficient confirmed edge for trade entry."

        if comparison.get("status") == "NO_REPORTS":
            rationale = "No department reports available."
        elif comparison.get("average_confidence", 0) >= 0.7:
            signal = "NO_TRADE"
            rationale = "Reports received, but live market confirmation layer not connected yet."

        decision = {
            "decision_id": f"DECISION-{self.identity['agent_id']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "mission_id": mission_id,
            "agent_id": self.identity["agent_id"],
            "signal": signal,  # Buy | Sell | No Trade
            "confidence": comparison.get("average_confidence", 0.0),
            "rationale": rationale,
            "comparison": comparison,
            "departments_used": comparison.get("departments_received", []),
            "status": "COMPLETED",
            "timestamp": datetime.utcnow().isoformat()
        }

        self.memory_engine.add_experience(
            content=decision,
            mission_id=mission_id,
            confidence=decision["confidence"]
        )

        return decision

    def submit_to_user(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Submit final decision only to User."""
        return {
            "from": self.identity["agent_id"],
            "to": "USER",
            "type": "FINAL_DECISION",
            "payload": decision,
            "timestamp": datetime.utcnow().isoformat()
        }
