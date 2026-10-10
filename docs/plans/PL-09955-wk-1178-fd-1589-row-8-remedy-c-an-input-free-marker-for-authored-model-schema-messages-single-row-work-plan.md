---
id: PL-9955
family: plan
kind: map
title: WK-1178 — FD-1589 row 8, remedy (c): an input-free marker for authored model-schema validator messages, allow-listed by pricing_core.safe_error, so the request-validation 422 keeps authored guidance and drops anything else: single-row Work plan
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
> REQUIRED SUB-SKILL for the executor: subagent-driven-development (recommended) or
> executing-plans. The executor also binds `python-test` (the `req` marker, broken-input
> proofs), `test-driven-development` (every red seen first, by its cause), `python-package`
> (the import-linter layers), `dev-commands` (the gate slot wrapper, the two-half gate,
> `uv sync --all-packages` in a fresh worktree), `spec-change` (Task 5's one dated line) and
> `git-hygiene`; reads [`README.md`](README.md)'s five unchecked conventions; and is spawned
> from `.claude/roles/executor.md`.

*Disclosure: drafted under working ids 9955 (this plan) and 9956 (its slice row), both reserved
by the lead in `~/gi-pricing-plan.local/handover/brief-planner-remedy-c-2026-10-10.md`. The
brief asks for "a LEAF PLAN"; this file is `kind: map`, a single-row Work plan, because
`document-ids.md` §1.6's PL row reads "from Lean P2 L5 **one plan per Work**, slices as rows,
no per-slice `leaf`", and WK-1178's recent fresh drafts (`PL-1535`, `PL-1574`) take that form.
If the lead rules `leaf`, only the `kind:` line and this paragraph change.*

Written by the planner (`planner-remedy-c`) on 2026-10-10 from 15:46:41 BST
(`TZ=Europe/London date`). Evidence read at `origin/main`
`fe0b0627590307259ec6d56be7f73115cf245092` (#1265, 2026-10-10T14:39:26+01:00) unless a line
names another commit. **No test, check or gate was run at planning time.** Every count below
gives its predicate verbatim; each was run read-only against that tree.

**Draft, not frozen.** Seven decision points (DP-1 to DP-7) are open for the lead (the
15:37:31 entry: "its DPs come to me"). The tasks below are written against the
recommendation of each; where another option changes a task, the task says how.

## Authority

- `to-lead.md` "2026-10-10 15:37:31 BST — RULING: DP-M2 WITHDRAWN (my 14:37:13). FD-1589 row 8
  (errors.py:490) is NOT changed in the FD-1374 slice; remedy (c) in its own slice, owner
  WK-1178, before the exit demo. Neither (a) nor (b)", item 2, verbatim: *"Remedy (c), in its
  OWN slice (owner WK-1178), planned now and built before the exit demo if the lanes allow: an
  input-free marker exception in model-schema (an authored-message ValueError subclass carrying
  no input value), adopted by the authored validators, and allow-listed in
  pricing_core.safe_error; then row 8 renders authored messages and drops anything else. It
  needs a plan (one planner seat) and its DPs come to me."* Item 3: FD-1589 row 8's interim
  line is *"remedy (c), its own slice; interim: unchanged (requester-only exposure)"*.
- The lead's entry "2026-10-10 15:37:06 BST — Lead: DP-M2 CONSEQUENCE needs your call" in
  `from-lead-2026-10-09.md`: option (c) as first described, and the bare-app probe of the
  reverted implementation.
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
validator's message only when that message is input-free by construction, and shows a fixed text
naming the error code otherwise. "Input-free by construction" is a class: `InputFreeError`, a
`ValueError` subclass in `model-schema` whose every raise site is a string literal, held so by an
AST guard. Every authored model-schema validator message that is already a literal adopts it, so
an actuary still reads (for example) *"a Poisson model must declare an offset (FR-111 …)"*, byte
for byte as on `main`. A validator message that interpolates a value is dropped (the ruling's
"drops anything else"). The same rule is applied by `pricing_core.safe_error._validation_detail`,
so a stored sink and the 422 cannot disagree.

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
5. **The reverted implementation** (the FD-1374 slice, reachable objects, not on `main`):
   `40604029` (code-only text for `value_error`, `assertion_error`, `union_tag_invalid`;
   `_field_error_message` and `_INPUT_BEARING_ERROR_TYPES` in `errors.py`), `01d8bac0` (rebuilt
   from `ctx["error"]` through `safe_error_detail`), reverted by `8842b7c5`. Its two tests
   (`test_a_request_validation_422_carries_no_submitted_value`,
   `test_a_coded_validator_message_survives_the_422_sink`, in `backend/tests/test_error_sinks.py`,
   DB-backed through `api_client`) are this slice's starting point. **The brief's parked branch
   `draft/fd1589-row8-tests` does not exist** (`git ls-remote origin 'refs/heads/draft/fd1589*'`
   and `git branch --list '*1589*' '*row8*'` both empty at 15:4x BST); read the tests from
   `git show 40604029 01d8bac0 -- backend/tests/test_error_sinks.py`.

### The population (predicates verbatim, at `fe0b0627`)

- **253** `raise ValueError` lines in `packages/model-schema/src`:
  `git grep -c 'raise ValueError' -- packages/model-schema/src` (summed over 24 files).
- An AST walk agrees: **253** `ast.Raise` nodes whose `exc` is `ast.Call` with
  `func == ast.Name('ValueError')`, over `packages/model-schema/src/model_schema/*.py`. Of these:
  - **95** take a plain string literal (`isinstance(args[0], ast.Constant)` and `str`);
  - **158** take an f-string (`isinstance(args[0], ast.JoinedStr)`); none uses `.format`, `%` or a
    name. Of the 158, **1** interpolates only an upper-case module constant
    (`modelling.py:1142`, `{SURROGATE_RESPONSE_COLUMN!r}`; predicate: every `ast.Name` inside each
    `FormattedValue` matches `_?[A-Z][A-Z0-9_]*`); **157** interpolate a runtime value.
  - Of the 157, **15** interpolate only a closed vocabulary or a count (every `FormattedValue` is
    `len(...)` or an attribute named `value`, i.e. an enum member's value):
    `diagnostics.py:195 :648`, `jobs.py:142 :263 :265`, `metrics.py:189 :208`,
    `modelling.py:873 :920 :1719 :1844`, `objectives.py:806`, `perils.py:425`,
    `profiles.py:72 :79`. **142** interpolate a free value (a slug, a ref, a number, a step id).
  - By enclosing function: **231** sit in a function decorated with a pydantic validator (any
    decorator whose source contains `validator`): 95 literal, 136 f-string; **22** sit in helper
    functions, all f-strings (`ids.py`, `money.py`, `refs.py`, `objectives.py` `check` and
    `battery_is_exactly`, `rating.py` `check_model_reference_mode` and `_reject_float_type`,
    `permissions.py`, `validation.py`, `modelling.py` `_the_interaction_arm`,
    `_columns_match_the_type`).
- **Input-free by AST: 96 = 95 literal + 1 constant-only.** All 96 are inside validators, so each
  reaches a 422 as a `value_error` whose `ctx["error"]` is the instance. They are in 17 files:
  `approvals.py` 4, `audit.py` 1, `datasets.py` 5, `diagnostics.py` 2, `dislocation.py` 8,
  `jobs.py` 2, `metrics.py` 1, `modelling.py` 33 (32 + `:1142`), `objectives.py` 4, `perils.py` 4,
  `prediction.py` 3, `profiles.py` 1, `rating.py` 11, `regression.py` 9, `scoring.py` 1,
  `sub_graphs.py` 5, `transparency.py` 2.
- Outside model-schema, validators that raise `ValueError`: `backend/src/app` **1**
  (`config.py:198`, `Settings`, not a request model); `pricing_core` **0** (same AST walk over
  `rating`/`data` sources). Model-schema raises **0** `PydanticCustomError` and has **0** `assert`
  statements (`git grep -nE 'PydanticCustomError|^\s*assert ' -- packages/model-schema/src`), so
  `assertion_error` has no authored source to keep.
- The typed graph signals (`GraphCycleError`, `GraphUnresolvedRefError`, `graph_errors.py`) are
  5 further raises (`rating.py:575 :596`, `sub_graphs.py:82 :91 :151`), outside the
  `raise ValueError` predicate and outside this slice (row 4's sink maps them).

**The executor re-derives every number above at its base** (Task 0) and records both trees in
the LG; a slice that merged in between can move them.

## Acceptance Standard

1. `uv run pytest -q packages/model-schema/tests/test_input_free_raises.py` passes, and its
   broken-input case shows the guard reporting a planted interpolating `InputFreeError` and a
   planted literal `ValueError` (the red is seen in Task 1 before the adoption).
2. At the slice head, the guard's own census reports **0** literal or constant-only
   `raise ValueError(...)` sites in `packages/model-schema/src`, and every `raise InputFreeError(...)`
   takes a literal or a constant-only f-string. The LG records the adopted count (96 at
   `fe0b0627`, re-derived at the base).
3. `uv run pytest -q packages/pricing-core/tests/test_safe_error.py` passes, including the two
   new cases: a `ValidationError` from an `InputFreeError` keeps the authored text in
   `safe_error_detail`; one from a plain `ValueError` interpolating `_SENTINEL` does not carry it.
4. `uv run pytest -q backend/tests/test_errors.py` passes, including: (a) a request model's
   `InputFreeError` reaches the 422 as `"Value error, <text>"` exactly; (b) a plain
   `ValueError(f"… {value}")` with a sentinel reaches it as
   `"The value is not valid (VALUE_ERROR)."` with the sentinel absent from the whole body;
   (c) the real `GlmSpec` Poisson refusal reaches it with
   `"a Poisson model must declare an offset"` in the message; (d) an `int_parsing` control keeps
   pydantic's fixed text. Each was red first (a), (c) against `main`'s handler are green already,
   so their red is the Task 4 Step 2 run against the half-done handler; (b) is red on `main`.
5. `uv run lint-imports` passes (the new `pricing_core.safe_error → model_schema.input_free` edge
   is inside the `layering` contract).
6. `00-overview.md` §5.3 carries one dated paragraph stating the rule (Task 5), and
   `python3 scripts/audit-docs.py` exits 0 at the head.
7. The full two-half gate passes locally in a slot (`dev-commands`), at the slice head, with the
   tree named; `ModelSpecBuilderView.test.ts` is unchanged and passes.
8. The diff touches no file outside the write set below; `git diff --stat origin/main...HEAD`
   is in the LG.

## Global Constraints

- NFR-499 (`03-rating-engine.md:1416`; the brief's "(07)" is corrected here: the row is in `03`,
  and `07:321` and `06` cite it): *"quote inputs are never logged in full outside sampled traces,
  which are access-controlled"*, clarified to govern persistence; `safe_error.py:1-9` states the
  allow-list form: *"an exception's text is kept only where it is ours and known to be
  input-free; everything else is its type name and nothing more."*
- FR-450 (`07-platform.md:181`): RFC 9457 problem responses with stable `code`s; `00` §5.3 is the
  shape (`00-overview.md:344-366`). `FieldError` (`model_schema/problem.py:20-32`) is frozen,
  `extra="forbid"`, `message: str` required: a dropped message is a fixed text, never empty.
- ADR-703/ADR-704 via `.importlinter`: `model_schema` imports nothing but pydantic (`:36-51`);
  `pricing_core` imports no web library (`:16-34`).
- Never hand-write a shape that exists in `model-schema` (`CLAUDE.md` §2): the marker is defined
  once, in `model-schema`.
- RL-1263's contention rule (`docs/rulings/RL-01263-…md:89-100`) as amended by RL-1445: two
  concurrent build slices may not both change the same existing function or class; any other
  shared path serialises unless the dispatch record shows the check.
- The `compile.py` serial set and `pricing_core/rating/**` are **untouched** by this slice.
- Standing: red-first per task, closing acts in the slice PR (LG and SL `closed`), one PR per
  slice, barred word 0 in hunks, Co-Authored-By only.

## Write set

| File | Change | Task |
|---|---|---|
| `packages/model-schema/src/model_schema/input_free.py` | **new**: `class InputFreeError(ValueError)` | 1 |
| `packages/model-schema/tests/test_input_free_raises.py` | **new**: the AST guard + broken-input case | 1 |
| the 17 model-schema files of the population | `raise ValueError(` → `raise InputFreeError(` at the 96 sites; one import line each | 2 |
| `packages/pricing-core/src/pricing_core/safe_error.py` | `safe_validation_message`; `_validation_detail` uses it; docstring | 3 |
| `packages/pricing-core/tests/test_safe_error.py` | two cases | 3 |
| `backend/src/app/errors.py` | `_field_error_message`; `:499` uses it | 4 |
| `backend/tests/test_errors.py` | four cases | 4 |
| `docs/specs/00-overview.md` | one dated paragraph in §5.3 | 5 |
| `docs/ledgers/LG-…md`, `docs/roadmap.md` (SL 9956 status), `docs/INDEX.md` (generated) | closing acts | 6 |

**Not in the write set:** `model_schema/__init__.py` (the marker is imported by module path, the
`graph_errors` precedent, which also keeps this slice off the `__init__.py` hunks of SL-1557 and
SL-1559); `backend/tests/test_error_sinks.py` (its census does not cover `errors.py`:
`grep -n 'errors.py' backend/tests/test_error_sinks.py` has no `_SINKS` key); the frontend.

## Decision points (for the lead; none is picked here)

**DP-1 — the marker's name and home.**
(a) `model_schema/input_free.py`, `class InputFreeError(ValueError)`, imported by module path.
(b) Added to `model_schema/graph_errors.py` beside the graph signals.
(c) `AuthoredValueError` (the 15:37:06 entry's example name), in either home.
**Recommend (a).** The name states the property the allow-list relies on, not who wrote the text;
"authored" already names a different rule here (`pricing_core/rating/authored.py`, FR-244's
authored rating strings), and `graph_errors.py`'s docstring scopes it to FR-212's refusals.

**DP-2 — the 157 interpolating messages.**
(a) Leave them plain `ValueError`: their 422 message becomes the fixed text (the ruling's
"drops anything else"). The LG lists the 157 by file:line as the residual.
(b) (a), plus rewrite the 15 closed-vocabulary/count messages input-free (drop the value) and adopt
the marker for them (111 adopted).
(c) Rewrite all 157 input-free and adopt (253 adopted).
**Recommend (a).** It is the ruling's scope; (b) is cheap but each rewrite loses information a
reader has today; (c) is a large reword across every module, with merge contention on every open
slice in model-schema. If the lead wants guidance restored for a particular message before the
exit demo, it is a one-line rewrite, carried by the next slice touching that file.

**DP-3 — do `CodedError` and the marker unify?**
(a) Keep them separate; the allow-list recognises each by `isinstance`.
(b) `CodedError(InputFreeError)`: one root class for "input-free by construction".
**Recommend (a).** `CodedError`'s text is parsed as `CODE: message`
(`pricing_core/rating/score.py` `_batch_error_code`; `backend/src/app/api/score.py:320`); a parent
class whose text is not coded invites a misparse in the other direction, and (b) touches the rating
path for no behaviour change. With (a) this slice changes no rating code.

**DP-4 — does the 422 keep pydantic's "Value error, " prefix?**
(a) Keep `err["msg"]` verbatim for an allowed message: identical to `main` for every adopted
message; `ModelSpecBuilderView.test.ts:167` unchanged.
(b) Render `str(ctx["error"])` without the prefix: cleaner text; changes every adopted message and
that mock line.
**Recommend (a).** The remedy restores `main`'s rendering; the prefix is a separate UX choice.

**DP-5 — which pydantic error types the 422 rule governs.**
(a) The reverted `40604029` form, a deny-list: `value_error`, `assertion_error`,
`union_tag_invalid` are rebuilt (marker kept, else the fixed text); every other type keeps its
`msg` as on `main`.
(b) One allow-list shared with `_validation_detail`: a `msg` is kept only for a type in
`_FIXED_TEXT_TYPES` or a `value_error` whose `ctx["error"]` is an `InputFreeError`; every other
type gets the fixed text. A type joins `_FIXED_TEXT_TYPES` only with its sentinel case
(the existing mechanism, `test_safe_error.py:127`).
**Recommend (b).** It is the form `safe_error.py:7-9` argues for (a deny-list "misses the next
library"), and it puts the 422 and the stored sinks on one function, so they cannot diverge.
**Its cost, stated:** 422 messages of types outside the 30 (for example `uuid_parsing`,
`json_invalid`, `url_parsing`) become the fixed text. pydantic's `uuid_parsing` text quotes the
offending character, so at least one of them is a real echo. Under (a), Task 3 shrinks to the
`_validation_detail` change and Task 4's helper keeps the three-type set.

**DP-6 — where the rule is written in the spec.**
(a) One dated paragraph in `00-overview.md` §5.3 (the error model).
(b) A dated clarification on NFR-499 (`03:1416`).
(c) No spec text; FD-1589's row 8 disposition is the record.
**Recommend (a).** The 422 shape is §5.3's and platform-wide; NFR-499 is the rating engine's row.
No new requirement id is needed for a clarification of an existing shape.

**DP-7 — does the 422's fixed text keep the reverted form?**
(a) `f"The value is not valid ({TYPE})."`, with `TYPE` the upper-cased error type, as in
`40604029`.
(b) Pydantic-free fixed text without the code (`"The value is not valid."`), since
`FieldError.code` already carries it.
**Recommend (a).** Already probed, and it tells an analyst which check failed even where the
frontend shows only the message.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm the activation needs (below) by reading `origin/main`, and record the
  base sha in the LG.
- [ ] **Step 2:** Re-derive the population at the base with the predicates of §"The
  population". If it differs from `fe0b0627`'s, record both and work from the base's.
- [ ] **Step 3:** For every open slice branch that touches `packages/model-schema/src` (at
  `fe0b0627`: `origin/sl-1557-wk675-s3`, `model_schema/rating.py` and `__init__.py`;
  `origin/sl-1559-wk675-s4`, the same), list the functions both diffs change:
  `git diff -U0 origin/main...origin/<branch> -- packages/model-schema/src` against this
  slice's 96 sites. Any shared function is named in the dispatch record, and the later of the two
  merges main in and re-runs Task 1's guard (a literal `raise ValueError` the other slice adds
  then fails the guard, and is adopted).

### Task 1: The marker and its guard (red first)

**Files:** Create `packages/model-schema/src/model_schema/input_free.py`,
`packages/model-schema/tests/test_input_free_raises.py`.

**Interfaces:** Produces `model_schema.input_free.InputFreeError` (a `ValueError` subclass, no
new attributes) and `_census(source: str) -> tuple[list[int], list[int]]` (test-local: the lines
of a literal `ValueError` raise, the lines of a non-literal `InputFreeError` raise).

- [ ] **Step 1: Write the guard** (the test file; the marker does not exist yet, so the guard is
  written against its name only, by AST):

```python
"""An `InputFreeError`'s message is a literal, and every literal validator message is one
(NFR-499; FD-1589 row 8, remedy (c)).

`pricing_core.safe_error` keeps an `InputFreeError`'s text, so the rule holds only while every
raise site's message carries no value: a string literal, or an f-string over upper-case module
constants alone. And a literal `ValueError` is adopted, so authored guidance reaches a 422.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src" / "model_schema"
_CONST = re.compile(r"_?[A-Z][A-Z0-9_]*")


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


def _census(source: str) -> tuple[list[int], list[int]]:
    """(lines of a literal `raise ValueError(...)`, lines of a non-literal `raise InputFreeError(...)`)."""
    plain_literal: list[int] = []
    marker_interpolating: list[int] = []
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)):
            continue
        func, args = node.exc.func, node.exc.args
        name = func.id if isinstance(func, ast.Name) else None
        if name == "ValueError" and args and _input_free(args[0]):
            plain_literal.append(node.lineno)
        if name == "InputFreeError" and not (len(args) == 1 and _input_free(args[0])):
            marker_interpolating.append(node.lineno)
    return plain_literal, marker_interpolating


@pytest.mark.req("NFR-499")
def test_every_literal_validator_message_is_input_free_and_every_marker_is_literal() -> None:
    literal, interpolating = [], []
    for path in sorted(_SRC.glob("*.py")):
        plain, bad = _census(path.read_text())
        literal += [f"{path.name}:{line}" for line in plain]
        interpolating += [f"{path.name}:{line}" for line in bad]
    assert not interpolating, f"an InputFreeError must take a literal message: {interpolating}"
    assert not literal, f"raise InputFreeError, not ValueError, for a literal message: {literal}"


@pytest.mark.req("NFR-499")
def test_the_census_reports_planted_violations() -> None:
    planted = (
        "def f(value):\n"
        "    raise ValueError('a literal message')\n"
        "    raise InputFreeError(f'bad {value}')\n"
        "    raise InputFreeError(f'ok {_LIMIT}')\n"
        "    raise ValueError(f'keeps its value {value}')\n"
    )
    assert _census(planted) == ([2], [3])
```

- [ ] **Step 2: Run it and see the red by its cause.**
  `uv run pytest -q packages/model-schema/tests/test_input_free_raises.py`. Expected: the
  planted case PASSES; the census test FAILS on its **second** assert, listing the 96 sites
  (`modelling.py:1121`, the Poisson refusal, among them), with the first assert passing (no `InputFreeError` exists
  yet). A failure on the first assert, or a count other than Task 0's, is a plan defect: stop.
- [ ] **Step 3: Create the marker.**

```python
"""A validator refusal whose message is authored text with no submitted value in it
(NFR-499; FD-1589 row 8, remedy (c)).

`pricing_core.safe_error` keeps this exception's message where it keeps no other `ValueError`'s:
a request-validation 422 and a stored `ValidationError` detail both show it. That is safe only
because every raise site passes a string literal (or an f-string over module constants alone),
which `tests/test_input_free_raises.py` holds by AST. Raised inside a pydantic validator, it is
reported as `type == "value_error"`, with the instance at `errors()[i]["ctx"]["error"]`, like
`graph_errors`'s signals.
"""

from __future__ import annotations


class InputFreeError(ValueError):
    """A `ValueError` whose message is a literal: it names the rule, never the value."""
```

- [ ] **Step 4: Commit** (the guard stays red until Task 2; commit them together if the
  executor's workflow forbids a red commit, and say so in the LG).

### Task 2: Adopt the marker at the input-free sites

**Files:** the 17 files of the population. **Interfaces:** consumes `InputFreeError`.

- [ ] **Step 1:** In each file, add `from model_schema.input_free import InputFreeError` with
  the other first-party imports, and change each site the guard lists from
  `raise ValueError(` to `raise InputFreeError(`. The message text is not touched.
- [ ] **Step 2:** `uv run pytest -q packages/model-schema/tests/test_input_free_raises.py`:
  PASS. Then `uv run pytest -q packages/model-schema/tests`: PASS (`pytest.raises(ValueError)`
  and `except ValueError` still match a subclass; a failure here that names `InputFreeError` in
  a `type(...) is ValueError` or a class-name assertion is a finding to report, not to patch
  around).
- [ ] **Step 3:** `uv run ruff check packages/model-schema && uv run mypy` on the package; commit.

### Task 3: `pricing_core.safe_error` allow-lists the marker (DP-5 (b))

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

### Task 4: The 422 sink uses it (FD-1589 row 8)

**Files:** Modify `backend/src/app/errors.py` (`:485-510`); test `backend/tests/test_errors.py`.

**Interfaces:** consumes `safe_validation_message`.

- [ ] **Step 1: Write the failing tests.** A new fixture beside `failing_client` (`:27-48`),
  bare app, no database:

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
  `_spec` (`:10-19`) without its `offset`; if `GlmSpec` refuses it for a second reason at the base, mirror
  that test's builder rather than inventing fields. The `int_parsing` text is pydantic 2.13.5's
  (`uv.lock:1845-1846`); verify it in the red run and copy the observed text, never this line,
  if it differs.
- [ ] **Step 2: Run them; see each red by its cause.**
  `uv run pytest -q backend/tests/test_errors.py`. On `main`'s handler: the interpolating case
  FAILS because `_SENTINEL` is in the body (`"Value error, unacceptable value SENTINEL-…"`); the
  three others PASS (that is `main`'s behaviour, and the point of the remedy is to keep it). So
  the red for the authored and Poisson cases is taken **after** writing a `_field_error_message`
  that returns the fixed text for every `value_error` (the reverted `40604029` form, the
  regression the ruling names): both FAIL with the fixed text in place of the guidance. Record
  both runs in the LG. A red with any other cause is a plan defect: stop.
- [ ] **Step 3: Implement.**

```python
from collections.abc import Mapping
from typing import Any, Final

from pricing_core.safe_error import safe_validation_message


def _field_error_message(err: Mapping[str, Any]) -> str:
    """`FieldError.message` for one pydantic error, with no submitted value in it (NFR-499).

    `pricing_core.safe_error.safe_validation_message` keeps fixed-text types and an
    `InputFreeError`'s authored text; anything else, which a validator may have filled with the
    value it was given, is replaced by a fixed text naming the error type.
    """
    message = safe_validation_message(err)
    if message is not None:
        return message
    return f"The value is not valid ({str(err['type']).upper()})."
```

  and `:499` becomes `message=_field_error_message(err),`.
- [ ] **Step 4:** `uv run pytest -q backend/tests/test_errors.py`: PASS; `uv run lint-imports`
  and `uv run mypy`: PASS. Commit.

### Task 5: The spec line (DP-6 (a))

- [ ] **Step 1:** Append to `00-overview.md` §5.3, after the paragraph ending "corrected
  2026-08-14 when WK-658 implemented the propagation." (`:366`), one paragraph, following
  `spec-change`:

  *(Clarified 2026-10-XX, WK-1178, FD-1589 row 8 remedy (c), on the lead's entry "2026-10-10
  15:37:31 BST — RULING: DP-M2 WITHDRAWN …".)* A request-validation `422`'s `errors[].message`
  carries no submitted value (`03` NFR-499). It is the validator's own text only where that text
  is input-free by construction: a fixed-text error type, or a refusal raised as `model-schema`'s
  `InputFreeError`, whose every raise site is a literal. Any other message is
  `The value is not valid (<CODE>).` `errors[].code` and `errors[].field` are unchanged.

  (`XX` is the executor's commit date, from `date`.)
- [ ] **Step 2:** `python3 scripts/audit-docs.py`: exit 0. Commit.

### Task 6: The gate and the closing acts

- [ ] **Step 1:** The full two-half gate in a slot (`dev-commands`), at the head, tree named.
- [ ] **Step 2:** The LG: scope quoted from SL 9956; the base and head; both population
  derivations; the red runs of Tasks 1, 3, 4 by cause; the 157 residual sites by file:line
  (DP-2 (a)); the `--stat`. LG and SL 9956 `closed` in the slice PR.

## Sequencing, lane and merge-order slot

- **Lane:** a WK-1178 fix slice, **not** in the `compile.py` serial set and touching no
  `pricing_core/rating/**` file. It touches `backend/src/app/errors.py` in a function
  (`_handle_validation_error`, `:485-510`) different from the FD-1374 slice's registry line
  (`RATING_ERROR_CODES`, `:309`, its new entry at `:335` at `b3c0a939`, the `sl-1536` head at 15:46 BST); the brief
  requires that slice merged first, which also removes any doubt about its row-8 revert.
- **Contention:** the 96 sites are inside existing validators in 17 model-schema files.
  `SL-1557` and `SL-1559` (WK-675, `draft`) change `model_schema/rating.py` and `__init__.py` on
  their branches; this slice changes `rating.py`'s 11 literal sites and not `__init__.py`.
  Task 0 Step 3 names any shared function; RL-1263 serialises the pair where one exists.
- **Plan dependency, named:** after this slice merges, any slice that adds a literal
  `raise ValueError` in `packages/model-schema/src` fails Task 1's guard until it raises
  `InputFreeError`. The guard's message says so; a dispatch record for such a slice should
  name it.
- **Exit demo:** the ruling places it "before the exit demo if the lanes allow"; it holds no
  other slice and is held only by its activation needs.

## Size

About 330 changed lines: the marker 18; the guard 75; 96 one-line renames + 17 import lines;
`safe_error.py` about 25; `errors.py` about 20; tests about 110; the spec paragraph. One
executor session of roughly 3–4 hours including one full gate (derived from the line count and
the two comparable WK-1178 fix slices, not measured). Small.

## Activation needs

1. The FD-1374 slice (`SL-1536`, `PL-1535`) merged (the brief's need: it touches `errors.py`'s
   registry line, and carries the row-8 revert `8842b7c5`).
2. DP-1 to DP-7 ruled; PL 9955 and SL 9956 minted; this plan `active`.
3. The dispatch record carries Task 0 Step 3's check against every open model-schema slice
   (today `SL-1557`, `SL-1559`).
4. The lead's GO.

## Observed, not planned (for the lead)

- **The 422's `field` can carry an input key.** `errors.py:497` joins `err["loc"][1:]`, and for a
  dict-typed field pydantic's `loc` holds the submitted key; `safe_error._safe_location`
  (`:96-101`) replaces such a key with `<key>` for exactly that reason. FD-1589 row 8 names the
  `msg` only. Changing `field` touches FR-403's form-marking, so it is not folded in here; it is
  a candidate row for the auditor.

## Hand-off (not this plan's writes)

- FD-1589 row 8's dated lines (the interim line, 15:37:31 item 3; the disposition at merge): the
  lead's docs batch.
- The barred-word count of this file and its commit: 0 (`grep -ciE 'dep''uty'`).

## Self-review

1. **Spec coverage:** NFR-499 (Tasks 1–4), FR-450 / `00` §5.3 (Tasks 4–5), FR-403 (Task 4's
   control). Every limb of the ruling's item 2 has a task: marker in model-schema (1), adopted by
   the authored validators (2), allow-listed in `pricing_core.safe_error` (3), row 8 renders
   authored messages and drops the rest (4).
2. **Placeholders:** none but Task 5's `XX`, a date the executor writes.
3. **Names:** `InputFreeError`, `safe_validation_message`, `_field_error_message`,
   `_validation_detail`, `_FIXED_TEXT_TYPES`, `failing_client`, `create_app`, `GlmSpec`,
   `new_uuid7` are each grepped at `fe0b0627` or defined in a task above; the test helpers
   `_SENTINEL` and `_failure` in `test_safe_error.py` exist at `:40` and `:120`.
