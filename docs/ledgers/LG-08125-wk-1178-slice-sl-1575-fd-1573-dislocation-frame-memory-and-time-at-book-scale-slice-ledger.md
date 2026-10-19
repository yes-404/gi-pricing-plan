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
- [x] Task 1: `_score_pass` retains rung values, not `LadderRung` objects (H1 confirmed, so it applies): commit `2ff1f69b`.
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

#### 2026-10-18 — Task 1, `_score_pass` retains rung values (commit `2ff1f69bc9e3bac3b3945065b6fb3fcd9c488253`, tree `c662ae07805719aaecefd98eff7f0cfdd289dc80`)

Files: `packages/pricing-core/src/pricing_core/rating/analysis.py`, `packages/pricing-core/tests/test_rating_dislocation.py`. Each run is the whole test file (42 tests) through `run-small.sh`, on this worktree.

- **Red first:** `test_dislocation_frame_retains_no_ladder_objects` failed on `assert all("ladder" not in v for v in quoted)`; the other 41 passed, `unchanged_on_the_fixture_book` included (1 failed, 41 passed).
- **Change:** `_RungValues`, `_rung_values`, `_origin_rung_of` as the plan gives them; `_origin_rung` delegates; `_score_pass` stores `"rungs"`; the row loop calls `_origin_rung_of`. After the change: 42 passed.
- **Plan deviation, disclosed:** the plan's fixture says both bundles differ in an `unrounded_minor` only. The `expense_direct="1.2"` candidate moves values too, so on its own it cannot fail the proof. The unchanged test therefore also compares a second candidate, `expense_direct="1.10001"` (default 1.1), measured to leave 880 of 2,000 policies with `change_minor == 0` and a non-null `origin_rung` (the `unrounded_minor` move alone).
- **Broken-input proof:** with the `if b[1] != c[1]: return name` branch deleted from `_origin_rung_of`, the file gave `1 failed, 41 passed`: `FAILED test_dislocation_frame_output_unchanged_on_the_fixture_book`, on `assert old.equals(new)`. The branch is restored (`diff` against the saved copy is empty).
- **Static checks:** `ruff check .` rc 0 ("All checks passed!"); `ruff format --check` on the two files rc 0; `mypy` (the configured `files`, which do not include tests) rc 0, "Success: no issues found in 243 source files". The test module's `_old_*` copy is formatted by ruff, and its names and `analysis.` qualifiers are the only edits from the base code.

#### 2026-10-19 04:33 BST — the QUIET 200k before-leg and the comparison rule for Task 2's after-leg

Source: the maintainer's entry "2026-10-19 04:31:13 BST — Maintainer: SL-1575 QUIET 200k before-leg END ruled + the comparison rule for Task 2" in `~/gi-pricing-plan.local/channel/to-lead.md` (local, not in the repository), read by the executor.

**QUIET before-leg** (protocol `scratch/sl1575-quiet.sh` v2, sha256 `3d050ea80ce6fe3a7624e7c8b02428b6a7027fef0329860b3cba367954e93084`; output `~/gi-pricing-plan.local/scratch/sl1575-quiet/spike-200k.jsonl`; run START 03:11:51Z, END 03:30:36Z): load1 at START 1.47 (END load3 1.53 2.45 2.47); `dislocation_frame.returned` t_s **1116.35 s**; VmHWM **6,385,760 KiB**; rows 200000; rc 0. Both legs are on the base code (before Task 1).

| Before-leg | load1 | `dislocation_frame.returned` | VmHWM KiB | rc |
|---|---|---|---|---|
| Task 0, LOADED (above) | 3.14 | 1,032.39 s | 6,469,204 | 0 |
| QUIET (this entry) | 1.47 | 1,116.35 s | 6,385,760 | 0 |

The QUIET leg is **8.1 % slower** than the LOADED one; peak memory agrees within **1.3 %**. Run-to-run time noise on this box is therefore at least 8 %, larger than the load effect; peak memory is the stable quantity.

**Binding comparison rule for the after-leg (quoted from the entry):**
- "(a) the after-leg uses the SAME protocol (sl1575-quiet.sh v2, quiet wait, both slots, same command);"
- "(b) a **memory** claim (VmHWM) may rest on ONE quiet after-run against this before-leg, if the change exceeds 3× the observed 1.3% spread (> ~4%);"
- "(c) a **time** claim needs ≥ 2 quiet runs per leg (this before-leg + one more, and 2 after), reported as both values per leg, and an improvement larger than the larger leg's spread. Otherwise the time result is "within noise", not a gain."

**Acceptance line this maps onto** (`PL-1574`, `docs/plans/PL-01574-…-single-row-work-plan.md:145-146`): "4. **Time is measured, not asserted**: the same run's `dislocation_frame` wall time at 200,000 is no more than Task 0's (a slower fix fails this item)." **It is time-based**, so under rule (c) **a second quiet before-leg is owed** before Task 2's after-run (two quiet runs per leg), and the after-leg needs two quiet runs. Item 3 (`:141`, memory) is a memory claim and falls under rule (b): one quiet after-run against the leg above, if VmHWM drops by more than about 4 %. Task 2 has no code change of its own (`PL-1574:478-484`: after-measurement, then the gate); the code of Task 1 (`2ff1f69b`) is already on the branch.

**Stage breakdown, QUIET against LOADED, as observed and UNEXPLAINED (no causal claim).** Figures read from `spike-200k.jsonl` (QUIET) and the Task 0 table above (LOADED):

| Interval | LOADED | QUIET | QUIET − LOADED |
|---|---|---|---|
| `pass1.score_batch.collected` t_s | 431.65 s | 538.17 s | +106.52 s |
| pass1 scoring, start → collected | 426.72 s (431.65 − 4.93) | 530.05 s (538.17 − 8.12) | +103.33 s |
| pass2 scoring, start → collected | 481.95 s (967.96 − 486.01) | 455.36 s (1,055.11 − 599.75) | −26.59 s |
| `dislocation_frame.returned` t_s | 1,032.39 s | 1,116.35 s | +83.96 s |

The lead's relayed pass2 figures (455.36 against 487.51) do not match the LOADED table: 967.96 − 486.01 = 481.95, so the pass2 difference is −26.59 s, not −32 s. Pass1 scoring was slower and pass2 scoring faster in the quiet leg, which is not what a load effect alone would suggest; it is recorded as run-to-run variance, which the rule above covers: time claims need at least 2 runs per leg, and memory is the stable metric.

## PRs

None yet.
