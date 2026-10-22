---
id: FD-8169
family: finding
title: BlobStore.ensure_bucket loses a head-then-create race on a fresh bucket, so a concurrent first start exits
status: active
created: 2026-10-22
owner: auditor
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
corrected_by: []
relates: [WK-1178, SL-1711, SL-8172, LG-8173]
---

# FD-8169 — BlobStore.ensure_bucket loses a head-then-create race on a fresh bucket, so a concurrent first start exits

## Finding

**MEDIUM; owner WK-1178.** Found by SL-1711 attempt 1 (W2). Severity accepted, and the fix ruled a P2 item to land
**before the 12 Nov exit demo**, by the maintainer's (by delegation) entry "2026-10-22 16:22:33 BST" (`to-lead.md`):
a fresh-install `docker compose up`, the documented deploy path, can fail at worker start on a new bucket, and the
exit demo shows the compose deploy. Filed under working id 8169.

`BlobStore.ensure_bucket` is documented "Idempotent, so startup can always call it" but is not idempotent under
concurrency: it heads the bucket, and on any `ClientError` creates it. Two processes starting together on a bucket
that does not yet exist both see the head fail, both call `create_bucket`, and the loser receives
`BucketAlreadyOwnedByYou`, which nothing catches. The startup call raises and the service exits.

## Evidence

At `origin/main` 71e481fa, `backend/src/app/platform/blobs.py`:

- :147-151, `_ensure()`: `try: self._client.head_bucket(...)` / `except ClientError: self._client.create_bucket(...)`.
  No code is inspected, and the create is not guarded.
- :140-145, the docstring: "Idempotent, so startup can always call it."

**The occurrence:** `~/gi-pricing-plan.local/scratch/sl1711-reds/w2-up-worker-io-exit.log`, SL-1711 W2 attempt 1: the
`docker ps` table shows `gi-pricing-worker-io-1 ... Exited (2) 19 seconds ago` (line 13) and the traceback ends
`botocore.errorfactory.BucketAlreadyOwnedByYou: An error occurred (BucketAlreadyOwnedByYou) when calling the
CreateBucket operation: Your previous request to create the named bucket succeeded and you already own it.` (line 120).

Not measured here: no concurrent-start reproduction was run for this record; the race is read from the code and
the log above.

## Interim control

The maintainer's (by delegation) entry accepts pre-creating the per-run bucket with `mc mb` before `up` as W2 setup;
LG-1841 discloses that this masks the product race in that run.

## Remedy (not made here)

The maintainer's (by delegation) entry names it: `ensure_bucket` treats `BucketAlreadyOwnedByYou` as success, and
`BucketAlreadyExists` by re-heading, re-raising when the bucket is not ours; the docstring's "Idempotent" claim is
corrected to hold under concurrency; red-first, two concurrent calls on a fresh bucket where one fails today and both
succeed after. The fixing slice is SL 8172 with LG 8173, branch `fix/fd-8169-ensure-bucket-race` @a32ac117 (unmerged
when this record was written).

## Disposition

Open, owner WK-1178; **fix before close**: SL 8172 (LG 8173), a WK-1178 delta row (Lean P2 L5). Closed in place, citing
the PR, when that slice merges. Filed under working id 8169.
