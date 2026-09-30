"""
Ramaz X1 Runtime Dispatcher
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from runtime.registry import AgentRegistry


class Dispatcher:
    """
    Routes missions and tasks to correct departments and agents.
    Enforces hierarchy: Employees only talk to their Manager.
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def route_to_department(self, mission: Dict[str, Any], department: str) -> Optional[str]:
        managers = [
            a for a in self.registry.get_by_department(department)
            if a["agent_type"] == "Manager"
        ]
        if not managers:
            return None
        return managers[0]["agent_id"]

    def route_to_employees(self, department: str) -> list:
        return self.registry.get_employees(department)

    def can_communicate(self, sender_id: str, receiver_id: str) -> bool:
        """
        Communication rules:
        - Employees can only talk to their own Manager
        - Employees cannot talk to each other
        - Employees cannot talk to Assistant
        - Managers talk to Assistant
        - Assistant talks to User
        """
        sender = self.registry.get(sender_id)
        receiver = self.registry.get(receiver_id)

        if not sender or not receiver:
            return False

        # Employee rules
        if sender["agent_type"] == "Employee":
            if receiver["agent_type"] != "Manager":
                return False
            if sender["department"] != receiver["department"]:
                return False
            return True

        return True
