---
id: RL-9710
family: ruling
title: WK-673 Slice 7 spec texts — FD-1358's per-cell weight is served by a separate cursor-paged diff-cells route over every changed cell, and exposure_weights is a pure pricing-core function with a dated 03 §5.2 entry
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-05              # the mint date (check 31); ruled 2026-10-05
owner: decision-maker
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FD-1358, RL-1361, PL-1267, PL-1286, FR-231, FR-232, FR-450]
---

# RL 9710 (working id) — WK-673 Slice 7 spec texts: the paged diff-cells route and the exposure_weights entry

## How this was ruled

- **Filed under working id 9710, allocated by the lead.** The id is replaced at the mint.
  In the texts below, `RL-9710` stands for this ruling's minted id.
- **The decisions are not this record's.** They are the maintainer's, by delegation, in the
  entry "2026-10-05 12:58:22 BST — DECISIONS (the maintainer, by delegation): FD 9780; DP-A;
  OQ 9739; RL 9715 DP-2; PL 9716 DP-B; the OQ 9739 row" (`channel/to-lead.md`), items 2 and 5:
  - **DP-A (PL 9716, FD-1358): option (c)**, "a separate paged cells route. NOT the
    recommended (b)". `RateTableDiff` "stays the aggregate summary, with no contract break".
    "(a) is refused: it would rewrite FR-231 down to aggregates." "The DM drafts the spec
    texts: the route in 03 §5.1 with its paging and ordering, the cell schema in
    model-schema, and the refusals."
  - **DP-B (PL 9716): option (a)**, "A pure pricing-core `exposure_weights(...) ->
    PortfolioWeights` with a dated 03 §5.2 entry. … The planner drafts the T-text; a DM
    adopts it in a ruling before the executor uses it."
- **This record drafts texts for those options and decides nothing beyond them.** Where a
  text needed a detail the decisions do not name, the detail is the repository's standing
  convention or behaviour already on main, cited at the tree above; each one is listed under
  "Details taken from main" so a reader can check that no new choice was made.
- **Brief:** `brief-dm-1358-2026-10-05.md` (the lead, 2026-10-05).

## Locators — read at `caa4e411`

- `03-rating-engine.md:122`, FR-231: "Rate table edits are diffable cell-by-cell against any
  prior version, with the diff showing absolute and relative change and the exposure weight
  behind each cell (from the portfolio dataset), so an actuary sees which edits matter." No
  dated amendment on the row at this tree (`grep -n "FR-231" docs/specs/03-rating-engine.md`).
  `RL-1361` T3 (its clarification) is not yet applied: it is Slice 7's.
- `03:123`, FR-232: rows to a configurable cell count (default 250 000), a parquet blob
  above it; above it "FR-231's diff and its exposure weighting become a Job returning the
  same artifact, and the API answers 202 rather than 200 for them". "Everything a caller
  may *ask* is identical; only the latency and the status code differ." No dated amendment.
- `03:904`, the §5.1 diff row, as `RL-1361` T10 found it at `:785` (the row moved; its bytes
  did not). The §5.1 table has three columns, `Method | Path | Purpose`; a permission is
  stated in the Purpose cell (`03:897-900`, the Sub-graph rows: "requires `rating:read`").
  There is no permission column on main, so none is used here.
- `packages/model-schema/src/model_schema/rating.py:735-747`, `RateTableDiff`:
  `changed_cells`, `max_abs_change_pct`, `exposure_weighted_mean_change_pct`.
- `packages/pricing-core/src/pricing_core/rate_tables/operations.py:384-435`,
  `_compute_diff`: a changed cell is a key in either version whose value differs, added and
  removed keys included; the set is `sorted(...)` over `KeyTuple` (`:85`, `tuple[str, ...]`,
  one value per declared key in key-declaration order); a percentage needs both values and a
  non-zero baseline.
- `backend/src/app/api/pagination.py:37-38,45,48-61,64-99`: `DEFAULT_LIMIT`, `MAX_LIMIT`,
  `Limit`, `Page[T]` (`items`, `next_cursor`, `total_estimate`, counted up to `COUNT_CAP`),
  `encode_cursor(int)`, `decode_int_cursor`, and `_malformed()` — **400**
  `VALIDATION_FAILED` "Malformed cursor". `00-overview.md` §5.2 and `07` FR-450: cursor
  pagination everywhere.
- `backend/src/app/errors.py:465-490`: a request that fails parameter validation (a `limit`
  out of range) answers **422** `VALIDATION_FAILED`.
- `backend/src/app/api/rate_tables.py:268-327`: the diff route's 202 path submits
  `JobKind.RATE_TABLE_DIFF` (`model_schema/jobs.py:55`, `"rate_table.diff"`) and sets
  `Location: /api/v1/jobs/{id}`; the Job stores its artifact as a blob, `result.ref` its
  sha256. `backend/src/app/platform/diff_cache.py:1-17`: the DP3 cache is keyed by both
  versions' content hashes and the portfolio identity, never a date, and fails open.
- `PL-01286` (WK-675) `:288-292` (F-W10-2 to WK-673; "The editor's exposure-weight column
  (Slice 5) depends on `PL-1267` Slice 7 and ships with the weights") and `:307` (S5: the
  diff route's 202 with a Job, "the view polls the Job and renders the same artifact"; the
  exposure-weight column). S4 (`:306`) pages the grid "with no Job" through the cell read
  route — a different route, not this one.

## Details taken from main (no new choice)

| Detail | Taken from |
|---|---|
| Page size: `limit` 1 to `MAX_LIMIT`, default `DEFAULT_LIMIT` | `app.api.pagination`, by symbol; `00` §5.2 |
| Page body: `Page[RateTableDiffCell]` | `app.api.pagination.Page` |
| Cursor: opaque, a position (an integer) in the ordered set | `encode_cursor(int)` / `decode_int_cursor` |
| Bad cursor: **400** `VALIDATION_FAILED` | `pagination._malformed()` |
| Bad `limit`: **422** `VALIDATION_FAILED` | `errors.py` request-validation handler |
| Order: key tuple in key-declaration order, each value compared as its stored string by code point | `_compute_diff`'s `sorted` over `KeyTuple` |
| The cell set: exactly what `changed_cells` counts | `_compute_diff` |
| Relative change: null without both values or with a zero baseline | `_compute_diff` |
| Portfolio checks, codes and order | `RL-1361` T10 (the diff row), restated, not changed |
| 202 with a Job, `Location`, blob `result.ref` | the diff route (`rate_tables.py:300-316`) and FR-232 |
| No new error code | every refusal below uses a code `03` already owns or re-raises (`DATASET_NOT_VALIDATED` via `RL-1361` T11) |

One identifier is new and is a product identifier, not a choice of option: the Job kind
`rate_table.diff_cells`. A per-page Job on a table of millions of cells, or reusing
`rate_table.diff` and changing the artifact its summary route already returns, would each
break the decision's "no contract break" or FR-232's "only the latency and the status code
differ"; a separate kind breaks neither.

## Ruled

1. **DP-A, as decided (option (c)).** FR-231's per-cell change and weight are served by a
   separate route, `GET /api/v1/rate-tables/{slug}@{version}/diff/cells`, cursor-paged over
   every changed cell in a total key order, as `RateTableDiffCell` items. `RateTableDiff`
   and the diff route are unchanged. Parquet-stored versions answer 202 with a
   `rate_table.diff_cells` Job, then 200 pages from its stored artifact (FR-232). The texts
   are T1–T4.
2. **DP-B, as decided (option (a)).** `exposure_weights(...) -> PortfolioWeights` is a pure
   `pricing-core` function with a dated `03` §5.2 entry. The text is T5.

## The spec texts

Each item gives the file, the place, who applies it, and the exact bytes. Placement was read
at `origin/main` `caa4e411`. The placeholders are `RL-9710` (this ruling's minted id) and
`<Slice 7 date>` (the date of the WK-673 Slice 7 commit that applies the item). Nothing else
in a text is a placeholder. All five are applied by Slice 7, in one commit with the code
(`CLAUDE.md` §2).

**T1 — `03` §5.1, the diff-cells route (DP-A items 1, 2, 4, 5).** Placement: a new row
**inserted immediately after** the diff row (`03:904` at `caa4e411`, the row `RL-1361` T10
replaces; insert after T10's replacement if T10 is applied first). Insert

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff/cells?against=&portfolio=&limit=&cursor=` | **200** One cursor page of the diff's changed cells (FR-231), `Page[RateTableDiffCell]` (§4.2): every cell the diff's `changed_cells` counts, ordered by key tuple (§4.2), with each cell's baseline and current value, absolute and relative change, and its exposure weight when `portfolio` names a `validated` portfolio Dataset Version, weighted as the diff row states. The pages together hold every changed cell; nothing is capped but the page. Requires `rating:read`. `limit` is 1 to `MAX_LIMIT`, default `DEFAULT_LIMIT` (`00` §5.2); `next_cursor` is null on the last page; `total_estimate` is the diff's `changed_cells`, counted up to `COUNT_CAP`. **202** with a `rate_table.diff_cells` Job and a `Location` header where either version is `storage: parquet` (FR-232) and the query's cell artifact is not yet stored: the Job writes every changed cell, in order, as one content-addressed blob keyed like the diff's cache by both versions' content hashes and the portfolio's identity, and the same request then answers **200** with pages read from it; an artifact that cannot be found is computed again, never served from another query. `against` and `portfolio` are checked as on the diff row, before any cell is read and before any Job: **404** `NOT_FOUND` for an unknown table, version or `against`; with `portfolio`, **403** without `dataset:read`, the same for any id, **404** `NOT_FOUND` for a portfolio that is missing or in another workspace, **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio, **404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve, and **422** `VALIDATION_FAILED` for the diff row's portfolio faults. **400** `VALIDATION_FAILED` for a cursor this API did not issue or one past the last cell; **422** `VALIDATION_FAILED` for a `limit` out of range. A Job fails with the same codes. `RateTableDiff` on the diff row is unchanged. (**added <Slice 7 date>, `RL-9710`, FD-1358**) |
```

**T2 — `03` §4.2, the cell shape and its order (DP-A items 2 and 3).** Placement: a
blockquote paragraph **inserted after** `RL-1361` T6's "Coverage added" paragraph, with one
blank line between them. Insert

```text
> **Per-cell diff added <Slice 7 date> (`RL-9710`, FR-231, FD-1358).** The diff's changed
> cells are served one page at a time by `GET …/diff/cells` (§5.1), as `RateTableDiffCell`
> items in `model-schema`: `key`, an object holding each declared key's name and the cell's
> stored value for it; `change`, one of `added`, `removed`, `changed`; `baseline_value` and
> `current_value`, decimal strings, null on the side where the cell is absent;
> `abs_change`, `current_value − baseline_value`, null unless both are present;
> `rel_change_pct`, `(current_value − baseline_value) / baseline_value × 100`, null unless
> both are present and the baseline is not zero; and `weight`, a decimal string: the
> cell's Σ exposure as FR-231 states it, `"0"` for a cell of the current version that no
> portfolio row maps to, and null when no portfolio is named or the cell is `removed`
> (rows map only to cells of the current version). The set is exactly the cells
> `changed_cells` counts, added and removed cells included. The order is ascending by key
> tuple, the keys taken in declaration order and each value compared as its stored string
> by code point; a version is immutable and a key tuple unique within it, so the order is
> total and every page is reproducible. The items agree with the summary:
> `max_abs_change_pct` is the largest `|rel_change_pct|`, and
> `exposure_weighted_mean_change_pct` is Σ(`weight` × `rel_change_pct`) / Σ `weight` over
> the items where both are present and `weight` is not zero. `RateTableDiff` is unchanged.
```

**T3 — `03` §5.2, `diff_cells` (DP-A item 3, the pure core of T1).** Placement: after the
`diff_vs_seed` signature (`03:1117-1119` at `caa4e411`), before the closing fence. Insert

```text
def diff_cells(baseline_cells: Cells, current_cells: Cells,            # added <Slice 7 date> (RL-9710, FD-1358):
               keys: Sequence[RateTableKey], value: RateTableValue, *,  # every changed cell in §4.2's order,
               weights: Weights | None = None) -> list[RateTableDiffCell]  # the set diff_vs_* count
