---
id: RL-9484
family: ruling
title: The rate-table cells route serves every page from the stored artifact, keyed by immutable version identity; the first request for a key may answer 202 on either storage (amends RL-1418 T1 and FR-232)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: b6dd96fdf9ad74a5fbb4593ac7b041dbabc9446e
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1418
relates: [WK-673, WK-1178, RL-1418, PL-1419, FR-231, FR-232, NFR-457]
---

# Ruling — the rate-table cells route serves its pages from the stored artifact

**Decided by the maintainer, by delegation**, in the entry headed
*"2026-10-05 22:25:03 BST — S7 R1 STOP: (C) REFUSED (it does not comply); (A) with the
IDENTITY key, INSIDE S7, by an RL first; FD 9487 widened to the diff route"* in
`~/gi-pricing-plan.local/channel/to-lead.md` (`:18852`). The decision, verbatim:

> (C) is REFUSED. By its own description, "the pages after the Job still reload and hash". At 250k that is the SQL load (p50 5.5 s) plus the hash (0.4 s) on EVERY later page, so the route would still breach R1 after the Job. It is not a stopgap; it moves the breach from the first page to every other page.
> DECISION: (A), INSIDE S7 (no merge of a route its own spec forbids):
> - Every cells page for a version pair is served from the stored artifact. The first request for a (versions, portfolio) key answers 202 with a Job (rows pairs too), and later pages read only their NDJSON slice.
> - THE KEY is IMMUTABLE VERSION IDENTITY ((slug, version) of each side, plus the portfolio Dataset Version id). A page finds its artifact WITHOUT loading or hashing any cells. NO migration. The content-hash twin sharing I accepted earlier (S7's twin-key test) is REVERSED: twins no longer share an artifact. That costs at most one extra Job per twin pair, never correctness. The twin test is rewritten to assert that identity keys are distinct and that each twin's artifact has identical content. A stored per-version hash is NOT added now; if twin sharing is ever wanted, that is a later optimisation with its own migration.
> - SPEC FIRST: ONE RL (a DM) amending RL-1418 T1 / 03:933 (the 202 condition becomes "where the query's cell artifact is not yet stored", for EITHER storage) and FR-232's "the editor pages without a job" (a dated amendment saying the FIRST request for a pair may answer 202; later pages do not). It cites R1, this entry, and the measurement file.
> - S7 records it as a plan deviation (a dispatch-record delta, since PL-1419 is frozen), with the write set extended to the artifact-keying code and its tests. It runs red-first: a 250k rows pair's FIRST request answers 202, and a later page at 250k has p99 under 300 ms (RL 9485's NFR, measured in the same protocol). It then RE-GATES.
>
> FD 9487: HIGH (by its conditional rule). Widen its scope: the DIFF route itself (FR-231, the pre-S7 route that S7 extends with weighting) also computes the full diff synchronously for a rows pair (diff_cells about 4 s at 250k). That is a breach ON MAIN today, not S7's. The FD records it with a measurement of the diff route at 250k in the same protocol, and its fix is FD 9487's fix slice under RL 9485 (or S7 if the same artifact path covers it at no extra write set; executor-s7 says which).

The entry's other lines (the measurement accepted, the expected cost, the lane B batch) are
not quoted. The entry headed *"2026-10-05 22:26:27 BST —
No veto: S7 may write reds and code while RL 9484 is drafted"* adds: *"The 03 and FR-232
T-texts are applied ONLY from the MINTED RL 9484, byte for byte, in the same commit as the
code they govern or a later one, never before the RL mints. S7 merges only after that. If RL
9484's drafting changes any T-text the reds assume, the reds follow the RL, not the
reverse."*

## How this was ruled

**Written 2026-10-05, from 22:27 BST**, by the decision-maker session `dm-rl9484`, on the
lead's brief `~/gi-pricing-plan.local/handover/brief-dm-rl9484-2026-10-05.md`. **Working id
9484 is the lead's allocation.** This record drafts the texts the decision names and decides
nothing beyond it. Unminted records (RL 9485, OQ 9486, FD 9487) are cited in working-id form
and kept out of `relates:` (check 32).

## Verified first

