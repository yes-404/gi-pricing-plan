---
id: PL-1295
family: plan
kind: leaf
title: WK-690 Slice 1 — the parser brought to §4.6's four profiles, with its limits and the sympy pin: leaf plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: fb90d381fae0f7cf8a92b09b56bb002dc6958e80
phase: P2
work: WK-690
slice: SL-1271
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1268, RL-1184, RL-1265, RL-1289]
---

# PL-1295 — WK-690 Slice 1 — the parser brought to §4.6's four profiles, with its limits and the sympy pin: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `python-package` (every code task), `python-test` (every task: requirement markers, negative tests), `spec-change` (Tasks 1, 3, 4 and 6), `library-spike` (Task 5's first step), `dev-commands` (the gate and its traps) and `git-hygiene`, and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Bring `pricing_core.data.expressions` to `02` §4.6's four named profiles (`objective`,
`factor`, `recipe`, `check`), with `where()` in every profile, the strict `objective` and
`factor` refusals, and the node-count and depth limits in all four. Translate the
`objective` profile to a SymPy tree, with `where()` as a `Piecewise`. Pin `sympy==1.14.0`,
and have the spec cite the pin.

**Architecture.** One parser with one allow-list walk. A `GrammarProfile` argument selects
the node set, the function set, the bound symbols and the arity rules. The limits are the
same for every profile. Two translators sit on the one validated tree: the existing Polars
translator (`recipe`, `check`, `factor`), and a new SymPy translator in its own module for
`objective`. The Polars path therefore never imports `sympy`. Existing callers keep their
behaviour: `recipe` and `check` only add, in the sense RL-1292 gives it: every
existing recipe and check test passes unmodified. A legacy function given extra
arguments, which computed a number different from the one written, is now refused.
*(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*

**Tech Stack:** Python 3.12 `ast`, Polars 1.44.2 (`uv.lock:1633`), SymPy 1.14.0 (new; its
only runtime dependency is `mpmath`), pytest. No pandas.

**Spec:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) §4.6, the profile table and its
  rules as amended by `RL-1184` E2 (`02:915-1038` at the tree above). §4.7's example
  (`:1069`) and §8's SymPy row (`:2842`) are for the pin only.
- `02` §3.7 **FR-144** (`02:208`), the 2026-09-28 amendment clause only: *"WK-690's first
  slice brings `pricing_core.data.expressions` to §4.6's `objective` profile before any
  objective is derived: `where()` compiled to a SymPy `Piecewise`; bare comparisons, `%`,
  ternaries and boolean operators refused outside `where`; and the node-count and depth
  limits enforced."* Derivation, storage and fit-time compilation are Slice 2's and 3's.
- `02` §3.7 **FR-145** (`02:209`), and `02` §9 **NFR-483**'s first two clauses (never
  `eval`; position-accurate refusal). Its third clause (FR-165's budget) is Slice 2's.
- [`../specs/01-data-management.md`](../specs/01-data-management.md) **FR-36** (the `recipe`
  profile) and §4.5's `expression` check row (`01:487`, the `check` profile).
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) **FR-244** (`03:146`), for
  `RL-1265` DP-5's amendment only.

**What this plan implements.** `PL-1268` Slice 1 and its row `SL-1271`, with the rulings
that bind it:
- `RL-1265` DP-5 puts `filter_rows` on `recipe`, and amends `03` FR-244 with a matching
  `02` §4.6 note in one commit.
- `RL-1265` also requires one exact pin, with §4.6 and §4.7 citing it.
- `RL-1289` fixes the pin at `sympy==1.14.0`. Its form is a `pyproject.toml` `==` pin, the
  same as `hypothesis`. `02` §4.6, §4.7 and §8 and `skills-map.md` cite the lock **in the
  same commit as the pin**.
- **How this plan reads `RL-1289`'s "in one commit with the code".** The code is the pin:
  `packages/pricing-core/pyproject.toml` and `uv.lock`. Task 1 is that one commit, and it
  carries the pin, the four spec and `skills-map.md` citations, and the pin's own test
  (`tests/test_sympy_pin.py`). The parser and the SymPy translator follow in later commits
  (Tasks 3 to 5). The ruling's reason (ruling 4 and "No `FR-` is appended") is that the
  spec must not cite a pin the lock does not yet hold, and one commit holding both pin and
  citations meets that reason. The `sympy.*` mypy override in Task 1 is **this plan's
  addition**, not a ruling's. It uses the form of the `sklearn.*` and `interpret.*`
  entries at `pyproject.toml:149-158`, because `mypy --strict` cannot pass without it
  (premise e). *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F4.)*

## Status

