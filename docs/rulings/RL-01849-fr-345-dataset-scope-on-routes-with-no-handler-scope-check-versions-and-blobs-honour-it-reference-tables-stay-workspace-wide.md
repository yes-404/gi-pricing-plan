---
id: RL-1849
family: ruling
title: "FR-345 dataset scope on the routes with no handler scope check: Dataset Version routes and blobs honour a dataset-scoped grant, reference tables stay workspace-wide (adopted by the maintainer 2026-10-22 17:36:24 BST, as amended 17:38:11 BST)"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-22   # drafted and adopted 2026-10-22 under working id 8182; not minted
owner: decision-maker
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1301]
---

# RL-1849 — FR-345 dataset scope on the routes with no handler scope check: Dataset Version routes and blobs honour a dataset-scoped grant, reference tables stay workspace-wide

**Adopted by the maintainer, 2026-10-22 17:36:24 BST, as amended 17:38:11 BST.** Drafted by
the decision-maker (dm-8182) on 2026-10-22 and recorded as adopted by dm-8182b. The working ids
in prose (FD-1852, FD-1853, PL 8181, RL-1848, SL 8185) are not minted. The authority is item 1
of the maintainer's entry "2026-10-22 17:36:24 BST — Maintainer: RL-1849 ADOPTED, option (C);
the other single-Dataset routes join its slice; the id-oracle residual ACCEPTED; FD-1853 probe
GO" in `to-lead.md`, verbatim:

> 1. **ADOPTED: (C), per route by what it acts on:**
>    - dataset_versions.py :60–62 (11 routes) HONOUR the scope;
>    - blobs.py:52 upload-url/complete is "held under any scope", with the scope check at ingest;
>    - blobs.py:50 GET is scoped through the owning Dataset Version (job-only blobs workspace-wide; a refusal is the same 404);
>    - reference_tables.py:50 stays WORKSPACE-wide and **the spec records it** (not a Dataset, no ScopeType, outside FR-345; FR-350 never infers scope).
>    **Order: holds_anywhere → 403; load → 404; scoped → SCOPE_DENIED.** It applies to PL 8181's 3 routes too, and it is one more dated FR-343 sentence, minted with RL-1848's clause (one docs change, both sentences). **Owner:** WK-1178; **its own slice AFTER PL 8181's** (shared files are sequenced, not concurrent). The authority is this entry.

**The amendment that binds over item 1's placement.** The maintainer's entry "2026-10-22
17:38:11 BST — Maintainer: PL 8181 (FD-1852 fix) DP-0..DP-3 RULED; GO (SL 8185 / LG 8186); my
17:36:24 FR-343 placement AMENDED to FR-345" in `to-lead.md`, its DP-2 bullet verbatim:

> - **DP-2 = a dated FR-345 clause** stating the order. **This AMENDS my 17:36:24 item 1:** the scope-order sentence goes in **FR-345** (dataset scope), not FR-343, to avoid two rulings on one row (RL-1848's clause stays in FR-343). FR-343 carries a one-line pointer to FR-345. RL-1849 cites FR-345. The id-oracle residual is stated in the clause; no OQ.

So item 1's "one more dated FR-343 sentence" is **replaced**: the order sentence and the residual
go in a dated **FR-345** clause, and FR-343 gains only a one-line pointer to it ("What it
obliges" item 1). Items 2–4 of the 17:36:24 entry are recorded below ("What it obliges" items
2, 4 and 5; "Residual"). The draft text that follows ("Verified first", the options and "Why
(C)") is kept as drafted; where it said "recommended", (C) is now adopted.

**The question.** The maintainer's entry "2026-10-22 17:27:15 BST — Maintainer: FD-1852
CONFIRMED HIGH; planner GO for the fix slice; the FR-345 spec question goes to a decision-maker
in parallel" in `to-lead.md`, verbatim:

> - **The spec question** (DATASET_* permissions on blobs.py:50–52, dataset_versions.py:60–62 and reference_tables.py:50, which have no handler scope check: must a scoped grant be honoured there under FR-345?): **seat a decision-maker in parallel** for options plus one recommendation, as an RL draft. If it rules "honoured", its routes join the fix slice or follow it. The fix slice does NOT wait for this ruling.

## Verified first, at `71e481fa` (origin/main)

Paths are under `backend/src/app/` unless they start with `docs/`.

**1. How a scoped grant is refused today.** `api/authz.py`:170 `requires(permission)` calls
`rbac.require_permission` with no `resource` (:194–205). `platform/rbac.py`:205–217 `_covers`
returns `True` for a `workspace` assignment, and `False` for any scoped assignment when
`resource is None` (:209–212). So a route-level `requires(DATASET_*)` refuses a principal whose
only grant is scoped to one Dataset, with 403 `PERMISSION_DENIED`. The FD-1852 probe shows this
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

**6. The order rule now adopted.** RL-1848 (draft branch `draft/rl-8176` @`aab1b741`, adopted by
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

*Adopted as (C) by the maintainer, 2026-10-22 17:36:24 BST, as amended 17:38:11 BST.*

**Option (C) is adopted: split by what each route acts on.** The principle is one sentence:
**a `DATASET_*` permission is checked with the Dataset as the resource wherever the route acts on
one identifiable Dataset; where it acts on no Dataset, it is checked as "held under any scope"
only if the action binds to no Dataset's data, and workspace-wide otherwise.**

**The options considered.**

| | (A) Honour the scope on every route | (B) Workspace-only on all three files, written into FR-345 | (C) Per route, by what it acts on (adopted) |
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
   **Why not (B).** It keeps the defect FD-1852 calls HIGH, only renamed: a scoped grant that
   cannot read or validate its own Dataset's versions is the "legitimate scoped user locked out"
   case the maintainer's 17:27:15 entry ruled against.

**The refusal order (it interacts with RL-1848).** A dataset-scoped check needs the Dataset id,
so it comes after a lookup. RL-1848's FR-343 clause admits only the Environment exception to
"permission before lookup", and its reasoning names datasets as the protected case. So each route
in this ruling, **and each of PL 8181's three routes**, uses this order:

1. **"Held under any scope" before any lookup:** `rbac.holds_anywhere(permission)`
   (`platform/rbac.py`:219) false → 403 `PERMISSION_DENIED`. A caller with no grant learns
   nothing about which ids exist.
2. **Load:** unknown or other-workspace id → 404 `NOT_FOUND` (as `_scoped` does today).
3. **Scoped check** with `ResourceRef(ScopeType.DATASET, dataset_id)` → 403 `SCOPE_DENIED`.

**Residual — ACCEPTED** (item 3 of the maintainer's 17:36:24 entry). A principal that holds
the permission on *another* Dataset can tell an unknown id (404) from an out-of-scope one (403
`SCOPE_DENIED`): after the load, `SCOPE_DENIED` reveals that the id exists. The maintainer
accepted it, consistent with RL-1848 (A)'s reasoning: it is a workspace-internal oracle to an
already-privileged holder. It is limited to members of the same workspace who already hold the
permission; `SCOPE_DENIED` is `06` §5.1's actionable distinction; for `dataset_versions.py` the
ids are UUIDv7, not guessable slugs. **Revisit trigger:** if Dataset slugs or ids become
sensitive across scopes. Per the 17:38:11 DP-2 amendment, the residual is stated in the FR-345
clause, and there is no OQ.

**This order is one dated clause in `06` FR-345, not FR-343** (the 17:38:11 amendment): RL-1848's
clause stays alone in FR-343, and FR-343 carries a one-line pointer to FR-345.

## What it obliges

*As adopted, with the 17:38:11 BST amendment.*

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
   - `06` FR-345 gains, in the same dated clause: **Order, for a dataset-scoped check:** the
     permission is first checked as held under any scope, before any lookup (403
     `PERMISSION_DENIED`); the Dataset or Dataset Version is then loaded (404 `NOT_FOUND`); the
     scoped check follows (403 `SCOPE_DENIED`). It applies to every route this clause scopes,
     PL 8181's three routes included. **Residual, accepted:** a principal holding the permission
     on another Dataset can tell an unknown id from an out-of-scope one; revisit if Dataset slugs
     or ids become sensitive across scopes. (The 17:38:11 DP-2 amendment: this sentence is
     FR-345's, not FR-343's.)
   - `06` FR-343 gains **one line only**: a pointer that a dataset-scoped check's refusal order
     is FR-345's (RL-<n>). It gains no order sentence from this ruling; RL-1848's clause is
     FR-343's only dated clause from this batch.
   - `06` §3's `dataset:read` row (`06-governance.md`:273) gains "and Reference Tables,
     workspace-wide only (FR-345)". This records the pairing the code already has.
2. **The code, in one slice. Owner: WK-1178** (the maintainer's 17:36:24 item 1; the 17:38:11
   entry's DP-0 puts PL 8181's fix in WK-1178 too). **Sequencing:** this RL's slice runs
   **after PL 8181's slice (SL 8185)**, not concurrently with it — shared files are sequenced.
   It reuses SL 8185's `held_anywhere` helper (DP-1: `requires(perm, held_anywhere=True)`, built
   on `rbac.holds_anywhere`, `platform/rbac.py`:219) and SL 8185's permanent guard (task 5: an
   AST-based guard with an owned exclusion list). Until this slice lands, the guard's exclusion
   list holds this RL's routes; **this slice removes each entry as it fixes the route**. Content:
   - the "held under any scope" route dependency from SL 8185 (built on `rbac.holds_anywhere`, keeping
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
4. **The same class outside the three named files JOINS this slice** (the maintainer's 17:36:24
   item 2): `api/datasets.py`'s single-Dataset routes — ingest `POST /datasets/{slug}/versions`
   :515, detail `GET /datasets/{slug}` :433, versions `GET /datasets/{slug}/versions` :588,
   `GET /datasets/{slug}/versions/{version}` :647 and `GET /dataset-versions/{version_id}` :662,
   and the schema patch `PATCH /datasets/{slug}/versions/{version}/schema` :751 — and
   `api/validation.py`:67 (the `ReadDatasets` alias and the routes it guards). **Each route gets
   its own red-first test with a scoped principal**, and SL 8185's permanent guard covers them.
   The list routes (`GET /datasets`, sources) stay workspace-wide under the principle.
5. **FD-1853 — CONFIRMED, HIGH; its fix JOINS this slice** (the maintainer's 17:36:24 item 4
   and 17:41:48 item 2). `docs/specs/03-rating-engine.md`:1080 and :1083 require `dataset:read`
   on the portfolio Dataset Version, but `api/rate_tables.py`:430–437 and :528–535 (the diff and
   diff-cells routes) and `api/dislocation_runs.py`:50–59 `_require_dataset_read` (called at :79
   estimate, :105 start, :167 movers) call `rbac.require_permission` with no resource, so a
   dataset-scoped grant is refused with 403 `PERMISSION_DENIED`. Confirmed by probe
   `probe/fd-8184-portfolio-dataset-read` @`ee4e8596`
   (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/fd-8184/result.md`: `assert 403 in (200,
   202)`, server log `"permission":"dataset:read" … "scope":"workspace"`, `platform/rbac.py`:292).
   The fix uses this ruling's order and guard. **On the dislocation routes the portfolio
   `dataset_id` must be resolved first** — from the `DislocationSpec` on estimate and start,
   from the stored run on movers — **before** the `ResourceRef(ScopeType.DATASET, dataset_id)`
   is built; the rate-table diff routes resolve it from the `portfolio` query parameter. Each
   route red-first; the control asserts 403 `SCOPE_DENIED` (code, not only status), not the
   wrong-reason 403 the probe's control passed with.

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
  it pass; RL-1848's guard test (Environment paths only) catches that.
- *A route pairs a scope-less route-level `requires()` with a handler scoped check.* Caught by PL
  8181's regression guard (the maintainer's 17:27:15 entry), once it lands.
- *Reference tables are widened to a dataset-scoped grant without a decision.* Caught by item 3's
  last test (403 `PERMISSION_DENIED` on `GET /reference-tables`).

This seat runs no tests, so none of these has been shown red here.

## Also found — now routed

The draft's "Also found" note (the `03`:1080/:1083 vs no-resource `dataset:read` disagreement) was
raised as FD-1853, probed, CONFIRMED and graded HIGH; its fix joins this slice ("What it obliges"
item 5).

## Revisit trigger

Reopen the residual if Dataset slugs or ids become sensitive across scopes (the
maintainer's 17:36:24 item 3). Reopen the reference-table answer if `ScopeType` gains a reference-table scope, if FR-345's scope
list changes, or if a Dataset's validation depends on a reference table the scoped analyst must
read to fix its own data.
