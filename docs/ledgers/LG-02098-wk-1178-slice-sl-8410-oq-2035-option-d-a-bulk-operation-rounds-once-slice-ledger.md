---
id: LG-2098
family: ledger
title: WK-1178 slice SL-2084 — OQ-2035 option D, a bulk operation rounds its exact result once, in a stated context it records (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-08            # original date 2026-11-08, draft under working id 8411; minted 2026-11-08
owner: executor
tree: f80dc9cb96657d223020815fa82006825b6e29bf   # the tree of the gated head 8b6c42466df5 (sl-8410-oq2035-option-d); the gate ran on it, and the one test-only fix f6fa7d18 follows it (the gate START line, "START head: 8b6c4246… tree: f80dc9cb…"); was ba298745f793 (the tree of R2b b196e208), corrected at the mint
slice: SL-2084
phase: P2
work: WK-1178
plans: [PL-2083]
corrected_by: []
relates: [PL-2083, FR-2082, FD-2028, OQ-2035, SL-2084]
---

# LG-2098 — WK-1178 slice SL-2084: OQ-2035 option D

*Disclosure: drafted under working id 8411; minted as LG-2098 on 2026-11-08, in the SL-2084 mint (WK-1178), after SL-2096's LG-2097 (ids in merge order).*

**GO:** the brief `brief-exec-sl8410-2026-11-08.md` (sha256 prefix `223e3453a9d2`), lead 31, on to-lead
"2026-11-07 23:56:36 GMT" (PL-2083 accepted; DP-1 (a), DP-2, DP-3 (a), DP-4 (a); the three LG conditions
C1–C3) and "2026-11-07 23:22:37 GMT", "2026-11-07 23:29:34 GMT". **MERGE-ACK:** (added at merge.)

Every run below is DB-free, through `run-small.sh`, on the executor's own tree
`.claude/worktrees/sl-8410`; each log's first line is `head=<sha>` and its last `rc=<n>`
(`~/gi-pricing-plan.local/scratch/sl-8410/*.log`). `pgrep -af '[d]emo.py|[v]itest'` printed nothing before each.

## Tasks

1. **R1, red first, `a6a00f01`.** `TestABulkOperationRoundsOnceInAStatedContext` (5 tests) appended to
   `packages/pricing-core/tests/test_rate_table_bulk_ops.py`, committed alone.
2. **R2a, `8aedf310`.** `BulkOperationContext` and the three `…RecordedParameters` in
   `model_schema/rating.py`; the three records narrow `parameters`; `TestTheRecordCarriesTheContext`
   (4 tests); `docs/contracts/` regenerated in the same commit. **Departure from the plan:** the plan's R2a
   leaves `operations.py` untouched, but pydantic refuses a parent-class instance in the narrowed field
   (`Input should be a valid dictionary or instance of UpliftTableRecordedParameters`), which made 39 tests
   fail with a `ValidationError` — an error, not the red A2 names. So this commit also swaps the three
   `parameters=` constructors to the Recorded classes **without** a context; R2b adds it. The record's red is
   then a `context` of `None`, as A2 says.
3. **R2b, `b196e208`.** `_result_context`, `_RESULT_CONTEXT_RECORD`; `uplift_table` / `uplift_by_filter` use
   `old.fma(percentage, old, context=context)`, `rebase_to_level` uses `context.divide`; each record carries
   the context. Also fixes RUF043 on R2a's `match=` (R2a's pushed head was `ruff check` red: one error, that line).

## Red first (A2), at base `663d7dcd` + R1 tests (`r1-red.log`: `4 failed, 120 passed`, rc=1)

