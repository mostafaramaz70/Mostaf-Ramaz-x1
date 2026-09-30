"""
Ramaz X1 Runtime State Definitions
Version: 1.0.0
"""

from enum import Enum, auto
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class RuntimeState(Enum):
    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()


class MissionStatus(Enum):
    CREATED = auto()
    VALIDATING = auto()
    PLANNING = auto()
    ROUTING = auto()
    EXECUTING = auto()
    REVIEWING = auto()
    VOTING = auto()
    REPORTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class MissionState(TypedDict, total=False):
    runtime_id: str
    mission_id: str
    mission_input: Dict[str, Any]
    mission_objective: str
    mission_status: str
    current_phase: str
    current_node: str
    required_departments: List[str]
    active_managers: List[str]
    active_employees: List[str]
    task_registry: Dict[str, Any]
    message_registry: List[Dict[str, Any]]
    knowledge_references: List[str]
    experience_references: List[str]
    memory_references: List[str]
    discovery_references: List[str]
    agent_outputs: Dict[str, Any]
    votes: List[Dict[str, Any]]
    reports: List[Dict[str, Any]]
    logs: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    timestamps: Dict[str, str]
