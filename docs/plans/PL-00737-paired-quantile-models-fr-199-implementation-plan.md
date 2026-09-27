---
id: PL-737
family: plan
kind: leaf
title: Paired Quantile Models (FR-199) Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-19
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-19-paired-quantile-models.md
---

# Paired Quantile Models (FR-199) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a GBM able to carry a real prediction interval, by letting an actuary fit
paired quantile Models linked to a central Model, detecting crossing rather than hiding it,
and making the two `UnavailableReason` values that are currently declared-and-unreachable
reachable.

**Architecture:** A bound is an ordinary `Model` — same family, dataset version, split and
factor set as its central Model — fitted with the `quantile` template at a declared `alpha`,
and linked by a new `interval_for` block on `GbmSpec`. Because the link lives in the spec it
joins `spec_hash` (FR-206, `v3 → v4`), which is what stops two bounds against different
central versions colliding. Prediction finds the pair by querying the link, decides one
verdict per model, and either returns bounds or FR-198's typed absence.

**Tech Stack:** Python 3.12, Pydantic v2 (`model-schema`), SQLAlchemy 2.x async + Alembic
(`backend`), Polars + XGBoost/LightGBM (`pricing-core`), pytest + hypothesis.

**Spec:** `docs/specs/02-modelling.md` — §3.10 (FR-MODEL-63, 77, 78, 93, 98, 99), §4.5's
`quantile` row, §4.8 `Model`, §4.4 `GbmSpec`, §5.1. Read §3.10 in full before Task 1; the
requirement text and the amendment note under it are the contract this plan argues from.

---

## Global Constraints

Copied verbatim from `CLAUDE.md` and the specs. Every task's requirements include these.

- **Requirement IDs are permanent** (`CLAUDE.md` §5). Never renumber. Append, or mark
  superseded. The next free id is **FR-200**; the next free open question is
  **OQ-588**. Find the *maximum* id, not the last one you read — `02`'s requirement
  tables are not in numeric order.
- **`model-schema` is the single source of truth** for shapes crossing a boundary
  (`CLAUDE.md` §2, ADR-704). Nobody hand-writes a shape that already exists there — not the
  backend, not the frontend, not a test fixture.
- **`pricing-core` stays importable standalone** with zero FastAPI/SQLAlchemy/Redis
  dependencies (ADR-703, enforced by `.importlinter`).
- **Money is integer minor units or `Decimal`, never float**, in the rating path
  (`CLAUDE.md` §7). `DecimalStr` refuses a `float` as of PR #116 (OQ-547).
- **Artifacts are immutable.** A Model is never edited; a change is a new version
  (`02` §4.8 R2). Artifact tables carry `SELECT, INSERT`-only privileges *and* the
  `artifact_append_only` trigger (FR-43/44).
- **Any change to the set of fields entering the `spec_hash` payload increments
  `SPEC_HASH_VERSION` in the same commit as the field** (FR-206).
- **A field is shown live only once a slice populates it** (FR-207). Anything else is
  named in place with a dated note saying it is declared-and-unbuilt and who owns it.
- **When code and spec disagree, stop and resolve it** (`CLAUDE.md` §0) — never quietly make
  one match the other.
- **Every test carries a `@pytest.mark.req` marker** naming the requirement it satisfies
  (`CLAUDE.md` §13). A negative test is required for every invariant introduced.
- **Conventional Commits**, short-lived branch from `main`, squash-merge.

### The gate (run both halves, read each command's own exit code)

