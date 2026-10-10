---
id: PL-9955
family: plan
kind: map
title: WK-1178 — FD-1589 row 8, remedy (c): an input-free marker for authored model-schema validator messages, all 253 adopted and the 157 interpolating messages rewritten input-free, allow-listed by pricing_core.safe_error, so the request-validation 422 keeps authored guidance and drops anything else: single-row Work plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-10            # working id; the mint date will replace this (check 31)
owner: planner
tree: fe0b0627590307259ec6d56be7f73115cf245092
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1589, PL-1535, SL-1536, SL-1340, SL-1557, SL-1559]
---

# PL 9955 (working id) — WK-1178: FD-1589 row 8, remedy (c), single-row Work plan

> **For agentic workers:** this is a **single-row WK-1178 Work plan** under Lean P2 L5, in the
> form of `PL-1535` and `PL-1574`: WK-1178 has no map plan, so this is one row, the slice
> SL 9956 (working id), cut on this file's branch. Its `LG-` quotes the row as its scope.
> **If the lead takes DP-9's split, SL 9956 is slice A and the further rows are cut under ids
> the lead reserves** (§"Size and the split"). REQUIRED SUB-SKILL for the executor:
> subagent-driven-development (recommended) or executing-plans. The executor also binds
> `python-test` (the `req` marker, broken-input proofs), `test-driven-development` (every red
> seen first, by its cause), `python-package` (the import-linter layers), `dev-commands` (the
> gate slot wrapper, the two-half gate, `uv sync --all-packages` in a fresh worktree),
> `spec-change` (Task 6's one dated paragraph) and `git-hygiene`; reads
> [`README.md`](README.md)'s five unchecked conventions; and is spawned from
> `.claude/roles/executor.md`.

*Disclosure: drafted under working ids 9955 (this plan) and 9956 (its slice row), both reserved
by the lead in `~/gi-pricing-plan.local/handover/brief-planner-remedy-c-2026-10-10.md`. The
brief asks for "a LEAF PLAN"; this file is `kind: map`, a single-row Work plan, because
`document-ids.md` §1.6's PL row reads "from Lean P2 L5 **one plan per Work**, slices as rows,
no per-slice `leaf`", and WK-1178's recent fresh drafts (`PL-1535`, `PL-1574`) take that form.
The lead accepted `kind: map` (premise note (1) of the entry "2026-10-10 15:51:57 BST — Lead: DP
REQUEST — PL 9955 / SL 9956 …" in `from-lead-2026-10-09.md`).*

Written by the planner (`planner-remedy-c`) on 2026-10-10 from 15:46:41 BST; **amended in place
(still a draft, not merged) by the planner `planner-remedy-c2` on 2026-10-10 from 15:59:03 BST**
(`TZ=Europe/London date`) to the lead's rulings of 15:52:31 BST: DP-1 to DP-7 recorded as
ruled, DP-2 (c) planned (all 157 interpolating messages rewritten input-free, all 253 adopt the
marker), the slice re-sized, the parked row-8 tests cited, and two new decision points (DP-8,
DP-9) brought to the lead. Evidence read at `origin/main`
`fe0b0627590307259ec6d56be7f73115cf245092` (#1265, 2026-10-10T14:39:26+01:00; `origin/main`
still there at 15:59 BST) unless a line names another commit. **No test, check or gate was run
at planning time.** The amendment's counts come from three read-only Python AST passes over the
tree, run once each under `nice -n 19` (sub-second, not a check), whose predicates are stated in
words at each count below; the scripts were scratch files, so the executor re-derives every
number at its base (Task 0) from the guard's own census.

**Draft, not frozen.** DP-1 to DP-7 are **ruled** (§"Decision points"). **DP-8** (the graph
signals) and **DP-9** (the split, because the honest size exceeds ~2 lane-days) are open for the
lead; the tasks are written against the recommendation of each, and say where another option
changes them.

## Authority

- `to-lead.md` "2026-10-10 15:52:31 BST — RULINGS on PL 9955 / SL 9956 (FD-1589 row 8 remedy
  (c), draft/pl-remedy-c @a8e465be): DP-1 (a), DP-2 (c), DP-3 (a), DP-4 (a), DP-5 (b), DP-6
  (a), DP-7 (a); the dict-KEY echo FD row YES". Quoted per DP in §"Decision points".
- `to-lead.md` "2026-10-10 15:37:31 BST — RULING: DP-M2 WITHDRAWN (my 14:37:13). FD-1589 row 8
  (errors.py:490) is NOT changed in the FD-1374 slice; remedy (c) in its own slice, owner
  WK-1178, before the exit demo. Neither (a) nor (b)", item 2, verbatim: *"Remedy (c), in its
  OWN slice (owner WK-1178), planned now and built before the exit demo if the lanes allow: an
  input-free marker exception in model-schema (an authored-message ValueError subclass carrying
  no input value), adopted by the authored validators, and allow-listed in
  pricing_core.safe_error; then row 8 renders authored messages and drops anything else. It
  needs a plan (one planner seat) and its DPs come to me."* Item 1: *"The red-first test written
  for row 8 is removed or parked on a draft/ branch for the remedy slice."* Item 3: FD-1589 row
  8's interim line is *"remedy (c), its own slice; interim: unchanged (requester-only
  exposure)"*.
- The lead's entry "2026-10-10 15:51:57 BST — Lead: DP REQUEST — PL 9955 / SL 9956 …" in
  `from-lead-2026-10-09.md`, premise note (3): *"The planner reported draft/fd1589-row8-tests
  "does not exist" — WRONG: lead verified origin has it @cfe8e15f03171ed54bdee6e27bb783a6cc83bfbc
  (the FD-1374 seat pushed it after the planner looked); the plan will be corrected pre-merge to
  cite it."*
- `to-lead.md` "2026-10-10 09:42:06 BST — FD 9952 (11 ValidationError sinks) ACCEPTED", item 2:
  rows 2–11 owner WK-1178, discharged before WK-1178's Work close.
- `to-lead.md` "2026-10-10 10:14:29 BST — Premise correction CONFIRMED", the
  `safe_error_detail(exc) or type(exc).__name__` form: a sink that partitions a code must never
  use `safe_error_text`.
- [`FD-1589`](../findings/FD-01589-validationerror-text-reaches-sinks-not-built-through-safe-error-and-a-platformerror-detail-is-persisted-by-the-worker-unsanitised.md)
  row 8 (`:78`): *"`FieldError(message=str(err["msg"]))`; `input` is never read, but a
  `value_error` `msg` carries whatever a custom validator interpolated"*, LOW.

## Goal

A request-validation 422 (`backend/src/app/errors.py` `_handle_validation_error`) shows a
validator's message only when that message is input-free by construction, and shows
`The value is not valid (<TYPE>).` otherwise (DP-7 (a)). "Input-free by construction" is a
class: `InputFreeError`, a `ValueError` subclass in `model_schema/input_free.py` (DP-1 (a)),
whose every raise site is a string literal or an f-string over upper-case module constants
alone, held so by an AST guard. **Every** `raise ValueError` in `packages/model-schema/src` (253
at `fe0b0627`) adopts it (DP-2 (c)): the 96 input-free messages unchanged, the 157 interpolating
ones **rewritten to input-free authored text that keeps the guidance — naming the FIELD and the
RULE, never the submitted VALUE**. So an actuary still reads (for example) *"a Poisson model must
declare an offset (FR-111 …)"* byte for byte as on `main` (DP-4 (a)), and reads the rule instead
of a fixed text for every rewritten message. The same allow-list function is read by
`pricing_core.safe_error._validation_detail` (DP-5 (b)), so a stored sink and the 422 cannot
disagree. The rule is one dated paragraph in `00-overview.md` §5.3 (DP-6 (a)).

## What the code says today (at `fe0b0627`)

1. **The 422 sink.** `errors.py:485-510` `_handle_validation_error` builds one `FieldError` per
   `exc.errors()` entry; the message is `message=str(err["msg"])` at `:499`, the field the loc
   joined after its first part (`:497`), the code `str(err["type"]).upper()` (`:498`).
2. **What `err` carries for a validator's `ValueError`.** FastAPI 0.142.2 (`uv.lock:530-531`)
   collects `exc.errors(include_url=False)` (`.venv/…/fastapi/_compat/v2.py:187`), so
   `include_context` keeps its default `True`: the error's `type` is `"value_error"`, its `msg`
   is pydantic's `"Value error, " + str(exc)`, and its `ctx["error"]` is the exception
   **instance**. A `ValueError` subclass is reported the same way, by `isinstance`: the repo
   already relies on it (`model_schema/graph_errors.py:1-6` docstring; consumers
   `backend/src/app/platform/rating_algorithms.py:63`, `:70`). The frontend mock pins the prefix:
   `frontend/src/views/__tests__/ModelSpecBuilderView.test.ts:167`
   `message: "Value error, a Poisson model must declare an offset (FR-111)."`; the view renders
   the message as given (`ModelSpecBuilderView.vue:626` `{{ error.message }}`).
