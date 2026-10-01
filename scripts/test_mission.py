"""
Ramaz X1 - First Test Mission Runner
Run from project root:
    py scripts/test_mission.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from runtime.flow import MissionFlow
from runtime.state import MissionStatus
from datetime import datetime
import uuid


def run_test_mission():
    print("=" * 50)
    print("Ramaz X1 — First Test Mission")
    print("=" * 50)

    flow = MissionFlow()
    mission_id = f"MISSION-{str(uuid.uuid4())[:8].upper()}"

    initial_state = {
        "runtime_id": str(uuid.uuid4()),
        "mission_id": mission_id,
        "mission_input": {
            "symbol": "EURUSD",
            "timeframe": "M1",
            "context": "Test mission for TECH-NDS-01"
        },
        "mission_objective": "Perform NDS technical analysis on EURUSD",
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

    print(f"\nMission ID: {mission_id}")
    print(f"Objective: {initial_state['mission_objective']}")
    print("\nRunning Mission Flow...\n")

    final_state = flow.run(initial_state)

    print("-" * 50)
    print(f"Status: {final_state.get('mission_status')}")
    print(f"Final Node: {final_state.get('current_node')}")
    print(f"Active Employees: {final_state.get('active_employees')}")
    print(f"Active Managers: {final_state.get('active_managers')}")
    print(f"Errors: {final_state.get('errors')}")
    print(f"\nAgent Outputs: {list(final_state.get('agent_outputs', {}).keys())}")
    print(f"Reports Count: {len(final_state.get('reports', []))}")
    print(f"\nTimestamps:")
    for node, ts in final_state.get("timestamps", {}).items():
        print(f"  {node}: {ts}")
    print("=" * 50)

    return final_state


if __name__ == "__main__":
    run_test_mission()
