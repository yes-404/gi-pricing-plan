---
id: LG-9455
family: ledger
title: WK-1178 slice SL-1466 — Option A, A-3, Peril Structure scoring (PL-1465), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: e0e12dd834318294a5e0932618ca177c71a7bf46
phase: P2
work: WK-1178
slice: SL-1466
plans: [PL-1465]
corrected_by: []
relates: [PL-1465, PL-1471, RL-1459, RL-1523, RL-1263, FR-188, FR-189, FR-191, FR-193, FR-222, FR-237, FR-239, FR-240, FR-20, NFR-491, WK-1178]
---

# LG-9455 — WK-1178 slice SL-1466: Option A, A-3, Peril Structure scoring

**GO:** not yet given. Authoring ahead of the GO at the user's order (`to-lead.md`, a local file: "2026-10-10 03:07:11 BST — W3 (new week) pacing …", item 1): code and tests are written on a branch from A-2's pushed head `e0e12dd834318294a5e0932618ca177c71a7bf46`; only small tests run (one file, no database), after the lead's "small tests RESUME"; nothing merges before the GO, the full gate and the MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `SL-1466` in `docs/roadmap.md` (WK-1178, Option A, A-3). Its scope is `PL-1465` §"Scope" and §"Write set, and its contention", read at this branch's tree. Ruling records: `RL-1459` (DP-A3-1 to DP-A3-7) and `RL-1523` (the per-component completeness limb, which is not built here).

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1465`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1466`'s roadmap row at its head.

Write set: `PL-1465` §"Write set" only. Any other path is a stop to the lead.

**Serial after A-2.** This branch is cut from A-2's head, which carries S4's old base, A-1 and A-2. The resolver is `WorkspaceResolver`, re-anchored by symbol.

### Task list

Order and acceptance checks are `PL-1465` §"Tasks" and §"Acceptance Standard". Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run during the authoring phase; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Task 0 — preconditions, read 2026-10-10 (BST) at this branch's base `e0e12dd8`; `origin/main` is `3519a919e30aa6993d40b22df212dd57bbd4a685`

