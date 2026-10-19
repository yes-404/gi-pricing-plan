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

#### 2026-10-19 04:34 BST — the maintainer's interpretation of acceptance 3/4 and the decision rule for the QUIET block

PL-1574 is frozen, so what follows is an **interpretation** of its acceptance items 3 and 4, not an amendment; it rides D26 as an RL. The maintainer's entry in `to-lead.md`, quoted in full:

> **2026-10-19 04:34:00 BST — Maintainer: SL-1575 acceptance 3/4 — interpretation and decision rule (PL-1574 is frozen: this is an interpretation, recorded in LG 8125; it rides D26 as an RL)**
> - **Correction accepted:** pass2 −26.59 s, not −32 s. The FINAL 12 addendum is right to fix it.
> - **Item 4's "Task 0's" (PL-1574 :145-146) = the QUIET before-legs** on 50476d3f under the v2 protocol: the 04:11 leg (1116.35 s) plus before #2. Task 0's LOADED leg (1032.39 s) is the measurement the QUIET re-run was ordered to replace; it is recorded, not compared against.
> - **Decision rule for item 4** (B1, B2 = before-legs; A1, A2 = after-legs at e73ecd65 or the final head):
>   - **PASS** if mean(A) ≤ max(B1, B2);
>   - **FAIL** ("a slower fix") if min(A) > max(B1, B2);
>   - otherwise **INCONCLUSIVE**: one more B and one more A in the same block, then re-apply.
>   - Report all four values plus the mean and the spread.
> - **Item 3 (memory, :141):** decided on VmHWM from the same block. ONE after-run suffices if it falls > ~4% below the before-legs' mean. Otherwise report the change as within noise, against the item's own wording.
> - **Order accepted:**
>   1. SL-1770's 6.2 re-gate (script for GO);
>   2. one QUIET block of B2, A1, A2, each ALONE, in one window, ABAB-adjacent order **B2 → A1 → A2** (two worktrees prepared before the first START);
>   3. then acceptance 5 (R6-size under inv-rss.sh, alone);
>   4. then the full gate on the final head.
> - **Acceptance 5:** send me the exact R6 ruling text the seat says it needs (its stamp, or "not found"). Do not proceed on a guess.

Reading, for the block script `scratch/sl1575-quiet-block.sh`: (1) item 4's "Task 0's" means the QUIET before-legs (the 04:11 leg and before #2, B2), not the LOADED 1,032.39 s leg; (2) item 4 is decided by the PASS / FAIL / INCONCLUSIVE rule above; (3) item 3 (memory) is decided on VmHWM from the same block; (4) order B2 → A1 → A2, each alone, one window, two worktrees prepared before the first START.

#### 2026-10-19 04:44:47 BST — QUIET block: B2 disclosed-contaminated, light-seat overlap disclosed, and Acceptance 5's R6 (three maintainer entries)

**1. B2 is DISCLOSED-CONTAMINATED** (the maintainer's entry in `to-lead.md`, "2026-10-19 04:39:35 BST — Maintainer: SL-1575 QUIET block, B2 is DISCLOSED-CONTAMINATED (the maintainer's own act)"). Lead 13 was started at 03:38:43Z, two minutes into B2 (START B2 03:36:47Z); at 04:39 BST `ps` showed `claude` (PID 1068114) at 38% CPU beside spike.py (158%), load 3.68 2.85 2.58, which breaks B2's ALONE condition. The binding guard, as the entry states it:

> - if item 4 passes **only because of B2** (mean(A) > B1 = 1116.35 s), B2 is RE-RUN alone before any decision;
> - if mean(A) ≤ B1, the result stands, with B2 recorded as disclosed;
> - item 3 (VmHWM) is unaffected by CPU contention, so B2's VmHWM stands.

Reason given: B2 is a slower-biased baseline, and a slower baseline favours PASS under item 4's rule (mean(A) ≤ max(B)).

