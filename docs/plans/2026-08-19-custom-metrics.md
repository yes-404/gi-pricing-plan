# Custom Metrics (FR-MODEL-45) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Custom Metric artifact and its lifecycle so that `GbmSpec.eval_metrics` stops being a field nothing reads, and a GBM fitted under a custom objective can early-stop on a metric that means what it names.

**Architecture:** A `CustomMetric` is a named, versioned, reusable artifact parallel to `CustomObjective` — same lifecycle, same certification gate before submission, but no gradient, no hessian and no hessian strategy, because a metric only reports. In Phase 1 it is templates-only (OQ-MODEL-1's rule applied to metrics), and a metric template *is* an objective template's loss evaluated as a summary — so `pricing-core`'s existing `_TEMPLATES` registry is the single source of the arithmetic, and no loss is written twice. The backend resolves `custom_metric:<slug>@<version>` and hands `pricing-core` the artifact (ADR-0001); `pricing-core` never resolves a reference.

**Tech Stack:** Python 3.12, Pydantic v2 (`model-schema`), NumPy (`pricing-core`), XGBoost + LightGBM `feval`, FastAPI + SQLAlchemy 2.x async + Alembic (backend), pytest + hypothesis.

**Spec:** `docs/specs/02-modelling.md` — FR-MODEL-45 (§3.7), §4.4's `eval_metrics` block, §4.5's template catalogue, §4.7's `ObjectiveCertificate`, §5.1's endpoint table. Read all five before Task 1; the plan argues from them.

---

## Global Constraints

Copied verbatim from `CLAUDE.md` and the specs. Every task's requirements implicitly include this section.

- **`pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis dependencies.** Enforced by `.importlinter`; `uv run lint-imports` is part of the gate.
- **ADR-0001: `pricing-core` is handed the artifact and never resolves a reference.** A function that takes a `custom_metric:` string and returns an artifact belongs in `backend/`, never in `packages/`.
- **ADR-0002: `model-schema` is the single source of truth for shapes crossing a boundary.** Nobody hand-writes a shape that already exists there — not the backend, not the frontend, not a test fixture.
- **Requirement IDs are permanent.** Never renumber. Append only. **The current maximum is `FR-MODEL-102`** — find the maximum, not the last id you read; `02`'s requirement table is not in numeric order.
- **Artifacts are immutable once fitted/approved.** A new definition is a new version, never an edit.
- **`ruff` line length 100. `mypy --strict` on `packages/`.** Both are gate steps.
- **Every test carries `@pytest.mark.req("FR-MODEL-N")`** naming the requirement it satisfies. `req-coverage.py` fails on a marker naming a requirement that does not exist, so Task 1 must land before any test names a new id.
- **A negative test for every invariant introduced.** For a governed system the suite must prove the wrong thing *cannot* happen, not merely that the right thing can.
- **No pandas.** Polars and NumPy only.
- **Money is integer minor units or Decimal** — not reached by this slice, but do not introduce a float where a Decimal belongs.

### Environment

```bash
uv sync --all-packages --dev                 # --all-packages is not optional
docker compose -f deploy/docker-compose.yml up -d --wait
export GIP_TEST_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
export GIP_DATABASE_URL="$GIP_TEST_DATABASE_URL"
uv run alembic upgrade head
```

Without the DSN roughly 90 tests skip **silently**. LightGBM needs `libgomp1` (`sudo apt-get install -y libgomp1`) — a fresh box hits it as a collection error with no obvious link to the change. `psql` is not installed; reach the database with `docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -c '…'`.

**Never nest `database.unit_of_work()`.** Each takes its own connection, so an inner one opened inside an outer one deadlocks against the pool rather than failing — the run hangs with no output and no traceback.

---

## DECISION GATE — **ANSWERED 2026-08-19**

> **Maintainer acceptance, 2026-08-19: all three recommendations accepted as written** —
> DG-1 (a) a reduced certificate sharing §4.7's vocabulary, DG-2 (a) a metric names an
> `ObjectiveTemplate` and reuses its loss, DG-3 (a) all six endpoints with the five missing
> rows appended to §5.1. Task 1 records these as `OQ-MODEL-18/19/20`, decided, following the
> OQ-MODEL-16 precedent. Execution may begin.


`CLAUDE.md` §0: *a design choice the specs leave open is recorded with options and a recommendation, never silently picked.* FR-MODEL-45 is one sentence — *"Custom eval metrics (`feval`) follow the same lifecycle and grammar as objectives, declared separately so that a metric can be reused across objectives"* — and three things it does not say decide the shape of this slice. **Do not start Task 1 until the maintainer has answered all three.** Each becomes an `OQ-MODEL-` entry recorded as decided, following the OQ-MODEL-16 precedent (raised and decided the same day, then specified).

### DG-1 — What does a Custom Metric's certificate check?

§4.7's `ObjectiveCertificate` is built around derivatives: `analytic_vs_numeric_gradient`, `analytic_vs_numeric_hessian`, `convexity`, `branch_discontinuity`. **A metric has no gradient and no hessian**, so four of the nine checks are undefined for it, not merely uninteresting.

- **(a) A reduced certificate, sharing the check vocabulary.** `finiteness`, `direction_holds`, `scale_behaviour`, `smoke_evaluation`. Reuses `CertificateCheck`, `CheckStatus`, `SamplingSpec`, `CertificateOutcome` and `CertificateResult.outcome_of` verbatim — no shape defined twice — and the derivative checks are simply **absent** rather than recorded as `not_applicable`.
- **(b) No certificate; the lifecycle skips `certified`** (`draft → review → approved → deprecated`). Cheapest, and arguable on the grounds that a metric cannot mis-fit a model.
- **(c) The full `ObjectiveCertificate` with derivative checks marked `not_applicable`.** Keeps one type, at the cost of a certificate whose majority of rows say "does not apply".

**Recommendation: (a).** (b)'s premise is false in the case this slice exists to serve — a metric that early-stops a fit *decides when boosting halts*, so it changes the model just as surely as the objective does, and FR-MODEL-42's argument for certifying an objective applies unchanged. (c) makes the common case unreadable to buy a type nobody asked for; `CheckStatus` would also need a fifth member meaning "this question is not askable here", which is neither `warn` nor `pass`.

### DG-2 — Where does a Phase-1 metric's arithmetic come from?

Phase 1 is templates-only for objectives (OQ-MODEL-1, decided 2026-08-15). By symmetry a metric is templates-only too — but there is no metric catalogue, and `02` §4.4's example names `custom_metric:capped-gamma-nll@2`, which is an *objective* template's loss.

- **(a) A metric names an `ObjectiveTemplate` and its params, and is that template's loss evaluated as an exposure-weighted mean.** `pricing-core`'s `_TEMPLATES` registry already holds every loss; the metric path reuses it and writes no arithmetic of its own.
- **(b) A separate `MetricTemplate` catalogue** with its own entries (Gini, lift, deviance, …).
- **(c) Defer entirely to Phase 2 with expressions**, building only the artifact and its endpoints now.

**Recommendation: (a).** It is the DRY answer and it is what the spec's own example implies. (b) is a second catalogue to maintain, and the metrics an actuary most wants early stopping on *are* the loss functions — a Gini or a lift curve is a diagnostic (FR-MODEL-50, already built), not an early-stopping signal. (c) leaves `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` in place, which is the refusal this slice exists to retire.

### DG-3 — How many endpoints?

§5.1 declares exactly one: `POST /api/v1/custom-metrics`. FR-MODEL-45 says "the same lifecycle", and that lifecycle needs certification, submission and readback.

- **(a) Build the full parallel set and append the five missing rows to §5.1** — `GET /{id}`, `POST /{id}/certify`, `GET /{id}/certificate`, `POST /{id}/submit`, `GET /{id}/usage`.
- **(b) `POST` + `GET /{id}` only**, deferring certification and submission.
- **(c) `POST` only, exactly as declared.**

**Recommendation: (a).** (c) reproduces precisely the defect FR-MODEL-95 was raised to fix for objectives eleven days ago: §5.1 declared five write endpoints and no way to read what they wrote, and an approver who cannot fetch the certificate is being asked to approve a verdict they cannot see. Building the same gap knowingly, in the same module, is worse than having built it by accident the first time. (b) leaves a metric permanently in `draft`, and `FITTABLE_METRIC_STATUSES` excludes `draft` — so under (b) no metric could ever be used, which makes the slice inert.

**Cost if the gate is answered differently:** Tasks 2, 3 and 5 change shape. Tasks 4, 6 and 7 do not — the table, the fit-path wiring and the gate are the same whichever way the three land.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `docs/specs/02-modelling.md` | FR-MODEL-103…108, §4.13's contract, §4.7's metric addendum, §5.1's rows | 1 |
| `docs/open-questions.md` | OQ-MODEL-18/19/20 recorded as decided | 1 |
| `packages/model-schema/src/model_schema/metrics.py` | **Create.** `CustomMetric`, `MetricStatus`, `MetricDirection`, `MetricCertificate`, the transition map | 2 |
| `packages/model-schema/src/model_schema/__init__.py` | Re-export the new shapes | 2 |
| `packages/pricing-core/src/pricing_core/modelling/objectives.py` | **Modify.** One public accessor, `template_loss`, so the metric path reuses `_TEMPLATES` | 3 |
| `packages/pricing-core/src/pricing_core/modelling/metrics.py` | **Create.** `evaluate_metric`, `certify_metric` | 3 |
| `backend/migrations/versions/<rev>_custom_metrics.py` | **Create.** Table, unique constraint, immutability trigger | 4 |
| `backend/src/app/db/models.py` | **Modify.** `CustomMetricRow`, `MetricCertificateRow` | 4 |
| `backend/src/app/platform/metrics.py` | **Create.** Service: create, resolve_ref, certify, submit, usage | 5 |
| `backend/src/app/api/custom_metrics.py` | **Create.** The six routes | 5 |
| `backend/src/app/errors.py` | **Modify.** Three metric error codes | 5 |
| `backend/src/app/main.py` | **Modify.** Register the router | 5 |
| `packages/pricing-core/src/pricing_core/modelling/gbm.py` | **Modify.** Honour `eval_metrics`; narrow the early-stopping refusal | 6 |
| `backend/src/app/worker/model_handlers.py` | **Modify.** Resolve `custom_metric:` refs before the fit | 6 |
| `docs/roadmap.md` | The slice record | 7 |

Metrics live in their own module rather than beside `CustomObjective` because the two artifacts share *vocabulary* (`Applicability`, `CertificateCheck`, `ObjectiveTemplate`) but not *shape* — a metric has no `hessian_strategy` and no `hessian_min`, and a single class carrying fields meaningful for only one of its two uses is the shape-defined-twice problem wearing a different hat.

---

### Task 1: The specification

**Files:**
- Modify: `docs/specs/02-modelling.md` — §3.7 requirement table, §4.7, §4.13 (new), §5.1
- Modify: `docs/open-questions.md`
- Test: none. `python3 scripts/audit-docs.py` is the check.

**Interfaces:**
- Consumes: the decision gate's three answers.
- Produces: **FR-MODEL-103, 104, 105, 106, 107, 108** — the ids every later task's `@pytest.mark.req` names. This task must land first: `req-coverage.py` fails on a marker naming a requirement that does not exist.

- [ ] **Step 1: Confirm the maximum requirement id before appending**

Run: `grep -oE 'FR-MODEL-[0-9]+' docs/specs/02-modelling.md | sort -t- -k3 -n | tail -1`

Expected: `FR-MODEL-102`. If it prints anything higher, **stop and renumber this plan's new ids upward** — do not reuse an id. `02`'s table is not in numeric order, so the last row you read is not the maximum.

- [ ] **Step 2: Append the six requirements to §3.7's table**

Add these rows immediately after FR-MODEL-45's row. Keep the existing cell structure — a pipe inside a code span splits a table row, so escape any as `\|`.

```markdown
| **FR-MODEL-103** | A **Custom Metric** is its own versioned artifact (`custom_metric:<slug>@<version>`), declared separately from objectives so one metric can be evaluated across many. In Phase 1 it is templates-only, on OQ-MODEL-1's rule: a metric names an `ObjectiveTemplate` and its parameters, and its value is that template's loss evaluated as an exposure-weighted mean. It carries no `hessian_strategy` and no `hessian_min` — a metric is never differentiated, and a field that is structurally meaningless is worse than an absent one. |
| **FR-MODEL-104** | A Custom Metric declares its `direction` — `lower_is_better` or `higher_is_better` — and early stopping reads it rather than inferring one. A metric whose direction is guessed stops the fit at the wrong round in exactly half of cases, and produces a fitted model rather than an error. |
| **FR-MODEL-105** | A Custom Metric carries a `MetricCertificate` before submission, on FR-MODEL-42's argument: a metric that early-stops a fit decides when boosting halts and therefore changes the model. Its checks are `finiteness`, `direction_holds`, `scale_behaviour` and `smoke_evaluation`. §4.7's derivative and convexity checks are **absent, not `not_applicable`** — a metric has no gradient or hessian to compare, so the question is not askable rather than unanswered. The check vocabulary (`CheckStatus`, `SamplingSpec`, `CertificateOutcome`, and `CertificateResult.outcome_of`'s derivation of `overall`) is shared with §4.7 unchanged. |
| **FR-MODEL-106** | `GbmSpec.eval_metrics` is **honoured**: `kind: builtin` names are passed to the backend's own metric vocabulary, and `kind: custom` refs are resolved by the backend and handed to `pricing-core` as artifacts (ADR-0001). A ref that does not resolve, names a metric whose applicability excludes the spec's response or backend, or names one whose status is outside `FITTABLE_METRIC_STATUSES`, refuses the fit before any boosting round. *(Recorded 2026-08-19: the field was declared from Phase 0 and read by nothing — a spec accepted, silently ignored, and reported to the caller as configured.)* |
| **FR-MODEL-107** | Early stopping on a **Custom Metric** is supported under a custom objective. `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` narrows to its true scope: a **builtin** metric under a callable objective, where both backends hand the metric the raw score rather than the transformed prediction, so the metric it stops on is not the metric it names. |
| **FR-MODEL-108** | A Custom Metric is readable and governable over the API: create, read, certify, read the certificate, submit for approval, and list usage — FR-MODEL-95's argument applied to metrics, since an approver who cannot fetch the certificate is being asked to approve a verdict they cannot see. |
```

- [ ] **Step 3: Add §4.13, the `CustomMetric` contract**

Insert after §4.12. Use the next free section number — check with `grep -n '^### 4\.' docs/specs/02-modelling.md` and use the successor of the highest, not 4.13 if 4.13 is taken.

````markdown
### 4.13 `CustomMetric`

```json
{
  "id": "uuid", "slug": "capped-gamma-nll", "version": 2,
  "kind": "template", "template": "capped_gamma",
  "params": {"cap": 250000.0},
  "applicability": {"responses": ["claim_severity"], "backends": ["xgboost", "lightgbm"],
                    "offset_required": false, "y_domain": {"min": 0.0}},
  "direction": "lower_is_better",
  "status": "approved",
  "certificate_id": "uuid", "approval_request_id": "uuid",
  "description": "Gamma NLL with losses capped at 250k, for early stopping on large-loss-heavy severity fits"
}
```

**Invariants.** `template` is required while `kind` is `template`, and Phase 1 admits no
other kind (FR-MODEL-75's rule, applied to metrics). `params` must be exactly the named
template's own parameters — an unknown key is refused rather than ignored, because a
misspelled `cap` that is silently dropped produces an uncapped metric under a name that
says capped. A status past `draft` requires a `certificate_id` (FR-MODEL-105). `direction`
has no default (FR-MODEL-104).

**Why the shape is not `CustomObjective`'s.** No `hessian_strategy`, no `hessian_min`: both
describe what happens where the curvature is negative, and a metric is never
differentiated. `Applicability`, `ObjectiveTemplate`, `TemplateParameter` and `YDomain` are
imported from §4.5 rather than restated — the same catalogue, read two ways.
````

- [ ] **Step 4: Add the `MetricCertificate` addendum to §4.7**

Append to §4.7, after the existing amendment block:

```markdown
> **`MetricCertificate` (FR-MODEL-105), added 2026-08-19.** Same two-object split as
> `ObjectiveCertificate` and for the same ADR-0001 reason: `certify_metric` computes a
> `CertificateResult` in `pricing-core`, which may not allocate an id, read a clock or know
> a Job exists, and the backend stamps `id`, `custom_metric_id`, `metric_version`,
> `certified_at` and `job_id` around it. The four checks:
>
> * **`finiteness`** — no NaN or inf over the sampled `(y, f, w)` domain, the same check
>   §4.7 already runs for objectives.
> * **`direction_holds`** — the metric is better at `f = log(y)` than at a perturbed `f`, in
>   the direction the metric declares (FR-MODEL-104). This is the metric's analogue of
>   `minimum_at_truth`, and it is the check that catches a `direction` declared backwards —
>   the defect that silently halves the value of early stopping.
> * **`scale_behaviour`** — how the value moves with the magnitude of `y`, reported so a
>   reader can tell a metric that spans six orders from one that does not.
> * **`smoke_evaluation`** — on synthetic data whose answer is computable by hand, the
>   metric returns that value within tolerance.
>
> `overall` is derived by the same `CertificateResult.outcome_of` and never supplied.
```

- [ ] **Step 5: Add the endpoint rows to §5.1, and correct the existing one**

Replace the existing `POST /api/v1/custom-metrics` row (it currently ends *"— **not built**, see the amendment below"*) and add the rest:

```markdown
| `POST` | `/api/v1/custom-metrics` | **201** Create → `draft` (FR-MODEL-45, FR-MODEL-103) |
| `GET` | `/api/v1/custom-metrics/{id}` | The metric, its status and its certificate outcome (FR-MODEL-108) |
| `POST` | `/api/v1/custom-metrics/{id}/certify` | **202** Run §4.7's metric checks (FR-MODEL-105) |
| `GET` | `/api/v1/custom-metrics/{id}/certificate` | The latest `MetricCertificate` for that version (FR-MODEL-108) |
| `POST` | `/api/v1/custom-metrics/{id}/submit` | Submit for approval (FR-MODEL-45's lifecycle) |
| `GET` | `/api/v1/custom-metrics/{id}/usage` | Blast radius: models using this metric version (FR-MODEL-108) |
```

Then find the amendment block that says `POST /custom-metrics` is deferred (`grep -n 'custom-metrics' docs/specs/02-modelling.md`) and **strike it through with a dated note rather than deleting it** — the repository's established pattern, as FR-MODEL-57's row uses:

```markdown
> * ~~**`POST /custom-metrics` (FR-MODEL-45) is not built, and is deferred to Phase 1b with
>   this slice.**~~ **Built 2026-08-19.** The reasoning below held exactly as written — a
>   custom metric does not gate the fitting path — and it stopped holding when early
>   stopping under a custom objective turned out to need one (FR-MODEL-107).
```

- [ ] **Step 6: Record the three gate decisions in `docs/open-questions.md`**

Add three rows as **decided**, each with its options and the recommendation that was taken, following the OQ-MODEL-16 precedent. Use the next free `OQ-MODEL-` numbers — check with `grep -oE 'OQ-MODEL-[0-9]+' docs/open-questions.md | sort -t- -k3 -n | tail -1` (expected maximum: `OQ-MODEL-17`). Every row needs an owner and a recognised status column, which `audit-docs.py` checks.

- [ ] **Step 7: Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: `All checks passed.`, and the requirement count rises **483 → 489**. If a table row fails a cell count, look for a `|` inside a code span.

- [ ] **Step 8: Commit**

```bash
git add docs/specs/02-modelling.md docs/open-questions.md
git commit -m "docs(model): FR-MODEL-103..108 — the Custom Metric artifact and its lifecycle"
```

---

### Task 2: `CustomMetric` in model-schema

**Files:**
- Create: `packages/model-schema/src/model_schema/metrics.py`
- Modify: `packages/model-schema/src/model_schema/__init__.py`
- Test: `packages/model-schema/tests/test_metrics.py`

**Interfaces:**
- Consumes: from Task 1, the ids FR-MODEL-103/104/105. From the existing `objectives.py`: `Applicability`, `ObjectiveKind`, `ObjectiveTemplate`, `TEMPLATE_PARAMETERS`, `CertificateCheck`, `CertificateResult`, `SamplingSpec`.
- Produces: `CustomMetric`, `MetricStatus`, `MetricDirection`, `MetricCertificate`, `VALID_METRIC_TRANSITIONS`, `FITTABLE_METRIC_STATUSES`. Tasks 3, 4, 5 and 6 all import these names.

- [ ] **Step 1: Read the shapes you are paralleling**

Run: `sed -n '133,175p;287,330p;434,552p' packages/model-schema/src/model_schema/objectives.py`

You are reading `ObjectiveStatus` + `VALID_OBJECTIVE_TRANSITIONS` + `FITTABLE_OBJECTIVE_STATUSES`, `Applicability`, and `CustomObjective` with its four validators. Your class mirrors the first, third and fourth; it does **not** get `hessian_strategy` or `hessian_min`.

- [ ] **Step 2: Write the failing tests**

Create `packages/model-schema/tests/test_metrics.py`:

```python
"""FR-MODEL-103/104/105 — the Custom Metric artifact."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from model_schema.metrics import (
    FITTABLE_METRIC_STATUSES,
    VALID_METRIC_TRANSITIONS,
    CustomMetric,
    MetricDirection,
    MetricStatus,
)
from model_schema.objectives import Applicability, ObjectiveKind, ObjectiveTemplate, YDomain


def _applicability() -> Applicability:
    return Applicability(
        responses=("claim_severity",),
        backends=("xgboost",),
        offset_required=False,
        y_domain=YDomain(min=0.0),
    )


def _metric(**overrides: object) -> CustomMetric:
    kwargs: dict[str, object] = {
        "id": uuid.uuid4(),
        "slug": "capped-gamma-nll",
        "version": 2,
        "template": ObjectiveTemplate.CAPPED_GAMMA,
        "params": {"cap": 250000.0},
        "applicability": _applicability(),
        "direction": MetricDirection.LOWER_IS_BETTER,
    }
    kwargs.update(overrides)
    return CustomMetric(**kwargs)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-103")
def test_a_template_metric_is_constructible() -> None:
    metric = _metric()
    assert metric.kind is ObjectiveKind.TEMPLATE
    assert metric.status is MetricStatus.DRAFT
    assert metric.certificate_id is None


@pytest.mark.req("FR-MODEL-103")
def test_a_metric_carries_no_hessian_fields() -> None:
    """A metric is never differentiated, so the fields cannot be set even by mistake."""
    assert "hessian_strategy" not in CustomMetric.model_fields
    assert "hessian_min" not in CustomMetric.model_fields
    with pytest.raises(ValidationError):
        _metric(hessian_strategy="clip_to_min")


@pytest.mark.req("FR-MODEL-103")
def test_an_unknown_parameter_is_refused_not_ignored() -> None:
    """A misspelled `cap` silently dropped is an uncapped metric named capped."""
    with pytest.raises(ValidationError, match="cap"):
        _metric(params={"capp": 250000.0})


@pytest.mark.req("FR-MODEL-103")
def test_phase_1_admits_no_expression_metric() -> None:
    with pytest.raises(ValidationError, match="template"):
        _metric(kind=ObjectiveKind.EXPRESSION, template=None)


@pytest.mark.req("FR-MODEL-104")
def test_direction_has_no_default() -> None:
    """A guessed direction stops the fit at the wrong round in half of cases."""
    assert CustomMetric.model_fields["direction"].is_required()


@pytest.mark.req("FR-MODEL-105")
def test_a_status_past_draft_needs_a_certificate() -> None:
    with pytest.raises(ValidationError, match="certificate"):
        _metric(status=MetricStatus.CERTIFIED, certificate_id=None)


@pytest.mark.req("FR-MODEL-105")
def test_draft_is_not_fittable_and_certified_is() -> None:
    """A draft metric has no certificate, so its behaviour is unproven."""
    assert MetricStatus.DRAFT not in FITTABLE_METRIC_STATUSES
    assert MetricStatus.CERTIFIED in FITTABLE_METRIC_STATUSES
    assert MetricStatus.DEPRECATED not in FITTABLE_METRIC_STATUSES


@pytest.mark.req("FR-MODEL-105")
def test_the_lifecycle_has_no_edge_out_of_deprecated() -> None:
    assert VALID_METRIC_TRANSITIONS[MetricStatus.DEPRECATED] == frozenset()
    assert MetricStatus.CERTIFIED in VALID_METRIC_TRANSITIONS[MetricStatus.REVIEW]
    assert MetricStatus.DRAFT not in VALID_METRIC_TRANSITIONS[MetricStatus.REVIEW]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest packages/model-schema/tests/test_metrics.py -q`
Expected: collection error — `ModuleNotFoundError: No module named 'model_schema.metrics'`.

- [ ] **Step 4: Write the implementation**

Create `packages/model-schema/src/model_schema/metrics.py`:

```python
"""Custom eval metrics — FR-MODEL-45, FR-MODEL-103/104/105, `02` §4.13.

Parallel to `CustomObjective` and deliberately not the same class: the two share a
catalogue and a lifecycle, but a metric is never differentiated, so `hessian_strategy` and
`hessian_min` would be fields meaningful for only one of two uses.
"""

from __future__ import annotations

import enum
from typing import Final, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.objectives import (
    TEMPLATE_PARAMETERS,
    Applicability,
    CertificateResult,
    ObjectiveKind,
    ObjectiveTemplate,
)
from model_schema.refs import Slug

__all__ = [
    "FITTABLE_METRIC_STATUSES",
    "TERMINAL_METRIC_STATUSES",
    "VALID_METRIC_TRANSITIONS",
    "CustomMetric",
    "MetricCertificate",
    "MetricDirection",
    "MetricStatus",
]


class MetricDirection(enum.StrEnum):
    """FR-MODEL-104. Declared, never inferred.

    Early stopping compares successive values and halts when they stop improving; which
    comparison "improving" is cannot be read off the arithmetic. A metric whose direction
    is guessed stops at the wrong round in half of cases, and returns a fitted model rather
    than an error — the failure that leaves no trace.
    """

    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


class MetricStatus(enum.StrEnum):
    """FR-MODEL-45's "same lifecycle as objectives"."""

    DRAFT = "draft"
    CERTIFIED = "certified"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


#: The same two non-arrow edges `VALID_OBJECTIVE_TRANSITIONS` carries, for the same reasons:
#: re-certification must be able to withdraw a claim, and a review decision does not
#: withdraw a certificate.
VALID_METRIC_TRANSITIONS: Final[dict[MetricStatus, frozenset[MetricStatus]]] = {
    MetricStatus.DRAFT: frozenset({MetricStatus.CERTIFIED, MetricStatus.DEPRECATED}),
    MetricStatus.CERTIFIED: frozenset(
        {MetricStatus.REVIEW, MetricStatus.DRAFT, MetricStatus.DEPRECATED}
    ),
    MetricStatus.REVIEW: frozenset({MetricStatus.APPROVED, MetricStatus.CERTIFIED}),
    MetricStatus.APPROVED: frozenset({MetricStatus.DEPRECATED}),
    MetricStatus.DEPRECATED: frozenset(),
}

TERMINAL_METRIC_STATUSES: Final[frozenset[MetricStatus]] = frozenset({MetricStatus.DEPRECATED})

#: A `draft` metric has no certificate, so `direction_holds` is unproven and early stopping
#: would rest on an unchecked claim. A `deprecated` one has been withdrawn.
FITTABLE_METRIC_STATUSES: Final[frozenset[MetricStatus]] = frozenset(
    {MetricStatus.CERTIFIED, MetricStatus.REVIEW, MetricStatus.APPROVED}
)


class CustomMetric(BaseModel):
    """A named, versioned, reusable eval metric (FR-MODEL-45, §4.13)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: Slug
    version: int = Field(ge=1)
    kind: ObjectiveKind = ObjectiveKind.TEMPLATE
    template: ObjectiveTemplate | None = None
    params: dict[str, int | float] = Field(default_factory=dict)
    applicability: Applicability
    #: FR-MODEL-104: required, because there is no safe default.
    direction: MetricDirection
    status: MetricStatus = MetricStatus.DRAFT
    description: str | None = None
    certificate_id: UUID | None = None
    approval_request_id: UUID | None = None

    @model_validator(mode="after")
    def _only_templates_are_built(self) -> Self:
        """FR-MODEL-75's rule, at the type — the second door behind the API's refusal."""
        if self.kind is not ObjectiveKind.TEMPLATE or self.template is None:
            raise ValueError(
                "Phase 1 admits only `kind: template` metrics, and a template metric needs "
                "a `template` (FR-MODEL-103)."
            )
        return self

    @model_validator(mode="after")
    def _the_parameters_are_the_templates_own(self) -> Self:
        """An unknown key is refused, never dropped.

        A misspelled `cap` that is silently ignored produces an uncapped metric under a
        name that says capped — and nothing downstream can tell.
        """
        if self.template is None:  # pragma: no cover — the validator above ran first
            return self
        declared = {p.name: p for p in TEMPLATE_PARAMETERS[self.template]}
        unknown = sorted(set(self.params) - set(declared))
        if unknown:
            raise ValueError(
                f"metric params {unknown} are not parameters of template "
                f"{self.template.value!r}; it declares {sorted(declared)} (FR-MODEL-103)."
            )
        for name, parameter in declared.items():
            if name in self.params:
                parameter.check(self.params[name])
        return self

    @model_validator(mode="after")
    def _a_status_past_draft_rests_on_a_certificate(self) -> Self:
        """FR-MODEL-105 — a claim with no evidence behind it is refused at the type."""
        if self.status is not MetricStatus.DRAFT and self.certificate_id is None:
            raise ValueError(
                f"metric status {self.status.value!r} without a certificate_id; every "
                "status past `draft` rests on one (FR-MODEL-105)."
            )
        return self


class MetricCertificate(BaseModel):
    """The identity around `CertificateResult` — the ADR-0001 split §4.7 already uses."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    custom_metric_id: UUID
    metric_version: int = Field(ge=1)
    certified_at: str
    job_id: UUID | None = None
    result: CertificateResult
```

**If `TEMPLATE_PARAMETERS` is not the exported name** in `objectives.py`, find the real one with `grep -n 'TEMPLATE_PARAMETERS\|_PARAMETERS' packages/model-schema/src/model_schema/objectives.py` and use that. Do not duplicate the parameter catalogue — it exists, and a second copy would diverge.

- [ ] **Step 5: Re-export from the package root**

Add to `packages/model-schema/src/model_schema/__init__.py`, following the existing style there (read the file first; it has an explicit `__all__`):

```python
from model_schema.metrics import (
    FITTABLE_METRIC_STATUSES,
    TERMINAL_METRIC_STATUSES,
    VALID_METRIC_TRANSITIONS,
    CustomMetric,
    MetricCertificate,
    MetricDirection,
    MetricStatus,
)
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `uv run pytest packages/model-schema/tests/test_metrics.py -q`
Expected: 8 passed.

- [ ] **Step 7: Type-check and regenerate contracts**

```bash
uv run ruff check packages/model-schema
uv run mypy
uv run python scripts/generate-contracts.py
```

Expected: ruff 0, mypy 0, and the contract count rises from 21 (a new schema for `CustomMetric`). **The new file is a generated artifact and must be committed** — CI fails on drift.

- [ ] **Step 8: Commit**

```bash
git add packages/model-schema/src/model_schema/metrics.py \
        packages/model-schema/src/model_schema/__init__.py \
        packages/model-schema/tests/test_metrics.py docs/contracts/
git commit -m "feat(schema): FR-MODEL-103/104/105 — the CustomMetric artifact"
```

---

### Task 3: Evaluation and certification in pricing-core

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/objectives.py` — add `template_loss` to the public surface
- Create: `packages/pricing-core/src/pricing_core/modelling/metrics.py`
- Test: `packages/pricing-core/tests/test_metrics.py`

**Interfaces:**
- Consumes: `CustomMetric`, `MetricDirection` (Task 2); `_TEMPLATES` via the new accessor.
- Produces: `evaluate_metric(metric: CustomMetric, y: NDArray, f: NDArray, w: NDArray) -> float` and `certify_metric(metric: CustomMetric, *, seed: int) -> CertificateResult`. Task 6 calls the first; Task 5's worker handler calls the second.

- [ ] **Step 1: Read the registry you are reusing**

Run: `sed -n '102,128p;488,500p;636,650p' packages/pricing-core/src/pricing_core/modelling/objectives.py`

You are reading `_Template`, the head of the `_TEMPLATES` dict, and how `compile_objective` looks an entry up. **Write no loss arithmetic** — every template's loss is already there, and a second copy would diverge from the objective that shares its name.

- [ ] **Step 2: Write the failing tests**

Create `packages/pricing-core/tests/test_metrics.py`:

```python
"""FR-MODEL-103/104/105 — evaluating and certifying a Custom Metric."""

from __future__ import annotations

import uuid

import numpy as np
import pytest

from model_schema.metrics import CustomMetric, MetricDirection
from model_schema.objectives import (
    Applicability,
    CertificateOutcome,
    CheckStatus,
    ObjectiveTemplate,
    YDomain,
)
from pricing_core.modelling.metrics import certify_metric, evaluate_metric


def _metric(template: ObjectiveTemplate = ObjectiveTemplate.POISSON, **kw: object) -> CustomMetric:
    kwargs: dict[str, object] = {
        "id": uuid.uuid4(),
        "slug": "poisson-nll",
        "version": 1,
        "template": template,
        "params": {},
        "applicability": Applicability(
            responses=("claim_count",),
            backends=("xgboost",),
            offset_required=False,
            y_domain=YDomain(min=0.0),
        ),
        "direction": MetricDirection.LOWER_IS_BETTER,
    }
    kwargs.update(kw)
    return CustomMetric(**kwargs)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-103")
def test_the_metric_is_the_weighted_mean_of_the_templates_loss() -> None:
    """Reuses the objective catalogue's arithmetic — no second implementation."""
    from pricing_core.modelling.objectives import template_loss

    y = np.array([0.0, 1.0, 3.0])
    f = np.array([-0.2, 0.1, 1.0])
    w = np.array([1.0, 2.0, 4.0])
    expected = float(np.average(template_loss(ObjectiveTemplate.POISSON)(y, f, {}), weights=w))
    assert evaluate_metric(_metric(), y, f, w) == pytest.approx(expected)


@pytest.mark.req("FR-MODEL-103")
def test_weights_are_honoured_not_ignored() -> None:
    """An exposure-weighted metric that ignores weights is a different metric."""
    y = np.array([0.0, 5.0])
    f = np.array([0.0, 0.0])
    flat = evaluate_metric(_metric(), y, f, np.array([1.0, 1.0]))
    tilted = evaluate_metric(_metric(), y, f, np.array([1.0, 99.0]))
    assert flat != pytest.approx(tilted)


@pytest.mark.req("FR-MODEL-104")
def test_certification_catches_a_direction_declared_backwards() -> None:
    """The check that exists because the defect is otherwise invisible."""
    backwards = _metric(direction=MetricDirection.HIGHER_IS_BETTER)
    result = certify_metric(backwards, seed=20260819)
    direction = next(c for c in result.checks if c.name == "direction_holds")
    assert direction.status is CheckStatus.FAIL
    assert result.overall is CertificateOutcome.FAILED


@pytest.mark.req("FR-MODEL-105")
def test_a_correctly_declared_metric_certifies() -> None:
    result = certify_metric(_metric(), seed=20260819)
    assert result.overall in (
        CertificateOutcome.CERTIFIED,
        CertificateOutcome.CERTIFIED_WITH_FINDINGS,
    )
    assert {c.name for c in result.checks} == {
        "finiteness",
        "direction_holds",
        "scale_behaviour",
        "smoke_evaluation",
    }


@pytest.mark.req("FR-MODEL-105")
def test_no_derivative_check_appears_on_a_metric_certificate() -> None:
    """Absent, not `not_applicable` — the question is not askable of a metric."""
    result = certify_metric(_metric(), seed=20260819)
    names = {c.name for c in result.checks}
    assert not {n for n in names if "gradient" in n or "hessian" in n or n == "convexity"}


@pytest.mark.req("FR-MODEL-105")
def test_certification_is_deterministic_under_its_seed() -> None:
    first = certify_metric(_metric(), seed=20260819)
    second = certify_metric(_metric(), seed=20260819)
    assert [(c.name, c.status, c.detail) for c in first.checks] == [
        (c.name, c.status, c.detail) for c in second.checks
    ]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest packages/pricing-core/tests/test_metrics.py -q`
Expected: collection error — `No module named 'pricing_core.modelling.metrics'`.

- [ ] **Step 4: Expose the registry's loss, minimally**

In `packages/pricing-core/src/pricing_core/modelling/objectives.py`, add the accessor and put it in `__all__`:

```python
def template_loss(template: ObjectiveTemplate) -> _Fn:
    """The catalogue's loss for one template — the metric path's single source (FR-MODEL-103).

    Public so `metrics.py` reuses this arithmetic rather than copying it. Nothing else about
    `_TEMPLATES` is exported: the gradient and hessian are the fitting path's business, and a
    metric has no use for either.
    """
    return _TEMPLATES[template].loss
```

Add `"template_loss"` to `__all__`, keeping it alphabetically sorted with the existing entries.

- [ ] **Step 5: Write the metric module**

Create `packages/pricing-core/src/pricing_core/modelling/metrics.py`:

```python
"""Evaluating and certifying a Custom Metric — FR-MODEL-103/104/105, `02` §4.7 and §4.13.

`pricing-core` is handed the artifact and never resolves a reference (ADR-0001): every
function here takes a `CustomMetric`, and the backend is what turned a
`custom_metric:<slug>@<version>` string into one.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import numpy.typing as npt

from model_schema.metrics import CustomMetric, MetricDirection
from model_schema.objectives import (
    CertificateCheck,
    CertificateResult,
    CheckStatus,
    SamplingSpec,
)
from pricing_core.modelling.objectives import template_loss

__all__ = ["certify_metric", "evaluate_metric"]

_Arr = npt.NDArray[np.float64]

#: The sampling grid the certificate reports. Fixed rather than tunable: a certificate whose
#: grid the author chose is a certificate the author can pass by choosing.
_N_POINTS: Final = 10_000
_Y_RANGE: Final = (0.0, 1e7)
_F_RANGE: Final = (-20.0, 20.0)
_W_RANGE: Final = (1e-3, 1e4)


def evaluate_metric(metric: CustomMetric, y: _Arr, f: _Arr, w: _Arr) -> float:
    """The template's loss as an exposure-weighted mean (FR-MODEL-103).

    `f` is the **raw score**, not the transformed prediction — the same convention the
    objective path uses, and the reason FR-MODEL-107 exists: a backend's builtin metric
    receives the raw score under a callable objective and silently means something else.
    """
    if metric.template is None:  # pragma: no cover — refused at the type
        raise ValueError("a Phase 1 metric always names a template (FR-MODEL-103)")
    per_row = template_loss(metric.template)(y, f, dict(metric.params))
    return float(np.average(per_row, weights=w))


def _grid(seed: int) -> tuple[_Arr, _Arr, _Arr]:
    rng = np.random.default_rng(seed)
    y = rng.uniform(*_Y_RANGE, _N_POINTS)
    f = rng.uniform(*_F_RANGE, _N_POINTS)
    w = rng.uniform(*_W_RANGE, _N_POINTS)
    return y, f, w


def _better(direction: MetricDirection, candidate: float, reference: float) -> bool:
    if direction is MetricDirection.LOWER_IS_BETTER:
        return candidate < reference
    return candidate > reference


def certify_metric(metric: CustomMetric, *, seed: int) -> CertificateResult:
    """§4.7's four metric checks (FR-MODEL-105).

    Returns the findings only: no id, no clock, no Job — the backend stamps those around
    this into a `MetricCertificate` (ADR-0001, the same split as `certify_objective`).
    """
    y, f, w = _grid(seed)
    checks: list[CertificateCheck] = []

    values = template_loss(metric.template)(y, f, dict(metric.params))  # type: ignore[arg-type]
    finite = bool(np.all(np.isfinite(values)))
    checks.append(
        CertificateCheck(
            name="finiteness",
            status=CheckStatus.PASS if finite else CheckStatus.FAIL,
            detail=(
                f"no NaN/inf over {_N_POINTS:,} sampled points, y in {_Y_RANGE}, "
                f"f in {_F_RANGE}, w in {_W_RANGE}"
                if finite
                else f"{int(np.sum(~np.isfinite(values))):,} of {_N_POINTS:,} sampled "
                "points are NaN or inf"
            ),
        )
    )

    # `direction_holds`: at the truth `f = log(y)` the metric must be better than at a
    # perturbed score. This is what catches a `direction` declared backwards — the defect
    # that otherwise halves the value of early stopping while producing a fitted model.
    truthful = np.log(np.clip(y, 1e-9, None))
    at_truth = evaluate_metric(metric, y, truthful, w)
    perturbed = evaluate_metric(metric, y, truthful + 1.0, w)
    holds = _better(metric.direction, at_truth, perturbed)
    checks.append(
        CertificateCheck(
            name="direction_holds",
            status=CheckStatus.PASS if holds else CheckStatus.FAIL,
            detail=(
                f"value at f=log(y) is {at_truth:.6g} against {perturbed:.6g} one unit away; "
                f"the metric declares {metric.direction.value}"
            ),
        )
    )

    small = evaluate_metric(metric, y, truthful, w)
    large = evaluate_metric(metric, y * 10.0, np.log(np.clip(y * 10.0, 1e-9, None)), w)
    span = abs(large) / abs(small) if small else float("inf")
    checks.append(
        CertificateCheck(
            name="scale_behaviour",
            status=CheckStatus.PASS if span < 1e3 else CheckStatus.WARN,
            detail=f"value changes by a factor of {span:.3g} when y is scaled by 10",
        )
    )

    # `smoke_evaluation`: on a constant population the weighted mean of a constant loss is
    # that loss, which is computable without this module.
    ones_y = np.ones(1_000)
    ones_f = np.zeros(1_000)
    ones_w = np.full(1_000, 3.0)
    expected = float(
        template_loss(metric.template)(ones_y, ones_f, dict(metric.params))[0]  # type: ignore[arg-type]
    )
    observed = evaluate_metric(metric, ones_y, ones_f, ones_w)
    agrees = bool(np.isclose(observed, expected, rtol=1e-12))
    checks.append(
        CertificateCheck(
            name="smoke_evaluation",
            status=CheckStatus.PASS if agrees else CheckStatus.FAIL,
            detail=(
                f"constant population of 1,000: {observed:.12g} against the hand-computable "
                f"{expected:.12g}"
            ),
        )
    )

    frozen = tuple(checks)
    return CertificateResult(
        checks=frozen,
        sampling=SamplingSpec(
            n_points=_N_POINTS,
            seed=seed,
            y_range=list(_Y_RANGE),
            f_range=list(_F_RANGE),
            w_range=list(_W_RANGE),
        ),
        overall=CertificateResult.outcome_of(frozen),
        library_versions={"numpy": np.__version__},
    )
```

**`SamplingSpec`'s field names and types are read off §4.7's JSON, not off the class.** Confirm them with `sed -n '592,631p' packages/model-schema/src/model_schema/objectives.py` and use the real ones — if the ranges are tuples rather than lists, pass tuples.

- [ ] **Step 6: Run the tests to verify they pass**

Run: `uv run pytest packages/pricing-core/tests/test_metrics.py -q`
Expected: 6 passed.

- [ ] **Step 7: Prove the direction check fails on broken input**

Temporarily change `_better` to always return `True`, then run:

Run: `uv run pytest packages/pricing-core/tests/test_metrics.py -q`
Expected: `test_certification_catches_a_direction_declared_backwards` **FAILS**. Restore `_better` and re-run; expected 6 passed. A check that cannot be shown to fail is the defect it exists to prevent (`CLAUDE.md` §13.4).

- [ ] **Step 8: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/metrics.py \
        packages/pricing-core/src/pricing_core/modelling/objectives.py \
        packages/pricing-core/tests/test_metrics.py
git commit -m "feat(model): FR-MODEL-103/105 — evaluate and certify a Custom Metric"
```

---

### Task 4: The table and its migration

**Files:**
- Modify: `backend/src/app/db/models.py` — `CustomMetricRow`, `MetricCertificateRow`
- Create: `backend/migrations/versions/<rev>_custom_metrics.py`
- Test: `backend/tests/test_custom_metrics_table.py`

**Interfaces:**
- Consumes: `MetricStatus`, `MetricDirection` (Task 2).
- Produces: the `custom_metrics` and `metric_certificates` tables, and the `custom_metrics_definition_immutable` trigger. Task 5's service reads and writes them.

- [ ] **Step 1: Read the migration you are paralleling**

Run: `cat backend/migrations/versions/d0e1f2a3b4c5_custom_objectives.py`

Note especially the immutability trigger: the definition columns of a row cannot be updated, because a Model referencing `custom_metric:<slug>@<version>` must keep meaning what it was fitted under. Your table needs the same guarantee over `slug`, `version`, `kind`, `template`, `params`, `applicability` and `direction`. `status`, `certificate_id` and `approval_request_id` **must stay mutable** — they are the lifecycle.

- [ ] **Step 2: Read the row class you are paralleling**

Run: `sed -n '1530,1620p' backend/src/app/db/models.py`

- [ ] **Step 3: Write the failing test**

Create `backend/tests/test_custom_metrics_table.py`. Read `backend/tests/conftest.py` first and use its real session and workspace fixture names — the ones below are the shape, not verified names.

```python
"""FR-MODEL-103 — the custom_metrics table and its immutability guarantee."""

from __future__ import annotations

import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError

from app.db.models import CustomMetricRow

pytestmark = pytest.mark.anyio

_APPLICABILITY = {
    "responses": ["claim_severity"],
    "backends": ["xgboost"],
    "offset_required": False,
    "y_domain": {"min": 0.0},
}


def _row(workspace_id, **kw) -> CustomMetricRow:
    fields = {
        "id": uuid.uuid4(),
        "workspace_id": workspace_id,
        "slug": "capped-gamma-nll",
        "version": 1,
        "kind": "template",
        "template": "capped_gamma",
        "params": {"cap": 250000.0},
        "applicability": _APPLICABILITY,
        "direction": "lower_is_better",
        "status": "draft",
    }
    fields.update(kw)
    return CustomMetricRow(**fields)


@pytest.mark.req("FR-MODEL-103")
async def test_a_metric_row_round_trips(session, workspace_id) -> None:
    row = _row(workspace_id)
    session.add(row)
    await session.flush()
    fetched = await session.get(CustomMetricRow, row.id)
    assert fetched is not None
    assert fetched.params == {"cap": 250000.0}
    assert fetched.direction == "lower_is_better"


@pytest.mark.req("FR-MODEL-103")
async def test_the_definition_cannot_be_edited(session, workspace_id) -> None:
    """A Model fitted under version 1 must keep meaning version 1's arithmetic."""
    row = _row(workspace_id, slug="poisson-nll", template="poisson", params={})
    session.add(row)
    await session.flush()
    with pytest.raises(DBAPIError):
        await session.execute(
            sa.update(CustomMetricRow)
            .where(CustomMetricRow.id == row.id)
            .values(params={"cap": 1.0})
        )
        await session.flush()


@pytest.mark.req("FR-MODEL-45")
async def test_the_lifecycle_columns_stay_mutable(session, workspace_id) -> None:
    """The trigger must not freeze the status, or nothing could ever be certified."""
    row = _row(workspace_id, slug="gamma-nll", template="gamma", params={})
    session.add(row)
    await session.flush()
    await session.execute(
        sa.update(CustomMetricRow)
        .where(CustomMetricRow.id == row.id)
        .values(status="certified", certificate_id=uuid.uuid4())
    )
    await session.flush()
    await session.refresh(row)
    assert row.status == "certified"


@pytest.mark.req("FR-MODEL-103")
async def test_a_slug_and_version_pair_is_unique(session, workspace_id) -> None:
    session.add(_row(workspace_id, slug="duplicate"))
    await session.flush()
    session.add(_row(workspace_id, slug="duplicate"))
    with pytest.raises(DBAPIError):
        await session.flush()
```

- [ ] **Step 4: Run to verify it fails**

Run: `uv run pytest backend/tests/test_custom_metrics_table.py -q`
Expected: `ImportError: cannot import name 'CustomMetricRow'`.

- [ ] **Step 5: Add the row classes**

Add `CustomMetricRow` and `MetricCertificateRow` to `backend/src/app/db/models.py`, immediately after the custom-objective classes. Mirror their column types, the `workspace_id` scoping, the `uq_` unique constraint on `(workspace_id, slug, version)`, the `version >= 1` check, a check that `status` is in the lifecycle, a check that `direction` is one of the two values, and the `ix_` index on `(workspace_id, slug, status)`.

- [ ] **Step 6: Generate and then hand-finish the migration**

```bash
uv run alembic revision --autogenerate -m "custom metrics"
```

Autogenerate will produce the tables but **not the trigger** — copy the `custom_objectives_definition_immutable` trigger from `d0e1f2a3b4c5_custom_objectives.py`, renaming it and listing this table's definition columns. Include the `DROP TRIGGER` and `DROP FUNCTION` in `downgrade()`; a migration that only goes one way is not reversible and this repository's migrations are.

- [ ] **Step 7: Apply and test**

```bash
uv run alembic upgrade head
uv run pytest backend/tests/test_custom_metrics_table.py -q
```

Expected: 4 passed. Then prove the migration reverses:

```bash
uv run alembic downgrade -1
uv run alembic upgrade head
```

Expected: both succeed. A trigger left behind by `downgrade()` makes the second command fail with "trigger already exists" — which is how you find out you forgot it.

- [ ] **Step 8: Commit**

```bash
git add backend/src/app/db/models.py backend/migrations/versions/ \
        backend/tests/test_custom_metrics_table.py
git commit -m "feat(db): FR-MODEL-103 — the custom_metrics table, with its definition frozen"
```

---

### Task 5: The service and the six routes

**Files:**
- Create: `backend/src/app/platform/metrics.py`
- Create: `backend/src/app/api/custom_metrics.py`
- Modify: `backend/src/app/errors.py`, `backend/src/app/main.py`
- Modify: `backend/src/app/worker/model_handlers.py` — a `metric.certify` job handler
- Test: `backend/tests/test_custom_metrics_api.py`

**Interfaces:**
- Consumes: `CustomMetricRow` (Task 4), `certify_metric` (Task 3), `CustomMetric`/`MetricStatus`/`VALID_METRIC_TRANSITIONS` (Task 2).
- Produces: `resolve_ref(session, *, workspace_id, ref) -> CustomMetric`, which **Task 6's worker calls**. Its signature must match `app.platform.objectives.resolve_ref` exactly, so read that one first: `grep -n 'async def resolve_ref' -A 12 backend/src/app/platform/objectives.py`.

- [ ] **Step 1: Read the router and service you are paralleling**

```bash
sed -n '100,200p' backend/src/app/api/custom_objectives.py
grep -n '^async def \|^def ' backend/src/app/platform/objectives.py
```

Note how the router obtains the database, checks permissions, opens **one** `unit_of_work`, and writes the audit event **inside the caller's transaction** — that last point is a retrofit-impossible foundation (`docs/roadmap.md` §5) and must not be loosened.

- [ ] **Step 2: Register the three error codes**

In `backend/src/app/errors.py`, add to the modelling frozenset:

```python
"METRIC_REF_UNRESOLVED",
"METRIC_NOT_APPLICABLE",
"METRIC_NOT_FITTABLE",
```

**Declare them in `02` §5.1's error-code table in the same commit.** OQ-OVR-9 records that nothing cross-checks the two lists, so this is currently a discipline rather than a check — which is exactly why it is written here as a step.

- [ ] **Step 3: Write the failing API tests**

Create `backend/tests/test_custom_metrics_api.py`. Read the objectives' API test first (`ls backend/tests | grep objective`) and follow its client fixture and auth headers exactly.

```python
"""FR-MODEL-108 — the Custom Metric endpoints."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.anyio

_BODY = {
    "slug": "capped-gamma-nll",
    "template": "capped_gamma",
    "params": {"cap": 250000.0},
    "applicability": {"responses": ["claim_severity"], "backends": ["xgboost"],
                      "offset_required": False, "y_domain": {"min": 0.0}},
    "direction": "lower_is_better",
}


@pytest.mark.req("FR-MODEL-45")
async def test_create_returns_201_and_a_draft(client) -> None:
    response = await client.post("/api/v1/custom-metrics", json=_BODY)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["version"] == 1
    assert body["certificate_id"] is None


@pytest.mark.req("FR-MODEL-108")
async def test_the_created_metric_is_readable(client) -> None:
    created = (await client.post("/api/v1/custom-metrics", json=_BODY)).json()
    response = await client.get(f"/api/v1/custom-metrics/{created['id']}")
    assert response.status_code == 200
    assert response.json()["slug"] == "capped-gamma-nll"


@pytest.mark.req("FR-MODEL-108")
async def test_the_certificate_404s_before_certification_and_names_the_metric(client) -> None:
    created = (await client.post("/api/v1/custom-metrics", json=_BODY)).json()
    response = await client.get(f"/api/v1/custom-metrics/{created['id']}/certificate")
    assert response.status_code == 404
    assert created["id"] in response.text


@pytest.mark.req("FR-MODEL-105")
async def test_an_uncertified_metric_cannot_be_submitted(client) -> None:
    """The negative half of the lifecycle: `draft -> review` is not an edge."""
    created = (await client.post("/api/v1/custom-metrics", json=_BODY)).json()
    response = await client.post(f"/api/v1/custom-metrics/{created['id']}/submit")
    assert response.status_code == 409


@pytest.mark.req("FR-MODEL-104")
async def test_a_metric_without_a_direction_is_refused(client) -> None:
    body = {k: v for k, v in _BODY.items() if k != "direction"}
    response = await client.post("/api/v1/custom-metrics", json=body)
    assert response.status_code == 422


@pytest.mark.req("FR-MODEL-103")
async def test_creating_the_same_slug_twice_makes_a_second_version(client) -> None:
    first = (await client.post("/api/v1/custom-metrics", json=_BODY)).json()
    second = (await client.post("/api/v1/custom-metrics", json=_BODY)).json()
    assert (first["version"], second["version"]) == (1, 2)
```

The 409's `code` is deliberately not asserted here: find the code the objectives' submit route raises for a bad transition and assert **that** one — do not introduce a second code meaning the same thing.

- [ ] **Step 4: Run to verify they fail**

Run: `uv run pytest backend/tests/test_custom_metrics_api.py -q`
Expected: every test 404s — the router is not registered.

- [ ] **Step 5: Write the service**

Create `backend/src/app/platform/metrics.py` mirroring `platform/objectives.py`: `create`, `get`, `resolve_ref`, `record_certificate`, `submit`, `usage`. `resolve_ref` parses `custom_metric:<slug>@<version>`, loads the row scoped to the workspace, and returns a `CustomMetric` — raising `METRIC_REF_UNRESOLVED` when there is no such row.

- [ ] **Step 6: Write the router and register it**

Create `backend/src/app/api/custom_metrics.py` with the six routes from §5.1, and register it in `backend/src/app/main.py` beside the custom-objectives router. `certify` returns **202 with a Job** (FR-MODEL-105 follows FR-MODEL-42's shape); add the `metric.certify` handler to `backend/src/app/worker/model_handlers.py`, calling `certify_metric` from Task 3 and persisting a `MetricCertificateRow`.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `uv run pytest backend/tests/test_custom_metrics_api.py -q`
Expected: 6 passed.

- [ ] **Step 8: Commit**

```bash
git add backend/src/app/platform/metrics.py backend/src/app/api/custom_metrics.py \
        backend/src/app/errors.py backend/src/app/main.py \
        backend/src/app/worker/model_handlers.py \
        backend/tests/test_custom_metrics_api.py docs/specs/02-modelling.md
git commit -m "feat(api): FR-MODEL-108 — the Custom Metric endpoints and certification job"
```

---

### Task 6: Honour `eval_metrics`, and narrow the early-stopping refusal

This is the task the slice exists for. Everything before it built an artifact nothing consumed.

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/gbm.py`
- Modify: `backend/src/app/worker/model_handlers.py`
- Test: `packages/pricing-core/tests/test_gbm.py` (extend), `backend/tests/test_model_jobs_gbm.py` (extend)

**Interfaces:**
- Consumes: `evaluate_metric` (Task 3), `resolve_ref` (Task 5), `FITTABLE_METRIC_STATUSES` (Task 2).
- Produces: no new public names. It changes the meaning of `GbmSpec.eval_metrics` from "ignored" to "honoured", and narrows one error's scope.

- [ ] **Step 1: Read the refusal you are narrowing**

Run: `sed -n '440,480p' packages/pricing-core/src/pricing_core/modelling/gbm.py`

The current rule refuses **all** early stopping under a custom objective. FR-MODEL-107 narrows it to a **builtin** metric: the reason in the message — both backends hand a builtin metric the raw score rather than the transformed prediction — does not apply to a custom metric, because `evaluate_metric` is written against the raw score by construction.

- [ ] **Step 2: Write the failing tests**

Add to `packages/pricing-core/tests/test_gbm.py`. **Read the top of that file first** and use its existing spec/frame/holdout fixtures — the helper names below are the shape, not verified names; do not create parallel fixtures.

```python
@pytest.mark.req("FR-MODEL-107")
def test_early_stopping_on_a_custom_metric_is_allowed_under_a_custom_objective() -> None:
    """The refusal FR-MODEL-45 was deferred behind, retired."""
    spec = _gbm_spec_with_custom_objective(
        eval_metrics=(GbmFunctionRef(kind="custom", ref="custom_metric:poisson-nll@1"),),
        early_stopping=EarlyStopping(
            on="holdout", metric="custom_metric:poisson-nll@1", rounds=10
        ),
    )
    result = fit_gbm(
        spec, frame, holdout=holdout, objective=objective,
        metrics={"custom_metric:poisson-nll@1": metric},
    )
    assert result.best_iteration is not None


@pytest.mark.req("FR-MODEL-107")
def test_early_stopping_on_a_builtin_metric_is_still_refused_under_a_custom_objective() -> None:
    """The narrowing must not become a removal — the raw-score problem is unchanged."""
    spec = _gbm_spec_with_custom_objective(
        early_stopping=EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=10),
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(spec, frame, holdout=holdout, objective=objective)
    assert raised.value.code == "OBJECTIVE_EARLY_STOPPING_UNSUPPORTED"


@pytest.mark.req("FR-MODEL-106")
def test_a_custom_eval_metric_that_was_not_supplied_refuses_the_fit() -> None:
    """ADR-0001: pricing-core does not resolve refs, so an unsupplied one is the caller's bug."""
    spec = _gbm_spec(eval_metrics=(GbmFunctionRef(kind="custom", ref="custom_metric:absent@1"),))
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(spec, frame, holdout=holdout)
    assert raised.value.code == "METRIC_REF_UNRESOLVED"


@pytest.mark.req("FR-MODEL-106")
def test_a_metric_whose_applicability_excludes_the_backend_refuses_the_fit() -> None:
    lightgbm_only = _metric(
        applicability=Applicability(
            responses=("claim_count",), backends=("lightgbm",),
            offset_required=False, y_domain=YDomain(min=0.0),
        )
    )
    spec = _gbm_spec(
        model_type="xgboost",
        eval_metrics=(GbmFunctionRef(kind="custom", ref="custom_metric:poisson-nll@1"),),
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(spec, frame, holdout=holdout,
                metrics={"custom_metric:poisson-nll@1": lightgbm_only})
    assert raised.value.code == "METRIC_NOT_APPLICABLE"


@pytest.mark.req("FR-MODEL-106")
def test_a_draft_metric_cannot_be_fitted_with() -> None:
    """FITTABLE_METRIC_STATUSES excludes draft: an uncertified metric is unproven."""
    draft = _metric(status=MetricStatus.DRAFT)
    spec = _gbm_spec(
        eval_metrics=(GbmFunctionRef(kind="custom", ref="custom_metric:poisson-nll@1"),)
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(spec, frame, holdout=holdout, metrics={"custom_metric:poisson-nll@1": draft})
    assert raised.value.code == "METRIC_NOT_FITTABLE"


@pytest.mark.req("FR-MODEL-106")
def test_a_builtin_eval_metric_reaches_the_backend() -> None:
    """The half that needed no FR-MODEL-45 machinery and was ignored anyway."""
    spec = _gbm_spec(eval_metrics=(GbmFunctionRef(kind="builtin", name="poisson-nloglik"),))
    result = fit_gbm(spec, frame, holdout=holdout)
    assert "poisson-nloglik" in result.evals_result["holdout"]
```

- [ ] **Step 3: Run to verify they fail**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q -k "metric or early_stopping"`
Expected: failures — `fit_gbm()` got an unexpected keyword argument `metrics`.

- [ ] **Step 4: Add the `metrics` parameter and the resolution checks**

In `gbm.py`, give `fit_gbm` a keyword-only `metrics: Mapping[str, CustomMetric] | None = None`, and add a `_resolve_metrics` helper that, for each `eval_metrics` entry of `kind: custom`, refuses with `METRIC_REF_UNRESOLVED` when the ref is absent from `metrics`, `METRIC_NOT_APPLICABLE` when the spec's backend or response is outside its applicability, and `METRIC_NOT_FITTABLE` when its status is outside `FITTABLE_METRIC_STATUSES`. Mirror `_resolve_objective`'s message style: name the ref, name the requirement.

- [ ] **Step 5: Narrow the early-stopping refusal**

Replace the unconditional `if spec.early_stopping is not None:` refusal with one that fires only when the named metric is **not** one of the spec's custom eval metrics:

```python
    if spec.early_stopping is not None and not _is_custom_metric_ref(
        spec.early_stopping.metric, spec.eval_metrics
    ):
        raise GbmFitError(
            "OBJECTIVE_EARLY_STOPPING_UNSUPPORTED",
            f"the spec pairs Custom Objective {ref!r} with early stopping on the builtin "
            f"metric {spec.early_stopping.metric!r}. Under a callable objective both "
            "backends hand a builtin metric the **raw score** rather than the transformed "
            "prediction, so the metric it stops on is not the metric it names. Declare a "
            "Custom Metric in `eval_metrics` and stop on that instead (FR-MODEL-107).",
            terms=[ref, str(spec.early_stopping.metric)],
        )
```

- [ ] **Step 6: Wire `feval` for both backends**

Build the backend callable from `evaluate_metric`, honouring `metric.direction` — XGBoost's `feval` returns `(name, value)` and takes `is_higher_better` from the metric, LightGBM's returns `(name, value, is_higher_better)`. **This is where a wrong `direction` would stop the fit at the wrong round**, which is why FR-MODEL-104 makes it required and Task 3 certifies it.

- [ ] **Step 7: Resolve the refs in the worker**

In `backend/src/app/worker/model_handlers.py`, beside the existing objective resolution (around line 245), resolve every `kind: custom` entry of `spec.eval_metrics` through Task 5's `resolve_ref` and pass the mapping into `fit_gbm(..., metrics=...)`. **Do not open a second `unit_of_work`** — extend the existing `load()` block; a nested one deadlocks against the pool rather than failing.

- [ ] **Step 8: Run the tests**

```bash
uv run pytest packages/pricing-core/tests/test_gbm.py -q
uv run pytest backend/tests/test_model_jobs_gbm.py -q
```

Expected: both green, including the pre-existing test at `packages/pricing-core/tests/test_gbm.py:984` that asserts the builtin refusal — **it must still pass**, because the narrowing is not a removal.

- [ ] **Step 9: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/gbm.py \
        backend/src/app/worker/model_handlers.py \
        packages/pricing-core/tests/test_gbm.py backend/tests/test_model_jobs_gbm.py
git commit -m "feat(model): FR-MODEL-106/107 — eval_metrics honoured, early stopping on a custom metric"
```

---

### Task 7: The gate, and the record

**Files:**
- Modify: `docs/roadmap.md` — the slice record
- Test: the whole suite

**Interfaces:**
- Consumes: everything.
- Produces: a merged, recorded slice.

- [ ] **Step 1: Run the Python gate, reading each command's own exit code**

```bash
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```

Do **not** chain these with `&&` into a single `| tail -1` — that reports `tail`'s exit code and has produced a false clean here more than once. Expected: 489 requirements, all open questions mirrored, contracts matching.

- [ ] **Step 2: Run the frontend gate**

The frontend is untouched by this slice, but the gate is both halves and a generated client can drift:

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```

`pnpm` is at `~/.npm-global/bin` and is not on the default PATH.

- [ ] **Step 3: Confirm the endpoint axis closed**

Run: `uv run python scripts/scope-audit.py MODEL --endpoints`
Expected: **every declared endpoint published** — 34 of 35 before this slice, and Task 1 adds five more declarations, so the target is 40 of 40. Report the number the run prints, not the number this plan predicted.

- [ ] **Step 4: Write the slice record**

Add a `#### W5 slice — custom metrics, and a field that was read by nothing, 2026-08-19` section to `docs/roadmap.md`, immediately before `### Phase 1b — Modelling Workbench`, following the shape of the GLM-approximation record above it: a Delivered/Evidence table, what the gate measured, what was **not** delivered with owners, and the finding — `eval_metrics` was declared from Phase 0 and consumed by nothing, so a caller could name a metric and be told nothing was wrong.

Update W5's row in §6 to name this slice and raise the count to twenty-two.

- [ ] **Step 5: Commit and open the PR**

```bash
git add docs/roadmap.md
git commit -m "docs(roadmap): the custom-metrics slice record"
git push -u origin feat/custom-metrics
gh pr create --title "feat(model): FR-MODEL-45 — custom eval metrics" --body-file <path>
```

`gh pr checks` answers *"Resource not accessible by personal access token"* here — that is a scope limit, not a red build. Read CI with `gh pr view <n> --json mergeStateStatus`: `CLEAN` means checks passed, `UNSTABLE` means pending or failing.

---

## Self-Review

**1. Spec coverage.** FR-MODEL-45's three clauses: *"same lifecycle"* → Tasks 2 (transitions), 4 (mutable status columns), 5 (certify/submit routes). *"same grammar"* → Task 2's templates-only validator, and DG-2's decision that a metric names an objective template. *"declared separately so that a metric can be reused across objectives"* → Task 4's own table keyed on `(workspace_id, slug, version)`, with nothing tying a metric to one objective. §5.1's `POST /custom-metrics` → Task 5. §4.4's `eval_metrics` block → Task 6. **One gap found and closed while reviewing:** the spec's §4.4 example shows `eval_metrics` alongside `early_stopping.metric` as a plain string, and nothing said whether a ref may appear there — FR-MODEL-107 and Task 6 Step 5 now decide it explicitly.

**2. Placeholder scan.** No "TBD", no "add appropriate error handling", no "similar to Task N". Five places name a guess *as* a guess and say how to check it — `SamplingSpec`'s fields, the test fixtures in Tasks 4, 5 and 6, `TEMPLATE_PARAMETERS`, and the bad-transition error code. That is deliberate: this repository's FR-MODEL-96 ledger records a brief that invented a spec caveat which did not exist, and the fix was to write from the real file rather than from memory of it.

**3. Type consistency.** `CustomMetric`, `MetricStatus`, `MetricDirection`, `MetricCertificate`, `VALID_METRIC_TRANSITIONS`, `FITTABLE_METRIC_STATUSES` are spelled identically in Tasks 2, 3, 4, 5 and 6. `evaluate_metric(metric, y, f, w)` and `certify_metric(metric, *, seed)` are defined in Task 3 and called with those signatures in Tasks 5 and 6. `resolve_ref(session, *, workspace_id, ref)` is defined in Task 5 and called in Task 6, and is flagged there to be matched against `objectives.resolve_ref` rather than invented. `template_loss` is added in Task 3 Step 4 and used in Step 5 and in Task 3's first test.

**One honest correction to the roadmap's framing.** I recorded this slice yesterday as *"the smallest, nothing gates it"*, on the strength of `02` §5.1's amendment saying the lifecycle and certification machinery it waits on is built. That is true of the *machinery* and false of the *slice*: a metric needs its own artifact, table, certificate variant, evaluation path and `feval` wiring, none of which the objective work provides. Seven tasks, a migration and a fit-path change is a middling slice, not the smallest — the custom-metrics row in `docs/roadmap.md`'s "W5 — outstanding work" section should be corrected when this lands, or now if you would rather reorder the five.
