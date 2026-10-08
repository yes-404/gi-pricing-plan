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

## PRs

#1243, a draft. The branch `sl-1387-attribution-exact-shapley-largest-remainder` is pushed; the PR is not merged by the executor.
