---
id: RL-1793
family: ruling
title: PL-1454 Task 4's acceptance sweep runs on the dedicated host nfr-bench-1, and its reading there is the G4 discharge for the FD-1411 remedy proof; the NFR-489 exit verdict stays SL-1259's per RL-1614 (precises PL-1454 Acceptance 2 and Task 4's host; G4 discharge event met)
status: retired                # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-18   # filed 2026-10-16 under working id 8076; minted 2026-10-18 as RL-1793
owner: decision-maker
tree: 055b5e6b74f9d4b10f6df54570e33ed2805ae9a8
phase: P2
work: WK-1178
slice: SL-1455
supersedes: []
superseded_by: ~
corrected_by: [RL-8122]
relates: [PL-1454, SL-1455, WK-1178, NFR-489, NFR-454, RL-1614, FD-1411]
---

# RL-1793 — PL-1454 Task 4's acceptance sweep runs on the dedicated host, and its reading is the G4 discharge for the FD-1411 remedy proof

**Precises PL-1454 Acceptance 2 and Task 4's host; G4 discharge event met.**

**Decided by the maintainer, by delegation**, in the entry headed *"2026-10-16 22:22:44 BST —
Maintainer: DATED LINE on PL-1454 Acceptance 2 / Task 4 — the sweep moves to the dedicated
host, and its reading is the G4 VERDICT (discharges SL-1455 audit F1)"* in
`~/gi-pricing-plan.local/channel/to-lead.md` (`:25011`, read 2026-10-17). Its item 4 names
this record: *"It is minted as an RL in the next D batch ("precises PL-1454 Acceptance 2 and
Task 4's host; G4 discharge event met"), drafted verbatim from this entry."* The
decision-maker drafted this record and decides nothing beyond the entry. The lead reserved
the working id in `~/gi-pricing-plan.local/handover/eta.md`, entry "2026-10-16 22:23:23 BST".

**Corrected by the maintainer** in the entry headed *"2026-10-17 11:22:47 BST — Maintainer:
SL-1259 (S5) DPs ruled; CORRECTION of my 16 Oct 22:22:44 item 2 (it overreached RL-1614)"*
in the same file (`:25217`–`:25218`, read 2026-10-17). The correction supersedes item 2 of
the 22:22:44 entry. It was made before this record was minted, so this record carries the
corrected reading from its first merge; nothing frozen is edited.

## Verified first, at 055b5e6b74f9d4b10f6df54570e33ed2805ae9a8

The entry, verbatim (`to-lead.md` `:25011`–`:25025`):

> ## 2026-10-16 22:22:44 BST — Maintainer: DATED LINE on PL-1454 Acceptance 2 / Task 4 — the sweep moves to the dedicated host, and its reading is the G4 VERDICT (discharges SL-1455 audit F1)
> Basis, read at origin/main 6b25b9bc:
> - PL-1454 (`docs/plans/PL-01454-…-leaf-plan.md`) Acceptance 2 (around :122-148) and Task 4 (around :512-523) say the sweep "runs on the shared VM (e2-standard-8)" and label every figure "measured, diagnostic (G4)".
> - docs/roadmap.md §G4 (around :571-573), amended 2026-09-29 by the maintainer: near-bound verdicts including NFR-489 are "measured, diagnostic on the shared VM; the verdict is carried, owner the maintainer, discharge event a dedicated host available".
> - The user approved the dedicated host on 12 Oct (brief handover/vm-build-brief-nfr-bench-1-2026-10-12.md).
> RULED (the maintainer, by delegation):
> 1. PL-1454 Task 4's acceptance sweep (Acceptance 2 and 3: the 12 interleaved invocations at R ∈ {25, 50, 100, 200} × 3, with the same command, timeout 1500, scratch DB, un-instrumented head and per-invocation records) runs on **nfr-bench-1**, not the shared VM. PL-1454's text stays as written (frozen); THIS line supersedes its host clause.
> 2. On nfr-bench-1 the reading is labelled "**measured, dedicated host (G4 discharge)**". It IS the NFR-489 verdict (and NFR-454's limb in the same invocations): a pass or fail may be claimed, on these conditions:
>    - (a) the host runs nothing but the sweep, its server and its DB, shown by `uptime` + `pgrep -c pytest` = 0 + `ps` top-5 per invocation;
>    - (b) the head benched is named by full sha and tree;
>    - (c) the host spec (machine type, vCPU, RAM) is recorded in the ledger.
>    If (a) fails for any invocation, that invocation is diagnostic only and is re-run.
> 3. The OVER rule is unchanged: stop and report, no re-run without a new go. The two owed items (Task 1 Step 4 --rates 25; Task 3 Step 5 byte-identity) and Acceptance 1's default-live limb run in the same session.
> 4. Record: this entry is the dated line. It is minted as an RL in the next D batch ("precises PL-1454 Acceptance 2 and Task 4's host; G4 discharge event met"), drafted verbatim from this entry. LG 9932 cites it, and SL-1455's audit F1 cites it as discharged.
> The session is earliest Mon 19 Oct (readiness note). I ask the user ~2 h ahead.

The entry read its basis at origin/main 6b25b9bc. The drafter re-read each cited cell at
this record's tree (055b5e6b, tree f394adecbe0382f790c6402b2558fbd4eec302c9):

- `docs/plans/PL-01454-wk-1178-nfr-489-remedy-the-score-request-path-meets-its-p99-budget-leaf-plan.md`
  Acceptance 2: `:141`–`:143` quote G4 (*"measured, diagnostic on the shared VM"*, bold dropped) and say
  *"This sweep runs on the shared VM"*. Task 4: `:520` labels each reading *"measured,
  diagnostic (G4)"*. Both sit inside the ranges the entry gives (around :122-148 and
  :512-523).
- `docs/roadmap.md` §G4 `:571`–`:573`: the 2026-09-29 amendment quotes the maintainer:
  *"These verdicts are **measured, diagnostic** on the shared VM; the verdict is
  **carried**, owner the maintainer, discharge event **a dedicated host available**."* Its
  list of near-bound verdicts names NFR-489.
- NFR-489 is `docs/specs/03-rating-engine.md` `:1507`; NFR-454 is `docs/specs/00-overview.md`
  `:544`.
- The 12 Oct host approval (`handover/vm-build-brief-nfr-bench-1-2026-10-12.md`) is the
  entry's citation; the drafter did not re-read it.

The correction, verbatim (`to-lead.md` `:25217`–`:25218`; the entry's other lines rule
SL-1259's DPs into PL-1794 and are not this record's):

> ## 2026-10-17 11:22:47 BST — Maintainer: SL-1259 (S5) DPs ruled; CORRECTION of my 16 Oct 22:22:44 item 2 (it overreached RL-1614)
> CORRECTION: my 22:22:44 item 2 said SL-1455's dedicated-host sweep "IS the NFR-489 verdict". RL-1614 (on main; my own 11 Oct ruling) says SL-1259 holds P2's NFR-489 EXIT verdict on the exit tree, and SL-1455's Task 4 sweep is the FD-1411 REMEDY PROOF only, with "no two competing verdicts". I did not re-read RL-1614 before writing 22:22:44. CORRECTED: on nfr-bench-1, SL-1455's sweep is the G4 discharge for the FD-1411 remedy proof (a near-bound pass or fail may be claimed FOR THE REMEDY). The NFR-489 exit verdict stays S5's. RL-1793's text says exactly this and cites RL-1614.

The drafter checked RL-1614 at origin/main 055b5e6b
(`docs/rulings/RL-01614-dp-s5-a-decided-a-sl-1259-holds-the-nfr-489-exit-verdict-and-sl-1455-s-task-4-sweep-is-the-fd-1411-remedy-proof.md`):
its ruled items 1 and 2 (`:82`, `:86`–`:88`) say the NFR-489 exit verdict is SL-1259's and
that SL-1455's Task 4 table is the FD-1411 remedy proof, *"never written as P2's NFR-489
exit verdict"*; its quoted entry rejects option (c) as *"two competing verdicts"* (`:50`).
FD-1411 is `docs/findings/FD-01411-the-full-score-http-path-on-main-misses-nfr-489-at-every-rate-measured-with-and-without-a-gbm-call-and-runs-away-from-100-rps.md`.

## Ruled

The 22:22:44 entry's items 1–3, as quoted above, with item 2 as corrected at 11:22:47. In
short:

1. PL-1454 Task 4's acceptance sweep (Acceptance 2 and 3: 12 interleaved invocations at
   R ∈ {25, 50, 100, 200} × 3, same command, timeout 1500, scratch DB, un-instrumented head,
   per-invocation records) runs on **nfr-bench-1**, not the shared VM. PL-1454 stays as
   written (frozen); this ruling supersedes its host clause.
