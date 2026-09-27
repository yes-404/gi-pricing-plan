---
id: RL-885
family: ruling
title: Finding 1: the `rating_version` evidence floor stands; the specification is the side that moves
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-2-4-rulings.md
---

## RL-885 — Finding 1: the `rating_version` evidence floor stands; the specification is the side that moves

**The finding, restated.** `EVIDENCE_FLOOR["rating_version"]`
([`../../packages/model-schema/src/model_schema/approvals.py`](../../packages/model-schema/src/model_schema/approvals.py)`:106`)
names `structural_diff`, `regression_run` and `dislocation_run` — three kinds nothing can
verify — while the docstring 27 lines above it (`:79-100`) states that the floor is §3.3's
*"**checkable projection**, not the whole table"*. And `06` §4.2's restatement of the floor —
the blockquote opening *"These defaults sit on top of §3.3's floor"* — named it for `model`,
`validation_rule`, `custom_objective` and `peril_structure`, omitting `rating_version`,
`custom_metric` and `deployment`: three of the six keys the constant actually holds. (Cited by
its opening words rather than a line range, because the correction below moves the range.)

**Ruled: the code stands; the specification moves.**

- **Not lowering the constant.** Its only live effect for `rating_version` is `below_floor()` →
  `POLICY_BELOW_EVIDENCE_FLOOR` at policy-save (`backend/src/app/platform/approvals.py:113`,
  proven at `backend/tests/test_approvals.py:503` and `:582`). FR-364's stated harm is a
  **submission** refusing on an unverifiable kind, and RL-881 keeps that wiring out of WK-671,
  so the harm cannot occur. Lowering the entry now and restoring it at WK-672/WK-673 is the same edit
  twice, with a window in between during which a workspace can save a policy below the floor.
- **What is actually missing is FR-364's own second half.** It requires that *"the remainder
  is named with an owner rather than asserted"*, and does that for `model` and for
  `peril_structure`. For `rating_version` it names nothing at all. That is the defect, and it is
  in the requirement.

**Spec changes in this commit, both to `06`:**

1. **FR-364 gains a dated amendment** naming the `rating_version` floor and the owner of each
   kind's verifiability: `regression_run` becomes verifiable in **WK-672**, `dislocation_run` in
   **WK-673**. `structural_diff` gets a **trigger rather than an owner** — no workstream row names a
   persisted structural-diff artifact, and inventing an owner would be the "phrase rather than a
   workstream" that FR-364 itself rejects; the precedent for a triggered, deliberately
   unowned row is `docs/findings/register.md`'s F7.
2. The amendment also states the invariant that was implicit and is now load-bearing: **a floor
   entry that no submission path can yet verify is permissible only while no submission path
   consults it, and the path that will consult it carries the owner.** That is the rule under
   which `rating_version`'s entry is legitimate and `model_comparison_if_predecessor`'s exclusion
   is legitimate at the same time — without it the two look contradictory.
3. **§4.2's floor restatement gains the three artifact types it omits.** Mechanism (i) of
   FR-364 is that the floor *"is restated in §4.2's own text"*; it has been restating four
   sixths of it since `custom_metric` was added on 2026-08-22.

**Scope note.** FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363 and evidence enforcement are **WK-677's** by FR-364's own words.
What lands here is the naming FR-364 requires of itself, not a change to what is enforced;
anything beyond that is WK-677's.

**Acceptance test — the violation that must become expressible.** Until this amendment, "a key
exists in `EVIDENCE_FLOOR` that FR-364 does not name" was not a statement a reader could
evaluate, because three of six keys were unnamed and the comparison had no second list. After
it, the two lists exist and the comparison is one read of each. **The ruling is overridden** if
`EVIDENCE_FLOOR` gains a key that FR-364 does not name, or if a submission path begins
consulting `effective_evidence("rating_version")` while any of its kinds is still unverifiable —
RL-881 already makes the second observable as two named tests going red.

---
