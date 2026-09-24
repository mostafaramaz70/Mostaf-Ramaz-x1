"""
Ramaz X1 Runtime Core
Version: 1.0.0
"""

from enum import Enum, auto


class RuntimeState(Enum):
    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()
    ERROR = auto()


class RuntimeCore:
    """
    Central Runtime Controller for Ramaz X1.
    """

    def __init__(self):
        self.state = RuntimeState.INITIALIZING

    def initialize(self):
        self.state = RuntimeState.READY

    def start(self):
        if self.state == RuntimeState.READY:
            self.state = RuntimeState.RUNNING

    def pause(self):
        if self.state == RuntimeState.RUNNING:
            self.state = RuntimeState.PAUSED

    def stop(self):
        self.state = RuntimeState.STOPPED

    def status(self):
        return self.state.name
        from runtime.state import RuntimeState


class RuntimeCore:
    def __init__(self):
        self.state = RuntimeState.INITIALIZING

    def initialize(self):
        self.state = RuntimeState.READY

    def start(self):
        if self.state == RuntimeState.READY:
            self.state = RuntimeState.RUNNING

    def pause(self):
        if self.state == RuntimeState.RUNNING:
            self.state = RuntimeState.PAUSED

    def resume(self):
        if self.state == RuntimeState.PAUSED:
            self.state = RuntimeState.RUNNING

    def stop(self):
        self.state = RuntimeState.STOPPING
        self.state = RuntimeState.STOPPED

    def error(self):
        self.state = RuntimeState.ERROR

    def status(self):
        return self.state.name