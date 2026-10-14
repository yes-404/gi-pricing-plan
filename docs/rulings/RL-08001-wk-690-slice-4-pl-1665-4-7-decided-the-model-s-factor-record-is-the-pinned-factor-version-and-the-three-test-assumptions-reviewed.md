---
id: RL-8001
family: ruling
title: WK-690 Slice 4, PL-1665 4.7 decided — the fitted Model's factor record is the Factor version its spec pins, proven by a test of the chain and not copied into the fit result; the seat's three test assumptions reviewed (a confirmed, b corrected, c confirmed with four consequences)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-14
owner: decision-maker
tree: 36e2610ab8135bc3b3563464e7f5f719713b168b
phase: P2
work: WK-690
slice: SL-1274
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1665, PL-1621, RL-1615, RL-1362, SL-1274, FD-1619, OQ-1617, FR-44, FR-87, FR-95, FR-96, FR-97, FR-228, NFR-484]
---

# RL-8001 — WK-690 Slice 4: PL-1665 4.7 (RL-1615 need 4.5 (c)) decided, and the seat's test assumptions reviewed

*Disclosure: drafted under **working id RL 8001**, reserved by the lead (team-lead) on
2026-10-14 (`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-14 09:38:35
BST": "RESERVED working id RL 8001 (first in the 8000–8299 range, the maintainer's 09:33:32) =
WK-690 S4 ruling on PL-1665 4.7 / RL-1615 need 4.5(c) ("the fitted Model's factor record
carries the expression text" — no such record exists) + review of the seat's test assumptions
(a) declared columns = source_columns, (b) loose position assert, (c) Banding.column
optional."). The lead mints it.*

## How this was ruled

- **The question is the lead's referral**, in the lead's entry "2026-10-14 09:38:35 BST — Lead:
  SL-1274 PREP DONE (executor-sl1274-prep) …" in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`,
  verbatim in the part relied on: *"OPEN DP (not the seat's, not the lead's to pick): PL-1665
  4.7 — options (A) FitResult.factor_expressions, (B) Model API embeds pinned Factors, (C) pin
  alone suffices; seat recommends (A). → dm-wk690-47 at effort high, RL 8001 reserved."*
- **The effort is the maintainer's (by delegation) condition**, the entry "2026-10-14 09:23:02
  BST — READ-IN OK …" in `~/gi-pricing-plan.local/channel/to-lead.md`, item 1, verbatim: *"The
  decision-maker for DP-P1 runs at medium unless its ruling writes spec text; if it does, it is
  a separate CLI at --effort high, verified by its transcript's perTurnEffort."* This record
  writes spec text. The lead verified the seat in its entry "2026-10-14 09:39:59 BST", item
  (3): *"dm-wk690-47: transcript 19e6eb86 "perTurnEffort":"high" x17, medium x0,
  claude-opus-5-5 x17 → VERIFIED HIGH"*.
- **The working id is in range**: the maintainer's (by delegation) entry "2026-10-14 09:33:32
  BST — working-id range ruling + seat fill", item 1: *"Working-id range: 8000–8299 from the
  next reservation."*
- **This record rules a plan's decision point and never edits the plan** (`document-ids.md`
  §1.6, PL row). `PL-1665` says *"Decision points: None open"*; 4.7 became one when the seat
  found that the record it names does not exist. The words being ruled are the maintainer's,
  `RL-1615` lines 34 and 95-96: *"(c) interim, S4's evidence carries the expression text in
  the Model's factor record, as the memo says."* The memo
  (`~/gi-pricing-plan.local/handover/dm-wk690-dps4-1-2026-10-11.md`, §4) gives the purpose:
  *"so a reviewer can compare the two copies."* It names no field. **What "the Model's factor
  record" is, is this record's reading**, and the maintainer may override it.