**Draft**, filed 2026-09-30 against `fb90d381` (origin/main). Minted 2026-09-30 as PL-1295 (`doc-id.py next --ref origin/main` = 1295 at `48792023`); it was drafted under working id 9960. DP-S1-1 to DP-S1-3 below are decision
points for the decision-maker, one `RL-` each, ruled at medium effort, each with an
executable red/green proof. Each is resolved before this plan's activation, and applied at
the task its row names (`document-ids.md` §1.7). **All three are now ruled**, each by its
own record, merged: DP-S1-1 by RL-1291 (#956), DP-S1-2 by RL-1292 (#957), DP-S1-3 by RL-1293 (#958). *(Revised 2026-09-30 on the decision-maker's rulings RL-1291, RL-1292 and RL-1293, #956 to #958.)* *(Revised 2026-09-30 on the maintainer's pre-decision, relayed by the lead: the decision-maker rules each at medium effort, one `RL-` each, each with an executable red/green proof.)* *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F1.)*

**Gates, both verified at `fb90d381`:**
1. `RL-1265` is on main (`docs/rulings/RL-01265-…md`, merged by #847 at `a6146ec4`).
2. OQ-1266 is ruled: `RL-1289` (merged by #937, the tip of main at `fb90d381`) decides it
   as `sympy==1.14.0`. `docs/open-questions.md:119` shows OQ-1266 struck through, citing
   `RL-1289`.

**File contention under `RL-1263` option (c), checked at `fb90d381`.** This slice writes:
- code: `packages/pricing-core/pyproject.toml`, `uv.lock`, root `pyproject.toml` (one mypy
  override), `pricing_core/data/expressions.py`, the new
  `pricing_core/data/expression_sympy.py`, one line in each of `pricing_core/data/prepare.py`
  and `pricing_core/data/validate.py`, and tests;
- docs: `02` §4.6, §4.7's example and §8's SymPy row; `03` §3.5 (the FR-244 row only);
  `docs/skills-map.md`'s SymPy row; the ledger; and `docs/INDEX.md`.

Against the other lane:
- **WK-674 Slice 2** (`SL-1256`, lane A's next slice, waiting on OQ-1234, which has a
  prepared ruling on #935) writes the Environment and Deployment record: `model-schema`,
  the backend, `07` §3.5, and `03` §3.10 with new §4 contracts. `PL-1237:49` says *"no new
  dependency is planned"*. So it edits no existing definition that this slice edits.
- **Two shared paths are not on the registry list**, and each needs the lead's dispatch
  record under option (c):
  - `docs/specs/03-rating-engine.md`: this slice edits only the FR-244 row in §3.5, and
    WK-674 Slice 2 edits §3.10 and §4.
  - `uv.lock` (with `docs/skills-map.md`): any concurrent dependency change conflicts. None
    is planned by WK-674 Slice 2, or by WK-1178's `PL-1279` (which creates only
    `tests/test_permission_parity.py`), or by any open PR at the time of writing (`gh pr
    list --state open`, 11 PRs: none touches `uv.lock`, a `pyproject.toml`, `02`, `03`,
    `skills-map.md` or `pricing_core/data/`). A Dependabot bump would conflict, so the lead
    holds dependency PRs while this slice is open.
- **Verdict: file-clean for lane-B dispatch beside WK-674 Slice 2**, provided the dispatch
  record names those two paths with the check above.
- **The three-pair contention measurement** in `RL-1263` is about the machine, not about
  files. It binds the first three concurrent gate pairs whatever they are. If this slice's
  gate is in one of those pairs, the lead records wall-clock, load and `free -h` for it as
  that ruling says.
- **Task 2 is not a timing measurement.** It counts AST nodes, which is deterministic and
  independent of machine load. So on this plan's reading it is not a "measurement step" in
  the sense of `RL-1263` item 3. That reading is the lead's to confirm at dispatch.

- **This slice resolves FD-1294** (#959, HIGH). On main today the parser
  silently drops extra arguments to the seven legacy functions (premise c), and that finding
  records it. It resolves at this slice's merge, and Acceptance 12 is its proof through all
  three reachable callers. *(Revised 2026-09-30 on the maintainer's ruling "DATA CHECK 0 ACCEPTED" (to-lead.md), relayed by the lead: DP-S1-2's defect is FD-1294, #959, severity HIGH, live on main; this slice is its fix.)*
- **Activation: the condition is met, and the plan is `active` from this commit.** Every
  blocking row has its resolver id (`document-ids.md` §1.7): RL-1291 (DP-S1-1, merged
  09:23 BST, #956, `7040cf1e`), RL-1292 (DP-S1-2, merged 09:43 BST, #957, `7c354305`) and
  RL-1293 (DP-S1-3, merged 10:04 BST, #958, `eeda8f4b`), all on 2026-09-30. The merge
  carries the maintainer's MERGE-ACK. A leaf plan takes no acceptance line. ~~_pending. The
  plan goes `active` once RL-1291, RL-1292 and RL-1293 are merged and minted …_~~ *(Revised 2026-09-30 on auditor-plans2's audit at
  dc49b9d9, finding F9, and the maintainer's ruling that a leaf plan takes no acceptance line,
  the same ruling as #929 / `PL-1278`. It read "…then the maintainer's acceptance".)*

## Acceptance Standard

A fresh reviewer checks each item by the command given, on the slice's final tree.

1. **The pin is exact and single.** `uv run pytest tests/test_sympy_pin.py -q` passes. The
   file includes the broken-input cases of Task 1 (absent, `1.13.3`, two entries), each
   shown red first in the ledger. `grep -n '"sympy==1.14.0"' packages/pricing-core/pyproject.toml`
   prints one line. `uv run python -c "import sympy; print(sympy.__version__)"` prints
   `1.14.0`.
2. **The pin and its spec citations are one commit** (`RL-1289` ruling 2). `git show --stat
   <Task 1 commit>` lists `packages/pricing-core/pyproject.toml`, `uv.lock`,
   `docs/specs/02-modelling.md` and `docs/skills-map.md`.
3. **No uncited sympy version literal remains in `02` §4.6 or §4.7** (`RL-1289`,
   Acceptance, third violation). `sed -n '/^### 4.6/,/^### 4.8/p' docs/specs/02-modelling.md
   | grep -n -E '1\.1[0-9]\.[0-9x]'` prints exactly these hits, and a reviewer checks each:
   - §4.6's example line `"derivation_version": "1.14.0"`;
   - §4.7's example line `"library_versions": {"sympy": "1.14.0", …}`;
   - lines inside the dated `RL-1289` note after §4.6's example, which names `==1.14.0` and
     "The example's `1.14.0` is that pin". The §4.7 note carries no version literal, so
     it produces no hit. *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F5.)*
   Any other hit is a violation. `02:2842`'s SymPy row names the pin together with
   `uv.lock` and `RL-1289`.
4. **The corpus was measured before the limits were enforced** (`PL-1268` Acceptance 4).
   The ledger holds Task 2's table. `git merge-base --is-ancestor <Task 2 commit> <Task 4
   commit>` exits 0. If any corpus expression exceeds a limit, the lead's record of the
   deputy's decision predates the Task 4 commit.
5. **Every refusal was seen failing first** (`PL-1268` Acceptance 5). The ledger quotes each
   of these red, then green:
   - in `objective` and `factor`: bare comparison, `%`, ternary and boolean operator;
   - node count 201 and depth 21, in all four profiles;
   - an unknown function, and an unknown symbol in a strict profile;
   - a legacy single-argument function given two arguments (`abs(a, b)`, `round(x, 2)`,
     `log(x, 10)`, and each of the seven), in every profile that admits the function.
     *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*
   Each has a positive control, as in Tasks 3 and 4: the same string accepted where the
   rule does not bind.
6. **`recipe` and `check` only add.** Every test that exists at `fb90d381` in
   `packages/pricing-core/tests/test_prepare.py` and `test_expression_nfrs.py` (the two
   files that call the parser, premise a) passes unmodified: `git diff fb90d381 -- <those two
   files>` is empty.
7. **The call sites pass their profiles.** `uv run pytest
   packages/pricing-core/tests/test_expression_profiles.py -q -k call_site` passes: the
   spies show `derive_expression` and `filter_rows` pass `recipe` and the `expression`
   check passes `check`.
8. **The objective profile reaches SymPy through the platform's own tree, never `eval`.**
   `uv run pytest packages/pricing-core/tests/test_expression_sympy.py -q` passes, including
   the test with `eval`, `exec` and `sympy.parsing.sympy_parser.parse_expr` all replaced by
   functions that raise, together with its positive control (`sympify` trips the raiser).
   The raiser test also passes alone: `uv run pytest
   packages/pricing-core/tests/test_expression_sympy.py -k never_reaches -q` in a fresh
   process, with its unpatched warm-up (*F7, revised 2026-09-30 on auditor-plans2's delta
   audit at 1296d9dc*).
   `uv run pytest packages/pricing-core/tests/test_expression_hostile_inputs.py -q` passes:
   NFR-483's hostile set is refused, with a position, in all four profiles. *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F2 and F3.)*
9. **`pricing-core` stays standalone.** `uv run lint-imports` passes, and
   `git grep -n -E '^\s*(import|from) sympy' -- packages/pricing-core/src` names only
   `expression_sympy.py`. No new code imports pandas:
   `git diff fb90d381 -- packages | grep -E '^\+.*import pandas'` prints nothing.
10. **Both halves of the gate pass** on the final tree (`CLAUDE.md` §11). The ledger quotes
    every rc, and pytest's `N passed` against main's `N passed` at `fb90d381`. A total that
    did not rise means the new tests were not collected.
11. **The slice closes on its clean audit and the lead's merge on the maintainer's
    MERGE-ACK** (`.claude/roles/lead.md` rule 4; `CLAUDE.md` §13).
12. **Finding FD-1294 is fixed at every reachable caller, not only in the parser.**
    `uv run pytest packages/pricing-core/tests/test_expression_profiles.py -q -k
    through_the_callers` passes. `round(y, 2)` is refused with a positioned `ExpressionError`
    through a `derive_expression` recipe step (`prepare.py:167`), a `filter_rows` recipe step
    (`prepare.py:170`) and an `expression` validation check (`validate.py:1892-1899`). Each
    test is shown red first in the ledger: at `fb90d381` the call silently succeeds. *(Revised 2026-09-30 on the maintainer's ruling "DATA CHECK 0 ACCEPTED" (to-lead.md), relayed by the lead: DP-S1-2's defect is FD-1294, #959, severity HIGH, live on main; this slice is its fix.)*

## Global Constraints

- `pricing-core` imports no web, database, queue or cloud client (`.importlinter`, contract
  `core-has-no-infrastructure`; `CLAUDE.md` §2). SymPy and `mpmath` are neither.
- No pandas in new code (`CLAUDE.md` §3).
- User input never reaches `eval` or `exec` (NFR-483). `sympy.sympify`, `sympy.parse_expr`
  and `sympy.lambdify` are never called on user text. The objective tree is built node by
  node from the validated `ast` (`02` §8: *"lambdify-free code generation into our own
  expression tree"*).
- One parser, one allow-list walk and one security review, with a named profile per
  context (`02` §4.6 as amended by `RL-1184` E2). No second parser.
- The limits are node count ≤ 200 and depth ≤ 20, configurable (FR-145, §4.6), in all
  four profiles.
- `recipe` and `check` only add, as `PL-1268` Slice 1's Gate outline defines it: every
  existing recipe and check test passes unmodified. ~~Every expression accepted at
  `fb90d381` is still accepted and gives the same result.~~ That stronger wording was this
  plan's own, and it is false under RL-1292. An expression relying on the silent
  drop of extra arguments (premise c) is now refused. RL-1292 records that no
  expression in the repository relies on it, and that such an expression was already
  computing a different number from the one written. *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*
- The sympy version recorded anywhere comes from the pin: `==1.14.0` in
  `packages/pricing-core/pyproject.toml`, and cited from `uv.lock` in the spec (`RL-1289`).
- Requirement ids are permanent. Spec edits go through `.claude/skills/spec-change`, dated,
  in the same commit as the code they describe (`CLAUDE.md` §2 and §5).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice owes | Task |
|---|---|---|---|
| `02` §3.7 | FR-144 | The 2026-09-28 amendment clause: the `objective` profile; `where()` as a SymPy `Piecewise`; the strict refusals; the limits | 3, 4, 5 |
| `02` §3.7 | FR-145 | The allow-list walk; the ten functions; the node cap, default 200 | 3, 4 |
| `02` §4.6 | profile table and OQ-1185 | Four profiles; `where()` everywhere; strict `objective` and `factor`; limits in all four; the DP-5 notes | 3, 4, 6 |
| `02` §9 | NFR-483 | Never `eval`; a position-accurate refusal, in every profile | 3, 5 |
| `01` §3.2 | FR-36 | `derive_expression` and `filter_rows` in the `recipe` profile | 3 |
| `01` §4.5 | `expression` check | The row predicate in the `check` profile | 3 |
| `03` §3.5 | FR-244 | `RL-1265` DP-5: the rating grammar is FR-244's own, not a §4.6 profile | 6 |

`RL-1289` adds no FR. The pin is Task 1.

### Premises re-derived at `fb90d381`

a. **The parser has three source call sites**, plus two test files. The sites are
   `prepare.py:167` (`derive_expression`), `prepare.py:170` (`filter_rows`) and
   `validate.py:1899` (the `expression` check, imported lazily at `:1892`). The test files
   are `test_prepare.py` and `test_expression_nfrs.py`. *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F6.)* Measured with
   `git grep -n -E "compile_expression|referenced_columns" -- packages backend examples`.
   The backend imports the parser nowhere. The `"type": "expression"` rating steps go to
   ZEN (`rating/compile.py:245`), not to this parser.

b. **The `expression` check has no test.** `test_builtin_rule_checks.py:38` asserts that
   `expression` is a check *no catalogue rule uses*, and
   `git grep -n 'CHECKS\["expression"\]' -- packages` prints nothing. This is a missing
   neighbour ([`README.md`](README.md)), so Task 3 adds the first test that runs the check.

c. **Legacy functions ignore extra arguments, and RL-1292 ends it.** `_call` reads
   `args[0]` for `abs`, `round`, `floor`, `ceil`, `log`, `exp` and `sqrt` (`expressions.py`,
   `_call`), so `abs(a, b)` is `abs(a)`. The ruling's proof shows `round(x, 2)` rounding to
   0 decimals, and `log(x, 10)` giving the natural log. The seven now take exactly one
   argument in every profile. `min`, `max` and `coalesce` keep "at least one". Honouring
   `round(x, n)` or `log(x, base)` is not ruled, and would be a later pure addition. *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*

d. **Chained comparisons are refused already**, at translation (`_translate`'s
   `ast.Compare()` case), with "chained comparisons are not permitted; use `and`".

e. **sympy 1.14.0 ships no `py.typed`**, checked by a `uvx` spike. `mypy --strict` therefore
   needs an override, in the form the `sklearn.*` and `interpret.*` entries use
   (`pyproject.toml:149-158`).

f. **Polars 1.44.2 has `Expr.log1p` and `Expr.clip` with expression bounds, and no
   `Expr.expm1`**, checked by a spike on 1.39.0 and the lock's 1.44.2 API. So the Polars
   translation of `expm1(x)` is `x.exp() - 1`.

g. **SymPy 1.14.0 facts**, checked by a `uvx --with sympy==1.14.0` spike:
   - `sympy.codegen.cfunctions.log1p` and `expm1` exist, and differentiate to `1/(x + 1)`
     and `exp(x)`.
   - `diff(Abs(g), g)` is `sign(g)` for a real symbol, and
     `(re(g)*Derivative(re(g), g) + im(g)*Derivative(im(g), g))*sign(g)/g` for a plain one.
     This is DP-S1-3.

h. **Node counts under the two predicates of DP-S1-1**, from the same spike. The first two
   figures are `ast.expr` nodes and depth. The third is every node `ast.walk` yields.
   - `a + b`: 3, 2 and 6.
   - `min(x, …)` with 198 arguments: 200, 2 and 399. With 199 arguments: 201, 2 and 401.
   - 19 nested `abs(…)` around `x`: 39, 20 and 59. With 20 nested: 41, 21 and 62.
   - §4.6's example loss: 19, 6 and 34.

i. **`Profile` is taken.** `pricing_core.data.profile` imports `Profile` (the dataset
   profile), so the new enum is `GrammarProfile`.

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S1-1 | What does §4.6's "AST node count ≤ 200; nesting depth ≤ 20" count? | **(a)** `ast.expr` nodes only (the sub-expressions an author wrote: names, literals, calls, operations), with depth as the longest chain of nested `ast.expr` nodes, the root at 1. **(b)** Every node `ast.walk` yields, including operator tokens and `Load` contexts, with depth over the same. | **(a).** It is what an author can count. Under (b), `a + b` is 6 nodes, and 200 means about 100 written terms, a limit the spec did not state. ~~Task 2 measures both, so the ruling can be made from data.~~ Premise h's spike figures, measured at `fb90d381`, inform the ruling. Task 2 re-measures the corpus under both predicates after it. *(Revised 2026-09-30 on auditor-plans2's audit at c76faa22, finding F8: the ruling now comes before activation, so before Task 2 runs.)* | decision point: it interprets what §4.6's limit means, and a measurement informs it but cannot settle it | **yes, for activation.** Resolving step: the plan's activation. Applied at Task 4 (Steps 1, 3 and 4); Task 4 Step 1 names the constants that change under (b). Task 2 measures both predicates either way | **RL-1291** (#956, decision-maker, medium, red/green proof): **(a)**, `ast.expr` nodes, depth the longest `ast.expr` chain with the root at 1, refused above 200 nodes or 20 deep in all four profiles. *(Revised 2026-09-30 on the decision-maker's ruling RL-1291, #956.)* |
| DP-S1-2 | Do the legacy single-argument functions (`abs round floor ceil log exp sqrt`) keep ignoring extra arguments in `recipe` and `check` (premise c)? | **(a)** Keep them, because `recipe` and `check` only add. Exact arity binds the four new functions in every profile, and every function in `objective` and `factor`. **(b)** Enforce exact arity everywhere. | **(a)**, with the silent drop reported to the auditor as a finding candidate. (b) could refuse an expression that works today, which the only-add rule forbids. | decision point: a behaviour choice for existing callers | **yes, for activation.** Resolving step: the plan's activation. Applied at Task 3 Step 3 (where arity is implemented) | **RL-1292** (#957, decision-maker, medium, red/green proof): **(b), against this plan's recommendation.** Exact arity: the seven legacy functions take exactly one argument in every profile, and any other count is an `ExpressionError` with a position. `min`, `max` and `coalesce` stay at least one. The finding candidate this row proposed is discharged by the ruling. *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)* |
| DP-S1-3 | What SymPy assumptions do the objective symbols (`y`, `f`, `w`, parameters) carry? | **(a)** `real=True`. **(b)** None. | **(a).** §4.6's domains are real (`y_domain`, raw score `f`, weight `w`). Without the assumption, `Abs` differentiates to the complex form in premise g, and that would become the canonical text Slice 2 records. | decision point: it fixes the canonical derived text a reviewer approves | **yes, for activation.** Resolving step: the plan's activation. Applied at Task 5 Step 4 (where the symbols are created). Slice 2 inherits it | **RL-1293** (#958, decision-maker, medium, red/green proof): **(a)**, `real=True` for `y`, `f`, `w` and every parameter. *(Revised 2026-09-30 on the decision-maker's ruling RL-1293, #958.)* |

*(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F1.)* The three rows were filed as kind *fact*. They are decisions: an interpretation of the spec, a behaviour choice and a canonical-form choice. So their resolver is the decision-maker (`document-ids.md` §1.7). *(Revised 2026-09-30 on the maintainer's pre-decision, relayed by the lead: the decision-maker rules each at medium effort, one `RL-` each, each with an executable red/green proof.)* Each row is ruled before activation and applied at its named task. The recommendations are unchanged. The executor cites each `RL-` id at its task and in the ledger.

## Tasks

The tasks run in order. Each ends in one commit. Task 1 is `RL-1289`'s commit, Task 2
records the table that Task 4 must descend from, and Task 6 is `RL-1265` DP-5's
paired-spec commit.

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree, and `git branch --show-current` is the slice branch
  (created from `origin/main`).
- [ ] `uv sync --all-packages` (`dev-commands`: without `--all-packages`, a fresh worktree
  reports hundreds of phantom mypy errors).
- [ ] Record main's pytest total: `uv run pytest -q 2>&1 | tail -1` at `origin/main`, quoted
  in the ledger (Acceptance 10).
- [ ] Re-derive premises a–i at the slice's base. Record the tree and each result in the
  ledger.
- [ ] `gh pr list --state open`. Read anything that touches `pricing_core/data/`,
  `uv.lock`, any `pyproject.toml`, `02` §4.6–§4.8, `03` §3.5 or `skills-map.md`, and anything
  that rules on DP-S1-1 to DP-S1-3 ([`README.md`](README.md) convention 4). Name the SHA
  read.
- [ ] Create the slice ledger (`LG-`, the executor's; `document-ids.md` §1.6). Take a working
  id from `python3 scripts/doc-id.py next`, and reconcile it with the lead.

### Task 1: The sympy pin, with its spec citations — one commit (`RL-1289`)

**Files:**
- Create: `tests/test_sympy_pin.py`
- Modify: `packages/pricing-core/pyproject.toml` (`dependencies`, after the `hypothesis`
  pin)
- Modify: `uv.lock` (regenerated by `uv lock`, never by hand)
- Modify: `pyproject.toml` (a `[[tool.mypy.overrides]]` entry for `sympy.*`, beside
  `interpret.*`)
- Modify: `docs/specs/02-modelling.md`: §4.6's example and the prose after it, §4.7's
  example (`:1069`), and §8's SymPy row (`:2842`)
- Modify: `docs/skills-map.md` (the SymPy row, `:67`)

**Interfaces:**
- Produces: `sympy` importable in the workspace at exactly `1.14.0`.
- Produces: `tests/test_sympy_pin.py::lock_violations(lock_text: str) -> list[str]`, used
  only in this file.

- [ ] **Step 1: Write the failing test.** Create `tests/test_sympy_pin.py`:

```python
"""RL-1289: `sympy` is pinned at exactly 1.14.0, once, in the lock and in pricing-core.

The violation the ruling names is "the derivation version the platform records differs from
the sympy actually pinned". Its first half is checked here: `uv.lock` resolves exactly one
`sympy`, at `1.14.0`, and `pricing-core` declares it with `==`. The checker is a function of
the lock text, so the broken-input cases below run the same code as the real-tree case.
"""

from __future__ import annotations

import pathlib
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PINNED = "1.14.0"


def lock_violations(lock_text: str) -> list[str]:
    """Every way `lock_text` fails RL-1289's pin. An empty list means it holds."""
    packages = tomllib.loads(lock_text).get("package", [])
    versions = [p.get("version") for p in packages if p.get("name") == "sympy"]
    if not versions:
        return ["sympy is absent from the lock"]
    problems = []
    if len(versions) > 1:
        problems.append(f"the lock resolves sympy {len(versions)} times: {versions}")
    problems += [f"the lock resolves sympy {v}, not {PINNED}" for v in versions if v != PINNED]
    return problems


def test_the_lock_resolves_sympy_exactly_once_at_the_pin() -> None:
    assert lock_violations((ROOT / "uv.lock").read_text()) == []


def test_pricing_core_declares_the_exact_pin() -> None:
    project = tomllib.loads((ROOT / "packages/pricing-core/pyproject.toml").read_text())
    assert f"sympy=={PINNED}" in project["project"]["dependencies"]


@pytest.mark.parametrize(
    ("lock_text", "expected"),
    [
        ('[[package]]\nname = "polars"\nversion = "1.44.2"\n', "absent"),
        ('[[package]]\nname = "sympy"\nversion = "1.13.3"\n', "not 1.14.0"),
        (
            '[[package]]\nname = "sympy"\nversion = "1.14.0"\n'
            '[[package]]\nname = "sympy"\nversion = "1.13.3"\n',
            "2 times",
        ),
    ],
)
def test_a_broken_lock_is_reported(lock_text: str, expected: str) -> None:
    """The checker on deliberately broken input. Without these, a checker that returns
    `[]` for everything would pass the real-tree test above."""
    assert any(expected in problem for problem in lock_violations(lock_text))
```

- [ ] **Step 2: Run it and see it fail for the right cause.** Run
  `uv run pytest tests/test_sympy_pin.py -q`. Expected:
  - `test_the_lock_resolves_sympy_exactly_once_at_the_pin` fails with `['sympy is absent
    from the lock']`;
  - `test_pricing_core_declares_the_exact_pin` fails on the `in` assertion;
  - the three broken-lock cases **pass**, which proves the checker works before the pin
    exists.
  Any other failure (a collection error, a `tomllib` error) is a defect in the test, not the
  red this step wants. Quote the output in the ledger.
- [ ] **Step 3: Pin.** In `packages/pricing-core/pyproject.toml` `dependencies`, directly
  after `"hypothesis==6.165.7",`, add:

```toml
    # RL-1289 (OQ-1266): SymPy derives the `expression` objective's gradient and hessian
    # (02 FR-144), and the certificate records its version from `sympy.__version__`.
    # Pinned exactly, because an upgrade can change the canonical derived text a reviewer
    # approved (02 §4.6). Its one runtime dependency is mpmath. No web, database or queue
    # client, so the import-linter contract holds (ADR-703).
    "sympy==1.14.0",
```

  Then run `uv lock`, and confirm with `git diff uv.lock | grep -E '^\+name = '` that the
  lock gains `sympy` and `mpmath` and nothing else. Then run `uv sync --all-packages`.
- [ ] **Step 4: The mypy override.** In the root `pyproject.toml`, after the
  `interpret.*` override, add:

```toml
# sympy 1.14.0 ships no `py.typed` marker (RL-1289's pin), the same shape as the two above.
# Only `pricing_core.data.expression_sympy` imports it, and it builds SymPy objects from a
# validated `ast` tree, so the untyped surface is that one module's.
[[tool.mypy.overrides]]
module = ["sympy.*"]
ignore_missing_imports = true
```

- [ ] **Step 5: The spec citations** (`spec-change`; dated; this commit).
  - **`02` §4.6.** Leave the example's `"derivation_version": "1.14.0"` as it is. After
    the paragraph that begins "The `derived` block is generated by the platform", add:

    > *(Amended 2026-09-30, `RL-1289`: `derivation_version` is the `sympy` version pinned
    > in `uv.lock`, `==1.14.0` in `packages/pricing-core/pyproject.toml`. The platform
    > reads it at derivation time from `sympy.__version__`, never from a literal in code.
    > The example's `1.14.0` is that pin.)*

  - **`02` §4.7.** In the example, change `"library_versions": {"sympy": "1.13.x", …}` to
    `"library_versions": {"sympy": "1.14.0", …}`. After the example, add:

    > *(Amended 2026-09-30, `RL-1289`: `library_versions.sympy` is the version pinned in
    > `uv.lock`, read from `sympy.__version__`. The example's former value was a version
    > range with no recorded rationale, and it is replaced by the pin.)*

  - **`02` §8, the SymPy row.** Append to the "What" cell: *"Pinned `==1.14.0` in
    `packages/pricing-core/pyproject.toml` and resolved once in `uv.lock` (`RL-1289`,
    2026-09-30)."*
  - **`docs/skills-map.md:67`.** In the SymPy row, change "**Verified on 1.14.0:**" to
    "**Pinned `==1.14.0` (`RL-1289`, 2026-09-30); verified on 1.14.0:**".
- [ ] **Step 6: Green.** Run `uv run pytest tests/test_sympy_pin.py -q`: every test passes.
  Run `uv run python -c "import sympy; print(sympy.__version__)"`: it prints `1.14.0`.
  Run `uv run mypy`, `uv run lint-imports` and `python3 scripts/audit-docs.py`, and quote
  each rc. Run Acceptance 3's `sed | grep` and quote its output.
- [ ] **Step 7: Commit, one commit, all six files.**

```bash
git add tests/test_sympy_pin.py packages/pricing-core/pyproject.toml uv.lock pyproject.toml \
  docs/specs/02-modelling.md docs/skills-map.md
git commit -m "build(pricing-core): pin sympy==1.14.0 and cite the lock in 02 §4.6/§4.7/§8 (RL-1289, WK-690 S1)"
```

### Task 2: The node and depth counter, and the corpus measurement

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/expressions.py` (add
  `ExpressionSize`, `measure_expression`, `_measure`; nothing enforces them yet)
- Create: `packages/pricing-core/tests/test_expression_limits.py`
- Modify: the slice ledger (the measurement table)

**Interfaces:**
- Produces: `ExpressionSize` (frozen dataclass: `nodes: int`, `depth: int`,
  `all_nodes: int`), `measure_expression(expression: str) -> ExpressionSize`, and
  `_measure(root: ast.expr) -> tuple[ExpressionSize, ast.expr]`, which returns the size and
  the deepest node. Task 4 uses `_measure`.

- [ ] **Step 1: Write the failing test.** Create
  `packages/pricing-core/tests/test_expression_limits.py`:

```python
"""FR-145 and 02 §4.6: node count ≤ 200 and depth ≤ 20, in all four profiles.

The counts are over `ast.expr` nodes, with the root at depth 1. That is DP-S1-1's
(a), ruled by RL-1291. `all_nodes` is option (b), measured beside
it so the corpus table shows both predicates (F8). The
figures below are premise h's, from the spike at fb90d381.
"""

from __future__ import annotations

import pytest

from pricing_core.data.expressions import ExpressionSize, measure_expression


def _min_of(n: int) -> str:
    return "min(" + ", ".join(["x"] * n) + ")"


def _nested_abs(n: int) -> str:
    return "abs(" * n + "x" + ")" * n


@pytest.mark.req("FR-145")
@pytest.mark.parametrize(
    ("expression", "size"),
    [
        ("a + b", ExpressionSize(nodes=3, depth=2, all_nodes=6)),
        (_min_of(198), ExpressionSize(nodes=200, depth=2, all_nodes=399)),
        (_min_of(199), ExpressionSize(nodes=201, depth=2, all_nodes=401)),
        (_nested_abs(19), ExpressionSize(nodes=39, depth=20, all_nodes=59)),
        (_nested_abs(20), ExpressionSize(nodes=41, depth=21, all_nodes=62)),
        (
            "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
            ExpressionSize(nodes=19, depth=6, all_nodes=34),
        ),
    ],
)
def test_the_counter_measures_expr_nodes_and_depth(expression: str, size: ExpressionSize) -> None:
    assert measure_expression(expression) == size
```

- [ ] **Step 2: Run it and see it fail.** `uv run pytest
  packages/pricing-core/tests/test_expression_limits.py -q`. Expected: a collection
  `ImportError` naming `ExpressionSize`. That is the only acceptable red here, because the
  names do not exist yet.
- [ ] **Step 3: Implement the counter.** In `expressions.py`, add `from dataclasses import
  dataclass` and, after `ExpressionError`:

```python
@dataclass(frozen=True, slots=True)
class ExpressionSize:
    """An expression's size under 02 §4.6's limits (FR-145).

    `nodes` and `depth` count `ast.expr` nodes only, the root at depth 1 (DP-S1-1 (a), RL-1291).
    `all_nodes` counts every node `ast.walk` yields (option (b)). It is carried so that the
    corpus measurement records both predicates, and nothing enforces it.
    """

    nodes: int
    depth: int
    all_nodes: int


def measure_expression(expression: str) -> ExpressionSize:
    """The size of `expression`, parsed but not checked against any profile."""
    return _measure(ast.parse(expression, mode="eval").body)[0]


def _measure(root: ast.expr) -> tuple[ExpressionSize, ast.expr]:
    """Count iteratively, so a deep tree cannot exhaust Python's own stack here."""
    nodes, depth, deepest = 0, 0, root
    stack: list[tuple[ast.expr, int]] = [(root, 1)]
    while stack:
        node, level = stack.pop()
        nodes += 1
        if level > depth:
            depth, deepest = level, node
        stack.extend(
            (child, level + 1)
            for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.expr)
        )
    all_nodes = sum(1 for _ in ast.walk(root))
    return ExpressionSize(nodes=nodes, depth=depth, all_nodes=all_nodes), deepest
```

  Add `"ExpressionSize"` and `"measure_expression"` to `__all__`.
- [ ] **Step 4: Green.** Re-run the Step 2 command. All six cases pass.
- [ ] **Step 5: Measure the corpus.** The predicate is *every expression string that
  reaches `compile_expression` from a committed source*. There are two instruments,
  because the backend tests need the database stack:
  - **Runtime capture** over `packages/pricing-core/tests` and `examples/fremtpl2`. Write
    this plugin to `/tmp/capture_expressions.py`, outside the repository:

```python
import ast, json, os
import pricing_core.data.expressions as expressions

_seen: set[str] = set()
_real_parse = ast.parse

class _Recorder:
    def __getattr__(self, name):
        return getattr(ast, name)

    @staticmethod
    def parse(source, *args, **kwargs):
        if isinstance(source, str):
            _seen.add(source)
        return _real_parse(source, *args, **kwargs)

expressions.ast = _Recorder()  # the module reads `ast.parse` through this global

def pytest_sessionfinish(session, exitstatus):
    with open(os.environ["CAPTURE_OUT"], "w") as out:
        json.dump(sorted(_seen), out, indent=1)
```

    Run it with `CAPTURE_OUT=/tmp/corpus-runtime.json PYTHONPATH=/tmp uv run pytest -p
    capture_expressions packages/pricing-core/tests examples/fremtpl2 -q`.
  - **Static sweep** for the sources a runtime run cannot reach: `git grep -n -E
    '"(expression|expr)": *"' -- backend/tests examples '*.json'`. Keep only the hits whose
    step is `derive_expression` or `filter_rows`, or whose check is `expression`. Drop
    rating steps (`"type": "expression"` with a `step_id`), which ZEN compiles (premise a).
  - **Remove the hostile strings.** The union still includes the refusal tests' deliberately
    hostile inputs (for example `eval('1')`). List them separately, as *refusal fixtures*,
    and do not count them as corpus.
  - **Write the ledger table.** For each corpus string: its source file(s), and
    `measure_expression`'s `nodes`, `depth` and `all_nodes`. Add the class and total ("N
    distinct corpus expressions from M files; max nodes X, max depth Y"), not a sample.
- [ ] **Step 6: If any corpus expression exceeds 200 nodes or depth 20** under either
  predicate, stop. Report it to the lead for the deputy's decision (`02` §4.6's profile
  note; `RL-1184` E2 item 4), and do not start Task 4 until the lead records that decision.
- [ ] **Step 7: Commit** the counter, its test and the ledger table together:
  `feat(pricing-core): measure an expression's node count and depth (FR-145, WK-690 S1)`.

### Task 3: The four profiles, `where()`, the new functions and the strict refusals

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/expressions.py`
- Modify: `packages/pricing-core/src/pricing_core/data/prepare.py:167` and `:170`
- Modify: `packages/pricing-core/src/pricing_core/data/validate.py:1899`
- Create: `packages/pricing-core/tests/test_expression_profiles.py`
- Create: `packages/pricing-core/tests/test_expression_hostile_inputs.py` (NFR-483 in every
  profile; *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F2.)*)
- Modify: `docs/specs/02-modelling.md` §4.6 (`RL-1265` DP-5's `filter_rows` note)

**Interfaces:**
- Consumes: `ExpressionSize` and `_measure` (Task 2; not yet used here).
- Produces:
  - `GrammarProfile(StrEnum)`, with members `OBJECTIVE = "objective"`, `FACTOR =
    "factor"`, `RECIPE = "recipe"` and `CHECK = "check"`.
  - `parse_expression(expression: str, profile: GrammarProfile, *, symbols: frozenset[str]
    | None = None) -> ast.Expression`. It is the one validation entry point. `symbols` is
    required for `OBJECTIVE` and `FACTOR`, and optional for the others.
  - `compile_expression(expression: str, *, profile: GrammarProfile =
    GrammarProfile.RECIPE, symbols: frozenset[str] | None = None) -> pl.Expr`. It raises
    `ValueError` for `OBJECTIVE`.
  - `referenced_columns(expression: str, *, profile: GrammarProfile = GrammarProfile.RECIPE)
    -> frozenset[str]`.
  - The default `RECIPE` keeps today's two-argument call form valid. That is what lets
    Acceptance 6's unmodified tests pass.

- [ ] **Step 1: Write the failing tests.** Create
  `packages/pricing-core/tests/test_expression_profiles.py`:

```python
"""02 §4.6's four profiles (RL-1184 E2; FR-144's 2026-09-28 amendment; FR-145; FR-36).

Each strict refusal has a positive control: the same string accepted by `recipe`. That
proves the refusal comes from the profile, and not from CPython's parser or a missing
translation.
"""

from __future__ import annotations

from uuid import uuid4

import polars as pl
import pytest

from model_schema import Severity, ValidationLayer, ValidationRule
from pricing_core.data import expressions as expr_module
from pricing_core.data.expressions import (
    ExpressionError,
    GrammarProfile,
    compile_expression,
    parse_expression,
)
from pricing_core.data.prepare import apply_recipe
from pricing_core.data.validate import CHECKS, ValidationContext

OBJECTIVE_SYMBOLS = frozenset({"y", "f", "w"})
FACTOR_SYMBOLS = frozenset({"y", "f", "w"})  # stands in for declared columns
FRAME = pl.DataFrame({"y": [0.5, 2.0, 5.0], "f": [0.0, 1.0, -1.0], "w": [1.0, 1.0, 2.0]})
STRICT = [
    (GrammarProfile.OBJECTIVE, OBJECTIVE_SYMBOLS),
    (GrammarProfile.FACTOR, FACTOR_SYMBOLS),
]


def _values(expression: str, profile: GrammarProfile = GrammarProfile.RECIPE) -> list[object]:
    return FRAME.select(compile_expression(expression, profile=profile)).to_series().to_list()


# -- where() and the four new functions, in recipe and check (they only add) ---------------


@pytest.mark.req("FR-36")
@pytest.mark.parametrize("profile", [GrammarProfile.RECIPE, GrammarProfile.CHECK])
def test_where_and_the_new_functions_compute(profile: GrammarProfile) -> None:
    assert _values("where(y > 1, 1, 0)", profile) == [0, 1, 1]
    assert _values("clip(y, 1, 3)", profile) == [1.0, 2.0, 3.0]
    assert _values("log1p(f)", profile)[0] == pytest.approx(0.0)
    assert _values("expm1(f)", profile)[0] == pytest.approx(0.0)


# -- the strict profiles' refusals, each with its recipe control ---------------------------


@pytest.mark.req("FR-144")
@pytest.mark.req("FR-145")
@pytest.mark.parametrize(("profile", "symbols"), STRICT)
@pytest.mark.parametrize(
    ("expression", "names"),
    [
        ("y > f", "comparison"),
        ("y % 2", "Mod"),
        ("y if f > 0 else w", "IfExp"),
        ("y > 0 and f > 0", "BoolOp"),
        ("not y", "Not"),
        ("+y", "UAdd"),
        ("floor(y)", "not an allowed function"),
        ("y + 'a'", "numeric"),
        ("where(y, f, w)", "one comparison"),
        ("where(y > 0 and f > 0, 1, 2)", "BoolOp"),
        ("where(y > f, 1)", "exactly 3"),
        ("y + z", "'z'"),
    ],
)
def test_a_strict_profile_refuses(
    profile: GrammarProfile, symbols: frozenset[str], expression: str, names: str
) -> None:
    with pytest.raises(ExpressionError, match=names) as excinfo:
        parse_expression(expression, profile, symbols=symbols)
    assert excinfo.value.lineno == 1  # NFR-483: every refusal carries a position


@pytest.mark.req("FR-36")
@pytest.mark.parametrize(
    "expression",
    ["y > f", "y % 2", "y if f > 0 else w", "y > 0 and f > 0", "not y", "+y", "floor(y)"],
)
def test_recipe_accepts_what_the_strict_profiles_refuse(expression: str) -> None:
    """The positive control. These are today's grammar, and `recipe` only adds."""
    parse_expression(expression, GrammarProfile.RECIPE)


@pytest.mark.req("NFR-483")
def test_an_unknown_symbol_is_refused_at_its_own_position() -> None:
    with pytest.raises(ExpressionError) as excinfo:
        parse_expression("y + z", GrammarProfile.OBJECTIVE, symbols=OBJECTIVE_SYMBOLS)
    assert (excinfo.value.col_offset, excinfo.value.end_col_offset) == (4, 5)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize(("profile", "symbols"), STRICT)
def test_the_strict_grammar_accepts_the_spec_example(
    profile: GrammarProfile, symbols: frozenset[str]
) -> None:
    loss = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
    parse_expression(loss, profile, symbols=symbols | {"w_under", "w_over"})


def test_a_strict_profile_needs_its_symbols() -> None:
    with pytest.raises(ValueError, match="symbols"):
        parse_expression("y", GrammarProfile.OBJECTIVE)


def test_the_objective_profile_does_not_compile_to_polars() -> None:
    with pytest.raises(ValueError, match="to_sympy"):
        compile_expression("y", profile=GrammarProfile.OBJECTIVE, symbols=OBJECTIVE_SYMBOLS)


# -- exact arity, in every profile (RL-1292, DP-S1-2 (b)) --------------------------

LEGACY = ["abs", "round", "floor", "ceil", "log", "exp", "sqrt"]
STRICT_LEGACY = ["abs", "log", "exp", "sqrt"]  # the four the strict profiles admit
LENIENT = [GrammarProfile.RECIPE, GrammarProfile.CHECK]
EVERY = [(p, None) for p in LENIENT] + STRICT


def _admitted(profile: GrammarProfile) -> list[str]:
    return LEGACY if profile in LENIENT else STRICT_LEGACY


@pytest.mark.req("FR-36")
@pytest.mark.req("FR-145")
@pytest.mark.parametrize(("profile", "symbols"), EVERY)
def test_a_legacy_function_given_two_arguments_is_refused(
    profile: GrammarProfile, symbols: frozenset[str] | None
) -> None:
    """Red first: at fb90d381 every one of these compiles and silently drops the second
    argument (premise c). RL-1292 makes each an ExpressionError with a position."""
    for name in _admitted(profile):
        with pytest.raises(ExpressionError, match=rf"{name}\(\) takes exactly 1 argument") as e:
            parse_expression(f"{name}(y, f)", profile, symbols=symbols)
        assert (e.value.lineno, e.value.col_offset) == (1, 0)


@pytest.mark.req("FR-36")
@pytest.mark.parametrize("expression", ["abs(y, f)", "round(y, 2)", "log(y, 10)"])
def test_the_ruling_s_named_cases_are_refused_in_recipe(expression: str) -> None:
    """The three expressions RL-1292's proof names. At fb90d381, `round(y, 2)`
    rounds to 0 decimals and `log(y, 10)` is the natural log."""
    with pytest.raises(ExpressionError, match="takes exactly 1 argument"):
        compile_expression(expression)


@pytest.mark.req("FR-36")
@pytest.mark.parametrize(("profile", "symbols"), EVERY)
def test_a_legacy_function_with_one_argument_is_still_accepted(
    profile: GrammarProfile, symbols: frozenset[str] | None
) -> None:
    """The positive control: the refusal is of the extra argument, not of the function.
    `min`, `max` and `coalesce` keep "at least one", so several arguments stay valid."""
    for name in _admitted(profile):
        parse_expression(f"{name}(y)", profile, symbols=symbols)
    parse_expression("min(y, f, w) + max(y, f)", profile, symbols=symbols)
    if profile in LENIENT:
        parse_expression("coalesce(y, f, w)", profile, symbols=symbols)


# -- FD-1294: the refusal reaches all three callers (Acceptance 12) -------


def _round_check(expr: str) -> ValidationRule:
    return ValidationRule(
        id=uuid4(), slug="rounded", version=1, layer=ValidationLayer.ACTUARIAL_SANITY,
        check="expression", severity=Severity.FAIL, target={"table": "t"},
        params={"expr": expr},
    )


@pytest.mark.req("FR-36")
def test_round_with_two_arguments_is_refused_through_the_callers_derive_expression() -> None:
    """Red first: at fb90d381 this step succeeds and rounds to 0 decimals."""
    with pytest.raises(ExpressionError, match=r"round\(\) takes exactly 1 argument") as e:
        apply_recipe(
            {"t": FRAME},
            [{"step": "derive_expression", "params": {"column": "z", "expression": "round(y, 2)"}}],
        )
    assert (e.value.lineno, e.value.col_offset) == (1, 0)


@pytest.mark.req("FR-36")
def test_round_with_two_arguments_is_refused_through_the_callers_filter_rows() -> None:
    """Red first: at fb90d381 this filter succeeds on the silently rounded value."""
    with pytest.raises(ExpressionError, match=r"round\(\) takes exactly 1 argument") as e:
        apply_recipe(
            {"t": FRAME}, [{"step": "filter_rows", "params": {"expression": "round(y, 2) > 1"}}]
        )
    assert (e.value.lineno, e.value.col_offset) == (1, 0)


@pytest.mark.req("FR-50")
def test_round_with_two_arguments_is_refused_through_the_callers_expression_check() -> None:
    """Red first: at fb90d381 the check runs and reports on the silently rounded value."""
    with pytest.raises(ExpressionError, match=r"round\(\) takes exactly 1 argument") as e:
        CHECKS["expression"](
            _round_check("round(y, 2) > 1"),
            {"t": FRAME},
            ValidationContext(reference_tables={}, reference_frames={}),
        )
    assert (e.value.lineno, e.value.col_offset) == (1, 0)


# -- the call sites pass their profiles (Acceptance 7) --------------------------------------


def _spy(monkeypatch: pytest.MonkeyPatch, target: object) -> list[GrammarProfile]:
    seen: list[GrammarProfile] = []
    real = expr_module.compile_expression

    def spy(expression: str, **kwargs: object) -> pl.Expr:
        seen.append(kwargs["profile"])  # type: ignore[arg-type]
        return real(expression, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(target, "compile_expression", spy)
    return seen


@pytest.mark.req("FR-36")
def test_call_site_derive_expression_and_filter_rows_pass_recipe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pricing_core.data.prepare as prepare

    seen = _spy(monkeypatch, prepare)
    apply_recipe(
        {"t": FRAME},
        [
            {"step": "derive_expression", "params": {"column": "z", "expression": "y * 2"}},
            {"step": "filter_rows", "params": {"expression": "y > 1"}},
        ],
    )
    assert seen == [GrammarProfile.RECIPE, GrammarProfile.RECIPE]


@pytest.mark.req("FR-50")
def test_call_site_expression_check_passes_check(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = _spy(monkeypatch, expr_module)  # validate imports it lazily, at call time
    rule = ValidationRule(
        id=uuid4(), slug="y-positive", version=1, layer=ValidationLayer.ACTUARIAL_SANITY,
        check="expression", severity=Severity.FAIL, target={"table": "t"},
        params={"expr": "where(y > 1, 1, 0) == 1"},
    )
    outcome = CHECKS["expression"](rule, {"t": FRAME}, ValidationContext(
        reference_tables={}, reference_frames={}))
    assert seen == [GrammarProfile.CHECK]
    assert outcome.violating_rows == 1  # y = 0.5 is the one row the predicate rejects
```

- [ ] **Step 1b: NFR-483's hostile set, in every profile.** *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F2.)*
  `PL-1268` Slice 1 and this plan's Scope both claim NFR-483 "in every profile".
  `test_expression_nfrs.py` runs its hostile strings through `recipe` only, and Acceptance
  6 keeps that file unmodified, so the claim needs its own file. Create
  `packages/pricing-core/tests/test_expression_hostile_inputs.py`:

```python
"""NFR-483 in every profile of 02 §4.6: each route to eval is refused by this parser.

The strings are `test_expression_nfrs.py`'s hostile set and `test_prepare.py`'s, joined.
That file runs them through `recipe` only, and it stays unmodified (only-add). Each is
valid Python, so an `ExpressionError` with a position proves that this grammar refused
it, and not CPython's parser.
"""

from __future__ import annotations

import pytest

from pricing_core.data.expressions import ExpressionError, GrammarProfile, parse_expression

HOSTILE = [
    "eval('1')",
    "exec('x = 1')",
    "__import__('os').system('ls')",
    "compile('1', '<s>', 'eval')",
    "globals()",
    "open('/etc/passwd').read()",
    "premium.__class__",
    "premium.__class__.__mro__",
    "(lambda: 1)()",
    "(lambda: eval('1'))()",
    "[x for x in premium]",
    "[eval(x) for x in premium]",
    "premium[0]",
    "f'{premium}'",
]


@pytest.mark.req("NFR-483")
@pytest.mark.parametrize("profile", list(GrammarProfile))
@pytest.mark.parametrize("expression", HOSTILE)
def test_every_profile_refuses_every_route_to_eval(
    profile: GrammarProfile, expression: str
) -> None:
    with pytest.raises(ExpressionError) as excinfo:
        parse_expression(expression, profile, symbols=frozenset({"premium", "x"}))
    assert excinfo.value.lineno == 1  # refused with a position, by this grammar


@pytest.mark.req("NFR-483")
@pytest.mark.parametrize("profile", list(GrammarProfile))
def test_the_same_parser_accepts_a_legitimate_expression(profile: GrammarProfile) -> None:
    """The positive control: every profile's refusals above are refusals of the input,
    not of everything."""
    parse_expression("abs(premium - x) / 2", profile, symbols=frozenset({"premium", "x"}))
```

  Its red is an `ImportError` naming `GrammarProfile`, until Step 3 exists. Then the
  refusal cases pass and the control passes, in all four profiles. Before Step 3, compare
  `HOSTILE` with the parametrize lists at `test_expression_nfrs.py:82-89` and
  `test_prepare.py:78-85`, and confirm it is their union with no string dropped.
  Task 5 adds the same set through `to_sympy`.

  **Before running it, check each literal against the shipped source** ([`README.md`](README.md)
  convention 1). `apply_recipe(tables, recipe)` is `prepare.py:89`, and its step shape is
  `test_prepare.py:300-310`'s. `ValidationRule`'s fields mirror `test_sql_check.py:39-48`. The `FACTOR_SYMBOLS` stand-in is enough, because
  Slice 4 binds the real columns.
- [ ] **Step 2: Run and see it fail.** The expected red is an `ImportError` naming
  `GrammarProfile`. **The three `through_the_callers` tests are red at `fb90d381` for the
  finding's own cause**, and the ledger quotes each. Run them against main with only the
  `from pricing_core.data.expressions import (...)` names that exist there. Each fails with
  `DID NOT RAISE`, because the call silently succeeds (FD-1294). *(Revised 2026-09-30 on the maintainer's ruling "DATA CHECK 0 ACCEPTED" (to-lead.md), relayed by the lead: DP-S1-2's defect is FD-1294, #959, severity HIGH, live on main; this slice is its fix.)*
  Then, once Step 3's first sub-step makes the names exist, re-run: the refusal
  cases must now fail as `DID NOT RAISE` (the checks are not written yet). Quote both runs in
  the ledger (Acceptance 5).
- [ ] **Step 3: Implement.** In `expressions.py`:
  - Replace `_ALLOWED_NODES` and `_FUNCTIONS` with the per-profile tables:

```python
class GrammarProfile(StrEnum):
    """02 §4.6's profile table. The context names which grammar an expression is parsed in."""

    OBJECTIVE = "objective"
    FACTOR = "factor"
    RECIPE = "recipe"
    CHECK = "check"


_STRICT: Final = frozenset({GrammarProfile.OBJECTIVE, GrammarProfile.FACTOR})
_COMPARISONS: Final = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)

#: `objective` and `factor`: §4.6's EBNF. Arithmetic, unary minus, calls, and comparisons
#: (which `_check_structure` then confines to where()'s condition).
_STRICT_NODES: Final[tuple[type[ast.AST], ...]] = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare, ast.Name, ast.Load, ast.Constant,
    ast.Call, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, *_COMPARISONS,
)
#: `recipe` and `check`: exactly the node set accepted at fb90d381 (only-add).
_LENIENT_NODES: Final[tuple[type[ast.AST], ...]] = (
    *_STRICT_NODES, ast.BoolOp, ast.IfExp, ast.Mod, ast.UAdd, ast.Not, ast.And, ast.Or,
)
#: The ten in §4.6's `func`. `ceil coalesce floor round` are not differentiable, so they
#: are recipe and check only (the profile note).
_STRICT_FUNCTIONS: Final = frozenset(
    {"log", "exp", "sqrt", "abs", "min", "max", "clip", "where", "log1p", "expm1"}
)
_FUNCTIONS: Final[Mapping[GrammarProfile, frozenset[str]]] = {
    GrammarProfile.OBJECTIVE: _STRICT_FUNCTIONS,
    GrammarProfile.FACTOR: _STRICT_FUNCTIONS,
    GrammarProfile.RECIPE: _STRICT_FUNCTIONS | {"ceil", "coalesce", "floor", "round"},
    GrammarProfile.CHECK: _STRICT_FUNCTIONS | {"ceil", "coalesce", "floor", "round"},
}
#: Exact arity, in every profile (RL-1292, DP-S1-2 (b)). The seven legacy
#: single-argument functions no longer drop extra arguments silently. `min`, `max` and
#: `coalesce` are absent: they keep "at least one", which `_call`'s empty-args refusal holds.
_ARITY: Final = {
    "where": 3, "clip": 3, "log1p": 1, "expm1": 1,
    "abs": 1, "round": 1, "floor": 1, "ceil": 1, "log": 1, "exp": 1, "sqrt": 1,
}
```

  - `_check(tree, profile)` keeps its breadth-first walk and its messages. It takes the node
    set and the function set from the profile, and names the profile in the message:
    `f"{type(child).__name__} is not permitted in the {profile} profile (02 §4.6)"`. The
    phrases `"is not an allowed function"`, `"only plain function calls are permitted"` and
    `"keyword arguments are not permitted"` stay verbatim, because the unmodified tests
    match on them. Add the arity check against `_ARITY`, in every profile, positioned at
    the call: `f"{name}() takes exactly {n} argument(s), got {len(child.args)}"`. The
    message names the function and the count, as RL-1292 requires. The check
    runs after the function-set check, so in `objective` a `round(x, 2)` is refused as "not
    an allowed function" first. *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*
  - Add `_check_structure(node: ast.expr, profile, *, where_condition: bool = False)`. It
    recurses over `ast.expr` children, and it raises in these cases:
    - a `Compare` with more than one operator: `"chained comparisons are not permitted; use
      \`and\`"`, in every profile (premise d moves earlier, with the same outcome);
    - a `Compare` in a strict profile that is not `where()`'s first argument: `"a
      comparison is permitted only as the condition of where(cond, a, b) in the {profile}
      profile"`;
    - a `where` call whose first argument is not a single `Compare`: `"where(cond, a, b)
      needs cond to be one comparison between two sub-expressions"`, positioned at the
      condition. This applies in every profile (`PL-1268` Slice 1);
    - a `Constant` in a strict profile whose value is a `bool` or is not an `int` or
      `float`: `"only numeric literals are permitted in the {profile} profile"`.
    It recurses into a `Compare`'s two sides with `where_condition=False`, so a comparison
    nested inside a condition is refused.
  - Add `_check_symbols(tree, symbols)`. Every `Name` that is not a `Call.func` must be in
    `symbols`, else `f"{name!r} is not a bound symbol or declared parameter"`, positioned at
    the name.
  - Add `parse_expression`: `ast.parse` (a `SyntaxError` propagates, as today), then
    `_check`, then `_check_structure(tree.body, profile)`, then `_check_symbols` when
    `symbols` is given. A strict profile with `symbols=None` raises
    `ValueError("the objective and factor profiles need their bound symbols")`.
  - `compile_expression` and `referenced_columns` call `parse_expression`.
    `compile_expression` raises `ValueError("the objective profile translates to SymPy: use
    pricing_core.data.expression_sympy.to_sympy")` for `OBJECTIVE`. `referenced_columns`
    excludes the names in `_FUNCTIONS[profile]`, as today.
  - In `_call`, add these cases:
    - `"where"`: `pl.when(args[0]).then(args[1]).otherwise(args[2])`;
    - `"clip"`: `args[0].clip(args[1], args[2])`;
    - `"log1p"`: `args[0].log1p()`;
    - `"expm1"`: `args[0].exp() - 1`. Polars has no `expm1` (premise f), and the precision
      loss near 0 is a `recipe` and `check` matter only. `objective` compiles through SymPy.
  - Imports: `from collections.abc import Iterator, Mapping` and `from enum import
    StrEnum` (`model_schema/rating.py:31` is the repository's `StrEnum` precedent).
  - Rewrite the module docstring's first line to name all four profiles, and update
    `__all__`.
  - `prepare.py:167` and `:170`: pass `profile=GrammarProfile.RECIPE`. `validate.py:1899`:
    pass `profile=GrammarProfile.CHECK`, importing `GrammarProfile` beside
    `compile_expression` at `:1892`.
- [ ] **Step 4: The spec note** (`spec-change`; this commit, because the code is here). In
  `02` §4.6, after the profile note that ends "rather than raising the limit.", add:

  > *(Amended 2026-09-30, `RL-1265` DP-5: `filter_rows` (`01` FR-35) parses in the `recipe`
  > profile. It is a data-preparation step, and it already used `recipe`'s operator set.)*

  Directly after it, add the arity statement that RL-1292 requires. *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*

  > *(Amended 2026-09-30, RL-1292 (DP-S1-2): the arity of every function, in every
  > profile. `abs`, `round`, `floor`, `ceil`, `log`, `exp`, `sqrt`, `log1p` and `expm1` take
  > exactly one argument. `clip` and `where` take exactly three. `min`, `max` and `coalesce`
  > take one or more. Any other count is refused with a position-accurate error naming the
  > function and the count. An extra argument was silently dropped before this date, so
  > `round(x, 2)` rounded to 0 decimals and `log(x, 10)` was the natural log. Both are now
  > refused. Honouring a second argument is not specified.)*

- [ ] **Step 5: Green.** Run `uv run pytest packages/pricing-core/tests -q`: everything
  passes, including the two unmodified files of Acceptance 6. Run `uv run mypy` and
  `uv run ruff check .`. Quote each rc.
- [ ] **Step 6: Commit:** `feat(pricing-core): the expression grammar's four profiles,
  where(), and the strict refusals (FR-144, FR-145, FR-36, WK-690 S1)`.

### Task 4: The limits, enforced in all four profiles

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/expressions.py`
- Modify: `packages/pricing-core/tests/test_expression_limits.py` (append)
- Modify: `docs/specs/02-modelling.md` §4.6 (the delivery note on the 2026-08-22 divergences)

**Interfaces:**
- Consumes: `_measure` (Task 2), and `parse_expression` and `GrammarProfile` (Task 3).
- Produces: `ExpressionLimits` (frozen dataclass: `max_nodes: int = 200`,
  `max_depth: int = 20`) and `DEFAULT_LIMITS`. `parse_expression`, `compile_expression`
  and `referenced_columns` each gain `limits: ExpressionLimits = DEFAULT_LIMITS`.

**Precondition:** the Task 2 commit is an ancestor of this branch's HEAD, and Task 2 Step
6 did not stop the slice (Acceptance 4).

- [ ] **Step 1: Write the failing tests.** Add `ExpressionError`, `ExpressionLimits`,
  `GrammarProfile` and `parse_expression` to the file's existing top-of-file import from
  `pricing_core.data.expressions`, then append:

```python
SYMBOLS = frozenset({"x"})
ALL_PROFILES = list(GrammarProfile)


def _parse(expression: str, profile: GrammarProfile, **kwargs: object) -> None:
    parse_expression(expression, profile, symbols=SYMBOLS, **kwargs)  # type: ignore[arg-type]


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", ALL_PROFILES)
def test_200_nodes_and_depth_20_are_accepted(profile: GrammarProfile) -> None:
    _parse(_min_of(198), profile)       # 200 nodes (premise h)
    _parse(_nested_abs(19), profile)    # depth 20


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", ALL_PROFILES)
def test_201_nodes_are_refused(profile: GrammarProfile) -> None:
    with pytest.raises(ExpressionError, match="201 nodes; the limit is 200"):
        _parse(_min_of(199), profile)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", ALL_PROFILES)
def test_depth_21_is_refused_at_the_deepest_node(profile: GrammarProfile) -> None:
    with pytest.raises(ExpressionError, match="depth 21; the limit is 20") as excinfo:
        _parse(_nested_abs(20), profile)
    assert excinfo.value.col_offset is not None  # NFR-483: positioned, not whole-string


@pytest.mark.req("FR-145")
def test_the_limits_are_configurable() -> None:
    small = ExpressionLimits(max_nodes=3, max_depth=2)
    _parse("x + x", GrammarProfile.RECIPE, limits=small)  # 3 nodes, depth 2
    with pytest.raises(ExpressionError, match="5 nodes; the limit is 3"):
        _parse("x + x + x", GrammarProfile.RECIPE, limits=small)
```

  RL-1291 ruled (a), so these fixtures stand. *(Revised 2026-09-30 on the decision-maker's ruling RL-1291, #956.)* ~~Under DP-S1-1 (b), the
  figures that change are premise h's third column.~~ The fixtures
  would then be `_min_of(98)` and `_min_of(99)` (about 200 `ast.walk` nodes), and a depth
  fixture recomputed with `measure_expression(...).all_nodes`. Update both in this step if
  the ruling says (b).
- [ ] **Step 2: Run and see it fail.** The expected red is an `ImportError` naming
  `ExpressionLimits`. Once the dataclass exists, the refusal cases fail with `DID NOT RAISE`,
  and the accept cases pass: the positive control, which shows the limits refuse exactly at
  the boundary. Quote both runs.
- [ ] **Step 3: Implement.** Add `ExpressionLimits` and `DEFAULT_LIMITS: Final =
  ExpressionLimits()`. At the end of `parse_expression`, call `size, deepest =
  _measure(tree.body)`, then:
  - if `size.nodes > limits.max_nodes`, raise `ExpressionError(f"the expression has
    {size.nodes} nodes; the limit is {limits.max_nodes} (02 §4.6, FR-145)",
    node=tree.body)`;
  - if `size.depth > limits.max_depth`, raise `ExpressionError(f"the expression reaches depth
    {size.depth}; the limit is {limits.max_depth} (02 §4.6, FR-145)", node=deepest)`.
  Thread `limits` through `compile_expression` and `referenced_columns`.
- [ ] **Step 4: The spec note** (`spec-change`; this commit). In `02` §4.6, after the
  paragraph that begins "**Decided 2026-09-28 by delegation (OQ-1185, `RL-1184` E2)", add:

  > *(Delivered 2026-09-30, WK-690 Slice 1: the parser implements the profile table. The
  > three 2026-08-22 divergences are closed. Both limits are enforced in all four profiles,
  > counted over `ast.expr` nodes (DP-S1-1, RL-1291). The
  > function sets are the table's. Comparisons in `objective` and `factor` exist only as
  > `where()`'s condition.)*

  RL-1291 ruled (a), so the note says `ast.expr` nodes. *(Revised 2026-09-30 on the decision-maker's ruling RL-1291, #956.)*
- [ ] **Step 5: Green.** Run `uv run pytest packages/pricing-core/tests -q`, with Acceptance
  6's two files unmodified, and run `uv run mypy`. Quote each.
- [ ] **Step 6: Commit:** `feat(pricing-core): enforce the expression node and depth limits
  in every profile (FR-145, WK-690 S1)`.

### Task 5: The objective profile, translated to SymPy

**Files:**
- Create: `packages/pricing-core/src/pricing_core/data/expression_sympy.py`
- Create: `packages/pricing-core/tests/test_expression_sympy.py`
- Modify: `docs/specs/02-modelling.md` §4.6 (the `real=True` statement; RL-1293)

**Interfaces:**
- Consumes: `parse_expression`, `GrammarProfile`, `ExpressionLimits`, `DEFAULT_LIMITS` and
  `ExpressionError` (Tasks 3 and 4).
- Produces: `OBJECTIVE_SYMBOLS: frozenset[str]` (`{"y", "f", "w"}`), and
  `to_sympy(expression: str, *, parameters: Collection[str] = (), limits: ExpressionLimits =
  DEFAULT_LIMITS) -> sympy.Expr`. Slice 2 differentiates what this returns.

- [ ] **Step 1: A two-minute `library-spike` check** of premise g on the locked version:
  `uv run python -c "import sympy; from sympy.codegen.cfunctions import log1p, expm1;
  print(sympy.__version__, sympy.diff(log1p(sympy.Symbol('x', real=True)),
  sympy.Symbol('x', real=True)))"`. It prints `1.14.0 1/(x + 1)`. Record it in the ledger.
- [ ] **Step 2: Write the failing tests.** Create
  `packages/pricing-core/tests/test_expression_sympy.py`:

```python
"""The `objective` profile to SymPy (FR-144's 2026-09-28 amendment; NFR-483)."""

from __future__ import annotations

import builtins
import sys

import pytest
import sympy
from sympy.codegen.cfunctions import expm1, log1p

from pricing_core.data.expression_sympy import to_sympy
from pricing_core.data.expressions import ExpressionError

y, f, w, w_under, w_over, lo, hi = (
    sympy.Symbol(n, real=True) for n in ("y", "f", "w", "w_under", "w_over", "lo", "hi")
)


@pytest.mark.req("FR-144")
def test_the_spec_example_translates_with_where_as_piecewise() -> None:
    loss = to_sympy(
        "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
        parameters=("w_under", "w_over"),
    )
    expected = w * sympy.Piecewise((w_under, sympy.exp(f) < y), (w_over, True)) * (
        y - sympy.exp(f)
    ) ** 2
    assert loss == expected
    assert loss.has(sympy.Piecewise)


@pytest.mark.req("FR-144")
@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("log(y) + exp(f) - sqrt(w)", sympy.log(y) + sympy.exp(f) - sympy.sqrt(w)),
        ("abs(f) / 2", sympy.Abs(f) / 2),
        ("min(y, f) + max(y, f, w)", sympy.Min(y, f) + sympy.Max(y, f, w)),
        ("clip(f, lo, hi)", sympy.Min(sympy.Max(f, lo), hi)),
        ("log1p(f) - expm1(f)", log1p(f) - expm1(f)),
        ("-y ** 2", -(y**2)),
    ],
)
def test_each_function_maps_to_its_sympy_form(source: str, expected: sympy.Expr) -> None:
    assert to_sympy(source, parameters=("lo", "hi")) == expected


@pytest.mark.req("FR-144")
def test_the_strict_refusals_hold_on_the_sympy_path() -> None:
    with pytest.raises(ExpressionError, match="comparison"):
        to_sympy("y > f")


@pytest.mark.req("FR-144")
def test_every_objective_symbol_is_real() -> None:
    """RL-1293 (DP-S1-3 (a)): y, f, w and every parameter are real."""
    loss = to_sympy("w_under * abs(y - f) + w", parameters=("w_under",))
    assert loss.free_symbols and all(s.is_real is True for s in loss.free_symbols)


@pytest.mark.req("FR-144")
def test_the_abs_derivative_is_the_real_one() -> None:
    """RL-1293: with real symbols, d|f|/df has no re, im or unevaluated Derivative.
    Red first: build the symbols without `real=True` and this fails (premise g's complex
    form). The ledger quotes that red."""
    derivative = sympy.diff(to_sympy("w * abs(y - f)"), f)
    assert not derivative.has(sympy.re, sympy.im, sympy.Derivative)


@pytest.mark.req("FR-144")
def test_the_spec_example_gradient_and_hessian_are_reproduced() -> None:
    """RL-1293's third violation. §4.6's printed gradient and hessian are
    algebraically what SymPy derives from this translation. It is compared as expressions,
    not text: Slice 2 owns the canonical text. Spiked on sympy 1.14.0: both differences
    simplify to 0 after `piecewise_fold`."""
    loss = to_sympy(
        "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
        parameters=("w_under", "w_over"),
    )
    e = sympy.exp(f)
    gradient = sympy.Piecewise(
        (2 * w * w_under * (e - y) * e, y > e), (2 * w * w_over * (e - y) * e, True)
    )
    hessian = sympy.Piecewise(
        (2 * w * w_under * (2 * e - y) * e, y > e), (2 * w * w_over * (2 * e - y) * e, True)
    )
    assert sympy.simplify(sympy.piecewise_fold(sympy.diff(loss, f) - gradient)) == 0
    assert sympy.simplify(sympy.piecewise_fold(sympy.diff(loss, f, 2) - hessian)) == 0


def test_a_parameter_cannot_shadow_a_bound_symbol() -> None:
    with pytest.raises(ValueError, match="y, f or w"):
        to_sympy("y", parameters=("y",))


@pytest.mark.req("NFR-483")
def test_the_translation_never_reaches_eval_or_a_string_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The tree is built node by node. With every string-to-code route replaced by a raiser,
    the spec example still translates.

    **The warm-up is required, and the test must pass in isolation** (F7). Python's import
    machinery calls the builtin `exec`, and SymPy imports modules lazily on first use: in a
    fresh process the spec example imports modules such as `sympy.sets.setexpr` on its first
    call. Patching `exec` before that call makes the import itself trip the raiser, and the
    test would then pass only when an earlier test had warmed the imports. So the same
    translation runs once unpatched, and the patched run must import nothing new and give
    the same result. Checked with `uv run pytest <this file> -k never_reaches` in a fresh
    process (Step 5).
    """
    source = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
    warm = to_sympy(source, parameters=("w_under", "w_over"))  # imports SymPy's lazy modules

    def refuse(*args: object, **kwargs: object) -> object:
        raise AssertionError("user text reached eval/exec/parse_expr (NFR-483)")

    import sympy.parsing.sympy_parser as sympy_parser

    loaded = set(sys.modules)
    monkeypatch.setattr(builtins, "eval", refuse)
    monkeypatch.setattr(builtins, "exec", refuse)
    monkeypatch.setattr(sympy_parser, "parse_expr", refuse)
    assert to_sympy(source, parameters=("w_under", "w_over")) == warm
    assert set(sys.modules) == loaded  # nothing imported under the patch
    # The positive control (F3; CLAUDE.md §13): the raisers are live. A string route
    # through SymPy's own parser trips them. So the translation above passing means it
    # took no such route, not that the patch missed.
    with pytest.raises(AssertionError, match="NFR-483"):
        sympy.sympify("y + 1")
    with pytest.raises(AssertionError, match="NFR-483"):
        sympy_parser.parse_expr("y + 1")


@pytest.mark.req("NFR-483")
@pytest.mark.parametrize(
    "expression",
    ["eval('1')", "__import__('os').system('ls')", "y.__class__", "(lambda: 1)()", "y[0]"],
)
def test_the_sympy_path_refuses_every_route_to_eval(expression: str) -> None:
    """NFR-483 on the objective path itself (F2): `to_sympy` goes through the one parser."""
    with pytest.raises(ExpressionError) as excinfo:
        to_sympy(expression)
    assert excinfo.value.lineno == 1
```

  *(Revised 2026-09-30 on auditor-plans2's audit of #954 at 3e4402cd, finding F3.)* The spike behind the control, run with sympy 1.14.0: with
  `sympy_parser.parse_expr` replaced by a raiser, `sympy.sympify("y + 1")` raised it; with
  `builtins.eval` replaced, it raised again. Either patch alone trips the control.
  *(Revised 2026-09-30 on auditor-plans2's delta audit at 1296d9dc, finding F7.)* The test
  keeps the `exec` patch and warms first. The spike ran sympy 1.14.0 in two fresh processes,
  building §4.6's example as `to_sympy` would: `real` symbols, `exp`, `Lt`, `Piecewise`,
  `Integer`. Without a warm-up, the patched build raised the NFR-483 raiser from inside
  SymPy's own imports. With one unpatched build first, the patched build succeeded,
  imported 0 new modules, and both controls (`sympify` and `parse_expr`) still tripped.
  `test_the_sympy_path_refuses_every_route_to_eval` patches nothing, so it needs no
  warm-up.

- [ ] **Step 3: Run and see it fail.** The expected red is an `ImportError` naming
  `pricing_core.data.expression_sympy`. Quote it.
- [ ] **Step 4: Implement** `expression_sympy.py`:

```python
"""02 §4.6's `objective` profile, translated to a SymPy expression (FR-144).

Translation, not evaluation: the tree is `parse_expression`'s validated `ast`, and each node
becomes the SymPy object it names. No string reaches `sympify`, `parse_expr`, `lambdify` or
`eval` (NFR-483; 02 §8). The symbols are real (DP-S1-3, RL-1293), so `Abs` differentiates to
`sign`, and the canonical text Slice 2 records is the real-variable one.

A separate module so that the Polars path (`recipe`, `check`) never imports sympy.
"""

from __future__ import annotations

import ast
from collections.abc import Collection, Mapping
from typing import Final

import sympy
from sympy.codegen.cfunctions import expm1, log1p

from pricing_core.data.expressions import (
    DEFAULT_LIMITS,
    ExpressionError,
    ExpressionLimits,
    GrammarProfile,
    parse_expression,
)

__all__ = ["OBJECTIVE_SYMBOLS", "to_sympy"]

#: 02 §4.6: an objective's bound symbols are the label, the raw score and the weight.
OBJECTIVE_SYMBOLS: Final = frozenset({"y", "f", "w"})

_BINARY: Final = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a**b,
}
_RELATIONS: Final = {
    ast.Eq: sympy.Eq, ast.NotEq: sympy.Ne, ast.Lt: sympy.Lt,
    ast.LtE: sympy.Le, ast.Gt: sympy.Gt, ast.GtE: sympy.Ge,
}


def to_sympy(
    expression: str,
    *,
    parameters: Collection[str] = (),
    limits: ExpressionLimits = DEFAULT_LIMITS,
) -> sympy.Expr:
    """Parse `expression` in the `objective` profile and build its SymPy expression."""
    shadowed = OBJECTIVE_SYMBOLS & set(parameters)
    if shadowed:
        raise ValueError(f"a parameter may not be named y, f or w: {sorted(shadowed)}")
    names = OBJECTIVE_SYMBOLS | frozenset(parameters)
    tree = parse_expression(
        expression, GrammarProfile.OBJECTIVE, symbols=names, limits=limits
    )
    table = {name: sympy.Symbol(name, real=True) for name in names}
    return _build(tree.body, table)


def _build(node: ast.expr, table: Mapping[str, sympy.Symbol]) -> sympy.Expr:
    match node:
        case ast.Constant(value=bool()):
            pass  # refused by the parser; unreachable, and falls through to the raise
        case ast.Constant(value=int() as value):
            return sympy.Integer(value)
        case ast.Constant(value=float() as value):
            return sympy.Float(value)  # sympy.sympify's own mapping of a Python float
        case ast.Name(id=name):
            return table[name]
        case ast.UnaryOp(op=ast.USub(), operand=operand):
            return -_build(operand, table)
        case ast.BinOp(left=left, op=op, right=right) if type(op) in _BINARY:
            return _BINARY[type(op)](_build(left, table), _build(right, table))
        case ast.Call(func=ast.Name(id=name), args=args):
            return _call(name, args, table, node)
    raise ExpressionError(f"{type(node).__name__} is not translatable", node=node)


def _call(
    name: str, args: list[ast.expr], table: Mapping[str, sympy.Symbol], node: ast.expr
) -> sympy.Expr:
    if name == "where":
        condition, then, otherwise = args
        assert isinstance(condition, ast.Compare)  # the parser guarantees one comparison
        relation = _RELATIONS[type(condition.ops[0])](
            _build(condition.left, table), _build(condition.comparators[0], table)
        )
        return sympy.Piecewise(
            (_build(then, table), relation), (_build(otherwise, table), True)
        )
    built = [_build(a, table) for a in args]
    match name:
        case "log":
            return sympy.log(built[0])
        case "exp":
            return sympy.exp(built[0])
        case "sqrt":
            return sympy.sqrt(built[0])
        case "abs":
            return sympy.Abs(built[0])
        case "min":
            return sympy.Min(*built)
        case "max":
            return sympy.Max(*built)
        case "clip":
            return sympy.Min(sympy.Max(built[0], built[1]), built[2])
        case "log1p":
            return log1p(built[0])
        case "expm1":
            return expm1(built[0])
    raise ExpressionError(f"{name!r} is not an allowed function", node=node)
```

  If `mypy --strict` rejects the lambdas' implicit `Any`, give `_BINARY` the annotation
  `Mapping[type[ast.operator], Callable[[sympy.Expr, sympy.Expr], sympy.Expr]]`. Do not add
  `type: ignore`.
- [ ] **Step 4b: The §4.6 statement** (`spec-change`; this commit). *(Revised 2026-09-30 on the decision-maker's ruling RL-1293, #958.)* In `02` §4.6,
  after Task 4's delivery note, add:

  > *(Amended 2026-09-30, RL-1293 (DP-S1-3): the `objective` profile's bound
  > symbols and declared parameters are real-valued, and the derivation treats them so.
  > `abs` therefore differentiates to `sign`, and the `derived` text a reviewer approves is
  > the real-variable form.)*

- [ ] **Step 5: Green.** Run `uv run pytest packages/pricing-core/tests/test_expression_sympy.py
  -q`, then the raiser test alone in a fresh process: `uv run pytest
  packages/pricing-core/tests/test_expression_sympy.py -k never_reaches -q`.
  It must pass on its own, not only after other tests have warmed SymPy's imports (F7). Also
  run `uv run mypy` and `uv run lint-imports`. Run Acceptance 9's `git grep`: only
  `expression_sympy.py` imports sympy. Quote each.
- [ ] **Step 6: Commit:** `feat(pricing-core): translate the objective profile to SymPy,
  where() as Piecewise (FR-144, WK-690 S1)`.

### Task 6: `RL-1265` DP-5 — `03` FR-244 and the matching `02` §4.6 note, one commit

**Files:**
- Modify: `docs/specs/03-rating-engine.md:146` (the FR-244 row; §3.5)
- Modify: `docs/specs/02-modelling.md` §4.6

- [ ] **Step 1: Amend FR-244** (`spec-change`). Append to its cell:

  > **Amended 2026-09-30, `RL-1265` DP-5:** the rating grammar is FR-244's own: ZEN's
  > expression language, restricted to the function list above and verified against the
  > engine by FR-276. It shares function names with `02` §4.6 where they coincide, but it
  > is not one of §4.6's profiles, and `pricing_core.data.expressions` never parses it.
  > "The same restricted grammar as `02` §4.6" is superseded by this sentence. Nothing
  > is struck.

- [ ] **Step 2: The matching `02` §4.6 note.** Directly after Task 3's `filter_rows` note,
  add:

  > *(Amended 2026-09-30, `RL-1265` DP-5: rating `expression` steps are not a profile of
  > this parser. They are ZEN expressions under `03` FR-244 and FR-276, and `03` FR-244 now
  > says so.)*

- [ ] **Step 3:** Run `python3 scripts/audit-docs.py` and quote the rc.
- [ ] **Step 4: Commit both files together:** `docs(specs): rating expressions are FR-244's
  own grammar, not a 02 §4.6 profile (RL-1265 DP-5, WK-690 S1)`.

### Task 7: The gate, the ledger and the PR

- [ ] Run the full two-half gate on the committed tree, as in `CLAUDE.md` §11
  (`dev-commands` for the exit-code trap). Quote every rc. Quote the `N passed` line
  against Task 0's figure for main.
- [ ] Run `python3 scripts/doc-index.py`, then `python3 scripts/doc-index.py --check`, and
  `uv run python scripts/req-coverage.py`. Quote the FR-144, FR-145, FR-36, FR-50 and
  NFR-483 lines. FR-144's marker covers its 2026-09-28 amendment clause only. Its
  derivation, storage and fit-time clauses are Slices 2 and 3, and the ledger says so, so
  the marker is not read as whole coverage (`CLAUDE.md` §13).
- [ ] The ledger records:
  - the tree, premises a–i, and every red-then-green quote;
  - Task 2's table;
  - the three `RL-` records that resolved DP-S1-1 to DP-S1-3, and the task at which each was applied;
  - that this slice resolves FD-1294 (#959): the three `through_the_callers`
    quotes, red at `fb90d381` and green at the slice's head. The finding resolves at merge.
    *(Revised 2026-09-30 on the maintainer's ruling "DATA CHECK 0 ACCEPTED" (to-lead.md), relayed by the lead: DP-S1-2's defect is FD-1294, #959, severity HIGH, live on main; this slice is its fix.)*
  - ~~DP-S1-2's silent-argument finding candidate, for the auditor.~~ Discharged by RL-1292, which refuses the silent drop. *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*
- [ ] Open the PR against `main`, noting the lead's file-contention dispatch record
  (Status). Report the head SHA.

## Hand-off

Slice 2 (symbolic derivation, the compilation target and the certificate, `SL-1272`)
starts after this slice closes. It consumes `to_sympy` and DP-S1-3's symbol assumptions. It
records `derivation_version` and `library_versions.sympy` from `sympy.__version__`, and
carries `RL-1289`'s patched-version test (the Acceptance section's second violation).
Slice 4 (`SL-1274`) consumes `GrammarProfile.FACTOR` with real column symbols.

## Self-review

1. **Spec coverage.** Every row of "Requirement coverage" names a task:
   - FR-144's amendment clause: Tasks 3 (refusals), 4 (limits) and 5 (`Piecewise`).
   - FR-145: Tasks 3 and 4.
   - §4.6: Tasks 3, 4 and 6.
   - NFR-483's first two clauses: Tasks 3 (positions), 4 (the depth refusal's position) and
     5 (no `eval` or parser on the SymPy path). Its third clause is Slice 2's (Hand-off).
   - FR-36 and the `check` profile: Task 3, including premise b's first-ever check test.
   - FR-244: Task 6.
   - `RL-1289`'s three violations: Task 1 (the lock), Hand-off (the patched version, Slice
     2) and Acceptance 3 (uncited literals).
2. **Rulings at every site** ([`README.md`](README.md) convention 5).
   - `RL-1289`: narrative (What this plan implements), Files (Task 1), Steps (Task 1, Steps
     3–5) and Acceptance (1–3).
   - `RL-1265` DP-5: narrative, Files (Tasks 3 and 6), Steps (Task 3 Step 4 and Task 6) and
     Scope (FR-244 row).
   - `RL-1184` E2: Global Constraints, Tasks 3 and 4, and Acceptance 5 and 6.
3. **Placeholder scan.** No step says "TBD" or "add tests". One literal is named as a
   stand-in, with its reason: `FACTOR_SYMBOLS` (Slice 4 binds real columns).
   DP-S1-1's alternative constants are named in Task 4 Step 1.
4. **Type consistency.** These names match across Tasks 2–5 and the Hand-off:
   `GrammarProfile`, `parse_expression(expression, profile, *, symbols, limits)`,
   `ExpressionSize(nodes, depth, all_nodes)`, `_measure -> (ExpressionSize, ast.expr)`,
   `ExpressionLimits(max_nodes, max_depth)`, `DEFAULT_LIMITS`, `OBJECTIVE_SYMBOLS` and
   `to_sympy(expression, *, parameters, limits)`.
5. **Only-add.** The lenient node set is exactly `fb90d381`'s `_ALLOWED_NODES`. The two
   existing test files stay unmodified (Acceptance 6). There are two deliberate
   subtractions. The limits are licensed by Task 2's measurement. Exact arity for the
   seven legacy functions is licensed by RL-1292, which records that no
   repository expression relies on the dropped argument. *(Revised 2026-09-30 on the decision-maker's ruling RL-1292, #957.)*
