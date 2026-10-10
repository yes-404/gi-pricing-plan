---
id: RL-1459
family: ruling
title: WK-1178 Option A, A-3 and A-4 decision points — a Peril Structure model_call yields one produced name, separate_model is refused at compile, A-3 closes PL 9649's FR-240 component gap, WF-699 C4 is noted and shown live on a superseded component, the reconciliation tolerance is 0.05; FR-249 carried as OQ-1460
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-06              # the mint date (check 31); ruled 2026-10-05
owner: decision-maker
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: [RL-1580]
relates: [WF-699, FR-20, FR-188, FR-189, FR-190, FR-222, FR-226, FR-227, FR-240, FR-249, FR-255, NFR-489]
---

# RL-1459 — A-3 (PL-1465) and A-4 (PL 9593) decision points, ruled

## How this was ruled

- **Filed under working id 9571 (minted as RL-1459), reserved by the lead (team-lead) on 2026-10-05. The question
  it raises, working id OQ 9570, is minted as OQ-1460.** At the mint, on 2026-10-06 in the G2 chain batch,
  the working ids of this record and of the three rows this commit adds were replaced by their minted ids,
  as were the other working ids named here that mint with it (PL-1465, SL-1466, PL-1461, PL-1464, FD-1456).
  PL 9593, SL 9594, PL 9649 and RL 9588 are re-pointed when each mints. Nothing else in the
  texts below is a placeholder, except `<date>` and `<RL>` inside the T- and P-texts, which
  the applying slice fills.
- **The decisions are not this record's.** They are the maintainer's (by delegation), in the
  entry "2026-10-05 17:08:35 BST — A-3 / A-4 DP memo (handover/dp-memo-a3-a4-2026-10-05.md)
  RULED; the reconciliation TOLERANCE set" (`channel/to-lead.md`). Its body, verbatim:

```text
1. DP-A3-3: (a), the scope growth ACCEPTED (+0.25 executor-day, A-3 now ~1.25/1.75/2.5, estimates). A-1 excludes components, so without it PL 9649's T1 "FD 9995 owns that gap" would point at a fix that never closes it.
2. FR-249's per-peril map (PL-1286 puts it in WK-675 S6, which has no backend producer under DP-A3-1 (c)): a NEW 03 OQ, owner WK-1178, decided after G2: a dated carry. WK-675 S6's FR-249 limb is carried with it (recorded in S6's dispatch record when S6 is planned), so S6 does not build a view with no producer.
3. RECONCILIATION TOLERANCE (FR-190, 02 :296: "total modelled burning cost reconciles to observed burning cost within a declared tolerance on the holdout"; stored as a fractional tolerance on |ratio − 1|, model_schema/perils.py:308-309, quantum 0.000001): the demo structure DECLARES tolerance = 0.05 (5%). Because large loss is UNCAPPED (DP-A4-3 (x)), the holdout burning cost is volatile, so the value is CHECKED before the demo depends on it: the probe runs at the DEMO'S ROW COUNT (the full freMTPL2 portfolio, not only --rows 20000), and the measured ratio is recorded verbatim in the ledger. If |ratio − 1| > 0.05: STOP to me with the measured ratio. Then I choose between capping large loss with a loading (a modelling change) and a wider tolerance justified by the measured holdout variance. Never silently widened.
4. DP-A3-1: (c), one produced name, with the code BUNDLE_COMPILE_FAILED (03-owned, the compile default), not VALIDATION_FAILED.
5. DP-A3-2: (a), re-justified by the NEW FACT: the platform already refuses separate_model at reconcile (409 LOSS_TREATMENT_UNIMPLEMENTED, platform/perils.py request_reconciliation), and review is reachable only from reconciled, so no approved structure carries one. A-3's handler maps assemble_risk_premium's ModellingError to _model_call_failure.
6. DP-A3-4: (a), with the WF-699 C4 NOTE text as the memo drafts it. The LIVE C4 demonstration uses the memo's fallback (c): approve a LATER version of a component model (modelling.py _supersede_earlier_versions supersedes the earlier one), then compile the structure pinned to the superseded version → refused, as C4 shows. That keeps C4 in the demo without breaking A-1's approval rule.
7. DP-A3-5: (a). The frequency GLM's offset (exposure_years) comes through B4's feature_map, else MODEL_OFFSET_MISSING: consistent with my A-2 DP-3 (17:03:45).
8. DP-A3-6: (a), record only, run only when no gate is running.
The DM's own: DP-A4-2 (c) and DP-A4-3's factors (a) (7 = 3 continuous + 4 categorical, verified): noted.
A-1 BUG (to planner-a12fold): `_require_approved_components` lists "approved, live or retired", but `live` and `retired` are not ModelStatus values (copied from compile's cross-type _APPROVED_OR_BETTER). Fix: use ModelStatus's own approved set, with a red test (a model in a non-existent status string never passes). Good catch.
dm-a34 files the A-3/A-4 RL now (reserve the id); T2's anchor is re-derived after #1152 merges.
```

