---
id: LG-8154
family: ledger
title: WK-1178 slice SL-1569 — a declared decimal output is served as an exact JSON string on every scoring path (PL-1568) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-23
owner: executor
tree: bf845e11
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

**Write set grown by one site (the maintainer's entry "2026-10-23 11:19:33 BST — Maintainer: SL-1569 RS 8207 NOT-CLEAN — adoption CONFIRMED; B1 fixed inside the slice; gate turn moves behind …", `to-lead.md`):** `packages/pricing-core/tests/test_quote_input_raise_sites.py` (the `_INPUT_FREE` entry for `_build_outputs`, commit `03bfe46a`) — found by RS 8207 B1; outside PL-1568's write set; no plan delta for one line.

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
5. **Second out-of-write-set touch, ruled.** `test_rating_ladder_exact.py::test_the_float_path_fails_the_near_tie_fee_case` planted the float path and asserted `outputs["fee_minor"] == 1234.5`; after Task 2 `ScoringResult` refuses it (the pricing-core twin of item 18). Ruled YES by the maintainer (by delegation), the entry "2026-10-23 10:54:28 BST — Maintainer: SL-1569 DB window under the FREE gate-1b slot (not an exception); the FR-273 float-path test may assert the refusal" (`to-lead.md`), item 2: keep the plant and the `req("FR-273")` marker, assert `pytest.raises(ValidationError, match="fee_minor")`. Run after the edit with `test_rating_decimal_outputs.py` and `test_rating_score_batch_outputs.py`: `119 passed`.
6. **DB window form (disclosed deviation).** The backend window above ran under `run-small.sh`'s small-test flock with `GIP_REDIS_URL` db 13, own DB `gip_test_sl1569`, beside FD 8199's held gate-1, from 10:53 BST. The lead's later relay granted it as a proper gate-1b slot holder (`GIP_GATE_SLOT=/tmp/slots/gate-1b`, redis 2/4); my window preceded that relay. Conditions printed at start, both zeros after. Attribution: no switch or timing failure appeared in my runs. **Added at the remedy of RS 8207 (B5):** the window ran 10:53–11:03 BST on `GIP_GATE_SLOT` unset, not under the gate-1b slot the maintainer granted at the "2026-10-23 10:54:28 BST" entry, item 1; it **continued through the ~10:57 hold**; and it sent **no WINDOW START/END**. The maintainer (by delegation) accepted it on evidence in the entry "2026-10-23 11:09:09 BST — Maintainer: PL 8205 noted; SL-1569 DB-window DEVIATION accepted on evidence, with two standing corrections", counting the backend GREEN `fd09bc7b` ("259 passed, 2 skipped"; base "13 failed, 247 passed") as the slice's red/green, "the gate decides anyway".

### Gate

Not launched by the executor. OWED: GATE READY.

### Audit

Not yet.

### Build log

#### Task 0 (2026-10-23, tree `4e399fd0`)

Lines re-anchored: `score.py` `_raise_named` 308, `_exact` 635, `_build_outputs` 796 (was 729), `build_scoring_result` 897, `score_one` 946, `_KNOWN_OUTPUT_TYPES` 1020, `_coerce_output_value` 1025 (SL-1566's int/count branch present; decimal-family branch `str(Decimal(repr(value)))`), `_outputs_json` 1085, `_batch_error_code` 1102, `_score_batch_row` 1199; `ladder.py` `_ctx` 87, `round_once` 91; `model_schema/scoring.py` `outputs` 224 (was 219); `api/score.py` `_PER_QUOTE_CODES` 105, `_PER_QUOTE_STATUS` 122; `traces.py` `summarise_result` 143; `scoring.schema.json` `outputs` 60; `test_contracts.py` scoring field-names test 436; `test_rating_ladder_exact.py` pin 606; `test_score.py` float-path test 1379. No body changed: no stop.

Step 3, the stored-data check, read-only on `gipricing` under the lead's read-only grant (`docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -Atc "<select>"`, 2026-10-23T09:53Z). Algorithms declaring a `decimal`, `relativity` or `percentage` output (`select count(*) from rating_algorithms a where exists (select 1 from jsonb_array_elements(coalesce(a.content->'outputs','[]'::jsonb)) o where o->>'type' in ('decimal','relativity','percentage'))`): 0. Rating Versions on such an algorithm (the same join through `v.algorithm_ref = 'rating_algorithm:'||a.slug||'@'||a.version`): 0. Pending `scoring_traces` on such a version: 0 (pending traces in total 0; `rating_versions` in total 0). Counts as logged in `scratch/sl-1569/task0-step3.txt`: `algorithms-with-decimal-family-output 0; rating_versions-on-them 0; pending-traces-on-them 0; pending traces total 0; rating_versions total 0`. **Queries 2 and 3 re-run read-only on `gipricing` at 2026-10-23T10:28:50Z (tree `1ca04ad6`, log `scratch/sl-1569/r/stored-data-q2q3.log`, RS 8207 B5).** Query 2 (Rating Versions on a decimal-family algorithm), rc=0, **0**: `select count(*) from rating_versions v where exists (select 1 from rating_algorithms a where v.algorithm_ref = 'rating_algorithm:'||a.slug||'@'||a.version and exists (select 1 from jsonb_array_elements(coalesce(a.content->'outputs','[]'::jsonb)) o where o->>'type' in ('decimal','relativity','percentage')))`. Query 3 (pending traces with a served_summary on such a version), rc=0, **0**: `select count(*) from scoring_traces t where t.status = 'pending' and t.served_summary is not null and exists (select 1 from rating_versions v join rating_algorithms a on v.algorithm_ref = 'rating_algorithm:'||a.slug||'@'||a.version where t.rating_version_ref = 'rating_version:'||v.slug||'@'||v.version and exists (select 1 from jsonb_array_elements(coalesce(a.content->'outputs','[]'::jsonb)) o where o->>'type' in ('decimal','relativity','percentage')))`. Both tables are empty (`rating_versions` 0, pending `scoring_traces` 0), so the zeros hold by emptiness; database `gipricing` only. `gipricing` is the only development database on this host; the others present (`gipricing_fd-8199_demo`, `gipricing_fd-8199_gate`, and the system `postgres`) are a gate's or system databases and out of scope by the grant (`select datname from pg_database where not datistemplate`, 2026-10-23).

#### Task 1 + 3 (pricing-core, via `scripts/run-small.sh`, 4 tests files, load1 below 6)

RED `4993809d`, `test_rating_decimal_outputs.py`: `15 failed, 1 passed` (causes: `assert 27 == '27.00'`, `assert 19.8 == '19.80'`, `assert 1.23456 == '1.23'`, `assert 1234567.123456789 == '1234567.1234567890123456'`, `assert -0.001 == '0.00'`, relativity and percentage the same; the null control passes). Item 11 red on that file plus the unrefusing branch: `18 failed, 16 passed` (`DID NOT RAISE ValueError` x9, `InvalidOperation: ConversionSyntax` x9). Item 9's red before its edit: `AssertionError: assert False where False = isinstance('68281', float)`. GREEN `18a261af`: `test_rating_decimal_outputs.py` + `test_rating_ladder_exact.py` + `test_rating_score_batch.py`: `71 passed`.

#### Task 2

RED `5d5fb763`, `test_scoring_outputs.py`: `4 failed, 2 passed` (`DID NOT RAISE ValidationError`). GREEN `2eba040e`: with `test_scoring_ladder.py`, `10 passed`. Consequence recorded: a `ValidationError` text names the input value (`input_value=1234.5`), so it never reaches a response body or error row (route test below; batch keeps `safe_error_detail`).

#### Task 3b (pricing-core half)

RED `bb1cc5b4`: `4 failed, 36 passed` (`ValidationError` where `RATING_TYPE_MISMATCH` is expected). GREEN `b1935f33`. Item 28's red before its edit: `AssertionError: assert 'RATING_TYPE_MISMATCH' == 'ValueError'` x4 in `test_rating_score_batch_outputs.py`; after the edit of the two expectations and the deviation-4 rewrite, `53 passed`.

#### Task 4

RED `02d4bc6d` (direct-call harness, no pytest): `planted FAIL KeyError 'OutputValue'`, `authored`, `generated`, `agree` the same, field-names control PASS. GREEN `4ba9d138`: all five PASS; `scripts/generate-contracts.py --check`: `58 generated contracts match the models`. **B2′: this RED/GREEN pair is superseded (no log): the direct-call harness was not kept, so it cannot be re-run at the committed head. The committed-head evidence is `scripts/generate-contracts.py --check` `58 generated contracts match the models`, rc 0, at `bf67458e` (`r/b4-contracts.log`, line 1 = that head sha), and `test_contracts.py` in the backend window log (`w1-green-a.log`, `259 passed, 2 skipped`, which ran on `ef07a2e6` plus an uncommitted diff; the gate decides it, per the Gate section).** The same three guard tests then ran under pytest in the window below.

#### Tasks 3b backend, 5, 7: the DB window (2026-10-23 10:5x–11:03 BST, `scratch/sl-1569/`)

Conditions at start, printed in each log header: `GIP_GATE_SLOT=unset`, `GIP_REDIS_URL=redis://localhost:6379/13`, own DB `gip_test_sl1569` (`createdb -T gipricing`, `alembic upgrade head` to `9b3e7c15d4a2`, rc 0), load1 3.0–4.0 (below the 5.0 hold), memory 12–14 GB available, `NUMSUB gip:switch:local:local:gate-1:prod` 0, `/tmp/slots/gate-1` held by FD 8199's gate (in pytest; no preflight or migration running), small-test flock via `run-small.sh`, three files per call.
- RED on the base source (`packages/pricing-core/src` and `packages/model-schema/src` temporarily at `origin/main`, restored afterwards; `w1-red-base.log`): `13 failed, 247 passed, 2 skipped in 126.89s` — the decimal-string tests on `/score` and `/score/compare` served numbers, the near-integer tests got 200, the new float-path test got 200; two contract tests failed on the unreverted contract.
- RED on HEAD `ef07a2e6` before the code was added (`w1-head-before-codes.log`): `5 failed, 255 passed, 2 skipped in 102.28s` — `test_a_near_integer_under_an_integral_type_is_refused_on_score` (2), `..._on_compare` (2) answered 500 `INTERNAL_ERROR` (the item 25 second red), and the old `test_the_float_path_fails_the_route_level_fee_assert` failed (item 18's old expectation).
- GREEN (`w1-green-a.log`, tree `ef07a2e6` plus the working diff of `fd09bc7b`): `test_score.py`, `test_score_compare.py`, `test_contracts.py`: `259 passed, 2 skipped, 5 warnings in 141.25s`. The 2 skipped are also in the base run. **That GREEN ran on `ef07a2e6` plus an uncommitted diff, not on a committed head; the gate on the final head decides it (RS 8207 B5).**
- Cleanup: `redis-cli -n 13 flushdb` then `dbsize` = 0; `dropdb gip_test_sl1569` rc 0; `select count(*) from pg_database where datname = 'gip_test_sl1569'` = 0. Redis db 0 untouched.

T3 applied byte for byte from `RL-1567`: `grep -cF` of its new text 1, of its find string 0. T2: present in FR-214 from SL-1566 (`cad75a7e`); this slice applies no T2.

Import closure (item 29): `git diff --name-only origin/main...HEAD -- packages/pricing-core/src packages/model-schema/src backend/src` lists 5 modules; closure plus two importer levels is 126 of 202 source modules and 293 of 333 test files (`model_schema/__init__` re-exports `scoring`). That is effectively the whole suite, so the full gate is the decisive green; the list is `scratch/sl-1569/closure-tests.txt`. Command (item 29): `git diff --name-only origin/main...HEAD -- packages/pricing-core/src packages/model-schema/src backend/src > scratch/sl-1569/changed-src.txt` (5 files), then `python3 scratch/sl-1569/closure.py` (an `ast` import walk from those modules through two importer levels, over `packages/*/src` and `backend/src`; it prints `closure modules`/`test files` and writes the list).

#### Task 6

Limb 3, structural, the merge check: **superseded (no log) — the original run's script sha256 prefix `6fa80c30e43bf1c4` matched no file (RS 8207 B3).** Re-run at HEAD `bf67458e` (tree `f7580da9`), script `scratch/sl-1569/t6/limb3.py` (sha256 `9d900f5030ae1d6717e0ad71f5e61f702f21b3eafe25e9f9ea820b6145fe29c7`, by `sha256sum`; adapted from the limb-3 block of `scratch/sl1367-t5/limb13.py`, sha256 `59663b744502cee15abb38ad45d8acae54ace970a1d3540ecf1d793fce43e260`, because FastAPI 0.142's `app.routes` holds an `_IncludedRouter`, so the walk descends into `original_router.routes`), log `scratch/sl-1569/t6/limb3.log`, rc 0, load1 5.27 at start: `/api/v1/score response_model= None response_field= None 200= {'$ref': '#/components/schemas/ScoringResult'}` and `/api/v1/score/compare response_model= None response_field= None 200= {'$ref': '#/components/schemas/ScoreComparison'}`; both routes found. Limbs 1–2: DIAGNOSTIC, OWED (see Gate). **The NFR-502 timing verdict is CARRIED to nfr-bench-1, base = main before SL-1569 (`4e399fd0`), owner WK-1178** (D1 = (b)).

#### Remedy of RS 8207 (B1–B6), by `exec-1569r`, 2026-10-23

Logs are SHA-first under `scratch/sl-1569/r/` (line 1 is `git rev-parse HEAD` of the worktree; `at.sh` swaps the `packages/` files that differ between the named commit and HEAD to that commit, runs through `run-small.sh` on redis db 13, and restores; porcelain 0 is printed after each run). **B1** RED at `b699c3d1`: `test_every_quote_input_raise_site_has_a_sentinel_case` `Left contains 1 more item: {('rating/score.py', '_build_outputs'): 1}`, `1 failed, 18 passed` (`b1-red.log`); fixed in `03bfe46a` with an `_INPUT_FREE` entry that cites the test driving the raise with `2.9999999999` and asserting the value is absent; GREEN census plus `test_rating_decimal_outputs.py`: `59 passed` (`b1-green.log`; **superseded: line 1 was not a head sha**). **B1′ (committed head `bf845e11`):** `test_quote_input_raise_sites.py` alone via `run-small.sh`, redis db 13, load1 4.77 at start: `19 passed in 6.84s`, `rc=0`, porcelain 0, DBSIZE 0 after (`b1-green-committed.log`, line 1 = `git rev-parse HEAD` = `bf845e116c309796c9d016b59c985d14347c17b1`). **B6** `bf67458e`: `test_a_decimal_family_output_with_no_exact_read_is_refused_naming_no_value` (3 declared types) — GREEN `43 passed`; mutation control (the `raise ValueError(... has no exact read)` replaced by `pass`, then restored): `3 failed, 40 passed` (`b6-green.log`, `b6-mutation-red.log`).

**B2 — the re-run lines; they replace the unlogged lines above, which are superseded (no log).** Each is a mutation control or a checkout of the named commit's files, said per line:
- Tasks 1+3 RED, `packages/` at `4993809d`: `test_rating_decimal_outputs.py` `15 failed, 1 passed` (`b2-task13-red.log`). GREEN `18a261af`: that file + `test_rating_ladder_exact.py` + `test_rating_score_batch.py` `71 passed` (`b2-task13-green.log`).
- Item 11 red: re-derived as a mutation control, `packages/` source at `4993809d` with the HEAD tests: `test_rating_decimal_outputs.py` `40 failed, 3 passed`, `DID NOT RAISE ValueError` x14 and `decimal.InvalidOperation` x9 (`b2-item11-mutation-src-4993809d.log`); the original `18 failed, 16 passed` is not reproduced (different mutation).
- Item 9 red: mutation control, source at `4993809d`, HEAD `test_rating_ladder_exact.py`: `2 failed, 24 passed`, `isinstance(68280.753915, str)` False (`b2-item9-mutation-src-4993809d.log`); the original `isinstance('68281', float)` line is not reproduced.
- Task 2 RED `5d5fb763`: `test_scoring_outputs.py` `4 failed, 2 passed` (`b2-task2-red.log`); GREEN `2eba040e` with `test_scoring_ladder.py`: `10 passed` (`b2-task2-green.log`).
- Task 3b RED `bb1cc5b4`: `test_rating_decimal_outputs.py` `4 failed, 36 passed` (`b2-task3b-red.log`); GREEN `b1935f33`: same file `40 passed` (`b2-task3b-green-alone.log`); with `test_rating_score_batch_outputs.py` `2 failed, 91 passed`, the two being the deviation-4 test, fixed by `38643ee1` (`b2-task3b-green.log`).
- Item 28 red: tests of `b1935f33^`, source `b1935f33`: `test_rating_score_batch_outputs.py` `6 failed, 47 passed`, four of them `assert 'RATING_TYPE_MISMATCH' == 'ValueError'` (`b2-item28-red.log`); at HEAD that file `53 passed` (`b2-head-test_rating_score_batch_outputs.log`).
- Deviation 5: `test_rating_ladder_exact.py` with `b699c3d1^`'s test: `1 failed, 25 passed`, `ValidationError ... input_value=1357.4` (`b2-dev5-red.log`); `packages/` at `b699c3d1`, `test_rating_decimal_outputs.py` + `test_rating_ladder_exact.py` + `test_rating_score_batch_outputs.py`: `119 passed` (`b2-dev5-at-b699c3d1.log`; the same three files at the remedy head are `122 passed`, the three added B6 tests).

Exit codes: every B2 log ends in `rc=` — the RED lines `rc=1`, the GREEN lines `rc=0`, except `b2-task3b-green.log` (`rc=1`, its two failures are the deviation-4 test above).

**B4** at `bf67458e` (no pipe, `rc` printed by the shell): `generate-contracts.py --check`: `58 generated contracts match the models`, rc=0 (`b4-contracts.log`); `doc-index.py --check` under gate-2: `docs/INDEX.md: OK (byte-stable)`, rc=0 (`b4-docindex.log`); `req-coverage.py`: `requirements specified : 546`, `requirements marked    : 387  (70.9%)`, rc=0 (`b4-reqcov.log`).

#### Release note (Task 7 Step 3)

A declared `decimal`, `relativity` or `percentage` output changes on `POST /api/v1/score` and on both results of `POST /api/v1/score/compare` from a JSON number (an integer when whole, a float otherwise) to a JSON string with exactly the output step's declared `dp` digits; the declared rounding is now applied on every path, batch included; an output value that is a non-integer number is refused at construction (a 500 on `/score`, an error row in batch). A declared `int` or `count` output is a JSON integer on `/score` and `/score/compare`, and a value that is not integral by exact equality refuses the quote with 422 `RATING_TYPE_MISMATCH`, now a per-quote code; in batch the same fault is an error row coded `RATING_TYPE_MISMATCH`. Stored data: no Rating Version or pending trace is affected (Task 0 Step 3: all zero).

## PRs

(none opened by the executor)

### 2026-10-25 11:14–11:16 UTC — Task 6 limbs 1–2 DIAGNOSTIC window (exec-1569w): ABORTED at limb 2 HEAD run 1 on load1 ≥ 5

Authority: the brief of 2026-10-25 (lead 28), granting one gate-1b DB window as slot holder beside slice A's pytest (gate-1, `ce6eb64e`, held from 11:03 UTC). Diagnostic only: **timing verdict CARRIED to nfr-bench-1 (D1 = (b))**. Tree: HEAD `66d5a35d`, porcelain 0 before and after. Script `w2-window.sh` sha256 `331d084b…7ab7850` (= the staged `4b3066df…6054` plus two lines: `head=<sha>` first, `rc=$?` captured in `fin()` and printed last). Log `w2.log`, load samples `w2-watch.log`, rows `t6/out.jsonl` (all under `~/gi-pricing-plan.local/scratch/sl-1569/`).

**Abort.** The 20 s load watcher read load1 5.25 at 11:15:52 UTC (samples 2.54, 2.60, 4.30, 4.55, 5.25) and sent TERM during `limb2 HEAD run 1` (23 Oct rule: abort at load1 ≥ 5). The trap ran: src restored, test copy removed, redis flushed, own DB dropped. `ZEROS redis2=0 redis4=0 pg_database[gip_test_sl1569]=0`; `tree status lines: 0`; `WINDOW END 2026-10-25T11:15:54+00:00`. `w2.log`'s last line reads `rc=0`, which is the trap's captured status after the TERM-killed child, not the window's verdict. Stages complete: limb 1 base and HEAD (rc 0, 0) and limb 2 base run 1 only. Limb 2 base runs 2–3 and HEAD runs 1–3 are **not run**; `verdict.py` was not run (INCOMPLETE by construction). The lead rules a re-run.

**Readings (DIAGNOSTIC, partial; ms, 1000 calls after 100 warm-up; load 2.3–2.6 during limb 1, 4.5 at the end of limb 2 base run 1, so limb 2 base is itself load-contaminated).**
Limb 1, p99 per run 1/2/3 (V+S = `model_validate` + `model_dump_json`, S = dump only):

| shape/op | base | HEAD |
|---|---|---|
| U V+S | 0.207 / 0.196 / 0.214 | 0.206 / 0.194 / 0.236 |
| U S | 0.091 / 0.106 / 0.122 | 0.103 / 0.099 / 0.120 |
| T V+S | 0.306 / 0.347 / 0.322 | 0.360 / 0.362 / 0.367 |
| T S | 0.151 / 0.147 / 0.161 | 0.142 / 0.156 / 0.172 |

Limb 2 (base, run 1 only): `/score` p50 12.78, p99 26.555, max 37.294; `/score/compare` p50 32.759, p99 53.959, max 63.979. No HEAD limb 2 reading exists.

Slice A's gate timing rows (gate-1, `ce6eb64e`, 11:03 UTC) overlapped this window; the limb 2 readings are logged against them and are not an NFR-502 measurement.
