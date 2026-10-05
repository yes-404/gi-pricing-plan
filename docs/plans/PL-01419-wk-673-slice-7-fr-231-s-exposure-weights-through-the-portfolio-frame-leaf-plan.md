---
id: PL-1419
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

# PL-1419 — WK-673 Slice 7: FR-231's exposure weights through the portfolio frame, leaf plan

This plan was filed under working id 9716, which the lead reserved in `eta.md` (5 Oct 12:54:19), and
minted as `PL-1419` on 2026-10-05. Its slice is the existing row `SL-1391` under `### WK-673` in
[`../roadmap.md`](../roadmap.md), which is `draft`. The `tree:` above is the tree of `origin/main`
`caa4e411`. Every line number in this plan was read at that commit.

**Ordered by** the maintainer's (by delegation) instruction of 2026-10-05 12:51:33 BST, item 1, which the lead relayed in
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
reports `portfolio_exposure` and `matched_exposure` (`RL-1361` item 4). A separate route,
`GET /api/v1/rate-tables/{slug}@{version}/diff/cells`, serves every changed cell one cursor page at a
time, as `Page[RateTableDiffCell]`, with its change and weight (RL-1418 T1, T2; DP-A (c), FD-1358).
A parquet-stored pair answers 202 with a `rate_table.diff_cells` Job. `RateTableDiff` gains no
per-cell field.
The 202 path computes the same figures. Every refusal that
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
- it passes the weights to the existing `diff_vs_previous` and `diff_vs_seed`, and to RL-1418's
  `diff_cells` for the cells route.
The route checks first, then submits the Job or answers 200. The worker calls the same service
path.

**Tech stack.** Python 3.12, Polars, Pydantic v2 (`model-schema`), FastAPI, SQLAlchemy async,
pytest. No frontend change: WK-675 Slice 5 consumes this.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-231, FR-232, FR-228,
§4.2, §4.8 ("The portfolio frame"), §5.1 and §5.2. The rulings are `RL-1361` (DP-5, option (e),
with its exact texts T3, T6 and T10), **RL-1418** (minted from working id 9710; dm-1358's ruling on this plan's
DP-A, DP-B and DP-C: the cells route, its paging and ordering, the cell schema and its refusals,
the `03` §5.2 entries for `diff_cells` and `exposure_weights`, and T11 re-anchored as a correction
of `RL-1361`; draft PR #1128, read at head `c89ffe74`, texts T1–T5 and §"Correction of `RL-1361`
T11's anchor") and `RL-1375` DP-1 (a2). The finding is `FD-1358`. **The executor applies only RL
9710's and RL-1361's texts.**

## Status

`draft`. **DP-A, DP-B and DP-C are decided** by the maintainer (by delegation), in the entries headed "2026-10-05
12:58:22 BST" (DP-A (c), DP-B (a)) and "2026-10-05 13:00:09 BST" (DP-C (a); lanes A/C option (b))
in `to-lead.md`, as the lead relayed them. Their exact texts are **RL-1418** (minted from working id 9710; PR #1128, drafted
at `c89ffe74`). Its T5 is the planner's DP-B proposal, adopted with four amendments.
When this plan was filed it was not yet merged or minted, so the plan stayed `draft`.

**The open item against RL-1418 is closed.** At `b0c1237a`, RL-1418 said `RateTableDiff` was
"unchanged" and "byte-identical", while the same commit applies `RL-1361` item 4 and T6, which add
two optional coverage fields to it. The planner reported this to dm-1358 on 2026-10-05. At
`c89ffe74`, RL-1418 says it adds nothing to `RateTableDiff`, and that `RateTableDiff` changes in
the Slice 7 commit only by `RL-1361` item 4, T6 and T10. Its last acceptance bullet now reads:
"`RateTableDiff`'s schema differs from `caa4e411` only by `RL-1361` item 4's two optional
coverage fields" (verified at `c89ffe74`: Ruled item 1 at `:107-108`, the obliges line at
`:282`, the acceptance bullet at `:327-328`). The plan moves to `active` only through a
separate activation PR, after every activation need below holds.

### Activation needs, in order

