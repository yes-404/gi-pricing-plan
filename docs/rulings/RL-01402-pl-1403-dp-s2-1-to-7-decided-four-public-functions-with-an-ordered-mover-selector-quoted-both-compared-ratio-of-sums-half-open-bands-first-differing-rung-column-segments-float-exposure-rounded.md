---
id: RL-1402
family: ruling
title: PL-1403 DP-S2-1 to DP-S2-7 decided — four public functions with an ordered mover selector, the quoted-both compared set with outcomes counted, exact ratio-of-sums means rounded once, half-open bands, the first differing rung, a segment is a portfolio column with null a level, and a float exposure is read rounded to six places; P1 to P6 adopted, all amended
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-04              # the mint date (check 31); ruled 2026-10-04
owner: decision-maker
tree: 1ab1776dae080dcde4eb8e79ac84f5f5f653136a
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1267, RL-1394, RL-1361, RL-1379, RL-1263, SL-1386, SL-1387, SL-1388, SL-1389, FR-263, FR-264, FR-1397, FR-62, FR-247, FR-252, NFR-495, NFR-496]
---

# RL-1402 — PL-1403 DP-S2-1 to DP-S2-7 decided

## How this was ruled

- **Filed under working id 9734, allocated by the lead; minted as `RL-1402`** (2026-10-04,
  `python3 scripts/doc-id.py next`), in one PR with `PL-1403`. The working ids 9734 and 9735
  survive only where this paragraph, the branch and agent names, and the handover file names
  below carry them.
- **The plan ruled on** is WK-673 Slice 2's leaf plan (SL-1386), then working id 9735 and now `PL-1403`, on PR #1097
  at `a6dcdccd` (`status: draft`, `tree: 1ab1776d`). It is not on `main`, so it is named by PR
  and head. Its Decision points table is at `:301-308` of that file; its proposed texts P1 to
  P6 are its Appendix, `:817-884`.
- **Mandate:** the lead's GO in `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
  "2026-10-04 00:12:32 BST — GO: dm-1386 …", verbatim in the parts that bind this record:

  > - **B2** goes into the DM: DP-S2-1 is ruled with an explicit mover selector, defined so that Task 5's mover test is deterministic (a stated tie-break, and integer minor units per FR-1397).
  > - Conditions:
  >   1. One record, exact texts and placement for any spec amendment, and which side was wrong for each DP. PL-1267 and RL-1394 are frozen (deltas only).
  >   2. If any DP needs OQ 9739 (the subset input contract), the DM says so, and it stays SL-1387's unless it blocks S2.

  B2 is the plan audit's (`~/gi-pricing-plan.local/handover/audit-9735-2026-10-03.md`, Sun
  2026-10-04 00:11:14 BST). That audit's non-blocking N1, N2, N3 and N6 fall inside DP-S2-1 and
  DP-S2-5, and are ruled there.
- **Decided by the decision-maker, 2026-10-04.** Drafted from 00:13:10 BST
  (`TZ=Europe/London date`), in the decision-maker's own worktree, on branch
  `rl-9734-wk-673-s2-dp-ruling`, cut from origin/main `1ab1776d`. Every locator below was read
  at `1ab1776d`.
- **Effort:** medium, inherited from the lead (the charter's "Model / effort" line; no
  maintainer raise to high was given).
- **Scope.** DP-S2-1 to DP-S2-7 are ruled. DP-S2-8 is the planner's (kind `scope`) and is not
  re-ruled. P1 to P6 are adopted, each amended; the adopted texts are S1 to S5 under "The exact
  texts". Nothing here is later-phase capability: every text is spec for WK-673, a Phase 2 Work.
- **OQ 9739 is not needed.** No DP here concerns a subset bundle: Slice 2 rates the baseline
  and the candidate, each with its own `input_contract` (`03` §4.8 at `:702`). OQ 9739 stays
  SL-1387's.

## Verified first, at `1ab1776d`

| Fact the ruling rests on | Read at `1ab1776d` |
|---|---|
| FR-263 and FR-264's words | `docs/specs/03-rating-engine.md:186-187`. FR-263: *"movers beyond configurable thresholds with drill-down to individual quotes"*. Neither says which policies are compared, how a mean is taken, or which band an edge is in |
| FR-1397's arithmetic | `03:190`: *"integer minor units taken from the payable premium's `value_minor` … with no float summed after rounding"*. Its every-run failing check is attribution's (Slice 3) |
| §5.2 fixes `dislocate` only | `03:985-987`; the types paragraph `:1052` says the band and mover names *"are Slice 2's to confirm"* (`RL-1394` T7, ruling file `:569-570`) |
| Slice 7 needs Slice 2's reader | `RL-1361` Ruled item 1 (`:364-372`): *"The frame is read through PL-1267 Slice 2's reader"* |
| The §4.6 example and the contract | `03:514-557`; `docs/contracts/schemas/dislocation-run.schema.json`: `by_segment.items.properties.level` is `{"type": "string"}`; `errors.items.properties.sample` is an array of **objects**; every percentage and share is `{"type": "number"}`, non-nullable; the example's rung is `"base_premium"` and its top band `"> +10%"` |
| The rung names and order | `packages/model-schema/src/model_schema/scoring.py:49-60` `LadderRungName`; `packages/pricing-core/src/pricing_core/rating/ladder.py:52-63` `RUNG_ORDER`, the same ten names in the same order. `base_premium` is not one of them |
| A rung appears at most once, and carries both values | `score.py:683` `_build_ladder` walks `RUNG_ORDER` once and sets `value_minor=round_once(current, rounding)` and `unrounded_minor=current`; `LadderRung.unrounded_minor` is `PositionalDecimalStr \| None` (`scoring.py:161`). The rounding is per rung and per version, so two ladders can share an unrounded value and differ in `value_minor` |
| The float exposure rule | `packages/pricing-core/src/pricing_core/data/profile.py:414` `_stored_exposure(value: float) -> Decimal`, `Decimal(str(round(value, 6)))` (FR-62); `examples/fremtpl2/seed.py:56` `"exposure_years": "float"` |
| A null level is a level | `profile.py:411` `return None if value is None else str(value)`: the profiler keeps a null category as `None`, never as a dropped row or the text "None" |
| The error-mapping precedent | `backend/src/app/worker/data_handlers.py:408-411`: `SplitError` → `PlatformError("VALIDATION_FAILED", …, 422, …)` |
| `DecimalStr` renders with `str` | `packages/model-schema/src/model_schema/money.py:93-97` |
| The contract is hand-authored | `backend/tests/test_contracts.py:89` `"dislocation-run": "03 §4.6 — hand-authored until WK-673 Slice 4 generates and compares it (PL-1267)"` |