- `test_a_rebase_below_one_tenth_is_stored_not_refused`: `ValueError: RATE_TABLE_CELL_UNPARSEABLE: value '0.03333333333333333333333333333' for key ('17-20',) is not a number the rating engine can read`.
- `test_the_stored_text_does_not_depend_on_the_callers_context`: `ValueError: RATE_TABLE_CELL_UNPARSEABLE: value '3.37037036703703703670370370367' …` (at `prec=400`; the default context stored `…704`).
- `test_the_factor_is_not_rounded_before_the_product`: `assert '2.2401728372...7283729061729' == '2.2401728372...7283729061728'`.
- `test_every_result_is_the_exact_result_rounded_once`: `ValueError: RATE_TABLE_CELL_UNPARSEABLE: value '0.001817401515196671574266691304' …`.
- **A3 (pin green before and after):** `test_a_money_minor_uplift_holds_the_fraction` is among the 120 passed at base and in R2b's 213.
- **Record red (`r2a-red.log`, after R2a's shape, `6 failed, 122 passed`, rc=1):** the four above, plus
  `test_each_computing_operation_records_its_context`: `assert None == BulkOperationContext(precision=28, places=28, rounding='half_even', version=1)`
  and `test_a_record_from_before_reads_as_no_context`: `KeyError: 'context'`.

## Conditions C1–C3 (to-lead 23:56:36)

- **C1.** A red-first cell below 0.1 (the 28-dp floor): `test_a_rebase_below_one_tenth_is_stored_not_refused`
  (`0.05 / 1.5`, 29 dp), red above, green in R2b. One ≥ 0.1 with more than 28 significant digits:
  `test_the_stored_text_does_not_depend_on_the_callers_context` (`3 × 1.123456789012345678901234567890`,
  `3.37037036703703703670370370367`, 30 digits), red above, green in R2b.
- **C2.** The same operation under `localcontext` `prec` 28, 400, 5 (half-even) and 10 (`ROUND_DOWN`) gives
  the same text: `_CALLER_CONTEXTS` in `test_the_stored_text_does_not_depend_on_the_callers_context`
  (uplift_table, uplift_by_filter and rebase_to_level each). Red at base (above), green at R2b
  (`r2b-green.log`, rc=0). **Mutation proof (`r2b-mutation.log`):** with `uplift_table` and `rebase_to_level`
  put back on ambient arithmetic (`old * (Decimal(1) + percentage)`, `Decimal(...) / reference`) the file gives
  `4 failed, 124 passed`, rc=1 (the four causes above); `operations.py` was restored from a saved copy and
  `cmp` reported it identical.
- **C3.** The pre-change-bytes pin `test_a_bulk_operation_record_dumps_the_bytes_it_dumped_before_the_request_models`
  (`packages/model-schema/tests/test_rate_tables.py`), on R2a's shape: with `exclude_if` (`c3-green_exclude_if.log`,
  `72 passed`, rc=0); with the three fields as a plain `context: BulkOperationContext | None = None`
  (`c3-red_plain_none.log`, `1 failed, 71 passed`, rc=1: `…"0.10"}}` against `…"0.10","context":null}}`).
  `rating.py` restored from a saved copy, `cmp` identical, three `exclude_if` fields back.

## Green (A4) at `b196e208`

`run-small.sh` on `test_rate_table_bulk_ops.py`, `test_rate_table_operations.py`, `test_rate_table_weights.py`
(`r2b-green.log`): `213 passed in 3.44s`, rc=0 (the head line of that log names `8aedf310`, the parent: the
commit was made after the run on the same tree). `TestFormatValueIsBoundedBeforeItIsBuilt` is inside it.
`ruff check .` rc=0 and `mypy` rc=0 (`Success: no issues found in 256 source files`) on the R2b tree;
`lint-imports` rc=0 (`Contracts: 4 kept, 0 broken.`); `generate-contracts.py --check` rc=0
(`58 generated contracts match the models`). `ruff format --check` fails on both changed source files, and
on the test file, **on hunks that predate this slice** (the base files are not format-clean; the CI gate runs
`ruff check`, not `format --check`); the new test code was hand-formatted.

## Commands for A5, A6, A9, A12

- A5: `git -C <wt> grep -n -E 'getcontext|setcontext|localcontext' -- packages/pricing-core/src/pricing_core/rate_tables/` → no output, rc=1;
  `grep -n -E 'Decimal\(1\) \+ percentage|old \* factor|\]\) / reference' …/operations.py` → no output, rc=1.
- A6: `git diff origin/main...HEAD --stat -- packages/model-schema/src/model_schema/money.py` → empty. `_format_value` and `MAX_POSITIONAL_EXPONENT` were not edited.
- A9: `git diff --stat -- docs/contracts` at R2a: `docs/contracts/openapi/generated.json` (136) and `…/schemas/generated/rate-table-version.schema.json` (91) only.
- A12: `git diff --name-only origin/main...HEAD | grep -E '^(frontend/|backend/src/|backend/migrations/)|__init__.py'` → no output, grep rc=1.
- A7: `uv run python scripts/req-coverage.py` rc=0 prints `FR-2082 9 test file(s)` (the nine new tests, all in `test_rate_table_bulk_ops.py`).

## The spike (A14)

