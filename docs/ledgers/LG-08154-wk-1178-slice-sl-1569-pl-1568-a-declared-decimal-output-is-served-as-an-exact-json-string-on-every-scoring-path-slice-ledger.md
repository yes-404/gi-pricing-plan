---
id: LG-8154
family: ledger
title: WK-1178 slice SL-1569 — a declared decimal output is served as an exact JSON string on every scoring path (PL-1568) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-23
owner: executor
tree: fd09bc7b
phase: P2
work: WK-1178
slice: SL-1569
plans: [PL-1568]
corrected_by: []
relates: [PL-1568, SL-1569, RL-1343, RL-1567, RL-1365, FD-1333, SL-1566, SL-1367]
---

# LG-8154 — WK-1178 slice SL-1569: decimal outputs as exact JSON strings

Disclosure: drafted under working id 8154 (lead-reserved, eta 2026-10-22 11:54:44); not minted. Executor seat `exec-1569`, base `origin/main` `4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a`, branch `sl-1569-wk1178-decimal-outputs`.

**GO:** the maintainer's (by delegation) entry, heading verbatim: "## 2026-10-23 10:15:22 BST — Maintainer: SL-1569 GO (D1 = (b)); the 1(e) docs-only gate covers the lead.md amendment riding the RS docs PR; seats 7/9 noted". Body, D1: "**D1 = (b):** limb 3 of Task 6 / Acceptance 19 is checked locally as a structural merge check; limbs 1–2 run locally as DIAGNOSTIC readings only; the NFR-502 timing verdict is CARRIED to nfr-bench-1 with base = main before SL-1569 (the user starts that VM with ≥ 2 h notice). The LG records the carry with its owner (WK-1178) and base commit."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1568`, the one plan (Lean P2 L1); FR-214, FR-226, FR-250, FR-254, FR-255, FR-273, FR-451, NFR-499, NFR-502 as its §"Requirement coverage" lists. Needs 1–5 met at `4e399fd0`: `SL-1427` `b6dd96fd`, `SL-1367` `13a02bba`, `SL-1566` `cad75a7e`, `RL-1343`, `RL-1567` on main.

### Task list

| Task | Plan items | State |
|---|---|---|
| 0 | preconditions | done; line numbers below; Step 3 counts all 0 |
| 1 + 3 (together, disclosed) | 1–9, 11 | RED `4993809d`, GREEN `18a261af` |
| 2 | 10 | RED `5d5fb763`, GREEN `2eba040e` |
| 3b | 24, 25–27, 28 | RED `bb1cc5b4`, GREEN `b1935f33` (pricing-core); backend `fd09bc7b` |
| 4 | 13–15 | RED `02d4bc6d`, GREEN `4ba9d138` |
| 5 | 16–18 | tests `2f4c35f1`, reds and green in the DB window, `fd09bc7b`; docstring `ef07a2e6` |
| 6 | 19 | limb 3 run; limbs 1–2 DIAGNOSTIC OWED; timing CARRIED |
| 7 | 20 | T3 applied in `fd09bc7b`; T2 present from SL-1566 (`cad75a7e`), no T2 here |
| 8 | 21–23 | OWED: GATE READY to the lead |

### Deviations (ruled or disclosed)

1. **Tasks 1 and 3 were done together.** After Task 1's producer, SL-1566's interim batch branch (`Decimal(repr(value))`) raised on the producer's string: `AssertionError: InvalidOperation` / `assert 'InvalidOperation' is None` on four `test_a_fractional_declared_output_is_a_decimal_string_in_batch` cases and `assert 'error' == 'quoted'` on `test_score_batch_and_score_one_produce_byte_identical_ladders`, so Task 1 Step 6's "batch passes" could not hold. Commits `4993809d` (RED) and `18a261af` (GREEN, both tasks). Accepted by the lead (disclosed deviation).
2. **Item 7's null control.** At `4e399fd0` a null decimal source leaves the output name out of `outputs`; it is not served `None`. The control asserts `.get("probe_out") is None`. A plan defect, accepted by the lead.
3. **Item 24 cannot be red.** The engine returns the integer `3` for `3.0 + 0 * x` (probed), so `3.0 -> 3` is a control; the exact-equality rule is carried by the near-integer tests.
4. **Out-of-write-set touch, ruled.** `test_rating_score_batch_outputs.py::test_relativity_and_percentage_take_the_decimal_string_form_never_a_float` pinned the conversion RL-1343 rule 3.4 bans. Ruled by the maintainer's (by delegation) entry "2026-10-23 10:48:01 BST — Maintainer: (A) SL-1569 may rewrite the SL-1566 test to assert REFUSAL; (B) RL 8203 ADOPTED with one amendment; (C) SL 8185 gate-ready ac1dce42 noted; the two breaches logged", (A) YES. Red line before the edit: `ValueError: score_batch: a relativity output must be a positional decimal string, got int` (tree `18a261af`+`2eba040e`). Rewritten in `38643ee1`; `test_rating_score_batch_outputs.py`: `53 passed`.
5. **Second out-of-write-set failure, OWED a ruling:** `test_rating_ladder_exact.py::test_the_float_path_fails_the_near_tie_fee_case` plants the float path and asserts `outputs["fee_minor"] == 1234.5`; after Task 2 `ScoringResult` refuses it (`ValidationError`). The pricing-core twin of item 18; not edited.

