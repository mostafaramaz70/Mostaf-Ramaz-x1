"""
Ramaz X1 Backend - FastAPI
Version: 1.3.0
"""

import sys
from pathlib import Path

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
from backend.memory_store import get_agent_memory
from core.brain_registry import get_agent_brain

app = FastAPI(
    title="Ramaz X1 API",
    description="Multi-Agent AI Trading Operating System",
    version="1.3.0",
)

runtime = RuntimeCore()
registry = AgentRegistry()
mission_manager = MissionManager()
logger = RuntimeLogger()
flow = MissionFlow()
setup_blueprint_agents(registry)
runtime.initialize()

VISUAL_INTAKE: List[Dict[str, Any]] = []


class MissionRequest(BaseModel):
    objective: str = "Visual mission intake"
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


class AttachModelRequest(BaseModel):
    agent_id: str
    name: str
    provider: str
    model_id: str
    role: str = "primary"
    meta: Dict[str, Any] = {}


class RecallRequest(BaseModel):
    agent_id: str
    query: str
    top_k: int = 5
    kinds: Optional[List[str]] = None


class PromptPackRequest(BaseModel):
    agent_id: str
    task: str
    query: str
    top_k: int = 5


class VisualMissionRequest(BaseModel):
    source_note: Optional[str] = None
    files: List[Dict[str, Any]] = []  # [{name, type, size, data_url?}]
    captured_by: str = "USER"  # USER | AGENT
    source_type: str = "SCREENSHOT"  # SCREENSHOT | CHART_CAPTURE | FEED
    meta: Dict[str, Any] = {}