- **Written 2026-10-14 by `date`** (09:47:59 BST at the last fact check), by the
  decision-maker seat `dm-wk690-47`. Every fact below was read at `origin/main`
  `36e2610ab8135bc3b3563464e7f5f719713b168b`, by symbol with its line. The seat's evidence is
  `origin/sl-1274-wk690-s4-factor-expression` at `2e163cb73e0d1d1171a7ff32339fa02991083f26`:
  three test files, `git diff --stat origin/main...` → 654 insertions, no other change.
- **Two facts were run, not only read**, on 2026-10-14 at about 08:45Z, while gate-1 was held
  by another seat. Each was one call to the parser, not a sweep. The interpreter was the root
  checkout's `.venv` (Python 3.13.5) over this worktree's `packages/*/src`. CI runs 3.12, so
  the `SyntaxError` offset below is not asserted exactly (§(b)).

## Locators — read at `36e2610a`

| Fact | Where |
|---|---|
| A Model pins its Factors by id: `factors: tuple[UUID, ...]` | `packages/model-schema/src/model_schema/modelling.py` `ModelSpecCommon` `:835` |
| `FitResult` has no per-factor field; the arms are `GlmFitResult`, `GbmFitResult` and `EbmFitResult` | same file `:1561`, `:1631`, `:1790`; the union `:1954` |
| One `factors` row is one version of one slug, with its own id | `backend/src/app/db/models.py` `FactorRow` `:1315-1338` (`id` default `new_uuid7`; `uq_factors_slug_version`) |
| The Factor body is stored whole, so a new `Factor` field is stored with no schema change | `backend/src/app/platform/modelling.py` `create_factor` `:221-264` (`body = factor.model_dump(…)`) |
| The fit, prediction and rating load the pinned Factors by id | `load_factors`, `backend/src/app/platform/modelling.py` `:286`; called by the model worker (`backend/src/app/worker/model_handlers.py` `:202`, `:672` and others), prediction (`backend/src/app/platform/prediction.py` `:130`, `:511`) and `rating_algorithms.py` `:140` |
| A fitted Model's `spec` cannot change | `models_fit_immutable`, latest body `backend/migrations/versions/9e4c7b21fa08_diagnostics_id_immutable.py` `:66-85` (`OR NEW.spec IS DISTINCT FROM OLD.spec`) |
| The `factors` table is **not** append-only | `backend/migrations/versions/b2c3d4e5f6a7_model_fit_immutable.py` `:89` (`GRANT SELECT, INSERT, UPDATE ON models, factors`); no trigger on `factors` in any migration; `e1f2a3b4c5d6_artifact_row_triggers.py` `:48`, `:50` list six other tables; `backend/tests/test_artifact_immutability.py` `APPEND_ONLY_TABLES` `:38-52` has no `factors` |
| `bandings` and `groupings` are append-only | `c3d4e5f6a7b8_modelling_bandings_and_groupings.py` `:111-112` (`REVOKE UPDATE, DELETE`) |
| A test edits a `factors` row in place | `backend/tests/test_fr240_governance.py` `_make_control` `:247-256` |
| The read routes | `backend/src/app/api/models.py` `list_factors` `:303-323` (`GET /factors`, `?dataset_id=`), `get_model` `:626-653` (`GET /models/{slug}`); there is no `GET /factors/{id}` |
| The one positioned-error form | `RL-1362` DP-S3-3, item 1; built as `_require_the_grammar`, `backend/src/app/platform/objectives.py` `:297-322` |
| A request-validation 422 keeps a validator's message only for an `InputFreeError` | `backend/src/app/errors.py` `_field_error_message` `:494-505`; `packages/pricing-core/src/pricing_core/safe_error.py` `safe_validation_message` `:145-161` |
| The `factor` profile needs bound symbols, and refuses an unbound name with its position | `packages/pricing-core/src/pricing_core/data/expressions.py` `parse_expression` `:288-304`; the refusal text `:268` |
| `referenced_columns` cannot run in the `factor` profile | same file `:307-321`: it calls `parse_expression` with no `symbols` |
| `Banding.column` is required | `modelling.py` `Banding` `:359`; contract `docs/contracts/schemas/banding.schema.json` `:7` (`required`) |
| `bandings.column_name` is `NOT NULL` and is written from `banding.column` | `c3d4e5f6a7b8…` `:53`; `BandingRow` `models.py` `:1358`; `transformations.py` `:288`. No line in `backend/src` reads it |
| Every other reader of `Banding.column` | `transformations.py` `:179` (evaluate), `:304` (`banding.created`); `pricing_core/modelling/bandings.py` `:458`, `:482`, `:512`; `pricing_core/modelling/factors.py` `:195`; `pricing_core/rate_tables/weights.py` `:82`, `:107-115` |

