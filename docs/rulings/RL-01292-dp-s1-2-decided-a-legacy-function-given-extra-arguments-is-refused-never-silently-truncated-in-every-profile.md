---
id: RL-1292
family: ruling
title: DP-S1-2 decided — a legacy function given extra arguments is refused, never silently truncated, in every profile
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 095dd400918348b32ee6eab1db7915faaa9dfe35
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1268, RL-1184]
---

# RL-1292 — DP-S1-2 decided: extra arguments to a legacy function are refused

## How this was ruled

**Ruled at effort `medium`**, under the maintainer's pre-decision by delegation of
2026-09-30 08:48:15 BST (`to-lead.md`, entry headed "PRE-DECISION: the DM may rule
SL-1271's three DPs at MEDIUM effort, under the 08:00 basis, with an executable-evidence
condition"). It applies the 08:00 CHECKPOINT DECISION's basis. For this DP the condition
reads: "`abs(a, b)` (and one other legacy function) either **refused with a coded error**
or accepted as ruled. **Silently ignoring an argument an analyst wrote is the
mispricing-shaped outcome**". It also says that a choice to keep ignoring must be
justified against the transparency default (`CLAUDE.md` §1).

**Minted 2026-09-30 as RL-1292** (`doc-id.py next --ref origin/main` = 1292 at `7040cf1e`); it was prepared and ruled under working id 9972.

## Verified first, at 095dd400918348b32ee6eab1db7915faaa9dfe35

- **The decision point** is DP-S1-2 of SL-1271's leaf plan (#954, working id 9960; read at `4d2e78e8` and re-checked at `6853c1b3`, `:276`). Its
  question: "Do the legacy single-argument functions (`abs round floor ceil log exp sqrt`)
  keep ignoring extra arguments in `recipe` and `check`?"
  - (a) keeps them, "because `recipe` and `check` only add".
  - (b) enforces exact arity everywhere.
  - The plan recommends (a), "with the silent drop reported to the auditor as a finding
    candidate". It argues that (b) "could refuse an expression that works today, which the
    only-add rule forbids".
- **The code.** `_call` in `packages/pricing-core/src/pricing_core/data/expressions.py:228-253`
  returns `args[0].<fn>()` for all seven functions. `round` hard-codes `digits = 0`
  (`:235`). Every argument after the first is discarded without a message.
- **The only-add rule's source.** `PL-1268` Slice 1, Gate outline
  (`docs/plans/PL-01268-wk-690-expression-custom-objectives-map-plan.md:439-441`): "Every
  existing recipe and check test passes unchanged, which proves that the `recipe` and
  `check` profiles only add". The stronger wording, "every expression accepted at
  `fb90d381` is still accepted", is the leaf plan's own. It is not in `PL-1268`, in `02`,
  or in `01`.
- **Where arity would be stated.** `01` FR-36 (`docs/specs/01-data-management.md:93`)
  defines the recipe grammar as "the `recipe` profile in `02-modelling.md` §4.6's profile
  table". `01` §4.5's `expression` check uses the `check` profile. So the functions each
  profile admits, and their arity, are §4.6's to state.
- **Existing callers.** Nothing in the repository passes more than one argument to a legacy
  function in an expression string. The search was:
  `git grep -n -P '["'"'"'][^"'"'"'\n]*\b(abs|round|floor|ceil|log|exp|sqrt)\([^()"'"'"']*,[^"'"'"']*["'"'"']' origin/main -- packages/pricing-core/tests backend/tests examples frontend/src '*.json'`,
  run at `fb90d381`. It printed nothing (the expression-bearing files are unchanged at
  `095dd400`).
- **No catalogue rule uses the `expression` check** (SL-1271's leaf plan, premise b).

## Proof — executable, red on (a), green on the ruling

**Where it ran.**
- Scratch directory: `/home/puzhenhao1989/.claude/jobs/0081b83b/dm-s1-proofs/`, not
  committed.
- Environment: a worktree at `fb90d381` after `uv sync --all-packages`, Polars 1.44.2.
  `git diff --quiet fb90d381 095dd400 -- packages` → rc 0, so the code is identical at
  this record's tree.
- `test_dp_s1_2_legacy_arity.py` (sha256 prefix `568df6d3bd592bd1`) runs against the real
  `compile_expression`, with `DF = {"a": [-3.0, 2.5], "b": [10.0, 10.0], "x": [1234.5678, 100.0]}`:

```python
def test_abs_extra_arg_is_refused_with_a_coded_error():
    assert refused("abs(a, b)")                      # raises ExpressionError
def test_round_digits_argument_is_refused_or_honoured():
    assert refused("round(x, 2)") or ev("round(x, 2)") == [1234.57, 100.0]
def test_log_base_argument_is_refused_or_honoured():
    assert refused("log(x, 10)") or ev("log(x, 10)") == [math.log10(1234.5678), 2.0]
```

- `arity_patch.py` (sha256 prefix `6afe816f94f8307c`) is a pytest plugin. It applies the
  ruled rule to today's parser: `abs round floor ceil log exp sqrt` given any number of
  arguments other than one raise
  `ExpressionError(f"{name}() takes exactly 1 argument, got {n}", node=node)`.

**Commands and results** (2026-09-30 08:50:59 to 08:54:30 BST):

```text
# today's parser, option (a): the silent drop
$ uv run --no-sync pytest -q -p no:cacheprovider --rootdir=$S $S/test_dp_s1_2_legacy_arity.py
FAILED …test_abs_extra_arg_is_refused_with_a_coded_error - AssertionError: abs(a, b) accepted and evaluated as abs(a): [3.0, 2.5]
FAILED …test_round_digits_argument_is_refused_or_honoured - AssertionError: [1235.0, 100.0]
FAILED …test_log_base_argument_is_refused_or_honoured - AssertionError: [7.118476228297786, 4.605170185988092]
3 failed in 2.82s                                             rc=1
# the ruling, applied
$ PYTHONPATH=$S uv run --no-sync pytest -q -p no:cacheprovider -p arity_patch --rootdir=$S $S/test_dp_s1_2_legacy_arity.py
3 passed in 0.33s                                             rc=0
# only-add: the two existing parser test files, unmodified, under the ruling
$ PYTHONPATH=$S uv run --no-sync pytest -q -p no:cacheprovider -p arity_patch packages/pricing-core/tests/test_prepare.py packages/pricing-core/tests/test_expression_nfrs.py
38 passed, 4 warnings in 0.60s                                rc=0
# and the whole pricing-core suite under the ruling
$ PYTHONPATH=$S uv run --no-sync pytest -q -p no:cacheprovider -p arity_patch -x packages/pricing-core/tests
939 passed, 10 warnings in 136.48s (0:02:16)                  rc=0
```

**What (a) does today, on real code.**
- `round(x, 2)` rounds to **0** decimals: 1234.5678 → 1235.0, where the author asked for
  1234.57.
- `log(x, 10)` is the **natural** log: 7.118 where log₁₀ gives 3.09, and 4.605 where it
  gives 2.
- `abs(a, b)` is `abs(a)`.

Each is a derived column, or a check predicate, that computes something other than what the
analyst wrote, and nothing says so. In a preparation recipe, that reaches the modelled
data.

## Ruled

**Exact arity in every profile. A legacy function given extra arguments is refused.**
- `abs round floor ceil log exp sqrt` take exactly one argument in every profile. Any other
  count is refused with `ExpressionError`: the parser's existing refusal type,
  position-accurate under NFR-483, naming the function and the count.
- `min`, `max` and `coalesce` keep today's "at least one argument".
- The four new functions keep the leaf plan's exact arity.
- The leaf plan's option (b) is chosen, for the reason the maintainer's condition gives.

**Why not (a).** Keeping the silent drop cannot be justified against `CLAUDE.md` §1's
default ("Every design decision favours reproducibility, auditability, and transparency of
the maths"). The proof shows two ordinary analyst expressions, `round(x, 2)` and
`log(x, 10)`, computing a different number from the one written. A reviewer reading the
recipe would read the intended maths, not the executed maths.

**Why this does not break the only-add rule.** The rule's source (`PL-1268`) defines it
through the existing recipe and check tests. They pass unmodified under the ruling (38 of
38; 939 of 939 across `pricing-core`). No expression in the repository relies on the drop.
An expression that relied on it was already computing the wrong thing. Refusing it turns a
silent mispricing into a positioned error the author can fix.

**Not ruled here: honouring the argument.** `round(x, n)` or `log(x, base)` would be new
grammar. Adding it later is a pure addition, which the only-add rule permits. Refusal now
keeps that option open. Honouring it now would change the result of expressions that
compile today.

**Narrowness: narrow.**
- It states arity for functions that `02` §4.6's profile table already lists. `01` FR-36
  and `01` §4.5 take their grammar from that table, so no FR text beyond §4.6 changes.
- No published contract changes: no schema, no route, and no new error code (the existing
  `ExpressionError` path).
- No existing caller or test breaks.
- One effect is disclosed rather than asserted absent. An expression with an extra argument
  stored outside the repository, in a database of any environment, would be refused on its
  next compile. None exists in the repository. The refusal is the intended outcome.

## What it obliges

- **WK-690 Slice 1 (SL-1271's leaf plan, Task 3 Step 3, where arity is implemented):**
  - implements the rule;
  - states the arity of every function in `02` §4.6, dated, citing this record;
  - carries the tests below, each shown red first.
- **The planner (SL-1271's leaf plan, #954, working id 9960), not this commit.** Premise c, the DP-S1-2 row, and the
  acceptance line "every expression accepted at `fb90d381` is still accepted" should say
  that an expression relying on the silent drop is refused by this ruling. The leaf plan's
  "finding candidate" for the auditor is discharged by this record.

## Acceptance — the violation that must become detectable

- *Violation: `abs(a, b)` compiles, in any profile.*
- *Violation: `round(x, 2)` or `log(x, 10)` compiles.* This covers each of the seven legacy
  functions with two arguments; the refusal must be `ExpressionError` with a position.
- *Violation: an existing test in `test_prepare.py` or `test_expression_nfrs.py` needs
  modifying.* This is the only-add proof.
