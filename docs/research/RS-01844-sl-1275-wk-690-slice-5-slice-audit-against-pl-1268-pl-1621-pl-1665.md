---
id: RS-1844
family: research
kind: audit
title: SL-1275 (WK-690 Slice 5, the authoring view and WF-702 Route B) slice audit against PL-1268, PL-1621 and PL-1665
status: draft
created: 2026-10-22
owner: auditor
tree: 6408949fe094de0e2a3bf0d598f70cc952c76300
phase: P2
work: WK-690
corrected_by: []
relates: [SL-1275, PL-1268, PL-1621, PL-1665, RL-1616, RL-1362, WF-702]
---

# RS-1844 — SL-1275 slice audit

*(Working id 8151, reserved by the lead in eta.md. Written by `aud-1275`, 2026-10-22. Check 31 on this id is expected until the mint.)*

## Question

Does the tree `origin/main...fd1dbcff` meet the Acceptance Standards of `PL-1268`, `PL-1621` and `PL-1665` for `SL-1275`, and what does `LG 1839` fail to evidence? Authority: the lead's brief (to-lead "2026-10-22 00:50:46 BST"). The family is `RS` `audit` (`document-ids.md` §1.6: "auditor — a bespoke audit's method, evidence and verdicts; files every finding as `FD-`"; precedent `RS-1649`).

## Method

Range `origin/main` (`f3462d8fc1336dc4583fe8a7af92fed399993a55`)`...sl-1275-wk690-s5-authoring-view` (`fd1dbcff2df837143911fad847f9b88ffb8cd636`, tree `6408949fe094de0e2a3bf0d598f70cc952c76300`), PR #1359, 24 files, +2254 −63 (`git diff --stat origin/main...fd1dbcff`). Scope was read first from `PL-1665` S5 (5.1′, 5.3′, 5.7), `PL-1621` S5 (5.2, 5.4, 5.5, 5.6) and the `SL-1275` roadmap row; then evidenced at `fd1dbcff` with `git show`/`git grep`. The audit ran **no test, no gate, no DB**. It ran two cheap things at `fd1dbcff`: `uv run --directory <sl-1275 worktree> python scripts/generate-contracts.py --check` (rc 0, "54 generated contracts match the models") and one in-process call of `app.platform.objective_preview._run` (no DB; item B1). The gate evidence is `scratch/sl1275-gate/gate.log` (START head `fd1dbcff`, tree `6408949f…`, the same tree as this audit; every stage row `rc=0`; pytest `6656 passed, 13 skipped`; END 2026-10-21T23:50:09Z). "MET" means the named test or text exists at the tree and its assert was read; a pass is CARRIED from the gate (`pytest -q` lists no test names, so an individual test's pass is not separately confirmed). Verdicts are proposals; the lead adopts, amends or rejects them.

Ledger SHAs: all twelve SHAs `LG 1839` cites that are reachable commits (`41f73db2 37c0c66f 8d2fe052 c74da4f1 90078720 1fe70cab 203fee4c adc8885c 5cb23bb6 81952ca7 ad9eeb21 cd70551b`) exit 0 under `git merge-base --is-ancestor <sha> fd1dbcff`.

## Scope against evidence

