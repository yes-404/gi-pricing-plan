---
id: PL-1327
family: plan
kind: leaf
title: WK-690 Slice 2 — symbolic derivation, the compilation target and the expression certificate: leaf plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: 11c76b6c83647c512796fedb9c0143927dcd78cb
phase: P2
work: WK-690
slice: SL-1272
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1268, PL-1295, RL-1265, RL-1289, RL-1291, RL-1292, RL-1293, LG-1304]
---

# WK-690 Slice 2 — symbolic derivation, the compilation target and the expression certificate: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `library-spike` (Task 1), `python-package` and `python-test` (every code task), `contract-schema` and `contract-guard` (Task 5), `spec-change` (Tasks 4 and 5), `dev-commands` (the gate, the slot rule and the NFR-476 measurement) and `git-hygiene`, and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Give `pricing-core` the `expression` objective's middle layer. It covers four things:
- derive the gradient and hessian of a Slice 1 SymPy tree, as canonical text in §4.6's
  grammar;
- compile that text into vectorised NumPy kernels through the platform's own tree;
- budget every boosting round's objective time, for templates and expressions alike;
- certify an `expression` objective with all nine §4.7 checks, the first two being
  `symbolic_vs_numeric_gradient` and `symbolic_vs_numeric_hessian`.

No route, no workspace flag and no persisted artifact are added: those are Slice 3's.

**Architecture.**
- **Derivation.** `derive` differentiates the tree Slice 1's `to_sympy` returns, lifts each
  branch outward with `piecewise_fold`, and prints it with a printer this plan adds. The
  printer's output is text that Slice 1's parser accepts in the `objective` profile.
- **Compilation.** `compile_kernel` parses that text, then walks the validated `ast` into
  NumPy operations on the caller's fixed-size arrays. No string ever becomes code.
- **One compiled type.** An `ObjectiveFns` built from an expression is the same type as one
  built from a template. So `make_xgb_objective`, `make_lgb_objective` and
  `certify_objective`'s battery serve both kinds unchanged, apart from the first two checks'
  names and their reference derivative.
- **The budget.** The per-round budget is measured around the objective callable inside the
  two `make_*_objective` adapters, so it binds both kinds at the one place both pass through.

**Tech Stack:** Python 3.12 `ast`, SymPy 1.14.0 (pinned by `RL-1289`), NumPy, XGBoost and
LightGBM callable objectives, Pydantic v2 (`model-schema`), pytest. No new dependency.

**Spec:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) §3.7:
  - **FR-144** (`02-modelling.md:208`): derivation and compilation. Storage and the
    approval review are Slice 3's.
  - **FR-146** (`:210`): the certificate for the `expression` kind. Persistence and
    attachment to the approval request are Slice 3's.
  - **FR-147**, **FR-148**, **FR-149**: exercised on a real `where()`.
  - **FR-151**: the substituted check.
  - **FR-165**: fixed arrays, the per-round budget and the NaN/inf abort.
- `02` §4.6: the `derived` block and the division-by-zero rule. `02` §4.7: the certificate,
  the expression half.
- `02` §9 **NFR-476** (the 25 % overhead limb) and **NFR-483**'s third clause (bounded memory
  and per-round time).
- [`../workflows/WF-00702-custom-objective-lifecycle.md`](../workflows/WF-00702-custom-objective-lifecycle.md)
  C5 (`WF-00702-custom-objective-lifecycle.md:137`): the NaN abort names the round and "the
  offending input range".

**What this plan implements.** `PL-1268` Slice 2 and its row `SL-1272`
(`docs/roadmap.md:896`), which lists FR-144, FR-146, FR-147, FR-148, FR-149, FR-165,
NFR-476, NFR-483 and the `02` §4.7 expression half. Two rulings bind it:
- `RL-1265` places FR-165's per-round budget in Slice 2.
- `RL-1289`'s second violation belongs to this slice: "a `derived.derivation_version` or
  `library_versions.sympy` is written from a literal rather than `sympy.__version__`". It
  requires a test with a patched `sympy.__version__`.

Slice 1 (`PL-1295`, merged by #981 at `bd67fb51`, ledger `LG-1304`) is the ground this
stands on. Its delivered code is read as premises below, not its plan's expectations.

## Status

Filed 2026-09-30 against `11c76b6c` (origin/main), under working id 9946. The status is the
`status:` field alone. Activation is that field's flip. The facts of activation (gates met,
the grant and the dispatch record) live in the dispatch record, quoted in the slice ledger's
Task 0, as the maintainer directed at 2026-09-30 14:48:52 BST, item (3). This paragraph does
not change when they happen.

**Held from Slice 1, not this slice's.** Slice 1's held FR-244 sentence (`LG-1304`, Task 6
and the closing pass) goes to #967's code slice (`PL-1314`). Nothing here writes `03`.

### Write set, and contention under `RL-1263` option (c)

Measured at `11c76b6c` against the two slices in flight or next.

This slice writes:
- `pricing-core`: `packages/pricing-core/src/pricing_core/modelling/objectives.py`, the new
  `packages/pricing-core/src/pricing_core/modelling/expression_objective.py`, and
  `packages/pricing-core/src/pricing_core/modelling/errors.py`;
- `model-schema`: `packages/model-schema/src/model_schema/objectives.py` (the battery) and
  `packages/model-schema/src/model_schema/__init__.py` (its re-export);
- contracts: `docs/contracts/schemas/objective-certificate.schema.json`, which is
  hand-authored and so not registry-exempt, plus the regenerated `docs/contracts/` outputs;
- `scripts/bench-model.py` (the NFR-476 limb);
- tests under `packages/pricing-core/tests/`, `packages/model-schema/tests/` and
  `backend/tests/test_contracts.py`, if the guard needs a new comparison;
