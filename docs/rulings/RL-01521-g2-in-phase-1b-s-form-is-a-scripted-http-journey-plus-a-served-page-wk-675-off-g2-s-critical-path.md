---
id: RL-1521
family: ruling
title: G2's "in Phase 1b's form" is a scripted HTTP journey ending in a served page, and WK-675 is off G2's critical path (the maintainer's ruling by delegation, recorded)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: decision-maker
tree: 809a3794af6d3a6ba688663b0d9b59f951190680
phase: P2
work: ~
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [CR-1212, CR-821, FD-1283, PL-1371, WK-675]   # at the mint, add PL 9629's minted id
---

# RL-1521 — G2's "in Phase 1b's form": a scripted HTTP journey plus a served page; WK-675 off G2's critical path

*(Minted 2026-10-08 as RL-1521 from working id 9623, in the G2-a batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

## How this was ruled

- **Filed under a working id the lead reserved.** `RL-1521` in this draft stands for this
  record's minted id. It mints **before** PL 9629 (the exit-demo leaf (b), `PL-1371` Task 3),
  which cites it.
- **The ruling is not this record's.** It is the maintainer's (by delegation), in
  `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-05 13:05:42 BST — RULING (the
  maintainer, by delegation): G2's "in Phase 1b's form" = a scripted HTTP journey plus a
  served page; WK-675 is OFF G2's critical path". That file is local, so a repository reader
  cannot open it (RFC-777). This record quotes the entry verbatim and re-reads its four sources
  at `origin/main`, so that PL 9629 can cite a governed record instead. It decides nothing.
- **Mandate:** the maintainer's (by delegation) entry "2026-10-05 15:06:32 BST — Exit-demo
  re-scope under PL-1371 Task 3: ACCEPTED; my G2 ruling needs a governed home before PL 9629
  mints": "A DM records it as a short RL quoting the entry verbatim with its sources (CR-1212
  :68, CR-821 :17-19, roadmap :350, FD-1283 :107). PL 9629 cites that RL, which mints BEFORE
  PL 9629. The G2 interpretation of an accepted exit criterion is the maintainer's, and the RL
  records it as given by delegation."

## Ruled

The entry, verbatim (header above):

> Verified at caa4e411: CR-1212 :68 "It runs from one command to a served page, in Phase 1b's form (`docs/roadmap.md:350`)."; CR-821 :17-19 "a scripted HTTP run of the core `WF-698` journey (`scripts/demo.py` with the full 678 013-row freMTPL2 seed), with the UI available for hands-on driving."; roadmap :350, the Phase 1b exit-demo row, "exercised over HTTP"; FD-1283 :107 ends "… in Phase 1b's form" (`docs/roadmap.md`, G2), which is a demo run, not a UI walk-through".
> Ruling: G2 is met by `scripts/demo.py`-style ONE command that runs WF-699 A–E and its deploy step over HTTP on the freMTPL2 seed and ends with the frontend SERVING (a 200 page, routes registered), the UI available for hands-on driving but not driven. No WK-675 view is a G2 prerequisite. The Exit demo row's "where no view is needed" (:603) is read accordingly: no view is needed for G2.
> Consequences: WK-675 stays on its PL-1371 schedule, not the critical path; G1 still requires every P2 Work, WK-675 included, to be resolved, so its slices still need doing or a dated move. The exit-demo plan records this ruling by this entry's header when it is filed.

## Sources — re-read at `origin/main` `809a3794`, 2026-10-05

The entry verified its sources at `caa4e411`. Each was re-read at `809a3794` with
`git show 809a3794:<file> | sed -n '<line>p'`. All five lines are where the entry says they
are, and each says what the entry quotes. None contradicts the ruling.

- **`CR-1212` :68** (`docs/closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md`):
  "It runs from one command to a served page, in Phase 1b's form (`docs/roadmap.md:350`)."
- **`CR-821` :17-19** (`docs/closures/CR-00821-phase-1b-exit-demo-uat-acceptance-record.md`):
  "Acceptance mechanism: a scripted HTTP run of the core `WF-698` journey (`scripts/demo.py`
  with the full 678 013-row freMTPL2 seed), with the UI available for hands-on driving."
- **`docs/roadmap.md` :350**, the Phase 1b Exit demo row: "the core `WF-698` journey (dataset →
  factors → GLM + GBM fits → comparison → approval → rating version) — exercised over HTTP".
  G2 itself is at `:566`: "… from one command to a served page, in Phase 1b's form."
- **`FD-1283` :107** (`docs/findings/FD-01283-three-03-5-3-views-the-rating-version-list-the-regression-suite-and-deployments-are-owned-by-no-work-plan-ruling-or-closure.md`),
  row E, ends: "G2 is "from one command to a served page, in Phase 1b's form"
  (`docs/roadmap.md`, G2), which is a demo run, not a UI walk-through".
- **`docs/roadmap.md` :603**, the Phase 2 Exit demo row, which the ruling reads: "It can be cut
  in parallel with WK-675 where no view is needed".

## What it obliges

- **PL 9629** cites this record, not the local entry, for G2's form.
- **No spec or roadmap text changes here.** G2 (`docs/roadmap.md:566`) and the Exit demo row
  (`:603`) are read as the ruling says; neither is edited.
- **WK-675** stays on its `PL-1371` schedule. G1 still applies to it.

## Acceptance — the violation that must become detectable

1. **A G2 run that stops short of a served page.** A demo command that runs the journey over
   HTTP but does not end with the frontend answering 200 with its routes registered does not
   meet G2 as ruled.
2. **A G2 plan that gates on a WK-675 view.** PL 9629, or any later exit-demo plan, that makes a
   WK-675 view, or a driven UI walk-through, a G2 prerequisite contradicts the ruling quoted
   above.
