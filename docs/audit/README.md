# docs/audit — the historical record and the closure records

This directory has two roles.

**The archive** (from the roadmap slim, NT-0009, accepted 2026-08-27). Holds what
`docs/roadmap.md` used to carry and no longer does: the closure records, the plan
reviews, and the retrofit-impossible list. The roadmap is the forward-looking plan; the
archive is the record of what was believed and decided at each date. Nothing here changes
status.

**The record layer** (from the closure-audit standard, filed 2026-08-27). Per-work-item
and per-phase records of how a close was audited, with two checklists and the global
register. `close-workstream` and `phase-review` stay the binding procedures; this
directory records what they close, and never restates their audit steps.

- `closure-records.md` — per-workstream closures, the Phase 1a exit demo, the independent
  audit, and the W5 slice records (the archive).
- `plan-reviews.md` — §14 plan reviews 1-6, with their proposals and acceptance lines.
- `retrofit-impossible.md` — the invariants the plan was shaped around.
- [`checklists/work-item-close.md`](checklists/work-item-close.md) — the record a work-item
  close writes, following [`close-workstream`](../../.claude/skills/close-workstream/SKILL.md).
- [`checklists/phase-close.md`](checklists/phase-close.md) — the roll-up record a phase close
  writes, following [`phase-review`](../../.claude/skills/phase-review/SKILL.md).
- [`register.md`](register.md) — the global list of open findings carried across work items
  and phases.
- [`security-posture.md`](security-posture.md) — the repository *platform's* security
  configuration as a public repo: what is enforced, what refuses to change, and what is
  deliberately open. Distinct from the product's security NFRs, which are requirements in
  `docs/specs/` and audited as such.

## Conventions

- **Existing-id naming.** A work item is named by its existing id — a PR number, a slice id,
  or a workstream id. A phase is named by its existing id (`1a`, `1b`, `2`). No new id
  family is minted here.
- **Evidence is write-once.** A record that changes after the fact must say it changed, with
  the correction dated.
- **Checklist versioning.** A checklist is versioned; a record names the checklist version it
  was written against.
- **ISO dates.** All dates are ISO 8601, for example `2026-08-27`.
- **Secrets redaction.** No secrets, credentials, or dataset contents
  (`.claude/skills/secret-hygiene`).
- **A tag at phase close.** The phase record is tagged at the phase's close.

The three NT-0008 acceptance points were answered 2026-08-27: the checklists are a hybrid
complement that point at the skills, records reuse existing ids, and the third §14 rule
(CLAUDE.md) names resolution state with no severity vocabulary.
