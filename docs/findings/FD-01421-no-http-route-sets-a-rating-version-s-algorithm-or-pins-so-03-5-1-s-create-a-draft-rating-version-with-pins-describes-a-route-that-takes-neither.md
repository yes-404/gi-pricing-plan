---
id: FD-1421
family: finding
title: No HTTP route sets a Rating Version's algorithm or pins, so 03 §5.1's "Create a draft Rating Version with pins" describes a route that takes neither
status: active
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-673, WK-1178, FR-237, FR-440, FD-1297]
---

# FD-1421 — `POST /rating-versions` cannot declare the algorithm or any pin

**Filed** by the auditor at the lead's request of 2026-10-05, from planner-demo's exit-demo draft
(step C1). `tree:` is `origin/main` = `caa4e411a9c07a389cf47092a923c7761b2b92dc`, the tree every
statement below was read on. The id is a working id until the lead mints it. **This is a
spec-versus-code disagreement (`CLAUDE.md` §0). The essay states both sides and does not decide which is wrong.**

## Finding

The spec says the route creates a Rating Version *with pins*. The code's request model accepts no
algorithm and no pin, and no other route writes either. Every Rating Version that compiles on main
got its `algorithm_ref` and `pins` from a service call in the demo seed or from a test or bench insert.

## Both sides, verbatim

**Spec.**
- `docs/specs/03-rating-engine.md` §5.1 (line 908): `| POST | /api/v1/rating-versions | Create a draft Rating Version with pins (FR-237) |`
- FR-237 (line 134, no dated amendment): "A **Rating Version** pins: one Rating Algorithm version, an exact Rate Table Version per referenced table, an exact Model/Peril Structure version per `model_call`, an exact Reference Table Version per `lookup`, and the input contract. Nothing is unpinned."
- `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` step C1: "`POST /rating-versions` — declares the algorithm version and every pin: rate tables, peril structure, reference tables."
- **The spec also says the opposite, in the same file.** §4.3's "Scoped 2026-08-27, W7-3 — OD1" note (line ~430): "Phase 1b builds the **minimal subset** … `slug`, `version`, `status`, `workspace_id`, `dataset_version_id`, a single pinned `model:{slug}@{version}` reference … Compile, score, rate tables, the `pins`/`evidence`/`bundle` blocks, `model_reference_mode`, and deployment stay Phase 2 (FR-440)." `07-platform.md` FR-440 is the same scope. Nothing dated says when, or by which route, Phase 2 widens the create.

**Code.**
- `backend/src/app/api/models.py:271-276`: `class RatingVersionCreate(BaseModel)`, `model_config = ConfigDict(frozen=True, extra="forbid")`, fields `slug: str`, `dataset_version_id: UUID`, `model_ref: ArtifactRef`.
- The handler (`api/models.py:1161-1186`, `create_rating_version`) passes only those three to `rating_versions_service.create_rating_version` (`platform/rating_versions.py:230-275`), whose signature takes only `slug`, `dataset_version_id`, `model_ref`. The `RatingVersionRow` it builds sets neither `algorithm_ref` nor `pins`. The handler docstring says "Create a draft rating version with pins to a model (FR-237)", and the "pin" is the one `model_ref`.
- By `extra="forbid"`, a body carrying `algorithm_ref` or `pins` is refused as 422. This was read from the model, not run.

## Evidence

### Every pin on a Rating Version, and what can set it over HTTP

`model_schema.RatingVersion` (`packages/model-schema/src/model_schema/rating.py:138-170`) and `Pins` (`:65-78`):

| Field | Set by an HTTP route? |
|---|---|
| `model_ref` (the single Phase 1b model) | **Yes**: `POST /rating-versions` |
| `dataset_version_id` | **Yes**: same route |
| `algorithm_ref` | **No** |
| `pins.rate_tables` | **No** |
| `pins.models` | **No** |
| `pins.reference_tables` | **No** |
| `pins.custom_objectives` | **No** |
| `model_reference_mode`, `effective_from`, `effective_to` | **No** (column defaults only) |

`pins.models` is a different field from the top-level `model_ref`; FR-237's per-`model_call` model pin is the former.

### Every writer of `algorithm_ref` / `pins`

The Rating Version routes in `api/models.py` are: `GET /rating-versions` (`:1113`), `GET .../{id}` (`:1139`), `POST /rating-versions` (`:1161`), `POST .../{id}/submit`, `.../compile`, `.../regression-runs` and its two `GET` reads. None is a `PATCH` or `PUT`; none reads a pin from a body. The submit and compile handlers only read the pins.