- **Two decisions are the lead's (team-lead).** The entry records them as "noted":
  DP-A4-2 (c), and DP-A4-3's severity factors (a). The lead's message of 2026-10-05 (after
  17:11:34 BST) reads: "The lead decided DP-A4-2 (c) (the seed creates and approves the
  structure via A-1's workflow service; the journey does one GET) and DP-A4-3 factors (a)
  (7)." That is a message, so this record cites the ruling entry above, which notes both.
- **Rulings this record carries and does not make:**
  - DP-A4-2's condition and DP-A4-3's large-loss treatment. These are in the entry
    "2026-10-05 17:01:30 BST — Discrepancy CLOSED; PR triage accepted (4 closes, each after
    its absorber merges); A-3/A-4/S3 rulings; the to_wire defect: REPRODUCE NOW", verbatim:
    "DP-A4-2 (the seed creates the structure; the journey does one GET over HTTP): ACCEPTED,
    on condition that the structure is APPROVED through the approval workflow's service (A-1's
    path), never by SQL, and that the journey's B4 model_call and C1 pin run over HTTP (G2).
    DP-A4-3: LARGE LOSS is mine: UNCAPPED for the P2 demo, labelled in the plan and the script
    as a simplification (no large-loss loading), with the STOP if reconciliation fails as
    proposed."
  - The rounding root. It is in the entry "2026-10-05 17:02:50 BST — A-1/A-2 plans and batch
    5 noted; the model_call ROUNDING is fixed IN A-2 by declared result type, not worked
    around in A-3", verbatim: "A-3 composes frequency × severity on Decimals and rounds once,
    at the money step."
- **The correction that governs items 2, 6 and 7.** It is in the entry "2026-10-05 17:12:40 BST — CORRECTION to my 17:02:50 rounding ruling: OPTION (B); A-2 gains the model-schema field; C4 stays (c); FR-249 carry text accepted"
  (`channel/to-lead.md`). Its three relevant paragraphs, verbatim:

```text
RULING: OPTION (B). A model_call's output is ALWAYS an exact Decimal, never rounded at the model_call. ALL rounding stays on the output step, as FR-226 already says (no FR-226 amendment). RatingModelCallStep gains `result_type: RatingResultType` as a TYPE only (decimal | money_minor, for compile's FR-227 type checks; money_minor is a type label, not a rounding). Red first: a frequency GLM model_call returns the exact Decimal (~0.07, today 0); a money_minor-typed model_call feeding a non-money step is refused at compile as a type mismatch; the output step rounds once.
C4: STAYS at my ruled fallback (c) (a superseded component version, refused at compile). S1 (the seed leaves the AD severity GLM in review, so C5 approves and recompiles inside the journey) is NOT taken: it adds about +0.25 day and moves an approval into the scripted journey for no G2 gain. The RL files (c).
FR-249 carry text for RL 9571 / OQ 9570: ACCEPTED (owner WK-1178 now, re-decided at the Fri 9 Oct checkpoint; if no slice fits before 4 Nov it carries into P3, listed in the P2 closure; WK-675 S6 shows per-peril output as absent meanwhile).
```

  The 17:02:50 rounding sentence quoted above is **corrected** by this entry: a `model_call`'s
  output is always an exact `Decimal`, and all rounding stays on the output step.
- **The options memo** is `handover/dp-memo-a3-a4-2026-10-05.md` (local, dm-a34). Revision 1
  was written from 17:05:56 BST, which is the revision the entry rules. Revision 2 was
  written from 17:09:36 BST. This record carries the memo's texts and decides nothing
  beyond the rulings above.
