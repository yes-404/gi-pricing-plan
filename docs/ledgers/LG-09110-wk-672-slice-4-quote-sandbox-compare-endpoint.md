---
id: LG-9110
family: ledger
title: WK-672 Slice 4 — Quote Sandbox compare endpoint (FR-262 backend limb)
status: active
created: 2026-09-29
owner: executor
tree: b4aa909d43f347091e3ee239fbc72ab4c5ca4491
phase: P2
work: WK-672
plans: [PL-1213]
corrected_by: []
relates: [RL-1172, PL-930, PL-1205, LG-1225]
---

# LG-9110 — WK-672 Slice 4 — Quote Sandbox compare endpoint (FR-262 backend limb)

Executed from `PL-1213` under `RL-1172` §5 and the deputy's DP-S4-1 to DP-S4-5 (entry of
2026-09-28 21:08:30 BST) and its F5 amendment (21:10:34 BST). Branch `p2-d-s4`, from `b4aa909d`
(#886's MERGE-ACKed head, S3). `LG-9110` is a **working id** given by the lead; it is minted at
the PR's queue turn.

## Task 0 — adjusted by the maintainer's instruction (to-lead.md ~12:01 BST 2026-09-29)

- **Step 1** satisfied by branching from #886's ACKed head `b4aa909d`, which contains S3's code.
  Symbol check: `packages/pricing-core/src/pricing_core/rating/replay.py` exists in the tree.
  The `origin/main` subject-line check comes after #886 merges.
- **Step 2** the decision entry is in `channel/to-lead.md` (2026-09-28 21:08:30 BST, line 9327;
  the F5 entry at 21:10:34 BST, line 9342). Both read.
- **Step 3** `origin/main` is **not** merged now. The lead says when #886 has squash-merged; then
  a plain merge, quoted conflict-free, and the plan's literals re-read.
- Literals re-read at `b4aa909d`, no drift: `score.py:110` `ScoreExecuteDep`, `:114`
  `_required_ref`, `:206` `_compiled_for`, `:241` `_as_platform_error`; `03` has no §4.10.
- Test database `gipricing_executor-s4_18004fad` (created from the template, `alembic upgrade head` rc 0).

## Tasks

| Task | Commit | Red cause | What was done |
|---|---|---|---|
| 2 | `92a281c0` | `ImportError: cannot import name 'ScoreCompareRequest'` | `StepChange`, `TraceDiff`, `ScoreCompareRequest`, `ScoreComparison`; `score-comparison` generated; `ONE_SIDED_SLUGS` line in `test_contracts.py` (not in the plan). |
| 3 | (this commit) | `ModuleNotFoundError: pricing_core.rating.trace_diff` | `diff_traces` and `test_trace_diff.py` (10 passed). |

### Task 3 mutations (not committed)

1. `own_change=True` for every changed step → red: `assert ['s_rate', 's_total'] == ['s_rate']`
   (cascade test) and the known-limit test.
2. `"produced"` dropped from `_COMPARED` → 6 failed, 4 passed: cascade, known-limit, no-downstream
   (`assert [] == ['s_rate']`) and the three `1`/`1.0`/`True` cases.
