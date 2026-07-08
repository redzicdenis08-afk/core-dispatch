# Adapter Reference

Core Dispatch is designed around adapter protocols. Swap any adapter to connect
to your real infrastructure.

## VoiceProvider

    class MyVAPIAdapter:
        def place_call(self, lead_id, phone, script) -> str:
            # Returns call_id
            ...
        def get_call_status(self, call_id) -> str:
            # Returns: pending | ringing | answered | voicemail | failed
            ...

## LeadStore

    class NeonLeadStore:
        def get(self, lead_id) -> Lead: ...
        def save(self, lead) -> None: ...
        def pending(self) -> list[Lead]: ...

## Qualifier (LLM-based)

    class GPTQualifier:
        def is_qualified(self, transcript) -> bool:
            # Call GPT-4o with your qualification prompt
            ...

## Notifier

    class TelegramNotifier:
        def send(self, message) -> None:
            # POST to Telegram Bot API
            ...

## Wiring it together

    from coredispatch import Dispatcher, DispatchConfig

    config = DispatchConfig(call_window_start=9, call_window_end=17)
    dispatcher = Dispatcher(
        config=config,
        voice=MyVAPIAdapter(),
        store=NeonLeadStore(),
        qualifier=GPTQualifier(),
        notifier=TelegramNotifier(),
    )
    dispatcher.run()
