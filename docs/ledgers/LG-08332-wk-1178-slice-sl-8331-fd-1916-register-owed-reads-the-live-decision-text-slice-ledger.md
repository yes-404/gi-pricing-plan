---
id: LG-8332
family: ledger
title: WK-1178 slice SL-8331 — FD-1916, register-owed.py reads the live decision text (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05            # filed under working id 8332
owner: executor
tree: afe1ee999f91cd0959609c8a0c146e2daeecd178   # sl-8343-table-row-parser, the code head this was written against (base c8d8522758859d23fac5542815ccaa59c5a4b087)
slice: SL-8331
phase: P2
work: WK-1178
plans: [PL-8330]
corrected_by: []
relates: [FD-1916, PL-8330, LG-8344]
---

# LG-8332 — WK-1178 slice SL-8331: `register-owed.py` reads the live decision text

**GO:** to-lead "2026-11-05 09:58:58 GMT"; "2026-11-05 10:36:35 GMT" (all nine plans accepted; T folded onto the FD-1484 branch and gate).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL 8330, "SL 8331 — `_live_text`". No requirement id: tooling. Register: FD-1916. The commits ride `sl-8343-table-row-parser`; one gate covers both slices (LG 8344).

### Task list

1. **R1 — red first.** `731df717`: `tests/test_register_owed.py`, T1 `test_review_mode_ignores_a_superseded_opening`, T2 `test_work_mode_ignores_a_superseded_opening`; T3 and T4 are controls. Committed alone.
2. **R2 — green.** `b9214ae6`: `scripts/register-owed.py`: `_SUPERSEDED_OPENING` once, `_live_text`, used by `_matches_review` and `_matches_work_id` (the work-item cell is unchanged). `_is_resolved` is unchanged and `scripts/register-lint.py` is untouched by this slice (its change is SL 8343's).

### Gate

Runs on the executor's tree through `run-heavy.sh --over-load "2026-11-05 13:58:21 GMT"`.

**Red first, by cause, on base `c8d85227`** (the new test file copied into a detached worktree of base):

- T1: `assert [<_register_owed_under_test.Match object ...>] == []`, `Left contains one more item`: row 1 matched `review`.
- T2: the same assert shape: row 1 matched `WK-B`.
- `3 failed, 13 passed`: T1, T2 and `test_check_29_wiring_is_undisturbed` (red on base because `audit-docs.py` exits 1 on the working-id gaps and the stale INDEX, as in LG 8344). T3 and T4 are green at base.

**Green, slice tree:** `tests/test_register_owed.py`: `15 passed, 1 failed in 61.13s`; the one failure is `test_check_29_wiring_is_undisturbed`, for the audit-docs cause above.

**A4, the real register, `python3 scripts/register-owed.py review`:**

- Base `c8d85227`: `31 owed row(s), 11 matched but excluded as opening with a resolution marker`.
- Head `b9214ae6`: `11 owed row(s), 1 matched but excluded`.
- The 20 rows that left, each with the live text before the marker (a script check read `docs/findings/register.md`; none has `§14` before the marker, `bad 0`): FR-240 (F-W9-3); 03 rating shapes vs hand-authored contracts (F27); RFC-840/841 adoption pilot (F28); Error codes across the spec/code boundary (F29); Roster publishing emits a constant (F31); mypy files coverage (F33); NFR-499 rate limits (F48); `register-owed.py WK-671` finds 10 open rows … (F63); `.claude/roles/reporter.md`'s Mechanism section …; The "never end your turn with outstanding background work" rule …; RL-909's decay rule has no faithful check …; Five test fixtures are written into the real `docs/plans/` …; Check 37 reds on 95 of 95 post-migration rulings …; RFC-937 §1.5 requires the vendored manifest …; The plan's ruling-heading census …; A filed ruling that omits the `## Ruling N` heading …; A session ends leaving the shared checkout …; A guard disarmed by the very event it was written to survive; Two freeze-clause breaches on `PL-1070`; Four frozen plans state row (d)'s criterion in a superseded form. Each opens `**deferred with an owner — <the lead | the maintainer | the create-read-retire audit Work | WK-674>**` above its marker.
- The 20 that left are under the plan's upper bound of 28 (rows with `§14` only after the marker, counted over the whole row). The auditor re-runs the count after the closing act (A7).

### Audit

(To be written by the auditor.)

### Build log

- 2026-11-05: T1–T4 `731df717`, `_live_text` `b9214ae6`, on `sl-8343-table-row-parser`.

## PRs

(Added at the PR.)
