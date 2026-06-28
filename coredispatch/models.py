"""Core data structures for the dispatch lifecycle."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class DispatchStage(str, Enum):
    """Where a lead sits in the dispatch lifecycle."""

    NEW = "new"
    CALLBACK_QUEUED = "callback_queued"
    QUALIFYING = "qualifying"
    QUALIFIED = "qualified"
    BOOKED = "booked"
    FOLLOW_UP = "follow_up"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    DO_NOT_CONTACT = "do_not_contact"


class CallOutcome(str, Enum):
    """The result of a single call attempt."""

    HUMAN_REACHED = "human_reached"
    VOICEMAIL = "voicemail"
    IVR = "ivr"
    NO_ANSWER = "no_answer"
    FAILED = "failed"


@dataclass
class Lead:
    """A contactable lead moving through the pipeline."""

    id: str
    name: str
    phone: str
    business: str = ""
    email: Optional[str] = None
    timezone: str = "America/New_York"
    stage: DispatchStage = DispatchStage.NEW
    attempts: int = 0
    tenant: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CallResult:
    """The outcome of one voice attempt against a lead."""

    lead_id: str
    outcome: CallOutcome
    transcript: str = ""
    qualified: bool = False
    duration_seconds: int = 0


@dataclass
class Appointment:
    """A booked slot for a qualified lead."""

    lead_id: str
    when_iso: str
    notes: str = ""
