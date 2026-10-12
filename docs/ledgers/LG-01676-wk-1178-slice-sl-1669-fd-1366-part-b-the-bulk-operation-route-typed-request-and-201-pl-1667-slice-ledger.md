---
id: LG-1676
family: ledger
title: WK-1178 slice SL-1669 — FD-1366 Part B for the bulk-operation route, a discriminated request body and a typed 201 (PL-1667), slice ledger
status: closed                 # active → closed (§1.2a)
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

# LG-1676 — WK-1178 slice SL-1669: the bulk-operation route, a typed request and a typed 201

*(Minted 2026-10-12 as LG-1676 from working id 9877, reserved by the lead; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

**GO:** the lead's from-lead entry "2026-10-12 04:53:47 BST" (GO SL-1669; the ledger's working id 9877, minted as LG-1676). Authority for the scope: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-12 02:58:33 BST" (DP-0 = (b); the bulk-operation request and 201 only), "2026-10-12 03:06:12 BST" (DecimalStr; the breaking-caller sweep), "2026-10-12 03:07:15 BST" (the 04 :278 T-text) and "2026-10-12 03:08:30 BST" item 3 (integers stay accepted); `RL-1670` on main.
**FALLBACK (02:58:33 condition 3):** if `SL-1548` merges before this slice, the maintainer rules S5's path.
**MERGE-ACK:** not yet given.
**Audit:** written 2026-10-12 by auditor-sl1669, section "Audit" below; the verdicts are proposals, the lead decides.

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

The new generated `docs/contracts/schemas/generated/bulk-operation-request.schema.json` cannot carry a header, so `audit-docs.py` checks 30 and 35 failed naming it (run at the branch head before the fix, under `flock -w 1800 /tmp/slots/gate-2`). Registered as every earlier generated schema was (LG-1405, `seed-from-model-request` precedent): the literal path joins `_CONTRACT_ARTIFACT_PATHS` in `scripts/audit-docs.py`, and `tests/test_audit_docs_ids.py` `non_markdown` goes 83 to **84** (83 read from the committed assertion at `249670fe`, +1 here). Neither file is in PL-1667's write set; neither is touched by `origin/sl-1548-wk675-s6-sandbox` (`git diff --name-only origin/main...` over `audit-docs`, `test_audit_docs_ids`, `contracts`, `rating.py`, `rate_tables.py`, `test_contracts` prints nothing). If another slice merges first with the same bump, the count is re-measured on the merged tree. **Accepted** by the lead as a precedent-based widening (`LG-1405`, the `seed-from-model-request` registration), in the lead's from-lead entry "2026-10-12 05:03:49 BST"; the lead flags it to the maintainer at the ACK.

### Gate — head `15439b9d29a71fd4b8e09567e1b99935a55fe1c5`

Full two-half gate, 2026-10-12 05:04:46 to 05:55:21 BST, under `flock /tmp/slots/gate-1` with `handover/slot-preflight.sh` sourced, on this slice's own database; granted by the lead for `b3efad52`, and the lead's message to this seat confirmed the grant covers `15439b9d` (three docs-only commits on top; code unchanged). Evidence, durable: `~/gi-pricing-plan.local/scratch/sl1669/` (`sl1669-gate.out` and `logs/`; local, not in the repository).

| stage | rc |
|---|---|
| ruff | 0 |
| mypy | 0 |
| import_linter | 0 |
| pytest | 1 |
| audit_docs | 1 |
| req_coverage | 0 |
| contracts `--check` | 0 |
| fe_install, fe_generate, fe_lint, fe_types, fe_test, fe_build | 0 |

- **audit_docs:** one failure, check 31, `gap in the full allocation between 1672 and 9877`: this ledger's then-unminted working id 9877 (now LG-1676). Quoted as the gate printed it.
- **pytest:** 13 failed, 5744 passed, 6 skipped. All 13 are that same gap: twelve run `scripts/audit-docs.py` on the real tree and assert exit 0 (the log carries the check-31 line in each), and `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity` reports `[(1672, 9877)]`. No route, model-schema, contracts or frontend test failed.


