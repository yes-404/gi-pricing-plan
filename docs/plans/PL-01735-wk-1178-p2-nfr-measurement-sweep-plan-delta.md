---
id: PL-1735
family: plan
kind: map
title: WK-1178 — the P2 NFR measurement sweep (NFR-467, NFR-468, NFR-470, NFR-485, NFR-1443 measured DIAGNOSTIC on the shared VM with pre-registered reading rules; NFR-472's red-first test): a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-16 # original date 2026-10-14, set at the draft; minted 2026-10-16
owner: planner
tree: 8eaf6d5f9cd4204e1e077b44069d4afd395f1461
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1736, RL-1441, FD-1439, LG-1444, SL-1391, SL-1259, PL-1620, RL-1614, CR-754, CR-721, LG-730, RL-1724]  # forward-cites kept out until their batch mints them: FD 8046, FD 8047
---

# PL-1735 — WK-1178, the P2 NFR measurement sweep: a dated Work-plan delta

*(Minted 2026-10-16 as PL-1735 and SL-1736 from working ids 8034 and 8035, in the P1 batch mint PR.)*

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1667` and `PL-1682`, this delta `relates:` the records it
> builds on. It adds **one slice row**, `SL-1736`, under `### WK-1178` in
> [`../roadmap.md`](../roadmap.md).
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (Task 1's test is seen red **by its cause** before the fix), `python-test` (the `req`
> marker), `dev-commands` (its benchmark and load sections, `:887-901`; `uv sync
> --all-packages`; both gate halves), `close-workstream` (its "NFRs are measured, not
> asserted" step), `spec-change` (Task 3's dated clarification on NFR-470's row, DP-3) and
> `git-hygiene`. The executor is spawned from `.claude/roles/executor.md`;
> a measurement task may be delegated to the `performance-engineer` agent
> (`.claude/agents/performance-engineer.md`), which gathers and decides nothing.

Filed under **working id 8034**; its slice row is **SL-1736** (`draft`, working id 8035). Both
ids were reserved by the lead in the brief that seated this planner (seat planner-nfrsweep).
Written 2026-10-14 by the planner. **Tree read:** `origin/main` at `8eaf6d5f` (committed
2026-10-14T11:25:34+01:00). Every `path:line` below is at that tree, unless a line says it
was read at `a3fc2e8d`.

**Amended 2026-10-14, before the mint, by the planner (seat planner-pl8034b), to the
decision-point rulings** of the maintainer's (by delegation) entry in
`~/gi-pricing-plan.local/channel/to-lead.md` headed **"2026-10-14 12:07:40 BST — PL 8034/SL 8035
(the P2 NFR sweep) DPs RULED (re lead 12:06:57)"**, read in full. Its seven DP items, verbatim:

> - **DP-1 → (b) 43% = 1/2.3**, on the MEASURED contention factor; cite where 2.3 was measured (run, date, tree) in the plan. A shared-VM reading within that band of its threshold is labelled NEAR-BOUND, not a verdict, and goes to a quiet host. Outside the band, the shared-VM reading stands as DIAGNOSTIC-PASS/OVER with that label.
> - **DP-2 → (a)** in-process ASGI + real Postgres, labelled "server-side, in-process, excludes network" in every reading. The NFR texts measured here are server-side.
> - **DP-3 → (b), WITHOUT the retained source upload.** 01 NFR-470 (:1184): "Storage overhead **of a Dataset Version** is ≤ 1.2× the parquet payload; identical tables across versions are deduplicated by content hash". The subject is the version's own storage (its tables + reports + profile vs its parquet payload). The source upload is the promotion Job's blob (RL 8028 O1), not the version's. Measure the dedup limb too (a second version with an identical table adds ~0 bytes for that table). **Write this reading as a dated clarification line on NFR-470 in SL-1736's commit** (spec text, citing this entry), so the pass/fail-deciding reading is in the spec, not only the plan. No RL is needed; this is a reading of the row's own subject.
> - **DP-4 → (b):** the 5M run per arm on nfr-bench-1 SESSION 2 under MemoryMax=30G; a cap-kill → an FD. It adds ≈ +30 min/arm to the APPROVED session 2 (not a third session, so within the user's 12 Oct VM approval). Record it as a dated line amending S5's run list (RL-1614), and include it in my 2 h VM heads-up. The 250k–1M curve on the shared VM is a DIAGNOSTIC projection, never a verdict.
> - **DP-5 → an FD, measure as-is:** NFR-485 names `QuantileDMatrix`/streaming, but the code uses `xgb.DMatrix` (gbm.py:895), LightGBM `free_raw_data=False` (gbm.py:1108) and a dense GLM (glm.py:578). Which side is wrong is the FD's §0 question. The 5M reading answers whether the gap matters.
> - **DP-6 → a finding:** the purge audit lacks `before` (datasets.py:1051-1055), and test_data_nfrs.py:147 claims coverage it does not assert (green by construction, today's class). One FD, both limbs; NFR-472's red-first test covers the replace_rule_set limb in SL-1736.
> - **DP-7 → (a)** an RL-1441 shared-VM quiet window, unless near-bound per DP-1.

Every task, reading rule and acceptance item below is made consistent with them; the options
no longer open are removed from the decision-point table.

DP-1 was then **amended** by the maintainer's (by delegation) entry headed **"2026-10-14
12:25:22 BST — PL-1735 DP-1 amended: (b) re-measure the contention factor on THIS box as Task 0,
with (a) as interim; 0.43 accepted as the conservative rounding (re lead 12:24:58)"**, read in
full; its two ruling items, verbatim:

> (i) **(b), plus (a) until it lands.** The 2.3 factor rests on ONE pair of readings (02:2981-2993, NFR-477 note, 2026-08-22, 4-core/16.4 GB; no run id or tree), and one run cannot establish a verdict. **Task 0 re-measures it on this box:**
> - one fixed benchmark (named, with its tree);
> - ≥ 3 ALONE/contended PAIRS, interleaved (ABAB), with load1 recorded at each start;
> - the factor = the MAX of the per-pair ratios (conservative; the spread printed);
> - the reading rule pre-registered before the first run.
> Because today's load swings with the user's catering work, record the contended runs' load. If a contended run sees load beyond the regime the sweep will run in, it is excluded and re-run, never kept. **The new band = 1 / measured-max-factor, rounded DOWN to 2 decimals.** Until Task 0 lands, the 0.43 band applies, cited with its provenance AND its limits.
> (ii) **NEAR_BOUND_FRACTION = 0.43: ACCEPTED** as the conservative rounding (it makes the near-bound zone slightly WIDER than 1/2.3 = 0.4348: 129 ms vs 130.4 ms on 300 ms). Say so in the plan.

Task 0 carries (i); the DP-1 row carries both.

**Amended 2026-10-14, before the mint, by the planner (seat planner-p1fix)**, on the
maintainer's (by delegation) entry headed **"2026-10-14 12:31:22 BST — Three planner choices
ruled; P1/P2 re-cut OK (re lead 12:30:55)"**, read in full. It **confirms** the two choices this
plan put to the lead (Self-review, "Readings put to the lead"), and the `SL-1259` line. Its two
PL-1735 items, verbatim, and the one sentence of its PL-1737 item that is this plan's:

> - **PL 8034 (a), the Task 0 regime: CONFIRMED.** ALONE = load1 < 1.0 at start; contended = load1 in [1.0, 2.0) at start and < 2.0 at end. The factor calibrates the load regime the sweep itself runs in (its settle ceiling 2.0), which is what the band is for. A contended run outside that regime is excluded and re-run (12:25:22). The provenance (8.58 s @ 1.6 vs 20.01 s @ 8.4, one pair, 4-core) is correctly stated.
> - **PL 8034 (b), NFR-470's counted overhead: CONFIRMED** = the version's tables + reports + profile; ingestion_runs and audit_events rows EXCLUDED and printed separately (they are platform records, not the version's storage).
> The S5 run-list amendment as a dated line under SL-1259's roadmap row (RL-1614/PL-1620 frozen): OK.

Its PL-1737 item is otherwise PL-1737's, and its P1/P2 item is the lead's.

**Amended again 2026-10-14, before the mint, by the planner (seat planner-p1fix)**, on the
maintainer's (by delegation) entry headed **"2026-10-14 12:42:55 BST — PL 8042 DP-S1 → (i) a
column on the run; PL-1735: NFR-467 MEASURED at 10M (re lead 12:42:23)"**, read in full. Its
item (2), verbatim (item (1) is PL-1737's):

> **(2) PL 8034 → ADD NFR-467's measurement, as you recommend.** My 11:06:52 classed it PARTIAL-MEASUREMENT ("10M extrapolated from a 2M run is not a measurement"), and 11:28:56 put it in the sweep. PL 8034 must carry its own instrument, the pre-registered threshold from NFR-467's text, a task and an acceptance item, measured at 10M. If the shared VM cannot hold it, it goes to nfr-bench-1 session 2 with NFR-485's 5M runs. **Restate session 2's total planned duration** in the plan (5M × arms + NFR-467 at 10M + S5's own list), because my 2 h VM heads-up to the user must carry a true duration and cost. If it now exceeds ~6 h, tell me before it is committed.

It is carried by: the Goal; the scope table (NFR-467 moves out of the read-only list); the new
NFR-467 section (instrument, threshold from the row and its 2026-08-14 amendment, host and
sizing); Task 5a; Acceptance 10; "nfr-bench-1 session 2 — the total planned duration"; the
write set; the Hand-off; and the Self-review. The dated lines that
record the three confirmations are at Task 0 Step 2, the NFR-470 section, DP-3, Task 3 Step 2,
Task 4 Step 4, the write set and the Self-review.

**Corrected 2026-10-16, before the mint, by the planner (seat planner-p1b)**, on the lead's
brief of 2026-10-16 item 1. `FD 8046` and `FD 8047` moved from the D17 docs batch to D18 (D17's
commit `965e86a4`, "docs(findings): move FD 8040, 8046, 8047 to D18"); they are on
`origin/docs-d18-2026-10-14` @`b1ecf56d`. Scope, DP-5, DP-6 and the Hand-off now say D18. Task 0
Step 1 now says the plan merges before D18 (mint order P1 → D18 → P2, the maintainer's (by
delegation) entry "2026-10-16 09:40:20 BST"); what the step requires is unchanged.

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
  `RL-1614` and `PL-1620`; **none of this slice's NFRs is on it today.** Under DP-4 (b) the
  NFR-485 5 M runs join session 2 (Task 4, Step 4, the dated line that adds them).
- **The shared VM** (this box): `nproc` 8, `free -g` total 31 GB, read 2026-10-14 by the
  planner. A measurement that needs more than about 20 GB cannot run here without starving the
  other seats.

## Goal

Each of NFR-467, NFR-468, NFR-470, NFR-485 and NFR-1443 gets one **committed** instrument, a
**pre-registered** threshold and reading rule committed before its first run, and one
recorded **DIAGNOSTIC** reading on the shared VM in the slice's `LG-`, with the load, the tree
and the size beside every figure, and every latency reading labelled **"server-side,
in-process, excludes network"** (DP-2). A latency reading in the NEAR-BOUND band (DP-1) and
NFR-485 at its stated 5 M scale (DP-4) are written into the slice's ledger as **named extra
readings** for nfr-bench-1's second session; this slice does not run them. NFR-467 is measured
**at its stated 10 M rows** on the shared VM, never extrapolated (the 12:42:55 entry). A reading that comes
out OVER is reported to the lead for an `FD-` (the auditor files it) and the requirement's
text is not touched. NFR-470's pass/fail-deciding reading is written into the spec as one dated
clarification on its row (DP-3). NFR-472 gets one red-first test, red by its cause, and the fix
that turns it green.

## Scope and requirements, each id individually

| Id | Spec row at `8eaf6d5f` | Kind in this slice |
|---|---|---|
| NFR-467 | `docs/specs/01-data-management.md:1181`, amendment note `:1190-1207` | measurement at 10 M rows (time + memory scaling); added 2026-10-14 by the 12:42:55 entry |
| NFR-468 | `docs/specs/01-data-management.md:1182` | measurement (latency) |
| NFR-470 | `docs/specs/01-data-management.md:1184` | measurement (bytes) |
| NFR-472 | `docs/specs/01-data-management.md:1186` | test gap: one red-first test + its fix |
| NFR-485 | `docs/specs/02-modelling.md:2952`, measurement note `:3131-3168` | measurement (peak memory) + a mechanism clause (DP-5) |
| NFR-1443 | `docs/specs/03-rating-engine.md:1518` | measurement (latency + a ratio) |

Read only, cited: NFR-457 (`00-overview.md:547`), `07` §1.3 R1 (`07-platform.md:36-37`),
NFR-475 and NFR-476 (the `02` measurement note), FR-7, FR-51, FR-62, FR-231, FR-232.

*(Dated 2026-10-14 by the planner, seat planner-p1fix, before the mint: the citation the sweep
finds by stamp.)* The maintainer's (by delegation) entry headed **"2026-10-14 11:28:56 BST —
FD 8027 severity → HIGH (the max of its limbs), per-limb table kept; the FR-127 GLM limb may
touch G2: CHECK NOW (re lead 11:28:22)"** (FD-1723's ruling, in `to-lead.md`, read in full)
says, in its LOW-limbs line, verbatim: *"**LOW limbs:** fixed in P2 where small (FR-33, 80,
123, NFR-467's measurement joins the P2 NFR sweep); else carried with owner at §14."* When this
line was first written the plan carried NFR-467 read-only, and the difference was reported to
the lead; the 12:42:55 entry, item (2), then **added NFR-467's measurement at 10 M** (Context),
and the scope table above carries it.

**One spec edit only:** the dated clarification on
NFR-470's row that DP-3 orders (Task 3, Step 4); it records how the row is read and changes
neither its subject nor its 1.2× bound. A reading that disagrees with a requirement is an
`FD-`, never a re-wording (the ruling's third bullet). Two findings already filed from this
plan's reading, both working ids in the D18 docs batch (`origin/docs-d18-2026-10-14` @`b1ecf56d`,
not yet on `main`; moved there from D17 by D17's commit `965e86a4`): **`FD 8046`** (DP-5: NFR-485's construction clause against the code) and
**`FD 8047`** (DP-6: the purge audit's missing `before`, and `test_data_nfrs.py:147`'s
docstring claiming coverage it does not assert).

## The six requirements — spec row, owning code, existing evidence, and the instrument

### NFR-467 — profiling a 10 M-row version (added 2026-10-14, the 12:42:55 entry)

**Spec row, verbatim** (`01-data-management.md:1181` at `a3fc2e8d`, unchanged since `8eaf6d5f`):

> | **NFR-467** | Profiling a 10 M-row version completes in ≤ 5 min, and its memory **does not scale with row count**: every statistic is aggregated in DuckDB and only aggregates are materialised (see the note below). |

**Its dated amendment, verbatim** (`:1190-1207`, the note the row's "see the note below" names; no
later amendment):

> **NFR-467 amended 2026-08-14.** It previously bounded profiling memory at "2× the
> largest column's compressed size". That number is not achievable and was never the
> property worth requiring. Measured on the WK-660 benchmark (`scripts/bench-data.py`), 80
> columns × 2 M rows: the largest compressed column is 15.4 MB, so the old bound was
> 30.7 MB — while a Python process with `polars`, `duckdb`, `scipy` and `pydantic`
> imported occupies 140 MB before it has read a byte. The bound counted the interpreter
> against the dataset.
>
> The property that actually protects the platform is that profiling does not hold the
> data, and that *is* measurable: over a 10× increase in payload (109 MB → 1,092 MB),
> peak RSS above the import baseline moved 113 MB → 236 MB. Sub-linear, so a 10 M-row
> version does not need 10 M rows' worth of memory.
>
> The requirement was met in intent and missed in fact by the first implementation, which
> ran `SELECT *` and handed the frame to the in-memory profiler — 2,278 MB peak on that
> same 1,092 MB payload, and roughly 11 GB at the scale the requirement is written
> against. The parenthetical "DuckDB streaming, not full materialisation" was already in
> the spec; the code did not do it, and no test asked.

**Owning code.** `pricing_core.data.profile.profile_parquet`, which aggregates in DuckDB (the
amendment's fix). **Existing evidence: a partial measurement.** `CR-721`'s NFR table
(`docs/closures/CR-00721-wk-660-data-workbench-closed.md:85-98` at `a3fc2e8d`) records
*"NFR-467 profiling | 91.7 s | 300 s"* and the memory line *"113 MB → 236 MB above baseline
over a 10× payload increase"*, both from `scripts/bench-data.py` *"at 2 M rows × 80 columns,
extrapolated to 10 M"*. The 11:06:52 entry, item 1, classes it **PARTIAL-MEASUREMENT** (*"10M
extrapolated from a 2M run … is not a measurement"*).

**Instrument (pre-registered).** `scripts/measure-p2-nfr-sweep.py profile` (Task 5a). For each
of two sizes, **2 000 000 and 10 000 000 rows × 80 columns**:
1. generate the synthetic parquet in its own process with the existing generator,
   `uv run python scripts/bench-data.py --rows N --generate-to <path>` (`bench-data.py:166-173`,
   `:186-191`; the file goes under the executor's job tmp directory, never `/tmp`, and is
   deleted after its run);
2. profile it in a **fresh** process that never held the data (the reason `bench-data.py`
   gives at `:169-173`): read `VmRSS` after the imports as the **baseline**, call
   `profile_parquet` exactly as `bench-data.py:196-198` does, time the call with
   `time.perf_counter()` at its boundaries, then read `VmHWM` (one phase per process,
   `dev-commands:887-889`; no sampler thread, which the Global Constraints bar). It prints
   wall seconds, `VmHWM`, the baseline, **Δpeak = VmHWM − baseline**, the payload bytes, the
   load at start and end, and the tree.

**Threshold and reading rule (pre-registered, from the row and its amendment).**
- **Time:** the 10 M profile's wall time **≤ 300 s** (*"completes in ≤ 5 min"*), read by DP-1's
  bands as every latency reading is: ≤ `NEAR_BOUND_FRACTION` × 300 s (129 s at the interim 0.43)
  is DIAGNOSTIC-PASS; above it and ≤ 300 s is NEAR-BOUND, a named nfr-bench-1 session 2 extra
  reading; > 300 s is DIAGNOSTIC-OVER, an `FD-`.
- **Memory:** *"does not scale with row count"*, read as the amendment reads it, *"Sub-linear,
  so a 10 M-row version does not need 10 M rows' worth of memory"*: **r = Δpeak(10 M) ÷
  Δpeak(2 M) < 5.0**, the row ratio. r ≥ 5.0 (linear or worse) is DIAGNOSTIC-OVER, an `FD-`.
  The row gives no tighter number, so none is invented here; r and both Δpeaks are printed.
  **DERIVED, not specified:** 5.0 is the planner's literal reading of "sub-linear", not a number
  the row states. *(Ruled 2026-10-14 by the maintainer's (by delegation) entry "2026-10-14 13:21:41 BST — MERGE-ACK #1302 (D15) + eight pending rulings (re lead 12:46:13 → 13:15:54)", verbatim: **PL 8034 (b) NFR-467's memory threshold: ACCEPT r < 5.0** as the literal reading of "sub-linear" (the row gives no number; a stricter bound would invent one). Pre-registered as the planner wrote, with the reading flagged as derived, not specified.)* The executor
  records the reading in the `LG-` with the same flag: "derived from 'sub-linear', ruled
  13:21:41".
  Memory does not change with load, so this limb is a reading, not a diagnostic of load.
- The aggregation clause (*"every statistic is aggregated in DuckDB and only aggregates are
  materialised"*) is the mechanism the memory limb tests; it gets no separate check.

**Host and sizing: the shared VM**, as the 12:42:55 entry allows when it can hold the run.
Sizing, at this plan's reading on 2026-10-14: the box has 8 vCPU and 31 GB, `MemAvailable`
read 18 GB and `/` had 15 GB free. The 10 M parquet is about **5.5 GB** (the amendment's 1,092 MB
at 2 M, × 5). Generation holds 80 numeric columns at 10 M rows, **6.4 GB** resident by
`bench-data.py`'s own docstring (`:11-13`), plus transients: about **8–13 GB peak** in the
generating process, which exits before profiling. The profiling process is sub-linear by the
amendment's own reading (236 MB above baseline at 2 M), well under 2 GB. So the run fits, with
two guards checked before generating and recorded: **`MemAvailable` ≥ 16 GB** and **free disk
under the job tmp ≥ 12 GB**. If either guard fails, the run waits and re-checks; if it cannot
run on the shared VM before Task 6, it moves to nfr-bench-1 session 2 (e2-standard-8, 32 GB,
50 GB disk, the VM brief) as a named run, and the session-2 total below already allows for it.
The profile is CPU-heavy (DuckDB uses every core), so it runs under the gate-1 slot with the
load settled below 2.0 at its start, like Tasks 2 and 5.


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
route is called through the app **in-process** (DP-2 (a): `httpx.AsyncClient` over
`ASGITransport(app=create_app(...))`) against the migrated development Postgres, and every
figure is labelled **"server-side, in-process, excludes network"**. **Corpus:** (i) the freMTPL2 prepared version from `examples/fremtpl2/seed.py`
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
max and n printed. Read by DP-1's bands (the decision-point table): p95 ≤ 129 ms is
DIAGNOSTIC-PASS, 129 ms < p95 ≤ 300 ms is NEAR-BOUND, p95 > 300 ms is DIAGNOSTIC-OVER. Quiet
host: only a NEAR-BOUND reading, as a named nfr-bench-1 session 2 extra reading.

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
`validation_reports.body` (`:1031-1080`), `profiles.body` (`:1131`) and its audit rows. The
**uploaded source file** also stays in the blob store (`data_handlers.py:127-136`), but it is
**not the version's storage**: it is the promotion Job's blob (RL-1724 DP-U1.1, O1, read as working id
`RL 8028` on `origin/rl-8028-upload-completion-2026-10-14` @`a8e1191a`; minted in D17, #1307), and DP-3 (b) excludes
it.

**Existing evidence.** `backend/tests/test_data_nfrs.py:110`
`test_identical_tables_across_versions_are_stored_once` (`req("NFR-470")`) ingests one 3-line
CSV twice and asserts one `BlobRow` (`:136`, `:144`): the dedup clause at toy size. **No test
or record measures the 1.2× ratio.**

**Instrument (pre-registered).** `scripts/measure-p2-nfr-sweep.py storage` (Task 3). It seeds
freMTPL2's two versions (`examples/fremtpl2/seed.py`; README `:26-33`), then ingests the
**identical** source a second time as a third version, then queries:
- **payload** = Σ `blobs.bytes` over the version's `tables[*].blob` refs;
- **overhead** = Σ `pg_column_size(t.*)` over the version's own rows, the ruling's *"its
  tables + reports + profile"*: its `dataset_versions` row, its `validation_reports` rows and its
  `profiles` rows, plus the bytes of every blob the version references that is neither a parquet
  table nor the uploaded source file. **Not counted, each printed on its own line labelled
  "excluded" so the ledger shows what was left out:** the source upload (DP-3 (b): *"the
  promotion Job's blob (RL 8028 O1), not the version's"*), and the `ingestion_runs` and
  `audit_events` rows naming the version (records of the ingestion Job and the audit trail, not
  the version's storage under the ruling's enumeration). *(Confirmed 2026-10-14 by the
  maintainer (by delegation), entry "2026-10-14 12:31:22 BST", PL-1735 (b): the counted
  overhead is the version's tables + reports + profile; the `ingestion_runs` and
  `audit_events` rows are excluded and printed separately, as platform records, not the
  version's storage.)*
- **dedup** = the parquet blob bytes **new** with the third version (digests not present before
  it), for the table identical to an earlier version's.

Bytes do not change with load, so **no quiet host**; the seed is CPU-heavy, so it runs under
the gate-1 slot (Global Constraints).

**Threshold and reading rule (DP-3 (b), ruled).** Per version: **(payload + overhead) ÷ payload
≤ 1.2**, the source upload excluded; above 1.2 is DIAGNOSTIC-OVER. Dedup limb: the third
version's new parquet bytes for its identical table **= 0** (the ruling's *"adds ~0 bytes for
that table"*: a content-hash dedup either stores the blob once or not at all); any new bytes
for that table are DIAGNOSTIC-OVER. The third version's own rows are overhead in its own ratio,
not a dedup failure. This reading is written onto NFR-470's row as a dated clarification
(Task 3, Step 4).

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
`after` only** (`datasets.py:1051-1055`) — that limb is `FD 8047` (DP-6), not this slice's fix.

**Existing evidence.** `backend/tests/test_data_nfrs.py:147`
`test_every_dataset_transition_emits_an_audit_event_with_before_and_after` names rule-set
changes and purges in its docstring but asserts only the draft→validating event (`:179`). No
test asserts on `validation_rule_set.replaced`. The docstring's unasserted claim is `FD 8047`'s
second limb (DP-6). `CR-721:129` claims the replacement *"writes
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
mechanism the code uses** — DP-5, ruled: `FD 8046` asks which side is wrong; this slice
measures the code as it stands and changes neither.

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
projections; neither is read as a verdict** (the ruling's item 1 on NFR-467; DP-4: *"a
DIAGNOSTIC projection, never a verdict"*). **The stated scale** (5 M × 60), DP-4 (b): one run
per arm (`--only glm`, `--only gbm`) on nfr-bench-1's **approved session 2**, about +30 min per
arm, not a third session, each under `systemd-run --scope -p MemoryMax=30G`; Task 4, Step 4
adds them to session 2's run list by a dated line.

**Threshold and reading rule.** Peak `VmHWM` ≤ **32 GB** (32 × 2³⁰ bytes) at 5 M × 60, per
arm. On the shared VM: a measured peak is recorded; a projection is recorded and not read. On
nfr-bench-1 session 2: a completed run's `VmHWM` ≤ 32 GB is a PASS for that arm, > 32 GB is
OVER; **a run killed at the 30 GB cap is reported as "peak > 30 GB" and goes to the lead for an
`FD-`** (DP-4). Either reading is also evidence for `FD 8046` (*"The 5M reading answers whether
the gap matters"*). nfr-bench-1 is used not for quietness (bytes are not slowed by load) but
for **RAM**.

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

**Instrument (pre-registered).** `scripts/measure-p2-nfr-sweep.py cells-diff` (Task 5), in-process
as DP-2 (a) rules, each figure labelled **"server-side, in-process, excludes network"**. Six runs, as `LG-1444` Hold B: rows 10 000, rows 250 000 (threshold at its
default), parquet 10 000 and parquet 250 000 (threshold set to 5 000 for both), parquet
1 000 000 (default threshold); each pair two versions of one table differing in every cell,
no `portfolio`; 10 000 completed `diff_cells` Jobs of other keys seeded first. Per run: the
first request asserted **202**, the Job run to completion and asserted **`succeeded` with its
artifact present** (not merely terminal), then **n = 100** later pages at `limit=50`, cursors
cycling through the artifact, one request at a time.

**Threshold and reading rule.** Each run's nearest-rank page p95 ≤ **300 ms**; on each path,
p95(250 000) ÷ p95(10 000) ≤ **2.0**. Each p95 is read by DP-1's bands (≤ 129 ms
DIAGNOSTIC-PASS, ≤ 300 ms NEAR-BOUND, above OVER); the ratio has its own bands because contention
can move it either way: ≤ 1.5 DIAGNOSTIC-PASS, 1.5–2.0 NEAR-BOUND, > 2.0 DIAGNOSTIC-OVER. Quiet
host (DP-7 (a), ruled): the reading is taken on the shared VM in an `RL-1441` quiet window, with
the load settled below 2.0 before each run; only a NEAR-BOUND figure goes to nfr-bench-1
session 2 as a named extra reading.

## nfr-bench-1 session 2 — the total planned duration (the 12:42:55 entry)

*(Stated 2026-10-14 by the planner, seat planner-p1fix, before the mint, as the 12:42:55
entry orders: "Restate session 2's total planned duration … because my 2 h VM heads-up to the
user must carry a true duration and cost.")* Every run assigned to session 2, summed:

| Runs | Source | Hours |
|---|---|---|
| WK-674 S5's own list: SL-1259's verdicts (NFR-489's exit verdict and the other S5 NFRs, NFR-502 among them) | `RL-1614` item 6, `PL-1620` D5.3; the session estimate is the approved spend's, `~/gi-pricing-plan.local/handover/vm-build-brief-nfr-bench-1-2026-10-12.md:41` (*"WK-674 S5, the exit verdicts (~2.9 h)"*) | 2.9 |
| NFR-485 at 5 M × 60, one run per arm (`--only glm`, `--only gbm`) | DP-4 (b), the 12:07:40 entry: *"≈ +30 min/arm"* | 2 × 0.5 = 1.0 |
| **Committed total** | | **2.9 + 1.0 = 3.9** |
| NFR-467 at 10 M, **only if** the shared VM cannot hold it (the NFR-467 section's guards) | planner's allowance: generate 2 M and 10 M (about 5 min), profile both (≤ 300 s at 10 M by the budget; CR-721's extrapolated 91.7 s), set-up | 0.25 |
| NEAR-BOUND re-run of NFR-468, **only if** its shared-VM reading is NEAR-BOUND | planner's allowance: 2 corpora × 220 requests at < 300 ms is under 3 min; the rest is seeding the freMTPL2 prepared version on the VM | 0.5 |
| NEAR-BOUND re-run of NFR-1443, **only if** NEAR-BOUND | planner's allowance: six runs, each one `diff_cells` Job plus 100 pages, over 10 000 seeded Jobs | 0.5 |
| **Upper total, every allowance taken** | | **3.9 + 0.25 + 0.5 + 0.5 = 5.15** |

So session 2 is **3.9 h committed, at most 5.15 h**, which is under the entry's ~6 h line. The
allowances are the planner's estimates, not measured durations; the slice's `LG-` replaces each
with the run's own wall time. **Cost**, at the VM brief's unconfirmed $0.3453/h (`:54`):
session 2 is 3.9 × 0.3453 ≈ **$1.35** committed, 5.15 × 0.3453 ≈ **$1.78** at most. The
approved budget (*"Likely ≈ $2.20, worst ≈ $7.00"*, `:54`) matches set-up 1 h + session 1
~2.25 h + session 2 ~2.9 h = 6.15 h ≈ $2.12. With this plan's additions the VM's whole life is
1 + 2.25 + 5.15 = 8.4 h ≈ **$2.90** at most: above the "likely" figure, inside the worst case.
The stopped disk (about $0.20/day, `:33`) is extra, as before.

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
4. No requirement is re-worded and no threshold is moved after a reading. The slice's one spec
   edit, NFR-470's dated clarification (Task 3, Step 4), is ordered by DP-3 and written whatever
   the reading; it is never a response to one.
5. A NFR-485 5 M run killed at the 30 GB cap on nfr-bench-1 is handled as an OVER reading
   (steps 1 and 2), with the figure "peak > 30 GB" (DP-4).

## Decision points

Kind and resolver per `document-ids.md` §1.7. The planner ruled none of them. **All seven are
ruled**; the options the ruling did not take are removed, and each row states the one in force.

| # | Question | Ruling in force | Kind | Resolved by |
|---|---|---|---|---|
| DP-1 | What does "near-bound" mean on the shared VM, so that G4's "no near-bound pass or fail is claimed from the shared VM" can be pre-registered? | **(b)**, **amended 12:25:22: the factor is re-measured on this box by Task 0**, and the band becomes 1 / (Task 0's max factor), rounded **down** to 2 decimals; **until Task 0 lands, the interim band is 0.43** (the provenance and limits below). Three bands, the line at that fraction of the budget, the inverse of the measured contention factor. A shared-VM latency ≤ 43 % of its budget is **DIAGNOSTIC-PASS**; above 43 % and ≤ 100 % is **NEAR-BOUND**, not a verdict, and goes to a quiet host as a named nfr-bench-1 session 2 extra reading; above 100 % is **DIAGNOSTIC-OVER**, an `FD-` (the OVER section). Interim `NEAR_BOUND_FRACTION = 0.43`, **accepted (12:25:22 (ii)) as the conservative rounding**: below 1/2.3 = 0.4348, it makes the NEAR-BOUND zone slightly **wider** (129 ms against 130.4 ms on a 300 ms budget), so fewer shared-VM readings are called DIAGNOSTIC-PASS. The NFR-1443 ratio has its own bands (either direction under load): ≤ 1.5 DIAGNOSTIC-PASS, 1.5–2.0 NEAR-BOUND, > 2.0 DIAGNOSTIC-OVER. **Where 2.3 was measured:** 2026-08-22, WK-661's audit-remediation slice, the same `propose_grouping` (`hierarchical_clustering`) call on the same fixture (678 013 rows, a 10 000-level categorical): **8.58 s at 1-minute load 1.6 and 20.01 s at load 8.4** (20.01 ÷ 8.58 = 2.33). Primary record: `docs/specs/02-modelling.md:2981-2993` at `a3fc2e8d`, the NFR-477 re-measurement note, landed by `4d00790a` (#133, 2026-08-22T15:05:36+01:00). The note names the machine (Intel Xeon @ 2.20 GHz, 4 cores, 16.4 GB), **not a run id or a tree**; the nearest recorded tree is `4d00790a`, the commit that recorded it. Restated in `.claude/skills/python-test/SKILL.md:748-758` and `.claude/skills/dev-commands/SKILL.md:895-898` (the plan's earlier citation) and cited in `LG-730:1447`, all at `a3fc2e8d`. **Its limits:** one pair of readings, no run id or tree, on the development machine's earlier 4-core, 16.4 GB shape; the box now reads `nproc` 8, 31 GB. One run cannot establish a verdict, which is why Task 0 re-measures it | decision point | Ruled 2026-10-14, the maintainer (by delegation), to-lead entry 12:07:40 BST (quoted in full under Context), DP-1; **amended** 2026-10-14, the same, to-lead entry 12:25:22 BST, items (i) and (ii) (quoted under Context); Task 0's load regime (ALONE load1 < 1.0 at start; contended [1.0, 2.0) at start, < 2.0 at end) **confirmed** 2026-10-14, the same, to-lead entry 12:31:22 BST, PL-1735 (a) |
| DP-2 | At what level are NFR-468 and NFR-1443 timed? | **(a)** in-process ASGI, `httpx.AsyncClient(transport=ASGITransport(app=create_app(...)))` (`backend/src/app/main.py:70`), against the real migrated Postgres. It covers routing, auth, the DB and serialisation, not the socket, and hosts NFR-468's "never computed" guard. **Every reading is labelled "server-side, in-process, excludes network"** | decision point | Ruled 2026-10-14, the maintainer (by delegation), to-lead entry 12:07:40 BST (quoted in full under Context), DP-2 |
| DP-3 | What does NFR-470's "Storage overhead … ≤ 1.2× the parquet payload" compare, and does the retained source upload count? | **(b), without the retained source upload**: the subject is the Dataset Version's own storage (its tables, reports and profile, and its own rows), read as (payload + overhead) ≤ 1.2 × the parquet payload. The source upload is the promotion Job's blob (RL-1724 DP-U1.1, O1), not the version's, and is not counted. The dedup limb is measured too: a second version with an identical table adds ~0 bytes for that table (read as = 0 new parquet bytes, the NFR-470 section). **The reading is written onto NFR-470's row as a dated clarification in SL-1736's commit** (Task 3, Step 4, exact text there); no `RL-` is needed | design unknown | Ruled 2026-10-14, the maintainer (by delegation), to-lead entry 12:07:40 BST (quoted in full under Context), DP-3; the counted overhead (tables + reports + profile, `ingestion_runs` and `audit_events` excluded and printed) **confirmed** 2026-10-14, the same, to-lead entry 12:31:22 BST, PL-1735 (b) |
| DP-4 | How is NFR-485 measured at its stated scale (5 M × 60, ≤ 32 GB), when neither host has more than 32 GB? | **(b)**: the shared-VM curve to 1 M is a **DIAGNOSTIC projection, never a verdict**; plus one 5 M × 60 run per arm on nfr-bench-1's **approved session 2** (≈ +30 min per arm, not a third session, so within the user's 12 Oct VM approval), each under `systemd-run --scope -p MemoryMax=30G`. A completed run's `VmHWM` is the measurement; a run killed at the cap is "peak > 30 GB" and becomes an `FD-`. Recorded as a dated line amending S5's run list (Task 4, Step 4), which lives in `RL-1614` "What it obliges" item 6 (`:107-111` at `a3fc2e8d`) and `PL-1620` (Global Constraints `:125-130`, D5.3 `:189-199`); the lead puts it in the 2 h VM heads-up | decision point | Ruled 2026-10-14, the maintainer (by delegation), to-lead entry 12:07:40 BST (quoted in full under Context), DP-4 |
| DP-5 | NFR-485's mechanism clause names `QuantileDMatrix`/streaming construction; the code uses `xgb.DMatrix` (`gbm.py:895`), LightGBM keeps raw data (`gbm.py:1108`), and the GLM is dense (`glm.py:578`). Which one is wrong? | **An `FD-`, measure as-is**: filed as **`FD 8046`** (working id, D18, `origin/docs-d18-2026-10-14` @`b1ecf56d`); which side is wrong is its `CLAUDE.md` §0 question. This slice changes neither code nor spec; the 5 M reading (DP-4) answers whether the gap matters | fact | Ruled 2026-10-14, the maintainer (by delegation), to-lead entry 12:07:40 BST (quoted in full under Context), DP-5 |
| DP-6 | The purge limb has the same gap as the rule-set limb (`datasets.py:1051-1055` passes `after` only), and `test_data_nfrs.py:147` names both in its docstring but asserts neither. Is it in this slice? | **One finding, both limbs**: filed as **`FD 8047`** (working id, D18, same branch). NFR-472's red-first test **stays in this slice** for the `replace_rule_set` limb (Task 1); the purge limb and the docstring are `FD 8047`'s, not this slice's | scope | Ruled 2026-10-14, the maintainer (by delegation), to-lead entry 12:07:40 BST (quoted in full under Context), DP-6 |
| DP-7 | Does NFR-1443's "on a quiet box" require nfr-bench-1, or can the shared VM in an `RL-1441` quiet window ("the gate slots free, no other heavy process") satisfy it? | **(a)**: the shared-VM reading, taken in an `RL-1441` quiet window with the load settled below 2.0 before each run, is the reading, **unless it is NEAR-BOUND per DP-1**, when it joins nfr-bench-1 session 2 as a named extra reading | decision point | Ruled 2026-10-14, the maintainer (by delegation), to-lead entry 12:07:40 BST (quoted in full under Context), DP-7 |

## Write set

- Modify: `backend/src/app/platform/validation_rules.py` (`replace_rule_set`, `:801-913`).
- Modify: `backend/tests/test_api_datasets.py` (one new test after `:190`).
- Create: `scripts/measure-p2-nfr-sweep.py` (subcommands `one-way`, `storage`, `cells-diff`, and `profile` for NFR-467, added by the 12:42:55 entry). `scripts/bench-data.py` is called as it is, not modified.
- Modify: `scripts/bench-model.py` (`--peak hwm`, Task 4).
- Create: the slice's `LG-` under `docs/ledgers/` (`docs/_templates/LG.md`).
- Modify: `docs/specs/01-data-management.md` — NFR-470's row (`:1184` at `a3fc2e8d`) only: one
  dated clarification appended inside its cell (DP-3; Task 3, Step 4). No other spec line.
- Modify: `docs/roadmap.md` — the slice's own closing lines, and **one dated line under
  `SL-1259`'s row** (S5) amending its nfr-bench-1 session 2 run list (DP-4; Task 4, Step 4).
  `RL-1614` and `PL-1620`, where the run list is stated, are frozen and are not edited
  (`document-ids.md` §1.5); `SL-1259`'s living row already carries dated lines of this kind (the
  planner's of 2026-10-12, `docs/roadmap.md:1162` at `a3fc2e8d`). *(Confirmed 2026-10-14 by
  the maintainer (by delegation), entry "2026-10-14 12:31:22 BST": the S5 run-list line under
  `SL-1259`'s row is OK.)*

No other spec file, and no contract, migration or frontend file.

## Tasks

### Task 0: Preconditions, the contention factor re-measured on this box, and pre-registration

- [ ] **Step 1:** Confirm this plan is on `main` with all seven DP rows ruled (the "Resolved by" column: the maintainer's (by delegation) entries of 2026-10-14 12:07:40 BST and, for DP-1, 12:25:22 BST), and that `FD 8046` and `FD 8047` are minted on `main` (Scope). This plan merges before them (mint order P1 → D18 → P2, the maintainer's (by delegation) entry "2026-10-16 09:40:20 BST"), so the slice's GO waits for D18's merge. If either is not on `main`, stop.
- [ ] **Step 2: Pre-register the factor's reading rule, before its first run (DP-1, 12:25:22 (i)).** Add a `contention` subcommand to `scripts/measure-p2-nfr-sweep.py` with these module-level constants, and commit it (**pre-registration P0**); the `LG-` cites P0's sha, and every factor run's start stamp is later than P0's `%aI`:
  - **The fixed benchmark:** `uv run python scripts/bench-model.py --only proposals` at its defaults (678 013 rows, `--levels 10000`, `--groups 20`), reading only the line `NFR-477 propose_grouping hierarchical_clustering` (wall-clock and CPU seconds) — the same call on the same fixture that produced 8.58 s and 20.01 s on 2026-08-22. **Its tree** is P0's commit, printed with `git rev-parse HEAD` at every run; the factor runs never span a commit.
  - **ALONE run (A):** taken in a lead-granted ALONE window (both gate slots free, no other heavy process), load1 < 1.0 at its start.
  - **Contended run (B):** taken outside an ALONE window, in **the regime the sweep's latency runs will meet**: load1 at its start ≥ 1.0 and < 2.0, the ceiling Tasks 2 and 5 settle the load below before each timed run. **A contended run whose load1 at its start or at its end is ≥ 2.0 is excluded and re-run, never kept;** an ALONE run whose load1 at its start is ≥ 1.0 is likewise excluded and re-run.
  - *(Confirmed 2026-10-14 by the maintainer (by delegation), entry "2026-10-14 12:31:22 BST",
    PL-1735 (a): ALONE = load1 < 1.0 at start; contended = load1 in [1.0, 2.0) at start and
    < 2.0 at end. The two bullets above were the planner's pre-registration; they now stand as
    ruled, unchanged.)*
  - **Pairs:** at least **3** A/B pairs, run interleaved A, B, A, B, …; each pair is one A and the next valid B. Every run records load1 at its start and at its end, CPU seconds and wall-clock.
  - **The factor** = the **maximum** of the per-pair ratios B ÷ A; the instrument prints every pair's ratio, the min, the max and the spread (max − min).
  - **The band** = 1 / factor, **rounded down** to 2 decimals (`math.floor(100 / factor) / 100`). If the factor is ≤ 1.0, the band is reported to the lead and not applied.
- [ ] **Step 3: Run the factor.** Record every run, every exclusion and its reason, each pair's ratio, the factor, the spread and the band in the `LG-`, with the tree. Until this step's reading is in the `LG-`, the interim band **0.43** applies (DP-1), cited there with its provenance and its limits.
- [ ] **Step 4: Pre-register the sweep's thresholds and reading rules (pre-registration P1).** Write them, as ruled, as module-level constants at the top of `scripts/measure-p2-nfr-sweep.py` (`THRESHOLDS_MS`, `NEAR_BOUND_FRACTION`, `RATIO_BANDS`, `NFR_470_RULE`), with `NEAR_BOUND_FRACTION` set to Step 3's band (or 0.43 if Step 3 has not landed), and in the `LG-`'s Scope section, quoting this plan's rows. Commit them **before any sweep run**; the `LG-` cites P1's sha, and every sweep run's start stamp must be later than P1's `%aI`. Every 129 ms figure in this plan is the 300 ms budget at the interim 0.43 and moves with the band.
- [ ] **Step 5:** Each measurement session records at its start and end: `git rev-parse HEAD`, the tree, `nproc`, `free -m`, `/proc/loadavg`, `pgrep -af 'pytest|vitest|flock'`, and the state of both gate slots.

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

- [ ] **Step 1:** Build the client in-process (DP-2 (a)): construct the app with `create_app` (`backend/src/app/main.py:70`) and the settings the backend test fixtures use; mirror `backend/tests/conftest.py`, do not reinvent it.
- [ ] **Step 2:** Seed the two corpora (the NFR-468 section above); assert each version reaches `validated` with a stored profile, and print `pg_column_size(body)`.
- [ ] **Step 3:** Install the "never computed" guard (the three `pricing_core.data.profile` functions replaced by a raiser) for the timed phase only.
- [ ] **Step 4:** 20 warm-up requests, then n = 200 timed, each `time.perf_counter_ns()` around one awaited request, closed loop, one client. No profiler, no asyncio debug mode, no sampler or poller thread during the timed phase. Print p50/p95/p99/max (nearest rank), n, corpus, profile bytes, load before and after, CPU seconds, and the label "server-side, in-process, excludes network".
- [ ] **Step 5:** Run it on the shared VM under the gate-1 slot, with the load settled below 2.0 immediately before the timed phase (printed). Record the reading, its DP-1 band (DIAGNOSTIC-PASS, NEAR-BOUND or DIAGNOSTIC-OVER), its DP-2 label and the tree in the `LG-`. A NEAR-BOUND reading is written as a named nfr-bench-1 session 2 extra reading. Commit.

### Task 3: NFR-470 — the storage instrument and its reading

**Files:** `scripts/measure-p2-nfr-sweep.py` (`storage` subcommand).

- [ ] **Step 1:** Seed freMTPL2's two versions with `examples/fremtpl2/seed.py`, then ingest the identical source again as a third version.
- [ ] **Step 2:** The byte accounting, as the NFR-470 section states, printed per version: payload, counted overhead, the ratio, and each excluded figure on its own labelled line (the `ingestion_runs` and `audit_events` rows among them, as confirmed by the 12:31:22 entry, PL-1735 (b)); the third version's new parquet bytes for its identical table printed separately (the dedup limb).
- [ ] **Step 3:** Read by DP-3 (b)'s rule (ratio ≤ 1.2, dedup = 0 new bytes); record in the `LG-` with its band. Commit.
- [ ] **Step 4: The dated clarification on NFR-470's row (DP-3, ruled; in the slice's commit, whatever the reading).** Follow `spec-change`. In `docs/specs/01-data-management.md`, NFR-470's row (`:1184` at `a3fc2e8d`), append the text below inside the row's second cell, after `(ID-4).` and before the closing ` |`. Substitute the commit date and the **minted** ids for `SL-1736`, `PL-1735` and `RL 8028` (minted as `RL-1724` in D17, #1307; never commit a working id into a spec). No other word of the row changes. Proposed text:

  > *(Clarified &lt;date&gt;, WK-1178, SL-1736, PL-1735 DP-3 (b), on the maintainer's (by delegation) entry "2026-10-14 12:07:40 BST" in `to-lead.md`: **the subject is the Dataset Version's own storage** — its parquet tables, its validation reports and its profile — and the bound reads as that total ≤ 1.2× the parquet payload of its tables. The uploaded source file is not counted: it is the promotion Job's blob (RL 8028, O1), not the version's. The deduplication clause reads: a later version whose table is identical to an earlier version's adds no new parquet bytes for that table.)*

  Then run `python3 scripts/audit-docs.py` through the gate-2 slot (`CLAUDE.md` §0: every spec change runs it before commit).

### Task 4: NFR-485 — the peak-memory instrument and the shared-VM curve

**Files:** Modify `scripts/bench-model.py`.

- [ ] **Step 1:** Add `--peak hwm`: after the one phase, read `VmHWM` from `/proc/self/status` and print it (MB and bytes) beside the existing statm peak. Abort before the phase if `MemAvailable` < 8 GB.
- [ ] **Step 2:** On the shared VM, under the gate-1 slot: `--only glm` and `--only gbm` at 250 000, 500 000 and 1 000 000 rows, `--factors 60`, each in its own process. Record each `VmHWM`, the two projections to 5 M, labelled "projection, not a reading".
- [ ] **Step 3:** Write the DP-4 extra readings for nfr-bench-1 session 2 into the `LG-` as named items, one per arm: the exact commands (`systemd-run --scope -p MemoryMax=30G uv run python scripts/bench-model.py --only glm --rows 5000000 --factors 60 --peak hwm`, and the same with `--only gbm`), the cap, and the reading rule (the NFR-485 section). Commit.
- [ ] **Step 4: The dated line amending S5's run list (DP-4, ruled).** S5's run list is stated in `RL-1614` "What it obliges" item 6 (`:107-111` at `a3fc2e8d`) and `PL-1620` (`:125-130`, D5.3 `:189-199`), both frozen (`document-ids.md` §1.5), so the line goes under `SL-1259`'s row in `docs/roadmap.md`, after its existing dated line (`:1162` at `a3fc2e8d`). Text, with the minted ids substituted:

  > *Dated &lt;date&gt;, WK-1178's SL-1736 (PL-1735 DP-4 (b)), on the maintainer's (by delegation) entry "2026-10-14 12:07:40 BST" in `to-lead.md`, DP-4: nfr-bench-1 session 2's run list (`RL-1614` item 6; `PL-1620` D5.3) also carries NFR-485's 5 M × 60 runs, one per arm (`bench-model.py --only glm` and `--only gbm`, `--peak hwm`), each under `systemd-run --scope -p MemoryMax=30G`, ≈ +30 min per arm inside the approved session 2, not a third session. A run killed at the cap is reported as "peak > 30 GB" and becomes an `FD-`. The commands are SL-1736's `LG-`'s. This row's status and fields are unchanged.*

  *(Confirmed 2026-10-14 by the maintainer (by delegation), entry "2026-10-14 12:31:22 BST":
  "The S5 run-list amendment as a dated line under SL-1259's roadmap row (RL-1614/PL-1620
  frozen): OK.")*

  Commit.

### Task 5: NFR-1443 — the cells-diff instrument and its reading

**Files:** `scripts/measure-p2-nfr-sweep.py` (`cells-diff` subcommand).

- [ ] **Step 1:** The six runs as the NFR-1443 section states, the threshold set per run through the `rate_tables.cell_threshold` setting, and each version's `storage` asserted before timing.
- [ ] **Step 2:** For each run, assert that the first request returns 202 and that its Job is `succeeded` with its artifact present. Then time n = 100 later pages at `limit=50` under the same instrument rules as Task 2, Step 4.
- [ ] **Step 3:** Take the readings in an `RL-1441` quiet window on the shared VM, settling the load immediately before each run. Read them by DP-1's bands and the ratio bands, each labelled "server-side, in-process, excludes network", and record them in the `LG-`. Under DP-7 (a) only a NEAR-BOUND figure becomes a named nfr-bench-1 session 2 extra reading. Commit.

### Task 5a: NFR-467 — the profiling instrument at 10 M rows (added 2026-10-14, the 12:42:55 entry)

**Files:** `scripts/measure-p2-nfr-sweep.py` (`profile` subcommand).

- [ ] **Step 1:** Pre-register with P1 (Task 0, Step 4): add `NFR_467_RULE` beside the other
  constants: `{"sizes": [2_000_000, 10_000_000], "columns": 80, "time_budget_s": 300,
  "memory_ratio_below": 5.0, "mem_available_min_gb": 16, "disk_free_min_gb": 12}`.
- [ ] **Step 2:** Write the `profile` subcommand as the NFR-467 section states: for each size,
  check both guards and print them; generate with `bench-data.py --rows N --generate-to` in its
  own process under the job tmp directory; profile in a fresh process (baseline `VmRSS` after
  imports, `profile_parquet` as `bench-data.py:196-198`, `perf_counter` at its boundaries,
  `VmHWM` after); print wall seconds, `VmHWM`, baseline, Δpeak, payload bytes, load at start and
  end, and the tree; delete the parquet.
- [ ] **Step 3:** Run it on the shared VM under the gate-1 slot, load settled below 2.0 at
  start. Read the 10 M time by DP-1's bands against 300 s, and r = Δpeak(10 M) ÷ Δpeak(2 M)
  against 5.0. Record both in the `LG-`, labelled DIAGNOSTIC (time) and as a reading (memory),
  each with its size, tree and load. If a guard keeps the run off the shared VM, or the time is
  NEAR-BOUND, name the 10 M run as an nfr-bench-1 session 2 extra reading. Commit.

### Task 6: The gate, the ledger, the hand-off

- [ ] **Step 1:** Run both gate halves (`dev-commands`), through the gate-1 slot.
- [ ] **Step 2:** In the `LG-`, record one row per NFR: the reading, its band (DIAGNOSTIC-PASS, NEAR-BOUND or DIAGNOSTIC-OVER; NFR-485's shared-VM curve "projection, not a reading"), and its next step. The next step is "none", "nfr-bench-1 session 2 extra reading (named)", or "OVER, reported to the lead for an `FD-`". NFR-485's row names its two session 2 runs (Task 4).
- [ ] **Step 3:** Send the lead the list of named extra readings (always NFR-485's two 5 M runs; any NEAR-BOUND latency reading; NFR-467's 10 M run if Task 5a named it), with session 2's total re-summed from "nfr-bench-1 session 2 — the total planned duration" using the actual list, for the lead's 2 h VM heads-up (DP-4; the 12:42:55 entry).

## Acceptance Standard

1. `uv run pytest backend/tests/test_api_datasets.py -k test_replacing_a_rule_set_is_audited_with_before_and_after -q` passes on the slice head. The `LG-` quotes the red run from before the fix. That run failed on `v2.before == v1.after` with `None` on its left side, and on no other line.
2. `git -C <wt> grep -n 'req("NFR-472")' backend/tests/test_api_datasets.py` lists the new test.
3. `git -C <wt> log --format='%h %aI %s' -- scripts/measure-p2-nfr-sweep.py` shows pre-registration P0 (Task 0, Step 2), older than every factor run's start stamp in the `LG-`, and P1 (Task 0, Step 4), older than every sweep run's start stamp. The `LG-` records at least 3 interleaved A/B pairs of the named benchmark, each run's load1 at start and end, every exclusion, each ratio, the max factor and the spread. P1's constants equal the ruled DP-1 and DP-3 values: `NEAR_BOUND_FRACTION` = `floor(100 / max factor) / 100` from that record (0.43 only if the factor reading has not landed), the ratio bands 1.5 and 2.0, and an NFR-470 rule of ratio ≤ 1.2 with the source upload excluded and dedup = 0 new bytes.
4. `uv run python scripts/measure-p2-nfr-sweep.py --help` lists `one-way`, `storage`, `cells-diff` and `profile`. `uv run python scripts/bench-model.py --help` lists `--peak`.
5. The `LG-` has one reading row for each of NFR-467, NFR-468, NFR-470, NFR-485 and NFR-1443, each labelled DIAGNOSTIC. Each row carries its size or corpus, its n and percentile (latency), the tree, the load at start and end, and its band: DIAGNOSTIC-PASS, NEAR-BOUND or DIAGNOSTIC-OVER (DP-1). Every NFR-468 and NFR-1443 figure carries the label "server-side, in-process, excludes network" (DP-2). The NFR-470 row gives the ratio without the source upload, the excluded figures on their own lines, and the dedup limb's new-bytes figure (DP-3).
6. Each OVER reading in the `LG-` has a matching line to the lead, sent at the time of the reading, that names the NFR, the figure and the threshold. `git -C <wt> diff --stat origin/main...HEAD -- docs/specs` lists only `docs/specs/01-data-management.md`, and `git -C <wt> diff -U0 origin/main...HEAD -- docs/specs/01-data-management.md` shows one changed line, NFR-470's row, which still contains the row's original text unchanged and now ends with Task 3, Step 4's clarification (DP-3).
7. The NFR-485 projections in the `LG-` are labelled as projections, and no verdict is read from them. The `LG-` names NFR-485's two 5 M × 60 nfr-bench-1 session 2 runs with their commands and the `MemoryMax=30G` cap, and `git -C <wt> diff origin/main...HEAD -- docs/roadmap.md` adds Task 4, Step 4's dated line under `SL-1259`'s row and changes no other line of that row (DP-4).
8. Both gate halves exit 0 on the slice head, through the gate-1 slot.
9. `python3 scripts/audit-docs.py` prints no line that names this slice's files, except the working-id lines expected before the mint (checks 31, 32 and 39).
10. **NFR-467 at 10 M (the 12:42:55 entry).** The `LG-` has the `profile` subcommand's output for 2 000 000 and 10 000 000 rows × 80 columns, each from a fresh process: wall seconds, `VmHWM`, baseline, Δpeak, payload bytes, both guards, load at start and end, and the tree. The 10 M time is read against 300 s by DP-1's bands, and r = Δpeak(10 M) ÷ Δpeak(2 M) against 5.0, by `NFR_467_RULE` as committed at P1, older than both runs' start stamps. No NFR-467 figure in the `LG-` is extrapolated from another size.

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
- The lead: NFR-485's two 5 M runs (and any NEAR-BOUND latency reading the slice names, and NFR-467's 10 M run if Task 5a names it) in the 2 h nfr-bench-1 VM heads-up (DP-4), with session 2's duration and cost from "nfr-bench-1 session 2 — the total planned duration": 3.9 h committed, at most 5.15 h; ≈ $1.35, at most ≈ $1.78 (the 12:42:55 entry). Session 2 runs them only if `SL-1259`'s dated line (Task 4, Step 4) is on `main` by then, or the lead adds them to the session's brief directly.
- `FD 8046` (DP-5) and `FD 8047` (DP-6) are filed (D18); their rulings, severities and owners are the auditor's and the lead's, not this slice's.

## Self-review

- **Coverage.** Each of the five ids in the ruling's item 3 has a section with its verbatim row, its owning code and its existing evidence. Each of the four measured NFRs has an instrument, a corpus, a pre-registered threshold and reading rule, and a quiet-host statement. NFR-472 has its red-first test, the red's cause, and its fix. "OVER → an FD" is one shared section.
- **Literals checked against `8eaf6d5f`.** These were checked: the route paths, `DEFAULT_LIMIT = 50`, `rate_tables.cell_threshold` at 250 000, `decide_storage_mode`, `replace_rule_set`'s `audit.record` call with no `before`, `audit.record`'s `before=None` default, `_approved_rule`'s signature, the PUT body shape (`rules`, `rule_id`, `enabled`), the action string `validation_rule_set.replaced` and its entity ref form, `create_app`, `TARGET_FACTORS = 60`, `xgb.DMatrix` at `gbm.py:895`, and `x = design.to_numpy()` at `glm.py:578`.
- **Not verified here.** `backend/tests/conftest.py`'s app and DSN fixtures (Task 2, Step 1 names that file as the authority). The `systemd-run` cap on nfr-bench-1 (DP-4 (b); the session's set-up seat checks it there).
- **Amendment of 2026-10-14 (the 12:07:40 BST rulings), checked at `a3fc2e8d`.** Every DP row states one ruling and its resolver; no option the ruling did not take remains. Each consequence is carried into a task and an acceptance item: DP-1's bands and its 12:25:22 re-measure (Task 0, Steps 2 to 4; Tasks 2, 5, 6; Acceptance 3, 5), DP-2's label (Tasks 2, 5; Acceptance 5), DP-3's reading and the NFR-470 clarification (Task 3, Steps 2 to 4; write set; Acceptance 3, 5, 6), DP-4's session 2 runs and the `SL-1259` dated line (Task 4, Steps 3 and 4; write set; Acceptance 7), DP-5 and DP-6 as `FD 8046` and `FD 8047` (Scope; the NFR-472 and NFR-485 sections), DP-7's quiet window (NFR-1443 section; Task 5). The 2.3 factor is traced past `dev-commands` to its primary record (DP-1 row). Line numbers in the amended text cited "at `a3fc2e8d`" were read there; between `8eaf6d5f` and `a3fc2e8d` none of the code files this plan cites changed, and `03-rating-engine.md`'s NFR-1443 row moved from `:1518` to `:1519`.
- **Readings put to the lead.** (i) The 2.3 factor's limits and the 0.43 rounding were put to the lead and ruled at 12:25:22: Task 0 re-measures the factor, and 0.43 is accepted as the interim, conservative rounding. **The planner's own pre-registration in Task 0, Step 2, open to the lead's correction before P0:** the named benchmark, the ALONE limit load1 < 1.0, and the contended regime load1 in [1.0, 2.0) at start and < 2.0 at end, taken from Tasks 2 and 5's settle ceiling. (ii) NFR-470's counted overhead follows the ruling's enumeration (*"its tables + reports + profile"*), so the `ingestion_runs` and `audit_events` rows are excluded and printed apart.
- **Confirmed 2026-10-14 by the maintainer (by delegation), entry "2026-10-14 12:31:22 BST"** (recorded by the planner, seat planner-p1fix, before the mint): (a) the Task 0 regime — ALONE = load1 < 1.0 at start; contended = load1 in [1.0, 2.0) at start and < 2.0 at end — **CONFIRMED** (Task 0 Step 2, DP-1 row); (b) NFR-470's counted overhead = the version's tables + reports + profile, with the `ingestion_runs` and `audit_events` rows excluded and printed — **CONFIRMED** (the NFR-470 section, DP-3 row, Task 3 Step 2); and the S5 run-list line under `SL-1259`'s row: **OK** (Task 4 Step 4, write set). Neither choice is now open to correction before P0; both stand as ruled, and no task's text changed beyond these dated lines.
- **The 12:42:55 entry, item (2), at every site** (amended 2026-10-14 by the planner, seat planner-p1fix, before the mint): *"its own instrument"*: the `profile` subcommand (the NFR-467 section, Task 5a, write set, Acceptance 4); *"the pre-registered threshold from NFR-467's text"*: the row and its 2026-08-14 amendment quoted verbatim, time ≤ 300 s by DP-1's bands and memory r < 5.0 read as the amendment's own "sub-linear" (the NFR-467 section; `NFR_467_RULE` at P1, Task 5a Step 1); *"a task and an acceptance item"*: Task 5a, Acceptance 10 (and 5); *"measured at 10M"*: 10 000 000 rows, never extrapolated (Goal, Acceptance 10); *"If the shared VM cannot hold it, it goes to nfr-bench-1 session 2"*: the shared VM, with the sizing (5.5 GB parquet, 8–13 GB generation peak, under 2 GB profiling, against 31 GB and 15 GB free disk) and two guards, session 2 the fallback (the NFR-467 section); *"Restate session 2's total planned duration"*: its section, with the arithmetic, 3.9 h committed and 5.15 h at most, under ~6 h, with its cost (and Task 6 Step 3, Hand-off). The memory reading's 5.0 is the planner's reading of the row's "does not scale" through its amendment's "sub-linear"; the row states no number, and a tighter bound would be one this plan invented. **It stays flagged DERIVED, not specified**; it was **accepted as pre-registered** by the maintainer's (by delegation) entry "2026-10-14 13:21:41 BST" (*"ACCEPT r < 5.0 as the literal reading of "sub-linear" … with the reading flagged as derived, not specified"*), recorded at the threshold in the NFR-467 section.
- **No placeholders.** `<date>` and the working ids in Task 3, Step 4 and Task 4, Step 4 are substituted at the slice's commit, as those steps say.
