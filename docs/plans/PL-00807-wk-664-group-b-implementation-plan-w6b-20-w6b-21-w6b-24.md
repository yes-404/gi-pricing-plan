---
id: PL-807
family: plan
kind: leaf
title: WK-664 Group B Implementation Plan — W6b-20 + W6b-21 + W6b-24
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-26
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-26-w6b-group-b.md
---

# WK-664 Group B Implementation Plan — W6b-20 + W6b-21 + W6b-24

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the three decided open-question slices the manager batched as Group B — W6b-20 (OQ-551 (b)), W6b-21 (OQ-552 (a)), W6b-24 (OQ-655 (c)) — on one branch, into one PR, with one CI pass.

**Architecture:** Three independent changes, one per slice. W6b-20 makes the two views that format money read the dataset's currency via `getDataset(slug)` and deletes the `?? "GBP"` fallbacks. W6b-21 adds a resolved owner name to the `Dataset` shape: the list endpoint batch-resolves `owner_id` to a display name, the frontend owner column renders it with a raw-id fallback, and FR-82 records the sentence. W6b-24 generates two TypeScript type sets from the same OpenAPI — strict for responses, permissive for request bodies — and removes the three `as unknown as ModelSpec` casts. Each slice lands as one commit — spec, code, tests and contract regen together (`CLAUDE.md` §2).

**Tech Stack:** Pydantic v2 (`model-schema`), FastAPI + SQLAlchemy (backend), `generate-contracts.py` regen, Vue 3 + `openapi-typescript` (frontend), `audit-docs.py` and `req-coverage.py` for the docs half.

**Spec:** Three decided open questions, each filed in `docs/open-questions.md` and a module spec's §10:
- `OQ-551` — **DECIDED 2026-08-26: (b)** — views read the dataset's currency via `getDataset(slug)`; the `?? "GBP"` fallbacks are deleted.
- `OQ-552` — **DECIDED 2026-08-26: (c), with (a) as the near-term step** — the list endpoint resolves `owner_id` to a name; FR-82 gains the resolved-name sentence. The (c) route defers with the shared trigger.
- `OQ-655` — **DECIDED 2026-08-26: (c)** — two generated type sets: strict for responses, permissive for request bodies.

**Slice source:** `docs/plans/PL-00811-wk-664-the-slice-map-revised-a-third-time.md` §3 rows for W6b-20, W6b-21, W6b-24; the manager's batching direction (Group B = W6b-20 + W6b-21 + W6b-24, one branch, one PR).

**Highest ids:** No new requirement id is filed. W6b-20 records a dated rule on the existing FR-10 row; W6b-21 amends the existing FR-82 row; W6b-24 records a dated note in `07` §5.3. The decisions are already recorded in each spec's §10 row.

## Global Constraints

- `CLAUDE.md` §2's money rule binds W6b-20: the currency a view formats with must be the dataset's own, never a hardcoded default. `FR-10` governs values; a euro amount under a pound sign is the defect this slice removes.
- W6b-21's `owner_name` is a derived, read-only field on `Dataset`, like `latest_version_status` — it is computed per request from `users` / `service_accounts` and stored on no row. A `None` name is an honest answer (the id did not resolve); the frontend falls back to the raw id, never to a fabricated name (OQ-552's rejection of (d)-as-end-state does not forbid the raw-id fallback; it is the correct interim).
- W6b-21's (c) route — a batch principal-name endpoint — is **not** built by this slice. It defers with the shared trigger (slice-map §1).
- W6b-24 generates both type sets from the same OpenAPI; neither is hand-written (`CLAUDE.md` §2). The strict set keeps `--default-non-nullable` at its default (true); the permissive set passes `--default-non-nullable false`.
- The generated API client (`frontend/src/api/generated/`) is VCS-ignored and never hand-edited. The second generated file inherits the ignore rule from the directory.
- Responses keep the strict set. A type used in both directions keeps its strict alias for reads and gains a separate request alias for the write path.
- Both gate halves pass before a push. This PR touches Python, docs and frontend; all three CI workflows run.
- ASD-STE100 prose. Code, identifiers and file paths stay unchanged.

---

## Findings (verified 2026-08-27 against origin/main 8b0977f)

