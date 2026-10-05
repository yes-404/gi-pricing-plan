---
id: RL-9491
family: ruling
title: Compile refuses a model_call whose feature_map misses the pinned Model's required inputs, per component for a peril structure, with MODEL_CALL_FEATURE_MAP_INVALID; FR-240 takes the T-text
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-05              # the mint date (check 31); ruled 2026-10-05
owner: decision-maker
tree: ecbd1954d90b1faf0bd197174d720d90ad8f6c6d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-240, FR-222, FR-87, FR-255]
---

# Compile refuses a model_call whose feature_map misses the pinned Model's required inputs (FR-240)

## How this was ruled

- **Filed under working id 9491, reserved by the lead (team-lead) on 2026-10-05.** At the
  mint, `RL 9491` is re-pointed to its minted id. The other working ids named here (PL 9494,
  SL 9495, PL 9597) are re-pointed the same way at their own mints.
- **The decision is not this record's.** It is the maintainer's, by delegation, in the entry
  headed `2026-10-05 18:51:33 BST — Save-time completeness: DECIDED NOW as (b), completeness
  at COMPILE; no OQ; an RL with the FR-240 T-text; A-2's code reused` in
  `~/gi-pricing-plan.local/channel/to-lead.md`, quoted verbatim below. That entry orders this
  record ("ONE RL (a DM when a seat frees) with the FR-240 T-text"). This record carries the
  decision, drafts the T-text the entry describes, and records the serialisation.
- **Why there was a decision to make.** A read-only audit (auditor-complete, reported to the
  lead at 18:51:22 BST in `handover/mint-queue-2026-10-05.md`) found that no requirement asks
  for a `model_call`'s inputs to be complete before scoring. `03` FR-240's "all references
  resolvable" reads as artifact references; `02` FR-87 is fit-time. A `feature_map` that
  misses a Factor of its Model saves, compiles, and fails only per quote at score time, as
  `MODEL_CALL_FAILED`. The auditor reported liveness as none: no committed algorithm maps
  fewer than all of its Models' Factors. This record did not re-run that search. So this is
  a new requirement, and the spec comes first.

## The maintainer's entry, verbatim

