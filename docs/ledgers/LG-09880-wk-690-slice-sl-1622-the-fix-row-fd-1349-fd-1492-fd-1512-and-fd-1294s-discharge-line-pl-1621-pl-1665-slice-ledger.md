---
id: LG-9880
family: ledger
title: WK-690 slice SL-1622 — the fix row, FD-1349, FD-1492 and FD-1512 fixed before close and FD-1294's discharge line (PL-1621, PL-1665), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-690
slice: SL-1622
plans: [PL-1621, PL-1665]
corrected_by: []
relates: [PL-1621, PL-1665, SL-1622, FD-1294, FD-1349, FD-1492, FD-1512, FR-146, FR-157]
---

# LG-9880 — WK-690 slice SL-1622: the fix row

**GO:** the lead's `from-lead` entry "2026-10-12 05:31:21 BST" (GO; readiness; ledger working id 9880), on the maintainer's (by delegation) entries in `to-lead.md`: "2026-10-11 11:21:02 BST" item 2 (DP-W-1 (a): the fix row, off the cut ladder) and "2026-10-12 02:53:52 BST" item 3 (the PL-1665 delta approved).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1621`'s fix row, order 0 ("SL-1622 — WK-690 fix row: the three fix-before-close findings"), items F.1 to F.6, with F.1 replaced by `PL-1665`'s F.1′ (the guard is already on main at `backend/tests/test_contracts.py:2995-3013`, added by `36a9f483`, #1122; this slice writes no new guard and proves it red on BOGUS input). Requirements: `02` §3.7 FR-146 (the certificate a `failed` `pseudo_huber` blocks) and FR-157 (the metric evidence kind FD-1492 bypasses).

Branch `sl-1622-wk690-fix-row`, worktree `.claude/worktrees/sl-1622`, cut from `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`. Row: `SL-1622` in `docs/roadmap.md`.

### Task list

- **T1 — F.1′ (FD-1349).** Red-on-BOGUS proof of the existing guard, then restore. The discharge line in the register is the auditor's write at the close.
- **T2 — F.2 (FD-1492).** Test through `submit`: a custom metric whose `certificate_id` names no `metric_certificate` row is refused 409 `VALIDATION_FAILED`. Red first, then the fix in `backend/src/app/platform/metrics.py`.
- **T3 — F.3 (FD-1512).** `pseudo_huber` certifies on the default grid at delta 1, 63, 100, 1000 and 100000; gradient and hessian unchanged to 1e-12. Red first, then the fix in `packages/model-schema/src/model_schema/objectives.py`.
- **T4 — F.4, F.5.** FD-1294's dated line and the closing of each register row: the auditor's writes at the close. `python3 scripts/register-lint.py` exits 0.
- **T5 — F.6.** Both gate halves pass on the merge tree.

### Gate

Not yet run.

### Audit

Not yet run.

### Build log

- 2026-10-12 05:3x BST — activation commit: `SL-1622` and `PL-1665` set `active`; `PL-1665` added to `SL-1622`'s `relates`. Per-branch check (`PL-1621:331-333`) re-run at base `604ea084`: see the next entry.

## PRs

Not yet opened.
