---
id: LG-9973
family: ledger
title: WK-1178 slice SL-1529 — FD-1416, one ApprovalRequest shape, generated and typed on every approval route (PL-1528 slice ledger)
status: active
created: 2026-10-10
owner: executor
tree: 31b88780aa52894624a5e08454ce2d5925d04b37
phase: P2
work: WK-1178
slice: SL-1529
plans: [PL-1528]
corrected_by: []
relates: [PL-1528, FD-1416, FD-1335, RL-1522, SL-1409, FR-9, FR-451, FR-351, FR-355, FR-357]
---

# LG-9973 — WK-1178 slice SL-1529: FD-1416, one ApprovalRequest shape

*(LG-9973 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1529` from PL-1528, base `origin/main` `31b88780aa52894624a5e08454ce2d5925d04b37`.
Times are BST (`TZ=Europe/London date`) unless marked.

**GO:** "2026-10-10 21:36:36 BST — DISPATCH GO: SL-1526 (exit demo (a)) and SL-1529 (FD-1416); FD-1573 severity; SL-1575 OFF the G2 serial path (corrects my 21:33:57 items 2 and 4)", item 4 (`to-lead.md`, a local channel file, so cited by its header): need 4 is the executor's Task 0 print, with STOP if non-zero; OP-1529-W1 ADOPTED (`scripts/audit-docs.py` joins the write set for `_CONTRACT_ARTIFACT_PATHS` only; the count comment at `:2612` is updated by a dated clause if the total changes; the SL-1430 precedent is `5351f116`, +2); `generated.json` regenerated on the merge base at merge time. Gate order, item 5 (revised): ready-first among WK-675 S4, WK-675 S3, SL-1600; then SL-1526's proving run alone, SL-1541, SL-1390, SL-1529, SL-1503.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice is `SL-1529` (`docs/roadmap.md`, `#### SL-1529`, WK-1178): *"WK-1178 fix slice — FD-1416: one ApprovalRequest shape, generated and typed on every approval route"*. Its plan is `PL-1528` (leaf plan, Tasks 0 to 7, DP-1 to DP-10 all ruled by `RL-1522`). Requirement ids: FR-9, FR-451, FR-351, FR-355, FR-357. Per Lean P2 L1 (a') the slice's one PR sets `PL-1528` and the `SL-1529` row to `active` in this branch's first commit and closes this ledger and the row at its head.

Write set: `PL-1528` §"Write set, and its contention", plus the ruled `scripts/audit-docs.py` entry (OP-1529-W1: `_CONTRACT_ARTIFACT_PATHS` only). Any other path is a STOP to the lead.

### Task list

- [x] Task 0 Steps 1 to 3 (preconditions, re-measure, data check): see the build log.
- [ ] Task 1: characterisation and Acceptance 12, 13.
- [ ] Task 2: the model (Acceptance 2, red first).
- [ ] Task 3: service and routes (Acceptance 2, 3, 4).
- [ ] Task 4: one definition (Acceptance 6; the ruled `audit-docs.py` entry).
- [ ] Task 5: the F27-class guard (Acceptance 7).
- [ ] Task 6: check `06`'s texts (Acceptance 8).
- [ ] Task 7: the gate and this ledger.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (not yet run) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-10 20:39 to 21:42 BST, Task 0.** Worktree `.claude/worktrees/sl-1529`, branch `sl-1529-fd1416-approval-request`, from `origin/main` `31b88780aa52894624a5e08454ce2d5925d04b37`.

- **Need 4, Step 3 (the data check).** Script: `/tmp/sl1529-scratch/need4.py` (outside the repository). It reads each `approval_requests` row with its decisions through a read-only `SELECT` (`docker exec gi-pricing-postgres-1 psql`), drops `environment` and `decided_at` (the current model lacks the first; Task 2 adds it as `str | None`), recomputes `approvers_recorded` from the approve decisions, and validates with `ApprovalRequest.model_validate`. Output, verbatim:

```text
gipricing: rows=12 unparseable=0
gipricing_sl-1340_fbd0c18e: rows=0 unparseable=0
gipricing_sl-1387_16b0caff: rows=0 unparseable=0
gipricing_sl-1463_2128cef0: rows=0 unparseable=0
gipricing_sl-1466_829eef9f: rows=0 unparseable=0
gipricing_sl-1536_a185ace2: rows=0 unparseable=0
gipricing_sl-1557_99fec5d8: rows=12 unparseable=0
gipricing_sl-1559_a21fe7ac: rows=76 unparseable=0
gipricing_sl-1600_08820bd9: rows=12 unparseable=0
gipricing_sl-9618_6692d8df: rows=0 unparseable=0
TOTAL unparseable=0
```

  (`gipricing_sl-1559_a21fe7ac` read 50 rows in an earlier count query, 76 at the print: another run was writing to it.) `n = 0`, so no STOP.
- **Commit 1:** `PL-1528` `status:` `draft` to `active`, the `SL-1529` row `draft` to `active`, and this file.

## PRs

(none yet)
