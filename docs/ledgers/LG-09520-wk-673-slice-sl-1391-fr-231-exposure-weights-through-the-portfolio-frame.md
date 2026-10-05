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

## PRs

Not yet opened (the PR is opened as a draft after Task 1 is committed and pushed).
