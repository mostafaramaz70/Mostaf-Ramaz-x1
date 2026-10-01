"""
Ramaz X1 Runtime Dispatcher
Version: 1.0.0

Enforces Blueprint hierarchy and communication rules:
- Employees → only their Department Manager
- Employees never talk to each other
- Employees never talk to Assistant
- Managers → Assistant
- Assistant → User
"""

from typing import Dict, Any, Optional, List
from runtime.registry import AgentRegistry


class Dispatcher:
    """
    Routes missions and tasks to correct departments and agents.
    Strictly enforces communication hierarchy from Blueprint.
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

    def route_to_employees(self, department: str) -> List[Dict[str, Any]]:
        return self.registry.get_employees(department)

    def get_assistant(self) -> Optional[Dict[str, Any]]:
        for agent in self.registry.list_all():
            if agent["agent_type"] == "Assistant":
                return agent
        return None

    def can_communicate(self, sender_id: str, receiver_id: str) -> bool:
        """
        Strict communication rules from Blueprint:

        1. Employee → only own Department Manager
        2. Employee ✗ Employee
        3. Employee ✗ Assistant
        4. Manager → Assistant
        5. Assistant → User (external)
        """
        sender = self.registry.get(sender_id)
        receiver = self.registry.get(receiver_id)

        if not sender:
            return False

        # Receiver can be User (external)
        if receiver_id == "USER":
            return sender["agent_type"] == "Assistant"

        if not receiver:
            return False

        sender_type = sender["agent_type"]
        receiver_type = receiver["agent_type"]

        # Rule 1 & 2 & 3: Employee restrictions
        if sender_type == "Employee":
            if receiver_type != "Manager":
                return False
            if sender["department"] != receiver["department"]:
                return False
            return True

        # Rule 4: Manager → Assistant
        if sender_type == "Manager":
            return receiver_type == "Assistant"

        # Assistant can receive from Managers and send to User
        if sender_type == "Assistant":
            return True

        return False

    def get_allowed_receivers(self, sender_id: str) -> List[str]:
        """Return list of agent_ids this sender is allowed to communicate with."""
        sender = self.registry.get(sender_id)
        if not sender:
            return []

        allowed = []

        if sender["agent_type"] == "Employee":
            for agent in self.registry.get_by_department(sender["department"]):
                if agent["agent_type"] == "Manager":
                    allowed.append(agent["agent_id"])

        elif sender["agent_type"] == "Manager":
            assistant = self.get_assistant()
            if assistant:
                allowed.append(assistant["agent_id"])

        elif sender["agent_type"] == "Assistant":
            allowed.append("USER")

        return allowed
