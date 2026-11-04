---
id: FD-1983
family: finding
title: Two WK-673 deferrals of LG-1545 §13 live only in the ledger, the per-set S figures and the 690/976 per-policy maxima
status: active
created: 2026-11-03   # drafted 2026-11-03 under working id 8308
owner: auditor
tree: 55bddaf279fc73fd9b52f523fdea908d6c4aada3   # origin/main when read
corrected_by: []
relates: [WK-673, LG-1545, CR-1981, FD-1576, PL-1267]
---

# FD-1983 — Two WK-673 deferrals of LG-1545 §13 live only in the ledger

## Finding

**LOW, owner WK-673** (no price moves; the record is incomplete). Filed from CR-1981 "FD candidate
3" by the maintainer's "2026-11-03 16:03:37 GMT" entry, ruling (C), `to-lead.md`. LG-1545's §13
verdicts (the lead, 2026-10-10 01:15:46 BST; `LG-1545:361-364`) are two deferrals with an owner:

- **Limb 1 — the per-set S figures of Acceptance 20:** "deferred with an owner. Owner WK-673;
  discharged before WK-673's Work close, by the first WK-673 slice whose write set takes
  measure-attribution-cost.py to emit subset values".
- **Limb 2 — the 690/976 per-policy maxima:** "deferred with an owner. Owner WK-673; same discharge
  point and the same harness change, which also emits per-policy contributions for the two sets;
  until then 'shown not to recur' is not concluded".

No row of `register.md` carried them, so `scripts/register-owed.py` could not see them (the F41
shape `close-workstream` §5b exists to catch). At `55bddaf2` no WK-673 commit has touched
`scripts/measure-attribution-cost.py` since `e40ab532`
(`git log e40ab532..HEAD -- scripts/measure-attribution-cost.py` prints only `1aab7a21`, WK-1178's
SL-1575, per CR-1981 §5); PL-1984 names neither limb.

## Evidence

`LG-1545:361-364` (the two verdicts, quoted above); `git log e40ab532..HEAD -- scripts/measure-attribution-cost.py` as CR-1981 §5 reports it; `PL-1984` names neither limb. Source: `docs/closures/CR-01981-wk-673-close-audit.md` § Findings, candidate 3.

## Disposition

Open, owner WK-673, **deferred with an owner**, both limbs. The event that next discharges it: a
WK-673 slice that changes the harness to emit the per-set S figures and the per-policy contributions
for the two sets, before WK-673's Work close; or a dated ruling carrying or accepting the limbs.
Filed under working id 8308.

## Dated line, 2026-11-04 — carried to WK-1178

*(Docs batch 8, by the auditor, on the maintainer's ruling on CR 8310 BLOCKER (1) in `to-lead.md` "2026-11-04 10:00:29 GMT".)* **CARRIED**, owner ~~WK-673~~ WK-1178, discharge event the P3 plan review, alongside FD-1576: the per-set S figures and the 690 / 976 per-policy maxima are the attribution-cost family already carried to P3, no price moves, and a harness slice before Tue 10 Nov buys a record, not a safer price. The finding stays open on WK-1178; the Disposition above is not edited.
