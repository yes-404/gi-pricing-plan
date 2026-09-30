---
id: RL-9961
family: ruling
title: WK-690 Slice 2's DP-S2-1 to DP-S2-6 decided — primitive inputs, derived text rewritten into the grammar, a 30 s round budget, a value-free NaN abort, a numeric division rule, and NFR-476 at a declared shape
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 11c76b6c83647c512796fedb9c0143927dcd78cb
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1268, SL-1272, RL-1289, RL-1291, RL-1293, FD-1219, WF-702]
---

# RL-9961 — WK-690 Slice 2's DP-S2-1 to DP-S2-6 decided

## How this was ruled

- **Effort and routing.** Ruled at effort `medium`, on the lead's routing of 2026-09-30. The
  session's `$CLAUDE_EFFORT` read `medium`.
- **Working id 9961.** Assigned by the lead. It is minted at the merge turn.
- **The decision points.** They are those of WK-690 Slice 2's leaf plan (SL-1272, PL working
  id 9946), read **only** at the planner's local commit
  `7cd40ad72b31eeb3160e6d27a33024be5da6d97d` (worktree `planner-690-s2`, not pushed), via
  `git -C <path> show 7cd40ad7:<plan>`. Its DP table is at `:332-338`.
  - auditor-plans2 found the plan CLEAN at `7cd40ad7`, on condition that #969's plan (PL working id 9833) mints in
    batch 4.
  - DP-S2-7 is a fact for the executor's spike (`RS-`), not a ruling.
- **One record for six points.** They belong to one slice's plan, and each is small. Each
  point below is ruled separately and carries its own acceptance.
- **Every premise below was re-read at `11c76b6c`.** None was taken from the plan's text.
  `git diff --stat 11c76b6c e3600789 -- packages backend/src docs/specs/02-modelling.md
  docs/workflows scripts/bench-model.py` prints nothing, so each premise also holds at `main`
  `e3600789`.

## Verified first, at 11c76b6c83647c512796fedb9c0143927dcd78cb

| Premise | Where | Present? | What the source says |
|---|---|---|---|
| FR-165's three limbs | `docs/specs/02-modelling.md`, FR-165 | present | "evaluated on fixed-size NumPy arrays …; wall-clock is budgeted per boosting round, and NaN/inf … aborts the fit with a named error identifying the round and the offending input range" |
| NFR-483's budget clause | `02` NFR-483 | present | "compiled objectives cannot allocate unbounded memory or exceed their per-round time budget (FR-165)" |
| NFR-476's expression limb | `02` NFR-476 | present | "5 M rows × 60 factors × 500 trees fits in < 20 min; a custom `expression` objective adds no more than 25 % overhead versus the equivalent builtin" |
| The nine checks | `02` FR-158; `packages/model-schema/src/model_schema/objectives.py:612-622` | present | `OBJECTIVE_CERTIFICATE_CHECKS` holds exactly nine, including `finiteness` and `branch_discontinuity` |
| Branch points are excluded, then reported | `02` FR-147, FR-148 | present | Points within `h` of a `Piecewise` boundary are excluded, and the boundaries are a reported finding |
| No expression fields on the artifact | `model_schema/objectives.py:438-500` (`CustomObjective`, `_only_templates_are_built`) | **absent** | Adding them is Slice 3's (`PL-1268`) |
| The existing domain and strategy types | `model_schema/objectives.py:120` (`HessianStrategy`), `:226` (`YDomain`) | present | Both already exist in `model-schema` |
| The NaN abort carries values | `packages/pricing-core/src/pricing_core/modelling/objectives.py:698-713`; `modelling/errors.py:62-73` | present | "The offending inputs span y ∈ [...], f ∈ [...]". `NonFiniteDerivativeError(ObjectiveError)` is a `ModellingError` (a `RuntimeError`), code `OBJECTIVE_NONFINITE_DERIVATIVE`, and not a `CodedError` |
| The NaN text is persisted today | the path from `_finite_or_abort` (`objectives.py:732`, `:768`, inside `xgb.train`/`lgb.train`) to the job | **absent (latent)** | `gbm.py:590` wraps only `compile_objective`. The fit site catches only `EbmFitError`, `GbmFitError` and `GlmFitError` (`backend/src/app/worker/model_handlers.py:392-399`). The error reaches `worker/tasks.py`'s generic clause, whose `safe_job_error_text` (`platform/safe_exception.py:30-47`) reduces a non-`CodedError` to its type |
| FD-1219's sinks | `docs/findings/FD-01219-…md:38-55` | present | "the stored `JobError.message`, and the process log" |
| C5's words | `docs/workflows/WF-00702-custom-objective-lifecycle.md:137` | present | The fit aborts "with `OBJECTIVE_NONFINITE_DERIVATIVE`, naming the round and the offending input range" |
| No per-round budget, no budget code | `objectives.py:1248`, `:1280`; `02` §5.1 | **absent** | Only the smoke fit's elapsed detail exists |
| The builtin benchmark only | `scripts/bench-model.py:93`, `:246` | present | `"NFR-476 gbm fit, 500 trees"` on `count:poisson`. No expression limb |
| The dedicated host | `docs/closures/CR-01247-…md:308-335` (Proposal 4) | **absent** | It is maintainer-owned, and "No repository record names a host". A shared-VM run "claims no verdict near a bound" (`RL-921` §4) |
| SymPy 1.14.0's derivative heads | spike, below | present | Every `min`, `max` and `clip` hessian carries `DiracDelta`. `Heaviside` appears too whenever the argument is nonlinear in `f` (for example `exp(f)`), and always for `clip`. `min(f, y)` and `max(f, y)` carry `DiracDelta` only. `d²\|x\|/dx²` = `2*DiracDelta(x)`; `Heaviside(0)` = `1/2` *(corrected 2026-09-30 on auditor-plans2's F3; see the spike)* |

