---
id: CR-788
family: closure
kind: review
title: Plan review 4 — at WK-692's close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-24
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 4 — at WK-692's close, 2026-08-24

`CLAUDE.md` §14 requires a plan review at **each workstream close**. This is the fourth; the
procedure is `.claude/skills/phase-review`. **The output is a proposal, never a change** —
every recommendation below needs a dated maintainer acceptance line before it binds. Findings
about Phase 2 or later are **spec changes only** (§0's table).

**1. Completion — not re-derived, because a fresh audit already covers it.**
The WK-692 closure record immediately below is hours old and derived its scope from the
specification before opening a source file: **27 requirement ids across 12 slices**, of which
**26 are delivered with a marker** and **1 carries a §13 verdict** (NFR-488, *delivered
but untested*). The full gate ran clean at `60f6e46` — thirteen commands, all exit 0. The
skill is explicit that re-deriving the same numbers from the same sources *"would have looked
like work and confirmed nothing"*, and review 2 set that precedent. **No change proposed.**

**2. Omission — the workstream boundary was drawn by subject matter, and remainders are now
booked by screen.** The WK-692 row describes the workstream as *"everything in Phase 1b that is
not a browser"*. Each later slice booked what it could not finish onto the row that owns the
**screen**, because that is the row a reader looking for "thresholds" would search. **`W6b-13`
— a WK-664 slice titled "Rule set threshold editing" — now carries four booked items, three of
them backend.** No single booking was wrong; the sentence aged into a false partition, the
same mechanism as a frozen dependency column ageing into a false *ready*. **The sentence and
the 27-id table disagree in both directions** — `W6b-13` is work the sentence disclaims and a
WK-664 row owns, and the modelling PII guard is work the sentence claims and the table does not.
Neither is a safe restatement of the other. **Proposed:** the WK-692 row is *not* amended in that
respect — it records what the split intended on 2026-08-22 and rewriting it destroys that —
but the phase plan should state that **the slice map determines slices and the scope sentence
only describes them**. Separately, **WK-690 owns four requirements while its scope row describes
one capability**; WK-690 is Phase 2, so that is a **spec change only**.

**3. Skills and research — the gap analysis re-run; both indexes complete.** All 43 skill
directories have a README row and all 7 agent files are named; the two README names with no
directory are §12's required refusal records, not defects. Three gaps were found, and per §12
a known-wrong or missing skill is fixed in the same session — precedent set by review 3's own
Q3, and §14's "proposal, never a change" governs **the plan**, not the skills.

| Gap | State |
|---|---|
| (a) Validating a gate whose passing state is **empty output** — stated nowhere; the nearest cousin was `contract-guard`'s two-empty-maps case | **Fixed in this commit** — `close-workstream` gains the control-script procedure and its four rules, verified against the run that gated this record |
| (b) *"A delegated gate must report the tree it ran in"* existed as a **finding** and never as a **procedure** | **Fixed earlier** (`caa5bee`) — `gate-runner` now carries it |
| (c) The shared git stash stack, stated only in a *domain* skill and contradicted by a vendored one | **Fixed earlier** — `git-hygiene` now carries it. The vendored `testing-strategy` is **not** edited: it is not wrong upstream, only wrong in this repository's conditions, so §12 makes it a recorded caveat |

**Two further candidates, booked rather than fixed**, because fixing them at a close is the
scope creep the standard warns against: concurrent slices needing a database each, absent from
`python-test`, `dev-commands` and `reproducing-ci-locally`; and *a slice that moves a measured
figure owes a re-read to every skill quoting it*, stated inside the one skill it protects and
nowhere general.

**4. An accepted proposal that was never built — and the reason it drifted is question 5.**
**`scope-audit.py --params` was accepted 2026-08-22 and does not exist.** Review 3's own words
were that *"a wrong parameter is invisible to all three axes — that is not an oversight in this
audit, it is a hole in the instrument, and it is the single change most likely to prevent a
repeat"*, and it was accepted per-line the same day. Verified at this close: the argument
parser declares `module`, `--sections`, `--extra`, `--endpoints`, `--catalogue`, and
**`grep -c params scripts/scope-audit.py` returns 0**. **Proposed:** give it an owner. The
change review 3 called the single most valuable one was accepted into no row at all.

**5. Shape — an acceptance is not an assignment, and that is the recurrence.**
Review 3 had five accepted proposals; **W32-1 delivered three of them in one commit, all three
assigned to WK-664**, verified by file-addition and `-S` history rather than recollection. Read
one way that is a slice being helpful. Read as a pattern it is the same defect as (4): **an
accepted proposal with no owning row is executed by whoever happens to touch the area next, or
by nobody, and both outcomes look identical in the plan.** One produced three early
deliveries; the other produced `--params`. **Proposed:** every accepted §14 proposal gets an
owning row in the same edit that accepts it, or is explicitly marked unowned.

**Three instrument findings from the same review, each verified against an artifact:**

- **Corrections are unreviewed writes.** A correction reads as already-checked and receives
  *less* scrutiny than the text it replaces; one commit here fixed three rows and broke a
  fourth. The sharpest form: **an exoneration is the one correction its recipient has no
  incentive to check**, and two of the eight instances in the closure record below are
  corrections of corrections.
- **The §0 correction convention manufactures its own false positives.** Dated correction
  prose accumulates inside rows that later readers grep as current assertions, and a struck
  sentence keeps living in any code comment that quoted it verbatim. Raised as an instrument
  question, **not** a request to stop recording corrections.
- **An accidental gap in a permanent-id sequence is a collision invitation, and §5 does not
  forbid it.** `9ab14d6` filed `OQ-649`, `-11` and `-13`, skipping **12** with no
  reservation and no note; §5 forbids renumbering and says nothing about holes. **This one is
  mine.** It closed harmlessly — W32-7 filed `OQ-652` and no duplicate exists in history —
  but by luck, not by rule. **It survived only because the FR-396 verdict rule refused to
  pin a number**, requiring *"a new `OQ-PLAT` question, whatever its number"*: an unnumbered
  condition tolerated a sequence defect that a numbered one would have turned into a false
  failure on a correct slice.

**No change** is proposed to the phase boundaries, to Phase 1b's exit criterion, or to
Phases 2–4. Nothing this review found argues for re-cutting them; every finding is an
ownership or instrument defect inside the existing shape.

**Maintainer acceptance: accepted as proposed, 2026-08-29.** Each proposal below binds from
that date. Recorded per proposal rather than as one blanket sentence, on review 3's own
reasoning at line 214 — *"a single 'accepted' over five proposals leaves no way to tell later
which of them anyone actually read."* Review 4 has three proposals and no consolidated table,
so they are enumerated here from the questions that raised them.

- **Question 2, the WK-692 row — accepted 2026-08-29.** The row is **not** amended: it records
  what the split intended on 2026-08-22, and rewriting it destroys that. What binds is the
  accompanying statement that **the slice map determines slices and the scope sentence only
  describes them**. The separate WK-690 observation — four requirements against a scope row
  describing one capability — is Phase 2 and remains a **spec change only** (§0's table), not
  a roadmap edit made here. **Owner: unowned**; the phase-plan sentence is a `docs/roadmap.md`
  edit and naming who makes it is not a planner's call.
- **Question 4, `scope-audit.py --params` gets an owner — accepted 2026-08-29, and still
  unowned as of this date.** Re-verified at `3edd75a`: the parser declares five arguments and
  `grep -c -- --params scripts/scope-audit.py` returns 0, so the axis review 3 accepted on
  2026-08-22 has now gone un-built through two further reviews. Accepting the proposal does
  not build it and does not name its owner — **unowned**, and recorded as such deliberately,
  because that is exactly the state question 5 below is about.
- **Question 5, every accepted §14 proposal gets an owning row — accepted 2026-08-29, and it
  binds this edit first.** *"Every accepted §14 proposal gets an owning row in the same edit
  that accepts it, or is explicitly marked unowned."* This is the only proposal here that
  changes how acceptance itself is written, and today's edit is the first to fall under it:
  every item accepted below — in reviews 7 and 8 as well as this one — therefore carries an
  owner or is marked **unowned**. Marking unowned is not a lesser outcome; it is the escape
  the proposal itself names, and it is used wherever naming an owner would be a
  `docs/roadmap.md` edit, which `CLAUDE.md` §12 does not put in a planner's hands.
- **The three instrument findings needed no acceptance line and did not wait on one** —
  corrections are unreviewed writes; the §0 correction convention manufactures its own false
  positives; an accidental gap in a permanent-id sequence is a collision invitation. Each is a
  finding about the instrument, not a proposal to the maintainer.
- **The "no change" answer stands** on the phase boundaries, Phase 1b's exit criterion and
  Phases 2–4, and needed no acceptance.
