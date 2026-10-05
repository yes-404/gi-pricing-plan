---
id: LG-9482
family: ledger
title: WK-673 slice SL-1436 — FD-1425's wiring limb, to_wire wires by dependency order, and FD-1433's trace mark (PL-1435), task ledger
status: active
created: 2026-10-05
owner: executor
tree: 23af6997161789887d26f2868a6022a0738e44e6
phase: P2
work: WK-673
slice: SL-1436
plans: [PL-1435]
corrected_by: []
relates: [RL-1423, RL-1434, RL-1263, FD-1425, FD-1433, FR-212, FR-259, WK-673]
---

# WK-673 slice SL-1436 — the wiring limb of FD-1425 and FD-1433's trace mark

Executed from `PL-1435` by `executor-sl1436` (sonnet). Branch `sl-1436-fd-1425-to-wire-dependency-order`. Stamps are
BST (`TZ=Europe/London date`). The dispatch record is `gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1436-2026-10-05.md`
(FINAL; a local file, not in the repository). **FD-1425 stays OPEN in every record until this slice merges.**

## Tasks

### Task 0 — preconditions and the RL vs PL comparison

**Base.** Worktree from `origin/main` `23af6997161789887d26f2868a6022a0738e44e6` (#1226). `uv sync --all-packages` ran.
Test database `gipricing_sl-1436_d9698591` (`createdb -T gipricing`, `alembic upgrade head`); `alembic current` and
`alembic heads` both print `e5b7d9f1a3c6`. PL-1435 and SL-1436 are `active`.

**RL-1434 vs PL-1435:** D1 none (the anchors `RL-916.)* |` and the FR-212 row's closing text each `grep -cF` = 1 in `03`).
D2: T-M1 names WK-1178 where the slice is WK-673; applied as written, per the maintainer's (by delegation) entry
"2026-10-05 22:52:50 BST", which leaves it. D3: the `models.py` comment is Delta 7's; RL-1434 is silent, no conflict.

**RL-1423 vs PL-1435 (T1):** RL-1423's T1 replacement carries the working id "FD 9572" (28 occurrences in the RL);
RL-1423 lines 243-244 say the mint replaces it with the minted `FD-` id. The lead ruled (A): apply `FD-1425`, citing the
maintainer's (by delegation) entry "2026-10-05 19:33:23 BST" (Option A, SL-1427's T2) and RL-1423 lines 243-244.

### Task 1 and Task 2b — the reds, at base commit `23af6997` (tests only, no code change)

Commit `835e0e3d`. `_SCORE_FIXTURE_HASH` was printed twice before it was pasted: both runs
`sha256:86abdb81dc16d2075956aa11e05f2e9c87fe191d4a3397574e5a82520039073d`.

`uv run pytest packages/pricing-core/tests/test_rating_wire_order.py -q` at the base: **8 failed, 6 passed.**

| Test | At base | Cause shown |
|---|---|---|
| `…_topological_twin[ctx0]` | FAIL | `RuntimeError` NodeError on `s_b`, "base + 50" |
| `…_topological_twin[ctx1]` | FAIL | `assert 57 == 350` |
| `…_clamp_listed_before_its_producer_still_binds` | FAIL | `assert 1507 == 5250` |
| `…_no_side_branch_carries_a_stale_copy_into_the_sink` | FAIL | `assert 777 == 5250` (the plan's expected cause) |
| `…_r5_reorder_pair_prices_alike[False]` | FAIL | `assert 777 == 5250` |
| `…_r5_reorder_pair_prices_alike[True]` | PASS | a pin: the instalment step listed early already gave 5250 |
| `…_no_ladder_side_branch…[True-decline]`, `[True-error]`, `[True-terminal_expression]` | FAIL | `assert 300 == 5000` (side branch listed before the clamp) |
| `…_no_ladder_side_branch…[False-*]` (three) | PASS | pins: branch listed after the clamp |
| `…_wires_exactly_as_listed`, `…_bundle_hash_is_unchanged` | PASS | pins (proven able to fail in Task 2 Step 5) |

The no-ladder cases the plan expected might pass: three of the six are real reds (300 against 5000), a case the
auditor's measurement could not reach. No case was weakened. The `(c)` tests of the original Task 1 are PL-1426's and
were not added (Delta 1). The test module drops the `polars`/`score_batch` imports the withdrawn tests used.

### Task 2d — FD-1433: a trace that did not reproduce is marked where it is read (commit `6f4b6f2f`)

Lands **before** the `to_wire` chain change (FD-1433's ordering, GO condition (4)). Base run, alone, the test database
above: `test_a_reproduction_that_differs_from_the_served_quote_is_marked` FAILS with `assert None == 'complete'`.

Applied: T-M1 byte for byte at the end of FR-259's third clarification (`03` row, inserted after `RL-916.)*`), with
`<Task 2d date>` = 2026-10-05; `TraceView.status: Literal["complete", "mismatch"]`, required, set in `_view` from the
row (`cast`, because the model validates the two values at runtime and `mypy --strict` types the column as `str`);
`_filtered` unchanged; the `ScoringTraceRow.blob_sha256` comment corrected (a `mismatch` row whose bundle no longer
resolved has no body); `docs/contracts/openapi/generated.json` regenerated (`TraceView` gains `status`, nothing else;
`generate-contracts.py --check`: "45 generated contracts match the models"). No `model-schema` file, no migration.

Head: `test_traces_api.py` 8 passed, `test_traces.py` 39 passed, no assert edited. Broken `_view` (`status="complete"`
for every row): the new test FAILS at the `quote-differs` assert (the `mismatch` item, `'complete'` against
`'mismatch'`); reverted. `mypy` and `ruff` clean.

### Task 2c, Step 1 — the golden replay, recorded at the base (tests-only tree `835e0e3d`, `runtime.py` unchanged)

Script `replay.py` (sha256 prefix `b43d213cdd4bae7c`; scratch directory, with `base.jsonl`). It records, per case and
context, `score_one` with `trace=False` and `trace=True` (`trace` and `timing_ms` blanked) and the raw engine `result`,
each as canonical JSON, plus every `content_hash`. Cases: fremtpl2-demo@1 (21 contexts), bench-rating-gbm and
bench-rating-no-gbm (200 each, booster 300 rows / 20 rounds), bench-trace-size n = 5, 20, 50, 100, 187 (50 each),
bench-score-batch and bench-compiled-for (20 each), score-fixture and score-fixture-glm (243 each).
`base.jsonl`: 3603 lines, sha256 `19b819f761760779a4e4d9c15304255cd78a10a47fc58d1c82dd27c325d2cc70`.
`score` classes at base: quoted 809, clamp 91, declined 53, error 244. **Unproven class:** `score-fixture-glm` errors
on every context with `MODEL_CALL_FAILED` (a GLM pin has no factors in the bundle, by design at the base), so that
case proves only that the error is unchanged.

### The production-handler census (before the chain commit; the maintainer's (by delegation) ruling (A))

Pattern, verbatim, run at the worktree root on the tree above:

`grep -rnE "customHandler|custom_handler|ZenEngine\(|zen\.ZenEngine|create_decision|\"customNode\"|def handler\(" packages/*/src backend/src --include=*.py`

and `grep -rnE "^import zen|^from zen|import zen" packages/*/src backend/src --include=*.py`. Code hits (prose hits in
docstrings omitted): exactly **one** engine is built, `runtime.py:697` (`zen.ZenEngine({"customHandler": handler})`,
in `load_bundle`), and exactly **one** handler exists, `handler` at `runtime.py:556` inside `_model_call_handler`
(`customNode` is emitted only at `runtime.py:409`). Its three returns: the two failure returns (`:561`, `:594`) go
through `_model_call_failure` (`:138`: `{**context, <zeros>, MODEL_CALL_ERROR_KEY}`), and the one success return
(`:610`) is `{**context, <produced>}`: **all three pass the context through; none drops it.** The other importer,
`compile.py:25`, uses only `zen.compile_expression` (`:320`), a validator, no engine. The only context-dropping handler
in the repository was the test stand-in at `test_rating_runtime.py:345-346`, fixed by the one-line edit below.

**The one test line (ruling (A)).** `test_rating_runtime.py:346` now returns `{"output": {**request.input,
"risk_premium_minor": 5000}}`; the assert at `:351` is untouched; `git diff -U0` of the file shows that line alone.
Before it, `test_to_wire_translates_a_constraint_step` failed with `NodeError` on `s_office` (the stand-in dropped
`expense_factor`); after it the file passes (11 passed).

**Hand-off to A-1, A-2 and A-3 (WK-1178; PL 9599, PL 9597, PL 9595; `_model_call_handler`).** After this slice merges, the
handler returns `{**context, **produced}` on success and `{**context, <zeros>, MODEL_CALL_ERROR_KEY}` on failure. A
branch any of them adds (a GLM branch, a peril-structure branch) returns through that same success expression or through
`_model_call_failure`, never `{"output": {produced names only}}`: on the ordered chain the next step would lose the
context. The one that merges second rebases (merges main) and re-runs `test_rating_wire_order.py` and Task 2c's replay.

### Task 2 / 2b — the chain commit, with T1

T1 is applied to the FR-212 row of `03` in the same commit as the code (`CLAUDE.md` §2), `FD-1425` substituted for the
RL-1423 working id "FD 9572" as ruled (the 19:33:23 BST entry; RL-1423 lines 243-244). After it: `grep -cF` of the
substituted text prints **1**, and `grep -cF 'FD 9572'` over `docs/specs/03-rating-engine.md` prints **0**. At head with
the chain: `test_rating_wire_order.py` 14 passed (the eight base reds all green); pin proofs, each reverted after: a FIFO
in place of the heap fails `test_a_topologically_listed_algorithm_wires_exactly_as_listed` with
`assert ['s_a', 's_d', 's_b'] == ['s_a', 's_b', 's_d']`; the last hex digit of `_SCORE_FIXTURE_HASH` changed fails
`test_the_bundle_hash_is_unchanged` naming both values. `test_rating_score.py` 40 passed, `test_rating_ladder_exact.py`
26 passed, `test_rating_runtime.py` 11 passed (after the one-line stand-in fix above), no assert edited.