- **One text is adapted to fit the ruling, and the adaptation is disclosed.** Item 6 rules
  "(a), with the WF-699 C4 NOTE text as the memo drafts it" **and** a LIVE C4 demonstration
  by fallback (c). Revision 1's note ends "This step is shown in tests, not in the scripted
  journey." That sentence contradicts the live demonstration the same item orders. T5 below
  replaces it with a sentence that states item 6's fallback (c). No other word of the note
  changes.

## Locators — read at `4d3be141` (origin/main at filing) unless a PR head is named

| What | Where | Says |
|---|---|---|
| Every produced name gets one value | `packages/pricing-core/src/pricing_core/rating/runtime.py`, `_model_call_handler`, the inner `handler`'s final `return` | `{"output": {str(name): value for name in _as_list(step.produces)}}` |
| The provisional rounding | same function | `value: int = round(prediction)`, under the docstring's "documented, provisional convention" |
| A peril payload has no `fit_result` | same function | `fit_result = dict(payload["fit_result"])` |
| The `03` example produces two names | `docs/specs/03-rating-engine.md` §4, the algorithm example | `"produces": ["risk_premium_minor", "peril_risk_premium"]`, the second declared `map<string, money_minor>` |
| No map type in the engine | `git grep -n 'map<' origin/main -- packages/model-schema/src/model_schema/rating.py packages/pricing-core/src/pricing_core/rating` | no output |
| `separate_model` refused in `pricing-core` | `pricing_core/modelling/perils.py`, `_restore` | `ModellingError("LOSS_TREATMENT_UNIMPLEMENTED", …)` |
| `separate_model` refused before reconcile | `backend/src/app/platform/perils.py`, `request_reconciliation` | `PlatformError("LOSS_TREATMENT_UNIMPLEMENTED", …, 409, …)` |
| Review only after reconcile | `backend/src/app/platform/perils.py`, module docstring | "**`review` is reachable only from `reconciled`.**" |
| Compile refusals are 422 | `backend/src/app/platform/rating_versions.py`, the `compile_bundle` call | a `CODE: detail` `ValueError` becomes `PlatformError(code, …, 422, detail)`; unnamed text becomes `BUNDLE_COMPILE_FAILED` |
| Compile's maturity floor | `packages/pricing-core/src/pricing_core/rating/compile.py`, `_APPROVED_OR_BETTER` | `frozenset({"approved", "live", "retired"})`, no `superseded` |
| A model is superseded on its successor's approval | `backend/src/app/platform/modelling.py`, `_supersede_earlier_versions` | "`approved → superseded` for every earlier approved version of the family" |
| FR-240's known gap | PL 9649 (#1152 @`df8ba756`), §"Spec texts" T1 | "**Known gap:** a peril structure's models are not reached, because a peril structure cannot be resolved at compile; FD 9995 owns that gap, and this clause reaches them when it is fixed." |
| A-1 excludes components | PL-1461 (#1177 @`08e53e88`), §"Scope" | "resolving and maturity-checking a structure's **component models at compile** … (both A-3 …)" |
| FR-249 | `03` §3, FR-249 | "Per-peril risk premium components are available as outputs, since monitoring (`05`) and reinsurance analysis both need them." |
| FR-249's view | `docs/plans/PL-01286-wk-675-frontend-dag-designer-rate-table-editor-quote-sandbox-and-dislocation-views-map-plan.md`, row S6 | "the per-peril risk-premium components among the outputs (FR-249)" |
| The tolerance | `packages/model-schema/src/model_schema/perils.py`, `Reconciliation.tolerance` and `TOLERANCE_QUANTUM` | "Declared fractional tolerance on \|ratio - 1\| (FR-190)."; `Decimal("0.000001")` |
| FR-190 | `docs/specs/02-modelling.md`, FR-190 | "total modelled burning cost reconciles to observed burning cost within a declared tolerance on the holdout" |
| WF-699 C4 | `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`, row C4 | "First attempt fails: `PIN_NOT_APPROVED` — the windscreen burning-cost model is still `review`." |

## Ruled

1. **DP-A3-3: (a). A-3 closes PL 9649's FR-240 gap for a structure's component models.**
   Once A-3 resolves the components, it passes them to PL 9649's custom-objective and
   `control`-factor checks. This is scope growth over the sizing memo's A-3 row, accepted
   at +0.25 executor-day. A-3 becomes about 1.25 / 1.75 / 2.5 executor-days; these are
   estimates.
2. **FR-249 is carried as a new `03` question, `OQ-1460`, with the carry text accepted at
   17:12:40.** The owner is WK-1178 now, and it is **re-decided at the Fri 2026-10-09
   checkpoint**. If no slice fits before the Wed 2026-11-04 code freeze, it carries into Phase
   3 and the P2 phase closure record lists it (CLAUDE.md §14). WK-675 S6 shows per-peril
   output as absent meanwhile, and S6's FR-249 limb is carried with it. S6's dispatch record records the carry when
   S6 is planned, so S6 does not build a view that has no producer. This commit raises the
   question in `03` §10, in `docs/open-questions.md` and in `docs/roadmap.md` §10.
3. **The reconciliation tolerance is 0.05 on |ratio − 1| (FR-190).** A-4's demo seed requests
   the AD structure's reconciliation with `tolerance = 0.05`, which is stored as
   `Reconciliation.tolerance`. Large loss is uncapped (the 17:01:30 ruling). So A-4's Task 0
   probe runs at **the demo's own row count (the full freMTPL2 portfolio)**, and it can also
   run on `--rows 20000`. The measured ratio is recorded verbatim in A-4's ledger. **If
   |ratio − 1| > 0.05, STOP to the maintainer (by delegation) with the measured ratio.** The
   maintainer then chooses between capping large loss with a loading and a wider tolerance
   justified by the measured holdout variance. The tolerance is never widened silently.
4. **DP-A3-1: (c).** A `model_call` on a Peril Structure declares exactly one produced name,
   which receives the structure's risk premium. A step that declares more is refused at
   compile with `BUNDLE_COMPILE_FAILED` (`03`-owned, 422), and the message names the step and
   the extra names. The code is not `VALIDATION_FAILED`.
5. **DP-A3-2: (a).** Compile refuses a pinned Peril Structure that has a `separate_model`
   peril. The refusal raises `LOSS_TREATMENT_UNIMPLEMENTED` (re-raised from `02`, 422) and
   names the structure and the peril. On the platform this is defence in depth, because
   `request_reconciliation` refuses such a structure with a 409 and `review` is reachable
   only from `reconciled`. Compile's refusal covers `pricing-core`'s standalone callers.
   **A-3's handler maps a `ModellingError` raised in `assemble_risk_premium` to
   `_model_call_failure`** (FR-255), never to an unhandled exception.
6. **DP-A3-4: (a), and C4 is shown live by fallback (c).**
   - Compile checks every component of a pinned structure (FR-240, FR-20), as A-3's plan
     builds it. WF-699 C4 gets the dated note T5.
   - **The live C4 beat:** a component model's later version is approved, which supersedes
     the earlier version (`_supersede_earlier_versions`). A Rating Version pinning a
     structure that is still `approved` but composed over the superseded version then
     compiles to `PIN_NOT_APPROVED`, naming the component.
   - This keeps C4 in the demo without breaking A-1's approval rule (PL-1461 DP-1 (a),
     accepted 17:02:50).
   - A-4 builds the beat under P-text P4's constraint.
   - S1 (approving inside the journey) was offered and **not taken** (17:12:40).
