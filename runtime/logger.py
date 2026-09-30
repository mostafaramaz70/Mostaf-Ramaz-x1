"""
Ramaz X1 Runtime Logger
Version: 1.0.0
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json


class RuntimeLogger:
    """
    Structured logger for all runtime events.
    Logs are immutable and traceable.
    """

    def __init__(self):
        self.logs = []

    def log(
        self,
        mission_id: str,
        agent_id: Optional[str],
        department: Optional[str],
        event: str,
        data: Optional[Dict[str, Any]] = None,
        status: str = "INFO"
    ) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "mission_id": mission_id,
            "agent_id": agent_id,
            "department": department,
            "event": event,
            "data": data or {},
            "status": status
        }
        self.logs.append(entry)
        return entry

    def get_logs(self, mission_id: Optional[str] = None) -> list:
        if mission_id:
            return [log for log in self.logs if log["mission_id"] == mission_id]
        return self.logs

    def export(self) -> str:
        return json.dumps(self.logs, indent=2, ensure_ascii=False)