```

**T4 — `03` FR-231, the route named (DP-A item 6).** Placement: the FR-231 row (`03:122`).
The text is **appended** to the end of the second cell, after `RL-1361` T3's text (or after
`so an actuary sees which edits matter.` if T3 is not yet applied) and one space, before the
closing ` |`. Nothing is struck.

```text
**Clarified <Slice 7 date> (`RL-9710`): the weight behind each cell (FD-1358).** Each changed cell's baseline and current value, absolute and relative change and exposure weight are served by `GET /api/v1/rate-tables/{slug}@{version}/diff/cells` (§5.1), one cursor page at a time in §4.2's key order, with no cap on the cells but the page. `RateTableDiff`, on the diff route, stays the aggregate summary of the same cells.
```

**T5 — `03` §5.2, `exposure_weights` (DP-B).** *Pending planner-1391's proposed text; this
item is completed, and the adoption or amendment stated, before the PR leaves draft.*

## What it obliges

- **This commit:** this record only. No spec, `model-schema` or code file is edited here.
- **WK-673 Slice 7 (PL 9716, the planner's file, not edited here)** applies T1–T5 with the
  code in one commit: `RateTableDiffCell` in `model_schema/rating.py`;
  `JobKind.RATE_TABLE_DIFF_CELLS = "rate_table.diff_cells"` in `model_schema/jobs.py`;
  `diff_cells` in `pricing_core/rate_tables/operations.py`, sharing `_compute_diff`'s pass so
  that the summary and the cells cannot disagree; the route; the worker handler; and the
  regenerated `docs/contracts/` (FR-451). `RateTableDiff`'s contract does not change.
- **FD-1358** is closed by that commit when the acceptance below is met. The verdict is the
  lead's.
- **PL-1286 S5 (WK-675)** reads the per-cell weight from this route. That plan is frozen and
  is not edited; its S5 leaf plan names the route.
- **Observed at `caa4e411`, for the lead (not a correction of `RL-1361`, which this record
  does not make):** `RL-1361` T11's find string ends
  `` `app.platform.traces.complete_pending_trace` is the only raiser)*. `` On main that
  clause now ends `)*,` and `RATING_VERSION_IMMUTABLE` (`RL-1379`) follows it
  (`03:963-965`), so T11's bytes do not match. Its intent — append `DATASET_NOT_VALIDATED`
  at the paragraph's end — is unaffected; Slice 7's executor will meet the mismatch.

## Acceptance — the violation that must become detectable

The violation: **a changed cell whose change or weight the caller cannot get, or gets wrong,
or gets from a page that a repeat request would not return.** Each test is shown failing on
deliberately broken input.

- **FD-1358's own evidence.** A two-cell change returns each cell's `abs_change`,
  `rel_change_pct` and `weight` equal to hand-computed figures. Red on `caa4e411`: the route
  does not exist.
- **No cap.** An `uplift_table` over a table with more than `MAX_LIMIT` cells is served in
  full across pages: the items number `changed_cells`, and no key repeats. With a cap
  introduced, the test fails.
- **The order.** Pages at `limit=1` concatenate to `diff_cells`' full list in §4.2's order. A
  fixture with key values `"9"` and `"10"` places `"10"` first. A repeat of any page returns
  identical bytes.
- **Agreement with the summary.** `max_abs_change_pct` and
  `exposure_weighted_mean_change_pct` recomputed from the items equal `RateTableDiff`'s, with
  and without a portfolio. With `diff_cells` computed apart from `_compute_diff` and one
  zero-baseline rule changed, the test fails.
- **The weight's three states.** Null with no portfolio; null on a `removed` cell with one;
  `"0"` on a current cell no row maps to. With a missing weight read as `"0"` everywhere,
  the test fails.
- **Cursor and limit.** A forged cursor and a cursor past the last cell each give 400
  `VALIDATION_FAILED`; `limit=MAX_LIMIT+1` gives 422.
- **Portfolio refusals before anything else.** Each refusal of T1 is given on a rows table
  and on a parquet table, and the parquet case writes **no Job row**. A rating-only caller
  succeeds without `portfolio`.
- **The 202 path.** A parquet version gives 202 with a `rate_table.diff_cells` Job and a
  `Location`. After the Job succeeds, the same request gives 200 pages equal to the
  rows-stored twin's. With the stored artifact removed, the request gives 202 again, never
  another query's page. A portfolio archived between submit and run fails the Job with
  `DATASET_NOT_VALIDATED`.
- **No contract break.** `docs/contracts/` is regenerated with `RateTableDiff` byte-identical
  and `RateTableDiffCell` added.

Drafted as working id 9710.
