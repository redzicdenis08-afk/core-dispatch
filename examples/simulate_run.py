"""
End-to-end simulation of a Core Dispatch run.

Uses the in-memory adapters -- no real calls, no real data.

Run with:
    python examples/simulate_run.py
"""
from coredispatch import Dispatcher, DispatchConfig
from coredispatch.adapters.memory import (
    MemoryLeadStore,
    MemoryVoiceProvider,
    MemoryCalendar,
    MemoryNotifier,
)
from coredispatch.models import Lead
import json


def main():
    config = DispatchConfig(
        call_window_start=8,
        call_window_end=20,
        max_attempts=3,
        dry_run=False,
    )
    store = MemoryLeadStore()
    voice = MemoryVoiceProvider()
    calendar = MemoryCalendar()
    notifier = MemoryNotifier()
    leads = [
        Lead(id="lead-001", phone="+15550001111", name="Alice Smith"),
        Lead(id="lead-002", phone="+15550002222", name="Bob Jones"),
        Lead(id="lead-003", phone="+15550003333", name="Carol White"),
    ]
    for lead in leads:
        store.save(lead)
    dispatcher = Dispatcher(
        config=config, voice=voice, store=store,
        calendar=calendar, notifier=notifier,
    )
    print("Starting simulation...")
    results = dispatcher.run()
    print(json.dumps(results, indent=2, default=str))
    booked = sum(1 for r in results if r.get("state") == "booked")
    print(f"Booked: {booked}/{len(results)}")


if __name__ == "__main__":
    main()
