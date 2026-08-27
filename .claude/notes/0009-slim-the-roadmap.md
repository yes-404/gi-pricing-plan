# NT-0009 — Slim the roadmap: split the plan from the archive

| | |
|---|---|
| **Raised** | 2026-08-27, maintainer — "create a note for research and discuss for slim roadmap.md, current the file mixed with material irrelevant to roadmap" |
| **Status** | `accepted` — maintainer accepted 2026-08-27: the historical record (closure records, plan reviews 1–5, the retrofit-impossible list) moves to `docs/audit/`, and `docs/roadmap.md` keeps only the forward-looking plan. The restructure is scheduled after W7 |
| **Deliverable** | Spec-change-first: a restructured `docs/roadmap.md` that separates the forward-looking plan from the historical record. No code |
| **Owner** | Maintainer accepts the structure · Claude drafts the restructure and files it |
| **Lands in** | `docs/roadmap.md` (restructure); possibly a new secondary file for closure records and plan reviews |
| **Trigger** | After W7; before the next roadmap edit that would otherwise add another mixed section |

---

## Request, refined

The maintainer wants `docs/roadmap.md` slimmed, because it has grown into a file that is
at once the **plan** (workstream table, phase boundaries, open questions) and the **archive**
(closure records, plan-review prose, the retrofit-impossible list, the decision-gate table).
The concrete proposal below (a `ROADMAP.md` with header, vision, goals, scope, phase
overview, phase detail, milestones, dependencies, decision log, backlog, change history)
shares one core intent: **keep detail out of the roadmap, and link to where it lives** — the
specs, the ADRs, the tracker.

## Claude's assessment (kept separate from the maintainer's words)

The proposal is largely a restatement of machinery this repository already owns, and its
genuine value is the **separation it names**, not the structure it lists. Stated plainly:

1. **Most of the proposed sections already exist elsewhere, and that is correct.** The
   decision log is `docs/adr/`. The change history is the plan-review sections inside the
   roadmap. The open questions and their disposition are the roadmap §10 decision-gate table
   plus `docs/open-questions.md`. The per-work-item detail is the slice-map and per-slice
   plans. Duplicating any of these in a new "decision log" or "change history" section is the
   exact failure NT-0003 records.
2. **The one real insight is: the roadmap is both plan and archive.** Closure records,
   plan reviews 1–5, and the retrofit-impossible list are *history* — they answer "why did
   the plan change", not "where are we now". Keeping them in the same file as the current
   workstream table is what makes `docs/roadmap.md` read as mixed. The slim fix is to split
   those two: a forward-looking plan at the top, the archive below a clear fold, or a second
   file.
3. **The status vocabulary would change.** The repo's workstream status is `open`/`closed`
   (plus the roadmap's own annotations). The proposal's `planned · in progress · at risk ·
   blocked · closed` is a real change with audit consequences (the closure tripwire greps for
   the `closed` form) — it is not a relabel.
4. **"Every phase has a stated outcome and exit criteria" is already CLAUDE.md §9 + §14.**
   Phase 1b's exit criterion is `wf-01` end to end; the §14 plan review is the exit-criteria
   check. The proposal's phase-outcome row would restate this, and restating is drift.

The three decisions that matter before anything is built: (a) does the archive move to a
second file or below a fold in the same file, (b) does the status vocabulary change, and
(c) does the roadmap gain a `WI-###` work-item table or keep linking to the slice-map.

## Decision

Maintainer accepted 2026-08-27. The historical record — closure records, plan reviews 1–5,
and the retrofit-impossible list — moves out of `docs/roadmap.md` into `docs/audit/` (see
[[NT-0008]]). The roadmap keeps only the forward-looking plan: the header, the workstream
table, the phase boundaries, and the §10 decision-gate table. The two remaining sub-questions
stay open and belong to the restructure work, not to this note: whether the status vocabulary
changes, and whether work items appear in the roadmap or only by link.

## Next step

Schedule the restructure as its own workstream after W7: move the archive to `docs/audit/`,
slim the roadmap, and re-run the closure tripwire and `audit-docs.py` to prove no requirement
or status is silently dropped. The notes NT-0008 and NT-0009 land together.

## Original wording

Kept verbatim below, corrected for grammar and punctuation only — never for wording,
structure or meaning. The maintainer supplied the "Project Roadmap Structure" proposal and a
one-line instruction; a second block of text that described a different repository's layout
is excluded, as it is not the maintainer's proposal.

> slim roadmap.md, current the file mixed with material irrelevant to roadmap.

> # Proposal: Project Roadmap Structure
>
> Status: Draft — for discussion. Author: @name. Date: 2026-08-27. Reviewers: @lead, @pm.
> Decision needed by: <date>.
>
> ## 1. Summary
> Proposes a single `ROADMAP.md` in the repo that states what we plan to deliver, in which
> phase, by when, and what has changed along the way — the one place anyone can look to answer
> "where are we, what's next, and why did the plan change".
>
> ## 2. Problem
> The plan lives in several places and they disagree; phases lack written outcomes or exit
> criteria; scope moves between phases without a record; decisions that shaped the plan are
> hard to find later.
>
> ## 3. Goals
> One current version-controlled view; every phase has a stated outcome and exit criteria;
> scope and status changes are recorded with dates; maintainable in a few minutes a week.
> Non-goals: replacing the issue tracker, or detailed estimation and resourcing.
>
> ## 4. Proposal
> `ROADMAP.md` at repo root, changed via PR, one named owner. Structure: header, vision,
> goals & success metrics, scope, phase overview, phase detail (outcome, exit criteria
> checklist, work-item table), milestones & timeline, external dependencies, decision log,
> backlog/parked, change history. Status vocabulary: `planned · in progress · at risk ·
> blocked · closed`. Rules: a phase is `closed` only when all exit criteria are ticked; moving
> a work item between phases is recorded; keep detail out of the roadmap — link to specs,
> tickets and ADRs; update at least weekly and at every phase boundary.
>
> ## 5. Options considered
> A. Tracker only — no new artefact, no narrative or decision log. B. Slide/wiki roadmap —
> familiar but not version-controlled. C. Proposed `ROADMAP.md` in repo — versioned, reviewed
> via PR, lives next to the work. D. Dedicated roadmap tool — rich but another system.
> Recommendation: C.
>
> ## 6. Costs and risks
> ~10 minutes a week plus ~30 minutes per phase boundary. Main failure mode is staleness —
> mitigations: named owner, "last updated" in the header, review as a standing weekly item.
> Keep the roadmap at work-item granularity; task-level detail stays in the tracker.
>
> ## 7. Rollout
> Agree the proposal; create `ROADMAP.md` from the template; fill vision, goals, scope, phase
> overview; populate the current phase in detail; review after the first phase boundary.
>
> ## 8. Open questions
> Repo root or `docs/`? Work items in the roadmap or only phases with tracker links? How much
> of the decision log here versus in ADRs? A generated stakeholder summary? Who owns it if the
> lead changes?
>
> ## 9. Decision
> Outcome: Accepted / Accepted with changes / Rejected / Deferred, with notes and date.
