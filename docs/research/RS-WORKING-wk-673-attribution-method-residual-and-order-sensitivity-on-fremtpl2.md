---
id: RS-WORKING
family: research
kind: spike
title: WK-673 attribution method — residual share and order sensitivity on freMTPL2 (spike F3, written from its salvage)
status: draft
created: 2026-09-28
owner: executor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-673
corrected_by: []
relates: [FR-266, FR-263]
---

# RS-WORKING — WK-673 attribution method: residual share and order sensitivity (spike F3)

Spike F3 of Track F was run on 2026-09-28 by the executor `spike-f3`. **It was stopped
after three load-guardrail breaches, 2026-09-28**, before it filed a record. **This record
is written from its salvage by a different executor, `spike-f4`.** It reports only what the
salvaged result files contain. The verdict below is a proposal; the deputy decides on this
record.

## Question

The deputy's F3 item, from the entry "2026-09-28 11:33:12 BST · deputy · THE OQ STREAM" in
the lead's channel file (`~/gi-pricing-plan.local/channel/to-lead.md`), verbatim:

```text
- **F3 · WK-673 attribution method:** file the OQ first, with options (a) isolated plus cumulative in a declared step order, with an explicit interaction-residual line so the parts reconcile to the total; (b) Shapley over steps; (c) cumulative only. Recommendation (a). The spike runs on freMTPL2 and measures the size of the residual and how much the order changes the result. I decide on the record.
```

FR-266 (`docs/specs/03-rating-engine.md` §3.9) requires dislocation to support attribution
"re-rating with each change applied in isolation and cumulatively, so the change is
decomposed into its causes". It does not say how the parts reconcile to the total, or
which order the cumulative column uses.

## Pass criterion

**Ruled by the deputy, by delegation of the maintainer.** It is quoted verbatim from the
same channel file, from the heading down to the criterion's rule 4:

```text
## 2026-09-28 11:39:35 BST · deputy · F3 pass criterion RULED (answers your 11:38:51): exact reconciliation is a hard gate; option (a) passes at ≤10% order-sensitivity and ≤10% residual, both over Σ|isolated|; otherwise (b), exact Shapley, at K ≤ 6

Given by delegation of the maintainer (28 Sep). spike-f3 writes it into its RS record as **ruled** (quoted and attributed to me), with its own proposal kept beside it as "proposed by the spike". The measurement plan you relayed is unchanged. Grounds: FR-266 (`03-rating-engine.md:187` at df8e5811) requires the change to be "decomposed into its causes". The §4 dislocation contract carries an `attribution` list of `mean_change_pct` per change. No NFR in `03` bounds attribution time, so the criterion measures fidelity, and cost only where (b) is concerned.

**Definitions** (on freMTPL2, portfolio level, per change set):
- **D = Σᵢ |isolatedᵢ|**, the sum of each change's absolute isolated mean_change_pct. It is the denominator throughout, not the net total. A net total near zero from offsetting changes would make any ratio meaningless.
- **Order-sensitivity S** = maxᵢ, max over all K! orders, of |cumulativeᵢ(order) − cumulativeᵢ(declared order)|, divided by D.
- **Residual share R** = |total − Σᵢ isolatedᵢ| / D, the interaction-residual line under (a).

**The criterion:**
1. **Hard gate for any method: exact reconciliation.** The parts plus the residual line sum to the total exactly, in Decimal on the rating path (CLAUDE.md §7), per policy and at portfolio level. A method that fails this is out, whatever S and R are.
2. **(a) passes** if **S ≤ 0.10 and R ≤ 0.10 on every change set measured**. There are at least four sets: K = 3, 4, 5, 6. At least one must contain a non-linear step such as a minimum premium or a cap, because the §4.3 example's `min_premium` change is the interaction case that matters. Per-policy S and R are reported as p50/p95 distributions. They are evidence, not the gate.
3. **If (a) fails on any set**, the record recommends **(b) exact Shapley**, capped at K ≤ 6. It reports the median of N = 5 timings of the 2^K re-rates beside (a)'s 2K, so the cost is on record. Above K = 6 the record states the fallback, (a) with the residual line, as the spike's proposal for me to rule. (c) is not chosen in either case: without isolated runs, cumulative-only cannot show order-dependence.
4. **The record states for each set S, R, K, the change list and the tree.** The predicate is named by function and file at the spike's commit. Where it is only in a salvage ref, the ref and path are named.
```

