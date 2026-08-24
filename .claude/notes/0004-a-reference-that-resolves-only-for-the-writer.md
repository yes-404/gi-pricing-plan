# NT-0004 — A reference that resolves only in the writer's context

| | |
|---|---|
| **Raised** | 2026-08-24, Claude — during W32-1b, after the same defect was committed ten times in one day by two sessions that were actively looking for it |
| **Status** | `open` — the rule below is a `CLAUDE.md` §13 amendment and needs maintainer acceptance. Raised and assessed, not agreed: nothing is built on it |
| **Deliverable** | **No code and no spec change.** Ten measured instances, and one mechanical rule — the ninth instance is what forced the rule into its final form |
| **Owner** | Claude records · maintainer accepts |
| **Lands in** | Proposed: `CLAUDE.md` §13, as a fourth bullet beside "NFRs are measured, not asserted" |
| **Trigger** | Before writing any count, schema name, file basename, or `Verified` date into a governed file |

---

## The defect

**A reference resolves against context the writer holds and the reader does not.** The
sentence is well-formed, reads as precise, and survives proofreading — because the person
proofreading is the person who holds the missing context.

It has two surface forms, and they are the same defect:

- **Ambiguous** — several readings, all plausible. `custom-objective.schema.json` names two
  different files depending on directory.
- **Stale** — one reading, no longer true. `twelve compared slugs`, written when there were
  twelve.

Both are a reference minus its qualifier. Which form you get depends only on whether the
missing qualifier is a *place* or a *time*.

## The ten instances, all from 2026-08-24

| # | Written | The missing qualifier | Consequence if read wrong |
|---|---|---|---|
| 1 | `generate-contracts.py` rewrote `custom-objective.schema.json` | **directory** — generated or authored? | Under the authored reading the sentence describes an **ADR-0002 violation**: the contract flow is one-way and nothing generates the authored side |
| 2 | "W32-11 takes 13 → 11" | **which 13** — `COMPARED_SLUGS`, or the authored-with-no-generated-side count? Both were exactly 13, and they move in **opposite** directions | A handoff between two sessions writes the wrong number into a skill |
| 3 | A filed plan's `grep "twelve\|fourteen"` sweep, told to fix docstrings that "still say twelve" | **which occurrences** — the sweep cannot tell the count being updated from a dated measurement, or from a different quantity that happens to be twelve | Measured on `946725f` in the plan's own declared scope: **8 hits, exactly 1** is the live `COMPARED_SLUGS` count. Four are dated historical measurements, true as written; three name the **envelope's** fourteen fields, an unrelated quantity |
| 4 | `validation-rule` appearing in both the compared tuple and the uncompared list, four paragraphs apart | **which is current** | Two stale counts (14→13, three→two) get double-counted as two independent corrections when they are one |
| 5 | `Verified: 2026-08-22` in a skill header | **which tree** | A clause cited at `:1047` on `main` sat at `:1058` in a peer's tree the same day |
| 6 | "nothing between `5f915d5` and `946725f` moved a contract **shape**" | **shape = the file, or its contents?** | Contents moved (4 files); membership did not. The loose reading reaches a phase reviewer as evidence that contracts do not drift — the exact opposite of what `OQ-PLAT-10` is filed to ask |
| 7 | A filed plan's docstring: the arm set is the same "whether built from a `discriminator.mapping` or from **four** `if`s" | **measured on which tree** — the authored `model-spec` has **three** `if`s carrying four values | A false number is copied verbatim into live code by an executor correctly refusing to edit a frozen plan |
| 8 | This note's own first draft: "corrupts 4 lines, fixes 1" | **which tree** — carried from recollection | Measuring gave 8 and 1. Caught one commit before shipping |
| 9 | "roughly twelve assertions across `test_validate.py` and `test_catalogue.py`" | **the scope, not the number** — "across X and Y" reads as a complete enumeration. Measured on `1af0e9a`: 13 assertions, and a **third** module the sentence omitted, `backend/tests/test_api_datasets.py` | The count was near enough to survive checking. **A reader who verified the number would have confirmed it and still been misled**, then scoped a decision's blast radius to two files out of three |
| 10 | "`OQ-PLAT-14` is now unconditional — **take it**" | **the verb's object** — an id's *availability* was confirmed and phrased as an instruction to *consume* one | Neither a count nor an enumeration: a verb applied to the wrong noun. A permanent requirement id, allocated once, **cannot be un-allocated** (`CLAUDE.md` §5). Cost one message because it was asked about rather than assumed |

## Why this is not a carelessness finding

