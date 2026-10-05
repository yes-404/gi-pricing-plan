---
id: FD-1439
family: finding
title: The rate-table cells-diff page's p99 exceeds 1 s at 260 000 cells
status: active
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: auditor
tree: a5657fa4520739f182cbea79e0057afeed991ac1
corrected_by: []
relates: [WK-1178, WK-673, FR-231, FR-232, NFR-457, FD-1358, RL-1418, SL-1391]
---

# The cells-diff page recomputes its whole input on every request: the rows page took p50 9604 ms at 260 000 cells against R1's 2 s, and the parquet page p99 1098 ms

**Filed** by auditor-cost on the lead's brief of 2026-10-05, working id 9487, minted as FD-1439 (the companion open question is OQ-1440, minted as OQ-1440), from three entries of the maintainer (by delegation) in `to-lead.md` (a local channel file, so each is cited by its header):

1. The filing rule, entry headed "2026-10-05 18:25:08 BST — S7 cells-page cost: my SPEC READING now, and the decision rule for
   the numbers": *"If it exceeds 3x, or any page's p99 exceeds 1 s: an FD (a proposed severity, owner WK-1178) naming two gaps:
   (a) the cost…; (b) the ABSENCE of a latency NFR for these routes, as an OQ for me (owner WK-673)."* and *"The 3x and 1 s are MY
   decision thresholds for filing, not a requirement."* **Its reading that no NFR bounds the route is SUPERSEDED by entry 3**; the
   filing rule itself was applied to the clean numbers and fired on the p99 limb.
2. The acceptance, entry headed "2026-10-05 20:51:44 BST — S7 measurement ACCEPTED; FD 9487 must lead with the ROWS path, the
   larger cost": *"the ROWS-stored page (p50 9604 / p99 9995 ms, about 3.7 s of diff+cut RECOMPUTED ON EVERY PAGE, plus 5.5 s of SQL
   load) is TEN TIMES the parquet page. Rows storage is the NORMAL path for every table up to FR-232's 250k default, so a
   near-threshold rows table pays about 9 s per page TODAY. The parquet reload is the smaller limb."*
