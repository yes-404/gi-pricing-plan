---
id: RL-1239
family: ruling
title: FR-218's "mounts" means inlined at bundle time; until FR-217's inlining is built, every MTA and cancellation quote is refused
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: decision-maker
tree: 2c2bbcdf3c91267f7d2b42159b1420e12ce1c634
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [CR-838]
---

# RL-1239 — FR-218's "mounts" means inlined at bundle time; until FR-217's inlining is built, every MTA and cancellation quote is refused

## Verified first, at 2c2bbcdf3c91267f7d2b42159b1420e12ce1c634

**The conflict (`CLAUDE.md` §0).** PR #907, *"fix(rating): FR-218 refuses every MTA and
cancellation quote until sub-graph inlining exists (WK-1178)"*, makes the purpose guard refuse
every `mid_term_adjustment` and `cancellation` quote, whatever `sub_graphs` holds. Read on
branch `wk1178-fr218-fail-closed` at `748b7680`:
`packages/pricing-core/src/pricing_core/rating/score.py:411-413` is
`if ctx.purpose in ("mid_term_adjustment", "cancellation"):` followed by
`_raise_named("INPUT_CONTRACT_VIOLATION", …)`. `03` FR-218 (`03-rating-engine.md:87`) says that
a version mounting the sub-graph prices these purposes, and that one mounting none refuses.
Read literally, the spec admits a case the code now refuses. So spec and code disagree, and the
disagreement has to be recorded, not left silent.

**What was read:**
- `03` FR-217 (`:86`): sub-graphs are *"versioned artifacts referenced by the parent and inlined
  at bundle time"*.
- `03` FR-218 (`:87`): the mount is *"declared on the Rating Version and version-pinned"*. *"A
  version that mounts no such sub-graph refuses an MTA or cancellation quote rather than
  pricing it as new business."*
- `INPUT_CONTRACT_VIOLATION` is declared in `03` §5.1's error codes (`:773`), so the refusal
  needs no new code.
- PR #908, *"CR-838 marks FR-217 delivered, but its pin and bundle-time inlining are not
  built"*, records that no slice builds the inlining. The engine evaluates no sub-graph, and a
  non-empty `sub_graphs` let a reference that resolves to nothing price both purposes as new
  business.
- The maintainer's entry `2026-09-29 16:34:39 BST · maintainer (acting on the maintainer's
  behalf) · FR-217 GUARD FAILS OPEN: the interim fix is dispatched NOW as HIGH; P9 recurrence
  check` decided the interim refusal, and quotes auditor-a-2's reproduction at `49604a31`:
  `sub_graph:does-not-exist@1` gives payable 1507 as new business.

## Ruled

**The spec is right, and it is read strictly. The code in #907 is the correct reading of it.**
- FR-217 defines a sub-graph as inlined at bundle time. So a sub-graph is **mounted** only when
  it is inlined into the compiled bundle and evaluated. A reference declared in `sub_graphs`
  that is not inlined is not a mount.
- No sub-graph can be inlined until FR-217's inlining is built. So, until then, no Rating
  Version mounts the MTA or cancellation sub-graph. FR-218's own refusal clause then applies to
  every such quote: it is refused with `INPUT_CONTRACT_VIOLATION`, and never priced as new
  business.
- This clarifies FR-218. It does not amend it. No requirement id changes. The clarification is
  a dated note on FR-218's row, in this commit.

**Why this reading and not the looser one.** The looser reading, *"a non-empty `sub_graphs` is
a mount"*, is the one the earlier guard used. It is what let a reference that resolves to
nothing price a cancellation as new business, which is the silent failure FR-218 exists to
prevent. A refusal that is too strict is visible, and it costs a quote that could not be priced
correctly anyway. A mount that is too loose is silent, and it costs a mispricing.

## What it obliges

- **This commit:** `03` FR-218 gains the dated clarification note.
- **#907** is consistent with the spec as clarified. This ruling requires nothing more of it.
- **When FR-217's inlining is built,** the Work that builds it replaces the interim refusal
  with the check the note describes: the sub-graph this purpose needs is inlined in the
  bundle. It retires the note's interim clause in the same commit.
- **Not decided here:** which Work builds FR-217's inlining. #908's record and the plan review
  that proposes the new Work for FR-217 and FR-218 own that.

## Acceptance — the violation that must become detectable

The violation: **an MTA or cancellation quote priced when no sub-graph is inlined in the
bundle.** #907 carries the checks; this ruling names them:
- *Violation: an algorithm whose `sub_graphs` names a reference that is never inlined
  (`sub_graph:does-not-exist@1`) prices a `cancellation` or `mid_term_adjustment` quote.* It
  must be refused with `INPUT_CONTRACT_VIOLATION`. #907's broken-input test is this case.
- *Violation: a `new_business`, `renewal` or `what_if` quote on the same algorithm is refused by
  the guard.* It must be unaffected. #907's second test covers these three purposes.