### Merge of main and the re-check (the mint turn)

The lead's from-lead entry "2026-10-12 05:56:06 BST" accepted the gate as check-31-only and ordered the mint turn. `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a` (carrying SL-1548 / S6, #1291) was merged into the branch with a merge commit, no rebase. **One conflict, in `docs/INDEX.md` only** (a generated file: both sides had added rows). It was resolved by regenerating it (`python3 scripts/doc-index.py`), not by hand, and no marker is left. Nothing else conflicted. Re-checks after the merge, small ones through `handover/run-small.sh`: `generate-contracts.py --check` rc 0 (49 contracts match); `pnpm --dir frontend generate:api` rc 0 and `git status --short` clean of tracked files; `type-check` rc 0; `lint` rc 0; `pytest -q` over `backend/tests/test_api_rate_tables.py`, `backend/tests/test_contracts.py`, `packages/model-schema/tests/test_rate_tables.py` and `tests/test_audit_docs_ids.py` (`-k 'bulk or contracts or rate_tables or non_markdown'`): 311 passed, 2 skipped; `ruff check .`: all checks passed; `mypy`: no issues in 239 source files.

### Gate evidence, durable

`/tmp/sl1669-gate.out` and the gate's log directory (`/tmp/tmp.lqQlkPZKKZ`) are copied to `~/gi-pricing-plan.local/scratch/sl1669/` (`sl1669-gate.out`, `logs/`), local and not in the repository. The 13 pytest failures, by name (every one is the check-31 gap `1672 → 9877`):
`tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`; `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`; `tests/test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree`; `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`; `tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec`; `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`; `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`; `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`; `tests/test_register_lint.py::test_check_29_note_carries_the_residue_line`; `tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count`; `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`; `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`; `tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci`.

## PRs

- #1293, "feat(rating): SL-1669 — type POST bulk-operation's request and 201, DecimalStr parameters (FD-1366 Part B; WK-1178; PL-1667, LG-1676)", opened 2026-10-12 at head `01ed71b1ddc9e86c003ca4e4f320f27ba915e66e`. Merge commit: recorded at merge.

## Audit

Auditor seat `auditor-sl1669`, 2026-10-12. **Range:** `origin/main...origin/sl-1669-wk1178-bulk-op-typing`, PR #1293 head `70e59ed5350628032daba5c357b6329c0cf6fa8d` (19 files, `git diff --stat`). **Tree read:** a detached worktree at that head. No full suite was run (gate-1 held by SL-1622); every check below is a read, a grep, a python read of the generated JSON, or a `merge-base`. Authority relied on: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-12 02:58:33 BST", "03:06:12 BST", "03:07:15 BST", "03:08:30 BST" item 3; the lead's from-lead entries "05:03:49 BST" (widening) and "05:56:06 BST" (gate accepted as check-31-only); `RL-1670`.

### Acceptance table (PL-1667 Acceptance 1–9)

