# W32-4 — The EBM predict arm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `POST /api/v1/models/{model_id}/predict` score an EBM instead of refusing it,
by routing the EBM arm to the `predict_ebm` that `pricing-core` has had since 2026-08-21 —
and give the response a typed reason for having no interval, because an EBM has no
covariance matrix and no quantile pair and the existing four reasons all say something that
is not true of it.

**Architecture:** The maths already exists and is already dispatched — `score_fitted` in
`packages/pricing-core/src/pricing_core/modelling/predict.py:406` routes an `EbmFitResult`
to `predict_ebm` at `:449`. What is missing is one arm in the backend service, one widened
`Literal`, and one new `UnavailableReason` member. No new file in `pricing-core`, no new
endpoint, no frontend work at all — `grep -rn -i "ebm" frontend/src` returns nothing.

**Tech Stack:** Python 3.12, Pydantic v2, FastAPI, Polars, NumPy, pytest.
`scripts/generate-contracts.py` regenerates the committed contract; CI fails on drift
(FR-PLAT-48).

**Spec:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) — FR-MODEL-37 (EBM is transparent
  by construction), FR-MODEL-62 (the predict endpoint), FR-MODEL-77 and FR-MODEL-93
  (the typed-absence vocabulary this slice extends), FR-MODEL-100 (what its members mean),
  §5.2's `predict.py` block at lines 2185–2205.
- [`../roadmap.md`](../roadmap.md) — lines 704–713 and 3311, where the refusal was recorded
  when it was written, and where ownership is still attributed to W6b.