**Spike** (scratch `vocab.py`, then `vocab3.py`, sha256 prefix `46de41d2cdcf4fe5`;
sympy 1.14.0 in the scratch venv of `RL-1289`; `real=True` symbols as `RL-1293` rules).
- `vocab.py` printed `min hess heads: ['DiracDelta', 'Heaviside']`, with `max …` and
  `clip …` the same, `Heaviside(0) = 1/2` and `d2|x|: 2*DiracDelta(x)`.
- Its arguments held `exp(f)`. The first form of this record generalised from that, and
  auditor-plans2's F3 found `['DiracDelta']` only for `min` and `max`.
- **Both are right, and the argument decides.** `vocab3.py` printed:
  - `min(f,y)` hess `['DiracDelta']` (`-w*DiracDelta(f - y)`), and `max(f,y)` the same;
  - `min(exp f,y)` and `max(exp f,y)` hess `['DiracDelta', 'Heaviside']`;
  - `clip(f,a,b)` and `clip(exp f,a,b)` hess `['DiracDelta', 'Heaviside']`.
- The rewrites in DP-S2-2 cover every head in every form, so the ruling is unchanged.

## Ruled

**DP-S2-1 — (c), primitive arguments, with the existing types.** Before Slice 3, the
expression path takes:
- `loss: str`;
- `parameters: Mapping[str, float]`;
- `y_domain: model_schema.YDomain`;
- `hessian_strategy: model_schema.HessianStrategy`;
- `hessian_min: float`;
- `ref: str`.

**"Primitive" means no new shape, not re-typed fields.** The domain and the strategy are the
`model-schema` types that already exist (`:120`, `:226`), never a tuple or a string copy of
them. That is `CLAUDE.md` §2's rule: nobody hand-writes a shape that already exists. Slice 3
passes the artifact's fields.
- (a) would be a second definition of a shape `model-schema` will own.
- (b) moves Slice 3's contract work into this slice.

**DP-S2-2 — (a), the printer rewrites into the objective grammar.**
- The rewrites:
  - `sign(x)` → `where(x > 0, 1, where(x < 0, -1, 0))`;
  - `Heaviside(x)` → `where(x > 0, 1, 0)`;
  - `DiracDelta(·)` → `0`, the almost-everywhere derivative.
- The kink is reported by FR-148 as a found branch boundary. The certificate's
  `branch_discontinuity` names every point where a `DiracDelta` was dropped.
- Derived text is parsed in the `objective` profile under `DERIVED_LIMITS`, from DP-S2-7's
  spike (or its stated default).
- **Why:** one grammar and one parser (`02` §4.6). The rewrites differ from SymPy only on
  measure-zero sets, `Heaviside(0) = 1/2` against `0`. FR-147 already excludes points within
  `h` of those sets from the agreement check.
