# W32-5 — The two partial-dependence defects Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a GBM's partial-dependence curve say what its field names claim — that
`exposure_share` is a share of exposure rather than of rows, and that a point on a banded or
grouped factor's curve is a point on *that factor*, not on the raw column underneath it.

**Architecture:** Both defects live in one private helper, `_sweep`, in
`packages/pricing-core/src/pricing_core/modelling/diagnostics.py:895-968`. It has exactly one
caller (`:1052-1067`, inside `compute_gbm_diagnostics`), is absent from `__all__`, and is
reached from no test, no backend module and no script — so the whole slice changes no public
signature and no persisted shape. `PartialDependencePoint.exposure_share` already exists and
is already a `float` in `[0, 1]`: this is arithmetic under an unchanged name, so there is no
schema change and no contract to regenerate.

**Tech Stack:** Python 3.12, Polars, NumPy, XGBoost/LightGBM, pytest.
`scripts/bench-model.py` measures NFR-MODEL-14.

**Spec:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) — FR-MODEL-52 (partial dependence),
  FR-MODEL-118 (the cap, and its explicit deferral of the second defect), FR-MODEL-119,
  FR-MODEL-121 and FR-MODEL-122 (the neighbouring importance requirements, owned by W30 and
  **not** this slice), NFR-MODEL-14 (the diagnostics budget), §5.2's fenced block at
  lines 2148–2310.
- [`../roadmap.md`](../roadmap.md) — lines 3604–3614 (the first defect, recorded as two
  sub-defects) and 3615–3621 (the second), plus 704–713 where W5's closure recorded both.