| Item | Evidence | Proposed verdict |
|---|---|---|
| 5.1′ spec first: FR with 3a–3d + audit sentence | `FR 1840` in `02` §3.7 carries 3a (500 points), 3b (2 workers, 5 s), 3c, 3d (p95 ≤ 2 s / 500 points) and the NFR-484 audit sentence; `LG 1839` "Decisions" gives a reason for each value | MET |
| 5.1′ §5.1 row, §5.3 built line, WF-702 B1.4 citation, `model-schema` shapes | all four in the range diff (`02` §5.1 row; §5.3 amendment; `WF-702` B1.4; `objectives.py` `ObjectivePreview*`, request reuses `ObjectiveParameter`) | MET |
| 5.1′ "in the slice's first commit, before any code that calls the route" | the FR is `37c0c66f`, the second commit; the activation `41f73db2` is first. `37c0c66f` precedes every caller (`8d2fe052`, `c74da4f1`); the B1.4 citation (`203fee4c`) is later. `LG 1839` "Spec-first ordering" discloses this | MET in substance; literal "first commit" wording not met, disclosed |
| 5.1′ `generate-contracts --check` rc 0; `generate:api` leaves `frontend/src/api/generated` empty | rc 0 (this audit, `fd1dbcff`); gate `pnpm generate:api rc=0`; `git check-ignore frontend/src/api/generated` prints the path (VCS-ignored) | MET |
| 5.2 WF-702 Route B over HTTP, one file | `backend/tests/test_wf702_route_b.py`, two tests (flag on, create to two approvals; flag default, create 409); gate pytest rc 0 | MET, CARRIED by gate |
| 5.3′ parse only, 200 `ok:false` with position; 422 on malformed body | `test_objective_preview_api.py` `test_a_loss_that_does_not_parse_answers_200_ok_false_with_a_position`, `test_a_malformed_request_answers_422` | MET |
| 5.3′ derive-and-evaluate equals the fit's `compile_kernel`/`derive`; no copy | `test_the_curve_is_the_fits_own_kernel_…`; `objective_preview._run` imports `derive`, `compile_kernel` | MET |
| 5.3′ 3a: grid over maximum **and expression over an FR-145 limit** each 422 `VALIDATION_FAILED`, SymPy not called | grid limb: 422 by the request model (`test_3a_a_grid_over_the_maximum…`, `test_3a_an_over_cap_grid_is_422…`). Expression limb: see B1 | **NOT MET** (B1) |
| 5.3′ 3b: slow derivation → `ok:false` timeout, no worker left | `test_3b_a_slow_derivation_times_out_…_and_leaves_no_worker`, `…_work_not_yet_started_is_cancelled…`, API `test_3b_a_timeout_answers_ok_false_not_a_500` | MET |
| 5.3′ 403 without `model:fit` **or** without `custom_objective:author`; 409 flag off; permission first | `test_without_the_author_permission_the_answer_is_403_whatever_the_flag` uses a principal holding `model:fit` but not author. No test holds author without `model:fit`. 409 test present | PARTIAL: delivered but untested for the `model:fit` limb (B2) |
| 5.3′ nothing persisted, nothing audited | `test_a_successful_preview_writes_no_row_and_no_audit_event` | MET |
| 5.4 view: parse error at position; editor disabled with the flag off; `certified_with_findings` not styled as failure; `ChartFigure` with accessible table; accessibility report quoted | `ObjectiveEditorView.test.ts` "renders the route's parse error at the position it names", "disables the editor … OBJECTIVE_KIND_NOT_ENABLED"; `ObjectiveLossCurve.test.ts` NFR-463 table; the certified-with-findings rule is held by the existing `ObjectiveCertificateView.test.ts` (the editor renders no certificate outcome); report quoted in `LG 1839` "Accessibility review" (a code read, no screen reader). The editor learns the flag only from the first 409 (carried finding in the ledger) | MET; flag-off limb is "disabled after the first preview", disclosed |
| 5.5 one parser | `git diff --name-only origin/main...fd1dbcff -- frontend/src \| grep -ciE 'pars\|grammar\|evaluat'` prints `0` | MET |
| 5.6 both gate halves on the merge tree | gate.log at head `fd1dbcff`, tree `6408949f…`: ruff, mypy, import_linter, audit_docs, req_coverage, contracts, pytest, pnpm install/generate:api/lint/type-check/test/build all `rc=0`; demo D7 ok | MET |
| 3c "never queue ahead of `/score`": test of separate executors | `objective_preview._executor` is a private `ThreadPoolExecutor`; no test asserts it is separate from `/score`'s path (`git grep` of `_executor` in `backend/tests` finds none for it). `PL-1665` 5.7 requires this test apart from the timing | Delivered but untested (B3) |
| 5.7 3c and 3d measured in a TRUE ALONE window | `LG 1839` "Needs census": "Not met at the time of the build"; no measurement recorded; `PL-1665` S5 row: "S5 does not close until 5.7 is measured" | Not started. Deferred to the booked window; **blocks the slice's close** (B4) |

## Findings

**B1 — an expression over an FR-145 limit answers 200 `ok:false`, not 422 `VALIDATION_FAILED`; the test accepts both.** `FR 1840` clause 3a and `PL-1665` 5.3′ both say an expression over a profile limit answers 422 `VALIDATION_FAILED` before any SymPy work. `test_3a_an_over_cap_grid_is_422_before_any_sympy_work` asserts `status_code in (200, 422)` for the 299-node loss, with the comment "FR-145's limit is a grammar refusal, answered as one". This audit ran `_run` on that loss (150 `f` terms) at `fd1dbcff`: `{'ok': False, 'error': {'reason': 'grammar', 'message': 'line 1, column 1: the expression has 299 nodes; the limit is 200 (02 §4.6, FR-145)', …}}`. So the code answers 200 and the spec text says 422; the permissive assert hides it, and `LG 1839` does not disclose it. Under `CLAUDE.md` §0 code and spec disagree and one must be corrected visibly: either the route refuses an over-limit expression 422 (and the test pins `== 422`), or `FR 1840` 3a gets a dated amendment saying a node-count/depth overrun is a grammar refusal (200 `ok:false`) and `RL-1616` condition 3a is read accordingly. Which is right is the lead's (and the ruling's owner's) to decide; the audit proposes the first, since the ruling says "over any bound 422".

**B2 — the 403 limb "without `model:fit`" has no test** (see table). Delivered but untested; one test line closes it.

**B3 — no test that the preview executor is separate from `/score`'s** (`PL-1665` 5.7, last sentence). Delivered but untested.

