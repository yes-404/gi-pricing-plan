---
id: RL-1958
family: ruling
title: FD-1954 decided — WF-699 B9 names the refusal save actually returns, a float result or port type is 422 VALIDATION_FAILED naming the field, and MONETARY_FLOAT_REFUSED is withdrawn from 03 (option (c))
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; DRAFT until the maintainer adopts it and it is minted
created: 2026-10-29               # drafted 2026-10-26 under working id 8268
owner: decision-maker
tree: 0996cadaaf0331a15e9387074a35eb28f4fb00d5
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1954, FD-1490, CR-1952, RL-1564, WF-699, WK-675, WK-673, PL-1544, FR-227, FR-245]
---

# RL-1958 — FD-1954: which side is wrong about WF-699 B9

**DRAFT — the maintainer rules.** It binds nothing until the maintainer adopts it, and the
maintainer rules by Tue 27 Oct 2026 noon. Drafted 2026-10-26 by the decision-maker (seat
dm-1954) on lead 28's brief `brief-dm-1954-2026-10-26.md`. The working id in prose, RL-1958, is
not minted.

## Authority and scope

- **The order:** the maintainer's entry "2026-10-26 13:56:26 GMT" (`to-lead.md`, a local
  channel file, cited by its header), DP-T27-7: *"Seat the decision-maker **today** … the §0
  question is which side is wrong — an owning §5.x row for `MONETARY_FLOAT_REFUSED` with FR-227
  amended, or WF-699 B9 and `:112` corrected to `RATING_TYPE_MISMATCH`; the RL comes to me and I
  rule by **Tue 27 noon**. If not ruled by then, FD-1954 stays out …"*
- **The finding:** FD-1954 (LOW, owner WK-675), from CR-1952 §5c's B9 row and its correction
  of 2026-10-26 10:57 GMT.
- **The rule:** `CLAUDE.md` §0: *"When code and spec disagree, stop and resolve it … which one
  is wrong is a real question."* This record proposes. The maintainer rules.
- **The tree:** every citation was read at `origin/main` 0996cada
  (`0996cadaaf0331a15e9387074a35eb28f4fb00d5`) with `git show origin/main:<path>`. Nothing was
  executed. The HTTP behaviour below is read from code. It was reproduced at the mapping seam
  only by FD-1490, at an earlier tree (see §Evidence item 4).

## The question, in one line

What do WF-699 B9 (`:64`) and its §3 row (`:112`) say happens at save when a step is
float-typed? And what becomes of `MONETARY_FLOAT_REFUSED`, a code that `03` lists and the
backend registers but that nothing raises?

## Evidence (at 0996cada)

1. **The workflow says:** WF-699 at `:64`: *"B9 | Backend | Type-checks on save. An
   `expression` step multiplying a `money_minor` by a float-typed value is refused:
   `MONETARY_FLOAT_REFUSED`. | `03` FR-227/245, R2"*. `:112`: *"Monetary value would be
   float-typed | `MONETARY_FLOAT_REFUSED` at save | `03` R2, FR-227"*.
