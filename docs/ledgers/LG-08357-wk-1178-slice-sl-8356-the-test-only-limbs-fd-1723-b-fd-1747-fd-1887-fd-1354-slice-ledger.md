---
id: LG-8357
family: ledger
title: WK-1178 slice G (SL 8356) — the test-only limbs: FD-1723 slice B, FD-1747, FD-1887, FD-1354
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-11-05
owner: executor
tree: 9e2a1b1388bbf390d31995b35418cf4e350103db
phase: P2
work: WK-1178
slice: SL-8356
plans: [PL-8355]
corrected_by: []
relates: [PL-8355, FD-1723, FD-1747, FD-1887, FD-1354]
---

# LG-8357 — WK-1178 slice G (SL 8356): the test-only limbs

**GO:** the plan of record is PL 8355 on `draft/pl-g-2026-11-05` @`228145c6` (DP-G1 ruled (a) in
to-lead "2026-11-05 11:52:34 GMT"); the executor brief is
`~/gi-pricing-plan.local/handover/brief-exec-sl8356g-2026-11-05.md` (sha256 prefix `70c16303a1e4`).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL 8355, "Tasks / SL 8356 — the test-only limbs", R0 to R5. Requirements: `01` FR-41, FR-33, FR-80;
`02` FR-123; `07` FR-452 (FD-1747); FD-1887 H1 and H2; FD-1354 under DP-G1 (a). **No source file
changes** (A1). Write set: `backend/tests/test_ingestion.py`, `backend/tests/test_lineage.py`,
`backend/tests/test_score_rate_limit.py`, `packages/pricing-core/tests/test_gbm.py`,
`packages/pricing-core/tests/test_metrics.py`, `tests/test_fremtpl2_data_guard.py`, and this ledger.

**Dated line (lead ruling, to-lead "2026-11-05 14:05:07 GMT"), PL 8355 T4 / R2:**
~~"Build `y` with a real `a * b` term, group `(a,)`, `(b,)`"~~ — `GbmSpec` refuses a group of one feature
("an interaction group must name at least two features"), so the test as first written failed at
`_spec` on both backends with no mutation (A2 STOP, reported, ruled). Now: four features `a b c d`,
groups `(a, b)` and `(c, d)`, signal `a * c` across the groups; the constrained fit holds no
cross-group path, the unconstrained fit holds one, and the holdout predictions differ.

### Task list

| Task | Limb | Test | Commit |
|---|---|---|---|
| T8 | FD-1354, DP-G1 (a) | `test_metrics.py::test_no_test_pins_a_metric_certificates_measured_text` (own file excluded; zero pins on main) | `d6e5ac4d`, `e78fd694` |
| T6, T7 | FD-1887 H2, H1 | `test_fremtpl2_data_guard.py`: `_tests_the_data`, `_PATH_BUILDERS`, `_import_origins`; four new tests | `1316def2` |
| T4 | FR-123 | `test_gbm.py::test_a_constrained_booster_has_no_cross_group_split[xgboost] and [lightgbm]` | `011be3f3`, `33b5d32e`, `91c559c9` |
| T1, T2, T3 | FR-41, FR-33, FR-80 | `test_ingestion.py` x2, `test_lineage.py::test_an_auditor_reads_an_archived_version_and_its_model_over_the_api` | `ba1823a1` |
| R4 | FD-1747 | `test_score_rate_limit.py::_limiter_was_enforced` (autouse), `_unenforced_total`, `_FAILS_OPEN` | `e0320b81` |

**FD-1887 fixture inputs changed (lead ruling to-lead 12:03:55 GMT: not an assert softened).** Two
existing checker tests feed the checker a source string whose guard asks `.exists()` of a name that is
not the data, which H2 now correctly refuses. Both sites, inputs only, no assert touched:
1. `test_a_skip_guard_anywhere_in_the_closure_passes`: `if not DATA.exists():` became `if not DATA_DIR.exists():`.
2. the same test's `via_fixture` string: `if not D.exists():` became `if not DATA_DIR.exists():`.

### Gate

