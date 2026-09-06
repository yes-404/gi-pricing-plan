---
id: PL-736
family: plan
kind: leaf
title: The GLM Approximation as a Model — Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-19
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-19-glm-approximation-as-model.md
---

# The GLM Approximation as a Model — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist the GLM approximation of a GBM as a Model in its own right, so a
`TransparencyArtifact` references it by `approximating_model_id` instead of carrying its
coefficients inline (FR-137, OQ-577 decided 2026-08-18).

**Architecture:** The `model.transparency` Job already fits a GLM to the booster's own
predictions and throws the fitted object away, keeping only its summary. This slice keeps
it: `pricing-core` returns the `GlmFitResult` and the two augmented frames beside the
measurements, and the handler reserves a Model for it, records the fit with diagnostics of
the surrogate **against the source model's predictions**, and puts that Model's id in the
artifact. The surrogate is identifiable from its spec alone — `approximates_model_id` set
**iff** `response_column` is the reserved surrogate column — which is what lets every
reader tell a surrogate from a model fitted on observed claims without a second field
saying so.

**Tech Stack:** Python 3.12, Pydantic v2 (`model-schema`), Polars + glum (`pricing-core`),
SQLAlchemy 2.x async + Celery worker (`backend`), pytest with `@pytest.mark.req` markers.

**Spec:** `docs/specs/02-modelling.md` — FR-137 (§3.6), §4.4 `ModelSpec`, §4.8 `Model`,
§4.9 `TransparencyArtifact`, §5.1 error codes, §5.2 `pricing-core` interfaces.
Decision record: `docs/open-questions.md` OQ-577.

---

## Global Constraints

- **Requirement IDs are permanent** (`CLAUDE.md` §5). Append or mark superseded; never
  renumber. Find the **maximum** id in `02`'s table, not the last one you read — the table
  is not in numeric order.
- **`model-schema` is the single source of truth** for any shape crossing a boundary
  (`CLAUDE.md` §2). Nothing else defines one, including tests.
- **`pricing-core` reaches no database and stores no blob** (ADR-703). It is handed
  resolved artifacts and returns data.
- **Artifacts are immutable.** `transparency_artifacts` is insert-only at the privilege
  layer (FR-43); a Model is immutable once fitted (`02` R2).
- **Never nest `database.unit_of_work()`.** An inner one takes a second connection and
  **deadlocks against the pool with no output and no traceback**. Sequence transactions.
- **Money is never float** — not touched by this slice, but the rule stands.
- Every new test carries a `@pytest.mark.req("FR-…")` marker naming a requirement that
  exists (`scripts/req-coverage.py` fails on one that does not).
- Ruff line length 100; `mypy --strict` over `packages/` and `backend/`.
- Conventional Commits; branch from `main`; **do not push or open a PR** unless the
  maintainer asks — the branch's ending is theirs.

### Environment

```bash
uv sync --all-packages --dev
docker compose -f deploy/docker-compose.yml up -d --wait
export GIP_TEST_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
export GIP_DATABASE_URL="$GIP_TEST_DATABASE_URL"
uv run alembic upgrade head
```

Without `GIP_TEST_DATABASE_URL` about **90 backend tests skip silently** and the run looks
green. `libgomp1` is required by LightGBM (`sudo apt-get install -y libgomp1`); without it
`packages/pricing-core/tests/test_transparency.py` fails at collection with no obvious link
to this change. `pnpm` is at `~/.npm-global/bin`, not on the default PATH.

---

## Decision gate — **ANSWERED by the maintainer, 2026-08-19: option A**

> The maintainer chose **A** when commissioning execution: `coefficients`/`relativities`
> stay on `GlmApproximation` as a legacy era, exclusive with `approximating_model_id` at the
> type. Task 2 Step 4 and Task 1 Step 5 are written for A and need no change; the option-B
> fallback at the end of this section is now dead and must not be built.

## The gate as it was put

**What happens to a `TransparencyArtifact` written before this slice?** Its
`glm_approximation` block carries `coefficients` and `relativities` inline and no
`approximating_model_id`. `TransparencyArtifact` is `extra="forbid"`, so whatever the new
shape is, the old rows are read through it by `to_artifact`.

| | Option | Consequence |
|---|---|---|
| **A** *(recommended)* | Keep `coefficients`/`relativities` on `GlmApproximation` as **legacy-only**, with a validator making the two eras exclusive: `approximating_model_id is None` **iff** inline coefficients are present. New writes always set the id and never the inline fields. | Old evidence stays readable and stays labelled as pre-FR-137. The published contract carries two eras, with a dated note saying which is which. This is the shape `covariance_blob` already has — optional, with the absence given a stated meaning rather than pretended away. |
| **B** | Remove both fields outright. | One meaning in the contract. Every artifact written before today fails validation on read — a 500 on `GET /models/{id}/transparency`, not a graceful message — unless a data migration rewrites or deletes rows, which destroys the evidence an approval was granted against. |

**Recommendation: A.** The repository's own precedent is `covariance_blob` ("every Model
fitted before this date has none", FR-195) and FR-207's staging rule: an absence
with a stated meaning, not a shape that pretends the earlier era did not happen. The cost
is one validator and one dated spec note.

The plan below is written for **A**. If the maintainer chooses **B**, Task 2 Step 3 drops
the two fields and their validator instead, Task 2 Step 1's test becomes a test that a
legacy payload is refused, and Task 1 records B's reasoning in place of A's.

---

## Rulings made while planning

**RL-864 — no new field on `Diagnostics` for "these are surrogate diagnostics".**
FR-137(iii) requires the surrogate's diagnostics to be *recorded as* diagnostics
against the source model's predictions. A `surrogate_of` field on `Diagnostics` would be a
copy of `GlmSpec.approximates_model_id`, and this repository's rule is that a fact stated
twice diverges (`CLAUDE.md` §2) — `GlmSpec.uncertainty_basis` is derived "rather than
stored on purpose" for exactly this reason, and `TransparencyArtifact.kinds` and
`Model.flags` are both derived. Instead the **spec** carries it, and Task 2 makes it
impossible to hide: `approximates_model_id` is set **iff** `response_column` is the
reserved surrogate column, so a reader holding either the Model or its spec knows what the
A/E is measured against, and a spec cannot claim to be a surrogate while pointing at an
observed response column. *Cost if wrong:* a reader who has the `Diagnostics` document and
not the Model must fetch the Model. Both come from the same model id.

**RL-865 — `approximates_model_id` is a bare `UUID`, not an `IntervalFor`-shaped block.**
FR-200 gave `interval_for` a block with the central model's id *and* version because
`motor-ad-frequency@7` is what a human reads in a review. FR-137 names the field
`approximates_model_id` twice, and a block under a different name would contradict the
requirement text. `interval_for` needed a block regardless — it carries `alpha` — and this
one carries nothing else. *Cost if wrong:* a reviewer resolves one extra id to get a
version. Recorded in `02` §4.4 as a dated note so the divergence is deliberate.

**RL-866 — the surrogate Model's `covariance_blob` is stripped, not stored.**
`fit_glm` returns a `GlmFit` whose `result.covariance_blob` is already a `BlobRef` and
whose bytes the caller must store; today the approximation takes `.result` and drops the
bytes, so persisting that result unchanged would give the surrogate Model a reference
resolving to nothing. The fix is to persist `result.model_copy(update={"covariance_blob":
None})`: the surrogate then reports FR-195's typed absence at predict time instead of
offering a GLM interval that a careless reader would take for the GBM's uncertainty — which
is the existing code comment's reasoning, unchanged, now with somewhere to live. *Cost if
wrong:* the surrogate offers no prediction interval; OQ-576 is where that question
belongs anyway.

**RL-867 — the surrogate is reserved and fitted inside the transparency Job's final
transaction, not by a second Job.** Reserve, `record_fit` and `record_transparency` are one
`unit_of_work`, so a compute that fails leaves nothing behind, and the artifact never
commits without the Model it references. `reserve_model` is idempotent on `spec_hash`, so a
rebuilt artifact reuses the same surrogate Model and `record_fit` is skipped — calling it
twice would raise `MODEL_IMMUTABLE` and fail the Job. *Cost if wrong:* one transaction holds
the fit and the artifact writes together; both are small.

**RL-868 — the plan's test counts are not acceptance criteria.** Report the number the run
prints. The gate is each command's own exit code.

---

## File structure

