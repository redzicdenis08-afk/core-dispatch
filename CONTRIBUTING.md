# Contributing to core-dispatch

Thanks for considering a contribution. The goal is a small, readable, dependency-free dispatch engine that is easy to extend with your own providers.

## Development setup

```bash
git clone https://github.com/redzicdenis08-afk/core-dispatch
cd core-dispatch
pip install -e ".[dev]"
```

## Running checks

```bash
ruff check .
pytest -q
# or, with zero dependencies:
python tests/test_coredispatch.py
```

## Guidelines

- Keep `coredispatch/` core dependency-free (standard library only). Optional integrations go behind extras.
- The dispatcher depends only on the adapter protocols in `coredispatch/adapters/base.py`. Do not import a vendor SDK into core logic.
- Add a test for any new stage, outcome, adapter, or webhook parser.
- Never commit secrets. Config references env-var names only.
- One focused change per PR, with a clear before/after description.

## Adding a provider adapter

1. Implement the relevant protocol from `coredispatch/adapters/base.py` (for example `VoiceProvider`).
2. Keep vendor-specific code inside the adapter; do not leak it into the dispatcher.
3. Add a test using a mock or recorded payloads. Do not put real keys in tests.
4. If it is broadly useful, add a short note to `docs/`.

## Reporting issues

Open an issue with what you expected, what happened, and a minimal repro. For anything security-related, see [SECURITY.md](SECURITY.md) instead of opening a public issue.
