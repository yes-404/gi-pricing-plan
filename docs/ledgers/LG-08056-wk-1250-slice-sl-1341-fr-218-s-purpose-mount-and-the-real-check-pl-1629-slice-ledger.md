---
id: LG-8056
family: ledger
title: WK-1250 slice SL-1341 — FR-218's purpose mount and the real check (retires RL-1242), PL-1629 slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-16
owner: executor
tree: 658c4cd67d8cab11a02be35a4ad100ab2eacb26a
phase: P2
work: WK-1250
slice: SL-1341
plans: [PL-1629]
corrected_by: []
relates: [PL-1629, RL-1344, RL-1628, RL-1242, RL-1571, LG-1588, SL-1341, FR-218, FR-212, FR-217, FR-239]
---

# LG 8056 — SL-1341: FR-218's purpose mount and the real check

Executed by `executor-1341b` (sonnet, medium) from **PL-1629** (`active`), binding **RL-1344** §2, §3, §4 (Slice 3 bullet) and
**RL-1628** (T1 to T3, "What it obliges"). Branch `sl-1341-wk1250-s3-purpose-mount`, worktree `.claude/worktrees/sl-1341`,
base `origin/main` `0877e6e7` merged at `c1f7c447`.
**GO:** the maintainer (by delegation), `to-lead.md` "2026-10-16 09:35:13 BST"; the lead's request in
`from-lead-2026-10-09.md`, entry "SL-1341 … GO-READY". That entry is the dispatch record (need 3).
**MERGE-ACK:** at the lead's merge turn (not yet).

## Tasks

| Task | Commit | State |
|---|---|---|
| 1 spec: RL-1628 T1, T2, T3 (+ the `CompiledBundle` field note in `03` §5.x) | `aa482243` | done; audit-docs rc 0 |
| 2 `SubGraphRef.purposes`, FR-212 per purpose, R1 | feat(model-schema) | done |
| 3 `inline_mounts(purpose=)`, `Bundle.purpose_graphs`, `bundle_hash`, `load_bundle` per purpose | feat(pricing-core) | done |
| 4 the real check and one selector for every algorithm/decision read; interim tests rewritten | feat(pricing-core) | done |
| 5 FR-218 strike; `RL-1242` `status: retired` (status line only; RL-1628 names the writer) | `658c4cd6` | done |
| 6 full gate; backend route tests run | — | **not done** (gate barred; route tests need the DB) |

**Beyond the plan's text.** `AlgorithmSubGraphChange.purposes_changed` (and its change-summary wording): without it a change
to `purposes` alone was not in `diff_algorithms`, failing RL-1344 acceptance 5. `backend/src/app/api/score.py`'s compare route
reads the purpose's algorithm for its trace diff. `MountPurpose` is stated once beside `QuotePurpose`. The hand-authored
`rating-algorithm.schema.json` carries `purposes`; `docs/contracts/openapi/generated.json` regenerated.

## Stale cites (plan/ruling cite → at base `c1f7c447`)

`docs/specs/03-rating-engine.md`: RL-1628 T1 find `:340` → `:341`; T1 anchor `:349` → `:350`; T2 anchor `:943` → `:980`;
T3 anchor `:1154` → `:1195`; FR-218 `:87` unchanged. Each anchor counted exactly once at the base.
`packages/pricing-core/src/pricing_core/rating/score.py` (changed by SL-1566, `cad75a7e`):
`_check_purpose_mount` `:391` → `:392`; its calls `:941` → `:942` (`score_one` `:919` → `:920`) and `:1108` → `:1134`
(`_score_context_sync` `:1090` → `:1116`); `build_scoring_result` `:873` → `:874`; `_score_batch_row` `:1128` → `:1175`;
the reads of `bundle.algorithm`/`decision`: `score_one` `:939`, `:962`; `_score_context_sync` `:1132`, `:1143`;
`_score_batch_row` `:1191`. Not re-measured one by one: the `runtime.py`, `compile.py`, `inline.py` and `rating.py` cites.

## Proofs run (no full gate; run-small, ≤3 files each, before GATE START)

- model-schema `test_rating_algorithm.py` + `backend/tests/test_contracts.py` + `test_rating_purpose_mount.py`: 230 passed, 2 skipped.
- `test_rating_score.py` + `test_rating_compile_bundle.py` + `test_rating_inline.py`: 100 passed.
- `test_rating_runtime.py` + `test_quote_input_raise_sites.py` + `test_rating_shadowed_inputs.py`: 45 passed.
- `test_rating_wire_order.py` + `test_rating_mounted_model_call.py`: 17 passed. `test_input_free_raises.py` + `test_rating_algorithm_draft.py`: 8 passed.
- ruff and mypy on the touched files: rc 0. `generate-contracts.py --check`: rc 0. `audit-docs`, `doc-index`, `req-coverage`: rc 0.
- Acceptance 5 (not bypassable): `test_removing_the_real_check_would_be_caught` and `test_the_purpose_guard_would_be_caught_if_removed`
  patch `_check_purpose_mount` out and see the MTA quote priced; the patch is in the test, never committed.
- Acceptance 7, existing hashes: `test_rating_wire_order.py` and `test_rating_shadowed_inputs.py` pass unmodified; the re-run against
  WK-675 S5 (`SL-1547`) belongs to whichever slice merges second.

## Verdicts

FR-218's authoring half: delivered (the purpose mount, FR-212 per purpose, the real check, the interim rule's retirement); the route
tests (`backend/tests/test_score_purpose_mount.py`) are written and **delivered but untested** until a DB window runs them.

## PRs

One PR for this slice (L1 (a')): opened and merged by the lead; not yet opened.
