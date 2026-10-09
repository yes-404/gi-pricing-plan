---
id: LG-9478
family: ledger
title: WK-673 slice SL-1387 — attribution, exact Shapley, largest remainder, the broken-input proof, the cost (PL-1452), task ledger
status: active
created: 2026-10-08
owner: executor
tree: 8b0256fdb5f000c11817838c129e1f9a4f8d8e10
phase: P2
work: WK-673
slice: SL-1387
plans: [PL-1452]
corrected_by: []
relates: [RL-1445, RL-1449, RL-1451, RL-1263, FR-266, FR-1397, FR-1398, FR-1399, WK-673]
---

# WK-673 slice SL-1387 — attribution: exact Shapley, largest remainder, the broken-input proof, the cost

Executed from `PL-1452` by `executor-s3` (sonnet). Branch `sl-1387-attribution-exact-shapley-largest-remainder`, worktree
`.claude/worktrees/sl-1387`, from `origin/main` `8b0256fdb5f000c11817838c129e1f9a4f8d8e10` (#1238, the activation). The dispatch
record is `gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1387-2026-10-08.md` (FINAL; a local file, not in the repository).
Stamps are BST (`TZ=Europe/London date`). `uv sync --all-packages` ran.

## Tasks

### Task 0 — preconditions (2026-10-08, from 11:20 BST)

**Dispatch tree.** `8b0256fd`, author date `2026-10-08T11:33:16+01:00`.

**Status at that tree** (`docs/roadmap.md`): `SL-1391` closed; `SL-1387` and `SL-1448` active; `SL-1340`, `SL-1341`, `SL-1477`
draft. No WK-1250 slice is active.

**Spec find strings** (`grep -cF -- '<string>' docs/specs/03-rating-engine.md`), each count 1:

| Anchor | Plan/ruling line | Line at `8b0256fd` |
|---|---|---|
| FR-1399 T1/T2 (the `DP-2 (c)` row end) | 192 | 192 |
| FR-1398 T3 (the `DP-1 (a), with its conditions` row end) | 191 | 191 |
| §4.6 P2 (the Slice 1 "reconciled with dislocation-run.schema.json" note) | 516 | 550 |
| §5.2 `async def attribute(baseline: RatingVersion, candidate: RatingVersion,` | 1060 | 1100 |
| §5.2 public-surface paragraph (P4) | 1124 | 1173 |
| `Error codes owned by this module:` | ~928 | 963 |
| P1 old find string (the `require_compilable` ... only-raiser entry) | 965 | **count 0** — the tail moved; re-counted at the P1 re-read ([R]uling 2) |

**Moved code anchors.** `score_batch` `score.py:1135` → `1159`; `AlgorithmDiff` `rating.py:541` → `589`; `diff_algorithms` `571` → `619`;
`_score_pass` `analysis.py:144` and `compile_bundle` `compile.py:573` unchanged; `_raise_named` `compile.py:538`; `analysis.py` has no
`CodedError` or `_raise_named`. `Any` is imported at `backend/src/app/api/rating_algorithms.py:10` (the record says `:18`).
Contract: `dislocation-run.schema.json` `:88-89` ratios are `number` only, `:101` enum has five kinds, `:9` `dependentRequired` as the plan says.

**Baseline** on the untouched tree, both slots free: `pytest packages/pricing-core/tests/test_rating_dislocation.py
packages/model-schema/tests/test_dislocation.py packages/model-schema/tests/test_rating_algorithm.py -q` → `60 passed in 26.68s`, rc 0.
`python3 scripts/audit-docs.py` → rc 0, `All checks passed.`

**Standing blocks.** Task 7 waits for the decision-maker's [R]uling 1 confirmation in the dispatch record. The P1 owned-codes hunk
waits for PL-1471's merge ([R]uling 2).
### Tasks 1 and 2 — the ruled spec texts, `model-schema` deltas and attribution types (2026-10-08)

**Spec texts applied** (`<date>` = 2026-10-08) in `docs/specs/03-rating-engine.md` from the rulings' own texts: RL-1449 T1 then T2 at FR-1399's
row end, then RL-1451 P6; RL-1449 T3 then RL-1451 P5 at FR-1398's row end; P2 after the §4.6 paragraph (`:550`); P4's signature in the
§5.2 `analysis.py` block and its paragraph after the public-surface paragraph. **Not applied yet:** P3 (its `<LEDGER_ID>`,
`<MEASURED_TREE>` and `<SET_1>`..`<SET_6>` are Task 7's figures; it is appended to P2's paragraph in the final commit) and P1
(waits for PL-1471, [R]uling 2). `python3 scripts/audit-docs.py` → rc 1 with check 31 only (`gap in the full allocation between 1477
and 9478`, the working ledger id), as the plan expects before the mint.

**Reds, quoted by cause** (before any production edit):
- `uv run pytest packages/model-schema/tests/test_dislocation.py` → collection error `ImportError: cannot import name 'DeltaKind'
  from 'model_schema.dislocation'`.
- `uv run pytest packages/model-schema/tests/test_rating_algorithm.py` → `test_diff_algorithms_reports_contract_and_output_deltas`
  failed with `AttributeError` (no `input_contract_deltas` on `AlgorithmDiff`); the other ten passed.
- `uv run pytest backend/tests/test_rating_algorithms.py -k typed` → `test_algorithm_diff_route_is_typed_and_keeps_its_keys` failed on
  the `$ref` assertion: the 200 schema was the untyped `{'type': 'object', 'additionalProperties': True, ...}`.
- The contract-side reds, run with the base contract restored (`git checkout 8b0256fd -- docs/contracts/schemas/dislocation-run.schema.json`,
  then back to HEAD) and the new code in place: `test_attribution_ratio_with_zero_denominator_validates_against_the_contract` failed
  `AssertionError: mean_change_pct`; `test_delta_kinds_equal_the_contract_enum` failed on the two missing kinds; `2 failed, 11 passed`.

**Greens.** `test_dislocation.py` and `test_rating_algorithm.py` → `24 passed`; `backend/tests/test_rating_algorithms.py` → `11 passed`
(own database `gipricing_sl-1387_29cf62e3`, made from the template and migrated). `ruff check backend packages/model-schema` clean.

**The hand edit (DP-S3-1 (a)).** `docs/contracts/schemas/dislocation-run.schema.json`: the `kind` enum (`:101`) gains `input_field` and `output`;
`attribution.items` `mean_change_pct` and `cumulative_change_pct` (`:88-89`) become `{"type": ["number", "null"]}`; nothing else in the
file. The `test_contracts.py:98` hand-authored marker stays. `docs/contracts/openapi/generated.json` is regenerated by
`scripts/generate-contracts.py` (`--check` rc 0: `46 generated contracts match the models`), not edited.

**One test edit forced by the new fields.** `test_run_refuses_an_unknown_field` used `attribution=[]` as its unknown field; the field now
exists, so it uses `unknown_field=[]`.

### Tasks 3 to 6 — `derive_changes`, subsets, Shapley, `attribute` (2026-10-08)

**Red first.** `uv run pytest packages/pricing-core/tests/test_rating_attribution.py` before any production code →
`ImportError: cannot import name 'AttributionError' from 'pricing_core.rating.analysis'` (collection error, cause: the names do not
exist; the plan's Step 2 expectation). 27 tests, Acceptance 1-15 and 18's second test (`test_attribute_records_rerate_and_no_fallback`).
Acceptance 18's replay-harness test belongs to Task 7 (the harness is the measurement script) and is not written.

**Green.** `test_rating_attribution.py` 27 passed. With `test_rating_dislocation.py`, `test_quote_input_raise_sites.py` and all of
`packages/model-schema`: `600 passed in 35.54s`. `uv run mypy` → `Success: no issues found in 227 source files`. `ruff check` clean.
`scripts/req-coverage.py`: FR-266 (7 test files), FR-1397 (4), FR-1398 (6), FR-1399 (11).

**Broken-input proof of the tests that cannot be red by absence** (each mutation applied to `analysis.py`, one test run, restored with
`git checkout`):
- the subset's `input_contract` taken from the baseline → `test_subset_contract_carries_the_field_its_own_change_adds` red;
- a subset that fails to compile skipped (`continue`) → `test_attribute_fails_the_run_naming_a_subset_that_does_not_compile` red (`KeyError: 2`);
- a policy not quoted in a subset skipped → `test_attribute_fails_naming_a_policy_not_quoted_in_some_subset` red (`TypeError` on `int(None)`);
- a contract delta attached to the first reader when two read it → `test_delta_with_two_readers_is_its_own_change_and_refused_ungrouped` red.
The reconciliation tests break the allocator, the residual and the Shapley part through seams (`_allocate`, `_residual`) and each
raises `ATTRIBUTION_RECONCILIATION_FAILED` naming `Q000`. The first version of violation 1's test used one group, so no mixed subset
existed (the empty and full subsets are the baseline and candidate by construction); it now has a third change and two groups.

**Choices the plan or ruling left to the executor** (the lead and auditor can reverse any):
- `_Change` is not the plan's field list: it carries `old_step`, `new_step`, `pin`, `fields`, `outputs`. The pins of a subset are
  derived from the subset's steps (a pin the candidate dropped is removed once no subset step names it), so two steps sharing a ref
  cannot leave one pinless.
- The subset algorithm for no changes is the baseline object and for every change the candidate object, so RL-1449 violation 2 holds
  by content hash; a mixed subset is the baseline's order with substitutions and additions appended.
- The synthetic algorithm ref is served with the baseline algorithm's resolved status: `rating_algorithm` is exempt from the maturity
  floor (`compile._MATURITY_CHECK_EXEMPT`, RL-859) and no maturity order exists to take "the lower of the two" by.
- `cumulative_minor` is the declared-order marginal, `v(prefix i) - v(prefix i-1)`, because §4.6's example sums to the total.
- `Attribution.change_groups` carries the analyst's groups as given (empty when none were), because above 6 changes a one-per-change
  list would break the `maxItems` 6 bound of the model and the contract.
- Every subset is compiled before any is rated, so a compile failure rates nothing. A compile failure is any `ValueError`
  (`CodedError` and a model validation error both are), so `analysis.py` imports no `CodedError` and calls no `_raise_named`.
- `estimate_attribution_ratings(..., grouped=True)` with k above 6 raises `ValueError`: groups are at most 6.

**Not done, by name.** P3 (§4.6, its placeholders are Task 7's figures) and P1 (owned-codes tail, waits for PL-1471) are not in the spec
yet. Task 7, and with it Acceptance 18's replay test, 19, 20 and the `examples/fremtpl2/rating/` fixture, waits for the [R]uling 1
confirmation. The full gate (Task 8) waits for the lead's slot grant.

### Task 6b — choice 3 clarified in FR-1399; the choice-1 comment (2026-10-08, executor-s3b)

**Authority.** The maintainer (by delegation), "2026-10-08 12:16:26 BST — S3 (SL-1387, #1243) choice 3, change_groups: RULED (a)"; no OQ, no RL.
**Spec.** One dated sentence group appended to FR-1399's row end in `03` ("Clarified 2026-10-08"; `grep -cF` of its anchor = 1): `change_groups` holds
the analyst's groups only and is `[]` when none are given; the implicit groups are the derived changes in derived order, one item each.
**Tests (no new test; the rule is pinned by existing ones, extended).** `test_isolated_and_cumulative_views_and_residual_line` (K = 3, no groups:
`shapley`, items `c1, c2, c3` in derived order, sums equal the total) gains `change_groups == []` and the derived-id order;
`test_above_six_ungrouped_is_order_dependent_with_r_and_s_bound` (K = 7: `order_dependent`) gains `change_groups == []` and items in derived order.
Both were green before the extension (the code already did this), so a red is by mutation: `analysis.py`'s `attribute` writing the implicit groups
(`groups[:6]`) to `change_groups` → both tests red on `assert result.change_groups == []`; restored with `git checkout`.
**Choice 1 comment.** `analysis.py` before `status = (await resolver.resolve(baseline.algorithm_ref)).status` names DP-S3-8 (a), RL-859 and the tripwire test.
**Node ids.** `packages/pricing-core/tests/test_rating_attribution.py::test_isolated_and_cumulative_views_and_residual_line` and
`packages/pricing-core/tests/test_rating_attribution.py::test_above_six_ungrouped_is_order_dependent_with_r_and_s_bound` (the ruling's item 2).
**Reflow.** `ruff format` reflowed existing lines in `test_rating_attribution.py` (commit 1d91cdfd, `git diff 1d91cdfd~1 1d91cdfd -U0`): every hunk is
reflow only except the two assertion additions (new-file lines 586-587 and 680-681). `analysis.py`: reflow plus the comment.
**INDEX.** `docs/INDEX.md` regenerated with `scripts/doc-index.py` (check 39 was stale after the ledger edit); `audit-docs.py` then FAILED (1): check 31 only.
**Also.** `ruff format` on `analysis.py` and `test_rating_attribution.py` (an E501 at the earlier `step_added` assertion); `ruff check packages/pricing-core` clean.

### Task 7 preparation — fixture, harness, replay test (2026-10-08, executor-s3b; NO measurement run)

**Authority.** [R]uling 1 (b'), confirmed with five conditions by dm-s3 (dispatch record §(2), 12:14:08 BST). The measurement is not started; it
runs alone overnight 9 to 10 Oct on the lead's slot grant.

**The fit (condition (i)).** `uv run python scripts/measure-attribution-cost.py fit` (rc 0, 18 s). Data: `examples/fremtpl2/data/freMTPL2freq.arff`,
sha256 `a45363e056e2ea56408b38eeb9d4d04d7f6c6982eb7a14ed5e807c7c71807cdd` (the pin in `fetch.py`; the file was copied from the root checkout's gitignored `data/` and its digest checked),
678013 rows, 36102 claims. `glum` 3.4.1, `polars` 1.44.2. Poisson, log link, `alpha=0`, y = ClaimNb / Exposure
weighted by Exposure (exposure clipped at 1). Base frequency exp(b0): freq_v1 `0.019369349543`, freq_v2 `0.025586326426`. Both coefficient
vectors are in `examples/fremtpl2/rating/fremtpl2-fit-record.json` (53 and 59 coefficients). Table values are written to
8 decimal places, the base frequency to 12.

**Condition (ii), the feature list (the fixture defines it).** freq_v1: area (6 levels), veh_power (int 4..12, clipped at 12), age_band (8), veh_brand,
region, bonus_malus (int key, every value 50..150, exp(b*x)), density (int key, every one of 1607 distinct values in the file,
exp(b*log d); `on_miss: error`). freq_v2 adds veh_gas and veh_age_band (VehAge clipped at 15, floor-divided by 3: int 0..5). One field per term, no
interactions, no `interpolation`. This is RS-1201's `prep` list (`spike/run.py` at `46ecb632`, lines 29-37); the dispatch record's remark that the spike
does not record it is not right for `run.py`. Reference level of a categorical is its first sorted level, relativity 1.0.

**Condition (iii), disjoint steps.** Member 0: the seven frequency tables (repointed v1 to v2), `s_freq` (new base and two more relativities), the new inputs
`s_in_veh_gas`, `s_in_veh_age_band` and the new tables `s_t_veh_gas`, `s_t_veh_age_band` (with the two contract fields): one group. Member 1: `s_age` only.
Member 2: `s_risk` only (severity). Member 3: `s_load`. Member 4: `s_floor`. Member 5: `s_cap`. No step belongs to two members.
**Condition (iv)**: `fremtpl2-rate.changes.json` carries the members' steps and the six sets; `groups_for` builds one `ChangeGroup` per member.
**Condition (v)**: no GLM artifact, no `model_call`, no `pins.models`; every file under `examples/fremtpl2/rating/` starts `fremtpl2-`.

**Two departures from RS-1201's `rate()`, forced by the engine, disclosed.** (1) The engine allows one `clamp` per ladder rung (two clamps on one name are a
DAG cycle; a clamp elsewhere is `LADDER_CLAMP_UNPLACEABLE`). The minimum premium is the clamp (`s_floor`). The cap is an expression `min([pre_cap, current_premium * f])`
ahead of the loading rung (`s_cap`), present in the baseline with f = 1000 (it cannot bind) and edited to 1.25 by member 5; it caps the premium before the
age adjustment, not after the floor as RS-1201 did. (2) The age relativity is its own rung (`profit_loading`) after the expense loading, so it is a
separate ladder operation. The input `current_premium_minor` is the baseline's own payable premium (`portfolio_for`), as RS-1201's cap was relative to the baseline premium.

**Tests (all written after the files they test, so each red is shown against the base).**
- `packages/pricing-core/tests/test_fremtpl2_rate_fixture.py::test_every_fixture_file_loads_and_compiles`: red with `examples/fremtpl2/rating/` moved away
  (`2 failed`, FileNotFoundError); green with it (`2 passed`).
  `::test_member_zero_is_one_group_and_the_catalogue_partitions_the_derived_changes`: the six groups partition the derived changes exactly, member 0 holds 7 `table_repointed`.
- `packages/pricing-core/tests/test_rating_attribution.py::test_replay_that_differs_from_a_true_rerate_is_detected_and_recorded` (Acceptance 18, first test): red with
  `scripts/measure-attribution-cost.py` moved away; red with `replay_subset`'s multiply broken (`value *= factor + 1`); green with the script. It first
  returned a vacuous pass: the book's int keys were strings and every policy was `INPUT_CONTRACT_VIOLATION`; it now asserts all 30 policies are quoted.
  Finding in the data: replay equals every true re-rate on the linear subsets and on the whole set (1, 2, 4), and differs on subsets holding the minimum premium
  without the age change ((4,): Q000 off by minor units): the candidate ladder records no clamp where the full set lifts the policy above the floor.
- Suite: `test_fremtpl2_rate_fixture.py` and `test_rating_attribution.py` together `30 passed in 53s`; `ruff check packages/pricing-core scripts/measure-attribution-cost.py` clean;
  `mypy` 227 files clean; `lint-imports` 4 kept, 0 broken.

**Smoke runs (tiny; they prove the harness runs, they are NOT the measurement and are not timings to cite).** `sets --policies 300`: all six sets run end to end, K = 3
to 6 `method: shapley`, 6 to 46 s (compile-dominated at this size). `replay --policies 60`: sets 0,1,4,5 and 1,2,4 are step-aligned (replay 3 to 7 ms, re-rates 2.4 to 5 s, 0 mismatches
on that book), the other four are not (members 0 and 2 feed one rung).

## Merge of origin/main, the S2 overlap, and the P1 hunk (2026-10-09)

**Merge.** `origin/main` 2e766906f8f57d47b458e218a787a404a3f54286 merged into the branch at 5da13384 as a80ac4971a214767d6ec9ec1923c62197f5c2ad9. `git merge-tree --write-tree origin/main HEAD` exit 1, four conflicts: `backend/src/app/api/rating_algorithms.py`, `backend/tests/test_rating_algorithms.py`, `docs/INDEX.md`, `docs/contracts/openapi/generated.json`. `03` and `packages/model-schema/src/model_schema/rating.py` auto-merged: S2's `rating.py` hunks are at `RatingAlgorithm` (about :423-460), this slice's at `InterfaceDelta`, `AlgorithmDiff`, `diff_algorithms` (from about :609); disjoint.

**RL-1445 overlap note.** RL-1445: the S2 (SL-1477) / S3 write-set overlap on backend/src/app/api/rating_algorithms.py and backend/tests/test_rating_algorithms.py was not flagged when S2's write set was approved (to-lead 2026-10-09 10:48:20 BST).

**Per-file resolution.**
- `rating_algorithms.py`: S2 contributed the `model_schema` import block (`Permission`, `RatingAlgorithm`, `RatingAlgorithmDraft`, `RatingAlgorithmSaved`), typed `create_rating_algorithm` and the new `get_rating_algorithm` route. S3 contributed `from model_schema.rating import AlgorithmDiff` and `algorithm_diff`'s `-> AlgorithmDiff`. Both imports kept; `Any` is now unused and is dropped from `from typing import Annotated, Any`.
- `test_rating_algorithms.py`: base 10 tests, S3 adds 1 (`test_algorithm_diff_route_is_typed_and_keeps_its_keys`), S2 adds 8; merged file has 19, none dropped.
- `docs/INDEX.md` regenerated by `scripts/doc-index.py`; `generated.json` by `scripts/generate-contracts.py`.

**P1 (RL-1451's text, the dispatch record's second ruling).** PL-1471 merged as 7e3a4803 (an ancestor of the merged tree). Owned-codes tail re-read at the merged tree: `docs/specs/03-rating-engine.md` line 1012, `between submit and run; the detail names the diff)*.`; `grep -cF` of that anchor = 1. The FD-1421 code `MODEL_REFERENCE_MODE_INCONSISTENT` is already on the list (line 978). P1 appended after the tail with date 2026-10-09; the tail's full stop became a comma.

## Gate 1 on the merged tree: three reds beyond the check-31 set (2026-10-09)

Gate at d15b8ecf, 11:00:16 to 11:44:30 BST: pytest 16 failed, 5167 passed, 3 skipped; 13 failures are the check-31 set (audit-docs and its dependants). The other three, each reproduced alone, and the lead's rulings (to-lead relay, 2026-10-09):
- `examples/fremtpl2/test_seed.py::test_the_seed_reruns_against_a_seeded_database`: environmental. This worktree's `examples/fremtpl2/data/` lacked `freMTPL2sev.arff` (the root checkout has it); `git check-ignore -v` shows `.gitignore:61 examples/fremtpl2/data/` ignores it. Cause: the data dir is untracked and was fetched only partly in this worktree. Fix: `cp` of the file from the root checkout's data dir, left untracked. Re-run alone: 8 passed.
- `packages/pricing-core/tests/test_rating_committed_strings.py::test_every_committed_string_is_accepted_or_a_declared_negative`: the extractor's line regex read `expr = " * ".join(...)` in `scripts/measure-attribution-cost.py` as an expression string `' * '`. Fix, a WORKAROUND for an extractor false positive and not a root-cause fix: the local variable is renamed `prod` (rename only; the joined expression and the step dict are unchanged). The `" * "` literal is still committed. It passes only because the extractor's line regex `_KEY` (`packages/pricing-core/tests/test_rating_committed_strings.py:43-46`) keys on the names `condition`, `expr` and `key_expr`, so it reads any line of the form `expr = "<literal>"` as an expression string and a join separator on such a line is a false positive. The limitation is the class of FD 9460 (working id, filed in D1: the extractor's handling of non-expression literals); the lead routes it. Neither test file is in PL-1452's write set, so neither was touched.
- `backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for`: `analysis.py` `attribute` put `{exc}` of a compile `ValueError` into `AttributionError`'s message, and a validation error's text can carry input values (NFR-499). Fix: `safe_error_text(exc)` from `pricing_core.safe_error` (the allow-list: our coded errors keep their text, a validation error is rebuilt from declared parts, anything else is its type name). `safe_error_text` and not `safe_error_detail` because it returns the type name when the detail is empty, so a non-coded error still names its class. No `_SINKS` line was needed.
After both fixes: the three tests and `test_rating_attribution.py`, `test_fremtpl2_rate_fixture.py`, `test_quote_input_raise_sites.py` pass (57 passed together; 36 passed after the final rename for the three most affected files); ruff, ruff format, mypy and lint-imports are green. Not pushed; re-gate follows the lead's slot grant.

## Task 8 — full gate at dc99d377 (2026-10-09)

GATE START 12:02:07 BST, GATE END 12:45:45 BST, under the `/tmp/slots/gate-1` flock, head dc99d377 (the merge of origin/main 2e766906, P1, the three red fixes). Per-command rc: ruff 0, mypy 0, lint-imports 0, audit-docs 1 (check 31 only: gap between 1533 and 9478), req-coverage 0, generate-contracts --check 0, pytest 1 (13 failed, 5170 passed, 3 skipped, 41m51s; the 13 are the check-31 set), frontend install, generate:api, lint, type-check, test (102 files, 653 tests) and build all 0. The first gate at d15b8ecf had 16 failures; the three extra are the reds fixed above.

## Task 7 run — where the output lands (written before the run, 2026-10-09, executor-s3e)

**Script change before the run.** `scripts/measure-attribution-cost.py cost` gained `--score-policies N` (score_batch N-run median on the first N policies; 0 skips), `--ks 3,4,5,6` and `--rate` (policies per second for the DERIVED lines when score_batch is not run in the call); and a bug in it is fixed (`f["name"]` on an `InputContractField` raised `TypeError`; now `f.name`), found by a 400-policy smoke run before the measurement (not a timing). No other file changed.

**The run.** One driver, `/home/puzhenhao1989/gi-pricing-plan.local/task7-s3e/run-task7.sh` (local, not in the repository; its text is below), started detached (`setsid nohup`) inside the gate-1 flock, so it keeps running if this seat stops:

```
flock -w 60 /tmp/slots/gate-1 setsid nohup /home/puzhenhao1989/gi-pricing-plan.local/task7-s3e/run-task7.sh > /home/puzhenhao1989/gi-pricing-plan.local/task7-s3e/out/driver.log 2>&1
```

Blocks in order, each writing its own file under `/home/puzhenhao1989/gi-pricing-plan.local/task7-s3e/out/`: `01-k3-score.jsonl` (score_batch N=5 on all 678,013 policies, then K=3 re-rates N=5 on the first 20,000; the K=3 timing reported first), `02-k4`, `03-k5`, `04-k6` (N=5 each on 20,000, DERIVED lines from the block-1 rate), `05-sets.jsonl` (the six sets, S and R, 20,000 policies), `06-replay.jsonl` (2,000 policies), `07-full-k3.jsonl` (K=3 on all 678,013, N=1, the linearity check). `*.err` holds stderr. Progress and per-block load1 and start/end stamps (UTC and BST): `out/progress.log`; `DRIVER DONE` is its last line on success, `STOP load1=…` or `END <block> rc=<nonzero>` on a stop. The driver refuses to start a block when load1 >= 12 (exit 3) and each block has `timeout 14400`.

**How to read.** One JSON object per line: `what` (`score_batch`, `attribute`, `derived`, `set`, `replay`), `k`, `policies`, `seconds` (median of `runs`), `load1`, `tree`, `stamp`. A `derived` line is DERIVED (2^K x 678013 / rate), never measured, and draws no NFR verdict.

**If this seat stops mid-run.** The driver is not tied to it: `tail out/progress.log`, `flock -n /tmp/slots/gate-1 true` (rc 1 = the run still holds the slot), `pgrep -f '[r]un-task7.sh'`. Do not start a second run, a gate or a sweep while it holds the slot. When `DRIVER DONE` is the last progress line, collect the figures from the `.jsonl` files into this ledger's Task 7 entry (Step 4: the NFR text with the three under-statements of the dispatch record §(2), both fixture departures beside the figure, Acceptance 20 as narrowed at 12:44:19), commit, and push once. A block that stopped with a nonzero rc is re-run alone by hand with the command line in its `START` progress line.

Driver text:

```bash
#!/bin/bash
# WK-673 S3 Task 7 measurement driver. Run under the gate-1 flock. Output: out/*.jsonl, out/progress.log.
W=/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1387
O=/home/puzhenhao1989/gi-pricing-plan.local/task7-s3e/out
M="uv run --directory $W python $W/scripts/measure-attribution-cost.py"
log() { echo "$(date -u +%FT%TZ) $(TZ=Europe/London date +%T) BST load1=$(cut -d' ' -f1 /proc/loadavg) $*" >> $O/progress.log; }
guard() { l=$(cut -d' ' -f1 /proc/loadavg); if awk "BEGIN{exit !($l>=12)}"; then log "STOP load1=$l >= 12 before $1"; exit 3; fi; }
blk() { name=$1; shift; guard $name; log "START $name: $M $*"; timeout 14400 $M "$@" > $O/$name.jsonl 2> $O/$name.err; rc=$?; log "END $name rc=$rc"; [ $rc -eq 0 ] || exit $rc; }
log "DRIVER START"
blk 01-k3-score $(echo cost --policies 20000 --score-policies 678013 --ks 3 --runs 5)
log "BLOCK1_DONE"
RATE=$(python3 -I -c "import json,sys;print([json.loads(l) for l in open('$O/01-k3-score.jsonl') if '\"score_batch\"' in l][0]['policies_per_s'])")
log "rate=$RATE"
blk 02-k4 cost --policies 20000 --ks 4 --runs 5 --rate $RATE
blk 03-k5 cost --policies 20000 --ks 5 --runs 5 --rate $RATE
blk 04-k6 cost --policies 20000 --ks 6 --runs 5 --rate $RATE
blk 05-sets sets --policies 20000
blk 06-replay replay --policies 2000
blk 07-full-k3 cost --policies 678013 --ks 3 --runs 1 --rate $RATE
log "DRIVER DONE"
```

## Task 7 run — block 1 stopped, the rate probe (2026-10-09, executor-s3e)

**Concurrent load disclosure.** From about 15:2x BST three authoring seats ran small single-file tests beside the run (nice 19, one at a time via `/tmp/slots/small-test`, at most 2 min each; the lead's ruling at to-lead 15:22:26 BST item 3). load1 is recorded per invocation in `out/progress.log`.

**Block 1 stopped (no figure).** Driver started 14:02:18 BST (load1 0.79) on `cost --policies 20000 --score-policies 678013 --ks 3 --runs 5` at tree `088a0c23`. The lead stopped it with `kill -TERM -- -707382` at 15:56:31 BST under the maintainer's authority (to-lead 15:56:07 BST, STOP AUTHORISED); progress.log: `END 01-k3-score rc=143` (load1 2.68). Elapsed 1h54m13s; output file 0 bytes ("no line emitted"). Cause: `cmd_cost` emits its first line only after all `--runs` score_batch passes, so with 5 passes over 678,013 policies no projection was possible. The probe below puts one pass at about 23.5 min, so the five passes alone (about 118 min) fit the elapsed time.

**Per-invocation design from here (no script edit).** Each invocation is `/home/puzhenhao1989/gi-pricing-plan.local/task7-s3e/inv.sh <name> cost ...` under its own gate-1 flock, own file `out/<name>.jsonl`, own START/END progress lines, `--runs 1`.

**(i) Rate probe** `cost --policies 20000 --score-policies 50000 --ks 3 --runs 1`, START 15:57:23 BST (load1 1.43), END 16:11:32 BST (load1 2.11), rc 0, wall 14m09s, file `out/10-rate-probe.jsonl`:
- score_batch, 50,000 policies, 1 run: 104.03 s = **480.65 policies/s** (load1 2.56). Not the 1414/s planning rate: 2.9x slower.
- attribute K=3, 20,000 policies, 1 run: 363.92 s (8 re-rates x 20,000 = 160,000 ratings, 440 ratings/s).
- DERIVED K=3 full portfolio: 2^3 x 678,013 / 480.65 = 11,285 s (3.13 h). DERIVED, no verdict.
- About 8 min of the wall time is setup before the first score (portfolio build and compile), not a rating cost.

**Projection at the observed rate (DERIVED, linear in ratings).** One score pass over 678,013: 23.5 min. K=3/4/5/6 on 20,000 policies, one run each: 364, 728, 1,456, 2,912 s (about 91 min together); N=5 of those: about 7.6 h. Five full score passes about 2 h; the full-portfolio K=3 run about 3.1 h. Plan total about 12.8 h at N=5, past the 6 h STOP of the brief. Reported to the lead; nothing further started.

**(a) Rate probe at 20,000** (the lead's ruling, by flags only): `cost --policies 20000 --score-policies 20000 --ks 3 --runs 1` (`out/11-a-probe20k.jsonl`), START 16:12:14 BST (load1 1.50), END 16:22:24 BST (load1 2.32), rc 0, tree `7dba2d11`: score_batch 20,000 policies = 41.17 s = **485.76 policies/s** (50,000 policies gave 480.65; the two agree within 1%); attribute K=3, 20,000 policies, 1 run = 370.86 s. One score pass over 678,013 projects to 678,013 / 485.76 = 1,396 s = 23.3 min, within the 45 min test, so step (c) (one timed full-book pass) stays in the plan, last.

**(b) K = 3 runs** are separate invocations, each under its own gate-1 flock, driver `loop-k.sh` (local, next to `inv.sh`): `cost --policies 20000 --ks 3 --runs 1 --rate 485.7552475841824`, files `out/23-k3-r1.jsonl` to `r5`; `--rate` is (a)'s rate, used only for the DERIVED lines.

**K = 3 block result (b).** Five invocations, 16:22:38 to 17:01:39 BST, all rc 0, load1 at END 2.85, 1.92, 1.92, 2.60, 1.80 (none above 4.0), tree `7dba2d11`/`59e24c85`: attribute K=3 on the first 20,000 policies: 372.20, 364.28, 351.89, 400.11, 366.85 s; **median 366.85 s** (`out/23-k3-r1..r5.jsonl`).

**K = 4 block result.** Five invocations `cost --policies 20000 --ks 4 --runs 1 --rate 485.7552475841824`, 17:01:57 to 18:11:14 BST, all rc 0, load1 at END 1.96, 1.55, 2.72, 1.85, 2.07: 742.40, 768.35, 702.56, 734.73, 733.90 s; **median 734.73 s** (`out/24-k4-r1..r5.jsonl`). K=4 / K=3 = 2.00 (the expected 2^K ratio is 2.0).

## Task 7 run — K = 5, K = 6, the full-book score_batch, the scaling curve, the linearity check (2026-10-09, executor-s3f)

**Seat change and N, disclosed.** executor-s3e was replaced by executor-s3f at about 18:13 BST (the lead's brief, under the maintainer's 18:12:40 authority, items 3 to 5). The loop `loop-k.sh 5 5` was ended by the lead at 18:12:56 BST, so K = 5 has **N = 1** (`25-k5-r1`), not 5. K = 3 and K = 4 ran at **N = 5** (above R2's N = 1) and are reported as N = 5. Every figure below carries its N, load1 and tree `f59b546e`. All runs were alone in the gate-1 slot; no small test ran beside them (ruling 16:12:53 item 2). Raw files: `~/gi-pricing-plan.local/task7-s3e/out/*.jsonl`, `progress.log` (local, not in the repository).

**Harness copies (not the measured script; `scripts/measure-attribution-cost.py` is unedited).** `inv-long.sh` = `inv.sh` with `timeout 7200` instead of `3600`. `inv-rss.sh` = `inv-long.sh` run through `python3 -I -c 'subprocess.run(["timeout","7200","uv","run",…])'`, which prints `resource.getrusage(RUSAGE_CHILDREN).ru_maxrss` (KiB) beside the END line; `timeout` and `uv` wait for the python grandchild, so Linux folds its maximum in (the number is plausible: 6.2 GiB for 200,000 policies, 11.9 GiB for 400,000). `/usr/bin/time` is not installed. Peak RSS was not captured for the 20,000 and 50,000 runs.

**K = 5 and K = 6 (attribute, first 20,000 policies by `quote_id`, N = 1 each).**

| K | N | seconds | load1 at END | ratio to previous K |
|---|---|---|---|---|
| 3 | 5 | 366.85 (median; 351.89 to 400.11) | 1.80 to 2.85 | |
| 4 | 5 | 734.73 (median; 702.56 to 768.35) | 1.55 to 2.72 | 2.00 |
| 5 | 1 | 1,527.04 (`25-k5-r1`, 18:11:26 to 18:38:36 BST) | 2.41 | 2.08 |
| 6 | 1 | 3,024.77 (`26-k6-r1`, 19:39:30 to 20:31:37 BST) | 1.78 | 1.98 |

The ratios agree with the expected 2.0 per extra group. N = 1 shows no spread; the K = 3 spread (N = 5) is 351.89 to 400.11 s, ±7%.

**Linearity check (100,000 policies, K = 3, N = 1).** `40-lin-r1`, 20:31:44 to 21:12:27 BST, rc 0, load1 2.29: **1,983.42 s**. Against K = 3 on 20,000 (median 366.85 s, N = 5): 5.00x the policies took 5.41x the time, 8% above linear. Inside the K = 3 N = 5 band scaled by 5 (1,759 to 2,001 s). N = 1: no spread at 100,000.

**score_batch alone (`cost --policies 1000 --score-policies <N> --ks "" --runs 1`; `--ks ""` runs no attribute; the `--policies 1000` book is built and unused).**

| policies | N | seconds | policies/s | peak RSS | load1 | invocation wall |
|---|---|---|---|---|---|---|
| 20,000 | 1 | 41.17 | 485.76 | not captured | | |
| 50,000 | 1 | 104.03 | 480.65 | not captured | | |
| 200,000 | 1 | 424.86 | 470.74 | 6,513,848 KiB (6.21 GiB) | 2.45 | 24.2 min |
| 400,000 | 1 | 848.41 | 471.47 | 12,515,908 KiB (11.94 GiB) | 2.80 | 45.9 min |

The rate is flat from 200,000 to 400,000 (3% below the 50,000 figure); peak RSS is about 31 KiB per policy. The invocation wall time exceeds the scoring time by 17 min at 200,000 and 31.8 min at 400,000: book build and compile, untimed by `cost`, about 4.8 min per 100,000 policies.

**The full book (678,013 policies) was not completed within 60 min (two runs).** (1) `01-k3-score`, `--score-policies 678013 --ks 3 --runs 5`: stopped by the lead at 114 min, no output. (2) `30-score-r1`, `--score-policies 678013 --ks 3 --runs 1`, started 18:38:57 BST: killed by `inv.sh`'s inner `timeout 3600` at 19:38:57 BST (18:38:57 UTC), no output (both files 0 bytes). `cmd_cost` builds the score book once per invocation (`sbook = portfolio_for(fx, args.score_policies).collect().lazy()`, then the bundle compile; `portfolio_for` itself rates the whole book once through `dislocation_frame` to set `current_premium_minor`, which is the untimed "build") and scores it `--runs` times in a loop, emitting only after the loop. DERIVED, not measured: about 54 min of build and compile plus a single scoring pass of 678,013 / 471.47 = 1,438 s (24.0 min) is about 78 min per single-pass invocation, so run (2) at 60 min was still in its build or first pass; run (1) was `--runs 5`, about 54 + 5 x 24 = 174 min, so at 114 min it was in roughly its third scoring pass, not stalled (the lead's reading, 2026-10-09; consistent with the code and the derived overhead); peak RSS about 20.3 GiB by linear scaling of the 400,000 figure, on a 31 GiB box. The earlier 23.5 min projection (rate probe) counted scoring only. The rate finding is FD 9446 (draft `draft/fd-9446` at `08f50d11`).

**An error of mine, disclosed.** I ran `30-score-r1` under an outer `timeout 3000` of my own, on top of `inv.sh`'s inner 3600. At about 19:29 BST (18:29 UTC) it killed `inv.sh` and its flock but not the python grandchild, which ran on holding the slot until the inner timeout killed it at 19:38:57 BST. There is no END line for `30-score-r1` in `progress.log`; this entry is its record. No other run used an outer timeout.

## Task 7 Step 4 — the proposed dislocation-attribution NFR text (2026-10-09, executor-s3f; for the decision-maker through the lead, `RL-1264` item 4)

**Proposal, stated against the measured times; no verdict is drawn from a derived figure (DP-S3-10 (b)).**

> A dislocation attribution over K change groups re-rates the portfolio 2^K times (`subset_valuation` is `rerate`; replay is not on the production path, DP-S3-3 (b)). Its cost is therefore linear in 2^K × policies, and the measured figures below are a **table-based lower bound** (see the three under-statements). On the fixture of `examples/fremtpl2/rating/` and the first 20,000 policies by `quote_id`, on the shared development box (31 GiB memory) with load1 1.6 to 2.9: K = 3 took a median 366.85 s (N = 5, range 351.89 to 400.11), K = 4 a median 734.73 s (N = 5), K = 5 1,527.04 s (N = 1), K = 6 3,024.77 s (N = 1): 2.00, 2.08 and 1.98 per extra group. K = 3 on 100,000 policies took 1,983.42 s (N = 1), 5.41x the 20,000 median for 5.00x the policies. `score_batch` alone ran at 485.76 policies/s (20,000), 480.65 (50,000), 470.74 (200,000) and 471.47 (400,000), N = 1 each, against the 1,414 policies/s planning rate (FD 9446, draft `draft/fd-9446` at `08f50d11`). A K = 4 attribution of 20,000 policies takes about 12 min; of 100,000 policies about 1.1 h (derived: 5.41 × 734.73 s = 3,975 s, using the measured 5.41 factor); K = 6 of 20,000 policies about 50 min. **The 678,013-policy book was not completed within 60 min (2 runs: a 60 min timeout and a 114 min authorised stop); derived about 78 min per single-pass invocation (about 54 min build/compile + about 24 min score at 471 pol/s) and about 20.3 GiB peak RSS (linear from 400k); not measured at 678,013.** Derived only, and labelled so: K = 3 over 678,013 policies is about 3.1 to 3.7 h; scoring alone about 24 min.

**What N = 1 cannot show.** K = 5, K = 6, the 100,000-policy linearity point and every `score_batch` figure are one run each: they show no spread. The only spread measured is K = 3 and K = 4 at N = 5 (K = 3: ±7% of the median). The 8% excess of the linearity check over 5x is inside that spread and is not evidence of super-linearity, nor of its absence. Peak RSS is measured for `score_batch` only (6.21 GiB at 200,000, 11.94 GiB at 400,000 policies, about 31 KiB per policy; N = 1); the attribute runs' memory was not measured.

**What the measured cost under-states (the dispatch record's three items).**
- (a) *Per-rating cost.* A `table` lookup per factor is cheaper than a `model_call`, which evaluates a model artifact inside the engine and today also carries `runtime.py:592`'s provisional `round(prediction)` (A-2 replaces it). The seconds per rating here are a **lower bound** for a portfolio rated through a real model; the proposal states them as table-based figures and draws no `model_call` budget from them.
- (b) *Untested paths.* The pin difference carried through a step's **model** reference (FR-1399: "through that step's table, lookup or model reference") and the model-artifact compile and hydrate path for each subset bundle are not exercised; they go to the GLM `model_call` hand-off.
- (c) *Derived-list size.* Member 0 is several derived changes in one group (RS-1201 treated it as one change). This does not change 2^K, because K counts groups; it lengthens the derive and dependence checks, which run once per run, not once per subset, so they are noise next to the re-rates.

**Both fixture departures from RS-1201's `rate()`, beside the figures** (accepted by the lead, 12:43:50 BST): (1) the cap is an expression ahead of the loading rung (`s_cap`), so it caps the premium before the age adjustment, not after the floor as RS-1201 did (the engine allows one `clamp` per ladder rung, the minimum premium); (2) the age relativity is its own `profit_loading` rung after the expense loading. The run measures the cost of attribution, not RS-1201's premium.

**Not decided here.** K = 4 does fit a 20,000-policy attribution (12 min); whether it fits a full portfolio is not measured, and the figure above (derived, 678,013 policies, K = 3, 3.1 to 3.7 h; K = 4 twice that) goes to the decision-maker before any fallback is built (Task 7 Step 4). The score_batch rate (FD 9446) is a separate finding and is not an attribution NFR.

## PRs

#1243, a draft. The branch `sl-1387-attribution-exact-shapley-largest-remainder` is pushed; the PR is not merged by the executor.
