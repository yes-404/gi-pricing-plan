# Transparency Exposure Share Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the transparency artifact's `exposure_share` a share of exposure everywhere it
survives, and delete the one place where it was never a measurement at all.

**Architecture:** Two defects in `pricing-core`'s `transparency.py`, both closing the gap W32-5
closed one module away in `diagnostics.py`. FR-MODEL-36's worst-region share is computed as
`mask.sum() / rows` and becomes a weighted share, reusing `diagnostics.py`'s existing `_weights`
and `_share` helpers rather than growing a second pair; the prose that renders it says "of rows"
and becomes "of exposure". FR-MODEL-79's `ShapInteraction.exposure_share` is the literal `1.0`
by construction and is deleted from the shape, the producer, the authored contract and the drift
guard's reached-path list. The two halves share no code and are separate tasks; only the shape
deletion touches the published contract.

**Tech Stack:** Python 3.12, Polars, NumPy, Pydantic v2, `pytest`, `uv`.

**Spec:** [`../specs/02-modelling.md`](../specs/02-modelling.md) — FR-MODEL-36 (the fidelity
statement and its worst regions), FR-MODEL-79 (interaction candidates), with FR-MODEL-125 as the
precedent this mirrors and OQ-MODEL-31 as the decision that withdrew the interaction share.

