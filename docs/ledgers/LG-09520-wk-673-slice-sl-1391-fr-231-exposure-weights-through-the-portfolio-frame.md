---
id: LG-9520
family: ledger
title: WK-673 slice SL-1391 — FR-231's exposure weights through the portfolio frame and the paged diff cells route (PL-1419), task ledger
status: active
created: 2026-10-05
owner: executor
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
phase: P2
work: WK-673
slice: SL-1391
plans: [PL-1419]
corrected_by: []
relates: [RL-1418, RL-1361, RL-1263, FD-1358, WK-673]
---

# WK-673 slice SL-1391 — FR-231's exposure weights through the portfolio frame

Executed from `PL-1419` by `executor-s7`. The model is Sonnet 5.5 (`claude-sonnet-5-5`). Branch
`sl-1391-fr-231-exposure-weights-portfolio-frame`, worktree `.claude/worktrees/sl-1391`, from `origin/main`
`5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a` (#1190, the activation). This record is under working id LG 9520 and mints
later. The dispatch record is the lead's local file `gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1391-2026-10-05.md`;
it is not in the repository.

## Tasks

### Task 0 — preconditions (no code), 2026-10-05

**Step 1 — activation needs.** Needs 1 to 6 hold: `PL-1419` and `SL-1391` are `active` on main; `RL-1418` is minted and
`active`; `SL-1377` and `SL-1386` are `closed`; the lane is free (the only `SL-` row with `status: active` is `SL-1391`:
`grep -n -B3 "^status: active" docs/roadmap.md | grep "id: SL"`); the maintainer's (by delegation) GO of "2026-10-05
17:17:37 BST — DISPATCH GO" stands.

**Differences between `RL-1418` as minted and `PL-1419`**, reported to the lead and ruled by the lead (the lead's
verdicts, dispatch record §(8)):

- **D1** — `RL-1418` says the texts land "in one commit with the code"; `PL-1419` has per-task commits. Ruled: follow
  the plan; the squash-merge lands one commit.
- **D2** — `RL-1418` T1 keys the cell artifact by both content hashes and the portfolio; `PL-1419` Task 6 Step 3 uses
  Task 3's full key (adds the definition hash, and the workspace when a portfolio is named). Ruled: follow the plan.
- **D3** — `PL-1419` Acceptance 6 has a Banding with `error` policy meeting an out-of-range value raise
  `WeightJoinError`; `RL-1418` T5's prose does not list that case. This is a case beyond T5's prose. It is implemented as
  `apply_banding`'s refusal re-wrapped as `WeightJoinError`. There is no spec text change.
- **D4** — the plan still carries working ids and a draft-PR head. Informational; swept at the mint.

**Step 2 — find strings**, `grep -cF -- <string> docs/specs/03-rating-engine.md` at `5fe56b87`:

| Text | Find string (start) | Hits |
|---|---|---|
| `RL-1361` T3 | `so an actuary sees which edits matter. \|` | 1 |
| `RL-1361` T6 | `"exposure_weighted_mean_change_pct": 0.8},` | 1 |
| `RL-1418` T5 prose | `§4.6 states their rules.*` | 1 |
| `RL-1361` T11, original anchor | `orphaning a blob. `app.platform.traces.complete_pending_trace` is the only raiser)*.` | **0** |
| `RL-1361` T11, `RL-1418` corrected anchor | `` `app.platform.rating_versions.require_compilable` is the only raiser)*. `` | 1 |

**Step 3 — contention.** No other `SL-` row is active. Open PRs touching a write-set path
(`gh pr list --state open --limit 200 --json number,headRefName,isDraft,files`, filtered to the write set): five draft
docs PRs on `03-rating-engine.md` only — #1200, #1188, #1179, #1126, #1048. None is a build. The lead lists their hunks
against this slice's only when one is about to merge. No new SERIALISES path.

**Step 4 — baseline.** `packages/pricing-core/tests/test_rate_table_operations.py`: 33 passed.
`backend/tests/test_diff_cache.py`: 5 passed, 1 error (`GIP_TEST_DATABASE_URL is not set`; the per-worktree test
database did not exist yet).

### Task 1 — the spec texts, verbatim

