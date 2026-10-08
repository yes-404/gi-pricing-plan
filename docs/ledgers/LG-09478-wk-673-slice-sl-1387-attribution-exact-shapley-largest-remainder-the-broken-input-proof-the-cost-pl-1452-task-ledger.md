---
id: LG-9478
family: ledger
title: WK-673 slice SL-1387 — attribution, exact Shapley, largest remainder, the broken-input proof, the cost (PL-1452), task ledger
status: active
created: 2026-10-08
owner: executor
tree: 8b0256fdb5f000c11817838c129e1f9a4f8d8e10
phase: P2
work: WK-673
slice: SL-1387
plans: [PL-1452]
corrected_by: []
relates: [RL-1445, RL-1449, RL-1451, RL-1263, FR-266, FR-1397, FR-1398, FR-1399, WK-673]
---

# WK-673 slice SL-1387 — attribution: exact Shapley, largest remainder, the broken-input proof, the cost

Executed from `PL-1452` by `executor-s3` (sonnet). Branch `sl-1387-attribution-exact-shapley-largest-remainder`, worktree
`.claude/worktrees/sl-1387`, from `origin/main` `8b0256fdb5f000c11817838c129e1f9a4f8d8e10` (#1238, the activation). The dispatch
record is `gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1387-2026-10-08.md` (FINAL; a local file, not in the repository).
Stamps are BST (`TZ=Europe/London date`). `uv sync --all-packages` ran.

## Tasks

### Task 0 — preconditions (2026-10-08, from 11:20 BST)

**Dispatch tree.** `8b0256fd`, author date `2026-10-08T11:33:16+01:00`.

**Status at that tree** (`docs/roadmap.md`): `SL-1391` closed; `SL-1387` and `SL-1448` active; `SL-1340`, `SL-1341`, `SL-1477`
draft. No WK-1250 slice is active.

**Spec find strings** (`grep -cF -- '<string>' docs/specs/03-rating-engine.md`), each count 1:

| Anchor | Plan/ruling line | Line at `8b0256fd` |
|---|---|---|
| FR-1399 T1/T2 (the `DP-2 (c)` row end) | 192 | 192 |
| FR-1398 T3 (the `DP-1 (a), with its conditions` row end) | 191 | 191 |
| §4.6 P2 (the Slice 1 "reconciled with dislocation-run.schema.json" note) | 516 | 550 |
| §5.2 `async def attribute(baseline: RatingVersion, candidate: RatingVersion,` | 1060 | 1100 |
| §5.2 public-surface paragraph (P4) | 1124 | 1173 |
| `Error codes owned by this module:` | ~928 | 963 |
| P1 old find string (the `require_compilable` ... only-raiser entry) | 965 | **count 0** — the tail moved; re-counted at the P1 re-read (Ruling 2) |

**Moved code anchors.** `score_batch` `score.py:1135` → `1159`; `AlgorithmDiff` `rating.py:541` → `589`; `diff_algorithms` `571` → `619`;
`_score_pass` `analysis.py:144` and `compile_bundle` `compile.py:573` unchanged; `_raise_named` `compile.py:538`; `analysis.py` has no
`CodedError` or `_raise_named`. `Any` is imported at `backend/src/app/api/rating_algorithms.py:10` (the record says `:18`).
Contract: `dislocation-run.schema.json` `:88-89` ratios are `number` only, `:101` enum has five kinds, `:9` `dependentRequired` as the plan says.

**Baseline** on the untouched tree, both slots free: `pytest packages/pricing-core/tests/test_rating_dislocation.py
packages/model-schema/tests/test_dislocation.py packages/model-schema/tests/test_rating_algorithm.py -q` → `60 passed in 26.68s`, rc 0.
`python3 scripts/audit-docs.py` → rc 0, `All checks passed.`

**Standing blocks.** Task 7 waits for the decision-maker's Ruling 1 confirmation in the dispatch record. The P1 owned-codes hunk
waits for PL-1471's merge (Ruling 2).
