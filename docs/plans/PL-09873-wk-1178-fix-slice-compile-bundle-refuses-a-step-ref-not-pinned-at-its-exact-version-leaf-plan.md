---
id: PL-9873
family: plan
kind: leaf
title: WK-1178 fix slice — compile_bundle refuses a step ref not pinned at its exact version (FR-237): leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: eeda8f4ba20d247ac18d6a35d7f81589c8527ed2
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-9872, PL-1278, PL-1254, RL-1263, FD-1241]
---

# WK-1178 fix slice — `compile_bundle` refuses a step ref not pinned at its exact version (FR-237): leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (the `03` line in Task 2), `python-package` (Tasks 2–3), `python-test` (every task: requirement markers, negative tests), `fastapi-service` (Task 4's route test) and `dev-commands` (the gate), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make FR-237's "Nothing is unpinned" true at compile. `compile_bundle` refuses a Rating Version
when a `table`, `lookup` or `model_call` step names a ref that the version's pins do not carry
**at that exact version**. It refuses with `RATING_VERSION_UNPINNED`, and `03`'s catalogue says
what that code means. The two bare `KeyError`s on the model path at score become coded. After
this slice, no bundle that `compile_bundle` produces can price a step against a missing payload.

**Architecture.** One new function in `pricing-core`'s `compile.py` compares each step's ref with
the pin list of its kind. `compile_bundle` calls it after `check_model_reference_mode`
(`compile.py:464`) and before it resolves the pins (`:466-481`). The two runtime sites become
coded backstops. WK-1250 Slice 2's G1 later calls the same function over the inlined algorithm,
so this slice names it and the executor records it in the slice ledger.

**Tech Stack:** Python 3.12, Pydantic v2 (`model-schema`, read only), `pricing-core`, pytest.
No new dependency.

**Spec:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.4, **FR-237** (`03:134` at
  the tree above): "A **Rating Version** pins: one Rating Algorithm version, an exact Rate Table
  Version per referenced table, an exact Model/Peril Structure version per `model_call`, an exact
  Reference Table Version per `lookup`, and the input contract. Nothing is unpinned."
- `03` §5.1's paragraph "**Error codes owned by this module:**" (`03:772-776`), which lists
  `RATING_VERSION_UNPINNED` with no meaning (Task 2 adds one).
- `03` §4.3's example (`03:355`): a peril structure is pinned under `pins.models`.

**What this plan implements.** The finding filed as #961 (working id 9977; read at its head
`f78d4340451a4684dd58970ad51ce48c122f5222`, which carries the maintainer's dated correction;
first read at `ee33fb99`), titled "compile_bundle does not check step table,
lookup and model refs against the pin set (FR-237)", severity high. Its *Disposition* gives the
maintainer's scope, acceptance and order, and this plan carries them as #961 states them at
`f78d4340`: the null-tolerant case is "written with the `??` consumer", and `coalesce(` "is not an
acceptance case" (#961, *Disposition*). The
relation to the WK-1250 rulings is #938 (working id 9851; read at its head
`2538ca69f0ae73cb326c5cdfb57557cee97f2769`), DP-1 item 6, **G1**. Neither record is minted, so
both are cited by PR and working id. They are re-pointed to their ids when they mint; #961 mints
fifth in the queue.

## Status

**Draft**, filed 2026-09-30 against the tree above under working id 9873. Its slice row is
**SL-9872** (working id), added under `### WK-1178` in `docs/roadmap.md` in this PR. Both take
their real ids at their merge turn. Neither working id appeared among the 9860–9899 hits found
by `git grep -h -o -E '\b98[6-9][0-9]\b' -- docs .claude` and a `docs` filename match over every
`origin/*` branch and the head of every open PR (35 refs). Only 9864, 9871 and 9885 are in use.

