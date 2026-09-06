---
id: PL-829
family: plan
kind: leaf
title: WK-670 Implementation Plan — Rate tables: seeding, diffs, bulk operations, import/export
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-28
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-28-w10-rate-tables.md
---

# WK-670 Implementation Plan — Rate tables: seeding, diffs, bulk operations, import/export

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the rate-table layer of the rating engine: the `RateTable` and `RateTableVersion` contracts, seeding from approved models, cell-level diffs against prior versions and seed origins, validation, bulk operations, CSV/XLSX import/export with round-trip guarantees, and the storage threshold decision (rows vs parquet).

**Architecture:** Three slices on the existing Phase 1b seam. Slice W10-1 defines the `RateTable` and `RateTableVersion` shapes in `model-schema` (keys, value column, storage mode, immutability invariants). Slice W10-2 builds seeding from an approved model's relativity table, implements cell-level diffs with exposure weighting, and enforces validation rules. Slice W10-3 implements bulk operations (uplift, floor/cap, rebase), CSV/XLSX import/export with strict round-trip verification, and the parquet-spill threshold logic (FR-232). The workspace-configurable cell-count threshold (default 250 000) determines storage mode at write time and is immutable with the version.

**Tech Stack:** Pydantic v2 (`model-schema`), FastAPI + SQLAlchemy (backend), `pricing-core` (the `rate_tables/` module), Polars, content-addressed parquet blob storage (Redis/S3), CSV and OpenPyXL libraries.

**Spec:** [`03-rating-engine.md`](../specs/03-rating-engine.md) FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236, FR-232 · `04` FRs for bulk-operation metadata (lifted from optimisation) · [`04-optimisation.md`](../specs/04-optimisation.md) for the data model of bulk operations.

**Highest ids in use:** FR-252 (instalment loading, Phase 2). Next free: FR-243, NFR-RATE-15.

## Global Constraints