**B4 — 5.7 is unmeasured.** Not started; the ALONE window is the lead's to book (`PL-1665` S5 row). The slice does not close until it is measured; `FR 1840` 3d's budget is provisional until then (`LG 1839`).

**O1 (observation, not blocking) — the F2 wire-text change.** `81952ca7` (with `5cb23bb6`) routes the grammar and preview refusals through `safe_error_detail` (NFR-499). Before, `grammar_refusal` returned `(line, column, str(exc))` and `_require_the_grammar` built `f"line {line}, column {column}: {reason}"` whenever `line` was not `None`, so an `ExpressionError` with a line and no column rendered `column None`. Now `grammar_refusal` returns `safe_error_detail(exc)` for an `ExpressionError` (`safe_error.py` `_expression_detail`, `line N` then `, column M` only if a column exists, then `: message`), and `_require_the_grammar` and the preview use that text as is. Effect: a line-only position reads `line N: message`; with a column the text is unchanged (`line N, column M: message`); with no line, `str(exc)` as before. The preview's position fields and the 422 `errors[0].message` carry the same string. Two further input-text edits come with it: the preview's `values` refusals no longer echo the parameter name (`"values names a parameter that is not declared."`, `"a value is outside its parameter's declared min..max."`). Affected spec/contract: `RL-1362` DP-S3-3 says the message begins `line <L>, column <C>:`; the line-only case now departs from that pattern, by design, and no spec text or contract file contains `column None` (`git grep -n -i "column None" fd1dbcff -- docs` finds none). The OpenAPI message fields are free strings, so the contract is unchanged (`generate-contracts --check` rc 0). Two residuals: the `SyntaxError` branch of `grammar_refusal` still builds `column {exc.offset}` and renders `column None` if CPython gives a line and no offset (not reproduced; none seen); and `backend/src/app/platform/modelling.py:310` still builds `f"line {line}, column {column}: {reason}"` for the Factor path (outside this range, same pattern). Whether `RL-1362` DP-S3-3 needs a dated line for the line-only form is the lead's.

**O2 — `LG 1839` does not record the NFR-499 fix (`5cb23bb6`, `81952ca7`), the first re-gate RED, or the GREEN re-gate.** Its Tasks end at the first DB run (`1fe70cab`); the DB-run results, the RED diagnosis and the GREEN gate (`scratch/sl1275-gate/`) live in scratch and from-lead only. A reviewer holding only the repository cannot reproduce them. Owed to the ledger before it closes.

## (ii) The mint

`fd1dbcff` ("mint LG 1839 and FR 1840 from working ids 8138 and 8140"): 18 files, +50 −48. The ledger was renamed to `docs/ledgers/LG-01839-…`; `FR 8140` became `FR 1840` in `02`, `WF-702`, the backend/model-schema docstrings and comments, the frontend comments and the three test files. `docs/contracts/openapi/generated.json` changed by exactly four description lines (`FR 8140` → `FR 1840`; the diff shows four `-`/`+` pairs and nothing else), the sed edit; `generate-contracts.py --check` rc 0 at `fd1dbcff` (this audit) and in the gate vouches that the generated file matches the models, whose docstrings the same commit re-pointed. Whole-tree sweep at `fd1dbcff` for `8138`/`8140` (`git grep -n -E "\b(LG|FR)[ -]0?(8138|8140)\b|\b(8138|8140)\b" fd1dbcff -- . ':!docs/INDEX.md'`): three hits, all in `LG 1839` lines 19, 44, 45, each a deliberate "minted from working id" provenance statement. No stale re-point. **MET.**

## (iii) Closing acts owed in this PR

At `fd1dbcff`: `LG 1839` `status: active`; the `SL-1275` roadmap row `status: active` (activated 2026-10-21, no "Closed" line); no roadmap closure line. All three closing acts are **absent**. Under `document-ids.md` §1.6 (SL row, amended 2026-10-04) the auditor's CLEAN verdict authorises them and the executor applies them in the mint commit. This audit is **not CLEAN** (B1–B4), so none is authorised yet. They also cannot be applied while 5.7 is unmeasured (`PL-1665` S5 row).

## Proposal

**NOT-CLEAN.** Blocking: B1 (spec/code disagreement on 3a, with a test that hides it). B2 and B3 are small missing tests. B4 (5.7) blocks the slice's *close*, not necessarily the merge, if the lead rules the merge may precede the window with the close deferred to an owner (the plan's wording: the code "may be built before the window"; "S5 does not close until 5.7 is measured"). O2 is a ledger completion. No `FD-` is minted by this record; the lead gives each finding its disposition and an id.

## Re-audit

After a fix, re-run only: the B1 call of `_run`/the route on the 299-node loss and the pinned assert; the new B2 and B3 tests; `LG 1839`'s added sections; and name the tree.