1. **This plan is merged, minted, and made `active` by a dated line.**
2. **RL-1418 is merged and minted.** DP-A, DP-B and DP-C are decided (§"Status");
   RL-1418 carries their exact texts:
   - DP-A (c): the paged cells route in `03` §5.1, its paging and ordering, the cell schema, the
     refusals, and `diff_cells` in `03` §5.2;
   - DP-B (a): the `03` §5.2 entry for `exposure_weights`;
   - DP-C (a): T11's placement, re-anchored as a correction of `RL-1361`, payload unchanged.

   Where RL-1418's minted text differs from what this plan assumes, the minted text governs, and
   the dispatch record names each difference. An unminted RL-1418 is a stop.
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

**FD-1358: the paged cells route (DP-A (c), RL-1418 §"Acceptance"; `B` and `P`)**

18. Each test is red first. At `caa4e411`, the route-level tests fail because no
    `…/diff/cells` route is registered (FastAPI's `404 Not Found`, with no problem body), and the
    pure ones fail with `ImportError` for `diff_cells`.
    - `test_diff_cells_gives_each_cells_change_and_weight` (`P`, and `B` through the route): for a
      two-cell change, each cell's `abs_change`, `rel_change_pct` and `weight` equal
      hand-computed figures (FD-1358's own evidence).
    - `test_an_uplift_of_every_cell_is_served_in_full` (`B`): an `uplift_table` over more than
      `MAX_LIMIT` cells. The items number `changed_cells`, and no key repeats. With a cap
      introduced, the test fails.
    - `test_the_pages_concatenate_in_key_order` (`B`): pages at `limit=1` concatenate to
      `diff_cells`' full list in §4.2's order. The fixture's `"10"` sorts before its `"9"`. A
      repeated page returns identical bytes.
    - `test_the_cells_agree_with_the_summary` (`P`): `max_abs_change_pct` and
      `exposure_weighted_mean_change_pct`, recomputed from the items, equal `RateTableDiff`'s,
      with and without weights. `diff_cells` shares `_compute_diff`'s pass (RL-1418 §"What it
      obliges"). With a separate computation and one zero-baseline rule changed, the test fails.
    - `test_the_weight_has_three_states` (`P`): the weight is null with no weights, and null on a
      `removed` cell. It is `"0"` on a current cell that no row maps to, and on one whose mapped
      rows all have zero exposure; that cell is left out of the mean. With a missing weight read
      as `"0"` everywhere, the test fails.
    - `test_one_weights_map_feeds_summary_and_cells` (`B`): the map `exposure_weights` returns is
      the one that both `diff_vs_*` and `diff_cells` receive. A `FactorResolutionError` reaches
      the 422's detail with its count and example value. `WeightJoinError`'s own messages carry
      no value.
    - `test_a_bad_cursor_is_400_and_a_bad_limit_is_422` (`B`): a forged cursor and a cursor past
      the last cell each give 400 `VALIDATION_FAILED`, and `limit=MAX_LIMIT+1` gives 422.
    - `test_the_cells_route_refuses_before_anything_else` (`B`): each T1 refusal is given on a rows
      table and on a parquet table, and the parquet case writes no `JobRow`. A rating-only caller
      succeeds without `portfolio`.
    - `test_a_parquet_cells_request_runs_one_job_then_pages` (`B`): 202 with a
      `rate_table.diff_cells` Job and a `Location`. After the Job, the same request gives 200 pages
      equal to the rows-stored twin's. With the stored artifact removed, it gives 202 again, never
      another query's page. A portfolio archived between submit and run fails the Job with
      `DATASET_NOT_VALIDATED`.

**Spec, contract, gate, record**

19. **The spec texts are byte for byte.**
    - Each of `RL-1361` T3, T6 and T10, RL-1418 T1–T5, and `RL-1361` T11 at RL-1418's corrected
      anchor (`` `app.platform.rating_versions.require_compilable` is the only raiser)*. ``,
      `03:965`), is applied verbatim. `<Slice 7 date>` is set to the commit date, and RL-1418's own-id placeholder is
      set to RL-1418's minted id. Every find string occurs exactly once before it is applied.
    - Checked with `git diff origin/main...HEAD -- docs/specs/03-rating-engine.md` against the
      ruling's text blocks. Any wording that differs is a stop (`RL-1361` §"The exact texts").
    - `python3 scripts/audit-docs.py` exits 0.
20. **The contract.** `uv run python scripts/generate-contracts.py --check` exits 0 on the merge
    tree. `docs/contracts/openapi/generated.json` shows:
    - the `portfolio` query parameter on the diff route;
    - the new `RateTableDiff` properties (`grep -c '"matched_exposure"'
      docs/contracts/openapi/generated.json` prints at least 1);
    - the `…/diff/cells` route, `RateTableDiffCell`, and `rate_table.diff_cells` in the
      `JobKind` enum.
    RL-1418's acceptance at `c89ffe74`: `RateTableDiff`'s schema differs from `caa4e411` only by
    `RL-1361` item 4's two optional coverage fields, `portfolio_exposure` and `matched_exposure`
    (T6), and any other change to it fails. Checked with
    `git diff origin/main -- docs/contracts/openapi/generated.json`, read inside the
    `RateTableDiff` component.
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
  coverage fields, the diff cell and its page (RL-1418) are `model-schema` types in
  `model_schema/rating.py`; the page is the backend's existing `Page`. The contract is regenerated, never hand-edited.
- **No spec text is written by the executor.** Every `docs/specs/` byte comes from a ruling's text
  block: `RL-1361` §"The exact texts" (T3, T6, T10) or RL-1418 (everything else, T11's placement
  included). A find string not found exactly once is a
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
| `03` | FR-231 | The weight limb: Σ exposure per cell from a named portfolio, the weighted mean, the coverage figures, and the refusals (T3, T10); the paged per-cell change and weight (RL-1418, DP-A (c)) | `req("FR-231")` on Acceptance 1–18 |
| `03` | FR-232 | The 202 path carries `portfolio`, and the Job computes the same figures (T10; `RL-1361` item 8) | `req("FR-232")` on Acceptance 17 |
| `03` | FR-228 | Read only. The binding (`factor_ref`, `banding_ref`, or by name) decides the join. T1 is already applied (`03:119`) | none new |
| `07` | FR-451 | `RateTableDiff`, the route parameter and the cells route are regenerated into `docs/contracts/` | Acceptance 20 |
| `03` | NFR-495, NFR-496 | **Not applied.** Both are about premiums and the ladder. The diff produces no premium. The WK-673 row applies them to "this Work's artifacts", which are the Dislocation Run and the Attribution | — |

**Findings and register rows.**
- `FD-1358` (MEDIUM, owner WK-673). This slice closes it with RL-1418's paged cells route (DP-A (c)); FR-231's "each cell" is then delivered for every cell count FR-232 allows.
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
file, or a new file. A row marked *(RL-1418)* exists because RL-1418 (§"What it obliges") names it.

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
| `packages/pricing-core/src/pricing_core/rate_tables/operations.py` | edited: `_compute_diff` (`:386-435`), which ignores a zero weight; added *(RL-1418 T3)*: `diff_cells(...) -> list[RateTableDiffCell]`, sharing `_compute_diff`'s pass over the changed set | none in flight. WK-675 S4/S5 (not dispatched) read it | none |
| `packages/model-schema/src/model_schema/rating.py` | edited: `RateTableDiff` (`:735-747`) gains `portfolio_exposure` and `matched_exposure` (`Decimal \| None`); added *(RL-1418 T2)*: `RateTableDiffCell`. The page is the backend's `app.api.pagination.Page` (`pagination.py:48`), not a new `model-schema` type. `RateTableDiff`'s three existing fields are unchanged | none. `SL-1409` edits `model_schema/approvals.py` and `validation.py` only | none |
| `packages/model-schema/src/model_schema/jobs.py` | edited *(RL-1418)*: `JobKind` (`:55` region) gains `RATE_TABLE_DIFF_CELLS = "rate_table.diff_cells"`. `JobKind` is already exported, so `model_schema/__init__.py` does not change | none. `SL-1409` does not touch it | none |
| `backend/src/app/platform/jobs.py` | edited: the kind-to-queue map (`:74`) gains `JobKind.RATE_TABLE_DIFF_CELLS: JobQueue.COMPUTE` | none. `SL-1409` does not touch it | none |
| `backend/src/app/platform/rate_tables.py` | edited: `diff` (`:291-349`) and `diff_needs_job` (`:262-288`), each with a `portfolio_dataset_version_id` and the checks; added: `check_portfolio`, `_portfolio_frame`, `_key_artifacts`, and *(RL-1418 T1)* the cells page service, which answers a page from the stored cell artifact or reports that the Job is needed | none in flight (`SL-1377` closed) | none |
| `backend/src/app/platform/diff_cache.py` | edited: `DiffCache.key` (`:77-88`) gains `definition_hash` and `workspace_id`; added: `definition_hash` | none | none |
| `backend/src/app/platform/modelling.py` | added: `load_factor_by_ref` | none. `SL-1409` does not touch it | none |
| `backend/src/app/platform/transformations.py` | added: `load_banding_by_ref` | none | none |
| `backend/src/app/platform/datasets.py` | added: `read_version` (the lock-free twin of `load_version`, P7) | none. `SL-1409` does not touch it | none |
| `backend/src/app/api/rate_tables.py` | edited: `rate_table_diff` (`:278-321`), which gains the `portfolio` query and the checks before the cache read and the Job; its `responses` gain 409; added *(RL-1418 T1)*: the `…/diff/cells` handler, which returns `Page[RateTableDiffCell]` or 202 | none. WK-675 S2's routes are in other modules (rating algorithms and rating versions) | none |
| `backend/src/app/worker/rate_table_handlers.py` | edited: `_rate_table_diff` (`:24-54`), which passes `portfolio`; added *(RL-1418)*: `_rate_table_diff_cells`, registered in `register_rate_table_handlers` (`:65`) | none | none |
| `docs/specs/03-rating-engine.md` | edited: the FR-231 row (`RL-1361` T3, then RL-1418 T4, `:122`); §4.2 (T6 at `:312-322`, then RL-1418 T2 after T6's paragraph); the §5.1 diff row (T10, `:904`) with RL-1418 T1's row **inserted immediately after it**; the owned codes (T11 at RL-1418's anchor, `:965`); §5.2 (RL-1418 T3 and T5's signature before the fence at `:1120`, and T5's prose after `:1124`) | **WK-675 S2 (lane C)** inserts two `03` §5.1 rows: RL 9753 T2 before the `POST /api/v1/sub-graphs` row (`:897`) and RL 9766 T2 after the `POST /api/v1/rating-versions` row (`:908`). `SL-1409` edits `01` and `06` only | **shared, allowed under the maintainer's (by delegation) lanes A/C option (b)** (below) |
| `docs/contracts/openapi/generated.json` | regenerated | **`SL-1409`** regenerates it | exempt (generated) |
| `docs/contracts/schemas/generated/` | unchanged unless `RateTableDiff` is registered as a slug (it is not at `caa4e411`) | — | exempt (generated) |
| `packages/pricing-core/tests/test_rate_table_weights.py` | added | none | none |
| `backend/tests/test_rate_table_diff_portfolio.py` | added | none | none |
| `backend/tests/test_diff_cache.py` | edited: the tests that call `DiffCache.key` move to its new signature; added: Acceptance 16 | none | none |
| `backend/tests/test_api_rate_tables.py`, `backend/tests/test_worker_rate_tables.py` | edited only where a call to `service.diff` or `DiffCache.key` changes signature | none | none |
| `packages/model-schema/tests/test_rate_tables.py` | added: the `JobKind.RATE_TABLE_DIFF_CELLS` value, beside the existing `RATE_TABLE_DIFF` assertion (`:596`) | none | none |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | exempt (generated) for `INDEX.md` |

**Lanes A/C share `03` §5.1: option (b)**, the maintainer's (by delegation) decision of "2026-10-05 13:00:09 BST" in
`to-lead.md`, as the lead relayed it. Both slices may run. Its four conditions, each the
dispatch's to check:
1. **The dispatch records list each side's hunks and anchors.** This slice's `03` hunks are listed
   in the row above, at `caa4e411`. WK-675 S2's are RL 9753 T2 (insert before `:897`) and RL 9766
   T2 (insert after `:908`), read from drafts #1067 (`dm-9753-dp4-texts` at `96fa35bf`) and #1055
   (`dm-675dp56-rulings` at `39bd865b`).
2. **S2's new rows are not adjacent to S7's diff row.** At `caa4e411`, S7's T10 replaces `:904`.
   S2's nearest hunk is the insertion after `:908`, with `:905-907` (the two export rows and the
   import row) unchanged between them. RL 9753 T2's insertion before `:897` is seven rows away.
   RL-1418 T1 inserts the cells route row **immediately after** the diff row, so the unchanged
   gap stays `:905-907`. The executor re-measures
   this gap on the dispatch tree (Task 0 Step 3) and records it.
3. **The second to merge merges `main`, re-runs `git merge-tree`** (reading its exit code, not its
   first line), **and re-gates.**
4. **The two gates never overlap.**

**Result.**
- No path SERIALISES against `SL-1409`.
- One path is shared with `SL-1409`, and it is exempt: `generated.json`.
  `model_schema/__init__.py` is **no longer in this slice's write set**: `RateTableDiffCell` lives in
  `rating.py`, whose names `__init__.py` does not export (`git grep -n "RateTableKey\|RateTableDiff"
  origin/main -- packages/model-schema/src/model_schema/__init__.py` prints nothing), and
  `JobKind` is exported already (`__init__.py:123`, `:563`). So the `__all__` key is not reached.
- One path is shared with WK-675 S2 (lane C), `docs/specs/03-rating-engine.md` §5.1, and is allowed
  under the maintainer's (by delegation) option (b) above. PL 9713 (S2's leaf plan) was not on `origin` when this was
  read. Task 0 Step 3 re-reads its write set for any other shared path (`backend/src/app/api/`
  modules, `model_schema/rating.py`, `model_schema/jobs.py`, `platform/jobs.py`, `generated.json`).
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

About one and a half executor days. There are six tasks after the preconditions; Task 6 adds the
paged cells route (DP-A (c)). There are two new test modules, with real dataset versions, a seeded GLM and a parquet Job.
One full two-half gate run is needed. There is no NFR measurement, so the slice need not run
exclusive.

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-A** | **FD-1358.** FR-231 promises "the exposure weight behind each cell". `RateTableDiff` is aggregate only (P2), and T6 adds two more aggregates. WK-675 S5 needs per-cell data (`PL-1286` `:307`, `:290-292`) | (a) amend FR-231: aggregates only. (b) `RateTableDiff.cells`, a list of changed cells, optionally capped. (c) a separate paged cells resource | the plan recommended (b) | **DECIDED, (c)**, by the maintainer (by delegation), "2026-10-05 12:58:22 BST" (`to-lead.md`): "FR-231 says each cell, FR-232 allows 250k+ cells, and uplift_table changes every cell, so a capped list truncates on the commonest bulk op"; `RateTableDiff` stays the aggregate summary, with no contract break. Texts: RL-1418 (working id, dm-1358): the route in `03` §5.1 with its paging and ordering, the cell schema, the refusals, and `diff_cells` in §5.2. Applied as RL-1418 T1–T4 (route, cell shape and order, `diff_cells`, FR-231's clarification), with a new Job kind `rate_table.diff_cells`; Task 6; Acceptance 18 | Tasks 1, 5, 6 |
| **DP-B** | Where the join lives, and its `03` §5.2 text. RL-1361's texts cover FR-231, §4.2 and §5.1, not §5.2, and every public pricing-core function is listed in §5.2 (`03:1023`; `read_portfolio` `:1052`) | (a) a pure `exposure_weights` in `pricing_core/rate_tables/weights.py`, with a dated §5.2 entry; (b) a private helper in the platform | the plan recommended (a) | **DECIDED, (a)**, by the maintainer (by delegation), same entry. The planner drafted the §5.2 text (a signature block before the fence at `:1120`, after RL-1418's `diff_cells`, and a prose paragraph after `:1124`) and sent it to dm-1358 on 2026-10-05. RL-1418 adopts it as **T5**, with four amendments: its own-id placeholder (hyphenated); `diff_cells` among the functions that receive the map; `WeightJoinError`'s own messages carry no value, while a `FactorResolutionError`'s message is carried with its count and example (`RL-1361` item 3); and the types stay in `weights.py`. `PortfolioWeights.weights` is a `dict[KeyTuple, Decimal]`, so it is a `Weights` (`operations.py:88`) and is passed unchanged to `diff_vs_previous`, `diff_vs_seed` and `diff_cells` | Tasks 1, 2 |
| **DP-C** | T11's find string has 0 hits (Task 0 Step 3). `RL-1361` makes that "a stop … the executor does not re-word it" | (a) a correcting record re-anchors T11 on `` `app.platform.rating_versions.require_compilable` is the only raiser)*. ``, with the payload unchanged; (b) the dispatch record names the delta | the plan recommended (a) | **DECIDED, (a)**, by the maintainer (by delegation), "2026-10-05 13:00:09 BST": RL-1418 carries the re-anchor as a correction of `RL-1361`, payload byte-identical. RL-1418 §"Correction of `RL-1361` T11's anchor" gives the anchor (1 hit, `03:965`) and proves the payload byte-identical. The executor applies T11 there and never re-words it | Task 1 |
| DP-D *(not blocking)* | A portfolio Dataset Version with more than one table (P6) | (a) `tables[0]`, as fitting and banding proposal do; (b) refuse more than one table with 422 (a refusal T10 does not list, so it needs text) | **(a)** | **the plan's choice** (the lead, 2026-10-05: "keep your recommendations as the plan's choices, labelled as such"); recorded in the ledger. If it proves wrong, it is one function (`_portfolio_frame`) | none |
| DP-E *(not blocking)* | A rows-stored table with a large portfolio stays on the synchronous 200 path, because `RL-1361` item 8 lets storage, not portfolio size, choose 202 | (a) as ruled; (b) a portfolio row threshold also routes to 202 (a spec change) | **(a)**. The ledger records the wall-clock of one weighted 200 diff on the freMTPL2 seed (about 678k rows) as information, not as an NFR verdict. A slow figure is a finding for the lead | **the plan's choice** (same instruction) | none |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm each activation need. Quote RL-1418's minted id and its text blocks into
  the ledger, and list each place where the minted text differs from RL-1418 at `c89ffe74`, the
  head this plan was aligned to.
- [ ] **Step 2:** Re-run Task 0 Step 3's `grep -cF` over every find string, using the texts as
  minted. Any count that is not 1 is a stop.
- [ ] **Step 3:** Re-run the contention commands (§"Task 0 at planning time", Step 4). Record the
  output and each class in the ledger. A new SERIALISES path is a stop, reported to the lead.
  For lane C (WK-675 S2), list both sides' `03` §5.1 hunks and anchors on the dispatch tree, and
  the number of unchanged rows between S7's nearest hunk and S2's (it was 3 at `caa4e411`:
  `:905-907`). Zero, meaning adjacent, is a stop: the maintainer's (by delegation) option (b) requires the rows not to
  be adjacent.
- [ ] **Step 4:** `uv sync --all-packages`, then `uv run pytest packages/pricing-core/tests/test_rate_table_operations.py backend/tests/test_diff_cache.py -q`
  green on the base. Record the counts.

### Task 1: The spec texts, verbatim

**Files:** `docs/specs/03-rating-engine.md`.

- [ ] **Step 1:** Apply `RL-1361` T3 (`03:122`), T6 (`:312-313`, and the insert after `:322`) and
  T10 (`:904`), byte for byte. Set `<Slice 7 date>` to today's date (`date +%F`).
- [ ] **Step 2:** Apply RL-1418's texts, byte for byte, at its placements: T1 (the cells route row,
  inserted immediately after T10's row), T2 (after T6's "Coverage added" paragraph), T3 and T5's
  signature (before the §5.2 fence), T4 (appended after T3's text on the FR-231 row), T5's prose
  (after the `analysis.py` paragraph), and `RL-1361` T11 at RL-1418's corrected anchor. Set
  `<Slice 7 date>`, and set RL-1418's own-id placeholder to its minted id.
- [ ] **Step 3:** `python3 scripts/audit-docs.py`. It exits 0, or with check 31 only while a
  working id stands.
- [ ] **Step 4:** Commit: `docs(specs): 03 FR-231 weights and the paged diff cells (RL-1361 T3, T6, T10; RL-1418)`.
  Write RL-1418's minted id in the message; a working id in a commit message cannot be corrected.

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

RL-1418's minted §5.2 text (DP-B) governs the name and the signature. If it differs, follow the text and record
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
  Inspect `git diff docs/contracts/`. It shows the `portfolio` parameter and the two properties,
  and after Task 6 the cells route and its schemas. Nothing is removed or changed in
  `RateTableDiff`'s existing properties.
- [ ] **Step 3:** Commit: `feat(model-schema): RateTableDiff coverage figures; contracts regenerated (FR-231, FR-451)`.

### Task 6: The paged cells route (DP-A (c), RL-1418 T1–T4; Acceptance 18)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rate_tables/operations.py` (add `diff_cells`;
  factor `_compute_diff`'s changed-set pass so both use it)
- Modify: `packages/model-schema/src/model_schema/rating.py` (add `RateTableDiffCell`, T2's fields)
- Modify: `packages/model-schema/src/model_schema/jobs.py` (`JobKind.RATE_TABLE_DIFF_CELLS`)
- Modify: `backend/src/app/platform/jobs.py` (the queue map, `:74`)
- Modify: `backend/src/app/platform/rate_tables.py` (the cells page service)
- Modify: `backend/src/app/api/rate_tables.py` (the `…/diff/cells` handler)
- Modify: `backend/src/app/worker/rate_table_handlers.py` (`_rate_table_diff_cells`, registered)
- Regenerate: `docs/contracts/openapi/generated.json`
- Test: `P`, `B`, and `packages/model-schema/tests/test_rate_tables.py`

**Interfaces.**
- Consumes: `check_portfolio`, `_portfolio_frame`, `_key_artifacts` and `exposure_weights` (Tasks 2
  and 3); `Page`, `encode_cursor` and `decode_int_cursor` from `app.api.pagination`
  (`pagination.py:48`, `:64`, `:91`), with its limit constants by symbol.
- Produces (RL-1418 T3): `diff_cells(baseline_cells, current_cells, keys, value, *, weights: Weights | None = None) -> list[RateTableDiffCell]`.
  A key absent from `weights` reads `"0"` on a current cell when weights are given (RL-1418's
  answer on zero Σ); null means only "no weights" or a `removed` cell (T2).

- [ ] **Step 1: Write the failing tests** (Acceptance 18), each with `req("FR-231")`, and
  `req("FR-232")` on the parquet test. Every path, field and code comes from RL-1418 T1/T2.
- [ ] **Step 2:** Run them. Expected: the pure tests fail with `ImportError` for `diff_cells`.
  The route tests get FastAPI's `404 Not Found` with no problem body, because no route is
  registered. Record each.
- [ ] **Step 3: Implement**, in T1's order:
  1. the `against` resolution and the portfolio checks (`check_portfolio`), before any cell is
     read and before any Job;
  2. for a rows pair, the cells, the weights, then `diff_cells`, cut to one page at the decoded
     cursor position;
  3. for a parquet pair, the stored cell artifact, if it exists, is one blob keyed like the diff's
     cache, which means Task 3's full key: both content hashes, the definition hash, the
     portfolio id, and the workspace when a portfolio is named (`RL-1361` item 5). If it is found,
     answer 200 with the page cut from it. Otherwise submit `rate_table.diff_cells` (202,
     `Location`). The worker re-runs the checks, writes every changed cell in order as one
     blob, and records it under that key. An artifact that is not found is computed again,
     never served from another key.
  4. A cursor this API did not issue, or one past the last cell, gives 400; a bad `limit`
     gives 422 (the existing request-validation handler).
- [ ] **Step 4:** Regenerate the contract and run `--check`. Run `P`, `B` and the model-schema test in
  full.
- [ ] **Step 5:** Commit: `feat(rate-tables): the paged diff cells route with per-cell weights (FR-231, FR-232, FD-1358)`.

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
   (DP-A (c): the paged cells route).
3. WK-675 Slice 5 (`PL-1286` `:307`) is unblocked. Its leaf plan reads this slice's merged
   `RateTableDiff` and cells route, not this plan's description of them. Its diff shading and
   exposure-weight column page through the cells route.
4. WK-673 Slice 3 (`SL-1387`) follows, in `PL-1267`'s order.

## The RL-1309 carrier (added 2026-10-05, before the mint)

`RL-1309` `:309-310` (the DP-1 item 3 condition) requires an in-repo WK-673 record that carries
the sub-graph limb: `WK-1250` Slice 2's dispatch is gated on it (the maintainer's, by delegation,
ruling of "2026-09-30 14:47:19 BST — RL-1309:309-311's gate: NO, a local delta file doesn't
satisfy it; an IN-REPO carrier is needed", `channel/to-lead.md`, which names a WK-673 slice leaf
plan or ledger as the carrier). The maintainer's (by delegation) direction of "2026-10-05 16:43:57
BST — MERGE-ACK #1128 (RL-1418) …; answers to the queued items", WK-1250 item 2, puts the carrier
in this plan, in a normal commit before the mint: *"The RL-1309 carrier: a short dated note
quoting RL-1309 :309-310 verbatim, added to PL 9716 (#1127) in a NORMAL pre-mint commit (not
inside the mint commit), so its ACK's normalised diff shows it as reviewed content."* Both
entries are local and not in the repository.

`RL-1309` `:309-310`, verbatim, at `origin/main` `137bc817ef1fb40ea57e9053e0ad40b73bdff3a8`:

```text
   - **The maintainer's condition.** Before Slice 2 is dispatched, both WK-673's plan and
     PL-1254 Task 2 carry this limb. The first is the lead's to route, the second the
```

The two lines end mid-sentence in the source; the sentence closes on `:311`, "planner's.", which
the maintainer's ruling above names (`:309-311`). **The limb they refer to** is the `RL-1309` DP-1
item 3 bullet list at `:296-311`: `WK-1250` Slice 2 widens `AlgorithmDiff` and `diff_algorithms` to
cover sub-graph mounts and pins, and **WK-673 persists the whole diff the computation returns**
as the `structural_diff` evidence blob, never a hand-picked subset (`RL-1309` `:300-303`).
This section is a carrier only: it adds no task and changes no acceptance item.

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
   - "carries FD-1358": DP-A (c), Task 6, Acceptance 18.
2. **Coverage of `RL-1361`'s Acceptance** (`:775-857`). Every bullet maps to Acceptance 1–17.
   The seeding bullets were `SL-1377`'s and are closed there.
3. **Every open choice is a DP** (A–E). A, B and C are decided by the maintainer (by delegation), with texts in RL
   9710. No spec text is written without a ruling (Task 1). **The decisions are applied at every
   site** ([`README.md`](README.md) rule 5): narrative
   (Goal, Status, the DP table), Files (§"Write set", Tasks 1, 5 and 6), Steps (Task 0 Steps 1
   and 3, Task 1 Steps 1 and 2, Task 6), and Acceptance (18, 19, 20). No site still describes
   DP-A option (b).
4. **Repository literals checked at `caa4e411`:** every line range in §"Write set" and in P1–P9.
   The `RateTableDiff` fields and the zero-weight red were run (Task 0 Step 2). The T-text find
   strings were counted (Task 0 Step 3).
5. **What was not executed:** the test sketches. They depend on RL-1418's minted texts and on
   fixture helpers whose signatures the executor reads first. A sketch that does not run as
   written is a plan defect to report, not to work around.
6. **Type consistency:**
   - `exposure_weights` and `PortfolioWeights` are defined in Task 2 and consumed in Task 3;
   - `DiffCache.key`'s five-argument form is defined in Task 3 and used in Acceptance 16;
   - `check_portfolio` is defined in Task 3 and called in Task 3 Step 3, Task 4 Step 3 and
     Task 6 Step 3;
   - `diff_cells` is defined in Task 6 and consumes Task 2's `PortfolioWeights.weights` as its
     `weights`.
