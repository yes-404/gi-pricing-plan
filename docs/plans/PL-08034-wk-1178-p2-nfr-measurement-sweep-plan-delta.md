---
id: PL-8034
family: plan
kind: map
title: WK-1178 — the P2 NFR measurement sweep (NFR-468, NFR-470, NFR-485, NFR-1443 measured DIAGNOSTIC on the shared VM with pre-registered reading rules; NFR-472's red-first test): a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 8eaf6d5f9cd4204e1e077b44069d4afd395f1461
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-8035, RL-1441, FD-1439, LG-1444, SL-1391, SL-1259, PL-1620, RL-1614, CR-754, CR-721]
---

# PL-8034 — WK-1178, the P2 NFR measurement sweep: a dated Work-plan delta

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1667` and `PL-1682`, this delta `relates:` the records it
> builds on. It adds **one slice row**, `SL-8035`, under `### WK-1178` in
> [`../roadmap.md`](../roadmap.md).
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (Task 1's test is seen red **by its cause** before the fix), `python-test` (the `req`
> marker), `dev-commands` (its benchmark and load sections, `:887-901`; `uv sync
> --all-packages`; both gate halves), `close-workstream` (its "NFRs are measured, not
> asserted" step) and `git-hygiene`. The executor is spawned from `.claude/roles/executor.md`;
> a measurement task may be delegated to the `performance-engineer` agent
> (`.claude/agents/performance-engineer.md`), which gathers and decides nothing.

Filed under **working id 8034**; its slice row is **SL-8035** (`draft`, working id 8035). Both
ids were reserved by the lead in the brief that seated this planner (seat planner-nfrsweep).
Written 2026-10-14 by the planner. **Tree read:** `origin/main` at `8eaf6d5f` (committed
2026-10-14T11:25:34+01:00). Every `path:line` below is at that tree.

## Context — the ruling this delta records

The authority is the maintainer's (by delegation) entry in
`~/gi-pricing-plan.local/channel/to-lead.md` headed **"2026-10-14 11:06:52 BST — D-list
line-read RULED (35 ids; lineread-dlist-2026-10-14.md at ba68a6da) (re lead 11:06)"**, item 3,
verbatim:

> **3. P2-SCOPE, unmeasured or untested (NFR-468, 470, 472, 485, 1443): none is accepted as asserted.**
> - ONE WK-1178 slice "P2 NFR measurement sweep", before the code freeze, measuring each on the shared VM labelled DIAGNOSTIC with pre-registered thresholds and reading rules. Any that need a quiet host join nfr-bench-1's second session (WK-674 S5's) as named extra readings.
> - NFR-472 (the rule-set change audit) is a TEST gap, not a measurement: one red-first test in that slice, red by cause.
> - A reading that comes out OVER → an FD, not a re-wording.

The same entry's item 1 states the standard this plan applies to every extrapolation:
*"NFR-467 → PARTIAL-MEASUREMENT: 10M extrapolated from a 2M run (CR-721:93-97 [the entry writes the id padded; unpadded here per RFC-937 §1.1 rule 2]) is not a
measurement."* The lead received it in `from-lead-2026-10-09.md`, entry headed
**"2026-10-14 11:07:28 BST — Lead: RECEIVED the maintainer's (by delegation) 11:06:52 — LINE-READ
RULED: …"**, item (3): *"NFR-468/470/485/1443 → ONE WK-1178 P2 NFR measurement-sweep slice
(DIAGNOSTIC on the shared VM, pre-registered rules; quiet-host ones → nfr-bench-1 session 2;
NFR-472 a red-first test in it; OVER = an FD)."*

Three further constraints are cited to source:

- **G4** (`docs/roadmap.md:571-573`): *"Every P2 NFR is measured on the exit tree or carried
  with an owner"*; its 2026-09-29 amendment, quoting the maintainer: *"These verdicts are
  **measured, diagnostic** on the shared VM; the verdict is **carried**, owner the maintainer,
  discharge event **a dedicated host available**. No near-bound pass or fail is claimed from
  the shared VM."*
- **The code freeze** is *"Wed 2026-11-04"* (`docs/roadmap.md:588`); the ruling places this
  slice before it.
- **nfr-bench-1** is recorded only in the channel, not in the tree: to-lead **"2026-10-12
  09:21:07 BST — USER DECISION: the dedicated NFR VM is APPROVED. …"**: *"VM: nfr-bench-1,
  e2-standard-8, europe-west2-b, Debian 13, 50 GB pd-balanced"*, *"Sessions: SL-1455 Task 4
  (after Tasks 1–3 merge) and WK-674 S5 (after S4)"*, and *"a 3rd session needs a new
  approval"*; corrected by **"2026-10-12 09:23:56 BST — CORRECTION to 09:21:07: NO VM is created
  now. …"**: the VM is created only when a session is ready to run. An e2-standard-8 has 8
  vCPU and 32 GB. WK-674 S5 is `SL-1259` (`docs/roadmap.md:1144`), whose run list is in
  `RL-1614` and `PL-1620`; **none of this slice's NFRs is on it today.**
- **The shared VM** (this box): `nproc` 8, `free -g` total 31 GB, read 2026-10-14 by the
  planner. A measurement that needs more than about 20 GB cannot run here without starving the
  other seats.

## Goal

