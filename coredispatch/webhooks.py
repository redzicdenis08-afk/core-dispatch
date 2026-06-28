"""Inbound webhook handling: signature verification and defensive parsing.

Voice providers notify your system over webhooks (inbound call, call ended,
recording ready). Two rules keep that surface safe:

1. Verify the signature before trusting a payload (``verify_signature``).
2. Never trust field presence or types from the wire (the parsers below
   validate and coerce everything).
"""
from __future__ import annotations

import hashlib
import hmac
from typing import Any, Dict

from coredispatch.models import CallOutcome, CallResult, Lead


def verify_signature(secret: str, payload: bytes, signature: str) -> bool:
    """Constant-time HMAC-SHA256 verification for an inbound webhook body."""
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def lead_from_inbound(event: Dict[str, Any], tenant: str = "default") -> Lead:
    """Normalize a provider 'inbound / missed call' webhook into a ``Lead``."""
    caller = event.get("caller")
    if not isinstance(caller, dict):
        caller = {}
    phone = str(caller.get("number") or event.get("from") or "").strip()
    if not phone:
        raise ValueError("inbound webhook missing a caller number")
    return Lead(
        id=str(event.get("id") or phone),
        name=str(caller.get("name") or "Unknown"),
        phone=phone,
        business=str(caller.get("business") or ""),
        tenant=tenant,
    )


_OUTCOME_MAP = {
    "human_reached": CallOutcome.HUMAN_REACHED,
    "customer-ended-call": CallOutcome.HUMAN_REACHED,
    "assistant-ended-call": CallOutcome.HUMAN_REACHED,
    "voicemail": CallOutcome.VOICEMAIL,
    "ivr": CallOutcome.IVR,
    "no-answer": CallOutcome.NO_ANSWER,
    "no_answer": CallOutcome.NO_ANSWER,
    "customer-did-not-answer": CallOutcome.NO_ANSWER,
}


def result_from_call_ended(event: Dict[str, Any]) -> CallResult:
    """Normalize a provider 'call.ended' webhook into a ``CallResult``."""
    raw = str(event.get("outcome") or event.get("endedReason") or "").lower()
    return CallResult(
        lead_id=str(event.get("leadId") or event.get("id") or ""),
        outcome=_OUTCOME_MAP.get(raw, CallOutcome.FAILED),
        transcript=str(event.get("transcript") or ""),
        duration_seconds=_as_int(event.get("durationSeconds")),
    )
