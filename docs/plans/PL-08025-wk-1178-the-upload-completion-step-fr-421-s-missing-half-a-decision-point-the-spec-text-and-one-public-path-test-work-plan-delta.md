---
id: PL-8025
family: plan
kind: map
title: WK-1178 — the upload-completion step, FR-421's missing half — the completion design as a decision point, the spec text, one public-path HTTP test with no seeding, and slice SL-8026 — Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 4420f91fa4112a1fcabcae23d3d50a1ad4fcbb59
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-8026, SL-1258]                # PL-1714, FD-1713 and FD-1715 (working ids 8022, 8021, 8023 at filing, minted in D16) are cited in the body
---

# PL-8025 — WK-1178: the upload-completion step (Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5. WK-1178 is the
> standing maintenance Work and has no single map plan; this delta cuts one new slice, `SL-8026`,
> and changes no other slice. It is `draft` while DP-U1 and DP-U2 are open, and it does not
> decide either. Required sub-skill for the executor: `subagent-driven-development` or
> `executing-plans`. Bound skills: `spec-change` (the spec text lands first, in the slice's
> commit), `fastapi-service`, `python-package`, `python-test`, `contract-guard` (the generated
> OpenAPI regenerates), `dev-commands`, `git-hygiene`.

Working ids PL 8025 and SL 8026, reserved by the lead in `eta.md`, "2026-10-14 10:57:11 BST lead:
RESERVED working ids PL 8025 … and SL 8026". Written 2026-10-14 (from 11:04:18 BST) by the planner
(planner-upload). Evidence was read at `origin/main` `ba68a6da` and the branch was cut from
`4420f91f`; `git diff --stat ba68a6da 4420f91f` over every spec and source file cited below
changes only `docs/roadmap.md`, so each line number below holds at both trees.

## Authority

