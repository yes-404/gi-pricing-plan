---
id: FD-9487
family: finding
title: The rate-table cells-diff page's p99 exceeds 1 s at 260 000 cells
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: a5657fa4520739f182cbea79e0057afeed991ac1
corrected_by: []
relates: [WK-1178, WK-673, FR-231, FR-232, NFR-457, FD-1358, RL-1418, SL-1391]
---

# The cells-diff page recomputes its whole input on every request: p99 1098 ms on the parquet path and 9995 ms on the rows path, at 260 000 cells

**Filed** by auditor-cost on the lead's brief of 2026-10-05, working id 9487 (the companion open question is OQ 9486, working
id), from the maintainer's (by delegation) filing rule in `to-lead.md`, entry headed "2026-10-05 18:25:08 BST — S7 cells-page
cost: my SPEC READING now, and the decision rule for the numbers" (a local channel file, so cited by its header). The rule,
verbatim: *"If it exceeds 3x, or any page's p99 exceeds 1 s: an FD (a proposed severity, owner WK-1178) naming two gaps: (a)
the cost, whose fix is to find the artifact without reloading (the content hashes recorded at the first request, on the
version or in the Job parameters); (b) the ABSENCE of a latency NFR for these routes, as an OQ for me (owner WK-673). The fix
is a small follow-on slice, not S7 scope."* and *"The 3x and 1 s are MY decision thresholds for filing, not a requirement"*:
the 3x and the 1 s are filing thresholds, not requirements, and this finding is filed on the second, not on a breach of a
numbered NFR. This finding is gap (a). Gap (b) is OQ 9486.

## Finding

