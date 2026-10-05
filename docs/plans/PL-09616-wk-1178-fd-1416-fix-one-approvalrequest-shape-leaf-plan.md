---
id: PL-9616
family: plan
kind: leaf
title: WK-1178 — the FD-1416 fix, one ApprovalRequest shape, generated and typed on every approval route (FR-9, FR-451, FR-351, FR-357): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: cdaaa57345cb765f96034ce1ec2733c338f1c3cd
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1416, FD-1335, PL-1392, PL-1408, SL-1409, SL-1367, PL-1364, RL-1301, RL-878, ADR-704, OQ-649, RL-1263, PL-1371]
---

# PL-9616 (working id) — WK-1178: the FD-1416 fix, one `ApprovalRequest` shape, leaf plan

Filed under working id 9616 (this plan) and slice working id 9615 (its `SL-` row under
WK-1178 in [`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead
(`handover/eta.md`, "5 Oct 15:29:48"). Ordered by the maintainer (by delegation), entry
"2026-10-05 15:28:26 BST — Wave results: D1 = (c); D2 PL 9624 DPs; D3 PL 9629 DP-6 + plan the 2
missing G2 items; C1′ is FD 9995 (no new finding); FD 9619 noted" (`to-lead.md`, a local channel
file, so cited by its header), item D3:

> "YES, plan the two G2 needs with NO plan as the NEXT prep items: the FD-1416 fix (ApprovalRequest
> defined three ways; HOLD on reading its responses) and the FD-1244 and FD-1245 rulings (WF-699 D4
> vs FR-261; E2 vs FR-257). One planner, one DM; docs only."

and slot (1) of the entry "2026-10-05 15:28:42 BST — Corrections noted (57-line gap; one-gate
effective now); C1′ = FD 9995, NOT a new finding; 4 free slots assigned": "(1) a planner for the
FD-1416 fix". `PL-1371` §4 row 5 already places this slice: "FD 9752 one ApprovalRequest shape | 1 |
a DM rules the decision enum; after 3 (`approvals.py`)", Appendix A node `"1178-FD9752"`
(dependency `["1178-FD1356"]`, lane B).

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item marked red first is seen red, by
> its cause, before the code that turns it green), `fastapi-service` (Task 3's routes),
> `contract-schema` and `contract-guard` (Tasks 2, 4 and 5: the generated schema, the retired
> hand-authored file, the new guard), `python-package` (Task 2), `spec-change` (Task 6, only
> where a ruling carries text), `dev-commands` (the two-half gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s conventions before the first step. The executor is spawned from
> `.claude/roles/executor.md`.

## Goal

One `ApprovalRequest` definition, the `model-schema` class, is what every approval route
returns and what `docs/contracts/` publishes. The four routes `FD-1416` names —
`GET /api/v1/approval-requests/{request_id}`, `POST /api/v1/approval-requests`,
`POST …/{request_id}/decide` and `POST …/{request_id}/withdraw` — return it as a typed 2xx, and
leave `FD-1335` Part B's open-object list. The decision enum, `workspace_id`, `environment`,
the evidence and checklist fields, `comment`'s nullability and the withdrawal fields are each
what the decision-maker rules (DP-1 to DP-6), applied to the model, the service, and `06` §4.3's
example in one change. The hand-authored `docs/contracts/schemas/approval-request.schema.json` is
retired (DP-8). A guard fails when an authored-only slug in `ONE_SIDED_SLUGS` has a `model-schema`
class that nothing compares, proven on broken input (DP-9). This discharges `FD-1416` (MEDIUM,
owner WK-1178, deadline before the P2 exit demo), whose HOLD is lifted by DP-1's ruling, not by
this plan.

**Architecture:** `platform/approvals.py`'s `to_dict` is replaced by a constructor that returns
`ApprovalRequest`, so the shape is built in one place and a drift fails at construction. The
routes declare that class as their response (DP-10). `scripts/generate-contracts.py` gains the
`approval-request` slug, which publishes the generated schema the frontend client is built
from. No route changes its status codes, request bodies or permission checks.

**Tech Stack:** Python 3.12, FastAPI + Pydantic v2, SQLAlchemy 2 async, pytest; the OpenAPI
generator (`scripts/generate-contracts.py`) and `pnpm --dir frontend generate:api`.

**Spec, finding and rulings:**
- `docs/findings/FD-01416-approvalrequest-is-defined-three-ways-that-disagree-and-a-hand-authored-contract-sits-under-docs-contracts.md`:
  §"Remedy" items 1–4 and §"Maintainer's decision (2026-10-01 10:38:52 BST)", whose
  "Discharge, all of" list **is this slice's scope**. Its register row is
  `docs/findings/register.md:285`.
- [`../specs/06-governance.md`](../specs/06-governance.md) §4.3 (`:458`, example `:460-488`),
  §5.1's decide row (`:561`), FR-351 (`:92`), FR-352 (`:93`), FR-357 (`:98`).
- [`../specs/00-overview.md`](../specs/00-overview.md) FR-9 (`:220`);
  [`../specs/07-platform.md`](../specs/07-platform.md) FR-451 (`:182`); ADR-704.
- `docs/contracts/README.md` (`:17`, `:43-52`: the Phase 0 carve-out and "the generated one is
  authoritative").

## The maintainer's decisions this plan rests on, quoted

From `FD-1416` §"Maintainer's decision (2026-10-01 10:38:52 BST)", recording the entry headed
"2026-10-01 10:38:52 BST — FD 9752 (#1066 @24933167, the approval request's three disagreeing
shapes): MEDIUM, owner WK-1178, deadline BEFORE the P2 exit demo, plus a consumer hold":

> "**HOLD:** no slice ships code that reads a response of any of the four `to_dict` routes until a
> DM rules the enum. Typing the request bodies is unaffected."

> "**Discharge, all of:** (1) a DM rules per field which shape is right (`CLAUDE.md` §0), the enum
> first, with verbatim `06` text if the spec moves; the contract and the spec example agreeing is
> not proof. (2) One shape: the `model-schema` model, the hand-authored schema retired ("generated
> wins"), the four routes' 2xx typed by `$ref`. (3) The F27 class: the `ONE_SIDED_SLUGS` reason
> fixed, and a guard that fails when a listed slug has a `model-schema` class, proven on broken
> input."

## Status

`draft`. **Every decision point below is OPEN.** DP-1 to DP-6, DP-8, DP-9 and DP-10 are the
decision-maker's (`CLAUDE.md` §0: a spec/code disagreement, and design choices `FD-1416` leaves
open); DP-7 widens the finding's route list and is the maintainer's (by delegation). No decision
maker is assigned to them yet: the maintainer's 15:28:26 entry assigns "one DM" to the FD-1244 and
FD-1245 rulings, and `PL-1371` §5 item (9) planned "one DM session for FD 9752's enum and FD-1244
and FD-1245". The plan moves to `active` only through a separate activation PR, after every
activation need below holds; that PR carries the `SL-` row's status flip and this plan's.

### Activation needs, in order

1. **`SL-1409` merged: MET** at `origin/main` `cdaaa573` (#1157, 2026-10-05). It moved `Decide`
   from `backend/src/app/api/approvals.py` into `model_schema/approvals.py` (`:64`), added
   `decide_and_carry`, and rewrote `decide_request`'s handler, whose return this slice edits. The
   two were serial (`RL-1263` item 4; `PL-1371` §5 rule 4: "WK-674 S2 / FD-1356 fix / WK-673 S5 /
   FD 9752 (`approvals.py`)"), and every cite below is read after that merge.
2. **A decision-maker ruling on DP-1 to DP-6, DP-8, DP-9 and DP-10, merged and minted**, and the
   maintainer's (by delegation) dated line on DP-7. Where the ruling and this plan differ, the
   ruling wins and the planner aligns the plan before its first merge. The HOLD lifts at DP-1's
   ruling.
3. **Contention re-checked at the dispatch tree** against §"Write set, and its contention": in
   particular `PL 9683` (working id; same Work, `GENERATED_SHAPES`), and `SL-1367` (if merged, its
   untyped-2xx lists gain approval entries this slice removes).
4. **Task 0 prints `TOTAL unparseable=0`** on every `gipricing*` database at dispatch (the rows
   the new shape would refuse to return).
5. **The maintainer's agreement**, and **the lead's go in a separate activation PR**.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means the named test was run and failed **for the stated cause** before the code that turns it
green; a failure with the right status and a different cause is a plan defect
([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger, with the failure
line as printed. Items carry the recommended option of each open DP; the ruling replaces them
where it differs.

1. **Characterisation first (Task 1).** Before any shape changes, a key-set and value test pins
   what the routes emit at the base tree: the 12 keys of `APPROVAL_REQUEST_KEYS`
   (`backend/tests/test_deployment_route_types.py:550`) on `GET …/{request_id}` and on each item
   of `GET /api/v1/approval-requests` (the two routes no test pins today), and the stored decision
   values `approve`, `reject`, `request_changes` read back from `decide`. It passes on the base
   tree (it is a characterisation, not a red) and is then edited, deliberately, by Task 3, so the
   diff shows every key that changes.
2. **Every route's 2xx is an `ApprovalRequest`, red first.** `test_every_approval_route_returns_an_approval_request`
   (new, `backend/tests/test_approval_request_shape.py`) calls the four routes, and the list route
   under DP-7 (a), and passes each body (each list item) to `ApprovalRequest.model_validate`. Red
   first on the base tree: `workspace_id` is missing and `environment` is refused by
   `extra="forbid"` (`FD-1416` §"Field by field", consequence 1).
3. **The OpenAPI 2xx is a `$ref`, red first.** In `docs/contracts/openapi/generated.json`, the
   2xx schema of each of the four routes is `{"$ref": "#/components/schemas/ApprovalRequest"}`
   (the list route: `Page`'s `items` is that `$ref`, DP-7 (a)).
   `test_the_approval_routes_publish_the_approval_request_ref` (same module). Red first: at
   `cdaaa573`, `ApprovalRequest` has 0 hits in `generated.json`.
4. **`FD-1335` Part B's list loses the four.** In `ROWS` of
   `backend/tests/test_deployment_route_types.py` (`:61-64` at `cdaaa573`), the `POST
   /api/v1/approval-requests` and `…/withdraw` rows change their `response` from `None` to
   `"ApprovalRequest"`; the guard's own run is the red first (on the base tree it fails naming
   the route as an open object). If `SL-1367` has merged, its untyped-2xx exception list loses the
   four approval routes in the same commit, and `FD-1335`'s list-is-empty condition is measured and
   recorded in the ledger.
5. **The decision enum, as ruled (DP-1).** `test_a_decision_reads_back_as_the_ruled_value`
   decides once with each of the three values and asserts the `decisions[].decision` the response
   carries. Under DP-1 (a), these are the code's values, and the test is green at the base tree
   (the code is unchanged); it pins them against any later rename. Under DP-1 (b) it is red first.
6. **One definition (DP-8 (a)).** `docs/contracts/schemas/approval-request.schema.json` is
   deleted; `docs/contracts/schemas/generated/approval-request.schema.json` exists;
   `uv run python scripts/generate-contracts.py --check` exits 0; `ONE_SIDED_SLUGS["approval-request"]`
   gives a generated-only reason that cites `FD-1416`, and `test_every_one_sided_slug_is_declared`
   (`test_contracts.py:2657`) passes.
7. **The F27-class guard, proven on broken input (DP-9 (a)).**
   `test_no_authored_only_slug_hides_a_model_schema_class` (new, in `test_contracts.py`) fails
   when an authored-only key of `ONE_SIDED_SLUGS` names a slug whose `model-schema` class exists
   and the slug is not in `SHIPPED_NOT_COMPARED` with its owning record. Three proofs, each in
   the ledger: (i) on the base tree, with the new map holding only the four exemptions of DP-9, it
   fails naming `approval-request` and nothing else; (ii) a positive control: removing
   `rate-table` from the map makes it fail naming `rate-table`, so the slug-to-class lookup is not
   vacuous; (iii) after Task 4 it passes.
8. **`06` §4.3 agrees with the shape.** The ruling's texts are applied verbatim (Task 6). Under
   DP-1 (a): `grep -cF '"decision": "approved"' docs/specs/06-governance.md` prints `0` and
   `grep -cF '"decision": "approve"' docs/specs/06-governance.md` prints `1`.
9. **The frontend client is regenerated and nothing is hand-written.** `pnpm --dir frontend
   generate:api` produces an `ApprovalRequest` type; `git grep -n 'ApprovalRequest' -- frontend/src ':!frontend/src/api/generated'`
   prints nothing new from this slice (no consumer is added here; `PL 9629`'s journey is the first).
10. **The full two-half gate** (`CLAUDE.md` §11) exits 0 on the merge tree, run through the
    gate-runner under one gate slot (`RL-1263`; one full gate at a time, `RL 9620`, working id,
    #1162).
11. **The write set.** `git diff --stat origin/main...HEAD` names only paths in §"Write set", and
    the ledger records it.

## Global Constraints

- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2; `00`
  FR-9). After this slice the approval request has one definition; the frontend reads it only
  through the generated client (`CLAUDE.md` §3).
- **`docs/contracts/` generated outputs are regenerated, never hand-edited** (`CLAUDE.md` §2,
  FR-451). The one hand edit is the deletion of the hand-authored file under DP-8 (a), which
  `docs/contracts/README.md`'s carve-out sanctions ("the generated one is authoritative").
- **No route changes its status code, request body, permission or error codes.** Request bodies
  are already typed (`ApprovalSubmission`, `ApprovalWithdrawal` by `PL-1392`; `Decide` by
  `PL-1408`); this slice types responses only.
- **The approval guard is untouched** (`RL-1301` A.4): no change to `approval_decision()`, its
  sites or `_carry_to_the_artifact`.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): Acceptance 2, 3, 4 and
  7 are each red first.
- **Shared files** (`RL-1263` option (c), and its two dated registry amendments): two concurrent
  build slices may not both change the same existing function, class, spec section or policy
  table. `ONE_SIDED_SLUGS` is exempt for key-disjoint edits; `__all__` for appended names;
  generated files are regenerated.
- **No spec text is written by this slice unless a ruling carries it verbatim** (Task 6).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `00` | FR-9 | One `ApprovalRequest` definition, generated into JSON Schema, OpenAPI and TypeScript; the hand-authored twin retired | `req("FR-9")` on Acceptance 2, 6, 7 |
| `07` | FR-451 | The committed OpenAPI carries the routes' 2xx as a `$ref`; `--check` exits 0 | `req("FR-451")` on Acceptance 3 |
| `06` | FR-351 | The decision values the uniform lifecycle records, as DP-1 rules | `req("FR-351")` on Acceptance 5 |
| `06` | FR-357 | The withdrawal is carried as DP-6 rules (`withdrawn_reason` under (a)) | `req("FR-357")` on the withdraw case of Acceptance 2 |

`06` FR-352 (evidence and checklist at submission) is **not** in scope: under DP-4 (a) the shape
describes what exists, and FR-352's checklist and evidence limbs stay with WK-677 (the requirements row of the
`### WK-677` section of `docs/roadmap.md` lists FR-352).

### Task 0 at planning time (measured, not asserted)

Read at `origin/main` `cdaaa57345cb765f96034ce1ec2733c338f1c3cd` (after #1157), by reading the owning modules:

- **S1, `to_dict`** (`backend/src/app/platform/approvals.py:672-697`): 12 keys; it emits
  `environment` and no `workspace_id`; `decision` is the stored string; `approvers_recorded` is
  counted from `approve` decisions. Unchanged since `FD-1416`'s mint tree `caa4e411`.
- **S2, `ApprovalRequest`** (`packages/model-schema/src/model_schema/approvals.py:405-431`):
  `frozen=True`, `extra="forbid"`; requires `workspace_id`; no `environment`; the
  `_recorded_matches_decisions` validator (`:423-431`). `DecisionKind` (`:58-61`) is `approve`,
  `reject`, `request_changes`. Exported from `model_schema/__init__.py` (`:446`), so no `__all__`
  edit is needed.
- **S3**, `docs/contracts/schemas/approval-request.schema.json`: `required` names
  `evidence_bundle` and `checklist`; `decisions[].decision` is
  `enum ["approved", "rejected", "changes_requested"]`; `decisions[].comment` is required with
  `minLength` 1.
- **The spec disagrees with itself.** `06` §5.1's decide row (`:561`) writes
  "`approve` / `reject` / `request_changes` + comment (FR-353/355)", the code's values; only the
  §4.3 example (`:483`, `"decision": "approved"`) and S3 write the past participles.
- **A fifth route emits S1 and is in neither list.** `list_requests` (`GET
  /api/v1/approval-requests`, `backend/src/app/api/approvals.py`, `-> Page[dict[str, Any]]`)
  builds each item with `_detail`, which returns `service.to_dict`. `FD-1416` names four routes,
  and `FD-1335` Part B lists the same four (`FD-1335` lines `:141`, `:144-146`); the list route's
  items are an open object inside `Page`, which neither sweep reached. Raised as DP-7.
- **The route set after `SL-1409`.** `service.to_dict` is still called by `_detail`,
  `submit_for_approval`, `decide_request` and `withdraw_request`
  (`backend/src/app/api/approvals.py:89`, `:133`, `:244`, `:329`), and by nothing else:
  `git grep -n 'to_dict' -- backend/src scripts examples`, filtered to approvals, prints those four
  and the definition and `__all__` entry in `backend/src/app/platform/approvals.py` (`:672`, `:67`).
- **No consumer.** `git grep -n -i 'approval-requests\|ApprovalRequest\b' origin/main -- frontend/src ':!frontend/src/api/generated'`
  prints nothing.
- **The `FD-1335` "temporary exclusion list"** is, at `cdaaa573`, two `ROWS` entries with
  `response=None` in `backend/tests/test_deployment_route_types.py` (`:61-64`; the rule `:42-44`),
  pinned by key set (`APPROVAL_REQUEST_KEYS`, `:550`;
  `test_the_two_changed_approval_routes_return_exactly_the_declared_keys`, `:605`). `SL-1367`
  (`PL-1364`) is `draft` and its untyped-body guard is not on `main`.
- **`ArtifactRef` admits every stored type.** `ARTIFACT_TYPES` includes `deployment`
  (`model_schema/refs.py:32`), so a deployment approval request's `artifact_ref` parses.
- **`workspace_id` precedent.** The Slice-2 typed responses carry it: `model_schema/deployments.py:105`
  and `:169`.
- **The F27 class at this tree.** Authored-only keys of `ONE_SIDED_SLUGS` whose PascalCase class
  exists in `model_schema`: `approval-request` (`ApprovalRequest`, `approvals.py:405`),
  `dislocation-run` (`DislocationRun`, `dislocation.py:116`), `rate-table` (`RateTable`,
  `rating.py:702`), `rating-algorithm` (`RatingAlgorithm`, `rating.py:375`), `rating-version`
  (`RatingVersion`, `rating.py:138`). `dossier`, `gipp-check`, `monitoring` and
  `optimisation-run` have none. Predicate: `git grep -n "^class <Name>\b" origin/main -- packages/model-schema/src`
  for each name.
- **Not measured:** whether any stored `approval_requests` row would fail the new shape (an
  `artifact_ref` the parser refuses, a `status` outside `ApprovalStatus`). No database was queried
  at planning time; Task 0 measures it.

### Write set, and its contention (`RL-1263`)

"Edited" means an existing definition changes; "added" means a new definition in an existing
file. Rows marked *(DP-n x)* exist only under that option.

| Path | Change | Other slices touching it | Consequence |
|---|---|---|---|
| `backend/src/app/platform/approvals.py` | edited: `to_dict` replaced by `to_approval_request(row, decisions) -> ApprovalRequest` (`:672-697`), and its `__all__` entry (`"to_dict"`, `:67`) | none in flight (`SL-1409` merged at `cdaaa573` and left `to_dict` as it was) | none |
| `backend/src/app/api/approvals.py` | edited: the return of `_detail`, `submit_for_approval`, `decide_request`, `withdraw_request`, and `list_requests` *(DP-7 a)*; their response declarations (DP-10) | none in flight (`SL-1409`'s edits merged at `cdaaa573`) | none; Task 0 re-reads the file at dispatch |
| `packages/model-schema/src/model_schema/approvals.py` | edited: `ApprovalRequest` (`:405-431`) gains `environment` *(DP-3 a)*; `ApprovalDecision` (`:394-402`) only if DP-5 or DP-1 changes it | none in flight (`SL-1409`'s `Decide`, `:64`, merged) | none |
| `scripts/generate-contracts.py` | edited: `GENERATED_SHAPES` (`:38`) gains `"approval-request": "ApprovalRequest"` | **PL 9683** (working id, #1140; same Work, WK-1178) appends `"rating-version-create"` | **serial with PL 9683**: `GENERATED_SHAPES` is not on `RL-1263`'s registry list, so same-Work concurrency fails `RL 9620`'s condition (a) |
| `docs/contracts/schemas/approval-request.schema.json` | **deleted** *(DP-8 a)* | **PL 9649** (working id, #1152) **reads** `:53-54` for the `custom_objective_not_approved` spelling (its Acceptance 9) | no shared write. If this slice merges first, PL 9649's executor re-anchors that citation to `ModelFlag`; the lead names it in both dispatch records |
| `docs/contracts/schemas/generated/approval-request.schema.json`, `docs/contracts/openapi/generated.json` | added; regenerated | every contract-changing slice | registry: regenerate on the merge base, never hand-merge |
| `backend/tests/test_contracts.py` | edited: the value of `ONE_SIDED_SLUGS["approval-request"]` (`:97`); added: `SHIPPED_NOT_COMPARED` and `test_no_authored_only_slug_hides_a_model_schema_class` *(DP-9 a)* | **PL 9683** appends key `rating-version-create`; **PL 9713** (working id, #1131) edits `UNTYPED_REQUEST_PENDING` only if `SL-1367` has landed | `ONE_SIDED_SLUGS`: key-disjoint, exempt under the 2026-10-03 21:11:06 amendment (one slice's change to one key's value). The two additions are new definitions; the lead's dispatch record names them under `RL-1263` `:100` |
| `backend/tests/test_deployment_route_types.py` | edited: `ROWS` (`:61-64`, two `response` values); `APPROVAL_REQUEST_KEYS` (`:550`) if DP-2 adds `workspace_id`; the module docstring (`:9-13`) | none in flight | none |
| `backend/tests/test_validation_rule_approval.py` (added by #1157) | edited: `test_the_decide_response_keeps_its_key_set` (`:804`), to the ruled key set | none in flight | none |
| `backend/tests/test_approval_request_shape.py` | added (Acceptance 1, 2, 3, 5) | none | none |
| `backend/tests/test_contracts.py` SL-1367 lists | edited only if `SL-1367` has merged: the four approval 2xx removed | **PL 9713** removes `POST /rating-algorithms` from the request list under the same condition | different entries of one list: the lead's dispatch record names both entries, or the two serialise |
| `docs/specs/06-governance.md` §4.3 (`:458-488`) | edited with the ruling's texts, verbatim (Task 6) | none in flight (the agent sweep of the nine plans found none writing `06`) | none |
| `frontend/src/api/generated/` | regenerated (VCS-ignored) | every slice | not committed |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry |

**Not written:** `backend/src/app/db/models.py` (no migration under DP-3 (a), DP-6 (a)), any
`frontend/src` source file, `docs/contracts/README.md`, `06` §5.1.

### Contention with the in-flight plans, pair by pair

Read at each PR's head on 2026-10-05 (the plans' own write-set tables, quoted by line), against
`RL-1263` (`:89`, `:100`, `:110-115`) and `RL 9620` (working id, #1162 @`e1e85bd1`, `:130-139`:
same-Work concurrency only with (a) file sets resolved and (b) no plan dependency either way).

| Plan | Work / slice | Shared paths with this slice | Plan dependency | Verdict |
|---|---|---|---|---|
| `PL-1408` / #1157 | WK-1178 / `SL-1409` | `api/approvals.py` (`decide_request`), `model_schema/approvals.py`, `test_validation_rule_approval.py`, generated | none either way; both change `decide_request` | **serialised, and resolved: #1157 merged at `cdaaa573` before this plan's first merge** (activation need 1, met) |
| PL 9716 / #1127 | WK-673 / `SL-1391` | `generated.json` (registry) | none | **may run concurrently** (different Works; registry only) |
| PL 9688 / #1145 | WK-673 / SL 9685 | none | none | **may run concurrently** |
| PL 9689 / #1138 | WK-673 / `SL-1387` | `generated.json` (registry). It edits the hand-authored `dislocation-run.schema.json`, which DP-9 (a) lists as exempt; it writes neither `test_contracts.py` nor `generate-contracts.py` (its `:388-389`) | none | **may run concurrently** |
| PL 9649 / #1152 | WK-673 / SL 9647 | generated (registry); it **reads** `approval-request.schema.json:53-54` | a citation, not an output | **may run concurrently** (different Works, as the maintainer's D1 requires for PL 9649); the second to merge re-anchors the citation |
| PL 9683 / #1140 | WK-1178 / SL 9678 | `GENERATED_SHAPES` (not exempt); `ONE_SIDED_SLUGS` (key-disjoint, exempt); generated | none | **serialise** (same Work; `RL 9620` (a) not met on `GENERATED_SHAPES`) |
| PL 9728 / #1113 | WK-1178 / SL 9727 | none (`api/score.py` is `FD-1335`'s `/score` half, not this one) | none | **may run concurrently** (`RL 9620` (a) and (b) both hold) |
| PL 9713 / #1131 | WK-675 / SL 9711 | `test_contracts.py` (`UNTYPED_REQUEST_PENDING`, only if `SL-1367` has landed); generated | none | **may run concurrently** if `SL-1367` is not merged at dispatch; otherwise the two entries are named in both dispatch records or the slices serialise |
| PL 9624 / #1161 | WK-1178 / SL 9626 | none (`examples/fremtpl2/` only; its "Not written" `:321-323`) | none | **may run concurrently** (`RL 9620` (a) and (b) both hold) |
| PL 9629 / #1164 | WK-1178 / SL 9625 | none | **PL 9629 consumes this slice** (its activation need 13) | **serialise: this slice first** |

### Size

Small to medium: about one executor day. Six tasks after the preconditions, no migration, no
frontend source change. One full two-half gate run (one gate slot). No NFR measurement.

## Decision points

All ten are **OPEN**. The recommendation is the planner's; the owner rules.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | The decision enum (the HOLD's subject) | (a) the code's values `approve` / `reject` / `request_changes`: `DecisionKind`, the stored rows, the `Decide` body, `06` §5.1 (`:561`) and `06`'s glossary entry **Approval Decision** (`:67`, "An approve / reject / request-changes act") already use them; `06` §4.3's example (`:483`) is amended; (b) the contract's `approved` / `rejected` / `changes_requested`: a data migration of `approval_decisions.decision`, `DecisionKind`, every caller and test | **(a)**: the spec's interface table already agrees with the code, the values are verbs for a decision and `ApprovalStatus` keeps the participles for states, and (b) migrates governed records for no consumer (exposure 0, `FD-1416`'s ruling). Text: in `06`, the find string `"decision": "approved"` (`grep -cF` = 1 at `cdaaa573`) becomes `"decision": "approve"` | decision-maker | Tasks 1, 6; the HOLD |
| **DP-2** | `workspace_id` on the wire | (a) emitted: the service adds it; (b) not emitted: S2 loses it, or a separate wire class | **(a)**: the row stores it, S2 requires it, and the Slice-2 typed responses carry it (`deployments.py:105`, `:169`) | decision-maker | Tasks 2, 3 |
| **DP-3** | `environment` | (a) added to S2 as `environment: str \| None = None` (the deployment branch writes and reads it, `RL-1301`, `PL-1306`); (b) no longer emitted | **(a)**: it is real state of a deployment approval request; (b) hides it | decision-maker | Task 2 |
| **DP-4** | `evidence_bundle`, `checklist`, `expedited`, `expedited_reason`, `flags`, `flag_overrides` (S3 only) | (a) not fields of the shape now; `06` §4.3 gains a dated note that the example illustrates FR-352's full submission, whose checklist and evidence limbs are WK-677's (the `### WK-677` section of `docs/roadmap.md`), and that evidence lives with the Deployment Request (`RL-1301` A.2); (b) added to S2 as optional and always `null` | **(a)**: a field nothing carries is a promise the API breaks; FR-352 is not built. Text anchor for the note: after the example's last line `"approvers_required": 2, "approvers_recorded": 1` (`grep -cF` = 1) and its closing fence, before `### 4.4 \`Dossier\` structure` (`grep -cF` = 1) | decision-maker | Tasks 2, 6 |
| **DP-5** | `decisions[].comment` nullability | (a) nullable, as S1 and S2; (b) required and non-empty, as S3 (and `06` §5.3's approval detail, "decision panel with mandatory comment", `:640`) | **(a) for the response shape**: stored rows hold `null`, and a required field would make every such read fail. Whether `decide` must *demand* a comment is a request-body question on `Decide` (`PL-1408`'s), outside this slice; the ruling can name an owner for it | decision-maker | Task 2 |
| **DP-6** | Withdrawal fields | (a) `withdrawn_reason` (S1, S2); the actor and time are on the withdraw's Audit Event; (b) S3's `withdrawn: {by, at, reason}`, which needs two new columns and a migration | **(a)**: no stored `by`/`at` exists, and the audit trail already records them | decision-maker | Task 2 |
| **DP-7** | The list route `GET /api/v1/approval-requests`, whose items are S1 too and which neither `FD-1416` nor `FD-1335` Part B lists | (a) in scope: `Page[ApprovalRequest]`; (b) out: the list stays `Page[dict]` and a new finding owns it | **(a)**: the items come from the same `_detail`, so typing four routes and not the fifth leaves one shape in two forms | **the maintainer (by delegation)**: it widens the finding's scope | Tasks 1, 3 |
| **DP-8** | The hand-authored file | (a) deleted; the slug becomes generated-only and `ONE_SIDED_SLUGS["approval-request"]`'s value changes to a reason citing `FD-1416`; (b) rewritten to the ruled shape and moved to `COMPARED_SLUGS`, so the comparison walkers run on it | **(a)**: the maintainer's discharge item (2) says "retired (\"generated wins\")"; nothing remains to drift; and (a) is a one-key value change, which the 2026-10-03 21:11:06 amendment exempts, while (b) removes the key and edits `COMPARED_SLUGS`, which is not exempt | decision-maker | Task 4 |
| **DP-9** | The F27-class guard. Read literally ("fails when a listed slug has a `model-schema` class"), it would also fail on four other slugs at `cdaaa573`: `dislocation-run` (owned by `PL-1267`, WK-673 Slice 4), `rate-table`, `rating-algorithm`, `rating-version` (register F27) | (a) a named map `SHIPPED_NOT_COMPARED = {slug: owning record}` holding those four; the guard fails for any other authored-only slug with a class, and for a map entry whose slug no longer has one; (b) guard `approval-request` only (does not reach the class); (c) fix the four here (scope growth; collides with PL 9689 on `dislocation-run`) | **(a)**: it closes the class without taking the four, and each exemption names who owns it | decision-maker; the maintainer confirms it meets discharge item (3) | Task 5 |
| **DP-10** | How the 2xx is typed | (a) `response_model=ApprovalRequest`, the service returning the model, so FastAPI validates outbound; (b) `responses={2xx: {"model": ApprovalRequest}}` with the `dict` kept (the `SL-1367` form, chosen there for `/score`'s latency, NFR-502) | **(a)**: approvals are not a hot path, and (a) makes a drift fail at construction, where (b) only documents it | decision-maker | Task 3 |

## Tasks

### Task 0: Preconditions and containment (no code)

- [ ] **Step 1:** Confirm activation needs 1–3: #1157's squash `cdaaa573` is an ancestor of
  `origin/main`; the ruling is minted (`docs/rulings/`); re-read every plan of §"Contention" at its
  current head and record any change to its write set.
- [ ] **Step 2:** Re-measure §"Task 0 at planning time" at the dispatch tree, by symbol:
  `to_dict`, `ApprovalRequest`, `ROWS`, `APPROVAL_REQUEST_KEYS`, `GENERATED_SHAPES`,
  `ONE_SIDED_SLUGS["approval-request"]`, and the five classes of the F27 class.
- [ ] **Step 3: The data check.** On every `gipricing*` database, load each `approval_requests`
  row with its decisions and build the ruled shape from it; print one line per database and a
  last line `TOTAL unparseable=<n>`. **`n > 0` is a STOP** to the lead with the rows, because
  under DP-10 (a) such a row would answer 500. The script lives in the ledger, not the repository.

### Task 1: The characterisation (Acceptance 1)

**Files:** Create `backend/tests/test_approval_request_shape.py`.

- [ ] **Step 1:** Pin the key set of `GET …/{request_id}` and of each list item against
  `APPROVAL_REQUEST_KEYS` (import it; do not copy it), and the three decision values read back
  from `decide`. Run it on the base tree: it passes. Commit.

### Task 2: The model, as ruled (Acceptance 2, red first)

**Files:** Modify `packages/model-schema/src/model_schema/approvals.py`; extend
`backend/tests/test_approval_request_shape.py`.

- [ ] **Step 1: Red.** Add `test_every_approval_route_returns_an_approval_request` (Acceptance 2).
  Run it: it fails on `workspace_id` (missing) and `environment` (extra). Record both lines.
- [ ] **Step 2:** Apply the ruled fields to `ApprovalRequest` and `ApprovalDecision`. Under the
  recommendations: `environment: str | None = None` added (DP-3 (a)); nothing else changes. The
  validator `_recorded_matches_decisions` stays.

### Task 3: The service and the routes (Acceptance 2, 3, 4)

**Files:** Modify `backend/src/app/platform/approvals.py`, `backend/src/app/api/approvals.py`,
`backend/tests/test_deployment_route_types.py`, `backend/tests/test_validation_rule_approval.py`.

- [ ] **Step 1: Red.** Add `test_the_approval_routes_publish_the_approval_request_ref`
  (Acceptance 3), and change the two `ROWS` responses to `"ApprovalRequest"` (Acceptance 4). Run
  both: they fail naming the untyped 2xx.
- [ ] **Step 2:** Replace `to_dict` with:

  ```python
  def to_approval_request(
      row: ApprovalRequestRow, decisions: list[ApprovalDecisionRow]
  ) -> ApprovalRequest:
      """The one place an approval request becomes its published shape (FD-1416)."""
      return ApprovalRequest(
          id=row.id,
          workspace_id=row.workspace_id,
          artifact_ref=row.artifact_ref,
          artifact_type=row.artifact_type,
          environment=row.environment,
          submitted_by=row.submitted_by,
          submitted_at=row.submitted_at,
          change_summary=row.change_summary,
          status=row.status,
          approvers_required=row.approvers_required,
          approvers_recorded=sum(1 for d in decisions if d.decision == DecisionKind.APPROVE.value),
          decisions=tuple(
              ApprovalDecision(
                  approver_id=d.approver_id, decision=d.decision, at=d.at, comment=d.comment
              )
              for d in decisions
          ),
          withdrawn_reason=row.withdrawn_reason,
      )
  ```

  The fields follow the ruling; the sample carries the recommendations.
- [ ] **Step 3:** In `api/approvals.py`, each of the four handlers (and `list_requests` under
  DP-7 (a)) returns the model and declares it (DP-10 (a): `response_model=ApprovalRequest`;
  `Page[ApprovalRequest]` for the list). `_detail`'s return type follows.
- [ ] **Step 4:** Edit the key-set pins deliberately: `APPROVAL_REQUEST_KEYS` gains
  `workspace_id` (DP-2 (a)); #1157's `test_the_decide_response_keeps_its_key_set` follows; Task
  1's characterisation follows. Each edit is one line in the diff, which is the record of the
  change.
- [ ] **Step 5:** If `SL-1367` has merged, remove the four approval routes from its untyped-2xx
  exception list in this commit (Acceptance 4).

### Task 4: One definition (Acceptance 6; DP-8 (a))

**Files:** Modify `scripts/generate-contracts.py`, `backend/tests/test_contracts.py`; delete
`docs/contracts/schemas/approval-request.schema.json`; regenerate `docs/contracts/`.

- [ ] **Step 1:** Append `"approval-request": "ApprovalRequest"` to `GENERATED_SHAPES`.
- [ ] **Step 2:** Delete the hand-authored file; change the value of
  `ONE_SIDED_SLUGS["approval-request"]` (key unchanged, in place) to a generated-only reason, e.g.
  `"generated-only since FD-1416 — the hand-authored Phase 0 draft retired, generated wins"`.
- [ ] **Step 3:** `uv run python scripts/generate-contracts.py` and commit the outputs;
  `--check` exits 0; `test_every_one_sided_slug_is_declared` and
  `test_every_eligible_schema_is_compared` pass.

### Task 5: The F27-class guard (Acceptance 7; DP-9 (a))

**Files:** Modify `backend/tests/test_contracts.py`.

- [ ] **Step 1: Red, on the base of this task** (the hand-authored file still present, i.e. run
  it before Task 4 Step 2 or on a scratch revert of it). Add:

  ```python
  #: Authored-only slugs whose `model-schema` class has shipped and that nothing compares yet,
  #: each with the record that owns closing it (FD-1416, DP-9). Not a place to park a new one.
  SHIPPED_NOT_COMPARED: Final[dict[str, str]] = {
      "dislocation-run": "PL-1267 (WK-673 Slice 4 generates and compares it)",
      "rate-table": "register F27",
      "rating-algorithm": "register F27",
      "rating-version": "register F27",
  }


  def _class_name(slug: str) -> str:
      return "".join(part.capitalize() for part in slug.split("-"))


  def test_no_authored_only_slug_hides_a_model_schema_class() -> None:
      import model_schema

      authored_only, _ = _one_sided_slugs()
      hidden = sorted(
          s for s in authored_only
          if hasattr(model_schema, _class_name(s)) and s not in SHIPPED_NOT_COMPARED
      )
      stale = sorted(s for s in SHIPPED_NOT_COMPARED if s not in authored_only)
      assert not hidden, f"authored-only but shipped in model-schema: {hidden}"
      assert not stale, f"SHIPPED_NOT_COMPARED names a slug that is no longer authored-only: {stale}"
  ```

  Run it: it fails naming `["approval-request"]` only. Record the line (proof (i)). The
  authored-only predicate is the file's own `_one_sided_slugs()` (`test_contracts.py:2640` at
  `cdaaa573`), the one `test_every_one_sided_slug_is_declared` uses, so the two tests cannot
  disagree on which slugs are authored-only.
- [ ] **Step 2: Positive control (proof (ii)).** Remove `rate-table` from the map on a scratch
  edit; the test fails naming `rate-table`; restore. Record.
- [ ] **Step 3 (proof (iii)).** After Task 4, it passes.

### Task 6: The spec texts, verbatim from the ruling

**Files:** Modify `docs/specs/06-governance.md` §4.3 only.

- [ ] **Step 1:** Apply each text the ruling carries, by its find string, after checking
  `grep -cF` = 1 at the dispatch tree. Write no text the ruling does not carry. Run
  `python3 scripts/audit-docs.py`.

### Task 7: The gate and the ledger

- [ ] **Step 1:** The full two-half gate (Acceptance 10) through the gate-runner, under one gate
  slot; record each rc and the tree.
- [ ] **Step 2:** In the slice's `LG-` ledger: Task 0's output, every red of Acceptance 2, 3, 4
  and 7 with its printed line, the three proofs of Acceptance 7, and `git diff --stat
  origin/main...HEAD` against §"Write set" (Acceptance 11).

## Hand-off

1. The lead mints PL 9616 and SL 9615 at the merge turn, and dispatches only after §"Activation
   needs" hold, in a separate activation PR.
2. **What this unblocks in `PL 9629`** (working id, #1164, the P2 exit demo's scripted journey):
   its **activation need 13** ("`FD-1416` fixed (FD 9752; one ApprovalRequest shape; WK-1178,
   deadline before the P2 exit demo) | E5, E6, E8: the script reads approval responses | **no
   plan** on `main` or in an open PR", its `:161`), and through it the steps whose Needs column
   names 13: **C5** (approve the GBM via `/approval-requests/{id}/decide`, `:274`), **E5**
   (`:287`), **E6** (`:288`), **E8** (`:290`) and **Deploy** (`:292`); and its **Task 4 Step 1**,
   `_phase_e` (`:421-423`), "reading approval responses only through the shape `FD-1416`'s fix
   publishes". Its rehearsal checklist row 4 (`:470`) checks this slice's squash is on `main`.
3. When this slice merges, `FD-1416`'s discharge items (2) and (3) are met; item (1) is met by
   the ruling. The auditor closes the finding.
4. Follow-ons not built here, each with an owner: FR-352's checklist and evidence at submission
   (WK-677, under DP-4 (a)); whether `decide` must demand a comment (DP-5; the ruling names the
   owner); the four `SHIPPED_NOT_COMPARED` slugs (their named owners).

## Self-review

1. **Coverage of `FD-1416`'s discharge, item by item.** (1) a per-field ruling: DP-1 to DP-6,
   DP-1 first, the `06` text by find string (Task 6). (2) one shape, the hand-authored file
   retired, the four 2xx typed by `$ref`: Tasks 2–4, Acceptance 2, 3, 6. (3) the `ONE_SIDED_SLUGS`
   reason fixed (Task 4 Step 2) and a guard proven on broken input (Task 5, Acceptance 7). The
   Remedy's characterisation-first (item 3) is Task 1; `FD-1335`'s list (item 4) is Acceptance 4.
2. **Every design choice the finding leaves open is a DP with an owner**, and so are the three
   this plan found: the list route (DP-7), the four other F27-class slugs (DP-9) and the typing
   form (DP-10).
3. **Repository literals checked at `cdaaa573`** (first read at `809a3794`, re-read after #1157 merged): every line cite in §"Task 0 at planning time"
   and §"Write set"; the `06` find strings (`grep -cF` = 1 each, recorded in DP-1 and DP-4);
   `ApprovalRequest` exported (`__init__.py:446`); `Page` (`backend/src/app/api/pagination.py:48`).
4. **What was not executed.** No database was queried (Task 0 Step 3 does it). The Python samples
   were **not** run: Task 3's depends on the ruling; Task 5's reuses
   the file's own `_one_sided_slugs()` and was not executed either.
   A sample that does not run as written is a plan defect to report, not to work around.
5. **Type consistency.** `to_approval_request(row, decisions)` is defined in Task 3 Step 2 and
   used by every handler in Step 3; `SHIPPED_NOT_COMPARED` and `_class_name` are defined and used
   in Task 5 only.
