"""
Ramaz X1 Runtime Configuration
Version: 1.0.0
"""

from typing import Dict, Any
import os


class RuntimeConfig:
    """
    Central configuration loader.
    Secrets must come from environment variables only.
    """

    def __init__(self):
        self.config: Dict[str, Any] = {
            "runtime_version": "1.0.0",
            "language": "python",
            "framework": "langgraph",
            "primary_llm": "openai",
            "log_level": "INFO",
            "max_retries": 3,
            "timeout_seconds": 300
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def load_from_env(self) -> None:
        self.config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
        self.config["log_level"] = os.getenv("LOG_LEVEL", "INFO")