**F1 (W6b-20). The two `?? "GBP"` fallbacks are the only money-currency defaults in `frontend/src`, and nothing passes the prop.** `ProfileView.vue:42` and `VersionDetailView.vue:25` both resolve `props.currency ?? "GBP"`, and both declare `currency?: string` on their props (`ProfileView.vue:23`, `VersionDetailView.vue:15`). The router mounts both with `props: true` (`router/index.ts:58,65`), which maps route params — `slug` and `version` — and never `currency`, so the fallback is the only path, exactly as OQ-551 states. `getDataset(slug)` exists (`frontend/src/api/datasets.ts:32`) and returns `Dataset` with `currency: string` required (`schema.d.ts:3308`); the generated `DatasetVersion` carries no `currency` (`schema.d.ts:3463-3521`), which is why the (b) mechanism reads the dataset, not the version. Both views already hold a `slug` prop and call `getVersion(props.slug, …)`, so the extra fetch is one call in the existing `load()`.

**F2 (W6b-20, locator drift). The slice map's "00 §5.3 records the rule" does not match the section.** At the map's anchor (`7400846`) and at `8b0977f`, `00` §5.3 is the **Error model** — no home for a currency rule. The rule is a money-correctness fact and belongs on FR-10's row (`00` §3, `00-overview.md:213`), which already carries the one-currency sentence (OQ-542). The plan files the drift and records the dated rule there.

**F3 (W6b-21). `owner_id` is returned raw; no principal-name resolution exists anywhere.** The list endpoint builds each row with `to_schema` (`api/datasets.py:336-341`), and `to_schema` sets `owner_id=row.owner_id` (`platform/datasets.py:393`) with no name. `latest_version_status` already rides on a batched `_latest_versions` query (`api/datasets.py:348-380`); the owner resolution composes with that batching. There is no `/api/v1/users` and no principal-lookup route (`00` §5.1, OQ-552); `/api/v1/me` answers for the caller alone (`api/me.py:152`). A principal id is a UUID that is either a `UserRow.id` or a `ServiceAccountRow.id`: `Principal(kind=ActorKind.USER, id=user.id, display=user.email or claims.subject)` (`auth/service.py:117-118`), and `Principal(kind=ActorKind.SERVICE_ACCOUNT, id=account.id, display=account.slug)` (`auth/service.py:225-226`). `UserRow` carries `display_name`, `email`, `subject` (`db/models.py:363-365`); `ServiceAccountRow` carries `slug` (`db/models.py:379`). The seed writes the analyst with `display_name="Demo Analyst"` and `email="analyst@example.fr"` (`examples/fremtpl2/seed.py:351-352`), so the demo owner resolves. The test-suite `principal` fixture is a bare `Principal` with no `UserRow` (`conftest_db.py:201-202`), so the resolution must be null-tolerant: an unresolvable id yields `owner_name = None` and the frontend falls back to the raw id.

**F4 (W6b-21, shape consistency). Four more `Dataset`-returning routes call `to_schema`.** `create_dataset` (`api/datasets.py:296`), the detail route (`:440`), `patch_dataset_owner` (`:479`) and `put_dictionary` (`api/datasets.py:502`) all return a `Dataset`. FR-55's recorded finding is that the same artifact shape from two routes disagreeing is a defect; `owner_name` must not repeat it. The list uses the batch helper; the single-row routes resolve one id; `create_dataset` and the ingestion path use the actor's own display. The `to_schema` keyword is optional, so a caller that omits it yields `None` — but every current route populates it.

**F5 (W6b-24). One generated type serves both directions, and three casts live with it.** `generate:api` runs `openapi-typescript` `^7.13.0` once with no flags (`frontend/package.json:13`), so `--default-non-nullable` takes its default of *true* and every property carrying a JSON-Schema `default` is a required TypeScript property. Verified in the artifact: `GlmSpec` lists 3 required and 13 defaulted properties; `GbmSpec` 8, `EbmSpec` 10. The consequence is three `as unknown as ModelSpec` casts at `ModelSpecBuilderView.vue:142,149,155` — the only non-test `as unknown as` in `frontend/src` — documented at `:121-128`. The CLI flag is verified: `openapi-typescript --default-non-nullable false` disables the default-required behaviour (`openapi-typescript --help`). The whole `frontend/src/api/generated/` directory is VCS-ignored (`.gitignore:38`), so the second generated file inherits the rule.

