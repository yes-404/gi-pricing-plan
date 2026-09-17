---
id: CR-832
family: closure
kind: work
title: Work-item record — W10-2 (Seeding, Diffs, Validation)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-28
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/W10-2/README.md
---

# Work-item record — W10-2 (Seeding, Diffs, Validation)

Audited 2026-08-28 against origin/main `4a8729e` (PR #302 merged, CI green on head
`4b33b28`), branch w10-2-seed-diff-validate-2 head `4b33b28`.

## Scope

Derived from `docs/plans/PL-00829-wk-670-implementation-plan-rate-tables-seeding-diffs-bulk-operations-import-export.md` slice W10-2 (T1–T4) first, then
evidenced. W10-2 delivers the pricing actions behind FR-230 (seed a table from an
approved model's relativities), FR-231 (cell-level diffs with exposure weighting) and
FR-234 (named validation on save, checked before the version persists):

- T1 seeding: `seed_from_model()` in `pricing_core.rate_tables.operations`, approval gate
  (FR-20 → `PIN_NOT_APPROVED`), `seeded_from` `{model_ref, seeded_at}` lineage
- T2 diffs: `diff_vs_previous()` / `diff_vs_seed()` with caller-supplied exposure weights
  (DP1), exposure-weighted mean change; parquet deferral (FR-232)
- T3 validation: `validate_rate_table()` — complete key-domain coverage (or explicit
  `default_row`), no nulls, in-bounds decimal values, no duplicate keys, each failure named
- T4 endpoints: `POST /api/v1/rate-tables/{slug}/seed-from-model` (201) and
  `GET /api/v1/rate-tables/{slug}@{version}/diff?against=` (200 / 404 / 422 / 501)

Slice gate (plan §4): a rate table is seeded from an approved model, cell diffs are
computed with exposure weighting, and validation failures are named.

## Divergences from the plan (both follow the spec — §0, recorded not silent)

| Plan | Spec 03 §5.1 (implemented) |
|---|---|
| T4 drafted `/seed` and separate diff-vs-previous / diff-vs-seed endpoints | `POST /rate-tables/{slug}/seed-from-model` and one `GET .../diff?against=previous\|seed\|N` — the spec's names and its established `@{version}` addressing |
| T3's four named codes (INCOMPLETE_KEY_DOMAIN, NULL_VALUE, OUT_OF_BOUNDS, DUPLICATE_KEY) | Kept internal; mapped at the API boundary onto 03 §5.2's `RATE_TABLE_INCOMPLETE` / `RATE_TABLE_KEY_DUPLICATE`; every registered code spec-enumerated, unregistered shapes → `VALIDATION_FAILED` |

The parquet half of FR-232 was out of W10-2's reach (nothing can yet write parquet
storage): a diff touching a `parquet` version answers **501** `RATE_TABLE_PARQUET_UNBUILT`
until W10-3 delivers the 202-with-Job form — declared as a dated amendment to 03 §5.2 in
the same commit as the code (one-commit rule; mirrors `01`'s `DERIVATION_NOT_MATERIALISED`
precedent).

## Evidence

**Requirement coverage:** FR-229/230/231/234 each carry `@pytest.mark.req` evidence in
test files (req-coverage green at head `4b33b28`: FR-229 ×2, FR-230 ×9,
FR-231 ×8, FR-234 ×2, FR-232 ×2 files; no nonexistent-ID FAIL). Endpoint
evidence is marker-visible: the API suite's 13 tests carry markers (F1 gap from the first
audit pass, fixed and re-audited).

| Requirement | Verdict |
|---|---|
| FR-229 | ✓ delivered and tested — immutable version, change_note required (bad-body test asserts its absence → 422) |
| FR-230 | ✓ delivered and tested — seeded_from lineage, approval gate, extraction (non-log links skipped), decimal strings (R2) |
| FR-231 | ✓ delivered and tested at the core — diff_vs_previous/seed, changed cells, max-abs and exposure-weighted mean (hand-computed weighting test); **carry-forward**: the endpoint passes no weights (DP1 substrate absent — the portfolio-dataset join is built nowhere) — finding F-W10-2 |
| FR-234 | ✓ delivered and tested — four named failure modes, checked before the version persists; boundary codes asserted (RATE_TABLE_KEY_DUPLICATE) |
| FR-232 | (partial) parquet half = W10-3 scope — W10-2 records the 501 refusal via the dated §5.2 amendment and proves it on deliberately broken input (hand-inserted parquet version → 501 RATE_TABLE_PARQUET_UNBUILT) |

**Gate (measured in this audit, tree = PR #302 head):** ruff clean on all changed files ·
`audit-docs.py` pass · `generate-contracts --check` pass (28 contracts; both endpoints
present in `docs/contracts/openapi/generated.json`) · pytest 55/55 on the slice files at
`073ca7a` + 13/13 on the API file at `4b33b28`, each reconciled against `--collect-only`
(55, 13) · req-coverage green. Executor's full local gate (reported): ruff · mypy --strict
(144 files) · lint-imports · pytest 2134 passed · audit-docs · req-coverage ·
generate-contracts --check · frontend half (lint, type-check, test, build); CI green on
`4b33b28` (lead-verified at merge).

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W10-2 | FR-231 exposure-weight wiring: pricing-core accepts caller weights (DP1) but the diff endpoint passes none; the portfolio-dataset join is scheduled in no slice | carry forward with an owner — portfolio-dataset integration | closed-with-findings |
| F-W10-2-1 | DP3's diff cache (keyed by version hash + portfolio identity, ruling 2026-08-28) is unbuilt and its deferral was not declared in PR #302 — silent until this record | carry forward with an owner — W10-3 diff/portfolio work (the cache wrapper lands with the weights it caches) | closed-with-findings |

## Sign-off

Auditor verdict: slice verified — clean after the F1 fix (markerless API tests, fixed
`4b33b28` and re-audited green). Verdicts adopted by the lead; merged 2026-08-28 as
`4a8729e`.
