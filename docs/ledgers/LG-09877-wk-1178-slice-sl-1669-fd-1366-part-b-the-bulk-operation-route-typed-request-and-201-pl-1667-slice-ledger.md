---
id: LG-9877
family: ledger
title: WK-1178 slice SL-1669 — FD-1366 Part B for the bulk-operation route, a discriminated request body and a typed 201 (PL-1667), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 249670fe2506ea1572d80faa1f3821edf04f194c
phase: P2
work: WK-1178
slice: SL-1669
plans: [PL-1667]
corrected_by: []
relates: [PL-1667, SL-1669, FD-1366, FD-1335, RL-1670, PL-1668, SL-1547, FR-233, FR-451]
---

# LG-9877 — WK-1178 slice SL-1669: the bulk-operation route, a typed request and a typed 201

*(Working id 9877, reserved by the lead. The id is minted at the merge turn; until then every citation of this record is by working id.)*

**GO:** the lead's from-lead entry "2026-10-12 04:53:47 BST" (GO SL-1669; ledger working id 9877). Authority for the scope: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-12 02:58:33 BST" (DP-0 = (b); the bulk-operation request and 201 only), "2026-10-12 03:06:12 BST" (DecimalStr; the breaking-caller sweep), "2026-10-12 03:07:15 BST" (the 04 :278 T-text) and "2026-10-12 03:08:30 BST" item 3 (integers stay accepted); `RL-1670` on main.
**FALLBACK (02:58:33 condition 3):** if `SL-1548` merges before this slice, the maintainer rules S5's path.
**MERGE-ACK:** not yet given.

## Tasks

