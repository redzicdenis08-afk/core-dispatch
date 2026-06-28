"""Callback scheduling with calling-window enforcement, capped retries, and backoff.

Cold and warm callbacks are the heart of a dispatch system. This module keeps
three things honest: you only call inside allowed local-time windows, you never
exceed a per-lead attempt cap, and the gap between attempts grows over time.

The default windows are intentionally conservative placeholders. Set windows
that match your own jurisdiction and compliance obligations (for example, TCPA
in the US restricts when you may call).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class CallWindow:
    """An allowed local-time window. ``CallWindow(8, 12)`` means 08:00-12:00."""

    start_hour: int
    end_hour: int

    def contains(self, hour: int) -> bool:
        return self.start_hour <= hour < self.end_hour


# Conservative defaults. Override per deployment.
DEFAULT_WINDOWS: Sequence[CallWindow] = (CallWindow(8, 12), CallWindow(16, 20))


def in_calling_window(when: datetime, windows: Sequence[CallWindow] = DEFAULT_WINDOWS) -> bool:
    return any(w.contains(when.hour) for w in windows)


def next_window_start(when: datetime, windows: Sequence[CallWindow] = DEFAULT_WINDOWS) -> datetime:
    """Return the next datetime that falls inside an allowed window."""
    ordered = sorted(windows, key=lambda w: w.start_hour)
    for w in ordered:
        if when.hour < w.start_hour:
            return when.replace(hour=w.start_hour, minute=0, second=0, microsecond=0)
        if w.contains(when.hour):
            return when
    first = ordered[0]
    tomorrow = when + timedelta(days=1)
    return tomorrow.replace(hour=first.start_hour, minute=0, second=0, microsecond=0)


@dataclass
class CallbackTask:
    lead_id: str
    due_at: datetime
    attempt: int


class CallbackQueue:
    """Schedules callbacks under window, retry-cap, and backoff constraints."""

    def __init__(
        self,
        windows: Sequence[CallWindow] = DEFAULT_WINDOWS,
        max_attempts: int = 4,
        backoff_hours: Sequence[int] = (1, 4, 24, 72),
    ) -> None:
        self.windows = windows
        self.max_attempts = max_attempts
        self.backoff_hours = backoff_hours
        self._tasks: List[CallbackTask] = []

    def schedule(self, lead_id: str, attempt: int, now: datetime) -> Optional[CallbackTask]:
        """Queue the next attempt, or return None if the cap is reached."""
        if attempt >= self.max_attempts:
            return None
        delay = self.backoff_hours[min(attempt, len(self.backoff_hours) - 1)]
        target = now + timedelta(hours=delay)
        if not in_calling_window(target, self.windows):
            target = next_window_start(target, self.windows)
        task = CallbackTask(lead_id=lead_id, due_at=target, attempt=attempt)
        self._tasks.append(task)
        return task

    def due(self, now: datetime) -> List[CallbackTask]:
        """Pop and return all tasks that are due at or before ``now``."""
        ready = [t for t in self._tasks if t.due_at <= now]
        self._tasks = [t for t in self._tasks if t.due_at > now]
        return ready

    def pending(self) -> List[CallbackTask]:
        return list(self._tasks)
