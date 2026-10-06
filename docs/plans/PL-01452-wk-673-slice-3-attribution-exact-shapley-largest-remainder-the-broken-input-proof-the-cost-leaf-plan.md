---
id: PL-1452
family: plan
kind: leaf
title: WK-673 Slice 3 — attribution, exact Shapley, largest remainder, the broken-input proof, the cost: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-06            # original date 2026-10-05, set at the draft; minted 2026-10-06
owner: planner
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-673
slice: SL-1387
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1387, PL-1267, PL-1371, PL-1403, PL-1408, LG-1400, LG-1406, RL-1264, RL-1394, RL-1402, RL-1263, RS-1201, SL-1386, SL-1391, SL-1409]
---

# PL-1452 — WK-673 Slice 3: attribution — exact Shapley, largest remainder, the broken-input proof, the cost: leaf plan

*(Minted 2026-10-06 as PL-1452 from working id 9689, in the B1 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor is spawned from `.claude/roles/executor.md` and also
> binds `test-driven-development` (every task is red first), `python-package` (Tasks 2–6:
> where code lives, `model-schema` idioms), `python-test` (requirement markers, negative
> tests), `spec-change` (Task 1), `contract-schema` (Task 1: the hand-authored
> `dislocation-run.schema.json`, if DP-S3-1 is ruled (a)), `dev-commands` (the two-half gate,
> the benchmark load trap) and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked
> conventions before the first step.

Filed under working id **9689**, reserved by the lead in `eta.md` and named in the lead's brief
`~/gi-pricing-plan.local/handover/brief-plan-sl1387-2026-10-05.md` (written on the maintainer's (by delegation)
instruction of 2026-10-05 12:51:33 BST, item 1). Drafted from 13:16:52 BST
(`TZ=Europe/London date`) on 2026-10-05 against origin/main
`caa4e411a9c07a389cf47092a923c7761b2b92dc` (`git rev-parse origin/main` after `git fetch`,
unchanged at 13:25 BST). Every locator below was read at that tree unless another tree or a
branch head is named. Unminted records are cited by working id and kept out of `relates:`
(check 32): RL-1449 (draft PR #1126, branch `dm-9715-oq9739-subset-input-contract`),
PL-1419 (#1127), RL-1418 (#1128), PL 9713 (#1131), PL-1429 (the FD-1421 fix), RL-1451 (dm-s3). FD-1416 (#1066) was minted as FD-1416 at `99afcde2` after this plan's tree; this branch merged that commit (only `docs/findings/` and `docs/INDEX.md` changed, so every locator here reads the same).

## Goal

Build `derive_changes` and `attribute` (`03` §5.2) in `pricing_core/rating/analysis.py`: the
declared changes derived from baseline and candidate at step granularity, with the input
contract and the outputs derived too (FR-1399 as RL-1449 amends it); the analyst's groups
checked for a partition and for dependence, both refused before any subset is compiled; the
2^K subset bundles built from the baseline with each subset's changes substituted, compiled by
`compile_bundle` and rated by `score_batch` on ZEN (FR-1398 as RL-1449 amends it); exact
Shapley per policy as an integer over K!, allocated to integer minor units by largest
remainder with ties in declared order; the isolated and cumulative views and the residual line;
the labelled above-six fallback with R and a lower bound on S (FR-266); the reconciliation
checked on every run and proven on broken input (FR-1397). `BundleDelta`, `Attribution` and
`DislocationRun`'s four attribution fields are added to `model-schema`
(`model_schema/dislocation.py`). The cost is measured, not asserted (`RL-1264` feasibility
rule), and the dislocation-attribution NFR is proposed to the decision-maker from the figure.

**Architecture.** Everything is pure `pricing-core` plus `model-schema`: no route, no Job, no
persisted row (Slice 4, `SL-1388`). Subset bundles are in-memory `Bundle` objects compiled
through an overlay resolver and discarded when `attribute` returns; nothing can persist them,
because `pricing-core` has no database (import-linter `core-has-no-infrastructure`). Ratings
go through the existing `score_batch` (`score.py:1135`) via the S2 helper `_score_pass`
(`analysis.py:144`), so each subset sees only its own contract's declared inputs (`RL-1394`
DP-S1-1 (b)).

**Tech stack.** Python 3.12, Polars, Pydantic v2, `fractions`/`math.factorial` for the exact
arithmetic, the ZEN engine through `score_batch`. No new dependency.

**Spec.** [`03-rating-engine.md`](../specs/03-rating-engine.md) FR-266, FR-1397, FR-1398,
FR-1399 (`:189-192`), §4.6 (`:514-578`), §5.2 (`:1050-1058`, `:1122-1124`); RL-1449's T1–T3
(applied by Task 1); `RL-1264` (feasibility rule, `:96-110`); `RL-1394` DP-S1-5, DP-S1-6 and
"What it obliges" (`:618-640`).

## Status

`draft`. **Every decision point is decided** by the maintainer (by delegation), as the lead relayed them on
2026-10-05: DP-S3-1 (a) (the maintainer's (by delegation) entry of 2026-10-05 13:12:56 BST in `to-lead.md`, item 16); DP-S3-2 (a) with a condition, DP-S3-3 (b), DP-S3-6 (a), and
DP-S3-4 and DP-S3-5 accepted (the maintainer's (by delegation) entry of 2026-10-05 13:15:53 BST in `to-lead.md`, items 17–19); DP-S3-7 (a), DP-S3-10 (b), and DP-S3-8 and DP-S3-9 accepted
(the maintainer's (by delegation) entry of 2026-10-05 13:20:26 BST in `to-lead.md`, items 23–24). The lead's relay added one item within DP-S3-1 (a): the same hand edit widens the two
attribution ratios, with a red-first test. Each row of §"Decision points" quotes its decision.
**One thing is still open: the exact spec texts.** RL-1451 (dm-s3) adopts P1–P6
as T-texts (the maintainer's (by delegation) entry of 2026-10-05 13:25:23 BST in `to-lead.md`, items 29–30, item 29); P5 (DP-S3-7's FR-1398 sentence) was sent to the lead on 2026-10-05
for it. The plan stays `draft` until RL-1451 is minted, and moves to `active` only through a separate
activation PR.

### Activation needs, in order

1. **This plan is merged, minted, and made `active` by a dated line.**
2. **RL-1449 is merged and minted** (PR #1126). Its T1–T3 are this slice's to apply
   verbatim (Task 1), with `<date>` its commit date, and its five acceptance violations are this
   slice's tests (Acceptance 7–11). Where its minted text differs from what this plan assumes,
   the minted text governs and the dispatch record names each difference. An unminted RL-1449
   is a stop.
3. **RL-1451 (dm-s3; draft PR #1141, branch `dm-9663-wk673-s3-ruling`, head
   `6604cb858edafa8d72d0c05d8864f398bbf12b60`, base `99afcde2`)** records the
   maintainer's (by delegation) decisions on DP-S3-1 to DP-S3-10 and adopts P1–P6 as T-texts for this slice's code
   commit (the maintainer's (by delegation) entry of 2026-10-05 13:25:23 BST in `to-lead.md`, items 29–30, item 29). It is merged and minted; it mints before this plan. Where its minted
   texts differ from the Appendix, they govern and the dispatch record names each difference.
   As dm-s3 reported it: P2, P4 and P6 verbatim; P1 widened to both raisers; P5 as sent, its
   `<RL id>` written as RL-1451; **P3 carries named placeholders** (`<LEDGER_ID>`,
   `<MEASURED_TREE>`, `<SET_1>` … `<SET_6>`), which the executor fills from Task 7's ledger
   figures in the code commit and names in the ledger. The executor applies the ruling's texts,
   never the Appendix.
4. **`SL-1391` (WK-673 Slice 7) is closed.** `PL-1267`'s one-slice-at-a-time order is
   1 → 2 → 7 → 3 (`PL-1267` Sequencing; `PL-1371` §5 rule 1, `:302`, orders the G2 chain
   "WK-673 S2, S7, S3"). **This slice follows Slice 7 and never runs beside it**; the paths they
   share are listed in §"Write set". `SL-1386` (Slice 2) is closed (roadmap `:738`), so its data
   dependency is met.
5. **No WK-1250 slice that edits `compile_bundle` or the trace is in flight** (`PL-1267` Risks,
   `:336-337`). At `caa4e411`, `SL-1340` (the pin and the inlining) and `SL-1341` are `draft`
   (roadmap `:1488`, `:1506`). Task 0 Step 3 re-checks.
6. **The lane is free under `RL-1263`**, re-checked at dispatch (Task 0 Step 3), including the
   conditions of the maintainer's (by delegation) option (b) as extended to this slice against WK-675 Slice 2, and
   the one serialisation with the FD-1421 fix on the `03` owned-codes tail (the maintainer's (by delegation) entry of 2026-10-05 13:25:23 BST in `to-lead.md`, items 29–30, item 30;
   §"Contention").
7. **The maintainer's dispatch GO**, and the lead's go in a separate activation PR. Task 7's
   measurement needs the exclusive measurement slot (`delivery-process.core.json`
   `guards.parallelism.build_slices_across_works.measurement_step_runs_alone`).

Not needs: OQ-1450 (decided by RL-1449; this plan cites the ruling, it does not carry the
question); FD-1416 (this slice touches no approval route and no `to_dict` response).

**A delta against frozen `PL-1267`, stated here and recorded by the lead in the dispatch
record** (DP-S3-10 (b), the maintainer's (by delegation) entry of 2026-10-05 13:20:26 BST in `to-lead.md`, items 23–24): `PL-1267` Acceptance 5 asks for N = 5 medians of the 2^K re-rates
for K = 3–6 on freMTPL2. This slice times them on a declared 20,000-policy sample, runs one
full-portfolio K = 3 linearity run, and reports each full-portfolio figure as **derived**, with
its formula and inputs. No NFR verdict is drawn from a derived figure. The ledger carries the
measured times.

## Acceptance Standard

Each item is a named test or a measurement a fresh reviewer can re-run. Every test is shown
red before its code exists, and the ledger quotes the red (cause, not status: README
convention 2). `T` below is `packages/pricing-core/tests/test_rating_attribution.py`; `M` is
`packages/model-schema/tests/test_dislocation.py`; `R` is
`packages/model-schema/tests/test_rating_algorithm.py`.

1. **FR-1399 derivation, steps and pins.** `T::test_derive_changes_one_change_per_step_id_sorted`
   (a step added, one removed, one with two fields changed → three changes `c1..c3`, kinds
   `step_added`, `step_removed`, `step_changed`, sorted by `step_id`);
   `T::test_derive_changes_table_repoint_is_one_change` (`RL-1394` Acceptance: only one step's
   table ref `@5 → @6` → exactly one change, kind `table_repointed`, its pin carried, no `pin`
   change); `T::test_derive_changes_unaccounted_pin_is_its_own_change_after_the_steps`.
2. **Groups partition the derived list** (`LG-1400` Task 7 row, carried by name):
   `T::test_attribute_refuses_groups_that_do_not_partition_the_derived_changes` — a change left
   out, and a change in two groups, each refused `VALIDATION_FAILED` naming the change, before
   any `compile_bundle` call (a spy counts zero calls).
3. **A subset that does not compile fails the run by name** (`LG-1400` Task 7 row, by name):
   `T::test_attribute_fails_the_run_naming_a_subset_that_does_not_compile` — a resolver that
   refuses one subset's algorithm; `attribute` raises with `code == "BUNDLE_COMPILE_FAILED"` and
   the message names that subset's change ids; it is never skipped (broken by catching and
   continuing: the test goes red).
4. **Exact Shapley and largest remainder.** `T::test_shapley_is_exact_over_k_factorial` (a
   three-change fixture whose per-policy v(S) table is written out; the numerators equal the
   hand-computed ones); `T::test_largest_remainder_ties_go_in_declared_order`;
   `T::test_largest_remainder_handles_negative_parts` (floor toward −∞, remainders in [0, K!)).
5. **Reconciliation, asserted every run and proven on broken input** (FR-1397; `PL-1267`
   Acceptance 4): `T::test_reconciliation_refuses_plain_rounding_allocation` — the allocator
   monkeypatched to `round(p / K!)` on a policy whose plain rounding does not sum to its total;
   `attribute` raises with the reconciliation code (DP-S3-4) naming that `quote_id`;
   `T::test_reconciliation_refuses_a_shapley_value_perturbed_by_one_minor_unit`;
   `T::test_reconciliation_refuses_isolated_plus_residual_off_by_one`.
6. **Views and the residual line.** `T::test_isolated_and_cumulative_views_and_residual_line`:
   isolated = v({g}) − v(∅), cumulative in declared order, residual = total − Σ isolated, all
   integers, per policy and summed; `T::test_attribution_portfolio_figures_are_sums_of_policy_parts`
   (NFR-496 applied to this artifact).
7. **RL-1449 violation 1 (DP-1 (c))**: `T::test_subset_contract_carries_the_field_its_own_change_adds`
   — the worked case (`ncd` added with `in_ncd`, `rate` edited to consume it, grouped together):
   the subset holding the group declares `ncd`, and the frame `score_batch` receives carries the
   column (S2's `_Spy`); broken by building the subset from the baseline's contract.
8. **RL-1449 violation 2**: `T::test_empty_and_full_subsets_hash_equal_baseline_and_candidate` —
   the subset bundles for ∅ and for every change have `content_hash` equal to
   `compile_bundle(baseline)` and `compile_bundle(candidate)`.
9. **RL-1449 violation 3 (DP-3 (β), case 2)**: `T::test_contract_change_with_no_reader_is_one_input_field_change`
   — only `age`'s `max` 99 → 90: one change, kind `input_field`.
10. **RL-1449 violation 4 (DP-2 (i))**: `T::test_dependent_changes_ungrouped_are_refused_before_any_compile`
    — `in_ncd` and `t_ncd` ungrouped: `VALIDATION_FAILED` naming the pair (consumer, producer),
    zero `compile_bundle` calls.
11. **RL-1449 violation 5 (DP-3 case 3)**: `T::test_delta_with_two_readers_is_its_own_change_and_refused_ungrouped`
    — `vehicle_age` `int → decimal` read by `in_vage` and `in_vage_band`: three changes, the
    third `input_field`; grouping c1 without c3 refused naming (c1, c3); broken by attaching the
    delta to the first reader.
12. **The above-six fallback** (FR-266): `T::test_above_six_ungrouped_is_order_dependent_with_r_and_s_bound`
    — K = 7 ungrouped: `method == "order_dependent"`, every `shapley_minor` is `None`,
    `orders_sampled == n` (DP-S3-5), R exact as a decimal string, S a lower bound, and the
    number of distinct subset masks rated is 3K − 2 (∅, N, the K singletons, and the K − 2
    inner prefixes of each of the two orders), never 2^K (a spy counts calls); `T::test_above_six_grouped_runs_shapley_over_groups`.
13. **The undeclared column never reaches a subset** (`RL-1394` Acceptance, Slice 3's half):
    `T::test_attribute_undeclared_column_never_reaches_the_engine` — the S2 `_with_secret_step`
    fixture; every subset's premium equals the premium with the column absent.
14. **A non-quoted subset** (DP-S3-7 (a)):
    `T::test_attribute_fails_naming_a_policy_not_quoted_in_some_subset` — a candidate change
    that declines one compared policy only in combination with the baseline's other steps (a
    decline constraint whose threshold one change lowers and another raises back), so the policy
    is quoted at ∅ and N and declined in one mixed subset: `attribute` raises with
    `code == "ATTRIBUTION_RECONCILIATION_FAILED"`, naming that `quote_id` and the subset's change
    ids, and returns nothing; broken by skipping the policy, the test goes red.
15. **NFR-495 applied to this artifact**: `T::test_attribute_is_byte_identical_across_processes`
    — two `subprocess` runs of `attribute` on one fixture print the same
    `Attribution.model_dump_json()` bytes (S2's `test_dislocation_*_across_processes` pattern in
    `test_rating_dislocation.py`).
16. **Field-level deltas, and the FR-219 route typed** (DP-S3-2 (a) with its condition):
    `R::test_diff_algorithms_reports_contract_and_output_deltas` — added, removed and changed
    fields and outputs listed by name; the two booleans unchanged.
    `backend/tests/test_rating_algorithms.py::test_algorithm_diff_route_is_typed_and_keeps_its_keys`
    — red first: the route's 200 schema in `app.openapi()` is a `$ref` to `AlgorithmDiff` (red
    while it is `dict[str, Any]`), and the response body's keys are exactly the eight the model
    declares, the six that exist at `caa4e411` pinned by a literal set (`added_steps`,
    `removed_steps`, `changed_steps`, `repointed_tables`, `input_contract_changed`,
    `outputs_changed`) plus the two new ones; `uv run python scripts/generate-contracts.py
    --check` rc 0 after regeneration.
17. **The types match §4.6 field for field, and the contract admits a zero-denominator
    ratio** (DP-S3-1 (a)): the existing `M::test_dislocation_run_fields_match_the_hand_authored_contract`
    (`test_dislocation.py:161`) is extended: `_SLICE_3_FIELDS` becomes empty (every contract
    property is emitted), the compared objects gain `attribution` items, `derived_changes` items,
    `change_groups` items and `attribution_summary`, and `_NULLABLE` gains
    `("attribution", "shapley_minor")`, `("attribution", "mean_change_pct")`,
    `("attribution", "cumulative_change_pct")` and the three `attribution_summary` nullables.
    New, red first: `M::test_attribution_ratio_with_zero_denominator_validates_against_the_contract`
    — for every `_NULLABLE` entry the **contract** side admits null (`"null"` in its `type` list
    or an `anyOf` null arm); red on `:88-89` until the hand edit. `M::test_delta_kinds_equal_the_contract_enum`
    — `get_args(DeltaKind)` equals the schema's `kind` enum, red until `:101` gains the two kinds.
    `M::test_dislocation_run_attribution_is_all_or_none` (the schema's `dependentRequired`, `:9`).
18. **The replay-exactness check** (`RL-1264` Acceptance, Slice 3's; `PL-1267` Acceptance 11):
    `T::test_replay_that_differs_from_a_true_rerate_is_detected_and_recorded` — a deliberately
    wrong replay for one policy is reported by the evaluation harness as a mismatch naming the
    policy and the minor-unit difference (DP-S3-3 (b): replay is measured, never a production
    path). `T::test_attribute_records_rerate_and_no_fallback` — every run's summary has
    `subset_valuation == "rerate"` and `replay_fell_back is False`.
19. **The cost is measured** (`PL-1267` Acceptance 5 with the DP-S3-10 (b) delta the lead
    records at dispatch): the ledger records the command, the tree and the 1-minute load at each
    run (< 12); the N = 5 median `score_batch` rate on the full freMTPL2 portfolio; the N = 5
    medians of the 2^K re-rates for K = 3, 4, 5, 6 on the first 20,000 policies by `quote_id`; one
    full-portfolio K = 3 run as the linearity check; and for each K the full-portfolio cost
    labelled **DERIVED**, with its formula (2^K × 678,013 ÷ the measured rate) and inputs. No NFR
    verdict is drawn from a derived figure. The proposed dislocation-attribution NFR text, stated
    against the measured times, goes to the decision-maker through the lead before the PR is
    marked ready.
20. **The F3 carried items** (DP-S3-6 (a)): the six RS-1201 change sets repeated on ZEN, on the
    declarative fixture under `examples/fremtpl2/rating/`, with S and R per set beside RS-1201's table and
    the replay measurement per set (aligned or not; agreement with re-rates in minor units; wall
    time); the 690 and 976 per-policy maxima explained or
    shown not to recur; "no public second portfolio in the repository" recorded, or the second
    portfolio's results.
21. **The gate**: both halves green on the slice head (`dev-commands`), `generate-contracts.py
    --check` rc 0, `audit-docs.py` with only check 31 (working ids) red before the mint and clean
    after, `req-coverage.py` listing FR-266, FR-1397, FR-1398 and FR-1399 with at least one test
    each. Every rc and summary line is quoted in the ledger with the tree it was measured on.

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path, never float** (`CLAUDE.md`
  §7). Every v(S), part, residual and total is a Python `int` taken from the `payable_premium`
  rung's `value_minor` (FR-1397). The only `float` is a `mean_change_pct`-style percentage at
  the model boundary, computed as S2 does (`analysis.py:238` `_rounded_float`).
- **No pandas.** Polars only (`CLAUDE.md` §3).
- **`pricing-core` imports no FastAPI, SQLAlchemy or Redis, and raises no `PlatformError`**; a
  refusal is a `ValueError` subclass carrying `code` (as `PortfolioFrameError`, `analysis.py:60`).
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2): tests build
  `BundleDelta`, `Attribution` and `DislocationRun` from the models, never as dicts.
- **`docs/contracts/` generated files are never hand-edited**; `dislocation-run.schema.json` is
  listed hand-authored at this tree (`backend/tests/test_contracts.py:98`;
  `delivery-process.core.json` `…no_shared_files.registry_exempt_append_only.not_exempt_hand_authored`
  names `docs/contracts/schemas/*.json`). It is hand-edited by this slice, in its code commit,
  per DP-S3-1 (a); the `:98` marker stays and the ledger names the edit. `docs/contracts/openapi/generated.json`
  is regenerated by `scripts/generate-contracts.py`, never edited (DP-S3-2's condition).
- **A subset bundle has no Rating Version identity** (FR-1398): never a `RatingVersion` row,
  never in a version list. In this slice nothing can write one; Slice 4 owns
  `test_dislocation_subset_bundles_never_become_rating_versions` (`LG-1400` Task 7 table).
- **Sorted iteration everywhere a result is built** (NFR-495): no `set` iteration order reaches
  an id, an order or a hash.

## Scope

### Requirement coverage, each id individually

| Id | Where | What this slice delivers | Acceptance |
|---|---|---|---|
| FR-266 | `03` §3.9 `:189` | exact Shapley for K ≤ 6, largest remainder, isolated and cumulative views, residual line, above-six rule with R and the S bound | 4, 6, 12 |
| FR-1397 | `03:190` | integer reconciliation on every run, per policy and portfolio; broken-input proof; the failure code (DP-S3-4) | 5, 6 |
| FR-1398 | `03:191` (T3 appended) | subsets built from the baseline with the subset's changes substituted, through `compile_bundle`/`load_bundle`, cached by content hash per run; `BUNDLE_COMPILE_FAILED` naming the subset; count and hashes on the artifact; contract and outputs per DP-1 (c) | 3, 7, 8 |
| FR-1399 | `03:192` (T1, T2 appended) | derived changes incl. `input_field`/`output`; partition check; dependence check before any subset | 1, 2, 9, 10, 11 |
| NFR-495 | `03:1336` | applied to the attribution artifact | 15 |
| NFR-496 | `03:1337` | applied: portfolio figures are sums of per-policy integer parts | 6 |
| FR-219 | `03:88` | not amended; `AlgorithmDiff` gains field-level deltas if DP-S3-2 is (a) | 16 |

**Not in scope:** FR-263, FR-264 (Slice 2, closed); FR-265 and the route, Job, persisted row,
`dislocation-run` generation and `COMPARED_SLUGS` (Slice 4); FR-224, FR-257 limb (2), `06`
FR-364 (Slices 5, 6); FR-231 (Slice 7). Backend registration of the new code in
`backend/src/app/errors.py` is Slice 4's: no backend raiser exists until then, and
`backend/tests/test_errors.py:114` checks `07` §5.1 only.

### Premises read at `caa4e411`

- P1. `03` §5.2 already fixes `derive_changes(baseline, candidate, resolver) -> list[BundleDelta]`
  and `attribute(baseline, candidate, portfolio, spec, resolver) -> Attribution`, both `async`,
  in `analysis.py` (`03:1058-1061`). Neither exists: `git grep -n 'def attribute\|def derive_changes' origin/main -- packages`
  prints nothing.
- P2. `model_schema/dislocation.py` (149 lines) has `ChangeGroup` (`:27`) and `DislocationSpec`
  with `change_groups` (`:47`, max 6) and `DislocationRun` (`:116`) **without** the four attribution
  fields; `BundleDelta` and `Attribution` do not exist ("defined in model-schema by the slice that
  first returns them", `03:1122`). The module is not exported from `model_schema/__init__.py`
  (`PL-1403` DP-S2-8); this slice keeps it so.
- P3. `diff_algorithms` (`model_schema/rating.py:571-618`) reports the contract and outputs only as
  two booleans (`:617-618`); `AlgorithmDiff` (`:541-568`) is returned raw by
  `GET /rating-algorithms/{slug}@{version}/diff` (`backend/src/app/platform/rating_algorithms.py:163`,
  route `backend/src/app/api/rating_algorithms.py:58`, typed `dict[str, Any]`, so absent from the
  OpenAPI component schemas) and appears in no generated contract.
- P4. `compile_bundle(version, resolver)` (`compile.py:573`) resolves `version.algorithm_ref`
  through the resolver and refuses any status below approved (`:604-610`); `bundle_hash(graph, pins)`
  does not read the algorithm ref (`:640`).
- P5. `_score_pass` (`analysis.py:144-175`) projects the portfolio to `quote_id` plus the bundle's
  declared inputs present in the frame and stamps `purpose`, `effective_date`,
  `rating_version_ref` (`:153-158`). Attribution reuses it per subset; the subset's stamped ref is
  its synthetic algorithm ref string (DP-S3-8).
- P6. The hand-authored contract's `kind` enum is `:101`; `attribution_summary` requires
  `subset_valuation` and `replay_fell_back` (`:121-134`); `dependentRequired` ties the four fields
  (`:9`).
- P7. `LadderRung` (`model_schema/scoring.py:149-164`) records an `operation` per rung, but the
  `risk_premium` rung is one value for every factor step; replay can only separate changes that
  land on different rungs (DP-S3-3).
- P8. There is no freMTPL2 ZEN rating algorithm on main: `examples/fremtpl2/model.py:327-331`
  `_demo_algorithm` is `payable = premium_in * 2` (DP-S3-6). The freMTPL2 files are fetched by
  `examples/fremtpl2/fetch.py` (checksummed) into the git-ignored `examples/fremtpl2/data/`.
- P9. NFR-493's only recorded throughput is 5,093,947 risks/hour/worker (`CR-927` §10.4, an older
  tree, 300,000 rows); it is a planning estimate here, not a measurement (DP-S3-10).
- P10. RL-1449's find strings, counted with `grep -cF` on `docs/specs/03-rating-engine.md`:
  T1/T2's ``DP-2 (c); `RL-1394`.)* |`` → 1 hit, line 192; T3's
  ``DP-1 (a), with its conditions; `RL-1394`.)* |`` → 1 hit, line 191. §4.6's
  "Slice 3 may amend these two with a dated note if it does not adopt replay.)*" → line 516.
  The §5.1 owned-codes list ends with ``require_compilable` is the only raiser)*.`` → 1 hit
  (`:965`); **Slice 7's RL-1418 T11 appends there first**, so this slice's P1 anchor is re-read
  at dispatch after S7 merges.

### Task 0 at planning time (measured, not asserted)

Run by this plan's author on 2026-10-05 in `.claude/worktrees/pl-9689` at `caa4e411`, after
`uv sync --all-packages`:
- `uv run pytest packages/pricing-core/tests/test_rating_dislocation.py packages/model-schema/tests/test_dislocation.py -q`
  → `50 passed in 22.31s`, rc 0 (the S2 baseline this slice must keep green).
- `ls packages/pricing-core/tests/test_rating_attribution.py` → "No such file or directory".
- `grep -n -B3 '^status: active' docs/roadmap.md | grep 'id: SL'` → `1421-id: SL-1409` (only).
- The load at 13:16 BST was 2.63 (`uptime`); no measurement was taken.

### Risks

- **Subset cost.** 2^K full `score_batch` passes per run. Tests use portfolios of ≤ 20 rows.
  Task 7 runs alone (activation need 7).
- **WK-1250** changes `compile_bundle` and the trace; Acceptance 8 and 18 are the guards.
- **The `03` §5.1 owned-codes list is a single tail** shared with Slice 7 (serial by order) and
  the FD-1421 fix (serialised by the maintainer (by delegation), item 30); see §"Contention".
- **A spec find string can move** before dispatch (S7 lands first). The executor re-counts each
  find string (Task 0 Step 4); a count other than 1 is a stop, never a re-wording.

## Write set, and its contention (`RL-1263`)

**Classes**, cited by key in `docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`: **exempt (generated)** —
`registry_exempt_append_only.generated` (`docs/contracts/openapi/generated.json`,
`docs/contracts/schemas/generated/`, `docs/INDEX.md`); **`__all__` name-disjoint** —
`registry_exempt_append_only.packages/*/src/*/__init__.py#__all__`; **ALLOWED one-sided** — a
shared path where only one slice edits an existing definition and the dispatch record names the
path and the check (`other_shared_path`: `serialise_unless_dispatch_record_names_path_and_check`);
**SERIALISES** — `forbidden`: `both_change_same_existing_function_class_method_spec_section_or_policy_table`.

### By file and symbol, at `caa4e411`

| Path | Symbol or region | Change |
|---|---|---|
| `docs/specs/03-rating-engine.md` | FR-1398 row (`:191`, T3); FR-1399 row (`:192`, T1 then T2); §4.6 dated notes after `:516` (P2, P3); §5.1 owned-codes list end (P1, after S7's T11); §5.2 `analysis.py` block and the prose after `:1124` (P4) | RL-1449 T1–T3 verbatim; the ruling's texts for P1–P4 and P6 |
| `docs/contracts/schemas/dislocation-run.schema.json` | `derived_changes.items.properties.kind.enum` (`:101`); `attribution.items` `mean_change_pct`, `cumulative_change_pct` (`:88-89`) | two kinds appended; two ratios number-or-null (DP-S3-1 (a)) |
| `packages/model-schema/src/model_schema/rating.py` | `AlgorithmDiff` (`:541-568`), `diff_algorithms` (`:571-618`); new `InterfaceDelta` | two list fields and their computation (DP-S3-2 (a)); `summary` unchanged |
| `backend/src/app/platform/rating_algorithms.py` | `diff_between` (`:157-163`) | returns `AlgorithmDiff`, not `.model_dump()` (DP-S3-2's condition) |
| `backend/src/app/api/rating_algorithms.py` | `algorithm_diff` (`:53-69`) | return annotation `AlgorithmDiff`; nothing else |
| `backend/tests/test_rating_algorithms.py` | new `test_algorithm_diff_route_is_typed_and_keeps_its_keys` | Acceptance 16 |
| `docs/contracts/openapi/generated.json` | generated | regenerated (`AlgorithmDiff`, `InterfaceDelta` components) |
| `packages/model-schema/src/model_schema/dislocation.py` | `DislocationRun` (`:116`); new `BundleDelta`, `AttributionItem`, `AttributionSummary`, `Attribution`; `DeltaKind` literal | four optional attribution fields + an all-or-none validator; new types |
| `packages/model-schema/tests/test_dislocation.py` | `_SLICE_3_FIELDS`, `_NULLABLE`, `test_dislocation_run_fields_match_the_hand_authored_contract` (`:161`) edited; new tests | Acceptance 17 |
| `packages/model-schema/tests/test_rating_algorithm.py` | new test | Acceptance 16 |
| `packages/pricing-core/src/pricing_core/rating/analysis.py` | `__all__` (module-local); new `AttributionError`, `derive_changes`, `attribute`, `estimate_attribution_ratings`; private `_subset_version`, `_SubsetResolver`, `_shapley_numerators`, `_allocate`, `_reconcile`, `_check_groups`, `_check_dependence` | added; `_score_pass` reused unchanged |
| `packages/pricing-core/tests/test_rating_attribution.py` | new | Acceptance 1–15, 18 |
| `examples/fremtpl2/rating/` | new directory (DP-S3-6 (a)): `fremtpl2-rate.rating-algorithm.json` (the baseline algorithm), `fremtpl2-rate.changes.json` (RS-1201's six catalogue entries as candidate edits), `fremtpl2-freq-v1.glm.json`, `fremtpl2-freq-v2.glm.json` (declarative GLM artifacts), `fremtpl2-age-relativity-v1.rate-table.json`, `-v2`, and a `README.md` saying what it is for and that it is measurement-only | declarative JSON only, never code or a pickle; `seed.py` is not edited |
| `packages/pricing-core/tests/test_fremtpl2_rate_fixture.py` | new | loads every fixture file through the `model-schema` models and compiles the baseline and each candidate (no data needed) |
| `scripts/measure-attribution-cost.py` | new | Task 7's measurement; prints JSON lines |
| `docs/ledgers/LG-<n>-…md`; `docs/INDEX.md` | added; regenerated | registry |

**Not written:** any other `backend/` file (no new route; Slice 4); `frontend/` (the generated client is VCS-ignored); `examples/fremtpl2/seed.py`; `model_schema/__init__.py` (`AlgorithmDiff` is exported at `:278`/`:436` already; `InterfaceDelta` is reached through it and not exported);
`score.py`, `compile.py`, `runtime.py` (called, not edited); `docs/open-questions.md` and `03`
§10 (OQ-1450's rows are RL-1449's P4); `docs/roadmap.md`; `PL-1267`; `scripts/generate-contracts.py`;
`backend/tests/test_contracts.py`.

### Contention

| Path | This slice | Other slice | Shared existing definition? | Class |
|---|---|---|---|---|
| `docs/specs/03-rating-engine.md` | §3.9 FR-1398/1399; §4.6; §5.1 owned-codes list; §5.2 | **SL-1391** (S7, PL-1419 at `origin/pl-9716-wk673-s7-leaf`): FR-231 `:122`, §4.2, §5.1 diff row and the owned-codes list (RL-1418 T11, `:965`), §5.2 | **yes**: §5.1 owned-codes list, §5.2 `analysis`/rate-table blocks | **SERIALISES** — and serial by `PL-1267`'s order; S3 starts after S7 closes, re-reading its anchors |
| the same | as above | **WK-675 S2** (lane C, PL 9713, draft #1131 at `origin/pl-9713-wk675-s2-leaf`): §3.1, §3.4 after `:140`, §5.1 rows before `:897` and after `:908`, §8 `:1314` | §5.1 is one section: S2 inserts table rows; S3 appends to the owned-codes list (from `:928`), more than twenty lines below S2's nearest hunk | **ALLOWED under the maintainer's (by delegation) option (b), extended to S3** (the maintainer's (by delegation) entry of 2026-10-05 13:25:23 BST in `to-lead.md`, items 29–30, item 30), on the 13:00:09 BST conditions: (1) each dispatch record lists its side's hunks and anchors; (2) the hunks are not adjacent, and the gap is measured on the dispatch tree and recorded; (3) the second to merge merges main, reads `git merge-tree`'s exit code, and re-gates; (4) the two gates never run at once |
| the same | the owned-codes list's **single tail** (P1 appends `ATTRIBUTION_RECONCILIATION_FAILED` after the list's last entry) | **the FD-1421 fix** (WK-1178; PL-1429, draft, branch `origin/pl-9683-fd9708-rv-pins` at `f811e37d`): appends `MODEL_REFERENCE_MODE_INCONSISTENT` to the same list (its write set, the `03` row) | **yes**: one tail, both append | **SERIALISES** (the maintainer's (by delegation) entry of 2026-10-05 13:25:23 BST in `to-lead.md`, items 29–30, item 30): the second to merge merges main and re-appends after the first's entry, then re-gates |
| `packages/model-schema/src/model_schema/rating.py` | `AlgorithmDiff`, `diff_algorithms` | **the FD-1421 fix**: adds `RatingVersionCreate` after `RatingVersion` (`:138-170`), `RatingVersion` unchanged | no | **ALLOWED one-sided**, named in the dispatch record (hunks: S3 inside `:541-618`; the fix after `:170`) |
| `packages/model-schema/src/model_schema/rating.py` | `AlgorithmDiff`, `diff_algorithms` (DP-S3-2 (a) only) | SL-1391: `RateTableDiff` (`:735-747`), new `RateTableDiffCell`. WK-675 S2: `RatingAlgorithm` (`:375`) split into `RatingAlgorithmDraft` + new `RatingAlgorithmSaved` | no (different classes) | vs S7: serial anyway. vs WK-675 S2: **ALLOWED by class** (the maintainer's (by delegation) entry of 2026-10-05 13:25:23 BST in `to-lead.md`, items 29–30, item 30) — the dispatch record names the path and the check `git diff -U0 origin/main...<branch> -- packages/model-schema/src/model_schema/rating.py` showing hunks only inside `:541-618` (S3) and `:375-…` (S2) |
| `backend/src/app/api/rating_algorithms.py` | `algorithm_diff` (`:53-69`), annotation only | **WK-675 S2**: `create_rating_algorithm` (`:28-50`) edited, new `get_rating_algorithm` added **after the diff route** | no (different functions); the S2 insertion is adjacent to `algorithm_diff`'s end | **ALLOWED one-sided** — the dispatch record names the path and the check (`git diff -U0` hunks: S3 inside `:53-69`, S2 inside `:28-50` plus an insertion after `:69`); the second to merge merges main, reads `git merge-tree`'s exit code, and re-gates |
| `backend/tests/test_rating_algorithms.py` | one new test, appended | **WK-675 S2**: new tests (Acceptance 1–3) | no existing definition edited by either | **ALLOWED one-sided** (appends only), named in the dispatch record |
| `docs/contracts/openapi/generated.json` | regenerated | **SL-1409** and **WK-675 S2** regenerate it | — | exempt (generated): regenerated on the merge base, never hand-merged |
| `docs/INDEX.md` | regenerated | every PR, incl. SL-1409 | — | exempt (generated) |
| every other path in the table above | — | none: SL-1409's 35 paths (`git diff --name-only origin/main...origin/sl-1409-validation-rule-approval-through-the-workflow`) include `model_schema/__init__.py`, `approvals.py`, `validation.py`, `backend/src/app/errors.py`, `generated.json`, `01`, `06`; none is in this slice's write set | — | none |

**Result.** No path shared with `SL-1409` (in flight) except the exempt `docs/INDEX.md` and
`generated.json`. With
Slice 7 (same Work, run before this one): `03` and `model_schema/rating.py` — serial by order.
With WK-675 S2: `03` §5.1 is allowed under the maintainer's (by delegation) option (b), extended to this slice on
its four conditions; `rating.py`,
`backend/src/app/api/rating_algorithms.py` and `backend/tests/test_rating_algorithms.py` are
ALLOWED one-sided, named in the dispatch record. **One serialisation:** the `03` owned-codes
list's single tail, with the FD-1421 fix (PL-1429); the second to merge re-appends. `rating.py`
against the FD-1421 fix is ALLOWED one-sided. **FD-1416 (#1066), merged as FD-1416 at `99afcde2` after this plan's tree; this branch merged it** holds the four `to_dict` approval routes' responses: neither this slice nor Slice 7
(PL-1419 §"Result": "No approval route or `approvals.py` is touched") touches them. Open PRs
read 2026-10-05 at `caa4e411` (`gh pr list --state open`): RL-1449 (#1126), RL-1418 (#1128),
PL-1419 (#1127), PL 9713 (#1131), RL-1428 (#1133: its ruling file and `INDEX.md` only, rules on
FR-237's `POST /rating-versions`, not on `compile_bundle`), and findings PRs; none other rules
on FR-266, FR-1397–1399 or §4.6.

### Size

About two executor days plus the measurement window: six code tasks, one new test module of
~30 tests, a fixture module and a script; the measurement (Task 7) under DP-S3-10 (b) is about
1.5–2 hours exclusive.

## Decision points

Kind and blocking per `document-ids.md` §1.7. Rows of kind "decision point" are the
decision-maker's, resolved in one ruling that also adopts or amends P1–P6. **The slice may not
move `draft → active` while any blocking row is open.** Each row was sent to the lead on
2026-10-05 as it was found, for the maintainer (by delegation). **All ten are now decided** (the "Resolved by"
column, as the lead relayed the decisions). The Options and Recommendation cells keep the
plan's proposals as sent.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S3-1 | **How do RL-1449's kinds `input_field` and `output` reach `dislocation-run.schema.json`? And the two attribution ratios:** §4.6 makes a zero-denominator ratio null (`:570`), but the schema types `attribution.items.mean_change_pct` and `cumulative_change_pct` as `number` only (`:88-89`); S2 widened six ratios the same way (`RL-1402` S5). RL-1449 T4 withdrew the hand edit ("generated and never hand-edited") and says the contract gets them "by the path that governs it at S3's tree"; at that tree the file is hand-authored (`test_contracts.py:98`; core.json `not_exempt_hand_authored`), and S1 (#1094) and S2 (#1107, `f68db62a`) both hand-edited it | (a) hand-edit the authored file: the enum (`:101`) and the two ratios widened to number-or-null, as S1 and S2 did; S4 still replaces it by generation (`PL-1267` Acceptance 6). (b) pull S4's generation forward: register `DislocationRun` in `generate-contracts.py`, regenerate, move the slug to `COMPARED_SLUGS` — a scope move from `SL-1388`, i.e. a replan (the lead's call). (c) leave the contract unchanged until S4; model-schema's literal and the authored enum disagree for one slice | **(a).** It is the governing path at this tree, it matches the S1/S2 precedent, and it keeps `PL-1267`'s cut. `CLAUDE.md` §2's rule binds generated files; this one is registered hand-authored. (c) second | decision point | yes — Tasks 1, 2 | **DECIDED (a)** (the maintainer (by delegation), 2026-10-05 13:12:56 BST, item 16): the hand edit in the CODE commit, the enum and the attribution items it types; the `test_contracts.py:98` marker stays, Slice 4 generates later, and the ledger names the edit. The same entry corrects the earlier "docs/contracts is generated" reason for this file. **Within (a), per the lead's relay:** `mean_change_pct` and `cumulative_change_pct` widened to number-or-null, with a red-first test that a zero-denominator item validates against the contract (Task 2) |
| DP-S3-2 | **Where do the field-level contract and output deltas live?** RL-1449: "beside `diff_algorithms`'s two booleans" | (a) two list fields on `AlgorithmDiff`, `input_contract_deltas` and `output_deltas` (`list[InterfaceDelta]`, `InterfaceDelta = {name, change: added\|removed\|changed}`), computed by `diff_algorithms`; the FR-219 diff route's 200 body gains two keys (`test_rating_algorithms.py:215` reads only `repointed_tables`). (b) a sibling pure function `diff_interfaces(old, new)` in `model_schema/rating.py`; `AlgorithmDiff` unchanged. (c) private to `analysis.py` | **(a).** FR-1399 derives "from the structural diff (FR-219)", so one diff holds every difference the derivation reads; the booleans stay for the approval summary (RL-1449 "What it costs") | decision point | yes — Tasks 2, 3 | **DECIDED (a)** (the maintainer (by delegation), 2026-10-05 13:15:53 BST, item 17), **with a condition**: the FR-219 route's 200 is a changed JSON route, so the slice types it as `AlgorithmDiff` in the same commit (the WK-1178 template line), regenerates the contracts, and pins the existing keys with a test (Task 2, Steps 5–7) |
| DP-S3-3 | **Ladder replay** (`RL-1264` feasibility item 2: "evaluate ladder replay as the primary route where the declared changes are step-aligned") | (a) build replay for the aligned case (each group's steps feed a distinct rung, ≤ 1 group on `risk_premium`), proven equal to re-rates on the full portfolio at K ≤ 3 and a declared sample at K = 4–6, falling back on mismatch, recorded. (b) re-rates only in production; replay **evaluated** by a measurement harness over the six F3 change sets (which are aligned; replay vs re-rate where they are), results in the ledger; `subset_valuation` always `rerate`, `replay_fell_back` always `false`, and §4.6 gets the dated note `RL-1394` already permits (P3). (c) Task 7 measures first and the executor stops and routes the figure before building either | **(b).** P7: the commonest rate change (two factor edits, as §4.6's own example) is not aligned, so replay helps only changes outside `risk_premium`; P9 puts K = 4 re-rates near two worker-hours. If (a) is ruled, Task 6 gains a replay sub-task and its negative test moves onto the production path | decision point | yes — Tasks 6, 7 | **DECIDED (b)** (the maintainer (by delegation), 2026-10-05 13:15:53 BST, item 18): re-rates only; `RL-1394` T1 `:342` makes replay optional ("may"). The harness **measures** replay on the six F3 sets (aligned or not, agreement in minor units, wall time) into the ledger and the §4.6 note (P3). Runs record `rerate`. The ≈ 2 worker-hours is an estimate; the ledger gives the measured figure |
| DP-S3-4 | **The reconciliation failure code** (`RL-1394` DP-S1-6: "Slice 3 registers one in `03` §5.1") | (a) `ATTRIBUTION_RECONCILIATION_FAILED`. (b) `ATTRIBUTION_FAILED`, also covering DP-S3-7 | **(a)**, one meaning per code (`RL-1394` DP-S1-6's reason for refusing `LADDER_RECONCILIATION_FAILED`); text P1 | decision point | no | **ACCEPTED (a)** (the maintainer (by delegation), 2026-10-05 13:15:53 BST). P1 is worded to cover DP-S3-7's raiser too |
| DP-S3-5 | **The S-bound order count n, and the precision of S and R** (`RL-1394` DP-S1-5: "Slice 3 fixes it from its cost measurement, with a floor of 2") | (a) n = 2 (declared and reverse); S and R as exact `Fraction`s rounded once to 6 places, half-even (S2's share convention, `analysis.py` `_SHARE_PLACES`), null when D = 0 (§4.6's zero-denominator rule). (b) n = 2 + a fixed number of seeded random orders | **(a).** Each extra order costs up to K − 2 more prefix passes over the portfolio; Task 7 reports the cost per order, and a later amendment can raise n. Text P2 | decision point | no | **ACCEPTED (a), n = 2** (the maintainer (by delegation), 2026-10-05 13:15:53 BST) |
| DP-S3-6 | **Which ZEN algorithm the measurement and the F3 carried items run on** (P8) | (a) a measurement-only freMTPL2 algorithm reproducing RS-1201's `rate()` (a `model_call` on a declarative GLM artifact, severity, an age table, expense load, min premium, cap) and its six change sets, in a fixture module and the script. (b) as (a) with the frequency model as a precomputed relativity table (loses set member 0's model swap). (c) cost measured on the smallest faithful algorithm; the six-set rerun and the 690/976 question carried to the G2 exit-demo slice with an owner | **(a).** The carried items are this Work's (`PL-1267` Slice 3, "The F3 carried items"); member 0 is in four of the six sets; the fixture also serves Slice 4 | decision point | yes — Task 7 | **DECIDED (a)** (the maintainer (by delegation), 2026-10-05 13:15:53 BST, item 19): a measurement-only ZEN algorithm as a **declarative JSON fixture** (never code, never a pickle), named so the exit-demo slice can adopt it; no `seed.py` edit (Task 7) |
| DP-S3-7 | **A compared policy not `quoted` in some intermediate subset** (v(S) undefined; FR-1398 "never skipped") | (a) fail the run naming the first such `quote_id` and the subset's change ids, with DP-S3-4's code family. (b) attribute over the policies quoted in every subset; count the rest in a new `attribution_summary.unattributed_policies` (§4.6 + contract). (c) v(S) = 0 — invents a premium | **(a)**: rare, governance-safe, no new field; (b) is the later amendment. Text P5 | decision point | yes — Task 6 | **DECIDED (a)** (the maintainer (by delegation), 2026-10-05 13:20:26 BST, item 23): fail the run, naming the first such `quote_id` and the subset's change ids, with `ATTRIBUTION_RECONCILIATION_FAILED`; never skipped. The FR-1398 sentence (P5) is a T-text for a decision-maker to adopt; sent to the lead 2026-10-05 |
| DP-S3-8 | **How an ephemeral subset is fed to `compile_bundle`** (P4) | (a) an in-memory `RatingVersion` copied from the baseline with the subset's `pins` and `algorithm_ref = rating_algorithm:<baseline algorithm slug>-subset-<K-bit mask>@1`, compiled through `_SubsetResolver`, which serves that one ref (status: the lower maturity of the two source algorithms) and delegates every other ref. (b) bypass `compile_bundle`, building the `Bundle` directly | **(a).** (b) breaks FR-1398 ("compiled by `compile_bundle`"). `bundle_hash` ignores the ref, so Acceptance 8 holds | decision point | no | **ACCEPTED (a)** (the maintainer (by delegation), 2026-10-05 13:20:26 BST) |
| DP-S3-9 | **A version-level difference FR-1399 derives no change for** — `model_reference_mode` (`rating.py:164`); mixed subsets would fail `check_model_reference_mode` at compile | (a) `derive_changes` refuses up front with `VALIDATION_FAILED` naming the field. (b) let the subset fail `BUNDLE_COMPILE_FAILED` | **(a)**, RL-1449 DP-2 (i)'s principle (by name, before any compile). Text P6 | decision point | no | **ACCEPTED (a)** (the maintainer (by delegation), 2026-10-05 13:20:26 BST) |
| DP-S3-10 | **The measurement's size.** `PL-1267` Acceptance 5 on the full portfolio for every K is ≈ 5 × (8+16+32+64) × 678,013 ≈ 407M ratings, ≈ 80 exclusive worker-hours at P9's rate | (a) as written. (b) `score_batch` rate N = 5 on the full portfolio; 2^K re-rates N = 5 for K = 3..6 on the first 20,000 policies by `quote_id`; one full-portfolio K = 3 run as the linearity check; full-portfolio cost per K reported as **derived** and labelled. (c) as (b) with N = 3 | **(b)**: re-rates are 2^K independent passes, linear in passes × policies, and the full K = 3 run tests that on the real portfolio | decision point | yes — Task 7 | **DECIDED (b)** (the maintainer (by delegation), 2026-10-05 13:20:26 BST, item 24): full-portfolio figures are labelled DERIVED with the formula and inputs; **no NFR verdict from a derived figure**; the ledger carries the measured times. Acceptance 5's change is a dispatch-record delta against frozen `PL-1267`, the lead's at dispatch (§"Status") |

## Tasks

### Task 0: Preconditions (no code)

**Files:** the slice ledger `docs/ledgers/LG-<working id>-….md` (the executor's).

- [ ] **Step 1:** Confirm each activation need at the dispatch tree:
  `git -C <worktree> log -1 --format='%H %aI' origin/main`; RL-1449 and the DP ruling resolve
  (`grep -l '^id: RL-<n>' docs/rulings/*.md`); this plan is `active`; `SL-1391` is `closed` and
  `SL-1387` `active` in `docs/roadmap.md`.
- [ ] **Step 2:** `uv sync --all-packages`; `uv run python examples/fremtpl2/fetch.py` (checksummed;
  the data is git-ignored).
- [ ] **Step 3:** Contention, re-run and recorded:
  ```bash
  git fetch -q origin
  gh pr list --state open --json number,headRefName --jq '.[] | "\(.number) \(.headRefName)"'
  grep -n -B3 "^status: active" docs/roadmap.md | grep "id: SL"
  git diff --name-only origin/main...origin/<each active slice branch>
  ```
  Record any WK-1250 slice (`SL-1340`, `SL-1341`) that is `active`: if one edits `compile.py` or
  the trace, stop (activation need 5). Record whether WK-675 S2 is in flight and the maintainer's (by delegation)
  call on `03` §5.1.
- [ ] **Step 4:** Copy RL-1449's T1–T3 and the ruling's texts into the ledger with their minted
  ids and line ranges; re-count every find string with `grep -cF` on the dispatch tree (each must
  be 1). Every later step applies the ledger copy, never this plan's Appendix.
- [ ] **Step 5:** Baseline `uv run pytest packages/pricing-core/tests/test_rating_dislocation.py packages/model-schema/tests/test_dislocation.py packages/model-schema/tests/test_rating_algorithm.py -q`
  and the four docs checks on the untouched tree; record rc and summary lines.

### Task 1: Spec and contract — the ruled texts

**Files:** `docs/specs/03-rating-engine.md`; `docs/contracts/schemas/dislocation-run.schema.json`
(DP-S3-1 (a) only).

- [ ] **Step 1:** Apply T1 then T2 at FR-1399's row end, and T3 at FR-1398's, from the ledger copy,
  with `<date>` the commit date. Apply the ruling's P1–P6 texts at their anchors.
- [ ] **Step 2:** Under DP-S3-1 (a): append `"input_field", "output"` to the `kind` enum (`:101`)
  and widen `mean_change_pct` and `cumulative_change_pct` (`:88-89`) to `{"type": ["number", "null"]}`,
  nothing else in that file. **Make this edit at Task 2 Step 3**, after Task 2's contract tests
  are red, so the red is recorded first.
- [ ] **Step 3:** `python3 scripts/audit-docs.py` — expected: check 31 only (the ledger's working
  id), anything else is a defect of this step.
- [ ] **Step 4:** Do not commit alone: spec and the code that implements it land in one commit
  (`CLAUDE.md` §2). Stage and continue to Task 2.

### Task 2: `model-schema` — the deltas and the attribution types

**Files:** `packages/model-schema/src/model_schema/rating.py` (DP-S3-2 (a)),
`packages/model-schema/src/model_schema/dislocation.py`, their tests.

**Interfaces — Produces:**
```python
# model_schema/rating.py (DP-S3-2 (a))
class InterfaceDelta(BaseModel):              # frozen, extra="forbid"
    name: str
    change: Literal["added", "removed", "changed"]
# AlgorithmDiff gains:
    input_contract_deltas: list[InterfaceDelta] = Field(default_factory=list)
    output_deltas: list[InterfaceDelta] = Field(default_factory=list)

# model_schema/dislocation.py
DeltaKind = Literal["pin", "step_added", "step_removed", "step_changed",
                    "table_repointed", "input_field", "output"]
class BundleDelta(BaseModel):      # §4.6 derived_changes item: id, kind, description
class AttributionItem(BaseModel):  # group, shapley_minor: MoneyMinor | None, isolated_minor,
                                   # cumulative_minor, mean_change_pct: float | None,
                                   # cumulative_change_pct: float | None = None
class AttributionSummary(BaseModel):  # method, total_change_minor, residual_minor,
                                      # order_sensitivity_lower_bound: DecimalStr | None,
                                      # residual_share: DecimalStr | None, orders_sampled: int | None (ge=2),
                                      # subset_bundle_count: int (ge=0), subset_bundle_hashes: list[str],
                                      # subset_valuation: Literal["rerate", "ladder_replay"],
                                      # replay_fell_back: bool
class Attribution(BaseModel):      # derived_changes, change_groups: list[ChangeGroup],
                                   # attribution: list[AttributionItem], attribution_summary
# DislocationRun gains derived_changes, change_groups, attribution, attribution_summary,
# each `... | None = None`, with a model_validator: all four present or none (schema `:9`).
```
Field names and requiredness are copied from the schema at `:77-134`, not from this block
(README convention 1): the test of Step 1 is what holds them equal.

- [ ] **Step 1: Write the failing tests.** In `test_dislocation.py`, extend the existing
  `test_dislocation_run_fields_match_the_hand_authored_contract` (`:161`) as Acceptance 17
  states (`_SLICE_3_FIELDS` emptied; the four attribution objects compared; `_NULLABLE` extended),
  and add:
  ```python
  from typing import get_args
  from model_schema.dislocation import DeltaKind

  def _contract_admits_null(node: dict[str, Any]) -> bool:
      t = node.get("type")
      return (isinstance(t, list) and "null" in t) or any(
          b.get("type") == "null" for b in node.get("anyOf", []))

  @pytest.mark.req("FR-1397")
  def test_attribution_ratio_with_zero_denominator_validates_against_the_contract() -> None:
      contract = json.loads(_CONTRACT.read_text())["properties"]
      items = contract["attribution"]["items"]["properties"]
      for prop in ("mean_change_pct", "cumulative_change_pct", "shapley_minor"):
          assert _contract_admits_null(items[prop]), prop

  @pytest.mark.req("FR-1399")
  def test_delta_kinds_equal_the_contract_enum() -> None:
      contract = json.loads(_CONTRACT.read_text())["properties"]
      enum = contract["derived_changes"]["items"]["properties"]["kind"]["enum"]
      assert sorted(get_args(DeltaKind)) == sorted(enum)

  @pytest.mark.req("FR-1399")
  def test_dislocation_run_attribution_is_all_or_none() -> None:
      body = ...  # this module's existing valid run body (the one `test_run_accepts_a_consistent_body` uses)
      with pytest.raises(ValidationError, match="attribution"):
          DislocationRun.model_validate({**body, "derived_changes": []})
  ```
  `_CONTRACT` and `_admits_null` are the module's own (`:14`, `:155`); reuse them, do not
  re-declare. In
  `test_rating_algorithm.py`, `test_diff_algorithms_reports_contract_and_output_deltas`: a
  candidate adding field `ncd`, removing `channel`, changing `driver_age.max`, and changing an
  output's `required` → `input_contract_deltas == [("channel","removed"), ("driver_age","changed"),
  ("ncd","added")]` sorted by name; `output_deltas` likewise; `input_contract_changed` still
  `True`.
- [ ] **Step 2:** `uv run pytest packages/model-schema/tests/test_dislocation.py packages/model-schema/tests/test_rating_algorithm.py -q`
  — expected: `ImportError` on `DeltaKind` (cause) and `AttributeError` on
  `input_contract_deltas`; once the types exist, `test_attribution_ratio_with_zero_denominator_validates_against_the_contract`
  fails on `mean_change_pct` (the contract's `:88` is `number` only) and
  `test_delta_kinds_equal_the_contract_enum` on the two missing kinds. A different error is a plan
  defect; record it. The ledger quotes both reds.
- [ ] **Step 3:** Implement, including Task 1 Step 2's hand edit of the contract (DP-S3-1 (a)),
  which the ledger names. `diff_algorithms` compares fields by name: added/removed by set
  difference; `changed` where `model_dump()` differs. Sorted by name.
- [ ] **Step 4:** Re-run: pass. `uv run mypy` on `model-schema`.
- [ ] **Step 5: The FR-219 route, typed (DP-S3-2's condition), red first.** In
  `backend/tests/test_rating_algorithms.py`, append:
  ```python
  @pytest.mark.req("FR-219")
  def test_algorithm_diff_route_is_typed_and_keeps_its_keys(
      api_client, workspace_id, principal, grant
  ) -> None:
      schema = api_client.app.openapi()
      ok = schema["paths"]["/api/v1/rating-algorithms/{slug}@{version}/diff"]["get"][
          "responses"]["200"]["content"]["application/json"]["schema"]
      assert ok == {"$ref": "#/components/schemas/AlgorithmDiff"}
      ...  # create two versions exactly as the existing diff test does (`:193-224`); then
      body = diff.json()
      assert set(body) == {"added_steps", "removed_steps", "changed_steps", "repointed_tables",
                           "input_contract_changed", "outputs_changed",
                           "input_contract_deltas", "output_deltas"}
  ```
  Mirror the existing diff test's fixtures and setup rather than this sample (README
  convention 3); read how `app.openapi()` is reached in a neighbouring route-type test
  (`backend/tests/test_deployment_route_types.py`) and use that form. Run it:
  `uv run pytest backend/tests/test_rating_algorithms.py -q -k typed` — expected red on the
  `$ref` assertion (the 200 is an untyped object while the route returns `dict[str, Any]`). Any
  other failure first is a plan defect; record it.
- [ ] **Step 6:** `diff_between` returns `AlgorithmDiff` (drop `.model_dump()`, `:163`) and
  `algorithm_diff` is annotated `-> AlgorithmDiff` (`:58`); import it from `model_schema.rating`.
  This is the maintainer's (by delegation) "WK-1178 template line"; read that entry for the line itself.
- [ ] **Step 7:** `uv run python scripts/generate-contracts.py` (regenerates `generated.json`), then
  `--check` rc 0; `pnpm --dir frontend generate:api && pnpm --dir frontend type-check` (the client
  is VCS-ignored; this proves it still builds). Re-run Step 5's test: pass; and the existing
  diff test (`test_rating_algorithms.py:215`) still passes.

### Task 3: `derive_changes` — steps, pins, contract and outputs (FR-1399, T2, DP-S3-9)

**Files:** `analysis.py`; `test_rating_attribution.py` (created here).

**Interfaces — Produces:**
```python
class AttributionError(ValueError):
    def __init__(self, code: str, message: str) -> None: ...
    code: str           # "VALIDATION_FAILED" | "BUNDLE_COMPILE_FAILED" | DP-S3-4's code

async def derive_changes(baseline: RatingVersion, candidate: RatingVersion,
                         resolver: ArtifactResolver) -> list[BundleDelta]
```
Internally it also returns, per change, the structured payload Task 4 substitutes: the step
(from candidate, or `None` for a removal), the pins carried, the contract and output deltas
carried. Keep that as a private frozen dataclass `_Change(delta: BundleDelta, step_id: str | None,
new_step: RatingStep | None, pins: tuple[ArtifactRef, ...], fields: tuple[str, ...],
outputs: tuple[str, ...])` and a private `_derive(...) -> list[_Change]`; `derive_changes`
returns `[c.delta for c in _derive(...)]`.

Rules, in order (FR-1399 + T2):
1. Resolve both algorithms through the resolver; `diff_algorithms(base_alg, cand_alg)`.
2. Refuse `VALIDATION_FAILED` naming the field if `model_reference_mode` differs (DP-S3-9 (a)).
3. One change per `step_id` in `added_steps`, `removed_steps`, and the distinct `step_id`s of
   `changed_steps`; kind `table_repointed` where the only changed field is the table or lookup
   reference, else `step_changed`. Sorted by `step_id`.
4. Each pin difference (by pin list and ref) that a step change's table, lookup or model ref
   accounts for travels with it; the rest are `pin` changes sorted by reference string.
5. Each `input_contract_deltas` entry attaches to the change of the one input step whose
   `input_name` reads it (candidate side for added/changed, baseline side for removed); each
   `output_deltas` entry to the one output step change writing it by `output_name`. Zero or more
   than one such change → its own change, `input_field` / `output`, numbered after the `pin`
   changes, sorted by name.
6. Ids `c1, c2, …` in that order. `description` follows §4.6's example form
   (`"<step_id>: <field> <before> → <after>"`; for a contract field `"field <name> <change>"`).

- [ ] **Step 1: Write the failing tests** — Acceptance 1, 9, 11 (derivation half), and
  `test_derive_changes_refuses_a_model_reference_mode_difference`. Build versions from S2's
  helpers: `from test_rating_score import _algorithm_payload, _FakeResolver, _version`, editing a
  `copy.deepcopy` of the payload and registering it under `rating_algorithm:score-fixture@2` in
  `resolver._payloads`. Example:
  ```python
  @pytest.mark.req("FR-1399")
  def test_derive_changes_table_repoint_is_one_change() -> None:
      resolver = _FakeResolver()
      cand_alg = copy.deepcopy(_algorithm_payload()); cand_alg["version"] = 2
      next(s for s in cand_alg["steps"] if s["step_id"] == "s_expense")["rate_table_ref"] = (
          "rate_table:motor-expense@2")
      resolver._payloads["rating_algorithm:score-fixture@2"] = cand_alg
      resolver._payloads["rate_table:motor-expense@2"] = copy.deepcopy(
          resolver._payloads["rate_table:motor-expense@1"])
      base, cand = _version(), _candidate(alg="rating_algorithm:score-fixture@2",
                                          tables=["rate_table:motor-expense@2"])
      changes = asyncio.run(derive_changes(base, cand, resolver))
      assert [(c.id, c.kind) for c in changes] == [("c1", "table_repointed")]
  ```
  (`_candidate` is a local helper: `_version()` with `algorithm_ref` and `pins` replaced via
  `model_copy(update=…)`.)
- [ ] **Step 2:** Run; expected `ImportError: cannot import name 'derive_changes'`.
- [ ] **Step 3:** Implement; **Step 4:** pass; mypy.

### Task 4: Groups, dependence, and subset construction (FR-1398, FR-1399 T1, T3, DP-S3-8)

**Files:** `analysis.py`; `test_rating_attribution.py`.

**Interfaces — Produces (private, used by Task 6):**
```python
def _check_groups(changes: Sequence[_Change], groups: Sequence[ChangeGroup] | None
                  ) -> list[tuple[str, tuple[_Change, ...]]]   # (name, members), declared order
def _check_dependence(base_alg: RatingAlgorithm,
                      groups: Sequence[tuple[str, tuple[_Change, ...]]]) -> None
def _subset_algorithm(base_alg: RatingAlgorithm, cand_alg: RatingAlgorithm,
                      members: Iterable[_Change]) -> RatingAlgorithm
def _subset_version(baseline: RatingVersion, mask: int, k: int,
                    members: Iterable[_Change]) -> RatingVersion
class _SubsetResolver:   # serves one synthetic algorithm ref; delegates every other ref
    def __init__(self, inner: ArtifactResolver, ref: ArtifactRef,
                 payload: dict[str, Any], status: str) -> None: ...
    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact: ...
```
- `_check_groups`: no groups → one group per change named by its id; else every change in
  exactly one group, else `AttributionError("VALIDATION_FAILED", …)` naming each change left out
  or placed twice.
- `_check_dependence` (T1): for each group alone, `_subset_algorithm(base, cand, members)`; any
  `consumes` name no step in it produces names (consumer change, producer change) — the producer
  is the change whose candidate (or baseline, for a removal) step produces the name; and any
  member step that reads/writes a field or output whose delta is its own change in another group
  names (step change, that delta change). All pairs collected, sorted, one `VALIDATION_FAILED`
  saying to group them. Runs before any `compile_bundle`.
- `_subset_algorithm`: baseline steps with each member's step replaced, added or removed; the
  baseline `input_contract`/`outputs` with each member's field and output deltas applied
  (added/changed from the candidate, removed dropped) (T3). Steps sorted as the candidate orders
  them where present, else the baseline's (NFR-495).
- `_subset_version`: `baseline.model_copy(update={"algorithm_ref": ref, "pins": pins})` with the
  baseline pins plus each member's carried pins swapped; `ref = ArtifactRef(type="rating_algorithm",
  slug=f"{base_slug}-subset-{mask:0{k}b}", version=1)`.

- [ ] **Step 1: Write the failing tests** — Acceptance 2, 3, 7, 8, 10, 11 (refusal half). The
  compile-spy counts calls to `analysis.compile_bundle` via `monkeypatch.setattr`. For Acceptance
  3, `analysis.compile_bundle` is wrapped to raise the `ValueError` `compile_bundle` itself raises
  (`_raise_named`'s form; read it at `compile.py`, do not invent the message) for the one subset
  whose `algorithm_ref` slug ends `-subset-010`; assert `exc.code == "BUNDLE_COMPILE_FAILED"`, that
  `"c2"` is in the message, and that no later mask was rated (the run stopped, nothing skipped).
- [ ] **Step 2:** Run; expected `ImportError` on the private names (cause). **Step 3:** implement.
  **Step 4:** pass.

### Task 5: Shapley, allocation, views, reconciliation (FR-266, FR-1397)

**Files:** `analysis.py`; `test_rating_attribution.py`.

**Interfaces — Produces (private):**
```python
def _shapley_numerators(v: Mapping[int, int], k: int) -> list[int]
    # p_i = Σ_{S ∌ i} |S|!(k−|S|−1)! (v[S|i] − v[S]); subsets as bitmasks; Σ p_i = k!(v[N] − v[0])
def _allocate(numerators: Sequence[int], k: int) -> list[int]
    # floors p_i // k!; remainders p_i − floor·k! in [0, k!); the leftover units go to the largest
    # remainders, ties in declared (index) order
def _reconcile(quote_id: str, parts: Sequence[int], total: int,
               isolated: Sequence[int], residual: int) -> None
    # raises AttributionError(<DP-S3-4 code>, naming quote_id) unless Σ parts == total and
    # Σ isolated + residual == total
```
- [ ] **Step 1: Write the failing tests** — Acceptance 4, 5, 6. The worked example, written out
  in the test (K = 3, one policy): v = {0b000: 1000, 0b001: 1100, 0b010: 1050, 0b100: 1000,
  0b011: 1180, 0b101: 1130, 0b110: 1070, 0b111: 1200}; assert `_shapley_numerators(v, 3)` equals
  the hand-computed list (compute it in the test body from the formula with `itertools`, and also
  assert the hard-coded literal so a formula error in both is caught by `sum == 6 * 200`).
  Broken input: `monkeypatch.setattr(analysis, "_allocate", lambda p, k: [round(Fraction(x, factorial(k))) for x in p])`
  on a policy whose rounded parts sum to `total ± 1` → `attribute` raises the DP-S3-4 code naming
  the policy.
- [ ] **Step 2:** Run red; **Step 3:** implement with `math.factorial` and integers only (no
  `Fraction` in the production path; `Fraction` only in tests). **Step 4:** pass.

### Task 6: `attribute` end to end (FR-266, FR-1397, FR-1398, DP-S3-3, DP-S3-5, DP-S3-7)

**Files:** `analysis.py`; `test_rating_attribution.py`; `03` §5.2 text (P4).

**Interfaces — Produces:**
```python
async def attribute(baseline: RatingVersion, candidate: RatingVersion,
                    portfolio: pl.LazyFrame, spec: DislocationSpec,
                    resolver: ArtifactResolver) -> Attribution
def estimate_attribution_ratings(k: int, policies: int, *, grouped: bool) -> int
    # k ≤ 6 (after grouping): 2**k * policies; else (3*k − 2) * policies (n = 2, DP-S3-5)
```
Flow: `read_portfolio(portfolio, segments=spec.segments)` (refusals first) → `_derive` →
`_check_groups` → `_check_dependence` → the masks to rate (all 2^K if K ≤ 6 after grouping;
else ∅, singletons, declared and reverse prefixes) → per mask: `_subset_version`, compile through
`_SubsetResolver`, `load_bundle`, cache by `content_hash` (a mask whose hash is cached is not
re-rated), `_score_pass(bundle, portfolio, columns, spec, ref)` → per compared policy (quoted in
masks 0 and N) the v table; a compared policy not `quoted` in another mask → DP-S3-7 (a) →
`_shapley_numerators`, `_allocate`, isolated, cumulative, residual, `_reconcile` per policy →
portfolio sums → `Attribution` with `subset_bundle_count = len(cache)`, sorted
`subset_bundle_hashes`, `subset_valuation = "rerate"`, `replay_fell_back = False` (DP-S3-3 (b)).
`mean_change_pct` = part ÷ Σ compared baseline × 100 via S2's `_pct`; under `order_dependent`
from `isolated_minor` (§4.6).

- [ ] **Step 1: Write the failing tests** — Acceptance 12, 13, 14, 15, and
  `test_estimate_attribution_ratings_counts`. For 12, the baseline is the score fixture with
  seven chained expression steps `x1 … x7` inserted between `s_instalment` and
  `s_out_payable` (each `x_i = x_(i−1) * 1.00`), and the candidate changes each constant: seven
  independent `step_changed` changes, no new names, so DP-2 refuses nothing. Ungrouped, assert the
  masks rated equal 3 × 7 − 2 = 19 and `estimate_attribution_ratings(7, n, grouped=False) == 19 * n`.
- [ ] **Step 2:** Run red (`ImportError: attribute`). **Step 3:** implement. **Step 4:** pass;
  then the whole `T` file and S2's file: `uv run pytest packages/pricing-core/tests/test_rating_attribution.py packages/pricing-core/tests/test_rating_dislocation.py -q`.
- [ ] **Step 5: Commit** (spec + contract + code + tests, one commit):
  ```bash
  git add docs/specs/03-rating-engine.md docs/contracts/schemas/dislocation-run.schema.json \
    packages/model-schema packages/pricing-core
  git commit -m "feat(rating): SL-1387 — attribution: exact Shapley, largest remainder, derived changes (WK-673 Slice 3)"
  ```

### Task 7: The measurement, replay evaluation and the F3 carried items (DP-S3-3, DP-S3-6, DP-S3-10)

**Files:** `examples/fremtpl2/rating/` (new, declarative JSON); `packages/pricing-core/tests/test_fremtpl2_rate_fixture.py`;
`scripts/measure-attribution-cost.py`; `test_rating_attribution.py` (Acceptance 18); the ledger.

- [ ] **Step 1: The fixture (DP-S3-6 (a)): declarative JSON only, never code or a pickle; no
  `seed.py` edit.** Under `examples/fremtpl2/rating/`, write the baseline `RatingAlgorithm` mirroring
  RS-1201's `rate()` (read it with `git show 46ecb632:spike/f3_attribution.py`, salvage ref
  `refs/salvage/2026-09-28/spike-f3`; reproduce its structure — a `model_call` frequency, a
  severity constant, an age-band table, an expense load, a minimum-premium clamp, a cap — not its
  float arithmetic), the rate tables, and the six catalogue entries as candidate edits
  (`fremtpl2-rate.changes.json`: each entry names the steps, pins and contract fields it changes).
  The two frequency GLMs (`freq_v1`; `freq_v2` adding `VehGas`, `VehAge`) are fitted with `glum` on
  the public freMTPL2 file by `scripts/measure-attribution-cost.py fit` and written as declarative
  GLM artifacts in the payload form `test_rating_score._glm_model_payload` uses (verify the form
  there; do not invent it); the ledger records the command and the data checksum `fetch.py` pins.
  File names start `fremtpl2-rate` so the exit-demo slice can adopt them; the directory's
  `README.md` says they are measurement-only until then. Red first:
  `test_fremtpl2_rate_fixture.py::test_every_fixture_file_loads_and_compiles` (absent files →
  `FileNotFoundError`), then green.
- [ ] **Step 2:** Acceptance 18 first, red: a replay function in the harness (each rung's
  `operation` re-applied with the operand taken from baseline or candidate per S, where the
  changes are step-aligned) compared with a true re-rate; a deliberately wrong replay (one
  operand off) must be reported as a mismatch naming the policy and the minor-unit difference.
  Replay stays in the harness (DP-S3-3 (b)): `attribute` never calls it.
- [ ] **Step 3:** The script, run alone in the measurement slot, load < 12 before each run
  (`uptime`), prints one JSON line per run: `{"what", "k", "policies", "seconds", "load1",
  "tree"}`. As DP-S3-10 (b) rules: `score_batch` N = 5 on all 678,013 policies; the 2^K re-rates
  N = 5 for K = 3, 4, 5, 6 on the first 20,000 policies by `quote_id`; one full-portfolio K = 3 run.
  For each K the full-portfolio figure is printed as `{"what": "derived", "formula": "2^K * 678013 / rate", "inputs": {…}}`
  and labelled DERIVED in the ledger. The replay measurement per F3 set (aligned or not;
  agreement with re-rates in minor units; wall time). The six sets' S and R on ZEN beside
  RS-1201's table, and the per-policy maxima with the `quote_id`s and D_i behind 690 and 976 (or
  their absence).
- [ ] **Step 4:** Write the proposed dislocation-attribution NFR text against the **measured**
  times and send it to the decision-maker through the lead (`RL-1264` item 4); no verdict is drawn
  from a derived figure. If K = 4 does not fit the proposal, stop: the figure goes to the
  decision-maker before any fallback is built.

### Task 8: The gate and the ledger

- [ ] **Step 1:** The full two-half gate (`dev-commands`) on the slice head; `generate-contracts.py
  --check`; the four docs checks; `req-coverage.py`. Quote every rc and summary line with the tree.
- [ ] **Step 2:** The ledger: Task 0's records, every red quoted, Acceptance 1–21 each with its
  evidence, the measurement table, the NFR proposal as sent, and the `LG-1400` Task 7 rows
  discharged by name.

## Hand-off

The executor works in its own worktree on a branch from origin/main after `SL-1391` merges,
spawned from `.claude/roles/executor.md` with this plan and the dispatch record. The slice closes
on a clean audit and the lead's merge. Slice 4 (`SL-1388`) starts after it closes and inherits:
the backend registration of `ATTRIBUTION_RECONCILIATION_FAILED` in
`backend/src/app/errors.py`; the `examples/fremtpl2/rating/` fixture, for the exit-demo slice to adopt; `test_dislocation_subset_bundles_never_become_rating_versions`; the
route's 422 for a bad partition (`LG-1400` Task 7); the contract's generation; and the measured
cost for the Job's fan-out.

## Appendix — proposed texts P1–P6 (for the ruling to adopt, amend or reject)

The maintainer (by delegation) decided the choices each text carries (§"Decision points"); the wording is still a
decision-maker's to adopt. P5 was sent to the lead on 2026-10-05 for routing.

### P1 — `03` §5.1 owned codes, appended after the list's last entry at the dispatch tree (DP-S3-4 (a))

```markdown
`ATTRIBUTION_RECONCILIATION_FAILED`
*(added <date>, WK-673 Slice 3, FR-1397, FR-1398, `RL-1394` DP-S1-6 — a Dislocation Run's attribution does not reconcile: for some compared policy the Shapley parts do not sum to its candidate minus baseline payable premium, or its isolated figures plus the residual line do not, as integers; or a compared policy has no premium under some subset bundle (FR-1398). The run fails naming the first such `quote_id` (and, for the second, the subset's change ids) and persists nothing. Raised by `pricing_core.rating.analysis.attribute`; the platform maps it with Slice 4's route)*
```

### P2 — `03` §4.6, a dated note after the paragraph at `:516` (DP-S3-5 (a))

```markdown
*(Amended <date>, WK-673 Slice 3, `RL-1394` DP-S1-5: the order count.)* Under `order_dependent`, S's lower bound is taken over exactly 2 orders, the declared order and its reverse, so `orders_sampled` is 2. S and R are exact ratios of integers rounded once to 6 decimal places, half-even; where D is 0 each is null.
```

### P3 — `03` §4.6, the same note continued (DP-S3-3 (b))

```markdown
Ladder replay is not adopted (`RL-1394` T1 makes it optional): every v(S) is a re-rate of its subset bundle, so `subset_valuation` is `rerate` and `replay_fell_back` is `false` on every run. Slice 3 measured replay against re-rates on the six F3 change sets; its ledger records, per set, whether the changes were step-aligned, the agreement in minor units and the wall time.
```

### P4 — `03` §5.2, in the `analysis.py` block after `attribute`'s three lines, and a paragraph after `:1124`

```python
def estimate_attribution_ratings(k: int, policies: int, *,       # added <date> (WK-673 S3,
                                 grouped: bool) -> int            # RL-1264 item 3)
```

```markdown
*`attribute` (added <date>, WK-673 Slice 3).* It reads the portfolio with `read_portfolio`, derives the changes (FR-1399), checks the groups and their dependence before compiling anything, and rates each subset bundle with `score_batch` over the compared set's policies, each pass given only its subset's declared inputs. `AttributionError` is a `ValueError` with `code`: `VALIDATION_FAILED` (partition, dependence, a version-level difference), `BUNDLE_COMPILE_FAILED` (a subset, named by its change ids) or `ATTRIBUTION_RECONCILIATION_FAILED`. `estimate_attribution_ratings` returns the rating count the run will perform, 2^K × policies, or under the above-six rule (3K − 2) × policies, so a caller can show it before launch.
```

### P5 — `03` FR-1398, appended at the row's end after RL-1449's T3 (DP-S3-7 (a); sent to the lead 2026-10-05)

```markdown
*(Amended <date>, WK-673 Slice 3, <RL id>, DP-S3-7 (a).)* **A compared policy is attributed only from its own premium under every subset.** Where a policy quoted in both the baseline and the candidate pass (the compared set, §4.6) is not quoted under some other subset bundle, so that its v(S) is undefined, the run fails with `ATTRIBUTION_RECONCILIATION_FAILED`, naming the first such `quote_id` in `quote_id` order and the ids of the changes in that subset; the policy is never dropped from the attribution and its v(S) is never assumed.
```

### P6 — `03` FR-1399, appended at the row's end after T2 (DP-S3-9 (a))

```markdown
*(Amended <date>, WK-673 Slice 3.)* A difference between baseline and candidate that no derived change can carry, `model_reference_mode`, refuses the run with `VALIDATION_FAILED`, naming the field, before any subset is computed.
```

## Self-review

1. **Spec coverage.** FR-266 → Tasks 5, 6 (Acceptance 4, 6, 12); FR-1397 → Task 5 (5, 6);
   FR-1398 + T3 → Task 4 (3, 7, 8), Task 6 (14); FR-1399 + T1, T2 → Tasks 3, 4 (1, 2, 9, 10, 11);
   RL-1449's five violations → Acceptance 7–11; `LG-1400`'s two Slice 3 tests → Acceptance 2, 3,
   by name; `RL-1394`'s two Slice 3 violations → Acceptance 1 (table re-point), 13; `RL-1264`'s
   replay check → 18; the feasibility rule → Task 7 and Acceptance 19; the F3 items → 20;
   NFR-495/496 → 15, 6. The estimated rating count → `estimate_attribution_ratings`.
2. **Placeholders.** None outside the ruling-dependent branches, each named by its DP.
3. **Type consistency.** `_Change`, `_check_groups`, `_subset_version`, `_SubsetResolver`,
   `_shapley_numerators`, `_allocate`, `_reconcile`, `AttributionError`, `estimate_attribution_ratings`
   are defined once (Tasks 3–6) and used with the same signatures. Literals checked against the
   source at `caa4e411`: `_algorithm_payload`, `_FakeResolver._payloads`, `_version`
   (`test_rating_score.py:46`, `:103-115`, `:118`); `_score_pass` (`analysis.py:144`);
   `ChangeGroup` (`dislocation.py:27`); the schema property names (`:77-134`).
