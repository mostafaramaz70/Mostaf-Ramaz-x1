"""
Ramaz X1 Backend - FastAPI
Version: 1.1.0
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

from runtime.runtime import RuntimeCore
from runtime.registry import AgentRegistry
from runtime.mission import MissionManager
from runtime.logger import RuntimeLogger
from runtime.agents_setup import setup_blueprint_agents
from runtime.flow import MissionFlow
from runtime.state import MissionStatus
from backend.memory_store import get_agent_memory

app = FastAPI(
    title="Ramaz X1 API",
    description="Multi-Agent AI Trading Operating System",
    version="1.1.0"
)

runtime = RuntimeCore()
registry = AgentRegistry()
mission_manager = MissionManager()
logger = RuntimeLogger()
flow = MissionFlow()

setup_blueprint_agents(registry)
runtime.initialize()


class MissionRequest(BaseModel):
    objective: str
    mission_input: Dict[str, Any] = {}
    success_criteria: str = "Produce valid analysis report"
    priority: str = "MEDIUM"


class TrainingRequest(BaseModel):
    agent_id: str
    title: str = "Untitled Training"
    content: str = ""
    source: str = "USER"
    tags: List[str] = []


class ExamRecord(BaseModel):
    question: str
    expected: Optional[str] = None
    score: float = 0.0
    feedback: str = ""


class PromoteTrainingRequest(BaseModel):
    agent_id: str
    training_id: str
    exam: Optional[ExamRecord] = None
    approved_by: str = "USER"


class DiscoveryProposeRequest(BaseModel):
    agent_id: str
    content: Dict[str, Any] | str
    evidence: List[Any] = []
    confidence: float = 0.0


class DiscoveryDecisionRequest(BaseModel):
    agent_id: str
    discovery_id: str
    reason: str = ""
    decided_by: str = "USER"


@app.get("/")
def root():
    return {
        "system": "Ramaz X1",
        "version": "1.1.0",
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


@app.post("/training")
def add_training(req: TrainingRequest):
    """User teaches an agent. Stores training only."""
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    training_id = mem.add_training(
        content=req.content,
        title=req.title,
        source=req.source,
        tags=req.tags,
    )
    return {"status": "STORED", "agent_id": req.agent_id, "training_id": training_id}


@app.get("/training/{agent_id}")
def list_training(agent_id: str):
    if not registry.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_memory(agent_id).get_training()


@app.post("/experience/from-training")
def promote_training(req: PromoteTrainingRequest):
    """USER-ONLY: move training to experience after explicit approval."""
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    exam_dict = req.exam.dict() if req.exam else None
    result = mem.promote_training_to_experience(
        training_id=req.training_id,
        exam_record=exam_dict,
        approved_by=req.approved_by,
    )
    if result.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Training not found")
    return result


@app.get("/experience/{agent_id}")
def list_experience(agent_id: str):
    if not registry.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_memory(agent_id).get_experience()


@app.post("/discoveries/propose")
def propose_discovery(req: DiscoveryProposeRequest):
    """Agent proposes discovery. Stays pending until User decides."""
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    discovery_id = mem.propose_discovery(
        content=req.content,
        evidence=req.evidence,
        confidence=req.confidence,
    )
    return {
        "status": "PENDING_USER_APPROVAL",
        "agent_id": req.agent_id,
        "discovery_id": discovery_id
    }


@app.get("/discoveries/{agent_id}/pending")
def pending_discoveries(agent_id: str):
    if not registry.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_memory(agent_id).get_pending_discoveries()


@app.post("/discoveries/approve")
def approve_discovery(req: DiscoveryDecisionRequest):
    """USER-ONLY: discovery -> experience."""
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    result = mem.approve_discovery_to_experience(
        discovery_id=req.discovery_id,
        approved_by=req.decided_by,
    )
    if result.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Discovery not found")
    return result


@app.post("/discoveries/reject")
def reject_discovery(req: DiscoveryDecisionRequest):
    """USER-ONLY: reject discovery."""
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    result = mem.reject_discovery(
        discovery_id=req.discovery_id,
        reason=req.reason,
        rejected_by=req.decided_by,
    )
    if result.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Discovery not found")
    return result


@app.post("/missions", response_model=None)
def create_mission(request: MissionRequest):
    mission_id = mission_manager.create(
        objective=request.objective,
        mission_input=request.mission_input,
        success_criteria=request.success_criteria,
        priority=request.priority
    )
    logger.log(mission_id=mission_id, agent_id=None, department=None, event="MISSION_CREATED", data={"objective": request.objective})
    return {"mission_id": mission_id, "status": "CREATED", "message": "Mission created successfully"}


@app.post("/missions/run")
def run_mission(request: MissionRequest):
    mission_id = mission_manager.create(
        objective=request.objective,
        mission_input=request.mission_input,
        success_criteria=request.success_criteria,
        priority=request.priority
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

    final_state = flow.run(initial_state)
    final_status = final_state.get("mission_status", "UNKNOWN")
    try:
        mission_manager.update_status(mission_id, MissionStatus[final_status])
    except Exception:
        pass

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