**Proposed slice id:** `W32-9`. The W32 slice boundaries in
[`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) are recorded as *pending* maintainer
acceptance and stop at `W32-6`; this number is a proposal, not an accepted allocation.

## Global Constraints

- No new requirement ids. Every id cited here already exists in
  [`../specs/02-modelling.md`](../specs/02-modelling.md).
- No pandas. Polars and NumPy only.
- `pricing-core` stays importable standalone: no FastAPI, SQLAlchemy, Redis or `app` import may
  enter it. `.importlinter`'s `core-has-no-infrastructure` contract enforces this.
- A shared helper may **not** move into `model-schema`: the `schema-depends-on-pydantic-only`
  contract forbids polars and numpy there.
- Do not hand-edit anything under `docs/contracts/schemas/generated/` or
  `docs/contracts/openapi/`. Regenerate with `uv run python scripts/generate-contracts.py`.
- Every new test carries a `@pytest.mark.req(...)` marker naming a requirement that exists —
  `--strict-markers` is on, and `scripts/req-coverage.py` reads these.
- Conventional Commits. Commit at the end of every task.

---

### Task 1: The worst-region share becomes exposure

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/transparency.py:237-274` (`_worst_regions`)
- Modify: `packages/pricing-core/src/pricing_core/modelling/transparency.py:222-224` (the call site)
- Test: `packages/pricing-core/tests/test_transparency.py`

**Interfaces:**
- Consumes: `_weights(spec, data) -> npt.NDArray[np.float64]` (`diagnostics.py:128-134`) and
  `_share(weight: float, total_weight: float) -> float` (`diagnostics.py:896-906`). `_weights`
  returns the offset column when `spec.offset.kind` is `log_column` or `column`, else the weight
  column, else ones. `_share` returns `0.0` rather than `nan` when the denominator is zero.
- Produces: `_worst_regions(data, factors, target, approximated, *, spec, bandings, groupings)
  -> tuple[WorstRegion, ...]` — one new keyword-only parameter, `spec: ModelSpecCommon`.

The frame is the **train** frame, not the holdout. This is the deliberate difference from
FR-MODEL-125, and `transparency.py:206-208` already states the reason: `02` §3.6 approximates the
population the model was fitted on, so the fit, the R², the deviance and the worst regions all use
the train frame. Do not change it to the holdout.

- [ ] **Step 1: Write the failing test**

Add to `packages/pricing-core/tests/test_transparency.py`. It calls `_worst_regions` directly with
synthetic error arrays, so it needs no GBM fit and runs in milliseconds.

```python
@pytest.mark.req("FR-MODEL-36")
def test_worst_region_shares_are_exposure_and_not_row_counts() -> None:
    """A frame where the two definitions give opposite orderings.

    `common` has 400 rows carrying 4.0 years between them; `rare` has 20 rows carrying 200.0.
    A row-count share makes `common` the larger region and an exposure share makes `rare` the
    larger one, so this test can only pass under one of the two definitions — which the
    existing `0.0 < share <= 1.0` assertion could not distinguish, and did not.
    """
    from pricing_core.modelling.transparency import _worst_regions

    n_common, n_rare = 400, 20
    frame = pl.DataFrame(
        {
            "exposure_years": [0.01] * n_common + [10.0] * n_rare,
            "area": ["common"] * n_common + ["rare"] * n_rare,
            "driv_age": [40.0] * (n_common + n_rare),
            "claim_count": [1.0] * (n_common + n_rare),
        }
    )
    spec = _spec("xgboost")
    target = np.ones(n_common + n_rare)
    approximated = np.full(n_common + n_rare, 1.5)

    regions = _worst_regions(
        frame, FACTORS, target, approximated,
        spec=spec, bandings=None, groupings=None,
    )
    share = {region.description: region.exposure_share for region in regions}

    # Exposure: rare 200.0/204.0 = 0.980, common 4.0/204.0 = 0.0196.
    # Row counts would be rare 20/420 = 0.048 and common 400/420 = 0.952 — reversed.
    assert share["area = rare"] > share["area = common"]
    assert share["area = rare"] == pytest.approx(200.0 / 204.0, abs=1e-6)
    assert share["area = common"] == pytest.approx(4.0 / 204.0, abs=1e-6)
```

`_spec`, `FACTORS`, `pl` and `np` are already imported at the top of this module (it imports
`from test_gbm import BACKENDS, FACTORS, _factor, _frequency_data, _spec`). `FACTORS` is
`[_factor("area", "area"), _factor("driv_age", "driv_age")]`, and `_spec` sets
`offset=OffsetSpec(kind="log_column", column="exposure_years")`, which is what makes `_weights`
return the exposure column. Check the import line before running and add `numpy as np` if absent.

The description format is `f"{slug} = {level}"`, taken from the existing implementation — verify
against the current source rather than trusting this plan if the assertion keys miss.

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_transparency.py::test_worst_region_shares_are_exposure_and_not_row_counts -v
```
Expected: FAIL with `TypeError: _worst_regions() got an unexpected keyword argument 'spec'`.

- [ ] **Step 3: Thread `spec` into `_worst_regions` and weight the share**

In `packages/pricing-core/src/pricing_core/modelling/transparency.py`, change the signature, the
docstring and the two lines that compute the share:

```python
def _worst_regions(
    data: pl.DataFrame,
    factors: Sequence[Factor],
    target: np.ndarray,
    approximated: np.ndarray,
    *,
    spec: ModelSpecCommon,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> tuple[WorstRegion, ...]:
    """The cells where the approximation is worst, with their share of the book.

    By **factor level**, not by arbitrary slice: a region an actuary cannot name is a region
    they cannot act on, and "young high-mileage drivers" is a rating cell while "rows 40000 to
    41000" is not.

    The share is a share of **exposure** (FR-MODEL-36), the same quantity FR-MODEL-125 names one
    module away: a row-count share on a motor book reports a level held for a fortnight as a
    region the same size as one held for a year, and stating how much of the book the
    approximation is wrong over is the whole purpose of the sentence it appears in. The frame is
    the **train** frame, deliberately — `02` §3.6 approximates the population the model was
    fitted on, so unlike a partial-dependence curve this must not report the holdout's profile.
    """
    from pricing_core.modelling.diagnostics import _share, _weights

    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    error = np.abs(target - approximated) / np.maximum(target, 1e-12)
    weights = _weights(spec, data)
    total_weight = float(weights.sum())
    found: list[WorstRegion] = []
```

then, at the site that today reads `exposure_share=float(mask.sum()) / max(rows, 1),`:

```python
                    exposure_share=min(1.0, _share(float(weights[mask].sum()), total_weight)),
```

Leave every other line of the loop as it is. The deferred import matches the one already at
`transparency.py:204` (`from pricing_core.modelling.diagnostics import deviance`), inside the same
call chain. `min(1.0, ...)` guards float summation drift against `WorstRegion`'s `le=1.0` bound,
the same way `_sweep`'s omission record does.

The local `rows = data.height` becomes unused — delete that line. Add `ModelSpecCommon` to the
module's `model_schema` import if it is not already there.

- [ ] **Step 4: Update the one call site**

`packages/pricing-core/src/pricing_core/modelling/transparency.py:222-224`, inside
`build_glm_approximation`, which already has `spec: GbmSpec` as a parameter:

```python
    report.update(0.90, "locating the worst regions")
    regions = _worst_regions(
        train_frame, factors, target, approximated,
        spec=spec, bandings=bandings, groupings=groupings,
    )
```

`GbmSpec` subclasses `ModelSpecCommon`, so this type-checks. `train_frame` is `data` plus the
surrogate response column, so the offset column is present.

- [ ] **Step 5: Run the test to verify it passes**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_transparency.py::test_worst_region_shares_are_exposure_and_not_row_counts -v
```
Expected: PASS.

- [ ] **Step 6: Run the whole transparency suite for regressions**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_transparency.py -q
uv run mypy
```
Expected: both pass. `test_the_worst_regions_name_a_cell_and_its_share_of_the_book` asserts
`0.0 < share <= 1.0` and keeps passing under either definition — Step 1's test is the one that
discriminates.

- [ ] **Step 7: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/transparency.py
git add packages/pricing-core/tests/test_transparency.py
git commit -m "fix(w32-9): a worst region's share is exposure, not row count"
```

- [ ] **Step 8: Prove the new test is non-trivial**

Break the implementation on purpose against the committed version, confirm the test fails, then
restore. `.claude/skills/contract-guard` §"Prove it fails on deliberately broken input" is the
procedure this follows; it is done after the commit so `git checkout --` restores the intended
code and not the pre-slice code.

```bash
sed -i 's|_share(float(weights\[mask\].sum()), total_weight)|_share(float(mask.sum()), float(len(mask)))|' packages/pricing-core/src/pricing_core/modelling/transparency.py
uv run pytest packages/pricing-core/tests/test_transparency.py::test_worst_region_shares_are_exposure_and_not_row_counts -q
git checkout -- packages/pricing-core/src/pricing_core/modelling/transparency.py
git status --short packages/pricing-core/src/pricing_core/modelling/transparency.py
```
Expected: the pytest run FAILS (the row-count share puts `common` above `rare`), and `git status`
prints nothing after the restore. Record the failure message in the ledger — a check that has
never printed a failure has not been tested (`CLAUDE.md` §13).

---

### Task 2: The fidelity statement says "of exposure"

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/transparency.py:430-435` (`fidelity_statement`)
- Test: `packages/pricing-core/tests/test_transparency.py:180-201`

**Interfaces:**
- Consumes: Task 1's weighted `WorstRegion.exposure_share`. No signature changes.
- Produces: nothing new. The rendered sentence changes wording only.

`02` §4.9's example sentence at `../specs/02-modelling.md:1354` already reads
`"(0.8% of exposure, mean |error| 11.4%)"`. **The spec is the correct side and the code is the
wrong one** — this is the site the W32-5 ledger left alone on the belief that §5.2 described it as
a percentage of rows.

- [ ] **Step 1: Write the failing test**

Extend the existing FR-MODEL-36 statement test rather than adding a third. **Insert two
assertions; do not replace the block.** In
`packages/pricing-core/tests/test_transparency.py:180-201` the assertions today are:

```python
    assert "%" in statement
    assert "Divergence concentrates in area = " in statement
    if backend == "lightgbm":
        assert "not SHAP interaction values" in statement
```

The `lightgbm` branch is the only assertion anywhere that the backend-specific caveat is rendered,
and the bare `assert "%"` is what catches a statement that stops interpolating numbers at all.
Losing either to a tidier-looking block is a coverage regression the gate cannot see. Add the two
new lines between the existing second and third, leaving everything else — setup, marker,
docstring, parametrize — untouched:

```python
    assert "%" in statement
    assert "Divergence concentrates in area = " in statement
    # The noun matters: the number beside it is a share of exposure (FR-MODEL-36), and `02`
    # §4.9's own example sentence says so. Naming it "of rows" describes a quantity the
    # artifact no longer carries.
    assert "% of exposure" in statement
    assert "% of rows" not in statement
    if backend == "lightgbm":
        assert "not SHAP interaction values" in statement
```

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_transparency.py::test_the_fidelity_statement_says_where_the_approximation_fails -v
```
Expected: FAIL on `assert "% of exposure" in statement`.

- [ ] **Step 3: Change the rendered noun**

`packages/pricing-core/src/pricing_core/modelling/transparency.py:430-435`:

```python
    if approximation.worst_regions:
        worst = approximation.worst_regions[0]
        parts.append(
            f"Divergence concentrates in {worst.description} "
            f"({worst.exposure_share * 100:.1f}% of exposure, mean |error| "
            f"{worst.mean_abs_error_pct:.1f}%). Rating on the approximation would misprice "
            "that cell."
        )
```

Match the surrounding lines exactly rather than pasting this verbatim if the string has moved —
the change is the single word `rows` becoming `exposure`.

- [ ] **Step 4: Run the test to verify it passes**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_transparency.py::test_the_fidelity_statement_says_where_the_approximation_fails -v
```
Expected: PASS.

- [ ] **Step 5: Check the EBM statement for the same wording**

Run:
```bash
grep -rn "of rows" packages/pricing-core/src/pricing_core/
```
Expected: **exactly three hits, all unrelated, none of them changed** —

```
packages/pricing-core/src/pricing_core/modelling/perils.py:260:  "numbers of rows",
packages/pricing-core/src/pricing_core/data/validate.py:383:     ... permitted share of rows read.
packages/pricing-core/src/pricing_core/modelling/bandings.py:214: ... of rows, or of exposure.
```

Each is genuinely counting rows: a peril-structure diagnostic, VR-STR-9's quarantine share, and
banding cut points — where "of rows, or of exposure" is the *distinction* being drawn, so changing
it would make the docstring wrong. Leave all three and say so in the ledger. The verification this
step actually performs is that `transparency.py:432` has left the list; if a fourth hit appears
beside an `exposure_share`, that is a sibling statement (`ebm_fidelity_statement` or similar) with
the same defect — change it too and name the site in the commit body. An EBM is a glass box and its
statement is a different sentence, so do not assume without looking.

- [ ] **Step 6: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/transparency.py
git add packages/pricing-core/tests/test_transparency.py
git commit -m "fix(w32-9): the fidelity statement names exposure, not rows"
```

---

### Task 3: Delete `ShapInteraction.exposure_share`

**Files:**
- Modify: `packages/model-schema/src/model_schema/transparency.py:146` (the field)
- Modify: `packages/pricing-core/src/pricing_core/modelling/transparency.py:398` (the producer)
- Modify: `packages/pricing-core/src/pricing_core/modelling/transparency.py:296-298` (the docstring)
- Modify: `docs/contracts/schemas/transparency-artifact.schema.json` (authored contract)
- Modify: `backend/tests/test_contracts.py:1275` (`REACHED_NESTED_PATHS`)
- Regenerate: `docs/contracts/schemas/generated/transparency-artifact.schema.json`, `docs/contracts/openapi/generated.json`
- Test: `packages/pricing-core/tests/test_transparency.py`

**Interfaces:**
- Consumes: nothing from Tasks 1 and 2. This task is independent and may be done first.
- Produces: `ShapInteraction(pair: tuple[str, str], strength: float)` — two fields, not three.

A per-pair exposure share is `1.0` by construction: every row has a value for both features of a
pair, so the cross of their observed cells is the whole book. `_interaction_candidates`
(`transparency.py:367-401`) takes no `spec` and no weights, which is the structural reason
FR-MODEL-79 withdraws the field rather than fixing it. The disanalogy with a partial-dependence
point or a worst region is real: those are per level and their shares partition exposure, while a
candidate is one object spanning the entire frame. OQ-MODEL-31 decided on 2026-08-23 that what
stands beside a candidate is its holdout strength ratio (FR-MODEL-128), which is **not** this
slice's: until it lands the artifact publishes `strength` alone.

`ShapInteraction` is `extra="forbid"`, so after this change a stored artifact JSON still carrying
the key is **rejected on read** rather than ignored. Step 5 checks whether any exists.

- [ ] **Step 1: Write the failing test**

Add to `packages/pricing-core/tests/test_transparency.py`:

```python
@pytest.mark.req("FR-MODEL-79")
def test_an_interaction_candidate_carries_no_exposure_share() -> None:
    """The field was `1.0` at its construction site and `1.0` as a default on its type.

    It could not have been anything else — a pair spans the whole frame, and
    `_interaction_candidates` receives neither a spec nor a weight vector — so publishing it
    told an actuary nothing while looking like a measurement. OQ-MODEL-31 withdrew it on
    2026-08-23; `strength` alone is what the artifact truthfully carries until FR-MODEL-128's
    holdout strength ratio lands.
    """
    assert "exposure_share" not in ShapInteraction.model_fields
    with pytest.raises(ValidationError):
        ShapInteraction(pair=("a", "b"), strength=0.1, exposure_share=1.0)
```

Add `ShapInteraction` to the `from model_schema import (...)` block at the top of the file and
`from pydantic import ValidationError` beside it.

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_transparency.py::test_an_interaction_candidate_carries_no_exposure_share -v
```
Expected: FAIL on the first assertion — the field is still declared.

- [ ] **Step 3: Delete the field and its producer**

`packages/model-schema/src/model_schema/transparency.py` — delete the `exposure_share` line at
`:146` so the class body ends:

```python
    pair: tuple[str, str]
    strength: float = Field(ge=0.0)
```

`packages/pricing-core/src/pricing_core/modelling/transparency.py:396-399` — drop the kwarg:

```python
            strengths.append(
                ShapInteraction(pair=(order[i], order[j]), strength=strength)
            )
```

`packages/pricing-core/src/pricing_core/modelling/transparency.py:296-298` — the
`build_shap_summary` docstring still promises the withdrawn number. Replace those three lines:

```python
    `top_interactions` are FR-MODEL-79 **suggestions**: the platform never writes a Factor into
    a Model Spec. Each carries its interaction `strength` alone — a per-pair exposure share was
    `1.0` by construction and was withdrawn by OQ-MODEL-31 on 2026-08-23, and the out-of-sample
    evidence that replaces it is FR-MODEL-128's holdout strength ratio, which is not built here.
```

- [ ] **Step 4: Delete it from the authored contract**

In `docs/contracts/schemas/transparency-artifact.schema.json`, remove the `"exposure_share"`
property from `shap_summary.top_interactions.items.properties`, leaving `pair` and `strength`.
Find it with:

```bash
grep -n "exposure_share" docs/contracts/schemas/transparency-artifact.schema.json
```

Only the entry inside `top_interactions` goes — the artifact has other `exposure_share` fields
(the worst regions) that Tasks 1 and 2 keep. Confirm which line is which by reading three lines of
context around each hit before deleting.

The field is not in that object's `required` list, so nothing else in the file changes. This file
is hand-authored; it is **not**
`docs/contracts/schemas/generated/transparency-artifact.schema.json`.

- [ ] **Step 5: Check for persisted artifacts carrying the key**

Run:
```bash
grep -rln "top_interactions" --include=*.json examples/ backend/tests/ packages/ docs/
```
Then grep each hit for `exposure_share`. Expected: **three files, all under `docs/contracts/`** —
`schemas/transparency-artifact.schema.json` (hand-authored, edited in Step 4),
`schemas/generated/transparency-artifact.schema.json` and `openapi/generated.json` (both generated,
so they change when `generate-contracts.py` reruns, never by hand). No fixture, example or test
JSON carries the key. If one appears, delete it there too and name the file in the commit body —
`extra="forbid"` turns a leftover key into a read failure, not a warning.

- [ ] **Step 6: Update the drift guard's reached-path list**

`backend/tests/test_contracts.py:1275` — delete the
`"shap_summary.top_interactions.[].exposure_share"` entry from
`REACHED_NESTED_PATHS["transparency-artifact"]`.

This is required, not cosmetic: the list exists so a nested field's removal is *noticed*, and
`test_the_comparison_reaches_the_nested_fields_this_slice_added` asserts each entry is a path both
maps reach. Leaving it in fails exactly that guard.

- [ ] **Step 7: Regenerate the contracts**

Run:
```bash
uv run python scripts/generate-contracts.py
git diff --stat docs/contracts/
```
Expected: `docs/contracts/schemas/generated/transparency-artifact.schema.json` and
`docs/contracts/openapi/generated.json` both change, dropping the property. Never hand-edit either.

- [ ] **Step 8: Run the tests to verify they pass**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_transparency.py -q
uv run pytest backend/tests/test_contracts.py -q
uv run python scripts/generate-contracts.py --check
```
Expected: all pass; `--check` exits 0.

- [ ] **Step 9: Commit**

```bash
git add packages/model-schema/src/model_schema/transparency.py
git add packages/pricing-core/src/pricing_core/modelling/transparency.py
git add packages/pricing-core/tests/test_transparency.py
git add backend/tests/test_contracts.py docs/contracts/
git commit -m "fix(w32-9): withdraw the constant exposure_share from ShapInteraction"
```

---

### Task 4: Run the gate and record what this slice found

**Files:**
- Modify: [`../roadmap.md`](../roadmap.md) — a slice record, appended
- Create: `2026-08-23-w32-9-transparency-exposure-share-ledger.md`

**Interfaces:**
- Consumes: Tasks 1-3 complete and committed.
- Produces: the slice record the closure audit reads.

- [ ] **Step 1: Run the Python half of the gate**

```bash
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```
Expected: every command exits 0. Check the exit codes, not the last line of output —
`.claude/skills/dev-commands` records that several of these print reassuring text while failing.

- [ ] **Step 2: Run the frontend half**

It cannot be skipped even though this slice touches no `.vue` file: Task 3's regeneration changes
the OpenAPI the client is generated from.

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```
Expected: every command exits 0. If `type-check` fails on a removed `exposureShare`, the generated
client caught a real consumer the sweep in Task 3 missed — fix the consumer, do not restore the
field.

- [ ] **Step 3: Write the ledger**

Create `docs/plans/2026-08-23-w32-9-transparency-exposure-share-ledger.md` recording, task by task,
what execution actually did — including anything this plan got wrong. Paste the real gate output
and Task 1 Step 8's failure message rather than a summary typed from memory.

- [ ] **Step 4: Record the unresolved spec disagreement**

**Not** the `holdout` keyword. `02` §5.2 at
[`../specs/02-modelling.md`](../specs/02-modelling.md):2355-2359 declares a `holdout` keyword on
`build_shap_summary` that the code does not have — the function takes `sample`, `seed`, `bandings`,
`groupings` and `progress`. That reads like `CLAUDE.md` §0's stop-and-resolve case and is not one:
`git log -L 2355,2358:docs/specs/02-modelling.md` attributes those lines to commit `b019070`, the
same commit that appended **FR-MODEL-128** (`:232`, *(appended 2026-08-23, OQ-MODEL-31)*). The
signature is a dated, owned forward declaration of a function this slice is not building. **Leave
it alone and do not raise it** — note in the ledger that it was checked and why it is not a finding,
so the next audit does not spend the hour again.

What this slice does record is FR-MODEL-79's withdrawn field: `top_interactions[].exposure_share`
is removed from the hand-authored contract by Task 3, and the spec text that described it must be
read against the change rather than assumed to match. Name the exact `02` line in the ledger.

- [ ] **Step 5: Append the slice record to the roadmap**

Follow the shape of the existing W32-6 record in [`../roadmap.md`](../roadmap.md). Say which of the
three FR-MODEL-36 sites moved, that FR-MODEL-79's field was withdrawn rather than computed, and
that FR-MODEL-128 is left unbuilt with OQ-MODEL-31 as its origin.

- [ ] **Step 6: Commit**

```bash
git add docs/plans/2026-08-23-w32-9-transparency-exposure-share-ledger.md docs/roadmap.md
git commit -m "docs(w32-9): record the transparency exposure slice"
```
