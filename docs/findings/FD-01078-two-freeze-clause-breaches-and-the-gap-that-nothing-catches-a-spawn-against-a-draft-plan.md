---
id: FD-1078
family: finding
title: Two freeze-clause breaches on PL-1070, and the gap that nothing catches a spawn against a draft plan
status: active
created: 2026-09-19
owner: lead
tree: 38033319b2654072bb8825529fc6da09f99dc788
corrected_by: []
relates: []
---

# FD-1078 — Two freeze-clause breaches on `PL-1070`, and the gap that nothing catches a spawn against a `draft` plan

**This finding's content is the lead's**, filed against the lead's own conduct. It was
landed in the repository by the W37-7 executor, which could write to the branch where the
lead could not; authorship and responsibility are the lead's.

## Finding

`PL-1070` carries a freeze clause at `:74`:

> No executor is spawned and no branch beyond this plan draft exists until DP-7-1 carries a
> resolver.

**That clause was breached twice on 2026-09-19, in two different ways.** Both are recorded
here in the order they happened, untidied, because the sequence is the evidence.

### First breach — 2026-09-19 13:24:42 BST

The lead spawned the W37-7 executor while DP-7-1 had **no resolver anywhere**:
`grep -rln 'DP-7-1' docs/` returned only `PL-1070` itself, meaning the ruling existed solely
as a channel message. `CLAUDE.md` §12 requires that every decision land as a dated artifact,
*"never in chat"*.

The executor quoted the clause back in its first message and declined to write an owner
value into a governed record on the strength of a message. **The lead filed that as a
finding against the plan's freeze state rather than acting on it as a prohibition on the
lead** — reading a clause about the *act of spawning* as though it governed only the plan's
recorded state. Halted at 13:35 on the deputy's ruling: the clause **names the act, not the
work**, so "the tasks in flight do not touch DP-7-1" is the plan-independence argument this
stage has already refused twice.

### Second breach — 2026-09-19 13:59 BST

The lead resumed the executor on the strength of `RL-1075` **existing as a filed record**,
while `PL-1070` still read `status: draft` and DP-7-1's `Resolved by` cell still read
`_open_`. **The clause names the plan's own row as the gate, not the existence of a ruling
elsewhere.** Ruled CONTINUE with conditions; the commit landing this finding is condition
(c).

The two breaches share one shape: **a resolver existing somewhere other than the row the
plan names.** In the first it existed only in a chat message; in the second it existed as a
merged record while the row it was supposed to fill was still empty.

### The gap that outlives both

`scripts/audit-docs.py` check 33 fails a `PL-` marked `active` that still carries an open
blocking decision point. **Nothing catches the opposite and more dangerous case: a lead
spawning an executor against a plan that is still `draft`.**

The enforcement covers **the record's state**, not **the behaviour the record forbids**. A
plan can therefore sit correctly `draft`, pass every check, and have work executing against
it — which is exactly what happened here, twice, with the gate green throughout. The
executor's reading of its own plan was the only thing that caught it on either occasion.

This is the same class as two other findings raised the same day: an enforcement declared in
prose and mechanised nowhere. It differs in that the thing unenforced is not a document's
content but an actor's conduct, which no tree-snapshot tool can observe.

## Evidence

- `PL-1070:74`, the clause, quoted above verbatim.
- This repository's own history: the executor's branch carries commits timestamped inside
  both windows, and `PL-1070` at `origin/main` read `status: draft` with DP-7-1's
  `Resolved by` cell `_open_` throughout both.
- `#794` merged as `3803331`, its sole parent `7d5d6e0` — the merge that made `RL-1075`,
  `RL-1076` and `RL-1077` citable at a reachable tree, and which **followed** the resume
  rather than preceding it.
- Channel entries of 13:32:15 (the executor's first quotation of the clause) and 14:04 (the
  lead's disclosure of the second breach).
- The negative half, which is what makes the gap a finding rather than an incident:
  `scripts/audit-docs.py`'s check 33 clause covers *"a `PL-` `active` with an open blocking
  decision point"*. There is no converse clause, and no check in 30-39 reads agent
  behaviour at all.

## Disposition

**Accept, with a standing rule**, owner the lead.

The rule adopted, which addresses the shape both breaches share rather than either
instance: **the resolver's pull request merges *before* the executor is resumed on dependent
work, and the cell is filled *in the resume commit*.** A ruling that exists anywhere other
than the row the plan names does not satisfy a clause that names that row.

**The mechanical gap is not closed by this finding and is not claimed to be.** Nothing
proposed here would catch a spawn against a `draft` plan; a tree-snapshot checker cannot
see a spawn. Recording it as an accepted, open gap is deliberate — the alternative is a
finding that claims a fix it does not have, which is the failure mode this work item
exists to remove. It decays to the next `CLAUDE.md` §14 plan review, which must give it a
disposition rather than list it.
