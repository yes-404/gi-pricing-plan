# W6b-4a — Model Spec Builder, Builtin Arm — Implementation Plan

**Slice:** `W6b-4a` — `/models/new`: the form, builtin objective selection for all three model
types, and live spec validation.
**Base:** `cdb9f9d` on `main` — W6b-3 (#200) merged.
**Owner:** `w6b-executor`, arbitrated by `w6b-lead` 2026-08-25.
**Map row:** [`2026-08-24-w6b-slice-map-revised.md`](2026-08-24-w6b-slice-map-revised.md):152
(`W6b-4`), dependency `W6b-1a` (merged, `ccc9d64` #173), blocker `—`. **Split into `W6b-4a`
and `W6b-4b` on 2026-08-25** — §1.

**Highest ids in use: `FR-MODEL-128`, `OQ-MODEL-34`, `OQ-OVR-15`. Next free: `OQ-MODEL-35`,
taken by this PR.**

**`OQ-MODEL-35` is filed with this plan although its finding belongs to `W6b-4b`.** The
derivation that found it is here, filing costs no extra cycle, and it starts the maintainer's
clock a cycle before `W6b-4b` needs the answer — the precedent being W6b-3's delivery-gap note,
which landed in a spec row inside its own slice's PR. The *finding* stays allocated to 4b; only
the question is filed early.

---

## Global Constraints

- **No backend change.** Every route and shape this view needs already exists.
- **No requirement renumbered**; this PR proposes no requirement and one open question,
  `OQ-MODEL-35`, mirrored into `open-questions.md` and `02` §10 in the same commit.
- **`docs/roadmap.md` is not edited.** A slice close is not a §13 workstream close.
- **Nothing hand-writes a shape `model-schema` declares.**
- **Every enum→display map is keyed off the generated union**, never `Record<string, string>`
  (the `StatusBadge` precedent, `6ab3895`).
- **Table assertions use `cellUnder` from the start.**
- **Three pre-existing `Record<string, string>` defects are out of scope and must not be
  touched**: `VersionDetailView.vue`:28 (a third copy of the `failed`-missing defect W6b-3
  fixed) and `GbmFitPanel.vue`:14 (`DIRECTION`, keyed off `MonotonicDirection`). The lead is
  routing both. `GbmFitPanel`'s is confirmed not to be this slice's surface — see §3.
- The gate runs both halves, every exit code read separately (§11).

---

## 1. The split, and why the seam is where it is

`W6b-4` is split at **builtin versus custom objectives**, not at form versus picker.

I proposed the latter and it was wrong, for a reason worth recording because it is a whole
class of mistake. **`GbmSpec.objective` is `GbmFunctionRef`, required, with no default**
(`model-schema/modelling.py`:1321), and its validator raises "a builtin objective or metric
needs a name" when `kind` is `builtin` and `name` is absent. A slice owning the model-type
tabs but not objective selection therefore **cannot construct a valid GBM spec at all** — it
would ship a builder that creates GLM models and silently cannot produce the other two. That
is not a half a reviewer can accept on its own terms, which is the test the split is judged on.

The correct seam was already visible in my own evidence and I read it too widely: the
2026-08-22 map's blocker was "no collection endpoints **for custom objectives**". It blocked
the custom arm specifically, never objective selection as such. The original seam *was*
builtin/custom.

**What each half owns:**

| | |
|---|---|
| **`W6b-4a`** (this plan) | The form; builtin objective selection across all three model types; live validation; both response branches; the eleven problem kinds; the route. Rests on spec plain text throughout. |
| **`W6b-4b`** | The custom arm: the list endpoint, which statuses are offered, applicability filtering, the GLM/GBM asymmetry, the picker/library boundary, and `OQ-MODEL-35`. |

`GbmFunctionRef` is **one shape serving both arms** — `kind: Literal["builtin", "custom"]`,
`name`, `ref`, with a validator refusing `name` and `ref` together. So 4a constructs
`kind: "builtin"` and 4b extends to `kind: "custom"`. An extension, not a second shape.

**Findings allocated to 4b and deliberately absent here**, so nothing is orphaned by the
re-cut: the deposited scope from the silently-cleared blocker, the objective-status question,
applicability-across-pages, and the GLM/GBM asymmetry. The parent id would otherwise have kept
4a — the half that does not build the picker.

---

## 2. Scope, derived from the specification first

**The Contents cell does not bind.** `02` §5.3:2584 names seven things. Under **FR-OVR-21** a
§5.3 Contents cell is prose unless declared exhaustive, with a carve-out for seven named cells;
I read the enumeration, and the Model spec builder is **not** among them.

**The cell's citation is narrower than the phrase it attaches to** — the case FR-OVR-21 warns
of, where "a discharge is checked by reading the cited requirement's predicate, not by
confirming its id exists". The cell cites **FR-MODEL-44** for "live spec validation";
FR-MODEL-44 (`02`:217) is the *applicability* rule. The endpoint's own §5.1 row (`02`:1705)
cites **FR-MODEL-44 and FR-MODEL-81**, and the lead confirmed FR-MODEL-81 is a distinct
predicate — the complexity gate.

| Source | What it binds here |
|---|---|
| **`02` §5.1:1705** | `POST /model-specs/validate` → **200** with `SpecValidation`: "`ok` plus **every problem, never only the first**". A spec that merely cannot be fitted "is not a bad *request*, so it is not a 4xx"; a spec naming a version that does not exist **is a 404**. |
| **`FR-MODEL-26`** (`02`:174) | The builtin set: `count:poisson`, `reg:gamma`, `reg:tweedie` (with `tweedie_variance_power`), `binary:logistic`. |
| **`FR-MODEL-81`** (`02`:253) | "Model complexity is a diagnostic **by default**, and a gate only where a workspace asks for one" (OQ-MODEL-6). |
| **`FR-MODEL-19`** | Family, link, offset and weight per response type — the GLM arm's correctness defaults (`CLAUDE.md` §7). |

**The contract was written for this view and says so.** `SpecValidation`'s docstring: "Reported
as a list rather than raised as the first failure. A spec builder that surfaced one error at a
time would make a ten-factor spec a ten-round conversation, and `02` §5.3 asks for live
validation as the form is edited." `SpecProblemKind`'s: "A **closed set, because the frontend
renders each differently** and an open string would make that a guess about wording." Eleven
members, confirmed against `modelling.py`:2105-2129.

---

## 3. Findings

### F1 — "the objective" is three contract shapes, not one control with three vocabularies

This is the finding that shapes the slice, and neither the Contents cell nor the map hints at
it. Across the three tabs the objective is:

| Tab | Shape |
|---|---|
| **GLM** | `family` — `poisson \| negative_binomial \| gamma \| inverse_gaussian \| tweedie \| binomial \| gaussian` (**7**) — **×** `link` — `log \| logit \| identity \| inverse` (**4**) — plus `family_params`. Governed by FR-MODEL-19. |
| **GBM** | `objective: GbmFunctionRef` — `{kind, name, ref}` with a validator. `reg:tweedie` carries a dependent `tweedie_variance_power`. |
| **EBM** | `objective: "rmse" \| "mae"` — an inline literal, **2** members. |

These are not three vocabularies behind one abstraction; they are three different things the
contract deliberately keeps apart, because a GLM's family/link pair *is* its distributional
assumption while a GBM's objective is a named loss. A builder that unifies them either flattens
the GLM pair into a single "objective" choice — losing the link, which FR-MODEL-19 makes a
numbered correctness default — or forces `GbmFunctionRef`'s shape onto EBM's literal.

**Consequence for the design: three controls, one per tab, with no shared "objective" type.**
The tabs share the form around them, not the objective within them.

### F2 — `complexity_limit` cannot be produced in a default workspace

`backend/src/app/platform/model_specs.py`:55-57 states the decision outright: "`None` is the
default and the decision — OQ-MODEL-6 refused a platform-wide constant, so an unset limit means
**'no gate'**, not 'gate at zero'." Both `modelling.max_factor_count` and
`modelling.min_exposure_per_parameter` resolve to `None` unless a workspace sets them.

So one of the eleven `SpecProblemKind` members is unreachable without workspace configuration.
The hazard is not the gap but what it does to a test suite: a suite built from *producible*
cases covers **ten of eleven** and reads as complete, and the missing one is the kind nobody
sees until a workspace turns the gate on.

This slice is immune by construction and says so rather than relying on it — the view renders a
**payload**, so every kind is constructible in a fixture regardless of what a live backend would
emit. Task 3 tests all eleven for exactly this reason.

### F3 — in a default workspace the complexity numbers are *only* ever a diagnostic

Following from F2. FR-MODEL-81: complexity is "a diagnostic **by default**, and a gate only
where a workspace asks for one". `SpecValidation` carries `factor_count` and
`estimated_parameter_count` as required fields, and `exposure_per_parameter`,
`max_factor_count`, `min_exposure_per_parameter` as optional.

A builder rendering `SpecValidation` **only when `ok` is false** therefore shows the complexity
diagnostic **never** in a default workspace: the limits are unset, no `complexity_limit` problem
is raised, and `ok` stays true for a spec with 300 factors against 40 exposure-years.
FR-MODEL-81's *default* case is precisely the case such a builder discards — and the default
case is every workspace until someone configures one.

**Rendering rule: the complexity block is drawn whenever a validation response has been
received, independent of `ok`**, with thresholds shown only where the workspace set them.

### F4 — `/models/new` is captured by `/models/:slug` unless declared above it

`router/index.ts`:87 declares `path: "/models/:slug"`. A `/models/new` record added after it
matches `:slug` first, and the builder never loads — `ModelDetailView` renders with
`slug: "new"` and fetches a model that does not exist. The failure is a 404 inside a view that
looks like it loaded, not a routing error, so it reads as a backend problem.

Declared above, and **tested by resolving the path** rather than by eyeballing the order: a
route that silently resolves to the wrong component is the kind that passes review.

### F5 — there is no form primitive on this branch, and this slice needs two at most

No `FormField`, no `Select`, no `FieldError` exists. The nearest precedent is
`RuleBuilder.vue`, which is a stage machine (`"idle" | "creating" | "running" | "submitting" |
"done"`) over `ProblemError` and `waitForJob` — a useful shape for the *interaction*, not for
the fields.

Per the lead's condition: **extract only what this slice itself uses twice**, no speculative
component library. On the current design that is a labelled field wrapper (used by every
control) and nothing else; the selects differ enough per tab (F1) that a shared `Select`
abstraction would be three call sites with three different option types. **Decision 2.**

---

## 4. Decisions for arbitration

### Decision 1 — three objective controls, not one abstraction over three vocabularies (F1)

This is the slice's structural decision and it is stated here, rather than left in F1, so a
reviewer can reject it on the merits instead of meeting it in the diff.

**The design: one objective control per tab, with no shared "objective" type.** The tabs share
the form around them; they do not share the thing inside them.

| | Option | |
|---|---|---|
| **(a)** | **Three controls, one per tab** | Each renders the shape `model-schema` declares for that model type. Three components where a reader might expect one. |
| **(b)** | One `ObjectiveControl` with a discriminated internal union | Looks unified. Its prop type is the union of three unrelated shapes, so every branch inside it is `if model_type === …` — the tabs, re-implemented one level down. |
| **(c)** | One control over a normalised "objective" shape invented here | The tidiest-looking, and the one that breaks the rule. |

**Recommendation: (a).** The three shapes are not three vocabularies behind one idea — a GLM's
`family` × `link` pair **is** its distributional assumption, and FR-MODEL-19 makes family, link,
offset and weight numbered correctness defaults per response type; a GBM's objective is a named
loss carried in `GbmFunctionRef`; an EBM's is a two-member literal. Flattening the GLM pair into
a single "objective" choice loses the link, which is a numbered requirement, not a field.

**(c) is the one to reject explicitly**: `model-schema` already declares all three shapes, so a
fourth unifying shape invented in the frontend is exactly what `CLAUDE.md` §2 forbids — "nobody
hand-writes a shape that already exists in `model-schema` … a shape defined twice will diverge,
and in a pricing platform a diverged shape is a mispricing." It is the same violation the
`StatusBadge` extraction was about, arriving from the opposite direction: there, one shape had
been copied into a view; here, three shapes would be collapsed into one the contract does not
have.

**What would change this:** if `W6b-4b`'s custom arm — which extends `GbmFunctionRef` to
`kind: "custom"` — turns out to want a shape shared across tabs, (a) is too strong. It does not
today: the custom arm reaches one of the three controls, not all of them.

### Decision 2 — how live validation is triggered

`02` §5.3 asks for "live spec validation … as the form is edited". Three readings:

| | Option | |
|---|---|---|
| **(a)** | Validate on every keystroke | Truest to "live". One request per character on a factor filter, and `SpecValidation` reads an unindexed JSONB column (FR-MODEL-127's own note). |
| **(b)** | **Debounced on change** | "Live" as a user experiences it. One tunable constant. |
| **(c)** | On an explicit Validate button | Cheapest and least live; makes a ten-factor spec a deliberate act rather than a running commentary, which is close to what `SpecValidation`'s docstring says the endpoint exists to avoid. |

**Recommendation: (b)**, debounced, with the in-flight response superseded rather than raced —
a slower earlier request must not overwrite a faster later one, which is the defect that makes
a debounced validator show stale problems.

### Decision 3 — what, if anything, is extracted as a form primitive (F5)

**Recommendation: one `FormField` wrapper (label, control slot, field-level problems), and
nothing else** — it is used by every control in the form, which is the "twice" test met many
times over. No `Select`: F1 shows the three objective controls take three different option
types, and a shared select would be a generic wrapper around three unrelated unions.

`SpecProblemList` is a component but not a primitive — it renders a contract shape.

### Decision 4 — whether field-level problems are routed to fields

`SpecProblem` carries `subject?: string | null`. Two readings: render every problem in one
list, or route those with a `subject` to the field they name and list the rest.

**Recommendation: one list for this slice**, with `subject` rendered as part of the problem.
Routing by `subject` requires a mapping from subject strings to form fields that nothing in the
contract specifies — `subject` is `"modelling.max_factor_count"` in the complexity case, a
setting key rather than a field — so the mapping would be invented here and wrong the first
time a new problem kind arrived. If the maintainer wants field-routing it should be specified,
not guessed.

---

## 5. Interactions this slice touches but does not resolve

1. **The custom objective arm is `W6b-4b`'s**, with the four contestable judgements that come
   with it.
2. **`GlmSpec.custom_objective_ref` is a governed gap, not a §0 disagreement.** FR-MODEL-87
   records it "absent entirely", owner Phase 1b; it is in the hand-authored contract tier
   (`docs/contracts/schemas/model-spec.schema.json`) and `backend/tests/test_contracts.py`:368
   allowlists the divergence deliberately. **No spec change is owed and none is filed.** The
   lead is tracking that no W6b slice builds it.
3. **`VersionDetailView.vue`:28 is a third copy of the defect W6b-3 fixed** — `Record<string,
   string>`, four of five `DatasetStatus` members, `failed` falling through to draft's
   background at `:78`. `StatusBadge` now exists to replace it. Different view, not this
   surface, and the lead is routing it. **Left alone deliberately.**
4. **`GbmFitPanel.vue`:14 `DIRECTION` is not this slice's surface.** It is keyed off
   `MonotonicDirection` (`increasing | decreasing | none`), which lives on the **Factor** and is
   a fit-result rendering. This builder sets `GbmSpec.monotone_constraints`, a *different*
   generated union (`"derived_from_factors" | "none"`). Checked rather than assumed. Also being
   routed by the lead.

---

## 6. File Structure

```
frontend/src/
  api/
    modelSpecs.ts                            NEW  — validateSpec(), typed from components["schemas"]
  components/
    FormField.vue                            NEW  — the one primitive (Decision 3)
    SpecProblemList.vue                      NEW  — eleven kinds, Record<SpecProblemKind, …>
    __tests__/{FormField,SpecProblemList}     NEW
    __tests__/SpecProblemList.test-d.ts       NEW  — the exhaustiveness proof
  views/
    ModelSpecBuilderView.vue                 NEW  — /models/new
    __tests__/ModelSpecBuilderView.test.ts    NEW
  router/index.ts                            /models/new, declared above /models/:slug
```

---

## 7. Tasks

Each task is one commit; the gate runs at Task 5.

### Task 1 — the route, declared above `/models/:slug` (F4)

The record plus `modelSpecs.ts`'s `validateSpec()`. Tested by **resolving** `/models/new`
through the router and asserting the matched component is the builder — not by asserting
declaration order, which is what makes the test survive a later reordering.

### Task 2 — `SpecProblemList`, all eleven kinds (ruled)

`Record<SpecProblemKind, …>` off the generated union, the `StatusBadge` precedent, which the
contract's own docstring independently asks for. Tests: every kind renders; **the eleven
renderings are mutually distinct** — a map giving two kinds the same rendering passes "every
kind renders something" while leaving the analyst unable to tell them apart; problems render in
the order received; **all of them render, not the first**, which is the specific failure
`SpecValidation`'s docstring names.

All eleven from fixtures, `complexity_limit` included, since no default workspace can produce it
(F2). Mutation: delete a member, show the type error, restore.

### Task 3 — the form and the three objective controls (F1, Decision 1)

Dataset/split pickers, response, offset/weight, factor multi-select (`listFactors` exists),
model-type tabs, hyperparameters, and **three separate objective controls** — GLM family × link
+ `family_params`; GBM `GbmFunctionRef{kind: "builtin", name}` over FR-MODEL-26's four with
`tweedie_variance_power` appearing only for `reg:tweedie`; EBM's `"rmse" | "mae"`. `FormField`
lands here (Decision 3).

Tests include that switching tabs does not carry an objective across shapes — the failure F1
predicts.

### Task 4 — live validation, both branches, and the complexity block

Debounced validation with the in-flight response superseded (Decision 2).

**Both branches tested, as W6b-3's Decision 3 was:**

- **200 with problems** — `ok: false` is a *result*. The view renders the problems and stays a
  form; it must not show the `ProblemError` surface.
- **404 for a version that does not exist** — a different code path, the one the §5.1 row was
  written to separate. A builder routing both through one handler is the defect that row
  prevents.

**And the complexity block renders whenever a response has been received, independent of `ok`**
(F3), thresholds shown only where set. Tested with `ok: true` and a large `factor_count` — the
default-workspace case FR-MODEL-81 is actually about.

### Task 5 — the gate, both halves, and the close

All thirteen commands, each exit code read separately. §13 mutations at minimum: a problem kind
losing its rendering (type error, not test); `problems[0]` rendered instead of all; the
complexity block hidden when `ok` is true; the 404 branch routed through the 200 handler; the
route declared below `/models/:slug`. Then PR, CI read per-workflow, merge verified by
`state`/`mergeCommit`, cleanup, report.

---

## 8. What would make this plan wrong

1. **If "live validation" is meant to be a button.** Decision 2(b) reads §5.3's "as the form is
   edited" as debounced-live; a maintainer could reasonably want (c), and `SpecValidation`'s own
   docstring is quotable both ways.
2. **If `subject` is meant to route problems to fields.** Decision 4 declines to invent the
   mapping. If one is specified, Task 2's single list becomes wrong rather than merely simple.
3. **If the builtin objective set for a *spec* is not FR-MODEL-26's.** The GBM arm's four names
   are taken from that row; if a different catalogue governs what a spec may name, the GBM arm
   is wrong and the GLM and EBM arms still stand, since theirs come from the generated unions.
4. **If W6b-4b's custom arm forces a shared objective abstraction after all.** F1 argues for
   three separate controls. 4b adds `kind: "custom"` to one of them — the GBM one — and if that
   turns out to want a shared shape, F1's conclusion is too strong and Task 3 is the commit to
   revisit.