| Fact | Where, read at |
|---|---|
| R1: *"**R1 — Everything slow is a Job.** Any operation that can exceed 2 s returns `202` with a Job, has progress, is cancellable, and persists its result (FR-13, NFR-457)."* | `docs/specs/07-platform.md:36-37`, `origin/main` `b6dd96fd` |
| The cells row (RL-1418 T1, applied with the date `2026-10-05`) is `03:933`; its 202 clause answers 202 *"where either version is `storage: parquet` (FR-232) and the query's cell artifact is not yet stored"* and keys the blob *"like the diff's cache by both versions' content hashes and the portfolio's identity"*. On `origin/main` the row is absent: S7 has not merged | `docs/specs/03-rating-engine.md:933` at S7's head `386f4d5485f6efa3fe2d9b05842d4f752d5d989d` (#1206); `grep -c 'diff/cells?against' docs/specs/03-rating-engine.md` gives 0 at `b6dd96fd` |
| FR-232, the sentence amended: *"Rows are the default because they are what makes the rest of this section cheap: FR-231's cell diff is a SQL join, its exposure weighting is a join to the portfolio dataset, and the editor pages without a job."* The row has no dated amendment, and its bytes are identical at S7's head | `docs/specs/03-rating-engine.md:123`, at `b6dd96fd` and at `386f4d54` (a `diff` of the two rows printed nothing) |
| The twin sharing reversed: `test_a_rows_version_and_its_parquet_twin_find_the_same_cells_artifact` | `backend/tests/test_rate_table_diff_portfolio.py:1172` at `386f4d54` |
| The measurement: rows storage at the default threshold, 250 000 cells with a portfolio, page p50 12241 ms, p99 12434 ms (n=10); without a portfolio p99 9848 ms; 100 000 cells p99 4265 ms. Head `386f4d54`, tree `1511ac46`, 22:12:36–22:23:33 BST | `~/gi-pricing-plan.local/handover/s7-measurement-2026-10-05/rows2.out`, sha256 `360b730703491e92b3ecfcca7aba5617868a855ccf7e05b849cf207f3237fc9b`, lines 9–33 |
| RL 9485's NFR: every page after the first request for a key, p95 ≤ 300 ms at `DEFAULT_LIMIT`, measured at n ≥ 100 at 250 000 cells (rows) and 1 000 000 (parquet); the first request for a key may answer 202 | RL 9485 (working id) T1, PR #1222 head `a3a90cbd`, open |
| FD 9487 (working id), the finding | PR #1223 head `8fc404a7`, open |

## Ruled

1. **Every page of the cells route is read from the query's stored cell artifact**, on
   either storage. The first request for a key whose artifact is not yet stored answers
   **202** with a `rate_table.diff_cells` Job; rows pairs too. Later pages read only their
   slice of the artifact. Text T1'.
2. **The key is immutable version identity**: the table `slug` and the `version` of each
   side, plus the portfolio Dataset Version's id (or no portfolio). A page finds its
   artifact without loading or hashing any cell. Versions are immutable, so the key never
   names two different cell sets. **No migration** is made.
3. **Twin sharing is reversed.** Two versions with identical cells no longer share an
   artifact. The maintainer's reason: *"That costs at most one extra Job per twin pair, never
   correctness."* S7's twin test is rewritten to assert that the identity keys are distinct
   and that each twin's artifact has identical content.
4. **No stored per-version content hash is added now.** Twin sharing, if wanted later, is
   *"a later optimisation with its own migration"*.
5. **FR-232's "the editor pages without a job" is amended**: the first request for a key may
   answer 202; later pages do not. Text T2'.
6. **The budget.** Later pages are bound by RL 9485 (working id)'s NFR, deciding OQ 9486
   (working id): p95 ≤ 300 ms after the first request. S7's merge measurement is the
   entry's: a later page at 250 000 cells, rows, with p99 under 300 ms, in the protocol of
   `rows2.out` (n=10, `limit` 50, `OMP_NUM_THREADS=1`, state at both ends). The NFR row
   itself lands with FD 9487's fix slice, as RL 9485 states, and is not applied here.
7. **FD 9487 (working id)** is the finding. S7 discharges its cells-route limb. The diff
   route's limb (FR-231's summary route, synchronous on a rows pair today) is measured
   separately, and its fix is **not ruled here**: the entry assigns it to FD 9487's fix
   slice under RL 9485, or to S7 if the same artifact path covers it with no extra write
   set, as executor-s7 says.

**Not ruled here** (unchanged from RL-1418): whether a request arriving while the key's Job
runs is given that Job or a new one. T1' requires only 202 with a Job until the artifact is
stored.

## The exact texts

**Applied by S7 (SL-1391), from the minted record only**, byte for byte, in one commit with
the code they govern or a later one (the 22:26:27 entry). The placeholders are
`<Slice 7 date>` (the date of that commit) and `RL 9484` (the mint replaces it, in both
texts and their backticks, with the minted `RL-` id). Nothing else is a placeholder.

### T1' — `03` §5.1, the cells row (amends RL-1418 T1)

