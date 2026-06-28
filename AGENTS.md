# AGENTS.md

Repository instructions for AI coding agents (Codex and compatible tools). Keep this file small and high-signal; it applies before an agent starts work.

## Project overview

- Framework core lives in `coredispatch/` (standard library only).
- Provider adapters and their protocols live in `coredispatch/adapters/`.
- Tests live in `tests/`. Runnable examples live in `examples/`.
- Docs live in `docs/`.

## Mandatory skill usage

- Run `$code-change-verification` when changes affect runtime code, tests, or build behavior. Do not mark work complete until it passes.
- Use `$pr-draft-summary` when a substantive change is finished and ready for review.

## Build and test commands

- Install: `pip install -e ".[dev]"`
- Lint: `ruff check .`
- Test: `pytest -q` (or, with no dependencies, `python tests/test_coredispatch.py`)

## Conventions

- Keep the core dependency-free. Optional integrations go behind extras, never in core.
- The dispatcher depends only on the protocols in `coredispatch/adapters/base.py`. Do not import a vendor SDK into core logic.
- Never commit secrets. Config references environment-variable names only (`DispatchConfig`).
- Add or update a test for any new stage, outcome, adapter, or webhook parser.
- Verify inbound webhook signatures before trusting payloads, and parse them defensively.
