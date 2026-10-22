---
id: RS-1845
family: research
kind: audit
title: SL-1275 (WK-690 Slice 5) re-audit of the delta fd1dbcff..96354f9c against RS-1844 B1-B4 and O2
status: draft
created: 2026-10-22
owner: auditor
tree: 530c3e1da5821a639577d4da3de8cdde1ada7359
phase: P2
work: WK-690
corrected_by: []
relates: [SL-1275, PL-1665, PL-1621, RL-1616, RL-1362]
---

# RS-1845 — SL-1275 re-audit of the delta

*(Working id 8152, reserved by the lead. Written by `aud-1275b`, 2026-10-22. Check 31 on this id is expected until the mint.)*

## Question

Does the delta `fd1dbcff..96354f9c` resolve `RS-1844`'s B1, B2, B3, B4 and O2, and does it introduce a defect? Authority: the lead's brief (to-lead "2026-10-22 00:57:13 BST", "11:15:26 BST", "11:38:53 BST"). The auditor of `RS-1844` was a different seat; this one read its record, not its reasoning.

## Method

Range `origin/main` (`f3462d8fc1336dc4583fe8a7af92fed399993a55`)`...sl-1275-wk690-s5-authoring-view` (`96354f9cddf968aabbc817570c2b0b3f6ea55a5a`, tree `530c3e1da5821a639577d4da3de8cdde1ada7359`; `git merge-base --is-ancestor f3462d8f 96354f9c` rc 0), PR #1359, 24 files. The delta is five commits: `d96b33f8` (tests), `a2e203fe` (fix), `27d33a3f` (ledger), `d49b207f` (test fix), `96354f9c` (ledger); `git diff --stat fd1dbcff 96354f9c` is 6 files, +145 −20. Spec read to the clause: `02` FR 1840 clause 3a and 3c/3d (`docs/specs/02-modelling.md:236`, unchanged by the delta), `PL-1665` 5.3′ and 5.7, `RL-1616` 3a. The audit ran **no test, no gate, no DB**. It ran, read-only at `96354f9c` in the slice worktree: `generate-contracts.py --check` (rc 0, "54 generated contracts match the models"); `ruff check` on the four changed `.py` files (rc 0); and in-process calls of `measure_expression` on hostile losses (item N1). Passes of the new tests are CARRIED from `LG 1839` item 11 (a DB run in the lead's window); this audit did not re-run them.

## Resolution of RS-1844

