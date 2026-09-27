---
id: RFC-711
family: proposal
kind: process
title: Plan review at each phase boundary
status: closed                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-15
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/notes/0001-phase-boundary-plan-review.md
---

# Plan review at each phase boundary

## The request

The roadmap was written before any application code existed. Code has since contradicted it
more than once, so treat the plan as a working hypothesis and re-test it **while the phase
is still open** — early enough that the answer can change what the phase does.

Run the review at a fixed trigger, not "sometime": **at each workstream close, and again
before the phase's exit demo.** Five questions, in this order:

1. **Completion.** Which of the phase's planned tasks are actually done — derived from the
   specs, then evidenced, never from recollection (`CLAUDE.md` §13 step 1).
2. **Omission.** What the phase plainly needs that no workstream row names. WK-660's Dagster
   mark and the missing blob endpoints were both of this kind: absent from the plan, not
   merely unfinished.
3. **Skills and research.** Which entries `docs/skills-map.md` and
   `.claude/skills/README.md` are now missing, and which have gone stale against the code.
   Re-run the gap analysis rather than appending to a list.
4. **Document drift.** Whether `docs/roadmap.md`, `docs/open-questions.md`, the module specs
   and `CLAUDE.md` §2's layout marks still describe the repository as it is.
5. **Shape.** Whether the remaining phases, workstreams and requirements are still cut in
   the right place — split, merge, add, or supersede — now that some of the work is real.

**Why:** the plan is pre-determined and cannot stay correct by default. Every phase boundary
is a cheap chance to correct it; the alternative is discovering the mis-cut at the end, when
the correction is a rewrite.

## Assessment — Claude, 2026-08-15

**Worth doing, and it fills a real gap.** `CLAUDE.md` §13 and `scripts/scope-audit.py` audit
*one workstream against its own scope*. Nothing audits **the plan itself** — whether the
phase boundaries, the workstream cuts and the requirement set still make sense. The
project's own record argues the plan needs it: three open questions answered by reasoning
had to be corrected once a spike tested them, and the 1a/1b split was itself the output of
exactly this kind of review.

Four corrections before it is run:

- **Reuse the existing machinery, do not build a parallel audit.** Question 1 is
  `scope-audit.py` (`--sections`, `--endpoints`, `--catalogue`) plus `req-coverage.py`, and
  `close-workstream` already covers it. The review's own contribution is questions 2–5.
- **The output is a proposal, never a change.** Follow the precedent the 1a/1b split set —
  recommendation, rationale, and an explicit maintainer acceptance line with a date. A
  review that edits the roadmap on its own authority is re-planning, not reviewing.
- **Question 5 has a hard boundary: requirement IDs are permanent** (`CLAUDE.md` §5).
  "Remove a requirement" means *mark superseded*; renumbering is never the answer. Likewise
  an accepted ADR is amended by addendum, not edited (`.claude/skills/adr-write`).
- **Name the failure mode it must avoid.** Mid-phase re-planning invites scope churn and
  building ahead of the phase. Anything the review surfaces that belongs to a later phase is
  a spec change only (`CLAUDE.md` §0's table) — it does not become work now because a review
  noticed it.

## Acceptance criteria

- Every in-scope requirement without evidence has one of the four §13 verdicts.
- Questions 2–5 each have a written answer — "no change" included.
- Every proposed change is either accepted with a date, or recorded in
  `docs/open-questions.md` with options and a recommendation.

## Where it went

Accepted by the maintainer 2026-08-15 and merged into the suite, which is where it is now
authoritative:

| Outcome | Landed in |
|---|---|
| The standard — when it runs, the five questions, the four rules | `CLAUDE.md` §14 |
| The trigger, and that its output is a proposal on that page | `docs/roadmap.md`, beside the §13 closure paragraph |

All four corrections from the assessment survived into §14: reuse `scope-audit.py` rather
than building a parallel audit, the output is a proposal never a change, requirement IDs are
permanent so "remove" means *mark superseded*, and a later phase's finding is a spec change
only.

## Next step

Run it once at WK-663's close — the first run is now recorded as due in `docs/roadmap.md`.
After a second run, the procedure becomes `.claude/skills/phase-review`, alongside
`close-workstream` (`CLAUDE.md` §12).

## Original wording

As raised by the maintainer. Grammar and punctuation corrected; wording, structure and
meaning are theirs.

> Evaluate the project plan before any one phase is complete, in order to assess:
> 1. whether the planned tasks have been completed;
> 2. any topics that should have been completed but are missing from the plan;
> 3. any skills and research that should be added to the list, and evaluate them;
> 4. whether the plan, roadmap, open questions and other docs need to be upgraded or
>    revised in the light of the code written so far;
> 5. whether the planned phases need to be split or merged, whether work should be merged
>    or split, and whether detailed requirements should be added, merged or removed.
>
> The aim is to give the plan a chance to be upgraded: it was pre-determined, and may no
> longer be suitable once some code has been written.
