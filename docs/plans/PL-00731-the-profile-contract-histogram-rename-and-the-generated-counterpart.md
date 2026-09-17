---
id: PL-731
family: plan
kind: leaf
title: The Profile Contract — Histogram, Rename, and the Generated Counterpart
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-18
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-18-profile-contract.md
---

# The Profile Contract — Histogram, Rename, and the Generated Counterpart

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the `ColumnProfile` histogram divergence — the field `01` §4.7, the committed contract and `01` §5.3's view all promise and no code produces — and, because that makes this the slice that changes the profile contract, discharge FR-64's deferred rename and publish a generated counterpart so the profile contract stops being unchecked.

**Architecture:** `ColumnProfile` gains a `Histogram` sub-shape in `model-schema` (the SSOT). Both profiling engines — `profile_frame` (Polars) and `profile_parquet` (DuckDB) — compute it from **identical arithmetic over Python-chosen edges**, never from either engine's own histogram function, because every divergence the existing agreement test ever caught came from trusting an engine default. `profile` then joins `GENERATED_SHAPES`, and a nested conformance test compares the hand-authored Phase-0 contract against the generated one one level down, where the profile's divergences actually live.

**Tech Stack:** Python 3.12, Pydantic v2 (`packages/model-schema`), Polars + DuckDB (`packages/pricing-core`), FastAPI worker (`backend/`), Vue 3 + ECharts via `vue-echarts` (`frontend/`).

**Spec:** `docs/specs/01-data-management.md` — §4.7 (`Profile` contract), §5.3 (Profile view), FR-60/61/62, FR-64. Contract: `docs/contracts/schemas/profile.schema.json`. Divergences recorded in `docs/roadmap.md` (~line 768) and the §5.3 audit row (~line 701).

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Requirement IDs are permanent** (`CLAUDE.md` §5). Never renumber. The **maximum** existing id — not the last one you read — is `FR-44`, so **the next free id is `FR-65`**. `01`'s requirement tables are not in numeric order; re-derive with `grep -o "FR-DATA-[0-9]*" docs/specs/01-data-management.md | sort -t- -k3 -n | tail -1` before appending. Max `OQ-DATA` is `8`, so **the next free question is `OQ-565`**.
- **Money is integer minor units or an exact decimal string, never float** (FR-10). Exposure is `DecimalStr`.
- **`model-schema` is the single source of truth.** Never hand-write a shape that exists there — not in the backend, not in the frontend, not in a fixture.
- **`docs/contracts/` is generated and committed.** Never hand-edit anything under `docs/contracts/schemas/generated/` or `docs/contracts/openapi/generated.json`.
- **Do NOT rename `modelled_burning_cost_minor` or `observed_burning_cost_minor`** (`packages/model-schema/src/model_schema/perils.py`, `pricing_core/modelling/perils.py`). They are genuine integer `MoneyMinor` fields and FR-10 requires the `_minor` suffix on them. FR-64 targets **only** `OneWayRow`'s two float means. A blind `sed` over `burning_cost_minor` breaks money discipline.
- Ruff line length 100; `mypy --strict` on `packages/`; TS strict on `frontend/`.
- **Every test carries `@pytest.mark.req("FR-...")`** naming the requirement it satisfies (`CLAUDE.md` §13).
- Conventional Commits; short-lived branch from `main`; squash-merge.
- Environment (from `task_plan.md`):

```bash
uv sync --all-packages --dev                 # --all-packages is not optional
docker compose -f deploy/docker-compose.yml up -d --wait
export GIP_TEST_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
export GIP_DATABASE_URL="$GIP_TEST_DATABASE_URL"
export PATH="$HOME/.npm-global/bin:$PATH"    # pnpm is not on the default PATH
```

- **Sessions run concurrently in this working directory.** Fetch and re-read refs immediately before acting; push with `--force-with-lease`; stage explicit paths, never `git add -A`.
- **`gh` cannot read Actions here.** `gh pr view <n> --json mergeStateStatus` is the usable signal: `CLEAN` passed, `UNSTABLE` pending or failing.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `docs/open-questions.md` | `OQ-565` raised with options and a recommendation | 1 |
| `docs/specs/01-data-management.md` | `OQ-565` mirrored into §10; `FR-65` appended; §4.7 dated note; FR-64 marked delivered | 1, 2, 5, 8 |
| `packages/model-schema/src/model_schema/profiles.py` | `Histogram`; `ColumnProfile.histogram`; `OneWayRow`'s two renamed means | 2, 5 |
| `packages/model-schema/src/model_schema/__init__.py` | Export `Histogram` | 2 |
| `packages/model-schema/tests/test_profiles.py` | `Histogram` invariants (create if absent) | 2 |
| `packages/pricing-core/src/pricing_core/data/profile.py` | `HISTOGRAM_BINS`, `_histogram_edges`, `_stored_exposure`, both engines' histogram | 3, 4, 5 |
| `packages/pricing-core/tests/test_profile.py` | Histogram behaviour; the two-engine agreement test carries it free | 3, 4 |
| `scripts/generate-contracts.py` | `profile` added to `GENERATED_SHAPES` | 6 |
| `docs/contracts/schemas/generated/profile.schema.json` | Generated output — committed, never hand-edited | 6 |
| `docs/contracts/schemas/profile.schema.json` | The hand-authored Phase-0 contract, corrected where *it* is wrong | 6 |
| `backend/tests/test_contracts.py` | Nested conformance for `profile`; delete the FR-64 exclusion | 5, 6 |
| `frontend/src/components/HistogramChart.vue` | ECharts histogram (new) | 7 |
| `frontend/src/views/ProfileView.vue` | Render the histogram; remove the fake PSI badge | 7 |
| `docs/roadmap.md` | Slice record; the two divergences resolved to one | 1, 8 |

---

## Task 1: Raise OQ-565 — the Dataset display fields

The other half of `task_plan.md`'s named item. `01` §5.3 asks the dataset list to show "status badge, last validated, owner"; `Dataset` (`packages/model-schema/src/model_schema/datasets.py:148`) carries none of the three. Unlike the histogram, **this one has two defensible answers**, so `CLAUDE.md` §10 requires a recorded question rather than a silent pick. Docs only — no code — and it unblocks the maintainer while the rest of this plan builds.

