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
(`03:933`) already state "422 `VALIDATION_FAILED`" for these faults. No new code, no spec change. The D3 case
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

## PRs

Not yet opened (the PR is opened as a draft after Task 2 is committed and pushed).
