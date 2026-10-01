"""
TECH-MANAGER — Technical Department Manager
Version: 1.0.0
Status: Active
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from memory.memory_engine import MemoryEngine


class TechManager:
    """
    Technical Department Manager.

    Responsibilities:
    - Receive reports from Technical employees
    - Review and aggregate analyses
    - Resolve conflicts between employee reports
    - Produce department-level report
    - Submit final department report only to Assistant (ASSISTANT-NDS)

    Rules:
    - Communicates with employees under Technical department
    - Communicates with Assistant
    - Never communicates with Fundamental employees
    - Never executes trades
    """

    IDENTITY = {
        "agent_id": "TECH-MANAGER",
        "name": "Technical Department Manager",
        "agent_type": "Manager",
        "department": "Technical",
        "role": "Department Head",
        "version": "1.0.0",
        "status": "ACTIVE"
    }

    RESPONSIBILITIES = [
        "Receive and review reports from Technical employees",
        "Aggregate multiple employee analyses",
        "Resolve conflicts in technical findings",
        "Produce department-level final report",
        "Submit report only to Assistant (ASSISTANT-NDS)"
    ]

    RESTRICTIONS = [
        "Cannot communicate with Fundamental employees",
        "Cannot execute trades",
        "Cannot modify architecture",
        "Cannot create autonomous missions",
        "Final decision authority belongs to Assistant / User"
    ]

    def __init__(self):
        self.identity = self.IDENTITY.copy()
        self.memory_engine = MemoryEngine(agent_id=self.identity["agent_id"])
        self.received_reports: List[Dict[str, Any]] = []

    def receive_report(self, report: Dict[str, Any]) -> None:
        """Receive report from a Technical employee."""
        self.received_reports.append(report)
        self.memory_engine.add_working(
            content=report,
            meta={"type": "employee_report", "from": report.get("agent_id")}
        )

    def aggregate(self) -> Dict[str, Any]:
        """
        Aggregate all received employee reports into department-level analysis.
        """
        if not self.received_reports:
            return {
                "status": "NO_REPORTS",
                "summary": "No employee reports received",
                "confidence": 0.0
            }

        analyses = []
        confidences = []

        for report in self.received_reports:
            analysis = report.get("analysis", {})
            analyses.append(analysis)
            confidences.append(report.get("confidence", 0.0))

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        aggregated = {
            "department": "Technical",
            "manager_id": self.identity["agent_id"],
            "employee_count": len(self.received_reports),
            "analyses": analyses,
            "average_confidence": avg_confidence,
            "bias": None,
            "key_levels": [],
            "summary": f"Aggregated {len(self.received_reports)} employee report(s)",
            "status": "AGGREGATED",
            "timestamp": datetime.utcnow().isoformat()
        }

        return aggregated

    def generate_department_report(self, aggregated: Dict[str, Any], mission_id: str) -> Dict[str, Any]:
        """Generate formal department report for Assistant."""
        report = {
            "report_id": f"REPORT-TECH-MANAGER-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "mission_id": mission_id,
            "agent_id": self.identity["agent_id"],
            "department": "Technical",
            "type": "DEPARTMENT_REPORT",
            "aggregated_analysis": aggregated,
            "confidence": aggregated.get("average_confidence", 0.0),
            "recommendation": None,
            "validation": "PENDING",
            "status": "COMPLETED",
            "timestamp": datetime.utcnow().isoformat()
        }
        return report

    def submit_to_assistant(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Submit department report only to Assistant."""
        return {
            "from": self.identity["agent_id"],
            "to": "ASSISTANT-NDS",
            "type": "DEPARTMENT_REPORT",
            "payload": report,
            "timestamp": datetime.utcnow().isoformat()
        }