**Files:**
- Modify: `docs/open-questions.md` (append `OQ-565`)
- Modify: `docs/specs/01-data-management.md` (§10 Open questions table — mirror the id)
- Modify: `docs/roadmap.md` (~line 768's "Two unresolved model/contract divergences" row)

**Interfaces:**
- Consumes: nothing.
- Produces: the id `OQ-565`. No later task in this plan depends on it.

- [ ] **Step 1: Confirm the id is free and the facts are still true**

```bash
cd /home/puzhenhao1989/gi-pricing-plan
grep -o "OQ-DATA-[0-9]*" docs/open-questions.md docs/specs/01-data-management.md \
  | grep -o "OQ-DATA-[0-9]*" | sort -t- -k3 -n | tail -1     # expect OQ-563
sed -n '148,170p' packages/model-schema/src/model_schema/datasets.py
sed -n '799,800p' docs/specs/01-data-management.md
```

Expected: max is `OQ-563`; `Dataset` carries `created_at` and `archived_at` and none of the three; §5.3's Dataset list row reads "Datasets with latest version, status badge, last validated, owner".

- [ ] **Step 2: Append OQ-565 to `docs/open-questions.md`**

Match the table's existing column order exactly (id · question · context · recommendation · owner · status). Copy this text:

> **OQ-565** | `01` §5.3 asks the dataset list to display a status badge, a last-validated date and an owner. `Dataset` carries none of the three: status and `validation_report_id` live on `DatasetVersion`, and ownership is only implied by `workspace_id`. Does `Dataset` gain the three fields, or does §5.3 mean the **latest version's** status and validated-at, plus a workspace-level owner? | Raised 2026-08-18 (WK-661). Recorded as an unowned divergence in `docs/roadmap.md` since 2026-08-15 and built around in silence, which is the `CLAUDE.md` §0 failure dated amendment notes exist to prevent. `Dataset` is a *container*: `01` §4.1's contract shows no status either, so the divergence is between §5.3 and §4.1 as much as between spec and code. | **Read §5.3 as the latest version's status and validated-at, and add an explicit `owner_id` to `Dataset`.** A status on the container would be a second answer to "can I fit on this?", and `DatasetVersion.is_fittable` is deliberately the only one (`01` §1.3). `latest_version` already exists, so the list view resolves both from the version it names, at the cost of one join. **Owner is different**: it is a fact about the container, no version carries it, and `06`'s RBAC will need a subject to attach to — deriving it from `workspace_id` makes every dataset in a workspace equally owned, which is exactly what an approval trail cannot say. | maintainer | **open** |

- [ ] **Step 3: Mirror the id into `01` §10**

`audit-docs.py` fails when a question is listed in `open-questions.md` and raised in no spec. Add the row to §10's table in `docs/specs/01-data-management.md`, one line, same wording as the question column.

- [ ] **Step 4: Update the roadmap row**

In `docs/roadmap.md`, the "Two unresolved model/contract divergences" row: the `ColumnProfile` half is now owned by this slice, the `Dataset` half by `OQ-565`. Rewrite so neither half is unowned. Do **not** delete the row — it records that both were built around in silence.

- [ ] **Step 5: Run the audit**

```bash
python3 scripts/audit-docs.py
```

Expected: `All checks passed`. If it reports `OQ-565 listed in open-questions.md but raised in no spec`, Step 3's row is missing or its id is not backticked the way the audit reads it.

- [ ] **Step 6: Commit**

```bash
git add docs/open-questions.md docs/specs/01-data-management.md docs/roadmap.md
git commit -m "docs(data): OQ-565 — the dataset list asks for three fields Dataset lacks"
```

---

## Task 2: `Histogram` in model-schema, and FR-65

The shape first, with no producer. `01` §4.7 and `docs/contracts/schemas/profile.schema.json:35` both define a histogram; FR-60's enumerated statistics do not mention one. **The contract is right and the requirement is incomplete** — so the requirement gains the obligation (`CLAUDE.md` §14: resolve, never soften) rather than the contract losing the field.

**Files:**
- Modify: `packages/model-schema/src/model_schema/profiles.py`
- Modify: `packages/model-schema/src/model_schema/__init__.py`
- Test: `packages/model-schema/tests/test_profiles.py` (create if absent — `ls packages/model-schema/tests/` first)
- Modify: `docs/specs/01-data-management.md`

**Interfaces:**
- Consumes: `DecimalStr` from `model_schema.money` (already imported by `profiles.py`).
- Produces:
  - `class Histogram(BaseModel)` with `edges: tuple[float, ...]`, `counts: tuple[int, ...]`, `exposure: tuple[DecimalStr, ...] = ()`.
  - `ColumnProfile.histogram: Histogram | None = None`.
  - Invariants: `len(edges) == len(counts) + 1`; `len(exposure)` is `0` or `len(counts)`; `edges` strictly increasing.

- [ ] **Step 1: Write the failing tests**

Create `packages/model-schema/tests/test_profiles.py`:

```python
"""Profile shapes (`01` §4.7, FR-65)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import ColumnProfile, Histogram, SemanticType


@pytest.mark.req("FR-65")
def test_a_histogram_has_one_more_edge_than_it_has_bins() -> None:
    histogram = Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6))
    assert len(histogram.edges) == len(histogram.counts) + 1


@pytest.mark.req("FR-65")
def test_a_histogram_with_a_missing_edge_is_refused() -> None:
    with pytest.raises(ValidationError, match="one more edge"):
        Histogram(edges=(0.0, 1.0), counts=(4, 6))


@pytest.mark.req("FR-65")
def test_edges_must_increase() -> None:
    with pytest.raises(ValidationError, match="increasing"):
        Histogram(edges=(0.0, 2.0, 1.0), counts=(4, 6))


@pytest.mark.req("FR-65")
def test_exposure_is_absent_or_one_weight_per_bin() -> None:
    Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6))
    Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6), exposure=("1.5", "2.25"))
    with pytest.raises(ValidationError, match="one exposure weight per bin"):
        Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6), exposure=("1.5",))


@pytest.mark.req("FR-65")
def test_a_column_profile_carries_no_histogram_by_default() -> None:
    column = ColumnProfile(
        name="driver_age",
        dtype="Int64",
        semantic_type=SemanticType.CONTINUOUS,
        row_count=10,
        null_count=0,
        null_rate=0.0,
        distinct_count=10,
    )
    assert column.histogram is None
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
uv run pytest packages/model-schema/tests/test_profiles.py -q
```

Expected: FAIL — `ImportError: cannot import name 'Histogram' from 'model_schema'`.

- [ ] **Step 3: Add the shape**

In `packages/model-schema/src/model_schema/profiles.py`, add `"Histogram"` to `__all__` (it is alphabetical — keep it so), and insert the class **above** `ColumnProfile`:

```python
class Histogram(BaseModel):
    """The binned distribution of a numeric column (`01` §4.7, FR-65).

    Bin *edges* rather than a bin width, because the last bin is closed and the others are
    half-open: `[e0, e1) … [e(n-1), en]`. A reader given only a width has to guess which
    end carries the maximum, and the two profiling engines would guess differently.

    `exposure` is optional and, when present, holds one exact decimal weight per bin
    (FR-10). A count histogram of an exposure-weighted book overstates the tail: a bin
    of 200 policies each on risk a fortnight is not the same risk as 200 policies on risk a
    year, and pricing reads the second.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    edges: tuple[float, ...] = ()
    counts: tuple[Annotated[int, Field(ge=0)], ...] = ()
    exposure: tuple[DecimalStr, ...] = ()

    @model_validator(mode="after")
    def _edges_bound_the_bins(self) -> Histogram:
        if len(self.edges) != len(self.counts) + 1:
            raise ValueError(
                "a histogram needs one more edge than it has bins "
                f"({len(self.edges)} edges, {len(self.counts)} counts)"
            )
        if any(b <= a for a, b in zip(self.edges, self.edges[1:], strict=False)):
            raise ValueError("histogram edges must be strictly increasing")
        if self.exposure and len(self.exposure) != len(self.counts):
            raise ValueError(
                "a histogram with exposure needs one exposure weight per bin "
                f"({len(self.exposure)} weights, {len(self.counts)} bins)"
            )
        return self
```

Add to `ColumnProfile`, immediately after `quantiles` and before `top_levels`:

```python
    #: Present for a numeric, non-identifier column only (FR-65). A histogram of a
    #: policy id is five million bars, and a histogram of a categorical column is what
    #: `top_levels` already is.
    histogram: Histogram | None = None
```

`profiles.py` currently imports `BaseModel, ConfigDict, Field` from pydantic and `Annotated` from typing — **add `model_validator`** (and `Annotated` if the import is not already there).

Export from `packages/model-schema/src/model_schema/__init__.py`: add `Histogram` to both the `from .profiles import (...)` block and `__all__`.

- [ ] **Step 4: Run the tests to verify they pass**

```bash
uv run pytest packages/model-schema/tests/test_profiles.py -q
uv run mypy
```

Expected: PASS; mypy 0 errors.

- [ ] **Step 5: Append FR-65 to `01`**

In `docs/specs/01-data-management.md`, in the table FR-60 lives in, append:

> | **FR-65** | *(appended 2026-08-18; `ColumnProfile` had no `histogram` while `01` §4.7's contract example, `docs/contracts/schemas/profile.schema.json` and §5.3's Profile view all declared one — a divergence recorded in `docs/roadmap.md` and built around in silence since 2026-08-15.)* Profiling additionally produces, for every **numeric non-identifier** column, a **histogram**: `HISTOGRAM_BINS` (20) equal-width bins over the observed `[min, max]`, published as `edges` (one more than there are bins), `counts`, and — where the version carries an exposure column — one exact decimal `exposure` weight per bin. Bins are half-open, `[e(i), e(i+1))`, except the last, which is closed. A constant column yields a single bin. **Equal-width bins over the observed range, computed from edges chosen in Python rather than by either engine's own histogram function**: FR-62 requires one answer regardless of engine, and every divergence `test_the_two_profiling_paths_agree` has ever caught came from an engine default — tie-breaking, null handling, quantile interpolation. |

Add a dated note under §4.7 recording which side was wrong:

> *(2026-08-18)* The example above has always shown a `histogram`, and so has the committed contract; `ColumnProfile` did not carry one until FR-65. **The contract was right and the requirement was incomplete** — FR-60 enumerates the statistics and never named this one. The example's uneven edges were illustrative, not a specification: FR-65 fixes equal-width bins, because two engines must agree and quantile-derived edges collapse to duplicates on a low-cardinality column, with each engine deduplicating differently.

- [ ] **Step 6: Audit, coverage, commit**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
git add packages/model-schema docs/specs/01-data-management.md
git commit -m "feat(data): a Histogram shape, and FR-65 naming what produces it"
```

Expected: audit passes; `req-coverage.py` exits 0 with FR-65 evidenced. If it reports `FR-65 claimed but nonexistent`, Step 5's row did not land in a table the script reads.

---

## Task 3: `profile_frame` computes the histogram (Polars)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/profile.py`
- Test: `packages/pricing-core/tests/test_profile.py`

**Interfaces:**
- Consumes: `Histogram` from `model_schema` (Task 2).
- Produces, all module-level in `pricing_core.data.profile`:
  - `HISTOGRAM_BINS: Final = 20`
  - `def _histogram_edges(minimum: float, maximum: float) -> tuple[float, ...]`
  - `def _stored_exposure(value: float) -> Decimal`
  - `def _bin_index_expression(column: str, edges: tuple[float, ...]) -> pl.Expr`
  - `def _histogram_frame(frame: pl.DataFrame, column: str, *, minimum: float, maximum: float, exposure_column: str | None) -> Histogram`

  Task 4 calls `_histogram_edges` and `_stored_exposure` from the DuckDB path. They exist so the two engines cannot drift — the same reason `_one_way_row` is shared today.

- [ ] **Step 1: Write the failing tests**

Append to `packages/pricing-core/tests/test_profile.py`:

```python
# -- FR-65: histograms ------------------------------------------------------------


@pytest.mark.req("FR-65")
def test_a_numeric_column_gets_a_histogram() -> None:
    profile = profile_frame(FRAME, dataset_version_id=uuid4())
    age = profile.column("driver_age")

    assert age is not None and age.histogram is not None
    assert len(age.histogram.edges) == len(age.histogram.counts) + 1
    assert age.histogram.edges[0] == age.minimum
    assert age.histogram.edges[-1] == age.maximum
    # Every non-null row lands in exactly one bin, the maximum included.
    assert sum(age.histogram.counts) == FRAME.height - age.null_count


@pytest.mark.req("FR-65")
def test_an_identifier_and_a_categorical_get_no_histogram() -> None:
    profile = profile_frame(FRAME, dataset_version_id=uuid4())
    policy_id, vehicle_group = profile.column("policy_id"), profile.column("vehicle_group")

    assert policy_id is not None and policy_id.histogram is None
    assert vehicle_group is not None and vehicle_group.histogram is None


@pytest.mark.req("FR-65")
def test_the_maximum_lands_in_the_last_bin_not_past_it() -> None:
    """The closed last bin. Without it the maximum falls in bin 20 of 20 and is lost."""
    frame = pl.DataFrame({"x": [float(i) for i in range(101)]})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None and column.histogram is not None
    assert sum(column.histogram.counts) == 101
    assert column.histogram.counts[-1] > 0


@pytest.mark.req("FR-65")
def test_a_constant_column_is_one_bin_not_twenty_empty_ones() -> None:
    frame = pl.DataFrame({"x": [3.0] * 50})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None and column.histogram is not None
    assert column.histogram.counts == (50,)
    assert column.histogram.edges == (3.0, 4.0)


@pytest.mark.req("FR-65")
def test_the_histogram_carries_exposure_when_the_column_is_present() -> None:
    age = profile_frame(FRAME, dataset_version_id=uuid4()).column("driver_age")

    assert age is not None and age.histogram is not None
    assert len(age.histogram.exposure) == len(age.histogram.counts)
    # FRAME carries exactly 1.0 exposure year per row, so bin exposure equals bin count.
    assert [float(e) for e in age.histogram.exposure] == [float(c) for c in age.histogram.counts]


@pytest.mark.req("FR-65")
def test_no_exposure_column_means_no_weights_not_zeroes() -> None:
    frame = pl.DataFrame({"x": [1.0, 2.0, 3.0]})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None and column.histogram is not None
    assert column.histogram.exposure == ()


@pytest.mark.req("FR-65")
def test_nulls_are_excluded_from_every_bin() -> None:
    frame = pl.DataFrame({"x": [1.0, 2.0, None, 4.0]})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None and column.histogram is not None
    assert sum(column.histogram.counts) == 3
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
uv run pytest packages/pricing-core/tests/test_profile.py -k histogram -q
```

Expected: FAIL — `assert None is not None`, because `ColumnProfile.histogram` defaults to `None` and nothing sets it.

- [ ] **Step 3: Implement**

In `packages/pricing-core/src/pricing_core/data/profile.py`:

Add `Histogram` to the `from model_schema import (...)` block. Add the constant beside `TOP_LEVELS`, and `"HISTOGRAM_BINS"` to `__all__`:

```python
#: Bins in a column histogram (FR-65). Twenty is enough to show a mode and a tail on a
#: card-sized chart and few enough that an empty bin is visible rather than a hairline.
HISTOGRAM_BINS: Final = 20
```

Lift the exposure rounding out of `_one_way_row` so both paths share it — the helper is the point, not the arithmetic:

```python
def _stored_exposure(value: float) -> Decimal:
    """Exposure as the exact decimal that is *stored*, not the raw float sum.

    Six decimal places. Two engines summing the same column in different orders differ in
    the last bit, and a published figure that depends on which engine read the file is what
    FR-62 exists to prevent. `_one_way_row` and the histogram share this so they cannot
    drift apart.
    """
    return Decimal(str(round(value, 6)))
```

Replace `_one_way_row`'s `stored = Decimal(str(round(exposure, 6)))` with `stored = _stored_exposure(exposure)`.

Then the edges and the Polars histogram:

```python
def _histogram_edges(minimum: float, maximum: float) -> tuple[float, ...]:
    """Equal-width bin edges over the observed range (FR-65).

    Computed here rather than by Polars' `hist` or DuckDB's `histogram`, so both engines bin
    against the same numbers. A constant column is one bin of unit width: zero width would
    divide by zero, and twenty bins of one value is nineteen empty bars.
    """
    if not maximum > minimum:
        return (minimum, minimum + 1.0)
    width = (maximum - minimum) / HISTOGRAM_BINS
    return tuple(minimum + width * i for i in range(HISTOGRAM_BINS)) + (maximum,)


def _bin_index_expression(column: str, edges: tuple[float, ...]) -> pl.Expr:
    """Which bin a value falls in — the same arithmetic the SQL path uses.

    Half-open bins with a closed last one, expressed as a clamp rather than a comparison:
    the maximum computes to index `n` and is pulled back to `n - 1`, which is what "the last
    bin is closed" means in one operation.
    """
    bins = len(edges) - 1
    width = (edges[-1] - edges[0]) / bins
    return (
        ((pl.col(column).cast(pl.Float64) - edges[0]) / width)
        .floor()
        .clip(0, bins - 1)
        .cast(pl.Int64)
        .alias("_bin")
    )


def _histogram_frame(
    frame: pl.DataFrame,
    column: str,
    *,
    minimum: float,
    maximum: float,
    exposure_column: str | None,
) -> Histogram:
    edges = _histogram_edges(minimum, maximum)
    bins = len(edges) - 1

    aggregates = [pl.len().alias("_n")]
    if exposure_column:
        aggregates.append(pl.col(exposure_column).cast(pl.Float64).sum().alias("_e"))

    grouped = (
        frame.filter(pl.col(column).is_not_null())
        .with_columns(_bin_index_expression(column, edges))
        .group_by("_bin")
        .agg(aggregates)
    )

    # Seeded with zeroes and filled from the groups: an empty bin is a fact about the
    # distribution, and a group-by only returns the bins that have rows.
    counts = [0] * bins
    weights = [Decimal(0)] * bins
    for row in grouped.iter_rows(named=True):
        counts[row["_bin"]] = int(row["_n"])
        if exposure_column:
            weights[row["_bin"]] = _stored_exposure(float(row["_e"]))

    return Histogram(
        edges=edges,
        counts=tuple(counts),
        exposure=tuple(str(w) for w in weights) if exposure_column else (),
    )
```

Wire it into `profile_frame`'s column loop — after the `quantiles` block, before `top`:

```python
        histogram = None
        if numeric and height and minimum is not None and maximum is not None:
            histogram = _histogram_frame(
                frame,
                name,
                minimum=minimum,
                maximum=maximum,
                exposure_column=(
                    exposure_column
                    if exposure_column in frame.columns and exposure_column != name
                    else None
                ),
            )
```

and pass `histogram=histogram,` into the `ColumnProfile(...)` construction, after `quantiles=quantiles,`.

> `exposure_column != name` is deliberate: an exposure column weighted by itself is a chart of exposure against exposure, which says nothing and invites the reader to think it does.

- [ ] **Step 4: Run the tests to verify they pass**

```bash
uv run pytest packages/pricing-core/tests/test_profile.py -q
uv run ruff check . && uv run mypy
```

Expected: the histogram tests PASS, ruff 0, mypy 0. **`test_the_two_profiling_paths_agree` will FAIL** — Polars produces a histogram and DuckDB does not. That is Task 4's failing test, and it is correct for it to be red here.

To confirm nothing *else* is broken before committing:

```bash
uv run pytest packages/pricing-core/tests/test_profile.py -q \
  --deselect packages/pricing-core/tests/test_profile.py::test_the_two_profiling_paths_agree
```

**Do not weaken the agreement test to make this commit green.**

- [ ] **Step 5: Commit**

```bash
git add packages/pricing-core/src/pricing_core/data/profile.py \
        packages/pricing-core/tests/test_profile.py
git commit -m "feat(data): profile_frame computes FR-65's histogram

The two-engine agreement test is red until the DuckDB path follows; the
engines genuinely disagree and the test is right to say so."
```

---

## Task 4: `profile_parquet` computes the same histogram (DuckDB)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/profile.py`
- Test: `packages/pricing-core/tests/test_profile.py`

**Interfaces:**
- Consumes: `_histogram_edges`, `_stored_exposure`, `HISTOGRAM_BINS` (Task 3).
- Produces: `_profile_column` gains keyword `exposure_column: str | None = None`; `profile_parquet` passes it.

- [ ] **Step 1: The failing test already exists — run it**

```bash
uv run pytest packages/pricing-core/tests/test_profile.py::test_the_two_profiling_paths_agree -q
```

Expected: FAIL, the diff showing `histogram` populated on the Polars side and `null` on the DuckDB side. **Read the failure** — it is this task's specification.

- [ ] **Step 2: Add the DuckDB histogram**

Change `_profile_column`'s signature to:

```python
def _profile_column(
    connection: Any,
    name: str,
    dtype: Any,
    *,
    row_count: int,
    exposure_column: str | None = None,
) -> ColumnProfile:
```

After the quantiles block and before `top`:

```python
    histogram = None
    if numeric and row_count and minimum is not None and maximum is not None:
        edges = _histogram_edges(minimum, maximum)
        bins = len(edges) - 1
        width = (edges[-1] - edges[0]) / bins
        weighted = exposure_column is not None and exposure_column != name
        # The same arithmetic as `_bin_index_expression`, in SQL. `least(..., bins - 1)` is
        # the closed last bin; `greatest(0, ...)` guards a value that lands a hair below the
        # minimum after the subtraction.
        index = (
            f"greatest(0, least({bins - 1}, "
            f"floor(({quoted} - {edges[0]!r}) / {width!r})::BIGINT))"
        )
        weight = f", sum({_identifier(exposure_column)})" if weighted else ", NULL"
        binned = connection.execute(
            f"SELECT {index} AS bin, count(*){weight} FROM src "
            f"WHERE {quoted} IS NOT NULL GROUP BY 1"
        ).fetchall()

        counts = [0] * bins
        weights = [Decimal(0)] * bins
        for bin_index, count, exposure_sum in binned:
            counts[int(bin_index)] = int(count)
            if weighted and exposure_sum is not None:
                weights[int(bin_index)] = _stored_exposure(float(exposure_sum))

        histogram = Histogram(
            edges=edges,
            counts=tuple(counts),
            exposure=tuple(str(w) for w in weights) if weighted else (),
        )
```

Pass `histogram=histogram,` into the `ColumnProfile(...)` construction, after `quantiles=quantiles,`.

In `profile_parquet`, thread the column through:

```python
        columns = [
            _profile_column(
                connection,
                name,
                dtype,
                row_count=row_count,
                exposure_column=exposure_column if exposure_column in schema else None,
            )
            for name, dtype in schema.items()
        ]
```

- [ ] **Step 3: Run the agreement test**

```bash
uv run pytest packages/pricing-core/tests/test_profile.py -q
```

Expected: PASS, agreement test included.

**If the histogram disagrees between engines, do not add a tolerance.** Read that test's docstring — every divergence it caught was a real defect. Likely causes, in order:
1. The float repr in the SQL string does not round-trip. Bind `edges[0]` and `width` as query parameters instead of interpolating them.
2. `floor` on a negative operand, if a column's minimum is negative. The `greatest(0, ...)` guard covers it — confirm it is present.
3. DuckDB summing exposure in a different order. `_stored_exposure` rounds to 6 dp precisely to absorb that; a difference surviving the rounding is larger than a last-bit difference and is a real disagreement.

- [ ] **Step 4: Add a direct two-engine histogram test**

The agreement test compares whole dumps; this one names the requirement so `req-coverage.py` can see it:

```python
@pytest.mark.req("FR-65")
def test_both_engines_bin_a_column_identically(tmp_path: Path) -> None:
    frame = pl.DataFrame(
        {
            "driver_age": [17 + (i % 60) for i in range(400)],
            "exposure_years": [0.5 + (i % 3) / 4 for i in range(400)],
        }
    )
    path = tmp_path / "ages.parquet"
    frame.write_parquet(path)

    from_frame = profile_frame(frame, dataset_version_id=uuid4()).column("driver_age")
    from_parquet = profile_parquet([str(path)], dataset_version_id=uuid4()).column("driver_age")

    assert from_frame is not None and from_parquet is not None
    assert from_frame.histogram == from_parquet.histogram
```

- [ ] **Step 5: Run and commit**

```bash
uv run pytest packages/pricing-core/tests/test_profile.py -q
uv run ruff check . && uv run mypy && uv run lint-imports
git add packages/pricing-core
git commit -m "feat(data): the DuckDB path bins identically, and the engines agree again"
```

---

## Task 5: FR-64's rename

FR-64 (`docs/specs/01-data-management.md`, ~line 160) decided this rename and assigned it to "the slice that next changes the profile contract". **This is that slice.** The requirement also says the money-scan exclusion "may not grow" — deleting it is how this task proves the rename landed.

**Files:**
- Modify: `packages/model-schema/src/model_schema/profiles.py` (`OneWayRow`)
- Modify: `packages/pricing-core/src/pricing_core/data/profile.py` (`_one_way_row`)
- Modify: `docs/contracts/schemas/profile.schema.json`, `banding.schema.json`, `peril-structure.schema.json` — **only where the field is `OneWayRow`'s mean**
- Modify: `backend/tests/test_contracts.py` (delete `ratio_statistics`)
- Modify: `frontend/src/views/ProfileView.vue` and its test
- Modify: `docs/specs/01-data-management.md` (FR-64 marked delivered)
- Regenerate: `docs/contracts/schemas/generated/*`, `docs/contracts/openapi/generated.json`, `frontend/src/api/generated/`

**Interfaces:**
- Produces: `OneWayRow.mean_severity: float | None` and `OneWayRow.mean_burning_cost: float | None`, replacing `severity_minor` and `burning_cost_minor`. Both stay floats and stay expressed in the workspace currency's minor unit — **only the names change** (FR-64).

- [ ] **Step 1: Enumerate the true targets, and the ones that must not move**

```bash
cd /home/puzhenhao1989/gi-pricing-plan
echo "--- rename these ---"
grep -rn "\bseverity_minor\b" --include=*.py --include=*.ts --include=*.vue --include=*.json \
  packages backend/src backend/tests frontend/src docs/contracts | grep -v "/generated/"
grep -rn "\bburning_cost_minor\b" --include=*.py --include=*.ts --include=*.vue --include=*.json \
  packages backend/src backend/tests frontend/src docs/contracts \
  | grep -v "/generated/" | grep -v "modelled_burning_cost_minor\|observed_burning_cost_minor"
echo "--- LEAVE THESE ALONE (genuine integer money) ---"
grep -rn "modelled_burning_cost_minor\|observed_burning_cost_minor" --include=*.py packages
```

Expect roughly a dozen sites in each of the first two groups and a handful in the third. **Do not run a bare `sed` over `burning_cost_minor`** — it would rename the peril structure's genuine `MoneyMinor` fields and break FR-10.

- [ ] **Step 2: Write the failing test**

Check `one_way`'s exact signature first (`grep -n "def one_way" packages/pricing-core/src/pricing_core/data/profile.py`) and match it. Add to `packages/pricing-core/tests/test_profile.py`:

```python
@pytest.mark.req("FR-64")
def test_the_one_way_means_are_named_as_means_not_as_minor_units() -> None:
    """FR-10 reserves `_minor` for integer minor units; both of these are float means."""
    summary = one_way(
        FRAME,
        column="vehicle_group",
        exposure_column="exposure_years",
        claim_count_column="claim_count",
        claim_amount_column="claim_amount_minor",
    )
    row = summary.rows[0]

    assert row.mean_severity is not None
    assert row.mean_burning_cost is not None
    assert not hasattr(row, "severity_minor")
    assert not hasattr(row, "burning_cost_minor")
```

- [ ] **Step 3: Run it to verify it fails**

```bash
uv run pytest packages/pricing-core/tests/test_profile.py -k named_as_means -q
```

Expected: FAIL — `AttributeError: 'OneWayRow' object has no attribute 'mean_severity'`.

- [ ] **Step 4: Rename, site by site**

`packages/model-schema/src/model_schema/profiles.py`, `OneWayRow`:

```python
    mean_severity: float | None = None
    severity_ci: tuple[float, float] | None = None
    mean_burning_cost: float | None = None
```

Amend the class docstring's second paragraph to name the new fields and keep its reason ("they are statistics, not amounts").

Then work Step 1's list. In the hand-authored schemas change the property **key** only — the type stays, because the values are unchanged. In `frontend/src/views/ProfileView.vue`, `row.burning_cost_minor` becomes `row.mean_burning_cost` (~line 240) and `severity_minor` likewise; **the `/ 100` scaling stays** — the unit did not change, only the name.

In `backend/tests/test_contracts.py`, **delete** the `ratio_statistics` set (~line 123) and every reference to it in the scan. The new names do not match the scan's `money_like` pattern `(_minor$|relativity|premium|exposure)`, so no exclusion is needed. Deleting it is the proof.

- [ ] **Step 5: Regenerate both generated surfaces**

```bash
uv run python scripts/generate-contracts.py
export PATH="$HOME/.npm-global/bin:$PATH"
pnpm --dir frontend generate:api
```

- [ ] **Step 6: Run everything that touches the name**

```bash
uv run pytest -q
pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test
uv run python scripts/generate-contracts.py --check
```

Expected: all green. `--check` proves the committed contracts match the models after the rename.

> **`backend/tests/test_demo_guide.py` is derived (FR-409)**, and it reads the profile contract. If it fails, the derivation needs the new names — never hand-edit the guide.

- [ ] **Step 7: Mark FR-64 delivered**

In `docs/specs/01-data-management.md`, replace FR-64's "**Not yet delivered**: …" through "Owner: the next slice to change the profile contract." with:

> **Delivered 2026-08-18**, in the slice that added FR-65's histogram — the change to the profile contract OQ-544 was waiting for. The hand-written money-scan exclusion in `backend/tests/test_contracts.py` is deleted: `mean_severity` and `mean_burning_cost` do not match the scan's pattern, so nothing needs excluding.

- [ ] **Step 8: Audit and commit**

```bash
python3 scripts/audit-docs.py
git add packages backend frontend/src docs
git commit -m "refactor(data): FR-64's rename — mean_severity, mean_burning_cost

A mean is not a minor unit. The hand-written money-scan exclusion goes with
it, which is what FR-64 said may not grow."
```

---

## Task 6: Publish the generated profile contract, and reconcile what it exposes

`profile.schema.json` is a hand-authored Phase-0 contract with no generated counterpart — the position `banding` and `grouping` were in when **four divergences** accumulated unseen. The existing conformance tests compare **top-level properties only**, and the profile's divergences are one level down, in `ColumnProfile`. This task adds both the generated file and a nested comparison.

**Files:**
- Modify: `scripts/generate-contracts.py`
- Create (generated): `docs/contracts/schemas/generated/profile.schema.json`
- Modify: `docs/contracts/schemas/profile.schema.json` — only where the **contract** is wrong
- Modify: `backend/tests/test_contracts.py`

**Interfaces:**
- Consumes: `Profile` from `model_schema`, with Tasks 2–5 applied.
- Produces: slug `profile` in `GENERATED_SHAPES`; a nested conformance test over `ColumnProfile`.

- [ ] **Step 1: Register the shape and look at what appears**

Add to `GENERATED_SHAPES` in `scripts/generate-contracts.py`, in the established commented style:

```python
    # Added 2026-08-18 (WK-661, the profile contract). `profile.schema.json` is a hand-authored
    # Phase-0 contract that nothing has ever compared against code — the position `banding`
    # and `grouping` were in when four divergences had accumulated unseen. It is also the
    # artifact `02`'s factor workbench reads and never recomputes (FR-62), so a field
    # the contract promises and the model does not carry is a wrong number on a screen
    # rather than a documentation defect.
    "profile": "Profile",
```

```bash
uv run python scripts/generate-contracts.py
python3 - <<'PY'
import json, pathlib
root = pathlib.Path("docs/contracts/schemas")
gen = json.loads((root / "generated" / "profile.schema.json").read_text())
aut = json.loads((root / "profile.schema.json").read_text())
props = lambda d: set(d.get("properties", {}))
print("top-level, contract-only :", sorted(props(aut) - props(gen)))
print("top-level, model-only    :", sorted(props(gen) - props(aut)))
PY
```

Record the output verbatim — it is the divergence list this task must give verdicts on. Expect the contract to declare `job_id` and `weight_column`, which the model lacks, and the model to produce `id`, `row_count` and `library_versions`, which the contract does not declare.

- [ ] **Step 2: Write the failing nested conformance test**

Pydantic emits nested models as `$ref` into `$defs`, so a one-hop resolver is needed. **Check whether `test_contracts.py` already has one and reuse it**; otherwise add beside `_load`:

```python
def _resolve(document: dict, node: dict) -> dict:
    """Follow a local `$ref` one hop. Pydantic nests models through `$defs`."""
    ref = node.get("$ref")
    if ref is None:
        return node
    return document["$defs"][ref.rsplit("/", 1)[-1]]
```

> Bare `dict`, matching `_load`'s own return type in that file. `test_contracts.py` imports
> only `Final` from `typing`, so a parameterised annotation would mean a new import for no
> gain — and mypy runs `--strict` on `packages/`, not on `backend/tests/`.

```python
@pytest.mark.req("FR-9")
def test_the_column_profile_shape_matches_its_contract() -> None:
    """The profile's divergences live one level down, where the flat tests do not look.

    `test_an_artifact_shape_carries_exactly_what_its_contract_declares` compares top-level
    properties. `ColumnProfile` is nested inside `columns.items`, which is where the
    histogram was missing for three days and where `min`/`minimum` still disagree — so a
    flat comparison would have reported this contract as conforming throughout.
    """
    generated = _load(GENERATED / "profile.schema.json")
    authored = _load(AUTHORED / "profile.schema.json")

    produced = set(
        _resolve(generated, generated["properties"]["columns"]["items"])["properties"]
    )
    declared = set(authored["properties"]["columns"]["items"]["properties"])

    assert not declared - produced, (
        f"the contract declares column fields the model lacks: {sorted(declared - produced)}"
    )
    assert not produced - declared, (
        "the model produces column fields the contract does not declare: "
        f"{sorted(produced - declared)}"
    )
```

- [ ] **Step 3: Run it to see the divergences named**

```bash
uv run pytest backend/tests/test_contracts.py -k column_profile -q
```

Expected: FAIL, listing the nested divergences. From the audit already done, expect at least:
- the contract says `min` / `max`, the model says `minimum` / `maximum`;
- the contract's `top_levels` items are objects `{level, count, exposure_years}`, the model's are two-element arrays.

`histogram` should **not** appear. If it does, Task 2 did not land.

- [ ] **Step 4: Give each divergence a verdict, and fix the side that is wrong**

Not a mechanical reconciliation. Decide which side is right and record it (`CLAUDE.md` §0):

| Divergence | Verdict | Action |
|---|---|---|
| `min`/`max` vs `minimum`/`maximum` | **Code is right.** `min` and `max` are Python builtins; the model has shipped `minimum`/`maximum` since Phase 1a and every consumer reads them. Renaming the model to match a document nobody consumes would break the frontend to tidy a schema. | Change the **contract** to `minimum`/`maximum`, with a dated note under `01` §4.7. |
| `top_levels` item shape | **Contract is right.** `("G1", 402)` gives a reader no way to know which element is the level, and the contract's third field (`exposure_years`) is the one an actuary needs — a top-20 by count is not a top-20 by exposure, and FR-60 asks for **both**. | A **model change with callers**. If it fits the slice, introduce a `LevelCount` shape and update `compare_profiles`, `psi_from_weights` and the frontend chip list. **If it does not**, append `FR-66` naming the obligation and an owner — do not edit the contract down to what was built. |
| `job_id`, `weight_column` on `Profile` | **Decide from the requirement, not the diff.** `weight_column` is what makes a one-way exposure-weighted and FR-61 implies it; `job_id` is provenance the Job model already records elsewhere. | Add `weight_column: str = "exposure_years"` to `Profile` if FR-61 reads that way; for `job_id`, either add it or remove it from the contract with a dated note saying where provenance lives instead. |
| `id`, `row_count`, `library_versions` on the model | **Model is right** — all three are recorded per artifact throughout this repository. | Add them to the contract. |

> A generated artifact matching its source proves neither is correct (`CLAUDE.md` §13 step 4). Check each field against **FR-60/61/62**, not only against the other file.

- [ ] **Step 5: Regenerate, verify, and prove the check bites**

```bash
uv run python scripts/generate-contracts.py
uv run pytest backend/tests/test_contracts.py -q
uv run python scripts/generate-contracts.py --check
```

Then prove the new test fails on deliberately broken input (`CLAUDE.md` §13 step 4):

```bash
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("docs/contracts/schemas/profile.schema.json")
d = json.loads(p.read_text())
d["properties"]["columns"]["items"]["properties"]["invented_field"] = {"type": "string"}
p.write_text(json.dumps(d, indent=2) + "\n")
PY
uv run pytest backend/tests/test_contracts.py -k column_profile -q   # expect FAIL naming invented_field
git checkout docs/contracts/schemas/profile.schema.json
```

Record both outputs — the closure standard asks for the failure, not the claim.

- [ ] **Step 6: Commit**

```bash
git add scripts/generate-contracts.py docs/contracts backend/tests/test_contracts.py \
        packages docs/specs/01-data-management.md
git commit -m "feat(contracts): generate the profile schema, and compare it where it diverges

The flat conformance test looks at top-level properties; every profile
divergence was one level down, in ColumnProfile."
```

---

## Task 7: The Profile view renders the histogram

`01` §5.3 asks the Profile view for "per-column cards, histograms, one-way charts with CI bands, PSI comparison selector". Histograms were absent because the field was. Also: `ProfileView.vue` (~line 264) colours the **dtype** label with `PSI_TONE[psiBand(null)]`, which reads as PSI support the view does not have.

**Files:**
- Create: `frontend/src/components/HistogramChart.vue`
- Modify: `frontend/src/views/ProfileView.vue`
- Test: `frontend/src/components/__tests__/HistogramChart.test.ts`, `frontend/src/views/__tests__/ProfileView.test.ts`

**Interfaces:**
- Consumes: `Histogram` via the regenerated `frontend/src/api/generated` types, re-exported through `@/api/profiles`.
- Produces: `<HistogramChart :histogram="column.histogram" />`.

- [ ] **Step 1: Regenerate the client and confirm the type arrived**

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
grep -n "histogram" frontend/src/api/generated/schema.d.ts | head
```

Expected: `histogram` appears. If not, the OpenAPI document was not regenerated — re-run Task 6's generation.

- [ ] **Step 2: Write the failing tests**

`frontend/src/components/__tests__/HistogramChart.test.ts`:

```ts
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import HistogramChart from "@/components/HistogramChart.vue";

const stubs = { VChart: { name: "VChart", template: "<div />", props: ["option"] } };

describe("HistogramChart", () => {
  it("labels each bar with its bin interval", () => {
    const wrapper = mount(HistogramChart, {
      props: { histogram: { edges: [0, 10, 20], counts: [3, 7], exposure: [] } },
      global: { stubs },
    });
    const option = wrapper.findComponent({ name: "VChart" }).props("option") as {
      xAxis: { data: string[] };
      series: { data: number[] }[];
    };

    expect(option.xAxis.data).toEqual(["0–10", "10–20"]);
    expect(option.series[0].data).toEqual([3, 7]);
  });

  it("plots exposure when the histogram carries it", () => {
    const wrapper = mount(HistogramChart, {
      props: { histogram: { edges: [0, 10, 20], counts: [3, 7], exposure: ["1.5", "9.25"] } },
      global: { stubs },
    });
    const option = wrapper.findComponent({ name: "VChart" }).props("option") as {
      series: { name: string; data: number[] }[];
    };

    expect(option.series.map((s) => s.name)).toContain("Exposure");
    expect(option.series[1].data).toEqual([1.5, 9.25]);
  });
});
```

Add to `frontend/src/views/__tests__/ProfileView.test.ts` — **read the file first** and follow its existing mocking of `@/api/profiles`:

```ts
  it("renders a histogram for a numeric column and none for a categorical one", async () => {
    // mount with a profile fixture whose driver_age carries a histogram
    // and whose vehicle_group does not
    expect(wrapper.findAllComponents({ name: "HistogramChart" })).toHaveLength(1);
  });

  it("does not colour the dtype label as though it were a PSI band", () => {
    expect(wrapper.html()).not.toContain("psi-");
  });
```

- [ ] **Step 3: Run them to verify they fail**

```bash
pnpm --dir frontend test -- HistogramChart ProfileView
```

Expected: FAIL — `Failed to resolve import "@/components/HistogramChart.vue"`.

- [ ] **Step 4: Write the component**

`frontend/src/components/HistogramChart.vue` — follow `OneWayChart.vue`'s structure (same `use([...])` registration, same `computed` option object):

```vue
<script setup lang="ts">
import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { Histogram } from "@/api/profiles";

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{ histogram: Histogram }>();

const edges = computed(() => props.histogram.edges ?? []);
const counts = computed(() => props.histogram.counts ?? []);
const exposure = computed(() => props.histogram.exposure ?? []);

function format(edge: number | undefined): string {
  if (edge == null) return "";
  return Number.isInteger(edge) ? String(edge) : edge.toFixed(2);
}

/** Bin labels from the edges. The last bin is closed (FR-65), hence the en dash. */
const labels = computed(() =>
  counts.value.map((_, i) => `${format(edges.value[i])}–${format(edges.value[i + 1])}`),
);

/**
 * Exposure is an exact decimal **string** (FR-10). `Number()` here is deliberate and
 * safe, for the reason `OneWayChart` gives: a chart coordinate is a float64 either way and
 * nothing computes with the plotted value.
 */
const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: exposure.value.length ? ["Rows", "Exposure"] : ["Rows"], bottom: 0 },
  grid: { left: 50, right: 50, top: 16, bottom: 46 },
  xAxis: { type: "category" as const, data: labels.value, axisLabel: { rotate: 45 } },
  yAxis: [
    { type: "value" as const, name: "Rows", position: "left" as const },
    ...(exposure.value.length
      ? [{ type: "value" as const, name: "Exposure", position: "right" as const }]
      : []),
  ],
  series: [
    { name: "Rows", type: "bar" as const, data: counts.value, yAxisIndex: 0 },
    ...(exposure.value.length
      ? [
          {
            name: "Exposure",
            type: "bar" as const,
            yAxisIndex: 1,
            data: exposure.value.map((e) => Number(e)),
          },
        ]
      : []),
  ],
}));
</script>