## DP-S2-1 — `analysis.py`'s public surface, with the mover selector (B2)

### Options

The plan's (a), (b) and (c), plus the audit's B2 alternatives: (a1) an `is_mover` column in
`dislocation_frame`; (a2) a fourth public function that selects and orders the movers.

### Ruled: (a), amended to (a2) — four public functions, an ordered mover selector, a typed error with a code

`analysis.py` defines, beside `dislocate` (whose `RL-1394` T7 signature is unchanged):

1. `read_portfolio(portfolio, *, segments=()) -> pl.LazyFrame` — §4.8's reader. It checks the
   frame **when it is called** (it collects its counts in one `select` inside the call), so a
   caller, Slice 7 included, gets the refusal before it builds anything on the result. It
   returns the frame with every column kept and `exposure_years` read per DP-S2-7.
2. `dislocation_frame(baseline, candidate, portfolio, spec) -> pl.DataFrame` — one row per
   policy, **sorted by `quote_id`**, with the columns S2 lists. It adds `change_minor`
   (`candidate_minor − baseline_minor`, integers, null unless both passes quoted) to the plan's
   columns, so the mover rule and every sum read one integer column. It refuses, before any
   rating, a portfolio column named as one of its own columns (audit N2).
3. `select_movers(frame, spec) -> pl.DataFrame` — **the mover selector.** It returns the rows
   of `frame` that are movers under DP-S2-4, in this order:
   1. the absolute percentage change, largest first, compared exactly as the rational
      `|change_minor| / baseline_minor` of two integers;
   2. then `|change_minor|`, largest first, as an integer;
   3. then `quote_id` ascending in code-point order (Python `str` comparison).

   `quote_id` is unique (§4.8), so the order is total and the output is deterministic.
   Membership is decided exactly in integers: a banded policy is a mover when
   `100 × |change_minor| ≥ mover_threshold_pct × baseline_minor`, with the threshold taken as
   an exact rational of its decimal. No float is formed. There is no cap: every mover is
   returned, because FR-263 asks for the movers beyond the threshold, not the top n; Slice 4
   writes all of them to `largest_movers_blob`.
4. `summarise_dislocation(frame, spec) -> DislocationRun`; `dislocate` is exactly
   `summarise_dislocation(dislocation_frame(…), spec)`.

`PortfolioFrameError(ValueError)` carries a class attribute `code = "VALIDATION_FAILED"`, so the
two `RL-1394` refusal tests (Task 3) assert `exc.code == "VALIDATION_FAILED"` as well as the
type and the message (audit N1). The platform mapping is still Slice 4's (P10's precedent).

**Task 5's mover test is then deterministic:** `test_dislocation_movers_are_kept_for_drill_down`
calls `select_movers` on the fixture frame and asserts the exact list of `quote_id`s in order,
with a fixture that holds: two movers with the same percentage and the same `|change_minor|`
(for example −12% and +12% on one baseline), which must come out in `quote_id` order; a mover
with a larger percentage, which comes first; a policy exactly at the threshold (in); one minor
unit below it (out); a `zero_baseline` policy and a declined policy (both out). It is shown red
against an implementation that sorts by signed change.

**Why (a2).** A column (a1) says which rows are movers but not their order, and Slice 4 would
then have to pick an order for the blob, which is the second implementation of a rule that
B2 exists to prevent. A function owns the rule and the order in one place. (b) duplicates the
reader against `RL-1361` item 1; (c) changes the signature `RL-1394` just fixed.

**Which side was wrong.** The spec was incomplete: §5.2 named only `dislocate`, though `RL-1361`
item 1 already required a public reader. The plan's (a) was incomplete: no mover selector
(B2), no code on the error (N1), no collision rule (N2). No code exists.

## DP-S2-2 — which policies are compared

### Ruled: (b), amended — outcomes counted, and two sets: compared and banded

- `outcomes` is a new required §4.6 field: `quoted_both`, `quoted_to_declined`,
  `declined_to_quoted`, `declined_both`, `error` (an `"error"` row in either pass), summing to
  `policy_count`, and `zero_baseline`.
