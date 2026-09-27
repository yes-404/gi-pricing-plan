---
id: FD-1023
family: finding
title: RL-909's decay rule has no faithful check, the wrong population, and a blind backstop
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F86.md
---

# F86 — RL-909's decay rule has no faithful check, the wrong population, and a blind backstop

**Raised** 2026-09-02 by the lead, from the acceptance-item sweep's `CANNOT_DETERMINE` bucket.
Phase 2. Evidence gathered by the sweep's author on request; the verdict is the lead's.

**Three limbs, one defect.** Limbs 1 and 2 would be survivable on their own. **Limb 3 is what
makes them live**, because RL-909's own text names the review as the fallback when the check
does not fire — and the tool that builds every review's agenda cannot see the shape either.

## The rule

RL-909 Text B (`docs/rulings/INDEX.md#2026-08-30-nt-0015-q1-q5-rulingsmd`), copied into
`docs/findings/register.md`'s own header:

> An unowned row must name the event that next confirms or assigns its owner. Absent a named
> event it decays to the next `CLAUDE.md` §14 plan review, which must give it a disposition
> rather than merely list it; a row that reaches a review and leaves it unchanged is a review
> finding, not a register one.

## Limb 1 — the check enforces a length proxy, not the rule

`check_unowned_decay` (`scripts/register-lint.py:331`) selects on `_UNOWNED` (`:93`,
`re.compile(r"\bunowned\b", re.IGNORECASE)`) and then passes any cell of at least
`_UNOWNED_MIN_LEN` (`:105`, `40`). Its own comment at `:103-104` states the substitution
plainly: *"a cell long enough to say more than the bare disposition + 'unowned' is presumed to
name something; a bare stop is presumed not to."*

**Presumed, not verified.** A cell naming no event whatever passes if it is verbose. **19 of 82
rows carry the marker and the check reports zero violations across all of them**, every one
clearing 40 characters. A check that reds on nothing in its whole live population has not been
tested against the rule it is named for, whatever its fixtures show.

**Read against Text B's actual words, the 19 are not alike:**

| Shape | Rows | Count |
|---|---|---|
| Names an owner-assignment event, plainly | F77 | 1 |
| Complies via Text B's own decay fallback, quoted | F74, F75 | 2 |
| Partial: ties ownership to a future decision point, non-committally | F52, F53, F58 | 3 |
| Names a **finding-discharge** event, not an **owner** event | F65, F66, F69, F72, F73, F79 | 6 |
| Names no event at all, and does not invoke the fallback | F45, F47, F54, F55 | 4 |
| Resolved — the marker match is stale (limb 2) | F50, F51 | 2 |
| Does not fit Text B's model: *"unowned by design"*, not transitional | F7 | 1 |

## Limb 2 — the population is measured wrong, not merely policed weakly

`_UNOWNED` matches **F50 and F51**, both of which carry `***Resolved 2026-08-30***` later in the
same cell. The regex cannot distinguish *unowned* from *was unowned, now resolved*, so the check
counts rows that are not in the state it exists to police.

**This is the worse of the first two limbs**, because it is invisible from the count in either
direction: a wrong population and a right one both report a number, and nothing in the output
says which was measured. It is the same class as `F64` at a different layer.

## Limb 3 — the backstop cannot express the shape, so the fallback never fires

Text B's fallback is decay to the next §14 review. **The tool that generates every review's
agenda is structurally blind to the rows that need it.** At `24193dd`:

- `_REVIEW_MARKER = re.compile(r"§14")` (`scripts/register-owed.py:97`)
- `_matches_review` returns `bool(_REVIEW_MARKER.search(row.fields[4]))` (`:140-141`) — the
  Decision cell, and nothing else.

**A row that names no event names no review either.** The predicate can never surface the exact
shape Text B's fallback exists for, on any run, for any review. So three reviews passing over
these rows is **one defect reflected three times, not three independent misses** — the
distinction matters, because three misses invite asking reviewers to look harder and one blind
tool does not.

## What is live today, measured

**Three rows are in breach of Text B's fallback**, filed before a review that never mentioned
them. Filing commits and review commits, with times:

| Row | Filed | Review 9 `daa6fbe` 08-30 12:01:40 | Review 10 `18831bd` 08-30 22:20:43 | Review 11 `fbf483e` 08-31 16:17:27 | Mentioned in `plan-reviews.md` |
|---|---|---|---|---|---|
| F45 | `721fe67` 08-30 11:29:09 | predates | predates | predates | **none** |
| F47 | `721fe67` 08-30 11:29:09 | predates | predates | predates | **none** |
| F54 | `e9b5338` 08-30 19:20:05 | after | predates | predates | **none** |
| F55 | `b749acb` 08-30 21:25:36 | after | predates | predates | review 10 §5c, dispositioned `eef1c95` 08-31 10:28:11 |

**F55 is clean and is the most informative row here.** It got substantive engagement and a dated
register amendment before review 11 ran. **But it does not carry the `§14` literal either** —
verified at `24193dd`, all four rows return zero for it. So the mechanism's detection rate on
this shape is **zero of four**, and F55 was caught by a person reading review 10's own unrelated
topic and connecting it. That is the *enforced by vigilance, not by mechanism* mode the
register's own motivation already names as insufficient.

