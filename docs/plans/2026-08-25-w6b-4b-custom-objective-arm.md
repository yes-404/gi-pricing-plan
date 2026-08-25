# W6b-4b — The Custom Objective Arm — Implementation Plan

**Slice:** `W6b-4b` — custom objectives in the model spec builder's objective picker.
**Base:** `b77d95a` on `main` — W6b-4a (#203) merged.
**Owner:** `w6b-executor`, arbitrated by `w6b-lead` 2026-08-25.
**Map row:** [`2026-08-24-w6b-slice-map-revised.md`](2026-08-24-w6b-slice-map-revised.md):152
(`W6b-4`), split into `4a`/`4b` at builtin-versus-custom on 2026-08-25.

**Highest ids in use: `FR-MODEL-128`, `OQ-MODEL-37`, `OQ-OVR-15`, `OQ-PLAT-15`.**
This plan proposes no id of its own. **`OQ-MODEL-37` was authored by the lead** and lands
verbatim in this PR, in both mirrors — §2 wants the open question and the workaround it
justifies in one change. `OQ-PLAT-16` (the `openapi-typescript` flag behind the casts) is
the lead's and is not touched here.

---

## Global Constraints

- **No backend change**, and no `model-schema` change. Both of this slice's structural
  findings want one and neither may have it here.
- **`docs/roadmap.md` is not edited.**
- **Nothing hand-writes a shape `model-schema` declares** — and this slice exists partly
  because 4a broke that rule in one place (F1).
- **The `as unknown as ModelSpec` cast pattern is kept as documented.** Its root cause is
  `openapi-typescript` v7 defaulting `--default-non-nullable` true, so server-defaulted
  fields render required; the generated OpenAPI is correct. **The tooling is not changed
  here** — that is `OQ-PLAT-16`, the lead's.
- Table assertions use `cellUnder`; enum→display maps are keyed off generated unions.
- The gate runs both halves, every exit code read separately (§11).

---

## 1. What this slice is

`GbmSpec.objective` is a `GbmFunctionRef`, which is `{kind: "builtin" | "custom", name, ref}`.
4a built the `builtin` arm. This builds `custom`: list the workspace's Custom Objectives,
filter them to the ones that apply, and emit `{kind: "custom", ref: "custom_objective:<slug>@<version>"}`.

**On the GBM tab only.** `GlmSpec` has no `custom_objective_ref` — FR-MODEL-87 records it
"absent entirely", owner Phase 1b; it exists in the hand-authored contract tier and
`backend/tests/test_contracts.py`:368 allowlists the divergence deliberately. That is a
**governed gap, not a §0 disagreement**, and no spec change is owed. `ObjectiveBackend`'s own
docstring states it: "a custom objective on the GLM arm needs `GlmSpec.custom_objective_ref`,
which FR-MODEL-87 records as absent entirely and owned by Phase 1b."

**It is not the artifact library.** No `usage_count` column, no certificate rendering, no
submit or certify affordance — those are `W6b-7`'s. `CustomObjective` carries `usage_count`
on the row, so this is a decision not to render a field that is right there.

---

## 2. Two findings carried from 4a, both mine

### F1 — the builtin objective list is a second hand-written copy, and the repo said not to

`ModelSpecBuilderView.vue`'s `BUILTIN_GBM_OBJECTIVES` has **no contract source**. The
authoritative set is `SUPPORTED_GBM_OBJECTIVES` in
`packages/pricing-core/src/pricing_core/modelling/gbm.py`:115 — "FR-MODEL-26's set, for
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
class. Fixed in passing, and pinned with a `.test-d.ts` the way `SpecProblemKind` is, so a
member added to the contract fails at type-check rather than silently narrowing a picker.

---

## 3. Decisions for arbitration

### Decision 1 — how the builtin list stops being a second source of truth (F1) — **RULED**

| | Option | |
|---|---|---|
| **(a)** | A closed type for the **objective position only**, leaving `GbmFunctionRef.name` open for eval metrics | The right fix. A `model-schema` change, so **no owner** — W32 is closed. The lead is authoring the open-question row; it lands in this PR. |
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
by nothing", noticed when W6a's closure edited the seed. This is the third instance and the
first on the frontend side.

**One judgment inside the ruling, flagged rather than taken silently.** `frontend.yml`'s
`docs/contracts/openapi/**` entry is on the **`pull_request` trigger only**; its `push` paths
are `frontend/**` and the workflow file. `python.yml` by contrast puts `docs/contracts/**` on
**both**. I am adding the new path to **both** triggers, matching `python.yml`, because the
cost is nil and PR-only coverage depends on the never-push-to-main policy holding. The
pre-existing asymmetry on the openapi entry is **not** changed here — noticed, not fixed.

### Decision 2 — which objective statuses the picker offers

Carried from 4a's plan, unresolved. `02` §5.3's Contents cell says "builtin or **approved**
custom"; the cell is prose under FR-OVR-21. The binding rule is **R4** (`02`:49): "A Model
using a Custom Objective can only reach `approved` if that objective is itself `approved`" —
a constraint on the **Model reaching approved**, not on what a draft spec may reference.

`ObjectiveStatus` is `draft | certified | review | approved | deprecated` (FR-MODEL-46).

**Recommendation: `approved` and `certified`, with `certified` marked**, as in the 4a plan.
Under R4 a spec referencing a `certified` objective is authorable and fittable; it simply
cannot carry the resulting Model to `approved` until the objective gets there. `certified` is
the state an objective sits in while its approval is in flight, and excluding it makes the
picker useless during exactly the window when a new objective is interesting. The mark is the
disclosure — the difference between "this will fit" and "this will fit and then stop at
approval", which the analyst should learn at build time rather than at submission.

`draft` and `deprecated` are excluded under every option: `draft` has not passed FR-MODEL-42's
certificate checks, `deprecated` is withdrawn from use.

### Decision 3 — applicability filtering across pages (OQ-MODEL-35(a))

The picker must filter by applicability: FR-MODEL-44 makes an objective applicable to
particular responses and backends, and a spec pairing them wrongly is refused at validation,
so offering an inapplicable objective manufactures the error the requirement prevents.
`CustomObjective` carries `applicability` on the row; the query carries `status`, `slug`,
`cursor`, `limit` only.

**OQ-MODEL-35 ruled (a) with a stated bound, and the bound is the requirement**: an
implementation that quietly stops paging reproduces the defect the question exists to fix — a
picker that cannot distinguish "none applicable" from "none seen".

**Design: fetch at most 5 pages at `limit=200`** (1000 objectives; `MAX_LIMIT` is 200), and
**when `next_cursor` is still non-null at the cap, the picker says so** rather than presenting
a filtered list as complete. Both branches tested, including the disclosure — a truncation
nobody can see is the thing being guarded against.

---

## 4. Interactions this slice touches but does not resolve

1. **FR-MODEL-19 limbs A and B stay `not started` with no owner**, as landed in 4a.
2. **OQ-MODEL-36** (validate 422s where §5.1 says it cannot) is not resolved here.
3. **`OQ-PLAT-16`** — the `openapi-typescript` flag causing the casts — is the lead's; the
   documented cast pattern is used unchanged.
4. **`usage_count` is on the row and deliberately not rendered** (W6b-7's boundary).
5. **The GLM tab gains nothing.** No "custom objectives coming soon" affordance: FR-MODEL-87
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

### Task 5 — `OQ-MODEL-37`, both mirrors (landed with this plan)

Landed as authored, in `open-questions.md` and `02` §10.

### Task 6 — the gate, both halves, and the close

All thirteen commands, each exit code read separately; §13 mutations; PR; CI read
per-workflow — **and this PR is the first that should trigger the frontend workflow from a
`packages/` change, which is itself worth confirming rather than assuming**; merge verified by
`state`/`mergeCommit`; cleanup; report.

---

## 7. What would make this plan wrong

1. **If the maintainer reads the Contents cell's "approved" as binding**, Decision 2
   over-offers. FR-OVR-21 makes it prose, which is why this is a recommendation.
2. **If 5 pages is the wrong cap.** It is chosen for a modal at Phase 1b scale; the
   disclosure is what makes a wrong cap visible rather than silent, which is the property
   OQ-MODEL-35 actually required.
3. **If reading `gbm.py` from a vitest test is judged too clever.** It is a text read of a
   file in the same repo, and the alternative — no guard — is the state F1 describes. But it
   is the first cross-language test here, and that is a precedent worth objecting to now
   rather than after it is copied.
4. **If adding the path to `frontend.yml`'s `push` trigger is unwanted.** The precedent I am
   citing put its cross-cutting path on `pull_request` only; I am deviating deliberately and
   saying so.
