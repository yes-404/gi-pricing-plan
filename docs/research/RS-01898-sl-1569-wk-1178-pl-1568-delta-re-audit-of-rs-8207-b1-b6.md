---
id: RS-1898
family: research
kind: audit
title: SL-1569 (WK-1178, PL-1568) delta re-audit of RS-1897 B1–B6 at bf845e11
status: draft
created: 2026-10-25   # drafted 2026-10-23 under working id 8210; minted 2026-10-25 as RS-1898
owner: auditor
tree: 41e3c4f826645b646a465c25b8b5434cfbe6a102
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1569, PL-1568, LG-1896, RS-1897]
---

# RS-1898 — SL-1569 delta re-audit of RS-1897 B1–B6 at `bf845e11`

*(Working id 8210, written by `aud-1569b`, 2026-10-23, from `brief-aud-1569b-2026-10-23.md` (lead 27). Check 31/32 on this id is expected until the mint. The ledger is cited as `LG-1896`, its working id; the first audit as "RS-1897". Read by `git show` / `git diff` and plain reads of `~/gi-pricing-plan.local/scratch/sl-1569/r/`; no test, no DB, no gate was run; the one script run is a read-only AST count in the job tmp (Findings 1). `aud-1569b` proposes; the verdict is the lead's.)*

## Question

Branch `sl-1569-wk1178-decimal-outputs`, delta `b699c3d1..bf845e116c309796c9d016b59c985d14347c17b1` (tree `41e3c4f826645b646a465c25b8b5434cfbe6a102`, five commits: `03bfe46a` B1, `bf67458e` B6, `1ca04ad6` the B2–B5 LG commit, `f05a2d0c` stored-data SQL, `bf845e11` left-over LG edits), plus `LG-1896` as it stands: does each of RS-1897's B1–B6 now meet the maintainer's conditions in the entry "2026-10-23 11:19:33 BST — Maintainer: SL-1569 RS 8207 NOT-CLEAN — adoption CONFIRMED; B1 fixed inside the slice; gate turn moves behind" (`to-lead.md`, read by heading)?

## Method

Scope came from RS-1897's B-items and that entry's conditions **before** the ledger or the logs. Then evidence: `git diff b699c3d1..origin/sl-1569-wk1178-decimal-outputs` (3 files: the LG and two test files; **0 files** under `packages/*/src`, `backend/src` or `backend/tests`: `git diff --name-only b699c3d1..<head> -- packages/pricing-core/src packages/model-schema/src backend/src backend/tests | wc -l` = 0); every log under `scratch/sl-1569/r/` read at line 1, summary line and `rc=`; `sha256sum` of the limb-3 script; `git diff origin/main...<head>` for the census file. Clock at audit: `TZ=Europe/London date` = 11:33 BST, load1 2.57.

## Findings

### B1 — the census entry (`03bfe46a`): met in substance; one log-form gap

- **The entry exists.** `packages/pricing-core/tests/test_quote_input_raise_sites.py` at the head: `("rating/score.py", "_build_outputs"): 1,` in `_INPUT_FREE`, preceded by a comment citing `test_a_near_integer_under_an_integral_type_is_refused_with_rating_type_mismatch` (exists, `test_rating_decimal_outputs.py:207`; line 216 asserts `"2.9999999999" not in str(caught.value)`).
- **The census file is not weakened.** `git diff origin/main...origin/sl-1569-wk1178-decimal-outputs -- packages/pricing-core/tests/test_quote_input_raise_sites.py` = `5 +++++`, no `-` line: one dict key and four comment lines added.
- **The census predicate holds at the head, by a static count (not a test run).** A Python AST script over `git archive` copies of the two trees (the predicate of `test_quote_input_raise_sites.py::_raise_sites`, `_SITE_NAMES = ("_raise_named", "CodedError", "_model_call_failure", "PlatformError")`, `_INPUT_SITES` removed, compared with the file's own `_INPUT_FREE` read by `ast.literal_eval`): at the head `input sites 11` (`len(_CASES)` = 11) and `others==_INPUT_FREE: True`; at `b699c3d1` (control) `others==_INPUT_FREE: False`, `diff: {('rating/score.py','_build_outputs'): (1, None)}` — the exact defect RS-1897 B1 named, now closed.
- **The log.** `r/b1-red.log` line 1 `b699c3d18c8142adea37dc6d7fdec5228043cd0f`, `1 failed, 18 passed`, `Left contains 1 more item`, `rc=1`: a proper RED. `r/b1-green.log` has `59 passed in 4.95s`, `rc=0`, but **line 1 is `tree (uncommitted fix on b699c3d18c8142adea37dc6d7fdec5228043cd0f)`, not a head sha**, and the run (11:19:35 BST) is before commit `03bfe46a` (10:19:46Z = 11:19:46 BST). The maintainer's condition read "log b1-green.log, head sha on line 1, rc": the rc is there, the head sha is not. No log runs the census at a committed head. The static count above stands in for it for the first assertion; the gate (the census file is in `closure-tests.txt`) decides.
- **The LG Scope sentence.** `LG-1896:30`: "**Write set grown by one site** (the maintainer's entry "2026-10-23 11:19:33 BST — Maintainer: SL-1569 RS 8207 NOT-CLEAN — adoption CONFIRMED; B1 fixed inside the slice; gate turn moves behind …", `to-lead.md`): `packages/pricing-core/tests/test_quote_input_raise_sites.py` (the `_INPUT_FREE` entry for `_build_outputs`, commit `03bfe46a`) — found by RS-1897 B1; outside PL-1568's write set; no plan delta for one line." Contains the required text. ✓

### B2 — the RED/GREEN lines: met except one unlogged, unmarked group

`LG-1896:107-116` replaces the unlogged lines with 7 re-run lines; each log's line 1 is `bf67458e9a43…` (the worktree head) with the tested tree named in the same line (`at.sh` swaps `packages/` files to the named commit, runs, restores; every log ends `restored: porcelain=0`). Summary lines matched against the LG, verbatim:

| LG line | Log | Summary in log | rc |
|---|---|---|---|
| Tasks 1+3 RED `4993809d` `15 failed, 1 passed` | `b2-task13-red.log` | `15 failed, 1 passed` | 1 |
| GREEN `18a261af` `71 passed` | `b2-task13-green.log` | `71 passed` | 0 |
| Item 11 mutation `40 failed, 3 passed`, `DID NOT RAISE ValueError` ×14, `decimal.InvalidOperation` ×9 | `b2-item11-mutation-src-4993809d.log` | `40 failed, 3 passed`; `grep -c '^E *Failed: DID NOT RAISE .*ValueError'` = 14; `grep -c '^E .*decimal.InvalidOperation'` = 9 | 1 |
| Item 9 mutation `2 failed, 24 passed`, `isinstance(68280.753915, str)` | `b2-item9-mutation-src-4993809d.log` | same, `where False = isinstance(68280.753915, str)` | 1 |
| Task 2 RED `4 failed, 2 passed` / GREEN `10 passed` | `b2-task2-red.log` / `-green.log` | same | 1 / 0 |
| Task 3b RED `4 failed, 36 passed` / `40 passed` / with batch_outputs `2 failed, 91 passed` | `b2-task3b-red.log` / `-green-alone.log` / `-green.log` | same; the dev-4 text `must be a positional decimal string, got int` ×2 in `-green.log` | 1 / 0 / 1 |
| Item 28 `6 failed, 47 passed`, four `'RATING_TYPE_MISMATCH' == 'ValueError'` | `b2-item28-red.log` | `6 failed, 47 passed`; `grep -c` of the quoted assertion = 4 | 1 |
| Head `53 passed` (batch_outputs) | `b2-head-test_rating_score_batch_outputs.log` | `53 passed` | 0 |
| Deviation 5 `1 failed, 25 passed` (`input_value=1357.4`); `119 passed`; "122 at the remedy head" | `b2-dev5-red.log` (`TESTSHA=b699c3d1^`), `b2-dev5-at-b699c3d1.log`; head: `43 + 26 + 53` = 122 in `b2-head-*` | same | 1 / 0 / 0 |

- **"Superseded (no log)" originals are marked, not deleted.** `git diff b699c3d1..<head> -- docs/ledgers | grep '^-'` shows only edited deviation 5/6, the Step 3 paragraph, the GREEN line, the closure paragraph, the limb-3 line and `tree:`; the original RED/GREEN lines at `:73,77,81` stay. The mark is **one collective sentence** (`:107`, "they replace the unlogged lines above, which are superseded (no log)") plus the explicit mark on limb 3 (`:101`); the original lines themselves carry no mark (minor).
- **The two mutation re-derivations are labelled** (`:109` "re-derived as a mutation control … the original `18 failed, 16 passed` is not reproduced"; `:110` "mutation control … the original … line is not reproduced"). ✓
- **GAP — Task 4 (`LG-1896:85`) is neither re-run nor marked.** "RED `02d4bc6d` (direct-call harness, no pytest): `planted FAIL KeyError 'OutputValue'` … GREEN `4ba9d138`: all five PASS" has no log and is not in the B2 list or marked superseded. The `generate-contracts.py --check` clause on that line is covered by `b4-contracts.log`; the harness RED/GREEN is not. RS-1897 listed "Task 4 RED/GREEN" under B4's rc only, so this is a residual, not a regression.
- **Other residual wording.** `:116` says "every B2 log ends in `rc=`"; each ends `restored: porcelain=0` with the `rc=` line just above it. `b6-green.log` and `b6-mutation-red.log` line 1 are labels naming `03bfe46a` (run before `bf67458e` was committed), not head shas; the B6 test is also in `b2-head-test_rating_decimal_outputs.log` at `bf67458e` (`43 passed`, `rc=0`), which carries the proper head.

### B3 — limb 3: met

`sha256sum ~/gi-pricing-plan.local/scratch/sl-1569/t6/limb3.py` = `9d900f5030ae1d6717e0ad71f5e61f702f21b3eafe25e9f9ea820b6145fe29c7`, equal to the LG's value (`:101`) — run by the auditor. The adapted-from file `scratch/sl1367-t5/limb13.py` = `59663b744502cee15abb38ad45d8acae54ace970a1d3540ecf1d793fce43e260`, equal to the value in the script's docstring. `t6/limb3.log`: line 1 `HEAD bf67458e9a4386d644cb7f06a73631dbdcbc2fdf tree f7580da94238b50e45589a4bd3b2461ca33624c7` (`git rev-parse bf67458e^{tree}` = the same); both routes found, `response_model None`, `response_field None`, 200 `$ref` `ScoringResult` / `ScoreComparison`; `rc=0`. The old sha prefix `6fa80c30e43bf1c4` is stated as matching no file. Not evidenced anywhere in the log: the LG's "load1 5.27 at start" (the log has no load line) — a claim the brief for the run barred above 5.0 (minor). Source commits since `bf67458e` touch no source (`git diff --name-only bf67458e..<head>` = the LG only), so the head tree this log names holds the same source as the audited head.

### B4 — rc captured: met

`r/b4-contracts.log` (line 1 `bf67458e…`) `58 generated contracts match the models`, `rc=0`; `r/b4-docindex.log` `docs/INDEX.md: OK (byte-stable)`, `rc=0`; `r/b4-reqcov.log` `requirements specified : 546`, `requirements marked    : 387  (70.9%)`, `rc=0`. LG `:118` quotes all three with rc. ✓

### B5 — the LG's accuracy: met, one convention note

- **The 10:54:28 header** is quoted verbatim in deviation 5 (`:52`): "2026-10-23 10:54:28 BST — Maintainer: SL-1569 DB window under the FREE gate-1b slot (not an exception); the FR-273 float-path test may assert the refusal" = `to-lead.md:30136`. ✓ (the mis-cited "11:00" is gone.)
- **Deviation 6 (`:53`)** now states the run was on `GIP_GATE_SLOT` unset and not under the gate-1b slot of the 10:54:28 item 1, **continued through the ~10:57 hold**, sent **no WINDOW START/END**, and cites the 11:09:09 acceptance with its heading verbatim (= `to-lead.md:30172`) and the counted GREEN `fd09bc7b` "259 passed, 2 skipped". ✓ (The maintainer's 11:09:09 text says `GIP_GATE_SLOT=small-test`; the LG says unset; the log headers say unset, as RS-1897 recorded.)
- **The closure command** (`:97`) is quoted: the `git diff --name-only origin/main...HEAD -- packages/pricing-core/src packages/model-schema/src backend/src` form, then `python3 scratch/sl-1569/closure.py`. Re-run by the auditor: the first command gives the same 5 modules as `scratch/sl-1569/changed-src.txt`, and the delta changes no source (above), so the closure and its 293-of-333 list stand. `closure.py` itself hard-codes the `sl-1569` worktree and overwrites `closure-tests.txt`, and lives in scratch, not the repo: re-runnable only on that host and path (minor; the auditor did not re-run the walk).
- **Stored-data SQL.** Query 1 quoted at `:69`; queries 2 and 3 quoted verbatim in the LG and byte-equal to `r/stored-data-q2q3.log` (line 1 `1ca04ad6…`, `# result: 0   rc=0` ×2, run `2026-10-23T10:28:50Z`); the "tables empty" caveat is there ("`rating_versions` 0, pending `scoring_traces` 0 … the zeros hold by emptiness; database `gipricing` only"). ✓
- **`tree:` field.** `bf67458e` = the last **code** commit (`git rev-parse bf67458e^{tree}` = `f7580da9…`), not the head (`bf845e11`, a docs-only commit; its tree `41e3c4f8…`). The LG states no convention for the field; the first audit's note was "`fd09bc7b` is not the head". `bf67458e` is correct if "tree = the last commit that changed what the tests ran on" is the convention, and it is the object every `r/` log names; the LG should say so in one line (minor).

### B6 — the untested branch: met

`test_a_decimal_family_output_with_no_exact_read_is_refused_naming_no_value` at `test_rating_decimal_outputs.py:150-162` (parametrised over `decimal`, `relativity`, `percentage`; `monkeypatch.setattr(score_module, "_exact", lambda result, name: None)`; `pytest.raises(ValueError, match="has no exact read")`; asserts `probe_out` and the declared type are in the message and `"19.8"` is not). Mutation control: `b6-mutation-red.log` `3 failed, 40 passed`, `rc=1`, the three failures being exactly the new test's three cases; `b6-green.log` `43 passed`, `rc=0`; at the head `b2-head-test_rating_decimal_outputs.log` `43 passed`, `rc=0`.

### The GREEN set after the last code commit

The two code commits are `03bfe46a` (`test_quote_input_raise_sites.py`) and `bf67458e` (`test_rating_decimal_outputs.py`); both **change tests only**: no source line has changed since `b699c3d1`. After `bf67458e` the only commits are `1ca04ad6`, `f05a2d0c`, `bf845e11`, all LG-only. The runs at the head `bf67458e` (lines 1 of `r/b2-head-*`, `b4-*`): `test_rating_decimal_outputs.py` `43 passed`, `test_rating_ladder_exact.py` `26 passed`, `test_rating_score_batch.py` `11 passed`, `test_rating_score_batch_outputs.py` `53 passed`, all `rc=0`. **Not re-run at any committed head:** `test_quote_input_raise_sites.py` (only the uncommitted-tree `b1-green.log`, B1 above) and the backend window (`test_score.py`, `test_score_compare.py`, `test_contracts.py`: `259 passed, 2 skipped` at `ef07a2e6` plus an uncommitted diff, disclosed in `:92`; the delta does not change what those files import). The gate (items 21–23) decides.

## Verdict proposed

**NOT-CLEAN, on two narrow B-items** — both about the form of evidence the 11:19:33 conditions asked for, not a defect in the code or tests: every substantive remedy reads as met (B1 entry and static census count, B3 hash match, B4 rcs, B5 text, B6 test and mutation), and the delta changes no source. If the lead reads the 11:19:33 condition "head sha on line 1" and "every RED/GREEN line gets its log path" as satisfied by the static count and the gate, **CLEAN with the two items owed to the gate and the next LG edit** is the equally supported reading; the verdict is the lead's.

## B-items

- **B1′ — `r/b1-green.log` line 1 is not a head sha, and the census test has no committed-head run.** The condition "head sha on line 1, rc" is met for rc only; the run was on an uncommitted tree before `03bfe46a`. Remedy: one `run-small` run of `test_quote_input_raise_sites.py` + `test_rating_decimal_outputs.py` at the final head, sha on line 1, quoted in the LG (or leave it to the gate, which includes the file, and say so in the LG).
- **B2′ — `LG-1896:85` (Task 4 RED `02d4bc6d` / GREEN `4ba9d138`, the direct-call harness) has no log and is not marked superseded.** Remedy: mark it "superseded (no log)" at the line, or re-derive it as a labelled mutation control like items 9 and 11.

## Owed

- Minor LG wording, no verdict weight: the collective (not per-line) supersession mark at `:107`; "every B2 log ends in `rc=`" (`:116`); the unevidenced "load1 5.27" (`:101`); a one-line statement of the `tree:` convention; `closure.py` hard-codes the executor's worktree and lives in scratch.
- Unchanged from RS-1897: the full two-half gate (items 21–23) and `req-coverage`/`audit-docs` rc 0 in it; Task 6 limbs 1–2 as DIAGNOSTIC readings; the NFR-502 timing verdict on nfr-bench-1 (owner WK-1178, base `4e399fd0`, D1 = (b)); the redis-13 / `gip_test_sl1569` zeros are claimed in the LG only (no cleanup log).
- This record's mint **in the slice's PR, before CI** (seat-brief item 34), with RS-1897's.
- The slice's closing acts after a clean re-audit.

- B1′/B2′ discharged 2a1588c9, verified by the lead directly, to-lead 2026-10-23 11:38:45 BST.
