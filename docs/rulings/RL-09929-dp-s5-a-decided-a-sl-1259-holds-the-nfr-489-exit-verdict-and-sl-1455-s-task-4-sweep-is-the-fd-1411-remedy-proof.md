---
id: RL-9929
family: ruling
title: DP-S5-a decided (a) — WK-674 S5 (SL-1259) holds P2's NFR-489 exit verdict on the exit tree; SL-1455's Task 4 sweep is the FD-1411 remedy proof only; the 2026-10-10 21:38:39 BST M1/M3 wording corrected; the dedicated VM's run list covers both
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-11
owner: decision-maker           # a technical decision-point ruling (§1.6 RL row); the maintainer ruled it, this records it
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1454, SL-1455, SL-1259, PL-1237, PL-1537, FD-1411, NFR-489, RL-9926]
---

# RL-9929 — DP-S5-a decided (a): SL-1259 holds the NFR-489 exit verdict; SL-1455's sweep is the FD-1411 remedy proof

*Disclosure: drafted under working id 9929, reserved by the lead (team-lead) on 2026-10-11
(`~/gi-pricing-plan.local/handover/brief-dm-lanec-2026-10-11.md`, "Reserved working ids").
The id is minted in a later docs batch. When it is minted, the working id in this record is
replaced by the minted id.*

## How this was ruled

