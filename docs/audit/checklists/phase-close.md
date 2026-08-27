# Phase close record

Follow the [`phase-review`](../../../.claude/skills/phase-review/SKILL.md) skill. That
skill reviews the plan; this checklist adds the roll-up record the close leaves in
`docs/audit/`. Nothing here restates the skill's review steps.

## When a record is written

A phase is named by its existing id (`1a`, `1b`, `2`). The record directory is
`docs/audit/phases/<phase>/`.

## The record

Write `docs/audit/phases/<phase>/README.md` with these sections.

### Scope reconciliation

The phase's boundaries, workstream cuts and requirement set as filed, and how the actual
phase measured against them.

### Finding roll-up

Every finding carried into the phase is resolved, accepted with an owner, or re-planned.
This is the §13 four-verdict discipline in table form.

| Finding id | Concerns | Verdict | Owner |
|---|---|---|---|
| The requirement or artifact id | What the finding is about | `delivered but untested` · `deferred with an owner` · `reassigned` · `not started` | The named owner |

A finding with no verdict is silence, which §13 forbids.

### Cross-cutting checks

The checks that span workstreams — contract drift, money discipline, workflow coverage.
Each names its measurement and the tree it was measured on.

### Retrospective

What the phase's shape got right and wrong, for the next phase.

### Evidence

The measurements behind the roll-up, each with its tree and its scope.

### Sign-off

The named owner who accepted the phase close, and the date. The record is tagged at the
close.

## The phase register

`docs/audit/phases/<phase>/register.md` lists the phase's open findings, one row per
finding. The phase register derives from `docs/roadmap.md` §6 and never repeats it: the
roadmap owns workstream and phase status; the register records only the findings a close
carried.
