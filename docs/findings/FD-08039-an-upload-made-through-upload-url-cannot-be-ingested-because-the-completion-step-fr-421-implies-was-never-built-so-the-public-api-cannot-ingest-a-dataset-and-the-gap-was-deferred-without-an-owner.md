---
id: FD-8039
family: finding
title: An upload made through upload-url cannot be ingested, because the completion step FR-421 implies was never built, so the public API cannot ingest a dataset, and the gap was deferred 16 days without an owner
status: active
created: 2026-10-14
owner: auditor
tree: 8eaf6d5f9cd4204e1e077b44069d4afd395f1461
corrected_by: []
relates: [WK-1178, SL-8026, PL-8025, RL-8028, FR-421, FR-418, FR-419, FR-27, FR-405, FD-1715, P2]
---

# FD-8039 — `POST /blobs/upload-url` → PUT → `POST /datasets/{slug}/versions` ends in `404 Blob not found`

*(Filed under working id 8039, reserved by the lead; a minter folds it into the docs batch.
Authority for filing it as its own finding: the maintainer's (by delegation) entry
"2026-10-14 11:55:21 BST" in `channel/to-lead.md`: *"Upload-404 run (11:53:20): confirmed by the
public-API run … A SEPARATE FD, as you recommend, in D17, proposed HIGH, discharged by SL 8026.
The regression gets its own register row; the FD names #869/d068fb00's unowned deferral."*
The order to act on the gap is the same file's "2026-10-14 10:56:38 BST" entry, items 1 to 4.
Reads were made at `origin/main` `ba68a6daf3cfb7634258915a6e542bc658ae3f62`; the run was made at
`8eaf6d5f9cd4204e1e077b44069d4afd395f1461`, and `git diff --stat ba68a6da 8eaf6d5f` over
`backend/src/app/api/blobs.py`, `backend/src/app/api/datasets.py`,
`backend/src/app/platform/blobs.py` and `docs/specs/07-platform.md` is empty, so the code and
spec under test are identical at both. The claim was raised by an auditor reading the essay for
FD-1713 (branch `fd-8021-unconsumed-queues-2026-10-14` @`cb64f336`); it is re-read and re-run
here, not copied.)*

## Finding

**Severity: HIGH, proposed by the auditor (to be ruled by the maintainer, whose expectation in
the 10:56:38 entry, item 1, is HIGH). Owner WK-1178, fixed in P2 by SL-8026 (`PL-8025`,
`RL-8028`) before the 4 Nov code freeze.**

A file uploaded through the platform's own upload route cannot become a Dataset Version. The
public API has no sequence of calls that takes a client's file to an ingested dataset:

1. `POST /api/v1/blobs/upload-url` returns a **staging key** and presigned PUT URLs, and **no
   sha256**.
2. The PUT to the presigned URL succeeds. The object lands on `staging/YYYY/MM/DD/<uuid7>`.
3. Nothing completes the upload. No code hashes the object, moves it to its content address
   `blob/{sha256[:2]}/{sha256}` (`07` FR-418), writes its `blobs` row, or records an owner.
4. `POST /api/v1/datasets/{slug}/versions` takes a 64-hex sha256 (`VersionCreate.blob`,
   `backend/src/app/api/datasets.py:153-158`) and refuses any digest that
   `blob_readable_by` (`backend/src/app/platform/blobs.py:508`) does not find owned by the caller's
   workspace. A freshly uploaded blob has no `blobs` row and no owner, so the route answers
   `404 NOT_FOUND "Blob not found"` (`datasets.py:543-546`) before a Job exists.

`07` FR-421 (`docs/specs/07-platform.md:115`): *"Large uploads use presigned multipart URLs so
dataset files do not transit the API process."* The route implements that sentence's first half
(the bytes bypass the API). Its second half, what makes the uploaded bytes a blob that
`POST …/versions` can name, is not built. `07` §5.1's `upload-url` row (`07-platform.md:327`),
amended 2026-09-28, says so itself: *"the completion step FR-421 implies has no endpoint. So an
upload made through this URL cannot yet be ingested or downloaded as a blob."* No FR numbers the
completion step, so this is a specification gap and a code gap.

**The finding has two limbs, and the second is the one the process rules name.**

- **Limb 1, the capability.** `docs/workflows/WF-00698-dataset-to-approved-model.md` step A5 is
  `POST /datasets/{slug}/versions` → `202` + `dataset.ingest` Job, the first step in the platform's
  first journey that touches data. Over the public API that step cannot be reached from a client's
  own file. Every consumer today gets around it by writing the `blobs` row some other way
  (`examples/fremtpl2/seed.py` puts the bytes through `BlobStore.put` in-process; every test seeds the
  row directly, §2 below).