**The probes.** `parse_expression(t, GrammarProfile.FACTOR, symbols=frozenset({'driver_age',
'vehicle_power'}))` gave:

| Text | Result |
|---|---|
| `driver_age * vehicle_value` | `ExpressionError`, line 1, `col_offset` 13: *"'vehicle_value' is not a bound symbol or declared parameter"* |
| `driver_age * 2 + frobnicate(driver_age)` | `ExpressionError`, line 1, `col_offset` 17: *"'frobnicate' is not an allowed function; …"* |
| `driver_age % 2` | `ExpressionError`, line 1, `col_offset` 0 |
| `driver_age > 40` | `ExpressionError`, line 1, `col_offset` 0 |
| `driver_age * (vehicle_power` | `SyntaxError`, line 1, offset 14: *"'(' was never closed"* |
| `3.5` | parses |

`referenced_columns('where(driver_age > 40, region, alt)', profile=GrammarProfile.FACTOR)`
raised `ValueError: the objective and factor profiles need their bound symbols`.

## `CLAUDE.md` §0 — spec and code

No disagreement is resolved here. `02` §4.1 prints `expression` on `Factor`, and the type does
not have it; that is recorded (FR-208, OQ-582) and `RL-1615`'s 4.1′ closes it. `02` §4.4 prints
`factors` as `{factor_id, factor_version}` objects, and the type is a tuple of ids; that is
recorded as **UNRECONCILED** in `docs/contracts/schemas/model-spec.schema.json`'s own
`factors` description, and this record does not touch it. The id the code pins is a
per-version row id, so the pin identifies one version either way.

## DP 4.7 — ruled: (C), with a stated variant

**Ruled (C′).** "The fitted Model's factor record" is **the Factor version the Model's spec
pins**. `Model.spec.factors` holds the id of one `factors` row, which is one version of one
slug. After `PL-1665` 4.1′, that Factor carries `expression`. **No new field is added**: not
on `FitResult`, not on `Model`, and not on the Model API response.

**The variant: 4.7's test proves the chain, not the field.** In one test, over HTTP:

1. A Model at `fitted` or beyond whose spec pins an `expression` Factor. The slice chooses how
   it gets one: a fit, or the suite's existing fitted-model seeding.
2. `GET /api/v1/models/{slug}`: `spec.factors` contains that Factor's id.
3. `GET /api/v1/factors?dataset_id=…`: the Factor with that id has `expression` equal, as a
   string, to the text that was posted.
4. A version 2 of the same slug is created with a different `expression` (with a Banding whose
   `source_expression` matches it). Version 2 has a different id. The Model's pinned id still
   returns version 1's text.

Step 4 is what makes this evidence and not only a lookup. A pin that followed the slug would
pass steps 1 to 3 and fail step 4. The `LG-` cites FD-1619 and OQ-1617 as the owners of the
parity check itself, as `PL-1665` 4.7 already says.

### Why (C′)

- **The text has one home after 4.1′, and it is the declared artifact.** `PL-1621`'s S4 row
  says *"Declared: the `factor` profile (`02:940`), with the text stored on the Factor"*.
  Model and rating definitions are declarative artifacts (`CLAUDE.md` §2). The Model refers
  to the Factor by a pin, and the `models_fit_immutable` trigger stops that pin from changing
  once the Model is fitted.
