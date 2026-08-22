# Filed plans

The implementation plans this project has worked from, and the ledgers recording what
happened when they were executed. They are committed, so the record outlives the session
that wrote it.

They live under `docs/` rather than in an untracked scratch directory for the reason
`.gitignore` already gave for keeping them out of one: a plan is *"a second account of what
the project is doing"*, and the objection was never to the second account — it was to an
**unaudited** one. Filed here, `scripts/audit-docs.py` reads them like every other document
in the suite, and a plan that cites a requirement which does not exist fails the gate.

## A filed plan is a record, not an instruction

Each file is frozen at its date. It says what was believed, intended and decided *then* —
including the parts that later turned out to be wrong, which are usually the most useful
parts to a reader working out why the code looks the way it does.

**Do not edit a filed plan to agree with today's repository.** That is the same rule
[`CLAUDE.md`](../../CLAUDE.md) §0 applies to a spec and its code: quietly making one match
the other destroys the record of which was believed, which is the thing a governed system
cannot afford to lose. If a plan is wrong, the correction belongs in the document that is
still authoritative — the spec, [`../roadmap.md`](../roadmap.md), or a working note.

The one exception is a change that preserves the claim exactly while fixing how it is
*addressed* — the relative links repointed when these files moved out of `.planning/` are
the whole of it.

## The four kinds of file

| Suffix | Written by | Holds |
|---|---|---|
| *(none)* | `writing-plans` | The plan — goal, architecture, tasks, bite-sized steps |
| `-ledger` | `subagent-driven-development` | What execution actually did, task by task |
| `-final-review`, `-verified` | a review pass | Findings against a finished branch, and their verdicts |
| `-handover` | a session ending mid-work | State a successor session needs to resume |

## Naming

`YYYY-MM-DD-<slug>.md`, dated when the file was started.

**`ls docs/plans/` is the index.** There is deliberately no hand-maintained list of contents
in this file: the date prefix already sorts the directory chronologically, and a list that
nothing enforces goes stale — the lesson `CLAUDE.md` §0 records about counts and §9 records
about restating the roadmap.

## Writing one so it passes the audit

Four conventions, each of them a check that will otherwise fail:

1. **Relative links resolve from `docs/plans/`** — a spec is
   [`../specs/01-data-management.md`](../specs/01-data-management.md), the roadmap is
   `../roadmap.md`, the repository root is `../../`.
2. **Every `FR-`/`NFR-` id you cite must already be defined in a spec.** The exception is
   the id a plan intends to *take*, which the audit accepts only after a `Next free:`
   marker, as in — "Highest ids in use: FR-DATA-52. Next free: `FR-DATA-53`". The exemption
   covers the rest of that line only; an undefined id before the marker, or on any other
   line, still fails.
3. **Markdown table rows must match their header's cell count.** A literal `|` inside a cell
   shifts every column after it while still rendering, so escape it as `\|`.
4. **Every `ADR-NNNN` you cite must have a file** in [`../adr/`](../adr/).

Run `python3 scripts/audit-docs.py` before handing a plan off.

## Live plan state is *not* here

`planning-with-files` keeps an agent's working memory — `task_plan.md`, `findings.md`,
`progress.md` — in `.planning/`, and `subagent-driven-development` keeps its per-plan
workspace in `.superpowers/sdd/`. Both stay git-ignored. They are a running session's
scratch, rewritten every few turns; this directory holds the finished record.