**Readiness table** (the plan's activation needs, each read in the primary source):

| Need | Status | Evidence |
|---|---|---|
| 1. PL-1429 merged | MET (on this base) | `rating_versions.py` is the file PL-1429 edits; the create route is not exercised in Task 0, so Task 5 re-checks `_PIN_TYPES` by symbol |
| 2. PL 9649 merged (now PL-1471 / SL-1472, #1247 @`7e3a4803`) | MET | `compile.py` carries `_refuse_unapproved_objectives`, `_refuse_control_factor_keys`, `_refuse_control_factor_model_calls`, and `ResolvedArtifact.factors` |
| 3. A-1 merged (SL-1462) | NOT on `origin/main`; carried on this base | `WorkspaceResolver.resolve` has the `peril_structure` branch (`rating_versions.py:645`); `_require_approved_components` is at `platform/perils.py:708`. Gates the MERGE only |
| 4. A-2 merged (SL-1463) | NOT on `origin/main`; carried on this base | `_model_call_handler` has the GLM branch and `_GlmScorer`; `required_model_inputs` is in `modelling/factors.py:338`. Gates the MERGE only |
| 5. The ruling merged and minted | MET | `RL-1459` carries DP-A3-1 to DP-A3-7; DP-A3-7 = (a) at `:179–:191` of the record. The completeness limb is `RL-1523` (the plan still calls it "RL 9491") |
| 6. The lane is free | NOT checked here | `gh pr list` is not run in this phase; gates the MERGE only (lead's) |
| 7. Maintainer's agreement and the lead's go | NOT given | this is not a GO |

**Plan drift** (the plan is frozen; the code is taken as merged; PL-1465's body is not edited):

1. `_check_reachable_objectives` / `_check_control_factor_model_calls` are merged as `_refuse_unapproved_objectives(version, payloads, resolver)` (`compile.py:675`), `_refuse_control_factor_keys` (`:701`) and `_refuse_control_factor_model_calls(algorithm, resolved_pins)` (`:724`). The first takes `version` and walks `version.pins.models`; the third takes `algorithm` and `resolved_pins` and skips a `peril_structure_ref` step (`:724–:749`: `step.model_ref is None` continues). Task 3 therefore needs the components to enter the `models` walk and `resolved_pins`, not a changed signature alone.
2. `compile_bundle` is at `compile.py:778` (the plan cites `:573-643`); `ResolvedArtifact` at `:521`; `_raise_named` at `:640`. Every line cite in the plan is stale and is re-anchored by symbol.
3. "PL 9649 / #1152" is `PL-1471` / `SL-1472` / #1247. "RL 9491" is `RL-1523`. "FD 9995" is `FD-1456`.
4. DP-A3-3 (a) reads "FD 9995 owns that gap". `PL-1471`'s merged T1, as it stands in `docs/specs/03-rating-engine.md` FR-240, reads "FD-1456 owns that gap, and this clause reaches them when it is fixed". The two name the same finding (working id 9995, minted FD-1456); they do not disagree, so no STOP. T2's anchor is the last sentence of that merged text, re-derived at Task 6.
5. **`_model_call_handler` already has a peril branch** (`runtime.py:611`), left by A-1 under `RL-1457` DP-3 (b): it returns `_model_call_failure(... "scoring a Peril Structure is slice A-3 (PL-1465); it is not yet built.")`. The plan's red cause ("`KeyError` on `payload["fit_result"]`, swallowed as `Failed to run custom node handler`") is therefore not the red cause on this base. The red for items 3 to 6 is `$model_call_error` carrying that sentence (the A-2 ledger's red-by-cause form), and Task 4 replaces the refusal. Reported to the lead.
6. `_load_boosters` (`runtime.py:777`) keys by `step.model_ref or step.peril_structure_ref` and reads `payloads[ref]["fit_result"]` with `.get("fit_result", {})`, so a structure ref is already skipped without error. It does not load component boosters (Task 4 Step 1). A-2 added `_load_glm_scorers` (`:761`), which Task 4 must also extend for a GLM component.
7. The rounding rule changed after the plan. See the open points below.

### Open points raised at Task 0 (not decided here)

**OP-1 — composition on `Decimal` against `assemble_risk_premium`'s float64.** `RL-1459` item 7 rules DP-A3-5 (a): "A-3 predicts each component at full precision. It composes `frequency × severity` per peril, or `burning_cost`, applies FR-189's treatment, and sums (FR-188), all on `Decimal`." The plan (Global Constraints, "Not edited, read only") keeps `assemble_risk_premium` unchanged, and that function computes on `float64` arrays (`modelling/perils.py:104`). Both cannot hold: a `Decimal` composition either needs a new `Decimal` path (and the plan's write set has no file for it) or a change to `perils.py`, which the plan lists as read only. Recommendation: build the composition inside `_score_peril_structure` on `Decimal(repr(x))` per component using `_restore`'s arithmetic restated for one row, and test it against `assemble_risk_premium` to a stated tolerance; or rule that float64 is accepted for A-3. Not built until the lead rules; the compile tasks (1 to 3) do not depend on it.

**OP-2 — the rounding rule for a peril step.** The plan's item 3 expects `round(v)`; `RL-1459` item 7 says a `model_call` output is never rounded at the step; A-2's later rulings (00:40:31 and 00:44:31 BST, recorded in `LG-9449`) make it one rule for every `model_call`: `result_type` absent means legacy `round(prediction)`, `result_type` present means unrounded to FR-244's boundary. Proposed reading: the peril step follows A-2's rule, so a step without `result_type` rounds the total once, a step with `result_type` carries it unrounded. Items 3 to 6 then assert both forms. Needs the lead's confirmation before Task 4.

## Build log

**2026-10-10, authoring phase.** Branch `sl-1466-a3-peril-scoring`, from `e0e12dd834318294a5e0932618ca177c71a7bf46`. Stamps are BST.

- Commit 1: `PL-1465`'s `status:` line `draft` to `active` and this file.
- **Task 1, compile-side reds (items 1, 2, 7, 8, 9), 2026-10-10.** New `packages/pricing-core/tests/test_rating_peril_scoring.py`: an AD `frequency_severity` and a WS `burning_cost` peril over three GBM payloads, a `FakeResolver`, an algorithm whose `s_rp` names the structure. **Authored, not run**: small tests are paused by the lead; the expected causes are item 1 `AssertionError` (a component ref missing from `resolved_payloads`), items 2, 8, 9 `Failed: DID NOT RAISE`. Red-by-cause is owed after "small tests RESUME". The runtime items (3 to 6) wait on OP-1 and OP-2.
- **Task 2 (compile resolves and checks the components), 2026-10-10.** `compile.py`: `_check_peril_model_calls` (`BUNDLE_COMPILE_FAILED`, called beside `check_step_refs_pinned`), `_resolve_peril_components(structure_ref, payload, resolver, resolved_pins) -> dict[str, ResolvedArtifact]` (`separate_model` refused first with `LOSS_TREATMENT_UNIMPLEMENTED`; each distinct component resolved once, a directly pinned component reusing the pin loop's result; `PIN_NOT_APPROVED` naming component, structure and peril), and a loop in `compile_bundle` after the pin loop that embeds each component's payload (a GLM component's Factors, Bandings and Groupings through `_carry_glm_inputs`) and adds it to `resolved_pins` for Task 3. A fourth parameter `resolved_pins` beyond the plan's signature, to honour "never resolve a ref twice"; name and return type are as `PL-1471`/`RL-1523` need. `ruff check` clean on both files. **Not run**: small tests are paused; the expected result is items 1, 2, 7, 8, 9 green.
