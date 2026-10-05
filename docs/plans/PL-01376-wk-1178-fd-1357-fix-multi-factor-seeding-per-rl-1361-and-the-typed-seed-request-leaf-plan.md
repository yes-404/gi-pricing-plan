---
id: PL-1376
family: plan
kind: leaf
title: WK-1178 slice — FD-1357's fix, multi-factor seeding per RL-1361 (one table per Factor, factor_ref), with the seed route's request and 201 typed (FR-228, FR-230, FR-234, FR-451): leaf plan
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-03
owner: planner
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-1178
slice: SL-1377
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1357, RL-1361, FD-1358, FD-1366, PL-1364, PL-1267, RL-1263, PL-1359, SL-1360, PL-1306, ADR-704]
---

# PL-1376 — WK-1178 slice — FD-1357's fix: multi-factor seeding per RL-1361, with the seed route typed: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `test-driven-development` (every acceptance
> item is seen red before the code that turns it green), `python-test` (the `req` marker,
> broken-input proofs), `python-package` (model-schema shapes, import boundaries),
> `fastapi-service` (the route and its problem responses), `contract-guard` and
> `contract-schema` (the generated slugs and `ONE_SIDED_SLUGS`), `spec-change` (the
> `RL-1361` texts), `dev-commands` (the two-half gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s conventions before the first step. The executor is spawned
> from `.claude/roles/executor.md`.

## Status

Filed 2026-10-01 10:18 BST against `origin/main` `1dd5e264195677b4a13268b80ac8673c2c027135`
(tree object `8bd782acbbdde8e3b4195b5a0acb89183b5a0253`), under **working id 9764** (this
plan) and **working id 9763** (its slice row `SL-1377` under `### WK-1178` in
`docs/roadmap.md`, `draft`). The lead reserved both ids and is the only allocator. Both are
minted at the merge turn; every working-id citation is then re-pointed. Unminted ids are
cited in working-id form and kept out of `relates:` (check 32). Two are cited here: `PL 9765`
(WK-674 Slice 2's superseding plan) and `RL-1375` (the ruling on DP-1 to DP-4, draft PR #1065).
Each is re-pointed when it is minted. *(Re-pointed 2026-10-01 at the merge of `origin/main`
`92b4e4ac`, where mint batch A landed: working id 9788 is `PL-1364`; 9779 is `FD-1366`.)*
*(Minted 2026-10-03 at `origin/main` `6891b30e` as `PL-1376`, filed under working id 9764, with
its slice row `SL-1377`, filed under working id 9763, and the ruling `RL-1375`, filed under
working id 9757. The citations of those three are re-pointed. `PL 9765` stays in working-id
form. The FD-1357 batch.)*

**Amended before its mint, 2026-10-01, on auditor-1057's audit of #1057 at `205e71e2`** (four
findings, all adopted by the lead). A plan freezes at its first merge, so this is pre-merge
authoring of the same draft. The changes:
- F1: DP-1 is reframed as (a1), (a2) and (b) against `_resolve_baseline`, and "no diff
  output" is now conditional on it.
- F2: `__init__.py` exports both `RateTableVersion` and `SeedFromModelRequest`.
- F3: Acceptance 9 counts by text kind.
- F4: red-first cases are added (the `factor_ref` type, the request refusals, Acceptance 4's
  red), with the hardening message rule and the refusal order.

**Amended again before its mint, 2026-10-01, on `RL-1375`** (filed as working id 9757; draft PR #1065 at
`cb3f9705`, by `dm-1357`), which rules DP-1 to DP-4, and on the lead's items P1 to P7 and the
maintainer's addendum to P7. The changes:
- DP-1 is decided (a2), with the ruling's resolver rule. The resolver cells cite `RL-1375`,
  and premise m is added.
- New acceptance items: the re-seed baseline test (13), the rewritten origin test (14) and the
  `against=seed` sweep (15). The "no diff output" lines are now unconditional.
- `T-A` and `T-B` join the text table and Acceptance 9. Acceptance 3(e) is widened to DP-2's
  full rule.
- The write set gains `_resolve_baseline`, `scripts/audit-docs.py` with
  `tests/test_audit_docs_ids.py`, and, conditionally, the `contract-schema` skill.
- The 201 is `response_model=RateTableVersion`, with a stop on a suffixed component name.

**`draft`.** The plan stays `draft` while any **blocking** decision point below is open and
until every activation need is met. It turns `active` in a **separate activation PR**, on the
maintainer's agreement and the lead's go.

## Goal

`seed_from_model` seeds a GLM with two or more factors. Per `RL-1361` section A, one seed
request names one Factor, and it seeds **one table with one key**, bound by `factor_ref` to
the Factor version the model pins. The platform loads the model's Factors and passes them in
(section D). The seed route's request body becomes a typed `model-schema` request, and its
201 becomes a typed response. Both are `$ref`s to shapes published under
`docs/contracts/schemas/generated/`. An unseedable row shape is a named 422, never a
`KeyError`. The `[seeding]` spec texts of `RL-1361` are applied byte for byte, with `T1` and
`T5` if this slice lands `factor_ref` first.

**Architecture.** `RateTableKey` gains `factor_ref: ArtifactRef | None = None` (type
`factor`), with a validator that refuses a key carrying both `factor_ref` and `banding_ref`
(`RL-1361` Ruled item 9). The pure `seed_from_model` gains `factor: str` and
`factors: Sequence[Factor]` (`RL-1361` T9). It extracts the one named relativity entry and
binds its key. The platform `seed_from_model` calls `load_factors` with `model.spec.factors`
under the caller's workspace. It checks the lineage before it appends. The route takes a
`SeedFromModelRequest` and declares its 201 as `RateTableVersion`.

**Breaking change.** A body without `factor` is now refused 422. The route's only caller at
`1dd5e264` is `backend/tests/test_api_rate_tables.py`; the frontend has none (premise d).
The commit message carries a `BREAKING CHANGE:` footer (`RL-1361`, "The contract, a breaking
change").

## Acceptance Standard

Each item is shown **red first**: the test is written, run on the unmodified tree (or on the
named broken input), and its failure is quoted in the ledger before the code that turns it
green. "Red" below names the expected failure. A test that has never printed its failure is
not evidence (`CLAUDE.md` §13).

1. **A two-factor model seeds one table per Factor, end to end** (`FR-230`, the FD-1357 red).
   `backend/tests/test_api_rate_tables.py::test_a_two_factor_model_seeds_one_table_per_factor`.
   It uses an approved GLM whose fit carries two categorical relativity entries
   (`driver_age_band`, `region`), each pinned as a Factor in `model.spec.factors`. It sends
   two seed requests, one per Factor, to two table slugs. Each gives 201 and a table with
   exactly one key, named after the Factor's slug, with that Factor's levels only.
   **Red on `1dd5e264`:** the current `_seed_body` ignores `factor` and seeds every entry, so
   `validate_rate_table` raises `KeyError` (`operations.py:289`) and the route answers 500.
   Quote the status and the `KeyError` from the log.
2. **The seeded key is bound** (`FR-228`, `FR-230`).
   `packages/pricing-core/tests/test_rate_table_operations.py::test_the_seeded_key_is_bound_to_the_pinned_factor_version`:
   the pure seed's one key is
   `{"name": <slug>, "type": "string", "factor_ref": "factor:<slug>@<version>"}`, and its
   `banding_ref` is `None`. Its domain is the entry's levels that carry a relativity.
   **Red on `1dd5e264`:** `TypeError` (no `factor` parameter). On broken input (the key
   built without `factor_ref`), the test fails.
3. **Seeding refusals, each by name** (`RL-1361` sections A and D; `T7`'s 422 and 404).
   Pure tests in `test_rate_table_operations.py` and route tests in
   `test_api_rate_tables.py`:
   - (a) a `factor` that names no relativity entry: 422 `VALIDATION_FAILED`;
   - (b) a continuous factor (it has no relativity entry): 422 `VALIDATION_FAILED`;
   - (c) a named entry with no Factor of that slug among those passed: refused. **Broken
     input:** a fallback to an unbound key makes the seed succeed, and the test fails;
   - (d) two passed Factors with that slug: refused;
   - (e) a seed into an existing table that `RL-1375` DP-2 refuses: 422 `VALIDATION_FAILED`,
     with a detail naming the table slug and the current version's key names. One route test
     per shape: a one-key table bound by `factor_ref` to another Factor's slug; a one-key
     unbound table with another name; a one-key table bound by `banding_ref`; and a two-key
     table. **Red on `1dd5e264`:** each answers 201 (or 500 on the two-key table);
   - (e′) the seeds DP-2 accepts: a one-key unbound table whose key is named after the
     Factor's slug (the shape of every seed made before `factor_ref`), and a one-key table
     whose `factor_ref` names the same slug. Each gives 201, and the new version's one key
     carries `factor_ref` to the model's pinned Factor version. **Red on `1dd5e264`:** the new
     version's key has no `factor_ref`;
   - (f) a `model.spec.factors` id that does not resolve in the caller's workspace: 404
     `NOT_FOUND` (`load_factors`). It is never an empty list.
   **Red on `1dd5e264`:** (a) to (d) raise `TypeError` at the pure level, and at the route
   (a), (b) and (e) answer 201 or 500. (f) answers 201, because nothing loads Factors.
4. **A re-seed with a newer version of the same Factor is accepted** (`RL-1361` section A;
   its Acceptance, "Re-seed with a newer version of the same Factor is accepted").
   `test_api_rate_tables.py::test_a_reseed_with_a_newer_version_of_the_same_factor_is_accepted`:
   model v2 pins version 2 of the Factor that model v1 pinned at version 1. Seeding v2 into
   v1's lineage gives 201 and version 2 of the table, and its key's `factor_ref` is
   `factor:<slug>@2`. **Broken input:** the slug check compares the whole
   `factor:<slug>@<version>` reference. The seed is refused, and the test fails.
   **Red on `1dd5e264`:** the re-seeded version's key carries no `factor_ref` (the field does
   not exist, so the JSON key is absent), and the assertion on `factor:<slug>@2` fails.
5. **One binding, never two** (`FR-228`, `RL-1361` Ruled item 9).
   `packages/model-schema/tests/test_rate_tables.py::test_a_key_carries_at_most_one_of_factor_ref_and_banding_ref`
   first asserts that a key with **only** `factor_ref` validates, then that a key with both
   is refused with `ValidationError`. A second test,
   `test_a_factor_ref_of_another_artifact_type_is_refused`, first asserts that a valid
   `factor:<slug>@<version>` key is accepted, then that a `factor_ref` of another type (for
   example `banding:<slug>@<version>`) is refused with `ValidationError` (`RL-1361` Ruled
   item 9, "of type `factor`"). **Red on `1dd5e264`:** in both tests the first assertion
   fails (`extra="forbid"` refuses `factor_ref`). The first assertion exists so that the
   refusal cannot pass vacuously on the current tree.
6. **The request is typed** (maintainer's rule (i); `FD-1366`'s seed-from-model entry).
   `test_api_rate_tables.py::test_the_seed_route_publishes_a_typed_request_and_201`, against
   `docs/contracts/openapi/generated.json`. The `POST /api/v1/rate-tables/{slug}/seed-from-model`
   `requestBody` JSON schema is a `$ref` to the `SeedFromModelRequest` component, and
   `docs/contracts/schemas/generated/seed-from-model-request.schema.json` exists. A body
   without `factor` gives 422 `VALIDATION_FAILED`, with a field error on `factor`.
   **Red on `1dd5e264`:** the schema is
   `{"additionalProperties": true, "title": "Body", "type": "object"}`, and the body without
   `factor` gives 201.
   **6b. The request's own refusals** (per DP-3's ruling; listed here for DP-3 (a)).
   `packages/model-schema/tests/test_rate_tables.py::test_the_seed_request_refuses_bad_bodies`,
   parametrised, each case after a positive control (a valid body validates):
   a blank or whitespace-only `change_note` (FR-229), a `model_ref` of another artifact type
   (`rating_algorithm:x@1`), an empty `factor`, and an unknown field (under `extra="forbid"`).
   Each raises `ValidationError`. At the route, each is 422 `VALIDATION_FAILED` with a field
   error. **Red on `1dd5e264`:** `ImportError` (`SeedFromModelRequest` does not exist). At
   the route, the unknown field and the missing `factor` give 201. Under DP-3 (c), the
   unknown-field case is dropped.
7. **The 201 is typed** (maintainer's rule (ii); `RL-1375` DP-4). The route declares
   `response_model=RateTableVersion` and returns the instance (the precedent is
   `sub_graphs.py:42`). The same test asserts that the 201 JSON schema is a `$ref` to the
   component named **exactly** `RateTableVersion`, and that
   `docs/contracts/schemas/generated/rate-table-version.schema.json` exists.
   `uv run python scripts/generate-contracts.py --check` exits 0. **Red on `1dd5e264`:** the
   201 schema is an open object, and the generated file is absent. **Stop:** if FastAPI
   emits a suffixed component name (for example `RateTableVersion-Output`), the executor
   stops and reports to the lead (`RL-1375` DP-4).
8. **An unseedable row shape is a named 422, never a `KeyError`** (`FR-234`; FD-1357
   *Disposition*, "Hardening").
   `test_rate_table_operations.py::test_a_row_lacking_a_declared_key_is_a_named_refusal`: a
   two-key declaration with a row that carries one key. `validate_rate_table`,
   `diff_vs_previous` and `diff_vs_seed` each raise `ValueError`, and its message names the
   missing key. Through `_map_operation_error` (`platform/rate_tables.py:84-92`), that is 422
   `VALIDATION_FAILED`. **Red on `1dd5e264`:** `KeyError` at `operations.py:289`, `:232` and
   `:327`. Subject to DP-6.
9. **The `RL-1361` texts are applied byte for byte.** For each text this slice applies (see
   *Spec texts this slice applies*), a script in the ledger prints two counts in the file.
   The expected values depend on the text's kind:
   - **Replace texts (`T4`, `T7`, `T8`, `T9`; and `RL-1375`'s `T-A`):** after the edit, the
     find string's count is 0 and the replacement's count is 1. **Red before the edit:** find
     1, replacement 0. `T-A`'s find string and replacement are the one-line fenced blocks of
     `RL-1375`'s Amendment 2026-10-01 10:47 BST (LOW-a) at `23ff15d1`, copied verbatim and
     counted over `docs/specs/03-rating-engine.md`. T-A find (1 before, 0 after):

     ```text
     > seed-from-model, on the first version of a lineage; every derived version — manual
     ```

     T-A replacement (0 before, 1 after):

     ```text
     > `against=seed` on a version resolves to its seed origin: the lowest-numbered version of
     ```

     Every find string and count predicate is copied from `RL-1375`'s **fenced** blocks at
     `23ff15d1`, exactly as `grep -cF` takes them, with no backslash escapes. A
     single-backtick form with a literal escape counts 0.
   - **Append and insert texts (`T1`, `T2`, `T5`, and `RL-1375`'s `T-B`; `T3` is of this kind
     but is Slice 7's):**
     the anchor stays, so after the edit the anchor's count is 1 and the appended or inserted
     text's count is 1. **Red before the edit:** anchor 1, text 0.

   The only filled placeholders are `<fix date>` and `<first date>`, both the date of the fix
   commit, written `YYYY-MM-DD`, and `<RL id>` in `T-A` and `T-B`, which is `RL-1375`'s minted
   id, written `RL-NNNN`.
10. **The untyped-body guard agrees, in either merge order.**
    - **Case A, this slice merges before `PL-1364`** (lane B order). `UNTYPED_REQUEST_PENDING`
      does not exist on main, and this slice adds no entry to any guard list. After this
      slice merges, `PL-1364`'s Task 0 drops the seed-from-model entry from
      `UNTYPED_REQUEST_PENDING`, and its activation re-measure drops
      `("POST", "/api/v1/rate-tables/{slug}/seed-from-model", "201")` from
      `UNTYPED_2XX_PENDING_PART_B`. The lead carries both drops to `PL-1364`'s dispatch
      record.
    - **Case B, `PL-1364` has merged first.** This slice removes both entries in the same
      commit that types the route. **Red:** with the route typed and both entries still
      listed, the guard's "a typed route still listed fails" test is red. Quote it, then
      remove the entries.
11. **Existing callers are migrated, and the break is proved.** Every seed call at
    `1dd5e264` (premise e) names a `factor` and pins Factor rows. A seed body without
    `factor` is refused 422 (item 6). `grep -rn "seed-from-model\|seed_from_model" backend/tests packages/pricing-core/tests`
    shows no call without `factor`.
12. **The gate, both halves, green on the final tree** (`CLAUDE.md` §11):
    `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`;
    `python3 scripts/audit-docs.py`; `uv run python scripts/req-coverage.py`;
    `uv run python scripts/generate-contracts.py --check`;
    `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api`;
    `pnpm --dir frontend lint && pnpm --dir frontend type-check`;
    `pnpm --dir frontend test && pnpm --dir frontend build`. Each exit code is quoted with
    the tree it ran on (the commit SHA and `git rev-parse HEAD^{tree}`).
13. **A re-seed starts its own seed origin** (`RL-1375` DP-1 (a2), item 4; `FR-230`).
    `test_api_rate_tables.py::test_against_seed_resolves_to_the_versions_own_seed_origin`:
    seed v1 from model A, derive v2 (a manual edit or bulk operation), re-seed v3 from model
    B, then derive v4. `against=seed` on `@4` resolves to v3, and on `@2` to v1. v3's
    `seeded_from.model_ref` names model B. **Red on `1dd5e264`:** `@4` resolves to v1, because
    `_resolve_baseline` takes the lowest-numbered version with any `seeded_from`
    (`platform/rate_tables.py:433-453`).
14. **The origin test keeps its meaning with derived versions** (`RL-1375` DP-1 item 4).
    `test_diff_vs_seed_compares_against_the_origin_not_the_previous_version`
    (`test_api_rate_tables.py:224-262`) keeps its name and its assertions (`@3`: 1 changed
    cell against `previous`, 2 against `seed`). Its versions 2 and 3 become **derived**
    versions, not re-seeds. **Red:** under the new resolver, the unchanged test re-seeds v3,
    so `@3` against `seed` resolves to v3 itself and gives 0 changed cells, not 2. Quote that
    red after the resolver change and before the rewrite.
15. **Every other `against=seed` test is read and kept or updated** (`RL-1375` DP-1 item 4).
    Run `grep -n '"against": "seed"' backend/tests/test_api_rate_tables.py` and
    `grep -n 'against="seed"' backend/tests/test_rate_tables_service.py`. At `1dd5e264` they
    print `:258`, `:491` and `:638`, and `:556`. Read each test's seed calls. Only `:258`
    re-seeds (item 14). `:491` (a direct-insert table with no seed, 404 `RATE_TABLE_MISS`
    "No seed origin") is **kept as it is**. The ledger quotes both greps and gives one line
    per hit: kept, or updated and why.

## Global Constraints

- **Spec text only where a ruling carries it verbatim** (the maintainer's rule (iv)).
  `RL-1361`'s texts are applied byte for byte. Any spec or contract wording that `RL-1361`
  does not carry is a decision point (below). The executor never writes it. If a find string
  is not found exactly once, the executor stops and reports to the lead (`RL-1361`, "The
  exact texts", last paragraph).
- **One commit for spec, code, tests and contracts** (`CLAUDE.md` §2). Contracts are
  regenerated, never hand-edited (`docs/contracts/openapi/generated.json`,
  `docs/contracts/schemas/generated/`). `gi-pricing.yaml` is the hand-authored stub and
  takes `T8` only.
- **No shape is hand-written twice** (`CLAUDE.md` §2). The request and the response are
  `model-schema` classes. The test reads the generated contract and never restates a shape.
- **`pricing-core` takes no database** (ADR-703; `CLAUDE.md` §2). Factor loading is the
  platform's (`RL-1361` section D).
- **No migration** (`RL-1361` section A, "No migration"; FR-4). Existing versions stay
  unbound.
- **Money and values are decimal strings** (R2). Seeded values keep
  `str(Decimal(str(relativity)))`, as now.
- **`WF-699` A1 (`T12`) is not this slice's.** A decision-maker applies it in its own PR
  after this slice merges (`RL-1361` T12).
- **FD-1358 is out of this slice.** Its owner is WK-673, and its fix is undecided
  (`RL-1361` section F). This slice changes no diff output: no change to `RateTableDiff`, to
  the diff computation or to any diff route's shape. It changes only which version the
  `against=seed` baseline is (`RL-1375` DP-1 item 4). `T3`, `T6`, `T10` and `T11` are WK-673
  Slice 7's.

## Scope

### Requirement coverage, each id individually

| Id | Where | This slice |
|---|---|---|
| FR-228 | `03` §3.3, `:119` | `factor_ref` on `RateTableKey`, at most one binding; `T1` if first (DP-5) |
| FR-229 | `03` §3.3, `:120` | `change_note` stays required and non-empty in the typed request |
| FR-230 | `03` §3.3, `:121` | one table per Factor; a re-seed's own seed origin; `T2`, `T4`, `T7`, `T8`, `T9`, `T-A`, `T-B` |
| FR-234 | `03` §3.3, `:125` | a row lacking a declared key is a named refusal (DP-6) |
| FR-451 | `07` §3.9, `:182` | contracts regenerated; the typed request and 201 published |
| FR-4 | `00`, `:209` | existing versions stay unbound, with no migration |

`FR-231` is **not** covered (FD-1358, `RL-1361` section F; WK-673 Slice 7).

### Premises, read at `1dd5e264`

| | Premise | Locator and command | Result |
|---|---|---|---|
| a | The pure seed declares one key per factor, while a row carries only its own factor's key | `packages/pricing-core/src/pricing_core/rate_tables/operations.py:142-157` (`extract_relativity_table`), `:191-194` (keys), `:289` (`row[key]`) | reproduces FD-1357 |
| b | The route body is `dict[str, Any]`, parsed by `_seed_body`, and returns `version.model_dump(mode="json")` | `backend/src/app/api/rate_tables.py:57-95`, `:118-145` | reproduces |
| c | The platform seed appends to an existing lineage and sets `seeded_from` on every seed | `backend/src/app/platform/rate_tables.py:95-173` (`:133-150` lineage, `:162` `seeded_from`) | reproduces; `03:334-335` is wrong here (`RL-1375` DP-1 item 3) |
| d | No frontend caller | `grep -rn "seed-from-model\|seedFromModel" frontend/src --include=*.ts --include=*.vue \| grep -v generated` | prints nothing |
| e | Seed call sites | `grep -c "seed_from_model\|seed-from-model\|_seed_body(" backend/tests/test_api_rate_tables.py backend/tests/test_rate_tables_service.py packages/pricing-core/tests/test_rate_table_operations.py` | 39, 1 and 3 lines |
| f | `RateTableKey` is `extra="forbid"`, with `name`, `type` and `banding_ref` only | `packages/model-schema/src/model_schema/rating.py:662-669` | reproduces |
| g | Neither `RateTableVersion` nor a seed request is published under `generated/` | `ls docs/contracts/schemas/generated/` (33 files); `scripts/generate-contracts.py` `GENERATED_SHAPES` | reproduces |
| h | The authored `rate-table.schema.json` is never compared | `backend/tests/test_contracts.py`, `ONE_SIDED_SLUGS["rate-table"]` = "shipped in model-schema, never compared — register F27" | reproduces (DP-4) |
| i | Every `RL-1361` find string this slice applies occurs exactly once | `grep -cF -- '<find>' docs/specs/03-rating-engine.md` per text: FR-228 `:119`, FR-230 `:121`, §4.2 `:292`, `:296-298`, `:310`, §5.1 `:786`, §5.2 `:976-977`; `gi-pricing.yaml:238` | each prints 1 |
| j | `load_factors(session, *, workspace_id, factor_ids)` exists and also loads interaction operands | `backend/src/app/platform/modelling.py:284` | reproduces |
| k | `Factor` carries `slug` and `version` | `packages/model-schema/src/model_schema/modelling.py:122-135` | reproduces |
| l | The existing test models pin no Factors (`GlmSpec` default `factors=()`), so after the fix each must pin Factor rows | `backend/tests/test_api_rate_tables.py:61-69`, `:114-131` | reproduces |
| m | `_resolve_baseline`'s seed branch takes the lowest-numbered version with any `seeded_from`, so after a re-seed `against=seed` still answers the first seed | `backend/src/app/platform/rate_tables.py:433-453` (`.order_by(RateTableVersionRow.version_number).limit(1)` over `seeded_from.is_not(None)`); pinned by `test_api_rate_tables.py:224-262` | reproduces; wrong under `RL-1375` DP-1 item 3, changed by Acceptance 13 |

Task 0 re-reads every premise at the activation SHA. A premise that no longer holds is a stop.

### Spec texts this slice applies

The `[seeding]` texts are applied in this slice's commit, and `T1` and `T5` too if this slice
lands `factor_ref` first (DP-5). Each is applied verbatim from
[`RL-1361`](../rulings/RL-01361-pl-1267-dp-5-decided-a-seeded-rate-table-holds-one-factor-and-a-named-portfolio-joins-each-key-through-its-bound-factor-its-declared-banding-or-its-same-named-column.md)
"The exact texts". The executor copies them from the ruling file, never from this plan.

| Text | File and place | Condition |
|---|---|---|
| T1 | `03` FR-228 row, appended | if this slice lands `factor_ref` first (DP-5); `<first date>` = fix date |
| T2 | `03` FR-230 row, appended | always; `<fix date>` |
| T4 | `03` §4.2 JSON block, four lines replaced | always |
| T5 | `03` §4.2, blockquote inserted after the "Values are stored as decimal strings" line | with T1 |
| T7 | `03` §5.1 seed row, replaced | always; `<fix date>` |
| T8 | `docs/contracts/openapi/gi-pricing.yaml:238`, replaced | always |
| T9 | `03` §5.2 signature, replaced | always; `<fix date>` |
| T-A | `03` §4.2, the first two lines of the "Seed lineage survives every derivation" blockquote (`:334-335`), replaced (`RL-1375` DP-1) | always; `<fix date>`, `<RL id>` |
| T-B | `03` §4.2, a blockquote paragraph inserted after the blockquote's last line, "`created_by_import` remain mutually exclusive." (`:343`) (`RL-1375` DP-2) | always; `<fix date>`, `<RL id>` |

If WK-673 Slice 7 lands `factor_ref` first, it applies `T1` and `T5`, and this slice cites
them and does not re-apply them. `T-A` and `T-B` are applied verbatim from
[`RL-1375`](../rulings/RL-01375-pl-1376-dp-1-to-4-decided-a-re-seed-starts-its-own-seed-origin-an-unbound-lineage-takes-a-seed-only-through-its-one-same-named-key-and-the-seed-request-and-201-are-generated-model-schema-shapes.md) (draft PR #1065) at
`23ff15d1`, its "Spec texts this ruling carries", never from this plan. `RL-1375` is not
minted yet. At dispatch the executor re-copies both texts from the minted ruling file on main,
and any difference from `23ff15d1` is reported in the ledger.

**Dispatch hint.** `RL-1361` `T7` cites the §5.1 seed row at `:783` (read at `101e32dc`). At
`1dd5e264` it is at `:786`. The find-once rule covers this: the executor matches the bytes,
not the line number.

### Out of scope

- FD-1358 (per-cell weight in the diff output; owner WK-673). Its fix is not decided
  (`RL-1361` section F). This slice touches no diff output, only which version the
  `against=seed` baseline is (`RL-1375` DP-1).
- FR-231's weighting (`T3`, `T6`, `T10`, `T11`; WK-673 Slice 7).
- `WF-699` A1 (`T12`; a decision-maker, after this merges).
- The other four `FD-1366` routes (its Part B).
- The authored `rate-table.schema.json` (F27(c), the create-read-retire audit Work), unless
  DP-4 is ruled otherwise.

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocking | Resolver |
|---|---|---|---|---|---|---|
| DP-1 | `03:334-335` says `seeded_from` is set "only by seed-from-model, on the first version of a lineage". The code sets it on every seed, including a seed appended to an existing lineage (`platform/rate_tables.py:162`). The diff baseline is a separate matter: `_resolve_baseline(..., against="seed")` (`platform/rate_tables.py:433-453`) picks the **lowest-numbered** version with any `seeded_from` set, which is the first seed, and `test_api_rate_tables.py:224-262` asserts v3-vs-v1 after three seeds. `RL-1361` "What it obliges" says the fix must settle which statement is right. This is a spec-versus-code conflict (`CLAUDE.md` §0) | **(a1) First-seed baseline; the code is right.** A re-seed records its own `seeded_from` (the new model), and `against=seed` still resolves to the first seeded version. Code: none. Diff: no change, and `:224-262` stays green. **(a2) A re-seed starts its own seed origin.** `against=seed` on version N resolves to **the lowest-numbered version of the table whose `seeded_from` equals N's** (the whole stored value, `model_ref` and `seeded_at`). Derived versions carry their baseline's `seeded_from` exactly (the FR-234 guard, `_guard_seed_lineage`), so this is the version that created N's anchor. Code: `_resolve_baseline`'s seed branch changes; `:224-262` is rewritten with derived versions; no cache change, because the cache key hashes the resolved baseline's cells (`RL-1375` DP-1 item 6). Diff: `RateTableDiff`, the diff computation and every diff route's shape are unchanged; only the baseline version moves. Serialises with WK-673 Slice 7 on the file, not the function. **(b) The spec is right.** A re-seed inherits the first version's `seeded_from`, and the platform seed changes (`:162`). Diff: no change. The re-seeded version no longer records the model it came from | **Decided (a2)** by `RL-1375`: the spec was wrong at `03:334-335`; the write path (`:162`) was right; the resolver (`:433-453`) and its test (`:224-262`) were wrong (`RL-1375` DP-1 item 3) | decision-maker (`dm-1357`) | yes | `RL-1375` |
| DP-2 | A re-seed into an existing lineage whose current version's key is **unbound** (a table seeded before `factor_ref`, or a hand-authored table, perhaps with several keys). `RL-1361` section A rules only "the slug the lineage's key is bound to" | (a) Accept when the current version has exactly one key, the key has no `factor_ref` and no `banding_ref`, and its name equals the named Factor's slug (every pre-fix seed named its key after the slug, `operations.py:191-194`). Otherwise refuse 422 by name. (b) Refuse every unbound lineage, so the caller must seed a new table slug. (c) Accept any unbound lineage | **(a).** `RL-1361` "What it obliges" says a table seeded before `factor_ref` "must be re-seeded to be weighted through a Factor". (a) lets that re-seed keep its lineage and its diff-vs-previous. (b) breaks it, and (c) lets a vehicle × area table take a one-key seed. Any spec sentence for (a) is the decision-maker's exact text, or the ruling says that `T2` and `T7` suffice | decision-maker | **yes** (Acceptance 3(e) and the lineage check) | `RL-1375`: (a), made total; the full refusal set is Acceptance 3(e), the accepted shapes 3(e′); text `T-B` |
| DP-3 | The typed request. The maintainer's rule (i) decides that it is typed. `T7` fixes the fields `{"model_ref", "factor", "change_note"}`. `RL-1361` says "Whether the body gains a typed `model-schema` shape is not decided by this ruling", and it carries no text naming the shape | (a) `SeedFromModelRequest` in `model_schema/rating.py`: `model_ref: ArtifactRef` (an `after` validator refuses a type other than `model`), `factor: str` (non-empty), `change_note: str` (stripped and non-empty, FR-229), with `extra="forbid"`. No spec text: `T7`'s row states the body, and `generated/seed-from-model-request.schema.json` is the shape's written form. (b) As (a), plus a `03` §4.2 note naming the shape, in the decision-maker's exact text. (c) As (a), but `extra="ignore"`, so unknown fields keep being accepted | **(a).** `extra="forbid"` is the `model-schema` convention (`RateTableKey`, `rating.py:665`), and the break is already marked. The sub-graph request shapes were published with no spec note (`generate-contracts.py`, the `sub-graph-create` comment). (b) is acceptable if the decision-maker supplies the text | decision-maker | **yes** (Acceptance 6 and the schema slug) | `RL-1375`: (a); exactly three fields, `extra="forbid"`, today's two refusal messages, no `rateable` field, no spec text |
| DP-4 | Under which generated slug the 201's `RateTableVersion` is published, and whether the authored `docs/contracts/schemas/rate-table.schema.json` gains `factor_ref` | (a) A new generated-only slug `rate-table-version`, declared in `ONE_SIDED_SLUGS` with the reason "first written form of the route's 201; the authored rate-table contract is F27(c)'s, never compared". The authored file is not edited, and the ledger records the new divergence (`factor_ref`) for F27(c)'s owner. (b) The slug `rate-table`, which pairs it with the authored file and forces the comparison walkers over F27's seven known divergences. (c) No generated file, only the OpenAPI component | **(a).** (b) is F27(c)'s Work, which is a separate audit, and it would grow this slice by a contract reconciliation. (c) fails the maintainer's rule (ii), "a `$ref` into `docs/contracts/schemas/generated/`". The reason string is a code comment, not spec text | decision-maker | **yes** (Acceptance 7 and `ONE_SIDED_SLUGS`) | `RL-1375`: (a), for both shapes; the two `ONE_SIDED_SLUGS` reason strings are its text; `response_model=RateTableVersion` |
| DP-5 | Does this slice land `factor_ref` (and so `T1` and `T5`), or does WK-673 Slice 7? `RL-1361`: "Which comes first is the lead's to order" | (a) This slice lands it, with `T1` and `T5`. (b) Slice 7 lands it first, and this slice waits for it | **(a).** The lane B order (the maintainer, about 10:10 BST) puts this fix ahead of every WK-673 slice, and seeding cannot set a field that does not exist | lead | yes (the dispatch record states it) | **Decided (a)**: the lead's verdict, accepted by the maintainer, to-lead.md entry headed "2026-10-01 10:24:27 BST — The clock correction acknowledged (my own approximate references noted too); #1057 FD-1357 fix plan: audit + DM in PARALLEL approved, with conditions", item (4); its condition (4) wording ("VALIDATION_FAILED for the KeyError hardening must be an existing code in 03's owned-codes table") was corrected by the entry headed "2026-10-01 10:38:30 BST — Mint order: (X) APPROVED: #1058 mints first (PL-1368 + SL-1369), SL-1360 takes the next LG at its own mint; my #1057 condition (4) corrected; #1065 noted": `VALIDATION_FAILED` is a generic code (`errors.py:382-385`), not owned by `03`, and using the existing code is right. The corrected text binds |
| DP-6 | Is the FD-1357 *Disposition*'s hardening in this slice (Acceptance 8), and with which code? | (a) In: `validate_rate_table`, `_value_issue` and `_index_rows` raise a `ValueError` naming the missing key, which `_map_operation_error` maps to 422 `VALIDATION_FAILED` (`platform/rate_tables.py:92`). The message must **not** begin with an `UPPER_SNAKE: ` prefix, because `_map_operation_error` (`:84-92`) turns any such prefix into a new error code. No new code name and no spec text. (b) In, with a new named code, which needs the decision-maker's `03` §5.2 text. (c) Out, as a follow-up | **(a).** The *Disposition* names it ("never a `KeyError`"). (a) adds no code name, so it needs no spec text under rule (iv) | lead (scope); decision-maker only if (b) | no (Acceptance 8 drops if (c)) | **Decided (a)**: in, with `VALIDATION_FAILED`, a generic code (`backend/src/app/errors.py:382-385`); the lead's verdict, accepted by the maintainer, to-lead.md entry headed "2026-10-01 10:24:27 BST — The clock correction acknowledged (my own approximate references noted too); #1057 FD-1357 fix plan: audit + DM in PARALLEL approved, with conditions", item (4); its condition (4) wording ("VALIDATION_FAILED for the KeyError hardening must be an existing code in 03's owned-codes table") was corrected by the entry headed "2026-10-01 10:38:30 BST — Mint order: (X) APPROVED: #1058 mints first (PL-1368 + SL-1369), SL-1360 takes the next LG at its own mint; my #1057 condition (4) corrected; #1065 noted": `VALIDATION_FAILED` is a generic code (`errors.py:382-385`), not owned by `03`, and using the existing code is right. The corrected text binds |

**FD-1358 is out** (not a decision point). `RL-1361` section F rules that the per-cell weight
in the diff output predates the ruling, is owned by WK-673, and has no decided fix. This slice
changes neither `RateTableDiff`, the diff computation, nor any diff route's shape. It changes
only which version the `against=seed` baseline is (`RL-1375` DP-1 item 7: FD-1358 weights the
resolved pair, and (a2) only chooses the pair).

## Write set, and its serialisation (`RL-1263`)

| Path | Change | Shared with | Serialisation |
|---|---|---|---|
| `packages/model-schema/src/model_schema/rating.py` | `RateTableKey.factor_ref` and its validator (existing class); new `SeedFromModelRequest` | WK-673 Slice 7 (`RateTableKey`, `RateTableDiff`); WK-674 S2 / `PL 9765` (working id) if it edits this file | serialises with Slice 7 (same class): this slice first, under DP-5. Against `PL 9765`: the dispatch record names the path and checks that no existing definition is edited by both |
| `packages/model-schema/src/model_schema/__init__.py` | **two** exports appended, each with its `__all__` entry: `RateTableVersion` and `SeedFromModelRequest`. `RateTableVersion` is not exported at `1dd5e264` (`grep -n RateTable packages/model-schema/src/model_schema/__init__.py` prints nothing). `generate-contracts.py` resolves each slug with `getattr(model_schema, name)` (`build_schemas`), so both must be exported | WK-674 S2 / `PL 9765`, WK-1250 (`PL-1306:503`; `PL-1278:178-179`) | not on the registry list: serialises unless the dispatch record names the path (append-only `__all__` entries, with no existing definition edited) |
| `packages/pricing-core/src/pricing_core/rate_tables/operations.py` | `seed_from_model`, `extract_relativity_table`, `_key_domains_of`, `validate_rate_table`, `_value_issue`, `_index_rows` | WK-673 Slice 7 (the diff functions take `weights`) | serialises with Slice 7 |
| `backend/src/app/platform/rate_tables.py` | `seed_from_model` (Factor loading, the lineage check); `_resolve_baseline`'s seed branch (`RL-1375` DP-1 item 2) | WK-673 Slice 7 (`diff`), the FD-1356 fix if it touches it | serialises with Slice 7 |
| `backend/src/app/api/rate_tables.py` | the seed handler typed; `_seed_body` removed | WK-675 S4 and S5 (`PL-1286`), Slice 7 (the diff route) | the FD-1366 hold, rule (i): a WK-675 slice that calls this route waits for this slice's merge. Serialises with Slice 7 |
| `scripts/generate-contracts.py` | two `GENERATED_SHAPES` entries appended (DP-4) | WK-674 S2 / `PL 9765`, WK-1250 S2 and S3 | not on the registry list: serialises unless the dispatch record names the path |
| `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/` | regenerated | everyone | registry-exempt: regenerated at the second merge, never hand-merged |
| `docs/contracts/openapi/gi-pricing.yaml` | `T8` (one line) | any slice editing the stub | hand-authored and **not** exempt: serialises |
| `docs/specs/03-rating-engine.md` | FR-228 row (`T1`), FR-230 row (`T2`), §4.2 block and note (`T4`, `T5`), §5.1 seed row (`T7`), §5.2 signature (`T9`), and DP-1's or DP-2's text if ruled | WK-674 S2 (§4 new subsection, one §5.1 row appended, `PL-1306:494-496`); WK-1250 S2 and S3 (§4.11, §5.1 rows); Slice 7 (`T3`, `T6`, `T10`, `T11`) | row-disjoint from WK-674 S2 and WK-1250 (different rows; the dispatch record checks both diffs). §4.2's block is shared with Slice 7 (`T6` edits the same JSON block): this slice first |
| `backend/tests/test_contracts.py` | two `ONE_SIDED_SLUGS` entries (DP-4); in Case B, two guard entries removed | `PL-1364` (it creates the guard lists), WK-674 S2, WK-1250, PL-1267 Slice 1 (`ONE_SIDED_SLUGS["dislocation-run"]`) | `ONE_SIDED_SLUGS` is an existing definition: serialises with each. `PL-1364` comes after this slice in lane B, and the second to merge re-gates (holds register) |
| `packages/model-schema/tests/test_rate_tables.py` | Acceptance 5 appended | none found | — |
| `packages/pricing-core/tests/test_rate_table_operations.py` | Acceptance 2, 3, 8 appended; the `seed_from_model` calls and `_glm_model` updated | Slice 7 | serialises with Slice 7 |
| `backend/tests/test_api_rate_tables.py` | Acceptance 1, 3, 4, 6, 7 and 13 appended; `test_diff_vs_seed_compares_against_the_origin_not_the_previous_version` rewritten with derived versions (Acceptance 14); `_seed_approved_model`, `_seed_body` and every seed call updated (Factor rows pinned) | Slice 7 | serialises with Slice 7 |
| `backend/tests/test_rate_tables_service.py` | its `_seed_approved_model` and `_seed` updated | Slice 7 | as above |
| `scripts/audit-docs.py` | `_CONTRACT_ARTIFACT_PATHS` (`:2620`), the generated block (about `:2640-2667`): the two literal paths `docs/contracts/schemas/generated/rate-table-version.schema.json` and `docs/contracts/schemas/generated/seed-from-model-request.schema.json` registered | WK-674 S2 / `PL 9765` (it adds about ten generated schemas), any slice adding a generated schema | shared under `RL-1263` (`:89`): a tuple entry is an edit to an existing definition. Serialises: the **second** of this slice and `PL 9765` to merge re-applies its entries on the merged tuple and re-gates |
| `tests/test_audit_docs_ids.py` | the count assertion at `:2117` (in `test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts`, `:2072`) goes from `== N` to `== N+2`, where N is the base's count (70 at `92b4e4ac`), with a dated comment line in the existing pattern (`RL-1375` as amended at `23ff15d1`). The ledger records N as measured, with the base SHA | WK-674 S2 / `PL 9765`, any slice adding a generated schema | a count bump is not append-only. The **second** of the two slices to merge re-bumps on the merged count (70 + both slices' additions) and re-gates |
| `.claude/skills/contract-schema/SKILL.md` | **conditional:** whichever of this slice and `PL 9765` merges **first** writes the step "a new generated schema → register its literal path in `scripts/audit-docs.py` `_CONTRACT_ARTIFACT_PATHS` and bump `tests/test_audit_docs_ids.py`'s count", with a `Verified` date and tree (`CLAUDE.md` §12), plus a pointer from `.claude/skills/docs-audit/SKILL.md`'s check-35 text if that text names the register | `PL 9765` | the second slice to merge does not write it again; it checks that the step is there |
| `docs/ledgers/LG-<id>-….md`, `docs/INDEX.md` | the ledger; the index regenerated | — | `INDEX.md` is registry-exempt |

**Lane B order** (the maintainer, about 10:10 BST): `SL-1360` → **this slice** → the
FD-1356 fix → the RL-1343 decimal-output fix → `PL-1364`. All are WK-1178 slices, so they run
one after another in any case (`RL-1263`: concurrent build slices only from different Works).
On lane A, WK-674 S2 (`PL 9765`) may run at the same time. The shared non-registry paths
above (`__init__.py`, `generate-contracts.py`, `test_contracts.py`, `03`) are named in the
dispatch record with the check that no existing definition is edited by both, or the second
slice waits.

**Holds** (`~/gi-pricing-plan.local/handover/holds-2026-10-01.md`):
- The **FD-1366 per-route hold, rule (ii)**: this slice **edits** the seed-from-model handler,
  so it types the body in the same slice (Acceptance 6). Its dispatch record states "case
  (ii)".
- This slice's merge **lifts rule (i)** for `POST /rate-tables/{slug}/seed-from-model`. A
  WK-675 slice that calls that route may then be dispatched.

## Activation needs, in order

1. `SL-1360` has merged on main. Run `git log --oneline origin/main | grep -m1 "SL-1360"`.
2. `RL-1375` (DP-1 to DP-4) is minted on main. A ruling that
   carries spec or contract text carries it verbatim. Check with `doc-id.py` and `grep` for
   each ruling id.
3. DP-5 (a) and DP-6 (a) are decided (the lead's verdicts, accepted by the maintainer, to-lead.md entry headed "2026-10-01 10:24:27 BST — The clock correction acknowledged (my own approximate references noted too); #1057 FD-1357 fix plan: audit + DM in PARALLEL approved, with conditions", item (4); its condition (4) wording ("VALIDATION_FAILED for the KeyError hardening must be an existing code in 03's owned-codes table") was corrected by the entry headed "2026-10-01 10:38:30 BST — Mint order: (X) APPROVED: #1058 mints first (PL-1368 + SL-1369), SL-1360 takes the next LG at its own mint; my #1057 condition (4) corrected; #1065 noted": `VALIDATION_FAILED` is a generic code (`errors.py:382-385`), not owned by `03`, and using the existing code is right. The corrected text binds). The dispatch record cites that entry.
4. This plan and `SL-1377` are minted, and the working ids are re-pointed.
5. Task 0's premises (a)–(m) re-read at the activation SHA, each holding. Every `RL-1361`
   find string still occurs exactly once. A changed line number is fine; a changed count is
   a stop.
6. `PL-1364`'s status is read at the activation SHA. The dispatch record states which case
   of Acceptance 10 applies.
7. **The maintainer's agreement and the lead's go**, in a **separate activation PR** that
   sets this plan `active` and `SL-1377` `active`.

## Tasks

### Task 0: Preconditions (no code)

- [ ] `uv sync --all-packages` in the executor's worktree (`dev-commands`).
- [ ] Re-run premises (a)–(m) at the activation SHA, and quote each output in the ledger.
- [ ] Read each ruling for DP-1 to DP-4 to the clause. Copy each exact text it carries into
  the ledger's text table, with its source line.
- [ ] State the Acceptance 10 case (A or B) and the DP-5 outcome.

### Task 1: model-schema — `factor_ref` and the typed request (Acceptance 5, and the shape for 6)

- [ ] Append Acceptance 5's test (`@pytest.mark.req("FR-228")`) to
  `packages/model-schema/tests/test_rate_tables.py`. Run it, and quote the red (the
  only-`factor_ref` key refused as an extra field).
- [ ] Add `factor_ref: ArtifactRef | None = None` to `RateTableKey`, with a
  `model_validator(mode="after")` that refuses a key carrying both, and a `factor_ref` whose
  type is not `factor`. Update the class docstring to cite `RL-1361`.
- [ ] Append the `SeedFromModelRequest` tests (per DP-3's ruling: a valid body, a missing
  `factor`, a blank `change_note`, a non-model `model_ref`, and an unknown field if
  `extra="forbid"`). Run them red (`ImportError`), then add the class.
- [ ] Export **both** `SeedFromModelRequest` and `RateTableVersion` from
  `model_schema/__init__.py`: the import line and the `__all__` entry for each.
  `generate-contracts.py` reads each slug's class with `getattr(model_schema, name)`, so a
  missing export fails generation. Neither is exported at `1dd5e264`.
- [ ] Run the model-schema tests green.

### Task 2: pricing-core — one table per Factor, and the hardening (Acceptance 2, 3(a)–(d), 8)

- [ ] Append the pure tests (`@pytest.mark.req("FR-230")`, with `FR-228` on Acceptance 2 and
  `FR-234` on Acceptance 8). Include an interaction entry, which seeds one table whose levels
  are the crossed labels (`RL-1361` section A). Run them, and quote each red.
- [ ] Change `seed_from_model` to `T9`'s signature. Select the relativity entry named by
  `factor` (refuse with `ValueError` naming the factor if it is absent). Take the passed
  Factor whose slug equals `factor` (refuse if there are none or several). Build one key:
  `RateTableKey(name=factor, type=STRING, factor_ref=ArtifactRef(type="factor", slug=f.slug, version=f.version))`.
  The domain and cells come from that entry alone.
- [ ] Hardening (DP-6 (a)): in `validate_rate_table`, `_value_issue` and `_index_rows`, a row
  missing a declared key raises `ValueError` naming the key and the row index. It never
  raises `KeyError`. The message starts with lower-case prose (for example
  `"row 1 lacks declared key 'region'"`), never with an `UPPER_SNAKE: ` prefix, because
  `_map_operation_error` (`platform/rate_tables.py:84-92`) would read that prefix as a new
  code. Acceptance 8's route-level assertion is `code == "VALIDATION_FAILED"`.
- [ ] Update the existing pure tests' `seed_from_model` calls (premise e) to pass `factor` and
  `factors`. Run the module green.

### Task 3: platform and route — loading, lineage, resolver, typing (Acceptance 1, 3(e)–(f), 4, 6, 7, 11, 13–15)

- [ ] Update the backend fixtures. `_seed_approved_model` (both test modules) inserts a
  Factor row per relativity entry and pins the ids in `GlmSpec.factors`. `_seed_body` gains
  `factor`. Update every seed call (premise e).
- [ ] Append the route tests (Acceptance 1, 3(e), 3(f), 4, 6, 7). Run them against the
  unmodified `src/`, and quote each red. Acceptance 1's red is the 500 with `KeyError`.
- [ ] **Refusal order (a plan choice).** The platform checks approval **before** it loads
  Factors: `load_model` → `to_model` → `check_model_approved` (imported from pricing-core) →
  `load_factors` → the pure seed. So a non-approved model with a dangling Factor id gives
  **422 `PIN_NOT_APPROVED`**, not 404. The reasons:
  - FR-230 seeds only approved models, so approval is the route's first precondition.
  - A caller learns nothing about an ungoverned model's Factors.
  - `test_seed_refuses_a_non_approved_model` (`:293-319`) keeps asserting
    `PIN_NOT_APPROVED` without pinning Factor rows.

  A route test pins this order: a `fitted` model whose `spec.factors` holds an id that
  resolves nowhere gives 422 `PIN_NOT_APPROVED`. **Red:** on `1dd5e264` this test is green
  for the wrong reason (nothing loads Factors), so its red is shown on broken input. With
  `load_factors` moved before the approval check, the route answers 404 and the test
  fails. The pure function keeps its own `check_model_approved` call (defence in depth).
- [ ] Platform `seed_from_model` gains `factor: str`. It calls `load_factors(session,
  workspace_id=workspace_id, factor_ids=list(model.spec.factors))` and passes `factor` and
  the Factors to the pure function. If the lineage exists, it reads the current version's
  keys and applies `RL-1375` DP-2's rule: accepted only when the current version has exactly
  one key, and that key either has a `factor_ref` naming the same slug (any version) or has
  neither ref and is named after the slug. Anything else is refused 422 `VALIDATION_FAILED`
  via `PlatformError("VALIDATION_FAILED", …, 422, detail)`, the detail naming the table slug
  and the key names. `seeded_from` stays as it is written today (`:162`, `RL-1375` DP-1 item 1).
- [ ] The route: `body: SeedFromModelRequest`, `_seed_body` deleted, and
  `response_model=RateTableVersion` with `responses=problems(401, 403, 404, 409, 422)`. The
  handler returns the `RateTableVersion` instance (`RL-1375` DP-4; the precedent is
  `sub_graphs.py:42`). The docstring names the body and the refusals. After regeneration,
  check that the 201 `$ref` names `RateTableVersion` exactly. A suffixed name (for example
  `RateTableVersion-Output`) is a **stop** (Acceptance 7).
- [ ] **The resolver (`RL-1375` DP-1 item 2).** First write Acceptance 13 and run it against
  the unmodified `src/` (red: `@4` resolves to v1). Then change `_resolve_baseline`'s seed
  branch: read version N's `seeded_from`; if it is null, keep the existing 404
  `RATE_TABLE_MISS` "No seed origin"; otherwise select the lowest `version_number` of the same
  table whose `seeded_from` equals it. Run the unchanged origin test and quote its red
  (Acceptance 14: 0 changed cells, not 2). Then rewrite that test with derived v2 and v3,
  keeping its name and assertions. Then run the Acceptance 15 sweep. The diff cache is not
  touched (`RL-1375` DP-1 item 6).
- [ ] Append the two `GENERATED_SHAPES` entries and the two `ONE_SIDED_SLUGS` entries, the
  reason strings copied verbatim from `RL-1375` DP-4 with `<RL id>` filled. Run
  `uv run python scripts/generate-contracts.py`, then `--check` (exit 0).
- [ ] Register the two generated schema paths in `scripts/audit-docs.py`'s
  `_CONTRACT_ARTIFACT_PATHS` (the generated block). Then change the count assertion at
  `tests/test_audit_docs_ids.py:2117` from `== N` to `== N+2`, where N is the base's count,
  with a dated comment line in the file's pattern (`RL-1375` as amended at `23ff15d1`). First
  run the test at `:2072` on the base and record N and the base SHA in the ledger (N is 70
  at `92b4e4ac`). A base where N is not 70 (for example because WK-674 S2 merged first) is
  **not** a stop. The executor stops if the unmodified test at `:2072` **fails on the
  base**. Run
  `uv run pytest -q tests/test_audit_docs_ids.py` and `python3 scripts/audit-docs.py`.
- [ ] **Conditional, if this slice merges before `PL 9765`:** add the step to
  `.claude/skills/contract-schema/SKILL.md` ("a new generated schema → register its literal
  path in `scripts/audit-docs.py` `_CONTRACT_ARTIFACT_PATHS` and bump
  `tests/test_audit_docs_ids.py`'s count"), with a `Verified` date and tree. Add a pointer from
  `.claude/skills/docs-audit/SKILL.md`'s check-35 text if that text names the register. If
  `PL 9765` merged first, check that the step is there and say so in the ledger.
- [ ] Case B only: remove the seed-from-model entries from `UNTYPED_REQUEST_PENDING` and
  `UNTYPED_2XX_PENDING_PART_B`, after quoting the guard's red with them still listed.
- [ ] Run the rate-table, contract and model-schema tests green.

### Task 4: The spec texts (Acceptance 9)

- [ ] Run the Acceptance 9 count script before the edit (red), and quote it.
- [ ] Apply `T2`, `T4`, `T7`, `T8` and `T9`, plus `T1` and `T5` under DP-5 (a), from
  `RL-1361`; and `T-A` and `T-B` from `RL-1375`; each verbatim from its ruling file. Fill
  `<fix date>` and `<first date>` with the commit date, and `<RL id>` with `RL-1375`'s minted
  id. Change nothing else.
- [ ] Re-run the script (green), and quote it. Then run `python3 scripts/audit-docs.py`.

### Task 5: The gate and the ledger (Acceptance 12)

- [ ] Run the full two-half gate on the final tree. Announce it to the team first
  (`delivery-process.md` §8). Quote each exit code with the commit SHA and the tree.
- [ ] One commit, Conventional Commits:
  `feat(rating)!: SL-<id> — FD-1357's fix: one seeded table per Factor (RL-1361), typed seed request and 201`.
  Its body carries a `BREAKING CHANGE:` footer (`RL-1375` DP-3). It says that the seed body
  now requires `factor`, and that any unknown field, `rateable` included, is now refused 422
  with a field error where it was silently ignored.
- [ ] The ledger records: each red and green, the Acceptance 10 case, the DP resolvers, the
  F27(c) divergence note (DP-4 (a)), and the hand-off below.

## Hand-off

- **To a decision-maker, after the merge:** `RL-1361` `T12` (`WF-699` A1), with `<WF date>`.
- **To the lead:** in Case A, `PL-1364`'s dispatch record drops the seed-from-model request
  entry and its 201 entry. The FD-1366 hold, rule (i), lifts for seed-from-model. FD-1357's
  *Event* is met at the merge (the auditor's to close).
- **To WK-673 Slice 7:** `factor_ref` exists, and `T1` and `T5` are applied (DP-5 (a)). Slice 7
  cites them and applies `T3`, `T6`, `T10` and `T11`.
- **To the exit-demo slice** (holds register, "Saturday lane-loading plan" item (a)): multi-factor
  seeding works, so A1–A2 can be scripted on the seven-factor GLM, with one request per
  categorical Factor.

## Self-review

- **Spec coverage.** Every `[seeding]` text of `RL-1361` (`T2`, `T4`, `T7`, `T8`, `T9`) is
  in a task, and `T1` and `T5` are conditional on DP-5. `T12` is handed off. Every
  acceptance case in `RL-1361` that is about seeding (the two-factor red, the refusals, the
  newer-version re-seed, `factor_ref` with `banding_ref` refused) is an acceptance item
  here. The weighting cases are Slice 7's. Each obligation in `RL-1375`'s "What it obliges"
  and its "Acceptance" is an item: the resolver (13), the rewritten test (14), the sweep (15),
  DP-2's refusals and acceptances (3(e), 3(e′)), and the typed request and 201 (6, 6b, 7).
- **No executor wording.** Every spec and contract sentence comes from `RL-1361` or from
  `RL-1375`. DP-1 to DP-4 existed because `RL-1361` carries no text for them.
- **Red first.** Each of the 15 items names its red. Acceptance 5 guards against a vacuous red.
- **Placeholders.** None, except `RL-1361`'s own date placeholders, the `SL-<id>` and
  `LG-<id>` mint values, and the slug names that depend on DP-4.
