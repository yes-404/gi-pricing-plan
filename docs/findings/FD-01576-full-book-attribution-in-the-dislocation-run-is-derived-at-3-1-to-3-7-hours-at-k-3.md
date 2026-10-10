---
id: FD-1576
family: finding
title: Full-book attribution in the exit demo's dislocation run is derived at 3.1 to 3.7 hours at K = 3 (doubling per extra change group), with no budget in any spec and the handler attributing the whole portfolio synchronously
status: active
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: auditor
tree: 61e2a8d9d06087cadd3760e9668b3caff881b85c
corrected_by: []
relates: [WK-673, WK-1178, SL-1387, SL-1388, PL-1452, PL-1544, FD-1573, LG-1545, FR-263, FR-266, FR-1397, FR-1399]
---

# FD-1576 — Attribution over the full book: measured on 20,000 and 100,000 policies, derived for 678,013

*Disclosure: drafted under working id 9451; minted as FD-1576 on 2026-10-10, in the D5 batch mint PR.*

**DRAFT.** Filed on `draft/fd-9451`, no PR, at the lead's ruling (`to-lead.md`, "2026-10-10 00:20:03 BST — RULINGS on the FD 9446 remedy plan …" [FD 9446 is minted as FD-1573], the NEW RISK item: a separate FD, not folded into `PL-1574`). **Every figure marked "measured" is a line in `~/gi-pricing-plan.local/task7-s3e/out/` (local, named below) or in `LG-1545` on `origin/sl-1387-attribution-exact-shapley-largest-remainder`. Every figure marked "derived" is the auditor's arithmetic from those lines and is not a measurement; per `PL-1452` DP-S3-10 (b) there is no NFR verdict from a derived figure.** No full-book attribution run was made.

## Finding

The exit demo's dislocation job (`dislocation.run`, `SL-1388`) calls `attribute(...)` once, synchronously, over **every row** of the portfolio Dataset Version, at a K equal to the number of change groups. Attribution re-rates the portfolio 2^K times. Measured on 20,000 policies, K = 3 takes a median 366.9 s; the cost is linear in policies (100,000 policies took 5.41x for 5x), so the full 678,013-row book is **derived at 3.1 to 3.7 hours at K = 3**, and about **twice that per extra group** (K = 4: 6.9 h; K = 5: 14.4 h; K = 6: 28.5 h, all derived). No FR or NFR gives attribution or the dislocation run a time budget, and `WF-699` Phase D budgets "30–60 min compute" for dislocation as a whole. `WF-699` E3/E4 asks for a re-run, so the demo's compute is derived at twice the figure. The finding does not say the engine is wrong: attribution is exact (`FR-266`, `FR-1397`) and the cost is the 2^K re-rates `FR-266` specifies. It says the spec, the plan and the handler do not bound a cost that is hours at demo-day size.

## The code path (read at `origin/sl-1388-wk673-s4-backend-job-routes`, `8af8a9b4`)

`backend/src/app/worker/dislocation_handlers.py` — the portfolio is read whole (`:201-208`) and both calls take the same lazy frame:

- `:222` `lazy = loaded.portfolio.lazy()`
- `:223` `frame = dislocation_frame(loaded.baseline_bundle, loaded.candidate_bundle, lazy, spec)`
- `:231` `attribute(loaded.baseline, loaded.candidate, lazy, spec, loaded.resolver)` (inside `asyncio.run(`, `:230`, after `progress.update(0.5, "attributing")` at `:228`; `progress.update(0.9, "persisting")` follows at `:235`)

**Over what:** `lazy` is `pl.read_parquet` of the whole stored table of `spec.portfolio_dataset_version_id` (`:195-208`). `attribute` (`packages/pricing-core/src/pricing_core/rating/analysis.py:972`) takes `portfolio: pl.LazyFrame` and has no row sample: a grep for `sample` in that file finds only `ErrorSample`, `_SAMPLE_SIZE` for error examples and `_ORDERS_SAMPLED` (a count of Shapley orders, not rows) — this is `planner-r6`'s reading (`~/gi-pricing-plan.local/handover/r6-portfolio-size-2026-10-10.md`, (b)), and I read `attribute`'s signature and body head at the same tree.

