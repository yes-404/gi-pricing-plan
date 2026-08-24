# NT-0005 — Six deferred items with no durable custody

| | |
|---|---|
| **Raised** | 2026-08-24, Claude — during W6b, from six items that were found, agreed to be real, and then held only in a session's working memory |
| **Status** | `open` — six backlog items, each needing a maintainer decision on *where* it lands. Raised and assessed, not agreed: nothing is built on them |
| **Deliverable** | Mixed, and stated per item below. Four are **no code and no spec change** (a convention, two one-line script fixes, a plan-freeze consequence); one is a **new audit check**; one is an **`OQ-` entry**. None is a requirement |
| **Owner** | Claude records · maintainer accepts, per item |
| **Lands in** | Per item: [`scripts/audit-docs.py`](../../scripts/audit-docs.py), [`docs/open-questions.md`](../../docs/open-questions.md), [`docs/roadmap.md`](../../docs/roadmap.md), [`docs/specs/00-overview.md`](../../docs/specs/00-overview.md) |
| **Sequencing** | Items (a), (d) and (e) are workable now. Item (b) is blocked on (e). Item (c) is workable now and expires when `W6b-1b` is sequenced. Item (f) is a `W6b` close item |

---

## Why this note exists at all

Each of the six was found during W6b, checked against the repository, and agreed by more
than one session to be real. None of them belonged to the slice being worked at the time, so
each was "noted for later" — and *later* was, in every case, a session's own context, which
is discarded when the session ends.

**A finding with no filed home is indistinguishable from a finding that was withdrawn.** The
repository afterwards looks the same either way: no roadmap row, no open question, no check.
That is the same failure mode [`NT-0003`](0003-duplicated-status-goes-stale.md) records for
duplicated status and [`NT-0004`](0004-a-reference-that-resolves-only-for-the-writer.md)
records for references — a claim that is true when written and unreadable afterwards.

**This note is custody, not a decision.** Per the directory standard, nothing here is
settled; each row names where it would land if accepted.

## The six items

| | Item | Deliverable per `CLAUDE.md` §0 | Status |
|---|---|---|---|
| **(a)** | A `Next free:` marker for `OQ-` ids in `docs/open-questions.md` | No code, no spec change — a convention, plus the marker line | `open` |
| **(b)** | A reconciliation check between `00` §5.6 and each spec's §5.3 that **diffs routes, not view names** | New check in `scripts/audit-docs.py` | `open` — blocked on (e) |
| **(c)** | The `W6b-9` → `W6b-1b` dependency, which the frozen slice map's dependency column does not carry | No code, no spec change — a roadmap row | `open` |
| **(d)** | `audit-docs.py:383` and `:514` append a clean summary line on runs where their own check failed | No code, no spec change — two one-line script fixes | `open` |
| **(e)** | Which of §5.6's two columns is authoritative — the convention (b) needs before it can be written | No code, no spec change — a convention, recorded in `00` §5.6 | `open` |
| **(f)** | Nothing checks that an `FR-` id cited by a workflow step *contains* what the step claims | `OQ-` entry | `open` |

---

### (a) `docs/open-questions.md` has no `Next free:` marker

The convention already exists in this repository, for a different id family.
[`docs/plans/README.md:55-56`](../../docs/plans/README.md) requires a plan that intends to
take a requirement id to declare it — *"Highest ids in use: FR-DATA-52. Next free:
`FR-DATA-53`"* — and the audit accepts the id only after that marker.

`docs/open-questions.md` carries no equivalent. Allocating a new `OQ-` id therefore means
scanning the file and taking the next integer, which is correct exactly until two sessions
do it in the same hour. During W6b three `OQ-` drafts were prepared concurrently and the
next-free ids had to be re-derived by hand each time.

**Claude's assessment.** This is the cheapest of the six and the one most likely to be
skipped, because the manual derivation *works* — it is only unsafe under concurrency, which
is the condition this project now runs in permanently. The marker is one line, and the
mechanical half is already written for `FR-` ids.

### (b) The §5.3 ↔ §5.6 reconciliation must diff routes, not view names

`docs/specs/00-overview.md` §5.6 lists every SPA view with its route. Each module spec's §5.3
lists that module's views with a Contents column. Nothing checks the two against each other.

**The check must compare the Route column, not the view-name column.** The names are prose
and legitimately differ between the two tables; the routes are identifiers. A check written
against names would fail on every correctly-recorded row and pass on a genuinely divergent
one — which is worse than no check, per the argument
[`.claude/notes/README.md`](README.md) makes about a silently-passing check.

The counterexample that establishes it is `00` §5.6's own row —

```
| Quote sandbox & trace viewer | `/rating/:slug/v/:version/sandbox` | 03 |
```

— two named views on one route. A name-diffing check reads that as two missing §5.3 rows.

**Claude's assessment.** Real, and blocked: the check cannot be written until (e) says which
column governs when the two tables disagree. Filing it without (e) produces a check whose
failure message cannot say which side to fix.

### (c) `W6b-9` depends on `W6b-1b`, and the frozen map's dependency column says it does not

