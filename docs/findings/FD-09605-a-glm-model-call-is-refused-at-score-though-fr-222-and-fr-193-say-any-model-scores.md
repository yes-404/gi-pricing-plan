---
id: FD-9605
family: finding
title: A GLM model_call is refused at score, though FR-222 and FR-193 say any persisted Model scores
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: cdaaa57345cb765f96034ce1ec2733c338f1c3cd
corrected_by: []
relates: [WK-1178, WK-673, FR-193, FR-222, FR-223, FR-243]
---

# FD-9605 — a `model_call` that pins a GLM is refused at score (`runtime.py:568-579`)

**Filed** by auditor-glm on the lead's order of 2026-10-05, working id 9605 (reserved in the lead's
`eta.md`), from the maintainer's (by delegation) approval in the entry after 15:48 BST in `to-lead.md` (a
local channel file, so cited by its description, "model_call refusal"; **I could not find that entry's
text in the channel file at 15:49 BST, so its header is not quoted here and the lead supplies it before the
ACK**). The evidence is the sizing memo `~/gi-pricing-plan.local/handover/sizing-g2-peril-path-2026-10-05.md`
§F5, **every fact of which was re-read below, not trusted**. `tree:` is `origin/main` at filing; every
read ran at that tree.

## Finding

**Severity: proposed MEDIUM at least; higher if Option A (the literal Peril Structure path in P2) is
chosen; ruled by the maintainer (by delegation) at the mint.** **Owner: proposed WK-1178; ruled by the
maintainer (by delegation) at the mint** (reasons below).

A Rating Version whose `model_call` step pins a **GLM** compiles, then **refuses every quote**. The
branch is `_model_call_handler`'s `else:` (`packages/pricing-core/src/pricing_core/rating/runtime.py:568-579`,
after the `if model_type in ("xgboost", "lightgbm"):` branch at `:549`). It returns `_model_call_failure(...)`
(`:94`), which reports through the handler's returned `output` (the sentinel, `MODEL_CALL_ERROR_KEY`) and
surfaces as `MODEL_CALL_FAILED`. The reason it gives, verbatim joined:

> model_call step '…' pins a 'glm' model. Bundle.resolved_payloads carries the Model's own dump but not the
> Factor/Banding/Grouping objects predict_glm requires (ModelSpecCommon.factors is bare UUIDs —
> resolve_factors builds zero design columns from an empty sequence, so every non-intercept coefficient's
> term goes unresolved). Scoring a GBM works because predict_gbm has a documented fallback for factors=()
> that reads each feature off the frame directly; predict_glm has no such fallback.

**The contradiction (spec versus code, with no record).**

- `03` FR-222 (`docs/specs/03-rating-engine.md:108`): *"`model_call` steps declare `mode`: `exact` invokes the
  model itself; `approximation` uses the model's GLM approximation relativity tables (`02` OQ-575)."* No
  carve-out for a GLM in `exact` mode.
- `02` FR-193 (`docs/specs/02-modelling.md:304`): *"`pricing-core` can score any persisted Model from its
  declarative artifact alone (ADR-705), with no dependency on the fitting session. GLM scoring requires no
  `glum`; GBM scoring loads the JSON booster."*

`exact` mode over a GLM is therefore specified and **cannot run**; only the GBM half of FR-193 is built into
the rating runtime.

## Why it matters

1. **A Rating Version that pins a GLM through `model_call` is accepted at save and compile, and fails at
   score.** `compile_bundle` has no check that a pinned `model_call` model is scorable (FD-1297's remedy
   adds pin-membership, not scorability). The failure is loud (a coded refusal, never a silent price), so
   this is a capability gap, not a mispricing.
2. **It blocks WF-699's literal path.** WF-699 B4 (`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:59`)
   adds a `model_call` that references the Peril Structure, whose components are GLMs on the demo's data
   (`examples/fremtpl2/model.py` fits a frequency GLM and a frequency GBM). That is why the sizing memo
   prices this as slice A-2 of Option A, and why the severity rises if Option A is chosen.
3. **The refusal is pinned by tests, so a fix must change them deliberately:**
   `packages/pricing-core/tests/test_rating_runtime.py:377` (`test_a_glm_model_call_is_refused_with_a_named_code`)
   and `packages/pricing-core/tests/test_rating_score.py:429`.

