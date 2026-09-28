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
other blob.

**There are two exposures.**

1. **Trace bodies, which hold quote inputs,** reach any `dataset:read` holder who has the
   trace's digest.
2. **Dataset blobs leak across workspaces.** executor-s1 established this while building the
   fix, and the lead relayed it. A `dataset:read` holder in workspace A who presents workspace
   B's dataset digest gets a 307 redirect to B's parquet. That is cross-tenant data, and unlike
   the trace case, the digest is handed out by the API itself (see below).

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

## Reachability of a dataset blob digest: exposed by design

Read at `e6a9ca71`:

- **Dataset-version responses.** A Dataset Version carries `tables: tuple[DatasetTable, ...]`
  (`model_schema/datasets.py:363`), and each `DatasetTable` has
  `blob: BlobRef | None` (`:256`). `BlobRef.sha256` is the bare-hex content address
  (`model_schema/refs.py:141`). Any reader of a Dataset Version sees its tables' digests, and
  with this route, anyone holding `dataset:read` anywhere can use them.
- **Job results.** `api/rate_tables.py:330` documents a diff Job's `result.ref` as *"its sha256,
  fetchable from `/blobs/{sha256}`"*. Model and peril artifacts carry `BlobRef`s too
  (`model_schema/modelling.py:772`, `:1605`, `:1668`; `perils.py:169`).
- **Trace views.** They return `bundle_hash`. That is the Rating Version's `content_hash`, with a
  `sha256:` prefix, which `model_schema/rating.py:82–87` distinguishes explicitly from the
  bundle's blob digest. So it is not a blob address. The lead's relay listed trace views among
  the exposures; at `e6a9ca71` the auditor finds no blob digest in them. That leaves the trace
  case at the reachability stated above, and the dataset case exposed by design.

**Past reads cannot be ruled out.** There is no download audit on this route, so this record
does not claim "no evidence of access".

## Disposition

**Fix in progress — owner the lead.** Event: executor-s1's WK-1178 PR (the number follows),
under the deputy's ruling (a). It is governance/security class, priority 2 in budget mode, and
it is not a Slice of WK-672. It covers:

- the route refusing any blob referenced by a quote-input store, with 404 rather than 403;
- **workspace scoping for every other blob**, since the cross-workspace answer is yes: the
  digest resolves to an owning artifact in the caller's workspace (any owner suffices, because
  content addressing can give one blob two owners);
- negative tests through the route, red first against `e6a9ca71`;
- the `07` §5.1 route row amended in the same commit;
- a mutation proof.

WK-672 Slice 3's case-store code does not merge before this fix.
