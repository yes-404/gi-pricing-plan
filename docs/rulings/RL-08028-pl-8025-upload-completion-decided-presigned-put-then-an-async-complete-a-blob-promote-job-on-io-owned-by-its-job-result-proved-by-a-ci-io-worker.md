---
id: RL-8028
family: ruling
title: WK-1178's upload-completion decision points — (a2) a presigned PUT then an async complete, a blob.promote Job on io; its Job result owns the blob; a pending Blob Upload record authorises it; the slice's one public-path test runs its own io worker in CI
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-14
owner: decision-maker
tree: 4420f91fa4112a1fcabcae23d3d50a1ad4fcbb59
phase: P2
work: WK-1178
slice: SL-8026
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-8025, SL-8026, FR-418, FR-419, FR-420, FR-421, FR-27, FR-405, FR-416, FR-417, FR-436, WK-1178, WK-1251, SL-1258]
---

# RL-8028 — PL-8025 DP-U1 to DP-U3: how a presigned upload becomes an owned, content-addressed blob

*Disclosure: drafted under **working id RL 8028**, reserved by the lead (team-lead) on
2026-10-14 (`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-14 11:09:44
BST": "RESERVED working id RL 8028 = the upload-completion DP ruling (PL 8025 DP-U1, U1.1, U1.2,
U2, U3), seat dm-upload"). The plan it rules on, `PL-8025`, and its slice, `SL-8026`, are also
working ids (reserved "2026-10-14 10:57:11 BST"), filed on
`origin/pl-8025-wk1178-upload-completion-2026-10-14` @`78e58ff0636a255cc55414f3c8f80b5e26c576b8`.
FD 8021, FD 8023 and PL 8022 are working ids and are cited in the body only. The lead mints all
of them; the mint sweep replaces the working ids below with their minted ids. Written 2026-10-14
from 11:16:29 BST by the decision-maker (dm-upload, separate CLI, effort high: the lead's message
of 2026-10-14 confirming "perTurnEffort":"high" on this transcript).*

*2026-10-14: per the maintainer's (by delegation) "2026-10-14 11:24:38 BST — RL 8028 (upload completion) CONFIRMED as drafted; the no-seeding carve-out ACCEPTED; FD 8023's check widened (re lead 11:24:06)" (`to-lead.md`) — "RL 8028 @a8e1191a: CONFIRMED, no amendment." The carve-out, quoted: "The no-seeding carve-out: ACCEPTED (my dated line). 'Seeding' in my 10:56:38 (4) means writing a row the path under test would otherwise create (blob, blob owner, Blob Upload, Job, Dataset, Dataset Version). `principal`/`grant` are identity and provisioning, not seeding. The predicate binds as written: no `blob_fixtures` import, no `Database` session, and only the listed fixtures. The LG names the fixture set."*

## How this was ruled

- **The order is the maintainer's (by delegation)**, the entry "2026-10-14 10:56:38 BST —
  Upload-completion gap: owner WK-1178, FIXED IN P2 (spec first, off the G2 path); 2nd-pass counts
  noted (re lead 10:56:05)" in `~/gi-pricing-plan.local/channel/to-lead.md`, items 3 and 4
  verbatim: *"3. **Spec first (§0):** a planner drafts the plan with the completion step as a
  decision point. The design options (e.g. a presigned PUT then `POST …/uploads/{key}/complete`
  where the server hashes, promotes and writes the blobs row with its owner, versus a
  server-proxied upload; how the client learns the sha256; FR-421 multipart interplay) go to a
  DECISION-MAKER (effort high, separate CLI) with a recommendation. A new 07 FR for the completion
  step, and 01's ingest row amended to cite it, ship in the slice's commit. 4. **The test that
  would have caught it:** the slice adds ONE HTTP test that walks upload-url → PUT (to MinIO) →
  complete → POST versions → ingest `succeeded` on a real worker (with S4's io consumer), with no
  DB seeding. The existing fixtures stay for unit tests."*
- **The meaning of "a real worker" is the same author's**, the entry "2026-10-14 11:10:26 BST —
  Upload plan, the two points: "real io worker" defined (W2 OK, conditional); E4.3 may seed now,
  with the conversion an OBLIGATION (re lead 11:09:44)", item (a) verbatim: *"**(a) What my
  10:56:38 (4) "a real worker" means:** a separate Celery worker PROCESS that takes the Job from
  Redis by queue routing and runs it through the handler registry that `app.worker.entrypoint`
  builds, i.e. NOT inline `execute_job` and NOT a test-assembled registry. **W2 (the test starts
  its own io worker, runs in CI) satisfies it IF** that worker is launched as `celery -A
  app.worker.entrypoint worker --queues io` (or imports the entrypoint module unmodified). The test
  asserts the Job was consumed from the `io` queue and its status is `succeeded`. A worker that
  registers handlers itself would hide exactly the unregistered-handler defect found today, and
  does NOT qualify. W1 (compose) is not required for this slice. DP-U1/U1.1 remain the DM's (RL
  8028); this settles only the meaning of my words."* The lead relayed it as binding on this
  record (message to dm-upload, 2026-10-14: "Put that in RL 8028 as the binding reading").
- **The retention boundary is the same author's**, "2026-10-14 10:51:08 BST — FR-420 → WK-1251
  ACCEPTED; latent blob-GC DATA-LOSS finding …", item 3 verbatim in the part relied on: *"No
  non-dry `collect_garbage` is wired until every blob-owning artifact retains its blobs, proven by a
  DERIVED check (every `BlobStore.put` call site in backend/src is paired with a `retain` by its
  owning record, or is listed with a reason)"*; and "2026-10-14 10:57:10 BST — FD 8023 MEDIUM +
  trigger CONFIRMED …", item 1, which confirms FD 8023 "MEDIUM latent, owner WK-1251".
- **The options and the recommendation are the planner's**, `PL-8025` §Decision points (the
  branch named above), read in full; this record rules on them and does not edit the plan.

## Verified first, at `4420f91f`

Every line below was read at `origin/main` `4420f91fa4112a1fcabcae23d3d50a1ad4fcbb59` (re-read
11:16:29 BST, unmoved since 11:10:21 BST), by `git show origin/main:<path>`, never the root
checkout.

**PL-8025's premises, confirmed in the owning code:**

- **P1 (FR-421 half-built) — confirmed.** `docs/specs/07-platform.md:115` is FR-421: "Large
  uploads use presigned multipart URLs so dataset files do not transit the API process."
  `BlobStore.presign_upload` (`backend/src/app/platform/blobs.py:238-288`) mints
  `staging/{yyyy/mm/dd}/{uuid7}` (`:255`), presigns one `put_object` for one part (`:257-264`,
  `upload_id` left `None`) or calls `create_multipart_upload` (`:266-271`) and presigns one
  `upload_part` URL per part (`:273-286`). Its docstring (`:241-248`) says the completion step
  "is not built". `expires_in_s` defaults to 3600 (`:239`).
- **P2 (a key, never a digest) — confirmed.** `backend/src/app/api/blobs.py:65-71`
  `UploadUrlResponse(key, upload_id, urls, expires_in_s)`; `parts` is `ge=1, le=10_000`
  (`:62`); the route (`:74-98`) takes no database dependency and records nothing. Its docstring
  (`:84-86`): "Asking the client for the digest up front would let it choose one, which is the
  difference between content addressing and client-supplied naming."
- **P3 (the spec names the gap) — confirmed.** `07-platform.md:327`, the upload-url row's
  2026-09-28 amendment: "the completion step FR-421 implies has no endpoint. So an upload made
  through this URL cannot yet be ingested or downloaded as a blob. The completion step, and the
  owner it would record, are unbuilt and are a spec change of their own."
- **P4 (an owned digest only) — confirmed.** `api/datasets.py:155` `blob: Annotated[str,
  Field(pattern=r"^[0-9a-f]{64}$")]`; `start_ingestion` refuses at `:543-546` (`if not await
  blob_readable_by(...): raise blob_not_found(body.blob)`) inside the unit of work, before
  `job_service.submit`. `blob_readable_by` (`blobs.py:508-534`) refuses any quote-input
  reference first (`:518-520`), then admits only a `DatasetVersionRow` table or a `JobRow` with
  `JobRow.workspace_id == workspace_id` and `JobRow.result.contains({"kind": "blob", "ref":
  sha256})` (`:526-529`). `01-data-management.md:858` states the same rule for the ingest route.
- **P5 (the ingest worker) — confirmed.** `platform/jobs.py:59` `JobKind.DATASET_INGEST:
  JobQueue.IO`; `_ingest` (`worker/data_handlers.py:108-155`) checks only that the `blobs` row
  exists (`:128-136`); its comment at `:122-127` ends "The worker-side check arrives with the
  owner record the upload-completion finding in #869 calls for."
  `backend/tests/test_ingest_enqueuers.py`'s module docstring (`:1-19`) carries the same
  promise: "the worker-side check arrives with an owner record (the upload-completion finding in
  #869)".
- **P7 (R1) — confirmed.** `07-platform.md:36`: "**R1 — Everything slow is a Job.** Any operation
  that can exceed 2 s returns `202` with a Job".
- **P8 (retention) — confirmed.** `BlobStore.put` adds `BlobRow(..., ref_count=0)`
  (`blobs.py:185-187`); `retain` (`:439-441`); `collect_garbage` (`:379`) selects
  `BlobRow.ref_count == 0, BlobRow.created_at < cutoff`. FD 8023's remedy items 1 and 2, on
  `origin/fd-8023-blob-gc-unretained-2026-10-14` @`b94883a70f5831e65032523bb9b899986e7c38af`
  (`docs/findings/FD-08023-…md:176-180`), verbatim: "1. **Retain at every owner.** Every
  blob-owning artifact takes a reference to its blob in the transaction that stores it, and
  releases it when the owner replaces or deletes the blob (row 2). 2. **A derived check, not a
  list.** Every `BlobStore.put` call site in `backend/src` is paired with a `retain` by its
  owning record, **or is listed with a reason**."
- **P9 (CI services) — confirmed, with one addition.** `.github/workflows/python.yml:132`
  `redis:`; `:247` `- name: Start MinIO`; `:306` `GIP_BLOB_ENDPOINT_URL: http://localhost:9000`.
  **The addition:** the MinIO step carries `continue-on-error: true` (`:249`), and the
  `blob_store` fixture skips when MinIO is unreachable (`backend/tests/conftest_db.py:203-216`).
  So a CI run in which MinIO failed to start is green with every blob test *skipped*. Acceptance
  item 9 below exists for that reason.
- **The worker entrypoint.** `backend/src/app/worker/entrypoint.py` runs FR-436's tenant-binding
  check at import (`:31-44`), builds the app (`:46`), and registers the data, model, rate-table,
  rating, scoring and dislocation handlers at module level (`:61-76`). Its docstring's own usage
  line is `celery -A app.worker.entrypoint worker --queues compute --concurrency 2`.
- **The relay.** `worker/tasks.py:77` publishes with `send_task(task, kwargs=payload,
  queue=queue.value)`; the queue comes from the outbox row (`platform/outbox.py:65`, `:118`),
  which takes it from `DEFAULT_QUEUE_FOR_KIND`. The Celery task id is not the Job id.
- **The Job's queue is public.** `packages/model-schema/src/model_schema/jobs.py:227`, `Job.queue:
  JobQueue`, so `GET /api/v1/jobs/{id}` shows which queue a Job was routed to.
- **Identity fixtures.** `backend/tests/conftest_db.py:219-283`, `grant`: in one unit of work it
  ensures the workspace row, seeds the built-in roles and the built-in validation-rule catalogue
  ("The catalogue arrives with the workspace, exactly as the roles do (FR-68)"), and adds a
  `RoleAssignmentRow` and a `WorkspaceMemberRow`. `principal` (`:330-332`) builds a `Principal`
  in memory and writes nothing.

**Three facts PL-8025 does not state, which change what the slice must build:**

1. **`job_kind` is a PostgreSQL enum.** `backend/src/app/db/models.py:135` `kind:
   Mapped[JobKind] = mapped_column(_pg_enum(JobKind, "job_kind"), ...)`. A `blob.promote` Job's
   INSERT fails with `invalid input value for enum job_kind` unless a migration adds the value.
   The pattern is `backend/migrations/versions/f3a7c1d9e2b4_rate_table_diff_cells_job_kind.py:29-39`:
   `ALTER TYPE job_kind ADD VALUE IF NOT EXISTS …` in `upgrade`, and a `downgrade` that keeps the
   value with the reason ("PostgreSQL cannot drop an enum value"). PL-8025 Task 3's migration
   "creates `blob_uploads`" only.
2. **`ListParts` pages at 1,000 parts; the route admits 10,000.** S3's `ListParts` returns at
   most 1,000 parts per call and signals more with `IsTruncated`; `parts` is `le=10_000`
   (`api/blobs.py:62`). A part check that reads one page refuses every valid upload above 1,000
   parts as "missing parts". *(S3 API behaviour from the API reference, not run here; the slice's
   unit test below makes it checkable.)*
3. **FD 8023's derived check is keyed on `BlobStore.put` call sites.** A promotion that writes a
   `BlobRow` without calling `put` is invisible to that check as worded (item 2 above). So where
   the promotion's row is written decides whether WK-1251's check can see it.

**Not verified here:** whether the compose MinIO accepts an `AbortIncompleteMultipartUpload`
lifecycle action, and what its own stale-multipart-upload expiry is. No spike was run by this
seat (no code, no tests, by brief). PL-8025 Task 0 is the spike; DP-U1.2 below is ruled so that
either answer leaves the invariant intact.

## Ruled

### DP-U1 — the completion design: **(a2)**, a presigned PUT, then `complete` answers `202` with a `blob.promote` Job on `io`

**Ruled (a2)**, with the refinements below, which become T1's text.

- `POST /api/v1/blobs/upload-url` records a **Blob Upload** (DP-U1.1) and returns its `id`
  beside the existing fields. The existing fields stay: the change is additive.
- `POST /api/v1/blobs/uploads/{id}/complete` reads the Blob Upload only (database, no S3 call),
  and answers `202` with the Job and `Location: /api/v1/jobs/{job_id}`, as the ingest route does
  (`api/datasets.py:562`). The path names the Blob Upload's `id`, not the staging key that the
  10:56:38 entry used as an example ("e.g."): a staging key contains `/` and is a storage
  detail, while the `id` is the record that authorises the completion.
- The `blob.promote` Job, routed `io` by `DEFAULT_QUEUE_FOR_KIND`, does in this order:
  1. **Checks the workspace.** It fails the Job unless its own `workspace_id` equals the Blob
     Upload's (DP-U3 below says why).
  2. **Confirms the bytes.** For a multipart Blob Upload it lists the parts, **following
     `IsTruncated` to the last page**, and fails with `VALIDATION_FAILED` naming each missing part
     unless the parts are exactly 1 to the declared count; then it calls
     `complete_multipart_upload` with that list. For a single-part Blob Upload it confirms the
     staging object exists (`head_object`). A part below the store's minimum size
     (`EntityTooSmall` at completion) fails the Job with `VALIDATION_FAILED`, never
     `JOB_HANDLER_FAILED`.
  3. **Hashes by streaming.** It reads the staged object once, in bounded chunks, to compute its
     SHA-256. It never holds the whole object in memory. `BlobStore.put` does
     (`b"".join(content)`, `blobs.py:157`), so the promotion does not call `put`.
  4. **Copies server-side.** Unless a `blobs` row for that digest exists (FR-419), it copies the
     staged object to `blob/{sha256[:2]}/{sha256}` with a managed copy that switches to multipart
     copy above the single-request limit (boto3's `copy`). No byte crosses the worker on the
     write side.
  5. **Commits once.** In one transaction it writes the `blobs` row if absent, as `INSERT … ON
     CONFLICT (sha256) DO NOTHING`, so that a concurrent promotion of identical bytes is FR-419's
     no-op and not a failed Job; takes **one** reference (`retain`, FR-420); and marks the Blob
     Upload promoted with the digest. A re-run that finds the Blob Upload already promoted
     returns the same result and takes no second reference.
  6. **Cleans up after the commit.** It deletes the staging object only after that transaction
     has committed. A failed delete is logged and left to the lifecycle rule (DP-U1.2). Deleting
     first would leave a retry with nothing to read if the commit failed.
  7. **Succeeds** with `JobResult(kind="blob", ref=<sha256>)`. The client reads the digest from
     `GET /api/v1/jobs/{id}`.
- **The promotion's `blobs` row is written inside `BlobStore`** (`blobs.py`, T4's
  `promote_upload`), next to `put`, the module's only other writer of that row. This keeps the
  row's writers in one module, which WK-1251's derived check has to enumerate (§What it obliges).

**Why (a2):** it is the only option that keeps both FR-421 ("dataset files do not transit the
API process", `07:115`) and R1 ("Any operation that can exceed 2 s returns `202` with a Job",
`07:36`). Hashing reads every byte. `01` §4.2's own example table blob is 412,000,000 bytes in 8
parts (`01-data-management.md:280`). The owner it records is one the allow-list already admits
(`blobs.py:526-529`), so neither `blob_readable_by` nor `01`'s ingest rule needs a new owner
kind.

**Why each other option loses:**

- **(a1) synchronous `complete`.** It moves the whole object through the API process to hash it,
  which is the cost FR-421 exists to avoid. The request lasts as long as that read, which breaks R1
  for any file big enough to need multipart. A proxy timeout mid-request drops the response, so
  the client cannot learn a digest the server may already have committed. Its one advantage, a
  single call, is not worth a breach of a §1.3 hard rule.
- **(b) proxied upload.** It contradicts FR-421 verbatim, so FR-421 would have to be amended.
  It holds an API worker for the length of every upload, and it leaves the presigned route dead.
  `put`'s whole-body join (`blobs.py:157`) would make a large upload an API-process memory
  event.
- **(c) client-computed SHA-256.** The server must still read every byte to verify the digest:
  an S3 multipart checksum is a checksum of part checksums, not the content's SHA-256. So the
  server does the same work as (a2), and the client must also hash. A browser's WebCrypto
  `digest` takes one buffer and cannot stream, so a large file needs a hashing library in the
  frontend, a `CLAUDE.md` §3 dependency change. It also gives the client the naming role that
  `api/blobs.py:84-86` refuses. A client that wants to check the result can compare its own local
  hash with the Job's `result.ref`. That needs nothing from the server.

### DP-U1.1 — the owner, and the pending record: **O1** plus a **Blob Upload** record

**The owner is the promotion Job's result (O1).** `JobResult(kind="blob", ref=<sha256>)` on a
`succeeded` Job in the Blob Upload's workspace is the owner `blob_readable_by` already admits
(`blobs.py:526-529`). The digest is then ingestible (`01:858`) and downloadable (`07:328`) in that
workspace and nowhere else. Neither rule changes. The owner is permanent, like every Job result.

**The pending record — a Blob Upload — is required before completion.** Today the staging key is
recorded nowhere (`api/blobs.py:74-98`). So nothing stops a `dataset:write` holder in another
workspace who learns a key from completing it and owning the bytes. The Blob Upload is one row
in a new table `blob_uploads`, written by `upload-url` in the caller's unit of work, with these
fields:

- `id` (uuid7);
- `workspace_id` and the requesting principal;
- the staging key, the S3 multipart upload id (null for one part), the declared part count and
  the media type;
- `created_at`, and `complete_by = created_at + 24 h`;
- the completing Job's id (null until completed);
- the promoted digest (null until promoted).

**Who may complete:** any caller with `dataset:write` in the Blob Upload's workspace. Another
workspace's Blob Upload, or a missing one, is refused with the same `404` problem body. **Not
"only the requesting principal":** the workspace is the platform's authorisation boundary for
every other route, and a principal match would add a rule no other route has. It would refuse a
service account's upload completed by a user, and it would protect nothing: the bytes land in the
same workspace either way. The requesting principal is recorded, and the Job's submitter is
audited by `job_service.submit` (`platform/jobs.py:145`).

**The deadline:** a completion after `complete_by` is refused with `409 VALIDATION_FAILED`. The
row is kept as the record. The presigned URLs still expire at `expires_in_s` (3600 s by default,
`blobs.py:239`). The longer completion window lets a client that crashed after uploading
complete the upload without uploading again.

**Repeat completion:** returns the Job recorded on the Blob Upload, whatever its state. A `failed`
promotion ends that Blob Upload: the client starts a new one. Re-completing after a failure has
little value, because the part URLs have expired by then. Allowing it would add a second Job per
Blob Upload, and with it a second path to the promotion's single reference.

**No separate audit event for `upload-url`.** `06`'s audit log is "the append-only record of
every state change that affects a price" (`06-governance.md:18`). A Blob Upload affects no price.
The Job submission is audited, and the Dataset Version that an ingestion produces is audited.

**Why each other option loses:** **O2** (the Blob Upload as a third owner kind) adds an entry to
an allow-list that is deliberately two entries long. It changes `01:858` and `07:328`, and it gains
nothing over O1 under (a2), where a Job exists to be the owner. O2 was the planner's fit for (a1),
which is not ruled. **O3** (no owner after an expiry) makes a Dataset Version's *source* upload
unreadable after a deadline, while the version that was ingested from it stays. A blob that the
platform holds and that its own workspace cannot download is not an obvious improvement, and the
release that would justify it is WK-1251's in any case.

### DP-U1.2 — retention and abandoned uploads

- **Retain at promotion, once per Blob Upload**, in the transaction that writes the `blobs` row
  (DP-U1 step 5; FD 8023 remedy item 1). A second Blob Upload of identical bytes takes a second
  reference, because it has a second owner.
- **Release is not built here.** O1's owner is permanent, so the promotion's reference is never
  released by this slice. Release and GC are FR-420's limb under WK-1251 (FD 8023), unchanged.
- **Abandoned bytes:** a lifecycle rule on the `staging/` prefix removes staging objects and
  incomplete multipart uploads older than **2 days**. `BlobStore.ensure_bucket` (`blobs.py:125`)
  sets it idempotently on every startup, so it holds under `docker compose up`.
- **The invariant, binding whatever the spike finds:** the completion deadline is shorter than
  every store-side removal of staged bytes. With a 24-hour deadline and a 2-day rule it holds.
  PL-8025 Task 0's spike records two facts in the slice's `LG-`: whether the compose MinIO accepts
  an `AbortIncompleteMultipartUpload` action, and MinIO's own stale-multipart expiry. Then:
  - **The store refuses the action.** The slice sets the expiration-only rule on `staging/`,
    which S3 and MinIO both accept, and the `LG-` records that MinIO's own stale-upload expiry
    removes incomplete uploads in its place.
  - **That expiry is 24 hours or less.** `complete_by` is lowered to half of it.
  - **Either case.** The lead is told before Task 3.
  `ensure_bucket` fails loudly if the store refuses the rule form that the spike proved. It never
  starts silently without a rule.
- **A note for WK-1251, not ruled here:** FR-423 (blob store versioning) is WK-1251's (the
  maintainer's (by delegation) entry "2026-10-14 11:00:31 BST"). On a versioned bucket an
  expiration rule only adds a delete marker. When versioning lands, the `staging/` rule needs a
  noncurrent-version expiration too.

### DP-U1.3 — multipart interplay (no recommendation changed)

Ruled as PL-8025 recommends, option (ii): the Job lists the parts. The client never sends ETags,
so the bucket's CORS need not expose `ETag`. The only change is DP-U1 step 2's pagination. The
copy is the managed copy (step 4). `part_count` is the declared count for a multipart Blob
Upload, and null for one part (`BlobRef.part_count`, as in `01` §4.2's example).

### DP-U2 — the one HTTP test's `io` worker: **W2**, under the maintainer's binding reading

**Ruled W2: the test starts its own `io` worker and runs in CI on every pull request.** The
11:10:26 entry, item (a), quoted above, is **the binding reading** of 10:56:38 (4)'s "a real
worker". Under it, W2 qualifies only if all three of these hold, and the slice is held to all
three:

1. **The worker is a separate process launched from the unmodified entrypoint:** `uv run celery -A
   app.worker.entrypoint worker --queues io` (PL-8025's `--pool solo --concurrency 1` are
   permitted: they size the pool and do not touch the registry). The test file never imports
   `app.worker.entrypoint` and never registers a handler. It never calls `execute_job` or any job
   runner. A worker that registers handlers itself does not qualify, because it would hide the
   unregistered-handler defect FD 8021 found today. **So `blob.promote` must be registered in
   `entrypoint.py`**, or the test cannot pass.
2. **The Job is taken from Redis by queue routing.** The test drives the relay with
   `outbox.relay_once` (as `test_celery_broker.py` does), which publishes to the queue that the
   outbox row carries (`outbox.py:118`, `tasks.py:77`).
3. **It asserts consumption from `io` and `succeeded`, for both Jobs** (the promotion and the
   ingestion): `GET /api/v1/jobs/{id}` shows `queue == "io"` and `status == "succeeded"`.
   `failed` is also terminal, so the test never asserts "terminal". The fixture records the
   worker's argv and captured output, and the slice's `LG-` quotes the worker's start-up banner
   with its queue list (`io` only) and the receipt lines of the two tasks. The Celery task id is
   not the Job id (`tasks.py:77`), so the receipt lines are evidence for the `LG-`, not the
   test's own assertion.

**Why W2 over W1:** W2 is the only option under which the test that "would have caught it" runs
on every pull request. W1 runs only with `GIP_DEPLOY_TESTS=1` in a granted build window, never in
CI. Its helpers also seed by `psql` (PL-8025 DP-U2, W1). The 11:10:26 entry says "W1 (compose)
is not required for this slice". **W3 is not this record's to rule:** the conversion of PL 8022
E4.3's compose ingest test to the public path is an **acceptance line in SL-8026**, by the
11:10:26 entry, item (b), which the lead queued for D17 (`eta.md`, "2026-10-14 11:10:51 BST").

### DP-U3 — a worker-side ownership check: **(b) no, for `dataset.ingest`**; one consistency check in the new `blob.promote` handler

**`dataset.ingest`: (b), no worker-side ownership check.** `test_ingest_enqueuers.py` pins
`start_ingestion` as the only enqueuer by an AST census that fails closed (its docstring,
`:10-15`). That census already closes the bypass a worker check would guard. (a) would make
`examples/fremtpl2/seed.py`, and every test that enqueues `dataset.ingest` directly with an
unowned blob, fail and need an owner. That widens a small P2 slice into the seed and the
direct-enqueue tests, with no new protection. The trigger that `d068fb00` item 3 recorded ("the
worker-side check arrives with the owner record") was considered and is declined here. Both
places that promise it are rewritten to cite this record: `data_handlers.py:122-127` and
`test_ingest_enqueuers.py`'s docstring.

**`blob.promote`: the handler compares the Job's workspace with the Blob Upload's (DP-U1 step 1).**
This is not the check that (b) declines. Ingestion *consumes* ownership that the route has already
checked. Promotion *creates* ownership, and it creates it in the Job's own workspace (the owner is
the Job's result, matched on `JobRow.workspace_id`, `blobs.py:527`). A `blob.promote` Job
submitted with a workspace other than the Blob Upload's, by any future enqueuer, would grant
another workspace the bytes. The check is one comparison inside new code. It touches no existing
test or seed, and it makes an enqueuer census for `blob.promote` unnecessary: the failure cannot
survive the handler, whoever enqueues the Job.

### The no-seeding carve-out — identity fixtures are not "DB seeding" within 10:56:38 (4)

**Ruled: `principal` and `grant` are permitted in the one HTTP test.** 10:56:38 (4) names the
defect that the test must not reproduce. The entry's reads, item (ii): "every POST
/datasets/{slug}/versions test seeds an owned blob in the DB … so none walks the public path".
"Seeding" there means writing a row that the path under test would otherwise have to create. On
this path that means a blob, a blob owner, a Blob Upload, a Job, a Dataset or a Dataset Version.
`grant` writes none of those. It writes the workspace row, the built-in roles and the built-in
validation-rule catalogue that "arrives with the workspace" (FR-68), a role assignment and a
membership (`conftest_db.py:219-283`). That is the workspace's provisioning and the caller's
identity. Every HTTP test in the suite needs them, and no route under test creates them. An
identity cannot be bootstrapped over an API that refuses an unauthorised caller.

**The predicate, so the carve-out cannot widen silently:** the test file imports nothing from
`backend.tests.blob_fixtures`, opens no `Database` session, and uses no fixture other than
`principal`, `grant`, `api_client`, the settings and blob-store fixtures that build those, and the
worker fixture of DP-U2. Any fixture that writes a row of the six kinds above is seeding. The
slice's `LG-` names the fixture set. *This reads the maintainer's own word. As at 11:10:26 (a),
the maintainer may overrule it by a dated line, and the lead should route it there for
acceptance.*

### The spec text (T-text) the slice applies, replacing PL-8025's T1 to T6

The slice's commit replaces `<date>` with its own date, `FR-<n>` with the id that `python3
scripts/doc-id.py next` returns in that commit, and `RL-8028` with this record's minted id.
Where this text differs from PL-8025's T-text, this text governs (PL-8025 Task 0, first bullet).

**T1 — `07` §3.3, a new row appended after FR-423 (`07-platform.md:117`), with its anchor:**

> | **FR-<n>** | *(appended <date>, WK-1178, `SL-8026`; the completion step FR-421 implies, as `RL-8028` rules `PL-8025` DP-U1 to DP-U3)* **An upload completes into an owned, content-addressed blob.** `POST /api/v1/blobs/upload-url` records a **Blob Upload** in the caller's workspace (the requesting principal, the staging key, the S3 multipart upload id when `parts > 1`, the declared part count, the media type, and a completion deadline 24 hours after it is created) and returns its `id`. `POST /api/v1/blobs/uploads/{id}/complete` reads the Blob Upload only and returns `202` with a Job of kind `blob.promote` on the `io` queue (R1). The Job fails unless its workspace is the Blob Upload's. For a multipart upload it lists every uploaded part, across all pages, and fails with `VALIDATION_FAILED` naming each missing part unless they are exactly parts 1 to the declared count, then completes the multipart upload; for one part it confirms the staged object exists. It reads the object once, streamed in bounded chunks, to compute its SHA-256; copies it server-side to `blob/{sha256[:2]}/{sha256}` unless a blob with that digest is already stored (FR-419); and, in one transaction, writes the `blobs` row if absent (a concurrent promotion of identical bytes is a no-op, not a failure), takes one reference (FR-420) and marks the Blob Upload promoted. A re-run of a promoted Blob Upload returns the same result and takes no second reference. Only after that transaction commits does it delete the staging object. It succeeds with `JobResult(kind="blob", ref=<sha256>)`, which is the blob's owner in the Blob Upload's workspace (§5.1, `GET /api/v1/blobs/{sha256}`), so the digest the client reads from `GET /api/v1/jobs/{id}` is one `01`'s ingest route accepts. The file's bytes never transit the API process (FR-421). A Blob Upload in another workspace, or none, is refused with the same `404` a missing one gets; a completion after the deadline is refused `409 VALIDATION_FAILED`; a repeated completion returns the Job of the first, whatever its state, and a failed promotion ends the Blob Upload. A part below the store's minimum size fails the Job with `VALIDATION_FAILED`. Staging objects and incomplete multipart uploads older than two days are removed by a lifecycle rule on the `staging/` prefix that the platform sets on startup; the completion deadline is always shorter than any removal of staged bytes. Releasing the reference is FR-420's, and is not delivered by this clause. |

**T2 — `07` §5.1, the upload-url row (`07-platform.md:327`): a dated line appended to its cell.
The 2026-09-28 text is not edited:**

> **Amended <date> (WK-1178, `SL-8026`, FR-<n>, `RL-8028`):** the request records a Blob Upload
> and the response also carries its `id`; `POST /api/v1/blobs/uploads/{id}/complete` (the next
> row) moves the staged object to its content address and records its owner. The 2026-09-28
> sentences saying nothing does so, and that such an upload cannot be ingested or downloaded, are
> superseded.

**T3 — `07` §5.1, a new row directly after the upload-url row:**

> | `POST` | `/api/v1/blobs/uploads/{id}/complete` | **202** Complete a Blob Upload → Job `blob.promote` (FR-<n>, FR-421). The Job's result, `JobResult(kind="blob")`, names the digest and is its owner in the caller's workspace. `404` for another workspace's Blob Upload or a missing one; `409 VALIDATION_FAILED` past the completion deadline; a repeat returns the first Job. Requires `dataset:write`. *(appended <date>, WK-1178, `RL-8028`)* |

**T4 — `07` §5.2, one signature appended under `# backend/app/platform/blobs.py`
(`07-platform.md:389-392`):**

> `async def promote_upload(upload_id: UUID) -> BlobRef   # FR-<n>; runs in the blob.promote Job; idempotent per Blob Upload`

**T5 — `07` §2, the Job Kind row (`07-platform.md:57`):** add `blob.promote` to the parenthesised
list, after `dataset.ingest`.

**T6 — `07` §2, a new glossary row directly after Blob (`07-platform.md:59`).** This is new to
PL-8025. `spec-change`: "A new term goes in the glossary **before** first use". "Blob Upload" is
used nowhere in `docs/specs` at `4420f91f` (`git grep -n -w -E 'Upload|Uploads' origin/main --
docs/specs` printed nothing), and platform terms such as Blob, Job and Job Kind are defined in
`07` §2, not in `00` §2:

> | **Blob Upload** | A pending client upload to the blob store's staging area, recorded when an upload URL is issued: its workspace, principal, staging key, declared parts and completion deadline. Completing it promotes the bytes to a Blob owned in that workspace (FR-<n>). *(appended <date>, WK-1178, `RL-8028`)* |

The term is "Blob Upload", not PL-8025's bare "Upload": "upload" is a verb and an ordinary noun
throughout the suite. The table name `blob_uploads` and the class `BlobUploadRow` that PL-8025
Task 3 already names match this term.

**T7 — `01` §5.1, the ingest row (`01-data-management.md:858`): a dated line appended to its
cell. The 2026-09-28 text is not edited:**

> **Amended <date> (WK-1178, `SL-8026`, `RL-8028`):** a client obtains an admissible digest
> through `07` FR-<n>: request an upload URL, upload, complete the Blob Upload, and read the digest
> from the completing Job's result, which is the owner the rule above admits. The client never
> names a digest before the platform has computed it.

## What it obliges

**The slice (`SL-8026`, executor), in addition to PL-8025 Tasks 0 to 4:**

1. **Apply T1 to T7** in the slice's first commit (spec first), via `spec-change`, with
   `<a id="fr-<n>"></a>` before T1's row.
2. **The migration adds the enum value as well as the table:** `ALTER TYPE job_kind ADD VALUE IF
   NOT EXISTS 'blob.promote'` (the `f3a7c1d9e2b4` pattern) beside `CREATE TABLE blob_uploads`.
   The downgrade drops `blob_uploads` and keeps the enum value, with the reason written in the
   downgrade (FR-416). The chain keeps one head (FR-417).
3. **Register `blob.promote` in `backend/src/app/worker/entrypoint.py`.** Without it, DP-U2's
   worker cannot run the Job, and S4's E4.7 guard reds if S4 has merged.
4. **Write the promotion's `blobs` row inside `BlobStore`** (T4), never in the handler or the
   route.
5. **Rewrite the two promises that DP-U3 (b) declines:** `data_handlers.py:122-127` and
   `test_ingest_enqueuers.py`'s docstring. Each cites this record.
6. **The reds and breakers in the Acceptance section below**, in addition to PL-8025's R1 to R9.

**The lead:**

- **Mint this record with PL-8025 and SL-8026.** PL-8025's Activation item 1 ("DP-U1 ruled …
  with DP-U1.1 to DP-U1.3 and DP-U3 in the same `RL-`") and item 2 ("DP-U2 ruled. Under W2, no
  dependency on S4") are discharged by this record once it is minted.
- **Route the no-seeding carve-out to the maintainer** for a dated acceptance line, as stated
  under that ruling.
- **For FD 8023 / WK-1251 (not ruled here, which is the FD's and the maintainer's):** as
  worded, FD 8023's derived check counts `BlobStore.put` call sites. The promotion writes a
  `BlobRow` through `promote_upload`, not `put`. The check needs to count every writer of a
  `BlobRow` (at this tree, `put` only; after SL-8026, `put` and `promote_upload`), or the
  promotion's retain is outside its sight. It is in sight only because it lives in the same
  module.

**Not decided here:** the release half of FR-420 and any `blob.gc` handler (FD 8023, WK-1251).
An upload UI. PL 8022's E4.3 conversion (the 11:10:26 entry, item (b)). FR-421's part-size
guidance to clients beyond the store's own minimum. Whether `00` §2's "a new term must be added
here" should also list module-glossary terms such as Blob: T6 follows the suite's existing
practice and does not rule on that rule.

## Acceptance — the violation that must become detectable

The violation: **a file that reaches the platform only through its public API cannot become an
ingested Dataset Version, or becomes one in the wrong workspace or from the wrong bytes, and no
test fails.** Each item names the broken input that it must red on. The slice's `LG-` shows each
red before it is filed (`CLAUDE.md` §13).

1. **The public path (PL-8025 R1, unchanged).** *Violation: any break between upload-url and an
   ingested `draft` version.* It is red on `main` by `KeyError: 'id'`, then by FastAPI's own
   `404` for the absent route, then by `api/datasets.py:546`'s "Blob not found". It runs on the
   DP-U2 worker and asserts `queue == "io"` and `status == "succeeded"` for both Jobs.
2. **The unmodified registry (DP-U2 1).** *Violation: `blob.promote` not registered in
   `entrypoint.py`.* Breaker: delete the registration. R1 must then fail with the promotion Job
   not `succeeded`. A test-assembled registry would pass here, which is why it is not allowed.
3. **A truncated file (PL-8025 R6).** *Violation: a 2-part Blob Upload with only part 1 sent is
   promoted.* Breaker: drop the part check. The Job then `succeeded` with the digest of part 1
   alone.
4. **Pagination (new, R10).** *Violation: the part check reads one page.* A unit test feeds the
   part-listing function a stubbed client that returns two pages (parts 1–1000 with `IsTruncated`,
   then 1001–1002) for a declared count of 1002. It asserts success, and asserts refusal when part
   1001 is absent. Breaker: read the first page only. The complete upload is then refused as
   missing 1001–1002.
5. **Cross-workspace completion (PL-8025 R3).** *Violation: workspace B completes A's Blob
   Upload.* Breaker: drop the workspace filter. B then gets `202`.
6. **Cross-workspace promotion (new, R11, DP-U3).** *Violation: a `blob.promote` Job whose
   workspace differs from its Blob Upload's succeeds.* The test submits the Job directly through
   the job service (a unit test; the 10:56:38 entry: "The existing fixtures stay for unit tests")
   and asserts `failed`, with the digest not readable in the Job's workspace. Breaker: remove the
   comparison. The Job then succeeds, and `GET /api/v1/blobs/{sha}` answers `307` to the other
   workspace.
7. **One reference per Blob Upload (PL-8025 R8, plus new R12).** *Violation: a promotion that
   takes no reference, or a re-run that takes a second one.* After one promotion `ref_count ==
   1`. After running the handler a second time on the same Blob Upload it is still `1`. Breakers:
   drop `retain` (count 0), and drop the promoted-marker read (count 2).
8. **Clean-up after commit (new, R13).** *Violation: the staging object is deleted before the
   transaction commits.* The test makes the transaction fail (`retain` patched to raise) and
   asserts the staging object still exists and no `blobs` row exists. Breaker: move the delete
   before the commit. The staging object is then gone.
9. **Not skipped in CI.** *Violation: R1 skipped, which a green CI run permits when MinIO fails
   to start (`python.yml:249`, `continue-on-error: true`; `conftest_db.py:213-214` skips).* The
   slice's `LG-` quotes the CI job log at the slice head showing
   `test_upload_to_ingest.py::…` **PASSED**. A `SKIPPED` there fails acceptance.
10. **No seeding (the carve-out's predicate).** *Violation: R1 seeds a row of a kind its path
    creates.* `git grep -n -E "blob_fixtures|unit_of_work|session\.add|\.execute\(|Database\("
    <slice head> -- backend/tests/test_upload_to_ingest.py` prints nothing. This is PL-8025
    acceptance item 4's pattern, widened by `Database\(`. The `LG-` lists R1's fixtures.
11. **The spec text.** `git grep -n "FR-<n>"` (the minted id) at the slice head finds T1 in
    `docs/specs/07-platform.md`, T7 in `docs/specs/01-data-management.md`, and T6's
    `**Blob Upload**` row in `07` §2. `git log` shows the spec commit before every commit that
    touches `backend/src` (PL-8025 acceptance item 3).
