---
id: RS-WORKING
family: research
kind: spike
title: WK-673 dislocation attribution method — residual size, order sensitivity and Shapley cost on freMTPL2
status: active                  # draft → active → closed | retired (§1.2a)
created: 2026-09-28
owner: executor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-673
corrected_by: []
relates: [FR-266, FR-263, WK-673]
---

# RS-WORKING — WK-673 attribution method: residual, order sensitivity and Shapley cost on freMTPL2

| | |
|---|---|
| **Spike** | Track F item F3 of the deputy's "OQ STREAM" entry (2026-09-28, 11:33:12 BST), run by spike-f3 as an executor |
| **Timebox** | started 11:36:42 BST; 3 hours |
| **Spike code tree** | scratch worktree detached at `df8e5811`; spike code committed on top and kept as the salvage ref `refs/salvage/2026-09-28/spike-f3` (SALVAGE-SHA); nothing merged |
| **Record branch base** | `origin/main` at `12431a88` |
| **Decides** | nothing. The verdict below is a proposal; the deputy decides on this record |

## Question

As the deputy framed it (F3): **what method should WK-673 use for FR-266's attribution?**
FR-266 (`docs/specs/03-rating-engine.md`, §3.9, at `df8e5811`) says: *"re-rating with each
change applied in isolation and cumulatively, so the change is decomposed into its
causes"*. §4.6 `DislocationRun` carries an `attribution` list with one `mean_change_pct` per
change. The three options:

- **(a)** isolated plus cumulative in a declared step order, with an explicit
  interaction-residual line so that the parts reconcile to the total;
- **(b)** Shapley over steps;
- **(c)** cumulative only.

The deputy recommended (a). The spike measures on freMTPL2 how large (a)'s residual is and
how much the step order changes the result, and gives (b)'s cost and result for comparison.

## Pass criterion

**Ruled by the deputy, by delegation of the maintainer**, at "2026-09-28 11:39:35 BST ·
deputy · F3 pass criterion RULED" in the team channel. Quoted verbatim:

> **Definitions** (on freMTPL2, portfolio level, per change set):
> - **D = Σᵢ |isolatedᵢ|**, the sum of each change's absolute isolated mean_change_pct. It is the denominator throughout, not the net total. A net total near zero from offsetting changes would make any ratio meaningless.
> - **Order-sensitivity S** = maxᵢ, max over all K! orders, of |cumulativeᵢ(order) − cumulativeᵢ(declared order)|, divided by D.
> - **Residual share R** = |total − Σᵢ isolatedᵢ| / D, the interaction-residual line under (a).
>
> **The criterion:**
> 1. **Hard gate for any method: exact reconciliation.** The parts plus the residual line sum to the total exactly, in Decimal on the rating path (CLAUDE.md §7), per policy and at portfolio level. A method that fails this is out, whatever S and R are.
> 2. **(a) passes** if **S ≤ 0.10 and R ≤ 0.10 on every change set measured**. There are at least four sets: K = 3, 4, 5, 6. At least one must contain a non-linear step such as a minimum premium or a cap, because the §4.3 example's `min_premium` change is the interaction case that matters. Per-policy S and R are reported as p50/p95 distributions. They are evidence, not the gate.
> 3. **If (a) fails on any set**, the record recommends **(b) exact Shapley**, capped at K ≤ 6. It reports the median of N = 5 timings of the 2^K re-rates beside (a)'s 2K, so the cost is on record. Above K = 6 the record states the fallback, (a) with the residual line, as the spike's proposal for me to rule. (c) is not chosen in either case: without isolated runs, cumulative-only cannot show order-dependence.
> 4. **The record states for each set S, R, K, the change list and the tree.** The predicate is named by function and file at the spike's commit. Where it is only in a salvage ref, the ref and path are named.

**Proposed by the spike, not ruled** (written after the ruling reached it): keep the ruled
criterion unchanged, and add one reporting rule. A step whose isolated effect is zero *by
its definition* is labelled a **pure-interaction step** in the attribution output. A cap
measured against the baseline premium is such a step. Without the label, its whole effect
lands in the residual line (see Finding 2). This rule changes no verdict.

## Method

**Portfolio.** freMTPL2 frequency file (OpenML 41214), all **678 013** rows. The file's
SHA-256 is `a45363e0…c7cdd`, matching the pin in `examples/fremtpl2/fetch.py`. Exposure is
clipped at 1.0, for fitting only.

