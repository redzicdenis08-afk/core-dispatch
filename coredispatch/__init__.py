"""core-dispatch: an open-source framework for AI voice-dispatch workflows.

Missed-call intake, qualifying callbacks, booking, and follow-up, built around
pluggable provider adapters so you can bring your own voice, LLM, storage,
calendar, and payment providers.
"""
from coredispatch.callbacks import CallbackQueue, CallWindow
from coredispatch.config import DispatchConfig
from coredispatch.dispatcher import Dispatcher
from coredispatch.models import (
    Appointment,
    CallOutcome,
    CallResult,
    DispatchStage,
    Lead,
)

__version__ = "0.1.0"
__all__ = [
    "Dispatcher",
    "DispatchConfig",
    "CallbackQueue",
    "CallWindow",
    "Lead",
    "CallResult",
    "Appointment",
    "DispatchStage",
    "CallOutcome",
]
