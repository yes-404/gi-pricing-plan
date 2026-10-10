---
id: FD-1573
family: finding
title: Rating throughput at exit-demo scale — score_batch runs at 471 policies per second (flat 50k to 400k) and the dislocation book build at 195 to 228 policies per second, so a full 678,013-row book is derived at 76 to 82 minutes and about 20 GiB, against a planning rate of 1,415 policies per second
status: active
created: 2026-10-10            # original date 2026-10-09, set at the draft; minted 2026-10-10
owner: auditor
tree: f59b546e748eca464c279a77ca48e166689d5a0e
corrected_by: []
relates: [WK-673, WK-1178, SL-1387, PL-1452, PL-1544, CR-927, CR-1212, RL-1521, NFR-493, NFR-504]
---

# FD-1573 — Two rating paths, two measured rates, one derived full-book cost

*Disclosure: drafted under working id 9446; minted as FD-1573 on 2026-10-10, in the D5 batch mint PR. `LG 9478` (the S3 ledger, unminted) is cited in space form, "LG 9478", and left out of `relates:`.*

**DRAFT, rewritten 2026-10-10 on the logged figures only** (the first draft read one 50,000-policy probe and a wrong path split). Filed on `draft/fd-9446`, no PR, at the lead's ruling (`to-lead.md`, "2026-10-09 16:12:53 BST — RULING: Task 7 reduced design = R2 …", item 4), re-opened by the entries "2026-10-10 00:08:17 BST" and "2026-10-10 00:08:46 BST" (the correction of the 00:08:17 curve to two rating paths; `channel/from-lead-2026-10-09.md`). **Every figure marked "measured" is a line in `~/gi-pricing-plan.local/task7-s3e/out/` (named below). Every figure marked "derived" is the auditor's arithmetic and is not a measurement; per `PL-1452` DP-S3-10 (b), "no NFR verdict from a derived figure".** No full-book run completed.

## Finding

`PL-1452` P9 (`:326`, `origin/main` `61e2a8d9`) books Task 7 on NFR-493's only recorded throughput, 5,093,947 risks/hour/worker (`CR-927` §10.4, an older tree, 300,000 rows), which is **1,414.985 policies/s** ("1414" in the brief and ledger truncates it). Measured on the freMTPL2 `model_call` algorithm, the two paths that rate a book run at:

- **`score_batch` alone: 470.7 to 480.7 policies/s, flat from 50,000 to 400,000 policies** (linear in N). That is 2.94x to 3.01x below the planning rate.
- **The book build `portfolio_for` → `dislocation_frame`: about 195 policies/s (200k) and about 210 (400k) as whole-invocation remainders, 228 as the marginal rate between the two sizes** (all derived from logged walls). It rates every policy once to set `current_premium_minor`, before `score_batch` is timed.

The finding does **not** say the engine regressed: the workload (`CR-927` Task 3D, handler with Postgres/MinIO I/O, a different algorithm) and the tree both differ from the planning figure, and nothing here separates them. It says the planning rate does not transfer to this workload and every size or schedule derived from it is short.

## Evidence — what was measured

All commands run through `~/gi-pricing-plan.local/task7-s3e/inv.sh` / `inv-rss.sh` (`timeout … uv run --directory <sl-1387 worktree> python scripts/measure-attribution-cost.py <args>`), output in `~/gi-pricing-plan.local/task7-s3e/out/`, stamps from `progress.log`. **Machine: 8 CPUs, 31 GiB** (`nproc`; `free -g`, 2026-10-09 23:10 UTC). **Trees:** `088a0c23` (probe), `7dba2d11` (20k probe), `f59b546e` (200k, 400k). `git diff --name-only 088a0c23 f59b546e` and `088a0c23 7dba2d11` each list only `docs/ledgers/LG-09478-…`, so the measured code is identical at all three.

### Path 1 — `score_batch` alone (`what: "score_batch"`, timed as its own figure around `score_batch(bundle, frame).collect()` on a pre-built frame, `cmd_cost`)