- The **compared set** is the quoted-both policies. Every money figure, `totals.change_pct`,
  `by_ladder_rung` and `by_segment` are over it. A ratio-of-sums figure (DP-S2-3) is defined
  with a zero baseline in it, so a `zero_baseline` policy belongs there.
- The **banded set** is the compared set less the `zero_baseline` policies. Bands and movers,
  which need a per-policy percentage, are over it only. This amends the plan's (b), which kept
  `zero_baseline` policies out of the segment means as well; there is no reason to, under
  DP-S2-3.
- `errors` lists each code with at least one policy, in code order. An `error` policy is counted
  once, under its baseline pass's `error_code` where that pass errored, else its candidate
  pass's, so `Σ errors[].count = outcomes.error`. `sample` holds up to 10 of those policies as
  objects `{"quote_id": …}`, the first 10 by `quote_id`. The contract's `sample` items are
  objects at `1ab1776d`, so this keeps that shape; the plan's "a sample of `quote_id`s" read as
  bare strings, and is corrected.

**Why (b).** Quoted-to-declined is the dislocation an approver most needs to see; (a) hides it
under a code that is not an error, and (c) lets one decline fail a book.

**Which side was wrong.** The spec was silent. The plan's `sample` wording did not match the
contract; the contract was right.

## DP-S2-3 — averages and shares

### Ruled: (a), amended — exact, rounded once by `round(Fraction, n)`, and null for a zero denominator

A mean or total change in percent over a group is Σ `change_minor` ÷ Σ `baseline_minor` × 100
over the group, held as a `fractions.Fraction` of Python `int`s and rounded **once** with
`round(fraction, 2)` (exact, half-even), then converted to `Decimal` exactly and to `float` only
at the model boundary. An `exposure_share` is rounded the same way to 6 places;
`exposure_years` is the exact decimal sum over every policy, quantised once to 6 places,
half-even. **A ratio whose denominator is 0 is `null`**: an empty band's `mean_change_pct`, a
segment level whose baselines are all 0, every share when the exposure total is 0,
`totals.change_pct` when the compared set is empty or all zero-baseline. The contract widens
those six fields to number-or-null (S5).

