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
| 4, 5, 1 | (this commit) | route test: 404 for the unrouted path | `POST /api/v1/score/compare`; `test_score_compare.py` (13 passed); `03` §4.10, §5.1, §5.2, FR-262, OQ-9401 (working id) in `03` §10 and `open-questions.md`; `score-comparison` added to `audit-docs.py`'s non-markdown stamp-exemption tuple (precedent: `regression-run`); `openapi/generated.json` regenerated; `INDEX.md` regenerated. |

### Task 3 mutations (not committed)

1. `own_change=True` for every changed step → red: `assert ['s_rate', 's_total'] == ['s_rate']`
   (cascade test) and the known-limit test.
2. `"produced"` dropped from `_COMPARED` → 6 failed, 4 passed: cascade, known-limit, no-downstream
   (`assert [] == ['s_rate']`) and the three `1`/`1.0`/`True` cases.

### Plan gaps found (recorded at the lead's request)

- Task 2: `backend/tests/test_contracts.py` needs an `ONE_SIDED_SLUGS` line for `score-comparison`
  (`test_every_one_sided_slug_is_declared` failed without it). The plan says only "a scope line if
  the guard needs one".
- Task 2 Step 1 red: my first test fixture used `purpose: "quote"`, which `QuotePurpose` refuses
  (valid: `new_business`, `renewal`, `mid_term_adjustment`, `cancellation`, `what_if`). Fixed to
  `new_business`; the plan gave no fixture value.

## PRs

| PR | Branch | Title | Squash SHA on `main` |
|---|---|---|---|
| (draft, number on opening) | `p2-d-s4` | feat(rating): WK-672 Slice 4 — Quote Sandbox compare endpoint, PL-1213 | (on merge) |

### Tasks 4-5: findings against the plan

- **NFR-499 persistence test, as the plan wrote it, is vacuous.** `rating:read` is not a Service Account
  permission (FR-389 allows `score:execute` and `score:batch` only), so the caller (DP-S4-3 (i)) is a
  user, and a user has no `caller.environment`. A copied `_maybe_sample_trace` then raises inside its own
  `try`, is logged, and writes nothing. The mutation (call `_maybe_sample_trace` after each `score_one`)
  left the row-count and caplog tests green. The test now also spies on `_maybe_sample_trace` and asserts it
  is never called; under the mutation it goes red: `AssertionError: the sandbox route reached FR-259's
  trace sampling`. The caplog test stays green under the mutation (the swallowed error logs no input value),
  so plan item 7's "both red" is unreachable; the caplog test still guards a route that logs the input.
- **The engine traces expression steps only**, and `consumed` is the whole environment. The minimal
  algorithm has one expression step, so the fixtures insert a downstream expression step `s_adj`
  (`payable + 100`) to make the cascade observable through HTTP: own_change entries `["s_expr"]`, `s_adj`
  downstream with `consumed` in `changed_fields`, `unchanged == 0`; identical refs give `unchanged == 2`.
- `_insert_version` (`test_rating_version_compile.py`) gained optional `slug`/`version` keywords, backward
  compatible, so two versions can be inserted.
- Mutation B (`_naming_side` removed): the 404, 409 and 422 side-naming tests go red (6 failed).
- Red-first for the other route tests was shown by mutation, not by an absent route: only the first test
  was written before the route.
- Plan item 4's grep (`class .*Comparison|class TraceDiff|class StepChange`) prints two unrelated classes
  (`ModelComparisonRow`, `ComparisonCandidate`); none is a compare shape. The predicate is too loose.
- Docs checks: `audit-docs.py` FAILED (2): check 31 gaps 1225→9110 and 9110→9401, the working-id gap only.
