# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Reference VAPI and Twilio voice adapters
- SQLite-backed `LeadStore`
- Pluggable LLM `Qualifier`

## [0.1.0] - 2026-06-24

### Added
- Dispatch lifecycle state machine (`Dispatcher`): intake, qualifying callback,
  booking, follow-up, with `closed_lost` and `do_not_contact` branches.
- `CallbackQueue` with calling-window enforcement, attempt caps, and backoff.
- Provider adapter protocols (`VoiceProvider`, `Qualifier`, `LeadStore`,
  `Notifier`, `PaymentProvider`, `Calendar`) plus in-memory reference adapters.
- Webhook helpers: HMAC signature verification and defensive event parsing.
- `DispatchConfig` with environment-referenced secrets.
- `coredispatch simulate` CLI and a runnable example.
- Test suite and CI across Python 3.9 / 3.11 / 3.13.
