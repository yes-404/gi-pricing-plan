# Filed plans

The implementation plans this project has worked from, and the ledgers recording what
happened when they were executed.

## A filed plan is a record, not an instruction

Each file is frozen at its date. **Do not edit a filed plan to agree with today's
repository.** The one exception is a change that preserves the claim exactly while fixing
how it is *addressed* — the relative links repointed when these files moved.

## The four kinds of file

| Suffix | Written by | Holds |
|---|---|---|
| *(none)* | `writing-plans` | The plan — goal, architecture, tasks, bite-sized steps |
| `-ledger` | `subagent-driven-development` | What execution actually did, task by task |
| `-final-review`, `-verified` | a review pass | Findings against a finished branch |
| `-handover` | a session ending mid-work | State a successor session needs to resume |

## Naming

`YYYY-MM-DD-<slug>.md`, dated when the file was started.

**`ls docs/plans/` is the index.** There is deliberately no hand-maintained list here.

## Writing one so it passes the audit

Four conventions, each of them a check that will otherwise fail:

1. **Relative links resolve from `docs/plans/`** — a spec is
   [`../specs/00-overview.md`](../specs/00-overview.md), the roadmap is `../roadmap.md`.
2. **Every `FR-`/`NFR-` id you cite must already be defined in a spec**, as on
   [`2026-08-17-example-plan.md`](2026-08-17-example-plan.md).
3. **Markdown table rows must match their header's cell count.**
4. **Every ADR you cite must have a file** in [`../adr/`](../adr/).

Run `python3 scripts/audit-docs.py` before handing a plan off.
