---
id: PL-796
family: plan
kind: leaf
title: W6b-4b — The Custom Objective Arm — Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-25
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-25-w6b-4b-custom-objective-arm.md
---

# W6b-4b — The Custom Objective Arm — Implementation Plan

**Slice:** `W6b-4b` — custom objectives in the model spec builder's objective picker.
**Base:** `b77d95a` on `main` — W6b-4a (#203) merged.
**Owner:** `w6b-executor`, arbitrated by `w6b-lead` 2026-08-25.
**Map row:** [`PL-00786-wk-664-the-revised-slice-map.md`](PL-00786-wk-664-the-revised-slice-map.md):152
(`W6b-4`), split into `4a`/`4b` at builtin-versus-custom on 2026-08-25.

**Highest ids in use: `FR-168`, `OQ-607`, `OQ-552`, `OQ-654`.**
This plan proposes no id of its own. **`OQ-607` was authored by the lead** and lands
verbatim in this PR, in both mirrors — §2 wants the open question and the workaround it
justifies in one change. `OQ-655` (the `openapi-typescript` flag behind the casts) is
the lead's and is not touched here.

---

## Prerequisites

**The validator must stop refusing every custom objective before this picker is built.**
`_objective_problems` returned `OBJECTIVE_UNSUPPORTED` for every `kind: "custom"` spec, on
the stated ground that FR-142 "no slice has built". `02` §5.3 puts live validation on
the very view this slice extends, so the picker would have composed specs its own screen
immediately refused.

That refusal was **stale, and the spec had said so in advance**: `02` §5.1:1933 authorised
it conditionally — "a Custom Objective **while FR-142 is unbuilt**" — and FR-142
ships end to end. Retiring it is a §0 resolution, not a capability: it landed as its own
change, mirroring `pricing_core.modelling.gbm`'s checks and stopping there, with the test
that forbade custom objectives rewritten to permit a `certified` one.

Named by content rather than by number, because a plan is frozen at its date and a PR
number is a fact about one repository's sequence, not about what this slice needs.

**The boundary that change does not move.** WK-664 may discharge an expired condition in
behaviour the spec has already fixed. WK-664 may **not** author new capability on a backend or
`model-schema` surface. `OQ-607`(a) and (b) and `OQ-605`(c) therefore keep **no
owner** — they need a maintainer's design decision, not permission for WK-664 to touch Python.

---

## Global Constraints

- **No backend change**, and no `model-schema` change. Both of this slice's structural
  findings want one and neither may have it here. The prerequisite above is a separate
  change for exactly this reason: it keeps this line literally true, and with it the
  interim-guard reasoning of F1 and F2 and OQ-607's no-owner disposition.
- **`docs/roadmap.md` is not edited.**
- **Nothing hand-writes a shape `model-schema` declares** — and this slice exists partly
  because 4a broke that rule in one place (F1).
- **The `as unknown as ModelSpec` cast pattern is kept as documented.** Its root cause is
  `openapi-typescript` v7 defaulting `--default-non-nullable` true, so server-defaulted
  fields render required; the generated OpenAPI is correct. **The tooling is not changed
  here** — that is `OQ-655`, the lead's.
- Table assertions use `cellUnder`; enum→display maps are keyed off generated unions.
- The gate runs both halves, every exit code read separately (§11).

---

## 1. What this slice is

`GbmSpec.objective` is a `GbmFunctionRef`, which is `{kind: "builtin" | "custom", name, ref}`.
4a built the `builtin` arm. This builds `custom`: list the workspace's Custom Objectives,
filter them to the ones that apply, and emit `{kind: "custom", ref: "custom_objective:<slug>@<version>"}`.

**On the GBM tab only.** `GlmSpec` has no `custom_objective_ref` — FR-207 records it
"absent entirely", owner Phase 1b; it exists in the hand-authored contract tier and
`backend/tests/test_contracts.py`:368 allowlists the divergence deliberately. That is a
**governed gap, not a §0 disagreement**, and no spec change is owed. `ObjectiveBackend`'s own
docstring states it: "a custom objective on the GLM arm needs `GlmSpec.custom_objective_ref`,
which FR-207 records as absent entirely and owned by Phase 1b."

**It is not the artifact library.** No `usage_count` column, no certificate rendering, no
submit or certify affordance — those are `W6b-7`'s. `CustomObjective` carries `usage_count`
on the row, so this is a decision not to render a field that is right there.

---

## 2. Two findings carried from 4a, both mine

### F1 — the builtin objective list is a second hand-written copy, and the repo said not to

`ModelSpecBuilderView.vue`'s `BUILTIN_GBM_OBJECTIVES` has **no contract source**. The
authoritative set is `SUPPORTED_GBM_OBJECTIVES` in
`packages/pricing-core/src/pricing_core/modelling/gbm.py`:115 — "FR-120's set, for
callers that need to *check* rather than translate". The comment twelve lines above it is
the warning against exactly what 4a did:

> "Two hand-written lists would eventually disagree about which objectives the platform
> supports, and the disagreement would show up as a spec that validated and then failed."

**This is the second time in this slice** that a finding was filed without grepping the file
it was about: F4's router claim was a regression against W6b-2's measurement recorded twelve
lines above the line F4 cited. Recorded as a pattern, not as a one-off.

**Why it cannot simply be typed.** `GbmFunctionRef` serves two vocabularies through one
field. `GbmSpec.objective` (`modelling.py`:1321) takes a closed set of four; `eval_metrics`
(:1345) takes the same shape with a deliberately **open** vocabulary — `_METRICS`: "Anything
else is passed to the backend **verbatim** — the metric vocabulary is the backend's own, and
refusing an unrecognised one here would refuse metrics XGBoost supports." `name`'s own
comment: "Not an enum — the eval-metric vocabulary is the backend's and differs between them."

So narrowing `name` would break eval metrics, and the closed set lives in `pricing-core`,
which `model-schema` does not depend on (`["pydantic>=2.9"]` only) and the contract does not
reach: `docs/contracts/openapi/generated.json` contains **zero** occurrences of
`count:poisson`, and the hand-authored `model-spec.schema.json` carries the four names inside
a description string that ends "…" and says "Not an enum".

**Decision 1** covers what this slice does about it.

### F2 — three more copies of generated unions

`FAMILIES`, `LINKS` and `RESPONSES` in the same file are verbatim duplicates of generated
unions, derivable as `GlmSpec["family"]`, `GlmSpec["link"]` and
`NonNullable<ModelSpec["response"]>`. Lower stakes than F1 — a stale copy here renders a
missing option rather than a wrong claim about what the platform supports — but the same
class. Fixed in passing.

**Two corrections to how, both from arbitration.**

`satisfies readonly GlmSpec["family"][]` catches a **wrong** member, not a **missing** one:
a subset satisfies the constraint, so a member the contract *adds* narrows the picker
silently — which is the direction F2 said it wanted to catch. The pin is therefore
`expectTypeOf<GlmSpec["family"]>().toEqualTypeOf<typeof FAMILIES[number]>()`, the
`SpecProblemList.test-d.ts` precedent, with `satisfies` kept for the other direction.

And the scope widens to **`ModelSpecBuilderView.vue`:69-71**, where `family` and `link` are
written a **third** time as `ref<"poisson" | …>` annotations. Deriving the arrays while
leaving those would fix the copy that *lists* the vocabulary and leave the copy that *types
the state* — which is the one a wrong value flows out of.

The lists move to `@/api/modelSpecs` so the type test can import them: a list the test
cannot see is a list the pin does not cover.

---

## 3. Decisions for arbitration

### Decision 1 — how the builtin list stops being a second source of truth (F1) — **RULED**

| | Option | |
|---|---|---|
| **(a)** | A closed type for the **objective position only**, leaving `GbmFunctionRef.name` open for eval metrics | The right fix. A `model-schema` change, so **no owner** — WK-692 is closed. The lead is authoring the open-question row; it lands in this PR. |
| **(b)** | An endpoint publishing the set | **New build**, not exposure: the contract carries the set nowhere machine-readable. |
| **(c)** | Keep the frontend list and pin it with a cross-language test | The only one this slice can build. |

**RULED: (c), repaired.** My first scoping of (c) was unsound and the repair is the
substance of it:

- **The guard goes frontend-side** — a vitest test reads `gbm.py` as text and pins the four
  `_OBJECTIVES` keys against the TypeScript array. No script or test in this repo reads
  across languages today (`generate-contracts.py`'s only `frontend` hit is a comment), so
  the side it lives on is a real choice, not a detail.
- **Because the path filters make it blind either way.** `python.yml` has no `frontend/**`;
  `frontend.yml` has no `packages/**`. A Python test pinning the `.vue` array **never runs
  when someone edits the array** — which is the edit that would break it.
- **So `frontend.yml` gains `packages/pricing-core/src/pricing_core/modelling/**`.** The
  argument is already accepted here: `frontend.yml` lists `docs/contracts/openapi/**` with
  the comment "a contract change can break the frontend without touching a file under
  frontend/". A `pricing-core` change can now break a frontend test the same way.

**`python.yml` records two prior incidents of this exact failure mode**, which is why the
addition is not speculative: `scripts/**` was added because "a new script that does not match
the filter is linted by nothing", noticed when scope-audit.py "triggered only the docs
workflow"; `examples/**` was added because a change touching only that directory "was checked
by nothing", noticed when WK-663's closure edited the seed. This is the third instance and the
first on the frontend side.

**One judgment inside the ruling, flagged rather than taken silently.** `frontend.yml`'s
`docs/contracts/openapi/**` entry is on the **`pull_request` trigger only**; its `push` paths
are `frontend/**` and the workflow file. `python.yml` by contrast puts `docs/contracts/**` on
**both**. I am adding the new path to **both** triggers, matching `python.yml`, because the
cost is nil and PR-only coverage depends on the never-push-to-main policy holding. The
pre-existing asymmetry on the openapi entry is **not** changed here — noticed, not fixed.

### Decision 2 — which objective statuses the picker offers — **DECIDED: all three**

**The set already exists and I should not have been recommending one.**
`FITTABLE_OBJECTIVE_STATUSES` (`model_schema/objectives.py`:174) is
`{certified, review, approved}`, exported, and enforced at `gbm.py`:532. Its own comment
answers the R4 reasoning I had been building on, verbatim: *"Not the same set as the one R4
requires for the model to reach `approved` — that is `approved` alone."*

This plan first recommended `approved` + `certified`, which **omits `review`** and would
have made the picker **stricter than the fit** — an actuary unable to select an objective
the platform would accept, with nothing on screen to say why. All three are reachable
through the product's own routes (`certify`, `submit`, the approval mapping at
`platform/objectives.py`:873), so hiding `review` hides objectives the platform creates.

**The picker derives its set from `FITTABLE_OBJECTIVE_STATUSES` and does not spell it out.**
Spelling it would have been the **fourth** hand-written list in this file after F1's and
F2's three. My standing check from F1 did not fire because it grepped `pricing_core` only;
it now greps `model_schema` too.

`ObjectiveStatus` *is* a generated schema, so the **type** derives cleanly. The **subset**
does not: it reaches no contract, which is OQ-607's defect one surface over — hence the
widening in §2. The divergence test extends to read both files.

`draft` and `deprecated` are outside the set: `draft` has no certificate, so FR-146 is
unsatisfied and its derivatives are unproven; `deprecated` has been withdrawn.

**Labelling is a live question, not a settled one.** `model_schema/objectives.py`:160-161
pins the transitions — `REVIEW → {APPROVED, CERTIFIED}`, and neither `DRAFT` nor `CERTIFIED`
may jump straight to `APPROVED` (pinned at `test_objectives.py`:226-227). So "in review" is
not simply a step before "approved"; a label implying a linear ladder would misdescribe the
lifecycle. Read the transitions before writing any label.

### Decision 3 — applicability filtering across pages (OQ-605(a))

The picker must filter by applicability: FR-153 makes an objective applicable to
particular responses and backends, and a spec pairing them wrongly is refused at validation,
so offering an inapplicable objective manufactures the error the requirement prevents.
`CustomObjective` carries `applicability` on the row; the query carries `status`, `slug`,
`cursor`, `limit` only.

**OQ-605 ruled (a) with a stated bound, and the bound is the requirement**: an
implementation that quietly stops paging reproduces the defect the question exists to fix — a
picker that cannot distinguish "none applicable" from "none seen".

**DECIDED: fetch at most 5 pages at `limit=200`** (1000 objectives; `MAX_LIMIT` verified 200),
and **when `next_cursor` is still non-null at the cap, the picker says so** rather than
presenting a filtered list as complete. Both branches tested, including the disclosure — a
truncation nobody can see is the thing being guarded against.

**The cap is a named constant citing OQ-605**, not a bare `5` in a loop. A magic number
here would send the next reader looking for a rationale that lives in an open question they
have no reason to know exists; the name is what carries them to it.

---

## 4. Interactions this slice touches but does not resolve

1. **FR-111 limbs A and B stay `not started` with no owner**, as landed in 4a.
2. **OQ-606** (validate 422s where §5.1 says it cannot) is not resolved here.
3. **`OQ-655`** — the `openapi-typescript` flag causing the casts — is the lead's; the
   documented cast pattern is used unchanged.
4. **`usage_count` is on the row and deliberately not rendered** (W6b-7's boundary).
5. **The GLM tab gains nothing.** No "custom objectives coming soon" affordance: FR-207
   stages the field, and a UI hint would assert a schedule the requirement does not carry.

---

## 5. File Structure

```
frontend/src/
  api/
    objectives.ts                              NEW  — listObjectives(), bounded paging
    __tests__/objectives.test.ts               NEW
  components/
    ObjectivePicker.vue                        NEW  — builtin + custom, applicability-filtered
    __tests__/ObjectivePicker.test.ts          NEW
    __tests__/objectiveVocabulary.test-d.ts    NEW  — F2's pins
    __tests__/builtinObjectives.test.ts        NEW  — F1's cross-language guard
  views/
    ModelSpecBuilderView.vue                   the picker replaces the builtin select
.github/workflows/frontend.yml                 + packages/pricing-core/.../modelling/**
docs/
  open-questions.md                            the lead's row (+ 02 §10 mirror)
```

---

## 6. Tasks

### Task 1 — F1's guard, and the path filter that makes it run

The vitest test reading `gbm.py`, plus `frontend.yml`'s new path on both triggers. **Proven
by mutation in both directions**: change the TypeScript array → red; change the pinned Python
keys → red. A guard that only fires one way is half a guard.

### Task 2 — F2's derived unions and their pins

`FAMILIES`/`LINKS`/`RESPONSES` derived from the generated types, pinned in a `.test-d.ts`.

### Task 3 — `listObjectives()` with the bounded paging (Decision 3)

Including the cap and the "there may be more" signal, both tested.

### Task 4 — `ObjectivePicker` (Decisions 2 and 3)

Builtin and custom in one control, custom filtered by status and by applicability against the
chosen response and backend, `certified` marked, emitting a correct `GbmFunctionRef` — which
the validator constrains: exactly one of `name`/`ref`, and `ref` is
`custom_objective:<slug>@<version>`.

### Task 5 — `OQ-607`, both mirrors (landed with this plan)

Landed as authored, in `open-questions.md` and `02` §10.

### Task 6 — the gate, both halves, and the close

All thirteen commands, each exit code read separately; §13 mutations; PR; CI read
per-workflow — **and this PR is the first that should trigger the frontend workflow from a
`packages/` change, which is itself worth confirming rather than assuming**; merge verified by
`state`/`mergeCommit`; cleanup; report.

---

## 7. What would make this plan wrong

1. **If the maintainer reads the Contents cell's "approved" as binding**, Decision 2
   over-offers. FR-24 makes it prose, which is why this is a recommendation.
2. **If 5 pages is the wrong cap.** It is chosen for a modal at Phase 1b scale; the
   disclosure is what makes a wrong cap visible rather than silent, which is the property
   OQ-605 actually required.
3. **If reading `gbm.py` from a vitest test is judged too clever.** It is a text read of a
   file in the same repo, and the alternative — no guard — is the state F1 describes. But it
   is the first cross-language test here, and that is a precedent worth objecting to now
   rather than after it is copied.
4. **If adding the path to `frontend.yml`'s `push` trigger is unwanted.** The precedent I am
   citing put its cross-cutting path on `pull_request` only; I am deviating deliberately and
   saying so.