## Evidence

**1. The refusal text and its reason** — read at `cdaaa573`: `runtime.py:568-579` as quoted; `_model_call_failure`
at `:94` (its docstring records the zen binding swallowing a raised exception, hence the sentinel).

**2. Its origin.** `git log -S"predict_glm has no such fallback" --format='%h %aI %s'` over `origin/main`
prints one commit: `24b537df 2026-08-29T21:19:55+01:00 feat(rating): CompiledBundle, load_bundle and the JDM wire
translation (W11 Task 1.3) (#406)`. **This is the sizing memo's claim, confirmed.** (The memo also names #415, W11 Task
1.4, for the same lines by `git blame`; I did not check that, and the `-S` result needs only #406.) So the
refusal is an implementation gap recorded in a comment, not a ruling: the text says "the Bundle carries
X but not Y", never "a GLM must not be scored this way".

**3. Why it refuses (mechanism).** `load_bundle` (`runtime.py:646`) builds the handler from
`bundle.resolved_payloads` only and states "every pinned artifact's content already travels *inside*
`bundle` (RL-873)", with `_load_boosters` the only per-model preparation. `predict_glm`
(`packages/pricing-core/src/pricing_core/modelling/predict.py:230`) has the signature
`predict_glm(fit, data, factors: Sequence[Factor], spec: GlmSpec, *, model_offset=None, bandings=None,
groupings=None)`. The payload holds the model's `fit_result`; the `Factor`, `Banding` and `Grouping` objects
are separate artifacts a `Bundle` does not carry (`ModelSpecCommon.factors` is bare UUIDs). `predict_gbm`
tolerates `factors=()` and the handler calls it that way (`:563-566`, `factors=()`). This **confirms the memo's
mechanism**, with one limit: I read the signature and the bundle's construction, and did not run either.

**4. No record names it.** `git grep -n -i 'model_call' origin/main -- docs/findings docs/rulings` matches
only FD-935 (the timing example), FD-1297 (the pin-membership refusal) and FD-1374 (the `feature_map` input rule); none
concerns a GLM refusal. `grep -n -i 'model_call' docs/findings/register.md` matches four rows (:59 F-W9-1, :71 F29, :103 F62, :219
FD-1297), none about a GLM refusal. The only mention outside `docs/` is the lead's channel
(`to-lead.md:17795`, read: "DP-a0: do NOT adopt S3's model_call fixture (a GLM cannot be scored via model_call
on main). AGREED.") — a decision to avoid it, not a record of it.

## Owner (proposed)

`runtime.py` and `compile.py` were built under **WK-669** (the bundle) and **WK-671** (scoring), both
**closed** (`docs/roadmap.md:620`, `:650`). A defect in closed Work's code goes to the standing item
for work that "belongs to no other Work" (**WK-1178**, `docs/roadmap.md:1284`; its `SL-1300` fixes `compile_bundle`
at the same seam). **If Option A is chosen, the fix is also a WK-673 exit-demo dependency; the owner then
stays WK-1178 and the slice is cited from the exit-demo plan.** *Proposed: WK-1178; ruled by the maintainer
(by delegation) at the mint.*

## Disposition

Open. Filed by the auditor, 2026-10-05. Severity and owner above are proposals.

**Remedy, proposed (the maintainer chooses; two ways to close the contradiction):**

- **(a) Build it.** Compile embeds each pinned GLM's `Factor`, `Banding` and `Grouping` versions in
  `Bundle.resolved_payloads`; the runtime rebuilds them and calls `predict_glm`. Red first: a golden test
  that the `model_call` value equals `predict_glm` on the same row; `test_rating_runtime.py:377` flips.
  The sizing memo cuts this as one slice ("A-2", likely 1 executor-day), and it can reuse PL 9649's
  `factor` resolver branch only after that plan merges.
- **(b) Narrow the spec.** `03` FR-222 and `02` FR-193 gain a dated amendment saying `exact` scores a GBM
  only, and a Rating Version that pins a GLM through `model_call` is refused **at save**, not at score, with a
  named code. That makes the refusal a requirement rather than a gap.

Event that next confirms or discharges it: the maintainer's severity and owner at the mint, then a merged
fix under (a) or (b); the discharge test is `test_a_glm_model_call_is_refused_with_a_named_code` flipped
(a) or a save-time refusal test (b).