**2. Disclosed overlap** (the maintainer's entry "2026-10-19 04:39:47 BST — Maintainer: READ-IN OK (lead 9a873d42, PID 1068114)"): during the QUIET block, at most two light seats, READ or EDIT only, no tests, checks, builds, uv sync or DB. The maintainer's reading: A-leg contention biases toward FAIL (conservative), and B2 is already guarded (item 1). Seats and their own stamps (BST):

- exec-1770f: 04:40:53–04:41:55 and 04:42:22–04:42:34, idle after 04:42:34; TaskStopped 04:44:36 (from-lead "2026-10-19 04:44:36 BST"), so seated 04:40:53–04:44:36
- auditor-1259w: 04:41:04–04:42:07, idle after 04:42:07; TaskStopped 04:44:36 (same entry), so seated 04:41:04–04:44:36
- exec-1259c: 04:44:14–04:45:43 (TaskStopped 04:46:06; from-lead "2026-10-19 04:46:06 BST")
- exec-1575n: 04:44:28–04:44:47 (TaskStopped 04:45:12; from-lead "2026-10-19 04:45:12 BST")
- exec-1770g: 04:45:13–04:45:22 (TaskStopped 04:45:33; from-lead "2026-10-19 04:45:33 BST")
(Sources: from-lead-2026-10-09.md entries 04:44:36, 04:45:12, 04:45:33, 04:46:06; lead-handover-2026-10-18.md :581-596. The heading's earlier typed stamp "04:45" was replaced with the read stamp 04:44:47.)

**3. Acceptance 5 / R6** (the maintainer's entry "2026-10-19 04:36:34 BST", Acceptance 5 bullet): R6 = (A1) per `to-lead.md` "2026-10-10 00:27:18 BST — RULING: R6 = (A1), a 20,000-policy demo portfolio built by the seed's existing sampler" (line 20671 of the file at this read), and the cost run uses the built 19,985-row portfolio (`to-lead.md` "2026-10-11 19:36:01 BST", line 22477: stage d stays on the 19,985-row portfolio, not the full book). `PL-1574`'s "R6 size pending" (`docs/plans/PL-01574-…-single-row-work-plan.md:111-114`, `:144`) predates that ruling. Recorded here; no plan edit (`PL-1574` is frozen).

#### 2026-10-19 05:08 BST — QUIET block END, B2 accepted, the A1 crash and its cause

- **Block END:** rc=1, 04:01:15Z (lead handover FINAL 13). **B2 accepted** (to-lead "2026-10-19 05:01:56 BST"): `dislocation_frame.returned` 1011.73 s, VmHWM 6,408,564 KiB; B1 1116.35 s, 6,385,760 KiB. A1 at e73ecd65 crashed rc 1 after `pass1.score_batch.collected` t_s 433.89; A2 did not run. Items 3 and 4 undecided.
- **A1 crash and cause (to-lead "2026-10-19 05:05:35 BST", ruled):** the repro at 20k (`scratch/sl1575-repro/spike-20k.err`) shows `task-9447/spike.py:73 rungs = sum(len(v["ladder"]) …)` raising `KeyError: 'ladder'`. The cause is the spike instrument: `pricing_core/rating/analysis.py` at 50476d3f:201 returns `"ladder"`; Task 1 at e73ecd65:216 returns `"rungs"`. **No FD.** B1 and B2 stand (the edit touches only a post-collection summary line).
- **Fix (key-compatible, one instrument for both trees):** `task-9447/spike.py:73` now reads `v.get("rungs", v.get("ladder"))`; JSONL field names unchanged. sha256 before `1b1bee35ea5d97bf5ddfea74b8b0fa0c14f82418b39488f06ceca95184988721`, **after `0be5f6b8ebbaeb3a13be131b488ddbee3fcbc542a01952f010c6ce9cfaf3525e`**; `python3 -m py_compile` rc 0. The spike was not run.
- **Required cross-check (before A1/A2 are read):** A1's summed rung count (`pass1.retained` `rungs=`) at 200k must EQUAL B2's at 200k; a difference is a finding against Task 1, not a pass.

#### 2026-10-19 08:41 BST — Acceptance 5, the R6 cost run: PASS (maintainer, `to-lead.md` "2026-10-19 08:37:07 BST")

- **Argv (as corrected by `to-lead.md` "2026-10-19 07:06:58 BST"):** `inv-rss.sh acc5 cost --policies 19985 --runs 1` (`ks` default "3,4,5,6"), run under the gate-1 + gate-1b slot flocks. Script `scratch/sl1575-acc5/inv-rss.sh`; outputs `scratch/sl1575-acc5/out/{progress.log,acc5.jsonl,acc5.rss,acc5.err}`. Tree `0022257cb142683a824c244cfc78f91c19398f44` (the `tree` field of every `acc5.jsonl` row).
- **START / END (`progress.log`):** START 2026-10-19T06:07:23Z (07:07:23 BST) load1=1.17; END 2026-10-19T07:36:26Z (08:36:26 BST) load1=2.94, rc=0.
- **Per dislocation run (`acc5.jsonl`, one row per k, `--runs 1`):**

  | k | seconds | load1 | stamp (UTC) |
  |---|---|---|---|
  | 3 | 382.01 | 2.96 | 06:15:08 |
  | 4 | 728.97 | 2.32 | 06:27:17 |
  | 5 | 1420.44 | 2.97 | 06:50:58 |
  | 6 | 2728.02 | 2.94 | 07:36:26 |

- **Peak RSS (`acc5.rss`):** `ru_maxrss_KiB=2476624` = 2.36 GiB. Reading: it is `getrusage(RUSAGE_CHILDREN)`, the largest waited-for descendant (the measuring python), not a sum over the process tree. `acc5.err` is 0 B.
- **Limit (PL-1574:555, quoted):** *"peak RSS ≤ 15.5 GiB and ≤ 60 min per dislocation run at the R6 size"*. Every k ≤ 3600 s and 2.36 GiB ≤ 15.5 GiB. **Verdict: PASS** (maintainer, 08:37:07 BST).
- **Disclosures:**
  - (a) **Option (a) slice:** the run used the first 19,985 rows by quote_id, not the seed's sampled set (`seed.py` `build_portfolio_csv`), per `to-lead.md` "2026-10-19 07:06:05 BST". An interpretation of R6's size; it rides D26 with the other rulings.
  - (b) **Lead swap inside k5:** lead-15's first command was 07:30:47 BST, while k5 ran (`to-lead.md` "2026-10-19 07:30:26 BST", amending 07:13). A lead start can only slow a run, which biases toward FAIL, and peak RSS is unaffected. k5 (1420.4 s) is ≈1.95× k4, in line with the trend: no visible effect (08:37:07).
  - (c) **Observation, not a finding against this slice:** cost is roughly ×2 per k (382 → 729 → 1420 → 2728 s). k=7 projects to ≈5,400 s, over 60 min; the limit above k=6 is unmeasured. Routed to D26 as an OQ, owner planner: *"is k ≤ 6 the product bound for attribution sets, or does FR-263 need a k ceiling?"* No spec or plan edit here (PL-1574 is frozen).

#### 2026-10-19 BST — Gate RED at 564a6d76: the `ladder` consumer defect, fixed (maintainer ruling `to-lead.md` "2026-10-19 09:50:47 BST", R1/R2)

- **Defect:** FD-1573's change made `_score_pass` (`packages/pricing-core/src/pricing_core/rating/analysis.py`) hold `rungs` (`_rung_values` dicts) instead of `LadderRung` lists. `scripts/measure-attribution-cost.py` `replay_values` still read `b["ladder"]` / `c["ladder"]` (`KeyError: 'ladder'`). The gate's red: `FAILED packages/pricing-core/tests/test_rating_attribution.py::test_replay_that_differs_from_a_true_rerate_is_detected_and_recorded` (`pytest.log:10625`).
- **Consumers** (`git grep -n '_score_pass\|dislocation_frame' HEAD -- '*.py'`, code uses only; the rest are prose mentions):

  | Consumer | Reads |
  |---|---|
  | `analysis.py` `dislocation_frame` (:236-237, :242-253) | `outcome`, `error_code`, `minor`, `rungs` |
  | `analysis.py` attribution (:1104, :1112-1131) | `minor` |
  | `backend/src/app/worker/dislocation_handlers.py:305` | calls `dislocation_frame`; reads the returned frame's columns, not the dicts |
  | `scripts/measure-attribution-cost.py` `portfolio_for` (:493) | calls `dislocation_frame`; reads `baseline_minor` |
  | `scripts/measure-attribution-cost.py` `_pass` (was :722-732) | called `_score_pass`; fed `replay_values`, which read **`ladder`** (the only reader) and `minor` |

- **Fix:** `_score_pass`/`dislocation_frame` are unchanged (no `ladder` key, no `LadderRung` lists: the −76% memory result stands). The script gets its own `_ladder_pass` (`{"minor", "ladder"}` per policy, via `score_batch`), and `_pass` calls it. One file, +29/−4.
- **Red → green:** red `FAILED packages/pricing-core/tests/test_rating_attribution.py::test_replay_that_differs_from_a_true_rerate_is_detected_and_recorded` (gate `pytest.log:10625`); green `uv run pytest -q packages/pricing-core/tests/test_rating_attribution.py` → `43 passed in 29.67s`; `ruff check` and `ruff format --check` on the script clean; `mypy` → `Success: no issues found in 244 source files`.
- **Acceptance 5 path:** not touched. acc5 ran `cost --policies 19985 --runs 1` (above); `cmd_cost` (:645-702) calls neither `_pass`, `_ladder_pass` nor `replay_values` (the only callers of `_pass` are in `cmd_replay`), and the diff hunks are `@@ -719,0 +720,26 @@` and `@@ -721,2 +747 @@` / `@@ -731,2 +756,2 @@` inside `_ladder_pass`/`_pass`. acc5 stands.
- **Provisioning gap (R2):** `freMTPL2sev.arff` was never copied into this worktree (the 3 seed FAILED, 3 ERRORs and the 65 s demo exit); copied from tools-main, `cmp` equal, sha256 `047632016b87e132247124f449a95d6d0e9f8ba05f2fe0947ef76ab8aaa10e0a` on both; the re-gate script's preflight now aborts unless both `.arff` files exist.

## PRs

None yet.