[`docs/plans/2026-08-24-w6b-slice-map-revised.md:157`](../../docs/plans/2026-08-24-w6b-slice-map-revised.md)
carries `W6b-9` with both dependency cells empty, and the *What can start today* list at
:220 names it among eight startable slices. The prose at :230 says the opposite, and says it
well:

> **`W6b-9` is deliberately not first**, despite being unblocked and small. It retrofits a
> tabular fallback onto charts, and `W6b-1b` adds eight. Doing it first means doing it twice,
> and a fallback proven against the two charts that exist today … is a positive control run
> on the easy case — it goes green because of what it does not cover.

**A filed plan is frozen at its date** ([`docs/plans/README.md`](../../docs/plans/README.md)),
so the dependency column cannot be corrected in place, and should not be. The consequence is
that a reader who consults the column and not the prose four sections below it will schedule
`W6b-9` early and get a fallback that is green for the wrong reason.

**Claude's assessment.** The durable home is a `docs/roadmap.md` row for `W6b-9` naming
`W6b-1b` as its predecessor, with the reason. This item expires the moment `W6b-1b` is
actually sequenced — which is precisely why it will be forgotten if it is not written down
now.

### (d) Two summary lines assert a clean result on runs where their own check failed

`scripts/audit-docs.py` collects failures via `fail()`, which appends and returns; execution
continues. Two summary lines are therefore emitted unconditionally, after their own failure
loops:

```
:383    notes.append(f"{len(in_file)} open questions, all mirrored")
:514    notes.append(f"{len(owner)} error codes, ownership exclusive")
```

On a run where an open question is raised in a spec and not mirrored, the audit prints the
failure **and** prints *"N open questions, all mirrored"*.

**This has a deliberate precedent in the same file.** Check 21 already does it correctly, and
its comment states the principle:

```python
# The verdict goes in the summary line, not just in the failure list. A note reading
# "all declared" above a `FAILED` block is the shape of thing this audit exists to catch.
verdict = "all declared" if not undeclared else f"**{undeclared} undeclared**"
```

**Claude's assessment.** Two lines, one established pattern, no design question — the only
reason it is not already done is that it was found while working on something else. The fix
must be proven on deliberately broken input (`CLAUDE.md` §13): add an unmirrored `OQ-` id,
confirm the summary line changes, restore.

### (e) Which of §5.6's two columns is authoritative

(b) cannot be written without this. When a view appears in `00` §5.6 with one route and in a
module's §5.3 with another, which is wrong? The suite does not say, and the answer is not
obvious in either direction: §5.6 is the single cross-module list, and §5.3 sits next to the
requirements that build the view.

**Claude's assessment.** The convention is the deliverable and it must be *written before*
the check, not derived from whatever the check happens to do. A check whose failure message
says "these disagree" without saying which to fix converts a two-minute correction into a
judgement call each time it fires.

### (f) Nothing checks that a cited `FR-` id contains what the step claims

Two mechanisms score workflow citations, and neither reads the requirement's text:

- **Check 21** (`:601`) resolves an endpoint path or a `` name() `` function citation against
  the owning module's §5.1/§5.2 — it validates the *interface*, not the requirement.
- **Check 14** (`:571`) scores per-module workflow coverage with `if rid in wf_text` — a
  substring hit of the id anywhere in the workflows corpus.

So a journey step may cite `FR-MODEL-50` while describing something `FR-MODEL-50` explicitly
struck, and both mechanisms record it as coverage. That is not hypothetical: `wf-01` step D5
named double lift as a `compute_diagnostics()` output and cited `FR-MODEL-50/51/54`, and
`FR-MODEL-50`'s own amendment of 2026-08-17 had removed double lift and moved it to
`FR-MODEL-56`. The citation was correct; the content it vouched for was not. It survived a
week of reading for exactly that reason, and was corrected on 2026-08-24 (`OQ-OVR-10`'s PR).

**Claude's assessment.** This is the one item of the six that is genuinely open rather than
merely unfiled, which is why its deliverable is an `OQ-` entry and not a check. A mechanical
content check is not obviously constructible — requirement text is prose — and the honest
options are a narrower structural check (an amendment that says *"X is removed"* should fail
any journey cell citing that id and naming X), a review obligation at each workstream close,
or accepting the gap and recording it. It should be filed as an open question against `00`,
which owns `FR-OVR-17` and therefore owns the citation audit.

## Acceptance criteria

Each item is discharged when it has a home outside a session's context: a marker line, a
roadmap row, a script change with its broken-input proof, a written convention, or an `OQ-`
id. **This note is `landed` only when all six have one**, and it records where each went.

## Next step

Maintainer decides per item. (a), (d) and (e) are small enough to land in one PR; (c) wants a
roadmap row before `W6b-1b` is sequenced; (b) follows (e); (f) is a `W6b` close item.

## Original wording

There is none — no maintainer request produced this note. It is Claude's own record of six
findings that arose during W6b and had nowhere to go, filed under
[`.claude/notes/README.md`](README.md)'s standard so they are not lost between sessions. The
assessments above are Claude's throughout and are marked as such.