2. *(As corrected 2026-10-17 11:22:47 BST; this supersedes the 22:22:44 item 2.)* On
   nfr-bench-1 the reading is labelled **"measured, dedicated host (G4 discharge)"**. It is
   the G4 discharge for the **FD-1411 remedy proof**: a near-bound pass or fail may be
   claimed **for the remedy**, on conditions (a)–(c). An invocation that fails (a) is
   diagnostic only and is re-run. It is **not** the NFR-489 verdict: the NFR-489 exit
   verdict stays SL-1259's (WK-674 S5), per RL-1614, with no two competing verdicts.
3. The OVER rule does not change. The two owed items (Task 1 Step 4 `--rates 25`; Task 3
   Step 5 byte-identity) and Acceptance 1's default-live limb run in the same session.

## What it obliges

- SL-1455's executor runs the sweep on nfr-bench-1 under conditions (a)–(c), and records
  them per invocation in the slice's ledger (LG 9932, a working id).
- LG 9932 cites this ruling. SL-1455's audit cites it for F1 as discharged.
- SL-1455's ledger and audit write the sweep's reading as the FD-1411 remedy proof, never
  as P2's NFR-489 exit verdict, which stays SL-1259's (RL-1614).
- It does **not** edit PL-1454, and it does not change any other G4 carried verdict. The
  session date (earliest Mon 19 Oct) is the maintainer's to arrange.

## Acceptance — the violation that must become detectable

The violation: a reading labelled "measured, dedicated host (G4 discharge)", or a pass or
fail of the FD-1411 remedy claimed from the sweep, whose ledger record lacks one of
conditions (a)–(c) for its invocation; or the sweep's reading written as the NFR-489 exit
verdict.

- *Violation: an invocation's record has no `uptime`, no `pgrep -c pytest` = 0, or no `ps`
  top-5, but its reading counts toward the verdict.*
- *Violation: the benched head is named without its full sha and tree.*
- *Violation: the ledger does not record the host's machine type, vCPU and RAM.*
- *Violation: SL-1455's ledger or audit claims an NFR-489 pass or fail (the exit verdict)
  from the sweep, instead of the FD-1411 remedy proof (RL-1614).*

No script checks these. They are checked by reading the ledger, at SL-1455's audit and at
the lead's ACK.
