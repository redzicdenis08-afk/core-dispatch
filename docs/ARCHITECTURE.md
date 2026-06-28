# Architecture

core-dispatch is a small state machine plus a set of provider seams. This doc explains the moving parts and how to wire in your own providers.

## The lifecycle

A lead moves through `DispatchStage`:

```
new -> callback_queued -> qualifying -> qualified -> booked -> follow_up -> closed_won
                                     \-> closed_lost
                                     \-> do_not_contact
```

- **intake** registers a lead (e.g. from a missed-call webhook) and queues the first callback.
- **run_callback** places one attempt, then advances the lead based on the result:
  - a do-not-call phrase anywhere in the transcript moves the lead to `do_not_contact` and stops everything.
  - a machine or no-answer outcome re-queues the lead, until the attempt cap is hit, then `closed_lost`.
  - a reached human is handed to the `Qualifier`. Qualified leads are booked and followed up; the rest are `closed_lost`.

The `Dispatcher` keeps an `events` log of every transition, which makes runs easy to inspect and test.

## Callback scheduling

`CallbackQueue` is responsible for *when* a callback may happen:

- **Calling windows** (`CallWindow`): callbacks only land inside allowed local-time windows. Defaults are placeholders; set windows for your jurisdiction.
- **Attempt cap** (`max_attempts`): a lead is never dialed more than N times.
- **Backoff** (`backoff_hours`): the delay grows per attempt.

When a scheduled time falls outside a window, the queue pushes it to the next window start.

## Provider adapters

The dispatcher never imports a vendor. It depends on the protocols in `coredispatch/adapters/base.py`:

| Protocol | Method | What you implement |
|---|---|---|
| `VoiceProvider` | `call(lead, script) -> CallResult` | place a call with your voice vendor and map the result |
| `Qualifier` | `is_qualified(result) -> bool` | keyword baseline, or an LLM call |
| `LeadStore` | `upsert / get / all` | your database or CRM |
| `Calendar` | `book(lead, when_iso) -> Appointment` | your booking system |
| `PaymentProvider` | `create_link(lead, amount_cents) -> str` | your checkout provider |
| `Notifier` | `send(to, subject, body) -> bool` | your email provider |

### Example: sketching a real voice adapter

```python
from coredispatch.models import CallOutcome, CallResult, Lead

class MyVoiceProvider:
    def __init__(self, client):
        self._client = client  # your vendor SDK, configured with an env-var key

    def call(self, lead: Lead, script: str) -> CallResult:
        call = self._client.calls.create(to=lead.phone, prompt=script)
        outcome = CallOutcome.HUMAN_REACHED if call.answered_by_human else CallOutcome.NO_ANSWER
        return CallResult(lead_id=lead.id, outcome=outcome, transcript=call.transcript)
```

Keep vendor specifics inside the adapter. The dispatcher stays the same no matter which provider you use.

## Webhooks

Real deployments are event-driven. `coredispatch/webhooks.py` provides:

- `verify_signature(secret, payload, signature)` — verify before trusting anything.
- `lead_from_inbound(event)` — normalize an inbound/missed-call event into a `Lead`.
- `result_from_call_ended(event)` — normalize a call-ended event into a `CallResult`.

Both parsers coerce and validate; they never assume a field is present or well-typed.

## Configuration and secrets

`DispatchConfig` holds tuning (plan amount, max attempts, script) and the *names* of environment variables that carry secrets. Secret values are resolved at runtime via `resolve_secret` and are never stored in config files or committed.