```bash
uv sync --all-packages --dev
docker compose -f deploy/docker-compose.yml up -d --wait
export GIP_TEST_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
export GIP_DATABASE_URL="$GIP_TEST_DATABASE_URL"
uv run alembic upgrade head

uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check

pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

`pnpm` is at `~/.npm-global/bin` and is not on the default PATH. LightGBM needs `libgomp1`
(`sudo apt-get install -y libgomp1`); without it you get a collection error with no obvious
link to your change. ~90 backend tests skip silently without `GIP_TEST_DATABASE_URL`.

### Baseline at the time of writing (2026-08-19)

`main` at `e3b46c3`. Suite: **1283 Python**, **113 frontend**. Requirements: **478 specified,
224 marked**. Generated contracts: **21**. `SPEC_HASH_VERSION` is **3**.

---

## ⚠ Decision gate — read before starting

**Task 1 raises `OQ-588` and the plan cannot finish without an answer to it.** Tasks 2–5
are unaffected by which way it goes and can be built while it is open. **Task 6 onward
depends on it.** Do not start Task 6 until the maintainer has written an acceptance line into
`docs/open-questions.md`.

The question, in one sentence: **a paired quantile interval covers `Y`, but the only
`UncertaintyKind` the platform offers covers `E[Y|x]` — what does the response call it?**

FR-196 (decided 2026-08-18, OQ-585) says the platform offers **exactly one**
interval kind, `confidence_interval_mean`, and that the second — when a named consumer
appears — is `prediction_interval`, computed as `φ·V(μ)` from `GlmFitResult.dispersion`, for
aggregate predictions first. A quantile pair is neither: it estimates the same *quantity* as
`prediction_interval` by an entirely different *estimator*, it is per-row rather than
aggregate, and it arrives through a door FR-196 did not name — an actuary who opted in
and paid the 2–3× fit cost.

This plan builds on the recommended answer (a third member, `quantile_pair_interval`). If the
maintainer decides otherwise, the changes are confined to Task 6 Step 1 and Task 7 Step 3 —
noted inline at both.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `backend/migrations/versions/<rev>_interval_for_index.py` | One functional index on `models.spec->'interval_for'->>'model_id'`, so finding a central Model's bounds is not a sequential scan over every model in the workspace. |
| `backend/tests/test_paired_quantile_models.py` | The pairing rules, the two interpretation choices, and the reachability of all four `UnavailableReason` values. |
| `packages/pricing-core/tests/test_quantile_crossing.py` | Crossing detection as pure arithmetic, with no database. |

### Modified

| Path | Change |
|---|---|
| `docs/specs/02-modelling.md` | FR-200 appended to §3.10; FR-198 and FR-207 gain dated amendment notes; §4.4 gains the `interval_for` block; §4.8's staging note updated; §5.1's error-code paragraph gains one code. |
| `docs/open-questions.md` | OQ-588 raised with options and a recommendation. |
| `packages/model-schema/src/model_schema/modelling.py` | `IntervalFor` model; `GbmSpec.interval_for`; validators. |
| `packages/model-schema/src/model_schema/prediction.py` | `UncertaintyKind.QUANTILE_PAIR_INTERVAL`; `IntervalModels` block on `Uncertainty`; validator widened. |
| `packages/model-schema/src/model_schema/diagnostics.py` | `QuantileCrossing` model; `GbmDiagnostics.quantile_crossing`. |
| `packages/model-schema/src/model_schema/__init__.py` | Re-export the four new names. |
| `packages/pricing-core/src/pricing_core/modelling/predict.py` | `detect_quantile_crossing`. |
| `backend/src/app/platform/modelling.py` | `SPEC_HASH_VERSION` `3 → 4`; `_refuse_mismatched_interval_model`; `load_interval_models`. |
| `backend/src/app/platform/prediction.py` | `_score_gbm` gains the pair lookup and the four-way verdict. |
| `backend/src/app/worker/model_handlers.py` | Fit-time crossing detection for the second bound. |
| `backend/src/app/errors.py` | `MODEL_INTERVAL_PAIR_INVALID` registered. |
| `docs/contracts/schemas/model-spec.schema.json`, `model.schema.json`, `diagnostics.schema.json` | Regenerated, never hand-edited. |
| `docs/roadmap.md` | WK-661 slice record; WK-661's row gains this slice. |

### Deliberately not touched

- **The frontend.** No view renders a GBM interval, and `02` §5.3's model-detail view is
  WK-664's. Building a screen here is building ahead of the row that owns it (`CLAUDE.md` §0).
  Task 8 records this as a stated verdict with an owner, not as silence.
- **`03-rating-engine.md`.** Whether a Rating Version may rate on a quantile bound is Phase 2
  and a spec change if anyone asks. Nothing here touches it.

---

## Task 1: The spec change — FR-200, and the question the requirement leaves open

Documents only. No code. This is the design step, not paperwork (`CLAUDE.md` §0).

**Files:**
- Modify: `docs/specs/02-modelling.md` (§3.10 requirement table, §4.4, §4.8, §5.1)
- Modify: `docs/open-questions.md`

**Interfaces:**
- Consumes: nothing.
- Produces: `FR-200` (the id every later task's `@pytest.mark.req` names) and
  `OQ-588` (the gate above).

- [ ] **Step 1: Confirm the ids are free before writing either**

```bash
grep -o "FR-MODEL-[0-9]*" docs/specs/02-modelling.md | sort -t- -k3 -n | tail -3
grep -o "OQ-MODEL-[0-9]*" docs/open-questions.md | sort -t- -k3 -n | tail -3
```

Expected: highest `FR-197`, highest `OQ-587`. If either is higher, use the next
free number and update every reference in this plan. **Do not renumber anything existing.**

- [ ] **Step 2: Append FR-200 to §3.10's requirement table**

Put it immediately after FR-199's row, since it is that requirement's build record.

```markdown
| **FR-200** | **`interval_for` lives on `GbmSpec` and joins the `spec_hash` payload; the two readings FR-198 left open are fixed here.** Added 2026-08-19 (WK-661, the paired-quantile slice), building FR-199. **(i) The link is a spec field, not a Model column** — FR-137 set the precedent for a Model that exists relative to another Model (`approximates_model_id` on the approximating Model's spec), and the reason is the same: the pairing is part of what the model *is*, so two bounds against different central versions must not collide under one `spec_hash`. `SPEC_HASH_VERSION` moves `v3 → v4` in the same commit (FR-206). **(ii) `interval_models_not_approved` means the bounds are less advanced than the model they bound**, not that they are unapproved outright — the strict reading would make the feature unusable before approval, which is exactly when an actuary is deciding whether the bounds are any good. The bounds must be at a lifecycle status at least as advanced as their central Model's; an `approved` Model quoting a `fitted` bound would put an unreviewed number beside a reviewed one. **(iii) `interval_models_stale` means the central Model is `superseded`** — the literal reading of FR-198's "fitted against a superseded Model version". `SCOREABLE_MODEL_STATUSES` admits `superseded`, so a bound on a retired version is quotable and would otherwise be quoted with nothing saying the family has moved past it. **(iv) Exactly one bound per side.** A central Model carries at most one `alpha < 0.5` and one `alpha > 0.5`; a second on either side is refused with `MODEL_INTERVAL_PAIR_INVALID`. Widening to a set of nested bands is additive; shipping an ambiguous set is not, because the response carries one `level` and nothing would say which pair produced it. |
```

- [ ] **Step 3: Add a dated amendment note under FR-198**

Directly below FR-198's row, in the same blockquote style §3.10 already uses:

```markdown
> **All four `UnavailableReason` values are reachable from 2026-08-19 (WK-661, the
> paired-quantile slice).** FR-207's staging rule required the two unreachable ones to
> be named in place; they were, in `UnavailableReason`'s docstring, and that note is now
> removed rather than left to describe a state the code has left. What the reasons *mean* was
> not decided by FR-198 and is decided by FR-200 — a requirement rather than an
> implementation choice, because "not approved" and "stale" each had two defensible readings
> and the one built is the one a reader will assume was specified.
```

- [ ] **Step 4: Add the `interval_for` block to §4.4's `GbmSpec` JSON example**

Find §4.4's gradient-boosting arm and add the field to the example, with a note:

```json
  "interval_for": {
    "model_id": "uuid",
    "model_version": 7,
    "alpha": 0.05
  }
```

```markdown
> **`interval_for` is live from 2026-08-19 (WK-661, the paired-quantile slice)** — FR-207's
> staging rule, and the last of the fields OQ-582 listed as absent-entirely on this arm.
> `null` on every GBM that is not itself a bound, which is almost all of them: it is the
> declaration that *this* model is one side of another model's interval, and FR-199
> makes that an opt-in the actuary pays 2–3× a fit for.
```

- [ ] **Step 5: Update §4.8's staging note and FR-207's residual list**

In FR-207's row, `interval_for` is listed under **absent entirely**. It is no longer
absent. Amend in place rather than deleting the mention:

```markdown
`interval_for` — **live from 2026-08-19** (FR-200), on `GbmSpec` rather than on
`Model`;
```

- [ ] **Step 6: Register the new error code in §5.1**

Find the paragraph listing `MODEL_TERM_UNRESOLVED`, `MODEL_LINK_UNSUPPORTED`,
`MODEL_OFFSET_MISSING`, `MODEL_INTERVAL_UNAVAILABLE` (around line 1377) and add
`MODEL_INTERVAL_PAIR_INVALID` to it, with a sentence saying it refuses a bound whose spec
disagrees with its central Model.

- [ ] **Step 7: Raise OQ-588 in `docs/open-questions.md`**

Add a row to the `MODEL` table, matching the existing column shape exactly (Question ·
Options · Recommendation · Owner · Status). The recommendation must be a recommendation, not
a decision — the status is `open`.

```markdown
| **OQ-588** | A paired quantile interval covers `Y`; `UncertaintyKind.confidence_interval_mean` covers `E[Y|x]`; and FR-196 fixes the platform at exactly one kind, naming `prediction_interval` (`φ·V(μ)`, aggregate-first) as the only future second. What does a quantile-pair response call itself? | Raised 2026-08-19 (WK-661, the paired-quantile slice) on finding FR-199's deliverable has no name in the enum FR-196 closed. **Reuse `confidence_interval_mean`:** no contract change, and it is a lie — the pair covers the outcome, not the mean, and FR-196 says that value is "never silently widened". **Use FR-196's reserved `prediction_interval`:** the right *quantity*, and it collides with a reserved name whose stated computation is `φ·V(μ)` from a GLM's dispersion, offered for aggregates first — a client matching the value would get a per-row quantile pair where the requirement promised an aggregate variance interval. **A third member, `quantile_pair_interval`:** names the estimator as well as the quantity, so a reader comparing a GBM bound with a GLM bound can tell they are not the same kind of claim; costs an enum member, which FR-196 correctly calls a contract change. | **A third member, `quantile_pair_interval`.** FR-196's argument against a second kind was that shipping one *before a consumer exists* puts two numbers on a screen with nothing saying which to trust. Here the consumer exists and is explicit — FR-199 makes the pair opt-in and 2–3× the cost, so nobody receives one without having asked. The argument that survives is the naming one, and it points at a distinct member rather than at either existing value: `confidence_interval_mean` would be false, and `prediction_interval` is reserved for a different estimator at a different granularity, so taking it would leave FR-196's named trigger with no name to fire into. **FR-196 is amended by addendum, not edited** — its boundary holds, and this is the second door it did not anticipate. | maintainer | **open** |
```

- [ ] **Step 8: Run the docs audit**

```bash
python3 scripts/audit-docs.py
```

Expected: `All checks passed`. The audit checks that every open question in a spec's §10 is
mirrored into `open-questions.md` and back — so if you added OQ-588 to only one of them,
this is where you find out. It also catches a requirement-id collision, but *after* the edit.

- [ ] **Step 9: Commit**

```bash
git add docs/specs/02-modelling.md docs/open-questions.md
git commit -m "docs(model): FR-200 — interval_for's home, and the two readings FR-198 left open"
```

- [ ] **Step 10: Ask the maintainer for OQ-588**

Stop here and surface the question. Tasks 2–5 do not depend on the answer; Task 6 does.
Do not pick it yourself (`CLAUDE.md` §0).

---

## Task 2: `IntervalFor` on `GbmSpec`, and the `spec_hash` bump

**Files:**
- Modify: `packages/model-schema/src/model_schema/modelling.py`
- Modify: `packages/model-schema/src/model_schema/__init__.py`
- Modify: `backend/src/app/platform/modelling.py:100` (`SPEC_HASH_VERSION`)
- Test: `packages/model-schema/tests/test_modelling.py`
- Test: `backend/tests/test_model_specs.py` (the `spec_hash` version assertions)

**Interfaces:**
- Consumes: `FR-200` from Task 1.
- Produces: `IntervalFor(model_id: UUID, model_version: int, alpha: float)`, frozen,
  `extra="forbid"`; `GbmSpec.interval_for: IntervalFor | None = None`;
  `SPEC_HASH_VERSION == 4`.

- [ ] **Step 1: Write the failing tests**

Add to `packages/model-schema/tests/test_modelling.py`:

```python
@pytest.mark.req("FR-200")
def test_an_interval_bound_declares_a_two_sided_alpha() -> None:
    """`alpha` is a quantile, so 0 and 1 are not bounds — they are the whole distribution.

    Exclusive rather than inclusive because the pinball loss at `alpha = 0` has zero
    gradient everywhere the residual is positive: the fit would run, converge on nothing,
    and return a bound indistinguishable from a broken one.
    """
    with pytest.raises(ValidationError):
        IntervalFor(model_id=uuid4(), model_version=1, alpha=0.0)
    with pytest.raises(ValidationError):
        IntervalFor(model_id=uuid4(), model_version=1, alpha=1.0)


@pytest.mark.req("FR-200")
def test_a_bound_at_the_median_is_not_a_bound() -> None:
    """`alpha = 0.5` is the median — a central estimate, not a side of an interval.

    Refused at the type because FR-200(iv) allocates exactly one bound per side, and
    a median belongs to neither: admitting it would make "the lower bound" a question the
    lookup cannot answer.
    """
    with pytest.raises(ValidationError, match="0.5"):
        IntervalFor(model_id=uuid4(), model_version=1, alpha=0.5)


@pytest.mark.req("FR-200")
def test_interval_for_is_absent_by_default_and_forbidden_on_a_glm() -> None:
    """A GLM has a covariance matrix; FR-199's route is the GBM's alone.

    `GlmSpec` must not silently accept the field — `extra="forbid"` is what refuses it, and
    this pins that the field was added to the GBM arm and not to the common block.
    """
    gbm = _a_gbm_spec()
    assert gbm.interval_for is None
    with pytest.raises(ValidationError):
        GlmSpec(**{**_a_glm_spec().model_dump(), "interval_for": None})
```

Add to `backend/tests/test_model_specs.py`:

```python
@pytest.mark.req("FR-206")
@pytest.mark.req("FR-200")
def test_the_spec_hash_algorithm_version_moved_with_the_new_field() -> None:
    """FR-206: adding a spec field increments `n` in the same commit as the field.

    Without this the digest of every stored spec silently changes, FR-204's dedup ends
    with no error to see, and the same model is fitted twice under two versions with nothing
    to say why. The assertion is on the constant rather than on a digest because a digest
    test passes just as well after a hand-edit that forgot the constant.
    """
    assert SPEC_HASH_VERSION == 4
    assert spec_hash(_a_gbm_spec()).startswith("v4:sha256:")
    assert not spec_hash_is_current("v3:sha256:" + "0" * 64)


@pytest.mark.req("FR-200")
def test_two_bounds_against_different_central_models_do_not_collide() -> None:
    """The whole reason the link is in the spec rather than beside it.

    Two bounds identical but for the model they bound must hash differently, or
    `reserve_model` returns the first when asked for the second and the second central model
    silently acquires the first one's bound.
    """
    base = _a_gbm_spec()
    left = base.model_copy(update={"interval_for": IntervalFor(
        model_id=UUID(int=1), model_version=7, alpha=0.05)})
    right = base.model_copy(update={"interval_for": IntervalFor(
        model_id=UUID(int=2), model_version=7, alpha=0.05)})
    assert spec_hash(left) != spec_hash(right)
```

- [ ] **Step 2: Run them to verify they fail**

```bash
uv run pytest packages/model-schema/tests/test_modelling.py -k interval -v
uv run pytest backend/tests/test_model_specs.py -k "spec_hash_algorithm or collide" -v
```

Expected: FAIL with `NameError: name 'IntervalFor' is not defined`, and
`assert 3 == 4`.

- [ ] **Step 3: Add `IntervalFor` to `modelling.py`**

Place it immediately before `class GbmSpec` (currently line 956), beside `EarlyStopping`,
which is the other GBM-only sub-model.

```python
class IntervalFor(BaseModel):
    """This model is one side of another model's prediction interval (FR-199).

    **On the spec, so it joins `spec_hash`** (FR-200). FR-137 set the precedent
    for a Model that exists relative to another Model, and the reason is the same one: the
    pairing is part of what this model *is*. Two bounds identical but for the central model
    they bound would otherwise share a digest, and `reserve_model` would hand the second
    caller the first caller's model.

    The central model is named by **id and version**. The id is what the lookup uses; the
    version is what a human reads in a review, where `motor-ad-frequency@7` is recognisable
    and a UUID is not — the same argument `Prediction` carries for holding both.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: UUID
    model_version: int = Field(ge=1)
    #: The quantile this bound estimates. Exclusive at both ends: at `alpha = 0` the pinball
    #: loss has zero gradient wherever the residual is positive, so the fit converges on
    #: nothing and returns a bound that cannot be told from a broken one.
    alpha: float = Field(gt=0.0, lt=1.0)

    @model_validator(mode="after")
    def _the_median_is_not_a_side(self) -> IntervalFor:
        """`alpha = 0.5` is a central estimate, and an interval has no central side.

        FR-200(iv) allocates one bound per side and finds them by comparing `alpha`
        with 0.5. A median bound belongs to neither set, so admitting it would make "the
        lower bound of this model" a question with no answer at exactly the point the
        prediction path asks it.
        """
        if self.alpha == 0.5:
            raise ValueError(
                "alpha=0.5 is the median, not a bound. A paired interval has a lower side "
                "(alpha < 0.5) and an upper side (alpha > 0.5), and the median is neither."
            )
        return self
```

- [ ] **Step 4: Add the field to `GbmSpec`**

Inside `class GbmSpec`, after `backend_params`:

```python
    #: FR-199/200. Set only on a model that *is* a bound; `None` on every other GBM.
    #: In the spec rather than beside it because it changes the model's identity — see
    #: `IntervalFor`.
    interval_for: IntervalFor | None = None
```

- [ ] **Step 5: Re-export and bump the hash version**

In `packages/model-schema/src/model_schema/__init__.py`, add `IntervalFor` to the imports and
to `__all__`, keeping both alphabetical.

In `backend/src/app/platform/modelling.py`, change line 100 and extend the comment above it:

```python
#: `interval_for` moved it `v3 → v4` (2026-08-19, FR-200).
SPEC_HASH_VERSION: Final = 4
```

- [ ] **Step 6: Run the tests to verify they pass**

```bash
uv run pytest packages/model-schema/tests/test_modelling.py backend/tests/test_model_specs.py -q
```

Expected: PASS.

- [ ] **Step 7: Regenerate the contracts**

```bash
uv run python scripts/generate-contracts.py
git diff --stat docs/contracts/schemas/
```

Expected: `model-spec.schema.json` and `model.schema.json` change; nothing else does. **Read
the diff** — `CLAUDE.md` §13 rule 4: a generated artifact matching its source proves neither
is correct. Confirm `interval_for` appears with `model_id`, `model_version` and an `alpha`
carrying `exclusiveMinimum: 0` and `exclusiveMaximum: 1`.

- [ ] **Step 8: Commit**

```bash
git add packages/model-schema backend/src/app/platform/modelling.py \
        backend/tests/test_model_specs.py docs/contracts/schemas
git commit -m "feat(model): FR-200 — interval_for on GbmSpec, spec_hash v4"
```

---

## Task 3: The pairing rules — a bound must match the model it bounds

FR-199: *same Model Family, same dataset version, split and factor set*. Nothing enforces
that yet, and a bound fitted on a different factor set is an interval around a different
model.

> **Ordering note:** this task calls `load_interval_models`, which Task 4 Step 3 writes.
> Implement that step first, or this task lands red.

**Files:**
- Modify: `backend/src/app/platform/modelling.py` (`reserve_model`)
- Modify: `backend/src/app/errors.py:173` area (`MODELLING_ERROR_CODES`)
- Test: `backend/tests/test_paired_quantile_models.py` (create)

**Interfaces:**
- Consumes: `IntervalFor`, `GbmSpec.interval_for` from Task 2; `load_interval_models` from
  Task 4.
- Produces: `_refuse_mismatched_interval_model(session, *, workspace_id, spec) -> None`,
  raising `PlatformError("MODEL_INTERVAL_PAIR_INVALID", ..., 409, ...)`. Called from
  `reserve_model` after `_refuse_unusable_factors`.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_paired_quantile_models.py`:

```python
"""FR-199/200 — paired quantile models, and the four ways a pair can be wrong.

Every test here is a negative one, which is the point (`CLAUDE.md` §13). A bound that agrees
with its central model is a bound; a bound that disagrees is an interval drawn around a model
nobody fitted, and it renders identically.
"""

import pytest

from app.errors import PlatformError


@pytest.mark.req("FR-199")
async def test_a_bound_on_a_different_dataset_version_is_refused(session, workspace) -> None:
    """An interval around a model fitted on other data is not this model's interval.

    It fits, it produces two ordered numbers, and it describes a different population. The
    refusal names the field so the actuary can see which half to change.
    """
    central = await _a_fitted_gbm(session, workspace)
    bound = _a_quantile_spec(central, alpha=0.05).model_copy(
        update={"dataset_version_id": await _another_validated_version(session, workspace)}
    )
    with pytest.raises(PlatformError) as caught:
        await service.reserve_model(
            session, workspace_id=workspace.id, actor=_actor, spec=bound
        )
    assert caught.value.code == "MODEL_INTERVAL_PAIR_INVALID"
    assert "dataset_version_id" in str(caught.value)


@pytest.mark.req("FR-199")
async def test_a_bound_with_a_different_factor_set_is_refused(session, workspace) -> None:
    """Order does not matter and membership does — the comparison is on the set.

    `factors` is a tuple and two specs listing the same factors in a different order are the
    same factor set. Comparing the tuples would refuse a legitimate bound; comparing the sets
    refuses only the ones that differ.
    """
    central = await _a_fitted_gbm(session, workspace)
    bound = _a_quantile_spec(central, alpha=0.05).model_copy(
        update={"factors": central.spec.factors[:-1]}
    )
    with pytest.raises(PlatformError, match="factors"):
        await service.reserve_model(
            session, workspace_id=workspace.id, actor=_actor, spec=bound
        )


@pytest.mark.req("FR-199")
async def test_a_bound_whose_factors_are_reordered_is_accepted(session, workspace) -> None:
    """The other half of the set comparison, so the rule cannot be tightened by accident."""
    central = await _a_fitted_gbm(session, workspace)
    bound = _a_quantile_spec(central, alpha=0.05).model_copy(
        update={"factors": tuple(reversed(central.spec.factors))}
    )
    row, should_fit = await service.reserve_model(
        session, workspace_id=workspace.id, actor=_actor, spec=bound
    )
    assert should_fit


@pytest.mark.req("FR-200")
async def test_a_second_bound_on_the_same_side_is_refused(session, workspace) -> None:
    """FR-200(iv). One lower and one upper, so the response's `level` is unambiguous.

    Two lower bounds at 0.05 and 0.10 both satisfy every other rule, and the prediction path
    would have to choose between them with nothing in the artifact saying which the actuary
    meant.
    """
    central = await _a_fitted_gbm(session, workspace)
    await _fit_bound(session, workspace, central, alpha=0.05)
    with pytest.raises(PlatformError, match="already has a lower bound"):
        await service.reserve_model(
            session, workspace_id=workspace.id, actor=_actor,
            spec=_a_quantile_spec(central, alpha=0.10),
        )


@pytest.mark.req("FR-200")
async def test_a_bound_naming_a_model_that_does_not_exist_is_refused(session, workspace):
    """404-shaped, not 409: the caller named something that is not there.

    Kept in this suite rather than the generic not-found tests because the id arrives inside
    a spec rather than in the path, and a spec field pointing at nothing is the mistake a
    copied-and-edited request makes.
    """
    with pytest.raises(PlatformError) as caught:
        await service.reserve_model(
            session, workspace_id=workspace.id, actor=_actor,
            spec=_a_quantile_spec_naming(UUID(int=999), alpha=0.05),
        )
    assert caught.value.status == 404
```

- [ ] **Step 2: Run them to verify they fail**

```bash
uv run pytest backend/tests/test_paired_quantile_models.py -v
```

Expected: FAIL — `reserve_model` accepts every one of these specs today, so the
`pytest.raises` blocks fail with `DID NOT RAISE`.

- [ ] **Step 3: Register the error code**

In `backend/src/app/errors.py`, add to the `MODELLING_ERROR_CODES` set beside
`MODEL_INTERVAL_UNAVAILABLE`:

```python
        "MODEL_INTERVAL_PAIR_INVALID",
```

A repository invariant test asserts every raised code is registered, so an unregistered code
is a `ValueError: unknown error code` waiting inside the error path.

- [ ] **Step 4: Implement the check**

Add to `backend/src/app/platform/modelling.py`:

```python
async def _refuse_mismatched_interval_model(
    session: AsyncSession, *, workspace_id: UUID, spec: ModelSpec
) -> None:
    """FR-199's "same family, dataset version, split and factor set", enforced.

    A bound that disagrees with its central model on any of these is an interval drawn
    around a different model. It fits without complaint, it produces two ordered numbers,
    and nothing downstream can tell it from a correct one — which is why the refusal is here
    rather than in a reviewer's judgement.

    **Set comparison on `factors`, not tuple comparison.** Two specs listing the same factors
    in a different order describe the same design matrix, and refusing that would refuse a
    legitimate bound for a difference the fit cannot see.
    """
    if not isinstance(spec, GbmSpec) or spec.interval_for is None:
        return

    central = await session.get(ModelRow, spec.interval_for.model_id)
    if central is None or central.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "The model this bound is for does not exist",
            404,
            f"interval_for names model {spec.interval_for.model_id}, which is not in this "
            "workspace.",
        )

    central_spec = MODEL_SPEC_ADAPTER.validate_python(central.spec)
    mismatches = [
        field
        for field, mine, theirs in (
            ("model_family_slug", spec.model_family_slug, central_spec.model_family_slug),
            ("dataset_version_id", spec.dataset_version_id, central_spec.dataset_version_id),
            ("split_ref", spec.split_ref, central_spec.split_ref),
            ("factors", set(spec.factors), set(central_spec.factors)),
        )
        if mine != theirs
    ]
    if mismatches:
        raise PlatformError(
            "MODEL_INTERVAL_PAIR_INVALID",
            "This bound does not match the model it bounds",
            409,
            f"interval_for names {central.model_family_slug}@{central.version}, but the two "
            f"specs disagree on {', '.join(mismatches)} (FR-199). An interval fitted "
            "on a different design is an interval around a different model, and renders "
            "identically to a correct one.",
        )

    side = "lower" if spec.interval_for.alpha < 0.5 else "upper"
    for existing in await load_interval_models(
        session, workspace_id=workspace_id, central_model_id=central.id
    ):
        existing_spec = MODEL_SPEC_ADAPTER.validate_python(existing.spec)
        assert isinstance(existing_spec, GbmSpec) and existing_spec.interval_for is not None
        if (existing_spec.interval_for.alpha < 0.5) == (spec.interval_for.alpha < 0.5):
            raise PlatformError(
                "MODEL_INTERVAL_PAIR_INVALID",
                f"This model already has a {side} bound",
                409,
                f"{central.model_family_slug}@{central.version} already has a {side} bound "
                f"at alpha={existing_spec.interval_for.alpha} "
                f"({existing.model_family_slug}@{existing.version}). FR-200 allows one "
                "per side: the response carries a single `level`, and two bounds on one side "
                "leave nothing to say which pair produced it.",
            )
```

Call it from `reserve_model`, immediately after `_refuse_unusable_factors`:

```python
    await _refuse_mismatched_interval_model(session, workspace_id=workspace_id, spec=spec)
```

- [ ] **Step 5: Run the tests to verify they pass**

```bash
uv run pytest backend/tests/test_paired_quantile_models.py -v
```

Expected: PASS, all five.

- [ ] **Step 6: Prove the check fails on deliberately broken input**

`CLAUDE.md` §13 rule 4. Comment out the `if mismatches:` raise, re-run, and confirm three
tests go red — not one. Restore it. Record the observed failure text in the commit body.

- [ ] **Step 7: Commit**

```bash
git add backend/src/app/platform/modelling.py backend/src/app/errors.py \
        backend/tests/test_paired_quantile_models.py
git commit -m "feat(model): FR-199 — a bound must match the model it bounds"
```

---

## Task 4: Finding the pair, without a sequential scan

**Files:**
- Create: `backend/migrations/versions/<rev>_interval_for_index.py`
- Modify: `backend/src/app/platform/modelling.py` (`load_interval_models`, `__all__`)
- Test: `backend/tests/test_paired_quantile_models.py`

**Interfaces:**
- Consumes: `GbmSpec.interval_for` from Task 2.
- Produces:
  ```python
  async def load_interval_models(
      session: AsyncSession, *, workspace_id: UUID, central_model_id: UUID
  ) -> list[ModelRow]: ...
  ```
  Returns every Model whose `spec.interval_for.model_id` is `central_model_id`, ordered by
  `alpha` ascending, so index 0 is the lower bound where a pair is complete.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.req("FR-199")
async def test_the_bounds_come_back_lower_first(session, workspace) -> None:
    """Ordered by alpha, so a caller reads `[lower, upper]` rather than sorting again.

    Two callers sorting the same list two ways is how a lower bound ends up on the upper
    side of a response — and `PredictedRow` would then refuse to serialise it, turning a
    lookup-order bug into a 500 three layers away from its cause.
    """
    central = await _a_fitted_gbm(session, workspace)
    await _fit_bound(session, workspace, central, alpha=0.95)
    await _fit_bound(session, workspace, central, alpha=0.05)
    found = await service.load_interval_models(
        session, workspace_id=workspace.id, central_model_id=central.id
    )
    alphas = [
        MODEL_SPEC_ADAPTER.validate_python(r.spec).interval_for.alpha for r in found
    ]
    assert alphas == [0.05, 0.95]


@pytest.mark.req("FR-199")
async def test_bounds_do_not_leak_across_workspaces(session, workspace, other_workspace):
    """The lookup is a JSONB predicate, and a JSONB predicate has no tenancy of its own.

    Every other model query in this service filters on `workspace_id`; this one reaches
    models by a field inside a JSON document, which is exactly the shape that forgets to.
    """
    central = await _a_fitted_gbm(session, workspace)
    await _fit_bound(session, other_workspace, central, alpha=0.05)
    assert await service.load_interval_models(
        session, workspace_id=workspace.id, central_model_id=central.id
    ) == []
```

- [ ] **Step 2: Run to verify they fail**

```bash
uv run pytest backend/tests/test_paired_quantile_models.py -k "lower_first or leak" -v
```

Expected: FAIL with `AttributeError: module 'app.platform.modelling' has no attribute
'load_interval_models'`.

- [ ] **Step 3: Implement the lookup**

```python
async def load_interval_models(
    session: AsyncSession, *, workspace_id: UUID, central_model_id: UUID
) -> list[ModelRow]:
    """Every bound fitted for `central_model_id`, lower first (FR-199).

    **Ordered here rather than by the caller.** Two callers sorting the same list two ways is
    how a lower bound reaches the upper side of a response, and `PredictedRow`'s ordering
    validator would then raise three layers from the cause.

    The predicate reads a field inside a JSON document, so `workspace_id` is filtered
    explicitly: unlike a foreign key, a JSONB path carries no tenancy of its own.
    """
    rows = (
        await session.execute(
            select(ModelRow).where(
                ModelRow.workspace_id == workspace_id,
                ModelRow.spec["interval_for"]["model_id"].astext
                == str(central_model_id),
            )
        )
    ).scalars().all()
    return sorted(
        rows,
        key=lambda r: MODEL_SPEC_ADAPTER.validate_python(r.spec).interval_for.alpha,
    )
```

Add `"load_interval_models"` to `__all__`, alphabetically.

- [ ] **Step 4: Write the migration**

```bash
uv run alembic revision -m "interval_for index"
```

In the generated file:

```python
def upgrade() -> None:
    """A functional index on the bound→central link (FR-199).

    Without it, every prediction on a GBM scans every model in the workspace to discover it
    has no bounds — which is the common case, and the one that must stay cheap. Partial on
    `interval_for IS NOT NULL` because almost no model is a bound, so the index stays a few
    rows rather than one entry per model.
    """
    op.execute(
        """
        CREATE INDEX ix_models_interval_for_model_id
            ON models ((spec -> 'interval_for' ->> 'model_id'))
         WHERE spec -> 'interval_for' IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_models_interval_for_model_id")
```

- [ ] **Step 5: Apply and verify the index is used**

```bash
uv run alembic upgrade head
```

Then, against the dev database, confirm the planner uses it rather than assuming so:

```sql
EXPLAIN SELECT * FROM models
 WHERE workspace_id = '...'
   AND (spec -> 'interval_for' ->> 'model_id') = '...';
```

Expected: the plan names `ix_models_interval_for_model_id`. On a table with a handful of rows
Postgres will prefer a sequential scan regardless — that is not a failure; note it and move
on rather than forcing `enable_seqscan=off` into a test.

- [ ] **Step 6: Run the tests to verify they pass**

```bash
uv run pytest backend/tests/test_paired_quantile_models.py -v
```

Expected: PASS, all seven.

- [ ] **Step 7: Commit**

```bash
git add backend/src/app/platform/modelling.py backend/migrations/versions \
        backend/tests/test_paired_quantile_models.py
git commit -m "feat(model): FR-199 — find a model's bounds, lower first"
```

---

## Task 5: Crossing detection, at fit time

FR-199: *crossing quantiles are detected, reported in the diagnostics, and never
silently reordered.* FR-170 computes diagnostics once at fit time, so the detection
happens when the **second** bound of a pair is fitted — the first has no counterpart to cross.

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/predict.py`
- Modify: `packages/model-schema/src/model_schema/diagnostics.py`
- Modify: `packages/model-schema/src/model_schema/__init__.py`
- Modify: `backend/src/app/worker/model_handlers.py`
- Test: `packages/pricing-core/tests/test_quantile_crossing.py` (create)

**Interfaces:**
- Consumes: `IntervalFor` from Task 2, `load_interval_models` from Task 4.
- Produces:
  ```python
  # pricing_core/modelling/predict.py
  def detect_quantile_crossing(
      lower: npt.NDArray[np.float64], upper: npt.NDArray[np.float64]
  ) -> tuple[int, float]: ...   # (rows_crossing, worst_gap)
  ```
  and, in `model-schema`, `QuantileCrossing(counterpart_model_id, rows_checked,
  rows_crossing, worst_gap)` plus `GbmDiagnostics.quantile_crossing: QuantileCrossing | None`.

- [ ] **Step 1: Write the failing tests**

Create `packages/pricing-core/tests/test_quantile_crossing.py`:

```python
"""FR-199's crossing detection, as arithmetic (`pricing-core`, no database)."""

import numpy as np
import pytest

from pricing_core.modelling.predict import detect_quantile_crossing


@pytest.mark.req("FR-199")
def test_an_ordered_pair_does_not_cross() -> None:
    lower = np.array([1.0, 2.0, 3.0])
    upper = np.array([1.5, 2.5, 3.5])
    assert detect_quantile_crossing(lower, upper) == (0, 0.0)


@pytest.mark.req("FR-199")
def test_crossing_is_counted_and_its_worst_gap_reported() -> None:
    """The count says how widespread it is; the gap says how bad the worst case is.

    Both, because they answer different questions and either alone misleads: one crossing row
    out of a million is a curiosity, and one crossing row by a factor of ten is not.
    """
    lower = np.array([1.0, 9.0, 3.0])
    upper = np.array([1.5, 2.5, 3.5])
    rows, gap = detect_quantile_crossing(lower, upper)
    assert rows == 1
    assert gap == pytest.approx(6.5)


@pytest.mark.req("FR-199")
def test_equal_bounds_are_not_crossing() -> None:
    """A zero-width interval is degenerate, not inverted.

    `lower == upper` says the two quantile fits agree exactly at that row, which is unusual
    and not a contradiction. Counting it as crossing would report a defect on every row a
    constant-prediction bound produces.
    """
    assert detect_quantile_crossing(np.array([2.0]), np.array([2.0])) == (0, 0.0)


@pytest.mark.req("FR-199")
def test_it_never_reorders() -> None:
    """The requirement's own word. Detection returns numbers and mutates nothing.

    A helper that quietly swapped the arrays would make every downstream test pass and every
    downstream interval a fiction — the exact failure OQ-574 was decided to avoid.
    """
    lower = np.array([9.0, 1.0])
    upper = np.array([2.0, 5.0])
    detect_quantile_crossing(lower, upper)
    assert lower.tolist() == [9.0, 1.0]
    assert upper.tolist() == [2.0, 5.0]
```

- [ ] **Step 2: Run to verify they fail**

```bash
uv run pytest packages/pricing-core/tests/test_quantile_crossing.py -v
```

Expected: FAIL with `ImportError: cannot import name 'detect_quantile_crossing'`.

- [ ] **Step 3: Implement the detector**

Append to `packages/pricing-core/src/pricing_core/modelling/predict.py`:

```python
def detect_quantile_crossing(
    lower: npt.NDArray[np.float64], upper: npt.NDArray[np.float64]
) -> tuple[int, float]:
    """How often, and how badly, a quantile pair contradicts itself (FR-199).

    Returns `(rows_crossing, worst_gap)`. **It reorders nothing** — that is the requirement's
    own word, and the reason this returns numbers rather than a corrected pair: a reordered
    pair still does not describe one distribution, and hiding that is the failure mode
    OQ-574 was decided to avoid.

    Both figures, because either alone misleads. One crossing row in a million is a
    curiosity; one crossing row by a factor of ten is a bound nobody should quote.

    `lower == upper` is **not** crossing: the two fits agreeing exactly at a row is
    degenerate, not inverted, and counting it would report a defect on every row where a
    bound is constant.
    """
    if lower.shape != upper.shape:
        raise PredictionError(
            "MODEL_INTERVAL_UNAVAILABLE",
            f"the bounds have different lengths ({lower.shape} and {upper.shape}); they "
            "were scored over different row sets and cannot be compared.",
        )
    gaps = lower - upper
    crossing = gaps > 0.0
    return int(crossing.sum()), float(gaps.max()) if crossing.any() else 0.0
```

- [ ] **Step 4: Run to verify they pass**

```bash
uv run pytest packages/pricing-core/tests/test_quantile_crossing.py -v
```

Expected: PASS, all four.

- [ ] **Step 5: Add the contract field**

In `packages/model-schema/src/model_schema/diagnostics.py`, before `class GbmDiagnostics`:

```python
class QuantileCrossing(BaseModel):
    """Whether this bound contradicts its counterpart, over the fit population (FR-199).

    On the **second** bound's diagnostics, because the first has no counterpart to cross and
    FR-170 computes diagnostics once at fit time. `counterpart_model_id` names the model
    it was compared against, so a reader is not left inferring it from the alpha.

    Present only on a model that is a bound; `None` on every other GBM.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    counterpart_model_id: UUID
    rows_checked: int = Field(ge=1)
    rows_crossing: int = Field(ge=0)
    #: The largest `lower - upper` over the crossing rows, on the response scale. `0.0` when
    #: nothing crosses. Reported beside the count because one row crossing by a factor of ten
    #: and a thousand rows crossing in the sixth decimal are different findings.
    worst_gap: float = Field(ge=0.0)

    @model_validator(mode="after")
    def _crossing_rows_are_a_subset_of_the_rows_checked(self) -> QuantileCrossing:
        if self.rows_crossing > self.rows_checked:
            raise ValueError(
                f"{self.rows_crossing} crossing rows out of {self.rows_checked} checked."
            )
        if (self.rows_crossing == 0) != (self.worst_gap == 0.0):
            raise ValueError(
                "rows_crossing and worst_gap disagree: a gap with no crossing rows, or "
                "crossing rows with no gap, is one of the two computed from the wrong array."
            )
        return self
```

Add to `GbmDiagnostics`:

```python
    #: FR-199. Set on the second bound of a pair; `None` on every other model.
    quantile_crossing: QuantileCrossing | None = None
```

Re-export `QuantileCrossing` from `__init__.py`.

- [ ] **Step 6: Wire it into the fit handler**

In `backend/src/app/worker/model_handlers.py`, inside `_fit`, after `computed` is built and
before `Diagnostics(...)` is constructed (around line 336): if the spec is a `GbmSpec` with
`interval_for` set, look for the counterpart via `load_interval_models`, and when one exists,
score both over the fit frame and attach the result.

```python
    # FR-199. Only the *second* bound of a pair has a counterpart to cross; the first
    # is fitted against nothing and carries `quantile_crossing=None`. Scoring the counterpart
    # here costs one extra pass over the fit frame, which is cheap beside the fit that just
    # produced it — and it is the only moment both boosters and the population are in hand.
    if isinstance(spec, GbmSpec) and spec.interval_for is not None:
        computed = await _attach_quantile_crossing(
            computed, spec=spec, result=result, frame=frame, progress=progress,
            workspace_id=workspace_id, model_id=model_id,
        )
```

Implement `_attach_quantile_crossing` beside `_resolve_candidate`, following that function's
pattern exactly: resolve the counterpart's spec, factors, bandings and groupings from ids,
fetch its booster from the blob store, call `score_fitted` for each side, then
`detect_quantile_crossing`. `pricing-core` is handed dataframes and artifacts, never ids
(ADR-703).

- [ ] **Step 7: Add the integration test**

```python
@pytest.mark.req("FR-199")
async def test_the_second_bound_records_whether_it_crosses(session, workspace) -> None:
    """Fitted first, then its counterpart — and only the counterpart carries the finding.

    Asserted on both models, not just the second: a detector that attached the block to
    whichever model it happened to be looking at would pass a test that checked one.
    """
    central = await _a_fitted_gbm(session, workspace)
    lower = await _fit_bound(session, workspace, central, alpha=0.05)
    upper = await _fit_bound(session, workspace, central, alpha=0.95)

    assert (await _diagnostics_for(session, lower)).gbm.quantile_crossing is None
    crossing = (await _diagnostics_for(session, upper)).gbm.quantile_crossing
    assert crossing is not None
    assert crossing.counterpart_model_id == lower.id
    assert crossing.rows_checked > 0
```

- [ ] **Step 8: Run the tests and regenerate the contract**

```bash
uv run pytest packages/pricing-core/tests/test_quantile_crossing.py \
              backend/tests/test_paired_quantile_models.py -q
uv run python scripts/generate-contracts.py
```

Expected: PASS; `diagnostics.schema.json` gains `quantile_crossing`. **Read that diff against
FR-199, not only against the model it was generated from.**

- [ ] **Step 9: Commit**

```bash
git add packages/pricing-core packages/model-schema backend/src/app/worker/model_handlers.py \
        backend/tests/test_paired_quantile_models.py docs/contracts/schemas
git commit -m "feat(model): FR-199 — crossing quantiles are detected, never reordered"
```

---

## Task 6: Prediction consumes the pair — ⚠ needs OQ-588 decided

**Do not start this task until the maintainer has written an acceptance line for OQ-588
into `docs/open-questions.md`.** The steps below assume the recommended answer.

**Files:**
- Modify: `packages/model-schema/src/model_schema/prediction.py`
- Modify: `packages/model-schema/src/model_schema/__init__.py`
- Modify: `backend/src/app/platform/prediction.py` (`_score_gbm`)
- Test: `backend/tests/test_prediction.py`, `backend/tests/test_paired_quantile_models.py`

**Interfaces:**
- Consumes: `load_interval_models` (Task 4), `IntervalFor` (Task 2).
- Produces: `UncertaintyKind.QUANTILE_PAIR_INTERVAL`; `IntervalModels(lower_model_id,
  upper_model_id, lower_alpha, upper_alpha)`; `Uncertainty.interval_models`.

- [ ] **Step 1: Add the enum member and the block**

> **If the maintainer chose differently:** reusing `confidence_interval_mean` deletes this
> step and Step 2's validator change; taking `prediction_interval` renames the member and
> requires FR-196 to gain an addendum (never an edit — `CLAUDE.md` §14). Everything
> below is otherwise unchanged.

In `prediction.py`, add to `UncertaintyKind`:

```python
    #: A paired-quantile interval on `Y` itself (FR-199, OQ-588). **Not**
    #: `confidence_interval_mean`, which covers `E[Y|x]` and is a different and much narrower
    #: claim; **not** FR-196's reserved `prediction_interval`, which names a `φ·V(μ)`
    #: computation over aggregates and would leave that requirement's trigger with no name to
    #: fire into. The value names the *estimator* as well as the quantity, because a reader
    #: comparing a GBM's bound with a GLM's must be able to see they are not the same claim.
    QUANTILE_PAIR_INTERVAL = "quantile_pair_interval"
```

And a new block:

```python
class IntervalModels(BaseModel):
    """Which two Models produced a quantile-pair interval (FR-199).

    Carried on the response because the bounds cost the actuary two extra fits and are
    Models in their own right — a reader who wants to know how the interval was made should
    reach them from the prediction rather than from a query they have to construct.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    lower_model_id: UUID
    upper_model_id: UUID
    lower_alpha: float = Field(gt=0.0, lt=0.5)
    upper_alpha: float = Field(gt=0.5, lt=1.0)
```

Add to `Uncertainty`:

```python
    #: Set exactly when `kind` is `quantile_pair_interval`, by the validator below.
    interval_models: IntervalModels | None = None
```

- [ ] **Step 2: Widen the `Uncertainty` validator**

The current validator requires `basis` for any non-`unavailable` kind. A quantile pair has no
covariance matrix, so `basis` must be **forbidden** for it and `interval_models` **required** —
and the mirror must hold. Restructure `_the_kind_and_its_evidence_agree` into three arms
(`UNAVAILABLE` / `CONFIDENCE_INTERVAL_MEAN` / `QUANTILE_PAIR_INTERVAL`) rather than the
current two, with `level` required by all but the first.

```python
        elif self.kind is UncertaintyKind.QUANTILE_PAIR_INTERVAL:
            if self.basis is not None:
                raise ValueError(
                    f"a quantile-pair interval carries basis={self.basis!r}. "
                    "`UncertaintyBasis` describes a covariance matrix, and a pair of "
                    "quantile fits has none — stating one would claim inference this "
                    "interval did not do."
                )
            if self.interval_models is None:
                raise ValueError(
                    "a quantile-pair interval names no models. The bounds cost two extra "
                    "fits and are Models in their own right; a reader must be able to "
                    "reach them (FR-199)."
                )
```

and, in the `confidence_interval_mean` arm, refuse `interval_models`.

- [ ] **Step 3: Write the failing prediction tests**

```python
@pytest.mark.req("FR-199")
async def test_a_gbm_with_a_complete_approved_pair_returns_an_interval(client, ...):
    """The happy path, and the first time a GBM prediction carries bounds at all."""
    ...
    assert body["uncertainty"]["kind"] == "quantile_pair_interval"
    assert body["uncertainty"]["level"] == pytest.approx(0.90)   # 0.95 − 0.05
    assert body["uncertainty"].get("basis") is None
    assert all(r["lower"] < r["upper"] for r in body["rows"])


@pytest.mark.req("FR-198")
async def test_a_gbm_with_only_one_bound_says_no_interval_models_fitted(client, ...):
    """Half a pair is not a pair, and the reason is the honest one rather than a new code.

    FR-198's vocabulary is closed; a lone bound is the absence of a *pair*, which
    `no_interval_models_fitted` already says.
    """
    assert body["uncertainty"]["reason"] == "no_interval_models_fitted"


@pytest.mark.req("FR-200")
async def test_an_approved_model_whose_bounds_are_only_fitted_says_not_approved(client, ...):
    """FR-200(ii). The first time this reason has ever been reachable.

    An approved model quoting an unreviewed bound puts a reviewed and an unreviewed number
    on one line with nothing distinguishing them.
    """
    assert body["uncertainty"]["reason"] == "interval_models_not_approved"


@pytest.mark.req("FR-200")
async def test_a_superseded_model_reports_its_bounds_stale(client, ...):
    """FR-200(iii), and the fourth reason made reachable.

    `SCOREABLE_MODEL_STATUSES` admits `superseded`, so this model is predictable and its
    bounds are quotable — and quoting them without saying the family has moved on is the
    silence FR-198 exists to refuse.
    """
    assert body["uncertainty"]["reason"] == "interval_models_stale"


@pytest.mark.req("FR-207")
def test_every_unavailable_reason_is_now_reachable() -> None:
    """The staging rule's own check, so the docstring cannot drift back into a claim.

    FR-207 required the unreachable members to be named in place. They are reachable
    now, and this test is what stops the note being removed while a member quietly is not.
    """
    assert _REASONS_RETURNED_BY_THE_PLATFORM == set(UnavailableReason)
```

- [ ] **Step 4: Run to verify they fail**

```bash
uv run pytest backend/tests/test_prediction.py backend/tests/test_paired_quantile_models.py -v
```

Expected: FAIL — `_score_gbm` returns `no_interval_models_fitted` unconditionally today.

- [ ] **Step 5: Rewrite `_score_gbm`'s verdict**

Replace the unconditional `Uncertainty(...)` at the end of `_score_gbm` with the four-way
decision, in this order — **most specific first**, so a superseded model with unapproved
bounds reports staleness rather than approval:

1. Fewer than two bounds, or not one per side → `NO_INTERVAL_MODELS_FITTED`.
2. Central model `superseded` → `INTERVAL_MODELS_STALE` (FR-200 iii).
3. Any bound less advanced than the central model → `INTERVAL_MODELS_NOT_APPROVED`
   (FR-200 ii). Compare on an explicit ordering of `ModelStatus`, not on the enum's
   declaration order — `StrEnum` members compare as strings, and `"approved" < "fitted"`.
4. Otherwise score both bounds and return `QUANTILE_PAIR_INTERVAL` with
   `level = upper_alpha − lower_alpha`.

Update the function's docstring: it currently states that `no_interval_models_fitted` is the
only reachable reason, and that stops being true here. Update
`backend/src/app/platform/prediction.py`'s **module** docstring for the same reason, and
`UnavailableReason`'s docstring in `model-schema` — three places assert the old state and all
three become wrong in this commit.

- [ ] **Step 6: Run to verify they pass**

```bash
uv run pytest backend/tests/test_prediction.py backend/tests/test_paired_quantile_models.py -v
```

Expected: PASS.

- [ ] **Step 7: Prove the ordering matters**

Swap arms 2 and 3, re-run, and confirm `test_a_superseded_model_reports_its_bounds_stale`
goes red. Restore. A four-way branch whose order nothing pins is a branch that will be
reordered by the next person who reads it.

- [ ] **Step 8: Commit**

```bash
git add packages/model-schema backend/src/app/platform/prediction.py backend/tests
git commit -m "feat(model): FR-199 — a GBM can carry an interval, and all four reasons are reachable"
```

---

## Task 7: Crossing at prediction time — the reader is told, not protected

A pair can be ordered over the fit population and cross on a row nobody fitted.
`PredictedRow`'s validator **raises** on `lower > upper`, so this path currently turns a real
finding into a 500.

**Files:**
- Modify: `backend/src/app/platform/prediction.py`
- Test: `backend/tests/test_paired_quantile_models.py`

**Interfaces:**
- Consumes: `detect_quantile_crossing` (Task 5), the `_score_gbm` verdict (Task 6).
- Produces: no new type. A crossing request is refused with
  `PlatformError("MODEL_INTERVAL_UNAVAILABLE", ..., 409, ...)`.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.req("FR-199")
async def test_a_crossing_row_is_refused_rather_than_reordered(client, ...) -> None:
    """"Never silently reordered" — and never silently dropped either.

    The rows that cross are the rows where the pair does not describe one distribution, and
    they are exactly the rows an actuary needs to see. A 409 names them; swapping the bounds
    would return two plausible numbers that mean nothing.
    """
    response = await client.post(f"/api/v1/models/{central.id}/predict", json={"rows": rows})
    assert response.status_code == 409
    problem = response.json()
    assert problem["code"] == "MODEL_INTERVAL_UNAVAILABLE"
    assert "cross" in problem["detail"]
    assert "2 of 5 rows" in problem["detail"]


@pytest.mark.req("FR-199")
async def test_a_non_crossing_request_on_the_same_pair_still_succeeds(client, ...) -> None:
    """The refusal is per request, not per pair.

    A pair that crosses somewhere in covariate space is still usable everywhere it does not,
    and disabling it wholesale would discard a bound over rows nobody asked about.
    """
    assert (await client.post(..., json={"rows": safe_rows})).status_code == 200
```

- [ ] **Step 2: Run to verify it fails**

Expected: a **500**, from `PredictedRow`'s `interval bounds are reversed` validator — which is
the defect this task exists to fix. Capture the traceback in the commit body: it is the
evidence that the validator was doing its job and the caller was not.

- [ ] **Step 3: Refuse the request, in `_score_gbm`, before `Prediction` is built**

> **If the maintainer chose differently on OQ-588:** the shape of this refusal does not
> change, only the `kind` on the successful path above it.

Call `detect_quantile_crossing` on the two scored arrays. When `rows_crossing > 0`:

```python
        raise PlatformError(
            "MODEL_INTERVAL_UNAVAILABLE",
            "The interval models cross on these rows",
            409,
            f"{rows_crossing} of {frame.height} rows have a lower bound above their upper "
            f"bound (worst gap {worst_gap:.4g}). FR-199: a crossing pair does not "
            "describe one distribution, and the bounds are reported as computed or not at "
            "all — reordering them would return two plausible numbers that mean nothing. "
            f"The pair's fit-time crossing is on {upper_model.model_family_slug}@"
            f"{upper_model.version}'s diagnostics.",
        )
```

409 rather than 422, matching `_unscoreable`: the request is well formed and the model is
real, and what fails is the pairing of the two.

- [ ] **Step 4: Run to verify both pass**

```bash
uv run pytest backend/tests/test_paired_quantile_models.py -k cross -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/platform/prediction.py backend/tests/test_paired_quantile_models.py
git commit -m "fix(model): FR-199 — a crossing pair is refused, not reordered into a 500"
```

---

## Task 8: The gate, the audit, and the slice record

**Files:**
- Modify: `docs/roadmap.md` (WK-661's row; a new slice record in §6)
- Modify: `docs/skills-map.md` **only if** a tech dependency changed (it should not have)
- Verify: `docs/contracts/schemas/*` regenerated, never hand-edited

- [ ] **Step 1: Run the whole gate, both halves**

Use the block under **Global Constraints**. Read each command's own exit code — `cmd | tail -1
&& echo ok` reports `tail`'s and has produced a false clean here more than once.

- [ ] **Step 2: Check the requirement audit moved the way you expect**

```bash
uv run python scripts/req-coverage.py
uv run python scripts/scope-audit.py MODEL --endpoints
```

Expected: the specified count rises by **1** (FR-200) and the marked count rises by
**1** or more. `FR-199` must leave `--endpoints`' unevidenced list. If it has not, a test
claims it without exercising it — a marker is a claim, not a proof (`CLAUDE.md` §13).

- [ ] **Step 3: Confirm the demo guide still derives**

```bash
uv run pytest backend/tests/test_demo_guide.py
```

FR-409 makes it derived, not written, so there is nothing to update — but check that it
still derives. Expected: 11 passed.

- [ ] **Step 4: Write the slice record in `docs/roadmap.md`**

Follow the shape of the `top_levels` and profile-contract records: what was done, **what the
code said that the requirement did not**, the gate numbers, enforcement proven against broken
input, what was raised rather than silently picked, and where the next session starts.

State explicitly, because §13 rule 6 requires the "not delivered" half:

- **No frontend.** `02` §5.3's model-detail view is WK-664's; nothing renders a GBM interval, so
  the capability is reachable only over the API. Owner: **WK-664**.
- **`quantile_crossing` is computed and rendered nowhere.** Same owner, same reason.
- **OQ-588's answer, with its date**, and — if the maintainer chose the third member —
  that FR-196 was amended by **addendum**, never edited (`CLAUDE.md` §14).
- **The two interpretation choices** FR-200 fixed, named as choices with alternatives,
  so a later reader can see they were decided rather than assumed.

- [ ] **Step 5: Add the slice to WK-661's row**

WK-661's row in the Phase 1b table currently ends "…the profile contract, and `top_levels`'
exposure per level". Append ", and paired quantile models". Do not renumber or restructure the
row.

- [ ] **Step 6: Final audit and push**

```bash
python3 scripts/audit-docs.py
uv run python scripts/generate-contracts.py --check
git add docs/roadmap.md
git commit -m "docs(model): the paired-quantile slice record"
git push --force-with-lease -u origin <branch>
gh pr create --title "feat(model): FR-199 — paired quantile models" --body "..."
```

`gh pr checks` answers *"Resource not accessible by personal access token"* here — that is a
scope limit, not a red build. Use `gh pr view <n> --json mergeStateStatus`: `CLEAN` means
checks passed, `UNSTABLE` means pending or failing.

- [ ] **Step 7: After merge, verify the branch by content before deleting it**

```bash
git fetch origin
git diff --stat origin/main <branch>
```

Expected: empty. A squash-merged branch looks unmerged to every tool, and `git branch -d`
refuses even when the work is fully merged.

---

## Self-Review

**1. Spec coverage.** FR-199's four clauses map to tasks: *"each bound is a Model in its
own right, same family / dataset version / split / factor set"* → Task 3; *"carrying
`interval_for`, which names the central Model version and the alpha"* → Task 2; *"crossing
quantiles are detected, reported in the diagnostics, and never silently reordered"* → Tasks 5
and 7; *"the 2–3× fit cost is a choice the actuary makes and can see"* → Task 6's
`IntervalModels` block on the response. FR-198's three reasons → Task 6 Step 5.
FR-206's bump → Task 2. FR-207's staging rule → Task 1 Step 5 and Task 6 Step 3's
reachability test.

**Gap, stated rather than closed:** FR-199 says the cost "is a choice the actuary makes
**and can see**". Over the API they can; on a screen they cannot, because no screen exists.
That is WK-664's and Task 8 Step 4 records it as an owner rather than as done.

**2. Placeholders.** Task 6 Step 3 and Task 7 Step 1 use `...` inside test bodies for fixture
setup that follows `backend/tests/test_prediction.py`'s existing pattern exactly; the
assertions — which are the part a reviewer gates on — are complete. Task 5 Step 6 describes
`_attach_quantile_crossing` by the function it mirrors (`_resolve_candidate`) rather than
transcribing it, because that function is 40 lines of id-resolution this task does not change.

**3. Type consistency.** `IntervalFor` (Task 2) is referenced by Tasks 3, 4, 5, 6.
`load_interval_models` (Task 4) is called by Tasks 3 and 6 — **Task 3 depends on Task 4's
function**, called out at the head of Task 3 and again in its Interfaces block.
`detect_quantile_crossing` returns `(int, float)` in Task 5 and is unpacked as
`rows_crossing, worst_gap` in Task 7. `QuantileCrossing.counterpart_model_id` is asserted in
Task 5 Step 7 under that exact name. `UncertaintyKind.QUANTILE_PAIR_INTERVAL` serialises as
`"quantile_pair_interval"`, which is what Task 6 Step 3 asserts.

**One ordering hazard, restated because it is easy to miss:** implement **Task 4 Step 3 before
Task 3 Step 4**, or Task 3 lands red.
