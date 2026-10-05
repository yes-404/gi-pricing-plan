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

### Task 6 — part 2: the Job kind, the migration, the service, the route and the worker

**The migration, and the plan deviation.** `PL-1419` says no migration (its "Not in scope": "Any migration: existing
versions stay unbound"), and its write set lists none. `JobKind` is a native PostgreSQL enum, so the new kind needs one,
and `RL-1418` requires a kind of its own (`rate_table.diff_cells`) rather than reuse of `rate_table.diff`. The lead ruled
option A (dispatch record §(10)) and the maintainer (by delegation) upheld it, on three conditions (`to-lead.md`, "S7 Task 6:
option A is UPHELD", after 18:14), quoted: (1) mirror `d5e6f7a8b9c0` exactly: `ADD VALUE IF NOT EXISTS`, the downgrade a
commented `pass`, `down_revision` `e5b7d9f1a3c6`, no other DDL; (2) this ledger records the plan deviation, which §(10) is
the delta to; (3) exactly one Alembic head, checked at the gate and by the maintainer at the merge ACK, and if another
slice's migration lands on main first that is a stop and a rebase (re-point `down_revision`), never a merge migration. The
file is `backend/migrations/versions/f3a7c1d9e2b4_rate_table_diff_cells_job_kind.py`. On the per-worktree database,
`alembic upgrade head` ran `e5b7d9f1a3c6 -> f3a7c1d9e2b4`, and `alembic current` and `alembic heads` both printed
`f3a7c1d9e2b4 (head)`.

**Red**, `uv run pytest backend/tests/test_rate_table_diff_portfolio.py -q -k cells`, before the route existed: every route
test answered `{"type":".../not-found","title":"Resource not found","status":404,"code":"NOT_FOUND","detail":"Not Found"}`.
(The plan expected FastAPI's `404 Not Found` with no problem body; the app wraps it in a problem body, and `detail` is the
tell that no route matched.) The pure tests' red was `ImportError` for `RateTableDiffCell` (part 1).

**Green**: 35 passed in the file. The new tests: `test_diff_cells_gives_each_cells_change_and_weight_through_the_route`,
`test_an_uplift_of_every_cell_is_served_in_full` (250 cells, `MAX_LIMIT` + 50, across pages, no key repeats),
`test_the_pages_concatenate_in_key_order` (`"10"` before `"2"` before `"9"`, a repeated page the same bytes),
`test_one_weights_map_feeds_summary_and_cells`, `test_a_resolution_error_reaches_the_422_with_its_count_and_example`,
`test_a_bad_cursor_is_400_and_a_bad_limit_is_422` (a forged cursor, positions 0, 2 and 10000 on a two-cell diff, and
`limit=MAX_LIMIT+1`), `test_the_cells_route_refuses_before_anything_else[rows|parquet]` (403, 404, 409, unknown `against`;
no `JobRow`; a rating-only caller without `portfolio` gets 200 or 202), `test_a_parquet_cells_request_runs_one_job_then_pages`
(202, `Location`, kind `rate_table.diff_cells`; after the Job, 200 pages equal to the rows twin's; another portfolio is a
202; with the artifact's `BlobRow` deleted, a 202 again) and `test_a_cells_job_for_an_archived_portfolio_fails`
(`DATASET_NOT_VALIDATED`).

**Broken-input proofs** (a mutation, run, then reverted): `diff_cells_page` cutting `cells[:200]` fails the uplift test
(`assert 200 == 250`); a weight read as `"0"` on a `removed` cell fails the weight-states test (`assert Decimal('9') is
None`).

**How the artifact is found** (the lead accepted it as implementation). A Job's parameters carry `key`, `cells_key(...)`:
`version_content_hash` of both versions' cells (the one `diff` keys its cache by, `RL-1361` item 5), the definition hash,
and with a portfolio its id and the workspace. The Job writes one NDJSON blob and returns its sha256 as `result.ref`; the
route finds the newest succeeded `rate_table.diff_cells` `JobRow` of the workspace with that `key` whose blob still exists,
else it submits again. There is no cache or table dependency, because `DiffCache` fails open and a table would be a
migration. **The lead's correction:** my first version keyed a parquet version by its stored blob sha256, which differs
from `version_content_hash` of the same cells and so split a rows version from its parquet twin, against FR-232. Red,
`test_a_rows_version_and_its_parquet_twin_find_the_same_cells_artifact` (a (rows, parquet) pair and a (parquet, parquet)
pair of the same cells): `assert 202 == 200` (the second request submitted a second Job). Green after the key used
`version_content_hash` for both storages (36 passed in the file). The diff cache's own key was already
`version_content_hash(current_cells)` for both, so Task 3 needed no ruling. **A cost to know:** the cells route's parquet
request now loads both versions' cells to hash them, on every page request, which is the work FR-232 moves into a Job for
the diff itself; if that proves slow on a 250k-cell table it is a finding for the lead, not a measured NFR here.

**The second plan deviation** (the lead's verdict, dispatch record §(11)): the hand-authored
`docs/contracts/schemas/job.schema.json` lists every Job kind, and
`backend/tests/test_contracts.py::test_job_status_and_kind_enums_agree_with_the_contract` failed with `Extra items in the
left set: 'rate_table.diff_cells'`. The file is not in `PL-1419`'s write set, which names only `docs/contracts/schemas/
generated/`. One line, `"rate_table.diff_cells",`, was added after `"rate_table.diff",` (line 41, the precedent), and nothing
else in the file. `test_contracts.py` alone: 152 passed, 2 skipped; `generate-contracts.py --check` clean.

**The twin-key question** (the lead's, answered): the key uses `version_content_hash` for both storages, not the parquet
blob sha256. The cells artifact: `_content_hash`, `backend/src/app/platform/rate_tables.py:547-556`, which calls
`version_content_hash(await _load_cells_of(...))`. The diff cache: `rate_tables.py:492-493`,
`version_content_hash(current_cells)` and `version_content_hash(baseline_cells)`. Both are `diff_cache.py:48`. A rows version
and its parquet twin find the same stored artifact, one Job: `test_a_rows_version_and_its_parquet_twin_find_the_same_cells_
artifact` (red first, `assert 202 == 200`).

### Task 7 — the gate and the cost measurement

**Gate 1, head `c1f2ef177d3a7aed2a47ae8b100662b7d0c75dff`, tree `2618382e8508bed68996bcce4310fd39120d4859`**, slot `gate-1`
(granted by the lead), a detached checkout of that SHA with empty porcelain, `uv sync --all-packages`, `alembic current`
== `alembic heads` == `f3a7c1d9e2b4` (one head) before `pytest`. The `dev-commands` gate body verbatim with
`LOKY_MAX_CPU_COUNT=4`. Start 2026-10-05 18:25:12 BST (load 1.86, 19.3G free); Python half done 18:54:40 (load 3.63);
frontend half done 18:55:57 (load 8.72, 17.0G free).

| stage | result |
|---|---|
| ruff | pass |
| mypy | pass |
| import_linter | pass |
| audit_docs | **FAIL** exit 1: `check 31: gap in the full allocation between 1419 and 9520` (the working id, expected until the mint) |
| req_coverage | pass |
| contracts (`generate-contracts.py --check`) | pass |
| pytest | **FAIL** exit 1: 14 failed, 4985 passed, 4 skipped (29:10) |
| frontend install `--frozen-lockfile`, `generate:api`, lint, type-check, test, build | all pass |

**The 14 pytest failures.** Thirteen are downstream of the one audit failure, check 31: each is a test that runs
`audit-docs.py` or `doc-id.py` on the real tree and quotes its output (`tests/test_audit_docs_finding_citations.py`,
`test_audit_docs_ids.py` x2, `test_audit_docs_process_core_digest.py` x2, `test_audit_docs_w37_11_ceiling.py`,
`test_doc_index.py` (`the live allocation is not contiguous: [(1419, 9520)]`), `test_register_lint.py` x3,
`test_register_owed.py`, `test_repository_invariants.py` x2); the audit log's only failure is check 31. That is inferred
from the messages and is proved only by the minted-head gate. **One is a real red from this slice:**
`backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for` (NFR-499): the census
finds two sinks that use an exception's text, `backend/src/app/platform/rate_tables.py` `_portfolio_weights` `str(exc)` and
`packages/pricing-core/src/pricing_core/rate_tables/weights.py` `_resolved_series` `str(exc)`, neither listed in `_SINKS`
(that file's own rule: "a sink in one that is not a quote-input path is listed in `_SINKS` with why"). Reported to the lead
as a stop: `backend/tests/test_error_sinks.py` is outside the write set.

**Cost measurement, INVALID and not used** (inside `gate-1`, 18:56:08 to 18:56:46 BST, load 7.2 at the start because the
gate had just ended; no rows-stored baseline; run without the START / GO MEASURE protocol, so the lead's sweep was not
paused; the figures are kept only as information), `OMP_NUM_THREADS=1`, service level (`diff_cells_page`, not HTTP), a parquet pair of 260 000
cells (`(1, 'parquet')`, `(2, 'parquet')`), the cells Job having stored the artifact (Job 6.8 s, setup 5.3 s), N=10 pages at
limit 50 and distinct cursors:

| | p50 | p99 | max |
|---|---|---|---|
| whole page request | 1024 ms | 1204 ms | 1204 ms |
| of which loading both versions' cells | 490 ms | 566 ms | 566 ms |
| of which `version_content_hash` x2 | 442 ms | 552 ms | 552 ms |

**Against the bound.** No NFR bounds the diff or cells route's latency (searched `03`, `00`, `07`, `02`). The only text is
FR-232 (`03:123`): above the threshold (default 250 000 cells) "FR-231's diff and its exposure weighting become a Job
returning the same artifact, and the API answers 202 rather than 200 for them … only the latency and the status code
differ", and the cells row (`03:933`): "**202** with a `rate_table.diff_cells` Job … where either version is `storage:
parquet` (FR-232) and the query's cell artifact is not yet stored … the same request then answers **200** with pages read
from it". Whether FR-232 covers the cells page itself (so that the 200 read must not load both versions' cells) is a spec
reading for the maintainer, not decided here. About 93% of the request is loading and hashing the two versions' cells
(932 of 1024 ms at p50); no optimisation was made.

### Task 7 (continued) — audit-prep record

**The ruling on the `_SINKS` stop** (the maintainer, by delegation, `to-lead.md`, after 19:00, relayed by the lead): option (a)
adopted, both sinks listed in `test_error_sinks.py`'s `_SINKS` (count 1 each), each citing `RL-1361` item 3 and `RL-1418` T5
by id; option (b), routing them through the safe-exception helpers, refused. Done in the delta commit; `test_error_sinks.py`
alone: 4 passed. The delta commit is on top of `059599df`: the two `_SINKS` entries, the four `req("FR-231")` markers, and this
ledger. The re-gate follows at the new head, in `gate-1`, with the lead's allowance: exactly check 31's "1419 and 9520" line,
and the same 13 named tests failing on that gap; anything else is a stop.

**The third plan deviation.** `docs/contracts/schemas/generated/job.schema.json` gained one line (`"rate_table.diff_cells"`,
regenerated from the new `JobKind`). It is allowed by class (generated, exempt), but `PL-1419` `:445` says that directory is
"unchanged unless `RateTableDiff` is registered as a slug", a premise this slice falsified. The three deviations from the
plan's write set are therefore: the migration `backend/migrations/versions/f3a7c1d9e2b4_…` (the lead's §(10), the
maintainer's three conditions), the hand-authored `docs/contracts/schemas/job.schema.json` (§(11), `docs/contracts/README.md:17`
marks `schemas/` as hand-authored, so the enum line is the documented path), and this generated line.

**Acceptance 23, the write set.** `git diff --stat origin/main...HEAD` lists 24 paths: those of the plan's §"Write set", plus
exactly four deviations. The first three are above (the migration, the hand-authored `docs/contracts/schemas/job.schema.json`,
the generated `docs/contracts/schemas/generated/job.schema.json`). **The fourth is `backend/tests/test_error_sinks.py`** (+16:
the two `_SINKS` entries for the portfolio join's exception-text sinks), covered by the maintainer's option (a), in the entry
headed "2026-10-05 18:58:28 BST — S7 gate 1: (a) _SINKS entries ADOPTED; the re-gate plan CONFIRMED, with an explicit
allowed-failure set; the measurement re-run in the slot" (`to-lead.md`): "1. The NFR-499 sink STOP: (a). Both sinks go into
_SINKS WITH the reasons as you state them … (b) is refused: it would drop what RL-1361 item 3 requires."

**Acceptance 19, the texts byte for byte.** Each text was copied by script out of `RL-1361` (T3, T6, T10) and `RL-1418`
(T1 to T5, and T11 at the corrected anchor) (Task 1), and every find string occurred once before and the text once after.

**Acceptance 21.** `uv run python scripts/req-coverage.py` lists `FR-231` and `FR-232` against the new files. Every test in
`test_rate_table_weights.py` and `test_rate_table_diff_portfolio.py` carries `req("FR-231")`, and the 202 and Job tests
also carry `req("FR-232")`. At the gated head three Job tests and the twin test carried `FR-232` only; `FR-231` was added
(marker lines only).

**Mutation proofs** (the plan's "with X removed the test fails", each a single-file targeted run, `OMP_NUM_THREADS=1 nice`,
the file reverted and proven reverted: `git status --porcelain` clean, and `git hash-object <file>` equal to `git rev-parse
HEAD:<file>`; the driver is a scratch script). Every proof below is the failing line as printed.

| Acc | the break | the test that fails | the failing line | `hash-object` == `HEAD:file` after the revert |
|---|---|---|---|---|
| 2 | a `factor_ref` key joined by its same-named column | `test_a_factor_ref_key_weights_through_each_factor_type[identity, banding, grouping, interaction]` (4) | `WeightJoinError: key 'area_k': portfolio column 'area_k' is absent` | `weights.py` `7a64d59c122c92cbb83705ead01a3d3fd314d062`, equal |
| 3 | a `banding_ref` key joined on the raw column | `test_a_banding_ref_key_weights_through_apply_banding` | `WeightJoinError: no portfolio row maps to a cell of the table (keys 'age_band')` | same, equal |
| 4 | keys compared as raw strings (both sides) | `test_keys_compare_in_their_declared_type` | `WeightJoinError: no portfolio row maps to a cell of the table (keys 'ncd', 'garaged')` | same, equal |
| 6 | the zero-match refusal removed | `test_refusals_name_the_key_or_the_column[no-match]` | `Failed: DID NOT RAISE WeightJoinError` | same, equal |
| 8 | seeding does not set `factor_ref` | `test_seeded_banding_and_grouping_tables_are_weighted` | `WeightJoinError: key 'age_banded': portfolio column 'age_banded' is absent` | `operations.py` `ca48456091748f31cd85e83ce3ce0f1b278df7ed`, equal |
| 11 | the portfolio checks moved after the cache read | `test_a_foreign_portfolio_is_404_on_a_warm_cache` | `Failed: DID NOT RAISE PlatformError` | `rate_tables.py` `e1a2bdbe4a39e030a9ae0096515da60cf31d5a5a`, equal |
| 15 | the frame reader keeps only the declared columns | `test_the_frame_passes_through_undeclared_columns` | `FactorResolutionError: factor 'age_banded' needs ['age'], which this dataset version does not have (FR-87)` | same, equal |
| 16 | the portfolio id removed from the cache key | `test_two_portfolios_are_two_entries`, `test_two_portfolios_are_two_cached_figures` | `assert 'rate_table:diff:c:b:d:<uuid>' != 'rate_table:diff:c:b:d:<uuid>'`; `assert 1 == 2` | `diff_cache.py` `128110066e7fa68fe231181c8ae508078cdf2884`, equal |
| 16 | the workspace removed from the cache key | `test_two_workspaces_are_two_entries_with_a_portfolio` | the same `!=` assertion | same, equal |
| 16 | the definition hash removed from the cache key | `test_a_definition_change_is_a_new_entry` (8 of 8 params) | `assert 'rate_table:diff:c:b:none' != 'rate_table:diff:c:b:none'` | same, equal |
| 18 | the zero-baseline rule changed (a zero baseline reads a 0 percentage) | `test_the_cells_agree_with_the_summary[True]` | `assert Decimal('-2.222222222222222222222222222') == Decimal('-5')` | `operations.py` same as above, equal |

Acc 18's "with a cap introduced" and the weight-states proofs are recorded under Task 6 (`assert 200 == 250`, `assert
Decimal('9') is None`). Acc 18's "separate computation" is not a break one can run: the summary is computed from the cells'
own pass, so a separate computation is the thing the design removes; the zero-baseline mutation above shows the test is
sensitive to that rule on the shared pass. **Acceptance 10 and 17** each name a break (`dataset:read` route-wide; the handler
check removed; the worker's re-check removed); the worker's was run (Task 4: the Job tests failed with the worker unchanged);
the other two are covered by the Task 4 reds (`[200, 200] == [403, 403]`, `202 == 403`).

**Acceptance 15's red.** `test_the_frame_passes_through_undeclared_columns` was one of the 20 reds at Task 3
(`AttributeError: 'RateTableDiff' object has no attribute 'matched_exposure'`: the fields did not exist yet); it is not
a pin. The mutation above is its own proof.

**The cost measurement, the maintainer's ruling and the protocol** (relayed by the lead): the maintainer (by delegation)
ruled that "FR-232's 'only the latency and the status code differ' PERMITS a slower page, and no NFR bounds these routes,
so it is NOT an S7 defect and does NOT block S7; S7 ships as built, with the numbers in the ledger". The filing rule is the
maintainer's, not a requirement: a parquet p50 within 3x the rows baseline is no finding; over 3x, or any p99 over 1 s, the
lead files an FD (WK-1178) and an OQ for the missing latency NFR. **The 18:56 measurement above does not count:** it ran at
load 7.2 right after the gate, without the rows-stored baseline, and without the START / GO MEASURE protocol (the lead's
sweep was not paused). It is kept as information only. The re-run, with the protocol, is in the same slot as the re-gate.

**The delta proof's conditions** (the maintainer, by delegation, after 18:40, relayed by the lead): a delta stands in for a
re-gate only if `git diff c1f2ef17..HEAD` touches nothing under `backend/src`, `packages/*/src`, `frontend/src`,
`backend/migrations` or `docs/contracts`, every changed test-file line is a req-marker line, and the rest is the ledger and
the PR body. This delta is not that: the lead holds `test_error_sinks.py`'s `_SINKS` entries for the maintainer's ruling and
expects a full re-gate.

### Task 7 — gate 2, the re-gate at the delta head

**Head `75928847e0fc4989d422c1ef3674ed8189ea44cd`, tree `fb95424587f8c845ebd172ec9707db8769a69188`** (detached checkout,
`git status --porcelain` empty at the set-up, about 19:03 BST, and again at 19:44 BST; `alembic current` == `alembic heads` ==
`f3a7c1d9e2b4`). Granted by the lead for `gate-1`. The delta against the gated `c1f2ef17` is `test_error_sinks.py` +16,
`test_rate_table_diff_portfolio.py` +4 (marker lines) and this ledger; nothing under `backend/src`, `packages/*/src`,
`frontend/src`, `backend/migrations` or `docs/contracts`. Stamps are `TZ=Europe/London` (BST); `uptime` prints UTC.

**Python half** (the `dev-commands` gate body verbatim, `LOKY_MAX_CPU_COUNT=4`). The slot was held from 19:03:23 BST and the
lead's START was honoured at 19:04:20 BST (uptime 18:04:20 UTC, load 4.79/4.57/4.11, 17 356 MB free). Logs and `.rc` files:
`/tmp/tmp.RxXXLtJE37/` (scratch, not in the repository). Stage table:

| stage | exit | result |
|---|---|---|
| ruff | 0 | pass |
| mypy | 0 | pass |
| import_linter | 0 | pass |
| audit_docs | 1 | FAIL: `check 31: gap in the full allocation between 1419 and 9520` only |
| req_coverage | 0 | pass |
| contracts (`generate-contracts.py --check`) | 0 | pass |
| pytest | 1 | FAIL: `13 failed, 4986 passed, 4 skipped, 87 warnings in 1669.22s (0:27:49)` |

The 13 failures are exactly the allowed set (the working id's check 31 plus the same 13 tests that fail on that gap):
`test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`,
`test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks` and `::test_doc_id_check_exits_0_on_the_real_tree`,
`test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green` and
`::test_the_committed_digest_currently_matches_the_committed_spec`,
`test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`,
`test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`,
`test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`, `::test_check_29_note_carries_the_residue_line` and
`::test_phase1b_residue_count_matches_check_29s_own_count`, `test_register_owed.py::test_check_29_wiring_is_undisturbed`,
`test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit` and
`::test_journey_citations_are_audited_in_ci`. `backend/tests/test_error_sinks.py` passes: the 14th failure of gate 1 is gone.
The lead verified the report against the logs.

**Frontend half**, re-taken in a fresh hold at 19:42:39 BST on the same head: `pnpm --dir frontend install --frozen-lockfile`,
`generate:api`, `lint`, `type-check`, `test` and `build` all pass (each command's exit code 0; wrapper logs
`/tmp/tmp.mbfMWBTkto/fe2_*.log`, scratch). Finished 19:43:38 BST (uptime 18:43:38 UTC, load 6.55/2.99/2.58, 19 251 MB free).

**The slot's history, stated as it happened.** The first hold ran the python half and was released at **19:32:26 BST, when
the script exited**: a shell-quoting error in my chained command after the gate body (a stray `;` before `echo PYTHON_HALF_RC`)
ended the held script before its frontend and measurement phases ran. That release was **not on purpose**, and the stage
table had already printed. At 19:42:39 BST I took `gate-1` again with `flock -n` to run the frontend half, before the lead's
order not to take a slot reached me. At 19:44:02 BST, on the maintainer's order (by delegation), I killed my own processes by
pid (each pid's `/proc/<pid>/cwd` read as this worktree) and `flock -n /tmp/slots/gate-1 true` printed free (uptime 18:44:02
UTC, load 4.44/2.78/2.52, 19 475 MB free). No measurement ran from this head and none is claimed.

**Two stamps are missing, for the maintainer to judge:** the python half's end `uptime` and `free` (my chained `echo MID …;
uptime` line never ran, because of the quoting error), and the frontend half's start `uptime` and `free` (not recorded at
19:42:39 BST).

**The maintainer's ruling on this re-gate** (by delegation; `to-lead.md`, the entry headed "2026-10-05 19:45:18 BST — S7's
re-gate COUNTS; the missing machine-state stamps are a ledgered omission, not a re-gate"), quoted verbatim:

> (b) is satisfied: you verified it from the log (13 failed, exactly the allowed set; test_error_sinks passes; check 31 only;
> the other stages rc 0). The frontend half: all 6 pass.
> (a): the python-half START prints head 75928847 and tree fb954245. The FRONTEND half's start porcelain is NOT in the log, so
> it is UNPROVEN, but it is IMMATERIAL to the result: the frontend checks depend only on frontend/ and the generated client,
> which no docs or ledger commit touches, and the mint head's CI re-proves both halves anyway.
> The missing uptime/free stamps (the python END and the frontend START) are a CHECKLIST OMISSION: no assertion in either half
> is timing-bound, and contention can only cause spurious failures, not a false pass. So the gate COUNTS. LG 9520 records the
> omission in those words, with the 19:32:26 script-bug release.
> BACKSTOP, unchanged: S7's merge ACK requires FULL green CI at the mint head (check 31 and the 13 cleared by the LG mint).

So, in those words: the missing `uptime` and `free` stamps (the python half's end and the frontend half's start) are a
**checklist omission**, and the 19:32:26 BST release was the script's own bug (a shell-quoting error in my chained command),
not a decision.

**The order of the measurement.** The maintainer (by delegation) ordered, relayed by the lead: at `READY_FOR_MEASUREMENT` do
not measure, release `gate-1`, and report from the log. S7 may mint and merge on that report plus CI. The cost measurement,
parquet and a rows-stored baseline at limit 50 with N of at least 10, under the START / GO MEASURE protocol, runs later on the
lead's grant, after SL 1427's gate, and is ledgered then. The 18:56 figures above stay INVALID.

### Task 8 — R1: every cells page from the stored artifact (the maintainer's ruling, option (A), inside this slice)

**The measurement that raised it** (a quiet `gate-1` hold, 22:12:36 to 22:23:33 BST, head `386f4d54`, tree
`1511ac46a4f5298a01cb65820bdcf559639b0046`, `OMP_NUM_THREADS=1`, service level, N=10 pages at limit 50, storage asserted
rows at the default threshold): a rows pair's cells page, p50 / p99 in ms: 250 000 cells unweighted 9639 / 9848 (SQL load of
both versions 5469 / 5710, `version_content_hash` x2 382 / 414, `diff_cells` 3971 / 4188); 250 000 weighted (a 678 000-row
portfolio) 12241 / 12434 (the portfolio read and join alone 1568 / 1611); 100 000 unweighted 4104 / 4265. `07` §1.3 R1: "Any
operation that can exceed 2 s returns `202` with a Job"; the worst p99 at 250k was 12 434 ms. These figures are the red for the
latency limb of this task. State at the start 22:12:36 BST: load 0.77/0.80/0.62, 20 100 MB free, `pgrep` empty; at the end
22:23:33 BST: load 1.54/1.59/1.17, 19 521 MB free, `pgrep` empty. (An earlier run at 18:56 BST and the 20:45 BST parquet / rows
pair at 260 000 cells are recorded above; the 18:56 run is invalid.)

**The ruling** (the maintainer, by delegation, `to-lead.md`, the entry headed "2026-10-05 22:25:03 BST — S7 R1 STOP: (C)
REFUSED (it does not comply); (A) with the IDENTITY key, INSIDE S7, by an RL first; FD 9487 widened to the diff route"): (C) is
refused, because the pages after its Job would still reload and hash every cell; (A) inside this slice: every cells page for a
version pair is served from the stored artifact, the first request for a (versions, portfolio) key answers 202 with a Job,
rows pairs too, and later pages read only their NDJSON slice; **the key is immutable version identity** (`slug@version` on each
side and the portfolio Dataset Version id), found without loading or hashing a cell; no migration; the content-hash twin
sharing is reversed, and the twin test is rewritten to assert distinct keys and identical content; spec first, by one RL (working
id RL 9484) that amends `RL-1418` T1 / `03:933` and FR-232's "editor pages without a job"; FD 9487 widened to the diff route.
This is the fifth plan deviation, recorded in the dispatch record's §(12).

**Red** (`backend/tests/test_rate_table_diff_portfolio.py`, before the change): `test_a_rows_pair_answers_202_first_then_pages_
from_its_artifact` failed with the first request answering 200 (the page computed in the request);
`test_a_later_page_loads_no_cells` failed with a 500 `INTERNAL_ERROR` (the page reached the monkeypatched cell loader that
raises `a cells page loaded cells`); `test_the_artifact_is_keyed_by_version_identity_so_twins_do_not_share` failed with 200 where
202 was expected.

**Green**: `cells_key(slug, current_version, baseline_version, portfolio)` is the identity key
(`rate_table:diff_cells:<slug>@<v>:<slug>@<b>:<portfolio|none>`); `diff_cells_page` no longer branches on storage or hashes
anything: it resolves the versions (and the portfolio checks), looks up the stored artifact by that key, and answers a page
from it or reports that the Job is needed. The Job is unchanged (it carries the key and writes the NDJSON blob). The existing
cells-route tests were updated to build the artifact first (a 202, the Job run, then pages); `test_a_resolution_error_reaches_
the_failed_job_with_its_count_and_example` replaces the 422 test, because the weights are now computed in the Job: the refusal
(`VALIDATION_FAILED`, with the count and example value `RL-1361` item 3 requires) is the Job's failure, not the response's.
The contract is regenerated (the route's description). 38 passed in the file; `ruff`, `mypy`, `generate-contracts --check` clean.
The 03 texts wait for the minted RL; the later-page p99 < 300 ms and the 250 000-cell first-request-202 measurement need the
slot and wait for it.

### Task 8 (continued) — the diff route on the same artifact, chunks and a manifest, the in-flight rule

**The rulings applied** (the maintainer, by delegation, relayed by the lead; the dispatch record's §(12) quotes them): "2026-10-05
22:27:31 BST — S7: the write set ACCEPTED; the diff-route measurement on the branch ACCEPTED with the diff proof; the diff
route goes INTO S7, option (a)"; "2026-10-05 22:32:19 BST — S7 / RL 9484: all four asks ACCEPTED, with one precision each; the
literal-main measurement decision upheld" (chunks and a manifest, with a page touching at most two chunks for every legal limit;
the test-file widening; the in-flight rule; the 1M harness); "2026-10-05 22:31:11 BST — S7 flags: (1) async portfolio refusals
ACCEPTED, stated in RL 9484; (2) the unindexed lookup measured at a STATED Job count". The 03 texts wait for the minted RL.

**Red** (`backend/tests/test_rate_table_diff_portfolio.py`, before the code): `test_a_diff_answers_202_first_then_200_from_the_
same_artifact` answered 200 on the first diff (computed in the request); `test_a_later_diff_loads_no_cells` a 500 (the diff
reached the monkeypatched cell loader); `test_a_page_reads_the_manifest_and_at_most_two_chunks` `json.decoder.JSONDecodeError:
Extra data` (the artifact was one NDJSON blob, not a manifest). The in-flight test passed on its first run (written with
the code); its break (the in-flight reuse removed) fails it with `assert '<job id>' == '<other job id>'`; `rate_tables.py`
before and after the break: `8f83d8a15222f3d954062e4e1c3a143d8c3e1129`, equal.

**Green.** The artifact is `CELLS_CHUNK` (1000, at least `MAX_LIMIT`) cells per chunk blob, NDJSON, plus one manifest
(`chunk_size`, `total`, `chunks`, and `summary`: the `RateTableDiff` with its coverage figures); the Job's `result.ref` is the
manifest. A cells page reads the manifest and the one or two chunks it lies in; the diff route reads the manifest only.
`diff_summary` (`operations.py`) derives the summary from the cells (one pass, shared with `_compute_diff`). Both routes use one
Job (`rate_table.diff_cells`) and one key: a first request for a key answers 202; a request while that Job is queued or
running answers 202 with THAT Job (no second); a failed Job is not cached, so the next request starts a new one; a succeeded
Job with its manifest answers 200. `rate_table.diff` stays valid in the enum and the schemas for old rows; this route no longer
creates it, and its worker handler and `diff()` remain. 41 tests pass in the file; `test_api_rate_tables.py` (46) was updated
to run a Job when a diff answers 202 (`_diff_ready`; the parquet 202 test now expects kind `rate_table.diff_cells`);
`test_worker_rate_tables.py` 3, `test_rate_tables_service.py` 13, `test_diff_cache.py` 6, `test_contracts.py` 152 (+2 skipped),
the pricing-core rate-table tests 57; `ruff`, `mypy` and `generate-contracts --check` clean.

**What the diff-route proof will say.** `_compute_diff` was rewritten unconditionally by this slice (it now summarises
`_diff_cells`' per-cell objects), so `svc.diff(…, portfolio None)` on this branch is not main's path. The lead upheld the
literal-`origin/main` measurement for FD 9487's evidence.

**The ref 404 is synchronous** (the maintainer, by delegation, relayed by the lead): an unresolved `factor_ref` or `banding_ref`
is a `404` naming the key and the ref BEFORE any Job, on both routes and both storages, and `RL 9484` supersedes `RL-1361`'s
parquet "the Job fails with NOT_FOUND" clause. Red: `test_a_dangling_ref_is_a_synchronous_404_before_any_job` (route x
storage x ref kind, 8 cases) answered 202 and created a Job in each. Green: `_refuse_dangling_refs` runs
`_key_artifacts` when a portfolio-weighted query has no artifact and no Job in flight, before the Job is submitted
(a query that finds its artifact, or its Job, never reaches it; an unweighted query reads no ref). The other content-dependent
refusals (a missing column, a negative exposure, a portfolio that maps to no cell, a Banding error policy) are the Job's
`VALIDATION_FAILED`: `test_a_portfolio_refusal_that_reads_the_content_is_the_jobs_validation_failed` (both routes) asserts
the code, that the message names the column or the count, and that a sentinel portfolio value never appears (NFR-499); these
passed on first run, because the Job path already carried them, so they are pins. `test_a_resolution_error_reaches_the_failed_job_
with_its_count_and_example` keeps `RL-1361` item 3's count and example. 49 tests pass in the file; `test_api_rate_tables.py` 46.

**Hold A: the pre-S7 diff route, measured literally on `origin/main`** (FD 9487's evidence; the maintainer's 22:27:31 BST
condition, whose branch-based proof failed because `_compute_diff` was rewritten unconditionally by this slice, so the branch's
`svc.diff` is not main's path). A second detached worktree at `origin/main` `52c153cd1dcf7eb8a716559216a30b245dd6a7e2` (tree
`4fe99da0472c47845330aec9e7731ba3b06afc53`), its own venv and database at Alembic head `e5b7d9f1a3c6`, in `gate-1`
(2026-10-05 22:46:20 to 22:50:53 BST): START load 2.60/2.10/1.61, 18 660 MB free, `pgrep` empty; the lead's GO seen 22:47:02;
load settled to 1.86 after 10 s; timing began 22:47:07; END 22:50:53 BST, load 1.70/1.98/1.69, 18 510 MB free, `pgrep` empty.
`OMP_NUM_THREADS=1`, service level, no portfolio, no cache, N=10, a 250 000-cell ROWS pair seeded through main's own seed and uplift
(rows asserted): `svc.diff` whole request p50 9286 ms, p99 9633 ms; SQL load of both versions p50 6696 / p99 7688 ms;
`diff_vs_previous` alone p50 1825 / p99 1858 ms. The diff route on main breaches `07` §1.3 R1's 2 s by about 4.6x at 250k, which
is FD 9487's limb (a breach on main, discharged by this slice moving the route onto the stored artifact). This slice's
rewrite of `_compute_diff` (it now summarises `_diff_cells`' per-cell objects) makes that phase about 4.0 s against main's
1.8 s, now inside the Job only, off the request path.

**An unweighted query gets no ref 404** (the lead's answer, the maintainer's rule): it reads no `factor_ref` or `banding_ref`,
and `RL-1361` T10 lists that 404 under the portfolio checks; `_refuse_dangling_refs` is a no-op without a portfolio.

## PRs

#1206, a draft, `SL-1391: Slice 7: FR-231's exposure weights through the portfolio frame (F-W10-2)`, head branch
`sl-1391-fr-231-exposure-weights-portfolio-frame`.
