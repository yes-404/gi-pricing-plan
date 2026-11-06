---
id: PL-2044
family: plan
kind: map
title: WK-1178 — A/E for a diagnostic partition is weighted by the declared scheme (OQ-1692 ruled (b), FD-1691), SL-2045 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-06   # original date 2026-11-05, working id 8358, minted 2026-11-06
owner: planner
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [OQ-1692, FD-1691, SL-1675, PL-1674, FR-111, FR-171, FR-183, FR-184, FR-186]
---

# PL-2044 — WK-1178: A/E weighted by the declared scheme (SL-2045, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a') (`.claude/roles/planner.md`, "Lean
> P2"). One slice row, SL 8359; no filed plan is edited. The executor's skills are `superpowers:test-driven-development`,
> `.claude/skills/python-test`, `spec-change` and `git-hygiene`. PL-2044, SL-2045 and LG-2046 (working ids 8358, 8359 and 8360 until the mint) are reserved by the
> lead. **This is a ruled number change.**

## Authority

**The ruling of record is the correction, closed, verbatim** (the maintainer's entry "2026-11-05 11:55:25 GMT" in
`~/gi-pricing-plan.local/channel/to-lead.md`):

> OQ-1692 RULING CORRECTED (my 11:50:05) and PLAN M. CORRECTION, verified at origin/main 2f108b1e: `_weights` (diagnostics.py:133–139) returns the OFFSET column first, so on a frequency model it is exposure, and "Σw·y / Σw·μ with `_weights`" would be the double count the same ruling forbids — the two clauses could not both hold; the GUARD is the substance and the `_weights` clause is STRUCK by this dated line. THE DEFINITION OF RECORD: A/E = Σw·y / Σw·μ where w = `ae_weights` = the model's DECLARED WEIGHT COLUMN, else 1 — severity: the claim count; frequency (exposure offset, `mu` already the expected count): 1, so Σy / Σμ unchanged; a pure-premium model lands on exposure only when it declares exposure as its weight column, and on 1 when it carries exposure as an offset (`mu` is then the expected total), which is the same principle — the weight is whatever makes w·y the aggregate, and an offset has already put the aggregate in `mu`. `_weights` stays for calibration, unchanged. T2's mutation swaps `_weights` back in and the frequency fixture catches the double count — that is the red the ruling asked for. FR-171/183/184's dated lines carry THIS wording, not 11:50's. DP-M1 (by-level `ci_95`, :406): `ratio·z/√Σw` under a weight column, byte-identical for frequency — ACCEPTED, the byte-identity proven by the frequency fixture's before/after, not asserted. DP-M2 (comparison.py:274's own unweighted `ae_overall`, verified): the SAME `ae_weights` — ACCEPTED; the comparison table and the Diagnostics page must print one number. DP-M3 (offset AND weight column both declared): the weight column — ACCEPTED as the rule, R0 enumerates the tree and quotes the count (expected 0); a hit is reported before T1, not resolved silently; R0 also enumerates the pure-premium case (how each burning-cost spec in the tree declares exposure) and quotes it. COUNT: "15" was my number from one predicate and does not travel — at 2f108b1e `git grep -lE ae_overall 2f108b1e -- '*test*'` prints 21 and `… -- 'packages/*/tests/*.py' 'backend/tests/*.py'` prints 15; the LG states its own predicate verbatim and the number it prints, and lists every file whose expected values move with each new value shown as the weighted sum. A moved value on a no-weight model = STOP (A9). SL-1913: any rehearsal note pinning a severity A/E is re-derived by dated line, named in the LG. The ~20 min window after the mutation, before the SOLO gate, ACCEPTED — moved values are read there first. PLAN M ACCEPTED at 6b85918a (PL-2044 / SL-2045 / LG-2046, working ids 8358 / 8359 / 8360 until the mint, base 2f108b1e, 6 h, SOLO gate after R, A and D) subject to the planner's FINAL head: if it moves, the lead names the delta and I accept on the diff as with G. The 11:50 fallback stands: chain slipping at the Tue 10 18:00 census → (a) with a named carry, the OQ open with this ruling recorded as deferred.

