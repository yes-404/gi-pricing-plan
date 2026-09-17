---
id: RL-969
family: ruling
title: W37-6's go-ahead is withheld — the maintainer's decision of 2026-09-02, and what "yet" costs
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-6-go-ahead-withheld.md
---

# W37-6's go-ahead is withheld — the maintainer's decision of 2026-09-02, and what "yet" costs

**Status:** decided. **Decision:** *not yet.* **Decided by:** the maintainer, 2026-09-02.
**Recorded by:** the lead, at the maintainer's instruction — *"it is a decision — 'not yet' —
and it should not live only in chat."*

**Tree:** `ffac8ba`. Every figure below is measured there and named with it.

## 1. What was decided, and what was not

W37-6 is RFC-937's migration run: one supervised commit that dissolves `docs/audit/`,
renumbers every requirement id in the repository, and rewrites citations across the tracked
tree. Its final precondition is *"the maintainer has given a dated go-ahead for this specific
run … it is not a slice a lead dispatches on standing authority."*

**The lead did not ask for that go-ahead**, and the maintainer's decision confirms that
withholding the ask was right.

**This record is not a go-ahead, conditional or otherwise.** The maintainer's words:

> Nothing here is a go-ahead, conditional or otherwise: RL-987 §3 requires the disclosure
> to arrive with the ask, and the run's figures move under it, so an approval given now would
> describe a run other than the one that happens.

That second clause is measurable rather than rhetorical. The leaf plan's §4.2 is pinned at
`39ee30c` and states **1447** tracked files. At `ffac8ba` it is **1471**. The corpus grows
while the decision is open, so an approval given against last night's figures authorises a
different run from the one that would execute.

## 2. What "yet" costs — the maintainer's six conditions

Recorded here in substance, in the maintainer's own ordering.

1. **One list of everything W37-6 owns before the run**, not the four discovery defects alone —
   each item with its state and what discharges it. The roadmap's WK-697 row also names
   `is_vendored`'s `LICENSE` probe (Rulings 69 and 76) and the roadmap restructure blocked by
   Rulings 79 and 80. *"If there is more, it goes on the list."*
2. **The four discovery defects**, with `_discover_plan_reviews` first **because it is the one
   that fails silently**. `_discover_roadmap` and `_discover_register` raise today and the
   guard is not the fix — the patterns are. `_discover_closure_records` is correct and raises
   on the one heading class with no family yet; **that is a decision to route, not a code
   change**, so a run is not halted on it on the day.
3. **A property for the guard class, stated as a property rather than a design:** a legacy
   file's run must be able to fail on an **undercount**, not only on zero. *"Found nothing
   means already migrated" was a fixture-corpus assumption; the real tree needs the arithmetic
   to close.* How is a ruling to bring, not something to pick silently.
4. **Every fix proven on deliberately broken input** (`CLAUDE.md` §13) — for plan-reviews, a
   test carrying the real decorated heading shape, red before and green after. *"A guard that
   has never printed a failure has not been tested."*
5. **The WK-697 row's plan-reviews figures are wrong** and must be corrected with a dated note.
   See §3.
6. **On return, every figure re-derived at that day's tree**, with §4 of the leaf plan attached
   in full — RL-987's enlargement and §4.4's irreversibility list included. *"I want to read
   the run I am authorising, not the run as planned."*

**And a constraint on all of it:** the leaf plan is **not** edited to agree with any of this.
It is frozen at its date (`CLAUDE.md` §2). Findings against it, and any replan, are new dated
artifacts. This document is one of those.

## 3. A correction the lead owes, and the measurement that settles it

**The WK-697 roadmap row records `plan-reviews` as "15 headings, 12 records". Both numbers are
wrong.** The lead wrote them from an executor's report without running the function, and
propagated them into `docs/roadmap.md` (PR #586) and into that PR's merge commit on `main`.
The maintainer caught it by running the function.

Measured at `ffac8ba` by executing `_discover_plan_reviews` against `docs/closures/INDEX.md#plan-reviewsmd`:

| Quantity | Recorded in the WK-697 row | Actual |
|---|---|---|
| `###` headings in the file | 15 | **14** |
| of which `Plan review N` | not stated | **11** |
| of which non-review sub-content | 3 | **3** |
| records produced | 12 | **10** |

**The mechanism, which the row also did not carry.** `_REVIEW_HEADING_RE` is
`^###\s+(.+?),\s*(\d{4}-\d{2}-\d{2})\s*$` — the date must **end the line**. `Plan review 9`'s
heading carries trailing text after its date, so it never matches. This is the identical
end-anchor defect that PR #585 fixed for `closure-records.md`, surviving in a second file.

**And the consequence is worse than "the preceding record".** The file is not in numeric
order. `Plan review 1 — at WK-663's close, 2026-08-15` is the last *matched* heading before four
consecutive unmatched ones, so a single `CR- kind: review` document titled for a review of
2026-08-15 would absorb `Candidate A`, `Candidate B`, `Also carried, and not a new rule`, **and
the entire body of `Plan review 9`, dated 2026-08-30** — fifteen days later.

**Why the existing guard cannot see it.** The file-level guard is wired for `plan-reviews` and
trips on **zero** discovered. This is ten of eleven. That is precisely the property the
maintainer's condition 3 asks to be ruled: the arithmetic must close, not merely be non-zero.

## 4. Where each condition is routed

| Condition | Owner | State at `ffac8ba` |
|---|---|---|
| 1 — the full obligation list | planner | in flight, as a new dated artifact |
| 2 — `_discover_plan_reviews` code fix | executor | not started; blocked on nothing |
| 2 — the three undated headings: records or sub-content | decision-maker | in flight |
| 2 — the closure-record family, routed as a decision | decision-maker | in flight |
| 3 — the undercount property | decision-maker | in flight, as a ruling |
| 4 — broken-input proofs | executor, per fix | standing requirement |
| 5 — correct the WK-697 row | lead | this branch |
| 6 — re-derive at the day's tree, attach §4 in full | lead, at the next ask | owed |
| Rulings 79 and 80's fixes | executor | in flight |

**Sizing, and whether the remainder is W37-6 scope or a replan, is the lead's to propose** —
the maintainer left that open explicitly. The planner's list is the input to that proposal.

## Acceptance Standard

The violation this record must make detectable: **an approval for W37-6 that does not carry
its own disclosure, or that describes a run other than the one that would execute.**

1. No document in `docs/plans/` records a W37-6 go-ahead dated on or before 2026-09-02.
   A go-ahead appearing without an accompanying disclosure of that day's figures violates
   RL-987 §3 and this record.
2. `docs/roadmap.md`'s WK-697 row carries a dated correction of the `plan-reviews` figures, and
   no longer states 15 and 12 as current. Violation: the row still reports figures the
   function does not produce.
3. `docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md` is unmodified by this branch.
   Violation: a frozen plan edited to agree with a later decision.
4. Each of the six conditions has a named owner and a state above. Violation: a condition
   recorded with no owner, which is how an item becomes nobody's.