| file | command (after `cost`) | tree | N policies | seconds | policies/s | load1 at emit | ru_maxrss of the whole invocation |
|---|---|---|---|---|---|---|---|
| `11-a-probe20k.jsonl` | `--policies 20000 --score-policies 20000 --ks 3 --runs 1` | `7dba2d11` | 20,000 | 41.173 | 485.76 | 2.43 | not taken |
| `10-rate-probe.jsonl` | `--policies 20000 --score-policies 50000 --ks 3 --runs 1` | `088a0c23` | 50,000 | 104.025 | 480.65 | 2.56 | not taken |
| `50-sb-200k.jsonl` | `--policies 1000 --score-policies 200000 --ks "" --runs 1` | `f59b546e` | 200,000 | 424.865 | 470.74 | 2.45 | 6,513,848 KiB (6.21 GiB) |
| `60-sb-400k.jsonl` | `--policies 1000 --score-policies 400000 --ks "" --runs 1` | `f59b546e` | 400,000 | 848.405 | 471.47 | 2.80 | 12,515,908 KiB (11.94 GiB) |

One run each (`--runs 1`), so no median across runs. The rate falls 3% from 20k to 400k. The 20k and 50k probes ran with small single-file authoring tests beside them (nice 19, disclosed in the first draft; the lead's ruling at `to-lead.md` 15:22:26 BST, item 3), load1 at or below 2.56; the 200k and 400k runs read load1 2.45 and 2.80 at emit, `progress.log` START readings 1.43 and 1.98, with no heavy command running beside them by the lead's rule. The load1 numbers are single readings, not a mean.

### Path 2 — the book build, `portfolio_for(fx, N)` → `dislocation_frame`

`cmd_cost` calls `portfolio_for(fx, args.score_policies)` before it times `score_batch`. Read at `f59b546e` (`scripts/measure-attribution-cost.py:477-495`): `portfolio_for` calls `dislocation_frame(bundle, bundle, first, spec)` over the whole book to set `current_premium_minor`. `dislocation_frame` (`packages/pricing-core/src/pricing_core/rating/analysis.py:177`, `origin/main`) runs `_score_pass` twice, baseline and candidate, and each `_score_pass` calls `score_batch(bundle, frame).collect()` (`:159`) and then loops the result in Python (`iter_rows`, `LadderRung.model_validate`). **The build is not timed on its own**: it is the remainder of the invocation.

| file | whole-invocation wall (`progress.log` START to END, UTC) | `score_batch` timed | remainder | remainder per policy |
|---|---|---|---|---|
| `50-sb-200k` | 20:13:07Z → 20:37:19Z = 1,452 s | 424.865 s | **1,027 s (derived)** | 5.13 ms = **194.7 policies/s** |
| `60-sb-400k` | 20:37:35Z → 21:23:27Z = 2,752 s | 848.405 s | **1,904 s (derived)** | 4.76 ms = **210.1 policies/s** |

The remainder also holds interpreter start, fixture load, the 1,000-policy `book` build, bundle compile and load. Taking the two points as a line: marginal **(1,904 − 1,027) / 200,000 = 4.385 ms/policy = 228 policies/s** and a fixed part of about **150 s** (derived; two points, so no residual to test the fit). That marginal cost is 2.07x the `score_batch` per-policy cost (2.12 ms), which is what two `score_batch` passes plus a small Python loop predict (4.24 ms + 0.14 ms). **That is a reading of the code against two derived numbers, a hypothesis for the remedy's profiling, not a measurement.**

### Memory (whole invocation, measured)

`ru_maxrss` is `RUSAGE_CHILDREN` of the wrapper (`inv-rss.sh`), the peak of the largest descendant, so it covers both paths and the build. 6,513,848 KiB at N=200,000 (32.57 KiB/policy) and 12,515,908 KiB at 400,000 (31.29 KiB/policy). The slope is **30.01 KiB/policy** and the intercept about 0.49 GiB (two points, derived). The peak is the build's frame and the collected portfolio, which the run holds beside the bundle; which of them dominates is not measured.

### The full book — not completed

The full freMTPL2 book is **678,013 policies** (`cost … --score-policies 678013`). Two attempts to score it did not finish: `01-k3-score` (`--score-policies 678013 --ks 3 --runs 5`, tree `088a0c23`, started 13:02:18Z, ended `rc=143` at 14:56:31Z by the lead's stop: 1 h 54 m, no output line) and `30-score-r1` (`--score-policies 678013 --ks 3 --runs 1`, tree `f59b546e`, START 17:38:57Z, **no END line in `progress.log`; the next START is at 18:39:30Z, 60 min 33 s later**; the stop is not logged there, and `30-score-r1.jsonl` and `.err` are empty). **Neither gives a figure.** The first is consistent with the rate: five passes at 471/s are 120 min.

**Derived full book (not measured):** build at 228 policies/s ≈ 49.6 min plus the ~150 s fixed part, plus `score_batch` at 471 policies/s ≈ 24.0 min, **≈ 76 min** (at the whole-invocation remainders 195 to 210 policies/s the build is 54 to 58 min and the total **78 to 82 min**). Range **76 to 82 min**. **Memory ≈ 19.9 GiB** by the slope and intercept, **≈ 20.2 GiB** by 400k's 31.29 KiB/policy, against 31 GiB on this box. Linear extrapolation from 200k and 400k to 678k is untested beyond 400k.

## Which path NFR-493 governs

- **NFR-493** (`docs/specs/03-rating-engine.md:1390`, no dated amendment): *"Batch scoring ≥ 1 M risks/hour per worker (NFR-455), linear in workers."* **NFR-455** (`docs/specs/00-overview.md:532`): *"Batch scoring throughput: ≥ 1 M risks/hour per worker for a typical motor rating structure (≈ 200 DAG steps)."* The floor in this unit is 1,000,000 / 3,600 = **277.78 risks/s**.
- **It governs `score_batch`** (batch scoring of risks, `03` §8; `score_batch` is the batch scorer, `rating/score.py`). **It does not name the Dislocation Run**: `FR-263` (`03:188`) states no time or throughput budget, and no NFR in `03` §8 or `04` §9 gives the dislocation path one. `WF-699` Phase D says "30–60 min compute" for 1.28 M policies, a workflow estimate, not an NFR.
- **NFR-504** (`docs/specs/04-optimisation.md:431`): *"A GIPP check over an 850 k renewal population completes in < 20 min (it is two full batch scoring passes — NFR-493)."* It governs the **GIPP check**, and it is the only text that composes NFR-493 into two passes. It does not govern the dislocation run, which is a different job.
- **The unit is "risks", not policies.** A policy rated under two bundles is two risks scored.

### Rating each path against the 277.78 line

| path | rate | in risks/hour | vs 277.78/s | verdict (derived from measured rates; no NFR verdict, DP-S3-10 (b)) |
|---|---|---|---|---|
| `score_batch`, 200k and 400k | 470.74 and 471.47 policies/s = risks/s | 1,694,656 and 1,697,302 | **1.69x to 1.70x above** | floor met on the governing path, by the measured figure |
| `score_batch`, 50k probe | 480.65 | 1,730,347 | 1.73x above | same |
| book build, per policy | 194.7 to 228 policies/s | — | **0.70x to 0.82x**: below, if the unit is policies | NFR-493 does not name this path; read per policy it is below the line |
| book build, per risk (two bundles) | 389 to 456 risks/s (2 x the policy rate, derived) | 1.40 M to 1.64 M | **1.40x to 1.64x above** | above the line, if each pass counts as a risk scored |
| NFR-504 shape, 850,000 x 2 passes | at 471.47/s | — | 1,700,000 / 471.47 = **60.1 min** against < 20 min (derived) | would need about 3 workers if linear; linear-in-workers is unmeasured (register F52, `CR-927` §10.4) |

The lead's 00:08:46 correction reads the build "below the 277.8 line IF NFR-493 governs that path". This is the case where the unit matters: by the text NFR-493 does not govern the build, and if it did, the build rates two risks per policy and passes. **The finding therefore does not report an NFR miss.** The planning-rate shortfall stands (about 3x on `score_batch`).

## Which path the exit demo uses (G2 text, quoted)

- `CR-1212:62-69` (G2): *"The exit demo is `WF-699` end to end on the freMTPL2 seed, with its deploy step. … Then comes a regression run (the Regression Suite), a dislocation run with attribution, and submission. … It runs from one command to a served page, in Phase 1b's form (`docs/roadmap.md:350`)."*
- `RL-1521` (`docs/rulings/RL-01521-…`, line 44-45): *"Verified at caa4e411: … CR-821 :17-19 'a scripted HTTP run of the core `WF-698` journey (`scripts/demo.py` with the full 678 013-row freMTPL2 seed), with the UI available for hands-on driving.' … Ruling: G2 is met by `scripts/demo.py`-style ONE command that runs WF-699 A–E and its deploy step over HTTP on the freMTPL2 seed and ends with the frontend SERVING …"*
- `PL-1544` Size (`:468-470`, `origin/main` at `docs/plans/PL-01544-…`): *"The one-command run is the full seed (`--rows 20000` in rehearsal; the full 678,013 rows on demo day)."*
- `WF-699` D6 (`docs/workflows/WF-00699-…:86`): *"`POST /dislocation-runs` against the current live version over the portfolio."* E3/E4 (`:97-98`): the first submission is refused because the dislocation run is stale, and the actuary *"Re-runs dislocation, resubmits."*

**Reading, not inference beyond the quotes:** the governing texts say the demo runs on the **full 678,013-row seed on demo day**, and a **subset (`--rows 20000`) only in rehearsal**. They do not say what size the dislocation run's *portfolio Dataset Version* is. `PL-1544` names the portfolio only in row A3 (`:342`, "the portfolio's exposure weights"), with no row count. **Open point for the lead and the remedy plan: confirm in `scripts/demo.py` and the seed which size `POST /dislocation-runs` scores.** If it is the full seed, the exit demo's heavy path is the **dislocation run** (D6 and the E4 re-run, each two `score_batch` passes through the same pricing-core function the build uses), not a bare `score_batch`; the regression run's golden quotes are small; the deploy step scores one quote.

## What it affects

- **`PL-1452` Task 7 size.** 20,814,169 ratings: 4.09 h at 1,414.985/s (derived, `goB-readiness` `:153`) becomes **12.3 h** at 471.47/s (derived; the first draft's 12.03 h used 480.65). `LG 9478` projects the whole plan at about 12.8 h at N=5, past the 6 h STOP: the reason R2 exists.
- **`PL-1452` DP-S3-10 (a)**, about 407 M ratings, "≈ 80 exclusive worker-hours at P9's rate": about **240 h** at 471.47/s (derived).
- **G2's rehearsal arithmetic.** At the derived full-book figure, one dislocation run on the 678,013-row book is about **50 to 58 min** of build-path compute (derived), and `WF-699` E3/E4 asks for a re-run: about **100 to 116 min** of dislocation compute in one demo, each at about **20 GiB** peak on a 31 GiB box that also hosts the API, Postgres and the frontend. `WF-699`'s own "30–60 min" for Phase D is for 1.28 M policies and is not met at these rates either (1.28 M / 228 per s ≈ 94 min, derived).
- **Not affected, by scope:** NFR-489 (the `/score` request path, `SL-1455`) is a per-request latency budget. The demo's single-quote score at deploy is that path.

## Disposition (proposed; the lead decides)

**Severity: MEDIUM, proposed** (the first draft proposed LOW). Reasons, each from the evidence: (1) no NFR floor is breached on the governing path (`score_batch` 1.69x above, measured), and nothing misprices, so it is not HIGH; (2) the planning input was about 3x off and the full-book cost at demo size is derived at about 50 to 58 min per dislocation pass (76 to 82 min with a `score_batch` pass) and about 20 GiB, which lands on a dated gate (G2, with a re-run step in the journey) rather than only on a plan; (3) the cause is unseparated (the build's two-pass structure is a code reading, the memory split is unmeasured), so a remedy cannot yet be sized. It falls to LOW if the maintainer rules that the exit demo's dislocation run scores a subset, and rises to HIGH if the full-book run fails on memory or exceeds the demo's window when first run end to end.

**Owner: WK-1178** (the P2 standing-maintenance Work), as a new slice placed before `SL-1526` in the exit-demo chain (the lead's plan `PL 9447` / row `SL 9448` in draft). **Not `SL-1455`** (NFR-489, a different path).

**Event that next confirms or discharges it:** the remedy slice's profiling spike on the path the demo uses (hypothesis first: per-policy memory from `.collect()` materialisation and frame width; the build's cost as two `score_batch` passes plus a Python row loop), then a measured end-to-end dislocation run at a size the maintainer names. The `R2` full-book N=3 median is no longer expected: the full book did not complete in 60 min (two attempts, above).

**Remedy: none applied; none proposed in code here.** The planning inputs (`PL-1452`, the dispatch record) are frozen; the correction is this record's measured figures.
