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

**Provenance note (W37-10).** The old audit tree's own findings README — the directory
`document-ids.md` §1.4 dissolves — carried the fuller naming and migration conventions
below. Its content folds in here rather than being duplicated in a second surviving file;
the two paragraphs after this note are that folded content, not new policy.

## Naming an essay file, and what a migrated row keeps

An essay file is named for the finding id exactly as the register writes it in that row's
own Finding-id cell — no slug, no description, no suffix. A description in the filename
goes stale the moment the register's own prose is amended, which it is often. A finding
with sub-parts (labelled limbs, letters or numbers) keeps them as **sections inside the one
essay file**, never as separate filenames — a limb is a clause of a finding, not a finding
of its own, and minting one a file would put an id outside the register's own sequence.

**Migrating a long row to an essay does not touch how the row names itself.**
`scripts/audit-docs.py` check 25 resolves a finding citation made elsewhere in `docs/`
against the register's own text, never against this directory — so a citation that resolved
before a row's migration resolves identically after it. What moves to the essay is the
*reasoning* — why a concern was raised, why a disposition was reached — while the row keeps
a short synopsis, its disposition compressed to index length, and a forward link to the
essay. The link points one way, row to essay: the essay does not need to link back to be
resolvable, because nothing reads it mechanically.

**Compressing a row's Decision cell can silently remove it from an owed-work sweep.**
`scripts/register-lint.py`'s decision-grammar check and `scripts/register-owed.py`'s
work-id and review-marker matchers each read specific substrings of that cell, not its
length or its meaning. Before shortening a Decision cell for migration, read what those
functions currently match in it and keep those tokens in the compressed sentence — the
functions are the authority for what must survive, not this paragraph, and running
`register-owed.py`'s relevant mode before and after the edit is what turns "kept the
tokens" into a checked claim rather than a belief.

**An essay file is write-once, amended in place** — the same convention the register
applies to a row. A correction is appended and dated, quoting what it supersedes, never a
silent rewrite. A row migrates to an essay opportunistically, at its next substantive
amendment, never in a bulk sweep and never on a schedule: `register-lint.py` prints the
count of rows still over the migration threshold on every run precisely so that claim stays
checkable rather than asserted. A finding whose essay is over threshold from the day it is
filed is filed split from the start.

## Conventions

- **Every row has a verdict.** A finding with no status is not a finding that is fine; it is
  one nobody has read. `scripts/register-lint.py` enforces the grammar.
- **Evidence is write-once.** A record that changes after the fact must say it changed, with
  the correction dated.
- **ISO dates.** All dates are ISO 8601, for example `2026-08-27`.
- **Secrets redaction.** No secrets, credentials, or dataset contents
  (`.claude/skills/secret-hygiene`).
