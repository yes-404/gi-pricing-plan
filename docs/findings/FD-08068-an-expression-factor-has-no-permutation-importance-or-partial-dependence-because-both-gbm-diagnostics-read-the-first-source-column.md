---
id: FD-8068
family: finding
title: An expression Factor has no permutation importance or partial dependence, because both GBM diagnostics read the first source column and S4 omits the factor under a named reason
status: active
created: 2026-10-16
owner: auditor
tree: a2f77b2dcad5aaec41a5f10aa664383caf421e8b
corrected_by: []
relates: [WK-690]
---

# FD-8068 — `diagnostics.py` cannot measure an `expression` Factor; FR-174's per-factor diagnostics are undelivered for it

*(Filed under working id 8068 (written "FD 8068" in prose), supplied by the lead; a minter folds
it into the docs batch. Authority: the maintainer's entry "2026-10-16 10:27:41 BST" in
`channel/to-lead.md` (DP-1274-DIAG, ruled (a)) and the lead's decision point "2026-10-16 10:27:00
BST" in `channel/from-lead-2026-10-09.md`, as concurred by the maintainer's entry "2026-10-16
10:33:35 BST" (the form is a named reason, surfaced and not dropped, on both omission-reason
enums). Reads were made at `origin/main`
`a2f77b2dcad5aaec41a5f10aa664383caf421e8b` and at `origin/sl-1274-wk690-s4-factor-expression`
(head `afcd84fb`), on 2026-10-16 between 10:28 and 10:35 BST. Nothing here was run: every
statement about behaviour is read from code, and the S4 red tests are the measurement owed.)*

## Finding

**Proposed severity: MEDIUM (the maintainer rules it); owner WK-690; verdict `deferred with an
owner` (CLAUDE.md §13).**

Both per-factor GBM diagnostics take the **first** of a Factor's source columns as the factor's
column. For every factor type that has one source column that is correct. An `expression` Factor
(FR-83 / FR-95) is computed from **one or more** columns by a formula, so its first source column
is not the factor. S4 (WK-690 Slice 4, SL-1274) lets an `expression` Factor resolve, and so fit.
From that point, unless something stops it, a fitted model can carry a factor for which:

- **permutation importance** shuffles only the first source column, and the degradation it
  reports is that of one operand of the formula, not of the factor; and
- **partial dependence** sweeps the raw first column and labels the curve with the factor's
  slug, so the chart's axis is not the axis the model was fitted on (the defect FR-175 records for
  banded factors, 2026-08-23).

