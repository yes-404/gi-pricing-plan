---
id: LG-9442
family: ledger
title: WK-1178 slice SL-1462 — FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch (PL-1461), slice ledger
status: active
created: 2026-10-09
owner: executor
tree: 8af8a9b48e459c159666bd4e468d743719ade84c
phase: P2
work: WK-1178
slice: SL-1462
plans: [PL-1461]
corrected_by: []
relates: [PL-1461, RL-1457, FD-1456, RL-1445, RL-1263, FR-20, FR-191, FR-237, FR-255, FR-351, FR-355, FR-363, WK-1178]
---

# LG-9442 — WK-1178 slice SL-1462: FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-09 15:22:26 BST — USER: 'worrying only one executor runs'. FILL THE VM NOW …", items 1–4, in `to-lead.md`, a local file): code and tests are written on a branch from S4's pushed head `8af8a9b4`; only small tests run (one file, no database), nothing merges before the GO, the full gate and the MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `SL-1462` in `docs/roadmap.md` (WK-1178, Option A, A-1): *"FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch"*. Its scope is `PL-1461` §"Scope" (requirement coverage table) and §"Write set, and its contention", read at this branch's tree. Requirement ids covered: FR-20, FR-190, FR-191, FR-237, FR-255, FR-351, FR-355, FR-363. The ruling is `RL-1457` (DP-1 (a), DP-2 (a), DP-3 (b), and T1, the `06` §4.2 note).

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1461`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1462`'s roadmap row at its head.

Write set: `PL-1461` §"Write set" only. Any other path is a stop to the lead.

**Serial with S4 on the resolver.** `PL-1461` was written against `_Resolver.resolve`. This branch is cut from S4's head, where S4's Task 3 has already lifted the class to module-level `WorkspaceResolver` (`rating_versions.py`). The peril branch goes into that class, re-anchored by symbol (Q1 (a) of planner-g2's GO request).

### Task list

Order and acceptance checks are `PL-1461` §"Tasks" and §"Acceptance Standard" (items 1 to 14). Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run while S3's Task 7 holds gate-1; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-09, authoring phase.** Worktree `.claude/worktrees/sl-1462`, branch `sl-1462-a1-peril-approval`, from `8af8a9b48e459c159666bd4e468d743719ade84c` (S4's pushed head). Stamps are BST (`TZ=Europe/London date`).

- Commit 1: `PL-1461`'s `status:` line `draft` to `active` (the Q1 ruling, `L1 (a')`), and this file.
- **Red-first proof is OWED for every database-backed test.** The tests of items 1 to 9 need Postgres (`GIP_TEST_DATABASE_URL`), which the small-test rule bars; each is written before its code, and its red (by cause) is shown at the first gate-slot window. Item 10 (`packages/pricing-core/tests/test_rating_runtime.py`) needs no database and is run red then green here.
- **Tasks 1 and 2 (PL-1461 Tasks 1, 2), 2026-10-09.** `backend/tests/test_api_approvals.py`: `_AFTER["peril_structure"]` is `_moves("approved", "review", "reconciled")` and `_MOVE_ACTION` gains `peril_structure`. New module `backend/tests/test_peril_structure_approval.py`: items 4 (supersession), 5 (unapproved component refused, control approved), 13 (parametrised over every `ModelStatus` member, plus the accepted-set-inside-the-enum test), an `excess_model` case, and item 6 (`reconciled`/`review` refused `PIN_NOT_APPROVED`; approved structure compiles, Bundle `resolved_payloads[ref]["status"] == "approved"`). `backend/tests/test_rating_version_create_pins.py`: item 7, PL-1429's Acceptance 7 test renamed `test_a_peril_structure_pin_is_stored_and_compile_names_the_missing_structure`, asserting the ref in the message and not "has no backend table yet". **Red for all of these is OWED**: every one needs Postgres, which the small-test rule bars. Each is shown red by cause at the first gate-slot window, by running the file against the tree with Tasks 3 and 4's code absent.
- **Task 3 (PL-1461 Task 3), 2026-10-09.** `backend/src/app/platform/perils.py`: `apply_approval_decision`, `_target_status`, `_require_approved_components`, `_supersede_earlier_versions`, `APPROVED_COMPONENT_STATUSES` (`frozenset({ModelStatus.APPROVED})`); `api/approvals.py`: one call in `_carry_to_the_artifact`'s `approval_decision()` block, docstring corrected. **Implementation deltas from the plan's text (no spec change):** (1) `_target_status` also maps `WITHDRAWN → RECONCILED`, as every sibling does and as `withdraw_request` also calls the carry (`api/approvals.py`); without it a withdrawn request strands the structure in `review`. (2) `_require_approved_components` reads the stored `perils` through `PerilComponent.model_validate`, not `to_structure(row)`, so a stub `reconciliation` (as `test_api_approvals`'s table fixture inserts) cannot break the check; the `excess_model` is read from `large_loss`.
- **Task 4 (PL-1461 Task 4), 2026-10-09.** The peril branch is in `WorkspaceResolver.resolve` (S4's lifted `_Resolver`), before the final raise; `perils.load_structure_by_ref` added; the final raise now says the compile resolver has no branch for the artifact type (item 8). **Item 10 red then green (small test, no database):** `flock -w 300 /tmp/slots/small-test -c "nice -n 19 timeout 150 uv run --directory <wt> pytest -q packages/pricing-core/tests/test_rating_runtime.py -k peril_structure_model_call"`. RED, 1 failed in 10.60s, at `runtime.py:589`: `KeyError: 'fit_result'` (the cause the plan names). `_model_call_handler` now returns `_model_call_failure(...)` naming the ref and A-3 before the `payload["fit_result"]` read. GREEN: the same file, `pytest -q packages/pricing-core/tests/test_rating_runtime.py`, 12 passed in 3.47s.
- **Task 5 (PL-1461 Task 5), 2026-10-09.** RL-1457 T1 applied to `docs/specs/06-governance.md` §4.2's floor note, byte for byte except `<date>` = 2026-10-09 and `<RL>` = RL-1457. The find string counted 1 before the edit (`grep -cF`); after it, `git grep -n 'per-peril approvals half is unqueryable' -- docs/specs` prints nothing (rc 1): Acceptance 14.
- **Owed after Task 7:** red-by-cause for items 1, 4, 5, 6, 7, 13 (needs the database); `mypy`, `lint-imports`, `audit-docs`, the full gate. `model-schema`'s `DEFAULT_POLICY` comment block (`approvals.py`, "enforced nowhere") also describes the old state; it is outside the write set, so it is left and reported to the lead.

## PRs
