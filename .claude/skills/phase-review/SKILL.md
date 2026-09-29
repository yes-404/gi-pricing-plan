---
name: phase-review
description: Run CLAUDE.md §14's plan review — in full before each phase's exit demo, and at a Work close only when the auditor's replan check fires. Tests whether the plan still says the right thing, rather than whether a workstream did what it said (that is close-workstream). Five questions in fixed order, each with a written answer including "no change"; the output is a short index of proposals, each accepted one routed to an owned record, never an edit to the plan. Use when asked to review the plan, the roadmap, or the phase shape, before every phase exit demo, and when a Work close's replan check fires.
---

# Running a plan review

`CLAUDE.md` §14 is the standard. This is how to satisfy it, written after two runs.

`close-workstream` asks whether **one workstream did what it said**. This asks whether
**the plan still says the right thing** — and they fail differently. A workstream can close
honestly against a row that describes the wrong work.

## When

*(Amended 2026-09-29, `RFC-1248`, option C: the trigger below replaces "at each workstream
close, and again before a phase's exit demo". The old wording is kept here so a reader of an
older review knows which rule it ran under.)*

1. **Before each phase's exit demo: a full plan review, always.** Unchanged, and a phase's
   exit criteria may count it (P2's G6 does).
2. **At a Work close: a replan check, not a review.** The auditor's `CR- kind: work` carries
   a **Replan check** section: the five questions below, each answered **yes** or **no** with
   one line. **A full review runs only if one of these fires:**
   - a phase boundary, or a Work's scope, moved;
   - an exit criterion is at risk;
   - a replan was decided;
   - a finding moves a slice or a phase.

   The lead gives its verdict on the check. **"No trigger" is recorded, never assumed**:
   an empty check reads as one nobody ran.

Both can still fire together (review 2 did). The trigger stays fixed, not "when someone
remembers": a review after the mis-cut is a review of a decision already paid for. What
changed is that a Work close which moved nothing costs one short section, not a review.

### The replan check — the five questions, one line each

The auditor answers these in the Work's `CR- kind: work`, from the close's own evidence:

1. **Completion:** did the close's scope audit disagree with the roadmap row? (yes/no)
2. **Omission:** did the close find something the phase needs that no row names?
3. **Skills and research:** did a skill or research record prove wrong or missing?
4. **Drift:** does a spec, the roadmap or an OQ now disagree with the code or the plan?
5. **Shape:** did a phase boundary or Work scope move, an exit criterion come under risk,
   a replan get decided, or a finding move a slice or phase?

A **yes** to question 5 is a trigger. A yes to 1–4 is a trigger when its one line shows it
moves scope, an exit criterion, a slice or a phase; otherwise it is recorded and carried to
the next full review. Add one evidence line: `python3 scripts/register-owed.py review`'s
owed count at the close's tree, so rows waiting for a review are visible without one.

## The agenda includes every register row that decayed to this review

The agenda includes every `docs/findings/register.md` row that has decayed to this review —
every unowned row naming no other event. **Each gets a disposition in the review's output:**
an owner, an accepted deferral with a new named event, or a finding against the register.
**Listing one without disposing of it is not a disposition.** (RFC-896 P2, RL-909 B.)

Generate the list; do not recall it — `python3 scripts/register-owed.py review` against a
**committed** revision (it refuses a dirty register). The reason is measured: at the WK-671 close
the hand-compiled owed list lost NFR-502/501 (F41), and running the generator over that
same close afterwards surfaced ten further attributed rows the record never mentions (F63).
The output is **evidence, not authority** — where it and the record disagree, one or the other
is amended, never silently (`CLAUDE.md` §0).

## The five questions, in order

Order matters. Completion first, because an omission is only visible once you know what is
actually done; shape last, because it depends on the other four.

### 1. Completion — derived, never recalled

`scope-audit.py` with `--sections`, `--endpoints` and `--catalogue`, plus `req-coverage.py`.
Both inputs are documents, so the answer does not depend on who runs it.

**If a fresh audit has just covered this, say so and move on.** Review 2 took its numbers
from an independent audit run hours earlier rather than re-deriving them from the same
sources — re-deriving would have looked like work and confirmed nothing.

**A disagreement with the roadmap is the finding**, not a nuisance to reconcile quietly.

### 2. Omission — what the phase needs that no row names

Distinct from unfinished work. Ask: *what would nobody notice was missing?*

What this has actually found:

- `pipelines/` marked 1a WK-660 while belonging to WK-665 — in the plan, wrong phase
- the blob endpoints, declared in a spec and owned by no row
- **endpoints declared in neither the spec nor the contract** — invisible to
  `--endpoints`, which compares the two
- **`docs/workflows/WF-698…05` evidenced by nothing.** No test cites a journey; the phase's
  exit criterion is a slice of `WF-698` and the test covering it does not name it

The pattern in all four: *a number exists, it is not measuring what its name suggests, and
nobody had looked.*

### 3. Skills and research — re-run the gap analysis

Not "append to the list" — a list only ever grows. Ask which entries are now **ahead** of
the code (declared, not installed — fine, if the phase says so) and which are **behind**
it (claimed as verified while the repository depends on them nowhere; `skills-map.md` had
pandera at ★★ *Verified* for exactly that).

Never install an external skill without the maintainer's approval.

### 4. Document drift

Specs first — §14 makes the **specification** the main target, in both directions:
§5.1 endpoint tables, §5.2 signatures, §5.3 Contents columns, named catalogues, and the
params a caller would copy off the page. Then the roadmap and open questions. `CLAUDE.md`
§2 no longer carries component status marks — `docs/roadmap.md` §6 owns them outright since
the 2026-08-23 restructure ([`RFC-756`](../../../docs/rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md)),
so check them there and not in two places.

Resolve, never soften (§0). Where the code is right, amend the spec with a dated note
saying which side was wrong. Where the *spec* is right and the code does not meet it, the
spec gains the obligation — an appended requirement, an owner, a verdict. **FR-40 and
FR-43 are what that looks like**: a review that found the code short of the spec, and
left the spec carrying the precise obligation rather than editing it down to what was
built.

### 5. Shape — is the cut still right?

Split, merge, add, supersede. Two smells worth naming:

- **A row nothing can be said to have closed.** WK-664 grew to span a Vue view, an OIDC flow
  and a database trigger. Scope that crosses that many kinds cannot be audited as one thing.
- **A phase exit criterion the phase cannot meet.** Phase 1a's says the retrofit list is
  fully in place; one item on it is enforced by convention. Either the work lands or the
  criterion is amended — and the review's job is to make somebody choose, not to choose.

## Length

**A review is proposals only, about 150 lines.** Evidence lives in the records it cites
(`CR- kind: work`, `FD-`, `RS-`, the register), not restated. Reviews 1–15 averaged 302
lines, and every review from 9 to 15 ran 207 to 935 (`RFC-1248`'s evidence).

## The rules that keep a review a review

- **The output is a proposal, never a change.** Recommendation, rationale, and an explicit
  `**Maintainer acceptance:** _pending_` line, dated when it is given.
- **Requirement ids are permanent.** "Remove a requirement" means mark superseded.
- **A later phase's finding is a spec change only.** It does not become work now.
- **Every question gets a written answer, "no change" included.** A silent question cannot
  be told apart from one nobody asked.
- **No accepted proposal is unowned** (`RFC-1248` Part 2). At the acceptance line, every
  accepted proposal has a record id and an owner, or the lead names one, or the proposal is
  **withdrawn** with a dated reason.

## When a review gets its own premise wrong

It will. Review 1 proposed adding a `WK-664` row that had existed since the 1a/1b split.

**Record the correction beside the proposal, not instead of it.** The substance usually
survives — three items had no owner either way — but a review that quietly repairs itself
leaves nobody able to tell what was believed, which is the thing the reviews exist to
preserve.

The same applies to an instruction that names a workstream that does not exist or is
closed: check the id against `docs/roadmap.md` before acting on it, and say so plainly.

## Output

*(Amended 2026-09-29, `RFC-1248` Part 2, future-facing: reviews 1–15 are not converted.)*

**The review is a `CR- kind: review` under `docs/closures/`, conducted and filed by the
planner; the family is the lead's** (`document-ids.md` §1.6). It is a **short index**, with
no free-text proposal left without a record:
1. **Tracking first:** the previous review's records, each with its current state,
   **derived from the records** (their `status:`, their rows), never recalled.
2. A short evidence summary, citing records rather than restating them.
3. **A table:** proposal → record id → owner → state.
4. The maintainer's acceptance line.

**Each accepted proposal becomes an owned record in the family `document-ids.md` §1.6 gives
its kind**, created in its proposed or draft state by that family's owner:

| Proposal kind | Record | Created by | Landing is tracked by |
|---|---|---|---|
| Process, scope, phase boundary or convention (skill, charter, `CLAUDE.md`, delivery process) | **RFC** | the planner drafts; the maintainer owns | the RFC `closed` when it ships |
| Replan (re-cut, reorder) | a **new PL** that supersedes the old one | the planner, on the lead's replan decision | the PL's execution state (§1.7) |
| Spec or requirement change | **RL** + the spec amendment | the decision-maker | the RL's sites, checked at close |
| Gap, defect or risk | **FD** with an owner | the auditor; the lead sets `decision:` | the FD `closed`, citing the PR |
| Open design question | **OQ** | the decision-maker | closed by an RL or ADR |
| Owned Work or slice change | a **WK/SL row** edit | the lead or the planner | its own status |

Anything undecided still goes to `docs/open-questions.md` with options and a recommendation,
as an `OQ-` row in the table.

**Cite the phase's retry counters (RFC-895 artifact B).** The same field
`close-workstream` cites at Work close (`.claude/skills/close-workstream/SKILL.md`,
"Closure record template") applies here one layer up: read
`python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show` for
each `project`/`phase`-layer `replan`/`fix` entry the phase's Works recorded, and name it
in the review — this is the §7 pilot data question 5 ("no change" included) has to answer
against, once one workstream's worth exists.

## Verified

2026-09-29 — **the trigger, the output and a length cap amended by `RFC-1248`** (option C,
Part 1 and Part 2), adopted by the maintainer on 2026-09-29 and confirmed by the user. The
trigger in *When* and the index form in *Output* are new; the five questions, their order
and the four existing rules are unchanged, with a fifth ("no accepted proposal is unowned")
added. Not yet exercised: the first Work close under it is the test of the replan check.

2026-08-31 — added the retry-counters citation to Output, RFC-895 adoption slice G
(impact-matrix row 17: "Same as row 16 at phase level"). Not yet exercised by a real
review — no phase-level review has run since C2 existed to populate the counters.

2026-08-29 — the Output location corrected. It named `docs/roadmap.md`, which was where
reviews 1-6 originally landed; the roadmap slim (RFC-813, accepted 2026-08-27) moved all six
to `docs/closures/INDEX.md#plan-reviewsmd` and nothing updated this skill to match, so a reader following
it two days later would have filed the next review in the wrong file. Caught while filing
plan reviews 7 and 8, which is the proof the correction is right: they land where this now
says. No other section was stale.

2026-08-23 — question 4 amended when `CLAUDE.md` was cut to its binding rules: §2's
component status marks no longer exist to check, and the FR-40/43 exemplar moved here
from §14. The five questions and their order are unchanged.

2026-08-15 — written after review 2, from what reviews 1 and 2 actually did. Review 1
found the browser could not authenticate at all; review 2 found the workflow journeys
evidenced by nothing and a phase exit criterion its phase cannot meet. Neither finding came
from the question its author expected.
