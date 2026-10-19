---
id: RL-1827
family: ruling
title: SL-1575 acceptance item 4: "Task 0's" means the quiet before-legs, and the decision rule is PASS, FAIL or INCONCLUSIVE on four timings
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-19   # filed 2026-10-19 under working id 8130; minted 2026-10-19 as RL-1827
owner: decision-maker
tree: 1aab7a21fc5732ac6c0ea0c47d02ac4980638220
phase: P2
work: WK-1178
slice: SL-1575
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1574, LG-1826, WK-1178]
---

# RL-1827 — SL-1575 acceptance item 4: "Task 0's" means the quiet before-legs, and the decision rule is PASS, FAIL or INCONCLUSIVE on four timings

Filed 2026-10-19 under working id 8130 (a working id until a later seat mints it). The ruling is the maintainer's (by delegation). Its source is the entry "2026-10-19 04:34:00 BST" in `~/gi-pricing-plan.local/channel/to-lead.md`.

## How this was ruled

The source is the entry "2026-10-19 04:34:00 BST" in `~/gi-pricing-plan.local/channel/to-lead.md` (that file is local, so the whole entry is quoted below, copied from the file by `sed`, not retyped). The heading of the entry (copied below) says it is an interpretation of a frozen plan and that it rides D26 as an RL. LG 8125 was minted as `LG-1826` (`docs/ledgers/LG-01826-*`, line 19 records the working id).

## Verified first, at 1aab7a21fc5732ac6c0ea0c47d02ac4980638220

- `docs/plans/PL-01574-*` lines 145-146 read: "4. **Time is measured, not asserted**: the same run's `dislocation_frame` wall time at 200,000 / is no more than Task 0's (a slower fix fails this item)." Both lines were read at this tree.
- The entry below is copied from `to-lead.md` line 27560 onward.

## Ruled

The maintainer's entry "2026-10-19 04:34:00 BST", verbatim (heading: "Maintainer: SL-1575 acceptance 3/4 — interpretation and decision rule (PL-1574 is frozen: this is an interpretation, recorded in LG 8125; it rides D26 as an RL)"):

> - **Correction accepted:** pass2 −26.59 s, not −32 s. The FINAL 12 addendum is right to fix it.
> - **Item 4's "Task 0's" (PL-1574 :145-146) = the QUIET before-legs** on 50476d3f under the v2 protocol: the 04:11 leg (1116.35 s) plus before #2. Task 0's LOADED leg (1032.39 s) is the measurement the QUIET re-run was ordered to replace; it is recorded, not compared against.
> - **Decision rule for item 4** (B1, B2 = before-legs; A1, A2 = after-legs at e73ecd65 or the final head):
>   - **PASS** if mean(A) ≤ max(B1, B2);
>   - **FAIL** ("a slower fix") if min(A) > max(B1, B2);
>   - otherwise **INCONCLUSIVE**: one more B and one more A in the same block, then re-apply.
>   - Report all four values plus the mean and the spread.
> - **Item 3 (memory, :141):** decided on VmHWM from the same block. ONE after-run suffices if it falls > ~4% below the before-legs' mean. Otherwise report the change as within noise, against the item's own wording.
> - **Order accepted:**
>   1. SL-1770's 6.2 re-gate (script for GO);
>   2. one QUIET block of B2, A1, A2, each ALONE, in one window, ABAB-adjacent order **B2 → A1 → A2** (two worktrees prepared before the first START);
>   3. then acceptance 5 (R6-size under inv-rss.sh, alone);
>   4. then the full gate on the final head.
> - **Acceptance 5:** send me the exact R6 ruling text the seat says it needs (its stamp, or "not found"). Do not proceed on a guess.

The quoted entry is the rule; this record adds no second statement of it.

## What it obliges

- `LG-1826` records the interpretation (the entry says LG 8125 does).
- `PL-1574` is **not** edited (a frozen plan, `CLAUDE.md` §12).
- Acceptance 5 is decided by RL-1830, not here.

## Acceptance — the violation that must become detectable

This ruling answers an interpretation of a plan acceptance item, with no check that can fail on a broken input. The violation to catch by reading: *Violation: an item 4 verdict compares the after-legs against Task 0's LOADED leg (1032.39 s), or reports fewer than all four values with the mean and spread.* A reviewer reads the ledger's item 4 verdict against the quoted rule.