2. **The spec says:** FR-227 (`03:115`), with both dated amendments (2026-10-10 WK-1178 A-2,
   and 2026-10-17 `RL-1564`). It defines a closed set of numeric types: `money_minor`,
   `decimal`, `relativity`, `percentage`, `count` and `int`. It refuses every pair it does not
   admit with `RATING_TYPE_MISMATCH`, and it names no float type. FR-245 (`03:152`): *"Mixing
   a monetary value and a float-typed value in one expression is a compile-time error"*, with
   no code named. The only `03` hit for the code is the enumeration *"Error codes owned by
   this module"* at `03:1136` (`git grep -n MONETARY_FLOAT_REFUSED origin/main --
   docs/specs/03-rating-engine.md`). RL-1564 does not mention float or the code
   (`grep -n -i 'float\|MONETARY'` over RL-1564's file prints nothing).
3. **The code has no float type:**
   - `RatingInputType` (`packages/model-schema/src/model_schema/rating.py:279-287`) has six
     members: `int`, `decimal`, `string`, `date`, `bool` and `enum`.
   - `_reject_float_type` (`rating.py:325-336`) raises `InputFreeError` (*"a rating result
     type is never float (FR-227)"*) on any declared type containing `float`.
   - That validator is `RatingResultType` (`:340`). It types `AlgorithmOutput.type` (`:349`),
     `RatingExpressionStep.result_type` (`:399`) and a sub-graph port's `type`
     (`sub_graphs.py:38`).
   - `InputFreeError` subclasses `ValueError` (`input_free.py:32`), so Pydantic reports it as
     a `ValidationError`.
4. **What save returns today:**
   - `POST /api/v1/rating-algorithms` takes `body: RatingAlgorithmDraft`
     (`backend/src/app/api/rating_algorithms.py:41-42`). Its `outputs` and `steps` carry those
     types (`rating.py:580-581`).
   - A float type therefore fails at request parse. `_handle_validation_error`
     (`backend/src/app/errors.py:520-545`) answers with **422 `VALIDATION_FAILED`** and a field
     error that names the location, for example `outputs.0.type`.
   - FD-1490 reproduced the same code at the route's mapping seam (`graph_validation_error`) at
     `caa4e411`: *"{'code': 'VALIDATION_FAILED', … 'status_code': 422, … outputs.0.type …
     never float (FR-227)"*.
   - **No backend test pins the HTTP limb** (`git grep -n '"float"' origin/main --
     backend/tests` finds no rating-algorithm case). The model-schema limb is pinned by
     `packages/model-schema/tests/test_rating_algorithm.py:163-174` (`match="never float"`).
5. **The code is raised nowhere:**
   - `git grep -n 'MONETARY_FLOAT_REFUSED' origin/main -- backend packages frontend` prints
     exactly one line, `backend/src/app/errors.py:323`, its registration in
     `RATING_ERROR_CODES`.
   - No raise and no test.
6. **`RATING_TYPE_MISMATCH` does not answer a float either.** It is raised for a pair of
   declared types that both exist: `compile.py:179` (an output's declared type against its
   producer, FR-227), `:729` (a sub-graph port) and `:402` (an `as_at` that is not a date). A
   float type never reaches these checks, because it fails at parse (item 4).
7. **This defect is already filed once:** FD-1490 (`status: active`, LOW, owner WK-673;
   register row: *"fix before close with an owner: WK-673 … Raise the code (typed signal,
   mapped, red first) or unpublish it from `RATING_ERROR_CODES` and `03:929` [now `:1136`]"*).
   FD-1954 does not cite it.
8. **The P2 exit demo skips B9 today:**
   - `examples/fremtpl2/journey.py:88` has `Skip("B9", "KNOWN GAP B9: FD-1490")`.
   - `backend/tests/test_wf699_journey.py:38-52` pins that line exactly.
   - PL-1544's B9 row records the journey's current behaviour: it asserts *"today's refusal,
     422 `VALIDATION_FAILED` for an algorithm whose output type is `float`"*.
9. **The spec check does not depend on the code registry.** audit-docs check 10
   (`scripts/audit-docs.py:3926-3950`) reads only the spec enumerations, for exclusive
   ownership. `test_spec_error_codes_are_all_constructible` (`backend/tests/test_errors.py:116`)
   iterates `PLATFORM_ERROR_CODES`, not `RATING_ERROR_CODES`. A dated note on `03:1136`
   therefore leaves `errors.py` and its tests untouched.

## R2 at runtime once the save-time refusal is withdrawn

This section meets the maintainer's condition (to-lead "2026-10-26 14:01:49 GMT"): *"what
guards R2 at runtime … which declared type a `model_call` output port carries and where the
runtime coerces it to `Decimal` before any money arithmetic (or that the expression
type-checker refuses the multiplication under FR-227); if that cannot be cited, the RL names it
as an open question with an owner."* All citations are at 0996cada.

**First, what (c) withdraws.** (c) withdraws a code *name* that nothing raises. It does not
withdraw a refusal. `_reject_float_type` (`model_schema/rating.py:325-336`, wired at `:340`)
stays exactly as it is, and save still refuses the type name `float` at parse. The runtime
question below stands on its own and is answered on its own.

1. **The declared type a `model_call` output carries is never float.**
   `RatingModelCallStep.result_type` (`rating.py:416`) is `None` or one of two values. The
   validator at `:418-423` refuses anything else: *"a model_call's result_type is decimal or
   money_minor (FR-227)"*.
   - **`None`** is the legacy default. The handler rounds the value to an integer at the step:
     `round(composed) if step.result_type is None else float(composed)` (`runtime.py:840-842`).
     The checker has no type for it: *"a model_call's None is the legacy default"*
     (`compile.py:122`).
   - **`decimal` or `money_minor`** is carried unrounded. FR-227's checks read it
     (`compile.py:107-108`, `:120-122`).
2. **The prediction is a Python float in memory, as the condition says.** A GBM returns
   `float(predict_gbm(…)[0])` (`runtime.py:657`); a GLM returns `glm_scorers[…].predict(…)`
   (`runtime.py:659`).
   - **Peril-structure path:** each peril's float is converted in our code by
     `Decimal(repr(value))` (`_decimal`, `runtime.py:666-668`). It is composed on `Decimal`:
     *"This is the rating path's own arithmetic (`CLAUDE.md` §7: Decimal, never float)"*
     (`runtime.py:691-692`).
   - **Every `model_call`:** the value enters the engine as a Python `float` or `int`
     (`runtime.py:839-842`). The comment says: *"A Decimal crosses the engine as the float it
     rounds to, as a GBM's or GLM's does."* The binding accepts no decimal type (FR-273,
     `03:237`; `score.py:331-332`).
3. **The money arithmetic happens inside the engine, on an exact decimal.** ZEN's
   `Variable::Number` is `rust_decimal` (`03:1555`: *"exact decimal — verified"*; OQ-614,
   resolved 2026-08-14, `03:1603`). So `money × prediction` in an `expression` step is decimal
   arithmetic on the value the binding admitted, not binary floating point.
   - **Output boundary:** the result is read back as the engine's exact string, not as the
     float. `test_rating_ladder_exact.py:533` asserts this: *"the float says 1.0, the engine's
     exact string says 70725.8475: the string governs"*.
   - **Rounding:** the `output` step rounds once (FR-226), pinned by
     `test_rating_glm_model_call.py:481` `test_the_output_step_rounds_a_model_call_once`.
     Money leaves as integer minor units (FR-273, `assert_integer_minor_round_trip`,
     `compile.py:84-98`).
4. **The type-checker does not refuse the multiplication.** FR-227's save-time checks compare
   declared types at output and sub-graph-port boundaries (`compile.py:165-179`, `:729`). They
   do not type the operands inside an `expression` (FD-1490 §Finding: *"nothing in expression
   validation"*). There is nothing float-typed for them to refuse: no input type is float
   (`rating.py:279-287`), and no result type is (item 1).
5. **The point where the float becomes a decimal is the ZEN binding's, not ours. That is the
   one part that cannot be cited by an assert.**
   - The only record of how the binding converts it is a docstring written from a live probe:
     *"The engine carries a handler's float at 15 significant digits (`0.0588198259273704` for
     `0.058819825927370374`, probed live …), so no form crosses the binding bit-exactly"*
     (`test_rating_glm_model_call.py:301-306`).
   - The test itself asserts only 1e-14 relative (`:317`, `pytest.approx(expected, rel=1e-14)`).
     Its docstring calls that assertion *"a DRAFT, not the item's evidence"* (`:297`).
     LG-1587's four checks are the evidence, and one of them is *"a deterministic pinned
     engine"* (`:299`).
   - So the engine version is pinned by the lockfile, but no assert pins the binding's
     float-to-`rust_decimal` rule itself. An engine upgrade that changed the rule would move
     a price with every test green, because the 1e-14 bound would still hold.

   **Open question (proposed for Tue 27's PR, not minted here):** *"What exact `rust_decimal`
   does the ZEN binding admit for a `model_call`'s float, and should a test pin it bit-exactly
   (or should the handler cross a `str`-free exact form)?"*
   - **Owner:** WK-1178, the standing maintenance Work that holds the `model_call` handler
     (FD-1458, `PL-1464`).
   - **Decide by:** Thu 2026-11-05, the P2 docs freeze.
   - **Filing:** the row is mirrored in `03` §10 and `docs/open-questions.md`, with its
     `docs/roadmap.md` §10 gate row in the same commit (`spec-change`).
   - It is not a G2 blocker. The carriage is deterministic and sits 13 orders of magnitude
     below the output step's rounding, so no price moves today. Only an *unpinned* change
     could move one.

**Answer to the condition:** a `model_call` output port carries `None`, `decimal` or
`money_minor`, never float (`rating.py:416-423`). Its float prediction enters the engine at
`runtime.py:839-842`. The engine performs the money arithmetic in `rust_decimal`
(`03:1555`), not in float. The result is read back exactly and rounded once at the `output`
step. The checker does not refuse the multiplication, and needs not, since no operand is
float-typed. The one link without an assert, the binding's float-to-decimal conversion, is the
open question above, owned by WK-1178.

## The options

### (a) Add a §5.x row that owns `MONETARY_FLOAT_REFUSED`, and amend FR-227

- **It obliges:**
  - A new owning row or clause in `03`, and a dated FR-227 amendment that names the code for
    a float type.
  - B9 and `:112` stay as they are.
  - **Code:** a typed signal from `_reject_float_type`, mapped to the code where the request
    is parsed. The route parses the body before any service code runs (Evidence item 4), so
    the mapping goes in `_handle_validation_error`, or the route's body type changes.
  - A red-first test at the route.
  - `journey.py:88` and `test_wf699_journey.py:47` change from a `KNOWN GAP` to an asserted
    probe.
  - FD-1490 is discharged by its first path.
- **What the code does today:** `errors.py:323` has `"MONETARY_FLOAT_REFUSED",`, and nothing
  else.
- **Tue 27's PR:** the spec half only. The code cannot ride a docs-only PR under DP-T27-6's
  narrow cover. Until a code slice lands, the spec claims a raise point the code does not
  have, which is the same defect in the other direction.
- **The P2 exit demo (G2):** B9 runs end to end only if that slice merges before the demo.
  Until then it stays `KNOWN GAP B9`.
- **Ids:** no requirement id changes. The code is a product identifier and stays.

### (b) Change WF-699 B9 and `:112` to `RATING_TYPE_MISMATCH`

- **It obliges:** two workflow cells, and nothing in `03`.
- **What the code does today:** it contradicts this option for the case B9 describes. A float
  type never reaches the type check (Evidence items 4 and 6), so save answers
  `VALIDATION_FAILED`, not `RATING_TYPE_MISMATCH`.
  - (b) is true only if B9's scenario is rewritten to a pair that can be declared. One example
    is a `money_minor` value fed into a `relativity` slot, which `compile.py:179` refuses
    under RL-1564. That pair is pinned at the route by
    `backend/tests/test_rating_algorithm_validate.py:151`, among others.
  - That rewrite changes what B9 demonstrates: R2's float discipline becomes RL-1564's closure
    of `money_minor`.
- **What it leaves:** FD-1490 open. A published code that no client can receive.
- **Tue 27's PR:** docs only.
- **The P2 exit demo:** the journey's B9 skip line still cites FD-1490.

### (c) Make the docs say what save returns, and withdraw `MONETARY_FLOAT_REFUSED` from `03`

The evidence shows this option. The maintainer's framing did not name it.

- **It obliges (spec, the decision-maker's per `document-ids.md` §1.6 WF and FR rows):**
  1. **WF-699 B9 (`:64`)**, the cell rewritten. The workflow is a journey; this is not an FR
     row. New cell: *"Type-checks on save. A step or output declared with a `float` type is
     refused: **422 `VALIDATION_FAILED`**, naming the field — no rating type is float (R2).
     *(Amended 2026-10-27, `RL-1958` (FD-1954): was `MONETARY_FLOAT_REFUSED`, which nothing
     raises.)*"* Refs: `03` FR-227/245, R2.
  2. **WF-699 §3 row (`:112`):** *"Monetary value would be float-typed | **422
     `VALIDATION_FAILED`** at save, naming the field *(amended 2026-10-27, `RL-1958`)* | `03`
     R2, FR-227"*.
  3. **FR-227 (`03:115`)**, one dated clause appended. The row text is not rewritten: *"(Amended
     2026-10-27, `RL-1958` (FD-1954, FD-1490): **no rating type is float.** A `float` input,
     result or port type is refused at parse, before the type check, with 422
     `VALIDATION_FAILED` naming the field; `MONETARY_FLOAT_REFUSED` is not raised.)"*
  4. **`03:1136`**: the code stays in the enumeration as a tombstone. Its identifier is a
     product identifier and is not reused (`CLAUDE.md` §5). It gets: *"(withdrawn 2026-10-27,
     `RL-1958`: never raised; a float type is `VALIDATION_FAILED`, FR-227)"*.
  *Correction 2026-10-29 (lead 29; to-lead 2026-10-29 10:12:41 item 3): the four prescribed texts at :240, :243, :246 and :250 say 2026-10-27, the planned landing day; the edits were written on 2026-10-26 and carry that date as applied (d93a36d6). The ruling's substance is unchanged.*
- **This is FD-1490's second close path.** FD-1490's own disposition offers it: *"remove it
  from `RATING_ERROR_CODES` and `03:929` and say `VALIDATION_FAILED` is the answer"*. Tue 27
  does the spec half. The two code items below do the rest, and they include the pinned line
  `backend/tests/test_wf699_journey.py:47`, `"KNOWN GAP B9: FD-1490",`. FD-1490 closes when
  both items have merged. Its FR-245 expression limb is answered by §R2 at runtime below, or
  carried by the open question that section raises.
- **Two owed code items, none on Tue 27.** Each has an owner and a date.
  - **(i) Drop `"MONETARY_FLOAT_REFUSED",` from `RATING_ERROR_CODES`** (`errors.py:323`), so
    the registry stops offering a code the spec has withdrawn.
    - **Owner:** WK-673, FD-1490's owner by the ruling of 2026-10-05 15:19:09 BST.
    - **Date:** merged by **Wed 2026-11-04**, the P2 code freeze (`docs/roadmap.md:588`).
  - **(ii) Replace B9's `Skip` with an asserted 422 probe.** `examples/fremtpl2/journey.py:88`
    `Skip("B9", "KNOWN GAP B9: FD-1490")` becomes a step that saves an algorithm whose output
    type is `float`. It asserts **422 `VALIDATION_FAILED`** with the field error
    `outputs.0.type`, over HTTP. That also pins the route limb that no backend test pins
    today (Evidence item 4).
    - `test_wf699_journey.py:47`'s pinned list loses `"KNOWN GAP B9: FD-1490"` in the same
      commit, and gains a `@pytest.mark.req("FR-227")` assert on the probe.
    - This changes an exact-list assert to match a ruled behaviour. It is not a weakened test,
      but it still needs the lead's OK under common item 13.
    - **Owner:** WK-673, as for (i). **Date:** merged by **Wed 2026-11-04**, so that G2's
      journey at the P2 exit demo (Thu 2026-11-12, `docs/roadmap.md:590`) runs B9 as an
      asserted step and not as a known gap.
  - If WK-673 is closed before either item lands, the item moves to WK-1178. WK-1178 is the
    standing maintenance Work and is exempt from G1 (`docs/roadmap.md:567`). The lead records
    that move on FD-1490's register row. The date does not move.
- **What the code does today:** this option describes it. Save refuses a float type with 422
  `VALIDATION_FAILED` (Evidence items 3 and 4). (c) changes no behaviour.
- **Tue 27's PR:** four docs edits, all under `docs/`, so the docs-only gate applies (common
  item 30). Evidence item 9: check 10 and `test_errors.py` are unaffected. FD-1954 is
  discharged in that PR. FD-1490's "unpublish" path is half done (the spec half) and stays
  open, owned, for code items (i) and (ii).
- **The P2 exit demo (G2):** until (ii) lands, B9 stays a `KNOWN GAP` citing FD-1490. After
  (ii), B9 is a step the journey asserts and no longer a gap. G2's "end to end" loses one
  exception, and no feature is built ahead of the phase (`CLAUDE.md` §0).
- **Ids:** no requirement id is created, renumbered or superseded. FR-227 takes a dated clause.

## Ruled

**Proposed: (c).** The maintainer rules.

**Which side is wrong: the workflow.** WF-699 B9 and `:112` name a code that nothing raises
(Evidence item 5), for a value the schema cannot express (Evidence item 3). Option (b), as
framed, would write a second wrong code into the same cells: `RATING_TYPE_MISMATCH` is not what
a float type gets (Evidence items 4 and 6). **The spec is stale in one place:** `03:1136` lists
a code without a raise point, and FD-1490 has recorded that since 2026-10-05. **The code is
right in behaviour:** it refuses float everywhere a rating type is declared, which is
R2's purpose. Its one defect is a dead registration (`errors.py:323`).

(a) would make the code match the documents. That is the right repair only if a separate code
for "float" is worth more to a client than the field-level `VALIDATION_FAILED` it already
receives. Two facts say it is not:

- **The schema can never produce the value.** No input is float (Evidence item 3), so the code
  could only ever answer a malformed declaration.
- **The client already learns the field.** `VALIDATION_FAILED` names the offending field
  (`outputs.0.type`), which is what FR-403's principle asks for (`errors.py:524-526`).

(c) needs no code before the docs are true. It fits Tue 27's docs-only PR, discharges FD-1954
there, and leaves FD-1490 open, owned and narrowed to two code items with a date.

**Not ruled here:** FR-245's expression clause (*"Mixing a monetary value and a float-typed
value in one expression"*), which FD-1490 holds as a separate limb (*"a reproduction of a
money-times-float expression is the first step"*). §R2 at runtime answers it in part. No
operand can be declared float (items 1 and 4), and the runtime float is admitted as a
`rust_decimal` (items 2 and 3). It is still not reproduced, so it stays FD-1490's limb, and the
open question in §R2 at runtime carries the unpinned link.

## What it obliges

If (c) is adopted:

- **In Tue 27's lane-C PR,** in the commit that mints this record: (c)'s four docs edits
  (WF-699 `:64` and `:112`, FR-227's dated clause, and the `03:1136` withdrawal note), written
  by the decision-maker. FD-1954 is closed there, citing this record.
- **Also in that PR:** the open question in §R2 at runtime, owner WK-1178, decided by Thu
  2026-11-05. The row is mirrored in `03` §10 and `docs/open-questions.md`, with its roadmap
  §10 gate row.
- **Owed, after the PR:** code items (i) and (ii), owner WK-673, merged by Wed 2026-11-04.
  They are recorded on FD-1490's register row. FD-1490 stays `active` until both merge.

If the maintainer rules (a) or (b) instead, that option's "It obliges" list above applies
unchanged.

## For the lead (not ruled here)

1. **FD-1490's owner and the two code items.** WK-673 owns FD-1490 by the 2026-10-05 ruling.
   Re-owning items (i) and (ii) to WK-675 (FD-1954's owner) is the lead's call, recorded on
   FD-1490's register row.
2. **The register's "discharged by … Tue 27 Oct" for FD-1954.** It stays true under (c), and
   under (a) or (b) for the docs half. If the maintainer has not ruled by noon, DP-T27-7's
   fallback applies, and the lead corrects the line.
3. **Minting.** This record mints in Tue 27's lane-C PR with its adoption line appended, in the
   same commit as the four edits it disposes (role file: *"A spec edit is never made without a
   ruling record in the same commit naming it as that ruling's disposition"*).

## Acceptance — the violation that must become detectable

- *Violation: a workflow or spec cell names `MONETARY_FLOAT_REFUSED` as raised.* `git grep -n
  MONETARY_FLOAT_REFUSED -- docs/specs docs/workflows` at the PR's head prints only `03:1136`
  with the word "withdrawn". Any other hit is the defect back.
- *Violation: save answers a float type with anything but 422 `VALIDATION_FAILED`.* Owed item
  (ii)'s HTTP probe and its `req("FR-227")` assert fail on it. Until they land, the
  model-schema test (`test_rating_algorithm.py:163-174`) covers the parse limb only.
- *Violation: the registry still offers the withdrawn code.* After owed item (i), `git grep -n
  MONETARY_FLOAT_REFUSED -- backend packages frontend` prints nothing.

## What guards R2 at runtime

*(Appended 2026-10-26 14:09 GMT, on the lead's relay of the maintainer's condition
(to-lead "2026-10-26 14:01:49 GMT"). The section **"R2 at runtime once the save-time refusal is
withdrawn"** above carries every citation, at 0996cada. It was inserted at `a2440fff`, before
the lead's "append, editing nothing above" instruction arrived. This section restates its
conclusion under the heading the lead named, and edits nothing above.)*

- **The port type.** A `model_call` output is declared `None`, `decimal` or `money_minor`,
  never float.
  - Declared in model-schema: `RatingModelCallStep.result_type`, `model_schema/rating.py:416`,
    with the validator at `:418-423`.
  - Derived for the checker by `producer_types`: `compile.py:107-108` and `:120-122`. `None`
    is the legacy default, rounded to an integer at the step (`runtime.py:840-842`) and left
    untyped by the checker.
- **Where a float output becomes a decimal.**
  - The prediction is a float in memory (`runtime.py:657`, `:659`).
  - On the peril-structure path, our code converts it with `Decimal(repr(value))`
    (`runtime.py:666-668`).
  - Every `model_call` value enters the engine as a float (`runtime.py:839-842`; FR-273).
    Money arithmetic then runs in ZEN's `rust_decimal` (`03:1555`; OQ-614, `03:1603`). The
    result is read back as an exact string (`test_rating_ladder_exact.py:533`) and rounded
    once at the `output` step (`test_rating_glm_model_call.py:481`).
- **The type-checker does not refuse the multiplication.** FR-227's checks at `compile.py:179`
  and `:729` compare declared types at output and port boundaries. They do not type an
  expression's operands, and no operand can be declared float.
- **The one link no line can pin is an OPEN QUESTION.** The binding's float-to-`rust_decimal`
  conversion is recorded only by a live-probe docstring, "15 significant digits"
  (`test_rating_glm_model_call.py:301-306`). Its assert is `rel=1e-14` (`:317`).
  - **Owner: WK-1178**, which holds the `model_call` handler (FD-1458, `PL-1464`). The lead
    proposed WK-673; WK-1178 is proposed here because that Work wrote the handler and its
    tests. **The maintainer confirms the owner.**
  - **Decide by:** Thu 2026-11-05, the P2 docs freeze.
  - **Filing:** the OQ row is raised in Tue 27's PR, mirrored in `03` §10 and
    `docs/open-questions.md`, with its roadmap §10 gate row.

## Owners and dates, as ruled (supersedes the owner and date lines above)

*(Appended 2026-10-26 14:09 GMT, on the maintainer's entry "2026-10-26 14:07:41 GMT"
(`to-lead.md`), Asks 1 and 2, verified verbatim in the channel. Where §The options (c),
§What it obliges or §For the lead item 1 above name a different owner or date, this section
governs.)*

1. **Drop `"MONETARY_FLOAT_REFUSED",` from `errors.py:323`, and write the `03:1136` tombstone.**
   - **Owner: WK-673. Date: by Fri 2026-11-06.**
   - This is FD-1490's own second close path. Its register row (`docs/findings/register.md:316`)
     names *"unpublish it from `RATING_ERROR_CODES` and `03:929`"*. **Its merge closes FD-1490.**
   - The `03:1136` note itself rides Tue 27's docs PR, under (c) item 4.
2. **B9's `Skip` becomes an asserted 422 probe.** `examples/fremtpl2/journey.py:88` and the
   pin line `backend/tests/test_wf699_journey.py:47` (`"KNOWN GAP B9: FD-1490",`) change
   together.
   - **Owner: WK-1178.** The journey test is SL-1527's: its docstring at `test_wf699_journey.py:1`
     reads *"(PL-1544, SL-1527)"*, and SL-1527 is WK-1178's exit-demo slice (b).
   - **Date: by the P2 exit demo, Thu 2026-11-12**, as a dated row under WK-1178's plan.
   - **The item-13 OK for `:47` is granted only inside that code slice.** The pin line goes
     with the Skip it pins, red-first. It is not granted on Tue 27 and not in a docs PR.
   - Removing B9 from the pinned list while the Skip stays would be a false green.
3. **The FR-227 route test rides with item 2's slice, under WK-1178, by the same date.**
   - The journey walks over HTTP (`test_wf699_journey.py:1`: *"walked over HTTP"*), so the
     probe already asserts at the route.
   - That slice should still add one fast test that does not need the journey: a float output
     type at `POST /api/v1/rating-algorithms` answers 422 `VALIDATION_FAILED` with the field
     `outputs.0.type`, under `@pytest.mark.req("FR-227")`. It sits beside
     `test_another_shape_refusal_is_validation_failed` (`backend/tests/test_rating_algorithms.py:251`),
     which pins the same mapping for another shape.
   - Nothing in the evidence argues for a different owner.
4. **FD-1490's second close path, named explicitly.** It has two parts:
   - **Tue 27's docs half:** WF-699 `:64` and `:112`, FR-227's dated clause, and the
     `03:1136` tombstone.
   - **Item 1's code:** `errors.py:323`.
   - Item 2's change to the pin line `test_wf699_journey.py:47` retires the journey's
     `KNOWN GAP B9: FD-1490` once FD-1490 is closed. FD-1954 is discharged on Tue 27 by the
     docs half.
