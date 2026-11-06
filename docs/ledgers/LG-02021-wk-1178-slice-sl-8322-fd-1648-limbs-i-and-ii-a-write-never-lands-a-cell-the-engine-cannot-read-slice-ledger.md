---
id: LG-2021
family: ledger
title: WK-1178 slice SL-2020 — FD-1648 limbs (i) and (ii): a write never lands a cell the engine cannot read (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-05
owner: executor
tree: 880a22f9           # sl-8322-r1-rate-table-cells head this was written against (base a459d49a, tree 259f0b25)
slice: SL-2020
phase: P2
work: WK-1178
plans: [PL-2019]
corrected_by: []
relates: [FD-1648, FD-1767, FD-1780, FD-1781, PL-2019, FR-234, FR-214, FR-222, FR-261]
---

# LG-2021 — WK-1178 slice SL-2020 (R1): a write never lands a cell the engine cannot read

**GO:** to-lead "2026-11-05 10:41:08 GMT" (plan R revised @dbe20ec5 accepted, split into R1 and R2), amended by the lead's dated line of 10:43:54 GMT: the plan head is a459d49a, tree 259f0b25, no scope change.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`PL-2019`, R1 (SL-2020), items A1 to A11. Requirements: `03` FR-234 (spec text amended first), FR-214 (guard only), FR-222, FR-261. FD-1648 gains limbs (i) and (ii) and **stays open** (closes at R2); FD-1767, FD-1780, FD-1781 close at the audit. Limb (iii) and score-time behaviour are R2's and untouched here.

Write set: the plan's R1 write set, plus **one line** in `packages/pricing-core/tests/test_quote_input_raise_sites.py` (`_INPUT_FREE`), by the lead's OK of this date: the new compile-time raise site `_refuse_unparseable_cells` names the table ref, key values and stored cell text (configuration, no quote input), and the registry test fails without the entry.

### Task list

- **R1.0** spec text first (A2), commit `ca959718`, alone: FR-234 clause, `RATE_TABLE_CELL_UNPARSEABLE` in `03` §5.2.
- **R1.1** limb (i) (A4): red `7098ddc2`, green `ddec9ebc`.
- **R1.2** limb (ii) (A5): red `a1423996`, green `7fb22005` (with R1.3).
- **R1.3** compile backstop (A6): red `28b8c29d`, green `7fb22005`.
- **R1.4** goldens T8 (A7), **R1.5** FD-1767 guard T9 (A8), **R1.6** FD-1780 T10 (A9), **R1.7** FD-1781 T11 (A10): tests `68cb58df`, guard-type correction `55ec1bcd`, green `1f7338a9`, wrap `880a22f9`.

**Write paths verified by reading** (A5): import (`_checked_import`, operations.py), manual edit (`apply_cell_edits`), uplift, uplift by filter, floor and cap, rebase (all via `_validate_result`), and seed (`seed_from_model`). Every one ends in `validate_rate_table` and so in `_value_issue`, the one choke point. Rebase and seed write only computed fixed-point text (limb (i)), so no input reaches them that the new check could refuse: T3's refusal cases cover import, edit, uplift, uplift by filter and floor/cap; rebase and seed are covered by limb (i)'s tests, as the test docstring says.

**Departures and notes**
- T3 over the "seven paths": five carry refusal cases; rebase and seed cannot hold unreadable text after limb (i) (above).
- T9 (FD-1767 guard) declares `decimal`, not `relativity`/`percentage`: the compiler widens `int`/`count` only into `decimal` (`_WIDENING`); the first draft was refused at compile with `RATING_TYPE_MISMATCH` (commit `55ec1bcd`).
- T10: with two NaN the collision check now passes, and the model then refuses the NaN by name in the banding (`FactorResolutionError`, null band). A `Decimal('NaN')` reaching that fixture's banding panics inside the engine (`pyo3_runtime.PanicException`); that is a separate, pre-existing defect (score-time, R2's area), so T10 asserts the collision check on `float` NaN at `predict`, and `_same_value` itself on `float` and `Decimal`.
- Route-level tests (`backend/tests/test_api_rate_tables.py`: manual edit and import) are DB-lane: written, **not run here**; proved in the gate.
- A compile-time table with blob cells (no inline `rows`) is skipped by the backstop.

### Gate