| File | Responsibility after this slice |
|---|---|
| `packages/model-schema/src/model_schema/modelling.py` | `GlmSpec.approximates_model_id`, `SURROGATE_RESPONSE_COLUMN`, and the iff-validator that ties them together |
| `packages/model-schema/src/model_schema/transparency.py` | `GlmApproximation` carries the model reference; the inline table is legacy-only and the two eras are exclusive |
| `backend/src/app/platform/modelling.py` | `SPEC_HASH_VERSION` → 5; `_refuse_mismatched_approximation` beside `_refuse_mismatched_interval_model` |
| `backend/src/app/platform/model_specs.py` | `validate_spec` does not report a surrogate's response column as missing |
| `packages/pricing-core/src/pricing_core/modelling/transparency.py` | `approximation_spec()` (pure) and `build_glm_approximation()` returning `GlmApproximationFit` |
| `backend/src/app/worker/model_handlers.py` | `_transparency` reserves the surrogate Model, records its fit and diagnostics, and references it from the artifact |
| `docs/specs/02-modelling.md` | §3.6, §4.4, §4.8, §4.9, §5.1 error codes, §5.2 signatures — all dated |
| `docs/open-questions.md` | OQ-577's outcome column records the build date |
| `docs/roadmap.md` | WK-661 slice record |
| `docs/contracts/**` | regenerated, never hand-edited |

Tests: `packages/model-schema/tests/test_modelling_contracts.py` (or the file that holds
`GlmSpec` tests — check first), `packages/pricing-core/tests/test_transparency.py`,
`backend/tests/test_spec_hash.py`, `backend/tests/test_model_specs.py`, and a new
`backend/tests/test_glm_approximation_model.py`.

---

### Task 1: The specification change

**Files:**
- Modify: `docs/specs/02-modelling.md` — §3.6 (a new requirement row), §4.4, §4.8, §4.9,
  §5.1 error codes, §5.2 signatures
- Modify: `docs/open-questions.md` — OQ-577's outcome column
- Test: none — docs only. `python3 scripts/audit-docs.py` is the check.

**Interfaces:**
- Consumes: nothing.
- Produces: **FR-141** (the id every later task's `@pytest.mark.req` marker cites for
  the surrogate-identifiability invariant) and the error code
  `MODEL_APPROXIMATION_INVALID`, which Task 5 raises.

- [ ] **Step 1: Confirm the requirement id before writing it**

`02`'s requirement table is **not in numeric order**, so read the maximum rather than the
last row:

```bash
cd /home/puzhenhao1989/gi-pricing-plan
grep -rho "FR-MODEL-[0-9]\+" docs/ | sort -u -t- -k3 -n | tail -3
```

Expected: `FR-201` is the maximum, so the new requirement is **FR-141**. If it
is not, use `max + 1` and use that id everywhere this plan says FR-141.

- [ ] **Step 2: Append FR-141 to §3.6's requirement table**

Add as the last row of the §3.6 table (after the FR-140 row):

```markdown
| **FR-141** | **A surrogate is identifiable from its spec alone.** Added 2026-08-19 (WK-661, building FR-137). `GlmSpec.approximates_model_id` is set **if and only if** `response_column` is the reserved surrogate column `__gbm_prediction__`, refused at the type in both directions. A spec that named a source model while pointing at an observed response column would describe a model fitted on claims and read as a surrogate; one that fitted the reserved column while naming no source would be a model of a prediction nobody can identify. This is also what makes FR-137(iii) enforceable without a second field: the A/E in the surrogate's `Diagnostics` is against the source model's predictions because the spec the diagnostics were computed under says so, and `CLAUDE.md` §2's rule against a fact stated twice keeps it there rather than copied onto the diagnostics document. Two consequences are stated rather than left to be discovered: a surrogate Model **carries no `covariance_blob`**, so FR-195's typed absence is what a prediction against it reports — an interval computed from a surrogate's coefficients describes the surrogate and would be read as the GBM's uncertainty; and a surrogate **appears in `GET /api/v1/models`** like any other Model, which is the point of FR-137 rather than a side effect. |
```

- [ ] **Step 3: Record the field in §4.4 with the divergence from `interval_for`**

Add `approximates_model_id` to §4.4's `glm` arm where the arm's fields are listed, and
append this dated note to §4.4:

```markdown
> **`approximates_model_id` is live from 2026-08-19 (WK-661, FR-137)**, on `GlmSpec`
> rather than on the common block: only a GLM approximates another model, and a field
> defined on the union rather than on the arm that uses it is a field the other arm will
> eventually be asked to spell.
>
> **It is a bare `UUID`, and that is a deliberate divergence from `interval_for`.**
> FR-200 gave the paired-quantile link a block carrying the central model's id *and*
> version, because `motor-ad-frequency@7` is what a human reads in a review and a UUID is
> not. This field is a bare id because FR-137 names it that way and a block under a
> different name would contradict the requirement — and because `interval_for` needed a
> block regardless, carrying `alpha`, while this carries nothing else. A reviewer resolves
> one id to get the version.
>
> **`spec_hash` moves `v4` to `v5` with it** (FR-206): the model a surrogate
> approximates is part of what that surrogate *is*, and two approximations of two different
> GBMs over one population would otherwise share a digest — which FR-204 would answer
> by handing the second caller the first caller's model.
```

- [ ] **Step 4: Record the two consequences in §4.8**

Append to §4.8, after the `covariance_blob` note:

```markdown
> **A surrogate Model reaches `fitted` on diagnostics against another model's predictions**
> (FR-137(iii), built 2026-08-19). §4.8's `status ≥ fitted ⟹ diagnostics_id` is met
> the same way every other model meets it, and the quantity is different: the A/E, lift and
> calibration are the surrogate against the source GBM's predictions over the same split —
> FR-136's quantity, on both partitions. Nothing on the `Diagnostics` document says so,
> and nothing needs to: FR-141 makes the spec say it, and a fact stated in two places
> diverges.
>
> **It carries no `covariance_blob`.** The bytes exist at fit time and are deliberately
> dropped, so a prediction against a surrogate reports FR-195's typed absence rather
> than an interval. The interval would be a correct statement about the surrogate's
> coefficients and would be read as the GBM's uncertainty; FR-198 already refuses a
> GBM approximation on exactly this ground.
```

- [ ] **Step 5: Correct §4.9's note and record the two eras**

§4.9's JSON example already shows `approximating_model_id` and no inline coefficients — it
was written for the built state, and the built state now matches it. Replace the module's
old caveat by appending:

```markdown
> **`approximating_model_id` is live from 2026-08-19 (WK-661, FR-137).** The block holds
> the *measurements* — R², deviance explained, worst regions, the relativity-table blob —
> and the table itself is the approximating Model's `fit_result`, reachable by that id like
> any other Model's.
>
> **Artifacts written before this date carry the table inline and no id, and stay
> readable.** `coefficients` and `relativities` remain on the block as a legacy era, and
> the two are exclusive at the type: an artifact carries a model reference or an inline
> table, never both and never neither. The alternative — dropping the fields — would make
> every artifact written before today fail validation on read, and those artifacts are the
> evidence a Rating Version's approval was granted against (FR-136). This is the shape
> `covariance_blob` already has: an absence with a stated meaning rather than a contract
> that pretends the earlier era did not happen.
```

- [ ] **Step 6: Add the error code to §5.1**

Append `MODEL_APPROXIMATION_INVALID` to §5.1's error-code list, and add this note beside
the `MODEL_INTERVAL_PAIR_INVALID` note:

```markdown
> **`MODEL_APPROXIMATION_INVALID` added 2026-08-19 (WK-661, FR-137).** It refuses a spec
> whose `approximates_model_id` names a Model the surrogate cannot be an approximation of —
> one that is not fitted, one that is itself a GLM (FR-132 applies to non-GLM models,
> and a GLM approximating a GLM reports 100 % fidelity that looks like evidence), or one
> whose dataset version, split or factor set disagrees with the surrogate's. Its own code
> rather than `VALIDATION_FAILED` for `MODEL_INTERVAL_PAIR_INVALID`'s reason: the request is
> well formed and both models are real, and what fails is the relation between them.
```

- [ ] **Step 7: Correct §5.2's signature**

§5.2 still declares `build_glm_approximation(model: Model, data, spec) -> GlmApproximation`,
which the 2026-08-16 note already flagged as a signature that "will need it when their
slices land". Replace the two transparency lines with what Task 3 builds:

```python
# pricing_core/modelling/transparency.py
def approximation_spec(spec: GbmSpec, *, source_model_id: UUID) -> GlmSpec
def build_glm_approximation(result: GbmFitResult, booster: bytes, spec: GbmSpec,
                            factors: Sequence[Factor], data: pl.DataFrame, *,
                            holdout: pl.DataFrame, source_model_id: UUID,
                            bandings=None, groupings=None,
                            progress: ProgressCallback | None = None
                            ) -> GlmApproximationFit
def build_shap_summary(result: GbmFitResult, booster: bytes, spec: GbmSpec,
                       factors: Sequence[Factor], data: pl.DataFrame, *, sample: int,
                       bandings=None, groupings=None,
                       progress: ProgressCallback | None = None) -> ShapSummary
```

and append:

```markdown
> **Both corrected 2026-08-19 (WK-661, FR-137)** — the correction the 2026-08-16 note
> predicted for every function declared as taking a `Model`. `build_shap_summary` had
> already been built to this shape and the spec had not caught up; `build_glm_approximation`
> additionally returns `GlmApproximationFit`, because the fitted surrogate is now persisted
> as a Model and a function that returned only its summary threw away the artifact.
```

- [ ] **Step 8: Record the outcome on OQ-577**

In `docs/open-questions.md`, append to OQ-577's outcome column (the row is already
struck through and marked decided — **do not** restate the decision, only its build):

```markdown
**Built 2026-08-19** (WK-661): `approximates_model_id` on `GlmSpec` joining `spec_hash` at
`v5`, the surrogate reserved and fitted inside the `model.transparency` Job with
diagnostics against the source model's predictions, and FR-141 appended for the
invariant that keeps a surrogate identifiable from its spec alone. The deadline the row
states is met: nothing references a transparency artifact by identifier yet.
```

- [ ] **Step 9: Run the docs audit and read its own exit code**

```bash
python3 scripts/audit-docs.py; echo "exit=$?"
```

Expected: `exit=0`, with the requirement count one higher than before (482 → 483) and every
open question mirrored. Two traps this file has hit before: **a pipe inside a code span
still splits a table row** (write `E[Y\|x]`), and **a bolded `**FR-141**` used as a
cross-reference reads as a second definition** — only the §3.6 row may define it.

- [ ] **Step 10: Commit**

```bash
cd /home/puzhenhao1989/gi-pricing-plan
git add docs/specs/02-modelling.md docs/open-questions.md
git commit -m "docs(model): FR-141 — a surrogate is identifiable from its spec (FR-137)"
```

---

### Task 2: The contract — `approximates_model_id`, the two eras, and `spec_hash` v5

**Files:**
- Modify: `packages/model-schema/src/model_schema/modelling.py` (`GlmSpec`, a new
  `SURROGATE_RESPONSE_COLUMN` constant, `__all__`)
- Modify: `packages/model-schema/src/model_schema/transparency.py` (`GlmApproximation`)
- Modify: `packages/model-schema/src/model_schema/__init__.py` (re-export the constant)
- Modify: `backend/src/app/platform/modelling.py:105` (`SPEC_HASH_VERSION` → 5, with its
  note)
- Modify: `backend/tests/test_spec_hash.py:160`
- Create: `packages/model-schema/tests/test_glm_approximation.py`
- Modify: `packages/model-schema/tests/test_gbm_spec.py` (the `GlmSpec` prohibitions live
  beside the existing spec tests)
- Regenerate: `docs/contracts/**` via `scripts/generate-contracts.py`

**Interfaces:**
- Consumes: FR-141 from Task 1 (the marker id).
- Produces:
  - `model_schema.SURROGATE_RESPONSE_COLUMN: Final[str] = "__gbm_prediction__"`
  - `GlmSpec.approximates_model_id: UUID | None = None`
  - `GlmApproximation.approximating_model_id: UUID | None`, with `coefficients` and
    `relativities` retained as the legacy era and exclusive with it
  - `SPEC_HASH_VERSION == 5`

- [ ] **Step 1: Write the failing schema tests**

Create `packages/model-schema/tests/test_glm_approximation.py`:

```python
"""The approximating Model's spec and the artifact block that references it.

FR-137 makes the GLM approximation a Model; FR-141 makes it one a reader can
recognise without holding anything else. Every test here is a prohibition, for the reason
`test_gbm_spec.py` gives: a shape that can represent a nonsense model eventually holds one.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import (
    SURROGATE_RESPONSE_COLUMN,
    Coefficient,
    GlmApproximation,
    GlmSpec,
    OffsetSpec,
    new_uuid7,
)

EXPOSURE = OffsetSpec(kind="log_column", column="exposure_years")


def _surrogate(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency-approx",
        "dataset_version_id": new_uuid7(),
        "response_column": SURROGATE_RESPONSE_COLUMN,
        "approximates_model_id": new_uuid7(),
        "family": "gamma",
        "link": "log",
        "offset": EXPOSURE,
    }
    return GlmSpec.model_validate(base | over)


@pytest.mark.req("FR-141")
def test_a_surrogate_declares_both_halves() -> None:
    """The pair is what makes a surrogate recognisable — neither half alone does."""
    spec = _surrogate()
    assert spec.approximates_model_id is not None
    assert spec.response_column == SURROGATE_RESPONSE_COLUMN


@pytest.mark.req("FR-141")
def test_a_spec_naming_a_source_model_over_an_observed_response_is_refused() -> None:
    """It would be a model fitted on claims that every reader takes for a surrogate."""
    with pytest.raises(pydantic.ValidationError, match=SURROGATE_RESPONSE_COLUMN):
        _surrogate(response_column="claim_count")


@pytest.mark.req("FR-141")
def test_a_spec_fitting_the_surrogate_column_with_no_source_model_is_refused() -> None:
    """A model of a prediction, with nothing saying whose prediction it is."""
    with pytest.raises(pydantic.ValidationError, match="approximates_model_id"):
        _surrogate(approximates_model_id=None)


@pytest.mark.req("FR-137")
def test_the_artifact_block_references_the_model_that_holds_the_table() -> None:
    block = GlmApproximation(
        approximating_model_id=new_uuid7(), r_squared=0.97, deviance_explained=0.96
    )
    assert block.coefficients == ()


@pytest.mark.req("FR-137")
def test_an_artifact_block_carrying_both_eras_is_refused() -> None:
    """A reference *and* an inline table are two answers to "where is the table?"."""
    with pytest.raises(pydantic.ValidationError, match="exactly one"):
        GlmApproximation(
            approximating_model_id=new_uuid7(),
            r_squared=0.97,
            deviance_explained=0.96,
            coefficients=(
                Coefficient(
                    term="intercept", estimate=-2.4, std_error=0.01, z=-199.8,
                    p_value=0.0, ci_95=(-2.44, -2.39),
                ),
            ),
        )


@pytest.mark.req("FR-137")
def test_an_artifact_block_carrying_neither_era_is_refused() -> None:
    """A fidelity score with no table behind it says the approximation was good without
    saying what it was — the module docstring's own reason for holding the table."""
    with pytest.raises(pydantic.ValidationError, match="exactly one"):
        GlmApproximation(r_squared=0.97, deviance_explained=0.96)
```

Check `Coefficient`'s required fields against
`packages/model-schema/src/model_schema/modelling.py:1119` before running — R5 makes the
standard error and interval mandatory, and the constructor above must satisfy the real
shape rather than this plan's memory of it.

- [ ] **Step 2: Run the tests and watch them fail for the right reason**

```bash
cd /home/puzhenhao1989/gi-pricing-plan
uv run pytest packages/model-schema/tests/test_glm_approximation.py -q; echo "exit=$?"
```

Expected: collection fails on `ImportError: cannot import name 'SURROGATE_RESPONSE_COLUMN'`.
That is the right failure. A test that fails because a *fixture* is wrong proves nothing.

- [ ] **Step 3: Add the constant, the field and the two validators**

In `packages/model-schema/src/model_schema/modelling.py`, beside the other module-level
constants:

```python
#: The response column of a GLM fitted to another model's predictions (FR-133).
#:
#: A reserved name rather than a caller's choice: FR-141 keys the surrogate invariant
#: on it, and a dataset column that happened to be called this would make a model fitted on
#: observed data indistinguishable from a surrogate. The dunder spelling is what keeps that
#: collision implausible rather than merely unlikely.
SURROGATE_RESPONSE_COLUMN: Final = "__gbm_prediction__"
```

On `GlmSpec`, after `tolerance`:

```python
    #: FR-137 — the Model whose predictions this GLM approximates. `None` for every
    #: model fitted on an observed response, which is every model but a surrogate.
    approximates_model_id: UUID | None = None

    @model_validator(mode="after")
    def _a_surrogate_says_so_in_both_places(self) -> GlmSpec:
        """FR-141: `approximates_model_id` is set iff the response is the surrogate
        column.

        Both directions, because each half alone is a different defect. A spec naming a
        source model over an observed response column is a model fitted on claims that
        every reader takes for a surrogate; one fitted on the surrogate column with no
        source named is a model of a prediction nobody can identify — and its diagnostics
        are then an A/E against an unnamed target, which is what FR-137(iii) exists to
        prevent.
        """
        surrogate_column = self.response_column == SURROGATE_RESPONSE_COLUMN
        if surrogate_column and self.approximates_model_id is None:
            raise ValueError(
                f"response_column is {SURROGATE_RESPONSE_COLUMN!r} and no "
                "approximates_model_id names the model it approximates (FR-141). "
                "A model of a prediction must say whose prediction it is."
            )
        if self.approximates_model_id is not None and not surrogate_column:
            raise ValueError(
                f"approximates_model_id is set and response_column is "
                f"{self.response_column!r}, not {SURROGATE_RESPONSE_COLUMN!r} "
                "(FR-141). A surrogate is fitted to another model's predictions; a "
                "spec fitted to an observed column is a model in its own right."
            )
        return self
```

