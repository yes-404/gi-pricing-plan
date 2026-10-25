---
id: RS-1897
family: research
kind: audit
title: SL-1569 (WK-1178, PL-1568) slice audit at b699c3d1 — a declared decimal output is served as an exact JSON string on every scoring path
status: draft
created: 2026-10-25   # drafted 2026-10-23 under working id 8207; minted 2026-10-25 as RS-1897
owner: auditor
tree: 40aa993134a9c2c88e474d925ea6fc844f638e68
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1569, PL-1568, LG-1896, RL-1343, RL-1567, RL-1365]
---

# RS-1897 — SL-1569 slice audit (PL-1568) at `b699c3d1`

*(Working id 8207, written by `aud-1569`, 2026-10-23, from `brief-aud-1569-2026-10-23.md` (lead 27). Check 31 on this id is expected until the mint. The ledger is cited as `LG-1896`, its working id. The audit read the object by `git show` / `git diff` only; no test, no DB, no gate was run. `aud-1569` proposes; the verdict is the lead's.)*

## Question

Does branch `sl-1569-wk1178-decimal-outputs` at `b699c3d18c8142adea37dc6d7fdec5228043cd0f`, range `origin/main...b699c3d1` (base `origin/main` = `4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a`, tree `40aa9931`), deliver `PL-1568`'s Acceptance Standard (items 1–28, Tasks 0–8, Global Constraints, write set) as amended by the maintainer's (by delegation) entries "2026-10-23 10:15:22 BST" (GO, D1 = (b)), "2026-10-23 10:48:01 BST" item (A) and "2026-10-23 10:54:28 BST" item 2 (the FR-273 float-path test), and does its ledger `LG-1896` evidence match its logs?

## Method

Scope came from `docs/plans/PL-01568-…` (Acceptance Standard `:250-438`, Global Constraints `:440-465`, Write set `:552-575`, §"Spec text owed", Task 3b items 24–28) and the three channel entries (read by heading in `to-lead.md`) **before** the ledger or the diff. Then evidence, each by command at the named object:

- Diff: `git diff origin/main...origin/sl-1569-wk1178-decimal-outputs` (21 files, +864/−69).
- Ledger: `git show origin/sl-1569-wk1178-decimal-outputs:docs/ledgers/LG-01896-…`.
- Reachability: `git merge-base --is-ancestor <sha> origin/sl-1569-wk1178-decimal-outputs` for the 12 ledger SHAs and the 3 need SHAs (`cad75a7e`, `13a02bba`, `b6dd96fd`): **all 15 exit 0**.
- Logs: `~/gi-pricing-plan.local/scratch/sl-1569/` (listed below).
- Spec: the T3 block of `RL-1567` extracted with a Python regex over its ```` ```text ```` fences (blocks 4 and 5), applied with `str.replace(find, new, 1)` to `origin/main:docs/specs/03-rating-engine.md`; compared with the branch's file.
- Raise-site census: an AST count (`_raise_named`, `CodedError`, `_model_call_failure`, `PlatformError` calls per enclosing function) of `rating/score.py` at `origin/main` and at the branch, the same predicate as `test_quote_input_raise_sites.py::_raise_sites` (`:142-158`). A script in the job tmp, not a test run.

## Findings

### 1. Scope — acceptance items 1–28 and tasks

| Item | Verdict | Evidence (file:line at `b699c3d1`) |
|---|---|---|
| 1, 2 | delivered, tested; red/green log **missing** (B2) | `test_rating_decimal_outputs.py:71-83`; producer `score.py:855` `outputs[declared.name] = round_to_text(exact, rounding)`; fixture is `_chain_algorithm` with `risk_premium_minor` = 18, not the plan's `_algorithm_payload`/`driver_age` (stated in the test docstring `:5-7`, not in the LG's deviations; harmless) |
| 3 | delivered, tested | `:86-97` three parametrised cases, 1.23 / 1.22 / 1.23 |
| 4 | delivered, tested | `:100-103` dp 16 `"1234567.1234567890123456"` (the engine read was exact; the plan's stop did not fire) |
| 5 | delivered, tested | `:106-123` five cases incl. `-0.001`→`"0.00"` and dp 0 `"27"` |
| 6 | delivered, tested | `:126-137` |
| 7 | **deviated and disclosed** (LG deviation 2; accepted 10:48:01) | `:140-146` asserts `.get("probe_out") is None`; at `4e399fd0` a null source omits the name, so the control cannot detect a `None` served; weak by construction, disclosed |
| 8 | delivered | `test_rating_score_batch.py:194-201` (assertion added); `test_rating_score_batch_outputs.py` PL-1565 item 7 flipped to `"27.00"`/`"19.80"` plus a `score_one` equality |
| 9 | delivered | `test_rating_ladder_exact.py:621-625` renamed, asserts `"68281"` str; red `isinstance('68281', float)` is in the LG only (B2) |
| 10 | delivered, tested | `test_scoring_outputs.py` four float cases (adds `3.0`) + control + the `{"r": 27}` blind-spot test |
| 11 | delivered, tested | `:149-170`, 15 refusals + control |
| 12 | superseded by 24–27 (pre-mint delta 1) | — |
| 13 | delivered | `scoring.schema.json` `OutputValue` + `outputs` `$ref`; generated `score-comparison.schema.json` the same shape; no `number` at any depth |
| 14 | delivered | `test_contracts.py` `_number_paths`, planted-copy test names `/anyOf/<n>`, agreement test; the red in the LG is a "direct-call harness, no pytest" (`02d4bc6d`), later the same functions run in the window (259 passed) |
| 15 | delivered, **rc not captured** (B4) | `contracts.log`: `58 generated contracts match the models` |
| 16 | delivered, tested | `test_score.py` `test_a_decimal_output_is_a_json_string_on_score` (4 cases) incl. `traces.summarise_result` equality |
| 17 | delivered, tested | `test_score_compare.py` `test_both_results_of_a_comparison_carry_the_decimal_string` |
| 18 | delivered, tested | `test_score.py:1378-1399` keeps the plant and `req("FR-273")` (adds `NFR-499`); asserts 500, `code == "INTERNAL_ERROR"`, `not in _PER_QUOTE_CODES`, `"1234" not in response.text` |
| 19 | **partly owed** | limb 3 claimed run, **no log** (B3); limbs 1–2 DIAGNOSTIC not run (no `w2.log` exists); timing verdict carried (D1 = (b)). See Owed |
| 20 | delivered | see §7 |
| 21 | **owed** (gate not launched) | LG §Gate "Not launched by the executor. OWED: GATE READY." |
| 22 | delivered by construction; `test_one_invalid_row_does_not_stop_the_batch` is not in the diff; run result `53 passed` has **no log** (B2) | |
| 23 | **one path outside the write set is needed and absent** (B1) | see §3 |
| 24 | deviated and disclosed (control, not red; LG deviation 3; noted 10:54:28 item 2) | `test_rating_decimal_outputs.py:174-186`; the `/score` body check is in the engine-level test only, via `model_dump_json()` |
| 25 | delivered, tested | `test_score.py` near-integer 422 `RATING_TYPE_MISMATCH`; asserts the literal is absent; **does not assert "any quote input value" absent** (plan item 25 text); both reds logged (`w1-red-base.log` `assert 200 == 422`; `w1-head-before-codes.log` 500) |
| 26 | delivered, tested | `test_score_compare.py` `…_refused_on_compare[int, count]`, same weaker body assert |
| 27 | delivered, tested | `test_rating_decimal_outputs.py:203-218` |
| 28 | delivered | `test_rating_score_batch_outputs.py` two `error_code` expectations → `RATING_TYPE_MISMATCH`; red `'RATING_TYPE_MISMATCH' == 'ValueError'` x4 in the LG only (B2) |

Tasks 0–8: 0 delivered (line anchors and stored-data counts in the LG); 1+3 together (deviation 1, accepted 10:48:01); 2, 3b, 4, 5, 7 delivered; 6 partly owed; 8 owed.

**Global Constraint with no test (delivered but untested, B6):** "A `decimal`-family output whose exact read is missing while `result[name]` is not `None` raises `ValueError`" is written at `score.py:861-863`; `git grep -n "has no exact read" origin/sl-1569-wk1178-decimal-outputs -- packages backend` finds only the source line. Its effect is partly covered by item 18's plant (via `ScoringResult`), but that plant monkeypatches `_exact` for a `money_minor` output (`fee_minor`), not a decimal-family one, so the new branch is not exercised.

### 2. Money and maths invariants (read at the source, not run)

- **Exact positional string, one producer.** `_build_outputs` (`score.py:808-866`) reads `_exact(result, name)` for `_DECIMAL_FAMILY` (`:799`) and writes `round_to_text(exact, rounding)` (`:855`); `/score`, `/score/compare` (same `score_one`) and batch (`_coerce_output_value` `:1099-1108` checks, returns unchanged) share it. No `result[name]` float is read for the family: `:859-866` raises `ValueError` when there is no exact read and the value is not `None`.
- **`round_to_text`** (`ladder.py:102-112`): `quantize(Decimal(1).scaleb(-dp), rounding=ROUNDING_MODES[mode])` inside `_ctx()` (100 digits), then `copy_abs()` on a zero, `format(…, "f")`. Mode is the output step's declared mode, applied once; dp 0 gives no point; a rounded zero carries no sign (`-0.001`, dp 2 → `"0.00"`). The **ladder pin**: `round_once` (`ladder.py:91`) is untouched; `round_to_text` reuses `_ctx()` and `ROUNDING_MODES`, and the `test_rating_ladder_exact.py` ladder pins are not in the diff except the ruled `:594-625` region. Rounding mode: `ROUNDING_MODES` is the module's one table (`pricing_core.money`), the same as `round_once`; no new mode table.
- **No float survives `ScoringResult` construction.** `scoring.py:217-220` `OutputValue = StrictInt | StrictStr | StrictBool | dict[str, OutputValue] | list[OutputValue] | None`; `:246` `outputs: dict[str, OutputValue]`. `StrictInt` refuses `float` including `3.0`, `Decimal`, and a `bool` is taken by `StrictBool` only. Tests: `test_scoring_outputs.py` (float, whole float, in map, in list refused; `{"i":27,"s":"27.00","b":True,…}` accepted).
- **`int`/`count` served as integer.** `score.py:841-852`: `exact != exact.to_integral_value()` (exact equality, no tolerance) else `int(exact)`; `type(...) is int` asserted at `test_rating_decimal_outputs.py:185`.
- **Near-integer → `RATING_TYPE_MISMATCH`.** `_raise_named("RATING_TYPE_MISMATCH", …)` at `score.py:848-852`, text names the output and type, never the value (`test_rating_decimal_outputs.py:200`); `api/score.py:111` adds the code to `_PER_QUOTE_CODES`; `/score` and `/score/compare` 422 reds/greens in `w1-*.log`; batch `error_code` `RATING_TYPE_MISMATCH` (`:203-218`).
- **Batch regex** `_POSITIONAL_DECIMAL` (`score.py:805`) = the contract's `Decimal` minus a signed zero; refuses `"1E-7"` and `"-0.00"` (item 11).
- **Observation (no finding):** an `int`/`count` output whose `_exact` read is `None` but whose `result[name]` is a non-null float falls to `outputs[declared.name] = result[name]` (`:864-866`, no integral guard there), so `ScoringResult` would refuse it as an internal error, not a 422. The decimal family has the explicit `ValueError` guard; the integral types rely on construction. This is the engine-invariant breach path, consistent with item 18; named so the lead can say whether the asymmetry is intended.

### 3. Write set (plan `:552-575`) against `git diff --name-only origin/main...b699c3d1`

In the write set: `score.py`, `ladder.py`, `scoring.py`, `scoring.schema.json`, `generated/*` + `openapi/generated.json`, `test_contracts.py`, `traces.py` (docstring only, confirmed: the diff touches comment lines only), the two new test files, `test_rating_score_batch.py`, `test_rating_score_batch_outputs.py`, `test_rating_ladder_exact.py`, `test_score.py`, `test_score_compare.py`, `api/score.py` (one entry), spec 03 (T3 only), LG, `INDEX.md`, `roadmap.md`.

Outside the write set (or beyond the listed edits within a listed file):

| Path / region | Covered by | Verdict |
|---|---|---|
| `test_rating_score_batch_outputs.py::test_relativity_and_percentage_take_the_decimal_string_form_never_a_float` | the maintainer's (by delegation) entry "2026-10-23 10:48:01 BST" (A) | ruled |
| `test_rating_ladder_exact.py::test_the_float_path_fails_the_near_tie_fee_case` | the entry "2026-10-23 10:54:28 BST" item 2 (**not** an entry stamped "11:00": no such heading exists in `to-lead.md`; the LG calls it "the entry the lead relayed as '11:00'" — B5) | ruled |
| `docs/plans/PL-01568-…` (status `active` + an activation note) | GO "10:15:22 BST": "Lean P2 L1 (draft→active rides the slice PR; this header is quoted in the LG)" | ruled |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | **no ruling, and not changed** | **B1: the slice needs this file in its write set and did not touch it** |

### 4. RED/GREEN lines in `LG-1896` against logs (`~/gi-pricing-plan.local/scratch/sl-1569/`, listing: `audit.log changed-src.txt closure-tests.txt closure.py contracts.log docindex*.log lib.sh reqcov.log task0-step3.txt w1-green-a.log w1-head-before-codes.log w1-head.sh w1-red-base.log w1-red.sh w1-setup.* w2-window.sh t6/`)

| LG line | Log | First line = head sha? | Summary matches | Verdict |
|---|---|---|---|---|
| Task 0 Step 3 counts all 0 | `task0-step3.txt` (counts only; the first query is quoted in the LG, the other two are described) | n/a | yes | ok; queries 2 and 3 not quoted (B5) |
| RED `4993809d` `15 failed, 1 passed` / `18 failed, 16 passed` / item 9 red | **none** | — | — | **B2** |
| GREEN `18a261af` `71 passed` | **none** | — | — | **B2** |
| RED `5d5fb763` `4 failed, 2 passed`; GREEN `2eba040e` `10 passed` | **none** | — | — | **B2** |
| RED `bb1cc5b4` `4 failed, 36 passed`; GREEN `b1935f33`; item 28 red x4; `53 passed` | **none** | — | — | **B2** |
| Task 4 RED `02d4bc6d` direct-call harness, GREEN `4ba9d138`, `58 generated contracts match` | `contracts.log` (message only) | no head line | message yes, **rc absent** | **B4** |
| Deviation 5 `119 passed` | **none** | — | — | **B2** |
| Backend RED on base `13 failed, 247 passed, 2 skipped in 126.89s` | `w1-red-base.log` | `tree: ef07a2e6…` (the LG says ef07a2e6 + base src; the header lists the staged base src) | verbatim; rc=1 | ok |
| Backend RED on HEAD `5 failed, 255 passed, 2 skipped in 102.28s` | `w1-head-before-codes.log` | `ef07a2e6…` | verbatim; rc=1 | ok |
| Backend GREEN `259 passed, 2 skipped, 5 warnings in 141.25s` | `w1-green-a.log` | `ef07a2e6…` **plus an uncommitted diff** (` M backend/src/app/api/score.py`, ` M backend/tests/test_score.py`, ` M docs/specs/…`); rc=0 | verbatim | ok as disclosed ("tree ef07a2e6 plus the working diff of fd09bc7b"); the tested content cannot be proven equal to the committed `fd09bc7b` (no diff hash). Evidence of the test names: the base-red log lists `test_the_float_path_is_an_internal_error_that_leaks_no_value`, a name absent at `fd09bc7b`/`b699c3d1` (`git grep -c`: 1 at `ef07a2e6`, none at `fd09bc7b`), so `test_score.py` was edited between runs. The gate decides |
| Limb 3 (script `limb3.py` sha256 prefix `6fa80c30e43bf1c4`, HEAD `38643ee1`, tree `ddc26d37`) | **none**; no `limb3.py` anywhere under `scratch/`; `sha256sum scratch/sl-1569/t6/limb13.py` = `e9f57bfd60e56eb9…`, written after the ledger commit (mtime 10:08Z vs `cc6b4774` 10:05:31Z) | tree: `38643ee1^{tree}` = `ddc26d37` ✓ | — | **B3** |

All backend windows ran at times consistent with the LG (09:53–10:03Z = 10:53–11:03 BST; `TZ=Europe/London date` at audit 11:10 BST).

### 5. Test set derivation (common item 29)

`closure.py` (`scratch/sl-1569/closure.py`) walks `ast` imports from the 5 changed modules (`changed-src.txt`: `api/score.py`, `traces.py`, `scoring.py`, `ladder.py`, `score.py`) through two importer levels and prints 293 test files of 333 (`closure-tests.txt`, 293 lines; first line `backend/tests/test_api_acknowledge.py`). It is an import walk, not a text grep, as required; it matches the LG's "293 of 333". The LG quotes the `git diff --name-only` form and the count but **not the walk's command**; the script and list live only in scratch (B5). `closure-tests.txt` contains `test_quote_input_raise_sites.py` (count 1): the file the closure demands and the slice did not run (B1). Not re-run by the auditor (the script writes into the executor's scratch).

### 6. The six deviations (LG `:44-51`)

1. Tasks 1+3 together: disclosed with cause and failing lines; accepted ("10:48:01"). ✓
2. Item 7 control: disclosed; accepted. ✓
3. Item 24 control: disclosed with cause (engine returns int `3`); noted "10:54:28" item 2. ✓
4. Batch-outputs test rewrite: disclosed; ruled "10:48:01" (A). Quoted red `ValueError: score_batch: a relativity output must be a positional decimal string, got int` — a `ValueError` whose text is the branch's own (no log, B2).
5. Ladder-exact test: disclosed; **mis-cited** ("11:00"), true header "2026-10-23 10:54:28 BST — Maintainer: SL-1569 DB window under the FREE gate-1b slot (not an exception); the FR-273 float-path test may assert the refusal", item 2 (B5).
6. **DB-window deviation, stated plainly.** The window ran 10:53–11:03 BST on `GIP_GATE_SLOT` unset (log headers) via `run-small.sh`'s small-test flock (the maintainer's 11:09:09 entry says "`GIP_GATE_SLOT=small-test`"), redis db 13, own DB `gip_test_sl1569`, **beside FD-1872's held gate-1** (`lslocks` in the headers), **not** under the gate-1b slot the maintainer granted at 10:54:28 item 1, and it **continued through the ~10:57 hold** and sent **no WINDOW START/END**. The maintainer's (by delegation) entry "2026-10-23 11:09:09 BST — PL 8205 noted; SL-1569 DB-window DEVIATION accepted on evidence, with two standing corrections": accepted, "backend GREEN `fd09bc7b` '259 passed, 2 skipped' (base '13 failed, 247 passed') counts as the slice's red/green; the gate decides anyway". LG deviation 6 does not mention the hold or the missing WINDOW START/END and does not cite the 11:09:09 acceptance; it should (B5). The `ZEROS` for redis db 13 and the dropped DB are claimed in the LG; the logs do not carry them (no cleanup log) — the LG line is the only record.

### 7. Spec text

`git diff origin/main...b699c3d1 --stat -- docs/specs` = `03-rating-engine.md | 2 +-` (1 line). Applying `RL-1567` T3 (find block 4, new block 5) to `origin/main:docs/specs/03-rating-engine.md` with `str.replace(find, new, 1)` gives a file **byte-identical to the branch's** (`head == main.replace(find,new,1)` → True). Counts: find string in main 1 → in branch 0; new text in main 0 → branch 1. T3 applied at the owned-code list (the line moved from `03:929` to `03:1119`, same row). T2 (FR-214): its new text is present on `origin/main` (count 1, from SL-1566 `cad75a7e`, ancestor of the branch), and the branch applies no T2, as `PL-1568` §"Spec text owed" prescribes ("SL-1566 first"). No open question touched (`git diff --name-only` lists no `open-questions.md` or spec §10), so there is no mirror to check. `req-coverage.py`: `reqcov.log` exists, ends in the per-requirement table; **no rc captured and the LG claims none** (B4). `audit-docs.py` (`audit.log`): the only `FAILED` block is `check 31: gap in the full allocation between 1859 and 8154`, the expected working-id failure.

### 8. Contracts

`generate-contracts.py --check`: `contracts.log` holds the single line `58 generated contracts match the models`; no exit code was captured in the log (the seat reported one rc was `tail`'s). The branch diff shows the generated `score-comparison.schema.json` and `openapi/generated.json` regenerated with `OutputValue` and no hand edit, and the hand-authored `scoring.schema.json` agrees (`test_generated_and_authored_agree_on_the_scoring_outputs_value_schema`, green in the 259 window). The claim "the check passes" is plausible; the **rc is not evidenced** (B4). Per `close-workstream` §3 the contract matching the model proves neither correct; the requirement text (`RL-1343` rule 4: no non-integer number at any depth) was read against `scoring.schema.json` `OutputValue` (integer, string, boolean, object, array, null) — consistent.

### 9. Stored-data check

`task0-step3.txt` (2026-10-23T09:53Z, `gipricing`): algorithms with a decimal-family output 0; rating versions on them 0; pending traces on them 0; pending traces total 0; rating versions total 0. The LG quotes the first query verbatim (`select count(*) from rating_algorithms a where exists (… jsonb_array_elements(coalesce(a.content->'outputs','[]'::jsonb)) …)`) and describes the second and third in words. All counts 0 but the totals are 0 too: the check passes vacuously on an empty dev DB, which is what Task 0 Step 3 asks to record. Queries 2 and 3 are not quoted (B5, minor).

### 10. The carry line (NFR-502)

LG `:99`: "The NFR-502 timing verdict is CARRIED to nfr-bench-1, base = main before SL-1569 (`4e399fd0`), owner WK-1178 (D1 = (b))" — names the base commit and the owner, as the GO required. Limb 3's structural result is claimed in the LG (response_model/response_field `None`, `$ref` on 200) with **no log or script behind it** (B3). Limbs 1–2: **DIAGNOSTIC, not run** (no `w2.log`, no `t6/out.jsonl`; `w2-window.sh` and the `t6` scripts exist). The plan's Acceptance 19, as amended by D1 = (b), says limbs 1–2 "run locally as DIAGNOSTIC readings only": they are a deliverable owed before close, not a blocker of this audit.

### 11. Other

- `LG-1896` front matter `tree: fd09bc7b` is the backend commit, not the branch head `b699c3d1` (minor).
- Commits are Conventional-Commit shaped; the trailer form is not part of this audit.
- Barred-word check on the branch's added lines: `git diff origin/main...origin/sl-1569-wk1178-decimal-outputs | grep '^+' | grep -v '^+++' | grep -o -i ".\{25\}delegat.\{12\}"` prints six matches, each in the form "(by delegation)"; none is the barred word.

## Verdict proposed

**NOT-CLEAN** — six B-items, one of which (B1) is a real failing test the slice's own change causes, and three (B2, B3, B4) are evidence claims that no log supports. The code, the tests it added, the contracts and the spec text read as correct against `RL-1343`/`RL-1567` and `PL-1568`. The verdict is the lead's.

## B-items

- **B1 — `test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case` fails at `b699c3d1`.** `_build_outputs` gains a `_raise_named` call (`score.py:848`); the census `_raise_sites()` (`test_quote_input_raise_sites.py:142-158`) keys it as `("rating/score.py", "_build_outputs"): 1`, absent from `_INPUT_FREE` (`:62-`), so `others == _INPUT_FREE` (`:180`) is false. AST count at `origin/main`: `_build_outputs` absent; at the branch: `'_build_outputs': 1`. Seat-brief item 11 names this exact trap; the file is not in the write set, was not changed, and is not in any small run (it is in `closure-tests.txt`, so the full gate would turn red). Needs the lead's/maintainer's ruling to add the file (and an `_INPUT_FREE` entry saying the text names the output and type, never a value, with a sentinel case driven through `score_one` and `score_batch` if the guard's rule requires one).
- **B2 — twelve LG RED/GREEN lines have no log:** Task 1+3 (`15 failed, 1 passed`, `18 failed, 16 passed`, item 9 red, `71 passed`), Task 2 (`4 failed, 2 passed`, `10 passed`), Task 3b (`4 failed, 36 passed`, item 28 red x4, `53 passed`), deviation 4's red, deviation 5's `119 passed`. Only the three backend `w1-*.log` files exist.
- **B3 — limb 3 has no evidence:** no `limb3.py` and no output log; the sha256 prefix `6fa80c30e43bf1c4` matches no file in scratch (`t6/limb13.py` is `e9f57bfd60e56eb9`, written after the ledger commit).
- **B4 — no exit code is captured for `generate-contracts.py --check`, `doc-index.py --check` or `req-coverage.py`** (`contracts.log`, `docindex-check.log`, `reqcov.log` are output only); the LG claims the contracts message without an rc.
- **B5 — `LG-1896` accuracy:** deviation 5 cites a non-existent "11:00" entry (true header "2026-10-23 10:54:28 BST …" item 2); deviation 6 omits the hold, the missing WINDOW START/END and the 11:09:09 acceptance; the import-closure command is not quoted (only `scratch/` holds it); the stored-data queries 2–3 are not quoted; front matter `tree:` is `fd09bc7b`, not the head.
- **B6 (minor) — a Global Constraint without a test:** the "decimal-family output with no exact read and a non-null value raises `ValueError`" branch (`score.py:859-866`) is untested.

## Owed

- The full two-half gate (items 21–23), through the gate-runner, with `frontend/src/api/generated/schema.d.ts` change recorded (the typed `outputs` value changes the OpenAPI); then `req-coverage.py` and `audit-docs.py` rc 0 in it. Not a B-item: the gate is not yet launched.
- Task 6 limbs 1–2 as DIAGNOSTIC readings (`w2-window.sh` exists, window not run) — owed to the slice before its close; the plan (as amended by D1 = (b)) makes them a deliverable, not a merge blocker for this audit.
- The NFR-502 timing verdict on nfr-bench-1: owner WK-1178, base `4e399fd0` (D1 = (b)); the user starts the VM with ≥ 2 h notice.
- This record's mint **in the slice's PR, before CI** (seat-brief item 34): fold this RS file into the slice branch, mint `RS-1897` with the slice's ids, re-point every cite, audit-docs rc 0.
- The slice's closing acts after a clean re-audit of B1–B6: `LG-1896` and the `SL-1569` row to `closed` (the auditor's act at slice close), the MERGE-ACK quoting the gate's `Test Files N passed` line.
- The re-audit rule: after the fixes, re-run the specific checks that found B1 (AST count + the census test's own assert) and B2–B5 (log presence and heads), scoped to what changed, naming the tree.