- **The thing being evidenced is two copies with no agreement check** (FD-1619). A copy in the
  fit result would be a third copy of the same formula. OQ-1617's option (a) is to *"generate
  the ZEN step from the stored expression"*. Its design should read one stored expression, not
  choose between two.
- **Scoring reads the pinned Factor, not the fit result.** The fit and the prediction path
  resolve the Factors loaded by id from `spec.factors`. A copy in `FitResult` would describe
  the fit, while the Factor drives the price. If the two ever differed, the copy would be the
  one that is wrong about the price.

### Rejected

- **(A) `FitResult.factor_expressions: dict[slug, str]`.** A fit result is what a fit returns
  (`GlmFitResult`'s docstring, ADR-705), and the expression is the fit's input. It changes
  three arms, not two (`EbmFitResult` too), the contract and the generated client. It is keyed
  by slug while the pin is by id. "It travels with the artifact" buys nothing: a Model cannot
  be scored without its pinned Factors. Its one real advantage is that the copy would sit
  under the `models` trigger and would survive a direct edit of a `factors` row. That is an
  argument for protecting `factors` rows (next section), not for copying them, because the
  copy would not stop the edited row from pricing.
- **(B) The Model API response embeds the pinned Factors.** Derived and not stored, so it
  passes `CLAUDE.md` §2 if it reuses `Factor`. But it is a new interface on every Model read,
  for something two existing reads already answer. It changes `02` §5.1's model response and
  every generated client. If an authoring view needs it, that view's plan specifies it.
- **(C) as offered, "the pin alone".** Taken only with the variant above, and with its
  premise stated as it is, not as assumed (next section).

### The premise (C′) rests on, and a gap found

The seat's option (C) says *"a Factor version is immutable"*. That is true of the
application and **not of the database**. The `factors` table grants `UPDATE` to `gip_app` and
carries no trigger. `bandings` and `groupings` have `UPDATE` and `DELETE` revoked.
`test_artifact_immutability.py` derives its append-only set from the grants, so `factors`
falls outside it unnoticed. FR-44's first sentence is *"Every artifact table carries both
layers"*. No application path updates a `factors` row: every `FactorRow` use in `backend/src`
is an insert or a select, by the predicate `git -C <tree> grep -n 'FactorRow' -- backend/src`
at `36e2610a` (class definition, `select(FactorRow…)` and one `FactorRow(` constructor).
`test_fr240_governance.py` `:247-256` does edit one in place, *"the way a later edit would"*.

A direct edit of a `factors` row changes how every Model pinned to that row scores, while the
pin stays the same. That is `RL-1615`'s stale-band class one level up. **It is a present gap
on main, independent of S4.** It is routed, not fixed here:

- **A finding**, for an auditor to file (the auditor proposes the severity). The lead
  allocates its id. The proposed owner is WK-1178, P2's open maintenance Work, as for FD-1619.
- **The fix, proposed:** one migration that revokes `UPDATE` and `DELETE` on `factors` from
  `gip_app` and `PUBLIC` and attaches `artifact_append_only`'s row and `TRUNCATE` triggers, as
  `e1f2a3b4c5d6` did for six tables. `APPEND_ONLY_TABLES` gains `factors`.
  `_make_control` is rewritten to create a `control` version instead of editing one.
- **Where it lands is the lead's** (write set and size). The recommendation is a fix row of its
  own, not S4: S4 is already about 1.5 slices and on rung 6, and the fix changes a `03`
  governance test.
- **4.7 does not wait for it.** The 4.7 test is valid against the application. This record
  states the premise rather than asserting it.

### Does this change a spec data contract?

**No.** The one new field is `Factor.expression`, which is `RL-1615`'s 4.1′ disposition.
One note goes into `02` §4.8, so that a reader knows where a fitted Model's formula is read
and does not add a copy. The slice applies it, through `spec-change`, in the code's commit:

> **Noted <the slice's commit date> (`RL-8001`): where a fitted Model's factor formula is
> read.** A Model's `spec.factors` pins Factor versions by id, and once the Model is fitted the
> pin cannot change (the `models_fit_immutable` trigger covers `spec`). The formula of an
> `expression` Factor is that Factor's `expression` (§4.1), read through the pin:
> `GET /api/v1/models/{slug}` names the id, and `GET /api/v1/factors` returns the Factor with
> its `expression`. Neither the Model nor its `fit_result` stores a copy. A second copy of the
> formula is the defect FD-1619 records, and a reviewer who compares a Rating Version's
> restatement with the model reads the text the model was fitted and is scored with.

## The seat's three assumptions

### (a) "Declared columns" = `source_columns` — **confirmed**, with the mechanism stated

FR-95 says *"evaluated over dataset columns only"*. `PL-1268` Slice 4 says *"over the declared
dataset columns only (FR-95)"*. `RL-1615`'s creation row says *"an undeclared column
(FR-95)"*. A Factor is defined against a Dataset, not a version (FR-87), so at creation the
only declaration there is to check against is the Factor's own `source_columns`.

**The check is the parse itself, not a second walk.** The `factor` profile cannot be parsed
without bound symbols (`parse_expression` `:296-297`), and it refuses an unbound name with its
position (the first probe). So the creation check is
`parse_expression(expression, GrammarProfile.FACTOR, symbols=frozenset(source_columns))`.
"Referenced ⊆ declared" holds because the parse enforces it.

Two consequences:

- `referenced_columns(…, profile=GrammarProfile.FACTOR)` raises `ValueError`, because it
  passes no symbols. `RL-1615`'s accepted cost (i) has the propose and evaluate paths *"read
  only `referenced_columns`"*. Those paths must parse with the Factor's `source_columns` as
  symbols, or `referenced_columns` gains a `symbols` argument. Either way there is one parser.
- **Not tightened to equality.** A declared column that the expression does not read is not
  refused. It can only fail loudly: FR-87 refuses a Dataset Version that lacks it. An
  expression that reads no column (`3.5`) passes this check and is refused as certainly numeric
  (FR-210), as the seat's parametrisation expects.

**FR-95 text, appended by the slice** (exact):

> *(Clarified <the slice's commit date>, `RL-8001` (a): "dataset columns only" means the
> Factor's own `source_columns`. They are the bound symbols of the `factor` profile's parse,
> so a name the expression reads that is not among them is refused at creation with its
> position, in `RL-1362` DP-S3-3's form (one field error on `expression`, its message
> beginning `line <L>, column <C>:`). FR-87 then refuses at resolution a declared column that
> the Dataset Version lacks. A declared column that the expression does not read is not
> refused.)*

