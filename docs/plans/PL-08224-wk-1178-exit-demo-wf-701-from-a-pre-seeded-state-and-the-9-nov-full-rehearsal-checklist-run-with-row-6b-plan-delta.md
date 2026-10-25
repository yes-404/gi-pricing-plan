---
id: PL-8224
family: plan
kind: map
title: WK-1178 — the exit demo shows WF-701 from a pre-seeded state, and the full PL-1544 rehearsal checklist runs on the exit tree on Mon 9 Nov 2026 with a new WF-701 browser row 6b: a dated delta to PL-1544
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-25            # original date 2026-10-25, set at the draft
owner: planner
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1544, PL-1577, PL-1644, PL-1710, SL-1711, LG-1841, OQ-1789, WF-699, WF-701, SL-8225]
---

# WK-1178, exit demo: WF-701 from a pre-seeded state, and the 9 Nov full checklist run with row 6b (delta to PL-1544)

*(Drafted 2026-10-25 under working id PL 8224, reserved by the lead in `eta.md` with SL 8225 and
LG 8226. The ids mint in the §14 plan review's PR, item 34's order.)*

> **For agentic workers:** this is a **dated delta** under Lean P2 L5 (`document-ids.md` §1.6,
> PL row: *"a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's
> plan"*). It does not replace and does not edit
> [`PL-1544`](PL-01544-wk-1178-exit-demo-slice-b-the-scripted-wf-699-journey-over-http-to-a-served-page-leaf-plan.md)
> (frozen). Its form follows the two earlier deltas to `PL-1544`,
> [`PL-1577`](PL-01577-wk-1178-r6-the-exit-demo-dislocation-portfolio-a-20000-policy-sample-built-by-the-seed-plan-delta.md)
> and
> [`PL-1644`](PL-01644-wk-1178-exit-demo-b-wf-699-d4-s-fixed-property-declaration-and-the-lines-the-11-oct-merges-made-stale-plan-delta.md),
> including their `kind: map` (the `PL-` kinds are `map`, `leaf`, `review` and `handover`;
> "delta" is the title's word, not a kind). **Read `PL-1544` §"Rehearsal checklist", then this
> file.** The executor of `SL 8225` binds `dev-commands` and `git-hygiene` and is spawned from
> `.claude/roles/executor.md`. It writes no code.

Written 2026-10-25 by the planner (planner-pl14), on the lead's brief of 2026-10-25. Evidence
was read at `origin/main` `ff976406f1bf133cfe040d2c44d383011503988a`.

## Status

`active` at the draft: no decision point is open. Both choices it records were made by the
maintainer's dated line quoted below. It carries two changes, E1 and E2 of the §14 plan
review (the review's `CR- kind: review`, working id CR 8219, indexes this file as their record).

## Goal

The 12 Nov exit demo shows WF-701, the journey the demo now covers, without a live run whose
length has no budget; and the full `PL-1544` rehearsal checklist, including the browser path
that `SL-1711` waived and a new WF-701 browser row, has been run once on the exit tree, with a
ledger, three days before the demo.

## The ruling this delta records, quoted

The maintainer, `channel/to-lead.md` (local; RFC-777), entry headed *"2026-10-25 11:32:17 GMT —
Maintainer: §14 note r5 — the six owed rulings, decided now (dated lines for the review's
rows)"*, line 6, verbatim:

> 6. **E1 — option (b):** the exit demo shows WF-701 from a pre-seeded state; one **PL delta** (planner) `relates:` the exit-demo plan, recording the live run's measured duration as an observation with **no budget** (a cap from the fit stays refused). **E2 — the run:** one full PL-1544 checklist run (rows 0–9, row 6 included) on the exit tree on **Mon 9 Nov 2026**, owner WK-1178, as an **SL** row + LG; and **yes**, add a WF-701 browser check as row 6b by the same PL delta as E1, since the demo shows WF-701.

The acceptance of both items as drafted, the entry headed *"2026-10-23 10:57:28 BST —
Maintainer: the §14 review agenda: the three carries JOIN; the "Before Phase 2" drift is an E3
PROPOSAL; my 10:52 seating order recorded here"*, verbatim:

> - **E1 (WF-701 2500 s with no budget; OQ-1789 caps WF-699 only) and E2 (PL-1544 row 6 browser step as one full checklist run on the exit tree): ACCEPTED as drafted.**

## The evidence these changes rest on, at `ff976406`

- **The one measured WF-701 run.** `LG-1841` §"The compose SOLO run of the scripted WF-701
  demo" quotes `demo.py --journey wf-701 --target compose`'s closing lines: `WF-699 part done in
  1335s`, `WF-701 part done in 1165s: OVER the pre-registered 10 min target (recorded, not
  tuned)`, `journey done in 2500s`. The 10 min is `WF701_TARGET_SECONDS: Final = 600`
  (`scripts/demo.py:62`), PL-1710 T7's pre-registered target; `LG-1841` records the miss as "not
  a fail" and its §"Carried observation" says "No budget exists".
- **No budget covers it.** `OQ-1789` (`03` §10, decided 2026-10-18) caps the WF-699 demo at
  1,500 s, quiet window only. It does not cover WF-701 (the 10:57:28 line above).
- **PL-1544's checklist runs WF-699 only.** Row 5 is `uv run python scripts/demo.py --journey
  wf-699`; row 6 is the browser on `/demo` and `/rating-versions/<id>` from row 5's output.
- **Row 6 has not been run since SL-1711 waived it.** `LG-1841`'s checklist row 6: *"WAIVED for
  SL-1711 … The browser path … is carried to the CLAUDE.md §14 plan review and the 12 Nov
  exit-demo rehearsal, which run it in full"*. The compose target runs no frontend (same row).
- **The local target serves WF-701 with the frontend.** `scripts/demo.py:56` has `JOURNEYS:
  Final = ("wf-699", "wf-701")`; `--target compose` runs only `wf-701` and no frontend
  (`:452-453`); the default (local) target with `--journey` needs the frontend and ends with it
  serving a 200 page (`:455-460`).
- **What WF-701 leaves.** `examples/fremtpl2/journey_wf701.py` walks the steps of its
  `STEP_ORDER` (`:76-80`) on the state WF-699's journey leaves. Two candidate Rating Versions,
  K1 and K2, are built, compiled and approved by two principals over HTTP (`:745-749`,
  `:1161-1165`; the module docstring). C1 ends with *"K1 is prod's newest deployment"*
  (`:1036-1038`); C6 prints the prod golden quote (`:1060-1062`). The two ruled lines are
  `COMPOSE_ONLY` = `"COMPOSE-ONLY A2/C4/C6 replica limb"` and `C7_ERRORS` = `"C7-errors:
  refused, not traced (FR-259, RL-1712)"` (`:70-71`).
- **No browser view shows a deployment.** `frontend/src/views/RatingVersionView.vue:146-147`:
  *"The Phase 1b rating version (FR-440). Compile, score, rate tables and deployment stay
  Phase 2."* The router has `/rating-versions/:id` (`frontend/src/router/index.ts:241`) and no
  deployment or environment route. So a browser check can show the candidates' approval, and
  the deployment is shown by the journey's own server read-back line, not by a page.

## E1 — the exit demo shows WF-701 from a pre-seeded state

1. **The pre-seed.** On the exit tree, before the audience joins, the operator runs `uv run
   python scripts/demo.py --journey wf-701` (the local target, full seed) to the served page.
   That command walks WF-699's journey and then WF-701's on the state it leaves. Its log is
   kept, by tree.
2. **What the demo shows.** The presenter shows the state the pre-seed left: the WF-701 step
   lines of the kept log (A1–A6, C1–C4, C6, C7, as `STEP_ORDER` gives them) and the browser
   pages of row 6b below. No part of WF-701 is run live in front of the audience. The demo does
   not show the compose target; `LG-1841`'s compose run stands as the replica-limb evidence.
3. **The duration is an observation with no budget.** The pre-seed's three timing lines
   (`WF-699 part done in …s`, `WF-701 part done in …s: …`, `journey done in …s`) are quoted
   verbatim, with the tree, in the record of the run. They are never a pass or fail. No cap is
   set from them or from `LG-1841`'s 2500 s: *"a cap from the fit stays refused"* (line 6
   above). The demo's own `within` / `OVER the pre-registered 10 min target` word is quoted as
   printed and is not a verdict of this plan.
4. **Not changed.** No spec NFR is added, `OQ-1789` is not reopened, and `WF701_TARGET_SECONDS`
   is not edited.

## E2 — the full checklist run on Mon 9 Nov 2026, and row 6b

### The run

One full run of `PL-1544` §"Rehearsal checklist", rows 0 to 9 **as written there** (row 6
included), plus row 6b below, on `main` at the exit tree, on **Monday 9 November 2026**, owner
**WK-1178**. It is slice `SL 8225`, and its ledger `LG 8226` records each row by command, output
and tree, never from memory. The order is 0, 1, 2, 3, 4, 5, 6, 6b, 7, 8, 9. Row 9 stops the
demo that row 6b started. A row that fails is recorded as it printed and the run STOPS to the
lead; no row is re-run until green.

### The new row 6b — the WF-701 browser check

| # | Command | Check |
|---|---|---|
| 6b | After row 6's check: Ctrl-C row 5's demo; `pgrep -af 'uvicorn\|vite'` (nothing left). Then `uv run python scripts/demo.py --journey wf-701` (full seed; E1's pre-seed command). In the browser: `/demo`, then `/rating-versions/<id>` for K1 and for K2, each `<id>` the item of `GET /api/v1/rating-versions` whose `slug@version` the run printed on its `K1: rating version …` and `K2: rating version …` lines | The run: every WF-701 step in `STEP_ORDER` printed `ok` once; the only other lines are the ruled `COMPOSE-ONLY A2/C4/C6 replica limb` (once) and `C7-errors: refused, not traced (FR-259, RL-1712)` (once); C1's line says K1 is prod's newest deployment; the served page 200; the `/demo` URL printed; the three timing lines quoted verbatim as an observation (E1 item 3). The browser: `/demo` loads; both Rating Version pages load and show `approved`. The deployment is evidenced by C1's line, not by a page (no view shows one at `ff976406`) |

*(Dated 2026-10-25 by the lead, on the maintainer's entry "2026-10-25 11:53:23 GMT — Maintainer: PL 8227 DP-S1 (ii), DP-S2 (i)/(i)/(i), departure (b) accepted; the loopback PR = PL-1769 Step 1.5 delivered early, :187 bound too, full gate": row 6b's browser pages are reached over an SSH port-forward, because the local compose stack binds to `127.0.0.1` once the loopback PR (PL-1769 Step 1.5) lands.)*

Row 7's `test_wf699_journey.py` is unchanged. A `test_wf701_journey.py` run is not added to the
checklist: it runs in every gate's full pytest (`LG-1841` row 7).

### The roadmap row, as drafted (the lead adds it; this plan does not edit `docs/roadmap.md`)

````markdown
#### SL-8225 — WK-1178 rehearsal slice — the full PL-1544 rehearsal checklist (rows 0–9 and PL-8224's row 6b) on the exit tree, Mon 9 Nov 2026

```yaml
id: SL-8225
family: slice
title: WK-1178 rehearsal slice — the full PL-1544 rehearsal checklist (rows 0–9 and PL-8224's row 6b) on the exit tree, Mon 9 Nov 2026
status: draft                    # draft → active → closed | retired (§1.2a)
created: 2026-10-25
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-1178
corrected_by: []
relates: [PL-8224, PL-1544, LG-1841, SL-1711]
```

One full run of `PL-1544` §"Rehearsal checklist", rows 0 to 9 as written there (row 6, the browser path `SL-1711` waived, included), plus row 6b, the WF-701 browser check that PL 8224 adds, on `main` at the exit tree on Monday 9 November 2026; order 0–6, 6b, 7–9. Cut as one WK-1178 slice by the maintainer's entry "2026-10-25 11:32:17 GMT — Maintainer: §14 note r5 — the six owed rulings, decided now (dated lines for the review's rows)", line 6 (E2), in the CLAUDE.md §14 plan review before the 12 Nov exit demo. Its ledger LG 8226 records each row's command, output and tree; WF-701's timing lines are an observation with no budget (PL 8224 E1 item 3). No code, spec or plan file changes. **Activation needs:** PL 8224 minted; the exit tree named by the lead; no gate slot held and no other run on the box (row 1); the lead's GO. *(Row cut 2026-10-25 by the planner in PL 8224; working ids SL 8225 and LG 8226 reserved by the lead in `eta.md`.)*
````

## Decision points

None open. E1's option (b) and E2's date, owner and row 6b were ruled by the 11:32:17 entry's
line 6, quoted above. The exit tree's sha and SL 8225's GO are the lead's, as for every slice.

## Tasks

### Task 1 (SL 8225, Mon 9 Nov 2026): the full checklist run

- [ ] **Step 1:** Record the exit tree, then run `PL-1544` rows 0 to 6 as written there, each
  row's command, output and tree into LG 8226.
- [ ] **Step 2:** Run row 6b (above) and record it the same way, the three timing lines
  verbatim as an observation.
- [ ] **Step 3:** Run `PL-1544` rows 7 to 9 as written there; row 9 stops row 6b's demo.
- [ ] **Step 4:** Any failing row: record it as printed and STOP to the lead.

### Task 2 (the exit demo, 12 Nov): the pre-seed

- [ ] **Step 1:** Before the audience joins, run E1 item 1's command on the exit tree and keep
  its log by tree; quote its timing lines as E1 item 3 says. The demo shows that state (E1
  item 2).

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **This delta is filed and `PL-1544` is unedited.** `git diff --name-only origin/main...HEAD`
   on this delta's branch lists only this file and `docs/INDEX.md`;
   `git diff origin/main...HEAD -- docs/plans/PL-01544-*` prints nothing.
2. **Row 6b exists here, with its command and its check**, and rows 0–9 are cited, not
   restated: `grep -c '^| 6b |' <this file>` prints `1`.
3. **No budget is set.** `git grep -n -i -E 'WF-701.*(budget|cap)' -- docs/specs/` prints no new
   line against `origin/main`; `scripts/demo.py:62` still reads `WF701_TARGET_SECONDS: Final =
   600`.
4. **The run happened on its date, in full.** `LG 8226` (minted id) carries one line per row 0,
   1, 2, 3, 4, 5, 6, 6b, 7, 8, 9, each with its command, its output as printed and the exit
   tree, dated 2026-11-09; row 6b quotes the three timing lines verbatim and records the K1 and
   K2 pages as loaded and `approved`.
5. **The record is clean.** `python3 scripts/audit-docs.py` and `python3 scripts/doc-index.py
   --check` exit 0 on the minted tree.

## Global Constraints

- **Frozen plan:** `PL-1544` is never edited (`document-ids.md` §1.5); every change is this delta.
- **No budget from the fit:** line 6 of the 11:32:17 entry, quoted above.
- **Phase:** P2, docs only (`CLAUDE.md` §0); no code, spec or contract change.
- **The run's environment:** `PL-1544` rows 0 and 1 hold — `main` at the exit tree, clean, both
  gate slots free, nothing heavy running.

## Self-review

1. *Line 6 coverage.* "pre-seeded state": E1 items 1–2. "the live run's measured duration … as
   an observation with no budget": E1 item 3, Acceptance 3. "rows 0–9, row 6 included … on the
   exit tree on Mon 9 Nov 2026, owner WK-1178, as an SL row + LG": E2 §"The run", the drafted
   row. "a WF-701 browser check as row 6b": the row 6b table.
2. *Nothing claimed that the tree does not do.* The browser shows approval, not deployment
   (`RatingVersionView.vue:146-147`); row 6b says so. The local target runs WF-701 with the
   frontend (`demo.py:455-460`); the compose target does not (`:452-453`, `LG-1841` row 6).
3. *Id forms.* Front matter and the drafted row's YAML use the hyphen form; prose uses the
   space form for the unminted SL 8225, LG 8226 and CR 8219.
4. *Not decided here.* The exit tree's sha and the GO are the lead's; the 12 Nov presenter's
   script is not this plan's.
