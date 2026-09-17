---
id: CR-835
family: closure
kind: work
title: Work-item record — W9-1 (the RatingAlgorithm contract)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-28
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/W9-1/README.md
---

# Work-item record — W9-1 (the RatingAlgorithm contract)

Audited 2026-08-27 against origin/main `550b32d` (#290), PR #291 head `8899d1d`.

## Scope

Derived from `docs/plans/PL-00818-wk-669-implementation-plan-rating-algorithm-contract-validation-bundle-compilation.md` slice W9-1 first, then
evidenced. W9-1 defines the `RatingAlgorithm` shape in model-schema: T1 the §4.1 shape
(seven step types, input contract, outputs, sub-graphs, money types), T2 the graph
invariants, T3 the structural diff. The slice gate: the shape parses, its invariants
hold, and the diff names changes.

## Checklist

The `close-workstream` checklist version this close ran against: the 2026-08-24 skill
text (scope-first, negative tests for invariants, marker on each test).

## Evidence

| Task | Evidence | Verdict |
|---|---|---|
| T1 — the shape (03 §4.1) | `packages/model-schema/src/model_schema/rating.py` — `RatingAlgorithm` (slug, version, input_contract, outputs, steps, sub_graphs); seven step types as a discriminated union (`input`/`lookup`/`table`/`expression`/`model_call`/`constraint`/`output`); `InputContractField` (FR-213), `AlgorithmOutput` (FR-214), `SubGraphRef` (FR-217), `RoundSpec` (FR-226), `_reject_float_type` (FR-227). **Spec-reconciliation vs `03` §4.1: PASS** — the JSON example's fields and step keys match the shape exactly; no drift | delivered |
| T2 — the invariants | Unique `step_id` (FR-215); every `consumes` resolves to a producer; re-production only as a chain; acyclic via Kahn (FR-212); every declared output has an `output` step (FR-214); no orphan (FR-212); `model_call` exactly one of `model_ref`/`peril_structure_ref` (FR-222). Negative tests: cycle, undefined reference, missing output step, orphan — all refused. Focused run: 10/10 passed | delivered |
| T3 — the structural diff | `diff_algorithms` names added/removed/changed steps field-by-field and re-pointed tables (FR-219); tests cover both the change set and the repoint | delivered |
| Slice gate | Shape parses, invariants hold, diff names changes — met | delivered |

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W9-1-1 | The W9-1 tests carried **no `@pytest.mark.req` markers**, so the requirements W9-1 implements were not evidenced by `req-coverage.py` | resolved 2026-08-27 (781b440) — markers added, one per test, mapped to FR-212/213/214/215/217/219/220/221/222/225/226/227; `req-coverage.py` reports all twelve evidenced | closed |

## Sign-off

Owner: the maintainer. Auditor: 2026-08-27. The slice work is verified (shape,
invariants, diff all pass); F-W9-1-1 (the marker gap) must be fixed before the close.
