# Work-item record — W10-3 (Bulk Operations, Import/Export, Storage Spill)

Audited 2026-08-28 against origin/main `f442387` (final slice PR #311 merged, CI
docs + frontend green, python in flight at filing time), the executor's self-split
of the plan's W10-3 slice into four PRs: #304 (3A), #307 (3B), #310 (3C), #311 (3D),
with the decision-maker's rulings #305, #306, #308, #309 landing alongside.

## Scope

Derived from `docs/plans/2026-08-28-w10-rate-tables.md` slice W10-3 (T1–T4) first, then
evidenced. W10-3 delivers FR-RATE-18 (bulk operations that record their parameters),
FR-RATE-20 (CSV/XLSX export/import with strict round-trip), and the storage half of
FR-RATE-62 (workspace-configurable cell-count threshold, parquet spill, 202-with-Job
diff), plus the backend endpoints behind FR-RATE-16/19/62's write paths:

- 3A (contract, #304): `RateTableVersion` wire form per 03 §4.2 — `created_by_operation`
  XOR `created_by_import`, `BulkOperation` per 04 §4.4, `ImportVerdict.applied_to`
  (#306 fold), `JobKind.RATE_TABLE_DIFF`
- 3B (pricing-core ops, #307): `uplift_table` / `uplift_by_filter` / `floor_and_cap` /
  `rebase_to_level` (each validating before persisting, FR-RATE-19), `decide_storage_mode`
  (FR-RATE-62), `export_to_csv` / `export_to_xlsx` / `import_from_csv` /
  `import_from_xlsx` with the shared strict pipeline (FR-RATE-20)
- 3C (backend, #310): threshold REGISTRY entry `rate_tables.cell_threshold` (DP2, read
  at write time only), migration `c9c2e5f8b1d4`, bulk/export/import endpoints, parquet
  write path (`BlobRef` put), `_guard_seed_lineage` (DP4, RATE_TABLE_SEED_MISMATCH),
  import confirmation (DP6), uploaded filename (DP5)
- 3D (backend, #311): 202-with-Job diff endpoint (baseline-first), DP3 `DiffCache`,
  the first `JobResult(kind="blob")` worker handler, typed 200 `RateTableDiff`,
  migration `d5e6f7a8b9c0` (job_kind enum), the 501 superseded

Slice gate (plan §4): bulk operations record their parameters, CSV/XLSX round-trip
preserves schema and completeness, and the storage threshold determines whether diffs
run as SQL joins or Jobs.

## Divergences from the plan (both follow the spec or a ruling — recorded, not silent)

| Plan | Spec / ruling (implemented) |
|---|---|
| W10-3 T4 drafted `/versions/{version}/` forms for bulk/import/export | `{slug}@{version}` — the module's established versioned addressing, ruled 2026-08-28 (decision-maker, recorded in 03 §5.1) because an operation must state the baseline it transforms |
| Import preview, then a separate confirmation mechanism | one `POST .../import` with `confirm: true` (ruled DP6) — the same bytes are parsed again through the shared strict pipeline, so the created version cannot diverge from the preview; confirmation cannot override the round-trip verdict |
| Import record's filename as a format-derived constant | the actually-uploaded name (ruled DP5), bounded ≤255 chars, text, never a path |
| `storage` spill decision at write time | DP2: threshold changes apply to new versions only; old versions keep their storage (immutability, FR-RATE-62) |
| `seeded_from` on derived versions unspecified | DP4: derived versions inherit the baseline's `seeded_from` unchanged; save-time equality proof (`_guard_seed_lineage` → RATE_TABLE_SEED_MISMATCH 422, direction-neutral) |

## Evidence

**Requirement coverage (head `f442387`, scope-audit §3.3):** 9/9 in-scope requirements
evidenced (100 %). req-coverage marker counts: FR-RATE-18 ×24, FR-RATE-20 ×26,
FR-RATE-62 ×25 test files (W10-3's share; FR-RATE-16 ×11, FR-RATE-17 ×10, FR-RATE-19 ×5
carry the slice's guard and import tests too). No nonexistent-ID FAIL.

| Requirement | Verdict |
|---|---|
| FR-RATE-18 | ✓ delivered and tested — four bulk operations record their parameters (`uplift_table: percentage=…` auto-notes mirror 04 §4.4); each validates before persisting (FR-RATE-19); named refusals `FILTER_UNKNOWN_KEY` / `FLOOR_ABOVE_CAP` / `REBASE_NO_MATCH` / `REBASE_AMBIGUOUS` / `REBASE_ZERO_REFERENCE` |
| FR-RATE-20 | ✓ delivered and tested — export CSV/XLSX + import with strict round-trip (`_checked_import` shared by preview and confirm: header equality, ragged-rows check, type check, completeness); named refusals `IMPORT_KEY_MISMATCH` / `IMPORT_TYPE_MISMATCH` / `IMPORT_PARSE_ERROR`; import presents the diff, `confirm: true` creates the version (201, same wire shape as bulk-operation); cannot-override test proves 422 + no version created |
| FR-RATE-62 | ✓ delivered and tested — `rate_tables.cell_threshold` REGISTRY (INT 250 000, min 1), read at version-creation time only (DP2); `decide_storage_mode`; rows → PostgreSQL rows, parquet → content-addressed blob; 202-with-Job diff where either version is `storage: parquet` (baseline resolved before the storage check — same refusals as the 200 path); worker computes the same artifact and returns `JobResult(kind="blob", ref=sha256)` fetchable from `/blobs/{sha256}`; the 501 (`RATE_TABLE_PARQUET_UNBUILT`) retired and superseded in 03 §5.1 with a dated W10-3D amendment |

**Judgment calls judged in audit (3C):** import `change_note = "import: <filename>"`
mirrors the bulk-op auto-note convention; `RATING_WRITE` on preview and confirm matches
the datasets file-upload convention (datasets.py preview_source); confirm's 201 matches
the bulk-operation 201 wire shape. **(3D):** baseline-first ordering is correct — both
forms answer identically about what exists, and with a real 202 the baseless must 404
in both; the pair-of-content-hashes cache key means a change in either version is a
different entry; the blob-kind result outlives the Job row and is content-addressed;
the worker path has no cache because the blob IS the cache for that pair.

## Gate

Measured in audit at head `d6d05ad7` (= merged `f442387`): ruff clean · mypy clean
(146 files, zero suppressions) · lint-imports 3 contracts kept, 0 broken · pytest
2233 passed / 2 skipped / 1 xfailed = 2236 collected (reconciled against
`--collect-only`) · audit-docs all passed · req-coverage clean · generate-contracts
--check 28/28 (all six rate-table endpoints published; diff 200 is `$ref RateTableDiff`,
202 is `$ref Job` — the dict[str, Any] 200 is gone). CI on the merge: docs success,
frontend success, python in flight at filing time (lead verifies terminal state).

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W10-2-1 | DP3's diff cache was unbuilt and its deferral was not declared in PR #302 | resolved 2026-08-28 (PR #311) — `DiffCache` shipped with 3D: pair-of-content-hashes + portfolio dataset version identity key (never a date), no TTL, fail-open both get/set (proven on a broken client), 200 read path only | closed (register row updated) |
| FR-PLAT-48 (F-W10-2-2) | W10-2's diff endpoint answered `dict[str, Any]` while the platform computes a typed RateTableDiff — the ADR-0002 divergence class, invisible to the drift check | resolved 2026-08-28 (PR #311) — the diff 200 is declared `$ref RateTableDiff` in the generated OpenAPI; the deferral's register row was filed with the discharge | closed (register row filed) |
| F-W10-3 | 03 §5.1 `POST /api/v1/rate-tables/{slug}/versions` ("New Rate Table Version with change note", declared Phase 0) has no route; version creation happens via the three create paths (seed-from-model creates the table or appends, bulk-operation, import-confirm), each change-note-required | deferred with an owner — the W15 rate-table editor slice (the manual editing entry point); the plan's W10-1 T3 create/GET/list endpoint tasks were plan-only, never spec-declared, and fold into this row | carried (register row filed) |
| NO_RELATIVITIES (3C nuance) | its first platform use was W10-2's seed path, where it was absent from errors.py — a latent 500; 3C declares it with the other nine owned codes | accepted — the spec's "all ten declared before first use" is strictly true for nine, and this PR closed the gap | closed |

**Spec record notes (non-blockers):** 03 §4.2's example version carries
`diff_vs_previous` / `diff_vs_seed` keys — these are the diff endpoint's read model
(`RateTableDiff`), not stored fields on the version; candidate annotation cleanup.
`docs/contracts/schemas/rate-table.schema.json` is a Phase-0 hand-authored schema
nothing references (model-schema owns the shapes) — cleanup candidate, owner: the
maintainer.

## Sign-off

Auditor verdict: slice verified — clean across 3A (after two re-audits, F-3A-1/2/3
closed), 3B (after F-3B-1), 3C (no fixable gaps) and 3D (no fixable gaps). Verdicts
adopted by the lead; merged 2026-08-28 as `3f3fe3c` (#304), `0e14d39` (#307),
`49be463` (#310), `f442387` (#311).