- docs: `docs/specs/02-modelling.md` (§4.6, §4.7 and §5.1 notes, and FR-165's amendment),
  the ledger, and `docs/INDEX.md`.

Against the other lane:
- **WK-674 Slice 2a** (`SL-1302`, `PL-1303`, lane A) writes the backend approvals path:
  `backend/src/app/platform/approvals.py`, `backend/src/app/api/approvals.py`,
  `backend/src/app/db/models.py`, `backend/src/app/db/session.py`, a new
  `backend/migrations/versions/` revision, `backend/tests/conftest_db.py` and
  `backend/tests/test_approval_guard.py`. There is **no shared path**.
- **The #967 code slice** (`PL-1314`, PR #969 at `023dcbd4`, next on lane B) writes:
  - `packages/pricing-core/src/pricing_core/rating/` (`compile.py`, `score.py`,
    `vocabulary.py`, `authored.py`), with tests;
  - `packages/model-schema/src/model_schema/rating.py`, `backend/src/app/errors.py` and
    `docs/specs/03-rating-engine.md`.
  There is **no shared existing file**. The one shared path is the generated `docs/contracts/`
  outputs (`openapi/generated.json`, `schemas/generated/`), if both regenerate, and those
  are registry-exempt: the later slice regenerates at its second merge.
- **One sequencing constraint that is not about files.** Task 6 is the NFR-476 measurement,
  a timing measurement, so under `RL-1263` item 3 it **runs alone**: the other gate slot stays
  empty while it runs. The lead grants that window. Every other task can run beside a lane-A
  slice.
- **Verdict: file-clean beside WK-674 Slice 2a and beside the #967 code slice.** Task 6
  needs a solo window.

## Acceptance Standard

A fresh reviewer checks each item by the command given, on the slice's final tree. Suite
runs are slotted, with `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`
(`LG-1304`, the slot rule).

1. **§4.6's example derives to the gradient and hessian §4.6 prints, compared as SymPy
   expressions and never as text.** `uv run pytest
   packages/pricing-core/tests/test_expression_objective.py -q -k spec_example` passes. The
   derived text parses back in the `objective` profile. Its `to_sympy` form minus the
   printed form simplifies to 0 after `piecewise_fold`, for both.
2. **The derivation version is read, never written** (`RL-1289`, second violation). `-k
   derivation_version` passes. With `sympy.__version__` patched to `"9.9.9"`, the recorded
   `derivation_version` and the certificate's `library_versions.sympy` are both `"9.9.9"`.
3. **The compiler builds kernels from text, and never from a string evaluator.** `-k
   kernel` passes, including a run with `eval`, `exec`, `compile`, `sympy.lambdify` and
   `sympy.parsing.sympy_parser.parse_expr` replaced by raisers, with a warm-up and a
   `sys.modules` assertion (the `PL-1295` F7 pattern). Each kernel agrees with SymPy's own
   evaluation to 1e-12 relative on a seeded grid.
4. **The per-round budget binds both kinds** (FR-165; NFR-483, third clause). `uv run pytest
   packages/pricing-core/tests/test_objectives.py -q -k round_budget` passes: a template
   whose callable is slowed past a small budget aborts with the typed error naming the
   round, an expression aborts the same way, and a positive control inside the budget
   completes.
5. **The NaN/inf abort is reused for expressions and carries what DP-S2-4 rules.** `-k
   nonfinite` passes: an expression whose gradient overflows aborts naming the round.
6. **An expression certificate carries all nine checks, with the symbolic pair** (FR-146,
   FR-151, FR-158). `uv run pytest packages/pricing-core/tests/test_objectives.py -q -k
   expression_certificate` passes, on §4.6's example:
   - `overall` is `certified_with_findings`;
   - `convexity` is `violated` and `branch_discontinuity` is `warn`;
   - the gradient detail reports a non-zero excluded count (FR-147, on a real `where()`);
   - `library_versions` has `sympy`.
   A template certificate still carries the `analytic_*` pair, unchanged.
7. **The battery accepts either pair and nothing else.** `uv run pytest
   packages/model-schema/tests/test_objectives.py -q -k battery` passes. A certificate
   mixing one `analytic_*` and one `symbolic_*` name is refused, and so is one short of
   nine. `uv run python scripts/generate-contracts.py --check` passes.
8. **Division by a sub-expression that can be zero fails certification** (§4.6), as DP-S2-5
   rules. `-k division` passes, with a positive control: a denominator bounded away from 0
   certifies.
9. **Every refusal and failure was seen red first.** The ledger quotes each test failing
   before its implementation, or a mutation control on the finished code where the
   intermediate red cannot be staged (the `LG-1304` pattern). Each control is named by the
   code it disables.
10. **NFR-476's expression limb is measured, not asserted.** The ledger holds the shape
    DP-S2-6 rules and N ≥ 3 paired runs (expression and equivalent builtin), each with its
    one-minute load average. It gives the median ratio and the spread, run in a solo window
    (`RL-1263` item 3).
11. **`pricing-core` stays standalone and pandas-free.** `uv run lint-imports` passes.
    `git diff 11c76b6c -- packages | grep -E '^\+.*import pandas'` prints nothing.
12. **Both halves of the gate pass** on the final tree (`CLAUDE.md` §11). The ledger quotes
    every rc, and pytest's `N passed` against main's at `11c76b6c`.

## Global Constraints

- `pricing-core` reads no clock and allocates no id (ADR-703; `02-modelling.md:1123`). So
  `derive` returns `derivation_tool` and `derivation_version`, and not `derived_at`, which
  Slice 3's backend stamps. The certificate path stays as it is: the backend stamps
  `certified_at`. **This is a declared departure from `PL-1268` Slice 2**, whose scope
  bullet lists `derived_at` among `derive`'s returns. The reason is ADR-703: `pricing-core`
  may not read a clock. It is stated here rather than folded in, as premise d's is. *(Revised 2026-09-30 on auditor-plans2's audit of PL-1327 at fbe5a255, finding F2.)*