Each of NFR-468, NFR-470, NFR-485 and NFR-1443 gets one **committed** instrument, a
**pre-registered** threshold and reading rule committed before its first run, and one
recorded **DIAGNOSTIC** reading on the shared VM in the slice's `LG-`, with the load, the tree
and the size beside every figure. A reading that is near-bound (DP-1) or that needs a host
the shared VM cannot be (DP-4, DP-7) is written into the slice's ledger as a **named extra
reading** for nfr-bench-1's second session; this slice does not run it. A reading that comes
out OVER is reported to the lead for an `FD-` (the auditor files it) and the requirement's
text is not touched. NFR-472 gets one red-first test, red by its cause, and the fix that turns
it green.

## Scope and requirements, each id individually

| Id | Spec row at `8eaf6d5f` | Kind in this slice |
|---|---|---|
| NFR-468 | `docs/specs/01-data-management.md:1182` | measurement (latency) |
| NFR-470 | `docs/specs/01-data-management.md:1184` | measurement (bytes) |
| NFR-472 | `docs/specs/01-data-management.md:1186` | test gap: one red-first test + its fix |
| NFR-485 | `docs/specs/02-modelling.md:2952`, measurement note `:3131-3168` | measurement (peak memory) + a mechanism clause (DP-5) |
| NFR-1443 | `docs/specs/03-rating-engine.md:1518` | measurement (latency + a ratio) |

Read only, cited: NFR-457 (`00-overview.md:547`), `07` §1.3 R1 (`07-platform.md:36-37`),
NFR-467 (`01-data-management.md:1181`), NFR-475 and NFR-476 (the `02` measurement note),
FR-7, FR-51, FR-62, FR-231, FR-232. **No spec text changes in this slice.** A reading that
disagrees with a requirement is an `FD-`, never a re-wording (the ruling's third bullet).

## The five requirements — spec row, owning code, existing evidence, and the instrument

### NFR-468 — the one-way read

**Spec row, verbatim** (`01-data-management.md:1182`; no dated amendment):

> | **NFR-468** | A one-way summary read from a stored Profile returns in < 300 ms (NFR-457); it is never computed on request. |

NFR-457 (`00-overview.md:547`): *"Interactive UI: p95 < 300 ms for metadata reads; any
operation exceeding 2 s becomes a Job with progress."* So the bound is read as a **p95**.

**Owning code.** Route `GET /api/v1/dataset-versions/{version_id}/one-ways?column=`
(`backend/src/app/api/dataset_versions.py:58` prefix, `:277-293` handler `get_one_way`) →
`profile_service.one_way_of` (`backend/src/app/platform/profiles.py:114-135`) →
`latest_profile` (`:89-111`). `latest_profile` selects the newest `ProfileRow` and returns
`Profile.model_validate(row.body)` (`:111`): **every one-way read loads and validates the
whole stored profile**, every column's one-way, not one. The body is one JSONB column
(`backend/src/app/db/models.py:1131`). One one-way has at most `MAX_ONE_WAY_LEVELS = 200` rows
(`packages/pricing-core/src/pricing_core/data/profile.py:66`). Nothing is computed on request:
a missing column is a 404 (`profiles.py:129-135`).

**Existing evidence.** `backend/tests/test_data_nfrs.py:220`
`test_a_one_way_is_read_from_the_profile_not_recomputed` (`req("NFR-468")`) is structural: an
in-memory `profile_frame` → JSON → `model_validate_json` round trip, no database, no route, no
timing. `scripts/bench-data.py:282` times `Profile.model_validate_json(blob)` in memory, has
no budget for it (`BUDGETS`, `:54-59`), and scales it linearly by rows (`:291-295`), which is
wrong for a read whose cost does not follow row count. `CR-721`'s measured table has no
NFR-468 row. **No measurement exists.**

**Instrument (pre-registered).** `scripts/measure-p2-nfr-sweep.py one-way` (Task 2). The
route is called through the app, at the level DP-2 picks, against the migrated development
Postgres. **Corpus:** (i) the freMTPL2 prepared version from `examples/fremtpl2/seed.py`
(678 013 rows; its profile with every auto-selected one-way); (ii) a wide synthetic version, 80
columns × 1 000 000 rows from `scripts/bench-data.py`'s generator written to parquet and
ingested through the normal path, because the read's cost follows **profile size** (column
count, levels), not rows. The instrument prints the profile body's stored size
(`pg_column_size(body)`) beside each run. **n = 200** timed requests after 20 untimed warm-up
requests, columns cycled in a fixed order, one request at a time (closed loop).

**Never computed on request — the second clause.** During the timed run the harness replaces
`pricing_core.data.profile.profile_frame`, `profile_parquet` and `one_way` with a function
that raises; any call fails the run. This is possible only in-process (DP-2 (a)).

**Threshold and reading rule.** Nearest-rank p95 < **300 ms** at each corpus; p50, p95, p99,
max and n printed. Read by DP-1's bands. Quiet host: no, unless DP-1 places a reading in the
near-bound band.

### NFR-470 — storage overhead and deduplication

**Spec row, verbatim** (`01-data-management.md:1184`; no dated amendment):

> | **NFR-470** | Storage overhead of a Dataset Version is ≤ 1.2× the parquet payload; identical tables across versions are deduplicated by content hash (ID-4). |

ID-4 (`00-overview.md:290`): blobs are stored at `blob/{sha256}`; *"Identical content is
stored once."*

