---
id: PL-774
family: plan
kind: leaf
title: W32-9 execution ledger — the transparency exposure share
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-9-transparency-exposure-share-ledger.md
---

# W32-9 execution ledger — the transparency exposure share

**Plan:** [`PL-00775-transparency-exposure-share-implementation-plan.md`](PL-00775-transparency-exposure-share-implementation-plan.md),
frozen at 2026-08-23. **Executed:** 2026-08-24. **Branch:** `w32-9-transparency-exposure-share`.

This ledger records what execution actually did, including the two places the plan's expectations
did not survive contact with the repository. The plan is not edited to agree with them.

## Result

| Task | Outcome |
|---|---|
| 1 — the worst-region share becomes exposure-weighted | Done. `30 passed` |
| 2 — the fidelity statement says "of exposure" | Done, folded into Task 1's test run |
| 3 — `ShapInteraction.exposure_share` deleted | Done. `31 passed` transparency, `103 passed` contracts, `generate-contracts --check` **0** |
| 4 — gate, ledger, roadmap | This document, plus the roadmap slice record |

Diff: **8 files changed, 88 insertions(+), 28 deletions(-)**. No new requirement id was allocated;
every marker names one that already existed (FR-136, FR-135).

## What moved, per site

FR-136's share appears in three places. **Two moved:**

1. `packages/pricing-core/src/pricing_core/modelling/transparency.py` — `_worst_regions` computed
   `float(mask.sum()) / max(rows, 1)`, a row-count share. It now resolves the weight vector through
   `diagnostics.py`'s existing `_weights` and `_share` and reports `weights[mask].sum() / total`.
   No second pair of helpers was grown.
2. The same file's `fidelity_statement` rendered `"{...}% of rows"`. It now renders
   `"{...}% of exposure"`, so the noun and the number agree for the first time.

**The third did not need to move:** `WorstRegion.exposure_share` in `model-schema` was already
*named* for exposure — only its value was wrong — so the published shape is unchanged and no
consumer of the worst-region half sees a contract change.

FR-135's `ShapInteraction.exposure_share` was **withdrawn, not computed**. It was the literal
`1.0` at its only construction site, so there was nothing to make correct; OQ-601 decided on
2026-08-23 that the honest fix is deletion. It is gone from the Pydantic shape, the producer, the
hand-authored contract, both generated artifacts, and `test_contracts.py`'s `REACHED_NESTED_PATHS`.

**FR-168 is left unbuilt.** The out-of-sample evidence that replaces the withdrawn field —
a holdout strength ratio — was appended by commit `b019070` with OQ-601 as its origin and is
not this slice's scope. Between the withdrawal landing and FR-168 being built, an interaction
candidate carries `strength` alone. That is a smaller artifact than the spec's eventual target and
a truthful one, which the constant was not.

## The frame is the train frame, deliberately

`_worst_regions` weights over the **train** frame, not the holdout. This is the one place W32-9
deliberately differs from the FR-181 precedent it otherwise mirrors: `02` §3.6 approximates
the population the model was fitted on, so unlike a partial-dependence curve this must not report
the holdout's exposure profile. The reasoning is in the function's docstring so the next reader does
not "fix" it.

## Mutation proofs

**Task 1 — the worst-region share.** The fixture makes the exposure ranking and the row-count
ranking disagree: `area = rare` is 4 rows carrying 50.0 exposure years each, `area = common` is
200 rows carrying 0.02 each. Restoring `float(mask.sum()) / max(rows, 1)`:

```
E       assert 0.047619047619047616 > 0.9523809523809523
```

The row-count definition inverts the ordering the test asserts, so the new test fails against the
behaviour it replaces. This is the proof the W32-10 slice found missing from W32-5's equivalent.

**Task 2 — the fidelity statement.** Reverting the noun to `"of rows"` fails both statement tests
(the GLM arm and the no-interaction-values arm):

```
E       assert '% of exposure' in "The GLM approximation reproduces 95.9% of the model's
        prediction variance (97.2% of its deviance). Divergence concentrates in area = rural
        (48.9% of rows, mean |error| 9.5%). Rating on the approximation would misprice that cell."
2 failed, 1 passed, 28 deselected in 3.42s
```

**Task 3 — the deleted field.** `assert "exposure_share" not in ShapInteraction.model_fields`
fails by construction if the field is restored, and `generate-contracts.py --check` fails if the
shape and the committed contract disagree in either direction.

## The `min(1.0, ...)` clamp

`_share`'s result is clamped to `1.0` before it reaches `WorstRegion(exposure_share=...)`, which is
`le=1.0`. This is a float guard, not a masked bug, and it was verified rather than assumed: the
numerator and the denominator sum over **different arrays**, so a factor with a single level makes
`weights[mask]` and `weights` the same multiset summed in a different order, which can land a last
bit above `1.0` and raise a `ValidationError` rather than round. `1.0` is the exact answer in that
case. The reason is a comment at the call site.

