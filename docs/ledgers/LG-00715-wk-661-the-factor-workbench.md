---
id: LG-715
family: ledger
title: WK-661 — the factor workbench
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-15
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — the factor workbench, 2026-08-15 *(in progress, not closed)*

The third slice, and the first one with a screen. `02` §5.3's factor workbench is routed at
`/factors/:datasetVersionId` and reachable from a `validated` version — which turns the
previous slice's API into something a person can drive, and the exit demo's outstanding
half ("accepted without being driven") into something with more to drive.

**Two gaps found by building the view, both spec changes made before the code:**

| Gap | What it was |
|---|---|
| **FR-102** *(new)* — evaluate a Banding or Grouping **without persisting it** | §5.3's interaction requirement — that an edit's consequence is visible before saving — was **unmeetable**. `/propose` derives boundaries from a *method* and has no way to accept an edited one, so "the proposal is always editable" (FR-98, FR-105) meant editable but unmeasurable. `POST /bandings/evaluate` and `POST /groupings/evaluate` are the answer |
| **`GET /dataset-versions/{id}`** — added to `01` §5.1 | Nine routes in that table are children of `/dataset-versions/{id}` and **the parent was not among them**. The only version detail route was `/datasets/{slug}/versions/{version}`, so anything holding a version id and not a dataset slug could not resolve it — which is exactly the position a view routed on `:datasetVersionId` is in. Not a new capability, so no new requirement: the row the table should always have had |

| Delivered | Evidence |
|---|---|
| `/factors/:datasetVersionId` — banding and grouping editors | 12 view tests. Moving a boundary calls `/bandings/evaluate`; re-pointing a level calls `/groupings/evaluate`; deleting either call fails a test rather than silently making the preview local |
| The edit that cannot be valid | A boundary crossing its neighbour is marked and **not sent**. The platform would refuse it correctly with a `422`, and a 422 per keystroke is not an editor — so the last valid evaluation stays on screen |
| The merge verdict in words | `02` §4.3's p-value read out loud: above 0.05 "the data does not distinguish these levels", below 0.01 "this merge discards real signal". One place says it, so a later dossier cannot describe the same number differently |
| Reachability | Linked from a version's detail view, and **only from a `validated` one** — `02` R1 means a link on a draft leads to a 409 the screen cannot explain |

**Not delivered, and §5.3 says so rather than the note quietly dropping it:** drag handles
on the boundaries (numeric inputs meet the requirement and can express a cut the mouse
cannot land on), the merge-tolerance slider (it is a *proposal* parameter — re-proposing on
every drag would discard the actuary's edits), inline profile one-ways in the column list,
and the monotonic-direction and intent controls, which belong with creating the Factor that
pins a banding.

**FR-393 still gates real browser use.** Until PKCE ships (WK-664), the SPA reaches the
API only through the dev proxy, so this view is drivable via `scripts/demo.py` and not from
a deployed browser.
