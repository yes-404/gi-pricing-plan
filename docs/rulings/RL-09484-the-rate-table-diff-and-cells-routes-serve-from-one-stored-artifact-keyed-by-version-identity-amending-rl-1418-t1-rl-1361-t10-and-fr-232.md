---
id: RL-9484
family: ruling
title: The rate-table diff and cells routes serve from one stored artifact, keyed by immutable version identity; the first request for a key may answer 202 on either storage (amends RL-1418 T1, RL-1361 T10 and FR-232)
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
relates: [WK-673, WK-1178, RL-1418, RL-1361, PL-1419, FR-231, FR-232, NFR-457]
---

# Ruling — the rate-table diff and cells routes serve from one stored artifact

**Decided by the maintainer, by delegation**, in six entries in
`~/gi-pricing-plan.local/channel/to-lead.md`. This record drafts the texts they name and
decides nothing beyond them.

**The entry headed *"2026-10-05 22:25:03 BST — S7 R1 STOP: (C) REFUSED (it does not
comply); (A) with the IDENTITY key, INSIDE S7, by an RL first; FD 9487 widened to the diff
route"*** (`:18852`), verbatim:

> (C) is REFUSED. By its own description, "the pages after the Job still reload and hash". At 250k that is the SQL load (p50 5.5 s) plus the hash (0.4 s) on EVERY later page, so the route would still breach R1 after the Job. It is not a stopgap; it moves the breach from the first page to every other page.
> DECISION: (A), INSIDE S7 (no merge of a route its own spec forbids):
> - Every cells page for a version pair is served from the stored artifact. The first request for a (versions, portfolio) key answers 202 with a Job (rows pairs too), and later pages read only their NDJSON slice.
> - THE KEY is IMMUTABLE VERSION IDENTITY ((slug, version) of each side, plus the portfolio Dataset Version id). A page finds its artifact WITHOUT loading or hashing any cells. NO migration. The content-hash twin sharing I accepted earlier (S7's twin-key test) is REVERSED: twins no longer share an artifact. That costs at most one extra Job per twin pair, never correctness. The twin test is rewritten to assert that identity keys are distinct and that each twin's artifact has identical content. A stored per-version hash is NOT added now; if twin sharing is ever wanted, that is a later optimisation with its own migration.
> - SPEC FIRST: ONE RL (a DM) amending RL-1418 T1 / 03:933 (the 202 condition becomes "where the query's cell artifact is not yet stored", for EITHER storage) and FR-232's "the editor pages without a job" (a dated amendment saying the FIRST request for a pair may answer 202; later pages do not). It cites R1, this entry, and the measurement file.
> - S7 records it as a plan deviation (a dispatch-record delta, since PL-1419 is frozen), with the write set extended to the artifact-keying code and its tests. It runs red-first: a 250k rows pair's FIRST request answers 202, and a later page at 250k has p99 under 300 ms (RL 9485's NFR, measured in the same protocol). It then RE-GATES.

Its other lines (the measurement accepted, the expected cost, FD 9487's widening, the lane B
batch) are not quoted; the next entry overtakes the FD 9487 line.

**The entry headed *"2026-10-05 22:27:31 BST — S7: the write set ACCEPTED; the diff-route
measurement on the branch ACCEPTED with the diff proof; the diff route goes INTO S7, option
(a)"*** (`:18869`), item 3, verbatim:

> 3. The diff route: option (a), INTO S7, overriding the recommendation, for one reason: S7 ADDS portfolio WEIGHTING to that route. At 250k the weighted rows request is about 12 s (the 22:12–22:23 measurement), and that WEIGHTED synchronous diff is NEW behaviour that S7 introduces. My 22:25:03 principle (a slice does not merge new code its own spec rule forbids) therefore reaches the diff route as well. Since the same stored-artifact path covers it with no new code paths (the summary is derived from the stored cells, with the two coverage figures as an artifact header line), the extra cost is about half a day on lane A, which is off G2's path.
>    So RL 9484's brief EXTENDS to amend 03:904 (RL-1361 T10's diff row): a first diff request for a pair, rows or parquet, whose artifact is not yet stored answers 202 with the same Job; later requests answer 200 from it. RL 9484 covers 03:904, 03:933 and FR-232 together. S7's reds add: a first 250k rows diff request is 202, and a later diff request has p99 under 300 ms. FD 9487's diff-route limb is then DISCHARGED BY S7, named in the FD.