| # | Item | Evidence read | Proposed verdict |
|---|---|---|---|
| 1 | typed request and 201 published | `backend/tests/test_api_rate_tables.py` `test_bulk_operation_publishes_a_discriminated_request_and_a_typed_201` asserts `discriminator.propertyName == "kind"`, `len(oneOf) == 4`, 201 `$ref` ends `/RateTableVersion`. PL-1667's own `python3 -c` command, run on the head's `generated.json`, prints the `kind` discriminator (four-entry mapping to the `*Request` schemas) and `{'$ref': '#/components/schemas/RateTableVersion'}` | delivered, tested |
| 2 | both guard entries gone, sub-graph entries stay | `git grep -c 'pending FD-1366 Part B' backend/tests/test_contracts.py` prints `3`; the only `bulk-operation` hit in the file is the `ONE_SIDED_SLUGS` line `:83`, in neither pending list | delivered, tested |
| 3 | server-set field refused; float refused; breaking callers | Red 4 `test_bulk_operation_refuses_a_server_set_field` (422, `VALIDATION_FAILED`, a field error ending `applied_to`); Red 5 `…_refuses_a_json_number_for_a_decimal_parameter` (body `0.1`; 422; field error ending `percentage`); `test_a_bulk_operation_decimal_parameter_refuses_a_float` (model level); `test_the_bulk_operation_request_refuses_a_server_set_field` (`extra_forbidden`). Integer line present ("Integers", item 3 of 03:08:30). Sweep: see "Breaking-caller sweep" below | delivered, tested |
| 4 | record field order pinned | `test_a_bulk_operation_record_keeps_its_field_order` asserts `["applied_to", "result", "kind", "parameters"]`, four parametrisations; planted reversal recorded in Task 2 | delivered, tested |
| 5 | stored bytes do not move | `test_a_bulk_operation_record_dumps_the_bytes_it_dumped_before_the_request_models` compares `model_dump_json()` with literals "from origin/main 249670fe"; planted `PlainSerializer` red recorded | delivered, tested (the literals' provenance is the ledger's word; not re-derived at the base) |
| 6 | existing behaviour holds | `git diff origin/main...HEAD -- backend/tests/test_api_rate_tables.py`: 50 insertions, 0 removed lines | delivered, tested |
| 7 | no hand-written shape; no drift | `bulk-operation-request` is in `GENERATED_SHAPES` (`BULK_OPERATION_REQUEST_ADAPTER`); no hand-written request shape in `backend/src/app/api/rate_tables.py`, whose hand check and `dict` body are deleted. `--check` rc 0 and the frontend regeneration are the ledger's (Task 4 and the mint-turn re-check); not re-run here | delivered, tested (rc is the executor's, unreproduced) |
| 8 | `rate-table-version.schema.json` moves only in the four decimal fields | `git diff origin/main...HEAD` on that file: four hunks, each `anyOf [number, string]` → `{description, pattern, title, type: string}`, titles Cap, Floor, Percentage, Percentage; no other line | delivered, tested |
| 9 | gate green on the merge tree | Not met as written: the gate was at `15439b9d`, pytest rc 1 and audit_docs rc 1, both only check 31 (see "Gate"). The head carries a main merge after that gate | deferred, owner the lead: green only after `#1292` merges and the gate or CI is re-read on the merge tree |

No requirement is "not started". FR-233, FR-451 and FR-10 each have the tests named above.

### Reds by cause (item 2 of the brief)

Read against the ledger's quoted outputs, not re-run (heavy; DB):
- Red 4 `assert 201 == 422` — the cause the red claims (open body ignores `applied_to`). Matches.
- Red 5 — the ledger records that the red at Task 3 was **not** the plan's 201: after Task 2 the service's own `*Parameters.model_validate` already gave a 422 without a field error. The ledger then proves the plan's premise against `origin/main` `249670fe` (201, the float accepted). That is the right record of both causes; accepted. Note the test turns green at the boundary by giving the refusal its field path.
- Red 6 `KeyError: 'discriminator'` — the cause claimed; also run against `249670fe`.
- Stale-list test: `AssertionError: no longer untyped, remove from the 2xx lists: [('POST', '…/bulk-operation', '201')]`. Matches the plan's named cause.

### Breaking-caller sweep (item 3)

Both predicates run verbatim at the head: first 14 hits, second 1. The single bulk-operation hit is `backend/tests/test_api_rate_tables.py:871`, the slice's own Red 5 body (`{"percentage": 0.1}`), posted on purpose. The other 14 are the non-bulk hits the ledger names. Nothing else converts; matches the LG.

### T-text (item 4)

