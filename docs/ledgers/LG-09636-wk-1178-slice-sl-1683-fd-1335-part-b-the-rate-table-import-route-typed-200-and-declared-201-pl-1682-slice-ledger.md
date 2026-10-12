---
id: LG-9636
family: ledger
title: WK-1178 slice SL-1683 — FD-1335 Part B for the rate-table import route, a typed 200 (ImportPreview) and a declared 201 (RateTableVersion) (PL-1682), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: c26cfdc4d8b6f7e818975d9da1ca084a825611aa
phase: P2
work: WK-1178
slice: SL-1683
plans: [PL-1682]
corrected_by: []
relates: [PL-1682, SL-1683, FD-1335, FD-1684, SL-1669, PL-1667, SL-1547, FR-235, FR-451]
---

# LG-9636 — WK-1178 slice SL-1683: the rate-table import route, a typed 200 and a declared 201

**GO:** the lead's from-lead entry "2026-10-12 07:50:10 BST" (GO SL-1683; the ledger's working id 9636). Authority for the scope: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-12 07:28:38 BST" (flag (1) → (d): type the import 200 first from model-schema types; no cast; S5's gate waits for this slice) and "2026-10-12 07:46:06 BST" (items 1 and 2: DP-1 the 201 typed as RateTableVersion; DP-2 no standalone schema).
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Tasks

Executed from `PL-1682` (Tasks 0–4), branch `sl-1683-wk1178-import-200-typing`, worktree `.claude/worktrees/sl-1683`, cut from `origin/pl-9906-wk1178-import-200-typing` `c26cfdc4d8b6f7e818975d9da1ca084a825611aa` (PR #1297, not yet on `origin/main` `50bbdd96`). `origin/main` is merged in once #1297 lands.

### Task 0 — preconditions

- **Authority read in full** in `to-lead.md`: the maintainer's (by delegation) entry "2026-10-12 07:28:38 BST", flag (1), which says: *"(d): a tiny WK-1178 slice (Part B continued) gives POST /rate-tables/{slug}@{version}/import a response_model built from the existing model-schema types (RateTableDiff + ImportVerdict, or the composed model DEFINED IN model-schema, not in TS). It removes the route from UNTYPED_2XX_PENDING_PART_B; contracts and the generated client are regenerated. S5 then uses the generated type with no cast."* and *"S5's gate waits for it"*; and the maintainer's (by delegation) entry "2026-10-12 07:46:06 BST", item 1 (*"A bare response_model=ImportPreview would 500 on the confirm branch … Typing the 201 as RateTableVersion is the same pair the manual-edit route uses"*) and item 2 (*"generated.json is drift-checked, so a standalone schema file would be a second copy"*). Entries after 07:28:38 on `import`, `ImportPreview`, `FD-1335` or `UNTYPED_2XX`: only the 07:46:06 entry (items 3–5 are FD-1684's, not this slice's). The last to-lead header read is "2026-10-12 07:46:06 BST".
- **Premises re-read at the slice base `c26cfdc4`:** a (`backend/src/app/api/rate_tables.py:266-326`: no `response_model`, `-> dict[str, Any]`, both returns `model_dump(mode="json")`), e (the manual-edit decorator at `:138-147`, `response_model=None` plus `responses` with `200`/`201` models), f (`backend/tests/test_contracts.py:3191-3196` the pending list; `:3215` the stale `225-226` citation), b (the regenerated diff below shows the old open 200 and no 201), i (the existing import tests: 10 selected by `-k import`). c, d, g, h, j, k were not needed beyond what the edit touched: `ImportPreview` exists in `model_schema.rating` and was imported, no `packages/model-schema` change.
- **Open PRs:** `gh` not used in this seat; the base PR (#1297) is not on `origin/main` `50bbdd96` at the time of writing, so the merge-in of `origin/main` is still owed.
- **Task 1 (spec):** `03-rating-engine.md` §5.1 import row carries the dated clause, commit `c635c57a`; `audit-docs` leaves only check 31 (working-id gaps, expected until minted).

### Reds, by their cause

- **Red 1** (`test_import_publishes_a_typed_200_and_a_typed_201`, at the base route code): `KeyError: '$ref'` on the 200 — the published 200 was `{"additionalProperties": true, "type": "object"}`. Red on the tree it names, before the code.
- **Red 2** (`test_import_responses_round_trip_through_the_published_models`): a **guard**, green at the base (the route already dumps these models). Shown able to fail: with `return {**preview.model_dump(mode="json"), "planted": 1}` in the preview branch it failed with `ValidationError: 1 validation error for ImportPreview / planted / Extra inputs are not permitted [type=extra_forbidden]`. Scratch edit reverted (`git diff -- backend/src` empty before the real change).
- **Stale-list test**: after the route was typed and `generate-contracts.py` re-run, `pytest backend/tests/test_contracts.py -k untyped` failed with `AssertionError: no longer untyped, remove from the 2xx lists: [('POST', '/api/v1/rate-tables/{slug}@{version}/import', '200')]`. Not red on `main`: it reds only once the route is typed and the contract regenerated (as LG-1676 recorded).

### Green

- Route: `response_model=None`, `responses` with `200: ImportPreview` and `201: RateTableVersion`, return annotation `ImportPreview | RateTableVersion`, both returns are the models (commit `f955366e` below). `pytest -k import` on `test_api_rate_tables.py`: 10 passed. `ruff` and `mypy` on the touched source and test file: clean.
- Contracts: `git diff --stat docs/contracts` names only `openapi/generated.json` (+29/−3): the new `ImportPreview` component (`ImportVerdict` and `RateTableDiff` already existed), the import 200 now a `$ref` to it, and the new 201 `$ref` to `RateTableVersion`. Nothing else of that path moved. `generate-contracts.py --check`: 49 match. `pnpm generate:api` and `type-check`: exit 0.
- Guard list: the import 200 key removed from `UNTYPED_2XX_PENDING_PART_B` (three remain); the `NON_JSON_REQUEST_BODIES` citation now `rate_tables.py:285-286`. `pytest backend/tests/test_contracts.py`: 171 passed, 2 skipped.
- Register: FD-1335's row carries the dated line (`register-lint`: 0 violations).

## PRs

- (none opened yet; the PR is opened by the executor after the gate.)
