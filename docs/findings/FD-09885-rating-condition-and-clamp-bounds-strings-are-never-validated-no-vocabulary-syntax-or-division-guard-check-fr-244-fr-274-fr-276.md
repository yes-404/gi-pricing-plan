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

**Severity: HIGH, in force.** The maintainer decided HIGH, effective on independent
reproduction (`~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 10:53:10 BST — DECISION:
condition/clamp FD (B) — HIGH on independent reproduction; owner and order; two small items"),
and accepted it in force once auditor-docs reproduced it ("2026-09-30 10:57:06 BST — #968 HIGH
in force: accepted; committed `/` strings; …", the header's tail elided because it names an
unrelated mint). The FD was first filed at
medium (provisional) on "2026-09-30 10:50:57 BST — #967 CLEAN on content: noted; B confirmed →
file the FD now". The trigger was met by a silent wrong accept (D2 below) and a silently lost
clamp (E4 below).

**Independent reproduction: auditor-docs's, attributed and not re-run by this record's author**,
at `9f63d0fe`, on the `test_rating_score.py` fixture with its own inputs and thresholds. A
decline condition `((loss_num / exposure_den) ?? 0) <= 3` with loss 90 is **declined**
(`['SANITY_CAP']`) at den 10 and **quoted at den 0** (payable 1507). A clamp max
`((bound_num / bound_den) ?? 5000000)` with num 600 gives payable 210 at den 3 and **no clamp at
den 0** (payable 1507). The unmasked forms raise `RATE_TABLE_MISS`, and compile is silent.

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

**Cause, by code reading: a class of four checks.** Each of four checks in
`packages/pricing-core/src/pricing_core/rating/compile.py` picks its own fields, and each picks
only `RatingExpressionStep.expr`:

| Check | Lines | Skips non-expression steps at |
|---|---|---|
| `_check_determinism` (`now()`, FR-216) | `:142-163` | `:146` |
| `_check_division_guards` (FR-274) | `:166-193` | `:176` |
| `_check_scale_cap` (FR-275) | `:196-230` | `:200` |
| `_check_vocabulary` (FR-276) | `:233-258` | `:242` |

Each loops over `algo.steps` with `if not isinstance(step, RatingExpressionStep): continue` and
reads `step.expr`. Nothing reads `condition`, `clamp_bounds` or `key_expr`; this record did not
measure `key_expr`. The table above shows all four failing: `now()` (determinism), a 31-decimal
literal (scale cap), an unguarded division (division guard), and broken syntax, `sum`, `[0]` and
`%` (vocabulary). Because each check chooses its own fields, a fifth field or a fifth check would
repeat the gap. `CLAUDE.md` §13's "prefer a check the failure cannot survive" applies, per the
maintainer's entry "2026-09-30 10:55:40 BST — time-citation correction acknowledged; #968
widened, so fix the CLASS structurally".

**Engine constructs outside FR-244** (reported by auditor-rl, **not measured by this record's
author**): `sum`, `%`, `^`, `in`, `len`, `date`, `a[0]`, `{a: 1}` and `a.b` are all compiled by
the engine. `sum`, `[0]` and `%` are also in the table above.

**Data — reported by #967's sweep (RL working id 9904), not run by this record's author.**
The sweep, at `48792023`, **covered `condition` and `clamp_bounds` specifically**, with `expr` and
`key_expr`: every rating string extracted from `examples`, `backend`, `packages`, `scripts`,
`tests`, `frontend` and `03`'s example, 68 occurrences and 37 distinct strings. It found no `??`,
`%`, `^`, `in`, `!` or string or date operation, and the only functions were the two
deliberate negative-test ones (`now()`, `foo()`). **It did find `/`** among the committed
strings' operators, without saying in which string kind; this record's own listing under
**Exposure** below resolves that. The maintainer's dated correction (`to-lead.md`, "2026-09-30
10:58:13 BST — DATED CORRECTION to my 10:53:10 entry (condition/clamp FD, "Exposure" bullet)")
supersedes the "Exposure" bullet of the 10:53:10 entry:
**stored exposure = 0; committed exposure was UNKNOWN until this record's list.** What
the sweep shows of the stored data: the sweep's read-only
Postgres pass (one database with rows: 25 algorithms, 29 versions; strings
`premium_in * 2`, `risk_premium_minor * expense_factor`, `office_premium_minor >= 100` and bare
`key_expr`s) and MinIO pass (compiled bundles; `* + ( )` only) show no division and no `??`.
Not checked by the sweep: Redis, other hosts and parquet dataset contents.

**Exposure.** *Stored exposure is 0* (the sweep's Postgres and MinIO passes above, reported).
**Committed exposure** is this record's own listing, at `origin/main` `9f63d0fe`, of every
committed rating string that contains `/`, by field. **The predicate, runnable** (run from the
repository root at `9f63d0fe`, with `python3 script.py`; it prints one `path:line [field] string`
row per hit and a count):

```python
import re
import subprocess

files = subprocess.run(
    ["git", "ls-files", "examples", "backend", "packages", "scripts", "tests", "frontend", "docs"],
    capture_output=True, text=True, check=True,
).stdout.split("\n")
skip = ("docs/rfcs/", "docs/plans/", "docs/closures/", "docs/rulings/", "docs/findings/",
        "docs/research/", "docs/ledgers/", "node_modules/", "docs/INDEX.md")
exts = (".py", ".json", ".yaml", ".yml", ".ts", ".vue", ".md", ".csv", ".toml")
key_re = re.compile(r"""["']?\b(condition|expr|key_expr)\b["']?\]?\s*[:=]\s*(?:"((?:[^"\\\n]|\\.)*)"|'((?:[^'\\\n]|\\.)*)')""")
clamp_re = re.compile(r"""clamp_bounds\b["']?\]?\s*[:=]\s*\{([^}\n]*)\}""")
str_re = re.compile(r""""((?:[^"\\\n]|\\.)*)"|'((?:[^'\\\n]|\\.)*)'""")
rows = []
for f in files:
    if not f or f.startswith(skip) or not f.endswith(exts):
        continue
    try:
        lines = open(f, encoding="utf-8").read().split("\n")
    except (OSError, UnicodeDecodeError):
        continue
    for n, line in enumerate(lines, 1):
        for m in key_re.finditer(line):
            s = m.group(2) if m.group(2) is not None else m.group(3)
            if "/" in s:
                rows.append((f, n, m.group(1), s))
        for m in clamp_re.finditer(line):
            for sm in str_re.finditer(m.group(1)):
                s = sm.group(1) if sm.group(1) is not None else sm.group(2)
                if "/" in s:
                    rows.append((f, n, "clamp_bounds", s))
for r in rows:
    print(f"{r[0]}:{r[1]} [{r[2]}] {r[3]}")
print(len(rows), "hits")
```

Result: **4 strings, all in the `expr` field, none in `condition`, `clamp_bounds` or `key_expr`**
(the last printed line is `4 hits`).

**What this extractor misses**, by construction: it reads **one line at a time** and needs a
quoted string right after the field name and `:` or `=`. So it does not see **(a) a split
string** (a string broken across lines or implicitly concatenated), **(b) a helper-built string**
(an f-string, a `+` join, a factory or fixture function that assembles the text, or any string
held in a variable and assigned to the field later), **(c) a positional string** (a step built as
`Step("id", "cond ...")` with no field name), or **(d) a multi-line dict or JSON value** whose
string starts on the line after the key. It also skips the record directories named in `skip`.

| File:line | Field | String | Guarded? |
|---|---|---|---|
| `backend/tests/test_rating_algorithms.py:112` | `expr` | `risk_premium_minor / expense_factor` | unguarded (asserts the 422 refusal) |
| `packages/pricing-core/tests/test_rating_compile.py:125` | `expr` | `risk_premium_minor / expense_factor` | unguarded (`test_an_unguarded_division_is_refused`) |
| `packages/pricing-core/tests/test_rating_compile.py:136` | `expr` | `expense_factor != 0 ? risk_premium_minor / expense_factor : 0` | guarded (`test_a_guarded_division_is_accepted`) |
| `packages/pricing-core/tests/test_rating_compile_bundle.py:248` | `expr` | `risk_premium_minor / expense_factor` | unguarded (asserts the compile-time refusal) |

So **no committed condition or clamp-bound string contains a division, guarded or not**, and
there is no exposed committed example. The three unguarded `expr` strings are deliberate
negative tests, and the checks refuse them today. **Corroboration, attributed and not re-run by
this record's author:** auditor-plans's independent multi-line scan (368 token sites, 260
characters read after each) found **no** committed `condition`, clamp bound or `key_expr` string
with `/`, which covers the split and multi-line forms the extractor above cannot. **Limits:** see
the list above; a further independent line-scoped `git grep -A4` over `clamp_bounds`, `"condition"`, `condition=`,
`"key_expr"` and `key_expr=` in `examples`, `backend`, `packages`, `scripts`, `tests`,
`frontend`, `docs/specs`, `docs/workflows` and `docs/contracts`, filtered to ` / `, returned
nothing. This is a listing at one tree, not a proof for later commits. The maintainer asked for
this list on "2026-09-30 10:57:06 BST" and, in the 10:58:13 BST correction above, made
committed exposure *"UNKNOWN until auditor-928's list"*: **it is now this list**, at `9f63d0fe`.
Each unguarded committed condition or bound would be an acceptance case of the #967 slice; there
is none, so the slice's acceptance uses the planted cases in the matrix test below.

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
slice, then WK-1250 S1, serialised on `compile.py`. The slice widens **all four checks** to
`condition`, `clamp_bounds` and `key_expr`, structurally (below). Event that discharges it: that
slice's merge.

**Red-first acceptance**, each written to fail on `origin/main` first:

- **D2's condition and E3/E4's clamp bounds are refused at save**, and every non-baseline,
  non-control row of the evidence table returns an issue;
- **`??` is never a division guard**: a masked division does not satisfy the guard check;
- **the misleading `RATE_TABLE_MISS`**, in the maintainer's words (10:53:10 BST): *"a division
  guarded at save makes it unreachable; any residual runtime evaluation failure in a condition or
  bound raises its own evaluation code, never RATE_TABLE_MISS"*, red first.

**The structural fix**, in the slice's acceptance ("2026-09-30 10:55:40 BST — time-citation
correction acknowledged; #968 widened, so fix the CLASS structurally"), each red first:

- **one enumerator of every authored expression field** (`expr`, `condition`, `clamp_bounds`
  min and max, `key_expr` and any other), iterated by **every** expression check, so no check
  picks its own fields;
- **a matrix test** that plants each check's violation (`now()`, an over-scale literal, an
  unguarded division, an off-vocabulary construct or broken syntax) in each field, and fails
  where any cell is not refused;
- **closure tests**: a new expression field that is not in the enumerator, and a new check that
  does not iterate the enumerator, each fail a test.

No committed condition or bound needs to be rewritten or shown refused (Exposure above); the
matrix test's planted cases are the acceptance cases. The severity is HIGH, in force.

*Drafted under working id 9885.*
