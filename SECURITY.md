# Security Policy

core-dispatch coordinates telephony webhooks, lead data, callback scheduling, and a payment handoff, so it takes a few security surfaces seriously by design.

## Reporting a vulnerability

Please do not open a public issue for security reports. Email **contact@denisai.online** with a description and a minimal reproduction. You can expect an acknowledgement within a few days.

## Security-sensitive surfaces

- **Webhook ingestion.** Inbound provider events must be verified with `verify_signature` (constant-time HMAC-SHA256) before they are trusted, and parsed defensively. Never act on an unverified payload.
- **Secret handling.** Secrets are referenced by environment-variable *name* via `DispatchConfig` and resolved at runtime. No secret values live in config files, code, or this repository.
- **Lead data (PII).** Leads carry names, phone numbers, and emails. Keep your `LeadStore` implementation access-controlled and avoid logging raw PII.
- **Payment handoff.** The `PaymentProvider` adapter only creates a checkout link; this project never handles card data directly.
- **Multi-tenancy.** Leads carry a `tenant` field. If you serve multiple tenants, enforce isolation in your store and never let one tenant's identifiers resolve another's data.

## Supported versions

This project is pre-1.0. Security fixes are applied to the latest `main`.