> ## 2026-10-05 18:51:33 BST — Save-time completeness: DECIDED NOW as (b), completeness at COMPILE; no OQ; an RL with the FR-240 T-text; A-2's code reused
>
> Decided now rather than opened as an OQ: the trade-off is clear and G2's peril path (A-3/A-4, the exit demo) is exactly where a short-mapped GBM would fail per quote after deploy.
> (b): compile_bundle refuses a model_call step whose feature_map does not cover the PINNED model's required Factors (or its feature_order where it has none), using the existing resolver, before approval or deploy. Per component for a peril_structure_ref (17:44 DP-A3-7's per-component limb now has its home, at compile, not at save).
> CODE: REUSE MODEL_CALL_FEATURE_MAP_INVALID (A-2's code, once A-2 owns it in 03), naming the step and the missing features, not a new code: one fault, one code, at save (membership) and at compile (completeness). If A-2's code is not yet in 03's owned list when this RL is drafted, the RL cites A-2's T-text as the code's home and serialises after A-2.
> RECORDS: ONE RL (a DM when a seat frees) with the FR-240 T-text (a dated amendment: "all references resolvable" extended to a model_call's feature coverage of its pinned model), plus a note in PL 9597 (A-2) that its membership check is explicitly NOT a completeness check. The build is a small WK-1178 slice after A-2 (the same function family) and before A-4's demo path. Reserve the ids. (a), (c) and (d) are recorded as not taken.
> FD 9497's reservation released: correct (no requirement was broken; this is a new requirement, so it is spec first).

## Locators — read at `ecbd1954` (origin/main at filing) unless a PR head is named

| What | Where | What it says |
|---|---|---|
| FR-240 | `docs/specs/03-rating-engine.md:137` | "all references resolvable and at a sufficient maturity (FR-20)"; one dated amendment (2026-09-30, `RL-1329`, `LADDER_CLAMP_UNPLACEABLE`). Nothing on a `model_call`'s inputs. |
| FR-87 | `docs/specs/02-modelling.md:88` | Factors "are *resolved* against a specific version at fit time" — fit-time, not compile-time. |
| The owned-codes list | `docs/specs/03-rating-engine.md:929` onward | `MODEL_CALL_FEATURE_MAP_INVALID` is **not** in it (`grep -c MODEL_CALL_FEATURE_MAP_INVALID docs/specs/03-rating-engine.md` prints `0`). |
| `compile_bundle` | `packages/pricing-core/src/pricing_core/rating/compile.py:573` | The compile entry point. `:546`–`:556`: a `model_call`'s `model_ref` or `peril_structure_ref` is checked against `pins.models` (FR-237); its `feature_map` is not checked. |
| The score-time failure | `packages/pricing-core/src/pricing_core/rating/runtime.py:541`–`:545` | `feature_row` keeps only the `feature_map` entries whose graph name is in the context. A missing entry is silently absent, and the model then fails as `MODEL_CALL_FAILED` (`:133`). |
| A-2's code and its home | PL 9597 (its one file under `docs/plans/`, which is not on main), at #1178's head `176a6a756f863376515f3dd5ec0a4c29afbc14a7` (branch `pl-9597-a2-glm-model-call`; `ls-remote` read at filing) | Task 6's T3 (`:825`–`:832`) appends `MODEL_CALL_FEATURE_MAP_INVALID` to the owned-codes list (422 at the three save endpoints). T1 (`:807`–`:820`) amends FR-222 with the save-time **membership** check. Items 13 (`:354`) and 18 (`:499`) are that check's reds; item 18 makes it one function, called from every save path. |

## Ruled

1. **(b), completeness at compile.** `compile_bundle` refuses a `model_call` step whose
   `feature_map` does not cover every Factor of the **pinned** Model, or every entry of the
   Model's `feature_order` when the Model has no Factors. The pinned Model is resolved with
   the resolver compilation already uses, so the refusal comes before approval and
   deployment. A `feature_map` maps graph names to feature slugs (`runtime.py:541`–`:545`), so
   "covers" means: every required slug is a value of the map.
2. **Per component for a peril structure.** For a `peril_structure_ref`, each component
   Model is checked, and the one `feature_map` must cover every component's required inputs.
   This is the home of the per-component limb of DP-A3-7 (the 18:44:45 BST entry, item 1).
   That limb is at compile, not at save.
3. **One fault, one code.** The refusal reuses `MODEL_CALL_FEATURE_MAP_INVALID`, A-2's code,
   and its message names the step and the missing features, and for a peril structure the
   component. No new code is minted. Save checks membership (A-2, FR-222 as T1 amends it);
   compile checks completeness (this record, FR-240).
4. **The offset is not a required input under this check.** An offset column is not a
   Factor. A GLM's offset already reaches the model through `feature_map` (DP-A3-5 (a), the
   17:08:35 BST entry, item 7), and its absence stays `MODEL_OFFSET_MISSING`'s. This follows
   from item 1's "required Factors"; it is stated so that the applier's red (v) has a source.
5. **Options (a), (c) and (d) are not taken** (the entry: "(a), (c) and (d) are recorded as
   not taken"). The entry gives one reason for (b), and it is the reason the others lose:
   "the trade-off is clear and G2's peril path (A-3/A-4, the exit demo) is exactly where a
   short-mapped GBM would fail per quote after deploy". It also says where the check does
   **not** go: "at compile, not at save". **The texts of (a), (c) and (d) were in
   auditor-complete's OQ proposal, which was reported in a message and is not in any file
   this record could read**; `handover/mint-queue-2026-10-05.md` (18:51:22 BST) records only
   "an OQ proposal (rec (b) compile-time, an FR-240 amendment)". So the three are recorded by
   letter, not by content. If their texts are later recovered, a correcting record adds them;
   this record's body is not edited after its mint.
6. **No OQ is opened** (the entry: "no OQ"). FD 9497's reservation is released (the entry).

## The spec text

**T-text, appended to FR-240's row (`docs/specs/03-rating-engine.md:137`).** The anchor is
the end of the row's existing `RL-1329` amendment:

- Anchor: `The message names the step and the rung.)* |`
- `grep -cF 'The message names the step and the rung.)* |' docs/specs/03-rating-engine.md`
  at `ecbd1954` prints **`1`**.
- Apply: replace the anchor with `The message names the step and the rung.)*`, then the
  T-text below (it begins with one space), then ` |`.
- Trial apply, run at filing on a copy of `03` at `ecbd1954`: the anchor's count went
  **1 → 0**, and the T-text's count went **0 → 1**.

The T-text, byte for byte (one line in the file). `<SL 9495 date>` is the date of the
commit that applies it, and `RL-9491` is re-pointed to the minted id at this record's mint
(the convention RL 9633, #1155, sets out in its "Amendments common to all four", item 1: a
spec amendment cites the governed record that rules it, because a spec reader cannot open
the channel file):

```
 *(Amended <SL 9495 date>, `RL-9491`: "all references resolvable" also covers a `model_call` step's inputs. Compiling a bundle refuses, with `MODEL_CALL_FEATURE_MAP_INVALID`, a `model_call` step whose `feature_map` does not map every Factor of its pinned Model, or every entry of the Model's `feature_order` when the Model has no Factors. The pinned Model is resolved with the resolver that compilation already uses, so the refusal comes before approval and deployment. For a `peril_structure_ref`, the check applies to each component Model, and the one `feature_map` must map the required inputs of every component. The message names the step and the missing features, and for a peril structure the component. A save checks only that each mapped name is one the Model accepts (FR-222); this compile check is the completeness check. An offset column is not a Factor, and this check does not require it.)*
```

**Serialisation 1 — after A-2.** At `ecbd1954`, `MODEL_CALL_FEATURE_MAP_INVALID` is not in
`03`'s owned-codes list, and FR-222 does not yet carry the membership check the T-text's
"(FR-222)" cites. Both come from A-2's T-texts (PL 9597 Task 6, T1 `:807` and T3 `:825`, at
`176a6a75`). So this T-text is applied **only after A-2's slice has applied T1 and T3 to `03`
on main**. Until then, the code's home is A-2's T3. A-2's T-texts do not touch FR-240's row
(T1 is FR-222's row, T2 FR-227's, T3 the owned-codes tail).

**Serialisation 2 — the same anchor as RL 9633's T1.** RL 9633 (#1155, branch
`dm-9633-fr240` @`95590c87`, unminted) appends its T1 to FR-240's row with the **same** find
string, `The message names the step and the rung.)* |`, applied by SL 9647 (PL 9649, #1152).
Whichever applies second finds a count of `0`. **The rule for the applier:** this T-text is
always appended at the **end of FR-240's second cell**, after the last dated amendment then
present and before the closing ` |`. If RL 9633's T1 is already on main, the find string is
the last sentence of that T1 followed by ` |`, and the applier re-counts it at its own base
(`grep -cF` must print `1`; any other count is a STOP to the lead). The two texts are
independent: neither strikes or depends on the other's words.

## What it obliges

- **The applier is PL 9494 / SL 9495** (working ids; a small WK-1178 leaf plan and its
  slice). It applies the T-text byte for byte, in the same commit as the code
  (`CLAUDE.md` §2), and builds the refusal in `compile_bundle`, reusing A-2's check function
  where it can.
- **Order:** SL 9495 starts after A-2's slice (PL 9597) has merged, and lands before A-4's
  demo path (PL 9593, #1175).
- **PL 9597 gains a dated pre-mint note** that its `feature_map` check is membership only and
  is not a completeness check. That note is the planner's, not this record's.

## Acceptance — the violation that must become detectable

At `ecbd1954`, each of these compiles, and fails only per quote at score time. After
SL 9495, each is refused at compile with `MODEL_CALL_FEATURE_MAP_INVALID`:

1. A GLM `model_call` whose `feature_map` omits one Factor of its pinned Model. The message
   names the step and the Factor.
2. A GBM `model_call` whose `feature_map` omits one entry of its `feature_order`. The message
   names the step and the feature.
3. A `peril_structure_ref` `model_call` whose one `feature_map` covers every component but
   one. The message names the step, the component and the missing feature.

And these compile:

4. The complete control: the same algorithms with every required input mapped.
5. A GLM whose offset column is mapped but is not a Factor; and one whose offset is not
   mapped at all (that is `MODEL_OFFSET_MISSING`'s at score, not this check's).

Each red is red first, at the base, before the code is written.

## What this record does not decide

- **The HTTP status at compile.** A compile refusal surfaces through the compile path
  (`CodedError`, `compile.py:539`; FR-240's `POST …/compile`, `03:909`). This record does not
  set a status for it; A-2's 422 is the code's status at save.
- **Whether a save also checks completeness.** It does not, under this ruling (item 1: "at
  compile, not at save"). A save-time completeness check would be a new decision.
- **The check function's shape**, and how much of A-2's function it reuses: the plan's.
- **What happens to a committed algorithm that is already short-mapped.** The auditor
  reported none (liveness: none; not re-run here). If one is found, it is a finding, not this record's.
- **The texts of options (a), (c) and (d)** (Ruled, item 5).
- **Whether `MODEL_CALL_FAILED` stays reachable for a short map at score.** After this
  ruling, a compiled bundle cannot carry one; the runtime path is not changed by this record.
