"""
Ramaz X1 Backend - FastAPI
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add project root to path so runtime can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from runtime.runtime import RuntimeCore
from runtime.registry import AgentRegistry
from runtime.mission import MissionManager
from runtime.logger import RuntimeLogger
from runtime.agents_setup import setup_blueprint_agents
from runtime.flow import MissionFlow
from runtime.state import MissionStatus

app = FastAPI(
    title="Ramaz X1 API",
    description="Multi-Agent AI Trading Operating System",
    version="1.0.0"
)

# Initialize core components
runtime = RuntimeCore()
registry = AgentRegistry()
mission_manager = MissionManager()
logger = RuntimeLogger()
flow = MissionFlow()

# Setup agents from Blueprint
setup_blueprint_agents(registry)
runtime.initialize()


class MissionRequest(BaseModel):
    objective: str
    mission_input: Dict[str, Any] = {}
    success_criteria: str = "Produce valid analysis report"
    priority: str = "MEDIUM"


class MissionResponse(BaseModel):
    mission_id: str
    status: str
    message: str


@app.get("/")
def root():
    return {
        "system": "Ramaz X1",
        "version": "1.0.0",
        "status": runtime.status(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
def health():
    return {"status": "ok", "runtime": runtime.status()}


@app.get("/agents")
def list_agents():
    return registry.list_all()


@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    agent = registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.post("/missions", response_model=MissionResponse)
def create_mission(request: MissionRequest):
    mission_id = mission_manager.create(
        objective=request.objective,
        mission_input=request.mission_input,
        success_criteria=request.success_criteria,
        priority=request.priority
    )

    logger.log(
        mission_id=mission_id,
        agent_id=None,
        department=None,
        event="MISSION_CREATED",
        data={"objective": request.objective}
    )

    return MissionResponse(
        mission_id=mission_id,
        status="CREATED",
        message="Mission created successfully"
    )


@app.post("/missions/run")
def run_mission(request: MissionRequest):
    """
    Create and fully execute a mission through the Mission Flow.
    Runs: Entry → Validation → Planning → Routing → Manager → Employee (TECH-NDS-01)
          → Output Collection (TECH-MANAGER) → Report → Logging → Completion
    """
    mission_id = mission_manager.create(
        objective=request.objective,
        mission_input=request.mission_input,
        success_criteria=request.success_criteria,
        priority=request.priority
    )

    logger.log(
        mission_id=mission_id,
        agent_id=None,
        department=None,
        event="MISSION_RUN_STARTED",
        data={"objective": request.objective}
    )

    initial_state = {
        "runtime_id": runtime.runtime_id,
        "mission_id": mission_id,
        "mission_input": request.mission_input,
        "mission_objective": request.objective,
        "mission_status": MissionStatus.CREATED.name,
        "current_phase": "CREATED",
        "current_node": "entry",
        "required_departments": [],
        "active_managers": [],
        "active_employees": [],
        "task_registry": {},
        "message_registry": [],
        "knowledge_references": [],
        "experience_references": [],
        "memory_references": [],
        "discovery_references": [],
        "agent_outputs": {},
        "votes": [],
        "reports": [],
        "logs": [],
        "errors": [],
        "timestamps": {"created": datetime.utcnow().isoformat()}
    }

    # Execute full mission flow
    final_state = flow.run(initial_state)

    # Update mission status
    final_status = final_state.get("mission_status", "UNKNOWN")
    try:
        mission_manager.update_status(mission_id, MissionStatus[final_status])
    except Exception:
        pass

    logger.log(
        mission_id=mission_id,
        agent_id=None,
        department=None,
        event="MISSION_RUN_COMPLETED",
        data={
            "status": final_status,
            "nodes": list(final_state.get("timestamps", {}).keys()),
            "errors": final_state.get("errors", [])
        }
    )

    return {
        "mission_id": mission_id,
        "status": final_status,
        "current_node": final_state.get("current_node"),
        "active_employees": final_state.get("active_employees", []),
        "active_managers": final_state.get("active_managers", []),
        "agent_outputs": final_state.get("agent_outputs", {}),
        "reports": final_state.get("reports", []),
        "errors": final_state.get("errors", []),
        "timestamps": final_state.get("timestamps", {})
    }


@app.get("/missions")
def list_missions():
    return mission_manager.list_missions()


@app.get("/missions/{mission_id}")
def get_mission(mission_id: str):
    mission = mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@app.get("/logs")
def get_logs(mission_id: Optional[str] = None):
    return logger.get_logs(mission_id)
