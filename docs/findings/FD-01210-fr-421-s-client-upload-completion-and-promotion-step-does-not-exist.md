---
id: FD-1210
family: finding
title: FR-421's client-upload completion and promotion step does not exist
status: active
created: 2026-09-28
owner: auditor
tree: 5ec47dc46ac2f174c5d427f5558a6cb365ff8166
corrected_by: []
relates: [FD-1206, WK-1178]
---

# FD-1210 — FR-421's client-upload completion and promotion step does not exist

**Severity: medium.** The auditor filed this finding on 2026-09-28, on the lead's instruction and
the deputy's DP-P1 (C) decision (his entry of 21:39:48 BST, item 2: *"FR-421's gap is recorded,
not silent (CLAUDE.md §0: code and spec disagree)"*). It is a spec-versus-code disagreement, and
`CLAUDE.md` §0 says to resolve it rather than let either side quietly match the other. It is
medium because a requirement is typed delivered that is not, and because the missing step is why
`FD-1206`'s first design was built on a premise that was false. No data is exposed by it.

## Finding

`07-platform.md:115` (FR-421) reads *"Large uploads use presigned multipart URLs so dataset files
do not transit the API process."* The code issues the presigned upload URL and stops. The object
lands on a staging key, and **nothing completes the upload or promotes the object to its content
address**. So no client upload ever becomes a blob that ingestion can use.

Two docstrings say otherwise. They describe the promotion as if it existed:

- `backend/src/app/platform/blobs.py:231`, `presign_upload`: *"The digest is not known until the
  client has uploaded, so the object lands under a staging key and is promoted to its content
  address on completion."*
- `backend/src/app/api/blobs.py:118`, `upload_url`: *"…the object lands on a staging key and is
  promoted to its content address on completion."*

## Evidence

At `origin/main` `5ec47dc4`:

- `git grep -nE 'copy_object|staging/' -- backend packages` prints only
  `backend/src/app/platform/blobs.py:243` (the `staging_key` built in `presign_upload`) and a
  comment at `:286`. Nothing copies, moves or renames a staging object.
- `git grep -n 'BlobRow(' -- backend packages`, excluding tests, prints
  `backend/src/app/platform/blobs.py:176` only, inside `BlobStore.put`, which is a server-side
  write from bytes in memory. `db/models.py:274` is the class definition. No path creates a
  `BlobRow` from a client upload.
- `07` §5.1 lists `POST /api/v1/blobs/upload-url` (`:306`) and `GET /api/v1/blobs/{sha256}`
  (`:307`). It lists no completion route.
- **A record types it delivered:** `docs/closures/CR-00721-wk-660-data-workbench-closed.md:36`
  lists, among the WK-660 deliverables, *"(reassigned from WK-658) Blob endpoints, `/metrics` |
  Presigned upload and 307 download"*. I found no other record that does; the WK-692, WK-661 and
  WK-664 closures name only the content-addressed store.
- **The test evidence proves less than it looks:** `uv run python scripts/req-coverage.py` prints
  an FR-421 row with "10 test file(s)". The tests that carry the marker include
  `backend/tests/test_blobs.py::test_presigned_single_part_upload_is_usable`, which proves the
  presigned URL accepts bytes, and the route tests in `backend/tests/test_api_blobs.py`. **They
  prove a usable URL, not a completed upload.**

## Disposition

**Deferred with an owner — WK-1178.** The deputy declined building the completion step tonight
(DP-P1 option (A)) because its design is unsettled. It is built **spec-first**: an FR-421
amendment settles who completes the upload, how the digest is verified server-side, and where the
owner row is written, and then the code follows. This record proposes that the two docstrings
above are corrected in the P1 fix PR or in the fix for this finding, so that they stop describing
a promotion that does not exist. It also proposes that `CR-721`'s row is left as filed and this
record is what corrects the reading of it.

**The fix also carries the worker-side ingest check.** By the deputy's DP-P1-2 ruling (his entry of
2026-09-28 21:51:10 BST), the P1 fix for `FD-1206` checks ownership at the ingest **route** only.
Until the upload completion and its owner table exist, the route is the only enqueuer of
`JobKind.DATASET_INGEST` in `backend/src` (`api/datasets.py:540`, verified by the deputy at
`e1d050f7`), and an invariant test in the P1 PR pins that. When this finding's fix lands, the
worker's `_ingest` re-checks ownership too, using the owner table, and the worker's comment that
says the check is absent by design is removed in the same commit.

## Progress — the docstrings (2026-09-28)

#883 (`d068fb00`) corrected the two docstrings this record proposed correcting: `presign_upload` in
`platform/blobs.py` and `upload_url` in `api/blobs.py` now say the object lands on a staging key and nothing
yet promotes it, and the `07` §5.1 upload-url row carries a dated amendment. A grep for the old wording
("promoted to its content address on completion") in `backend` and `docs/contracts` finds nothing at `d068fb00`.
The completion step is still unbuilt, so this finding stays **active**.
