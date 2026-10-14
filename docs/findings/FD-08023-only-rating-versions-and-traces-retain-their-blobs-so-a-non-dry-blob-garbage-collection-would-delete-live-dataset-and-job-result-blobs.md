---
id: FD-8023
family: finding
title: Only rating versions and traces retain their blobs, so a non-dry blob garbage collection would delete live dataset and job-result blobs
status: active
created: 2026-10-14
owner: auditor
tree: ba68a6daf3cfb7634258915a6e542bc658ae3f62
corrected_by: []
relates: [WK-1251, FR-420, FR-418, FR-419, NFR-530, NFR-459, RL-888, FD-8007, FD-1660, FD-1679, P2]
---

# FD-8023 — blob GC selects `ref_count == 0`, and 14 of 17 blob writers never raise it

*(Filed under working id 8023, reserved by the lead in `handover/eta.md` ("2026-10-14 10:51:36
BST"); a minter folds it into the docs batch. Every `file:line` below was read at `origin/main`
`ba68a6daf3cfb7634258915a6e542bc658ae3f62` through `git -C /home/puzhenhao1989/gi-pricing-plan
grep|show`. The raising evidence is the planner's memo `handover/memo-fr420-blobgc-2026-10-14.md`
§1a. Its claims were re-read against the primary files, not copied.)*

## Finding

**Severity: MEDIUM, latent, owner WK-1251, with the HIGH re-rate trigger below: CONFIRMED** by the
maintainer (by delegation), "2026-10-14 10:57:10 BST" item 1 (the auditor proposed it). **Consequence:
the 14 un-retained owners include rate-table cells, model boosters and compiled bundles, i.e.
APPROVED pricing artifacts, so the HIGH trigger is not hypothetical in impact.** Authority for the filing: the maintainer's (by delegation) entry
"2026-10-14 10:51:08 BST — FR-420 → WK-1251 ACCEPTED; latent blob-GC DATA-LOSS finding: file in
D16 (not D17) + a precondition line" in `channel/to-lead.md`. Its items 2 to 4, in substance: the FD
is filed now, in D16; an auditor proposes the severity, owner WK-1251; MEDIUM while no production
path can run a non-dry GC, with a re-rate to HIGH if any route, CLI, job handler or script gains
a non-dry call; a precondition line goes on WK-1251's roadmap row; no code change in P2, and S4
must not register a `blob.gc` handler.

`07` FR-420 (`docs/specs/07-platform.md:114`): *"a blob is deletable only when no artifact
references it and it is older than a configurable grace period (default 30 days)."* The code
reads "no artifact references it" as `ref_count == 0`
(`backend/src/app/platform/blobs.py:403`, `select(BlobRow).where(BlobRow.ref_count == 0,
BlobRow.created_at < cutoff)`). But `BlobStore.put` creates every row at `ref_count=0`
(`blobs.py:186`), and **a reference is taken only by `blobs.retain`**. At `ba68a6da` only three
lines call it. So the blob of a Dataset Version's table, a Job's result, a model's booster, a
rate-table version's cells, a compiled bundle, a regression case log, a dislocation mover list
and a score output all sit at `ref_count == 0`. They match the collector's selector exactly once
they are 30 days old. A non-dry `collect_garbage` would delete the S3 object
(`blobs.py:418`, `delete_object`) and the `blobs` row, and every reference to it would resolve
to nothing. That is permanent data loss, in a platform whose retention floor is seven years
(`00` NFR-459).

**It is latent today.** Nothing calls `collect_garbage` outside tests, `dry_run` defaults to
`True`, and `BLOB_GC` has a queue but no handler and no submitter (§3). So the finding is a
precondition the FR-420 Work must satisfy before it wires anything, not a defect any request can
reach now.

## Evidence

### 1. Every blob writer, and whether it retains

Command (run at `ba68a6da`, from the repository root; rc 0):

```bash
git grep -n -E '\.put\(' ba68a6da -- backend/src packages | grep -v -E '@router|put_object|@app'
```

It printed 20 lines. Three are not blob writes: `blobs.py:153` (the `RuntimeError` text naming
`blobs.put()`), and `api/score.py:292` and `:309` (`slot.put`, a compiled-bundle cache). That
leaves **17 writers**. `BlobRow(` is constructed once in `backend/src`, at `blobs.py:186`
(`git grep -n -E 'BlobRow\(|insert\(BlobRow' ba68a6da -- backend/src packages`), so `put` is the
only way a row is made. The retain and release calls:

```bash
git grep -n -E 'retain\(|release\(' ba68a6da -- backend/src packages | grep -v 'def '
```

Output: `rating_versions.py:1243` (retain), `traces.py:127` (retain), `traces.py:255` (retain),
`traces.py:331` (release), and `traces.py:284`, a comment. **Three retains, one release.**
Each `put` below was read in its function body at `ba68a6da`; "same transaction" means the retain
is in the same function and session.

| # | `put` site (`backend/src/app/…`) | Function | Owner of the blob | Retained? | Evidence |
|---|---|---|---|---|---|
| 1 | `data/ingestion.py:308` | `_store_table` | Dataset Version `tables[].blob` (parquet) | **no** | returns the ref into the `tables` dict (`:310-318`); no retain in the function |
| 2 | `data/ingestion.py:453` | `correct_schema` | Dataset Version `tables[].blob`, replaced in place (`:456-462`) | **no**; and the replaced blob is not released | `version.tables = tables` (`:462`); neither retain nor release |
| 3 | `worker/data_handlers.py:428` | `_materialise_split` | derived Dataset Version `tables[].blob` | **no** | entry built at `:429-434` |
| 4 | `platform/rate_tables.py:839` | `build_cells_artifact` | chunk blobs of a diff-cells artifact, named only inside the manifest JSON | **no** | digests go into `chunks` (`:839`, `:843`) |
| 5 | `platform/rate_tables.py:846` | `build_cells_artifact` | the manifest, a Job `JobResult(kind="blob")` | **no** | returns `ref.sha256` (`:847`) |
| 6 | `platform/rate_tables.py:1475` | `_persist_new_version` | rate-table version `cells` (parquet) | **no** | `version_row.cells = blob_ref…` (`:1480`) |
| 7 | `platform/rating_versions.py:1240` | `_structural_diff_gate` | rating version structural diff | **yes** | `blobs.retain` at `:1243`, same function |
| 8 | `platform/traces.py:122` | `write_trace` | scoring trace | **yes** | `blobs.retain` at `:127` |
| 9 | `platform/traces.py:254` | `complete_pending_trace` | scoring trace (completed) | **yes** | `blobs.retain` at `:255` |
| 10 | `worker/dislocation_handlers.py:329` | `_dislocation_run` (`persist`) | `DislocationRun.largest_movers_blob` (a prefixed digest string) | **no** | digest written to the run at `:335`; no retain |
| 11 | `worker/model_handlers.py:543` | `_fit` (`store`) | fitted Model booster | **no** | `put` at `:543`, then `record_fit` (`:552`) |
| 12 | `worker/model_handlers.py:549` | `_fit` (`store`) | GLM covariance blob | **no** | as #11 |
| 13 | `worker/rate_table_handlers.py:58` | `_rate_table_diff` | Job `JobResult(kind="blob")` | **no** | returns the digest as the result (`:59`, `:63`) |
| 14 | `worker/rating_handlers.py:68` | `_rating_compile` | compiled bundle, on the version's metadata (RL-915) | **no** | key stored on the row; no retain |
| 15 | `worker/rating_handlers.py:193` | `_rating_regression` (`persist`) | `RegressionRunRow.cases_blob_sha256` (a quote-input store) | **no** | `persist_run` (`:199`); no retain |
| 16 | `worker/scoring_handlers.py:280` | `_score_one_ref` | `score.batch` output parquet | **no** | returned as `output_ref` |
| 17 | `worker/scoring_handlers.py:376` | `_score_batch_handler` | Job `JobResult(kind="blob")` (summary) | **no** | returned as the result (`:377`, `:381`) |

**3 of 17 writers retain; 14 do not.** Of the 14, rows 1 to 3 and 5, 13 and 17 are the owners
`blob_readable_by` (`blobs.py:508-534`) names as the readable ones (a Dataset Version's `tables`,
a Job's `JobResult(kind="blob")`): the owner list the route trusts is not the reference count the
collector trusts. Row 4's chunk blobs have no owner row at all, only a manifest that lists them.

The one proof that retention works is `backend/tests/test_traces.py`'s GC-survival test
(`collect_garbage` at `:340`), which covers rows 8 and 9 only. Row 2 is a second gap inside the
first: when a schema correction replaces a table's blob, the old blob is no longer referenced by
anything, yet no release exists to say so. So even after every owner retains, a collector keyed on
`ref_count` needs the replace and delete paths to release, or the old blob is never reclaimed (a
leak, not a loss).

### 2. Who calls `collect_garbage`, and the `dry_run` default

```bash
git grep -n collect_garbage ba68a6da -- backend packages
```

Output: `backend/src/app/platform/blobs.py:379` (the definition) and, in tests only,
`backend/tests/test_blobs.py:176`, `:199`, `:217`, `:235` and `backend/tests/test_traces.py:340`.
**No production caller.** The signature is `dry_run: bool = True` (`blobs.py:385`), and the docstring
gives the reason (*"A destructive sweep whose default is to destroy is a sweep someone runs by
accident."*). The default protects a caller who omits the argument. It does not protect a handler
that forwards a job parameter into `dry_run`, which is the obvious way to write one.

### 3. Can any route or job kind trigger a non-dry GC?

```bash
git grep -n -E 'BLOB_GC|blob\.gc|blob_gc' ba68a6da -- backend/src packages
```

Output: `packages/model-schema/src/model_schema/jobs.py:74` (`BLOB_GC = "blob.gc"`),
`backend/src/app/platform/jobs.py:86` (`JobKind.BLOB_GC: JobQueue.IO`), and
`backend/src/app/config.py:140` and `platform/settings.py:259` (the grace-period setting only).
**No handler registration, no submitter, no route.** `collect_garbage` is not reachable from any
request, job or script in `backend/src` or `packages`. That is the whole basis for "latent".

### 4. What bounds it, and what does not

- **Bounds it today:** no caller (§2), no handler (§3), the keyword default, the 30-day grace
  (`config.py:140`, `ge=1, le=3650`), and the audit row `collect_garbage` writes either way
  (`blobs.py:427`).
- **Does not bound it:** the grace period only delays the loss; a 30-day-old dataset blob is
  exactly what the selector wants. The `QUOTE_INPUT_BLOB_COLUMNS` allow-list (`blobs.py:496`) is a
  read-access list and is not consulted by the collector.

## Severity: the proposal and its reasoning

**MEDIUM, latent, with a HIGH re-rate trigger.** Weighed against the two comparators the lead named:

- **Against FD-1660 and FD-1679 (HIGH).** Those are silently wrong approval evidence **reachable
  by an ordinary call on `main`**. This finding is reachable by no call. Nothing runs
  `collect_garbage` outside tests. The silent-change class is HIGH when a user can produce the
  wrong outcome; here a user cannot, so the rating cannot be the same.
- **Against FD-8007 (MEDIUM, confirmed by the maintainer (by delegation) at "2026-10-14 10:11:47
  BST").** FD-8007's consequence is a silent changed price, and it needs a write path the
  application lacks. This finding needs a caller the application lacks. The same shape, so the
  same rating. This one is worse in kind (an S3 object is deleted, and an erased dataset blob cannot
  be recomputed from the pin), and better in scope (one function and one selector, not a
  per-row edit anywhere). The two effects do not cancel into HIGH.
- **Against the data-loss class.** The loss is permanent unless the bucket is versioned (`07`
  FR-423, not built as a restore path). That is the argument for a precondition and a derived
  check, and for the re-rate trigger, not for HIGH while the path does not exist.

**Re-rate to HIGH on any one of:**

1. a production call to `collect_garbage` with `dry_run=False`, or with `dry_run` taken from
   untrusted or job parameters;
2. a `blob.gc` handler registration in `HANDLERS` (the kind is routed to `io` and has no handler,
   so S4 must not add one, and the E4.7 guard is what enforces it);
3. a route, CLI or script that reaches `collect_garbage` at all, since the first non-dry
   invocation is one argument away;
4. a change to the selector that drops `created_at < cutoff` or the `ref_count == 0` clause.

## Disposition

**Carry forward with an owner: WK-1251** (P3, "Production packaging and supply chain"; FR-420 is
placed there by the maintainer's (by delegation) entry "2026-10-14 10:51:08 BST", item 1). **No code
change in P2.** The remedy shape, exactly as ruled in that entry's item 3 and 4:

1. **Retain at every owner, and release on replace (`data/ingestion.py:453`).** `correct_schema` replaces a Dataset Version's blob in place (`:456-462`) and never releases the old one; the remedy covers it (confirmed in the 10:57:10 entry).
   **Retain at every owner.** Every blob-owning artifact takes a reference to its blob in the
   transaction that stores it, and releases it when the owner replaces or deletes the blob (row 2).
2. **A derived check, not a list.** Every `BlobRow` writer in `backend/src` is paired with
   a `retain` by its owning record, **or is listed with a reason**. *(Widened 2026-10-14 by the
   maintainer (by delegation), entry "2026-10-14 11:24:38 BST" in `to-lead.md`, which says the check
   counts "EVERY writer of a `BlobRow` (at this tree `BlobStore.put`; after SL 8026 also
   `promote_upload`)", not `put` call sites only.)* At `origin/main` the writer set, from
   `git grep -nE 'BlobRow\(' origin/main -- backend/src packages`, is one constructor, `BlobRow(`
   at `backend/src/app/platform/blobs.py:186`, inside `BlobStore.put` (`:140`); no other
   insert into the `blobs` table exists, and `blobs.py:455` (`update(BlobRow)`) only adjusts
   `ref_count` for `retain` and `release`. So the writers are: **`BlobStore.put`**, whose 17 call
   sites above are the starting population, and, **after SL 8026**, **`promote_upload`** (RL 8028's
   `blob.promote`), which creates the `BlobRow` for a promoted upload without calling `put`. A new
   writer of either kind with neither a `retain` nor a reason fails the check.
3. **A seeded dry run.** A `collect_garbage(dry_run=True)` report over a seeded database, with one
   live blob per owner kind past the grace period, selects **0 live blobs**.
4. **No non-dry GC is wired until both pass.** The precondition line goes on WK-1251's roadmap row
   in D16 (the maintainer's (by delegation) item 3, verbatim in the register row below).
5. **S4 registers no `blob.gc` handler.** `BLOB_GC` stays allow-listed as `("P3", "WK-1251", "07
   FR-420")` in the E4.7 guard, which keeps the kind handler-less.

The event that next confirms or discharges the finding is the merge of the WK-1251 slice that adds
the derived check and the seeded dry-run red, with both green on `main`.
