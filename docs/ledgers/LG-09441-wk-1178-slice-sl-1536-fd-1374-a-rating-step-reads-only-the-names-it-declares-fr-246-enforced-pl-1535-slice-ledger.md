---
id: LG-9441
family: ledger
title: WK-1178 slice SL-1536 — FD-1374, a rating step reads only the names it declares, FR-246 enforced (PL-1535), slice ledger
status: active
created: 2026-10-09
owner: executor
tree: d471a43bdc4ed123258a7398bbcf30c62605aa27
phase: P2
work: WK-1178
slice: SL-1536
plans: [PL-1535]
corrected_by: []
relates: [PL-1535, PL-1520, RL-1519, FD-1374, FD-1534, FR-246, FR-212, WK-1178]
---

# LG-9441 — WK-1178 slice SL-1536: FD-1374, FR-246 enforced

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-09 13:17:43 BST — USER: parallel …" item 2, in `to-lead.md`, a local file): code and tests are written on a branch from `origin/main` `d471a43bdc4ed123258a7398bbcf30c62605aa27`; no heavy run while S3's Task 7 holds gate-1; nothing merges before the GO and the gate.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `PL-1535` (single-row Work plan for WK-1178), slice `SL-1536`: *"WK-1178 fix slice — FD-1374: a rating step reads only the names it declares (FR-246 enforced)"*. Its tasks are `PL-1520` Task 1A, Steps 1–8, as ruled by `RL-1519` (DP-F35-1 (ii) (a)/(a)/(a), (iii-a) (b), (iii-b) (b)), with the plan's deviations D1 (tokenizer, no Spike S1), D2 (no Task 1 Step 6) and D3. Requirement ids: FR-246, FR-212 (fixtures gain producers); register FD-1374.

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1535`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1536`'s roadmap row at its head.

Write set: `PL-1535` §Tasks / `PL-1520` Task 1A "Files" only. **FD-1534's remedy (a)** (the extractor in `packages/pricing-core/tests/test_rating_committed_strings.py` skips an empty literal) is the lead's 2026-10-09 brief item for this slice, but that path is not in that write set; it waits on a ruling (build log).

### Task list

PL-1520 Task 1A, by step (acceptance checks are PL-1535 Acceptance Standard items 1 to 6):
- [x] Step 1: `test_rating_declared_reads.py` (6 tests), commit `3af2475f`. **Red proof owed** (Step 2: expected `ModuleNotFoundError: No module named 'pricing_core.rating.references'` at collection, then per Step 3 the two refusal tests and the two example tests red by their causes).
- [x] Step 3: `pricing_core/rating/references.py` (deviation D4 below).
- [x] Step 4: `_check_declared_reads` appended to `compile.py`, last entry of `ALGORITHM_CHECKS`; commit `aeeb39ad` (Steps 3 and 4 together).
- [x] Step 5: four fixtures fixed, three `input` steps added in `test_rating_score.py`, one in the model-schema fixture (whose `input_contract` gains `min_premium_minor`; its step-count assert 9 to 10); commit `cb945b84` and a style commit.
- [ ] Step 6, 7: **owed** (need pytest; gate slot for Step 7).
- [x] Step 8 (authoring half): RL-1519 T1 to T5 applied: `03` (FR-246 row, the 4.1 example fence, its Invariants note, the owned-code row) and `errors.py`; commit `497bd69d`. T2's sha256 (with final newline) printed `6a35964d410f9b6c`, matching RL-1519. Audit-docs, FD-1374's predicate, the release note in the squash body, `git diff` of `03` beside the RL text: **owed**.
- [x] FD-1534, both limbs, authored in `test_rating_committed_strings.py`, commit below (write-set addition ruled, build log). **Red proofs and the controls' run at the test file: owed.** FD-1534 is closed (status, register row) only if both limbs are discharged by that run.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run while S3's Task 7 holds gate-1) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-09, authoring phase.** Worktree `.claude/worktrees/sl-1536`, branch `sl-1536-fd1374-dp-f35-1`, from `origin/main` `d471a43bdc4ed123258a7398bbcf30c62605aa27`.

- Commit 1: `PL-1535`'s `status:` line `draft` to `active`, and this file.
- **Deviation D4 (this slice, not PL-1535's D1 to D3).** `references.py` takes its evaluated field names from `authored.EXPRESSION_FIELDS` (FD-1317's one registry, which landed after PL-1520 was written) rather than repeating a hard-coded field list; it skips a `None` clamp bound. `referenced_names`' contract and the plan's tests are unchanged. D1 (the tokenizer, no Spike S1) applies as PL-1535 says.
- **RATING_ERROR_CODES placement.** RL-1519 T5 inserts the code immediately after `"LADDER_CLAMP_UNPLACEABLE",`; applied so, byte for byte. The lead's brief said tail; the ruling wins and the insertion site does not touch the tail S4 appends to (`ATTRIBUTION_RECONCILIATION_FAILED`).
- **Light smoke, no pytest (not the red/green proof).** With `PYTHONPATH` on the tests dir, the six test functions called directly all passed, `validate_algorithm` over `test_rating_score._algorithm_payload`, `test_rating_compile.valid_algorithm`, `test_rating_compile_bundle.valid_algorithm_payload` and the model-schema fixture gave 0 FR-246 issues.
- **STOP, FD-1534's remedy (a).** It edits `packages/pricing-core/tests/test_rating_committed_strings.py`, which is not in `PL-1535` / Task 1A's write set. Reported to the lead 2026-10-09; RULED the same day in `to-lead.md`, entry headed "2026-10-09 13:48:15 BST — RULING: PL-1535 write set + scope. (1) YES, test_rating_committed_strings.py joins. (2) WIDEN: fix the _KEY limb too, in this slice": the file joins the write set for FD-1534 only, and the scope is widened to both limbs.
- **FD-1534 authored (2026-10-09).** Limb (a): `_text` picks the double-quoted group by `is not None` and skips an empty literal (a blank placeholder), at both sites. Limb `_KEY`: the literal must be the whole value (a lookahead for a delimiter, comment or line end), so `expr = " * ".join(...)`, whose literal is a method receiver, is no longer read as the expression ` * `. A first design that dropped bare `name = "..."` was rejected after a light diff of old against new extraction over the tracked tree showed it would lose two real expressions (`test_rating_pin_membership.py:234`, `:240`); the shipped design lost none (the only two lines it no longer reads are this file's own comment and test text). Two new tests are the positive controls per limb (empty literal skipped, a real literal beside it caught; a non-whole-value literal skipped, whole-value forms caught). Light smoke (functions called directly, no pytest) passed. S3's rename `expr` to `prod` (`5647779f`, `scripts/measure-attribution-cost.py`) is now unnecessary and is not reverted (S3's write set).
- **RATING_ERROR_CODES placement.** RL-1519 T5, at `backend/src/app/errors.py` right after `"LADDER_CLAMP_UNPLACEABLE",`; S4 appends `ATTRIBUTION_RECONCILIATION_FAILED` at the tail, so there is no textual overlap. At the merge turn, after S4 and A-1 merge, this slice still reports `RATING_ERROR_CODES` with both sides kept (Q3).
- **Alembic.** This slice adds no migration.

## PRs

(none yet)
