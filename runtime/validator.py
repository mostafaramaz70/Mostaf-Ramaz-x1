"""
Ramaz X1 Runtime Validator
Version: 1.0.0
"""

from typing import Dict, Any, Tuple


class MissionValidator:
    """
    Validates incoming missions before execution.
    """

    REQUIRED_FIELDS = [
        "mission_objective",
        "mission_input",
        "success_criteria",
        "priority",
        "constraints",
        "required_output",
        "requesting_identity",
        "timestamp"
    ]

    def validate(self, mission_data: Dict[str, Any]) -> Tuple[bool, list]:
        errors = []

        for field in self.REQUIRED_FIELDS:
            if field not in mission_data or mission_data[field] is None:
                errors.append(f"Missing required field: {field}")

        if "priority" in mission_data:
            if mission_data["priority"] not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                errors.append("Invalid priority value")

        is_valid = len(errors) == 0
        return is_valid, errors