| Item | Evidence at `96354f9c` | Verdict |
|---|---|---|
| **B1** over-FR-145 expression is 422 `VALIDATION_FAILED` before derive | `backend/src/app/platform/objective_preview.py` `refuse_over_bound` raises `PlatformError("VALIDATION_FAILED", …, 422, errors=(FieldError(field="loss", code="VALIDATION_FAILED", …),))` when `size.nodes > DEFAULT_LIMITS.max_nodes or size.depth > max_depth`; `backend/src/app/api/custom_objectives.py` `preview_custom_objective` calls it after `refuse_expression_kind` and **before** `objective_preview.preview(body)`, so before `_run`, `grammar_refusal`, `derive` and SymPy. Test `test_objective_preview_api.py::test_3a_a_request_over_an_fr145_bound_is_422_validation_failed_before_any_sympy_work`: five params (`grid_points`, `nodes_with_grid`, `depth_with_grid`, `nodes_parse_only`, `depth_parse_only`), each `assert response.status_code == 422` and `["code"] == "VALIDATION_FAILED"`, with `derive` monkeypatched to raise `AssertionError`; the permissive `in (200, 422)` is gone. Bodies: 299 nodes (`" + ".join(["f"]*150)`) and depth 26 (`"-"*25+"f"`) against 200 and 20. A loss that does not parse stays 200: `refuse_over_bound` returns on `SyntaxError`, and `test_a_loss_that_does_not_parse_answers_200_ok_false_with_a_position` is untouched by the delta (`git diff` shows no change to it). Code now agrees with `FR 1840` 3a and `RL-1616` 3a; no spec text changed | **MET** (tests' pass CARRIED from `LG 1839` item 11) |
| **B2** 403 without `model:fit` | `test_without_model_fit_the_answer_is_403_though_the_author_permission_is_held`: fixture `author_without_fit` holds `{"custom_objective:author", "model:read"}`; asserts `403` for the flag off and on. Closes the limb RS-1844 named | **MET** |
| **B3** executor separate | `test_objective_preview.py::test_3c_the_preview_executor_is_its_own_and_shared_with_nothing`: `derive` stubbed to record `threading.current_thread().name` and raise `RuntimeError` (now wrapped in `pytest.raises(RuntimeError, match="stop after recording")`); asserts the name `startswith("objective-preview")` (the executor's `thread_name_prefix`, `objective_preview.py:46`), that an `asyncio.to_thread` thread does not, `_executor._max_workers == PREVIEW_WORKERS`, and that no other `.py` under `app/` contains both `_executor` and `objective_preview` (`users == []`). That last assert is a text grep, weak against a renamed alias; `git grep -c _executor -- backend/src` finds `_executor` only in `objective_preview.py` (2 hits). What it shows is "the preview does not run on the default `to_thread` pool and no module touches its pool". `PL-1665` 5.7 last sentence asks "a test … of separate executors"; this is that test. It does not exercise `/score` itself; the p99 under saturation is B4's measurement | **MET** (as the plan words it) |
| **B4** 5.7 unmeasured | Not measured, as the maintainer ruled merge-then-measure ("2026-10-22 00:57:13 BST"; precedent SL-1367 Acc 10). `LG 1839` "Findings carried to the lead" now carries the item: owner WK-690; (1) flag default OFF, quoted `backend/src/app/platform/settings.py:318` `"features.expression_objectives_enabled": False` (read here at `96354f9c`, same line); (2) slice stays `active` in the `SL-` row and ledger, closes only on the 5.7 measurement in a TRUE ALONE window; (3) `FR 1840` 3d provisional until measured (the FR still says "diagnostic measurement" and the p95 ≤ 2 s budget, `02`:236); and says the MERGE-ACK request quotes all three | **Deferred with an owner (WK-690)**; the measurement itself is **not started**; blocks the slice's close, not the merge, per the ruling |
| **O2** ledger completeness | `LG 1839` items 7 (first re-gate RED and its classification), 8 (NFR-499 fix `5cb23bb6`, `81952ca7`, the F2 wire text), 9 (GREEN gate at `fd1dbcff`), 10 (audit and R1–R3), 11 (the DB window) | **MET** |

## LG 1839 item 11 against the lead's required contents

- **RED (4 + grid_points pin):** "rc 1, `4 failed, 10 passed`" at `d96b33f8`; the four failing params are named (`nodes_with_grid`, `depth_with_grid`, `nodes_parse_only`, `depth_parse_only`, each `assert 200 == 422`); `grid_points` "passes at the red head: a regression pin of the request model's `PREVIEW_MAX_GRID_POINTS` cap, already 422". Consistent with the code: the grid cap is the request model's, so five params would give 4 failures. Ordering is reachable: `d96b33f8` (tests only, `git show --stat`: two test files) precedes `a2e203fe` (the fix, three files).
- **The `27d33a3f` defect:** "`1 failed, 39 passed`. A TEST DEFECT, not green", the stub's `RuntimeError` escaping `preview`, fixed by `d49b207f` "every assertion kept, no product code changed". The diff confirms `pytest.raises` was added around the call and no assert was removed or loosened (`git diff fd1dbcff 96354f9c -- backend/tests`).
- **GREEN at `d49b207f`:** "rc 0, `40 passed`, 0 failed, 0 skipped" over three named files. `d49b207f` is a test-only commit and `96354f9c` is ledger-only, so the tested code equals the head's code. (The window's output is quoted, not independently reproduced here.)
- **R2's red not shown:** recorded as a "DISCLOSED GAP", "tests written and green, not red-first; only R1 is red-first". The ledger does not claim red-first for R2. Correct.
- **Cleanup:** DB dropped (count 0), redis `DBSIZE` 56 before and after (the harness's rule 22/23 asks for 0; 56 equal before and after is disclosed, with the lead's ruling "2026-10-22 11:15:26 BST" the authority — not re-opened here).

## Findings

**N1 (checked, not a defect) — `refuse_over_bound` catches only `SyntaxError`.** `ast.parse` can also raise `MemoryError` or `RecursionError` on very large inputs (measured here: `"-"*20000+"f"` gives `MemoryError`; `"f+"*50000+"f"` gives `RecursionError`). The request model caps `loss` at `max_length=2000` (`packages/model-schema/src/model_schema/objectives.py:539`). Within 2000 characters this audit tried unary chains (2000 characters, `ExpressionSize(nodes=2000, depth=2000)`), `+` chains, `not` chains, `lambda` chains, conditional chains, and parenthesis/bracket/call/dict nesting (the last four raise `SyntaxError: too many nested parentheses`, which the function catches). None raised anything but `SyntaxError` or returned a size. So no 500 is reachable through the route. Side effect worth knowing, not blocking: an over-bound text that `grammar_refusal` itself cannot survive (it raised `RecursionError` on a 2000-character unary chain and on `"f+"*999+"f"`) is now answered 422 by `refuse_over_bound` first, because `measure_expression` counts iteratively. The `RecursionError` in `grammar_refusal` is **pre-existing** (create path, `_require_the_grammar`, not in this delta) and unreachable from the preview after the fix; no `FD-` is proposed by this record, and whether the create path needs one is the lead's.

**O3 (observation) — ordering of the 422 limbs against the 409.** The grid limb is refused by the request model (before the route body, hence before the flag check); the expression limb is refused after `refuse_expression_kind`. With the flag off, an over-node loss therefore answers 409 and an over-grid body 422. `FR 1840` says permissions are checked "before the flag" and is silent on bounds against the flag; no test pins either order. Not a defect against the text; stated so the lead can rule on it or ignore it.

**O4 (observation) — `LG 1839` item 10 still says "The DB red-then-green run is owed in the lead's window".** Item 11 says it "discharges task 10's owed run", so the pair reads correctly in order; a reader of item 10 alone sees a stale owed line. Not a defect.

**O1 of RS-1844 (F2 wire text)** is unaffected by the delta; it is already recorded in `LG 1839` item 8.

## Generated contract

`docs/contracts/openapi/generated.json` changed by exactly one `description` line (the preview route's docstring now ends with the 422 sentence); it equals the new docstring in `custom_objectives.py` and `generate-contracts.py --check` at `96354f9c` is rc 0 ("54 generated contracts match the models"). No schema shape changed.

## Owed, not defects

- The **re-gate at the new head** (the maintainer's GO follows the SL-1711 compose retry).
- The **closing acts** (`LG 1839` and the `SL-1275` row stay `active` by the B4 ruling), and PR CI.
- The 5.7 measurement (B4).

## Proposal

**CLEAN for the delta**, with B4 carried as the ruled, owned, merge-then-measure item and the re-gate owed. Blocking items: none. B1, B2, B3 and O2 are resolved; B4 is deferred with the owner WK-690 and its three conditions quoted from code and ledger. N1 is checked and closed; O3 and O4 are observations. The verdict is the lead's.