**The ruling it corrects, for the record** (the entry "2026-11-05 11:50:05 GMT"; **its `_weights` clause is STRUCK** by the entry above, and FR-171, FR-183 and FR-184
carry the correction's wording, not this one's):

> OQ-1692 RULED (b) — A/E for a diagnostic partition is WEIGHTED BY THE DECLARED SCHEME: overall and by-level A/E = Σw·y / Σw·μ with
> `_weights` (diagnostics.py:132–139) under the scheme `_weighting` records on the partition (:444), as calibration already does
> (:406–408). Read in both mirrors (open-questions.md:122, 02-modelling.md:3417) and FD-1691 (register :366). REASON: FR-184 requires
> each metric's scheme explicit and FR-171 already calls the A/E exposure-weighted; a per-row ratio on a severity book is
> total-cost-wrong, not mislabelled — an actuary reads that figure first, and a wrong headline number is a mispricing-class defect, the
> register's own test for a code fix before the freeze. THE GUARD IS PART OF THE RULING: the weight is the one that turns the per-row
> response into its aggregate — the claim count for severity (Σ count·severity = total cost), exposure for a pure premium per unit; for
> a COUNT response whose `mu` already carries exposure (frequency, calibration divides it by exposure), the weight is 1, so Σy / Σμ is
> unchanged there and exposure is never counted twice. M PROVES IT RED FIRST: a severity fixture with varying claim counts where the
> per-row and the weighted ratio differ by a known amount; a frequency fixture with varying exposure whose A/E equals Σy / Σμ before and
> after. SPEC IN THE SAME COMMIT: FR-171's definition gets the formula by dated line, FR-183 gains the weighting clause, FR-184's label
> clause names the scheme the partition records; OQ-1692 → DECIDED in BOTH mirrors, same wording; FD-1691 closes on M's merge (dated line
> citing M's PR). Persisted values: a changed `ae_overall` on severity models is the intended effect — the LG lists the 15 test files it
> touches and the fixtures re-derived, each new expected value shown as the weighted sum, not retyped. (c) NOT taken: no contract widening
> before the freeze. FALLBACK: if the Tue 10 18:00 census shows the chain slipping, (a) with a named carry — the OQ then stays OPEN with
> this ruling recorded as the decision deferred to P3's first slice, never silently. Not a third exception: ruled today, inside Fri 6.

Also: triage2 (`c9e75802158f`) §3 "NEW slice M", and "a number change a week before the rehearsal, so it needs its own gate rather than a
ride".

## Goal

Overall and by-level A/E on every partition is Σw·y / Σw·μ with the weight that turns the row into its aggregate. Severity moves, frequency does
not by construction. The spec, both OQ mirrors and FD-1691 close with it. No contract shape changes.

## Evidence at `2f108b1e`

Every cite was read at `origin/main` `2f108b1eda22a4835279cee9b4c9e305babe3662`, in
`packages/pricing-core/src/pricing_core/modelling/diagnostics.py` unless named.

- **The defect.** `_partition` (`:353`): `exposure = _weights(spec, data)` (`:380`), `scheme = _weighting(spec)` (`:381`), `ae_overall = Σy / Σmu`
  (`:383-385`); by level `actual`, `expected`, `ratio` (`:393-400`). Calibration divides by `bin_exposure`.
- **`_weights` and the guard are not one function** (the correction, 11:55:25). `_weights` (`:135-141`) returns the
  **offset column first**, then the weight column, then ones, and calibration needs that. For a frequency model it returns exposure. `Σ exposure·y /
  Σ exposure·μ` is the double count the guard forbids. **So A/E needs its own selection:** a declared weight column, else ones. A frequency model
  or a pure premium carrying exposure as an offset gets 1, unchanged. Severity (weight column, the claim count) moves. A pure premium declaring
  exposure as its weight column moves. That is the definition of record in one rule, and `_weights` stays as it is for calibration, lift and the
  deviance.
- **`_weighting` (`:124-133`)** returns `EXPOSURE` for an offset, `CLAIM_COUNT` for a weight column, else `COUNT`. A weight column holding exposure is
  therefore labelled `CLAIM_COUNT`. Pre-existing; the label cannot grow a value (no contract widening), so FR-184's clause says "the declared weight".
