---
id: PL-9521
family: plan
kind: leaf
title: WK-1178 — money_minor closed both ways at save, the numeric type-check fix (FR-227, FR-226): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: planner
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1263, PL-1371]
---

# WK-1178 — money_minor closed both ways at save: the numeric type-check fix, leaf plan

Filed under working id 9521 (this plan) and slice working id 9522 (its `SL-` row under WK-1178
in [`../roadmap.md`](../roadmap.md), `draft`). The lead reserved both in
`~/gi-pricing-plan.local/handover/eta.md` (row "SL 9522 / PL 9521"). The finding it fixes is
FD 9549 (working id; #1197, branch `fd-9549-numeric`, read at `9c8a52c6`). Nothing here is
minted. Every line number was read at `origin/main` `4d3be141`, the `tree:` above.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (pricing-core stays standalone),
> `fastapi-service` (the sub-graph route's 422), `spec-change` (only if an `RL-` carries
> FR-227 text), `dev-commands` (the two-half gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

FR-227's save-time check treats every pair of numeric types as interchangeable.
`_compatible` (`packages/pricing-core/src/pricing_core/rating/compile.py:124-129`) returns
`True` for any two members of `_NUMERIC` (`:57`). Its comment (`:127-128`) defers the real
check to "the bundle compilation", and no such check was ever built. So a pence-valued
`money_minor` value can be declared as a `decimal`, `relativity`, `percentage`, `count` or
`int` output, or the reverse, and it saves and compiles. At score time, the declared type
decides how the value is served (`score.py:751`, `:947-975`, as FD 9549 records).

This slice closes `money_minor` in both directions at save, as the maintainer (by delegation)
ruled. A value leaves `money_minor` only into `money_minor`. A value enters `money_minor` only
from `money_minor`, or from `decimal` at an output step, the rounding point (FR-226). The
rule holds on all three call paths: `output_type_issues`, `_check_result_types` (through
`ALGORITHM_CHECKS`), and `fragment_output_type_issues` (sub-graphs).

**Spec, finding and decision:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-227 (`03:113`): *"Every step
  declares its result type, and type compatibility is checked at save time. A monetary result
  must be `decimal` or `money_minor` (R2)."* FR-226 (`03:112`): *"`output` steps declare
  rounding explicitly … Rounding is never implicit and never happens twice."*
- FD 9549 (working id; #1197 @`9c8a52c6`). Its finding file is under `docs/findings/` on that
  branch, and its name begins with the working id (`…09549-rating-save-time-type-check-…`). The
  full name is not written here, because check 32 reads an id in it. Its §"Disposition" (a)
  reads: "make `_compatible` exact for `money_minor`". Its §"Boundary" reads: "the `model_call`
  producer case is not this finding's … `_compatible` stays as A-2 leaves it, and this finding
  owns the change to it".

## The maintainer's decision this plan rests on, quoted

From `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed *"2026-10-05 17:36:28 BST
— FD 9549 (#1197 @9c8a52c6): MEDIUM LATENT confirmed; disposition (a) narrowed, with
money_minor CLOSED both ways; batch 2 agreed"*, read in full by this planner. Verbatim, items 1
to 3:

> 1. Severity: MEDIUM, LATENT (no live artifact; all non-test algorithms are money_minor→money_minor). The wider reach (all six numeric types and 30 pairs; the sub-graph create path via fragment_output_type_issues; serve-time coercion by the DECLARED type) is ACCEPTED as the finding's text.
> 2. Disposition: (a), narrowed. money_minor is CLOSED in BOTH directions at save time:
>    - OUT of money_minor: only into money_minor. Refuse money_minor into decimal, relativity, percentage, count or int, for EVERY producer (A-2 item 15 stays the model_call instance; the fix slice generalises it without editing A-2's tests).
>    - INTO money_minor: from money_minor, or decimal AT AN OUTPUT STEP ONLY (FR-226's rounding point under option (B)). Refuse relativity, percentage and count into money_minor.
>    - int→money_minor and the non-money pairs among themselves (relativity/percentage/count/int/decimal) go to ONE OQ, owner WK-1178, decided before the fix slice's plan mints.
>    The fix slice's FIRST task is red-first: one red per refused direction, plus a sweep showing no committed algorithm or fixture newly fails. If one does, STOP and report; do not loosen the rule.
> 3. Reserve the fix slice under WK-1178, AFTER the emergency slice (lane B order: emergency (c) → FD 9707 fix → this, unless PL 9728 is ready first; you sequence it).

The OQ in item 2 is OQ 9556 (working id; #1200).

**Dated note, 2026-10-05 (written 17:46:24 BST, pre-mint): OQ 9556 is decided.** The entry is
in the same file. Its header carries the literal word "STAMP" in place of a time, and its body
says why: *"The header above carries the literal word STAMP by my error; its true time is 2026-10-05 17:42:06 BST, taken by `date` in the same command that wrote it. Nothing is deleted."* So it is cited here by its body's time,
**2026-10-05 17:42:06 BST**, and by its header text, *"STAMP — OQ 9556 (#1200 @f46ca86f)
DECIDED: A1 + B3; E1 folds noted"*. It was read in full by this planner. Verbatim:

> OQ 9556 DECIDED, by the maintainer (by delegation), before PL 9521 mints:
> - A1. int→money_minor is REFUSED at save. Money enters a computation through an EXPLICIT money_minor-typed expression step, the one visible place a pence integer becomes money. RatingInputType (rating.py:196) has no money_minor member, so this is how a pence input is declared money; A4 (a new input type) is not taken now.
> - B3. Widening only: int, count, relativity and percentage→decimal, and count→int, are allowed. EVERY other non-money pair is refused, including relativity↔percentage (a 100× unit error) and decimal→int, count, relativity or percentage.
> - Combined with 17:36:28 item 2: money_minor is closed both ways; decimal→money_minor only at an output step (FR-226).
> - PL 9521's sweep, BEFORE its red tasks: the planner confirms no committed algorithm, fixture or seed feeds an int input into a money_minor output, or uses a refused B pair. If any does, that is a STOP to me with the file:line. It is NOT an automatic A3 fallback.
> - The real-time /score output coercion (not checked) is in PL 9521's read-first list, with a red if it serves a refused pair differently from batch.
> OQ 9556's row is decided citing this entry; the 03 §10 mirror is decided in the same commit (both ways).

This plan is rewritten to it: the directions table (D10–D25, A3–A7), items 1–3, 6, 7 and 11,
and the tasks. The sweep now runs **before** the reds (Task 1), and a hit is a STOP to the
maintainer (by delegation), never an automatic fallback. The real-time `/score` coercion is
read first (Task 0 Step 3), with a red if it differs from batch (item 11).

## Status

`draft`. **DP-1 is open** (§"Decision points"). It is the maintainer's (by delegation),
because its recommended option flips one committed test assertion, and the ruling's item 2
says "If one does, STOP and report; do not loosen the rule". **OQ 9556 is decided** (A1 + B3,
17:42:06 BST; dated note above). The plan moves to `active` only through a separate
activation PR, after every activation need below holds.

### Activation needs, in order

1. **FD 9549 minted** (batch 2, after RL 9562 and before PL 9560; the 17:36:28 entry, item 4).
2. **OQ 9556 decided on main** (#1200). Its decision (A1 + B3, 17:42:06 BST) is already written
   into this plan. The need is met when OQ 9556's row on `main` reads decided, citing that entry,
   with the `03` §10 mirror decided in the same commit. *(Dated note, 2026-10-05: this need
   said "decided … before this plan mints"; the decision came at 17:42:06.)*
3. **DP-1 ruled.**
4. **The emergency slice merged** (SL 9561 / PL 9560, #1196). The ruling's item 3 places this
   slice after it. Lane B's order is: the emergency slice (c) → the FD 9707 fix (PL 9688,
   #1145) → this slice, unless PL 9728 (#1113) is ready first. The lead sequences that.
5. **If an `RL-` carries FR-227 text** (a T-text recording the closed rule), that `RL-` is
   merged, and Task 4 applies its text byte for byte. This plan drafts no spec text.
6. **The lane and the dispatch GO.** The dispatch record writes `RL 9620`'s same-Work lines
   (a) and (b) for every WK-1178 slice in flight beside this one (§"Write set").

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means that the named test was run, and it failed **for the stated cause**, before the code that
turns it green existed. A failure with the right status and a different cause is a plan defect
([`README.md`](README.md) rule 2). The ledger records each red, with the failure line as
printed. Test modules:
- `P` is `packages/pricing-core/tests/test_rating_compile.py` (appended);
- `B` is `backend/tests/test_sub_graphs_api.py` (appended).

**The refused directions.** These are the ruling's item 2, one red per direction on each call
path:

| # | Producer → declared | Refused? | Source |
|---|---|---|---|
| D1 | `money_minor` → `decimal` | yes | "OUT of money_minor: only into money_minor" |
| D2 | `money_minor` → `relativity` | yes | same |
| D3 | `money_minor` → `percentage` | yes | same |
| D4 | `money_minor` → `count` | yes | same |
| D5 | `money_minor` → `int` | yes | same |
| D6 | `relativity` → `money_minor` | yes | "Refuse relativity, percentage and count into money_minor" |
| D7 | `percentage` → `money_minor` | yes | same |
| D8 | `count` → `money_minor` | yes | same |
| D9 | `decimal` → `money_minor` at a sub-graph **output port** (not an output step) | per DP-1 | "decimal AT AN OUTPUT STEP ONLY" |
| A1 | `money_minor` → `money_minor` | no (control) | — |
| A2 | `decimal` → `money_minor` at an **output step** | no (control) | "or decimal AT AN OUTPUT STEP ONLY" |
| D10 | `int` → `money_minor` | yes | OQ 9556 A1: "int→money_minor is REFUSED at save" |
| D11 | `decimal` → `int` | yes | OQ 9556 B3: "EVERY other non-money pair is refused, including … decimal→int, count, relativity or percentage" |
| D12 | `decimal` → `count` | yes | same |
| D13 | `decimal` → `relativity` | yes | same |
| D14 | `decimal` → `percentage` | yes | same |
| D15 | `relativity` → `percentage` | yes | B3: "including relativity↔percentage (a 100× unit error)" |
| D16 | `percentage` → `relativity` | yes | same |
| D17 | `int` → `count` | yes | B3: every other non-money pair |
| D18 | `int` → `relativity` | yes | same |
| D19 | `int` → `percentage` | yes | same |
| D20 | `count` → `relativity` | yes | same |
| D21 | `count` → `percentage` | yes | same |
| D22 | `relativity` → `int` | yes | same |
| D23 | `relativity` → `count` | yes | same |
| D24 | `percentage` → `int` | yes | same |
| D25 | `percentage` → `count` | yes | same |
| A3 | `int` → `decimal` | no (control) | B3: "Widening only: int, count, relativity and percentage→decimal, and count→int, are allowed" |
| A4 | `count` → `decimal` | no (control) | same |
| A5 | `relativity` → `decimal` | no (control) | same |
| A6 | `percentage` → `decimal` | no (control) | same |
| A7 | `count` → `int` | no (control) | same |

The table covers all 30 ordered pairs of `_NUMERIC`'s six types: 5 out of `money_minor`
(D1–D5); 5 into it (D6–D8, D10, and `decimal`, which is A2 at an output step and D9 at a port);
and 20 non-money pairs (A3–A7 allowed, D11–D25 refused). *(Dated note, 2026-10-05: rows O1 and
O2, "OPEN (OQ 9556)", are replaced by D10–D25 and A3–A7 on the 17:42:06 BST decision.)*

The **refused set** is D1–D8 and D10–D25; D9 is DP-1's. The **allowed set** is A1–A7.
*(Dated note, 2026-10-05: items 1–3 were parametrised over D1–D8. Item 6 held the OQ pairs at
today's behaviour, and item 11 is new. All are rewritten to the 17:42:06 BST decision.)*

1. **`output_type_issues` refuses every refused direction (P).**
   `test_output_type_issues_refuses_a_closed_direction` is parametrised over the refused set.
   A types map `{"v": producer}` and one output `(…, "out", declared, "v")` give exactly one
   `RATING_TYPE_MISMATCH`. The allowed set gives none (A2 with the output-step flag set).
   **Red first:** at the base each refused case returns `[]` (`_compatible` passes every
   `_NUMERIC` pair, `compile.py:129`).
2. **`validate_algorithm` refuses every refused direction through `_check_result_types` (P).**
   `test_an_algorithm_output_refuses_a_closed_direction` is parametrised over the refused set.
   An algorithm has a producer of the producer type and an output step whose output is declared
   as the declared type. `validate_algorithm` reports exactly one `RATING_TYPE_MISMATCH` naming
   the output step (as `test_an_algorithm_type_mismatch_reports_the_output_step`, `P:334`,
   does). The producer is an `expression` step with that `result_type`. D10 is also run with
   an `int` **input** step (`int` from the input contract) feeding the output directly, which
   is the case A1 names. The allowed set reports none. **Red first:** at the base none is
   reported.
3. **`fragment_output_type_issues` refuses every refused direction on a sub-graph output port
   (P).** `test_a_fragment_port_refuses_a_closed_direction` is parametrised over the refused
   set, built with the existing `_fragment(output_type, result_type)` helper (`P:352`). Each
   case gives exactly one `RATING_TYPE_MISMATCH` naming `s_last`. A1 and A3–A7 give none. D9
   follows DP-1. **Red first:** at the base each returns `[]`.
4. **The sub-graph route refuses one direction end to end (B).**
   `test_a_sub_graph_port_feeding_money_minor_into_decimal_is_refused`: `POST
   /api/v1/sub-graphs` with D1 (a `money_minor` expression into a `decimal` output port)
   answers `422` with `code == "RATING_TYPE_MISMATCH"`, as the existing
   `test_an_output_port_type_mismatch_is_refused_rating_type_mismatch` (`B:90`) shows for a
   non-numeric pair. The route reaches `fragment_output_type_issues` through `_check`
   (`backend/src/app/platform/sub_graphs.py:40-42`). **Red first:** at the base it answers
   `201`.
5. **One refusal per output, never two (the overlap with A-2 item 15).**
   `test_a_refused_pair_raises_exactly_one_issue` (P): for D2, with an `expression` producer,
   and, once A-2 is merged, with a `model_call` producer declared `money_minor` (A-2's
   `RatingModelCallStep.result_type`), `validate_algorithm` returns exactly **one**
   `RATING_TYPE_MISMATCH` for the output. **Red first:** at the base the expression case
   returns zero. If A-2 lands first, the `model_call` case is added in this slice and must
   show one issue, not two (§"Hand-off").
6. **Widening is kept: the allowed set passes on every path (P).**
   `test_a_widening_pair_is_allowed` is parametrised over A3–A7 and run on all three paths,
   with A1 and A2 as well. Each passes. This is the control that keeps the refused set from
   over-reaching. A refused-set test that passes A3–A7 by accident would show here. It is green
   at the base, and it must stay green after the change.
7. **The sweep, run BEFORE the reds: no committed algorithm, fixture or seed uses a refused
   pair.** Task 1 runs the script **before** any red is written. It applies the **new rule**
   as a pure function (Task 1 Step 1's `closed_rule(producer, declared, at_output_step)`,
   written to the table above) to the producer and declared types of every output and
   output port that the repository commits. It lists each hit with `file:line`. The
   algorithms are:
   - the demo seed fixture (`examples/fremtpl2/model.py:334-343`, `fremtpl2-demo@1`);
   - `scripts/bench-rating.py:248-267`;
   - `scripts/bench-score-batch.py:78-86`;
   - `scripts/bench-compiled-for.py:79-87`;
   - any seed under `backend/src/app/demo/` (FD 9549 found that it builds none);
   - every algorithm or sub-graph body built in a test module under `packages/*/tests` and
     `backend/tests`. Task 1 Step 1 names its predicate.

   **Any hit, an `int` input into a `money_minor` output included, is a STOP to the maintainer
   (by delegation), with `file:line`.** It is **not** an automatic fallback (OQ 9556:
   "It is NOT an automatic A3 fallback") and not a reason to loosen the rule. One hit is
   already known, and it is DP-1's: `test_a_compatible_fragment_output_port_raises_no_issue`
   (`P:386-389`) asserts `_fragment("money_minor", result_type="decimal") == []`, which is D9.
   After the change (Task 4), the same script runs `validate_algorithm` (and
   `fragment_output_type_issues`) on the slice head. Its refusals must equal the
   before-the-change prediction. Then these files pass unedited:
   `uv run pytest packages/pricing-core/tests/test_rating_compile.py backend/tests/test_sub_graphs_api.py backend/tests/test_sub_graphs_service.py backend/tests/test_rating_algorithms.py -q`.
8. **The deferral comment is gone.** `git grep -n "the bundle compilation resolves" --
   packages/pricing-core/src` prints nothing. `_compatible`'s docstring states the closed rule
   and cites the 17:36:28 and 17:42:06 BST entries.
9. **The gate.** The full two-half gate (`CLAUDE.md` §11) passes on the merge tree, run once,
   holding the one gate slot (`RL 9620` as corrected at 15:27:25 BST). The ledger records each
   rc and the tree.
10. **The write set.** `git diff --stat origin/main...HEAD` names only §"Write set"'s paths.
11. *(Added 2026-10-05, pre-mint, from the 17:42:06 BST decision: "The real-time /score output
    coercion (not checked) is in PL 9521's read-first list, with a red if it serves a refused
    pair differently from batch".)* **Real-time and batch serve a refused pair alike, or a red
    says otherwise.** Read first (Task 0 Step 3): the real-time path builds `outputs` in
    `_build_outputs` (`packages/pricing-core/src/pricing_core/rating/score.py:729`) and does not
    call `_coerce_output_value`. The batch path serialises them through `_outputs_json`
    (`:991-1002`), which calls `_coerce_output_value` (`:950`) by the declared type. For each
    refused class (out of `money_minor`, into `money_minor`, a refused non-money pair), the
    executor reads what each path serves for an algorithm that carries the pair. Such an
    algorithm is one stored or compiled before this fix: built with
    `RatingAlgorithm.model_validate`, with no `validate_algorithm`. If the two paths serve it
    differently, `test_score_and_batch_serve_a_pre_fix_pair_alike` (in
    `packages/pricing-core/tests/test_rating_score.py`, appended) is written red: one quote
    through `score_one` and through the batch scorer, asserting the same served value, and
    red by the difference. **Its green is not scoped by this plan.** Aligning the paths edits
    `score.py`, outside §"Write set", so a red here is a STOP to the lead, who scopes it. If
    no class differs, the ledger records each reading and no test is added.

## Global Constraints

- **Money is integer minor units or Decimal, never float** (`CLAUDE.md` §7). This slice
  closes the save-time hole through which a `money_minor` value changes unit by declaration.
- **`pricing-core` stays standalone** (`CLAUDE.md` §2). The change is pure.
- **Do not loosen the rule** (the ruling, item 2). A committed algorithm or fixture that newly
  fails is a STOP, not a reason to narrow the rule.
- **A-2's tests are not edited** (the ruling, item 2: "the fix slice generalises it without
  editing A-2's tests").
- **Widening only** (OQ 9556 B3): A3–A7 stay allowed (item 6). A sweep hit is a STOP to the
  maintainer, never an automatic fallback (item 7).
- **Shared files** (`RL-1263`, amended by `RL 9620`): two concurrent build slices may not
  both change the same existing function, class, spec section or policy table.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): items 1–5 are red
  first.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-227 | Type compatibility at save: `money_minor` closed both ways | `req("FR-227")` on items 1–5 |
| `03` | FR-226 | `decimal` enters `money_minor` only at an output step, the rounding point | `req("FR-226")` on items 1, 2 (A2) |
| `03` | FR-217 | A sub-graph's output ports obey the same rule at create | `req("FR-217")` on items 3, 4 |

Out of scope, named so no reader assumes it:
- a new input type for money (OQ 9556: "A4 (a new input type) is not taken now");
- the `model_call` producer's typing (A-2 item 15, #1178);
- typing an `expression` step's **inputs** (the maintainer (by delegation), 17:22:01 BST:
  "typing expression INPUTS is wider and a STOP");
- serve-time coercion (`score.py:751`, `:947-975`), which reads the declared type. Once save
  refuses a mismatch, that coercion no longer sees one.

### Task 0 at planning time (read, not run)

Read at `4d3be141` by this planner; no code was run.

| # | Fact | Where | Consequence |
|---|---|---|---|
| 0.1 | `_NUMERIC = frozenset({"int", "decimal", "money_minor", "relativity", "percentage", "count"})` | `compile.py:57` | the set is kept; the rule is a narrowing inside `_compatible` |
| 0.2 | `_compatible` returns `producer == declared`, else `producer in _NUMERIC and declared in _NUMERIC`; comment `:127-128` defers to "the bundle compilation" | `compile.py:124-129` | the one place to change; the comment goes (item 8) |
| 0.3 | `output_type_issues(types, outputs)` is `_compatible`'s one caller (`:143`) | `compile.py:132-155` | it gains the output-step flag it passes on |
| 0.4 | `_check_result_types` builds outputs from **output steps** (`RatingOutputStep`) and calls `output_type_issues` | `compile.py:158-170`; in `ALGORITHM_CHECKS` (`:359-363`) | the algorithm path sets "at an output step" |
| 0.5 | `fragment_output_type_issues` compares sub-graph **output ports** (`AlgorithmOutput`) and calls `output_type_issues` | `compile.py:173-199`; called by `_check`, `backend/src/app/platform/sub_graphs.py:40-42` | a port is not an output step: D9 is DP-1's |
| 0.6 | `producer_types` types `input` steps (from the input contract) and `expression` steps (`result_type`) only | `compile.py:95-116` | a `model_call` producer is untyped until A-2 lands |
| 0.7 | `test_a_compatible_fragment_output_port_raises_no_issue` asserts `_fragment("money_minor", result_type="decimal") == []` | `P:386-389` | D9 under DP-1 (a) flips this assertion: the ruling's STOP |
| 0.8 | Every non-test algorithm is `money_minor` → `money_minor` (demo `examples/fremtpl2/model.py:334-343`; `bench-rating.py:248-267`; `bench-score-batch.py:78-86`; `bench-compiled-for.py:79-87`) | FD 9549 §"Liveness" | the sweep's committed-algorithm half is expected clean |
| 0.9 | A `RatingInputType` (`int`, `decimal`, `string`, `date`, `bool`, `enum`) is never `money_minor` | `model_schema/rating.py:195-203` | an `input` producer reaches `money_minor` only as `int` (D10, refused: OQ 9556 A1) or `decimal` (A2) |

### Write set, and its contention (`RL-1263`, `RL 9620`)

| Path | Change |
|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | edited: `_compatible` (`:124-129`) gains a keyword-only `at_output_step: bool` with no default, and the closed rule; its comment (`:127-128`) is replaced. `output_type_issues` (`:132-155`) takes and passes `at_output_step`. `_check_result_types` (`:158-170`) passes `True`. `fragment_output_type_issues` (`:173-199`) passes `False`. `_NUMERIC` and `ALGORITHM_CHECKS` are not edited. |
| `packages/pricing-core/tests/test_rating_compile.py` | appended: items 1–3, 5, 6. Edited only under DP-1 (a): the second assertion of `test_a_compatible_fragment_output_port_raises_no_issue` (`:389`) |
| `backend/tests/test_sub_graphs_api.py` | appended: item 4 |
| `packages/pricing-core/tests/test_rating_score.py` | appended **only if** item 11's red is due (Task 0 Step 3). Its green, in `score.py`, is outside this write set and is the lead's to scope *(added 2026-10-05)* |
| `packages/pricing-core/src/pricing_core/rating/score.py` | **read only**: `_build_outputs` (`:729`), `_coerce_output_value` (`:950`), `_outputs_json` (`:991-1002`) (item 11) |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated |
| `docs/specs/03-rating-engine.md` FR-227 row (`:113`) | only if an `RL-` carries text (activation need 5) |

**Contention.** The classes are those in `docs/process/delivery-process.core.json`'s
`no_shared_files`. **Snapshot:** the open PRs at `4d3be141`, read 2026-10-05 between 17:38 and
17:41 BST. Each plan's write set was read from its branch at the head named, grepped for
`_compatible`, `output_type_issues`, `_check_result_types`, `fragment_output_type_issues`,
`producer_types`, `_NUMERIC`, `test_rating_compile.py` and `platform/sub_graphs.py`.

| Other slice (Work; source read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **A-2**, PL 9597 (#1178 @`04f99c1f`; WK-1178) | `compile.py` `producer_types`, `_check_result_types` / `output_type_issues`; `test_rating_compile.py` (via its item 15) | types a `model_call` producer by `result_type`; refuses a `money_minor` `model_call` into a non-money output, for `model_call` producers only, `_compatible` untouched | `_compatible`; `output_type_issues`'s and `_check_result_types`'s flag | **same functions → SERIALISE.** The overlap: both refuse `money_minor` → `relativity` for a `model_call` producer. Whichever lands **second** leaves one refusal (item 5). If this slice is second, it removes A-2's `model_call`-only refusal branch, because the general rule now covers it through `producer_types`, and A-2's tests stay green unedited. If A-2 is second, its dispatch record drops that branch and keeps only the `producer_types` typing. **A-2's control conflicts with OQ 9556 B3** *(dated note, 2026-10-05)*. A-2 item 15's control says "declared `decimal`, the same graph saves", for a `decimal` `model_call` into a `relativity` output. That pair is D13, which B3 refuses. If both merge as written, A-2's control fails under this slice's rule. The fix is pre-mint, in A-2's own plan: its control becomes a legal pair, for example a `decimal` `model_call` into a `decimal` output. This plan does not edit A-2's tests, and the conflict is reported to the lead |
| **The FD 9707 fix**, PL 9688 (#1145 @`2f3269c8`; WK-673), and RL 9642 (#1148, its ruling) | `compile.py` | adds `_check_lookup_as_at`; appends one entry to `ALGORITHM_CHECKS` (`:359-363`) | `_compatible`, `output_type_issues`, `_check_result_types`, `fragment_output_type_issues`; not `ALGORITHM_CHECKS` | different definitions, one file → **ALLOWED one-sided** with the dispatch record naming each path and its check; lane B's order puts it first anyway. RL 9642 writes no code. PL 9688 uses `RATING_TYPE_MISMATCH` for a lookup input (its DP-4), at a different site |
| **PL 9728**, the NFR-489 remedy (#1113 @`3ad98fe2`; WK-1178) | none written by both: it edits `scripts/bench-rating.py`, `backend/src/app/db/session.py`, `config.py`, `api/deps.py`, `api/authz.py`, `auth/service.py`, `api/score.py`, `main.py` | — | item 7's sweep **reads** `scripts/bench-rating.py:248-267` | **no shared write → concurrent allowed.** Same Work: `RL 9620` (a) and (b) are written ((b): neither consumes the other's output). If PL 9728 changes `bench-rating.py`'s algorithm, item 7's sweep reads it at the dispatch tree |
| **PL 9610**, WK-1250 S2 (#1170; WK-1250) | `compile.py` `_compatible` (**called**) | adds a mount-port check that calls `producer_types` and `_compatible` (its plan `:581-583`) | changes `_compatible`'s signature (a required `at_output_step`) and its numeric rule | **a caller of an edited function → SERIALISE.** Whichever lands second updates the other's call: a mount port is not an output step, so it passes `at_output_step=False` |
| **PL 9578**, WK-675 S3 (#1186 @`c5d1d03a`) | `compile.py` (its `ValidationIssue` move, RL 9767; the import block) | moves `ValidationIssue` to `model-schema`; runs `test_rating_compile.py` | `output_type_issues` builds `ValidationIssue`s | the holds register: "S3 is never concurrent with a slice editing compile.py" → **SERIALISE** |
| **The emergency slice**, PL 9560 / SL 9561 (#1196 @`68b2f860`; WK-1178) | none (it edits `score.py`, `test_rating_shadowed_inputs.py`, `test_quote_input_raise_sites.py`, backend score tests, `03` FR-213) | — | — | no shared write; **ordered first** by the ruling's item 3 (activation need 4) |

Every other open plan names none of this write set. That was checked by the same grep over
each plan file on its branch.

### Size

Small: about half an executor day, to three quarters with OQ 9556's 16 added directions and
item 11's read. It is one pure function and three callers, about 60 parametrised cases (24
refused directions and 7 allowed pairs, on three paths), one backend test, and a sweep script
run twice. Item 11 may add one red, whose green is the lead's to scope. *(Dated note,
2026-10-05: was "about 30 parametrised cases"; re-estimated, unmeasured.)*

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | D9: `decimal` into a `money_minor` sub-graph **output port**. The ruling admits `decimal` → `money_minor` "AT AN OUTPUT STEP ONLY (FR-226's rounding point)". A port is not an output step, and it carries no rounding (0.5). The committed `test_a_compatible_fragment_output_port_raises_no_issue` (`P:386-389`) asserts that this pair passes today | (a) refuse at a port, as the ruling reads, and flip `P:389`'s second assertion, with the maintainer's (by delegation) approval, because the ruling's STOP covers a newly failing fixture; (b) admit it at a port, read as the parent's output step rounding it after inlining. No assertion flips, but a `decimal` value enters the parent as `money_minor` unrounded, and nothing guarantees an output step consumes it; (c) admit it at a port now, and check it at mount (PL 9610's mount-port check, `at_output_step=False`) | **(a).** It is the ruling's text, and the hazard FD 9549 names is a unit changing by declaration without a rounding point. Under (a), a sub-graph exposes the value as `decimal`, and the mounting algorithm's output step rounds it once (FR-226, option (B)). (b) leaves the gap open for sub-graphs. (c) moves the check to a slice that is not merged | the maintainer (by delegation) | item 3 (D9), item 7, activation need 3 |

OQ 9556 is not a DP of this plan: it is recorded by a decision-maker and decided before the
mint (activation need 2).

## Tasks

*Dated note, 2026-10-05 (pre-mint): the tasks are re-ordered so that the sweep runs **before**
the reds, as the 17:42:06 BST decision orders: "PL 9521's sweep, BEFORE its red tasks". The
17:36:28 entry's item 2 wrote "FIRST task is red-first … plus a sweep"; the later entry fixes
the order. The read-first step for `/score` is Task 0 Step 3.*

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm activation needs 1–6 on `origin/main`. Re-read every line cite at
  the dispatch tree and re-anchor it by symbol. A-2, PL 9610, PL 9578 and PL 9688 may have
  moved `compile.py`.
- [ ] **Step 2:** Re-read the write set of every slice in flight against §"Write set". Give the
  lead the `RL 9620` (a)/(b) lines for each same-Work pair (A-2, PL 9728). Record which of A-2
  and this slice merged first, because item 5 and §"Hand-off" depend on it.
- [ ] **Step 3: Read first, the real-time `/score` coercion (item 11).** Read `_build_outputs`
  (`score.py:729`), `_coerce_output_value` (`:950`) and `_outputs_json` (`:991-1002`) at the
  dispatch tree. For each refused class, record in the ledger what `/score` and batch would
  serve for one value. If they differ, item 11's red is due, and its green is a STOP to the
  lead.

### Task 1: The sweep, BEFORE any red (item 7)

- [ ] **Step 1:** In a `mktemp -d` outside the repository, write `closed_rule(producer,
  declared, at_output_step)` as a pure function of the directions table. Write a script that
  collects every committed output and output port with its producer type and `file:line`:
  - the demo (`examples/fremtpl2/model.py`);
  - `scripts/bench-rating.py`, `scripts/bench-score-batch.py` and
    `scripts/bench-compiled-for.py`, through their builder functions;
  - any seed under `backend/src/app/demo/`;
  - every test-module algorithm. Their predicate is
    `git grep -l -E '"(steps|outputs)"' -- 'packages/*/tests' backend/tests`. For each file
    listed, the script calls its builder helpers (`valid_algorithm`, `_fragment`, and the like)
    and records any it cannot call.

  Producer types come from `producer_types` (`compile.py:95`), as the check reads them.
- [ ] **Step 2:** Run the script at the base and keep its output and the script inline in the
  ledger. **Any hit other than DP-1's known `P:389`, an `int` input into a `money_minor`
  output included, is a STOP to the maintainer (by delegation) with `file:line`. Nothing
  further is done until it is answered.** It is not an automatic fallback, and the rule is
  not loosened.

### Task 2: The reds (items 1–6, and 11 if due)

**Files:** `packages/pricing-core/tests/test_rating_compile.py`,
`backend/tests/test_sub_graphs_api.py`.

- [ ] **Step 1:** Write items 1–3 and 5 (P), parametrised over the refused set, with item 6's
  allowed set as the control, and D9 to DP-1's ruling. Run them, and record each red by its
  stated cause.
- [ ] **Step 2:** Write item 4 (B); red (`201`).
- [ ] **Step 3:** If Task 0 Step 3 found a difference, write item 11's red, then STOP to the
  lead for its scope.
- [ ] **Step 4: Commit** (red): `test: money_minor closed both ways, widening only, red first (FR-227, FR-226)`.

### Task 3: The rule (items 1–6, 8)

**Files:** `packages/pricing-core/src/pricing_core/rating/compile.py`.

- [ ] **Step 1:** `_compatible(producer, declared, *, at_output_step)`:

```python
_WIDENING = frozenset({
    ("int", "decimal"), ("count", "decimal"), ("relativity", "decimal"),
    ("percentage", "decimal"), ("count", "int"),
})  # OQ 9556 B3: widening only

def _compatible(producer: str, declared: str, *, at_output_step: bool) -> bool:
    if producer == declared:
        return True
    if producer == "money_minor":          # out of money_minor: only into money_minor
        return False
    if declared == "money_minor":          # into money_minor: decimal, at an output step only
        return producer == "decimal" and at_output_step   # int → money_minor refused (A1)
    return (producer, declared) in _WIDENING   # every other pair refused (B3)
```

  Pairs with a non-numeric type keep their only match, equality, as at `4d3be141`. The
  docstring states the rule and cites the 17:36:28 and 17:42:06 BST entries, and it replaces
  the comment at `:127-128` (item 8). The sketch is against `4d3be141`. A line that does not
  run as written is a plan defect to report, not to work around.
- [ ] **Step 2:** `output_type_issues(types, outputs, *, at_output_step: bool)` passes the flag.
  `_check_result_types` passes `True`, and `fragment_output_type_issues` passes `False`. Every
  other caller found at the dispatch tree (`git grep -n "_compatible(\|output_type_issues(" --
  packages backend/src`) is named in the ledger with the value it passes.
- [ ] **Step 3:** If A-2 is merged: remove its `model_call`-only refusal branch from
  `_check_result_types` / `output_type_issues`, because the general rule covers it through
  `producer_types`. Run A-2's item 15 tests **unedited**; they must pass. Its control must
  already be a legal pair (§"Write set", the A-2 row). Item 5 shows one issue.
- [ ] **Step 4:** Run items 1–6; green. Commit: `fix(rating): money_minor closed both ways; numeric widening only (FR-227, FR-226)`.

### Task 4: The sweep, after (item 7)

- [ ] **Step 1:** Re-run Task 1's script on the slice head, now through `validate_algorithm`
  and `fragment_output_type_issues`. Its refusals must equal Task 1's prediction. **Any other
  difference is a STOP** to the maintainer (by delegation), with `file:line`.
- [ ] **Step 2:** Run item 7's four test files, unedited except under DP-1 (a).

### Task 5: The spec text, only from an `RL-` (activation need 5)

- [ ] **Step 1:** If an `RL-` carries FR-227 text, apply it byte for byte under
  `spec-change`, run `python3 scripts/audit-docs.py`, and commit. Otherwise this task is
  empty, and the ledger says so. This plan drafts no spec text (the lead's brief: "Any spec
  text for FR-227 is a T-text for an RL").

### Task 6: The gate and the ledger (items 9, 10)

- [ ] **Step 1:** The full two-half gate through the gate-runner, holding the one gate slot.
  Record each rc and the tree.
- [ ] **Step 2:** The `LG-` ledger: Task 0 Step 3's readings, the sweep's two outputs and its
  script, every red with its printed line, the `_compatible` callers with their flags, which
  of A-2 and this slice merged first, and `git diff --stat origin/main...HEAD` against
  §"Write set".

## Hand-off

1. The lead mints PL 9521 and SL 9522 after FD 9549 and OQ 9556, and dispatches only after
   §"Activation needs" hold, in a separate activation PR.
2. When this slice merges, FD 9549's event is discharged: "a merged change to `_compatible`".
   The auditor closes it.
3. **To A-2's planner and executor (#1178):** if this slice merges first, A-2's dispatch
   record drops item 15's `model_call`-only refusal branch and keeps the `producer_types`
   typing, and A-2's item 15 tests stay as written. If A-2 merges first, this slice removes
   the branch (Task 3 Step 3). Either way, A-2's control must first become a legal pair: its
   `decimal` → `relativity` control is D13, refused by OQ 9556 B3.
4. **To PL 9610's executor:** `_compatible` now takes a required `at_output_step`. A mount
   port passes `False`.
5. **OQ 9556:** its decision (17:42:06 BST) is written into the directions table, items 1–3,
   6, 7 and 11, and Task 3's sketch. Activation need 2 is met when its row is decided on
   `main` (#1200).

## Self-review

1. **Coverage of the ruling's item 2, clause by clause.**
   - "OUT of money_minor: only into money_minor … for EVERY producer": D1–D5 on three paths
     (items 1–3), plus the route (item 4).
   - "A-2 item 15 stays the model_call instance … without editing A-2's tests": item 5,
     Task 3 Step 3 and Hand-off 3.
   - "INTO money_minor: from money_minor, or decimal AT AN OUTPUT STEP ONLY": A1, A2 and D9
     (DP-1).
   - "Refuse relativity, percentage and count into money_minor": D6–D8.
   - "int→money_minor and the non-money pairs … ONE OQ": OQ 9556, decided at 17:42:06 BST.
     A1 is D10. B3 is D11–D25, and A3–A7 are its allowed widenings. These are items 1–3 and
     6, and activation need 2.
   - "FIRST task is red-first: one red per refused direction, plus a sweep": Task 1.
   - "If one does, STOP and report; do not loosen the rule": item 7, Tasks 1 and 4, DP-1.
   - OQ 9556's "sweep, BEFORE its red tasks … NOT an automatic A3 fallback": Task 1, item 7.
     Its "/score output coercion … a red if it serves a refused pair differently from batch":
     Task 0 Step 3, item 11.
2. **Coverage of item 3** ("AFTER the emergency slice … you sequence it"): activation need 4
   and the contention table. The lead sequences.
3. **Every open design choice has an owner:** DP-1 (the maintainer (by delegation)). OQ 9556 is
   decided. Item 11's green, if a red is due, is the lead's to scope. No spec text is drafted
   (Task 5).
4. **Repository literals read at `4d3be141`:** every line in §"Task 0 at planning time" and
   §"Write set". FD 9549 was read at `9c8a52c6`. Each other plan was read on its branch at
   the head named in the contention table.
5. **What was not executed.** No test, script or code was run. The sketch is against names
   read at `4d3be141`. `score.py`'s anchors (`:729`, `:950`, `:991-1002`) were read at
   `5fe56b87`, whose change since `4d3be141` touches only `docs/`.
