---
name: pr-draft-summary
description: Produce a branch name, PR title, and draft description after a substantive change (runtime code, tests, adapters, or webhook parsing) is finished and ready for review.
---

# PR draft summary

Trigger this when a moderate-or-larger change is effectively finished and ready to hand off, and the change touched runtime code, tests, adapters, build config, or docs with behavior impact. Do not trigger it for trivial edits.

## Collect

- current branch and working-tree status
- changed files and a short diff stat
- recent commit messages on the branch

## Output

Produce exactly three blocks:

1. **Branch name suggestion** in `type/short-slug` form (for example `feat/sqlite-lead-store`).
2. **PR title** in Conventional Commit style, one line.
3. **Description**: what changed and why, any behavior or compatibility impact, and how it was verified (ruff + tests). Reference any issue it resolves.
