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

from runtime.runtime import RuntimeCore
from runtime.registry import AgentRegistry
from runtime.mission import MissionManager
from runtime.logger import RuntimeLogger
from runtime.agents_setup import setup_blueprint_agents
from runtime.flow import MissionFlow

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
    mission_input: Dict[str, Any]
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