## Limb 3, measured rather than argued — `register-owed.py review` at `2c2535b`

Run on a clean tree, because the tool refuses a dirty one (RL-912). **12 of 83 rows surface.**

| Row | Surfaced by the review agenda? | Why |
|---|---|---|
| **F86** (this finding) | **yes** | its Decision cell names its owner-assignment event and carries the `§14` literal |
| **F74** | **yes** | invokes Text B's decay fallback, quoting the clause |
| **F45** | **no** | names no event |
| **F47** | **no** | names no event |
| **F54** | **no** | names no event |
| **F55** | **no** | names no event — and was dispositioned anyway, by a person |

**Both controls are present**, which is what makes this a measurement rather than an absence: the
tool surfaces 12 rows including two of the shapes Text B sanctions, and surfaces none of the four
that need the fallback most. A predicate that returns nothing would have produced the same
"invisible" reading for every row — and did, on the first attempt, when the tool refused the
dirty worktree and every row read as invisible including the two that are not. **An empty output
parsed for absence is a confident false negative**, and it confirmed the hypothesis for three
rows by accident while being wrong about two others.

## A passing test holds limb 1 in place — the `_restructure_roadmap` pattern again

**The defect is not merely unenforced. It is defended.**
`tests/test_register_lint.py:160` — `test_resolved_used_in_prose_about_something_else_is_not_a_false_positive`
— asserts `_lint(tmp_path, _table(cell)) == []` on:

> `carry forward — unowned, needs its own authorisation. Recorded rather than fixed because the remedy is wide.`

**That is F45's own shape**, and the test's docstring names it: *"Two real register rows (F26,
F45) tripped an earlier, cruder version of this check on exactly this shape."*

**The test's purpose is legitimate** — it guards against `resolved`/`fixed` appearing in ordinary
prose being mistaken for a row's own resolution annotation. **Its assertion form is the problem**:
`== []` asserts *no failure from any rule*, so it silently pins the absence of the decay rule
alongside the presence of the property it was written for. **Fix limb 1 and this test goes red**,
and the tempting repair is the fixture rather than the code.

**This is exactly W37-5b's `_restructure_roadmap` finding in a second place**: there, a test
expecting `_restructure_roadmap` to *create* `docs/roadmap.md` encoded a destructive overwrite,
and the fixture was corrected rather than the behaviour it described. Here a blanket `== []`
encodes an unenforced rule. **A test written for property A that asserts an empty failure list
locks in the absence of every property B**, and nothing about it looks wrong.

**Remedy, and it is not "delete the test":** assert the *specific* rule it is about — that no
resolution-annotation failure is raised — rather than that nothing at all is. Then it keeps
guarding its own false positive and stops guarding the defect.

**RL-910 is where this became invisible.** Its §3 acceptance item names three deliberately
broken fixtures, the third *"an unowned row naming no decay event"*, and the sweep classed the
ruling `CONSTRUCTIBLE` on the evidence that `check_decision_grammar`,
`check_resolution_annotation` and `check_unowned_decay` are *"exactly the three named"*. **All
three exist. RL-910's own text is sound — it states an observable violation.** What the
fixture actually exercises is `carry forward — unowned.`, **24 characters**, a bare stop that the
40-character proxy catches. **The live population contains no bare stops**; all 19 rows are
verbose. So the fixture proves the proxy fires on the easiest possible case and nothing more —
a positive control that passes because of what it misses.

## Not covered by any existing row

**`F64`** was a row-*discovery* bug in `parse_register` — rows never examined at all — fixed and
closed at `f99b55d`, reopening only on a regression in blank-line handling. **`F79`** is about
row-*accounting*: whether every discovered row reaches some bucket, checked by comparing totals.
Both were read in full rather than by summary. Neither reaches whether an individual check's
predicate is faithful to the rule it is named for.

## What a check would have to assert, and its stated limit

**The violation, in RL-860's form:** an unowned row whose Decision cell names neither a
sentence tying a future event to naming, assigning or confirming an **owner**, nor the literal
decay clause.

**This cannot be made fully mechanical, and the finding says so rather than pretending
otherwise.** The real distinction — *this event resolves who owns the row* versus *this event
resolves the finding* — is reading comprehension, not lexis. A narrower predicate can still be
satisfied by a sentence mentioning an owner without committing to one.

**It is worth building anyway.** The current check reds on **nothing**; a narrower one reds
immediately on F45, F47 and F54. The improvement is from zero to three, not from three to
perfect, and **a partial check that names its own blind spot is a different object from a proxy
that presumes.**

## Falsifiable

Discharged when all three limbs are addressed: a predicate that reds on a row naming no event,
proven on the three live rows; a population that excludes resolved rows, proven on F50 or F51;
and a review-agenda predicate that can surface a row naming no event, proven on F45. **Not
discharged by the three rows receiving owners** — a correct value reached by hand leaves the next
row unprotected, which is the same reasoning `F84` was ruled on. Re-opened if any check in this
family is found to select on a proxy without stating in its own output which population it
measured.