- **The interval breaks when `actual` changes meaning.** `half = _NORMAL_975 * sqrt(actual) / expected` (`:404`), and its comment: "treating the claim
  count as the only random quantity". That holds where `actual` is a count. For severity it is already dimensionally wrong (√ of a money sum), and
  under the ruling `actual` is total cost. The ruling is silent. DP-M1.
- **A second `ae_overall`.** `comparison.py:274`, `_metrics`, computes `Σactual / Σmu` on the shared holdout under the same name, with `directions` at
  `:284` calling it closer-to-one-is-better. The ruling says "a diagnostic partition". Left alone, one model shows two A/Es under one name. DP-M2.
- **The consumers read the fields and need no change:** `frontend/src/views/DiagnosticsView.vue:46`, `BacktestView.vue`, `AeByFactorChart.vue:49,80`. All
  three `_partition` callers go through one function (`:759`, `:772`, `:930`), so backtests move too.
- **The 15 test files naming `ae_overall`** (`git grep -l ae_overall origin/main -- backend/tests packages tests frontend/src`, less source): backend
  `test_api_backtests.py`, `test_backtests.py`, `test_diagnostics.py`, `test_ebm_model_jobs.py`, `test_glm_approximation_model.py`, `test_model_jobs_gbm.py`,
  `test_wf01_journey.py`; `frontend/src/views/__tests__/fixtures.ts`; model-schema `test_backtests.py`, `test_comparison.py`,
  `test_cross_validation_diagnostics.py`, `test_partition_zero_weight_count.py`; pricing-core `test_backtests.py`, `test_comparison.py`, `test_diagnostics.py`, and
  `test_gbm.py` (16 by this predicate, which includes the frontend fixture. **The count does not travel** (11:55:25): the LG states its own predicate
  verbatim and the number it prints). Most construct shapes or use
  frequency fits, so **few values are expected to move.** Which do is found by running them, not assumed.
- **The spec.** FR-171 (`02:303`), FR-183 (`:315`), FR-184 (`:316`). OQ-1692: `02:3417` and `docs/open-questions.md:122`. The §4 example `:1698` (`"ae_overall",
  "weighting": "exposure"`) stands. `02:2997`: "`05` reuses `compute_diagnostics`' A/E computation on live data", so monitoring inherits this.
- **Stored values.** FR-170 computes diagnostics once at fit time, so existing rows keep their old figure. A new severity fit shows the new one.
  `MODELS_NOT_COMPARABLE` does not separate old from new.

## Decision points

**None open.** All three are ruled by the entry "2026-11-05 11:55:25 GMT": DP-M1 `ratio·z/√Σw` under a weight column, "the byte-identity proven by the frequency fixture's
before/after, not asserted"; DP-M2 the same `ae_weights` in `comparison.py`; DP-M3 the weight column, "a hit is reported before T1, not resolved silently". For a weight column
holding exposure, Σw is exposure, not claims, so the interval there is an approximation, and the code comment says so.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge tree. Items 1 and 2 apply to this plan; A1 to A11 apply to
the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing line except check 31 / check 32 lines naming working ids
   8358, 8359 or 8360. After the mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set. `docs/contracts/` is not in it, and `generate-contracts.py --check` rc 0 (no
  contract widening, ruled).
- **A2. Spec in the same commit as the code** (ruled): one commit carries FR-171, FR-183, FR-184, both OQ mirrors and the `diagnostics.py` change.
  `audit-docs.py` passes at it but for working ids.
- **A3. The severity red.** T1, a fixture with varying claim counts, whose per-row and weighted ratios differ by a known amount, worked by hand in the test: red at
  the base with that per-row value.
- **A4. The frequency guard.** T2, varying exposure: `ae_overall` equals Σy / Σμ **before and after**, quoted at base and head; by-level likewise. A mutation using
  `_weights` in place of the A/E weight reds it: the double count is shown caught.
