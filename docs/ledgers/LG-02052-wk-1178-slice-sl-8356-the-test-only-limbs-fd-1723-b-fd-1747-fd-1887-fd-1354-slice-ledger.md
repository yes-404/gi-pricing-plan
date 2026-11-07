---
id: LG-2052
family: ledger
title: WK-1178 slice G (SL-2051) — the test-only limbs: FD-1723 slice B, FD-1747, FD-1887, FD-1354
status: closed                 # active → closed (§1.2a)
created: 2026-11-06   # original date 2026-11-05, working id 8357, minted 2026-11-06
owner: executor
tree: 9e2a1b1388bbf390d31995b35418cf4e350103db
phase: P2
work: WK-1178
slice: SL-2051
plans: [PL-2050]
corrected_by: []
relates: [PL-2050, FD-1723, FD-1747, FD-1887, FD-1354]
---

# LG-2052 — WK-1178 slice G (SL-2051): the test-only limbs

*(Minted 2026-11-06 as LG-2052 from working id 8357, with the plan PL-2050 (working id 8355) and the slice SL-2051 (working id 8356), in the SL-2051 PR.)*

**GO:** the plan of record is PL-2050 on `draft/pl-g-2026-11-05` @`228145c6` (DP-G1 ruled (a) in
to-lead "2026-11-05 11:52:34 GMT"); the executor brief is
`~/gi-pricing-plan.local/handover/brief-exec-sl8356g-2026-11-05.md` (sha256 prefix `70c16303a1e4`).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2050, "Tasks / SL-2051 — the test-only limbs", R0 to R5. Requirements: `01` FR-41, FR-33, FR-80;
`02` FR-123; `07` FR-452 (FD-1747); FD-1887 H1 and H2; FD-1354 under DP-G1 (a). **No source file
changes** (A1). Write set: `backend/tests/test_ingestion.py`, `backend/tests/test_lineage.py`,
`backend/tests/test_score_rate_limit.py`, `packages/pricing-core/tests/test_gbm.py`,
`packages/pricing-core/tests/test_metrics.py`, `tests/test_fremtpl2_data_guard.py`, and this ledger.

**Dated line (lead ruling, to-lead "2026-11-05 14:05:07 GMT"), PL-2050 T4 / R2:**
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

**The DB window (lead-granted, to-lead "2026-11-05 23:47:23 GMT"; driver `~/gi-pricing-plan.local/scratch/sl8356-win.sh`; logs `sl8356-w-*.log`, `sl8356-win-start.log`, `sl8356-win-end.log`).**
START 23:48:53 UTC: load1 5.22; BEFORE `-n 0 dbsize` 56; template guard `alembic_version=1 environments=3 tenant_marker=1`; copy `gipricing_sl8356`; redis db 11 (`dbsize` 0); `PUBSUB CHANNELS 'gip:switch:*'` empty; bucket `gip-test-blobs-8356`; `GIP_GATE_SLOT=/tmp/slots/window-sl8356`, quoted from `/proc/<pid>/environ` on every run (pid 2661951 first: `GIP_REDIS_URL=redis://localhost:6379/11 GIP_TEST_BUCKET=gip-test-blobs-8356 GIP_GATE_SLOT=/tmp/slots/window-sl8356`). All runs on tree `5d7d3066`, through `run-heavy --over-load`.

| Limb | Run | Result |
|---|---|---|
| T1, T2 green | `test_ingestion.py -k "replayed or released"` | `2 passed, 17 deselected` rc=0 |
| T3 green | `test_lineage.py -k auditor_reads` | `1 passed, 27 deselected` rc=0 |
| R4 green | `test_score_rate_limit.py` (whole file) | `11 passed, 1 skipped` rc=0 (the skip is the pre-existing `skipif` at `:396`) |