- (b) adds a fifth profile, a §4.6 amendment, for text a reviewer then has to learn to read.
- (c) would refuse every objective using `abs`, `min`, `max` or `clip`.
- **Condition:** the dropped `DiracDelta` must be visible, never silent. It is visible
  through `branch_discontinuity`, as above. A hessian that is identically `0` on an open set,
  for example the L1-type `w*abs(y - exp(f))`, is not negative, so FR-152's `convexity` does
  not flag it. The declared `hessian_strategy` (`clip_to_min` raises it to `hessian_min`)
  keeps boosting well-posed, and the certificate's `branch_discontinuity` detail names the
  dropped delta's location.

**DP-S2-3 — (a), 30 s per round, on the objective callable, coded.**
- **What is timed:** the objective callable's own wall-clock (the gradient and hessian
  evaluation) inside `make_*_objective`. That is the code an author controls, and what
  NFR-483 names.
- **Default and override:** 30 s per round, with a keyword on both adapters.
- **What it raises:** a new `OBJECTIVE_ROUND_BUDGET_EXCEEDED`, a `CodedError` whose text
  names the round and the budget, and no data value. It is declared spec first in `02` §5.1,
  "(declared, Phase 2)", and registered in the backend in Slice 3.
- **Why:** it is a runaway guard. The builtin's NFR-476 budget is 20 min for 500 rounds, about
  2.4 s a round at the full shape, so 30 s is more than ten times that. A rate derived from
  NFR-476 (b) would turn a slow shared machine into a fit failure.
- **Why not (c):** "the caller must pass one" would leave the guard off wherever a caller
  forgets.

**DP-S2-4 — (b), value-free coded text; the ranges only as structured detail.**
- `NonFiniteDerivativeError` also becomes a `CodedError` (a mixin next to `ObjectiveError`;
  the MRO `(…, RuntimeError, CodedError, ValueError)` builds, checked). It keeps the code
  `OBJECTIVE_NONFINITE_DERIVATIVE` that C5 names.
- Its text names the round, the non-finite row count and the fields (`y`, `f`), with **no
  values**.
- The numeric ranges are structured attributes on the exception: `round_index`, `rows`,
  `y_range` and `f_range`.
- **The condition that makes (b) meet FD-1219:**
  - The ranges reach **only** the stored job record's structured `detail`. **That mechanism
    does not exist yet, and Slice 3 builds it** *(corrected 2026-09-30 on auditor-plans2's
    F1)*. At `11c76b6c`:
    - `PlatformError` (`backend/src/app/errors.py:393-412`) carries `code`, `title`,
      `status_code`, a **text** `detail` and `errors`. It has no structured extras.
    - The worker's `PlatformError` clause (`backend/src/app/worker/tasks.py:222-232`) sets
      `JobError.message = exc.detail or exc.title`, and never `JobError.detail`.
    - `JobError.detail` is already a contract field, `dict[str, Any]`
      (`packages/model-schema/src/model_schema/jobs.py:181`).
    - The precedent for filling it is the same file's `JobBudgetExceededError` clause
      (`:184-194`), which sets `detail={"wall_clock_s": …, "elapsed_s": …}`.
  - **Ruled: extend, rather than fall back to persisting no ranges.** The fallback would leave
    C5's "naming … the offending input range" unmet in the only record an author can read
    after the fit. The extension changes no contract, because `JobError.detail` already
    exists.
    - `PlatformError` gains an optional keyword-only `job_detail: Mapping[str, Any]`.
    - The worker's `PlatformError` clause passes it through as `JobError.detail`.
    - The fit site maps `NonFiniteDerivativeError` to
      `PlatformError(code, "…could not be fitted", 409, <the value-free text>,
      job_detail={"round_index": …, "rows": …, "y_range": […], "f_range": […]})`.
  - They never reach `JobError.message`, a log call's text, or log `extra`. Those are
    FD-1219's two sinks (the stored message and the process log).
- **Latent, not live.** Today the error is reduced to its type before it is stored (the table
  above). Once it becomes a `CodedError`, its text **is** persisted. That is why the text
  must carry no value.
- **The rule covers templates too.** `_finite_or_abort` is shared.
- (a) persists nothing useful: the reduction strips the whole message.
- (c) is wrong about FD-1219: min and max of `y` are dataset values.

**DP-S2-5 — (a), numeric on the certificate's grid, with bounded refinement.**
- **The test:** every denominator in the loss and in the derived text is evaluated on the
  certificate's own grid. Any of these is `failed` under the existing `finiteness` check,
  naming the denominator's text:
  - a zero;
  - a sign change along any sampled `y`'s `f`-sweep (by continuity, a zero lies between);
  - an interior local minimum of `|d|` along a sweep that a bounded bisection or
    golden-section refinement drives below the grid's zero tolerance. The refinement is at
    most 40 steps per minimum.
