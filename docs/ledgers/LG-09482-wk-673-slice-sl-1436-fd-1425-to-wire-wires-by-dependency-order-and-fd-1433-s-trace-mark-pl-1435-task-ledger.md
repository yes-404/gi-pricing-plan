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

### Task 2c, Steps 2 and 4 — the head replay: a DIFFERENCE, so a STOP (RL-1423 conditions A and B)

At head `47e09550`, `replay.py` (sha256 prefix `b43d213cdd4bae7c`), the already-compiled path and the fresh path agree
with each other (both output files sha256 `8c1cec7b09f15a050130a479c66fd4152bf4f22841fdba66084ecefdd3c3ac4c`) and
every `content_hash` equals the base's. Per case, `equal N of N` over (hash line, then `score`, `score_trace`, `raw` per
context): fremtpl2-demo@1 64/64; bench-rating-no-gbm 601/601; bench-score-batch 61/61; bench-compiled-for 61/61;
score-fixture 730/730 (quoted 98, clamp 91, declined 53, error 1); score-fixture-glm 730/730 (all 243 error, unproven
beyond "the error is unchanged"); **bench-rating-gbm 401/601 and bench-trace-size n = 5, 20, 50, 100, 187 each 101/151.**

**All 450 differing lines are `raw` lines of the `model_call` cases** (200 + 5 x 50); **no `score` or `score_trace`
line differs anywhere**, so every served `ScoringResult` is identical, and every `content_hash` is identical. The
difference is the raw engine dict's echo of the quote's own float inputs `f0`..`f7`: the head value is the base
value cut to 15 significant digits (`0.08487199515892163` becomes `0.0848719951589216`; maximum relative difference
measured `1.17e-15`; no other key differs). The cause is read from the diff, not proven: on the chain the context
travels through the `model_call` handler's `request.input` and back, which the engine re-serialises.

**This is a difference outside the FD-1425 fixtures, so it is a STOP for the maintainer (by delegation)** (RL-1423
Condition B; Task 2c Step 4). Nothing was edited, no comparator was loosened. Reported to the lead.

**Timing and the sweep-pause (stated honestly).** The head replay ran once, as one process (`OMP_NUM_THREADS=1 nice -n 19`,
no pytest, no database), started just after the chain commit `47e09550` (commit stamp 22:48:35 UTC = 23:48:35 BST) and
finished 22:49:58 UTC (23:49:58 BST): `head-compiled.jsonl` written 22:49:19 UTC, `head-fresh.jsonl` 22:49:58 UTC (file
mtimes). The base recording had run earlier, finishing 22:42:19 UTC. **The head replay overlapped S7's held gate-1:** I did
not read the slots immediately before starting it, and the maintainer's (by delegation) ruling that Task 2c's replay is a
batch which waits for S7's release reached me after it had run. S7's gate may therefore have been contended during that
window of about 80 seconds. The replay is a run, not a re-run: it is not repeated, and its result above stands. A re-run, if
the maintainer rules one, waits for the release of gate-1.

### The two conditions on ruling (A) — run after S7's gate end (00:15:47 BST; both slots read free before each run)

**(1) The cause, one single-file experiment** (`echo_experiment.py`, scratch directory; one process, `OMP_NUM_THREADS=1 nice -n 19`):
the same float, bench-rating-gbm context 0's `f0`, through (i) an expression node only, and (ii) a `customNode` whose handler
returns `request.input` UNCHANGED. Echoes, verbatim:

```
input         : 0.08487199515892163
(i)  expression: 0.08487199515892163
(ii) handler in : 0.08487199515892163
(ii) handler out: 0.0848719951589216
```

The expression path keeps all 17 digits. The handler **receives** the exact value and the value it **returns** unchanged comes back
cut to 15 significant digits: **(ii) alone truncates**, on the handler's return path into the engine. So (A) stands.

