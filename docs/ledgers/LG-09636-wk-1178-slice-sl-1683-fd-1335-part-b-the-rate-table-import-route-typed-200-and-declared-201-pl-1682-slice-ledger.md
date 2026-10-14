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

### Gate 1 — merged head, 2026-10-14

Gate head `ee15ba9916639890155394b80e46ad9689f56b13` (the merge of `origin/main` `36e2610a` into the branch; `docs/findings/register.md` resolved as the lead ruled: main's FD-1679 row verbatim, the branch's FD-1684 row kept; `docs/INDEX.md` regenerated with `scripts/doc-index.py`). The Python/docs half ran as the body in `dev-commands`, under `flock -w 3600 /tmp/slots/gate-1`, `GIP_GATE_SLOT` exported, `timeout 3600` per stage, DB `gipricing_sl-1683_8984a869` (alembic rc 0, one head `d4e81b7a2c95`). Start 08:43:52Z, end 09:40:30Z (56 min 38 s). The frontend half ran afterwards, 09:44:26Z to 09:46:25Z, **under a separate `flock` acquisition** (gate-1 was free between the halves, so the halves were not held under one lock; the frontend half has no timing tests).

| stage | exit |
|---|---|
| `uv run ruff check .` | 0 |
| `uv run mypy` | 0 |
| `uv run lint-imports` | 0 |
| `python3 scripts/audit-docs.py` | 1 |
| `uv run python scripts/req-coverage.py` | 0 |
| `uv run python scripts/generate-contracts.py --check` | 0 (49 generated contracts match the models) |
| `uv run pytest -q` | 1 — `13 failed, 5758 passed, 6 skipped, 116 warnings in 3373.30s (0:56:13)` |

| `pnpm install --frozen-lockfile` | 0 |
| `pnpm generate:api` | 0 |
| `pnpm lint` | 0 |
| `pnpm type-check` | 0 |
| `pnpm test` | 0 |
| `pnpm build` | 0 |

Every failure body was read. `audit-docs` prints one failure, `check 31: gap in the full allocation between 1684 and 9636` (the working id `9636` of this ledger is unminted — expected until the mint). All 13 pytest failures carry that same text: ten run `audit-docs.py` on the real tree and assert exit 0 (`1 == 0`), two assert the allocation is contiguous (`test_doc_id_check_exits_0_on_the_real_tree`: `[noncontiguous] docs/INDEX.md has a gap between 1684 and 9636`; `test_an_index_skipping_a_reserved_block_breaks_contiguity`: `[(1684, 9636)]`), and the thirteenth, `test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`, asserts audit-docs exits 0 with the same text. No other cause found.

## PRs

- (none opened yet; the PR is opened by the executor after the gate.)
