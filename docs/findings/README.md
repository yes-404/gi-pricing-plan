---
family: reference
title: docs/findings — the register, and the evidence behind each row
status: active                  # active → retired (§1.2a)
created: 2026-08-27
owner: lead
corrected_by: []
relates: []                      # ids only
was: docs/audit/README.md
---

# docs/findings — the register, and the evidence behind each row

**The register is a ledger; the evidence is a file.** [`register.md`](register.md) is the
global list of findings carried across work items and phases: one row per finding, with its
status, its decision and its owner. An `FD-` document beside it is the evidence essay for a
row too long to carry inline — the row stays the index, the essay is where its Concerns
prose lives.

Per-phase views are **generated**, never files: `python3 scripts/doc-index.py --phase <p>`.
There is no second copy of the register to disagree with the first one.

The closure records this directory used to sit beside now live in
[`../closures/`](../closures/README.md), and the checklists a close writes against in
[`../process/checklists/`](../process/checklists/). `close-workstream` and `phase-review`
stay the binding procedures; nothing here restates their audit steps.

## Conventions

- **Every row has a verdict.** A finding with no status is not a finding that is fine; it is
  one nobody has read. `scripts/register-lint.py` enforces the grammar.
- **Evidence is write-once.** A record that changes after the fact must say it changed, with
  the correction dated.
- **ISO dates.** All dates are ISO 8601, for example `2026-08-27`.
- **Secrets redaction.** No secrets, credentials, or dataset contents
  (`.claude/skills/secret-hygiene`).