Source: `~/gi-pricing-plan.local/scratch/plan-oq2035/spike_ctx.py` and PL-2083's Evidence block. **20,000 of
20,000 pairs equal to an exact-rational oracle**; **606 of 1,999 accepted-today cells differ in the 28th
significant digit for one 30-dp percentage** (relative 1e-27; no payable can move). R1's
`test_every_result_is_the_exact_result_rounded_once` is the in-tree form (2,000 draws, seed 2035).

## GREEN set by import closure (item 29; items 21, 41, 43, 45)

Changed modules: `git diff --name-only origin/main...HEAD -- 'packages/*/src' 'backend/src'` →
`packages/model-schema/src/model_schema/rating.py`, `packages/pricing-core/src/pricing_core/rate_tables/operations.py`.
Closure: those two modules, every `packages/*/src` and `backend/src` module importing one (by `ast`, `import` and
`from … import` names), and one more level: **123 modules**; GREEN = every `test_*.py` under `backend/tests`,
`tests` and `packages/*/tests` importing a closure module: **302 test files** (backend 181, pricing-core 78,
model-schema 41). Script `scratch/sl-8410/closure.py`, list `scratch/sl-8410/green-closure.txt`. Items 43 and 45:
`backend/tests/test_api_authorisation_sweep.py` and `backend/tests/test_error_sinks.py` are both in the list
(the slice changes no route or handler, so the sweep and census are read, not edited). Item 41: nothing under
`scripts/` changed, so no snapshot fixture applies. A11's two API tests are in `test_api_rate_tables.py`, in
the list; they are the gate's. **Owed to the gate:** the 302-file set (DB-backed files included), A10, A11, A13.

## Gate

Source: `~/gi-pricing-plan.local/scratch/sl8410-gate/gate/` (`gate.log`, `pytest.log`, every `*.rc`). The gate
ran on slot gate-1 (pytest redis db 1, demo db 3), START head `8b6c42466df5e6a1597c135a2f43bc036a524f8e`, tree
`f80dc9cb96657d223020815fa82006825b6e29bf` (the branch after the merge of origin/main `81c898c7`, merge 90);
END `2026-11-08T05:27:14+00:00` with `rc=1`. Range `origin/main...sl-8410-oq2035-option-d`: 7 files
(INDEX, the two generated contracts, this ledger, `rating.py`, `operations.py`, `test_rate_table_bulk_ops.py`).

| Row | Result | Source |
|---|---|---|
| ruff check | rc=0 (`All checks passed!`) | `ruff.rc` |
| mypy | rc=0 (`Success: no issues found in 257 source files`) | `mypy.rc` |
| lint-imports | rc=0 (`Contracts: 4 kept, 0 broken.`) | `import_linter.rc` |
| audit-docs | rc=1: one check, **check 31** — `gap in the full allocation between 2090 and 8411` (own working id) | `audit_docs.rc`, gate.log item 31 |
| req-coverage | rc=0 | `req_coverage.rc` |
| generate-contracts --check | rc=0 (`58 generated contracts match the models`) | `contracts.rc` |
| pytest | rc=1: `14 failed, 7607 passed, 28 skipped, 5 xfailed, 156 warnings in 4754.50s (1:19:14)` | `pytest.rc`, `pytest.log` |
| pytest skipped | 28 == baseline 28 (`SKIP_BASELINE` override) | gate.log |
| pnpm install / generate:api / lint / type-check | rc=0 each | `fe-*.log` |
| pnpm test | rc=0: `Test Files  138 passed (138)`, `Tests  919 passed (919)` | `fe-test.log` |
| pnpm build | rc=0 | gate.log |
| demo (`--journey wf-699 --no-compose`) | rc=0, PASS, 1438 s | gate.log |
| D7 | ok — 19985 policies in the sample; rate table edits +485990825; NCD ladder and expense loading +3851186; sum +489842011 minor units | gate.log |
| shared-stack restore | rc=0; keycloak bind source under tools-main | gate.log |
| template guard `gipricing` (start / end) | `alembic_version=1 environments=3 tenant_marker=1`, rc=0 both | gate.log |
| redis db 0 dbsize (start / end) | 56 / 56 (the live db, untouched) | gate.log |
| own-DB and redis zeros | own-DB count=0, db 1 dbsize=0, db 3 dbsize=0 | gate.log |
| infra before/after demo | diff rc=0 | gate.log |
| END rc parts | `python max=1 fe max=0 demo=0 restore rc_kc=0 role rc_role=0 skip rc_skip=0 infra rc_infra=0 template rc_tg=0 db0 rc_db0=0` | gate.log |

