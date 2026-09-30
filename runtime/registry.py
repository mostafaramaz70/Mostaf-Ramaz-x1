"""
Ramaz X1 Agent Registry
Version: 1.0.0
"""

from typing import Dict, Any, Optional, List


class AgentRegistry:
    """
    Registry of all available agents (managers and employees).
    """

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        department: str,
        role: str,
        version: str = "1.0",
        status: str = "ACTIVE"
    ) -> None:
        self.agents[agent_id] = {
            "agent_id": agent_id,
            "name": name,
            "agent_type": agent_type,  # Manager or Employee
            "department": department,
            "role": role,
            "version": version,
            "status": status
        }

    def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self.agents.get(agent_id)

    def get_by_department(self, department: str) -> List[Dict[str, Any]]:
        return [a for a in self.agents.values() if a["department"] == department]

    def get_managers(self) -> List[Dict[str, Any]]:
        return [a for a in self.agents.values() if a["agent_type"] == "Manager"]

    def get_employees(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        employees = [a for a in self.agents.values() if a["agent_type"] == "Employee"]
        if department:
            return [e for e in employees if e["department"] == department]
        return employees

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self.agents.values())