Instance 6 was committed **inside the sentence cataloguing instances 1 through 5**, by a
session that had the taxonomy open in front of it. Instance 7 was committed by an executor
applying a *correct* rule — a filed plan is frozen at its date and is never edited to agree
with today's repository — one file too far, into a docstring that is not frozen.

So the mechanism is not inattention. The writer holds the disambiguating context, which
makes the ambiguous word read as precise **to them**, at the moment they check it. Re-reading
is performed by the one reader guaranteed to resolve it correctly. That is why care does not
scale here and a mechanical rule does: care was applied at maximum, by two sessions, and
produced instances 6 and 7 anyway.

## The rule

The obvious rule is *a count carries the tree it was measured on*. **Instance 9 defeats it**,
and that is why it is worth writing this note rather than a one-line reminder. There the
count — "roughly twelve assertions" against a measured 13 — was near enough to survive any
check a careful reader would run. The false part was the **noun**: "across `test_validate.py`
and `test_catalogue.py`" reads as a complete enumeration, and a third module was missing. A
reader who verified the number would have confirmed it and been misled anyway, then scoped a
decision's blast radius to two files out of three.

So the rule is about the **scope**, and the quantity is only the part that happens to be easy
to check:

**Measure the scope, not just the quantity — and carry both.**

- a **count** carries the tree *and the corpus it counted over* — not `13`, but
  `13 assertions across the three modules that assert on it, measured on 1af0e9a`
- a list introduced by *across*, *in*, *the N files that* is an **enumeration claim**, and is
  re-derived by a command, never by recall
- a **schema or contract name** carries its directory, always in full path form
- a **`Verified` date** carries the tree, not just the date
- a word with two scopes — **`shape`, `slug`, `contract`, `variant`** — says which it means
- a **claim copied from a filed plan into live code** is re-measured first; the plan stays
  frozen, the correction lands in the code and in the commit message
- **an availability is not an instruction.** Instance 10 is the sub-kind that is neither a
  count nor an enumeration: the noun was right and the *verb* was wrong. Confirming that an
  id is free and telling someone to consume it are one sentence apart, and only one of them
  is reversible
- **a `grep` proposes the candidate set and never the edit set.** The sweep in instance 3 is
  a perfectly good discovery command — it does find the one line that must change. What it
  cannot do is decide per hit, and the plan's step pairs it with prose ("some docstrings
  still say twelve") phrased as if the match set were the answer set. The instruction to
  avoid is not the grep; it is treating its output as a verdict

The test for whether a sentence needs this: **would it still resolve for a reader holding
none of your open context?** Not "is it true" — every one of the ten was true, or was
believed true on evidence, and several were true in the only reading their author could see.

## Where this connects to an existing rule

`CLAUDE.md` §13 already says **enforcement is proven on deliberately broken input** — a check
that has never printed a failure has not been tested. The generalisation this note asks for
is that the rule governs **verification steps, not only tests**. A `grep -c` returning `1`
proves nothing unless it returned `0` beforehand; a sweep that "found nothing to change"
and a sweep that silently matched the wrong lines are indistinguishable from their output.

That is the same reasoning `NT-0003` used for duplicated status: the copy nobody re-derives
is the one that gets read first.

## What was actually done about each

Instances 1, 6 and 7 were **corrected in their own commits**, not amended into the original,
so the record of what was believed survives (`CLAUDE.md` §0). The clean W32-11 diff is the
control case: that session changed exactly one of the eight hits, and it did so **without
running the sweep at all** — it had measured the count independently. Same answer either way,
which is the point: the measurement is what produced it, and the grep would have been sound
had each hit then been decided rather than accepted. Instances 2, 4 and 5 were
corrected in the handoff before either session wrote to a governed file. Instance 3 was
**not executed**: the plan's sweep was measured first and run selectively.

Instance 8 was caught by this note's own drafting: the row for instance 3 first read
"corrupts 4 lines, fixes 1", carried from recollection with no tree beside it. Measuring gave
8 and 1. A note proposing that counts carry their measurement was one commit from shipping a
count that did not. Instance 9 was caught the same way, by the other session, in the diff it
was about to merge.

## Open, and deliberately not decided here

Whether `.claude/skills/contract-guard/SKILL.md` should restate a raw count at all.
`COMPARED_SLUGS` in `backend/tests/test_contracts.py` owns that number; a prose copy in a
skill is the `NT-0003` duplication pattern, and dating the copy mitigates staleness without
removing the duplication. Recorded rather than resolved — it is a skill-design question, and
this note is not authoritative (see the README).
