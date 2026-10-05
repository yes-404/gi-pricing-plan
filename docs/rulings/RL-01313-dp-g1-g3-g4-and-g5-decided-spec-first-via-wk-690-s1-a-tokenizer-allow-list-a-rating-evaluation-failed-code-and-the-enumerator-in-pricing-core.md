---
id: RL-1313
family: ruling
title: DP-G1, G3, G4 and G5 decided — spec first via WK-690 S1, a tokenizer allow-list, a RATING_EVALUATION_FAILED code, and the enumerator in pricing-core
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1263, RL-1265]
---

# RL-1313 — DP-G1, G3, G4 and G5 decided: (a), (a), (a)+(i), (a)+(i)

## How this was ruled

- **Effort.** Ruled at effort `medium`, on the lead's routing of 2026-09-30 about 11:00 BST.
  The session's `$CLAUDE_EFFORT` read `medium`.
- **The maintainer's entries relied on.** Each is cited by its header time in
  `~/gi-pricing-plan.local/channel/to-lead.md`, read at 11:01 BST:
  - "2026-09-30 10:27:10 BST — DECISION: PL-1295 Task 6's FR-244 sentence is held (option a)";
  - "2026-09-30 10:53:10 BST — DECISION: condition/clamp FD (B) — HIGH on independent
    reproduction; owner and order";
  - "2026-09-30 10:55:40 BST — … #968 widened, so fix the CLASS structurally";
  - "2026-09-30 10:57:06 BST — #968 HIGH in force";
  - "2026-09-30 11:05:21 BST — DECISION: I accept #967's departure; it supersedes the rounding
    part of my 10:46:20 (A)": `round`, `floor` and `ceil` are not on P2's allow-list.
