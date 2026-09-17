---
id: LG-713
family: ledger
title: WK-661 — the GLM spine
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-15
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — the GLM spine, 2026-08-15 *(in progress, not closed)*

Phase 1b opened with the thinnest path that produces a real fitted model, so the remaining
`MODEL` requirements have a working spine to build on rather than a design:

**dataset → Factor → `GlmSpec` → `model.fit` Job → coefficients on screen.**

| Delivered | Evidence |
|---|---|
| `Factor`, `GlmSpec`, `Coefficient`, `GlmFitResult`, `Model` in `model-schema` | R2 and R5 structural: everything frozen, and a `Coefficient` cannot exist without a standard error and an interval that contains its estimate |
| GLM fitting with `glum` 3.4.1 | a Poisson book generated from known coefficients is recovered at 20 000 rows; standard errors from the observed information, since `glum` returns none |
| `model.fit` through the Job path | end to end via `execute_job`: urban rows carry twice the claims of rural ones and the fitted relativity lands near 2 |
| `POST`/`GET /factors`, `POST`/`GET /models` | R1 refused before a Job exists; FR-204 returns the existing model on a `spec_hash` match |
| `/models/:slug` | every estimate with its interval, a coefficient spanning zero marked, the base level shown at 1.000 |

**Not delivered, and the audit says so numerically:** `scope-audit MODEL --endpoints` reads
**4 of 23**. Bandings, groupings, spec validation, diagnostics, transparency, backtests,
comparison, prediction, GBMs, custom objectives, custom metrics and peril structures are
declared and unbuilt. Only the six error codes the spine can raise are registered — the
other sixteen arrive with the slices that raise them, rather than sitting in the catalogue
looking implemented.

**Two `02` corrections, both found by building it**: `@version` in a path becomes
`?version=` in §5.1 and §5.3 (an `@` must be percent-encoded by every client, and
`family@7` then reads as `family%407` in every log and support conversation), and
`POST /models` answers 202-with-a-Job **or** 200-with-the-Model rather than 202 always.

**WK-661 is not closed and this is not a closure record.** It is one slice of ~~seventy-eight~~
**125** requirements, written down so the next one starts from what is true. *(Corrected
2026-08-22, the audit-remediation slice, and the correction is not that the number grew.*
**"Seventy-eight" was never a count of `02`.** It is §6's Phase-1b coverage estimate — "≈ 78
of 375 module requirements" — borrowed from a planning table two pages away and read here as
a derivation. The derived count *on the day this record was written* was **85**:
`grep -cE '^\| \*\*(FR\|NFR)-MODEL-[0-9]+\*\*' docs/specs/02-modelling.md` at `ed3a733`.
Today `uv run python scripts/scope-audit.py MODEL` derives **125 in scope, 110 evidenced
(88 %), 15 without** — both requirement kinds across §3.1–§3.10 and §9. The original figure
is kept because what was believed on the day is what a governed record cannot lose; the
finding is that **an estimate lifted out of a planning table is indistinguishable, on the
page, from a number someone derived** — and that this very correction was written against
124 and had to be re-derived to 125 before it landed, because the slice writing it had
appended FR-118 an hour earlier.*)