- The gate has two halves. Both must pass before a push (CLAUDE.md §11).
- Write prose in ASD-STE100. Code, identifiers and file paths stay unchanged.
- A filed plan stays frozen at its date. The plan file commits on the branch, never copied back.
- Requirement ids are permanent. Append, never renumber (CLAUDE.md §5).
- Every spec change runs `python3 scripts/audit-docs.py` before commit (CLAUDE.md §0).
- Nobody hand-writes a shape that already exists in `model-schema`.
- Money is integer minor units or Decimal in the rating path, never float (CLAUDE.md §7).
- `pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis deps.
- A Rating Version pins an exact RateTableVersion per referenced table; all versions are immutable (FR-229).
- The cell-count threshold is stored on RateTableVersion and immutable with it (FR-232).
- Cells stored as PostgreSQL rows use SQL joins for diffs; cells above the threshold spill to parquet and degrade to Job-based diff (FR-231, FR-232).
- A filed plan under `docs/plans/` stays frozen at its date.

---

## Scope and requirement coverage

| Requirement | Slice |
|---|---|
| FR-228 (Rate Table definition) | W10-1 |
| FR-229 (immutability) | W10-1, W10-2 |
| FR-230 (seeding from model) | W10-2 |
| FR-231 (cell-level diff with exposure weighting) | W10-2 |
| FR-233 (bulk operations: uplift, floor/cap, rebase) | W10-3 |
| FR-234 (validation on save) | W10-2 |
| FR-235 (CSV/XLSX import/export with round-trip) | W10-3 |
| FR-236 (rateable vs diagnostic) | W10-1 |
| FR-232 (storage threshold, rows vs parquet) | W10-1, W10-3 |

---

## Findings (verified 2026-08-28 against origin/main `eb9b6a1`)

**F1. Rate tables are greenfield beyond the Phase 1b seam.** `backend/src/app/platform/rating_versions.py` carries the Phase 1b minimal `RatingVersion` pinning a single model. No `RateTable` or `RateTableVersion` shape exists in `model-schema`, no `rate_tables/` module in `pricing-core`, no rate-table routes, and no FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236 marker exists in the codebase.

**F2. The seeding, diff and validation scope is non-trivial.** FR-230 requires tracking the source model and version; FR-231 requires exposure-weighted diffs fetched from the portfolio dataset; FR-234 requires complete key-domain coverage validation. These are not CRUD operations; they are analytical operations over multiple versioned artifacts.

**F3. The storage threshold decision is specified but deferred implementation-wise.** FR-232 is decided (OQ-616, 2026-08-18) and has fixed implementation details: `storage` is a version property (`rows | parquet`), immutable at write time, and determines whether FR-231 diffs run as SQL joins or as Jobs returning the same artifact (202 instead of 200).

---

## The three slices

**Sequencing:** the slices run one at a time. The executor finishes W10-1, the auditor audits it against the work-item-close checklist, and only then does W10-2 start. The same holds between W10-2 and W10-3. The audit is per-slice, never one audit after all three.

### Slice W10-1 — the RateTable and RateTableVersion contract

**T1. model-schema: the rate-table shapes.**

- [ ] Add `RateTable` to `packages/model-schema/src/model_schema/rating.py`: `slug`, `version`, `rateable` (bool), `storage` (`rows \| parquet`, immutable), `keys`, `value`, `default_row` (FR-228, FR-236, FR-232).
- [ ] Add `RateTableKey`: `name`, `type`, `banding_ref` (optional, references a Banding artifact).
- [ ] Add `RateTableValue`: `name`, `type` (`relativity \| money_minor \| percentage \| count`), unit, `min`/`max` bounds.
- [ ] Add the `storage` field to `RateTableVersion`: `rows` or `parquet`, decided at write time based on the workspace's cell-count threshold, immutable with the version (FR-232).
- [ ] Add `seeded_from` to track the source model reference and timestamp (FR-230).
- [ ] Add `change_note` as a required field on version creation (FR-229).
- [ ] Add model-schema tests: a valid rate table parses. Key domain types are enforced. A `default_row` is validated against the key schema.

**T2. The immutability invariants.**

- [ ] Enforce that a Rate Table Version is immutable: editing produces a new version, never in-place modification (FR-229).
- [ ] Enforce the `storage` mode is immutable with the version (FR-232): once written, a version's `storage` field cannot change.
- [ ] Add tests: attempting to edit a version fails; storage mode is fixed when the version is written.

**T3. The endpoints.**

- [ ] Add `POST /api/v1/rate-tables` to create a new rate table and its first version.
- [ ] Add `POST /api/v1/rate-tables/{slug}/versions` to create a new version of an existing table.
- [ ] Add `GET /api/v1/rate-tables/{slug}` and `GET /api/v1/rate-tables/{slug}/versions/{version}` to retrieve table metadata.
- [ ] Add `GET /api/v1/rate-tables/{slug}/versions` to list all versions of a table.
- [ ] The storage mode is determined at version-creation time based on the workspace's cell-count threshold (configurable setting).

**Slice gate:** the `RateTable` and `RateTableVersion` shapes parse, immutability invariants hold, and the storage mode is fixed at write time.

### Slice W10-2 — seeding, diffs, validation

**T1. Seeding from a model.**

- [ ] Implement `seed_from_model()` in `packages/pricing-core/src/pricing_core/rate_tables/operations.py`: accept an approved Model or Peril Structure, extract its relativity table, create a `RateTableVersion` with `seeded_from` metadata (FR-230).
- [ ] Validate that the model reference is approved (maturity check per FR-20).
- [ ] Store the seed source UUID and timestamp for later diffing.
- [ ] Add tests: seeding from a GLM extracts the relativity table. Seeding from a non-approved model fails.

**T2. Cell-level diffs with exposure weighting.**

- [ ] Implement `diff_vs_previous()` and `diff_vs_seed()` in `pricing_core.rate_tables.operations`: compare cells by key, report absolute and relative change (FR-231).
- [ ] For tables stored as PostgreSQL rows: join against the portfolio dataset to fetch exposure weights per cell, compute exposure-weighted mean change (FR-231).
- [ ] For tables stored as parquet: defer to a Job that re-fetches and re-computes the diff, returning the same artifact structure; API answers 202 instead of 200 (FR-232).
- [ ] Return: number of changed cells, max absolute change percentage, exposure-weighted mean change percentage.
- [ ] Add tests: diff against prior version; diff against seed. Exposure weighting is correct for a sample key set.

**T3. Rate-table validation.**

- [ ] Implement `validate_rate_table()` per `03` §5.2 (FR-234): check complete coverage of the declared key domain (or an explicit `default_row`), no null values, values within declared bounds, no key duplication.
- [ ] Check at version-creation time before the version persists.
- [ ] Return a named error for each validation failure: `INCOMPLETE_KEY_DOMAIN`, `NULL_VALUE`, `OUT_OF_BOUNDS`, `DUPLICATE_KEY`.
- [ ] Add tests per failure mode; each test demonstrates the failure is caught and named.

**T4. The endpoints.**

- [ ] Add `POST /api/v1/rate-tables/{slug}/seed` to seed a new version from an approved model.
- [ ] Add `GET /api/v1/rate-tables/{slug}/versions/{version}/diff-vs-previous` to fetch the diff against the prior version.
- [ ] Add `GET /api/v1/rate-tables/{slug}/versions/{version}/diff-vs-seed` to fetch the diff against the seed origin.
- [ ] Diff endpoints may return 200 (row-backed) or 202 (parquet-backed, Job in progress). The artifact structure is identical; only latency and status differ.

**Slice gate:** a rate table is seeded from an approved model, cell diffs are computed with exposure weighting, and validation failures are named.

### Slice W10-3 — bulk operations, import/export, storage spill

**T1. Bulk operations.**

- [ ] Implement `uplift_table()`, `uplift_by_filter()`, `floor_and_cap()`, `rebase_to_level()` in `pricing_core.rate_tables.operations` (FR-233).
- [ ] Each operation records its parameters (percentage, filter expression, bounds, base level) as metadata on the new version, not just the resulting cells (FR-233).
- [ ] All operations produce a new immutable version with the updated cells.
- [ ] Each operation validates the result before persisting (FR-234).
- [ ] Add tests: uplift a whole table by 10%; uplift a subset by key filter; floor at 0.5, cap at 2.0; rebase to a 1.0 base level. Each records its parameters.

**T2. CSV/XLSX import/export.**

- [ ] Implement `export_to_csv()` and `export_to_xlsx()` in `pricing_core.rate_tables.operations` (FR-235).
- [ ] Export includes keys, value column, and all declared metadata (types, bounds, banding references).
- [ ] Implement `import_from_csv()` and `import_from_xlsx()` with strict round-trip validation (FR-235): keys, types, and completeness must match the table schema.
- [ ] The import is presented as a diff for confirmation before creating a version.
- [ ] A mismatch in keys, types, or completeness is rejected with a named error.
- [ ] Add tests: export and re-import; verify round-trip. Import with mismatched keys fails; import with extra keys fails; import with missing domain fails.

**T3. Storage threshold and parquet spill.**

- [ ] Implement `decide_storage_mode()` in `pricing_core.rate_tables.operations`: given a cell count and the workspace's configured threshold (default 250 000), return `rows` or `parquet` (FR-232).
- [ ] When a version is created, calculate the cell count and store `storage` immutably on the version.
- [ ] For `rows` storage: cells are persisted as PostgreSQL rows. The diff query is a SQL join (fast, paged, 200 response).
- [ ] For `parquet` storage: cells are persisted as a content-addressed blob. The diff is a Job returning the same artifact structure (202 response, eventually 200).
- [ ] Both paths serve the same API; only latency and status differ (FR-232).
- [ ] Add a workspace setting for the cell-count threshold (configurable, with a default).
- [ ] Add tests: a 100-cell table uses rows storage. A 1M-cell table uses parquet storage. Storage mode is immutable with the version.

**T4. The endpoints.**

- [ ] Add `POST /api/v1/rate-tables/{slug}/versions/{version}/bulk-operations` to perform a bulk operation and create a new version.
- [ ] Add `GET /api/v1/rate-tables/{slug}/versions/{version}/export/csv` and `/export/xlsx` to export cells.
- [ ] Add `POST /api/v1/rate-tables/{slug}/versions/{version}/import` to accept CSV/XLSX, present the diff, and confirm before creating a version.
- [ ] Bulk-operation and import endpoints record the operation and its parameters on the new version.

**Slice gate:** bulk operations record their parameters, CSV/XLSX round-trip preserves schema and completeness, and the storage threshold determines whether diffs run as SQL joins or Jobs.

---

## Decision points

**DP1 — exposure-weighted diff calculation.** FR-231 requires "the exposure weight behind each cell (from the portfolio dataset)". Options: (a) calculate at diff-fetch time (query the portfolio once per request), or (b) cache weights on the rate-table version at creation time (snapshot the portfolio's weights, stale if portfolio changes). **Recommendation:** calculate at diff-fetch time. The portfolio is the authority for current exposure, and staleness adds a silent risk that a diff looks safe when the book has actually moved.

**DP2 — parquet spill triggering.** FR-232 specifies a workspace-configurable threshold (default 250 000 cells). Options: (a) retroactively move an existing version to parquet if the threshold is lowered (breaks immutability), or (b) the threshold change applies to new versions only (old versions keep their original storage mode). **Recommendation:** (b). Immutability is the rule; a threshold change does not reach backward.

**DP3 — diff endpoint latency for row-backed tables.** FR-231's diff requires joining against the portfolio dataset to weight cells. A large portfolio (10 M+ rows) and a large table (100 k+ cells) makes this query expensive. Options: (a) materialise the diff eagerly at version creation (cost at write time), or (b) compute on read with a cache (cost at first read, then cached). **Recommendation:** compute on read with Redis caching keyed by version hash and portfolio snapshot date. This shifts cost to the read path, which is infrequent (diffs are reviewed once per rate change, not on every quote).

---

## Verification

- Both gate halves pass locally before a push:
  - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
  - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
  - `uv run python scripts/generate-contracts.py --check`
- Every in-scope FR-RATE carries a marker. Validation failures are named and tested on deliberately broken input.
- A rate table is seeded from an approved model. Cell diffs are computed with exposure weighting. CSV/XLSX round-trips preserve schema.
- The storage mode is immutable with the version. The threshold determines API response codes (200 vs 202) and operation paths (SQL join vs Job).
- The `RateTable` and `RateTableVersion` shapes match `03` §4.2, and the bulk-operation metadata matches `04` §4 (once specified).

---

## Sources

- `docs/specs/03-rating-engine.md`: FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236, FR-232, §4.2, §5.1.
- `docs/roadmap.md` §7: the WK-670 row and the Phase 2 workstreams.
- `docs/specs/04-optimisation.md` §4: bulk-operation metadata structure (to be refined in spec if WK-670 requires it).
- `backend/src/app/platform/rating_versions.py`: the Phase 1b seam this plan widens.
