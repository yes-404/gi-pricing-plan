---
id: PL-764
family: plan
kind: leaf
title: W32-4 — the EBM predict arm: execution ledger
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-4-ebm-predict-arm-ledger.md
---

# W32-4 — the EBM predict arm: execution ledger

What executing [`PL-00765-w32-4-the-ebm-predict-arm-implementation-plan.md`](PL-00765-w32-4-the-ebm-predict-arm-implementation-plan.md)
actually did, on 2026-08-23, the same day the plan was written.

The plan is **not** edited to agree with this file — [`README.md`](README.md) has that rule.
Where the plan was wrong, this record says so and the correction lives here.

**Executed by one subagent in an isolated worktree**, as one of five WK-692 slices run
concurrently. Five commits, no migration, so no Alembic collision with its siblings.

---

## Result

Every gate command exit 0, each read from its own exit code. **1774 passed, 1 xfailed, 0
skipped** in 12:09 at load 5.8.

That timing is reported only as a fact about this run, and **no number from this session is
quotable as a measurement**. The same suite took 2:36:57 at load 16–31 earlier the same day —
a contention factor of roughly 13 on a machine shared between concurrent agent sessions.
[`CLAUDE.md`](../../CLAUDE.md) §11 requires the load be quoted beside every figure for exactly
this reason, and a headline number re-taken in a quiet window.

---

## Enforcement proven, not assumed

[`CLAUDE.md`](../../CLAUDE.md) §13 rule 4 asks that a new check be shown to fail on
deliberately broken input. Both new checks were.

| Check | How it was falsified |
|---|---|
| The narrowed EBM refusal | Replacing `if not isinstance(fit, EbmFitResult):` with `if False:` failed `test_an_ebm_spec_carrying_a_glm_fit_result_is_refused_by_name`; reverting restored it |
| The contract drift guard | `generate-contracts.py --check` exited 1 before regeneration and 0 after |

## Three resolutions, one of them found by the suite

`02` §5.2's `predict.py` block omitted `score_fitted` and `detect_quantile_crossing`. The
**specification** was wrong; it was completed with a dated note.

The blanket EBM refusal existed only in a docstring, with the spec silent on it. Here the
**code** was wrong, and the obligation was written down rather than the behaviour quietly
widened: `FR-180` was appended to carry it.

The third was not in the plan at all. `FR-207`'s exhaustiveness guard tripped on the new
`UnavailableReason` member — behaving exactly as its own docstring promised it would. It was
resolved by listing the reason and making the claim true with a test, not by loosening the
guard.

## Where the plan was wrong

| Plan said | Repository |
|---|---|
| `UncertaintyKind.PREDICTION_INTERVAL` | No such member |
| `_fitted_glm` returns a 3-tuple | It returns a 2-tuple |
| `spec["factors"]` holds dicts | It holds a list of id strings |
| An `_ebm_spec` needing no `split_ref` | The fit job failed until the split was read off the GLM's stored spec |

## Deliberately not done

The plan's closing step asked for its own checkboxes to be ticked. They were left unticked:
[`README.md`](README.md) freezes a filed plan as a record of what was believed at its date,
and that rule outranks an instruction inside the frozen file. This ledger is where execution
is recorded instead.

Of the four [`../roadmap.md`](../roadmap.md) sites the plan named, two were corrected. The
other two correctly attribute the frontend EBM views to WK-664 and were left alone.