Executed from `PL-1667` (Tasks 0–5), branch `sl-1669-wk1178-bulk-op-typing`, worktree `.claude/worktrees/sl-1669`, cut from `origin/main` `249670fe2506ea1572d80faa1f3821edf04f194c` (#1290).

### Task 0 — preconditions

- **Readiness** (reported to the lead before the GO): no blocking need found; file-set re-check at `249670fe`: only `docs/findings/register.md` and `docs/specs/03-rating-engine.md` moved in the write set since the plan's base `fc4401dc`, the 03 change being one added line near `:1555`, away from the §5.1 row at `:1039`.
- **Breaking-caller sweep (03:06:12 item 2)**, run verbatim at `249670fe` from the worktree root: the first command prints **13** hits and the second **1**, as the planner recorded. **None is a bulk-operation body** (no `_bulk_body(`, no post to `bulk-operation`, no `svc.bulk_operation(`, no `*Parameters(` or `*Operation(` constructor, no `BULK_OPERATION_ADAPTER` on any hit line). The hits are custom-metric and objective `cap` params (`test_custom_metrics.py:69`, `test_custom_metrics_api.py:41`, `test_custom_metrics_table.py:57,77,95`, `test_custom_objectives.py:690,706`, `packages/model-schema/tests/test_metrics.py:56`, `packages/model-schema/tests/test_objectives.py:251,252`, `packages/pricing-core/tests/test_objectives.py:83`), an expression arity table (`pricing_core/data/expressions.py:76`), a ZEN input (`test_rating_wire_order.py:234`) and a `change_note` string assertion (`test_rate_table_bulk_ops.py:156`). **Nothing converts**; the sweep is re-run at the head (Acceptance 3).
- **Python-mode dump sweep** (`created_by_operation|BulkOperation|Parameters(` over `packages/*/src`, `backend/src`): the stores are JSON-mode (`backend/src/app/platform/rate_tables.py:1439-1442`, `.model_dump(mode="json")`); `pricing_core/rate_tables/operations.py:653` builds the version from the model, and `:717`, `:752`, `:783` build the `*Parameters` from values the operations already hold. No Python-mode dump of a `*Operation` found.
- **Open PRs and rulings:** `gh` answers "HTTP 401: Bad credentials" in this shell (no token exported yet); the to-lead entries since "2026-10-12 02:58:33 BST" naming `bulk-operation`, `SL-1669`, `FD-1366` or `DecimalStr` are the three listed above, read in full.

- **Premises a–k** re-read at `249670fe`: a (`backend/src/app/api/rate_tables.py:180-224`, open `dict[str, Any]` body and hand check) and k (`backend/tests/test_api_rate_tables.py`, the existing bulk tests) were read and exercised; b–d at `packages/model-schema/src/model_schema/rating.py:1215-1300` (`BulkOperationBase`, four `*Parameters`, four `*Operation`, `BULK_OPERATION_ADAPTER`; `percentage`, `floor` and `cap` were a bare `Decimal`); e, f, g unchanged in the service, the seed route and `errors.py`; h at `backend/tests/test_contracts.py` (`UNTYPED_REQUEST_PENDING`, `UNTYPED_2XX_PENDING_PART_B`, `test_every_untyped_body_exclusion_is_still_untyped`); i at `scripts/generate-contracts.py` (`GENERATED_SHAPES`, the `TypeAdapter` path) and `ONE_SIDED_SLUGS`. The generated `model_schema/__init__.py` exports are what `generate-contracts.py` reads by `getattr`, so the six new names are exported there. j: the locked `fastapi` took the bare `Annotated` union with no `Body(discriminator=)`; Red 6 is green with `body: BulkOperationRequest`.
- **Spec lines quoted:** `04-optimisation.md:278-279` as amended in this slice (the T-text of the maintainer's (by delegation) entry "2026-10-12 03:07:15 BST", copied from `to-lead.md`), and the lead's from-lead entry "2026-10-12 03:05:42 BST" (DP-2 = spec compliance).

### Task 2 — the reds, by their cause (`packages/model-schema/tests/test_rate_tables.py`, at the base model code)

- **Red 2** (`test_the_bulk_operation_request_refuses_a_server_set_field`) and the parse test: `ImportError` (`BULK_OPERATION_REQUEST_ADAPTER` does not exist).
- **Red 3** (`test_a_bulk_operation_decimal_parameter_refuses_a_float`, four parametrisations): `Failed: DID NOT RAISE ValidationError` (a bare `Decimal` takes a float). 6 failed, 66 passed in total at the base.
- **Red 1** (field order) is a guard, green at the base; its **planted reversal** `class UpliftTableOperation(BulkOperationBase, UpliftTableRequest)` fails: `assert ['kind', 'par…to', 'result'] == ['applied_to'… 'parameters']`, `At index 0 diff: 'kind' != 'applied_to'`. Reverted. The chosen form `(UpliftTableRequest, BulkOperationBase)` keeps `applied_to, result, kind, parameters`.
- **Acceptance 5** (stored bytes; literals from a run at the base `249670fe`) is green at the base and after; its planted `PlainSerializer(lambda v: format(v, 'e'))` on `percentage` fails: `'…"percentage":"1.0e-1"}}' == '…"percentage":"0.10"}}'`. Reverted.

### Task 3 — the reds (`backend/tests/test_api_rate_tables.py`), before the route change

- **Red 4** (`test_bulk_operation_refuses_a_server_set_field`): `assert 201 == 422`, by its cause (the open body ignores `applied_to`).
- **Red 5** (`test_bulk_operation_refuses_a_json_number_for_a_decimal_parameter`): red, but not at 201 as the plan expected. After Task 2 the service's own `*Parameters.model_validate` already refused the float, so the response was a 422 `VALIDATION_FAILED` titled "Invalid bulk operation parameters" with no field error naming `percentage`; the test failed on that assertion (`any(e["field"].endswith("percentage"))` false). The route change turns it green by giving the refusal its field path at the boundary. **Against the base (the lead's from-lead order, 2026-10-12):** the same test file run once against `origin/main` `249670fe`'s code (a scratch detached worktree at that commit with only this branch's `test_api_rate_tables.py`, through `run-small.sh`, on this slice's database) gives `assert 201 == 422` for Red 5 (`{"percentage": 0.1}` is accepted and recorded, a 201 with the new version), as for Red 4; Red 6 gives `KeyError: 'discriminator'`. So the plan's premise holds on main: the route accepts a JSON float today. The scratch worktree was removed.
- **Red 6** (`test_bulk_operation_publishes_a_discriminated_request_and_a_typed_201`): `KeyError: 'discriminator'` (an open object). Green with `body: BulkOperationRequest` and `response_model=RateTableVersion`; no `Body(discriminator=)` needed.
- Existing bulk tests: `git diff origin/main -- backend/tests/test_api_rate_tables.py` removes no line.

### Task 4 — contracts

`generate-contracts.py` writes `docs/contracts/openapi/generated.json`, the new `schemas/generated/bulk-operation-request.schema.json` and `schemas/generated/rate-table-version.schema.json`; nothing else. The `rate-table-version` hunk is only the four decimal fields (`UpliftTableParameters.percentage`, `UpliftByFilterParameters.percentage`, `FloorAndCapParameters.floor` and `.cap`), each `anyOf: [number, string]` becoming `{"type": "string", "pattern": "^-?[0-9]+(\\.[0-9]+)?$", "description": "Exact decimal as a string; never a binary float (FR-10)."}`; `base_level` is unchanged. The stale-list test went red by its cause before the two pending entries were removed: `AssertionError: no longer untyped, remove from the 2xx lists: [('POST', '/api/v1/rate-tables/{slug}@{version}/bulk-operation', '201')]`. After removal `test_contracts.py` passes (171 passed, 2 skipped), `--check` exits 0, `pnpm generate:api` and `type-check` exit 0, and `grep -c 'pending FD-1366 Part B' backend/tests/test_contracts.py` prints `3`.

### Breaking-caller sweep at the head (03:06:12 item 2)

The two predicates, verbatim, now print 14 and 1 hits. The one new hit against the base's 13 is the slice's own Red 5 body in `backend/tests/test_api_rate_tables.py` (`{"percentage": 0.1}`), which posts a float on purpose and asserts the 422. **No other bulk-operation body sends a number; nothing else converts.**

### Integers (the maintainer's (by delegation) entry "2026-10-12 03:08:30 BST", item 3)

`DecimalStr` refuses a Python `float` and still accepts an `int` (`model_schema/money.py` `_reject_float`), while the published schema is string-only. An integer is exact, so accepting it violates nothing R2 protects; this is lenient input, not drift in what is stored. No FD.

### Write-set addition (audit-docs scope registration)

The new generated `docs/contracts/schemas/generated/bulk-operation-request.schema.json` cannot carry a header, so `audit-docs.py` checks 30 and 35 failed naming it (run at the branch head before the fix, under `flock -w 1800 /tmp/slots/gate-2`). Registered as every earlier generated schema was (LG-1405, `seed-from-model-request` precedent): the literal path joins `_CONTRACT_ARTIFACT_PATHS` in `scripts/audit-docs.py`, and `tests/test_audit_docs_ids.py` `non_markdown` goes 83 to **84** (83 read from the committed assertion at `249670fe`, +1 here). Neither file is in PL-1667's write set; neither is touched by `origin/sl-1548-wk675-s6-sandbox` (`git diff --name-only origin/main...` over `audit-docs`, `test_audit_docs_ids`, `contracts`, `rating.py`, `rate_tables.py`, `test_contracts` prints nothing). If another slice merges first with the same bump, the count is re-measured on the merged tree. **Accepted** by the lead as a precedent-based widening (`LG-1405`, the `seed-from-model-request` registration), in the lead's from-lead order of 2026-10-12 after the 05:0x report; the lead flags it to the maintainer at the ACK.

## PRs

- Not yet opened; the lead's merge-turn mint resolves the working id.
