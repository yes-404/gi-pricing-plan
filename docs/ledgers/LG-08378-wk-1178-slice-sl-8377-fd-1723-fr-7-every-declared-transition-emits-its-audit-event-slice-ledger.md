---
id: LG-8378
family: ledger
title: WK-1178 slice SL-8377 — FD-1723's FR-7 limb, every declared transition emits its audit event (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05             # filed under working id 8378
owner: executor
tree: 921d9270cd2a8f7afb232e13ad2f0aeadbe595c2   # sl-8377-fr7-events, the T2 writer commit this was first written against (base ac123679f741c02ec86504b1b017b923a93b4151)
slice: SL-8377
phase: P2
work: WK-1178
plans: [PL-8376]
corrected_by: []
relates: [FD-1723, PL-8376, FR-7, FR-368, FR-146, FR-157, FR-238, FR-349, FR-351]
---

# LG-8378 — WK-1178 slice SL-8377: every declared transition emits its audit event

**GO:** to-lead "2026-11-05 16:50:00 GMT" (accepted; GO behind M; T1 and T2 must land, T3 may stay a named exception), on the 15 rulings of "2026-11-05 16:39:14 GMT". The lead's order of 2026-11-05 (after the T1 and T2 commits): T3 GO, tests committed alone first, built DB-free up to window 2.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

The slice's row is SL 8377 in `PL-8376` ("SL 8377: the row. Scope: A1 to A14"), read at origin/draft/pl-1723-2026-11-05 @ac123679. Requirements: `00` FR-7; `06` FR-368, FR-349, FR-351; `02` FR-146, FR-157, FR-154, FR-163; `03` FR-238. Ruled decisions DP-1 to DP-15 are cited by the entry "2026-11-05 16:39:14 GMT". The branch was cut from the plan's head, not from origin/main (the brief's order); `git merge-base --is-ancestor ac123679 HEAD` printed success at the start.

### Task list

- **T1** (DP-1, DP-2, DP-3; A1 to A4). Tests `8cefe0f3`, writer `c9cf0f1a`. `record_certificate` in `objectives.py` and `metrics.py` names `certification_failed` for a failed run from `draft` or `certified`, and on a run that ends outside `draft` and `certified` keeps the certificate row, moves no status, leaves `certificate_id` and records `certificate_recorded`. Clauses at `02` FR-146 and FR-157 and `06` FR-368. The first-of-two row pins `approval_request.approve`.
- **T2** (DP-6; A5). Tests `a175b786`, writer `921d9270`. `rating_version.submitted` after the `draft` to `review` write; `deployment_request.executed` inside the deploy transaction after the guarded status update. Clauses at `03` FR-238 and the Audit actions bullet of §4.12.
- Housekeeping `refactor(audit)` commit: reverts two lines `ruff format` rejoined in `metrics.py`, on the lead's order (CI does not run `ruff format`).
- **T3** (A6 to A9, A13, A14): in progress, see the Build log.
- **T4** (A8, A9, A12): not started.

### Gate

(Written by the gate holder, not by this executor.)

DB-free checks on this executor's side, tree `921d9270`: `ruff check backend` rc 0; `audit-docs.py` (`--light`, `env -C` the worktree) FAILED (2): `check 31: gap in the full allocation between 2010 and 8376` (the working ids), `check 39: docs/INDEX.md is stale against a fresh regeneration (2194 governed record(s))` (the mint's, ruled by the lead).

### Audit

(The auditor's.)

### Build log

- 2026-11-05 17:48 UTC. T1 and T2 tests and writers committed, in the order `8cefe0f3`, `a175b786`, `c9cf0f1a`, `921d9270`. **Window 1** runs `backend/tests/test_audit_transitions.py` twice in one DB window: at the test commit `a175b786` in a throwaway checkout (expected red: 14; green: the one pin), then at head. The reds therefore stay provable though the writers are in later commits. Window lines: (to be added after the window runs.)
- 2026-11-05. DP-3's limb stands unless window 1 finds the eight `certificate_recorded` cases green at `a175b786`; if so, the limb is withdrawn (`moved` and `.certificate_recorded` dropped) and this ledger says so.

## PRs

(None yet: the executor does not push or open the PR.)
