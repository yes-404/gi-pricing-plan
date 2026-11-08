---
name: adr-write
description: Create, supersede, or annotate an architecture decision record in docs/adrs/ of this GI pricing platform. Use when a choice constrains more than one module, is expensive to reverse, or has already been made and needs recording — and when research later confirms or contradicts an accepted ADR. Covers the numbering, the status lifecycle, and the addendum-versus-edit rule that keeps accepted decisions immutable.
---

# Writing an ADR

## When it is an ADR at all

Write one when the choice **constrains more than one module**, is **expensive to reverse**,
or has **already been made** and needs recording. Otherwise it belongs in
`docs/open-questions.md` as an open question with options and a recommendation.

## Creating one

Next number, never reused, from the one allocator (`docs/process/document-ids.md` §1.7):

```bash
python3 scripts/doc-id.py next
```

File as `docs/adrs/ADR-<nnnnn>-<kebab-title>.md`, the id zero-padded to five digits. Start from
`docs/_templates/ADR.md`, which fixes the header. The body has this shape:

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

Then add the row to the table in `docs/adrs/README.md`.

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
| … | `03` FR-273 |

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

2026-11-08 (tree `c4ae584a`) — Numbering and filing replaced (skills-gap F1): `docs/adr/` is absent, `docs/adrs/` holds `ADR-<nnnnn>-…` files, and `doc-id.py next` is the allocator. Only that paragraph was re-read. The entries below name no tree; none was recorded (`CLAUDE.md` §13; skills-gap F5).

2026-08-14 — Confirmed by adding dated addenda to ADR-706 (ZEN Engine, where research
resolved OQ-614 and the decision survived) and ADR-707 (Polars/DuckDB, where an open
upstream regression validated the split for an unanticipated reason). Both addenda left
the original Context/Decision/Consequences untouched; `scripts/audit-docs.py` passed.
