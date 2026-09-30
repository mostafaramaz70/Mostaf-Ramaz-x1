"""
Ramaz X1 Mission Flow
Version: 1.0.0

Standard Mission Flow based on frozen Runtime Design:

1. Entry
2. Validation
3. Planning
4. Routing
5. Manager Coordination
6. Employee Execution
7. Output Collection
8. Voting (if required)
9. Report Generation
10. Logging
11. Completion
"""

from typing import Dict, Any, Callable, List
from runtime.nodes import (
    entry_node,
    validation_node,
    planning_node,
    routing_node,
    manager_coordination_node,
    employee_execution_node,
    output_collection_node,
    voting_node,
    report_generation_node,
    logging_node,
    completion_node,
    error_node,
)


class MissionFlow:
    """
    Orchestrates the standard mission execution flow.
    """

    def __init__(self):
        self.nodes: List[Callable] = [
            entry_node,
            validation_node,
            planning_node,
            routing_node,
            manager_coordination_node,
            employee_execution_node,
            output_collection_node,
            voting_node,
            report_generation_node,
            logging_node,
            completion_node,
        ]
        self.error_node = error_node

    def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        state = initial_state.copy()

        try:
            for node in self.nodes:
                state = node(state)
                if state.get("mission_status") == "FAILED":
                    return self.error_node(state)
            return state
        except Exception as e:
            state["errors"] = state.get("errors", [])
            state["errors"].append({"error": str(e)})
            return self.error_node(state)

    def get_flow_order(self) -> List[str]:
        return [node.__name__ for node in self.nodes]
