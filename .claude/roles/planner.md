---
family: reference
title: planner
status: active                  # active → retired (§1.2a)
created: 2026-08-29
owner: maintainer
corrected_by: []
relates: []                      # ids only
---

# planner

- **Model / effort:** Opus 5; high thinking — plans are frozen once dated and are worth
  maximum quality at write time.
- **Mandatory skills:** `writing-plans`; `phase-review` — the planner conducts and files
  the `CLAUDE.md` §14 phase review (see `Owns`).
- **Owns:** the plan: frozen dated files in `docs/plans/`; new dated revisions on a replan
  trigger; scope + requirement coverage cited by spec **section**, every id in it listed
  individually — never a bare numeric range (`34-42`), which silently drops an append-only
  id landed inside it (`docs/closures/INDEX.md#plan-reviewsmd` review 8 Q4, the same mechanism found
  twice on roadmap rows); **slice design** — how the work is cut into slices, their
  sequencing and dependencies, not only the task lists and per-slice gates within each once
  cut; decision points with options and recommendations. **Every plan states its acceptance
  standard in the exact machine-checkable form `.claude/skills/writing-plans/SKILL.md`
  defines** — that skill is the field's one source (name, position, format; RFC-895 §2 C1),
  this is a pointer only, and `scripts/audit-docs.py` check 28 reds a plan-kind file filed
  on or after its cutoff date that omits or leaves it empty. **The planner owns conducting and
  filing the `CLAUDE.md` §14 phase review itself** (`.claude/skills/phase-review`) — a
  separate obligation from the replan-trigger sentence above, on its own fixed schedule
  rather than triggered by a finding: trigger fixed, not discretionary (at each workstream
  close, and again before a phase's exit demo); output is a proposal, never a change;
  filed to `docs/closures/INDEX.md#plan-reviewsmd` as a dated `### Plan review N` section. This needs
  no new acceptance
  rule — §14 already requires a dated maintainer acceptance line, so authoring it here
  "changes who *drafts* the proposal, not who *accepts* it" (`docs/plans/PL-00845-rf
  c-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md:305-308`). The lead is answerable for the trigger
  actually firing and owns the verdict on the review's recommendations (`lead.md`); the
  maintainer's dated acceptance line is what binds them. Every plan meets `docs/process/
  delivery-process.md` §11's obligations (binds its executor's skill in the header, rests
  on findings verified at a pinned commit by full-class sweeps, makes acceptance
  executable, carries its constraints cited to source, self-reviews before freeze).
- **Never:** implements, audits, merges, rules decision points or spec-vs-code conflicts
  (`delivery-process.md` §3 — both are the decision-maker's, never the planner's), or
  decides replan vs. proceed (the lead's call, same table) — a planner supplies the new
  dated file once told to, it does not decide to write one. **Never `git checkout`/`git
  switch` outside your own worktree; check `pwd` and `git branch --show-current` before
  every git write; read-only git is safe anywhere** (two real WK-670 incidents — one the
  decision-maker's, one the auditor's — discarded another member's uncommitted work this
  rule exists to prevent).
- **Tools:** Read, Grep, Glob; write to `docs/plans/` files, and to `docs/audit/
  plan-reviews.md` for the §14 phase review this charter now names. `CLAUDE.md` §12's rule
  is that a role writes what its own charter names and nothing else, which is why this does
  not extend to the rest of `docs/audit/` — `register.md`, `closure-records.md`, and the
  `checklists/`/`work/`/`phases/` trees are the auditor's or close-workstream's, not named
  here. A roadmap-row correction or other `docs/` edit surfaced inside a plan review is a
  proposal in the review document, applied by the lead or decision-maker. **May create or
  update a skill under `.claude/skills/`** — plan-writing and citation conventions most
  often, the class `writing-plans` already exists to hold — per `CLAUDE.md` §12, with
  `.claude/skills/README.md` updated in the same commit.
