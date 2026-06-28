---
name: code-change-verification
description: Run the mandatory verification stack (ruff + tests) when a change affects runtime code, tests, or build behavior in core-dispatch. Do not mark the work complete until it passes.
---

# Code change verification

When runtime code under `coredispatch/`, tests under `tests/`, or build configuration changes, run the full verification stack and do not report the work as done until it passes. Documentation-only changes do not require this.

## Steps

1. `ruff check .`
2. `pytest -q`
   - With no dependencies available, run `python tests/test_coredispatch.py` instead.

## Definition of done

- `ruff check .` reports no errors.
- All tests pass.
- If you added a stage, outcome, adapter, or webhook parser, a test covers it.