Add `"SURROGATE_RESPONSE_COLUMN"` to `modelling.py`'s `__all__` and to
`model_schema/__init__.py`'s import block and `__all__`, keeping both alphabetical as the
file already is.

- [ ] **Step 4: Make the artifact block reference the Model, keeping the legacy era**

In `packages/model-schema/src/model_schema/transparency.py`, replace the
`approximating_model_id` field comment and add the validator:

```python
    #: FR-137 — the Model that holds the approximation's table. Set on every artifact
    #: written from 2026-08-19; `None` on artifacts written before, which carry the table
    #: inline instead.
    approximating_model_id: UUID | None = None
    ...
    #: **Legacy era.** Populated only on artifacts written before FR-137 was built
    #: (2026-08-19), where the table had nowhere else to live. New artifacts name a Model
    #: and leave these empty; the validator below refuses the mixture.
    coefficients: tuple[Coefficient, ...] = ()
    relativities: dict[str, tuple[RelativityLevel, ...]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _the_table_is_in_exactly_one_place(self) -> Self:
        """FR-137: a model reference, or an inline table, never both and never neither.

        Both is two answers to "where are the coefficients?", and the reader who takes the
        wrong one is reading a table that was not approved. Neither is a fidelity score with
        no table behind it — the approximation reported as good without saying what it was.
        """
        inline = bool(self.coefficients) or bool(self.relativities)
        if inline == (self.approximating_model_id is not None):
            raise ValueError(
                "a GLM approximation carries exactly one table: `approximating_model_id` "
                "naming the Model that holds it (FR-137), or the inline "
                "`coefficients`/`relativities` of an artifact written before 2026-08-19."
            )
        return self
```

Update the module docstring's second bullet, which currently says `approximating_model_id`
is "**not** populated" and cites OQ-577 as open. Replace it with what is now true,
dated, and keep the sentence about what the legacy artifacts hold.

- [ ] **Step 5: Run the schema tests to green**

```bash
uv run pytest packages/model-schema/tests/test_glm_approximation.py -q; echo "exit=$?"
```

Expected: `exit=0`, 6 passed.

- [ ] **Step 6: Bump `SPEC_HASH_VERSION` and its test**

`backend/src/app/platform/modelling.py:105` — `SPEC_HASH_VERSION: Final = 5`, and append to
the comment block above it, in the style of the `v4` line:

```python
#: `approximates_model_id` moved it `v4` to `v5` (2026-08-19, FR-137): the model a
#: surrogate approximates is part of what that surrogate is, and two approximations of two
#: different GBMs over one population would otherwise share a digest — which FR-204
#: answers by handing the second caller the first caller's model. Every `v4:` digest is
#: findable with `LIKE 'v4:%'` and reported stale by `spec_hash_is_current`.
```

`backend/tests/test_spec_hash.py:160` — update the assertion **and its message**, which is
the part that carries the reason:

```python
    assert SPEC_HASH_VERSION == 5, "approximates_model_id joined the payload; the tag moves with it"
```

- [ ] **Step 7: Regenerate the contracts**

```bash
uv run python scripts/generate-contracts.py; echo "exit=$?"
git diff --stat docs/contracts/
```

Expected: `exit=0`, and a diff touching `model-spec.schema.json`, `model.schema.json`,
`transparency-artifact.schema.json` and `openapi/generated.json`. **Never hand-edit these.**
Then confirm the check mode agrees:

```bash
uv run python scripts/generate-contracts.py --check; echo "exit=$?"
```

- [ ] **Step 8: Run the Python gate for this task**

```bash
uv run ruff check . ; echo "ruff=$?"
uv run mypy ; echo "mypy=$?"
uv run pytest packages/model-schema backend/tests/test_spec_hash.py -q ; echo "pytest=$?"
```

All three must print `0`. Read each command's own exit code — `cmd | tail -1 && echo ok`
reports `tail`'s and has produced a false clean here before.

- [ ] **Step 9: Commit**

```bash
git add packages/model-schema backend/src/app/platform/modelling.py \
        backend/tests/test_spec_hash.py docs/contracts
git commit -m "feat(schema): approximates_model_id and spec_hash v5 (FR-137, FR-141)"
```

---

### Task 3: `pricing-core` keeps the fitted surrogate

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/transparency.py:55-147`
- Modify: `packages/pricing-core/src/pricing_core/modelling/__init__.py` (exports)
- Modify: `packages/pricing-core/tests/test_transparency.py` (three call sites at lines
  ~50, ~71, ~170 and their assertions)

**Interfaces:**
- Consumes: `SURROGATE_RESPONSE_COLUMN` and `GlmSpec.approximates_model_id` from Task 2.
- Produces, both exported from `pricing_core.modelling`:
  - `approximation_spec(spec: GbmSpec, *, source_model_id: UUID) -> GlmSpec` — pure, so the
    platform can hash and reserve before spending a fit.
  - `GlmApproximationFit` — frozen dataclass with fields `spec: GlmSpec`,
    `result: GlmFitResult`, `r_squared: float`, `deviance_explained: float`,
    `worst_regions: tuple[WorstRegion, ...]`, `train: pl.DataFrame`,
    `holdout: pl.DataFrame`, and the method
    `artifact_block(approximating_model_id: UUID) -> GlmApproximation`.
  - `build_glm_approximation(result, booster, spec, factors, data, *, holdout,
    source_model_id, bandings=None, groupings=None, progress=None) -> GlmApproximationFit`.

  `train` and `holdout` are the caller's frames **with `SURROGATE_RESPONSE_COLUMN`
  appended** — the booster's predictions on each. Task 4 hands them straight to
  `compute_diagnostics`, which is what makes the surrogate's A/E an A/E against the source
  model's predictions on both partitions.

- [ ] **Step 1: Write the failing test for the new return shape**

Append to `packages/pricing-core/tests/test_transparency.py`:

```python
@pytest.mark.req("FR-137")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_approximation_returns_the_fit_that_produced_it(backend: str) -> None:
    """FR-137 persists the surrogate as a Model, so its fit result must survive.

    Before this it was fitted and thrown away, and the artifact kept a summary of a model
    nothing could reproduce.
    """
    data, spec, factors, fit = _fit(backend)
    source = new_uuid7()
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=source,
    )
    assert approximation.result.model_type == "glm"
    assert any(c.term == "intercept" for c in approximation.result.coefficients)
    assert approximation.result.relativities
    assert approximation.spec.approximates_model_id == source
    assert approximation.spec.response_column == SURROGATE_RESPONSE_COLUMN
    # The surrogate target travels with the frames, so the caller's diagnostics measure the
    # surrogate against the booster rather than against the observed response.
    assert SURROGATE_RESPONSE_COLUMN in approximation.train.columns
    assert SURROGATE_RESPONSE_COLUMN in approximation.holdout.columns


@pytest.mark.req("FR-137")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_artifact_block_names_the_model_and_carries_no_table(backend: str) -> None:
    """The table lives on the Model now; the block carries the measurements and the id."""
    data, spec, factors, fit = _fit(backend)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    model_id = new_uuid7()
    block = approximation.artifact_block(model_id)
    assert block.approximating_model_id == model_id
    assert block.coefficients == ()
    assert not block.relativities
    assert block.r_squared == approximation.r_squared
    assert block.worst_regions == approximation.worst_regions
```

Import `new_uuid7` and `SURROGATE_RESPONSE_COLUMN` from `model_schema` at the top of the
file. Passing `data` as its own holdout is deliberate here and **only** here: this test is
about the return shape, not about generalisation, and a second frame would add a fixture
that proves nothing extra. Task 4's tests use the real split.

- [ ] **Step 2: Run them and watch them fail**

```bash
uv run pytest packages/pricing-core/tests/test_transparency.py -q -k "returns_the_fit or artifact_block"; echo "exit=$?"
```

Expected: `TypeError: build_glm_approximation() got an unexpected keyword argument
'holdout'`.

- [ ] **Step 3: Extract the spec into a pure function**

In `transparency.py`, above `build_glm_approximation`:

```python
def approximation_spec(spec: GbmSpec, *, source_model_id: UUID) -> GlmSpec:
    """The specification of the GLM that approximates `spec`'s model (FR-MODEL-34, 96).

    Pure, and separate from the fit, because the platform reserves the Model this describes
    **before** it spends a fit on it: `spec_hash` is taken over this object, and a surrogate
    that already exists must be recognised rather than fitted twice (FR-204).

    The approximating spec mirrors the GBM's structure — same factors, same offset, same
    split — and differs only in what it is fitted *to*. Anything else would make the
    comparison between them a comparison of two different questions.
    """
    return GlmSpec(
        model_family_slug=f"{spec.model_family_slug}-approx",
        dataset_version_id=spec.dataset_version_id,
        split_ref=spec.split_ref,
        response_column=SURROGATE_RESPONSE_COLUMN,
        approximates_model_id=source_model_id,
        offset=spec.offset,
        weight=spec.weight,
        factors=spec.factors,
        family="gamma",
        link="log",
        seed=spec.seed,
    )