<template>
  <VChart
    class="h-40 w-full"
    :option="option"
    autoresize
  />
</template>
```

If `@/api/profiles` does not re-export `Histogram`, add the export there — do **not** declare the shape in the component (`CLAUDE.md` §2).

- [ ] **Step 5: Wire it into the view and remove the fake PSI badge**

In `frontend/src/views/ProfileView.vue`, import `HistogramChart` and add inside the column `<article>`, after the `<dl>`:

```vue
            <HistogramChart
              v-if="column.histogram"
              :histogram="column.histogram"
              class="mt-2"
            />
```

Replace the dtype span (~line 263) with an uncoloured one:

```vue
              <span class="ml-auto text-xs text-slate-500">{{ column.dtype }}</span>
```

Drop the now-unused `psiBand` import and `PSI_TONE` entry **only if nothing else in the file uses them** — check first. `psiBand` stays in `@/api/profiles`: it is correct code awaiting the comparison selector, which is not this slice.

- [ ] **Step 6: Run the frontend gate**

```bash
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

Expected: all 0; test count above the current 105.

- [ ] **Step 7: Commit**

```bash
git add frontend/src
git commit -m "feat(w6a): the profile view renders FR-65's histogram

The dtype label no longer borrows a PSI colour for a comparison the view
cannot make; psiBand stays for the selector slice that will."
```

