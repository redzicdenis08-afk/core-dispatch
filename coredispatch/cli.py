"""Command-line interface for core-dispatch."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from coredispatch.adapters.memory import (
    ConsoleNotifier,
    InMemoryCalendar,
    InMemoryLeadStore,
    KeywordQualifier,
    MockPaymentProvider,
    ScriptedVoiceProvider,
)
from coredispatch.dispatcher import Dispatcher
from coredispatch.models import CallOutcome, DispatchStage, Lead

_BOOKED_STAGES = (DispatchStage.BOOKED, DispatchStage.FOLLOW_UP, DispatchStage.CLOSED_WON)


def _simulate(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    leads: List[Lead] = []
    script_map = {}
    for row in rows:
        lead = Lead(
            id=str(row["id"]),
            name=row.get("name", "Unknown"),
            phone=str(row.get("phone", "")),
            business=row.get("business", ""),
            email=row.get("email"),
        )
        leads.append(lead)
        sim = row.get("sim") or {}
        outcome = CallOutcome(sim.get("outcome", "no_answer"))
        script_map[lead.id] = (outcome, sim.get("transcript", ""))

    store = InMemoryLeadStore()
    dispatcher = Dispatcher(
        store=store,
        voice=ScriptedVoiceProvider(script_map),
        qualifier=KeywordQualifier(),
        notifier=ConsoleNotifier(),
        calendar=InMemoryCalendar(),
        payments=MockPaymentProvider(),
    )

    now = datetime(2026, 1, 5, 9, 0, 0)
    for lead in leads:
        dispatcher.intake(lead, now=now)
        dispatcher.run_callback(lead, now=now)

    width = max((len(lead.id) for lead in leads), default=8)
    print(f"{'LEAD'.ljust(width)}  STAGE")
    print("-" * (width + 22))
    for lead in store.all():
        print(f"{lead.id.ljust(width)}  {lead.stage.value}")

    print("\nEVENT LOG")
    for entry in dispatcher.events:
        print("  " + entry)

    booked = sum(1 for lead in store.all() if lead.stage in _BOOKED_STAGES)
    print(f"\n{len(leads)} leads | {booked} booked")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="coredispatch",
        description="Run AI voice-dispatch workflows: intake, callbacks, qualify, book, follow up.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("simulate", help="Run a dispatch simulation from a leads file.")
    s.add_argument("path", type=Path, help="JSON file of leads with optional 'sim' scripts.")
    args = parser.parse_args(argv)

    if args.command == "simulate":
        return _simulate(args.path)
    return 1


if __name__ == "__main__":
    sys.exit(main())