3. **The allow-list.** `packages/pricing-core/src/pricing_core/safe_error.py`: `CodedError(ValueError)`
   (`:64-70`), text `CODE: message`; `_FIXED_TEXT_TYPES` (`:50-58`, 30 types); `_validation_detail`
   (`:104-116`) keeps a `msg` only for a type in `_FIXED_TEXT_TYPES` (`:113-114`), so a
   `value_error` keeps its type alone (module docstring `:22-23`); `safe_error_detail` (`:119-125`)
   keeps a `ValidationError` via `_validation_detail` and a `CodedError` as `str(exc)`;
   `safe_error_text` (`:128-134`) prefixes the type name.
4. **The import boundary.** `.importlinter:53-59` `layers = app / pricing_core / model_schema`, and
   `:36-51` forbids `model_schema` from importing `pricing_core` (`:49`). So the marker must live
   in `model_schema`, and `pricing_core.safe_error` may import it; `pricing-core` already
   declares `model-schema` (`packages/pricing-core/pyproject.toml:8`) and imports
   `model_schema.graph_errors` (`pricing_core/rating/inline.py:34`, `rating/runtime.py:50`).
   That is why a `CodedError` cannot be the marker: 0 model-schema raises can reach it.
5. **The parked row-8 tests — the starting point.** *(Corrected 2026-10-10 by
   `planner-remedy-c2`: the first draft said this branch did not exist; it was pushed after that
   look, premise note (3) above.)* `origin/draft/fd1589-row8-tests` @
   `cfe8e15f03171ed54bdee6e27bb783a6cc83bfbc` (`git ls-remote origin draft/fd1589-row8-tests`,
   15:5x BST) is two commits on `fe0b0627`: `cb9b1788` (2026-10-10T13:44:22Z, the first DP-M2
   form) and `cfe8e15f` (2026-10-10T14:36:15Z, the `safe_error_detail` form);
   `git diff --stat fe0b0627 cfe8e15f` = `backend/src/app/errors.py` +28/−3 and
   `backend/tests/test_error_sinks.py` +51/−1. **Take the tests, not the `errors.py` hunks** (that
   is the withdrawn implementation): `_SentinelBody` with its `_refuse_with_the_value` validator,
   `test_a_request_validation_422_carries_no_submitted_value` (DB-backed through `api_client`,
   adds a route `/__nfr499_422`) and `test_a_coded_validator_message_survives_the_422_sink`
   (`/__nfr499_coded`, a `CodedError` from `pricing_core.safe_error`). Under DP-3 (a) and DP-5
   (b) the second test's premise changes: a `CodedError` is **not** on the 422 allow-list
   (`safe_validation_message` keeps a fixed-text type or an `InputFreeError`, Task 3), and
   model-schema validators cannot raise it (item 4). Task 4 therefore keeps the first test as is
   and retargets the second to `InputFreeError` (`"an authored, input-free message"` survives),
   with a third asserting a `CodedError` raised in a request validator renders the fixed text —
   recorded in the LG as a deliberate change from the parked test.

### The population (at `fe0b0627`)

- **253** `raise ValueError` lines in `packages/model-schema/src`:
  `git grep -c 'raise ValueError' -- packages/model-schema/src` (summed over 24 files).
