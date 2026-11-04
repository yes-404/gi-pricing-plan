---
id: RS-1865
family: research
kind: audit
title: SL-1260 (WK-674 Slice 6) delta re-audit of the maintainer's 17:34:47 items 2 and 4, c55410d6..57b7fa04
status: draft
created: 2026-10-22   # drafted 2026-10-22 under working id 8187; minted 2026-10-23 as RS-1865
owner: auditor
tree: 13fc30f525065bec48714d00d6fd4b825595f0c4
phase: P2
work: WK-674
corrected_by: []
relates: [SL-1260, LG-1859, RS-1864, RL-1834]
---

# RS-1865 — SL-1260 delta re-audit, items 2 and 4

*Minted 2026-10-23 as RS-1865 from working id 8187, in the SL-1260 audit-records docs PR. Prose below that calls this record or another id "unminted" or names a working id describes the draft state at filing, not the tree at the mint.*

*(Working id 8187, reserved by the lead. Written by `aud-1260b`, 2026-10-22, from `brief-aud-1260b-2026-10-22.md` (lead 26); fresh seat, not the author of RS 1864. Check 31 on this id is expected until the mint. `LG-1859` is cited by its working id. Scope is only items 2 and 4 of the maintainer's entry "2026-10-22 17:34:47 BST" and the maintainer's later acceptance of the correction relayed by the lead ("the two control runs (24-nv4, 25-nv5) ARE item 2's red … No duplicate assertions"); everything else is settled by RS 1864.)*

## Question

Do the positive audit-event assertions plus controls V2b/V2c meet item 2, and do the `03` clause, the test, the green and red controls and `LG-1859` meet item 4, of the maintainer's entry "2026-10-22 17:34:47 BST"?

## Method

Object `origin/sl-1260-wk674-s6` at `57b7fa0419811b169ab782e2e6a56d55dc0e24a5` (tree `13fc30f525065bec48714d00d6fd4b825595f0c4`). Delta `c55410d6..57b7fa04`: six commits. Read through `git show`, `git diff` and `git log` on the fetched ref; logs 21 to 27 under `gi-pricing-plan.local/scratch/sl1260-db/` read directly. No test was run by this seat.

## Findings

### Check 1 — item 2, one audit event of the right type with before and after

**Verdict: met.**

- `test_routing_write.py`: `_events` filters `AuditEventRow.workspace_id == workspace_id` and `AuditEventRow.action == _ACTION` (`_ACTION = "deployment.routing_changed"`, line 34). The positive test unpacks `(event,) = await _events(...)` (line 103), so exactly one event of that action, then asserts `entity_ref == "environment:dev"`, `before is None` and `after["ranges"][0]["deployment_id"]`. The second-write test unpacks `_, latest` (line 120), exactly two, and asserts `latest.before["ranges"]` equals the first response and `latest.after`.
- `test_shadow_write.py`: the same shape; `_ACTION = "deployment.shadow_configured"` (line 32), `(event,) =` at line 110 with `entity_ref == "environment:prod"`, `before is None`, `after["candidate_rating_version_ref"]`; `_, latest =` at line 126 with `before["fraction"] == 0.1` and `after["fraction"] == 1.0`.
- The tests are unchanged in the delta (the delta touches `backend/tests/test_routing.py`, the `03` spec and the ledger only), which matches the maintainer's accepted "no duplicate assertions".
- `24-nv4-routing-audit-skipped.log` (first lines: head `571d8319`, `backend/src/app/platform/routing.py | 2 +-`, 1 insertion, 1 deletion) ends `3 failed, 11 passed, 1 warning in 7.51s`, with verbatim `FAILED backend/tests/test_routing_write.py::test_a_rule_naming_a_deployed_version_is_written_and_audited`, `::test_a_second_write_appends_and_records_the_previous_rule_as_before`, `::test_a_routing_change_cannot_commit_without_its_audit_event`; the traceback names `ValueError: not enough values to unpack (expected 1, got 0)` at `test_routing_write.py:103`.
- `25-nv5-shadow-audit-skipped.log` (first lines: head `571d8319`, `backend/src/app/platform/shadow.py | 2 +-`) ends `3 failed, 9 passed, 4 warnings in 5.60s`, failing `test_shadow_write.py::test_a_compiled_candidate_is_configured_and_audited`, `::test_a_second_write_appends_and_records_the_first_as_before`, `::test_a_shadow_change_cannot_commit_without_its_audit_event`; `ValueError … expected 1, got 0` at `test_shadow_write.py:110`.
- Reverted and never committed: `git log c55410d6..57b7fa04` has six commits (ledger, spec, test only), none touching `backend/src`; `git diff --stat c55410d6..57b7fa04` lists three files, none under `backend/src`.

