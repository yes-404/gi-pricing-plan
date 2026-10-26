---
id: FD-8263
family: finding
title: WF-699 B9 says MONETARY_FLOAT_REFUSED at save where FR-227 refuses with RATING_TYPE_MISMATCH, and no §5.x row owns the code
status: active
created: 2026-10-26   # drafted 2026-10-26 under working id 8263
owner: auditor
tree: 1e0a8abbc90723ae9c887a901f700b72f6f94cc1
corrected_by: []
relates: [WK-675, CR-8261, RL-1564]
---

# FD-8263 — WF-699 B9 says MONETARY_FLOAT_REFUSED at save where FR-227 refuses with RATING_TYPE_MISMATCH, and no §5.x row owns the code

## Finding

**LOW (to-lead "2026-10-26 11:04:42 GMT"); owner WK-675, as a spec decision raised in the lane-C docs PR of Tue 27 Oct 2026.** A spec and workflow disagreement on an error code; no price moves. Authority: to-lead "2026-10-26 10:54:44 GMT", with the count corrected by the lead in `from-lead-2026-10-09.md` "2026-10-26 10:55:24 GMT". Filed under working id FD 8263, from CR 8261 §5c.

WF-699 B9 (`docs/workflows/WF-00699-*.md:64`, and the §3 row at `:112`) says an `expression` step multiplying a `money_minor` by a float-typed value is refused at save with `MONETARY_FLOAT_REFUSED`. FR-227 (`03:115`, amended 2026-10-17 by RL-1564) closes `money_minor` both ways at save and refuses every other pair with `RATING_TYPE_MISMATCH`; its closed type list has no float type.

## Evidence

At `origin/main` 1e0a8abbc90723ae9c887a901f700b72f6f94cc1:

- `git grep -c MONETARY_FLOAT_REFUSED -- docs/specs/03-rating-engine.md` prints `docs/specs/03-rating-engine.md:1`; the one hit is `:1136`, the error-code enumeration. **The code is enumerated in `03`; it is not "never named".** No §5.x row owns it, so nothing in `03` says when it is raised.
- `backend/src/app/errors.py:323` defines it in `RATING_ERROR_CODES`: `        "MONETARY_FLOAT_REFUSED",`.
- WF-699 gives it a save-time raise point that FR-227 assigns to `RATING_TYPE_MISMATCH`.

## Severity

LOW: a code without an owner set against a workflow that names a raise point; no wrong merge, price or data is let through.

## Remedy

A spec decision, which side is wrong is `CLAUDE.md` §0's question: either an owning §5.x row for `MONETARY_FLOAT_REFUSED` (and FR-227 amended), or WF-699 B9 and its `:112` row corrected to `RATING_TYPE_MISMATCH`. Raised in the lane-C docs PR of Tue 27 Oct 2026 (CR 8261 §5e owed row (1)). The workflow edit is the decision-maker's, not the executor's.

## Disposition

Open, owner WK-675; decision raised in the Tue 27 Oct 2026 docs PR. Filed under working id FD 8263.
