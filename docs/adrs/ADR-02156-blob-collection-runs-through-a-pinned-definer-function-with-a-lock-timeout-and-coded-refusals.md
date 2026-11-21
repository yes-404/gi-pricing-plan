---
id: ADR-2156
family: decision
title: Blob collection runs through a pinned definer function with a lock timeout, and its refusals and a deadlock are coded
status: active              # draft → active → superseded | retired (§1.2a)
created: 2026-11-16
owner: executor
tree: ad4fc5cab9a133e8504c35326ededac15364d1a7
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-419, FR-420, ADR-2150]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2156 — Blob collection runs through a pinned definer function with a lock timeout, and its refusals and a deadlock are coded

- **Status:** Accepted (front matter `active`), accepted by the maintainer as written on 2026-11-16 ([comment on #1504](https://github.com/yes-404/gi-pricing-plan/issues/1504#issuecomment-6909140793)). Supersedes nothing.
- **Deciders:** the maintainer, on the decision issues named below.
- **Decision issues:** #1550 (c) (the definer function), #1855 (v) (the collector's contract), #1888 option (d) (the deadlock), #1895 option (a) (the dry-run action).
- **Enacted by:** the pull request that adds this record (#1504 slice 3b-1). Part of #1504.

## Context

Slice 3a made the collector delete a blob in two statements under a per-digest advisory lock. The login role has no `DELETE` on `blobs`, so the delete needs a privilege the login role does not hold, and a collector that runs as that role needs a way to use it that the role cannot widen. Four questions were open: how the collector gets the privilege, what it does when a lock is held by its caller or when an owner row appears during its run, what a caller sees when PostgreSQL aborts a transaction as a deadlock victim, and how a dry run appears in the audit trail.

## Decision

1. **A `SECURITY DEFINER` function, `blob_gc_delete_unreferenced`, owned by the table owner, is the only way the login role deletes a `blobs` row.** It sets `search_path = pg_catalog, public, pg_temp`, refuses a cutoff less than one day old (`BLOB_GC_CUTOFF_TOO_RECENT`), and has three statements: a row lock on the candidates; the delete of those with no owner row (one `NOT EXISTS` per owner place); and a re-check that no owner row for a deleted digest appeared, which rolls the run back (`BLOB_GC_OWNER_APPEARED`). `EXECUTE` is revoked from `PUBLIC` and granted to the login role. The function body's md5 is pinned in `db/immutability.py`, and the start-up check refuses a function whose text differs, so the definer function cannot be changed without a migration and a pin that name it.
2. **The collector's contract is stated and held by a lock timeout.** The caller holds no open transaction. The collector sets `lock_timeout` to a module constant (10 s, `GC_LOCK_TIMEOUT_S`, not a setting) before its statements; a held lock ends the run with `BLOB_GC_LOCK_TIMEOUT` (503) and not with a hang. The honest remainder is written in `FR-420`: the re-check covers an owner row committed while the delete runs, not a writer that takes no reference.
3. **A deadlock is a named conflict, and nothing is retried.** SQLSTATE `40P01` answers a route with `409 CONCURRENT_WRITE_RETRY` and fails a Job with that code and `retryable` true. The platform never re-runs a handler, so no side effect repeats; the caller sends the request or submits the Job again.
4. **A dry run is audited as `blob.garbage_collection_previewed`.** `blob.garbage_collected` stays for a non-dry run, so a count of it counts deletions.
5. **A census holds the writers of every owner place.** `OWNER_WRITERS` in `platform/blobs.py` names each writer and how it takes its reference, and a test fails on a writer that is not listed or that takes none. One place is stated and not changed: a Job result's blob has no reference of its own while the Job row names it (carried to slice 3c).

## Consequences

- A change to the definer function needs a new migration and a new pin; a deployment whose function differs from the pin does not start.
- The collector cannot be run inside a caller's open transaction; the next slice's handler runs it outside one.
- A route or Job that loses a deadlock now says so with a code a client can branch on. The 500 and `JOB_HANDLER_FAILED` for it are gone.
- The audit trail has a second blob action; a reader of the old name sees only deletions.
