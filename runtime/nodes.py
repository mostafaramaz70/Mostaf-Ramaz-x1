"""
Ramaz X1 Runtime Nodes
Version: 1.0.0

Standard Mission Flow Nodes based on frozen Runtime Design.
"""

from typing import Dict, Any
from runtime.state import MissionStatus
from datetime import datetime


def entry_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Entry node - receive mission."""
    state["current_node"] = "entry"
    state["mission_status"] = MissionStatus.CREATED.name
    if "timestamps" not in state:
        state["timestamps"] = {}
    state["timestamps"]["entry"] = datetime.utcnow().isoformat()
    return state


def validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mission validation node."""
    state["current_node"] = "validation"
    state["mission_status"] = MissionStatus.VALIDATING.name
    state["timestamps"]["validation"] = datetime.utcnow().isoformat()
    return state


def planning_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mission planning node."""
    state["current_node"] = "planning"
    state["mission_status"] = MissionStatus.PLANNING.name
    state["timestamps"]["planning"] = datetime.utcnow().isoformat()
    # Default: route to Technical department for NDS analysis
    state["required_departments"] = ["Technical"]
    state["active_employees"] = ["TECH-NDS-01"]
    return state


def routing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Department routing node."""
    state["current_node"] = "routing"
    state["mission_status"] = MissionStatus.ROUTING.name
    state["timestamps"]["routing"] = datetime.utcnow().isoformat()
    state["active_managers"] = ["TECH-MANAGER"]
    return state


def manager_coordination_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Manager coordination node."""
    state["current_node"] = "manager_coordination"
    state["mission_status"] = MissionStatus.EXECUTING.name
    state["timestamps"]["manager_coordination"] = datetime.utcnow().isoformat()
    return state


def employee_execution_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Employee execution node - runs TECH-NDS-01."""
    state["current_node"] = "employee_execution"
    state["timestamps"]["employee_execution"] = datetime.utcnow().isoformat()

    active_employees = state.get("active_employees", [])
    if "TECH-NDS-01" in active_employees:
        try:
            from agents.technical.workers.tech_nds_01 import TechNDS01

            agent = TechNDS01()
            mission_input = {
                "mission_id": state.get("mission_id"),
                "objective": state.get("mission_objective"),
                "input": state.get("mission_input", {})
            }
            analysis_result = agent.analyze(mission_input)
            report = agent.generate_report(analysis_result)
            submission = agent.submit_to_manager(report)

            if "agent_outputs" not in state:
                state["agent_outputs"] = {}
            state["agent_outputs"]["TECH-NDS-01"] = {
                "analysis": analysis_result,
                "report": report,
                "submission": submission
            }
        except Exception as e:
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append({
                "agent_id": "TECH-NDS-01",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    return state


def output_collection_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Collect outputs from employees and process via TECH-MANAGER."""
    state["current_node"] = "output_collection"
    state["mission_status"] = MissionStatus.REVIEWING.name
    state["timestamps"]["output_collection"] = datetime.utcnow().isoformat()

    # TECH-MANAGER receives employee reports and aggregates
    agent_outputs = state.get("agent_outputs", {})
    if "TECH-NDS-01" in agent_outputs:
        try:
            from agents.technical.manager.tech_manager import TechManager

            manager = TechManager()
            employee_report = agent_outputs["TECH-NDS-01"].get("report", {})
            manager.receive_report(employee_report)

            aggregated = manager.aggregate()
            dept_report = manager.generate_department_report(
                aggregated=aggregated,
                mission_id=state.get("mission_id", "UNKNOWN")
            )
            submission = manager.submit_to_assistant(dept_report)

            state["agent_outputs"]["TECH-MANAGER"] = {
                "aggregated": aggregated,
                "department_report": dept_report,
                "submission": submission
            }
        except Exception as e:
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append({
                "agent_id": "TECH-MANAGER",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    return state


def voting_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Voting node when required."""
    state["current_node"] = "voting"
    state["mission_status"] = MissionStatus.VOTING.name
    state["timestamps"]["voting"] = datetime.utcnow().isoformat()
    return state


def report_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mission report."""
    state["current_node"] = "report_generation"
    state["mission_status"] = MissionStatus.REPORTING.name
    state["timestamps"]["report_generation"] = datetime.utcnow().isoformat()

    agent_outputs = state.get("agent_outputs", {})
    reports = []

    # Prefer department report from manager
    if "TECH-MANAGER" in agent_outputs:
        dept_report = agent_outputs["TECH-MANAGER"].get("department_report")
        if dept_report:
            reports.append(dept_report)

    # Also keep employee reports
    for agent_id, output in agent_outputs.items():
        if agent_id != "TECH-MANAGER" and "report" in output:
            reports.append(output["report"])

    state["reports"] = reports
    return state


def logging_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Write execution logs."""
    state["current_node"] = "logging"
    state["timestamps"]["logging"] = datetime.utcnow().isoformat()
    return state


def completion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mark mission as completed."""
    state["current_node"] = "completion"
    state["mission_status"] = MissionStatus.COMPLETED.name
    state["timestamps"]["completion"] = datetime.utcnow().isoformat()
    return state


def error_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle unrecoverable errors."""
    state["current_node"] = "error"
    state["mission_status"] = MissionStatus.FAILED.name
    state["timestamps"]["error"] = datetime.utcnow().isoformat()
    return state
