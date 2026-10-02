"""
Global registry of per-agent brains.
"""

from typing import Dict
from core.agent_brain import AgentBrain

_brains: Dict[str, AgentBrain] = {}


def get_agent_brain(agent_id: str) -> AgentBrain:
    if agent_id not in _brains:
        _brains[agent_id] = AgentBrain(agent_id=agent_id)
    return _brains[agent_id]