Both outputs are numbers and neither refuses. That is a silently wrong transparency output, which
the maintainer ruled a mispricing-class defect that must not ship. The ruling (DP-1274-DIAG (a)):
**S4 makes each diagnostic that reads `source_columns[0]` omit an `expression` Factor, surfaces the
omission in the diagnostics output under a named reason code and never drops it silently, and
carries a red-first test per diagnostic.** The code S4 uses is
**`EXPRESSION_FACTOR = "expression_factor"`**, declared on both
`PermutationOmissionReason` (`packages/model-schema/src/model_schema/diagnostics.py:380`) and
`PartialDependenceOmissionReason` (`:434`), read at `origin/sl-1274-wk690-s4-factor-expression`
commit `86e42d79` (an ancestor of that branch's head `49cec47e` read on 2026-10-16 10:4x BST; both
members carry the comment "Real support is owed (WK-690)" and "Added 2026-10-16, after which an
older build cannot read the value"). The maintainer's 10:33:35 entry concurs with that form and
orders the frontend to render `EXPRESSION_FACTOR` as readable text, with its own branch in any
`switch` over the reasons. This finding is the other half of that ruling: the
omission is a **gap in what the spec requires**, and the gap needs an owner and a remedy.

## Evidence

### 1. The two sites, at `origin/main` `a2f77b2d` and unchanged at S4's head

The S4 branch does not touch `diagnostics.py`: `git diff --stat a2f77b2d...origin/sl-1274-wk690-s4-factor-expression`
lists 19 files and `packages/pricing-core/src/pricing_core/modelling/diagnostics.py` is not one.
The line numbers below are the same on both trees.

| Site | Lines (`packages/pricing-core/src/pricing_core/modelling/diagnostics.py`) | What it does |
|---|---|---|
| Permutation importance | `:957` `columns = tuple(factor.source_columns[:1])`, in the `else` of `if factor.type is FactorType.INTERACTION` (`:954-957`) | The shuffled column set is the first source column only. The cross arm above it uses `_operand_columns` (FR-177). |
| Partial dependence | `:1213` `columns = (factor.source_columns[0],)`, in the `else` of `if is_cross:` (`:1203`) | The held column is the first source column; `source = data[columns[0]]` (`:1214`). |
| Axis | `_TRANSFORMED_FACTOR_TYPES = (FactorType.BANDING, FactorType.GROUPING)` (`:1056`), `_resolved_axis` (`:1059-1075`) | `return None` for any type not in the tuple. `EXPRESSION` is absent, so an expression Factor, banded or not, takes the "the factor is its source column" path. |

(The lead's relay gave `:1056-1075` for the tuple; the tuple is the single line `:1056` and
`:1059-1075` is the function. The lead's `:957` is the slice form `[:1]`, not `[0]`; it does not
raise on a factor with no column and returns an empty tuple, which the next line records as
`NO_HOLDOUT_COLUMN`.)

`FactorType.EXPRESSION` exists on `main` (`packages/model-schema/src/model_schema/modelling.py:99`)
and is refused at resolution there (FR-208). S4 removes that refusal for it
(`packages/pricing-core/src/pricing_core/modelling/factors.py`, `+121` lines), which is the moment
the two sites become reachable with an expression Factor.

### 2. Why the output is wrong, and what is reasoned rather than measured

- `predict_gbm` re-runs `resolve_factors` on whatever frame it is handed (the comment at
  `diagnostics.py` in `_representatives`). For an expression Factor it therefore re-evaluates the
  formula over the frame. Shuffling one operand moves the formula's result only through that
  operand, and holding one operand at a value holds the formula's other operands at their row
  values. Neither is the factor's permutation or the factor held at a level.
- This is **reasoned from the code and not measured**. No expression Factor can fit on `main`, and
  S4 has not run. The red-first tests the maintainer ordered are the measurement; this finding
  does not claim a number.
- **Two further `source_columns` readers, added 2026-10-16 (BST) before merge on the lead's
  brief, each read at `origin/main` `a2f77b2d` (`git show a2f77b2d:<path> | grep -n
  'source_columns\[0\]'` prints `:86` and `:877` respectively):**
  - `backend/src/app/platform/model_specs.py:86`, in `_estimated_parameters` (`:70-90`):
    `source = factor.source_columns[0] if factor.source_columns else factor.slug`, then
    `counts.get(source)` for the distinct count that sizes the parameter estimate. For an
    `expression` Factor over several columns this counts the first operand's levels, not the
    expression's. The docstring (`:78-82`) already calls the number "an **estimate**, and named one"
    that errs conservatively for banding; for an expression Factor the error has **no known
    direction** (the first operand may have more or fewer levels than the formula's result), so
    "conservative" is not established. The estimate gates a refusal (`complexity_or_refuse`, `:92`).
    **Reasoned from code, not run.**
  - `packages/pricing-core/src/pricing_core/rating/runtime.py:877`: `columns = {f.slug:
    f.source_columns[0] for f in factors if len(f.source_columns) == 1}`. A one-column expression
    Factor is mapped to its raw column; `_GlmScorer.predict` (`:817-818`) then renames each
    `feature_row` key through that map (`self.columns.get(k, k)`). Whether that is right depends on
    whether a scoring caller supplies the factor's slug or the raw column for an expression
    Factor, which this audit did **not** establish. The `len == 1` guard prevents the multi-column
    first-column error and leaves the one-column case unexamined.
  - **Proposed scope (the maintainer rules each):** `model_specs.py:86` **in** this finding's
    scope as a third limb owned by WK-690: it is the same defect, the first source column read as
    the factor, it is reachable the moment S4 lets an expression Factor resolve, and an
    undercount can let a spec through a gate meant to refuse it; its remedy is the expression's
    own level count (or an explicit "not estimable" that refuses nothing silently), and it needs
    its own red test. `runtime.py:877` **out** of this finding, to be examined by the rating-path
    owner: it sits on the scoring path, which the finding says nothing reads these diagnostics
    from; it concerns a different artifact (the Rating Version's scorer, not the transparency
    output) and different requirement text (FR-239's bundle semantics, not FR-174), and it is not
    shown wrong, so it belongs in its own finding if the examination shows a defect.
- Other `source_columns[` reads in the tree
  (`packages/pricing-core/src/pricing_core/modelling/factors.py:190,303,314` at `a2f77b2d`) are
  **outside this finding** and **not examined**; they are named so that WK-690's later slices read
  them, not because they are shown wrong.

### 3. The requirement text, quoted with its locator (`docs/specs/02-modelling.md` at `a2f77b2d`)

`FR-MODEL-33` is a pre-migration id. `docs/REDIRECTS.csv:707` maps it:
`FR-MODEL-33,FR-132,docs/specs/02-modelling.md,...`. Its current id is **FR-132**. FR-132 is the
*existence* rule for the transparency artifact, and it is **not** the clause an expression Factor
leaves undelivered (see "Which clause" below). The clauses that are:

**FR-174** (`02-modelling.md:271`, §3.7):
> GBM-specific diagnostics: evaluation curve per iteration for train and holdout, gain/cover/frequency
> importance, **permutation importance on the holdout, partial dependence for declared factors**,
> monotonicity verification (that the fitted response actually respects declared constraints), and
> tree-count/depth summary.

Its dated amendment, 2026-08-22 (OQ-596), fixes the scope: *"'declared factors' means the factors
the Model Spec declares, and the sweep already covers exactly those"*, and adds *"neither per-factor
block may assume one source column per factor — FR-176."* An expression Factor in a Model Spec is a
declared factor; it is therefore in scope, and it is multi-column. The amendment does not invert
the clause; it narrows "declared" to "in the spec" and so confirms the expression Factor is covered.

**FR-176** (`:273`), the precedent for this exact shape: *"permutation importance and the
partial-dependence sweep each open by taking `factor.source_columns[0]`, which an `interaction` —
required to name none — makes an `IndexError`"*, resolved by recording the skip, *"a cross that no
per-factor diagnostic describes is a gap a reviewer must be able to see, which is why it is
recorded rather than silent. Owner WK-690."* That gap was later delivered for the cross
(FR-177, amended 2026-09-28, WK-1178, FD-1195). The expression Factor is the second factor type to
meet the same two lines.

**FR-175** (`:272`): the partial-dependence grid of a banded or grouped factor is drawn on the
factor's own levels (the code comment at `diagnostics.py:1059-1075` cites it for the axis).
An `expression` Factor with a `banding_id` (FR-97, amended 2026-10-16 by S4) is exactly that case.

**FR-183** (`:280`): permutation importance *"is measured on the holdout by definition"*, labelled
as holdout; a diagnostic reported without its holdout counterpart is a defect except where this
amendment says the diagnostic is single-valued. This is why the omission must be recorded **in the
artifact** and not be left as an absent row.

**FR-132** (`:193`), the quoted existence rule: *"Every non-GLM Model must carry at least one
**Transparency Artifact** before it can be referenced by a Rating Version (R3). Three forms are
supported and may be present in any combination."* A GBM that fits an expression Factor can still
carry a transparency artifact (SHAP summary FR-134, GLM approximation FR-133), so FR-132 as an
existence rule is met. Whether FR-134's per-factor dependence summaries are correct for an
expression Factor was **not examined** (see Disposition, owed checks).

### 4. Which clause is undelivered

Once S4 omits expression Factors from both per-factor blocks, the clause left undelivered is
**FR-174's "permutation importance on the holdout, partial dependence for declared factors"**,
read with its 2026-08-22 amendment (declared = every factor in the spec; no single-source-column
assumption), for the one factor type that is both declared and multi-column. FR-175's axis limb
is undelivered with it for a banded expression Factor. A reviewer of such a model sees a named
omission instead of a curve: FR-202's gate for `fitted → review` (*"requires diagnostics"*, `:367`)
is met by the other factors' diagnostics, so the model can advance with its most formula-driven
factor undescribed.

## Severity: the reasoning (the maintainer rules it)

Proposed **MEDIUM**.

- **Not HIGH.** The mispricing-class defect, a wrong number presented as a measure, is what the
  ruling stops in S4. What remains after S4 is an omission with a reason code: no wrong value
  reaches a reader, and nothing downstream (rating, scoring) reads these diagnostics. Without
  S4's omission this finding would be HIGH.
- **Not LOW.** The omitted factor is the factor type chosen for the most bespoke rating logic, so
  the model a reviewer most needs to understand is the one whose per-factor effect is shown
  least. Under FR-174 the gap is a missing deliverable and not stale metadata. FR-176 treated the
  same omission for a cross as a requirement to schedule, and it took a Work to deliver it.
- It is not reached by a user until S4 merges and a model with an expression Factor is fitted, so
  the cost is bounded to a model class that does not exist on `main`.

## Disposition

**Verdict: `deferred with an owner` (CLAUDE.md §13): WK-690.** Proposed by the auditor; the
verdict and the severity are the lead's and the maintainer's to adopt.

**Remedy: real diagnostics on the resolved expression column.** Permutation importance shuffles
the factor's **resolved** value (the expression's result, or its banded level when a `banding_id`
is set) as a single unit; partial dependence holds that resolved value at one observed level and
sweeps the factor's own axis (numeric quantiles, or the banded levels under FR-175's cap),
with `_TRANSFORMED_FACTOR_TYPES` and `_resolved_axis` extended to `EXPRESSION`. Because
`predict_gbm` re-resolves from raw columns on every call, the held or shuffled value must be
applied through the operand columns **jointly**, the way FR-177 does it for a cross (one shared
order for the shuffle; one real row of the held level for the sweep), so no unobserved operand
combination is scored. Two points for the owner's slice to decide in the spec first (CLAUDE.md
§0), not here: how a factor that shares an operand column with an expression Factor is reported
(the FR-178 `operand_of_interaction` rule has no analogue yet), and the reason that replaces
S4's `EXPRESSION_FACTOR` once the omission is lifted (FR-177 kept `no_source_column` as a reserved,
no-longer-emitted reason for artifacts already written; the same applies here).

