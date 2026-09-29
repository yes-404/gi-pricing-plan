---
id: RS-1201
family: research
kind: spike
title: WK-673 attribution method — residual share and order sensitivity on freMTPL2 (spike F3, written from its salvage)
status: active
created: 2026-09-28
owner: executor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-673
corrected_by: []
relates: [FR-266, FR-263]
---

# RS-1201 — WK-673 attribution method: residual share and order sensitivity (spike F3)

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

The deputy later corrected the hard gate, rule 1 of the criterion, by a dated line. The
whole entry is quoted verbatim from the same channel file:

```text
## 2026-09-28 13:57:02 BST · deputy · (1) cwd rule (2) RESTATED in a keepable form; (2) F3's hard gate CORRECTED by a dated line to integer minor units (FR-273). The WK-673/674 map-plan adoptions are noted

**(1) The working form of cwd rule (2)**, replacing "a spawned agent's session cwd is its worktree", which the harness defeats (isolation worktrees are auto-removed after a turn that changes nothing, and Bash is then refused):
- A spawned agent's **session cwd may be the root**. It **never writes in the root**: no file edit, no git write, no build output.
- **Every process it launches runs with `env -C <its job-dir tree>`** (or `git -C` / `--project` with an absolute path), and its first report quotes `readlink /proc/<pid>/cwd` for one launched process.
- Around each git write it quotes root `git status --porcelain` before and after (0 lines both times).
- A breach is handled agent-first (the 11:59 rule).
- This form is in force now, and your respawn of planner-673/674/690 satisfies it. **Plan review 15** records the harness limit and this working form as a finding against the spawn brief (with the three root-cwd incidents of this morning). Its proposal is the place for any durable fix (a brief template, or a guard).

**(2) F3, a dated correction. It supersedes the hard-gate wording of my 11:39:35 criterion (rule 1) and of my 12:10:21 decision (item 4, first bullet):**

> *Corrected 2026-09-28 13:57:02 BST by the deputy.* "Exact reconciliation … in Decimal on the rating path" and "the rating path's own arithmetic (Decimal / integer minor units through the engine)" are replaced by: **exact reconciliation in integer minor units, as the rating path produces them.** The ZEN engine is float64 at its boundary. `03` FR-273 (`03:220` at `6c6f4532`): *"The binding accepts no decimal type and returns `float`"*, so money crosses only as integer minor units. Each output is rounded by `_round_minor` (`packages/pricing-core/src/pricing_core/rating/score.py:526`, `int(Decimal(repr(raw)).quantize(…))`). The gate is therefore: every attribution part, the interaction-residual line and the total are **integers in minor units taken from the engine's own `value_minor` outputs**, and the parts (plus the residual) sum to the total **exactly as integers**, per policy and at portfolio level. No float is summed after rounding. Shapley's rational × K! and the largest-remainder allocation run on those integers. **CLAUDE.md §7 permits this** ("integer pence/cents, or Decimal in the rating path"). The broken-input test and the "on ZEN, not a Polars mirror" requirement stand unchanged.

WK-673's S1 FR-266 amendment cites this line. #833 (F3's RS record) appends it fenced after my 12:10:21 quote, before its mint. **The WK-673/674 map-plan proposals are adopted, as noted.** Their maintainer-resolver DPs come to me as they arise.
```

The deputy's 14:05:30 entry amends item 5 of the F3 decision. It is filed in #845's WK-673
ruling, and the whole entry is quoted verbatim from the same channel file:

```text
## 2026-09-28 14:05:30 BST · deputy · WK-673 ([#844's WK-673 map plan], #844): DP-1, DP-2 and DP-3 DECIDED; the §3.11-vs-code disagreement RESOLVED (the spec is right; the code docstring is corrected); the Shapley cost gets a feasibility rule

Given by the maintainer's delegation (28 Sep, extended goal). A decision-maker files these as `RL-` records quoting this entry, in S1's PR or before it, since DP-1 and DP-2 block S1. Read at `ed123cb0`.

**DP-1 (how the 2^K subset bundles are built): (a) ACCEPTED, with conditions.** Synthetic bundles are compiled through `compile_bundle` at step granularity, and they are:
- **ephemeral and content-addressed, and never persisted as Rating Versions:** no `VR-` identifier, never approvable, never deployable, never visible in any version list;
- cached per run by content hash, and discarded with the run's scratch;
- surfaced by name if one fails to compile (a subset that cannot compile fails the run with the subset named; it is never silently skipped);
- stated in the run artifact, which records that K + … subset bundles were compiled, with their hashes.

**DP-2 (where a "declared change" comes from): (c) ACCEPTED.** Changes are derived from the structural diff between baseline and candidate. The analyst may regroup them into ≤ 6 groups, and the **server verifies that the groups partition the diff exactly** (no change missing, none duplicated) and refuses otherwise, by name. The derived and regrouped lists are both on the artifact.

**DP-3 (where FR-224's threshold lives): (b) ACCEPTED.** It is the `rating_version` ApprovalPolicy entry: versioned, its every change audited (`06`'s governance path), with **no environment-variable override** (FR-446's mechanism is not applied to it). S5 cites this.

**The disagreement (CLAUDE.md §0), RESOLVED: the spec is right, and the code's docstring is corrected.**
- `03` §3.11 (`03:206–211` at `ed123cb0`) records spike S1's measurement: *"Inside the engine, arithmetic is exact. `0.1 + 0.2 == 0.3` evaluates `true`"* (impossible in float64), and *"At the Python binding … every value returned is a Python `float`"*.
- `_round_minor`'s docstring (`score.py:527–531`) says *"the engine's float64 arithmetic"*. The float64 is the **binding's** return type, not the engine's arithmetic. The rounding function itself is right, and only its sentence is wrong.
- **S1 corrects that docstring sentence** (spec and code in one commit, CLAUDE.md §2) to *"the binding's float64 return values (the engine's own arithmetic is exact, `03` §3.11)"*. No behaviour changes.
- My 13:57:02 F3 correction already reads "float64 **at its boundary**", which is consistent. It stands.

**The Shapley cost: a feasibility rule, amending my F3 decision's item 5 (dated):**
1. **S3 measures first.** The real `score_batch` rate on freMTPL2, N = 5, load < 12. The 43.4M-rating / ~43 worker-hour figure uses NFR-493's **floor** (≥ 1M risks/hour/worker, `03:945`), not a measurement.
2. **S3 evaluates ladder replay as the primary route.** `03` FR-248 requires each ladder rung to record its value and operation so that *"the ladder reconciles exactly"*. Where the declared changes are **step-aligned** (each change replaces steps' inputs, and the step graph is shared), v(S) for each subset is computed by replaying the ladder with each rung taken from baseline or candidate according to S. That is **2 ratings per policy plus integer arithmetic**, not 2^K.
   - **Exactness is proven, not assumed:** replay must equal a true re-rate for every policy on the full portfolio at K ≤ 3, and on a declared verification sample at K = 4–6. Any mismatch falls the run back to re-rates, recorded on the artifact.
   - Structural changes (steps added or removed) are not step-aligned and use re-rates.
3. **Where re-rates are needed:** the run computes and **shows its estimated rating count (2^K × policies) before launch**, and runs as a background Job. **A sampled portfolio is never presented as exact Shapley.** If sampling is ever offered, it is a separately named estimate with its interval, and that is a spec change, not a default.
4. **S3 proposes the dislocation-attribution NFR from the measurement.** If neither replay nor re-rates at K = 4 fit it, S3 brings the figure to me before building any fallback, as item 5 already requires.
5. Exact Shapley over declared changes (K ≤ 6) and largest-remainder allocation **stand** as the method of record.

**The other premises are noted for S1**, which amends them: the contract's `job_id` / `by_ladder_rung` / `errors` missing from §4.6; `attribute`'s §5.2 signature having no baseline; RL-881's stale "06 §4.2 omits rating_version". S6's split (floor wiring after WK-672 S3) is sound slice design. **I accept [#844's WK-673 map plan] as WK-673's map plan** once the RL records these DPs and the plan cites it. The acceptance line follows your request.
```

*The only deviation from the channel text is one marked substitution. Where the entry names
#844's WK-673 map plan by its working id (twice), it is shown here as "[#844's WK-673 map plan]". That id
is unminted, so the literal would never resolve. The proof is to reverse the substitution in
the fence and diff it against the channel entry, which prints nothing.*

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
