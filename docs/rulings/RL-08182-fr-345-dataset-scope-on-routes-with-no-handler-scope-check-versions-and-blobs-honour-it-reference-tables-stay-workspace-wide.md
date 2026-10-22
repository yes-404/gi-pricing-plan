---
id: RL-8182
family: ruling
title: "FR-345 dataset scope on the routes with no handler scope check: Dataset Version routes and blobs honour a dataset-scoped grant, reference tables stay workspace-wide (draft, for the maintainer's adoption)"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-22   # drafted 2026-10-22 under working id 8182; not minted
owner: decision-maker
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1301]
---

# RL-8182 — FR-345 dataset scope on the routes with no handler scope check: Dataset Version routes and blobs honour a dataset-scoped grant, reference tables stay workspace-wide

**Status of this draft.** Recommended by the decision-maker (dm-8182) on 2026-10-22. It binds
nothing until the maintainer adopts, amends or rejects it with a dated line. The working ids
in prose (FD 8177, PL 8181, RL 8176) are not minted.

**The question.** The maintainer's entry "2026-10-22 17:27:15 BST — Maintainer: FD 8177
CONFIRMED HIGH; planner GO for the fix slice; the FR-345 spec question goes to a decision-maker
in parallel" in `to-lead.md`, verbatim:

> - **The spec question** (DATASET_* permissions on blobs.py:50–52, dataset_versions.py:60–62 and reference_tables.py:50, which have no handler scope check: must a scoped grant be honoured there under FR-345?): **seat a decision-maker in parallel** for options plus one recommendation, as an RL draft. If it rules "honoured", its routes join the fix slice or follow it. The fix slice does NOT wait for this ruling.

## Verified first, at `71e481fa` (origin/main)

Paths are under `backend/src/app/` unless they start with `docs/`.

