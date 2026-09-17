---
id: PL-742
family: plan
kind: leaf
title: Offset from Another Model Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-21
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-21-offset-from-another-model.md
---

# Offset from Another Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans — this plan is a sequence of small, individually verifiable tasks; follow it strictly, do not "improve" the shape of the data, and do not skip the gate steps.

**Goal.** FR-116: let a GLM spec declare an **offset from another model** (`offset_model_ref`) — the referenced fitted GLM's linear predictor on the training data becomes the offset, enabling residual modelling and "fit on top of the current rating structure" workflows. The referenced model version is pinned by the canonical `model:slug@version` ref (ID-3). Delivered as `OffsetSpec.offset_model_ref: ModelRef | None` (schema, replacing the dead `model_ref: str` scaffold), `resolve_offset_model()` in the backend (ref resolution and named refusals), `model_offset` parameters threaded through pricing-core (`fit_glm`, `compute_diagnostics`, `linear_predictor`/`predict_glm`/`predict_glm_interval`/`score_fitted`/`backtest_model`), and `GlmFitResult.offset_model_ref` recording what was constructed.

**Architecture.** Pricing-core never resolves artifacts (ADR-703), so the split is exactly the booster-bytes pattern: the backend resolves the pinned ref to the referenced model's spec, fit result, factors, bandings and groupings (`resolve_offset_model`, modelled on `objectives.resolve_ref` + `_refuse_mismatched_approximation`), and each call site computes η with the existing `linear_predictor` and passes it as `model_offset`. Every pricing-core entry point that takes `model_offset` **requires it when `spec.offset.kind == "model"`** and raises the already-registered `MODEL_OFFSET_MISSING` when it is absent — turning every un-wired call site into a named failure instead of a silently missing offset (the defect class FR-126 refuses for `base_margin`). Scope is GLM-to-GLM only: a `GbmSpec` with `kind="model"` is refused by name at schema level, a ref naming a GBM/EBM model or a mismatched link is refused by name (`MODEL_OFFSET_REF_INVALID`), and the peril-reconciliation scoring path is declared-and-refused until a later slice wires it.

**Tech Stack.** Python 3.12; Pydantic v2 (model-schema); glum (unchanged fit path — the offset array slots into the existing `offset=` arguments); NumPy; Polars; SciPy untouched; pytest with `@pytest.mark.req`; no pandas; no new dependencies of any kind.

**Spec.** `docs/specs/02-modelling.md` FR-116 (line 162), amended by Task 1 of this plan (dated 2026-08-21). The resolved design, which the amendment records:

- `OffsetSpec.offset_model_ref: ModelRef | None = None` — `ModelRef` is a canonical `model:slug@version` string (ID-3), pattern-validated. Renames the Phase-0 scaffold's `model_ref: str` (read by nothing; `docs/contracts/schemas/model-spec.schema.json:23-31` has always carried `offset_model_ref` as an artifact-ref — the spec and the hand-authored contract agree, the code scaffold is the outlier, and the code follows the spec).
- Validators: `kind == "model"` ⟺ `offset_model_ref` set; the pattern admits `model:` refs only. `GbmSpec` refuses `kind == "model"` by name.
- Fit-time behaviour: the offset is the referenced fitted GLM's linear predictor (η, including its own offset) on the training data; the referenced model's link must equal the new spec's link, refused by name otherwise. CV and Tweedie-profile paths inherit the same array (fold masks slice it).
- `GlmFitResult.offset_model_ref: ModelRef | None = None` — the resolved pinned ref, "what was actually constructed is recorded on the fit result" (FR-126's rule, applied to GLM).
- Named refusals: `GbmSpec` with `kind="model"`; a ref naming a non-fitted, non-GLM, or link-mismatched model (`MODEL_OFFSET_REF_INVALID`); the peril-reconciliation scoring path fails named (`MODEL_OFFSET_MISSING`) until WK-661 wires the resolver there.
- Diagnostic weighting for a model-offset fit follows `spec.weight` (COUNT default) — the exposure-weighting convention is never inferred from the offset.
- `spec_hash` covers the ref automatically (the payload is the whole canonicalised spec dump); `SPEC_HASH_VERSION` moves 7 → 8 in the same commit (FR-206).
- `POST /model-specs/validate` resolves the ref and reports failures as a new `SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE`.

## Slice context (verified at planning time, 2026-08-21)

- FR-116 is unevidenced and open; roadmap's "WK-661 — outstanding work" table, row 4 (`docs/roadmap.md:2569`): "`offset_model_ref` appears nowhere in `packages/` or `backend/src`. This is residual modelling and 'fit on top of the current rating structure', with the referenced model version pinned." The row's "appears nowhere" is true of code, but the hand-authored Phase-0 contract has carried the field since `b452c78` — this plan reconciles the two (below) rather than treating it as a clean slate.
- **The §0 divergence, resolved here:** the spec (FR-116 text) and the hand-authored contract (`docs/contracts/schemas/model-spec.schema.json:23-31`) declare `offset_model_ref` as an artifact-ref string; the code scaffold (`modelling.py:659-672`) declares `model_ref: str | None` and nothing reads it. **Spec wins** — recorded in the Task 1 amendment. Note for the executor: `scripts/generate-contracts.py --check` only byte-compares the *generated* files against model-schema; it never diffs generated against hand-authored. The hand-authored file is synced by hand (Task 2), per the roadmap's job.schema.json discipline.
- **Today's behaviour is a defect, not an absence:** `fit_glm` passes `kind="model"` silently with `offset = None` (glm.py:517-546), fitting as though no offset were declared; `predict._offset` (predict.py:140-166) likewise returns `None`; GBM's `_offset` (gbm.py:200-229) *accidentally* refuses it via `column="None"`. The slice replaces silence and accident with the implemented path plus named refusals.
- Precedents the tasks copy: `_quantile_crossing` (model_handlers.py:438-528 — loads a sibling model's row, spec via `MODEL_SPEC_ADAPTER`, fit via `FIT_RESULT_ADAPTER`, factors, bandings, groupings, then scores), `_refuse_mismatched_approximation` (platform/modelling.py:598-660 — the NOT_FOUND / not-fitted / named-refusal shape), `objectives.resolve_ref` (objectives.py:327-353 — the slug+version ref lookup), `load_model` (platform/modelling.py:803-823 — the slug+version row lookup to reuse), the CV and Tweedie slices (the spec-first amendment commit, the same-commit SPEC_HASH_VERSION bump, the error-code catalogue discipline).
- **Scope honesty — what this slice does NOT do** (each with an owner): GBM/EBM referenced models and GbmSpec offsets (refused by name; OQ-594 records the widening options); the peril-reconciliation scoring path (declared-and-refused, owner WK-661); EBM as a model type (FR-140, separate slice); FR-115's fit-error surfacing (unbuilt, owner WK-661); the frontend model-spec builder (WK-664). `WF-699…05` owe FR-19(ii) regardless.

## Global Constraints

- **Workspace:** single uv workspace — `packages/model-schema`, `packages/pricing-core`, `backend`, all with `--all-packages --dev`. No frontend change in this slice (generated types only, via the contracts).
- **Ruff** line length 100; **mypy --strict** on all packages; **lint-imports** (pricing-core imports model_schema only, never backend; backend may import pricing-core).
- **No pandas** anywhere; **glum** is the estimator; **Pydantic v2**.
- **Every new test** carries `@pytest.mark.req("FR-116")`; **a negative test precedes every positive one** for each invariant.
- **Spec-change discipline (§0):** any change to what a model *is* bumps `SPEC_HASH_VERSION` in the same commit (7 → 8, FR-206); any new error code is registered in `backend/src/app/errors.py` **and** the §5.1 backtick catalogue (`02-modelling.md:1619-1639`) **in the same commit as its first raise** — the catalogue entry lands with the implementation, not the amendment (the Tweedie slice's correction). New codes also get a dated blockquote note (`MODEL_APPROXIMATION_INVALID` at :1649-1660 is the format).
- **Contracts:** run `scripts/generate-contracts.py` after every model-schema change and commit the result (FR-451); `--check` in the gate. The hand-authored `docs/contracts/schemas/model-spec.schema.json` is synced by hand in the same commit (the script never compares the two — verified 2026-08-21). Read `.claude/skills/contract-schema` before the sync step.
- **If code proves the spec wrong**, amend the spec with a dated note — never a quiet edit (§0). If the plan proves wrong, append to the execution-corrections addendum at the end of this file.
- **Conventional Commits** (`feat(model-schema):`, `feat(pricing-core):`, `feat(backend):`, `chore(contracts):`, `docs(spec):`, `docs(roadmap):`), each tagged with FR-116, with the `Co-Authored-By: Claude <noreply@anthropic.com>` trailer on every commit.
- **Branch and PR flow** per `.claude/skills/git-hygiene`: short-lived branch from `main`, squash-merge, branch auto-delete. The last task opens the PR and delegates CI watching (`gh pr checks` exits 0 without data on this repo's token — read merge state via `gh pr view --json mergeStateStatus`).
- **Skills per task:** `spec-change` (Tasks 1, 9), `python-package` + `python-test` (Tasks 2-4), `contract-schema` (Task 2's sync step), `git-hygiene` (every commit, Task 9). The gate is §11's **both halves**.

---

## Task 1 — Spec amendment: FR-116 defined, §4.4 block, OQ-594

**Files:**
- Modify: `docs/specs/02-modelling.md` (FR-116 row at :162; §4.4 offset example at :498)
- Modify: `docs/open-questions.md` (new OQ-594)

**Interfaces:**
- Consumes: the FR-207 staged-contract rule (:325), the §4.4 amendment-block style of `GlmCvSpec`/`TweediePowerSpec` (02-modelling.md:559-594).
- Produces: the amended FR-116 text every later task argues from; OQ-594.

- [ ] **Step 1: Read the spec-change skill and the amendment precedents**

Run: read `.claude/skills/spec-change/SKILL.md`, then `sed -n '155,170p' docs/specs/02-modelling.md` and `sed -n '555,600p' docs/specs/02-modelling.md` (the two dated amendment blocks this task's style must match).

- [ ] **Step 2: Amend the FR-116 row (02-modelling.md:162)**

Replace the row's single sentence with the definition plus a dated amendment (append inside the same table cell, matching the FR-112/114 amendment style):

```
| **FR-116** | An **offset from another model** is supported (`offset_model_ref`), enabling residual modelling and "fit on top of the current rating structure" workflows. The referenced model version is pinned. **Amended 2026-08-21 (WK-661 slice 4).** The ref is the canonical `model:slug@version` string (ID-3). v1 builds the offset for GLM specs only: the referenced model must be a fitted GLM, and the offset is its linear predictor (η, including its own offset) on the training data — the two links must be equal, refused by name otherwise (`MODEL_OFFSET_REF_INVALID`). Refused by name, not built: a `GbmSpec` whose offset is `kind: "model"`; a ref naming a GBM or EBM model; the peril-reconciliation scoring path (it fails named, `MODEL_OFFSET_MISSING`, until WK-661 wires the resolver there). The fit records what was constructed: `GlmFitResult.offset_model_ref` carries the resolved pinned ref. Diagnostic weighting for a model-offset fit follows `spec.weight` (COUNT default) — the exposure-weighting convention is never inferred from the offset. The Phase-0 scaffold's `model_ref: str` is renamed `offset_model_ref` with the artifact-ref pattern: the spec and the hand-authored contract have always named and typed it that way, and the scaffold field was read by nothing. |
```

- [ ] **Step 3: Add the §4.4 dated amendment block after the offset example (:498)**

```
> **`offset_model_ref` — declared 2026-08-21 (WK-661 slice 4, FR-116).** The common
> block's `offset` gains the field: a canonical `model:slug@version` string, valid only
> with `kind: "model"`, naming the fitted GLM whose linear predictor is the offset
> (FR-116 as amended). Live once the slice populates it (FR-207). A `GbmSpec`
> naming it is refused by name, and a ref naming a non-fitted, non-GLM, or
> link-mismatched model is refused at fit time (`MODEL_OFFSET_REF_INVALID`).
```

- [ ] **Step 4: Record the widening question as OQ-594 in docs/open-questions.md**

Follow the file's OQ format; options and recommendation:

```
### OQ-594 — which offsets-from-model come after the GLM-to-GLM slice? (open)

FR-116's 2026-08-21 amendment builds offset-from-another-model for GLM specs
referencing fitted GLMs only. **Options:** (a) extend to GBM-referenced offsets — the
referenced raw score minus its own `base_margin`, as η on the link scale — when a
workflow needs it; (b) extend to `GbmSpec` declaring the offset (base_margin from η);
(c) wire the peril-reconciliation scoring path to the resolver; (d) leave GLM-to-GLM
as the whole capability. **Recommendation:** (a) then (c), each as its own slice;
(d) only if residual modelling stays GLM-shaped in practice. Gate: WK-661, no date.
```

- [ ] **Step 5: Run the docs audit and commit**

Run: `python3 scripts/audit-docs.py`
Expected: clean exit 0.

```bash
git add docs/specs/02-modelling.md docs/open-questions.md
git commit -m "docs(spec): FR-116 defined — offset from another model, GLM-to-GLM v1 (OQ-594)"
```

---

## Task 2 — model-schema: `ModelRef`, `offset_model_ref`, refusals, spec-hash bump

**Files:**
- Modify: `packages/model-schema/src/model_schema/refs.py` (add `ModelRef`; `__all__` at :17)
- Modify: `packages/model-schema/src/model_schema/modelling.py` (`OffsetSpec` :659-672; GbmSpec validators near :1328-1346; `GlmFitResult` near :1505; `SpecProblemKind` :1752-1772)
- Modify: `packages/model-schema/src/model_schema/__init__.py` (export `ModelRef` — the import at :237 and the name list near :308)
- Modify: `backend/src/app/platform/modelling.py` (`SPEC_HASH_VERSION` :121 and its history comment)
- Create: `packages/model-schema/tests/test_offset_model_spec.py`
- Modify: `packages/model-schema/tests/test_gbm_spec.py` (one refusal test, reusing its `_spec` builder)
- Regenerate: `docs/contracts/schemas/generated/model-spec.schema.json`, `docs/contracts/schemas/generated/model.schema.json`, `docs/contracts/openapi/generated.json` (via the script); sync the hand-authored `docs/contracts/schemas/model-spec.schema.json:23-31`

**Interfaces:**
- Consumes: `_SLUG` from refs.py:30; the `OffsetSpec`/`GbmSpec` validator style; `new_uuid7()` for test ids.
- Produces:
  - `ModelRef = Annotated[str, Field(pattern=rf"^model:{_SLUG}@[1-9][0-9]*$")]` in refs.py, exported.
  - `OffsetSpec.offset_model_ref: ModelRef | None = None` (replaces `model_ref: str | None = None`).
  - `OffsetSpec._a_model_offset_names_its_model(self) -> OffsetSpec`.
  - `GbmSpec._a_gbm_offset_from_another_model_is_refused(self) -> GbmSpec`.
  - `GlmFitResult.offset_model_ref: ModelRef | None = None`.
  - `SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE = "model_offset_unresolvable"`.
  - `SPEC_HASH_VERSION: Final = 8` (backend).

- [ ] **Step 1: Write the failing tests** in `test_offset_model_spec.py` (negative first):

```python
"""FR-116: `offset_model_ref` on `OffsetSpec` — the declared shape, and what is
refused. Negative tests first: a staged contract admits only what a slice has built."""

import pydantic
import pytest
from model_schema import GlmSpec, OffsetSpec, new_uuid7


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": new_uuid7(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-116")
def test_a_model_offset_names_its_model() -> None:
    with pytest.raises(pydantic.ValidationError, match="offset_model_ref"):
        _spec(offset=OffsetSpec(kind="model"))


@pytest.mark.req("FR-116")
def test_a_model_ref_declares_the_model_kind() -> None:
    with pytest.raises(pydantic.ValidationError, match="kind.*model"):
        _spec(offset=OffsetSpec(offset_model_ref="model:base@1"))


@pytest.mark.req("FR-116")
def test_the_ref_must_name_a_model_not_any_artifact() -> None:
    with pytest.raises(pydantic.ValidationError, match="model:"):
        _spec(offset=OffsetSpec(kind="model", offset_model_ref="dataset:thing@1"))


@pytest.mark.req("FR-116")
def test_a_model_offset_spec_constructs_and_round_trips() -> None:
    spec = _spec(offset=OffsetSpec(kind="model", offset_model_ref="model:base@7"))
    dumped = spec.model_dump(mode="json")["offset"]
    assert dumped["offset_model_ref"] == "model:base@7"
    assert dumped["kind"] == "model"
```

In `test_gbm_spec.py`, after the existing `_spec` builder, add:

```python
@pytest.mark.req("FR-116")
def test_a_gbm_offset_from_another_model_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="GLM specs only"):
        _spec(offset=OffsetSpec(kind="model", offset_model_ref="model:base@1"))
```

- [ ] **Step 2: Run them, watch them fail**

Run: `uv run pytest packages/model-schema/tests/test_offset_model_spec.py packages/model-schema/tests/test_gbm_spec.py -q`
Expected: FAIL — the field does not exist (constructor errors) and the GBM refusal is absent.

- [ ] **Step 3: Implement the schema changes**

In `refs.py` (after `Slug`, keeping `__all__` alphabetical):

```python
#: A canonical reference to a Model specifically: `model:slug@version` (ID-3).
#: FR-116's offset ref is one of these — the prefix is part of the pattern, so
#: the published contract admits `model:` refs and nothing else.
ModelRef = Annotated[str, Field(pattern=rf"^model:{_SLUG}@[1-9][0-9]*$")]
```

Add `"ModelRef"` to `__all__` and export it from `__init__.py` (the import line near :237 and the name list near :308, both alphabetical).

In `modelling.py`, replace `OffsetSpec` (:659-672) with:

```python
class OffsetSpec(BaseModel):
    """`02` §4.4. `log_column` is the frequency default: `offset = log(exposure)`.

    `model` is the offset from another model (FR-116): the referenced fitted GLM's
    linear predictor, resolved by the backend and supplied as the fit's `model_offset`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["none", "log_column", "column", "model"] = "none"
    column: str | None = None
    #: The pinned reference whose linear predictor is the offset: `model:slug@version`.
    #: Renamed from the Phase-0 scaffold's `model_ref` (read by nothing) to the name the
    #: spec and the hand-authored contract have always carried (FR-116, 2026-08-21).
    offset_model_ref: ModelRef | None = None

    @model_validator(mode="after")
    def _a_column_offset_names_its_column(self) -> OffsetSpec:
        if self.kind in {"log_column", "column"} and not self.column:
            raise ValueError(f"offset kind {self.kind!r} requires a column")
        return self

    @model_validator(mode="after")
    def _a_model_offset_names_its_model(self) -> OffsetSpec:
        if self.kind == "model" and self.offset_model_ref is None:
            raise ValueError("offset kind 'model' requires offset_model_ref (FR-116)")
        if self.kind != "model" and self.offset_model_ref is not None:
            raise ValueError("offset_model_ref is set but offset kind is not 'model'")
        return self
```

Add the import of `ModelRef` to modelling.py's `refs` import (:34). In `GlmFitResult`, after the `tweedie` field (near :1514), add:

```python
    #: What an offset-from-another-model fit was constructed against — the resolved,
    #: pinned ref (FR-116). `None` for every other offset kind.
    offset_model_ref: ModelRef | None = None
```

Add to `GbmSpec` (next to `_a_frequency_gbm_declares_its_exposure`, :1328-1346):

```python
    @model_validator(mode="after")
    def _a_gbm_offset_from_another_model_is_refused(self) -> GbmSpec:
        #: Declared-and-refused rather than omitted (FR-207): the enum arm stays so
        #: the refusal is by name, and the 2026-08-21 FR-116 amendment records that
        #: the first slice builds offsets-from-model for GLM specs only.
        if self.offset.kind == "model":
            raise ValueError(
                "offset kind 'model' is built for GLM specs only (FR-116, "
                "2026-08-21); a GBM spec must name a column offset instead"
            )
        return self
```

Add to `SpecProblemKind` (:1752-1772), after `OFFSET_MISSING`:

```python
    #: FR-116's ref-resolution half: the offset's model ref names no model, an
    #: unfitted one, a non-GLM, or one whose link is not the new spec's.
    MODEL_OFFSET_UNRESOLVABLE = "model_offset_unresolvable"
```

In `backend/src/app/platform/modelling.py`, bump the hash (:121) with a dated history entry matching the v6/v7 entries:

```python
#: `offset_model_ref` (renamed from the scaffold's `model_ref`, FR-116) moved it
#: `v7` to `v8` (2026-08-21, the offset-from-another-model slice): the field joins the
#: canonicalised spec — the offset it names is part of what a fit means, and FR-204's
#: dedup must not match a fit against another model's structure to one that has no offset.
SPEC_HASH_VERSION: Final = 8
```

- [ ] **Step 4: Run the tests, watch them pass**

Run: `uv run pytest packages/model-schema/tests/test_offset_model_spec.py packages/model-schema/tests/test_gbm_spec.py -q`
Expected: PASS. Then `uv run pytest packages/model-schema/tests/ -q` — the whole model-schema suite still green (no existing fixture passes `model_ref`; the rename is inert). Then `uv run pytest backend/tests/test_spec_hash.py -q` — if it asserts a stale-digest list that names `v7`, update the assertion to `v8` in the same commit (the v7 digests are what this bump makes stale).

- [ ] **Step 5: Regenerate the contracts, sync the hand-authored file, commit**

Run: `uv run python scripts/generate-contracts.py && uv run python scripts/generate-contracts.py --check`
Then read `.claude/skills/contract-schema/SKILL.md` (the hand-authored-sync rules), and in `docs/contracts/schemas/model-spec.schema.json:23-31` replace the `offset_model_ref` member so it matches the regenerated `OffsetSpec` def (the generated file now shows `offset_model_ref` with the model-only pattern; the hand-authored file's `$ref` to the *generic* artifact-ref pattern is broader than the code now admits). The replacement member:

```json
        "offset_model_ref": {
          "anyOf": [
            {"type": "string", "pattern": "^model:[a-z0-9][a-z0-9-]{1,62}@[1-9][0-9]*$"},
            {"type": "null"}
          ]
        }
```

Commit everything (schema, backend hash bump, tests, generated contracts, hand-authored sync — one commit, per §2's rhythm):

```bash
git add packages/model-schema packages/model-schema/tests backend/src/app/platform/modelling.py docs/contracts
git commit -m "feat(model-schema): FR-116 — offset_model_ref replaces the dead model_ref scaffold (SPEC_HASH_VERSION 8)"
```

---

## Task 3 — pricing-core: `fit_glm` gains `model_offset`

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/glm.py` (signature :486-495; offset construction :534-546)
- Create: `packages/pricing-core/tests/test_glm_model_offset.py`

**Interfaces:**
- Consumes: `OffsetSpec(kind="model", offset_model_ref=...)` from Task 2; the existing `offset` array's consumers (`estimator.fit` :606, `_fit_cv_path` :585-588 with its fold slicing at :320/:328, `_estimate_tweedie_power` :416-417) — none of them change.
- Produces:
  - `fit_glm(..., *, model_offset: np.ndarray | None = None, ...) -> GlmFit` — when `spec.offset.kind == "model"`, `model_offset` is required; the array is validated for length and finiteness and becomes the offset.
  - `_model_offset(data: pl.DataFrame, spec: GlmSpec, model_offset: np.ndarray | None) -> np.ndarray` (module-private).

- [ ] **Step 1: Write the failing tests** in `test_glm_model_offset.py`. Copy the `_frequency_data`/`_spec` builders verbatim from `test_glm.py:39-71`, and `_factor` from `test_glm.py` (grep `def _factor`). Add the residual generator:

```python
"""FR-116: `kind="model"` offsets — supplied, validated, honoured. The array is the
referenced model's linear predictor; pricing-core cannot resolve the ref itself and must
refuse to fit without the array rather than fit with no offset."""

import numpy as np
import polars as pl
import pytest

from model_schema import GlmSpec, OffsetSpec
from pricing_core.modelling import GlmFitError
from pricing_core.modelling.glm import fit_glm

# ... copied builders: _frequency_data, _spec, _factor ...


def _residual_data(n: int = 20_000, seed: int = 20260821) -> tuple[pl.DataFrame, np.ndarray]:
    """y ~ Poisson(exp(eta_base + 0.2·z)); `eta_base` is the referenced model's truth.

    log(mu) = log(exposure) - 2.0 + 0.5·[urban] + 0.2·[resid_flag]
    """
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.25, 1.0, n)
    urban = rng.integers(0, 2, n)
    z = rng.integers(0, 2, n)
    eta_base = np.log(exposure) - 2.0 + 0.5 * urban
    eta = eta_base + 0.2 * z
    return (
        pl.DataFrame(
            {
                "exposure_years": exposure,
                "area": ["urban" if u else "rural" for u in urban],
                "resid_flag": z.astype(float),
                "claim_count": rng.poisson(np.exp(eta)).astype(float),
            }
        ),
        eta_base,
    )


def _model_offset_spec() -> GlmSpec:
    return _spec(offset=OffsetSpec(kind="model", offset_model_ref="model:base@1"))


@pytest.mark.req("FR-116")
def test_a_model_offset_without_the_array_is_refused() -> None:
    data, _ = _residual_data()
    with pytest.raises(GlmFitError, match="MODEL_OFFSET_MISSING"):
        fit_glm(data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")])


@pytest.mark.req("FR-116")
def test_a_model_offset_of_the_wrong_length_is_refused() -> None:
    data, eta_base = _residual_data()
    with pytest.raises(GlmFitError, match="rows"):
        fit_glm(
            data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")],
            model_offset=eta_base[:-1],
        )


@pytest.mark.req("FR-116")
def test_a_model_offset_with_non_finite_values_is_refused() -> None:
    data, eta_base = _residual_data()
    eta_base[0] = np.inf
    with pytest.raises(GlmFitError, match="finite"):
        fit_glm(
            data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")],
            model_offset=eta_base,
        )


@pytest.mark.req("FR-116")
def test_the_residual_fit_recovers_the_signal_on_top_of_the_offset() -> None:
    data, eta_base = _residual_data()
    result = fit_glm(
        data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")],
        model_offset=eta_base,
    ).result
    by_term = {c.term: c for c in result.coefficients}
    assert by_term["intercept"].estimate == pytest.approx(0.0, abs=0.06)
    assert by_term["resid_flag"].estimate == pytest.approx(0.2, abs=0.05)
```

- [ ] **Step 2: Run them, watch them fail**

Run: `uv run pytest packages/pricing-core/tests/test_glm_model_offset.py -q`
Expected: FAIL — `model_offset` is an unexpected keyword, and the recovery test would fit without any offset (intercept lands near −2, not 0).

- [ ] **Step 3: Implement**

In `glm.py`, add `model_offset: np.ndarray | None = None` to `fit_glm`'s keyword-only block (after `seed`), add the helper above `fit_glm`, and extend the offset construction (:534-546) with a third arm:

```python
def _model_offset(
    data: pl.DataFrame, spec: GlmSpec, model_offset: np.ndarray | None
) -> np.ndarray:
    """The `kind="model"` offset: the referenced model's linear predictor, which
    pricing-core cannot resolve itself — the caller supplies it (FR-116). Missing
    it would fit as though no offset were declared: named, never silent."""
    if model_offset is None:
        raise GlmFitError(
            "MODEL_OFFSET_MISSING",
            "offset kind 'model' requires the resolved offset array (model_offset), and "
            "none was supplied. The fit job resolves offset_model_ref before fitting "
            "(FR-116).",
            terms=[str(spec.offset.offset_model_ref)],
        )
    if model_offset.shape != (data.height,):
        raise GlmFitError(
            "MODEL_OFFSET_MISSING",
            f"model_offset has {model_offset.shape[0]} rows for {data.height} data rows "
            "(FR-116).",
            terms=[str(spec.offset.offset_model_ref)],
        )
    if not np.all(np.isfinite(model_offset)):
        raise GlmFitError(
            "MODEL_OFFSET_MISSING",
            "model_offset carries non-finite values; the referenced model's linear "
            "predictor must be finite (FR-116).",
            terms=[str(spec.offset.offset_model_ref)],
        )
    return np.asarray(model_offset, dtype=np.float64)
```

and in the offset construction:

```python
    elif spec.offset.kind == "model":
        offset = _model_offset(data, spec, model_offset)
```

`_fit_cv_path` and `_estimate_tweedie_power` take the finished array — no change (the CV fold masks at glm.py:320/:328 slice it correctly). `_relativities` (glm.py:865) keeps `exposure_column = None` for `"model"` — the exposure column is simply not part of this fit's construction.

- [ ] **Step 4: Run the tests, watch them pass**

Run: `uv run pytest packages/pricing-core/tests/test_glm_model_offset.py -q`
Expected: PASS. Then `uv run pytest packages/pricing-core/tests/test_glm.py packages/pricing-core/tests/test_glm_cv.py packages/pricing-core/tests/test_tweedie_power.py -q` — no regressions in the offset-adjacent suites.

- [ ] **Step 5: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/glm.py packages/pricing-core/tests/test_glm_model_offset.py
git commit -m "feat(pricing-core): FR-116 — fit_glm honours a supplied model offset, named refusal otherwise"
```

---

## Task 4 — pricing-core: the scoring and recompute side takes `model_offset`

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/predict.py` (`_offset` :140-166; `linear_predictor` :169-193; `predict_glm` :196-216; `predict_glm_interval` :219-293; `score_fitted` :296-335)
- Modify: `packages/pricing-core/src/pricing_core/modelling/diagnostics.py` (`compute_diagnostics` :557-570 and its four `predict_glm` call sites :510, :583, :591, :598; `backtest_model` :670-685 and its `score_fitted` call :708-710)
- Modify: `packages/pricing-core/tests/test_glm_model_offset.py` (extend)

**Interfaces:**
- Consumes: Task 3's `fit_glm`; the existing `PredictionError("MODEL_OFFSET_MISSING")` precedent (predict.py:151,161).
- Produces (all new params keyword-only, default `None`, and **required when the spec's offset kind is `"model"`** — absent ⇒ `PredictionError("MODEL_OFFSET_MISSING")`):
  - `_offset(data, spec, model_offset: np.ndarray | None = None)` — gains the `"model"` arm.
  - `linear_predictor(..., *, model_offset=None, bandings=None, groupings=None)`, `predict_glm(..., *, model_offset=None, ...)`, `predict_glm_interval(..., *, model_offset=None, ...)`, `score_fitted(..., *, model_offset=None, ...)` — threaded through.
  - `compute_diagnostics(..., *, model_offset_train: np.ndarray | None = None, model_offset_holdout: np.ndarray | None = None, ...)` — threaded to the `predict_glm` calls that score `train` and `holdout`.
  - `backtest_model(..., *, model_offset: np.ndarray | None = None, ...)` — passed to its `score_fitted` call.

- [ ] **Step 1: Write the failing tests** — extend `test_glm_model_offset.py`:

```python
from model_schema import GlmSpec, OffsetSpec
from pricing_core.modelling import GlmFitError, PredictionError
from pricing_core.modelling.glm import fit_glm

# builders as in Task 3 ...

@pytest.mark.req("FR-116")
def test_prediction_without_the_array_is_refused_and_with_it_reproduces_the_fit() -> None:
    data, eta_base = _residual_data()
    spec = _model_offset_spec()
    factors = [_factor("resid_flag", "resid_flag")]
    fit = fit_glm(data, spec, factors, model_offset=eta_base).result

    from pricing_core.modelling import PredictionError
    from pricing_core.modelling.predict import linear_predictor, predict_glm

    with pytest.raises(PredictionError, match="MODEL_OFFSET_MISSING"):
        predict_glm(fit, data, factors, spec)

    by_term = {c.term: c for c in fit.coefficients}
    manual_mu = np.exp(eta_base + by_term["intercept"].estimate
                       + by_term["resid_flag"].estimate * data["resid_flag"].to_numpy())
    assert predict_glm(fit, data, factors, spec, model_offset=eta_base) == pytest.approx(
        manual_mu, rel=1e-9
    )
    eta = linear_predictor(fit, data, factors, spec, model_offset=eta_base)
    assert np.exp(eta) == pytest.approx(manual_mu, rel=1e-9)


@pytest.mark.req("FR-116")
def test_diagnostics_require_the_arrays_for_a_model_offset_fit() -> None:
    data, eta_base = _residual_data()
    spec = _model_offset_spec()
    factors = [_factor("resid_flag", "resid_flag")]
    fit = fit_glm(data, spec, factors, model_offset=eta_base).result

    from pricing_core.modelling.diagnostics import compute_diagnostics

    with pytest.raises(PredictionError, match="MODEL_OFFSET_MISSING"):
        compute_diagnostics(fit, spec, factors, train=data, holdout=data.head(0))
    result = compute_diagnostics(
        fit, spec, factors, train=data, holdout=data.head(0),
        model_offset_train=eta_base, model_offset_holdout=eta_base[:0],
    )
    assert result.deviance > 0


@pytest.mark.req("FR-116")
def test_backtest_requires_and_honours_the_array() -> None:
    data, eta_base = _residual_data()
    spec = _model_offset_spec()
    factors = [_factor("resid_flag", "resid_flag")]
    fit = fit_glm(data, spec, factors, model_offset=eta_base).result

    from pricing_core.modelling.diagnostics import backtest_model

    with pytest.raises(PredictionError, match="MODEL_OFFSET_MISSING"):
        backtest_model(
            fit, spec, factors, data,
            model_ref="model:residual@2",
            dataset_version_ref="dataset_version:book@2",
            fitted_on_ref="dataset_version:book@2",
        )
    summary = backtest_model(
        fit, spec, factors, data,
        model_ref="model:residual@2",
        dataset_version_ref="dataset_version:book@2",
        fitted_on_ref="dataset_version:book@2",
        model_offset=eta_base,
    )
    assert summary.rows_scored == data.height
```

(Adjust `BacktestSummary`'s attribute name to whatever the existing `test_backtests.py` asserts — grep `summary\.` there; the `ref` strings follow FR-187's invariant that the backtest target is not the fitted-on version.)

- [ ] **Step 2: Run them, watch them fail**

Run: `uv run pytest packages/pricing-core/tests/test_glm_model_offset.py -q`
Expected: FAIL — unexpected keywords, and the without-array cases return numbers instead of raising.

- [ ] **Step 3: Implement**

In `predict.py`, change `_offset` (:140-166) to take and honour the array:

```python
def _offset(
    data: pl.DataFrame, spec: GlmSpec, model_offset: np.ndarray | None = None
) -> npt.NDArray[np.float64] | None:
    """The offset column on the linear-predictor scale, or `None` when the spec has none.

    `kind="model"` takes the array the backend resolved — pricing-core cannot resolve
    the ref itself, and returning `None` here would score as though no offset were
    declared (FR-116): named, never silent.
    """
    if spec.offset.kind == "model":
        if model_offset is None:
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                "offset kind 'model' requires the resolved offset array (model_offset), "
                "and none was supplied (FR-116).",
            )
        if model_offset.shape != (data.height,):
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                f"model_offset has {model_offset.shape[0]} rows for {data.height} "
                "data rows (FR-116).",
            )
        if not np.all(np.isfinite(model_offset)):
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                "model_offset carries non-finite values (FR-116).",
            )
        return np.asarray(model_offset, dtype=np.float64)
    if spec.offset.kind not in {"log_column", "column"}:
        return None
    # ... the existing column arms unchanged ...
```

Thread `model_offset: np.ndarray | None = None` through `linear_predictor` (pass it to `_offset`), `predict_glm` and `predict_glm_interval` (pass to their `linear_predictor` call; the interval adds the offset to the centre only — unchanged behaviour, the array arrives via the same call), and `score_fitted` (forward on the GLM arm only; the GBM arm ignores it — a GbmSpec with `kind="model"` is schema-refused in Task 2).

In `diagnostics.py`, add `model_offset_train`/`model_offset_holdout` to `compute_diagnostics` and pass the matching array at each of the four `predict_glm` call sites (:510, :583, :591, :598) — read the five lines above each call to see which frame it scores (`train` ⇒ `model_offset_train`, `holdout` ⇒ `model_offset_holdout`; the type-III reduced fit at :510 scores `train`). Add `model_offset` to `backtest_model` (:670-685) and pass it to its `score_fitted` call (:708-710).

- [ ] **Step 4: Run the tests, watch them pass**

Run: `uv run pytest packages/pricing-core/tests/test_glm_model_offset.py -q`
Expected: PASS. Then `uv run pytest packages/pricing-core/tests/ -q` — the full pricing-core suite still green (all new params default `None`; existing specs never use `kind="model"`).

- [ ] **Step 5: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/predict.py packages/pricing-core/src/pricing_core/modelling/diagnostics.py packages/pricing-core/tests/test_glm_model_offset.py
git commit -m "feat(pricing-core): FR-116 — prediction, diagnostics and backtest take the resolved model offset"
```

---

## Task 5 — backend: resolve the ref, wire the fit job, register the new code

**Files:**
- Modify: `backend/src/app/platform/modelling.py` (add `OffsetModelSource` + `resolve_offset_model`, near `load_model` :803-823)
- Modify: `backend/src/app/errors.py` (add `MODEL_OFFSET_REF_INVALID` to `MODELLING_ERROR_CODES`, :100-114)
- Modify: `docs/specs/02-modelling.md` (§5.1 catalogue :1619-1639 gains `MODEL_OFFSET_REF_INVALID` + a dated blockquote note in the `MODEL_APPROXIMATION_INVALID` format :1649-1660; the existing `MODEL_OFFSET_MISSING` note gains a dated addendum for its fit-side uses)
- Modify: `backend/src/app/worker/model_handlers.py` (`_fit` :162-435: resolution in the `load()` closure, η computation in the sync body, arrays into `fit_glm` :308-313 and `compute_diagnostics` :335-362)
- Create: `backend/tests/test_model_offset_jobs.py`

**Interfaces:**
- Consumes: Task 2's schema (the spec field), Task 3-4's params; `load_model` (platform/modelling.py:803-823), `MODEL_SPEC_ADAPTER`/`FIT_RESULT_ADAPTER`, `model_service.load_factors`, `transform_service.load_bandings/load_groupings`, the `FactorResolutionError → FACTOR_RESOLUTION_FAILED` mapping (:327-334).
- Produces:
  - `class OffsetModelSource` (frozen dataclass): `spec: GlmSpec`, `fit: GlmFitResult`, `factors: list[Factor]`, `bandings: Mapping[UUID, Banding]`, `groupings: Mapping[UUID, Grouping]` — the η array is deliberately NOT in it; the caller computes it on the worker thread.
  - `async def resolve_offset_model(session, *, workspace_id, ref: str, caller_link: str) -> OffsetModelSource` — raises `NOT_FOUND` (404), `MODEL_OFFSET_REF_INVALID` (409), `FACTOR_RESOLUTION_FAILED` (409).

- [ ] **Step 1: Write the failing tests** in `test_model_offset_jobs.py`. Copy the seeding helpers from `test_model_jobs.py:199-267` (the `_dataset`/`_validated_version`/`_factor`/`_split`/`reserve_model`/`job_service.submit`/`execute_job` pattern) and adapt:

```python
"""FR-116 end to end: a base GLM fit, then a residual fit offset against it — and
the named refusals. The Job is the gate: resolution happens at fit time, on the worker."""

import numpy as np
import polars as pl
import pytest

# ... copied/adapted seeding helpers from test_model_jobs.py:199-267 ...


def _residual_frame(n: int = 4_000, seed: int = 20260821) -> pl.DataFrame:
    """v2 of the book: v1's columns plus a residual signal and its own response.

    claim_count2 ~ Poisson(exp(eta_base + 0.2·resid_flag)), eta_base = the base truth.
    """
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.25, 1.0, n)
    urban = rng.integers(0, 2, n)
    z = rng.integers(0, 2, n)
    eta_base = np.log(exposure) - 2.0 + 0.5 * urban
    return pl.DataFrame(
        {
            "exposure_years": exposure,
            "area": ["urban" if u else "rural" for u in urban],
            "resid_flag": z.astype(float),
            "claim_count": rng.poisson(np.exp(eta_base)).astype(float),
            "claim_count2": rng.poisson(np.exp(eta_base + 0.2 * z)).astype(float),
        }
    )


@pytest.mark.req("FR-116")
async def test_a_residual_fit_offsets_against_the_referenced_model(database, blob_store):
    # Seed v1, fit the base GLM (Poisson, log link, exposure offset, factor `area`).
    # Seed v2 = _residual_frame() with a `resid_flag` factor.
    base = await _fit_base_model(database, blob_store)  # returns the base ModelRow
    ref = f"model:{base.model_family_slug}@{base.version}"

    # Match test_model_jobs.py's reserve_model(...) signature and args exactly —
    # the helpers copied from :199-267 carry the real shape.
    residual = await reserve_model(
        database, spec=GlmSpec(
            model_family_slug="motor-residual",
            dataset_version_id=v2_id,
            response_column="claim_count2",
            offset=OffsetSpec(kind="model", offset_model_ref=ref),
            family="poisson", link="log",
            factors=[resid_factor_id], split_ref=SplitRef(split_artifact_id=split_id),
            seed=0,
        )
    )
    job = await job_service.submit(JobKind.MODEL_FIT, {...})
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    model = await session.get(ModelRow, residual.id)  # noqa: F821 — session per the file's pattern
    assert model.status is ModelStatus.FITTED
    assert model.fit_result["offset_model_ref"] == ref
    resid = next(c for c in model.fit_result["coefficients"] if c["term"] == "resid_flag")
    assert resid["estimate"] == pytest.approx(0.2, rel=0.1)
```

Then the three refusal tests, each asserting `JobStatus.FAILED` and the job's error code (grep `FAILED` in `test_model_jobs.py` for the error-code assertion pattern): a ref naming no model (`model:ghost@1` → `NOT_FOUND`), a ref naming an unfitted model (reserve one, never fit it → `MODEL_OFFSET_REF_INVALID`), and a link mismatch (residual spec declares `link="identity"` → `MODEL_OFFSET_REF_INVALID`).

- [ ] **Step 2: Run them, watch them fail**

Run: `uv run pytest backend/tests/test_model_offset_jobs.py -q`
Expected: FAIL — the fit proceeds with no offset (or errors on the unknown code).

- [ ] **Step 3: Implement the resolver** — in `platform/modelling.py`, after `load_model`:

```python
@dataclasses.dataclass(frozen=True)
class OffsetModelSource:
    """What an offset-from-another-model ref resolves to (FR-116).

    The η array is deliberately not computed here: the linear predictor is pricing-core
    maths and belongs on the worker thread, not the event loop.
    """

    spec: GlmSpec
    fit: GlmFitResult
    factors: list[Factor]
    bandings: Mapping[UUID, Banding]
    groupings: Mapping[UUID, Grouping]


async def resolve_offset_model(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    ref: str,
    caller_link: str,
) -> OffsetModelSource:
    """Resolve `offset_model_ref` to the artifacts whose η is the offset (FR-116).

    Every refusal is named: the ref must name a fitted GLM in this workspace whose link
    equals the new spec's — otherwise the fit would be offset by a number from another
    scale, the defect class FR-126 refuses for `base_margin`.
    """
    parsed = ArtifactRef.model_validate(ref)
    if parsed.type != "model":
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The model the offset names is not a model",
            409,
            f"{ref} names a {parsed.type}, and an offset must be another model (FR-116).",
        )
    row = await load_model(
        session, workspace_id=workspace_id, slug=parsed.slug, version=parsed.version
    )
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "The model the offset names does not exist",
            404,
            f"{ref} resolves to no model in this workspace.",
        )
    if row.fit_result is None:
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The model the offset names has no fit to offset against",
            409,
            f"{ref} is not fitted, and the offset is its linear predictor (FR-116).",
        )
    ref_spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
    ref_fit = FIT_RESULT_ADAPTER.validate_python(row.fit_result)
    if not isinstance(ref_spec, GlmSpec) or not isinstance(ref_fit, GlmFitResult):
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The model the offset names is not a GLM",
            409,
            f"{ref} is not a GLM, and the first offset-from-model slice is GLM-to-GLM "
            "(FR-116, amended 2026-08-21).",
        )
    if ref_spec.link != caller_link:
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The offset model's link is not the new spec's",
            409,
            f"{ref} was fitted with a {ref_spec.link} link and the new spec declares "
            f"{caller_link}; the offset would be a number from another scale (FR-116).",
        )
    try:
        factors = await model_service.load_factors(
            session, workspace_id=workspace_id, factor_ids=list(ref_spec.factors)
        )
    except FactorResolutionError as exc:
        raise PlatformError(
            "FACTOR_RESOLUTION_FAILED",
            "The offset model's factors do not resolve",
            409,
            str(exc),
        ) from exc
    bandings = await transform_service.load_bandings(
        session, workspace_id=workspace_id,
        ids=[f.banding_id for f in factors if f.banding_id],
    )
    groupings = await transform_service.load_groupings(
        session, workspace_id=workspace_id,
        ids=[f.grouping_id for f in factors if f.grouping_id],
    )
    return OffsetModelSource(
        spec=ref_spec, fit=ref_fit, factors=factors, bandings=bandings, groupings=groupings
    )
```

(Check the import block: `ArtifactRef` comes from model_schema — `objectives.py` imports it the same way; `FactorResolutionError` is the class `_fit` maps at :327-334.)

- [ ] **Step 4: Wire `_fit`** (model_handlers.py). In the `load()` closure (:175-278), after the objective/metrics resolution, add:

```python
            offset_source = None
            if isinstance(spec, GlmSpec) and spec.offset.kind == "model":
                offset_source = await resolve_offset_model(
                    session,
                    workspace_id=workspace_id,
                    ref=str(spec.offset.offset_model_ref),
                    caller_link=spec.link,
                )
```

and return it from `load()`. In the sync body, compute the arrays on the worker thread and thread them into the two pricing-core calls (:308-313 and :335-362):

```python
    model_offset = None
    model_offset_holdout = None
    if offset_source is not None:
        model_offset = linear_predictor(
            offset_source.fit, frame, offset_source.factors, offset_source.spec,
            bandings=offset_source.bandings, groupings=offset_source.groupings,
        )
        model_offset_holdout = linear_predictor(
            offset_source.fit, holdout, offset_source.factors, offset_source.spec,
            bandings=offset_source.bandings, groupings=offset_source.groupings,
        )
```

Pass `model_offset=model_offset` to `fit_glm` and `model_offset_train=model_offset, model_offset_holdout=model_offset_holdout` to `compute_diagnostics` — reading the two call sites (:300-365) for the exact variable names of the fit frame and holdout frame (`frame` and `holdout` as above; adjust if they differ). `record_fit` (:423-431) needs no change — `fit_result.offset_model_ref` persists via the existing `model_dump`.

- [ ] **Step 5: Register the code and run everything**

In `errors.py`, add `"MODEL_OFFSET_REF_INVALID"` to `MODELLING_ERROR_CODES` (alphabetical). In `02-modelling.md`'s §5.1 catalogue (:1619-1639), add `` `MODEL_OFFSET_REF_INVALID`, `` to the backtick list and append a dated blockquote note in the `MODEL_APPROXIMATION_INVALID` format:

```
> **`MODEL_OFFSET_REF_INVALID` added 2026-08-21 (WK-661, the offset-from-another-model slice).**
> It refuses a spec whose `offset_model_ref` names a model that cannot serve as the
> offset — not a model at all, not fitted, not a GLM, or fitted with a link that is not
> the new spec's (FR-116). Its own code rather than `NOT_FOUND` because the request
> is well formed: what fails is what the ref names.
```

And append a dated addendum to the existing `MODEL_OFFSET_MISSING` note (grep `` `MODEL_OFFSET_MISSING` `` in `02-modelling.md` to find it): "…FR-116 also raises it when a `kind="model"` spec reaches fit or scoring without the resolved offset array."

Run: `uv run pytest backend/tests/test_model_offset_jobs.py backend/tests/test_model_jobs.py backend/tests/test_worker.py -q`
Expected: PASS. Then `uv run pytest backend/tests/test_repository_invariants.py -q` — the invariant test is green (the new code is registered and catalogued in this same commit; `MODEL_OFFSET_MISSING` was already both).

- [ ] **Step 6: Commit**

```bash
git add backend/src/app/platform/modelling.py backend/src/app/errors.py backend/src/app/worker/model_handlers.py backend/tests/test_model_offset_jobs.py docs/specs/02-modelling.md
git commit -m "feat(backend): FR-116 — the fit job resolves offset_model_ref and fits on the referenced linear predictor"
```

---

## Task 6 — backend: the prediction endpoint resolves the ref

**Files:**
- Modify: `backend/src/app/platform/prediction.py` (`_score_glm` :182-236 — the `predict_glm` call at :216-218 and `predict_glm_interval` at :226-235)
- Modify: `backend/tests/test_prediction.py` (new test)

**Interfaces:**
- Consumes: `resolve_offset_model` (Task 5), `linear_predictor` (pricing-core).
- Produces: `POST /models/{model_id}/predict` honours a model-offset spec — resolves the ref per request, computes η on the request frame, passes `model_offset` to both GLM prediction calls.

- [ ] **Step 1: Write the failing test** in `test_prediction.py`, mirroring its existing end-to-end prediction test (read the file's fixture names first): fit the Task 5 pair (base + residual), then `POST /models/{residual_id}/predict` with rows carrying `resid_flag`; assert the prediction equals `exp(eta_base + β̂·resid_flag)` within tolerance. Then the negative: a residual model whose ref names a deleted/nonexistent model → the request maps to `NOT_FOUND` (404), not a 500.

- [ ] **Step 2: Run it, watch it fail**

Run: `uv run pytest backend/tests/test_prediction.py -q`
Expected: FAIL — the endpoint scores without the offset (under-predicts) or errors.

- [ ] **Step 3: Implement**

In `_score_glm`, where `spec`, `frame`, `factors`, `bandings` and `groupings` are in scope (read :182-236 for the exact names), add before the `predict_glm` call:

```python
    model_offset = None
    if spec.offset.kind == "model":
        source = await resolve_offset_model(
            session, workspace_id=workspace_id,
            ref=str(spec.offset.offset_model_ref), caller_link=spec.link,
        )
        model_offset = linear_predictor(
            source.fit, frame, source.factors, source.spec,
            bandings=source.bandings, groupings=source.groupings,
        )
```

and pass `model_offset=model_offset` to both the `predict_glm` (:216-218) and `predict_glm_interval` (:226-235) calls. (`_score_glm` must have `session` and `workspace_id` — if they arrive as parameters, use them; if not, thread them from `predict_rows` :73-81.)

- [ ] **Step 4: Run it, watch it pass**

Run: `uv run pytest backend/tests/test_prediction.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/platform/prediction.py backend/tests/test_prediction.py
git commit -m "feat(backend): FR-116 — prediction resolves the offset model per request"
```

---

## Task 7 — backend: the backtest job resolves the ref

**Files:**
- Modify: `backend/src/app/worker/model_handlers.py` (`_backtest` :898-999 — resolution in the `load()` closure :920-975, the tuple it returns, and the `backtest_model` call :984-999)
- Modify: `backend/tests/test_backtests.py` (new test)

**Interfaces:**
- Consumes: `resolve_offset_model` (Task 5), Task 4's `backtest_model(model_offset=...)`.
- Produces: the backtest job scores a model-offset fit with its offset honoured.

- [ ] **Step 1: Write the failing test** in `test_backtests.py`, mirroring its existing backtest-job test: fit the Task 5 pair, run the backtest job for the residual model against v2's sibling version (or v2 itself, following FR-187's target rule as the file's existing tests do), assert `JobStatus.SUCCEEDED` and a sensible summary (`rows_scored == frame height`).

- [ ] **Step 2: Run it, watch it fail**

Run: `uv run pytest backend/tests/test_backtests.py -q`
Expected: FAIL — the summary scores without the offset (or the job errors on the missing array).

- [ ] **Step 3: Implement**

In `_backtest`'s `load()` (:920-975), add the same resolution block as Task 5's (guarded by `isinstance(spec, GlmSpec) and spec.offset.kind == "model"`), return `offset_source` in the tuple, and in the sync body compute the η array for the frame and pass `model_offset=eta` to the `backtest_model` call (:984-999) — the booster-bytes pattern: resolved on the loop, maths on the worker.

- [ ] **Step 4: Run it, watch it pass**

Run: `uv run pytest backend/tests/test_backtests.py backend/tests/test_model_offset_jobs.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/worker/model_handlers.py backend/tests/test_backtests.py
git commit -m "feat(backend): FR-116 — backtests honour the resolved model offset"
```

---

## Task 8 — backend: `POST /model-specs/validate` resolves the ref

**Files:**
- Modify: `backend/src/app/platform/model_specs.py` (`validate_spec` :141-148; new arm after the `OFFSET_MISSING` block :241-255)
- Modify: `backend/tests/test_model_specs.py` (new tests)

**Interfaces:**
- Consumes: Task 2's `SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE`, Task 5's resolver.
- Produces: validation reports the ref's problems before a Job is queued (WF-698 D2's rule applied to offsets-from-model).

- [ ] **Step 1: Write the failing tests** in `test_model_specs.py` (mirror its existing validate tests): a spec whose `offset_model_ref` names a missing model → a problem with `kind == SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE` whose `subject` is the ref; same for an unfitted model and a link mismatch; and the clean case — a valid ref yields no `MODEL_OFFSET_UNRESOLVABLE` problem.

- [ ] **Step 2: Run them, watch them fail**

Run: `uv run pytest backend/tests/test_model_specs.py -q`
Expected: FAIL — validation passes the bad refs silently.

- [ ] **Step 3: Implement** — after the `OFFSET_MISSING` block (:241-255):

```python
    if isinstance(spec, GlmSpec) and spec.offset.kind == "model":
        try:
            await resolve_offset_model(
                session,
                workspace_id=workspace_id,
                ref=str(spec.offset.offset_model_ref),
                caller_link=spec.link,
            )
        except PlatformError as exc:
            problems.append(
                SpecProblem(
                    kind=SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE,
                    subject=str(spec.offset.offset_model_ref),
                    message=f"the offset model cannot be used: {exc.detail}",
                )
            )
```

- [ ] **Step 4: Run them, watch them pass**

Run: `uv run pytest backend/tests/test_model_specs.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/platform/model_specs.py backend/tests/test_model_specs.py
git commit -m "feat(backend): FR-116 — spec validation resolves offset_model_ref before a job is queued"
```

---

## Task 9 — closure: the staged contract goes live, the roadmap records the slice

**Files:**
- Modify: `docs/specs/02-modelling.md` (FR-207's list at :325 gains the ninth live entry; §4.4's Task 1 block gains the "live" wording)
- Modify: `docs/roadmap.md` (the "WK-661 — outstanding work" table row 4 at :2569 struck DELIVERED; the count line :2560-2562 corrected; a new `#### WK-661 slice —` record after :2598's)
- No code changes.

- [ ] **Step 1: FR-207's ninth live entry** — append to the list at :325, matching the eighth entry's wording:

```
**`offset_model_ref` is the ninth, live 2026-08-21** (the offset-from-another-model slice), on `OffsetSpec` — `kind: "model"` with the canonical `model:slug@version` ref, GLM-to-GLM only; `GbmSpec` naming it, and refs naming non-fitted, non-GLM or link-mismatched models, are refused by name (`MODEL_OFFSET_REF_INVALID`).
```

And in the Task 1 §4.4 block, change "Live once the slice populates it (FR-207)." to "**Live 2026-08-21** (the offset-from-another-model slice)."

- [ ] **Step 2: Roadmap updates**

At :2569, strike the row 4 text and append: "~~`offset_model_ref` appears nowhere…~~ **— DELIVERED 2026-08-21:** `OffsetSpec.offset_model_ref` (renamed from the dead `model_ref` scaffold), GLM-to-GLM, resolved at fit/predict/backtest time, refused by name elsewhere." Correct the count line (:2560-2562) to "**one**, corrected 2026-08-21: slice 4 below is delivered" (EBM remains; FR-115's paragraph at :2591-2596 stays with its owner). Then add the slice record, matching the `#### WK-661 slice — …` heading, framing paragraph and `| Delivered | Evidence |` table format of the custom-metrics record (:2598-2612); its finding paragraph states the §0 resolution — the code scaffold's `model_ref` was the outlier, the spec and hand-authored contract agreed, and the silent-ignore defect in `fit_glm` was replaced by the implemented path plus named refusals. Keep every table's cell count valid — `scripts/audit-docs.py` checks the pipe counts.

- [ ] **Step 3: The full gate, both halves** (delegate to the `gate-runner` agent, or run directly):

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

Expected: every command's own exit code 0 (read each one's exit code, never `| tail`).

- [ ] **Step 4: Commit the docs, push the branch, open the PR**

```bash
git add docs/specs/02-modelling.md docs/roadmap.md
git commit -m "docs(roadmap): FR-116 — the offset-from-another-model slice record, live on the staged contract"
git push -u origin $(git branch --show-current)
gh pr create --fill
```

Then delegate CI watching to the `ci-watcher` agent (this repo's `gh` token cannot read check details and the commands exit 0 anyway — the agent reads `gh pr view --json mergeStateStatus`). Squash-merge and branch deletion per `git-hygiene` once green.

- [ ] **Step 5: Execution-corrections addendum** — if any step above deviated, append a dated addendum below with the mechanism, the fix, and which commits carry it (the Tweedie plan's addendum is the format).

---

## Execution corrections addendum

*(Dated entries appended here if the executor deviates — mechanism, fix, commits. None yet.)*

**2026-08-21 — Task 1, OQ-594's form broke the two-direction mirror.** The plan's Step 4 verbatim text presents OQ-594 as a heading-form block under open-questions.md's MODEL table. The repo's register is a 6-column table (`ID | Question | Options / trade-offs | Recommendation | Owner | Status`), and `scripts/audit-docs.py`'s mirror check only sees **bolded** OQ references — a heading-form block passes the audit while no spec §10 raises the id, silently breaking the spec-change skill's two-direction mirror (the spec's §10 table carries a row for every OQ, open ones included: OQ-593 is the precedent). **Fix:** OQ-594 converted to a register row in `docs/open-questions.md`, and a matching row added to `02-modelling.md` §10's table; both direction checks now hold ("74 open questions, all mirrored", audit exit 0). **Commits:** the Task 1 commit (`docs(spec): FR-116 defined — offset from another model, GLM-to-GLM v1 (OQ-594)`) was amended with the fix before anything depended on it.

**2026-08-21 — Task 4, type-III reduced fits dropped the offset.** The plan threads `model_offset` through `compute_diagnostics`' four `predict_glm` call sites only. `_type_iii`'s internal reduced **fits** (diagnostics.py, the `fit_glm` call in the drop-one-term loop) were not among them: `reduced_spec` is a `model_copy` of the caller's spec, so for a `kind="model"` spec every reduced fit raised `MODEL_OFFSET_MISSING` — and the pre-existing `except GlmFitError: continue` guard (in place for genuinely degenerate reduced designs) swallowed it, so a model-offset fit with ≥2 factors got a **silently empty** type-III table. Exactly the silent-defect class the slice exists to replace. **Fix:** the reduced fit passes `model_offset=model_offset` (the same `model_offset_train` array `compute_diagnostics` supplied — the reduced fit is on the same `train` frame the array was validated against). A regression test (`test_type_iii_reduced_fits_keep_the_offset`, two factors, negative-first: before the fix it asserts `dict_keys([])`) pins presence for both terms and — the discriminating assertion — that the factor whose effect lives *inside* the offset is insignificant on top of it, which fails again if a future change strips the offset from the reduced design. **Commits:** the follow-up commit `feat(pricing-core): FR-116 — type-III reduced fits keep the model offset`.

**2026-08-21 — Task 9 gate, the plan's verbatim Task 2 test text was not ruff-clean.** The full gate found two ruff violations in `packages/model-schema/tests/test_offset_model_spec.py`, both from the plan's literal snippet: I001 (the `from model_schema import …` needs a blank line after the `import` block) and RUF043 (`match="kind.*model"` must be raw). **Fix:** blank line added, string made raw; the file is now ruff-clean and the gate is fully green. **Commits:** the fixup commit `chore(model-schema): FR-116 — ruff fixes on the new offset spec tests`.

**2026-08-21 — Task 9, four roadmap corrections to the closure text.** (i) The plan's count-line wording "**one**, corrected 2026-08-21: slice 4 below is delivered" under-counts: the chain's "three" correction had already accounted only slices 1–2, and the Tweedie slice (slice 3, delivered 2026-08-21) never updated the line — so the honest increment from three to one is **two** slices. Final wording: "slices 3 and 4 below are delivered." (ii) Row 4's name cell now struck with the DELIVERED marker, matching rows 1–3 (the plan's given text covered only the description cell). (iii) The "FR-115 and FR-116 remain unbuilt" sentence in the three-requirements paragraph now credits FR-116 to this slice and leaves FR-115 unbuilt with its owner — the paragraph stays with its owner, only the false claim is corrected. (iv) The slice record's framing "spanning 2026-08-20 → 08-21" corrected to "spanning 2026-08-21" — the slice was planned and executed on one day. **Commits:** the Task 9 docs commit.

**2026-08-21 — Task 9 merge, two post-merge observations.** (i) The ci-watcher's first reading — `mergeStateStatus UNSTABLE` a minute after PR creation — was the **in-flight** state, not a failure: all three workflows (docs 10s, frontend 1m14s, python) completed `success`, and the PR merged CLEAN. The disambiguator the trap note does not name: `gh run list --branch <branch> --json status,conclusion` shows per-workflow state (the token reads it) while `statusCheckRollup` is blocked. (ii) `gh pr create --fill` titled the PR from the branch name, so main's squash commit reads `worktree offset model (#126)` (`e36e5d0`) rather than a conventional FR-116-tagged message — cosmetic, on main, and not rewriteable without a force-push this repo forbids; flagged to the maintainer. **Commits:** PR #126, squash-merged 2026-08-21 20:00Z, branch deleted.

**2026-08-21 — Task 3, the plan's `match="MODEL_OFFSET_MISSING"` cannot match a `GlmFitError`.** `pytest.raises(match=...)` searches `str(exc)`, and this repo's error classes deliberately separate the code from the message (`GlmFitError(code, message)`, glm.py:84-94; `PredictionError` the same shape) — the message the plan's own Step 3 helper specifies never contains the code string, so the literal Step 1 test text could not pass against the literal Step 3 implementation. **Fix:** in `test_a_model_offset_without_the_array_is_refused`, `with pytest.raises(GlmFitError, match="MODEL_OFFSET_MISSING"):` became the repo's established assertion for this class (test_glm.py:144-146, :447-454): `with pytest.raises(GlmFitError) as refused:` + `assert refused.value.code == "MODEL_OFFSET_MISSING"`. No design change: the exception, code, message and terms are exactly the plan's Step 3 text, and the invariant asserted (the named refusal) is unchanged. The other two refusal tests match message text ("rows", "finite") and were unaffected. Note for Task 4's executor: the same `match="MODEL_OFFSET_MISSING"` pattern appears in that task's `PredictionError` tests, and `PredictionError` separates code from message the same way — those assertions need the same `.code` treatment. **Commits:** the Task 3 commit (`feat(pricing-core): FR-116 — fit_glm honours a supplied model offset, named refusal otherwise`).

**2026-08-21 — Task 4, follow-ups to the Task 3 entry.** Three adaptations, all in the test text, none in the implementation (which is the plan's Step 3 verbatim):
1. As predicted above, all three `PredictionError` refusals took the `.code` treatment: `with pytest.raises(PredictionError) as refused:` + `assert refused.value.code == "MODEL_OFFSET_MISSING"` instead of `match="MODEL_OFFSET_MISSING"`.
2. `summary.rows_scored` does not exist — the plan's own parenthetical said to grep `summary\.` in `test_backtests.py` and use what the existing tests assert; that is `summary.partition.rows` (test_backtests.py:130, :230). The assertion became `assert summary.partition.rows == data.height`.
3. `result.deviance` does not exist either — `DiagnosticsResult` nests it as `result.glm.deviance`, which is what test_diagnostics.py asserts (:181, :204). The assertion became `assert result.glm.deviance > 0`.
4. The plan's literal backtest ref block passed `dataset_version_ref="dataset_version:book@2"` **and** `fitted_on_ref="dataset_version:book@2"` — identical, which `BacktestSummary`'s own validator refuses ("fitted on", FR-187). The plan's parenthetical says the refs "follow FR-187's invariant that the backtest target is not the fitted-on version", so the target is `dataset_version:book@2` and the fitted-on is `dataset_version:book@1` — the parenthetical's rule, not the sketch's literal strings.

**Observation, resolved 2026-08-21 by the follow-up commit above:** the plan threads `model_offset` at the four `predict_glm` call sites only. The type-III reduced **fit** inside `_type_iii` (diagnostics.py :499-505, not one of the four) did not receive the array — for a `kind="model"` spec with ≥2 factors, every reduced `fit_glm` raised `GlmFitError(MODEL_OFFSET_MISSING)`, which the existing `except GlmFitError: continue` swallowed, so `type_iii_tests` came back silently empty for such a fit. Task 4's own diagnostics test never reached the loop (single factor ⇒ early return). **Resolved:** the reduced fit now receives `model_offset` and `test_type_iii_reduced_fits_keep_the_offset` pins it (see the Task 4 type-III entry above).

**Commits:** the Task 4 commit (`feat(pricing-core): FR-116 — prediction, diagnostics and backtest take the resolved model offset`).


**2026-08-21 — Task 5, three adaptations, one test-data fix.**

1. **Job-row error-code assertions don't exist.** The task brief's "grep FAILED in test_model_jobs.py for the pattern" found only `is JobStatus.FAILED` — no job-row code assertion — because `execute_job` maps every handler exception to `JOB_HANDLER_FAILED` (worker/tasks.py). The refusal tests therefore assert `execute_job(...) is JobStatus.FAILED` **and** read the named code the established way (`test_model_jobs_gbm.py:270-290`): the handler run exactly as the runner runs it, against a real queued Job, with `pytest.raises(PlatformError)` and `caught.value.code`. `_refusal_code` in `test_model_offset_jobs.py` is that helper.
2. **`GlmFitResult.offset_model_ref` is populated nowhere else.** The plan's happy-path test asserts the pinned ref on the fit result, and `record_fit` persists it via `model_dump` — but no plan step sets it (`fit_glm` constructs `GlmFitResult` without the field). The backend `_fit` GLM branch stamps it after the fit: `result.model_copy(update={"offset_model_ref": str(spec.offset.offset_model_ref)})` — "what was actually constructed is recorded on the fit result", per the plan's own spec note. No pricing-core change; Task 3's commit is untouched.
3. **The plan's `model_service.load_factors` / `transform_service.load_bandings` aliases don't exist in `platform/modelling.py`** (they are `model_handlers.py` aliases). The resolver uses the module-local `load_factors` and `transformations.load_bandings/load_groupings` (added to the `app.platform` import line; no import cycle).
4. **Test-data fix: `resid_flag` came through ingestion as String, not Float64.** `read_tabular` reads every column as a string and `CAST_RECIPE` casts only `exposure_years`/`claim_count`/`claim_amount_minor`, so the plan's `resid_flag`-on-a-float-column-⇒-continuous assumption failed: the fit produced the term `resid_flag[0.0]` (categorical level deviation, signal still recovered at ±0.2) and the happy path's `c.term == "resid_flag"` lookup raised StopIteration. **Fix:** the residual book's ingest uses its own cast recipe (`_RESIDUAL_CAST_RECIPE` — the base three casts plus `resid_flag: float`, `claim_count2: int`) via `_residual_ingest`/`_residual_version` (mirrors of `test_data_jobs._ingest`/`test_model_jobs._validated_version`). The coefficient assertion then holds: `resid_flag` estimate ≈ 0.2 (rel 0.1) at n=4000, seed 20260821.

**Commits:** the Task 5 commit (`feat(backend): FR-116 — the fit job resolves offset_model_ref and fits on the referenced linear predictor`).

**2026-08-21 — Task 6, three adaptations, none in the implementation.**

1. **"A residual model whose ref names a deleted model" cannot exist through the real path.** The DB refuses deleting a fitted model by design (`models_fitted_undeletable` trigger, migration `b2c3d4e5f6a7`; "Archive it" — and archiving keeps the row, so `load_model` still resolves it), and fit-time resolution refuses a ghost ref before a Job runs. The negative test therefore simulates the state the repository's established way (`test_a_glm_fitted_before_the_covariance_blob_says_so_rather_than_going_quiet`): the real residual fit result is copied onto a **reserved** residual model whose ref is `model:ghost@1` (`ModelRow.__table__.update()` — the R2 trigger permits the write because `OLD.fit_result IS NULL` on a draft), then `predict_rows` asserts the refusal is `NOT_FOUND` / 404, not a 500. The assertion the task specifies is unchanged; only the construction of the state differs. Note the `row is None` arm in `resolve_offset_model` is unreachable — `load_model` itself raises `NOT_FOUND` — observed, not changed (Task 5's code, identical outcome).
2. **The plan's `_residual_frame` does not exist in `test_model_offset_jobs.py`.** The Task 5 commit's helpers are `_residual_book` (CSV bytes), `_residual_spec`, `_residual_row`, `_residual_version`, `_RESIDUAL_CAST_RECIPE`; the pair-fitting setup was assembled in `test_prediction.py` as a `_fitted_residual_pair` helper reusing those (the file's cross-test import style). `resid_flag` is a float column via the Task 5 recipe, as the brief requires.
3. **Resolution placement.** The plan's "add before the `predict_glm` call" is implemented as the first statement of `_score_glm`'s `try` — inside it deliberately, so a `linear_predictor` failure on the request frame (rows missing the offset model's factor columns) maps to the existing 409 `_unscoreable` refusal instead of an unguarded 500, while `resolve_offset_model`'s `PlatformError` (`NOT_FOUND` 404) propagates untouched (it is neither `ModellingError` nor `PredictionError`). `session`/`workspace_id` were threaded from `predict_rows` per the plan's parenthetical.

**Commits:** the Task 6 commit (`feat(backend): FR-116 — prediction resolves the offset model per request`).

**2026-08-21 — Task 7, two adaptations in the test, none in the implementation.**

1. **The backtest target is v3 of the residual book, not "v2 itself".** FR-187's rule — the target must not be the fitted-on version nor a split part — forces a third version. The plan's sketch allowed either option; I used the first: `_later_residual_period` (mirroring `_later_period`'s ingest→validate→promote, with `_RESIDUAL_CAST_RECIPE` so `resid_flag` stays a float column per the Task 5 addendum) ingests `_residual_book(seed=20260822)` — fresh draws under the same truth — as v2's sibling in the same dataset. The pair fitting reuses Task 6's `_fitted_residual_pair` from `test_prediction.py`, per that task's addendum.
2. **One assertion beyond the plan's literal row count.** The plan's text names `JobStatus.SUCCEEDED` + the row-count assertion; the file's convention (its own docstring: "a backtest that did not move is one that scored the wrong frame") asks for a known answer. The test adds `partition.ae_overall == approx(1.0, abs=0.15)` — the residual model is correctly specified on the same truth, so a backtest that honours the offset reads ≈1, while a backtest that dropped it would score `exp(β̂·resid_flag)` alone and read ≈ e². Also mirrors the artifact-test trio (`model_ref` startswith `model:`, `dataset_version_ref != fitted_on_ref`, `partition.rows == 4000`); the row attribute is `partition.rows`, per the Task 4 addendum.

Implementation is the plan's Step 3 verbatim: the `isinstance(spec, GlmSpec) and spec.offset.kind == "model"`-guarded `resolve_offset_model` block in `load()`, `offset_source` as the tuple's 12th element (`OffsetModelSource | None` on the annotation), the η array computed on the worker thread with `linear_predictor` (added to the `backtest_model` import), `model_offset=model_offset` to `backtest_model`. Failure mode confirmed before the fix: `PredictionError(MODEL_OFFSET_MISSING)` from `_offset` (predict.py:154) → job `FAILED`. **Commits:** the Task 7 commit (`feat(backend): FR-116 — backtests honour the resolved model offset`).

**2026-08-21 — Task 8, test construction only; the implementation is the plan's Step 3 verbatim.** The Task 8 brief names the four cases and the helpers to seed them; the concrete choices, all inside the brief's bounds:
1. **Seeding split between the two helper modules.** The ghost and unfitted tests need only the residual book's artifacts, so they use `_residual_version`/`_residual_spec`/`_base_spec` from `test_model_offset_jobs.py` via a local `_residual_ready` helper (mirror of the file's `_ready`). The link-mismatch and clean cases need a fitted base GLM, so they use `_fitted_residual_pair` from `test_prediction.py` (which returns the pair plus `v2_id`/`resid_flag_id`/`split2`/`ref` — exactly what a further `_residual_spec` reservation needs). Importing `test_model_offset_jobs` registers the data and model handlers at module level, as it already does for `test_prediction.py`.
2. **Assertion strength.** The negatives assert `result.ok is False` (the spec is otherwise sound, so the offset problem is the only one) and the clean case asserts `result.ok is True` — the file's `test_a_sound_spec_validates` style — rather than the brief's minimal "no `MODEL_OFFSET_UNRESOLVABLE` problem". The clean case would also catch an unexpected resolver crash.
3. **No drift in the cited anchors:** the `OFFSET_MISSING` block was exactly at model_specs.py:241-255, and `resolve_offset_model`/`PlatformError.detail`/`SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE` all exist as the plan states. Per the Task 6 addendum's observation, `load_model` raises `NOT_FOUND` itself, so the resolver's `row is None` arm never fires for the ghost case — same `PlatformError` outcome, nothing changed. Failure mode before the fix: `SpecValidation(ok=True, problems=())` for all three bad refs — validation passed them silently. **Commits:** the Task 8 commit (`feat(backend): FR-116 — spec validation resolves offset_model_ref before a job is queued`).
