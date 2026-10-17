---
id: RL-8076
family: ruling
title: PL-1454 Task 4's acceptance sweep runs on the dedicated host nfr-bench-1, and its reading there is the NFR-489 verdict (precises PL-1454 Acceptance 2 and Task 4's host; G4 discharge event met)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-16            # original date 2026-10-16, the maintainer's dated line; drafted 2026-10-17
owner: decision-maker
tree: 055b5e6b74f9d4b10f6df54570e33ed2805ae9a8
phase: P2
work: WK-1178
slice: SL-1455
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1454, SL-1455, WK-1178, NFR-489, NFR-454]
---

# RL-8076 — PL-1454 Task 4's acceptance sweep runs on the dedicated host, and its reading is the G4 verdict

**Precises PL-1454 Acceptance 2 and Task 4's host; G4 discharge event met.**

**Decided by the maintainer, by delegation**, in the entry headed *"2026-10-16 22:22:44 BST —
Maintainer: DATED LINE on PL-1454 Acceptance 2 / Task 4 — the sweep moves to the dedicated
host, and its reading is the G4 VERDICT (discharges SL-1455 audit F1)"* in
`~/gi-pricing-plan.local/channel/to-lead.md` (`:25011`, read 2026-10-17). Its item 4 names
this record: *"It is minted as an RL in the next D batch ("precises PL-1454 Acceptance 2 and
Task 4's host; G4 discharge event met"), drafted verbatim from this entry."* The
decision-maker drafted this record and decides nothing beyond the entry. The lead reserved
the working id in `~/gi-pricing-plan.local/handover/eta.md`, entry "2026-10-16 22:23:23 BST".

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

## Ruled

The entry's items 1–3, as quoted above. In short:

1. PL-1454 Task 4's acceptance sweep (Acceptance 2 and 3: 12 interleaved invocations at
   R ∈ {25, 50, 100, 200} × 3, same command, timeout 1500, scratch DB, un-instrumented head,
   per-invocation records) runs on **nfr-bench-1**, not the shared VM. PL-1454 stays as
   written (frozen); this ruling supersedes its host clause.
2. On nfr-bench-1 the reading is labelled **"measured, dedicated host (G4 discharge)"**. It
   is the NFR-489 verdict, and NFR-454's limb in the same invocations: a pass or a fail may
   be claimed, on conditions (a)–(c). An invocation that fails (a) is diagnostic only and is
   re-run.
3. The OVER rule does not change. The two owed items (Task 1 Step 4 `--rates 25`; Task 3
   Step 5 byte-identity) and Acceptance 1's default-live limb run in the same session.

## What it obliges

- SL-1455's executor runs the sweep on nfr-bench-1 under conditions (a)–(c), and records
  them per invocation in the slice's ledger (LG 9932, a working id).
- LG 9932 cites this ruling. SL-1455's audit cites it for F1 as discharged.
- It does **not** edit PL-1454, and it does not change any other G4 carried verdict. The
  session date (earliest Mon 19 Oct) is the maintainer's to arrange.

## Acceptance — the violation that must become detectable

The violation: a reading labelled "measured, dedicated host (G4 discharge)", or a pass or
fail of NFR-489 claimed from the sweep, whose ledger record lacks one of conditions (a)–(c)
for its invocation.

- *Violation: an invocation's record has no `uptime`, no `pgrep -c pytest` = 0, or no `ps`
  top-5, but its reading counts toward the verdict.*
- *Violation: the benched head is named without its full sha and tree.*
- *Violation: the ledger does not record the host's machine type, vCPU and RAM.*

No script checks these. They are checked by reading the ledger, at SL-1455's audit and at
the lead's ACK.
