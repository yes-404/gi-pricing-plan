---
id: LG-8125
family: ledger
title: WK-1178 slice SL-1575 — FD-1573, dislocation_frame's memory and time at book scale (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-18
owner: executor
tree: 50476d3f5ef181453b890196ec9637306df4b81e
phase: P2
work: WK-1178
slice: SL-1575
plans: [PL-1574]
corrected_by: []
relates: [PL-1574, SL-1575, SL-1387, FD-1573, NFR-493]
---

# LG-8125 — WK-1178 slice SL-1575: FD-1573, dislocation_frame's memory and time at book scale

Filed 2026-10-18 under working id 8125 (lead-reserved in eta.md); executed by `exec-1575`, base `origin/main` `84b0ff5765e55bc8edd139cd22bb57cd474de807`, branch `sl-1575-wk1178-dislocation-memory`.

**GO:** the maintainer's entry "2026-10-18 22:50:32 BST — Maintainer: the duplicate-mint anomaly ruled; GO SL-1259, SL-1770, SL-1738, SL-1575 (with conditions)"; for this slice: "SL-1575 (PL-1574, the FD-1573 HIGH remedy). GO; Acceptance 5 split per checkpoint Q1 (the 20k sample here, the full book on nfr-bench-1 when it exists)."
**Activation need "FD-1573 minted with HIGH":** met by the maintainer's entry "2026-10-10 21:36:36 BST", item 1: "SL-1575's 'minted HIGH' text predates R6 and is stale. That need is met by FD-1573 being minted at all." (FD-1573's severity is LOW, re-rated 2026-10-11.)
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Quoted from `PL-1574` (Tasks table, row 1):