### (b) The position, asserted loosely — **corrected**

The seat asserts that any of `"position"`, `"column"` or `"col_offset"` appears anywhere in
the problem body. Any message that names a column passes that, with no position in it, so the
assertion cannot fail on the defect it guards. The platform already has **one** positioned
form: `RL-1362` DP-S3-3, item 1, *"a `message` that begins `line <L>, column <C>:` from
`ExpressionError.lineno` and `col_offset` (1-based column)"*, built in `_require_the_grammar`.
`PL-1665` 5.3′ cites it for S5. S4 uses the same form:

- **The answer:** 422 with `code` `VALIDATION_FAILED` (the seat's `_refusal_text` already
  asserts that). `errors` contains one `FieldError` with `field` `"expression"`, `code`
  `"VALIDATION_FAILED"`, and a `message` matching `^line \d+, column \d+: `. No new error code
  is added, because a new code needs an entry in `02` §5.1's owned-code list.
- **Where it applies:** the parser's refusals, which are the parse error, the three grammar
  refusals (`%`, a bare comparison, an unknown function) and the undeclared column. It does
  not apply to the FR-210 refusal or to the `source_expression` mismatch, which are about the
  whole expression or the pinned Banding. Those keep the seat's assertions.
- **One exact position**, from an AST-positioned refusal that is not at column 1:
  `driver_age * 2 + frobnicate(driver_age)` → the message begins `line 1, column 18:`.
  The undeclared column: `driver_age * vehicle_value` → it begins `line 1, column 14:` and
  names `vehicle_value`. The `SyntaxError` case asserts the form only, because its offset comes
  from CPython's tokenizer and the probe ran on 3.13.5.