```

`family="gamma"`, `link="log"`: the target is a strictly positive mean, and a Gaussian
approximation to a multiplicative structure understates the fit exactly where the
predictions are largest. That reasoning is already in the docstring below — leave it there
rather than copying it.

- [ ] **Step 4: Add the result dataclass**

```python
@dataclass(frozen=True)
class GlmApproximationFit:
    """What an approximation produces: the measurements, and the model behind them.

    Two halves rather than one because FR-137 made the surrogate a Model. The
    `GlmApproximation` block is a summary and the platform gives it an identity, so it is
    built by `artifact_block` once the Model is reserved — this class cannot construct it,
    because a block with neither a model reference nor an inline table is refused at the
    type, and rightly.

    `train` and `holdout` carry the booster's predictions in
    `SURROGATE_RESPONSE_COLUMN`. They are returned rather than recomputed by the caller for
    the reason `GbmFit` returns its bytes: the scoring pass has already happened, and a
    second one is a second answer.
    """

    spec: GlmSpec
    result: GlmFitResult
    r_squared: float
    deviance_explained: float
    worst_regions: tuple[WorstRegion, ...]
    train: pl.DataFrame
    holdout: pl.DataFrame

    def artifact_block(self, approximating_model_id: UUID) -> GlmApproximation:
        """`02` §4.9's block, once the platform has reserved the Model that holds the table."""
        return GlmApproximation(
            approximating_model_id=approximating_model_id,
            r_squared=self.r_squared,
            deviance_explained=self.deviance_explained,
            worst_regions=self.worst_regions,
        )
```

Add `from dataclasses import dataclass` and the `GlmFitResult`, `GlmSpec`,
`SURROGATE_RESPONSE_COLUMN` imports to the module's existing `model_schema` import block.

- [ ] **Step 5: Rework `build_glm_approximation`**

Signature becomes:

```python
def build_glm_approximation(
    result: GbmFitResult,
    booster: bytes,
    spec: GbmSpec,
    factors: Sequence[Factor],
    data: pl.DataFrame,
    *,
    holdout: pl.DataFrame,
    source_model_id: UUID,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    progress: ProgressCallback | None = None,
) -> GlmApproximationFit:
```

Inside, four changes and nothing else:

1. Replace the inline `approximation_spec = GlmSpec(...)` block with
   `approximation_spec_ = approximation_spec(spec, source_model_id=source_model_id)` and
   use `SURROGATE_RESPONSE_COLUMN` in place of the local `surrogate_column`.
2. Score the holdout too, and refuse a non-positive prediction on either frame with the
   existing `APPROXIMATION_TARGET_NOT_POSITIVE` — the same error, raised for the same
   reason, on whichever frame produced it:

```python
    frames: dict[str, pl.DataFrame] = {}
    for name, frame in (("train", data), ("holdout", holdout)):
        target = predict_gbm(
            result, booster, frame, factors, bandings=bandings, groupings=groupings
        ).to_numpy()
        if np.any(target <= 0):
            raise GbmFitError(
                "APPROXIMATION_TARGET_NOT_POSITIVE",
                f"the booster predicts a non-positive value on the {name} partition, "
                "which a Gamma approximation cannot take as a response (FR-133).",
            )
        frames[name] = frame.with_columns(pl.Series(SURROGATE_RESPONSE_COLUMN, target))
```

   The fit, the R², the deviance and the worst regions all continue to use the **train**
   frame: `02` §3.6 approximates the population the model was fitted on, and approximating
   the holdout would report how well a surrogate generalises, which is a different question.
3. Keep `.result` and keep dropping the covariance bytes, and say why in the comment that
   is already there — now with the extra sentence that matters:

```python
    # `.result` and not the covariance bytes beside it: the surrogate is a *description* of
    # the booster, and FR-194's interval belongs to the model that priced the row, not
    # to an approximation of it. The platform strips `covariance_blob` from the result
    # before persisting it (FR-141), so the reference cannot resolve to bytes nobody
    # stored.
```
4. Return `GlmApproximationFit(...)` instead of `GlmApproximation(...)`.

- [ ] **Step 6: Update the three existing call sites**

`test_the_approximation_is_fitted_to_the_boosters_predictions`,
`test_the_worst_regions_name_a_cell_and_its_share_of_the_book` and
`test_the_fidelity_statement_says_where_the_approximation_fails` all call the old
signature. Each gains `holdout=data, source_model_id=new_uuid7()`. The first one's two
table assertions move to where the table now is, and its comment moves with them:

```python
    # It is a rateable table or it is not an approximation (FR-133) — and from
    # FR-137 the table is the surrogate Model's fit result.
    assert approximation.result.relativities
    assert any(c.term == "intercept" for c in approximation.result.coefficients)
```

`fidelity_statement(approximation, summary)` takes a `GlmApproximation`, so that call site
becomes `fidelity_statement(approximation.artifact_block(new_uuid7()), summary)`. Its
signature does not change: `transparency.py:316-355` reads only `r_squared`,
`deviance_explained`, `worst_regions` and the summary — verified while planning — and all
three survive on the block.

- [ ] **Step 7: Export and run**

Add `approximation_spec` and `GlmApproximationFit` to `transparency.py`'s `__all__`, to
`pricing_core/modelling/__init__.py`'s import list and to its `__all__`.

```bash
uv run pytest packages/pricing-core/tests/test_transparency.py -q; echo "exit=$?"
uv run ruff check . ; echo "ruff=$?"
uv run mypy ; echo "mypy=$?"
uv run lint-imports ; echo "imports=$?"
```

All four `0`. `lint-imports` matters here: `pricing-core` must not have acquired an import
of anything the contracts forbid.

- [ ] **Step 8: Commit**

```bash
git add packages/pricing-core
git commit -m "feat(model): pricing-core returns the fitted surrogate (FR-137)"
```

---

### Task 4: The Job persists the surrogate and the artifact references it

**Files:**
- Modify: `backend/src/app/worker/model_handlers.py:634-752` (`_transparency`)
- Create: `backend/tests/test_glm_approximation_model.py`

**Interfaces:**
- Consumes: `approximation_spec`, `GlmApproximationFit`, `build_glm_approximation` (Task 3);
  `SURROGATE_RESPONSE_COLUMN` (Task 2); `model_service.reserve_model` and
  `model_service.record_fit` as they already are.
- Produces: a `model.transparency` Job that leaves behind a fitted Model whose
  `spec.approximates_model_id` is the GBM, and a `TransparencyArtifact` whose
  `glm_approximation.approximating_model_id` is that Model.

**The transaction shape, which is the part to get right.** One `unit_of_work` holds the
reserve, the fit and the artifact write, so a failed compute leaves nothing and the
artifact never commits without the Model it names. **Never open a second `unit_of_work`
inside it** — an inner one takes a second connection and deadlocks against the pool with no
output and no traceback.

- [ ] **Step 1: Write the failing end-to-end test**

Create `backend/tests/test_glm_approximation_model.py`. Reuse `test_model_jobs_gbm.py`'s
fixtures — read `_fitted_gbm` and `_actuary` there first and import them rather than
writing a second GBM fixture:

```python
"""FR-137 — the GLM approximation of a GBM, persisted as a Model.

The artifact used to carry the table inline, which made it the only thing that could ever
rate on the approximation — and a `TransparencyArtifact` has no status, so FR-20's pin
could never resolve to one (`03` FR-223). These tests are about the Model that fixes
that: it exists, it is fitted, its diagnostics are against the booster's predictions rather
than against observed claims, and rebuilding the artifact does not fit it a second time.
"""

from __future__ import annotations

import pytest

from app.platform import modelling as model_service
from app.platform import transparency as transparency_service
from model_schema import MODEL_SPEC_ADAPTER, JobKind, JobStatus, ModelStatus, SURROGATE_RESPONSE_COLUMN

from tests.test_model_jobs_gbm import _actuary, _fitted_gbm   # confirm the real names first


async def _transparency_job(database, blob_store, workspace_id, model_id, actor):
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.MODEL_TRANSPARENCY,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id), "sample": 2_000},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        return await transparency_service.load_transparency(
            session, workspace_id=workspace_id, model_id=model_id
        )


