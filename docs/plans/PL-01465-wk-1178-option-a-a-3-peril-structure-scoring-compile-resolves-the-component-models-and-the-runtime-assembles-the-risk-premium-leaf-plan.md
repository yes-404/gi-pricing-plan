---
id: PL-1465
family: plan
kind: leaf
title: WK-1178 — Option A, A-3, Peril Structure scoring, compile resolves and maturity-checks the component models and the runtime assembles the risk premium (FR-188, FR-189, FR-191, FR-222, FR-237, FR-240, FR-20, NFR-491): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-06            # original date 2026-10-05, set at the draft; minted 2026-10-06
owner: planner
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1263, PL-1371, CR-1212, PL-1408]
---

# PL-1465 — WK-1178: Option A, A-3, Peril Structure scoring, leaf plan

Filed under working id 9595 (this plan, minted as PL-1465) and slice working id 9596 (its `SL-` row under WK-1178
in [`../roadmap.md`](../roadmap.md), `draft`, minted as SL-1466), both reserved by the lead in
`~/gi-pricing-plan.local/handover/eta.md` ("SL 9596 / PL 9595 … planner-a3 (opus) | Option A
A-3"). Minted 2026-10-06 in the G2 chain batch. Every code fact was read at `origin/main`
`137bc817ef1fb40ea57e9053e0ad40b73bdff3a8` (#1128's merge, 2026-10-05T16:44:24+01:00) unless a PR
head is named.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (`pricing-core` stays free of FastAPI,
> SQLAlchemy and Redis; ADR-703), `fastapi-service` (Task 5's HTTP test only), `spec-change`
> (Task 6, only where a ruling carries text), `dev-commands` (the two-half gate) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

### Pre-mint delta, 2026-10-05

Edited 2026-10-05 from 18:39:52 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's brief `~/gi-pricing-plan.local/handover/brief-capacity-fill-2026-10-05.md`
Part C. origin/main `116a0da6f63cd7733335d6c2c6975c219b4e0e3d` was merged in first (only the
generated `docs/INDEX.md` conflicted, and was regenerated). Nothing is re-decided here. What this
delta changed, each marked in place, nothing deleted:

1. **RL-1459's P1 and P2, applied byte for byte.** The authority is RL-1459 (#1188 @`cc5d0d61`), §"The plan texts (P-texts)" (`:258-301` of the record at that
   head): P1 at `:265-270`, P2 at `:272-282`. `<RL>` inside a P-text is filled with `RL-1459`,
   as the record's `:25-27` says ("`<date>` and `<RL>` inside the T- and P-texts, which the
   applying slice fills"); it is re-pointed at the mint. Counts are exact-substring counts in
   this file (`grep -c -F` semantics), read before and after the edit:

   | P-text | Find string | Find before → after | New text before → after |
   |---|---|---|---|
   | P1 | the line `## Decision points` (an insertion after it; the line is kept) | 1 → 1 | 0 → 1 |
   | P2 | `Medium: about one and a half executor days (sizing memo §2, A-3: 1 / 1.5 / 2).` | 1 → 0 | 0 → 1 |

2. **Activation need 5 names the ruling:** RL-1459 (#1188), and also DP-A3-7 below.
3. **A-2's R4 hands A-3 a check (with a red).** The maintainer's (by delegation) entry
   "2026-10-05 17:27:55 BST — FD 9572 CAUSE: …; A-2 readings" (`channel/to-lead.md`), its A-2
   line, verbatim in the part that binds this plan:

   > R4 (peril_structure_ref steps are not checked): ACCEPTED for A-2, and A-3 checks a structure's component models' feature maps (add it to A-3's plan).

   A-2 (PL-1464, #1178 @`176a6a75`) builds the check as "one function, called from both save
   paths" (`POST /api/v1/rating-algorithms` and `POST /api/v1/sub-graphs`), refusing with
   `422 MODEL_CALL_FEATURE_MAP_INVALID` under its readings R1 to R3 (its Task text read at that
   head, `:360-390`). This slice extends **that function** to a `peril_structure_ref` step, so
   both save paths gain it at once. New **Acceptance 16** and **DP-A3-7**, both below. The
   write set gains the file that defines A-2's function (`backend/src/app/platform/
   rating_algorithms.py` in PL-1464; Task 0 Step 3 records its name and file at A-2's merge),
   and its tests go in `backend/tests/test_rating_peril_scoring_api.py`, already in the write
   set. The size is not re-estimated here: this is a scope point for the lead, and a write into
   `backend/src/app/platform/` the plan had listed as not written.
4. **DP-A3-7 (open; owner the decision-maker).** One `feature_map` feeds every component of the
   structure, but A-2's check compares a map with one Model. Which set is a value checked
   against? (a) **the union**: a value is accepted if at least one component model accepts it
   (its Factor slugs, its declared offset column under R2, or its `feature_order` under R3);
   a value no component accepts is refused. (b) **every component**: a value must be accepted
   by each component. **Recommendation (a).** Under (b) the frequency GLM's `exposure_years`
   offset column (RL-1459's P3: "The frequency GLM's `exposure_years` offset reaches B4 through
   its `feature_map`") is refused against the severity component, which declares no such
   offset, so A-4's ruled path could not save. A component ref resolving to no Model is left to
   compile under (a) and (b) alike (R1). *(Pre-mint delta 2 2026-10-05, DP-A3-7 ruled; see §"Pre-mint delta 2, 2026-10-05".)* **Ruled (a)** at 18:44:45 BST;
   A-2's check has no completeness limb, so none applies here. *(Pre-mint delta 3 2026-10-06, records named; see §"Pre-mint delta 3, 2026-10-06".)* The union's record is RL-1459 (#1188); the per-component completeness limb's is RL 9491 (working id, #1214), built by SL 9495, not here.
5. **Serialisation with SL-1436 (PL-1435, WK-673; #1193 @`42d8be16`).** Its hand-off
   (`:235-243` at that head), and the maintainer's (by delegation) entry "2026-10-05 17:51:03
   BST — …", item 2, "Serialising A-1/A-2/A-3 with SL 9568 on _model_call_handler: agreed". So
   this slice and SL-1436 **serialise** on `_model_call_handler`; the one that merges second
   rebases and re-runs `test_rating_wire_order.py` and SL-1436's Task 2c replay script. The
   hand-off binds this slice's peril branch, verbatim: "A branch that any of them adds must
   return through that same expression, or through `_model_call_failure`, and must not return
   `{"output": {produced names only}}`" (the expression is `{**context, **produced}`). With
   **A-2** (#1178 @`176a6a75`) the order was already serial (activation need 4, a plan
   dependency); item 3 adds a second shared definition, A-2's save-path check, which changes
   nothing in that order.

### Pre-mint delta 2, 2026-10-05

Edited 2026-10-05 from 18:46:00 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's brief `~/gi-pricing-plan.local/handover/brief-planner-a3b-2026-10-05.md`.
origin/main `116a0da6f63cd7733335d6c2c6975c219b4e0e3d` was already contained in this branch, so
nothing was merged. Nothing is re-decided here. What this delta changed, each marked in place,
nothing deleted:

1. **DP-A3-7 is ruled (a), the union.** The maintainer's (by delegation) entry "2026-10-05
   18:44:45 BST — DP-A3-7 = (a) the UNION, with a per-component COMPLETENESS limb; A-1's needs
   put lane C on the G2 path" (`channel/to-lead.md`), item 1, verbatim:

   > DP-A3-7: (a). For the "this key is not a feature" test, a feature_map entry passes if AT LEAST ONE component model accepts it (one map feeds every component; the frequency GLM's exposure_years OFFSET, RL 9571 P3, is not a severity feature, and (b) would refuse A-4's ruled demo path).
   > PLUS a COMPLETENESS limb, if A-2's single check function has one (R1–R3: a model's own factors or feature_order must be mapped): it applies PER COMPONENT, so EVERY component's required inputs must be present in the one map. The union must not let a map that starves one component save; that would only fail at score time as MODEL_CALL_FAILED. The planner states, with file:line in PL 9597, whether A-2's function has a completeness limb. If it does, Acceptance 16 gains a red (a map missing one severity factor → 422). If it does not, say so; no new limb is invented in A-3.
   > R4 now in PL 9595 as Acceptance 16: good catch; the platform/ write is accepted within A-3's estimate.

   The entry is not yet in a minted RL; the ruling's record id is the lead's to name, and the
   plan is re-pointed at it at the mint. *(Pre-mint delta 3 2026-10-06, records named; see §"Pre-mint delta 3, 2026-10-06".)* RL-1459 (#1188) is named for the union half (the 2026-10-06 01:15:49 BST entry); the completeness limb is RL 9491's. Its last line settles delta 1 item 3's scope point:
   the `backend/src/app/platform/` write is inside A-3's estimate.

2. **The completeness limb: A-2's check has NONE.** Read in PL-1464 (#1178,
   `pl-9597-a2-glm-model-call` @`176a6a756f863376515f3dd5ec0a4c29afbc14a7`,
   its one file under `docs/plans/`, path elided because it carries the unminted id, which check 32
   refuses):
   - item 13, `:363-366`: the save "resolves each `model_call`'s `model_ref` to its Model and
     the Model's Factors … and **refuses a value outside them**": a membership test on each
     `feature_map` value;
   - R2, `:379-380`: "the **accepted values** are the Model's Factor slugs plus the column its
     spec declares as a `log_column` or `column` offset": membership again;
   - R3, `:382-384`: a GBM "is checked the same way, against its Factors' slugs", or "against
     `feature_order`" when it has no Factors: the same membership test;
   - item 18, `:507-511`: the sub-graph save calls "the check item 13 adds", "one function";
     it adds no limb.

   No item asks that a model's Factors, offset column or `feature_order` all be mapped, and no
   red test in PL-1464 posts a map that omits one. The code the check builds on adds none:
   `create_algorithm` at origin/main `116a0da6`
   (`backend/src/app/platform/rating_algorithms.py:94-125`) runs `_parse_algorithm` and
   `_issues_to_error` and the duplicate `(slug, version)` refusal, with no `feature_map` check
   at all. An unmapped Factor is refused only at score time, by `resolve_factors`'s missing
   source column (`packages/pricing-core/src/pricing_core/modelling/factors.py:170-172`, FR-87,
   PL-1464's Task 0 row 0.5), reaching the caller as `MODEL_CALL_FAILED`; an unmapped offset
   column as `MODEL_CALL_FAILED` naming `MODEL_OFFSET_MISSING` (PL-1464 item 14, `:403-404`).
   *(Dated note, 2026-10-05 18:48:53 BST: this cited `factors.py:106`, copied from PL-1464's
   row 0.5 unchecked. At origin/main `ecbd1954d90b1faf0bd197174d720d90ad8f6c6d` (the file is
   unchanged since `116a0da6`), `def resolve_factors` is `:105`; the refusal is `:170-172`, the
   `missing = [c for c in factor.source_columns if c not in frame.columns]` test and its
   `raise FactorResolutionError(`.)*

   So, as the ruling says for that case, **no completeness limb is invented in A-3**, and
   Acceptance 16 gains **no** "missing severity factor → 422" red. Acceptance 16's membership
   test stands under (a) as written. If A-2's check gains a completeness limb before this
   slice runs (Task 0 Step 3 reads A-2's merged function), the ruling's per-component clause
   then binds, and the executor STOPS and reports rather than building it unplanned. *(Pre-mint delta 3 2026-10-06, this STOP re-scoped; see §"Pre-mint delta 3, 2026-10-06".)* The per-component limb is at compile, SL 9495's (RL 9491); A-2's `required_model_inputs` helper is not a trigger. Only a save-time refusal of an unmapped required input in A-2's merged check is.

3. **Marked in place:** delta 1 item 4 (DP-A3-7), activation need 5, and Acceptance 16. No
   `SL-` row text names DP-A3-7 (`grep -n 'DP-A3-7' docs/roadmap.md` is empty), so
   `docs/roadmap.md` is not touched.

### Pre-mint delta 3, 2026-10-06

Edited 2026-10-06 from 01:17:02 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's brief `~/gi-pricing-plan.local/handover/brief-planner-a3-delta3-2026-10-06.md`,
items (i) and (ii) of `~/gi-pricing-plan.local/handover/a2a3-readiness-2026-10-06.md`. Read at
this branch's head `2404ac86aaba6e1211d0779d7d20bcfeb9c4742e`; nothing was merged. Nothing is
re-decided here. What this delta changed, each marked in place, nothing deleted:

1. **The completeness limb, per component included, is SL 9495's at compile, never A-3's.**
   Delta 2 item 2 was written before two entries in `channel/to-lead.md`. The first, headed
   "2026-10-05 18:51:33 BST — Save-time completeness: DECIDED NOW as (b), completeness at
   COMPILE; no OQ; an RL with the FR-240 T-text; A-2's code reused", verbatim in part:

   > (b): compile_bundle refuses a model_call step whose feature_map does not cover the PINNED model's required Factors (or its feature_order where it has none), using the existing resolver, before approval or deploy. Per component for a peril_structure_ref (17:44 DP-A3-7's per-component limb now has its home, at compile, not at save).

   and, from its RECORDS line: "plus a note in PL 9597 (A-2) that its membership check is
   explicitly NOT a completeness check. The build is a small WK-1178 slice after A-2 (the same
   function family) and before A-4's demo path." Its record is RL 9491 (working id, #1214
   @`6a33fca2`), item 2, "This is the home of the per-component limb of DP-A3-7 (the 18:44:45
   BST entry, item 1)"; its build is SL 9495 (PL 9494, working ids, #1216 @`b11f610b`).

   The second, headed "2026-10-05 19:03:24 BST — PL 9494 (#1216 @b4e4fdf5): the order change,
   A-4's need, DP-1 and R-a all ACCEPTED; DP-1's helper is BORN IN A-2", items 1 and 3, verbatim:

   > 1. ORDER: A-2 → A-3 → SL 9495 → A-4, ACCEPTED (the per-component limb needs A-3's _resolve_peril_components; it still satisfies after A-2 and before A-4). The need "PL 9649 merged" (ResolvedArtifact.factors): accepted.

   > 3. DP-1: ONE public pricing-core helper defines "a model's required inputs" (its Factors, or fit_result.feature_order when it has none). It is BORN IN A-2, which merges first: A-2's plan (PL 9597, unminted) gains a pre-mint task that creates the helper in pricing-core and has its own save check call it. SL 9495 then REUSES it with no second definition. If A-2 has already merged without it when SL 9495 starts, SL 9495 extracts it from A-2's function as a no-behaviour-change refactor commit before its reds. Either way, one definition, and a test proves both call sites use it (one helper, two callers, by grep in the test or an import assertion).

   So delta 2 item 2's conditional STOP is **re-scoped** as follows. Its other sentences stand.
   - **Not a trigger:** A-2's merged save check defining or calling `required_model_inputs`
     (`pricing_core.modelling.factors`, PL-1464 Task 1b). Under item 3 above the save check
     calls the helper, and the helper is not a completeness limb. Nor is the absence of any
     compile-time completeness check when this slice runs: SL 9495 runs after A-3 (item 1
     above).
   - **Still a trigger, and only this:** Task 0 Step 3 finds that A-2's merged save check
     **refuses** a `feature_map` because one of a model's required inputs is **not mapped**.
     That is a completeness refusal at save. The 18:51:33 entry homes it at compile, not at
     save, and its RECORDS line says A-2's check is "explicitly NOT a completeness check". The
     executor then STOPS and reports to the lead. It does not extend that refusal to the
     peril branch, and it does not remove it.
   - **Never built in A-3:** a completeness check of any kind, per component or not, at save
     or at compile. It is SL 9495's (RL 9491 item 2).

2. **SL 9495 consumes `_resolve_peril_components`.** PL 9494 (#1216 @`b11f610b`) Task 0 Step 1
   (`:381-386` at that head) greps for it under `packages/pricing-core/src`. Its Step 2
   (`:387-389`) records "its return type and the key of its dict". So Task 2 Step 1 keeps the
   name `_resolve_peril_components` and the return type `dict[str, ResolvedArtifact]`
   (§"Self-review" item 5). A change to either is a STOP to the lead before commit.

3. **DP-A3-7's records, named.** The maintainer's (by delegation) entry "2026-10-06 01:15:49 BST — The G2 records:
   ONE batch of seven, not two", verbatim in part: "DP-A3-7's union half goes into RL 9571 #1188
   with no new PR." So the record of DP-A3-7 (a), the union, is **RL-1459** (#1188). The record of its completeness limb is **RL 9491** (item 1 above). At
   `cc5d0d61c8c3229074bc93d876bd869f8fe6ac9e` (#1188's head, read 2026-10-06 01:17 BST) RL-1459
   does not yet carry DP-A3-7 (`git grep -c DP-A3-7` over its `docs/` files: no hit). Activation
   need 5's alignment clause covers the minted text. RL 9491 is SL 9495's need, not this
   slice's. The working → minted re-points are the minter's, at the mint.

4. **Marked in place:** delta 1 item 4, delta 2 items 1 and 2, activation need 5, and
   Acceptance 16. No `SL-` row text changes, so `docs/roadmap.md` is not touched.

## Goal

A Rating Version whose `model_call` step names a Peril Structure compiles and scores. At compile,
`compile_bundle` resolves each component model of the pinned structure (`frequency_model`,
`severity_model`, `burning_cost_model`), checks each is `approved` or better (FR-20, FR-240) and
embeds each payload in the Bundle, so the Bundle still scores with no database (NFR-491). At
score, the `model_call` handler predicts each component, builds one `PerilPrediction` per peril
and calls `pricing_core.modelling.perils.assemble_risk_premium`, so the step yields the
structure's risk premium (FR-188), restored per peril before the sum (FR-189). Today the
handler reads `payload["fit_result"]` from the structure's payload, which has none
(`runtime.py:540`), and a peril bundle fails at score with the engine's generic custom-node
error. This makes `WF-699` C4 (`PIN_NOT_APPROVED` on a component model) a reachable compile
outcome, subject to DP-A3-4.

**Architecture:** no new seam. Compile reuses the resolver it already receives
(`ArtifactResolver.resolve`, `compile.py:444-450`): a component is a `model` ref, so the
backend's existing `model` branch of `_Resolver.resolve` serves it, with whatever A-2 adds to
that branch for a GLM. The runtime reuses the one prediction dispatch per model kind that
A-2 leaves in `_model_call_handler` (the GBM branch at `runtime.py:549-567` today, plus A-2's
GLM branch), called once per component on the same one-row frame, and the arithmetic is
`assemble_risk_premium` unchanged (`modelling/perils.py:104`). The reconciliation job already
composes a structure this way over a holdout (`backend/src/app/worker/model_handlers.py:1437-1486`,
`_score` then `assemble_risk_premium`); rating and reconciliation then compute one risk premium
on one basis (FR-128).

**Tech Stack:** Python 3.12, Pydantic v2, Polars, the ZEN engine's `customHandler`
(`runtime.py:512`), pytest; FastAPI + SQLAlchemy 2 async only in Task 5's test.

**Spec, finding and records:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) §3.9, FR-188, FR-189, FR-190, FR-191
  (`02:294-297`), FR-193 (`02:304`);
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) the `model_call` row of the step
  table (`03:100`), FR-222 (`03:108`), FR-237 (`03:134`), FR-240 (`03:137`), FR-247 (`03:154`),
  FR-249 (`03:156`), the §4 example step `s_rp` (`03:265-268`), NFR-491 (`03:1332`);
- [`../specs/00-overview.md`](../specs/00-overview.md) FR-20 (`00:231`);
- `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` `:19` (trigger), `:28`
  (precondition), B4, C1, C3, C4, C5 (`:59`, `:70-74`);
- FD-1456 (#980 @`9074f155`, LOW at filing; HIGH by the maintainer's entry below),
  whose fix is A-1; FD-1458 (#1172 @`dee1a85c`, HIGH), whose fix is A-2;
- the sizing memo `~/gi-pricing-plan.local/handover/sizing-g2-peril-path-2026-10-05.md` (a local
  working note, read at `cdaaa573`): §1 F3, F4 and F8; §2's A-3 row.

## The maintainer's decisions this plan rests on, quoted

From `~/gi-pricing-plan.local/channel/to-lead.md`, the entry "2026-10-05 16:43:31 BST — THE
MAINTAINER'S DECISION (asked live): G2 takes OPTION A, WF-699's literal Peril Structure path is
BUILT IN P2; and the FD 9605 approval, now on the record" (`:17898`), verbatim:

> THE MAINTAINER, asked live with the sizing memo's two options (handover/sizing-g2-peril-path-2026-10-05.md, read at cdaaa573): "A: build it in P2". So G2 (CR-1212 :62-69, "WF-699 end to end") stands as written, no amendment, and the exit demo walks WF-699's trigger (:19), precondition (:28), B4 (:59, a model_call referencing the Peril Structure) and C1 (:70, pinning it).

> 1. Four serial build slices under WK-1178, as sized: A-1 FD 9995 in full (the peril approval carry plus the _Resolver peril branch; it flips PL 9683's Acceptance 7); A-2 GLM via model_call (FD 9605); A-3 Peril Structure scoring (compile resolves and maturity-checks the component models; the runtime calls assemble_risk_premium, fixing the bare KeyError on payload["fit_result"] at runtime.py:540); A-4 the demo scope on PL 9624/PL 9629 (a severity GLM, the peril structure, reconcile, approve, the B4 model_call, the C1 pin). About 5 executor-days likely (3.5–8), a chain after PL 9683 and PL 9649.

> 3. Planning starts now: leaf plans for A-1..A-4, red first, with contention against the in-flight plans.

> 4. The DOUBLE-COUNT design point (A1 seeds tables from the AD frequency model while B4's model_call scores a Peril Structure containing it, so the factor effects may count twice; WF-699 does not say how they combine) needs a DM's options and a recommendation, ruled BEFORE A-4's plan activates.

> 5. RISK, recorded: the sizing fits before the 4 Nov code freeze only on "3 lanes every day" (about 2 days spare at best). The maintainer has said the VM may be shut down from when the weekly allowance runs out until the reset (10 Oct 01:59 UTC); lost days come out of that slack. The Friday 9 Oct checkpoint re-checks the fit with measured progress.

So this slice is the third of a serial chain, A-1 → A-2 → A-3 → A-4, under WK-1178. Item 4's
double count is A-4's activation need, not this slice's: A-3 makes a peril `model_call` score
correctly in isolation, and how its output combines with seeded tables is an algorithm-design
question the ruling answers for the demo.

## Status

`draft`. **Six decision points are open** (§"Decision points"), each for a decision-maker's
ruling (a working id the lead reserves). None changes the slice's Work, its owner or its
place in the chain; three of them (DP-A3-1, DP-A3-2, DP-A3-3) change what compile refuses, so
their codes and texts must be ruled before Task 2. The plan moves to `active` only through a
separate activation PR, after every activation need below holds. That PR carries the `SL-`
row's status flip and this plan's.

### Activation needs, in order

1. **PL-1429 (#1133, the FD-1421 fix) merged.** It admits `peril_structure` in `pins.models` on
   the create route (`_PIN_TYPES`, its Task 2), which Task 5's HTTP test uses, and it edits
   `backend/src/app/platform/rating_versions.py`.
2. **PL 9649 (#1152, the FR-240 family fix) merged.** It edits `compile_bundle` (three calls
   after the pin loop) and `ResolvedArtifact` (a `factors` field), and adds
   `_check_reachable_objectives` and `_check_control_factor_model_calls`, whose T1 names "a peril
   structure's models are not reached … FD 9995 owns that gap, and this clause reaches them when
   it is fixed" (#1152 @`df8ba756`, its §"Spec texts" T1). DP-A3-3 decides whether this slice
   closes that gap.
3. **A-1 merged** (SL-1462 / PL-1461): the Peril Structure approval path and the
   `peril_structure` branch of `_Resolver.resolve`. Without it no backend compile can reach a
   peril pin (FD-1456, F1 and F2), and Task 5 has no `approved` structure to pin.
4. **A-2 merged** (SL-1463 / PL-1464): GLM scoring via `model_call` (FD-1458). This
   slice predicts each component through the same per-kind dispatch, so a GLM component scores
   only after A-2. A-2 and this slice both edit `_model_call_handler` and `compile_bundle`;
   they serialise in any case.
5. **The ruling on DP-A3-1 to DP-A3-6 merged and minted.** *(Pre-mint delta 2026-10-05, RL-1459; see §"Pre-mint delta, 2026-10-05". It is RL-1459 (#1188 @`cc5d0d61`); DP-A3-7's ruling is needed too.)* *(Pre-mint delta 2 2026-10-05, DP-A3-7 ruled; see §"Pre-mint delta 2, 2026-10-05".)* DP-A3-7 was ruled (a) at 18:44:45 BST; the need is its record minted. *(Pre-mint delta 3 2026-10-06, records named; see §"Pre-mint delta 3, 2026-10-06".)* That record is RL-1459 (#1188), which carries the union half; RL 9491 (the completeness limb) is SL 9495's need, not this slice's. If the minted text differs from this
   plan, the minted text governs, and the planner aligns the plan before its first merge.
6. **The lane is free under `RL-1263` as amended by RL 9620 (working id, #1162):** no build
   slice that edits `compile_bundle` (PL 9610, PL 9609; PL 9649 once merged is history) or
   `_model_call_handler` is in flight (§"Write set").
7. **The maintainer's agreement**, and **the lead's go in a separate activation PR**.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means the named test was run and failed **for the stated cause** before the code that turns it
green; a failure with the right exception type and a different cause is a plan defect
([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger, with the
failure line as printed. The pricing-core tests are in the new module
`packages/pricing-core/tests/test_rating_peril_scoring.py`; run one module at a time
(`uv run pytest packages/pricing-core/tests/test_rating_peril_scoring.py -q`), never the full
suite outside Task 7.

1. **The components are embedded (red first).**
   `test_a_peril_structure_pin_compiles_with_its_component_models_embedded`: a structure with an
   AD `frequency_severity` peril and a WS `burning_cost` peril compiles, and
   `bundle.resolved_payloads` holds `str(ref)` for each of its three component model refs.
   Red today by cause: `AssertionError` naming a missing component key (compile walks only
   `version.pins`, `compile.py:618-631`).
2. **A component below `approved` is refused at compile (red first).**
   `test_a_peril_component_below_approved_is_refused_at_compile`, parametrised over the
   component statuses `draft`, `fitted`, `review`, `superseded`, `archived`
   (`model_schema.modelling.ModelStatus`, `modelling.py:1975-1981`): `ValueError` matching
   `PIN_NOT_APPROVED`, whose message names the component ref, the structure ref and the peril
   code. Red today: `Failed: DID NOT RAISE`. The control,
   `test_an_approved_component_compiles`, passes on both trees.
3. **A peril `model_call` scores the assembled risk premium (red first).**
   `test_a_peril_structure_model_call_scores_its_assembled_risk_premium`: two GBM components
   (built with `_train_tiny_booster`, `test_rating_runtime.py:30`, in the payload shape of
   `_gbm_model_payload`, `:42`) and one GBM burning-cost component; `score_one` returns, for the
   step's produced name, exactly `round(v)`, where `v` is the `risk_premium` row of
   `assemble_risk_premium` over `PerilPrediction`s whose arrays the test computes with
   `pricing_core.modelling.predict.score_fitted` on the same one-row frame (the reconciliation
   path, `model_handlers.py:1437-1447`). Red today by cause: `RuntimeError` whose text contains
   `Failed to run custom node handler` and the step's `nodeId` (the handler's `KeyError` on
   `payload["fit_result"]`, `runtime.py:540`, swallowed by the binding as `_model_call_failure`'s
   docstring records, `runtime.py:94-105`). A different cause is a plan defect.
4. **A GLM component scores (red first, after A-2).**
   `test_a_peril_structure_with_a_glm_component_scores`: the AD frequency component is a GLM
   (`_glm_model_payload`, `test_rating_runtime.py:72`, with whatever Factor, Banding and Grouping
   payloads A-2's compile embeds; Task 0 Step 3 records A-2's shape). The expected value is
   computed as in item 3. Red today by the same cause as item 3.
5. **Restoration is per peril, before the sum (FR-189).**
   `test_peril_scoring_restores_each_peril_before_the_sum`: the AD peril `capped` with
   `restoration_loading` `"1.10"` and the WS peril `flat_loading`; the value equals item 3's
   computation with the same treatments, and differs from a computation that applies either
   loading to the total. Red today by item 3's cause.
6. **The Bundle is self-contained (NFR-491).**
   `test_a_peril_bundle_scores_after_a_json_round_trip_with_no_resolver`:
   `Bundle.model_validate_json(bundle.model_dump_json())`, then `load_bundle`, then `score_one`,
   with the resolver object deleted before the round trip; the value equals item 3's. Red today
   by item 3's cause.
7. **The content hash is unchanged by component embedding (FR-239).**
   `test_the_peril_bundle_hash_is_reproducible_from_the_pins`: two compiles of one version give
   one `content_hash`, and it equals `bundle_hash(graph, pins)` (`compile.py:522`): components
   are pinned by version inside an immutable structure (`model_schema/perils.py:214-221`), so
   the hash stays a function of the pins. Green on both trees; it guards the design against a
   hash that starts to read the payloads.
8. **DP-A3-1's outputs rule (red first, under the ruled option).** Under the recommended (c):
   `test_a_peril_model_call_with_two_produced_names_is_refused_at_compile`, with the §4 example's
   `["risk_premium_minor", "peril_risk_premium"]` (`03:268`): `ValueError` with the ruled code,
   naming the step and the names. Red today: `Failed: DID NOT RAISE`.
9. **DP-A3-2's `separate_model` rule (red first, under the ruled option).** Under the
   recommended (a): `test_a_separate_model_large_loss_is_refused_at_compile`: `ValueError`
   matching `LOSS_TREATMENT_UNIMPLEMENTED`, naming the structure and the peril. Red today:
   `Failed: DID NOT RAISE`.
10. **DP-A3-3's transitive checks (red first, only under (a)).**
    `test_a_control_factor_in_a_peril_component_is_refused` (`CONTROL_FACTOR_IN_RATEABLE_PATH`,
    naming the component, the feature and the Factor) and
    `test_an_unapproved_custom_objective_under_a_peril_component_is_refused`
    (`PIN_NOT_APPROVED`, naming the component and the objective), each built on PL 9649's own
    fixtures as merged. Red after PL 9649 and before this slice: `Failed: DID NOT RAISE`.
11. **Over HTTP, end to end (Task 5).**
    `backend/tests/test_rating_peril_scoring_api.py::test_a_rating_version_pinning_an_approved_peril_structure_compiles_and_scores`:
    a structure approved through A-1's path, a Rating Version created through PL-1429's route
    with the structure in `pins.models`, `POST /api/v1/rating-versions/{id}/compile` → the Job
    `succeeded`, then `POST /api/v1/score` returns the value item 3's computation gives for
    the posted context. Red before this slice by cause: the score answers the
    `MODEL_CALL_FAILED` path or the engine's custom-node error, never a value.
12. **Unchanged behaviour stays green, by run:** `test_rating_compile_bundle.py`,
    `test_rating_runtime.py`, `test_perils.py`, `test_rating_pin_membership.py` (all under
    `packages/pricing-core/tests/`), and A-1's discharge test (an unapproved structure is
    refused at compile), each `-q` with its pass count recorded in the ledger.
13. **DP-A3-6 (only under (a)):** `uv run python scripts/bench-rating.py --peril-structure`
    prints a p50/p99 for a peril `model_call` with two `frequency_severity` perils and one
    `burning_cost` peril, run in a window with no gate slot held (`flock -n /tmp/slots/gate-1
    true` and the same for `gate-2`, both rc 0, recorded) and recorded in the ledger. No budget
    is asserted (DP-A3-6).
14. **The full two-half gate** (CLAUDE.md §11) passes on the slice's head, run once, through
    the gate-runner, in a held gate slot; each command's rc and the tree are recorded.
15. **`git diff --stat origin/main...HEAD`** lists only §"Write set"'s paths; the ledger
    records it.
16. **A peril `model_call`'s `feature_map` is checked against its component models (red
    first).** *(Pre-mint delta 2026-10-05, RL-1459; see §"Pre-mint delta, 2026-10-05".)* Saving an algorithm (`POST /api/v1/rating-algorithms`)
    and a sub-graph (`POST /api/v1/sub-graphs`) whose `peril_structure_ref` step maps a value
    that no component model accepts (under DP-A3-7 (a); A-2's R2 and R3 define "accepts")
    answers `422` with `code == "MODEL_CALL_FEATURE_MAP_INVALID"`, the detail naming the step,
    the value and the structure's ref; no row is written. The control: a map whose every value
    some component accepts, including the frequency component's offset column, answers `201`.
    **Red first:** after A-2's merge the same map saves `201`, because R4 skips the step; the
    red is recorded in the ledger. *(Pre-mint delta 2 2026-10-05, DP-A3-7 ruled; see §"Pre-mint delta 2, 2026-10-05".)* DP-A3-7 is ruled (a); A-2's check
    has no completeness limb, so no "missing factor" red is added here. *(Pre-mint delta 3 2026-10-06, completeness re-homed; see §"Pre-mint delta 3, 2026-10-06".)* A map that misses a component's required input still saves `201` at this slice's merge; its `422` at compile is SL 9495's (RL 9491 item 2).

## Global Constraints

- **Money is integer minor units** (CLAUDE.md §7). The step's value is one `int`, rounded once
  from the float sum; no per-peril value is rounded before the sum (`assemble_risk_premium`
  sums floats, `perils.py:104-151`).
- **The model_call rounding convention stays the provisional one** that the handler's
  docstring records (`runtime.py:512-524`: "`round()` to the nearest whole unit, on the
  assumption the pinned model was itself fitted to predict on the money-minor scale already").
  This slice does not settle it (DP-A3-5).
- **`pricing-core` stays importable standalone** (CLAUDE.md §2, ADR-703): no FastAPI,
  SQLAlchemy or Redis import enters `pricing_core/rating/`.
- **Nobody hand-writes a shape that exists in `model-schema`** (CLAUDE.md §2): the structure is
  read with `model_schema.PerilStructure.model_validate`, never as a hand-indexed dict.
- **No pandas** (CLAUDE.md §3).
- **A handler never raises** (`runtime.py:94-133`): any refusal at score goes through
  `_model_call_failure`, so `score_one` reports `MODEL_CALL_FAILED` with the real cause.
- **Enforcement is proven on deliberately broken input** (CLAUDE.md §13): items 1–5, 8–10 are
  red first.
- **Shared files** (`RL-1263`, as amended by RL 9620): two concurrent build slices may not both
  change the same existing function, class, spec section or policy table. `docs/INDEX.md` is a
  registry: regenerate, never hand-merge.
- **No spec text is written by this slice unless a ruling carries it verbatim** (Task 6).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `02` | FR-188 | A `model_call` on a Peril Structure yields the sum over perils of `frequency × severity` or `burning_cost` | `req("FR-188")` on items 3, 4 |
| `02` | FR-189 | Each peril's large-loss treatment is applied before the sum; `separate_model` per DP-A3-2 | `req("FR-189")` on items 5, 9 |
| `02` | FR-191 | A Rating Version references the structure, not a scatter of models, and scores through it | `req("FR-191")` on items 3, 11 |
| `02` | FR-193 | A component scores from its declarative artifact alone, inside the Bundle | `req("FR-193")` on item 6 |
| `03` | FR-222 | `exact` invokes the structure's models; the outputs rule per DP-A3-1 | `req("FR-222")` on items 3, 8 |
| `03` | FR-237 | The structure is pinned at its exact version; its components are pinned by version inside it | `req("FR-237")` on items 1, 7 |
| `03` | FR-239 | The hash stays reproducible from the pins | `req("FR-239")` on item 7 |
| `03` | FR-240 | "All references resolvable and at a sufficient maturity" reaches the components; the transitive clauses per DP-A3-3 | `req("FR-240")` on items 1, 2, 10 |
| `00` | FR-20 | A component below `approved` is refused | `req("FR-20")` on item 2 |
| `03` | NFR-491 | The peril Bundle scores with no database or network | `req("NFR-491")` on item 6 |

**Out of scope, stated so nothing is silently dropped:**
- the Peril Structure approval path and the resolver's `peril_structure` branch (A-1, FD-1456);
  whether that approval checks FR-20 on the components is A-1's (DP-A3-4 reads it);
- GLM scoring itself (A-2, FD-1458), which this slice calls;
- the demo: a severity GLM, the structure, its reconciliation and approval, the B4 step and the
  C1 pin (A-4, on PL 9624 and PL 9629), and the double count (the maintainer's item 4, ruled
  before A-4);
- FR-249's per-peril outputs, under DP-A3-1 (c), carried with the owner the ruling names;
- `approximation` mode for a structure: the handler ignores `step.mode` today for every
  `model_call` (`git grep -n approximation origin/main -- packages/pricing-core/src/pricing_core/rating`
  finds only a docstring at `score.py:404`), and this slice does not change that;
- FR-190's reconciliation at compile: WF-699's precondition (`:28`) puts a passing
  reconciliation before approval, which is A-1's path.

### Task 0 at planning time (measured, not asserted)

Run by this plan's author at 2026-10-05 16:51:10 BST, at `origin/main` `137bc817`:

```text
$ git grep -n 'assemble_risk_premium' origin/main -- packages backend examples scripts
origin/main:backend/src/app/worker/model_handlers.py:1363:        assemble_risk_premium,
origin/main:backend/src/app/worker/model_handlers.py:1486:        assembled = assemble_risk_premium(predictions)
origin/main:packages/pricing-core/src/pricing_core/modelling/perils.py:9: (docstring)
origin/main:packages/pricing-core/src/pricing_core/modelling/perils.py:51:    "assemble_risk_premium",
origin/main:packages/pricing-core/src/pricing_core/modelling/perils.py:104:def assemble_risk_premium(
(and 20 lines in packages/pricing-core/tests/test_perils.py)

$ git grep -n -E 'frequency_model|severity_model|burning_cost_model|excess_model' origin/main -- packages/pricing-core/src/pricing_core/rating backend/src/app/platform/rating_versions.py
(no output)
```

So nothing in `rating/` calls the assembly, and nothing in compile or the backend compile
resolver reads a component field. The first output is shortened where marked; the second is
verbatim.

### Write set, and its contention (`RL-1263`)

"Edited" means an existing definition changes; "added" means a new definition in an existing
file. Rows marked *(DP-n x)* exist only under that option.

| Path | Change | Other slices touching it | Consequence |
|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | edited: `compile_bundle` (`:573-643`), one call after the pin loop; added: `_resolve_peril_components` (resolves, maturity-checks and returns each component's `ResolvedArtifact`); added *(DP-A3-1 c, DP-A3-2 a)*: `_check_peril_model_calls`; edited *(DP-A3-3 a)*: the callers of PL 9649's `_check_reachable_objectives` and `_check_control_factor_model_calls`, to pass the components | **PL 9649** (#1152 @`df8ba756`) edits `compile_bundle` and `ResolvedArtifact`, adds the two checks; **PL 9610** (#1170 @`ca407ed9`, WK-1250 S2) edits `compile_bundle` and `_MATURITY_CHECK_EXEMPT`; **PL 9609** (#1173 @`7c8736fd`, WK-1250 S3) edits `Bundle`, `compile_bundle`, `bundle_hash`; **A-2** (PL-1464, not pushed at planning) embeds GLM Factor, Banding and Grouping payloads at compile (sizing memo §2, A-2 row) | **serial**: `compile_bundle` is in the set PL-1371 §5 rule 4 serialises outright. PL 9649 and A-2 are activation needs; PL 9610 and PL 9609 must not be in flight beside this slice (activation need 6) |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | edited: `_model_call_handler` (`:512-583`), a `peril_structure_ref` branch before the `fit_result` read; `_load_boosters` (`:586-621`), loading each GBM component's booster under the component's ref; added: `_score_peril_structure` | **A-2** edits `_model_call_handler`'s `else:` branch (`:568-579`) and its tests; **PL 9776** (#1051 @`ecbb82ab`) edits `to_wire`, three node builders, `CompiledBundle` and `load_bundle`; **PL 9610**, **PL 9609** edit `load_bundle` / `CompiledBundle`; **PL 9688** (#1145 @`2f3269c8`) edits `_decision_table_node` | A-2: **serial** (activation need 4). The others edit different definitions in the same file: `other_shared_path`, so they serialise unless the dispatch record names the path and the check that no definition is shared. This slice edits neither `load_bundle` nor `CompiledBundle` |
| `packages/pricing-core/tests/test_rating_peril_scoring.py` | added (new module) | none | none |
| `packages/pricing-core/tests/test_rating_runtime.py`, `test_rating_compile_bundle.py` | **read only**: fixtures imported (`_train_tiny_booster`, `_gbm_model_payload`, `_glm_model_payload`; `FakeResolver`, `valid_algorithm_payload`, `_version`) | A-2 flips `test_rating_runtime.py:377` | none: no existing test is edited here |
| `backend/tests/test_rating_peril_scoring_api.py` | added (new module, Task 5); Acceptance 16's tests *(Pre-mint delta 2026-10-05, RL-1459; see §"Pre-mint delta, 2026-10-05".)* | none | none |
| the file defining A-2's save-path feature-map check (`backend/src/app/platform/rating_algorithms.py` in PL-1464) *(Pre-mint delta 2026-10-05, RL-1459; see §"Pre-mint delta, 2026-10-05".)* | edited: that function gains a `peril_structure_ref` branch (Acceptance 16) | **A-2** (PL-1464, #1178) adds it | plan dependency: serial after A-2 (activation need 4) |
| `scripts/bench-rating.py` *(DP-A3-6 a)* | edited: `main` (`:882`), one flag; added: a peril fixture builder | **PL 9728** (#1113 @`3ad98fe2`) edits `scripts/bench-rating.py` | different definitions: `other_shared_path`; the second to merge re-reads |
| `docs/specs/03-rating-engine.md` (texts T1–T3 under the ruling) | edited: FR-240 cell (`:137`), the `model_call` row (`:100`), the owned-code list (`:933`) | **PL 9649** appends T1/T5 to the FR-240 cell and T4 to the owned list; PL 9688, PL-1429, PL-1419, PL 9689 edit other `03` rows | **serial with PL 9649** on the FR-240 cell and the owned list (it is an activation need); others: distinct rows, the second to merge re-reads |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry |

**Not edited, read only:** `pricing_core/modelling/perils.py` (`assemble_risk_premium`,
`PerilPrediction`), `pricing_core/modelling/predict.py` (`score_fitted`, `predict_glm`),
`model_schema/perils.py`, `backend/src/app/platform/rating_versions.py` (`_Resolver.resolve`'s
`model` branch serves a component; A-1 adds the `peril_structure` branch). If the executor
finds a change is needed in any of these, that is a replan trigger to the lead, not a silent
widening.

**Same Work.** A-1 to A-4 are all WK-1178, as are PL-1429 and PL 9776. Under `RL-1263` as it
stands ("from different Works", `:54`) none runs beside another WK-1178 build; under RL 9620's
amendment (#1162) same-Work pairs may run together only with no plan dependency. A-1 → A-2 →
A-3 is a dependency chain, so this slice is serial either way.

**Open PRs read at `137bc817` (`gh pr list --state open`, 2026-10-05 16:4x BST).** Each plan's
write set was read from its branch at the head named in the table; the reading was delegated
and its result kept, not its transcript. No open PR rules on this slice's subject. A-1 (PL-1461)
and A-2 (PL-1464) were **not pushed** at planning (`git ls-remote origin` shows no branch for
either), so their write sets come from the sizing memo §2 and the maintainer's item 1; Task 0
Step 3 re-reads both as merged.

### Size

Medium: about one and three-quarter executor days (sizing memo §2, A-3: 1 / 1.5 / 2, plus DP-A3-3's +0.25 accepted by RL-1459: 1.25 / 1.75 / 2.5, estimates). Five build tasks
after the preconditions, no migration, no frontend. One full two-half gate. Under DP-A3-6 (a)
one bench run in a quiet window.

## Decision points

**Ruled 2026-10-05 by RL-1459 (the maintainer's (by delegation) entry "2026-10-05 17:08:35 BST — A-3 / A-4 DP memo (handover/dp-memo-a3-a4-2026-10-05.md) RULED; the reconciliation TOLERANCE set").** DP-A3-1 (c), code `BUNDLE_COMPILE_FAILED`; DP-A3-2 (a), and Task 4 maps `assemble_risk_premium`'s `ModellingError` to `_model_call_failure`; DP-A3-3 (a), scope accepted, +0.25 executor-day; DP-A3-4 (a), C4 shown live by A-4 on a superseded component; DP-A3-5 (a), composed on exact `Decimal` and rounded only at the output step (17:12:40, option (B)), the frequency offset through the `feature_map`; DP-A3-6 (a), recorded only, run only when no gate is running. The table below records what was weighed; where it differs, the ruling governs. Spec texts T1–T4 are the ruling's, verbatim.

Each is open. The owner is a decision-maker; the ruling's working id is reserved by the lead.
Every option below was weighed against the code at `137bc817`.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-A3-1** | What a peril `model_call` writes to its `produces` names. Today the handler writes one value to **every** produced name (`runtime.py:581`), and the `03` §4 example produces `["risk_premium_minor", "peril_risk_premium"]` (`03:268`) where the second is declared `map<string, money_minor>` (`03:255`). No such map type is handled anywhere in the runtime (`git grep -n 'map<' origin/main -- packages/model-schema/src/model_schema/rating.py packages/pricing-core/src/pricing_core/rating` is empty) | (a) every name gets the total, as for a model; (b) the first name gets the total, a second gets a per-peril map `{peril: minor}` (FR-249), a third is refused; (c) a peril call declares exactly one produced name, which gets the total; more is refused at compile with a named code; FR-249's per-peril outputs are carried with an owner | **(c).** (a) writes the total into a name the example declares as per-peril: a silently wrong value. (b) needs a map value to travel through the ZEN engine's pass-through, the output rounding (FR-226) and the ladder, none of which has been probed; that is a spike, not this slice. (c) refuses what it cannot yet serve. The code is the ruling's (`VALIDATION_FAILED` 422 is the nearest existing one) | decision-maker | Tasks 2, 6; item 8 |
| **DP-A3-2** | `separate_model` large-loss treatment. `assemble_risk_premium` refuses it with `LOSS_TREATMENT_UNIMPLEMENTED` (`perils.py`, `_restore`; `02:2691`). Where does a Rating Version meet that refusal? | (a) at compile: a pinned structure with any `separate_model` peril is refused, naming the structure and the peril; (b) at score: `_model_call_failure` on every quote; (c) build the excess layer | **(a).** A refusal that waits for a quote makes a version that compiles and then fails on every price. (c) needs FR-189's excess-layer arithmetic that `02` has not specified. (a) re-raises a `02` code in `03`, so `03`'s owned-code list needs a dated line (T3) | decision-maker | Tasks 2, 6; item 9 |
| **DP-A3-3** | Does this slice close PL 9649's "known gap" (its T1: "a peril structure's models are not reached … FD 9995 owns that gap, and this clause reaches them when it is fixed")? Once components resolve, FR-240's custom-objective and control-factor clauses can reach them | (a) yes: the components are passed to PL 9649's two checks in this slice, with T1's gap sentence superseded by a dated line; (b) no: a follow-on slice; (c) A-1 owns it, as FD-1456's fix | **(a).** This slice is where components first become resolved artifacts; a priced peril path that skips them contradicts FR-240 and `02` FR-88 as soon as it merges. (c) cannot work: A-1 resolves the structure, not its components. Scope growth over the sizing memo's A-3 row, so it is the ruling's | decision-maker (a scope point: the maintainer, if the ruling holds that it moves A-3's size) | Task 3; item 10 |
| **DP-A3-4** | Is `WF-699` C4 ("`PIN_NOT_APPROVED` — the windscreen burning-cost model is still `review`") reachable? FR-20 says maturity is "Enforced at transition time" (`00:231`). If A-1's approval refuses a structure whose component is below `approved`, no approved structure ever has a component in `review`, and C4 can only be shown on a structure that is itself unapproved (refused one step earlier, on the structure) | (a) compile checks components anyway (this slice, items 1–2), and the C4 beat is shown in tests only; `WF-699` C4 gets a dated note naming what the journey can show; (b) A-1 does not check components at approval, so C4 is reachable as written; (c) C4 is shown on a component that became `superseded` after the structure's approval, which compile refuses as it refuses a superseded direct model pin (`_APPROVED_OR_BETTER`, `compile.py:404`) | **(a)**, with A-1's answer read first. (b) breaks FR-20's "at transition time". (c) is reachable but is not C4's text, and whether approving a successor supersedes a model is not read here. Compile's check is needed under every option: it is FR-240's clause and defence in depth | decision-maker, after A-1's plan states its approval check | A-4's demo script, not this slice's tasks |
| **DP-A3-5** | The unit of a component's prediction. The handler's convention assumes a model predicts on the money-minor scale (`runtime.py:518-522`). A frequency model predicts a count, a severity model an amount per claim; their product is minor units only if severity is fitted on minor units | (a) keep the convention, stated: a `severity_model` and a `burning_cost_model` predict minor units; a frequency model predicts an expected count for the row's own exposure (`PerilPrediction`'s docstring, `perils.py:65-68`); the A-4 demo fits its severity GLM on minor units; (b) declare a unit on the model; (c) convert at the handler by a declared factor | **(a)** for P2: it is the convention every `model_call` already uses, and (b) and (c) are schema changes to `02` with no requirement asking for them yet. The ruling should say so, so A-4 fits severity on minor units | decision-maker | A-4 (the severity fit); this slice states it in the handler's docstring |
| **DP-A3-6** | Measure the score latency of a peril `model_call`? NFR-489's budget is stated "with one `exact` GBM call" (`03:1330`); a peril call makes two predictions per `frequency_severity` peril and one per `burning_cost` peril | (a) record a p50/p99 with `scripts/bench-rating.py --peril-structure` (new flag), no budget asserted, in a quiet window; (b) no measurement; A-2's GLM measurement stands alone | **(a).** CLAUDE.md §13: NFRs are measured, not asserted, and a peril quote is the hot path the exit demo shows. Recording without asserting keeps the result honest until `03` states a budget for it | decision-maker | item 13 |

### Spec texts (proposed for the ruling; applied verbatim in Task 6)

**T1** (DP-A3-1 (c), DP-A3-2 (a)), a dated amendment appended to the `model_call` row's
description cell (`03-rating-engine.md:100`):

> *(Amended <date>, A-3.)* On a Peril Structure, an `exact` step yields the structure's risk
> premium (`02` FR-188), each peril's large-loss treatment applied before the sum (FR-189),
> rounded once to `money_minor`, and declares exactly one produced name; a step that declares
> more is refused at compile. Per-peril outputs (FR-249) are carried by <owner>. A structure
> with a `separate_model` peril is refused at compile with `LOSS_TREATMENT_UNIMPLEMENTED`.

**T2** (DP-A3-3 (a)), a dated amendment appended to the FR-240 cell (`:137`), after PL 9649's
T1:

> *(Amended <date>, A-3.)* **A pinned Peril Structure's component models are references of the
> Rating Version**: each is resolved, must be `approved` or better (FR-20), and is reached by the
> custom-objective and `control`-factor clauses above as a pinned model is. The "known gap" named
> in the 2026-10-05 amendment is closed.

**T3** (DP-A3-2 (a)), a dated note after `LOSS_TREATMENT_UNIMPLEMENTED` is added to `03` §5.1's
owned-code list (`:933`): *(re-raised <date> from `02`: **422** at bundle compile (FR-240) for a
pinned Peril Structure with a `separate_model` peril; the message names the structure and the
peril)*.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Activation needs 1–4 hold: `git log --oneline origin/main` shows PL-1429's,
  PL 9649's, A-1's and A-2's merges. Record each SHA.
- [ ] **Step 2:** Re-read `compile_bundle`, `_model_call_handler` and `_load_boosters` **by
  symbol** on the merged tree; every line cite in this plan is re-anchored in the ledger.
- [ ] **Step 3:** Record A-2's shapes: how a GLM's Factors, Bandings and Groupings reach the
  Bundle (a `_Resolver` `model`-branch payload, or a compile-time embedding), and the name and
  signature of the per-kind prediction A-2 leaves in `_model_call_handler`. This slice calls
  that dispatch; it never writes a second one (`score_fitted`'s docstring, `predict.py:419-426`:
  "a second copy of a dispatch is a second place for the kinds to diverge").
- [ ] **Step 4:** Record A-1's approval check: does it refuse a structure whose component is
  below `approved`? Quote the line. This is DP-A3-4's input.
- [ ] **Step 5:** `gh pr list --state open`; re-read anything that edits `compile_bundle`,
  `_model_call_handler`, `_load_boosters` or the FR-240 cell. **STOP** if one is in flight and
  not named in the dispatch record.

### Task 1: The reds (Acceptance 1–6, 8–10)

**Files:** Create `packages/pricing-core/tests/test_rating_peril_scoring.py`.

- [ ] **Step 1: The fixture.** A structure payload built with
  `model_schema.PerilStructure` and dumped with `model_dump(mode="json")`: peril `AD`,
  `method=PerilMethod.FREQUENCY_SEVERITY`, `frequency_model="model:ad-freq@1"`,
  `severity_model="model:ad-sev@1"`, `large_loss=LargeLossTreatment(kind=LargeLossKind.NONE)`;
  peril `WS`, `method=PerilMethod.BURNING_COST`, `burning_cost_model="model:ws-bc@1"`.
  `PerilCode` is the pattern `^[A-Z][A-Z0-9_]{0,31}$` (`model_schema/perils.py:70`), so `AD` and
  `WS` are valid. Three GBM payloads in `_gbm_model_payload`'s shape, each
  with its own trained booster. A `FakeResolver` (`test_rating_compile_bundle.py:92`) over
  these plus an algorithm whose `s_rp` step carries `peril_structure_ref` and one produced name,
  and a version whose `pins.models` is `["peril_structure:motor-perils@1"]`.
- [ ] **Step 2:** Write items 1–6, 8 and 9 as specified in §"Acceptance Standard", each with its
  `req` markers from §"Scope". Item 4 waits on Task 0 Step 3's shape.
- [ ] **Step 3:** Run the module. Expected, per item: 1 `AssertionError` (missing component key);
  2, 8, 9 `Failed: DID NOT RAISE`; 3–6 `RuntimeError` containing `Failed to run custom node
  handler`. Any other cause is a plan defect: STOP and report.
- [ ] **Step 4:** Commit (red): `test: A-3 — a peril structure is neither resolved nor scored (FR-188, FR-240)`.

### Task 2: Compile resolves and checks the components (Acceptance 1, 2, 7, 8, 9)

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/compile.py`.

- [ ] **Step 1:** Add `_resolve_peril_components(structure_ref, payload, resolver)`. It
  validates `payload` with `PerilStructure.model_validate`, and for each peril in order and each
  of `frequency_model`, `severity_model`, `burning_cost_model` that is set, calls
  `await resolver.resolve(ref)` once per distinct ref, and refuses with `_raise_named(
  "PIN_NOT_APPROVED", …)` when `resolved.status not in _APPROVED_OR_BETTER`, naming the
  component, the structure and the peril and ending `(FR-20)`. Under DP-A3-2 (a) it first refuses
  a `separate_model` peril with `LOSS_TREATMENT_UNIMPLEMENTED`. It returns
  `dict[str, ResolvedArtifact]`.
- [ ] **Step 2:** In `compile_bundle`, after the pin loop, for each ref in `version.pins.models`
  with `ref.type == "peril_structure"`, call it and add each component's payload to `payloads`
  under `str(ref)`. Never resolve a ref twice (the RL-859 note in `compile_bundle`); a component
  that is also pinned directly reuses the pin loop's result. `bundle_hash` is not changed.
- [ ] **Step 3:** Under DP-A3-1 (c), add `_check_peril_model_calls(algorithm)`: a
  `RatingModelCallStep` with `peril_structure_ref` whose `produces` lists more than one name is
  refused with the ruled code, naming the step and the names. Call it beside
  `check_step_refs_pinned`.
- [ ] **Step 4:** Run the module: items 1, 2, 7, 8, 9 green; 3–6 still red by their cause. Commit:
  `feat: compile resolves and maturity-checks a peril structure's components (FR-240, FR-20)`.

### Task 3: The transitive checks reach the components (Acceptance 10; only under DP-A3-3 (a))

**Files:** Modify `compile.py`; the test module.

- [ ] **Step 1:** Write item 10's two tests on PL 9649's fixtures as merged; run; expected
  `Failed: DID NOT RAISE`. Commit (red).
- [ ] **Step 2:** Pass the components from Task 2 to PL 9649's `_check_reachable_objectives` and
  `_check_control_factor_model_calls`, in their own calling convention as merged (Task 0 Step 2).
  Run; green. Commit: `fix: FR-240's transitive clauses reach a peril structure's components`.

### Task 4: The runtime assembles the risk premium (Acceptance 3–6)

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/runtime.py`.

- [ ] **Step 1:** `_load_boosters`: for a step with `peril_structure_ref`, validate the
  structure's payload and load each GBM component's booster under the component's `str(ref)`,
  once, with `nthread=1`, as for a direct pin (`runtime.py:586-621`).
- [ ] **Step 2:** Add `_score_peril_structure(step, structure, payloads, boosters, feature_row,
  context) -> int`: for each peril, predict each set component through A-2's per-kind dispatch
  (Task 0 Step 3) on the one-row frame, unrounded; build `PerilPrediction(peril=…, method=…,
  frequency=…, severity=…, burning_cost=…, large_loss=peril.large_loss)` with one-element
  `float64` arrays; call `assemble_risk_premium`; return `round(float(frame["risk_premium"][0]))`.
- [ ] **Step 3:** In `_model_call_handler`, branch on `step.peril_structure_ref is not None`
  **before** `payload["fit_result"]` (`:540`). A `ModellingError` or `PredictionError` from the
  assembly becomes `_model_call_failure(step, f"{exc.code}: {exc}")`, never a raise.
- [ ] **Step 4:** Update the handler's docstring: the peril branch, and DP-A3-5's unit statement
  as ruled.
- [ ] **Step 5:** Run the module, then `test_rating_runtime.py` and `test_perils.py` (item 12).
  Commit: `feat: a peril model_call scores the assembled risk premium (FR-188, FR-189, NFR-491)`.

### Task 5: Over HTTP (Acceptance 11)

**Files:** Create `backend/tests/test_rating_peril_scoring_api.py`.

- [ ] **Step 1:** Mirror A-1's own peril approval test and PL-1429's create-route test for the
  fixtures (README rule 3: do not reinvent the module's fixtures). Three approved component
  models, a structure taken to `approved` through A-1's path, an algorithm whose `s_rp` names the
  structure, a version through `POST /api/v1/rating-versions`, a compile, a score.
- [ ] **Step 2:** Run it against the pre-Task-2 tree (a scratch checkout of Task 1's red commit)
  and record the cause; then on the slice head, green. Commit.

### Task 6: The spec texts, verbatim from the ruling

- [ ] Apply T1–T3 exactly as the minted ruling words them, each in its own hunk. If the ruling
  carries no text for a DP, write none. `python3 scripts/audit-docs.py`: no new failure.

### Task 7: The gate, the bench and the ledger

- [ ] **Step 1 (DP-A3-6 (a) only):** add the `--peril-structure` fixture to
  `scripts/bench-rating.py`, then check `pgrep -af 'pytest|vitest|flock'` and both gate slots;
  run it only when neither slot is held; record item 13.
- [ ] **Step 2:** The full two-half gate (item 14) through the gate-runner, in a held gate slot,
  one gate at a time (RL 9620). Record each rc and the tree.
- [ ] **Step 3:** In the slice's `LG-` ledger: Task 0's records, every red with its printed line
  (paraphrase any line naming an undefined id, README rule 2), item 12's pass counts, item 13,
  and `git diff --stat origin/main...HEAD` against §"Write set" (item 15).

## Hand-off

1. The lead mints PL-1465 and SL-1466 at their merge turn, and dispatches only after
   §"Activation needs" hold, in a separate activation PR.
2. **A-4** (the demo) consumes this slice: its B4 step names the structure with one produced
   name (DP-A3-1 (c)); its severity GLM is fitted on minor units (DP-A3-5 (a)); its C4 beat
   follows DP-A3-4's ruling. A-4 also waits on the double-count ruling (the maintainer's item 4).
3. **FR-249's per-peril outputs**, under DP-A3-1 (c), go to the owner the ruling names; the
   planner does not pick one.
4. When this slice merges, PL 9649's T1 gap sentence is superseded by T2 (DP-A3-3 (a)); the
   auditor records it at this slice's close.

## Self-review

1. **Coverage of the maintainer's A-3 clause, part by part.** "compile resolves … the component
   models": Task 2 Steps 1–2, item 1. "and maturity-checks the component models": Task 2 Step 1,
   item 2. "the runtime calls assemble_risk_premium": Task 4 Step 2, items 3–5. "fixing the bare
   KeyError on payload["fit_result"] at runtime.py:540": Task 4 Step 3, item 3's red cause.
   "WF-699 C4 becomes reachable" (the brief): items 1–2 make the compile outcome real; whether
   the journey can reach it is DP-A3-4, stated rather than assumed.
2. **Every design choice the clause leaves open is a DP with an owner**: the outputs
   (DP-A3-1), `separate_model` (DP-A3-2), PL 9649's gap (DP-A3-3), C4 (DP-A3-4), the unit
   (DP-A3-5), the measurement (DP-A3-6). No spec text is written without a ruling (Task 6).
3. **Repository literals checked at `137bc817`:** `_model_call_handler` `runtime.py:512`, the
   `fit_result` read `:540`, the GBM branch `:549-567`, the refusal `:568-579`, the produced-name
   write `:581`, `_load_boosters` `:586`, `_model_call_failure` `:94`; `compile_bundle`
   `compile.py:573`, the pin loop `:618-631`, `_APPROVED_OR_BETTER` `:404`, `ResolvedArtifact`
   `:434`, `ArtifactResolver` `:444`, `bundle_hash` `:522`; `PerilComponent` and its validator
   `model_schema/perils.py:214-258`, `PerilStructure` `:377-389`, `LargeLossKind` `:80-86`;
   `assemble_risk_premium` `modelling/perils.py:104`, `PerilPrediction` `:62-75`; `score_fitted`
   `predict.py:406`; `ModelStatus` `modelling.py:1975-1981`; `score_one` `score.py:876`; the
   reconciliation's composition `model_handlers.py:1437-1486`; the test helpers
   `test_rating_runtime.py:30, 42, 72, 171, 191` and `test_rating_compile_bundle.py:25, 69, 92,
   107`; `03:100, 108, 134, 137, 154, 156, 255, 268, 1330, 1332`; `02:294-297, 304`; `00:231`.
   `PerilCode` `model_schema/perils.py:70` (a pattern; `AD` and `WS` match it).
4. **What was not executed.** No test or sample was run; Task 0 at planning time ran two
   `git grep`s. A-1's and A-2's shapes are not known at planning (neither was pushed), so
   Task 0 Steps 3–4 read them before any code. A sample that does not run as written is a plan
   defect to report, not to work around.
5. **Type consistency.** `_resolve_peril_components` returns `dict[str, ResolvedArtifact]`
   (Task 2 Step 1) and Task 2 Step 2 and Task 3 Step 2 consume it; `_score_peril_structure`
   returns `int` (Task 4 Step 2), the type the handler's GBM branch already writes (`:567`).
