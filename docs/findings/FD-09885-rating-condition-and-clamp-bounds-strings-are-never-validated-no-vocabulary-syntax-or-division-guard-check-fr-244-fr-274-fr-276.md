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

**Severity: medium (provisional); the high trigger is met** (a silent wrong accept, D2 below,
and a silently lost clamp, E4 below). **High takes effect on independent reproduction**
(auditor-docs is running it). The trigger was: a decline condition that should decline lets the
quote through, or a clamp bound that silently does not apply.

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

## Score-level case — reported by auditor-rl, not re-run by this record's author

`score_one` on the fixture of `packages/pricing-core/tests/test_rating_score.py`, at `48792023`.
Baseline: office premium 1436, payable 1507. Every variant below **compiled OK**. In the decline
variants `s_decl_cap` has `on_violation=decline` and the input `sanity_floor_minor` is the divisor.

| Variant | Text | Result |
|---|---|---|
| A1 decline | `office_premium_minor / sanity_floor_minor <= 2`, floor 1 | declined `['SANITY_CAP']` |
| A2, A3 decline | same, floor 0 or null | raises `CodedError` **`RATE_TABLE_MISS`** (fail-closed, misleading code) |
| D1 decline | `((office_premium_minor / sanity_floor_minor) ?? 0) <= 2`, floor 1 | declined |
| **D2 decline** | same as D1, **floor 0** | **QUOTED**, `decline_reasons []`, office 1436, payable 1507 |
| C2 clamp | `clamp_bounds` max `1` | office 1 |
| C1 clamp | max `sanity_cap_minor / sanity_floor_minor`, floor 0 | raises `RATE_TABLE_MISS` |
| E1, E2 clamp | max `(cap / floor) ?? 1000`; floor 1, then floor 0 | floor 1: no clamp (1436); floor 0: clamps to 1000 (payable 1050) |
| E3 clamp | max `(cap / floor) ?? 999999999999`, cap 1000, floor 1 | office 1000 (the cap applies) |
| **E4 clamp** | same as E3, **floor 0** | **cap silently lost**, office 1436, unclamped |

E3 and E4's outcome was also affected by the fixture's separate `SANITY_CAP`; read the office
premium. **D2 is a silent wrong accept** (a decline that should fire lets the quote through) and
**E4 a silently lost clamp**: that is the high trigger. A2, A3 and C1 fail closed but under a
**misleading code**: a zero or null division in a condition or a clamp bound surfaces as
`RATE_TABLE_MISS`, which names a rate-table problem that did not happen. That is part of this
finding.

**How #967 relates.** #967's documentation of `??` (RL working id 9904) makes the masked form
legal. Its item 3, widening the guard check to `condition` and `clamp_bounds`, with `??` never
counting as a guard, is what would refuse D2 and E3/E4 at save.

## Disposition

**Deferred with an owner: the WK-1178 code slice that #967 (RL working id 9904) specifies**,
which widens both checks to `condition`, `clamp_bounds` and `key_expr` after the fix slice
planned for about 16:00. **The owner and the order are pending the maintainer's re-decision**,
since the high trigger is met. Event that discharges it: that slice's merge.

**Red-first acceptance**, each written to fail on `origin/main` first: **D2's condition and E4's
clamp bound are refused at save**, and every non-baseline, non-control row of the table above
returns an issue. The score-level rows must not reach `score_one` as a compiled bundle. The
severity becomes **high** on auditor-docs's independent reproduction, and this record is amended
then.

*Drafted under working id 9885.*
