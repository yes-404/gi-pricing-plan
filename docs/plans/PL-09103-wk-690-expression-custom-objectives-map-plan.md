---
id: PL-9103
family: plan
kind: map
title: WK-690 — `expression` custom objectives: Map Plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: 6c6f4532c7d0ec65646225108f8cf9f8f570c746
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1184, PL-930, PL-1070]
---

# PL-9103 — WK-690, `expression` custom objectives: Map Plan

First filed 2026-09-28 as working id PL-9103; `created` re-dated so the id sequence stays
non-decreasing (check 31).

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement each slice's leaf plan task-by-task. This map plan has no executable tasks of its own; each slice gets a leaf plan. Every leaf plan's executor also binds `python-package`, `python-test` (requirement markers, negative tests), `dev-commands` (the two-half gate and its traps) and, for Slice 2, `library-spike`; Slice 5 binds `vue-frontend` and `vue-best-practices`.

## Goal

Deliver `02` FR-144's `expression` Custom Objective end to end: one expression parser
brought to `02` §4.6's four per-context profiles; SymPy derivation of the gradient and
hessian; a vectorised compilation target that `pricing-core` owns; the `expression` kind
certified on WK-661's existing machinery (FR-151); the kind made available behind
`expression_objectives_enabled`, together with `custom_objective:author` and its check
(`06` FR-367); `expression` Factors (FR-95); and the authoring view. The Work ends with a
`WF-702` Route B run over HTTP and the flag still off by default. It is cut into five
slices (Slices 1 to 5). Each slice closes on its own clean audit and the lead's merge.

**Architecture:** A map plan, per `docs/process/delivery-process.md` §3, in the form of
`PL-930` (`docs/plans/PL-00930-wk-672-testing-map-plan.md`). It fixes the scope, the slice
cut, the sequencing and the decision points. Each slice gets a leaf plan when it opens, as
`PL-1177` is to `PL-930`. No slice is task-broken here. Nothing about Slice 1 waits on a
decision point, so its leaf plan can be written as soon as this plan is accepted.

**Tech Stack:** `pricing-core` (the parser `pricing_core.data.expressions`, the
objective machinery `pricing_core.modelling.objectives`), SymPy (new: `02` §8), NumPy,
Polars, XGBoost and LightGBM custom-objective callables, FastAPI + Pydantic v2
(`model-schema`), PostgreSQL through SQLAlchemy async, Vue 3 with a generated API client.

**Spec:** [`../specs/02-modelling.md`](../specs/02-modelling.md) §3.1, §3.7, §4.6, §4.7,
§5.1, §5.3, §8 and §9; [`../specs/06-governance.md`](../specs/06-governance.md) FR-366
and FR-367; [`../specs/07-platform.md`](../specs/07-platform.md) FR-448 and FR-449;
[`../specs/01-data-management.md`](../specs/01-data-management.md) FR-36 and §4.5;
[`../workflows/WF-00702-custom-objective-lifecycle.md`](../workflows/WF-00702-custom-objective-lifecycle.md)
Route B. Every `02` §4.6 citation here means §4.6 **as amended by `RL-1184` E2** (the
profile table and OQ-1185's decision). That text merged with #830 (merge commit
`3767b3b4`). §4.6 at that merge matches the text this plan was drafted from, apart from the
minted ids.

## Status

