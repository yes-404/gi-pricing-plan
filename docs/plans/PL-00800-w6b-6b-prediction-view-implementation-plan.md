---
id: PL-800
family: plan
kind: leaf
title: W6b-6b — Prediction View Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-25
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-25-w6b-6b-prediction-view.md
---

# W6b-6b — Prediction View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `02` §5.3's **Prediction** view at `/models/:slug/predict` — a generated
single-row input form, the scored expectation, and the uncertainty *or* the named refusal,
each reason rendered as what the specification says it means.

**Architecture:** One view, one API module, one pure input-resolver module, one presentational
component. The view resolves `slug → Model`, derives the input columns the model actually needs
from its pinned Factors (expanding interaction operands and, where the offset is another model,
that model's factors too), POSTs one row to `POST /api/v1/models/{id}/predict`, and renders
`Prediction`. There is no Job and no polling: this route answers **200**.

**Tech Stack:** Vue 3 `<script setup lang="ts">`, vue-router 5.2.0 function-mode props, Tailwind,
Vitest + `@testing-library/vue` + happy-dom. Types come from `@/api/generated/schema` only.

**Spec:** [`../specs/02-modelling.md`](../specs/02-modelling.md) (§5.1 endpoint table, §5.3 view
table, FR-194/198/199/195/196/197/200/201/180). Cross-references
[`../specs/07-platform.md`](../specs/07-platform.md) §1.3 R1 and
[`../specs/00-overview.md`](../specs/00-overview.md) FR-24.

---

## Global Constraints

Copied verbatim from the specification and `CLAUDE.md`. Every task's requirements implicitly
include this section.

- **Never hand-write an API type.** Every shape in this slice is
  `components["schemas"][…]` from `@/api/generated/schema`, which is VCS-ignored and generated
  from `model-schema` (`CLAUDE.md` §2). A shape defined twice will diverge, and here a diverged
  shape is a mispricing.
- **Vue 3 Composition API with `<script setup lang="ts">` only** — never Options API, JSX, React.
- **Branch on `problem.code`, never on `status`.** `frontend/src/api/problem.ts` states it on the
  field itself: *"The stable machine code. Branch on this, never on `status` — several codes
  share a status."* This slice has five distinct codes sharing `409`.
- **`tsconfig.app.json` is strict**, with `noUncheckedIndexedAccess`,
  `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `isolatedModules` and
  `noFallthroughCasesInSwitch`. An indexed read is `T | undefined`; an optional property may not
  be assigned `undefined` explicitly.
- **`vitest run` evaluates `.test-d.ts`** — `frontend/vitest.config.ts` sets
  `typecheck: { enabled: true, include: ["src/**/*.test-d.ts"], tsconfig: "./tsconfig.app.json" }`.
  A type-level assertion in this slice is a real gate, not documentation.
- **Money is integer pence/cents, or Decimal in the rating path — never float** (`CLAUDE.md` §7).
  Nothing in this slice is money: `PredictedRow.expected` is a modelled response (a count, a
  severity in the response column's own units, a rate), and FR-10 permits floats in
  diagnostics. **Do not add a `_minor` suffix to anything here** and do not format any value on
  this page as currency.
- **The generated contract is the floor, not the ceiling** (OQ-587, decided 2026-08-21).
  Anything this view needs beyond what the contract publishes is a **new requirement raised at
  build time and brought to the maintainer** — never a silent addition and never a frontend-side
  re-derivation.
- **Run the full gate before pushing, both halves.** `.claude/skills/dev-commands` has the traps;
  a Python-only "gate" has been green here while the frontend was red.

---

## What binds this slice

### The requirement set is nine

Derived from the specification first and then evidenced, per `CLAUDE.md` §13. Read each row's
predicate — not its id — before implementing against it.

| Req | What it obliges *this view* to do |
|---|---|
| **FR-194** | Render the expectation **and** an uncertainty measure: a GLM interval from the covariance matrix, or for a GBM either a quantile-model interval or an explicit `unavailable` **with the reason**. Never the expectation alone. |
| **FR-198** | The three GBM reasons — `no_interval_models_fitted`, `interval_models_not_approved`, `interval_models_stale`. **The variance-model approximation is not offered at all, at any setting**: the view must not offer a control that would produce one, because *"a wrong interval on a price is worse than no interval."* |
| **FR-199** | Paired quantile models are opt-in at 2–3× fit cost. Crossing quantiles are *"detected, reported in the diagnostics, and **never silently reordered**"* — so when the API refuses with `MODEL_INTERVAL_UNAVAILABLE`, the view reports the refusal and **must not** swap `lower` and `upper` to make a displayable interval. |
| **FR-195** | `covariance_not_stored` is *"a fourth reason beside FR-198's three and it is **not** one of them"* — do not group it with them in the copy. The expectation is still returned and still rendered. |
| **FR-196** | Exactly one confidence-side kind, `confidence_interval_mean`, covering `E[Y\|x]`. It *"is never silently widened to become"* a process-variance prediction interval. The view labels it as a mean interval and never as a range for an individual outcome. |
| **FR-197, limb A only** | *"every response carrying them states the basis they were computed on"* — render `uncertainty.basis` beside the interval whenever it is present. `unpenalised_information_matrix` means the interval is **wider** than the shrunk estimate warrants, and the view says so. **This slice evidences the prediction path and only that.** See the limb split below; do not book FR-197 delivered on the strength of this slice. |
| **FR-200** | The reason **semantics**: (ii) `interval_models_not_approved` means the bounds are *"less advanced than the model they bound"*, **not** unapproved outright; (iii) `interval_models_stale` means *"the central Model is `superseded`"*. Both are copy obligations — get them wrong and the page tells an actuary the opposite of what happened. |
| **FR-201** | `quantile_pair_interval` is a **third kind**, neither of FR-196's two names, and it covers **`Y` itself**, not `E[Y\|x]`: *"a reader comparing a GBM's bound with a GLM's must be able to see they are not the same kind of claim."* On this kind `basis` is **forbidden** and `interval_models` is **required**. |
| **FR-180** | An EBM prediction is served and states `model_type_has_no_interval`. Each of the other four reasons *"states something false of an EBM"*, so the view must not fall back to one. |

**FR-193 is not in this set.** Its full row is *"`pricing-core` can score any persisted Model
from its declarative artifact alone (ADR-705), with no dependency on the fitting session. GLM
scoring requires no `glum`; GBM scoring loads the JSON booster."* That is a `pricing-core`
backend capability; a frontend-only slice cannot evidence it. An earlier draft of this slice's
material cited it for the 200-not-202 fact, which it does not state.

**FR-200(iv) is out of scope.** *"Exactly one bound per side … a second on either side is
refused with `MODEL_INTERVAL_PAIR_INVALID`"* is a **fit-time** refusal:
`MODEL_INTERVAL_PAIR_INVALID` is raised only in `backend/src/app/platform/modelling.py`, six
times, and never in `backend/src/app/platform/prediction.py`. The prediction path cannot produce
it. Do not add a branch for it.

### FR-197 splits into two limbs, and this slice evidences one

Ruled by `w6b-manager` 2026-08-25. FR-197 reads on *"every response carrying"* standard
errors and intervals, and there are two such responses. They are in different states, so booking
the requirement as one thing gets it wrong in one direction or the other.

**Limb A — the prediction path. Discharged, and this slice evidences it.**
`Uncertainty.basis` in `packages/model-schema/src/model_schema/prediction.py` is a real
serialised field citing FR-197 in its own comment, and the model validator beneath it
refuses an interval that carries none: *"uncertainty is … with no basis. FR-197: an interval
read off a penalised fit's covariance matrix is not the interval that fit deserves."* It is on
the wire, in `docs/contracts/openapi/generated.json`, and Task 3 renders it.

**Limb B — the coefficient path. Not evidenceable, and not this slice's.** `Coefficient` in
`modelling.py` carries `std_error` and `ci_95` and has **no** basis field — with
`extra="forbid"`, so one cannot even be attached ad hoc. `Model.uncertainty_basis` is a Python
`@property`, which Pydantic does not serialise, so the value exists in the backend and appears
nowhere in the published contract. *"Every response carrying them states the basis"* therefore
binds a response with nowhere to put it. `ModelDetailView.vue` renders both columns and states no
basis, and it cannot: the fix is a contract change (finding 1).

**Book limb A only. Do not book FR-197 delivered on this slice.** Limb B goes to the closure
record as **not started**, backend owner, outliving WK-664.

### This route answers 200, so there is no Job to poll

`02` §5.1 states it directly, in the row for `POST /api/v1/models/{id}/predict`: **"200** Score
rows with FR-194's uncertainty (dev/debug scale, row-capped; production scoring is `03`)".

`07` §1.3 **R1** explains why that is consistent rather than an exception: *"Everything slow is a
Job. Any operation that can exceed 2 s returns `202` with a Job, has progress, is cancellable, and
persists its result (FR-13, NFR-457)."* Predict is capped at
`prediction_service.MAX_PREDICT_ROWS` = **1000** rows the caller sent in the request body, so it
does not reach R1's threshold.

The same §5.1 table gives the contrast the implementer needs: `POST /models` is 202, `/compare` is
202, backtest and transparency are 202 — **predict is 200**. Do not import `Job`, do not poll,
do not build a progress affordance. The response *is* the answer.

> **Cite the §5.1 row first and R1 second.** R1 is a rule about 202; deriving 200 from it is an
> inference, and an inference frozen into a plan reads later as a statement.

### FR-24 — the §5.3 Contents cell binds nothing here

`02` §5.3's Prediction row reads *"Ad-hoc scoring against a fitted Model: input row or uploaded
batch, the prediction with its interval where the model type offers one, and the refusal by name
where it does not (FR-180)"*.

**FR-24 makes a §5.3 Contents cell prose that binds nothing**, with a per-cell carve-out for
seven named cells: `01`'s validation report banner, `01` §5.3's interaction requirement paragraph,
`02`'s Diagnostics, `02`'s Objective certificate, `03`'s DAG designer, `05`'s Drift, and `07`'s
Jobs. **Prediction is not among the seven.** Checked per-cell, not by an id sweep — FR-24
warns that *"an id-matching sweep across the seven will report all of them green."*

Two consequences, and the second is the one that gets missed:

1. **"uploaded batch" is not an obligation.** The cell mentions it; the cell binds nothing. This
   slice ships one row (see the ruling below), and that is not a shortfall against a requirement.
2. **"the refusal by name" is still binding — from FR-180, which the cell cites.** The
   requirement is the source; the cell is only where it happens to be quoted.

### Input affordance: one generated row (decided)

Ruled by `w6b-decision-maker`, 2026-08-25: **a generated form, one row.** Not a JSON textarea and
not both. None of the nine requirements binds the input affordance, and `01`'s uploaded-batch
phrasing lives in a cell FR-24 makes non-binding.

The form is cheap because the pieces already exist: `listFactors(datasetId)` is already in
`frontend/src/api/models.ts`, and `Factor.source_columns` is already on the published read shape.

### The input-column derivation has three traps, all verified

The naive form — one field per `spec.factors` entry — is **wrong three ways**. Each was checked
against the source at `origin/main`.

1. **`spec.factors` holds Factor *ids*, not column names.** `GlmSpec.factors` is
   `array of uuid` in `docs/contracts/openapi/generated.json`. The columns come from each
   Factor's `source_columns`, which is a separate read.

2. **An `interaction` Factor has *empty* `source_columns`, by validated invariant.**
   `packages/model-schema/src/model_schema/modelling.py`'s `_columns_match_the_type` raises if an
   interaction names any: *"Its columns are its operands'; naming them again is a second
   statement of one fact, and the two disagree the first time an operand is re-versioned onto
   another column."* The operand ids are published as **`operand_factor_ids`** on `Factor`, and
   the spec's `factors` list does **not** contain them — `load_factors` expands them server-side
   and its docstring says *"One level of expansion is enough."* The form must expand them the
   same one level, or every interaction model renders a form missing real columns.

3. **`offset.kind === "model"` needs the *referenced* model's factor columns too.**
   `backend/src/app/platform/prediction.py`'s **`_score_glm`** holds the branch, and it calls
   `linear_predictor(source.fit, frame, source.factors, source.spec, …)` — the **same `frame` the
   caller sent**, with the offset source model's factors. A form built from the central model's
   factors alone therefore always fails with `MODEL_TERM_UNRESOLVED`, raised in
   `packages/pricing-core/src/pricing_core/modelling/predict.py`'s **`_term_vectors`**: *"term …
   names factor …, which this frame does not resolve. Scoring with the term dropped would
   silently move every prediction toward the base level."* `OffsetSpec.offset_model_ref` is published as an ID-3 ref
   matching `^model:[a-z0-9][a-z0-9-]{1,62}@[1-9][0-9]*$` — the exact pattern
   `parseModelRef` in `frontend/src/api/comparisons.ts` already implements. **Reuse it; do not
   write a second copy of that regex.**

Task 2 handles all three in one pure function so that they are testable without a component.

---

## File Structure

| File | Responsibility |
|---|---|
| `frontend/src/api/predictions.ts` | **Create.** Re-exported contract types, `predict()`, and the reason/kind copy that FR-198/195/200/201/180 fix. |
| `frontend/src/api/predictionInputs.ts` | **Create.** Pure: `requiredColumns(model, factorsById)` → the column set + the offset-model ref to resolve. No I/O. |
| `frontend/src/api/__tests__/predictions.test.ts` | **Create.** `predict()` request shape and the copy map. |
| `frontend/src/api/__tests__/predictions.test-d.ts` | **Create.** Type-level: `basis` forbidden on `quantile_pair_interval` is *not* expressible in the generated types — pin what *is*. |
| `frontend/src/api/__tests__/predictionInputs.test.ts` | **Create.** The three traps, one test each. |
| `frontend/src/components/PredictionUncertainty.vue` | **Create.** Renders one `Uncertainty` — three kinds, five reasons, the basis caveat. |
| `frontend/src/components/__tests__/PredictionUncertainty.test.ts` | **Create.** Every kind and every reason. |
| `frontend/src/views/PredictionView.vue` | **Create.** The page: form, submit, result, error taxonomy. |
| `frontend/src/views/__tests__/PredictionView.test.ts` | **Create.** Load, submit, and each 409/422 branch. |
| `frontend/src/router/index.ts` | **Modify.** Add the `/models/:slug/predict` record. |
| `frontend/src/router/__tests__/index.test.ts` | **Modify.** Assert resolution of the new path. |
| `frontend/src/views/__tests__/fixtures.ts` | **Modify.** Add `GLM_MODEL`, `PREDICTION`, and factor fixtures. |
| `docs/research/w6b-6b-prediction-material.md` | **Modify.** Mark superseded by this plan (see Task 5). |

---

## Task 1: The prediction API module

**Files:**
- Create: `frontend/src/api/predictions.ts`
- Create: `frontend/src/api/__tests__/predictions.test.ts`
- Create: `frontend/src/api/__tests__/predictions.test-d.ts`

**Interfaces:**
- Consumes: `request` from `./client` (already exists, signature in `frontend/src/api/client.ts`).
- Produces: `predict(modelId, row)`, `unavailableCopy(reason)`, `intervalClaim(kind)`, and the
  re-exported types `Prediction`, `PredictedRow`, `Uncertainty`, `UncertaintyKind`,
  `UncertaintyBasis`, `UnavailableReason`, `IntervalModels`.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/api/__tests__/predictions.test.ts`:

```ts
import { afterEach, describe, expect, it, vi } from "vitest";

import { intervalClaim, predict, unavailableCopy } from "@/api/predictions";

afterEach(() => {
  vi.unstubAllGlobals();
});

const MODEL_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";

describe("predict", () => {
  it("POSTs the row wrapped in `rows` and returns the body", async () => {
    const body = { model_id: MODEL_ID, rows: [{ expected: 0.13 }] };
    const fetchMock = vi.fn(
      async () =>
        new Response(JSON.stringify(body), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await predict(MODEL_ID, { driver_age: 42 });

    expect(result).toEqual(body);
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(String(url)).toContain(`/api/v1/models/${MODEL_ID}/predict`);
    expect(init!.method).toBe("POST");
    // `PredictRows` requires `rows` and sets `additionalProperties: false`.
    expect(JSON.parse(String(init!.body))).toEqual({ rows: [{ driver_age: 42 }] });
  });

  it("sends no Idempotency-Key: nothing is persisted, so there is nothing to deduplicate", async () => {
    const fetchMock = vi.fn(
      async () =>
        new Response(JSON.stringify({ rows: [] }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await predict(MODEL_ID, {});

    const headers = fetchMock.mock.calls[0]![1]!.headers as Record<string, string>;
    expect(headers["Idempotency-Key"]).toBeUndefined();
  });
});

describe("unavailableCopy", () => {
  it("does not call covariance_not_stored a GBM reason (FR-195)", () => {
    // FR-195: "a fourth reason beside FR-198's three and it is not one of them".
    expect(unavailableCopy("covariance_not_stored").family).toBe("glm");
    expect(unavailableCopy("no_interval_models_fitted").family).toBe("gbm");
    expect(unavailableCopy("interval_models_not_approved").family).toBe("gbm");
    expect(unavailableCopy("interval_models_stale").family).toBe("gbm");
    expect(unavailableCopy("model_type_has_no_interval").family).toBe("ebm");
  });

  it("reads `not_approved` as FR-200(ii), not as unapproved outright", () => {
    const copy = unavailableCopy("interval_models_not_approved").detail;
    expect(copy).toContain("less advanced");
    expect(copy).not.toMatch(/\bnot approved\b/);
  });

  it("reads `stale` as FR-200(iii): the central model is superseded", () => {
    expect(unavailableCopy("interval_models_stale").detail).toContain("superseded");
  });
});

describe("intervalClaim", () => {
  it("separates the two claims FR-201 exists to keep apart", () => {
    // FR-196: confidence_interval_mean covers E[Y|x].
    // FR-201: quantile_pair_interval covers Y itself.
    expect(intervalClaim("confidence_interval_mean")).toContain("average");
    expect(intervalClaim("quantile_pair_interval")).toContain("individual");
    expect(intervalClaim("confidence_interval_mean")).not.toEqual(
      intervalClaim("quantile_pair_interval"),
    );
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- predictions.test.ts`

Expected: FAIL — `Failed to resolve import "@/api/predictions"`.

- [ ] **Step 3: Write the implementation**

Create `frontend/src/api/predictions.ts`:

```ts
import { request } from "./client";
import type { components } from "./generated/schema";

export type Prediction = components["schemas"]["Prediction"];
export type PredictedRow = components["schemas"]["PredictedRow"];
export type Uncertainty = components["schemas"]["Uncertainty"];
export type UncertaintyKind = components["schemas"]["UncertaintyKind"];
export type UncertaintyBasis = components["schemas"]["UncertaintyBasis"];
export type UnavailableReason = components["schemas"]["UnavailableReason"];
export type IntervalModels = components["schemas"]["IntervalModels"];

/** One row of caller-supplied column values. `PredictRows.rows` items are open objects. */
export type PredictionInputRow = Record<string, string | number | boolean | null>;

/**
 * Score one row (`02` §5.1, FR-194).
 *
 * **200, not 202.** The §5.1 row for this endpoint states the code directly, and `07` §1.3 R1
 * explains why that is not an exception to "everything slow is a Job": the endpoint reads at
 * most `MAX_PREDICT_ROWS` rows the caller sent in the body, so it cannot exceed R1's 2 s
 * threshold. There is no Job, no poll and no result blob — the response is the answer.
 *
 * No `Idempotency-Key`. `00` §5.4 asks for one on "every POST that creates a Job or artifact";
 * this creates neither, and a retried score is the same arithmetic on the same numbers.
 */
export function predict(modelId: string, row: PredictionInputRow): Promise<Prediction> {
  return request<Prediction>(`/models/${encodeURIComponent(modelId)}/predict`, {
    method: "POST",
    body: { rows: [row] },
  });
}

/**
 * What an `unavailable` reason means, in the specification's own reading of it.
 *
 * `family` exists because FR-195 is explicit that `covariance_not_stored` is "a fourth
 * reason beside FR-198's three and it is **not** one of them", and FR-180 is
 * explicit that each of the other four "states something false of an EBM". Grouping them in
 * the UI would undo both statements.
 */
export function unavailableCopy(reason: UnavailableReason): {
  family: "glm" | "gbm" | "ebm";
  headline: string;
  detail: string;
} {
  switch (reason) {
    case "no_interval_models_fitted":
      // FR-198: paired quantile models are opt-in, at 2-3x fit cost (FR-199).
      return {
        family: "gbm",
        headline: "No interval models were fitted",
        detail:
          "Interval bounds are opt-in for a boosted model: they are two more fits, at two " +
          "to three times the cost of this one. Until they exist there is no interval to " +
          "report, and an approximation is not offered in their place.",
      };
    case "interval_models_not_approved":
      // FR-200(ii) — NOT "the bounds are unapproved".
      return {
        family: "gbm",
        headline: "The bounds are less advanced than this model",
        detail:
          "The interval bounds sit at an earlier lifecycle status than the model they " +
          "bound, so quoting them would put an unreviewed number beside a reviewed one. " +
          "Advance the bounds to at least this model's status.",
      };
    case "interval_models_stale":
      // FR-200(iii) — the literal reading of FR-198's "superseded version".
      return {
        family: "gbm",
        headline: "This model version has been superseded",
        detail:
          "A superseded model is still scoreable, and its bounds are still attached to it " +
          "— but the family has moved past this version, so the interval is not reported " +
          "without saying so.",
      };
    case "covariance_not_stored":
      // FR-195. Note what this reason is NOT: a blob that should exist and does not is
      // a platform fault and surfaces as one. This is reachable only when the artifact
      // itself records no blob.
      return {
        family: "glm",
        headline: "This fit stored no covariance matrix",
        detail:
          "The interval is read off the covariance matrix, and this model was fitted " +
          "before that matrix was retained. The expectation below is unaffected; refit to " +
          "get an interval.",
      };
    case "model_type_has_no_interval":
      // FR-180.
      return {
        family: "ebm",
        headline: "This model type offers no interval",
        detail:
          "An explainable boosting machine has neither a covariance matrix nor paired " +
          "quantile bounds, so none of the other reasons would be true of it. The " +
          "expectation below is a full answer for this model type.",
      };
  }
}

/**
 * What kind of claim an interval on this page is making.
 *
 * FR-201 is the whole reason this function exists: a paired-quantile interval covers
 * `Y` itself while `confidence_interval_mean` covers `E[Y|x]`, and "a reader comparing a
 * GBM's bound with a GLM's must be able to see they are not the same kind of claim". The two
 * strings must stay visibly different.
 */
export function intervalClaim(kind: Exclude<UncertaintyKind, "unavailable">): string {
  switch (kind) {
    case "confidence_interval_mean":
      // FR-196: exactly one confidence-side kind, and it is "never silently widened"
      // into a process-variance prediction interval.
      return "the average outcome for rows like this one";
    case "quantile_pair_interval":
      // FR-201.
      return "an individual outcome for a row like this one";
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pnpm --dir frontend test -- predictions.test.ts`

Expected: PASS, 6 tests.

- [ ] **Step 5: Add the type-level assertions**

Create `frontend/src/api/__tests__/predictions.test-d.ts`:

```ts
import { assertType, describe, expectTypeOf, it } from "vitest";

import type { Uncertainty, UncertaintyBasis, UnavailableReason } from "@/api/predictions";
import { intervalClaim } from "@/api/predictions";

describe("the uncertainty contract", () => {
  it("publishes exactly five unavailable reasons", () => {
    // FR-198's three, FR-195's fourth, FR-180's fifth. A sixth arriving in
    // the generated types breaks `unavailableCopy`'s exhaustive switch at compile time; this
    // assertion says the same thing where a reader will see it.
    expectTypeOf<UnavailableReason>().toEqualTypeOf<
      | "no_interval_models_fitted"
      | "interval_models_not_approved"
      | "interval_models_stale"
      | "covariance_not_stored"
      | "model_type_has_no_interval"
    >();
  });

  it("publishes exactly two bases (FR-197)", () => {
    expectTypeOf<UncertaintyBasis>().toEqualTypeOf<
      "information_matrix" | "unpenalised_information_matrix"
    >();
  });

  it("does not encode FR-201's exclusions in the type", () => {
    // FR-201 forbids `basis` on a quantile pair and requires `interval_models` on it.
    // The generated `Uncertainty` is a flat object with every field nullable, so neither
    // rule is expressible here and a runtime check cannot be replaced by a type. This
    // assertion records that deliberately: it is why `PredictionUncertainty.vue` branches on
    // `kind` rather than on field presence.
    assertType<Uncertainty>({
      kind: "quantile_pair_interval",
      basis: "information_matrix",
      level: 0.95,
      reason: null,
      interval_models: null,
    });
  });

  it("refuses `unavailable` where an interval claim is required", () => {
    // @ts-expect-error `unavailable` carries no interval, so it makes no claim.
    intervalClaim("unavailable");
  });
});
```

- [ ] **Step 6: Run the type tests**

Run: `pnpm --dir frontend test -- predictions.test-d.ts`

Expected: PASS. If the first two assertions fail, the contract has changed — **stop and
resolve it against the spec** (`CLAUDE.md` §0), do not edit the assertion to match.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api/predictions.ts frontend/src/api/__tests__/predictions.test.ts frontend/src/api/__tests__/predictions.test-d.ts
git commit -m "feat(w6b-6b): prediction API module with the reason semantics FR-200 fixes"
```

---

## Task 2: The input-column resolver

**Files:**
- Create: `frontend/src/api/predictionInputs.ts`
- Create: `frontend/src/api/__tests__/predictionInputs.test.ts`

**Interfaces:**
- Consumes: `Model`, `Factor` from `@/api/models`; `parseModelRef` from `@/api/comparisons`.
- Produces: `requiredColumns(model, factorsById): RequiredColumns` where
  `RequiredColumns = { columns: string[]; offsetModelRef: { slug: string; version: number } | null; unresolvedFactorIds: string[] }`.

Pure — no `fetch`, no component. The view composes it; this module never calls the API.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/api/__tests__/predictionInputs.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import type { Factor, Model } from "@/api/models";
import { requiredColumns } from "@/api/predictionInputs";

const DATASET = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";

function factor(id: string, slug: string, extra: Partial<Factor> = {}): Factor {
  return {
    id,
    slug,
    dataset_id: DATASET,
    version: 1,
    type: "identity",
    source_columns: [slug],
    operand_factor_ids: [],
    base_level_method: "largest_exposure",
    base_level: null,
    banding_id: null,
    grouping_id: null,
    intent: "rating",
    monotonic_direction: null,
    monotonic_rationale: null,
    prohibited: false,
    prohibited_reason: null,
    ...extra,
  } as Factor;
}

function glm(factorIds: string[], offset: Model["spec"]["offset"]): Model {
  return {
    id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    model_family_slug: "motor-ad-frequency",
    version: 3,
    status: "fitted",
    spec_hash: "v10:sha256:abc",
    dataset_version_id: DATASET,
    spec: {
      model_type: "glm",
      model_family_slug: "motor-ad-frequency",
      dataset_version_id: DATASET,
      response_column: "ad_claim_count",
      family: "poisson",
      link: "log",
      factors: factorIds,
      offset,
      weight: { kind: "none" },
      loss_treatment: { kind: "none" },
      seed: 0,
    },
  } as unknown as Model;
}

function byId(...factors: Factor[]): Map<string, Factor> {
  return new Map(factors.map((f) => [f.id, f]));
}

describe("requiredColumns", () => {
  it("reads columns off the factors, not off the pinned ids", () => {
    // `GlmSpec.factors` is an array of uuid. The ids are not column names, and a form built
    // from them would ask the user for a uuid.
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const result = requiredColumns(glm(["f1"], { kind: "none" }), byId(age));

    expect(result.columns).toEqual(["driver_age_years"]);
    expect(result.unresolvedFactorIds).toEqual([]);
  });

  it("expands an interaction's operands one level", () => {
    // An `interaction` Factor has empty `source_columns` by validated invariant, and its
    // operands are NOT in `spec.factors`. Without this expansion the form omits real
    // columns and every submission fails with MODEL_TERM_UNRESOLVED.
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const area = factor("f2", "area", { source_columns: ["area_code"] });
    const cross = factor("f3", "age_x_area", {
      type: "interaction",
      source_columns: [],
      operand_factor_ids: ["f1", "f2"],
    });

    const result = requiredColumns(glm(["f3"], { kind: "none" }), byId(age, area, cross));

    expect(result.columns).toEqual(["area_code", "driver_age_years"]);
  });

  it("includes an explicit offset column", () => {
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const result = requiredColumns(
      glm(["f1"], { kind: "log_column", column: "exposure_years" }),
      byId(age),
    );

    expect(result.columns).toEqual(["driver_age_years", "exposure_years"]);
  });

  it("reports the offset model ref rather than silently omitting its columns", () => {
    // The backend scores the referenced model on the CALLER's frame, so its factor columns
    // must be present too. Returning the ref is how the view knows to fetch and union.
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const result = requiredColumns(
      glm(["f1"], { kind: "model", offset_model_ref: "model:base-burning-cost@4" }),
      byId(age),
    );

    expect(result.offsetModelRef).toEqual({ slug: "base-burning-cost", version: 4 });
  });

  it("reports a pinned factor it cannot resolve instead of dropping it", () => {
    // A form quietly missing a column is the failure this whole module exists to prevent.
    const result = requiredColumns(glm(["f1", "f9"], { kind: "none" }), byId(factor("f1", "a")));

    expect(result.columns).toEqual(["a"]);
    expect(result.unresolvedFactorIds).toEqual(["f9"]);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- predictionInputs.test.ts`

Expected: FAIL — `Failed to resolve import "@/api/predictionInputs"`.

- [ ] **Step 3: Write the implementation**

Create `frontend/src/api/predictionInputs.ts`:

```ts
import { parseModelRef } from "./comparisons";
import type { Factor, Model } from "./models";

export interface RequiredColumns {
  /** The dataset columns one input row must carry, sorted for a stable form order. */
  readonly columns: string[];
  /**
   * The offset model to resolve and union in, or null. Non-null means this result is
   * **incomplete** on its own: see the note on `offset.kind === "model"` below.
   */
  readonly offsetModelRef: { slug: string; version: number } | null;
  /** Pinned factor ids not present in the supplied map. Surfaced, never dropped. */
  readonly unresolvedFactorIds: string[];
}

/**
 * The columns one prediction row must carry for this model.
 *
 * Pure and one-model-at-a-time. Three things make the obvious version wrong:
 *
 * 1. **`spec.factors` holds ids, not columns.** They are resolved through `factorsById`.
 *
 * 2. **An `interaction` Factor sources no columns of its own** — `model_schema` *validates*
 *    that it names none, because "its columns are its operands'". The operands are published
 *    as `operand_factor_ids` and are **not** in `spec.factors`; the backend's `load_factors`
 *    expands them transitively and records that "one level of expansion is enough". This
 *    does the same one level, so the two agree by construction of the same rule rather than
 *    by coincidence.
 *
 * 3. **`offset.kind === "model"` needs the referenced model's columns too.** The backend
 *    resolves that model per request and computes its linear predictor **on the frame the
 *    caller sent**. Its factors' columns are therefore caller-supplied, and a form built
 *    from the central model alone fails every time with `MODEL_TERM_UNRESOLVED`. This
 *    function cannot fetch, so it returns the ref and the caller unions the second result.
 */
export function requiredColumns(
  model: Model,
  factorsById: ReadonlyMap<string, Factor>,
): RequiredColumns {
  const spec = model.spec;
  const columns = new Set<string>();
  const unresolved: string[] = [];

  const take = (factorId: string, expandOperands: boolean): void => {
    const factor = factorsById.get(factorId);
    if (factor === undefined) {
      unresolved.push(factorId);
      return;
    }
    for (const column of factor.source_columns ?? []) columns.add(column);
    // One level, matching `load_factors`. An operand that is itself an interaction is
    // refused at resolution on the server, which is where that message belongs.
    if (expandOperands) {
      for (const operandId of factor.operand_factor_ids ?? []) take(operandId, false);
    }
  };

  for (const factorId of spec.factors ?? []) take(factorId, true);

  const offset = "offset" in spec ? spec.offset : undefined;
  let offsetModelRef: RequiredColumns["offsetModelRef"] = null;
  if (offset !== undefined && offset !== null) {
    if ((offset.kind === "log_column" || offset.kind === "column") && offset.column) {
      columns.add(offset.column);
    }
    if (offset.kind === "model" && offset.offset_model_ref) {
      // The same ID-3 pattern the contract publishes on `offset_model_ref`. Parsed by the
      // existing helper rather than a second copy of the regex (`CLAUDE.md` §2).
      offsetModelRef = parseModelRef(offset.offset_model_ref);
    }
  }

  return { columns: [...columns].sort(), offsetModelRef, unresolvedFactorIds: unresolved };
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pnpm --dir frontend test -- predictionInputs.test.ts`

Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/predictionInputs.ts frontend/src/api/__tests__/predictionInputs.test.ts
git commit -m "feat(w6b-6b): resolve prediction input columns through operands and the offset model"
```

---

## Task 3: The uncertainty component

**Files:**
- Create: `frontend/src/components/PredictionUncertainty.vue`
- Create: `frontend/src/components/__tests__/PredictionUncertainty.test.ts`

**Interfaces:**
- Consumes: `Uncertainty`, `PredictedRow`, `unavailableCopy`, `intervalClaim` from
  `@/api/predictions`.
- Produces: a component with props `{ uncertainty: Uncertainty; row: PredictedRow }`.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/__tests__/PredictionUncertainty.test.ts`:

```ts
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { PredictedRow, Uncertainty } from "@/api/predictions";
import PredictionUncertainty from "@/components/PredictionUncertainty.vue";

const ROW: PredictedRow = { expected: 0.1342, lower: 0.1201, upper: 0.1489 };

function mount(uncertainty: Uncertainty, row: PredictedRow = ROW) {
  return render(PredictionUncertainty, { props: { uncertainty, row } });
}

describe("a GLM confidence interval", () => {
  const GLM: Uncertainty = {
    kind: "confidence_interval_mean",
    basis: "information_matrix",
    level: 0.95,
    reason: null,
    interval_models: null,
  };

  it("states the level and both bounds", () => {
    mount(GLM);
    expect(screen.getByText(/95%/)).toBeTruthy();
    expect(screen.getByText(/0\.1201/)).toBeTruthy();
    expect(screen.getByText(/0\.1489/)).toBeTruthy();
  });

  it("says the interval is about the average, not an individual (FR-196)", () => {
    mount(GLM);
    expect(screen.getByText(/average outcome/)).toBeTruthy();
  });

  it("states the basis (FR-197)", () => {
    mount(GLM);
    expect(screen.getByTestId("uncertainty-basis").textContent).toContain("information matrix");
  });

  it("warns that an unpenalised basis makes the interval too wide (FR-197)", () => {
    mount({ ...GLM, basis: "unpenalised_information_matrix" });
    const basis = screen.getByTestId("uncertainty-basis").textContent ?? "";
    expect(basis).toContain("wider");
  });
});

describe("a paired-quantile interval", () => {
  // `level` is 0.9, not 0.95, and that is not a typo. `Uncertainty`'s validator pins it to the
  // alpha spread: "a 0.05/0.95 pair covers 0.90, and a response claiming 0.95 from it
  // overstates its own coverage by exactly the amount a reader cannot see." A fixture with
  // level 0.95 here could not be produced by the backend.
  const PAIR: Uncertainty = {
    kind: "quantile_pair_interval",
    basis: null,
    level: 0.9,
    reason: null,
    interval_models: {
      lower_model_id: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
      upper_model_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
      lower_alpha: 0.05,
      upper_alpha: 0.95,
    },
  };

  it("says the interval is about an individual outcome (FR-201)", () => {
    mount(PAIR);
    expect(screen.getByText(/individual outcome/)).toBeTruthy();
  });

  it("renders no basis, because FR-201 forbids one on this kind", () => {
    mount(PAIR);
    expect(screen.queryByTestId("uncertainty-basis")).toBeNull();
  });

  it("ignores a basis the server should not have sent, rather than displaying it", () => {
    // Defence in depth, and deliberately so. `Uncertainty`'s model validator already refuses
    // this server-side, citing FR-201 by name — "a pair of quantile fits has no
    // covariance matrix; stating one would claim inference this interval did not do". But the
    // generated TypeScript type is a flat object with every field nullable and cannot express
    // that, so the component branches on `kind` rather than on field presence. A stray basis
    // rendered here would attach a GLM's claim to a GBM's bound.
    mount({ ...PAIR, basis: "information_matrix" });
    expect(screen.queryByTestId("uncertainty-basis")).toBeNull();
  });

  it("names both bound models and their alphas (FR-199)", () => {
    mount(PAIR);
    const bounds = screen.getByTestId("interval-models").textContent ?? "";
    expect(bounds).toContain("0.05");
    expect(bounds).toContain("0.95");
  });
});

describe("an unavailable interval", () => {
  function unavailable(reason: Uncertainty["reason"]): Uncertainty {
    return { kind: "unavailable", basis: null, level: null, reason, interval_models: null };
  }

  it("still shows the expectation (FR-195)", () => {
    mount(unavailable("covariance_not_stored"), { expected: 0.1342, lower: null, upper: null });
    expect(screen.getByText(/0\.1342/)).toBeTruthy();
  });

  it("gives FR-200(ii)'s reading of `not_approved`", () => {
    mount(unavailable("interval_models_not_approved"));
    expect(screen.getByText(/less advanced/)).toBeTruthy();
  });

  it("gives FR-200(iii)'s reading of `stale`", () => {
    mount(unavailable("interval_models_stale"));
    expect(screen.getByText(/superseded/)).toBeTruthy();
  });

  it("names the EBM refusal rather than a reason false of an EBM (FR-180)", () => {
    mount(unavailable("model_type_has_no_interval"));
    expect(screen.getByText(/offers no interval/)).toBeTruthy();
  });

  it("renders a null reason as a stated gap, never as silence", () => {
    // `reason` is nullable in the contract while FR-194 requires "an explicit
    // `uncertainty: unavailable` with the reason". A null is therefore a server-side
    // requirement breach, and the page says so rather than showing an empty panel.
    mount(unavailable(null));
    expect(screen.getByText(/no reason/i)).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- PredictionUncertainty.test.ts`

Expected: FAIL — `Failed to resolve import "@/components/PredictionUncertainty.vue"`.

- [ ] **Step 3: Write the implementation**

Create `frontend/src/components/PredictionUncertainty.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue";

import {
  intervalClaim,
  unavailableCopy,
  type PredictedRow,
  type Uncertainty,
} from "@/api/predictions";

const props = defineProps<{ uncertainty: Uncertainty; row: PredictedRow }>();

/**
 * FR-201 forbids `basis` on a `quantile_pair_interval` and requires `interval_models`
 * on it; FR-196's kind is the mirror image. The generated `Uncertainty` is a flat object
 * with every field nullable, so neither rule is expressible in the type — the component
 * branches on `kind` and reads only the fields that kind is allowed to carry. A stray `basis`
 * on a quantile pair is therefore ignored rather than rendered, which matters because
 * rendering it would attach a GLM's claim to a GBM's bound.
 */
const showBasis = computed(
  () => props.uncertainty.kind === "confidence_interval_mean" && props.uncertainty.basis !== null,
);

const showIntervalModels = computed(
  () =>
    props.uncertainty.kind === "quantile_pair_interval" &&
    props.uncertainty.interval_models !== null,
);

const claim = computed(() =>
  props.uncertainty.kind === "unavailable" ? null : intervalClaim(props.uncertainty.kind),
);

const refusal = computed(() =>
  props.uncertainty.kind === "unavailable" && props.uncertainty.reason !== null
    ? unavailableCopy(props.uncertainty.reason)
    : null,
);

/**
 * FR-197: `unpenalised_information_matrix` means the matrix was computed as though the
 * fit were unpenalised, so the interval is **wider** than the shrunk estimate warrants. That
 * direction is the whole content of the caveat — an actuary who reads it as "narrower" draws
 * the opposite conclusion about precision.
 */
const basisCopy = computed(() =>
  props.uncertainty.basis === "unpenalised_information_matrix"
    ? "unpenalised information matrix — this fit is penalised, so the interval is wider than the shrunk estimate warrants"
    : "information matrix",
);

const percent = computed(() =>
  props.uncertainty.level === null || props.uncertainty.level === undefined
    ? null
    : `${(props.uncertainty.level * 100).toFixed(0)}%`,
);
</script>

<template>
  <section class="mt-4 rounded-md border border-slate-200 p-4">
    <p class="text-2xl font-semibold" data-testid="expected">{{ row.expected }}</p>
    <p class="text-xs text-slate-500">Expected value</p>

    <template v-if="claim !== null && row.lower !== null && row.upper !== null">
      <p class="mt-3 font-mono text-sm" data-testid="interval">
        {{ row.lower }} &ndash; {{ row.upper }}
      </p>
      <p class="text-xs text-slate-600">
        <template v-if="percent">{{ percent }} interval for </template>
        <template v-else>Interval for </template>{{ claim }}.
      </p>
      <p v-if="showBasis" class="mt-1 text-xs text-slate-500" data-testid="uncertainty-basis">
        Computed on the {{ basisCopy }}.
      </p>
      <!-- FR-199: a bound is a Model in its own right, at a declared alpha. Naming both
           is what lets a reader check the pair is the one they think it is. -->
      <p
        v-if="showIntervalModels && uncertainty.interval_models"
        class="mt-1 text-xs text-slate-500"
        data-testid="interval-models"
      >
        From paired quantile models at alpha {{ uncertainty.interval_models.lower_alpha }} and
        {{ uncertainty.interval_models.upper_alpha }}.
      </p>
    </template>

    <div v-else-if="uncertainty.kind === 'unavailable'" class="mt-3 rounded bg-slate-50 p-3">
      <template v-if="refusal">
        <p class="text-sm font-medium">{{ refusal.headline }}</p>
        <p class="mt-1 text-xs text-slate-600">{{ refusal.detail }}</p>
      </template>
      <!-- FR-194 requires the reason, so a null one is a breach on the server's side.
           Reported as such: an empty panel would read as "the page forgot". -->
      <p v-else class="text-sm text-amber-900">
        No interval, and the response carried no reason for it. FR-194 requires one.
      </p>
    </div>
  </section>
</template>
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pnpm --dir frontend test -- PredictionUncertainty.test.ts`

Expected: PASS, 13 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/PredictionUncertainty.vue frontend/src/components/__tests__/PredictionUncertainty.test.ts
git commit -m "feat(w6b-6b): render an interval as the claim its kind actually makes"
```

---

## Task 4: The view and its route

**Files:**
- Create: `frontend/src/views/PredictionView.vue`
- Create: `frontend/src/views/__tests__/PredictionView.test.ts`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/router/__tests__/index.test.ts`
- Modify: `frontend/src/views/__tests__/fixtures.ts`

**Interfaces:**
- Consumes: `getModel`, `listFactors` from `@/api/models`; `predict` from `@/api/predictions`;
  `requiredColumns` from `@/api/predictionInputs`; `PredictionUncertainty`; `isProblem` from
  `@/api/problem`.
- Produces: the route named `model-predict` at `/models/:slug/predict`.

- [ ] **Step 1: Add the fixtures**

Append to `frontend/src/views/__tests__/fixtures.ts`:

```ts
import type { Prediction } from "@/api/predictions";

/** A minimal fitted GLM. `GBM_MODEL` above is the boosted counterpart. */
export const GLM_MODEL: Model = {
  id: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
  model_family_slug: "motor-ad-frequency",
  version: 3,
  status: "fitted",
  spec_hash: "v10:sha256:def",
  dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  spec: {
    model_type: "glm",
    model_family_slug: "motor-ad-frequency",
    dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    response_column: "ad_claim_count",
    family: "poisson",
    link: "log",
    factors: ["f1"],
    offset: { kind: "log_column", column: "exposure_years" },
    weight: { kind: "none" },
    loss_treatment: { kind: "none" },
    seed: 0,
  },
} as unknown as Model;

export const DRIVER_AGE_FACTOR: Factor = {
  id: "f1",
  slug: "driver_age",
  dataset_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  version: 1,
  type: "identity",
  source_columns: ["driver_age_years"],
  operand_factor_ids: [],
  base_level_method: "largest_exposure",
  base_level: null,
  banding_id: null,
  grouping_id: null,
  intent: "rating",
  monotonic_direction: null,
  monotonic_rationale: null,
  prohibited: false,
  prohibited_reason: null,
} as Factor;

export const PREDICTION: Prediction = {
  model_id: GLM_MODEL.id,
  model_family_slug: GLM_MODEL.model_family_slug,
  version: GLM_MODEL.version,
  model_type: "glm",
  uncertainty: {
    kind: "confidence_interval_mean",
    basis: "information_matrix",
    level: 0.95,
    reason: null,
    interval_models: null,
  },
  rows: [{ expected: 0.1342, lower: 0.1201, upper: 0.1489 }],
};
```

Add `Factor` to the existing `@/api/models` type import at the top of the file if it is not
already there.

- [ ] **Step 2: Write the failing test**

Create `frontend/src/views/__tests__/PredictionView.test.ts`:

```ts
import { render, screen, waitFor } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import PredictionView from "@/views/PredictionView.vue";

import { DRIVER_AGE_FACTOR, GLM_MODEL, PREDICTION } from "./fixtures";

vi.mock("@/components/PredictionUncertainty.vue", () => ({
  default: {
    name: "PredictionUncertainty",
    props: ["uncertainty", "row"],
    template: "<div data-testid='uncertainty'>{{ row.expected }}</div>",
  },
}));

const global = {
  stubs: { RouterLink: { props: ["to"], template: "<a><slot /></a>" } },
};

afterEach(() => {
  vi.unstubAllGlobals();
});

/**
 * Answer by URL. Modelled on `ModelComparisonView.test.ts`'s `stubByUrl` and kept separate
 * for the same reason it was: this page needs a POST that can answer 409 with a real problem
 * document, because every refusal branch here is a code, not a status.
 */
function stubByUrl(routes: Record<string, { status?: number; body: unknown }>): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      const key = Object.keys(routes).find((route) => url.includes(route));
      const match = key === undefined ? undefined : routes[key];
      if (match === undefined) {
        return new Response(
          JSON.stringify({ type: "about:blank", code: "NOT_FOUND", title: "Not found" }),
          { status: 404, headers: { "Content-Type": "application/json" } },
        );
      }
      return new Response(JSON.stringify(match.body), {
        status: match.status ?? 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

function problem(code: string, status: number, detail: string) {
  return { status, body: { type: "about:blank", code, title: code, detail } };
}

const LOADED = {
  "/models/motor-ad-frequency": { body: GLM_MODEL },
  "/factors": { body: [DRIVER_AGE_FACTOR] },
};

describe("the input form", () => {
  it("asks for the model's source columns, not its factor ids", async () => {
    stubByUrl(LOADED);
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    // The offset column is caller-supplied too.
    expect(screen.getByLabelText("exposure_years")).toBeTruthy();
    expect(screen.queryByLabelText("f1")).toBeNull();
  });
});

describe("scoring", () => {
  it("renders the expectation and hands the uncertainty to the panel", async () => {
    stubByUrl({ ...LOADED, "/predict": { body: PREDICTION } });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    await userEvent.type(screen.getByLabelText("driver_age_years"), "42");
    await userEvent.type(screen.getByLabelText("exposure_years"), "1");
    await userEvent.click(screen.getByRole("button", { name: /score/i }));

    await waitFor(() => expect(screen.getByTestId("uncertainty").textContent).toContain("0.1342"));
  });

  it("shows no Job affordance: this route answers 200", async () => {
    stubByUrl({ ...LOADED, "/predict": { body: PREDICTION } });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    expect(screen.queryByText(/queued|progress|job/i)).toBeNull();
  });
});

describe("the refusal taxonomy", () => {
  /**
   * Five codes share 409 and one shares 422 with two other messages, so every case here
   * asserts on the rendered copy rather than on a status. `problem.ts` states the rule on the
   * field: "Branch on this, never on `status`".
   */
  const cases: ReadonlyArray<[string, number, RegExp]> = [
    ["MODEL_NOT_FITTED", 409, /not been fitted/i],
    ["MODEL_INTERVAL_UNAVAILABLE", 409, /cross/i],
    ["MODEL_TYPE_UNSUPPORTED", 409, /spec and fit result disagree/i],
    ["MODEL_TERM_UNRESOLVED", 409, /cannot be scored/i],
    ["VALIDATION_FAILED", 422, /check the values/i],
  ];

  for (const [code, status, expected] of cases) {
    it(`names ${code} rather than showing a status`, async () => {
      stubByUrl({ ...LOADED, "/predict": problem(code, status, "detail from the server") });
      render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

      await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
      await userEvent.click(screen.getByRole("button", { name: /score/i }));

      await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(expected));
      expect(screen.getByRole("alert").textContent).not.toContain(String(status));
    });
  }

  it("does not reorder crossed bounds into a displayable interval (FR-199)", async () => {
    // "detected, reported in the diagnostics, and never silently reordered". A view that
    // swapped them would show a plausible interval built from a refusal.
    stubByUrl({
      ...LOADED,
      "/predict": problem("MODEL_INTERVAL_UNAVAILABLE", 409, "The interval models cross"),
    });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    await userEvent.click(screen.getByRole("button", { name: /score/i }));

    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.queryByTestId("uncertainty")).toBeNull();
  });
});

describe("an offset-from-model spec", () => {
  it("asks for the referenced model's columns too", async () => {
    // The backend scores the referenced model on the caller's own frame, so a form built
    // from the central model alone would 409 on every submission.
    const central = {
      ...GLM_MODEL,
      spec: {
        ...GLM_MODEL.spec,
        offset: { kind: "model", offset_model_ref: "model:base-burning-cost@4" },
      },
    };
    const base = {
      ...GLM_MODEL,
      id: "ffffffff-ffff-4fff-8fff-ffffffffffff",
      model_family_slug: "base-burning-cost",
      spec: { ...GLM_MODEL.spec, factors: ["f2"], offset: { kind: "none" } },
    };
    const areaFactor = {
      ...DRIVER_AGE_FACTOR,
      id: "f2",
      slug: "area",
      source_columns: ["area_code"],
    };

    stubByUrl({
      "/models/base-burning-cost": { body: base },
      "/models/motor-ad-frequency": { body: central },
      "/factors": { body: [DRIVER_AGE_FACTOR, areaFactor] },
    });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    expect(screen.getByLabelText("area_code")).toBeTruthy();
  });
});
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- PredictionView.test.ts`

Expected: FAIL — `Failed to resolve import "@/views/PredictionView.vue"`.

- [ ] **Step 4: Write the view**

Create `frontend/src/views/PredictionView.vue`:

```vue
<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import { getModel, listFactors, type Factor, type Model } from "@/api/models";
import { requiredColumns } from "@/api/predictionInputs";
import { predict, type Prediction, type PredictionInputRow } from "@/api/predictions";
import { ProblemError } from "@/api/problem";
import PredictionUncertainty from "@/components/PredictionUncertainty.vue";

const props = defineProps<{ slug: string; version?: string | undefined }>();

const model = ref<Model | null>(null);
const columns = ref<string[]>([]);
const unresolved = ref<string[]>([]);
const values = ref<Record<string, string>>({});
const prediction = ref<Prediction | null>(null);
const failure = ref<string | null>(null);
const loadFailure = ref<string | null>(null);
const scoring = ref(false);

/**
 * Resolve the columns one row must carry.
 *
 * Two reads, and a third only where the spec needs it. `requiredColumns` is pure and handles
 * one model, so an `offset.kind === "model"` spec is completed here by resolving the
 * referenced model and unioning its columns: the backend computes that model's linear
 * predictor on the frame *this* caller sends, so its factor columns are caller-supplied too.
 */
watchEffect(async () => {
  loadFailure.value = null;
  try {
    const loaded = await getModel(props.slug, props.version ? Number(props.version) : undefined);
    model.value = loaded;
    const factors = await listFactors(loaded.dataset_version_id);
    const byId = new Map<string, Factor>(factors.map((factor) => [factor.id, factor]));

    const primary = requiredColumns(loaded, byId);
    const needed = new Set(primary.columns);
    const missing = [...primary.unresolvedFactorIds];

    if (primary.offsetModelRef !== null) {
      const source = await getModel(primary.offsetModelRef.slug, primary.offsetModelRef.version);
      const secondary = requiredColumns(source, byId);
      for (const column of secondary.columns) needed.add(column);
      missing.push(...secondary.unresolvedFactorIds);
    }

    columns.value = [...needed].sort();
    unresolved.value = missing;
    values.value = Object.fromEntries(columns.value.map((column) => [column, ""]));
  } catch (error) {
    loadFailure.value =
      error instanceof ProblemError ? error.problem.detail ?? error.problem.title : String(error);
  }
});

const row = computed<PredictionInputRow>(() =>
  Object.fromEntries(
    Object.entries(values.value).map(([column, raw]) => {
      if (raw === "") return [column, null];
      const asNumber = Number(raw);
      // A blank is a null, a numeric string is a number, and anything else stays a string:
      // the backend builds a frame from these and a categorical level is a string there too.
      return [column, raw.trim() !== "" && !Number.isNaN(asNumber) ? asNumber : raw];
    }),
  ),
);

/**
 * The refusals this page can receive, by code.
 *
 * Five of these share `409` and three distinct `VALIDATION_FAILED` messages share `422`, so
 * the branch is on `problem.code` — `problem.ts` states the rule on the field itself. The
 * server's `detail` is shown beneath, because it carries the specifics (which term, how many
 * rows) that a fixed sentence cannot.
 */
function refusalCopy(error: ProblemError): string {
  switch (error.code) {
    case "MODEL_NOT_FITTED":
      return "This model has not been fitted, so there is nothing to score with.";
    case "MODEL_INTERVAL_UNAVAILABLE":
      // FR-199: crossing quantiles are detected and reported, never silently reordered.
      // This page therefore shows no interval at all here rather than an ordered one.
      return "The interval models cross on these rows, so no interval is reported for them.";
    case "MODEL_TYPE_UNSUPPORTED":
      return "This model's spec and fit result disagree about its type.";
    case "NOT_FOUND":
      return "No model with that name and version.";
    case "VALIDATION_FAILED":
      return "The request was refused — check the values below.";
    default:
      // `MODEL_TERM_UNRESOLVED` and its siblings arrive here. They are a 409 about the
      // pairing of a well-formed request with a real model: commonly a column the model was
      // fitted on that this row does not carry.
      return "These rows cannot be scored with this model.";
  }
}

async function score(): Promise<void> {
  if (model.value === null) return;
  scoring.value = true;
  failure.value = null;
  prediction.value = null;
  try {
    // 200, synchronously. No Job, no poll.
    prediction.value = await predict(model.value.id, row.value);
  } catch (error) {
    failure.value =
      error instanceof ProblemError
        ? `${refusalCopy(error)}${error.problem.detail ? ` ${error.problem.detail}` : ""}`
        : String(error);
  } finally {
    scoring.value = false;
  }
}

const first = computed(() => prediction.value?.rows[0] ?? null);
</script>

<template>
  <main class="mx-auto max-w-3xl p-6">
    <h1 class="text-xl font-semibold">Prediction</h1>
    <p v-if="model" class="text-sm text-slate-600">
      {{ model.model_family_slug }}@{{ model.version }} &middot; {{ model.spec.model_type }}
    </p>

    <p v-if="loadFailure" role="alert" class="mt-4 rounded bg-amber-50 p-3 text-sm">
      {{ loadFailure }}
    </p>

    <!-- A pinned factor that did not resolve means the form is missing a column, and a
         submission would fail with MODEL_TERM_UNRESOLVED. Said here rather than discovered
         at submit. -->
    <p v-if="unresolved.length" role="alert" class="mt-4 rounded bg-amber-50 p-3 text-sm">
      {{ unresolved.length }} of this model's factors could not be resolved, so the form below
      is incomplete: {{ unresolved.join(", ") }}.
    </p>

    <form class="mt-6 grid gap-4 sm:grid-cols-2" @submit.prevent="score">
      <div v-for="column in columns" :key="column">
        <label :for="`field-${column}`" class="block text-xs font-medium text-slate-700">
          {{ column }}
        </label>
        <input
          :id="`field-${column}`"
          v-model="values[column]"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm"
          autocomplete="off"
        />
      </div>
      <div class="sm:col-span-2">
        <button
          type="submit"
          class="rounded bg-slate-900 px-4 py-2 text-sm text-white disabled:opacity-50"
          :disabled="scoring || model === null"
        >
          {{ scoring ? "Scoring…" : "Score row" }}
        </button>
      </div>
    </form>

    <p v-if="failure" role="alert" class="mt-4 rounded bg-amber-50 p-3 text-sm">{{ failure }}</p>

    <PredictionUncertainty
      v-if="prediction && first"
      :uncertainty="prediction.uncertainty"
      :row="first"
    />

    <!-- `02` §5.1: production scoring is `03`'s batch path, not this route. -->
    <p class="mt-8 text-xs text-slate-500">
      Ad-hoc scoring, capped at development scale. A portfolio re-rate runs through the rating
      engine's batch scoring.
    </p>
  </main>
</template>
```

- [ ] **Step 5: Run the view test**

Run: `pnpm --dir frontend test -- PredictionView.test.ts`

Expected: PASS, 10 tests.

- [ ] **Step 6: Add the route**

In `frontend/src/router/index.ts`, insert this record **immediately after** the
`/models/:slug/diagnostics` record and before `/models/new`:

```ts
  {
    // `02` §5.3. Three segments, so it cannot collide with `/models/:slug` — the ranking
    // question recorded at the `/models/compare` entry does not arise here, and
    // `/models/:slug/diagnostics` above is the precedent for exactly this shape.
    //
    // Function-mode props, not `props: true`: the boolean form maps `route.params` only, and
    // `?version=` is a query.
    path: "/models/:slug/predict",
    name: "model-predict",
    component: () => import("@/views/PredictionView.vue"),
    props: (route) => ({
      slug: String(route.params.slug),
      version: typeof route.query.version === "string" ? route.query.version : undefined,
    }),
  },
```

- [ ] **Step 7: Assert resolution rather than declaration order**

Add to `frontend/src/router/__tests__/index.test.ts`, following the file's existing style:

```ts
it("resolves the prediction view, version carried as a query", () => {
  const resolved = router.resolve("/models/motor-ad-frequency/predict?version=3");
  expect(resolved.name).toBe("model-predict");
  expect(resolved.params.slug).toBe("motor-ad-frequency");
  expect(resolved.query.version).toBe("3");
});

it("does not let /models/:slug capture the predict path", () => {
  expect(router.resolve("/models/motor-ad-frequency/predict").name).toBe("model-predict");
});
```

- [ ] **Step 8: Run the router and full frontend tests**

Run: `pnpm --dir frontend test`

Expected: PASS, whole suite. Then:

Run: `pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend build`

Expected: all clean.

- [ ] **Step 9: Commit**

```bash
git add frontend/src/views/PredictionView.vue frontend/src/views/__tests__/PredictionView.test.ts frontend/src/views/__tests__/fixtures.ts frontend/src/router/index.ts frontend/src/router/__tests__/index.test.ts
git commit -m "feat(w6b-6b): the prediction view, and the columns an offset model makes the caller supply"
```

---

## Task 5: Run the full gate

**Files:** none — this task changes nothing and exists to prove the four before it hold together.

`docs/research/w6b-6b-prediction-material.md` was marked superseded in the commit that landed
this plan, so there is nothing to do about it here. It said the requirement set was **six**; this
plan's is **nine**, and leaving both accounts live is RFC-756's failure mode.

- [ ] **Step 1: Run the docs half of the gate**

Run: `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`

Expected: both clean. `audit-docs.py` parses inside HTML comments and reads a leading `|` as a
table row, so keep any pipes off the start of a line.

- [ ] **Step 2: Run the whole gate, both halves**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

A fresh worktree needs `uv sync` first, or `mypy` reports several hundred phantom errors that
read as real defects.

Nothing to commit here: this task is a gate run, and the four tasks above committed their own
work.

---

## Findings to book at closure

Each carries one of `CLAUDE.md` §13's four verdicts. Silence is not one of them, and the verdict
is the main thread's, not a subagent's.

1. **FR-197 limb B — the coefficient path states no basis, and cannot.**
   **Verdict: not started. Owner: backend, outliving WK-664.** Ruled by `w6b-manager` 2026-08-25;
   `w6b-decision-maker` the same day put it as *"discharged on the prediction path
   (`Uncertainty.basis` IS on the wire) and breached on the coefficient path. Predates W6b-1a —
   book against the contract, not the view."* **`ModelDetailView.vue` is not the owner**: the
   breach is older than the view and structural, because `Coefficient` has no basis field and
   `extra="forbid"` refuses an ad-hoc one.

   FR-197 obliges *"every response carrying them"* to state the basis, and
   `Model.uncertainty_basis` in `packages/model-schema/src/model_schema/modelling.py` says the
   same of the surface: *"any surface that renders them states this beside them rather than
   deriving `alpha > 0` for itself. There is no such surface yet: regularisation has no UI."*
   That premise is now false — the model detail view was built 2026-08-24 (W6b-1a) and renders
   both — but the breach is older than the view, because the field was never published: it is a
   Python `@property`, so Pydantic does not serialise it and it appears nowhere in
   `docs/contracts/openapi/generated.json`. The fix is a contract change raised under
   OQ-587's floor-not-ceiling rule. **Not this slice's work** — W6b-6b renders
   `Uncertainty.basis`, which *is* on the wire.

2. **Whether the model detail view fires FR-197's bootstrap trigger. Ruled: no.**
   **Verdict: not started, and not owed by any built surface.** FR-197 owns valid penalised
   inference to *"the slice that builds the first of"* a surface rendering coefficient intervals
   on a **penalised** fit or an approval citing them. `ModelSpecBuilderView.vue` exposes neither
   an `alpha` input nor CV selection, so no penalised fit is reachable through the UI and the
   trigger has not fired.

   **This carries a correction into finding 1 that strengthens it.** An earlier reading here said
   a frontend re-derivation of `alpha > 0` was *forbidden* by FR-197 (*"derived in one place
   and never stored"*) and `CLAUDE.md` §2. It is also **wrong**, which is the stronger objection
   and the one that survives if the governance one were ever waived. `02` FR-197's
   2026-08-21 amendment: *"Under CV selection, `GlmSpec.alpha` is pinned to `0.0` (the effective
   penalty comes from `cv.alphas` instead) … every `select_by == "cv"` fit is treated as using
   the naive (penalised-fit) information matrix unconditionally."* `GlmSpec`'s own validator
   enforces the pinning — *"select_by='cv' but alpha is non-zero"* is refused — and
   `GlmSpec.uncertainty_basis` reads `self.alpha > 0.0 or self.select_by == "cv"`. So a penalised
   CV fit carries `alpha == 0.0`, and a frontend testing `alpha > 0` would report
   `information_matrix` for it: not a duplicated derivation but a **false statement about how the
   interval was computed**, in the one place FR-197 exists to make true.

3. **`backend/src/app/api/models.py`'s `predict` docstring misdescribes `02` §5.1.**
   **Verdict: delivered but untested — a one-line docstring correction, owner the next slice
   touching that module.** It reads *"`02` §5.1 marks the others with a status code and this one
   with none"*, but the §5.1 row for `POST /api/v1/models/{id}/predict` does carry **200**. Both
   were written in the same commit (`9a1c6ce`, 2026-08-18), so the docstring was inaccurate about
   its own commit's spec text rather than going stale. **Substance is unaffected** — both say
   200 — so this is not a `CLAUDE.md` §0 spec/code disagreement, only a wrong statement about
   where a fact is written. Not WK-664's file.

4. **`02` §5.3's Prediction cell claims a batch input this slice does not build.**
   **Verdict: reassigned — owner the maintainer, as a spec decision. WK-664 closes without building
   it.** A `CLAUDE.md` §14 question-4 finding, confirmed by `w6b-manager` 2026-08-25 and recorded
   in `docs/roadmap.md`'s question-4 block in the same PR as this plan. "batch"/"upload" appear
   **once** in all of `02` — in that cell — so no FR carries the capability, and FR-24 makes
   the cell non-binding. The divergence is in the UI only: `PredictRows.rows` is required with no
   default, so the wire shape is already a batch capped at `MAX_PREDICT_ROWS`, and its own schema
   description sends a portfolio re-rate to `03`. What is absent is a surface that uploads one.
   Closing it is a **spec change first** (§0's table) — either an FR states batch scoring here or
   §5.3 drops the clause — which is the maintainer's call, not a slice pickup. Booked with an
   owner rather than left as an absence, which is the orphaned-owner pattern W32-7 hit.

---

## Explicitly not in scope

- **Batch or file upload.** See finding 4.
- **`MODEL_INTERVAL_PAIR_INVALID`.** Fit-time only; the predict path cannot raise it.
- **Fitting interval models.** FR-199's opt-in paired quantile fit is a spec-builder
  concern, not this view's. This view reports their absence by name.
- **Any control that would produce a variance-model approximation.** FR-198: *"not offered
  at all, at any setting."*
- **Coefficient intervals.** They belong to the model detail view; findings 1 and 2 are about it.
- **A `basis` fix.** Blocked on a contract change (finding 1).

---

## Self-review

**1. Spec coverage.** Each of the nine requirements maps to a task: FR-194 → Tasks 3–4;
FR-MODEL-77, 93, 100, 124 → `unavailableCopy` (Task 1) and its rendering (Task 3); FR-196,
101 → `intervalClaim` and the kind-branch (Tasks 1, 3); FR-197 → the basis caveat (Task 3);
FR-199 → the `MODEL_INTERVAL_UNAVAILABLE` branch and its no-reordering assertion (Task 4).
The §5.1 200-not-202 fact is asserted in Task 4's "no Job affordance" test. FR-193 is
excluded with a reason, and FR-200(iv) is excluded with evidence.

**2. Placeholder scan.** No TBDs, no "add validation", no "similar to Task N". Every code step
carries the code. The one instruction that is not literal code — Task 4 Step 1's "add `Factor` to
the existing type import" — is an edit to a line whose current content depends on the file, which
the implementer can see.

**3. Type consistency.** `requiredColumns` returns `{ columns, offsetModelRef, unresolvedFactorIds }`
in Task 2 and is destructured on exactly those three names in Task 4. `unavailableCopy` returns
`{ family, headline, detail }` in Task 1 and is read on `headline`/`detail` in Task 3 and
`family` in Task 1's test. `predict(modelId, row)` is defined in Task 1 and called with
`(model.value.id, row.value)` in Task 4. `PredictionUncertainty` takes `{ uncertainty, row }` in
Task 3 and is passed exactly those in Task 4 and its stub. `intervalClaim` takes
`Exclude<UncertaintyKind, "unavailable">`, and both call sites guard on `kind !== "unavailable"`
first.

**4. One thing an implementer will hit that the tasks cannot pre-empt.** `listFactors` takes a
**dataset id**, and the view passes `model.dataset_version_id`. A Dataset Version id is not a
Dataset id (`CLAUDE.md` §7: a Dataset Version is the immutable snapshot, the Dataset is the
container). If `GET /factors?dataset_id=` returns empty for every model, that is the cause — the
view needs the Dataset id, which means resolving the version to its dataset. **Raise it rather
than guessing**: it is either a missing field on the `Model` read shape (a contract change under
OQ-587) or an extra read, and which one is a maintainer's call.
