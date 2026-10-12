---
id: PL-9866
family: plan
kind: map
title: WK-1178 — FD-1366 Part B for the bulk-operation route, a discriminated request body and a typed 201 (SL 9868): a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1366, FD-1335, PL-1364, SL-1367, PL-1546, SL-1547, RL-1613, RL-1263, RL-1445]
---

# PL 9866 — WK-1178, FD-1366 Part B for the bulk-operation route: a discriminated request body and a typed 201 (SL 9868)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1627` and `PL-1577`, this delta `relates:` the records it
> builds on: `FD-1366` (the finding), `PL-1364` (Part A, the guard) and `SL-1367` (its slice).
> It adds **one slice row**, SL 9868, under `### WK-1178` in [`../roadmap.md`](../roadmap.md).
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (every acceptance item is seen red **by its cause** before the code that turns it green),
> `python-test` (the `req` marker; negative tests), `python-package`, `fastapi-service`,
> `contract-schema` and `contract-guard` (Tasks 2–4), `spec-change` (Task 1), `dev-commands`
> (`uv sync --all-packages`; both gate halves) and `git-hygiene`. Read [`README.md`](README.md)'s
> five unchecked conventions before the first step. The executor is spawned from
> `.claude/roles/executor.md`.

Filed under **working id 9866**; its slice row is **working id 9868** (`draft`). Both were
reserved by the lead, `~/gi-pricing-plan.local/handover/eta.md` line "2026-10-12 02:54:24 BST",
free-checked 0/0/0. Written 2026-10-12 by the planner (seat planner-wk1250-s3). **Tree read:**
`origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` (#1288, SL-1517). Every `file:line`
below was read there. **No test was run at planning time.**

## Context — the rulings this delta records

Three entries in `~/gi-pricing-plan.local/channel/to-lead.md`, by the maintainer (by
delegation). A repository reader cannot open that file (RFC-777), so the parts this delta rests
on are quoted verbatim.

1. **"2026-10-12 02:51:32 BST — Lane C S5 NOT READY: (1)+(2) OK on the first free planner;
   ALSO check S8/S6 readiness so lane C does not idle"**: *"(1) the FD-1366 Part B typing-slice
   planner and (2) the PL-1546 delta for RL-1613: YES, on the first free readiness planner, no
   extra seat."* (2) is `PL 9867`, filed on the same branch.
2. **"2026-10-12 02:58:33 BST — DP-0: (b), stated as SUPERSEDING my 2026-10-11 10:55:02 item 2
   (DP-A (a)); with a fallback trigger"**, condition 1: *"PL 9866 cuts SL 9868 (WK-1178): the
   bulk-operation request + 201 only, (c) refused. It cites this entry AND strikes nothing,
   because the plan never carried DP-A. Instead PL 9866's Context names 10:55:02 item 2 as
   superseded by this entry."* Condition 3: *"FALLBACK TRIGGER: if SL 9868 is not merged when S6
   merges, bring it to me. S5 then either waits or reverts to DP-A (a), my ruling at that time."*
3. **Superseded: "2026-10-11 10:55:02 BST — S5 (SL-1547) not ready: … (2) DP-A = (a), S5 types
   its own bulk-operation route"**, item 2: *"S5 types POST bulk-operation itself, in its FIRST
   commit, with the existing BulkOperationBase (model_schema/rating.py:1179). That discharges
   FD-1366 Part B for that ONE route"*. **Item 2 is superseded by entry 2 above.** On `main` it
   is cited only by `RL-1613:111` (*"S5 is already OpenAPI-contract-changing under the 10:55:02
   BST entry's DP-A (a)"*). The supersession is recorded in a governed record by `RL 9870`
   (working id, reserved by the lead, eta "2026-10-12 02:58:57 BST"; the D13 batch), not here.

## Goal

`POST /api/v1/rate-tables/{slug}@{version}/bulk-operation` publishes a typed JSON request body
and a typed 201, so that WK-675 S5 (`SL-1547`) generates both types and hand-writes neither
(`CLAUDE.md` §2; `FD-1366` *Disposition*, per-route hold (i)):

- the request body is a **discriminated union on `kind`** of four request models, each carrying
  the existing `*Parameters` model of its kind (`model_schema/rating.py:1232-1264`);
- the four `*Operation` records (`:1267-1285`) are rebuilt on those request models, so the
  `kind`/`parameters` pairing is written once, and **their field order and serialised bytes do
  not move** (DP-1);
- the 201 is published as `RateTableVersion` (the seed route's precedent, `rate_tables.py:99`);
- the route leaves both pending lists in `backend/tests/test_contracts.py`:
  `UNTYPED_REQUEST_PENDING` (`:3202-3205`) and `UNTYPED_2XX_PENDING_PART_B` (`:3192`).

**Out of scope (02:58:33 condition 1, "(c) refused"):** the two sub-graph routes
(`sub_graphs.py:45`, `:60`), which stay in `UNTYPED_REQUEST_PENDING` with WK-1178. `FD-1366`
therefore stays **active**; this slice adds a dated line to its register row naming the route.

## Status

The status is the `status:` field in the header, and nothing else. **It stays `draft` while
DP-2 below is open.** DP-0 is ruled (Context, entry 2); DP-1 is the planner's design choice,
stated with its proof obligation, and is not a ruling.

## Activation needs, each with its state at `fc4401dc`

1. **DP-0 ruled.** **MET**: Context, entry 2 (02:58:33).
2. **DP-2 ruled** by the lead or a decision-maker, with a dated line. **OPEN.**
3. **This delta is minted or GO'd on its working ids**, as the lead dispatches. **OPEN.**
4. **No in-flight writer on the write set below, or the dispatch record names the
   definitions.** At `fc4401dc`, a sweep of 57 origin refs
   (`git diff --name-only origin/main...<ref> -- <write set>`) found none on
   `backend/src/app/api/rate_tables.py`, the bulk-operation block of
   `model_schema/rating.py`, or `backend/tests/test_api_rate_tables.py`. Known writers to
   shared paths: WK-1250 S3 (`SL-1341`, READY plan-side, not dispatched) edits `SubGraphRef` in
   the same `rating.py` (a different definition) and regenerates `docs/contracts/`; WK-675 S5
   (`SL-1547`) waits for this slice (PL 9867). **Re-check at the GO.**
5. **A build slot and the single gate** (`RL-1445` item 1). SL-1527 (WK-1178) is building: a
   second WK-1178 slice may run beside it only with `RL-1445` item 2's two conditions in the
   dispatch record. (a) **Files.** SL 9868's set (below) and SL-1527's (`examples/`, the demo
   path) are disjoint at `fc4401dc`; the lead re-checks this at the GO. (b) **Dependencies.**
   Neither slice consumes the other's output. It needs **no gate before S6's gate** (02:58:33,
   condition 2).
6. **The lead's GO**, on the FIRST free seat (02:58:33, condition 2).

## Scope and requirements, each id individually

- `03` **FR-233** (bulk operations are recorded with their parameters): the route this slice types.
- `07` **FR-451** (the contract is generated, and CI fails on drift): the regenerated
  `docs/contracts/`.
- `00` **FR-10** (exact decimals, never a float): DP-2 only.
- `FD-1366` Part B for this one route; `FD-1335` Part B for this route's 201.

## Premises, read at `fc4401dc`

| # | Premise | Where | What the source says |
|---|---|---|---|
| a | The route takes an open body | `backend/src/app/api/rate_tables.py:180-224` | `body: dict[str, Any]` (`:189`); `-> dict[str, Any]` (`:194`); a hand check of `kind`/`parameters` raising `VALIDATION_FAILED` (`:203-211`); `service.bulk_operation(..., kind=kind, parameters=parameters)` (`:213-223`); `return created.model_dump(mode="json")` (`:224`) |
| b | The record carries two server-set fields | `model_schema/rating.py:1224-1229`; `rate_tables.py:198-201` | `BulkOperationBase` = `applied_to: ArtifactRef`, `result: BulkOperationResult`; docstring: *"`applied_to` and `result` are server-side"*. So `BulkOperationBase` cannot itself be the request body (DP-1) |
| c | The four kinds | `rating.py:1232-1300` | four `*Parameters` models; four `*Operation(BulkOperationBase)` with `kind: Literal[...]` and `parameters`; `BulkOperation` = `Annotated[… , Field(discriminator="kind")]` (`:1289-1295`); `BULK_OPERATION_ADAPTER` (`:1300`) |
| d | The parameters accept a float today | `rating.py:1236`, `:1244`, `:1252-1253`; `docs/contracts/schemas/generated/rate-table-version.schema.json` `$defs.UpliftTableParameters` | `percentage: Decimal`, `floor: Decimal`, `cap: Decimal`; published as `anyOf: [{"type": "number"}, {"type": "string", …}]`. `04` §4.4: *"decimal strings, never floats (R2)"* (DP-2) |
| e | The service validates again, by kind | `backend/src/app/platform/rate_tables.py:1496-1522`, `:1525-1584` | `_dispatch_operation(kind: str, parameters: dict[str, Any], table)` parses each `*Parameters` by `model_validate`; unknown kind → `VALIDATION_FAILED`. Ten test call sites use this signature (`test_rate_tables_service.py:131`, `:179`, `:236`, `:248`, `:348`, `:372`, `:396`; `test_nfr498_audit_events.py:106`; `test_rate_table_diff_portfolio.py:871`). **The service signature is not changed** |
| f | The precedent for a typed 201 and a typed request | `rate_tables.py:95-133` (seed route) | `response_model=RateTableVersion`; `body: SeedFromModelRequest`; returns the model |
| g | A request-validation failure is `VALIDATION_FAILED` | `backend/src/app/errors.py:508-530` | `_handle_validation_error` renders a `RequestValidationError` with `code="VALIDATION_FAILED"` and field errors, the field path dropping its leading `body` segment |
| h | The guard and its stale check | `backend/tests/test_contracts.py:3187-3213`, `:3273-3290` | `test_every_untyped_body_exclusion_is_still_untyped` fails on any listed route that is no longer untyped (`stale_requests`, `stale_2xx`) |
| i | How a union reaches a published schema | `scripts/generate-contracts.py:215-237`, `:65` | `getattr(model_schema, name)`; a `TypeAdapter` takes `json_schema(mode="validation")` (`"model-spec": "MODEL_SPEC_ADAPTER"`); a first written form is listed in `test_contracts.py` `ONE_SIDED_SLUGS` (`:70-90`, e.g. `"seed-from-model-request"`) |
| j | FastAPI takes a discriminated body | `uv.lock:530-531` (`fastapi` `0.142.2`); `fastapi/param_functions.py` `Body(..., discriminator=...)` | Read in the root venv's `0.141.1`; the executor re-reads at the slice's own `uv sync` |
| k | Existing API tests that pin behaviour | `backend/tests/test_api_rate_tables.py:739-753`, `:780-781` (`_bulk_body`), `:784-878` | 401/403 with a valid body; 201 records the operation; unknown kind → 422 `VALIDATION_FAILED` (`:822-841`); floor above cap → 422 `FLOOR_ABOVE_CAP` (`:845-864`); missing version → 404 `RATE_TABLE_MISS` (`:868-878`). **All stay green unchanged** |

## Decision points

| DP | Question | Options | Recommendation | Blocking | Who |
|---|---|---|---|---|---|
| DP-0 | Who types this route: S5 (DP-A (a), 10:55:02) or a WK-1178 slice? | (a) S5, in its first commit; (b) a WK-1178 slice, S5 waits; (c) (b) plus the two sub-graph routes | — | — | **Ruled (b)**, the maintainer 02:58:33 (Context, entry 2); (c) refused |
| DP-1 | What is the request body's shape, since `BulkOperationBase` carries server-set fields (premise b)? | (i) four request models `{kind, parameters}`, the four records **inheriting** from them, with field order pinned; (ii) four request models written separately from the records; (iii) make `applied_to`/`result` optional on the record | **(i).** It writes the `kind`↔`parameters` pairing once (`CLAUDE.md` §2: "a shape defined twice will diverge"). (ii) defines it twice. (iii) weakens the persisted record. **Proof obligation:** the record's field order (`applied_to, result, kind, parameters`), its JSON dump and its published schema do not move (Acceptance 4, 5) | no | the planner (a design choice inside a ruled scope); stated here so the lead can overrule it |
| DP-2 | The typed request publishes `percentage`/`floor`/`cap` as `number \| string` (premise d), so a generated client may send a float, and the route accepts it today. Does this slice close that? | (a) the four `*Parameters` decimal fields become `DecimalStr` (`model_schema/money.py:95-100`, float refused, string schema), shared by record and request; (b) leave `Decimal`, publish `number \| string`, and file an FD (owner WK-1178) for the float acceptance; (c) request-only strictness with separate request parameter models | **(a).** The route is being typed now. Publishing a float-accepting contract that S5 then generates against is the hazard `generate-contracts.py:224-229` names (research F7), and `04` §4.4 already says "never floats". `DecimalStr` serialises with `str()`, as `Decimal` does in JSON mode, so stored bytes do not move (Acceptance 5 proves this). (c) duplicates four shapes; (b) leaves a known FR-10 gap published | **yes, for the GO** | lead or decision-maker, dated line |

## Write set

| Path | What changes | Task |
|---|---|---|
| `docs/specs/03-rating-engine.md` §5.1 bulk-operation row (`:1039`) | a dated clause: the request body and the 201 | 1 |
| `packages/model-schema/src/model_schema/rating.py` `:1215-1300` | four `*Request` models; `BulkOperationRequest` union; `BULK_OPERATION_REQUEST_ADAPTER`; the four `*Operation` records rebased (DP-1 (i)); under DP-2 (a), `DecimalStr` on four fields | 2 |
| `packages/model-schema/src/model_schema/__init__.py` (`:314`, `:720` neighbourhood) | import + `__all__`: the four request models, `BulkOperationRequest`, `BULK_OPERATION_REQUEST_ADAPTER` | 2 |
| `packages/model-schema/tests/test_rate_tables.py` | DP-1's order pin; DP-2's float refusal (if (a)); the request models' `extra="forbid"` | 2 |
| `backend/src/app/api/rate_tables.py` `:42-50`, `:180-224` | the typed body and 201; the hand check removed; the service call unchanged in signature | 3 |
| `backend/tests/test_api_rate_tables.py` | three new red-first tests (Task 3); the existing ones unchanged | 3 |
| `scripts/generate-contracts.py` `GENERATED_SHAPES` | `"bulk-operation-request": "BULK_OPERATION_REQUEST_ADAPTER"`, dated comment | 4 |
| `backend/tests/test_contracts.py` `:70-90`, `:3192`, `:3202-3205` | `ONE_SIDED_SLUGS` entry; both pending entries removed | 4 |
| `docs/contracts/openapi/generated.json`; `docs/contracts/schemas/generated/bulk-operation-request.schema.json` (new); `…/rate-table-version.schema.json` (DP-2 (a) only) | regenerated, never hand-edited | 4 |
| `docs/findings/register.md` FD-1366 row | a dated line: the bulk-operation route typed by SL 9868 | 5 |
| `docs/roadmap.md` SL 9868 row; `docs/ledgers/LG-<working id>` | status lines and the slice ledger (L1 (a')) | 0, 5 |

`frontend/src/api/generated` is regenerated and VCS-ignored; it is not in the write set. No
frontend source calls this route at `fc4401dc` (`grep -rln bulk frontend/src --include=*.ts
--include=*.vue | grep -v generated` → no output).

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, cut from
  `origin/main`. `uv sync --all-packages`.
- [ ] Re-read premises a–k at the slice base, and record each one in the `LG-`, with its locator.
- [ ] `gh pr list --state open`, and grep `to-lead.md` for entries since 2026-10-12 02:58:33 that
  rule on `bulk-operation`, `FD-1366`, `BulkOperation` or `DecimalStr`. Name the SHA and entry read.
- [ ] Quote DP-2's ruling (dated) in the `LG-`. Stop if it is absent.
- [ ] Sweep the python-mode dumps the DP-2 (a) serialiser could change:
  `grep -rn 'created_by_operation\|BulkOperation\|Parameters(' packages/*/src backend/src --include=*.py`;
  read each hit; record in the `LG-` any that dumps in Python mode, not JSON mode. At
  `fc4401dc` the stores are JSON-mode (`platform/rate_tables.py:1439-1442`) and
  `pricing_core/rate_tables/operations.py:653` builds the record from the model.
- [ ] Commit the `LG-` scaffold and the SL row's `active` line (L1 (a')).

### Task 1: Spec — `03` §5.1's bulk-operation row

- [ ] Append to the row's description cell (`03:1039`), keeping the row's cell count:
  `*(Amended <date>, SL 9868, FD-1366 Part B: the request body is a BulkOperationRequest, the 04 §4.4 record's kind and parameters, discriminated on kind; applied_to and result are set by the server. The 201 is the new RateTableVersion.)*`
  Under DP-2 (a), add: `percentage, floor and cap are decimal strings; a JSON number is refused (FR-10).`
- [ ] `python3 scripts/audit-docs.py` exits 0 (run once, under `flock -w 1800 /tmp/slots/gate-2`).
- [ ] Commit: `docs(specs): 03 §5.1 — the bulk-operation request body and 201 (FD-1366 Part B)`.

### Task 2: `model-schema` — the request models (DP-1 (i)) and, under DP-2 (a), `DecimalStr`

**Interfaces — Produces:** `UpliftTableRequest`, `UpliftByFilterRequest`, `FloorAndCapRequest`,
`RebaseToLevelRequest` (each `kind: Literal[...]`, `parameters: <Kind>Parameters`,
`ConfigDict(frozen=True, extra="forbid")`); `BulkOperationRequest = Annotated[UpliftTableRequest
| UpliftByFilterRequest | FloorAndCapRequest | RebaseToLevelRequest, Field(discriminator="kind")]`;
`BULK_OPERATION_REQUEST_ADAPTER: Final[TypeAdapter[BulkOperationRequest]]`.

- [ ] **Red 1 (the order pin, a guard).** In `packages/model-schema/tests/test_rate_tables.py`:

```python
@pytest.mark.req("FR-233")
@pytest.mark.parametrize(
    "record", [UpliftTableOperation, UpliftByFilterOperation, FloorAndCapOperation, RebaseToLevelOperation]
)
def test_a_bulk_operation_record_keeps_its_field_order(record: type[BaseModel]) -> None:
    # The stored JSON (platform/rate_tables.py:1439-1442) is dumped in this order.
    assert list(record.model_fields) == ["applied_to", "result", "kind", "parameters"]
```

  It is green at the base. Show it **red on a planted reversal** (declare the record
  `class UpliftTableOperation(BulkOperationBase, UpliftTableRequest)` in a scratch edit: the order becomes
  `kind, parameters, applied_to, result`). Revert. Record both outputs in the `LG-`.
- [ ] **Red 2 (the request refuses a server-set field).** `BULK_OPERATION_REQUEST_ADAPTER.validate_python({"kind": "uplift_table", "parameters": {"percentage": "0.10"}, "applied_to": "rate_table:t@1"})` raises `ValidationError` (`extra_forbidden`). Run it: **red by its cause** (`ImportError`, the adapter does not exist).
- [ ] **Red 3 (DP-2 (a) only).** `UpliftTableParameters.model_validate({"percentage": 0.1})` raises `ValidationError` from `_reject_float`'s `InputFreeError`; the same for `floor`/`cap`. Run it: **red by its cause** (`DID NOT RAISE`; `Decimal` accepts the float today).
- [ ] Implement. Each record keeps `BulkOperationBase` **first in its own field order**:
  `class UpliftTableOperation(UpliftTableRequest, BulkOperationBase)` declares no field and the
  pin decides. Pydantic collects fields in reverse MRO, so `BulkOperationBase`'s come first;
  Red 1 is the proof, not this sentence. Under DP-2 (a), `percentage`, `floor` and `cap` become
  `DecimalStr`, imported from `model_schema.money`.
- [ ] Export the new names from `model_schema/__init__.py` (import block and `__all__`).
- [ ] Reds 1–3 green; `uv run pytest -q packages/model-schema/tests/test_rate_tables.py` exits 0.
- [ ] Commit: `feat(model-schema): BulkOperationRequest — the bulk-operation request, discriminated on kind (FD-1366 Part B)`.

### Task 3: The route — typed body and 201

**Interfaces — Consumes:** Task 2's `BulkOperationRequest`. The service call keeps its
signature (premise e).

- [ ] **Red 4 (a server-set field is refused at the boundary).** In `test_api_rate_tables.py`, a
  `@pytest.mark.req("FR-233")` test seeds a table, posts
  `{"kind": "uplift_table", "parameters": {"percentage": "0.10"}, "applied_to": "rate_table:x@1"}`,
  and asserts 422, `code == "VALIDATION_FAILED"`, and a field error whose `field` ends with
  `applied_to`. Run it: **red by its cause** (201; the open body ignores the extra key).
- [ ] **Red 5 (DP-2 (a) only: a float is refused).** The same, with `{"percentage": 0.1}`;
  asserts 422 `VALIDATION_FAILED` with a field error ending `percentage`. Run it: **red by its
  cause** (201).
- [ ] **Red 6 (the published contract).** A `@pytest.mark.req("FR-451")` test in
  `test_api_rate_tables.py` reads `app.openapi()` for the route and asserts:
  - the request body's `application/json` schema has `discriminator.propertyName == "kind"`;
  - it has exactly four arms;
  - the `201` schema is a `$ref` ending `RateTableVersion`.

  Run it: **red by its cause** (an open object; `additionalProperties: true`).
- [ ] Implement at `rate_tables.py:180-224`:
  - `response_model=RateTableVersion` in the decorator;
  - `body: Annotated[BulkOperationRequest, Body()]`, or, if the published schema then lacks the
    discriminator, `Body(discriminator="kind")` on the bare union. Red 6 decides which, and the
    `LG-` records the form that turned it green;
  - `-> RateTableVersion`;
  - delete the hand check (`:203-211`);
  - call `service.bulk_operation(..., kind=body.kind, parameters=body.parameters.model_dump(mode="json"))`;
  - `return created`.

  Keep the docstring's 201/refusal text, and replace its body sentence with the model's name.
  Add `Body` to the `fastapi` import and the four request names to the `model_schema.rating`
  import. `Any` stays (`:288`, `:339`).
- [ ] Reds 4–6 green. Every existing bulk test in the file (premise k) passes **unchanged**:
  `uv run pytest -q backend/tests/test_api_rate_tables.py -k bulk` (one file, `-k` selection; check
  `pgrep -af 'pytest|vitest|flock'` and both slots first, per the executor charter).
- [ ] Commit: `feat(rating): type POST bulk-operation's request and 201 (FD-1366 Part B, FD-1335 Part B)`.

### Task 4: Contracts and the guard lists

- [ ] `uv run python scripts/generate-contracts.py` (writes). Then
  `git diff --stat docs/contracts` must name only:
  - `openapi/generated.json`;
  - the new `schemas/generated/bulk-operation-request.schema.json`;
  - under DP-2 (a), `schemas/generated/rate-table-version.schema.json`, whose only change is
    the three decimal fields' `anyOf` becoming the `DecimalStr` string schema. Show that hunk
    in the `LG-`.

  Any other file in the stat is a stop.
- [ ] `GENERATED_SHAPES`: add `"bulk-operation-request": "BULK_OPERATION_REQUEST_ADAPTER"` with a
  dated comment citing this delta. `ONE_SIDED_SLUGS`: add
  `"bulk-operation-request": "first written form — 03 §5.1 bulk-operation row (FD-1366 Part B, FR-233)"`.
- [ ] Run `uv run pytest -q backend/tests/test_contracts.py -k "untyped or one_sided"`: **red by
  its cause**. `test_every_untyped_body_exclusion_is_still_untyped` names
  `("POST", "/api/v1/rate-tables/{slug}@{version}/bulk-operation")` in `stale_requests` and its
  `"201"` key in `stale_2xx`. Record the output.
- [ ] Remove the `UNTYPED_REQUEST_PENDING` entry (`:3202-3205`) and the
  `UNTYPED_2XX_PENDING_PART_B` key (`:3192`). The two sub-graph entries stay. Re-run: green.
- [ ] `uv run python scripts/generate-contracts.py --check` exits 0;
  `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend type-check` exits 0.
- [ ] Commit: `chore(contracts): regenerate for the typed bulk-operation route; the guard lists shrink (FD-1366 Part B)`.

### Task 5: The gate, the register line, the ledger

- [ ] `docs/findings/register.md`, FD-1366's row: append
  `*(<date>: the bulk-operation route typed by SL 9868 (PL 9866). Remaining: POST /sub-graphs and POST /sub-graphs/{slug}/versions, owner WK-1178.)*`
  The finding stays `active`.
- [ ] The full gate, both halves (`CLAUDE.md` §11), in the single gate slot, on
  `origin/main...<branch>`; the rc table goes in the `LG-`.
- [ ] Closing acts in the slice PR's last commit (L1 (a')): SL 9868 `closed` line; the `LG-`'s
  Audit section after the auditor's verdict.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **The route publishes a typed request and 201:** Red 6's test passes, and
   `python3 -c "import json;d=json.load(open('docs/contracts/openapi/generated.json'));op=d['paths']['/api/v1/rate-tables/{slug}@{version}/bulk-operation']['post'];print(op['requestBody']['content']['application/json']['schema'].get('discriminator'), op['responses']['201']['content']['application/json']['schema'])"`
   prints a `kind` discriminator and a `RateTableVersion` `$ref`.
2. **Both guard entries are gone, the sub-graph entries stay:**
   `grep -n 'bulk-operation' backend/tests/test_contracts.py` prints no line inside
   `UNTYPED_REQUEST_PENDING` or `UNTYPED_2XX_PENDING_PART_B`; `grep -c 'pending FD-1366 Part B'
   backend/tests/test_contracts.py` prints `3` (two entries plus the assertion at `:3288`).
3. **A server-set field is refused at the boundary** (Red 4) and, under DP-2 (a), **a float is
   refused** (Reds 3, 5); each was seen red by its cause, in the `LG-`.
4. **The record's field order is pinned:** Red 1 passes, and its planted-reversal red is in the `LG-`.
5. **Stored bytes do not move:** a test dumps one record of each kind built from string decimals
   (`model_dump(mode="json")`) and compares it with the literal dump recorded at the slice base;
   the literals are pasted in the test from a run at the base. Shown red in the `LG-` by
   planting `PlainSerializer(lambda v: format(v, "e"))` on `percentage`.
6. **Existing behaviour holds:** premise k's tests pass unchanged (`git diff origin/main --
   backend/tests/test_api_rate_tables.py` adds lines only).
7. **No hand-written shape; no drift:** `uv run python scripts/generate-contracts.py --check`
   exits 0; `pnpm --dir frontend generate:api` leaves `git status --short` clean of tracked files.
8. **The gate is green on the merge tree:** the `CLAUDE.md` §11 commands, both halves, each exit 0
   against `origin/main...<slice branch>`.

## Global Constraints

- `CLAUDE.md` §2: no shape written twice; `docs/contracts/` generated, never hand-edited;
  `frontend/src/api/generated` VCS-ignored.
- `CLAUDE.md` §7 / `00` FR-10: an exact decimal never crosses as a float.
- `pricing-core` stays free of FastAPI/SQLAlchemy; no pandas.
- One PR per slice (L1 (a')): code, tests, spec clause, SL status line, one `LG-`.
- `RL-1445` item 1: one full gate at a time; targeted single-file runs only outside it.

## Hand-off (not this plan's writes)

- **The WK-1178 roadmap row** lists this delta as a Work-plan delta. The planner's charter
  limits its roadmap writes to the `SL-` rows it cuts. The line is the lead's or the D13
  minter's.
- **RL 9870** (the DP-0 supersession record) is D13's.
- **The fallback trigger** (02:58:33 condition 3) is the lead's: if SL 9868 has not merged when
  `SL-1548` (S6) merges, it goes to the maintainer.

## Self-review

- **Spec coverage.** FR-233's route is typed in both directions. FR-451's drift check covers the
  regenerated files. FR-10 is covered under DP-2 (a) only, and DP-2 is blocking, so no silent pick.
- **Placeholders.** None. `<date>` and the `LG-` working id are filled at execution.
- **Type consistency.** `BulkOperationRequest` and `BULK_OPERATION_REQUEST_ADAPTER` are named the
  same in Tasks 2–4. The four request names follow the records' names, with `Operation`
  replaced by `Request`.
- **Literals.** Every `file:line` was read at `fc4401dc`. The FastAPI `Body(discriminator=)`
  claim was read in the root venv (`0.141.1`), not at the locked `0.142.2`, so Red 6 is the
  arbiter (Task 3).
- **Convention 4.** `gh pr list --state open` at 2026-10-12 ~02:50 BST returned only #1289
  (SL-1527), which does not rule on this subject. The to-lead entries since this plan's
  premises were read up to 02:58:33.
