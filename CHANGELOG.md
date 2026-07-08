# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Planned
- Reference VAPI and Twilio voice adapters
- SQLite-backed LeadStore
- Pluggable LLM Qualifier

## [0.2.0] - 2026-07-08

### Added
- examples/simulate_run.py: end-to-end simulation with in-memory adapters
- docs/RUNBOOK.md: production deployment checklist and incident response
- docs/ADAPTERS.md: wiring guide for all provider protocols
- .github/workflows/release.yml: automated tag-based release workflow
- Holiday guard docs: configuring skip-days in DispatchConfig

## [0.1.0] - 2026-06-24

### Added
- Dispatch lifecycle state machine with closed_lost and do_not_contact branches
- CallbackQueue with calling-window enforcement, attempt caps, and backoff
- Provider adapter protocols plus in-memory reference adapters
- Webhook helpers: HMAC signature verification and defensive event parsing
- DispatchConfig with environment-referenced secrets
- coredispatch simulate CLI and a runnable example
- Test suite and CI across Python 3.9 / 3.11 / 3.13