Predicate, run at the tree above: `grep -rn "algorithm_ref\s*=\|\.pins\s*=\|\"pins\":" --include=*.py .` excluding `tests/`, `test_*`, `.venv` and worktrees. The writers outside tests are:
- `examples/fremtpl2/model.py:396-397`: `row.algorithm_ref = f"rating_algorithm:{DEMO_ALGORITHM_SLUG}@1"`, `row.pins = dict(_EMPTY_PINS)`, set on the row after the service creates it. **The pins are empty.**
- `scripts/bench-compiled-for.py:105`, `scripts/bench-score-batch.py:105`, `scripts/bench-rating.py:306,631`: benchmark inserts.
- Tests insert the row directly: `backend/tests/test_rating_version_compile.py::_insert_version` (`:86-110`) passes `algorithm_ref` and `pins` to the `RatingVersionRow` constructor. Other tests that name `algorithm_ref`: `test_rating_pin_membership_api.py`, `test_rating_versions.py`, `test_score.py`, `test_scoring_handlers.py`, `test_regression_runs.py`.
- Read-only uses: `platform/rating_versions.py:110-113` (`to_schema`), `:591-722` (golden-quote and regression gates), `worker/rating_handlers.py:153-158`.

So the demo seed's real pin set is empty: no seeded Rating Version pins a rate table, reference table or model, and the seed writes to the ORM row rather than through a route.

### Was it already tracked?

Searched at the tree above, `origin/main`:
- `grep -n -i "pin" docs/findings/register.md` filtered by `rating`/`FR-237`/`http`/`route`: the hits on FR-237 are `FD-1297` (compile does not check step refs against the pin set; fixed, SL-1300) and `FD 9995`. Neither is about *how pins get declared*.
- `gh pr list --state open --search pin`: #1061 (RL 9758, FR-223 check point), #980 (FD 9995), #975, #977, #976, #1113, #1121. None covers it. #1061 concerns when FR-223 is checked on "version pin writes"; it presumes a write path and does not add one (title read, not the diff; stated as a pointer, not a verdict).
- Roadmap: `docs/roadmap.md` has no row, slice or plan for a route that declares pins. WK-673's slices cover dislocation, not rating-version creation.

**Relation to FD 9995 (#980, open, unminted).** FD 9995 is narrower and downstream: given a `peril_structure` pin, the compile resolver has no branch for it. It assumes the pin is already on the row. This finding is upstream: no route can put any pin on the row, a `peril_structure` pin included. Fixing FD 9995 does not make a peril pin reachable over HTTP.

### Effect on WF-699 and P2's G2

`docs/roadmap.md:566` G2: "The exit demo is `WF-699` end to end on the freMTPL2 seed, with its deploy step: through approved models, a Rating Version compiled with pins, golden quotes, a regression run, a dislocation run …, from one command to a served page, in Phase 1b's form." WF-699 step C1 is the `POST /rating-versions` that "declares the algorithm version and every pin". A scripted HTTP journey stops at C1: it cannot create a version with an algorithm or any pin, so C2 (`POST .../compile`) on that version fails `RATING_VERSION_UNPINNED` (03 §5.1, line ~967: no `algorithm_ref`, no `pins`). Any demo that reaches C2 must create the row outside HTTP, as the seed does. Whether that satisfies "in Phase 1b's form" is a reading of G2 and not this finding's.

## Disposition

Proposal only; the lead gives the verdict and the decision-maker rules which side is wrong.

**Ruled: the code is behind (RL 9695, working id; the maintainer's (by delegation) 2026-10-05 13:12:56 BST, decision 15, option (a)).** `POST /rating-versions` takes `algorithm_ref` and `pins`, checked at compile, in a WK-1178 slice. The two sides above stay as filed; the ruling picked the spec's.

**Severity: HIGH (the maintainer's (by delegation) early signal of 2026-10-05 13:10:43 BST, confirmed at 13:12:56 BST; final at the mint).** Reason: G2 (`docs/roadmap.md:566`) requires "a Rating Version compiled with pins" over HTTP from one command, and no route can create one, so the exit criterion cannot be met as the code stands. The maintainer's (by delegation) condition for MEDIUM (a supported HTTP path that already writes pins) does not hold: `git grep -nE '\.(algorithm_ref|pins)\s*=[^=]' caa4e411a9c07a389cf47092a923c7761b2b92dc -- backend/src` returns 0 lines. Nothing mis-prices; the severity is the exit-demo block.

**Owner: WK-1178** (RL 9695, decision 15; the proposed alternative WK-673 is not taken). **Deadline: before the P2 exit demo.**