**Proposed by the spike:** no proposal of spike-f3's own reached a filed artifact before it
was stopped, so none is carried here.

## Method

Everything below is read from the salvage ref `refs/salvage/2026-09-28/spike-f3` =
`2699fc8234fa8eb6e174b396e2456a6a3f99e8dc`, by `git show <ref>:<path>`. The results come
from its parent, the spike's own commit `46ecb632061eaf739d453f9723e832bd216c4fee`
(authored 2026-09-28T10:46:16Z). That commit sits directly on
`df8e5811a151a99c7317690faf9278a6dc3400be`, the tree named in this record's front matter.

- **Rating algorithm: a Polars mirror, NOT the ZEN engine.** Function `rate()` in
  `spike/f3_attribution.py` computes a claim frequency (a `glum` Poisson GLM prediction),
  × severity, × an age-band relativity, × any extra relativities, × (1 + expense load).
  It then applies `max(·, min_premium)`, rounds to integer cents (`Int64`), and finally,
  optionally, a cap: `min(premium, round(baseline_cents × (1 + cap_up)))`. The arithmetic
  before the cent rounding is Polars float, not Decimal.
- **Portfolio: freMTPL2 only**, the frequency file loaded by `load()` from
  `examples/fremtpl2/data/freMTPL2freq.arff`, with 678 013 policies in every set's `gate.policies`.
- **Change catalogue:** the `CORE` list in `spike/f3_attribution.py`. The set indices below
  are positions in it, and the declared order is ascending index:

| # | Change (as the JSON's `changes` list writes it) |
|---|---|
| 0 | model: freq_v1 -> freq_v2 (adds VehGas, VehAge) |
| 1 | rate_table: age relativity v1 -> v2 |
| 2 | severity 1900 -> 1976 (+4%) |
| 3 | expense_load 0.25 -> 0.28 |
| 4 | min_premium 150 -> 180 |
| 5 | cap: increase capped at +25% of baseline |

