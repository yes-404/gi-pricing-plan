---
id: PL-844
family: plan
kind: leaf
title: RFC-840 / RFC-841 Adoption — Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-29
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-29-nt-0010-0011-adoption.md
---

# RFC-840 / RFC-841 Adoption — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use the project skill
> `subagent-driven-development` (recommended) or `executing-plans` to implement this plan
> task-by-task — skills are invoked by their registered project name; no plugin namespace
> is involved. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the process documentation, agent settings and role definitions that
`docs/plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md` ("the rulings record") rules
adopt or amend, in the dependency order the lead fixed (governing pointer + process
documents → drift fixes this plan's own sweep found → role definitions → checklist
reconciliation → the two maintainer-gated items, last and explicitly blocked → mechanical
automation, deliberately not built in this pass). **No change to `docs/specs/` and no
product code** — this is documentation and role definitions only, per RFC-840's own
Deliverable line (`.claude/rfcs/RFC-00840-a-layered-slice-based-workflow-project-phase-work-slice-gated-at-every-layer.md:7`).

**Architecture:** The rulings record is the frozen specification this plan implements —
every task below cites the Part B/C row that authorises it and does not re-argue it. Two
rows stay open (Part A1, A2); this plan builds everything that does not depend on their
answer and marks everything that does, rather than guessing or silently designing around
either. `CLAUDE.md` carries only a pointer; the process content itself lives in a new
`docs/process/` category, mirroring how `docs/roadmap.md` and `docs/specs/` already work —
the root file points, the detail lives where the detail is.

**Tech Stack:** Markdown documentation and `.md` role-definition files only.
`scripts/audit-docs.py` is the only executable gate this plan's tasks touch (no new check
is added by this plan — see Task 4's finding).

**Spec:** `docs/plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md` Parts A–D (the
governing record); `.claude/rfcs/RFC-00840-a-layered-slice-based-workflow-project-phase-work-slice-gated-at-every-layer.md` and
`.claude/rfcs/RFC-00841-per-agent-model-thinking-effort-and-skill-bindings-for-the-seven-roles.md` (the source proposals, cited only
where the rulings record does not already quote the needed text verbatim). No `FR-`/`NFR-`/
`OQ-` id is defined, changed, or superseded by this plan — this plan mints no requirement
ids of any kind.

**Slice source:** This is a single Work item (the RFC-840/841 adoption) sliced directly
into Tasks below — no parent map file exists yet because Part C row 3 rules "Project" needs
only the label, not a new artifact (`docs/plans/PL-00845-rfc-840-rfc-841-adoption-recon
ciliation-and-rulings-2026-08-29.md:417`). Team-lead's dispatch (`task_assignment` id 5, 2026-08-29T11:29:31Z) is the
slicing authority for the ordering used below.

**Highest ids in use at the anchor (`3b66ede`):** N/A — this plan mints no `FR-`/`NFR-`/
`OQ-`/`NT-` id. `.claude/notes/` currently ends at RFC-841; this plan creates no new note.

## Global Constraints

- **Frozen plan, dated revisions only.** This file is frozen at 2026-08-29. Any correction
  after freeze is a new dated file, never an in-place edit (`CLAUDE.md` §10; `docs/plans/
  README.md`).
- **Worktree hygiene.** Own worktree; never `git checkout`/`git switch` outside it; check
  `pwd` and `git branch --show-current` before every git write; read-only git is safe
  anywhere (`TEAM-STRUCTURE.md` §5, carried into every role file this plan creates — Task 2).
- **`audit-docs.py` clean before every commit** (`CLAUDE.md` §11).
- **PR-only; lead-only merge; CI verified on the exact head** (RFC-841 §3 delta 3, adopted
  as-is — rulings record Part C, RFC-841 row 3).
- **Frozen requirement ids elsewhere are not touched.** This plan's tasks never edit
  `docs/specs/`; if a task appears to need a spec change, that is a sign the task is out of
  this plan's scope, not a reason to widen it.
- **A dated correction is recorded beside the fact it corrects, never by silent
  replacement** (the rulings record's own convention, Part B8; the notes' `RFC-778` custody
  rule). Every drift fix in Task 2 follows this form.

## Findings the plan is built on

Each verified against shipped source at `3b66ede` this session, by a full-class sweep, not
a sample (obligation 4). Every finding below is either already in the rulings record (cited,
not re-derived) or newly found while sweeping for this plan and reported here because
nothing else would carry it.

### Finding 1 — `superpowers:` namespace references: the true class is wider than "four", and only one member is the defect

Full-repo sweep (`grep -rn "superpowers:" --include="*.md" .`) returns hits in eleven
distinct files, not one:

- **The defect (in scope, Task 2):** `.claude/skills/writing-plans/SKILL.md` — four hits
  (lines 16, 64, 169, 173). This file is **adapted for this project** (its own text says
  "Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md`... committed and audited" —
  project-specific framing, not upstream boilerplate), so a residual `superpowers:` self-
  reference is a leftover, not a vendored feature. Ruled in scope by Part B7.
