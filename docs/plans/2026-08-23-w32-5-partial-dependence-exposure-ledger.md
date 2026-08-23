# W32-5 — the two partial-dependence defects: execution ledger

What executing
[`2026-08-23-w32-5-partial-dependence-exposure.md`](2026-08-23-w32-5-partial-dependence-exposure.md)
actually did, on 2026-08-23, the same day the plan was written.

The plan is **not** edited to agree with this file — [`README.md`](README.md) has that rule.
Where the plan was wrong, this record says so and the correction lives here.

**Executed in two sittings.** The first stopped mid-run to release machine load and left a
`wip:` commit; the second rebased onto `main` (which had moved by two merges), reworded that
commit into two Conventional-Commit ones, took the measurement, and produced the mutation
evidence [`CLAUDE.md`](../../CLAUDE.md) §13 rule 4 requires and the first sitting had none of.

---

## Result

| | Before | After |
|---|---|---|
| `exposure_share`, categorical point | row count | summed exposure / total exposure |
| `exposure_share`, numeric point | `1.0 / len(labels)` — a constant | summed exposure in the grid cell |
| The ranking FR-MODEL-118's cap applies | row count | summed exposure |
| The omission record's share | dropped rows / rows | dropped exposure / total exposure |
| A banded or grouped factor's curve | one point per raw source value | one point per band or group |
| `FR-MODEL-125` | unallocated | defined, evidenced by two tests |
| NFR-MODEL-14 | 0.0480 fits/pass (2026-08-22) | **0.0356** fits/pass, budget 0.06 |

---

## The plan allocated an id the audit will not accept until another branch lands

Two ids named below are undefined by design, so they are declared here on marker lines the
audit reads as allocations rather than as citations, and referred to bare afterwards:

- Next free: `FR-MODEL-124` — the W32-4 branch's, allocated on 2026-08-23 and not yet landed.
- Next free: `FR-MODEL-999` — mutation M6's deliberately undefined id, which the check printed as `FAIL: tests claim requirements that do not exist: FR-MODEL-999  <- packages/pricing-core/tests/test_gbm.py`.

The plan's Global Constraints say 124 is taken by the W32-4 plan of the same date, so this
plan takes `FR-MODEL-125`, and — explicitly — *"do not renumber if the two land out of
order"*.

`scripts/audit-docs.py` does not allow that. Its numbering check is
`sorted(set(range(1, max(nums) + 1)) - set(nums))` and fails on any hole, so a branch that
defines 125 while 124 lives on a concurrent, unlanded branch fails the gate:

```
FAILED (1):
  - FR-MODEL has numbering gaps: [124]
```

Measured rather than argued: inserting a placeholder row for 124 and re-running the
audit gives **exit 0, "All checks passed."**, and the placeholder was then removed. The gap is
the sole failure on this branch, and nothing else about this slice contributes to it.

**Verdict: the plan's allocation rule and the audit's gap check cannot both hold for two
concurrent slices.** The id is left at `FR-MODEL-125` as the plan directs — renumbering to 124
would collide with W32-4, and requirement ids are permanent ([`CLAUDE.md`](../../CLAUDE.md)
§5). The consequence is a **merge-order dependency**: this branch is green only once W32-4's
requirement 124 is in `main`. Landing W32-4 first, or landing both together, clears it.
Recorded here for the maintainer rather than resolved on this branch's own authority.

## The measurement was taken at a different scale from the one the plan named

Task 3 Step 2 says to run `uv run python scripts/bench-model.py --only gbm` and compare the
result against the last recorded **0.0480**. Those are two different scales. The bare command
defaults to `--rows 678_013`; the 0.0480 in `02` §9 was measured at **75 000 x 60 x 500**.

Measured at the plan's own comparison scale instead:

```
NFR-MODEL-2 gbm fit, 500 trees      16.25 s wall
NFR-MODEL-14 gbm diagnostics       360.87 s wall
NFR-MODEL-14 — 360.87 s over 623 scoring passes (60 permutation, 560 partial-dependence points)
  / fit wall-clock, per scoring pass  =   0.0356 fits   (within 0.06)   [16.25 s]
```

**0.0356 fits per scoring pass against the 0.06 budget — met, 1.69x headroom**, at 1-minute
load average **0.85**. The 560 partial-dependence points are unchanged from the 2026-08-22
reading, which is expected: `bench-model.py`'s `factor_set` builds **identity** factors only,
so Task 2's band-and-group collapse has nothing to bite on here and Task 1's change is
pass-count-neutral by construction.