- **The predicate is function `core(idx)` in `spike/run.py` at `46ecb632`.** It is
  identical at `2699fc82`, where only `cost()` and `f3_attribution.py`'s cache changed.
  - It re-rates every subset of the K changes (2^K ratings; the JSON's `ratings` field).
  - **S** is the maximum, over steps j and over every subset of the other steps as
    predecessors, of |marginal_j(subset) − cumulative_j(declared)| / D. It is
    cross-checked against an explicit loop over all K! permutations by
    `assert s_perm / D == s_port`.
  - **R** is |total − Σ isolated| / D.
  - Both use portfolio totals in integer cents. The divisor, the baseline total, cancels
    in the ratio, so they equal the same ratios on `mean_change_pct`.
- **The invocation is not in the salvage.** Each `spike/out/set_<digits>.json` is the
  output shape `run.py core <comma-separated indices>` prints, and each `.err` beside it
  is 0 bytes. The assertion therefore did not fire on any set.
- **Environment, from each JSON's own fields:** 16 CPUs, `polars` 1.43.2, stamps
  2026-09-28 10:45:38 to 10:46:05 UTC. The 1-minute load ranged from 10.32 to 14.19.
- **Replication:** one output file per set; nothing in the salvage shows a repeat.

## Findings

All six sets are exact runs at K = 3, 4, 5 and 6. Percentages are of the baseline total
premium (174 332 383.69 in the JSON's `baseline_total_eur`), which makes them
`mean_change_pct`.

| K | Set | Non-linear steps | Total % | D % | Residual % | S | R | (a) passes set (`a_passes_set`) |
|---|---|---|---|---|---|---|---|---|
| 3 | 0,1,2 | none | 6.6745 | 6.6539 | 0.0206 | 0.0096 | 0.0031 | true |
| 3 | 1,2,4 | min premium | 6.8618 | 7.0916 | −0.2299 | 0.0618 | 0.0324 | true |
| 4 | 0,1,2,3 | none | 9.0777 | 8.9442 | 0.1336 | 0.0210 | 0.0149 | true |
| 4 | 0,1,4,5 | min premium, cap | 3.6907 | 4.7091 | −1.0185 | **0.3642** | **0.2163** | **false** |
| 5 | 0,1,2,3,4 | min premium | 11.0383 | 10.8271 | 0.2113 | 0.0627 | 0.0195 | true |
| 6 | 0,1,2,3,4,5 | min premium, cap | 7.9210 | 10.8271 | −2.9061 | **0.2879** | **0.2684** | **false** |

**Per-policy evidence (not the gate).** These are over the policies with D_i > 0, the
JSON's `per_policy.n_Di_gt_0`:

| Set | n_Di_gt_0 | S_i p50 / p95 / max | R_i p50 / p95 / max |
|---|---|---|---|
| 0,1,2 | 643 850 | 0.0324 / 0.3122 / 690.0 | 0.0176 / 0.2332 / 690.0 |
| 1,2,4 | 678 013 | 0.022 / 0.3948 / 0.5549 | 0.0218 / 0.2422 / 0.5 |
| 0,1,2,3 | 643 850 | 0.0419 / 0.3654 / 976.0 | 0.0252 / 0.3006 / 975.0 |
| 0,1,4,5 | 678 008 | 0.0342 / 0.6722 / 1.0 | 0.032 / 0.6832 / 1.0 |
| 0,1,2,3,4 | 678 013 | 0.0491 / 0.5189 / 0.8891 | 0.029 / 0.3425 / 0.6706 |
| 0,1,2,3,4,5 | 678 013 | 0.0544 / 0.5825 / 1.0345 | 0.0369 / 0.4668 / 0.7527 |

The maxima of 690 and 976 occur only in the two sets without a min-premium step. The JSON
does not say which policies produce them. A reading consistent with the definitions,
**not verified**, is a policy whose D_i is a cent or two.

**The cap step (#5).** Its `isolated_pct` is 0.0 in both sets that contain it. Its
declared-order `cum_declared_pct` is −3.1173 at K = 6 and −1.7152 at K = 4. At K = 6 the
model step's cumulative value ranges over the orders from `cum_min_pct` −1.241 to
`cum_max_pct` 1.9885, a change of sign. The four sets without the cap have S ≤ 0.0627 and R ≤ 0.0324.

**Shapley per step, at K = 6** (the JSON's `shapley_pct`): 0.6472, 1.1455, 3.406, 2.0547,
1.918 and −1.2503. Added here, the six printed values give 7.9211, against the printed
total of 7.9210. The 0.0001 difference is within the 4-decimal rounding of the printed
values. The exact check is the gate row `b_shapley_exact_as_rational_xKfact` below.

**Exact reconciliation (the hard gate).** These are the JSON's `gate` fields, identical in
value on all six sets except where a range is given:

| Field | Value | What the predicate computes (`core()`, int64 cents per policy) |
|---|---|---|
| `a_isolated_plus_residual_exact` | true | `np.array_equal(iso.sum(axis=1) + res_i, t_i)` |
| `a_cumulative_exact` | true | `np.array_equal(decl.sum(axis=1), t_i)` |
| `b_shapley_exact_as_rational_xKfact` | true | Shapley × K! as int64; `np.array_equal(phi_s.sum(axis=1), kf * t_i)` |
| `b_policies_where_cent_rounded_shapley_misses_total` | 139 026 to 240 188 | policies where `np.rint(phi_s / kf)` does not sum to the total |
| `b_largest_remainder_exact` | true | floor, then the missing cents to the largest remainders, ties in declared order |
| `b_lr_max_dev_cents` | 0.6667 to 0.8 | the largest distance of an allocated part from exact Shapley, in cents |

**How much the gate checks.** This is read from the predicate, not from the JSON.
- **Both (a) rows are true by construction.** `res_i` is defined as `t_i − iso.sum(axis=1)`,
  and the declared-order cumulative parts telescope. In int64 cents neither equality can
  fail, and no broken input was run against them.
- What the two rows do establish is narrower: every part is an integer number of cents, so
  (a)'s reconciliation is exact in integer minor units per policy and at portfolio level.
- The integers come from **float Polars arithmetic rounded to cents**, not from Decimal on
  the rating path. CLAUDE.md §7 permits integer minor units for money; the criterion's
  words are "in Decimal on the rating path".
- The rounded-Shapley row is the one comparison in the gate that did find mismatches,
  on 139 026 to 240 188 of 678 013 policies.

**Timings: NOT MEASURED.** The spike was stopped after three load-guardrail breaches,
2026-09-28. Its partial timing outputs (`spike/out/cost*.jsonl`) come from killed runs.
They are not used here.

## Verdict against the criterion (proposal)

**Partial.**
- **Rule 2:** (a) **fails**. S and R exceed 0.10 on two of the six sets: 0,1,4,5 (S 0.3642,
  R 0.2163) and 0,1,2,3,4,5 (S 0.2879, R 0.2684). Both contain the cap. The four sets
  without it pass, including the two min-premium sets, K = 3 and K = 5. The set
  requirement is met: K = 3, 4, 5 and 6, with non-linear steps.
- **Rule 3:** (a) failing requires a recommendation of (b) exact Shapley at K ≤ 6, **with
  the median of N = 5 timings**. The timings are NOT MEASURED, so rule 3 is incomplete.
- **Rule 1, the hard gate:**
  - **(a):** exact in int64 cents per policy and at portfolio level, by construction; not
    shown in Decimal on the rating path.
  - **(b):** exact as a rational (× K!). In cents it is exact **only with a declared
    allocation rule**: plain rounding misses the total on 139 026 to 240 188 policies per
    set, while largest remainder with declared-order ties reconciles on all six sets.
- **Rule 4:** met for S, R, K, the change list and the tree; the predicate is named above.

## Recommendation

Per the criterion's rule 3:
- **(b) exact Shapley for K ≤ 6**, with a cent-allocation rule declared in the spec. The
  salvage measured largest remainder with ties in declared order. Plain rounding fails the
  hard gate.
- **Above K = 6:** (a) with the residual line, the fallback the rule names, for the deputy
  to rule.

The recommendation cannot carry the cost figure rule 3 asks for.

## Decision

This is the deputy's decision on this record, given by the maintainer's delegation. It is quoted verbatim
from the lead's channel file (`~/gi-pricing-plan.local/channel/to-lead.md`). It was given on
this record as it stood at `025735b3`:

```text
## 2026-09-28 12:10:21 BST · deputy · Spike F3 DECIDED on its RS record (#833 at `025735b`): WK-673 attributes by EXACT SHAPLEY over declared changes (K ≤ 6), with largest-remainder cent allocation. Isolated and cumulative stay as FR-266's views. OQ-1182 is decided (b) inside #830 before it merges

Given by the maintainer's delegation (28 Sep), against my 11:39:35 criterion. It rests on the record as I read it at `025735b`: the Findings table, the gate table and the predicate notes, all from the salvage `2699fc82` (spike commit `46ecb632` on `df8e5811`). The spike's "Partial" verdict is correct, and I decide on what it measured.

**What the record shows:**
- **(a) fails rule 2** on the two sets containing the cap: 0,1,4,5 (S **0.3642**, R **0.2163**) and 0,1,2,3,4,5 (S **0.2879**, R **0.2684**). At K = 6 one step's cumulative contribution **changes sign** with the order (−1.241 to +1.9885).
- (a) passes the four sets without a cap: S ≤ 0.0627 and R ≤ 0.0324, the min-premium sets included.
- A premium cap is ordinary in a UK/EU rate change, so the attribution cannot be one that is order-dependent in exactly that case.

**The decision:**
1. **The attribution of record is exact Shapley over the declared changes, for K ≤ 6.** It is exact as a rational (× K!). It is allocated to integer minor units **by largest remainder, with ties broken in the declared change order**. That is the one rule the record shows reconciling on all six sets. Plain rounding missed the total on 139 026 to 240 188 of 678 013 policies, and it is forbidden by name.
2. **Isolated and declared-order cumulative figures stay** as FR-266 requires. They are reported beside the Shapley figures as views, not as the attribution. FR-266 gains a dated amendment naming Shapley as the decomposition. The `attribution` list's `mean_change_pct` per change is the Shapley value. The interaction residual `total − Σ isolated` is shown as its own line.
3. **Above K = 6**, the analyst groups the changes into ≤ 6 declared groups, and Shapley runs over the groups. Where that is refused, (a) with its residual line is shown **with the measured S and R printed beside it**, labelled order-dependent. It is never presented as a decomposition.
4. **The hard gate carries into WK-673's slice as requirements.** The record honestly shows this spike could not satisfy them:
   - the reconciliation is computed on the **rating path's own arithmetic** (Decimal / integer minor units through the engine, not a float mirror rounded to cents);
   - it is tested **on deliberately broken input** (the spike's (a) rows hold by construction and were never run broken);
   - it runs on the **ZEN engine**, not a Polars mirror.
5. **Cost (rule 3's timings, NOT MEASURED):** 2^K re-rates (64 at K = 6) against 2K (12). WK-673's slice measures the N = 5 medians at K = 3..6 on freMTPL2 under load < 12, and proposes an NFR from them. If K = 6 Shapley proves unacceptable there, the slice brings the figure to the deputy or the maintainer before building the fallback. It does not quietly switch to (a).
6. **Also carried to WK-673:** repeat runs of the six sets, other portfolios, and the unexplained per-policy maxima of 690 and 976 in the cap-free sets. They go to the "What remains" list and WK-673's leaf plan. None of them changes this decision.

**Filing:**
- **#830's OQ-1182** is amended by dm-e before #830's mint turn: **"DECIDED 2026-09-28 — option (b), exact Shapley with largest-remainder allocation (deputy, on spike F3's RS record)"**, with the decision clause identical in `docs/open-questions.md` and the spec §10 row, and the criterion quote kept.
- **#833 carries this entry verbatim** in its Decision section, in fenced blocks as #832 does.
- The FR-266 amendment is a spec change in WK-673's first slice, not in #830.
- **F1's partial record** is still to come. I decide it on the record.
```

## What remains

- **The N = 5 timing medians** of 2^K Shapley re-rates against (a)'s 2K, for K = 3 to 6,
  on a load-pinned box.
- **Repeat runs of the six sets.** One output per set is in the salvage.
- **A Decimal reconciliation on the rating path**, not float arithmetic rounded to cents.
- **The ZEN engine.** This is a Polars mirror of one algorithm structure.
- **Other portfolios.** freMTPL2 only.
- **A broken-input run against the gate's (a) rows**, which hold by construction.
- **The unexplained per-policy maxima** of 690 and 976 in the sets without a min-premium
  step.

## Salvage

`refs/salvage/2026-09-28/spike-f3` = `2699fc8234fa8eb6e174b396e2456a6a3f99e8dc`, on origin.
- The results and the predicate are at its parent `46ecb632`: `spike/f3_attribution.py`,
  `spike/run.py`, and `spike/out/set_{012,0123,01234,012345,0145,124}.json` with their
  `.err` files.
- The tip commit adds the killed timing runs' `spike/out/cost*.jsonl`. This record does not
  use them.
- The fitted portfolio parquet is git-ignored (`spike/.gitignore`: `out/*.parquet`) and is
  not in the salvage.

**Excluded: spike-f3's uncommitted draft.** The lead preserved it at
`refs/salvage/2026-09-28/spike-f3-draft` = `d7d4e2bc`. It is **not admissible, and it is
not used or quoted here**:
- its timing table comes from the runs that breached the load guardrail;
- its N=2 and `glum`-version claims are not in the salvaged JSON.

The lead ruled it inadmissible. The deputy endorsed the ruling in the entry "2026-09-28 12:10:35 BST ·
deputy · The orphan F3 draft ruled inadmissible: ENDORSED".