- **Limb 2, the process.** `d068fb00` (#883, WK-1178, 2026-09-28T23:27:39+01:00) added
  `blob_readable_by` as a security fix, and its own body states the gap: *"The design in the
  earlier ruling assumed an upload-completion step that records an owner; that step does not exist
  in the code (`upload-url` returns a staging key, nothing promotes it or writes its `blobs` row)
  … It is a spec change of its own and is not built here."* The gap was recorded in a docstring,
  in a spec row, and in a PR body, and in none of those did it get an owner, a requirement id or a
  roadmap row. It sat 16 days (2026-09-28 to 2026-10-14). `CLAUDE.md` §14 says "unowned" is not a
  permitted state. This is a deferral without an owner, and the finding names it as part of the
  finding, as the maintainer's 10:56:38 entry (item 1) directs.

## Evidence

### 1. The live run, over the public API only

Run 2026-10-14T10:51:11 UTC, tree `8eaf6d5f`, scratch DB `gipricing_upload_a47869af` (`createdb -T
gipricing`, then `alembic upgrade head`), scratch bucket `gip-upload404-a47869af`, `uvicorn`
with `GIP_DEV_AUTH_ENABLED=true`, `curl`. Queued behind `/tmp/slots/gate-1`. Dropped and deleted
afterwards. **Disclosure: the workspace, the `analyst` role assignment and the membership were
seeded once by a script taken from the test `grant` fixture**, because no public route creates a
workspace or a member. That is identity set-up, not a step under test (the "RL 8028 identity
carve-out" class the maintainer named in the 11:55:21 entry). Every step below is a public HTTP
call. The presigned query string is redacted.

```
POST /api/v1/datasets {"slug":"upl404"}                         → 201 Created
POST /api/v1/blobs/upload-url {"media_type":"text/csv","parts":1} → 200
  {"key":"staging/2026/10/14/01a13a0a-0efb-7d67-9a4e-0318597c503b","upload_id":null,
   "urls":["http://localhost:9000/gip-upload404-a47869af/staging/2026/10/14/01a13a0a-0efb-7d67-9a4e-0318597c503b?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=REDACTED&X-Amz-Date=20261014T105140Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=REDACTED"],
   "expires_in_s":3600}
PUT <presigned url>  (a 3-line CSV; sha256 of the file d836897ebef001d4726d1820f41dee297db2f9b7e332a21131ec7a77679e9b4c)
  → HTTP/1.1 200 OK   Server: MinIO   ETag: "a9a4e2d23764dc07f17332b8b4421a5f"
POST /api/v1/datasets/upl404/versions {"blob":"d836897e…9b4c","filename":"p.csv"} → 404 Not Found
  {"type":"https://docs.gi-pricing.dev/errors/not-found","title":"Blob not found","status":404,
   "code":"NOT_FOUND","detail":"No blob with digest d836897ebef001d4726d1820f41dee297db2f9b7e332a21131ec7a77679e9b4c.",
   "instance":"/api/v1/datasets/upl404/versions","errors":[],"trace_id":"947d435cee5b64c7de829615bf57f056"}
GET  /api/v1/blobs/d836897e…9b4c → 404 Not Found, the same body (trace_id df69dae4f2750ff1ee34d86138ab1b9d)
```

- The response carries **no sha256**: a client cannot name the blob it just uploaded without
  hashing its own file, and doing that still reaches the 404.
- The scratch DB's `blobs` table was inherited from the template (33 rows); the digest of the
  uploaded file is not among them. No `blobs` row and no Job were created.
- **The refuser is inferred, not traced.** The server log has only the access line for
  `POST …/versions 404`. The body's title, code and detail are exactly those of `blob_not_found()`
  (`platform/blobs.py:502`), whose only call site on that route is `datasets.py:543-546`, placed
  before `job_service.submit`.
- Single-part upload only (`upload_id: null`); the multipart path (`parts > 1`) was not run. By the
  code (`platform/blobs.py:238-288`) it calls `create_multipart_upload` and nothing calls
  `complete_multipart_upload` (`git grep -n -E 'complete_multipart'` over `backend/src` at `ba68a6da`:
  0 lines), so the client cannot finish the S3 multipart upload through the API either.

The run record (the scripts and the unredacted output; redact the `X-Amz-*` query before quoting)
is `~/.claude/jobs/b6860f8f/tmp/upload404/` (`job.sh`, `bootstrap.py`, `out.txt`).

### 2. Nothing in the repository walks the public path, which is why this survived

Each measured at `ba68a6daf3cfb7634258915a6e542bc658ae3f62`, from the repository root, with
`git grep` and `-n`:

| Question | Predicate | Result |
|---|---|---|
| Does the frontend call a blob route? | `git grep -n -i -E 'upload-url\|upload_url\|presign' ba68a6da -- frontend/src ':!frontend/src/api/generated'` | **0 lines.** There is no dataset-upload view; `frontend/src/api/datasets.ts:45` only lists versions. |
| Does any backend test call `upload-url`? | `git grep -n -E 'upload-url\|upload_url' ba68a6da -- backend/tests` | **0 lines.** |
| Which tests post a version, and how do they get an owned blob? | `git grep -n -E 'dataset_blob\(' ba68a6da -- backend/tests` | **7 lines in 4 files** (`blob_fixtures.py`, `test_api_blobs.py`, `test_api_dataset_ingest_owner.py`, `test_api_datasets.py`). `dataset_blob` (`backend/tests/blob_fixtures.py`) inserts a `blobs` row and a `DatasetVersionRow` owning it, straight into the database. |
| The 202 test, for example | `backend/tests/test_api_datasets.py:200-201` calls `dataset_blob(database, workspace_id, sha256)` before the POST (`:205`); the idempotency test does the same at `:541-542`; `test_api_dataset_ingest_owner.py:39` seeds then posts. | The route's own "positive" tests pass because the blob and its owner are inserted below the API. |

So the route's success path is covered only by a precondition no client can produce, and the
route that produces the precondition is covered by no test. `d068fb00`'s census test
(`backend/tests/test_ingest_enqueuers.py`) pins that the route is the only enqueuer; it does not
exercise the way a file reaches the route.

### 3. The history and the governing sources

- `git log -S 'blob_readable_by' --format='%h %aI %s' ba68a6da -- backend/src` gives one commit:
  `d068fb00 2026-09-28T23:27:39+01:00 fix(security): dataset ingest reads only a blob the caller's
  workspace owns (WK-1178, #869) (#883)`. Its PR body is quoted in the finding above.
- `backend/src/app/api/blobs.py:75-98` (the `upload_url` docstring): *"Nothing yet moves a staging
  object to its content address or creates its `blobs` row (the completion step FR-421 implies is
  not built), so an upload made through this URL cannot be ingested or downloaded as a blob
  today."* `platform/blobs.py:238-258` (`presign_upload`) says the same about the staging key.
- `01-data-management.md:858` (the ingest row, amended 2026-09-28) states the ownership rule and not
  the way to satisfy it; `VersionCreate.blob`'s comment (`datasets.py:153-155`) says *"`POST
  /blobs/upload-url` first, then this"*, which is the instruction the code cannot follow.

### 4. What the check is not at fault for

`blob_readable_by` is an allow-list by ruling ([the maintainer's (by delegation)] DP-P1-2, 2026-09-28 21:51:10 BST): a
digest is readable only if a Dataset Version's table or a Job's blob result in the caller's
workspace references it, and never if a quote-input store does. It is doing what it was written to
do, and it closed a real cross-workspace read. **The defect is not the 404 or the check.** It is
that the step which would give an uploaded blob an owner was left unbuilt when the check made an
owner mandatory. Weakening the check to admit unowned blobs would reopen the cross-workspace read
of `d068fb00`'s finding and is not a remedy.

## Severity: the proposal and its reasoning

**HIGH.** Weighed against the comparators already ruled on this register:

- **Against FD-1715 (MEDIUM, latent).** That finding needs a caller the application lacks. This one
  is reached by the ordinary first call of the first journey, on every attempt, with a
  deterministic result. Nothing latent about it.
- **Against the silent-wrong-outcome class (FD-1660, FD-1679, HIGH).** This outcome is loud (a
  `404`), so no wrong number is produced. It is HIGH on capability rather than on silence: the
  platform's front door does not open for a client's own file, and the whole lifecycle
  (`WF-698` A5 onward) starts there. A loud failure that blocks the primary use is the weaker
  claim, and the proposal says so.
- **The process limb raises it.** A gap that three artifacts (a docstring, a spec row, a PR body)
  all recorded and none owned, for 16 days, is the failure `CLAUDE.md` §14 names. §14 also bars
  carrying an open HIGH across a phase boundary without a resolution, which is why the maintainer
  ordered it fixed in P2 rather than carried.

If the maintainer rates it below HIGH, the owner, the fix and the discharge are unchanged.

## Disposition

**Fix with an owner: WK-1178, in P2, before the 4 Nov code freeze** (the maintainer's, by delegation,
"2026-10-14 10:56:38 BST", items 2 to 4). Not carried to P3; off the G2 critical path and never
displaces a G2 gate. The fix is already planned and decided:

- `PL-8025` and its slice `SL-8026` cut it. `RL-8028` (the decision-maker) rules the design: a
  presigned PUT, then an asynchronous complete, a `blob.promote` Job on `io`, with its Job result
  owning the blob and a pending Blob Upload record authorising it. A new `07` FR for the completion
  step, the `07` §5.1 `upload-url` row's dated line and a new `complete` row, and `01`'s ingest row
  citing the FR ship in the slice's commit (spec first, `CLAUDE.md` §0).
- **The test that would have caught it** is the slice's one public-path HTTP test: `upload-url` →
  PUT (to MinIO) → complete → `POST …/versions` → ingest `succeeded` on a real `io` worker, with no
  database seeding. `SL-8026`'s acceptance line also converts `PL-1714` E4.3's compose ingest test
  to that path.
- **The process remedy is the slice's own spec step.** The completion step gets a requirement id,
  and the `upload-url` docstring and the `07` row stop being the only places the gap is written.

**The event that next discharges this finding** is the merge of `SL-8026` with its public-path
test green on `main` and the `PL-1714` E4.3 conversion done. If it has not merged by the 4 Nov
freeze, the P2 closure record lists this finding as open with that reason, per `SL-8026`'s
acceptance line.

**Not in this finding.** FD-1715 (blob garbage collection) is related, not the same: its widened
derived check already counts `promote_upload` as a `BlobRow` writer after `SL-8026`, so the two
land together.
