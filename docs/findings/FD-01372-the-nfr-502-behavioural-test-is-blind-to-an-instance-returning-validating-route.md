---
id: FD-1372
family: finding
title: The NFR-502 behavioural test is blind to an instance-returning validating route
status: closed
created: 2026-10-03
owner: auditor
tree: 98d7191b62e73dcfba4bb294c743ee97cf6f6f59
corrected_by: []
relates: [WK-1178, NFR-502, RL-883, FD-1335, SL-1367, LG-1637]
---

# FD-1372 — The NFR-502 behavioural test is blind to an instance-returning validating route

**Filed** by auditor-pl9788b, found while re-auditing PL-1364, draft PR #1036, at the maintainer's request
("does the existing test infer no outbound validation from a 500 side effect?"). The `tree:` is the tree of
`origin/main` `19155b50`.

## Finding

**Severity: LOW; owner WK-1178.** Ruled by the maintainer (`~/gi-pricing-plan.local/channel/to-lead.md`, "2026-10-01 09:22:11 BST — PL 9788 re-audit (837ce184) accepted; FD 9775 = LOW (WK-1178), with conditions; F-A and F-B adopted"; first proposed LOW–MEDIUM by the auditor). The shipped route makes 0 outbound validations (the spy's raw count in the table below), so nothing in production is wrong: the defect is a blind test and a false docstring. `03` NFR-502 says a scoring route validates inbound and never outbound
(as amended by `RL-883`, the ruling whose acceptance test this is; RL-883 is frozen and this finding does not propose amending it). Its only behavioural test, `backend/tests/test_score.py::test_the_result_is_returned_without_outbound_validation`,
checks that rule by a **side effect**: a malformed body comes back verbatim with a 200. A route that **does** validate
outbound, and is handed an instance of its declared class, also gives a 200 with the same bytes, so the test passes on
a violating route. The rule holds today because `/score` returns a raw `Response`. The test would not notice if that changed in the way shown below. `/score/compare` has no such test at all.

## Evidence

**The test, at `origin/main` `19155b50`.** `backend/tests/test_score.py:341` carries `@pytest.mark.req("NFR-502")`.
`:342` defines the test. It builds `ScoringResult.model_construct(…)` holding values that break the declared types, stubs
`score_one`, posts to `/score`, and asserts only:

- `:375` `assert response.status_code == 200, response.text`
- `:377` `assert body["bundle_hash"] == 12345`
- `:378` `assert body["premium_ladder"] == "not-a-list"`
- `:379` `assert body["timing_ms"] == {"total": "not-a-float"}`

Its docstring (`:343-354`) says a route "carrying a Pydantic return annotation or a `response_model=` answers 500 here".
That is **false** for an instance return (table below): it holds for dict returns only. The test treats a 500 as the only
symptom of outbound validation.

**The reproduction** (scratch app, not committed). A bare `FastAPI()` with the repository's
`app.errors.install_error_handlers(app)`, at fastapi 0.141.1 (the repo `.venv`, 2026-10-01), driven by
`TestClient(app, raise_server_exceptions=False)` as `backend/tests/conftest.py` does. `ModelField.validate` (module
`fastapi._compat.v2`) is wrapped to record its keyword-only `loc`. Each route returns the same malformed
`ScoringResult.model_construct(…)` as the test, or its `.model_dump()`:

| Route form | Status | Calls with `loc[:1] == ("response",)` | The test's four asserts |
|---|---|---|---|
| raw `Response`, `responses={200: {"model": ScoringResult}}` (today's `/score`) | 200 | 0 | pass |
| `-> ScoringResult`, returning the **instance** | **200** | **1** | **pass** |
| `response_model=ScoringResult`, returning the **instance** | **200** | **1** | **pass** |
| `-> ScoringResult`, returning `model_dump()` | 500 | 1 | red |
| `response_model=ScoringResult`, returning `model_dump()` | 500 | 1 | red |
| `response_model=ScoringResult` over a raw `Response` | 200 | 0 | pass (FastAPI passes a `Response` through) |

For the two instance rows, the response body had `bundle_hash == 12345`, `premium_ladder == "not-a-list"` and
`timing_ms == {"total": "not-a-float"}`, which are the test's `:377-379` asserts. The cause: FastAPI's
`serialize_response` calls `field.validate(…, loc=("response",))`, and pydantic accepts an instance of the declared
class without revalidating it (`revalidate_instances='never'`). Validation ran, and nothing failed. `/score/compare`
behaves the same with `ScoreComparison`.

## Disposition

**fix before close with an owner: WK-1178.** Severity LOW (the maintainer's ruling, above). **Discharged at PL-1364's
merge**, which does two things:
- Acceptance 8b adds an `outbound_validation_spy` that counts calls to `fastapi._compat.v2.ModelField.validate` whose
  `loc` starts with `("response",)`, asserts 0 on `/score` and on `/score/compare`, and proves the spy is not blind with
  a planted `response_model=` control route (count >= 1). Its red-first steps include the instance form, where the spy
  counts 1 while the 500-style test stays green. **`/score/compare` is covered too**: it has no such test today, and
  PL-1364 gives it both its 500 test (Acceptance 8) and its spy test (8b).
- The slice **corrects the docstring** at `test_score.py:341-356`: the 500 holds for dict returns only, the existing test
  is the dict-form check, and the spy test is the one that catches every form. The existing test stays.

The finding closes when PL-1364's slice merges with both spy tests on `main` and the docstring corrected.
`RL-883` is named, not amended. The severity is the maintainer's; the lead gives the verdict on disposition.

***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor (aud-fdclose), on the lead's brief under to-lead "2026-11-05 09:40:57 GMT" item 8 (2), the FD-1842 form. Delivered remedy (PL-1364 Acceptance 8b: a spy counting outbound response validation on `/score` and `/score/compare`, each proved not blind by a planted `response_model=` control, and the docstring corrected): SL-1367 (LG-1637, PL-1364), PR #1282, squash commit 13a02bbab842e0d0717d112003da9ff24c7b1f30, merged 2026-10-11T19:52:01Z. `backend/tests/outbound_validation_spy.py` (`install_outbound_validation_spy`); `test_score.py` (:1835) asserts 0 calls on `/score` and at least 1 on the `/__nfr502_control` route declaring `response_model=ScoringResult`; `test_score_compare.py:505` `test_no_outbound_validation_runs_on_compare` does the same with `ScoreComparison`; the docstring at `test_score.py:365-372` now says the 500 holds for dict returns only and names FD-1372. The control route returns a dict; the essay's "instance form" is a red-first proof step of the slice, not a standing test, and was not re-checked.
