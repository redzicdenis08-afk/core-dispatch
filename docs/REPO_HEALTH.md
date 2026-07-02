# Repository Health

**Project:** core-dispatch

**Type:** Python voice-dispatch framework

## Public boundary

Open workflow framework only. Live prompts, provider keys, customer leads, payment records, and production deployment details stay private.

## Local verification

Run these before opening a PR or publishing a release:

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
ruff check .
```

## Release checklist

- Tests pass from a clean clone.
- Examples use synthetic names, numbers, domains, and records.
- No `.env`, credentials, real transcripts, customer data, private URLs, or production exports are included.
- README examples still match the CLI and library API.
- Any side-effecting workflow stays dry-run or explicitly gated by default.

## GitHub hygiene added

- Bug report and feature request templates.
- Pull request checklist focused on tests and data safety.
- Weekly Dependabot checks for GitHub Actions.
- Security policy when the repo did not already have one.
