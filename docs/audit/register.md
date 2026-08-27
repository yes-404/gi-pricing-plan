# Global register of open findings

One row per open finding, keyed by the requirement or artifact id it concerns. Each row
names the work item that carried it, the phase, and the decision. A finding is removed
when the close resolves it, accepts it, or re-plans it with an owner.

| Finding id | Concerns | Work item | Phase | Decision |
|---|---|---|---|---|
| The requirement or artifact id | What the finding is about | `pr-NNN`, a slice id, or a workstream id | `1a`, `1b`, `2` | `fix before close` · `carry forward with an owner` · `accept` |

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
