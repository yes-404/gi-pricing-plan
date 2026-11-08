---
id: LG-8411
family: ledger
title: WK-1178 slice SL-8410 — OQ-2035 option D, a bulk operation rounds its exact result once, in a stated context it records (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-08            # working id 8411
owner: executor
tree: ba298745f793f274231ee44afcef8f7022b4f696   # the tree of commit b196e208 (sl-8410-oq2035-option-d, R2b; base 663d7dcd of origin/draft/pl-oq2035-2026-11-07)
slice: SL-8410
phase: P2
work: WK-1178
plans: [PL-8409]
corrected_by: []
relates: [PL-8409, FR-8412, FD-2028, OQ-2035, SL-8410]
---

# LG 8411 — WK-1178 slice SL 8410: OQ-2035 option D

**GO:** the brief `brief-exec-sl8410-2026-11-08.md` (sha256 prefix `223e3453a9d2`), lead 31, on to-lead
"2026-11-07 23:56:36 GMT" (PL 8409 accepted; DP-1 (a), DP-2, DP-3 (a), DP-4 (a); the three LG conditions
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
- A7: `uv run python scripts/req-coverage.py` rc=0 prints `FR-8412 9 test file(s)` (the nine new tests, all in `test_rate_table_bulk_ops.py`).

## The spike (A14)

Source: `~/gi-pricing-plan.local/scratch/plan-oq2035/spike_ctx.py` and PL 8409's Evidence block. **20,000 of
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

## PRs

(Added at the PR.)