3. The correction, entry headed "2026-10-05 20:53:32 BST — CORRECTION to my 18:25:08 reading: R1 bounds the cells route; a
   sub-threshold ROWS measurement is now an S7 MERGE CONDITION": *"That rested on an NFR-rows-only search. It is WRONG, and
   SUPERSEDED: 07 1.3 R1 (:36-37: "Everything slow is a Job. Any operation that can exceed 2 s returns 202 with a Job …") and 00
   NFR-457 (:534) bound EVERY operation, these routes included."* and *"MERGE CONDITION for S7 (#1206): measure the ROWS-stored
   cells page AT THE THRESHOLD, 250 000 cells … plus 100k for the curve. If p99 is at or under 2 s at 250k: S7 mints and merges.
   FD-1439 then covers the parquet limb and anything over the threshold … If p99 is over 2 s at 250k: R1 is BREACHED by S7's own
   new route. STOP to me BEFORE the mint."*

## Finding

**Two limbs, the rows path first. Severity: HIGH, provisional, LATENT in the data that exists today (proposed by the auditor; the
lead gives the verdict); owner WK-1178.** The reasons are under Disposition. At S7's branch head
`386f4d5485f6efa3fe2d9b05842d4f752d5d989d` (SL-1391, PR #1206, not merged at filing), one page of the diff's changed cells
(`GET …/diff/cells`, `03` §5.1, row added by `RL-1418`, `03:933` at that head) costs the same whatever the page: the service
reloads and re-derives everything the page is cut from. Measured at the service level (`diff_cells_page`, not HTTP), 260 000
cells, N = 10 pages, limit 50, `OMP_NUM_THREADS=1`:

| Storage | whole page p50 | whole page p99 | loading both versions' cells p50 / p99 | `version_content_hash` ×2 p50 / p99 |
|---|---|---|---|---|
| **rows** (workspace threshold raised above 260 000 for the measurement) | **9604 ms** | **9995 ms** | 5544 / 5871 ms | 388 / 416 ms |
| parquet (the default above 250 000 cells, FR-232) | 948 ms | 1098 ms | 421 / 445 ms | 428 / 455 ms |

### Limb 1 (first): the rows page recomputes the whole diff on every page, and nothing bounds it below 2 s

`diff_cells_page` (`backend/src/app/platform/rate_tables.py:645` at the head above) answers a rows pair by calling `_all_cells`,
which loads both versions from SQL, diffs them and weights them, and then `_page` cuts 50 of the result. Nothing is kept between
pages: the SQL load is 5.5 s, the hash 0.4 s and the remaining ~3.7 s is `diff_cells` plus the cut, on **every** page request. The
rows page is **ten times the parquet page** (9604 / 948 ms) and rows is the **normal** storage for every table up to FR-232's 250 000
default, so the route as specified answers a rows table with a synchronous `200` (`03:933`: the `202` is only for a version with
`storage: parquet`).

**Does the text of R1 find a breach?** The text, verbatim, `07` §1.3 (`docs/specs/07-platform.md:36-37`): *"R1 — Everything slow
is a Job. Any operation that can exceed 2 s returns `202` with a Job, has progress, is cancellable, and persists its result (FR-13,
NFR-457)."* and `00` NFR-457 (`docs/specs/00-overview.md:534`): *"Interactive UI: p95 < 300 ms for metadata reads; any operation
exceeding 2 s becomes a Job with progress."* R1 is conditioned on an operation that *can* exceed 2 s, not on one that does at a
default size. On the measurement, a rows page **can** exceed 2 s (9.6 s at 260 000 cells), and the route answers it with `200`.
On R1's text the rows route is therefore **not compliant** where a rows table can reach that size, and it can: the threshold is a
workspace-configurable setting (FR-232), and the measurement raised it. **What is not established is the size at or under the
default.** The rows page at 250 000 and at 100 000 cells is **unmeasured**; the 260 000 figure is above FR-232's default, taken
with the threshold raised, and the cost is not assumed to be linear. Entry 3 names exactly those runs as an S7 merge
condition (p99 at or under 2 s at 250 000 means S7 merges; over means a STOP before the mint), so this limb is **updated with the
250 000 and 100 000 figures when they exist**; until then the finding states the 260 000 figure with this caveat. *(Updated 2026-10-05, pre-mint: the figures exist; see the Amendment at the end.)* The verdict
that this is a breach, and of what, is the lead's and the maintainer's.

### Limb 2: the parquet page reloads and hashes both versions on every page

On the parquet path the page costs p50 948 / p99 1098 ms. Loading plus hashing both versions is 421 + 428 = 849 ms of the 948 ms p50,
about 90 % (the parts were timed in a separate loop from the whole requests, so the 90 % is a sum of components, not an in-request
profile; the remaining ~100 ms is unattributed: the stored-artifact read, `splitlines` over 260 000 lines and the cut). In code,
each request calls `_content_hash` for both versions (each loads the cells and hashes them), builds the artifact key from the two
hashes, then reads the stored artifact and cuts one page; nothing between requests keeps the hashes. This limb is under R1's 2 s
at 260 000 cells (p99 1.1 s) and over the maintainer's 1 s filing threshold; the maintainer's rule names the direction
(*"find the artifact without reloading"*) and a plan owns the design. This finding proposes none.

**Two readings to hold against the numbers:** (i) N = 10, so each p99 is the maximum (`measure_cells.py` `pct`: index
`round(0.99 × 9)` = 9); it names the worst of ten pages, not a tail estimate; (ii) the filing rule's 3× limb does not fire
(parquet p50 is 0.10× rows); the 1 s limb does, for both paths.

## Liveness: how large are the rate tables that exist? (read, with the predicate)

The question: is any committed or seeded rate table anywhere near 250 000 cells? **None found.** The reads, at
`a5657fa4520739f182cbea79e0057afeed991ac1`:

```
git ls-files examples            # six files: fremtpl2/{README.md,arff.py,fetch.py,model.py,seed.py,test_seed.py}
grep -n -i -E 'rate.?table|seed_from|relativit' examples/fremtpl2/seed.py   # no hit: the seed writes no rate table
grep -rn -i -E 'seed.from.model|seed_from_model|/rate-tables' --include=*.py --include=*.sh --include=*.md --include=*.json -l backend/src scripts examples frontend/src
```

The third read names only the service, its route, the contract generator and the audit script, **not** `backend/src/app/demo`,
`scripts/` seed code or `examples/`: the demo and the example seed create no rate table. Fixtures and benches: `scripts/bench-rating.py`
`_rate_table_payload` (line 181) is a two-row table (`channel`: `direct`, `broker`); the rate-table tests set the workspace
threshold to 2 or 1000 cells (`_set_threshold` in `backend/tests/test_rate_tables_service.py`, `test_api_rate_tables.py`,
`test_worker_rate_tables.py`) and `packages/pricing-core/tests/test_rate_table_bulk_ops.py:126` decides storage at thresholds of
100 000 and 300 000 as bare integers, with no table of that size built. **So no committed or seeded table is within three orders of
magnitude of 250 000; the exposure is a user's own table** (a multi-factor seed, `FD-1357`'s fix, or an import) near the threshold's
top. This read did not enumerate every test fixture's cell count: it is a search for any large table, and a large fixture
under a name the predicates miss is possible.

## Requirement context (searched across the NFR rows and the hard rules)

The earlier search, over the NFR rows alone, found no budget and missed R1. Run again at `a5657fa4…` over both forms:

```
grep -n -E '^\| \*\*NFR-[0-9]+\*\*' docs/specs/0[0-7]-*.md | grep -i -E 'diff|cells|page|pagina|cursor|list'
grep -n -i -E 'exceed(s|ing)? 2 ?s|slow is a Job|longer than 2 ?s|[^0-9]2 s[^a-z]' docs/specs/0[0-7]-*.md
grep -n -E '^> \*\*R[0-9]+ ' docs/specs/*.md
```

The first over all 83 NFR rows of `00` to `07` names no rate-table route. The second finds four lines: the two bounds above
(`07:36`, `00:534`), `06` NFR-520 (a filtered audit page < 2 s) and one line in `02` that is a measured table, not a requirement.
The third lists every hard rule; the only one on latency is `07` R1. **NFR-526** (`07:482`): *"API metadata reads p95 < 300 ms
(NFR-457); the scoring path is specified separately in `03` (NFR-489)."* NFR-471 (`01`, summary < 500 ms) and NFR-520 (`06`) are the
two precedents for a budget on a paged read; none is a rate-table budget. FR-232 says above the threshold "only the latency and
the status code differ", which says what a parquet version answers, and does not say a rows version may exceed R1.

## Evidence

Run 2026-10-05 20:45:27 to 20:49:46 BST at the head above (tree `1511ac46a4f5298a01cb65820bdcf559639b0046`), one gate-1 hold,
no check process running, load 1.01 at start, 0.92 at the GO, 1.29 at the end. The protocol and the raw output are kept in the
lead's local handover directory `handover/s7-measurement-2026-10-05/` (`measure2.out`, `measure_cells.py`, `run_measure.sh`,
`measure_inner.sh`); the raw output is quoted here, verbatim except that the `setup` timing lines, the memory table and the empty
`pgrep` blocks are omitted:

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

