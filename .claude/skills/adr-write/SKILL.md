---
name: adr-write
description: Create, supersede, or annotate an architecture decision record in docs/adr/ of this GI pricing platform. Use when a choice constrains more than one module, is expensive to reverse, or has already been made and needs recording — and when research later confirms or contradicts an accepted ADR. Covers the numbering, the status lifecycle, and the addendum-versus-edit rule that keeps accepted decisions immutable.
---

# Writing an ADR

## When it is an ADR at all

Write one when the choice **constrains more than one module**, is **expensive to reverse**,
or has **already been made** and needs recording. Otherwise it belongs in
`docs/open-questions.md` as an open question with options and a recommendation.

## Creating one

Next number, never reused:

```bash
ls docs/adr/ | grep -oE '^[0-9]{4}' | sort -n | tail -1
```

File as `docs/adr/NNNN-kebab-title.md` with this shape:

```markdown
# ADR-NNNN — Title in the imperative

- **Status:** proposed | accepted
- **Date:** YYYY-MM-DD
- **Deciders:** who
- **Related:** requirement IDs, other ADRs

## Context      — the forces, including the options considered and rejected
## Decision     — what we will do, specifically enough to act on
## Consequences — **Positive / Negative / Neutral**, and the negative section must be real
```

Then add the row to the table in `docs/adr/README.md`.

## The rule that matters most

**An accepted ADR is immutable.** To change a decision, write a new ADR that supersedes it
and edit *only* the old one's status line.

## When research confirms or complicates an accepted ADR

Do **not** rewrite the body — that destroys the record of what was known when the decision
was taken. Append a dated addendum:

```markdown
---

## Addendum — YYYY-MM-DD: what changed and what did not

**This addendum does not change the decision** and does not supersede the ADR.
It records that a named risk was tested, and where the risk moved to.

| Residual risk | Now specified as |
|---|---|
| … | `03` FR-RATE-56 |

Evidence: [`docs/research/...`](../research/...)
```

Update the status line to note it, e.g.
`**Status:** accepted · **confirmed by research 2026-08-14** (see Addendum)`.

A risk that was flagged and did not materialise is worth recording explicitly — it tells a
future reader the question was asked, not overlooked.

## After

```bash
python3 scripts/audit-docs.py    # verifies every referenced ADR-NNNN exists
```

## Verified

2026-08-14 — Confirmed by adding dated addenda to ADR-0004 (ZEN Engine, where research
resolved OQ-RATE-1 and the decision survived) and ADR-0005 (Polars/DuckDB, where an open
upstream regression validated the split for an unanticipated reason). Both addenda left
the original Context/Decision/Consequences untouched; `scripts/audit-docs.py` passed.
