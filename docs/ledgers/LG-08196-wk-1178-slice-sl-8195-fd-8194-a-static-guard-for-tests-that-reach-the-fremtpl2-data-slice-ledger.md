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

**2026-10-22, re-merge of `origin/main` (`75f5f401`, after #1359, #1361 and the docs batch #1362), merge commit `b0d2580ceabdea1dd233cd7b55e7207df6618628`.** `git merge-tree --write-tree HEAD origin/main` gave rc=1, the one conflict `docs/INDEX.md`; main's INDEX taken and regenerated, `doc-index.py --check` rc 0 (`byte-stable`). Working-id sweep (`git grep -nE '(FD|RL|SL|LG|PL|RS)[- ]?8(1[4-9][0-9])'`, before 28 lines, after 51; logs `sweep-before.txt`, `sweep-after.txt`): the batch minted other slices' ids, but `git diff origin/main...HEAD` adds no 8xxx id other than 8194/8195/8196, so nothing of this slice's needs re-pointing.

**Red/green lines, all in `~/gi-pricing-plan.local/scratch/fix-8194/`, the log's first line the head it ran on:**

- (a) RED, `71e481fa-red-injected.log`: `FAILED tests/test_fremtpl2_data_guard.py::test_every_test_that_reaches_the_fremtpl2_data_carries_the_guard` / `1 failed, 7 passed in 9.97s`; the assert names `backend/tests/test_zz_injected.py::test_injected_unguarded`. Guarded variant `71e481fa-green-injected-guarded.log`: `8 passed in 9.20s`.
- (b) GREEN on main plus the file, `71e481fa-green-main.log`: `8 passed in 12.84s`, rc=0.
- (c) would have caught #1361, `c-proof.log` (`proof.py`, `c/`): `0a6cd6c9 test_wf701_journey.py -> ['test_c7_fails_naming_the_band_when_the_sample_rate_is_zero', 'test_wf701_journey_runs_end_to_end']`.
- (d) GREEN on the merged head, `b0d2580ceabdea1dd233cd7b55e7207df6618628-merged-guard.log` (`scripts/run-small.sh <wt> tests/test_fremtpl2_data_guard.py`, load1 2.93): `8 passed in 10.33s`, rc=0. main now carries #1361's skipif mark in `test_wf701_journey.py`, so zero offenders.

**Owed:** the code gate; the audit; the PR; the mint at its turn; `FD 8194`'s record, which a later docs batch writes.
**2026-10-23, re-merge of `origin/main` (`4e399fd0`, after #1365), merge commit `ca2057fbaf95406f2e8c500116de4d3aae58ddbb` (tree `0230fad3b4c5adfbd08c6590175d05e51a56c7f6`).** `git merge-tree --write-tree HEAD origin/main` gave rc=1, the one conflict `docs/INDEX.md`; main's INDEX taken, regenerated under gate-2, `doc-index.py --check` rc 0 (`OK (byte-stable)`); `docs/roadmap.md` auto-merged. The slice's own diff vs `origin/main` is still `tests/test_fremtpl2_data_guard.py` plus the LG, INDEX and roadmap rows.

- (e) GREEN on the re-merged head, `ca2057fb-guard-run-small.log` (`scripts/run-small.sh <wt> tests/test_fremtpl2_data_guard.py`, redis db 11, DB-free; load1 5.80 at start; DBSIZE 11 = 0 after): `8 passed in 10.70s`, rc=0. The import closure of the slice's changed source (`git diff --name-only origin/main...HEAD -- '*.py'` = `tests/test_fremtpl2_data_guard.py`, which nothing imports) is that file alone; its static scan covers `backend/tests`, `packages/*/tests` and `tests`, so it covers main's new tests. None of the 14 test files main added since `c7a3f8eb` names `fremtpl2` (`git grep -c -i fremtpl2 HEAD -- <file>` printed nothing for each).
- Gate script `~/gi-pricing-plan.local/scratch/fd8194-gate-g1.sh` is head-independent (`EXPECT_HEAD` required); sha256 `2f141c49c08b2b04339b63e3f091cb44900819ccf407fda9f627aac2f5d09c1d`, unchanged from the previous head. Not launched.

## PRs

None yet.

## Corrections after the slice audit (appended 2026-10-23 12:00 BST, head `59759536`)

Appended by executor seat `exec-8194r` on the lead's order, answering B1 and B2 of RS 8213 (the slice audit, proposed NOT-CLEAN on LG wording only; the lead adopted B1 and B2; the guard's code is unchanged). The lines above stay as written; where they disagree with this block, this block governs.

### B1 — what each log actually carries

The Build log's statement "the log's first line the head it ran on" is **false for the three `71e481fa-*` logs**: their first line is a `run-small: waiting …` line and the sha is in the file name only. The Build log also gives `rc=0` / `rc=1` for runs whose log holds no `rc=` line. Read on 2026-10-23, each log under `~/gi-pricing-plan.local/scratch/fix-8194/`:

| Log | Line 1 | Last line | `rc=` line | Head named inside the file |
|---|---|---|---|---|
| `71e481fa-red-injected.log` (a, red) | `run-small: waiting for /tmp/slots/small-test at 18:32:36 (load 4.15)` | `1 failed, 7 passed in 9.97s` | none | no (file name only) |
| `71e481fa-green-main.log` (b, green) | `run-small: waiting for /tmp/slots/small-test at 18:31:55 (load 3.76)` | `8 passed in 12.84s` | none | no (file name only) |
| `71e481fa-green-injected-guarded.log` | `run-small: waiting for /tmp/slots/small-test at 18:32:47 (load 4.12)` | `8 passed in 9.20s` | none | no (file name only) |
| `b0d2580ceabdea1dd233cd7b55e7207df6618628-merged-guard.log` (d) | `head b0d2580ceabdea1dd233cd7b55e7207df6618628` | `rc=0` | yes, `rc=0` | yes, line 1 |
| `c-proof.log` (c) | `head b0d2580ceabdea1dd233cd7b55e7207df6618628` | `rc=0` | yes, `rc=0` | yes, line 1 (the head the proof script ran on; the file it checks is `0a6cd6c9`'s `test_wf701_journey.py`, named on line 3) |
| `ca2057fb-guard-run-small.log` (e) | `head ca2057fbaf95406f2e8c500116de4d3aae58ddbb tree 0230fad3b4c5adfbd08c6590175d05e51a56c7f6 (merge commit; …)` | `8 passed in 10.70s` | none | yes, line 1 |

**Which recorded rc rests on this ledger's own account, not on the log:** (a) `rc=1`, (b) `rc=0`, the guarded variant `rc=0`, and (e) `rc=0`. For those four runs the log carries the pytest summary line only; the exit code is inferred from it (`1 failed` implies non-zero, `N passed` implies zero) and recorded here by the executor. For (a), (b) and the guarded variant the head is likewise the ledger's account: the Build log names the tree (`origin/main` `71e481fa` plus the new file, plus the injected test for (a)); the log does not. The injected test's content is in no log (RS 8213 check 4); its failure message names `backend/tests/test_zz_injected.py::test_injected_unguarded`. (c) and (d) carry their own `rc=0` and head line.

### B2 — the guard's stated limits (replaces "a static guard that cannot miss")

The slice does not claim a guard that cannot miss; that claim is withdrawn. RS 8213 check 3 probed the guard on fixture strings at `59759536`, with the readers derived from the example (`build_csv`, `build_portfolio_csv`, `portfolio_policies`, `a5_a6`, `uat_and_a`).

**Caught (controls return the offender):** a literal path `'examples/fremtpl2/data/x'`; an f-string path; a `'data' / 'freMTPL2freq.arff'` join; a class method; an async test; a comprehension; and the shapes in the Task list (helper chain, alias, fixture).

**Missed (returns no offender):**
- a path built from parts inside a function whose text uses lowercase `fremtpl2`: `ROOT / 'examples' / 'fremtpl2' / 'data'`, `Path('examples', 'fremtpl2', 'data')`, `os.path.join(…, 'fremtpl2', 'data', …)` (the join test needs the case-sensitive `freMTPL2` or `.arff`; lowercase `fremtpl2` is recognised only in a module-level alias);
- a reader imported under another name (`from … import build_csv as bc`) or fetched by string (`getattr(seed, 'build_csv')`);
- a reader reached through a subprocess (`subprocess.run(['python', 'examples/fremtpl2/seed.py'])`);
- a reader behind a fixture in `conftest.py`, or a helper in another file (the closure stops at the file; this adds to the two limits already stated above, names matched by name and calls into another test file's helper not followed);
- an unrelated guard counted as the data guard: `if not Path('/nope').exists(): pytest.skip(…)` anywhere in the test or its closure passes, whatever it tests.

**No live miss is shown at `59759536`:** the green run reports zero offenders, and RS 8213 found that `backend/tests/conftest.py`, the root `conftest.py`, `packages/pricing-core/tests/conftest.py` and `deploy_stack_helpers.py` name no data reader. The missed shapes are latent limits, not shown misses.

**Hardening is a decision for the maintainer and is not done here.** RS 8213 proposes H1 (recognise lowercase `fremtpl2` in a join, `Path(…)` and `os.path.join` inside a function; follow `import … as`) and H2 (require the guard's `.exists()` expression to name the data). If the limits above are accepted as recorded, neither needs a slice. This block changes the ledger's words only; `tests/test_fremtpl2_data_guard.py` is untouched.
