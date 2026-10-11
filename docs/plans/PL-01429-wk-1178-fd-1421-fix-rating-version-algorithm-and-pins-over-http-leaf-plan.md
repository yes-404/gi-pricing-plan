---
id: PL-1429
family: plan
kind: leaf
title: WK-1178 — FD-1421 fix, POST /rating-versions declares the algorithm and the pins (FR-237, FR-240, FR-223, FR-440, FR-451): leaf plan
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: planner
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1300, FD-1297, CR-838, PL-1371, PL-1408, SL-1409, SL-1391, RL-1263, FR-223, FR-237, FR-240, FR-440]
---

# PL-1429 — WK-1178: the FD-1421 fix, a Rating Version's algorithm and pins over HTTP, leaf plan

Filed under PL-1429 (this plan) and slice SL-1430 (its `SL-` row under WK-1178 in
[`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead (`eta.md`, the rows of
"5 Oct 13:14:56"). The lead mints both at the merge turn. The finding is **FD-1421** (working id,
draft PR #1130, branch `fd-9708`, head `11f87e26`), and the ruling is **RL-1428** (working id,
draft PR #1133, branch `dm-9695-rv-pins-http`, read first at head `68096376` and re-read at
`614ad96b` (12:23:39Z), which records DP-1 and DP-2 below). Neither is minted, so both are
cited unhyphenated and kept out of `relates:` (check 32).

**Ordered by** the maintainer's (by delegation) entry in `~/gi-pricing-plan.local/channel/to-lead.md` of
2026-10-05 13:12:56 BST, item 15, as the lead relayed it in the brief
`~/gi-pricing-plan.local/handover/brief-plan-fd9708-2026-10-05.md`: *"RL 9695: OPTION (a).
FD-1421 is HIGH, owner WK-1178, deadline before the exit demo. Spawn its planner now."* The
severity, owner and option are the maintainer's (by delegation). This plan did not read the channel entry itself.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `fastapi-service` (Task 3), `contract-schema` and
> `contract-guard` (Task 2's typed body and the regenerated contract), `spec-change` (Task 5,
> ruling texts only), `dev-commands` (the two-half gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

`POST /api/v1/rating-versions` accepts the algorithm version and every pin a Rating Version
needs (`03` FR-237), so a client can create a version over HTTP that then compiles
(FR-239/FR-240). This is WF-699 step C1 as written:
*"`POST /rating-versions` — declares the algorithm version and every pin: rate tables, peril
structure, reference tables."* It unblocks G2 (the maintainer's ruling of 2026-10-05 13:05:42
BST, by delegation: WF-699 A–E and deploy **over HTTP**), whose step C1 today ends in 422
`VALIDATION_FAILED` and whose C2 can then only compile a version that something outside HTTP
pinned.

**Architecture:** the request body becomes a `model-schema` type, `RatingVersionCreate`, next
to `RatingVersion` in `model_schema/rating.py`. It reuses `ArtifactRef`, `Pins` and
`ModelReferenceMode`, so no shape is written twice (`CLAUDE.md` §2). Its validator refuses a ref
of the wrong artifact type in `algorithm_ref` or in any `pins` list (422, RL-1428 T1). The
service `create_rating_version` takes the three new fields and writes them on the row. It does
not resolve them: resolvability and maturity stay with compile (FR-240, RL-1428 T3), with one
exception that DP-1 decides, FR-223's mode check (RL 9758 item 2). The route-local class in
`backend/src/app/api/models.py` is removed. The demo seed passes its algorithm and pins through
the same service call, and stops writing them on the ORM row.

**Tech Stack:** Python 3.12, FastAPI + Pydantic v2, SQLAlchemy 2 async, PostgreSQL 16, pytest;
`scripts/generate-contracts.py` for `docs/contracts/`. No frontend source changes: the generated
client picks the type up, and no hand-written frontend call creates a Rating Version
(`grep -rn "rating-versions" frontend/src --include=*.ts --include=*.vue` finds only the two
reads in `frontend/src/api/ratingVersions.ts` and a router link, at `caa4e411`).

**Spec, finding and rulings:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): FR-237 (`:134`), FR-240
  (`:137`), FR-239, FR-223 (`:109`), §4.3 and its Phase 1b note (`:430-436`), §5.1's create row
  (`:908`) and its owned-code list;
- [`../workflows/WF-00699-approved-models-to-approved-rating-version.md`](../workflows/WF-00699-approved-models-to-approved-rating-version.md)
  C1 (`:70`) and C4–C5 (`:73-74`);
- [`../specs/07-platform.md`](../specs/07-platform.md) FR-440 (`:156`), FR-451, FR-403;
- FD-1421), §"Evidence" and §"Disposition";
- RL-1428) at `614ad96b`, §"Ruled", §"The exact texts" T1–T3, §"Acceptance";
- RL 9758 (working id, draft PR #1061, branch `dm-9758-fr223-check-point`), §"Ruled" item 2 and
  §"What it obliges", bullet *"Item 2's future route"*.

## Status

`draft`. **The three blocking decision points are decided**, each sent to the lead when found:
DP-1 (a), DP-2 (a) and DP-3 (a), by the maintainer's (by delegation) entry headed *"2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap findings"* in `~/gi-pricing-plan.local/channel/to-lead.md`, items 25, 26 and 27, read by this planner in that
file. RL-1428 at `614ad96b` already carries DP-1's T3 amendment and DP-2's predicate. DP-4 (a)
and DP-5 (a) are accepted, with conditions, by the maintainer's (by delegation) entry headed *"2026-10-05 13:29:05 BST — DECISIONS 32 and 33 (PL 9683, the FD 9708 fix)"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 33. RL-1428's texts govern at dispatch: where its minted text differs from the
head cited here, the minted text wins and the dispatch record names each difference
([`README.md`](README.md) rule 4).

**Pre-mint fix F1 (2026-10-05 15:21 BST)**, ordered by the maintainer (by delegation) in
the entry headed *"2026-10-05 15:15:11 BST — F2 (RL-1263's "from different Works"): OPTION (i), amend RL-1263 by a dated RL, with conditions; F1, F3 and the stale RL 9633 sentence as you set them"* in `~/gi-pricing-plan.local/channel/to-lead.md`: *"F1: a pre-mint fix on #1140 (it is unmerged, so this is authoring)."*
`MODEL_REFERENCE_MODE_INCONSISTENT` is already in `03` §5.1's owned-code list (`03:936`, read at
`caa4e411` and at `origin/main` `809a3794`; there since `4a8729ee`, 2026-08-28), and the list
continues after it. The add this plan gave Task 5 Step 2 would have listed the code twice. Row
0.11, Acceptance 8 and 14, the write set, the S3 contention row, Task 3 Step 6 and Task 5 Step 2
are corrected. The code is still registered in no code (`git grep MODEL_REFERENCE_MODE_INCONSISTENT
origin/main -- backend/src packages`: 0 hits at `809a3794`), so the `errors.py` append (Task 3
Step 5) and Task 5 Step 3's test stay. RL 9758 T1 on FR-223 (`:109`) is unchanged.
**The owned-codes serialisation with WK-673 S3** (dispatch-record item 2) was stated for one
reason: both slices append at the list's tail. With the add struck, this slice no longer
appends to that list, so the stated reason no longer holds. The serialisation stands until the
maintainer (by delegation) lifts it.

### Activation needs, in order

1. **FD-1421 and RL-1428 minted.** An unminted RL-1428 is an activation need, not a plan defect
   (the brief).
2. **DP-1 to DP-5 decided: met** (13:20:26 BST, items 25–27; 13:29:05 BST, item 33).
3. **This plan `active`**, by the lead's activation PR, which flips this plan and the `SL-` row.
4. **The lane.** The maintainer's (by delegation) priority rule (13:12:56 BST, as the brief relays it): *a HIGH
   finding that blocks G2 takes the first build lane that frees once its plan is active.*
   The maintainer's (by delegation) entry headed *"2026-10-05 13:29:05 BST — DECISIONS 32 and 33 (PL 9683, the FD 9708 fix)"* in `~/gi-pricing-plan.local/channel/to-lead.md` applies it: **this fix goes first in lane C, and WK-675 S2 (PL 9713,
   working id) follows it there.** That order is also what the contention table below
   needs: this slice and S2 change adjacent rows of `03` §5.1 and the same §3.4 table.
5. **The dispatch GO** (the maintainer's GO check and the lead's go, in the activation PR).

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red
first" means the named test was run and failed **for the stated cause** before the code that
turns it green. A failure with the right status and a different cause is a plan defect
([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger, with the
failure line as printed. Tests live in the new module
`backend/tests/test_rating_version_create_pins.py`, run with
`uv run pytest -q backend/tests/test_rating_version_create_pins.py`.

1. **A version declared over HTTP compiles** (RL-1428 *Acceptance* bullet 1).
   `test_a_version_created_with_its_algorithm_and_pins_compiles_over_http`: `POST
   /api/v1/rating-versions` with `algorithm_ref` and a non-empty `pins` (one published reference
   table) answers 201, `GET .../{id}` returns both unchanged, and `POST .../{id}/compile` drives
   the `rating.compile` Job to `succeeded` with the pin in `resolved_payloads`. **Red at
   `caa4e411`:** the create answers 422 `VALIDATION_FAILED` whose `errors[]` hold
   `EXTRA_FORBIDDEN` on `algorithm_ref` and on `pins`. A 422 with any other `errors[].code` is a
   plan defect.
2. **The omitting body keeps today's behaviour** (control, green at `caa4e411` and after).
   `test_a_version_created_without_algorithm_or_pins_is_refused_at_compile`: 201, then the Job
   fails `RATING_VERSION_UNPINNED`.
3. **A malformed algorithm ref is refused and writes nothing** (RL-1428 *Acceptance* bullet 2).
   `test_an_algorithm_ref_of_another_type_is_refused`: `algorithm_ref` =
   `"model:motor-ad-frequency@7"` answers 422 `VALIDATION_FAILED`, with an `errors[]` entry on
   `algorithm_ref` whose code is `VALUE_ERROR`, and no `RatingVersionRow` with the request's slug
   exists. **Red at `caa4e411`:** the 422's entry is `EXTRA_FORBIDDEN`, not `VALUE_ERROR`.
4. **A malformed pin is refused and writes nothing.** `test_a_pin_of_another_type_is_refused`,
   parametrised over the four lists (`rate_tables` holding a `model` ref, `models` holding a
   `rate_table` ref, `reference_tables` holding a `rate_table` ref, `custom_objectives` holding a
   `model` ref): each is 422 `VALIDATION_FAILED`, `VALUE_ERROR` on `pins`, no row. **Red** as 3.
5. **An unknown ref is stored and refused at compile** (the brief's "unknown ref"; RL-1428
   T1 and T3: create does not resolve). `test_an_unknown_algorithm_is_refused_at_compile`:
   `algorithm_ref` = `"rating_algorithm:no-such-algorithm@1"` answers 201, and the Job fails
   `NOT_FOUND` (the resolver's refusal, `platform/rating_versions.py:456`). **Red at
   `caa4e411`:** 422 `EXTRA_FORBIDDEN`. Under DP-1 (a) this stays 201, because an algorithm that
   does not resolve cannot be mode-checked at create.
6. **Maturity is checked at compile only, and a recompile re-reads the declared pins**
   (RL-1428 *Acceptance* bullet 3; WF-699 C4–C5).
   `test_an_unapproved_model_pin_is_refused_at_compile_and_compiles_after_approval`: a fitted,
   **not approved** GBM in `pins.models` is created (201); the Job fails `PIN_NOT_APPROVED`;
   after `mark_approved` the same version recompiles to `succeeded`, and exactly one
   `RatingVersionRow` carries the slug. **Red at `caa4e411`:** 422 `EXTRA_FORBIDDEN`.
7. **A peril-structure pin is accepted and is FD 9995's tripwire** (DP-5 (a)).
   `test_a_peril_structure_pin_is_stored_and_compile_reports_no_resolver`: `pins.models` =
   `["peril_structure:motor-perils@1"]` answers 201 (FR-237's "Model/Peril Structure version per
   `model_call`"); the Job fails `NOT_FOUND` with the detail containing `has no backend table yet`
   (`platform/rating_versions.py:550-555`). FD 9995's fix changes this assertion in the commit
   that adds the resolver branch. **Red at `caa4e411`:** 422 `EXTRA_FORBIDDEN`.
8. **FR-223 at the pin write** (DP-1 (a), decided). `test_a_mode_mismatch_is_refused_at_create`:
   after `POST /api/v1/rating-algorithms` with `valid_algorithm()`
   (`backend/tests/test_rating_algorithms.py:64`, slug `motor-gb`, a `model_call` step with
   `mode: "exact"`), a create with `algorithm_ref` = `"rating_algorithm:motor-gb@1"` and
   `model_reference_mode` = `"approximation"` answers 422 `MODEL_REFERENCE_MODE_INCONSISTENT`
   naming step `s_rp`, and writes no row; the same body with `"exact"` answers 201. **Red at
   `caa4e411`:** 422 `VALIDATION_FAILED`, `EXTRA_FORBIDDEN`. Plus
   `test_model_reference_mode_inconsistent_is_registered_and_owned`: the code is in
   `RATING_ERROR_CODES` (`backend/src/app/errors.py:305`) and in `03` §5.1's owned-code list
   (RL 9758 *Acceptance* 3). Red at `caa4e411`: absent from `RATING_ERROR_CODES`; the owned-list
   half already holds (`03:936`). *(Corrected 2026-10-05, pre-mint fix F1; see §"Status".)*
9. **The request is the `model-schema` type** (RL-1428 *Acceptance* bullet 4; `CLAUDE.md` §2).
   `test_the_create_body_is_the_model_schema_type`: `app.api.models` defines no class named
   `RatingVersionCreate` of its own (`app.api.models.RatingVersionCreate is
   model_schema.RatingVersionCreate`), and the OpenAPI component `RatingVersionCreate` has the
   properties `algorithm_ref`, `pins` and `model_reference_mode`. **Red at `caa4e411`:** the
   identity is false (the route-local class at `api/models.py:271`).
10. **The contract is regenerated and published.** `uv run python scripts/generate-contracts.py
    --check` exits 0, `docs/contracts/schemas/generated/rating-version-create.schema.json`
    exists, and `uv run pytest -q backend/tests/test_contracts.py` passes (the slug is declared
    in `ONE_SIDED_SLUGS`). **Red first:** with the `GENERATED_SHAPES` entry added and the
    `ONE_SIDED_SLUGS` entry not yet added, `test_every_one_sided_slug_is_declared` fails naming
    `rating-version-create`.
11. **The creation is audited with what it pinned.**
    `test_the_creation_event_records_the_declared_pins`: the `rating_version.created` Audit
    Event's `after` holds `algorithm_ref`, `pins` and `model_reference_mode` as the request gave
    them. **Red at `caa4e411`:** `after` holds `status` and `model_ref` only
    (`platform/rating_versions.py:273`).
12. **No code outside tests and benches writes a pin onto the row** (RL-1428 *Acceptance*
    bullet 5, in the form DP-2 recommends). `grep -rnE "\.(algorithm_ref|pins)\s*=[^=]"
    --include=*.py examples/ backend/src/` prints nothing. **Red at `caa4e411`:** it prints
    `examples/fremtpl2/model.py:396` and `:397`. This is the predicate RL-1428 carries at
    `614ad96b` (DP-2, item 26); the minted record's text governs.
13. **The seed still works.** `uv run pytest -q backend/tests/test_demo_rating_evidence.py
    examples/fremtpl2/test_seed.py` passes, and the seeded `fremtpl2-demo` version's
    `rating_version.created` event carries the algorithm ref.
14. **Spec and code agree.** RL-1428 T1, T2 and T3 (and, under DP-1 (a), RL 9758 T1; the
    owned-code list already carries the code at `03:936` *(Corrected 2026-10-05, pre-mint fix F1; see §"Status".)*) are applied byte for byte in the commit that makes
    items 1–9 green; `python3 scripts/audit-docs.py` passes except check 31's expected working-id
    rows; the handler docstring no longer says "pins to a model" (RL-1428 *What it obliges*).
15. **The two-half gate is green** on the merge tree (`.claude/skills/dev-commands`), and
    `uv run python scripts/req-coverage.py` lists FR-237 with the new markers.

## Global Constraints

- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2):
  `algorithm_ref` is `ArtifactRef`, `pins` is `Pins`, `model_reference_mode` is
  `ModelReferenceMode` (`model_schema/rating.py:65-78`, `:136`), and the request is a
  `model-schema` class.
- **`pricing-core` is not touched.** Compile's checks and its refusal codes stay as they are
  (RL-1428: "Validation stays in one place (compile)").
- **Money and maths are untouched**; no pandas (`CLAUDE.md` §3).
- **The stored shape does not change**: `Pins`, `RatingVersion` and `RatingVersionRow` keep
  their fields. No migration (the columns exist; `_insert_version` writes them today,
  `backend/tests/test_rating_version_compile.py:86-110`).
- **No route is added**, and no pin is mutable after create: RL-1428 refused option (c), and
  the maintainer's (by delegation) DP-S2-3 decision (PL 9713, *"no re-pin (no route exists)"*) relies on it.
- **Effective dates are not in the create body.** RL-1428 T1 lists the body's fields, and
  `effective_from`/`effective_to` are not among them.
- **No spec text is written by this slice unless a ruling carries it verbatim** (Task 5). Any
  executor wording is a stop.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): Acceptance 1, 3–12
  are each red first, by cause.
- **Shared files** (`RL-1263`, `docs/process/delivery-process.core.json`
  `guards.parallelism.build_slices_across_works.no_shared_files`): two concurrent build slices
  may not both change the same existing function, class, spec section or policy table; the
  `generated` paths are regenerated, never hand-merged.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-237 | The algorithm version and every pin are declared at create over HTTP; a wrong-type ref is refused | `req("FR-237")` on Acceptance 1, 3, 4, 7, 9, 11 |
| `03` | FR-240 | Resolvability and maturity stay with compile; an unknown or unapproved pin is refused there, and a recompile re-reads the declared pins | `req("FR-240")` on Acceptance 5, 6 |
| `03` | FR-239 | A version created over HTTP compiles to a Bundle | `req("FR-239")` on Acceptance 1, 2 |
| `03` | FR-223 | The pin write refuses a mode mismatch with 422 `MODEL_REFERENCE_MODE_INCONSISTENT` | `req("FR-223")` on Acceptance 8 |
| `00` | FR-20 | Maturity is the compile-time gate, unchanged (Acceptance 6) | `req("FR-20")` on Acceptance 6 |
| `07` | FR-440 | Not changed. §4.3's note scoping Phase 1b is discharged by RL-1428 T2; FR-440 stays a Phase 1b seed requirement | none (spec text only) |
| `07` | FR-451 | `RatingVersionCreate` is regenerated into `docs/contracts/` | Acceptance 10 (contract test) |

Out of scope, named so no reader assumes it: FD 9995's resolver branch for `peril_structure`
(#980; Acceptance 7 is its tripwire); FD 9759 limbs 2 and 3 (the compile-site
`MODEL_REFERENCE_MODE_INCONSISTENT`, RL 9758, given to "S3"); the exit-demo script's C1 call
(`PL-1371` §3.8 row 7, which names this slice and FD 9995 as prerequisites, per RL-1428
*What it obliges*); `CR-838`'s FR-237 "delivered" line, which RL 9668 (working id, #1137) corrects to "partly
 delivered" (the maintainer's (by delegation) entry of 13:24:03 BST, item 1).

### Task 0 at planning time (measured, not asserted)

Read at `caa4e411`:

| # | Fact | Command or place | Result |
|---|---|---|---|
| 0.1 | The request model is route-local and closed | `sed -n '271,276p' backend/src/app/api/models.py` | `class RatingVersionCreate(BaseModel)`, `extra="forbid"`, `slug`, `dataset_version_id`, `model_ref` |
| 0.2 | No other `RatingVersionCreate` exists | `grep -rn RatingVersionCreate --include=*.py .` | `api/models.py:271`, `:1167` only |
| 0.3 | The service takes three fields | `sed -n '230,275p' backend/src/app/platform/rating_versions.py` | `slug`, `dataset_version_id`, `model_ref`; the audit `after` is `status` and `model_ref` |
| 0.4 | `Pins`' lists are bare `list[ArtifactRef]` | `model_schema/rating.py:65-78` | no per-list type constraint (DP-3) |
| 0.5 | `pins.models` holds a `model_call`'s `model_ref` **or** `peril_structure_ref` | `packages/pricing-core/src/pricing_core/rating/compile.py` `check_step_refs_pinned` (around `:565`) | so the admitted types of `pins.models` are `model` and `peril_structure` |
| 0.6 | The seed writes the pins on the row | `grep -rnE "\.(algorithm_ref\|pins)\s*=[^=]" --include=*.py examples/ backend/src/` | `examples/fremtpl2/model.py:396`, `:397` |
| 0.7 | RL-1428's own predicate already matches | `grep -rn "algorithm_ref\s*=\|\.pins\s*=" --include=*.py examples/ backend/src/` | the two seed lines **and** `platform/rating_versions.py:110`, `:113` (`to_schema`'s keyword reads), so it cannot print nothing (DP-2) |
| 0.8 | A body error renders as 422 `VALIDATION_FAILED` with `errors[].code` = the Pydantic type upper-cased | `backend/src/app/errors.py:466-493` | `extra_forbidden` → `EXTRA_FORBIDDEN`; a validator's `ValueError` → `VALUE_ERROR` |
| 0.9 | A failed compile Job carries the code in `JobRow.error["code"]` | `backend/src/app/worker/tasks.py:197-232`; `test_rating_version_compile.py:196` | as stated |
| 0.10 | The three RL-1428 find strings occur once each | `grep -c` on `Create a draft Rating Version with pins (FR-237) \|`, `build widens the shape with the full contract.`, `and the input contract. Nothing is unpinned. \|` in `docs/specs/03-rating-engine.md` | 1, 1, 1 (`:908`, `:436`, `:134`) |
| 0.11 | `MODEL_REFERENCE_MODE_INCONSISTENT` is in `03` §5.1's owned-code list and registered in no code | `grep -rn MODEL_REFERENCE_MODE_INCONSISTENT backend/src packages/*/src docs/specs/03-rating-engine.md` | `03:109` (FR-223's prose) and `03:936` (the owned-code list, which continues after it); no hit under `backend/src` or `packages/*/src`. *(Corrected 2026-10-05, pre-mint fix F1; see §"Status".)* The result read "only FR-223's prose at `03:109`", which was wrong at `caa4e411` too |
| 0.12 | The route is not a held approval route (FD 9752, working id; #1066, unmerged, would mint it as FD 1416) | the hold covers the four `to_dict` approval routes in `backend/src/app/api/approvals.py`; this route is in `api/models.py` and returns the typed `RatingVersion` | not held |
| 0.13 | No test file is shared with WK-675 S2 | S2 adds tests to `backend/tests/test_rating_versions.py` (PL 9713 Task 4); this slice adds a new module | disjoint |

### Write set, and its contention (`RL-1263`)

"Edited" means an existing definition changes; "added" means a new definition in an existing file.

| Path | Change | 
|---|---|
| `packages/model-schema/src/model_schema/rating.py` | added: `RatingVersionCreate`, directly after `RatingVersion` (`:138-170`); `RatingVersion` itself unchanged |
| `packages/model-schema/src/model_schema/__init__.py` | `RatingVersionCreate` appended to the import block and `__all__` |
| `backend/src/app/api/models.py` | removed: the route-local `RatingVersionCreate` (`:271-276`); edited: `create_rating_version` (`:1160-1185`: passes the three fields, docstring corrected); import of `RatingVersionCreate` from `model_schema` |
| `backend/src/app/platform/rating_versions.py` | edited: `create_rating_version` (`:230-275`: three keyword parameters, the row writes, the audit `after`; under DP-1 (a) the mode check) |
| `backend/src/app/errors.py` | *(DP-1 a)* `MODEL_REFERENCE_MODE_INCONSISTENT` appended to `RATING_ERROR_CODES` (`:305`) |
| `scripts/generate-contracts.py` | `GENERATED_SHAPES` (`:38`): `"rating-version-create": "RatingVersionCreate"` appended |
| `backend/tests/test_contracts.py` | `ONE_SIDED_SLUGS` (`:69`): one key appended |
| `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/rating-version-create.schema.json` | regenerated / generated |
| `docs/specs/03-rating-engine.md` | §5.1 create row (`:908`, RL-1428 T1); §4.3 note (after `:436`, T2); §3.4 FR-237 row (`:134`, T3); *(DP-1 a)* §3.x FR-223 row (`:109`, RL 9758 T1). §5.1's owned-code list: no edit, the code is already at `:936` *(Corrected 2026-10-05, pre-mint fix F1; see §"Status".)* |
| `examples/fremtpl2/model.py` | added: `save_demo_algorithm`; edited: `author_demo_rating_evidence` (`:366-`, drops the algorithm save and the two row writes), `create_approved_rating_version` (`:490-`, saves the algorithm first and passes it and `Pins()` to the service) |
| `backend/tests/test_demo_rating_evidence.py` | edited: `_draft` (`:34-41`) passes the algorithm ref and `Pins()` |
| `backend/tests/test_rating_version_create_pins.py` | added (new module) |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated |

**Contention.** Classes are `no_shared_files`' keys: `registry_exempt_append_only` (with its
`generated` list, `packages/*/src/*/__init__.py#__all__` and
`backend/tests/test_contracts.py#ONE_SIDED_SLUGS`) is **exempt**; `forbidden` **SERIALISES**;
`other_shared_path` **SERIALISES unless a dispatch record names the path and its check**
(written **ALLOWED one-sided** here where only one slice edits the shared definition).

| Other slice (lane; source read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **WK-675 S2**, PL 9713 (lane C; #1131 @ `origin/pl-9713-wk675-s2-leaf`, §"Write set", read 2026-10-05 between 13:15 and 13:24 BST) | `docs/specs/03-rating-engine.md` §5.1 | RL 9766 T2: two rows inserted **immediately after `:908`** (anchor: the row whose first two cells are `POST` and `/api/v1/rating-versions`) | T1 replaces `:908`'s purpose cell | `forbidden` (same section), and the hunks are **adjacent**, so the maintainer's (by delegation) lanes A/C option (b) condition 2 (non-adjacency) fails → **SERIALISE**. Either order keeps both anchors (S2's anchor is the row's first two cells; T1's is the third cell), so the second re-applies after a textual merge |
| | `03` §3.4 | RL 9766 T1 inserted after FR-243 (`:140`) | T3 appended to FR-237 (`:134`) | `forbidden` (same table) → SERIALISE |
| | `packages/model-schema/src/model_schema/rating.py` | `RatingAlgorithm` (`:375`) split into `RatingAlgorithmDraft` + `RatingAlgorithm` | `RatingVersionCreate` added after `RatingVersion` | `other_shared_path`, different classes → ALLOWED one-sided |
| | `backend/src/app/api/models.py` | `get_rating_version_by_ref` added between the list and by-id reads | `RatingVersionCreate` removed, `create_rating_version` edited | `other_shared_path`, different definitions → ALLOWED one-sided |
| | `model_schema/__init__.py` `__all__` | `RatingAlgorithmDraft`, `RatingAlgorithmSaved` | `RatingVersionCreate` | exempt (name-disjoint) |
| | `generated.json`, `docs/INDEX.md` | regenerated | regenerated | exempt |
| | `backend/tests/test_contracts.py` | `UNTYPED_REQUEST_PENDING` (only if `SL-1367` landed) | `ONE_SIDED_SLUGS` | different definitions; `ONE_SIDED_SLUGS` exempt |
| **SL-1391**, PL 9716 (lane A; #1127, §"Write set", read as above) | `03` §5.1 | T10 replaces the diff row (`:904`); RL 9710 T1 inserts immediately after it | `:908` | `forbidden` (same section), gap `:905-907` unchanged between the hunks → **ALLOWED: option (b) EXTENDED to this pair** on the 13:00:09 conditions, by the maintainer's (by delegation) entry headed *"2026-10-05 13:29:05 BST — DECISIONS 32 and 33 (PL 9683, the FD 9708 fix)"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 32. Addition: once both branches exist, a trial `git merge-tree --write-tree <S7 head> <this slice's head>` is run and its exit code recorded in both dispatch records (Task 0 Step 5); rc 0 confirms the gap, **rc 1 means SERIALISE** and the second to merge re-applies its row |
| | `model_schema/rating.py` | `RateTableDiff` (`:735-747`) edited, `RateTableDiffCell` added | `RatingVersionCreate` added | `other_shared_path`, different classes → ALLOWED one-sided |
| | `generated.json`, `docs/INDEX.md` | regenerated | regenerated | exempt |
| **SL-1409**, PL-1408 (lane B; in flight, `git diff --name-only origin/main...origin/sl-1409-validation-rule-approval-through-the-workflow`, 34 paths, read 2026-10-05 between 13:15 and 13:24 BST) | `backend/src/app/errors.py` | `RULE_VERSION_IMMUTABLE` added to `DATA_ERROR_CODES` | *(DP-1 a)* a code added to `RATING_ERROR_CODES` | `other_shared_path`, different definitions → ALLOWED one-sided |
| | `model_schema/__init__.py` `__all__` | its own names | `RatingVersionCreate` | exempt (name-disjoint) |
| | `generated.json`, `docs/INDEX.md` | regenerated | regenerated | exempt |
| | `examples/fremtpl2/` | `seed.py`, `test_seed.py` | `model.py` | different files; none shared |
| **PL 9728** / SL 9727 (lane B after SL-1409; #1113, §"Write set") | — | `score.py`, `db/session.py`, `config.py`, `api/deps.py`, `api/authz.py`, `auth/service.py`, `main.py` (DP-4 a), `scripts/bench-rating.py`, `scripts/demo.py` (DP-6 a); `03`/`00` only under its DP-3 (b) or DP-5 | — | disjoint, unless its DP-3 (b) or DP-5 lands text in `03` §3.4 or §5.1, which then serialises; both dispatch records name it |
| **The FD 9707 fix**, PL 9688 / SL 9685 (working ids; **not on `origin` at the time of reading**) | unknown | FR-221's lookup `as_at` (pricing-core lookup evaluation, `/score`, `/score/compare`, batch, per its brief) | — | **not read**: the dispatch re-reads its write set. Expected disjoint from this slice's code; a `03` §3.4 or §5.1 text would serialise |
| **FD 9759 limb 2's owner "S3"** (RL 9758, *What it obliges*) | `errors.py` `RATING_ERROR_CODES`; `03` FR-223 row (`:109`); §5.1 owned list | adds `MODEL_REFERENCE_MODE_INCONSISTENT` and RL 9758 T1 | the same, **under DP-1 (a)** | `forbidden` (same registry entry and same spec row) → **whichever merges first applies them, and the other re-reads and drops its copy**; both dispatch records name it (sent to the lead with DP-1) |
| **WK-673 S3** (SL-1387; #1138 @ `f3603e7c`, as the lead relayed it; not read by this planner) | `docs/specs/03-rating-engine.md` §5.1's owned-code list (`:928` onward, *"Error codes owned by this module:"*) | appends `ATTRIBUTION_RECONCILIATION_FAILED` at the list's tail | ~~appends `MODEL_REFERENCE_MODE_INCONSISTENT` at the same tail (DP-1, item 25)~~ no edit: the code is already at `:936` *(Corrected 2026-10-05, pre-mint fix F1; see §"Status".)* | one list, one tail → **SERIALISE**, by the maintainer's (by delegation) entry headed *"2026-10-05 13:25:23 BST — 29: RL 9663 OK; 30: extend option (b) to S3 vs S2, with one serialisation; 31: close #986 OK"*, item 30: the second to merge merges `main` and re-appends its code at the tail. Dispatch-record item 2. *(Note 2026-10-05, pre-mint fix F1: this slice no longer appends to the list, so the stated reason no longer holds; the serialisation stands until the maintainer (by delegation) lifts it.)* |

### Dispatch-record items

Each item is named in this slice's dispatch record and in the other slice's, as the maintainer (by delegation)
required.

1. **`MODEL_REFERENCE_MODE_INCONSISTENT` and RL 9758 T1** (DP-1, the maintainer's (by delegation) entry headed
   *"2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap findings"*,
   item 25): the first of this slice and the RL 9758 slice (FD 9759 limb 2, "S3") to merge
   registers the code in `RATING_ERROR_CODES` and lands RL 9758 T1. The second rebases, drops
   its copy, and its ledger says so.
2. **The `03` owned-codes tail** (the maintainer's (by delegation) entry headed *"2026-10-05 13:25:23 BST — 29: RL 9663 OK; 30: extend option (b) to S3 vs S2, with one serialisation; 31: close #986 OK"*, item 30): this slice and WK-673 S3 (SL-1387) each append one
   code at the tail of `03` §5.1's owned-code list (`:928` onward). They serialise: the second to
   merge merges `main`, re-appends its code at the tail, re-runs the merge-tree check reading its
   exit code, and re-gates. *(Note 2026-10-05, pre-mint fix F1: this slice no longer appends to
   the owned-code list, since the code is already at `03:936`, so the stated reason no longer
   holds; the serialisation stands until the maintainer (by delegation) lifts it.)*
3. **WK-675 S2 (PL 9713)**: serialised on `03` §5.1 (adjacent hunks at `:908`) and `03` §3.4
   (FR-237 `:134` against S2's insertion after FR-243 `:140`). Each side's hunks and anchors are
   listed.
4. **SL-1391 (PL 9716, lane A's S7)**: `03` §5.1 `:904` against `:908`. Option (b) is extended to
   this pair (the maintainer's (by delegation) entry headed *"2026-10-05 13:29:05 BST — DECISIONS 32 and 33 (PL 9683, the FD 9708 fix)"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 32): both dispatch records list both sides' hunks and anchors and the
   re-measured gap (`:905-907` at `caa4e411`), and the exit code of the trial `git merge-tree --write-tree <S7 head> <this slice's head>`
   (Task 0 Step 5). rc 1 means the pair serialises; the second to merge merges `main`, re-runs the
   merge-tree check reading its exit code, re-applies its row and re-gates. The two gates never run at once.

**Open PRs read** (`gh pr list --state open`, 2026-10-05, between 13:15 and 13:24 BST, `origin/main` `caa4e411`).
On this slice's subject: #1130 (FD-1421), #1133 (RL-1428), #1061 (RL 9758: binds the pin write,
DP-1), #980 (FD 9995: the peril resolver, Acceptance 7), #1131 (PL 9713), #1127 (PL 9716),
#1113 (PL 9728). #1066 (FD 9752, working id: the approval-route hold): not this route (0.12). The others
are findings, rulings and plans on other subjects, or dependency bumps.

### Size

Small: about half an executor day. Five tasks, no migration, no frontend source, no NFR
measurement (it need not run exclusive). One full two-half gate (a gate slot under `RL-1263`).

## Decision points

DP-1, DP-2 and DP-3 blocked activation; they were sent to the lead on 2026-10-05 between
13:15 and 13:24 BST and are **decided** by the maintainer's (by delegation) entry headed *"2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap findings"* in `~/gi-pricing-plan.local/channel/to-lead.md`, items 25–27. DP-4 and DP-5 do not block; the recommendation is applied unless ruled otherwise.
Two choices the brief offered as examples are **not open**: pins are not mutable after create,
and the effective dates are not in the create body; RL-1428 decides both (§"Global Constraints").

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | RL 9758 item 2: *"Any route that writes a Rating Version's `algorithm_ref` or `model_reference_mode` refuses a mismatching write with **422** `MODEL_REFERENCE_MODE_INCONSISTENT` … this binds the slice that adds one."* This slice adds one. RL-1428 T3 says the create route *"stores them and does not resolve them"*. Both cannot hold | **(a)** check at create when `algorithm_ref` resolves in the workspace (load `RatingAlgorithmRow`, run `check_model_reference_mode`); an algorithm that does not resolve is stored and refused at compile (`NOT_FOUND`); this slice also registers the code and lands RL 9758 T1 plus an owned-list text, unless S3 merged them first. **(b)** RL 9758 item 2 is satisfied at compile only for this route (amend RL 9758); create checks nothing. **(c)** check at create and refuse an unresolvable algorithm at create too (422 or 404), amending T1/T3's "resolvability at compile" | **(a)**: it honours both rulings in their intent — RL 9758's check where the version and algorithm first meet, RL-1428's "no resolution at create" for everything else — and costs one query. (b) weakens a ruling already audited; (c) puts resolvability in two places, which RL-1428 rejected | **DECIDED, (a)**, item 25: *"Check MODEL_REFERENCE_MODE_INCONSISTENT at create when algorithm_ref resolves; an unresolvable ref stays compile's. … The slice that merges first registers the code and lands RL 9758 T1; both dispatch records name it; the second rebases and drops its copy, its ledger saying so."* RL-1428 T3 amended pre-mint (`614ad96b`) | Tasks 3, 5; Acceptance 8 |
| **DP-2** | RL-1428 *Acceptance* bullet 5's predicate `grep -rn "algorithm_ref\s*=\|\.pins\s*=" --include=*.py examples/ backend/src/` matches at `caa4e411` beyond the seed (0.7) and would match this slice's own keyword arguments. It cannot print nothing | (a) replace it with `grep -rnE "\.(algorithm_ref\|pins)\s*=[^=]" --include=*.py examples/ backend/src/` (attribute assignment only; prints the two seed lines today); (b) keep the intent in prose and drop the predicate | **(a)**, corrected in RL-1428 before its mint | **DECIDED, (a)**, item 26; RL-1428 at `614ad96b` carries the predicate with its corpus and tree | Acceptance 12 |
| **DP-3** | Where the wrong-type check (RL-1428 T1, *"a ref of the wrong type in any of them is **422**"*) lives. `Pins`' lists are bare `list[ArtifactRef]` (0.4) | (a) a validator on the new `RatingVersionCreate` only; (b) tighten `Pins` itself (per-list admitted types) | **(a)**: T1 scopes the check to the create body. (b) changes every stored row's read (`to_schema` runs `Pins.model_validate` on every list, get, create and submit) and the published `RatingVersion` contract, so one mis-typed bench or legacy row would fail every read of its workspace (the blast-radius argument `BundleMetadata.blob_sha256`'s docstring makes). Admitted types under (a): `algorithm_ref` `rating_algorithm`; `rate_tables` `rate_table`; `models` `model` or `peril_structure` (0.5); `reference_tables` `reference_table`; `custom_objectives` `custom_objective`; `model_ref` stays as today (no new rule) | **DECIDED, (a)**, item 27: *"a validator on the new RatingVersionCreate only. Tightening Pins would change every stored read and the contract."* | Task 2; Acceptance 3, 4 |
| **DP-4** | RL-1428 *Ruled*: *"The seed moves to the route in the same slice."* The seed calls services and has no HTTP client (`examples/fremtpl2/model.py:17-31`) | (a) the seed passes `algorithm_ref` and `pins` to `rating_versions_service.create_rating_version`, the function the route calls; (b) the seed calls the route through an HTTP client | **(a)**: it removes the ORM write the ruling targets with no new dependency in `examples/`; the route itself is proven by Acceptance 1 | **DECIDED, (a)**, by the maintainer's (by delegation) entry headed *"2026-10-05 13:29:05 BST — DECISIONS 32 and 33 (PL 9683, the FD 9708 fix)"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 33, on a condition: the slice still proves the HTTP create route end to end, create with pins over HTTP then compile (Acceptance 1, which therefore may not be replaced by a service-level test), because G2 is over HTTP; and the exit-demo script creates its version through HTTP (`PL-1371` §3.8 row 7, §"Hand-off") | Task 4 |
| **DP-5** | Acceptance 7, the peril pin, while FD 9995 is open | (a) assert today's `NOT_FOUND` at compile, as FD 9995's tripwire, changed by FD 9995's fix; (b) a strict `xfail` asserting `succeeded`; (c) no peril test here | **(a)**: a strict assertion of today's behaviour that FD 9995's fix must visibly flip; (b) hides the failure mode in a marker; (c) loses the brief's case | **DECIDED, (a)**, by the maintainer's (by delegation) entry headed *"2026-10-05 13:29:05 BST — DECISIONS 32 and 33 (PL 9683, the FD 9708 fix)"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 33, on a condition: the test's name or docstring cites FD 9995 and says the assertion is expected to flip when FD 9995 is fixed, so nobody reads it as the intended behaviour (Task 1's docstring) | Acceptance 7 |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Record the dispatch tree: `git rev-parse origin/main` and `git log -1 --format='%H %aI' origin/main`.
- [ ] **Step 2:** Re-run Task 0 at planning time rows 0.1–0.11 on the dispatch tree. Any row
  that differs is reported to the lead before Task 1; a moved line number alone is recorded.
- [ ] **Step 3:** Read the minted RL-1428 and the DP ruling. List every difference from the head
  cited here (`614ad96b`) in the ledger, by `git diff`, not by headings ([`README.md`](README.md) rule 5).
- [ ] **Step 4:** Re-read the write sets of WK-675 S2, SL-1391, WK-673 S3 (SL-1387), PL 9728,
  the FD 9707 fix and FD 9759's S3, at their current heads, and record any path added to the contention table.
  Under DP-1 (a), record whether `MODEL_REFERENCE_MODE_INCONSISTENT` is already in
  `RATING_ERROR_CODES` on the dispatch tree; if it is, Task 3 Step 5 and Task 5 Step 3 are
  skipped and the ledger says so.

- [ ] **Step 5: The trial merge with S7** (the maintainer's (by delegation) entry headed *"2026-10-05 13:29:05 BST — DECISIONS 32 and 33 (PL 9683, the FD 9708 fix)"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 32). Once this slice's branch and SL-1391's
  (lane A's S7) both exist, run `git merge-tree --write-tree <S7 head> <this slice's head>` and record its exit code and the
  two heads in both dispatch records and in the ledger. rc 0: option (b) holds. rc 1: the pair
  serialises; report to the lead before the first gate. Read the exit code, never the first
  line of output.
### Task 1: The tests, red first (Acceptance 1–9, 11)

**Files:**
- Create: `backend/tests/test_rating_version_create_pins.py`

**Interfaces:**
- Consumes (existing, verified at `caa4e411`): fixtures `api_client`
  (`backend/tests/conftest.py:62`), `database`, `blob_store`, `grant`, `workspace_id`,
  `principal` (`backend/tests/conftest_db.py`); from `backend.tests.test_rating_version_compile`:
  `_headers(principal, workspace_id)`, `_minimal_algorithm()`, `_run_compile_job(api_client,
  headers, database, blob_store, rating_version_id) -> JobRow`, `_empty_pins()`; from
  `backend.tests.test_api_reference`: `_table(api_client, headers, publish=...)`; from
  `backend.tests.test_model_jobs_gbm`: `_fitted_gbm(database, blob_store, workspace_id) ->
  tuple[UUID, JobStatus]`; from `backend.tests.approved_rows`: `mark_approved(session, row)`;
  from `backend.tests.test_rating_algorithms`: `valid_algorithm()`.
- Produces: nothing other tasks import.

Mirror the neighbouring tests in `test_rating_version_compile.py` (`:149-197`, `:454-533`,
`:574-640`) where this sample and they differ; do not reinvent the module's fixtures
([`README.md`](README.md) rule 3).

- [ ] **Step 1: Write the module.**

```python
"""POST /api/v1/rating-versions declares the algorithm and the pins (FD-1421, RL-1428).

Create stores the declaration and checks only its shape (422); resolvability and maturity
stay with compile (FR-240), so each refusal below is read from the compile Job.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from backend.tests.approved_rows import mark_approved
from backend.tests.test_api_reference import _table as _seed_reference_table
from backend.tests.test_model_jobs_gbm import _fitted_gbm
from backend.tests.test_rating_algorithms import valid_algorithm
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _headers,
    _minimal_algorithm,
    _run_compile_job,
)
from sqlalchemy import func, select

from app.db.models import AuditEventRow, ModelRow, RatingVersionRow
from model_schema import JobStatus

_LOOP = asyncio.get_event_loop


@pytest.fixture(autouse=True)
def _handlers() -> None:
    from app.worker.rating_handlers import register_rating_handlers

    register_rating_handlers()


def _body(slug: str = "pinned-rv", **extra: object) -> dict:
    return {
        "slug": slug,
        "dataset_version_id": str(uuid4()),
        "model_ref": "model:motor-ad-frequency@7",
        **extra,
    }


def _algorithm(api_client, headers) -> str:
    created = api_client.post("/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers)
    assert created.status_code == 201, created.text
    return "rating_algorithm:minimal@1"


def _rows_with_slug(database, slug: str) -> int:
    async def _count() -> int:
        async with database.session() as session:
            return (await session.execute(
                select(func.count()).select_from(RatingVersionRow).where(RatingVersionRow.slug == slug)
            )).scalar_one()

    return _LOOP().run_until_complete(_count())


def _field_codes(response) -> dict[str, str]:
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED", problem
    return {e["field"]: e["code"] for e in problem["errors"]}


@pytest.mark.req("FR-237")
@pytest.mark.req("FR-239")
def test_a_version_created_with_its_algorithm_and_pins_compiles_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    _LOOP().run_until_complete(grant("admin"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    table = f"reference_table:{_seed_reference_table(api_client, headers, publish=True)}@1"
    pins = {**_empty_pins(), "reference_tables": [table]}

    created = api_client.post(
        "/api/v1/rating-versions", json=_body(algorithm_ref=algorithm_ref, pins=pins), headers=headers
    )
    assert created.status_code == 201, created.text
    version = api_client.get(f"/api/v1/rating-versions/{created.json()['id']}", headers=headers).json()
    assert version["algorithm_ref"] == algorithm_ref
    assert version["pins"] == pins

    job_row = _run_compile_job(api_client, headers, database, blob_store, version["id"])
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error


@pytest.mark.req("FR-239")
def test_a_version_created_without_algorithm_or_pins_is_refused_at_compile(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    created = api_client.post("/api/v1/rating-versions", json=_body(), headers=headers)
    assert created.status_code == 201, created.text
    job_row = _run_compile_job(api_client, headers, database, blob_store, created.json()["id"])
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "RATING_VERSION_UNPINNED"


@pytest.mark.req("FR-237")
def test_an_algorithm_ref_of_another_type_is_refused(
    api_client, workspace_id, principal, grant, database
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    response = api_client.post(
        "/api/v1/rating-versions",
        json=_body("bad-algo-rv", algorithm_ref="model:motor-ad-frequency@7"),
        headers=_headers(principal, workspace_id),
    )
    assert _field_codes(response).get("algorithm_ref") == "VALUE_ERROR"
    assert _rows_with_slug(database, "bad-algo-rv") == 0


@pytest.mark.req("FR-237")
@pytest.mark.parametrize(
    ("field", "ref"),
    [
        ("rate_tables", "model:motor-ad-frequency@7"),
        ("models", "rate_table:motor-expense@3"),
        ("reference_tables", "rate_table:motor-expense@3"),
        ("custom_objectives", "model:motor-ad-frequency@7"),
    ],
)
def test_a_pin_of_another_type_is_refused(
    api_client, workspace_id, principal, grant, database, field: str, ref: str
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    slug = f"bad-pin-{field.replace('_', '-')}"
    response = api_client.post(
        "/api/v1/rating-versions",
        json=_body(slug, pins={**_empty_pins(), field: [ref]}),
        headers=_headers(principal, workspace_id),
    )
    assert _field_codes(response).get("pins") == "VALUE_ERROR"
    assert _rows_with_slug(database, slug) == 0


@pytest.mark.req("FR-240")
def test_an_unknown_algorithm_is_refused_at_compile(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body(algorithm_ref="rating_algorithm:no-such-algorithm@1", pins=_empty_pins()),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    job_row = _run_compile_job(api_client, headers, database, blob_store, created.json()["id"])
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "NOT_FOUND"


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
def test_an_unapproved_model_pin_is_refused_at_compile_and_compiles_after_approval(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    model_id, fit_status = _LOOP().run_until_complete(_fitted_gbm(database, blob_store, workspace_id))
    assert fit_status is JobStatus.SUCCEEDED

    async def _ref() -> str:
        async with database.session() as session:
            row = await session.get(ModelRow, model_id)
            assert row is not None and row.status != "approved", row and row.status
            return f"model:{row.model_family_slug}@{row.version}"

    model_ref = _LOOP().run_until_complete(_ref())
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body("c4-rv", algorithm_ref=algorithm_ref, pins={**_empty_pins(), "models": [model_ref]}),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    version_id = created.json()["id"]

    first = _run_compile_job(api_client, headers, database, blob_store, version_id)
    assert first.status is JobStatus.FAILED
    assert first.error["code"] == "PIN_NOT_APPROVED"

    async def _approve() -> None:
        async with database.unit_of_work() as session:
            row = await session.get(ModelRow, model_id)
            await mark_approved(session, row)

    _LOOP().run_until_complete(_approve())
    second = _run_compile_job(api_client, headers, database, blob_store, version_id)
    assert second.status is JobStatus.SUCCEEDED, second.error
    assert _rows_with_slug(database, "c4-rv") == 1


@pytest.mark.req("FR-237")
def test_a_peril_structure_pin_is_stored_and_compile_reports_no_resolver(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """FD 9995's tripwire (PL-1429 DP-5 (a)), NOT the intended behaviour.

    A peril structure pin should compile; today the resolver has no `peril_structure` branch
    (FD 9995), so compile fails NOT_FOUND. This assertion is expected to flip to `succeeded`
    when FD 9995 is fixed, in the commit that adds the branch.
    """
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body(
            "peril-rv",
            algorithm_ref=algorithm_ref,
            pins={**_empty_pins(), "models": ["peril_structure:motor-perils@1"]},
        ),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    job_row = _run_compile_job(api_client, headers, database, blob_store, created.json()["id"])
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "NOT_FOUND"
    # `execute_job` carries a PlatformError's detail as JobError.message (worker/tasks.py:227).
    assert "has no backend table yet" in job_row.error["message"]


@pytest.mark.req("FR-223")
def test_a_mode_mismatch_is_refused_at_create(
    api_client, workspace_id, principal, grant, database
) -> None:
    """RL 9758 item 2 at the pin write (PL-1429 DP-1 (a)): only a resolving algorithm is checked."""
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    saved = api_client.post("/api/v1/rating-algorithms", json=valid_algorithm(), headers=headers)
    assert saved.status_code == 201, saved.text

    refused = api_client.post(
        "/api/v1/rating-versions",
        json=_body("mode-rv", algorithm_ref="rating_algorithm:motor-gb@1",
                   pins=_empty_pins(), model_reference_mode="approximation"),
        headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"
    assert "s_rp" in refused.json()["detail"]
    assert _rows_with_slug(database, "mode-rv") == 0

    accepted = api_client.post(
        "/api/v1/rating-versions",
        json=_body("mode-rv", algorithm_ref="rating_algorithm:motor-gb@1",
                   pins=_empty_pins(), model_reference_mode="exact"),
        headers=headers,
    )
    assert accepted.status_code == 201, accepted.text


@pytest.mark.req("FR-223")
def test_model_reference_mode_inconsistent_is_registered_and_owned() -> None:
    """RL 9758 Acceptance 3. It holds whichever slice registered the code first."""
    from pathlib import Path

    from app.errors import RATING_ERROR_CODES

    spec = (Path(__file__).resolve().parents[2] / "docs/specs/03-rating-engine.md").read_text()
    assert "MODEL_REFERENCE_MODE_INCONSISTENT" in RATING_ERROR_CODES
    owned = spec.split("### 5.1", 1)[1].split("\n### ", 1)[0]
    assert "`MODEL_REFERENCE_MODE_INCONSISTENT`" in owned


@pytest.mark.req("FR-237")
def test_the_create_body_is_the_model_schema_type(api_client) -> None:
    import model_schema
    from app.api import models as api_models

    assert api_models.RatingVersionCreate is model_schema.RatingVersionCreate
    schema = api_client.get("/openapi.json").json()["components"]["schemas"]["RatingVersionCreate"]
    assert {"algorithm_ref", "pins", "model_reference_mode"} <= set(schema["properties"])


@pytest.mark.req("FR-237")
def test_the_creation_event_records_the_declared_pins(
    api_client, workspace_id, principal, grant, database
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body("audited-rv", algorithm_ref=algorithm_ref, pins=_empty_pins()),
        headers=headers,
    )
    assert created.status_code == 201, created.text

    async def _after() -> dict:
        async with database.session() as session:
            return (await session.execute(
                select(AuditEventRow.after).where(
                    AuditEventRow.action == "rating_version.created",
                    AuditEventRow.entity_ref == "rating_version:audited-rv@1",
                )
            )).scalar_one()

    after = _LOOP().run_until_complete(_after())
    assert after["algorithm_ref"] == algorithm_ref
    assert after["pins"] == _empty_pins()
    assert after["model_reference_mode"] == "exact"
```

  Literals to verify against the shipped source before the first run
  ([`README.md`](README.md) rule 1), each a grep: `AuditEventRow`'s column names `action`,
  `entity_ref`, `after`; the problem body's `detail` and `errors[].field` keys
  (`backend/src/app/errors.py:466-493`); `JobRow.error["message"]` carrying the
  `PlatformError` detail (verified: `backend/src/app/worker/tasks.py:227`, `message=exc.detail or exc.title`); the OpenAPI path `/openapi.json`; whether the
  `analyst` role holds `rating:write` and `rating:compile` (`test_rating_version_compile.py`
  grants only `analyst` and compiles, `:149-178`). A literal that differs is corrected to the
  source and recorded in the ledger.

- [ ] **Step 2: Run it and record each red by cause.**

Run: `uv run pytest -q backend/tests/test_rating_version_create_pins.py`
Expected at the dispatch tree (before Tasks 2–5):
- `test_a_version_created_without_algorithm_or_pins_is_refused_at_compile` **passes** (control).
- `test_the_create_body_is_the_model_schema_type` fails with `AttributeError: module 'model_schema' has no attribute 'RatingVersionCreate'`.
- `test_model_reference_mode_inconsistent_is_registered_and_owned` fails on the `RATING_ERROR_CODES` assert.
- `test_the_creation_event_records_the_declared_pins` and every other create test fail on the
  create's 422, whose `errors[]` hold `EXTRA_FORBIDDEN` on `algorithm_ref` and/or `pins`
  (`model_reference_mode` too, in the DP-1 test). For the two `VALUE_ERROR` tests, the failure
  is `assert 'EXTRA_FORBIDDEN' == 'VALUE_ERROR'` (or `None` for `pins` when only `pins` is
  sent: read the printed dict). A 422 with any other code, or a 201, is a plan defect: stop
  and report.

- [ ] **Step 3: Commit** `test(rating): POST /rating-versions declares the algorithm and the pins, red (FD-1421)`.

### Task 2: The typed request (Acceptance 3, 4, 9, 10)

**Files:**
- Modify: `packages/model-schema/src/model_schema/rating.py` (after `RatingVersion`, `:138-170`)
- Modify: `packages/model-schema/src/model_schema/__init__.py` (import block and `__all__`)
- Modify: `scripts/generate-contracts.py` (`GENERATED_SHAPES`, `:38`)
- Modify: `backend/tests/test_contracts.py` (`ONE_SIDED_SLUGS`, `:69`)
- Regenerate: `docs/contracts/`

**Interfaces:**
- Produces: `model_schema.RatingVersionCreate` with fields `slug: Slug`,
  `dataset_version_id: UUID`, `model_ref: ArtifactRef`, `algorithm_ref: ArtifactRef | None = None`,
  `pins: Pins | None = None`, `model_reference_mode: ModelReferenceMode = "exact"`;
  `model_config = ConfigDict(frozen=True, extra="forbid")`.

- [ ] **Step 1: Add the class** (DP-3 (a), decided):

```python
#: The artifact types each pin list admits (FR-237; RL-1428 T1). `models` holds a
#: `model_call`'s `model_ref` or `peril_structure_ref` (`compile.check_step_refs_pinned`).
_PIN_TYPES: Final[dict[str, frozenset[str]]] = {
    "rate_tables": frozenset({"rate_table"}),
    "models": frozenset({"model", "peril_structure"}),
    "reference_tables": frozenset({"reference_table"}),
    "custom_objectives": frozenset({"custom_objective"}),
}


class RatingVersionCreate(BaseModel):
    """The body of `POST /api/v1/rating-versions` (03 §5.1, FR-237; RL-1428).

    Create stores the declared algorithm and pins and checks only their shape: a ref of the
    wrong type is refused here (422). Whether each ref resolves, and at what maturity, is
    compile's (FR-240), so a version created without them is refused there with
    `RATING_VERSION_UNPINNED`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug
    dataset_version_id: UUID
    model_ref: ArtifactRef
    algorithm_ref: ArtifactRef | None = None
    pins: Pins | None = None
    model_reference_mode: ModelReferenceMode = "exact"

    @field_validator("algorithm_ref")
    @classmethod
    def _an_algorithm(cls, ref: ArtifactRef | None) -> ArtifactRef | None:
        if ref is not None and ref.type != "rating_algorithm":
            raise ValueError(f"{ref} is not a rating_algorithm reference")
        return ref

    @field_validator("pins")
    @classmethod
    def _each_list_holds_its_own_type(cls, pins: Pins | None) -> Pins | None:
        for name, admitted in _PIN_TYPES.items():
            for ref in getattr(pins, name, ()):
                if ref.type not in admitted:
                    raise ValueError(f"pins.{name} holds {ref}, which is not a {' or '.join(sorted(admitted))} reference")
        return pins
```

  Check before writing: `slug` is `Slug` here because `RatingVersion.slug` is `Slug`
  (`rating.py:157`); the route-local class used `str`. A slug the old body accepted and the
  stored shape refuses would already fail `to_schema` on read, so the narrowing refuses at
  the boundary what could never be read back. Record it in the ledger. Confirm
  `field_validator`, `Final` and `UUID` are imported in `rating.py`, and add what is missing.
- [ ] **Step 2:** Append `RatingVersionCreate` to the import block and `__all__` in
  `model_schema/__init__.py` (name-disjoint append, `RL-1263` exempt key).
- [ ] **Step 3:** Append to `GENERATED_SHAPES`, with the house comment form:

```python
    # Added <date> (WK-1178, the FD-1421 fix, RL-1428): the body of `POST /rating-versions`,
    # moved out of the API module. First written form, no hand-authored counterpart.
    "rating-version-create": "RatingVersionCreate",
```

- [ ] **Step 4: Red (Acceptance 10).** Run `uv run python scripts/generate-contracts.py`, then
  `uv run pytest -q backend/tests/test_contracts.py -k one_sided`. Expected: fails naming
  `rating-version-create` as undeclared. Record it.
- [ ] **Step 5:** Append to `ONE_SIDED_SLUGS`:
  `"rating-version-create": "first written form — 03 §5.1 create row (RL-1428, FD-1421, FR-237)",`
  then `uv run python scripts/generate-contracts.py --check` and the contract tests: green.
- [ ] **Step 6: Commit** `feat(model-schema): RatingVersionCreate declares the algorithm and the pins (FD-1421)`.

### Task 3: The service and the route (Acceptance 1–8, 11)

**Files:**
- Modify: `backend/src/app/platform/rating_versions.py` (`create_rating_version`, `:230-275`)
- Modify: `backend/src/app/api/models.py` (remove `:271-276`; edit `:1160-1185`)
- Modify: `backend/src/app/errors.py` (`RATING_ERROR_CODES`, `:305`), unless the RL 9758 slice registered it first

**Interfaces:**
- Consumes: `model_schema.RatingVersionCreate` (Task 2); `Pins`, `ModelReferenceMode`,
  `RatingAlgorithm`, `check_model_reference_mode` from `model_schema`.
- Produces: `create_rating_version(session, *, workspace_id, actor, slug, dataset_version_id,
  model_ref, algorithm_ref: ArtifactRef | None = None, pins: Pins | None = None,
  model_reference_mode: ModelReferenceMode = "exact") -> RatingVersionRow`. Task 4 calls it.

- [ ] **Step 1: The service.** Add the three keyword parameters and write them on the row:
  `algorithm_ref=str(algorithm_ref) if algorithm_ref else None`,
  `pins=pins.model_dump(mode="json") if pins is not None else None`,
  `model_reference_mode=model_reference_mode`. Extend the audit `after` with
  `"algorithm_ref"`, `"pins"` and `"model_reference_mode"`, as the row stores them. Update
  the docstring: it declares the algorithm and pins (FR-237) and does not resolve them (FR-240).
- [ ] **Step 2: The mode check (DP-1 (a)).** Before `session.add(row)`:

```python
    if algorithm_ref is not None:
        algorithm_row = await session.scalar(
            select(RatingAlgorithmRow).where(
                RatingAlgorithmRow.workspace_id == workspace_id,
                RatingAlgorithmRow.slug == algorithm_ref.slug,
                RatingAlgorithmRow.version == algorithm_ref.version,
            )
        )
        # An algorithm that does not resolve is stored and refused at compile (FR-240,
        # RL-1428 T3); one that resolves is mode-checked here (FR-223, RL 9758 item 2).
        if algorithm_row is not None:
            _require_consistent_mode(model_reference_mode, RatingAlgorithm.model_validate(algorithm_row.content))
```

  with a module-level helper that calls `check_model_reference_mode` and raises
  `PlatformError("MODEL_REFERENCE_MODE_INCONSISTENT", "Model reference mode inconsistent", 422, str(exc))`
  on its `ValueError`. `check_model_reference_mode(version, algorithm)` reads only
  `version.model_reference_mode` (`rating.py:173-184`); pass the `RatingVersion` that
  `to_schema(row)` returns after `flush()` if a partial object will not type-check, and raise
  before `audit.record` either way.
- [ ] **Step 3: The route.** Delete the route-local `RatingVersionCreate`; import it from
  `model_schema`; pass `algorithm_ref=body.algorithm_ref`, `pins=body.pins`,
  `model_reference_mode=body.model_reference_mode`; `responses=problems(401, 403, 422)` is
  unchanged (every new refusal is a 422). Docstring: *"Create a draft rating version, declaring
  its algorithm and pins (FR-237). Their shape is checked here (422); whether they resolve, and
  at what maturity, is checked at compile (FR-240)."* Under DP-1 (a) add: *"A declared mode that
  the algorithm's `model_call` steps contradict is 422 `MODEL_REFERENCE_MODE_INCONSISTENT`
  (FR-223)."*
- [ ] **Step 4:** `grep -rn "RatingVersionCreate" backend/src` prints only the import and the
  handler's annotation.
- [ ] **Step 5: Unless Task 0 Step 4 found it registered.** Append
  `"MODEL_REFERENCE_MODE_INCONSISTENT",` to `RATING_ERROR_CODES` under a comment
  `# FR-223 at the pin write (RL 9758 item 2) and at compile (limb 2).`
- [ ] **Step 6:** Run the module: every test passes, including
  `test_model_reference_mode_inconsistent_is_registered_and_owned` (its owned-list half holds at
  `03:936`). *(Corrected 2026-10-05, pre-mint fix F1; see §"Status".)* Run
  `uv run pytest -q backend/tests/test_rating_versions.py backend/tests/test_rating_version_compile.py`:
  green (the old three-field body still creates).
- [ ] **Step 7: Commit** `fix(rating): POST /rating-versions takes algorithm_ref, pins and model_reference_mode (FD-1421)`.

### Task 4: The seed through the create path (DP-4 (a); Acceptance 12, 13)

**Files:**
- Modify: `examples/fremtpl2/model.py` (`author_demo_rating_evidence`, `:366-`; `create_approved_rating_version`, `:490-`)
- Modify: `backend/tests/test_demo_rating_evidence.py` (`_draft`, `:34-41`)

- [ ] **Step 1: Red (Acceptance 12).** Run the predicate:
  `grep -rnE "\.(algorithm_ref|pins)\s*=[^=]" --include=*.py examples/ backend/src/`
  Expected: `examples/fremtpl2/model.py:396` and `:397`. Record it.
- [ ] **Step 2:** Extract the algorithm save (`:383-391`) into

```python
async def save_demo_algorithm(
    database: Database, workspace_id: UUID, analyst: Principal
) -> ArtifactRef:
    """Save the demo-fixture algorithm through the service; a re-seed's 409 is tolerated."""
    if analyst.id is None:
        raise RuntimeError("the demo analyst has no id")
    try:
        await algorithm_service.create_algorithm(
            database, workspace_id, analyst.id, _demo_algorithm()
        )
    except PlatformError as exc:  # a re-seed: the algorithm is already saved
        if exc.status_code != 409:
            raise
    return ArtifactRef(type="rating_algorithm", slug=DEMO_ALGORITHM_SLUG, version=1)
```

- [ ] **Step 3:** In `author_demo_rating_evidence`, remove the save and the two row writes;
  keep the `load_rating_version` read for `ref`. Update its docstring: the version arrives with
  its algorithm and pins declared at create.
- [ ] **Step 4:** In `create_approved_rating_version`, call `save_demo_algorithm(...)` before
  the create and pass `algorithm_ref=<its result>, pins=Pins()` to
  `rating_versions_service.create_rating_version`. `Pins()` serialises to the same four empty
  lists as `_EMPTY_PINS`, which is then unused: remove it if nothing else reads it
  (`grep -n _EMPTY_PINS examples/`).
- [ ] **Step 5:** In `backend/tests/test_demo_rating_evidence.py` `_draft`, call
  `demo_model.save_demo_algorithm(database, workspace_id, analyst)` and pass its result and
  `Pins()` to the service.
- [ ] **Step 6:** Re-run the predicate: it prints nothing. Run
  `uv run pytest -q backend/tests/test_demo_rating_evidence.py examples/fremtpl2/test_seed.py`: green.
- [ ] **Step 7: Commit** `refactor(seed): the demo rating version declares its algorithm and pins at create (FD-1421)`.

### Task 5: The spec texts, verbatim (Acceptance 14)

**Files:**
- Modify: `docs/specs/03-rating-engine.md`

These land **in the commit that makes Acceptance 1–9 green**, not after it (`CLAUDE.md` §2):
squash Task 5 into Task 3's commit, or amend Task 3's commit before the PR, and say so in the
ledger.

- [ ] **Step 1:** Apply RL-1428 T1 (§5.1 `:908`), T2 (after `:436`) and T3 (FR-237, `:134`)
  byte for byte from the **minted** record, with `<date>` the commit date and the working id
  replaced by the minted `RL-` id. A find string not found exactly once is a stop.
- [ ] **Step 2: Unless Task 0 Step 4 found it landed:** RL 9758 T1 (FR-223,
  `:109`), byte for byte. The code is already in the owned-code list at `03:936`: no edit.
  *(Corrected 2026-10-05, pre-mint fix F1; see §"Status".)* The add at the list's tail is struck. Dispatch-record item 2's serialisation
  with WK-673 S3 stands as ruled until the maintainer (by delegation) lifts it.
- [ ] **Step 3:** `test_model_reference_mode_inconsistent_is_registered_and_owned` passes (DP-1 (a)).
- [ ] **Step 4:** `python3 scripts/audit-docs.py` (check 31's working-id rows are expected until
  the mint) and `uv run python scripts/req-coverage.py`.

### Task 6: The gate and the ledger (Acceptance 15)

- [ ] **Step 1:** Request a gate slot from the lead (`RL-1263`); run the two-half gate
  (`.claude/skills/dev-commands`) on the merge tree, through `gate-runner`, and record its
  exit-code table with the tree it ran on.
- [ ] **Step 2:** The ledger `docs/ledgers/LG-<n>` records: the dispatch tree; each red by its
  printed failure line; the literal corrections of Task 1 Step 1; the `Slug` narrowing (Task 2
  Step 1); the DP rulings applied; the predicate's before/after output; the gate table.
- [ ] **Step 3:** `python3 scripts/doc-index.py`, commit, push, open the PR against
  `main` with `origin/main...<branch>` named as the range.

## Hand-off

The slice is done when every Acceptance item holds on the merge tree and the slice audit is
clean. Then the lead adds this slice and FD 9995 to `PL-1371` §3.8 row 7 as prerequisites of
C1 (RL-1428 *What it obliges*), if that has not been done at the mint. The exit-demo script's
C1 call is that row's, not this slice's.

## Self-review

1. **Spec coverage.** FR-237 → Tasks 1–3, 5; FR-240 and FR-20 → Acceptance 5, 6 (no code: compile
   unchanged); FR-239 → Acceptance 1, 2; FR-223 → DP-1, Acceptance 8; FR-440 → T2 only; FR-451 →
   Task 2; RL-1428 T1–T3 → Task 5; RL-1428 *Acceptance* bullets 1–5 → Acceptance 1, 3–4, 6, 9, 12;
   RL-1428's docstring obligation → Task 3 Step 3; RL 9758 item 2 → DP-1. WF-699 C1 needs no
   text (RL-1428).
2. **Placeholders.** `<date>`, `<n>` and the minted `RL-` id are filled at the commit or the mint,
   as the house form does; nothing else is deferred. DP-dependent steps say which option they
   belong to.
3. **Type consistency.** `RatingVersionCreate`'s six fields are the same in Task 2's class, Task 3's
   service signature and the route, and Task 1's bodies; `save_demo_algorithm` returns
   `ArtifactRef` in Task 4 Steps 2, 4 and 5; `_PIN_TYPES` admits `peril_structure` in `models`,
   which Acceptance 7 relies on.
4. **Literals** quoted in samples that were not grep-verified at `caa4e411` are listed in Task 1
   Step 1 for the executor to verify; the rest were read (§"Task 0 at planning time").
