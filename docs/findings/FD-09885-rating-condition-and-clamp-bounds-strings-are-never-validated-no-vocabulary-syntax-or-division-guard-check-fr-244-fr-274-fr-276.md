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

**Severity: HIGH (effective on independent reproduction).** The maintainer's decision
(`~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 10:53:10 BST — DECISION:
condition/clamp FD (B) — HIGH on independent reproduction; owner and order; two small items"):
HIGH, effective when auditor-docs's independent reproduction of the score-level case below
confirms it; otherwise it stays medium and returns to the maintainer. The FD was first filed at
medium (provisional) on the entry "2026-09-30 10:50:57 BST — #967 CLEAN on content: noted; B
confirmed → file the FD now". The trigger was met by a
silent wrong accept (D2 below) and a silently lost clamp (E4 below).

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
  does not decide which reading is right (`CLAUDE.md` §0). **The pending resolution is #967**
(RL working id 9904), which rules FR-244 an enforced allow-list over every authored string (a
step's `expr`, a constraint's `condition`, a clamp bound and a `key_expr`); once it merges, the
scope question is answered by the spec.

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

**Data — reported by #967's sweep (RL working id 9904), not run by this record's author.**
The sweep, at `48792023`, **covered `condition` and `clamp_bounds` specifically**, with `expr` and
`key_expr`: every rating string extracted from `examples`, `backend`, `packages`, `scripts`,
`tests`, `frontend` and `03`'s example, 68 occurrences and 37 distinct strings. It found no `??`,
`%`, `^`, `in`, `!` or string or date operation, and the only functions were the two
deliberate negative-test ones (`now()`, `foo()`). **It did find `/`** among the committed
strings' operators, without saying in which string kind, so this record cannot say "no division"
of the committed strings; the maintainer's entry (10:53:10 BST, above) states *"0 stored or
committed conditions or bounds use `??` or division"*, and that statement is the maintainer's,
not this record's measurement. What the sweep shows of the stored data: the sweep's read-only
Postgres pass (one database with rows: 25 algorithms, 29 versions; strings
`premium_in * 2`, `risk_premium_minor * expense_factor`, `office_premium_minor >= 100` and bare
`key_expr`s) and MinIO pass (compiled bundles; `* + ( )` only) show no division and no `??`.
Not checked by the sweep: Redis, other hosts and parquet dataset contents. This record's author
did no sweep of their own.

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

**Owner: the #967 WK-1178 code slice** (RL working id 9904, cited as prose), **kept separate from
the #963 fix slice**, on the maintainer's decision of 10:53:10 BST above. **Order:** the fix slice, then the #967 code
slice, then WK-1250 S1, serialised on `compile.py`. The slice widens both checks to `condition`,
`clamp_bounds` and `key_expr`. Event that discharges it: that slice's merge.

**Red-first acceptance**, each written to fail on `origin/main` first:

- **D2's condition and E3/E4's clamp bounds are refused at save**, and every non-baseline,
  non-control row of the evidence table returns an issue;
- **`??` is never a division guard**: a masked division does not satisfy the guard check;
- **the misleading `RATE_TABLE_MISS`**, in the maintainer's words (10:53:10 BST): *"a division
  guarded at save makes it unreachable; any residual runtime evaluation failure in a condition or
  bound raises its own evaluation code, never RATE_TABLE_MISS"*, red first.

The severity is HIGH on auditor-docs's independent reproduction; this record is amended with
the result when the lead relays it.

*Drafted under working id 9885.*
