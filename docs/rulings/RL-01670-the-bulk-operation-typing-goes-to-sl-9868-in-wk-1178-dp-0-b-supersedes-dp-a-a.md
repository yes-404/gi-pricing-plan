---
id: RL-1670
family: ruling
title: The bulk-operation typing goes to SL-1669 in WK-1178 — DP-0 (b) supersedes DP-A (a) of the 2026-10-11 10:55:02 entry
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-12
owner: maintainer               # recorded on the maintainer's behalf (by delegation), as RL-1612 is (§1.6 RL row)
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [WK-1178, WK-675, FD-1366, RL-1613]
---

# RL-1670 — one supersession, written down outside chat

*(Minted 2026-10-12 as RL-1670 from working id 9870, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

## Ruled

The maintainer's (by delegation) entry "2026-10-12 02:58:33 BST — DP-0: (b), stated as SUPERSEDING my 2026-10-11 10:55:02 item 2 (DP-A (a)); with a fallback trigger" (`to-lead.md`, a local channel file, cited by header) says, verbatim: *"(b) supersedes 10:55:02 item 2."* It **supersedes** item 2 of the entry "2026-10-11 10:55:02 BST — S5 (SL-1547) not ready: (1) the OQ-1223 decision-maker takes the NEXT non-build seat, before the sweep; (2) DP-A = (a), S5 types its own bulk-operation route" (same file), whose item 2 said, verbatim: *"DP-A: (a) ADOPTED. S5 types POST bulk-operation itself, in its FIRST commit, with the existing BulkOperationBase (model_schema/rating.py:1179)."*

The bulk-operation request and 201 typing now goes to the `WK-1178` slice `SL-1669` (plan `PL-1667`), not to S5 (`SL-1547`). `PL-1667`'s Context names item 2 of the 10:55:02 entry as superseded by the 02:58:33 entry.

## What it obliges

- **PL-1667** cuts `SL-1669` (WK-1178): the bulk-operation request and 201 only. Its Context names item 2 of the 10:55:02 entry as superseded by the 02:58:33 entry, and strikes nothing, because the plan never carried DP-A.
- **PL-1668**, the delta to `PL-1546` row 1 (`SL-1547`), names `SL-1669` as an activation need, with `RL-1613`'s scope. At the mint, `SL-1547`'s need line gets `SL-1669`'s minted id.
- **Fallback trigger** (the 02:58:33 entry): if `SL-1669` is not merged when S6 (`SL-1548`) merges, it is brought to the maintainer; S5 then either waits or reverts to DP-A (a), as the maintainer rules at that time.
- Done at the D13 mint: this record is `RL-1670`, and its citations of `SL-1669`, `PL-1667` and `PL-1668` are re-pointed.

## Acceptance — the violation that must become detectable

The violation: **S5 (`SL-1547`) typing `POST bulk-operation` in its own commits while `SL-1669` is also planned, or `SL-1547` activating without `SL-1669` merged and no fallback ruling.**

- *Violation: SL-1547 active with `SL-1669` unmerged.* Held by `SL-1547`'s activation need (PL-1668), which the lead's dispatch check reads before a GO.
- *Violation: two slices typing the same route.* Held at the route's typing guard (`FD-1366` Part A, `PL-1364`): the untyped-route list names `bulk-operation` until `SL-1669` removes it, and a second typing of the route is a duplicate model, which "nobody hand-writes a shape that already exists" (`CLAUDE.md` §2) forbids.
