---
id: PL-9716
family: plan
kind: leaf
title: WK-673 Slice 7 — FR-231's exposure weights through the portfolio frame (F-W10-2, FD-1358): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 88d114fc44b9a77a57f29ca30bc3ee5d693085f8
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1391, PL-1267, PL-1371, PL-1403, PL-1408, RL-1361, RL-1375, RL-1263, FD-1358, SL-1377, SL-1409]
---

# PL 9716 (working id) — WK-673 Slice 7: FR-231's exposure weights through the portfolio frame, leaf plan

This plan is filed under working id 9716, which the lead reserved in `eta.md` (5 Oct 12:54:19). The lead
mints it at the merge turn. Its slice is the existing row `SL-1391` under `### WK-673` in
[`../roadmap.md`](../roadmap.md), which is `draft`. The `tree:` above is the tree of `origin/main`
`caa4e411`. Every line number in this plan was read at that commit.

**Ordered by** the deputy's instruction of 2026-10-05 12:51:33 BST, item 1, which the lead relayed in
`~/gi-pricing-plan.local/channel/to-lead.md`: *"dispatch the next READY slice under PL-1371 … If its
plan is not active, spawn the planner now"*. `PL-1371` §5 rule 1 (`:287`) puts WK-673's slices in G2's
chain. Its lane-load table (`:302`) gives lane A's week of 3–9 Oct as "WK-673 S2, S7, S3". The map plan
`PL-1267` (`:391-395`) orders the slices 1 → 2 → 7 → 3. S2 (`SL-1386`) is closed (roadmap
`:738`). So S7 is next.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (each acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (the new pricing-core module and the
> import-linter boundary), `fastapi-service` (Task 4's route), `contract-schema` and
> `contract-guard` (Task 5's `RateTableDiff` fields and the regenerated contract),
> `spec-change` (Task 1, the ruled texts only), `dev-commands` (the two-half gate) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

## Goal

`GET /api/v1/rate-tables/{slug}@{version}/diff` takes a `portfolio` query parameter that names a
`validated` portfolio Dataset Version. Each portfolio row maps to at most one cell of the current
version, through each key's binding (`RL-1361` Ruled item 2). A cell's weight is Σ `exposure_years`
over the rows that map to it. That weight feeds `exposure_weighted_mean_change_pct`. The diff also
reports `portfolio_exposure` and `matched_exposure`. Under DP-A, it also reports each changed
cell's change and weight (FD-1358). The 202 path computes the same figures. Every refusal that
`RL-1361` rules is in place before the cache is read and before any Job is created.

**Architecture.** The join is pure Polars in pricing-core (DP-B (a)):
`pricing_core/rate_tables/weights.py`. It reads `read_portfolio`'s frame (`analysis.py:78`), resolves
`factor_ref` keys with `resolve_factors` (`modelling/factors.py:106`) and `banding_ref` keys with
`apply_banding` (`modelling/bandings.py:419`), and compares keys in each key's declared type. The
platform (`backend/src/app/platform/rate_tables.py`) does five things before it calls the join:
- it checks the portfolio's permission, scope and status;
- it loads the frame;
- it loads every artifact a key pins, by its ref;
- it widens the cache key (`RL-1361` item 5).
- it passes the weights to the existing `diff_vs_previous` and `diff_vs_seed`.
The route checks first, then submits the Job or answers 200. The worker calls the same service
path.

**Tech stack.** Python 3.12, Polars, Pydantic v2 (`model-schema`), FastAPI, SQLAlchemy async,
pytest. No frontend change: WK-675 Slice 5 consumes this.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-231, FR-232, FR-228,
§4.2, §4.8 ("The portfolio frame"), §5.1 and §5.2. The rulings are `RL-1361` (DP-5, option (e),
with its exact texts T3, T6, T10 and T11) and `RL-1375` DP-1 (a2). The finding is `FD-1358`.

## Status

`draft`. **Three decision points block activation:** DP-A, DP-B and DP-C (§"Decision
points"). Each was sent to the lead on 2026-10-05 as it was found. Each needs exact text or a
decision from the decision-maker or the maintainer. The plan moves to `active` only through a
separate activation PR, after every activation need below holds.

### Activation needs, in order

1. **This plan is merged, minted, and made `active` by a dated line.**
2. **DP-A, DP-B and DP-C are decided.** Each decision carries the exact spec text that the
   decided option needs:
   - DP-A: FR-231 and `03` §4.2/§5.2 for the per-cell shape;
   - DP-B: the `03` §5.2 entry for `exposure_weights`;
   - DP-C: T11's corrected anchor.

   The text comes in a ruling (or a correcting `RL-`) that is merged on `main`. If a minted text
   differs from what this plan assumes, the minted text governs, and the dispatch record names
   each difference.
3. **`SL-1377` (FD-1357's fix) is merged.** Met: closed, roadmap `:1405`. `factor_ref` is on
   `RateTableKey` (`model_schema/rating.py:676`), and T1/T5 are applied (`03:119`, `:319`). This
   is `PL-1267`'s acceptance condition 1. The maintainer's acceptance of PL-1267 (17:53:43 BST,
   quoted in the roadmap row) says this slice "never runs concurrently with" `SL-1377`.
4. **`SL-1386` (S2) is closed.** Met: roadmap `:738`. `read_portfolio` exists.
5. **The lane is free.** No other slice that edits a path in §"Write set" with the class
   SERIALISES is in flight at dispatch. Task 0 Step 3 re-runs the contention check.
6. **The maintainer's dispatch GO**, and the lead's go in a separate activation PR.

## Acceptance Standard

Each item is checked by a command that runs from the repository root on the merge tree. "Red
first" means this: the named test was run, and it failed **for the stated cause**, before the code
that turns it green existed. If a test fails with the right status but a different cause, that is
a plan defect ([`README.md`](README.md) rule 2). The ledger records each red, with the failure line
as printed. Test modules: `P` is `packages/pricing-core/tests/test_rate_table_weights.py` (new);
`B` is `backend/tests/test_rate_table_diff_portfolio.py` (new); `C` is
`backend/tests/test_diff_cache.py`.

**The join (pure, `P`; `uv run pytest packages/pricing-core/tests/test_rate_table_weights.py -q`)**

1. `test_an_unbound_key_weights_by_its_same_named_column`. The weight of a two-key table equals a
   hand-computed Σ `exposure_years` per cell. Red: `ModuleNotFoundError` for
   `pricing_core.rate_tables.weights`.
2. `test_a_factor_ref_key_weights_through_each_factor_type`, parametrised once for each type that
   `resolve_factors` implements:
   - identity, whose slug differs from its column;
   - banding;
   - grouping;
   - interaction.

   Each weight equals a hand-computed figure. A same-named join on the identity case refuses
   "column absent", and the test fails.
3. `test_a_banding_ref_key_weights_through_apply_banding`. The weight equals a hand-computed
   figure. With the raw column used instead of the banded one, nothing matches, and the test
   fails.
4. `test_keys_compare_in_their_declared_type`. Cells stored as `"03"` (an `int` key) and `"True"`
   (a `bool` key) receive the weight of portfolio values `3` and `true`. With a raw-string join,
   nothing matches, and the test fails.
5. `test_a_zero_exposure_cell_carries_no_weight`. Every weighted changed cell sums to 0. The
   result is a `None` mean, no exception, and coverage figures that are not zero. Red at
   `caa4e411`: `decimal.InvalidOperation` (`DivisionUndefined`) from `operations.py`'s
   `total_weight` division (Task 0 Step 2).
6. `test_refusals_name_the_key_or_the_column`, parametrised over these cases:
   - a same-named column is absent;
   - a Factor's source column is absent;
   - a banded column is not numeric (checked before `apply_banding` casts);
   - a Banding with `error` policy meets an out-of-range value;
   - a portfolio matches no cell.

   Each raises `WeightJoinError` (`code = "VALIDATION_FAILED"`) whose message names the key, the
   column or the ref. With the zero-match refusal removed, a `None` mean comes back, and the test
   fails.
7. `test_coverage_is_the_fixtures_total_and_matched_exposure`, and
   `test_a_match_with_no_changed_cell_is_a_none_mean_not_a_refusal`.

**The route and the service (`B`, `C`; `uv run pytest backend/tests/test_rate_table_diff_portfolio.py backend/tests/test_diff_cache.py -q`)**

8. `test_seeded_banding_and_grouping_tables_are_weighted`:
   - The fixture GLM has two categorical Factors, one banding and one grouping.
   - It is seeded once per Factor, through the platform `seed_from_model`.
   - Each table's weighted diff equals a hand-computed figure.
   - With `factor_ref` stripped from the definition, the request is refused with zero match, and
     the test fails.
9. `test_an_unweighted_diff_says_so`. With no `portfolio`, the 200 body carries
   `portfolio_exposure` and `matched_exposure` as `null`. Red: `KeyError` on the absent field.
10. `test_portfolio_needs_dataset_read_and_hides_existence`:
    - A rating-only caller succeeds without `portfolio`.
    - With `portfolio`, that caller gets 403 for an existing id and for a nonexistent id, with
      the same body.
    - With `dataset:read` made route-wide, the first case fails.
    - With the handler check removed, the weighted case is served.
11. `test_a_foreign_portfolio_is_404_on_a_warm_cache`. Another workspace's portfolio gives the same
    404 body as a nonexistent id, after a cache entry for that id has been placed first. With the
    checks moved after the cache read, the test fails.
12. `test_a_portfolio_must_be_validated`. A `draft` portfolio and an `archived` one each give
    `DATASET_NOT_VALIDATED` 409, whose detail names the diff. A `validated` one is accepted.
13. `test_a_dangling_ref_is_404_naming_key_and_ref`, for `factor_ref` and for `banding_ref`. A
    ref that exists only in another workspace gives the same 404.
14. `test_null_and_negative_exposure_are_422_naming_the_column`. The null case names the count.
    These refusals come from `read_portfolio` (premise P3). The test pins that they reach the
    route as 422 and not as 500.
15. `test_the_frame_passes_through_undeclared_columns`. A Factor whose source column is outside
    §4.8's declared set resolves. With the reader keeping only the declared columns, the request
    is refused "source column absent", and the test fails.
16. The cache key tests (`C`). Each is red first: with that component removed from the key, the
    second request is served the first one's figure.
    - `test_two_portfolios_are_two_entries`;
    - `test_two_workspaces_are_two_entries_with_a_portfolio`;
    - `test_a_definition_change_is_a_new_entry`, parametrised over a key's role, a key's type,
      `banding_ref` and `factor_ref`, each with and without a portfolio.
17. The 202 path, on a parquet version:
    - `test_a_refused_portfolio_creates_no_job`: no `JobRow` is written, for a 403, a 404, a 409
      and a rating-only caller;
    - `test_the_job_result_equals_the_200_figure`: the result equals the 200 path's weighted
      figure on the rows-stored twin;
    - `test_a_portfolio_archived_before_the_worker_runs_fails_the_job`: the code is
      `DATASET_NOT_VALIDATED`. With the worker's re-check removed, the Job succeeds, and the test
      fails;
    - `test_a_dangling_ref_fails_the_job_with_not_found`.

**FD-1358 (only under DP-A (b); `B` and `P`)**

18. `test_a_two_cell_change_returns_each_cells_change_and_weight`. The response lists each changed
    cell's key tuple, baseline and current value, absolute change, relative change and weight.
    The weight is `null` without a portfolio. The weights sum to the cells' share of
    `matched_exposure`. Red at `caa4e411`: `RateTableDiff` has three fields only (Task 0 Step 2).

**Spec, contract, gate, record**

19. **The spec texts are byte for byte.**
    - Each of T3, T6, T10 and the DP-C-corrected T11, with `<Slice 7 date>` set to the commit
      date, is applied verbatim, and so is DP-A's and DP-B's text. Every find string occurs
      exactly once before it is applied.
    - Checked with `git diff origin/main...HEAD -- docs/specs/03-rating-engine.md` against the
      ruling's text blocks. Any wording that differs is a stop (`RL-1361` §"The exact texts").
    - `python3 scripts/audit-docs.py` exits 0.
20. **The contract.** `uv run python scripts/generate-contracts.py --check` exits 0 on the merge
    tree. `docs/contracts/openapi/generated.json` shows:
    - the `portfolio` query parameter on the diff route;
    - the new `RateTableDiff` properties (`grep -c '"matched_exposure"'
      docs/contracts/openapi/generated.json` prints at least 1).
21. **Requirement markers.** `uv run python scripts/req-coverage.py` lists FR-231 and FR-232 with
    the new tests. Each test in 1–18 carries `@pytest.mark.req("FR-231")`, and the 202 tests also
    carry `req("FR-232")`.
22. **The gate.** Both halves pass, through the gate-runner (CLAUDE.md §11), with each rc and the
    tree recorded in the ledger.
23. **The write set.** `git diff --stat origin/main...HEAD` lists only paths in §"Write set". Any
    other path is reported to the lead before merge.

## Global Constraints

- **Money is untouched.** Exposure and percentages are `Decimal`, never `float`
  (`CLAUDE.md` §7; `RateTableDiff`'s docstring: "never JSON floats (R2)"). A float
  `exposure_years` column is read by `read_portfolio`'s own rule (`03:578`).
- **No pandas** (`CLAUDE.md` §3). The join is Polars.
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2; ADR-703). `weights.py` takes the
  frame and the artifacts as arguments and imports nothing from `app`. `PlatformError` is never
  raised from pricing-core: the platform maps `WeightJoinError` and `FactorResolutionError` to
  `PlatformError("VALIDATION_FAILED", …, 422, …)`.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2). The two
  coverage fields, and under DP-A (b) the per-cell row, are `model-schema` types in
  `model_schema/rating.py`. The contract is regenerated, never hand-edited.
- **No spec text is written by the executor.** Every `docs/specs/` byte comes from a ruling's text
  block (`RL-1361` §"The exact texts", last paragraph). A find string not found exactly once is a
  stop, reported to the lead.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13). Acceptance 2–6, 8, 10,
  11 and 15–17 each name the break that turns them red.
- **Shared files** (`RL-1263`; `docs/process/delivery-process.core.json`
  `guards.parallelism.build_slices_across_works.no_shared_files`): §"Write set" classifies each
  path.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-231 | The weight limb: Σ exposure per cell from a named portfolio, the weighted mean, the coverage figures, and the refusals (T3, T10); under DP-A (b), the per-cell change and weight | `req("FR-231")` on Acceptance 1–18 |
| `03` | FR-232 | The 202 path carries `portfolio`, and the Job computes the same figures (T10; `RL-1361` item 8) | `req("FR-232")` on Acceptance 17 |
| `03` | FR-228 | Read only. The binding (`factor_ref`, `banding_ref`, or by name) decides the join. T1 is already applied (`03:119`) | none new |
| `07` | FR-451 | `RateTableDiff` and the route parameter are regenerated into `docs/contracts/` | Acceptance 20 |
| `03` | NFR-495, NFR-496 | **Not applied.** Both are about premiums and the ladder. The diff produces no premium. The WK-673 row applies them to "this Work's artifacts", which are the Dislocation Run and the Attribution | — |

**Findings and register rows.**
- `FD-1358` (MEDIUM, owner WK-673). This slice closes it under DP-A's decided option.
- The register row `FR-231 (F-W10-2)` (`docs/findings/register.md`) is discharged on merge by the
  auditor (`PL-1267` Slice 7).
- FD 9752 (working id; minted as FD 1416 in open PR #1066) holds the four `to_dict` approval routes' responses. **This slice
  touches no approval route** and does not touch `backend/src/app/api/approvals.py`.

**Not in scope.**
- `RL-1361` item 10: (b) is not planned. A key derived by an expression is refused by name.
- The WK-675 Slice 5 view.
- Any migration: existing versions stay unbound (FR-4; `RL-1361` item 9).

### Premises read at `caa4e411`

- **P1.** `RateTableKey.factor_ref` and its validator exist (`model_schema/rating.py:676-686`).
  Seeding sets the field (`pricing_core/rate_tables/operations.py:230`).
- **P2.** `RateTableDiff` has three fields (`model_schema/rating.py:735-747`). `_compute_diff`
  takes `weights: Weights | None`, keyed by `KeyTuple` (`operations.py:85`, `:88`, `:386-435`).
- **P3.** `read_portfolio` (`rating/analysis.py:78-125`):
  - it keeps every column;
  - it requires `quote_id` and `exposure_years`;
  - it refuses null, NaN, infinite and negative exposure, naming the column and the count, with
    `PortfolioFrameError` (`code = "VALIDATION_FAILED"`);
  - it returns `exposure_years` as `pl.Decimal`.

  So `RL-1361` §E's pass-through premise and its null and negative refusals are already delivered
  by the reader. This slice maps them to 422.
- **P4.** The diff service passes no weights (`platform/rate_tables.py:291-349`, docstring
  `:308`). The route has no `portfolio` parameter (`api/rate_tables.py:278-321`). The worker passes
  none (`worker/rate_table_handlers.py:24-54`). The cache key already carries the portfolio id
  (`platform/diff_cache.py:77-88`), but not the workspace or the definition.
- **P5.** **No loader resolves a `factor:` or `banding:` ref to its artifact.** `load_factors`
  (`platform/modelling.py:284`) and `load_bandings`/`load_groupings`
  (`platform/transformations.py:390`, `:414`) take ids. `FactorRow` and `BandingRow` carry `slug`
  and `version` (`db/models.py:1315`, `:1341`). This slice adds load-by-ref, with `_refuse_missing`'s
  404 form (`transformations.py:432`).
- **P6.** A Dataset Version's frame is read as `version.tables[0]`, which is the convention of
  `worker/model_handlers.py:89-98` and `platform/transformations.py:457`. See DP-D.
- **P7.** `fittable_or_refuse` and `load_version` (`platform/datasets.py:743`, `:763`) give the
  status 409 and the scope 404 that `RL-1361` item 7 names. `load_version` takes a row lock, which
  `RL-1361` item 7 says "a read may drop". Task 3 uses a lock-free twin.
- **P8.** `rbac.require_permission` (`api/authz.py:63`) is the in-handler check that `requires()`
  wraps. It is called with `Permission.DATASET_READ`, without loading the version.
- **P9.** `RL-1375` DP-1 (a2) is merged with `SL-1377`. `_resolve_baseline`'s seed branch is (a2).
  This slice does not edit `_resolve_baseline`. Its `against=seed` tests after a re-seed are
  written to (a2).

### Task 0 at planning time (measured, not asserted)

Run by this plan's author on 2026-10-05 in the worktree at `caa4e411`
(`git rev-parse HEAD` printed `caa4e411a9c07a389cf47092a923c7761b2b92dc`), after
`uv sync --all-packages`.

**Step 1: the slice is next and ready.**
- `SL-1391` is `draft` (roadmap `:812-828`). `SL-1386` is `closed` (`:738`). `SL-1377` is
  `closed` (`:1405`).
- The only `SL-` row whose `status:` is `active` is `SL-1409` (predicate:
  `grep -n -B3 "^status: active" docs/roadmap.md | grep "id: SL"`, which printed one line,
  `1421-id: SL-1409`).

**Step 2: the reds that exist today.** The script was
`$CLAUDE_JOB_DIR/tmp/t0.py`, run with `uv run python`: a one-key table, cell `A` changed from
`1.0` to `1.1`, and `B` unchanged. Output, verbatim:

```text
fields: ['changed_cells', 'max_abs_change_pct', 'exposure_weighted_mean_change_pct']
ZERO-WEIGHT: InvalidOperation [<class 'decimal.DivisionUndefined'>]
changed_cells=1 max_abs_change_pct=Decimal('10.0') exposure_weighted_mean_change_pct=Decimal('10.0')
```

So Acceptance 5's red and Acceptance 18's red reproduce. `RL-1361` new item 6's divide-by-zero
holds at `caa4e411`.

**Step 3: the spec find strings.** `grep -cF` over `docs/specs/03-rating-engine.md`:

| Text | Find string (start) | Hits | Line |
|---|---|---|---|
| T3 | `so an actuary sees which edits matter. \|` | 1 | 122 |
| T6 (a) | `"exposure_weighted_mean_change_pct": 0.8},` | 1 | 312 |
| T6 (b) | `"diff_vs_seed": {"changed_cells": 7, …` | 1 | 313 |
| T6 insert anchor | the `factor_ref added` blockquote (T5, applied) | 1 | 319 |
| T10 | the whole diff row | 1 | 904 |
| **T11** | ``orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*.`` | **0** | — |

T11's anchor moved: `dfddfad8` (#1104, `SL-1256`, 2026-10-04) appended `RATING_VERSION_IMMUTABLE`
after it, so line 963 now ends `)*,`. The paragraph's final `)*.` is on line 965. This is **DP-C**.

**Step 4: contention.** See §"Write set". The executor re-runs this step at dispatch:

```bash
git fetch -q origin
gh pr list --state open --json number,headRefName --jq '.[] | "\(.number) \(.headRefName)"'
grep -n -B3 "^status: active" docs/roadmap.md | grep "id: SL"
git diff --name-only origin/main...origin/sl-1409-validation-rule-approval-through-the-workflow
```

### Write set, and its contention (`RL-1263`)

"Edited" means that an existing definition changes. "Added" means a new definition in an existing
file, or a new file. Rows marked *(DP-A b)* exist only under that option.

**Classes**, cited by key in `docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`:
- **exempt (generated)**: `registry_exempt_append_only.generated` lists
  `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/` and `docs/INDEX.md`.
  These are regenerated on the merge base and never hand-merged.
- **`__all__` name-disjoint**: `registry_exempt_append_only.packages/*/src/*/__init__.py#__all__`.
- **SERIALISES**: `other_shared_path` (`serialise_unless_dispatch_record_names_path_and_check`).
- **none**: no other slice touches the path.

`SL-1409`'s change set was read at `origin/sl-1409-validation-rule-approval-through-the-workflow`
on 2026-10-05, with `git diff --name-only origin/main...origin/sl-1409-…`. It has 35 paths.

| Path | Change | Other slice touching it | Class |
|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rate_tables/weights.py` | added: `exposure_weights`, `PortfolioWeights`, `WeightJoinError` (DP-B (a)). The directory has no `__init__.py` at `caa4e411` (`ls` prints `operations.py` only), so no package export changes | none | none |
| `packages/pricing-core/src/pricing_core/rate_tables/operations.py` | edited: `_compute_diff` (`:386-435`), which ignores a zero weight; *(DP-A b)* builds the per-cell rows | none in flight. WK-675 S4/S5 (not dispatched) read it | none |
| `packages/model-schema/src/model_schema/rating.py` | edited: `RateTableDiff` (`:735-747`) gains `portfolio_exposure` and `matched_exposure` (`Decimal \| None`); *(DP-A b)* added: `RateTableDiffCell`, and `RateTableDiff.cells` | none. `SL-1409` edits `model_schema/approvals.py` and `validation.py` only | none |
| `packages/model-schema/src/model_schema/__init__.py` | *(DP-A b)* `RateTableDiffCell` appended, only if `rating`'s names are exported there (at `caa4e411`, `RateTableDiff` is not: `grep -n RateTableDiff` prints nothing) | **`SL-1409`** edits this file | `__all__` name-disjoint (if touched) |
| `backend/src/app/platform/rate_tables.py` | edited: `diff` (`:291-349`) and `diff_needs_job` (`:262-288`), each with a `portfolio_dataset_version_id` and the checks; added: `check_portfolio`, `_portfolio_frame`, `_key_artifacts` | none in flight (`SL-1377` closed) | none |
| `backend/src/app/platform/diff_cache.py` | edited: `DiffCache.key` (`:77-88`) gains `definition_hash` and `workspace_id`; added: `definition_hash` | none | none |
| `backend/src/app/platform/modelling.py` | added: `load_factor_by_ref` | none. `SL-1409` does not touch it | none |
| `backend/src/app/platform/transformations.py` | added: `load_banding_by_ref` | none | none |
| `backend/src/app/platform/datasets.py` | added: `read_version` (the lock-free twin of `load_version`, P7) | none. `SL-1409` does not touch it | none |
| `backend/src/app/api/rate_tables.py` | edited: `rate_table_diff` (`:278-321`), which gains the `portfolio` query and the checks before the cache read and the Job; its `responses` gain 409 | none | none |
| `backend/src/app/worker/rate_table_handlers.py` | edited: `_rate_table_diff` (`:24-54`), which passes `portfolio` | none | none |
| `docs/specs/03-rating-engine.md` | edited: FR-231 row (T3), §4.2 (T6), §5.1 diff row (T10), owned codes (T11 as DP-C corrects it), and DP-A's and DP-B's texts | none in flight. `SL-1409` edits `01` and `06` only | none |
| `docs/contracts/openapi/generated.json` | regenerated | **`SL-1409`** regenerates it | exempt (generated) |
| `docs/contracts/schemas/generated/` | unchanged unless `RateTableDiff` is registered as a slug (it is not at `caa4e411`) | — | exempt (generated) |
| `packages/pricing-core/tests/test_rate_table_weights.py` | added | none | none |
| `backend/tests/test_rate_table_diff_portfolio.py` | added | none | none |
| `backend/tests/test_diff_cache.py` | edited: the tests that call `DiffCache.key` move to its new signature; added: Acceptance 16 | none | none |
| `backend/tests/test_api_rate_tables.py`, `backend/tests/test_worker_rate_tables.py` | edited only where a call to `service.diff` or `DiffCache.key` changes signature | none | none |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | exempt (generated) for `INDEX.md` |

**Result.**
- No path SERIALISES against `SL-1409`.
- Two paths are shared, and both are exempt: `generated.json` (always), and
  `model_schema/__init__.py` (only under DP-A (b), and only if touched).
- `SL-1409` adds no name that this slice adds. The dispatch record names the `__all__` names if
  `__init__.py` is touched (the key's own condition), and the second to merge re-gates.
- `backend/src/app/errors.py` (a `SL-1409` path) is **not** touched: `DATASET_NOT_VALIDATED`,
  `VALIDATION_FAILED` and `NOT_FOUND` are already registered.
- No approval route or `approvals.py` is touched, so the FD 9752 hold is not reached.

**Open PRs read on 2026-10-05** (`gh pr list --state open`, at `origin/main` `caa4e411`). None
rules on FR-231, the diff route, or the rate-table weights:
- #1113 (PL 9728, docs: `docs/roadmap.md`, another row);
- #1119 (RL 9718), #1067 (RL 9753, WK-675 S2/S4 routes), #1055 (WK-675 DP-5/6), #1061 (FR-223);
- #1066 (FD 9752, working id);
- #972 (FD 9888, the scoring path's table miss, not the diff);
- the remaining findings and dependabot PRs.

PL 9713 (WK-675 S2's leaf, being planned, not pushed) and RL 9715 (S3's unblocker) were in
`eta.md` and not on `origin`.

### Size

About one executor day. There are five tasks after the preconditions, and a sixth under DP-A
(b). There are two new test modules, with real dataset versions, a seeded GLM and a parquet Job.
One full two-half gate run is needed. There is no NFR measurement, so the slice need not run
exclusive.

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-A** | **FD-1358.** FR-231 promises "the exposure weight behind each cell". `RateTableDiff` is aggregate only (P2), and T6 adds two more aggregates. WK-675 S5 needs per-cell data: `PL-1286` `:307` gives it "diff shading" and "the exposure-weight column", and `:290-292` say it "ships with the weights". FD-1358's Disposition gives two closes and "the lead's or maintainer's" choice | (a) amend FR-231: aggregates only, and a per-cell view is a later requirement. (b) `RateTableDiff.cells`: one `RateTableDiffCell` per **changed** cell (key tuple, baseline, current, absolute and relative change, weight or `null`); the Job artifact carries the same list. (c) a separate paged `…/diff/cells` resource | **(b), changed cells only.** FR-231's own purpose is "so an actuary sees which edits matter". The list is bounded by the edit, not by the table. The parquet case is already a Job artifact. Sub-option, if a hard bound is wanted: cap the inline list at N with `cells_truncated`, and keep the full list in the Job artifact (N would be a further decision). (a) leaves WK-675 S5 without its data. (c) adds a route, pagination and its own 202 rule | decision-maker (text); lead/maintainer (choice) | Tasks 1, 5, 6 |
| **DP-B** | Where the join lives, and its `03` §5.2 text. RL-1361's texts cover FR-231, §4.2 and §5.1, not §5.2, and every public pricing-core function is listed in §5.2 (`03:1023`; `read_portfolio` `:1052`) | (a) a pure `exposure_weights` in `pricing_core/rate_tables/weights.py`, with a dated §5.2 entry; (b) a private helper in the platform, with no §5.2 change | **(a).** The join is pure Polars over two pricing-core functions (ADR-703's split). Every `RL-1361` acceptance case then becomes a DB-free unit test. The planner can draft the §5.2 wording for the decision-maker to adopt | decision-maker (text) | Tasks 1, 2 |
| **DP-C** | T11's find string has 0 hits (Task 0 Step 3). `RL-1361` makes that "a stop … the executor does not re-word it" | (a) a correcting `RL-` re-anchors T11 on `` `app.platform.rating_versions.require_compilable` is the only raiser)*. ``, with the payload unchanged; (b) the dispatch record names the delta on the maintainer's line | **(a).** The payload stays byte-identical, the authorship stays with the decision-maker, and a frozen `RL-` is never edited. One `RL-` can carry DP-A, DP-B and DP-C | decision-maker | Task 1 |
| DP-D *(not blocking)* | A portfolio Dataset Version with more than one table (P6) | (a) `tables[0]`, as fitting and banding proposal do; (b) refuse more than one table with 422 (a refusal T10 does not list, so it needs text) | **(a)**, recorded in the ledger. If it proves wrong, it is one function (`_portfolio_frame`) | lead | none |
| DP-E *(not blocking)* | A rows-stored table with a large portfolio stays on the synchronous 200 path, because `RL-1361` item 8 lets storage, not portfolio size, choose 202 | (a) as ruled; (b) a portfolio row threshold also routes to 202 (a spec change) | **(a)**. The ledger records the wall-clock of one weighted 200 diff on the freMTPL2 seed (about 678k rows) as information, not as an NFR verdict. A slow figure is a finding for the lead | lead | none |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm each activation need. Quote the minted ruling ids for DP-A, DP-B and
  DP-C, and their text blocks, into the ledger.
- [ ] **Step 2:** Re-run Task 0 Step 3's `grep -cF` over every find string, using the texts as
  minted. Any count that is not 1 is a stop.
- [ ] **Step 3:** Re-run the contention commands (§"Task 0 at planning time", Step 4). Record the
  output and each class in the ledger. A new SERIALISES path is a stop, reported to the lead.
- [ ] **Step 4:** `uv sync --all-packages`, then `uv run pytest packages/pricing-core/tests/test_rate_table_operations.py backend/tests/test_diff_cache.py -q`
  green on the base. Record the counts.

### Task 1: The spec texts, verbatim

**Files:** `docs/specs/03-rating-engine.md`.

- [ ] **Step 1:** Apply T3 (`03:122`), T6 (`:312-313`, and the insert after `:322`), T10
  (`:904`), and T11 as DP-C corrects it, byte for byte. Set `<Slice 7 date>` to today's date
  (`date +%F`).
- [ ] **Step 2:** Apply DP-A's text and DP-B's §5.2 text, byte for byte.
- [ ] **Step 3:** `python3 scripts/audit-docs.py`. It exits 0, or with check 31 only while a
  working id stands.
- [ ] **Step 4:** Commit: `docs(specs): 03 FR-231 weights, the diff route's portfolio (RL-1361 T3, T6, T10, T11)`.

### Task 2: The pure join, red first (Acceptance 1–7)

**Files:**
- Create: `packages/pricing-core/src/pricing_core/rate_tables/weights.py`
- Modify: `packages/pricing-core/src/pricing_core/rate_tables/operations.py` (`_compute_diff`)
- Test: `packages/pricing-core/tests/test_rate_table_weights.py`

**Interfaces.**

Produces:

```python
class WeightJoinError(ValueError):
    """A portfolio that cannot weight this table; the platform maps it to VALIDATION_FAILED."""
    code = "VALIDATION_FAILED"

@dataclass(frozen=True, slots=True)
class PortfolioWeights:
    weights: dict[KeyTuple, Decimal]      # Σ exposure per stored key tuple; zero sums omitted
    portfolio_exposure: Decimal
    matched_exposure: Decimal

def exposure_weights(
    portfolio: pl.LazyFrame,              # read_portfolio's output (P3)
    keys: Sequence[RateTableKey],         # the CURRENT version's definition (RL-1361 item 2)
    cells: Cells,                         # the current version's cells
    *,
    factors: Mapping[str, Sequence[Factor]],    # factor_ref string -> [Factor, *operands]
    bandings: Mapping[UUID, Banding],           # by id: every Banding a key or Factor pins
    groupings: Mapping[UUID, Grouping],
) -> PortfolioWeights: ...
```

DP-B's minted text governs the name and the signature. If it differs, follow the text and record
the difference.

- [ ] **Step 1: Write the failing tests** (Acceptance 1–7), each with `@pytest.mark.req("FR-231")`.
  Hand-computed figures are literal `Decimal`s in the test. They are never computed by the code
  under test. A sketch for Acceptance 4:

```python
@pytest.mark.req("FR-231")
def test_keys_compare_in_their_declared_type() -> None:
    keys = [RateTableKey(name="ncd", type="int"), RateTableKey(name="garaged", type="bool")]
    cells = [{"ncd": "03", "garaged": "True", "relativity": "0.9"}]
    frame = pl.LazyFrame({"quote_id": ["q1", "q2"], "ncd": [3, 3], "garaged": [True, True],
                          "exposure_years": [Decimal("0.5"), Decimal("0.25")]})
    result = exposure_weights(read_portfolio(frame), keys, cells,
                              factors={}, bandings={}, groupings={})
    assert result.weights == {("03", "True"): Decimal("0.75")}
    assert result.matched_exposure == result.portfolio_exposure == Decimal("0.75")
```

  Check the `RateTableKeyType` literals (`int`, `bool`, `date`, `string`) against
  `model_schema/rating.py` before use ([`README.md`](README.md) rule 1).
- [ ] **Step 2:** Run `uv run pytest packages/pricing-core/tests/test_rate_table_weights.py -q`.
  Expected: every test fails with `ModuleNotFoundError: pricing_core.rate_tables.weights`, except
  Acceptance 5's diff-level case, which fails with `decimal.InvalidOperation`.
- [ ] **Step 3: Implement** the following:
  - per key, exactly one branch (`RL-1361` item 2):
    - `factor_ref` set: `resolve_factors(frame, factors[str(ref)], bandings=…, groupings=…)`,
      and the column `matrix.terms[factor.slug]` cast to `pl.String` (`RL-1361` §B);
    - `banding_ref` set: a numeric check on the Banding's `column`, then `apply_banding`;
    - neither set: the same-named column;
  - each stored cell key is parsed in the key's type: `int` as an integer, `bool` case-folded,
    `date` as a date, `string` exactly. The frame value is compared in that type;
  - an inner join of the frame's typed key tuple onto the cells' typed tuple; `group_by` the
    stored tuple, then `sum("exposure_years")`; zero sums are dropped;
  - `matched_exposure` is the sum over matched rows, and `portfolio_exposure` is the sum over
    every row. A null resolved key matches nothing but still counts in `portfolio_exposure`
    (`RL-1361` §E);
  - `matched_exposure == 0` raises `WeightJoinError`, naming the table's keys;
  - `FactorResolutionError` is re-raised as `WeightJoinError`, with its message kept.

  In `_compute_diff`, a weight equal to 0 is skipped like an absent one, so `total_weight` is
  never 0. That is the guard behind Acceptance 5.
- [ ] **Step 4:** Run the same command. Expected: all pass. Then
  `uv run lint-imports && uv run mypy`, which must stay clean (the pricing-core boundary).
- [ ] **Step 5:** Commit: `feat(pricing-core): exposure_weights — FR-231's per-cell weight join (RL-1361)`.

### Task 3: The platform: loaders, checks, the service and the cache (Acceptance 8–16)

**Files:**
- Modify: `backend/src/app/platform/rate_tables.py` (`diff`, `diff_needs_job`; add
  `check_portfolio`, `_portfolio_frame`, `_key_artifacts`)
- Modify: `backend/src/app/platform/diff_cache.py` (`DiffCache.key`; add `definition_hash`)
- Modify: `backend/src/app/platform/modelling.py` (add `load_factor_by_ref`)
- Modify: `backend/src/app/platform/transformations.py` (add `load_banding_by_ref`)
- Modify: `backend/src/app/platform/datasets.py` (add `read_version`)
- Test: `backend/tests/test_rate_table_diff_portfolio.py`, `backend/tests/test_diff_cache.py`

**Interfaces.**

Consumes: `exposure_weights`, `PortfolioWeights` and `WeightJoinError` (Task 2).

Produces:

```python
async def check_portfolio(session, *, workspace_id: UUID, version_id: UUID) -> DatasetVersionRow
    # RL-1361 item 7: read_version's scope 404, then the validated 409 (detail names the diff)
async def diff(database, workspace_id, slug, version, against, *, blob_store,
               cache: DiffCache | None = None,
               portfolio_dataset_version_id: UUID | None = None) -> RateTableDiff
def DiffCache.key(self, current_hash: str, baseline_hash: str, definition_hash: str,
                  portfolio_dataset_version_id: UUID | None, workspace_id: UUID | None) -> str
def definition_hash(table: RateTable) -> str   # sha256 of canonical JSON of keys + value
async def load_factor_by_ref(session, *, workspace_id: UUID, ref: ArtifactRef) -> list[Factor]
    # [the Factor, *its interaction operands], through load_factors; 404 names the ref
async def load_banding_by_ref(session, *, workspace_id: UUID, ref: ArtifactRef) -> Banding
```

- [ ] **Step 1: Write the failing tests:** Acceptance 8, 9 and 11–16 at service level, and
  Acceptance 10 at route level (Task 4 completes it). For the fixtures, reuse
  `backend/tests/test_api_rate_tables.py`'s `_seed_approved_model`, `_ensure_factor` and
  `_seed_body` (`:127-212`), and the validated-version helper of
  `backend/tests/test_interaction_factors.py:45` (`_validated`). Read each one's signature first
  (rule 1). A seeded `against=seed` diff after a re-seed is written to `RL-1375` (a2) (P9).
- [ ] **Step 2:** Run
  `uv run pytest backend/tests/test_rate_table_diff_portfolio.py backend/tests/test_diff_cache.py -q`.
  Expected: Acceptance 9 fails with `KeyError: 'portfolio_exposure'`. The others fail with a
  `TypeError` for the unexpected `portfolio_dataset_version_id` reaching the weight path, or for
  `DiffCache.key`'s arity. Record each.
- [ ] **Step 3: Implement**, in `diff`'s unit of work, in this order (`RL-1361` items 5–8):
  1. when a portfolio is given, `check_portfolio`, **before** `cache.get`;
  2. load the current definition (`RateTable.model_validate(version_row.definition)`, as now);
  3. compute `definition_hash(table)` and the key, with `workspace_id` only when a portfolio is
     given;
  4. on a miss:
     - `_portfolio_frame` reads `tables[0]` (DP-D) through `read_portfolio`;
     - `_key_artifacts` loads each `factor_ref` and `banding_ref` by ref, together with the
       Bandings and Groupings that the loaded Factors pin (`load_bandings` and `load_groupings`
       by id);
     - call `exposure_weights` and pass `weights=` to `diff_vs_previous` or `diff_vs_seed`;
     - set the two coverage fields from `PortfolioWeights`;
  5. map `PortfolioFrameError`, `WeightJoinError` and `FactorResolutionError` to
     `PlatformError("VALIDATION_FAILED", …, 422, <message>)`.

  `diff_needs_job` gains the same `portfolio_dataset_version_id` and runs `check_portfolio` first.
  So a refused portfolio never becomes a Job (`RL-1361` item 8).
- [ ] **Step 4:** Run the Step 2 command. Expected: all pass, except Acceptance 10's route half.
- [ ] **Step 5:** Commit: `feat(rate-tables): portfolio-weighted diff service and cache key (FR-231, RL-1361)`.

### Task 4: The route and the worker (Acceptance 10, 17)

**Files:** `backend/src/app/api/rate_tables.py` (`rate_table_diff`),
`backend/src/app/worker/rate_table_handlers.py` (`_rate_table_diff`); the tests in
`backend/tests/test_rate_table_diff_portfolio.py`.

- [ ] **Step 1: Write the failing tests** for Acceptance 10 and 17. For a parquet version, follow
  `test_a_diff_touching_a_parquet_version_answers_202_with_a_job`
  (`test_api_rate_tables.py:567`). Count `JobRow`s before and after each refused request.
- [ ] **Step 2:** Run them. Expected: 200 is served where 403 is required (Acceptance 10), and a
  `JobRow` is written for a refused portfolio (Acceptance 17).
- [ ] **Step 3: Implement.**
  - Add `portfolio: UUID | None = Query(None, description=…)`.
  - When `portfolio` is given, call `rbac.require_permission(..., permission=Permission.DATASET_READ, credential_permissions=caller.permissions)`,
    with no version load (P8). Then call `diff_needs_job(..., portfolio_dataset_version_id=portfolio)`.
  - The Job parameters gain `"portfolio": str(portfolio)` when it is given.
  - The 200 call passes the portfolio to `service.diff`.
  - `responses` gain 409.
  - The worker reads `parameters.get("portfolio")` and passes it to `service.diff`, which re-runs
    `check_portfolio` under the Job's workspace (`RL-1361` item 8).
- [ ] **Step 4:** Run `B` and `C` in full. Expected: all pass.
- [ ] **Step 5:** Commit: `feat(api): the diff route's portfolio parameter, checked before cache and Job (FR-231, FR-232)`.

### Task 5: The model-schema fields and the contract (Acceptance 9, 18, 20)

**Files:** `packages/model-schema/src/model_schema/rating.py`; regenerated
`docs/contracts/openapi/generated.json`.

- [ ] **Step 1:** Add `portfolio_exposure: Decimal | None = None` and
  `matched_exposure: Decimal | None = None` to `RateTableDiff`. Update the docstring to T6's
  meaning. This is done before Task 3's implementation step if the executor prefers, because
  Task 3 consumes the fields.
- [ ] **Step 2:** `uv run python scripts/generate-contracts.py`, then `--check`, which exits 0.
  Inspect `git diff docs/contracts/` (the `portfolio` parameter and the two properties only, plus
  DP-A (b)'s shape if decided).
- [ ] **Step 3:** Commit: `feat(model-schema): RateTableDiff coverage figures; contracts regenerated (FR-231, FR-451)`.

### Task 6: The per-cell diff (DP-A (b) only; Acceptance 18)

**Files:** `model_schema/rating.py` (`RateTableDiffCell`, `RateTableDiff.cells`);
`operations.py` (`_compute_diff` builds one row per changed key); the tests in `P` and `B`;
the contract regenerated.

- [ ] **Step 1:** Write `test_a_two_cell_change_returns_each_cells_change_and_weight`. Run it.
  Expected: it fails on the missing `cells` attribute.
- [ ] **Step 2:** Implement the shape as DP-A's minted text defines it. Every field is a `Decimal`
  or a string, and the relative change is `None` where the baseline is 0 or absent (as
  `_compute_diff` already treats them). Regenerate the contract.
- [ ] **Step 3:** Run `P`, `B` and `--check`. Commit:
  `feat(rate-tables): per-cell change and weight in RateTableDiff (FR-231, FD-1358)`.

### Task 7: The gate and the ledger

- [ ] **Step 1:** Run the full two-half gate (Acceptance 22) through the gate-runner. Record each
  rc and the tree.
- [ ] **Step 2:** Record DP-E's single timing: one weighted 200 diff on the freMTPL2 seed, with
  wall-clock, `uptime` load and the tree.
- [ ] **Step 3:** In the slice's `LG-` ledger, record:
  - Task 0's re-runs;
  - every red of Acceptance 1–18 with its printed line (paraphrase any line that names an
    undefined id, [`README.md`](README.md) rule 2);
  - `git diff --stat origin/main...HEAD` against §"Write set" (Acceptance 23).

## Hand-off

1. The lead mints this plan at the merge turn. The lead dispatches only after §"Activation needs"
   hold, in a separate activation PR, which flips `SL-1391` and this plan to `active`.
2. On merge, the auditor discharges the register row `FR-231 (F-W10-2)` and closes `FD-1358`
   under DP-A's decided option.
3. WK-675 Slice 5 (`PL-1286` `:307`) is unblocked. Its leaf plan reads this slice's merged
   `RateTableDiff`, not this plan's description of it.
4. WK-673 Slice 3 (`SL-1387`) follows, in `PL-1267`'s order.

## Self-review

1. **Coverage of the `SL-1391` row** (roadmap `:828`), clause by clause:
   - "the portfolio parameter and the refusal RL-1361 settles": Task 1 (T10), Tasks 3–4,
     Acceptance 10–14;
   - "aggregated to Σ exposure per cell key in Polars and passed as `weights`": Task 2;
   - "on the 202 path too": Task 4, Acceptance 17;
   - "an absent key column": Acceptance 6;
   - "an unweighted diff that says so": Acceptance 9;
   - "a hand-computed weighted mean": Acceptance 1–3 and 8;
   - "register row discharged on merge": Hand-off 2;
   - "RL-1375 DP-1 (a2) applies": P9 and Task 3 Step 1;
   - "never runs concurrently with SL-1377": activation need 3;
   - "carries FD-1358": DP-A, Task 6.
2. **Coverage of `RL-1361`'s Acceptance** (`:775-857`). Every bullet maps to Acceptance 1–17.
   The seeding bullets were `SL-1377`'s and are closed there.
3. **Every open choice is a DP** (A–E). No spec text is written without a ruling (Task 1).
4. **Repository literals checked at `caa4e411`:** every line range in §"Write set" and in P1–P9.
   The `RateTableDiff` fields and the zero-weight red were run (Task 0 Step 2). The T-text find
   strings were counted (Task 0 Step 3).
5. **What was not executed:** the test sketches. They depend on DP-B's minted signature and on
   fixture helpers whose signatures the executor reads first. A sketch that does not run as
   written is a plan defect to report, not to work around.
6. **Type consistency:**
   - `exposure_weights` and `PortfolioWeights` are defined in Task 2 and consumed in Task 3;
   - `DiffCache.key`'s five-argument form is defined in Task 3 and used in Acceptance 16;
   - `check_portfolio` is defined in Task 3 and called in Task 3 Step 3 and Task 4 Step 3.