**Dislocation.** `dislocation #1 | 539 s` (29 Oct passes 422 / 387 / 383 s; this box 21:17:05 baseline 552 / 558 s).
**QUIET by the lead's census** — `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`, the line beginning
"- 2026-11-08 05:29:53 GMT SL 8410 GATE END read": "Dislocation 539 s QUIET by census: seat exec-mint8406 runs ended 04:59:14
(~/.cache/s8406-*.log mtimes), batch 21 runs 04:47:47; demo 05:03:12-05:27:04 beside it only git ops, a remote gh merge (#1468), pgrep polls".

### The 14 failing tests, by full node id

Thirteen against item 31 (the eight docs-audit files; audit-docs red only on check 31 on this slice's own working id):

1. `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`
2. `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`
3. `tests/test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree`
4. `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`
5. `tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec`
6. `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`
7. `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`
8. `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`
9. `tests/test_register_lint.py::test_check_29_note_carries_the_residue_line`
10. `tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count`
11. `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`
12. `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`
13. `tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci`

The fourteenth is the one real red (item 31's "failing files outside the eight docs-audit files: [backend/tests/test_api_rate_tables.py]"):

14. `backend/tests/test_api_rate_tables.py::test_bulk_operation_creates_a_new_version_with_the_operation_record`
   (`pytest.log` line 10304; the traceback is at lines 109–150):

   ```
   >       assert operation["parameters"] == {"percentage": "0.10"}
   E       AssertionError: assert {'percentage'...'version': 1}} == {'percentage': '0.10'}
   E         Omitting 1 identical items, use -vv to show
   E         Left contains 1 more item:
   E         {'context': {'places': 28,
   E                      'precision': 28,
   E                      'rounding': 'half_even',
   E                      'version': 1}}
   backend/tests/test_api_rate_tables.py:853: AssertionError
   ```

   A11's two named tests (`test_api_rate_tables.py` :863, :896) passed.

## The fix to the one real red

- **RED** = the gate's own failure above (test 14, `:853`): the test asserted the pre-FR-2082 record; under
  FR-2082 (7) the record also carries `context`. A plan miss — PL-2083's A12 write set and gate form said nothing
  outside `operations.py` and its tests reads a bulk-operation record — not a code defect.
- **Ruling**, the maintainer, `to-lead.md` "2026-11-08 05:28:36 GMT": "VERDICT: STANDS WITH ONE FIX, test-only. FIX RULED: at :853
  assert the recorded parameters positively — `{"percentage": "0.10", "context": {"precision": 28, "places": 28, "rounding": "half_even", "version": 1}}`
  — the API-boundary assertion of FR-2082 (7) (not a key-drop or subset compare); PL-2083 gains a dated line under A12/Write set adding
  backend/tests/test_api_rate_tables.py and under the gate form correcting "nothing else reads the record", in the slice PR. [...] No full re-gate."
- **Fix commit** `f6fa7d180a4089553c0e9dbc26b32761a04f7f80` (`test(backend): SL 8410 — the bulk-operation record's parameters carry the FR-2082 context; PL-2083 write set adds the file`).
- **GREEN** is owed to the slice PR's python CI at the merged head, on its Postgres service (the maintainer's either/or:
  no local DB lane; never the shared server). This ledger does not claim it.

## Audit

Folded verbatim from the LG 8411 audit-section draft under `~/gi-pricing-plan.local/scratch/aud-s8406s8410/` (sha256 prefix `872c870d1f04`; item 34).
**Adopted** by lead 31, `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md` "2026-11-08 00:13:01 GMT aud-s8406s8410 FINAL ADOPTED": for
SL 8410 (PL 8409) at 28ca1d53: "A1, A4-A9, A12, DP-1 (a), DP-3 (a), DP-4 (a) MET; A2, A3, A14, C1, C2, C3 MET-BY-RECORD; A10, A11, A13
OWED-TO-GATE. Findings: N1 LOW the accepted R2a deviation's dated line in PL 8409 goes in the spec PR (maintainer 00:07:58); N2 LOW ruff format on
rating.py / operations.py / the test file pre-exists on main: disclosed, item 16 binds only post-gate edits; N3 INFO the branch carries the spec
change: mint once (the spec PR's mint), re-merge after; N4 INFO item 39's spec-reader list owed to the gate LG; FD-2028's dated line + register
row at the mint." The section's own header line below reads "DRAFT — proposal" because it is quoted as written; the adoption is the line above.
(Working ids in the quoted text — "SL 8410", "PL 8409", "FR 8412", "FD 8403" — are as the auditor wrote them; the mint re-points this slice's own.)

DRAFT — proposal. Auditor aud-s8406s8410 (sonnet, medium), Sun 8 Nov 2026. Not adopted until the lead adopts, amends or rejects it (CLAUDE.md §12/§13).

## Audit — SL 8410 (PL 8409, OQ-2035 option D, FR 8412), range `origin/main...origin/sl-8410-oq2035-option-d` @28ca1d534c69

Scope from PL 8409 first (A1–A14, DP rulings, conditions C1–C3 of to-lead "2026-11-07 23:56:36 GMT", rulings 23:22:37 and 23:29:34), then evidence read to the assert (operations.py and rating.py diffs, FR 8412 row in 03, LG 8411).
Own runs (tree = detached worktree `scratch/aud-s8406s8410/w8410` @28ca1d53; pgrep demo/vitest empty before each): `run-small.sh` on the three A4 files → **213 passed in 7.64s, rc=0** (`small-8410.log`); `packages/model-schema/tests/test_rate_tables.py` → **72 passed, rc=0** (`small-8410b.log`); `generate-contracts.py --check` → "58 generated contracts match the models"; `req-coverage.py` → `FR 8412 9 test file(s)` (9 `req("FR 8412")` markers, all in `test_rate_table_bulk_ops.py`); `ruff check` on both packages → all passed; `audit-docs.py` (gate-2 flock) rc=1, ONE failure `check 31: gap in the full allocation between 2077 and 8409` = own working ids; `doc-index.py --check` rc=0.

| Item | Verdict | Evidence |
|---|---|---|
| A1 write set | MET | 12 files: rating.py, operations.py, test_rate_table_bulk_ops.py, 2 generated contracts, LG, PL, roadmap, INDEX, open-questions, specs 03 and 04 (the spec change rides this branch, as the plan's Write set says) |
| A2 red first by cause | MET-BY-RECORD | LG: R1 `4 failed, 120 passed` — rebase `RATE_TABLE_CELL_UNPARSEABLE` on `0.0333…`, ambient `prec=400` unparseable `3.37037036703703703670370370367`, factor-rounded `…729061729` vs `…728`, oracle unparseable; record red `6 failed` after R2a (`context` None; `KeyError`). Not an import/NameError. Logs `scratch/sl-8410/r1-red.log`, `r2a-red.log` |
| A3 pin green before/after | MET-BY-RECORD | `test_a_money_minor_uplift_holds_the_fraction` in base 120 passed and in my 213 |
| A4 green | MET | my run above, 213 passed rc=0 (`TestFormatValueIsBoundedBeforeItIsBuilt` is in the files) |
| A5 no ambient / old arithmetic gone | MET | `git grep -E 'getcontext|setcontext|localcontext'` over rate_tables/ → none; the old-arithmetic grep on operations.py → none (both rc=1, run by me) |
| A6 308 bound untouched | MET | `git diff … money.py` empty; `-U0` diff of operations.py grep count of `MAX_POSITIONAL_EXPONENT|def _format_value` = 0 |
| A7 requirement evidenced | MET | req-coverage line above |
| A8 record carries context, only operation writes it | MET | `TestTheRecordCarriesTheContext` (4 tests) in my 213 run; request classes unchanged so `extra="forbid"` stands |
| A9 contracts follow shape | MET | `--check` rc 0; diff touches only `rate-table-version.schema.json` and `openapi/generated.json` |
| A10 GREEN by import closure | OWED-TO-GATE | LG: 123 modules / 302 test files incl. `test_api_authorisation_sweep.py` and `test_error_sinks.py`; not re-derived by me, not run (many DB-backed) |
| A11 API bound tests | OWED-TO-GATE | `test_api_rate_tables.py` :863/:896, in the gate |
| A12 nothing beyond | MET | no frontend/, backend/src/, backend/migrations/, `model_schema/__init__.py` in the diff (grep rc=1, run by me) |
| A13 gate by Tue 10 Nov 20:00 GMT | OWED-TO-GATE | not started; LG records no gate yet |
| A14 spike quoted | MET-BY-RECORD | LG quotes "20,000 of 20,000" and "606 of 1,999" with source path; the script lives under `scratch/plan-oq2035/` (not re-run) |
| C1 | MET-BY-RECORD | `test_a_rebase_below_one_tenth_is_stored_not_refused` (<0.1) and `test_the_stored_text_does_not_depend_on_the_callers_context` (30-digit ≥0.1); both red at R1 |
| C2 | MET-BY-RECORD | `_CALLER_CONTEXTS` prec 28/400/5/ROUND_DOWN-10, three operations; mutation `4 failed, 124 passed`, restored, `cmp` identical (log `r2b-mutation.log`; I did not repeat it) |
| C3 | MET-BY-RECORD, and re-checked in part | LG: `exclude_if` 72 passed; plain `= None` 1 failed (`"context":null`). I re-ran the green half (72 passed, `test_rate_tables.py`); the red half is the LG's. Code uses `exclude_if=lambda v: v is None` on all three |
| DP-1 (a) | MET | `_result_context()`: prec 28, half-even, `Emin=-1` (Etiny −28), traps InvalidOperation/DivisionByZero/Overflow only; uplift by `fma`, rebase by `context.divide` — exactly the ruling |
| DP-3 (a), DP-4 (a)+`places` | MET | `new == old` keeps the stored text; `BulkOperationContext` has precision/places/rounding/version, frozen, forbid; `floor_and_cap` records none |

### Deviations
1. **R2a also swapped the three `parameters=` constructors to the Recorded classes** (plan said operations.py untouched at R2a). Cause is real (pydantic refuses the parent instance: 39 `ValidationError`s). Ruling covering it: lead 00:07:58 GMT records "SL 8410 deviation accepted by the maintainer (dated line in PL 8409 under R2a, in the spec PR)". **That dated line is NOT in PL 8409 at branch tip 28ca1d53** (`grep` of the PL for a dated R2a deviation line: none) — finding N1.
2. R2a's pushed head was `ruff check` red (RUF043), fixed in R2b — disclosed in the LG; the head 8aedf310 is not a green commit but the branch tip is (`ruff check` passes at tip, run by me).
3. C2 adds prec 5 and ROUND_DOWN-10 beyond prec 400 — per the ruling, MET.
4. `r2b-green.log` head line names the parent 8aedf310, not b196e208 (LG states it; same tree). Common-brief item 37 expects the head of the tree run; the LG says the commit was made after the run on the same tree.

### Findings (proposals)
- **N1 (LOW, record gap).** The maintainer-accepted R2a deviation is not yet a dated line in PL 8409 on this branch. Propose: add it (the lead says it rides the spec PR) before the PR; otherwise the deviation has a ruling in chat only.
- **N2 (LOW, not introduced).** `ruff format --check` fails on rating.py, operations.py and test_rate_table_bulk_ops.py at the head AND at origin/main (base rc=1 for all three, run by me). `ruff format --diff` hunks I looked at are in older code; I could not separate the slice's own hunks mechanically (inconclusive, not a gate command). Propose the lead decides whether item 16 ("ruff format --check on changed files") is waived for these three files or a format hunk-check is run once.
- **N3 (INFO).** The branch contains the spec change (FR 8412, OQ-2035 rows, 04 §4.4, roadmap rows). The lead's log says PR #1462 merged (docs batch 18); whether the spec change reaches main by that PR or by this branch must be read at the merge so FR 8412/INDEX are not double-minted (item 26 idsweep, item 34).
- **N4 (INFO, item 39).** The branch edits `docs/specs/03` and `04`; a code gate covers the spec-reading tests, but the list `grep -lE 'docs/specs|"docs" */ *"specs"' backend/tests tests` was not quoted in the LG. OWED-TO-GATE (read the FAILED block whole).
- No NOT MET items. OWED-TO-GATE: A10, A11, A13; item 39 read.

### Closing acts owed (FD-2028, proposal; not on the branch)
FD-2028 gets a dated line (the PL 8409 hand-off names it): "decided D, `to-lead.md` 2026-11-07 23:22:37 GMT, corrected 23:29:34; fixed by SL 8410 (PR #<N>, squash <sha>)" with its register row at `docs/findings/register.md:450`'s row moved to resolved, and `OQ-2035` already DECIDED in both mirrors. SL 8410's roadmap row is `status: draft`, `tree: ~`: it goes active at the mint and closed on the clean audit and merge (item 42) — read at `origin/main` after the merge.

## PRs

(Added at the PR.)