| 1 | SL-1575 — WK-1178 fix slice — FD-1573: `dislocation_frame`'s memory and time at book scale | Task 0, the 1-hour profiling spike of `dislocation_frame` at 20,000 (Python heap) and 200,000 (RSS and time), with the H1 decision rule; then, only if H1 is confirmed, Task 1: `_score_pass` retains each rung's `(value_minor, unrounded_minor)` instead of the validated `LadderRung` objects; then Task 2, the after-measurement. **Out of scope:** `score_batch`'s per-row engine evaluation (its docstring: *"This is not genuine polars streaming"*, `score.py:1186-1234`); `attribute`'s 2^K re-rates (S3's code; see DP-1); any change to `03` text | `03` §8: NFR-493 (rated, not changed); `03` §3: FR-263 (output unchanged); `03` §8: NFR-495, NFR-496 (held) | WK-673 S3 (`SL-1387`) merged, because `analysis.py` and `measure-attribution-cost.py` are its write set; FD-1573 minted with HIGH; DP-1 to DP-3 ruled | B (recommended; see Sequencing) | ≈ 1.5 lane-days, derived (see Size) |

**Acceptance 5 split (checkpoint Q1, to-lead "2026-10-16 10:21:56 BST"):** "(A) 20,000 policies (PL-1574:150-151) in the slice's gate on THIS VM. (B) The full book (678,013 policies, 76–82 min, ~20 GiB, alone) is CARRIED to the dedicated host as OWED before the P2 close, owner = SL-1575's Work, recorded in its LG." Limb (B) is OWED: not run here.

### Task list

- [x] **Task 0 Step 1, harness:** `~/gi-pricing-plan.local/task-9447/spike.py`, the PL-1574 code block verbatim.
- [x] **Task 0 Step 2, smoke at 1,000 policies:** rc 0, 11 lines in the plan's stage order (`spike-1k.jsonl`; run at load1 4.23, outside a slot, accepted by the lead as a smoke).
- [x] **Task 0 Step 3, the two runs** (below).
- [x] **Task 0 Step 4, the decision rule** (below): H1 CONFIRMED.
- [ ] Task 1: `_score_pass` retains rung values, not `LadderRung` objects (H1 confirmed, so it applies).
- [ ] Task 2: the after-measurement and the gate.

### Gate

Not yet run.

### Audit

Not yet run.

### Build log

#### 2026-10-18 — Task 0, the profiling spike (tree `50476d3f5ef181453b890196ec9637306df4b81e`, i.e. 84b0ff57 plus the activation commit; `pricing_core` code identical to 84b0ff57)

Run as one job under `flock -w 1200 /tmp/slots/gate-1` with `GIP_GATE_SLOT=gate-1`, script `~/gi-pricing-plan.local/task-9447/run-step3.sh`, output `step3.out`; each run under `timeout 2700`, foreground. The freMTPL2 ARFF (git-ignored) was copied from the root checkout's `examples/fremtpl2/data/`.

| Run | START (load1) | END (load1) | rc |
|---|---|---|---|
| 20,000, `--tracemalloc` | 2026-10-18 23:04:08 BST (1.99; available memory 25 GiB) | 2026-10-18 23:07:20 BST (3.14) | 0 |
| 200,000 | 2026-10-18 23:07:20 BST (3.14, carried from the 20k run just before) | 2026-10-18 23:24:34 BST (2.81) | 0 |

**Load, per the lead's note (2026-10-18 23:33:47 BST):** the box went to load1 about 3.2 during the runs (a `run-small` on small-test, and a docs block on gate-2 that ran beside this slot). Recorded load1: 1.99 at the job start, 3.14 at the 20k end and 200k start, 2.81 at the 200k end. No sampler ran, so the peak is not measured; the lead's reading is about 3.2. **Every TIME figure in this entry is LOADED, not quiet** (t_s, the 20k and 200k totals, the derived 58.3 min). The memory figures (VmHWM, tracemalloc) are load-insensitive and stand. **H1 rests on memory only**, so it stands. **H3 uses a within-run time ratio** (about 10 % against a 20 % threshold, both runs), which load scales on both sides; it is a ratio, but still loaded. **Acceptance 3 (the after time no slower than Task 0's) compares times**, so it needs a quiet re-run of the 200k leg for a clean before figure; the lead may grant one.

Conditions were load1 < 2.0 and available memory ≥ 12 GiB, checked at the START of the job. The load1 at the 200k START is the first run's own load, not another job's. Other seats were building (load1 about 3 at times), so the times are one run each, N=1, under that contention. Every time includes a `gc.collect()` at each mark. The 20k times also include tracemalloc overhead (20k: 189.3 s, about 106 policies/s; 200k, no tracemalloc: 1,032.4 s, about 194 policies/s).

**20,000 policies (Python heap, tracemalloc), `spike-20k.jsonl`:**

| Stage | t_s | VmHWM KiB | traced_current B |
|---|---|---|---|
| read_portfolio.start | 20.53 | 1,336,980 | 1,272,022 |
| pass1.score_batch.collected | 98.75 | 1,336,980 | 1,419,710 |
| pass1.retained | 107.27 | 1,336,980 | 273,153,609 |
| pass2.score_batch.collected | 178.70 | 1,336,980 | 273,154,541 |
| pass2.retained | 186.93 | 1,543,112 | 544,888,551 |
| dislocation_frame.returned | 189.33 | 1,543,112 | 1,413,669 |

**200,000 policies (RSS and time), `spike-200k.jsonl`:**

| Stage | t_s | VmHWM KiB |
|---|---|---|
| portfolio.loaded | 4.34 | 800,980 |
| pass1.score_batch.start | 4.93 | 800,980 |
| pass1.score_batch.collected | 431.65 | 1,208,800 |
| pass1.retained | 480.44 | 3,674,212 |
| pass2.score_batch.start | 486.01 | 3,674,212 |
| pass2.score_batch.collected | 967.96 | 3,978,908 |
| pass2.retained | 1,026.75 | 6,469,204 |
| dislocation_frame.returned | 1,032.39 | 6,469,204 |

**Step 4, the decision rule:**

- **R** = (traced_current at pass2.retained − at read_portfolio.start) / 20,000 = (544,888,551 − 1,272,022) / 20,000 = **27,181 B** per policy.
- **P** = VmHWM at dislocation_frame.returned × 1024 / 200,000 = 6,469,204 × 1024 / 200,000 = **33,123 B** per policy. **Caveat beside P:** `load_portfolio` reads the whole ARFF, which puts about 0.8 GB (800,980 KiB, about 4.0 KiB per policy at 200k) into VmHWM before `dislocation_frame` starts. P includes it.
- **H1 (retention) CONFIRMED:** R = 27,181 B ≥ 0.4 × P = 13,249 B (R/P = 0.82; against P less the load caveat, 0.94). The VmHWM steps agree: +2.47 million KiB at pass1.retained (1,208,800 → 3,674,212 KiB) and +2.49 million KiB at pass2.retained (3,978,908 → 6,469,204 KiB); the retained dict is built in the loop after each `.collect()`. Task 1 applies as written.
- **H2 (transient `.collect()`) not indicated:** the VmHWM step from pass2.score_batch.start to .collected is +304,696 KiB, far smaller than the two retention steps. (The rule reads "the largest single step"; the largest steps are the retained ones, not the collect.)
- **H3 (JSON/Pydantic re-parse ≥ 20 % of a pass) not indicated:** 200k: (480.44 − 431.65) / (480.44 − 4.93) = 10.3 %; 20k: (107.27 − 98.75) / (107.27 − 20.84) = 9.9 %. Both are below 20 %.
- **Derived full book** (not measured): 33,123 B × 678,013 = about 22.5 GB, about 20.9 GiB, which matches FD-1573's about 20 GiB. 200k time 1,032 s derives about 58.3 min for 678,013 at this rate.

## PRs

None yet.
