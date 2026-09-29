---
family: reference
title: Work-item close record
status: active                  # active → retired (§1.2a)
created: 2026-08-27
owner: maintainer
corrected_by: []
relates: []                      # ids only
was: docs/audit/checklists/work-item-close.md
---

# Work-item close record

Follow the [`close-workstream`](../../../.claude/skills/close-workstream/SKILL.md) skill.
That skill audits the work item; this checklist adds the record the close leaves in
[`../../closures/`](../../closures/README.md). Nothing here restates the skill's audit
steps.

## When a record is written

A work item is any buildable unit the repository names: a PR, a slice, or a workstream. The
record is a `CR-` document under `../../closures/`, `kind: work`, named by the item's
existing id in its title and `relates:` field — a PR record cites `pr-NNN`, a slice record
cites the slice id, a workstream record cites the workstream id (for example `WK-661`).
No family outside [`../document-ids.md`](../document-ids.md) §1.2.

**Closing a workstream also answers the `CLAUDE.md` §14 plan review question, with a replan
check** *(amended 2026-09-29, `RFC-9631`, option C)*. The record carries a **Replan check**
section: the five questions of the
[`phase-review`](../../../.claude/skills/phase-review/SKILL.md) skill (*When*), each answered
yes or no in one line, plus `python3 scripts/register-owed.py review`'s owed count. A full
plan review runs only if the check fires — a phase boundary or Work scope moved, an exit
criterion is at risk, a replan was decided, or a finding moves a slice or phase — and always
before a phase's exit demo. The lead gives its verdict on the check; "no trigger" is
recorded, never assumed. A PR or slice close does not raise this question; only a
workstream close does.

**Every close also checks root `README.md`'s pointer freshness.** Does this close change
what the README's pointers resolve to (roadmap phase, process spec location)? If yes,
update the pointer — never the copied content, which the README must not contain.

- [ ] **A new record has an id**, from `python3 scripts/doc-id.py next`, and its header
      validates: `python3 scripts/doc-id.py check` exits 0.
- [ ] `python3 scripts/audit-docs.py` exits 0 at the tree the record is filed against.
- [ ] Every register row this close touches is current: `python3 scripts/register-lint.py`
      exits 0, and `python3 scripts/register-owed.py <WK-id>` has been run and its output
      reconciled — a cell reading "fix before close" against landed evidence is a stale
      cell, not a finding.

## The record

Write the `CR-` document with these sections.

### Scope

The item's scope, derived from the specification first, then evidenced (CLAUDE.md §13).
What the item was supposed to deliver, and what it delivered.

### Checklist

The `close-workstream` checklist version this close ran against, and the result of each
step. A record that predates a checklist change names the version it used.

### Evidence

The requirements evidenced, each with its tree and its measurement. A count carries the
tree and the corpus it counted over (CLAUDE.md §13).

### Owed list

**The owed list is generated, not recalled.** Run `register-owed.py <id>` against a
committed revision and paste its output verbatim into the closure record as a fenced block
marked generated, naming the command and that revision. The block is evidence; the record's
own findings-and-resolutions table stays hand-written, because it carries per-close
judgements and findings that have no register row. State in one sentence that every id in
the block appears in that table with a resolution, and that the table adds nothing the block
does not carry except findings named as having no register row.

### Findings

One row per finding. Each row names the requirement or artifact id it concerns, states
the decision, and states the status.

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| The requirement or artifact id | What the finding is about | `fix before close` · `carry forward with an owner` · `accept` | `closed` · `closed-with-findings` |

A carried finding stays a row in the global register ([`../../findings/register.md`](../../findings/register.md));
a per-phase view of it is generated (`python3 scripts/doc-index.py --phase <p>`), never a
second hand-kept file.

### Sign-off

The named owner who accepted the close, and the date.
