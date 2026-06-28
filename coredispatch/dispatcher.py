"""The dispatcher: orchestrates a lead through the voice-dispatch lifecycle.

    new -> callback_queued -> qualifying -> qualified -> booked -> follow_up
                                         \\-> closed_lost
                                         \\-> do_not_contact

The dispatcher depends only on the adapter protocols, so the same logic runs
against mock providers in tests and real ones in production.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from coredispatch.adapters.base import (
    Calendar,
    LeadStore,
    Notifier,
    PaymentProvider,
    Qualifier,
    VoiceProvider,
)
from coredispatch.callbacks import CallbackQueue
from coredispatch.models import CallOutcome, DispatchStage, Lead

_DNC_MARKERS = ("do not call", "take me off", "stop calling", "remove me from")
_DEFAULT_SCRIPT = "Hi, this is your dispatcher returning your call. Is now a good time?"


def _has_dnc(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in _DNC_MARKERS)


class Dispatcher:
    """Drives leads through the pipeline using pluggable providers."""

    def __init__(
        self,
        store: LeadStore,
        voice: VoiceProvider,
        qualifier: Qualifier,
        notifier: Notifier,
        queue: Optional[CallbackQueue] = None,
        calendar: Optional[Calendar] = None,
        payments: Optional[PaymentProvider] = None,
        plan_amount_cents: int = 14900,
        script: str = _DEFAULT_SCRIPT,
    ) -> None:
        self.store = store
        self.voice = voice
        self.qualifier = qualifier
        self.notifier = notifier
        self.queue = queue or CallbackQueue()
        self.calendar = calendar
        self.payments = payments
        self.plan_amount_cents = plan_amount_cents
        self.script = script
        self.events: List[str] = []

    def _log(self, lead: Lead, msg: str) -> None:
        self.events.append(f"[{lead.id}] {msg}")

    def intake(self, lead: Lead, now: Optional[datetime] = None) -> Lead:
        """Register a new lead (e.g. from a missed call) and queue a callback."""
        now = now or datetime.now()
        self.store.upsert(lead)
        task = self.queue.schedule(lead.id, attempt=lead.attempts, now=now)
        if task is None:
            lead.stage = DispatchStage.CLOSED_LOST
            self._log(lead, "no attempts remaining at intake, closed_lost")
        else:
            lead.stage = DispatchStage.CALLBACK_QUEUED
            self._log(lead, f"callback queued for {task.due_at.isoformat()} (attempt {task.attempt + 1})")
        self.store.upsert(lead)
        return lead

    def run_callback(self, lead: Lead, now: Optional[datetime] = None) -> Lead:
        """Place one callback attempt and advance the lead by its outcome."""
        now = now or datetime.now()
        lead.stage = DispatchStage.QUALIFYING
        lead.attempts += 1
        result = self.voice.call(lead, self.script)

        if _has_dnc(result.transcript):
            lead.stage = DispatchStage.DO_NOT_CONTACT
            self._log(lead, "do-not-call detected, lead suppressed")
            self.store.upsert(lead)
            return lead

        if result.outcome != CallOutcome.HUMAN_REACHED:
            task = self.queue.schedule(lead.id, attempt=lead.attempts, now=now)
            if task is None:
                lead.stage = DispatchStage.CLOSED_LOST
                self._log(lead, f"{result.outcome.value}, attempt cap reached, closed_lost")
            else:
                lead.stage = DispatchStage.CALLBACK_QUEUED
                self._log(lead, f"{result.outcome.value}, re-queued (attempt {task.attempt + 1})")
            self.store.upsert(lead)
            return lead

        if self.qualifier.is_qualified(result):
            lead.stage = DispatchStage.QUALIFIED
            self._log(lead, "human reached and qualified")
            self._book_and_follow_up(lead, now)
        else:
            lead.stage = DispatchStage.CLOSED_LOST
            self._log(lead, "human reached but not qualified, closed_lost")
        self.store.upsert(lead)
        return lead

    def _book_and_follow_up(self, lead: Lead, now: datetime) -> None:
        when_iso = now.replace(microsecond=0).isoformat()
        if self.calendar is not None:
            self.calendar.book(lead, when_iso)
        lead.stage = DispatchStage.BOOKED
        self._log(lead, f"appointment booked for {when_iso}")

        link = ""
        if self.payments is not None:
            link = self.payments.create_link(lead, self.plan_amount_cents)
        if lead.email:
            body = "Thanks for the time today. Here are your next steps."
            if link:
                body += f" Reserve your spot here: {link}"
            self.notifier.send(lead.email, "Your appointment", body)
            lead.stage = DispatchStage.FOLLOW_UP
            self._log(lead, "follow-up email sent")