---

## Task 8: Specs, roadmap, and the full gate

**Files:**
- Modify: `docs/specs/01-data-management.md` (§5.3 note)
- Modify: `docs/roadmap.md` (slice record; WK-661 row; the divergence rows)
- Modify: `CLAUDE.md` §2 layout marks **only if** a `◐`/`✔` genuinely changed

- [ ] **Step 1: Reconcile `01` §5.3 with what the view now does**

The Profile row claims four things. Histograms now exist; the **PSI comparison selector still does not** — `compareProfiles()` has no caller. Say so in place rather than deleting the claim (`CLAUDE.md` §14: resolve, never soften). Append a dated note under §5.3:

> *(2026-08-18)* The Profile view's histograms landed with FR-65. The **PSI comparison selector has not**: `compareProfiles()` is implemented and has no caller, and the dtype label that borrowed a PSI colour has been uncoloured rather than left reading as support the view lacks. FR-63's endpoint exists; the view that reads it is unowned. Owner: the slice that next opens `ProfileView.vue`, or WK-664.

- [ ] **Step 2: Update the roadmap**

Add the slice record to WK-661's list (it becomes the seventeenth) in the established form: what landed, what it found, what it deliberately did not do. Update the "Two unresolved model/contract divergences" row — the `ColumnProfile` half **resolved** with the date, the `Dataset` half now `OQ-565` and open. Update the §5.3 audit row (~line 701): histograms delivered, PSI selector still absent with an owner.