Two readings, neither blocking. (a) Each log records the mutation as a `--stat` only, not the diff text; the mutated text (`await audit.record(` replaced by `(lambda *a, **k: None)(`, `routing.py:131`) is stated in the ledger alone. The stat plus failures at the `(event,)` unpack make it credible; the logs do not prove the text. (b) The logs label a commit sha (`571d8319`, a commit: `git cat-file -t`) as "tree:".

### Check 2 — item 4, `_routed` fails closed, declared and pinned

**Order.** `11114581` (spec, 2026-10-22T16:39:01Z) precedes `c4333aa6` (test, 16:40:19Z); `git merge-base --is-ancestor 11114581 c4333aa6` exits 0. Met.

**Clause against intent.** The maintainer's item 4, verbatim: "a routing selection failure fails the quote (5xx, problem code named) and never falls back; a shadow failure never affects the response". The `03` §4.13 Selection hunk adds: "**A routing selection failure fails the quote and never falls back:** when reading the flag or selecting a range raises, the quote is refused 500 `INTERNAL_ERROR` and is not scored by the default-live version, because a fallback could price from the wrong Rating Version. A shadow failure never affects the response (below)." with a dated provenance note naming the entry and item 4. Both limbs present. Met.

**`INTERNAL_ERROR` as the named code.** It is the platform's one catch-all 500 code: `backend/src/app/errors.py:626` (`code="INTERNAL_ERROR"`) and `:432`, asserted in `test_errors.py:102`; the generated OpenAPI carries the 500 "Internal server error" response. `git grep INTERNAL_ERROR 57b7fa04 -- docs/specs` finds no hit: it is not in any spec catalogue, and until this clause no spec named it. It satisfies "5xx, problem code named" literally, and the test asserts the code, not only the status (`failed.json()["code"] == "INTERNAL_ERROR"`). Whether a generic code is the intended "named" one, or a dedicated routing code was meant, is the lead's reading; the maintainer's wording does not say. **Proposed: acceptable, flagged.**

**The test.** `test_a_routing_selection_failure_fails_the_quote_and_never_falls_back`: healthy selector, flag on, `_score` 200 and `refs_scored == [LIVE]`; `routing.select_range` monkeypatched to raise `RuntimeError`; `refs_scored.clear()`; second `_score` asserts 500, code `INTERNAL_ERROR`, `refs_scored == []` (nothing scored). Both limbs of the brief present. `26-b-routing-green.log` (tree of `11114581` plus the test file, stat 30 insertions): `8 passed, 1 warning in 8.82s`. `27-nv6-routed-falls-back.log` (`api/score.py` 5 lines changed): `FAILED backend/tests/test_routing.py::test_a_routing_selection_failure_fails_the_quote_and_never_falls_back`, `assert 200 == 500` at `test_routing.py:265`, `1 failed, 7 passed`.

**Gap, not blocking.** The clause says "reading the flag or selecting a range raises"; the test breaks `select_range` only. A flag-read failure is not pinned by a test. The clause's shadow limb ("never affects the response") has no new test in this delta; it rests on the existing guarded `_shadow_task` and prior tests (not re-read here).

### Check 3 — other changes in the delta

