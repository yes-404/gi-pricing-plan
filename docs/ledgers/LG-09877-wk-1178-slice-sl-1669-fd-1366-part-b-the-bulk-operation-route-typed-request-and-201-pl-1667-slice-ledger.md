---
id: LG-9877
family: ledger
title: WK-1178 slice SL-1669 — FD-1366 Part B for the bulk-operation route, a discriminated request body and a typed 201 (PL-1667), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 249670fe2506ea1572d80faa1f3821edf04f194c
phase: P2
work: WK-1178
slice: SL-1669
plans: [PL-1667]
corrected_by: []
relates: [PL-1667, SL-1669, FD-1366, FD-1335, RL-1670, PL-1668, SL-1547, FR-233, FR-451]
---

# LG-9877 — WK-1178 slice SL-1669: the bulk-operation route, a typed request and a typed 201

*(Working id 9877, reserved by the lead. The id is minted at the merge turn; until then every citation of this record is by working id.)*

**GO:** the lead's from-lead entry "2026-10-12 04:53:47 BST" (GO SL-1669; ledger working id 9877). Authority for the scope: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-12 02:58:33 BST" (DP-0 = (b); the bulk-operation request and 201 only), "2026-10-12 03:06:12 BST" (DecimalStr; the breaking-caller sweep), "2026-10-12 03:07:15 BST" (the 04 :278 T-text) and "2026-10-12 03:08:30 BST" item 3 (integers stay accepted); `RL-1670` on main.
**FALLBACK (02:58:33 condition 3):** if `SL-1548` merges before this slice, the maintainer rules S5's path.
**MERGE-ACK:** not yet given.

## Tasks

Executed from `PL-1667` (Tasks 0–5), branch `sl-1669-wk1178-bulk-op-typing`, worktree `.claude/worktrees/sl-1669`, cut from `origin/main` `249670fe2506ea1572d80faa1f3821edf04f194c` (#1290).

### Task 0 — preconditions

- **Readiness** (reported to the lead before the GO): no blocking need found; file-set re-check at `249670fe`: only `docs/findings/register.md` and `docs/specs/03-rating-engine.md` moved in the write set since the plan's base `fc4401dc`, the 03 change being one added line near `:1555`, away from the §5.1 row at `:1039`.
- **Breaking-caller sweep (03:06:12 item 2)**, run verbatim at `249670fe` from the worktree root: the first command prints **13** hits and the second **1**, as the planner recorded. **None is a bulk-operation body** (no `_bulk_body(`, no post to `bulk-operation`, no `svc.bulk_operation(`, no `*Parameters(` or `*Operation(` constructor, no `BULK_OPERATION_ADAPTER` on any hit line). The hits are custom-metric and objective `cap` params (`test_custom_metrics.py:69`, `test_custom_metrics_api.py:41`, `test_custom_metrics_table.py:57,77,95`, `test_custom_objectives.py:690,706`, `packages/model-schema/tests/test_metrics.py:56`, `packages/model-schema/tests/test_objectives.py:251,252`, `packages/pricing-core/tests/test_objectives.py:83`), an expression arity table (`pricing_core/data/expressions.py:76`), a ZEN input (`test_rating_wire_order.py:234`) and a `change_note` string assertion (`test_rate_table_bulk_ops.py:156`). **Nothing converts**; the sweep is re-run at the head (Acceptance 3).
- **Python-mode dump sweep** (`created_by_operation|BulkOperation|Parameters(` over `packages/*/src`, `backend/src`): the stores are JSON-mode (`backend/src/app/platform/rate_tables.py:1439-1442`, `.model_dump(mode="json")`); `pricing_core/rate_tables/operations.py:653` builds the version from the model, and `:717`, `:752`, `:783` build the `*Parameters` from values the operations already hold. No Python-mode dump of a `*Operation` found.
- **Open PRs and rulings:** `gh` answers "HTTP 401: Bad credentials" in this shell (no token exported yet); the to-lead entries since "2026-10-12 02:58:33 BST" naming `bulk-operation`, `SL-1669`, `FD-1366` or `DecimalStr` are the three listed above, read in full.

*Premises a–k, the Red outputs, the rc table and the integer line are appended below as they are produced.*
