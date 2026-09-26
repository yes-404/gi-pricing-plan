---
family: reference
title: Phase close record
status: active                  # active → retired (§1.2a)
created: 2026-08-27
owner: maintainer
corrected_by: []
relates: []                      # ids only
was: docs/audit/checklists/phase-close.md
---

# Phase close record

Follow the [`phase-review`](../../../.claude/skills/phase-review/SKILL.md) skill. That
skill reviews the plan; this checklist adds the roll-up record the close leaves in
[`../../closures/`](../../closures/README.md). Nothing here restates the skill's review
steps.

## When a record is written

A phase is named by its existing id (`1a`, `1b`, `2`). "Phase" here is
`docs/process/delivery-process.md` §4's Phase layer — same artifact, same id space (`1a`,
`1b`, `2`, ...). The record is a `CR-` document under `../../closures/`, `kind: phase`,
named by the phase id in its title and `relates:` field. No family outside
[`../document-ids.md`](../document-ids.md) §1.2.

- [ ] The record carries an id from `python3 scripts/doc-id.py next`, and its header
      validates: `python3 scripts/doc-id.py check` exits 0.
- [ ] `python3 scripts/audit-docs.py` exits 0 at the tree the record is filed against.
- [ ] Every register row this close touches is current: `python3 scripts/register-lint.py`
      exits 0, and `python3 scripts/register-owed.py <phase-id>` has been run and its
      output reconciled — a cell reading "fix before close" against landed evidence is a
      stale cell, not a finding.

## The record

Write the `CR-` document with these sections.

- [ ] The record's body is the generated phase report — `python3 scripts/doc-index.py --phase
      P<n>` — pasted with the tree it was generated at. **Never a hand-kept table**
      (`../document-ids.md` §1.10 (c)): a hand-kept one drifts from the corpus it summarises,
      which is RFC-756 at scale.

### Scope reconciliation

The phase's boundaries, workstream cuts and requirement set as filed, and how the actual
phase measured against them.

### Owed list

**The owed list is generated, not recalled.** Run `register-owed.py <id>` against a
committed revision and paste its output verbatim into the closure record as a fenced block
marked generated, naming the command and that revision. The block is evidence; the record's
own findings-and-resolutions table stays hand-written, because it carries per-close
judgements and findings that have no register row. State in one sentence that every id in
the block appears in that table with a resolution, and that the table adds nothing the block
does not carry except findings named as having no register row.

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

- [ ] The phase's three freeze gates — plan, code, docs — were declared with dates in the
      phase's milestone section in `../../roadmap.md`, and each passed on or before its date.
      A gate date that passed with a `draft` plan or an `active` slice behind it is a finding
      against the phase, not a note (`../document-ids.md` §1.10 (b), check 38's loop signal).

### Retrospective

What the phase's shape got right and wrong, for the next phase.

### Evidence

The measurements behind the roll-up, each with its tree and its scope.

### Sign-off

The named owner who accepted the phase close, and the date. The record is tagged at the
close.

## The phase register

The phase's findings are the global register's rows carrying that `phase:`. There is no
second, per-phase file: a per-phase view is generated
(`python3 scripts/doc-index.py --phase <p>`), and it derives from
[`../../roadmap.md`](../../roadmap.md) §6 and the global register
([`../../findings/register.md`](../../findings/register.md)) without repeating either — the
roadmap owns workstream and phase status; the register records only the findings a close
carried.