The 678 013-row default was not run. Diagnostics there project from this measurement to
roughly **55 minutes** on top of the fit, which is not a comparison the recorded figure
supports and not a wait the slice needs.

## The benchmark's ten silent minutes were normal, and are two effects, not one

The first sitting reported `--only gbm` running past ten minutes at load 0.42 with no output
and banked no timing. Both causes are confirmed, and neither is a regression.

1. **The default scale is nine times the comparison scale.** `--only gbm` with no flags is
   678 013 rows x 60 factors x 500 trees. NFR-MODEL-2's own budget for the *fit* alone at that
   shape is 1200 s, and diagnostics are an order of magnitude above the fit. Ten minutes is
   nowhere near the end of that run.
2. **`bench-model.py` block-buffers its stdout.** The script has no `flush=True`, no
   `sys.stdout.reconfigure`, and is not run with `-u`, so Python's default block buffering
   applies whenever stdout is a file or a pipe rather than a terminal. Demonstrated with a
   three-second script writing to a redirect: the file stayed at **0 bytes** for the whole
   three seconds and reached its full 19 bytes only at exit. A benchmark redirected to a log
   therefore looks identical whether it is working or wedged.

**Not a regression — the slice's `_sweep` is faster.** Interleaved A/B at a fixed
20 000 x 20 x 100 shape, alternating the committed `diagnostics.py` with `main`'s pre-slice
copy in the same process pattern:

| Round | new (s) | old (s) |
|---|---|---|
| 1 | 23.46 | 33.59 |
| 2 | 15.75 | 25.14 |
| 3 | 15.72 | 37.25 |

Same 211 scoring passes on both sides. The mechanism is in the diff: the old sweep ran
`(text == label).sum()` over the whole frame once per level *inside* the scoring loop, where
the new one computes every level's exposure in a single group-by before the loop starts. A
first, non-interleaved A/B pair read the other way round (new 21.83 s, old 15.40 s) and was
load noise — which is why it was re-run interleaved rather than reported.

## §13 rule 4 — six checks, each proven on deliberately broken input

Every mutation was applied to a pristine copy, run, and reverted; `git status --porcelain`
was checked clean of unintended changes after each.

| # | What was broken | What the check printed |
|---|---|---|
| M1 | The categorical point's share reverted to a row count | `assert 0.047619047619047616 > 0.9523809523809523` — the row-count answer, stated out loud |
| M2 | The numeric grid share reverted to `1.0 / len(labels)` | `AssertionError: every point carried the same share — the constant is back` |
| M3 | The level ranking reverted to `value_counts(sort=True)` | `assert 0.004901960784313725 > 0.004901960784313725` |
| M4 | `_resolved_axis` forced to `None`, collapsing the axis to the raw column | banding: `AssertionError: ['22', '26', '30', '34', '38', '41', ...]`; grouping: `assert {'centre', 'c...outh', 'west'} == {'coastal', 'inland'}` |
| M5 | `_share`'s zero-exposure guard removed, on an all-zero weight vector | `ZeroDivisionError: float division by zero` |
| M6 | A `@pytest.mark.req` marker renamed to the undefined id 999 declared above | `FAIL: tests claim requirements that do not exist:` naming that id and both call sites |
| M7 | `exposure_share` given a `default=0.0` in `model-schema` | `FAIL: committed contracts are out of date with the models:` |

**M3 also found a test that does not discriminate.** Task 1 Step 10 nominated
`test_the_cap_keeps_the_most_exposed_levels_and_is_what_bounds_the_grid` as the assertion that
"most directly changes meaning here". Under M3 it **passed** — on its fixture the row-count
order and the exposure order agree, so it cannot tell the two definitions apart in either
direction. It is a correct test of the cap; it is not evidence about the ranking quantity. The
test that discriminates is the one Task 1 Step 1 wrote.

## A docstring this slice introduced was wrong about its own failure mode

`_share`'s docstring said that dividing by a zero total *"returns `nan`, which
`PartialDependencePoint`'s `ge=0.0, le=1.0` bound rejects"*. M5 measured it: both operands are
Python floats by that point, so the unguarded division raises `ZeroDivisionError` out of the
middle of a diagnostics run and never reaches the bound. The bound does reject a `nan`
(`Input should be less than or equal to 1`), but only a numpy one would get that far.

