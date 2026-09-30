"""
Ramaz X1 Mission Manager
Version: 1.0.0
"""

from runtime.state import MissionStatus
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


class MissionManager:
    """
    Handles mission lifecycle: creation, status updates, completion.
    """

    def __init__(self):
        self.missions: Dict[str, Dict[str, Any]] = {}

    def create(
        self,
        objective: str,
        mission_input: Dict[str, Any],
        success_criteria: str,
        priority: str = "MEDIUM",
        constraints: Optional[list] = None,
        required_output: str = "report",
        requesting_identity: str = "USER"
    ) -> str:
        mission_id = f"MISSION-{str(uuid.uuid4())[:8].upper()}"
        mission = {
            "mission_id": mission_id,
            "mission_objective": objective,
            "mission_input": mission_input,
            "success_criteria": success_criteria,
            "priority": priority,
            "constraints": constraints or [],
            "required_output": required_output,
            "requesting_identity": requesting_identity,
            "status": MissionStatus.CREATED.name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "reports": [],
            "errors": []
        }
        self.missions[mission_id] = mission
        return mission_id

    def update_status(self, mission_id: str, status: MissionStatus) -> bool:
        if mission_id not in self.missions:
            return False
        self.missions[mission_id]["status"] = status.name
        self.missions[mission_id]["updated_at"] = datetime.utcnow().isoformat()
        return True

    def get(self, mission_id: str) -> Optional[Dict[str, Any]]:
        return self.missions.get(mission_id)

    def list_missions(self) -> list:
        return list(self.missions.values())