Not yet run (the SOLO gate is the lead's). The slice's runs so far, all through
`run-heavy.sh --over-load "2026-11-05 13:58:21 GMT"`, each log opening `head=` and ending `rc=`
(`~/gi-pricing-plan.local/scratch/`):

| Run | Tree | Result |
|---|---|---|
| `uv sync --directory <wt> --all-packages --frozen` (df before: 14G avail) | `e0320b81` | rc=0 |
| `test_metrics.py` (T8 green) | `e0320b81` | `36 passed in 10.79s` rc=0 |
| `tests/test_fremtpl2_data_guard.py` (T6, T7 green; the real-tree test included) | `e0320b81` | `12 passed in 27.80s` rc=0 |
| `test_gbm.py -k cross_group`, first form | `e0320b81` | UNMUTATED RED, A2 STOP: `ValidationError for GbmSpec: Value error, an interaction group must name at least two features. A group of one constrains nothing, and reads as though it did.` `2 failed, 162 deselected` rc=1 |
| `test_gbm.py -k cross_group`, ruled form (T4 green) | `91c559c9` | `2 passed, 162 deselected in 11.32s` rc=0 |

**Red lines (A3, A9, A10).**

| Limb | Mutation / plant | Red line | Reverted |
|---|---|---|---|
| T4 | `gbm.py:867` and `:1020`: the `interaction_constraints` assignment replaced by `pass` (both backends) | `AssertionError: a path splits on both groups` x2; `2 failed, 162 deselected` rc=1 (tree `91c559c9` + mutation) | `git checkout -- packages/pricing-core/src`; `git diff --quiet` rc=0 |
| T6, T7 | none: the four new tests on the base `228145c6` guard file (scratch copy, outside the repo) | `3 failed, 1 passed` rc=1: H2 `test_a_skip_on_a_path_that_is_not_the_data_is_not_a_guard`, H1 `test_a_data_path_built_by_a_join_is_caught_in_any_spelling` (`assert [] == ['test_a']`), H1 `test_a_reader_imported_under_another_name_is_still_a_reader` (`assert [] == ['test_a']`); the fourth, `test_a_skip_on_the_data_by_any_of_its_names_is_a_guard`, passes at base by design (the over-hardening control) | scratch only, nothing committed |
| T8 | plant: `backend/tests/test_planted.py` holding the phrase `constant population of 1,000`, in a scratch copy `sl8356-t8plant` (never committed) | `AssertionError: a test pins a certificate's measured text (FD-1354): backend/tests/test_planted.py: 'constant population of 1,000'` `1 failed, 35 deselected` rc=1 | scratch only |

**Still owed, in the DB window (T1, T2, T3, R4, the FD-1747 reproduction):** red / green lines, the
reproduction's three outputs (`GAP=2.5` RED `assert 409 == 429`, `GAP=0` GREEN, 3600 `GAP=2.5` GREEN),
`-n 0 dbsize` before and after, the template guard before `createdb` and at END, `-n 11 dbsize` = 0, the
copy dropped, the bucket `gip-test-blobs-8356` removed through the MinIO API.

### Audit

(The auditor's, with the lead's adoption, in the audit's own commit.)

### Build log

- 2026-11-05: worktree `.claude/worktrees/sl-8356`, branch `sl-8356-g-test-limbs`, base `228145c6`.
- 2026-11-05: T8, T6/T7, T4, T1/T2/T3 and R4 written (see the task table), unpushed.
- 2026-11-05: **process lines.** (1) Before the TESTS HOLD message reached the seat, the seat ran the 12 test
  functions of `tests/test_fremtpl2_data_guard.py` once with bare `python3` (stdlib only, no pytest, no
  venv) as a smoke; all passed. That is a run, taken under no `run-heavy` route; the lead ruled it an LG line,
  not a finding (to-lead 12:03:55 GMT), and the reds at base were taken afterwards through `run-heavy`.
  (2) That smoke command contained a `cd /tmp`, a NO-CD breach; the harness reset the cwd and no git write
  happened there.
- 2026-11-05: T4 first form red unmutated (A2); reported; ruled to-lead "14:05:07 GMT"; rewritten
  (`33b5d32e`, `91c559c9`).

## PRs

(None yet: the slice ends unpushed; the lead pushes and opens the PR.)