- [`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) — where this slice sits.
- [`../adr/`](../adr/) — ADR-0001 (`pricing-core` stays dependency-free, which is why the
  blob fetch lives in the backend) and ADR-0003 (declarative artifacts, which is why an
  EBM's exported tables *are* the model).

---

## Global Constraints

Copied from [`../../CLAUDE.md`](../../CLAUDE.md). Every task's requirements implicitly
include this section.

- **`model-schema` is the single source of truth for shared shapes** (§2, ADR-0002).
  `Prediction.model_type` is a `Literal` in `model-schema`; the OpenAPI enum and the
  frontend's generated type both descend from it. Never widen the enum in the contract.
- **Requirement IDs are permanent** (§5): append, never renumber. This slice appends exactly
  one requirement to `02` §3. Highest ids in use: FR-MODEL-123, NFR-MODEL-14.
  Next free: `FR-MODEL-124` — and this plan takes it; the W32-5 plan takes `FR-MODEL-125`.
  The two were written on the same day and must not both reach for the same number.
- **When code and spec disagree, resolve it — do not quietly change one to match the other**
  (§0). Task 4 carries two such resolutions and must say in the commit message which side was
  wrong.
- **A negative test for every invariant** (§13). The refusal this slice deletes is replaced by
  a narrower one, and that narrower refusal needs its own test — a deleted guard and a guard
  that never fires are indistinguishable without one.
- **`pricing-core` imports no FastAPI, SQLAlchemy or Redis** (ADR-0001). Nothing in this
  slice changes anything under `packages/pricing-core/`.
- **A fresh worktree has no `.venv`.** Run `uv sync --all-packages --dev` first, or `mypy`
  reports several hundred phantom errors that read as real defects.
- **The worktree guard refuses compound shell commands.** Run each command plainly rather
  than joining them with `&&`.

### The gate

Run all of this before opening a PR. Read each command's **own** exit code — `cmd | tail -1`
reports `tail`'s.

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

The frontend half is **not** touched by this slice's code, but Task 2 changes
`docs/contracts/openapi/generated.json`, and `.github/workflows/frontend.yml` triggers on
`docs/contracts/openapi/**`. Run it too:

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```

Database tests need the compose stack, or they **skip rather than fail**:

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
```

---

## File structure

| File | Change | Responsibility |
|---|---|---|
| `packages/model-schema/src/model_schema/prediction.py` | Modify `:135`, `:323` | The response vocabulary: one new `UnavailableReason` member, one widened `Literal` |
| `packages/model-schema/tests/test_ebm_prediction.py` | Create | That the widened literal and the new reason are both constructible, and that the old members still refuse what they always refused |
| `docs/contracts/openapi/generated.json` | Regenerate | Published contract; never hand-edited |
| `docs/contracts/generated/*.schema.json` | Regenerate | Same |
| `backend/src/app/platform/prediction.py` | Modify `:36-63`, `:155-166`, insert after `:425` | The EBM scoring arm, and the narrower refusal that replaces the old one |
| `backend/tests/test_prediction.py` | Modify `:488-535`, append | The EBM arm's happy path, its unseen-level refusal, and the spec/result-mismatch refusal |
| `docs/specs/02-modelling.md` | Modify §3, `:2185-2205` | The new requirement; the two `predict.py` functions §5.2 omits |
| `docs/roadmap.md` | Modify `:711`, `:3311`, `:3331`, `:3340` | Ownership reconciliation — the roadmap has no W32 row and still names W6b |

**Ordering.** Task 1 → Task 2 → Task 3 → Task 4. Task 2 cannot run before Task 1 (there is
nothing new to generate); Task 3 cannot compile before Task 1 (it constructs the new reason);
Task 4 is documentation and could run anywhere, but it records what Tasks 1–3 decided.

---

### Task 1: The EBM prediction vocabulary in `model-schema`

**Files:**
- Modify: `packages/model-schema/src/model_schema/prediction.py:135` (after
  `COVARIANCE_NOT_STORED`) and `:323` (`model_type`)
- Test: `packages/model-schema/tests/test_ebm_prediction.py` (create)

**Interfaces:**
- Consumes: `UnavailableReason` (`packages/model-schema/src/model_schema/prediction.py:104`),
  `Uncertainty` (`:158`), `Prediction` (`:310`), `UncertaintyKind`, `PredictedRow`.
- Produces:
  - `UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL`, wire value
    `"model_type_has_no_interval"`.
  - `Prediction.model_type: Literal["glm", "xgboost", "lightgbm", "ebm"]`.

  Both are consumed by Task 3.

**Why a fifth reason rather than reusing one.** The four that exist each state something
specific and each is false of an EBM. `no_interval_models_fitted` (FR-MODEL-77) says a
paired-quantile pair *could* be fitted and was not — but `interval_for` lives on `GbmSpec`
and `EbmSpec` has no such field, so no pair is fittable and the reader is told to do
something impossible. `interval_models_not_approved` and `interval_models_stale`
(FR-MODEL-100) both presuppose that pair exists. `covariance_not_stored` (FR-MODEL-93) says
the inputs to an interval were not kept and a refit would recover them — for an EBM there is
no covariance matrix to keep, and a refit recovers nothing. `02` R5 is satisfied by an
explicit statement of *why*, and four wrong whys are not one right one.

- [ ] **Step 1: Write the failing test**

Create `packages/model-schema/tests/test_ebm_prediction.py`:

```python
"""The response vocabulary an EBM prediction needs (W32-4).

An EBM is additive by construction and carries no covariance matrix and no quantile pair,
so the honest answer to "what is the uncertainty" is a typed absence with a reason of its
own. These tests pin the two shape changes that answer costs.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import (
    PredictedRow,
    Prediction,
    UnavailableReason,
    Uncertainty,
    UncertaintyKind,
    new_uuid7,
)


def _prediction(**over: object) -> Prediction:
    base: dict[str, object] = {
        "model_id": new_uuid7(),
        "model_family_slug": "freq-ebm",
        "version": 1,
        "model_type": "ebm",
        "uncertainty": Uncertainty(
            kind=UncertaintyKind.UNAVAILABLE,
            reason=UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL,
        ),
        "rows": (PredictedRow(expected=0.25),),
    }
    base.update(over)
    return Prediction(**base)  # type: ignore[arg-type]


def test_a_prediction_can_declare_the_ebm_model_type() -> None:
    """`model_type` is a closed `Literal`, so an EBM response was unrepresentable until
    this change — the endpoint could not have returned one even with the arm built."""
    assert _prediction().model_type == "ebm"


def test_the_no_interval_reason_names_the_model_type_rather_than_a_missing_pair() -> None:
    """The value is the wire form the frontend's generated union will carry."""
    assert UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL == "model_type_has_no_interval"


def test_the_new_reason_still_obeys_the_kind_and_evidence_validator() -> None:
    """A reason beside anything but `unavailable` is evidence for a claim the response is
    not making — the rule the other four members obey, checked once for the new one."""
    with pytest.raises(ValidationError):
        Uncertainty(
            kind=UncertaintyKind.PREDICTION_INTERVAL,
            reason=UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL,
            level=0.95,
        )


def test_an_ebm_response_carries_no_bounds_on_any_row() -> None:
    """`Prediction`'s own cross-check, exercised on the new arm: an `unavailable` verdict
    beside a row carrying bounds is two answers to one question."""
    with pytest.raises(ValidationError):
        _prediction(rows=(PredictedRow(expected=0.25, lower=0.2, upper=0.3),))


def test_an_unknown_model_type_is_still_refused() -> None:
    """Widening a `Literal` by one member must not turn it into `str`."""
    with pytest.raises(ValidationError):
        _prediction(model_type="random_forest")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest packages/model-schema/tests/test_ebm_prediction.py -q`

Expected: FAIL. The first two fail with `AttributeError: MODEL_TYPE_HAS_NO_INTERVAL` or a
`ValidationError` on `model_type`; `test_an_unknown_model_type_is_still_refused` passes
already, which is correct — it is the guard against over-widening.

- [ ] **Step 3: Add the enum member**

In `packages/model-schema/src/model_schema/prediction.py`, immediately after
`COVARIANCE_NOT_STORED = "covariance_not_stored"` (`:135`):

```python
    #: An EBM. Not "no pair was fitted" (FR-MODEL-77) — `interval_for` lives on `GbmSpec`
    #: and an EBM cannot have one, so that reason would tell a reader to do something the
    #: schema forbids. Not `covariance_not_stored` either: there is no matrix that was not
    #: kept. An EBM is a sum of exported lookup tables and the tables are the whole model,
    #: so the absence is a property of the model *type* and no refit changes it.
    MODEL_TYPE_HAS_NO_INTERVAL = "model_type_has_no_interval"
```

- [ ] **Step 4: Widen the literal**

In the same file, replace `:323`:

```python
    model_type: Literal["glm", "xgboost", "lightgbm"]
```

with:

```python
    model_type: Literal["glm", "xgboost", "lightgbm", "ebm"]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest packages/model-schema/tests/test_ebm_prediction.py -q`
Expected: PASS, 5 tests.

- [ ] **Step 6: Run the whole `model-schema` suite**

Run: `uv run pytest packages/model-schema -q`
Expected: PASS. Nothing else asserts the old three-member literal, but a widened enum can
break an exhaustiveness check elsewhere and this is where that surfaces.

- [ ] **Step 7: Commit**

```bash
git add packages/model-schema/src/model_schema/prediction.py packages/model-schema/tests/test_ebm_prediction.py
git commit -m "feat(w32-4): an EBM prediction has a model type and a reason for having no interval"
```

---

### Task 2: Regenerate the committed contract

**Files:**
- Modify (generated): `docs/contracts/openapi/generated.json`,
  `docs/contracts/generated/*.schema.json`

**Interfaces:**
- Consumes: Task 1's `model_type` literal and `UnavailableReason` member.
- Produces: an OpenAPI `Prediction.model_type` enum of four values, at
  `docs/contracts/openapi/generated.json` around `:7689` — the input `openapi-typescript`
  turns into `frontend/src/api/generated`.

**Why this is its own task.** It is one command, but it is the only step in the slice that
changes a *published* artifact, and `.github/workflows/frontend.yml` triggers on
`docs/contracts/openapi/**` — so this commit is what makes both CI halves run. A reviewer
can accept or reject it independently of the backend arm.

- [ ] **Step 1: Confirm the contract is currently in drift**

Run: `uv run python scripts/generate-contracts.py --check`
Expected: FAIL (non-zero exit), naming the `Prediction` schema. This is the drift guard doing
its job on Task 1's change, and seeing it fail here is the proof it is alive.

- [ ] **Step 2: Regenerate**

Run: `uv run python scripts/generate-contracts.py`

- [ ] **Step 3: Verify the enum actually widened**

Run: `grep -n -A 12 '"Prediction"' docs/contracts/openapi/generated.json`

Expected: the `model_type` property's `enum` now lists four values ending in `"ebm"`. Before
this task, `grep -n '"ebm"' docs/contracts/openapi/generated.json` returned eight hits and
**none** was in `Prediction` — they were `EbmFitResult`, `EbmSpec` and four discriminator
maps. That is why this step greps the schema rather than the string.

- [ ] **Step 4: Verify the drift check now passes**

Run: `uv run python scripts/generate-contracts.py --check`
Expected: PASS, exit 0.

- [ ] **Step 5: Verify the frontend still type-checks against it**

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend type-check
```

Expected: PASS. The frontend references nothing EBM-shaped today, so a widened union should
be inert — but the client is git-ignored and regenerated, so a diff can never show this and
only the type-check can.

- [ ] **Step 6: Commit**

```bash
git add docs/contracts
git commit -m "chore(w32-4): regenerate the contract for the EBM prediction vocabulary"
```

---

### Task 3: The EBM scoring arm

**Files:**
- Modify: `backend/src/app/platform/prediction.py` — the import block at `:36-63`, the
  dispatch at `:155-166`, and a new `_score_ebm` inserted after `_score_gbm` ends at `:425`
- Test: `backend/tests/test_prediction.py` — replace
  `test_an_ebm_spec_is_refused_by_name_at_the_predict_boundary` at `:488-535`, and append two

**Interfaces:**
- Consumes: Task 1's `UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL`; `predict_ebm` from
  `pricing_core.modelling.predict`; the existing `_unscoreable(exc)` helper at `:475`; the
  existing `_ebm_spec(version_id, factor_ids, **over)` test helper at
  `backend/tests/test_prediction.py:139`.
- Produces:

  ```python
  async def _score_ebm(
      fit: FitResult,
      frame: pl.DataFrame,
      factors: Sequence[Factor],
      *,
      bandings: Mapping[UUID, Banding],
      groupings: Mapping[UUID, Grouping],
  ) -> tuple[
      npt.NDArray[np.float64],
      npt.NDArray[np.float64] | None,
      npt.NDArray[np.float64] | None,
      Uncertainty,
  ]
  ```

  The four-tuple is the shape `_score_glm` and `_score_gbm` already return, so the dispatch
  stays a straight three-way assignment. The second and third elements are always `None`.

**What replaces the refusal, and what does not.** The `MODEL_TYPE_UNSUPPORTED` raise at
`:155-166` currently fires on *any* `EbmSpec`. After this task it fires on a narrower thing:
an `EbmSpec` whose stored `fit_result` is not an `EbmFitResult`. That pairing is supposed to
be impossible — `02` R2 freezes `spec` and `fit_result` together — but `predict_rows` reads
both out of a database row and validates them through two independent adapters, so nothing in
the type system connects them. `backend/src/app/worker/model_handlers.py:447` already treats
exactly this mismatch as `MODEL_TYPE_UNSUPPORTED`, so the code keeps its meaning and gains a
second, consistent site. It is also what narrows the type for `mypy`, which is why an
`assert` will not do: an `assert` compiled out under `-O` turns a governed refusal into an
`AttributeError`.

**No offset, no interval, no blob.** `predict_ebm` returns `mu` on the mean scale directly —
identity link, no link inversion, no `model_offset` (FR-MODEL-24 refuses an EBM offset ref at
the schema), and no blob fetch, because an EBM's fit result *is* its model. That is why
`_score_ebm` needs neither `session`, nor `blob_store`, nor `model`, nor `workspace_id`,
where `_score_gbm` needs all four.

- [ ] **Step 1: Replace the refusal test with the happy path**

In `backend/tests/test_prediction.py`, delete
`test_an_ebm_spec_is_refused_by_name_at_the_predict_boundary` in its entirety (`:488-535`,
from the `@pytest.mark.req("FR-MODEL-37")` line down to the
`assert refused.value.status_code == 409` that closes it) and put this in its place:

```python
@pytest.mark.req("FR-MODEL-37")
async def test_an_ebm_is_scored_and_states_that_its_type_has_no_interval(
    database, blob_store, workspace_id
) -> None:
    """The arm this slice builds, end to end through the real fit Job.

    Two things are asserted together because separating them would let either pass alone
    and neither is the requirement on its own: the rows carry an expectation that differs
    between the two areas — a model returning the intercept for every row would also
    "score" — and the response says *why* it carries no bounds rather than leaving the
    caller to infer it from three nulls.
    """
    actor, model_id = await _fitted_ebm(database, blob_store, workspace_id)

    async with database.session() as session:
        prediction = await service.predict_rows(
            session,
            workspace_id=workspace_id,
            actor=actor,
            model_id=model_id,
            rows=ROWS,
            blob_store=blob_store,
        )

    assert prediction.model_type == "ebm"
    assert prediction.uncertainty.kind is UncertaintyKind.UNAVAILABLE
    assert prediction.uncertainty.reason is UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL
    assert prediction.uncertainty.level is None
    assert len(prediction.rows) == len(ROWS)
    assert all(row.lower is None and row.upper is None for row in prediction.rows)
    assert prediction.rows[0].expected != prediction.rows[1].expected
```

- [ ] **Step 2: Add the fixture that fits a real EBM**

Immediately after `_fitted_glm` ends (`backend/tests/test_prediction.py:136`, the line
returning its tuple), add — reusing whichever dataset, version and factor helpers
`_fitted_glm` itself calls, so the two fixtures share one setup path:

```python
async def _fitted_ebm(database, blob_store, workspace_id) -> tuple[Principal, UUID]:
    """One EBM fitted through the real `MODEL_FIT` Job, exactly as `_fitted_glm` fits a GLM.

    Through the Job rather than by writing a `fit_result` onto a reservation, because the
    thing under test is scoring an artifact the platform actually produced: a hand-built
    `EbmFitResult` would pin this test to whatever shape the test author believed in rather
    than to the one `fit_ebm` exports.
    """
    actor, glm_id, _spare = await _fitted_glm(database, blob_store, workspace_id)

    async with database.session() as session:
        glm = await session.get(ModelRow, glm_id)
        assert glm is not None
        version_id = glm.dataset_version_id
        factor_ids = tuple(UUID(f["id"]) for f in glm.spec["factors"])

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_ebm_spec(version_id, factor_ids),
        )
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "model_id": str(model_id),
            },
            actor,
            workspace_id=workspace_id,
        )

    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    return actor, model_id
```

If `_fitted_glm`'s return arity or its spec's factor shape differs from what is written
here, adapt this fixture to it rather than the other way round — `_fitted_glm` is the
established path and eight other tests depend on it.

- [ ] **Step 3: Run the test to verify it fails**

Run:
`uv run pytest "backend/tests/test_prediction.py::test_an_ebm_is_scored_and_states_that_its_type_has_no_interval" -q`

Expected: FAIL with `PlatformError` code `MODEL_TYPE_UNSUPPORTED` — the refusal this task
removes, firing on a model that was really fitted. If it instead **skips**, the compose stack
is down; start it and re-run.

- [ ] **Step 4: Import what the arm needs**

In `backend/src/app/platform/prediction.py`, add `EbmFitResult` and `FitResult` to the
`model_schema` import block (`:36-63`), keeping its existing alphabetical order — `EbmFitResult`
goes immediately before `EbmSpec`, and `FitResult` immediately after `Factor`:

```python
    Banding,
    EbmFitResult,
    EbmSpec,
    Factor,
    FitResult,
    GbmFitResult,
```

- [ ] **Step 5: Write the arm**

Insert it after `_score_gbm` ends (`:425`) and before the next helper begins:

```python
async def _score_ebm(
    fit: FitResult,
    frame: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding],
    groupings: Mapping[UUID, Grouping],
) -> tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.float64] | None,
    npt.NDArray[np.float64] | None,
    Uncertainty,
]:
    """`mu` from an EBM's exported tables, and the typed absence its type forces.

    The shortest of the three arms, and the shortness is the requirement rather than a
    convenience: an EBM's fit result *is* its model (ADR-0003), so there is no blob to
    fetch, no link to invert, and no `model_offset` to forward — FR-MODEL-24 refuses an
    EBM offset ref at the schema, so no spec reaching here can carry one.

    The interval is absent by construction. `interval_for` lives on `GbmSpec`, so no
    quantile pair is fittable for an EBM, and there is no covariance matrix that could
    have been stored and was not. Reporting either of those reasons would tell a reader to
    do something the schema forbids, which is why this arm carries a reason of its own.
    """
    from pricing_core.modelling import ModellingError
    from pricing_core.modelling.predict import PredictionError, predict_ebm

    if not isinstance(fit, EbmFitResult):
        # `02` R2 freezes `spec` and `fit_result` together, so this pairing should not
        # exist — but the two are validated out of the row by independent adapters and
        # nothing in the type system joins them. Refused rather than asserted: an `assert`
        # compiled out under `-O` turns a governed refusal into an `AttributeError`, and
        # `model_handlers.py` already names this same mismatch with this same code.
        raise PlatformError(
            "MODEL_TYPE_UNSUPPORTED",
            "This model's spec and fit result disagree about its type",
            409,
            f"the spec is an EBM and the stored fit result is a "
            f"{type(fit).__name__}. `02` R2 freezes the two together, so this row was "
            "written by something that bypassed the model service.",
        )

    try:
        expected = predict_ebm(fit, frame, factors, bandings=bandings, groupings=groupings)
    except (ModellingError, PredictionError) as exc:
        raise _unscoreable(exc) from exc

    return (
        expected,
        None,
        None,
        Uncertainty(
            kind=UncertaintyKind.UNAVAILABLE,
            reason=UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL,
        ),
    )
```

Both imports sit inside the function body, matching `_score_gbm` — the module is imported at
request time, not at process start, and `_unscoreable` catches both hierarchies because
`FactorResolutionError` is a sibling of `PredictionError` rather than a subclass.

- [ ] **Step 6: Route the dispatch to it**

In `predict_rows`, replace the whole `elif isinstance(spec, EbmSpec):` branch — the
`raise PlatformError("MODEL_TYPE_UNSUPPORTED", ...)` block at `:155-166` — with:

```python
    elif isinstance(spec, EbmSpec):
        expected, lower, upper, uncertainty = await _score_ebm(
            fit,
            frame,
            factors,
            bandings=bandings,
            groupings=groupings,
        )
```

- [ ] **Step 7: Run the test to verify it passes**

Run:
`uv run pytest "backend/tests/test_prediction.py::test_an_ebm_is_scored_and_states_that_its_type_has_no_interval" -q`
Expected: PASS.

- [ ] **Step 8: Write the two refusal tests**

The arm removed one guard and added another; both new refusals need a test, and a refusal
test is finished only when a passing case sits beside it — Step 1's happy path is that case
for both. Append to `backend/tests/test_prediction.py`:

```python
@pytest.mark.req("FR-MODEL-37")
async def test_an_ebm_scored_on_a_level_it_never_saw_is_refused_by_name(
    database, blob_store, workspace_id
) -> None:
    """An EBM's categorical lookup has one slot per level the fit observed, and a level
    with no slot has no score. Inventing one would price the row as whichever level shares
    its index — FR-MODEL-32's rule, reaching the caller as a named 409 rather than as an
    `IndexError` in a traceback."""
    actor, model_id = await _fitted_ebm(database, blob_store, workspace_id)

    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.predict_rows(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                rows=[{"exposure_years": 1.0, "area": "offshore"}],
                blob_store=blob_store,
            )

    assert refused.value.code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert refused.value.status_code == 409
    assert "area" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-37")
async def test_an_ebm_spec_carrying_a_glm_fit_result_is_refused_by_name(
    database, blob_store, workspace_id
) -> None:
    """The narrower refusal that replaced the blanket one.

    Built the way the deleted refusal test built its ghost: a reservation carries the EBM
    spec and a real GLM fit is written onto it directly, because `02` R2 freezes the two
    together once either exists and no service path will produce this pair. Without this
    test, deleting the guard and leaving it in place look identical from outside.
    """
    actor, glm_id, _spare = await _fitted_glm(database, blob_store, workspace_id)

    async with database.session() as session:
        glm = await session.get(ModelRow, glm_id)
        assert glm is not None
        version_id = glm.dataset_version_id
        factor_ids = tuple(UUID(f["id"]) for f in glm.spec["factors"])
        glm_fit_result = glm.fit_result

    async with database.unit_of_work() as session:
        ebm_row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_ebm_spec(version_id, factor_ids),
        )
        ebm_id = ebm_row.id
        await session.execute(
            ModelRow.__table__.update()
            .where(ModelRow.id == ebm_id)
            .values(fit_result=glm_fit_result, status=ModelStatus.FITTED.value)
        )

    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.predict_rows(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=ebm_id,
                rows=ROWS,
                blob_store=blob_store,
            )

    assert refused.value.code == "MODEL_TYPE_UNSUPPORTED"
    assert refused.value.status_code == 409
    assert "GlmFitResult" in (refused.value.detail or "")
```

- [ ] **Step 9: Run both refusal tests**

Run: `uv run pytest backend/tests/test_prediction.py -q -k "ebm"`
Expected: PASS, 3 tests.

If the unseen-level test fails with `MODEL_TERM_UNRESOLVED` instead, the frame is missing the
resolved column rather than carrying an unknown level — check that `_ebm_spec` was given the
same factor ids `_fitted_ebm` fitted on.

- [ ] **Step 10: Run the whole prediction suite and `mypy`**

Run: `uv run pytest backend/tests/test_prediction.py -q`
Expected: PASS, no regressions.

Run: `uv run mypy`
Expected: PASS. This is the command the `isinstance` guard exists for — without it, `mypy`
reports `predict_ebm` receiving a `FitResult` where an `EbmFitResult` is required.

- [ ] **Step 11: Commit**

```bash
git add backend/src/app/platform/prediction.py backend/tests/test_prediction.py
git commit -m "feat(w32-4): score an EBM at the predict boundary instead of refusing it"
```

---

### Task 4: Resolve the spec and the roadmap against what was built

**Files:**
- Modify: `docs/specs/02-modelling.md` — §3's requirement table, and §5.2's `predict.py`
  block at `:2185-2205`
- Modify: `docs/roadmap.md:711`, `:3311`, `:3331`, `:3340`
- Modify: `backend/tests/test_prediction.py` — one added marker (Step 5)

**Interfaces:**
- Consumes: everything Tasks 1–3 built.
- Produces: no code. This task is CLAUDE.md §0's resolution step, and §14 question 4's
  finding for this corner of `02`.

**Three findings, three verdicts.**

1. **No requirement said an EBM could be predicted, and none said it could not.** Across `02`'s
   EBM mentions, exactly two touch prediction: FR-MODEL-24's refusal of an EBM offset ref,
   and §5.2's `predict_ebm` signature. The endpoint's refusal was therefore an implementation
   decision recorded only in a docstring and in the roadmap. The spec gains the obligation,
   because the next reader must be able to learn from `02` alone that an EBM prediction
   carries a typed absence and which one.
2. **§5.2's `predict.py` block is incomplete, and was before this slice.** It lists
   `linear_predictor`, `predict_glm`, `predict_glm_interval` and `predict_ebm`, and omits
   `score_fitted` and `detect_quantile_crossing` — both of which exist and are both called
   from `backend/src/app/platform/prediction.py`. The **code** is right here; the spec is
   incomplete and gets completed.
3. **The roadmap names W6b as this arm's owner in four places and has no W32 row at all.**
   `grep -n "W32" docs/roadmap.md` returns nothing; the highest id is W31. The slice map
   ([`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) §6) records that the split
   itself is accepted while the slice boundaries and sequencing are still pending, so this
   task reconciles the *ownership attribution* only and does **not** add a W32 workstream
   row — that is the maintainer's call, not this plan's.

- [ ] **Step 1: Append the requirement to `02` §3**

The requirement rows in `02` §3 are single lines of the form `| **FR-MODEL-N** | text |`.
Insert the row reproduced after the marker below — everything from the first `|` onward,
as one line — immediately after FR-MODEL-123's row (`docs/specs/02-modelling.md:244`).

Next free: `FR-MODEL-124` — the row to insert is: `| **FR-MODEL-124** | An EBM prediction is served, and states `model_type_has_no_interval` as its reason for carrying no interval. Added 2026-08-23 (W32-4). FR-MODEL-37 made an EBM storable and §5.2's `predict_ebm` made it scoreable; between 2026-08-21 and this date the endpoint refused every EBM with `MODEL_TYPE_UNSUPPORTED`, a decision recorded in a docstring and in the roadmap and in no requirement. The reason is a fifth member of `UnavailableReason` rather than a reuse of the four FR-MODEL-77 and FR-MODEL-93 define, because each of the four states something false of an EBM: the three interval-model reasons all presuppose a quantile pair, which `EbmSpec` cannot declare because `interval_for` lives on `GbmSpec`, so a reader told that no interval models were fitted is told to do something the schema forbids; and `covariance_not_stored` says inputs that existed were not kept, where an EBM has no covariance matrix at any point in its life and no refit produces one. R5 is satisfied by an explicit statement of why, and a reason that misdescribes the cause is not one. The blanket refusal is narrowed rather than deleted: `MODEL_TYPE_UNSUPPORTED` still fires where an EBM spec is paired with a fit result of another type, which R2 forbids and which the two independent validating adapters cannot rule out, and it is refused rather than asserted so that it survives `-O`. |`

- [ ] **Step 2: Complete §5.2's `predict.py` block**

In `docs/specs/02-modelling.md`, immediately after the `predict_ebm` signature (ending
`:2205`) and before the next module's comment line, add inside the same fenced block:

```
def score_fitted(fit: FitResult, spec: ModelSpec, data: pl.DataFrame,
                 factors: Sequence[Factor], *,
                 model_offset: np.ndarray | None = None,
                 bandings: Mapping[UUID, Banding] | None = None,
                 groupings: Mapping[UUID, Grouping] | None = None,
                 booster: bytes | None = None) -> NDArray[float64]
def detect_quantile_crossing(lower: NDArray[float64],
                             upper: NDArray[float64]) -> tuple[int, float]
```

Copy the two signatures from
`packages/pricing-core/src/pricing_core/modelling/predict.py:406` and `:462` rather than
from here, so the spec records what the code says on the day it is written.

- [ ] **Step 3: Add the dated note recording why §5.2 changed**

Immediately after the closing fence of §5.2's signature block, add:

```
> **Two functions were missing from this block until 2026-08-23 (W32-4).** `score_fitted`
> and `detect_quantile_crossing` have existed in `predict.py` since the prediction slice and
> are both called from the platform's own scoring service, so a reader working from this page
> alone would have concluded that the type dispatch lived in the backend and that a crossing
> pair was detected there. The code was right and this block was incomplete; it is completed
> rather than the functions being moved to match it.
```

- [ ] **Step 4: Reconcile ownership in the roadmap**

At `docs/roadmap.md:711`, `:3311`, `:3331` and `:3340` — each of which attributes the unbuilt
EBM predict arm to W6b — replace the attribution with **W32-4** and append to each:

```
Built 2026-08-23 (W32-4, the EBM predict arm).
```

Leave the surrounding text as written. A roadmap entry records what was believed at its date,
and the ownership label is the only part this slice has standing to correct.

- [ ] **Step 5: Mark the happy-path test with the new requirement**

Add a second marker to `test_an_ebm_is_scored_and_states_that_its_type_has_no_interval`,
naming the requirement id allocated in Global Constraints and written out in Step 1, so it
carries both `FR-MODEL-37` and the new id. `pytest` runs with `--strict-markers` and
`req-coverage.py` fails on a marker naming an id no spec defines, so this step must come
after Step 1 and never before it.

- [ ] **Step 6: Run the documentation checks**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
```

Expected: both PASS, with the new requirement reported as covered.

- [ ] **Step 7: Run the full gate**

Run every command in the gate block at the top of this plan, each on its own line, reading
each one's own exit code.

- [ ] **Step 8: Commit**

```bash
git add docs/specs/02-modelling.md docs/roadmap.md backend/tests/test_prediction.py
git commit -m "docs(w32-4): specify the EBM prediction arm, complete 5.2, reconcile ownership"
```

---

## Closing the slice

- [ ] Every task's steps are checked.
- [ ] The gate passes locally, both halves, with `generate-contracts.py --check` rather than
      the plain regenerate.
- [ ] `uv run python scripts/req-coverage.py` shows the new requirement covered.
- [ ] The branch is pushed and a PR is open. Do not force-push, do not merge, do not push to
      `main`.

## Self-Review

**1. Spec coverage.** The slice map's brief for W32-4 is one line — *"`prediction.py` refuses
EBM with `MODEL_TYPE_UNSUPPORTED`"*. Task 3 removes that refusal, Task 1 supplies the
vocabulary it needs, Task 2 publishes it, and Task 4 writes the requirement that was missing.
FR-MODEL-37 is the only existing requirement the arm is written against and it is cited by
every test. The two §14 question-4 divergences found while reading — §5.2's omissions and the
roadmap's ownership — are both resolved in Task 4 rather than noted and left.

**2. Placeholder scan.** Every code step carries its code. The one deferred value is the
requirement id in Task 4 Step 5, deferred only because `scripts/audit-docs.py` fails a plan
that names an undefined id anywhere except after a `Next free:` marker on the same line — the
id is allocated explicitly in Global Constraints and written out in full in Task 4 Step 1.
Task 3 Steps 2 and 8 both say what to do if `_fitted_glm`'s arity differs from what is
written; that is a stated fallback, not a placeholder — the code is present either way.

**3. Type consistency.** `_score_ebm` returns the same four-tuple as `_score_glm` and
`_score_gbm`, so the dispatch's three branches assign the same four names. `predict_ebm`'s
call in Task 3 matches its definition at
`packages/pricing-core/src/pricing_core/modelling/predict.py:338` exactly, including that
`bandings` and `groupings` are keyword-only. The enum member's Python name
(`MODEL_TYPE_HAS_NO_INTERVAL`) and wire value (`model_type_has_no_interval`) are used
consistently across Tasks 1, 3 and 4 — the Python name in code, the wire value in the
contract and in the requirement text.
