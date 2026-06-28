"""Reference in-memory adapters.

These let the framework run end to end with zero external services, which makes
local development, tests, and simulations trivial. Use them as the template for
your real provider adapters.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from coredispatch.models import Appointment, CallOutcome, CallResult, Lead


class InMemoryLeadStore:
    def __init__(self) -> None:
        self._leads: Dict[str, Lead] = {}

    def upsert(self, lead: Lead) -> None:
        self._leads[lead.id] = lead

    def get(self, lead_id: str) -> Optional[Lead]:
        return self._leads.get(lead_id)

    def all(self) -> List[Lead]:
        return list(self._leads.values())


class ScriptedVoiceProvider:
    """A deterministic voice provider for tests and simulations.

    Maps ``lead_id -> (outcome, transcript)``. Unmapped leads return no_answer.
    """

    def __init__(self, script: Optional[Dict[str, Tuple[CallOutcome, str]]] = None) -> None:
        self._script = script or {}

    def call(self, lead: Lead, script: str) -> CallResult:
        outcome, transcript = self._script.get(lead.id, (CallOutcome.NO_ANSWER, ""))
        return CallResult(
            lead_id=lead.id,
            outcome=outcome,
            transcript=transcript,
            duration_seconds=len(transcript.split()),
        )


class KeywordQualifier:
    """Flags a reached human as qualified on simple buying-signal keywords.

    A deliberately transparent baseline. Swap in an LLM-backed qualifier for
    production nuance; the dispatcher does not care which you use.
    """

    POSITIVE = ("interested", "how much", "price", "cost", "book", "let's do it",
                "lets do it", "sign me up", "set it up", "set me up")
    NEGATIVE = ("not interested", "no thanks", "no thank you", "do not call", "take me off")

    def is_qualified(self, result: CallResult) -> bool:
        if result.outcome != CallOutcome.HUMAN_REACHED:
            return False
        text = result.transcript.lower()
        if any(n in text for n in self.NEGATIVE):
            return False
        return any(p in text for p in self.POSITIVE)


class ConsoleNotifier:
    """Captures sent emails in memory (and is easy to assert against)."""

    def __init__(self) -> None:
        self.sent: List[Dict[str, str]] = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent.append({"to": to, "subject": subject, "body": body})
        return True


class MockPaymentProvider:
    def create_link(self, lead: Lead, amount_cents: int) -> str:
        return f"https://pay.example.com/{lead.tenant}/{lead.id}?amount={amount_cents}"


class InMemoryCalendar:
    def __init__(self) -> None:
        self.booked: List[Appointment] = []

    def book(self, lead: Lead, when_iso: str) -> Appointment:
        appt = Appointment(lead_id=lead.id, when_iso=when_iso)
        self.booked.append(appt)
        return appt
