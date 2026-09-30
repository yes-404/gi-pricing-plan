---
id: RL-1312
family: ruling
title: FR-244 decided — an enforced allow-list of operators and functions, and ?? is its coalescing operator
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 48792023e09cd79c771c2184d6808e378732b76b
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1265, PL-1268, FR-244, FR-274, FR-276, FR-246, OQ-1316]
---

# RL-1312 — FR-244 decided: an enforced allow-list of operators and functions, and `??` is its coalescing operator

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

**What was asked** (the maintainer's entry `to-lead.md` "2026-09-30 10:15:07 BST — … `??` goes
to the DM as a ruling", relayed by the lead, on auditor-933's facts at `eeda8f4b`). *(Time
corrected: this record first cited "about 10:22 BST", an estimate the lead relayed. The time
is now read from the file's own header.)* This is a `CLAUDE.md` §0 disagreement between code and
spec about the rating expression grammar, and the grammar is the decision-maker's
(`document-ids.md` §1.6, FR row). Rule:
- whether FR-244 is an **enforced allow-list, operators included**;
- whether `??` is a **spec gap**, to be documented, or a **code gap**, to be refused;
- after a sweep of stored algorithms, `examples/` and the test fixtures;
- and **which slice carries the change**.

The maintainer's steer was weighed on its merits. This record was minted 2026-09-30 as
RL-1312 (hand-assigned in the lead's batch plan, batch 4, under the maintainer's option (B));
it was filed under working id 9904, which had been checked free: no `[A-Z]{2,3}-0?9904` token
under `docs/` on any `origin/*` ref, nor in `~/gi-pricing-plan.local/channel/`.

**Context, not ruled here.** A HIGH finding (FD working id 9977, HIGH per the 10:15:07 BST
entry) is being filed at the time of writing, not yet on any ref: an unpinned or wrong-version `table` or `lookup` step prices silently wrong. It
was reproduced through `??` consumers. Its fix, the WK-1178 slice due about 16:00 BST,
refuses such a step at compile. That fix removes the upstream cause of the null that `??`
masked. This ruling does not depend on it and does not block it.

## Verified first, at `48792023e09cd79c771c2184d6808e378732b76b`

### Presence and absence, as verified

| Claim | Verdict | How it was verified |
|---|---|---|
| FR-244's text | **present** | `03-rating-engine.md:146`. Expression steps use "the same restricted grammar as `02` §4.6, extended with decimal-safe operators and these rating-specific functions: `round(x, mode, dp)`, `band(x, banding_ref)`, `coalesce(a, b)`, `date_diff_years(a, b)`, `min`, `max`, `clip`. No other functions." It says the list "states intent, not a guarantee". It enumerates no operators. |
| `??` in the spec | **absent** | `grep -n -F '??'` over `03-rating-engine.md` gives no hit, and `grep -n -i 'nullish'` gives none. The only coalescing text in `03` is FR-244's `coalesce(a, b)`. |
| The save-time vocabulary check | **present, `expr` only** | `_check_vocabulary` (`packages/pricing-core/src/pricing_core/rating/compile.py:233-257`) runs `zen.compile_expression(step.expr)` for `RatingExpressionStep`s only (`:240-247`). It accepts whatever the engine compiles, and nothing in it compares a name or an operator with FR-244. `git grep -n 'condition\|clamp_bounds' 48792023 -- packages/pricing-core/src/pricing_core/rating/compile.py` → rc 1: no check reads a constraint's `condition` or `clamp_bounds`. |
| The division-guard markers | **present** | `_GUARD_MARKERS` (`compile.py:41`) is `("!= 0", "> 0", "== 0", "< 0", "?:", "coalesce(", "if(", "guard")`. It has no `??`. |
| The platform's own generated ZEN | **present** | `runtime.py:292` wraps every constraint condition as `!(condition)`. `:310-313` turn clamp bounds into ternaries. `:219` passes each `key_expr` as a decision-table input `field`. These are generated strings, not authored ones. |
| RL-1265 DP-5 | **present** | `docs/rulings/RL-01265-…md:110-116`. WK-690 Slice 1 amends FR-244 to say that the rating grammar is FR-244's own: "ZEN's expression language, restricted to FR-244's function list and verified by FR-276". |
| The held sentence | **present, on its branch** | WK-690 Slice 1's leaf plan, not yet on `main` and so cited by branch: `origin/p2-wk690-s1-leaf` @ `57a4833e`, its file under `docs/plans/` whose name starts `wk-690-slice-1-parser-profiles`, lines 1536-1544, Task 6, Step 1: "the rating grammar is FR-244's own: ZEN's expression language, restricted to the function list above and verified against the engine by FR-276. …" The lead holds it until this ruling. |

### The engine, probed

`zen-engine==0.53.0` is pinned in `packages/pricing-core/pyproject.toml:58` and locked at
`uv.lock:2763-2764`. The installed interpreter reports the same version. Each string below
went through `zen.compile_expression`, and the values through `zen.evaluate_expression`. The
probe was read-only, run from a scratch directory with the repository's `.venv` interpreter.

| Expression | Result |
|---|---|
| `round(a)`, `round(a, 2)` | compile |
| `round(a, 'half_even', 2)` | refused: compilerError "Invalid function call" |
| `band(a, 'x')`, `coalesce(a, b)`, `date_diff_years(a, b)`, `clip(a, 0, 1)` | refused: parserError "Incomplete parser output" |
| `min(a, b)`, `max(a, b)` | refused: compilerError "Invalid function call" |
| `min([a, b])`, `max([a, b])`, `abs(a)`, `floor(a)`, `ceil(a)`, `sum([a, b])` | compile |
| `a ?? b`, `a ? b : c`, `a and b`, `a or b`, `not a`, `!a`, `==`, `!=`, `>=` | compile |
| `a % b`, `a ^ b`, `a in [1, 2]`, `a not in [1,2]`, `len('x')`, `'x' + 'y'`, `date('2020-01-01')`, `a[0]`, `{a: 1}`, `a.b` | compile |
| `a ?: b`, `a ** b` | refused |
| `a ?? 5` with `a = null` → `5`; with `a = 2` → `2` | evaluates |
| `a / b` with `b = 0` → `null`; `(a / b) ?? 7` with `b = 0` → `7` | evaluates: **`??` turns a division-by-zero null into a value** |
| `round(2.5)` → `3`, `round(-2.5)` → `-3`, `round(0.125, 2)` → `0.13` | the engine's `round` is **half away from zero** |

**The binding boundary**, probed the same way for the maintainer's 10:53:10 BST entry, which
asked for a boundary line in FR-244:

| Case | Result |
|---|---|
| `round(2.675, 2)`, `round(1.005, 2)`, `round(-2.675, 2)`, `round(1234.565, 2)` | `2.68`, `1.01`, `-2.68`, `1234.57`: exact decimal, half away from zero, with no binary-float tie error |
| `0.1 + 0.2 == 0.3` | `True` |
| context `a = 0.30000000000000004` (a Python float); `a`, and `a == 0.3` | `0.3`, and `True`: a float input keeps about 15 significant digits |
| context `a = 12345` (an int); `a * 1` | `12345.0`: outputs cross back as Python `float` |
| context `a = Decimal("2.5")` | refused at the binding: "argument 'ctx': unsupported type Decimal" |
| context `a = "2.5"` (a str); `a`, and `a + 1` | `'2.5'` is accepted **as a ZEN string**, and `a + 1` fails at evaluation (`vmError`, "Opcode Add: Unsupported type"). A number never arrives as a string |

The platform passes money in as integer minor units (FR-273). It takes each output through
`_round_minor` (`packages/pricing-core/src/pricing_core/rating/score.py:535-542`), which is
`Decimal(repr(raw))` quantized with the step's declared mode. **Integers above 2^53 at the
boundary are untested**: a stated limit, far above any premium in minor units.

So of FR-244's seven functions, the engine has only `round`, in one- and two-argument forms,
and `min` and `max` in their array forms. `coalesce(a, b)` cannot exist in the engine, and
`??` is the engine's coalescing operator. The engine's language is much larger than anything
the spec lists, and today the save-time check admits all of it.

### The sweep — before any refusal

Run read-only, by a delegated evidence agent, at `48792023`. Its commands and outputs are in
the session scratch directory, and the substance is here:
- **The git tree.** `git grep -n -F '??' 48792023 -- <dir>` with plain directory prefixes:
  `examples` 0, `backend/tests` 0, `packages` 0, `tests` 0. There is 1 hit in `scripts`,
  prose in a docstring. `frontend` and `docs` hits are TypeScript and prose, and there are no
  rating fixtures in `frontend`. Every rating `expr`, `condition`, `key_expr` and
  `clamp_bounds` string was extracted from `examples`, `backend`, `packages`, `scripts`,
  `tests` and `frontend`, and from `03`'s example: 68 occurrences, 37 distinct strings.
  - **Operators** in them: `+ - * /`, parentheses, `>= > <= < !=`, `and`, the ternary
    `? :`, and the literals: numbers and `true`.
  - **Functions** in them: only `now()` and `foo()`, each in a test that asserts its refusal
    (`packages/pricing-core/tests/test_rating_compile.py:114`, `:156`).
  - **`key_expr`** values are bare identifiers.
- **Postgres** (local, reachable; every query inside `BEGIN READ ONLY … ROLLBACK`): 77
  databases, of which 73 have `rating_algorithms` and `rating_versions`. One holds rows: 25
  algorithms and 29 versions. `??` occurrences: 0. The distinct strings are
  `premium_in * 2`, `risk_premium_minor * expense_factor`, the condition
  `office_premium_minor >= 100`, and bare `key_expr`s.
- **MinIO** (local, reachable; list and get only): 5 buckets and 14,626 objects, including
  the compiled bundles. `??` in any JSON object: 0. The four raw-byte matches are inside
  parquet **dataset** blobs, not rating artifacts. The expressions use `* + ( )` only.
- **Not checked:** Redis, other hosts, and the contents of the parquet datasets.

**Conclusion of the sweep:** no stored or committed rating expression uses `??`, `%`, `^`,
`in`, `!`, any string or date operation, or any function. The allow-list below refuses
nothing that exists, except the two deliberate negative-test functions.

## Ruled

1. **FR-244 is an enforced allow-list, operators included.** An authored rating ZEN string is
   one of: a step's `expr`, a constraint's `condition`, a clamp bound, or a `key_expr`. It may
   use only the constructs below. Anything else is refused at save with
   **`EXPRESSION_INVALID_VOCABULARY`**, the code FR-276's check already raises. This applies
   in addition to FR-276's engine compile, which still runs, since a construct can be on the
   list and still not compile. FR-244's "No other functions" has been unenforced, and it
   covered no operators at all. The engine's language includes indexing, member access,
   object literals, string functions, dates, `in`, `%` and `^`. None of these is reviewable in
   a rating path, and none is used today (the sweep).
   - **Literals:** numbers, `true`, `false`, `null`, and single-quoted strings (for
     comparisons against `string` and `enum` inputs, FR-213 at `03:82`).
   - **Names:** declared inputs and upstream produced values (FR-246 already bounds them).
   - **Operators:** `+`, `-` (binary and unary), `*`, `/`, parentheses; `==`, `!=`, `<`,
     `<=`, `>`, `>=`; `and`, `or`, `not`; the ternary `c ? a : b`; and **`??`** (item 2).
   - **Functions:**
     - `min([…])` and `max([…])`, **array forms only**. An array literal is permitted only as
       their argument;
     - `abs(x)`.
   - **No rounding function in P2: `round`, `floor` and `ceil` are not on the list**
     *(ruled on auditor-rl's note 4, after the maintainer's 10:46:20 BST entry accepted the
     engine's half-away-from-zero `round` as P2's in-expression rounding; this changes that
     point, for the reason below, and the maintainer may overrule it)*:
     - FR-226 (`03:112`) says `output` steps declare rounding explicitly, and "Rounding is
       never implicit and never happens twice". NFR-496 (`03:1152`) says "no rounding is
       applied more than once". FR-248 (`03:155`) requires the ladder to reconcile to the
       penny from each rung's **recorded operation**. An authored `round`, `floor` or `ceil`
       on a money path is a second rounding before the output step's own, and it is recorded
       on no rung, so the ladder cannot reconcile it.
     - The maintainer's steer (the entry after 10:53:10 BST, relayed) is to allow `round` only
       on dimensionless factors and refuse it on money minor-unit operands. **A save-time
       check cannot know that today.** FR-213's input types (`rating.py:194-202`: `int`,
       `decimal`, `string`, `date`, `bool`, `enum`) have no money type, and an operand is an
       arbitrary sub-expression, so deciding "money or not" needs type inference over ZEN
       expressions, which nothing in the codebase does.
     - **The interim rule is therefore that no rounding function is offered in an expression.**
       Rounding happens only where FR-226 declares it, on the output step. This costs nothing
       today: no committed, stored or bundled algorithm uses `round`, `floor` or `ceil` (the
       sweep; auditor-rl's database spot-check also found 0 `round(`). It is reversible by a
       spec change.
     - **The question — whether rounding is offered inside an algorithm, where, with what
       mode, and how it is recorded so the ladder reconciles and nothing rounds twice — is
       `OQ-1316`**, broadened for this. The dimensionless-factor rule is one of its
       options. The engine's `round` is half away from zero, which records what that option
       would use.
   - **Struck from FR-244's intent list, each with its replacement:**
     - `coalesce(a, b)` → `a ?? b`;
     - `clip(x, lo, hi)` → `min([max([x, lo]), hi])`;
     - `band(x, banding_ref)` → a `table` step whose key declares its `banding_ref`
       (FR-228);
     - `date_diff_years(a, b)` → a declared input, since a quote timestamp is already an input
       (FR-246);
     - `round(x, mode, dp)` → the output step's declared rounding (FR-226); intermediate
       rounding is `OQ-1316`;
     - the two-argument `min` and `max` → the array forms.

     None of the struck forms exists in the engine (the probe above).
   - **Not on the list** (a spec change can add any of these when a need appears): `round`,
     `floor`, `ceil` (above), `%`, `^`,
     `!` as authored text, `in` and `not in`, `sum`, string concatenation beyond comparison,
     `len`, `date`, indexing, member access, and object literals. The platform's own generated
     `!(…)` and clamp ternaries (`runtime.py:292`, `:310-313`) are outside the check, which
     reads authored strings before they are wired.
2. **`??` is documented, not refused: a spec gap.** `??` is FR-244's coalescing operator: the
   engine's realisation of the `coalesce(a, b)` that FR-244 always intended, which the engine
   cannot provide under that name. Refusing it would protect nothing. The same masking is
   written `x != null ? x : 0`, which also compiles and evaluates (the probe:
   `a / b != null ? a / b : 0` with `b = 0` gives `0`). And a nullable input (FR-213's
   `nullable`) needs a coalescing form. The steer for "one spelled, specified form" is met:
   `??` becomes that one form, because `coalesce(` cannot compile. What makes a masked null dangerous is controlled
   elsewhere, and this ruling states each control:
   - **`??` is never a division guard.** FR-274 requires an explicit zero guard on every
     division. `a / b ?? 0` must stay refused as `EXPRESSION_UNGUARDED_DIVISION`, and so must
     `a / b != null ? a / b : 0`. `_GUARD_MARKERS` must never gain `??` or `!= null`. Its two
     entries that can never occur in a compiling, allow-listed string, `?:` and `coalesce(`,
     are dead and are removed, so that no one reads them as protection.
   - **`??` is not a `table` or `lookup` step's miss policy.** A miss is declared by the
     step's `on_miss` (`03` §4.1). The HIGH finding above is closed upstream, by the WK-1178
     fix's compile refusal of an unpinned or wrong-version step. `??` downstream of a table
     or lookup step is permitted, but it is not how a miss is handled.
3. **The check covers every authored string.** FR-276's engine compile is widened from `expr`
   to `condition`, clamp bounds and `key_expr`. Today none of those is compiled at save (the
   table above), so an authored `??`, or a function, in a condition would be met only at
   scoring. **FR-274's division-guard check is widened the same way.** `_check_division_guards`
   (`compile.py:166-193`) also reads only `expr`, and its test is a substring match against
   `_GUARD_MARKERS` (`:179-181`). Verified by reading it: `a / b ?? 0` and
   `a / b != null ? a / b : 0` carry no marker and are refused today, and
   `x != 0 ? y / x : 0` passes on `"!= 0"`.

### The amended FR-244 text — the Slice 1 leaf plan's Task 6 held sentence

WK-690 Slice 1's Task 6 appends this to FR-244's cell, **in place of** the held sentence
(the leaf plan's lines 1538-1543 at `57a4833e`). The `02` §4.6 note of Task 6, Step 2 is unchanged. Nothing is struck:

> **Amended 2026-09-30, `RL-1265` DP-5 and `RL-1312`:** the rating grammar is FR-244's own:
> ZEN's expression language, **restricted to an enforced allow-list of operators and
> functions** and verified against the engine by FR-276. It shares function names with
> `02` §4.6 where they coincide, but it is not one of §4.6's profiles, and
> `pricing_core.data.expressions` never parses it. **Operators:** `+ - * /` (and unary `-`),
> parentheses, `== != < <= > >=`, `and or not`, the ternary `c ? a : b`, and `??`, which
> returns its right operand when its left is null. It is the coalescing form the function
> list above names `coalesce(a, b)`, and it is never a division guard (FR-274).
> **Literals:** numbers, `true`, `false`, `null` and single-quoted strings. **Functions:**
> `min([…])`, `max([…])` and `abs`. **No rounding function** (`round`, `floor`, `ceil`): money
> is rounded only by an `output` step's declared rounding (FR-226), never twice (NFR-496).
> Whether rounding is offered anywhere else is an open question (`03` §10, `OQ-1316`).
> The list above states intent that the engine does not meet. `coalesce(a, b)` is written
> `a ?? b`, `clip(x, lo, hi)` is `min([max([x, lo]), hi])`, `round(x, mode, dp)` is the
> output step's rounding, `band` is a `table` step with a banded key (FR-228), and
> `date_diff_years` is an input (FR-246). The allow-list binds every authored rating string
> (`expr`, `condition`, clamp bounds, `key_expr`), and anything outside it is refused at
> save with `EXPRESSION_INVALID_VOCABULARY`. **Numbers at the engine boundary:** inside ZEN,
> arithmetic is exact decimal (`0.1 + 0.2 == 0.3`).
> Callers pass money as integer minor units (FR-273). The binding refuses a `Decimal` input,
> and takes a `str` input as a string, never a number. Outputs return as floats and are taken
> through `_round_minor` (`Decimal(repr(x))`, quantized with the output step's declared mode).
> Integers above 2^53 at the boundary are untested. "The same restricted grammar as `02`
> §4.6" is superseded by this sentence.

## Which slice carries it

- **The spec: WK-690 Slice 1, Task 6**, as above. It is the FR-244 editor already, under
  RL-1265 DP-5, and it now writes this ruling's words. Its write set is unchanged: the FR-244
  row and the `02` §4.6 note. **Slice 1 changes no rating code and no `??` behaviour**, which
  keeps the bar on it as relayed.
- **The code: one WK-1178 slice, after the ~16:00 fix slice.** Both edit
  `packages/pricing-core/src/pricing_core/rating/compile.py`'s validation functions, so they
  are serialised (`RL-1263`). The slice adds:
  - the allow-list check (item 1);
  - the widened compile (item 3);
  - the removal of the dead guard markers (item 2), with their tests.

  WK-1178 is the standing rating maintenance Work, and it already holds this file's
  refusals. The planner cuts the slice, and the lead dispatches it.
- **The ~16:00 fix slice is not changed by this ruling.** It must not treat `??` as a guard,
  and it must not refuse `??`. Today it does neither.
- **The order is fixed by the maintainer** (the 10:53:10 BST entry): the fix slice (#963), then
  this ruling's WK-1178 code slice, then WK-1250 Slice 1. All three write `compile.py`. The
  condition and clamp-bound gap of item 3 is also filed as its own finding, by auditor-928, at
  MEDIUM rising to HIGH on reproduction. Its owner is this code slice, kept separate from the
  fix slice. Its acceptance adds: "a division guarded at save makes it unreachable; any
  residual runtime evaluation failure in a condition or bound raises its own evaluation code,
  never `RATE_TABLE_MISS`".

## What it obliges

- **This commit:** this record, and the new open question (`OQ-1316`) in `03` §10 and
  `docs/open-questions.md`. No FR-244 text changes here, because the FR-244 text is
  the Slice 1 leaf plan's Task 6, in its own commit with the `02` §4.6 note.
- **WK-690 Slice 1 (its leaf plan's Task 6):** the amended text above, in place of the held sentence.
- **WK-1178, a new slice after the fix slice:** items 1 to 3, with the acceptance below.
- **The lead:** routes the slice, and tells the WK-690 Slice 1 executor that Task 6's
  sentence is released in this wording.
- **The lead (the roadmap is the lead's file):** places `OQ-1316` on `docs/roadmap.md`
  §10's decision-gate table, at *Deferred / any time*, as `spec-change` requires of a new `OQ-`.

## Acceptance — the violation that must become detectable

Each is shown failing on deliberately broken input (`CLAUDE.md` §13), in the WK-1178 slice:
- **Refused at save with `EXPRESSION_INVALID_VOCABULARY`:** an `expr` using `%`, `in`, `a[0]`,
  `a.b`, `len('x')` or `sum([a, b])`, each case by its cause. With the allow-list check
  removed, each saves, and the test fails.
- **Refused at save** with `EXPRESSION_INVALID_VOCABULARY`: `round(p, 2)`, `floor(x)` and
  `ceil(x)`. The interim rule on rounding must be shown red, like any other refusal.
- **Accepted:** `a ?? 0`, `x != 0 ? y / x : 0`, `min([max([x, 0]), 1])` and
  `abs(x)`.
- **A `condition` with a function outside the list is refused at save.** Today it saves.
- **A `condition` or clamp bound that divides without a guard is refused** with
  `EXPRESSION_UNGUARDED_DIVISION`. Today it saves.
- **Still refused as `EXPRESSION_UNGUARDED_DIVISION`:** `a / b ?? 0` and
  `a / b != null ? a / b : 0`.
- **Dead markers:** with `?:` and `coalesce(` removed from `_GUARD_MARKERS`, every existing
  guard test passes unchanged.
- **Stored data:** the sweep's 37 distinct committed strings and the stored database and
  bundle strings all pass the allow-list. A test over the committed fixtures shows it.