7. **DP-A3-5: (a), on the rounding root as corrected at 17:12:40 (option (B)).**
   - A `model_call`'s output is always an exact `Decimal`, never rounded at the
     `model_call`. All rounding stays on the output step (FR-226, unamended). A-2 adds
     `RatingModelCallStep.result_type` as a type label only (`decimal` | `money_minor`), for
     compile's FR-227 checks.
   - A-3 predicts each component at full precision. It composes `frequency × severity` per
     peril, or `burning_cost`, applies FR-189's treatment, and sums (FR-188), all on
     `Decimal`. Nothing is rounded until the output step's single declared rounding.
   - The severity GLM is fitted on `claim_amount_minor`, so it predicts an amount per claim
     in minor units, which enters the composition unrounded.
   - The frequency GLM's offset (`exposure_years`) comes from the quote through B4's
     `feature_map`. Without it the call fails `MODEL_OFFSET_MISSING`, which reaches the
     caller as a `model_call` failure (A-2 DP-3, 17:03:45).
8. **DP-A3-6: (a).** The score latency of a peril `model_call` is recorded only: p50 and p99
   by `scripts/bench-rating.py --peril-structure`, with no budget asserted. It runs only when
   no gate is running.
9. **The lead's (noted in the entry):**
   - **DP-A4-2 (c)**, on the 17:01:30 condition. The seed creates the structure, reconciles
     it, and approves it through A-1's workflow service, never by SQL. The journey does one
     `GET /api/v1/peril-structures/{id}` and runs B4's `model_call` and C1's pin over HTTP.
   - **DP-A4-3's severity factors (a):** the same 7 as the frequency GLM, 3 continuous and 4
     categorical (`examples/fremtpl2/model.py`, `CONTINUOUS_FACTORS` and
     `CATEGORICAL_FACTORS`).
   - **Large loss: uncapped**, labelled in the plan and the script as a simplification (no
     large-loss loading).
