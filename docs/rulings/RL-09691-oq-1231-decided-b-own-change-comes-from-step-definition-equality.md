---
id: RL-9691
family: ruling
title: OQ-1231 decided (b) — `StepChange.own_change` comes from step-definition equality, not from `consumed`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: decision-maker
tree: f0c3d197f5d89863efc647a2d7c1a6994b74dd63
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1231, RL-1172]
---

# RL-9691 — OQ-1231 decided (b): `StepChange.own_change` comes from step-definition equality

## Verified first, at f0c3d197f5d89863efc647a2d7c1a6994b74dd63

**The question** (`OQ-1231`, `docs/open-questions.md` and `03` §10). Should `own_change` be
derived from step-definition equality instead of `consumed` equality? It is gated *Before
WK-675's map plan*, and it is a technical decision point, so this role rules it
(STRUCTURE §1). This record is filed on top of the branch that places that gate.

**RL-9691 is a working id**, minted at its merge turn with `doc-id.py next --ref origin/main`.
It was checked free on all 108 remote branches.

**The rule today and its limit** (`03` §4.10, `03-rating-engine.md:731-733`):
- `own_change` is true for an added or removed step, and for a changed step whose `consumed`
  is identical on both sides.
- The known limit (auditor-b F5): a downstream step that is itself edited *and* whose input
  moved reads `own_change: false`. The diff reports the change but cannot separate the two
  causes.

**The mechanisms, read with `sed -n` at this tree:**
- `diff_traces(base: Trace, comparison: Trace) -> TraceDiff`
  (`packages/pricing-core/src/pricing_core/rating/trace_diff.py:41`) takes only the traces,
  and sets `own_change="consumed" not in fields` for a changed step.
- The compare route loops over both sides (`backend/src/app/api/score.py:351-354`). Each side
  obtains a `CompiledBundle`, and the route then calls
  `diff_traces(base_result.trace, comparison_result.trace)` (`:374`).
- `CompiledBundle.algorithm: RatingAlgorithm`
  (`packages/pricing-core/src/pricing_core/rating/runtime.py:561`) carries the step
  definitions. The route already holds it and discards it.
- **Each step carries its own pins.**
  - `RatingLookupStep.reference_table_ref` (`packages/model-schema/src/model_schema/rating.py:277`).
  - `RatingTableStep.rate_table_ref` (`:285`).
  - `RatingModelCallStep` has `model_ref` and `peril_structure_ref` (`:299-300`), and its
    validator requires exactly one of them (`:305`).
  - So a step's definition names the exact versioned artifact it reads, and a changed rate
    table is a changed `rate_table_ref` on the step that reads it. No step relies on a pin
    held elsewhere.
- `RatingStepBase` (`rating.py:257-266`) carries `step_id`, `label`, `note`, `consumes` and
  `produces`. `note` is documentation.
- **A per-step definition comparison already exists.** `diff_algorithms(old, new) -> AlgorithmDiff`
  (`rating.py:569`, FR-219) matches steps by `step_id` and reports each changed field of a
  step's `model_dump()` as an `AlgorithmStepChange` in `changed_steps` (`AlgorithmDiff`, `:539`).
  It counts `note`. WK-673's ruling (PR #845, DP-2) already builds on it. `trace_diff.py:27` has its own `_canonical`,
  which compares trace values.

## Ruled

**(b), with its comparison stated exactly.** For a step present on both sides and changed in
the traces, `own_change` is **true exactly when its definition differs between the two
compiled algorithms**, as **FR-219's `diff_algorithms` reports it**. `own_change` is true when
`diff_algorithms(base_algorithm, comparison_algorithm).changed_steps` holds an entry for this
`step_id` whose `field` is not `note`. **`note` is excluded at this call site.** `diff_algorithms`
itself is unchanged and keeps counting `note`, because FR-219's structural diff is what an
approver reads, and a documentation edit belongs there. `label` stays compared: a label edit is
listed by the traces today and still reads true. An added or removed step stays
`own_change: true`.

**Why reuse, not a second comparison.** One definition of "this step's definition changed"
already exists and is already relied on. A second one, canonical JSON inside `diff_traces`,
would let the structural diff an approver reads and the Quote Sandbox's `own_change` disagree
about the same edit, which is the kind of drift a governed tool cannot show. Both compare
typed, validated step models, so `model_dump()` equality does not raise the `1` / `1.0` /
`true` ambiguity that `_canonical` guards against in trace values. Everything else in §4.10 is unchanged: which steps are listed, and
`changed_fields`, still come from the traces.

**Why (b).**
- (a)'s limit is a wrong answer in a review tool. An edited step whose input also moved is
  reported as not edited, so a reviewer comparing two versions is told a masked edit is only
  a knock-on.
- (b) answers the question the field names, "did this step itself change?", from the
  definitions, which are the only data that know.
- It keeps today's result for the case §4.10 was built for. A changed rate table is a changed
  `rate_table_ref` on the table step, so that step reads true and its downstream steps, whose
  definitions are unchanged, read false. `RL-1172` §5's one-step acceptance still holds.
- Its data is already in hand: the route holds both `CompiledBundle.algorithm`s.
- **Why `note` is excluded:** editing a note changes no behaviour, and counting it would mark
  a documentation edit as the cause of a price change.

**What (b) costs.** `diff_traces` takes the two algorithms as well as the two traces, and the
route passes them. That is a signature change in `pricing-core` and a body change in the
route. The route's request and response shapes (`ScoreCompareRequest`, `ScoreComparison`) do
not change. This is the backend scope that places the gate before WK-675's map plan.

**Not ruled here.** A step whose definition changed but whose trace is identical for this
quote stays counted in `unchanged`, as today, because the diff lists what this quote shows.
Whether the view should also show *"edited, no effect on this quote"* is a view design
question for WK-675's map plan.

## What it obliges

- **This commit:** `OQ-1231` is closed in both mirrors, citing this record. `03` §4.10 gains a
  dated amendment stating the rule and its owner. The known-limit bullet is kept, with a note
  that it ends when WK-675 delivers (b).
- **The roadmap:** the *Before WK-675's map plan* row strikes `OQ-1231` and reads
  `1 (0 open)`. A decided question keeps its row.
- **WK-675 (its map plan places it in a named slice):**
  - `diff_traces` takes both algorithms and derives `own_change` as ruled;
  - the route passes `CompiledBundle.algorithm` for each side;
  - `StepChange`'s docstring and field description in `model-schema`
    (`packages/model-schema/src/model_schema/scoring.py:196-214`) change with it, and so does
    the generated contract.
- **Until then** the trace-derived rule stays in force, and §4.10 says so.

## Acceptance — the violation that must become detectable

The violation: **a step whose own definition changed is reported `own_change: false`, or one
whose definition is unchanged is reported `own_change: true`.** The slice that builds (b)
carries the checks, each shown red on deliberately broken input:
- *Violation: a step whose definition is edited and whose `consumed` also moved reads
  `own_change: false`.* This is F5's masked edit, and it must read true.
- *Violation: a downstream step with an unchanged definition, whose input moved, reads
  `own_change: true`.*
- *Violation: a step whose only edit is its `note` reads `own_change: true`.* The step is listed
  only when its trace differs, so the fixture must also move this step's input. The step is then
  listed through `consumed`, and it must read false.
- *Violation: `own_change` and `diff_algorithms` disagree about whether a step's definition
  changed, other than for `note`.*
- *Violation: a changed `rate_table_ref` on one table step fails to give exactly one entry
  with `own_change: true`.* This is `RL-1172` §5's one-step acceptance, which must still hold.
