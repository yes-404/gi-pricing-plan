---
id: FD-9446
family: finding
title: score_batch measured at 480.65 policies per second on the freMTPL2 model_call algorithm, 2.94x below the 1,415 policies per second the SL-1387 plan and dispatch book from CR-927's 5,093,947 risks per hour
status: draft
created: 2026-10-09
owner: auditor
tree: 088a0c2346b2d4600002aaef69827316f53e8e4f
corrected_by: []
relates: [WK-673, WK-1178, SL-1387, PL-1452, CR-927, NFR-493, NFR-504, LG-9478]
---

# FD-9446 — The measured `score_batch` rate is 2.94x below the planning rate

**DRAFT.** Filed on `draft/fd-9446`, no PR, at the lead's ruling (`to-lead.md`, "2026-10-09 16:12:53 BST — RULING: Task 7 reduced design = R2 …", item 4). The figure below is **one run, a probe**. The R2 full-book N=3 median replaces it when it lands (a dated line, appended here then, not before).

## Finding

SL-1387's Task 7 (`PL-1452`, DP-S3-10) was sized on a throughput that was never measured on this workload. `PL-1452` P9 (`:326`, at `origin/main` `61e2a8d9`) reads: *"NFR-493's only recorded throughput is 5,093,947 risks/hour/worker (`CR-927` §10.4, an older tree, 300,000 rows); it is a planning estimate here, not a measurement (DP-S3-10)."* The dispatch record books Task 7 at "20,814,169 ratings, ≈ 4.09 h single-worker at P9's planning rate (goB §5)" (`~/gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1387-2026-10-08.md:114`; the same arithmetic is `~/gi-pricing-plan.local/handover/goB-readiness-2026-10-08.md:152-153`).

Task 7's first measurement of `score_batch` on the freMTPL2 `model_call` algorithm (the algorithm `PL-1452` P8 / DP-S3-6 requires, built by Task 7) gave **480.65 policies/s**. The planning rate in the same unit is 5,093,947 / 3600 = **1,414.99 policies/s**. (The brief and the ledger say "1414": that is the truncation of 1,414.985; rounded it is 1,415. The ratio is **2.94x** either way: 1,414.985 / 480.652 = 2.944; "2.9x" in `LG-9478`.)