@pytest.mark.req("FR-137")
async def test_the_artifact_names_a_fitted_model_that_holds_the_table(
    database, blob_store, workspace_id
) -> None:
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED
    actor = await _actuary(database, workspace_id)

    artifact = await _transparency_job(database, blob_store, workspace_id, model_id, actor)

    assert artifact.glm_approximation is not None
    surrogate_id = artifact.glm_approximation.approximating_model_id
    assert surrogate_id is not None
    # The table moved; it did not get copied.
    assert artifact.glm_approximation.coefficients == ()

    async with database.session() as session:
        surrogate = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
    assert surrogate.status == ModelStatus.FITTED.value
    assert surrogate.diagnostics_id is not None
    spec = MODEL_SPEC_ADAPTER.validate_python(surrogate.spec)
    assert spec.approximates_model_id == model_id
    assert spec.response_column == SURROGATE_RESPONSE_COLUMN
    assert surrogate.fit_result is not None
    assert surrogate.fit_result["coefficients"]


@pytest.mark.req("FR-141")
async def test_the_surrogate_carries_no_covariance_blob(
    database, blob_store, workspace_id
) -> None:
    """An interval from a surrogate's coefficients describes the surrogate, and would be
    read as the GBM's uncertainty — which FR-198 refuses by name."""
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    artifact = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    surrogate_id = artifact.glm_approximation.approximating_model_id

    async with database.session() as session:
        surrogate = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
    assert surrogate.fit_result["covariance_blob"] is None


@pytest.mark.req("FR-137")
async def test_rebuilding_the_artifact_reuses_the_surrogate_rather_than_refitting_it(
    database, blob_store, workspace_id
) -> None:
    """FR-204: the specification is the same, so the model is the same one.

    Without this the second build raises `MODEL_IMMUTABLE` against a model it just found,
    and the Job fails on its own success.
    """
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)

    first = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    second = await _transparency_job(database, blob_store, workspace_id, model_id, actor)

    assert second.id != first.id, "each build appends an artifact (FR-132)"
    assert (second.glm_approximation.approximating_model_id
            == first.glm_approximation.approximating_model_id)


@pytest.mark.req("FR-137")
async def test_the_surrogates_diagnostics_measure_it_against_the_booster(
    database, blob_store, workspace_id
) -> None:
    """FR-137(iii). The A/E is the surrogate against the source model's predictions —
    so it is close to 1 by construction on a well-fitting approximation, and the *spec* is
    what says which target that is (FR-141)."""
    from app.platform import diagnostics as diagnostics_service

    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    artifact = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    surrogate_id = artifact.glm_approximation.approximating_model_id

    async with database.session() as session:
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
    assert diagnostics.universal.train.rows > 0
    assert diagnostics.universal.holdout.rows > 0
    assert diagnostics.glm is not None
    assert 0.5 < diagnostics.universal.train.ae_overall < 1.5
```

Check the real names of `_fitted_gbm`, `_actuary`, `execute_job`, `job_service` and the
`diagnostics` service module in `backend/tests/test_model_jobs_gbm.py` and adjust the
imports; the fixtures `database`, `blob_store`, `workspace_id` come from
`backend/tests/conftest.py`.

- [ ] **Step 2: Run them and watch them fail**

```bash
uv run pytest backend/tests/test_glm_approximation_model.py -q; echo "exit=$?"
```

Expected: `AssertionError` on `approximating_model_id is not None` — the handler still
builds the old block. If instead every test **skips**, `GIP_TEST_DATABASE_URL` is not
exported and nothing has been proven.

- [ ] **Step 3: Take the holdout in the handler's `load()`**

In `_transparency`, `load()` returns the train frame today. Refuse a spec with no split
before anything is loaded — a fitted GBM always has one, and a fitted GBM that does not is
a model this Job cannot produce evidence for:

```python
            if spec.split_ref is None:
                raise PlatformError(
                    "MODEL_SPLIT_REQUIRED",
                    "This model spec declares no split",
                    422,
                    "The approximation is a Model in its own right (FR-137), and "
                    "FR-183 makes a diagnostic reported without its holdout "
                    "counterpart a defect. Without a split there is no holdout to report.",
                )
            train, holdout = await _split_frames(
                session, blob_store, workspace_id=workspace_id, spec=spec, parent=parent
            )
```

and widen the return type to carry `holdout` beside `train`.

- [ ] **Step 4: Refuse a surrogate slug the column cannot hold**

`models.model_family_slug` is `String(64)` and this Job generates a slug seven characters
longer than the one the analyst chose. Before reserving:

```python
    surrogate_spec = approximation_spec(spec, source_model_id=model_id)
    if len(surrogate_spec.model_family_slug) > 64:
        raise PlatformError(
            "VALIDATION_FAILED",
            "The approximating model's slug is too long",
            422,
            f"{spec.model_family_slug!r} plus the '-approx' suffix is "
            f"{len(surrogate_spec.model_family_slug)} characters, and a model family slug "
            "is 64. Rename the model family, or the approximation FR-137 requires "
            "cannot be stored.",
        )
```

A refusal naming the cause, rather than a `DataError` from the driver naming a column.

- [ ] **Step 5: Fit the surrogate, and its diagnostics, on both partitions**

Replace the `build_glm_approximation(...)` call and add the diagnostics pass. The progress
budget moves: the approximation now scores two frames and computes diagnostics, so SHAP
starts later.

```python
    progress.update(0.20, "fitting the GLM approximation")
    approximation = build_glm_approximation(
        result, booster, spec, factors, frame,
        holdout=holdout,
        source_model_id=model_id,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.20, end=0.50),
    )
    progress.update(0.50, "diagnostics of the approximation")
    # FR-137(iii): the surrogate reaches `fitted` on diagnostics of itself against the
    # source model's predictions — FR-136's quantity, on both partitions. The frames
    # carry the booster's predictions in `SURROGATE_RESPONSE_COLUMN`, so this is the
    # ordinary GLM diagnostics path measuring an extraordinary target, and FR-141's
    # spec invariant is what says so to every later reader.
    surrogate_diagnostics = compute_diagnostics(
        approximation.result, approximation.spec, factors,
        train=approximation.train, holdout=approximation.holdout,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.50, end=0.62),
    )
    progress.update(0.62, "tree shap")
    summary = build_shap_summary(
        result, booster, spec, factors, frame,
        sample=sample,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.62, end=0.90),
    )
```

Import `compute_diagnostics` and `approximation_spec` from `pricing_core.modelling` in the
same local import block the handler already uses.

- [ ] **Step 6: Reserve, fit and reference — one transaction**

Replace `store()`:

```python
    async def store() -> UUID:
        async with progress.database.unit_of_work() as session:
            # FR-174's monotonicity check, carried up to the artifact R3 reads. Taken
            # from the diagnostics rather than recomputed: the diagnostics swept the factors
            # at fit time, and a second sweep here could disagree with the evidence the
            # model was approved against.
            diagnostics = await diagnostics_service.load_diagnostics(
                session, workspace_id=workspace_id, model_id=model_id
            )
            checks = diagnostics.gbm.monotonicity if diagnostics.gbm else ()

            # FR-137. Reserved rather than created: `spec_hash` makes a rebuilt
            # artifact find the surrogate it already fitted (FR-204), and calling
            # `record_fit` on it a second time would raise `MODEL_IMMUTABLE` and fail a Job
            # that had done nothing wrong.
            surrogate, should_fit = await model_service.reserve_model(
                session,
                workspace_id=workspace_id,
                actor=actor,
                spec=approximation.spec,
                change_reason=(
                    f"glm approximation of {source.model_family_slug}@{source.version} "
                    "(FR-133)"
                ),
            )
            if should_fit:
                await model_service.record_fit(
                    session,
                    workspace_id=workspace_id,
                    actor=actor,
                    model_id=surrogate.id,
                    # The covariance reference is dropped, not stored: the bytes were never
                    # kept, and FR-194's interval belongs to the model that priced the
                    # row rather than to a description of it (FR-141).
                    fit_result=approximation.result.model_copy(
                        update={"covariance_blob": None}
                    ),
                    diagnostics=Diagnostics(
                        id=new_uuid7(),
                        model_id=surrogate.id,
                        computed_at=datetime.now(UTC),
                        job_id=job_id,
                        universal=surrogate_diagnostics.universal,
                        complexity=surrogate_diagnostics.complexity,
                        glm=surrogate_diagnostics.glm,
                    ),
                    job_id=job_id,
                )

            artifact = TransparencyArtifact(
                id=new_uuid7(),
                model_id=model_id,
                created_at=datetime.now(UTC),
                job_id=job_id,
                glm_approximation=approximation.artifact_block(surrogate.id),
                shap_summary=summary,
                fidelity_statement=fidelity_statement(
                    approximation.artifact_block(surrogate.id), summary
                ),
                monotonicity_verified=(
                    all(check.holds for check in checks) if checks else None
                ),
            )
            row = await transparency_service.record_transparency(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                artifact=artifact,
                job_id=job_id,
            )
            return row.id