**Owning code.** Parquet is written with `write_parquet(buffer, compression="zstd")` and
`blob_store.put(...)` at three sites: `backend/src/app/data/ingestion.py:307-308`
(`_store_table`), `:452-453` (`correct_schema`), and
`backend/src/app/worker/data_handlers.py:427-428` (split/derive). `BlobStore.put`
(`backend/src/app/platform/blobs.py:140-189`) hashes the body (`:158`) and returns the
existing row when the digest is present (`:160`, `:171`). Other storage that exists because a
version exists: the `dataset_versions` row (JSONB `tables`, `totals`,
`source_fingerprint`; `models.py:833-845`), `ingestion_runs.reject_sample` (`:921`),
`validation_reports.body` (`:1031-1080`), `profiles.body` (`:1131`), its audit rows, and the
**uploaded source file**, which stays in the blob store (`data_handlers.py:127-136`).

**Existing evidence.** `backend/tests/test_data_nfrs.py:110`
`test_identical_tables_across_versions_are_stored_once` (`req("NFR-470")`) ingests one 3-line
CSV twice and asserts one `BlobRow` (`:136`, `:144`): the dedup clause at toy size. **No test
or record measures the 1.2× ratio.**

**Instrument (pre-registered).** `scripts/measure-p2-nfr-sweep.py storage` (Task 3). It seeds
freMTPL2's two versions (`examples/fremtpl2/seed.py`; README `:26-33`), then ingests the
**identical** source a second time as a third version, then queries:
- **payload** = Σ `blobs.bytes` over the version's `tables[*].blob` refs;
- **overhead** = Σ `pg_column_size(t.*)` over the version's rows in `dataset_versions`,
  `profiles`, `validation_reports`, `ingestion_runs` and `audit_events` (entity refs naming the
  version), plus the bytes of every blob the version references that is not a parquet table —
  the source upload counted per DP-3;
- **dedup** = the parquet blob bytes **new** with the third version (digests not present before
  it), expected 0.

Each figure is printed with and without the source upload, whatever DP-3 rules, so the ledger
carries both. Bytes do not change with load, so **no quiet host**; the seed is CPU-heavy, so it
runs under the gate-1 slot (Global Constraints).

**Threshold and reading rule.** Per DP-3. Dedup: new parquet bytes for the identical re-ingest
**= 0**; anything else is OVER.

### NFR-472 — the rule-set change audit (test gap)

**Spec row, verbatim** (`01-data-management.md:1186`; no dated amendment):

> | **NFR-472** | Audit: dataset transitions, acknowledgements, dictionary edits, rule-set changes, and purges each emit an Audit Event with before/after state (FR-7). |

**Owning code.** `PUT /api/v1/datasets/{slug}/rule-set` (`backend/src/app/api/validation.py:419-436`)
→ `replace_rule_set` (`backend/src/app/platform/validation_rules.py:801`), the only rule-set
mutation (`ValidationRuleSetRow(` is built only at `:857`). It computes the next version as
`1 + max(version)` (`:844-851`) and **never loads the previous version**; its
`audit.record(...)` (`:894-912`) passes `action="validation_rule_set.replaced"` and `after={…}`
and **no `before=`**, so `before` takes its default `None` (`backend/src/app/platform/audit.py:60`).
The other four limbs, for comparison: a dataset transition passes `before` and `after`
(`backend/src/app/platform/datasets.py:591-594`); an acknowledgement does
(`validation.py:326-329`); a dictionary edit does (`datasets.py:299-302`); a **purge passes
`after` only** (`datasets.py:1051-1055`) — see DP-6.

**Existing evidence.** `backend/tests/test_data_nfrs.py:147`
`test_every_dataset_transition_emits_an_audit_event_with_before_and_after` names rule-set
changes and purges in its docstring but asserts only the draft→validating event (`:179`). No
test asserts on `validation_rule_set.replaced`. `CR-721:129` claims the replacement *"writes
through `audit.record`"*: an event is emitted; its `before` is not.

**The red-first test and its cause** — Task 1.

### NFR-485 — fitting memory at 5 M × 60

**Spec row, verbatim** (`02-modelling.md:2952`):

> | **NFR-485** | Memory: fitting a 5 M × 60 dataset stays within 32 GB, using `QuantileDMatrix`/streaming construction rather than duplicating the design matrix. |

Its measurement note (`02-modelling.md:3131-3168`, dated 2026-08-22, WK-661), the parts that
bind here: *"NFR-475 and NFR-485 measured 2026-08-22 (WK-661) at four scales below the one they
state, and both are met by extrapolation rather than by measurement."*; *"Peak RSS | `m = 0.101
· n^0.777` (R² = 0.9960) | 3 516 MB | **16.0 GB** of 32 GB | **met**, at 50 %"*; *"Projected
**linearly** from the largest measured point instead, … peak RSS reaches **25.9 GB — 81 % of
NFR-485's budget**, on a machine that cannot hold it to check. **Memory is the clause that
fails first, and the one nothing here can falsify.**"*; *"none of this exercises the streaming
construction NFR-485 names — the curve above is the dense GLM design matrix, precisely the
path `QuantileDMatrix` does not apply to."* The owner it names: *"the slice that first has a
worker resembling the 16-core machine these three requirements name"*. `CR-754:162` carried it
the same way (*"Measured by extrapolation — 173 s of 600 s, 16.0 GB of 32 GB"*).