**The entry headed *"2026-10-05 22:28:33 BST — S7 cost chain: CONFIRMED; the four-record
batch mint AGREED"*** (`:18876`), its first paragraph, verbatim:

> All of it is confirmed: no limb stays outside S7; S7 applies RL 9485 T1/T2 and must MEET its measured acceptance (p95 at or under 300 ms after the first request per key, n at least 100, quiet box, 250k rows AND 1M parquet, plus the 2x property against 10k on each path); RL 9485 "applied by" is re-pointed to SL-1391 pre-mint; FD 9487 names S7 as the discharger of both limbs (HIGH, with the 250k figures).

**The entry headed *"2026-10-05 22:31:11 BST — S7 flags: (1) async portfolio refusals
ACCEPTED, stated in RL 9484; (2) the unindexed lookup measured at a STATED Job count"***
(`:18881`), verbatim:

> 1. Content-dependent portfolio refusals arrive as the Job's FAILURE (VALIDATION_FAILED, with the count and example), and only 403/404/409 stay synchronous: ACCEPTED, no veto. It fits RL-1418 T1 ("A Job fails with the same codes"). RL 9484 states it and names the RL-1418 acceptance clause it changes ("reaches the 422's detail" becomes "reaches the Job failure's detail"). S7's tests assert the failure's code, count and example on the Job, and that NO portfolio value appears in it (NFR-499, as before).
> 2. The unindexed JobRow.parameters['key'] lookup: the combined measurement SEEDS the workspace with 10 000 completed rate_table.diff_cells Jobs of OTHER keys (a realistic upper bound for a pricing team's history, stated as such) and measures the page p95 with them present. If the p95 then exceeds 300 ms, or the lookup alone exceeds 50 ms, it comes back to me. My "no migration" excluded a stored-hash column; an INDEX migration for this lookup is NOT excluded, and I would rule on it on the numbers. Record the seeded count and the lookup's own time in the ledger either way.

**The entry headed *"2026-10-05 22:32:19 BST — S7 / RL 9484: all four asks ACCEPTED, with one precision each; the literal-main measurement decision upheld"*** (`:18886`), asks 1 to 3, verbatim:

> ASK 1, CHUNKED ARTIFACT: ACCEPTED. The Job writes content-addressed chunk blobs (about 1000 cells each) plus ONE manifest (the chunk shas, the total, the RateTableDiff summary with both coverage figures); a page reads the manifest plus the chunks its cursor range spans; the DIFF route reads only the manifest. RL 9484's T1' says "content-addressed chunk blobs and a manifest", naming RL-1418 T1's "one content-addressed blob" as the phrase it supersedes. PRECISION: a page with limit up to the chunk size touches at most 2 chunks. If the route's maximum limit exceeds the chunk size, the chunk size is set at least as large as that maximum, so the bound holds for every legal limit; the RL states the bound.
> ASK 2, WRITE SET WIDENING: ACCEPTED (behaviour edits in test_api_rate_tables.py and test_worker_rate_tables.py; no new path). PRECISION: the Job-kind change for the diff route's 202 (rate_table.diff → rate_table.diff_cells) is a WIRE change. T3' states it, and states that the kind rate_table.diff stays VALID in job.schema.json and the JobKind enum for existing Job rows (no enum value is removed; PostgreSQL could not drop it anyway), only no longer CREATED by this route. The contract check stays green.
> ASK 3, IN-FLIGHT: a request for a key whose Job is QUEUED or RUNNING gets THAT Job (its Location); no duplicate. PRECISION: a key whose latest Job FAILED is NOT cached as failed: the next request creates a NEW Job (the failure may have been transient), and the failed Job stays readable by its id. A key with a SUCCEEDED Job and a present artifact answers 200 from it. The RL states all three states.

Its ask 4 and its measurement decision bind S7's ledger, not a spec text, and are not quoted.

**The entry headed *"2026-10-05 22:36:21 BST — RL 9484 (#1225 @333b4971): (a) CONFIRMED; (b) relates: ACCEPTED, with an explicit sentence and a LOW tooling question; (c) synchronous 404 on both routes and storages"*** (`:18895`), verbatim:

> The resolved-against identity key (previous, seed and an explicit number naming one baseline share an artifact): ACCEPTED; it is the right reading of "immutable version identity".
> (a) CONFIRMED. RL-1361's own acceptance refusals (missing column, non-numeric banded column, negative or null exposure, zero match, the Banding error policy) become the Job's VALIDATION_FAILED on the diff route, by the same reasoning as my 22:31:11 entry for RL-1418's clause. RL 9484 names RL-1361's acceptance clause as changed, in those words.
> (b) ACCEPTED: corrects: RL-1418 and relates: RL-1361, plus ONE explicit sentence in RL 9484's body: "This record also changes RL-1361's acceptance clause '…each gives 422' (quoted in full); RL-1361 carries no back-reference because corrects: is single-id." The 03 text, which is living and governs, carries the change. A LOW tooling question for the register, not now: should corrects: allow a list? An auditor files it only if a second case arises; this one is recorded in RL 9484.
> (c) RULED: an unresolved factor_ref or banding_ref is a SYNCHRONOUS 404 NOT_FOUND BEFORE any Job, on BOTH routes and for BOTH storages, because resolving a ref reads no cell. RL 9484 states it, and states that it supersedes RL-1361's acceptance clause in which a dangling ref on parquet fails the Job with NOT_FOUND. The tests assert the 404 and that NO Job was created, for a rows and a parquet pair.
> Then ONE commit with the 22:32:19 items and these.

The entry headed *"2026-10-05 22:26:27 BST — No veto: S7 may write reds and code while RL
9484 is drafted"* (`:18865`) binds how the texts are applied: *"The 03 and FR-232 T-texts are
applied ONLY from the MINTED RL 9484, byte for byte, in the same commit as the code they
govern or a later one, never before the RL mints. S7 merges only after that. If RL 9484's
drafting changes any T-text the reds assume, the reds follow the RL, not the reverse."*

## How this was ruled

**Written 2026-10-05, from 22:27 BST, extended from 22:32 BST** on the lead's scope extension
(the brief's section "SCOPE EXTENSION, 22:27:45 BST") and two relayed items, **revised once
from 22:36 BST** on the brief's section "REVISION ORDER, 22:32:35 BST", and completed from
22:38 BST on the 22:36:21 entry, by the
decision-maker session `dm-rl9484`, on the lead's brief
`~/gi-pricing-plan.local/handover/brief-dm-rl9484-2026-10-05.md`. **Working id 9484 is the
lead's allocation.** Unminted records (RL 9485, OQ 9486, FD 9487) are cited in working-id
form and kept out of `relates:` (check 32). The mint replaces each with its minted id.

**Why `corrects:` names RL-1418 only.** `corrects:` holds one id, and the audit requires
each `corrected_by:` entry to be a record whose `corrects:` names that file
(`scripts/audit-docs.py:2416-2419` at `b6dd96fd`). RL-1418 is the record the 22:25:03 entry
names first. RL-1361 T10's row is amended here too (T3'), and RL-1361 is in `relates:`; its
front matter gains no entry. **This record also changes RL-1361's acceptance clause
*"… each gives 422 …"*, quoted in full in ruled item 7; RL-1361 carries no back-reference
because `corrects:` is single-id** (the 22:36:21 entry, (b)). The `03` text, which is living
and governs, carries the change. Whether `corrects:` should take a list is a LOW tooling
question the entry leaves to an auditor, filed only if a second case arises.

## Verified first

| Fact | Where, read at |
|---|---|
| R1: *"**R1 — Everything slow is a Job.** Any operation that can exceed 2 s returns `202` with a Job, has progress, is cancellable, and persists its result (FR-13, NFR-457)."* | `docs/specs/07-platform.md:36-37`, `origin/main` `b6dd96fd` |
| The cells row (RL-1418 T1, applied with the date `2026-10-05`) is `03:933`; its 202 clause answers 202 *"where either version is `storage: parquet` (FR-232) and the query's cell artifact is not yet stored"* and keys the blob *"like the diff's cache by both versions' content hashes and the portfolio's identity"*. On `origin/main` the row is absent: S7 has not merged | `docs/specs/03-rating-engine.md:933` at S7's head `386f4d5485f6efa3fe2d9b05842d4f752d5d989d` (#1206, re-read 22:32 BST); `grep -c 'diff/cells?against' docs/specs/03-rating-engine.md` gives 0 at `b6dd96fd` |
| The diff row with RL-1361 T10 applied is `03:932` at `386f4d54`. On `origin/main` the row is `03:904`, in its form before T10: *"**200** Cell-level diff with exposure weights (FR-231); **202** with a Job where either version is `storage: parquet` (FR-232)"* | `docs/specs/03-rating-engine.md:932` at `386f4d54`; `:904` at `b6dd96fd` |
| FR-232, the sentence amended: *"Rows are the default because they are what makes the rest of this section cheap: FR-231's cell diff is a SQL join, its exposure weighting is a join to the portfolio dataset, and the editor pages without a job."* The row has no dated amendment, and its bytes are identical at S7's head | `docs/specs/03-rating-engine.md:123`, at `b6dd96fd` and at `386f4d54` (a `diff` of the two rows printed nothing) |
| `MAX_LIMIT`, the route's largest `limit`, is the constant of that name | `backend/src/app/api/pagination.py:38` at `b6dd96fd`, by symbol |
| `rate_table.diff` is a member of `JobKind` and of the Job contract | `packages/model-schema/src/model_schema/jobs.py:55`; `docs/contracts/schemas/job.schema.json` (`grep -l '"rate_table.diff"'` lists it) at `b6dd96fd` |
| `against` is `previous`, `seed` or an explicit version number | `backend/src/app/api/rate_tables.py:64-74` (`_parse_against`) at `386f4d54` |
| The twin sharing reversed: `test_a_rows_version_and_its_parquet_twin_find_the_same_cells_artifact` | `backend/tests/test_rate_table_diff_portfolio.py:1172` at `386f4d54` |
| The RL-1418 acceptance clauses changed (item 7 below): *"A `FactorResolutionError` reaches the 422's detail with its count and example value; `WeightJoinError`'s own messages carry no value."* and *"**Portfolio refusals before anything else.** Each refusal of T1 is given on a rows table and on a parquet table, and the parquet case writes **no Job row**."* | `docs/rulings/RL-01418-*.md:318-319` and `:322-323` at `b6dd96fd` |
| The RL-1361 acceptance clauses changed (items 7 and 11 below): under **Refusals**, `:812-823`; under **The 202 path**, the dangling-ref clause, `:860-861` | `docs/rulings/RL-01361-*.md` at `b6dd96fd` |
| The measurement: rows storage at the default threshold, 250 000 cells with a portfolio, page p50 12241 ms, p99 12434 ms (n=10); without a portfolio p99 9848 ms; 100 000 cells p99 4265 ms. Head `386f4d54`, tree `1511ac46`, 22:12:36–22:23:33 BST | `~/gi-pricing-plan.local/handover/s7-measurement-2026-10-05/rows2.out`, sha256 `360b730703491e92b3ecfcca7aba5617868a855ccf7e05b849cf207f3237fc9b`, lines 9–33 |
| RL 9485's NFR: every page after the first request for a key, p95 ≤ 300 ms at `DEFAULT_LIMIT`, measured at n ≥ 100 at 250 000 cells (rows) and 1 000 000 (parquet); the first request for a key may answer 202 | RL 9485 (working id) T1, PR #1222 head `a3a90cbd`, open |
| FD 9487 (working id), the finding | PR #1223 head `8fc404a7`, open |

**Not verified here:** executor-s7's local commit `0ca852d8`, relayed by the lead as the
source of the async refusals. It is not on GitHub; the 22:31:11 entry is the authority this
record rests on.

## Ruled

1. **Every page of the cells route is read from the query's stored cell artifact**, on
   either storage. The first request for a key whose artifact is not yet stored answers
   **202** with a `rate_table.diff_cells` Job; rows pairs too. **The artifact is
   content-addressed chunk blobs and one manifest**: the chunks hold the changed cells in
   order, about 1000 cells each; the manifest holds the chunks' sha256s in order, the total,
   and the query's `RateTableDiff` with both coverage figures. A page reads the manifest and
   the chunks its cursor range spans. **The bound:** the chunk size is at least `MAX_LIMIT`,
   so a page touches at most two chunks for every legal `limit`. This supersedes RL-1418 T1's
   phrase *"as one content-addressed blob"*. Text T1'.
2. **The diff route is served from the same artifact.** A first diff request for a key
   whose artifact is not yet stored answers **202** with the same `rate_table.diff_cells`
   Job, rows or parquet; later requests answer **200** from the manifest's summary, reading
   no chunk. **The Job kind of the route's 202 changes from `rate_table.diff` to
   `rate_table.diff_cells`, a wire change.** `rate_table.diff` stays a valid kind in
   `job.schema.json` and `JobKind` for existing Job rows (no enum value is removed); this route
   no longer creates it. The maintainer's reason for the route: S7 adds portfolio
   weighting to it, a weighted 250 000-cell rows diff takes about 12 s synchronously, and
   that is new behaviour breaching R1. Text T3'.
3. **The key is immutable version identity**: the table `slug` and the `version` of each
   side, plus the portfolio Dataset Version's id (or no portfolio). `against` enters the key
   as the version it resolves to, so `previous`, `seed` and a number that name the same
   baseline share one artifact. A request finds its artifact without loading or hashing any
   cell. Versions are immutable, so a key never names two different cell sets.
4. **Twin sharing is reversed.** Two versions with identical cells no longer share an
   artifact. The maintainer's reason: *"That costs at most one extra Job per twin pair, never
   correctness."* S7's twin test is rewritten to assert that the identity keys are distinct
   and that each twin's artifact has identical content.
5. **No stored per-version content hash is added now.** Twin sharing, if wanted later, is
   *"a later optimisation with its own migration"*. **An index migration for the artifact
   lookup is not excluded**: S7 measures the lookup with 10 000 completed
   `rate_table.diff_cells` Jobs of other keys seeded, and a page p95 over 300 ms or a lookup
   over 50 ms goes back to the maintainer, who rules on the numbers (22:31:11, item 2).
6. **FR-232's "the editor pages without a job" is amended**: the first request for a key may
   answer 202, on either route; later requests do not. Text T2'.
7. **Content-dependent portfolio refusals arrive as the Job's failure.** The weights are
   computed in the Job, so a refusal that depends on the portfolio's content (a
   `WeightJoinError` or a `FactorResolutionError`) is the Job's failure, code
   `VALIDATION_FAILED`, its detail carrying the count and an example value and no portfolio
   value (NFR-499). Only the permission, scope and status refusals, **403**, **404** and
   **409**, stay in the first response. This changes acceptance clauses of two records:
   - **RL-1418**: *"A `FactorResolutionError` reaches the 422's detail with its count and
     example value"* becomes *"A `FactorResolutionError` reaches the Job failure's detail
     with its count and example value"*. *"**Portfolio refusals before anything else.** Each
     refusal of T1 …"* now covers the 403, 404 and 409 refusals only.
   - **RL-1361**, under **Refusals** (confirmed by the 22:36:21 entry, (a)), these clauses,
     in full:
     *"A missing same-named column, a missing source column, a non-numeric banded column, a negative exposure, and a portfolio that matches nothing: each gives 422 and names the column. With the zero-match refusal removed, a `None` mean comes back and the test fails."*;
     *"A Banding with `error` policy that meets an out-of-range value gives 422 and names the column."*;
     "*(New at the amending pass, audit F4.)* A null exposure value gives 422 and names the column and the null count. With nulls read as 0, a figure is served and the test fails.".
     Each refusal there that *"gives 422"* now fails the Job with `VALIDATION_FAILED` on the
     diff route, with the same naming. RL-1361 carries no back-reference (see "Why
     `corrects:` names RL-1418 only").
8. **The budget.** S7 applies RL 9485 (working id) T1 and T2 and meets its measured
   acceptance (22:28:33): p95 ≤ 300 ms for every request after the first for a key, n ≥ 100,
   a quiet box, at 250 000 cells rows and 1 000 000 parquet, plus the 2× property against
   10 000 on each path. S7's reds, from the entries: a first 250 000-cell rows request is
   202 on each route, and a later request has p99 under 300 ms in the protocol of
   `rows2.out` (n=10, `limit` 50, `OMP_NUM_THREADS=1`, state at both ends).
9. **FD 9487 (working id)** is the finding. **S7 discharges both its limbs**: the cells
   route and the diff route.
10. **The in-flight rule, three states of the key's latest Job.** Queued or running: a
    request answers **202** with that Job and its `Location`, and no second Job is made.
    Failed: the key is not cached as failed; the next request answers **202** with a new Job,
    and the failed Job stays readable by its id. Succeeded with its artifact present: **200**
    from the artifact. On both routes.

11. **An unresolved `factor_ref` or `banding_ref` is a synchronous 404 before any Job**,
    `NOT_FOUND`, on both routes and for both storages, because resolving a ref reads no cell
    (the 22:36:21 entry, (c)). This **supersedes** RL-1361's acceptance clause under **The
    202 path**:
    "*(New at the amending pass, audit F4.)* A dangling `factor_ref` or `banding_ref` on a parquet version fails the Job with `NOT_FOUND`, naming the key and the ref."
    The tests assert the 404 and that no Job was created, for a rows pair and a parquet pair.

## The exact texts

**Applied by S7 (SL-1391), from the minted record only**, byte for byte, in one commit with
the code they govern or a later one (the 22:26:27 entry). The placeholders are
`<Slice 7 date>` (the date of that commit) and `RL 9484` (the mint replaces it, in all three
texts and their backticks, with the minted `RL-` id). Nothing else is a placeholder.

### T1' — `03` §5.1, the cells row (amends RL-1418 T1)

Placement: the row of `03` §5.1 that begins
`` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff/cells?against= `` (`03:933` at
`386f4d54`; one row matches). The whole row is **replaced** by

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff/cells?against=&portfolio=&limit=&cursor=` | **200** One cursor page of the diff's changed cells (FR-231), `Page[RateTableDiffCell]` (§4.2), read from the query's stored cell artifact: every cell the diff's `changed_cells` counts, ordered by key tuple (§4.2), with each cell's baseline and current value, absolute and relative change, and its exposure weight when `portfolio` names a `validated` portfolio Dataset Version, weighted as the diff row states. The pages together hold every changed cell: a page bounds one response, not the cells. Requires `rating:read`. `limit` is 1 to `MAX_LIMIT`, default `DEFAULT_LIMIT` (`00` §5.2); `next_cursor` is null on the last page; `total_estimate` is the diff's `changed_cells`, counted up to `COUNT_CAP`. **202** with a `rate_table.diff_cells` Job and a `Location` header where the query's cell artifact is not yet stored, whatever `storage` either version has (FR-232, `07` §1.3 R1): the Job writes every changed cell, in order, as content-addressed chunk blobs of a fixed cell count no smaller than `MAX_LIMIT`, and one manifest holding the chunks' sha256s in order, the total, and the query's `RateTableDiff` with both coverage figures; the same request then answers **200** with pages read from them. A page reads the manifest and the chunks its cursor range spans, at most two for every legal `limit`. While the key's Job is queued or running, a request answers **202** with that Job and its `Location`, never a second Job; after it fails, the next request answers **202** with a new Job, and the failed Job stays readable by its id; after it succeeds, with its artifact present, **200**. The artifact is keyed by the query's immutable identity, the table `slug` and the `version` of each side, `against` taken as the version it resolves to, and the `portfolio` Dataset Version's id (or no portfolio), so a page finds it without loading or hashing any cell; two versions with identical cells do not share an artifact. An artifact that cannot be found is computed again, never served from another query. `against` and `portfolio` are checked as on the diff row, before any cell is read and before any Job, whatever `storage` either version has: **404** `NOT_FOUND` for an unknown table, version or `against`; with `portfolio`, **403** without `dataset:read`, the same for any id, **404** `NOT_FOUND` for a portfolio that is missing or in another workspace, **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio, and **404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve. The diff row's portfolio faults that depend on the portfolio's content are the Job's failure, `VALIDATION_FAILED`, never the first response. **400** `VALIDATION_FAILED` for a cursor this API did not issue or one past the last cell; **422** `VALIDATION_FAILED` for a `limit` out of range. A Job fails with the same codes. This route adds no field to `RateTableDiff`. (**added 2026-10-05, `RL-1418`, FD-1358; the 202 condition, the artifact, the key, the Job in flight, the ref 404 and the content faults amended <Slice 7 date>, `RL 9484`, FD 9487**) |
```

*What changes against the row at `386f4d54`*, and nothing else:
- `, read from the query's stored cell artifact` after the first `(§4.2)`;
- the 202 condition
  ``where either version is `storage: parquet` (FR-232) and the query's cell artifact is not yet stored``
  becomes
  ``where the query's cell artifact is not yet stored, whatever `storage` either version has (FR-232, `07` §1.3 R1)``;
- ``as one content-addressed blob keyed like the diff's cache by both versions' content hashes and the portfolio's identity, and the same request then answers **200** with pages read from it;``
  (RL-1418 T1's *"one content-addressed blob"*, superseded) becomes the chunks-and-manifest
  clause, the sentence on the two-chunk bound, the sentence on the Job in flight, and the
  sentence on the identity key and the twins; `an artifact that cannot be found` becomes
  `An artifact that cannot be found`, starting a sentence;
- `before any Job:` becomes ``before any Job, whatever `storage` either version has:``;
- ``, **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio, **404**``
  gains `and` before the last **404**, whose clause now ends the sentence; the clause
  ``, and **422** `VALIDATION_FAILED` for the diff row's portfolio faults`` is replaced by
  the sentence on content faults;
- ` and changes nothing on the diff row` is removed, since T3' changes that row;
- the marker gains `; the 202 condition, the artifact, the key, the Job in flight, the ref
  404 and the content faults amended <Slice 7 date>, `RL 9484`, FD 9487`.

### T3' — `03` §5.1, the diff row (amends RL-1361 T10)

Placement: the row of `03` §5.1 that begins
`` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against= `` (`03:932` at `386f4d54`,
RL-1361 T10's text; `03:904` at `b6dd96fd`, before T10; one row matches in each). The whole
row is **replaced** by

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=&portfolio=` | **200** Cell-level diff (FR-231), exposure-weighted when `portfolio` names a `validated` portfolio Dataset Version, with §4.2's coverage figures, read from the manifest of the query's stored cell artifact, the one the diff/cells row below pages, and no chunk; **202** with that row's `rate_table.diff_cells` Job and a `Location` header where the artifact is not yet stored, whatever `storage` either version has (FR-232, `07` §1.3 R1), the Job's parameters carrying `portfolio`; the same request then answers **200** from the manifest. The artifact is keyed, and a request during the key's Job answered, as on the diff/cells row, so a query's diff and its cells come from one Job. The 202's Job kind was `rate_table.diff` until <Slice 7 date>, a wire change: `rate_table.diff` stays a valid kind in `job.schema.json` and `JobKind` for existing Job rows, and this route no longer creates it. With `portfolio`, these are checked before the artifact is looked up and before any Job: **403** without `dataset:read`, the same for any id; **404** `NOT_FOUND` for a portfolio that is missing or in another workspace; **409** `DATASET_NOT_VALIDATED` for a `draft` or `archived` portfolio. **404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve, naming the key and the ref, also before any Job, whatever `storage` either version has, since resolving a ref reads no cell. A fault that depends on the portfolio's content is the Job's failure, never the first response: `VALIDATION_FAILED` naming the key, the column or the ref for an absent column, a non-numeric banded column, a resolution error, a null or negative exposure, or a portfolio that maps to no cell. A Job fails with the same codes (**amended 2026-10-05, `RL-1361`; the 202 condition, the artifact, the Job kind, the ref 404 and the content faults amended <Slice 7 date>, `RL 9484`, FD 9487**) |
```

*What changes against the row at `386f4d54`*, and nothing else:
- `, read from the manifest of the query's stored cell artifact, the one the diff/cells row
  below pages, and no chunk` after `§4.2's coverage figures`;
- ``**202** with a Job where either version is `storage: parquet` (FR-232), the Job's parameters carrying `portfolio`.``
  becomes the 202 clause on the artifact, followed by the sentence on the key and the Job in
  flight and the sentence on the wire change;
- `before the cache is read` becomes `before the artifact is looked up`;
- `naming the key and the ref` gains ``, also before any Job, whatever `storage` either version has, since resolving a ref reads no cell``;
- ``the ref; **422** `VALIDATION_FAILED` naming the key`` becomes
  ``the ref. A fault that depends on the portfolio's content is the Job's failure, never the first response: `VALIDATION_FAILED` naming the key``;
- the marker gains `; the 202 condition, the artifact, the Job kind, the ref 404 and the
  content faults amended <Slice 7 date>, `RL 9484`, FD 9487`.

**Predicate for T1' and T3'**, run from the repository root: `git diff --no-index
--word-diff=plain` of `git show 386f4d54:docs/specs/03-rating-engine.md | sed -n 933p` (T1')
and `sed -n 932p` (T3') against each block above printed only the changes listed.

### T2' — `03` FR-232 (the dated amendment)

Placement: the FR-232 row (`03:123` at `b6dd96fd` and at `386f4d54`). The text is
**appended** to the end of the second cell, after `only the latency and the status code
differ.` and one space, before the closing ` |`. Nothing is struck.

```text
**Amended <Slice 7 date> (`RL 9484`, FD 9487): the first request for a diff may answer 202, on either storage.** "The editor pages without a job" holds for every request to FR-231's diff and to its per-cell diff (`GET …/diff` and `GET …/diff/cells`, §5.1) after the first request for a key, the two versions and the `portfolio`: that first request may answer **202** with one `rate_table.diff_cells` Job, whatever `storage` either version has, because a weighted diff at the threshold exceeds `07` §1.3 R1's 2 s; later requests are read from the key's stored artifact and answer **200** without a Job.
```

## Acceptance — the violation that must become detectable

The violation: **a diff or cells request that loads or hashes the versions' cells after the
first, or a first request that computes the diff synchronously.** Each test is shown failing
on deliberately broken input. These amend the acceptance items of RL-1418 and RL-1361 named
in ruled item 7, RL-1418's "The 202 path" and the twin case; their other items stand.

- **Rows pairs answer 202 first, on both routes.** A 250 000-cell rows pair's first cells
  request and first diff request each answer 202 with a `rate_table.diff_cells` Job and a
  `Location`; after the Job succeeds, each answers 200. Red at `386f4d54`, which answers 200
  synchronously.
- **One Job per key.** After a diff request's Job succeeds, the cells request for the same
  key answers 200 with no new Job row, and the reverse.
- **The chunk bound.** Pages at `limit` 1 and at `MAX_LIMIT`, starting at a chunk's last
  cell, read at most two chunks; the diff route reads the manifest and no chunk. With the
  chunk size set below `MAX_LIMIT`, the first test fails.
- **The Job in flight.** A second request while the key's Job is queued, and again while it
  runs, answers 202 with the same Job id and writes no Job row. After a failed Job, the next
  request answers 202 with a new Job id, and the failed Job is still readable by its id.
- **The wire change.** The diff route's 202 Job has kind `rate_table.diff_cells`; an
  existing `rate_table.diff` Job row still validates against `job.schema.json` and reads
  back. With `rate_table.diff` removed from `JobKind`, the second test fails.
- **A request reads only the artifact.** A later request on either route does not load
  either version's cells nor compute a content hash: with the cell-load or the hash path
  made to raise, requests still answer 200.
- **The key.** `against=previous`, `against=seed` and the explicit number that resolve to
  one baseline find one artifact. The rewritten twin test: a rows version and its parquet
  twin give distinct keys, each answers 202 first, and the two artifacts' contents are
  identical.
- **Content faults fail the Job.** Each content-dependent refusal fails the Job with
  `VALIDATION_FAILED`; a `FactorResolutionError` reaches the Job failure's detail with its
  count and example value, and no portfolio value appears in the failure (NFR-499). The
  403, 404 and 409 refusals are given in the first response and write no Job row, on rows
  and on parquet.
- **The ref 404 before any Job.** An unresolved `factor_ref` and an unresolved
  `banding_ref` each answer 404 `NOT_FOUND` on both routes, for a rows pair and a parquet
  pair, and no Job row is written. With the ref check moved into the Job, the parquet case
  fails (ruled item 11).
- **The budget.** RL 9485's measured acceptance and the entries' p99 reds (ruled item 8).
  The lookup is measured with 10 000 seeded Jobs of other keys; the seeded count and the
  lookup's own time go in S7's ledger (ruled item 5).
- **No cross-query serving.** With the stored artifact removed, the request answers 202
  again, never another key's answer (RL-1418's item, kept).

## What it obliges

- **This commit:** this record only. No spec, `model-schema` or code file is edited.
- **S7 (SL-1391, #1206)**: records this as a plan deviation by a dispatch-record delta
  (PL-1419 is frozen and is not edited), with its write set extended to the artifact-keying
  code and its tests; runs red first; applies T1', T2' and T3' from the minted record, and
  RL 9485's T1 and T2; re-gates.
- **At the mint**: RL-1418's `corrected_by` gains this record's id; `RL 9484`, `RL 9485`,
  `OQ 9486` and `FD 9487` are replaced by their minted ids. The mint order is the 22:28:33
  entry's: FD 9487, then OQ 9486 with RL 9485, then this record, then S7.
- **FD 9487** names S7 as the discharger of both limbs (22:28:33). That is its own record's
  text, not this one's.

Drafted as working id 9484.