**Rating algorithm: a Polars mirror, NOT the ZEN engine** (accepted as a limit by the lead).
It mirrors a motor rating structure. The annual premium is:

1. claim frequency (a Poisson GLM from `glum`, log link, exposure weight; equivalent to a
   log-exposure offset);
2. × severity;
3. × an age-band rate-table relativity;
4. × (1 + expense load);
5. then `max(·, min_premium)`;
6. then rounding to **integer cents**;
7. then optionally a transitional cap: `min(premium, round(baseline_premium × 1.25))`.

Every total, difference and reconciliation after step 6 is an **int64 cent** sum. That
makes it exact integer arithmetic, not float. S and R are computed on total premium in
cents. They equal the same ratios on §4.6's total-premium `mean_change_pct`, because the
common divisor (baseline total premium) cancels.

**The change catalogue** (`CORE` in `spike/f3_attribution.py`). The index below is the
position in the declared order used in every set:

| # | Change | Linear in log space? |
|---|---|---|
| 0 | model: `freq_v1` → `freq_v2`, a refit adding `VehGas` and a vehicle-age band | yes |
| 1 | rate table: age relativity v1 (all 1.00) → v2 (18–20 ×1.35 … 71+ ×1.10) | yes |
| 2 | severity €1 900 → €1 976 (+4 %) | yes |
| 3 | expense load 0.25 → 0.28 | yes |
| 4 | minimum premium €150 → €180 | **no** |
| 5 | cap: an increase is capped at +25 % of the baseline premium | **no** |

**The predicate, by function and file**, at the salvage ref, in `spike/run.py`:

- `core(idx)` computes D, S, R, the per-policy evidence and the reconciliation gates.
- S is taken over every predecessor set, since any subset of the other steps precedes step
  i in some order. It is cross-checked against an explicit loop over all K! permutations,
  with `assert s_perm / D == s_port`, which passed on every set.
- `cost(kmax, nruns, kmin)` does the timings.
- The rating mirror is `rate()`, the methods are `method_a()` and `shapley_totals()`, and
  the per-subset re-rate cache is `Rater`, all in `spike/f3_attribution.py`.

**Commands**, run from the scratch root:

```bash
uv run python spike/run.py prep                      # fit both GLMs; writes spike/out/portfolio.parquet
uv run python spike/run.py core 0,1,2                # one change set; likewise 1,2,4 · 0,1,2,3 · 0,1,4,5 · 0,1,2,3,4 · 0,1,2,3,4,5
uv run python spike/run.py cost 20 5                 # timings, N=5 for K ≤ 6, single runs above
uv run python spike/run.py cost 16 1 13              # the ceiling run, totals-only cache
```

**Environment.**

- 16 CPUs; Python 3.12 (uv), `polars` 1.43.2, `glum` 3.4.1.
- The box was shared with spikes F1 and F4 and Track D's gates. Load was **10–20**
  throughout; each run records its own load in `spike/out/*.json`.
- The pause rule (load > 12) was reported to the lead at 11:43 BST. After that, only the
  load-independent integer totals were run under load.
- **The attribution numbers are deterministic.** Every set was run twice (N=2), and S and R
  were identical to the last digit.
- Timings are load-sensitive and are marked with their load.

## Findings

### 1. The per-set results (portfolio level)

All percentages are of the baseline total premium (€ SEE-JSON), so they are §4.6's
`mean_change_pct`.

