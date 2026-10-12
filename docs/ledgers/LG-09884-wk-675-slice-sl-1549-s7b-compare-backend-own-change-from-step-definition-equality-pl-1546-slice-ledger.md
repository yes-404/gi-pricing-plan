---
id: LG-9884
family: ledger
title: WK-675 slice SL-1549 — S7b, compare backend: own_change from step-definition equality (PL-1546), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-675
slice: SL-1549
plans: [PL-1546]
corrected_by: []
relates: [PL-1546, PL-1286, SL-1549, SL-1367, SL-1340, RL-1261, OQ-1231, FR-262, FR-219]
---

# LG-9884 — WK-675 slice SL-1549: S7b, compare backend

*(Working id 9884, reserved by the lead. The id is minted at the merge turn; until then every citation of this record is by working id.)*

**GO:** the lead's from-lead entry "2026-10-12 05:34:34 BST — LANE C READINESS (template, read-only at 604ea084): S7b SL-1549 (compare backend; own_change from step-definition equality) — needs MET (SL-1367 merged 13a02bba #1282; RL-1261 active); SCOPE NOTE: SL-1340 closed (#1263) so R7b.1's namespaced step_id limb is IN scope; backend-only; … GO S7b … LG working id 9884 RESERVED … Gate queues after SL-1669, SL-1543, SL-1622." Authority: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-11 10:39:56 BST" items 2–3 (lane C order, S7b third after SL-1367; a backend WK-675 seat may run beside S5 under RL-1445 item 2), "2026-10-11 20:52:24 BST" (#1282 SL-1367 read-back verified; unblocks S6/S7b/S7) and "2026-10-12 05:32:12 BST" (lane C readiness for S7b as a no-gate candidate).
**MERGE-ACK:** not yet given.

## Tasks

Base: `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`. The activation commit is the branch's first.

### Scope

`PL-1546` order table row 3: "SL-1549 — S7b: Compare backend | `PL-1286` S7b row, plus R7b.1 | `03` §4.10 `StepChange.own_change`; §3.8: FR-262 (backend limb) | `RL-1261` (met); **`SL-1367` merged first**". R7b.1's namespaced-`step_id` limb is in scope (`SL-1340` merged, #1263). `RL-1261`: `own_change` is true exactly when `diff_algorithms(base_alg, comparison_alg).changed_steps` holds an entry for the `step_id` whose `field` is not `note`; added and removed steps stay true. Backend-only: no `frontend/` file is touched.

### Task list

(entries follow)

### Gate

Not yet run.

### Audit

Not yet written.

### Build log

- 2026-10-12: activation commit. `SL-1549` draft→active.

## PRs

(none yet)
