---
id: RL-9485
family: ruling
title: The rate-table cells-diff page carries 300 ms p95 after the first request, at stated sizes, and a page cost bounded by its limit; options (a), (c) and (d) not taken
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: a5657fa4520739f182cbea79e0057afeed991ac1
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [WK-673, WK-1178, FR-231, FR-232, NFR-457, NFR-526]
---

# Ruling — the rate-table cells-diff page's latency budget

**Filed under working id 9485, allocated by the lead, the only allocator.** It rules on
OQ 9486 (working id; the `docs/open-questions.md` row and its `03` §10 mirror, raised on
draft PR #1222) and is applied by the fix slice of FD 9487 (working id; draft PR #1223,
head `8fc404a7`), in WK-1178. Unminted records are cited in working-id form and kept out of
`relates:` (check 32).

## How this was ruled

- **The decision is not this record's.** It is the maintainer's, by delegation, in the entry
  headed *"2026-10-05 20:58:27 BST — FD 9487 and OQ 9486 drafts: the severity path accepted;
  OQ 9486 DECIDED as (b)+(e)"* in `~/gi-pricing-plan.local/channel/to-lead.md` (read in full
  by this session before 21:01:44 BST, not taken from the lead's relay). This record states it as
  spec text a slice can apply, and nothing beyond it is decided here.
- **Written 2026-10-05, after 21:01:44 BST,** by the decision-maker, on the lead's brief
  `~/gi-pricing-plan.local/handover/brief-dm-rl9485-2026-10-05.md`. Every fact below was read
  at `origin/main` `a5657fa4520739f182cbea79e0057afeed991ac1`, unless it names another tree.

The decision, verbatim:

> OQ 9486 (#1222 @90390263): DECIDED, (b) plus (e).
> (b) ONE route NFR in 03 9 for the diff-cells page: p95 at or under 300 ms for every page AFTER the first request for a (versions, portfolio) key, which may answer 202 with a Job under R1. It is MEASURED, not asserted, at n ≥ 100 pages, on a quiet box, at a stated size: 250k cells for rows and 1M for parquet.
> (e) A page's cost is bounded by its limit, not by the table size. It is stated as a testable property: page time at 250k within 2x of page time at 10k, at the same limit.
> (a), (c) and (d) are recorded as not taken, with their trade-offs. This is a NEW requirement, so spec first: ONE RL carrying the 03 9 NFR text and the (e) property, applied by FD 9487's fix slice (WK-1178). The OQ row and its 03 10 mirror are decided in the same commit (both ways).

## Verified first, at `a5657fa4`

| Fact | Where |
|---|---|
| R1: *"**R1 — Everything slow is a Job.** Any operation that can exceed 2 s returns `202` with a Job, has progress, is cancellable, and persists its result (FR-13, NFR-457)."* | `docs/specs/07-platform.md:36-37` |
| NFR-457: *"Interactive UI: p95 < 300 ms for metadata reads; any operation exceeding 2 s becomes a Job with progress."* | `docs/specs/00-overview.md:534` |
| NFR-526: *"API metadata reads p95 < 300 ms (NFR-457); the scoring path is specified separately in `03` (NFR-489)."* | `docs/specs/07-platform.md:482` |
| FR-232: rows *"up to a workspace-configurable cell count (default 250 000)"*, parquet above it; rows are what lets *"the editor pages without a job"*; above the threshold *"Everything a caller may *ask* is identical; only the latency and the status code differ."* | `docs/specs/03-rating-engine.md:123` |
| `03` §9's table ends with the `NFR-502` row; no row names the diff or the cells route | `03:1326-1343` |
| The cells route is **not on `main`**. It is specified by WK-673 Slice 7 (#1206, open, head `386f4d54`): `GET /api/v1/rate-tables/{slug}@{version}/diff/cells?against=&portfolio=&limit=&cursor=`, `limit` defaulting to `DEFAULT_LIMIT`, **202** with a `rate_table.diff_cells` Job only where either version is `storage: parquet` and the query's cell artifact is not yet stored, its blob *"keyed like the diff's cache by both versions' content hashes and the portfolio's identity"* | `03:933` at `386f4d54` |
| `DEFAULT_LIMIT` is a shipped constant of the API's pagination module | `backend/src/app/api/pagination.py:37` |

## Ruled

| Option | Ruling |
|---|---|
| **(b)** | **Taken.** One route NFR in `03` §9, the same budget on both storage paths: p95 ≤ 300 ms for every page after the first request for a key, at stated sizes, measured. Text T1 below |
| **(e)** | **Taken**, as a testable property inside the same requirement: a page's time at 250 000 cells is within 2× of its time at 10 000 cells, at the same `limit`. Text T2 below |
| **(a)** A page is a metadata read; NFR-457 and NFR-526 apply as written | **Not taken.** Its trade-off on file: no table size is stated, so the budget is not testable as written, and "metadata" is stretched to cover cell values. (b) keeps the same 300 ms figure and adds the sizes. The maintainer gave no reason beyond the trade-offs on file. **Why not taken:** the OQ 9486 row (`docs/open-questions.md:142`) says of (a): *"But no table size is stated, so the budget is not testable as written, and "metadata" is stretched to cover cell values."* (b) states the sizes, so the same 300 ms figure is testable without stretching "metadata". |
| **(c)** Per-path budgets, looser on parquet | **Not taken.** Its trade-off on file: two figures to keep, and the parquet tables, the largest, would be the slowest to page with no stated reason beyond cost. The maintainer gave no reason beyond the trade-offs on file. **Why not taken:** the OQ 9486 row (`docs/open-questions.md:142`) says of (c): *"two figures to keep, and the parquet tables, the largest, are then the slowest to page with no stated reason beyond cost."* (b) is one figure for both paths, so no path is slower without a stated reason. |
| **(d)** No budget below R1 | **Not taken.** Its trade-off on file: a 1.9 s page would pass, paging below 2 s would be unbounded, and the measured parquet p99 of 1098 ms would be no defect. The maintainer gave no reason beyond the trade-offs on file. **Why not taken:** the OQ 9486 row (`docs/open-questions.md:142`) says of (d): *"a 1.9 s page passes, the paging experience below 2 s is unbounded, and the parquet p99 of 1098 ms is then no defect."* (b) bounds the paging below 2 s, which (d) leaves unbounded. |

R1 and NFR-457 still bound the route; this requirement is the budget below them. Which
mechanism meets it (an artifact read, a cache of the diff and the cut per key, or another) is
the FD 9487 fix plan's to choose, and is not ruled here.

**Two readings this record makes, stated so that the lead can reverse either at the ACK:**

1. *"page time"* in (e) is read as the page **p95**, measured as (b) measures it (n ≥ 100,
   quiet box, after the first request), so that one noisy page cannot decide it.
2. (e) is read as holding **on each storage path**, because (b) is one budget for both. On
   the parquet path a 10 000-cell table is below FR-232's default threshold, so the measurement
   sets the workspace threshold so that both versions take the path measured, as the S7
   measurement of 20:45 BST raised it to keep 260 000 cells on rows.

**Readings confirmed.** Both readings are confirmed by the maintainer (by delegation), in the
entry headed *"2026-10-05 21:04:46 BST — RL 9485 (#1222 @3ec4dbef): both readings CONFIRMED;
the 202 note accepted as written"*: *"Reading (1): "page time" in (e) is the page p95,
measured as in (b). CONFIRMED."* and *"Reading (2): (e) holds on EACH storage path, with
parquet at 10k measured with the threshold lowered so that the table takes that path.
CONFIRMED."*

## The exact texts

**T1 and T2 do not land in this PR.** The requirement is measured, not asserted (`CLAUDE.md`
§13), so it lands in one commit with the code that meets it and the measurement that shows
it (`CLAUDE.md` §2), applied by FD 9487's fix slice in WK-1178, byte for byte. `<date>` is
that commit's date.

**The requirement id.** `NFR-<next>` is a placeholder. The fix slice replaces it, in T1 and
everywhere it cites the requirement, with the id `python3 scripts/doc-id.py next` gives at
that slice's mint (requirement ids are on the single global sequence, `CLAUDE.md` §5). This
record does not allocate it: an id allocated now would be held by an unmerged draft that
`next` cannot see. The mint also replaces `RL 9485 (working id)`, `OQ-9486` and
`FD 9487 (working id)` with their minted ids.

### T1 — `03` §9: append as the table's last row

**Position:** the last row of the table under `## 9. Non-functional requirements` in
`docs/specs/03-rating-engine.md`, after the row that is last when the slice applies it (at
`a5657fa4`, the `NFR-502` row, `:1343`) and before the blank line that ends the table. Anchored
by position, not by a find string, so that another ruling appending to the same table does
not collide with this one.

```markdown
| **NFR-<next>** | Rate-table cells-diff paging (`GET /api/v1/rate-tables/{slug}@{version}/diff/cells`, FR-231, FR-232), below `07` §1.3 R1 and NFR-457. **Budget:** every page after the first request for a key (the two versions and the `portfolio`) answers with **p95 ≤ 300 ms** at `limit` = `DEFAULT_LIMIT`, on both storage paths; the first request for a key may answer **202** with a Job under R1. **Measured, not asserted:** n ≥ 100 pages, on a quiet box, at **250 000 cells** with both versions `storage: rows` and at **1 000 000 cells** with both versions `storage: parquet`; each figure states its size, `limit`, percentile and n. **A page's cost is bounded by its `limit`, not by the table's cell count:** on each storage path, the page p95 at 250 000 cells is within **2×** of the page p95 at 10 000 cells at the same `limit`, both measured as above, with the workspace threshold (FR-232) set so that both versions take the path measured. *(Added <date>, RL 9485 (working id), deciding OQ-9486; FD 9487 (working id).)* |
```

### T2 — the (e) property

T2 is **T1's sentence beginning `**A page's cost is bounded by its `limit`**`**, not a
separate insertion. It sits in the same row so that the property is traced to the same
requirement id as the budget, and a slice cannot apply one without the other. Quoted
alone:

```markdown
**A page's cost is bounded by its `limit`, not by the table's cell count:** on each storage path, the page p95 at 250 000 cells is within **2×** of the page p95 at 10 000 cells at the same `limit`, both measured as above, with the workspace threshold (FR-232) set so that both versions take the path measured.
```

## Acceptance — the violation that must become detectable

This record builds nothing. FD 9487's fix slice carries these:

- *Violation: a page after the first is over budget.* The measurement of T1 at both sizes,
  run on a quiet box (the gate slots free, no other heavy process), with its raw figures in the
  slice's ledger. At #1206's head `386f4d54` the rows page measured p50 9604 ms and the
  parquet page p50 948 ms at 260 000 cells, n=10, `limit` 50 (OQ 9486's row), so the figure
  before the fix fails T1, which shows the measurement can print a failure.
- *Violation: a page's cost grows with the table.* The (e) ratio, p95 at 250 000 over p95
  at 10 000, on each path. Before the fix it is expected to exceed 2× on both paths, since each
  page loads the whole table and, on rows, diffs it again; the slice records that figure
  before its fix and the passing one after.
- Whether (e) is also a test in the suite, rather than a ledger measurement only, is the fix
  plan's to choose. A timing assertion on the shared box can be flaky, so if it is a test, the
  plan says how it avoids reading load as a regression (`.claude/skills/dev-commands`).

## What it obliges

- **FD 9487's planner:** the fix plan cites this record for the budget and carries T1 and
  the acceptance list above as its scope, rather than re-deciding them. If its design answers
  the first rows-path request with 202, that changes the cells route's §5.1 row and FR-232's
  *"the editor pages without a job"*, and the plan names that as a spec change needing its
  own ruling. This record does not pre-decide it.
- **FD 9487's fix slice (WK-1178):** apply T1 verbatim, with the id its mint gives, in the
  commit that meets it, with the measurement.
- **The lead, at the mint:** mint this record before the FD 9487 fix plan, which cites it,
  and replace working id 9485 everywhere this commit writes it.

## Spec changes in this commit

None to a requirement. OQ 9486 is marked decided in both places, `docs/open-questions.md` and
`03` §10, citing this record and the 20:58:27 BST entry; the `docs/roadmap.md` §10 gate row
"Before the FD 9487 fix plan mints" records it decided. T1 and T2 are the fix slice's to apply.
