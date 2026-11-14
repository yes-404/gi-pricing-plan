---
id: FD-2135
family: finding
title: "A Rating Version's compiled bundle blob is stored with `ref_count` 0 and never retained, so FR-420's collector can take it once its grace period passes and an approved version would be left with a hash and no blob"
status: active
created: 2026-11-13
owner: executor
tree: 4ac2a06ceb23
corrected_by: []
relates: [WK-2113, SL-2132, LG-2133, FD-1495, OQ-1943, FR-420]
---

# FD-2135 — A Rating Version's compiled bundle blob is stored with `ref_count` 0 and never retained, so FR-420's collector can take it once its grace period passes and an approved version would be left with a hash and no blob

*Working id 8447, allocated by lead 34; minted as FD-2135 (WK-2113 S3). Raised by the maintainer's message after the SL-2132 pre-check, relayed in `to-lead.md` (quoted in `docs/ledgers/LG-02133-*`, the entry "2026-11-13 21:32:34 GMT"). This document files, as a finding file, the register row that carried the finding as a row only. Every statement below is the register row's or the slice ledger's; nothing is added to them.*

## Finding

Per the register row (`docs/findings/register.md`, the row ending "(FD-2135)"), severity and source: **MEDIUM**, set by the maintainer's message after the SL 2132 pre-check (relayed in `to-lead.md`). `backend/src/app/worker/rating_handlers.py` stored the bundle with `blob_store.put` (`ref_count` 0, `backend/src/app/platform/blobs.py` `put`) and took no `retain`, where the structural-diff blob does (`rating_versions.py`, `blobs.retain`). Not live today: `collect_garbage` has no caller in `backend/src` and the application role holds no `DELETE` on `blobs` (OQ-1943). SL 2132 retains the blob in the compile Job's unit of work (red first: `ref_count` 0, then at least 1, `test_fr240_governance.py`). Versions compiled before it still hold `ref_count` 0.

## Evidence

Locators are those the register row names, and `docs/ledgers/LG-02133-*` (amendment 4, the red-first test `test_a_compiled_bundle_blob_is_retained_so_the_collector_can_never_take_it`) and `docs/open-questions.md` OQ-1943 (the named limb). Not run here: this file adds no measurement beyond the row's and the ledger's.

## Disposition

Register decision, per the row (WK-2113, phase 3): **Closed for new compiles by SL 2132; carried with an owner (WK-2113) for the backfill**, a named limb of OQ-1943: no GC before every existing bundle blob is retained.
