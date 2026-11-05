---
id: LG-8329
family: ledger
title: WK-1178 slice SL-8328 — FactorCreate.slug takes the Factor grammar at the write boundary (PL-8327, FD-1384)
status: active
created: 2026-11-05
owner: executor
tree: a3046f64bdbe6a2a4f19c574d5589a3dcc043fa8
phase: P2
work: WK-1178
slice: SL-8328
plans: [PL-8327]
corrected_by: []
relates: [FD-1384, RL-1383, SL-1806, PL-8327]
---

# LG-8329 — WK-1178 slice SL-8328: `FactorCreate.slug` takes the Factor grammar

**GO:** the order in to-lead "2026-11-05 09:58:58 GMT" (the slice plan) and "2026-11-05 10:31:31 GMT" (plans C and H accepted); brief `brief-exec-slices-ch-2026-11-05.md`, row exec-sl8328c.
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

PL-8327, "SL 8328 — `FactorCreate.slug`": `POST /api/v1/factors` refuses a slug outside the
Factor pattern (`00` §4.3, RL-1383) with 422 `VALIDATION_FAILED` naming `slug`. Reads unchanged
(FR-209). Requirements: `02` FR-83; FR-209 (read). Register: FD-1384.

### Task list

1. **R0, spec first** — commit `fb5f7acc`: the `02` `POST /api/v1/factors` row gains the dated sentence.
   All cites re-read at base `c064a75d`: `api/models.py` `FactorCreate.slug: str` held; `refs.py`
   `_FACTOR_SLUG` and `Slug` held; Banding/Grouping `Slug` and `RatingVersionCreate.slug: Slug` held.
   Helper-argument sweep: the three files that POST `/factors` (`test_api_models.py`,
   `test_api_transformations.py`, `test_expression_factors_api.py`) use only slugs of the form
   `driver-age-<hex>` / `expr-<hex>`; the grep for slug literals outside the grammar printed nothing.
   No fixture changed.
2. **R1, red first, by cause** — commit `99120993`: `FactorSlug = str` (plain alias) plus T2
   (`test_a_factor_create_refuses_a_slug_outside_the_factor_grammar`, 7 params) and T3
   (`test_a_stored_factor_slug_is_not_revalidated_on_read`) in `packages/model-schema/tests/test_refs.py`
   (the only model-schema test file that exercises `refs`; `git grep -n Slug` finds no `Slug` unit test).
3. **R2, green** — commit `64525585`: `FactorSlug = Annotated[str, Field(pattern=rf"^{_FACTOR_SLUG}$")]`
   in `refs.py` (+ `__all__`), `FactorCreate.slug: FactorSlug`, T1
   (`test_a_factor_slug_outside_the_grammar_is_a_422_naming_the_field`, 5 params + a `veh_brand`
   positive control) in `backend/tests/test_api_models.py`, contract regenerated.

### Gate

Not run: the SOLO full gate is the lead's (brief). Run so far, DB-free, on branch `sl-8328-c-factor-slug`:

| Check | Result |
|---|---|
| `run-small.sh … packages/model-schema/tests/test_refs.py` at the red (`fb5f7acc` + uncommitted alias/tests) | `5 failed, 12 passed` — `Failed: DID NOT RAISE ValidationError`, params `[]`, `[Veh Brand]`, `[a:b@1]`, `[a×65]`, `[a]` |
| same file, green | `17 passed` rc 0 |
| `run-heavy.sh -- uv run ruff check .` | `All checks passed!` rc 0 |
| `generate-contracts.py --check` | `58 generated contracts match the models` rc 0 |
| A5 `git grep -n '\[a-z0-9\]\[a-z0-9_-\]' -- packages backend/src` | `refs.py:42` **and** `packages/pricing-core/src/pricing_core/rate_tables/operations.py:228` (an existing error-message string quoting the pattern, not a second grammar; outside the Write set) |
| A7 `generated.json` diff | one line: `"pattern": "^[a-z0-9][a-z0-9_-]{1,62}$"` |
| A6 `git diff origin/main...HEAD -- packages/model-schema/src/model_schema/modelling.py` | empty |

T1 is route-level and DB-backed; per the plan its green is the gate's (T1 was not run here).
`FactorSlug` is imported in `api/models.py` from `model_schema.refs`, not from the package root,
because `model_schema/__init__.py` is outside the Write set (it re-exports `Slug`).

GREEN set by import closure (common seat brief item 29): changed modules = `refs.py`, `api/models.py`.
Direct importers, `git grep -lE 'model_schema\.refs|app\.api\.models|app\.api import models|FactorCreate'
-- 'backend/tests/*.py' 'packages/*/tests/*.py'` (36 files); the gate's full suite is the decisive green.

### Audit

(the auditor's)

### Build log

- 2026-11-05 R0 `fb5f7acc`; R1 `99120993`; R2 `64525585`. Ledger drafted before audit.

## PRs

(none yet — the seat ends unpushed)
