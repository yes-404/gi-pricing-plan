---
id: RL-1318
family: ruling
title: WK-1170 DP-4 decided — a missing process step is written in its owning skill, and a Work-close sweep step enforces it
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: eeda8f4ba20d247ac18d6a35d7f81589c8527ed2
phase: P2
work: WK-1170
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1276, PL-1277, WK-1169]
---

# RL-1318 — WK-1170 DP-4 decided — a missing process step is written in its owning skill, and a Work-close sweep step enforces it

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared at effort `medium` (PR #940, head `8bfd305a`, "PREPARED, NOT
RULED"). Its evidence is kept below as it was prepared, and **the decision is in "Ruled"**.
It was minted 2026-09-30 as RL-1318 (hand-assigned in the lead's batch plan, batch 5, under the
maintainer's option (B)); it was filed under working id 9853.

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
- *Re-verified 2026-09-30 at `eeda8f4b` for this ruling.* `git diff --stat 0bc69b5b eeda8f4b --
  docs/process .claude scripts docs/plans/PL-01276* docs/plans/PL-01277* CLAUDE.md` prints
  nothing. Each premise the ruling rests on was re-read at `eeda8f4b` (see "Presence and
  absence, as verified" in "Ruled").
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

## Prepared recommendation (superseded by "Ruled"): (c′). This departs from the planner's (c) on enforcement, not on location.

- **Location.** The planner's reasoning holds: a step lives once, in its skill, and the
  `process/` checklists point at it rather than restating it.
- **Enforcement.** Check 38 cannot be it, so the ruling must choose:
  1. **A named check**, specified in the Slice 2 leaf plan. For example: every §1.6 transition
     cell names a role whose charter or skill carries a step for it. This needs §1.6's cells
     parsed, which is the same dependency as WK-1169 DP-2 (c) (`RL-1319`).
  2. **An explicit statement** that enforcement is by audit at each Work close. This is the
     cheaper choice, and it is honest.

  The provisional answer is **(2) now, and (1) only if WK-1169's parser lands**: the
  mechanical check then costs one rule, not a parser.
- **Charter gaps** go to WK-1169, as PL-1276's Task 2 already routes them. A charter edit
  needs the maintainer's line, so (c)'s "or charter" is not available inside WK-1170.

## Ruled

### Presence and absence, as verified at `eeda8f4b`

| Claim | Verdict | How it was verified |
|---|---|---|
| Check 38 enforces a step per transition | **absent** | The owning module, `scripts/audit-docs.py`, was read at `check_loop_signal` (`:3434-3468`). Its docstring says "warn-only … never fails the gate, only notes", and its only output is a note (`:3461-3467`): "the four warn-only sub-clauses … are not implemented yet". `document-ids.md:234` gives the same row. It never tests whether a transition has a step. |
| A step is already named under `process/` and specified in a skill | **present** | `docs/process/checklists/work-item-close.md` (`owner: maintainer`, `:6`) says at `:14`: "Follow the `close-workstream` skill", as a link to that skill. |
| The one-source convention | **present** | `docs/process/delivery-process.md:31` ("Tool scope lives once, in each role's own file") and `:257-260` ("Not restated here; one source, not two."). |
| Who may amend a skill | **present** | `document-ids.md:169`: "the five roles already permitted; lead approves". |
| Who owns `process/` | **present** | `document-ids.md:167`: "maintainer; amendments arrive as `RFC-` + `RL-`". |
| A machine-readable role per §1.6 action | **absent** | §1.6 (`document-ids.md:144-173`) is a prose table. The one structured transcription, `_OWNERSHIP_TABLE` (`scripts/doc-index.py:924-947`), covers the Owner column only. `ownership_matrix()` (`:958-969`) assigns a role to a family whenever the role's name appears in the cell text. At `eeda8f4b` that already lists the planner as an owner of `work (WK)` and the lead as an owner of `proposal (RFC)` (`docs/INDEX.md:1451`, `:1454` at `eeda8f4b`). So a mechanical per-transition check has no reliable input today (`RL-1319` rules on this). |

### DP-4 — option (c′): the step lives in its owning skill; enforcement is a named Work-close sweep step, not check 38

1. **Location.** A missing step that Slice 1 finds is written **in the owning skill**
   under `.claude/skills/`, with `.claude/skills/README.md` in the same commit
   (`CLAUDE.md` §12). A skill is amended by "the five roles already permitted; lead
   approves" (`document-ids.md:169`), so this needs no maintainer line and no `process/`
   amendment. A `process/checklists/` file that already points at a skill keeps pointing; it
   is not made to restate the step (`delivery-process.md:257-260`). **No §1.6 column is
   added** (option (a)), and **no generated table** (option (b)): each would be a second
   statement of what the skill carries.
2. **A charter gap is not written in WK-1170.** It is filed as an `FD-` routed to WK-1169, as
   PL-1276 Tasks 1 and 2 already say. Charters are maintainer-owned (`document-ids.md:168`).
3. **Enforcement — the planner's (c) premise is false, and this replaces it.** Check 38 is
   warn-only and unimplemented, and it never tests for a step (the table above). **The
   enforcement is a named step in the `close-workstream` skill**: at every Work close, for
   each §1.2 family or `kind` whose transitions the Work added or changed, the auditor
   confirms the transition names its step (a skill section, a charter line, a script function
   or a check number), or files an `FD-`. WK-1170 Slice 2 writes that step into
   `close-workstream`, as one of the steps it writes, so the sweep exists from the Work that
   found the gaps onward.
4. **No mechanical check is ruled.** A check that "every transition has a step" needs a
   machine-readable role per §1.6 action, and there is none (the table above). If `RL-1319`'s
   exact owner table is later extended to all five actions, a mechanical check can be
   proposed then, as a new `OQ-` or `FD-`. This record creates no obligation for it.

## What it obliges

- **This commit:** this record only.
- **PL-1276 (the planner's file, not edited here):** DP-4's "Resolved by" cell cites this
  record once it is minted. Task 2's enforcement premise ("check 38 as the enforcement")
  is replaced by item 3. No maintainer line is needed, because no `docs/process/` file is
  amended.
- **WK-1170 Slice 2:** each missing step Slice 1 records, written in its owning skill with
  the README row, and the `close-workstream` sweep step of item 3.

## Acceptance — the violation that must become detectable

The violation: **a transition with no step, discovered only by chance.**
- *Slice 2:* for each audit-record row that named a gap, the row is re-read at the slice's
  tree and names a skill section, as PL-1276 Task 2's gate already requires.
- *Slice 2:* `close-workstream` names the sweep step, and the first Work closure record after
  Slice 2 carries the sweep's result: each transition the Work added or changed, and its step
  or its `FD-`. This enforcement is by reading, stated as such and never claimed to be
  mechanical. A closure record without the sweep is incomplete under `close-workstream`, and
  the lead's review returns it.
