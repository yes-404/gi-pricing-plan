---
id: CR-837
family: closure
kind: work
title: Work-item record — W9-3 (bundle compilation)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-28
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/W9-3/README.md
---

# Work-item record — W9-3 (bundle compilation)

Audited 2026-08-27 against origin/main `c428839` (#292), PR #293 head `548de6a`.

## Scope

Derived from `docs/plans/PL-00818-wk-669-implementation-plan-rating-algorithm-contract-validation-bundle-compilation.md` slice W9-3 first, then
evidenced. W9-3 widens the `RatingVersion` to 03 §4.3, adds the lifecycle, the compiler
(`compile_bundle`/`to_jdm`/`bundle_hash`), and the compile endpoint. The slice gate: a
pinned version compiles to a self-contained Bundle with a reproducible hash, and every
validation failure is named.

## Checklist

The `close-workstream` checklist version this close ran against: the 2026-08-24 skill
text (scope-first, negative tests for the invariants, marker on each test).

## Evidence

| Task | Evidence | Verdict |
|---|---|---|
| T1 — the widened RatingVersion (03 §4.3) | `model-schema/rating.py` — `RatingVersion` gains `algorithm_ref`, `pins` (FR-237), `model_reference_mode` (FR-223), `effective_from/to` (FR-241), `bundle` (FR-239), `change_summary` (FR-242), `evidence`, `approval_request_id`, all nullable so the Phase 1b subset keeps parsing; `check_model_reference_mode` (FR-223). **Spec-reconciliation vs `03` §4.3: PASS** — the fields match | delivered |
| T2 — the lifecycle (FR-238) | `RatingVersionStatus` gains `live`/`retired`, declared but unreachable (transitions build through `approved` only; `live` is a Deployment property, WK-674's) | delivered |
| T3 — the compiler (FR-239/240) | `compile_bundle` / `to_jdm` / `bundle_hash` in `pricing-core/rating/compile.py`. `ArtifactResolver` protocol keeps pricing-core standalone. **Spec-reconciliation vs `03` §5.2: PASS for `compile_bundle` and `to_jdm`** (signatures match); `bundle_hash` differs — see F-W9-3-2. Slice-gate tests pass: a pinned version compiles to a self-contained Bundle, the content hash is reproducible, an unpinned version is refused, an unapproved pin is refused, a mode mismatch is refused (all named) | delivered with a finding |
| T4 — the compile endpoint | `rating_versions` §4.3 columns + migration; `POST /rating-versions/{id}/compile` (RATING_COMPILE); `RATING_VERSION_UNPINNED` added to the §5.1 error codes; backend test 2 passed | delivered |

Focused runs: pricing-core + model-schema 12 passed, backend 2 passed. audit-docs exit 0.
Collect-only 2083 reconciles the "2080 passed" claim.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W9-3-1 | FR-242 (change summary) carried **no `@pytest.mark.req` marker** — unevidenced by `req-coverage.py` | resolved 2026-08-27 (e30a403) — marker added to the change-summary test; `req-coverage.py` reports FR-242 evidenced | closed |
| F-W9-3-2 | `bundle_hash`'s signature differed from the `03` §5.2 interface (code `bundle_hash(graph, pins)` vs spec `bundle_hash(bundle)`) | resolved 2026-08-27 (a548517) — the decision-maker ruled the spec wrong (a Bundle carries `compiled_at`; hashing it would be unreproducible); `03` §5.2 amended to `bundle_hash(graph, pins: Pins)` with a dated note; the code's signature now matches exactly | closed |

## Sign-off

Owner: the maintainer. Auditor: 2026-08-27. The slice work is verified (compiler, gate,
endpoint all pass); F-W9-3-1 (the FR-242 marker) and F-W9-3-2 (the `bundle_hash`
signature drift) must be fixed before the close.