- **The mechanism this forces:** the refusal is raised as a `PlatformError` in the platform
  layer, as `_require_the_grammar` does, and not from a pydantic validator on `FactorCreate`.
  The request-validation 422 keeps a validator's message only for an `InputFreeError` raised
  from a literal. A message carrying a position or a column name would be replaced by *"The
  value is not valid (VALUE_ERROR)."* `model-schema` cannot import the parser in any case.

### (c) `Banding.column` becomes optional — **confirmed**, with four consequences the reds do not show

`RL-1615` DP-S4-1: *"Exactly one of `Banding.column` and `Banding.source_expression` is set."*
So `column` is `str | None`, as the seat's tests have it. Each of the following lands in S4
with the change:

1. **A migration.** `bandings.column_name` is `NOT NULL`, and `create_banding` writes
   `banding.column` into it. Without `ALTER COLUMN column_name DROP NOT NULL`, the seat's
   positive test answers 500, not 201. No line in `backend/src` reads the column. A DDL change
   is not refused by the row trigger. **The S4 write set gains one Alembic migration.**
2. **The hand-authored contract.** `banding.schema.json` lists `column` in `required` (`:7`).
   It drops it, gains `source_expression`, and states the exactly-one rule. The slice reads
   `.claude/skills/contract-guard` before it edits the file.
3. **Every reader of `Banding.column` narrows** (`mypy --strict` forces this): the evaluate
   path (`transformations.py` `:179`), `banding.created`'s after-state (`:304`, where `column`
   is null and `source_expression` is added, `PL-1665` 4.4′), `check_banding`
   (`bandings.py` `:458`, `:482`, `:512`, which reads the evaluated result for an expression
   Banding), and `_column_matches` (`factors.py` `:195`, generalised as DP-S4-1 rules).
4. **A Rate Table key cannot bind an expression Banding.** `weights.py` reads
   `frame[banding.column]` for a `banding_ref` (`:107-115`). No portfolio or quote carries a
   formula's result as a column. Such a key is **refused, naming the key and the Banding**
   (`WeightJoinError`). A key that needs that result binds the `expression` Factor by
   `factor_ref`, whose resolution evaluates the formula (`weights.py` `:97-103`). Supporting it
   through `banding_ref` instead would make rating evaluate a formula outside its Factor, which
   is a new copy path of FD-1619's kind. The test is red first. Whether the binding route also
   refuses earlier, at the key's creation, is the slice's choice. The S4 write set gains
   `pricing_core/rate_tables/weights.py` and its test.

**`02` §4.2 text, applied by the slice** (exact). It covers `RL-1615`'s §4.2 disposition and
this one:

> **Amended <the slice's commit date> (`RL-1615` DP-S4-1; `RL-8001` (c)): a Banding is cut
> over a column or over an expression.** `source_expression` is new. It is the text of the
> `expression` Factor's formula that the boundaries were cut over, stored as written. Exactly
> one of `column` and `source_expression` is set, so `column` is null on a Banding cut over an
> expression. The example above, with `column` set, is the column case. A Banding with
> `source_expression` is applied only to the result of an `expression` Factor whose
> `expression` parses to the same tree (an AST dump, so white space is not a difference), and
> resolution refuses any other pairing. It cannot be a Rate Table key's `banding_ref` (`03`
> FR-228), because neither a portfolio nor a quote carries the formula's result as a column.

