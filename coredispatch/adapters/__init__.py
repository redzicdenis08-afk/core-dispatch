"""Provider adapters: protocols plus in-memory reference implementations."""
from coredispatch.adapters.base import (
    Calendar,
    LeadStore,
    Notifier,
    PaymentProvider,
    Qualifier,
    VoiceProvider,
)
from coredispatch.adapters.memory import (
    ConsoleNotifier,
    InMemoryCalendar,
    InMemoryLeadStore,
    KeywordQualifier,
    MockPaymentProvider,
    ScriptedVoiceProvider,
)

__all__ = [
    "VoiceProvider",
    "Qualifier",
    "LeadStore",
    "Notifier",
    "PaymentProvider",
    "Calendar",
    "InMemoryLeadStore",
    "ScriptedVoiceProvider",
    "KeywordQualifier",
    "ConsoleNotifier",
    "MockPaymentProvider",
    "InMemoryCalendar",
]
