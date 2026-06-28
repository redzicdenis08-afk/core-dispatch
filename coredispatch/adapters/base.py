"""Adapter protocols: the bring-your-own-provider seams of the framework.

Implement these against your real providers (VAPI, Twilio, Retell for voice;
Stripe, Gumroad for payments; your CRM or a sheet for storage; Resend/SES for
email). The dispatcher only depends on these protocols, never on a vendor, so
swapping providers never touches core logic.
"""
from __future__ import annotations

from typing import List, Optional, Protocol, runtime_checkable

from coredispatch.models import Appointment, CallResult, Lead


@runtime_checkable
class VoiceProvider(Protocol):
    """Places an outbound call and returns its result."""

    def call(self, lead: Lead, script: str) -> CallResult: ...


@runtime_checkable
class Qualifier(Protocol):
    """Decides whether a reached human is a qualified opportunity."""

    def is_qualified(self, result: CallResult) -> bool: ...


@runtime_checkable
class LeadStore(Protocol):
    """Persists and retrieves leads."""

    def upsert(self, lead: Lead) -> None: ...

    def get(self, lead_id: str) -> Optional[Lead]: ...

    def all(self) -> List[Lead]: ...


@runtime_checkable
class Notifier(Protocol):
    """Sends an email (follow-ups, confirmations, payment handoffs)."""

    def send(self, to: str, subject: str, body: str) -> bool: ...


@runtime_checkable
class PaymentProvider(Protocol):
    """Creates a hosted checkout link for a qualified lead."""

    def create_link(self, lead: Lead, amount_cents: int) -> str: ...


@runtime_checkable
class Calendar(Protocol):
    """Books an appointment slot."""

    def book(self, lead: Lead, when_iso: str) -> Appointment: ...
