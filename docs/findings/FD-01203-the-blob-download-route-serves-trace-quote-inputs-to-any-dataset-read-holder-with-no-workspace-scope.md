---
id: FD-1203
family: finding
title: The blob download route serves trace quote inputs to any dataset-read holder, with no workspace scope
status: active
created: 2026-09-28
owner: auditor
tree: e6a9ca71a0bef3da41720d20f3f20db73f6a1d80
corrected_by: []
relates: [WK-1178]
---

# FD-1203 — The blob download route serves trace quote inputs to any dataset-read holder, with no workspace scope

**Severity: high.** The auditor filed this finding on 2026-09-28, on the lead's instruction and
the deputy's ruling in his entry in the lead's local channel file `to-lead.md`, stamped
2026-09-28 18:24:32 BST (line 8865), item 1.

## Finding

`GET /api/v1/blobs/{sha256}` is gated on the `dataset:read` permission alone, and it looks the
blob up by digest with no workspace predicate. The blob table has no workspace column. Sampled
scoring traces, which are NFR-499's quote-input store, are written into that same table. So a
caller holding `dataset:read`, in **any** workspace, who knows a trace blob's digest, can
download a trace body. That body carries quote inputs, which the traces API itself serves only
to `rating:read` holders in the trace's own workspace. The same missing scope applies to every
other blob (dataset parquet, model and rate-table artifacts). Whether a `dataset:read` holder in
workspace A can fetch workspace B's dataset blob today is being established by the fix PR.

## Evidence

At `origin/main` `e6a9ca71`, each line re-read by the auditor:

- **The route.** `backend/src/app/api/blobs.py:104` `download` takes `caller: ReadDatasets`,
  defined at `:39` as `Annotated[Caller, Depends(requires(Perm.DATASET_READ))]`. It runs
  `select(BlobRow).where(BlobRow.sha256 == sha256)` with no other predicate.
- **The table.** `backend/src/app/db/models.py:274` `class BlobRow`. Its primary key is the digest
  (`:288`, `sha256: Mapped[str] = mapped_column(String(64), primary_key=True)`). Its columns are
  `sha256`, `bytes`, `media_type`, `part_count`, `ref_count` and `created_at`; there is **no
  workspace column**.
- **Trace bodies are written there.** `backend/src/app/platform/traces.py:122` and `:247` both
  call `blob_store.put(session, payload, "application/json")`. The digest is stored on the trace
  row as `blob_sha256` (`:136`, `:263`).
- **The traces API is scoped and permissioned differently.** `backend/src/app/api/traces.py:83`
  gates reads on `Permission.RATING_READ`, and its queries are filtered by workspace.

## Reachability of a trace digest

Exploitation needs the digest. **This record does not assert that it is unreachable.** What was
searched at `e6a9ca71`:

- `grep -nE "blob_sha256|\.sha256|\"sha256\"" backend/src/app` outside the blob route and
  models finds no API response that carries a trace's `blob_sha256`. `TraceView`
  (`api/traces.py:100`) returns `id`, `quote_id`, `rating_version_ref`, `bundle_hash`,
  `sample_reason`, `environment`, `created_at` and the reconstructed `trace` body, but not the
  digest. A grep of `docs/contracts/openapi/gi-pricing.yaml` for `blob_sha256` finds nothing.
- The digest is therefore reachable through three channels: the `scoring_traces` table and
  anything that reads it (operators, logs, backups); a caller who can reproduce the exact stored
  bytes; and any future response that exposes it. A search is not a proof, and the deputy's
  ruling requires the reachability to be evidenced rather than asserted, so the severity stays
  high.
- **Digests of other blobs are exposed by design.** For example, `api/rate_tables.py:330` says a
  diff artifact's `result.ref` *"is its sha256, fetchable from `/blobs/{sha256}`"*. That is why
  the cross-workspace question for non-trace blobs is live.

**Past reads cannot be ruled out.** There is no download audit on this route, so this record
does not claim "no evidence of access".

## Disposition

**Fix in progress — owner the lead.** Event: executor-s1's WK-1178 PR (the number follows),
under the deputy's ruling (a). It is governance/security class, priority 2 in budget mode, and
it is not a Slice of WK-672. It covers:

- the route refusing any blob referenced by a quote-input store, with 404 rather than 403;
- a written answer on cross-workspace dataset-blob reads, with workspace scoping if that
  answer is yes;
- negative tests through the route, red first against `e6a9ca71`;
- the `07` §5.1 route row amended in the same commit;
- a mutation proof.

WK-672 Slice 3's case-store code does not merge before this fix.