## Two things the plan expected that the repository did not have

Recorded here because the plan is frozen at its date.

1. **`_worst_regions` had no access to the weight column.** The plan's Task 1 describes reusing
   `_weights(spec, data)` without noting that `_worst_regions` took no `spec`. It was threaded
   through from `build_glm_approximation`, which already holds one — a signature change to a
   private function with a single caller, not a new parameter on a public surface.
2. **The `grep -rn "of rows"` sweep returned the three hits the plan predicted, and none was
   changed.** `perils.py:260` ("numbers of rows"), `validate.py:383` (VR-STR-9's permitted share of
   rows read) and `bandings.py:214` ("of rows, or of exposure") each genuinely count rows, and in
   the third the distinction *is* the sentence — changing it would make the docstring wrong. No
   fourth hit appeared, so there is no sibling EBM statement carrying the same defect.

## Checked and not a finding: the `holdout` keyword

`02` §5.2 at `docs/specs/02-modelling.md:2355-2359` declares a `holdout` keyword on
`build_shap_summary` that the code does not have — the function takes `sample`, `seed`, `bandings`,
`groupings` and `progress`. This reads like `CLAUDE.md` §0's stop-and-resolve case and **is not
one.** `git log -L 2355,2358:docs/specs/02-modelling.md` attributes those lines to commit
`b019070`, the same commit that appended FR-168 at `:232` marked *(appended 2026-08-23,
OQ-601)*. It is a dated, owned forward declaration of a function this slice is not building.
It is recorded here so the next audit does not spend the hour re-deriving it.

## The spec line this slice must be read against

`docs/specs/02-modelling.md:194` — **FR-135**. Its 2026-08-23 amendment already withdrew the
exposure-share clause and stated that *"Removing the constant field from `ShapInteraction` is
**WK-692**'s, and until it lands the artifact publishes a number that means nothing."* It has now
landed, so that forward-looking clause would have gone stale on merge: the spec would still say the
removal is pending while the code has done it. Per `CLAUDE.md` §0 that is resolved rather than left,
and per §5 by **appending a dated note** to the same row rather than rewriting the amendment —
the record of what was believed on 2026-08-23 is preserved intact.

No other `02` line disagrees with the code after this slice. `:1339`'s
`"exposure_share": 0.008, "mean_abs_error_pct": 11.4` is a **worst-region** example, whose field
survives; `:1354`'s prose already said "of exposure" and it was the code that was wrong, which is
the defect Task 2 closed.

## Gate

Both halves, run locally in the worktree, each exit code read — the frontend half is **required**
here because Task 3 regenerated the OpenAPI the client is generated from. All thirteen commands
exit 0: `1856 passed, 1 xfailed`, coverage **264 (50.5%)**, 24 contracts match, frontend
`21 files / 131 tests`. `pnpm generate:api` leaves no tracked change (the generated directory is
VCS-ignored) and `ShapInteraction` in the regenerated client carries `pair` and `strength` only.

Coverage does not move, and should not: both markers name requirements that were already marked.
This slice makes the number behind FR-136 mean what the requirement says rather than adding
a marker.

## The delegated gate ran against the wrong tree

**This is the operational finding of the slice, and it nearly shipped an unverified branch.**

The first gate run was delegated to a `gate-runner` subagent, which reported all thirteen commands
green. It had prefixed its pytest invocation with `cd /home/puzhenhao1989/gi-pricing-plan` — the
**shared checkout, which is on `main`** — rather than running in the worktree. Every number it
reported was `main`'s.

It was caught by arithmetic, not by suspicion. The agent reported `1842 passed, 1 xfailed` = 1843
executed, while `uv run pytest --collect-only -q` in the worktree collects **1857**. A 14-test gap
with no `skipped` or `deselected` in the summary is not a gap a passing run can have. Re-running in
the worktree gives `1856 passed, 1 xfailed` = 1857 — exactly the collected count, and +2 against
`main`'s 1855, which is the two tests this slice adds.

Two of its specific claims were also false, in the direction that would have hidden a defect:

- *"`grep -rn "exposure_share" frontend/src`: No results found."* In the worktree there are **five**
  hits. All five are legitimate — `PartialDependence` and `WorstRegion` keep the field — but the
  check that was supposed to prove the deletion was clean proved nothing, because it ran where the
  generated client had not been regenerated.
- Its coverage and contract counts were `main`'s and coincidentally identical, which is exactly the
  failure mode that makes this hard to spot: **a wrong-tree gate agrees with a right-tree gate on
  every slice that does not change the numbers.**

The rule this yields: **a delegated gate must be told to run in the worktree and must report the
`pwd` it ran in**, and its pytest total must be reconciled against `--collect-only` before it is
believed. A gate that cannot say which tree it measured has not measured this branch.
