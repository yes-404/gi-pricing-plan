---
id: PL-9764
family: plan
kind: leaf
title: WK-1178 slice — FD-1357's fix, multi-factor seeding per RL-1361 (one table per Factor, factor_ref), with the seed route's request and 201 typed (FR-228, FR-230, FR-234, FR-451): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-01
owner: planner
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-1178
slice: SL-9763
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1357, RL-1361, FD-1358, PL-1267, RL-1263, PL-1359, SL-1360, PL-1306, ADR-704]
---

# PL-9764 — WK-1178 slice — FD-1357's fix: multi-factor seeding per RL-1361, with the seed route typed: leaf plan

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
plan) and **working id 9763** (its slice row `SL-9763` under `### WK-1178` in
`docs/roadmap.md`, `draft`). The lead reserved both ids and is the only allocator. Both are
minted at the merge turn; every working-id citation is then re-pointed. Unminted ids are
cited in working-id form and kept out of `relates:` (check 32). Three are cited here: `PL 9788`
(FD-1335 Part A and the untyped-body guard, draft PR #1036, which mint batch A gives the
number 1364), `FD 9779` (untyped JSON request bodies, draft PR #1044, batch A number 1366),
and `PL 9765` (WK-674 Slice 2's superseding plan). Each is re-pointed when it is minted.

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
   - (e) a re-seed into a lineage whose key is bound to another Factor's slug: 422
     `VALIDATION_FAILED`;
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
5. **One binding, never two** (`FR-228`, `RL-1361` Ruled item 9).
   `packages/model-schema/tests/test_rate_tables.py::test_a_key_carries_at_most_one_of_factor_ref_and_banding_ref`
   first asserts that a key with **only** `factor_ref` validates, then that a key with both
   is refused with `ValidationError`. **Red on `1dd5e264`:** the first assertion fails
   (`extra="forbid"` refuses `factor_ref`). The first assertion exists so that the second
   cannot pass vacuously on the current tree.
6. **The request is typed** (maintainer's rule (i); `FD 9779`'s seed-from-model entry).
   `test_api_rate_tables.py::test_the_seed_route_publishes_a_typed_request_and_201`, against
   `docs/contracts/openapi/generated.json`. The `POST /api/v1/rate-tables/{slug}/seed-from-model`
   `requestBody` JSON schema is a `$ref` to the `SeedFromModelRequest` component, and
   `docs/contracts/schemas/generated/seed-from-model-request.schema.json` exists. A body
   without `factor` gives 422 `VALIDATION_FAILED`, with a field error on `factor`.
   **Red on `1dd5e264`:** the schema is
   `{"additionalProperties": true, "title": "Body", "type": "object"}`, and the body without
   `factor` gives 201.
7. **The 201 is typed** (maintainer's rule (ii)). The same test asserts that the 201 JSON
   schema is a `$ref` to the `RateTableVersion` component, and that
   `docs/contracts/schemas/generated/rate-table-version.schema.json` exists.
   `uv run python scripts/generate-contracts.py --check` exits 0. **Red on `1dd5e264`:** the
   201 schema is an open object, and the generated file is absent. *(The slug names follow
   DP-4's recommendation and change if DP-4 is ruled otherwise.)*
8. **An unseedable row shape is a named 422, never a `KeyError`** (`FR-234`; FD-1357
   *Disposition*, "Hardening").
   `test_rate_table_operations.py::test_a_row_lacking_a_declared_key_is_a_named_refusal`: a
   two-key declaration with a row that carries one key. `validate_rate_table`,
   `diff_vs_previous` and `diff_vs_seed` each raise `ValueError`, and its message names the
   missing key. Through `_map_operation_error` (`platform/rate_tables.py:84-92`), that is 422
   `VALIDATION_FAILED`. **Red on `1dd5e264`:** `KeyError` at `operations.py:289`, `:232` and
   `:327`. Subject to DP-6.
9. **The `RL-1361` texts are applied byte for byte.** For each text this slice applies (see
   *Spec texts this slice applies*), a script in the ledger prints the count of the find
   string (0) and the count of the replacement (1) in the file. The only filled placeholders
   are `<fix date>` and `<first date>`, both the date of the fix commit, written
   `YYYY-MM-DD`. **Red before the edit:** each find count is 1, and each replacement count
   is 0.
10. **The untyped-body guard agrees, in either merge order.**
    - **Case A, this slice merges before `PL 9788`** (lane B order). `UNTYPED_REQUEST_PENDING`
      does not exist on main, and this slice adds no entry to any guard list. After this
      slice merges, `PL 9788`'s Task 0 drops the seed-from-model entry from
      `UNTYPED_REQUEST_PENDING`, and its activation re-measure drops
      `("POST", "/api/v1/rate-tables/{slug}/seed-from-model", "201")` from
      `UNTYPED_2XX_PENDING_PART_B`. The lead carries both drops to `PL 9788`'s dispatch
      record.
    - **Case B, `PL 9788` has merged first.** This slice removes both entries in the same
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
  (`RL-1361` section F). This slice changes no diff output. `T3`, `T6`, `T10` and `T11` are
  WK-673 Slice 7's.

## Scope

### Requirement coverage, each id individually

| Id | Where | This slice |
|---|---|---|
| FR-228 | `03` §3.3, `:119` | `factor_ref` on `RateTableKey`, at most one binding; `T1` if first (DP-5) |
| FR-229 | `03` §3.3, `:120` | `change_note` stays required and non-empty in the typed request |
| FR-230 | `03` §3.3, `:121` | one table per Factor; `T2`, `T4`, `T7`, `T8`, `T9` |
| FR-234 | `03` §3.3, `:125` | a row lacking a declared key is a named refusal (DP-6) |
| FR-451 | `07` §3.9, `:182` | contracts regenerated; the typed request and 201 published |
| FR-4 | `00`, `:209` | existing versions stay unbound, with no migration |

`FR-231` is **not** covered (FD-1358, `RL-1361` section F; WK-673 Slice 7).

### Premises, read at `1dd5e264`

| | Premise | Locator and command | Result |
|---|---|---|---|
| a | The pure seed declares one key per factor, while a row carries only its own factor's key | `packages/pricing-core/src/pricing_core/rate_tables/operations.py:142-157` (`extract_relativity_table`), `:191-194` (keys), `:289` (`row[key]`) | reproduces FD-1357 |
| b | The route body is `dict[str, Any]`, parsed by `_seed_body`, and returns `version.model_dump(mode="json")` | `backend/src/app/api/rate_tables.py:57-95`, `:118-145` | reproduces |
| c | The platform seed appends to an existing lineage and sets `seeded_from` on every seed | `backend/src/app/platform/rate_tables.py:95-173` (`:133-150` lineage, `:162` `seeded_from`) | reproduces; conflicts with `03:334-335` (DP-1) |
| d | No frontend caller | `grep -rn "seed-from-model\|seedFromModel" frontend/src --include=*.ts --include=*.vue \| grep -v generated` | prints nothing |
| e | Seed call sites | `grep -c "seed_from_model\|seed-from-model\|_seed_body(" backend/tests/test_api_rate_tables.py backend/tests/test_rate_tables_service.py packages/pricing-core/tests/test_rate_table_operations.py` | 39, 1 and 3 lines |
| f | `RateTableKey` is `extra="forbid"`, with `name`, `type` and `banding_ref` only | `packages/model-schema/src/model_schema/rating.py:662-669` | reproduces |
| g | Neither `RateTableVersion` nor a seed request is published under `generated/` | `ls docs/contracts/schemas/generated/` (33 files); `scripts/generate-contracts.py` `GENERATED_SHAPES` | reproduces |
| h | The authored `rate-table.schema.json` is never compared | `backend/tests/test_contracts.py`, `ONE_SIDED_SLUGS["rate-table"]` = "shipped in model-schema, never compared — register F27" | reproduces (DP-4) |
| i | Every `RL-1361` find string this slice applies occurs exactly once | `grep -cF -- '<find>' docs/specs/03-rating-engine.md` per text: FR-228 `:119`, FR-230 `:121`, §4.2 `:292`, `:296-298`, `:310`, §5.1 `:786`, §5.2 `:976-977`; `gi-pricing.yaml:238` | each prints 1 |
| j | `load_factors(session, *, workspace_id, factor_ids)` exists and also loads interaction operands | `backend/src/app/platform/modelling.py:284` | reproduces |
| k | `Factor` carries `slug` and `version` | `packages/model-schema/src/model_schema/modelling.py:122-135` | reproduces |
| l | The existing test models pin no Factors (`GlmSpec` default `factors=()`), so after the fix each must pin Factor rows | `backend/tests/test_api_rate_tables.py:61-69`, `:114-131` | reproduces |

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

If WK-673 Slice 7 lands `factor_ref` first, it applies `T1` and `T5`, and this slice cites
them and does not re-apply them. Any text a decision point below rules is applied the same
way, from its ruling file.

### Out of scope

- FD-1358 (per-cell weight in the diff output; owner WK-673). Its fix is not decided
  (`RL-1361` section F), and this slice touches no diff output.
- FR-231's weighting (`T3`, `T6`, `T10`, `T11`; WK-673 Slice 7).
- `WF-699` A1 (`T12`; a decision-maker, after this merges).
- The other four `FD 9779` routes (its Part B).
- The authored `rate-table.schema.json` (F27(c), the create-read-retire audit Work), unless
  DP-4 is ruled otherwise.

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocking | Resolver |
|---|---|---|---|---|---|---|
| DP-1 | `03:334-335` says `seeded_from` is set "only by seed-from-model, on the first version of a lineage". The code sets it on every seed, including a seed appended to an existing lineage (`platform/rate_tables.py:162`). `RL-1361` "What it obliges" says the fix must settle which is right. A spec-versus-code conflict (`CLAUDE.md` §0) | (a) The code is right: a seed starts a new baseline, so a re-seed's `seeded_from` names the new model, and `03:334-335` gets a dated clarification in the decision-maker's exact text. (b) The spec is right: a re-seed inherits the first version's `seeded_from`, and the code changes | **(a).** A re-seed from a newer model is a new technical rate. With (b), `diff_vs_seed` would measure distance from a superseded model, which defeats FR-230's "how far have we moved from the technical rate?". (a) changes no code and needs one dated sentence | decision-maker | **yes** (Acceptance 4 asserts the re-seeded version; the spec cannot be left contradicting the code in the same commit) | open |
| DP-2 | A re-seed into an existing lineage whose current version's key is **unbound** (a table seeded before `factor_ref`, or a hand-authored table, perhaps with several keys). `RL-1361` section A rules only "the slug the lineage's key is bound to" | (a) Accept when the current version has exactly one key, the key has no `factor_ref` and no `banding_ref`, and its name equals the named Factor's slug (every pre-fix seed named its key after the slug, `operations.py:191-194`). Otherwise refuse 422 by name. (b) Refuse every unbound lineage, so the caller must seed a new table slug. (c) Accept any unbound lineage | **(a).** `RL-1361` "What it obliges" says a table seeded before `factor_ref` "must be re-seeded to be weighted through a Factor". (a) lets that re-seed keep its lineage and its diff-vs-previous. (b) breaks it, and (c) lets a vehicle × area table take a one-key seed. Any spec sentence for (a) is the decision-maker's exact text, or the ruling says that `T2` and `T7` suffice | decision-maker | **yes** (Acceptance 3(e) and the lineage check) | open |
| DP-3 | The typed request. The maintainer's rule (i) decides that it is typed. `T7` fixes the fields `{"model_ref", "factor", "change_note"}`. `RL-1361` says "Whether the body gains a typed `model-schema` shape is not decided by this ruling", and it carries no text naming the shape | (a) `SeedFromModelRequest` in `model_schema/rating.py`: `model_ref: ArtifactRef` (an `after` validator refuses a type other than `model`), `factor: str` (non-empty), `change_note: str` (stripped and non-empty, FR-229), with `extra="forbid"`. No spec text: `T7`'s row states the body, and `generated/seed-from-model-request.schema.json` is the shape's written form. (b) As (a), plus a `03` §4.2 note naming the shape, in the decision-maker's exact text. (c) As (a), but `extra="ignore"`, so unknown fields keep being accepted | **(a).** `extra="forbid"` is the `model-schema` convention (`RateTableKey`, `rating.py:665`), and the break is already marked. The sub-graph request shapes were published with no spec note (`generate-contracts.py`, the `sub-graph-create` comment). (b) is acceptable if the decision-maker supplies the text | decision-maker | **yes** (Acceptance 6 and the schema slug) | open |
| DP-4 | Under which generated slug the 201's `RateTableVersion` is published, and whether the authored `docs/contracts/schemas/rate-table.schema.json` gains `factor_ref` | (a) A new generated-only slug `rate-table-version`, declared in `ONE_SIDED_SLUGS` with the reason "first written form of the route's 201; the authored rate-table contract is F27(c)'s, never compared". The authored file is not edited, and the ledger records the new divergence (`factor_ref`) for F27(c)'s owner. (b) The slug `rate-table`, which pairs it with the authored file and forces the comparison walkers over F27's seven known divergences. (c) No generated file, only the OpenAPI component | **(a).** (b) is F27(c)'s Work, which is a separate audit, and it would grow this slice by a contract reconciliation. (c) fails the maintainer's rule (ii), "a `$ref` into `docs/contracts/schemas/generated/`". The reason string is a code comment, not spec text | decision-maker | **yes** (Acceptance 7 and `ONE_SIDED_SLUGS`) | open |
| DP-5 | Does this slice land `factor_ref` (and so `T1` and `T5`), or does WK-673 Slice 7? `RL-1361`: "Which comes first is the lead's to order" | (a) This slice lands it, with `T1` and `T5`. (b) Slice 7 lands it first, and this slice waits for it | **(a).** The lane B order (the maintainer, about 10:10 BST) puts this fix ahead of every WK-673 slice, and seeding cannot set a field that does not exist | lead | yes (the dispatch record states it) | open |
| DP-6 | Is the FD-1357 *Disposition*'s hardening in this slice (Acceptance 8), and with which code? | (a) In: `validate_rate_table`, `_value_issue` and `_index_rows` raise a `ValueError` naming the missing key, which `_map_operation_error` maps to 422 `VALIDATION_FAILED` (`platform/rate_tables.py:92`). No new code name and no spec text. (b) In, with a new named code, which needs the decision-maker's `03` §5.2 text. (c) Out, as a follow-up | **(a).** The *Disposition* names it ("never a `KeyError`"). (a) adds no code name, so it needs no spec text under rule (iv) | lead (scope); decision-maker only if (b) | no (Acceptance 8 drops if (c)) | open |

**FD-1358 is out** (not a decision point). `RL-1361` section F rules that the per-cell weight
in the diff output predates the ruling, is owned by WK-673, and has no decided fix. This slice
changes neither `RateTableDiff` nor any diff route.

## Write set, and its serialisation (`RL-1263`)

| Path | Change | Shared with | Serialisation |
|---|---|---|---|
| `packages/model-schema/src/model_schema/rating.py` | `RateTableKey.factor_ref` and its validator (existing class); new `SeedFromModelRequest` | WK-673 Slice 7 (`RateTableKey`, `RateTableDiff`); WK-674 S2 / `PL 9765` (working id) if it edits this file | serialises with Slice 7 (same class): this slice first, under DP-5. Against `PL 9765`: the dispatch record names the path and checks that no existing definition is edited by both |
| `packages/model-schema/src/model_schema/__init__.py` | one export appended | WK-674 S2 / `PL 9765`, WK-1250 (`PL-1306:503`; `PL-1278:178-179`) | not on the registry list: serialises unless the dispatch record names the path (append-only `__all__` entries, with no existing definition edited) |
| `packages/pricing-core/src/pricing_core/rate_tables/operations.py` | `seed_from_model`, `extract_relativity_table`, `_key_domains_of`, `validate_rate_table`, `_value_issue`, `_index_rows` | WK-673 Slice 7 (the diff functions take `weights`) | serialises with Slice 7 |
| `backend/src/app/platform/rate_tables.py` | `seed_from_model` (Factor loading, the lineage check) | WK-673 Slice 7 (`diff`), the FD-1356 fix if it touches it | serialises with Slice 7 |
| `backend/src/app/api/rate_tables.py` | the seed handler typed; `_seed_body` removed | WK-675 S4 and S5 (`PL-1286`), Slice 7 (the diff route) | the FD 9779 hold, rule (i): a WK-675 slice that calls this route waits for this slice's merge. Serialises with Slice 7 |
| `scripts/generate-contracts.py` | two `GENERATED_SHAPES` entries appended (DP-4) | WK-674 S2 / `PL 9765`, WK-1250 S2 and S3 | not on the registry list: serialises unless the dispatch record names the path |
| `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/` | regenerated | everyone | registry-exempt: regenerated at the second merge, never hand-merged |
| `docs/contracts/openapi/gi-pricing.yaml` | `T8` (one line) | any slice editing the stub | hand-authored and **not** exempt: serialises |
| `docs/specs/03-rating-engine.md` | FR-228 row (`T1`), FR-230 row (`T2`), §4.2 block and note (`T4`, `T5`), §5.1 seed row (`T7`), §5.2 signature (`T9`), and DP-1's or DP-2's text if ruled | WK-674 S2 (§4 new subsection, one §5.1 row appended, `PL-1306:494-496`); WK-1250 S2 and S3 (§4.11, §5.1 rows); Slice 7 (`T3`, `T6`, `T10`, `T11`) | row-disjoint from WK-674 S2 and WK-1250 (different rows; the dispatch record checks both diffs). §4.2's block is shared with Slice 7 (`T6` edits the same JSON block): this slice first |
| `backend/tests/test_contracts.py` | two `ONE_SIDED_SLUGS` entries (DP-4); in Case B, two guard entries removed | `PL 9788` (it creates the guard lists), WK-674 S2, WK-1250, PL-1267 Slice 1 (`ONE_SIDED_SLUGS["dislocation-run"]`) | `ONE_SIDED_SLUGS` is an existing definition: serialises with each. `PL 9788` comes after this slice in lane B, and the second to merge re-gates (holds register) |
| `packages/model-schema/tests/test_rate_tables.py` | Acceptance 5 appended | none found | — |
| `packages/pricing-core/tests/test_rate_table_operations.py` | Acceptance 2, 3, 8 appended; the `seed_from_model` calls and `_glm_model` updated | Slice 7 | serialises with Slice 7 |
| `backend/tests/test_api_rate_tables.py` | Acceptance 1, 3, 4, 6, 7 appended; `_seed_approved_model`, `_seed_body` and every seed call updated (Factor rows pinned) | Slice 7 | serialises with Slice 7 |
| `backend/tests/test_rate_tables_service.py` | its `_seed_approved_model` and `_seed` updated | Slice 7 | as above |
| `docs/ledgers/LG-<id>-….md`, `docs/INDEX.md` | the ledger; the index regenerated | — | `INDEX.md` is registry-exempt |

**Lane B order** (the maintainer, about 10:10 BST): `SL-1360` → **this slice** → the
FD-1356 fix → the RL-1343 decimal-output fix → `PL 9788`. All are WK-1178 slices, so they run
one after another in any case (`RL-1263`: concurrent build slices only from different Works).
On lane A, WK-674 S2 (`PL 9765`) may run at the same time. The shared non-registry paths
above (`__init__.py`, `generate-contracts.py`, `test_contracts.py`, `03`) are named in the
dispatch record with the check that no existing definition is edited by both, or the second
slice waits.

**Holds** (`~/gi-pricing-plan.local/handover/holds-2026-10-01.md`):
- The **FD 9779 per-route hold, rule (ii)**: this slice **edits** the seed-from-model handler,
  so it types the body in the same slice (Acceptance 6). Its dispatch record states "case
  (ii)".
- This slice's merge **lifts rule (i)** for `POST /rate-tables/{slug}/seed-from-model`. A
  WK-675 slice that calls that route may then be dispatched.

## Activation needs, in order

1. `SL-1360` has merged on main. Run `git log --oneline origin/main | grep -m1 "SL-1360"`.
2. DP-1, DP-2, DP-3 and DP-4 each have a minted decision-maker ruling on main. A ruling that
   carries spec or contract text carries it verbatim. Check with `doc-id.py` and `grep` for
   each ruling id.
3. The lead's DP-5 and DP-6 verdicts are in the dispatch record.
4. This plan and `SL-9763` are minted, and the working ids are re-pointed.
5. Task 0's premises (a)–(l) re-read at the activation SHA, each holding. Every `RL-1361`
   find string still occurs exactly once. A changed line number is fine; a changed count is
   a stop.
6. `PL 9788`'s status is read at the activation SHA. The dispatch record states which case
   of Acceptance 10 applies.
7. **The maintainer's agreement and the lead's go**, in a **separate activation PR** that
   sets this plan `active` and `SL-9763` `active`.

## Tasks

### Task 0: Preconditions (no code)

- [ ] `uv sync --all-packages` in the executor's worktree (`dev-commands`).
- [ ] Re-run premises (a)–(l) at the activation SHA, and quote each output in the ledger.
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
  `extra="forbid"`). Run them red (`ImportError`), then add the class and its export.
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
  raises `KeyError`.
- [ ] Update the existing pure tests' `seed_from_model` calls (premise e) to pass `factor` and
  `factors`. Run the module green.

### Task 3: platform and route — loading, lineage, typing (Acceptance 1, 3(e)–(f), 4, 6, 7, 11)

- [ ] Update the backend fixtures. `_seed_approved_model` (both test modules) inserts a
  Factor row per relativity entry and pins the ids in `GlmSpec.factors`. `_seed_body` gains
  `factor`. Update every seed call (premise e).
- [ ] Append the route tests (Acceptance 1, 3(e), 3(f), 4, 6, 7). Run them against the
  unmodified `src/`, and quote each red. Acceptance 1's red is the 500 with `KeyError`.
- [ ] Platform `seed_from_model` gains `factor: str`. It calls `load_factors(session,
  workspace_id=workspace_id, factor_ids=list(model.spec.factors))` and passes `factor` and
  the Factors to the pure function. If the lineage exists, it reads the current version's
  keys and applies the lineage rule: the same slug is accepted, at any Factor version;
  another slug is refused 422 `VALIDATION_FAILED`; an unbound lineage follows DP-2's ruling.
  `seeded_from` follows DP-1's ruling.
- [ ] The route: `body: SeedFromModelRequest`, `_seed_body` deleted, and
  `responses={**problems(401, 403, 404, 409, 422), 201: {"model": RateTableVersion}}` (or
  `response_model=RateTableVersion`, whichever puts a `$ref` on the 201 while the handler
  returns the validated instance). The docstring names the body and the refusals.
- [ ] Append the two `GENERATED_SHAPES` entries (DP-4) and the two `ONE_SIDED_SLUGS` entries.
  Run `uv run python scripts/generate-contracts.py`, then `--check` (exit 0).
- [ ] Case B only: remove the seed-from-model entries from `UNTYPED_REQUEST_PENDING` and
  `UNTYPED_2XX_PENDING_PART_B`, after quoting the guard's red with them still listed.
- [ ] Run the rate-table, contract and model-schema tests green.

### Task 4: The spec texts (Acceptance 9)

- [ ] Run the Acceptance 9 count script before the edit (red), and quote it.
- [ ] Apply `T2`, `T4`, `T7`, `T8` and `T9`, plus `T1` and `T5` under DP-5 (a), plus any text
  that DP-1 to DP-4 rule, verbatim from the ruling files. Fill `<fix date>` and
  `<first date>` with the commit date. Change nothing else.
- [ ] Re-run the script (green), and quote it. Then run `python3 scripts/audit-docs.py`.

### Task 5: The gate and the ledger (Acceptance 12)

- [ ] Run the full two-half gate on the final tree. Announce it to the team first
  (`delivery-process.md` §8). Quote each exit code with the commit SHA and the tree.
- [ ] One commit, Conventional Commits:
  `feat(rating)!: SL-<id> — FD-1357's fix: one seeded table per Factor (RL-1361), typed seed request and 201`.
  Its body carries a `BREAKING CHANGE:` footer saying that the seed body now requires
  `factor`, and that unknown fields are refused if DP-3 is ruled (a).
- [ ] The ledger records: each red and green, the Acceptance 10 case, the DP resolvers, the
  F27(c) divergence note (DP-4 (a)), and the hand-off below.

## Hand-off

- **To a decision-maker, after the merge:** `RL-1361` `T12` (`WF-699` A1), with `<WF date>`.
- **To the lead:** in Case A, `PL 9788`'s dispatch record drops the seed-from-model request
  entry and its 201 entry. The FD 9779 hold, rule (i), lifts for seed-from-model. FD-1357's
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
  here. The weighting cases are Slice 7's.
- **No executor wording.** Every spec and contract sentence comes from `RL-1361` or from a DP
  ruling. DP-1 to DP-4 exist because `RL-1361` carries no text for them.
- **Red first.** Each of the 12 items names its red. Acceptance 5 guards against a vacuous red.
- **Placeholders.** None, except `RL-1361`'s own date placeholders, the `SL-<id>` and
  `LG-<id>` mint values, and the slug names that depend on DP-4.
