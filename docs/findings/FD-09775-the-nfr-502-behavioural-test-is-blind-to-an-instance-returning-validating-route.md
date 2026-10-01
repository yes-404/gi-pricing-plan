---
id: FD-9775
family: finding
title: The NFR-502 behavioural test is blind to an instance-returning validating route
status: active
created: 2026-10-01
owner: auditor
tree: 98d7191b62e73dcfba4bb294c743ee97cf6f6f59
corrected_by: []
relates: [WK-1178, NFR-502, RL-883, FD-1335, PL-9788]
---

# FD-9775 — The NFR-502 behavioural test is blind to an instance-returning validating route

**Filed** by auditor-pl9788b, found while re-auditing PL 9788 (working id), draft PR #1036, at the maintainer's request
("does the existing test infer no outbound validation from a 500 side effect?"). The `tree:` is the tree of
`origin/main` `19155b50`.

## Finding

**Severity: LOW–MEDIUM; owner WK-1178.** `03` NFR-502 says a scoring route validates inbound and never outbound
(as amended by `RL-883`). Its only behavioural test, `backend/tests/test_score.py::test_the_result_is_returned_without_outbound_validation`,
checks that rule by a **side effect**: a malformed body comes back verbatim with a 200. A route that **does** validate
outbound, and is handed an instance of its declared class, also gives a 200 with the same bytes, so the test passes on
a violating route. It is a contract-protection gap, not a mispricing: today's `/score` returns a raw `Response`, so the
rule holds. The test would not notice if that changed in the way shown below. `/score/compare` has no such test at all.

## Evidence

**The test, at `origin/main` `19155b50`.** `backend/tests/test_score.py:341` carries `@pytest.mark.req("NFR-502")`.
`:342` defines the test. It builds `ScoringResult.model_construct(…)` holding values that break the declared types, stubs
`score_one`, posts to `/score`, and asserts only:

- `:375` `assert response.status_code == 200, response.text`
- `:377` `assert body["bundle_hash"] == 12345`
- `:378` `assert body["premium_ladder"] == "not-a-list"`
- `:379` `assert body["timing_ms"] == {"total": "not-a-float"}`

Its docstring (`:343-354`) says a route "carrying a Pydantic return annotation or a `response_model=` answers 500 here".
So it treats a 500 as the only symptom of outbound validation.

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

**fix before close with an owner: WK-1178.** Covered by PL 9788 (working id) Acceptance 8b: an
`outbound_validation_spy` counts calls to `fastapi._compat.v2.ModelField.validate` whose `loc` starts with
`("response",)`, asserts 0 on `/score` and on `/score/compare`, and proves the spy is not blind with a planted
`response_model=` control route (count ≥ 1). Its red-first steps include the instance form, where the spy counts 1 while
the 500-style test stays green. The existing test stays as the dict-form check. `/score/compare` gets both its 500 test
(Acceptance 8) and its spy test (8b), because it has none today. The finding closes when PL 9788's slice merges and
both spy tests are on `main`. The severity is the auditor's proposal; the lead gives the verdict.
