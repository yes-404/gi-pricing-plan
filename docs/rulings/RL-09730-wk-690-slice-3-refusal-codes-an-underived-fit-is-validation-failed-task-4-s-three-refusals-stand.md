---
id: RL-9730
family: ruling
title: WK-690 Slice 3 refusal codes decided — an expression objective with no stored derivation is refused at fit 409 VALIDATION_FAILED, the code an underived certify gets; Task 4's three refusals stand, the create without applicability gains a §5.1 note, and the derive row cites its true source
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-04              # the mint date (check 31); ruled 2026-10-04
owner: decision-maker
tree: f68db62a01500b4120a21a0102442708f97f5e62
phase: P2
work: WK-690
slice: SL-1273
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1362, PL-1382, SL-1273, RL-1265, FR-144, FR-145, FR-150, FR-153, FR-202]
---

# RL 9730 (working id) — WK-690 Slice 3 refusal codes decided

## How this was ruled

- **Filed under working id 9730, allocated by the lead.** The id is renumbered at the mint
  turn (`python3 scripts/doc-id.py next --ref origin/main`); until then `audit-docs.py`
  check 31 reds this file by design. The frontmatter `id` field and the file name carry the
  hyphenated form only because the tooling parses them; the text names this record RL 9730,
  and every spec text below writes `<RL id>`, which reads as the minted id.
- **Ruled at effort `medium`** by the decision-maker session `dm-690`, started 2026-10-04
  18:11 BST; the first timestamp read in this session was `Sun Oct  4 18:15:46 BST 2026`
  (`TZ=Europe/London date`).
- **Mandate:** the lead's entry in `~/gi-pricing-plan.local/channel/to-lead.md` headed
  "2026-10-04 18:11:25 BST — DECIDED: rule NOW, in one WK-690 DM batch (dm-690, opus/medium;
  WK-690's DM for today), in parallel with Task 7; not at the slice audit", verbatim in the
  part that binds this record:

  > - **Scope, in one record:**
  >   1. The null-`derived` refusal: the status, the code (reuse a registered code where it fits; VALIDATION_FAILED is generic and owned by none) and the message.
  >   2. Task 4's three unplanned refusals, each with its status, code, the condition that triggers it, and the spec placement (02/06 rows, §5.1).
  >   3. Which side was wrong (plan or ruling) for each.
  >   4. Exact texts and placement. Nothing beyond these four.

- **The questions** are Delta 3 (b) and Delta 5 (a) of the dispatch record
  `~/gi-pricing-plan.local/handover/DISPATCH-WK-690-SL1273-2026-10-03.md` (entries dated
  2026-10-04 17:54:15 BST and 18:10:52 BST), and the Task 4 and Task 6 sections of the slice
  ledger LG 9731 (working id; its file is under `docs/ledgers/` on the S3 branch).
