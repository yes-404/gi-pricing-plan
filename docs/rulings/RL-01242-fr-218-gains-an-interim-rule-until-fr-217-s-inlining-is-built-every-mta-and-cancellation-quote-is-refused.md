---
id: RL-1242
family: ruling
title: FR-218 gains an interim rule — until FR-217's inlining is built, every MTA and cancellation quote is refused
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: decision-maker
tree: ac8ab519c8e46141e81cb5ca6f48da9afaa35075
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [CR-838]
---

# RL-1242 — FR-218 gains an interim rule: until FR-217's inlining is built, every MTA and cancellation quote is refused

## Verified first, at ac8ab519c8e46141e81cb5ca6f48da9afaa35075

Filed under working id 9650 (first taken as 1239, which PR #892 already held as a plan id in the
single global sequence); minted `RL-1242` at its merge turn, 2026-09-29 (`doc-id.py next --ref
origin/main` at `40739df0`), and the `03` FR-218 amendment's citation is renamed with it.

**The conflict (`CLAUDE.md` §0).** The implementing change is PR #907, *"fix(rating): FR-218
refuses every MTA and cancellation quote until sub-graph inlining exists (WK-1178)"*. It is
not merged when this is written, and this record merges after it. On branch
`wk1178-fr218-fail-closed` at `748b7680`,
`packages/pricing-core/src/pricing_core/rating/score.py:411-413` is
`if ctx.purpose in ("mid_term_adjustment", "cancellation"):` followed by
`_raise_named("INPUT_CONTRACT_VIOLATION", …)`: the guard refuses both purposes, whatever
`sub_graphs` holds. `03` FR-218 (`03-rating-engine.md:87`) says that a version mounting the
sub-graph prices these purposes, and that one mounting none refuses. So the spec admits a case
the change refuses. They disagree, and the disagreement is recorded here, not left silent.

**What was read:**
- `03` FR-217 (`:86`): sub-graphs are *"versioned artifacts referenced by the parent and inlined
  at bundle time"*.
- `03` FR-218 (`:87`): *"The mount is **declared on the Rating Version and version-pinned like
  any other sub-graph**"*, and *"A version that mounts no such sub-graph refuses an MTA or
  cancellation quote rather than pricing it as new business."*
- `SubGraphRef` (`packages/model-schema/src/model_schema/rating.py:340-345`) describes two
  steps: a sub-graph is *"mounted at a named point in the parent's DAG"*, and *"it is inlined
  at bundle time"*. FR-218's "mount" is the first step, the declaration.
- `INPUT_CONTRACT_VIOLATION` is declared in `03` §5.1's error codes, so the refusal needs no
  new code.
- The finding titled *"CR-838 marks FR-217 delivered, but its pin and bundle-time inlining are
  not built"* (PR #908) records that no slice builds the inlining. The engine applies no
  sub-graph, and a non-empty `sub_graphs` let a reference that resolves to nothing price both
  purposes as new business.
- The maintainer's entry `2026-09-29 16:34:39 BST · maintainer (acting on the maintainer's
  behalf) · FR-217 GUARD FAILS OPEN: the interim fix is dispatched NOW as HIGH; P9 recurrence
  check` decided the interim refusal. It quotes auditor-a-2's reproduction at `49604a31`:
  `sub_graph:does-not-exist@1` gives payable 1507 as new business.

## Ruled

**FR-218 is amended with a dated interim rule, on the maintainer's 16:34:39 decision. No
requirement id changes.**
- FR-218's declaration and pinning of the mount stay as written. While FR-217's bundle-time
  inlining is not built, they are **necessary but not sufficient**: a declared, pinned mount is
  never applied to a quote, so it cannot price one.
- Until the inlining is built, no Rating Version can price a `mid_term_adjustment` or
  `cancellation` quote. Every such quote must be refused with `INPUT_CONTRACT_VIOLATION`,
  never priced as new business.
- **This narrows FR-218.** Read alone, FR-218 lets a version that declares the mount price
  these purposes. The interim rule refuses them all until the mount can be applied. It is an
  amendment, not a clarification. It is dated, it names its end (FR-217's inlining), and it
  lands as a parenthetical on FR-218's row in this record's commit.

**Why the interim rule and not the unamended text.** The unamended text, applied to a system
that cannot inline, is what let a reference to nothing price a cancellation as new business.
That is the silent failure FR-218 exists to prevent. A refusal that is too strict is visible,
and it costs a quote that could not be priced correctly anyway. A mount that is honoured before
it can be applied is silent, and it costs a mispricing.

## What it obliges

- **This commit:** `03` FR-218 gains the dated interim amendment.
- **PR #907** is the implementing change, and it merges before this record. This record
  requires nothing more of it.
- **When FR-217's inlining is built,** the Work that builds it replaces the interim refusal with
  a check that the sub-graph this purpose needs is inlined in the bundle. It retires the
  interim rule in the same commit, with a dated strike.
- **Not decided here:** which Work builds FR-217's inlining. The finding above and the plan
  review that proposes the new Work for FR-217 and FR-218 own that.

## Acceptance — the violation that must become detectable

The violation: **an MTA or cancellation quote priced while no sub-graph can be applied.** The
implementing change carries the checks, in `packages/pricing-core/tests/test_rating_score.py`
on branch `wk1178-fr218-fail-closed` at `748b7680`:
- `test_a_bogus_sub_graph_ref_does_not_satisfy_the_purpose_guard[mid_term_adjustment]` and
  `[cancellation]`. *Violation: an algorithm whose `sub_graphs` names
  `sub_graph:does-not-exist@1` prices the quote.* It must be refused with
  `INPUT_CONTRACT_VIOLATION`.
- `test_the_other_purposes_are_unaffected_on_the_same_algorithm[new_business]`, `[renewal]` and
  `[what_if]`. *Violation: the guard refuses one of these purposes.* It must be unaffected.
- **Red run:** with the old condition restored, the two bogus-ref tests fail with
  `DID NOT RAISE ValueError` (2 failed, 8 passed, 19 deselected, rc=1); the fix passes 10 (rc=0) —
  auditor-a-2's log `~/gi-pricing-plan.local/evidence/907/revert-proof.log`, SHA
  748b7680cca06f44fce932c4fafee3fa9c39e8a5, in that directory's `SHA256SUMS`.
