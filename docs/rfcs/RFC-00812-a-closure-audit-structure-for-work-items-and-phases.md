---
id: RFC-812
family: proposal
kind: process
title: A closure audit structure for work items and phases
status: closed                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-27
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/notes/0008-project-closure-audit-structure.md
---

# A closure audit structure for work items and phases

## Request, refined

Standardise the closure audit so it runs as a two-level gate — a **work-item close** (a
task, ticket or PR finished) and a **phase close** (a milestone made of many work items) —
with findings, evidence and outcomes organised around *what is being closed*, not around a
one-off audit event. The structure is:

- `docs/findings/README.md` — what a close means, who signs off, the checklists.
- `docs/audit/checklists/` — `work-item-close.md` and `phase-close.md` (the second a
  superset of the first).
- `docs/audit/work/WI-###/` — per work item: `closure.md`, `findings.md`, `evidence/`.
- `docs/audit/phases/P#-name/` — per phase: `closure.md`, `findings.md`, `register.md`
  (rolls up every work item), `evidence/`.
- `docs/findings/register.md` — the single global list of *open* findings across all phases.

Two fill-in-the-blanks records (work-item closure and phase closure), two registers, and a
set of conventions: `WI-###` / `P#` / `F-<parent>-n` ids so origin is always visible;
evidence is write-once; checklists are versioned and each record states the version it used;
a tag at phase close so evidence reproduces against a fixed commit; secrets redacted; ISO
dates. One rule: nothing starts in phase N+1 while a Critical from phase N is open.

## Claude's assessment (kept separate from the maintainer's words)

This complements, and partly overlaps, the repository's existing §13/§14 machinery. The
worthwhile parts, stated plainly:

1. **A per-work-item record is the genuine addition.** `close-workstream` (CLAUDE.md §13)
   audits a workstream against its spec; it has no per-PR/per-task artifact. A `work/WI-###`
   record would give every slice's drift records and residue a durable home instead of a PR
   body that vanishes into a squash. This is the same gap the slice-plan discussion above was
   really about.
2. **The phase close maps onto `phase-review` (CLAUDE.md §14)** but adds a roll-up register
   and cross-cutting checks. The roll-up ("every closed-with-findings item is resolved,
   accepted with an owner, or re-planned") is exactly what §13's four-verdict discipline
   already demands; giving it a table is a real improvement over prose.
3. **The id family is new.** `WI-###` / `P#` / `F-<parent>-n` would be a fourth id series
   beside `FR-`/`NFR-`/`OQ-`/`ADR-`/`NT-`, and would need the same permanence rules
   (CLAUDE.md §5) and the same audit coverage as the rest — a non-trivial cost, not a
   naming change.
4. **The Critical-blocking rule is a governance rule**, not a note or a checklist — it
   belongs in an ADR or CLAUDE.md, and it is the part most likely to bind a later phase.
5. **It must not duplicate status.** `docs/roadmap.md` §6 owns component and workstream
   status (RFC-756). A `phases/P#/register.md` that restates it will drift; the register
   must derive from or point at the roadmap, not repeat it.

## Acceptance criteria

The maintainer states: (a) which parts replace versus complement the existing
close-workstream/phase-review skills, (b) whether the id family is adopted and where its
permanence rules live, and (c) whether the Critical-blocking rule becomes an ADR. Nothing is
built before those three are answered.

## Decision (partial, 2026-08-27)

The maintainer accepted the `docs/audit/` home on 2026-08-27, in the slim-roadmap decision
([[RFC-813]]): the historical record — closure records, plan reviews, the retrofit-impossible
list — moves to `docs/audit/`. That confirms the folder and the archive role. The three
acceptance points above remain open: which parts replace versus complement the
close-workstream/phase-review skills, whether the id family is adopted, and whether the
Critical-blocking rule becomes an ADR.

## Next step

The archive relocation is scheduled after WK-665 (via RFC-813). This note's fuller structure —
the per-work-item and per-phase checklists and registers — stays `open` until the three
acceptance points are answered.

## Original wording

Kept verbatim below, corrected for grammar and punctuation only — never for wording,
structure or meaning. It was supplied as a single markdown block; the headings and code
fences are the maintainer's.

> # Project Closure Audit Structure
>
> An audit that runs as a **closure gate**, twice: **work-item close** (a task, ticket or
> PR finished) and **phase close** (a milestone of many work items finished). Findings,
> evidence and outcomes are organised around *what is being closed*, not a one-off event.
>
> Folder layout:
> `docs/audit/` with `README.md`, `checklists/` (work-item-close, phase-close), `work/WI-…/`
> (closure.md, findings.md, evidence/), `phases/P#-…/` (closure.md, findings.md,
> register.md, evidence/), and a top-level `register.md`.
>
> Work-item closure record sections: Scope (spec link, delivered, drift), Checklist (tests
> exist and pass, code reviewed, docs updated, no silent TODOs, config/migrations recorded,
> security-sensitive changes flagged), Evidence (PR/commit, CI link, test report, acceptance
> proof), Findings (each with id `F-WI042-1`, severity, decision — fix before close / carry
> forward / accept — carried items copied to the phase register), Sign-off (author, reviewer,
> date; status `closed` or `closed-with-findings`).
>
> Phase closure record sections: Scope reconciliation (planned vs delivered vs dropped/moved
> with reasons), Finding roll-up (every carried-forward finding resolved, accepted with owner,
> or re-planned), Cross-cutting checks (E2E, perf/cost vs targets, dependency/licence, docs,
> operational readiness), Retrospective, Evidence (release tag, demo, metrics, stakeholder
> acceptance), Sign-off (phase owner + one stakeholder; status `closed`,
> `closed-with-carryover`, or `not-closed` with dated re-audit).
>
> Two registers: `phases/P#/register.md` (one row per work item), and `docs/findings/register.md`
> (open findings only, across phases). Rule: nothing starts in phase N+1 while a Critical from
> phase N is open.
>
> Conventions: ids `WI-###`, `P#`, `F-<parent>-n`; evidence write-once; checklists versioned
> and stated per record; tag at phase close; redact secrets; ISO dates.