**`03` FR-228 text, appended by the slice** (exact):

> *(Clarified <the slice's commit date>, `RL-8001` (c): "a banded input" is a Banding cut over
> a column. A `banding_ref` that names a Banding cut over an `expression` Factor's formula
> (`02` §4.2 `source_expression`) is refused, naming the key and the Banding, because no input
> carries the formula's result. A key that needs that result binds the `expression` Factor by
> `factor_ref`, whose resolution evaluates the formula.)*

## What it obliges

- **WK-690 Slice 4 (`SL-1274`)** builds 4.7 as ruled above, red first. It corrects assertion
  (b) in `test_expression_factors_api.py` before the implementation, and the `LG-` quotes the
  corrected test red by its cause. It lands (c)'s four consequences, and the three spec texts
  above, each through `spec-change` in the code's commit.
- **The lead** widens S4's write set at the GO, because the plan is frozen: one Alembic
  migration, `docs/contracts/schemas/banding.schema.json`,
  `packages/pricing-core/src/pricing_core/modelling/bandings.py`,
  `packages/pricing-core/src/pricing_core/rate_tables/weights.py` with its test, and
  `docs/specs/03-rating-engine.md` FR-228's clause. The lead also allocates the finding's id
  for the `factors` gap and decides where its fix lands.
- **An auditor** files the `factors` finding.

## Not decided here

- Where the `factors` append-only fix lands (the lead's), and the finding's severity (the
  auditor's).
- The `FieldError.field` of the FR-210 refusal and of the `source_expression` mismatch (the
  slice's; the seat's text assertions stand).
- `02` §4.4's `factors` shape, which is recorded as unreconciled in its own contract.
- The parity check's design (OQ-1617, owner WK-1178 or P3).

## Acceptance — the violation that must become detectable

Each is red first in Slice 4:

1. *A fitted Model's pinned Factor does not carry the text that was posted.* The 4.7 test
   fails at step 3.
2. *A new version of the slug changes what a fitted Model's pin returns.* The 4.7 test fails at
   step 4.
3. *A grammar refusal has no position, or a fixed one.* The `^line \d+, column \d+: ` match
   fails, and the `column 18` assertion fails.
4. *An expression Banding cannot be stored, or a Rate Table key bands a formula's result as if
   it were a column.* The seat's positive test answers 500 without the migration. The weights
   test sees no refusal naming the key.

## Ruled

| Item | Ruling |
|---|---|
| **DP 4.7** | **(C′).** The Model's factor record is the pinned Factor version, which carries `expression` after 4.1′. Proven by one HTTP test of the chain, including a version 2 that does not move the pin. No `FitResult`, `Model` or response field. Rejected: (A), a third copy of the formula in the fit's output; (B), a new interface for an existing read; (C) unqualified |
| **The premise** | `factors` is not append-only at the database (UPDATE granted, no trigger). Routed as a finding (auditor files, lead allocates, owner proposed WK-1178), with a fix of its own row recommended. 4.7 does not wait for it |
| **Data contract** | Unchanged by 4.7. A note in `02` §4.8 (exact text above) |
| **(a)** | Confirmed. Declared = `source_columns` = the `factor` parse's bound symbols. Not tightened to equality. `referenced_columns` needs symbols in this profile. FR-95 clause (exact text above) |
| **(b)** | Corrected. `RL-1362` DP-S3-3's form: one `FieldError` on `expression`, `^line \d+, column \d+: `, `VALIDATION_FAILED`. One exact position (`column 18`). Raised as a `PlatformError` in the platform layer |
| **(c)** | Confirmed. Plus a migration (`column_name` nullable), the hand-authored contract, every reader narrowed, and a `banding_ref` to an expression Banding refused by name. `02` §4.2 and `03` FR-228 texts (exact text above) |