**F6 (W6b-24, request-body surface).** The client types request bodies from component schemas at: `modelSpecs.ts:10` (`ModelSpec`, via `ModelSpecValidate.spec`), `rules.ts:11` (`RuleCreate`, `createRule` at `:69`), `transformations.ts:14,16` (`Banding`, `Grouping` — used both as request bodies in `createBanding`/`evaluateBanding`/`createGrouping`/`evaluateGrouping` and as response types in `listBandings`/`listGroupings`), and `datasets.ts:8` (`DataDictionaryEntry`, used in the `putDictionary` body). `Banding`, `Grouping` and `DataDictionaryEntry` carry defaulted properties, so the strict set over-requires a request. The permissive set types these write paths correctly without weakening response reads, which keep the strict alias.

---

## Tasks

### Slice W6b-20 — the views read the dataset's currency

**T1. 00 spec: record the rule on FR-10.**
- [ ] Add a dated amendment to the FR-10 row (`00-overview.md:213`): a view that formats a monetary amount reads the dataset's currency via `getDataset(slug)` (OQ-551, decided 2026-08-26 (b)); a hardcoded currency default is forbidden because a wrong symbol renders a right-looking wrong number. Note the drift: the slice map's "00 §5.3" is the Error model, so the rule lives here.
- [ ] Run `python3 scripts/audit-docs.py`.

**T2. ProfileView: fetch the dataset and read its currency.**
- [ ] Import `getDataset` and the `Dataset` type from `@/api/datasets` (`ProfileView.vue` currently imports `listVersions` from there).
- [ ] Add `const dataset = ref<Dataset | null>(null);` and remove `currency?: string` from the props (`:23`).
- [ ] In `load()` (`:79`), set `dataset.value = await getDataset(props.slug)` inside the same try block as `getVersion`.
- [ ] Replace the `currency` computed (`:42`) with `computed(() => dataset.value?.currency ?? "")`, with a dated comment: the empty string is unreachable at render — the value is read only inside the loaded branch — and is not a money default.
- [ ] Delete the `?? "GBP"` fallback. Confirm the two deleted sites are the only money-currency defaults in `frontend/src`.

**T3. VersionDetailView: same change.**
- [ ] Import `getDataset` and the `Dataset` type; add the `dataset` ref; remove `currency?: string` from the props (`:15`).
- [ ] In `load()` (`:35`), set `dataset.value = await getDataset(props.slug)`.
- [ ] Replace the `currency` computed (`:25`) with the dataset-derived form, same dated comment.
- [ ] The template's `formatMinor(detail.totals.claim_amount_minor, currency)` (`:172`) now reads the dataset's currency.

**T4. Frontend tests: the views fetch the currency themselves.**
- [ ] `ProfileView.test.ts` and `VersionDetailView.test.ts` currently pass `currency: "EUR"` in props (`ProfileView.test.ts:237`, `VersionDetailView.test.ts:58`). Remove the prop and stub `getDataset` to return the dataset with the intended currency; keep the EUR assertion (`ProfileView.test.ts:265`, `VersionDetailView.test.ts:73-77`).
- [ ] Add a test each: when `getDataset` returns the dataset's currency, the view renders in that currency (the fallback path is gone, so a missing currency is not a valid render state).

**T5. Docs half.**
- [ ] Run `python3 scripts/audit-docs.py` and `uv run python scripts/req-coverage.py`.

### Slice W6b-21 — the owner display, interim

**T1. 01 spec: FR-82 gains the resolved-name sentence.**
- [ ] Amend the FR-82 row (`01-data-management.md:213`) with a dated sentence (OQ-552, decided 2026-08-26 (a)): the §5.3 owner column renders the principal's resolved display name, never the raw id; `owner_name` is a derived, read-only field on `Dataset`, resolved per request from `users` and `service_accounts`, and null when the id does not resolve (the view then falls back to the id).
- [ ] Sweep `git grep owner_id docs/specs/01-data-management.md` and amend any quotation the sentence changes.
- [ ] Run `python3 scripts/audit-docs.py`.