- **Minted 2026-09-30 as RL-1313** (hand-assigned in the lead's batch plan, batch 4, under the
  maintainer's option (B)); it was filed under working id 9982.
- **Sources.** The decision points belong to the WK-1178 leaf plan `PL-1314` (#969, working id 9833). I
  first read it at `dee9ff9d` (`:307-310`), and this record rules its DP table at head
  `1cbcf474` (`:387-391`). There, DP-G2 is withdrawn and DP-G5 is added. They implement the
  ruling `RL-1312` (#967, working id 9904, first read at `1efa639d`, then at `6eb68d77`) and discharge the finding #968 (FD working id 9885, HIGH, head `fede7e5d`).
  `PL-1314` and `RL-1312` mint in the same batch as this record. #968 is not yet minted, so it
  is cited in prose.

## Verified first, at 9f63d0feee524815e7e0c68c99a53ac3f80e6c37

Each row was read with `git show 9f63d0fe:<path>`. `compile.py` means
`packages/pricing-core/src/pricing_core/rating/compile.py`, and `runtime.py` and `score.py`
are in the same directory.

| Premise (plan's letter) | Where | Present? | What the source says |
|---|---|---|---|
| (a) The four checks read only `expr` | `compile.py:146`, `:176`, `:200`, `:242` | present | Each check has `if not isinstance(step, RatingExpressionStep): continue` |
| (b) `_GUARD_MARKERS` is a substring list | `compile.py:41` | present | `("!= 0", "> 0", "== 0", "< 0", "?:", "coalesce(", "if(", "guard")` |
| (c) Vocabulary is the engine compile only | `compile.py:233-257` | present | `zen.compile_expression(step.expr)` gives `EXPRESSION_INVALID_VOCABULARY` |
| (e) Condition and bounds are strings | `packages/model-schema/src/model_schema/rating.py:312-322` | present | `condition: str`; `clamp_bounds: dict[str, str] \| None` |
| (f) Tables and lookups carry `key_expr` | `rating.py:275-288` | present | `key_expr: list[str]` on both |
| (g) Condition and clamp wiring | `runtime.py:288-316` | present | `{"id": f"{step_id}_v", …, "value": f"!({condition})"}` and `{"id": f"{step_id}_c", …}` |
| (h) Miss inferred from any `on_miss="error"` step | `score.py:469-498`; called at `:802` and `:952` | present | Otherwise `raise exc`, a bare `RuntimeError` |
| (i) No evaluation-failure code | `backend/src/app/errors.py:286-365`, `03:772-782` | **absent** | `grep -i evaluat` over those lines printed nothing (rc 1) |
| (k) The raise-site census counts it | `packages/pricing-core/tests/test_quote_input_raise_sites.py:66` | present | `("rating/score.py", "_reraise_engine_failure"): 1` |
| (l) FR-244 still points at `02` §4.6 | `03:146` | present | "the same restricted grammar as `02` §4.6" |
| An allow-list module exists | `packages/pricing-core/src/pricing_core/rating/` | **absent** | `git ls-tree 9f63d0fe …/rating/ \| grep -c vocabulary` printed 0 |
| WK-690 Slice 1's Task 6 is on `main` | `03:146` | **absent** | FR-244 still reads as in (l); Slice 1 is dispatched and running |
| #967 excludes the data parser | #967's record, "The amended FR-244 text" | present | "`pricing_core.data.expressions` never parses it" |

## Probe — what the engine reports when an authored string fails at evaluation

**Where it ran.**
- File: scratch `probe_nodeid.py` (sha256 prefix `ee00d2f35099de94`), in
  `/home/puzhenhao1989/.claude/jobs/0081b83b/dm-g-proofs/`. It is not committed.
- Tree: a worktree whose `packages/` equals `9f63d0fe`
  (`git diff --quiet 48792023 origin/main -- packages` → rc 0), after `uv sync --all-packages`.
- Code under test: the real `compile_bundle`, `load_bundle` and `score_one` on the score
  fixture (`packages/pricing-core/tests/test_rating_score.py`). The fixture has an
  `on_miss="error"` table, `s_expense`, which produces `expense_factor`.

**Cases.** Each makes a null by dividing by zero, then uses it:
- **EXPR:** `s_office`'s `expr`, satisfying today's guard with a `!= 0` substring.
- **COND:** `s_decl_cap`'s condition.
- **CLAMP:** `s_clamp`'s `min` bound.
- **MISS:** a genuine miss, with the fixture table's `direct` row removed.

| Case | `score_one` raised | The engine's error |
|---|---|---|
| EXPR | `CodedError RATE_TABLE_MISS: …` | `{"type":"NodeError","source":"Failed to evaluate expression: \"risk_premium_minor * expense_factor * (1 / (expense_factor - expense_factor)) + …\"","nodeId":"s_office"}` |
| COND | `CodedError RATE_TABLE_MISS: …` | `{"type":"NodeError","source":"Failed to evaluate expression: \"!(office_premium_minor + (1 / …) * 2 <= sanity_cap_minor)\"","nodeId":"s_decl_cap"}` |
| CLAMP | `CodedError RATE_TABLE_MISS: …` | `{"type":"NodeError","source":"Failed to evaluate expression: \"(office_premium_minor < (min_premium_minor + (1 / …) * 2) ? … )\"","nodeId":"s_clamp"}` |
| MISS (genuine) | `CodedError RATE_TABLE_MISS: …` | `{"type":"NodeError","source":"Failed to evaluate expression: \"risk_premium_minor * expense_factor\"","nodeId":"s_office"}` |

What this shows:
1. **`nodeId` is the step id itself**. auditor-933 got the same for an unguarded decline condition, independently (`"nodeId":"s_decl_cap"`, relayed by the lead). The clamp bound, which the relay calls untested, is covered here (`s_clamp`) (`s_office`, `s_decl_cap`, `s_clamp`), for an
   expression step, a condition and a clamp bound alike. It is not the entry ids `<step>_v`
   or `<step>_c`, so **no suffix mapping is needed**. The executor still re-proves this on
   its red run.
2. Today, **all four** cases raise `RATE_TABLE_MISS`. Three of them are not misses. This is
   #968's misleading-code defect, reproduced.
3. **The engine's error has the same shape** for a genuine miss (MISS) and for a non-miss
   failure (EXPR) in **the same consuming step**, `s_office`. Only the free-text expression
   differs. So attribution by `nodeId` cannot separate those two when the failing step itself
   directly consumes an `on_miss="error"` output. See DP-G4.

## Ruled

**DP-G1 — (a), with (b) as the fallback.**
- **(a):** this slice's dispatch waits until WK-690 Slice 1's Task 6 commit, carrying #967's
  amended FR-244 text, is on `main`. The code then lands against its spec. There is one
  writer per spec row, and PL-1295 is not changed.
- **(b), the fallback:** if the fix slice (#963) merges and Slice 1's Task 6 is not yet on
  `main`, the lead may take (b). This slice then carries #967's FR-244 sentence, spec first,
  and a dated dispatch-record delta re-scopes Slice 1's Task 6 to the `02` §4.6 note only.
  - The fallback is valid only before Slice 1's executor reaches Task 6.
  - **(b)'s authority is the lead's dated dispatch-record delta, not the maintainer's
    10:27:10 entry directly.** That entry provides only for Slice 1 reaching its close first
    (the held sentence "is carried to the ruling's implementing slice by name"). The (b) case
    here is this slice being dispatched before Slice 1's executor reaches Task 6. That is
    reasoned from 10:27:10, not provided by it, and it takes effect only through the lead's
    delta. The maintainer accepted G1 in that form at 11:07:11 ("G1 (a), with the (b)
    fallback only before S1 reaches Task 6 via a dated dispatch delta").
- **(c) is refused.** Code ahead of its spec is what `CLAUDE.md` §0 forbids.

**DP-G2 — withdrawn from the plan at `1cbcf474`, and not ruled here.** The maintainer
decided it at 10:55:40, as option (a). The plan keeps the row so that its id is not reused.
The decision is recorded here only because DP-G5 builds on it:
"**one enumerator** of every authored expression field … which **every** expression check
iterates; a **matrix test** … **Adding a new expression field without the enumerator, or a
new check that bypasses it, must fail a test.**"
- All four checks iterate the enumerator: `_check_determinism`, `_check_division_guards`,
  `_check_scale_cap` and `_check_vocabulary`.
- The enumerator yields `(step_id, field, string)` for `expr`, `condition`, each
  `clamp_bounds` value and each `key_expr` item.
- (b) would leave #968 open against its own acceptance.

**DP-G3 — (a).** The allow-list lives in a new module, `pricing_core/rating/vocabulary.py`.
- It is a small tokenizer, with the ruled lists held as data (one tuple per class). It runs
  before FR-276's engine compile, which still runs.
- (b) is excluded by #967 ("`pricing_core.data.expressions` never parses it").
- (c) cannot tell `a.b` from `1.5`, or `min([…])`'s bracket from indexing.
- The tokenizer's lists must equal #967's amended FR-244 text item for item. The slice
  carries a test comparing them, so the code's list is checkable against the spec's. At #967's
  head `6eb68d77` (`:150-172`, `:237-238`), and by the maintainer's 11:05:21 entry, the
  functions are `min([…])`, `max([…])` and `abs`. **`round`, `floor` and `ceil` are off the
  list** and are refused at save.

**DP-G4 — (a)+(i), with a stated limit.**
- **The code:** a new `RATING_EVALUATION_FAILED`.
  - It is added spec first to `03` §5.1's catalogue (`03:772-782`), with a one-line meaning:
    the engine failed evaluating an authored rating string, for a reason other than an
    `on_miss="error"` miss.
  - It is added to `RATING_ERROR_CODES` (`errors.py`).
  - (b) `BUNDLE_COMPILE_FAILED` and (c) `INPUT_CONTRACT_VIOLATION` each name a cause that
    did not happen.
- **Attribution (i):** `_reraise_engine_failure` parses the engine error's JSON and reads
  `nodeId`. It reports `RATE_TABLE_MISS` or `REFERENCE_LOOKUP_MISS` only when that step
  directly consumes the output of an `on_miss="error"` `table` or `lookup` step. Otherwise it
  reports `RATING_EVALUATION_FAILED`.
  - The bare `raise exc` fallthrough at `score.py:498` also becomes `RATING_EVALUATION_FAILED`,
    as FR-255 wants typed errors.
  - A `nodeId` that is missing or not parseable also takes the new code.
  - `test_quote_input_raise_sites.py:66`'s census is updated to match.
- **(ii) is rejected.** It would re-label every genuine miss, which is the same error in
  reverse.
- **The stated limit (probe, point 3).** When the failing step itself directly consumes an
  `on_miss="error"` output and fails for another reason, (i) still reports the miss code. The
  engine gives nothing structured to tell the two apart.
  - It is a wrong diagnosis on a refused quote, never a silent price: both paths raise.
  - It narrows #968's acceptance line ("any residual runtime evaluation failure in a
    condition or bound raises its own evaluation code, never `RATE_TABLE_MISS`") to:
    **every condition or bound whose step does not directly consume an `on_miss="error"`
    output.** This covers every row in #968's reproduction table, because those constraints
    consume `office_premium_minor`, not a table's output.
  - Closing the residual needs the wire-level change that `score.py:469-483`'s docstring
    already names ("making the wire translation itself fail gracefully"). That is outside this
    slice.
  - **Accepted by the maintainer** at "2026-09-30 11:07:11 BST — DECISION: #970 DP-G4
    residual → (a), recorded as a LOW FD; #970 G1–G3 accepted". It is fail-closed either way,
    and every #968 reproduction row is covered. #968's line is narrowed by a dated note, and
    the residual is recorded as a LOW finding (owner WK-1178), filed by auditor-928.

**DP-G5 — (a) and (i).**
- **Placement (a).** The enumerator and its two field registries (expression fields and
  non-expression string fields) live in a new `pricing_core/rating/authored.py`, next to the
  checks that iterate it.
  - (b) would put check policy into the shape package, and it would edit
    `model_schema/__init__.py` (712 lines at `9f63d0fe`), a file every shape slice touches.
  - The closure test walks the step schemas, so a new field is caught wherever it is added. It
    does not need the registry to sit beside the model.
- **`as_at` (i): a non-expression field.** It is `RatingLookupStep.as_at: str`
  (`packages/model-schema/src/model_schema/rating.py:279`).
  - `git grep -n as_at 9f63d0fe -- packages/pricing-core/src/pricing_core/rating` finds it
    only in `runtime.py`'s module docstring (`:26-35`): the effective-dating window is "an
    exact key match only", and no code evaluates it.
  - Its committed values are column names such as `"effective_date"` and `"postcode"`
    (`packages/pricing-core/tests/test_rating_compile.py:37` and
    `test_rating_runtime.py:445`), not expressions.
  - Checking it as an expression would refuse or accept a string that no engine reads.
  - Its registry entry carries the stated trigger: it moves to the expression fields when the
    window is wired to the engine.
  - The closure test still forces every string field into one registry or the other, so
    `as_at` cannot drift out of both.

**Departures from the recommendations.**
- DP-G1 (a), DP-G3 (a) and DP-G5 (a)+(i) are **as recommended**. DP-G2 is withdrawn.
- DP-G4 (a)+(i) is as recommended, **with one addition**: the stated limit above narrows
  #968's "never `RATE_TABLE_MISS`" line to the steps (i) can separate. This is reported for
  the maintainer.
- The plan's "strip the `_v`/`_c` suffix" contingency is moot: `nodeId` is the step id.

**Not touched.** `??`'s semantics, the allow-list's contents and the dead markers are #967's
and are not reopened here.

**Narrowness: narrow.**
- One code is added to the `03` §5.1 catalogue and to `RATING_ERROR_CODES`, spec first, as
  the plan's Task 1 already scopes.
- FR-244's text is #967's.
- No schema or route changes.

## What it obliges

The WK-1178 code slice (#969's plan):
- **Dispatch:** gated by DP-G1.
- **Tasks 2 and 3:** DP-G3 and DP-G5 as ruled, and the maintainer's DP-G2 decision. The enumerator, the matrix test and the closure
  tests follow the maintainer's 10:55:40 wording.
- **Tasks 1 and 4:** DP-G4 as ruled, with the stated limit recorded in
  `_reraise_engine_failure`'s docstring. A test pins the limit's behaviour, so any change to it
  is visible.

This commit edits no spec, plan or roadmap text.

## Acceptance — the violation that must become detectable

Each is shown red first in the slice's own suite.
- *Violation: a condition or clamp bound with an unguarded division, a `??`-only "guard", a
  `now()`, an over-scale literal, or a construct off the allow-list is accepted at save.* This
  is the matrix: each check against each field.
- *Violation: a new authored-string field, or a new expression check that does not use the
  enumerator, passes the closure tests.*
- *Violation: the tokenizer's lists differ from FR-244's text.*
- *Violation: COND or CLAMP above* (a residual failure in a step that does not consume a miss
  output) *raises `RATE_TABLE_MISS`.* It must raise `RATING_EVALUATION_FAILED`.
- *Violation: MISS above* (a genuine miss) *raises anything but `RATE_TABLE_MISS`.*
- *Violation: an engine failure escapes `score_one` as a bare `RuntimeError`.*
