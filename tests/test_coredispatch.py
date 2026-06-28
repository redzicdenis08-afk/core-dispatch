"""Tests for core-dispatch. Run with ``pytest`` or ``python tests/test_coredispatch.py``."""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coredispatch import CallbackQueue, CallWindow, Dispatcher, Lead  # noqa: E402
from coredispatch.adapters.memory import (  # noqa: E402
    ConsoleNotifier,
    InMemoryCalendar,
    InMemoryLeadStore,
    KeywordQualifier,
    MockPaymentProvider,
    ScriptedVoiceProvider,
)
from coredispatch.callbacks import in_calling_window, next_window_start  # noqa: E402
from coredispatch.models import CallOutcome, DispatchStage  # noqa: E402
from coredispatch.webhooks import (  # noqa: E402
    lead_from_inbound,
    result_from_call_ended,
    verify_signature,
)
import hashlib  # noqa: E402
import hmac  # noqa: E402

NOW = datetime(2026, 1, 5, 9, 0, 0)


def _dispatcher(script):
    store = InMemoryLeadStore()
    d = Dispatcher(
        store=store,
        voice=ScriptedVoiceProvider(script),
        qualifier=KeywordQualifier(),
        notifier=ConsoleNotifier(),
        calendar=InMemoryCalendar(),
        payments=MockPaymentProvider(),
    )
    return d, store


# --- dispatcher lifecycle ---

def test_qualified_lead_books_and_follows_up():
    lead = Lead(id="a", name="Mike", phone="1", email="mike@example.com")
    d, store = _dispatcher({"a": (CallOutcome.HUMAN_REACHED, "how much is it? okay let's do it")})
    d.intake(lead, now=NOW)
    d.run_callback(lead, now=NOW)
    assert store.get("a").stage == DispatchStage.FOLLOW_UP


def test_qualified_without_email_stops_at_booked():
    lead = Lead(id="a2", name="NoEmail", phone="1")
    d, store = _dispatcher({"a2": (CallOutcome.HUMAN_REACHED, "how much? sign me up")})
    d.intake(lead, now=NOW)
    d.run_callback(lead, now=NOW)
    assert store.get("a2").stage == DispatchStage.BOOKED


def test_voicemail_requeues():
    lead = Lead(id="b", name="Dana", phone="1")
    d, store = _dispatcher({"b": (CallOutcome.VOICEMAIL, "leave a message after the tone")})
    d.intake(lead, now=NOW)
    d.run_callback(lead, now=NOW)
    assert store.get("b").stage == DispatchStage.CALLBACK_QUEUED


def test_not_interested_is_closed_lost():
    lead = Lead(id="c", name="Sam", phone="1")
    d, store = _dispatcher({"c": (CallOutcome.HUMAN_REACHED, "no thanks, not interested")})
    d.intake(lead, now=NOW)
    d.run_callback(lead, now=NOW)
    assert store.get("c").stage == DispatchStage.CLOSED_LOST


def test_dnc_is_suppressed():
    lead = Lead(id="d", name="Pat", phone="1")
    d, store = _dispatcher({"d": (CallOutcome.HUMAN_REACHED, "take me off your list and do not call")})
    d.intake(lead, now=NOW)
    d.run_callback(lead, now=NOW)
    assert store.get("d").stage == DispatchStage.DO_NOT_CONTACT


# --- callback queue ---

def test_calling_windows():
    assert in_calling_window(datetime(2026, 1, 5, 9, 0))
    assert not in_calling_window(datetime(2026, 1, 5, 14, 0))


def test_next_window_pushes_out_of_dead_time():
    nxt = next_window_start(datetime(2026, 1, 5, 14, 0))
    assert nxt.hour == 16


def test_backoff_respects_cap():
    q = CallbackQueue(max_attempts=2)
    assert q.schedule("x", attempt=0, now=NOW) is not None
    assert q.schedule("x", attempt=2, now=NOW) is None


def test_custom_window_object():
    assert CallWindow(8, 12).contains(9)
    assert not CallWindow(8, 12).contains(12)


# --- webhooks ---

def test_webhook_signature_roundtrip():
    secret, payload = "shhh", b'{"event":"call.ended"}'
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_signature(secret, payload, sig)
    assert not verify_signature(secret, payload, "deadbeef")


def test_inbound_parse_and_missing_number():
    lead = lead_from_inbound({"id": "c1", "caller": {"number": "+15551234", "name": "Mike"}})
    assert lead.phone == "+15551234" and lead.name == "Mike"
    try:
        lead_from_inbound({"id": "x"})
        assert False, "expected ValueError on missing number"
    except ValueError:
        pass


def test_call_ended_normalization():
    r = result_from_call_ended(
        {"leadId": "l1", "outcome": "voicemail", "transcript": "hi", "durationSeconds": "12"}
    )
    assert r.outcome == CallOutcome.VOICEMAIL
    assert r.duration_seconds == 12


def _run() -> None:
    fns = sorted(
        (v for k, v in globals().items() if k.startswith("test_") and callable(v)),
        key=lambda f: f.__name__,
    )
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} passed")


if __name__ == "__main__":
    _run()