The plan's Task 5 Step 3 converts with `Decimal(n) / Decimal(d)` under a precision context and
then `quantize`. That rounds twice (at the context's precision, then at the quantum), and a
half-way case can then round the wrong way. `round(Fraction, n)` rounds once. The §4.6 example
holds under this rule: `round(Fraction(816_200_00, 41_882_100_00) * 100, 2)` is `39/20`, `1.95`,
computed at `1ab1776d`.

**Why (a).** One definition serves overall, segment and band figures, it is exact on the
integers, and a few tiny premiums cannot dominate it, as they can in (b) and (c).

**Which side was wrong.** The spec was silent, and the contract could not carry an undefined
ratio. The plan's Step 3 rounds twice.

## DP-S2-4 — bands and movers

### Ruled: (a), with the label format and the threshold arithmetic stated

Half-open bands `[lo, hi)` on the exact per-policy percentage, over the banded set; labels
`"< e₀%"`, `"eᵢ% to eᵢ₊₁%"`, `"≥ eₙ%"`, each edge printed as its plain decimal string with no
exponent and no trailing zeros, `+` before a positive edge, `0` for zero; every band listed. A
mover is a banded policy with |percentage| ≥ `mover_threshold_pct`, evaluated as DP-S2-1 states.
`band_edges_pct` (decimals, at least one, strictly increasing) and `mover_threshold_pct`
(a positive decimal) are both required, with no default; the names stay as `RL-1394` T7 wrote
them. The example's top label becomes `"≥ +10%"`.

**Why (a).** One rule with no special case at zero. No default, because any default is a pricing
judgement with no source here.

**Which side was wrong.** The spec's example label `"> +10%"`, under the rule now stated;
`RL-1394` T7 licensed the amendment.

## DP-S2-5 — the originating rung

### Ruled: (a), amended — a rung differs on either value, decimals compared as decimals, and an integer identity tested

A compared policy's originating rung is the first rung in `RUNG_ORDER` that differs between its
two ladders: present in one only, **or** a different `value_minor`, **or** a different
`unrounded_minor` compared as `Decimal` values (`"100"` equals `"100.0"`; audit N6). The plan's
(a) compared `unrounded_minor` alone. Rounding is per rung and per version, so a candidate
that changes only a rung's rounding moves `value_minor` and the premium with the unrounded value
unchanged, and (a) as written would give that policy a change but no origin. Under the amended
rule a policy with no differing rung has a change of 0. Hence:

- the integer sums of `change_minor` by originating rung add up exactly to
  `candidate_premium_minor − baseline_premium_minor` (audit N3). Task 5's rung test asserts this
  identity on integers, as well as the `Fraction` sum of the parts equalling the unrounded total
  percentage.
- `contribution_pct[r]` is Σ change over the policies whose origin is r ÷ Σ baseline over the
  compared set × 100, rounded once (DP-S2-3); rows only for rungs that originate at least one
  policy, in ladder order.

The §4.6 example's `"base_premium"` is not a rung name, and its single row (1.10) cannot sum to
`change_pct` 1.95 under an additive rule. The example becomes `risk_premium` 1.11 and
`constraints` 0.84.

**Why (a).** It is `PL-1267`'s "first ladder rung at which the two premiums differ", made precise,
and its parts add up. (b) does not add up; (c) misses a sub-minor-unit change at an early rung.

**Which side was wrong.** The spec's example (`base_premium`; one row that cannot add up); the
code's `LadderRungName` was right. The plan's (a) missed a rounding-only change.

## DP-S2-6 — what a segment is

### Ruled: (a), amended — a column of a stated dtype, levels in native order, null a level

A name in `segments` is a portfolio column. Names must be distinct (a `DislocationSpec`
validator). The column's dtype must be string, categorical or enum, an integer, boolean or date;
any other dtype (a float, a decimal, a datetime, a list, a struct) is a `PortfolioFrameError`
naming the column and its dtype, raised by `read_portfolio`, because a float level has no stable
string. An absent column is a `PortfolioFrameError` naming it. `by_segment` covers the compared
set, in `segments` order, then by level in native order (strings in code-point order, integers
by value, `false` before `true`, dates by date), the null level last. The level is the value as
a string (an integer in decimal, a date in ISO form, a boolean as `true` or `false`), or JSON
`null` for nulls, which form one level and are never dropped, as the profiler already does
(`profile.py:411`). A segment level's `exposure_share` is of the compared set. The contract's
`level` widens to string-or-null.

**Why (a).** It keeps `RL-1394` T7's signature; FR-264's "available on the portfolio dataset"
reads as a column; (c) would shrink a segment silently. (b) is a later amendment if analysts need
bands they cannot materialise.

**Which side was wrong.** The contract's `level` (`{"type": "string"}`) cannot hold a null level;
the plan's (a) left the level order and the admitted dtypes to the executor.

## DP-S2-7 — `exposure_years`'s dtype

### Ruled: (a), amended — NaN and infinity refused with nulls

An integer or decimal dtype is read exactly. A float dtype (Float32 or Float64) is read row by
row as `Decimal(str(round(v, 6)))`, `_stored_exposure`'s rule (FR-62). A NaN or infinite value
is refused and counted with the nulls, because a NaN is not null in Polars and passes a
`< 0` test. Any other dtype is a `PortfolioFrameError` naming the column and its dtype.

**Why (a).** §4.8's "decimal" then says how the column is read, and freMTPL2-shaped data
(`seed.py:56`) needs no conversion step. (b) refuses the public example; (c) puts binary noise
into a figure the profiler already rounds.

**Which side was wrong.** Neither spec nor code: §4.8 named the read type, and the stored type
was not its question. The plan's (a) missed NaN and infinity.

## Ruled

| DP | Ruling |
|---|---|
| DP-S2-1 | **(a), amended** — `read_portfolio` (refuses at the call), `dislocation_frame` (sorted by `quote_id`, adds `change_minor`, refuses a colliding column), `select_movers` (exact integer membership; order: \|pct\| desc, \|change_minor\| desc, `quote_id` asc), `summarise_dislocation`; `PortfolioFrameError.code = "VALIDATION_FAILED"` |
| DP-S2-2 | **(b), amended** — `outcomes`; compared set (money, segments, rungs) and banded set (bands, movers); `errors` sums to `outcomes.error`, `sample` as `{"quote_id"}` objects |
| DP-S2-3 | **(a), amended** — exact `Fraction`, rounded once with `round(…, n)`; a zero denominator is null |
| DP-S2-4 | **(a)** — half-open bands, label format stated, mover ≥ threshold, both fields required; `"≥ +10%"` |
| DP-S2-5 | **(a), amended** — a rung differs on presence, `value_minor` or `Decimal` `unrounded_minor`; integer identity tested; example rungs corrected |
| DP-S2-6 | **(a), amended** — a column of a stated dtype; levels in native order, null a level last |
| DP-S2-7 | **(a), amended** — int, decimal or float (rounded to 6 places); NaN and infinity refused |

## The exact texts

The executor applies these, never the plan's Appendix (PL-1403 Task 0 Step 4), in one commit
with the spec change (Task 1). `<date>` is the merge date the executor writes; `RL-<n>` is this
record's minted id. Each block's fence is not part of the text. **Status:** P1 to P6 are all
adopted amended, as S1 to S5; P2 to P5 become one text, S3.

### S1 — `03` §5.2, the `# pricing_core/rating/analysis.py` block: insert directly after `dislocate`'s two lines (`03:986-987`), before `async def derive_changes`

```python
def read_portfolio(portfolio: pl.LazyFrame, *,                     # added <date> (WK-673 S2, RL-<n>): §4.8's
                   segments: Sequence[str] = ()) -> pl.LazyFrame    # reader; refuses at the call; Slice 7 reuses it
def dislocation_frame(baseline: CompiledBundle, candidate: CompiledBundle,
                      portfolio: pl.LazyFrame, spec: DislocationSpec) -> pl.DataFrame   # one row per policy
def select_movers(frame: pl.DataFrame, spec: DislocationSpec) -> pl.DataFrame          # FR-263's movers, in §4.6's order
def summarise_dislocation(frame: pl.DataFrame, spec: DislocationSpec) -> DislocationRun  # dislocate = this ∘ dislocation_frame
```

### S2 — `03` §5.2: a new paragraph directly after the `DislocationSpec` types paragraph (`03:1052`), which is not edited

```markdown
*`analysis.py`'s public surface (added <date>, WK-673 Slice 2, `RL-<n>`).* `read_portfolio` checks §4.8's frame and each name in `segments` (present, of a dtype §4.6 admits) when it is called, not when its result is collected, and returns the frame with every column kept and `exposure_years` read as §4.6 states. `PortfolioFrameError` is a `ValueError` with `code = "VALIDATION_FAILED"`, raised for any such fault, and by `dislocation_frame` for a portfolio column named as one of its own columns; its message names the column and the count, or the column and its dtype, and never a value; the platform maps it to `VALIDATION_FAILED`. `dislocation_frame` calls `read_portfolio(portfolio, segments=spec.segments)` before any rating and returns one row per policy, sorted by `quote_id`: `quote_id`; `baseline_outcome`, `candidate_outcome`; `baseline_minor`, `candidate_minor`, the `payable_premium` rung's `value_minor` as an integer, null unless that pass quoted; `change_minor`, `candidate_minor − baseline_minor`, null unless both passes quoted; `baseline_error_code`, `candidate_error_code`; `origin_rung` (§4.6), null unless both passes quoted and a rung differs; then every portfolio column, in the portfolio's order. `select_movers` returns the frame's rows for FR-263's movers, in §4.6's mover order; Slice 4 writes them to `largest_movers_blob`. `dislocate(b, c, p, s)` is exactly `summarise_dislocation(dislocation_frame(b, c, p, s), s)`. `band_edges_pct` and `mover_threshold_pct` keep the names `RL-1394` gave them; §4.6 states their rules.*
```

### S3 — `03` §4.6: a new dated block directly after the JSON example's closing fence, before `### 4.7`

```markdown
*(Amended <date>, WK-673 Slice 2, `RL-<n>`: the run's arithmetic, for FR-263 and FR-264. The example's top band label, its `exposure_years`, `by_ladder_rung` and `errors` were changed and `outcomes` added to match.)*

**Outcomes, and the two sets.** `policy_count` counts every portfolio row. `outcomes` counts each policy once by its two outcomes: `quoted_both`, `quoted_to_declined`, `declined_to_quoted`, `declined_both` and `error` (an `"error"` row in either pass), which sum to `policy_count`; and `zero_baseline`, the quoted-both policies whose baseline payable premium is 0. The **compared set** is the quoted-both policies. The **banded set** is the compared set less its `zero_baseline` policies. `errors` has one item for each error code with at least one policy, in code order: an `error` policy is counted once, under its baseline pass's `error_code` where that pass errored and otherwise under its candidate pass's, so the counts sum to `outcomes.error`; `sample` holds up to 10 of those policies as `{"quote_id": …}`, the first 10 by `quote_id`.

**Money and ratios.** Every money figure is a sum over the compared set of the `payable_premium` rung's `value_minor`, as integers (FR-1397's arithmetic, NFR-496). A policy's change is its candidate minus its baseline payable premium. A mean or total change in percent over a group is the group's Σ change ÷ Σ baseline × 100, computed as an exact rational of the integers and rounded once to 2 decimal places, half-even. An `exposure_share` is the group's Σ `exposure_years` ÷ the Σ over the set the group is part of, rounded once to 6 places, half-even. A ratio whose denominator is 0 is `null`. `exposure_years` is the exact decimal sum over every policy, rounded once to 6 places, half-even. `totals`, `by_segment` and `by_ladder_rung` cover the compared set.

**Bands and movers** cover the banded set, because they need a per-policy percentage change, (candidate − baseline) ÷ baseline × 100, exactly. `band_edges_pct` (required; decimals; at least one; strictly increasing) cuts it into half-open bands `[lo, hi)`, labelled "< e₀%", "eᵢ% to eᵢ₊₁%" and "≥ eₙ%", each edge printed as its plain decimal string with no exponent and no trailing zeros, with "+" before a positive edge. Every band is listed, in edge order; an empty band has `policies` 0. A **mover** is a banded policy whose percentage change has an absolute value of at least `mover_threshold_pct` (required; a positive decimal), decided exactly on the integers. Movers are ordered by the absolute percentage change, largest first, then by the absolute change in minor units, largest first, then by `quote_id` in code-point order.

**Rungs.** A compared policy's **originating rung** is the first rung, in the ladder's fixed order (FR-247, FR-252), that differs between its two ladders: present in one ladder only, or with a different `value_minor`, or with a different `unrounded_minor` compared as decimal values. A policy with no differing rung has a change of 0. `by_ladder_rung` has one row for each rung that originates at least one compared policy's change, in ladder order; its `contribution_pct` is those policies' Σ change ÷ the compared set's Σ baseline × 100. The integer sums of change by originating rung add up exactly to `candidate_premium_minor − baseline_premium_minor`.

**Segments.** Each name in `segments` (distinct) is a portfolio column of a string, categorical, integer, boolean or date dtype; any other dtype, or an absent column, is refused with `VALIDATION_FAILED` naming the column. `by_segment` has one row per segment and level, in `segments` order, then by level in the value's own order (strings by code point, integers by value, `false` before `true`, dates by date), with the null level last. The level is the value as a string (an integer in decimal, a date in ISO form, a boolean as `true` or `false`), or `null`: null values form one level and are never dropped.

**`exposure_years` as read.** §4.8's "decimal" is how the column is read: an integer or decimal dtype exactly; a float dtype row by row as the decimal of the value rounded to 6 places (FR-62's rule); a NaN or infinite value is refused with the nulls; any other dtype is refused with `VALIDATION_FAILED` naming the column and its dtype.
```

### S4 — `03` §4.6's JSON example: five edits, in the same commit as S3

1. `"policy_count": 1_284_902, "exposure_years": "1240118.4",` becomes
   `"policy_count": 1_284_902, "exposure_years": "1240118.400000",`
2. Insert, as a new line directly after the `totals` object's closing line
   (`             "change_pct": 1.95},`):
   `  "outcomes": {"quoted_both": 1_284_902, "quoted_to_declined": 0, "declined_to_quoted": 0,`
   `               "declined_both": 0, "error": 0, "zero_baseline": 0},`
   (the example's six bands already sum to 1 284 902, so every policy is in the banded set.)
3. `{"band": "> +10%", …}` becomes `{"band": "≥ +10%", …}`, the rest of the line unchanged.
4. `"by_ladder_rung": [{"rung": "base_premium", "contribution_pct": 1.10}],` becomes
   `"by_ladder_rung": [{"rung": "risk_premium", "contribution_pct": 1.11},`
   `                   {"rung": "constraints", "contribution_pct": 0.84}],`
5. `"errors": [{"code": "INPUT_CONTRACT_VIOLATION", "count": 0}]` becomes `"errors": []`.

### S5 — `docs/contracts/schemas/dislocation-run.schema.json`, in the same commit as S3

1. Add `"outcomes"` to the top-level `required`, after `"totals"`, and add this property after
   `totals`:

```json
"outcomes": {
  "type": "object",
  "description": "Every policy counted once by its two outcomes; the first five sum to policy_count. zero_baseline counts the quoted-both policies with a baseline payable premium of 0 (03 §4.6).",
  "required": ["quoted_both", "quoted_to_declined", "declined_to_quoted", "declined_both", "error", "zero_baseline"],
  "properties": {
    "quoted_both": {"type": "integer", "minimum": 0},
    "quoted_to_declined": {"type": "integer", "minimum": 0},
    "declined_to_quoted": {"type": "integer", "minimum": 0},
    "declined_both": {"type": "integer", "minimum": 0},
    "error": {"type": "integer", "minimum": 0},
    "zero_baseline": {"type": "integer", "minimum": 0}
  }
}
```

2. `"type": "number"` becomes `"type": ["number", "null"]`, every other keyword kept, at exactly
   these six places: `totals.properties.change_pct`; `distribution.items.properties.mean_change_pct`
   and `.exposure_share`; `by_segment.items.properties.mean_change_pct` and `.exposure_share`;
   `by_ladder_rung.items.properties.contribution_pct`.
3. `by_segment.items.properties.level` becomes `{"type": ["string", "null"]}`.
4. `errors.items.properties.count` becomes `{"type": "integer", "minimum": 1}`, and
   `errors.items.properties.sample` becomes
   `{"type": "array", "maxItems": 10, "items": {"type": "object", "required": ["quote_id"], "properties": {"quote_id": {"type": "string"}}, "additionalProperties": false}}`.

No other contract text changes. The `dislocation-run` entry in `ONE_SIDED_SLUGS` is untouched
(Slice 4 lifts it).

## Which side was wrong (`CLAUDE.md` §0), collected

| DP | Where | Wrong side |
|---|---|---|
| DP-S2-1 | §5.2 named no reader, though `RL-1361` item 1 requires one | **the spec** (incomplete); the plan's (a) also lacked a mover selector, an error code and a collision rule; no code exists |
| DP-S2-2 | the plan's "sample of `quote_id`s" against the contract's object items | **the plan**; the contract was right. The spec was silent |
| DP-S2-3 | the contract's non-nullable ratios; the plan's two-step rounding | **the contract** (cannot carry an undefined ratio) and **the plan's Task 5 Step 3** |
| DP-S2-4 | the example's `"> +10%"` | **the spec's example**, under the rule stated; licensed by `RL-1394` T7 |
| DP-S2-5 | the example's `"base_premium"` and its non-additive single row; the plan's unrounded-only comparison | **the spec's example** (the code's `LadderRungName` was right) and **the plan's (a)** |
| DP-S2-6 | the contract's string-only `level` | **the contract**; the profiler's null-level convention was right |
| DP-S2-7 | §4.8 "decimal" against a float-stored column | **neither**; the plan's (a) missed NaN and infinity |

## What it obliges

- **This commit:** this record only. No spec, contract or code file is edited here; the SL-1386
  executor applies S1 to S5 through `spec-change` and `contract-schema` (PL-1403 Task 1).
- **PL-1403 (the planner's, pre-merge; planner-9735fix):** DP-S2-1 to DP-S2-7 cite this record's
  minted id in "Resolved by". Then, so that the plan agrees with this ruling:
  1. Acceptance 3 names five public functions, `select_movers` among them; the class
     `PortfolioFrameError` is checked by `grep -n '^class '` beside the `^def` grep.
  2. Task 3: `read_portfolio` raises at the call; the two `RL-1394` tests also assert
     `exc.code == "VALIDATION_FAILED"`; add tests for a NaN exposure, a float segment column
     (refused by dtype), and the positive float-exposure read (`0.1234567` reads as
     `Decimal("0.123457")`).
  3. Task 4: add `change_minor` to the frame; sort by `quote_id`; add a test that a portfolio
     column named `origin_rung` is refused before any rating; the origin-rung test includes a
     candidate that changes only a rung's rounding and a pair of equal decimals written
     `"100"` and `"100.0"`.
  4. Task 5: replace Step 3's conversion with `round(fraction, n)`; test 7 (the movers) calls
     `select_movers` with the fixture DP-S2-1 lists and asserts the ordered list; the rung test
     adds the integer identity; the outcomes test asserts `Σ errors[].count = outcomes.error`
     and a sample of `{"quote_id": …}` objects; add one test that an empty band's
     `mean_change_pct` is `None`.
  5. Write set: the contract is edited (S5: DP-S2-2, DP-S2-3 and DP-S2-6 all touch it), no longer
     "only if".
- **PL-1267 (frozen; the dispatch record carries this delta, the plan is not edited):**
  *"Slice 2's `analysis.py` public surface is `dislocate` plus `read_portfolio`,
  `dislocation_frame`, `select_movers` and `summarise_dislocation` (RL-1402 DP-S2-1). Slice 4
  writes `select_movers`' rows to `largest_movers_blob` in the order it returns and maps
  `PortfolioFrameError` (code `VALIDATION_FAILED`) to a 422. Slice 7's diff route reads its
  portfolio with `read_portfolio`. `DislocationRun` gains a required `outcomes` field, and six
  of its ratios may be null (RL-1402 DP-S2-2, DP-S2-3)."*
- **RL-1394 (frozen; not edited, no delta needed):** this record amends three texts `RL-1394`
  landed (the example's top band label and `errors` line, and the contract's `level` and
  `errors.items`); S3's dated note in §4.6 records it. `RL-1394`'s rulings stand.
- **Slice 5 (SL-1389, informational):** FR-224's quantile deviation will need a rule
  for `zero_baseline` policies; this record gives them no percentage.

## Acceptance — the violation that must become detectable

This record builds nothing, so no check is proven red here. Slice 2's executor shows each red on
deliberately broken input:

- *Violation: two runs order the movers differently.* `select_movers` sorted by signed change, or
  without the `quote_id` tie-break, fails the ordered-list assertion.
- *Violation: a figure rounded twice.* A conversion through `Decimal(n) / Decimal(d)` at a low
  context precision fails a half-way fixture figure that `round(Fraction, 2)` gets right.
- *Violation: a rounding-only rung change gets no origin.* Comparing `unrounded_minor` alone
  fails the integer identity on that fixture.
- *Violation: a null segment level dropped.* Filtering nulls out of `by_segment` fails the
  null-level row assertion.
- *Violation: a NaN exposure read as a number.* Removing the NaN check fails the refusal test.

## Amendment N2, 2026-10-04 — a negative baseline (pre-mint)

*Dated 2026-10-04 (`TZ=Europe/London date`: 2026-10-04 12:29:22 BST), before the mint of RL-1402.* Raised by this record's audit (`~/gi-pricing-plan.local/handover/audit-9734-2026-10-04.md`,
N2); the lead routed it here in the entry headed "2026-10-04 12:27:35 BST — N2 DECIDED (a): a
pre-mint amendment to RL-1402 by dm-9734b (opus/medium) …"
(`~/gi-pricing-plan.local/channel/to-lead.md`). This section rules N2 only and reopens nothing
else above. Where it gives a text, that text **replaces** the one above it names; every other text
above stands. Verified at `origin/main` `7e2ee2ba`.

**The defect.** DP-S2-2 and S3 define the banded set as "the compared set less its
`zero_baseline` policies", and `zero_baseline` counts a baseline of exactly 0. A quoted-both
policy with `baseline_minor < 0` is then banded. For it, DP-S2-1's membership test
`100 × |change_minor| ≥ mover_threshold_pct × baseline_minor` has a negative right side, so it is
a mover for every change, 0 included; and its percentage `change ÷ baseline × 100` has the
opposite sign to its change, so it lands in the wrong band. The mover order's `|change_minor| /
baseline_minor` is negative for it too.

### Item 3 — a negative baseline is a legitimate value, not an error row

It is a value, counted and excluded; it is never an `"error"` row and never a refusal:

- `MoneyMinor` admits it: `packages/model-schema/src/model_schema/money.py:69` is
  `Annotated[int, Strict(), Field(...)]`, with no lower bound (contrast `perils.py:290`, which adds
  `Field(ge=0)` where a bound is meant).
- Positivity is an opt-in test, not a runtime bound: `03`'s glossary (`03-rating-engine.md:69`)
  makes "no-negative-premium" a Regression Suite property assertion, and the code's form of it
  is `PremiumPositive`, `kind: Literal["premium_positive"]`
  (`packages/model-schema/src/model_schema/regression.py:90-93`), which a suite may declare.
- §4.8's error rows are rows `score_batch` writes for a row's own fault, with an `error_code`
  (`03-rating-engine.md` §4.8's `error_code` row: "populated only on an `"error"` row, the
  `_raise_named` convention's code"); its frame refusals name `exposure_years`' sign, never a
  premium's (`03:698`). A dislocation run reads both passes' outputs; it does not reclassify a
  `quoted` row. A Rating Version that can quote a negative premium is the Regression Suite's to
  catch, before approval; the run reports how many there are.

### Item 1 — the banded set is `baseline_minor > 0`

The banded set is the quoted-both policies whose baseline payable premium is **above 0**. Bands,
the band `exposure_share` denominator, the mover inequality, the mover percentage and the mover
order are over it only, so every division in them has a positive divisor. The compared set is
unchanged: a negative-baseline policy stays in `totals`, `by_segment` and `by_ladder_rung`, and
in every ratio-of-sums over a group it belongs to; DP-S2-3's ratio is the exact ratio of the
group's sums as their signs give it, and only a zero denominator is `null`.

### Item 2 — reported in a new count, `outcomes.negative_baseline`

Not dropped silently, and not folded into `zero_baseline`: a zero premium and a negative one are
different findings for an approver, and one count holding both would hide which. **A new
required count is added**: `negative_baseline`, the quoted-both policies whose baseline payable
premium is below 0. Then, for every run:
Σ `distribution[].policies` = `quoted_both` − `zero_baseline` − `negative_baseline`.
The contract and `03` §4.6 change, through texts S3, S4 and S5, which are already in Slice 2's
write set (PL-1403 Task 1 and its write-set row for `dislocation-run.schema.json`). The three
replacements:

**N2-a — replaces, in S3's "Outcomes, and the two sets." paragraph, the two sentences** from "and
`zero_baseline`, the quoted-both policies whose baseline payable premium is 0." to "The **banded
set** is the compared set less its `zero_baseline` policies." with:

> `zero_baseline`, the quoted-both policies whose baseline payable premium is 0; and
> `negative_baseline`, those whose baseline payable premium is below 0. The **compared set** is
> the quoted-both policies. The **banded set** is the compared policies whose baseline payable
> premium is above 0: the compared set less its `zero_baseline` and `negative_baseline`
> policies, so Σ `distribution[].policies` = `quoted_both` − `zero_baseline` −
> `negative_baseline`. A negative baseline is a value a Rating Version can return, not an error
> (no-negative-premium is a Regression Suite property, not a runtime bound): it stays in the
> compared set and enters no band and no mover.

The first sentence of that paragraph keeps its list up to "which sum to `policy_count`;"; the
sentence beginning "`errors` has one item" is unchanged. S3's "Bands and movers" paragraph is
unchanged: it already says "over the banded set".

**N2-b — replaces S4's edit 2** (the inserted `outcomes` lines) with:

`  "outcomes": {"quoted_both": 1_284_902, "quoted_to_declined": 0, "declined_to_quoted": 0,`
`               "declined_both": 0, "error": 0, "zero_baseline": 0, "negative_baseline": 0},`

and its parenthesis stands (every policy is in the banded set).

**N2-c — replaces S5 edit 1's `outcomes` property** with:

```json
"outcomes": {
  "type": "object",
  "description": "Every policy counted once by its two outcomes; the first five sum to policy_count. zero_baseline and negative_baseline count the quoted-both policies with a baseline payable premium of 0 and below 0; neither is in a band or a mover (03 §4.6).",
  "required": ["quoted_both", "quoted_to_declined", "declined_to_quoted", "declined_both", "error", "zero_baseline", "negative_baseline"],
  "properties": {
    "quoted_both": {"type": "integer", "minimum": 0},
    "quoted_to_declined": {"type": "integer", "minimum": 0},
    "declined_to_quoted": {"type": "integer", "minimum": 0},
    "declined_both": {"type": "integer", "minimum": 0},
    "error": {"type": "integer", "minimum": 0},
    "zero_baseline": {"type": "integer", "minimum": 0},
    "negative_baseline": {"type": "integer", "minimum": 0}
  }
}
```

S5's placement ("after `totals`", `"outcomes"` added to the top-level `required`) and its edits
2 to 4 stand.

### Item 4 — which side was wrong (`CLAUDE.md` §0)

**This ruling**, in DP-S2-2, S3, S4 and S5: it defined the banded set by the zero case alone, so
a negative baseline was banded and a mover under any change. **The plan** had the set right
(`baseline_minor > 0`, PL-1403 at `f6864de8` lines 395 and 924) and was wrong in one part: it
put the negative-baseline policy outside `zero_baseline` and in no other count, so the run
dropped it from every report silently. The spec was silent; FR-263 does not name the case.

### What N2 obliges

- **The SL-1386 executor** applies N2-a to N2-c in place of the texts they replace, in the same
  commit as S3 to S5.
- **PL-1403 (the planner's, pre-merge):** cite this section — "RL-1402, Amendment
  N2" until the mint, then `RL-<n>`'s — where the plan states N2: its audit-items paragraph
  (line 52), Task 0 Step 4 (lines 392-403, whose stop condition this section resolves: the S3
  copied into the ledger is N2-a's), and "The sets" (lines 924-928, where "outside
  `zero_baseline`" becomes "counted in `outcomes.negative_baseline`"). And, to agree with N2-c:
  `DislocationOutcomes` (lines 629-637) gains `negative_baseline: _Count`; the run's validator
  (lines 694-699) also refuses a run where Σ `distribution[].policies` ≠ `quoted_both` −
  `zero_baseline` − `negative_baseline`; the Task 2 test's `DislocationOutcomes(...)` (line 522)
  passes `negative_baseline=0`; the outcomes test (line 975) asserts seven figures, with
  `negative_baseline == 1` on the Task 5 fixture's negative-baseline policy; the bands test (line
  961) asserts the identity above. The PL-1267 delta in "What it obliges" reads "a required
  `outcomes` field" and needs no change.
- *Violation that must become detectable:* banding a negative baseline. Building the banded set
  as "compared less `zero_baseline`" puts the fixture's negative-baseline policy in a band and in
  `select_movers`' output, and fails both the bands identity and the movers' ordered list; the
  Slice 2 executor shows it red.