**(2) The downstream-reader check.** Predicate: every committed algorithm step with `"type": "model_call"`
(`grep -rnE "\"type\": *\"model_call\"|type: *model_call|'type': *'model_call'" examples scripts packages backend docs/contracts
--include=*.py --include=*.json --include=*.yaml --include=*.yml -l`, plus `git ls-files | grep -E "\.(json|ya?ml)$" | xargs grep -lE
"\"model_call\""`; and `grep -rnE "RatingModelCallStep\(" --include=*.py packages backend examples scripts`, non-`src/` hits none), then
the steps after it that read a float. Hits: `scripts/bench-rating.py` (`s_risk`, steps listed after it), `packages/pricing-core/tests/
test_rating_score.py:66` (`s_risk`), `test_rating_runtime.py:121`; copies of one shape at `test_rating_compile.py:38, :86`,
`test_rating_compile_bundle.py:49`, `backend/tests/test_rating_algorithms.py:40, :88`, `model-schema/tests/test_rating_algorithm.py:53`,
`test_rating_version.py:105`, which are compiled or saved, never scored through the handler. `examples/` has no `model_call` step
(`grep -rln "model_call" examples` prints nothing). In every scored case the steps after `s_risk` read only `risk_premium_minor`
(an `int`), `driver_age` (an `int`), and `expense_factor` (a rate-table float produced BEFORE the model call, `1.1` and `1.25`,
`test_rating_runtime.py:94-95`: both exact in 15 significant digits) — and, in `bench-rating.py`, `v000`.. (produced after). **No
committed step reads a float input after a `model_call`:** `f0`..`f7` are consumed only by `s_risk` itself.

**Limit (C), for this ledger and the PR body.** An algorithm that, after a `model_call`, reads a float (an input, or a value
produced before the call) carrying more than 15 significant digits would see it cut to 15 digits at the 1e-15 level; none is
committed. A LOW finding (WK-673) by an auditor follows, recording the mechanism proved in (1).

### The gate (2026-10-06, gate-1, one hold, head `e0e2ff2085c370c5b4e011acd84cfd1f632c8cf5`, tree `24595ee9483b0ef2cec32962972752116a7100a8`)

Granted by the lead for that head. `alembic current` == `alembic heads` == `e5b7d9f1a3c6` at the start. The Python half is
`dev-commands`' gate body verbatim, the frontend half follows inside the same `flock` hold (`flock -n -E 99 /tmp/slots/gate-1 env
GIP_GATE_SLOT=/tmp/slots/gate-1 timeout 3500 bash <script>`). The harness moved the foreground call to the background at its 600 s
cap; the wait was on the flock's pid (cwd read as this worktree). Python half 00:20:12 to 00:47:44 BST (start `load average:
2.05, 2.30, 1.93`, free 18048 MB; end 1.53, 1.51, 1.62, free 19609 MB); frontend half 00:47:44 to 00:48:45 BST (end 4.04, 2.15, 1.84).

| stage | result |
|---|---|
| ruff, mypy, import_linter, req_coverage, contracts | pass (exit 0) |
| audit_docs | FAIL (exit 1): only `check 31: gap in the full allocation between 1442 and 9482` (LG 9482 pre-mint) |
| pytest | FAIL (exit 1): `13 failed, 4957 passed, 4 skipped, 86 warnings in 1636.90s (0:27:16)` |
| pnpm install --frozen-lockfile, generate:api, lint, type-check, test, build | all rc 0 |

The 13 failed tests, each failing through audit-docs's check 31 or the `docs/INDEX.md` contiguity gap at 9482:
`test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`,
`test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`,
`test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`,
`::test_the_committed_digest_currently_matches_the_committed_spec`,
`test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`,
`test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`,
`test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`, `::test_check_29_note_carries_the_residue_line`,
`::test_phase1b_residue_count_matches_check_29s_own_count`, `test_register_owed.py::test_check_29_wiring_is_undisturbed`,
`test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`,
`::test_journey_citations_are_audited_in_ci`. The set was not compared with a recorded known set by the executor; the lead compares it.

## PRs

#1228, draft, opened 2026-10-06 from branch `sl-1436-fd-1425-to-wire-dependency-order` (gate head `e0e2ff20`; the
ledger commits after it are docs only). Not merged; the merge is the lead's.
