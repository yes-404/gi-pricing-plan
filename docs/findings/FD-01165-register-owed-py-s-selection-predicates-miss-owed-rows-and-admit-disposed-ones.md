---
id: FD-1165
family: finding
title: register-owed.py's selection predicates miss owed rows and admit disposed ones
status: active
created: 2026-09-27
owner: auditor
tree: cddf9a6e32e6a780ac93ba769767bb602b054919
corrected_by: []
relates: [CR-1164, LG-1148, FD-894]
---

# FD-1165 — register-owed.py's selection predicates miss owed rows and admit disposed ones

Filed by the auditor on 2026-09-27, in W37-11's closing-record PR, on the lead's instruction.
The evidence comes from the lead's plan review 14 (read-only, at `cddf9a6e`). The auditor
re-read each limb at `cddf9a6e` before filing. `scripts/register-owed.py` generates the owed
list that a close or a review reads (RFC-896 P5). This finding is that its selection
predicates err in both directions. Each error hides a row from the reader or gives the reader
a row that is not owed, and neither shows in the output.

## Finding

### Limb 1 — the review predicate misses a row deferred to a plan review

`_REVIEW_MARKER = re.compile(r"§14")` (`scripts/register-owed.py:102`) is applied by
`_matches_review` to the Decision cell alone (`row.fields[4]`, `:145-146`). F73's Decision
cell (`docs/findings/register.md:114`) says *"Event: plan review 14"* and never contains
`§14`. `CR-1164` §8 defers F73 to plan review 14. So `register-owed.py review` does not list
F73, and plan review 14 must add it by hand.

### Limb 2 — the review predicate admits rows already disposed elsewhere

F97 (`:138`) and F101 (`:141`) now open *"deferred with an owner — the lead"*, and their
events are the charter investigation's first slice and the create-read-retire audit's first
slice (`CR-1164` §8). They still match `§14`. The match comes only from their original
verdict's decay clause, kept below the new decision: *"Absent an owner, decays to the next
`CLAUDE.md` §14 plan review"*. So the review list gives two rows that are not owed to the
review.

### Limb 3 — the per-work sweep cannot reach a row that names no work id

`CR-1164` §8's owed list came from `register-owed.py <id>` over `WK-697`, `W37` and `W37-1` to
`W37-11`. In that mode a row matches only when its Work item cell or its Decision cell names
the id (`_matches_work_id`, `:139-142`). F91 (`:132`) and F93 (`:134`) have the Work item `—`,
and neither Decision cell names a W37 id. So the sweep did not reach them, and they are not
in `CR-1164` §8. The auditor's own run of the same thirteen ids at `3749db65` confirms this:
neither row is in the union of 39.

A `—` Work item alone is not the cause. F70 and F73 also have `—`, and they were reached
because their Decision cells name a W37 id. **Consequence:** review 12 routed F93 *"carry
forward, unowned, into W37-11's closure record"*
(`CR-01050-plan-review-12-the-w37-6-w37-11-boundary-mid-window.md:96`). The close did not
carry it, because the sweep that built §8 could not see it.

### Limb 4 — a resolution-marker exclusion hides a residual item with no owner

The tool excludes a row whose Decision cell opens with a resolution marker, and it lists the
row under *"Excluded as opening with a resolution marker — verify"*. F28 (`:70`) opens
**Fixed**, so the review run excludes it. Its cell carries on after the opener: *"**Still
carried: P5**, because no document owns the stand-down procedure it is against — which is the
finding"*. P5 is *"Not yet fixed: no document owns the stand-down procedure"*
(`FD-00894-rfc-840-841-adoption-pilot.md:648`), and neither the cell nor the essay gives it an
owner or an event. The tool's "verify" label is the only defence, and it depends on a reader
opening the cell.

## Evidence

At `cddf9a6e`:
- `python3 scripts/register-owed.py review` exits 0. It prints *"22 owed row(s), 4 matched but
  excluded as opening with a resolution marker"*. The owed list includes F91, F93, F97 and
  F101, and it omits F73. F28, F87, F88 and F92 are the four excluded rows.
- For each Decision cell (field 4), the auditor tested for the literal `§14` and for the
  phrase `plan review 14`:
  - F73: `§14` absent, `plan review 14` present.
  - F97: `§14` at character 1289, in the decay clause.
  - F101: `§14` at character 729, in the decay clause.
  - F28: its cell opens `**Fixed**`, and `Still carried: P5` follows.
- F91 and F93 have the Work item `—`. The per-id owed union at `3749db65` is 39 rows, and it
  contains neither of them. `LG-1148` records that union under "The owed rows".

## Disposition

**Deferred with an owner — the lead** (the lead's instruction, 2026-09-27, at plan review
14). Event: the create-read-retire audit's first slice (register tooling). The fix is the
owner's choice. Options include:
- widening limb 1's predicate to the phrasings the register uses;
- limiting limb 2's match to the current decision rather than the retained text;
- a sweep for limb 3 that also reports every open row whose Work item names no id;
- a residual-item test for limb 4, so the "verify" is not left to the reader.

Related to F86, the RL-909 decay rule, and to `FD-1166`.