Applied to `docs/specs/03-rating-engine.md` by a script that copies each text block out of `RL-1361` (T3, T6, T10) and
`RL-1418` (T1 to T5, and T11 at the corrected anchor) and replaces `<Slice 7 date>` with `2026-10-05`. Each find string
occurred once before it was applied. After: each applied text occurs once; the original T11 anchor occurs 0 times;
`<Slice 7 date>` and `9710` occur 0 times in the file. `RL-1418`'s own-id placeholder was already its minted id in the
text.

### Task 2 — the pure join, red first (Acceptance 1 to 7)

**The maintainer's condition on D3** (by delegation, relayed by the lead): "if WeightJoinError reaches the WIRE as a
client-visible error code, that code must be in 03's owned-code list with a meaning, or the slice's spec commit adds it
(spec first, CLAUDE.md §0). If it maps to an existing listed code, no spec change, and the ledger names the mapping."
**The mapping:** `WeightJoinError.code` is `VALIDATION_FAILED`, as `PortfolioFrameError`'s is
(`packages/pricing-core/src/pricing_core/rating/analysis.py:60-64`). The platform `diff` service maps it, `PortfolioFrameError`
and `FactorResolutionError` to `PlatformError("VALIDATION_FAILED", …, 422, <message>)` (PL-1419 Task 3 Step 3.5, Task 4 for
the Job). `VALIDATION_FAILED` is a shared request-machinery code (`backend/src/app/errors.py:399-402`,
`_GENERIC_ERROR_CODES`), so it is not in 03's module-owned list by design; 03's diff row (`03:932`) and cells row
(`03:933`) already state "422 `VALIDATION_FAILED`" for these faults. No new code, no spec change. At the maintainer's (by delegation) wording order, the Banding `error`-policy refusal and
the out-of-range value are mapped under `03:932`'s "a resolution error". The D3 case
(`apply_banding`'s `error` policy) raises `FactorResolutionError`, which T5's prose already lists; it is re-wrapped with
its message kept, so it is not beyond T5.

**Red**, `uv run pytest packages/pricing-core/tests/test_rate_table_weights.py -q -x`, before `weights.py` existed:
`E   ModuleNotFoundError: No module named 'pricing_core.rate_tables.weights'` (collection error, 1 error). With
`weights.py` written and `_compute_diff` unchanged, 17 passed and `test_a_zero_exposure_cell_carries_no_weight` failed
with `decimal.InvalidOperation: [<class 'decimal.DivisionUndefined'>]` at `operations.py:427`
(`sum(...) / total_weight`), the cause Acceptance 5 names.

**Green**: the zero-weight guard in `_compute_diff` (a weight equal to 0 is skipped like an absent one). 18 passed;
`test_rate_table_operations.py` 33 passed; `ruff check packages/pricing-core`, `mypy` (227 files) and `lint-imports`
(4 kept, 0 broken) clean.

**Choice beyond the plan's wording.** `PL-1419` Task 2 Step 3 raises when `matched_exposure == 0`; the refusal is on
**no row mapping to a cell** (the join is empty), which is the spec's own words ("a portfolio whose rows map to no
cell", `RL-1418` T5). The two differ only when every matched row has zero exposure, which then gives an empty
`weights` and a `None` mean instead of a refusal.

**The lead's verdict** (2026-10-05, on this choice): follow `RL-1418` T5's own words, "the applied spec text governs
over the plan's prose", and the departure is from `PL-1419` Task 2 Step 3 ("`matched_exposure == 0` raises
`WeightJoinError`", plan `:618`). One condition: the case it opens must be defined and must not reach a division.
`test_rows_that_map_with_zero_exposure_are_no_weight_not_a_refusal` pins it: every matched row has zero exposure, so
`weights` is empty, the coverage is `matched_exposure` 0 of `portfolio_exposure` 0, there is no refusal, the diff's
weighted mean is `None` and there is no `InvalidOperation`. It passed on first run, with no red, because the
omit-a-zero-sum rule (`RL-1361` T3: "a cell whose Σ is 0 carries no weight") already defined the case; it is a
regression pin, and I checked `03` for any text that says otherwise for zero total exposure (`grep -n` over the
spec for "zero-exposure", "Σ is 0", "zero exposure", "all-zero"): only the FR-231 row's Σ-is-0 clause, which agrees.

### Task 3 — the platform: loaders, checks, the service and the cache (Acceptance 8 to 16)

The per-worktree test database was created per `dev-commands` (`gipricing_sl-1391_d5679908`, from the `gipricing`
template); `alembic current` and `alembic heads` both printed `e5b7d9f1a3c6 (head)`.

**Red**, `uv run pytest backend/tests/test_rate_table_diff_portfolio.py -q`:

1. Before any code: collection error `ImportError: cannot import name 'definition_hash' from 'app.platform.diff_cache'`.
2. With only `definition_hash` added (the rest unchanged), 20 failed, each for the stated cause:
   - `AttributeError: 'RateTableDiff' object has no attribute 'portfolio_exposure'` (and `'matched_exposure'`): the
     unweighted-says-so test, and the weighted tests' coverage asserts;
   - `AssertionError: assert None is not None`: the weighted mean is `None`, because the service passes no weights
     (`test_a_weighted_diff_matches_the_hand_computed_figures`, the banding and grouping test);
   - `Failed: DID NOT RAISE PlatformError`: a draft, an archived, a foreign and a dangling-ref portfolio, and the
     negative-exposure portfolio, are not checked (Acceptance 11 to 14);
   - `TypeError: DiffCache.key() takes 4 positional arguments but 6 were given`: the two cache-key tests;
   - `pydantic ValidationError` for `RateTable` in `test_a_definition_change_is_a_new_entry`: a defect in the test's own
     table fixture (a one-letter slug, a ref with a one-letter slug, and the required `version`, `rateable` and
     `storage` fields), fixed in the test, not a reading of the code.

**Green**: 20 passed. `DiffCache.key(current_hash, baseline_hash, definition_hash, portfolio, workspace_id)`; the
workspace is in the key only with a portfolio. `check_portfolio` runs before any cell is read and before the cache read,
in both `diff` and `diff_needs_job`; `exposure_weights` and the loaders (`load_factor_by_ref`,
`load_banding_by_ref`, `datasets.read_version`) are used through `_portfolio_weights`, which `PortfolioFrameError`,
`WeightJoinError` and `FactorResolutionError` leave as `PlatformError("VALIDATION_FAILED", …, 422, <message>)`.
`RateTableDiff` gained `portfolio_exposure` and `matched_exposure` here (Task 5 Step 1, which the plan lets come first,
because Task 3 consumes them), and `docs/contracts/openapi/generated.json` was regenerated (`--check`: 45 match).

**An existing test moved.** `test_diff_is_computed_on_miss_and_served_from_the_cache_on_hit` passed a random portfolio id
and expected a computed diff, because the id was only a key part. A named portfolio must now exist and be validated
(`RL-1361` item 7), so that tail now asserts the 404 and that the cache is not read; two portfolios being two entries is
`test_two_portfolios_are_two_cached_figures`. `test_diff_cache.py`'s key test moved to the new signature.

Targeted runs (one file each, `OMP_NUM_THREADS=1 nice -n 10`): `test_diff_cache.py` 6 passed;
`test_rate_tables_service.py` 13; `test_worker_rate_tables.py` 3; `test_api_rate_tables.py` 46. `ruff check` and `mypy`
clean.

### Task 4 — the route and the worker (Acceptance 10 and 17)

**Red**, the five new route and Job tests in `backend/tests/test_rate_table_diff_portfolio.py`, before the route and
worker changed:

- `test_portfolio_needs_dataset_read_and_hides_existence`: `assert [200, 200] == [403, 403]` (the route ignored
  `portfolio`, so a rating-only caller was served where `dataset:read` is required);
- `test_a_refused_portfolio_creates_no_job`: `assert 202 == 403` (a refused portfolio reached the Job);
- the three Job tests first failed `JOB_HANDLER_NOT_REGISTERED`, a defect of the test file (the handlers are not
  registered in the test process; an autouse `register_rate_table_handlers()` fixture, as `test_worker_rate_tables.py`
  has, was added). With the route changed and the worker handler **not** changed, the three failed for their stated
  cause: `test_the_job_result_equals_the_200_figure` `assert RateTableDiff(…exposure=None) == RateTableDiff(…
  matched_exposure=Decimal('7.500000'))` (the Job ignored `portfolio`); `test_a_portfolio_archived_before_the_worker_runs_
  fails_the_job` and `test_a_dangling_ref_fails_the_job_with_not_found` each `assert <JobStatus.SUCCEEDED> is
  <JobStatus.FAILED>` (the Job computed an unweighted diff instead of re-running the checks).

**Green**: 25 passed in the file. The route takes `portfolio: UUID | None`; with it, `rbac.require_permission(…
Permission.DATASET_READ …)` runs in the handler with no version load (so the same 403 for any id), then
`diff_needs_job(…, portfolio_dataset_version_id=…)` runs `check_portfolio`, so a refused portfolio writes no `JobRow`
(`test_a_refused_portfolio_creates_no_job` counts them for the 403, the 404 and the 409, and shows a rating-only caller
without `portfolio` gets its 202 and its Job). The Job's parameters carry `"portfolio"`; the worker reads it and calls
`service.diff`, which re-runs `check_portfolio` under the Job's workspace: an archived portfolio fails the Job with
`DATASET_NOT_VALIDATED`, a dangling ref with `NOT_FOUND`, and the result blob equals the 200 figure on the rows-stored
twin. The route's `responses` gain 409. A rating-only caller needs a stored custom role, because every built-in role
that holds `rating:read` also holds `dataset:read` (`READ_PERMISSIONS`); the test stores one.

Also: `docs/contracts/openapi/generated.json` regenerated for the `portfolio` parameter and the 409 (`--check` clean);
`test_api_rate_tables.py` 46 passed, `test_worker_rate_tables.py` 3, `test_api_authorisation_sweep.py` 9,
`test_contracts.py` 152 passed and 2 skipped; `ruff`, `mypy` clean.

### Task 5 — the model-schema fields and the contract (Acceptance 9, 18, 20)

Its Step 1 and Step 2 landed with Tasks 3 and 4, because those consume the fields and the route parameter.
`git diff origin/main -- packages/model-schema/src/model_schema/rating.py` shows `RateTableDiff` changed only by its
docstring and the two optional fields `portfolio_exposure` and `matched_exposure` (`Decimal | None = None`); its three
existing fields are untouched. `generate-contracts.py --check` exits 0 (45 match).

**A shared test** (dispatch record §(9), the lead's note): `backend/tests/test_diff_cache.py::
test_diff_is_computed_on_miss_and_served_from_the_cache_on_hit`, which this slice edited at `5134906a`, is shared with
`SL 9515` (the `FD 9529` fix, not yet active). Whichever slice merges second rebases it and re-runs the full gate (the
maintainer's ruling).

### Task 6 — the paged cells route (DP-A (c), `RL-1418` T1 to T4; Acceptance 18), part 1: the pure core

**Stop reported to the lead.** The new Job kind needs an Alembic migration (`JobKind` is the native PostgreSQL enum
`job_kind`, `backend/src/app/db/models.py:95-107`, as in `d5e6f7a8b9c0_rate_table_diff_job_kind.py:31`), and
`backend/migrations/` is in neither the plan's nor the dispatch record's write set. Everything that submits or reads a
`rate_table.diff_cells` Job waits for the lead's ruling; the parts below touch write-set paths only.

**Red**, `uv run pytest packages/pricing-core/tests/test_rate_table_weights.py -q`: collection error
`ImportError: cannot import name 'RateTableDiffCell' from 'model_schema.rating'`.

**Green**: `RateTableDiffCell` (`model_schema/rating.py`) and `diff_cells` (`operations.py`, next to `_compute_diff`, not
near `seed_from_model`). The changed-set pass is now one function, `_diff_cells`, which `diff_cells` returns and
`_compute_diff` summarises, so the summary and the cells cannot disagree. The new tests: `test_diff_cells_gives_each_
cells_change_and_weight`, `test_the_cells_are_in_key_order_by_code_point` (`"10"` before `"2"` before `"9"`),
`test_the_weight_has_three_states`, `test_the_cells_agree_with_the_summary[False|True]` (the mean, -5, and the maximum,
50, recomputed from the items). 57 passed with `test_rate_table_operations.py`; `ruff` and `mypy` clean.

## PRs

Not yet opened (the PR is opened as a draft after Task 2 is committed and pushed).