- **The ruling is not this record's.** It is the maintainer's (by delegation), in the entry
  of `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-11 11:02:35 BST — DP-S5-a
  RULED (a): SL-1259 (WK-674 S5) holds the NFR-489 EXIT verdict; SL-1455's Task 4 is the
  FD-1411 remedy proof. CORRECTION of my 2026-10-10 21:38:39 M1/M3 wording"
  (`to-lead.md:21989`–`21998`). That file is local, so a repository reader cannot open it
  (RFC-777). The entry is therefore quoted whole below. This record decides nothing beyond it.
- **The decision point.** DP-S5-a was raised by the planner for WK-674 S4/S5
  (`~/gi-pricing-plan.local/handover/readiness-wk674-s4s5-2026-10-11.md` §4): who measures
  NFR-489 for P2's exit, S5 on the S4 path or SL-1455's Task 4 sweep. The maintainer routed
  it to the decision-maker in the entry "2026-10-11 10:55:55 BST — WK-674 S4/S5 readiness:
  PL 9921 (one delta, L5) ACCEPTED; DP-S5-a → the same DM seat after OQ-1223; …", item 2.
  The options memo is `~/gi-pricing-plan.local/handover/dm-dps5a-2026-10-11.md` (seat
  `dm-lanec`). Both files are local, and their substance is restated in "Verified first".
- **DP-S5-b is not ruled here.** The user decided it in the entry "2026-10-11 10:57:16 BST —
  USER DECISION, DP-S5-b: 'Temporary dedicated VM' for the ALONE NFR measurements …": a
  short-lived second VM, used only for the solo speed tests and then deleted, which is
  roadmap :569–570's discharge event "a dedicated host available". Item 3 of the ruling below
  sets that VM's run list. The spend approval stays the user's.

## Ruled

**The maintainer's decision, by delegation, quoted whole** (`to-lead.md:21989`–`21998`):

> ## 2026-10-11 11:02:35 BST — DP-S5-a RULED (a): SL-1259 (WK-674 S5) holds the NFR-489 EXIT verdict; SL-1455's Task 4 is the FD-1411 remedy proof. CORRECTION of my 2026-10-10 21:38:39 M1/M3 wording
> Read before ruling: PL-1454 @99f22479 :62 ("the NFR-489 verdict on the exit tree stays SL-1259's"), :146, :199 ("the verdict is carried per G4 and on the exit tree stays SL-1259's"), :268 (SL-1259 will edit score.py after SL-1455), :550 ("FD-1411's remedy event is met; its own discharge also needs SL-1259's NFR-489 verdict"). The memo handover/dm-dps5a-2026-10-11.md.
> 1. (a) ADOPTED: it is the frozen plans' own allocation. (b) is rejected: one process is not S4's replicas, and SL-1455 precedes SL-1259's bundle-path edits, so it cannot read the exit tree. (c) is rejected: two competing verdicts. PL 9921 is amended to (a) before its mint.
> 2. CORRECTION (mine): my 21:38:39 M1 said SL-1455's condition was the NFR-489 pass "on the exit tree", and M3 had WK-674 S3 merge first "so the sweep measures the exit-tree path". Both overreached PL-1454. Corrected:
>    - SL-1455's Acceptance 2 bar stands (both arms in budget at 25/50/100/200 rps, ×3 interleaved, issued = offered, 0 errors), as the FD-1411 REMEDY proof.
>    - The P2 exit's "meeting NFR-489" is SL-1259's verdict on the exit tree, with replicas per DP-3 (21:38:39 M2).
>    - M3's order (WK-674 S3 before the sweep) stays, because the sweep then includes the limiter. It is no longer justified as "the exit tree".
>    - An SL-1455 pass followed by an SL-1259 miss is a finding against S5's changes.
> 3. DEDICATED VM: its run list = SL-1455 Task 4 (remedy proof) plus SL-1259's verdicts (NFR-489 exit and the other S5 NFRs, NFR-502 among them). The hours cover both. The VM is STOPPED between the two sessions (vCPU/RAM billing stops; the disk keeps the state), not left up, and DELETED after S5's verdict, with deletion verified. The pack is amended to say so.
> 4. RL 9929 (the decision-maker's) records this ruling, cites PL-1454 :62/:199/:550 and this entry, and lists the correction.

## Verified first, at 99f22479a20e7fa64f8b6654e0d371c595b1e35a

`origin/main` was re-fetched before this record was written and was still `99f22479`.

| Premise | Where | What the source says |
|---|---|---|
| The requirement | `03-rating-engine.md:1466`, NFR-489 | "Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call (NFR-454). Without a GBM call, p99 < 15 ms. (Clarified 2026-10-05, OQ-1453: the ceiling governs untraced requests …)" |
| P2's exit binds it | `roadmap.md:3012`, §12 row 2 | "`WF-699` end to end, plus `WF-701` phases A–D, meeting NFR-489". |
| SL-1455 measures one replica, and the exit verdict is SL-1259's | `PL-1454` (`docs/plans/PL-01454-…-leaf-plan.md`) :58–62 | "`POST /api/v1/score` meets NFR-489 on one replica … This discharges the remedy half of FD-1411 (HIGH); the NFR-489 verdict on the exit tree stays SL-1259's." |
| The same allocation, restated | `PL-1454` :146; :199 | "The NFR-489 verdict stays carried per G4 and is SL-1259's on the exit tree"; "the verdict is carried per G4 and on the exit tree stays SL-1259's". |
| SL-1455 precedes SL-1259's edits to the same path | `PL-1454` :268 | the `backend/src/app/api/score.py` row: "**SL-1259** (WK-674 S5, `draft`) will edit the bundle path for FR-268 … this slice precedes SL-1259". |
| FD-1411's discharge needs both | `PL-1454` :550–552, Hand-off item 2 | "On merge, FD-1411's remedy event is met; its own discharge also needs SL-1259's NFR-489 verdict on the exit tree, or the maintainer amending or carrying NFR-489 by a dated line". |
| SL-1455's sweep form | `PL-1454` :339 (DP-3); :512–524 (Task 4) | DP-3: "(a) one process, as the harness runs today … (a) is the basis of Acceptance 2". Task 4: the head un-instrumented, R in 25, 50, 100, 200, three invocations each, interleaved. |
| A DP-3 ruling reaches SL-1259 | `PL-1454` :554–555, Hand-off item 3 | "If DP-3 (b) or DP-5 is ruled, the spec text and the measurement basis change for SL-1259 too". |
| S4 builds the replica path, and S5 reuses it | `PL-1237` :874; :895–896 | "The compose `api` service, runnable as n replicas behind a stated load-balancing …"; "A load harness that drives `/score` at 200 rps against n ∈ {2, 4, 8} replicas … Slice 5 reuses it." |
| S5 measures NFR-489 | `PL-1237` :913 (Task 5 heading); :929 | "Task 5 — Slice 5: atomic switchover, rollback and the measurements (FR-268, FR-269, NFR-494, NFR-489, NFR-502; …)"; "NFR-489 and NFR-502 on the dedicated host, more than one pass". |
| The fallback the VM discharges | `roadmap.md:569–570` | "These verdicts are **measured, diagnostic** on the shared VM; the verdict is **carried**, owner the maintainer, discharge event **a dedicated host available**. No near-bound pass or fail is claimed from the shared VM." |

## What it obliges

This record changes no plan and no requirement. `PL-1454`, `PL-1237` and `PL-1537` are frozen,
and the allocation it records is `PL-1454`'s own.

1. **The NFR-489 exit verdict is SL-1259's** (WK-674 S5). It is measured on the exit tree
   (after S5's own `/score` changes), on the S4 replica path and harness (n replicas, both
   arms, untraced per OQ-1453), on the dedicated VM, with "per replica" as `PL-1454` DP-3
   rules it. SL-1259's `LG-` records the verdict and cites this record.
2. **SL-1455's Task 4 table is the FD-1411 remedy proof**, against its Acceptance 2 bar (both
   arms in budget at 25, 50, 100 and 200 rps, ×3 interleaved, issued = offered, 0 errors). It is
   never written as P2's NFR-489 exit verdict. SL-1455's `LG-` cites this record.
3. **A conflict is a finding, not a tie-break.** An SL-1455 pass followed by an SL-1259 miss
   is raised as an `FD-` against S5's changes to the path.
4. **The 2026-10-10 21:38:39 BST wording is corrected** (ruling item 2):
   - **M1:** SL-1455's condition is its Acceptance 2 bar as the remedy proof, **not** "the
     NFR-489 pass on the exit tree".
   - **M3:** WK-674 S3 still merges before the sweep, so the sweep includes the Redis limiter.
     The justification "so the sweep measures the exit-tree path" is withdrawn.
   - **Living text that carries the old wording.** At this record's tree, no file on `main`
     states it. The D10 docs batch (PR #1274, branch `docs-d10-2026-10-11` @`1173a927`, not
     merged when this record was written) adds a dated line to the SL-1455 row
     (`roadmap.md:1912` on that branch) ending *"The exit condition is NFR-489's own: p99 in
     budget in both arms at 200 rps per replica over HTTP on the exit tree, under
     Acceptance 2's protocol."* That sentence restates the corrected M1. It is amended
     before D10's mint if D10 has not merged; otherwise a dated line on the SL-1455 row,
     citing this record, corrects it. That row is not edited in this record's commit.
5. **PL 9921** (planner-wk674's WK-674 S4+S5 Work-plan delta, draft on branch
   `pl-wk674-s4s5-2026-10-11`) is amended from (c) to (a) before its mint (ruling item 1). It
   cites this record.
6. **The dedicated VM's run list** is SL-1455 Task 4 (the remedy proof) plus SL-1259's measured
   verdicts (NFR-489's exit verdict and the other S5 NFRs, NFR-502 among them). The expected
   hours in the spend pack cover both. The VM is stopped between the two sessions and deleted
   after S5's verdict, with the deletion verified (ruling item 3). Its creation stays behind
   the user's spend approval (10:57:16 BST, item 2).

## Acceptance — the violation that must become detectable

The violation: SL-1455's table is recorded as P2's NFR-489 verdict; P2's exit is claimed on
a reading taken before SL-1259's `/score` changes, or on one process instead of the S4
replica path; an SL-1455/SL-1259 disagreement is settled by precedence instead of an `FD-`;
or the VM is left running, or not deleted, after S5's verdict.

- *Violation: the wrong verdict holder.* SL-1455's `LG-` or the SL-1455 roadmap row states an
  NFR-489 PASS or FAIL for P2's exit. This is checked at SL-1455's ACK, and at the Phase 2
  close against `roadmap.md` §12 row 2.
- *Violation: the exit reading is taken off the exit tree.* SL-1259's `LG-` names the tree its
  verdict was measured on. That tree must contain S5's own `score.py` changes, and the
  replica count must be stated. Checked at SL-1259's ACK.
- *Violation: a disagreement settled by precedence.* SL-1455 is in budget and SL-1259 is over
  budget, but the register gains no `FD-`. Checked at SL-1259's ACK.
- *Violation: the VM outlives its purpose.* The SL-1259 `LG-` and the dated line at
  `roadmap.md:569–570` (10:57:16 BST, item 1) record the VM's deletion, with its
  verification. This is held by the dispatch and the LG, not by a repository check.

## What this record does not decide

- **`PL-1454` DP-3** ("per replica"), ruled from SL-1455 Task 0's record.
- **The dedicated VM's type, cost and creation**: the user's (10:57:16 BST, item 2).
- **What happens if SL-1259 slips past P2's exit demo**: a narrowing question for the Fri
  16 Oct checkpoint ("2026-10-10 21:29:10 BST — USER DECISION: R2 = (A) …", item 3).
