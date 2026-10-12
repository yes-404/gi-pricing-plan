---
id: FD-1658
family: finding
title: 06 §5.1 declares GET/POST /api/v1/roles, POST /api/v1/role-assignments and POST /api/v1/break-glass, and none is served: the machinery is at the service layer only
status: active
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-676, SL-1527, FR-342, FR-344, FR-345, FR-349, FR-350]
---

# FD-1658 — three declared role routes with no HTTP route

*(Minted 2026-10-12 as FD-1658 from working id 9801, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Found by SL-1527 (LG-1647) while widening the demo seed so the journey has a principal who is neither submitter nor author. Filed from the maintainer's (by delegation) entry "2026-10-12 01:30:34 BST — SL-1527 condition 4: the role-routes FD → owner WK-676 (P3), LOW; CR-823 Q2(a) DECIDED as its recommendation" (`to-lead.md`, a local channel file, cited by its header). The entry's text for this finding, verbatim: *"06 §5.1 declares GET/POST /api/v1/roles, POST /api/v1/role-assignments and POST /api/v1/break-glass; none is served; service layer only (rbac.py). Demo workaround: SL-1527's seed widening (to-lead 23:27:48)."*

## Evidence

- `docs/specs/06-governance.md` §5.1's route table declares `GET`/`POST /api/v1/roles` (FR-344), `POST /api/v1/role-assignments` (FR-345) and `POST /api/v1/break-glass` (FR-349). A caller who copies the table gets a 404 on all three.
- The machinery exists at the service layer: `rbac.py`, `RoleRow`, `RoleAssignmentRow`.
- `docs/closures/CR-00823-plan-review-5-at-wk-664-s-close.md`, lines 55 to 58 (Q2(a)), raised this and recommended recording the routes as spec-ahead-of-phase, with a dated note in 06 §5.1 and no route built at that close.
- Owner. `docs/roadmap.md` `WK-676` ("Full scoped RBAC, custom roles, break-glass", phase P3) owns 06 FR-342 to FR-349, which includes FR-344, FR-345 and FR-349. The entry rules the owner is WK-676, **not** WK-1178.
- No membership route is specified (FR-350 is Phase 3), so there is no second finding.

## Finding

**Severity LOW (the maintainer's (by delegation), entry "2026-10-12 01:30:34 BST").** Nothing is mispriced and no phase-2 requirement depends on a route: the demo's principal set is provisioned by SL-1527's seed widening, one definition shared with the journey fixture. The cost is a spec table that promises three routes a reader cannot call.

## Disposition

**Owner: WK-676 (Phase 3).** `CR-823` Q2(a) is **decided** as its recommendation: spec-ahead-of-phase. The decision is recorded by one dated note in 06 §5.1, under the route table, naming WK-676, the entry above and this finding. No route is built in Phase 2 (`CLAUDE.md` §0: a later phase's capability is a spec change only). Event that discharges it: `WK-676` serving the three routes. Filed by the executor from the entry, 2026-10-12.