Two things differ between the planning figure and the measurement, and the probe cannot separate them: (1) the workload (`CR-927` §10.4: Task 3D, "real Postgres/MinIO I/O, 300,000 rows" through the handler, a different algorithm; Task 7: `score_batch` over freMTPL2 policies with a GLM `model_call`); (2) the tree (`CR-927`'s is "an older tree"). **This finding does not say the engine regressed.** It says the planning rate does not transfer to this workload and every figure derived from it is short.

## Evidence — the measurement, verbatim

Source: `LG-9478`, section "Task 7 run — block 1 stopped, the rate probe (2026-10-09, executor-s3e)", on `origin/sl-1387-attribution-exact-shapley-largest-remainder` @ `7dba2d11c55d6d8c704cac2dabf52f9dcf7bbf09`, bullet "(i) Rate probe"; and the raw files `~/gi-pricing-plan.local/task7-s3e/out/progress.log` and `10-rate-probe.jsonl`.

**Tree.** The measured code is commit `088a0c2346b2d4600002aaef69827316f53e8e4f` (tree `f9807920ca5029afb8bff8fea7ec73250311cd1f`), which is what the jsonl `"tree"` field records and what `LG-9478` names ("at tree `088a0c23`"). `7dba2d11` is the branch tip that carries the ledger entry; `git diff --stat 088a0c23 7dba2d11` is one file, the ledger, +16 lines, so the measured code is the same at both.

**Command** (`progress.log`, line "START 10-rate-probe", 15:57:23 BST; the wrapper is `~/gi-pricing-plan.local/task7-s3e/inv.sh`, which runs `timeout 3600 uv run --directory <sl-1387 worktree> python <sl-1387 worktree>/scripts/measure-attribution-cost.py "$@"`):

```
cost --policies 20000 --score-policies 50000 --ks 3 --runs 1
```

**Result lines** (`10-rate-probe.jsonl`, abridged to the fields used; the file has three lines):

```
{"what": "score_batch", "k": 0, "policies": 50000, "seconds": 104.02534730499974, "runs": [104.02534730499974], "policies_per_s": 480.65208427904827, "load1": 2.56, "tree": "088a0c2346b2d4600002aaef69827316f53e8e4f", "stamp": "2026-10-09T15:05:28+00:00"}
{"what": "attribute", "k": 3, "policies": 20000, "seconds": 363.91835524400085, "runs": [363.91835524400085], "load1": 2.11, "tree": "088a0c2346b2d4600002aaef69827316f53e8e4f", "stamp": "2026-10-09T15:11:32+00:00"}
```

| item | value | source |
|---|---|---|
| `score_batch` policies | 50,000 (1 run) | jsonl line 1 |
| `score_batch` wall | 104.03 s (104.02534730499974) | jsonl line 1 |
| rate | **480.65 policies/s** (480.65208427904827) | jsonl line 1; 50,000 / 104.0253 re-divided = 480.65 |
| load1 | START 1.43 (15:57:23 BST), at the `score_batch` line 2.56, END 2.11 (16:11:32 BST), rc 0, wall of the invocation 14m09s | `progress.log`; jsonl |
| K=3 attribute | 363.92 s on 20,000 policies, 1 run (8 re-rates x 20,000 = 160,000 ratings, 440 ratings/s) | jsonl line 2; `LG-9478` |
| setup inside the invocation | about 8 min before the first score (portfolio build, compile): not a rating cost | `LG-9478` |

**Disclosure.** From about 15:2x BST three authoring seats ran small single-file tests beside the run (nice 19, one at a time, at most 2 min each; the lead's ruling at `to-lead.md` 15:22:26 BST, item 3). The probe therefore did not run on an idle box; load1 stayed at or below 2.56 on an 8-CPU machine in the three readings that exist. A load that low would not by itself explain a factor of 2.94, but no idle-box repeat exists yet.

**Context.** The first attempt, block 1 (`--score-policies 678013 --runs 5`, tree `088a0c23`), was stopped by the lead at 15:56:31 BST after 1 h 54 m 13 s with no output line (`rc=143`, `progress.log`); `cmd_cost` emits only after all runs. It gives no figure. It is consistent with the probe: five passes at the probe rate are about 118 min.

**Later dated line (not yet written):** the R2 full-book N=3 median replaces the 480.65 figure here when it lands.

## What it affects

All "derived" below are the auditor's arithmetic from 480.652 policies/s, linear in ratings, and are not measurements; per `PL-1452` DP-S3-10 (decided (b), 2026-10-05 13:20:26 BST, item 24) *"no NFR verdict from a derived figure"*.

- **`PL-1452` Task 7 size.** 20,814,169 ratings: 4.09 h at 1,414.985/s (derived, `goB-readiness` :153) becomes **12.03 h** at 480.652/s (derived). `LG-9478` projects the whole plan at about 12.8 h at N=5, "past the 6 h STOP of the brief" — the reason R2 exists.
- **`PL-1452` DP-S3-10 (a), the rejected full design:** about 407 M ratings, "≈ 80 exclusive worker-hours at P9's rate" becomes **about 235 h** (derived). The rejection of (a) in favour of (b) holds with more force.
- **NFR-493** (`03` `:1390`, "Batch scoring ≥ 1 M risks/hour per worker (NFR-455), linear in workers"). 480.652 x 3600 = **1,730,347 risks/hour** (derived): still above the 1 M floor, **1.73x**, not 5.09x. **The floor is not breached by this probe**, so this is not an NFR miss. What changes is the headroom `CR-927` §10.4 reports ("PASS, 5.09×", `CR-927` `:355`, a verdict that stands for what it measured). The linear-in-workers clause is still "NOT MEASURED" (`CR-927` §10.4; register F52).
- **NFR-504** (`04` `:431`, a GIPP check over 850 k renewals, "two full batch scoring passes — NFR-493", < 20 min). 1.7 M risks at 5,093,947/h is 20.02 min on one worker (already at the edge); at 1,730,347/h it is **58.9 min** (derived), so about 3 workers are needed before the budget is met, **if** scaling is linear, which is unmeasured (F52). A plan that sized NFR-504 on one worker at the CR-927 rate would be short by the same 2.94x.
- **Not affected, by scope:** NFR-489 (the `/score` request path, `SL-1455`) is a per-request latency budget, a different quantity; this finding does not measure it.

## Disposition (proposed, the lead decides)

**Severity: LOW, proposed.** Reasons: no NFR floor is breached by the figure; no mispricing and no data path is touched; the harm is a planning input that was 2.94x off and has already cost a re-plan of Task 7 (the R2 reduction), which the ruling above has handled. It is not MEDIUM now because the probe is one run on a shared box and the cause (workload, tree or load) is unseparated. **Re-rate when the R2 N=3 median lands:** a rate below 277.8 policies/s (NFR-493's floor in this unit: 1,000,000 / 3600) is an NFR-493 miss and the finding becomes HIGH; a rate near 480/s keeps LOW, or MEDIUM if the lead weighs the NFR-504 headroom (about 3 workers needed, above) as a budget risk.

**Owner: WK-1178 proposed**, as the P2 standing-maintenance Work that carries the NFR slices. **Not `SL-1455`**: its row (`docs/roadmap.md` `:1637`) is "NFR-489: the /score request path meets its p99 budget at 25 to 200 rps", a different NFR and a different path; a batch-throughput finding there would widen it. The lead's brief says "likely the WK-1178 NFR slice alongside SL-1455"; the primary source supports the Work, not the slice. A new WK-1178 slice for NFR-493/NFR-504 (the F52 linearity measurement is the natural pair) is the shape; none exists at `origin/main` `61e2a8d9`. Rides D5 or the next batch; it does not hold S3.

**Event that next confirms or discharges it:** the R2 full-book N=3 median in `LG-9478` (confirms or revises the rate); then a WK-1178 slice measuring NFR-493 on the shipped algorithm with the linear-in-workers clause (discharges, F52).

**Remedy: none applied; none proposed in code.** The planning inputs to correct are frozen (`PL-1452`, the dispatch record); the correction is the ledger's measured figure.