**Severity: MEDIUM (proposed by the auditor; the lead gives the verdict); owner WK-1178.** At S7's branch head
`386f4d5485f6efa3fe2d9b05842d4f752d5d989d` (SL-1391, PR #1206, not merged at filing), a request for one page of the diff's
changed cells (`GET …/diff/cells`, `03` §5.1, row added by `RL-1418`) costs the same whatever the page: it reloads and
re-derives everything the page is cut from. Measured at the service level (`diff_cells_page`, not HTTP) over 260 000 cells,
N = 10 pages, limit 50, `OMP_NUM_THREADS=1`:

| Storage | whole page p50 | whole page p99 | loading both versions' cells p50 / p99 | `version_content_hash` ×2 p50 / p99 |
|---|---|---|---|---|
| parquet (the default above 250 000 cells, FR-232) | 948 ms | 1098 ms | 421 / 445 ms | 428 / 455 ms |
| rows (workspace threshold raised above 260 000 for the measurement) | 9604 ms | 9995 ms | 5544 / 5871 ms | 388 / 416 ms |

The filing rule's two limbs: the parquet p50 is 0.10× the rows p50 (948 / 9604), so the 3× limb **does not** fire; **any p99 over
1 s is met**, by both (parquet 1098 ms, rows 9995 ms). Two readings to hold against the numbers: (i) **N = 10, so the p99 is the
maximum** (`measure_cells.py` `pct`: index `round(0.99 × 9)` = 9); it says the worst of ten pages, not a tail estimate; (ii) the
rows figure is at 260 000 cells only because the threshold was raised for the measurement. A rows table can hold up to 250 000
cells at the default, with no setting changed; its page cost at that size was **not measured** (the load is SQL, so a linear
guess is a guess).

**What dominates.** On the parquet path, loading plus hashing both versions is 421 + 428 = 849 ms of the 948 ms p50, about 90 %
(the parts were timed in a separate loop from the whole requests, so the 90 % is a sum of components, not an in-request
profile; the remaining ~100 ms is unattributed: the stored-artifact read, `splitlines` over 260 000 lines and the cut). The
code says why at the head above, `backend/src/app/platform/rate_tables.py:645` (`diff_cells_page`): for a parquet pair each
request calls `_content_hash` for both versions (each loads the version's cells and hashes them), builds the cache key from the
two hashes, then reads the stored artifact and cuts one page; there is nothing between requests that keeps the hashes. On the
rows path each request calls `_all_cells`, which recomputes the whole diff and weights before `_page` cuts 50 of them: load
from SQL 5.5 s, hash 0.4 s, and the remaining ~3.7 s is `diff_cells` plus the cut. This finding does not propose a design for
either; the maintainer's rule names the direction (find the artifact without reloading) and a plan owns the choice.

## Requirement context: is any latency budget on this route? (searched, not assumed)

Searched at `a5657fa4520739f182cbea79e0057afeed991ac1` (`origin/main`) and again over the three specs at S7's head
`386f4d54…` (the route's own row, `03:933`, exists only there):

```
grep -n -E '^\| \*\*NFR-[0-9]+\*\*' docs/specs/0[0-7]-*.md | grep -i -E 'diff|cells|page|pagina|cursor|list'
grep -n -E '^\| \*\*NFR-' <03|00|07 at 386f4d54> | grep -i -E 'diff|cells|page|pagina|latency|p99|p95|[0-9] ?s\b'
```

All 83 NFR rows of `00` to `07` were in the first predicate's corpus (`grep -c -E '^\| \*\*NFR-[0-9]+\*\*'` per file: 11, 10, 14, 14, 7,
8, 8, 11). **No NFR row names the diff route, the cells route or a rate-table page.** The rows that touch a latency or a page, and
what each covers:

- **NFR-457** (`00`): *"Interactive UI: p95 < 300 ms for metadata reads; any operation exceeding 2 s becomes a Job with
  progress."* The second clause names no route. It is the one general clause a reader could apply: the parquet page (p99
  1.1 s) is under 2 s; the **rows page (9.6 s) is over 2 s and is a synchronous 200**, which FR-232 prescribes for a rows
  pair ("the editor pages without a job"). Whether a changed-cells page is an "operation" that NFR-457 reaches, or a read the
  first clause's "metadata" excludes, is a reading the text does not settle: it is raised in OQ 9486 and not decided here.
- **NFR-526** (`07`): API metadata reads p95 < 300 ms (NFR-457); a cells page is not obviously "metadata".
- **NFR-471** (`01`): the validation report summary < 500 ms; **NFR-520** (`06`): a filtered audit page < 2 s. These are the
  repository's two precedents for a budget on a paged read; neither covers a rate table.
- **NFR-489 to NFR-502** (`03`): scoring, tracing, bundle, batch and deployment budgets; none names a rate-table read.

FR-232 states that above the threshold only "the latency and the status code differ", so a slower page is permitted by its text;
the maintainer's (by delegation) reading of 2026-10-05 18:25:08 BST is that the per-page reload is not an S7 defect. Nothing
here contradicts that reading: this finding concerns a cost nothing bounds, and the entry's gap (b) asks for the budget
as a question (OQ 9486).

## Evidence

The measurement protocol and raw output are kept in the lead's local handover directory
`handover/s7-measurement-2026-10-05/` (`measure2.out`, `measure_cells.py`, `run_measure.sh`, `measure_inner.sh`), so the raw
output is quoted here, not cited by path alone. Run 2026-10-05 20:45:27 to 20:49:46 BST at the head above (tree
`1511ac46a4f5298a01cb65820bdcf559639b0046`), one gate-1 hold, no check process running, load 1.01 at start, 0.92 at the GO, 1.29
at the end. The raw output follows, verbatim except that the `setup` timing lines, the memory table and the empty `pgrep` blocks are omitted:

```
=== PARQUET 20:45:46 load1=0.92
storages (all versions in this DB): [(1, 'parquet'), (2, 'parquet')]
first request: DiffCellsJobNeeded
cells Job succeeded in 6.8s
v1/v2 storage: parquet parquet
page request (whole): n=10 p50=948ms p99=1098ms max=1098ms
  of which load both versions' cells: n=10 p50=421ms p99=445ms max=445ms
  of which version_content_hash x2: n=10 p50=428ms p99=455ms max=455ms
=== ROWS 20:46:22 load1=1.84
storages (all versions in this DB): [(2, 'parquet'), (2, 'rows')]
v1/v2 storage: rows rows
page request (whole): n=10 p50=9604ms p99=9995ms max=9995ms
  of which load both versions' cells: n=10 p50=5544ms p99=5871ms max=5871ms
  of which version_content_hash x2: n=10 p50=388ms p99=416ms max=416ms
```

The rows block began at load 1.84 (the first line above carries it). An earlier run (18:56 BST: p50
1024 ms, p99 1204 ms) is recorded as **invalid** (load 7.2, no rows baseline) and is not used; this run is consistent with it.

## Disposition

**Carry forward with an owner: WK-1178**, a small follow-on slice, not S7 scope (the maintainer's rule). Severity MEDIUM
because no numbered budget is breached by the parquet path, the page is correct, and the rows path's 10 s needs a table near the
threshold's top; it **rises to HIGH if the lead reads NFR-457 as binding the rows page** (a 9.6 s synchronous 200 against a
"becomes a Job above 2 s" clause), which is the question OQ 9486 puts. The acceptance a fix plan would carry is not set
here: it needs the budget OQ 9486 asks for. Companion: OQ 9486 (working id), the latency budget these routes should carry.