**Owning code.** XGBoost: a plain `xgb.DMatrix` (`packages/pricing-core/src/pricing_core/modelling/gbm.py:895`);
**no `QuantileDMatrix` anywhere under `packages/pricing-core/src`**. LightGBM:
`lgb.Dataset(..., free_raw_data=False)` (`gbm.py:1106-1108`), which keeps the raw array. GLM:
a hand-built dense one-hot `pl.DataFrame` (`modelling/glm.py:235-259`) turned into a dense
array, `x = design.to_numpy()` (`glm.py:578`). **The mechanism the clause names is not the
mechanism the code uses** — DP-5.

**Existing evidence.** `scripts/bench-model.py` (`--only glm|gbm|curve`, `--rows`,
`--factors` default `TARGET_FACTORS = 60` at `:95`, `--rounds` 500) measures peak RSS by a
20 ms `/proc/self/statm` sampler thread (`:111-147`); its `--only` help (`:814-816`) already
requires one phase per process for NFR-485. Its GBM arm is XGBoost; it has no LightGBM arm.

**Instrument (pre-registered).** `scripts/bench-model.py`, extended in Task 4 with
`--peak hwm`: at the end of the one phase a process runs, read `VmHWM` from
`/proc/self/status` (the kernel's own high-water mark for that process, no sampler) and print
it beside the existing statm peak. One phase per process (`dev-commands:887-889`). **Shared VM
(DIAGNOSTIC):** `--only glm` and `--only gbm` at 250 000, 500 000 and 1 000 000 rows × 60
factors, each in a fresh process, each preceded by a `MemAvailable` check that aborts below
8 GB. The power-law and the linear-from-largest projections to 5 M are printed and **labelled
projections; neither is read as a verdict** (the ruling's item 1 on NFR-467). **The stated
scale** (5 M × 60): per DP-4.

**Threshold and reading rule.** Peak `VmHWM` ≤ **32 GB** (32 × 2³⁰ bytes) at 5 M × 60, per
arm. On the shared VM: a measured peak is recorded; a projection is recorded and not read.
Quiet host: not for quietness (bytes are not slowed by load) but for **RAM** — DP-4.

### NFR-1443 — the cells-diff page

**Spec row, verbatim** (`03-rating-engine.md:1518`, including its dated addition):

> | **NFR-1443** | Rate-table cells-diff paging (`GET /api/v1/rate-tables/{slug}@{version}/diff/cells`, FR-231, FR-232), below `07` §1.3 R1 and NFR-457. **Budget:** every page after the first request for a key (the two versions and the `portfolio`) answers with **p95 ≤ 300 ms** at `limit` = `DEFAULT_LIMIT`, on both storage paths; the first request for a key may answer **202** with a Job under R1. **Measured, not asserted:** n ≥ 100 pages, on a quiet box, at **250 000 cells** with both versions `storage: rows` and at **1 000 000 cells** with both versions `storage: parquet`; each figure states its size, `limit`, percentile and n. **A page's cost is bounded by its `limit`, not by the table's cell count:** on each storage path, the page p95 at 250 000 cells is within **2×** of the page p95 at 10 000 cells at the same `limit`, both measured as above, with the workspace threshold (FR-232) set so that both versions take the path measured. *(Added 2026-10-05, RL-1441, deciding OQ-1440; FD-1439.)* |

`RL-1441` defines its quiet box as *"the gate slots free, no other heavy process"*
(`RL-1441` `:126-128`).

**Owning code.** Route `backend/src/app/api/rate_tables.py:463-513` (`against`, `portfolio`,
`limit` defaulting to `DEFAULT_LIMIT`, `cursor`) → `diff_cells_page`
(`backend/src/app/platform/rate_tables.py:715`), which pages over the stored artifact with an
integer offset cursor (`:747-758`) reading only the 1 000-cell chunks that cover the page
(`_read_cells`, `:656`; `CELLS_CHUNK = 1000`, `:560`). Storage matters only when the Job builds
the artifact (`_load_cells_of`, `:1224-1233`). `DEFAULT_LIMIT: Final = 50`
(`backend/src/app/api/pagination.py:37`). The FR-232 threshold is the setting
`rate_tables.cell_threshold`, default `250_000` (`backend/src/app/platform/settings.py:267-269`),
applied by `decide_storage_mode` (`packages/pricing-core/src/pricing_core/rate_tables/operations.py:696-700`,
`"parquet" if cell_count > threshold else "rows"`) when a version is written.

**Existing evidence.** `LG-1444` (SL-1391, WK-673) "Hold B", 2026-10-05, **service level, not
HTTP**, limit 50, N = 100 later pages, 10 000 other `diff_cells` Jobs seeded: page p95 rows
250 000 = 32.3 ms, parquet 1 000 000 = 37.0 ms; the 2× property rows 0.98×, parquet 1.03×.
Its settle deviation (later runs began at load 1.91–2.72) is ledgered, and the maintainer
accepted it (*"load only slows a measurement, so passing about 8x under the limit is
conservative"*, to-lead "2026-10-05 23:01:40 BST", as `LG-1444` quotes it). **Its harness was
scratch and is not in the repository** (`LG-1444`: *"the harness is scratch, not in the
repository"*). The 11:06:52 ruling lists NFR-1443 as unmeasured; this slice gives it a
committed harness at the route.

**Instrument (pre-registered).** `scripts/measure-p2-nfr-sweep.py cells-diff` (Task 5), at the
level DP-2 picks. Six runs, as `LG-1444` Hold B: rows 10 000, rows 250 000 (threshold at its
default), parquet 10 000 and parquet 250 000 (threshold set to 5 000 for both), parquet
1 000 000 (default threshold); each pair two versions of one table differing in every cell,
no `portfolio`; 10 000 completed `diff_cells` Jobs of other keys seeded first. Per run: the
first request asserted **202**, the Job run to completion and asserted **`succeeded` with its
artifact present** (not merely terminal), then **n = 100** later pages at `limit=50`, cursors
cycling through the artifact, one request at a time.

**Threshold and reading rule.** Each run's nearest-rank page p95 ≤ **300 ms**; on each path,
p95(250 000) ÷ p95(10 000) ≤ **2.0**. Read by DP-1's bands; the ratio has its own band because
contention can move it either way (DP-1). Quiet host: per DP-7.

## How an OVER reading is handled (every NFR)

An OVER reading is a fact the slice reports; the slice does not change the requirement or the
threshold.

1. The executor stops that NFR's runs (the other NFRs' runs go on), writes the reading into the
   `LG-` with its raw figures, load, tree and size, and sends the lead one line naming the NFR,
   the figure and the threshold.
2. **The lead routes it to the auditor, who files an `FD-`** (owner, severity and disposition
   are the auditor's and the lead's, never the planner's or the executor's). Under Lean P2 L3 a
   wrong-number class finding is an `FD-`, not a backlog row.
3. If the reading was taken on the shared VM, the slice's ledger also names it as an extra
   reading for nfr-bench-1's second session. That reading becomes evidence in the `FD-`, and it
   does not replace the `FD-`.
4. No spec text is edited in this slice, and no threshold is moved after a reading.

## Decision points

Kind, blocking status and resolver per `document-ids.md` §1.7. The planner rules none of them.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | What does "near-bound" mean on the shared VM, so that G4's "no near-bound pass or fail is claimed from the shared VM" can be pre-registered? | (a) a latency reading ≤ 50 % of its budget is a DIAGNOSTIC pass; 50–100 % is near-bound and becomes a named nfr-bench-1 extra reading; > 100 % is OVER. (b) The same three bands with the line at **1/2.3 ≈ 43 %**, the inverse of the contention factor measured on this box (`dev-commands:895-898`, "8.58 s at load 1.6 and 20.01 s at load 8.4"). (c) No band: every latency reading also gets a quiet-host reading. For the NFR-1443 ratio (either direction under load): ≤ 1.5 pass, 1.5–2.0 near-bound, > 2.0 OVER, under all three options | **(b)**: the line comes from a measured fact on this box, not a round number. Under (b) the `LG-1444` figures (≈ 12 % of budget) would need no quiet reading | decision point | yes — the thresholds are committed before the first run (Task 0) | |
| DP-2 | At what level are NFR-468 and NFR-1443 timed? | (a) **in-process ASGI**: `httpx.AsyncClient(transport=ASGITransport(app=create_app(...)))` (`backend/src/app/main.py:70`) against the migrated Postgres; it covers routing, auth, the DB and serialisation, not the socket, and allows NFR-468's "never computed" guard. (b) HTTP to a uvicorn process from the compose stack; it covers the socket too, needs a service, and cannot host the guard. (c) Service level, as `LG-1444` did; it misses routing and serialisation, so it is not the route the spec names | **(a)**. NFR-457 is a UI read on a local socket, where the socket costs well under a millisecond; (a) is the only option that tests both NFR-468 clauses in one run | decision point | yes — Tasks 2 and 5 are built on it | |
| DP-3 | What does NFR-470's "Storage overhead … ≤ 1.2× the parquet payload" compare, and does the retained source upload count? | (a) **total** stored bytes (payload + overhead) ≤ 1.2 × payload, that is overhead ≤ 20 %, with the source upload counted as overhead. (b) The same, without the source upload (it is ingestion input, not the version). (c) Overhead **alone** ≤ 1.2 × payload. Both figures, with and without the source upload, are printed under every option | **(a)**. "overhead … ≤ 1.2× the payload" read as a 20 % allowance is the only reading under which the clause bounds anything, and the source file is stored *because of* the version (`data_handlers.py:127-136`). This is a spec reading, so the resolver is the decision-maker's `RL-` | design unknown | yes — the reading rule is committed before the first run (Task 0) | |
| DP-4 | How is NFR-485 measured at its stated scale (5 M × 60, ≤ 32 GB), when neither host has more than 32 GB? | (a) Shared VM only: the curve to 1 M, DIAGNOSTIC; the verdict is **carried**, owner the maintainer, discharge event a host with more than 32 GB of RAM. (b) (a), **plus** a 5 M × 60 run per arm on nfr-bench-1's second session as a named extra reading, under a memory cap of 30 GB (`systemd-run --scope -p MemoryMax=30G`): a completed run's `VmHWM` is the measurement; a run killed at the cap is reported as "peak > 30 GB", and the lead routes it as an `FD-`. (c) Ask the user for a larger machine type for session 2 (for example 64 GB); a cost decision that is the user's | **(b)**. The spec note's linear projection (25.9 GB) fits inside the cap, so a real 5 M reading is likely possible on an 8-vCPU, 32 GB host; memory is not slowed by load. The extra time is about 30 min per arm (the note's 230 s GLM, 963 s GBM at 4 cores), and that time is session 2's to approve | decision point | yes — it changes nfr-bench-1 session 2's run list, which `RL-1614` owns | |
| DP-5 | NFR-485's mechanism clause names `QuantileDMatrix`/streaming construction; the code uses `xgb.DMatrix` (`gbm.py:895`), LightGBM keeps raw data (`gbm.py:1108`), and the GLM is dense (`glm.py:578`). Which one is wrong? | (a) The lead routes this disagreement now to the auditor as an `FD-`, for the decision-maker to rule code or spec (`CLAUDE.md` §0: *"When code and spec disagree, stop and resolve it"*); this slice measures the code as it stands and changes neither. (b) This slice switches XGBoost to `QuantileDMatrix`: scope the ruling did not give, and a change to every GBM fit before the freeze | **(a)** | fact | no — default (a); Task 4 measures the code as it stands either way | |
| DP-6 | The purge limb has the same gap as the rule-set limb (`datasets.py:1051-1055` passes `after` only), and `test_data_nfrs.py:147` names both in its docstring but asserts neither. Is it in this slice? | (a) No: the ruling says *"one red-first test"* for the rule-set audit; the lead routes the purge limb and the docstring as a finding. (b) Yes: a second red-first test and fix here | **(a)**; widening the ruled scope is not the planner's | scope | no — default (a) | |
| DP-7 | Does NFR-1443's "on a quiet box" require nfr-bench-1, or can the shared VM in an `RL-1441` quiet window ("the gate slots free, no other heavy process") satisfy it? | (a) The shared-VM reading, taken in an `RL-1441` quiet window with the load settled below 2.0 before each run, is the reading; it goes to nfr-bench-1 only if DP-1 places it near-bound or OVER. (b) It always joins nfr-bench-1 session 2 | **(a)**: `RL-1441` defined the quiet box on this box, and `LG-1444` measured at about 12 % of budget there | decision point | yes — it sets session 2's run list | |

## Write set

- Modify: `backend/src/app/platform/validation_rules.py` (`replace_rule_set`, `:801-913`).
- Modify: `backend/tests/test_api_datasets.py` (one new test after `:190`).
- Create: `scripts/measure-p2-nfr-sweep.py` (subcommands `one-way`, `storage`, `cells-diff`).
- Modify: `scripts/bench-model.py` (`--peak hwm`, Task 4).
- Create: the slice's `LG-` under `docs/ledgers/` (`docs/_templates/LG.md`).
- Modify: `docs/roadmap.md` — the slice's own closing lines only.

No spec, contract, migration or frontend file.

## Tasks

### Task 0: Preconditions and pre-registration

- [ ] **Step 1:** Confirm every blocking DP (DP-1, DP-2, DP-3, DP-4, DP-7) has a resolver id in this plan's table on `main`. If not, stop.
- [ ] **Step 2:** Write the thresholds and reading rules, as ruled, as module-level constants at the top of `scripts/measure-p2-nfr-sweep.py` (`THRESHOLDS_MS`, `NEAR_BOUND_FRACTION`, `RATIO_BANDS`, `NFR_470_RULE`) and in the `LG-`'s Scope section, quoting this plan's rows. Commit them **before any run**; the `LG-` cites that commit's sha as the pre-registration, and every run's start stamp must be later than that commit's `%aI`.
- [ ] **Step 3:** Each measurement session records at its start and end: `git rev-parse HEAD`, the tree, `nproc`, `free -m`, `/proc/loadavg`, `pgrep -af 'pytest|vitest|flock'`, and the state of both gate slots.

### Task 1: NFR-472 — the red-first test, then the fix

**Files:** Test: `backend/tests/test_api_datasets.py`. Modify: `backend/src/app/platform/validation_rules.py:894-912`.

- [ ] **Step 1: Write the failing test**, beside `test_replacing_the_dictionary_is_audited_with_before_and_after` (`:144-188`), using `test_a_rule_set_entry_carries_its_enabled_flag_and_override`'s fixtures and set-up (`:723-760`) and `_approved_rule` (`:687-721`). Mirror those tests; do not invent fixtures.

```python
@pytest.mark.req("NFR-472")
def test_replacing_a_rule_set_is_audited_with_before_and_after(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """NFR-472: a rule-set change carries the set it replaced, so "which rules were
    switched off, and when?" is answerable from the audit trail alone."""
    import asyncio

    from sqlalchemy import select

    from app.db.models import AuditEventRow

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal.id, workspace_id)
    approver = new_uuid7()
    asyncio.get_event_loop().run_until_complete(grant("approver", principal_id=approver))
    approver_headers = _headers(approver, workspace_id)

    slug = f"ds-{new_uuid7().hex[-8:]}"
    assert client.post(
        "/api/v1/datasets", json={"slug": slug, "name": "Rule-set audit"}, headers=headers
    ).status_code == 201
    kept = _approved_rule(client, headers, approver_headers, database)
    parked = _approved_rule(
        client, headers, approver_headers, database, layer="structural", check="not_null",
        params={"key_columns": ["policy_id"]},
    )

    first = client.put(
        f"/api/v1/datasets/{slug}/rule-set",
        json={"rules": [{"rule_id": kept}]},
        headers=headers,
    )
    assert first.status_code == 200, first.text
    second = client.put(
        f"/api/v1/datasets/{slug}/rule-set",
        json={"rules": [{"rule_id": kept}, {"rule_id": parked, "enabled": False}]},
        headers=headers,
    )
    assert second.status_code == 200, second.text

    async def events() -> dict[str, AuditEventRow]:
        async with database.session() as session:
            rows = (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == "validation_rule_set.replaced",
                    )
                )
            ).scalars().all()
            return {row.entity_ref: row for row in rows}

    by_ref = asyncio.get_event_loop().run_until_complete(events())
    v1 = by_ref[f"validation_rule_set:{slug}@1"]
    v2 = by_ref[f"validation_rule_set:{slug}@2"]
    # The set it replaced, in the same shape the earlier event wrote as its `after`.
    assert v2.before == v1.after
    assert v2.after["disabled"] == [parked]
    # The first version replaced nothing.
    assert v1.before is None
```

- [ ] **Step 2: Run it and see it red by its cause.**
Run: `uv run pytest backend/tests/test_api_datasets.py -k test_replacing_a_rule_set_is_audited_with_before_and_after -q`
Expected: the assertion `v2.before == v1.after` fails with **`None == {...}`** on its left side, because `replace_rule_set`'s `audit.record(...)` (`validation_rules.py:894-912`) passes no `before=`, so `before` is the default `None` (`audit.py:60`). A red for any other reason — a non-200 `PUT`, a `KeyError` on either entity ref, or an error in the set-up — is a plan or set-up defect: stop and report it, and do not touch product code.

- [ ] **Step 3: The minimal fix.** In `replace_rule_set`, load the previous version's row (`version - 1`, same `workspace_id` and `slug`) before the new row is added, and build both `before` and `after` with one helper from a stored body, so the two have one shape by construction:

```python
def _audit_state(version: int, body: Mapping[str, Any]) -> dict[str, Any]:
    """One rule-set version as NFR-472's audit state; `before` and `after` share it."""
    rules = body["rules"]
    return {
        "version": version,
        "rule_ids": [r["rule_id"] for r in rules],
        "disabled": [r["rule_id"] for r in rules if not r["enabled"]],
        "overridden": {
            r["rule_id"]: r["severity_override"]
            for r in rules
            if r["severity_override"] is not None
        },
    }
```

`after=_audit_state(version, row.body)`; `before=_audit_state(previous.version, previous.body)` when a previous row exists, else `None`. The `after` value must equal today's for the same input (same keys, same order of `rule_ids`, the same string forms): check by reading `:901-910` against the helper before running Step 4.

- [ ] **Step 4: Run it green**, then the module: `uv run pytest backend/tests/test_api_datasets.py -q` (one file, not the suite).
- [ ] **Step 5: Commit** — `fix(data): a rule-set replacement is audited with the set it replaced (NFR-472)`.

### Task 2: NFR-468 — the one-way instrument and its DIAGNOSTIC reading

**Files:** Create `scripts/measure-p2-nfr-sweep.py` (`one-way` subcommand).

- [ ] **Step 1:** Build the client at DP-2's level. For (a), construct the app with `create_app` (`backend/src/app/main.py:70`) and the settings the backend test fixtures use; mirror `backend/tests/conftest.py`, do not reinvent it.
- [ ] **Step 2:** Seed the two corpora (the NFR-468 section above); assert each version reaches `validated` with a stored profile, and print `pg_column_size(body)`.
- [ ] **Step 3:** Install the "never computed" guard (the three `pricing_core.data.profile` functions replaced by a raiser) for the timed phase only.
- [ ] **Step 4:** 20 warm-up requests, then n = 200 timed, each `time.perf_counter_ns()` around one awaited request, closed loop, one client. No profiler, no asyncio debug mode, no sampler or poller thread during the timed phase. Print p50/p95/p99/max (nearest rank), n, corpus, profile bytes, load before and after, CPU seconds.
- [ ] **Step 5:** Run it on the shared VM under the gate-1 slot, with the load settled below 2.0 immediately before the timed phase (printed). Record the reading, its DP-1 band, and the tree in the `LG-`. Commit.

### Task 3: NFR-470 — the storage instrument and its reading

**Files:** `scripts/measure-p2-nfr-sweep.py` (`storage` subcommand).

- [ ] **Step 1:** Seed freMTPL2's two versions with `examples/fremtpl2/seed.py`, then ingest the identical source again as a third version.
- [ ] **Step 2:** The byte accounting, as the NFR-470 section states, printed per version with and without the source upload; the third version's new parquet bytes printed separately.
- [ ] **Step 3:** Read by DP-3's rule; record in the `LG-`. Commit.

### Task 4: NFR-485 — the peak-memory instrument and the shared-VM curve

**Files:** Modify `scripts/bench-model.py`.

- [ ] **Step 1:** Add `--peak hwm`: after the one phase, read `VmHWM` from `/proc/self/status` and print it (MB and bytes) beside the existing statm peak. Abort before the phase if `MemAvailable` < 8 GB.
- [ ] **Step 2:** On the shared VM, under the gate-1 slot: `--only glm` and `--only gbm` at 250 000, 500 000 and 1 000 000 rows, `--factors 60`, each in its own process. Record each `VmHWM`, the two projections to 5 M, labelled "projection, not a reading".
- [ ] **Step 3:** Write the DP-4 extra reading for nfr-bench-1 session 2 into the `LG-` as a named item: the exact commands, the cap, and the reading rule. Commit.

### Task 5: NFR-1443 — the cells-diff instrument and its reading

**Files:** `scripts/measure-p2-nfr-sweep.py` (`cells-diff` subcommand).

- [ ] **Step 1:** The six runs as the NFR-1443 section states, the threshold set per run through the `rate_tables.cell_threshold` setting, and each version's `storage` asserted before timing.
- [ ] **Step 2:** For each run, assert that the first request returns 202 and that its Job is `succeeded` with its artifact present. Then time n = 100 later pages at `limit=50` under the same instrument rules as Task 2, Step 4.
- [ ] **Step 3:** Take the readings in an `RL-1441` quiet window on the shared VM, settling the load immediately before each run. Read them by DP-1 and DP-7, and record them in the `LG-`. Commit.

### Task 6: The gate, the ledger, the hand-off

- [ ] **Step 1:** Run both gate halves (`dev-commands`), through the gate-1 slot.
- [ ] **Step 2:** In the `LG-`, record one row per NFR: the reading, its band (pass-diagnostic, near-bound, or OVER), and its next step. The next step is "none", "nfr-bench-1 session 2 extra reading (named)", or "OVER, reported to the lead for an `FD-`".
- [ ] **Step 3:** Send the lead the list of named extra readings, so that session 2's run list can take them through `RL-1614`'s owner.

## Acceptance Standard

1. `uv run pytest backend/tests/test_api_datasets.py -k test_replacing_a_rule_set_is_audited_with_before_and_after -q` passes on the slice head. The `LG-` quotes the red run from before the fix. That run failed on `v2.before == v1.after` with `None` on its left side, and on no other line.
2. `git -C <wt> grep -n 'req("NFR-472")' backend/tests/test_api_datasets.py` lists the new test.
3. `git -C <wt> log --format='%h %aI %s' -- scripts/measure-p2-nfr-sweep.py` shows the pre-registration commit (Task 0, Step 2). It is older than every run start stamp in the `LG-`, and the constants it adds equal the ruled DP-1 and DP-3 values.
4. `uv run python scripts/measure-p2-nfr-sweep.py --help` lists `one-way`, `storage` and `cells-diff`. `uv run python scripts/bench-model.py --help` lists `--peak`.
5. The `LG-` has one reading row for each of NFR-468, NFR-470, NFR-485 and NFR-1443, each labelled DIAGNOSTIC. Each row carries its size or corpus, its n and percentile (latency), the tree, the load at start and end, and its band under DP-1.
6. Each OVER reading in the `LG-` has a matching line to the lead, sent at the time of the reading, that names the NFR, the figure and the threshold. No `docs/specs/` file is in `git -C <wt> diff --stat origin/main...HEAD`.
7. The NFR-485 projections in the `LG-` are labelled as projections, and no verdict is read from them.
8. Both gate halves exit 0 on the slice head, through the gate-1 slot.
9. `python3 scripts/audit-docs.py` prints no line that names this slice's files, except the working-id lines expected before the mint (checks 31, 32 and 39).

## Global Constraints

- **Pre-register before measuring** (the ruling's *"pre-registered thresholds and reading rules"*): no threshold, band or corpus is changed after a run has started. A change needs a new commit and a re-run, and the `LG-` records both.
- **Instruments do not saturate the event loop.** Use timers at request boundaries only. Do not use a profiler, asyncio debug mode, or a background poller during any timed latency phase. Memory is read from the kernel's `VmHWM` after the phase (`dev-commands:887-889`: one phase per process).
- **Quote the load with every number** (`dev-commands:900-901`). Report load and CPU demand together (`dev-commands:367-374`).
- **Runs are heavy and hold the gate-1 slot**, as `LG-1444` Hold B did. They never run beside another held slot or a timing benchmark (the planner charter's sweep-pause rule applies to every role).
- **A terminal state is not success.** Assert that a Job is `succeeded` and that its output is present.
- **No non-public data.** Use only freMTPL2 and synthetic data (`.claude/CLAUDE.md`). On nfr-bench-1, only synthetic data and freMTPL2 (to-lead "2026-10-12 09:21:07 BST").
- **Money is not touched.** No product code changes except Task 1's.

## Hand-off (not this plan's writes)

- The lead: a dated line on WK-1178's row that lists this delta, when it is accepted (the planner writes only the `SL-` row).
- The lead and the maintainer (by delegation): DP-1, DP-2, DP-3, DP-4 and DP-7 need resolvers. DP-3 is a spec reading, so it is the decision-maker's `RL-`. DP-4 and DP-7 change nfr-bench-1 session 2's run list (`RL-1614`).
- The auditor, through the lead: DP-5's spec-vs-code disagreement and DP-6's purge limb, if (a) is taken for each.

## Self-review

- **Coverage.** Each of the five ids in the ruling's item 3 has a section with its verbatim row, its owning code and its existing evidence. Each of the four measured NFRs has an instrument, a corpus, a pre-registered threshold and reading rule, and a quiet-host statement. NFR-472 has its red-first test, the red's cause, and its fix. "OVER → an FD" is one shared section.
- **Literals checked against `8eaf6d5f`.** These were checked: the route paths, `DEFAULT_LIMIT = 50`, `rate_tables.cell_threshold` at 250 000, `decide_storage_mode`, `replace_rule_set`'s `audit.record` call with no `before`, `audit.record`'s `before=None` default, `_approved_rule`'s signature, the PUT body shape (`rules`, `rule_id`, `enabled`), the action string `validation_rule_set.replaced` and its entity ref form, `create_app`, `TARGET_FACTORS = 60`, `xgb.DMatrix` at `gbm.py:895`, and `x = design.to_numpy()` at `glm.py:578`.
- **Not verified here.** `backend/tests/conftest.py`'s app and DSN fixtures (Task 2, Step 1 names that file as the authority). The `systemd-run` cap on nfr-bench-1 (DP-4 (b); the session's set-up seat checks it there).
- **No placeholders.** Each DP's resolver cell is empty because the planner rules none of them.
