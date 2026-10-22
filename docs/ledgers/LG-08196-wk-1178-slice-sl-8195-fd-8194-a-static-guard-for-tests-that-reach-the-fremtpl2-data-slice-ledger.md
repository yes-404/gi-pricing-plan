---
id: LG-8196
family: ledger
title: WK-1178 slice SL-8195 — FD 8194, a static guard: every test that reaches the freMTPL2 data carries the data-present guard (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: d66ad2ed40ef150d8bc1d26f79ea33a2bbc2397b
phase: P2
work: WK-1178
slice: SL-8195
plans: []
corrected_by: []
relates: [SL-8195, FD-8194, SL-1711]
---

# LG-8196 — WK-1178 slice SL-8195: FD 8194, a static guard for tests that reach the freMTPL2 data

Filed 2026-10-22 under working id 8196; executor seat `exec-8194`, branch `fix/fd-8194-fremtpl2-data-guard`, worktree `.claude/worktrees/fix-8194`, built from `origin/main` `71e481fa`. Logs are under `~/gi-pricing-plan.local/scratch/fix-8194/` (file names start with the sha of the tree they ran on).

**GO:** the maintainer's entry "2026-10-22 18:19:23 BST — Maintainer: #1361 CI red (2 freMTPL2 tests without the data guard): the fix plan ACCEPTED; a STATIC guard as an FD" (`to-lead.md`): "The process note becomes an FD (working id, LOW-MEDIUM, owner WK-1178). The remedy is a **STATIC guard test**: every test that references `examples/fremtpl2/data` (path literal or the data helper) must carry the existing data-present guard (marker or fixture). Red-first via an injected unguarded test. … It goes in a small slice after #1361; it does not block #1361."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

No plan: a one-file slice ordered by the entry above (FD 8194, owner WK-1178). No requirement id is claimed. Merges after #1361 (SL-1711), then re-merges `main` and re-runs the guard so it covers `backend/tests/test_wf701_journey.py`.

### Task list

1. **Enumerate** every test reaching the data (table below), before the rule.
2. **The guard test** `tests/test_fremtpl2_data_guard.py` (commit `d66ad2ed40ef150d8bc1d26f79ea33a2bbc2397b`): DB-free, AST-based.
3. **Red-first, three proofs** (below).

**Enumeration, on `origin/main` `71e481fa`.** Predicate (run at that tree over `backend/tests`, `packages/*/tests`, `examples/fremtpl2/test_*.py`): `git grep -n -i -E "fremtpl2/data|freMTPL2(freq|sev)|\.arff|build_csv|portfolio_policies|DATA_DIR|GIP_FREMTPL2|from examples|import examples" -- 'backend/tests' 'packages/*/tests' 'examples/**/test_*.py'`, read by hand, plus the readers derived from `examples/fremtpl2/*.py` (functions touching `DATA_DIR` or `to_csv`, and their callers): `build_csv`, `build_portfolio_csv` (`seed.py:121`, `:190`; `seed.py:133`/`:135` is the read).

| File | Reaches the data how | Guard |
|---|---|---|
| `examples/fremtpl2/test_seed.py` | `ARFF_DIR` alias (`:117`); `build_csv`, `build_portfolio_csv` | the `scratch_seed` fixture skips when `freMTPL2freq.arff` is absent (`:135-136`); the other readers redirect `DATA_DIR` to `tmp_path` (`:162, :283, :316, :343, :383`), so they read synthetic files |
| `packages/pricing-core/tests/test_glm_scalar_predict.py` | `_EXAMPLES / "data" / "freMTPL2freq.arff"`, `demo_seed.build_portfolio_csv` (`:353`) | `_demo_modules` skips when the file is absent (`:329-330`) |
| `backend/tests/test_demo_command.py` | the path literal `examples/fremtpl2/data/last-seed.json` (`:190`) | none needed: an expected error message inside an `assert`, no read |
| `backend/tests/test_demo_rating_evidence.py` | `GIP_FREMTPL2_EXAMPLE_DIR` (`:61`): the example's code directory | none needed: imports `model.py`, reads no data |
| `backend/tests/test_wf699_journey.py` | loads `journey.py`, `seed.py` | none needed: its world is a 40-policy synthetic portfolio (`:297`) |
| `backend/tests/test_wf701_journey.py` (**#1361 only**, `0a6cd6c9`) | `_run_in_process` → `_full_level_world` → `journey_wf701.portfolio_policies` → `seed.build_csv` | **none: the failure** |

**Two guard forms exist** (skip when absent; redirect `DATA_DIR` to synthetic files) and they are different in kind, not two spellings of one: the first needs the real data, the second must not touch it. A shared marker would unify neither, so none is introduced; the check recognises both.

**Why a closure, not a grep.** #1361's test file names no path and no reader; the read is three calls away. A text grep for `fremtpl2/data` passes it. The check follows the calls inside the file (helpers, fixtures named as parameters, module level) and derives the readers from the example, so a new reader added there is covered without editing the guard. Its limits, stated: a reader is matched by **name** (names defined in two example modules, and `main`, are dropped; `fetch.py`, which writes the directory, is not a reader); a call into another test file's helper is not followed.

### Gate

Not run. Docs-and-test-only slice; the lead grants the gate. Table empty.

Static checks at `d66ad2ed40ef150d8bc1d26f79ea33a2bbc2397b`: `ruff check tests/test_fremtpl2_data_guard.py` "All checks passed!"; `ruff format` clean; `mypy tests/test_fremtpl2_data_guard.py` "Success: no issues found in 1 source file".

### Audit

Not yet written (the auditor's).

### Build log

**2026-10-22, the guard test** (`d66ad2ed40ef150d8bc1d26f79ea33a2bbc2397b`). Three proofs, all through `scripts/run-small.sh` (single file, load1 3.76 at start):

- **(b) green on main**, tree `71e481fa` plus the new file, log `71e481fa-green-main.log`: `8 passed in 12.84s`, rc=0. Zero offenders over the real tree. First draft of the check failed here with 600+ false positives from generic reader names (`run`, `main`, `fetch`); those are the exclusions above, found by running it on main, not chosen in advance.
- **(a) red on an injected unguarded test**, same tree plus `backend/tests/test_zz_injected.py` (a helper calling `seed.build_csv(5)`, removed afterwards), log `71e481fa-red-injected.log`: `1 failed, 7 passed`, rc=1; the assertion names `backend/tests/test_zz_injected.py::test_injected_unguarded`. The same file with a `pytest.skip` guard added: `8 passed`, rc=0 (`71e481fa-green-injected-guarded.log`).
- **(c) it would have caught #1361**: `git show 0a6cd6c9:backend/tests/test_wf701_journey.py` fed with the readers derived from `main`'s example plus `0a6cd6c9:examples/fremtpl2/journey_wf701.py` (`scratch/fix-8194/proof.py`): readers `['a5_a6', 'build_csv', 'build_portfolio_csv', 'portfolio_policies', 'uat_and_a']`; flagged `['test_c7_fails_naming_the_band_when_the_sample_rate_is_zero', 'test_wf701_journey_runs_end_to_end']`: exactly the two tests #1361's CI failed.

Also in the file: seven fixture tests pin the checker's shapes (helper chain flagged; literal and alias flagged; skip guard via helper or fixture passes; `DATA_DIR` redirect passes; a comment, an `.exists()` with no skip, or a skip under an unrelated condition are not guards; a test reaching nothing is not flagged).

**Owed:** after #1361 merges, re-merge `main` and re-run `tests/test_fremtpl2_data_guard.py` (it then covers `test_wf701_journey.py`); the gate; `FD 8194`'s record, which a later docs batch writes.

## PRs

None yet.
