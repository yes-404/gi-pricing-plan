---
id: LG-9975
family: ledger
title: WK-1178 slice SL-1541 — compile refuses a model_call whose feature_map misses the pinned model's required inputs, per component for a Peril Structure (FR-240) (PL-1540 slice ledger)
status: active
created: 2026-10-10
owner: executor
tree: 14fa6fb3d5b7097a829343e38cb5f20afbd0d2e2
phase: P2
work: WK-1178
slice: SL-1541
plans: [PL-1540]
corrected_by: []
relates: [PL-1540, RL-1523, RL-1445, RL-1263, FD-1424, FR-240, FR-222, NFR-499, WK-1178]
---

# LG-9975 — WK-1178 slice SL-1541: compile refuses a short `feature_map`

*(LG-9975 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1541` from PL-1540, base `origin/main` `14fa6fb3d5b7097a829343e38cb5f20afbd0d2e2`. Times are BST
(`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md`, "2026-10-10 21:41:05 BST — RL-1445 CAP: AMENDED by dated line (counting unit = gate or measurement, with guard rails); GO SL-1541 (WS-1 (a)); OP-1503-1 (a); SL-1575 noted", item 2: "GO SL-1541 (PL-1540; A-4 need 4a), needs 1–5 MET as you quoted. Lane: MERGE serialises after SL-1557 on compile_bundle; authoring runs in parallel. FR-240's anchor: the executor re-counts at its base under RL-1523 :148, and a count ≠ 1 is a STOP. WS-1 (a) ADOPTED: test_quote_input_raise_sites.py joins the write set for ONE census entry ("rating/compile.py","check_model_call_coverage"), red-first, its input-free reason quoted. The second of SL-1541 and SL-1557 to merge reconciles _INPUT_FREE by content. If SL-1600 merges first, SL-1541's new raise uses its InputFreeError marker (DP-2 (c)), and its message is checked input-free at the ACK (NFR-499)."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1540` (leaf plan, WK-1178). Roadmap row `SL-1541` — "WK-1178 slice — compile refuses a `model_call` whose `feature_map` misses the pinned model's required inputs". Requirements: `03` FR-240 (as RL-1523 amends it), FR-222, FR-255 (the category these faults no longer reach), `02` FR-188. Write set: PL-1540 §"Write set", plus (WS-1 (a)) the one census entry in `packages/pricing-core/tests/test_quote_input_raise_sites.py`. Lane: authoring beside SL-1557 (WK-675 S3); the MERGE serialises after it on `compile_bundle`.

### Task list

- [x] Task 0 — preconditions (below).
- [ ] Task 1 — the reds (Acceptance 1–3, 6, 13 first test) and WS-1's census red.
- [ ] Task 2 — the check (Acceptance 1–6, 13).
- [ ] Task 3 — end to end, existing suites (Acceptance 7, 11).
- [ ] Task 4 — the FR-240 text (Acceptance 8).
- [ ] Task 5 — Acceptance 9, 10, gate (Acceptance 12), closing acts.

### Gate

Not yet run. Owed: one full two-half gate in gate-1, on the lead's "gate slot granted" for the head.

### Audit

Not yet given.

### Build log

#### Task 0 — read 2026-10-10 23:38 BST at base `14fa6fb3`

- `git grep -n "def required_model_inputs(" -- packages backend/src`: one hit, `packages/pricing-core/src/pricing_core/modelling/factors.py:338`. **Task 0a skipped.**
- Reuse mapping: `compile_bundle`'s `resolved_pins` (every pin, then every component by `setdefault`).
- FR-240 anchor, `git grep -cF` in `docs/specs/03-rating-engine.md` at this base: RL-1523's original string `The message names the step and the rung.)* |` = 0; the last amendment's closing sentence `(SL-1466, FD-1456). |` = **1** (row :138). Not a STOP (RL-1523 :148–154 limb 2, the last amendment now being RL-1459's).
- Status flips in the first commit: `PL-1540` `draft → active`, `SL-1541` `draft → active`.

## PRs

None yet.
