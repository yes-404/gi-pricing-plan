# W10 decision-point rulings — DP1 and DP3 (2026-08-28)

Decision-maker rulings on the W10-2 decision points, recorded per the W9 decision-point
precedent (2026-08-27). The plan itself is frozen at its date
(`2026-08-28-w10-rate-tables.md`) and is not amended; this record is the dated home of
the rulings.

## DP1 — exposure-weighted diff calculation

**Options:** (a) calculate exposure weights at diff-fetch time (query the portfolio once
per request); (b) cache weights on the rate-table version at creation time (snapshot,
stale if the portfolio changes).

**Ruled: (a) — calculate at diff-fetch time. Confirmed.**

Rationale:

- **FR-RATE-17 names the portfolio as the source.** "the exposure weight behind each
  cell **(from the portfolio dataset)**" — the requirement reads the weight from the
  portfolio, not from the version. Option (b) would substitute a creation-time snapshot
  for the named source.
- **A diff compares any prior version** (FR-RATE-17: "against any prior version"). Under
  (b) the two sides of a diff would carry weights from two different portfolio snapshots
  (each version created at a different time), so the weighted comparison would not be a
  comparison at all. Option (a) weights both sides against the same current portfolio.
- **Versions are immutable** (FR-RATE-62: storage mode fixed at write; the version is
  immutable with it). Weights are a presentational, portfolio-derived attribute, not a
  fact of the version; caching them on the version bakes a mutable view into an immutable
  artifact, with no refresh short of creating a new version.
- **Staleness is silent.** The plan's risk stands: a diff cached against an old book
  "looks safe when the book has actually moved", and the actuary's materiality judgement
  is the thing being gated.
- The cost objection to (a) — a portfolio query per diff request — is met by the DP3
  ruling: the read path is cached, so (a)'s fresh query runs once per portfolio snapshot.

## DP3 — diff endpoint latency for row-backed tables

**Options:** (a) materialise the diff eagerly at version creation (cost at write time);
(b) compute on read with a Redis cache keyed by version hash and portfolio snapshot date
(cost at first read, then cached).

**Ruled: (b) — compute on read with caching. Confirmed.**

Rationale:

- **FR-RATE-17 diffs against any prior version.** Eager materialisation at creation can
  only precompute the pairs that exist at that moment (vs previous, vs seed); a later
  "vs version 2" request has no eager artifact. Precomputing all pairs at every creation
  is O(n²) diff joins for pairs that may never be reviewed.
- **The diff is a review-time tool, not a quote-path read.** FR-RATE-17: "so an actuary
  sees which edits matter" — a human judgement, once per rate change. The plan's premise
  holds; write-time cost on every version creation (bulk ops and imports create versions
  too) would tax a path that runs on every rate change, to serve one that rarely runs.
- **FR-RATE-62 points the same way.** Above the storage threshold, the diff "becomes a
  Job returning the same artifact" — computed when asked, not materialised at write.
  Read-time computation is the storage-agnostic behaviour; (b) keeps rows and parquet
  on one contract, differing only in 200 vs 202.
- **The cache key is precise invalidation.** Version hash is immutable; the portfolio
  side changes only when the portfolio snapshot changes, so a cached diff is stale
  exactly when it should be, and re-reads between portfolio changes are stable.

**Implementation note (for T2):** the cache key's portfolio side must be the portfolio
**dataset version's identity** (a Dataset Version is immutable — 00-overview §2), not a
wall-clock date. A date key would silently serve stale diffs if the executor keys on
"today" rather than on the snapshot. With a dataset-version key, invalidation is exact:
the diff recomputes precisely when the portfolio actually changes.

## DP2 — parquet spill triggering

**Options:** (a) retroactively move an existing version to parquet if the threshold is
lowered (breaks immutability); (b) the threshold change applies to new versions only (old
versions keep their original storage mode).

**Ruled: (b) — the threshold change applies to new versions only. Confirmed.**

Rationale:

- **FR-RATE-62 already decides this.** The requirement's own text: "The threshold is a
  stored property of the version, not a runtime decision: `storage` is `rows | parquet`
  on `RateTableVersion` (§4.2), fixed when the version is written and immutable with it,
  so a reader never has to ask which form a past version took and **a change of threshold
  cannot silently re-home existing versions**." The ruling adopts the spec's stated design;
  option (a) contradicts the requirement it would implement.
- **A retroactive re-home breaks references.** Above the threshold the cells are addressed
  by a content-addressed `BlobRef`; moving a version to parquet changes the address of its
  cells, invalidating every pin, diff and comparison that points at the version as it was
  recorded. The version's immutable record (`storage: rows`) would also lie about where
  its data lives.
- **"New versions only" is not a loss.** The threshold's purpose is to bound storage for
  tables that grow; a version written under the old threshold was written under the rules
  it was reviewed against, and its reader (the FR-RATE-17 diff / FR-RATE-62 Job path)
  already handles both forms.

**Implementation note (for W10-3 T3):** `decide_storage_mode()` reads the workspace's
configured threshold at version-creation time only; the threshold is never consulted again
for a written version, and lowering it must not rescan existing versions.
