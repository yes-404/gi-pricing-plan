# Global register of open findings

One row per open finding, keyed by the requirement or artifact id it concerns. Each row
names the work item that carried it, the phase, and the decision. A finding is removed
when the close resolves it, accepts it, or re-plans it with an owner.

| Finding id | Concerns | Work item | Phase | Decision |
|---|---|---|---|---|
| FR-DATA-57 (F6) | `unrun_layers` projection — Phase 2 validation-report successor | W7-4 | 2 | carry forward with an owner (Phase 2 validation-report workstream) |
| FR-DATA-52 (F7) | exposure-ordered top-20 deferral — trigger has not fired | W7-4 | 2 | carry forward with a trigger (a named exposure-ordered reader), unowned by design |
| 03 rating surface (F8) | compile, score, rate tables, deployment | — | 2 | carry forward — phase boundary |
| wf-01 §4 surfaces (F9) | bandings, Peril Structure, reconciliation | W7-5 | 2 | carry forward — phase boundary |
| Phase 2/3/4 unevidenced (F22) | FR-MODEL-6/40/82/115/121; FR-PLAT-15/23-29/31-36/49/50/56/60/61/64; FR-GOV-16/17/18/27-35/38-45; NFR-OVR-1..8/10/11; NFR-PLAT-1/2/5/6/8/9/10; NFR-GOV-1/3-7 | — | 2/3/4 | carry forward — phase boundary; owners are the later-phase workstreams named in the roadmap |
| FR-OVR-20 (F14) | `_minor` suffix rule — enforcement invisible to `req-coverage.py` | W6b-15 | 1b | fix before close — add a test naming FR-OVR-20 |
| FR-PLAT-59 (F17) | no IdP in prod — enforcement not marker-evidenced | W6b-14 | 1b | fix before close — add a marker to the repository-invariant test |
| FR-OVR-22 (F13) | route reachability — Vitest-enforced, Python-marker-blind | #136 | 1b | accept — alternative instrument (Vitest), positive control + mutation verified |
| FR-OVR-21 (F15) | §5.3 cell is prose | W6b | 1b | accept — declared-prose affordance |
| FR-PLAT-55 (F16) | browser PKCE — Vitest-enforced | W6b-10 | 1b | accept — alternative instrument (Vitest) |
| NFR-PLAT-4 (F18) | compose < 5 min — measured 27 s | W6b-14 | 1b | accept — measured, recorded |
| FR-OVR-9 (F19) | pseudonymisation — ingestion enforces; PII-guard gap has a roadmap home | W6b | 1b | accept — enforcement exists; the PII-guard gap is recorded in the roadmap |
| Cross-cutting OVR (F20) | FR-OVR-2/4/10/11/12/14/15/16/19 | W6b/W7 | 1b | accept — conventions, ADRs, audit checks |
| Measured NFRs (F21) | NFR-DATA-1/2, NFR-MODEL-1..5, 10..13 | W4/W5/W7 | 1b | accept — measured, not asserted |
| NFR-RATE-13/14 (F-W9-1) | validate-inbound-never-outbound; nthread=1 per model_call — design constraints whose measurement belongs to the scoring path | W9-3 | 2 | carry forward with an owner — the W11 scoring workstream; W8's measurements recorded (NFR-RATE-13 p99 0.070 ms, NFR-RATE-14 p99 1.626 ms) |
| FR-RATE-17/18/19/20 (F-W10-1) | Cell diffs, bulk operations, validation, CSV/XLSX import/export | W10-1 | 2 | carry forward with owners — W10-2 (diffs, bulk ops, validation: FR-RATE-17/18/19), W10-3 (import/export: FR-RATE-20) |
| FR-RATE-16 (F-W10-1-1) | seeded_from lineage metadata: implemented in W10-1 but test marker not separate (tested within FR-RATE-15 immutability suite) | W10-1 | 2 | carry forward — marker can be added when seeding logic is implemented in W10-2 |

A carried finding is written here by the work-item close checklist
([`checklists/work-item-close.md`](checklists/work-item-close.md)) and by the phase close
checklist ([`checklists/phase-close.md`](checklists/phase-close.md)).

## NT-0005 discharges, recorded 2026-08-27

Two deferred NT-0005 items are discharged rather than filed. They are recorded here so
this register is the custody home NT-0005 asked for.

- **Item (c) expired.** The `W6b-9` to `W6b-1b` dependency, which the frozen slice map's
  dependency column does not carry: `W6b-1b` shipped as PR #194 and `W6b-9` shipped its
  checks. No roadmap row is needed.
- **Item (g) is placed.** The eight open questions that sat on no decision gate —
  OQ-OVR-10, OQ-DATA-12, OQ-DATA-13, OQ-PLAT-10, OQ-PLAT-11, OQ-PLAT-12, OQ-PLAT-13,
  OQ-PLAT-14 — are all named in the `docs/roadmap.md` §10 note of 2026-08-26, among the
  twenty questions placed or recorded that day.