- **The ruling:** the maintainer's (by delegation) entry in `to-lead.md`, "2026-10-14 10:56:38
  BST — Upload-completion gap: owner WK-1178, FIXED IN P2 (spec first, off the G2 path); 2nd-pass
  counts noted (re lead 10:56:05)". Its items 2 to 4, verbatim:
  "2. **Owner WK-1178, FIXED IN P2 before the 4 Nov code freeze,** not carried to P3. It is the
  platform's front door, the gap is small, and §14 would otherwise carry an open HIGH across the
  phase boundary. It is OFF the G2 critical path and never displaces a G2 gate.
  3. **Spec first (§0):** a planner drafts the plan with the completion step as a decision point.
  The design options (e.g. a presigned PUT then `POST …/uploads/{key}/complete` where the server
  hashes, promotes and writes the blobs row with its owner, versus a server-proxied upload; how
  the client learns the sha256; FR-421 multipart interplay) go to a DECISION-MAKER (effort high,
  separate CLI) with a recommendation. A new 07 FR for the completion step, and 01's ingest row
  amended to cite it, ship in the slice's commit.
  4. **The test that would have caught it:** the slice adds ONE HTTP test that walks upload-url →
  PUT (to MinIO) → complete → POST versions → ingest `succeeded` on a real worker (with S4's io
  consumer), with no DB seeding. The existing fixtures stay for unit tests."
  Its item 1 files the finding (D16's last slot), which names #883's unowned deferral as part of
  it.
- **The reads:** the lead's from-lead entries "2026-10-14 10:56:05 BST", item (1) (the
  upload-404 reads by auditor-upload404 at `ba68a6da`), and "2026-10-14 10:56:41 BST", item (2)
  (the FR-421 read: "FR-421 (07:115) half-implemented … NOTHING calls complete_multipart_upload,
  hashes, moves to blob/{sha}, writes the blobs row or records an owner; it returns key +
  upload_id, not a sha256"). The maintainer's (by delegation) entry "2026-10-14 10:57:10 BST",
  item 2, confirms that read against the 10:56:38 ruling "unchanged".
- **The deferral this closes:** commit `d068fb00` (2026-09-28T23:27:39+01:00, #883, WK-1178). Its
  message, verbatim with one elision: "**Route-only, per the [the maintainer's (by delegation)]
  DP-P1-2 (2026-09-28, 21:51:10 BST), which withdraws the worker half of DP-P1.** The design in
  the earlier ruling assumed an upload-completion step that records an owner; that step does not
  exist in the code (`upload-url` returns a staging key, nothing promotes it or writes its `blobs`
  row), so the owner record it needed has nothing to attach to. It is a spec change of its own and
  is not built here." *(The bracket replaces a word our records bar; the commit's own text is
  unedited.)* Its item 3: "The worker-side check arrives with the owner record the
  upload-completion finding in #869 calls for." DP-U3 is about that sentence.
- **The neighbours:** FD-1713 (minted from working id 8021; the unconsumed-queue class, owner WK-674, HIGH
  confirmed by the maintainer's (by delegation) entry "2026-10-14 10:52:40 BST"), discharged by
  S4 (`SL-1258`) under PL-1714 (minted from working id 8022). FD-1715 (minted from working id 8023; blob GC and un-retained owners,
  MEDIUM latent, owner WK-1251, confirmed by the maintainer's (by delegation) entry "2026-10-14
  10:57:10 BST", item 1).

## Goal

A client can take a file from its disk to a `succeeded` Dataset Version through the public API
alone: upload by presigned URL, complete the upload, read the digest the platform computed, and
start an ingestion with it. The spec says how (a new `07` FR, two `07` §5.1 rows, `01`'s ingest
row), and one HTTP test walks that path with no row seeded, so the gap cannot reopen silently.

## Premises (read at `ba68a6da`; unchanged at `4420f91f`)

- **P1 — FR-421 is half-built.** `docs/specs/07-platform.md:115`: "Large uploads use presigned
  multipart URLs so dataset files do not transit the API process." `BlobStore.presign_upload`
  (`backend/src/app/platform/blobs.py:238-288`) mints `staging/{yyyy/mm/dd}/{uuid7}` (`:255`). For
  `parts == 1` it presigns one `put_object` and returns `upload_id=None` (`:257-264`); otherwise
  it calls `create_multipart_upload` (`:266-271`) and presigns one `upload_part` URL per part.
  `git grep -n complete_multipart_upload origin/main -- backend/src` prints nothing. Nothing
  hashes, copies to `blob/…`, writes a `blobs` row or records an owner.
- **P2 — the route returns a key, never a digest.** `POST /api/v1/blobs/upload-url`
  (`backend/src/app/api/blobs.py:74-98`) answers `UploadUrlResponse(key, upload_id, urls,
  expires_in_s)` (`:65-71`); `parts` is `ge=1, le=10_000` (`:62`). Its docstring (`:82-89`) says
  "an upload made through this URL cannot be ingested or downloaded as a blob today". No record
  of the upload is kept: the staging key is known only to the client that received it.
- **P3 — the spec names the gap and leaves it unowned.** `07` §5.1's upload-url row
  (`07-platform.md:327`), amended 2026-09-28: "the completion step FR-421 implies has no endpoint.
  So an upload made through this URL cannot yet be ingested or downloaded as a blob. The
  completion step, and the owner it would record, are unbuilt and are a spec change of their
  own." No FR governs a completion step.
- **P4 — the ingest route admits only an owned digest.** `VersionCreate.blob` is a 64-hex digest
  (`backend/src/app/api/datasets.py:150-160`). `start_ingestion` refuses any digest
  `blob_readable_by` rejects with `blob_not_found` (`:543-546`), the `404` a missing blob gets.
  `blob_readable_by` (`blobs.py:508-534`) is an allow-list of two owners in the caller's
  workspace: a Dataset Version's `tables[].blob` and a Job whose `result` contains
  `{"kind": "blob", "ref": <sha256>}` (`:528`); any quote-input reference refuses first. `01`'s
  ingest row (`01-data-management.md:858`) states the same rule.
- **P5 — the ingest worker.** `dataset.ingest` routes to `io` (`backend/src/app/platform/jobs.py:59`).
  `_ingest` (`backend/src/app/worker/data_handlers.py:108-155`) checks only that the `blobs` row
  exists (`:128-136`) and reads the blob whole (`:137`). It has no ownership check, by the
  2026-09-28 ruling (`:122-127`).
- **P6 — no test walks the public path.** Every `POST /datasets/{slug}/versions` test seeds an
  owned blob through `backend/tests/blob_fixtures.py` (`dataset_blob`, `job_blob`), which inserts
  `BlobRow` and an owner row directly: `test_api_datasets.py:200-201` and `:541-542`,
  `test_api_dataset_ingest_owner.py:39` (the lead's 10:56:05 reads). No test under
  `backend/tests` starts a Celery worker process: `git grep -n -E "start_worker|--queues"
  origin/main -- backend/tests` prints nothing. `test_celery_broker.py` drives the relay by
  `outbox.relay_once` (`backend/src/app/platform/outbox.py:95`) against the compose Redis.
- **P7 — a slow request is a Job.** `07` §1.3, R1 (`07-platform.md:36`): "Any operation that can
  exceed 2 s returns `202` with a Job". Hashing a file means reading every byte of it, and the
  route caps a file at 10,000 parts (`api/blobs.py:62`); `01` §4.2's own example table blob is
  412,000,000 bytes in 8 parts (`01-data-management.md:280`). No hashing rate was measured for
  this plan.
- **P8 — retention.** `BlobStore.put` writes `ref_count=0` (`blobs.py:186`); only `retain`
  (`:439`) raises it, and `collect_garbage` (`:379`) selects `ref_count == 0` past the grace
  period. FD-1715's remedy item 1 (its branch `fd-8023-blob-gc-unretained-2026-10-14` at
  `b94883a7`): "Every blob-owning artifact takes a reference to its blob in the transaction that
  stores it, and releases it when the owner replaces or deletes the blob." Its item 2 makes every
  new `put` site either retain or be listed with a reason. `blob.gc` has no handler, and FR-420
  is WK-1251's (P3), by the maintainer's (by delegation) entry "2026-10-14 10:51:08 BST", item 1.
- **P9 — the CI stack has the services.** `.github/workflows/python.yml` runs a `redis` service
  (`:132`) and starts MinIO on `localhost:9000` (`:247-276`); `GIP_BLOB_ENDPOINT_URL` points at it
  (`:306`). `backend/tests/conftest_db.py:205-214` skips a blob test when MinIO is unreachable.
- **P10 — S4's compose proof of `dataset.ingest` meets the same gap.** PL-1714 (branch
  `pl-8022-wk674-e42-derived-queues-2026-10-14` at `60338263`), E4.3 extended, adds
  `test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker`: "start one ingestion through
  `lb` by `POST /api/v1/datasets/{slug}/versions` (P6), the smallest source the existing ingest
  tests use". On the compose stack, with no completion step, the only way to hold a digest that
  route admits is to insert the owner rows by `psql`. This plan does not edit PL-1714; the lead is
  told (§Report to the lead).

## Decision points

DP-U1 and DP-U2 go to a decision-maker at **high effort, in a separate CLI**, per the 10:56:38
entry's item 3. The planner recommends; it does not rule.

*2026-10-14: per the maintainer's (by delegation) "2026-10-14 11:10:26 BST" (a) — what "a real worker" in the 10:56:38 entry's item 4 means: "a separate Celery worker PROCESS that takes the Job from Redis by queue routing and runs it through the handler registry that `app.worker.entrypoint` builds, i.e. NOT inline `execute_job` and NOT a test-assembled registry. W2 (the test starts its own io worker, runs in CI) satisfies it IF that worker is launched as `celery -A app.worker.entrypoint worker --queues io` (or imports the entrypoint module unmodified). The test asserts the Job was consumed from the `io` queue and its status is `succeeded`. A worker that registers handlers itself would hide exactly the unregistered-handler defect found today, and does NOT qualify. W1 (compose) is not required for this slice."*

*2026-10-14: per the maintainer's (by delegation) "2026-10-14 11:24:38 BST" — RL 8028 (working id), the ruling on DP-U1 to DP-U3: "CONFIRMED, no amendment" (read at `a8e1191a`); "The no-seeding carve-out: ACCEPTED". "Seeding" means "writing a row the path under test would otherwise create (blob, blob owner, Blob Upload, Job, Dataset, Dataset Version). `principal`/`grant` are identity and provisioning, not seeding." "RL 8028 rides D17 with PL 8025 + SL 8026."*

| DP | Question | Options | Recommendation | Kind | Blocking? | Resolved by |
|---|---|---|---|---|---|---|
| **DP-U1** | How does a presigned upload become an owned, content-addressed blob? | **(a1) Presigned PUT, then a synchronous `complete`.** `POST /api/v1/blobs/uploads/{id}/complete` completes the multipart upload, streams the object back from S3 through the API process to compute SHA-256, copies it to `blob/{sha[:2]}/{sha}` (or finds it there, FR-419), writes the `blobs` row and the owner, and answers `200` with the `BlobRef`. Simplest client: one call returns the digest. Costs: every byte crosses the API process on the read side, which is the cost FR-421 exists to avoid; the request lasts as long as the read, so it breaks R1's 2-second rule (P7) for any file large enough to need multipart, and a proxy timeout can drop a completed promotion on the floor. **(a2) Presigned PUT, then `complete` returns `202` with a Job** of a new kind `blob.promote` on the `io` queue. The route checks the Upload record only (DB, no S3 call). The Job calls `complete_multipart_upload` (or `head_object` for one part), reads the object once to hash it, copies it to its content address unless that digest exists (FR-419), deletes the staging object, writes the `blobs` row with `part_count`, retains it (FR-420, FD-1715), and succeeds with `JobResult(kind="blob", ref=<sha256>)`. The client learns the digest from `GET /api/v1/jobs/{id}`. Costs: two Jobs between file and Dataset Version (promote, then ingest); a new Job Kind, its handler and its registration (S4's E4.7 guard, if merged, reds until it is registered); an `io` consumer is needed for the upload path as it is already for ingest. **(b) Proxied upload through the API.** The client streams the body to a route that calls `BlobStore.put`. Smallest code (`put` exists). Contradicts FR-421 verbatim ("so dataset files do not transit the API process"), would need FR-421 amended, holds an API worker for the length of every upload, and leaves the presigned route dead. **(c) The client computes SHA-256 and the server verifies.** The client sends its digest with `complete`. Verification still reads every byte server-side (an S3 multipart checksum is a checksum of part checksums, not the content SHA-256), so it buys no server work over (a1)/(a2). A browser cannot stream a digest through WebCrypto (`digest` takes one buffer), so a large file needs a hashing library in the frontend, a §3 tech-dependency change. And the existing reason against client-named digests stands (`api/blobs.py:84-86`: "Asking the client for the digest up front would let it choose one"). | **(a2).** It is the only option that keeps both FR-421 (no upload bytes through the API) and R1 (nothing slow in a request). The owner it records is one the allow-list already admits (`blobs.py:528`), so `blob_readable_by` and `01`'s ingest rule need no new owner kind. The two-Job cost is the R1 pattern every other slow operation here already follows. | design (spec change) | **yes** — the FR text, the route shape and every red below depend on it | the decision-maker's `RL-`, high effort, separate CLI |
| **DP-U1.1** | What owns the blob after completion, and what records the upload before it? | **(O1) The promotion Job's result** (`JobResult(kind="blob")`, already an owner at `blobs.py:528`): no allow-list change; permanent, like every Job result. **(O2) A new Upload owner**: the Upload row, once complete, is a third owner kind in `blob_readable_by`, with an expiry after which it no longer admits. One more allow-list entry, and `01`'s ingest row and `07` §5.1's download row both change. **(O3) A pending record with expiry only**: no owner after the expiry; an ingestion must start inside the window. Under every option a **pending Upload record** is needed *before* completion: today the staging key is recorded nowhere (P2), so nothing could stop a `dataset:write` holder in another workspace who learns a key from completing it and owning the bytes. The record holds workspace, principal, staging key, the S3 upload id, declared parts, media type, created time and a completion deadline. | **O1 under (a2)**, with the pending Upload record for authorisation and idempotency. **O2 under (a1)**, which has no Job to be the owner. | design | yes, with DP-U1 | the same `RL-` |
| **DP-U1.2** | Retention and abandoned uploads | **Retain:** the promotion takes one reference in the transaction that writes the `blobs` row (FD-1715 item 1; a second upload of the same bytes takes a second). **Release:** O1's owner is permanent, so it never releases; O2/O3's expiry would release, but nothing runs a sweep (`blob.gc` has no handler; P8), so the release is WK-1251's under FD-1715 in every option. **Abandoned bytes:** an incomplete multipart upload is not listed as an object and is kept until aborted; a never-completed single-part staging object is kept forever. Option: a bucket lifecycle rule on the `staging/` prefix (expire objects and abort incomplete multipart uploads after N days), set idempotently by `BlobStore.ensure_bucket` (`blobs.py:125`) so it holds under `docker compose up` (R2). A completion after the deadline is refused (`409 VALIDATION_FAILED`), and the Upload row stays as the record. | Retain at promotion; the release is FD-1715's, recorded and not built here. The lifecycle rule with N = 2 days and a 24-hour completion deadline, **if** Task 0's spike shows the compose MinIO applies an `AbortIncompleteMultipartUpload` rule; if it does not, the rule is still set (it is S3's contract) and the `LG-` records MinIO's own behaviour. | design | no — the defaults apply unless the `RL-` changes them | the same `RL-` |
| **DP-U1.3** | Multipart interplay | **Part list:** (i) the client sends `[{PartNumber, ETag}]` with `complete`; a browser can read `ETag` only if the bucket's CORS exposes it; or (ii) the Job lists the parts (`list_parts`) and refuses unless they are exactly parts 1 to the declared count. **Part size:** S3 refuses a part below 5 MiB except the last (`EntityTooSmall` at completion); the Job maps it to a `failed` Job with `VALIDATION_FAILED`, never `JOB_HANDLER_FAILED`. **Copy:** one `CopyObject` request is limited to 5 GB, so the Job uses a managed multipart copy (boto3's `copy`). **`part_count`:** the declared count for a multipart upload, null for one part (`BlobRef.part_count`, `01` §4.2's example). | (ii), and the rest as stated. | design | no | the same `RL-` |
| **DP-U2** | Where does the one HTTP test get a real `io` worker before S4 merges? | **(W1) An activation need: S4 merged.** The test lives in `backend/tests/test_deploy_stack_runtime.py`, through `lb`, on S4's `worker` consuming `io`. It runs only with `GIP_DEPLOY_TESTS=1` in a build window the lead grants, never in CI, and that file's helpers seed the service account by `psql` (`_seeded_scoring_request` and the `UPDATE service_accounts` in S4's runtime test), which is DB seeding. **(W2) The test starts its own worker.** A fixture starts `celery -A app.worker.entrypoint worker --queues io --pool solo --concurrency 1` as a subprocess with the test process's settings, empties the `io` list first, drives the relay with `outbox.relay_once` (as `test_celery_broker.py` does), and stops the worker in teardown. It runs in the ordinary backend suite, so CI runs it on every PR; it does not depend on S4. **(W3) W2 now, and the compose proof after both merge:** PL-1714's compose ingest test walks the public path once SL-8026 is on `main`, instead of seeding. | **(W2), with W3's follow-up offered to the lead** (P10). W2 is the only option under which the test that "would have caught it" runs in CI. It is a real Celery worker process on a real broker, not an inline `execute_job`. If the maintainer reads "(with S4's io consumer)" as requiring S4's compose service, W1 applies and SL-8026 waits for S4's merge. | test design (the maintainer's wording) | **yes** — it decides an activation need | the maintainer's dated line, or the decision-maker's `RL-` with DP-U1 |
| **DP-U3** | Does the ingest worker now also check ownership (`d068fb00` item 3's stated trigger)? | **(a) Yes:** `_ingest` calls `blob_readable_by` with the Job's workspace and fails the Job on a refusal. Defence in depth if a second enqueuer appears. Cost: `examples/fremtpl2/seed.py` and the tests that enqueue `dataset.ingest` directly with an unowned blob (`d068fb00`: "trusted local code, not the route") start failing, and each needs an owner. **(b) No:** the route stays the only check, and `backend/tests/test_ingest_enqueuers.py` still pins the route as the only enqueuer. | **(b).** The census already closes the bypass the worker check would guard, and (a) widens a small P2 slice into the seed and every direct-enqueue test. The `LG-` records that the trigger in `d068fb00` item 3 was considered and declined, citing the `RL-`. | scope | no — default (b) | the same `RL-` |

## The spec text (T-text), applied in the slice's commit, not here

Written for DP-U1 **(a2)** with **O1** and DP-U1.2/U1.3 as recommended. If the ruling differs, the
decision-maker's `RL-` carries the replacement text and the slice applies that instead. The new
FR's id is the one `python3 scripts/doc-id.py next` returns in the slice's commit, written below
as `FR-<n>`. The slice's commit replaces `<date>`, `<n>` and the `RL-` reference.

**T1 — a new FR in `07` §3.3, appended after FR-423:**

> | **FR-<n>** | *(appended <date>, WK-1178, `SL-8026`; the completion step FR-421 implies, as `RL-…` rules `PL-8025` DP-U1)* **An upload completes into an owned, content-addressed blob.** `POST /api/v1/blobs/upload-url` records an **Upload** in the caller's workspace (the principal, the staging key, the S3 multipart upload id when `parts > 1`, the declared part count, the media type and a completion deadline of 24 hours) and returns its `id`. `POST /api/v1/blobs/uploads/{id}/complete` returns `202` with a Job of kind `blob.promote` on the `io` queue (R1). The Job lists the uploaded parts and refuses unless they are exactly parts 1 to the declared count; completes the multipart upload; reads the object once to compute its SHA-256; copies it to `blob/{sha256[:2]}/{sha256}` unless a blob with that digest is already stored (FR-419); deletes the staging object; writes the `blobs` row, with `part_count` set to the declared count for a multipart upload; and takes a reference (FR-420) in the same transaction. It succeeds with `JobResult(kind="blob", ref=<sha256>)`. That result is the blob's owner in the Upload's workspace (§5.1, `GET /api/v1/blobs/{sha256}`), so the digest the client reads from `GET /api/v1/jobs/{id}` is one `01`'s ingest route accepts. The file's bytes never transit the API process (FR-421). An Upload in another workspace, or none, is refused with the same `404` a missing one gets; a completion after the deadline is refused `409 VALIDATION_FAILED`; a second completion of the same Upload returns the first Job. A part below the store's minimum size, or a missing part, fails the Job with `VALIDATION_FAILED`. Staging objects and incomplete multipart uploads older than two days are removed by a lifecycle rule on the `staging/` prefix, which the platform sets on startup. Releasing the reference is FR-420's, and is not delivered by this clause. |

**T2 — `07` §5.1, the upload-url row (`07-platform.md:327`), a dated line appended to its cell;
the 2026-09-28 text is not edited:**

> **Amended <date> (WK-1178, `SL-8026`, FR-<n>):** the response also carries the Upload's `id`,
> and `POST /api/v1/blobs/uploads/{id}/complete` (the next row) moves the staged object to its
> content address and records its owner. The 2026-09-28 sentences saying nothing does so, and
> that such an upload cannot be ingested or downloaded, are superseded.

**T3 — `07` §5.1, a new row after the upload-url row:**

> | `POST` | `/api/v1/blobs/uploads/{id}/complete` | **202** Complete an upload → Job `blob.promote` (FR-<n>, FR-421). The Job's result, `JobResult(kind="blob")`, names the digest and is its owner in the caller's workspace. `404` for another workspace's Upload or a missing one; `409 VALIDATION_FAILED` past the completion deadline; a repeat returns the first Job. Requires `dataset:write`. *(appended <date>, WK-1178)* |

**T4 — `07` §5.2 (`07-platform.md:389-393`), one signature appended under `blobs.py`:**

> `async def promote_upload(session: AsyncSession, upload: Upload) -> BlobRef   # FR-<n>; runs in the blob.promote Job`

**T5 — `07` §2, the Job Kind glossary row (`07-platform.md:57`):** add `blob.promote` to the
parenthesised list.

**T6 — `01` §5.1, the ingest row (`01-data-management.md:858`), a dated line appended to its
cell; the 2026-09-28 text is not edited:**

> **Amended <date> (WK-1178, `SL-8026`):** a client obtains an admissible digest through `07`
> FR-<n>: request an upload URL, upload, complete it, and read the digest from the completing
> Job's result, which is the owner the rule above admits. The client never names a digest
> before the platform has computed it.

## Tasks

### SL-8026 — the slice row

| Field | Value |
|---|---|
| Scope | FR-<n> (new, T1) as ruled, the `07` §5.1/§5.2 and `01` §5.1 text (T2–T6), the Upload record, the `blob.promote` Job Kind and handler, the `complete` route, the staging lifecycle rule, the regenerated OpenAPI, one public-path HTTP test and the route-level reds. |
| Requirements | `07` FR-418, FR-419, FR-420 (the retain limb only), FR-421, FR-<n>, FR-416 and FR-417 (the migration); `01` FR-27 (the ingestion the test ends in). |
| Discharges | the upload-completion FD (D16's last slot or D17; no working id reserved at this delta's date). |
| Dependencies | DP-U1 and DP-U2 ruled; under W1, `SL-1258` merged. |
| Lane / order | WK-1178, off the G2 path; never displaces a G2 gate; merged before the 4 Nov code freeze. |

### Task 0 — the readiness reads and the spike (no code)

- Quote the `RL-` for DP-U1 to DP-U3 into the `LG-`, and apply its T-text if it differs from
  this plan's.
- Re-read P1 to P6 at the slice's base and record the tree.
- **Spike, read-only against the compose MinIO:** does `put_bucket_lifecycle_configuration` with
  an `AbortIncompleteMultipartUpload` rule on `staging/` succeed, and does
  `get_bucket_lifecycle_configuration` read it back? Record the MinIO image digest and the
  answer in the `LG-`. A refusal changes DP-U1.2's default, and the lead is told before Task 3.
- Under DP-U2 (W2): start `uv run celery -A app.worker.entrypoint worker --queues io --pool solo
  --concurrency 1` once against the test database, Redis and MinIO, and record that it reaches
  ready. The entrypoint runs FR-436's tenant-binding check at import (`entrypoint.py:31-44`); a
  refusal there is a fixture problem to solve in the test's environment, never by weakening the
  check, and the lead is told before Task 2.
- If `SL-1258` (S4) has merged: confirm its E4.7 guard (`backend/tests/test_worker_handler_coverage.py`)
  requires a handler for every routed kind, so `blob.promote` must be registered in
  `backend/src/app/worker/entrypoint.py`.

### Task 1 — the spec (first commit, `spec-change`)

Apply T1 to T6 to `docs/specs/07-platform.md` and `docs/specs/01-data-management.md`. Run
`python3 scripts/audit-docs.py`; it exits 0 apart from the standing base reds named in the `LG-`.

### Task 2 — the reds, committed before the implementation

Every red below is stated by its cause on `main`. A matching status with a different reason is a
plan defect, not a red; the executor records it and tells the lead.

**R1 — THE ONE HTTP test, no seeding.** New file `backend/tests/test_upload_to_ingest.py`, one
test, `test_a_file_uploaded_through_the_public_api_ingests_to_a_succeeded_version`, marked
`req("FR-<n>")`, `req("FR-421")` and `req("FR-27")`. Steps, all through `api_client` except the
two `PUT`s, which go straight to MinIO on the presigned URLs:

1. `POST /api/v1/datasets` with a fresh slug.
2. Build a CSV in memory whose first 5 MiB form part 1 and whose remainder is part 2, so the
   multipart path (DP-U1.3) is the one exercised. Use the column set the existing ingest tests
   use; read `test_api_datasets.py` and mirror it rather than inventing one.
3. `POST /api/v1/blobs/upload-url` with `{"media_type": "text/csv", "parts": 2}`; keep `id` and
   `urls`.
4. `PUT` each part to its URL (`httpx`, no auth headers: the URL carries its own).
5. `POST /api/v1/blobs/uploads/{id}/complete` → `202`; poll `GET /api/v1/jobs/{job_id}` to a
   bound, then assert `status == "succeeded"` and `result == {"kind": "blob", "ref":
   hashlib.sha256(csv_bytes).hexdigest()}`.
6. `POST /api/v1/datasets/{slug}/versions` with `{"blob": <that digest>, "filename":
   "upload.csv"}` → `202`; poll that Job and assert `status == "succeeded"` (never "terminal":
   `failed` is terminal) and `result["ref"]` starts `dataset_version:`.
7. `GET /api/v1/datasets/{slug}/versions/1` → `status == "draft"`.

**No seeding, as a predicate:** the file imports nothing from `backend.tests.blob_fixtures`, and
it opens no `Database` session that adds, updates or deletes a row. The caller's identity comes
from the existing `principal` and `grant` fixtures, which write a membership row; that carve-out
is identity, not the blob path, and the `LG-` names it for the lead's acceptance.

**The worker (DP-U2):** under W2, a module-scoped fixture starts
`uv run celery -A app.worker.entrypoint worker --queues io --pool solo --concurrency 1` with the
test process's environment, waits for it to report ready, empties the Redis `io` list first,
and terminates it in teardown. The test drives the relay with `outbox.relay_once(database,
CeleryPublisher(app))` in its polling loop. Under W1, the same steps run in
`test_deploy_stack_runtime.py` through `lb`, and `GIP_DEPLOY_TESTS=1` gates it.

**Red on `main`, by cause:** step 3's response has no `id` (`KeyError: 'id'`), because no Upload
is recorded (P2). The next two failure points, which the executor shows by stubbing past each
one and records in the `LG-`, are: step 5's route does not exist (FastAPI's own `404`, `{"detail":
"Not Found"}`, not the platform's problem body); and step 6, given a locally computed digest
with no completion, answers the platform's `404` "Blob not found" from
`api/datasets.py:546`, the public-path 404 of the lead's 10:56:05 reads.

**R2 to R9 — the route-level reds,** in a new file `backend/tests/test_api_blob_uploads.py`.
These may run the promotion inline through the job runner the other route tests use (the
10:56:38 entry: "The existing fixtures stay for unit tests"). For each new route, the red on
`main` is the route's absence; so each guard also carries a **breaker**, a one-line mutation of
the implementation that the `LG-` shows red by its named cause.

| # | Test | Asserts | Red on `main` by cause | Breaker and its red |
|---|---|---|---|---|
| R2 | `test_upload_url_records_an_upload_and_returns_its_id` | the response has `id`; an Upload row exists with the caller's workspace, the declared parts and the S3 upload id | `KeyError: 'id'` | — |
| R3 | `test_completing_another_workspaces_upload_is_the_missing_404` | workspace B completing A's Upload gets a `404` byte-identical to a random UUID's; no Job row | route absent | drop the workspace filter → `202` |
| R4 | `test_a_completion_past_the_deadline_is_refused` | `409 VALIDATION_FAILED`; no Job | route absent | drop the deadline check → `202` |
| R5 | `test_a_repeated_completion_returns_the_first_job` | same Job id; one `blob.promote` Job row | route absent | drop the idempotency read → two Job ids |
| R6 | `test_a_missing_part_fails_the_promotion_by_name` | a 2-part Upload with only part 1 sent: the Job is `failed`, code `VALIDATION_FAILED`, and its detail names part 2 | route absent | drop the part-list check → the Job completes the upload from the one part S3 lists and `succeeded` with the digest of part 1 alone: a truncated file promoted as whole, which is why the check exists |
| R7 | `test_identical_bytes_promote_to_one_blob` | two Uploads of the same bytes: one `blobs` row, `ref_count == 2`, one object under `blob/`, both staging keys gone | route absent | skip the existence check → a second `put` and a primary-key error |
| R8 | `test_a_promoted_blob_is_retained` | after one promotion, `ref_count == 1` | route absent | drop the `retain` → `ref_count == 0` |
| R9 | `test_a_promoted_digest_downloads_only_in_its_workspace` | `GET /api/v1/blobs/{sha}` → `307` for the uploading workspace, `404` for another | route absent (no digest exists to ask for) | remove the Job-result owner from `blob_readable_by` → `404` for the owner |

Plus, in `backend/tests/test_blobs.py`, `test_ensure_bucket_sets_the_staging_lifecycle_rule`:
`get_bucket_lifecycle_configuration` names the `staging/` prefix after `ensure_bucket`. Red on
`main`: `NoSuchLifecycleConfiguration`. Its form follows Task 0's spike.

### Task 3 — the implementation

Files, all in the slice's one PR (L1 (a')):

- `packages/model-schema/src/model_schema/jobs.py` — `JobKind.BLOB_PROMOTE = "blob.promote"`.
- `backend/src/app/platform/jobs.py` — `DEFAULT_QUEUE_FOR_KIND[JobKind.BLOB_PROMOTE] = JobQueue.IO`.
- `backend/src/app/db/models.py` — `BlobUploadRow` (the Upload record of T1).
- `backend/migrations/versions/<rev>_blob_uploads.py` — creates `blob_uploads`; reversible
  (FR-416); one head (FR-417).
- `backend/src/app/platform/blobs.py` — `presign_upload` records the Upload; `promote_upload`
  (T4); the lifecycle rule in `ensure_bucket`; the docstrings at `:238-249` say what the code now
  does.
- `backend/src/app/api/blobs.py` — `UploadUrlResponse.id`; the `complete` route (T3); the
  docstring at `:82-89` corrected.
- `backend/src/app/worker/data_handlers.py` (or a new `blob_handlers.py`, the executor's call,
  recorded in the `LG-`) and `backend/src/app/worker/entrypoint.py` — the `blob.promote` handler
  and its registration. Under DP-U3 (b), the comment at `data_handlers.py:122-127` that
  promises a worker-side check "with the owner record" is rewritten to cite the `RL-` that
  declined it.
- `docs/contracts/openapi/generated.json` — regenerated by `uv run python
  scripts/generate-contracts.py`, never hand-edited.
- The two test files of Task 2 and `backend/tests/test_blobs.py`.

The model shapes the routes take and return live in `model-schema` where a shape already exists
there (CLAUDE.md §2: nobody hand-writes a shape that already exists). `BlobRef` and `JobResult`
exist; reuse them.

### Task 4 — the gate and the closing acts

The full gate, both halves (CLAUDE.md §11), in the gate slot the lead grants. The `LG-` quotes
every red line of Task 2 and every breaker's red. The closing acts go in the slice PR's last
commit (the slice's `status:` and the roadmap row's closing line), per the slice brief.

## The write set

`docs/specs/07-platform.md`, `docs/specs/01-data-management.md`,
`packages/model-schema/src/model_schema/jobs.py`, `backend/src/app/platform/jobs.py`,
`backend/src/app/db/models.py`, one new file under `backend/migrations/versions/`,
`backend/src/app/platform/blobs.py`, `backend/src/app/api/blobs.py`,
`backend/src/app/worker/data_handlers.py` (or a new `backend/src/app/worker/blob_handlers.py`),
`backend/src/app/worker/entrypoint.py`, `docs/contracts/openapi/generated.json`,
`backend/tests/test_upload_to_ingest.py` (new), `backend/tests/test_api_blob_uploads.py` (new),
`backend/tests/test_blobs.py`, the slice's `LG-` under `docs/ledgers/`, `docs/roadmap.md` (the
`SL-8026` row's closing lines only), and `docs/INDEX.md` (regenerated).

**Shared paths for the lead's census:** `backend/src/app/platform/jobs.py` and
`backend/src/app/worker/entrypoint.py` with S4 (`SL-1258`, PL-1714 E4.2/E4.7, and DP-Q4 (a) if
ruled, which moves `LATER_PHASE_KINDS` into `jobs.py`); `docs/contracts/openapi/generated.json`
with any open slice that regenerates it; `backend/migrations/versions/` with any open slice that
adds a revision (FR-417's one head).

**Out of scope:** an upload UI (none exists; the lead's 10:56:05 reads, item (i)); the release
half of FR-420 and any `blob.gc` handler (FD-1715, WK-1251); the PL-1714 compose ingest proof
(P10).

## Acceptance Standard

1. **This delta passes the docs checks on its own branch**, check 31's working-id lines excepted:
   `python3 scripts/audit-docs.py` exits 0 apart from them.
2. **DP-U1 (with U1.1 to U1.3) and DP-U2 each carry a ruling** — the decision-maker's `RL-` (high
   effort, separate CLI), or for DP-U2 the maintainer's dated line — before Task 2 is committed.
   DP-U3 carries a ruling or the `LG-` records default (b). The `LG-` quotes each.
3. **Spec first:** in the slice PR, `git log --format=%s origin/main..<slice head> -- docs/specs`
   names a commit earlier than every commit touching `backend/src`, and `git grep -n "FR-<n>"`
   (with the minted id) finds the T1 row in `docs/specs/07-platform.md` and the T6 line in
   `docs/specs/01-data-management.md`.
4. **R1, no seeding:** `git grep -n -E "blob_fixtures|unit_of_work|session\.add|execute\(" <slice
   head> -- backend/tests/test_upload_to_ingest.py` prints nothing, and `uv run pytest -q
   backend/tests/test_upload_to_ingest.py` exits 0 with both Jobs printed as `succeeded` (under
   W1: `GIP_DEPLOY_TESTS=1 GIP_N_SHA=<slice head> uv run pytest -q
   backend/tests/test_deploy_stack_runtime.py -k upload` in the build window). The `LG-` quotes
   R1's red on `main` (`KeyError: 'id'`) and the two later failure points by their causes.
5. **R2 to R9 and the lifecycle test:** `uv run pytest -q backend/tests/test_api_blob_uploads.py
   backend/tests/test_blobs.py` exits 0; the `LG-` quotes each red and each breaker's red, each by
   its named cause.
6. **No upload byte through the API process:** `git grep -n -E "put_object|upload_part|\.put\("
   <slice head> -- backend/src/app/api/blobs.py` prints nothing.
7. **The contract:** `uv run python scripts/generate-contracts.py --check` exits 0, and
   `docs/contracts/openapi/generated.json` at the slice head contains the path
   `/api/v1/blobs/uploads/{id}/complete`.
8. **The migration:** `uv run pytest -q tests/test_repository_invariants.py -k one_head` exits 0
   (FR-417), and the revision's `downgrade` drops `blob_uploads`.
9. **The full gate, both halves** (CLAUDE.md §11) at the slice head, in a granted slot; the `LG-`
   names the tree.
10. **The deferral closed:** `git grep -n -E "completion step FR-421 implies is not built|cannot be
    ingested or downloaded as a blob today" <slice head> -- backend/src` prints nothing.

## Activation

`SL-8026` is GO-able when all of these hold:

1. **DP-U1 ruled** by a high-effort decision-maker in a separate CLI (the 10:56:38 entry, item 3),
   with DP-U1.1 to DP-U1.3 and DP-U3 in the same `RL-` or defaulted as above.
2. **DP-U2 ruled.** Under W2, no dependency on S4. Under W1, `SL-1258` merged with its `worker`
   consuming `io` (PL-1714 E4.2), with this slice's base containing it.
3. **The upload-completion FD minted** (D16's last slot, or D17 if D16 is full: `eta.md`'s D17
   queue, "2026-10-14 11:01:07 BST"), so the `LG-` can name what the merge discharges. It names
   #883's unowned deferral (the 10:56:38 entry, item 1).
4. **Its relation to FD-1713 stated in that FD:** the public upload path needs an `io` consumer
   twice (promotion and ingestion). Under W2, SL-8026's test brings its own; a deployed or
   compose stack has one only once S4 discharges FD-1713. Until then the path works in the test
   and in CI, not on `docker compose up`.
5. **The shared-path census** above, against whatever is open at GO.
6. **This delta set `active`** in the slice's activation commit, and the lead's GO. Off the G2
   path; merged before the 4 Nov code freeze.

## Report to the lead (not an edit to PL-1714)

P10: PL-1714's compose ingest proof cannot reach `POST /api/v1/datasets/{slug}/versions` with an
admissible digest through the public API until SL-8026 is on `main`. Unless it waits, it must
insert a blob and an owner by `psql`, which is the seeding the 10:56:38 entry's item 4 names as
the reason the gap went unseen. Whether S4's proof seeds, or waits for SL-8026 (DP-U2's W3), is
the lead's to route; this delta records the dependency and does not decide it.