| Limb | Mutation (applied, run, reverted; `git diff --quiet` rc=0 after each) | Red line |
|---|---|---|
| T1 | `ingestion.py` stored recipe `list(recipe)` became `list(recipe)[:-1]` | `AssertionError: assert [{'step': 'no...e': 'lower'}}] == [{'step': 'no...': 'first'}}}]` `Right contains one more item: {'step': 'map_values', ...}`; `1 failed, 18 deselected` rc=1. **Note:** it trips the stored-recipe equality assert, which sits before the hash comparison, so the hash assert was not exercised alone by this mutation |
| T2 | the recipe-failure branch writes a `status="failed"` run and its version, commits, then raises (so `_find_run` returns it on the retry) | `assert True is False` (`.reused`); `1 failed, 18 deselected` rc=1. **Note:** the plan's wording "write a failed run" needed a committed run row with a version id, because the unit of work rolls back on the raise and `_find_run` is skipped for a run with no version |
| T3 | `datasets.py` `get_version_by_id` refuses `row.status == 'archived'` | `assert 404 == 200`; `1 failed, 27 deselected` rc=1 |
| R4 | test-file mutation: `_app_client` swaps in a `RateLimiter` on a dead store (`redis://127.0.0.1:1/0`) after startup | four `ERROR` lines `AssertionError: limiter not enforced: it failed open in this test` (teardown) beside two `assert 409 == 429` body failures; `4 failed, 7 passed, 1 skipped, 4 errors` rc=1. An earlier try with `GIP_REDIS_URL` on a dead store errored every test at app start-up (the switch client is not fail-open) and shows no such line: not a reading |

**FD-1747 by-run reproduction** (scratch `~/gi-pricing-plan.local/scratch/sl8356-repro/`, outside the repo; limit 3 rps, the clock pinned, the 4th request sent after `GAP` real seconds; `_KEY_TTL_SECONDS` at its shipped value unless noted):
- `GAP=2.5`: `AssertionError: assert 409 == 429`, `1 failed` rc=1.
- `GAP=0`: `1 passed` rc=0.
- `GAP=2.5`, `_KEY_TTL_SECONDS` patched to 3600: `1 passed` rc=0.
The production limiter did not reset in any run other than by the 2 s key expiry the essay names; no sign of the HIGH trigger.

END 23:55:31 UTC: `-n 11 dbsize` 0; AFTER `-n 0 dbsize` 56; the copy dropped (`pg_database` count 0); bucket `gip-test-blobs-8356` removed through the MinIO API (`mc ls g/` lists no such bucket); template guard `alembic_version=1 environments=3 tenant_marker=1`.

**The solo gate** (the lead's; log `~/gi-pricing-plan.local/scratch/slg-gate/gate/gate.log`, read, not recalled). START `2026-11-06T04:15:36+00:00`, END `2026-11-06T06:08:17+00:00`. Object: branch `sl-8356-g-test-limbs` at `d0307aa0d4eec07d4ac7e9a9d5154575c1cbdcaa`, tree `d521000ae3e6187b3168e4c76dd33a14d6a4c828`, **before** the merge of `origin/main` and before the mint; it ran alone.

| Part | Result |
|---|---|
| ruff, mypy, import_linter, req_coverage, contracts | rc=0 each |
| pytest | rc=1: `13 failed, 7291 passed, 27 skipped, 5 xfailed, 151 warnings in 4842.50s (1:20:42)`; skipped 27 = the baseline |
| audit_docs | rc=1: only check 31, on the slice's own working ids (the gap between 2043 and 8355; the `created:` order of 8355 against 2043) |
| item 31 | the 13 FAILED are all in the eight docs-audit files (`test_audit_docs_finding_citations`, `_ids` x2, `_process_core_digest` x2, `_w37_11_ceiling`, `test_doc_index`, `test_register_lint` x3, `test_register_owed`, `test_repository_invariants` x2); no failing file outside them |
| frontend: install, generate:api, lint, type-check, test, build | rc=0 each |
| demo (`--journey wf-699`) | rc=0, designed stop with both lines seen, 1558 s; dislocation #1 530 s |
| D7 | ok: "D7's total and both attribution limbs equal on the 19985-policy sample" |
| END parts | `python max=1 fe max=0 demo=0 restore rc_kc=0 role rc_role=0 skip rc_skip=0 infra rc_infra=0 template rc_tg=0 db0 rc_db0=0` |

The mint (merge of `origin/main` at `c99a6cd818b1`, then the mint commit) came after this gate. The merge brought main's code (`backend/tests/conftest_db.py`'s read-only session-start migration check among it); the slice is test-only and ran without it. `comm` of the non-docs paths of the slice against main's delta since `b911432a` is empty, but a shared fixture is not proved by a path comparison: **CI's full suite at the merged head is the proof.**

### Audit


