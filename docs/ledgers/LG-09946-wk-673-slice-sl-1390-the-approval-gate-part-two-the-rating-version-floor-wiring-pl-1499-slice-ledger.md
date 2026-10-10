---
id: LG-9946
family: ledger
title: WK-673 slice SL-1390 — the approval gate, part two — the rating_version floor wiring (PL-1499), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9
phase: P2
work: WK-673
slice: SL-1390
plans: [PL-1499]
corrected_by: []
relates: [PL-1499, RL-1504, RL-1445, RL-1263, SL-1389, FR-363, FR-364, FR-257, FR-352]
---

# LG-9946 — WK-673 slice SL-1390: the approval gate, part two — the floor wiring

**GO:** not yet given. Authoring ahead of the GO at the user's order (the lead's brief `brief-executor-s6-authoring-2026-10-10.md`, local, authority "2026-10-10 03:07:11 BST — W3 pacing"): code and tests are written on a branch from `origin/main` `db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9`; no PR and no gate before the GO.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `PL-1499`, slice `SL-1390`, WK-673 Slice 6: *"the approval gate, part two — the floor wiring"*. Its scope is `PL-1499` §"Scope" and §"Write set, and its contention", read at this branch's tree. Requirement ids covered: `06` FR-364, FR-363 (for `rating_version`), `03` FR-257 limbs (1) and (2) (re-routed, no new limb). DP-S6-1 is ruled (c) by `RL-1504` item 11; its T6 is the spec text Task 1 applies.

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1499`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1390`'s roadmap row at its head.

Write set: `backend/src/app/platform/rating_versions.py` (`submit_for_review` and the verifier wrappers only), `docs/specs/06-governance.md` (FR-364, appended), `backend/tests/test_rating_version_evidence_floor.py` (new), this file, `docs/INDEX.md` (regenerated). Any other path is a stop to the lead. Not `compile.py`, `errors.py`, `packages/` or any route.

### Task list

Order and acceptance checks are `PL-1499` §"Tasks" and §"Acceptance Standard" (items 1 to 10). Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no gate yet; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-10, authoring phase.** Worktree `.claude/worktrees/sl-1390`, branch `sl-1390-wk673-s6-floor-wiring`, from `origin/main` `db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9` (`SL-1389` merged, #1260). Stamps are BST (`TZ=Europe/London date`). The gate-1 slot is held by A-2's code gate: no tests run while it does; DB tests are authored and marked OWED.

- Commit 1: `PL-1499`'s `status:` line `draft` to `active` (the 2026-10-09 13:29:49 BST ruling, item 3, `L1 (a')`), and this file.
- **Task 0, Step 1 (activation needs).** Need 2 (`SL-1389` closed): MET, #1260 `db0642c4`. Need 3 (the DP-S6-1 ruling): MET, `RL-1504` is on `origin/main`, item 11 = option (c). Need 1 (plan active): this commit. Needs 4 and 5 (lane, GO): the lead's, at the merge turn.
- **Task 0, Step 2:** `uv sync --directory <wt> --all-packages` ran.
- **Task 0, Step 3 (stored kinds outside the floor).** `git grep -n "rate_table_diffs\|gipp_check_if_enabled\|change_summary" -- examples backend/src`, at `db0642c4`: no seed policy (`examples/`) and no `backend/src` policy default names `rate_table_diffs` or `gipp_check_if_enabled`; every `change_summary` hit is the submit argument or column. No stored policy is refused by DP-S6-1 (c) from the seeds. Contention re-check: A-2 and A-3 edit `compile_rating_version`'s region of `rating_versions.py`; this slice stays inside `submit_for_review` and the verifier wrappers (hunks checked by `git diff -U0` at the merge turn).
- **Task 0, Step 4 — deltas from the plan's `137bc817` citations (merged code governs).**
  - `submit_for_review` is `rating_versions.py:337` (the plan: `:278-338`); `_regression_run_gate` `:793` (plan `:648`).
  - Slice 5's merged `submit_for_review` runs, in order, `_golden_quote_gate`, `_regression_run_gate`, `policy_for` (positional `(session, workspace_id)`), `_dislocation_baseline`, `_dislocation_gate`, `_approximation_gate`, `_structural_diff_gate`, then writes `row.evidence` once. The plan's order of the old direct calls was regression, dislocation, structural diff; the floor order is `structural_diff`, `regression_run`, `dislocation_run`, so the structural-diff blob is now stored before the other two refuse. A refusal rolls the transaction back, and the blob's `retain` with it, leaving at worst an unreferenced blob that FR-420's collector takes.
  - `structural_diff_verified` (`:1124`) and `dislocation_run_verified` (`:1130`) take a `RatingVersionRow` and read `row.evidence` after it is written; they are not callables of the plan's `verifiers` shape (`Callable[[], Awaitable[tuple[str, Any]]]`). The gates return the value to record, so the verifier wrappers wrap the gates; the two predicates stay public and unchanged (a test uses them). Each verifier returns a dict of the `row.evidence` entries it contributes (`dislocation_run` returns `dislocation_run_id` or `no_baseline`, so a first version still records its reason).
  - Signatures: `_regression_run_gate(session, *, workspace_id, row, ref, golden_quotes) -> UUID`; `_dislocation_baseline(session, *, workspace_id, row, policy) -> tuple[ArtifactRef | None, str]`; `_dislocation_gate(session, *, workspace_id, row, ref, baseline) -> UUID | None`; `_structural_diff_gate(session, *, workspace_id, row, ref, baseline, blob_store) -> str`; `_approximation_gate(session, *, workspace_id, row, ref, policy)`.
- **Task 0, Step 5 (baseline run): OWED.** The three Acceptance 6 files need Postgres and the gate-1 slot is held; the four docs checks wait for the gate slot too.

## PRs

(None yet: authoring ahead of the GO.)