10. **DP-A3-7: (a), the union.** *(Added before the mint, 2026-10-06, on the lead's
    decision that this record carries DP-A3-7's union half.)*
    - **The question** (PL-1465, #1174 @`2404ac86`, delta 1 item 4): one
      `feature_map` feeds every component of a Peril Structure, but A-2's check compares a
      map with one Model. Which set is a value checked against: (a) the union, or (b) every
      component?
    - **The decision is the maintainer's (by delegation)**, in the entry "2026-10-05
      18:44:45 BST — DP-A3-7 = (a) the UNION, with a per-component COMPLETENESS limb; A-1's
      needs put lane C on the G2 path" (`channel/to-lead.md`), item 1. Its union sentence,
      verbatim:

```text
DP-A3-7: (a). For the "this key is not a feature" test, a feature_map entry passes if AT LEAST ONE component model accepts it (one map feeds every component; the frequency GLM's exposure_years OFFSET, RL 9571 P3, is not a severity feature, and (b) would refuse A-4's ruled demo path).
```

    - **Option taken: (a).** For the "this key is not a feature" test, a `feature_map` entry
      passes if at least one component model accepts it. An entry no component accepts is
      refused.
    - **The reason, as the entry gives it:** one map feeds every component. The frequency
      GLM's `exposure_years` offset (P3 below) is not a severity feature, so (b) would
      refuse A-4's ruled demo path.
    - The per-component completeness limb of the same entry is recorded in RL 9491 (working
      id, #1214), not here.

**Settled outside this record.** The `model_call` result-type mechanism is A-2's (#1178), as
ruled at 17:12:40, option (B). Item 7 depends on it and restates nothing beyond it.

## The spec texts

Each text gives the file, the find string, and the replacement. Each find string occurs
**exactly once** at `4d3be141`, by `grep -c -F`. Exception: T2's anchor is re-derived after
#1152 merges, as the entry's last line says ("T2's anchor is re-derived after #1152 merges"). **T1–T4 are applied by A-3 (SL-1466 / PL-1465, WK-1178)** in one commit with its
code, per `CLAUDE.md` §2. **T5 is applied by A-4 (SL 9594 / PL 9593)** with its journey.
**T6–T8, the `OQ-1460` rows, are applied in this commit.**

**T1 — `03` §3.2, the `model_call` row (items 4, 5).** Find:

```text
| `model_call` | Invokes a pinned Model or Peril Structure and yields its prediction(s) |
```

Replace with:

```text
| `model_call` | Invokes a pinned Model or Peril Structure and yields its prediction(s). *(Amended <date>, <RL>: on a Peril Structure, an `exact` step yields the structure's risk premium (`02` FR-188), each peril's large-loss treatment applied before the sum (FR-189), composed on exact decimals and never rounded at the step; the output step rounds once (FR-226). It declares exactly one produced name; a step that declares more is refused at compile with `BUNDLE_COMPILE_FAILED`, naming the step. A structure with a `separate_model` peril is refused at compile with `LOSS_TREATMENT_UNIMPLEMENTED`. Per-peril outputs (FR-249) are carried by `OQ-1460`.)* |
```

**T2 — `03` FR-240, appended to the cell after PL 9649's T1 (item 1).** The find string is
the last sentence of PL 9649's T1 **as minted**, re-derived at A-3's Task 0 after #1152 merges.
Until then, the cell ends at `4d3be141` with `The message names the step and the rung.)* |`
(`grep -c -F` = 1). Insert, before the closing ` |`:

```text
 *(Amended <date>, <RL>.)* **A pinned Peril Structure's component models are references of the Rating Version**: each is resolved, must be `approved` or better (FR-20), and is reached by the custom-objective and `control`-factor clauses above as a pinned model is. The "known gap" named in <PL 9649's RL>'s amendment is closed by <A-3's merge, FD 9995's minted id>.
```

**T3 — `03` §5.1, the owned-code list (item 5).** Find:

```text
`EVIDENCE_INCOMPLETE` (re-raised from `06`), 
```

Replace with:

```text
`EVIDENCE_INCOMPLETE` (re-raised from `06`), `LOSS_TREATMENT_UNIMPLEMENTED` *(re-raised <date>, <RL>, from `02`: **422** at bundle compile (FR-240) for a pinned Peril Structure with a `separate_model` peril, naming the structure and the peril. The platform refuses such a structure earlier, 409 at reconcile (`02` FR-190), so this refusal reaches only a `pricing-core` caller with its own resolver)*, 
```

(Both strings end with one space, as the list's separator does.)

**T4 — `03` FR-249 (item 2).** Find:

```text
since monitoring (`05`) and reinsurance analysis both need them. |
```

Replace with:

```text
since monitoring (`05`) and reinsurance analysis both need them. *(Carried <date>, <RL>: a Peril Structure `model_call` yields one produced name in P2. Per-peril components are `OQ-1460`'s, owner WK-1178, re-decided at the 2026-10-09 checkpoint and carried into Phase 3 if no slice fits before the 2026-11-04 code freeze; WK-675 S6 shows them as absent meanwhile.)* |
```

**T5 — `WF-699` row C4 (item 6).** Find:

```text
| C4 | Worker | First attempt fails: `PIN_NOT_APPROVED` — the windscreen burning-cost model is still `review`. | `03` FR-240, FR-20 |
```

Replace with:

```text
| C4 | Worker | First attempt fails: `PIN_NOT_APPROVED` — the windscreen burning-cost model is still `review`. *(Note <date>, <RL>: a Peril Structure's approval refuses an unapproved component (`06` FR-363, <A-1's RL>), so on the precondition's `approved` structure this refusal cannot occur as written. Compile still checks every component (FR-240) and refuses one that has since been `superseded` by a later approval; the exit demo shows this step that way.)* | `03` FR-240, FR-20 |
```

**T6–T8 — `OQ-1460`, applied in this commit:**
- T6: `03` §10;
- T7: `docs/open-questions.md`, section RATE;
- T8: `docs/roadmap.md` §10, the row **Before Phase 3**, with a dated placement paragraph.

The question is: **Should a Peril Structure `model_call` carry per-peril risk-premium
components (FR-249), and in what shape?** The options are in T7.

## The plan texts (P-texts)

PL-1465 (#1174 @`7b3df510`) and PL 9593 (#1175 @`d15399e0`) are unmerged drafts. Their
planners apply these texts before each plan's first merge. Each plan's activation need ("the
ruling … merged and minted") then cites this record. Find strings: `grep -c -F` = 1 in each
plan at the head named.

**P1 — PL-1465, inserted after the line `## Decision points`:**

```text

**Ruled 2026-10-05 by <RL> (the maintainer's (by delegation) entry "2026-10-05 17:08:35 BST — A-3 / A-4 DP memo (handover/dp-memo-a3-a4-2026-10-05.md) RULED; the reconciliation TOLERANCE set").** DP-A3-1 (c), code `BUNDLE_COMPILE_FAILED`; DP-A3-2 (a), and Task 4 maps `assemble_risk_premium`'s `ModellingError` to `_model_call_failure`; DP-A3-3 (a), scope accepted, +0.25 executor-day; DP-A3-4 (a), C4 shown live by A-4 on a superseded component; DP-A3-5 (a), composed on exact `Decimal` and rounded only at the output step (17:12:40, option (B)), the frequency offset through the `feature_map`; DP-A3-6 (a), recorded only, run only when no gate is running. The table below records what was weighed; where it differs, the ruling governs. Spec texts T1–T4 are the ruling's, verbatim.
```

**P2 — PL-1465, its size.** Find:

```text
Medium: about one and a half executor days (sizing memo §2, A-3: 1 / 1.5 / 2).
```

Replace with:

```text
Medium: about one and three-quarter executor days (sizing memo §2, A-3: 1 / 1.5 / 2, plus DP-A3-3's +0.25 accepted by <RL>: 1.25 / 1.75 / 2.5, estimates).
```

**P3 — PL 9593, inserted after the line `## Decision points`:**

```text

**Ruled 2026-10-05 by <RL>.** DP-A4-1: `RL 9588` (B1). DP-A4-2 (c), the lead's, on the maintainer's (by delegation) 17:01:30 condition: the structure is approved through A-1's workflow service, never by SQL, and the journey's B4 `model_call` and C1 pin run over HTTP. DP-A4-3: the severity factors (a), the 7, the lead's; large loss **uncapped**, labelled in this plan and in the script as a simplification (no large-loss loading), the maintainer's. **Tolerance 0.05** on |ratio − 1|, requested by the seed. Task 0 Step 4's probe runs at the demo's full row count (and may also run at `--rows 20000`); the measured ratio is recorded verbatim in the ledger; if |ratio − 1| > 0.05, STOP to the maintainer with the ratio, never widened silently. The frequency GLM's `exposure_years` offset reaches B4 through its `feature_map`. WF-699 C4 is shown live under P4.
```

**P4 — PL 9593, Acceptance 5's C4 beat (item 6).** Find:

```text
`test_wf699_journey.py` asserts that a version pinning an **unapproved**
```

Replace that sentence (through "then passes once approved.") with:

```text
`test_wf699_journey.py` asserts C4 live by <RL> item 6: after a later version of a component model is approved (superseding the earlier one), a version pinning an `approved` structure composed over the superseded version fails compile with `PIN_NOT_APPROVED` naming the component. **That structure has its own slug**, not an earlier version of the demo structure's slug: approving a later version of a structure supersedes the earlier one (PL 9599 DP-2 (a)), and compile would then refuse the structure itself before reaching its components. The main path then pins the demo structure, composed over the current approved versions, and compiles.
```

## What it obliges

- **This commit:** this record, T6–T8 (the `OQ-1460` rows), and the regenerated
  `docs/INDEX.md`. No FR text, no WF-699 text, no plan, and no `model-schema` or code file is
  edited here.
- **A-3 (SL-1466 / PL-1465)** cites this record, applies P1 and P2 before its first merge,
  and applies T1–T4 with its code. T2's anchor is re-derived after #1152 merges.
- **A-4 (SL 9594 / PL 9593)** cites this record and `RL 9588`, applies P3 and P4 before its
  first merge, and applies T5 with its journey.
- **`OQ-1460`** is owned by WK-1178 and re-decided at the 2026-10-09 checkpoint (item 2). WK-675 S6's dispatch record carries its
  FR-249 limb.

## Acceptance — the violation that must become detectable

The violation: **a Peril Structure priced on a path that this record refuses.** A-3 and A-4
show each case failing on deliberately broken input.

- A peril `model_call` declaring two produced names compiles to `BUNDLE_COMPILE_FAILED`.
  With one name it compiles, and that name carries the structure's risk premium.
- A structure with a `separate_model` peril, handed to `compile_bundle` by a test resolver,
  is refused with `LOSS_TREATMENT_UNIMPLEMENTED` naming the structure and the peril.
- A component's unapproved custom objective, or a `control`-intent factor reached through a
  component, is refused at compile as a direct pin is (T2).
- A structure over a superseded component compiles to `PIN_NOT_APPROVED` naming the
  component (C4, live in the demo).
- A frequency component predicting about 0.07 contributes its exact value to the composed
  premium. With an integer rounding inserted before the composition, a test row fails.
- A-4's ledger carries the measured reconciliation ratio at the full row count, and a ratio
  outside 0.05 stops the slice rather than passing.

Drafted as working id 9571; minted as RL-1459 on 2026-10-06.