@app.get("/")
def root():
    return {
        "system": "Ramaz X1",
        "version": "1.3.0",
        "status": runtime.status(),
        "timestamp": datetime.utcnow().isoformat(),
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


@app.post("/missions/visual")
def visual_mission_intake(req: VisualMissionRequest):
    """Mission intake by screenshot / chart capture / source feed (not text form)."""
    item = {
        "intake_id": f"VIS-{uuid.uuid4().hex[:8].upper()}",
        "source_note": req.source_note,
        "files": req.files,
        "captured_by": req.captured_by,
        "source_type": req.source_type,
        "meta": req.meta,
        "created_at": datetime.utcnow().isoformat(),
        "status": "RECEIVED",
    }
    VISUAL_INTAKE.append(item)

    # Optionally create a mission envelope around visual intake
    mission_id = mission_manager.create(
        objective=req.source_note or "Visual mission intake",
        mission_input={
            "visual_intake_id": item["intake_id"],
            "source_type": req.source_type,
            "files": req.files,
            "meta": req.meta,
        },
        success_criteria="Analyze visual intake through organization flow",
        priority="MEDIUM",
    )
    item["mission_id"] = mission_id

    logger.log(
        mission_id=mission_id,
        agent_id=None,
        department=None,
        event="VISUAL_MISSION_INTAKE",
        data={"intake_id": item["intake_id"], "files": len(req.files)},
    )

    return {"status": "RECEIVED", "intake": item}


@app.get("/missions/visual")
def list_visual_intakes():
    return VISUAL_INTAKE


@app.post("/models/attach")
def attach_model(req: AttachModelRequest):
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    brain = get_agent_brain(req.agent_id)
    model = brain.attach_model(
        name=req.name,
        provider=req.provider,
        model_id=req.model_id,
        role=req.role,
        meta=req.meta,
    )
    return {"status": "ATTACHED", "agent_id": req.agent_id, "model": model}


@app.get("/models/{agent_id}")
def list_models(agent_id: str):
    if not registry.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_brain(agent_id).list_models()


@app.post("/memory/recall")
def recall_memory(req: RecallRequest):
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_brain(req.agent_id).recall(query=req.query, top_k=req.top_k, kinds=req.kinds)


@app.post("/memory/prompt-pack")
def prompt_pack(req: PromptPackRequest):
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_brain(req.agent_id).build_model_prompt(task=req.task, query=req.query, top_k=req.top_k)


@app.post("/training")
def add_training(req: TrainingRequest):
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    training_id = mem.add_training(content=req.content, title=req.title, source=req.source, tags=req.tags)

    brain = get_agent_brain(req.agent_id)
    units = brain.remember_training(
        title=req.title,
        content=req.content,
        source_id=training_id,
        meta={"source": req.source, "tags": req.tags},
    )

    return {
        "status": "STORED",
        "agent_id": req.agent_id,
        "training_id": training_id,
        "rag_units": len(units),
    }


@app.get("/training/{agent_id}")
def list_training(agent_id: str):
    if not registry.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_memory(agent_id).get_training()


@app.post("/experience/from-training")
def promote_training(req: PromoteTrainingRequest):
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

    if result.get("status") == "APPROVED":
        training_items = mem.get_training()
        training = next((t for t in training_items if t["id"] == req.training_id), None)
        if training:
            brain = get_agent_brain(req.agent_id)
            brain.remember_experience(
                title=f"EXP from {training.get('title')}",
                content=str(training.get("content", "")),
                source_id=result.get("experience_id"),
                meta={"approved_by": req.approved_by, "from_training": req.training_id},
            )

    return result


@app.get("/experience/{agent_id}")
def list_experience(agent_id: str):
    if not registry.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_memory(agent_id).get_experience()


@app.post("/discoveries/propose")
def propose_discovery(req: DiscoveryProposeRequest):
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    discovery_id = mem.propose_discovery(content=req.content, evidence=req.evidence, confidence=req.confidence)

    brain = get_agent_brain(req.agent_id)
    brain.remember_discovery_pending(
        title=f"Discovery {discovery_id}",
        content=str(req.content),
        source_id=discovery_id,
        meta={"confidence": req.confidence},
    )

    return {"status": "PENDING_USER_APPROVAL", "agent_id": req.agent_id, "discovery_id": discovery_id}


@app.get("/discoveries/{agent_id}/pending")
def pending_discoveries(agent_id: str):
    if not registry.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return get_agent_memory(agent_id).get_pending_discoveries()


@app.post("/discoveries/approve")
def approve_discovery(req: DiscoveryDecisionRequest):
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    result = mem.approve_discovery_to_experience(discovery_id=req.discovery_id, approved_by=req.decided_by)
    if result.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Discovery not found")

    if result.get("status") == "APPROVED":
        brain = get_agent_brain(req.agent_id)
        brain.remember_experience(
            title=f"Approved discovery {req.discovery_id}",
            content=f"User-approved discovery {req.discovery_id}",
            source_id=result.get("experience_id"),
            meta={"from_discovery": req.discovery_id, "approved_by": req.decided_by},
        )

    return result


@app.post("/discoveries/reject")
def reject_discovery(req: DiscoveryDecisionRequest):
    if not registry.get(req.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    mem = get_agent_memory(req.agent_id)
    result = mem.reject_discovery(discovery_id=req.discovery_id, reason=req.reason, rejected_by=req.decided_by)
    if result.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Discovery not found")
    return result


@app.post("/missions/run")
def run_mission(request: MissionRequest):
    mission_id = mission_manager.create(
        objective=request.objective,
        mission_input=request.mission_input,
        success_criteria=request.success_criteria,
        priority=request.priority,
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
        "timestamps": {"created": datetime.utcnow().isoformat()},
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
        "agent_outputs": final_state.get("agent_outputs", {}),
        "reports": final_state.get("reports", []),
        "errors": final_state.get("errors", []),
        "timestamps": final_state.get("timestamps", {}),
    }


@app.get("/missions")
def list_missions():
    return mission_manager.list_missions()


@app.get("/logs")
def get_logs(mission_id: Optional[str] = None):
    return logger.get_logs(mission_id)