**The SOLO full gate at `662867bb1983c179a56f1697de75cc776b3f1345` (tree `81dc64af871320c3780f767305fd01c8ede0b501`, branch `sl-8322-r1-rate-table-cells`).** START 2026-11-05 12:09:05 UTC, END 14:37:12 UTC, `rc=125` (the gate's own demo code: "NOT RUN: not quiet", load1 9.52 still >= 2.0 after 1200 s; NOT GREEN until a quiet demo-only re-run passes). Every rc read from `gi-pricing-plan.local/scratch/slr1-gate/gate/*.rc`; "tree after gate: 0 changed path(s)":

| stage | rc | reading |
|---|---|---|
| ruff | 0 | `ruff.rc` |
| mypy | 0 | `mypy.rc` |
| import-linter | 0 | `import_linter.rc` |
| audit-docs | 1 | `audit_docs.rc`; check 32 on an id the plan cited that did not resolve (two plan lines at that head, fixed by `d5189039`) and 39 (INDEX stale: the mint regenerates it), see the eight files below |
| req-coverage | 0 | `req_coverage.rc` |
| generate-contracts --check | 0 | `contracts.rc` |
| pytest | 1 | `pytest.rc`; summary line whole: `15 failed, 7188 passed, 22 skipped, 5 xfailed, 146 warnings in 6732.05s (1:52:12)` |
| frontend (generate:api, lint, type-check, test, build) | 0 | vitest: `Test Files  138 passed (138)`, `Tests  919 passed (919)`, `Type Errors  no errors` |

- **Skipped 22 against the baseline of 22**: not above it (`rc_skip=0` in the END parts line).
- **The 15 failed by file** (`grep '^FAILED' pytest.log`, split at the first colon): `tests/test_audit_docs_finding_citations.py` 1, `tests/test_audit_docs_ids.py` 4, `tests/test_audit_docs_process_core_digest.py` 2, `tests/test_audit_docs_w37_11_ceiling.py` 1, `tests/test_doc_index.py` 1, `tests/test_register_lint.py` 3, `tests/test_register_owed.py` 1, `tests/test_repository_invariants.py` 2: 1+4+2+1+1+3+1+2 = 15, exactly the eight docs-audit files of the standing rule 1(f) (item 31 of the common seat brief), no other file.
- **External load, from `gate.log`**: START load1 1.28 (5.59 at 15 min); pytest START 12:10:21 load1 1.59, no external python; pytest END 14:03:01 load1 21.93 with pricing-catering's `scripts/build_freq_glm.py` (two processes at 211% and 218% CPU); pnpm test START 14:12:42 load1 19.89 and END 14:16:57 load1 10.83 (one `build_freq_glm.py` at 106%; a 60 s foreign-pid wait before the stage, not counted in its time); the demo stage START 14:17:06 load1 10.58; `quiet window | NOT QUIET: load1 9.52 still >= 2.0 after 1200 s`; END 9.24 / 8.21 / 10.39. `load.log`: before-python 1.24, after-python 21.93, after-frontend 10.58, after-demo 9.52.

**The demo-only runs** (`wf-699`, `--no-compose`, from `gi-pricing-plan.local/scratch/slr1-gate/`):
- **14:54 preflight abort, `rc 97`**: quoted from exec-gater1b's report; its log was overwritten by run 1 and is not read here.
- **Run 1**, `demo-run1/`: START 14:55:08 load1 5.07, END 14:58:23 (`gate.log` END 14:58:27, `rc=1`), 191 s, "EXITED EARLY rc=1 before both lines". The OpenML fetch got `urllib.error.HTTPError: HTTP Error 503: Service Temporarily Unavailable` (`demo-run1/demo.log:53`): an upstream outage, **no reading** of the slice.
- **Run 2**, `demo-run2/`: START 15:00:25 load1 9.22 (the quiet bar passed: every >50% process foreign at nice 19), END 15:40:45 load1 16.60, gate END 15:40:49 `rc=124` at the 2400 s cap (demo seconds 2414). Dislocation #1 **1209 s** against 383 to 422 s on the 29 Oct passes and 552 to 558 s for this box's baseline; **D7 "NOT FOUND in demo.log"**. A cap stop is not a pass and not RED (lead 30, to-lead "2026-11-05 15:43:06 GMT"): run 3 re-runs it once. Load1 rose from 9.2 to 16.6 as pricing-catering's normal-priority workers arrived at about 15:25. A6: infra inspect before and after the demo, `diff rc=0`; keycloak bind source under `tools-main`; both DBs, both buckets and redis dbs 1 and 3 removed, `own-DB count=0`, `dbsize=0`.
- **Run 2's four tracebacks** (`demo-run2/demo.log`, lines 261, 299, 555 and 665; the journey's negative steps, the seat's read, ruled at 15:43:06). Each is a `job handler failed` logged by `ForkPoolWorker-2` that ends in `pricing_core.safe_error.SanitisedError: PlatformError: <code>`:
  1. line 261, 15:05:52: `PIN_NOT_APPROVED`, from `app/platform/rating_versions.py:832` `compile_rating_version`, through `app/worker/rating_handlers.py:61` `work`.
  2. line 299, 15:05:53: `PIN_NOT_APPROVED`, the same frames.
  3. line 555, 15:06:47: `GOLDEN_QUOTE_MISMATCH`, from `app/worker/rating_handlers.py:210` `_rating_regression`, through `app/worker/tasks.py:180` `execute_job`.
  4. line 665, 15:07:06: `GOLDEN_QUOTE_MISMATCH`, the same frames.
  None names a `docs/` path.
- **The mint exposure during run 2** (lead 30, to-lead "2026-11-05 15:27:35 GMT", quoted whole there and not restated here; conditions confirmed met at "2026-11-05 15:43:06 GMT"): an exec-mintr1 merge began at about 15:25:50 in this worktree and was aborted by the lead at about 15:26:30. `build_guide` (`GET /api/v1/demo/guide`) reads `docs/specs`, `docs/contracts/openapi/generated.json` and `docs/roadmap.md` from the worktree per request. Read by exec-mintr1b from `demo-run2/demo.log`: **one** `demo/guide` request in all (`grep -n 'demo/guide' demo-run2/demo.log`: two log lines, 102 and 103, the app's `request completed` and uvicorn's access line of the same request, stamped 15:05:27, status 401 — the demo's readiness poll), **0 between 15:25:50 and 15:26:30** (0 in all of 15:25:00 to 15:26:59); correcting this ledger's earlier "2", which counted the two lines; the log runs 15:05:26 to 15:40:43. Head, tree and porcelain were re-read at exec-mintr1b's start: head `662867bb`, tree `81dc64af`, porcelain 0, no `MERGE_HEAD`.
- **Mint-seat disclosures** (exec-mintr1b, 2026-11-05): (1) the mint seat's shell changed directory twice (into `docs/` of this worktree at the mint, then into the gate scratch directory); the shell's directory was reset each time and no git write ran from either; (2) the six working-id cites in five code and test files were re-pointed in a separate mint commit (`chore(mint)`), ruled by the maintainer at to-lead "2026-11-05 15:49:09 GMT" (B) under DP-T27-6: docstring-stripped `ast.dump` equality held for each of the five files at that commit (the proof's output is in the FINAL); the non-docs delta `662867bb..` the mint head is exactly those 5 files.
- **The mint-then-unmint, and why** (maintainer, to-lead "2026-11-05 15:59:27 GMT"): this ledger and its mint commits (PL-2019, SL-2020, LG-2021; the six code-comment re-points; the regenerated INDEX) were minted on 2026-11-05 at 14:38:17 GMT's "mint, audit and PR proceed now", then taken back: ids land in merge order (standing since 29 Oct), so a mint belongs immediately before its PR, and R1 has a merge blocker (run 3). `docs/INDEX.md`, the roadmap row and the minted ids would have been a record of progress the repository does not have. The branch went back to the pre-mint commit `3559a9c1` (working ids); the mint was kept on the local, unpushed ref `draft/sl-8322-mint` @`aadcd653`, and R1 minted again after run 3 passed: see the re-mint note below.
- **Run 3 — PASS** (`demo-run3/`, script `slr1-demo3.sh` sha256 `02d644494b65`; lead 30's written START "2026-11-05 20:12:02 GMT", the maintainer's "2026-11-05 20:38:15 GMT"). It ran on the pre-mint head `3559a9c10067e551fadcb6022fe994e7c03ae2b9` (tree `c9317036c2735d6e6ad8867e2ed4e44662a8a7b7`), not on a mint head (the 15:59:27 ruling), with the non-docs delta `662867bb..3559a9c1` printed at START and empty (`[]`). Slot `gate-1b` (redis dbs 2 and 4, buckets `gip-test-blobs-gate-1b` and `gip-blobs-demo-gate-1b`, DBs `gipricing_slr1r3_gate` and `gipricing_slr1r3_demo`); the START guard allowed a start at load1 1.44 < 2.0 with nothing above 50 % CPU. START 20:12:16 UTC, demo START 20:12:23 (load1 1.73), designed stop 20:37:44 with both completion lines seen, END 20:37:53: `demo.py --journey wf-699 --no-compose` `rc=0`, **demo seconds 1526 of the 2400 s cap**, **dislocation #1 568 s** (29 Oct passes 422 / 387 / 383 s; this box's baseline 552 / 558 s), D7 `ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units`, demo end load1 1.41. **Balloon counters** (`/proc/vmstat`, read by the script at demo START and END): `balloon_inflate` 350166835 -> 354190351 and `balloon_deflate` 350166835 -> 354190351 (inflate equal to deflate at both reads: no ballooned interval at either); `/proc/pressure/memory` `some avg10=0.00 avg60=0.00 avg300=0.00` and `full` the same at both reads. A6: infra inspect before and after the demo `diff rc=0`; keycloak bind source under `tools-main`; DBs, buckets and redis dbs 2 and 4 removed (`own-DB count=0`, `dbsize=0`); `redis -n 0 dbsize` 56 at START and END; template guard `alembic_version=1 environments=3 tenant_marker=1` at both ends. END line: `END 2026-11-05T20:37:53+00:00 1.46 1.73 2.64 (date l1 l5 l15) rc=0 verdict=PASS`, every END rc part 0. **With run 3, the gate's `rc=125` demo stage is replaced by a PASS on the gated code** (the head's non-docs delta from the gated `662867bb` is empty); the gate's other stages stand as read above.


- **The re-mint, and what was replayed** (exec-run3, 2026-11-05, on lead 30's GO after D's #1435 merged, main `cded9f0e`): the branch was re-merged with `origin/main` (`cded9f0e`; a merge, not a rebase; `docs/roadmap.md` conflicted once, two adjacent slice rows kept in order). The ids after FD-2018 were read at the mint: PL-2019, SL-2020, LG-2021 (each free by `git grep` and `git ls-tree` on `origin/main`). The seven content commits of `draft/sl-8322-mint` (minus its two INDEX regenerations) were replayed with `git cherry-pick -n` and the minted ids 2011, 2012 and 2013 of that draft re-pointed to 2019, 2020 and 2021 by `mint-repoint.py` (`--frozen-on origin/main`, self-test rc 0; every hit read in `--dry-run` first: only this slice's own lines, none of main's `SL-2011`, `LG-2012` or `OQ-2013` rows). The six working-id cites in five code and test files are re-pointed in the same mint commit under DP-T27-6; docstring-stripped `ast.dump` equal for each (`errors.py`, `rate_tables.py`, `test_quote_input_raise_sites.py`, `test_rate_table_bulk_ops.py`, `test_rating_compile_fr240.py`). The non-docs paths of `origin/main...HEAD` are the thirteen of R1's write set, the five of them re-pointed comments only. The plan file is d5189039's: normalised for the id form (its own working id in the front matter and heading replaced by the minted id; the two slice ids in its title written in the space form, the rule of `65e9ceb7`), its status `draft` to `active`, its text otherwise equal line for line.
- **Disclosures of this re-mint** (exec-run3): one Bash call ran `cd /` while the shell was already in `tools-main`'s own directory; the shell's directory was reset after the call and no git write ran from it. The cherry-pick of the draft's first commit stopped on `docs/roadmap.md` (the conflict above); the remaining six applied cleanly.
- **`cell_parses` catches `ValueError` as well as `RuntimeError` (fail-closed)**, which the plan's snippet did not name (the audit's "claimed in the diff and not in the LG"): a cell the engine's parser refuses with either exception reads as unparseable, so `cell_parses` returns `False` and the write is refused with `RATE_TABLE_CELL_UNPARSEABLE` (the compile backstop refuses the stored cell) rather than the exception escaping. The safe direction: only those two exception types read as unparseable, and a refusal never lands a cell; no test fixture raises a `ValueError` there today, so the line carries no test of its own.
- **Known: `_format_value`'s positional form grows with the exponent** (maintainer, to-lead "2026-11-05 20:58:36 GMT"; a line, not a finding): limb (i) writes a computed cell as `format(value.normalize(), "f")` (`rate_tables/operations.py`), a positional string whose length grows with the exponent, where `origin/main` returns `str(value.normalize())`, a compact `1E+999990` of nine bytes. The class is the one a fix creates: it enters `main` at this slice's merge and leaves at R2's (`94d9e279`), which follows promptly; no deployment exists, so it is a tree state, not an exposure. R1's gated code is not changed after the reading. The watch the maintainer names is separate: the operation record's `percentage` under `DecimalStr` and `_positional`, decided by SL 8389's route test.
- **The GREEN set by import closure** (item 29 of the common seat brief): changed source modules = `git diff --name-only origin/main...HEAD -- packages backend/src` filtered to `/src/`: `app.errors`, `app.platform.rate_tables`, `pricing_core.rate_tables.operations`, `pricing_core.rating.compile`, `pricing_core.rating.properties`, `pricing_core.rating.runtime`; closure = those + every source module importing one + one more level of importers (96 modules); GREEN = every file under `backend/tests`, `packages/*/tests` and `tests` that imports a closure module: 210 files (162 under `backend/tests`, 46 under `packages/pricing-core`, `tests/test_permission_parity.py` and `tests/test_repository_invariants.py`). The derivation script and the list are `~/gi-pricing-plan.local/scratch/aud-slr1/closure-r1.py` and `green-set-closure-r1.txt` (an `ast` import graph, not a text grep). The decisive green for this set is the SOLO full gate at `662867bb` (pytest `15 failed, 7188 passed, 22 skipped`, the 15 exactly the eight docs-audit files); the seven-file small-run list above is the slice's own subset, not the closure.

Small runs, `run-small.sh`, tree = the worktree `sl-8322` at the commit named, load1 < 6:
- `ruff check .` rc 0; `mypy` "Success: no issues found in 252 source files" rc 0; `lint-imports` "Contracts: 4 kept, 0 broken." rc 0 (head 55ec1bcd + the edits of `1f7338a9`/`880a22f9`).
- test_rate_table_bulk_ops 84 passed; test_rate_table_operations 60 passed; test_rating_compile_fr240 28 passed; test_rating_column_collision 13 passed; test_testing 37 passed; test_rating_score_batch_outputs 55 passed; test_quote_input_raise_sites 19 passed.

### Audit

**Auditor aud-slr1, 2026-11-05 (read at 16:11 UTC; committed at the mint by exec-run3, verbatim from the auditor's draft with the ids re-pointed).** Object: range `origin/main...` the branch at the re-merged head `3559a9c1` (tree `c9317036`; the gate ran `662867bb`, tree `81dc64af`); the non-`docs/` delta `662867bb..3559a9c1` is empty (`git diff --name-only 662867bb 3559a9c1 | grep -v '^docs/'` prints nothing), so the gate's code is the head's code. Scope derived first from `PL-2019` Acceptance Standard A1 to A11 (the R1 half), then evidenced. Proposals only: the verdicts are the lead's (CLAUDE.md §12).

Re-runs on my own detached worktree `aud-slr1` @ `3559a9c1`, DB-free, one file per call through `run-heavy.sh --over-load`; logs `~/gi-pricing-plan.local/scratch/aud-slr1/` (each opens `head=`, closes `rc=`): `test_rate_table_bulk_ops` 84 passed, `test_rate_table_operations` 60 passed, `test_rating_compile_fr240` 28 passed, `test_rating_column_collision` 13 passed, `test_testing` 37 passed, `test_rating_score_batch_outputs` 55 passed, `test_quote_input_raise_sites` 19 passed; all rc 0.

| Item | Criterion (plan line) | Proposed verdict | Evidence |
|---|---|---|---|
| A1 | write set only; nothing under `frontend/`, `scripts/`, `deploy/`, `docs/contracts/` (L224) | MET | `git diff --name-only 2f108b1e...662867bb`: 17 paths, all in R1's write set, plus `test_quote_input_raise_sites.py` (one `_INPUT_FREE` line, the lead's OK, recorded in the Scope section) and the docs records. None of the four barred trees. |
| A2 | the `03` commit precedes the first code commit (L226) | MET | `ca959718` 10:44:48 touches only `docs/specs/03-rating-engine.md`; first code/test commit `7098ddc2` 10:45:51. |
| A3 | reds quoted by cause (L227) | MET | Causes quoted for T1/T2, T3, T4, T10, T11 (assert text or `DID NOT RAISE`, none a `NameError`/import). Independently re-derived with base source `2f108b1e` under the head's tests: T1 `assert '1E+2' == '100'`; T4 `DID NOT RAISE ValueError`; T10 `assert 'MODEL_CALL_FEATURE_COLLISION' != 'MODEL_CALL_FEATURE_COLLISION'`. T11's red is `scratch/sl-8322-r1/red-t10-t11.log` (`TypeError: x`). T3's red is the LG's quoted line only (not re-run). |
| A4 | limb (i): T1, T2 green; the grep prints only `_format_value` (L229) | MET | T1/T2 in `test_rate_table_bulk_ops` green. `git grep -n -E 'str\(Decimal\|\.normalize\(\)' -- packages/pricing-core/src/pricing_core/rate_tables` prints one line, `operations.py:697`, inside `_format_value`. `extract_relativity_table` now `format(Decimal(str(...)), "f")`. |
| A5 | limb (ii): every write path refuses, names the first cell, writes nothing; controls pass (L232) | MET for five paths; rebase and seed MET BY READING; route half MET-BY-RECORD; demo half OWED to run 3 | T3 (five paths x `1E+2`, `1.36E-7`, `.5`, message asserts the code, `repr(raw)` and the key) and its control (`1.36e-7`, `1_000`, `5.`) green. Rebase (`operations.py:830` .. `_validate_result`) and seed (`validate_rate_table` after extraction) both reach `_value_issue`, read; they write only computed fixed-point text, so no refusal case exists for them (the LG's disclosed departure). Route tests (`test_api_rate_tables.py`: manual edit, import preview and confirm, status 422, code, per-field error, version count unchanged): not re-run (DB lane); in the gate, `pytest.rc=1` with the 15 failures exactly the eight docs-audit files, skipped 22 = baseline. The demo run is owed to run 3. |
| A6 | compile backstop (L236) | MET | `_refuse_unparseable_cells` after `_refuse_control_factor_keys`; T4 green, message asserts the table ref, the key and `repr(raw)`; control reads. |
| A7 | bit-identical goldens (L238) | MET | T8: 1 207 seeded values, old expression held in the test, `compared >= 500` guard against vacuity; `git diff 2f108b1e...662867bb --stat -- '*golden*'` is empty. |
| A8 | FD-1767 guard green at base and head (L242) | MET | T9 (`int`, `count`) green at head, and re-run with `packages/pricing-core/src` and `backend/src` at `2f108b1e`: `2 passed` (`t9_base.log`). |
| A9 | FD-1780 (L243) | MET WITH ONE DEPARTURE: the `Decimal('NaN')` leg | Two `float('nan')` on one column no longer collide (T10, red then green); NaN against a number still `MODEL_CALL_FEATURE_COLLISION` (both orders); `git diff --numstat` shows 0 deleted lines in `test_rating_column_collision.py`, so the existing two tests are unedited. `Decimal('NaN')` is tested on `_same_value` only, not through `predict`: the LG says the fixture's banding panics in the engine (`pyo3_runtime.PanicException`), which I did not reproduce. **If the lead reads A9 literally, that leg is NOT MET**; I propose a finding for the panic. |
| A10 | FD-1781 (L245) | MET | T11 (`case_property`, `monotone_sweep`): a `TypeError` from `_score_context_sync` gives status `fail` and `run.overall == "fail"`; `NotImplementedError` still propagates (`except NotImplementedError: raise` precedes it). |
| A11 | GREEN set by import closure; SOLO full gate both halves green at the re-merged head; closing acts (L247) | NOT YET MET: gate `rc=125` and the demo owed to run 3; the GREEN-set derivation is not in the LG | The gate at `662867bb`: ruff, mypy, import-linter, req-coverage, contracts rc 0; audit-docs rc 1 (check 32 on an unresolved id fixed by `d5189039`, and check 39 INDEX stale: both the mint's); pytest 15 failed, 7188 passed, 22 skipped, the 15 exactly the eight docs-audit files (item 31); frontend rc 0 (vitest 138 files / 919 tests). The demo stage did not pass: run 1 upstream 503, run 2 capped `rc=124` (dislocation #1 1209 s, D7 not found), run 3 owed. **No item-31 STANDS is possible until run 3 passes.** The seven-file small-run list is hand-picked; item 29 asks for the import-closure derivation, commands and list quoted in the LG, and the LG does not carry it (the full gate is the decisive green). The closing acts below are drafted. |

**Enforcement.** Each new check has printed a failure at its red head, by cause (see A3); T3's controls and T4's controls show the refusal is not a blanket one. Claimed in the LG and not in the diff: nothing found. Claimed in the diff and not in the LG: `cell_parses` catches `(RuntimeError, ValueError)`, the plan's snippet only `RuntimeError`; harmless, undisclosed.

**Gate-record readings** (not re-run): the four `demo-run2` tracebacks read as the journey's negative steps per to-lead "2026-11-05 15:43:06 GMT"; the exposure window per "15:27:35 GMT" (0 `demo/guide` requests in 15:25:50 to 15:26:30).

**Owed, in order:** run 3 (quiet demo, on the mint head) with its line in `### Gate`; the mint's re-run of the eight docs-audit files; the closing acts' placeholders #1436; `docs/INDEX.md` regenerated after the closing acts (item 17).

*Adoption: (the lead's line, dated, at the merge.)*

**Updates at the mint (exec-run3, 2026-11-05, facts only; the verdicts above stay the auditor's proposals):** run 3 PASSED (see `### Gate`: rc 0, 1526 s, dislocation #1 568 s), so A5's demo half and A11's "demo owed" reading are discharged by that run; the GREEN-set derivation A11 found missing is now in `### Gate`; the `cell_parses` `ValueError` catch is disclosed there; the eight docs-audit files and `audit-docs` are re-run at the minted head (their results are in the Build log's closing line).

### Build log

- **2026-11-05 10:46 GMT** branch `sl-8322-r1-rate-table-cells` from a459d49a; spec first (`ca959718`).
- **Red lines, by cause** (base = the commit before each fix):
  - T1/T2 at `7098ddc2`: `5 failed, 47 passed in 8.85s`; `AssertionError: ... {'relativity': '1E+2'} != {'relativity': '100'}`; likewise `'1E+3'` and `'1.36E-7'`.
  - T3 at `a1423996`: `15 failed, 67 passed in 3.60s`; each `Failed: DID NOT RAISE ValueError` (5 paths x 3 cells `1E+2`, `1.36E-7`, `.5`); the control cases `1.36e-7`, `1_000`, `5.` pass.
  - T4 at `28b8c29d`: `3 failed, 25 passed in 3.52s`; `Failed: DID NOT RAISE ValueError` for `1E+2`, `1.36E-7`, `.5`; controls pass.
  - T10 at `68cb58df`: `2 failed, 10 passed in 5.53s`; `AssertionError: assert 'MODEL_CALL_FEATURE_COLLISION' != 'MODEL_CALL_FEATURE_COLLISION'` (float and Decimal NaN).
  - T11 at `68cb58df`: `2 failed, 35 passed in 31.55s`; `TypeError: x` propagates (case property and monotone sweep).
- **Green lines:** T1/T2 `52 passed` (`ddec9ebc`); T3/T4 `82 passed` and `28 passed` (`7fb22005`); T10 `13 passed`, T11 `37 passed`, raise-sites `19 passed` (`1f7338a9` + one `_INPUT_FREE` line).
- **Guards, green at base:** T9 `55 passed` (it touches no changed path); T8's first test compares the old expression against the new on every non-exponent value of a 1 200-value seeded fixture.
- Logs: `~/gi-pricing-plan.local/scratch/sl-8322-r1/`.

## PRs

#1436 (opened by the lead after the push of this branch).

*(Closed by a dated line, 2026-11-06, docs batch 12, by the executor, on to-lead "2026-11-05 22:04:05 GMT" item (5) and common brief item 42: the slice merged as #1436 (`5e5c83f7d4a4`, 2026-11-05); the Audit section above (aud-slr1) was adopted and accepted at to-lead "2026-11-05 16:14:12 GMT" with A11 open on run 3, and run 3's PASS is in `### Gate` (rc 0, 1526 s). The `*Adoption:*` placeholder above is superseded by this line.)*