**With which K:** `k = len(groups)` (`analysis.py`, in `attribute`), where `groups = _check_groups(changes, spec.change_groups)`: the analyst's declared `change_groups` (`DislocationSpec.change_groups`, `Field(max_length=6)`, `model_schema/dislocation.py:47`) or, where none are declared, the derived changes one per group. `shapley = k <= _MAX_SHAPLEY_GROUPS`; above 6 ungrouped changes the order-dependent method runs instead (`FR-266`). `masks = _masks_to_rate(k)`: every subset bundle is compiled before any is rated, then rated. The request does not carry K as a field; it follows from the two Rating Versions and the groups. `WF-699` D7 (`:87`) names three effects for the demo: "peril-structure, rate-table, and minimum-premium effects", so **K = 3 is the demo's reading by the workflow text** (the fixture of `examples/fremtpl2/rating/` has K = 3 to 6 members by design of `LG-1545`; the demo's K is not otherwise fixed by a text I found).

## Evidence

*What was measured.*

All runs: `scripts/measure-attribution-cost.py cost` via `~/gi-pricing-plan.local/task7-s3e/inv.sh`, alone in the gate-1 slot, **8 CPUs, 31 GiB**, fixture `examples/fremtpl2/rating/`, the **first 20,000 policies by `quote_id`** except the linearity row. Tree `f59b546e748eca464c279a77ca48e166689d5a0e` unless stated; K = 3 runs r1 to r5 ran at `7dba2d11`/`59e24c85` (per `LG-1545`), and `git diff --name-only` between those trees and `f59b546e` lists only `docs/ledgers/LG-01545-…` (the measured code is the same; `LG-1545` records the trees, I did not re-run the diff for `59e24c85`). load1 is the reading at the run's emit (`.jsonl`), the START and END readings are in `progress.log`.

| file | K | policies | N | seconds | load1 (emit) | tree |
|---|---|---|---|---|---|---|
| `23-k3-r1..r5.jsonl` | 3 | 20,000 | 5 | 372.20, 364.28, 351.89, 400.11, 366.85; **median 366.85** | 2.85, —, —, —, — (END 1.92, 1.92, 2.60, 1.80 per `LG-1545`) | `59e24c85` / `7dba2d11` |
| `24-k4-r1..r5.jsonl` | 4 | 20,000 | 5 | 742.40, 768.35, 702.56, 734.73, 733.90; **median 734.73** | END 1.96, 1.55, 2.72, 1.85, 2.07 | `59e24c85` |
| `25-k5-r1.jsonl` | 5 | 20,000 | 1 | **1,527.04** | 2.41 | `f59b546e` |
| `26-k6-r1.jsonl` | 6 | 20,000 | 1 | **3,024.77** | 1.78 | `f59b546e` |
| `40-lin-r1.jsonl` | 3 | **100,000** | 1 | **1,983.42** | 2.29 | `f59b546e` |

The K = 3 first-run line (`23-k3-r1.jsonl`) carries load1 2.85 and tree `59e24c8576768073daba10db5d7259d21b15a4c6`; the K = 3 median is `LG-1545`'s ("Task 7 run — … K = 3 block result (b)"). Ratios to the previous K: 2.00 (K = 4), 2.08 (K = 5), 1.98 (K = 6), against 2.0 expected. **Spread:** K = 3 351.89 to 400.11 s (±7% of the median) and K = 4 702.56 to 768.35 s are N = 5; K = 5, K = 6 and the linearity point are one run each and show no spread.

**Linearity check (100,000 policies, K = 3, N = 1):** 1,983.42 / 366.85 = **5.41x for 5.00x policies**, 8% above linear. That is inside the K = 3 band scaled by five (1,759 to 2,001 s), so it is neither evidence of super-linearity nor against it. Measured only to 100,000 policies; extrapolation to 678,013 (6.78x of 100,000) is untested.

**What the figures under-state** (`LG-1545`, "What the measured cost under-states"): the fixture rates through `table` lookups, which are cheaper per rating than a `model_call`; the model-reference and model-artifact hydrate paths are not exercised. The seconds per rating here are a lower bound for a portfolio rated through a real model. Memory of the attribute runs was **not measured** (only `score_batch` was, 6.21 GiB at 200,000 and 11.94 GiB at 400,000 policies, `FD-1573`).

## The derived full-book cost at K = 3 (derived, not measured)

Three derivations, over 678,013 policies (the full seed's row count; `planner-r6` computes v2 as 677,442 after the 571 dropped rows, a 0.1% difference that moves no figure below by more than 0.005 h):

| derivation | arithmetic | seconds | hours |
|---|---|---|---|
| 2^K x policies / score rate, with the first probe's rate 480.65 policies/s (`LG-1545`, rate probe) | 8 x 678,013 / 480.65 | 11,285 | **3.13** |
| the same with the 20,000-policy rate 485.76/s (the `derived` line of `23-k3-r1.jsonl`, `formula 2^K * 678013 / rate`) | 8 x 678,013 / 485.755 | 11,166 | **3.10** |
| the same with the 400,000-policy rate 471.47/s (`FD-1573`, `60-sb-400k`) | 8 x 678,013 / 471.47 | 11,505 | **3.20** |
| linear in policies from K = 3 at 20,000 (median 366.85 s) | 366.85 x 678,013 / 20,000 | 12,437 | **3.45** |
| linear in policies from the 100,000-policy point | 1,983.42 x 678,013 / 100,000 | 13,448 | **3.74** |

Range **3.10 to 3.74 h**; `LG-1545` states "3.1 to 3.7 h". The first three are rate-based (they treat attribution as 8 passes of `score_batch` at the measured rate) and the last two are scaled from measured attribution runs; the measured attribute runs cost more than the rate-based figure (366.85 s against 8 x 20,000 / 485.76 = 329 s), so the scaled figures are the better-founded pair. **How it grows with K (derived, scaled from the 20,000-policy medians by 678,013 / 20,000 = 33.9):** K = 3 3.45 h, K = 4 6.92 h, K = 5 14.38 h, K = 6 28.48 h. About 2x per extra group; the K = 6 ceiling of the Shapley method is derived at more than a day.

The dislocation step itself (`dislocation_frame` at `:223`) is `FD-1573`'s book build, derived there at 50 to 58 min for the same book. It runs before attribution in the same job. The job total at K = 3 is therefore derived at about 4.3 to 4.7 h (3.45 to 3.74 h plus 50 to 58 min; the two may share work, which is not measured).

## What governs it

- **`FR-263`** (`docs/specs/03-rating-engine.md:188`, no dated amendment on the row): the run's content. States no time or throughput budget.
- **`FR-266`** (`:191`, amended 2026-10-03): the attribution of record is exact Shapley over K <= 6 groups, from "the 2^K subsets S"; states the method and the K limit, **no time or cost bound**. **`FR-1397`** (`:192`, exact reconciliation) and **`FR-1399`** (`:194`, grouping): exactness and grouping. None states a budget.
- **No NFR** names attribution or the dislocation run. Grep, run at `origin/main` `61e2a8d9`: `git -C /home/puzhenhao1989/gi-pricing-plan grep -n -iE 'attribution' origin/main -- docs/specs | grep -iE 'NFR-|budget|minutes|within|< [0-9]'` returns **no line**; the NFR rows of `03` §8 (`NFR-489` to `NFR-502`, `:1386`-`:1399`) were read: `NFR-493` ("Batch scoring ≥ 1 M risks/hour per worker") governs `score_batch` (`FD-1573`), `NFR-489` the `/score` request path, and none names a dislocation or attribution job. `LG-1545`'s Task 7 Step 4 proposes an attribution NFR text ("a dislocation attribution over K change groups re-rates the portfolio 2^K times …") **for the decision-maker**; it is a proposal in a ledger on the unmerged `sl-1387` branch, not a requirement, and the spec diff `origin/main...sl-1387` on `docs/specs/03-rating-engine.md` adds none (`git diff origin/main...origin/sl-1387-attribution-exact-shapley-largest-remainder -- docs/specs/03-rating-engine.md | grep -E '^\+' | grep -iE 'seconds|hours|budget|NFR'` matched only `attribute`'s paragraph, which I read for a time or cost bound and found none; the same diff filtered on `budget|NFR-` returns 0 lines).
- **`WF-699:150`** (phase table): "D — Regression + dislocation | 30–60 min compute; hours of review". A workflow estimate, not an NFR. **`WF-699:87`** (D7) sizes the run at "1.28 M policies", which is not the freMTPL2 seed's 678,013 rows (`planner-r6`); the estimate is for a book about twice the seed and is already derived as unmet at `FD-1573` (1.28 M / 228 per s ≈ 94 min).

## The exit demo's impact

- **Which steps run attribution.** `WF-699` D6/D7 (`:86-87`): `POST /dislocation-runs` against the live version over the portfolio, with **attribution**; E3/E4 (`:97-98`): the first submission is refused because the dislocation run is stale, and the actuary "Re-runs dislocation, resubmits." The run is one job; attribution is its step from `0.5` to `0.9` of the progress.
- **Which size.** `planner-r6`'s answer (`~/gi-pricing-plan.local/handover/r6-portfolio-size-2026-10-10.md`): **no text fixes the D6 portfolio**; the run "dislocates and attributes every row" of the Dataset Version the request names, there is no sampling, `--rows` sizes the seed's Dataset Versions, and `PL-1544` makes demo day the full seed (`:468-470`: "`--rows 20000` in rehearsal; the full 678,013 rows on demo day"). By implication the demo attributes the full book (v2, 677,442 rows by `planner-r6`'s arithmetic). "Not fixed by any text" is the answer I cite; the implication is theirs, not a quoted figure.
- **Demo arithmetic (derived).** One attribution at K = 3 on the full book: 3.45 to 3.74 h. D6 plus E4: **6.9 to 7.5 h** of attribution compute alone, plus the dislocation build's derived 50 to 58 min each time (`FD-1573`). `WF-699` Phase D's "30–60 min" is exceeded by a factor of about 7 to 8. `PL-1544` calls the demo "one command to a served page" and its gate G2 (`CR-1212:62-69`, quoted in `FD-1573`) lists "a dislocation run with attribution" in that command; the plan has no row bounding its time. Rehearsal at `--rows 20000` runs the same attribution in 366.85 s at K = 3 (measured), so **a rehearsal passes and demo day does not**: the cost is invisible at the size the plan rehearses.
- **Is there a way out in the texts?** The synchronous `asyncio.run(attribute(...))` is a single Job step with no sample, no portfolio cap and no K cap below 6 (the handler `PlatformError`s only on `AttributionError`). The ways out are design choices the specs leave open (a demo-day subset portfolio Dataset Version, a persisted precomputed run, fewer groups, the order-dependent method above K = 6, a faster subset valuation, parallel workers); this record picks none (`CLAUDE.md` §0, §10).

## Disposition

*Proposed; the lead decides.*

**Severity: HIGH, proposed.** Reasons: (1) the demo's own texts put the full book on demo day (`PL-1544`), the handler has no bound, and the derived cost (3.1 to 3.7 h, 6.9 to 7.5 h with E4's re-run) is a multiple of the only time the workflows give (30 to 60 min), so the scripted journey as written cannot finish in a demo-sized window; (2) it lands on a dated gate (G2) and the rehearsal size hides it; (3) no requirement bounds it, so nothing would make a slow run a defect by the specs; (4) it grows 2x per group, so a K = 4 or 5 demo fixture is worse. Not misclassed as pricing-incorrect: attribution is exact and nothing misprices. It falls to **MEDIUM** if the maintainer rules that the demo's portfolio Dataset Version is a subset or the run is precomputed (the texts then bound it), and it stays HIGH if the demo attributes the whole seed live. **The derived figures are not an NFR verdict**; the first measured full-book (or 100,000-policy-scaled) end-to-end run is what would settle it, and `FD-1573` notes that a measured full-book score pass did not finish within 60 minutes.

**Owner: WK-673, proposed** (S3 delivered `attribute` and its cost-bound decision, `LG-1545` Task 7 Step 4; S4 owns the handler that calls it unbounded). The demo-size decision (R6) and the demo script are `WK-1178`'s (`PL-1544`), so the remedy plan `PL-1574` is where the choice is made; this record is not folded into it (the lead's ruling). **Event that next confirms or discharges it:** the maintainer's ruling on the demo's portfolio size and attribution mode (recorded as an `RL-`), then a measured attribution run at the chosen size and K on the demo box.

**Remedy: none applied; none proposed in code here.** Options belong in `docs/open-questions.md` or the remedy plan, not in a silent pick.

## Not checked

- No attribution run beyond 100,000 policies and none on the full book; memory of the attribute runs; the cost through a `model_call` (the fixture is table-based); whether the book build and the attribution share any work in one job.
- `FR-1397` and `FR-1399` row text beyond the lines above (read for their subject, not for any budget clause; the grep above found none).
- The S4 request schema's handling of `portfolio_dataset_version_id` beyond `planner-r6`'s read.
