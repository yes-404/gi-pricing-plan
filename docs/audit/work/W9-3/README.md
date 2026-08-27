# Work-item record — W9-3 (bundle compilation)

Audited 2026-08-27 against origin/main `c428839` (#292), PR #293 head `548de6a`.

## Scope

Derived from `docs/plans/2026-08-27-w9-rating-contract.md` slice W9-3 first, then
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
| T1 — the widened RatingVersion (03 §4.3) | `model-schema/rating.py` — `RatingVersion` gains `algorithm_ref`, `pins` (FR-RATE-22), `model_reference_mode` (FR-RATE-60), `effective_from/to` (FR-RATE-26), `bundle` (FR-RATE-24), `change_summary` (FR-RATE-27), `evidence`, `approval_request_id`, all nullable so the Phase 1b subset keeps parsing; `check_model_reference_mode` (FR-RATE-60). **Spec-reconciliation vs `03` §4.3: PASS** — the fields match | delivered |
| T2 — the lifecycle (FR-RATE-23) | `RatingVersionStatus` gains `live`/`retired`, declared but unreachable (transitions build through `approved` only; `live` is a Deployment property, W14's) | delivered |
| T3 — the compiler (FR-RATE-24/25) | `compile_bundle` / `to_jdm` / `bundle_hash` in `pricing-core/rating/compile.py`. `ArtifactResolver` protocol keeps pricing-core standalone. **Spec-reconciliation vs `03` §5.2: PASS for `compile_bundle` and `to_jdm`** (signatures match); `bundle_hash` differs — see F-W9-3-2. Slice-gate tests pass: a pinned version compiles to a self-contained Bundle, the content hash is reproducible, an unpinned version is refused, an unapproved pin is refused, a mode mismatch is refused (all named) | delivered with a finding |
| T4 — the compile endpoint | `rating_versions` §4.3 columns + migration; `POST /rating-versions/{id}/compile` (RATING_COMPILE); `RATING_VERSION_UNPINNED` added to the §5.1 error codes; backend test 2 passed | delivered |

Focused runs: pricing-core + model-schema 12 passed, backend 2 passed. audit-docs exit 0.
Collect-only 2083 reconciles the "2080 passed" claim.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W9-3-1 | FR-RATE-27 (change summary) carried **no `@pytest.mark.req` marker** — unevidenced by `req-coverage.py` | resolved 2026-08-27 (e30a403) — marker added to the change-summary test; `req-coverage.py` reports FR-RATE-27 evidenced | closed |
| F-W9-3-2 | `bundle_hash`'s signature differed from the `03` §5.2 interface (code `bundle_hash(graph, pins)` vs spec `bundle_hash(bundle)`) | resolved 2026-08-27 (a548517) — the decision-maker ruled the spec wrong (a Bundle carries `compiled_at`; hashing it would be unreproducible); `03` §5.2 amended to `bundle_hash(graph, pins: Pins)` with a dated note; the code's signature now matches exactly | closed |

## Sign-off

Owner: the maintainer. Auditor: 2026-08-27. The slice work is verified (compiler, gate,
endpoint all pass); F-W9-3-1 (the FR-RATE-27 marker) and F-W9-3-2 (the `bundle_hash`
signature drift) must be fixed before the close.