- An AST walk agrees: **253** `ast.Raise` nodes whose `exc` is `ast.Call` with
  `func == ast.Name('ValueError')`, over `packages/model-schema/src/model_schema/*.py`
  (re-run by `planner-remedy-c2`, same count). Of these:
  - **95** take a plain string literal (`isinstance(args[0], ast.Constant)` and `str`);
  - **158** take an f-string (`isinstance(args[0], ast.JoinedStr)`); none uses `.format`, `%` or a
    name. Of the 158, **1** interpolates only an upper-case module constant
    (`modelling.py:1142`, `{SURROGATE_RESPONSE_COLUMN!r}`; predicate: every `ast.Name` inside each
    `FormattedValue` matches `_?[A-Z][A-Z0-9_]*`); **157** interpolate a runtime value.
  - Of the 157, **15 closed-vocabulary** (every `FormattedValue` is `len(...)` or an attribute
    named `value`, i.e. an enum member's value): `diagnostics.py:195 :648`,
    `jobs.py:142 :263 :265`, `metrics.py:189 :208`, `modelling.py:873 :920 :1719 :1844`,
    `objectives.py:806`, `perils.py:425`, `profiles.py:72 :79`. **142 free-value** (a slug, a
    ref, a number, a step id, a column).
  - By enclosing function: **231** sit in a function decorated with a pydantic validator (any
    decorator whose source contains `validator`): 95 literal, 1 constant-only, 15 closed, 120
    free; **22** sit in helper functions, all free (`ids.py`, `money.py`, `refs.py`
    `ArtifactRef.parse`, `objectives.py` `TemplateParameter.check` and `battery_is_exactly`,
    `rating.py` `check_model_reference_mode` and `_reject_float_type`, `permissions.py`,
    `validation.py`, `modelling.py` `Factor._the_interaction_arm`, `Factor._columns_match_the_type`).
    Of the helpers, `money.py:83` `_reject_float` is a `BeforeValidator` (`money.py:95 :108
    :117`) and `rating.py:302` `_reject_float_type` an `AfterValidator` (`rating.py:310`), so both
    reach request bodies through their annotated types.
- **Input-free by AST: 96 = 95 literal + 1 constant-only.** All 96 are inside validators. They
  are in 17 files: `approvals.py` 4, `audit.py` 1, `datasets.py` 5, `diagnostics.py` 2,
  `dislocation.py` 8, `jobs.py` 2, `metrics.py` 1, `modelling.py` 33 (32 + `:1142`),
  `objectives.py` 4, `perils.py` 4, `prediction.py` 3, `profiles.py` 1, `rating.py` 11,
  `regression.py` 9, `scoring.py` 1, `sub_graphs.py` 5, `transparency.py` 2.
- **Other raise paths in model-schema** (every `ast.Raise` in the same files, 260 in all): the
  typed graph signals `GraphUnresolvedRefError` ×3 (`rating.py:575`, `sub_graphs.py:82 :91`, all
  three interpolating a step id or a value name) and `GraphCycleError` ×2 (`rating.py:596`,
  `sub_graphs.py:151`, literals) — `ValueError` subclasses, so in a validator they render as
  `value_error` and, not being `InputFreeError`s, would get the fixed text under DP-5 (b)
  (**DP-8**); `TypeError` ×1 (`money.py:151`, `apply_factor`) and `AttributeError` ×1
  (`money.py:157`, `__getattr__`), neither in a validator and neither converted by pydantic into
  a validation error, so outside acceptance (i). Model-schema raises **0** `PydanticCustomError`
  and has **0** `assert` statements (`git grep -nE 'PydanticCustomError|^\s*assert ' --
  packages/model-schema/src`).
- Outside model-schema, validators that raise `ValueError`: `backend/src/app` **1**
  (`config.py:198`, `Settings`, not a request model); `pricing_core` **0**.

### Where each of the 157 can be read (the measure behind the split)

- **422-reachable** (predicate: the enclosing class is in the `$ref` closure of some operation's
  `requestBody` in `docs/contracts/openapi/generated.json`, `-Input`/`-Output` suffixes
  stripped; plus every module-level helper, since two of them are annotated-type validators and
  a helper's callers are not tracked by this predicate): **2 closed + 54 free** — the free are
  45 by the closure and 9 module-level helpers (`ids.py` 2, `money.py` 2, `permissions.py` 1,
  `rating.py` 2, `validation.py` 1, `objectives.py` `battery_is_exactly` 1). The other 13 closed
  sit in system-produced models; slice A takes all 15. Of the free, **32** are reachable from
  an operation the UI posts to (`frontend/src/api/*.ts` calls with `method: "POST"` or `"PUT"`:
  `/model-specs/validate`, `/factors`, `/bandings` (+`/evaluate`, `/propose`), `/groupings`
  (+`/evaluate`, `/propose`), `/rating-algorithms`, `/validation-rules` (+`/dry-run`, `/submit`,
  `/approve`), `/datasets/{slug}/rule-set`, `/datasets/{slug}/dictionary`, `/models/compare`,
  `/models/{model_id}/predict`, `/me/workspace`, the acknowledge route): `Banding` 4,
  `Grouping` 5, `OffsetSpec` 1, `SplitRef` 1, `LossTreatment` 1, `GlmCvSpec` 1,
  `TweediePowerSpec` 1, `GlmSpec` 3, `GbmSpec` 2, `EbmSpec` 4 (all `modelling.py`, through
  `/model-specs/validate`, `/bandings`, `/groupings`), `RatingModelCallStep` 1 and `ArtifactRef` 8
  (through `/rating-algorithms`).
- **Not 422-reachable but user-authored** (B1, 41 free): the class is built inside a handler
  from a create body, so its refusal reaches a client through an in-handler `ValidationError`
  sink — FD-1589 rows 2–11, which read `_validation_detail` once remedied: `Factor` 10,
  `CustomObjective` 10, `TemplateParameter` 4, `CustomMetric` 3, `PerilStructure` 3,
  `RatingAlgorithm` 3, `SubGraphBody` 3, `DatasetSplit`, `Reconciliation`,
  `RegressionSuiteContent`, `ValidationRule`, `RuleSetEntry` 1 each.
- **Not 422-reachable, system-produced** (B2, 47 free): fit results, diagnostics, comparisons,
  predictions, jobs, backtests, approvals' recorded decisions (`EbmFitResult` 8, `Uncertainty` 8,
  `ComparisonSummary` 5, `TweediePowerFit` 3, `Model` 3, and 14 more classes at 1–2 each). A
  refusal here is a platform defect seen in logs and Job records, where `safe_error` keeps the
  type alone.
- **Test churn** (predicate: every `match=` string literal in `packages/*/tests/**/*.py` and
  `backend/tests/**/*.py`, 477 in all, split on regex metacharacters; a site is hit when any run
  of ≥10 characters occurs in the site's f-string with its `FormattedValue`s removed): **70** of
  the 157 sites are hit, by **104** asserts in **25** files. An upper bound on asserts to
  *review*: an assert matching only the rule text survives a rewrite that keeps that text. The
  frontend (`frontend/src`, `.ts` and `.vue`, generated code excluded) quotes **0** of the 157
  by the same fragment predicate.

**The executor re-derives every number above at its base** (Task 0) and records both trees in
the LG; a slice that merged in between can move them.

## Acceptance Standard

Each item names the slice it binds under DP-9 (c), the recommended split (A = SL 9956, B1, B2).
With DP-9 (a), all items bind the one slice.

1. **(i), the ruling's first test** (A; final form at B2). `uv run pytest -q
   packages/model-schema/tests/test_input_free_raises.py` passes. Its census enumerates every
   `ast.Raise` in `packages/model-schema/src/model_schema/*.py` whose callee resolves (by
   importing the module) to `ValueError` or a subclass, plus every `assert` statement and every
   `PydanticCustomError` call, and fails when any of them is not an `InputFreeError` (or
   subclass) — each such raise renders the fixed text in a 422. Under a split it holds against
   `_RESIDUAL`, an exact per-`(file, Class.function)` count of the plain raises still to rewrite:
   the census must equal it (a new plain raise fails; a rewritten one fails until its entry is
   decremented); `_RESIDUAL` holds only B1/B2 entries, so at A's merge **no 422-reachable raise
   path renders generic text**; at B2's merge `_RESIDUAL` is deleted and the test asserts zero.
   Its broken-input case reports a planted plain `ValueError`, a planted interpolating
   `InputFreeError` and a planted `assert`.
2. **(ii), the ruling's census test** (A, B1, B2). The same file asserts every `InputFreeError`
   raise takes a literal or a constant-only f-string — no rewritten message interpolates an
   input value. The LG records, per slice, the sites adopted unchanged and the sites rewritten
   by `file:line` at its base, with each rewritten message's before and after text.
3. **The rewrite keeps the guidance** (A, B1, B2). Every rewritten message names the field (by
   its declared name) and the rule, keeps any requirement citation the old text carried
   (`FR-…`, `` `02` §… ``), and keeps the old text's remedy sentence where it had one. The LG's
   before/after table is what the reviewer reads; a rewrite that drops a rule or a citation is
   a NOT-ACK.
4. `uv run pytest -q packages/pricing-core/tests/test_safe_error.py` passes (A), including: a
   `ValidationError` from an `InputFreeError` keeps the authored text in `safe_error_detail`;
   one from a plain `ValueError` interpolating `_SENTINEL` does not carry it; and (DP-8 (a)) a
   `GraphUnresolvedRefError` keeps its now-literal text.
5. `uv run pytest -q backend/tests/test_errors.py backend/tests/test_error_sinks.py` passes (A),
   including: (a) a request model's `InputFreeError` reaches the 422 as `"Value error, <text>"`
   exactly (DP-4 (a)); (b) a plain `ValueError(f"… {value}")` with a sentinel reaches it as
   `"The value is not valid (VALUE_ERROR)."` with the sentinel absent from the whole body
   (DP-7 (a)); (c) the real `GlmSpec` Poisson refusal reaches it with
   `"a Poisson model must declare an offset"` in the message; (d) an `int_parsing` control keeps
   pydantic's fixed text; (e) the parked row-8 tests (item 5 above), the first unchanged, the
   second retargeted. Each red seen first by its cause (Task 4 Step 2).
6. **DP-5's ACK line** (A): the slice's MERGE-ACK request lists every pydantic error type whose
   422 rendering changes against `main`, re-derived at the base by the predicate *"every member
   of `pydantic_core.core_schema.ErrorType` (pydantic-core 2.46.5, `uv.lock:1860-1861`) not in
   `_FIXED_TEXT_TYPES`; `value_error` changes only when `ctx["error"]` is not an
   `InputFreeError`"*. At `fe0b0627` that is **74**: `value_error` (non-marker) and the 73 types
   listed in §"DP-5's changed types". It also states the ones a request body reaches today
   (Task 0 Step 4).
7. `uv run lint-imports` passes (A; the new `pricing_core.safe_error → model_schema.input_free`
   edge is inside the `layering` contract).
8. `00-overview.md` §5.3 carries one dated paragraph stating the rule (A, Task 6), and
   `python3 scripts/audit-docs.py` exits 0 at each slice's head.
9. The full two-half gate passes locally in a slot (`dev-commands`), at each slice's head, with
   the tree named; `ModelSpecBuilderView.test.ts` is unchanged and passes.
10. Each slice's diff touches no file outside its write set below;
    `git diff --stat origin/main...HEAD` is in its LG.

## Global Constraints

- NFR-499 (`03-rating-engine.md:1416`; the row is in `03`, and `07:321` and `06` cite it):
  *"quote inputs are never logged in full outside sampled traces, which are access-controlled"*,
  clarified to govern persistence; `safe_error.py:1-9` states the allow-list form: *"an
  exception's text is kept only where it is ours and known to be input-free; everything else is
  its type name and nothing more."*
- FR-450 (`07-platform.md:181`): RFC 9457 problem responses with stable `code`s; `00` §5.3 is the
  shape (`00-overview.md:344-366`). `FieldError` (`model_schema/problem.py:20-32`) is frozen,
  `extra="forbid"`, `message: str` required: a dropped message is a fixed text, never empty.
- ADR-703/ADR-704 via `.importlinter`: `model_schema` imports nothing but pydantic (`:36-51`);
  `pricing_core` imports no web library (`:16-34`).
- Never hand-write a shape that exists in `model-schema` (`CLAUDE.md` §2): the marker is defined
  once, in `model-schema`.
- RL-1263's contention rule (`docs/rulings/RL-01263-…md:89-100`) as amended by RL-1445: two
  concurrent build slices may not both change the same existing function or class; any other
  shared path serialises unless the dispatch record shows the check. **Under a split, A, B1 and
  B2 all change `_RESIDUAL` in the guard file, so they run in sequence, never concurrently.**
- The `compile.py` serial set and `pricing_core/rating/**` are **untouched** by every slice.
- DP-3 (a): `CodedError` is not changed and no rating code changes.
- Standing: red-first per task, closing acts in the slice PR (LG and SL `closed`), one PR per
  slice, barred word 0 in hunks, Co-Authored-By only.

## Write set

| File | Change | Slice · Task |
|---|---|---|
| `packages/model-schema/src/model_schema/input_free.py` | **new**: `class InputFreeError(ValueError)` | A · 1 |
| `packages/model-schema/tests/test_input_free_raises.py` | **new**: guards (i) and (ii), `_RESIDUAL`, broken-input case | A · 1; B1, B2 shrink `_RESIDUAL` |
| the 17 model-schema files of the 96 | `raise ValueError(` → `raise InputFreeError(`; one import line each | A · 2 |
| model-schema files of the slice's rewrite set (§"Size and the split") | the message rewritten input-free and raised as `InputFreeError`; import line where new | A · 3, B1 · 1, B2 · 1 |
| `packages/model-schema/src/model_schema/graph_errors.py` | DP-8 (a): both signals subclass `InputFreeError`; docstring | B1 · 1 |
| model-schema test files whose `match=`/message asserts a rewritten text | the assert follows the new text (never loosened to a bare type) | with each rewrite |
| `packages/pricing-core/src/pricing_core/safe_error.py` | `safe_validation_message`; `_validation_detail` uses it; docstring | A · 4 |
| `packages/pricing-core/tests/test_safe_error.py` | three cases | A · 4 (third at B1) |
| `backend/src/app/errors.py` | `_field_error_message`; `:499` uses it | A · 5 |
| `backend/tests/test_errors.py`, `backend/tests/test_error_sinks.py` | four cases; the parked row-8 tests | A · 5 |
| `docs/specs/00-overview.md` | one dated paragraph in §5.3 | A · 6 |
| `docs/ledgers/LG-…md`, `docs/roadmap.md` (the slice's SL status), `docs/INDEX.md` (generated) | closing acts | each slice |

**Not in any write set:** `model_schema/__init__.py` (the marker is imported by module path, the
`graph_errors` precedent, which also keeps these slices off the `__init__.py` hunks of SL-1557
and SL-1559); `pricing_core/rating/**` (the graph-signal consumers `inline.py:280`,
`runtime.py:496` and `backend/src/app/platform/rating_algorithms.py:63 :70` match by `isinstance`
and are unchanged by DP-8 (a)); the frontend.

## Decision points

**DP-1 to DP-7 are RULED** — `to-lead.md` "2026-10-10 15:52:31 BST — RULINGS on PL 9955 / SL
9956 …", each quoted verbatim:

- **DP-1 — RULED (a).** *"DP-1 (a): `InputFreeError` in model_schema/input_free.py."*
- **DP-2 — RULED (c).** *"DP-2 (c), NOT (a). (a) drops 157 authored validator messages to fixed
  text: the same usability regression I withdrew at 15:37:31, at 157/253 scale, against actuaries
  who rely on these messages. Rewrite all 157 to INPUT-FREE authored text that keeps the
  guidance: name the FIELD and the RULE ("family must be one of the supported families"), never
  the submitted VALUE. All 253 then adopt the marker."* Acceptance, verbatim: *"a test enumerates
  model-schema's validator messages (by AST or by the marker's registry) and fails if any raise
  path renders generic text in the 422. A second test asserts no rewritten message interpolates
  an input value (the census style)."* Size, verbatim: *"the planner re-sizes. If (c) exceeds ~2
  lane-days, bring the split to me (e.g. the 15 closed-vocabulary messages plus the most-used
  validators first) BEFORE building; no silent fallback to (a)."* Scheduling, verbatim: *"after
  FD-1374 merges, off the G2 critical path, before the 4 Nov freeze."*
- **DP-3 — RULED (a).** *"DP-3 (a): CodedError stays separate (its "CODE: msg" form is parsed
  downstream)."*
- **DP-4 — RULED (a).** *"DP-4 (a): the marker's err["msg"] stays byte-identical to main,
  including the "Value error, " prefix; ModelSpecBuilderView's mock is unchanged."*
- **DP-5 — RULED (b).** *"DP-5 (b): ONE allow-list in pricing_core.safe_error, shared by the 422
  and _validation_detail; it also closes uuid_parsing's input-character echo. Unlisted types get
  the DP-7 fixed text. The ACK lists every pydantic error type that changes rendering vs main."*
- **DP-6 — RULED (a).** *"DP-6 (a): one dated paragraph in 00 §5.3 (no new id) stating the rule:
  authored messages are input-free and shown; anything else renders the fixed text."*
- **DP-7 — RULED (a).** *"DP-7 (a): "The value is not valid (<TYPE>).""*
- **The dict-key echo — RULED YES, not this plan's write.** *"The 422 `field` echoing a submitted
  dict KEY: YES, one FD row in D8 (owner WK-1178), proposed severity, remedy named. Not in this
  slice unless trivially inside its write set."* It is not trivially inside it (`errors.py:497`,
  FR-403's form-marking), so it stays out (§"Hand-off").

**Open for the lead:**

**DP-8 — the five graph-signal raises (new; acceptance (i) reaches them).**
`GraphUnresolvedRefError` ×3 (interpolating a step id or a value name) and `GraphCycleError` ×2
are `ValueError` subclasses raised in validators; under DP-5 (b) they would render the fixed
text, which acceptance (i) forbids for "any raise path".
(a) Both classes subclass `InputFreeError` (keeping `ValueError` ancestry, so every
`isinstance` consumer is unchanged) and the 3 interpolating messages are rewritten input-free
like the 157; the guard then covers them by subclass.
(b) `safe_validation_message` also allow-lists the two classes by `isinstance`, and the guard
exempts them by name with their 3 messages rewritten — two mechanisms for one property.
(c) Leave them, and narrow acceptance (i) to `raise ValueError` sites — a ruling change.
**Recommend (a).** One class carries the property; `graph_errors.py`'s docstring already says
the class, not the text, is the contract. Cost: 0.5 h in B1 (their classes, `RatingAlgorithm`
and `SubGraphBody`, are built in a handler, not 422-reachable). Note the guidance cost the
ruling's rule implies here, stated for the lead: *"step 'x' consumes undefined value 'y'"*
becomes *"a step consumes a value that no step produces (FR-212)"*, and a model-level
validator's 422 `field` is the model's own location, so the reader loses *which* step. The
same holds for any message whose value identifies an element (a column, a feature, a band).

**DP-9 — the split (the honest size exceeds ~2 lane-days; §"Size and the split").**
(a) One slice, all 157 + DP-8: ≈4.8 lane-days.
(b) Two slices: A = the marker, guards, allow-list, 422, spec, the 96, the 15 closed and the 54
422-reachable free (≈2.5); B = the 88 others + DP-8 (≈2.5).
(c) Three slices: A as (b) (≈2.5); **B1** = the 41 user-authored, handler-built free messages +
DP-8 (≈1.3); **B2** = the 47 system-produced free messages (≈1.4).
(d) The brief's example cut: A′ = infrastructure + the 96 + the 15 closed + only the 32
UI-form-reachable free (≈2.0); B′ = the other 110 + DP-8 (≈3.0, or split again).
**Recommend (c).** A is the whole of FD-1589 row 8: at its merge no 422-reachable raise path
renders generic text, and the demo forms (`/model-specs/validate`, `/bandings`, `/groupings`,
`/rating-algorithms`) keep their guidance. It runs 0.5 lane-days over the ~2 mark, which is the
22 request-reachable messages (13 behind non-UI routes, 9 in module-level helpers such as
`money.py:83`'s `_reject_float`) that (d) would leave rendering the fixed text in a 422 until
B′ — the regression the 15:37:31 entry withdrew, at smaller scale. B1 then restores guidance on
the handler-built sinks before FD-1589 rows 2–11 route them through `_validation_detail`; B2 is
the system-produced remainder. Each is under ~2 lane-days, and they run in sequence because all
three edit `_RESIDUAL`. **Not a fallback to DP-2 (a):** every slice rewrites; none drops a
message to fixed text by design.

## DP-5's changed types

At `fe0b0627` (pydantic-core 2.46.5), the 73 `ErrorType` members outside `_FIXED_TEXT_TYPES`,
each rendering `The value is not valid (<TYPE>).` in the 422 where `main` renders pydantic's
`msg`: `no_such_attribute json_invalid json_type needs_python_object recursion_loop
frozen_field frozen_instance invalid_key get_attribute_error model_attributes_type
dataclass_type dataclass_exact_type default_factory_not_called none_required multiple_of
finite_number iterable_type iteration_error string_sub_type string_unicode string_not_ascii
mapping_type tuple_type set_type set_item_not_hashable int_parsing_size int_from_float
bytes_type bytes_too_short bytes_too_long bytes_invalid_encoding assertion_error
missing_sentinel_error date_parsing date_from_datetime_inexact date_past date_future time_type
time_parsing datetime_parsing datetime_object_invalid datetime_past datetime_future
timezone_naive timezone_aware timezone_offset time_delta_type time_delta_parsing frozen_set_type
is_instance_of is_subclass_of callable_type union_tag_invalid union_tag_not_found arguments_type
missing_argument unexpected_keyword_argument missing_keyword_only_argument
unexpected_positional_argument missing_positional_only_argument multiple_argument_values
url_type url_parsing url_syntax_violation url_too_long url_scheme uuid_type uuid_parsing
uuid_version decimal_max_places decimal_whole_digits complex_type complex_str_parsing`; plus
`value_error` when `ctx["error"]` is not an `InputFreeError` (after B2, only a validator outside
model-schema). Predicate: the `Literal` arguments of `ErrorType = Literal[...]` in
`pydantic_core/core_schema.py` (104 members), minus the 30 of `safe_error.py:50-58` (all 30 are
members). **Observed for the lead, not a change:** several of these carry fixed, useful text a
request body can reach — `json_invalid` (a malformed body), `date_parsing`, `datetime_parsing`,
`uuid_parsing`, `decimal_max_places`, `decimal_whole_digits`, `union_tag_invalid`,
`union_tag_not_found`, `multiple_of`, `int_from_float`, `finite_number`, `timezone_naive` /
`timezone_aware`. Under the ruled mechanism a type joins `_FIXED_TEXT_TYPES` only with its own
sentinel case (`test_safe_error.py:127`); adding the input-free ones is a later, separate
choice, not this plan's.

## Tasks

The task list is slice A's. B1 and B2 (under DP-9 (c)) are Task 0 + Task 3 over their own sets
+ Task 7, each a slice of its own (§"Size and the split").

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm the activation needs (below) by reading `origin/main`, and record the
  base sha in the LG.
- [ ] **Step 2:** Re-derive the population at the base: the 253/96/15/142 counts, the 5 graph
  signals, the 422-reachable set and the B1/B2 sets, by the predicates of §"The population" and
  §"Where each of the 157 can be read". If they differ from `fe0b0627`'s, record both and work
  from the base's; the split's membership is the base's.
- [ ] **Step 3:** For every open slice branch that touches `packages/model-schema/src` (at
  `fe0b0627`: `origin/sl-1557-wk675-s3`, `model_schema/rating.py` and `__init__.py`;
  `origin/sl-1559-wk675-s4`, the same), list the functions both diffs change:
  `git diff -U0 origin/main...origin/<branch> -- packages/model-schema/src` against this
  slice's sites. Any shared function is named in the dispatch record, and the later of the two
  merges main in and re-runs Task 1's guard (a plain `raise ValueError` the other slice adds
  then fails the guard, and is adopted or rewritten).
- [ ] **Step 4:** List the `except ValueError` handlers outside model-schema that render or
  parse `str(exc)` of a model-schema raise (at `fe0b0627`: `git grep -nE 'except
  \(?[A-Za-z, ]*ValueError' -- backend/src packages/pricing-core/src`, 39 lines; those read in
  `backend/src/app/api/approvals.py:114`, `deps.py:165 :216`, `dislocation_runs.py:192` render
  a fixed text or `safe_error_text`). A handler that parses a message the slice rewrites is a
  plan defect: stop. Also list which of §"DP-5's changed types" a request body reaches, for
  acceptance 6.

### Task 1: The marker and its guards (red first)

**Files:** Create `packages/model-schema/src/model_schema/input_free.py`,
`packages/model-schema/tests/test_input_free_raises.py`.

**Interfaces:** Produces `model_schema.input_free.InputFreeError` (a `ValueError` subclass, no
new attributes) and, test-local, `_census(module) -> _Census` with three lists of
`(file, "Class.function", line)`: plain (a `ValueError`-family raise not of the marker family,
an `assert`, a `PydanticCustomError`), and interpolating-marker (an `InputFreeError`-family
raise whose message is not a literal or constant-only f-string).

- [ ] **Step 1: Write the guards.** The census resolves a raise's callee by name in the
  imported module's namespace, so a subclass counts by `issubclass`, not by spelling:

```python
"""Every model-schema raise path renders authored text in a 422, and no authored text carries
an input value (NFR-499; FD-1589 row 8, remedy (c); 15:52:31 DP-2 (c) acceptance (i), (ii)).

`pricing_core.safe_error.safe_validation_message` keeps an `InputFreeError`'s text and nothing
else a validator raises, so (i) every `ValueError`-family raise here is an `InputFreeError`, and
(ii) every such raise passes a literal, or an f-string over upper-case module constants alone.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import re
from collections import Counter
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src" / "model_schema"
_CONST = re.compile(r"_?[A-Z][A-Z0-9_]*")

#: Plain raises still to rewrite, by (file, "Class.function"): an EXACT count. A slice that
#: rewrites one decrements it; a new plain raise fails. Holds only sites no request body
#: reaches (PL 9955 §"Where each of the 157 can be read"). Emptied and deleted by the last slice.
_RESIDUAL: dict[tuple[str, str], int] = {
    # filled at Task 1 Step 4 from the census, B1 and B2 entries only
}


def _input_free(arg: ast.expr) -> bool:
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return True
    if isinstance(arg, ast.JoinedStr):
        names = {
            n.id
            for v in arg.values
            if isinstance(v, ast.FormattedValue)
            for n in ast.walk(v.value)
            if isinstance(n, ast.Name)
        }
        return all(_CONST.fullmatch(name) for name in names)
    return False


def _census(source: str, namespace: dict[str, object], filename: str):
    from model_schema.input_free import InputFreeError

    plain: list[tuple[str, str, int]] = []
    interpolating: list[tuple[str, str, int]] = []

    def visit(node: ast.AST, scope: list[str]) -> None:
        for child in ast.iter_child_nodes(node):
            inner = scope + [child.name] if isinstance(
                child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            ) else scope
            where = (filename, ".".join(inner[-2:]) or "<module>", getattr(child, "lineno", 0))
            if isinstance(child, ast.Assert):
                plain.append(where)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and (
                child.func.id == "PydanticCustomError"
            ):
                plain.append(where)
            if isinstance(child, ast.Raise) and isinstance(child.exc, ast.Call) and isinstance(
                child.exc.func, ast.Name
            ):
                name = child.exc.func.id
                cls = namespace.get(name, getattr(builtins, name, None))
                if isinstance(cls, type) and issubclass(cls, ValueError):
                    args = child.exc.args
                    if not issubclass(cls, InputFreeError):
                        plain.append(where)
                    elif not (len(args) == 1 and _input_free(args[0])):
                        interpolating.append(where)
            visit(child, inner)

    visit(ast.parse(source), [])
    return plain, interpolating


def _all() -> tuple[list[tuple[str, str, int]], list[tuple[str, str, int]]]:
    plain, interpolating = [], []
    for path in sorted(_SRC.glob("*.py")):
        module = importlib.import_module(f"model_schema.{path.stem}") if path.stem != "__init__" else importlib.import_module("model_schema")
        p, i = _census(path.read_text(), vars(module), path.name)
        plain += p
        interpolating += i
    return plain, interpolating


@pytest.mark.req("NFR-499")
def test_no_marker_raise_interpolates_a_value() -> None:  # acceptance (ii)
    _, interpolating = _all()
    assert not interpolating, f"an InputFreeError takes a literal message: {interpolating}"


@pytest.mark.req("NFR-499")
def test_every_raise_path_renders_authored_text_in_a_422() -> None:  # acceptance (i)
    plain, _ = _all()
    counts = Counter((f, where) for f, where, _ in plain)
    assert counts == Counter(_RESIDUAL), (
        "raise InputFreeError with input-free text; rewritten sites leave _RESIDUAL: "
        f"{sorted((counts - Counter(_RESIDUAL)).items())} new, "
        f"{sorted((Counter(_RESIDUAL) - counts).items())} stale"
    )


@pytest.mark.req("NFR-499")
def test_the_census_reports_planted_violations() -> None:
    from model_schema.input_free import InputFreeError

    planted = (
        "def f(value):\n"
        "    raise ValueError('a literal message')\n"
        "    raise InputFreeError(f'bad {value}')\n"
        "    raise InputFreeError(f'ok {_LIMIT}')\n"
        "    assert value\n"
    )
    plain, interpolating = _census(planted, {"InputFreeError": InputFreeError}, "planted.py")
    assert [line for *_, line in plain] == [2, 5]
    assert [line for *_, line in interpolating] == [3]
```

  The sketch is the shape; the executor may restructure it (for example, one walk shared by
  the three tests) but keeps: resolution by `issubclass` in the module's namespace, `assert`
  and `PydanticCustomError` counted as plain, the exact-count `_RESIDUAL`, and the planted case.
- [ ] **Step 2: Run it and see the red by its cause.**
  `uv run pytest -q packages/model-schema/tests/test_input_free_raises.py`. Expected: collection
  or the tests fail on `ModuleNotFoundError: model_schema.input_free` — the only cause. A
  failure on anything else is a plan defect: stop.
- [ ] **Step 3: Create the marker.**

```python
"""A validator refusal whose message is authored text with no submitted value in it
(NFR-499; FD-1589 row 8, remedy (c)).

`pricing_core.safe_error` keeps this exception's message where it keeps no other `ValueError`'s:
a request-validation 422 and a stored `ValidationError` detail both show it. That is safe only
because every raise site passes a string literal (or an f-string over module constants alone),
which `tests/test_input_free_raises.py` holds by AST. A message names the field and the rule,
never the value it was given. Raised inside a pydantic validator, it is reported as
`type == "value_error"`, with the instance at `errors()[i]["ctx"]["error"]`, like
`graph_errors`'s signals.
"""

from __future__ import annotations


class InputFreeError(ValueError):
    """A `ValueError` whose message is a literal: it names the field and the rule, never the value."""
```

- [ ] **Step 4: Re-run; see the second red.** The planted case and (ii) PASS (no marker raise
  exists yet); (i) FAILS listing every plain raise (253 + 5 graph signals at `fe0b0627`).
  Fill `_RESIDUAL` with exactly the B1 and B2 entries of that list (under DP-9 (a), leave it
  empty); (i) then fails on slice A's sites alone, which Tasks 2 and 3 clear.
- [ ] **Step 5: Commit** (the guard stays red until Task 3; commit with Task 2 if the executor's
  workflow forbids a red commit, and say so in the LG).

### Task 2: Adopt the marker at the 96 input-free sites

**Files:** the 17 files of the population. **Interfaces:** consumes `InputFreeError`.

- [ ] **Step 1:** In each file, add `from model_schema.input_free import InputFreeError` with
  the other first-party imports, and change each literal or constant-only site from
  `raise ValueError(` to `raise InputFreeError(`. The message text is not touched (DP-4 (a)).
- [ ] **Step 2:** `uv run pytest -q packages/model-schema/tests`: every test but (i) PASSES
  (`pytest.raises(ValueError)` and `except ValueError` still match a subclass; a failure that
  names `InputFreeError` in a `type(...) is ValueError` or a class-name assertion is a finding to
  report, not to patch around). (i) now lists only A's interpolating sites.
- [ ] **Step 3:** `uv run ruff check packages/model-schema && uv run mypy` on the package; commit.

### Task 3: Rewrite the slice's interpolating messages input-free

**Files:** slice A's rewrite set — the 15 closed and the 54 422-reachable free sites
(§"Size and the split"), and the test files whose asserts quote them. (B1 and B2 run this task
over their own sets.)

**The rewrite rule** (DP-2 (c), verbatim: *"name the FIELD and the RULE … never the submitted
VALUE"*):

1. Keep every sentence that states the rule, the reason and the remedy, and every requirement
   citation, word for word where it has no value in it.
2. Replace each interpolated value with the declared name of the field it came from
   (`self.slug` → "the banding's slug"; `len(self.alphas)` → "`cv.alphas`"), or drop the clause
   when the field is already named. Never an index, a key, a count of the input, or an enum
   member's value — the closed-vocabulary 15 included (*"cv.alphas has {len(...)} point(s); at
   least 2 are needed …"* → *"cv.alphas needs at least 2 points for a path to select from — one
   alpha is a fixed fit, not a cross-validation."*).
3. Raise `InputFreeError`; the message passes guard (ii).
4. Worked examples at `fe0b0627`:
   - `modelling.py:388` (`Banding`): *"banding {slug!r} has boundaries {list(...)}, which do not
     strictly increase (`02` §4.2). Equal cut points make an empty band …"* → *"a banding's
     boundaries must strictly increase (`02` §4.2). Equal cut points make an empty band …"* (the
     rest unchanged).
   - `refs.py:104` (`ArtifactRef`): *"{value!r} is not a valid artifact reference
     ({type}:{slug}@{version})"* → *"an artifact reference must have the form
     {type}:{slug}@{version}"* (the braces are literal text in the old message; keep them so,
     escaped as `{{…}}` only if the message stays an f-string).
   - `modelling.py:1407` (`GbmSpec`): *"objective {name!r} counts events but the spec declares no
     offset (FR-121). Set offset to log(exposure), or say in offset_acknowledgement why this data
     needs none."* → *"a counting objective needs an offset (FR-121). Set offset to
     log(exposure), or say in offset_acknowledgement why this data needs none."*
- [ ] **Step 1: Red first, per validator.** For each validator in the set, change the asserts
  that quote its message (the test-churn predicate lists them) to the new text, and add one
  assert where none exists that the message's new text appears and no sentinel value does; run
  that test file and see it FAIL on the old text. Batch by file.
- [ ] **Step 2: Rewrite**, per the rule; run the file's tests: PASS. A test whose assert can only
  pass by matching the removed value is a finding: report it, do not loosen it to a bare type.
- [ ] **Step 3:** When the set is done, `uv run pytest -q packages/model-schema/tests` and the
  backend and pricing-core test files the churn predicate named: PASS; guard (i) PASSES against
  `_RESIDUAL`, (ii) PASSES. The LG records the before/after table (acceptance 2, 3). Commit per
  file or per module group.

### Task 4: `pricing_core.safe_error` allow-lists the marker (DP-5 (b))

**Files:** Modify `packages/pricing-core/src/pricing_core/safe_error.py`; test
`packages/pricing-core/tests/test_safe_error.py`.

**Interfaces:** Produces
`safe_validation_message(error: Mapping[str, Any]) -> str | None` (exported in `__all__`): the
`msg` of one pydantic error dict when it is safe to show, else `None`.

- [ ] **Step 1: Write the failing tests** (beside `test_a_coded_error_keeps_its_text…`, `:229`;
  reuse the module's `_SENTINEL` and `_failure` helpers):

```python
from model_schema.input_free import InputFreeError


class _Authored(BaseModel):
    family: str

    @field_validator("family")
    @classmethod
    def _refuse(cls, value: str) -> str:
        if value == "authored":
            raise InputFreeError("a Poisson model must declare an offset")
        raise ValueError(f"unacceptable family {value}")


@pytest.mark.req("NFR-499")
def test_an_input_free_validator_message_is_kept_and_an_interpolating_one_is_not() -> None:
    kept = safe_error_detail(_failure(_Authored, {"family": "authored"}))
    assert "family: [value_error] Value error, a Poisson model must declare an offset" in kept
    dropped_exc = _failure(_Authored, {"family": _SENTINEL})
    assert _SENTINEL in str(dropped_exc), "control: the raw text carries the value"
    dropped = safe_error_detail(dropped_exc)
    assert _SENTINEL not in dropped
    assert "family: [value_error]" in dropped


@pytest.mark.req("NFR-499")
def test_safe_validation_message_keeps_fixed_text_and_the_marker_only() -> None:
    (authored,) = _failure(_Authored, {"family": "authored"}).errors()
    (plain,) = _failure(_Authored, {"family": _SENTINEL}).errors()
    assert safe_validation_message(authored) == authored["msg"]
    assert safe_validation_message(plain) is None
    assert safe_validation_message({"type": "int_parsing", "msg": "Input should be a valid integer"}) == (
        "Input should be a valid integer"
    )
    assert safe_validation_message({"type": "union_tag_invalid", "msg": _SENTINEL}) is None
```

  (Under DP-8 (a), B1 adds a third case: a `GraphUnresolvedRefError` raised in a validator is
  kept.)
- [ ] **Step 2: Run them; see the red by its cause.**
  `uv run pytest -q packages/pricing-core/tests/test_safe_error.py -k "input_free or safe_validation_message"`.
  Expected: collection fails with `ImportError` on `safe_validation_message`. Add the import of
  the not-yet-written name to the test module's `from pricing_core.safe_error import (...)`
  block first, so the cause is that name and nothing else.
- [ ] **Step 3: Implement.**

```python
from collections.abc import Callable, Mapping
from typing import Any

from model_schema.input_free import InputFreeError


def safe_validation_message(error: Mapping[str, Any]) -> str | None:
    """The `msg` of one pydantic error when it carries no input, else `None`.

    Kept for an error type in `_FIXED_TEXT_TYPES`, and for a `value_error` raised as an
    `InputFreeError` (whose every raise site is a literal). One rule for every sink: the
    request-validation 422 and `_validation_detail` both read it.
    """
    if error["type"] in _FIXED_TEXT_TYPES:
        return str(error["msg"])
    underlying = (error.get("ctx") or {}).get("error")
    if error["type"] == "value_error" and isinstance(underlying, InputFreeError):
        return str(error["msg"])
    return None
```

  and in `_validation_detail` replace `:113-114` with:

```python
        message = safe_validation_message(error)
        if message is not None:
            text += f" {message}"
```

  Add `"safe_validation_message"` to `__all__`, and amend the module docstring's second bullet
  (`:18-23`) to name the marker: *"…and the `msg` only for an error type in `_FIXED_TEXT_TYPES`,
  each verified to carry no input, or for a `value_error` raised as `model_schema`'s
  `InputFreeError`, whose raise sites are literals."*
- [ ] **Step 4:** `uv run pytest -q packages/pricing-core/tests/test_safe_error.py`: PASS (the
  existing parametrised cases at `:127` and `:185` unchanged). `uv run lint-imports`: PASS.
  Commit.

### Task 5: The 422 sink uses it (FD-1589 row 8)

**Files:** Modify `backend/src/app/errors.py` (`:485-510`); tests `backend/tests/test_errors.py`
and `backend/tests/test_error_sinks.py`.

**Interfaces:** consumes `safe_validation_message`.

- [ ] **Step 1: Bring in the parked tests.** From `origin/draft/fd1589-row8-tests` @`cfe8e15f`,
  take the `backend/tests/test_error_sinks.py` hunks only
  (`git diff fe0b0627 cfe8e15f -- backend/tests/test_error_sinks.py`), never the `errors.py`
  ones. Keep `test_a_request_validation_422_carries_no_submitted_value` as is. Retarget
  `test_a_coded_validator_message_survives_the_422_sink` to raise
  `InputFreeError("an authored, input-free message")` (rename it
  `test_an_input_free_validator_message_survives_the_422_sink`), and add
  `test_a_coded_validator_message_gets_the_fixed_text`, asserting the 422 message is
  `"The value is not valid (VALUE_ERROR)."` for the `CodedError` trigger (DP-3 (a) with DP-5 (b):
  `CodedError` is not on the 422 allow-list). The LG records the change from the parked form.
- [ ] **Step 2: Write the bare-app tests** beside `failing_client` (`test_errors.py:27-48`), no
  database:

```python
from pydantic import field_validator

from model_schema.input_free import InputFreeError
from model_schema import GlmSpec, new_uuid7

_SENTINEL = "SENTINEL-422-input-5e0c2b91"


class _Validated(BaseModel):
    family: str

    @field_validator("family")
    @classmethod
    def _refuse(cls, value: str) -> str:
        if value == "authored":
            raise InputFreeError("an authored, input-free message")
        raise ValueError(f"unacceptable value {value}")


@pytest.fixture
def validating_client(settings) -> TestClient:
    app = create_app(settings)

    @app.post("/_test/authored")
    async def _authored(body: _Validated) -> None:
        return None

    @app.post("/_test/glm")
    async def _glm(body: GlmSpec) -> None:
        return None

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.req("NFR-499")
def test_an_input_free_validator_message_reaches_the_422(validating_client: TestClient) -> None:
    response = validating_client.post("/_test/authored", json={"family": "authored"})
    assert response.status_code == 422
    (error,) = response.json()["errors"]
    assert error["code"] == "VALUE_ERROR"
    assert error["message"] == "Value error, an authored, input-free message"


@pytest.mark.req("NFR-499")
def test_an_interpolating_validator_message_does_not_reach_the_422(
    validating_client: TestClient,
) -> None:
    response = validating_client.post("/_test/authored", json={"family": _SENTINEL})
    assert response.status_code == 422
    assert _SENTINEL not in response.text
    (error,) = response.json()["errors"]
    assert error["field"] == "family"
    assert error["message"] == "The value is not valid (VALUE_ERROR)."


@pytest.mark.req("NFR-499")
def test_a_model_schema_authored_refusal_keeps_its_guidance(validating_client: TestClient) -> None:
    body = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": str(new_uuid7()),
        "response_column": "claim_count",
    }  # family defaults to poisson and offset to kind "none" (modelling.py:1040-1043, :680)
    response = validating_client.post("/_test/glm", json=body)
    assert response.status_code == 422
    messages = [e["message"] for e in response.json()["errors"]]
    assert any("a Poisson model must declare an offset" in m for m in messages), messages


@pytest.mark.req("FR-403")
def test_a_fixed_text_type_keeps_its_message(failing_client: TestClient) -> None:
    response = failing_client.post("/_test/validate", json={"count": "not-an-int"})
    (error,) = response.json()["errors"]
    assert error["code"] == "INT_PARSING"
    assert error["message"] == "Input should be a valid integer, unable to parse string as an integer"
```

  The `GlmSpec` body mirrors `packages/model-schema/tests/test_offset_model_spec.py:10-19`'s
  `_spec` without its `offset`; if `GlmSpec` refuses it for a second reason at the base, mirror
  that test's builder rather than inventing fields. The `int_parsing` text is pydantic 2.13.5's
  (`uv.lock:1845-1846`); verify it in the red run and copy the observed text, never this line,
  if it differs.
- [ ] **Step 3: Run them; see each red by its cause.**
  `uv run pytest -q backend/tests/test_errors.py backend/tests/test_error_sinks.py` (the second
  is DB-backed: inside the gate slot only, per `dev-commands`). On `main`'s handler: the two
  interpolating cases FAIL because the sentinel is in the body, and the coded case FAILS because
  `main` keeps its text; the authored, Poisson and `int_parsing` cases PASS (that is `main`'s
  behaviour, which the remedy keeps). So the red for the authored and Poisson cases is taken
  **after** writing a `_field_error_message` that returns the fixed text for every `value_error`
  (the reverted `40604029` form, the regression the ruling names): both FAIL with the fixed text
  in place of the guidance. Record every run in the LG. A red with any other cause is a plan
  defect: stop.
- [ ] **Step 4: Implement.**

```python
from collections.abc import Mapping
from typing import Any

from pricing_core.safe_error import safe_validation_message


def _field_error_message(err: Mapping[str, Any]) -> str:
    """`FieldError.message` for one pydantic error, with no submitted value in it (NFR-499).

    `pricing_core.safe_error.safe_validation_message` keeps fixed-text types and an
    `InputFreeError`'s authored text; anything else, which a validator may have filled with the
    value it was given, is replaced by a fixed text naming the error type (DP-7 (a)).
    """
    message = safe_validation_message(err)
    if message is not None:
        return message
    return f"The value is not valid ({str(err['type']).upper()})."
```

  and `:499` becomes `message=_field_error_message(err),`.
- [ ] **Step 5:** the two test files: PASS; `uv run lint-imports` and `uv run mypy`: PASS. Commit.

### Task 6: The spec line (DP-6 (a))

- [ ] **Step 1:** Append to `00-overview.md` §5.3, after the paragraph ending "corrected
  2026-08-14 when WK-658 implemented the propagation." (`:366`), one paragraph, following
  `spec-change` (no new id):

  *(Clarified 2026-10-XX, WK-1178, FD-1589 row 8 remedy (c), on the lead's entries "2026-10-10
  15:37:31 BST — RULING: DP-M2 WITHDRAWN …" and "2026-10-10 15:52:31 BST — RULINGS on PL 9955 /
  SL 9956 …".)* A request-validation `422`'s `errors[].message` carries no submitted value (`03`
  NFR-499). Authored validator messages are input-free — they name the field and the rule,
  never the value — and are shown: a refusal raised as `model-schema`'s `InputFreeError`, whose
  every raise site is a literal, and a fixed-text error type. Any other message is
  `The value is not valid (<TYPE>).` `errors[].code` and `errors[].field` are unchanged.

  (`XX` is the executor's commit date, from `date`.)
- [ ] **Step 2:** `python3 scripts/audit-docs.py`: exit 0. Commit.

### Task 7: The gate and the closing acts

- [ ] **Step 1:** The full two-half gate in a slot (`dev-commands`), at the head, tree named.
- [ ] **Step 2:** The LG: scope quoted from the slice's SL row; the base and head; the
  population derivations at both trees; the red runs by cause; the adopted and rewritten sites
  with the before/after table; `_RESIDUAL` at the head (empty at the last slice); for slice A,
  DP-5's changed-types list (acceptance 6); the `--stat`. LG and the SL `closed` in the slice PR.

## Size and the split

**Measured inputs** (§"Where each of the 157 can be read"); **rates are estimates, not
measurements**, stated so the lead can re-weight them: authoring a closed-vocabulary rewrite
4 min, a free-value rewrite 6 min (139 of the 157 span more than one line, 643 lines in all);
review 2 min per rewrite; 4 min per `match=` assert to review or update; infrastructure (marker,
guards, allow-list, 422 helper, tests, spec) 3.0 h, from the first draft's 3–4 h estimate less
the renames; the 96 renames and 17 imports 1.0 h; the graph signals 0.5 h; one gate and the
closing acts 1.5 h per slice. A lane-day is 7 executor-seat hours.

| Class | Sites | Lines spanned | `match=` asserts | Validators | Hours | Lane-days |
|---|---|---|---|---|---|---|
| Infrastructure (Tasks 1, 4, 5, 6) | — | — | — | — | 3.0 | 0.43 |
| Input-free, adopted unchanged (Task 2) | 96 | — | — | 17 files | 1.0 | 0.14 |
| Closed-vocabulary (enum `.value` / `len()`) | 15 | 58 | 15 | 13 in 7 files | 2.5 | 0.36 |
| Free, 422-reachable (32 via a UI form, 13 other routes, 9 module-level helpers) | 54 | 213 | 36 | 38 in 10 files | 9.6 | 1.37 |
| Free, user-authored, handler-built (B1) | 41 | 158 | 27 | 19 in 9 files | 7.3 | 1.04 |
| Graph signals, DP-8 (a) (B1) | 5 (3 rewritten) | — | — | 2 | 0.5 | 0.07 |
| Free, system-produced (B2) | 47 | 214 | 26 | 27 in 8 files | 8.0 | 1.14 |
| Gate + closing acts | per slice | | | | 1.5 | 0.21 |

Per file, the 157 (closed + free): `modelling.py` 55 (4 + 51), `objectives.py` 18 (1 + 17),
`perils.py` 12 (1 + 11), `prediction.py` 11, `comparison.py` 8, `rating.py` 8, `refs.py` 8,
`diagnostics.py` 7 (2 + 5), `metrics.py` 5 (2 + 3), `jobs.py` 4 (3 + 1), `approvals.py` 3,
`sub_graphs.py` 3, `validation.py` 3, `backtests.py` 2, `ids.py` 2, `money.py` 2,
`profiles.py` 2 (2 + 0), `datasets.py`, `dislocation.py`, `permissions.py`, `regression.py` 1
each. The densest validators: `CustomObjective._each_field_belongs_to_one_arm` 6,
`Grouping._the_declared_behaviour_is_reachable` 5, `EbmFitResult._the_lookup_shapes_match_the_bins`
5, `ComparisonSummary._every_reference_belongs_to_this_comparison` 5,
`Uncertainty._the_kind_and_its_evidence_agree` 8.

**Totals.** One slice (DP-9 (a)): **33.4 h ≈ 4.8 lane-days.** DP-9 (b): A 17.6 h ≈ 2.5, B 17.3 h
≈ 2.5. **DP-9 (c), recommended: A 17.6 h ≈ 2.5 · B1 9.3 h ≈ 1.3 · B2 9.5 h ≈ 1.4; total ≈ 5.2**
(two more gates). DP-9 (d): A′ 13.9 h ≈ 2.0 · B′ 21.0 h ≈ 3.0. At half the authoring rates the
one-slice total is still 25.8 h ≈ 3.7 lane-days, over ~2: the split does not rest on the rates.

**Slice A (SL 9956)** — the marker, guards (i) and (ii) with `_RESIDUAL`, the allow-list, the
422, the spec paragraph, the 96, the 15 closed, the 54 422-reachable free. Acceptance 1–10;
at its merge (i) holds for every 422-reachable path and `_RESIDUAL` holds the 41 + 5 + 47
others. Its validators, by class: `Banding` 4, `Grouping` 5, `OffsetSpec`, `SplitRef`,
`LossTreatment` 1 each, `GlmCvSpec` 1, `TweediePowerSpec` 1, `GlmSpec` 3, `GbmSpec` 2,
`EbmSpec` 4, `RatingModelCallStep` 1, `ArtifactRef` 8, `ApproximationDeviation`,
`ApprovalPolicyEntry` 1 each, `ObjectiveParameter`, `SamplingSpec` 1 each, `LargeLossTreatment`
3, `PerilComponent` 3, `ExcludedPeril` 1, `RatingVersionCreate` 2, and the module-level
helpers `ids.py` 2, `money.py` 2, `permissions.py` 1, `rating.py` 2, `validation.py` 1,
`objectives.py` `battery_is_exactly` 1. (`TemplateParameter.check`'s 4 are a method of a
handler-built class, so B1; Task 0 moves any site to A whose class it finds request-reachable.)
**Slice B1** — the 41 handler-built free messages and DP-8. Acceptance 1 (shrunk `_RESIDUAL`),
2, 3, 4 (third case), 8–10.
**Slice B2** — the 47 system-produced free messages; deletes `_RESIDUAL`. Acceptance 1 (final
form), 2, 3, 8–10.

## Sequencing, lane and merge-order slot

- **Scheduling (the 15:52:31 ruling):** after the FD-1374 slice (`SL-1536`) merges; off the G2
  critical path; before the 4 Nov freeze. Under DP-9 (c), A first (before the exit demo if the
  lanes allow, the 15:37:31 entry's "if the lanes allow"), then B1, then B2 — in sequence,
  because all three change `_RESIDUAL` (RL-1263).
- **Lane:** a WK-1178 fix slice, **not** in the `compile.py` serial set and touching no
  `pricing_core/rating/**` file. It touches `backend/src/app/errors.py` in a function
  (`_handle_validation_error`, `:485-510`) different from the FD-1374 slice's registry line
  (`RATING_ERROR_CODES`, `:309`).
- **Contention:** the rewrite sets sit inside existing validators in many model-schema files.
  `SL-1557` and `SL-1559` (WK-675, `draft`) change `model_schema/rating.py` and `__init__.py`;
  A changes `rating.py`'s 11 literal sites and 5 free ones (`RatingModelCallStep`,
  `RatingVersionCreate`, two helpers), B1 its 3 graph-signal sites. Task 0 Step 3 names any
  shared function; RL-1263 serialises the pair where one exists.
- **Plan dependency, named:** after A merges, any slice that adds a plain `raise ValueError` (or
  an `assert`) in `packages/model-schema/src` fails guard (i) until it raises `InputFreeError`
  with input-free text. The guard's message says so; a dispatch record for such a slice names
  it.

## Activation needs

1. The FD-1374 slice (`SL-1536`, `PL-1535`) merged (it touches `errors.py`'s registry line and
   carries the row-8 revert `8842b7c5`).
2. DP-1 to DP-7 ruled (done, 15:52:31); **DP-8 and DP-9 ruled**; PL 9955 and SL 9956 minted
   (and, under DP-9 (b) or (c), the further SL rows cut under ids the lead reserves); this plan
   `active`.
3. The dispatch record carries Task 0 Step 3's check against every open model-schema slice
   (today `SL-1557`, `SL-1559`).
4. The lead's GO.

## Hand-off (not this plan's writes)

- **The dict-key echo FD row** (ruled YES at 15:52:31): one FD row in D8, owner WK-1178,
  proposed severity LOW (requester-only), remedy named: `errors.py:497` joins `err["loc"][1:]`,
  and for a dict-typed field pydantic's `loc` holds the submitted key; render it through
  `safe_error._safe_location` (`:96-101`), which masks an undeclared key as `<key>`. The lead's
  docs batch drafts it; not in this plan's write set (it changes FR-403's form-marking
  `field`).
- FD-1589 row 8's dated lines (the interim line, 15:37:31 item 3; the disposition at A's merge):
  the lead's docs batch.
- The barred-word count of this file and its commit: 0 (`grep -ciE 'dep''uty'`).

## Self-review

1. **Spec coverage:** NFR-499 (Tasks 1–5), FR-450 / `00` §5.3 (Tasks 5–6), FR-403 (Task 5's
   control). Every limb of the 15:37:31 item 2 has a task: marker in model-schema (1), adopted
   by the authored validators (2, 3), allow-listed in `pricing_core.safe_error` (4), row 8
   renders authored messages and drops the rest (5). Every limb of the 15:52:31 DP-2 (c): all
   157 rewritten (Task 3 over A, B1, B2), all 253 adopt (guard (i) at B2), test (i) and test (ii)
   (Task 1), the re-size and the split (§"Size and the split", DP-9), the scheduling line
   (§"Sequencing"); DP-5's ACK list (§"DP-5's changed types", acceptance 6).
2. **Placeholders:** Task 6's `XX` (a date the executor writes) and `_RESIDUAL`'s entries (filled
   from the census at Task 1 Step 4, by design).
3. **Names:** `InputFreeError`, `safe_validation_message`, `_field_error_message`,
   `_validation_detail`, `_FIXED_TEXT_TYPES`, `_RESIDUAL`, `failing_client`, `create_app`,
   `GlmSpec`, `new_uuid7`, `GraphCycleError`, `GraphUnresolvedRefError`, `CodedError` are each
   grepped at `fe0b0627`, at `cfe8e15f`, or defined in a task above; the test helpers
   `_SENTINEL` and `_failure` in `test_safe_error.py` exist at `:40` and `:120`.
4. **Ruled vs open:** no task depends on an unruled choice except where it says so (DP-8 in B1;
   DP-9 in the slice boundaries). No option is silently picked: DP-9's recommendation is not a
   fallback to DP-2 (a).
