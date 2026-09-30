"""
Ramaz X1 Runtime Scheduler
Version: 1.0.0
"""

from typing import List, Dict, Any
from datetime import datetime


class Scheduler:
    """
    Simple task scheduler for mission execution order.
    """

    def __init__(self):
        self.queue: List[Dict[str, Any]] = []

    def add_task(self, task: Dict[str, Any], priority: int = 5) -> None:
        task["priority"] = priority
        task["queued_at"] = datetime.utcnow().isoformat()
        self.queue.append(task)
        self.queue.sort(key=lambda x: x["priority"])

    def next_task(self) -> Dict[str, Any] | None:
        if not self.queue:
            return None
        return self.queue.pop(0)

    def pending_count(self) -> int:
        return len(self.queue)
