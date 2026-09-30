---
id: PL-9833
family: plan
kind: leaf
title: WK-1178 slice — FR-244's enforced allow-list and FR-274's guard over every authored rating string: leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-9832, PL-1295, RL-1263, RL-1265]
---

# WK-1178 slice — FR-244's enforced allow-list and FR-274's guard over every authored rating string: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `python-package` (Tasks 2–4), `python-test` (every task: requirement markers, negative tests), `fastapi-service` (Task 5's route test) and `dev-commands` (the gate), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make every **authored** rating string — an `expression` step's `expr`, a constraint's
`condition`, its `clamp_bounds`, and a `table` or `lookup` step's `key_expr` — pass the same
save-time checks. Those checks are:
- FR-244's allow-list, enforced for operators and functions alike;
- FR-276's engine compile;
- FR-274's division guard, with `??` never counted as a guard;
- the determinism and scale-cap checks (DP-G2).

A decline condition or a clamp bound that would silently fail open at scoring is refused at
save. A residual evaluation failure at scoring is reported under its own code, not as
`RATE_TABLE_MISS`.

**Architecture.** One helper in `compile.py` lists every authored string with its step id and
field. The four existing checks (`_check_determinism`, `_check_division_guards`,
`_check_scale_cap`, `_check_vocabulary`) iterate that list instead of `RatingExpressionStep.expr`
alone. `_check_vocabulary` gains the allow-list pass (DP-G3) before the engine compile it
already does. `_GUARD_MARKERS` loses its two dead entries. `score.py`'s
`_reraise_engine_failure` stops inferring a table miss when the failing node is not downstream
of one (DP-G4).

**Tech Stack:** Python 3.12, `pricing-core`, `zen-engine` (the installed binding, read only),
pytest. No new dependency.

**Spec:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.5 **FR-244** (`03:146` at
  the tree above), and §3.11:
  - **FR-274** (`03:223`);
  - **FR-275** (`03:224`);
  - **FR-276** (`03:225`).
- §3.1 **FR-216** (`03:85`), for determinism.
- §3.7 **FR-255** (`03:167`), for typed scoring errors.
- §5.1's error-code paragraph (`03:772-782`) — the new code, DP-G4.

**What this plan implements.** The ruling on FR-244 is #967 (RL working id 9904, "RULED, NOT
MINTED"; read at head `fb4833a90edcd501e1f10ae03bf2205d29933f90`). This plan covers its
*Ruled* items 1 to 3, its *Which slice carries it* ("The code: one WK-1178 slice, after the
~16:00 fix slice") and its *Acceptance* section.

It also discharges the finding in #968 (FD working id 9885, read at head
`46b4d44548a5d7434084e737d6074ed85887f749`), titled "Rating condition and clamp_bounds strings
are never validated — no vocabulary, syntax or division-guard check (FR-244, FR-274, FR-276)".
That finding's *Disposition* names this slice as owner: "Deferred with an owner: the WK-1178
code slice that #967 (RL working id 9904) specifies". Neither record is minted, so each is cited
by PR and working id, and Task 0 re-points both at mint.

The maintainer's ordering is the lead's relay of the entry "DECISION on B" in `to-lead.md`,
the lead's local channel file, outside the repository. It runs: the fix slice (#963,
`SL-9872`/`PL-9873`, working ids) → **this slice** → WK-1250 Slice 1, all serialised on
`compile.py` under `RL-1263`.

## Status

**Draft**, filed 2026-09-30 against the tree above under working id 9833. Its slice row is
**SL-9832** (working id), added under `### WK-1178` in `docs/roadmap.md` in this PR. The ids were
chosen by `git grep -h -o -E '\b98[23][0-9]\b' -- docs .claude`, plus a `docs` filename match,
over every `origin/*` branch and every open PR's head (47 refs). Only 9820 and 9830 were in
use.

**Activation needs, in order:**
1. **The fix slice (#963) merged.** `compile.py` has one writer at a time (`RL-1263`; #967,
   *Which slice carries it*).
2. **FR-244's amended text on `main`, or carried by this slice** (DP-G1).
3. The decision-maker's rulings on DP-G1 to DP-G4.
4. #967 and #968 minted, and this plan's citations re-pointed (Task 0).
5. A free `RL-1263` gate slot, and the lead's dispatch record with its write-set check (below).

