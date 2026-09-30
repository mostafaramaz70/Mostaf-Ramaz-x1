"""
Ramaz X1 Runtime Context
Version: 1.0.0
"""

from typing import Dict, Any, Optional


class RuntimeContext:
    """
    Holds shared context for the current mission execution.
    """

    def __init__(self):
        self.data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def clear(self) -> None:
        self.data.clear()

    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()