- **Not in scope — genuinely vendored, cross-referencing the upstream Superpowers
  ecosystem by design:** `systematic-debugging`, `executing-plans`, `writing-skills` (two
  files), `using-superpowers`, `subagent-driven-development`, `test-driven-development/
  writing-good-tests.md`. These files' own content is still close to unmodified upstream
  form and their `superpowers:X` references point at other Superpowers skills in that same
  ecosystem — exactly what `CLAUDE.md` §12's vendoring rule preserves ("vendored files stay
  as upstream wrote them... every deviation recorded in the README rather than made
  silently"). No ruling touches these; this plan does not either.
- **Not in scope — frozen historical artifacts:** every `docs/plans/*.md` file that copied
  the (buggy) template before this plan's Task 2 fixes it — dozens of files, `2026-08-18`
  through `2026-08-28`. `docs/plans/README.md`'s own convention is that a filed plan is
  frozen at its date; retroactively editing every past plan's header would violate that
  convention for a cosmetic defect none of them depended on functioning. Fixing the
  **template** (Task 2) stops new instances; it does not and should not touch the old ones.
- **Also not in scope, recorded for completeness:** `.claude/rfcs/0011-…md` lines 35 and
  193 use `superpowers:` correctly, as a negated noun ("no `superpowers:` namespace is
  involved") — not a broken reference.

### Finding 2 — `docs/README.md`'s suite index is missing two top-level categories, not one

`docs/README.md`'s `## Map` table (lines 6–24) lists `specs/*`, `workflows/`, `contracts/`,
`adr/`, `skills-map.md`, `open-questions.md`, `closures/CR-00709-phase-0-specification-status.md`, `roadmap.md`. It has no
row for `docs/process/` (does not exist yet — this plan's Task 1 creates it) or for
`docs/research/` (already exists, holds four documents at this sha: `track-a-findings.md`,
`w6b-6b-prediction-material.md`, `w8-spike-resolution.md`, `zen-evaluate-concurrency.md`).
The `research/` gap is task board item #17, found by the lead independently while reviewing
PR #321, and explicitly sequenced to land here: *"fold into the adoption's step-4 slices,
where `docs/README.md` is already being touched for `docs/process/`."* Task 1 adds both rows
in the same edit, once, rather than twice — the reason item #17 gives for deferring itself
into this plan.

Both gaps are the same mechanism plan review 8 named for a different module (`docs/audit/
plan-reviews.md` Question 4, second mechanism): a document that summarises a directory in
free prose, going stale as the directory grows, with nothing structurally linking the
summary to what it summarises. This plan does not build a new check for it (out of scope —
seeSelf-review); it only fixes the two instances found.

### Finding 3 — the eight-vs-seven specialist miscount exists in *both* notes; only one instance is corrected

Part B8 rules RFC-840's claim ("`.claude/agents/` holds eight delegable specialists")
corrected to seven, and PR #320 already applied it in place with a dated note
(`.claude/rfcs/0010-…md:58-61`, "*(corrected 2026-08-29 — a directory listing that
included its own `README.md` read as eight...)*"). Direct read confirms this landed
correctly — no discrepancy between the rulings record's citation and the file (a check
worth doing explicitly, since a citation two steps removed from its source is exactly what
this project's own standards warn against re-trusting unread).

**`.claude/rfcs/RFC-00841-per-agent-model-thinking-effort-and-skill-bindings-for-the-seven-roles.md:58` carries the identical
miscount — "`.claude/agents/` holds eight delegable specialists and no role definitions" —
and has not been corrected.** Part B8's own text names only RFC-840; it does not claim to
have swept RFC-841 for the same sentence, so this is not a case of re-opening B8 — it is
the sibling instance a full-class sweep is supposed to catch and B8's own scope never
claimed to reach. Task 2 fixes it, in the identical dated-correction style RFC-840 already
uses, so the two notes read consistently.

### Finding 4 — the existing closure checklists already substantially satisfy RFC-840's audit obligations; no new checklist file is needed for "Project"

`docs/process/checklists/phase-close.md` and `work-item-close.md`, read in full: both already
use "phase" / "work item" (workstream, slice, or PR) / "slice" terminology identical to
RFC-840's Project→Phase→Work→Slice hierarchy, already point at `docs/audit/phases/<phase>/`
and `docs/audit/work/<id>/` record conventions, already carry the §13 four-verdict /
`docs/findings/register.md` carry-forward discipline, and already state "a finding with no
verdict is silence, which §13 forbids" — matching RFC-840 §12's obligations closely enough
that the rulings record calls this section "Agrees strongly" (`...rulings.md:426`). Part C
row 3 rules Project needs "only the label" — no new artifact — so no `project-close.md`
checklist is created. Task 3 (checklists) is therefore a **reconciliation and one
cross-reference note**, not a rewrite, and Task 3's gate proves that with a diff, not an
assertion.

### Finding 5 — the full blast radius of Part A1/A2, enumerated so nothing is silently designed around either answer

Every location whose *final* content depends on which option the maintainer accepts,
swept once here rather than re-discovered task by task:

| Location | Depends on | What differs by option |
|---|---|---|
| `docs/process/delivery-process.md`, the human-checkpoint section (from RFC-840 §9) | A1 | (a) checkpoint stays at Work/workstream close, escalation-vs-acceptance distinction adopted; (b) checkpoint moves to Project close only, §13/§14 gain an explicit no-per-workstream-checkpoint rule; (c) hybrid — Work close auto except a register-bound defer |
| `CLAUDE.md` §13/§14 | A1, option (b) only | Only option (b) states amending them; (a) and (c) need no `CLAUDE.md` edit beyond Task 1's pointer |
| `CLAUDE.md` §12, the role-write-authority sentence | A2 | (a) names per-role `docs/` write scope explicitly; (b) restores the literal no-write rule, reversing current practice; (c) a third, artifact-type rule matching neither current practice nor either note |
| `.claude/agents/README.md`'s dividing line | A2, option (a)'s bundled belt-and-braces sentence | Only meaningful under (a); (b) and (c) do not call for this specific sentence |
| `.claude/roles/planner.md`, `decision-maker.md`, `auditor.md`, `lead.md` — each role's docs-write tool-scope line | A2 | (a) states the scope explicitly per role; (b) removes docs-write from all four, adding a lead-mediated step; (c) permits dated records/register rows but not in-place spec edits |
| `.claude/rfcs/0010-…md` and `0011-…md`'s `Status` field | Both A1 and A2 | Stays `open` until both close (rulings record Verification section, `...rulings.md:497-498`) |

Every row above is a **named, bounded exclusion** in the relevant task below — built once
the maintainer accepts, never guessed at now.

## Task 1: `docs/process/` category, the `CLAUDE.md` pointer, and the two missing index rows

**Files:**
- Create: `docs/process/delivery-process.md`
- Create: `docs/process/agent-settings.md`
- Modify: `CLAUDE.md` (§12, add a pointer paragraph — exact anchor and text in Step 2)
- Modify: `docs/README.md` (`## Map` table, two new rows)

**Interfaces:**
- Consumes: rulings record Part C rows (RFC-840 §§1, 3, 5, 6, 7, 8, 10, 11, 12, 14, 15 —
  all `Adopt`; RFC-841 §§1, 2 [non-A2 fields], 3 — all `Adopt`); Part B1 (parallelism
  carve-out), B2 (ultrathink, already correctly worded — confirm, do not re-word), B3
  (instrumented defaults), B6 (the name is not "workflow" — this task names it
  `delivery-process.md`, satisfying B6's only constraint).
- Produces: the two document paths every later task and role file cites; the `## Map` row
  text later tasks do not need to touch again.

- [ ] **Step 1: Write `docs/process/delivery-process.md`**

Content, adapted from `.claude/rfcs/0010-…md`'s "Original wording" section (lines
242–660) with the rulings record's amendments folded in, not the original text verbatim:

```markdown
# Delivery Process — Project → Phase → Work → Slice

Adopted 2026-08-29 from RFC-840 (`.claude/rfcs/RFC-00840-a-layered-slice-based-workflow-project-phase-work-slice-gated-at-every-layer.md`),
reconciled and ruled in `docs/plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md`.
This document is the process specification `CLAUDE.md` §12 points at. It governs how a
Claude Code team does the work in this repository — a distinct concept from
`docs/workflows/WF-698…05`, the cross-module *domain* journeys (`CLAUDE.md` §4).

## 1. Purpose

[RFC-840 §1 content — the four-layer hierarchy, gated at every layer, one human checkpoint.
NOTE: the checkpoint's layer is Part A1, unruled — see §2 below.]

## 2. Human checkpoint — BLOCKED pending Part A1

**Not yet ruled.** Until `docs/plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md`
Part A1 carries a dated maintainer acceptance line, this section states only the
interpretation already in force, not any of A1's three options: workstream (Work-layer)
close requires the maintainer's acceptance, evidenced by WK-664, WK-669 and WK-670 all closing on
the maintainer's word (never the auditor's or the team's own verdict). This is standing
practice, not yet a written rule anywhere else, which is why RFC-840 exists to write it
down (Part D, item silent-but-real). Do not read this section as final; re-read Part A1's
acceptance line before relying on it.

## 3. Roles

[RFC-840 §2's role table verbatim — Lead/Planner/Decision-maker/Auditor/Executor/Watcher/
Reporter with responsibility column; "Suggested tool scope" column replaced with "see
`.claude/roles/<role>.md`" since Task 3 is where tool scope actually lives, avoiding a
second copy of a fact this document does not need to own.]

## 4. Hierarchy

[RFC-840 §3 — Project (the whole-repository scope `CLAUDE.md` §1 already names informally;
no new artifact, per rulings record Part C row 3) → Phase (`CLAUDE.md` §9) → Work
(workstream) → Slice.]

## 5. Per-layer flow

[RFC-840 §4, amended per rulings record Part C row 4 / RFC-841 §3 delta 1: auditor
proposes; **lead** adopts/amends/rejects and merges; decision-maker rules decision points
and spec conflicts only.]

## 6. Slice layer (TDD cycle)

[RFC-840 §5's TDD cycle, confirmed against `test-driven-development` / `python-test`
skills — Adopt. Step 6's "who decides fix/accept/defer" text uses §5's wording, not the
original's — same correction as §5 above. The enforcement *hook* RFC-840 §5 step 4 assumes
is noted as **not built** — an implementation gap for whoever executes automation later,
not a document conflict (rulings record Part C row 5).]

## 7. Escalation guards — instrumented defaults, not fixed governance

[RFC-840 §6's caps (≤1 Project/Phase/Work, ≤2 Slice) adopted **as instrumented defaults**
per Part B3: log every replan/audit-fix loop iteration and re-audit count from the first
slice under this process (the pilot — see Task 5's note on WK-671); revisit the numbers after
a workstream's worth of data. The ≤2 Slice cap is not a settled ceiling — W10-3A's own
history sits exactly on it.]

## 8. Parallelism

[RFC-840 §7 adopted **with the Part B1 carve-out**: sequential processing of a layer's
children (no two Slices run at once), unrestricted read-only fan-out for evidence-gathering
within a layer — `dispatching-parallel-agents` is the named precedent skill.]

## 9. Global findings register

[RFC-840 §8 — Adopt as-is; this *is* `docs/findings/register.md`, verbatim-matching per the
rulings record's own verification. No new file.]

## 10. Required artifacts

[RFC-840 §10's list, with names corrected: process spec = this document; agent settings =
`docs/process/agent-settings.md`; roadmap/plan/open-questions/register = existing files
unchanged; role definitions = `.claude/roles/*.md` (Task 3), **not** `.claude/agents/`
(rulings record Part B11 — that directory is reserved for the delegable specialists
catalogued in `.claude/agents/README.md`, a different concept).]

## 11. Plan file obligations

[Cross-reference only: "See `.claude/skills/writing-plans/SKILL.md` and `docs/plans/
README.md` — those conventions are stronger than anything this document would add, per
RFC-840 §11's own words." Do not restate the eight obligations here; one source, not two.]

## 12. Audit record obligations

[Cross-reference only: "See `.claude/skills/close-workstream/SKILL.md`, `.claude/skills/
phase-review/SKILL.md`, and `docs/audit/checklists/`." Same reasoning as §11.]

## 13. Monitoring & comms loop (watcher / reporter / lead)

[RFC-840 §14 verbatim-adapted — events-over-polling, the watcher script + agent split,
reporter mechanical-first + agent for critical relay, the derived status line, the
escalation ladder (>20 min stale → nudge → unanswered → critical relay), interrupt classes,
lead entrances (replan trigger / decision-maker / close sequence). State explicitly: **the
mechanical scripts described here are not built by this plan** — see this plan's Task 6.]

## 14. Adoption workflow

[RFC-840 §15 — Adopt as-is; this document, the rulings record, and this plan are steps 1–3
of it, in progress.]
```

- [ ] **Step 2: Write `docs/process/agent-settings.md`**

Content from `.claude/rfcs/0011-…md`'s "Original wording" §§1–3 (lines 171–332), with
these corrections applied in the text itself, not left as a diff against the original:

- Model names pinned (Part B5): `opus` → **Opus 5**, `sonnet` → **Sonnet 5**, `haiku` →
  **Haiku 4.5**. Add one line noting a fourth tier, **Fable 5**, exists (confirmed via the
  `Agent` tool's own `model` enum) and is not assigned to any role by this adoption — a
  separate question nobody has raised.
- The lead's row (Part B9): **"Tools: full read; git merge authority (sole merge
  authority); write to handover/status files only."** — RFC-841's version, not RFC-840's;
  state the correction inline: *"RFC-840 §2's lead row disagreed (read-only + plan/map
  files, no merge authority) — corrected here to match confirmed practice."*
- The lead's **model** row (Part B5, second part): state explicitly that the lead is the
  main thread, not spawned, so its model is whatever the session started with — not a
  setting this document can enforce, unlike every other role's file (Task 3), which binds
  a spawned session.
- `ultracode` → `ultrathink` (Part B2): already correctly written in the source as
  "ultrathink" — carry forward unchanged; add one line recording the resolution: *"Resolved
  2026-08-29 (rulings record Part B2): the decision-maker's effort setting is maximum
  extended thinking, never the multi-agent `Workflow`-orchestration keyword."*
- Retry caps / cost tiers (Part B3): add a line — *"Adopted as instrumented defaults, not
  fixed governance — see `docs/process/delivery-process.md` §7."*
- **Do not write a final `docs/`-write tools column for planner, decision-maker or
  auditor.** State per role: *"docs/-write scope: pending `docs/plans/PL-00845-rfc-840-rf
  c-841-adoption-reconciliation-and-rulings-2026-08-29.md` Part A2 — see `.claude/roles/<role>.md` for the current
  interim value."* (Finding 5.)

- [ ] **Step 3: Add the `CLAUDE.md` §12 pointer**

Insert one paragraph in §12 (Skills), after the existing "Discovered a non-obvious
procedure..." bullet list and before "**Evidence is delegated, verdicts are not.**" (the
sentence Part A2 will amend once ruled — do not touch it in this task):

```markdown
**Team process.** How this repository's Claude Code team does the work — the Project →
Phase → Work → Slice layering, roles, escalation guards, and the monitoring loop — is
`docs/process/delivery-process.md` and its companion `docs/process/agent-settings.md`.
Distinct from `docs/workflows/WF-698…05`, the cross-module *domain* journeys (§4) — one
describes how the team works, the other what the platform does.
```

- [ ] **Step 4: Add the two missing `docs/README.md` rows**

In the `## Map` table, insert (alphabetically consistent with the existing directory-then-
file ordering):

```markdown
| `process/` | Team execution process: layered workflow (Project→Phase→Work→Slice), roles, escalation, monitoring loop |
| `research/` | Spike findings and dated research notes (track-a, w6b-6b, w8, zen-evaluate-concurrency) |
```

- [ ] **Step 5: Verify**

Run: `python3 scripts/audit-docs.py`
Expected: `All checks passed.` — no new `FR-`/`NFR-`/`OQ-` id is introduced, so no check
that enumerates ids should change count.

Run: `grep -c '^|.*process/.*|' docs/README.md && grep -c '^|.*research/.*|' docs/README.md`
Expected: `1` and `1`.

- [ ] **Step 6: Commit**

```bash
git add docs/process/delivery-process.md docs/process/agent-settings.md CLAUDE.md docs/README.md
git commit -m "docs(process): adopt RFC-840/841 — delivery process, agent settings, CLAUDE.md pointer"
```

## Task 2: Fix the two drift instances this plan's own sweep found

**Files:**
- Modify: `.claude/rfcs/RFC-00841-per-agent-model-thinking-effort-and-skill-bindings-for-the-seven-roles.md:58`
- Modify: `.claude/skills/writing-plans/SKILL.md:16,64,169,173`

**Interfaces:**
- Consumes: Finding 1 and Finding 3 above; the exact dated-correction style already applied
  to `.claude/rfcs/0010-…md:58-61` (mirror it, do not invent a new style).
- Produces: a `writing-plans/SKILL.md` template with zero `superpowers:` residue, so every
  plan filed after this task (including, retroactively in spirit but not in text, this one)
  stops manufacturing new instances of Finding 1's defect.

- [ ] **Step 1: Correct RFC-841's specialist count in place**

In `.claude/rfcs/RFC-00841-per-agent-model-thinking-effort-and-skill-bindings-for-the-seven-roles.md`, line 58, change:

```
`.claude/agents/` holds eight delegable specialists and no role definitions; the seven roles
```

to:

```
`.claude/agents/` holds seven delegable specialists *(corrected 2026-08-29 — a directory
listing that included its own `README.md` read as eight; `.claude/agents/README.md:184`
already states "all seven"; see `docs/plans/PL-00845-rfc-840-rfc-841-adoption-recon
ciliation-and-rulings-2026-08-29.md` Part B8, which corrected RFC-840's identical instance but not this sibling
one)* and no role definitions; the seven roles
```

- [ ] **Step 2: Fix `writing-plans/SKILL.md`'s four references**

Replace, using `docs/plans/README.md:33`'s already-correct bare form as the model:
- Line 16: `superpowers:using-git-worktrees` → `using-git-worktrees`
- Line 64: `superpowers:subagent-driven-development (recommended) or superpowers:executing-plans` → `subagent-driven-development (recommended) or executing-plans`
- Line 169: `superpowers:subagent-driven-development` → `subagent-driven-development`
- Line 173: `superpowers:executing-plans` → `executing-plans`

- [ ] **Step 3: Verify**

Run: `grep -c 'superpowers:' .claude/skills/writing-plans/SKILL.md`
Expected: `0`

Run: `grep -n 'seven delegable specialists' .claude/rfcs/RFC-00841-per-agent-model-thinking-effort-and-skill-bindings-for-the-seven-roles.md`
Expected: one match, at line 58, carrying the corrected text.

Run: `python3 scripts/audit-docs.py`
Expected: `All checks passed.`

- [ ] **Step 4: Commit**

```bash
git add .claude/rfcs/RFC-00841-per-agent-model-thinking-effort-and-skill-bindings-for-the-seven-roles.md .claude/skills/writing-plans/SKILL.md
git commit -m "docs(notes): correct RFC-841's specialist count and writing-plans' stale superpowers: refs"
```

## Task 3: Role definition files under `.claude/roles/`

**Files:**
- Create: `.claude/roles/lead.md`, `planner.md`, `decision-maker.md`, `auditor.md`,
  `executor.md`, `watcher.md`, `reporter.md`

**Interfaces:**
- Consumes: `docs/process/agent-settings.md` (Task 1) as the settings source; rulings
  record Part B5 (model pins), B9 (lead tools), B10 (decision-maker citation), B2
  (ultrathink), B3 (instrumented defaults); Finding 5 (the A2-pending tool-scope lines).
- Produces: the seven files `docs/process/delivery-process.md` §3 refers a reader to for
  tool scope, and the files a future spawn of any role reads to know its own charter.
- **Not** `.claude/agents/` — that directory's own README dividing line is a separate,
  still-correct rule about a different category of file (rulings record Part B11).

- [ ] **Step 1: Write `.claude/roles/decision-maker.md` first — it carries the sourcing fix**

Per Part B10: state the "no write access to any code worktree" boundary with an **in-repo**
justification, not a citation to `TEAM-STRUCTURE.md` (a handover file outside this
repository and outside the durable record by this project's own convention). Content:

```markdown
# decision-maker

- **Model / effort:** Opus 5; ultrathink on every ruling — decisions are rare, binding, and
  cheap to think hard about relative to the cost of a wrong one.
- **Owns:** technical decisions only — decision-point rulings and spec changes, recorded as
  dated sibling records, never edits to a frozen plan. Pre-resolves every decision point
  before its slice starts. A spec change conforming to the plan needs no replan.
- **Never:** closes work or phases, implements, or rules audit verdicts (verdicts are the
  lead's). **No write access to any code worktree** — a decision-maker session checked out
  into an executor's worktree during WK-670 (three writes, one after an explicit stop order,
  the third discarding the executor's uncommitted tracked files; recovered from job-dir
  copies). The boundary is a hard one for exactly that reason, sourced here rather than in
  a handover file that does not persist.
- **Spawn:** only when a new decision point or spec conflict appears; stopped when duties
  complete.
- **Tools:** Read; write to ruling records and the open-questions log only. **docs/-write
  scope beyond ruling records and open-questions.md: pending Part A2** — until ruled, a
  decision-maker session does not edit `docs/specs/` or other `docs/` content directly;
  route such a finding to the planner or the lead.
```

- [ ] **Step 2: Write `.claude/roles/lead.md`**

Per Part B9's corrected row and Part B5's second point (the lead is not spawned):

```markdown
# lead (main thread)

- **Model / effort:** whatever session this thread started on — the lead is the main
  thread, not a spawned role, so no role file can bind its model the way it binds every
  other role's (contrast every file below, which does spawn and can).
- **Owns:** verdicts (adopts/amends/rejects the auditor's proposals), merges (sole merge
  authority; verify CI on the exact head), dispatch, replan triggers, status-line judgment
  and ETA adjustment over mechanically derived facts, handover maintenance, presenting a
  close to the user.
- **Never:** implements or audits itself; never declares a workstream or phase closed —
  closure acceptance is the user's alone.
- **Mandatory skill:** `using-git-worktrees` — the lead dispatches every member into its
  own worktree. Carry this rule into every dispatch: never `git checkout`/`git switch`
  outside your own worktree; check `pwd` and `git branch --show-current` before every git
  write; read-only git is safe anywhere (two real WK-670 incidents discarded uncommitted work
  this rule exists to prevent).
- **Tools:** full read; git merge authority; write to handover/status files only.
  **docs/-write scope beyond handover/status: pending Part A2.**
```

- [ ] **Step 3: Write `.claude/roles/planner.md`**

```markdown
# planner

- **Model / effort:** Opus 5; high thinking — plans are frozen once dated and are worth
  maximum quality at write time.
- **Mandatory skill:** `writing-plans`.
- **Owns:** the plan: frozen dated files in `docs/plans/`; new dated revisions on a replan
  trigger; scope + requirement coverage, slices with task lists and per-slice gates,
  decision points with options and recommendations. Every plan meets `docs/process/
  delivery-process.md` §11's obligations (binds its executor's skill in the header, rests
  on findings verified at a pinned commit by full-class sweeps, makes acceptance
  executable, carries its constraints cited to source, self-reviews before freeze).
- **Never:** implements, audits, merges, or rules decision points.
- **Tools:** Read, Grep, Glob; write to `docs/plans/` files only. **Write scope to other
  `docs/` content (e.g. a roadmap-row correction proposed inside a plan review): pending
  Part A2** — current interim practice is a proposal in the plan or review document, applied
  by the lead or decision-maker, not a direct edit by the planner outside `docs/plans/`.
```

- [ ] **Step 4: Write `.claude/roles/auditor.md`**

```markdown
# auditor

- **Model / effort:** Sonnet 5; high thinking — evidence gathering and comparison need
  care even though volume is moderate.
- **Mandatory skill:** `requesting-code-review`.
- **Owns:** per-slice audits (every axis runs per slice, not only at close — the WK-671
  lesson), gap lists, closure records, register deferral rows with named owners. **RE-audit
  rule:** after every fix, re-run the checks — never rubber-stamp. Fresh context each time;
  must not inherit the implementation session's reasoning. **Durability rule:** a finding
  that lives only in chat is ephemeral — the durable landing is always a merged artifact
  (closure record, register row, correction PR, or plan revision).
- **Never:** merges, implements, declares anything closed. Proposes verdicts; never issues
  them (verdicts are the lead's, per `docs/process/delivery-process.md` §5).
- **Tools:** Read-only + Bash for running checks. **Write access to closure records and
  register rows: pending Part A2** — current interim practice (three merged PRs this
  session, #308/#309, plus this session's own dispatch) already has the auditor writing
  these directly; this line records that practice exists and is unresolved, not that it is
  authorised or forbidden.
```

- [ ] **Step 5: Write `.claude/roles/executor.md`**

```markdown
# executor

- **Model / effort:** Sonnet 5; medium (standard) — the highest-volume role; per-slice
  gates and the auditor's re-check bound the risk of a cheaper setting.
- **Mandatory skills:** `subagent-driven-development` (recommended) or `executing-plans`,
  per the plan header, plus `test-driven-development`.
- **Owns:** one slice at a time from the frozen plan, in its own worktree; the full local
  gate before push; opens PRs.
- **Never:** merges, self-audits.
- **Tools:** full read/write + Bash, scoped to the current slice's worktree. Not affected by
  Part A2 — the executor's write scope is code and tests, not `docs/` policy content.
```

- [ ] **Step 6: Write `.claude/roles/watcher.md`**

```markdown
# watcher (support — mechanical first)

- **Form:** a script (no LLM in steady state) plus event hooks; a watcher agent (Haiku 4.5,
  low effort) spawns only when an anomaly needs judgment or a written signal.
- **Owns (script):** balance thresholds and re-arming one-shot triggers on confirmed
  recovery, roster/staleness watch, hygiene checks, publishing `roster-state.md` each cycle
  as the single source of team state, and a rolling mechanical ETA from per-slice durations.
- **Owns (agent):** judgment on ambiguous anomalies and the written signal to the lead.
- **Never:** dispatches stand-ins, touches the repo.
- **Built:** not by this plan — see `docs/process/delivery-process.md` §13 for the
  mechanism this file describes, and this plan's Task 6 for why the script itself is
  deliberately deferred.
```

- [ ] **Step 7: Write `.claude/roles/reporter.md`**

```markdown
# reporter (support — mechanical first)

- **Form:** routine summaries template-filled from state files by script; a reporter agent
  (Haiku 4.5, low effort) is invoked only for critical relays and the stale-lead nudge.
- **Owns:** the single external comms channel; watch-the-watcher (flags a stale
  `roster-state.md`, symmetric with the stale-balance-log flag); the escalation ladder —
  nudge the lead when the status line is over 20 minutes stale, escalate to the user
  channel as a critical relay if unanswered (a stale lead is treated like any dead member).
  Reads the watcher's published state; never polls agents.
- **Never:** edits the repo, merges, audits.
- **Built:** not by this plan — same note as `watcher.md`.
```

- [ ] **Step 8: Verify**

Run: `ls .claude/roles/ | wc -l`
Expected: `7`

Run: `grep -L "pending Part A2" .claude/roles/planner.md .claude/roles/decision-maker.md .claude/roles/auditor.md .claude/roles/lead.md`
Expected: empty output (every one of the four A2-affected files contains the marker;
`grep -L` lists files that do *not* match, so an empty result confirms all four do).

Run: `python3 scripts/audit-docs.py`
Expected: `All checks passed.`

- [ ] **Step 9: Commit**

```bash
git add .claude/roles/
git commit -m "docs(roles): create the seven role-definition files, docs/-write scope marked pending Part A2"
```

## Task 4: Reconcile the existing closure checklists against the adopted process

**Files:**
- Modify (small, or none — see Step 1): `docs/process/checklists/phase-close.md`
- Modify (small, or none — see Step 1): `docs/process/checklists/work-item-close.md`

**Interfaces:**
- Consumes: Finding 4 above; `docs/process/delivery-process.md` §§4, 9, 12 (Task 1).
- Produces: a recorded comparison (in the PR description, not a new file) confirming
  agreement or naming the delta, per the phase-review skill's own "no change is still a
  written answer" discipline.

- [ ] **Step 1: Compare, section by section**

Read `docs/process/delivery-process.md` §4 (Hierarchy) and §12 (Audit record obligations,
cross-referencing `close-workstream`/`phase-review`) against both checklist files in full.
Finding 4 already establishes the expected result is **no change** — both files already use
matching terminology and record conventions. If the comparison in this step finds the same,
add one line to `phase-close.md`, under "When a record is written": *"'Phase' here is
`docs/process/delivery-process.md` §4's Phase layer — same artifact, same id space
(`1a`, `1b`, `2`, ...)."* This is the only edit Finding 4 anticipates; if the comparison
finds something Finding 4 missed, name it here rather than silently patching it, since this
step's job is to prove the "no change" claim, not to assume it.

- [ ] **Step 2: Verify**

Run: `python3 scripts/audit-docs.py`
Expected: `All checks passed.`

- [ ] **Step 3: Commit**

```bash
git add docs/audit/checklists/
git commit -m "docs(audit): cross-reference the adopted process hierarchy in phase-close.md"
```

## Task 5 [BLOCKED — pending Part A1 AND Part A2 both carrying a dated maintainer acceptance line]: land the gated content, flip the notes' Status

**Do not start this task until both `docs/plans/PL-00845-rfc-840-rfc-841-adoption-recon
ciliation-and-rulings-2026-08-29.md` Part A1 and Part A2 carry a dated maintainer acceptance line.** Nothing in
Tasks 1–4 depends on this task; they are not resequenced by however long it stays blocked.

**Files (exact set depends on which options are accepted — see Finding 5's table; this task
cannot be executed as a fixed diff today, only as a checklist of what to resolve when it
unblocks):**
- `docs/process/delivery-process.md` §2 (Human checkpoint) — replace the "BLOCKED pending
  Part A1" placeholder with whichever of options (a)/(b)/(c) was accepted, written as final
  text, not as a record of the options.
- `CLAUDE.md` §12 — add the role-write-authority sentence(s) Part A2's accepted option
  specifies (only option (a) as drafted adds new text; (b) and (c) each need different
  wording the decision-maker states in the acceptance line itself).
- `CLAUDE.md` §13/§14 — only if A1's accepted option is (b), which is the only option that
  calls for it.
- `.claude/agents/README.md`'s dividing line — the belt-and-braces sentence, only if A2's
  accepted option is (a).
- `.claude/roles/planner.md`, `decision-maker.md`, `auditor.md`, `lead.md` — replace each
  "pending Part A2" marker with the accepted scope.
- `.claude/rfcs/RFC-00840-a-layered-slice-based-workflow-project-phase-work-slice-gated-at-every-layer.md` and `0011-…md` — flip `Status` from
  `open` to whatever `.claude/rfcs/README.md`'s convention calls the accepted state, once
  *both* rows carry a date.

- [ ] **Step 1 (on unblock): Re-read both acceptance lines verbatim** — do not act on a
  paraphrase or a memory of the options; the acceptance line is the ruling.

- [ ] **Step 2 (on unblock): Apply each file above per the table**, writing final text, not
  a record of the deliberation.

- [ ] **Step 3 (on unblock): Verify**

Run: `python3 scripts/audit-docs.py`
Expected: `All checks passed.`

Run: `grep -c "pending Part A2" .claude/roles/*.md CLAUDE.md docs/process/*.md`
Expected: `0` everywhere this pattern was inserted by Tasks 1 and 3.

- [ ] **Step 4 (on unblock): Commit**

```bash
git add -A
git commit -m "docs(process): land Part A1/A2 per the maintainer's dated acceptance"
```

## Task 6 [DELIBERATELY NOT BUILT]: watcher/reporter mechanical automation

**Explicit exclusion, per obligation 3.** `docs/process/delivery-process.md` §13 (Task 1)
and `.claude/roles/watcher.md` / `reporter.md` (Task 3) **describe** the monitoring
mechanism RFC-840 §14 and RFC-841 specify. The scripts themselves are not written by this
plan. Reason, in the lead's own words dispatching this plan: *"automation is worthless
until there is real activity to monitor, and building it early means building it against a
process that has not been exercised."* The pilot this adoption's own §15 step 6 calls for
**is WK-671's first slice, not a synthetic exercise** — the mechanical scripts, if built at
all, are sized and thresholded against what that slice actually produces (per-slice
durations, re-audit counts, the instrumented defaults Task 1 §7 logs), which does not exist
before the slice runs. Building Task 6 now would be guessing the same way RFC-840's own
retry caps were guessed (Part B3) — this plan does not repeat that shape of mistake for a
second parameter set.

**Owner and timing:** not assigned by this plan. A future dated plan, written after the
pilot has produced at least one slice's worth of the logs §7 describes, is the right vehicle
— named here so the omission is recorded, not silently dropped (obligation 3).

## Self-review

**1. Spec coverage.** Every `Adopt`/`Amend` row in the rulings record's Part C that names a
concrete artifact is covered: RFC-840 §§1, 3, 5, 6, 7, 8, 10, 11, 12, 14, 15 and RFC-841
§§1, 2 (non-gated fields), 3 → Task 1 (process docs) and Task 3 (role files). RFC-840 §2 /
§4 and RFC-841 §2 (gated fields) / §1 (auditor's tool-scope contradiction) → Task 5,
blocked, per Part A2. RFC-840 §9 → Task 5, blocked, per Part A1. RFC-840 §13 (self-
referential, N/A this round) → no task, correctly. B1–B11 → folded into Task 1 (B1, B2, B3,
B4, B6), Task 2 (B7, B8), Task 3 (B5, B9, B10), Task 1+3 jointly (B11, since it drives both
where the process doc points and where role files live). Part D's three "silent" items →
Task 1 §§3, 7, 9, 13 give each a governing-document home for the first time, which is the
custody gap both notes exist to close. Finding 2 / task board #17 → Task 1 Step 4.

**2. Placeholder scan.** No bare TBD/TODO. Every place this plan cannot state final content
today (Task 5's six locations) carries the exact reason (Part A1/A2 unruled), the exact
current interim value where one exists, and the exact command that proves it is gone once
resolved — not a silent gap.

**3. Consistency.** `.claude/roles/` (not `.claude/agents/`) is used identically across
Task 1 (§10, §3 of the process doc), Task 3 (all seven files), and Finding 5's table.
`docs/process/delivery-process.md` and `agent-settings.md` are named identically wherever
cited (Task 1's own steps, Task 3's Interfaces, Task 4's Step 1, Task 5's file list). The
model names Opus 5 / Sonnet 5 / Haiku 4.5 are used identically in Task 1 Step 2 and every
Task 3 role file — no file uses the bare `opus`/`sonnet`/`haiku` names Part B5 retired.

**Gaps found in review, fixed inline:** the first draft of Task 1 Step 1 embedded the full
role-responsibility table a second time inside `delivery-process.md` §3; changed to a
cross-reference to `.claude/roles/*.md` (Task 3) so the table has one home, not two — the
exact defect class Finding 2 and plan review 8's "second mechanism" both describe, and this
plan should not commit on its own first page. The first draft also left Task 6 unnumbered
and easy to mistake for silence; renumbered and titled `[DELIBERATELY NOT BUILT]` so a
future reader cannot read its absence as an oversight.