```

`job_id` is already computed twice in the current body as
`UUID(parameters["job_id"]) if parameters.get("job_id") else None` — bind it once above
`store()` and use it in all three places. `source` is the `ModelRow` that `load()` fetched
via `fitted_gbm_or_refuse`; return its `model_family_slug` and `version` from `load()`
rather than re-reading the row in a second session.

- [ ] **Step 7: Run the new tests to green, then the whole backend model suite**

```bash
uv run pytest backend/tests/test_glm_approximation_model.py -q; echo "exit=$?"
uv run pytest backend/tests/test_model_jobs_gbm.py backend/tests/test_wf01_journey.py \
              backend/tests/test_approvals.py backend/tests/test_artifact_immutability.py -q; echo "exit=$?"
```

Both `0`. The second command is the one that catches a fixture elsewhere that built a
`TransparencyArtifact` by hand.

- [ ] **Step 8: Prove the enforcement fails on broken input**

Not optional (`CLAUDE.md` §13.4) — a check nobody has seen fail is a check nobody has seen.
Do each, confirm the expected test reddens, then restore:

1. Make `store()` call `record_fit` unconditionally (drop the `if should_fit`) →
   `test_rebuilding_the_artifact_reuses_the_surrogate_rather_than_refitting_it` must fail
   with `MODEL_IMMUTABLE`.
2. Pass `train=approximation.train, holdout=approximation.train` to `compute_diagnostics` →
   nothing should fail, which is the honest result: **record that it does not**, because it
   means no test distinguishes the holdout partition here, and add one if the reviewer
   judges it worth it.
3. Drop the `model_copy(update={"covariance_blob": None})` →
   `test_the_surrogate_carries_no_covariance_blob` must fail.

`git checkout -- <file>` between each. A broken edit that fails to *parse* proves only that
broken Python does not run — check the diff before running.

- [ ] **Step 9: Commit**

```bash
git add backend/src/app/worker/model_handlers.py backend/tests/test_glm_approximation_model.py
git commit -m "feat(model): the transparency Job persists the approximating Model (FR-137)"
```

---

### Task 5: A hand-written surrogate spec is refused

**Files:**
- Modify: `backend/src/app/errors.py:174` area (register `MODEL_APPROXIMATION_INVALID` in
  `MODELLING_ERROR_CODES`)
- Modify: `backend/src/app/platform/modelling.py` (`_refuse_mismatched_approximation`,
  called from `reserve_model`)
- Modify: `backend/src/app/platform/model_specs.py:228` (`validate_spec`'s
  `RESPONSE_MISSING` check)
- Modify: `backend/tests/test_model_specs.py` (one new test)
- Modify: `backend/tests/test_glm_approximation_model.py` (the refusals)

**Why this is its own task.** `POST /api/v1/models` reserves from any spec a caller sends,
so from Task 2 onward a caller can hand-write `approximates_model_id` pointing at a model
that is not fitted, is itself a GLM, or was fitted on another dataset version. The type
cannot catch it — the type has no database — and the artifact that results would be a
surrogate of a model it does not describe. This is `_refuse_mismatched_interval_model`'s
problem again, and it gets the same answer.

**Interfaces:**
- Consumes: `GlmSpec.approximates_model_id` (Task 2), the error code declared in Task 1.
- Produces: `MODEL_APPROXIMATION_INVALID`, raised from `reserve_model` before a Job exists.

- [ ] **Step 1: Write the failing refusal tests**

Append to `backend/tests/test_glm_approximation_model.py`. Build the surrogate spec with
`approximation_spec(...)` and then break one thing at a time — a hand-built spec would test
this plan's idea of a surrogate rather than the one the platform produces:

```python
@pytest.mark.req("FR-137")
async def test_a_surrogate_of_a_model_that_does_not_exist_is_a_404(
    database, blob_store, workspace_id
) -> None:
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    async with database.session() as session:
        source = MODEL_SPEC_ADAPTER.validate_python(
            (await model_service.load_model_by_id(
                session, workspace_id=workspace_id, model_id=model_id)).spec
        )
    spec = approximation_spec(source, source_model_id=new_uuid7())

    with pytest.raises(PlatformError) as caught:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor, spec=spec
            )
    assert caught.value.status == 404


@pytest.mark.req("FR-137")
async def test_a_surrogate_of_a_glm_is_refused(
    database, blob_store, workspace_id
) -> None:
    """FR-132 applies to non-GLM models: a GLM approximating a GLM reports 100 %
    fidelity, which looks like evidence and is not — the refusal `fitted_gbm_or_refuse`
    already makes at the endpoint, now made where a spec can arrive without one."""
    ...


@pytest.mark.req("FR-137")
async def test_a_surrogate_on_a_different_dataset_version_is_refused(
    database, blob_store, workspace_id
) -> None:
    """An approximation fitted over a different population describes a different model, and
    renders identically to a correct one."""
    ...
    assert caught.value.code == "MODEL_APPROXIMATION_INVALID"
```

Fill the two elided bodies against `test_paired_quantile_models.py:200-240`, which is the
same shape against `interval_for`: build a fitted GLM in the workspace for the first, and
`spec.model_copy(update={"dataset_version_id": <another validated version>})` for the
second. **Do not** copy the assertions blind — the codes and statuses differ.

- [ ] **Step 2: Run them and watch them fail**

```bash
uv run pytest backend/tests/test_glm_approximation_model.py -q -k "does_not_exist or of_a_glm or different_dataset"; echo "exit=$?"
```

Expected: `DID NOT RAISE` on all three — `reserve_model` accepts them today.

- [ ] **Step 3: Register the error code**

In `backend/src/app/errors.py`, add to `MODELLING_ERROR_CODES` beside
`MODEL_INTERVAL_PAIR_INVALID`:

```python
        # FR-137, 2026-08-19. The surrogate the transparency Job reserves is an
        # ordinary Model, so `POST /api/v1/models` can be handed a spec claiming to
        # approximate anything at all.
        "MODEL_APPROXIMATION_INVALID",
```

`backend/tests/test_errors.py:109` asserts every code `02` §5.1 declares is constructible,
so Task 1's spec edit and this registration must both land or that test goes red.

- [ ] **Step 4: Add the refusal**

In `backend/src/app/platform/modelling.py`, beside `_refuse_mismatched_interval_model`:

```python
async def _refuse_mismatched_approximation(
    session: AsyncSession, *, workspace_id: UUID, spec: ModelSpec
) -> None:
    """FR-137's rules for what a surrogate may approximate, before a Job exists.

    The type already refuses a spec that claims to be a surrogate while pointing at an
    observed response column (FR-141). What the type cannot see is the *other* model:
    whether it exists, whether it has predictions to approximate, and whether it was fitted
    over the same population. An approximation of a model it does not describe fits without
    complaint and renders identically to a correct one.
    """
    if not isinstance(spec, GlmSpec) or spec.approximates_model_id is None:
        return

    source = await session.get(ModelRow, spec.approximates_model_id)
    if source is None or source.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "The model this approximates does not exist",
            404,
            f"approximates_model_id names model {spec.approximates_model_id}, which is "
            "not a model in this workspace.",
        )
    if source.fit_result is None:
        raise PlatformError(
            "MODEL_APPROXIMATION_INVALID",
            "The model this approximates has no fit to approximate",
            409,
            f"{source.model_family_slug}@{source.version} is at "
            f"{source.status!r} and has no predictions. FR-133 fits the surrogate to "
            "the model's own predictions, and a model at `draft` has none.",
        )

    source_spec = MODEL_SPEC_ADAPTER.validate_python(source.spec)
    if source_spec.model_type == "glm":
        raise PlatformError(
            "MODEL_APPROXIMATION_INVALID",
            "A GLM needs no approximation",
            409,
            f"{source.model_family_slug}@{source.version} is a GLM. FR-132 applies to "
            "non-GLM models: approximating a GLM with another GLM reports 100 % fidelity, "
            "which looks like evidence and is not.",
        )

    mismatches = [
        field
        for field, mine, theirs in (
            ("dataset_version_id", spec.dataset_version_id, source_spec.dataset_version_id),
            ("split_ref", spec.split_ref, source_spec.split_ref),
            ("factors", set(spec.factors), set(source_spec.factors)),
        )
        if mine != theirs
    ]
    if mismatches:
        raise PlatformError(
            "MODEL_APPROXIMATION_INVALID",
            "This approximation does not match the model it approximates",
            409,
            f"approximates_model_id names {source.model_family_slug}@{source.version}, but "
            f"the two specifications disagree on {', '.join(mismatches)} (FR-137). An "
            "approximation fitted over a different population or design describes a "
            "different model, and renders identically to a correct one.",
        )
