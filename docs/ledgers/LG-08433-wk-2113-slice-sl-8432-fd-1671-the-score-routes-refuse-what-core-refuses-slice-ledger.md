---
id: LG-8433
family: ledger
title: WK-2113 slice SL-8432 — FD-1671: the score routes refuse what core refuses (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-13
owner: executor
tree: 2ba0d0d53142dacd6550cb314a4d65685b612bd1
phase: P3
work: WK-2113
slice: SL-8432
plans: []
corrected_by: []
relates: [SL-8432, FD-1671, OQ-1672]
---

# LG-8433 — WK-2113 slice SL-8432: FD-1671, the score routes refuse what core refuses

Executed by seat `exec-sl8432`, base `origin/main` `2ba0d0d53142dacd6550cb314a4d65685b612bd1`, branch `sl-8432-fd1671-score-decimal`.

**GO:** the maintainer's entry "2026-11-13 19:53:34 GMT — Maintainer: RULINGS R1–R3", item (R2), verbatim:

> (R2) FD-1671: (i) SEVERITY MEDIUM, on the probe — POST /score returned 200 with 41234 where the exact Decimal price is 41235 (I2: a 20-significant-digit factor), 1 minor unit low, no warning; reachable only with a 16+ significant-digit Rating Input; the LOW of 2026-10-12 is superseded by a dated line on the row and essay, its FR-244 reason kept as written (the engine float is not the loss; the unrefused parse is). (ii) GO, slice WK-2113 S2 "FD-1671: the score routes refuse what core refuses", builder 2 in parallel with S1 (disjoint files; one gate at a time, S1's gate first). (iii) DESIGN (b): the score request bodies parse JSON numbers of Rating Inputs as Decimal, scoped to the scoring routes only, so core's FR-273 guard is the one definition and HTTP refuses exactly as core does; no second digit-counter. This implements FR-273, it does not choose an open design. CONDITIONS: (a) red first: I2 returns 200/41234 at 2ba0d0d5, then 422 INPUT_CONTRACT_VIOLATION as an RFC 9457 problem naming the input; I3 likewise refused; I1 (15 digits) still 200/41234. (b) EVERY scoring path: /score, both sides of /score/compare, and the batch path — the probe ran /score only; each path is read and tested, or named as not reachable by a JSON number with the reason. (c) FR-239, same hash same price: for every input of at most 15 significant digits the price is IDENTICAL before and after — proven by the existing golden-quote suite unchanged plus a property test that float(Decimal(text)) == float(text) over generated ≤15-digit texts and that the priced result is equal on both parses; no spec_hash moves. (d) the parse hook is scoped to the score request models, not app-wide (no other route's floats become Decimal); a test asserts a non-scoring route still parses float. (e) integers, booleans and strings are untouched; an input typed `float` receiving a Decimal behaves as today (test). (f) the stubbed reading is completed: one create_app()+DB test in the gate's DB window. (g) the contract: `generate-contracts.py --check` stays 0 or the regenerated contract is in the commit; the frontend half of the gate runs. (h) spec: 03 §5.1's /score row and FR-273 carry a dated line that the HTTP paths refuse over-precision inputs with the same code; the register row and essay re-rated and closed against the slice.

**MERGE-ACK:** not yet given.

## Tasks

### Scope

Slice `SL-8432` (roadmap row under WK-2113, `active`). Requirements covered: **FR-273** (the HTTP paths refuse what core refuses: amended by a dated line), **FR-239** (same hash, same price: guarded, no `spec_hash` moves), **FR-250** and **FR-262** (the two routes; §5.1's `/score` row carries the dated line), **FR-259** (a sampled quote's stored context). No Work plan row exists yet for this slice (`plans: []`); the GO above is the scope of record.

Not in scope, by the GO: OQ-1672's wire form (a decimal Rating Input stays a JSON number), the string-typed decimal (refused today, read in the probe's I6), money inputs.

### Task list

1. **Red first** (condition (a)): the tests committed alone at `265542e3`, run at that commit.
2. **Every scoring path** (condition (b)): the routes read below.
3. **Fix**: a score-only route class reading JSON floats as `Decimal`; core's guard refuses; the existing handler maps to 422.
4. **FR-239 property test** (condition (c)).
5. **Contract** (condition (g)): `generate-contracts.py --check`.
6. **Spec and records** (condition (h)): `03` FR-273 and §5.1, FD-1671's row and essay, the roadmap row.
7. **The create_app()+DB test** (condition (f)): written, not run by this seat.

### Gate

Not a full gate: the lead runs it (S1's first). The seat's runs are in the Build log; every log opens `head=` and ends `rc=`.

Seat runs at head `6ccc0a5fe5d7f94ff7acaa46574c47683711462f` (tree: that commit plus this ledger, `docs/INDEX.md`, the roadmap row, FD-1671's row and essay, and `03`'s two dated lines, uncommitted when run), no full gate, no database, no `createdb`, no mint:

| command | rc | reading |
|---|---|---|
| `uv run --directory <wt> ruff check .` | 0 | `All checks passed!` |
| `ruff format --check` on the four new or changed `.py` files | 0 | (`pricing-core/.../rating/score.py` is not format-clean on main and is left as it is) |
| `uv run --directory <wt> mypy` | 0 | `Success: no issues found in 257 source files` |
| `uv run --directory <wt> lint-imports` | 0 | `Contracts: 4 kept, 0 broken.` |
| `generate-contracts.py --check` | 0 | `58 generated contracts match the models` |
| `doc-index.py` / `doc-index.py --check` (gate-2) | 0 / 0 | regenerated after the ledger and the roadmap row |
| `register-lint.py` (gate-2) | 0 | `register.md: OK (0 violations)` |
| `req-coverage.py` (gate-2) | 0 | `FR-239  37 test file(s)`, `FR-273  38 test file(s)` |
| `audit-docs.py` (gate-2) | **1** | `FAILED (1): check 31: gap in the full allocation between 2115 and 8432`: the slice's own working ids (item 31's class); no other check fails |
| GREEN set, non-DB, 40 files via run-small in 14 batches (`green-nodb.log`) | see below | 11 batches `batch rc=0` (pricing-core and `tests/`); 3 batches rc=1 on `ERROR` at setup only |
| spec-reading set (items 39/40), 20 files (`specreading.log`) | see below | see below |

`test_error_sinks.py` (item 45; `errsinks.log`): `9 passed, 2 warnings, 4 errors`, rc=1, every error `RuntimeError: GIP_TEST_DATABASE_URL is not set, and the per-worktree test database 'gipricing_sl-8432_894ad706' does not exist yet` (a fixture needing the database, not a red).

### Audit

*(Written by the auditor.)*

### Build log

#### 2026-11-13 — red first, at `265542e389b9fc5760ba40d7d81c546b66a8e03e` (tests only, tree = base + 3 new test files)

Command: `scripts/run-small.sh <wt> backend/tests/test_score_decimal_input_http.py` (log `scratch/exec-sl8432/red-http-E.log`, local), the route being the real `app.api.score` router on a bare app with the app's error handlers and the auth, rate-limit, session and resolution dependencies stubbed (the probe's harness, `scratch/exec-fd1671p/probe.md`). Result: `4 failed, 9 passed`, rc=1. Each failure, verbatim (`E` lines; the 200 body is cut by the log):

| test | failure line | head | rc |
|---|---|---|---|
| `test_i2_a_20_digit_decimal_input_is_refused_not_rounded_and_priced` | `E       assert 200 == 422` (body `{"outcome":"quoted",…`, premium 41234; exact price 41235) | `265542e3` | 1 |
| `test_i3_a_20_digit_decimal_input_below_the_rounding_boundary_is_refused_too` | `E       assert 200 == 422` | `265542e3` | 1 |
| `test_compare_refuses_an_over_precision_input_and_names_the_side[0.82469000000000000002]` | `E       assert 200 == 422` (body `{"base":{"outcome":"quoted",…`) | `265542e3` | 1 |
| `test_compare_refuses_an_over_precision_input_and_names_the_side[0.82468999999999999998]` | `E       assert 200 == 422` | `265542e3` | 1 |

Green on both sides (guards): I1 (15 digits, 200, 41234), compare on I1 (41234), a route outside the scoring routes keeps `float`, `/score/batch` keeps the default route class and has no `inputs` field, ints/bools/strings reach the engine as themselves, an exactly representable decimal prices as before, an int-declared input given `50000.0` is refused as before, an undeclared float input is tolerated as before. `test_rating_score_decimal_parse_equivalence.py`: `3 passed`, rc=0 at `265542e3` (a guard: FR-239 holds on today's tree). **I2's failure is the finding**: the route answers 200 with the premium of the rounded float, 1 minor unit below the exact price.

#### 2026-11-13 — condition (b): every scoring path, read

Routers grepped: `git grep -n -E "QuoteContext|score_one|ScoreCompareRequest" -- backend/src`.

| path | takes a Rating Input as a JSON number? | evidence |
|---|---|---|
| `POST /api/v1/score` | yes: `ctx: QuoteContext`, `inputs: dict[str, object]` | `backend/src/app/api/score.py` `score`; red test I2, I3 |
| `POST /api/v1/score/compare`, base side | yes: `ScoreCompareRequest.context` | `score_compare`; red test, `base: ` named |
| `POST /api/v1/score/compare`, comparison side | yes, the same `context`, scored second | the base side refuses first, so the comparison side is reached only when the base side priced the same inputs; the one `body.context` is parsed once for both sides, so the base-side test covers the parse of both; a refusal on the comparison side alone (a different bundle) is the same `score_one` guard, named `comparison: ` by `_naming_side` |
| `POST /api/v1/score/batch` | **no**: `BatchScoreRequest` is a Dataset Version id, Rating Version refs and three numeric knobs, never a Rating Input | `test_the_batch_route_takes_no_rating_input_over_json` (the field set); rows come from the Dataset Version's table in `app.worker.scoring_handlers`, not from JSON |
| the off-path trace re-score (`app.worker.trace_handlers`) | no HTTP body: it reads a stored context | the stored context is now written with the input a JSON number (`_stored_context`; `test_a_stored_quote_context_keeps_a_decimal_input_a_json_number`, and the DB test of condition (f)) |
| any other router | none takes a `QuoteContext` | `git grep -n "QuoteContext" -- backend/src` hits only `app/api/score.py`, the two workers and `platform/traces.py` |

#### 2026-11-13 — the fix, at `6ccc0a5fe5d7f94ff7acaa46574c47683711462f`

`backend/src/app/api/score.py`: `_DecimalJSONRequest` (`json()` with `parse_float=Decimal`) and `_DecimalInputRoute` (`get_route_handler` wraps the request), the route class of a sub-router holding `/score` and `/score/compare`, included into `router`; `/score/batch` stays on the default route class (condition (d), the scope). `_stored_context` dumps a sampled quote's inputs with a `Decimal` as a float (a `Decimal` in pydantic's JSON mode is a string, which the re-score refuses as not numeric). `packages/pricing-core/src/pricing_core/rating/score.py`: `_engine_context` crosses a `Decimal` in an input the contract does not declare `decimal` as the float it always was (the binding refuses a `Decimal`; `_validate_inputs` tolerates extra keys). No change in `model-schema`: the schema is unchanged, so no contract moves.

An alternative read and why it was not taken: a Pydantic validator on `QuoteContext.inputs` cannot recover digits the float parse already dropped, and `model-schema` is shared with the worker's stored-context read, so the parse hook sits at the route.

#### 2026-11-13 — conditions (a) to (h): status and evidence

| cond | status | evidence |
|---|---|---|
| (a) red first | MET | red table above; I1 stays 200/41234 |
| (b) every path | MET | the path table above |
| (c) FR-239 | MET | the golden suites unchanged and green (the GREEN set below includes `test_rating_score.py`, `test_rating_score_batch.py` and the ladder files); `test_rating_score_decimal_parse_equivalence.py`: 2000 seeded texts of 1 to 15 digits, `float(Decimal(t)) == float(t)` and an equal `score_one` result on both parses; no `spec_hash` moves: the compile and hash code is untouched (`git diff --stat origin/main...HEAD -- packages` names only `rating/score.py`, whose change is after hashing) |
| (d) scoped | MET | `test_a_route_outside_the_scoring_routes_still_parses_a_json_number_as_float`; `test_the_batch_route_keeps_the_default_route_class` |
| (e) ints, bools, strings | MET | `test_ints_bools_and_strings_reach_the_engine_as_themselves`; "an input typed `float` receiving a Decimal" read as the two cases the type vocabulary has (there is no `float` input type, `RatingInputType`): an exactly representable `decimal` input (`…prices_as_before`) and a non-`decimal` input given a JSON float (`…int…50000.0…`, `…undeclared_float…`, `…nested_undeclared_float…`) |
| (f) create_app()+DB | WRITTEN, NOT RUN | `backend/tests/test_score_decimal_input_db.py` (imports clean, `ruff` clean; no database for this seat): 15 digits prices 41234, 20 digits a 422 problem naming `'factor'`, a sampled quote's stored context keeps the factor a number. The gate's DB window runs it |
| (g) contract | MET | `uv run --directory <wt> python scripts/generate-contracts.py --check`: "58 generated contracts match the models", rc 0; no model changed, no frontend regeneration owed |
| (h) spec | MET | `03` FR-273 amendment and §5.1 `/score` row dated lines; FD-1671 register row and essay: MEDIUM by the maintainer's dated line of 2026-11-13 19:53:34 GMT, the LOW's FR-244 reason kept, closed against SL 8432 |

#### 2026-11-13 — GREEN: the import closure (brief item 29)

Commands (the script is local, `scratch/exec-sl8432/closure.py`, an `ast` import graph over `backend/src` and `packages/*/src`):

- changed modules: `git diff --name-only origin/main...HEAD -- backend/src packages` filtered to `/src/` = `app.api.score`, `pricing_core.rating.score`;
- closure = those + every source module importing one + one more level of importers: 18 modules;
- GREEN = every test file importing anything in the closure: **102 files** (`closure.out`).

Run through `run-small` (non-DB only; a test whose fixture needs the database is owed to the gate's DB window):

- **Non-DB subset run, 40 files** (the closure's 33 `packages/pricing-core/tests` files and `tests/test_permission_parity.py`, plus the backend files that name no database fixture, plus this slice's http test and `test_error_sinks.py`): every test **passed** (e.g. `test_rating_score.py`, `test_rating_score_batch.py`, the ladder files, `test_rating_score_decimal_input.py`, `test_rating_score_decimal_parse_equivalence.py`, `test_quote_input_raise_sites.py`, `test_score_decimal_input_http.py`: `15 passed`), apart from the setup `ERROR`s of three files whose fixtures need the database (`RuntimeError: GIP_TEST_DATABASE_URL is not set …`): `test_deployment_route_types.py` and `test_approval_request_shape.py` (8 errors, 22 passed), `test_startup_gc_freeze.py` (2 errors, 20 passed), `test_error_sinks.py` (4 errors, 9 passed). No test FAILED.
- **Owed to the gate's DB window: the 72 backend closure files** that use the database (`classify.out`), the three above among them, with `test_score_decimal_input_db.py` (condition (f)) and `test_api_authorisation_sweep.py` as brief item 43 requires for a route-shape change (the sweep is not in the import closure; this change touches no request shape, but the sweep reads route classes, so the gate is its reading).
- **Spec-reading tests (items 39/40), 20 files by `grep -lE 'docs/specs|"docs" */ *"specs"' backend/tests tests`**: all pass except (a) setup errors (the DB message above, no test FAILED) in `test_demo_guide.py`, `test_objective_submission.py`, `test_rating_version_create_pins.py` and `test_settings_environment.py`, and (b) five failures that are all one cause, `audit-docs.py` check 31, this slice's working ids 8432 and 8433 not yet minted: `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity` (`the live allocation is not contiguous: [(2115, 8432)]`), `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`, `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`, `::test_journey_citations_are_audited_in_ci`. Item 31's class (the docs-audit set, check 31 on the slice's own working ids): the mint at its turn, then those re-run on the minted head.

#### 2026-11-13 — FIX ROUND (seat `exec-sl8432c`, brief `brief-exec-sl8432c-2026-11-13.md`), from `98ccbcb600ac`

Ids of the slice: SL 8432, LG 8433, FD 8442, OQ 8443. Both rulings, each quoted whole (the `## ` heading line is the entry's):

> ## 2026-11-13 20:31:04 GMT — Maintainer: S2 REVIEW READ (scratch/rev-sl8432/review.md 2387726fd4ba). F2 RULED: (i) — KEEP THE REFUSAL. An input whose text underflows to zero ("1e-400" → 0.0) is a silent rounding of the same class as FD-1671's, and FR-273 says refused, never rounded. My condition R2(c) is AMENDED by this line: "identical price for every input of at most 15 significant digits WHOSE MAGNITUDE THE FLOAT HOLDS EXACTLY; an input that underflows to zero, or does not round-trip, is refused with INPUT_CONTRACT_VIOLATION". This IS a behaviour change for inputs that priced before (as 0.0): it is named as such in the LG, the FR-273 dated line and the CHANGELOG entry, with the extremes tested by name (1e-400 and 1e-330 refused; 5e-324 and 1e-321 accepted; 1e400 refused as before; -0.0 and 0.0 accepted and equal in price; negative values through the same test). No spec_hash moves. F1 MEDIUM: fix as proposed — ONE shared recursive helper used by the live context and by `_stored_context`, with a test that a nested undeclared value re-scores off-path to the SAME result as the live quote (the sampled trace must reproduce the quote: that is the audit promise). F3: the property test drives the ROUTE's parse and its generator includes negatives, exponent notation and the extremes; it must go red if the refusal of 1e-400 is removed (prove it). F4, F5, F6: fix; /score/compare tested on BOTH sides. QUESTION (a) stays owed and is the one that matters: can an ALGORITHM consume an undeclared key, and so price a value of more than 15 digits as a float where a declared input would be refused? Trace it and test it; if it can, it comes to me as a finding with the options (refuse undeclared keys on the score routes; or apply FR-273's guard to every numeric key), before the second review. PLAN ACCEPTED: fresh fix seat on a brief file, a fresh review answering (a)(b)(c) by name, the gate at the NEW head; the gate now running on e2773dfb binds nothing.

> ## 2026-11-13 20:34:11 GMT — Maintainer: S2 QUESTION (a) RULED. The path is real (red test 98ccbcb600ac, 1 failed "DID NOT RAISE"; an `input` step on a key the input contract never declares prices Decimal("0.1234567890123456789") as a float). OPTION (ii): FR-273's guard applies to EVERY numeric key — `_engine_context` round-trip-checks every Decimal, nested included, before the float crossing, refusing by name. Reasons: the hole is in the guard's scope, not in which keys are allowed; one place covers /score, both sides of /score/compare, score_batch and a direct core caller; it is the same recursive helper F1 needs, so (a), F1 and F2 land in ONE helper; (i) would break the documented tolerance of extra keys and still leave score_one open. CONDITIONS: (1) the tolerance of extra keys is KEPT for every value the float holds exactly — the two existing "undeclared float is tolerated" tests stay green unchanged; (2) an over-precise or underflowing value in ANY key is refused with INPUT_CONTRACT_VIOLATION naming the key path (nested path included), value not echoed — this refuses a key no step reads, stricter than needed and stated as such in the LG, the FR-273 dated line and the CHANGELOG as a behaviour change; (3) the red test 98ccbcb6 goes green, and a nested case and a batch extra-column case are added; (4) non-numeric and integer values untouched. THE CONTRACT HOLE (an `input` step may name a key the input contract never declares; authored.py:60 says otherwise in a comment only): YES — its own register row, owner WK-2113, severity candidate MEDIUM (after (ii) no precision loss remains through it, but an algorithm can price on an input the contract does not declare, which FR-213's typed-input promise does not expect), and an OQ with the options (refuse at save and compile; or keep as documented tolerance and state it in FR-213), my recommendation recorded as REFUSE AT SAVE AND COMPILE; not fixed in S2. Proceed: amended brief FILE, fresh seat, fresh review naming (a)(b)(c), gate at the new head.

**Question (a), answered: a path exists.** `validate_algorithm` returns no issue for an `input` step on a key `input_contract` never declares (`test_save_time_validation_lets_an_input_step_name_an_undeclared_key`), the algorithm compiles, `_validate_inputs` tolerates the extra key, and `_engine_context` crossed its `Decimal` with no FR-273 guard: the red test (`98ccbcb6`, 1 failed "DID NOT RAISE", 2 passed) priced `Decimal("0.1234567890123456789")` as a float where the same text in a declared `decimal` input is refused. The maintainer ruled option (ii) (20:34:11).

**The fix, one helper (A, with F1 and F2).** `decimals_as_floats(value, path)` in `pricing_core/rating/score.py` crosses every `Decimal`, however nested, as a float and refuses one that is not finite or does not round-trip (`Decimal(repr(float(d))) == d`) with `INPUT_CONTRACT_VIOLATION` naming the key path (`extra_list[1].a`), never the value. `_engine_context` runs it over `ctx.inputs` (so `score_one`, `score_batch` and both sides of `/score/compare` share it); the backend's `_stored_context` calls the same function (the import runs backend to core, never the reverse). Floats, integers and non-numeric values pass through untouched.

**A BEHAVIOUR CHANGE, stated as the rulings require** (and in the FR-273 dated line of `03`): (1) an input whose text underflows to zero (`1e-400`, `1e-330`) priced before as `0.0` and is refused now; (2) an over-precise or underflowing value in **any** key, even a key no step reads, is refused: stricter than needed. The tolerance of an extra key is kept for every value the float holds exactly (`test_an_undeclared_float_input_is_tolerated_as_before` and `test_a_nested_undeclared_float_is_tolerated_as_before`: `git diff 98ccbcb6 HEAD` on that file removes no line and has no hunk inside either test: both are unchanged since the first round). R2(c) as amended: identical price for every input of at most 15 significant digits whose magnitude the float holds exactly; an input that underflows to zero or does not round-trip is refused. **Over-precision in an undeclared key is refused now; it was not before the fix (the red test).** No `spec_hash` moves.

**No CHANGELOG.md exists in the repository** (`git ls-files | grep -i change` finds none outside code and the generated-contract README's own changelog). The brief's CHANGELOG entry is therefore NOT written: the behaviour change is stated in this ledger, in `03` FR-273's dated line and in FD-1671's row; the lead decides whether a CHANGELOG file is to be started.

**Finding for the lead: the engine panics on a subnormal float anywhere in the context.** ZEN's core panics `ScaleExceedsMaximumPrecision(324)` on `5e-324` (and `1e-321`) read in any context key, surfacing as `RATING_EVALUATION_FAILED` (as before this slice: the guard does not change it). So "`5e-324` and `1e-321` accepted" of the 20:31:04 ruling holds at the guard (`decimals_as_floats(Decimal("5e-324"), "k") == 5e-324`); end to end through a priced route the quote is not refused by the guard but fails in the engine. The route tests assert exactly that (`code != INPUT_CONTRACT_VIOLATION`), not a price. Not fixed here; the maintainer may want an FD.

**The contract hole (C), docs only, not fixed:** FD 8442 (register row, owner WK-2113, MEDIUM candidate) and OQ 8443 (`docs/open-questions.md` and `03` §10, options "refuse at save and compile" / "keep as the documented tolerance and state it in FR-213", recommendation recorded "REFUSE AT SAVE AND COMPILE", status open).

**Red / green (this round).** Heads: red `98ccbcb6` then fix `40aa61b6`; tests and docs follow in this branch's log.

| item | test | red | green |
|---|---|---|---|
| (a) | `test_an_over_precise_value_in_an_undeclared_input_is_refused_too` | 1 failed "DID NOT RAISE" at `98ccbcb6` | passes at the fix |
| A(2) nested | `test_a_nested_over_precise_value_is_refused_naming_the_key_path` (`'extra_list[1].a'`, value not echoed) | written with the fix | passes |
| A(3) batch | `test_score_batch_refuses_an_over_precise_extra_column_row_by_name` (pl.Decimal column; the clean row still prices) | written with the fix | passes |
| A(4) | `test_integer_and_non_numeric_values_are_untouched_by_the_guard` | n/a (a pass-through) | passes |
| F2 | route: `1e-400`, `1e-330`, `-1e-400`, `1e400`, `-1e400` refused; `5e-324`, `1e-321`, `-5e-324` not refused by the guard; `0.0`/`-0.0` equal price; `-0.75` prices -37500 | with the underflow refusal removed: 3 refused-cases failed | passes |
| F3 | `test_the_route_prices_what_the_float_parse_priced_and_refuses_the_underflows` (300 generated signed / exponent texts of at most 15 digits priced against core's float parse; 40 underflow texts refused) | throwaway edit of `decimals_as_floats` so a zero float skips the round-trip check: `4 failed, 24 passed` (the three `[1e-400]`, `[1e-330]`, `[-1e-400]` cases and this property test); reverted, `git diff` empty | passes |
| F1 | `test_a_nested_undeclared_value_re_scores_off_path_to_the_live_quote` | `_stored_context` put back to its one-level body: `AssertionError: assert ['1.5', {'a': '2.5'}] == [1.5, {'a': 2.5}]`, `1 failed, 27 passed`; reverted, `git diff` empty | passes |
| F6 | `test_compare_names_the_comparison_side_when_only_it_refuses` (base call made to price a clean copy; the comparison side is the real core call) | none: the code already named the side; the test pins it | passes |
| F4 | `03` FR-273 cell: the closing `*` of the 2026-10-17 italic restored | n/a | read in the diff |
| F5 | FD-1671 row: Severity and Decision cells carry MEDIUM and "closed by SL 8432 at its merge" (the lead fills the merge sha at the PR's read-back); `register-lint.py` rc 0 | n/a | n/a |

`test_quote_input_raise_sites.py`: the one `_raise_named` site in `_engine_context` became two (`decimals_as_floats` and the non-finite float of a declared input), so `_INPUT_FREE` gained `("rating/score.py", "decimals_as_floats"): 1` with its reason; the file passes (19 passed).

**Seat runs of this round (head `ea153887357d`, no full gate, no database, no `createdb`, no mint, no PR; logs in `scratch/exec-sl8432c/`, each opening `head=`):**

| command | rc | reading |
|---|---|---|
| `ruff check .` | 0 | `All checks passed!` |
| `ruff format --check` on the three changed `.py` files that were format-clean (`backend/src/app/api/score.py`, the http test, the undeclared-input test) | 0 | `3 files already formatted` (`rating/score.py` and `test_quote_input_raise_sites.py` are not format-clean on main and are left as they are) |
| `mypy` | 0 | `Success: no issues found in 257 source files` |
| `lint-imports` | 0 | `Contracts: 4 kept, 0 broken.` |
| GREEN non-DB set, the same 40 files as the first round (`green-nodb.log`) | 11 batches rc 0, 3 rc 1 | the three rc 1 batches are `ERROR` at setup only (`GIP_TEST_DATABASE_URL` not set: `test_approval_request_shape.py`/`test_deployment_route_types.py`, `test_startup_gc_freeze.py`, `test_error_sinks.py`); no `FAILED` |
| `test_quote_input_raise_sites.py`, `test_rating_score_decimal_input.py`, `test_rating_score.py`, `test_rating_score_batch.py` (golden), the http test file | 0 | all passed (19; 80 passed with the three; http file 28 passed) |
| spec-reading set, 20 files (`specreading.log`) | see right | the only `FAILED` are the five docs-audit tests of item 31's class, one cause: `audit-docs.py` check 31 on the working ids (`the live allocation is not contiguous: [(2115, 8432), (8433, 8443)]`), plus DB-fixture setup `ERROR`s |
| `doc-index.py` / `--check` (gate-2) | 0 / 0 | regenerated after OQ-8443 |
| `register-lint.py` (gate-2) | 0 | `register.md: OK (0 violations)` |
| `req-coverage.py` (gate-2) | 0 | |
| `audit-docs.py` (gate-2) | **1** | `FAILED (2)`, both check 31: `gap in the full allocation between 2115 and 8432` and `between 8433 and 8443` (the slice's working ids); no other check fails |

## PRs

*(None: the branch is pushed, no PR is opened by the seat.)*