- **Evidence read**, read-only, no tests run: the S3 branch
  `origin/sl-1273-custom-objective-expression` at
  `c60888b7ecdcf84b07c8d4b450a84221b2aff25b` (cited below as `@c60888b7`), and `RL-1362` and
  `PL-1382` at `origin/main` `663433e4c38578239ca5abf15a716bef929e82cc`. `origin/main` moved to
  `f68db62a` (#1107) during the session; `git diff --stat 663433e4 f68db62a` over `RL-1362`,
  `PL-1382`, `02-modelling.md` and `backend/src/app/errors.py` is empty, so the citations hold at
  both.

## Ruled

### R1. An `expression` objective with no stored derivation that reaches a fit is refused 409 `VALIDATION_FAILED`, naming `/derive`. The ruling was silent on the code; the code picked the wrong one

**Decision.** `_compile_stored_expression`
(`packages/pricing-core/src/pricing_core/modelling/objectives.py:768`, `@c60888b7`) raises
`ObjectiveError` with code **`VALIDATION_FAILED`** (not `OBJECTIVE_KIND_NOT_ENABLED`) when
`objective.loss` or `objective.derived` is `None`. The existing GBM mapping carries the code
unchanged: `gbm.py:590` re-raises it as `GbmFitError(error.code, …)`, and
`worker/model_handlers.py:395` turns that into `PlatformError(exc.code, …, 409, str(exc))`.
So the fit job's stored error is **409 `VALIDATION_FAILED`**. The message is fixed under *Code
texts* below. No new code.

**Why.** `OBJECTIVE_KIND_NOT_ENABLED` is FR-150's flag refusal: it tells a client that the
workspace's `features.expression_objectives_enabled` is off. Here the kind is enabled, and the
missing thing is the derivation. `RL-1362` DP-S3-3 (2) already decided the code for this exact
condition, an `expression` objective whose `derived` is null, at the certify route: 409
`VALIDATION_FAILED`, the module's lifecycle-precondition code (`02` §5.1, "An **invalid
lifecycle transition** (FR-202) is `VALIDATION_FAILED` at `409`", `:2257` `@c60888b7`). It
refused a second code for that condition because "a code that names the wrong missing step
misleads the client that reads it". One condition takes one code, at certify and at fit. A new
code (`OBJECTIVE_NOT_DERIVED`) is refused. `RL-1362` DP-S3-1 says this path "is unreachable
through the lifecycle … and is defence for a hand-built artifact". A new client-visible code
for an unreachable state adds surface that nothing reaches. `OBJECTIVE_NOT_CERTIFIED` is
refused for the reason DP-S3-3 (2) gives. `VALIDATION_FAILED` is generic (`errors.py:393`,
`_GENERIC_ERROR_CODES`), so `PlatformError` accepts it. The FR-115 sweep
(`backend/tests/test_spec_hash.py`, `test_every_code_the_fit_path_can_raise_is_registered`)
parses only `GlmFitError`, `GbmFitError` and `EbmFitError` calls whose first argument is a
constant, so this `ObjectiveError` is outside it.

**The message names `/derive`** as certify's does. By the time an objective reaches a fit it
is past `draft`, and `/derive` refuses it there. So the message names the step that was
skipped, and does not tell the caller to run it now.

**Which side was wrong:** the code. `RL-1362` DP-S3-1 was silent on the code ("refused by
name"). The executor recorded the gap rather than choosing silently (LG 9731 Task 6,
deviation (2)), which is the right move under `CLAUDE.md` §0. The spec was silent too, and S1
below gives FR-144 the dated line.

### R2. Task 4's grammar refusal stands for a `SyntaxError` and for an `ExpressionError` from `loss` at create: 422 `OBJECTIVE_GRAMMAR_VIOLATION`, one `FieldError` on `loss`. The plan was incomplete; code and spec are right

**Decision.** Keep it unchanged. `_require_the_grammar` (`backend/src/app/platform/objectives.py:296`,
`@c60888b7`) is the trigger. It parses `loss` in the `objective` profile, after the contract has
accepted the shape. Its placement is in `create_objective`, after the permission and flag
checks and after `_validated`. Both exceptions give 422 `OBJECTIVE_GRAMMAR_VIOLATION`, with one
`FieldError(field="loss", code="OBJECTIVE_GRAMMAR_VIOLATION")`. The message begins
`line <L>, column <C>:`. That position is `ExpressionError.lineno` and `col_offset + 1`, or
`SyntaxError.lineno` and `offset` (already 1-based).

**Why it adds no rule.** `parse_expression` calls `ast.parse(expression, mode="eval")`
(`pricing_core/data/expressions.py:298`, `@c60888b7`), which raises a bare `SyntaxError` for text
that is not Python. Text that is not Python is outside FR-145's grammar. Without the mapping, a
create with `w * (y - ` answers 500. The refusal is `RL-1362` DP-S3-3 (1)'s refusal, given the
parser's second exception type. The position comes from the same source fields, and no
problem extension is added.

**The no-position case is ruled as built.** `ExpressionError` sets `lineno` and `col_offset`
together from one node. When both are `None`, the parser "could not know"
(`expressions.py:88-104`). The message then carries the reason with no `line …, column …:`
prefix. A position the parser does not have is not invented, and the 422, the code and the
`errors[0]` field are unchanged.

**Spec.** The FR-150 dated amendment on the branch (`02-modelling.md:214`, `@c60888b7`) already
says "A `loss` outside §4.6's grammar is refused 422 `OBJECTIVE_GRAMMAR_VIOLATION`, with
`line <L>, column <C>:` leading the message of one `errors[]` entry on `loss`". This covers
both exceptions. No text change.

**Which side was wrong:** the plan, by omission. `PL-1382` Task 4 Green says "mapping
`ExpressionError` to `OBJECTIVE_GRAMMAR_VIOLATION` per DP-S3-3", and the parser also raises
`SyntaxError`. Neither the ruling, the code nor the spec was wrong. The tests
`test_grammar_violation_is_422_with_the_position_in_errors` and
`test_grammar_violation_covers_text_that_does_not_parse`
(`backend/tests/test_custom_objectives_expression.py:386`, `:412`) already hold it.

### R3. A create of `kind: expression` without `applicability` is refused 422 `VALIDATION_FAILED`. The plan was silent; the code is right; the spec gains a §5.1 note

**Decision.** Keep the status, the code and the detail unchanged. The trigger is
`body.applicability` absent on an `expression` create. It is placed in `_validated`
(`backend/src/app/platform/objectives.py:927-934`, `@c60888b7`), after the permission and flag
checks and before the grammar check. The answer is 422 `VALIDATION_FAILED`, title "An expression
objective states its applicability".

**Why it adds no rule.** `CustomObjective.applicability` is required by the contract
(`docs/contracts/schemas/generated/custom-objective.schema.json` `@c60888b7`, `required`:
`id`, `slug`, `version`, `applicability`). The only default the create path supplies is the
template's own block (§4.5, "Each template declares its `applicability` block (FR-153)"), and
an `expression` objective has no template. Without the guard, `TEMPLATE_APPLICABILITY[None]`
raises `KeyError`, which is a 500. 422 `VALIDATION_FAILED` is what `_validated` already answers
for every other contract refusal (`objectives.py`, `except ValueError` in `_validated`). The
request body is malformed, and nothing about the lifecycle is involved.

**Spec.** The OpenAPI `CreateCustomObjective` has `applicability` optional, because a template
defaults it. So a client reading the contract cannot see that an `expression` create requires
it. S2 below puts that on the §5.1 create row.

**Which side was wrong:** the plan, by silence. `PL-1382` Task 4 does not say where an
`expression` objective's applicability comes from. No test holds this refusal at
`@c60888b7`; the delta adds one.

### R4. A second derive is refused 409 `VALIDATION_FAILED`. The plan was incomplete; the code is right; the derive row's citation is corrected

**Decision.** Keep the status, the code and the detail unchanged. `derive_objective`
(`backend/src/app/platform/objectives.py:323`, `@c60888b7`) is the trigger. It answers 409
`VALIDATION_FAILED` when `row.status != draft` or `row.derived is not None`. It is placed after
the route's `model:fit` and author checks and the flag, and before `derive()` runs.

**Why it adds no rule.** Task 2's storage trigger makes `derived` writable once, from NULL.
An already derived draft is therefore a third state in which the act cannot happen, alongside
the plan's "non-`draft` or template". `02` §5.1's rule covers it: "the request was well formed,
the artifact's state is what makes it impossible" (`:2257`), which is `VALIDATION_FAILED` at
409. Without the guard the database refuses the write, and the client gets a 500 (LG 9731
Task 4, broken-input proof, `assert 500 == 409`). An idempotent 200 that returns the stored
block was considered and refused. It would make a second `custom_objective.derived` event
either false or missing, and the detail already tells the caller the way forward ("create the
next version to change the loss").

**Spec.** The branch's derive row (`02-modelling.md:1844`, `@c60888b7`) already states the
three refusals. It attributes them to `RL-1362`, which ruled none of them: the template and
non-`draft` refusals are `PL-1382` Task 4's, and the already derived one is this record's. S3
below corrects the citation only.

**Which side was wrong:** the plan, by omission. `PL-1382` Task 4 Green lists "a non-`draft`
or template objective" and not the write-once state that its own Task 2 creates. The test
`test_derive_refuses_a_template_objective_and_a_second_derivation`
(`test_custom_objectives_expression.py:359`) already holds it.

## Code texts, with placement

**C1 (R1) — `packages/pricing-core/src/pricing_core/modelling/objectives.py`,
`_compile_stored_expression`** (`:786-792` `@c60888b7`). The `raise ObjectiveError(…)` under
`if objective.loss is None or stored is None:` becomes, byte for byte:

```python
        raise ObjectiveError(
            "VALIDATION_FAILED",
            f"objective {objective.slug}@{objective.version} has no stored derivation to "
            "compile: an expression objective is fitted from the derivation an Approver "
            "read, never re-derived (FR-144), and is derived on its draft at "
            "POST /api/v1/custom-objectives/{id}/derive before it is certified.",
            terms=[objective.slug],
        )
```

Only the first string is an f-string, so `{id}` is literal. The message holds no input value
(FD-1219). The `template is None` guard in `compile_objective` (`:742`) is not this record's.
Its `OBJECTIVE_KIND_NOT_ENABLED` is unreachable (`# pragma: no cover - the contract refuses
this`), and it is unchanged.

## Spec texts, with placement

**All three are carried by Slice 3** in the Task 8/9 executor's commit that applies C1 and the
tests, so that spec, code and tests land in one commit (`CLAUDE.md` §2). They are not edited on
`main` by this record, because S2's and S3's targets exist only on the S3 branch. `<RL id>` reads
as this record's minted id, and `<Task date>` is the date of the commit that applies each text.
The executor applies each text byte for byte. Any executor wording is a stop.

**S1 (R1) — `02` FR-144, appended to the end of its Requirement cell**
(`docs/specs/02-modelling.md:208` `@c60888b7`). Place it after
`` and the node-count and depth limits enforced. `` and one space, before the closing ` |`.
Nothing is struck:

    **Amended <Task date> (`<RL id>` R1; `RL-1362` DP-S3-1): a fit compiles the stored `derived` block and never re-derives from `loss`.** An `expression` objective whose `derived` is null that reaches a fit is refused 409 `VALIDATION_FAILED` on the fit job, the code an underived certify gets (§5.1 certify row), with a message naming the objective and `POST /api/v1/custom-objectives/{id}/derive`. The lifecycle cannot reach this state, because certify refuses an underived objective; the refusal guards a hand-built artifact.

**S2 (R3) — `02` §5.1, the create row** (`docs/specs/02-modelling.md:1841` `@c60888b7`). Replace the row

    | `POST` | `/api/v1/custom-objectives` | **201** Create → `draft` (FR-142) |

with

    | `POST` | `/api/v1/custom-objectives` | **201** Create → `draft` (FR-142). An `expression` objective names its `applicability`, because it has no §4.5 template to default from; a create without it is refused 422 `VALIDATION_FAILED` (**added <Task date>, `<RL id>` R3**) |

**S3 (R4) — `02` §5.1, the derive row's citation** (`docs/specs/02-modelling.md:1844`
`@c60888b7`). In that row only, replace

    (**built 2026-10-04, WK-690 Slice 3, `RL-1362`**)

with

    (**built 2026-10-04, WK-690 Slice 3, `PL-1382` Task 4; the already derived refusal ruled by `<RL id>` R4**)

**Error codes: none is new.** `VALIDATION_FAILED` is generic (`errors.py:393`);
`OBJECTIVE_GRAMMAR_VIOLATION` is registered (`errors.py`, `MODELLING_ERROR_CODES`) and is in
`02` §5.1's owned list without its marker (`:2112`, `@c60888b7`). No catalogue changes.

## Which side was wrong, per item

| Item | Plan | `RL-1362` | Code | Spec | Disposition |
|---|---|---|---|---|---|
| R1 null `derived` at fit | — | silent on the code | **wrong code** | silent | C1, S1 |
| R2 `SyntaxError`/`ExpressionError` → 422 | incomplete (`ExpressionError` only) | right | right | right (FR-150 amendment) | none |
| R3 no `applicability` → 422 | silent | — | right | silent | S2; new test |
| R4 second derive → 409 | incomplete (write-once state omitted) | — | right | right, miscited | S3 |

## What it obliges

WK-690 Slice 3 builds this. `PL-1382` is frozen and is not edited. The lead's dispatch record of
SL-1273 carries the delta. It binds the Task 8/9 executor once this record is minted, and it
lands before the minted-head gate:

> **Delta (RL 9730 minted id substituted): the refusal codes.** In one commit, red first on each changed test, each red quoted in LG 9731 with the broken input named.
> 1. **R1.** In `packages/pricing-core/tests/test_objectives.py`, `test_compile_dispatch_refuses_an_underived_expression_objective_by_name` binds `pytest.raises(…) as refused` and adds `assert refused.value.code == "VALIDATION_FAILED"` and `assert "/derive" in str(refused.value)`. Red at `c60888b7` on the code assertion (`'OBJECTIVE_KIND_NOT_ENABLED' == 'VALIDATION_FAILED'`). Apply C1, then S1.
> 2. **R2.** No change.
> 3. **R3.** New test `test_an_expression_objective_without_applicability_is_refused_422` in `backend/tests/test_custom_objectives_expression.py`, `@pytest.mark.req("FR-153")`. With the flag on and the author caller, it posts `_expression_body()` without `applicability`, and asserts 422, `code == "VALIDATION_FAILED"`, and no objective with that slug in `GET /api/v1/custom-objectives?slug=…`. The code already exists, so the red step is the broken-input proof: with the `if template is None:` branch removed from `_validated`, the create answers 500 and the test fails. Apply S2.
> 4. **R4.** Apply S3. No test change.
> 5. No new error code. No file beyond `objectives.py` (pricing-core), the two test files and `02-modelling.md`.

## Not ruled here

Out of the mandate's four items, so recorded for the lead and not decided. An `ExpressionError`
raised by `derive()` itself at `/derive` (`objectives.py:353-363` `@c60888b7`; LG 9731 Task 4,
deviation (2)) answers 422 `OBJECTIVE_GRAMMAR_VIOLATION` on `loss`, and its message has no
`line …, column …:` prefix. `02` §5.1's derive row does not list it. It is a fourth Task 4
refusal beyond `RL-1362` DP-S3-3's three, and the lead may route it to a decision-maker.

## Acceptance — the violation that must become detectable

1. **An underived fit reported as a disabled flag.** R1's test fails on `.code` while the
   refusal carries `OBJECTIVE_KIND_NOT_ENABLED`.
2. **An `expression` create without applicability answered 500.** R3's test fails with the
   `_validated` branch removed.
3. **A refusal row citing a ruling that did not make it.** S3's text names `PL-1382` Task 4
   and this record. A later edit that restores the `RL-1362` attribution contradicts both.

Drafted as working id 9730, 2026-10-04.
