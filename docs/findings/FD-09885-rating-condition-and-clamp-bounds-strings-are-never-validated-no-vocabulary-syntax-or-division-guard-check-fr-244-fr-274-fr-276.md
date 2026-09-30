---
id: FD-9885
family: finding
title: Rating condition and clamp_bounds strings are never validated — no vocabulary, syntax or division-guard check (FR-244, FR-274, FR-276)
status: active
created: 2026-09-30
owner: auditor
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
corrected_by: []
relates: [WK-1178]
---

# FD-9885 — Rating condition and clamp_bounds strings are never validated — no vocabulary, syntax or division-guard check (FR-244, FR-274, FR-276)

## Finding

**Severity: medium, provisional.** It **rises to high** if the score-level case (auditor-rl is
building it) shows a silent wrong accept, decline or clamp: a decline condition that should
decline lets the quote through, or a clamp bound that silently does not apply.

`validate_algorithm` checks only `RatingExpressionStep.expr`. A constraint step's `condition`
and its `clamp_bounds` strings, which the engine evaluates the same way, are never read by the
vocabulary, syntax or division-guard checks. Syntactically broken text, an unguarded division and
constructs outside FR-244's list all validate clean.

## Requirements read

- **FR-274** (`docs/specs/03-rating-engine.md:223`): *"Every division in a rateable path carries an
  explicit zero guard, bundle compilation (FR-240) rejects an unguarded one"*. A `condition` or a
  clamp bound is in a rateable path. **This is the direct breach.**
- **FR-244** (`:146`) and **FR-276** (`:225`) are worded for *"`expression` steps"* and *"the
  `expression` step's function vocabulary"*. Read literally, they name the expression step, so
  whether a `condition` is in their scope is a **spec question, not a settled breach**. FR-244's
  own grammar clause (*"the same restricted grammar as `02` §4.6 … No other functions"*) reads
  as a rule about the grammar, and a `condition` is evaluated by the same engine. This record
  does not decide which reading is right (`CLAUDE.md` §0); the fix slice's spec side settles it.

## Evidence

Measured at `origin/main` `9f63d0feee524815e7e0c68c99a53ac3f80e6c37`. Reproduced by this
record's author with `validate_algorithm(RatingAlgorithm.model_validate(...))` from
`packages/pricing-core/src/pricing_core/rating/compile.py`, on the repository's own fixture
`valid_algorithm()` (`packages/pricing-core/tests/test_rating_compile.py:15`), mutating the
constraint step `s_minprem` (or the expression step `s_office`), repo `.venv`, `PYTHONPATH` at
this tree (confirmed by `pricing_core.__file__`). Issue codes returned:

| Mutation | Issues |
|---|---|
| baseline fixture | `[]` |
| `condition`: `sum([office_premium_minor, 1]) >= 100` | `[]` |
| `condition`: `office_premium_minor[0] >= 100` | `[]` |
| `condition`: `office_premium_minor / expense_factor >= 100` (unguarded division) | `[]` |
| `condition`: `office_premium_minor >=(((` (syntactically broken) | `[]` |
| `condition`: `now() >= 100` (non-deterministic call, FR-216) | `[]` |
| `condition`: a 31-decimal-place literal (FR-275's cap is 28) | `[]` |
| `clamp_bounds.min`: `100 / expense_factor` (unguarded division) | `[]` |
| `clamp_bounds.min`: `(((` (syntactically broken) | `[]` |
| `expr`: `risk_premium_minor % 7` (`%` is not in FR-244's grammar) | `[]` |
| control, `expr`: `risk_premium_minor / expense_factor` | `[EXPRESSION_UNGUARDED_DIVISION]` |
| control, `expr`: `(((` | `[EXPRESSION_INVALID_VOCABULARY]` |

The two controls show the same harness flags the same defects in an `expr`, so the empty
results on `condition` and `clamp_bounds` are not a harness that cannot fail.

**Cause, by code reading.** `_check_division_guards` (`compile.py:166-193`) and
`_check_vocabulary` (`:233-257`) each loop over `algo.steps`, skip every step that is not a
`RatingExpressionStep` (`if not isinstance(step, RatingExpressionStep): continue`) and read only
`step.expr`. `_check_scale_cap` (`:196-`) has the same shape, and the `now()` row above is the
determinism check (`_check_determinism`, `:142-163`) missing a `condition` for the same reason. Nothing reads
`condition`, `clamp_bounds` or `key_expr`. This record did not measure `key_expr`.

**Engine constructs outside FR-244** (reported by auditor-rl, **not measured by this record's
author**): `sum`, `%`, `^`, `in`, `len`, `date`, `a[0]`, `{a: 1}` and `a.b` are all compiled by
the engine. `sum`, `[0]` and `%` are also in the table above.

**Data.** **No sweep for off-list constructs in stored conditions has been done by this
record's author.** #967's delegated sweep (RL working id 9904) reported 0 `??` and only
arithmetic, comparisons, and/or, ternary and `true` in the 37 git-tree rating strings; that is
cited as *reported by #967's sweep*, and it covers git-tree strings, not stored rating versions.

## Disposition

**Deferred with an owner: the WK-1178 code slice that #967 (RL working id 9904) specifies**,
which widens both checks to `condition`, `clamp_bounds` and `key_expr` after the fix slice
planned for about 16:00. Event that discharges it: that slice's merge, proven on this table's
inputs: each row above except the baseline and the controls must return an issue. The severity
review is due when auditor-rl's score-level case lands: a silent wrong accept, decline or clamp
makes this **high** and this record is amended.

*Drafted under working id 9885.*
