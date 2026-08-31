# Work-item close record

Follow the [`close-workstream`](../../../.claude/skills/close-workstream/SKILL.md) skill.
That skill audits the work item; this checklist adds the record the close leaves in
`docs/audit/`. Nothing here restates the skill's audit steps.

## When a record is written

A work item is any buildable unit the repository names: a PR, a slice, or a workstream.
Name the record directory by the item's existing id — `docs/audit/work/<existing-id>/`.
A PR record is `pr-NNN`; a slice record is the slice id; a workstream record is the
workstream id (for example `W5`). No new id family is minted.

**Closing a workstream also raises the `CLAUDE.md` §14 phase review question** — its
trigger is fixed, not discretionary: at each workstream close, and again before a phase's
exit demo. Nothing else in this checklist checks it, and this paragraph is the only place
that does — confirm with the planner whether a phase review (the
[`phase-review`](../../../.claude/skills/phase-review/SKILL.md) skill) is now due before
signing off. A PR or slice close does not raise this question; only a workstream close does.

**Every close also checks root `README.md`'s pointer freshness.** Does this close change
what the README's pointers resolve to (roadmap phase, process spec location)? If yes,
update the pointer — never the copied content, which the README must not contain.

## The record

Write `docs/audit/work/<existing-id>/README.md` with these sections.

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

A carried finding is copied to the phase's register (`docs/audit/phases/<phase>/register.md`)
and to the global register ([`../register.md`](../register.md)).

### Sign-off

The named owner who accepted the close, and the date.