**Proof, on a deliberately broken input (CLAUDE.md §13):** a test **per diagnostic** on an
`expression` Factor over **two** source columns, so the first-column read is distinguishable:

1. permutation importance: its degradation equals that of permuting the resolved expression
   column, and **differs** from the first-operand-only degradation (the test computes both, so
   the old behaviour is shown to fail it);
2. partial dependence: the curve's axis labels are the expression's own levels (or banded levels),
   not raw first-column values;
3. a banded expression Factor: the axis is the banding's levels (FR-175);
4. the S4 omission test is **inverted** in the same slice (an expression Factor now yields a
   number, and the reason code is no longer emitted for it).

Each must be shown red against the S4 code and green against the fix.

**The event that next discharges this finding:** the merge of the WK-690 slice that lifts the
omission, with the four tests recorded in its ledger. Until then S4's omission and its `EXPRESSION_FACTOR` reason
are the interim, and the red-first tests S4 carries pin them so that a later change to the
omission surfaces as a failing test.

**Owed checks (not run: ALONE gate in force):** none of this finding's claims depend on a run.
Two read-only checks are owed to whoever delivers the remedy: (a) whether `models/{id}/transparency`
(FR-134 per-factor SHAP dependence) is correct for an expression Factor, not examined here;
(b) the `source_columns` sites in §2 above: `model_specs.py:86` (proposed in scope) and
`runtime.py:877` (proposed out of scope) are stated there, and the `factors.py` sites are not examined.

**Not in this finding.** S4's omission itself (SL-1274, the lead's adoption of DP-1274-DIAG), the
`is_certainly_numeric` question (DP-1274-NUMERIC), and the interaction-diagnostics work that FR-176
to FR-178 moved to WK-1178.
