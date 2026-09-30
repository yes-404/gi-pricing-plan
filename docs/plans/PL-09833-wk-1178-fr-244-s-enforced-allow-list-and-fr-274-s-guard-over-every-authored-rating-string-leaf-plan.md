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
- the determinism and scale-cap checks, through one registry (the maintainer's 10:55:40 BST entry).

A decline condition or a clamp bound that would silently fail open at scoring is refused at
save. A residual evaluation failure at scoring is reported under its own code, not as
`RATE_TABLE_MISS`.

**Architecture — the class is fixed structurally.** Four checks skip conditions today, and each
picks its own fields (#968, *Cause*: "a class of four checks"). The maintainer's entry
"2026-09-30 10:55:40 BST — time-citation correction acknowledged; #968 widened, so fix the CLASS
structurally" requires the fix to be structural. It has three parts:
1. **One enumerator of every authored expression field**,
   `authored_expression_fields(algo) -> list[AuthoredString]`. It is driven by a declared registry,
   `EXPRESSION_FIELDS`, and it is the only code that reads those fields off a step. Every other
   string-bearing field of every step model is listed in `NON_EXPRESSION_FIELDS`, with a reason.
2. **One registry of expression checks**, `STRING_CHECKS`. Each check is a function of **one
   string**, `(text) -> (code, message) | None`, so it cannot choose fields.
   `validate_algorithm` applies every registered check to every enumerated string. The four
   existing checks (`_check_determinism`, `_check_division_guards`, `_check_scale_cap`,
   `_check_vocabulary`) are rewritten into that form. The allow-list (DP-G3) is added as one
   more entry, and `_GUARD_MARKERS` loses its two dead entries.
3. **A matrix test and two closure tests** (acceptance 3a–3c) make a new field, or a new check,
   that escapes the design fail a test.

Separately, `score.py`'s `_reraise_engine_failure` stops inferring a table miss when the failing
node is not downstream of one (DP-G4).

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
MINTED"; first read at `fb4833a9`, re-read at its head `6eb68d776aa7ef974fc234be56bbcd0b8a192908`, which every quote below is checked against). This plan covers its
*Ruled* items 1 to 3, its *Which slice carries it* ("The code: one WK-1178 slice, after the
~16:00 fix slice") and its *Acceptance* section.

It also discharges the finding in #968 (FD working id 9885, HIGH in force). It was first read at
`46b4d445` and then `fede7e5d`, and re-read at `02f3f588` and at its live head `7222023c`, which every
quote below is checked against. It is titled "Rating condition and clamp_bounds strings
are never validated — no vocabulary, syntax or division-guard check (FR-244, FR-274, FR-276)".
That finding's *Disposition* names this slice as owner: "Owner: the #967 WK-1178 code slice (RL
working id 9904, cited as prose), kept separate from the #963 fix slice". Neither record is minted, so each is cited
by PR and working id, and Task 0 re-points both at mint.

**The maintainer's entries,** cited by their header times as read in `to-lead.md`, the lead's
local channel file, outside the repository:
- "2026-09-30 10:53:10 BST — DECISION: condition/clamp FD (B) — HIGH on independent
  reproduction; owner and order; two small items". Owner: this slice. **Order, fixed:** the fix
  slice (#963, whose plan and slice row carry working ids 9873 and 9872) → **this slice** →
  WK-1250 Slice 1, all serialised on `compile.py` under `RL-1263`. It also gives the evaluation
  code's acceptance line (acceptance 6).
- "2026-09-30 10:55:40 BST — … fix the CLASS structurally": the enumerator, the matrix test and
  the closure tests. The header is elided at "…" to its operative clause.
- "2026-09-30 10:57:06 BST — #968 HIGH in force: …": each unguarded committed condition or bound
  with `/` becomes an acceptance case (acceptance 10).
- "2026-09-30 10:58:13 BST — DATED CORRECTION to my 10:53:10 entry …": stored exposure is 0, and
  committed exposure is #968's list.
- "2026-09-30 11:05:21 BST — DECISION: I accept #967's departure; it supersedes the rounding part
  of my 10:46:20 (A)": **`round`, `floor` and `ceil` are not on P2's allow-list**. Money is
  rounded only at the output step (FR-226, NFR-496, FR-248). The engine's facts are documented
  in FR-244's text, not checked here: its own `round` is half away from zero, and at the float
  boundary a `Decimal` input is refused while a `str` input is accepted as a ZEN string, not a
  number. OQ working id 9905 is broadened, and stays out of scope.
- "2026-09-30 11:07:11 BST — DECISION: #970 DP-G4 residual → (a), recorded as a LOW FD; #970
  G1–G3 accepted". The maintainer accepted the rulings on this plan's decision points: #970
  (RL working id 9982, read at `39dce368ef582b067a9be931ee2bd63ca2c6dd03`, unminted). The G4
  residual is recorded as a LOW finding, owner WK-1178, which auditor-928 is filing; it has no
  PR at this revision.

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
3. The decision-maker's rulings on DP-G1, DP-G3, DP-G4 and DP-G5 (DP-G2 is withdrawn: the maintainer decided it). **Ruled** in #970 (working id 9982, at `39dce368`, unminted): (a), (a), (a)+(i), (a)+(i). The maintainer accepted them at 11:07:11 BST.
4. #967 and #968 minted, and this plan's citations re-pointed (Task 0).
5. A free `RL-1263` gate slot, and the lead's dispatch record with its write-set check (below).

### Dependencies

- **On the fix slice (#963):** it edits `compile_bundle` and adds `check_step_refs_pinned`
  (#963's plan (working id 9873), Task 2). This slice edits `_check_determinism`, `_check_division_guards`,
  `_check_scale_cap`, `_check_vocabulary` and `_GUARD_MARKERS`. Those are different
  definitions in the same file, but the maintainer's order serialises them. The later slice
  merges `main` and re-runs its gate. #963 also adds `_INPUT_FREE` entries in
  `test_quote_input_raise_sites.py` (#963's plan (working id 9873), acceptance 7), which this slice may touch too
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
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `_GUARD_MARKERS` (`:41`) loses `"?:"` and `"coalesce("`; `_check_determinism` (`:142-163`), `_check_division_guards` (`:166-193`), `_check_scale_cap` (`:196-230`) and `_check_vocabulary` (`:233-258`) become one-string checks in `STRING_CHECKS`; `validate_algorithm` (`:261-275`) applies the registry over the enumerator | **Yes**: those six definitions |
| `packages/pricing-core/src/pricing_core/rating/authored.py` (new, DP-G5) | `EXPRESSION_FIELDS`, `NON_EXPRESSION_FIELDS`, `AuthoredString`, `authored_expression_fields` | no (new) |
| `packages/pricing-core/src/pricing_core/rating/vocabulary.py` (new, DP-G3) | the allow-list tokenizer, `check_allow_list` | no (new) |
| `packages/pricing-core/src/pricing_core/rating/score.py` | `_reraise_engine_failure` (`:469-498`) chooses the code (DP-G4); **its single `_raise_named` call stays single** | **Yes**: that function |
| `docs/specs/03-rating-engine.md` §5.1 | the new code in the error-code paragraph (`:772-782`), with a one-line meaning (DP-G4), spec first | **Yes**: §5.1 |
| `docs/specs/03-rating-engine.md` §3.5, FR-244's row (`:146`) | **only under DP-G1 (b)** | **Yes**: FR-244's row, **shared with WK-690 Slice 1's Task 6** |
| `backend/src/app/errors.py` | the new code in `RATING_ERROR_CODES` (`:286-365`) | **Yes**: that tuple |
| `packages/pricing-core/tests/test_rating_compile.py` | new tests appended | no |
| `packages/pricing-core/tests/test_rating_authored_fields.py` | new: the matrix test and the two closure tests (acceptance 3a–3c) | no |
| `packages/pricing-core/tests/test_rating_vocabulary.py` | new: the tokenizer's unit tests | no |
| `packages/pricing-core/tests/test_rating_score.py` | new tests appended (acceptance 6, 7) | no |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | **no change expected**: see acceptance 9 | only if a raise site is added |
| `backend/tests/test_rating_algorithms.py` | one save-route test appended (acceptance 8) | no |
| `docs/INDEX.md` | regenerated | exempt |

**Against the fix slice (#963, plan working id 9873):** its write set is `compile.py` (`compile_bundle`,
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
   - an `expr` using, in turn: `%`, `in`, `a[0]`, `a.b`, `len('x')`, `sum([a, b])`;
   - **no rounding function** (#967 at `6eb68d77`, *Acceptance*: "The interim rule on rounding
     must be shown red, like any other refusal"; the maintainer's 11:05:21 BST entry): an `expr`
     using `round(p, 2)`, then `floor(x)`, then `ceil(x)`. Each is refused, red first. **Predicted
     red:** it saves today, because the engine compiles all three.
1a. **The tokenizer's lists equal FR-244's text** (#970, DP-G3), red first on a planted
    difference (Task 3).
2. **The allow-list accepts** (#967): `a ?? 0`, `x != 0 ? y / x : 0`, `min([max([x, 0]), 1])`
   and `abs(x)`, each in an `expr` **and** in a `condition`.
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
   | `condition` | `now() >= 100` | `EXPRESSION_NON_DETERMINISTIC` |
   | `condition` | a 31-decimal-place literal | `EXPRESSION_SCALE_OVERFLOW` |
   | `clamp_bounds.min` | `100 / expense_factor` | `EXPRESSION_UNGUARDED_DIVISION` |
   | `clamp_bounds.min` | `(((` | `EXPRESSION_INVALID_VOCABULARY` |
   | `expr` | `risk_premium_minor % 7` | `EXPRESSION_INVALID_VOCABULARY` |
   | `key_expr` | a `table` step's key `channel % 2` | `EXPRESSION_INVALID_VOCABULARY` |

   #968's two controls stay as they are: `expr` `risk_premium_minor / expense_factor` →
   `EXPRESSION_UNGUARDED_DIVISION`, and `expr` `(((` → `EXPRESSION_INVALID_VOCABULARY`.
   **Predicted red for each new row:** the assertion that the code is in the issues fails on
   `[]`. The literals are #968's; re-verify each against its text at the head cited above. The
   `key_expr` row is this plan's, because #968 "did not measure `key_expr`". Every registered check
   runs on every string, so a `now()` row yields `EXPRESSION_NON_DETERMINISTIC` **and**
   `EXPRESSION_INVALID_VOCABULARY` (`now` is also off the allow-list). The test asserts that the
   row's own code is among the issues, which is `codes(algorithm)`'s existing form
   (`test_rating_compile.py:116`).
3a. **The matrix, red first.** In `test_rating_authored_fields.py`, a test is parametrised over
    **every (check, field) pair**: each entry of `STRING_CHECKS` × each entry of
    `EXPRESSION_FIELDS`. It plants that check's violation in that field of `valid_algorithm()`,
    and asserts that the check's code is issued with that `field`. The violations are:
    - `now() >= 1`, for determinism;
    - a 31-decimal-place literal, for scale;
    - `a / b >= 1`, for the division guard;
    - `(((`, for the engine compile;
    - `a % 2 >= 1`, for the allow-list.

    Each is adapted to the field's shape: a bare expression for `expr` and the bounds, a boolean
    for `condition`, and a key for `key_expr`. The parametrisation is **generated from the two
    registries**, not written out, so a new check or field adds its cells automatically.
    **Predicted red:** every cell whose field is not `expr` fails on `[]` (#968's table), and so
    does the allow-list column, whose check does not exist yet. The `expr` cells of the other
    four checks are green today. Each red cell is quoted by its (check, field) id.
3b. **Closure 1 — a new authored field cannot escape the enumerator.** A schema walk over the
    `RatingStep` union's members (`model_schema.rating`) lists every field whose annotation
    carries `str` (`str`, `str | None`, `list[str]`, `str | list[str]`, `dict[str, str]`,
    `dict[str, str] | None`). **It unwraps `Annotated[str, …]`** to its base type, so
    `RatingResultType` (`rating.py:235`) counts as `str`. `Literal[...]` fields are closed sets
    and are excluded. **Each field is resolved to the class that defines it**, the first class in
    the model's MRO whose own `__annotations__` declares it. So the five base fields (`step_id`,
    `label`, `note`, `consumes`, `produces`) are one entry each, under `RatingStepBase`, not
    seven entries each. Every listed `(defining class, field)` must be in **exactly one** of
    `EXPRESSION_FIELDS` or `NON_EXPRESSION_FIELDS`, and every registry entry must name a real
    field (no stale entries).
    **`RatingExpressionStep.result_type` (`rating.py:294`, typed `RatingResultType`) is a
    non-expression field.** It names the step's declared result type (FR-227). The result-type
    check reads it through `compile.py:102` (`types[name] = step.result_type`), and the engine
    never evaluates it. auditor-933 ran this walk's rule
    over the real `RatingStep` union at `1cbcf474`: 46 (model, field) rows, all classified except
    this one. So 3b would have gone red on day one without it. *(Added 2026-09-30 on
    auditor-933's G1.)*
    **`RatingLookupStep.as_at` (`rating.py:279`) is out of the enumerator**, in
    `NON_EXPRESSION_FIELDS`, per DP-G5 (i) as recommended. The reasons: nothing in
    `pricing_core/rating` evaluates it (`runtime.py:26-35`: the window is "translated as an exact
    key match only"), and its committed values are input names, not expressions:
    `"effective_date"` (`packages/pricing-core/tests/test_rating_compile.py:37`) and `"postcode"`
    (`test_rating_runtime.py:445`, `test_rating_score.py:372`). Its registry comment says that it
    moves to `EXPRESSION_FIELDS` when the runtime evaluates it. If DP-G5 rules (ii), the walk
    still forces a classification, and the matrix gains its column.
    **Broken-input proof:** the walk, run over a test-local subclass that adds `formula: str`,
    reports `formula` as unclassified, and the test fails. The ledger quotes that red.
3c. **Closure 2 — a new check cannot bypass the enumerator.** Two assertions over
    `pricing_core/rating/compile.py` and `vocabulary.py`, by `ast`:
    - (i) the attribute names of `EXPRESSION_FIELDS` (`expr`, `condition`, `clamp_bounds`,
      `key_expr`, derived from the registry, never listed by hand) are read inside
      `authored.py`'s enumerator and nowhere else in those modules;
    - (ii) every module-level function named `_check_*` is either in `STRING_CHECKS` or in the
      explicit `ALGORITHM_CHECKS` tuple (`_check_result_types`, `compile.py:114`, which reads
      output steps, not expression strings), and `validate_algorithm` calls exactly those.

    **Predicted red at the tree above:** (i) and (ii) both report the four loops that read step
    text themselves. Each skips non-expression steps at `compile.py:146`, `:176`, `:200` and
    `:242`, and reads `.expr` at `:148`, `:178`, `:202` and `:245`. The prose rule in Global
    Constraints ("One enumerator, one check registry") is enforced by this test, not by review.
    **Broken-input proof for each:** the predicate, run over a source string that adds
    `_check_x(algo)` reading `step.expr`, reports both the direct read and the unregistered check.
    The ledger quotes both reds. `to_jdm` and `runtime.py`, which read these fields to **wire**
    them, are out of scope. They are the platform's translation, not a check (Global
    Constraints). The predicate's module list says so explicitly.
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
6. **A residual evaluation failure has its own code, red first** (DP-G4, ruled by #970). The
   score fixture's A2/A3 and C1 rows (#968) are a decline condition or clamp bound dividing by
   a zero or null input. They are built by bypassing the save-time check, since after this slice
   they cannot be saved. Build a `Bundle` by hand, the route #963's plan (working id 9873),
   acceptance 5a, names: `to_jdm`, `bundle_hash`, `load_bundle`, `score_one`.
   - **Scope, narrowed as #970 rules and the maintainer accepted (11:07:11 BST):** every
     condition or bound **whose step does not directly consume an `on_miss="error"` output**
     raises `CodedError` `RATING_EVALUATION_FAILED`, never `RATE_TABLE_MISS`. This covers every
     row of #968's reproduction table, because those constraints consume
     `office_premium_minor`, not a table's output (#970, DP-G4).
   - Attribution reads the engine error's JSON `nodeId`, which **is the step id** for
     expression, condition and clamp failures alike (#970, *Probe*: `"nodeId":"s_office"`,
     `"s_decl_cap"`, `"s_clamp"`). No suffix mapping is needed.
   - A missing or unparseable `nodeId`, and the former bare `raise exc` fallthrough
     (`score.py:497`), also raise `RATING_EVALUATION_FAILED`. So no engine failure escapes
     `score_one` as a bare `RuntimeError`, and that is tested red first (#970, *Acceptance*).
   - **The residual, stated and not tested as fixed.** A failing step that itself directly
     consumes an `on_miss="error"` output, and fails for another reason, still reports the miss
     code. The engine error has the same shape in both cases (#970, *Probe*, rows EXPR and MISS).
     It is a wrong diagnosis on a refused quote, never a silent price. Its fix, the wire-level
     change `score.py:469-483`'s docstring names, is outside this slice. It is recorded as the
     LOW finding that auditor-928 is filing (owner WK-1178), cited here as prose until it has a PR.

   **Predicted red:** `RATE_TABLE_MISS` (`score.py:491`), and a bare `RuntimeError` for the
   fallthrough case.
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
   adds its `_INPUT_FREE` entry with the reason (#963's plan (working id 9873), acceptance 7, for the form). The
   ledger records which case held.
10. **Stored and committed strings.**
    - **Committed exposure** (the maintainer's 10:57:06 BST entry: each unguarded committed
      condition or bound with `/` becomes an acceptance case). #968 at `02f3f588` (*Exposure*)
      lists every committed rating string containing `/`, at `9f63d0fe`: "4 strings, all in the
      `expr` field", so **0 unguarded condition or clamp-bound strings**. Of the 4, three are
      deliberate negative tests (`backend/tests/test_rating_algorithms.py:112`,
      `packages/pricing-core/tests/test_rating_compile.py:125` and
      `packages/pricing-core/tests/test_rating_compile_bundle.py:248`) and one is guarded
      (`test_rating_compile.py:136`). So no committed condition or bound becomes an acceptance
      case, and the planted cells of 3a stand for them. **Task 0 re-reads #968's list at the
      executor's tree.** Any unguarded condition or bound it now lists becomes a case here,
      rewritten with a guard or shown refused at save, red first. #968's limits are carried: one
      line per string, and not a proof for later commits.
    - **The committed rating strings, checked both ways** (#967, *Acceptance*: "Stored data"). A
      test extracts every authored rating string from the committed fixtures, examples and bench
      scripts, and runs **the allow-list and the division guard** over each one:
      - every string that a committed test **expects to be accepted** passes both;
      - every **deliberate negative fixture stays refused**, under the code its own test asserts:
        the three unguarded divisions above; `test_rating_compile.py:116`'s `now()`; and the
        vocabulary test's foreign function (`test_rating_compile.py:152-159`).

      #967's sweep reported 37 distinct strings. The ledger quotes the test's count and pattern
      at the executor's tree, and reports any difference from 37, not explains it away.
    - **Out of scope:** data-preparation `expression` strings (for example
      `packages/pricing-core/tests/test_prepare.py` and `scripts/bench-data.py`). They are
      parsed by `pricing_core.data.expressions` under `02` §4.6, not by the rating engine (#967:
      the rating grammar "is not one of §4.6's profiles"). The extractor keys on the rating
      step models' fields, and the ledger names the pattern.
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
- **One enumerator, one check registry** (the maintainer's 10:55:40 BST entry). No check reads a
  step's expression fields itself. 3b and 3c enforce it, and it is not left to review.
- **`to_jdm` and `runtime.py` are not checks.** They read the same fields to wire them, and they
  stay as they are. Closure 2's predicate names the modules it covers.

## Scope

### Requirement coverage

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.5 | FR-244 | The allow-list, enforced over every authored string (#967 item 1) |
| `03` §3.11 | FR-274 | The division-guard check widened to every authored string; `??` never a guard (#967 items 2 and 3) |
| `03` §3.11 | FR-276 | The engine compile widened to every authored string (#967 item 3) |
| `03` §3.11 | FR-275 | The scale-cap check widened, through the registry |
| `03` §3.1 | FR-216 | The determinism check widened, through the registry |
| `03` §3.7 | FR-255 | A residual evaluation failure typed under its own code (DP-G4) |

**Not in this slice:**
- FR-244's text → WK-690 Slice 1, Task 6 (#967), unless DP-G1 rules (b).
- OQ working id 9905, broadened to "is rounding offered anywhere but an output step" (the
  maintainer's 11:05:21 BST entry) → open, owner WK-1178, **not** this slice. This slice only
  refuses `round`, `floor` and `ceil` at save, as the allow-list requires.
- Any change to `??` → none.
- The fix slice's pin-membership check → #963.

### Premises, read at the tree above

| # | Premise | Evidence |
|---|---|---|
| a | The four checks read only `RatingExpressionStep.expr` | `compile.py:142-163`, `:166-193`, `:196-230`, `:233-257`: each has `if not isinstance(step, RatingExpressionStep): continue` (#968, *Cause*) |
| b | `_GUARD_MARKERS` is `("!= 0", "> 0", "== 0", "< 0", "?:", "coalesce(", "if(", "guard")`, matched as substrings | `compile.py:41`, `:179-181` |
| c | `_check_vocabulary` is `zen.compile_expression` per `expr`, giving `EXPRESSION_INVALID_VOCABULARY` | `compile.py:233-257` |
| d | `coalesce(` does not compile; `??` compiles | the planner's run at `eeda8f4b`, recorded in #963's plan (working id 9873) acceptance 4: `zen.compile_expression('a * number(coalesce(x, "1.0"))')` raised `{"type":"parserError","source":"Incomplete parser output"}`, and the `??` form compiled |
| e | A constraint's `condition` is a `str`, and `clamp_bounds` is `dict[str, str] \| None` | `packages/model-schema/src/model_schema/rating.py:314-320` |
| f | `table` and `lookup` steps carry `key_expr: list[str]` | `rating.py:275-288` |
| g | The runtime wraps `condition` as `!(…)` and builds clamp ternaries from the bounds | `runtime.py:292`, `:310-313` |
| h | `_reraise_engine_failure` returns `RATE_TABLE_MISS` whenever **any** step is an `on_miss="error"` table, whatever actually failed | `score.py:484-497`; called at `:802` and `:952` |
| i | No evaluation-failure code exists | `backend/src/app/errors.py:286-365` and `03:772-782`: none among them names an evaluation failure |
| j | The existing check tests use `codes(algorithm)` over `valid_algorithm()` | `packages/pricing-core/tests/test_rating_compile.py:15`, `:109-159` |
| k | `_INPUT_FREE` counts `("rating/score.py", "_reraise_engine_failure"): 1` | `packages/pricing-core/tests/test_quote_input_raise_sites.py:66` |
| l | FR-244 at `03:146` still reads "the same restricted grammar as `02` §4.6" | `03:146` |
| m | **The step models' string-bearing fields.** Expression fields: `RatingExpressionStep.expr`; `RatingConstraintStep.condition`; every value of `RatingConstraintStep.clamp_bounds` (`dict[str, str] \| None`, of which the runtime reads `min` and `max`); `RatingTableStep.key_expr[i]`; `RatingLookupStep.key_expr[i]`. Non-expression fields: `step_id`, `label`, `note`, `consumes` and `produces` (on the base); `RatingInputStep.input_name`; `RatingLookupStep.as_at` (DP-G5); `RatingModelCallStep.feature_map` (graph name to feature slug); `RatingConstraintStep.reason_code`; `RatingOutputStep.output_name`; `RatingExpressionStep.result_type` (`RatingResultType`, an `Annotated[str, AfterValidator(…)]`, `rating.py:235`, `:294`). `Literal` fields and `ArtifactRef` fields are not strings | `packages/model-schema/src/model_schema/rating.py:257-326`; the runtime reads `expr` (`runtime.py:160`), `key_expr` (`:205`, `:236`), `condition` (`:292`) and `clamp_bounds` (`:303-314`); `as_at` is read by nothing in `pricing_core/rating` (`runtime.py:26-35`: the window is "translated as an exact key match only") |
| n | `validate_algorithm` calls five checks in order; `_check_result_types` is the one that does not read expression strings | `compile.py:261-275`, `:114-140` |
| o | #968's committed-exposure list: 4 strings with `/`, all `expr`; 0 in a condition or bound | #968 at `02f3f588`, *Exposure* |

The executor re-reads each at its own tree, including after the fix slice merges, and stops on
any that no longer holds ([`README.md`](README.md) convention 4).

### Decision points

Each is the decision-maker's (`delivery-process.md` §3). The planner rules none of them. #967
has already ruled the allow-list's contents, `??`'s status, the dead markers and the widening
of the vocabulary and guard checks. None of that is reopened.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-G1 | This slice enforces FR-244's allow-list. The text that says so is WK-690 Slice 1's Task 6 (#967, *Which slice carries it*). What if that text is not on `main` when the fix slice merges? | (a) This slice's dispatch waits until WK-690 Slice 1's Task 6 commit is on `main`. The code then lands against its spec; (b) this slice carries #967's amended FR-244 sentence itself, spec first, and WK-690 Slice 1's Task 6 is re-scoped to the `02` §4.6 note only. FR-244's row becomes this slice's write, and PL-1295 needs a dated delta; (c) dispatch without the text, and reconcile later | **(a), with (b) as the fallback the lead may take if WK-690 Slice 1 is not merged when the fix slice merges.** (a) keeps one writer per spec row and needs no change to PL-1295. (b) is clean if taken before WK-690 Slice 1's executor reaches Task 6, but it is a replan of another Work's slice, so it is the lead's and the decision-maker's to route. (c) is code ahead of its spec, which `CLAUDE.md` §0 refuses | decision point | yes — dispatch | #970 (working id 9982), at `39dce368`: **(a)**, with (b) as the lead's fallback, only before WK-690 Slice 1 reaches Task 6 |
| DP-G2 | *(Withdrawn 2026-09-30: the maintainer's 10:55:40 BST entry requires **every** expression check to iterate one enumerator, which is option (a). The row is kept so the id is not reused.)* #968 requires "every non-baseline, non-control row" to return an issue. That includes a `now()` condition (FR-216) and a 31-decimal-place literal (FR-275), which the vocabulary and guard checks do not catch. Are `_check_determinism` and `_check_scale_cap` widened too? | (a) Yes: all four checks iterate `_authored_strings`; (b) only the two #967 names (vocabulary and division guard), with the other two rows deferred as a finding | **(a).** The walk is one helper, so widening two more checks costs one line each. #968's acceptance names both rows, and a 31-place literal in a clamp bound is the same hazard FR-275 exists for. (b) leaves #968 open against its own acceptance | withdrawn | — | the maintainer, 10:55:40 BST |
| DP-G3 | How is the allow-list enforced? The engine exposes a compile, not a syntax tree | (a) A small tokenizer in `pricing_core/rating/vocabulary.py`: numbers, single-quoted strings, names, the ruled operators, brackets; a name followed by `(` must be a ruled function; `[` is permitted only as the sole argument of `min` or `max`; `.` other than in a number, `{`, `%`, `^`, `!` as authored text, and `in` are refused. FR-276's engine compile then runs as today; (b) reuse `pricing_core.data.expressions`' parser in a new profile; (c) refuse by regex substring search | **(a).** #967 rules that `pricing_core.data.expressions` "never parses" the rating grammar, which rules out (b). (c) cannot tell `a.b` from `1.5`, or `[` as `min`'s argument from indexing. A tokenizer states the list as data (one tuple per class), so the list in the code is checkable against FR-244's text. The engine compile still catches what is on the list but malformed (#967 item 1: "a construct can be on the list and still not compile") | decision point | yes — Task 2 | #970 (working id 9982), at `39dce368`: **(a)**, plus the lists-equal-FR-244 test |
| DP-G4 | Which code does a residual evaluation failure carry, and how is it told apart from a genuine miss? | Code: (a) a new `RATING_EVALUATION_FAILED`, added to `03` §5.1's catalogue with a one-line meaning (spec first) and to `RATING_ERROR_CODES`; (b) reuse `BUNDLE_COMPILE_FAILED` (a compile code, wrong for scoring); (c) reuse `INPUT_CONTRACT_VIOLATION` (an input-contract code; the input may be valid). Attribution: (i) read the `nodeId` the engine error carries (a JSON field, `runtime.py:89-90`). Report a table or lookup miss only when that node consumes an `on_miss="error"` table or lookup step's output; otherwise report the new code; (ii) report the new code for every engine failure, and drop the miss inference | **(a) with (i).** No existing code means "the engine failed evaluating an authored expression" (premise i), and FR-255 wants errors typed. (b) and (c) name a cause that did not happen, which is the defect being fixed. (i) keeps the genuine-miss path (acceptance 7), and it reads a structured field, not free text. (ii) would re-label a real table miss, which is the same class of error in reverse. *(The suffix-mapping contingency first written here is moot: #970's probe shows `nodeId` is the step id.)* | decision point | yes — Task 4 | #970 (working id 9982), at `39dce368`: **(a)+(i)**, with the stated residual, accepted by the maintainer at 11:07:11 BST |
| DP-G5 | Where do the two field registries and the enumerator live, and is `as_at` an expression field? | Placement: (a) a new `pricing_core/rating/authored.py`, next to the checks; (b) `model_schema.rating`, beside the step models, so a field author sees the registry. `as_at`: (i) non-expression, with the reason "names a date input; not wired to the engine (`runtime.py:26-35`)", and its registry comment says it moves to `EXPRESSION_FIELDS` when the window is wired; (ii) an expression field now | **(a) and (i).** (b) puts check policy in the shape package, and it edits `model_schema/__init__.py`, a file every shape slice touches. Closure 1's schema walk already makes a new field visible wherever it is added, without the registry sitting beside the model. For `as_at`: nothing evaluates it today (premise m), so checking it as an expression would refuse or accept a string no engine reads. (i) keeps the registry honest, and the comment carries the trigger for moving it | decision point | yes — Task 2 | #970 (working id 9982), at `39dce368`: **(a)** and **(i)** |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, cut
  from `main` **after** the fix slice (#963) merged.
- [ ] `uv sync --all-packages` (`dev-commands`).
- [ ] Re-derive premises a–o at that tree. Record each in the ledger. Re-read #968's
  *Exposure* list at its live head (acceptance 10).
- [ ] `gh pr list --state open`, and read anything that rules on FR-244, FR-274, FR-276,
  FR-255, `compile.py`'s checks, `??` or OQ working id 9905 ([`README.md`](README.md)
  convention 4). Name the SHA read. **Re-point #967, #968, #970 and the LOW finding to their ids if minted.**
- [ ] Confirm DP-G1, DP-G3, DP-G4 and DP-G5's resolutions, by record id, in the ledger. **Under DP-G1 (a),
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

### Task 2: The enumerator, the registries and the closure tests — red first

**Files:** Create `packages/pricing-core/src/pricing_core/rating/authored.py` (DP-G5 (a)) and
`packages/pricing-core/tests/test_rating_authored_fields.py`; modify
`packages/pricing-core/src/pricing_core/rating/compile.py`.

**Interfaces:**
- Produces, in `authored.py`:
  - `AuthoredString`, a frozen dataclass of `step_id: str`, `field: str` (for example `expr`,
    `condition`, `clamp_bounds.max`, `key_expr[0]`) and `text: str`;
  - `EXPRESSION_FIELDS: tuple[tuple[type, str], ...]`;
  - `NON_EXPRESSION_FIELDS: dict[tuple[type, str], str]`, each value a one-line reason;
  - `authored_expression_fields(algo: RatingAlgorithm) -> list[AuthoredString]`, in step order.
- Produces, in `compile.py`:
  - `STRING_CHECKS: tuple[Callable[[str], tuple[str, str] | None], ...]`;
  - `ALGORITHM_CHECKS: tuple[Callable[[RatingAlgorithm], list[ValidationIssue]], ...]`.

- [ ] **Red first:** closure 1 (acceptance 3b) and closure 2 (3c). Predicted red: the modules do
  not exist (`ImportError`) for 3b. For 3c, the four `_check_*` functions read `step.expr`
  directly (premise a), which the predicate reports. Also run each closure predicate on its
  planted broken input and quote the red.
- [ ] Write `authored.py` from premise m. The enumerator yields every value of `clamp_bounds`,
  not only `min` and `max`. Classify every field of premise m, with `as_at` per DP-G5.
- [ ] In `compile.py`, rewrite `_check_determinism`, `_check_division_guards`,
  `_check_scale_cap` and `_check_vocabulary` as one-string functions returning
  `(code, message) | None`. Keep each one's existing logic unchanged: this task moves them, it
  does not change what they catch. Register them in `STRING_CHECKS`, and `_check_result_types`
  in `ALGORITHM_CHECKS`. `validate_algorithm` builds `ValidationIssue(code, message,
  step_id=s.step_id, field=s.field)` for each `(check, s)`.
- [ ] Green for 3b and 3c. The matrix (3a) goes green for every field on the four existing
  checks, and stays red on the allow-list column. Every existing test in
  `test_rating_compile.py` and `test_rating_compile_bundle.py` passes unchanged. Acceptance 3's
  guard, determinism and scale rows, and acceptance 4 (D2, E3/E4), go green here.
- [ ] Commit: `fix(rating): one enumerator of authored expression fields, iterated by every check (WK-1178)`.

### Task 3: The allow-list and the dead markers — red first

**Files:** Create `packages/pricing-core/src/pricing_core/rating/vocabulary.py` (DP-G3 (a)) and
`packages/pricing-core/tests/test_rating_vocabulary.py`; modify `compile.py`; append to
`packages/pricing-core/tests/test_rating_compile.py`.

**Interfaces:**
- Produces: `check_allow_list(text: str) -> str | None` in `vocabulary.py`. It returns the first
  refused construct, or `None`.

- [ ] **Red first:** acceptance 1, 2 and 3's vocabulary rows (already red in 3a's allow-list
  column). Quote them.
- [ ] `vocabulary.py`: the ruled lists as tuples (#967 item 1): operators, literals, and the
  functions `min` and `max` (a single array-literal argument) and `abs`. **`round`, `floor`
  and `ceil` are not on it** (#967 at `6eb68d77`; the maintainer's 11:05:21 BST entry), so a
  call to any of them is refused like any other off-list function. Implement the tokenizer.
  Unit-test it against every ruled construct and every "Not on the list" construct
  (#967 item 1).
- [ ] **The lists equal FR-244's text, item for item** (#970, DP-G3). A test parses FR-244's
  amended cell in `docs/specs/03-rating-engine.md` (its "Operators:", "Literals:" and
  "Functions:" clauses, as #967 words them) and asserts that each tokenizer tuple equals the
  spec's set. **Broken-input proof:** with an operator added to the tuple and not to the text,
  the test fails. It needs the amended text on `main` (DP-G1 (a)); under the (b) fallback it
  reads this slice's own Task 1 text.
- [ ] Register the allow-list in `STRING_CHECKS`, ahead of the engine compile, as
  `EXPRESSION_INVALID_VOCABULARY`. The 3a matrix then goes green in its allow-list column with
  no change to the test.
- [ ] Remove `"?:"` and `"coalesce("` from `_GUARD_MARKERS`. Add the test that asserts `"??"` and
  `"!= null"` are absent (acceptance 5). Every existing guard test passes unchanged.
- [ ] Acceptance 10's committed-string test.
- [ ] Commit: `fix(rating): FR-244's allow-list enforced over every authored string; dead guard markers removed (WK-1178)`.

### Task 4: The residual evaluation code — red first

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/score.py`
(`_reraise_engine_failure`); `backend/src/app/errors.py` (`RATING_ERROR_CODES`); append to
`packages/pricing-core/tests/test_rating_score.py`.

- [ ] **Red first:** acceptance 6, on hand-built bundles (the route #963's plan (working id 9873), acceptance 5a,
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
  - the tree and premises a–o;
  - the red quotes;
  - #968's pre-fix rows and the executor's own scratch run of D2 and E4;
  - the DP resolutions by record id;
  - acceptance 9's outcome;
  - acceptance 10's count and pattern, and #968's committed-exposure list as re-read;
  - the matrix's size (checks × fields), and the two closure reds on planted input.
- [ ] Item 11 (acceptance 14).

## Hand-off

WK-1250 Slice 1 is dispatched after this slice merges (the maintainer's order).

## Self-review

- **#967, clause by clause:**
  - item 1, the allow-list, every authored string, the generated strings outside it →
    acceptance 1–3, Task 2, Global Constraints;
  - item 2, `??` documented, never a guard, dead markers removed → acceptance 5, Task 3;
  - no rounding function (the maintainer's 11:05:21 BST acceptance) → acceptance 1, Task 3;
  - item 3, the compile and the guard widened → acceptance 3, Tasks 2–3;
  - *Acceptance* → acceptance 1, 2, 3, 5 and 10;
  - *Which slice carries it* → Status, and DP-G1.
- **The structural fix** (the maintainer's 10:55:40 BST entry, and #968's *Disposition*):
  - one enumerator → Architecture, Task 2;
  - the matrix → acceptance 3a;
  - a new field, or a new check, failing a test → acceptance 3b and 3c, each with a
    broken-input proof.
- **#968, clause by clause:**
  - D2 and E4 refused at save → acceptance 4;
  - every table row returns an issue → acceptance 3 and 3a;
  - committed exposure → acceptance 10, from #968's list;
  - F1–F3 of auditor-933's audit at `dee9ff9d` → acceptance 3a–3c (matrix, closures), 3b (`as_at`), 10 (exposure, negative fixtures, data-prep strings out);
  - the misleading `RATE_TABLE_MISS` → acceptance 6 and 7, DP-G4;
  - `key_expr` unmeasured → acceptance 3's added row.
- **The lead's scope list:** 1 → Tasks 2–3; 2 → Task 3; 3 → acceptance 3 and 4; 4 → DP-G4,
  Task 4; 5 → acceptance 11; 6 → DP-G1 and Dependencies.
- **Literals** were read at the tree above (premises) or quoted from #967 and #968 at the heads
  named. `authored.py`, `AuthoredString`, `EXPRESSION_FIELDS`, `NON_EXPRESSION_FIELDS`,
  `authored_expression_fields`, `STRING_CHECKS`, `ALGORITHM_CHECKS`, `check_allow_list`,
  `vocabulary.py` and `RATING_EVALUATION_FAILED` are proposals, named once each and used consistently.
- **Ruled:** DP-G1, DP-G3, DP-G4 and DP-G5, by #970 (working id 9982), unminted (DP-G2 withdrawn). #967 and #968 unminted. The fix slice
  unmerged.