- **A5. The pure premium, both declarations.** T3: exposure declared as the weight column gives Σ exposure·y / Σ exposure·μ; exposure carried as an offset gives Σy / Σμ.
- **A6. By level.** T4: a cell's `actual`, `expected` and `ae` are the weighted sums, and `ae_overall` is the total of the same sums.
- **A7. The interval,** `ratio·z/√Σw` under a weight column: T5, and frequency's `ci_95` byte-identical, **proven by the frequency fixture's before and after at base and head, not asserted**.
- **A8. The comparison:** T6: `comparison.py`'s `ae_overall` and the Diagnostics partition print one number on one fixture, by one `ae_weights`.
- **A9. The test files.** LG-2046 states its own predicate verbatim and the number it prints, and lists every file whose expected values move. **Each new expected value is shown as the weighted
  sum, not retyped** (the ruling): in the test as an expression where it can be, else derived in the LG from the fixture's rows. A value that moves on a model with no
  weight column is a STOP: the guard failed. **SL-1913:** any rehearsal note pinning a severity A/E is re-derived by dated line, named in the LG.
- **A10. Both mirrors.** `git grep -n 'OQ-1692' -- docs/specs/02-modelling.md docs/open-questions.md` shows DECIDED in both, the same wording, and `audit-docs.py`'s mirror
  checks pass.
- **A11. The gate and the records.** The GREEN set by import closure (common seat brief, item 29). **The full code gate, both halves, SOLO, its own, never a ride** (triage2
  §3). **FD closing act in the FD-1842 form, in the slice's own PR, by the slice's auditor:** FD-1691, a dated line citing M's PR, as ruled. **The LG Audit section, with the
  lead's adoption, lands in the audit's own commit**, and `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. No contract widening** (ruled). `AeCell` and `PartitionDiagnostics` keep their fields. `Weighting` gains no value.
- **G2. `_weights` and `_weighting` are unchanged.** Calibration, lift, deviance and Gini do not move; any of them moving is a STOP.
- **G3. Exposure is never counted twice** (ruled). T2 is the proof.
- **G4. Stored diagnostics are not rewritten or back-filled.**
- **G5. FR-111's weight-0 rows are already removed** before `_partition`; a zero never reaches a Σw.
- **G6. The fallback, ruled:** if the Tue 10 Nov 18:00 census shows the chain slipping, (a) with a named carry: OQ-1692 stays OPEN with this ruling recorded as the decision
  deferred to P3's first slice, never silently. The lead names it; the slice then stops and keeps its branch.
- **G7. Red first, by cause. No test is removed or weakened** (common seat brief, item 13). A value re-derived by A9 is not a weakening.

## Needs

No DB window of its own: T1 to T6 are pricing-core tests through `~/gi-pricing-plan.local/handover/run-small.sh`. The backend files among the 15 are DB-backed and are proved in
the gate, but **moved values are read first in a lead-granted DB window** (ruled; about 20 min, **after the mutation, before the SOLO gate**, a `createdb -T` copy, **never the template**, Redis `-n 11`, `12` or `13`,
never db 0, which is live, ending with the two quoted zeros). No docker beyond that;
nothing on the NFR VM.

## Tasks

### SL-2045 — the weighted A/E

**The row.** Ahead of G (the lead's order). WK-1178. One `sonnet` executor. Requirements: `02` FR-171, FR-183, FR-184, FR-186 (under DP-M2). Register: FD-1691 (MEDIUM), closing at the
merge. Depends on: the GO; the window; a gate slot, after R, A and D (triage2 §5). **Size:** 6 h (triage2 5 h, plus the interval and the comparison). SOLO gate
about 2.5 h, not counted. Merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list, or the ruled fallback from Tue 10 18:00.

**R0.** Re-read every cite at the base. Run A9's predicate. **Enumerate over the tree and quote, before T1** (ruled): every spec declaring both an offset and a weight column, count expected 0, a hit reported, not resolved silently; and how each
burning-cost or pure-premium spec declares exposure, as a weight column or as an offset. Search `examples/`, `scripts/`, `backend/` and `packages/`, with the predicate quoted.

**R1 — red first (uncommitted until R2).** `packages/pricing-core/tests/test_diagnostics.py`, `req("FR-171")` and `req("FR-184")`:

- **T1** `test_a_severity_books_ae_is_weighted_by_the_claim_count`. Rows `y = (1000, 2000)`, `w = (1, 9)`, `mu = (1100, 1900)`: per-row `3000 / 3000 = 1.0`, weighted `19000 / 18200`.
  **Red:** `1.0`.
- **T2** `test_a_frequency_books_ae_ignores_exposure_because_mu_carries_it`, exposures varying, the expected value written as `sum(y) / sum(mu)`. **Green at base and head;** the
  mutation of A4 is the red.
- **T3** the pure premium, both declarations, **T4** by level, **T5** the interval.
- **T6**, `test_comparison.py`, `req("FR-186")`.

**R2 — green, one commit (A2).** In `diagnostics.py`, beside `_weights`:

```python
def ae_weights(spec: ModelSpecCommon, data: pl.DataFrame) -> npt.NDArray[np.float64]:
    """A/E's weight (OQ-1692, as corrected 2026-11-05 11:55:25): the declared weight column, else 1.
    Whatever makes w·y the aggregate: an offset has already put the aggregate in `mu`, so a
    frequency model gets 1 and exposure is never counted twice. This is **not** `_weights`,
    which is the offset first, for calibration."""
    if spec.weight.kind == "column" and str(spec.weight.column) in data.columns:
        return data[str(spec.weight.column)].cast(pl.Float64).to_numpy()
    return np.ones(data.height, dtype=np.float64)