- No string reaches `eval`, `exec`, `compile`, `sympy.sympify`, `sympy.parse_expr` or
  `sympy.lambdify` (NFR-483; `02` §8, *"lambdify-free code generation into our own
  expression tree"*).
- Kernels evaluate elementwise on the caller's arrays. Every intermediate has the input's
  length, and none grows with anything else (FR-165).
- One parser. Derived text is parsed by Slice 1's `parse_expression` in the `objective`
  profile, with the limits DP-S2-2 rules. There is no second parser.
- `sympy==1.14.0` is the only version, read from `sympy.__version__` (`RL-1289`).
- The symbols are real (`RL-1293`). The node limits are `RL-1291`'s. The arity is
  `RL-1292`'s.
- No pandas in new code (`CLAUDE.md` §3).
- Requirement ids are permanent. Spec edits go through `spec-change`, dated, in the same
  commit as their code.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice owes | Task |
|---|---|---|---|
| `02` §3.7 | FR-144 | SymPy derivation at authoring time; derived text in the grammar; compiled to NumPy kernels | 2, 3 |
| `02` §3.7 | FR-146 | The certificate, for the `expression` kind (persistence and approval are Slice 3's) | 5 |
| `02` §3.7 | FR-147 | The excluded count near a real `where()` boundary | 5 |
| `02` §3.7 | FR-148 | Where the derived gradient or hessian is discontinuous, reported | 5 |
| `02` §3.7 | FR-149 | The step-aware, Richardson comparison, against the symbolic derivative | 5 |
| `02` §3.7 | FR-151 | `symbolic_vs_numeric` substitutes for `analytic_vs_numeric`; every other check is shared | 5 |
| `02` §3.7 | FR-165 | Fixed-size kernels; the per-round budget for both kinds; the NaN/inf abort reused | 3, 4 |
| `02` §9 | NFR-476 | The expression-versus-builtin overhead ≤ 25 %, measured | 6 |
| `02` §9 | NFR-483 | Third clause: compiled objectives bounded in memory and per-round time. The first two clauses are re-tested on the new path | 3, 4 |
| `02` §4.7 | expression half | The symbolic pair; `library_versions.sympy` | 5 |

FR-158 is not new work: its nine-check floor already holds, and Task 5 keeps it for the
second battery.

### Premises re-derived at `11c76b6c`

Each line cites its file, at the tree above. A subagent swept
`packages/pricing-core/src/pricing_core/modelling/objectives.py` and
`packages/model-schema/src/model_schema/objectives.py`. The planner read Slice 1's modules
and ledger directly.

a. **Slice 1's API, as delivered** (`packages/pricing-core/src/pricing_core/data/expression_sympy.py`):
   - `to_sympy(expression, *, parameters=(), limits=DEFAULT_LIMITS) -> sympy.Expr` (`:46-61`),
     in the `objective` profile, with every symbol `sympy.Symbol(name, real=True)` (`:60`);
   - `where` → `Piecewise((then, relation), (otherwise, True))` (`:86-94`);
   - `clip` → `Min(Max(x, lo), hi)`; `log1p` and `expm1` from `sympy.codegen.cfunctions`.
   `parse_expression(expression, profile, *, symbols=None, limits=DEFAULT_LIMITS)` is at
   `packages/pricing-core/src/pricing_core/data/expressions.py:288`, and
   `ExpressionLimits(max_nodes=200, max_depth=20)` at `expressions.py:124`.

b. **The compiled type is template-shaped.** `ObjectiveFns` is a frozen dataclass
   (`objectives.py:563`). Its `loss`, `grad` and `hess` compute `w * template_fn(y, f,
   params)` (`objectives.py:595-602`), and its `stabilise` applies the FR-152 strategy
   (`objectives.py:604`). It carries `template` and `_template`. `compile_objective` raises
   `OBJECTIVE_KIND_NOT_ENABLED` when `objective.template is None`
   (`objectives.py:661-667`).

c. **Certification is template-shaped in two places.**
   - `_derivative_checks` (`objectives.py:921`) emits `analytic_vs_numeric_gradient` and
     `analytic_vs_numeric_hessian`.
   - `_branch_mask` (`objectives.py:907-918`) and `_branch_check` (`objectives.py:1017`) read
     `f_boundaries`, `y_anchors` and `branch_description` from `_template`. FR-148 is
     *declared* per template, not found.
   - The comparison itself is generic: `_richardson` (`objectives.py:855`), `_agreement`
     (`objectives.py:866`) and `_status_for` (`objectives.py:899`), with `_STEP = 1e-4`
     (`objectives.py:83`).
   - `library_versions` holds `numpy` (`objectives.py:1331`) and `xgboost` (added in the
     smoke fit, `objectives.py:1244`).

d. **The battery is enforced in `model-schema`, and it names only the analytic pair.**
   `OBJECTIVE_CERTIFICATE_CHECKS` (`packages/model-schema/src/model_schema/objectives.py:612-622`)
   is enforced by `battery_is_exactly` (`model_schema/objectives.py:625`) through
   `ObjectiveCertificate._the_battery_is_all_nine_named_checks`
   (`model_schema/objectives.py:751-763`). The hand-authored enum is at
   `docs/contracts/schemas/objective-certificate.schema.json:28-31`, whose `$comment` (`:6`)
   records the rename away from `symbolic_vs_numeric_*`. **An expression certificate cannot
   be constructed at this tree.** So this slice touches `model-schema`, although
   `PL-1268` Slice 2 says "All in `pricing-core`". The map plan's intent (no route, no
   artifact) holds, and this is stated rather than folded in.

e. **`CustomObjective` has no expression fields.** It has no `loss`, `parameters` or
   `derived` (`model_schema/objectives.py:438-500`), and `_only_templates_are_built`
   (`model_schema/objectives.py:482-500`) refuses `kind: expression`. Adding them is Slice
   3's (`PL-1268` Slice 3). This is DP-S2-1.

f. **There is no per-round budget.** The only timing is the smoke fit's elapsed detail
   (`objectives.py:1248`, `:1280`).
   `packages/pricing-core/tests/test_expression_nfrs.py:25-30` says so: *"The per-round
   wall-clock budget is not implemented anywhere"*.

g. **The NaN abort names data values.** `_finite_or_abort` (`objectives.py:698-713`)
   raises `NonFiniteDerivativeError` (`packages/pricing-core/src/pricing_core/modelling/errors.py:62-73`),
   a `ModellingError`, not a `CodedError`. Its message carries the bad rows' **y and f
   ranges**, as numbers. WF-702 C5 asks for "the offending input range", while FD-1219 and
   `pricing_core/safe_error.py` keep input values out of persisted error text. This is
   DP-S2-4.

h. **`02` §5.1 declares no budget code.** `grep -o -E 'OBJECTIVE_[A-Z_]+'
   docs/specs/02-modelling.md | sort -u` prints 13 names. One of them, `OBJECTIVE_STATUSES`,
   is a fragment of the Python constant `FITTABLE_OBJECTIVE_STATUSES` and not a code. So
   there are 12 codes, and none of them is about time. A new code
   is a spec change. This is DP-S2-3.

i. **SymPy 1.14.0's derivative vocabulary**, from a `uvx --with sympy==1.14.0` spike with
   `f` real, first and second derivative with respect to `f`:
   - `log`, `sqrt` and `log1p` produce no new function heads.
   - `exp` and `expm1` produce `exp`.
   - `where` produces `Piecewise`.
   - `abs` produces `sign` and `DiracDelta`.
   - `min`, `max` and `clip` produce `Heaviside` and `DiracDelta`.
   - `Heaviside(0)` is `1/2`.
   None of `sign`, `Heaviside` or `DiracDelta` is in §4.6's grammar. This is DP-S2-2.

j. **`piecewise_fold` lifts the branch outward on §4.6's example**, giving
   `Piecewise((-2*w*w_under*(y - exp(f))*exp(f), y > exp(f)), (-2*w*w_over*(y - exp(f))*exp(f), True))`.
   That is algebraically, not textually, §4.6's printed gradient. So Acceptance 1 compares
   expressions.

k. **NFR-476 has no expression harness.** `scripts/bench-model.py:93` budgets `"NFR-476 gbm
   fit, 500 trees"` on the builtin `count:poisson` (`scripts/bench-model.py:246`), and no
   expression limb exists. `docs/closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md:135`
   records it unmeasured.

l. **Marker counts at `11c76b6c`.** Command: `for id in FR-146 FR-147 FR-148 FR-149 FR-151
   FR-165 NFR-476 NFR-483; do git grep -c "req(\"$id\")" -- ':(glob)packages/*/tests/**'
   ':(glob)backend/tests/**'; done`. Results: FR-146 13, FR-147 1, FR-148 3, FR-149 2,
   FR-151 3, FR-165 4, NFR-476 0, NFR-483 9. The bare pathspec `packages/*/tests` matches no
   files here, which is why the glob form is used.

m. **The backend reaches certification at one site**:
   `backend/src/app/worker/model_handlers.py:1557-1561` calls `certify_objective` with
   `default_sampling(objective)` (`backend/src/app/platform/objectives.py:464`). This slice
   does not change that call, and the template path stays byte-identical in behaviour.

### Decision points

The kinds follow `document-ids.md` §1.7. Every decision point is the decision-maker's, one
`RL-` each. Each blocks this plan's activation, and each is applied at the task named.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S2-1 | What input does `pricing-core` take for an `expression` objective before `model-schema` carries one (premise e)? | **(a)** A pricing-core dataclass mirroring the future artifact fields. **(b)** Move `CustomObjective`'s `loss`, `parameters` and `derived` into this slice. **(c)** Primitive arguments: `loss: str`, `parameters: Mapping[str, float]`, `y_domain`, `hessian_strategy`, `hessian_min`, `ref`; Slice 3 passes the artifact's fields. | **(c).** (a) is a second definition of a shape `model-schema` will own, which `CLAUDE.md` §2 forbids. (b) moves Slice 3's contract work, and its contract regeneration, into this slice. (c) adds no shape. | decision point | yes, for activation. Applied at Tasks 2 to 5 | decision-maker, its own `RL-` (pending) |
| DP-S2-2 | How do `sign`, `Heaviside` and `DiracDelta` (premise i) appear in derived text, and under what limits is derived text parsed? | **(a)** The printer rewrites them into the objective grammar: `sign(x)` → `where(x > 0, 1, where(x < 0, -1, 0))`, `Heaviside(x)` → `where(x > 0, 1, 0)`, and `DiracDelta(·)` → `0`, the almost-everywhere derivative, with the kink reported by FR-148. Derived text is parsed in the `objective` profile under `DERIVED_LIMITS`, set from Task 1's measurement. **(b)** A fifth `derived` profile admitting `sign` and `heaviside` (a §4.6 profile-table amendment). **(c)** Refuse, as certification `failed`, any loss whose second derivative contains `DiracDelta` (`abs`, `min`, `max`, `clip`). | **(a).** One grammar and one parser (§4.6). (c) would make half the function list unusable in objectives. The `Heaviside(0) = 1/2` convention does not matter where the point set has measure zero, and FR-147 excludes those points from the comparison. | decision point | yes, for activation. Applied at Task 2 (printer) and Task 3 (limits) | decision-maker, its own `RL-` (pending) |
| DP-S2-3 | What does the per-round budget time, what is its default, and what does it raise? | **(a)** The objective callable's own wall-clock inside `make_*_objective`, default **30 s per round**, a keyword on both adapters, raising a new `OBJECTIVE_ROUND_BUDGET_EXCEEDED` (a `CodedError`, declared in `02` §5.1 "(declared, Phase 2)" and registered in the backend in Slice 3). **(b)** As (a), with a per-row rate derived from NFR-476. **(c)** No default: the caller must pass a budget. | **(a).** The budget is a runaway guard (NFR-483: "cannot exceed their per-round time budget"), not the performance target, which is NFR-476's and measured separately (Task 6). A rate derived from NFR-476 would turn a slow machine into a fit failure. | decision point | yes, for activation. Applied at Task 4 | decision-maker, its own `RL-` (pending) |
| DP-S2-4 | How is WF-702 C5's "offending input range" reconciled with FD-1219's rule that error text carries no input values (premise g)? | **(a)** Keep the numeric ranges in the message, and let `safe_error` reduce the persisted text to the type. **(b)** Make `NonFiniteDerivativeError` a `CodedError` whose text names the round, the row count and the fields (`y`, `f`) with no values. The numeric ranges go to structured attributes (`round_index`, `rows`, `y_range`, `f_range`) that the access-controlled job record may keep. **(c)** Treat the ranges as aggregates that are not inputs, and change nothing. | **(b).** It meets both texts: C5's range is present, and FD-1219's text is value-free. It applies to templates too, where the hazard is **latent**, one `PL-1268` Slice 2 already names. The ranges are not persisted in any job error today: the worker's generic handler reduces the error through `safe_job_error_text` (`backend/src/app/platform/safe_exception.py:30-47`, used at `backend/src/app/worker/tasks.py:35`) to `safe_error_text`, which keeps only the type of a non-`CodedError`. (b) makes the error a `CodedError`, whose text *is* persisted, which is why that text must carry no value. *(Revised 2026-09-30 on auditor-plans2's audit of PL-1327 at fbe5a255, finding DP-S2-4 wording.)* | decision point | yes, for activation. Applied at Task 4 | decision-maker, its own `RL-` (pending) |
| DP-S2-5 | How is §4.6's "division by a sub-expression that can be zero over the declared domain" decided, and which check reports it? | **(a)** Numerically, on the certificate's own grid: every denominator in the loss and the derived text is evaluated. A zero, or a sign change along any sampled `y`'s `f`-sweep, is `failed` under `finiteness`, naming the denominator's text. **(b)** Symbolically, with `sympy.solve` over the declared domain. **(c)** A tenth check. | **(a).** (b) is incomplete for transcendental denominators and has no time bound. (c) breaks FR-158's nine. A sign change is a zero by continuity, so (a) catches a zero the grid steps over. | decision point | yes, for activation. Applied at Task 5 | decision-maker, its own `RL-` (pending) |
| DP-S2-6 | At what shape is NFR-476's 25 % limb measured on this machine? | **(a)** A declared reduced shape (1 M rows × 60 factors × 100 trees), N ≥ 3 paired runs, solo, with the ratio as the verdict. The full 5 M × 500 run goes to the dedicated host with an owner. **(b)** The full NFR shape here, N ≥ 3 (six fits of about 20 minutes each, solo). **(c)** Defer the limb wholly to the dedicated host. | **(a).** The limb is a ratio, and a ratio at a declared shape is a measurement. (b) holds the solo window for over two hours. (c) leaves the limb unmeasured, as `CR-1212` found it. | decision point | yes, for activation. Applied at Task 6 | decision-maker, its own `RL-` (pending) |
| DP-S2-7 | How large are derived gradients and hessians, relative to their loss, in nodes and depth? | Measured, not chosen: Task 1's spike over the corpus it names. | n/a | fact | no. Resolved at Task 1 (an `RS-` of kind `spike`, the executor's). **Nothing reads it before Task 1.** Its only reader is `DERIVED_LIMITS` (DP-S2-2), first used in Task 2. If the spike is inconclusive, the default is `DEFAULT_LIMITS` × 10: `ExpressionLimits(max_nodes=2000, max_depth=200)`, recorded as the default and reported to the lead. *(Revised 2026-09-30 on auditor-plans2's audit of PL-1327 at fbe5a255, finding F4.)* | executor, `RS-` spike at Task 1 |

## Tasks

The tasks run in order. Each ends in one commit.

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree, and `git branch --show-current` is the slice branch,
  created from `origin/main`.
- [ ] `uv sync --all-packages`.
- [ ] Quote the dispatch record in the ledger: gates met, the grant, and the rulings for
  DP-S2-1 to DP-S2-6 by id.
- [ ] Record main's slotted pytest total (Acceptance 12).
- [ ] Re-derive premises a–m at the slice's base, with the tree.
- [ ] Run `gh pr list --state open` and read anything touching `pricing_core/modelling/`,
  `model_schema/objectives.py`, `docs/contracts/schemas/objective-certificate.schema.json`,
  `02` §4.6, §4.7 or §5.1, or `scripts/bench-model.py`. Name the SHA read.
- [ ] Create the slice ledger (`LG-`, the executor's).

### Task 1: Spike — the derivative vocabulary and the size of derived text (DP-S2-7)

`library-spike`, on the locked `sympy==1.14.0`, recorded as an `RS-` of kind `spike`.

- [ ] Re-run premise i for each of the ten functions, and for the compositions
  `abs(y - f)`, `clip(f, lo, hi)`, `max(y, f) * where(f < y, a, b)` and §4.6's example.
  Record each derivative's function heads.
- [ ] Measure the growth from loss to gradient to hessian, in `ast.expr` nodes and depth
  (`RL-1291`'s predicate), over:
  - every objective-profile loss in the repository's tests at the base (`git grep -n
    "to_sympy(" -- packages/pricing-core/tests`);
  - §4.6's example;
  - three constructed worst cases: a 200-node loss built from nested `exp`, a 200-node loss
    built from nested `where`, and a 20-deep `log1p` chain.
  Record the ratios `max(nodes_hess / nodes_loss)` and `max(depth_hess / depth_loss)`.
- [ ] State the `DERIVED_LIMITS` the measurement supports: the maxima times a margin of 2,
  rounded up to a multiple of 100 nodes and 10 depth. It is recorded for DP-S2-2's ruling
  if that ruling has not already fixed it.
- [ ] Commit the `RS-` and the ledger entry: `docs(research): the derivative vocabulary and
  derived-text size (WK-690 S2, DP-S2-7)`.

### Task 2: `derive` — canonical derivation and the grammar printer

**Files:**
- Create: `packages/pricing-core/src/pricing_core/modelling/expression_objective.py`
- Create: `packages/pricing-core/tests/test_expression_objective.py`

**Interfaces:**
- Consumes: `to_sympy`, `OBJECTIVE_SYMBOLS` (premise a) and `parse_expression`.
- Produces:
  - `Derived` (frozen dataclass: `gradient: str`, `hessian: str`, `derivation_tool: str`
    (`"sympy"`), `derivation_version: str`);
  - `derive(loss: str, *, parameters: Collection[str] = ()) -> Derived`, per DP-S2-1 (c);
  - `to_grammar(expr: sympy.Expr) -> str`, the printer.

- [ ] **Step 1: Write the failing tests.**

```python
"""FR-144: an expression objective's gradient and hessian, derived at authoring time."""

from __future__ import annotations

import pytest
import sympy

from pricing_core.data.expression_sympy import to_sympy
from pricing_core.data.expressions import GrammarProfile, parse_expression
from pricing_core.modelling.expression_objective import DERIVED_LIMITS, derive

EXAMPLE = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
PARAMS = ("w_under", "w_over")
y, f, w, w_under, w_over = (
    sympy.Symbol(n, real=True) for n in ("y", "f", "w", "w_under", "w_over")
)


def _same(text: str, expected: sympy.Expr) -> bool:
    got = to_sympy(text, parameters=PARAMS)
    return sympy.simplify(sympy.piecewise_fold(got - expected)) == 0


@pytest.mark.req("FR-144")
def test_the_spec_example_derives_to_the_printed_gradient_and_hessian() -> None:
    """§4.6's `derived` block, compared as expressions (premise j): the text differs in
    form from §4.6's, and the maths must not."""
    d = derive(EXAMPLE, parameters=PARAMS)
    e = sympy.exp(f)
    assert _same(d.gradient, sympy.Piecewise(
        (2 * w * w_under * (e - y) * e, y > e), (2 * w * w_over * (e - y) * e, True)))
    assert _same(d.hessian, sympy.Piecewise(
        (2 * w * w_under * (2 * e - y) * e, y > e), (2 * w * w_over * (2 * e - y) * e, True)))


@pytest.mark.req("FR-144")
@pytest.mark.parametrize("loss", [EXAMPLE, "w * abs(y - f)", "w * clip(f, 0, y) ** 2",
                                  "w * (exp(f) - y * f)", "w * log1p(exp(f)) - w * y * f"])
def test_derived_text_is_in_the_objective_grammar(loss: str) -> None:
    """The printer's output is text Slice 1's parser accepts: no sign, Heaviside or
    DiracDelta survives (DP-S2-2 (a))."""
    d = derive(loss, parameters=PARAMS)
    for text in (d.gradient, d.hessian):
        parse_expression(text, GrammarProfile.OBJECTIVE,
                         symbols=frozenset({"y", "f", "w", *PARAMS}),
                         limits=DERIVED_LIMITS)


@pytest.mark.req("FR-144")
def test_the_derivation_version_is_read_from_sympy(monkeypatch: pytest.MonkeyPatch) -> None:
    """RL-1289's second violation: a patched version must be what is recorded."""
    monkeypatch.setattr(sympy, "__version__", "9.9.9")
    d = derive("w * (exp(f) - y * f)")
    assert (d.derivation_tool, d.derivation_version) == ("sympy", "9.9.9")


@pytest.mark.req("FR-144")
def test_derivation_is_deterministic() -> None:
    """The text a reviewer approves must be reproducible: two derivations are identical."""
    assert derive(EXAMPLE, parameters=PARAMS) == derive(EXAMPLE, parameters=PARAMS)
```

  The `-k spec_example` and `-k derivation_version` selectors of Acceptance 1 and 2 match
  these test names. If DP-S2-2 is ruled other than (a), the second test's set of losses
  follows the ruling: under (c), the `abs` and `clip` losses become refusal cases.
- [ ] **Step 2: Red.** An `ImportError` naming `pricing_core.modelling.expression_objective`.
  Quote it.
- [ ] **Step 3: Implement.** In `expression_objective.py`:
  - `derive(loss, *, parameters=())` builds `tree = to_sympy(loss, parameters=parameters)`
    and `fs = sympy.Symbol("f", real=True)`. It computes
    `g = sympy.piecewise_fold(sympy.diff(tree, fs))`, then
    `h = sympy.piecewise_fold(sympy.diff(g, fs))`. It returns `Derived(gradient=to_grammar(g),
    hessian=to_grammar(h), derivation_tool="sympy", derivation_version=sympy.__version__)`.
    `sympy.__version__` is read at call time, never bound at import.
  - `to_grammar(expr)` is a recursive printer over SymPy node types, and it raises
    `ExpressionError` naming any node type outside this list:
    - `Symbol` → its name.
    - `Integer` → the digits, parenthesised if negative.
    - `Rational` → `(p / q)`.
    - `Float` → `repr(float(x))`, parenthesised if negative.
    - `Add` → ` + `-joined terms, each term parenthesised.
    - `Mul` → ` * `-joined factors, each parenthesised.
    - `Pow(b, e)` → `(b) ** (e)`.
    - `exp`, `log` and `Abs` → `exp(…)`, `log(…)` and `abs(…)`. `log1p` and `expm1`, the
      `sympy.codegen.cfunctions` classes, print under their own names.
    - `Min` and `Max` → `min(…)` and `max(…)`.
    - `sign`, `Heaviside` and `DiracDelta`, per DP-S2-2's ruling. Under (a):
      `where((x) > 0, 1, where((x) < 0, -1, 0))`, `where((x) > 0, 1, 0)` and `0`.
    - `Piecewise((e1, c1), …, (en, True))` → nested `where(c1, e1, where(c2, e2, … en))`.
      A condition that is an `And` nests one `where` per conjunct, sharing the else-branch.
      An `Or` becomes a chain. A `Not` flips its relation.
    - A relation (`<`, `<=`, `>`, `>=`, `==`, `!=`) → `(lhs) op (rhs)`.
    Deterministic order comes from SymPy's canonical argument order (`expr.args`). The
    printer never sorts by `str`.
  - `DERIVED_LIMITS: Final = ExpressionLimits(max_nodes=…, max_depth=…)`, from DP-S2-2's
    ruling (which reads Task 1's `RS-`).
- [ ] **Step 4: Green.** Run the file, then a mutation control: with `to_grammar`'s
  `DiracDelta` branch removed, the `abs` and `clip` cases fail. Quote both runs.
- [ ] **Step 5: Commit:** `feat(pricing-core): derive an expression objective's gradient
  and hessian, printed in the objective grammar (FR-144, WK-690 S2)`.

### Task 3: `compile_kernel` — derived text to NumPy, through the platform's own tree

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/expression_objective.py`
- Modify: `packages/pricing-core/tests/test_expression_objective.py` (append)

**Interfaces:**
- Consumes: `parse_expression`, `DERIVED_LIMITS` and `Derived` (Task 2).
- Produces: `Kernel = Callable[[NDArray[float64], NDArray[float64], NDArray[float64]],
  NDArray[float64]]`, and `compile_kernel(text: str, *, parameters: Mapping[str, float],
  limits: ExpressionLimits = DERIVED_LIMITS) -> Kernel`.

- [ ] **Step 1: Write the failing tests** (append):

```python
import builtins
import sys

import numpy as np

from pricing_core.modelling.expression_objective import compile_kernel

RNG = np.random.default_rng(20260930)
N = 4096
Y = RNG.uniform(0.1, 50.0, N)
F = RNG.uniform(-3.0, 4.0, N)
W = RNG.uniform(0.5, 2.0, N)
VALUES = {"w_under": 2.0, "w_over": 1.0}


def _sympy_values(text: str) -> np.ndarray:
    """SymPy's own numeric evaluation, point by point: slow, and the reference."""
    e = to_sympy(text, parameters=PARAMS).subs({w_under: 2.0, w_over: 1.0})
    return np.array([float(e.subs({y: a, f: b, w: c}).evalf()) for a, b, c in zip(Y[:64], F[:64], W[:64])])


@pytest.mark.req("FR-144")
@pytest.mark.req("FR-165")
def test_a_kernel_agrees_with_sympy_and_keeps_the_input_length() -> None:
    d = derive(EXAMPLE, parameters=PARAMS)
    for text in (EXAMPLE, d.gradient, d.hessian):
        out = compile_kernel(text, parameters=VALUES)(Y, F, W)
        assert out.shape == Y.shape and out.dtype == np.float64
        np.testing.assert_allclose(out[:64], _sympy_values(text), rtol=1e-12)


@pytest.mark.req("NFR-483")
def test_a_kernel_is_built_without_a_string_evaluator(monkeypatch: pytest.MonkeyPatch) -> None:
    """Warm first (PL-1295 F7): Python's import machinery calls `exec`, so the patched build
    must import nothing new and give the same numbers."""
    warm = compile_kernel(EXAMPLE, parameters=VALUES)(Y, F, W)

    def refuse(*args: object, **kwargs: object) -> object:
        raise AssertionError("a string reached a code evaluator (NFR-483)")

    import sympy.parsing.sympy_parser as sympy_parser

    loaded = set(sys.modules)
    for target, name in [(builtins, "eval"), (builtins, "exec"), (builtins, "compile"),
                         (sympy, "lambdify"), (sympy_parser, "parse_expr")]:
        monkeypatch.setattr(target, name, refuse)
    np.testing.assert_array_equal(compile_kernel(EXAMPLE, parameters=VALUES)(Y, F, W), warm)
    assert set(sys.modules) == loaded
    with pytest.raises(AssertionError, match="NFR-483"):
        sympy.sympify("y + 1")  # the positive control: the raisers are live
```

  The `-k kernel` selector of Acceptance 3 matches both tests. The reference evaluates 64
  points by `subs` and `evalf`, deliberately slow and independent of the kernel's code path.
- [ ] **Step 2: Red.** An `ImportError` naming `compile_kernel`. Quote it.
- [ ] **Step 3: Implement.** `compile_kernel(text, *, parameters, limits=DERIVED_LIMITS)`:
  - `tree = parse_expression(text, GrammarProfile.OBJECTIVE, symbols=frozenset({"y", "f",
    "w", *parameters}), limits=limits)`.
  - Return a closure `kernel(y, f, w)` that evaluates `tree.body` recursively.
  - The node mapping:
    - `Constant` → `np.float64(value)`.
    - `Name` → `y`, `f`, `w`, or `np.float64(parameters[name])`.
    - `USub` → `np.negative`.
    - `BinOp` → `np.add`, `np.subtract`, `np.multiply`, `np.divide` and `np.power`.
    - `where(c, a, b)` → `np.where(cond, a, b)`, where `cond` is `np.less`, `np.less_equal`,
      `np.greater`, `np.greater_equal`, `np.equal` or `np.not_equal`.
    - `log` → `np.log`, `exp` → `np.exp`, `sqrt` → `np.sqrt`, `abs` → `np.abs`,
      `log1p` → `np.log1p`, `expm1` → `np.expm1`.
    - `min` and `max` → `np.minimum` and `np.maximum`, reduced over the arguments.
    - `clip(x, lo, hi)` → `np.minimum(np.maximum(x, lo), hi)`.
  - Evaluate inside `np.errstate(all="ignore")`. Non-finite values are the NaN abort's to
    report (Task 4), not NumPy warnings'. Every result is `np.broadcast_to(result,
    y.shape).astype(np.float64, copy=False)`, so a constant sub-expression has the input's
    length.
  - The closure holds the validated `ast` and the parameter floats. It never holds a string
    that is later evaluated.
- [ ] **Step 4: Green**, plus a mutation control: with `where` mapped to `a` alone, the
  agreement test fails. Quote both runs.
- [ ] **Step 5: Commit:** `feat(pricing-core): compile derived text to NumPy kernels through
  the objective grammar's tree (FR-144, FR-165, WK-690 S2)`.

### Task 4: `ObjectiveFns` for expressions, the per-round budget, and the NaN abort (both kinds)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/objectives.py`
  (`ObjectiveFns` at `:563`, `make_xgb_objective` at `:716`, `make_lgb_objective` at
  `:739`, `_finite_or_abort` at `:698-713`)
- Modify: `packages/pricing-core/src/pricing_core/modelling/errors.py` (`:62-73`, per
  DP-S2-4; the new budget error per DP-S2-3)
- Modify: `packages/pricing-core/src/pricing_core/modelling/expression_objective.py`
  (`compile_expression_objective`)
- Modify: `packages/pricing-core/tests/test_objectives.py` (append)
- Modify: `docs/specs/02-modelling.md`: §5.1 (the budget code "(declared, Phase 2)") and
  FR-165 (a dated note naming the budget's default and what it times, citing DP-S2-3's `RL-`)

**Interfaces:**
- Consumes: `derive`, `compile_kernel` and `Derived`.
- Produces:
  - `compile_expression_objective(*, ref: str, loss: str, parameters: Mapping[str, float],
    y_domain, hessian_strategy, hessian_min, derived: Derived | None = None) ->
    ObjectiveFns`. It uses DP-S2-1 (c)'s primitive arguments, with `y_domain`'s type as
    `ObjectiveFns`'s own field.
  - `make_xgb_objective(fns, *, round_budget_s: float = DEFAULT_ROUND_BUDGET_S)` and the
    same keyword on `make_lgb_objective`.
  - `DEFAULT_ROUND_BUDGET_S: Final = 30.0`, per DP-S2-3 (a); the ruling's value if it
    differs.
  - `RoundBudgetExceededError`, code `OBJECTIVE_ROUND_BUDGET_EXCEEDED`, per DP-S2-3.

- [ ] **Step 1: Generalise `ObjectiveFns` without changing the template path.** Give it
  three optional kernel fields (`loss_kernel`, `grad_kernel`, `hess_kernel`), used when
  `template is None`. `loss`, `grad` and `hess` dispatch on which is set. `stabilise`,
  `inverse_link` and every template field are unchanged. The expression's `inverse_link` is
  `exp` for a `log`-linked applicability. Slice 3 wires the link from the artifact's
  applicability; until then `compile_expression_objective` takes it as an argument. The
  template tests in `test_objectives.py` at `11c76b6c` pass unmodified, and that is this
  step's proof.
- [ ] **Step 2: Failing tests** (append to `test_objectives.py`):
  - `test_round_budget_aborts_a_slow_template`. Use a template `ObjectiveFns` whose `grad`
    is wrapped to sleep 0.05 s, and `make_xgb_objective(fns, round_budget_s=0.01)` on a
    4-row `DMatrix`. Expect `RoundBudgetExceededError`, with `round_index == 0` and the
    code in the text. Red at `11c76b6c`: `TypeError: unexpected keyword round_budget_s`.
  - `test_round_budget_aborts_a_slow_expression`. The same, for an expression
    `ObjectiveFns`.
  - `test_round_budget_positive_control`: the same objective with `round_budget_s=5.0`
    completes a round.
  - The same three for `make_lgb_objective`.
  - `test_nonfinite_aborts_an_expression_naming_the_round`: the loss `w * exp(exp(f))` at
    `f = 10` overflows. Expect `NonFiniteDerivativeError` with `round_index == 0`, carrying
    what DP-S2-4 rules. Under (b): the text names the round, the row count and the fields
    `y` and `f`, and contains no digit of the offending values. `err.y_range` and
    `err.f_range` hold them.
  - Under DP-S2-4 (b), the existing FR-165 template tests at `test_objectives.py:453`,
    `:471`, `:493` and `:517` that match the old range text are **updated by this commit**.
    The ruling is the licence, and the ledger lists each assertion changed, with its before
    and after. This is the one place an existing test is modified.
  Every test above carries `@pytest.mark.req("FR-165")`, and the budget tests also carry
  `@pytest.mark.req("NFR-483")`.
- [ ] **Step 3: Red.** Quote each red, by its cause.
- [ ] **Step 4: Implement.**
  - In each adapter, time the objective callable with `time.perf_counter()` around the
    `grad` and `hess` evaluation. If the elapsed time exceeds `round_budget_s`, raise
    `RoundBudgetExceededError(round_index=…, elapsed_s=…, budget_s=…)`. It is a
    `CodedError` whose text names the round, the budget and the elapsed time: numbers that
    are not inputs.
  - `_finite_or_abort` keeps its call sites and gains DP-S2-4's shape.
  - `compile_expression_objective` builds the three kernels from `loss` and from `derived`,
    or from `derive(loss, …)` when `derived` is `None`.
- [ ] **Step 5: The spec.** In `02` §5.1, beside `OBJECTIVE_NONFINITE_DERIVATIVE`, declare
  `OBJECTIVE_ROUND_BUDGET_EXCEEDED` "(declared, Phase 2)". Add FR-165's dated note:

  > *(Amended <date>, `RL-` of DP-S2-3: the per-round budget times the objective callable,
  > gradient and hessian, inside each backend adapter. The default is 30 s per round,
  > configurable per fit. Exceeding it raises `OBJECTIVE_ROUND_BUDGET_EXCEEDED`, naming the
  > round. It binds template and `expression` objectives alike.)*

  Use the ruling's values where they differ.
- [ ] **Step 6: Green**, with `test_objectives.py`'s template tests passing (apart from the
  DP-S2-4 assertions the ledger lists), `uv run mypy` and `uv run ruff check .`.
- [ ] **Step 7: Commit:** `feat(pricing-core): the per-round objective budget for both kinds,
  and expression ObjectiveFns (FR-165, WK-690 S2)`.

### Task 5: The expression certificate — the symbolic pair, found branches, the division rule

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/objectives.py`
  (`_derivative_checks` `:921`, `_branch_mask` `:907-918`, `_branch_check` `:1017`,
  `_finiteness_check` `:965`, `certify_objective` `:1309`, `library_versions` `:1331`)
- Modify: `packages/model-schema/src/model_schema/objectives.py` (`:51` `__all__`,
  `:612-622`, `:625`, `:751-763`) and `packages/model-schema/src/model_schema/__init__.py`
  (`:190`, `:388`, where `OBJECTIVE_CERTIFICATE_CHECKS` is re-exported, so the new constant
  is exported beside it)
- Modify: `docs/contracts/schemas/objective-certificate.schema.json` (`:6`, `:28-31`), then
  `uv run python scripts/generate-contracts.py`
- Modify: `packages/model-schema/tests/test_objectives.py` and
  `packages/pricing-core/tests/test_objectives.py` (append)
- Modify: `docs/specs/02-modelling.md` §4.7 (a dated note on the second battery and on found
  branches)

**Interfaces:**
- Consumes: `compile_expression_objective`, `Derived` and `to_sympy`.
- Produces:
  - `certify_expression_objective(*, ref, loss, parameters, derived, y_domain,
    hessian_strategy, hessian_min, inverse_link, sampling: SamplingSpec, progress=None) ->
    CertificateResult` (DP-S2-1 (c));
  - `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC` in `model-schema`.

- [ ] **Step 1: `model-schema`: two batteries, exactly one per certificate.** Add
  `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC`, the same nine names in the same order with the
  first two `symbolic_vs_numeric_gradient` and `symbolic_vs_numeric_hessian`. The battery
  validator accepts a result whose names equal either tuple exactly. Tests (`-k battery`):
  - the symbolic battery constructs;
  - the analytic battery still constructs (the positive control, unchanged);
  - a certificate mixing one of each pair is refused;
  - one short of nine is refused.
  Red: the symbolic case is refused at `11c76b6c` by `battery_is_exactly`. Mark each test
  FR-158 and FR-151.
- [ ] **Step 2: The contract** (`contract-schema`). Add the two symbolic names to the enum
  at `objective-certificate.schema.json:28-31`, keep `minItems: 9`, and extend the `$comment`
  (`:6`) with a dated line: the symbolic pair returns for the `expression` kind (FR-151). Run
  `uv run python scripts/generate-contracts.py`, then `--check`. If the contract guard in
  `backend/tests/test_contracts.py` compares this enum, it passes. If it does not compare
  it, record that in the ledger (`contract-guard`).
- [ ] **Step 3: Failing certificate tests** (append to `test_objectives.py`; the selector
  `expression_certificate`):
  - `test_expression_certificate_spec_example`: `certify_expression_objective` on §4.6's
    example, with the default sampling for its `y_domain`. Assert:
    - the nine names in the symbolic order;
    - `overall == certified_with_findings`;
    - `convexity` is `violated` and `branch_discontinuity` is `warn`;
    - the gradient detail's excluded count is greater than 0 (FR-147);
    - `library_versions["sympy"] == sympy.__version__`.
    Mark it FR-146, FR-147, FR-148 and FR-151.
  - `test_expression_certificate_smooth_loss`: `w * (exp(f) - y * f)`. Assert
    `branch_discontinuity` is `pass` with "no branch boundary", and both symbolic checks are
    `pass` (FR-149).
  - `test_expression_certificate_catches_a_wrong_derivative`: `derived` is supplied with a
    hessian off by a factor of 1.01. Assert `symbolic_vs_numeric_hessian` is `failed`. This
    is the check on broken input.
  - `test_expression_certificate_division` (the selector `division`): loss `w * (y - f) ** 2
    / f`, whose `f` range crosses 0, gives `finiteness` `failed`, naming the denominator. The
    control `w * (y - f) ** 2 / (1 + f ** 2)` certifies (DP-S2-5).
  - `test_template_certificate_unchanged`: a template certificate at `11c76b6c`'s default
    sampling is equal, check by check, to its value before this task. The ledger records the
    comparison's source.
- [ ] **Step 4: Red.** Quote each red, by cause.
- [ ] **Step 5: Implement.**
  - `_derivative_checks` takes a `names` pair and a reference `(grad, hess)`. The template
    path passes the analytic pair and the template's functions. The expression path passes
    the symbolic pair and the compiled derived kernels. `_richardson`, `_agreement` and
    `_status_for` are unchanged (FR-149).
  - **Found branches (FR-147, FR-148) for expressions.** Collect every `Piecewise` condition
    in the loss and the derived text, walking the validated `ast` of each.
    - A sampled point is *near a boundary* when any condition's truth value differs between
      `f - 1.5·_STEP` and `f + 1.5·_STEP`. That is the template mask's width
      (`objectives.py:907-918`), found rather than declared.
    - `_branch_check` reports `warn` with the found share and the boundary text, or `pass`
      with "no branch boundary to exclude near" when no condition exists.
    - The same finding covers the kinks of `abs`, `min`, `max` and `clip` under DP-S2-2 (a),
      because their derived text is `where`.
  - **The division rule (DP-S2-5 (a)).** Collect every `Div` right operand in the loss and
    the derived text, compile each with `compile_kernel`, and evaluate it on the grid. Any
    exact zero, or any sign change along a sampled `y`'s ordered `f` values, makes
    `finiteness` `failed` with the denominator's text.
  - `certify_expression_objective` builds the grid with `_grid` (`objectives.py:798`) and
    runs the same battery order. It sets `library_versions["sympy"] = sympy.__version__` at
    the call, beside `numpy` and `xgboost`.
  - `certify_objective`, the template entry point, is unchanged in signature and in output.
- [ ] **Step 6: The spec** (`spec-change`). Add a dated note in `02` §4.7:

  > *(Amended <date>, WK-690 Slice 2: an `expression` certificate carries the nine checks
  > with the `symbolic_vs_numeric` pair, and `model-schema` accepts exactly one of the two
  > batteries. For an expression, branch boundaries are found from its `where()`
  > conditions, not declared (FR-147, FR-148). A denominator that is zero, or that changes
  > sign, over the sampled domain fails `finiteness` (§4.6; the `RL-` of DP-S2-5).
  > `library_versions.sympy` is read from `sympy.__version__` (`RL-1289`).)*

- [ ] **Step 7: Green**, plus two mutation controls:
  - with the found-branch mask disabled, the spec-example test's excluded-count assertion
    fails;
  - with the sign-change test disabled, the division case certifies and so fails.
  Run `generate-contracts.py --check` and `uv run mypy`.
- [ ] **Step 8: Commit:** `feat(pricing-core,model-schema): the expression certificate, the
  symbolic battery, found branches and the division rule (FR-146–FR-151, WK-690 S2)`.

### Task 6: NFR-476's expression limb, measured in a solo window

**Files:**
- Modify: `scripts/bench-model.py` (a new limb beside `:93` and `:369-385`)
- Modify: the slice ledger

- [ ] **Step 1: Add the limb.** Fit the same data twice at DP-S2-6's shape: once with the
  builtin `count:poisson` (`scripts/bench-model.py:246`), and once with the expression
  `w * (exp(f) - y * f)`, compiled by `compile_expression_objective`. That expression is the
  same Poisson deviance up to a constant in `f`. Report both wall-clocks and their ratio.
  Assert nothing in the script: the verdict is the ledger's.
- [ ] **Step 2: Solo window.** Ask the lead for the window (`RL-1263` item 3). Record the
  grant time from the dispatch record.
- [ ] **Step 3: Measure.** Run N ≥ 3 paired runs, under the slot wrapper with the slot rule's
  thread caps. Record for each run: both times, the ratio and the one-minute load average
  at start and end. Report the median ratio and the spread.
- [ ] **Step 4: The verdict**, against 1.25:
  - met at the declared shape, or not met;
  - under DP-S2-6 (a), the full-shape run is named with its owner (the dedicated host), not
    claimed.
- [ ] **Step 5: Commit:** `perf(bench): NFR-476's expression-objective limb (WK-690 S2)`.

### Task 7: The gate and the ledger

- [ ] Run the full two-half gate on the committed tree (`CLAUDE.md` §11), with slotted and
  capped suite runs. Quote every rc, and pytest's `N passed` against Task 0's.
- [ ] Run `python3 scripts/doc-index.py`, `--check`, and `uv run python
  scripts/req-coverage.py`. Quote the lines for FR-144, FR-146, FR-147, FR-148, FR-149,
  FR-151, FR-165, NFR-476 and NFR-483. Slice 3 still owns FR-144's storage clause and
  FR-146's persistence and approval, and the ledger says so, so a count is not read as whole
  coverage (`CLAUDE.md` §13).
- [ ] The ledger records:
  - the dispatch record (Task 0);
  - the `RS-` (Task 1);
  - each red-then-green quote and each mutation control;
  - the DP-S2-4 test changes, before and after;
  - the contract-guard result;
  - NFR-476's runs and verdict;
  - the deviations from this plan, each named.

## Hand-off

Slice 3 (`SL-1273`) consumes all of this:
- `derive`, whose `Derived` it stamps with `derived_at` and stores;
- `compile_expression_objective`, from the artifact's `loss`, `parameters` and `derived`;
- `certify_expression_objective`, behind the certify job;
- the budget and non-finite errors, which it registers in `backend/src/app/errors.py`.
It also adds `CustomObjective`'s expression fields (premise e), after which DP-S2-1 (c)'s
primitive calls read those fields.

## Self-review

1. **Spec coverage.** Every row of the coverage table names a task:
   - FR-144: Tasks 2 and 3.
   - FR-146 to FR-151: Task 5.
   - FR-165: Tasks 3 and 4.
   - NFR-476: Task 6.
   - NFR-483's third clause: Tasks 3 and 4.
   - The §4.7 expression half: Task 5.
   `RL-1289`'s second violation is Acceptance 2, in Task 2.
2. **Premises carry file and line.** Premise l's counts carry the command and the tree.
   Premise i's facts carry the spike and the pinned version.
3. **Rulings at every site** ([`README.md`](README.md) convention 5).
   - `RL-1289`: Global Constraints, Task 2 and Acceptance 2.
   - `RL-1291`: Task 1's predicate and `DERIVED_LIMITS`.
   - `RL-1293`: Global Constraints and Task 2's `f` symbol.
   - `RL-1263`: Status (contention and the solo window), Task 6 and Acceptance 10.
   - `RL-1265`: the narrative and Task 4.
4. **Deviations named rather than folded in.** This slice touches `model-schema` and a
   hand-authored contract, and the map plan said "All in `pricing-core`" (premise d). It may
   change the FR-165 template tests, but only under DP-S2-4's ruling (Task 4 Step 2).
5. **Type consistency.** These names match across Tasks 2–5 and the Hand-off: `Derived`,
   `derive`, `to_grammar`, `DERIVED_LIMITS`, `compile_kernel`, `Kernel`,
   `compile_expression_objective`, `DEFAULT_ROUND_BUDGET_S`, `RoundBudgetExceededError`,
   `certify_expression_objective` and `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC`.
6. **Placeholders.** Two values stand until their rulings, each named with its ruling: the
   `<date>` in the Task 4 and Task 5 notes (the commit's date) and `DERIVED_LIMITS`'
   numbers (DP-S2-2, reading DP-S2-7). Nothing else is left open.
