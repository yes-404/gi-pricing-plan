---
id: FD-8379
family: finding
title: the report route returns the stored ValidationReport, whose overall and counts are plain properties, so the response omits the outcome 01 §4.6 states
status: active                  # the closing act (FD-8379-closing-act.md) sets closed in the same PR
created: 2026-11-05             # original date; working id 8379, to be minted in merge order
owner: auditor
tree: 850cf225797c8a63065130dc9012a2ef31b5ef55   # RL 8375's read tree (bdad1322); the red lines below ran at dd729ed0
corrected_by: []
relates: [WK-1178, SL-8381, LG-8382, PL-8380, FD-1381, FR-42, FR-49, FR-451, NFR-469]
---

# FD-8379 — the report route returns the stored `ValidationReport`, whose `overall` and `counts` are plain properties, so the response omits the outcome `01` §4.6 states

*(Filed as a working id under RL 8375 row 5, to-lead "2026-11-05 16:31:45 GMT" (1). MEDIUM and owner WK-1178 are the maintainer's, same entry.)*

## Finding

`01` §4.6 prints a report with `overall` and `counts`, and the authored contract
`docs/contracts/schemas/validation-report.schema.json` requires both (`required`, former `:7-8`).
`ValidationReport` (`packages/model-schema/src/model_schema/validation.py`) holds neither as a field: both are
plain `@property` members, so `model_dump` omits them, and `GET /api/v1/validation-reports/{report_id}`
(`backend/src/app/api/validation.py`, `get_report`) returned `ValidationReport`. The report response never carried
the outcome the spec states. The authored contract had described the response all along, which is the defect.
`validation-report` was also absent from the contract guard's parametrize list, so no test compared the two
(`backend/tests/test_contracts.py`); that is why it stayed green.

The stored body is the artifact (`backend/src/app/db/models.py`, `ValidationReportRow`). A bare `@computed_field`
was refused by the maintainer: it would write `overall` into the stored body. The fix is therefore response-side.

## Evidence

Red at the base, `dd729ed043225c97a448415d09d7c7c85cc40dff` plus the R1 tests uncommitted (LG 8382, "Red and green lines"):

- T1: `AssertionError: the contract declares fields the model lacks: ['counts', 'overall']` (`test_contracts.py:786`).
- T2: `AssertionError: assert {'counts', 'overall'} <= {'dataset_ver... 'started_at'}` (`test_contracts.py:256`).
- T4 at `f985190a`, with the DB window of 23:05:41Z to 23:08:27Z: `KeyError: 'overall'` (`test_api_acknowledge.py:91`),
  `FAILED test_an_actuary_acknowledges_a_warning_through_the_route`.

Fix at `ce3676c7`: `ValidationReportView` and `ReportCounts` in `model_schema/validation.py` (one shape; the view checks
`overall` and `counts` against `results` so neither is assigned); `load_report_view` returns `ValidationReportView.of(report)`;
the contract generator's `validation-report` row moves to the view. Constraint proofs: T3 (stored bytes equal the pre-fix
fixture) and T5 (the row's `body` has neither key after `store_report` and `load_report_view`); mutation M1, a bare
`@computed_field`, reddens both and names `counts` and `overall` (`E       assert ['counts', 'overall'] == []`; `extra_forbidden`).
Mutation M2, the generator row back to `ValidationReport`, reddens T1 on the repaired tree.

## Disposition

MEDIUM, owner WK-1178. `counts` and `overall` were absent from one route's response only; the row holds `overall`
(`dataset_versions.py:188` returns it) and no frontend view reads either key on a report, so no consumer was misled and no
price depended on it. Fixed before the freeze by SL 8381 (the closing act sets this essay `closed`).