**1. How a scoped grant is refused today.** `api/authz.py`:170 `requires(permission)` calls
`rbac.require_permission` with no `resource` (:194–205). `platform/rbac.py`:205–217 `_covers`
returns `True` for a `workspace` assignment, and `False` for any scoped assignment when
`resource is None` (:209–212). So a route-level `requires(DATASET_*)` refuses a principal whose
only grant is scoped to one Dataset, with 403 `PERMISSION_DENIED`. The FD 8177 probe shows this
on `PUT /datasets/{slug}/dictionary` (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/fd-8177/result.md`,
probe branch `probe/fd-8177-dataset-scoped-write` @`f4c0832f`: `assert 403 == 200`,
`"code":"PERMISSION_DENIED"`, server log `"scope":"workspace"`).

**2. The scope types.** `packages/model-schema/src/model_schema/permissions.py`:94–108
`ScopeType`: `workspace`, `dataset`, `model_family`, `rating_algorithm`, `environment`. There is
no reference-table scope and no blob scope. `role_assignments` stores one `scope_type` and one
`scope_id`, and `scope_id` is null exactly when the scope is `workspace`
(`db/models.py`:711–712, :731).

**3. The three named files, route by route.**

| File:line (alias) | Permission | Routes (decorator line → handler line) | What the route acts on | Is there one Dataset to scope to? |
|---|---|---|---|---|
| `api/dataset_versions.py`:60 `ReadDatasets` | `dataset:read` | `GET /{version_id}/validation-reports` :168→173; `/profile` :263→266; `/one-ways` :277→282; `/compare` :296→301; `/lineage` :372→375; `/rejected` :413→418; `GET /splits` :505→510 | one Dataset Version (and `compare`'s `against` version) | **yes**: `DatasetVersionRow.dataset_id`, loaded by `_scoped` (:73–80) in every handler |
| `api/dataset_versions.py`:61 `WriteDatasets` | `dataset:write` | `POST /{version_id}/derive` :332→338; `POST /splits` :467→473 | one Dataset Version (the parent) | **yes**, as above |
| `api/dataset_versions.py`:62 `ValidateDatasets` | `dataset:validate` | `POST /{version_id}/validate` :130→136; `POST /transition` :203→208 | one Dataset Version | **yes**, as above |
| `api/blobs.py`:52 `WriteDatasets` | `dataset:write` | `POST /blobs/upload-url` :69→74; `POST /blobs/uploads/{upload_id}/complete` :110→116 | a staged upload in the caller's workspace (`BlobUploadRow`: workspace, principal, staging key; no Dataset) | **no**: the bytes are staged before any Dataset is named. The Dataset is named later, at `POST /datasets/{slug}/versions` (`api/datasets.py`:515→521), which checks the blob with `blob_readable_by` (:543–546) |
| `api/blobs.py`:50 `ReadDatasets` | `dataset:read` | `GET /blobs/{sha256}` :156→163 | a content-addressed blob. `platform/blobs.py`:703–729 `blob_readable_by`: readable only if an owner in the caller's workspace references it — a Dataset Version's table, or a Job's `JobResult(kind="blob")` | **sometimes**: through an owning Dataset Version (there may be several, in several Datasets); **none** for a Job-result blob |
| `api/reference_tables.py`:50 `ReadDatasets` | `dataset:read` | `GET /reference-tables/{slug}/lookup` :176→181; `GET /reference-tables` :206→211; `GET /{slug}/versions` :223→228; `GET /{slug}/versions/{version}/rows` :242→247 | a Reference Table: a workspace resource, not a Dataset (`01` FR-69–72). Its writes are `admin:manage_settings` (`api/reference_tables.py`:51) | **no** |

**4. What the spec says.** `docs/specs/06-governance.md`:81 FR-345: "Role assignments are
**scoped**: workspace-wide, or limited to named Datasets, Model Families, or Rating Algorithms",
amended 2026-10-03 (`RL-1301` B, `CR-1212` item 4) to add Environments. FR-350
(`06-governance.md`:86) makes the scope default closed: "a principal whose Role is granted but
whose scope is unassigned holds the role's permissions over **no artifacts** rather than over all
of them". `06` §3's permission table (`06-governance.md`:273–276): `dataset:read` governs
"Reading Datasets, Dataset Versions and their validation reports and profiles"; `dataset:write`
governs "Creating Datasets and Dataset Versions, and writing blobs, validation rules and
ingestion". **No `06` text gives `dataset:read` over reference tables**; that pairing exists only
in code.

**5. The pattern a scoped check follows.** `RL-1301` B.2: the route "checks in the handler, with
the target … as the resource" and "**must not** rely on a bare `requires(...)` dependency",
because with no resource `_covers` admits only a workspace-wide grant. Three dataset-scoped
handler checks exist (`platform/datasets.py`:282–288, `platform/validation_rules.py`:829,
`platform/validation.py`:259–264). PL 8181's slice fixes the three routes that put a bare
`requires` in front of them (the maintainer's 17:27:15 entry).

**6. The order rule now adopted.** RL 8176 (draft branch `draft/rl-8176` @`aab1b741`, adopted by
the maintainer 2026-10-22 17:21:38 BST, not minted) obliges a dated clause in `06` FR-343: "a
route's permission check precedes any lookup of an id its path names … **One exception:** where
the permission is checked with an **Environment** as the resource". Its reasoning (item 1 of
"Why (A)") names datasets as the case the rule protects: "It protects ids whose existence is
itself access-controlled, such as datasets and models."

**7. What a dataset-scoped analyst can do end to end, today.** Nothing in the data module. Every
`DATASET_*` route in `api/datasets.py`, `api/dataset_versions.py`, `api/validation.py`,
`api/blobs.py` and `api/reference_tables.py` carries a route-level `requires` (`api/datasets.py`:87–88;
`api/validation.py`:67–70; the files above). After PL 8181's slice, the analyst can replace the
dictionary and rule set of the in-scope Dataset and acknowledge its warnings, but cannot upload,
ingest, validate, transition or read a version of it.

## Ruled

*Recommended as (C); for the maintainer's adoption.*

**Option (C) is recommended: split by what each route acts on.** The principle is one sentence:
**a `DATASET_*` permission is checked with the Dataset as the resource wherever the route acts on
one identifiable Dataset; where it acts on no Dataset, it is checked as "held under any scope"
only if the action binds to no Dataset's data, and workspace-wide otherwise.**

**The options considered.**

| | (A) Honour the scope on every route | (B) Workspace-only on all three files, written into FR-345 | (C) Per route, by what it acts on (recommended) |
|---|---|---|---|
| **Dataset Version routes** | honoured: resolve `dataset_id`, check with it | refused | honoured, as (A) |
| **Blob upload / complete** | no Dataset exists to check, so (A) must invent one: a new `dataset` field on `UploadUrlRequest`, a contract change | refused | "held under any scope": staging binds no Dataset; the Dataset is checked at ingestion |
| **Blob download** | honoured through an owning Dataset Version | refused | honoured through an owning Dataset Version; a Job-result blob stays workspace-wide |
| **Reference tables** | no Dataset to check; (A) would have to read "held anywhere", which makes a one-Dataset grant read every workspace reference table | refused | refused: workspace-wide only, stated in the spec |
| **Least privilege** | widens reference data to every scoped holder | strict, but the scoped grant is unusable | strict on data; the one widening (staging bytes) grants no read of any Dataset |
| **FR-345 / FR-350 text** | needs reference tables added as a "Dataset" use | needs a carve-out that makes a dataset-scoped grant mean "the dictionary and rule set only" | fits FR-345's "limited to named Datasets" as written; one clause records the reference-table limit |
| **End to end, scoped analyst** | upload, ingest, validate, read | dictionary and rule set only (after PL 8181) | upload, ingest (once `api/datasets.py`'s single-Dataset routes follow, below), validate, transition, read, download its own version data |
| **Test churn** | high (contract change for upload) | none in code; one spec clause | medium: one dependency, eleven version routes, one owner-aware blob check, red-first tests |

**Why (C).**

1. **Every Dataset Version route already names its Dataset.** `_scoped` (`api/dataset_versions.py`:73–80)
   loads the row in every handler, and `DatasetVersionRow.dataset_id` is the `ResourceRef`. This
   is exactly `RL-1301` B.2's pattern. Refusing a scoped grant here makes FR-345's "limited to
   named Datasets" unusable for the Dataset's own versions: a motor-scoped analyst could edit the
   motor dictionary but could not see whether the motor data passed validation.
2. **A staged upload is not a Dataset's data yet.** `POST /blobs/upload-url` writes a
   `BlobUploadRow` with no Dataset, and completion makes a blob owned only by its Job. The
   binding to a Dataset happens at `POST /datasets/{slug}/versions`, and that is where the scope
   must be checked. Checking "held under any scope" at upload is the closed default applied
   correctly: the principal holds `dataset:write` over *some* artifact, and the upload gives it
   no read of any Dataset. Without this, no scoped analyst can ever ingest, because ingestion
   requires a blob the workspace owns (`api/datasets.py`:543–546).
3. **A download is a read of a Dataset Version's data when a version owns the blob.** The route's
   declared purpose is "a dataset version's parquet tables are blobs" (`api/blobs.py` module
   docstring). One digest can be owned by versions of several Datasets; the bytes are identical,
   so holding `dataset:read` on **any one** owning Dataset is enough. A blob owned only by a Job
   result has no Dataset, so it stays workspace-wide (closed, FR-350).
4. **A reference table is not a Dataset.** FR-345 lists no reference-table scope, `ScopeType` has
   none, and `06` §3 gives `dataset:read` no reference-table meaning. Admitting a one-Dataset
   grant to every workspace reference table would infer scope, which FR-350 forbids ("never
   inferred"). The cost is real but small: a scoped analyst does not see the `/reference` view.
   A `VR-REF-3` failure on its own Dataset is still reported in that Dataset's validation report.
5. **Why not (A).** It forces a Dataset onto the two upload routes (a contract change for no
   security gain, since ingestion checks the Dataset anyway) and widens reference data.
   **Why not (B).** It keeps the defect FD 8177 calls HIGH, only renamed: a scoped grant that
   cannot read or validate its own Dataset's versions is the "legitimate scoped user locked out"
   case the maintainer's 17:27:15 entry ruled against.

**The refusal order (it interacts with RL 8176).** A dataset-scoped check needs the Dataset id,
so it comes after a lookup. RL 8176's FR-343 clause admits only the Environment exception to
"permission before lookup", and its reasoning names datasets as the protected case. So each route
in this ruling, **and each of PL 8181's three routes**, uses this order:

1. **"Held under any scope" before any lookup:** `rbac.holds_anywhere(permission)`
   (`platform/rbac.py`:219) false → 403 `PERMISSION_DENIED`. A caller with no grant learns
   nothing about which ids exist.
2. **Load:** unknown or other-workspace id → 404 `NOT_FOUND` (as `_scoped` does today).
3. **Scoped check** with `ResourceRef(ScopeType.DATASET, dataset_id)` → 403 `SCOPE_DENIED`.

The residual: a principal that holds the permission on *another* Dataset can tell an unknown id
(404) from an out-of-scope one (403 `SCOPE_DENIED`). This is accepted: it is limited to members
of the same workspace who already hold the permission, `SCOPE_DENIED` is `06` §5.1's actionable
distinction, and the maintainer's 17:27:15 entry already requires the PL 8181 control on Dataset
Y to assert `SCOPE_DENIED`. For `dataset_versions.py` the ids are UUIDv7, not guessable slugs.
**This needs one more dated sentence in `06` FR-343, in the same mint as RL 8176's clause** (below).

## What it obliges

*If the maintainer adopts (C) as written.*

1. **The spec change, by the decision-maker, in the batch PR that mints this record (spec first,
   with the record in the same commit).**
   - `06` FR-345 (`docs/specs/06-governance.md`:81) gains a dated clause: *(Amended <date>,
     RL-<n>.)* **Where a dataset scope reaches.** A `dataset`-scoped `dataset:*` grant is checked
     with the Dataset as the resource on every route that acts on one Dataset or one of its
     Dataset Versions, including blob download through an owning Dataset Version. Staging a
     blob upload (`POST /api/v1/blobs/upload-url` and its completion) binds no Dataset and needs
     the permission under any scope; the Dataset is checked when the blob is ingested. A route
     that acts on no particular Dataset — a list, a Job-result blob, a Reference Table — needs a
     workspace-wide grant (FR-350's closed default). **Reference Tables are not Datasets**: a
     dataset-scoped grant does not reach them.
   - `06` FR-343 gains, after RL 8176's order clause: **Order, for a dataset-scoped check:** the
     permission is first checked as held under any scope, before any lookup (403
     `PERMISSION_DENIED`); the Dataset or Dataset Version is then loaded (404 `NOT_FOUND`); the
     scoped check follows (403 `SCOPE_DENIED`). A principal holding the permission on another
     Dataset can therefore tell an unknown id from an out-of-scope one.
   - `06` §3's `dataset:read` row (`06-governance.md`:273) gains "and Reference Tables,
     workspace-wide only (FR-345)". This records the pairing the code already has.
2. **The code, in one slice, owner Work WK-1178 unless PL 8181's planner names another for
   FD 8177, in which case this follows it.** It **follows PL 8181's slice and does not ride
   it**: the maintainer ruled the fix slice does not wait, and this slice reuses that slice's
   refusal helper and regression guard. Content:
   - a route dependency for "held under any scope" (built on `rbac.holds_anywhere`, keeping
     `RL-1687` (1a): the management count runs only after the final check, so a 403 is never
     counted — `api/authz.py`'s `management_counter`, :155, is the existing form);
   - the eleven `api/dataset_versions.py` routes: the pre-check, `_scoped`, then
     `rbac.require_permission(..., resource=ResourceRef(ScopeType.DATASET, row.dataset_id))`.
     Every version id the request names is checked, path or body (`compare`'s `against`,
     `record_split`'s parts);
   - `api/blobs.py`: the pre-check only on upload and completion; on download, a scope-aware
     owner check — a workspace-wide `dataset:read` keeps today's `blob_readable_by` answer; a
     scoped one is admitted only through an owning Dataset Version whose Dataset it covers.
     Refused is the same 404 as today (`blob_not_found`), so a blob's existence is not disclosed;
   - `api/reference_tables.py`: **no change**. The bare `requires(DATASET_READ)` is correct.
3. **Acceptance, red first** (each test fails at base and passes after):
   - a principal with `dataset:read` scoped to Dataset X reads X's version profile → 200; Y's →
     403 `SCOPE_DENIED`; a principal with no `dataset:read` → 403 `PERMISSION_DENIED` for an
     unknown version id (not 404);
   - the same scoped `dataset:write` principal gets an upload URL, completes the upload, and
     ingests into X → 202; ingest into Y → 403 `SCOPE_DENIED` (this one needs
     `POST /datasets/{slug}/versions` in the slice, item 4);
   - scoped download of a blob owned by X's version → 307; of one owned only by Y's version →
     404;
   - a dataset-scoped principal on `GET /reference-tables` → 403 `PERMISSION_DENIED` (pins (C)'s
     refusal, so a later widening is a visible decision).
4. **For the maintainer, not ruled here: the same class outside the three named files.** The
   FD 8177 sweep lists more `DATASET_*` route-level guards with no handler scope check:
   `api/datasets.py`:87–88 (the single-Dataset routes `GET /datasets/{slug}` :433→436,
   `POST /datasets/{slug}/versions` :515→521, `GET /datasets/{slug}/versions` :588→593,
   `GET /datasets/{slug}/versions/{version}` :647→652, `GET /dataset-versions/{version_id}`
   :662→667, the schema patch :751→756) and `api/validation.py`:67. The principle above
   covers them, and **ingestion (`:515`) is needed for the end-to-end case in item 3**. The
   recommendation is that they join this slice. The list routes (`GET /datasets`, sources)
   stay workspace-wide under the principle. The raise named three files, so including the
   others is the maintainer's call.

## Acceptance — the violation that must become detectable

The violations, and what catches each:

- *A Dataset Version or blob route keeps a bare route-level `requires(DATASET_*)`, so a
  dataset-scoped grant is refused with `PERMISSION_DENIED` on its own Dataset.* Caught by the
  red-first tests in "What it obliges" item 3 (200 / 202 / 307 for the in-scope principal).
- *The scope check is dropped and the "held under any scope" pre-check is left alone, so a
  one-Dataset grant reads every Dataset's versions.* Caught by the Dataset-Y control in item 3,
  which asserts 403 `SCOPE_DENIED` (code, not only status), and by the download control (404).
- *A route looks up a dataset id before any permission check, so a caller with no grant gets 404
  instead of 403.* Caught today by `test_every_operation_refuses_a_caller_holding_no_roles`
  (`backend/tests/test_api_authorisation_sweep.py`:367), which fills each path parameter with an
  unknown UUID and asserts 403. These routes must not be added to `RESOURCE_BACKED` (:299) to make
  it pass; RL 8176's guard test (Environment paths only) catches that.
- *A route pairs a scope-less route-level `requires()` with a handler scoped check.* Caught by PL
  8181's regression guard (the maintainer's 17:27:15 entry), once it lands.
- *Reference tables are widened to a dataset-scoped grant without a decision.* Caught by item 3's
  last test (403 `PERMISSION_DENIED` on `GET /reference-tables`).

This seat runs no tests, so none of these has been shown red here.

## Also found (not ruled; for the lead to route)

`docs/specs/03-rating-engine.md`:1080 and :1083 require "`dataset:read` on the portfolio Dataset
Version" for Dislocation Runs, and `api/dislocation_runs.py`:50–53's docstring says the check is in
the handler "(FR-345)". The code passes **no resource**: `api/dislocation_runs.py`:54–59, and the
same in `api/rate_tables.py`:432–437 and :530–535. So it checks `dataset:read` workspace-wide and
refuses a dataset-scoped grant on its own portfolio. The FD 8177 sweep's predicate 2 (`ResourceRef(` /
`resource=`) cannot see these sites, because they pass no resource. This is a spec/code
disagreement (`CLAUDE.md` §0: resolve, not quietly match), not decided here.

## Revisit trigger

Reopen the reference-table answer if `ScopeType` gains a reference-table scope, if FR-345's scope
list changes, or if a Dataset's validation depends on a reference table the scoped analyst must
read to fix its own data.