- [ ] **Step 3: Run the whole gate, both halves, reading each exit code**

```bash
cd /home/puzhenhao1989/gi-pricing-plan
uv run ruff check .;                                 echo "ruff=$?"
uv run mypy;                                         echo "mypy=$?"
uv run lint-imports;                                 echo "imports=$?"
uv run pytest -q;                                    echo "pytest=$?"
python3 scripts/audit-docs.py;                       echo "audit=$?"
uv run python scripts/req-coverage.py;               echo "reqs=$?"
uv run python scripts/generate-contracts.py --check; echo "contracts=$?"

export PATH="$HOME/.npm-global/bin:$PATH"
pnpm --dir frontend install --frozen-lockfile;       echo "install=$?"
pnpm --dir frontend generate:api;                    echo "genapi=$?"
pnpm --dir frontend lint;                            echo "lint=$?"
pnpm --dir frontend type-check;                      echo "types=$?"
pnpm --dir frontend test;                            echo "fetest=$?"
pnpm --dir frontend build;                           echo "build=$?"
```

Every line must print `=0`. **Read each command's own exit code** — a piped `&& echo ok` reports the last stage's and has produced a false clean here before.

Baselines for the progress entry: the suite was **1224 passed**, requirements **456 specified / 215 marked (47.1 %)**, frontend **105 tests**, **20 generated contracts**.