**Draft.** Written at `6c6f4532`, with #830's spec text read at `3319b34f` (the head of
`p2-e-spec`). It stays `draft` until the deputy's acceptance line below is dated. DP-1,
DP-2 and DP-3 are the maintainer's, resolved by the deputy by delegation (the deputy's
entry of 2026-09-28 13:51:08). DP-4 and DP-5 are marked with their resolver in the table.
*(revised 2026-09-29 against 19c395ac: the resolver of DP-1 to DP-5 is `RL-9202` (working id; minted at #847's
turn), the decision-maker's ruling, which adopts the deputy's entry of 2026-09-28 14:06:12
BST unchanged. #847 is open and unmerged at this tree. Slices 3 and 4 are gated on it: DP-3
blocks Slice 3 and DP-4 blocks Slice 4, and neither slice's leaf plan is filed before
`RL-9202` merges under its minted id.)* *(Revised again 2026-09-29, on the lead's direction
and `RL-9202` at #847 head 14d2caa0: **Slice 1 is also gated**, on `RL-9202` merged and on
**OQ-9660** (the exact `sympy` pin) ruled. See Slice 1's Gates.)*

- **No dependency on WK-674** *(revised 2026-09-29 against 19c395ac)*. No slice here waits on a
  WK-674 slice, and no WK-674 output is an input to any slice. Before this revision the plan
  did not name WK-674 at all: `git show 97986b7a:docs/plans/PL-09103-wk-690-expression-custom-objectives-map-plan.md | grep -c WK-674`
  prints `0`. The names below were added for the serialisation list only. *(Corrected
  2026-09-29 on auditor-plans' finding F1 at 18f85019: the text said that this file never
  names WK-674, with a count of `0`. At 18f85019 this bullet itself named WK-674.)*
  The files that WK-690 slices and WK-674 slices both write, for the lead's serialisation:
  - `packages/model-schema/src/model_schema/permissions.py` and `06` §4.1 (`Role`,
    `RoleAssignment`, `Permission`): WK-690 Slice 3 (`custom_objective:author`) against
    WK-674 Slices 2 and 3 (the permission rows of `PL-1237`'s permission table, on
    `RL-1236` rows 26 and 32).
  - The generated `docs/contracts/`: WK-690 Slice 3 (`CustomObjective`) against every
    WK-674 slice that regenerates it (Slice 1's `Job`, `PL-1239`).
  - `docs/skills-map.md`: WK-690 Slice 1 **edits** it (the `sympy` row, Acceptance item 3).
    WK-674 may edit it: `PL-1237`:49 says a leaf plan that needs a new dependency updates it.
  - `docs/specs/07-platform.md`: WK-690 only **cites** it (FR-448, FR-449 and FR-450). No
    slice here edits it. WK-674 Slice 1 edits it (§4.1 `Job`, `PL-1239` Task 1). The order
    matters only if a WK-690 leaf plan finds that `07` must change.
  *(Added 2026-09-29 on auditor-plans' list-gap finding at 18f85019.)*

- Acceptance and Work activation: _pending — the deputy's dated line by delegation_

## Acceptance Standard

A fresh reviewer checks each item by the command or the named artifact.

1. **Every slice closes on its clean audit and the lead's merge on the maintainer's
   MERGE-ACK.** The maintainer's dated MERGE-ACK entry in the channel names the slice's
   PR and its full head SHA, and the lead merges with `--match-head-commit` on that SHA
   (`.claude/roles/lead.md` rule 4). The slice's clean audit is filed.
   *(revised 2026-09-29 against 19c395ac: the text read "The deputy's merge acknowledgement is recorded on
   the slice's PR", PL-1070 item 11's condition. That condition has since been replaced by
   `lead.md` rule 4.)* Per `CLAUDE.md` §13, a Slice closes on a clean audit and
   the lead's merge. No maintainer acceptance line is required for a slice, and none is to
   be waited on. (Source: `docs/plans/PL-01070-w37-7-the-remaining-creating-and-reading-instruments-leaf-plan.md`
   item 11.) The Work's own close is the maintainer's (by delegation, the deputy's) and
   follows `.claude/skills/close-workstream`.
2. **Each core-scope requirement has evidence or one of the four verdicts** at the Work
   close. The ids are listed in "Scope" below. Checked by
   `uv run python scripts/req-coverage.py` at the closing tree, one line per id, and by
   reading each marked test's assertions (`CLAUDE.md` §13, RFC-779: verify the claim, not
   the citation).
3. **SymPy is a locked dependency and `docs/skills-map.md` names it.**
   `grep -c -i '^name = "sympy"' uv.lock` prints `1`, and
   `git grep -n -i sympy -- docs/skills-map.md` returns at least one row. Both land in one
   commit (`CLAUDE.md` §10).
4. **The recipe and check corpus was measured before the limits were enforced.** Slice 1's
   PR carries the measurement table (per expression: source file, node count, depth). The
   commit that enforces the limits is a descendant of the commit that records the table. If
   any expression exceeds a limit, the deputy's dated line is recorded before the enforcing
   commit (`02` §4.6's profile note; `RL-1184` E2 item 4).
5. **Every refusal was seen failing first.** For each refusal the Work adds, the slice's
   ledger quotes the test failing before the implementation and passing after. The
   refusals are: bare comparison, `%`, ternary and boolean operator in the `objective` and
   `factor` profiles; node count 201; depth 21; an unknown function; an expression
   objective under `model:fit` alone; an expression objective with the flag off.
6. **The measured NFRs are measured.** NFR-476's 25 % overhead clause (expression versus
   the equivalent builtin) and NFR-480's 3-minute certification are each run N ≥ 3 times,
   with the one-minute load average recorded beside each run (`dev-commands` covers why
   load matters on this machine). The report gives the median and the spread, not one run.
7. **`WF-702` Route B runs end to end over HTTP.** With the flag on in one test workspace,
   §4.6's example objective (`asymmetric-burning-cost`) goes from create through derive,
   certify (`certified_with_findings`, convexity `violated`) and submit, to `approved` by
   two non-author Approvers. With the flag at its default in another workspace,
   `POST /api/v1/custom-objectives` with `kind: expression` answers 409
   `OBJECTIVE_KIND_NOT_ENABLED`. The run is one test file that a reviewer runs with
   `uv run pytest <that file> -q`. Slice 5's leaf plan names the file.
8. **`custom_objective:author` exists, is checked, and is in no built-in role.**
   `git grep -n 'custom_objective:author' -- packages/model-schema/src` returns the enum
   member. A test shows a caller with `model:fit` and without the new permission gets 403
   on create, derive and edit of an `expression` objective. A test shows the permission is
   absent from every built-in role's default set (`06` FR-367).
9. **Both halves of the gate pass** on each slice's final tree (`CLAUDE.md` §11). The four
   docs checks pass on a detached copy of each slice's committed tree.
10. **No slice opens while a decision point that blocks it is open.** Checked by reading
    the Decision points table. Every row marked blocking for slice N carries a
    `Resolved by` entry before slice N's leaf plan is filed.

## Global Constraints

- `pricing-core` stays importable standalone, with zero FastAPI, SQLAlchemy or Redis
  dependencies (`CLAUDE.md` §2). SymPy enters `pricing-core`'s dependencies. It is not a
  backend dependency.
- Model and objective definitions are declarative JSON artifacts, never pickles
  (`CLAUDE.md` §2). The derived gradient and hessian are stored as expression text in the
  artifact (FR-144; §4.6's `derived` block), never as a serialised SymPy object or a
  compiled function.
- Nobody hand-writes a shape that already exists in `model-schema` (`CLAUDE.md` §2). The
  frontend's objective types come from the generated client, never by hand
  (`CLAUDE.md` §3).
- User input never reaches `eval` or `exec` (NFR-483; FR-145). The compilation target is
  the platform's own expression tree: §8's SymPy row says "lambdify-free code generation
  into our own expression tree". `sympy.lambdify` is therefore out of bounds, because it
  generates and executes Python source.
- One parser, one allow-list walk, one security review, with a named profile per context
  (`02` §4.6 as amended by `RL-1184` E2). No slice adds a second parser.
- No pandas in new code (`CLAUDE.md` §3).
- Vue 3 Composition API with `<script setup lang="ts">` only (`CLAUDE.md` §3).
- Requirement ids are permanent. Any spec change a slice proves necessary lands in the same
  commit as its code, through `.claude/skills/spec-change` (`CLAUDE.md` §2 and §5).
- The flag's default stays the safe value, off (`07` FR-449), whatever DP-3 decides.

## Scope

Derived from the specification first, at `6c6f4532` with #830's amendments at `3319b34f`,
and then evidenced in code (`CLAUDE.md` §13). Every id is listed individually.

### Core scope — the ids this Work delivers

| Spec section | Id | What WK-690 owes | Evidence at `6c6f4532` | Slice |
|---|---|---|---|---|
| `02` §3.7 | FR-144 | Loss in §4.6's `objective` profile; SymPy gradient and hessian at authoring time; stored as expressions; compiled at fit time | None. The only code naming it is the `/derive` route, which always refuses (`backend/src/app/api/custom_objectives.py`, `derive_custom_objective`) | 1, 2, 3 |
| `02` §3.7 | FR-145 | Allow-list AST walk; the ten functions; node cap 200 | Partial. The walk exists; the function set differs (no `clip`, `where`, `log1p`, `expm1`); no node or depth limit (§4.6's 2026-08-22 note) | 1 |
| `02` §3.7 | FR-146 | Certificate before submission, for the `expression` kind | Built for templates (FR-151) | 2, 3 |
| `02` §3.7 | FR-147 | Exclude points within `h` of a `Piecewise` boundary | Built for templates. First exercised on a real `where()` by this Work | 2 |
| `02` §3.7 | FR-148 | Branch discontinuity reported | As FR-147 | 2 |
| `02` §3.7 | FR-149 | Step-aware tolerance, Richardson extrapolation | Built for templates | 2 |
| `02` §3.7 | FR-150 | The `expression` kind, gated by the flag | The gate refuses whatever the flag says (`backend/src/app/platform/objectives.py`, `refuse_expression_kind`). The refusal becomes conditional in Slice 3 | 3 |
| `02` §3.7 | FR-152 | Non-convex expression: strategy required, second Approver | Built for the verdict. The two-approver rule is first reachable by an `expression` objective | 3 |
| `02` §3.7 | FR-163 | Lifecycle; non-author Approver; two Approvers when `convexity: violated` | Built for templates | 3 |
| `02` §3.7 | FR-165 | Fixed-size arrays; per-round wall-clock budget; NaN/inf abort naming round and input (a `CodedError` with no input values: FD-1219, `pricing_core/safe_error.py`; revised 2026-09-29 against 19c395ac) | **Partly met for templates:** fixed-size arrays and the NaN/inf abort are built, with four markers in `packages/pricing-core/tests/test_objectives.py`. The per-round wall-clock budget is built for neither kind (`packages/pricing-core/tests/test_expression_nfrs.py` module docstring) | 2 |
| `02` §3.1 | FR-95 | `expression` Factors over dataset columns, in the `factor` profile | None | 4 |
| `02` §3.1 | FR-208 (expression arm) | `Factor` gains the field and its validator arm; `expression` resolves | Refused by name at resolution | 4 |
| `02` §4.6 | profile table, OQ-1185 | Four profiles; `where()` everywhere; strict `objective` and `factor`; limits in all four | See FR-145 | 1 |
| `02` §4.7 | expression half | `symbolic_vs_numeric_gradient` and `symbolic_vs_numeric_hessian`; `library_versions.sympy` | The `analytic_vs_numeric` pair only | 2 |
| `02` §5.3 | Custom objective library (`/objectives`) | Editor with live parse errors, derived gradient and hessian display, loss-curve preview | List only (the 2026-08-27 note in that row) | 5 |
| `02` §3.10 | FR-207 | The staged contract: `custom_objective_ref` on `GlmSpec` (absent) and on `Model` (declared and unbuilt) are WK-690's | Declared and unbuilt, owner WK-690 (FR-207's 2026-08-25 amendment) | 3 |
| `02` §9 | NFR-476 | Expression objective overhead ≤ 25 % versus the builtin | None | 2 |
| `02` §9 | NFR-480 | Certification < 3 min, with the smoke fit | Templates only | 3 |
| `02` §9 | NFR-483 | Never `eval`; position-accurate refusal; compiled objectives bounded | The first two clauses are tested for the recipe parser | 1, 2 |
| `02` §9 | NFR-484 | Audit events for objective derivation | Derivation does not exist | 3 |
| `06` §3.3 | FR-366 | The permission question answered before the flag may be lifted | Answered by FR-367 on 2026-08-18. Discharged when FR-367 lands | 3 |
| `06` §3.3 | FR-367 | `custom_objective:author`, distinct from `model:fit`, in no built-in role, "the enum member and its check land together in WK-690" | Absent: not in `packages/model-schema/src/model_schema/permissions.py` | 3 |
| `07` §3.8 | FR-448 | `expression_objectives_enabled` is a workspace setting | Built: `features.expression_objectives_enabled`, default `False` (`backend/src/app/platform/settings.py`) | 3 |
| `07` §3.8 | FR-449 | The flag defaults to the safe value | Built. What changes is that the flag starts to gate something | 3 |
| `01` §3.2 | FR-36 | `derive_expression` in the `recipe` profile | Built on the unprofiled parser | 1 |
| `01` §4.5 | `expression` check | Row predicate in the `check` profile | Built on the unprofiled parser (`pricing_core.data.validate`) | 1 |
| `WF-702` | Route B, B1.1 to B4.6, and §7's failure rows | The whole governed journey | None | 5 |

### Held pending DP-1 — not slices of this plan

**Held; `RL-9202` (unmerged) moves them to P3.** *(revised 2026-09-29 against 19c395ac, on `RL-9202` (working id; #847 head 14d2caa0): DP-1 (b) sends FR-85,
FR-86's field, FR-210 and FR-208's `spline` and `polynomial` arms to Phase 3, spec change
first, deferred with an owner (the maintainer), the event being the P2 phase closure
record. `02` still names WK-690 for each at 19c395ac, until #847 merges.)*

`02` names WK-690 as owner of items that are not `expression` objectives. They are listed
so that nothing is dropped. They are **not** cut into slices here. The plan is valid under
any answer to DP-1: under DP-1 (a) the planner re-cuts them into later slices through a
replan (a new `PL-` with `supersedes:`). Under (b) or (c) they leave this plan, and
Slices 1 to 5 do not change.

| Id | Owner clause in `02` | State at `6c6f4532` |
|---|---|---|
| FR-85 | "Owner WK-690" (OQ-595); its gate was closed by FR-86 the same day | One marker. Nothing left to build under this id alone |
| FR-86 | The capability `diagnostic` named, re-sited on the Model Spec, "gated and owned by WK-690" | **No FR of its own.** The field exists only in FR-86's prose. `ModelSpecCommon.factors` is still a flat tuple of UUIDs |
| FR-210, with FR-208's `spline` and `polynomial` arms | "Owner **WK-690**" (OQ-571) | Not built. Both arms stay refused |

The marker counts use the predicate `req("FR-<n>")`, counted with `git grep -c` over
`packages/*/tests/*.py` and `backend/tests/*.py` at `6c6f4532`.

*(revised 2026-09-29 against 19c395ac: the FR-176, FR-177 and FR-178 rows are removed. Each row of `02`
(`02-modelling.md:271`–`:273`) now carries a dated amendment: "the owner is WK-1178 …
FD-1195 moved FR-176, FR-177 and FR-178 to WK-1178". FR-178 was delivered by #880
(`9fa2b833`) and #887, and FR-177 by #887 (`95faf68b`). What WK-690 still holds under DP-1
is FR-85, FR-86's field, and FR-210 with FR-208's `spline` and `polynomial` arms. `02`
still names WK-690 for each at this tree (FR-85 `:86`, FR-86 `:87`, FR-208 `:371`, FR-210
`:373`). `RL-9202` (unmerged) moves them to Phase 3. The recount with the same predicate at
19c395ac prints FR-85 `1`, FR-86 `1`, FR-210 `0`: the FR-85 cell is unchanged.)*

### Held pending DP-2

| Id | What is open |
|---|---|
| FR-154 (the `expression` half) | "Custom eval metrics follow the same lifecycle and grammar as objectives". FR-155 makes Phase 1 templates-only. Expression metrics are named by no roadmap row and no owner clause |

*(revised 2026-09-29 against 19c395ac, on `RL-9202` (working id; #847 head 14d2caa0), DP-2 (b)): which half of FR-154 is which.* FR-154 reads
"Custom eval metrics (`feval`) follow the same lifecycle and grammar as objectives,
declared separately so that a metric can be reused across objectives"
(`02-modelling.md:218`).
- **The non-expression half** is the template metric: the separately declared, versioned
  Custom Metric that FR-155 makes "templates-only" in Phase 1 (`02:219`). It stays where it
  is already delivered. `req("FR-155")` counts 17 markers at 19c395ac
  (`git grep -c` over `packages/*/tests/*.py` and `backend/tests/*.py`), in five files
  including `backend/tests/test_custom_metrics_api.py`. WK-690 does not touch it.
- **The expression half** is "the same … grammar as objectives" applied to a metric: a
  metric written in §4.6's grammar. It goes to Phase 3, spec change first, with the same
  owner and event as DP-1 (the maintainer; the P2 phase closure record). No slice here
  adds a `metric` profile.

### Premises re-derived at this tree

The lead's brief asked for four checks. Each is recorded as reproduced or not.

1. **`02` §5.3's authoring view: reproduced.** The Custom objective library row
   (`/objectives`) specifies the "editor with live parse errors … derived gradient/hessian
   display, loss-curve preview at chosen parameter values". Its 2026-08-27 note says that
   the display and the preview are not rendered and the view is list-only. Slice 5 owns
   the difference.
2. **`07` FR-450: its content is reproduced, and it does not support the flag.** FR-450 is
   "The API implements `00` §5 exactly: `/api/v1`, cursor pagination, RFC 9457 …". It says
   nothing about feature flags. The flag rests on FR-448 (the settings list names
   `expression_objectives_enabled`) and FR-449 (flags default to the safe value, and this
   one stays off for Phase 1). The predecessor's withdrawal of the FR-450 citation was
   correct. This plan does not cite FR-450 for the flag.
3. **FR-165 is partly met for templates: reproduced.** The evidence is in the table above.
   The unmet part is the per-round wall-clock budget, for both kinds. Slice 2 builds it
   once, for both kinds.
4. **The Model Spec's `diagnostic` field has no FR of its own: reproduced.** It exists only
   as FR-86's sentence "that field is what an asking caller gets, gated and owned by
   WK-690". No FR specifies it and no code declares it. Building it would be a spec change
   first (`CLAUDE.md` §0). This is part of DP-1.

Found while deriving the scope, not in the brief:

5. **The FR-144 amendment puts SymPy in Slice 1, not Slice 2.** The amendment reads:
   "WK-690's first slice brings `pricing_core.data.expressions` to §4.6's `objective`
   profile before any objective is derived: `where()` compiled to a SymPy `Piecewise`".
   The adopted proposal added `sympy` in Slice 2. This plan follows the spec text: Slice 1
   adds `sympy` with the `skills-map.md` update and translates the `objective` profile to a
   SymPy tree. Slice 2 differentiates that tree and compiles the result. This is recorded
   so the lead can confirm the move or amend it.
6. **The parser has a caller that the profile table does not name.** `filter_rows`
   (`01` FR-35) parses through the same `compile_expression`
   (`pricing_core/data/prepare.py`, the `filter_rows` case). §4.6's table names
   `derive_expression` alone for the `recipe` profile. This is DP-5.
7. **`03` FR-244 says rating `expression` steps "use the same restricted grammar as `02`
   §4.6"**, but those steps are handed to the ZEN engine (`pricing_core/rating/runtime.py`)
   and never reach `pricing_core.data.expressions`. `03` FR-276 validates their vocabulary
   against the engine. So the "one parser" sentence does not cover a fifth context that
   the spec claims shares the grammar. This is DP-5.
8. **Three objective codes are declared in `02` §5.1 and not registered in
   `backend/src/app/errors.py`.** *(revised 2026-09-29 against 19c395ac: the premise said that
   `OBJECTIVE_GRAMMAR_VIOLATION` was named by no module spec, which is false.)* `02` §5.1
   declares `OBJECTIVE_NOT_CERTIFIED` (`02-modelling.md:2054`),
   `OBJECTIVE_GRAMMAR_VIOLATION` (`:2056`) and `OBJECTIVE_NONFINITE_DERIVATIVE` (`:2057`),
   each "(declared, Phase 2)". The note at `:2091`–`:2094` marks them declared-and-unbuilt
   and owned by Phase 2's `expression` objectives. `WF-702` names two of them:
   `OBJECTIVE_GRAMMAR_VIOLATION` (B1.5 and §7) and `OBJECTIVE_NONFINITE_DERIVATIVE` (C5). None of the three is in `backend/src`. `00` FR-22
   (`00-overview.md:226`) makes `audit-docs.py` check 10 compare each §5.1 table with
   `errors.py`. One fact qualifies "unbuilt": `pricing-core` already raises
   `OBJECTIVE_NONFINITE_DERIVATIVE` as `NonFiniteDerivativeError`
   (`pricing_core/modelling/errors.py:62`, raised at `objectives.py:706`, FR-165's template
   abort). The codes go to these slices:
   - `OBJECTIVE_GRAMMAR_VIOLATION`: Slice 3. The HTTP create and derive paths raise it from
     Slice 1's position-accurate `ExpressionError`.
   - `OBJECTIVE_NONFINITE_DERIVATIVE`: Slice 2 raises it for both kinds (FR-165), reusing
     the existing class. Slice 3 registers it where the fit job surfaces it (`WF-702` C5).
   - `OBJECTIVE_NOT_CERTIFIED`: Slice 3. Submission of an `expression` objective with no
     certificate raises it (FR-146) in place of the `VALIDATION_FAILED` stand-in that
     `:2094` records. The leaf plan states whether the template path moves too. If
     moving it changes an existing response, the leaf plan raises a decision point.
   Each slice removes the code's "declared" marker in `02` §5.1 and registers the code in
   `errors.py` in one commit.
9. **§4.6 and §4.7 disagree on the SymPy version.** §4.6's example records
   `"derivation_version": "1.14.0"`, and §4.7's example records `"sympy": "1.13.x"`. Both
   are illustrative. Slice 1's leaf plan pins the locked version, and Slice 2 records it
   on the certificate from `sympy.__version__`, never as a literal.
   *(revised 2026-09-29 against 19c395ac, on `RL-9202` (working id; #847 head 14d2caa0)): Slice 1 pins **one exact** `sympy` version in `uv.lock` and
   amends both §4.6 and §4.7, dated, to cite that pin. Which version is **OQ-9660** (open,
   working id on #847), placed at the roadmap §10 gate *Before WK-690 Slice 1*. Slice 1 is
   gated on it.)*
10. **Stale owner text in code.** A comment in `pricing_core/modelling/diagnostics.py`
    (`:1040`) names WK-664 as FR-177's owner, and the spec names WK-1178
    (`02-modelling.md:272`, FD-1195). *(revised 2026-09-29 against 19c395ac: the premise said the spec
    names WK-690. `diagnostics.py` is now WK-1178's file, not a WK-690 slice's, so its
    comment is WK-1178's to correct.)* The docstring of the `/derive` route
    (`backend/src/app/api/custom_objectives.py`, `derive_custom_objective`) cites
    requirements in a pre-migration id form (module-scoped `FR-MODEL-` numbers). Neither changes
    behaviour. Slice 3 edits that route and corrects its docstring.

## Decision points

Kind, blocking status and resolver per RFC-937 §1.7. A blocking row must carry a resolver
id before the slice it blocks may start. A non-blocking row names the step that resolves
it and the default applied until then.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | Where do the non-expression items that `02` makes WK-690's go: FR-85, FR-86 (with its Model Spec field), and FR-210 with FR-208's `spline` and `polynomial` arms? *(revised 2026-09-29 against 19c395ac: FR-176, FR-177 and FR-178 are removed from the question. FD-1195 moved them to WK-1178 (`02:271`–`:273`), and #880 and #887 delivered FR-177 and FR-178. The options and the recommendation below are kept as written; their FR-176 to FR-178 limb is discharged.)* | **(a)** Keep them in WK-690, cut by a replan into slices after Slice 5. **(b)** Split by kind. FR-176, FR-177 and FR-178 go to WK-1178, the P2 standing maintenance Work (#840, which is unmerged). FR-85 and FR-86's field, and FR-210 with its two arms, go to a Phase 3 roadmap row as spec-change-first work with a named owner. **(c)** Move all of them to the roadmap's Deferred list with a named owner. | **(b).** FR-178 is a live defect: a GBM with a sparse cross cannot produce diagnostics. A defect needs an owner that can fix it this phase, and it has nothing to do with expressions. The maintenance Work exists for this kind of work. FR-86's field has no FR, and FR-210 is a capability with a stated precondition. Neither is a defect. `CLAUDE.md` §0 makes both spec work before code, and nothing in Phase 2 asks for them. (a) makes the Work's close wait on unrelated diagnostics. (c) leaves a live defect in Deferred. | scope | no. Slices 1 to 5 do not depend on it. It must be resolved before the Work closes, because a close cannot leave an owned id without a verdict | `RL-9202` (working id; minted at #847's turn) |
| DP-2 | Is the `expression` half of FR-154 (expression Custom Metrics) WK-690's? | **(a)** Yes, as a sixth slice after Slice 3. It needs a fifth, `metric`, profile in §4.6 (spec change first). **(b)** No. It goes to Phase 3 with a named owner, and the profile row is written when it is scheduled. **(c)** Yes, but held until the Work's other slices close. | **(b).** No finding and no user journey asks for expression metrics. A fifth profile widens Slice 1's security review for an unrequested capability. Metrics are never differentiated, so they reuse none of Slice 2. | scope | no. It must be resolved before the Work closes | `RL-9202` (working id; minted at #847's turn) |
| DP-3 | Does WK-690 make the flag **liftable** (the gate reads the setting, the default stays off), or does it **lift** it (the default becomes on)? | **(a)** Liftable only. After Slice 3 the kind works in any workspace whose Admin turns the flag on, and the default stays `False`. **(b)** Lifted. The default becomes `True` at the Work's close. **(c)** Liftable, and lifted in `dev` environments only. | **(a).** `07` FR-449 says flags "default to the safe value". The roadmap title's "lifting" is satisfied when the flag becomes something that can be lifted: today it gates nothing, because the refusal is unconditional. An insurer then chooses to enable a risk-bearing capability, which is the purpose of the flag. `06` FR-366's precondition is met by FR-367, so (a) has no open governance question behind it. | decision point | yes, for Slice 3 | `RL-9202` (working id; minted at #847's turn) |
| DP-4 | Does FR-210's gate ("a continuous Factor must be rateable and reviewable before any continuous basis type is scheduled") bind an `expression` Factor whose result is numeric? | **(a)** Yes. Slice 4 waits for FR-210 to be delivered. **(b)** Partly. Slice 4 ships `expression` Factors whose result is categorical, or numeric and banded through a stored banding (`02` FR-97), so every such Factor has FR-113's relativity table. A bare numeric result is refused by name until FR-210 is delivered. **(c)** No. FR-210 names `spline` and `polynomial`, and an expression over a numeric column is the `identity` case FR-210 already records as live. | **(b).** FR-210's argument is that a Factor an actuary can fit and cannot price must not ship. (c) would ship more of the gap FR-210 records. (a) holds FR-95 behind a capability that DP-1 may move to Phase 3. (b) ships what can be priced today and refuses the rest by name, which is FR-208's own pattern. | decision point | yes, for Slice 4 | `RL-9202` (working id; minted at #847's turn) |
| DP-5 | The profile table names four contexts, but the parser has a fifth caller and the spec claims a sixth context. Where do `filter_rows` (`01` FR-35; `pricing_core/data/prepare.py`) and rating `expression` steps (`03` FR-244) sit? | **(a)** `filter_rows` uses the `recipe` profile. §4.6 gains a dated note that rating steps are evaluated by the ZEN engine under `03` FR-244 and FR-276 and are not a profile of this parser. **(b)** As (a), and `03` FR-244 is also amended to stop saying "the same restricted grammar". **(c)** Add `filter` and `rating` profiles. | **(a),** with Slice 1's spec commit. `filter_rows` already parses today with the `recipe` operator set, so (a) keeps its behaviour exactly. A `rating` profile would describe a parser that rating does not use. Amending `03` (b) is a WK-671 and WK-673 matter, not WK-690's. | fact | no. Slice 1's leaf plan applies (a) as the default and records it. The deputy may amend it before Slice 1 merges | `RL-9202` (working id; minted at #847's turn) |

*(revised 2026-09-29 against 19c395ac: the Resolved by cells were empty, though Status recorded DP-1 to
DP-3 as resolved. Each now names `RL-9202`, the decision-maker's ruling on #847, which rules
all five. Slices 3 and 4 are gated on it: their leaf plans are not filed until `RL-9202`
merges under its minted id, and the cells then cite that id.)*

## Tasks

A map plan's tasks are its slices. Each slice's leaf plan breaks it into bite-sized tasks
per `writing-plans`. The five slices run in order, one at a time (`delivery-process.md`
§8: one slice at a time within a Work).

```
Slice 1 parser profiles + limits + sympy ──→ Slice 2 derivation + compilation + certificate
                                                   │
                                                   └──→ Slice 3 the kind through the platform
                                                         [DP-3] ──→ Slice 5 authoring UI
Slice 1 ─────────────────────────────────────────────→ Slice 4 expression factors [DP-4]
                                                         (after Slice 3, by the one-at-a-time rule)
```

Slice 4 depends only on Slice 1 in code. It runs after Slice 3 because of the
one-slice-at-a-time rule, not because of a data dependency. The lead may move it earlier
without a replan if Slice 3 is waiting on DP-3.

### Slice 1 — The parser brought to §4.6's four profiles, with its limits

**Scope.** `pricing_core.data.expressions` gains a named profile per context (`objective`,
`factor`, `recipe`, `check`). The profile selects the bound symbols, the operators and the
function set, as in §4.6's profile table.
- `where(cond, a, b)` in every profile. Its condition is one comparison between two
  sub-expressions. It translates to Polars (`recipe`, `check`) and to a SymPy `Piecewise`
  (`objective`), as FR-144's amendment requires.
- `clip`, `log1p` and `expm1` are added to every profile. `ceil`, `coalesce`, `floor` and
  `round` stay in `recipe` and `check` only.
- The `objective` and `factor` profiles refuse bare comparisons, `%`, ternaries and
  boolean operators, each with a position-accurate `ExpressionError` (NFR-483).
- The node-count ≤ 200 and depth ≤ 20 limits are configurable and bind all four profiles.
- `derive_expression` and `filter_rows` pass `recipe` (DP-5 default), and the `expression`
  validation check passes `check`.
- `sympy` is added to `pricing-core`, with the `docs/skills-map.md` update, in one commit.

**Its first task is the corpus measurement, and nothing is enforced before it.** The
predicate: every expression string that reaches `compile_expression` from a committed
source. The sources are `examples/fremtpl2/seed.py`, `backend/tests/test_data_jobs.py`,
`packages/pricing-core/tests/test_prepare.py`,
`packages/pricing-core/tests/test_expression_nfrs.py`, and any committed recipe JSON. The
leaf plan re-derives this list with a sweep over the tree and reports the class and total,
not a sample. Each string is measured with the node and depth counter Slice 1 itself adds,
named in the leaf plan by function and file, and run before the limit check is wired in.
If an expression exceeds a limit, the slice reports to the deputy and waits (`RL-1184` E2
item 4).

**Spec edits in the slice.** DP-5's note in §4.6, and FR-145's function list aligned with
the table if the leaf plan finds the two differ.
*(revised 2026-09-29 against 19c395ac, on `RL-9202` (working id; #847 head 14d2caa0)):*
- **DP-5's addition.** `03` FR-244 (`03-rating-engine.md:146`) is amended, dated, to say
  the rating grammar is FR-244's own: ZEN's expression language, restricted to FR-244's
  function list and verified by FR-276. It shares function names with §4.6 where they
  coincide, but it is not one of §4.6's profiles. §4.6's DP-5 note says the same. Both
  edits land in **one commit**, so `02` and `03` never disagree. No check holds the
  pairing: it is prose.
- **The sympy pin.** §4.6 (`"derivation_version"`) and §4.7 (`library_versions.sympy`)
  are amended, dated, to cite the exact version pinned in `uv.lock` (OQ-9660's answer).

**Depends on:** #830 merged. **Blocks:** Slices 2 and 4.
**Gates** *(revised 2026-09-29 against 19c395ac, on `RL-9202` (working id; #847 head 14d2caa0))*: Slice 1's leaf plan is filed only when **both** hold:
1. `RL-9202` is merged under its minted id (DP-5's addition and the pin obligation are
   its rulings).
2. **OQ-9660 is ruled**: the exact `sympy` version to pin.

**Gate outline.** The refusal tests of Acceptance item 5 for the limits and the strict
profiles, seen failing first. Every existing recipe and check test passes unchanged, which
proves that the `recipe` and `check` profiles only add. NFR-483's two existing tests are
re-pointed to run in every profile. Both gate halves pass.

### Slice 2 — Symbolic derivation, the compilation target, and the expression certificate

**Scope.** All in `pricing-core`; no route.
- `derive(loss)` differentiates the Slice 1 SymPy tree twice with respect to `f`. It
  returns the canonical gradient and hessian text that §4.6's `derived` block shows, with
  `derivation_tool`, `derivation_version` (from `sympy.__version__`) and `derived_at`.
- A compiler turns the derived text into vectorised NumPy kernels through the platform's
  own expression tree. It does not use `lambdify` (Global Constraints).
- FR-165 for both kinds: fixed-size arrays; the per-round wall-clock budget (built once,
  for templates and expressions); the existing NaN/inf abort, reused.
  *(revised 2026-09-29 against 19c395ac, on `RL-9202` (working id; #847 head 14d2caa0)): the ruling leaves the per-round budget to "Slice 2 or 3",
  with the plan to state which. This plan states **Slice 2**. The cut is unchanged.)*
  *(revised 2026-09-29 against 19c395ac, FD-1219 and `pricing_core/safe_error.py`):* the abort and the
  budget error are `CodedError`s, or are otherwise on `safe_error`'s allow-list. Each
  message names the round and the input by field name, never an input value. At this tree
  `NonFiniteDerivativeError` is a `ModellingError`, not a `CodedError`. The leaf plan
  reconciles this with `WF-702` C5's "the offending input range".
- The certificate's `symbolic_vs_numeric_gradient` and `symbolic_vs_numeric_hessian`
  checks, on FR-151's machinery. All nine checks run (FR-158). FR-147's boundary exclusion
  and FR-148's discontinuity finding are exercised on a real `where()`. The certificate
  records `library_versions.sympy`.
- §4.6's rule that division by a sub-expression that can be zero is a certification
  failure.

**Depends on:** Slice 1. **Blocks:** Slice 3.

**Gate outline.** §4.6's example objective derives to the canonical gradient and hessian
§4.6 prints, compared as SymPy expressions and not as strings. The certificate for that
objective is `certified_with_findings`, with convexity `violated` and
`branch_discontinuity` `warn`. A loss whose gradient overflows aborts naming the round. A
kernel that exceeds its budget aborts with a typed error. NFR-476 is measured per
Acceptance item 6. The leaf plan considers a `library-spike` on `Piecewise`
differentiation before its first task.

### Slice 3 — The `expression` kind through the platform, behind the flag

**Scope.**
- `model-schema`'s `CustomObjective` accepts `kind: expression`, with its `loss`,
  `parameters` and `derived` block. `docs/contracts/` is regenerated.
- `POST /api/v1/custom-objectives/{id}/derive` does the derivation (FR-144).
  `POST /custom-objectives` and `/derive` refuse with `OBJECTIVE_KIND_NOT_ENABLED` only
  while the workspace's flag is off (FR-150; DP-3).
- `custom_objective:author` and its check land together (`06` FR-367). Create, edit and
  version of an `expression` objective require the new permission. Selecting a template
  stays `model:fit`, and submitting stays `model:submit`. No built-in role grants it.
  FR-366 is discharged.
  *(revised 2026-09-29 against 19c395ac, `CR-1247` Proposal 1 (c), lead verdict ADOPTED and maintainer
  acceptance at `CR-1247` :143–:144, :158 and :159):* the `06` §4.1 row for `custom_objective:author`,
  the enum member in `packages/model-schema/src/model_schema/permissions.py`, and the route
  check land in **one commit**. The `06` §4.1 row is in this slice's scope.
- `OBJECTIVE_GRAMMAR_VIOLATION` and `OBJECTIVE_NOT_CERTIFIED` are raised here, and
  `OBJECTIVE_NONFINITE_DERIVATIVE` is registered where the fit job surfaces it. Each is
  registered in `backend/src/app/errors.py` with its `02` §5.1 "declared" marker removed,
  in one commit, with the position for the grammar code (premise 8, revised 2026-09-29).
- Certification of the `expression` kind as a 202 job (FR-146). NFR-480 is measured.
- Submission with two Approvers when `convexity: violated` (FR-152, FR-163).
- Audit events for derivation (NFR-484).
- FR-207's two `custom_objective_ref` residuals are made live or re-noted. The leaf plan
  states which, with its reason, and raises a decision point if the GLM arm's custom
  objective turns out to be a separate capability.

**Depends on:** Slice 2; DP-3 (`RL-9202`, merged under its minted id); and **WK-1178's
permission-parity check and its `RL-`**, both merged before the commit that adds
`custom_objective:author`. *(revised 2026-09-29 against 19c395ac, `CR-1247` Proposal 1 (c): "WK-1178 builds
the check, before the first slice that adds a new name. On the current plans that is
WK-690's `custom_objective:author`". The decision-maker's `RL-` that records the rule is
not filed at this tree: `git grep -l CR-1247 -- docs/rulings` names only `RL-1252`, which is
a different proposal.)* **Blocks:** Slice 5.

**Gate outline.** API tests over HTTP for every row of `WF-702` §7 that this slice makes
reachable. The permission negative tests of Acceptance item 8. The flag-off refusal, and
the flag-on success in a second workspace. `generate-contracts.py --check` passes.

### Slice 4 — `expression` Factors

**Scope.** `Factor` gains the expression field and its validator arm (FR-208's expression
arm). `resolve_factors` resolves an `expression` Factor through the `factor` profile over
the declared dataset columns only (FR-95). The refusal is removed for `expression` alone.
`spline`, `polynomial` and `offset` stay refused as they are. The result-type rule is
DP-4's answer. The spec edit for that rule lands in the same commit.

**Depends on:** Slice 1 and DP-4 (`RL-9202`, merged under its minted id; revised 2026-09-29 against 19c395ac). **Blocks:** nothing in this plan.

**Gate outline.** An `expression` Factor fits in a GLM and in a GBM and yields a
relativity table (FR-113). An expression that names an undeclared column is refused at
creation. Each refusal of DP-4's rule is seen failing first. The existing refusal tests
for the other three arms still pass.

### Slice 5 — The authoring view, and `WF-702` Route B end to end

**Scope.** `02` §5.3's Custom objective library: the editor with live parse errors
(through the API, never a client-side parser), the derived gradient and hessian display,
and the loss-curve preview at chosen parameter values. The editor is hidden or disabled
while the flag is off. The Objective certificate view renders `violated` as a finding
(FR-152's 2026-08-25 amendment). One HTTP test file runs `WF-702` Route B from B1.1 to
B4.6 (Acceptance item 7). The flag's default is unchanged (DP-3).

*(revised 2026-09-29 against 19c395ac, advisory):* the loss-curve preview is a new `ChartFigure` caller.
A new caller is the trigger of **OQ-550**, which was re-opened 2026-09-28 (`RL-1184` E10;
`docs/open-questions.md:41`). Slice 5's leaf plan revisits OQ-550 before it adds the chart.

**Depends on:** Slice 3. **Blocks:** the Work's close.

**Gate outline.** Both gate halves pass, including `pnpm --dir frontend generate:api` and
`type-check` run under `env -C`. A rendering test fails if `certified_with_findings` is
styled as a failure. The Route B file passes.

## Self-review

1. **Spec coverage.** Every row of "Core scope" names a slice. FR-142, FR-143, FR-151,
   FR-153, FR-164 and FR-166 are built and generic over `kind`. They are exercised by
   Route B in Slice 5 and are not claimed as new work. The DP-1 and DP-2 items are held
   with their resolver, not dropped.
2. **Placeholder scan.** The slices are scope statements by design, as in `PL-930`. The
   one deferred choice (FR-207's residuals, Slice 3) is named as the leaf plan's to state,
   and the condition that turns it into a decision point is written down.
3. **Consistency.** The profile names (`objective`, `factor`, `recipe`, `check`) are
   §4.6's own. The flag key is `features.expression_objectives_enabled`, as the settings
   registry spells it. The permission is `custom_objective:author`, as `06` FR-367 spells
   it.