- **Why the added clause:** a sign-change test cannot see an even-order zero, such as
  `(exp(f) - y)**2` in a denominator. A grid step can straddle it without any sign change.
  The refinement catches it within a fixed bound.
- (b) `sympy.solve` has no time bound and is incomplete for transcendental denominators.
- (c) would break FR-158's nine checks.

**DP-S2-6 — (a), a declared reduced shape here; the full shape on the dedicated host.**
- **The shape:** 1 M rows × 60 factors × 100 trees. N ≥ 3 paired runs, builtin against
  expression on the same data, in a solo window. Each run takes a gate slot, under the
  11:42:08 and 11:43:28 rules, with their thread caps. The ratio is the verdict.
- **The near-bound condition:** a ratio within ±5 percentage points of 25 % on the shared VM
  claims no verdict. It is recorded as "measured, near bound", following `RL-921` §4 and
  CR-1247 Proposal 4's "claims no verdict near a bound".
- **The full shape is carried forward:** 5 M × 60 × 500, N ≥ 3, on the dedicated host. The
  **run** is owned by WK-690, and the **host** by the maintainer, who has not named one
  (CR-1247 Proposal 4). WK-690's close records it under a §13 verdict, not as silence.
- (b) holds the solo window for over two hours.
- (c) leaves the limb unmeasured, as CR-1212 found it.

**Departures from the recommendations.** None: (c), (a), (a), (b), (a), (a) as recommended.
Each carries a condition the recommendation left implicit:
- DP-S2-1: the existing types;
- DP-S2-2: the dropped delta made visible;
- DP-S2-4: the ranges only in structured detail;
- DP-S2-5: the even-order refinement;
- DP-S2-6: the near-bound rule and the owner split.

**Narrowness.** One code, `OBJECTIVE_ROUND_BUDGET_EXCEEDED`, is added to `02` §5.1, spec
first, inside this slice's own scope. Nothing else changes FR text or a contract.

## What it obliges

WK-690 Slice 2, per the plan's tasks:
- **Tasks 2 to 5:** DP-S2-1.
- **Task 2 (printer) and Task 3 (limits):** DP-S2-2.
- **Task 5 (the certificate):** DP-S2-2's condition. `branch_discontinuity` names every
  dropped `DiracDelta`'s location, as a found boundary *(routed here 2026-09-30 on
  auditor-plans2's F2)*.
- **Task 4:** DP-S2-3 and DP-S2-4, with the `02` §5.1 declaration.
- **Task 5:** DP-S2-5.
- **Task 6:** DP-S2-6.

**Slice 3:**
- the backend registration of `OBJECTIVE_ROUND_BUDGET_EXCEEDED`;
- **DP-S2-4's persistence path.** `PlatformError`'s `job_detail` keyword, the worker clause
  that sets `JobError.detail` from it, and the fit-site mapping of `NonFiniteDerivativeError`.
  Red first: a NaN-producing objective's failed fit job carries `round_index`, `rows`,
  `y_range` and `f_range` in `JobError.detail`. No planted `y` or `f` value appears in
  `JobError.message` or in any log record the worker emits for that job, captured by
  `caplog` over the job run.

This record edits no spec, plan or roadmap text.

## Acceptance — the violation that must become detectable

Each is shown red first in the slice's suite.
- *DP-S2-1: an expression-path signature takes a hand-written domain or strategy shape.*
  A structural test asserts the annotations are `YDomain` and `HessianStrategy`.
- *DP-S2-2: derived text contains `sign`, `Heaviside` or `DiracDelta`, or fails to parse in
  the `objective` profile.* The fixtures are `abs`, `min`, `max` and `clip` losses.
- *DP-S2-2: a dropped delta is not reported by `branch_discontinuity`.*
- *DP-S2-3: an objective sleeping beyond the budget in one round is not refused with
  `OBJECTIVE_ROUND_BUDGET_EXCEEDED`.*
- *DP-S2-4: `str(NonFiniteDerivativeError(...))` contains any digit drawn from the planted
  `y` or `f` values.*
- *DP-S2-4: the ranges are absent from the exception's attributes.*
- *DP-S2-5: a loss with denominator `(exp(f) - y)**2` passes `finiteness` on the default
  grid.* This is the even-order case.
- *DP-S2-6: the ledger records an NFR-476 verdict from a run near the bound, or with fewer
  than three paired runs.*