**Verdict: the guard is right, its docstring was wrong.** Corrected in place rather than left,
with the measurement named — [`CLAUDE.md`](../../CLAUDE.md) §0 on resolving rather than
quietly matching.

## Four smaller places the plan did not match the repository

| Plan said | Repository |
|---|---|
| `curve.factor_slug`, `point.label` | `curve.factor`, `point.value`; the third field is `mean_prediction` |
| `_diagnose(frame, factor_columns=(...))` | `_diagnose(backend, factors, *, data=..., bandings=..., groupings=...)` — the driver takes the backend first and is parametrised over both |
| `banding.level_labels()` | `Banding.labels`, a tuple |
| Closing checklist: *"the branch is pushed and a PR is open"* | Not done, by instruction: the main thread lands all W32 branches |

The plan also states that *"the frontend half is not needed"*. Both halves were run anyway, on
instruction; the frontend half is green and unaffected, which is what the plan predicted.

## An environment failure that was not a code failure

The first full `pytest` run after the rebase reported **199 failed, 115 errors**, every one of
them `UndefinedColumnError: column validation_rules.catalogue_id does not exist`. The local
test database was still on `9e4c7b21fa08`; W32-2 landed `7c1a9e40b3d2` in `main` earlier the
same day. `GIP_DATABASE_URL=… uv run alembic upgrade head` cleared it — the DSN form
[`dev-commands`](../../.claude/skills/dev-commands/SKILL.md) records, because the bare command
uses the wrong credentials. Not a defect, and worth writing down because a rebase onto a
migration is now a routine event in a five-slice fan-out.

This branch adds **no** migration, so FR-PLAT-57's single-head invariant is untouched:
`alembic heads` reports `7c1a9e40b3d2 (head)`, one head.

## Verification

Both halves of the gate were run, each command's own exit code read from that command rather
than from a pipe.

| Command | Exit |
|---|---|
| `uv sync --all-packages --dev` | 0 |
| `uv run ruff check .` | 0 |
| `uv run mypy` | 0 — no issues in 131 source files |
| `uv run lint-imports` | 0 |
| `uv run pytest -q` | **1** — 2 failed, 1794 passed, 1 xfailed, 26:30 at load 10.4 |
| `python3 scripts/audit-docs.py` | **1** |
| `uv run python scripts/req-coverage.py` | 0 |
| `uv run python scripts/generate-contracts.py --check` | 0 — "Contracts: 3 kept, 0 broken", no regenerate |
| `pnpm --dir frontend install --frozen-lockfile` | 0 |
| `pnpm --dir frontend generate:api` | 0 |
| `pnpm --dir frontend lint` | 0 |
| `pnpm --dir frontend type-check` | 0 |
| `pnpm --dir frontend test` | 0 |
| `pnpm --dir frontend build` | 0 |

**The two red commands are one cause.** `tests/test_repository_invariants.py`'s two failures
are `subprocess`-invocations of `audit-docs.py` asserting `returncode == 0`, and both print
the same `FR-MODEL has numbering gaps` line. Nothing else in the suite is red, and the W30
`xfail` is still counted as `xfailed` rather than turning green.

The suite ran at 1-minute load average 10.4 on a 4-core machine shared with a concurrent
agent session running its own suite, which is why 26:30 is not comparable to the 7:34 the
W32-2 ledger records.

## Carried forward, with owners

- `packages/pricing-core/src/pricing_core/modelling/transparency.py` still computes
  `exposure_share` as a row count at `:268` and hardcodes `1.0` at `:398`, in the SHAP
  fidelity path. Deliberately untouched — `02` §5.2 describes *that* site as a percentage of
  rows, so changing it is a separate resolution with a separate requirement. **Unowned**;
  raised at close as the plan directs.
- **Cross factors still grid over their first source column.** A representative value for a
  cross level is a tuple across several columns. Recorded in
  [`../roadmap.md`](../roadmap.md). **Owner: W6b**, with the frontend that first plots a cross
  factor's curve.
- `_permutation_importances` shares the row-count defect at the same module's `:870`. Left
  alone: its FR-MODEL-119/121/122 block is **W30's**.
- The W30 `xfail(strict=True)` at `test_a_gbm_with_a_sparse_interaction_can_produce_diagnostics`
  is still red, as the plan requires.