The rows block began at load 1.84 (the first line above carries it). An earlier run (18:56 BST: parquet p50 1024 ms, p99 1204 ms)
is recorded as **invalid** (load 7.2, no rows baseline) and is not used; this run is consistent with it.

## Disposition

*(Amended 2026-10-05, pre-mint, on the 22:25:03, 22:27:31 and 22:28:33 BST entries: discharged by S7 (SL-1391, WK-673) for both limbs, via RL-1442; severity HIGH, the conditional rule fired; see the Amendment at the end. The text below is as filed.)*

**Carry forward with an owner: WK-1178**, a follow-on slice (the maintainer's rule), **except** that entry 3 makes the rows page
at 250 000 and 100 000 cells a **merge condition on S7 (#1206)**, which is the measurement this finding is waiting for.

**Severity HIGH, provisional, LATENT today.** HIGH because the breached text is a numbered **hard rule** (`07` R1) and the route
is **new in S7**, so S7's own spec row answers a rows page `200` where R1 says an operation that can exceed 2 s returns `202`; the
rows path is the **normal** storage, 10× the parquet page, and 3.7 s of it is recomputed per page. LATENT because no committed or
seeded table is near the threshold (Liveness), and because the size at or under 250 000 cells is unmeasured: **if the 250 000-cell
rows p99 is at or under 2 s the rows limb falls to MEDIUM or below and the finding rests on the parquet limb** (entry 3 says the
same, and says severity is then proposed from the clean numbers). The parquet limb alone, at p99 1.1 s against R1's 2 s and a
1 s filing threshold, is MEDIUM. The acceptance a fix plan would carry is not set here: it needs the budget OQ-1440 asks for.
Companion: OQ-1440, the latency budget these routes should carry, for both paths.

## Amendment, 2026-10-05 (after 22:28:33 BST), pre-mint: HIGH, widened to the diff route, discharged by S7 for both limbs

Three entries of the maintainer (by delegation) in `to-lead.md` (a local channel file, cited by its header) change this finding.

**1. The merge-condition measurement exists, and R1 is breached at the default size.** The entry "2026-10-05 22:25:03 BST — S7 R1 STOP: (C) REFUSED (it does not comply); (A) with the IDENTITY key, INSIDE S7, by an RL first; FD 9487 widened to the diff route" accepts the measurement (rows at the default threshold; one quiet hold; raw output saved) and rules, verbatim:

> FD 9487: HIGH (by its conditional rule). Widen its scope: the DIFF route itself (FR-231, the pre-S7 route that S7 extends with weighting) also computes the full diff synchronously for a rows pair (diff_cells about 4 s at 250k). That is a breach ON MAIN today, not S7's. The FD records it with a measurement of the diff route at 250k in the same protocol, and its fix is FD 9487's fix slice under RL 9485 (or S7 if the same artifact path covers it at no extra write set; executor-s7 says which).

The runs, at S7's branch head `386f4d5485f6efa3fe2d9b05842d4f752d5d989d` (tree `1511ac46a4f5298a01cb65820bdcf559639b0046`), service level, N = 10 pages, limit 50, one gate-1 hold, 2026-10-05 22:12:36 to 22:23:33 BST, load 0.77 at start and 1.54 at end; raw output in the lead's local handover directory `handover/s7-measurement-2026-10-05/rows2.out`. The rows storage is at the default workspace threshold, so these are the sizes at and under FR-232's default that the finding above called unmeasured. Each p99 is the maximum of ten pages.

| Rows pair | cells | whole page p50 | whole page p99 | loading both versions p50 / p99 | `version_content_hash` x2 p50 / p99 | `diff_cells` alone p50 / p99 |
|---|---|---|---|---|---|---|
| unweighted | 250 000 | 9639 ms | 9848 ms | 5469 / 5710 ms | 382 / 414 ms | 3971 / 4188 ms |
| weighted (portfolio of 678 000 rows) | 250 000 | 12241 ms | **12434 ms** | 5680 / 5874 ms | 384 / 405 ms | 3822 / 3980 ms |
| unweighted | 100 000 | 4104 ms | 4265 ms | 2540 / 2744 ms | 150 / 153 ms | 1531 / 1661 ms |

The weighted run also times the portfolio read plus the `exposure_weights` join alone: p50 1568 / p99 1611 ms. The 260 000-cell figures above (rows p50 9604 / p99 9995 ms) agree with the 250 000-cell ones, so the cost is not far from linear in this range. **Severity is HIGH, and the conditional rule fired:** the rows page p99 at 250 000 cells is 12 434 ms (weighted) and 9848 ms (unweighted), against R1's 2 s, and 4265 ms even at 100 000 cells. The finding is no longer LATENT in the sense used above only for lack of a measurement; it stays latent in the data that exists (Liveness above is unchanged).

**2. Widened to the diff route.** The diff route itself (FR-231, `GET …/diff`) also computes the full diff synchronously for a rows pair. Measured at the literal `origin/main` head `52c153cd1dcf7eb8a716559216a30b245dd6a7e2` (tree `4fe99da0472c47845330aec9e7731ba3b06afc53`), one gate-1 hold, 2026-10-05 22:46:20 to 22:50:53 BST, load 2.60 at the start (1.86 when it settled) and 1.70 at the end, so not as quiet as the runs above; a 250 000-cell rows pair, unweighted, no cache; raw output in `handover/s7-measurement-2026-10-05/holdA.out`:

| Route | whole request p50 | whole request p99 | SQL load of both versions p50 / p99 | `diff_vs_previous` alone p50 / p99 |
|---|---|---|---|---|
| diff on `origin/main`, 250 000-cell rows pair | 9286 ms | **9633 ms** | 6696 / 7688 ms | 1825 / 1858 ms |

That is a breach on `main` today, not S7's, as the entry says: p99 9633 ms against R1's 2 s on a pair at FR-232's default size. The `diff_cells` computation alone is about 4 s on S7's branch (the table above).

**3. The discharger is S7 (SL-1391), for both limbs, via RL-1442.** The entry "2026-10-05 22:27:31 BST — S7: the write set ACCEPTED; the diff-route measurement on the branch ACCEPTED with the diff proof; the diff route goes INTO S7, option (a)", item 3, ends, verbatim:

> So RL 9484's brief EXTENDS to amend 03:904 (RL-1361 T10's diff row): a first diff request for a pair, rows or parquet, whose artifact is not yet stored answers 202 with the same Job; later requests answer 200 from it. RL 9484 covers 03:904, 03:933 and FR-232 together. S7's reds add: a first 250k rows diff request is 202, and a later diff request has p99 under 300 ms. FD 9487's diff-route limb is then DISCHARGED BY S7, named in the FD.

and the entry "2026-10-05 22:28:33 BST — S7 cost chain: CONFIRMED; the four-record batch mint AGREED" confirms, verbatim: *"no limb stays outside S7"* and *"FD 9487 names S7 as the discharger of both limbs (HIGH, with the 250k figures)."* This finding names it: **S7 (SL-1391, WK-673) discharges both limbs, the cells page (rows and parquet) and the diff route, by serving every page from one stored artifact keyed by immutable version identity (RL-1442), and meets the budget of RL-1441 (OQ-1440's decision).** The Disposition above ("a follow-on slice in WK-1178") is superseded in place by this.
