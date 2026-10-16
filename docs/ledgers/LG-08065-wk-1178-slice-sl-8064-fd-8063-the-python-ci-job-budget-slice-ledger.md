---
id: LG 8065
family: ledger
title: WK-1178 slice SL 8064 — FD 8063, the python CI job runs its cheap checks before pytest and has a 50-minute budget, slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-16
owner: executor
phase: P2
work: WK-1178
slice: SL 8064
plans: []
corrected_by: []
relates: [SL 8064, FD 8063]
---

# LG 8065 — WK-1178 slice SL 8064: the python CI job budget

**GO:** the maintainer's ruling "2026-10-16 09:57:34 BST — RULING — the python CI job budget (#1309's cancelled run): finding MEDIUM, owner WK-1178, fix now" in `to-lead.md`. The finding is FD 8063.
**CI is the gate:** the ruling's proof is the slice's own python CI run, success, with the contracts and req_coverage stages logged before pytest. No local full gate.
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Tasks

Branch `sl-8064-ci-job-budget-2026-10-16`, worktree `.claude/worktrees/sl-8064`, cut from `origin/main` `0877e6e7`.

- **Order:** `Generated contracts are current` and `Requirement coverage` move to before `Tests` in `.github/workflows/python.yml`. Neither reads a step between (no DB, no output of `Migrate`/`Tests`).
- **Budget:** `timeout-minutes` 30 → 50.
- **Gate summary:** unchanged; it reads `steps.<id>.outcome` for all eight stages, so it is order-independent and keeps `if: always()`.

## PRs

Not opened yet; the lead joins this branch with FD 8063 and opens the PR.

## CI run

To cite here once the PR's python run is green: the run id, with the contracts and req_coverage stages logged before pytest and all eight stages in the Gate summary table.