| K | Set (#) | Total % | D % | Residual % | **S** | **R** | (a) passes set? | per-policy S p50 / p95 | per-policy R p50 / p95 |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 0,1,2 | 6.6745 | 6.6539 | 0.0206 | **0.0096** | **0.0031** | yes | 0.032 / 0.312 | 0.018 / 0.233 |
| 3 | 1,2,4 (min premium) | 6.8618 | 7.0916 | −0.2299 | **0.0618** | **0.0324** | yes | 0.022 / 0.395 | 0.022 / 0.242 |
| 4 | 0,1,2,3 | 9.0777 | 8.9442 | 0.1336 | **0.0210** | **0.0149** | yes | 0.042 / 0.365 | 0.025 / 0.301 |
| 4 | 0,1,4,5 (min premium, cap) | 3.6907 | 4.7091 | −1.0185 | **0.3642** | **0.2163** | **no** | 0.034 / 0.672 | 0.032 / 0.683 |
| 5 | 0,1,2,3,4 (min premium) | 11.0383 | 10.8271 | 0.2113 | **0.0627** | **0.0195** | yes | 0.049 / 0.519 | 0.029 / 0.343 |
| 6 | 0,1,2,3,4,5 (min premium, cap) | 7.9210 | 10.8271 | −2.9061 | **0.2879** | **0.2684** | **no** | 0.054 / 0.583 | 0.037 / 0.467 |

Per-policy S and R are over the policies with D_i > 0, which is all 678 013 except the few
the sets without a min-premium step leave unchanged. They are evidence, not the gate. Their
p95 of 0.24–0.68 shows that **a single quote's attribution is order-sensitive and carries a
large residual even when the portfolio's does not**. That matters for FR-263's drill-down
to individual quotes.

The K=6 set in full: the isolated, declared-order cumulative, min/max over all 720 orders,
and Shapley values, each in % of the baseline premium:

| Step | Isolated | Cumulative (declared) | Cumulative min … max over orders | Shapley |
|---|---|---|---|---|
| model refit | 1.4451 | 1.4451 | −1.2410 … 1.9885 | 0.6472 |
| age rate table | 1.3811 | 1.4197 | 0.5298 … 1.5773 | 1.1455 |
| severity +4 % | 3.8276 | 3.8096 | 2.6250 … 3.9970 | 3.4060 |
| expense 0.25→0.28 | 2.2903 | 2.4033 | 1.5809 … 2.4413 | 2.0547 |
| min premium 150→180 | 1.8829 | 1.9606 | 1.2818 … 2.5411 | 1.9180 |
| cap +25 % | 0.0000 | −3.1173 | −3.1173 … 0.0000 | −1.2503 |
| **total** | Σ 10.8271 + residual −2.9061 | 7.9210 | | 7.9210 |

### 2. Why (a) fails: the cap is a pure-interaction step

- **A cap measured against the baseline premium does nothing when applied alone to the
  baseline.** Its isolated value is exactly 0, by definition.
- So under (a) its whole effect (−3.12 % in the declared order) lands in the residual line.
- **Its cumulative value then depends entirely on what precedes it.** The model refit's
  cumulative contribution even **changes sign** across orders (−1.24 % … +1.99 %), because
  a cap applied earlier absorbs the refit's increases.
- Without the cap, every set passes:
  - the worst S is 0.063 and the worst R is 0.032;
  - the min-premium step alone keeps (a) inside 0.10 at K = 3 and at K = 5;
  - the purely multiplicative sets are at S ≤ 0.021 and R ≤ 0.015. Their residual is only
    the € cross-terms of multiplicative changes, (1+a)(1+b) − 1 ≠ a + b.

### 3. The hard gate: exact reconciliation, integer cents

| Method | Per policy and portfolio exact? | How |
|---|---|---|
| (a) isolated + residual line | **yes, all 6 sets, all 678 013 policies** | `iso.sum + res == total`, int64 `np.array_equal` |
| (a)/(c) cumulative (declared order) | **yes, all 6 sets** | the parts telescope: int64 `np.array_equal` |
| (b) Shapley, exact | **yes, as a rational only** | φ·K! is an integer; `Σφ·K! == K!·total` holds everywhere |
| (b) Shapley, rounded to cents | **no**: 139 026 – 240 188 policies per set (20–35 %) miss the total by a cent or more | `np.rint(φ)` |
| (b) Shapley, cents by largest remainder | **yes, all 6 sets**; each part within < 1 cent of exact Shapley (max 0.8 cent) | floor, then the missing cents go to the largest remainders, ties in declared order |

- **(b) cannot pass the hard gate "in Decimal" without a declared allocation rule.** Its
  weights are |S|!(K−|S|−1)!/K!, so a Shapley value is a multiple of 1/K!. For K = 3 that is
  1/6, which has no finite Decimal form.
- A spec choosing (b) must therefore name the rounding-and-allocation rule (largest
  remainder is the one measured here). Otherwise it fails its own gate on a fifth to a third
  of quotes.
- The rounded-Shapley row is also the gate predicate's **negative control**: the same
  `np.array_equal` prints a failure on it.

### 4. Cost: (b) at 2^K re-rates against (a) at 2K

Mirror re-rates of all 678 013 rows, in seconds; N=5 for K ≤ 6, reported as the median:

| K | (a): 2K re-rates, median s | (b): 2^K re-rates, median s | load (1 min) |
|---|---|---|---|
| 3 | 0.08 | 0.11 | 10.7 |
| 4 | 0.08 | 0.20 | 10.7 |
| 5 | 0.12 | 0.48 | 10.7 |
| 6 | 0.18 | 1.42 | 12.1 |
| 7 | 0.24 | 2.83 (N=1) | 11.8 |
| 8 | 0.24 | 7.23 (N=1) | 13.3 |
| 9 | 0.33 | 12.65 (N=1) | 13.7 |
| 10 | 0.29 | 29.91 (N=1) | 14.2 |
| 11 | 0.35 / 0.39 | 58.07 / 49.53 (N=2) | 13.5 / 13.1 |
| 12 | 0.40 / 0.38 | 137.91 / 111.05 (N=2) | 18.7 / 14.6 |
| CEILING-ROWS | | | |

**Changes beyond #5 in the cost rows are synthetic relativity edits** (`extra_delta()`),
used only to grow K. They are not part of the S/R sets.

**On the platform's engine**, the mirror's absolute seconds do not transfer.

- NFR-493 sets the batch floor at ≥ 1 M risks/hour per worker, so one re-rate of this
  portfolio is ≤ 40.7 worker-minutes at that floor.
- At K = 6: (a)'s 12 re-rates are ~8.1 worker-hours, and 2 of them are the dislocation run
  itself. (b)'s 64 re-rates are ~43 worker-hours.
- Both scale linearly in workers (NFR-493), but (b) costs 5.3× (a) at K = 6 and doubles
  with each further change.
- No NFR in `03` bounds attribution time (noted in the ruling), so this is on record, not
  gated.

## Verdict against the criterion (a proposal; the deputy decides)

- **Hard gate:**
  - (a) **passes**.
  - (b) **passes only with a declared cent-allocation rule**. Largest remainder was
    measured to pass; without such a rule it fails on 20–35 % of policies.
  - (c) passes arithmetically, but is excluded by the ruling.
- **(a): FAIL.** S and R are both ≤ 0.10 on four of six sets, including both min-premium
  sets. They are above 0.10 on both sets containing the cap: S 0.364 / R 0.216 at K = 4,
  and S 0.288 / R 0.268 at K = 6.

## Recommendation

Following the ruled rule 3:

1. **(b) exact Shapley for K ≤ 6**, with the cent-allocation rule written into the spec.
   Largest remainder, ties in declared order, is measured here to reconcile exactly per
   policy and at portfolio level.
2. **Above K = 6: (a) with the residual line**, the spike's proposal for the deputy to rule.
3. Whichever is chosen, **mark a step whose isolated effect is zero by definition** (a
   baseline-relative cap) as a pure-interaction step. Otherwise the attribution list
   reports it as "0.00 %" while it moves the total by −3 %.
4. **The OQ row** (Track E's) should carry Finding 3's gate consequence for (b) in its
   options cell. §4.6's `attribution[].mean_change_pct` is a float in the example, and a
   Decimal or integer-minor form is needed to satisfy the gate.

## What remains

- **The ZEN engine was not used.** The arithmetic is a Polars mirror of one structure. A
  real bundle's ladder (rounding per rung, constraint steps) can add interaction that the
  mirror does not have. The engine's batch path (`score_batch`) does not exist at
  `df8e5811`, so the engine-based cost is an extrapolation from NFR-493's floor, not a
  measurement.
- **Only one portfolio and one catalogue of changes.** Sets were chosen, not sampled. A
  different cap level or min-premium level moves S and R.
- **Timings were taken on a loaded box** (load 10–20; the pause was reported). Above K = 6
  they are single runs.
- **The two K ≥ 13 cost runs ended silently.** Both runs stopped during K = 13 with an empty
  stderr, the first with the per-subset premium vectors cached. The cause is not
  established. CEILING-NOTE
- Per-policy attribution for FR-263's drill-down was measured only as the p50/p95 evidence.
  No rule for presenting a single quote's residual was designed.

## Salvage

`refs/salvage/2026-09-28/spike-f3` → SALVAGE-SHA, local only; the lead pushes it.

- Paths: `spike/f3_attribution.py`, `spike/run.py`, and `spike/out/set_*.json` and
  `cost*.jsonl` (the raw results).
- The fitted portfolio parquet is git-ignored and regenerated by `run.py prep` (13 s).
