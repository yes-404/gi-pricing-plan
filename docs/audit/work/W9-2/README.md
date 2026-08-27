# Work-item record — W9-2 (save-time validation + boundary guards)

Audited 2026-08-27 against origin/main `1b723f5` (#291), PR #292 head `252db7e`.

## Scope

Derived from `docs/plans/2026-08-27-w9-rating-contract.md` slice W9-2 first, then
evidenced. W9-2 validates a `RatingAlgorithm` at save time and enforces the four W8-
confirmed boundary guards: T1 `validate_algorithm` (03 §5.2), T2 the guards
(FR-RATE-56/57/58/59), T3 the API. The slice gate: an invalid graph is refused at save
time, and the four boundary guards fail on deliberately broken input.

## Checklist

The `close-workstream` checklist version this close ran against: the 2026-08-24 skill
text (scope-first, negative tests for the guards, marker on each test).

## Evidence

| Task | Evidence | Verdict |
|---|---|---|
| T1 — `validate_algorithm` (03 §5.2) | `packages/pricing-core/src/pricing_core/rating/compile.py` — result-type compatibility (FR-RATE-13), deterministic evaluation (FR-RATE-5/30), the four guards. **Spec-reconciliation vs `03` §5.2: PASS** — the signature `validate_algorithm(algo) -> list[ValidationIssue]` matches exactly | delivered |
| T2 — the four guards, each proven to fail on broken input | FR-RATE-56 `assert_integer_minor_round_trip` (self-check); FR-RATE-57 unguarded division refused + guarded accepted; FR-RATE-58 scale-cap-28 overflow refused; FR-RATE-59 foreign function refused (compiled against the engine). Pricing-core focused run: 8/8 passed | delivered |
| T3 — the API | `POST /api/v1/rating-algorithms` validates-before-persist: the platform service (`backend/src/app/platform/rating_algorithms.py`) parses (mapping a cyclic graph to `RATING_GRAPH_CYCLIC`, an undefined value to `RATING_GRAPH_UNRESOLVED_REF`), runs `validate_algorithm`, refuses with the first issue's code, then writes the row. `GET /rating-algorithms/{slug}@{version}/diff` returns the structural diff. `RATING_ERROR_CODES` registered in `backend/src/app/errors.py:275` and declared in `03` §5.1. Backend focused run: 4/4 passed | delivered |
| Slice gate | An invalid graph is refused at save time (`RATING_GRAPH_CYCLIC`); the four guards fail on broken input — met | delivered |

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W9-2-1 | The zen-engine → pricing-core dependency was **not recorded in `docs/skills-map.md`** when the PR first landed. `CLAUDE.md` §10: "skills-map.md updated in the same PR whenever a tech dependency changes" | resolved 2026-08-27 (bdad5d1) — the ZEN row's "Used in" cell now names pricing-core (`pricing_core.rating.compile` imports the engine for FR-RATE-59); audit-docs exit 0 | closed |

## Sign-off

Owner: the maintainer. Auditor: 2026-08-27. The slice work is verified (validator, the
four guards, the API, the markers all pass); F-W9-2-1 (the skills-map dependency record)
must be fixed before the close.