Placement: the row of `03` §5.1 that begins
`` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff/cells?against= `` (`03:933` at
`386f4d54`; one row matches). The whole row is **replaced** by

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff/cells?against=&portfolio=&limit=&cursor=` | **200** One cursor page of the diff's changed cells (FR-231), `Page[RateTableDiffCell]` (§4.2), read from the query's stored cell artifact: every cell the diff's `changed_cells` counts, ordered by key tuple (§4.2), with each cell's baseline and current value, absolute and relative change, and its exposure weight when `portfolio` names a `validated` portfolio Dataset Version, weighted as the diff row states. The pages together hold every changed cell: a page bounds one response, not the cells. Requires `rating:read`. `limit` is 1 to `MAX_LIMIT`, default `DEFAULT_LIMIT` (`00` §5.2); `next_cursor` is null on the last page; `total_estimate` is the diff's `changed_cells`, counted up to `COUNT_CAP`. **202** with a `rate_table.diff_cells` Job and a `Location` header where the query's cell artifact is not yet stored, whatever `storage` either version has (FR-232, `07` §1.3 R1): the Job writes every changed cell, in order, as one content-addressed blob, and the same request then answers **200** with pages read from it. The artifact is keyed by the query's immutable identity, the table `slug` and the `version` of each side and the `portfolio` Dataset Version's id (or no portfolio), so a page finds it without loading or hashing any cell; two versions with identical cells do not share an artifact. An artifact that cannot be found is computed again, never served from another query. `against` and `portfolio` are checked as on the diff row, before any cell is read and before any Job: **404** `NOT_FOUND` for an unknown table, version or `against`; with `portfolio`, **403** without `dataset:read`, the same for any id, **404** `NOT_FOUND` for a portfolio that is missing or in another workspace, **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio, **404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve, and **422** `VALIDATION_FAILED` for the diff row's portfolio faults. **400** `VALIDATION_FAILED` for a cursor this API did not issue or one past the last cell; **422** `VALIDATION_FAILED` for a `limit` out of range. A Job fails with the same codes. This route adds no field to `RateTableDiff` and changes nothing on the diff row. (**added 2026-10-05, `RL-1418`, FD-1358; the 202 condition and the key amended <Slice 7 date>, `RL 9484`, FD 9487**) |
```

*What changes against the row at `386f4d54`*, and nothing else: `, read from the query's
stored cell artifact` after `(§4.2)` in the 200 clause; the 202 condition
``where either version is `storage: parquet` (FR-232) and the query's cell artifact is not yet stored``
becomes
``where the query's cell artifact is not yet stored, whatever `storage` either version has (FR-232, `07` §1.3 R1)``;
the blob's key ` keyed like the diff's cache by both versions' content hashes and the
portfolio's identity` is removed, and the sentence on the identity key and the twins is
added; `; an artifact that cannot be found` becomes a new sentence; the marker gains
``; the 202 condition and the key amended <Slice 7 date>, `RL 9484`, FD 9487``.
Predicate, run from the repository root: `git diff --no-index --word-diff=plain` of
`git show 386f4d54:docs/specs/03-rating-engine.md | sed -n 933p` against the T1' block above
printed only these changes.

### T2' — `03` FR-232 (the dated amendment)

Placement: the FR-232 row (`03:123` at `b6dd96fd` and at `386f4d54`). The text is
**appended** to the end of the second cell, after `only the latency and the status code
differ.` and one space, before the closing ` |`. Nothing is struck.

```text
**Amended <Slice 7 date> (`RL 9484`, FD 9487): the per-cell diff's first request may answer 202, on either storage.** "The editor pages without a job" holds for every page of FR-231's per-cell diff (`GET …/diff/cells`, §5.1) after the first request for a key, the two versions and the `portfolio`: that first request may answer **202** with a `rate_table.diff_cells` Job, whatever `storage` either version has, because computing the cells at the threshold exceeds `07` §1.3 R1's 2 s; later pages are read from the key's stored artifact and answer **200** without a Job.
```

## Acceptance — the violation that must become detectable

The violation: **a cells page that loads or hashes the versions' cells, or a pair whose
first request computes the cells synchronously.** Each test is shown failing on deliberately
broken input. These amend RL-1418's acceptance items "The 202 path" and the twin case; its
other items stand.

- **Rows pairs answer 202 first.** A 250 000-cell rows pair's first request answers 202 with
  a `rate_table.diff_cells` Job and a `Location`; after the Job succeeds the same request
  answers 200. Red at `386f4d54`, which answers 200 synchronously.
- **A page reads only the artifact.** A later page does not load either version's cells nor
  compute a content hash: with the cell-load or the hash path made to raise, pages still
  answer 200.
- **The budget.** A later page at 250 000 cells, rows, has p99 under 300 ms in `rows2.out`'s
  protocol (ruled item 6).
- **Identity keys.** The rewritten twin test: a rows version and its parquet twin give
  distinct keys, each answers 202 first, and the two artifacts' contents are identical.
- **No cross-query serving.** With the stored artifact removed, the request answers 202
  again, never another key's page (RL-1418's item, kept).

## What it obliges

- **This commit:** this record only. No spec, `model-schema` or code file is edited.
- **S7 (SL-1391, #1206)**: records this as a plan deviation by a dispatch-record delta
  (PL-1419 is frozen and is not edited), with its write set extended to the artifact-keying
  code and its tests; runs red first; applies T1' and T2' from the minted record; re-gates.
- **At the mint**: RL-1418's `corrected_by` gains this record's id.
- **FD 9487's fix slice**: lands RL 9485's NFR row, and the diff route's limb unless S7
  takes it as ruled item 7 allows.

Drafted as working id 9484.