- [ ] **Step 4: Verify the demo guide still derives**

```bash
uv run pytest backend/tests/test_demo_guide.py -q
```

FR-409 makes the guide derived, not written — a failure means the derivation needs the renamed fields, never a hand edit to the guide.

- [ ] **Step 5: Commit, push, PR**

```bash
git add docs CLAUDE.md
git commit -m "docs(data): the profile contract slice — histogram, rename, generated counterpart"
git fetch origin && git rebase origin/main       # sessions run concurrently here
git push -u origin HEAD --force-with-lease
gh pr create --title "feat(data): the profile contract — histogram, FR-64's rename, and a generated counterpart"
gh pr view <n> --json mergeStateStatus            # CLEAN means checks passed
```

- [ ] **Step 6: Update the working state**

Append one entry to `progress.md` (never rewrite it): what was done, the gate table with real numbers, the enforcement proven against broken input from Task 6 Step 5, and where the next session starts. Then **rewrite** `task_plan.md`'s "Next build step" so it no longer names this item, and add `OQ-565` to its decisions-waiting table.

---

## Self-Review

**Spec coverage.**

| Spec obligation | Task |
|---|---|
| `01` §4.7's `histogram` in the contract example | 2, 3, 4 |
| `docs/contracts/schemas/profile.schema.json`'s histogram block | 2, 6 |
| `01` §5.3 "histograms" in the Profile view | 7 |
| `01` §5.3 "PSI comparison selector" | **Not delivered** — stated in place with an owner (Task 8 Step 1). `compareProfiles()` exists and has no caller; wiring it is a view slice with its own test surface, and the part that actively misleads — the borrowed PSI colour — is removed here. |
| `01` §5.3 dataset list "status badge, last validated, owner" | **Not delivered** — genuinely open, raised as `OQ-565` (Task 1) rather than silently picked. |
| FR-64 (owner: "the next slice to change the profile contract") | 5 |
| FR-60's enumerated statistics | Unchanged. FR-65 is **appended**, not FR-60 edited — ids are permanent. |
| FR-62 (one answer regardless of engine) | 4 — the agreement test carries the histogram free |
| FR-9 (contract conformance) | 6 |
| FR-10 (money discipline) | 5 — the exclusion is deleted, not grown |