### Dependencies

- **On the fix slice (#963):** it edits `compile_bundle` and adds `check_step_refs_pinned`
  (PL-9873, Task 2). This slice edits `_check_determinism`, `_check_division_guards`,
  `_check_scale_cap`, `_check_vocabulary` and `_GUARD_MARKERS`. Those are different
  definitions in the same file, but the maintainer's order serialises them. The later slice
  merges `main` and re-runs its gate. #963 also adds `_INPUT_FREE` entries in
  `test_quote_input_raise_sites.py` (PL-9873, acceptance 7), which this slice may touch too
  (Task 4).
- **On WK-690 Slice 1 (PL-1295, dispatched now):** its Task 6 writes `03` FR-244's cell
  (`PL-1295:1530-1554`, "Modify: `docs/specs/03-rating-engine.md:146` (the FR-244 row; §3.5)").
  #967 releases that task's held sentence in the amended wording (*The amended FR-244 text*).
  Until it lands, `03` FR-244 at `03:146` still says "the same restricted grammar as `02`
  §4.6", and the allow-list this slice enforces is not in the spec. Enforcing it before the
  text lands is code ahead of its spec (`CLAUDE.md` §0). → **DP-G1.**
- **Code:** nothing unmerged beyond the fix slice.

### Write set, for the RL-1263 check

`RL-1263` option (c): "may not both change the same **existing** function, class, method, spec
section, or policy table" (`RL-1263:89`).

| Path | What changes | Existing definition edited |
|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `_GUARD_MARKERS` (`:41`) loses `"?:"` and `"coalesce("`; a new helper `_authored_strings`; `_check_determinism` (`:142-163`), `_check_division_guards` (`:166-193`), `_check_scale_cap` (`:196-230`) and `_check_vocabulary` (`:233-257`) iterate it; the allow-list pass (DP-G3), in a new function beside `_check_vocabulary` or in a new module `pricing_core/rating/vocabulary.py` | **Yes**: those five definitions |
| `packages/pricing-core/src/pricing_core/rating/score.py` | `_reraise_engine_failure` (`:469-498`) chooses the code (DP-G4); **its single `_raise_named` call stays single** | **Yes**: that function |
| `docs/specs/03-rating-engine.md` §5.1 | the new code in the error-code paragraph (`:772-782`), with a one-line meaning (DP-G4), spec first | **Yes**: §5.1 |
| `docs/specs/03-rating-engine.md` §3.5, FR-244's row (`:146`) | **only under DP-G1 (b)** | **Yes**: FR-244's row, **shared with WK-690 Slice 1's Task 6** |
| `backend/src/app/errors.py` | the new code in `RATING_ERROR_CODES` (`:286-365`) | **Yes**: that tuple |
| `packages/pricing-core/tests/test_rating_compile.py` | new tests appended | no |
| `packages/pricing-core/tests/test_rating_authored_strings.py` | new | no |
| `packages/pricing-core/tests/test_rating_score.py` | new tests appended (acceptance 6, 7) | no |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | **no change expected**: see acceptance 9 | only if a raise site is added |
| `backend/tests/test_rating_algorithms.py` | one save-route test appended (acceptance 8) | no |
| `docs/INDEX.md` | regenerated | exempt |

**Against the fix slice (#963, PL-9873):** its write set is `compile.py` (`compile_bundle`,
`__all__`, the new `check_step_refs_pinned`), `runtime.py` (`_load_boosters`, `load_bundle`),
`03` §5.1's catalogue line, `test_quote_input_raise_sites.py`'s `_INPUT_FREE`, and tests.
This slice shares `compile.py` (different functions) and `03` §5.1 (both add to the catalogue
paragraph). The maintainer's order puts this slice after it, so they never run together.

**Against WK-690 Slice 1 (PL-1295):** it edits `03` FR-244's row, `02` §4.6,
`pricing_core/data/*`, a `pyproject.toml`, `uv.lock` and `skills-map.md`
(`PL-1295:98-110`). It cites `rating/compile.py:245` only as a reference (`PL-1295:258`).
**Shared:** `03`. Under DP-G1 (a), this slice does not touch FR-244's row, and §3.5 is not
shared. Under DP-G1 (b), FR-244's row is the same existing definition, and the dispatch check
decides.

**Against WK-674 Slice 2:** `03` §5.1 is a shared path (a route row there, `PL-1237:773-774`).
Whether they may run together is decided at dispatch on the actual diffs, under `RL-1263:100`.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means
the failing run is quoted in the ledger with its failing assert line **and the cause the step
predicts**. A failure for any other cause is a plan defect, reported and not worked around.
Cases 1–5 are **save-time** checks through `validate_algorithm` (`compile.py:261`), unless a
case says otherwise.

1. **The allow-list refuses, red first, each case by its cause** (#967, *Acceptance*), marked
   `@pytest.mark.req("FR-244")`. Each refused string gives `EXPRESSION_INVALID_VOCABULARY`
   naming the step id, the field and the construct. Each is shown red (it saves) before the
   check exists:
   - an `expr` using, in turn: `%`, `in`, `a[0]`, `a.b`, `len('x')`, `sum([a, b])`.
2. **The allow-list accepts** (#967): `a ?? 0`, `x != 0 ? y / x : 0`, `round(p, 2)`,
   `min([max([x, 0]), 1])` and `abs(x)`, each in an `expr` **and** in a `condition`.
3. **Every authored field is covered, red first** (#967 item 3; #968's table). On the
   fixture `valid_algorithm()` (`packages/pricing-core/tests/test_rating_compile.py:15`),
   mutating the constraint step `s_minprem` or its bounds as #968 does, each row below returns
   the issue code shown. Today each returns `[]` (#968's table, measured at `9f63d0fe`, the tree
   above):

   | Field | String | Code |
   |---|---|---|
   | `condition` | `sum([office_premium_minor, 1]) >= 100` | `EXPRESSION_INVALID_VOCABULARY` |
   | `condition` | `office_premium_minor[0] >= 100` | `EXPRESSION_INVALID_VOCABULARY` |
   | `condition` | `office_premium_minor / expense_factor >= 100` | `EXPRESSION_UNGUARDED_DIVISION` |
   | `condition` | `office_premium_minor >=(((` | `EXPRESSION_INVALID_VOCABULARY` |
   | `condition` | `now() >= 100` | `EXPRESSION_NON_DETERMINISTIC` (DP-G2) |
   | `condition` | a 31-decimal-place literal | `EXPRESSION_SCALE_OVERFLOW` (DP-G2) |
   | `clamp_bounds.min` | `100 / expense_factor` | `EXPRESSION_UNGUARDED_DIVISION` |
   | `clamp_bounds.min` | `(((` | `EXPRESSION_INVALID_VOCABULARY` |
   | `expr` | `risk_premium_minor % 7` | `EXPRESSION_INVALID_VOCABULARY` |
   | `key_expr` | a `table` step's key `channel % 2` | `EXPRESSION_INVALID_VOCABULARY` |

   #968's two controls stay as they are: `expr` `risk_premium_minor / expense_factor` →
   `EXPRESSION_UNGUARDED_DIVISION`, and `expr` `(((` → `EXPRESSION_INVALID_VOCABULARY`.
   **Predicted red for each new row:** the assertion that the code is in the issues fails on
   `[]`. The literals are #968's; re-verify each against its text at the head cited above. The
   `key_expr` row is this plan's, because #968 "did not measure `key_expr`". A `now()` row that
   returns `EXPRESSION_INVALID_VOCABULARY` instead of `EXPRESSION_NON_DETERMINISTIC` (`now` is
   also off the allow-list) is acceptable only if DP-G2 rules that the first issue is enough.
   The ledger records which.
4. **The two cases that fail open are refused at save, red first** (#968, *Disposition*: "D2's
   condition and E4's clamp bound are refused at save"). On the score fixture
   (`packages/pricing-core/tests/test_rating_score.py:46-140`):
   - **D2:** `s_decl_cap`'s `condition` `((office_premium_minor / sanity_floor_minor) ?? 0) <= 2`,
     with `on_violation` `decline`, gives `EXPRESSION_UNGUARDED_DIVISION`;
   - **E3/E4:** a clamp bound `max` = `(sanity_cap_minor / sanity_floor_minor) ?? 999999999999`
     gives `EXPRESSION_UNGUARDED_DIVISION`.

   `compile_bundle` therefore refuses both, and neither reaches `score_one`. **Predicted red:**
   no issue; the bundle compiles. The ledger also quotes #968's score-level rows as the
   pre-fix evidence, as #968 reports them: D2 quoted at payable 1507 with `decline_reasons []`,
   and E4 at office 1436 with the cap lost. It adds the executor's own scratch run of D2 and
   E4 at the pre-change tree, never committed. A pre-fix result that differs from #968's is
   reported, not explained away.
5. **`??` is never a guard** (#967 item 2). `a / b ?? 0` and `a / b != null ? a / b : 0` stay
   `EXPRESSION_UNGUARDED_DIVISION`, in an `expr`, a `condition` and a clamp bound.
   `x != 0 ? y / x : 0` stays accepted. `_GUARD_MARKERS` contains neither `"??"` nor
   `"!= null"`, which a test asserts directly. With `"?:"` and `"coalesce("` removed, **every
   existing guard test passes unchanged** (#967, *Acceptance*: "Dead markers").
6. **A residual evaluation failure has its own code, red first** (DP-G4). The score fixture's
   A2/A3 and C1 rows (#968) are a decline condition or clamp bound dividing by a zero or null
   input. They are built by bypassing the save-time check, since after this slice they cannot
   be saved. Build a `Bundle` by hand, the route PL-9873's acceptance 5a names: `to_jdm`,
   `bundle_hash`, `load_bundle`, `score_one`. Each now raises `CodedError` with the new code,
   not `RATE_TABLE_MISS`. **Predicted red:** `RATE_TABLE_MISS` (`score.py:491`).
7. **A genuine miss keeps its code.** An `on_miss="error"` table step with no matching row,
   whose output a later `expr` consumes, still raises `RATE_TABLE_MISS` (the case
   `_reraise_engine_failure`'s docstring describes, `score.py:470-482`). The equivalent
   lookup raises `REFERENCE_LOOKUP_MISS`. The existing tests for them pass unchanged.
8. **Through the platform.** `POST /api/v1/rating-algorithms` with D2's condition returns 422
   `EXPRESSION_UNGUARDED_DIVISION` (`backend/src/app/platform/rating_algorithms.py:58-69`
   maps issues to the named error). Mirror the file's existing refusal test; do not invent
   helpers.
9. **The raise-site guard is accounted for.** The save-time checks return `ValidationIssue`
   lists, not raises, and `_reraise_engine_failure` keeps **one** `_raise_named` call with a
   computed code. So `test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case`
   passes with `_INPUT_FREE` unchanged. **If the implementation adds any `_raise_named`,
   `CodedError(` or `_model_call_failure(` call** under `pricing_core/rating`, the same commit
   adds its `_INPUT_FREE` entry with the reason (PL-9873, acceptance 7, for the form). The
   ledger records which case held.
10. **Stored and committed strings pass** (#967, *Acceptance*: "Stored data"). A test runs the
    allow-list over every authored string in the committed fixtures, examples and bench
    scripts, and each one passes. #967's sweep reported 37 distinct committed strings. The
    ledger quotes this test's count at the executor's tree, with the pattern it used, and
    reports any difference from 37, not explains it away.
11. **`??` semantics and OQ working id 9905 are untouched.** No change to how `??` evaluates, and
    none to `round`. `git diff origin/main...HEAD -- packages/pricing-core/src/pricing_core/rating/runtime.py`
    is empty.
12. **Coverage.** `uv run python scripts/req-coverage.py` lists the new tests against FR-244,
    FR-274, FR-276 and FR-255.
13. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree. The
    ledger quotes every command's rc, the `N passed` line and `HEAD`, and compares `N passed`
    with `origin/main`'s.
14. **Item 11.** Before the lead merges, the maintainer's **MERGE-ACK**, naming the PR's full
    head SHA, is recorded in the lead's channel file. That is a local file outside the
    repository, `~/gi-pricing-plan.local/channel/to-lead.md`, which `.claude/roles/lead.md:156-157`
    (rule 4) names. **It is never posted on the PR.** The slice's clean audit is filed. Per
    `CLAUDE.md` §13 a Slice closes on a clean audit and the lead's merge. No maintainer
    acceptance line is required for a slice, and none is to be waited on.

## Global Constraints

- **Spec before code** (`CLAUDE.md` §0; DP-G1). The allow-list is enforced only against
  FR-244 text that says so, whether it is on `main` or carried by this slice.
- **`??` is not changed and is not a guard** (#967 item 2). `_GUARD_MARKERS` never gains `"??"`
  or `"!= null"`.
- **The platform's generated strings stay outside the check** (#967 item 1): the `!(…)`
  wrapper (`runtime.py:292`) and the clamp ternaries (`runtime.py:310-313`). The check reads
  authored strings from the `RatingAlgorithm` before `to_wire`, and `runtime.py` is not edited
  (acceptance 11).
- **`pricing-core` stays standalone** (`.importlinter`). No `PlatformError`.
- **Refusal messages are input-free** (`safe_error.py:64-70`). They carry step ids, field
  names and constructs, never a quote value.
- **One implementation of the authored-string walk.** All four checks use `_authored_strings`,
  and no check keeps its own `isinstance(step, RatingExpressionStep)` loop.

## Scope

### Requirement coverage

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.5 | FR-244 | The allow-list, enforced over every authored string (#967 item 1) |
| `03` §3.11 | FR-274 | The division-guard check widened to every authored string; `??` never a guard (#967 items 2 and 3) |
| `03` §3.11 | FR-276 | The engine compile widened to every authored string (#967 item 3) |
| `03` §3.11 | FR-275 | The scale-cap check widened (DP-G2) |
| `03` §3.1 | FR-216 | The determinism check widened (DP-G2) |
| `03` §3.7 | FR-255 | A residual evaluation failure typed under its own code (DP-G4) |

**Not in this slice:**
- FR-244's text → WK-690 Slice 1, Task 6 (#967), unless DP-G1 rules (b).
- OQ working id 9905 (the rounding mode) → open, owner WK-1178, **not** this slice.
- Any change to `??` → none.
- The fix slice's pin-membership check → #963.

### Premises, read at the tree above

| # | Premise | Evidence |
|---|---|---|
| a | The four checks read only `RatingExpressionStep.expr` | `compile.py:142-163`, `:166-193`, `:196-230`, `:233-257`: each has `if not isinstance(step, RatingExpressionStep): continue` (#968, *Cause*) |
| b | `_GUARD_MARKERS` is `("!= 0", "> 0", "== 0", "< 0", "?:", "coalesce(", "if(", "guard")`, matched as substrings | `compile.py:41`, `:179-181` |
| c | `_check_vocabulary` is `zen.compile_expression` per `expr`, giving `EXPRESSION_INVALID_VOCABULARY` | `compile.py:233-257` |
| d | `coalesce(` does not compile; `??` compiles | the planner's run at `eeda8f4b`, recorded in PL-9873 acceptance 4: `zen.compile_expression('a * number(coalesce(x, "1.0"))')` raised `{"type":"parserError","source":"Incomplete parser output"}`, and the `??` form compiled |
| e | A constraint's `condition` is a `str`, and `clamp_bounds` is `dict[str, str] \| None` | `packages/model-schema/src/model_schema/rating.py:314-320` |
| f | `table` and `lookup` steps carry `key_expr: list[str]` | `rating.py:275-288` |
| g | The runtime wraps `condition` as `!(…)` and builds clamp ternaries from the bounds | `runtime.py:292`, `:310-313` |
| h | `_reraise_engine_failure` returns `RATE_TABLE_MISS` whenever **any** step is an `on_miss="error"` table, whatever actually failed | `score.py:484-497`; called at `:802` and `:952` |
| i | No evaluation-failure code exists | `backend/src/app/errors.py:286-365` and `03:772-782`: none among them names an evaluation failure |
| j | The existing check tests use `codes(algorithm)` over `valid_algorithm()` | `packages/pricing-core/tests/test_rating_compile.py:15`, `:109-159` |
| k | `_INPUT_FREE` counts `("rating/score.py", "_reraise_engine_failure"): 1` | `packages/pricing-core/tests/test_quote_input_raise_sites.py:66` |
| l | FR-244 at `03:146` still reads "the same restricted grammar as `02` §4.6" | `03:146` |

The executor re-reads each at its own tree, including after the fix slice merges, and stops on
any that no longer holds ([`README.md`](README.md) convention 4).

### Decision points

Each is the decision-maker's (`delivery-process.md` §3). The planner rules none of them. #967
has already ruled the allow-list's contents, `??`'s status, the dead markers and the widening
of the vocabulary and guard checks. None of that is reopened.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-G1 | This slice enforces FR-244's allow-list. The text that says so is WK-690 Slice 1's Task 6 (#967, *Which slice carries it*). What if that text is not on `main` when the fix slice merges? | (a) This slice's dispatch waits until WK-690 Slice 1's Task 6 commit is on `main`. The code then lands against its spec; (b) this slice carries #967's amended FR-244 sentence itself, spec first, and WK-690 Slice 1's Task 6 is re-scoped to the `02` §4.6 note only. FR-244's row becomes this slice's write, and PL-1295 needs a dated delta; (c) dispatch without the text, and reconcile later | **(a), with (b) as the fallback the lead may take if WK-690 Slice 1 is not merged when the fix slice merges.** (a) keeps one writer per spec row and needs no change to PL-1295. (b) is clean if taken before WK-690 Slice 1's executor reaches Task 6, but it is a replan of another Work's slice, so it is the lead's and the decision-maker's to route. (c) is code ahead of its spec, which `CLAUDE.md` §0 refuses | decision point | yes — dispatch | |
| DP-G2 | #968 requires "every non-baseline, non-control row" to return an issue. That includes a `now()` condition (FR-216) and a 31-decimal-place literal (FR-275), which the vocabulary and guard checks do not catch. Are `_check_determinism` and `_check_scale_cap` widened too? | (a) Yes: all four checks iterate `_authored_strings`; (b) only the two #967 names (vocabulary and division guard), with the other two rows deferred as a finding | **(a).** The walk is one helper, so widening two more checks costs one line each. #968's acceptance names both rows, and a 31-place literal in a clamp bound is the same hazard FR-275 exists for. (b) leaves #968 open against its own acceptance | decision point | yes — Task 3 | |
| DP-G3 | How is the allow-list enforced? The engine exposes a compile, not a syntax tree | (a) A small tokenizer in `pricing_core/rating/vocabulary.py`: numbers, single-quoted strings, names, the ruled operators, brackets; a name followed by `(` must be a ruled function; `[` is permitted only as the sole argument of `min` or `max`; `.` other than in a number, `{`, `%`, `^`, `!` as authored text, and `in` are refused. FR-276's engine compile then runs as today; (b) reuse `pricing_core.data.expressions`' parser in a new profile; (c) refuse by regex substring search | **(a).** #967 rules that `pricing_core.data.expressions` "never parses" the rating grammar, which rules out (b). (c) cannot tell `a.b` from `1.5`, or `[` as `min`'s argument from indexing. A tokenizer states the list as data (one tuple per class), so the list in the code is checkable against FR-244's text. The engine compile still catches what is on the list but malformed (#967 item 1: "a construct can be on the list and still not compile") | decision point | yes — Task 2 | |
| DP-G4 | Which code does a residual evaluation failure carry, and how is it told apart from a genuine miss? | Code: (a) a new `RATING_EVALUATION_FAILED`, added to `03` §5.1's catalogue with a one-line meaning (spec first) and to `RATING_ERROR_CODES`; (b) reuse `BUNDLE_COMPILE_FAILED` (a compile code, wrong for scoring); (c) reuse `INPUT_CONTRACT_VIOLATION` (an input-contract code; the input may be valid). Attribution: (i) read the `nodeId` the engine error carries (a JSON field, `runtime.py:89-90`). Report a table or lookup miss only when that node consumes an `on_miss="error"` table or lookup step's output; otherwise report the new code; (ii) report the new code for every engine failure, and drop the miss inference | **(a) with (i).** No existing code means "the engine failed evaluating an authored expression" (premise i), and FR-255 wants errors typed. (b) and (c) name a cause that did not happen, which is the defect being fixed. (i) keeps the genuine-miss path (acceptance 7), and it reads a structured field, not free text. (ii) would re-label a real table miss, which is the same class of error in reverse. **If the `nodeId` for a constraint's condition is its wire id (`<step_id>_v` or `<step_id>_c`, `runtime.py:292`, `:314`), the mapping strips the suffix. The executor proves this on the red run and does not assume it** | decision point | yes — Task 4 | |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, cut
  from `main` **after** the fix slice (#963) merged.
- [ ] `uv sync --all-packages` (`dev-commands`).
- [ ] Re-derive premises a–l at that tree. Record each in the ledger.
- [ ] `gh pr list --state open`, and read anything that rules on FR-244, FR-274, FR-276,
  FR-255, `compile.py`'s checks, `??` or OQ working id 9905 ([`README.md`](README.md)
  convention 4). Name the SHA read. **Re-point #967 and #968 to their ids if minted.**
- [ ] Confirm DP-G1 to DP-G4's resolutions, by record id, in the ledger. **Under DP-G1 (a),
  confirm FR-244's amended text is on `main`** (`03:146` carries "restricted to an enforced
  allow-list of operators and functions"). If it is not, stop and report.
- [ ] Confirm the `RL-1263` slot and the dispatch record's write-set check.

### Task 1: Spec — the new code (DP-G4), and FR-244 only under DP-G1 (b)

**Files:** Modify `docs/specs/03-rating-engine.md` (§5.1's error-code paragraph, `:772-782`;
FR-244's row `:146` only under DP-G1 (b)).

- [ ] Add the DP-G4 code to §5.1's catalogue, with a dated one-line meaning:

  > *`RATING_EVALUATION_FAILED` (added 2026-09-30, on the finding filed as #968, FR-255): the
  > engine failed evaluating an authored expression, condition or clamp bound at scoring, and
  > the failure is not a table or lookup miss.*

  Use the name DP-G4 rules. Replace "#968" with the finding's id if it is minted by then.
- [ ] DP-G1 (b) only: append #967's amended FR-244 sentence (#967, *The amended FR-244 text*),
  verbatim, to FR-244's cell.
- [ ] `python3 scripts/audit-docs.py`. Commit with Task 4's code, since the spec and the code
  that raises the code land together. Or commit the spec alone first, if the executor keeps
  the gate green in between.

### Task 2: The authored-string walk and the allow-list — red first

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/compile.py`; create
`packages/pricing-core/src/pricing_core/rating/vocabulary.py` (DP-G3 (a));
create `packages/pricing-core/tests/test_rating_authored_strings.py`; append to
`packages/pricing-core/tests/test_rating_compile.py`.

**Interfaces:**
- Produces: `_authored_strings(algo: RatingAlgorithm) -> list[tuple[str, str, str]]` in
  `compile.py`, returning `(step_id, field, text)`. `field` is one of `expr`, `condition`,
  `clamp_bounds.min`, `clamp_bounds.max` or `key_expr[i]`.
- Produces: `check_allow_list(text: str) -> str | None` in `vocabulary.py`. It returns the first
  refused construct, or `None`.

- [ ] **Red first:** acceptance 1, 2 and the vocabulary rows of acceptance 3. Predicted red:
  `[]` for each refused case, because the check does not exist. Quote them.
- [ ] `vocabulary.py`: the ruled lists as tuples (#967 item 1): operators, literals, and the
  functions `round` (1 or 2 arguments, the second an integer literal), `min` and `max` (a
  single array-literal argument), `abs`, `floor` and `ceil`. Implement the tokenizer.
  Unit-test it against every ruled construct and every "Not on the list" construct
  (#967 item 1).
- [ ] `_authored_strings` in `compile.py`, walking premises e and f. `_check_vocabulary`
  iterates it. For each string it runs `check_allow_list` first, then `zen.compile_expression`,
  issuing `EXPRESSION_INVALID_VOCABULARY` with `field` set.
- [ ] Green. Acceptance 10's committed-string test.
- [ ] Commit: `fix(rating): FR-244's allow-list enforced over every authored string (WK-1178)`.

### Task 3: The guard, determinism and scale checks widened; the dead markers removed — red first

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/compile.py`; append to
`packages/pricing-core/tests/test_rating_compile.py`.

- [ ] **Red first:** the guard, determinism and scale rows of acceptance 3, and acceptance 4
  (D2, E3/E4). Predicted red: `[]`, or a compiled bundle, for each.
- [ ] `_check_division_guards`, and per DP-G2 `_check_determinism` and `_check_scale_cap`,
  iterate `_authored_strings`. Remove `"?:"` and `"coalesce("` from `_GUARD_MARKERS`. Add the
  test that asserts `"??"` and `"!= null"` are absent (acceptance 5).
- [ ] Green. Every existing guard test passes unchanged (acceptance 5).
- [ ] Commit: `fix(rating): FR-274's guard, FR-216 and FR-275 checks cover every authored string (WK-1178)`.

### Task 4: The residual evaluation code — red first

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/score.py`
(`_reraise_engine_failure`); `backend/src/app/errors.py` (`RATING_ERROR_CODES`); append to
`packages/pricing-core/tests/test_rating_score.py`.

- [ ] **Red first:** acceptance 6, on hand-built bundles (the route PL-9873's acceptance 5a
  names). Predicted red: `RATE_TABLE_MISS`.
- [ ] Per DP-G4, choose the code inside the existing single `_raise_named` call. Parse the
  engine error's `nodeId` from its JSON; do not match free text. Add the code to
  `RATING_ERROR_CODES` beside `RATE_TABLE_MISS`.
- [ ] Acceptance 7 green (a genuine miss keeps its code). Acceptance 9: run the raise-site
  guard. It must pass with `_INPUT_FREE` unchanged, or the same commit adds the entry.
- [ ] Commit, with Task 1's spec line if not already committed:
  `fix(rating): a residual evaluation failure is RATING_EVALUATION_FAILED, not RATE_TABLE_MISS (FR-255, WK-1178)`.

### Task 5: Through the platform

**Files:** Append to `backend/tests/test_rating_algorithms.py`.

- [ ] Acceptance 8, red first. Predicted red: 201, because the condition saves today.
- [ ] Commit.

### Task 6: The gate and the ledger

- [ ] The full two-half gate on the committed tree, with each rc, the `N passed` line and
  `HEAD`, against `origin/main`'s `N passed`.
- [ ] The ledger records:
  - the tree and premises a–l;
  - the red quotes;
  - #968's pre-fix rows and the executor's own scratch run of D2 and E4;
  - the DP resolutions by record id;
  - acceptance 9's outcome;
  - acceptance 10's count and pattern.
- [ ] Item 11 (acceptance 14).

## Hand-off

WK-1250 Slice 1 is dispatched after this slice merges (the maintainer's order).

## Self-review

- **#967, clause by clause:**
  - item 1, the allow-list, every authored string, the generated strings outside it →
    acceptance 1–3, Task 2, Global Constraints;
  - item 2, `??` documented, never a guard, dead markers removed → acceptance 5, Task 3;
  - item 3, the compile and the guard widened → acceptance 3, Tasks 2–3;
  - *Acceptance* → acceptance 1, 2, 3, 5 and 10;
  - *Which slice carries it* → Status, and DP-G1.
- **#968, clause by clause:**
  - D2 and E4 refused at save → acceptance 4;
  - every table row returns an issue → acceptance 3, with DP-G2 for the `now()` and scale rows;
  - the misleading `RATE_TABLE_MISS` → acceptance 6 and 7, DP-G4;
  - `key_expr` unmeasured → acceptance 3's added row.
- **The lead's scope list:** 1 → Tasks 2–3; 2 → Task 3; 3 → acceptance 3 and 4; 4 → DP-G4,
  Task 4; 5 → acceptance 11; 6 → DP-G1 and Dependencies.
- **Literals** were read at the tree above (premises) or quoted from #967 and #968 at the heads
  named. `_authored_strings`, `check_allow_list`, `vocabulary.py` and
  `RATING_EVALUATION_FAILED` are proposals, named once each and used consistently.
- **Open:** DP-G1 to DP-G4, the decision-maker's. #967 and #968 unminted. The fix slice
  unmerged.