```

`_partition`: `w = ae_weights(spec, data)`; `expected_total = Σ w·mu`, `actual_total = Σ w·y`; by level, the same over `mask`, and `half = ratio * _NORMAL_975 / math.sqrt(n)`, `n` being `Σ w[mask]` under a weight column and `actual` otherwise, with the guard on `n > 0`. `exposure_years` stays
`Σ exposure`. `comparison.py:274`: `Σ w·actual / Σ w·mu` with `ae_weights(candidate.spec, holdout)`.

**The spec, same commit, under `spec-change`, dated, citing the 11:55:25 entry and this plan, in its wording, not 11:50's:**

- **FR-171:** "A/E = Σw·y / Σw·μ, where w is the model's declared weight column, else 1: the claim count for severity; 1 for frequency, whose μ is already the expected count, so Σy / Σμ
  is unchanged; a pure-premium model lands on exposure only when it declares exposure as its weight column, and on 1 when it carries exposure as an offset."
- **FR-183:** the same weighting on train and holdout, so the two sides are one statistic.
- **FR-184:** the A/E's label is the scheme the partition records.
- **OQ-1692,** both mirrors, the same wording: DECIDED 2026-11-05: (b) as corrected by the entry above; (c) not taken.

**R3 — the test files.** A9. **G.** A11.

### Write set

`packages/pricing-core/src/pricing_core/modelling/diagnostics.py`, `comparison.py`; the test files A9 finds moved; `docs/specs/02-modelling.md`, `docs/open-questions.md`; LG-2046 under
`docs/ledgers/`. At the mint: the SL-2045 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, FD-1691's essay and `docs/findings/register.md`.

### Files shared with other groups

`docs/specs/02-modelling.md`: **C** (the factors row) and **LAST-1** no; different rows, a textual re-merge at most. `docs/open-questions.md`: docs batches, one row. `packages/pricing-core/tests/test_gbm.py`:
**G** adds a test there, and M touches it only if a value moves. **Safe in parallel for building: all.** Its gate is its own, after R, A and D; its window is serial with all.

## Hand-off (not this plan's writes)

- The GO: the maintainer. The Tue 18:00 census and the fallback's call: the lead and the maintainer. The window and the gate: the lead. The LG: the executor. The close: the auditor.
- **For SL-1913 and the demo:** a severity model fitted after this merge shows a different headline A/E from any figure in a rehearsal note. A note that pins one is re-derived by dated line, named in the LG (A9).
- `05`'s monitoring A/E inherits the definition (`02:2997`): when it is built, its spec says so. No P2 code.

## Self-review

1. **Every cite was read** at `2f108b1e`. 2. **Requirements by id**, no range. 3. **No placeholder.** 4. **The rulings are verbatim:** the correction of 11:55:25 is of record, and 11:50:05 is kept with its struck clause marked. 5. **The red is by cause,** with worked numbers. 6. **The count** does not travel: the LG states its own predicate. 7. **Calendar:** 10 Nov 2026 is a Tuesday, 12 Nov a Thursday.
