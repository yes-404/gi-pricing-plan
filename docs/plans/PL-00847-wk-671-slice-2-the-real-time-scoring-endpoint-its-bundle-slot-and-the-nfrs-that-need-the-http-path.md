---
id: PL-847
family: plan
kind: leaf
title: WK-671 Slice 2 — the real-time scoring endpoint, its bundle slot, and the NFRs that need the HTTP path
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-29
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-29-w11-2-realtime-scoring-endpoint.md
---

# WK-671 Slice 2 — the real-time scoring endpoint, its bundle slot, and the NFRs that need the HTTP path

> **For agentic workers:** REQUIRED SUB-SKILL: use `subagent-driven-development`
> (recommended) or `executing-plans` to implement this plan task-by-task, plus
> `test-driven-development` and `git-hygiene` — the three skills
> [`.claude/roles/executor.md`](../../.claude/roles/executor.md) makes mandatory for this
> role. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put `score_one` behind `POST /api/v1/score` — with the per-worker bundle slot that
keeps a hydrated `CompiledBundle` off the request path, the typed refusal that replaces the
default-live resolution WK-674 owns, and the three NFRs that can only be measured once the HTTP
path exists.

**Architecture:** Four tasks, lettered rather than numbered — see *Task identifiers* below,
because the frozen map's `2.2` was deleted by a ruling and reusing the number would point two
documents at different work. **2A** adds the error code and the bundle slot, the first
in-process cache in this backend. **2B** is the route. **2C** is a single test that makes
FR-257's already-enforced limb visible to `req-coverage.py`. **2D** measures. 2A → 2B is a
hard dependency; 2C is independent of all three; 2D needs 2B and a scheduling constraint.