`git diff --stat c55410d6..57b7fa04`: `backend/tests/test_routing.py` +30, `docs/specs/03-rating-engine.md` 1 line, the `LG-1859` ledger +64 −1 (3 files, +95 −2). Commits: `5148a135` ledger (controls V1 to V3, round trip, `_routed` observation), `ef90399d` and `571d8319` ledger deviation edits, `11114581` spec, `c4333aa6` test, `57b7fa04` ledger. No source change, no scope creep. The round-trip re-run (item 3) is outside this brief.

### Check 4 — `LG-1859`

It records item 2 ("V2b/V2c … the maintainer, 2026-10-22 17:34:47 BST item 2", mutation, both control rows with log names, rc, summary lines and failing names, "Reverted … never committed") and item 4 ("`_routed` fails closed, declared", spec-first order, test name, green log, red control). It cites the entry and quotes the clause fragment "a routing selection failure fails the quote and never falls back"; it **paraphrases** the items rather than quoting them verbatim (minor). The **Deviation** line reads "The lead's brief placed the round trip in this window … The fault is the brief's, not the seat's." — it names the lead's brief. Met.

## Verdicts proposed (the lead's to issue)

- Item 2: **CLEAN.** Item 4: **CLEAN**, with three flags for the lead: `INTERNAL_ERROR` is the generic code and in no spec catalogue; the flag-read path and the shadow limb carry no new test; the ledger paraphrases rather than quotes the items.

## Addendum — the maintainer's added check on `INTERNAL_ERROR` (via lead 26), read at `57b7fa04`

**(a) The catalogue's definition covers a server-side failure the caller cannot fix: MET against the code, with no spec catalogue entry.** The only catalogue is the code's: `backend/src/app/errors.py:431-433` lists `INTERNAL_ERROR` in `_GENERIC_ERROR_CODES` ("Codes raised by the shared request machinery"). Its definition is `unexpected_problem`, `errors.py:610-631`: docstring "The problem returned for an unhandled exception", `title="Internal server error"`, `status=500`, `code="INTERNAL_ERROR"`, `detail="The request failed unexpectedly. Quote the trace id when reporting it."` (lines 624-627); the message is fixed so the exception text does not reach the caller. `git grep INTERNAL_ERROR 57b7fa04 -- docs/specs` has no hit, so no spec row defines it; the `03` clause is the first spec text to name it.

**(b) The server log names the cause when `select_range` raises: the mechanism exists by reading; no test or log line proves it for this path — NOT MET as proven.** Path: `api/score.py:579` `routed = await _routed(...)` (unguarded; `_routed` calls `routing_service.select_range` after the flag read, `api/score.py:365-372`) → the exception propagates to `TraceMiddleware` (`observability/middleware.py:47`, `except Exception as exc`) → `_log.error("request failed", exc_info=safe_job_exc_info(exc), extra={method, path, duration_ms})` (lines 56-63) → `problem_response(unexpected_problem(...))` carrying the trace id (line 64). `exc_info` is the sanitised triple: the exception class is kept and the text is cleaned (`safe_exception.py:31-46`, `type(exc).__name__`), and the traceback frames are kept (comment, `middleware.py:53-54`), so the frames name `_routed` and `routing.select_range`; `JsonFormatter` writes it to the `exception` field (`logging.py:60-61`). Not proven: `test_routing.py` has no `caplog` and asserts only status, code and nothing scored; `test_errors.py:94-104` proves the 500 and the no-leak for `/_test/boom`, not the log line; `test_job_error_sanitiser.py:135` renders the sanitised `exc_info` for a different exception. The log line carries the failing frames and the class, not a message naming "routing selection" in words. If the maintainer wants (b) proven, a `caplog` assertion on `test_a_routing_selection_failure_fails_the_quote_and_never_falls_back` for a record at ERROR, message `request failed`, whose `exc_info` class is the raised one and whose frames include `select_range`, is the missing evidence (a test addition for the lead to order; none made here).