- [`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) — line 95, this slice's row.
- [`2026-08-22-w5-closure.md`](2026-08-22-w5-closure.md) — lines 76 and 77, where both
  defects were written down at the close of the modelling workstream.

---

## Global Constraints

Copied from [`../../CLAUDE.md`](../../CLAUDE.md). Every task's requirements implicitly
include this section.

- **`pricing-core` imports no FastAPI, SQLAlchemy or Redis** (ADR-0001). This slice is
  entirely inside `packages/pricing-core/` and `packages/model-schema/`'s docstrings.
- **Requirement IDs are permanent** (§5): append, never renumber. This slice appends one
  requirement to `02` §3. Highest ids in use: FR-MODEL-123, NFR-MODEL-14.
  Next free: `FR-MODEL-124` is taken by the W32-4 plan of the same date, so this plan takes `FR-MODEL-125`.
  Do not renumber if the two land out of order — take the id this plan names.
- **When code and spec disagree, resolve it — do not quietly change one to match the other**
  (§0). Task 4 carries three resolutions, one of which changes the *spec* because the code is
  right, and one of which adds an obligation the spec never stated.
- **A negative test for every invariant** (§13), and enforcement proven on deliberately
  broken input (§13 rule 4). Both defects survived a green suite, and Task 1 Step 1 explains
  precisely which assertion let each one through.
- **NFRs are measured, not asserted** (§13 rule 5). Task 4 re-measures NFR-MODEL-14 and
  quotes `/proc/loadavg` beside the number — this machine is shared between concurrent agent
  sessions, and the same measurement has read 8.58 s at load 1.6 and 20.01 s at load 8.4.
- **`money` is not involved anywhere in this slice**; exposure is a float weight column.
- **A fresh worktree has no `.venv`.** Run `uv sync --all-packages --dev` first, or `mypy`
  reports several hundred phantom errors that read as real defects.
- **The worktree guard refuses compound shell commands.** Run each command plainly rather
  than joining them with `&&`.

### The gate

Run all of this before opening a PR, reading each command's **own** exit code.

```bash
uv sync --all-packages --dev
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```

**The frontend half is not needed.** `grep -rn "exposure_share\|partial_dependence\|PartialDependence" frontend/src frontend/tests`
returns nothing — no view plots this curve yet, and no committed contract file changes,
because the field's name, type and bounds are all unchanged. The roadmap pairs this defect
with "the frontend that first plots the curve"; that frontend is W6b's and is not this slice.

### What this slice deliberately does not touch

`packages/pricing-core/src/pricing_core/modelling/transparency.py:268` computes
`exposure_share=float(mask.sum()) / max(rows, 1)` and `:398` hardcodes `exposure_share=1.0` —
the same arithmetic under the same name, in the SHAP fidelity path. It is left alone because
`02` §5.2 line 1334 is the only spec text using that token and it names *that* site,
describing it as a percentage of rows: changing it is a separate resolution with a separate
requirement, and folding it in here would make one commit answer two questions. Record it as
a finding at close; do not fix it in this branch.

---

## File structure

| File | Change | Responsibility |
|---|---|---|
| `packages/pricing-core/src/pricing_core/modelling/diagnostics.py` | Modify `_sweep` `:895-968` and its call site `:1052-1067` | Both defects. Nothing else in the module changes |
| `packages/pricing-core/tests/test_gbm.py` | Modify `:667-680`, append | The assertions that let both defects through, replaced by ones that cannot |
| `scripts/bench-model.py` | Modify `:401-403` | A stale docstring that still describes the pre-cap behaviour |
| `docs/specs/02-modelling.md` | Modify §3, `:2255-2263` | The new requirement; `compute_gbm_diagnostics`'s missing parameter |
| `docs/roadmap.md` | Modify `:3604-3621` | Both defect records get their resolution and its date |

**Ordering.** Task 1 → Task 2 → Task 3 → Task 4. Task 1 and Task 2 both edit `_sweep` and
must not be given to two workers in parallel — W32-1's ledger recorded that fan-out is bounded
by file collisions, and this is a function collision inside one file. Task 3 depends on both.

---

### Task 1: Weight the shares by exposure

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/diagnostics.py` — `_sweep`'s
  signature (`:895`), `:927`, `:938`, `:949`, `:953`, `:965`, `:967`, and the call at `:1052`
- Test: `packages/pricing-core/tests/test_gbm.py` — replace `:667-680`, append two

**Interfaces:**
- Consumes: `_weights(spec, data)` at
  `packages/pricing-core/src/pricing_core/modelling/diagnostics.py:127`, which returns the
  exposure/weight vector a spec declares, or a vector of ones where it declares none.
- Produces: `_sweep` gains `spec` as its third positional parameter, matching
  `_permutation_importances(model, data, spec, ...)` at `:821`. `_sweep` stays private and
  stays out of `__all__`, so no other module's signature changes.

**The defect, in four places.** `_sweep`'s own docstring (`:919-921`) states the contract:
the ranking that decides which levels the cap keeps, and the share each surviving point
emits, must agree. Today both are row counts, so they agree with each other and disagree with
the field's name and with what an actuary reads off the chart. Four sites compute a row
count:

| Line | What it does today | What it must do |
|---|---|---|
| `:938` | `value_counts(sort=True)` — ranks levels by row count, deciding which the cap keeps | Rank by summed exposure |
| `:949`, `:953` | The omission record's share — how much was dropped | Summed exposure of the dropped levels over total exposure |
| `:965` | `shares.append(1.0 / len(labels))` — a constant, for a numeric grid | Summed exposure of the rows falling in each grid cell over total exposure |
| `:967` | The categorical point's share | Summed exposure of that level's rows over total exposure |

`:965` is the more serious of the two sub-defects the roadmap records: `1.0 / len(labels)` is
not a wrong weighting, it is not a measurement at all — every point on a numeric curve claims
identical exposure regardless of where the portfolio actually sits.

**The precedent to copy.** `_partition` at `:333-448` does both halves right in this same
module: it takes `spec`, calls `_weights`, and ranks and reports on the same weighted
quantity. `_permutation_importances` at `:821-832` is the precedent for the *signature*
change — `spec` as the third positional parameter, `weights = _weights(spec, holdout)` at
`:846`. That function shares this defect at `:870`, but its FR-MODEL-119/121/122 block
(`:853-867`) is owned by W30 and is **out of scope here**; do not fix it in passing.

- [ ] **Step 1: Replace the test that let the defect through**

`test_partial_dependence_carries_the_exposure_share_of_each_point` at
`packages/pricing-core/tests/test_gbm.py:667-680` asserts only that the shares sum to
approximately 1.0 — which is true of a row-count share and of an exposure share alike, and is
exactly why the defect survived a green suite for a fortnight. Replace it with:

```python
@pytest.mark.req("FR-MODEL-52")
def test_partial_dependence_shares_are_exposure_and_not_row_counts() -> None:
    """A frame where the two definitions disagree by construction.

    `rare` has few rows and almost all the exposure; `common` has most of the rows and
    almost none. A row-count share ranks and reports them one way and an exposure share the
    other, so this test can only pass under one of the two definitions — which the previous
    `sum == approx(1.0)` assertion could not distinguish, and did not.
    """
    import polars as pl

    from pricing_core.modelling.diagnostics import compute_gbm_diagnostics

    n_common, n_rare = 400, 20
    frame = pl.DataFrame(
        {
            "area": ["common"] * n_common + ["rare"] * n_rare,
            "exposure_years": [0.01] * n_common + [10.0] * n_rare,
            "claim_count": [0] * n_common + [1] * n_rare,
        }
    )
    diagnostics = _diagnose(frame, factor_columns=("area",))
    curve = _curve_for(diagnostics, "area")
    share = {point.label: point.exposure_share for point in curve.points}

    # Row counts: common 0.952, rare 0.048. Exposure: common 4.0/204.0 = 0.0196,
    # rare 200.0/204.0 = 0.980. The two orderings are opposite.
    assert share["rare"] > share["common"]
    assert share["rare"] == pytest.approx(200.0 / 204.0, abs=1e-6)
    assert share["common"] == pytest.approx(4.0 / 204.0, abs=1e-6)
    assert sum(share.values()) == pytest.approx(1.0)
```

Add the `_curve_for` helper beside the other module-level helpers in `test_gbm.py`, if one
does not already exist:

```python
def _curve_for(diagnostics, factor_slug: str):
    """The one partial-dependence curve for a factor, or a failure naming what was there.

    A bare `[0]` on an empty list raises `IndexError` and tells the reader nothing about
    which factors the diagnostics actually carried.
    """
    for curve in diagnostics.partial_dependence:
        if curve.factor_slug == factor_slug:
            return curve
    available = [curve.factor_slug for curve in diagnostics.partial_dependence]
    raise AssertionError(f"no curve for {factor_slug!r}; got {available}")
```

Adapt `_diagnose`'s call to whatever signature it has at `packages/pricing-core/tests/test_gbm.py:596-606`
— it is the established driver and this test must go through it rather than around it.

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest "packages/pricing-core/tests/test_gbm.py::test_partial_dependence_shares_are_exposure_and_not_row_counts" -q`

Expected: FAIL on `assert share["rare"] > share["common"]`, with `rare` at about 0.048 and
`common` at about 0.952 — the row-count answer, stated out loud.

- [ ] **Step 3: Write the second failing test, for the numeric grid**

The numeric arm's defect is a different one — a constant rather than a wrong weighting — and
the categorical test above cannot see it. Append:

```python
@pytest.mark.req("FR-MODEL-52")
def test_a_numeric_partial_dependence_point_carries_the_exposure_at_that_value() -> None:
    """`1.0 / len(labels)` was not a wrong weighting; it was no measurement at all.

    Every point on a numeric curve claimed identical exposure regardless of where the
    portfolio sat, so a chart showed a confidently flat exposure profile for a book that
    was concentrated at one end of the range.
    """
    import polars as pl

    from pricing_core.modelling.diagnostics import compute_gbm_diagnostics

    n = 400
    # Age is uniform on the grid, but exposure is concentrated in the young half, so a
    # per-cell exposure share must be visibly non-uniform while the row counts are flat.
    ages = [20 + (i % 40) for i in range(n)]
    frame = pl.DataFrame(
        {
            "driver_age": ages,
            "exposure_years": [5.0 if age < 40 else 0.05 for age in ages],
            "claim_count": [1 if age < 40 else 0 for age in ages],
        }
    )
    diagnostics = _diagnose(frame, factor_columns=("driver_age",))
    curve = _curve_for(diagnostics, "driver_age")
    shares = [point.exposure_share for point in curve.points]

    assert len(set(shares)) > 1, "every point carried the same share — the constant is back"
    assert sum(shares) == pytest.approx(1.0)
    assert max(shares) > 10 * min(shares)
```

- [ ] **Step 4: Run it to verify it fails**

Run: `uv run pytest "packages/pricing-core/tests/test_gbm.py::test_a_numeric_partial_dependence_point_carries_the_exposure_at_that_value" -q`

Expected: FAIL on `len(set(shares)) > 1` with the message quoted above — every share equal to
`1.0 / len(labels)`.

- [ ] **Step 5: Thread `spec` into `_sweep`**

Change `_sweep`'s signature at `:895` so `spec` is its third positional parameter, exactly as
`_permutation_importances` takes it at `:821`, and compute the weight vector once at the top
of the body, beside `rows = data.height` (`:927`):

```python
    weights = _weights(spec, data)
    total_weight = float(weights.sum())
```

Keep `rows = data.height` — it is still used for the grid-size decisions — and update the
docstring at `:919-921` so its statement of the contract names exposure rather than rows:

```
    The level ranking that the cap applies and the share each surviving point emits are the
    same quantity, deliberately: a chart whose bars are ordered by one measure and labelled
    with another is a chart that cannot be read. Both are exposure (the spec's weight column,
    or ones where it declares none), not row counts — a row-count share on a motor book
    ranks a level held for a fortnight beside one held for a year.
```

- [ ] **Step 6: Replace the ranking at `:938`**

`value_counts(sort=True)` ranks by row count. Replace it with a group-by that sums the weight
column and sorts on that sum descending, so the cap keeps the most *exposed* levels. Build the
grouping frame from `data` plus the weight vector as a temporary column, and take the level
labels and their summed weights out of the result.

- [ ] **Step 7: Replace the three share computations**

- `:949` and `:953` — the omission record's share becomes the summed weight of the dropped
  levels divided by `total_weight`.
- `:965` — `shares.append(1.0 / len(labels))` becomes the summed weight of the rows whose
  value falls in that grid cell, divided by `total_weight`. Use the same cell boundaries the
  grid itself was built from, so a row is counted in exactly one cell.
- `:967` — the categorical share becomes that level's summed weight divided by
  `total_weight`, which Step 6's group-by has already computed.

Guard `total_weight` against zero the way `_partition` does — a frame whose weights sum to
zero has no exposure to apportion, and the shares are then all zero rather than `nan`.

- [ ] **Step 8: Update the call site**

At `packages/pricing-core/src/pricing_core/modelling/diagnostics.py:1052`, pass `spec` as the
third positional argument. The sweep runs over `holdout`, and `_weights(spec, holdout)` is the
holdout's own exposure — which is correct: a partial-dependence curve computed on the holdout
must report the holdout's exposure profile, not the training set's.

- [ ] **Step 9: Run both new tests**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q -k "exposure_share or exposure_at_that_value or shares_are_exposure"`
Expected: PASS.

- [ ] **Step 10: Run the load-bearing cap test**

Run: `uv run pytest "packages/pricing-core/tests/test_gbm.py::test_the_cap_keeps_the_most_exposed_levels_and_is_what_bounds_the_grid" -q`

Expected: PASS. Its assertion is `min(kept) >= max(dropped)`, and its name has claimed
"most exposed" since it was written — before this task it was true only of row counts, and it
is the test that most directly changes meaning here. **If it fails, the fixture it uses has
row counts and exposure ordered oppositely and the test was passing for the wrong reason** —
which is a finding, not a reason to weaken the test.

- [ ] **Step 11: Run the whole GBM suite**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q`

Expected: PASS, with `test_a_gbm_with_a_sparse_interaction_can_produce_diagnostics`
(`:1843-1889`) still reported as `xfail`. That test is a **`@pytest.mark.xfail(strict=True)`
owned by W30** — if this task turns it green, `strict=True` fails the run, and the correct
response is to stop and report it rather than to remove the marker.

- [ ] **Step 12: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/diagnostics.py packages/pricing-core/tests/test_gbm.py
git commit -m "fix(w32-5): partial-dependence shares are exposure, not row counts"
```

---

### Task 2: A point on a banded factor is a point on the factor

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/diagnostics.py` — `_sweep`'s
  `:925` (`column = factor.source_columns[0]`), the grid construction that follows it, and
  the hold at `:960`
- Test: `packages/pricing-core/tests/test_gbm.py` — append two

**Interfaces:**
- Consumes: `resolve_factors` at
  `packages/pricing-core/src/pricing_core/modelling/factors.py:106`, whose type dispatch is at
  `:184-236`; `FactorMatrix` at `:85-103`. The resolved column is the raw source column for an
  `identity` factor and `f"{factor.slug}__resolved"` otherwise.
- Produces: no signature change. `_sweep` still returns the same `PartialDependence` shape;
  only its `label` values and the frame it hands `predict_gbm` change.

**The defect.** `_sweep` takes `factor.source_columns[0]`, builds its grid from *that raw
column's* values, and holds *that column* fixed while sweeping. For an `identity` factor that
is right and there is nothing to fix. For a banding or a grouping it is wrong twice over: the
curve has one point per raw value rather than one per band, so a 40-band age factor produces a
point per integer age; and the labels are raw values, so the chart's axis is not the axis the
model was fitted on. FR-MODEL-118 records this deferral explicitly — it is a known gap being
closed, not one being discovered.

**The hard constraint, and why the obvious fix is a silent no-op.** `predict_gbm`
(`packages/pricing-core/src/pricing_core/modelling/gbm.py:1185-1244`) takes the `if factors:`
arm at `:1210` whenever `factors` is non-empty, and that arm calls `resolve_factors`, which
**overwrites** any `{slug}__resolved` column the caller already set. `_sweep` always passes
`factors`. So writing a resolved column in `_sweep` today changes nothing at all, silently,
and a test asserting the curve's labels would be the only thing that ever noticed.

Two designs are available. **Take the first.**

1. **Hold the raw source column at a representative value per resolved level.** Grid over the
   resolved levels; for each, pick one raw value from the data that resolves to it, and hold
   the source column at that value. `predict_gbm` is unchanged, `resolve_factors` runs exactly
   as it does in production, and the resolution path under test is the real one.
2. Pre-resolve the frame, rename the resolved columns to the factor slugs, and call
   `predict_gbm` with `factors=()` so it takes the `else` arm at `:1215-1236`. This bypasses
   `resolve_factors` in the diagnostics path — so a resolution defect would show in scoring
   and not in diagnostics, which is the wrong way round — and it must not trip
   `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`. Rejected for the first reason; recorded here so the next
   reader does not re-derive it.

Under either design the frame must retain the exposure column, because `predict_gbm` computes
`_offset` from it at `:1244`.

**Cross factors are out of scope.** `resolve_factors` excludes cross operands from `terms`
(`:218-221`) and joins levels with `CROSS_SEPARATOR` (`:243`); a representative value for a
cross level is a tuple of raw values across several columns, which is a materially larger
change. Sweep cross factors as they are swept today and record the gap in Task 4's roadmap
note. The neighbouring xfail at `:1843-1889` is W30's and stays red.

- [ ] **Step 1: Write the failing test for a banded factor**

`grep -n "Grouping(" packages/pricing-core/tests/test_gbm.py` returns nothing and no
partial-dependence test in the file uses a banding, which is why this defect had no test to
fail. Append:

```python
@pytest.mark.req("FR-MODEL-118")
def test_a_banded_factor_has_one_partial_dependence_point_per_band() -> None:
    """The curve's axis must be the axis the model was fitted on.

    Forty integer ages behind four bands produced forty points labelled `20`, `21`, ...
    — a chart of the raw column, not of the factor. One point per band, labelled with the
    band, is what a reviewer comparing the curve against the fitted factor needs.
    """
    import polars as pl

    from pricing_core.modelling.diagnostics import compute_gbm_diagnostics

    n = 400
    ages = [20 + (i % 40) for i in range(n)]
    frame = pl.DataFrame(
        {
            "driver_age": ages,
            "exposure_years": [1.0] * n,
            "claim_count": [1 if age < 40 else 0 for age in ages],
        }
    )
    banding = _age_banding()  # four bands: [20,30) [30,40) [40,50) [50,60)
    diagnostics = _diagnose(
        frame, factor_columns=("driver_age",), bandings={banding.id: banding}
    )
    curve = _curve_for(diagnostics, "driver_age")

    assert len(curve.points) == 4, [point.label for point in curve.points]
    assert {point.label for point in curve.points} == set(banding.level_labels())
    assert sum(point.exposure_share for point in curve.points) == pytest.approx(1.0)
```

Build `_age_banding()` from whatever constructor
`packages/model-schema/src/model_schema/factors.py` publishes for a banding with four
half-open intervals over `driver_age`, and replace `banding.level_labels()` with whatever the
`Banding` shape actually calls its ordered level labels. Copy the construction idiom from an
existing banding test rather than inventing one — `grep -rn "Banding(" packages/pricing-core/tests`
will find the nearest.

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest "packages/pricing-core/tests/test_gbm.py::test_a_banded_factor_has_one_partial_dependence_point_per_band" -q`

Expected: FAIL on `len(curve.points) == 4`, printing forty raw age labels. That printed list
**is** the defect, and seeing it is what proves the test is pointed at the right thing.

- [ ] **Step 3: Write the failing test for a grouped categorical factor**

A grouping fails differently from a banding — its levels are sets of source levels rather than
intervals, so a representative value is a member rather than a midpoint. Append:

```python
@pytest.mark.req("FR-MODEL-118")
def test_a_grouped_factor_has_one_partial_dependence_point_per_group() -> None:
    """Six regions behind two groups is two points, labelled with the groups.

    Asserted separately from the banding case because the two take different arms of
    `resolve_factors`'s type dispatch, and a fix that handles intervals and not
    membership would pass the banding test alone.
    """
    import polars as pl

    from pricing_core.modelling.diagnostics import compute_gbm_diagnostics

    regions = ["north", "south", "east", "west", "centre", "coast"]
    n = 420
    values = [regions[i % len(regions)] for i in range(n)]
    frame = pl.DataFrame(
        {
            "region": values,
            "exposure_years": [1.0] * n,
            "claim_count": [1 if v in ("north", "south", "east") else 0 for v in values],
        }
    )
    grouping = _region_grouping()  # {"inland": north/south/east, "coastal": west/centre/coast}
    diagnostics = _diagnose(
        frame, factor_columns=("region",), groupings={grouping.id: grouping}
    )
    curve = _curve_for(diagnostics, "region")

    assert {point.label for point in curve.points} == {"inland", "coastal"}
    assert sum(point.exposure_share for point in curve.points) == pytest.approx(1.0)
```

- [ ] **Step 4: Run it to verify it fails**

Run: `uv run pytest "packages/pricing-core/tests/test_gbm.py::test_a_grouped_factor_has_one_partial_dependence_point_per_group" -q`
Expected: FAIL, with six raw region labels where two group labels belong.

- [ ] **Step 5: Grid over resolved levels**

In `_sweep`, replace the grid construction that starts at `:925`. Resolve the factor once,
against the same `bandings` and `groupings` the sweep was given, and read the grid's levels
off the *resolved* column:

- For an `identity` factor the resolved column **is** the source column, so this collapses to
  today's behaviour and nothing about the identity path changes.
- Otherwise the resolved column is `f"{factor.slug}__resolved"`, and the grid is its distinct
  values, ranked and capped by Task 1's exposure sum.
- For a cross factor, keep today's behaviour and skip this branch, per the scope note above.

Build the label from the resolved value, so the point's `label` is the band or group name
rather than a raw number.

- [ ] **Step 6: Hold the source column at a representative value**

Replace the hold at `:960`. For each resolved level, choose one raw value from `data` that
resolves to that level — the first such row's value is sufficient and is deterministic once
the frame's order is fixed — and set the *source* column to it across the swept frame.
`predict_gbm` then runs `resolve_factors` exactly as it does in production and maps every row
back to the level being held.

Two things must hold and are worth asserting in the implementation rather than discovering in
a test: the chosen representative must come from `data` (a synthesised value may fall outside
every band and trip `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`), and the exposure column must survive
into the frame handed to `predict_gbm`, because `_offset` reads it at `gbm.py:1244`.

- [ ] **Step 7: Run both new tests**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q -k "per_band or per_group"`
Expected: PASS, 2 tests.

- [ ] **Step 8: Run the pooled-other constraint test**

Run: `uv run pytest "packages/pricing-core/tests/test_gbm.py::test_a_pooled_other_bar_cannot_be_computed" -q`

Expected: PASS unchanged — use the test's full name as it appears at
`packages/pricing-core/tests/test_gbm.py:1710`. It constrains what a fix to this defect is
allowed to do with the levels the cap dropped, and it is the reason Step 6 holds a
representative value rather than pooling the remainder into a synthetic bar.

- [ ] **Step 9: Run the whole GBM suite**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q`
Expected: PASS, with the W30 xfail at `:1843-1889` still red.

- [ ] **Step 10: Run `mypy` and `ruff`**

Run: `uv run mypy`
Run: `uv run ruff check .`
Expected: both PASS.

- [ ] **Step 11: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/diagnostics.py packages/pricing-core/tests/test_gbm.py
git commit -m "fix(w32-5): sweep a banded or grouped factor over its own levels"
```

---

### Task 3: Re-measure NFR-MODEL-14

**Files:**
- Modify: `scripts/bench-model.py:401-403`

**Interfaces:**
- Consumes: `_gbm_passes` at `scripts/bench-model.py:397-424`, and the partial-dependence work
  measured inside `bench_gbm` at `:368-394`. There is no separate PD phase and this task does
  not add one — PD is measured as part of the GBM phase, and that is where its cost belongs.
- Produces: a recorded measurement for Task 4's roadmap note.

**Why this is a task and not a footnote.** §13 rule 5 requires the number and its budget, and
Task 2 changes the number in a specific direction: sweeping a 40-value column as 4 bands cuts
the passes through `predict_gbm` by an order of magnitude for banded factors. Task 1 changes
it not at all — a weighted sum costs the same as a count. A slice that makes a budgeted path
faster should say so with a measurement, because the next person to read `0.0480` needs to
know which code produced it.

- [ ] **Step 1: Record the load before measuring**

Run: `cat /proc/loadavg`

Write the first figure down. **This machine is shared between concurrent agent sessions** and
the same benchmark has read 8.58 s at load 1.6 and 20.01 s at load 8.4 — a 2.3x contention
factor that reads exactly like a regression. If the first figure is above about 2.0, wait for
a quiet window rather than recording a number that cannot be compared to anything.

- [ ] **Step 2: Measure**

Run: `uv run python scripts/bench-model.py --only gbm`

Expected: a passes-per-fit figure at or below NFR-MODEL-14's budget of **0.06**. The last
recorded measurement was **0.0480**, giving 1.25x headroom; Task 2 should improve it or leave
it unchanged, and Task 1 should leave it unchanged. **A figure above 0.06 is a stop** — report
it rather than adjusting the budget, and note that `_gbm_passes` counts passes rather than
seconds, so a contended machine does not explain a rise.

- [ ] **Step 3: Fix the stale docstring**

`scripts/bench-model.py:401-403` still describes `_gbm_passes` as counting the passes "with no
cap" and cites OQ-MODEL-26 as an open question. The cap has existed since FR-MODEL-118 and
OQ-MODEL-26 is decided (`docs/open-questions.md:79`). Rewrite those lines to describe what the
function counts today, and state that a banded or grouped factor now costs one pass per level
rather than one per raw value.

- [ ] **Step 4: Verify the script still runs**

Run: `uv run python scripts/bench-model.py --only gbm`
Expected: PASS, same figure as Step 2 — a docstring change must not move the number, and this
step is what proves the edit did not touch the arithmetic.

- [ ] **Step 5: Commit**

```bash
git add scripts/bench-model.py
git commit -m "chore(w32-5): bench-model's GBM pass count describes the capped sweep"
```

---

### Task 4: Resolve the spec and close both roadmap records

**Files:**
- Modify: `docs/specs/02-modelling.md` — §3's requirement table, and `:2255-2263`
- Modify: `docs/roadmap.md:3604-3621`
- Modify: `packages/pricing-core/tests/test_gbm.py` — markers (Step 4)

**Interfaces:**
- Consumes: everything Tasks 1–3 built, and Task 3's measurement.
- Produces: no code. CLAUDE.md §0's resolution step, and §14 question 4's finding for this
  corner of `02`.

**Three findings, three verdicts.**

1. **The spec states no exposure obligation at all.** `exposure_share` appears twice in
   `02` — at line 1334 and at lines 2692–2694 — and neither is partial dependence. The field
   was named `exposure_share` in `model-schema` and computed as a row count in
   `pricing-core`, and no requirement adjudicated between them, so neither side could be
   called wrong from the document. A requirement is appended, because the next person to read
   the field name must be able to confirm from `02` that the name is the contract.
2. **§5.2's `compute_gbm_diagnostics` signature omits `max_partial_dependence_levels`**
   (`:2255-2263`). The parameter exists, is what FR-MODEL-118's cap is spelled as, and is
   overridden by `_diagnose_wide` in the test suite. The **code** is right; §5.2 is
   incomplete and gets completed. This was already true before this slice.
3. **Cross factors keep the old sweep.** Task 2 fixes bandings and groupings and leaves cross
   factors gridding over their first source column. That is a narrower gap than the one this
   slice found, and it is recorded rather than fixed — with an owner, per §13 rule 6, not left
   as silence.

- [ ] **Step 1: Append the requirement to `02` §3**

The requirement rows in `02` §3 are single lines of the form `| **FR-MODEL-N** | text |`.
Insert the row reproduced after the marker below — everything from the first `|` onward, as
one line — immediately after FR-MODEL-123's row (`docs/specs/02-modelling.md:244`).

Next free: `FR-MODEL-125` — the row to insert is: `| **FR-MODEL-125** | A partial-dependence point's `exposure_share` is a share of exposure, and the ranking FR-MODEL-118's cap applies is the same quantity. Added 2026-08-23 (W32-5). Between the diagnostics slice and this date all four computations were row counts: the level ranking, the omission record's share, the categorical point's share, and the numeric point's share — the last of which was the constant `1.0 / len(labels)` and so not a measurement of anything. A row-count share on a motor book ranks a level held for a fortnight beside one held for a year, and an actuary reading the chart has no way to see that it did. Exposure means the weight column the spec declares, or a vector of ones where it declares none, taken from the frame the sweep runs over — which is the holdout, because a curve computed on the holdout must report the holdout's profile. Where the weights sum to zero every share is zero rather than `nan`. The ranking and the emitted share are required to be the same quantity because a chart ordered by one measure and labelled with another cannot be read, and that requirement is the reason all four sites move together rather than only the two a reader would notice. |`

- [ ] **Step 2: Complete §5.2's `compute_gbm_diagnostics` signature**

At `docs/specs/02-modelling.md:2255-2263`, add `max_partial_dependence_levels` to the
published signature, copying its name, type and default from
`packages/pricing-core/src/pricing_core/modelling/diagnostics.py:971-987` rather than from
here. Add a blockquote after the fenced block:

```
> **`max_partial_dependence_levels` was missing from this signature until 2026-08-23
> (W32-5).** It is how FR-MODEL-118's cap is spelled, it has existed since the cap did, and
> a caller working from this page alone could not have known the sweep was bounded at all.
> The code was right and this block was incomplete.
```

- [ ] **Step 3: Close both roadmap records**

At `docs/roadmap.md:3604-3614` (the first defect, recorded as two sub-defects — the wrong
weighting and the constant) and `:3615-3621` (the second), append to each:

```
Fixed 2026-08-23 (W32-5), under the requirement Step 1 appends.
```

Add to the second record only:

```
Cross factors are **not** covered: they still grid over their first source column, because a
representative value for a cross level is a tuple across several columns. Owner: W6b, with the
frontend that first plots a cross factor's curve.
```

Append Task 3's measurement to the first record, in the form §13 rule 5 requires — the figure,
the budget, and the load average it was taken at:

```
NFR-MODEL-14 re-measured after the fix: <figure> passes/fit against the 0.06 budget, at load
average <loadavg>.
```

Leave the surrounding text as written; a roadmap entry records what was believed at its date.

- [ ] **Step 4: Mark the new tests with the new requirement**

Add the id allocated in Global Constraints and written out in Step 1 as a second marker on
both of Task 1's tests, so each carries `FR-MODEL-52` and the new id. `pytest` runs with
`--strict-markers` and `req-coverage.py` fails on a marker naming an id no spec defines, so
this step must come after Step 1 and never before it.

- [ ] **Step 5: Run the documentation checks**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
```

Expected: both PASS, with the new requirement reported as covered.

- [ ] **Step 6: Run the full gate**

Run every command in the gate block at the top of this plan, each on its own line, reading
each one's own exit code. `generate-contracts.py --check` must pass **without** a regenerate,
which is this slice's proof that no persisted shape changed.

- [ ] **Step 7: Commit**

```bash
git add docs/specs/02-modelling.md docs/roadmap.md packages/pricing-core/tests/test_gbm.py
git commit -m "docs(w32-5): specify the exposure share, complete 5.2, close both defect records"
```

---

## Closing the slice

- [ ] Every task's steps are checked.
- [ ] The gate passes locally. The frontend half is not required — nothing under `frontend/`
      and no committed contract file changes.
- [ ] `generate-contracts.py --check` passes without a regenerate.
- [ ] The W30 xfail at `packages/pricing-core/tests/test_gbm.py:1843-1889` is still red.
- [ ] Both roadmap defect records carry a resolution date and the measurement.
- [ ] The two findings recorded but not fixed — `transparency.py`'s row-count share, and cross
      factors — each have an owner written down.
- [ ] The branch is pushed and a PR is open. Do not force-push, do not merge, do not push to
      `main`.

## Self-Review

**1. Spec coverage.** The slice map's brief is *"the two partial-dependence defects"*. Task 1
is the first (all four of its sites, including the sub-defect the roadmap records separately);
Task 2 is the second. Task 3 satisfies §13 rule 5, which the slice would otherwise fail
because Task 2 moves a budgeted number. Task 4 writes the requirement that was missing and
completes the two §14 question-4 divergences found while reading. The two things explicitly
out of scope — `transparency.py` and cross factors — are named with reasons and owners rather
than passed over.

**2. Placeholder scan.** Steps 6 and 7 of Task 1 and Steps 5 and 6 of Task 2 describe
transformations rather than quoting replacement code, because each is a local rewrite of an
expression whose surrounding lines the implementer will be reading anyway — every one names
the exact line, the exact quantity, and the guard it needs. Three places defer a value that
cannot be written today and each says why: the requirement id (audit constraint, allocated in
Global Constraints), Task 3's measured figure (it is a measurement), and `_age_banding`'s
constructor shape (the `Banding` API is read from `model-schema`, and the step says which
grep finds the idiom).

**3. Type consistency.** `_sweep` gains `spec` as its third positional parameter, matching
`_permutation_importances(model, data, spec, ...)`; `_weights(spec, data)` is called with the
same argument order in both. `_curve_for(diagnostics, factor_slug)` is defined once in Task 1
Step 1 and used by both of Task 2's tests. `PartialDependencePoint.exposure_share` keeps its
name, its `float` type and its `[0, 1]` bounds throughout, which is what makes the whole slice
schema-neutral.
