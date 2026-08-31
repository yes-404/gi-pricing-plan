---
name: phase-review
description: Run CLAUDE.md §14's plan review — at every workstream close and again before a phase's exit demo. Tests whether the plan still says the right thing, rather than whether a workstream did what it said (that is close-workstream). Five questions in fixed order, each with a written answer including "no change"; the output is a proposal with a maintainer acceptance line, never an edit to the plan. Use when asked to review the plan, the roadmap, or the phase shape — and always at a workstream close.
---

# Running a plan review

`CLAUDE.md` §14 is the standard. This is how to satisfy it, written after two runs.

`close-workstream` asks whether **one workstream did what it said**. This asks whether
**the plan still says the right thing** — and they fail differently. A workstream can close
honestly against a row that describes the wrong work.

## When

At **each workstream close**, and again **before a phase's exit demo**. Both can fire at
once, and did for review 2. A fixed trigger, not "when someone remembers": a review that
happens after the mis-cut is a review of a decision already paid for.

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

- `pipelines/` marked 1a W4 while belonging to W7 — in the plan, wrong phase
- the blob endpoints, declared in a spec and owned by no row
- **endpoints declared in neither the spec nor the contract** — invisible to
  `--endpoints`, which compares the two
- **`docs/workflows/wf-01…05` evidenced by nothing.** No test cites a journey; the phase's
  exit criterion is a slice of `wf-01` and the test covering it does not name it

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
the 2026-08-23 restructure ([`NT-0003`](../../notes/0003-duplicated-status-goes-stale.md)),
so check them there and not in two places.

Resolve, never soften (§0). Where the code is right, amend the spec with a dated note
saying which side was wrong. Where the *spec* is right and the code does not meet it, the
spec gains the obligation — an appended requirement, an owner, a verdict. **FR-DATA-41 and
FR-DATA-42 are what that looks like**: a review that found the code short of the spec, and
left the spec carrying the precise obligation rather than editing it down to what was
built.

### 5. Shape — is the cut still right?

Split, merge, add, supersede. Two smells worth naming:

- **A row nothing can be said to have closed.** W6b grew to span a Vue view, an OIDC flow
  and a database trigger. Scope that crosses that many kinds cannot be audited as one thing.
- **A phase exit criterion the phase cannot meet.** Phase 1a's says the retrofit list is
  fully in place; one item on it is enforced by convention. Either the work lands or the
  criterion is amended — and the review's job is to make somebody choose, not to choose.

## Four rules that keep a review a review

- **The output is a proposal, never a change.** Recommendation, rationale, and an explicit
  `**Maintainer acceptance:** _pending_` line, dated when it is given.
- **Requirement ids are permanent.** "Remove a requirement" means mark superseded.
- **A later phase's finding is a spec change only.** It does not become work now.
- **Every question gets a written answer, "no change" included.** A silent question cannot
  be told apart from one nobody asked.

## When a review gets its own premise wrong

It will. Review 1 proposed adding a `W6b` row that had existed since the 1a/1b split.

**Record the correction beside the proposal, not instead of it.** The substance usually
survives — three items had no owner either way — but a review that quietly repairs itself
leaves nobody able to tell what was believed, which is the thing the reviews exist to
preserve.

The same applies to an instruction that names a workstream that does not exist or is
closed: check the id against `docs/roadmap.md` before acting on it, and say so plainly.

## Output

Proposals land in `docs/audit/plan-reviews.md` as a dated `### Plan review N` section, and
anything undecided goes to `docs/open-questions.md` with options and a recommendation.

**Cite the phase's retry counters (NT-0014 artifact B).** The same field
`close-workstream` cites at Work close (`.claude/skills/close-workstream/SKILL.md`,
"Closure record template") applies here one layer up: read
`python3 .claude/skills/watcher-runtime-state/scripts/write_runtime_state.py show` for
each `project`/`phase`-layer `replan`/`fix` entry the phase's Works recorded, and name it
in the review — this is the §7 pilot data question 5 ("no change" included) has to answer
against, once one workstream's worth exists.

## Verified

2026-08-31 — added the retry-counters citation to Output, NT-0014 adoption slice G
(impact-matrix row 17: "Same as row 16 at phase level"). Not yet exercised by a real
review — no phase-level review has run since C2 existed to populate the counters.

2026-08-29 — the Output location corrected. It named `docs/roadmap.md`, which was where
reviews 1-6 originally landed; the roadmap slim (NT-0009, accepted 2026-08-27) moved all six
to `docs/audit/plan-reviews.md` and nothing updated this skill to match, so a reader following
it two days later would have filed the next review in the wrong file. Caught while filing
plan reviews 7 and 8, which is the proof the correction is right: they land where this now
says. No other section was stale.

2026-08-23 — question 4 amended when `CLAUDE.md` was cut to its binding rules: §2's
component status marks no longer exist to check, and the FR-DATA-41/42 exemplar moved here
from §14. The five questions and their order are unchanged.

2026-08-15 — written after review 2, from what reviews 1 and 2 actually did. Review 1
found the browser could not authenticate at all; review 2 found the workflow journeys
evidenced by nothing and a phase exit criterion its phase cannot meet. Neither finding came
from the question its author expected.
