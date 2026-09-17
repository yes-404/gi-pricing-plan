---
id: PL-855
family: plan
kind: leaf
title: WK-671 Slices 2–4 — planning readiness, the signals that release each, and what a leaf plan can already take from here (2026-08-29)
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-29
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-29-w11-slices-2-4-planning-readiness.md
---

# WK-671 Slices 2–4 — planning readiness, the signals that release each, and what a leaf plan can already take from here (2026-08-29)

**What this is.** [`PL-00854-wk-671-scoring-sequenced-slice-plan.md`](PL-00854-wk-671-scoring-sequenced-slice-plan.md) cuts WK-671 into four
slices. Slice 1 has a leaf plan
([`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)); Slices 2, 3 and
4 have none. This document is the planner's answer to whether they can have one **today**,
task by task, with the evidence for each answer, the signal that releases each held slice,
and the durable content the eventual leaf plans should not have to re-derive.

**What this is not.** It is not a plan and it is not a replan. It files no task list, freezes
no implementation, and rules nothing. Whether Slices 2–4 are re-cut is the lead's call
([`../process/delivery-process.md`](../process/delivery-process.md) §3); every decision point
below is the decision-maker's. A planner supplies options and a recommendation and rules none
of them.

**The verdict, in one line: all three are held, and none of them is held on the same thing.**
Two are held on code, one task is held only on a ruling, and the differences are what makes
the holds actionable rather than a wait.

**Tree:** `9891be1`, fetched and confirmed equal to `origin/main`, clean working tree. Every
grep, line number and absence claim below was run at that tree. A line number is only as good
as its revision.

**Highest ids in use, re-derived at `9891be1` by scanning
[`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) and
[`../open-questions.md`](../open-questions.md):** FR-243, NFR-501, OQ-619.
Next free: `FR-RATE-66`, `NFR-RATE-15`, `OQ-620`.

**This document mints none of them.** The line is re-derived rather than carried forward from
[`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md), which verified it
at `7b8473a`: a stale allocation aid is what mints a colliding id, and that plan's own line
exists because [`PL-00829-wk-670-implementation-plan-rate-tables-seeding-diffs-bulk-operations-import-export.md`](PL-00829-wk-670-implementation-plan-rate-tables-seeding-diffs-bulk-operations-import-export.md) went stale the
same way. One `OQ-620` is *owed* by someone — see D5 — and this document does not take it.

---

## 1. The verdict

| Slice | Verdict | Held on | Releases when |
|---|---|---|---|
| **2 — real-time endpoint + approval gate** | **Held**, and its three tasks are held on three different things | Task 2.1: unbuilt types + an unowned design question. Task 2.2: DP1. Task 2.3: DP2 only | See §5 |
| **3 — batch scoring** | **Held** | An evaluator seam whose name is Task 1.4's to choose, plus two unruled items | See §6 |
| **4 — trace sampling & persistence** | **Held**, and it is the most blocked of the three | An unbuilt `Trace` type an acceptance criterion measures the *size* of, plus one unruled item and one owed spec change | See §7 |

**Nothing here says the slices are unplannable.** It says a plan written today would freeze
literals that the work already scheduled ahead of it is chartered to change, and would have to
guess at design questions nobody has been asked. §5–§7 each end with the content that *is*
durable, so the eventual leaf plans start from evidence rather than from a blank file.

**Four things the sweep found that no document currently names**, each of which would otherwise
have been discovered mid-slice: a design question the frozen map leaves in a gap between two
rulings (D4, §9), a dependency NFR-502 needs that this workspace does not have (F1, §3.4), a
type `score_batch`'s signature requires that the repository has never used (F2, §3.4), and an
instruction in the frozen map that would break a passing test if followed (M4, §10). **D4, F1 and
M4 can each be put to the decision-maker now**, in parallel with Slice 1 execution; F2 is a scope
finding the Slice 3 plan absorbs rather than a question anyone has to answer first. That is what
makes the hold a schedule rather than a wait.

## 2. The test applied, and why it is this one

Three rules decide it, and none of them is a preference.

1. [`README.md`](README.md)'s **first unenforced convention** — *"Verify every repository
   literal against the shipped source before it enters sample code — enum members, fixture and
   factory names, route paths, status codes, model field names. Grep each one."* A literal that
   cannot be verified because the source does not exist yet fails this at the root: there is
   nothing to grep.
2. [`README.md`](README.md)'s **third** — *"Where you cannot verify, name the authority instead
   of supplying a sample."* This is the escape hatch, and it is a real one. The question for
   each slice is therefore not "is anything unbuilt" but **"is what is unbuilt narrow enough
   that naming the authority still leaves an executable plan?"** For Slices 2–4 it is not: the
   unbuilt thing is the *first parameter of every signature in the slice*, and a plan that
   names the authority for all of it has written prose, not a plan.
3. [`../../CLAUDE.md`](../../CLAUDE.md) §12 — a role decides what its charter names and nothing
   else, and decision points are the decision-maker's. Writing a step-level plan for one option
   of an unruled decision point pre-empts the ruling; the frozen map already refuses to
   ([`PL-00854-wk-671-scoring-sequenced-slice-plan.md`](PL-00854-wk-671-scoring-sequenced-slice-plan.md) Task 2.2: *"Files and exit criteria
   depend on which option rules — do not guess."*).

A fourth consideration, from [`README.md`](README.md)'s own fifth convention and from
[`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)'s self-review: **a
plan's premises age faster than its literals.** A leaf plan filed now would be frozen at
2026-08-29 and read by an executor after Tasks 1.2–1.5 merge — the exact window in which every
literal it could cite changes.

## 3. Evidence sweep at `9891be1`

### 3.1 The six names every Slice 2/3/4 signature takes have no Python definition

`git grep -n -E "QuoteContext|ScoringResult|score_one|score_batch|CompiledBundle|load_bundle"
-- '*.py'` returns **one hit repo-wide**, and it is a docstring:
`scripts/audit-docs.py:499` — `"""Resolve a JSON Pointer fragment such as
'/$defs/QuoteContext'."""`. No definition, no import, no call site.

`ls packages/pricing-core/src/pricing_core/rating/` returns `__init__.py` and `compile.py`.
There is no `score.py` and no `runtime.py`.

Read against [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §5.2, that is every
function the three held slices are made of:

| §5.2 declares | Exists at `9891be1` | Owed by |
|---|---|---|
| `load_bundle(bundle: Bundle) -> CompiledBundle` | No | Slice 1 Task 1.3 |
| `async def score_one(bundle: CompiledBundle, ctx: QuoteContext, *, trace: bool = False) -> ScoringResult` | No | Slice 1 Task 1.4 |
| `score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, *, chunk_rows: int = 100_000, progress: ProgressCallback \| None = None) -> pl.LazyFrame` | No | **Slice 3** |
| `QuoteContext`, `ScoringResult`, `Trace` as Python types | No | Slice 1 Task 1.4 |

Slice 3's own deliverable is the only row in that table it can supply for itself. The other
three are Slice 1's, and `score_batch` takes two of them.

And `score_batch`'s *other* parameter has no neighbour either. At `9891be1`,
`git grep -c "LazyFrame" -- '*.py'` returns **zero hits repo-wide**, while the same pattern with
no pathspec returns hits in five documents (`03`, `04`, `05`, `01`, plus the frozen map and a
research note) — so `LazyFrame` is a word this repository writes about and has never written.
The zero is a true negative, not a dead pathspec: the control `git grep -c "import polars" --
'*.py'` on the same pathspec returns hits in `backend/src/app/data/formats.py`,
`ingestion.py` and `platform/prediction.py`. The specified signature takes a `pl.LazyFrame` and
returns one, and nothing in this codebase has ever used the type.
[`README.md`](README.md)'s own rule applies — *"a missing neighbour is a scope finding … a zero
means that path has no coverage at all, which is larger than a formatting detail and belongs in
the plan's scope section"*. Parquet writing exists, but as `polars`'s `write_parquet` called
directly at each use site (`backend/src/app/data/ingestion.py`,
`backend/src/app/worker/data_handlers.py:419`, `backend/src/app/platform/rate_tables.py:512`),
with no shared helper; the nearest non-materialising *read* precedent is
`packages/pricing-core/src/pricing_core/data/profile.py:494` `profile_parquet`, which goes
through DuckDB rather than a `LazyFrame`.

### 3.2 The one shipped artifact that describes those shapes is verifiably wrong today

`QuoteContext`, `LadderRung`, `ScoringResult` and `Trace` exist as `$defs` in the
**hand-authored** contract [`../contracts/schemas/scoring.schema.json`](../contracts/schemas/scoring.schema.json).
Read [`.claude/skills/contract-guard`](../../.claude/skills/contract-guard/SKILL.md) before
citing it: `docs/contracts/schemas/*.schema.json` is the *specified*, hand-authored tier and
`docs/contracts/schemas/generated/*` is the *generated*, enforced one. Nothing compares the two
for these shapes.

At `9891be1`, `scoring.schema.json:12` reads:

```json
"purpose": {"enum": ["new_business", "renewal", "mid_term_adjustment", "what_if"]},
```

Four members. [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §2 (`:63`) has
**five** — `cancellation` was added 2026-08-18 with FR-218.
[`../findings/register.md`](../findings/register.md) row `03 rating shapes vs hand-authored contracts
(F27)` records this divergence and carries it forward with an owner, and
[`../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md`](../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md) RL-878 assigns the fix
to **Task 1.4**, in the same PR as the `model-schema` enum and the two-member refusal test.

This is the whole argument in one artifact. A Slice 2 leaf plan written today would put a
request-validation sample test into an executor's hands carrying a four-member `purpose` enum,
sourced from the only shipped description of the shape, and Task 1.4 is chartered to make it
five before that plan is ever executed. The plan would be self-consistent, would pass
`audit-docs.py`, and would be wrong — [`README.md`](README.md) rule 3's failure mode exactly.

### 3.3 What *does* exist, and is safe to plan against

Verified individually at `9891be1`:

| Thing | State |
|---|---|
| `POST /api/v1/rating-versions` | Exists — `backend/src/app/api/models.py:1155` (landed by PR #371, Task 1.1) |
| `POST /api/v1/rating-versions/{id}/submit` | Exists — `backend/src/app/api/models.py:1183` |
| `POST /rating-versions/{id}/compile` | Exists — `backend/src/app/api/models.py:1211`, still returns **200**; Task 1.2 makes it `202` |
| `submit_for_review` | Exists — `backend/src/app/platform/rating_versions.py:141` |
| `RatingVersionEvidence` | Exists — `packages/model-schema/src/model_schema/rating.py:88`; fields `regression_suite_run_id`, `dislocation_run_id`, `gipp_check_id`, `structural_diff_blob`, all `UUID \| None`/`str \| None` |
| `EVIDENCE_INCOMPLETE` | Registered — `backend/src/app/errors.py:254` |
| `Bundle`, `JdmGraph`, `to_jdm`, `compile_bundle`, `bundle_hash` | Exist — `packages/pricing-core/src/pricing_core/rating/compile.py` |
| `Permission.SCORE_EXECUTE`, `Permission.SCORE_BATCH` | Exist as enum members — `packages/model-schema/src/model_schema/permissions.py:58`, `:59`. **Granted by no builtin role, deliberately** — see M4 |
| `JobKind.SCORE_BATCH`, `JobKind.RATING_COMPILE` | Exist — `packages/model-schema/src/model_schema/jobs.py:56` (`"score.batch"`), `:53` (`"rating.compile"`). Neither has a registered handler; submitting either fails with `JOB_HANDLER_NOT_REGISTERED` at `backend/src/app/worker/tasks.py:117-123` |
| Blob store | `backend/src/app/platform/blobs.py`, `class BlobStore` at `:98`. The three methods a Slice 3/4 plan wants are `put(session, content, media_type) -> BlobRef` (`:130`), `open(ref) -> AsyncIterator[bytes]` (`:181`) and `read(ref) -> bytes` (`:208`). **There is no `get`** |
| `INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS`, `LADDER_RECONCILIATION_FAILED` | Owned by `03` §5.1 and **absent from `backend/src/app/errors.py`** — the class RL-877's finding 1 describes; nothing in the gate reads `errors.py` |
| `ORJSONResponse` / `orjson` | **Absent everywhere** — see F1 |
| `pl.LazyFrame` | **Zero hits repo-wide** — see §3.1 |

**That row set is the whole of Slice 2 Task 2.3's dependency surface**, and it is complete.
Task 2.3 needs nothing from Tasks 1.2–1.5. It is held by DP2 alone — a ruling, not a build.
That asymmetry is the single most useful thing in this document and §8's P1 acts on it.

### 3.4 Two obligations that no document currently names

Both were found by sweeping the tree rather than by reading the map, and neither appears in the
frozen map, in either rulings record, or in the recovery document. Neither is a decision point:
one is a dependency question with a governance consequence, the other is a scope finding.

**F1 — NFR-502 prescribes a response class whose library is not a dependency of this
workspace.** NFR-502 (`03` §9) requires the scoring endpoint to skip `response_model`
validation and serialise *"with a C-speed encoder (`ORJSONResponse`)"*. At `9891be1`:
`git grep -n "ORJSONResponse" -- backend/` returns nothing; the only `response_class=` uses in
the backend are `RedirectResponse` (`backend/src/app/api/blobs.py:102`) and `PlainTextResponse`
(`backend/src/app/api/health.py:139`); `git grep -n "orjson" -- '*.toml'` returns nothing; and
**`orjson` appears zero times in `uv.lock`**, so it is not even a transitive dependency today.

Adding it is a **tech-dependency change**, which [`../../CLAUDE.md`](../../CLAUDE.md) §10 makes a
`docs/skills-map.md` update in the same PR, and which the spec-change procedure makes a §8 row
in the owning spec. So Slice 2 carries a documentation obligation that reads as a one-line code
change and is not one. **Not resolved here** — whether NFR-502 is satisfied by adding
`orjson`, by a different encoder, or by re-reading the requirement in light of WK-668's measured
p99 0.070 ms (which is what prompted its 2026-08-27 amendment in the first place) is the
decision-maker's, and the amendment explicitly left the design rule unchanged while retiring
its cost premise. Raised now because it is dispatchable now and would otherwise be found
mid-slice. The Slice 2 planner should also verify, at their own commit, whether FastAPI's
`ORJSONResponse` fails at import or at first render without `orjson` — a failure at render is a
different, later, and more expensive discovery than a failure at import, and this document does
not assert which it is.

**F2 — Slice 3's specified signature has no neighbour to mirror.** Stated in §3.1: zero
`LazyFrame` hits repo-wide. This belongs in the Slice 3 plan's *scope* section, not in a step —
the plan has to decide whether `score_batch` establishes the repository's first `LazyFrame`
pattern or works in a shape that already has precedent, and that is a scope-sized question.

## 4. Requirement allocation, every id listed individually

Derived from [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.7, §3.8 and §9
first, then checked against the frozen map — not the other way round. A bare numeric range
silently drops an append-only id landed inside it
([`../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md`](../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md) review 8 Q4 found that mechanism twice).

| Requirement | Spec section | Slice | Note |
|---|---|---|---|
| FR-250 | §3.7 | 1 (core) + **2** (default-live resolution) | The split is DP1's subject |
| FR-251 | §3.7 | **2** | `prod` restricts to `approved`; recorded as `what_if` |
| FR-253 | §3.7 | **3** | `POST /api/v1/score/batch`, Job, parquet output |
| FR-254 | §3.7 | **3** | Identical bundle *and code path* as real-time |
| FR-255 | §3.7 | 1 (per-quote typing) + **3** (batch counts, samples, threshold) | The threshold's home is unruled — D3 |
| FR-256 | §3.7 | 1 | Amended 2026-08-29 by RL-875; nothing owed to 2–4 |
| FR-257 | §3.8 | **2** | DP2's subject |
| FR-258 | §3.7 | 1 (capture) | *"Traces are the same structure in real-time and batch"* binds Slice 3 |
| FR-259 | §3.8 | **4** | Sampling, ≥ 13-month retention |
| FR-252 | §3.7 | 1 | Both halves — the rung and the APR refusal |
| FR-243 | §3.4 | 1 | See §8 P3 |
| NFR-489 | §9 | 1 (component) + **2** (full path, sustained 200 rps) | |
| NFR-493 | §9 | **3** | ≥ 1 M risks/hour/worker |
| NFR-497 | §9 | **2** | *"degrading to the last-known-good cached bundle"* — see D4 |
| NFR-499 | §9 | **2** (auth, rate limits) + **4** (traces access-controlled) | |
| NFR-500 | §9 | **4** | 1 % of 50 M quotes under 200 GB/year |
| NFR-502 | §9 | **2** | Validate inbound, never outbound; `ORJSONResponse` |

**Excluded, each with its owner:** FR-RATE-43, 44, 45 → WK-672. FR-RATE-46, 47, 48, 49 → WK-673.
FR-267 and FR-428 → WK-674. FR-224 → WK-673
([`../findings/register.md`](../findings/register.md) row `FR-224 (F-W9-2)`), and its own text
says the check *"specialises FR-257's general approval-evidence gate, which WK-671 builds"* —
so **DP2's ruling is a WK-673 input**, not only a WK-671 one.

## 5. Slice 2 — held, on three different things

### 5.1 Task 2.1 — `POST /api/v1/score`, ref-based path

**Held on code, and on a design question nobody owns yet.**

Its request body is `QuoteContext`, its response is `ScoringResult`, and it calls `score_one`
with a `CompiledBundle`. None exists (§3.1), and the one shipped description of the first two
is wrong in a way Task 1.4 will fix (§3.2). Naming the authority does not rescue it: the
authority is the code Task 1.4 has not written.

Beyond that, **there is a hole between RL-876 and NFR-497 that no slice currently
fills** — raised as D4 in §9.

### 5.2 Task 2.2 — default-live resolution

**Held on DP1**, exactly as the frozen map says, plus everything in §5.1 — its branch hangs off
the same route. Even with DP1 ruled (b), the deferral has to be *written* as a named register
deferral, and the register row's wording is the auditor's and lead's, not the planner's.

### 5.3 Task 2.3 — the approval gate

**Held on DP2 alone.** Its whole dependency surface shipped (§3.3): `submit_for_review`,
`RatingVersionEvidence` with the two evidence ids the gate reads, the `EVIDENCE_INCOMPLETE`
code, and — as of PR #371 — an HTTP route in front of the service function. Nothing in Tasks
1.2–1.5 touches any of it.

So this task is plannable **the day DP2 rules**, whatever Slice 1 is doing, and it is the only
part of Slices 2–4 of which that is true.

### 5.4 Release signals for Slice 2

| Signal | Releases | Depends on |
|---|---|---|
| **S-A** — Task 1.4 merged to `main` | 2.1, 2.2 | Tasks 1.2, 1.3 first (strictly sequential) |
| **S-B** — DP1 ruled | 2.2 | Decision-maker; nothing else |
| **S-C** — DP2 ruled | **2.3, alone** | Decision-maker; nothing else |
| **S-D** — D4 ruled (§9) | 2.1 | Decision-maker; can be raised now |
| **S-K** — F1 settled: how NFR-502's `ORJSONResponse` is satisfied, and the `skills-map.md` and §8 rows it owes | 2.1 | Decision-maker; can be raised now |

S-B, S-C, S-D and S-K are all dispatchable **today**, in parallel with Slice 1 execution. Only
S-A is serial.

### 5.5 What the Slice 2 leaf plan can already take from here

- The requirement rows of §4 with their spec sections, and the exclusions with owners.
- The register rows: `NFR-502/501 (F-W9-1)` — its NFR-502 half *"needs the HTTP path and
  is Slice 2's"* per [`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md);
  `FR-224 (F-W9-2)` — WK-673's, but see §4's note that DP2 is its input; `03 rating surface
  (F8)` — the phase-boundary row.
- RL-872 already settles Task 2.1's load driver: *"the sustained-load driver that Slice 2's
  Task 2.1 needs is `asyncio` + `httpx` in the same `scripts/` convention"*, stdlib and `httpx`
  only, not a CI gate, result a dated note under [`../research/`](../research/). Its acceptance
  test is stated as a violation: if `locust`, `k6`, `hey` or `wrk` reaches any `pyproject.toml`,
  `uv.lock`, CI workflow or setup instruction for this measurement, RL-872 has been overridden
  and needs a successor record.
- The two measurements Slice 2 owes and their sources: NFR-489 at the full HTTP path
  including the sustained-200 rps test [`../roadmap.md`](../roadmap.md) names separately, and
  NFR-502 re-measured on the real path against WK-668's synthetic p99 0.070 ms.
- **The RBAC trap, which the frozen map walks into** — M4. Read it before writing a permission
  step.
- The evidence sweep the plan must re-run at **its own** pinned commit, not reuse from here:
  `git grep -n "score_one\|QuoteContext\|ScoringResult" -- '*.py'`;
  `git grep -n "SCORE_EXECUTE" -- backend/`; and a `git diff` of
  [`../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md`](../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md) between `9891be1` and
  that commit — **by diff, not by re-listing `## Ruling N` headings**, because an addendum to an
  existing ruling gets no new heading and a heading-based enumeration is structurally blind to
  it (that plan's self-review, third pass).

## 6. Slice 3 — held

### 6.1 Why

`score_batch`'s first parameter is `CompiledBundle` and its output rows carry the same ladder
`score_one` produces. Neither exists (§3.1).

Worse for planning purposes, FR-254 does not merely require the same *bundle* — it requires
*"the identical compiled bundle and code path"*. Slice 3's central acceptance test is a
byte-identical comparison against `score_one` over the same rows, and its central implementation
constraint is that it call the same per-step evaluator.
[`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)'s Global Constraints
require Task 1.4 to *keep* that seam callable — *"in a function `score_batch` can call directly,
not inline it inside `score_one`'s own body"* — but deliberately do **not** name it. That was the
right call there, on RL-874's reasoning that naming a function before it is designed is how a
spec acquires a signature nothing implements. Its consequence here is that **the one symbol
Slice 3 is built around is, by design, not knowable until Task 1.4 merges.**

Two further items are unruled and are Slice 3's own (§9, D3 and D5), and F2 makes the
`LazyFrame` shape a scope question rather than a step.

### 6.2 Release signals for Slice 3

| Signal | Releases | Depends on |
|---|---|---|
| **S-E** — Task 1.4 merged, and its per-step evaluator seam read from the shipped code | the slice | Serial behind Slice 1 |
| **S-F** — D3 ruled: where FR-255's batch abort threshold is configured | the error-handling task | Decision-maker; reaches into `07`, so raise early |
| **S-G** — D5 ruled or filed: chunk/resume mechanism, and whether batch traces at all | the chunking task | Decision-maker |

S-F and S-G are dispatchable today.

### 6.3 What the Slice 3 leaf plan can already take from here

- FR-RATE-36, 37, 38 (batch half) and NFR-493, with their spec sections (§4).
- The `score_batch` signature is **already declared** in §5.2 and is not the planner's to invent
  — copy it, do not retype it. It is the one Slice 3 literal that is safe today, because it is
  specified rather than implemented.
- FR-258's *"Traces are the same structure in real-time and batch"* is a Slice 3 constraint
  as well as a Slice 4 one, and it interacts with D5: whatever batch sampling rules, the
  *structure* is fixed.
- The recovered reasoning behind `chunk_rows: int = 100_000`, and the job-scoped-staging
  resume mechanism, are in
  [`PL-00851-wk-671-five-decision-points-recovered.md`](PL-00851-wk-671-five-decision-points-recovered.md)
  item 3 — recommended, not ruled. The plan cites the ruling that follows it, never the
  recommendation.
- FR-401's *"a cancelled Job leaves no partially-visible artifact"* governs **cancellation,
  not crash-resume** — that distinction is the reason FR-254's "resumable" asks for something
  the generic Job contract does not already give, and a plan that misses it will believe the
  platform already supplies resumability.
- The Job machinery Slice 3 plugs into, verified: `JobKind.SCORE_BATCH` exists with no handler;
  registration is a per-domain module wired from `backend/src/app/worker/entrypoint.py`, whose
  one-loop shape is `backend/src/app/worker/rate_table_handlers.py:57-68`;
  `backend/src/app/worker/handlers.py` is the dispatcher (`HANDLERS`, `register_handler`,
  `handler_for`), not a handler module — see M3 and M5.

## 7. Slice 4 — held, and most blocked

### 7.1 Why

Slice 4 persists and samples `Trace` objects. The Python `Trace` type is Task 1.4's (§3.1); the
shape is specified in §4.5 and in the hand-authored contract, and the contract for this family
is the one carrying known divergences (§3.2).

The decisive item is not the shape but a **measurement**: the frozen map's own exit criterion is
a capacity projection proving NFR-500 *"against the actual serialised `Trace` size Task 1.4
produces, not an estimate"*. That criterion cannot be written into a plan as a number today, and
a plan that supplied one would be supplying the estimate the criterion exists to forbid. This is
[`README.md`](README.md)'s own rule that a measured figure carries the shape it was measured in.

Two more: the persistence shape is queued unruled (D2), and a spec change is *owed before this
slice* (D5's second half).

### 7.2 Release signals for Slice 4

| Signal | Releases | Depends on |
|---|---|---|
| **S-H** — Task 1.4 merged, and a real `Trace` serialised so its size can be measured | the NFR-500 projection | Serial behind Slice 1 |
| **S-I** — D2 ruled: thin Postgres row + blob body, GC-based retention | the persistence task | Decision-maker |
| **S-J** — the FR-258/259 batch-sampling silence resolved as an `OQ-RATE` or a spec change | the sampling task | Decision-maker; carries a [`../open-questions.md`](../open-questions.md) mirror row and a [`../roadmap.md`](../roadmap.md) §10 gate row with a recount |

S-I and S-J are dispatchable today. S-J is the longest-lead item in WK-671 that nobody is currently
working: it is a spec change with a mirror row and a recount, not a one-line ruling.

### 7.3 What the Slice 4 leaf plan can already take from here

- FR-259, NFR-500 and NFR-499's access-control half, with their spec sections (§4).
- NFR-459 is the ≥ 13-month retention authority FR-259 defers to; FR-420's
  reference-counted blob GC with a configurable grace period is the mechanism recovery item 2
  proposes to reuse rather than build.
- `07`'s content-addressed blob store is the persistence tier, and `DislocationRun`'s
  `row + blob` shape in §4.6 is the precedent named for it. **Verify that precedent before
  citing it in a plan**: `largest_movers_blob` was cited by the frozen map as an existing
  precedent and
  [`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)'s correction C4
  found it does not exist in any `.py` file. The real backend precedent that plan names instead
  is `backend/src/app/worker/rate_table_handlers.py`.
- `GET /api/v1/traces?rating_version=&from=&to=` is already in the §5.1 endpoint table, cited to
  FR-259 — the route path is specified, not invented.
- One shape detail worth knowing before the plan is written: the hand-authored contract's
  `Trace` (`scoring.schema.json:64`) types `steps` as an array of **inline anonymous items**;
  there is no named `TraceStep` `$def`, and `git grep -n "TraceStep"` returns nothing anywhere.
  Whether Task 1.4's Python `Trace` names that item type is Task 1.4's choice, and Slice 4's
  row-versus-blob split may want it named. A question for the Slice 4 plan to check against the
  shipped type, not to assume either way.
- No `JobKind` member begins with `TRACE` (`jobs.py:42-63`, 22 members). The only `TRACE_`
  symbols in the repo are request-tracing constants — `backend/src/app/observability/trace.py:31`
  `TRACE_ID_PATTERN` and `middleware.py:26` `TRACE_HEADER` — an unrelated meaning of the word
  that a grep for "trace" will surface first.

## 8. Slice-design proposal — a proposal, not a change

The frozen map is left standing ([`README.md`](README.md): *"a filed plan is a record, not an
instruction"*). These are recorded for the lead to accept, amend or reject, and for the next map
revision if there is one.

**P1 — Slice 2 is cut across three different release signals, and one of its tasks is ready
now.** Task 2.3's dependency surface is complete at `9891be1` (§3.3) and its only blocker is a
ruling; Tasks 2.1 and 2.2 are serial behind Task 1.4. As cut, Task 2.3 inherits Task 2.1's wait
for no reason other than sharing a slice number. **Recommendation:** rule DP2 now, and let Task
2.3 be planned and executed as its own slice in parallel with Slice 1, rather than after it.
This is a sequencing change, not a scope change — the same shape the lead already accepted for
Slice 1 when Tasks 1.1–1.5 were run as five sequential slices with the frozen map unedited. **The
lead's call, not the planner's.**

**P2 — the map's dependency row for Slice 4 is incomplete in one direction.** The sequencing
table gives Slice 4 `Depends on: 1`. That holds for the *unit* of work — a sampling decision
function, a row table, a persistence service and a `GET` route can all be built and tested
against synthetic `Trace` objects. It does not hold for FR-259's own words, *"in production,
traces are sampled"*: nothing produces a trace into that store until a scoring call site exists,
which is Slice 2's endpoint or Slice 3's batch handler. **Recommendation:** keep the dependency
row as it is and add an end-to-end criterion to whichever of Slice 2 or 3 lands second — a
sampled trace produced by a real scoring call and read back through `GET /api/v1/traces`.
Re-sequencing Slice 4 behind Slice 2 would serialise work that does not need to be serial.

**P3 — [`../roadmap.md`](../roadmap.md)'s WK-671 row states its scope as the numeric range
`FR-250, FR-251, FR-253, FR-254, FR-255, FR-256, FR-257, FR-258, FR-259` plus FR-252, and FR-243 is inside WK-671 and outside that range.**
FR-243 (`03` §3.4) is what defines `CompiledBundle` as a distinct runtime type; Slice 1 Task
1.3 discharges it, and
[`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)'s correction C5 added
it to that plan's coverage table. `git grep -n "FR-243" -- docs/` at `9891be1` returns no
workstream row in [`../roadmap.md`](../roadmap.md). This is the same mechanism
[`../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md`](../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md) already filed for FR-224 and
FR-218 — *"neither appears in any `W_` row's stated scope"* — whose maintainer acceptance is
still pending there. **Recommendation:** fold FR-243 into that pending item rather than
opening a second one, so one acceptance settles the class. A roadmap edit is the lead's or the
decision-maker's; this document proposes and does not apply it.

## 9. Decision points — one raised here, five restated with their slice

Every item below is the decision-maker's. Recommendations are the planner's and bind nothing.

### D4 (new) — where does a loaded `CompiledBundle` live between HTTP requests?

**Nobody owns this, and it falls in a gap between two rulings.**

- RL-876 rules that the *refresh trigger* is WK-674's and gives Task 1.3 two properties so WK-674
  still has a choice: `CompiledBundle` exposes the `content_hash` of the `Bundle` it was loaded
  from, and **`load_bundle` is pure with respect to the cache** — *"it consults no cache,
  registers itself in no global, and starts no background task"*, partly because
  `.importlinter` forbids `pricing_core` from importing `redis` at all, so any cache tier must
  live above it in `backend/`.
- RL-876 also records that **Slice 2 has zero hits** for `redis`, `cache`, `warm`, `refresh`,
  `poll` and `slot`. So the frozen map schedules no work anywhere that builds the tier RL-876
  says must exist above `pricing_core`.
- Meanwhile NFR-497 is allocated to **Slice 2** and reads *"degrading to the last-known-good
  cached bundle if metadata storage is unavailable"* — a requirement that presupposes a cache in
  the scoring path — and NFR-489's 50 ms p99 has to absorb whatever the route does per
  request. RL-874 records that `predict_gbm` re-loads the booster on every call today, so
  "load it per request" is not a small cost.

**The question:** does Slice 2's Task 2.1 build a per-worker holding tier for loaded bundles, and
if so, how much of one?

- *(a) None — resolve, fetch the `Bundle` from the blob store and `load_bundle` per request.*
  Simplest and smallest. Puts blob-store I/O and a booster load inside the request, which reads
  against both NFR-489 and the spirit of NFR-491, and leaves NFR-497's
  "last-known-good cached bundle" with nothing to name.
- *(b) A per-worker in-process slot in `backend/`, keyed by `content_hash`, bounded, populated on
  first use via `load_bundle`, with no refresh trigger of any kind.* Satisfies NFR-497 by
  construction, keeps the seam on the `backend/` side of ADR-703 where RL-876 puts it, and
  leaves every refresh mechanism — push, poll, pub/sub — open for WK-674, which is what RL-876
  asks Slice 1 to preserve. Costs a bounded-cache decision (size, eviction) that is Slice 2's.
- *(c) A Redis tier holding serialised `Bundle` bytes, deserialised and loaded per request.*
  Matches `07` FR-422's naming of Redis as the cache, but RL-867 already rules that
  `CompiledBundle` never round-trips Redis, so this pays deserialise plus booster load on every
  request and buys only distribution.

**Recommendation: (b), scoped to the existence of a slot and nothing more** — no refresh, no
poll, no pub/sub, no "current hash for env X" pointer, all of which RL-876 keeps as WK-674's. An
acceptance test stated as the violation it must make expressible: **a test that fails if
`load_bundle` consults the slot, registers in a global, or starts a task** — RL-876's second
property, which is currently written in a ruling and in no acceptance block anywhere.

**Rules before Task 2.1 is planned.** Does not block Task 2.3, Slice 3 or Slice 4.

### The five already queued, restated with their release signal

Listed so that nothing reads as overlooked. Each is named in
[`../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md`](../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md)'s own queued table or in
[`PL-00851-wk-671-five-decision-points-recovered.md`](PL-00851-wk-671-five-decision-points-recovered.md); this
adds the slice-release mapping, not new options.

| Ref | Item | Slice | Signal | Standing recommendation, and whose |
|---|---|---|---|---|
| **DP1** | Default-live resolution for `POST /api/v1/score` | 2 (task 2.2) | S-B | Map plan recommends (b) — defer to WK-674 as a named register deferral |
| **DP2** | FR-257's approval gate ahead of WK-672/WK-673 | 2 (task 2.3) | S-C | Map plan recommends (a) — build the mechanism now. **Also a WK-673 input**, per FR-224's own text |
| **D2** | Trace persistence: thin Postgres row + blob body, GC-based retention | 4 | S-I | Recovery item 2's option (b) |
| **D3** | Where FR-255's batch abort threshold is configured | 3 | S-F | Recovery item 4 — a workspace setting on FR-448's precedent, with a per-request override. Reaches into `07` |
| **D5** | FR-258/259 state no **batch** sampling default | 3 and 4 | S-G, S-J | A spec silence, not a choice inside a requirement. Needs an `OQ-RATE` (next free `OQ-620`) or a spec change, with its [`../open-questions.md`](../open-questions.md) mirror and a [`../roadmap.md`](../roadmap.md) §10 gate row |

## 10. Corrections to the frozen map

The map is left standing; these are recorded so a reader of both is not misled.

**M1 — the map's Slice 2 requirement line omits NFR-499's second half.** It lists
"NFR-489 (full path + sustained load), 9, 11, 13" for Slice 2 and, separately, NFR-499 is
also what makes Slice 4's traces access-controlled — the map's Slice 4 line says so in prose
(*"access-control test (traces are access-controlled per NFR-499)"*) without listing the id
in its Requirements line. §4 above lists it against both slices.

**M2 — the map's Slice 4 Files line understates what Slice 4 has to decide.** It reads *"sampling
policy … applied to Task 1.4's already-captured `Trace` objects; persistence to the blob store"*,
which reads as a settled mechanism. The thin-row/blob split and the GC-based retention were
recovered as an unruled recommendation
([`PL-00851-wk-671-five-decision-points-recovered.md`](PL-00851-wk-671-five-decision-points-recovered.md) item
2) and queued as unruled
([`../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md`](../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md)); D2 above is that item.

**M3 — Slice 3's map line calls `handlers.py` the registration site.** It says to register the
`JobKind.SCORE_BATCH` handler in `backend/src/app/worker/handlers.py`. At `9891be1` that module
is the dispatcher — `HANDLERS`, `register_handler`, `handler_for` — and every actual handler
lives in a per-domain module (`data_handlers.py`, `model_handlers.py`,
`rate_table_handlers.py`), each wired from `backend/src/app/worker/entrypoint.py:41-46`. Same
class of error as the map's `largest_movers_blob` citation, which
[`PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`](PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md)'s correction C4 found
does not exist in any `.py` file. **Which file Slice 3 uses is still a fact about the tree at
Slice 3's own commit, and this document deliberately does not freeze it** — flagged so the
Slice 3 planner greps rather than copies.

**M4 — the map's Task 2.1 instruction to "grant `Permission.SCORE_EXECUTE` to the Service
Account role (currently granted to none)" describes a mechanism that does not exist, and
following it breaks a passing test.** Verified at `9891be1`: `SCORE_EXECUTE` and `SCORE_BATCH`
are `Permission` members (`permissions.py:58`, `:59`) and are granted by no entry in
`BUILTIN_ROLES` (`permissions.py:131-150`) — and that is **enforced on purpose**, by
`backend/tests/test_rbac.py:102-108`:

```python
@pytest.mark.req("FR-347")
def test_no_builtin_role_grants_a_service_account_permission_to_a_human() -> None:
    for slug, permissions in BUILTIN_ROLES.items():
        assert Permission.SCORE_EXECUTE not in permissions, slug
        assert Permission.SCORE_BATCH not in permissions, slug
```

The marker is the point: the exclusion is **FR-347**'s — *"Service Accounts (for Consumer
Systems) hold scoring permissions only, scoped to named environments … A Service Account can
never hold an approval or deployment permission"* ([`../specs/06-governance.md`](../specs/06-governance.md)
`:83`) — and the test asserts its converse. There is no "Service Account role" in
`BUILTIN_ROLES` to grant anything to; service accounts take a caller-specified permission list
instead, `backend/src/app/api/service_accounts.py:174` passing `permissions=body.permissions`
straight through with no role lookup.

So an executor following the map's wording would add `SCORE_EXECUTE` to a builtin role, turn
that test red, and read the red as their own defect — when it is the requirement working.
**Stated as the predicted failure by cause, not by status:** the assertion above fails naming
the offending role slug. A *different* RBAC failure, or a 403 from an integration test, means
something else is wrong and is a plan defect rather than the expected red. **Not resolved
here:** the grant path is a Service Account rather than a role, but FR-347 also scopes it *to
named environments*, and the Environment entity is FR-428 — WK-674's, the same entity DP1
turns on. Whether Slice 2's RBAC test can express "a scoped Service Account may call it" before
WK-674 exists is a question for the Slice 2 plan, and it may prove to be DP1-shaped rather than
independent of it.

**M5 — the 202 precedent the map points Slice 3 at is conditional, not unconditional.** The map
tells Task 1.2 to match *"the already-existing `RATE_TABLE_DIFF` 202 pattern"*, and Slice 3
inherits the citation for its own `POST /api/v1/score/batch`. At `9891be1` that route
(`backend/src/app/api/rate_tables.py:342`) submits a Job only on the parquet-eligible path; the
row-backed path stays synchronous. FR-253 specifies `POST /api/v1/score/batch` as a Job
unconditionally, so the precedent is a shape to copy from, not a branch structure to copy.

## 11. Self-review

**1. Coverage.** Every requirement the frozen map allocates to Slices 2, 3 and 4 appears in §4
with its spec section and its slice, listed individually rather than as a range. Exclusions are
named with owners. Every item in
[`../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md`](../rulings/RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md)'s queued table that
belongs to Slices 2–4 appears in §9's table; the one entry of that table not carried here is the
`model_schema.money.to_minor` home, which belongs to no slice and is marked *"not urgent"* there.
Of the five map corrections in §10 and the two findings in §3.4, five are also attached to the
slice they affect in §5–§7 so they are not reachable only from the section that raises them
(M3 and M5 in §6.3, M4 in §5.5, F1 in §5.4, F2 in §6.2). Two are not: **M1** is carried instead
by §4's requirement table, which lists NFR-499 against both slices, and **M2** by §9's D2
row. Stated rather than smoothed over, because "each" would have been the kind of quantifier
that reads as checked and is not.

**2. Placeholder scan.** No TBD. Three tasks and two slices are described as held, and each
states what releases it and who can send that signal — which is the honest state of a blocked
slice, not a placeholder. Three things are deliberately left unwritten and each says why: D4's
option (b) sizing and eviction policy, F1's resolution, and M4's grant mechanism — all three
downstream of a ruling this document is not allowed to make.

**3. Consistency.** `CompiledBundle`, `load_bundle`, `score_one`, `score_batch`, `QuoteContext`,
`ScoringResult` and `Trace` are used under the names §5.2 declares, copied rather than retyped.
`RatingVersionEvidence`'s four field names are quoted from
`packages/model-schema/src/model_schema/rating.py:88-96`, not from the requirement that
describes them.

**4. No literal is frozen that this document could not verify.** Every path and line number in
§3.3 was read at `9891be1`. Where a literal is unverifiable because it does not exist, this
document says so and names the task that will create it — it does not supply a sample. The one
place a future planner might be tempted to copy from here is §3.3's table, and §5.5, §6.3 and
§7.3 each say to re-run the sweep at the plan's own commit instead.

**5. Absence claims are stated with the command that produced them**, because an absence claim
is only as good as the pattern that failed to match. §3.1's grep is a full-class sweep over
`'*.py'` with an alternation of all six names, not a per-name spot check, and it is reported
with its one hit rather than as a bare zero — a zero with no hits at all would have been the
shape of a broken pattern rather than a true negative.

**6. What this document decides: nothing.** D4 is raised with options and a recommendation and
is the decision-maker's. F1 and M4 are raised with their evidence and **no** recommendation,
because neither is a taste call — F1 turns on a requirement's amended cost premise and M4 on
FR-347's scope, and both are the decision-maker's to read. P1, P2 and P3 are proposals and are
the lead's or the decision-maker's. The verdicts in §1 are a planner's judgement about
plannability, which is this role's, and they are reversible the moment a signal in §5.4, §6.2 or
§7.2 fires.

**7. The judgement could be wrong in one direction, and here is the direction.** If Task 1.4's
merged shape turns out to match `scoring.schema.json` and §4.4 exactly except for `purpose`,
then a Slice 2 plan written today would have been mostly right, and holding cost time. That is
the risk taken, and it is taken deliberately: a plan that is mostly right is the failure mode
[`README.md`](README.md)'s conventions 1 and 3 exist to prevent, because an executor cannot tell
which part was the wrong part. The asymmetry decides it — a held slice costs a delay, a wrong
frozen literal costs an executor's whole task and reads as their defect.

## 12. Verification

- **Tree:** `9891be1`, `git rev-parse HEAD` equal to `git rev-parse origin/main`, `git status
  --porcelain` empty, after `git fetch origin`. Every grep and line number above was run there.
- `gh pr list --state open` returns empty at that tree — nothing in flight that could change the
  absence claims between the sweep and this filing.
- **The absence sweep, reproducible:**
  `git grep -n -E "QuoteContext|ScoringResult|score_one|score_batch|CompiledBundle|load_bundle"
  -- '*.py'` → one hit, `scripts/audit-docs.py:499`, a docstring.
  `ls packages/pricing-core/src/pricing_core/rating/` → `__init__.py`, `compile.py`.
- **The stale-contract claim, checked rather than cited:** `scoring.schema.json:12` read
  directly, four enum members; `03-rating-engine.md` §2 `:63` read directly, five. The register
  row F27 was read to the sentence that carries the claim, not only to its heading.
- **F1's dependency claim was checked in all three places a dependency can hide**, because two
  of them would have produced a false negative on their own: `git grep -n "orjson" -- '*.toml'`
  (declaration), `grep -c "orjson" uv.lock` → `0` (resolution, including transitive), and
  `git grep -n "ORJSONResponse" -- backend/` (use). A `.toml` sweep alone cannot distinguish
  "not declared" from "not present"; the lock count is what makes this a true absence rather
  than an undeclared transitive.
- **M4 was checked against the test that enforces it**, not only against `BUILTIN_ROLES` — an
  absence in a mapping table is consistent with both an oversight and a deliberate exclusion,
  and only the test distinguishes them. It is deliberate.
- **The ids** were re-derived by `grep -o "FR-RATE-[0-9]\+" docs/specs/03-rating-engine.md | sort
  -t- -k3 -n | tail`, and the same for `NFR-RATE-` and for `OQ-RATE-` across the spec and
  [`../open-questions.md`](../open-questions.md) — not carried forward from an earlier plan's
  line.
- **The evidence sweep behind §3.3 and §3.4 was fanned out read-only to a subagent and every
  load-bearing claim re-checked here before it was written down** — `delivery-process.md` §8
  permits the fan-out; [`../../CLAUDE.md`](../../CLAUDE.md) §12 keeps the judgement in the main
  thread. The four claims this document rests hardest on — the six-name absence, the
  `scoring.schema.json` enum, the `orjson` lock count, and the `test_rbac.py` assertion — were
  each run again directly rather than adopted.
- `python3 scripts/audit-docs.py` — clean. **And it was seen to fail on this file first**, which
  is the only reason its pass is worth anything ([`../../CLAUDE.md`](../../CLAUDE.md) §13: a
  check that has never printed a failure has not been tested). The first run printed
  `FAILED (2)`, naming both ids on this document's own `Next free:` line as *referenced but
  never defined*. The cause was not a wrong id: the marker had hard-wrapped between `Next` and
  `free:`, so the exemption — which covers *the rest of that line* — applied to a line the ids
  were no longer on. Putting the marker and its ids on one physical line cleared it.
- **The fix then failed a second time, for a second-order form of the same rule**, and this is
  the part worth carrying: the paragraph above originally quoted the audit's failure message
  verbatim, and the message contains the ids. A quotation of the failure re-creates the
  condition, on a line with no marker on it. **A failure message naming an undefined id cannot
  be quoted literally in a governed document** — say what it named, do not reproduce it. Both
  facts are written into [`README.md`](README.md)'s second convention in this same commit, per
  [`../../CLAUDE.md`](../../CLAUDE.md) §12's rule that a discovered non-obvious procedure is
  recorded with the work rather than after it.
- This document mints no `FR-`/`NFR-`/`OQ-` id and declares no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no [`../roadmap.md`](../roadmap.md)
  §10 gate row. D5 is the item that *will* owe both; it is queued, not taken, here.