**Tech Stack:** FastAPI async routes; `pricing-core`'s shipped
`score_one`/`build_scoring_result`/`load_bundle`; the content-addressed blob store
(`backend/src/app/platform/blobs.py`); `Permission.SCORE_EXECUTE` on a Service Account;
typed settings in `backend/src/app/config.py`. **No new dependency** — RL-883 is explicit
that `orjson` is not added.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — §3.7 (FR-250,
35), §3.8 (FR-257), §5.1 (the `/score` row), §5.2 (`score_one`'s signature), §9
(NFR-RATE-1, 9, 11, 13). **Contract:**
[`../contracts/schemas/scoring.schema.json`](../contracts/schemas/scoring.schema.json), the
hand-authored tier — read
[`.claude/skills/contract-guard`](../../.claude/skills/contract-guard/SKILL.md) before citing
it, and note RL-878's obligation 4 means the generated side now exists too.

**Slice source:** [`PL-00854-wk-671-scoring-sequenced-slice-plan.md`](PL-00854-wk-671-scoring-sequenced-slice-plan.md), Slice 2. **That
file is frozen and is not edited by this one**; where evidence contradicts it, the
contradiction is in *Corrections to the frozen map* below.

**Rulings this plan rests on, cited by number and not re-argued:**
[`../rulings/RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md`](../rulings/RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md) Rulings 14 and 15;
[`../rulings/RL-00887-finding-3-the-framing-was-wrong-and-the-class-is-bigger-and-mostly-benign.md`](../rulings/RL-00887-finding-3-the-framing-was-wrong-and-the-class-is-bigger-and-mostly-benign.md) Rulings 16, 17
and 18; [`../rulings/RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md`](../rulings/RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md) Rulings 4, 5,
8 and 10. **Register row [`../findings/register.md`](../findings/register.md) F32 withdraws one of
RL-882's two acceptance items** — see Correction C4.

**Process:** [`../process/delivery-process.md`](../process/delivery-process.md) §6 (the Slice
TDD cycle), §8 (no two slices at once; read-only fan-out permitted), §9 (register rows, read
below).

**Highest ids in use, re-derived at `d6505e9` by scanning
[`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) and
[`../open-questions.md`](../open-questions.md):** FR-243, NFR-501, OQ-620.
Next free: `FR-RATE-66`, `NFR-RATE-15`, `OQ-RATE-8`.

**This plan mints none of them.** It cites ids that already exist and proposes no new one. One
error code is registered (`NO_LIVE_RATING_VERSION`, RL-880) and error codes are a separate
namespace from `FR-`/`NFR-`/`OQ-` ids, so the marker above does not cover it.

## Task identifiers — why letters

The frozen map names Tasks 2.1, 2.2 and 2.3. **RL-880 deletes 2.2** (*"Slice 2 loses that
task"*) and **RL-881 reduces 2.3 to a single test with no production code.** Renumbering
the survivors would make `2.2` mean the endpoint here and default-live resolution there;
keeping the map's numbers would leave a hole and a task whose content no longer matches its
description. Letters avoid both. The mapping is stated once, here:

| This plan | Frozen map | What changed |
|---|---|---|
| **2A** — error code + bundle slot | *(not in the map)* | New work, from Rulings 14 and 16 |
| **2B** — `POST /api/v1/score` | Task 2.1 | Gains the 409 branch; loses the `prod` restrictions (RL-880 clause 3) |
| **2C** — FR-257's one test | Task 2.3 | Reduced from a gate mechanism to one test, no production code (RL-881) |
| **2D** — NFR measurement | folded into map Task 2.1 | Split out; it has a scheduling constraint the others do not |
| *(deleted)* | Task 2.2 | Default-live resolution is WK-674's (RL-880) |

---

## Acceptance standard for the slice as a whole

`delivery-process.md` §3 requires one that is explicit and testable. Slice 2 is accepted when
**all seven** hold, each by a command a fresh reviewer can run.

1. **A quote scores over HTTP.** `POST /api/v1/score` with a valid `QuoteContext` carrying
   `options.rating_version_ref` returns **200** and a `ScoringResult` body whose
   `premium_ladder` reconciles to its terminal rung.
2. **The platform refuses to guess.** The same request with `options.rating_version_ref: null`,
   or with `options` omitted, returns **409 `NO_LIVE_RATING_VERSION`** — RL-880's own
   acceptance test. **Any build that answers it 200 has overridden the ruling**, whichever
   version it chose.
3. **The response is not validated outbound.** A `ScoringResult` whose contents violate its own
   declared types is returned **verbatim**, not 500 — RL-883's acceptance test, which
   discriminates the raw-`Response` implementation from the annotated one. `orjson` appears in
   no `pyproject.toml` and in no `uv.lock`, and the route declares no `response_model=` and no
   Pydantic-model return annotation.
4. **The slot serves a degraded read.** With the rating-version load patched to raise, a second
   request for a ref this worker already served returns **200** from the slot; a first request
   for an unseen ref is refused. **Overridden if any build serves a ref it has never resolved
   while metadata storage is down** — RL-882 acceptance item 2.
5. **RBAC holds in three cases** (RL-884): a Service Account scoped to `uat` holding
   `score:execute` may call it; the same account without the permission is refused; a key for
   an environment outside the account's list is refused at authentication, before the route.
6. **Every per-quote error maps to its own typed HTTP problem, and a decline does not.** Each of
   the four codes `pricing-core` raises as a bare `ValueError` — `INPUT_CONTRACT_VIOLATION`,
   `RATE_TABLE_MISS`, `REFERENCE_LOOKUP_MISS`, `MODEL_CALL_FAILED` — comes back as an RFC 9457
   problem carrying **that** code, one test each fired by a deliberately malformed input; and a
   constraint decline comes back **200** with `outcome: "declined"` and a populated ladder
   (FR-256), never as an error.
7. **The full local gate passes, both halves**, and NFR-RATE-1, 11 and 13 are measured and
   written into a dated note under [`../research/`](../research/) — not left as terminal
   output.

**Not in this slice, and not a gap:** `score_batch` is Slice 3's; trace *sampling and
persistence* is Slice 4's (this slice returns a `Trace` inline when asked, it does not store
one); default-live resolution, the Deployment entity and NFR-497's 99.95 % availability
target are WK-674's.

## Global Constraints

Every task's requirements implicitly include this section.

- **Money is integer minor units or `Decimal`, never `float`** — [`../../CLAUDE.md`](../../CLAUDE.md)
  §7, FR-245/273. The route does no ladder arithmetic; it must also not re-serialise money
  through anything that would float it.
- **NFR-502 as amended (RL-883): validate inbound, never outbound.** `QuoteContext` **is**
  validated on the way in; `ScoringResult` is serialised directly with Pydantic v2's compiled
  encoder and returned in a raw `Response`. **`ORJSONResponse` is deprecated in the pinned
  FastAPI 0.141.1 and is not used**, and the framework's suggested replacement — a return-type
  annotation — is precisely what this requirement forbids.
- **`load_bundle` stays pure** (RL-876, and `.importlinter:16-34` enforces the structural
  half). The slot lives in `backend/`, never inside `pricing_core`.
- **A negative test for every invariant introduced**, marked `@pytest.mark.req("<id>")`.
- **Spec-vs-code disagreement is a finding, stopped and resolved, never silently matched**
  ([`../../CLAUDE.md`](../../CLAUDE.md) §0).
- **Worktree hygiene:** your own worktree, never `git checkout`/`git switch` outside it, `pwd`
  and `git branch --show-current` before every git write.
- **The gate, both halves, run locally before every push:**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
```

WK-675 owns the scoring UI, so there is no frontend work here — but the scoring shapes are in
`GENERATED_SHAPES` as of RL-878's obligation 4, so `generate:api` and `type-check` must
still pass.

---

## Verified facts at `d6505e9`

Everything here was read at that tree. A line number is only as good as its revision, and
**Task 1.5 is building in parallel and may touch
`packages/pricing-core/src/pricing_core/rating/`** — so symbols in that package are cited by
name with a re-derivation command, not by line.

### The shipped scoring surface

`packages/pricing-core/src/pricing_core/rating/score.py` exposes exactly two public functions;
everything else is underscore-private. Re-derive with
`grep -n "^def \|^async def " packages/pricing-core/src/pricing_core/rating/score.py`.

```python
async def score_one(
    bundle: CompiledBundle, ctx: QuoteContext, *, trace: bool = False
) -> ScoringResult

def build_scoring_result(
    bundle: CompiledBundle,
    ctx: QuoteContext,
    rating_version_ref: ArtifactRef,
    result: Mapping[str, Any],
    engine_trace: Mapping[str, Any] | None,
) -> ScoringResult
```

**`score_one` requires `ctx.options.rating_version_ref` and raises
`INPUT_CONTRACT_VIOLATION` when it is `None`** — its own docstring says a caller *"resolves the
version and fills in `ctx.options.rating_version_ref` before calling this."* **That is not the
409.** RL-880's refusal is the route's, raised before `score_one` is reached; letting
`score_one`'s own error surface instead would answer with the wrong code. Task 2B's test
discriminates them.

### The error boundary is Slice 2's, and it is a whole task's worth of work

**`pricing-core` cannot raise `PlatformError` — it cannot import it** (ADR-703, enforced by
`.importlinter`). So `score_one` raises a **code-named bare `ValueError`** through one helper:

```python
def _raise_named(code: str, message: str) -> NoReturn:
    raise ValueError(f"{code}: {message}")
```

Two shipped comments make the mapping Slice 2's in as many words. `backend/src/app/errors.py`
(`:305-311`): *"`score_one` (`pricing_core`) never raises these directly — it cannot import
`PlatformError` … it raises a code-named `ValueError`; **the mapping to `PlatformError` is
Slice 2's**."* And `model_schema/scoring.py` (`:65-68`) on `ScoringOutcome`'s third member:
*"`error` … is not produced by `score_one` today — a per-quote refusal is a raised, code-named
`ValueError` … **mapped to a `PlatformError` at the backend boundary in Slice 2**."*

The codes actually raised out of `score.py`/`runtime.py`, verified by reading every raise site
rather than the registration list: **`INPUT_CONTRACT_VIOLATION`**, **`RATE_TABLE_MISS`**,
**`REFERENCE_LOOKUP_MISS`**, and **`MODEL_CALL_FAILED`** (whose message prefix is set in
`runtime.py`'s `_model_call_failure`, not in `score.py`). A firing `on_violation="error"`
constraint raises a plain `NotImplementedError` and is **deliberately undesigned** — it is not
a platform code and must not be mapped to one.

**A decline is not an error.** FR-256: `outcome: "declined"` with a populated ladder is a
**200**, never an HTTP error. `build_scoring_result` sets
`outcome = "declined" if decline_reasons else "quoted"`; nothing in the shipped path ever
produces `"error"`.

### The shapes, from `packages/model-schema/src/model_schema/scoring.py`

All frozen, all `extra="forbid"`. Do not retype these; import them.

| Type | Fields |
|---|---|
| `QuoteContext` | `quote_id: str \| None`, `purpose: QuotePurpose`, `quoted_at: datetime`, `effective_date: date`, `inputs: dict[str, object]`, `options: QuoteContextOptions \| None` |
| `QuoteContextOptions` | `trace: bool = False`, `rating_version_ref: ArtifactRef \| None = None` |
| `ScoringResult` | `outcome: ScoringOutcome`, `rating_version_ref: ArtifactRef`, `bundle_hash: str`, `premium_ladder: list[LadderRung]`, `outputs: dict[str, object]`, `decline_reasons: list[str]`, `trace: Trace \| None`, `timing_ms: dict[str, float]` |
| `QuotePurpose` | `"new_business"`, `"renewal"`, `"mid_term_adjustment"`, `"cancellation"`, `"what_if"` — five, RL-878 discharged |
| `ScoringOutcome` | `"quoted"`, `"declined"`, `"error"` |

`rating_version_ref` is **optional and nullable** inside `options`, and RL-880 clause 1
requires it stay that way: *"a required field puts the code above its own specification."*

### What exists, and what does not

| Thing | State at `d6505e9` |
|---|---|
| `POST /api/v1/score` | **No route.** `git grep -n "api/v1/score" -- backend/src/app/` returns nothing |
| `NO_LIVE_RATING_VERSION` | **Not registered.** Absent from `backend/src/app/errors.py` |
| `INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS`, `MODEL_CALL_FAILED`, `LADDER_RECONCILIATION_FAILED` | Registered — `errors.py:312-315`, added by Task 1.4 |
| `RATE_TABLE_MISS` | Registered — `errors.py:290` |
| `Permission.SCORE_EXECUTE` / `SCORE_BATCH` | Exist — `model_schema/permissions.py:58-59`. **Granted by no builtin role, deliberately** (FR-347), asserted by `backend/tests/test_rbac.py:101-107` |
| Any in-process cache in `backend/` | **None.** RL-882 swept `lru_cache`, `cached_property`, `@cache`, `functools`, module-level dicts and singletons — all absent. This slice ships the first |
| `backend/src/app/platform/diff_cache.py` | Exists — the *shape* to follow (`Protocol`-typed client, identity keys, no TTL, documented failure posture), **not** the backing store, which is Redis and per-request |
| `Settings` | `backend/src/app/config.py:84`, `BaseSettings` with `env_prefix="GIP_"` |
| `test_load_bundle_is_pure_with_respect_to_any_cache` | **Already in the tree and passing** (PR #406). Do not re-implement — register row F32 |

### The register rows this slice must honour

`delivery-process.md` §9 requires every slice plan to read them. All rating-bearing rows are
listed, because a row skipped silently is indistinguishable from one that does not exist.

| Row | Bearing on Slice 2 |
|---|---|
| `RL-882's acceptance-test premise (F32)` | **Resolved, and it changes this plan.** RL-882's acceptance item 1 (the `load_bundle` purity test) is **withdrawn** — it was already discharged in Slice 1 Task 1.3. Item 2 stands. Task 2A must not re-implement it |
| `NFR-502/501 (F-W9-1)` | **This slice discharges the NFR-502 half** — it needs the HTTP path. The NFR-501 half was Slice 1's |
| `FR-224 (F-W9-2)` | WK-673's. Its text says the check *"specialises FR-257's general approval-evidence gate, which WK-671 builds"* — RL-881 rules what WK-671 actually builds of that gate, which is one test |
| `03 rating surface (F8)` | The phase-boundary row. WK-671 discharges its scoring quarter |
| `FR-240 (F-W9-3)` | WK-669/Task 1.2's, about compile-time clauses. Not this slice's |
| `03 rating shapes vs hand-authored contracts (F27)` | Owner decided (RL-860): the §14 review at WK-671's close. The `scoring` half was RL-878's obligation on Task 1.4 and has landed. Not this slice's |
| `FR-231 (F-W10-2)`, `FR-231/233/234/235 (F-W10-1)`, `FR-230 (F-W10-1-1)`, `DP3 diff cache (F-W10-2-1)`, `FR-451 typed diff 200 (F-W10-2-2)`, `03 §5.1 POST /rate-tables/{slug}/versions (F-W10-3)` | WK-670's and WK-675's. Not this slice's |

**Nothing in the register blocks Slice 2.** One row (`F-W9-1`) is discharged in part by it; one
(`F32`) removes work this plan would otherwise have specified.

---

## Corrections to the frozen map

The map is left standing ([`README.md`](README.md): *"a filed plan is a record, not an
instruction"*).

**C1 — Task 2.2 does not exist any more.** RL-880: default-live resolution is WK-674's, and
*"Slice 2 loses that task and gains one refusal branch plus its test inside Task 2.1."*

**C2 — Task 2.3 is one test, not a gate mechanism.** RL-881 refuses option (a) as the map
constructs it, on three independent grounds, the sharpest being that wiring
`effective_evidence("rating_version")` today *"refuses every submission and turns two shipped
tests red"* (`backend/tests/test_rating_versions.py:84` and `:259-264`). What WK-671 owes is *"one
test, and no production code."*

**C3 — the map's FR-251 line reads as two things to implement and is neither.** It says the
endpoint *"resolves an explicit `rating_version_ref` (FR-251 — `prod` restricts to
`approved` versions, records as `what_if`)"*. RL-880 clause 3: both restrictions sit inside
FR-251's own `prod` clause, WK-671 has no environments, so **neither applies**. Do not restrict
to `approved` and do not rewrite `purpose`.

**C4 — one of RL-882's two acceptance items is withdrawn**, per register row F32 and the
*Correction to RL-882* in
[`../rulings/RL-00860-owners-for-the-seven-unowned-register-findings-and-one-new-row.md`](../rulings/RL-00860-owners-for-the-seven-unowned-register-findings-and-one-new-row.md). The
`load_bundle` purity test shipped with Task 1.3. Item 2, the degraded read, stands and is
acceptance criterion 4 above.

**C5 — this plan's own predecessor was wrong about NFR-497, and the correction is load-bearing.**
[`PL-00855-wk-671-slices-2-4-planning-readiness-the-signals-that-release-each-and-what-a-leaf-plan-can-already-take-from-here-2026-08-29.md`](PL-00855-wk-671-slices-2-4-planning-readiness-the-signals-that-release-each-and-what-a-leaf-plan-can-already-take-from-here-2026-08-29.md)
argued option (b) *"satisfies NFR-497 by construction"*. RL-882 clause 5 refutes it: a slot
indexed only by `content_hash` cannot be reached when metadata storage is down, because
ref → `Bundle` → hash **is** a metadata read. Hence Task 2A's second index — the ref → hash memo.
Recorded because the wrong version of this reasoning would have produced a slot that cannot do
the one thing the requirement names.

---

## Requirement coverage

Every id listed individually. A bare numeric range silently drops an append-only id landed
inside it ([`../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md`](../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md) review 8 Q4 found that
mechanism twice, and it has since fired a third time).

| Requirement | Where in `03` | Discharged by | How it is proven |
|---|---|---|---|
| FR-250 | §3.7 | 2B | 200 with a reconciling ladder over HTTP. **The default-live half is WK-674's** (RL-880) and owes a register row at the close |
| FR-251 | §3.7 | 2B | An explicit ref scores a `draft` version — the *"what-if and testing"* the requirement permits. Neither `prod` restriction is imposed (C3) |
| FR-255 | §3.7 | 2B | The error boundary: one test per code, each fired by a deliberately malformed input. **The per-quote *typing* was Slice 1's; the HTTP *mapping* is this slice's** |
| FR-256 | §3.7 | 2B | A decline is **200** with a populated ladder, never an HTTP error. Slice 1 proved it in-process; this proves it survives the boundary |
| FR-257 | §3.8 | 2C | A blank `change_summary` is refused **422**, from a test carrying `FR-257` |
| NFR-489 | §9 | 2D | p99 at the full HTTP path, plus the sustained-200 rps test [`../roadmap.md`](../roadmap.md) names separately |
| NFR-497 | §9 | 2A, 2B | The degraded read (acceptance 4). **The 99.95 % availability target is not discharged here** — RL-882 clause 5 — and owes a register row |
| NFR-499 | §9 | 2B | The three RBAC cases, plus a rate-limit test |
| NFR-502 | §9 | 2B, 2D | The malformed-`ScoringResult`-returned-verbatim test, and the re-measurement on the real path |

**Deliberately excluded, each with its owner:** FR-RATE-36, 37 → Slice 3. FR-255's batch
half → Slice 3. FR-259 → Slice 4. FR-RATE-43, 44, 45 → WK-672. FR-263–49 → WK-673. FR-267,
FR-428 → WK-674. NFR-493 → Slice 3. NFR-500 → Slice 4.

---

## Sequencing and blockers

| Task | Depends on | Blocked by | Why |
|---|---|---|---|
| 2A — error code + slot | Slice 1 (merged) | — | 2B cannot raise an unregistered code, and cannot hold a bundle without the slot |
| 2B — the route | 2A | — | The endpoint |
| 2C — FR-257 test | — | — | Independent of everything; may run first or in parallel |
| 2D — measurement | 2B | **Task 1.5, in flight** | See below |

**2D's scheduling constraint is real and is not a dependency on 2B alone.** RL-872 rules that
the sustained-load driver is `asyncio` + `httpx` *"in the same `scripts/` convention"*, and
**Task 1.5 is building `scripts/bench-rating.py` right now.** Two branches adding sibling
scripts and a `docs/research/` note will collide. **Land 2D after Task 1.5 merges**, and reuse
its harness rather than writing a second one. `httpx` is already a declared dependency
(`backend/pyproject.toml:18`, root `pyproject.toml:24`), so no dependency question arises —
unlike `orjson`, which RL-883 refuses.

**`PlatformError.__init__` raises `ValueError` on an unregistered code**, so 2A's registration
step physically cannot be skipped — which is the mechanism RL-880 relies on to stop itself
being half-applied.

---

## Task 2A — `NO_LIVE_RATING_VERSION`, and the bundle slot

**What this builds.** The error code RL-880 requires, and the per-worker in-process slot
RL-882 rules — *"the first in-process cache in this backend"*, which is why it must be
shaped as a dedicated module rather than appear as a module-level dict.

**Files**
- Modify: `backend/src/app/errors.py` — append `NO_LIVE_RATING_VERSION` to `RATING_ERROR_CODES`
  (the block at `:307-315`), HTTP **409**. 409 is this backend's established status for *"the
  artifact is not in a state that permits this"* — `platform/datasets.py:568`,
  `platform/jobs.py:214`, `platform/rating_versions.py:160`, `platform/approvals.py:427`.
- Create: `backend/src/app/platform/bundle_slot.py`.
- Modify: `backend/src/app/config.py` — one typed setting, capacity as a **count**, default
  **1** (RL-882 clause 3). Follow the neighbouring fields' form; `env_prefix` is `GIP_`.
- Test: `backend/tests/test_bundle_slot.py`.

**Interfaces — Produces** (2B relies on these names):
- `BundleSlot` — holds hydrated `CompiledBundle` objects, keyed by the source `Bundle`'s
  `content_hash`, plus a **second index** recording, for each `ArtifactRef` this worker has
  served, the hash it resolved to (RL-882 clause 5 — without it the degraded read cannot be
  reached, because ref → hash is itself a metadata read).
- Least-recently-used eviction, which at capacity 1 is replacement.
- **No refresh, no poll, no pub/sub, no environment pointer** — all four are WK-674's (RL-882
  clause 4). A slot that acquires any of them has overridden the ruling.

**Shape to follow.** `backend/src/app/platform/diff_cache.py` — a dedicated module, a
`Protocol`-typed client so a fake satisfies it without a broker, identity keys, no TTL, a
documented failure posture. **What must not be copied is its backing store**: `DiffCache` is
Redis (`diff_cache.py:70-75`) and constructed per request
(`backend/src/app/api/rate_tables.py:355`); this slot is in-process and per worker.

**Steps**

- [ ] **Step 1: Write the failing test for the code's registration.** Assert that
      `PlatformError("NO_LIVE_RATING_VERSION", ...)` constructs and carries status 409. Mirror
      the neighbouring error-code tests rather than inventing a fixture; do not reinvent the
      module's helpers.
- [ ] **Step 2: Run it and confirm the failure's cause, not just its status.** Expected: a
      `ValueError` from `PlatformError.__init__` naming the unregistered code. **A different
      exception, or an `AssertionError` about the status, means something else is wrong** and is
      a plan defect rather than the predicted red.
- [ ] **Step 3: Register the code.** Append to `RATING_ERROR_CODES`. Run: green.
- [ ] **Step 4: Write the failing slot tests.** Three, each a distinct property: a hydrated
      bundle is returned on a second `get` for the same hash without re-hydrating; at capacity 1
      a second distinct hash evicts the first; a ref served once is resolvable to its hash
      afterwards without a metadata read.
- [ ] **Step 5: Run them.** Expected: `ModuleNotFoundError` for `bundle_slot`. A different error
      means the module was created early.
- [ ] **Step 6: Implement `BundleSlot` and the capacity setting.** Keep it synchronous unless a
      caller needs otherwise; `load_bundle` is sync and pure.
- [ ] **Step 7: Run the slot tests and `uv run lint-imports`.** The import contract is what keeps
      the slot out of `pricing_core`; it must stay green.
- [ ] **Step 8: Commit.** `feat(rating): NO_LIVE_RATING_VERSION and the per-worker bundle slot`

**Must NOT touch.** `load_bundle` — RL-876's purity property is already tested in the tree
(`test_load_bundle_is_pure_with_respect_to_any_cache`, register row F32). Do not add a cache
lookup to it, and **do not re-implement its test**.

---

## Task 2B — `POST /api/v1/score`

**Files**
- Create: `backend/src/app/api/score.py`; register it in `backend/src/app/main.py`'s router
  list (`:110-129` at `d6505e9` lists 19 routers and no scoring one — re-derive the line).
- Test: `backend/tests/test_score.py`.

**Interfaces — Consumes:** 2A's `BundleSlot` and `NO_LIVE_RATING_VERSION`; `score_one`,
`load_bundle`, `CompiledBundle` from `pricing_core.rating`; `QuoteContext`/`ScoringResult` from
`model_schema.scoring`; `Permission.SCORE_EXECUTE`; the blob store's `read`.

**The request path, in order.** Each arrow is a place an executor could put the wrong behaviour:

1. Authenticate; the `Caller` carries `environments: frozenset[str]` and
   `permissions: frozenset[str]` (`backend/src/app/api/deps.py:65-66`). Require
   `Permission.SCORE_EXECUTE`. **Grant nothing** — RL-884: *"Task 2.1 grants nothing; it
   checks."*
2. Validate the inbound `QuoteContext`. Inbound validation is required; outbound is forbidden.
3. **If `options` is absent or `options.rating_version_ref` is `None` → 409
   `NO_LIVE_RATING_VERSION`.** This is the route's refusal, raised here, before `score_one`.
4. Resolve the ref to its `Bundle` — metadata read, then the blob store.
5. `BundleSlot` → hydrated `CompiledBundle`, hydrating via `load_bundle` on a miss.
6. `await score_one(bundle, ctx, trace=ctx.options.trace)`.
7. Serialise the `ScoringResult` directly into a raw `Response`. **No `response_model=`, no
   Pydantic-model return annotation** (RL-883).

**Steps**

- [ ] **Step 1: Write the failing happy-path test** — a real Rating Version created and compiled
      over HTTP (Tasks 1.1/1.2 shipped those routes), then posted to `/api/v1/score` with an
      explicit ref. Assert 200 and that the ladder reconciles. **Mirror
      `backend/tests/test_rating_versions.py`'s fixtures** (`_principal`, `_draft`) rather than
      building new ones.
- [ ] **Step 2: Run it.** Expected: **404**, because no route is registered. **A 405 means a
      router was added with the wrong method; a 401 means the auth dependency is wired but the
      route is not** — both are different failures and neither is the predicted red.
- [ ] **Step 3: Write the 409 test.** Post the same body with `"options": {"rating_version_ref":
      null}`, and again with `options` omitted entirely. Both must return **409** with code
      `NO_LIVE_RATING_VERSION`. Mark `@pytest.mark.req("FR-250")`.
- [ ] **Step 4: Write the discriminating test for step 3-versus-`score_one`.** Assert the 409
      body's code is `NO_LIVE_RATING_VERSION` and **not** `INPUT_CONTRACT_VIOLATION`. Without
      this, a route that simply forwards to `score_one` and maps its error passes step 3's
      status check while answering with the wrong code.
- [ ] **Step 5: Write the outbound-validation test** (RL-883's acceptance test). Construct a
      `ScoringResult` whose contents violate its own declared types, have the route return it,
      and assert the response body is that object **verbatim** with a 200 — not a 500. This is
      the test that discriminates the raw-`Response` implementation from the annotated one; a
      route with a return annotation returns 500 here.
- [ ] **Step 5a: Write the four error-mapping tests, one per code.** `pricing-core` raises a
      code-named bare `ValueError` (`_raise_named`); the boundary that turns it into a
      `PlatformError` is **this route's**, per `errors.py:305-311` and
      `model_schema/scoring.py:65-68`. One test each, fired by a deliberately malformed input:
      `INPUT_CONTRACT_VIOLATION` (a required input missing from `ctx.inputs`), `RATE_TABLE_MISS`,
      `REFERENCE_LOOKUP_MISS`, `MODEL_CALL_FAILED`. Assert the RFC 9457 problem body carries
      **that** code. Mark `@pytest.mark.req("FR-255")`.
      **Parse the code out of the message, do not string-match the whole message** — the
      `ValueError` text is `f"{code}: {message}"` and the message half is prose that will change.
- [ ] **Step 5b: Write the decline test.** A constraint decline must be **200** with
      `outcome: "declined"`, a non-empty `decline_reasons`, and a **populated** ladder —
      FR-256, never an HTTP error. Mark `@pytest.mark.req("FR-256")`.
      **This is the test that stops the mapping in 5a from being written too widely**: a boundary
      that catches every `ValueError` and problem-ifies it will pass 5a and fail here.
- [ ] **Step 5c: Confirm the one thing the mapping must NOT do.** A firing
      `on_violation="error"` constraint raises a plain `NotImplementedError`, deliberately
      undesigned in Task 1.4 (`score.py`'s `_apply_constraints`). It is **not** a platform code
      and must not be mapped to one. Assert it propagates as a 500 rather than being dressed as
      a typed per-quote error, so the gap stays visible to whoever designs it.
- [ ] **Step 6: Write the three RBAC tests** (RL-884): scoped account with the permission
      succeeds; scoped account without it is refused; a key for an environment outside the
      account's list is refused **at authentication**, before the route
      (`backend/src/app/auth/service.py:212`). Mark `@pytest.mark.req("NFR-499")`.
- [ ] **Step 7: Write the degraded-read test** (RL-882 acceptance item 2). Patch the
      rating-version load to raise. A second request for an already-served ref returns 200 from
      the slot; a first request for an unseen ref is refused. Mark
      `@pytest.mark.req("NFR-497")`.
- [ ] **Step 8: Run all of them and confirm each fails for its own stated cause** before writing
      the route.
- [ ] **Step 9: Implement the route** following the seven-step path above.
- [ ] **Step 10: Run the full gate, both halves.**
- [ ] **Step 11: Commit.** `feat(rating): POST /api/v1/score on the shared evaluator (WK-671 Task 2B)`

**Must NOT touch.** `score_one` or `build_scoring_result` — they are Task 1.4's, tested, and
**Task 1.5 may be editing that package concurrently**. If the route needs something they do not
expose, that is a finding, not an edit.

---

## Task 2C — the one test FR-257 owes

**What this builds: one test, and no production code.** RL-881's words. One of FR-257's
four limbs — a change summary (FR-242) — is *already enforced on `main`*:
`backend/src/app/platform/approvals.py:170-177` raises
`PlatformError("VALIDATION_FAILED", "A change summary is required", 422, ...)` citing FR-352,
and every rating-version submission reaches it via
`rating_versions.submit_for_review` (`rating_versions.py:166-172`). What it lacks is
**attribution**: no test names FR-257, so `req-coverage.py` cannot see the control.

**Files**
- Modify: `backend/tests/test_rating_versions.py` — one case. The file already uses
  `@pytest.mark.req(...)` at `:65`, `:111`, `:133`, and
  `test_submit_rating_version_over_http` (`:231`) with `submit_body = {"change_summary": "demo
  rating version"}` (`:258`) is the neighbour to mirror.

**Steps**

- [ ] **Step 1: Write the test.** Submit a rating version whose `change_summary` is `"   "`;
      assert **422**. Mark `@pytest.mark.req("FR-257")`.
- [ ] **Step 2: Run it.** It should **pass immediately** — the control already exists; this test
      attributes it. **That is the expected outcome here, and it is the one case in this plan
      where a first-run pass is correct rather than suspicious.** Confirm it is testing what you
      think by inverting it once: a non-blank summary must not 422.
- [ ] **Step 3: Run `uv run python scripts/req-coverage.py`** and confirm FR-257 now carries
      a marker.
- [ ] **Step 4: Commit.** `test(rating): attribute FR-257's change-summary limb (WK-671 Task 2C)`

**Must NOT touch.** `rating_versions.submit_for_review`. **RL-881's override condition is
explicit: if any WK-671 commit makes it call `policy.effective_evidence("rating_version")`, the
ruling has been overridden** — and it is directly observable, because
`backend/tests/test_rating_versions.py:84` and `:264` go red with no input change.

---

## Task 2D — the measurements [land after Task 1.5]

**Files**
- Reuse: Task 1.5's harness in `scripts/`. Extend rather than duplicate — RL-872 rules the
  driver is `asyncio` + `httpx` in that convention, and a second script measuring the same thing
  is how two numbers start disagreeing.
- Create: a dated note under [`../research/`](../research/), matching
  `zen-evaluate-concurrency.md`'s precedent.

**Acceptance**
- **NFR-489 at the full HTTP path** — p99 against the **< 50 ms** bound for a ~200-step motor
  structure with one `exact` GBM call, plus the **sustained-200 rps** test
  [`../roadmap.md`](../roadmap.md) names separately from the single-request spikes.
- **NFR-502 re-measured on the real path**, against WK-668's synthetic p99 0.070 ms.
- **NFR-499's rate limit** exercised.
- **Report the distribution, not only the p99 against the bound.** A number comfortably inside a
  budget and one sitting on it are different findings, and only the distribution separates them.
- **A number carries the shape it was measured in.** Say whether the figure includes bundle
  hydration or reads a warm slot — they are different measurements, and the register's own
  NFR-501 row is the standing example of a figure that meant something narrower than it read.
- **Not a CI gate.** A timing assertion on a shared runner fails for reasons unrelated to the
  code.

---

## Findings raised by this plan

**F-W11-2-1 — `LADDER_RECONCILIATION_FAILED` is registered, owned by the spec, and raised by
nothing; a ladder that fails to reconcile is currently silent.** Verified at `d6505e9`:
the code is in `RATING_ERROR_CODES` (`backend/src/app/errors.py:315`) and `03` §5.1 owns it,
but `git grep -n "LADDER_RECONCILIATION_FAILED" -- packages/ backend/` returns **only that
registration**. In the shipped path, `reconcile_ladder`'s boolean result flows to exactly one
place — `Trace.ladder_reconciled` — so a quote whose ladder does not reconcile is returned as a
normal **200**, and the fact is visible only if the caller asked for a trace *and* reads that
field.

Two reasons this is not simply "Slice 2 should raise it", which is why it is a finding rather
than a task:

- Task 1.4's `_build_ladder` derives each rung's recorded operation from the delta between
  consecutive rungs and then *reapplies* it, so the ladder reconciles **by construction**. On
  that design the check can only fire on a genuine defect, which is an argument for raising and
  also an argument that it is unreachable — and those want different answers.
- NFR-496 is Slice 1's and is already proven over generated contexts. Adding a runtime raise
  here would be new refusal behaviour on the quoting path, which is a scope question.

**Owner: the decision-maker** — it is a spec-vs-code question (`03` §5.1 owns a code the code
base never raises), which `delivery-process.md` §3 makes theirs, not the planner's and not the
executor's. **Not a blocker:** Slice 2's error boundary maps the four codes that *are* raised,
and this one is simply not among them. Related to, but distinct from, register row F29 — that
row is about the gate never comparing `errors.py` against the specs at all; this is one
concrete instance already visible without such a check.

## Self-review

**1. Spec coverage.** Every requirement the frozen map allocates to Slice 2 appears in the
coverage table with its spec section and the task that discharges it, listed individually.
Exclusions carry owners. Two requirements are *partially* discharged and say so in the table
rather than in prose — FR-250's default-live half and NFR-497's availability target are
WK-674's, and each owes a register row the lead writes at the close.

**2. Placeholder scan.** No TBD. Task 2D is scheduled behind an in-flight task rather than left
vague, and the reason is a file collision an executor could not otherwise predict.

**3. Type consistency.** `CompiledBundle`, `load_bundle`, `score_one`, `build_scoring_result`,
`QuoteContext`, `QuoteContextOptions`, `ScoringResult` are used under the names the shipped code
declares, copied from `model_schema/scoring.py` and `rating/score.py` rather than retyped.
`BundleSlot` is named once in 2A's *Produces* block and used under that name in 2B.

**4. Literals verified against shipped source at `d6505e9`.** Field lists, enum members, error
codes, permission names and the `diff_cache` shape were read out of the tree. **Where Task 1.5
may be editing concurrently — everything under `pricing_core/rating/` — symbols are cited by
name with a re-derivation command instead of a line number**, because a line number in a file
someone else is editing is a citation with a short half-life.

**5. Predicted failures are stated by cause.** Four: the `ValueError` versus a status assertion
in 2A Step 2; the 404-versus-405-versus-401 split in 2B Step 2; the
`NO_LIVE_RATING_VERSION`-versus-`INPUT_CONTRACT_VIOLATION` discrimination in 2B Step 4; and the
500-versus-verbatim discrimination in 2B Step 5. 2C Step 2 is the deliberate exception — a
first-run **pass** is correct there, and the step says so and gives an inversion to check it.

**6. What this plan does not decide: nothing was left to the executor that a charter owns.**
Every design question this slice faced is ruled — DP1 by RL-880, DP2 by RL-881, D4 by
RL-882, F1 by RL-883, M4 by RL-884. The one open item this plan found is not Slice 2's:
see the Slice 3 readiness record filed alongside it.

**7. One correction to this plan's own predecessor is recorded rather than folded in** — C5, the
NFR-497 claim. The readiness document reasoned that the slot satisfied it "by construction";
RL-882 clause 5 showed the reasoning skipped a metadata read, and the fix is a second index
that would not otherwise have been built. Left visible because a plan that quietly agrees with
today's rulings destroys the record of what was believed.