**Activation needs:**
1. The decision-maker's rulings on DP-F1, DP-F2 and DP-F3 below.
2. #961 minted, and this plan's two citations of it re-pointed.
3. A free RL-1263 gate slot. Per the lead's dispatch that is the next free slot, about 16:00
   BST on 2026-09-30. It must not pre-empt WK-674 Slice 2 or WK-690 Slice 1 (#961,
   *Disposition*: "It does not pre-empt WK-674 Slice 2 or WK-690 Slice 1: there is no
   production, and 0 stored rating versions are affected so far").
4. The lead's dispatch record, carrying the RL-1263 write-set check (**Write set**, below).

**Order.** This slice **merges before WK-1250 Slice 1 is dispatched**, because `compile.py` has a
single writer (#961, *Disposition*). WK-1250 Slice 2 then builds G1 on top of the function this
slice adds.

### Write set, for the RL-1263 check

RL-1263 option (c): two concurrent build slices "may not both change the same **existing**
function, class, method, spec section, or policy table" (`RL-1263:89`). The registry
exemptions are at `RL-1263:104-116`. This slice changes:

| Path | What changes | Existing definition edited |
|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | a new function `check_step_refs_pinned`; one call inside `compile_bundle`; `__all__` gains the name | **Yes**: `compile_bundle` (`:425-492`) and `__all__` |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `_model_call_handler`'s `handler` (`:436`, the handler at `:457-463`) and `_load_boosters` (`:510-540`) become coded; under DP-F2 (c), `load_bundle` (`:565-579`) gains one call | **Yes**: those functions |
| `docs/specs/03-rating-engine.md` §5.1 | one dated line after the "Error codes owned by this module" paragraph (`:772-776`) | **Yes**: §5.1 |
| `packages/pricing-core/tests/test_rating_pin_membership.py` | new | no |
| `backend/tests/test_rating_version_compile.py` | one test appended | no |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | `_INPUT_FREE` (`:62-75`) gains `("rating/compile.py", "check_step_refs_pinned"): 1` and `("rating/runtime.py", "_load_boosters"): 1`; `("rating/runtime.py", "handler")` changes from 2 to 3 only if the `:463` limb stays (F1, pending) | **Yes**: the `_INPUT_FREE` table |
| `docs/INDEX.md` | regenerated | exempt |

- **`backend/src/app/errors.py` is not changed.** `RATING_VERSION_UNPINNED` is already
  registered at `:298`, under "Bundle compilation (W9-3)".
- **Neither is `MODEL_CALL_FAILED`**, which is already registered (`errors.py:325`). No new code
  is added.

**Against WK-690 Slice 1** (its leaf plan, #954 at `178c6ce0`, working id 9960): that slice
edits only `03` §3.5's FR-244 row, `pricing_core/data/*`, `02`, `skills-map.md`, a
`pyproject.toml` and `uv.lock`. It names `rating/compile.py:245` only as a reference, and edits
neither `compile.py`, `runtime.py` nor `errors.py`. **No shared existing definition. The only
shared file is `03`, in different sections (§3.5 against §5.1).**

**Against WK-674 Slice 2** (PL-1237 Task 2; no leaf plan is open): it adds a deployment-history
`GET` row to `03` §5.1 (`PL-1237:773-774`). **`03` §5.1 is a shared path.** Whether the two slices
may run at once is decided at dispatch on the actual diffs, under `RL-1263:100`. This slice amends
the error-code catalogue; WK-674 Slice 2 appends a route row. Those are not the same definition
unless the diffs show otherwise. It edits no file under `pricing_core/rating/`. *(Revised
2026-09-30 on the lead's relay of the maintainer's dated correction of about 10:25 BST: the first
text said the two serialise.)*

### Dependencies

- **Code: none unmerged.** Everything this slice reads is on `origin/main` at the tree above.
- **Records:** #961 and #938 are unminted and not needed to build. Only the citations wait.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the
failing run is quoted in the ledger, with its failing assert line **and the cause the step
predicts**. A failure for any other cause is a plan defect, reported and not worked around.

1. **Spec, in the same commit as the refusal, written first** (#961, *Disposition*). `03` §5.1
   gains one dated line giving `RATING_VERSION_UNPINNED` a meaning that covers "a step ref not
   pinned at its exact version" (Task 2 has the text). `03` FR-237 is **not** reworded.
   `python3 scripts/audit-docs.py` exits 0 at the committed tree (a working-id gap in check 31 is
   the only permitted red while this plan's own ids are unminted).
2. **Refusal per kind, unpinned and wrong-version, red first**, in
   `packages/pricing-core/tests/test_rating_pin_membership.py`, each marked
   `@pytest.mark.req("FR-237")`. `compile_bundle` raises `CodedError` whose text starts
   `RATING_VERSION_UNPINNED:` and names the step id and the ref:
   - `table`, ref absent from `pins.rate_tables`;
   - `table`, step at `@1`, pinned only at `@2`;
   - `lookup`, ref absent from `pins.reference_tables`;
   - `lookup`, step at `@1`, pinned only at `@2`;
   - `model_call` by `model_ref`, absent from `pins.models`;
   - `model_call` by `model_ref`, step at `@1`, pinned only at `@2`;
   - `model_call` by `peril_structure_ref`, absent from `pins.models` (the `03:355` example
     pins peril structures there).

   **Predicted red** for each: `pytest.raises` reports `DID NOT RAISE`, because
   `compile_bundle` compiles today (#961, *Evidence* 1). A red from any other cause, such as a
   fixture `KeyError` or a validation error, is a plan defect.
3. **The consumer cases that priced wrong are refused at compile, red first.** Each case is the
   exact algorithm of #961's tables, written with `??`:
   - auditor-922's lookup case (#961 Table 2, row "(a) `??`, lookup UNPINNED", priced
     **1370**);
   - its wrong-version row (step `@1`, pin `@2` only, priced **1370** against a right answer of
     2740);
   - auditor-922's table case (#961, "Table step through a tolerant consumer": `on_miss="default"`,
     `s_office` = `risk_premium_minor * (expense_factor ?? 1.0)`, rate table unpinned, priced
     **1370** against 1507 pinned);
   - auditor-933's lookup and table cases (#961 Table 3, rows (b) and (c), priced **100000**).

   Each is refused with `RATING_VERSION_UNPINNED`. The ledger also quotes the **pre-fix** price
   of each case, from a scratch run at the pre-change tree that is never committed. That
   price must be 1370 or 100000 as the finding reports; a different pre-fix price is
   reported, not explained away.
4. **Controls stay green:**
   - auditor-922's control (step and pins at `@1`) prices **1507**;
   - its wrong-version control (step `@2`, pin `@2`) prices **2740**;
   - auditor-933's controls price **130000** (`@1`/`@1`) and **180000** (`@2`/`@2`);
   - #961 Table 1's "both table v1 and v2 pinned" row still compiles and prices **1507**
     (DP-F3 (a)).

   **Every refused case and every control uses the `??` consumer only.** **`coalesce(` is refused
   at compile at this tree**, so it is not an acceptance case *(revised 2026-09-30, on the
   maintainer's dated correction relayed by the lead, now in #961 at `f78d4340`)*.
   `_check_vocabulary` (`compile.py:233-258`) refuses it with `EXPRESSION_INVALID_VOCABULARY`.
   #961 reports it found by auditor-924d and re-run by the filer. The planner re-ran it as well:
   `zen.compile_expression('a * number(coalesce(x, "1.0"))')` raised
   `{"type":"parserError","source":"Incomplete parser output"}`, and the same expression written
   with `??` compiled. **`coalesce(` is outside this slice,** pending the decision-maker's ruling on
   `??` and FR-244.
5. **The model path is coded at score** (the `KeyError` at `runtime.py:463` and `:533`), red first.
   Any coded outcome meets the requirement. #961 at `f78d4340` says so ("Any coded outcome, such as
   `MODEL_CALL_FAILED` through the sentinel, meets the requirement"), and names the sentinel path
   as what "coded" means for the handler. The unpinned case is refused at compile anyway, so these sites are
   backstops. The mechanism is DP-F2's.
   Both tests use a hand-built `Bundle` whose `resolved_payloads` lack the step's model ref. It
   bypasses `compile_bundle`, as a pre-fix stored bundle would.
   - **A GBM model** (`_load_boosters`, `:533`). `load_bundle` raises `CodedError`
     `RATING_VERSION_UNPINNED: …`. Predicted red: `KeyError 'model:motor-freq@1'`.
   - **A GLM model** (the handler, `:463`). **Held for the decision-maker's amendment of DP-F2
     (auditor-933's F1):** through `load_bundle` this site is unreachable, because `_load_boosters`
     (`:533`) indexes every `model_call` payload first. This bullet is dropped, or rewritten to use a
     hand-built `CompiledBundle`, as the ruling says. Under DP-F2 (a) or (b), `score_one` raises
     `CodedError` `MODEL_CALL_FAILED: …`, naming the ref as unpinned. Under DP-F2 (c),
     `load_bundle` refuses first, with `RATING_VERSION_UNPINNED`. Predicted red under (a) or (b):
     `RuntimeError` `NodeError`, the zen binding's wrapping of the handler's `KeyError`
     (`runtime.py:85-91`). Under (c) it is `load_bundle` returning.
5a. **Under DP-F2 (c) only: a pre-fix bundle is refused at load, red first.** A `Bundle` built
    as a pre-fix `compile_bundle` would have built it passes to `load_bundle`. It carries an unpinned
    `lookup` ref, and in a second case a wrong-version `table` ref (step `@1`, pin `@2`), each with
    the `??` consumer and each with its payloads present only for what the pins name. `load_bundle`
    raises `CodedError` `RATING_VERSION_UNPINNED`. **Predicted red:** `load_bundle` returns, and
    scoring the bundle prices 1370. The ledger quotes that price. *(Added 2026-09-30 on the lead's
    relay of the maintainer's pre-acceptance of DP-F2 (c).)*
6. **Through the platform** (`backend/tests/test_rating_version_compile.py`), red first. A
   version whose algorithm's `table` step names a rate table the pins do not carry fails its
   compile Job with `job_row.error["code"] == "RATING_VERSION_UNPINNED"`. Mirror
   `test_an_unpinned_version_is_refused_over_http` (`:181-195`) and do not invent new helpers.
7. **Every existing fixture still compiles** (premise q predicts no correction), or is corrected by pinning its ref. The fixture is
   corrected, never the check. Each correction is listed in the ledger with its file:line.
   **One guard test changes by design, and it is not a fixture.** NFR-499's raise-site guard,
   `packages/pricing-core/tests/test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case`,
   counts every `_raise_named`, `CodedError(` and `_model_call_failure(` call per function under
   `pricing_core/rating` (`:84-110`). It asserts that the count equals `_INPUT_FREE` (`:62-75`),
   and that listed sites are input-free. Each new site in this slice is artifact-level: it names a
   step id and a ref string, never a quote value. So each one is listed in `_INPUT_FREE`, **in the
   same commit as the site**, with a one-line reason:
   - `("rating/compile.py", "check_step_refs_pinned"): 1` (Task 2). Write the function with **one**
     `_raise_named` call. If it has two, the count is 2 and the comment says why;
   - `("rating/runtime.py", "_load_boosters"): 1` (Task 3);
   - `("rating/runtime.py", "handler"): 3`, up from 2, **only if** the decision-maker keeps the
     `:463` limb (F1, below).

   `("rating/compile.py", "compile_bundle")` stays 5: the new call is to
   `check_step_refs_pinned`, not to a site name, and so is DP-F2 (c)'s call in `load_bundle`.
   Predicted red at Task 2 before the entry is added: the guard's "a `_raise_named` site is not
   accounted for" assert. auditor-933's scratch patch gave "1 failed, 201 passed". *(Added
   2026-09-30 on auditor-933's F2 against #963.)*
8. **The `??` operator is untouched.** `git diff origin/main...HEAD --
   packages/pricing-core/src/pricing_core/rating/compile.py` shows no change to
   `_GUARD_MARKERS` (`:41`), `_check_vocabulary` (`:233`) or any expression handling. `??` is a
   separate §0 question with the decision-maker (#961, *Related, not part of this fix*).
9. **The reusable function is recorded.** The slice ledger records `check_step_refs_pinned`'s
   symbol, file and signature at the merged tree, for WK-1250 Slice 2's G1. #938, DP-1 item 6:
   "The builder records the function's symbol and file in its slice ledger".
10. **Coverage.** `uv run python scripts/req-coverage.py` lists the new tests against FR-237.
11. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree. The
    ledger quotes every command's rc, the `N passed` line and `HEAD`, and compares `N passed`
    with `origin/main`'s.
12. **Item 11.** Before the lead merges, the maintainer's **MERGE-ACK**, naming the PR's full
    head SHA, is recorded in the lead's channel file. That is a local file outside the
    repository, `~/gi-pricing-plan.local/channel/to-lead.md`, which `.claude/roles/lead.md:156-157`
    (rule 4) names. **It is never posted on the PR.** The slice's clean audit is filed. Per
    `CLAUDE.md` §13 a Slice closes on a clean audit and the lead's merge. No maintainer
    acceptance line is required for a slice, and none is to be waited on.

## Global Constraints

- **`pricing-core` stays standalone** (`.importlinter`). The check reads `model_schema` shapes
  only, and raises `CodedError` from `pricing_core.safe_error`, never `PlatformError`.
- **One implementation, never a copy** (#938, DP-1 item 6). G1 calls this function later, and
  nothing else re-implements the comparison.
- **Exact string equality on `type:slug@version`.** No "latest", no range, no slug-only match.
- **A refusal's message is input-free** (`safe_error.py:64-70`). It names the step id and the ref
  string, which are artifact identifiers, never a quote value.
- **Do not change `??`, FR-244, `_GUARD_MARKERS` or `_check_vocabulary`** (acceptance 8). `??` is the decision-maker's pending §0 ruling.
- **Money** stays integer minor units. The controls assert exact integers.

## Scope

### Requirement coverage

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.4 | FR-237 | "Nothing is unpinned", enforced at compile for `table`, `lookup` and `model_call` step refs, and backstopped at load and score for the model path |

**Not in this slice:**
- `SubGraphRef` against `Pins.sub_graphs`, and fragment refs → **WK-1250 Slice 2**, G1, reusing
  this function.
- Whether `??` belongs in the grammar → **the decision-maker**, §0 (#961).
- An **unreferenced** extra pin (DP-F3) → not refused here.
- `custom_objectives` pins are reached through a model, not named by a step. They are not
  compared, and FR-240 clause (6) stays WK-690's (#938).

### Premises, read at the tree above

| # | Premise | Evidence |
|---|---|---|
| a | `compile_bundle` resolves the pins and never compares a step's ref with them | `compile.py:466-481`: `all_refs` is built from the four pin lists only; no line reads a step ref |
| b | It already raises `RATING_VERSION_UNPINNED` for a missing `algorithm_ref` or `pins` | `compile.py:434-443` |
| c | `_raise_named` raises `CodedError(f"{code}: {message}")` | `compile.py:421-422`; `CodedError` is a `ValueError` subclass (`safe_error.py:64`) |
| d | The step ref fields | `RatingTableStep.rate_table_ref` and `RatingLookupStep.reference_table_ref` (`model_schema/rating.py:275-288`); `RatingModelCallStep.model_ref` / `peril_structure_ref`, exactly one set (`:297-311`) |
| e | `Pins` has `rate_tables`, `models`, `reference_tables`, `custom_objectives` | `model_schema/rating.py:63-76` |
| f | A peril structure is pinned under `pins.models` | `03:355`, the §4.3 example: `"models": ["peril_structure:motor-gb-2026h2@2"]` |
| g | The model handler indexes `payloads[ref_str]` inside a zen custom handler; the booster loader does the same in `load_bundle` | `runtime.py:463`; `runtime.py:533` in `_load_boosters`, called from `load_bundle` at `:579` |
| h | An exception raised inside a zen custom handler surfaces as a generic `RuntimeError` `NodeError`; a handler reports failure through `_model_call_failure`'s sentinel, which `score_one` raises as `CodedError` | `runtime.py:81-121` (the finding at `:85-91`, the sentinel at `:120`); `score.py:443` |
| i | `runtime.py` imports from `compile.py`, not the reverse | `runtime.py:50`: `from pricing_core.rating.compile import Bundle, JdmGraph`; `compile.py` imports no `runtime` |
| j | `Bundle` carries `pins` | `compile.py:484-491` (`Bundle(..., pins=pins, ...)`) |
| k | The score fixture is #961's base: `rate_table:motor-expense@1` and `model:motor-freq@1`, pinned at `@1` | `packages/pricing-core/tests/test_rating_score.py:46-140` (`_algorithm_payload`, `_FakeResolver`, `_version`, `_compiled`) |
| l | Cross-module test helper imports are the local precedent | `packages/pricing-core/tests/test_safe_error.py:28` (`from test_rating_score import _compiled`) |
| m | A reference-table payload is `{"rows": [{"key", "payload", "effective_from", "effective_to"}]}` | `packages/pricing-core/tests/test_rating_runtime.py:458-466` |
| n | `RATING_VERSION_UNPINNED` and `MODEL_CALL_FAILED` are registered | `backend/src/app/errors.py:298`, `:325` |
| o | The platform test that asserts the compile Job's code | `backend/tests/test_rating_version_compile.py:181-195` |
| p | `03` §5.1's catalogue is a bare list, and the code has no meaning in the spec | `03:772-776`; `git grep -n RATING_VERSION_UNPINNED -- docs/specs` prints only `03:774` |
| q | **No existing fixture is refused by the new check. One guard test changes by design:** NFR-499's raise-site count (acceptance 7), which is not a fixture *(corrected 2026-09-30 on auditor-933's F2 against #963; the sweep below covered fixtures only)*. Every fixture that compiles pins each step ref at its exact version. The backend and example fixtures have no `table`, `lookup` or `model_call` step at all. No test passes a hand-built `Bundle` to `load_bundle` | A read-only sweep at the tree above, by a subagent; the planner took its conclusion, not its dumps. Two examples: `test_rating_compile_bundle.py:45-55` against `:77-88`, and `test_rating_score.py:46-70` against `:116-133`. `test_testing.py`'s `_VariantResolver` pins a model no step names, a superset that DP-F3 (a) keeps legal. The pattern: `grep -rn "compile_bundle\|load_bundle\|compile_rating_version" --include=*.py .`, then each fixture's `"type": "(table\|lookup\|model_call)"` steps compared with its `pins` |

The executor re-reads each at its own tree and stops on any that no longer holds
([`README.md`](README.md) convention 4).

### Decision points

Each is the decision-maker's (`delivery-process.md` §3). The planner rules none of them. The
maintainer has already decided the code (`RATING_VERSION_UNPINNED`), the severity, the owner,
the order and the acceptance (#961, *Disposition*). None of that is reopened here.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-F1 | Where does the comparison live, under what name? | (a) `pricing_core.rating.compile.check_step_refs_pinned(algorithm: RatingAlgorithm, pins: Pins) -> None`, raising `CodedError` `RATING_VERSION_UNPINNED` on the first mismatch in step order, exported in `__all__`; (b) `model_schema.rating`, beside `check_model_reference_mode` (`:171`), raising a bare `ValueError` that `compile_bundle` would have to re-code; (c) inline in `compile_bundle`, no separate function | **(a).** The code is a `pricing-core` error (premise c), and `runtime.py` can import it (premise i) for DP-F2 (c). G1 needs a named function to call, which rules out (c). (b) puts a coded rating refusal in the shared-shape package, and `model_schema/__init__.py` is a file every slice exporting a shape touches | decision point | yes — Task 2 | |
| DP-F2 | How far does the backstop go at load and score, for a bundle not produced by the fixed `compile_bundle` (for example one compiled and stored before this fix)? | (a) The minimum: `_load_boosters` (`:533`) raises `CodedError` `RATING_VERSION_UNPINNED` naming the ref, and the handler (`:463`) returns `_model_call_failure(step, …)`, so `score_one` raises `MODEL_CALL_FAILED`. A raise cannot be used there (premise h). `table` and `lookup` stay as today at score: a missing payload still builds an empty decision table (#961, *Evidence* 1); (b) as (a), with the handler's text starting `RATING_VERSION_UNPINNED` inside the sentinel so the reader sees the cause; (c) as (a), and `load_bundle` calls `check_step_refs_pinned(algorithm, bundle.pins)` first (premise j), so a stored bundle with an unpinned or wrong-version step of **any** kind is refused before it can score | **(c).** (a) and (b) code the model path, but leave a pre-fix stored bundle able to price a `table` or `lookup` step silently at a wrong premium, which is the finding's defect. #961 at `f78d4340` (*Evidence* 5) reports 0 affected in PostgreSQL and in 6519 MinIO bundles, but it leaves 3986 algorithm-shaped blobs in `gip-test-blobs`, which carry no pins, unchecked. (c) costs one call on a path with no I/O, reuses DP-F1's function, and closes the class at load. The two runtime sites stay coded as unreachable backstops. The maintainer has pre-accepted (c) as within scope if it is ruled (the lead's relay); the ruling is still the decision-maker's. Under (c), acceptance 5a applies | decision point | yes — Task 3 | |
| DP-F3 | Is a pin that no step references refused? #961 Table 1: "Both table v1 and v2 pinned … the v1 pin is used; the extra v2 pin is ignored" | (a) No. This slice refuses only a step ref not pinned at its exact version, and an extra pin stays allowed; (b) yes: refuse any `rate_tables`, `models` or `reference_tables` pin that no step names | **(a).** FR-237 says every reference is pinned, not that every pin is referenced. #961's scope is refs not pinned. Under (b), `custom_objectives` pins, which no step names (they are reached through a model), would need an exemption, and a rule would be written without a spec line. A second rule is a spec change first | decision point | yes — Task 2's acceptance 4 row | |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch.
- [ ] `uv sync --all-packages` (`dev-commands`).
- [ ] Re-derive premises a–p; record the tree and each result in the ledger.
- [ ] `gh pr list --state open`, and read anything that rules on FR-237, `compile.py`,
  `runtime.py`, `03` §5.1 or `??` ([`README.md`](README.md) convention 4). Name the SHA read.
  **Confirm #961 and #938 are minted** and re-point this plan's citations if the lead asks.
- [ ] Confirm DP-F1 to DP-F3's resolutions, by record id, in the ledger.
- [ ] Confirm the RL-1263 slot and the dispatch record's write-set check.

### Task 1: The red tests

**Files:** Create `packages/pricing-core/tests/test_rating_pin_membership.py`.

**Interfaces:**
- Consumes: from `test_rating_score` — `_algorithm_payload`, `_FakeResolver`, `_version`, `_ctx`
  (premises k, l); `compile_bundle`, `load_bundle`, `score_one`, `CodedError`.
- Produces: the tests of acceptance 2–5, and 5a under DP-F2 (c). They go red now and green after Tasks 2–3.

- [ ] Build each variant by **copying and editing** the fixture's dicts: a step's ref, and the
  version's `pins`. Do not mutate the shared helpers. For `@2` artifacts, add payloads to a local
  resolver whose `resolve` returns `ResolvedArtifact(status="approved", payload=…)`, as
  `_FakeResolver` does (`test_rating_score.py:103-115`).
- [ ] **Lookup variants.** Replace `s_expense` with a `lookup` step on
  `reference_table:expense@1`, with rows `direct → "1.1"` and `broker → "1.25"`, and `@2` at
  `direct → "2.0"`. Use `on_miss="default"` and `s_office`'s expression
  `risk_premium_minor * number(expense_factor ?? "1.0")`. The payload shape is premise m.
- [ ] **Table variant.** Keep `s_expense` as the fixture's `table` step, with `on_miss="default"`,
  and set `s_office`'s expression to `risk_premium_minor * (expense_factor ?? 1.0)` (#961 at
  `f78d4340`, "Table step through a tolerant consumer").
  These literals are #961 Table 2's. Re-verify them against its text before use.
- [ ] **auditor-933's variants.** A minimal algorithm:
  - an input `base_minor` (int), given 100000;
  - a `lookup` producing `veh_loading` from `reference_table:veh@1` (`"1.30"`; `@2` `"1.80"`);
  - a `table` producing `veh_factor` from `rate_table:veh@1` (1.30; `@2` 1.80);
  - expressions `base_minor * number(veh_loading ?? "1.0")` and `base_minor * (veh_factor ?? 1.0)`;
  - an `output` step.

  Build it from the score fixture's step shapes. Do not invent a new field.
- [ ] Controls first (acceptance 4). They must be **green before any change**: 1507, 2740, 130000,
  180000. If one is not, stop and report.
- [ ] The refusal tests (acceptance 2, 3) and the model-path tests (acceptance 5). Run them and
  quote the reds with their causes.
- [ ] The scratch pre-fix prices of acceptance 3, quoted in the ledger, never committed.
- [ ] Commit the tests, red: `test(rating): FR-237 pin-membership refusals, red (WK-1178 fix slice)`.
  The gate stays red until Task 2, and the slice branch is not pushed for merge in between.

### Task 2: The spec line and the compile refusal — one commit, spec first

**Files:** Modify `docs/specs/03-rating-engine.md` (after `:776`, the end of §5.1's code list);
`packages/pricing-core/src/pricing_core/rating/compile.py`.

**Interfaces:**
- Produces: `check_step_refs_pinned(algorithm: RatingAlgorithm, pins: Pins) -> None` (per
  DP-F1 (a)). G1 and DP-F2 (c) consume it.

- [ ] **Spec first.** Add one dated line after the catalogue paragraph:

  > *`RATING_VERSION_UNPINNED` (meaning added 2026-09-30, on the finding filed as #961, FR-237):
  > the Rating Version cannot be compiled because it has no `algorithm_ref`, has no `pins`, or
  > has a `table`, `lookup` or `model_call` step whose ref is not in the matching pin list
  > (`rate_tables`, `reference_tables`, `models`) at that exact version.*

  Replace "#961" with the finding's id if it is minted by then. `python3 scripts/audit-docs.py`.
- [ ] The function, below `_raise_named` (`:421`). It iterates `algorithm.steps` in order. For
  each `RatingTableStep`, `RatingLookupStep` and `RatingModelCallStep` it takes the ref and the pin
  list of its kind: `pins.rate_tables`, `pins.reference_tables`, or `pins.models` for either model
  ref. If `str(ref)` is not among the list's strings, it calls `_raise_named(
  "RATING_VERSION_UNPINNED", …)`. The message names the step id and the ref. When the same
  `type:slug` is pinned at another version, it adds "pinned at <that ref> instead", so the
  wrong-version case reads differently from the absent case under one code.
- [ ] Call it in `compile_bundle` immediately after `check_model_reference_mode(version,
  algorithm)` (`:464`), before `payloads` is built. Add it to `__all__`. Update
  `compile_bundle`'s docstring clause list.
- [ ] In `packages/pricing-core/tests/test_quote_input_raise_sites.py`, add
  `("rating/compile.py", "check_step_refs_pinned"): 1` to `_INPUT_FREE` with the comment
  `# step id and ref string (artifact-level, compile time), no quote` (acceptance 7). Run the
  guard: red before the entry, green after.
- [ ] Acceptance 2, 3 and 4 green. Acceptance 8's diff check. Commit, spec and code together:
  `fix(rating): compile_bundle refuses a step ref not pinned at its exact version (FR-237, WK-1178)`.

### Task 3: The coded backstops at load and score

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/runtime.py`,
`packages/pricing-core/tests/test_quote_input_raise_sites.py` (`_INPUT_FREE`).

- [ ] `_load_boosters` (`:531-533`): when `ref_str not in payloads`, raise through `CodedError`
  with `RATING_VERSION_UNPINNED: model_call step <id> names <ref>, which the bundle does not carry
  (FR-237)`. Import `CodedError` from `pricing_core.safe_error`, as `compile.py:37` does. Add
  `("rating/runtime.py", "_load_boosters"): 1` to `_INPUT_FREE` in the same commit (acceptance 7).
- [ ] **Held for the decision-maker (F1).** The handler (`:462-463`): when `ref_str not in
  payloads`, `return _model_call_failure(step, …)` with the same text. Do not raise: premise h.
  Update `("rating/runtime.py", "handler")` from 2 to 3. auditor-933's F1 found this site
  unreachable through `load_bundle`: `_load_boosters` indexes every `model_call` payload first
  (`runtime.py:533`, called at `:579`). The decision-maker is amending DP-F2 either to drop this
  limb or to keep it with a hand-built `CompiledBundle` test. This step and acceptance 5's GLM
  bullet follow that ruling.
- [ ] DP-F2 (c) only: in `load_bundle`, before `_load_boosters` (`:579`), call
  `check_step_refs_pinned(algorithm, bundle.pins)`.
- [ ] Acceptance 5 green. Commit: `fix(rating): code the model path's missing-payload failures (FR-237, WK-1178)`.

### Task 4: Through the platform, and the fixture sweep

**Files:** Modify `backend/tests/test_rating_version_compile.py` (one test appended); any fixture
acceptance 7 finds.

- [ ] Acceptance 6's test, red first. Predicted red: the Job **succeeds**, because the backend
  resolver resolves only pins. A red from anything else, such as the DB stack being absent, is not
  the proof ([`dev-commands`](../../.claude/skills/dev-commands/SKILL.md)).
- [ ] Run `uv run pytest -q packages/pricing-core backend/tests` and list every **newly** refused
  fixture. Fix each by pinning its ref (acceptance 7), and cite each in the ledger.
- [ ] Commit.

### Task 5: The gate and the ledger

- [ ] The full two-half gate on the committed tree, with each rc, the `N passed` line and `HEAD`,
  against `origin/main`'s `N passed`.
- [ ] The ledger records:
  - the tree, and premises a–p;
  - the red quotes, and the pre-fix prices;
  - the DP resolutions by record id;
  - the fixture corrections;
  - **`check_step_refs_pinned`'s symbol, file and signature** (acceptance 9).
- [ ] Item 11 (acceptance 12).

## Hand-off

WK-1250 Slice 2's G1 calls `check_step_refs_pinned` over the inlined algorithm, and adds only the
`SubGraphRef` against `Pins.sub_graphs` check (#938, DP-1 item 6). The planner's delta records to
PL-1254 and PL-1278 cite this slice's merged symbol once it exists.

## Self-review

- **The finding's disposition, clause by clause:**
  - refuse table, lookup and `model_call` at the exact version with `RATING_VERSION_UNPINNED` →
    Task 2, acceptance 2;
  - the catalogue meaning, spec first, in the same commit → Task 2, acceptance 1;
  - the model-path `KeyError` coded → Task 3, acceptance 5;
  - red first per kind, unpinned and wrong-version → acceptance 2;
  - the `??` cases (1370 and 100000) → acceptance 3; `coalesce(` is refused at compile and outside this slice (acceptance 4);
  - DP-F2 (c), pre-accepted by the maintainer if ruled → acceptance 5a;
  - controls 1507, 2740, 130000 and 180000 → acceptance 4;
  - the order and the slot → Status;
  - `??` untouched → acceptance 8;
  - G1's reuse → acceptance 9, Hand-off.
- **FR-237 read to its clauses** (`03:134`): "exact Rate Table Version per referenced table" →
  `table`; "exact Model/Peril Structure version per `model_call`" → both model refs; "exact
  Reference Table Version per `lookup`" → `lookup`; "one Rating Algorithm version" → already
  refused (premise b); "the input contract" is not a pin list and is out of this check.
- **Literals** were read at the tree above (premises). `check_step_refs_pinned` and the new test
  file are proposals, named once each and used consistently in Tasks 1–5.
- **Open:** DP-F1 to DP-F3, the decision-maker's; #961 and #938 unminted.