### Gate

Not launched by the executor. OWED: GATE READY.

### Audit

Not yet.

### Build log

#### Task 0 (2026-10-23, tree `4e399fd0`)

Lines re-anchored: `score.py` `_raise_named` 308, `_exact` 635, `_build_outputs` 796 (was 729), `build_scoring_result` 897, `score_one` 946, `_KNOWN_OUTPUT_TYPES` 1020, `_coerce_output_value` 1025 (SL-1566's int/count branch present; decimal-family branch `str(Decimal(repr(value)))`), `_outputs_json` 1085, `_batch_error_code` 1102, `_score_batch_row` 1199; `ladder.py` `_ctx` 87, `round_once` 91; `model_schema/scoring.py` `outputs` 224 (was 219); `api/score.py` `_PER_QUOTE_CODES` 105, `_PER_QUOTE_STATUS` 122; `traces.py` `summarise_result` 143; `scoring.schema.json` `outputs` 60; `test_contracts.py` scoring field-names test 436; `test_rating_ladder_exact.py` pin 606; `test_score.py` float-path test 1379. No body changed: no stop.

Step 3, the stored-data check, read-only on `gipricing` under the lead's read-only grant (`docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -Atc "<select>"`, 2026-10-23T09:53Z). Algorithms declaring a `decimal`, `relativity` or `percentage` output (`select count(*) from rating_algorithms a where exists (select 1 from jsonb_array_elements(coalesce(a.content->'outputs','[]'::jsonb)) o where o->>'type' in ('decimal','relativity','percentage'))`): 0. Rating Versions on such an algorithm (the same join through `v.algorithm_ref = 'rating_algorithm:'||a.slug||'@'||a.version`): 0. Pending `scoring_traces` on such a version: 0 (pending traces in total 0; `rating_versions` in total 0).

#### Task 1 + 3 (pricing-core, via `scripts/run-small.sh`, 4 tests files, load1 below 6)

RED `4993809d`, `test_rating_decimal_outputs.py`: `15 failed, 1 passed` (causes: `assert 27 == '27.00'`, `assert 19.8 == '19.80'`, `assert 1.23456 == '1.23'`, `assert 1234567.123456789 == '1234567.1234567890123456'`, `assert -0.001 == '0.00'`, relativity and percentage the same; the null control passes). Item 11 red on that file plus the unrefusing branch: `18 failed, 16 passed` (`DID NOT RAISE ValueError` x9, `InvalidOperation: ConversionSyntax` x9). Item 9's red before its edit: `AssertionError: assert False where False = isinstance('68281', float)`. GREEN `18a261af`: `test_rating_decimal_outputs.py` + `test_rating_ladder_exact.py` + `test_rating_score_batch.py`: `71 passed`.

#### Task 2

RED `5d5fb763`, `test_scoring_outputs.py`: `4 failed, 2 passed` (`DID NOT RAISE ValidationError`). GREEN `2eba040e`: with `test_scoring_ladder.py`, `10 passed`. Consequence recorded: a `ValidationError` text names the input value (`input_value=1234.5`), so it never reaches a response body or error row (route test below; batch keeps `safe_error_detail`).

#### Task 3b (pricing-core half)

RED `bb1cc5b4`: `4 failed, 36 passed` (`ValidationError` where `RATING_TYPE_MISMATCH` is expected). GREEN `b1935f33`. Item 28's red before its edit: `AssertionError: assert 'RATING_TYPE_MISMATCH' == 'ValueError'` x4 in `test_rating_score_batch_outputs.py`; after the edit of the two expectations and the deviation-4 rewrite, `53 passed`.

#### Task 4

RED `02d4bc6d` (direct-call harness, no pytest): `planted FAIL KeyError 'OutputValue'`, `authored`, `generated`, `agree` the same, field-names control PASS. GREEN `4ba9d138`: all five PASS; `scripts/generate-contracts.py --check`: `58 generated contracts match the models`. The same three guard tests then ran under pytest in the window below.

#### Tasks 3b backend, 5, 7: the DB window (2026-10-23 10:5x–11:03 BST, `scratch/sl-1569/`)

Conditions at start, printed in each log header: `GIP_GATE_SLOT=unset`, `GIP_REDIS_URL=redis://localhost:6379/13`, own DB `gip_test_sl1569` (`createdb -T gipricing`, `alembic upgrade head` to `9b3e7c15d4a2`, rc 0), load1 3.0–4.0 (below the 5.0 hold), memory 12–14 GB available, `NUMSUB gip:switch:local:local:gate-1:prod` 0, `/tmp/slots/gate-1` held by FD 8199's gate (in pytest; no preflight or migration running), small-test flock via `run-small.sh`, three files per call.
- RED on the base source (`packages/pricing-core/src` and `packages/model-schema/src` temporarily at `origin/main`, restored afterwards; `w1-red-base.log`): `13 failed, 247 passed, 2 skipped in 126.89s` — the decimal-string tests on `/score` and `/score/compare` served numbers, the near-integer tests got 200, the new float-path test got 200; two contract tests failed on the unreverted contract.
- RED on HEAD `ef07a2e6` before the code was added (`w1-head-before-codes.log`): `5 failed, 255 passed, 2 skipped in 102.28s` — `test_a_near_integer_under_an_integral_type_is_refused_on_score` (2), `..._on_compare` (2) answered 500 `INTERNAL_ERROR` (the item 25 second red), and the old `test_the_float_path_fails_the_route_level_fee_assert` failed (item 18's old expectation).
- GREEN (`w1-green-a.log`, tree `ef07a2e6` plus the working diff of `fd09bc7b`): `test_score.py`, `test_score_compare.py`, `test_contracts.py`: `259 passed, 2 skipped, 5 warnings in 141.25s`. The 2 skipped are also in the base run.
- Cleanup: `redis-cli -n 13 flushdb` then `dbsize` = 0; `dropdb gip_test_sl1569` rc 0; `select count(*) from pg_database where datname = 'gip_test_sl1569'` = 0. Redis db 0 untouched.

T3 applied byte for byte from `RL-1567`: `grep -cF` of its new text 1, of its find string 0. T2: present in FR-214 from SL-1566 (`cad75a7e`); this slice applies no T2.

Import closure (item 29): `git diff --name-only origin/main...HEAD -- packages/pricing-core/src packages/model-schema/src backend/src` lists 5 modules; closure plus two importer levels is 126 of 202 source modules and 293 of 333 test files (`model_schema/__init__` re-exports `scoring`). That is effectively the whole suite, so the full gate is the decisive green; the list is `scratch/sl-1569/closure-tests.txt`.

#### Task 6

Limb 3, structural, the merge check (script `limb3.py`, sha256 prefix `6fa80c30e43bf1c4`, the SL-1367 script unchanged; HEAD `38643ee1`, tree `ddc26d37`, load1 2.59): `/api/v1/score response_model= None response_field= None 200= {'$ref': '#/components/schemas/ScoringResult'}` and `/api/v1/score/compare response_model= None response_field= None 200= {'$ref': '#/components/schemas/ScoreComparison'}`. Limbs 1–2: DIAGNOSTIC, OWED (see Gate). **The NFR-502 timing verdict is CARRIED to nfr-bench-1, base = main before SL-1569 (`4e399fd0`), owner WK-1178** (D1 = (b)).

#### Release note (Task 7 Step 3)

A declared `decimal`, `relativity` or `percentage` output changes on `POST /api/v1/score` and on both results of `POST /api/v1/score/compare` from a JSON number (an integer when whole, a float otherwise) to a JSON string with exactly the output step's declared `dp` digits; the declared rounding is now applied on every path, batch included; an output value that is a non-integer number is refused at construction (a 500 on `/score`, an error row in batch). A declared `int` or `count` output is a JSON integer on `/score` and `/score/compare`, and a value that is not integral by exact equality refuses the quote with 422 `RATING_TYPE_MISMATCH`, now a per-quote code; in batch the same fault is an error row coded `RATING_TYPE_MISMATCH`. Stored data: no Rating Version or pending trace is affected (Task 0 Step 3: all zero).

## PRs

(none opened by the executor)