**Type consistency.** `Histogram` is defined once (Task 2) and consumed under that name in Tasks 3, 4, 6, 7. `_histogram_edges` and `_stored_exposure` are declared in Task 3's Produces block and called in Task 4. `_profile_column` gains `exposure_column` in Task 4 only. `mean_severity` / `mean_burning_cost` appear first in Task 5 and nowhere earlier.

**Known soft spot.** Task 6 Step 4's `top_levels` verdict is the one thing this plan cannot decide in advance: whether the shape change fits the slice depends on how many callers `compare_profiles` and `psi_from_weights` turn out to have. The escape hatch is written into the step — append `FR-66` with an owner rather than editing the contract down to what was built (`CLAUDE.md` §14).

**Deliberate ordering note.** Task 3 leaves `test_the_two_profiling_paths_agree` red until Task 4 closes it. That is stated in both tasks, with the instruction not to weaken the test. If red-between-commits is unacceptable for this branch, merge Tasks 3 and 4 into one commit — but do not soften the assertion.

---

## Execution Handoff

Plan saved to `.planning/PL-00731-the-profile-contract-histogram-rename-and-the-generated-counterpart.md` — git-ignored (`.gitignore` names `/.planning/`), matching the repo's stated policy that a committed plan file would be "a second, unaudited account of what the project is doing".

Two execution options:

1. **Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute in this session using `executing-plans`, batch execution with checkpoints.