`docs/specs/04-optimisation.md:278` at the head equals the maintainer's (by delegation) "03:07:15 BST" T-text, **except** that the entry says "Delivered with SL 9868" and the file says "Delivered with SL-1669". That is the mint re-pointing of a working id, which the plan's Task 1 text already writes as `SL-1669`; accepted, noted. The line lands in `720f4ab6` (`git show --stat`: `04-optimisation.md`, `model_schema/__init__.py`, `rating.py`, `test_rate_tables.py`), the same commit as the `DecimalStr` code; it is the only commit on the range touching `04`.

### Write set (item 6)

Beyond PL-1667's write set, all explained: `scripts/audit-docs.py` (+1 line) and `tests/test_audit_docs_ids.py` (83 → 84) — the lead's "05:03:49 BST" widening; `docs/INDEX.md` — generated; `docs/plans/PL-01667…` (status `draft` → `active`, the activation); `docs/ledgers/LG-1676`, `docs/roadmap.md` (SL-1669 row `closed`), `docs/findings/register.md` (FD-1366 dated line), `docs/specs/03-rating-engine.md` (the §5.1 clause) — plan Tasks 0, 1, 5. No unexplained file.

### Closing acts (item 7)

SL-1669 row `closed` with a dated line (it says the audit is pending; this section discharges that). LG-1676 `status: closed`. PL-1667 stays `active`, as the executor chose; the plan's header comment gives `draft → active → superseded | retired`, so `active` is the last live state for a delta whose slice has closed. FD-1366 register line: the route is typed, remaining routes named, the finding stays active as the plan requires. Every SHA the LG cites (`01ed71b1`, `15439b9d`, `249670fe`, `b3efad52`, `c66e6489`) satisfies `git merge-base --is-ancestor <sha> HEAD`, exit 0.

### Gate (items 7 and 8)

Raw logs `~/gi-pricing-plan.local/scratch/sl1669/logs/*.rc`: ruff, mypy, import_linter, req_coverage, contracts, and the six frontend stages are rc 0; pytest and audit_docs are rc 1. `pytest.log:10206`: `13 failed, 5744 passed, 6 skipped`. `audit_docs.log:883`: `check 31: gap in the full allocation between 1672 and 9877`. The 13 `FAILED` lines all belong to the nine test files the ledger names, none to a route, model-schema or contracts test (a filter for every other file name prints 0). So the gate is "check 31 only", not green. That gap is the executor's then-unminted `LG-9877`, now `LG-1676`; the mint turn has a main merge on top and the re-checks listed in the "Merge of main" section, which were small selections, not a gate. **CI** at 05:03 UTC on the head: `check` and `no-session-links` success; `specification audit` and `ruff · mypy · import-linter · pytest` still in progress when this was written. Not called green; the lead reads the finished runs, and per the brief a check-31-only red is expected until `#1292` merges.

### Findings

1. **LOW — `tests/test_audit_docs_ids.py:` (the comment above `assert len(non_markdown) == 84`)** still reads "named in LG-9877". The ledger was minted as LG-1676 and every other citation was re-pointed. A living-file comment, so a one-word fix (`LG-1676`) in a correcting commit. Not a closure blocker.
2. **LOW — unreproduced evidence:** Acceptance 5's literals and the `generate-contracts.py --check` / frontend rc values rest on the ledger and the executor's logs; this audit read the tests' asserts and the generated artefacts, not the base-tree dump or a fresh `--check`. If the lead wants it, one `--check` run under a free slot closes it.
3. **INFO — the roadmap row's "Closed … on the lead's merge" line was written before the merge**, as the plan's L1 (a') allows; it stays true only if the merge follows. No action.

No HIGH or MEDIUM finding. No finding is filed as an `FD-`.

### Proposed verdicts (the lead decides)

- Acceptance 1–8: delivered and tested. Acceptance 9: **deferred, owner the lead** — re-read the finished CI runs on the head after `#1292` merges and after any main re-merge.
- Slice closure: a clean audit on the above, subject to the lead's reading of CI and to Finding 1 (optional).
- Not proposed: any change to the maintainer-owned items (`04` §4.4 correction is already ruled; the integer leniency is ruled at "03:08:30 BST" item 3).