**T2. model-schema: the derived field.**
- [ ] Add `owner_name: str | None = None` to `Dataset` (`packages/model-schema/src/model_schema/datasets.py:156`), beside `owner_id`, with a comment: derived per request (OQ-552 (a)), stored on no row, null when the id does not resolve.
- [ ] Add a model-schema test: a `Dataset` constructs with or without `owner_name`.

**T3. backend: the resolution and the routes.**
- [ ] Add `resolve_owner_names(session, owner_ids) -> dict[UUID, str]` to `backend/src/app/platform/datasets.py`: batch `users` by id (display = `display_name` or `email` or `subject`) and `service_accounts` by id (display = `slug`); merge; ids in neither table are absent. One query per table, independent of page size.
- [ ] `to_schema` (`platform/datasets.py:364`) gains `owner_name: str | None = None` and passes it through to the schema.
- [ ] `list_datasets` (`api/datasets.py:299`): after `_latest_versions` / `_last_validated`, batch-resolve the page's owner ids and pass `owner_name` into each `to_schema` call.
- [ ] `get_dataset` (`:440`), `patch_dataset_owner` (`:479`), `put_dictionary` (`:502`): resolve the row's owner id (one id) and pass `owner_name`.
- [ ] `create_dataset` (`:296`): pass `owner_name=caller.principal.display`.
- [ ] The ingestion path (`backend/src/app/data/ingestion.py:504`): pass the actor's display.
- [ ] Backend tests: the list carries `owner_name` for a resolvable owner and `null` for an unresolvable one; a service-account owner resolves to its slug; the four single-row routes agree with the list on the same dataset (FR-55's disagreement defect does not recur).

**T4. frontend: the owner column renders the name.**
- [ ] `DatasetListView.vue` owner cell (`:227-231`): render `dataset.owner_name ?? dataset.owner_id`; keep the font-mono style for the id fallback and a non-mono style for a name; update the comment (`:217-226`) to record OQ-552 (a) — the list endpoint now resolves the name, and the raw id remains the honest fallback when the id does not resolve.
- [ ] Update `DatasetListView.test.ts`: the SEEDED fixture gains `owner_name`; the "whole owner id" tests (`:198-233`) cover both branches — a resolved name renders the name, an unresolvable owner renders the raw id.

**T5. Contract regen and the docs half.**
- [ ] Run `uv run python scripts/generate-contracts.py`; run `pnpm --dir frontend generate:api`; commit the generated side with the slice.
- [ ] Run `python3 scripts/audit-docs.py` and `uv run python scripts/req-coverage.py`.

### Slice W6b-24 — two generated type sets

**T1. 07 spec: document the flag and the asymmetry.**
- [ ] Add a dated note under `07` §5.3 Frontend views (`07-platform.md:364`): the generated client is produced twice from the same OpenAPI — `generate:api` runs `openapi-typescript` with `--default-non-nullable` (strict, for responses) and without it (permissive, for request bodies) — so a request body may omit a server-defaulted field while a response keeps every default required (OQ-655, decided 2026-08-26 (c)). The generated files are VCS-ignored and never hand-edited.
- [ ] Run `python3 scripts/audit-docs.py`.

**T2. Tooling: two generations.**
- [ ] `frontend/package.json:13`: the `generate:api` script runs `openapi-typescript` twice — once to `src/api/generated/schema.d.ts` (no flags; strict), once with `--default-non-nullable false` to `src/api/generated/schema.requests.d.ts` (permissive).
- [ ] Run `pnpm --dir frontend generate:api`; confirm both files exist and the request set differs from the strict set exactly on defaulted properties (`GlmSpec`'s `alpha: number` becomes `alpha?: number`).

**T3. Request-body aliases.**
- [ ] `modelSpecs.ts`: import the permissive set (`import type { components as requestComponents } from "./generated/schema.requests"`); `ModelSpec` aliases `requestComponents["schemas"]["ModelSpecValidate"]["spec"]`. The builder's `GlmSpec`/`GbmSpec`/`EbmSpec` and their derived unions keep whichever set renders the same union for the fields the view reads.
- [ ] `rules.ts:11`: `RuleCreate` aliases the permissive set.
- [ ] `transformations.ts`: keep strict `Banding`/`Grouping` for response reads (`listBandings`, `listGroupings`, propose/evaluate responses); add permissive `RequestBanding`/`RequestGrouping` aliases for the write-path parameters (`createBanding`, `evaluateBanding`, `createGrouping`, `evaluateGrouping`).
- [ ] `datasets.ts:8`: keep strict `DataDictionaryEntry` for reads; the `putDictionary` body parameter uses a permissive `RequestDataDictionaryEntry`.
- [ ] Sweep the remaining api/ modules for any request body typed against a strict component type that carries defaults; alias each from the permissive set. The sweep is complete when no write-path parameter in `frontend/src/api/` requires a field the request may omit.

**T4. The casts come off.**
- [ ] `ModelSpecBuilderView.vue` (`:130-156`): delete the three `as unknown as ModelSpec` casts and the cast rationale comment (`:118-128`); the three arm objects now assign directly to the permissive `ModelSpec`. If a residual field fails to type, correct the ref's annotation, never re-cast.
- [ ] Update `ModelSpecBuilderView.test.ts` if it asserts on the cast or the request shape.
- [ ] Confirm `git grep "as unknown as" frontend/src` (excluding `__tests__` and the generated dir) returns only the deletions' absence — no new casts.

**T5. Frontend gate.**
- [ ] `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`.

---

## Verification

- Both gate halves pass locally before the push:
  - Python/docs half: `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`, then `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`, then `uv run python scripts/generate-contracts.py --check`.
  - Frontend half: `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`.
- No `?? "GBP"` (or `?? "GBP"`-class currency default) remains in `frontend/src`.
- A euro-denominated dataset renders `€` in both views; a dataset with no explicit currency renders `£` (the model default, read from the dataset — never hardcoded).
- `GET /datasets` carries `owner_name` resolved per row; an unresolvable owner yields `null` and the frontend renders the raw id.
- The migration-free `Dataset` shape change round-trips: the contract regenerates, `test_contracts.py` stays green, and the generated frontend `Dataset` carries `owner_name`.
- `ModelSpecBuilderView` compiles with the three casts removed; `pnpm type-check` is green with no `as unknown as` in `frontend/src` outside tests.
- The two generated type sets exist, are VCS-ignored, and differ exactly on defaulted properties.

## Expected file changes

**W6b-20:** `docs/specs/00-overview.md` (FR-10 amendment) · `frontend/src/views/ProfileView.vue` · `frontend/src/views/VersionDetailView.vue` · `frontend/src/views/__tests__/ProfileView.test.ts` · `frontend/src/views/__tests__/VersionDetailView.test.ts`.

**W6b-21:** `docs/specs/01-data-management.md` (FR-82 amendment) · `packages/model-schema/src/model_schema/datasets.py` · `packages/model-schema/tests/` · `backend/src/app/platform/datasets.py` · `backend/src/app/api/datasets.py` · `backend/src/app/data/ingestion.py` · `backend/tests/test_api_datasets.py` · `frontend/src/views/DatasetListView.vue` · `frontend/src/views/__tests__/DatasetListView.test.ts` · `docs/contracts/schemas/generated/` · `frontend/src/api/generated/` (ignored).

**W6b-24:** `docs/specs/07-platform.md` (§5.3 note) · `frontend/package.json` · `frontend/src/api/generated/schema.requests.d.ts` (ignored) · `frontend/src/api/modelSpecs.ts` · `frontend/src/api/rules.ts` · `frontend/src/api/transformations.ts` · `frontend/src/api/datasets.ts` · `frontend/src/views/ModelSpecBuilderView.vue` · affected frontend tests.

## Drift records

1. **The slice map's "00 §5.3" is the Error model (W6b-20).** The map's citation does not match the section at the anchor (`7400846`) or at `8b0977f`. The currency rule is a money-correctness fact and is recorded on the FR-10 row instead (F2).

2. **W6b-21 needs backend work despite the "frontend" grouping.** The owner display's mechanism is the list endpoint resolving `owner_id`; Group B's PR therefore spans `model-schema`, `backend/`, `frontend/` and `docs/`. This is the decision's own mechanism (OQ-552 (a)), not a scope extension.

3. **`owner_name` is populated by every `Dataset`-producing route, not only the list.** The decision names the list endpoint; FR-55's recorded shape-consistency finding requires the other four routes to agree (F4). The `(c)` route — a batch principal-name endpoint — is deferred with the shared trigger and is not built here.
