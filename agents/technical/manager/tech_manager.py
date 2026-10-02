"""
TECH-MANAGER — Technical Department Manager
Version: 2.0.0
"""

from typing import Dict, Any, List
from datetime import datetime
from agents.base_trainable_agent import BaseTrainableAgent


class TechManager(BaseTrainableAgent):
    IDENTITY = {
        "agent_id": "TECH-MANAGER",
        "name": "Technical Department Manager",
        "agent_type": "Manager",
        "department": "Technical",
        "role": "Department Head",
        "version": "2.0.0",
        "status": "ACTIVE",
    }

    def __init__(self):
        super().__init__()
        self.received_reports: List[Dict[str, Any]] = []

    def receive_report(self, report: Dict[str, Any]) -> None:
        self.received_reports.append(report)
        self.memory_engine.add_working(report, meta={"type": "employee_report", "from": report.get("agent_id")})

    def aggregate(self) -> Dict[str, Any]:
        # Manager may recall relevant approved memory while aggregating
        recall = self.recall("technical department aggregation", top_k=3)

        if not self.received_reports:
            return {
                "status": "NO_REPORTS",
                "summary": "No employee reports received",
                "confidence": 0.0,
                "memory_refs": [u.get("id") for u in recall.get("units", [])],
            }

        analyses = []
        confidences = []
        for report in self.received_reports:
            analyses.append(report.get("analysis", {}))
            confidences.append(report.get("confidence", 0.0))

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "department": "Technical",
            "manager_id": self.identity["agent_id"],
            "employee_count": len(self.received_reports),
            "analyses": analyses,
            "average_confidence": avg_confidence,
            "summary": f"Aggregated {len(self.received_reports)} employee report(s)",
            "memory_refs": [u.get("id") for u in recall.get("units", [])],
            "status": "AGGREGATED",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def generate_department_report(self, aggregated: Dict[str, Any], mission_id: str) -> Dict[str, Any]:
        return {
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
            "timestamp": datetime.utcnow().isoformat(),
        }

    def submit_to_assistant(self, report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "from": self.identity["agent_id"],
            "to": "ASSISTANT-NDS",
            "type": "DEPARTMENT_REPORT",
            "payload": report,
            "timestamp": datetime.utcnow().isoformat(),
        }
