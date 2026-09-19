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

## Disclosure — this finding's own id collides, and the collision is its subject

**Dated 2026-09-19. Taken knowingly and disclosed rather than silently, in the form
`RL-1075` uses.**

`FD-1078` was allocated by `python3 scripts/doc-id.py next`. That id is **already assigned**
in `docs/REDIRECTS.csv`'s legacy block, to a rating requirement:

```
F-W9-2,FD-1078,docs/audit/register.md,docs/findings/register.md,,title:FR-RATE-61
```

So the commit filing a finding about **a resolver existing somewhere other than the row that
names it** was handed an identifier that **resolves to something else, in a file the
allocator does not read**. The finding's subject, enacted by its own identifier. It was
found by the deputy, not by the author or the lead.

**The id stands.** Every id below the block's top collides equally, and hand-picking one
above it is the hand-minting `RFC-937` forbids. The lead's policy of 2026-09-19 applies
unchanged: take the allocated id, disclose the collision, and let the instrument fix land
separately. A collision decision point carries the general question; under the
resolver-merges-first rule adopted above, its ruling lands and merges before any code is
written against it.

### The population — two predicates, two different harms, neither a standing fact

**Both figures move with every id minted until the instrument fix lands**, including the
ruling that will decide this very collision, so neither is written here as a number to be
quoted later. Run them at the tree you care about.

**(i) Reuse of a reserved number — the standard's actual invariant.** `RFC-937` rule 1 is
*"n is an integer from one sequence shared by every family"*, so **a number is reused
whatever letters precede it**, and check 31 is the clause that cares. This is the predicate
that matters:

```bash
# numbers reserved by the legacy block
git show <tree>:docs/REDIRECTS.csv \
  | awk -F, '$6 ~ /^"?title:/ {print $2}' | grep -oE '[0-9]{4}' | sort -u > block.txt
# numbers live in the index, any family
git show <tree>:docs/INDEX.md \
  | grep -oE '^\| [A-Z]+-[0-9]{4}' | grep -oE '[0-9]{4}' | sort -u > index.txt
comm -12 block.txt index.txt
```

**(ii) Mis-resolution — the reader-facing harm.** The same intersection restricted to
`FD-`, where one id names two different governed things and a reader following it lands on
the wrong one. This is the narrower set, and it is what the collision *looks* like from the
outside.

**At `38033319b2654072bb8825529fc6da09f99dc788` the reused numbers under (i) are
consecutive and unbroken, running from the 1063 mark to the 1077 mark** — `CR-` ×3, `FD-`
×4, `PL-` ×4, `FD-` ×1, `RL-` ×3, in that order. **So the allocator has not produced a
single non-colliding number since the block was reserved.** Not a few unlucky ids: every
governed document this work item has minted — all four Stage 3 leaf plans this slice is
executed from, all three of today's rulings, and the checkpoint-3 closure record. This file
extends the run by one.

**A consequence for whoever rules on this.** The fix must stop **(i)** growing, not merely
prevent future `FD-`/`FD-` clashes. A fix scoped to mis-resolution alone would leave the
standard's own invariant broken and the allocator still minting reused numbers on every
document it touches.

At `38033319b2654072bb8825529fc6da09f99dc788` that block spans the range from the 1063 mark
to the 1136 mark, and the live intersection is five ids, becoming six when this file lands.

**The endpoints are named by number rather than by id token, and that is itself a fifth
instance of this finding's class.** Writing them as ids reds check 32 — *"does not resolve
in `docs/INDEX.md`"* — which is **correct and is the whole point**: they name rows that were
never materialised, so of course they do not resolve. The check cannot distinguish an id
cited *as an example of a non-resolving id* from an id cited as a reference. A document
about unresolvable identifiers is therefore the one document that cannot spell them.

### Three predicate failures while measuring it, all of the finding's own class

Recorded because a finding about instruments that answer confidently and answer the wrong
question is the right place to record its own authors doing it twice.

**First: the right count of the wrong population.** A naive intersection of `FD-` ids
appearing in *both* `REDIRECTS.csv` and `INDEX.md` returns a much larger number, but it
counts the migration's **correct** `F-`→`FD-` mappings, which are not collisions at all. The
discriminator is the `title:` suffix, which marks the rows that name a thing that was never
materialised. The predicate answered *"which ids appear in both files"* when the question
was *"which ids name two different governed things"*.

**Second: the right population, with a pattern that could not see all of it.** The
corrected predicate was first written anchored on `/,title:/` — comma-immediately-`title`.
It undercounts by seven, and **the miss is structural rather than unlucky**: seven rows
carry a **CSV-quoted** title because the title itself contains a comma, so the field begins
comma-**quote**-`title` and a comma-anchored pattern can never match it. A CSV is precisely
where quoting happens — it is the format's whole mechanism for values containing the
delimiter — so the predicate was wrong about the format it was reading.

**The bias is systematic, not random.** It drops exactly the rows whose titles are long or
awkward enough to need escaping. A sample selected by *"did not require escaping"* is not a
sample of the population.

**Neither number was a miscount.** Each is the correct count of what its pattern asked for;
they answer different questions. The disposition is to **explain the difference — never to
average them, and never to pick the one you prefer**. Both were reproduced independently
before this paragraph was written, including the seven ids in the difference.

**Third, and the sharpest: a confident zero from a mis-sorted `join`.** A third measurement
of the same intersection used `join` over numerically sorted input. `join` requires its
inputs sorted **lexically on the join field**; given a numeric sort it silently produces no
matches. It printed **0**, with no error and no warning.

**A zero is the one wrong answer that looks like good news.** A count that comes back empty
reads as "no collisions" — the most reassuring result available — and nothing about the
output distinguishes it from a clean run. It was caught only because the reader already
knew a specific id was plainly in both sets and refused to believe the absence. Without
that prior, it would have closed the investigation.

**That is three predicate failures — one per author involved — produced while measuring a
finding about instruments that answer confidently and answer the wrong question.** The
first counted the wrong population, the second could not see part of the right one, and the
third returned an absence that was an artefact of the tool's own contract. They are
recorded here, each attributed, because a finding of this class is the right place to
record its own authors committing it — and because two of the three were caught only by a
reader's prior suspicion rather than by anything the instruments said.

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
