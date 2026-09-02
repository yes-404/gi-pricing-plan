<!--
TEMPLATE — Closure (`CR-`), one work, phase or review close.
Copy this file to `docs/closures/CR-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next`. A closure is write-once: fill in every
placeholder before filing, delete this comment block, and remove any field this record
does not use. There is no draft state and no later edit beyond what check 34's freeze
allowance permits on any frozen file.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `slice:`, `plans:`, `supersedes:` and
`superseded_by:` do not apply to this family and must not appear here — a closure has
exactly one status, `active`, for its whole life.
-->

---
id: CR-NNNNN
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: <one line — the work, phase or review this closes>
status: active                  # write-once; this is the only value this family ever takes
created: YYYY-MM-DD
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: <commit-sha this was written against>
phase: P<n>
work: WK-NNNNN                  # the work or phase-scoped review this closure covers
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
---

# CR-NNNNN — <Title>

## Scope

<What was audited, derived from the specification per CLAUDE.md §13 — never from
recollection of what was built.>

## Evidence

<The commands run and artifacts read, per requirement or per NFR, each with a verdict.>

## Verdict

<One of CLAUDE.md §13's four verdicts per unevidenced requirement — delivered but
untested, deferred with an owner, reassigned, not started — plus the overall close
decision this record makes durable.>