*(Proposal by aud-slg, 2026-11-06, for the lead's adoption. Object: `git worktree` `aud-slg` at detached
`2b31d9246a03f814bb7c4eeb6371168a01750c70`, tree `58bce6d1cb89b6d20a162ac9e13ffaf0c11cff6e`; the window's code tree is `5d7d3066`
and only this ledger changed after it (`git diff --name-only 5d7d3066 2b31d924`). Range: `origin/main...2b31d924`, with
`origin/main` = `5e5c83f7`; plan head `2f108b1e` is an ancestor of `origin/main`
(`git merge-base --is-ancestor 2f108b1e origin/main` rc 0). Scope derived from PL-2050 A1 to A11, then read to the assert.)*

| Item | Verdict | Read |
|---|---|---|
| A1 test-only | MET | `git diff --name-only origin/main...HEAD -- backend/src packages/pricing-core/src packages/model-schema/src frontend deploy scripts` prints nothing. Changed: 6 test files, PL, LG, `docs/INDEX.md`. |
| A2 unmutated red | MET | T4's first form red unmutated (`GbmSpec` refuses a one-feature group), stopped, ruled "14:05:07 GMT", rewritten as groups (a,b), (c,d). Two FD-1887 checker-test **inputs** changed (`.exists()` of `DATA_DIR`), no assert touched, ruled "12:03:55 GMT". |
| A3 / A4 T1 (FR-41) | **MET for the requirement; the plan's "fails on the hash" NOT MET as worded; lead to adopt or owe** | The mutation (`list(recipe)[:-1]` stored) reds on `assert stored == _REPLAY_RECIPE`, before `second_hash == first_hash`. On deterministic code a replay with the same steps cannot differ in hash unless the stored steps differ, so the equality assert fires first by construction; the hash assert is the requirement's statement and has the vacuity control (`plain` hash differs). No mutation isolates the hash assert alone: owed only if the lead wants one (it needs an apply path that differs between the first and second ingest, which no real defect has). |
| A5 T2 (FR-33) | MET, with a recorded deviation | The test does what the plan says (refused key, then `reused is False`, version 1). The plan's mutation "write a failed run" was unworkable as worded (the unit of work rolls back on the raise); the window's committed-run mutation reds `assert True is False`. The test does not assert that the refusal wrote no run row; the retry's `reused is False` is the evidence. |
| A6 T3 (FR-80) | MET for the dataset-version read; the Model half is not mutated | Red `assert 404 == 200` with `get_version_by_id` refusing `archived`. The "Model fitted on it" is a hand-inserted `ModelRow` (draft), not a fit; its read and the resolve are asserted green but no mutation targets the model read. Old row test stays (G6). |
| A7 T4 (FR-123) | MET | Both backends; red `a path splits on both groups` x2 with the assignment replaced by `pass` at `gbm.py:867`, `:1020`; `git diff --quiet` rc 0. The "predictions differ" threshold (mean abs > 0.05) is not exercised by the mutation (the path assert fires first). |
| A8 R4 (FD-1747) | MET | Mutation log `sl8356-w-r4-red2.log`: **4 failed, 4 errors**; each of four tests has a teardown `ERROR ... limiter not enforced: it failed open in this test` beside its `assert 409 == 429` body failure. **LG correction: it says two `409 == 429` body failures; the log has four** (lines 221, 272, 319, 371). The earlier dead-`GIP_REDIS_URL` try errored at start-up with no such line: correctly not counted. Limit: the red is shown on tests that already fail on a fail-open; no test is shown that passes while failing open. |
| FD-1747 reproduction | MET as a test-side proof; **the LG's production sentence is wider than the evidence** | Logs `sl8356-w-repro-gap25.log` (`assert 409 == 429`, rc 1), `-gap0.log` (rc 0), `-gap25-ttl3600.log` (rc 0), all `head=5d7d3066`, on a harness that pins the clock. The HIGH trigger reads "if the by-run reproduction shows the production limiter, not the test, can reset (a real-clock case this analysis missed)". Every run pinned the clock, so none tested a real clock; "no sign of the HIGH trigger" is true, but the production claim rests on the essay's argument (a 2 s TTL set inside a 1 s window cannot lapse inside it), not on these runs. Adopt: "The reproduction proves the pin is the cause; it does not run the production limiter on a real clock." |
| A9 FD-1887 | MET | `tests/test_fremtpl2_data_guard.py` 12 passed over the real tree. At base `2f108b1e` each spelling passes unflagged, run by the auditor through `run-heavy` (`scratch/aud-slg/base/probe.py`): lowercase join `[]`, `Path(...)` `[]`, `os.path.join` in a function `[]`, `import ... as` `[]`, `if other.exists(): skip` `[]`. The LG's base red shows only the first failing source of the looped H1 test; the five are now individually shown. |
| A10 T8 (FD-1354) | MET | All four phrases sit at `metrics.py:122` (two), `:135`, `:152`; plant red `1 failed`; the test file is the only exclusion. `req("FR-157")` is the custom-metric certificate requirement. |
| A11 gate and records | OWED-TO-GATE | Gate not run (the lead's). GREEN by import closure: changed modules are tests; importers by `import` (not text): `backend/tests/test_lineage_census_carveout.py` imports `test_lineage`, `packages/pricing-core/tests/test_transparency.py` imports `test_gbm`. Both are owed-to-gate beside the six changed files. |

**Common items.** 40: spec-reading predicate `grep -lE 'docs/specs|"docs" */ *"specs"' backend/tests tests` is the gate's; the slice changes no spec row. 41: the slice changes nothing under `scripts/`; `tests/test_fremtpl2_data_guard.py` is not copied by a fixture (`grep -rnE 'copytree|shutil.copy'` hits `tests/test_doc_id_migrate.py`, `test_template_headers.py` and others, none on this file). 42: `git grep -n -E "8356" origin/main -- docs/roadmap.md` prints nothing; the `SL-` row is added at the mint and must read closed by the close commit of this audit. 43: no API request shape changes, no route added; `backend/tests/test_api_authorisation_sweep.py` is owed-to-gate, not run.

**Static checks.** `audit-docs.py` on this tree: 4 failures, all the pre-mint working ids (check 31 gap, check 32 x2 for LG 8357, check 39 stale INDEX); rc 1 expected until the mint.

**NOT MET:** none outright. **Owed or lead's call:** T1's hash-only mutation; FD-1747's production sentence; the LG's "two" -> "four".

**The lead's adoption** (to-lead "2026-11-06 00:01:53 GMT", the four calls; the rows above stand as the auditor wrote them, and these lines are read with them):

(a) **T1, FR-41: met, with a note.** The mutation trips the recipe equality before the hash assert; on deterministic code no real defect isolates the hash assert, so no hash-only mutation is owed. The plan's "fails on the hash" is **not met as worded**; the requirement is met.

(b) **LG line corrected.** R4's red has **four** `assert 409 == 429` body failures, not the two the Gate table's R4 row says (`sl8356-w-r4-red2.log` lines 221, 272, 319, 371). The R4 row above is the earlier entry and is not rewritten; this line is the correction.

(c) **FD-1747 closes** on the wording that proves the test pin: the reproduction proves the pin is the cause; it does not run the production limiter on a real clock. "Production safety rests on the 2 s TTL argument" stays stated as an argument. Every run pinned the clock; no HIGH trigger fires.

(d) **The GREEN set gains** `backend/tests/test_lineage_census_carveout.py` and `packages/pricing-core/tests/test_transparency.py`, the two importers of the changed test files; both ran in the gate's full pytest (below).

(e) **Item 42.** The `SL-2051` row did not exist at `origin/main` (`git grep -n -E "SL-2051|8356" origin/main -- docs/roadmap.md` prints nothing); the mint added it as `active`, and the close commit of this audit sets it `closed`. Read at the merged head after this commit, it reads `closed`.

### Build log

- 2026-11-05: worktree `.claude/worktrees/sl-8356`, branch `sl-8356-g-test-limbs`, base `228145c6`.
- 2026-11-05: T8, T6/T7, T4, T1/T2/T3 and R4 written (see the task table), unpushed.
- 2026-11-05: **process lines.** (1) Before the TESTS HOLD message reached the seat, the seat ran the 12 test
  functions of `tests/test_fremtpl2_data_guard.py` once with bare `python3` (stdlib only, no pytest, no
  venv) as a smoke; all passed. That is a run, taken under no `run-heavy` route; the lead ruled it an LG line,
  not a finding (to-lead 12:03:55 GMT), and the reds at base were taken afterwards through `run-heavy`.
  (2) That smoke command contained a `cd /tmp`, a NO-CD breach; the harness reset the cwd and no git write
  happened there.
- 2026-11-05 23:48:53 to 23:55:31 UTC: the DB window (see Gate).
- 2026-11-05: T4 first form red unmutated (A2); reported; ruled to-lead "14:05:07 GMT"; rewritten
  (`33b5d32e`, `91c559c9`).

## PRs

(None yet: the slice ends unpushed; the lead pushes and opens the PR.)
