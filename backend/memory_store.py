"""
Shared in-memory store for agent memories in backend process.
"""

from typing import Dict
from memory.memory_engine import MemoryEngine

_agent_memories: Dict[str, MemoryEngine] = {}


def get_agent_memory(agent_id: str) -> MemoryEngine:
    if agent_id not in _agent_memories:
        _agent_memories[agent_id] = MemoryEngine(agent_id=agent_id)
    return _agent_memories[agent_id]


def list_agent_ids():
    return list(_agent_memories.keys())
