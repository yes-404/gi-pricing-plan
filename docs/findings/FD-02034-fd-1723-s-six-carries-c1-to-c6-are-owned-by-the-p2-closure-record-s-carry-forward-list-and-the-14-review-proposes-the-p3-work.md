---
id: FD-2034
family: finding
title: FD-1723's six carries (C1 to C6) are owned by the P2 closure record's carry-forward list, and the §14 review proposes the P3 Work
status: active
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8395, minted 2026-11-06
owner: lead
tree: ac123679   # PL 8376's head; origin/main when drafted is cded9f0e1953f2db6a6a1375892257a1a4822fc3
corrected_by: []
relates: [FD-1723, FD-2007, WK-1178]
---

# FD-2034 — the six carries of PL 8376 (FD-1723's FR-7 audit events)

*(Minted 2026-11-06 as FD-2034 from working id 8395, in the docs batch 12 PR.)*

## Finding

One finding, **six limbs, one register row** (to-lead "2026-11-05 16:50:00 GMT" item 3: accepted; batch 12 mints it). Each limb is a carry ruled by the maintainer on PL 8376's DPs (to-lead "2026-11-05 16:39:14 GMT"), **owned now by the P2 closure record's carry-forward list in the FD-2007 form**, because "a later phase names the owner" is refused: "unowned" is not a permitted state (§14); the §14 review proposes the P3 Work. **The P2 closure record quotes each limb separately; C5 is never a footnote.** The limbs, from PL 8376 @ `ac123679` (the carry table):

| Limb | What | Ruled by |
|---|---|---|
| **C1** | The rename of the four shared names (M4, O4, the metric return, P4) to `<type>.returned` | DP-8 (a) |
| **C2** | Custom Objective and Custom Metric `→ deprecated`: 6 edges, two routes, and OQ-609's selection refusal | DP-9 (b) |
| **C3** | Peril Structure `→ archived`: 3 edges, one route | DP-10 (b) |
| **C4** | FR-369's `entity_ref` form, missed by `ingestion.py:492` and the others in D0 §4(c) | DP-13 F5 |
| **C5** | **Role revocation, verdict "not started":** `revoked_at` is honoured on read (`backend/src/app/platform/rbac.py:183`, `backend/src/app/api/me.py:133`; `:190` is the `expires_at` line) and has **no writer**; with FR-350 | DP-14 (a) |
| **C6** | `traces.py:297`: no caller outside `test_traces.py`; the first route to call it owes an event | DP-14 (c) |

C2 and C3 are spec-only in the slice: a dated clause names the carry's owner (FR-154, FR-163, `02:1664`); the edges stay in `NOT_BUILT` under SL 8377's T3 guard.

## Evidence

PL 8376 @ `ac123679`, the carry table and the DPs it cites, quoted above; the rulings are the two to-lead entries named.

## Disposition

Open, owner the P2 closure record's carry-forward list; the §14 review proposes the P3 Work. **Homes proposed by the maintainer (to-lead "2026-11-05 22:04:05 GMT" item 3):** C2 and C3 together in one new P3 Work for the unreached lifecycle states (the ruling of "2026-11-05 16:39:14 GMT" meant "the P3 Work" of the carries as a class); C1, C4 and C6 to WK-679; C5 to WK-676 with FR-350, the right home for "not started". The §14 review proposes these; they are not yet rows. Event that next discharges each limb: the P3 Work's slice for it merging, or a dated acceptance. Two further items of the same plan are **not** carried here: DP-11's `retired` OQ is in SL 8377's Write set (owner the P2 carry-forward list, gate "Before Phase 3"), and the failed-certificate question is OQ-2037. Related, not yet minted (space form): PL 8376, SL 8377. Filed as working id 8395.