```

Set comparison on `factors` for `_refuse_mismatched_interval_model`'s reason: two specs
listing the same factors in a different order describe the same design matrix.

Call it from `reserve_model`, immediately after the `interval_for` check and **before**
`_refuse_unusable_factors` — for the same reason the interval check sits there, spelled out
in the comment already above it: a surrogate naming the wrong source model usually also
fails factor resolution, and the factor error sends the caller to re-check factors that
were never wrong.

- [ ] **Step 5: Stop `validate_spec` calling a surrogate's response column missing**

`backend/src/app/platform/model_specs.py:228`:

```python
    # A surrogate's response is another model's prediction, not a column the version has
    # (FR-137, FR-141). Reporting it missing would tell an analyst their
    # approximation was broken because it is an approximation.
    surrogate = isinstance(spec, GlmSpec) and spec.approximates_model_id is not None
    if columns and not surrogate and spec.response_column not in columns:
```

- [ ] **Step 6: Test that carve-out where the spec validator's tests live**

Append to `backend/tests/test_model_specs.py`, matching the file's existing helper style:

```python
@pytest.mark.req("FR-141")
async def test_a_surrogate_spec_is_not_reported_as_missing_its_response(...) -> None:
    """`__gbm_prediction__` is not in any dataset version, and never will be."""
    validation = await _validate(_surrogate_spec())
    assert not [p for p in validation.problems if p.kind is SpecProblemKind.RESPONSE_MISSING]


@pytest.mark.req("FR-141")
async def test_an_ordinary_spec_still_reports_a_response_column_it_does_not_have(...) -> None:
    """The carve-out is for surrogates only — the check it relaxes is the one that catches
    a typo in a response column, and losing it wholesale would be a worse defect than the
    one it fixes."""
    validation = await _validate(_spec(response_column="claims_kount"))
    assert [p for p in validation.problems if p.kind is SpecProblemKind.RESPONSE_MISSING]
```

The second test is the one that matters: a carve-out with no counterpart test is how a
check quietly stops applying to everything.

- [ ] **Step 7: Run to green**

```bash
uv run pytest backend/tests/test_glm_approximation_model.py backend/tests/test_model_specs.py \
              backend/tests/test_errors.py -q; echo "exit=$?"
```

- [ ] **Step 8: Prove the refusal fails on broken input**

Comment out the `_refuse_mismatched_approximation` call in `reserve_model`. The three
refusal tests must redden. Restore with `git checkout --`, and re-run to confirm green.

- [ ] **Step 9: Commit**

```bash
git add backend/src/app/errors.py backend/src/app/platform/modelling.py \
        backend/src/app/platform/model_specs.py backend/tests
git commit -m "feat(model): refuse a surrogate that does not match its source (FR-137)"
```

---

### Task 6: The gate, the measurement, and the roadmap record

**Files:**
- Modify: `docs/roadmap.md` (WK-661's slice record and its slice count)
- Modify: `CLAUDE.md` §2's layout marks **only if** a directory changed state — it did not,
  so expect no edit and say so rather than inventing one

**Interfaces:**
- Consumes: everything above.
- Produces: a branch a reviewer can read, with numbers rather than adjectives.

- [ ] **Step 1: Run the whole Python and docs gate, reading each exit code**

```bash
cd /home/puzhenhao1989/gi-pricing-plan
uv run ruff check . ; echo "ruff=$?"
uv run mypy ; echo "mypy=$?"
uv run lint-imports ; echo "imports=$?"
uv run pytest -q ; echo "pytest=$?"
python3 scripts/audit-docs.py ; echo "audit=$?"
uv run python scripts/req-coverage.py ; echo "req=$?"
uv run python scripts/generate-contracts.py --check ; echo "contracts=$?"
uv run pytest backend/tests/test_demo_guide.py ; echo "demo=$?"
```

Every one `0`. Expected movement: requirements 482 → **483**; marked requirements up by the
number of distinct ids the new markers name; contracts **21**, all matching. `pytest -q`
must report **zero skipped** — a skipped backend test means the DSN is not exported and the
run proves nothing about anything in Tasks 4 or 5.

- [ ] **Step 2: Run the frontend half**

The generated client changes because the schemas did, and nothing under `frontend/src`
should need an edit — the model-detail view that would read these fields is WK-664's.

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
rm -rf frontend/node_modules
pnpm --dir frontend install --frozen-lockfile ; echo "install=$?"
pnpm --dir frontend generate:api ; echo "api=$?"
pnpm --dir frontend lint ; echo "lint=$?"
pnpm --dir frontend type-check ; echo "types=$?"
pnpm --dir frontend test ; echo "test=$?"
pnpm --dir frontend build ; echo "build=$?"
```

A clean `node_modules` is what CI does, and a populated one hides a missing dependency.

- [ ] **Step 3: Measure what this slice added to the Job, and record the number**

The transparency Job now scores a second frame and computes a full GLM diagnostics pass
(including type-III tests, which refit the surrogate once per factor). That is a real cost
and `CLAUDE.md` §13.5 wants it measured rather than asserted:

```bash
uv run pytest backend/tests/test_glm_approximation_model.py -q --durations=5
```

Record the slowest test's wall time in the commit body beside the same figure from `main`
(`git stash`, run `test_model_jobs_gbm.py::test_a_transparency_artifact_is_built_and_read_back
--durations=5`, `git stash pop`). If the diagnostics pass dominates, say so and note
`type_iii=False` as the lever a later slice can pull — do **not** pull it here without the
maintainer, because FR-172 makes type-III tests part of what GLM diagnostics *are*.

- [ ] **Step 4: Write the roadmap slice record**

In `docs/roadmap.md`, WK-661's row lists its slices and a count. Add this one, and correct the
count in the same edit — the paired-quantile slice had to correct it once already because a
previous slice was omitted:

```markdown
the GLM approximation as a Model (FR-137, FR-141)
```

Then re-read the whole WK-661 row for claims this slice falsified. **Search the file for every
sentence saying the approximation is carried inline or that OQ-577 is unbuilt** —
`grep -n "approximating_model_id\|OQ-577\|inline" docs/roadmap.md` — and fix each. The
PSI slice found two stale mentions beyond the two its brief named, in one file.

- [ ] **Step 5: Update the skill if this slice taught one**

`CLAUDE.md` §12: a non-obvious procedure discovered here belongs in `.claude/skills/`,
committed with the work. Two candidates to judge, not to assume:
`python-package` (a Pydantic iff-validator across two fields, and why `model_copy` bypasses
validation — which is why Task 3 builds the block through a method rather than copying one)
and `python-test` (proving a `should_fit`-style idempotency branch by making it
unconditional). Add only what a future reader could not derive from the code.

- [ ] **Step 6: Commit and report**

```bash
git add docs/roadmap.md .claude/skills
git commit -m "docs(roadmap): the GLM approximation as a Model — WK-661 slice record"
git log --oneline main..HEAD
git status --short
```

Report to the maintainer: the six commits, the gate numbers from Steps 1 and 2 as printed,
the measurement from Step 3, and the decision-gate answer the branch was built on. **Do not
push or open a PR** unless asked — the branch's ending is the maintainer's.

---

## Self-review

**Spec coverage.** FR-137's three obligations map to tasks: (i) `approximates_model_id`
on the approximating Model's spec — Task 2 Step 3, with the surrogate spec built in Task 3
Step 3 and its `dataset_version_id` inherited from the GBM; (ii) the field joins the
`spec_hash` payload and `n` increments — Task 2 Step 6; (iii) §4.8's
`status ≥ fitted ⟹ diagnostics_id` met by diagnostics of the surrogate against the source
model's predictions — Task 4 Steps 5 and 6, tested in Task 4 Step 1. The sentence "stops
carrying its coefficients inline" is Task 2 Step 4 under decision-gate option A. The
requirement's deadline — "before anything references a transparency artifact by identifier"
— is checked in Task 1 Step 8's outcome note.

**Placeholders.** Two elided test bodies in Task 5 Step 1 are marked `...` **with the file
and line range to write them from** and an explicit instruction not to copy the assertions
blind; every other step carries the code it asks for. Task 6 Step 4's roadmap sentence is
one line because the row's exact wording must be read before it is extended.

**Type consistency.** `SURROGATE_RESPONSE_COLUMN` (Task 2) is used by name in Tasks 3, 4 and
5. `GlmApproximationFit`'s field names — `spec`, `result`, `r_squared`,
`deviance_explained`, `worst_regions`, `train`, `holdout` — are the ones Task 4 Steps 5 and
6 read. `approximation_spec(spec, *, source_model_id=...)` is called with that keyword in
Tasks 4 and 5. `artifact_block(model_id)` returns the `GlmApproximation` that
`fidelity_statement` takes.

**What this plan has not verified, and the implementer will hit first.** The test helpers
Task 4 imports from `backend/tests/test_model_jobs_gbm.py` (`_fitted_gbm`, `_actuary`,
`execute_job`, `job_service`) were read as names in a grep, not as signatures — check them
before writing the file, and prefer importing over re-creating a second GBM fixture.
`test_model_specs.py`'s helper style in Task 5 Step 6 is likewise sketched from the file's
shape rather than its body.
