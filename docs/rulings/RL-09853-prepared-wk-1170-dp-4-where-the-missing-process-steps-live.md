---
id: RL-9853
family: ruling
title: PREPARED, NOT RULED — WK-1170 map plan DP-4, where the missing process steps live
status: draft                  # PREPARED, NOT RULED — see the banner; RL's §1.2 subset has no draft (reported to the lead)
created: 2026-09-30
owner: decision-maker
tree: aa14e90dd77c7461aa35cc6461557b129959463f
phase: P2
work: WK-1170
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [WK-1169]
---

# RL-9853 (working id) — PREPARED, NOT RULED: WK-1170 DP-4, where the missing process steps live

> **Nothing in this record is ruled.** It was prepared at medium effort, under the
> maintainer's decision by delegation (lead channel, 2026-09-30 00:42 BST). It carries
> evidence, options and a **provisional** recommendation only. Do not rely on it. No slice
> may activate on it, the plan's DP-4 row is not resolved by it, and nothing under
> `docs/process/` or `.claude/` is amended by it. The ruling is a later pass at effort high.

## Evidence

**Trees.**
- The map plan is **PL-1276** (PR #930; first read on `origin/wk1170-map` at
  `25436a37ed6c00264b37066d794db618554bddac`, before it minted). It is now cited by section
  heading.
- *Refreshed 2026-09-30 at origin/main `0bc69b5b`.* `document-ids.md`, `audit-docs.py`,
  `doc-index.py`, the charters, the skills README and `process/checklists/` are unchanged since
  `aa14e90d`, so their file:line citations below still hold. `delivery-process.md` gained lines,
  and its one moved citation is updated below.
- Everything else was read at `origin/main` `aa14e90dd77c7461aa35cc6461557b129959463f`.
- The plan read its own premises at `19c395ac`, an ancestor of main.

**The row.** DP-4 is in PL-1276 §Decision points. It asks: *"Where does the 'process step per
transition' live once Slice 1 finds it?"* It is blocking for Slice 2 (§Tasks, "Task 2 — Slice
2: the missing steps written where they belong (docs-only)": "Blocked on DP-4"). At
`0bc69b5b` it is still open. Its "Resolved by" cell reads:
*"decision-maker, by `RL-`; the maintainer's line too if the answer amends `docs/process/`"*.

**Premises, checked at `aa14e90d`.**

| Premise | Status | Evidence |
|---|---|---|
| "§1.6 already names the role per action" | CONFIRMED | `docs/process/document-ids.md:148` has the columns *Owner — creates & amends · Accepts / decides · Reads & acts · Verifies & closes · Supersedes / retires*. |
| Option (a) amends a maintainer-owned file | CONFIRMED | `document-ids.md:167`: *"Reference — `process/` · maintainer; amendments arrive as `RFC-` + `RL-`"*. |
| Option (b) is a second transcription, like `_OWNERSHIP_TABLE` | CONFIRMED | `scripts/doc-index.py:920-947` transcribes §1.6's Owner column once. |
| Option (c): "check 38 as the enforcement" | **DIFFERS** | Check 38 is *"Loop signal, warn-only"* (`document-ids.md:234`). Its sub-clauses are *"not implemented yet; this line reports the population they will run over"* (`scripts/audit-docs.py:3465`). Even when built, it detects records that nothing cites. It does not test whether a step exists for a transition, and it never fails the gate. |
| "What is missing is the step inside the role's skill" | Not verifiable yet | This is Slice 1's finding, stated in advance. |

**Precedent the plan does not name.**
- `docs/process/checklists/work-item-close.md` (`owner: maintainer`) already names a step and
  points at its skill: *"Follow the `close-workstream` skill"* (`:14`). `phase-close.md` does
  the same. So steps are already *named* under `process/` and *specified* in skills: a hybrid
  that option (c)'s "only" would exclude.
- The "one source, point from process" convention is already written down:
  - `delivery-process.md:31`: *"Tool scope lives once, in each role's own file"*;
  - `:257-260` (was `:241-243` at `aa14e90d`; the text is unchanged): *"Not restated here; one
    source, not two."*
- `.claude/skills/README.md:73-75` has a `Creates` column naming the family each skill mints.
  It covers the create transition only.
- `document-ids.md:169`: skills are amended by *"the five roles already permitted; lead
  approves"*. Under (c), the skill half therefore needs no maintainer line. The charter half
  does, because charters are `owner: maintainer` (for example
  `.claude/roles/decision-maker.md` front matter). The plan itself routes charter gaps to
  WK-1169 (PL-1276 §Tasks, Task 1 and Task 2: "a charter gap … goes to WK-1169 as an `FD-`").

## Options

| | Option | For | Against |
|---|---|---|---|
| (a) | A new §1.6 column naming each transition's step (RFC- + RL-) | One table answers "who does what, by which step" | Amends a maintainer-owned file to restate what the skills carry, which is RFC-756's drift |
| (b) | A table `doc-index.py` generates from a declared structure, with a drift check | Mechanically checkable | A second transcription, the `_OWNERSHIP_TABLE` pattern |
| (c) | The owning skill or charter only; Slice 1's record is the evidence; check 38 enforces | One source per step | Its enforcement premise is false (see above), and "only" excludes the maintainer-owned checklists that already name steps |
| (c′) | **Not in the plan.** (c) on location: the step is specified in its owning skill, and a charter gap goes to WK-1169 as the plan already says. Existing `process/checklists/` pointers stay pointers. Enforcement is stated honestly: either a named new check, or "by audit at each Work close" | Keeps (c)'s single source without a false enforcement claim | Unless a check is built, a missing step is caught only by an auditor |

## Provisional recommendation: (c′). This departs from the planner's (c) on enforcement, not on location.

- **Location.** The planner's reasoning holds: a step lives once, in its skill, and the
  `process/` checklists point at it rather than restating it.
- **Enforcement.** Check 38 cannot be it, so the ruling must choose:
  1. **A named check**, specified in the Slice 2 leaf plan. For example: every §1.6 transition
     cell names a role whose charter or skill carries a step for it. This needs §1.6's cells
     parsed, which is the same dependency as WK-1169 DP-2 (c) (working id 9854).
  2. **An explicit statement** that enforcement is by audit at each Work close. This is the
     cheaper choice, and it is honest.

  The provisional answer is **(2) now, and (1) only if WK-1169's parser lands**: the
  mechanical check then costs one rule, not a parser.
- **Charter gaps** go to WK-1169, as PL-1276's Task 2 already routes them. A charter edit
  needs the maintainer's line, so (c)'s "or charter" is not available inside WK-1170.

## Ruled

**Nothing.** This section is held for the high-effort pass.

## What it obliges

**Nothing yet.** Under (c′), it would oblige:
- Slice 2 to write each missing step into its skill, with the lead's approval
  (`document-ids.md:169`);
- the Slice 2 leaf plan to state the enforcement choice;
- no `docs/process/` amendment.

## Acceptance — the violation that must become detectable

**Not set, because nothing is ruled.** Under (c′)(1): a §1.6 transition whose role has no
step in its skill or charter fails the named check on a deliberately broken fixture. Under
(c′)(2): the Work close audit's checklist names the step sweep, and a closure record without
it is incomplete.
