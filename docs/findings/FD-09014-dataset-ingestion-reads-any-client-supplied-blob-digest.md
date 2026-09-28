---
id: FD-9014
family: finding
title: Dataset ingestion reads any client-supplied blob digest
status: active
created: 2026-09-28
owner: auditor
tree: 4fb07b6cb17cacb2f6f578f264a36a455143c45f
corrected_by: []
relates: [FD-1203, WK-1178]
---

# FD-9014 — Dataset ingestion reads any client-supplied blob digest

**Severity: medium-high.** The auditor filed this finding on 2026-09-28, on the lead's
instruction and the deputy's decision on P1 in his entry in the lead's local channel file
`to-lead.md` stamped 2026-09-28 18:55:39 BST (line 8921). The deputy verified the defect at
`e6a9ca71`. The auditor re-read it at `origin/main` `4fb07b6c`.

## Finding

Starting an ingestion run names the source file by its blob digest, and the service accepts any
well-formed digest that exists in the blob store. It does not check that the caller's workspace
uploaded the blob or owns it. The blob table records no uploader and no workspace. So a caller
holding `dataset:write` in workspace A who knows a digest of workspace B's data can ingest B's
data into a Dataset Version in A, and then read it there. Once #868 (the blob-route fix, open at
this writing) scopes downloads by owning artifact, that Dataset Version would also make A count
as an owner of B's blob. This is the ingest-side twin of `FD-1203`'s exposure 2.

## Evidence

At `4fb07b6c`:

- **The request accepts any digest.** `backend/src/app/api/datasets.py:149` `class VersionCreate`
  has `blob: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]` (`:155`). The pattern is its
  only constraint.
- **The route passes it through.** `POST /api/v1/datasets/{slug}/versions`, `start_ingestion`
  (`:520`), takes `caller: WriteDatasets` (`:87`, `requires(Perm.DATASET_WRITE)`). It enqueues
  the job with `"blob": body.blob` (`:544`) and no ownership check.
- **The worker checks existence only.** `backend/src/app/worker/data_handlers.py:122` runs
  `row = await session.get(BlobRow, parameters["blob"])`. The only refusal that follows is
  `if row is None:` (`:123`–`:129`, a `NOT_FOUND`, *"The uploaded file is not in the blob
  store"*).
- **The blob records no owner.** `backend/src/app/db/models.py:274` `class BlobRow` has the columns
  `sha256` (primary key), `bytes`, `media_type`, `part_count`, `ref_count` and `created_at`. There
  is no uploader and no workspace.
- **The upload records none either.** `backend/src/app/api/blobs.py:78` `upload_url` issues a
  staging key. Its docstring reads *"The digest is not known until the bytes exist, so the object
  lands on a staging key"*, and the object is promoted to its address on completion (FR-421).
  The workspace is not captured anywhere along that path.

## Reachability of the digest

Exploitation needs another workspace's dataset digest. Those digests are in Dataset Version
responses, `tables[].blob.sha256` (`FD-1203` evidences the chain), but only **inside** the
owning workspace. A caller in A therefore needs a leak from B, or must be a member of both
workspaces. This is why the severity is medium-high rather than high. While `FD-1203`'s route
was unscoped, the same digests could be used to download directly.

## Disposition

**Fix in progress — owner the lead.** Event: a WK-1178 PR after #868 (the number follows). The
deputy chose option (a), with two design conditions:

1. **The owner is recorded at the point the digest exists.** The workspace is captured with the
   staging key when the upload URL is issued, and the (digest, workspace) owner row is written
   at promotion. Ingest refuses a digest that the caller's workspace neither uploaded nor already
   owns through a Dataset Version, using the same 404 body as a missing blob.
2. **Backfill.** The migration backfills owner rows from every existing Dataset Version's
   `tables` references, and from job results if the allow list uses the same table. The PR
   shows the backfill count and a positive control: a re-ingest in the owning workspace succeeds.
