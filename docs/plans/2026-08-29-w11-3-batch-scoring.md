# W11 Slice 3 — batch scoring: the pure transform, the checkpointing handler, and the route

> **For agentic workers:** REQUIRED SUB-SKILL: use `subagent-driven-development`
> (recommended) or `executing-plans` to implement this plan task-by-task, plus
> `test-driven-development` and `git-hygiene` — the three skills
> [`.claude/roles/executor.md`](../../.claude/roles/executor.md) makes mandatory for this
> role. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-rate a Dataset Version against one or more Rating Versions as a Job — chunked,
progress-reporting, and resumable — producing one content-addressed parquet per rating version,
through the same post-evaluation tail the real-time path uses.

**Architecture:** Four tasks, split along the line Ruling 31 draws through the middle of this
slice. **3A** is `score_batch` in `pricing-core`: a pure, chunked, lazy transform that holds no
durable state. **3B** is the `score.batch` handler, which owns everything durable — the
content-keyed chunk manifest, the scratch parts, the skip-on-re-entry, the abort threshold and
the final parquet. **3C** is the route. **3D** measures NFR-RATE-5. The 3A/3B split is not a
convenience: ADR-0001 makes it structural, and `lint-imports` enforces it.

**Tech Stack:** `pricing-core` (standalone, zero infrastructure imports); Polars for the frame;
Celery/Redis Job machinery; the content-addressed blob store for the output, and **scratch
storage outside it** for chunk parts (Ruling 31 §4).

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — §3.7 (FR-RATE-36, 37,
38), §5.1 (the `/score/batch` row, `:517`), §5.2 (`score_batch`'s signature and the corrected
shared-tail passage, `:676-690`), §9 (NFR-RATE-5). Platform: FR-PLAT-8 (progress), FR-PLAT-9
(cancellation), FR-PLAT-14 (Job parameters retained), FR-PLAT-20 (blob GC), FR-PLAT-43/45
(settings), FR-PLAT-64 (key release on failure).

**Slice source:** [`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md), Slice 3. **That file
is frozen and is not edited by this one**; three of its lines are corrected below.

**Rulings this plan rests on, cited by number and not re-argued:**
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md)
Rulings **31** (D6) and **32** (§5.2's false shared-evaluator claim);
[`2026-08-29-w11-slices-3-4-rulings.md`](2026-08-29-w11-slices-3-4-rulings.md) Rulings **24**
(abort threshold) and **25** (no batch sampling);
[`2026-08-29-w11-prework-rulings.md`](2026-08-29-w11-prework-rulings.md) Ruling **5**
(`score_batch` stays `def`); [`2026-08-29-w11-slices-2-4-rulings.md`](2026-08-29-w11-slices-2-4-rulings.md)
Ruling **18**, whose answer this slice reuses — see C3; and
[`2026-08-29-w11-slice-parallelism-ruling.md`](2026-08-29-w11-slice-parallelism-ruling.md)
Ruling **33**, which governs when this slice may be built relative to Slices 2 and 4.

**One correction to a ruling was filed from here** — F-W11-3-1, against Ruling 31 §6's precedent
citation. It was **accepted, and answered by an addendum that also found a second error and
rejected this plan's proposed workaround**. See *Corrections after filing* immediately below,
which is the section an executor should read before Task 3B.

**Process:** [`../process/delivery-process.md`](../process/delivery-process.md) §6, §8, §9.

**Highest ids in use, re-derived at `c79a39d` by scanning
[`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) and
[`../open-questions.md`](../open-questions.md):** FR-RATE-65, NFR-RATE-14, OQ-RATE-7.
Next free: `FR-RATE-66`, `NFR-RATE-15`, `OQ-RATE-8`.

**This plan mints none of them** and registers no new error code.

---

## Corrections after filing (2026-08-29, after `9942800`; this plan merged at `02679d0`)

**Two operative instructions in this plan were wrong and are corrected in place**, because a
plan is an instruction set and an executor who reads a wrong step does the wrong thing. What was
believed is preserved here rather than deleted, per [`README.md`](README.md).

The source is the **addendum to Ruling 31** (`fb56dc6`, PR #424), filed in response to this
plan's F-W11-3-1. **Ruling 31's decision is unchanged; two of its citations were wrong, and so
was this plan's proposed way round the first.**

**Error 1 — the test precedent does not exist. Raised here, confirmed, and this plan's
workaround refused.** F-W11-3-1 correctly found that `backend/tests/test_worker.py` drives
handlers through `execute_job` (17 call sites) and never invokes a handler function. The
addendum explains how the original error was made — the file's docstring says `execute_job` is
exercised *"directly rather than through a broker"*, and *"directly"* there means **without
Celery and Redis, not at handler level**; the word was read on the wrong axis.

**But this plan's proposed reconciliation was rejected.** Task 3B Step 1 first told the executor
to submit two Jobs and call `execute_job` on each, reasoning that a *different* Job id leaves the
row `QUEUED` so the guard never fires. That reasoning is factually correct and is **not** the
route: the addendum's disposition is that the test *"invokes the handler function itself …
and must not route either call through `execute_job`"*. Step 1 is corrected. **A planner does
not settle a decision-maker's test-shape call by finding a defensible alternative** — which is
what proposing that route amounted to, however well-evidenced.

**Error 2 — the guard was attributed one level too high, and this plan inherited it.** Ruling 31
§1 said *"`run_job` transitions the Job to `RUNNING` … and guards its own entry"*, and this plan
repeated it. Both should name **`execute_job`** (`tasks.py:79`). Re-verified here at `fb56dc6`:
`execute_job` is the `async def` at `:79` holding both guards (`:94`, `:103`); `run_job` is the
Celery task at `:266`, nested inside `create_worker`, a *"five-line adapter"*. The described
behaviour was right and reaches the guard transitively — only the name was wrong. The addendum
records the mechanism, which is the reusable part: the body was read with `sed -n '80,140p'`,
starting one line below the `def`, so **correct behaviour was attached to a guessed name**.

**Gained, not just fixed: the absent precedent is a scope finding.** Because nothing in this
platform has ever needed to run the same Job twice, there is no precedent for invoking a handler
directly — which *corroborates* Ruling 31 §1 rather than undermining it. It is now recorded in
*Verified facts* as scope: **Task 3B Step 1 writes a new test shape, it does not follow one.**

*Not carried into this section:* Ruling 34 (`fa2257c`) lands on Slice 4's design, not this one.


---

## Acceptance standard for the slice as a whole

`delivery-process.md` §3 requires one that is explicit and testable. Slice 3 is accepted when
**all seven** hold, each by a command a fresh reviewer can run.

1. **FR-RATE-37's byte-identity, proven through the shared tail.** `score_batch` and `score_one`
   over the identical rows produce **byte-identical** premiums, and the mechanism is that both
   reach `build_scoring_result` with the same engine result. Not "equal-looking": compare the
   serialised ladders.
2. **Resumability, proven by work *not repeated*.** Drive the **handler** directly — invoke,
   interrupt mid-chunk, re-invoke with the same parameters **under a different Job id** — and
   assert **both**: (i) chunks completed before the interruption are **not re-scored**,
   observable by counting chunk invocations or rows scored on the resumed call and **never by
   inspecting the output**; and (ii) the final parquet is byte-identical to an uninterrupted run
   over the same input. **Clause (i) is the one that distinguishes this from full restart** — a
   test asserting only (ii) passes under option (a) and makes "resumable" vacuous.
3. **The checkpoint is keyed on content, not on the Job.** The manifest key is the compiled
   bundle's content hash, the Dataset Version reference and the chunk index. **Overridden if a
   build keys a checkpoint on a Job id, puts checkpoint state in `pricing-core`, or uses
   `JobRow.progress` as the ledger** — Ruling 31 §7.
4. **The abort threshold behaves in both directions** (Ruling 24): a batch request carrying a
   threshold **above** the resolved workspace setting is **refused**; a run whose failure rate
   crosses the effective threshold **aborts recording both the threshold in force and the
   observed rate** on the Job. With the setting unset, there is no rate-based abort and the
   per-error-type counts still accrue.
5. **Errors are typed per category and do not abort individually** (FR-RATE-38): the run reports
   counts and samples per error type, and one bad row does not end the run below the threshold.
6. **No batch trace enters the production stream** (Ruling 25): `score_batch` takes no sampling
   parameter, and nothing this slice writes is returned by `GET /api/v1/traces`.
7. **NFR-RATE-5 is measured** — ≥ 1 M risks/hour/worker — and written into a dated note under
   [`../research/`](../research/), with the shape it was measured in.

**Not in this slice, and not a gap:** the real-time endpoint is Slice 2's; trace sampling and
persistence are Slice 4's; **the re-run trigger that would invoke a resumed batch is nobody's in
W11** — see the coverage table's FR-RATE-37 row, which is the single most important line in this
plan.

## Global Constraints

- **Money is integer minor units or `Decimal`, never `float`** — [`../../CLAUDE.md`](../../CLAUDE.md)
  §7. A parquet column holding premium is an integer minor-unit column.
- **`score_batch` holds no durable state and stays plain `def`** (Rulings 31 §3 and 5). It takes
  a frame and returns a frame. **It may not acquire a Job identity, an output location or a
  resume point**, and `.importlinter`'s `core-has-no-infrastructure` (ADR-0001/DEP-3) makes that
  structural rather than stylistic — `lint-imports` runs in the gate.
- **The handler owns everything durable**: manifest, scratch, skip, threshold, output.
  FR-PLAT-8 already allocates this — *"`pricing-core` reports through the injected
  `ProgressCallback` (ADR-0001); the worker translates it into Job state."*
- **Chunk parts are scratch, written outside the content-addressed store** (Ruling 31 §4), and
  carry a creation time so an age-based sweep can collect them. Only the concatenated output
  enters the blob store. A part inside the blob store would be permanently uncollectable while
  referenced, and would sit for the 30-day grace period after every crashed run.
- **A negative test for every invariant introduced**, marked `@pytest.mark.req("<id>")`.
- **Worktree hygiene:** your own worktree, never `git checkout`/`git switch` outside it.
- **The gate, both halves, run locally before every push:**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
```

---

## Verified facts at `c79a39d`

### The shared tail, and what it is not

Ruling 32 corrected `03` §5.2 in place. The spec now reads: *"`score_one` and `score_batch`
share the identical **post-evaluation tail** — `build_scoring_result`, the one function turning
an already-evaluated engine result into a `ScoringResult`."* Its previous wording named an
*"identical step evaluator"*, **which does not exist and was never going to**: per-step
evaluation happens inside the ZEN engine, not in this repository, and
`pricing_core.rating.score` exports exactly `__all__ = ["build_scoring_result", "score_one"]`.

```python
def build_scoring_result(
    bundle: CompiledBundle,
    ctx: QuoteContext,
    rating_version_ref: ArtifactRef,
    result: Mapping[str, Any],
    engine_trace: Mapping[str, Any] | None,
) -> ScoringResult
```

**This is the whole of what FR-RATE-37's byte-identity means here.** `score_one` reaches the
engine through `async_evaluate()`; `score_batch` stays plain `def` and uses the engine's
synchronous path. Different methods — so the proof is the tail, not the call.

### The signature, published and not this plan's to change

`03` §5.2:606-608:

```python
def score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, *,
                chunk_rows: int = 100_000,
                progress: ProgressCallback | None = None) -> pl.LazyFrame
```

One `bundle`. **FR-RATE-36 asks for *"one or more Rating Versions"*** — so multiple versions is
the *handler* looping bundles, not a signature change. Do not widen this signature.

### Two shapes that do not exist, and one that must not be assumed

- **`ScoringResult` has no `quote_id`.** Ruling 31 §3 establishes it: the field lives only on the
  optional input `QuoteContext` and the optional `Trace` sub-object, in both
  `docs/contracts/schemas/scoring.schema.json` and `model_schema.scoring`. FR-RATE-36 requires
  the output carry *"the quote key"* — **so the key must be carried through from the input
  frame; it cannot be read off the result.** This is the detail most likely to be discovered
  late.
- **`pl.LazyFrame` has no precedent in this repository.** Re-derive with
  `git grep -c "LazyFrame" -- '*.py'`; it returned zero repo-wide at the previous two commits
  while the same pattern with no pathspec hit five documents. The type is specified and has never
  been used here. **This is a scope fact, not a step** —
  [`README.md`](README.md)'s *"a missing neighbour is a scope finding"*.
- **Nothing re-runs a crashed Job.** Ruling 31 §1's behaviour, with its attribution corrected by
  the addendum (see *Corrections after filing*, Error 2) and re-verified here at `fb56dc6`:
  **`execute_job`** (`backend/src/app/worker/tasks.py:79`) makes the `RUNNING` transition and
  holds both guards — `if row.status in TERMINAL_STATUSES` (`:94`) and
  `if row.status is not JobStatus.QUEUED` (`:103`) — so a crashed worker leaves the row
  `RUNNING` and the redelivered message is a no-op. **`run_job` is not where the guard lives**:
  it is the Celery task at `:266`, nested inside `create_worker`, whose own docstring calls it
  *"Adapter: bind the trace, then run the lifecycle."* `VALID_TRANSITIONS`
  (`model_schema/jobs.py:106-114`) gives `SUCCEEDED`, `FAILED` and `CANCELLED` each
  `frozenset()`; there is no retry endpoint and no reaper; `Job.retries` is never incremented
  and `JobError.retryable` is never read.
- **The resumability test has no precedent in this repository, and that is a scope fact.**
  Nothing here has ever invoked a Job handler function directly: `backend/tests/test_worker.py`
  drives handlers through `execute_job` at every one of its call sites. **Task 3B Step 1
  therefore writes a new test shape for this suite rather than following one**, and should be
  budgeted as such. Per the addendum, the missing neighbour is also *corroboration* for Ruling
  31 §1 — there is no precedent for running a handler twice because nothing in this platform has
  ever needed to run the same Job twice. [`README.md`](README.md)'s *"a missing neighbour is a
  scope finding"*.

### What exists, and what does not

| Thing | State at `c79a39d` |
|---|---|
| `score_batch` | **Does not exist.** Re-derive: `git grep -n "score_batch" -- '*.py'` |
| `build_scoring_result`, `score_one` | Exist — `pricing_core/rating/score.py`, the module's entire public surface |
| `JobKind.SCORE_BATCH` | Exists — `model_schema/jobs.py:56`, value `"score.batch"`, **already queue-routed** to `JobQueue.SCORING` (`backend/src/app/platform/jobs.py:75`). **No registered handler** |
| `Permission.SCORE_BATCH` | Exists — `model_schema/permissions.py:59`. **Granted by no builtin role, deliberately** (FR-GOV-6), asserted by `backend/tests/test_rbac.py:101-107` |
| `POST /api/v1/score/batch` | No route. Specified at `03` §5.1:517 as **202** → Job |
| `rating.batch_abort_failure_rate` | Does not exist. Ruling 24 rules the name and the shape |
| Handler modules | Per-domain modules wired from `backend/src/app/worker/entrypoint.py`. `backend/src/app/worker/handlers.py` is the **registry** (`HANDLERS`, `register_handler`, `handler_for`), not a handler module |
| `JobProgress.update()` | **Silently drops writes inside a one-second throttle** (`backend/src/app/worker/progress.py`, `_MIN_WRITE_INTERVAL_S: Final = 1.0`), and nothing reads a Job's prior progress back. Forward-only, lossy by design — **excluded as a ledger candidate** (Ruling 31 §7) |
| A chunked/streaming loop over a dataset | **No precedent anywhere in backend or pricing-core source.** Task 3A's chunk loop is the repository's first. A scope fact, like `LazyFrame` |

### The shapes to mirror, read rather than described

**Handler signature and registration** — `backend/src/app/worker/rating_handlers.py`, the
nearest neighbour (Task 1.2 added it for `RATING_COMPILE`):

```python
def _rating_compile(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:

def register_rating_handlers() -> None:
    for kind, handler in ((JobKind.RATING_COMPILE, _rating_compile),):
        if kind not in HANDLERS:
            register_handler(kind, handler)
```

`entrypoint.py` calls `register_data_handlers()`, `register_model_handlers()`,
`register_rate_table_handlers()` and `register_rating_handlers()` in one block — add yours there.

**`ProgressCallback`** — `packages/pricing-core/src/pricing_core/progress.py`, a
`@runtime_checkable` `Protocol` with **two** methods: `update(fraction, stage, **counters)` and
`check_cancelled()`, the latter raising `JobCancelled`. **`check_cancelled` is how 3A honours
FR-PLAT-9** — it is not an extra you have to invent.

**Job parameters** reach a handler as `row.parameters` merged with an injected `job_id`. Routes
build them with `job_identity(caller)` (`backend/src/app/api/deps.py:319-330`, giving
`workspace_id` and `actor`) plus their own keys — see the `RATING_COMPILE` submission in
`backend/src/app/api/models.py`.

**Parquet, one idiom throughout**: an in-memory `io.BytesIO()` buffer to and from bytes held as
a blob, `compression="zstd"` on write, never a filesystem path outside tests. The closest
worked example is `data_handlers.py`'s split materialiser:

```python
buffer = io.BytesIO()
selected.write_parquet(buffer, compression="zstd")
ref = await blob_store.put(session, buffer.getvalue(), PARQUET_MEDIA_TYPE)
```

**Reading a Dataset Version's rows**: `_read_tables(session, blob_store, version)` in
`data_handlers.py` iterates `version.tables` and does `pl.read_parquet(io.BytesIO(...))` per
table. There is **no `scan_parquet` anywhere in the repository** — so a genuinely lazy
`LazyFrame` source is something 3A introduces, not something it inherits.

**Byte-identity assertions** have three precedents to mirror rather than invent:
`backend/tests/test_blobs.py`'s `test_identical_content_is_stored_once`,
`backend/tests/test_data_nfrs.py`'s `test_identical_tables_across_versions_are_stored_once`
(which asserts on parquet blobs specifically), and
`backend/tests/test_validation_reports.py`'s `test_a_stored_report_reads_back_byte_identical`.

### The register rows this slice must honour

`delivery-process.md` §9. All rating-bearing rows are listed; a row skipped silently is
indistinguishable from one that does not exist.

| Row | Bearing on Slice 3 |
|---|---|
| `03 rating surface (F8)` | The phase-boundary row; W11 discharges its scoring quarter |
| `NFR-RATE-13/14 (F-W9-1)` | Slice 1's and Slice 2's halves. Not this slice's |
| `Error codes across the spec/code boundary (F29)` | Open, owned. This slice registers no new code |
| `03 rating shapes vs hand-authored contracts (F27)` | Owner decided (Ruling 29): the §14 review at W11's close. **Bears indirectly** — if the batch output schema gains a published contract it joins that comparison |
| `Ruling 16's acceptance-test premise (F32)` | Resolved; Slice 2's. Not this slice's |
| `FR-RATE-61 (F-W9-2)`, `FR-RATE-25 (F-W9-3)` | W13's and Task 1.2's. Not this slice's |
| The six W10 rows, `F26`, `F28`, `F30`, `F31`, `F33` | W10's, W15's, or process rows. Not this slice's |

**Nothing in the register blocks Slice 3.**

---

## Corrections to the frozen map

The map is left standing ([`README.md`](README.md): *"a filed plan is a record, not an
instruction"*), and Ruling 32 explicitly declines to edit it for the same reason.

**C1 — "calling Task 1.4's identical per-step evaluator" names something that does not exist.**
Ruling 32: the shared thing is `build_scoring_result`, the post-evaluation tail. The map carries
the same phrasing the spec did, at
[`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md):503; the spec was corrected and the map
was not, because the spec is the artifact that governs.

**C2 — "register a `JobKind.SCORE_BATCH` handler in `backend/src/app/worker/handlers.py`" points
at the registry, not a handler module.** Handlers live in per-domain modules
(`data_handlers.py`, `model_handlers.py`, `rate_table_handlers.py`, `rating_handlers.py`) wired
from `entrypoint.py`. Mirror `rating_handlers.py`, which Task 1.2 added for `RATING_COMPILE`.

**C3 — "grant `Permission.SCORE_BATCH`" is the same trap Ruling 18 dissolved for Slice 2, and it
would turn a passing test red.** `test_rbac.py:101-107`, marked `@pytest.mark.req("FR-GOV-6")`,
asserts that **no builtin role** holds `SCORE_EXECUTE` **or** `SCORE_BATCH`. There is no
"Service Account role" to grant to; a Service Account takes a caller-supplied permission list
(`backend/src/app/api/service_accounts.py:173`). **Task 3C grants nothing; it checks
`Permission.SCORE_BATCH` on the caller.** An executor following the map's wording edits
`BUILTIN_ROLES` and gets a red naming the offending role slug — the expected red for that
mistake, and not a defect in this plan.

**C4 — the map's resumability exit criterion is right but under-specified, and the gap is the
one that matters.** *"Kill mid-chunk, resume from the last committed chunk"* is satisfiable by a
test that only checks the final output — which passes under full restart. Ruling 31 §6 supplies
the missing clause: the test must assert work was **not repeated**, and the second run must carry
a **different Job id**.

**C5 — this plan's own predecessor was wrong about option (a), and about (c)'s premise.**
[`2026-08-29-w11-3-batch-readiness-and-d6.md`](2026-08-29-w11-3-batch-readiness-and-d6.md)
offered (a) full-restart as the cheap baseline that *"matches the generic Job pattern exactly"*.
Ruling 31 §1: the generic pattern does not restart a crashed Job, it **strands** one — *"(a) is
not the cheap option; it is not an option at all."* And that document called (c)'s row key *"not
yet guaranteed unique"*; Ruling 31 §3 found it **does not exist at all**. Both are recorded
rather than folded away, because a plan that quietly agrees with the ruling that corrected it
destroys the record of what was believed.

---

## Findings raised by this plan

**F-W11-3-1 — RESOLVED 2026-08-29 by the addendum to Ruling 31 (`fb56dc6`, PR #424).** Accepted
on the citation; **the reconciling route this finding proposed was rejected**, and a second
citation error was found while verifying it. The finding as filed is left standing below; read
*Corrections after filing* for what changed, and Task 3B Step 1 for the instruction that now
governs.

**F-W11-3-1 as filed — Ruling 31 §6's precedent citation is inaccurate, and following it
literally produces the error the same paragraph warns about.** The ruling says the resumability test
*"drives the **handler** directly — invoke, interrupt, re-invoke with the same parameters — which
is both the level the manifest lives at and **how `backend/tests/test_worker.py` already
exercises handlers**."*

Verified at `9942800`: `test_worker.py` does **not** exercise handlers directly. It registers a
handler and calls `execute_job(database, job.id)` — `:67`/`:70` and the same pattern at `:102`,
`:121`, `:134` — and its module docstring states the convention: *"`execute_job` is exercised
directly rather than through a broker."* A bare handler call appears nowhere in the repository.

**The ruling's decision is unaffected and is followed in full**: the checkpoint is content-keyed,
the second run carries a different Job id, and the test proves work was skipped. Only the
*precedent* is wrong, and the ruling's stated reason for avoiding the guarded path —
*"whose `QUEUED` guard would refuse the second call"* — is true only of a **same-id** re-run,
which the ruling itself forbids two sentences earlier. With a different Job id the row is
`QUEUED` and `execute_job` proceeds normally. So the house pattern and the ruling agree, and the
citation is the only thing that does not.

**Why it is worth filing rather than quietly routing around.** An executor told to mirror
`test_worker.py` and to drive the handler directly will find those two instructions
irreconcilable, and the most likely resolution — reuse the Job id so there is something to
"re-invoke" — walks straight into the guard and produces the *"criterion is untestable"*
conclusion the ruling predicts. **Owner: the decision-maker**, as a correction to their own
record; **not a blocker**, because Task 3B Step 1 states the reconciling route.

---

## Requirement coverage

Every id listed individually.

| Requirement | Where in `03` | Discharged by | How it is proven |
|---|---|---|---|
| FR-RATE-36 | §3.7 | 3A, 3B, 3C | 202 → Job; a Dataset Version re-rated against **one or more** Rating Versions; content-addressed parquet carrying the quote key (from the input frame — it is not on `ScoringResult`), ladder and selected outputs |
| FR-RATE-37 — *chunked*, *progress-reporting*, *identical code path* | §3.7 | 3A, 3B | Byte-identity through `build_scoring_result`; chunking at `chunk_rows`; progress through the injected callback |
| FR-RATE-37 — *resumable* | §3.7 | 3B, **partially** | **Deferred with an owner at the W11 close — not delivered.** See below |
| FR-RATE-38 (batch half) | §3.7 | 3B | Counts and samples per error type; no individual abort below the threshold; threshold behaviour in both directions (Ruling 24) |
| NFR-RATE-5 | §9 | 3D | ≥ 1 M risks/hour/worker, measured with its shape recorded |

**FR-RATE-37's `resumable` clause is not fully discharged by this slice, and booking it as
delivered would put a guarantee in the roadmap that the repository does not have.** Ruling 31's
finding for the lead states it: when Slice 3 is complete and its resumability test passes, *"the
manifest will exist and be proven, and nothing in production will invoke it."* The re-run trigger
is `07` FR-PLAT-11 and FR-PLAT-64, owned by *"whichever workstream builds FR-PLAT-61"*, and
unbuilt. Under [`../../CLAUDE.md`](../../CLAUDE.md) §13 that clause takes **deferred with an
owner**. **The register row is the lead's to write at the close, not this plan's** — recorded
here so it is not discovered during the close.

The age-based sweep for orphaned scratch (Ruling 31 §4) belongs with the same work.

**Deliberately excluded, each with its owner:** FR-RATE-34, 35, 40 → Slice 2. FR-RATE-39, 41,
63, 64, 65 → Slice 1 (shipped). FR-RATE-42 → Slice 4. FR-RATE-43, 44, 45 → W12. FR-RATE-46–49 →
W13. FR-RATE-50, FR-PLAT-28 → W14. FR-PLAT-11, FR-PLAT-61, FR-PLAT-64 → whichever workstream
builds FR-PLAT-61. NFR-RATE-1, 9, 13 → Slice 2. NFR-RATE-12 → Slice 4. NFR-RATE-2, 3, 4, 7, 8,
14 → Slice 1 (measured).

---

## Sequencing and blockers

| Task | Depends on | Blocked by | Why |
|---|---|---|---|
| 3A — `score_batch` | Slice 1 (merged) | — | The handler has nothing to drive without it |
| 3B — the handler | 3A | — | Owns everything durable |
| 3C — the route | 3B | — | 202 → a Job whose handler exists |
| 3D — NFR-RATE-5 | 3B | — | Measure the handler, not the route |

**Nothing here is blocked.** Two coordination notes rather than blockers:

- **Task 1.5 is open as PR #416** and touches `packages/pricing-core/src/pricing_core/rating/compile.py`,
  `scripts/bench-rating.py` and four test files — **not `score.py`**, which is where 3A lands. So
  the two do not collide at file level. **Line numbers in `compile.py` will move**, so cite
  symbols there by name with a re-derivation command.
- **Slice 2 and Slice 4 have filed plans and may land in any order relative to this one — but
  not at the same time as it.** Ruling 33 (`2026-08-29-w11-slice-parallelism-ruling.md`) rules
  that *"two Slices of the same Work may not be built concurrently. §8 is not excepted for W11"*,
  and — the part that catches a plausible argument — §8 protects **context and resource usage
  per session**, not plan stability, so *"an exception argued on plan-independence"* misses the
  interest at stake. Slice 3 being plan-independent of Slices 2 and 4 is therefore not a reason
  to run it alongside them.
- Slice 4's Task 4C already writes the test that keeps batch traces out of the production stream
  (Ruling 25), so if Slice 4 lands first, acceptance criterion 6 is partly discharged there —
  confirm rather than duplicate.

---

## Task 3A — `score_batch`, a pure chunked transform

**Files**
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py` — add `score_batch` and add it
  to `__all__`.
- Test: `packages/pricing-core/tests/test_rating_score_batch.py` (mirror the neighbouring
  `test_rating_score*.py` naming; re-derive with `ls packages/pricing-core/tests/`).

**Interfaces — Produces** (3B relies on this and on nothing else):

```python
def score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, *,
                chunk_rows: int = 100_000,
                progress: ProgressCallback | None = None) -> pl.LazyFrame
```

Copied from `03` §5.2, not retyped. **Do not add a `job_id`, an output path, a resume point, a
sampling rate (Ruling 25) or an abort threshold** — all of those are 3B's, and three of the five
are override conditions.

**Steps**

- [ ] **Step 1: Write the byte-identity test first.** It is the slice's headline criterion, and
      writing it first stops `score_batch` growing a second result-construction path. Score N
      rows through `score_batch`, and the same N contexts through `score_one`; assert the
      serialised ladders are **byte-identical**. Mark `@pytest.mark.req("FR-RATE-37")`.
- [ ] **Step 2: Run it.** Expected: `ImportError`/`AttributeError` for `score_batch`. **A failure
      comparing two ladders means a stub returning something was written first** — not the
      predicted red.
- [ ] **Step 3: Write the chunking test.** With `chunk_rows` smaller than the input, the progress
      callback is invoked more than once and the output row count is unchanged. Mark
      `@pytest.mark.req("FR-RATE-37")`.
- [ ] **Step 4: Write the cancellation test** (FR-PLAT-9): a callback signalling cancellation
      makes `score_batch` return at the next chunk boundary. Cancellation is cooperative and is
      the one control that *is* already specified for this path.
- [ ] **Step 5: Write the purity test — the structural override condition, made behavioural.**
      Assert `score_batch` performs no I/O and holds no state across calls: two invocations with
      the same inputs return equal frames and leave nothing behind. `lint-imports` covers the
      import half; this covers the behavioural half. Mark `@pytest.mark.req("FR-RATE-37")`.
- [ ] **Step 6: Run all four, confirm each fails for its own cause, then implement.** Evaluate
      each row against `bundle.decision`'s **synchronous** path and pass the result to
      `build_scoring_result` — the identical tail (Ruling 32). Do not reimplement any of
      `score.py`'s private helpers.
- [ ] **Step 7: Run `uv run lint-imports`** and confirm green — it is what enforces that no
      durable-state import crept in.
- [ ] **Step 8: Commit.** `feat(rating): score_batch as a pure chunked transform (W11 Task 3A)`

**Must NOT touch.** `score_one`, `build_scoring_result` or any `_`-prefixed helper in `score.py`.
If batch needs something they do not expose, that is a finding.

---

## Task 3B — the `score.batch` handler, the manifest, and the threshold

**This task is where the ruling lives.** Everything durable is here.

**Files**
- Create: `backend/src/app/worker/scoring_handlers.py` — mirror
  `backend/src/app/worker/rating_handlers.py`, which Task 1.2 added, and wire it from
  `backend/src/app/worker/entrypoint.py` the way the other handler modules are. **Do not put the
  handler in `handlers.py`** (C2).
- Modify: `backend/src/app/platform/settings.py` or its neighbours — the workspace setting
  `rating.batch_abort_failure_rate`, **unset by default**.
- Test: `backend/tests/test_scoring_handlers.py`.

**Interfaces — Consumes:** 3A's `score_batch`; `BlobStore.put` for the final output;
`ProgressCallback` plumbing per FR-PLAT-8.

**The manifest, exactly as ruled.** Key: **the compiled bundle's content hash (FR-RATE-24), the
Dataset Version reference, and the chunk index.** All three are reproducible by a re-submission,
because a Dataset Version is immutable and a bundle hash is reproducible from its pins. **Never
the Job id** (Ruling 31 §2) — a fresh Job would not find a Job-keyed manifest and would re-score
everything, which is full restart wearing resume's name.

**Not decided by the ruling, and yours to choose** (Ruling 31 §7): the manifest's storage shape
(a table, or scratch keys enumerated by prefix), the scratch area's physical location, and the
chunk-part format. `JobRow.progress` is **excluded** — it is throttled, lossy and never read back.

**The threshold, exactly as ruled** (Ruling 24): `rating.batch_abort_failure_rate` follows the
`<module>.<name>` form of the two shipped neighbours read through one dotted-key resolver at
`backend/src/app/platform/model_specs.py:62` and `:65`, typed `| None` and guarded
`if … is not None`. The per-run value is a **Job argument**, never a fourth settings-resolution
tier — `settings.resolve` has exactly three branches and no fourth to add one to. **The argument
may only lower the effective threshold**, on `01`'s `severity_override` precedent. When a run
aborts, the Job records **both** the threshold in force and the observed failure rate.

**Steps**

- [ ] **Step 1: Write the resumability test first. Call the handler function itself.** Invoke it;
      interrupt mid-chunk; re-invoke with the same parameters **under a different Job id**.
      Assert **(i)** the already-completed chunks are not re-scored — count chunk invocations or
      rows scored on the resumed call, **never by inspecting the output** — and **(ii)** the
      final parquet is byte-identical to an uninterrupted run. Mark
      `@pytest.mark.req("FR-RATE-37")`.

      **Do not route either call through `execute_job`**, whose `QUEUED` guard would refuse the
      second. This is Ruling 31 §6 as its addendum restates it, and it is **a new test shape for
      this suite** — `backend/tests/test_worker.py` drives handlers through `execute_job` at
      every call site and nothing in the repository invokes a handler function directly. You are
      writing the first one; budget for that rather than looking for a neighbour to copy.

      *An earlier version of this plan told you the opposite* — two submitted Jobs, `execute_job`
      on each, on the reasoning that a fresh Job row is `QUEUED` so the guard never fires. That
      reasoning is factually correct and was **rejected** as the route; see *Corrections after
      filing*. Follow the paragraph above, not that one.
- [ ] **Step 2: Run it and read the failure carefully.** Expected: the handler does not exist —
      an import or attribute error for `_score_batch`. **If instead you see
      `JOB_HANDLER_NOT_REGISTERED`, you went through the Job lifecycle rather than calling the
      handler**, which is the wrong level; and **if the second invocation returns early with a
      Job-status value and no handler body runs, you routed through `execute_job`** — its guards
      at `tasks.py:94` and `:103` return before the handler is reached. Neither is a bug in the
      handler, and both are the failure Ruling 31 §6 predicts: *"An executor who concludes the
      criterion is untestable has tested it at the wrong level."*
- [ ] **Step 3: Write the two threshold tests.** A request whose argument is **above** the
      resolved workspace setting is **refused**; a run crossing the effective threshold aborts
      with both numbers recorded on the Job. Add a third for the unset default: no rate-based
      abort, counts still accrue. Mark `@pytest.mark.req("FR-RATE-38")`.
- [ ] **Step 4: Write the error-typing test** (FR-RATE-38): a frame containing rows that trigger
      each error category yields per-category counts and samples, and the run does **not** abort
      on them below the threshold.
- [ ] **Step 5: Write the scratch-lifecycle test.** Chunk parts are written **outside** the
      content-addressed store, and are released when the run completes. Assert the blob store
      holds exactly one new object after a successful run — the concatenated output — and not one
      per chunk. This is the test that keeps Ruling 31 §4 true.
- [ ] **Step 6: Run all of them, confirm the causes, then implement the handler.** Loop bundles
      for FR-RATE-36's *"one or more Rating Versions"*; carry the quote key through from the
      input frame, since `ScoringResult` does not have one.
- [ ] **Step 7: Run the gate, both halves. Commit.**

**Must NOT touch.** `execute_job`, `run_job`, `JobProgress`, or `VALID_TRANSITIONS`. The absence of a re-run
trigger is a finding already filed for the lead (Ruling 31's closing finding) — **do not build a
reaper or a retry endpoint inside a rating slice.**

---

## Task 3C — `POST /api/v1/score/batch`

**Files**
- Create or extend: a scoring router under `backend/src/app/api/`. **If Slice 2 has landed, add
  the route beside its `/score` sibling rather than creating a second module** — check first.
- Test: `backend/tests/test_score_batch_api.py`.

**Steps**

- [ ] **Step 1: Write the 202 test.** The route answers **202** with a `Job` body (`03` §5.1:517);
      polling the Job to completion yields a parquet retrievable from the blob store. Mirror the
      existing 202+Job route tests rather than inventing a fixture.
- [ ] **Step 2: Write the RBAC test — three cases**, exactly as Ruling 18 established for
      `SCORE_EXECUTE`: a Service Account scoped to the environment and holding `score:batch` may
      call it; the same account without the permission is refused; a key for an environment
      outside the account's list is refused **at authentication**, before the route. Mark
      `@pytest.mark.req("NFR-RATE-11")`.
- [ ] **Step 3: Confirm the standing guard is untouched.** `uv run pytest backend/tests/test_rbac.py`
      must stay green. **If it goes red naming a role slug, you granted the permission to a
      builtin role** (C3) — that is the predicted failure for the map's wording, not a defect
      here.
- [ ] **Step 4: Run, implement, re-run, gate, commit.**

---

## Task 3D — NFR-RATE-5

**Files**
- A dated note under [`../research/`](../research/). **Reuse Task 1.5's harness conventions**
  once PR #416 lands rather than establishing a second one.

**Acceptance**
- **≥ 1 M risks/hour per worker**, measured against the **handler**, not the route — the route
  adds HTTP overhead to a throughput figure that is about the worker.
- **Report the distribution and the shape.** State the chunk size, the row width, whether the
  structure included a `model_call`, and whether the figure is a single worker or extrapolated.
  A throughput number without its shape is not reproducible, and this repository's own
  NFR-RATE-14 row is the standing example of a figure that meant something narrower than it read.
- **"Linear in workers" is a claim, not a measurement, unless two workers were run.** If only one
  was, say so and mark the linearity untested rather than implying it.
- **Not a CI gate.**

---

## Self-review

**1. Spec coverage.** Every requirement the map allocates to Slice 3 appears in the coverage
table with its section and task, listed individually, and FR-RATE-37 is **split across two rows**
because its clauses do not share a disposition — the chunked/progress/identical-path clauses are
delivered here and the *resumable* clause is deferred with an owner. Collapsing them into one row
is precisely how a resumability guarantee the repository does not have would reach the roadmap.

**2. Placeholder scan.** No TBD. Three things are explicitly left to the executor because Ruling
31 §7 leaves them there — manifest storage shape, scratch location, chunk-part format — and each
says so at the point of use rather than being silently omitted.

**3. Type consistency.** `score_batch`'s signature is copied from `03` §5.2, not retyped;
`build_scoring_result` is named once in *Verified facts* and used under that name in 3A;
`rating.batch_abort_failure_rate` is named once and used under that name in 3B.

**4. Literals verified against shipped source at `c79a39d`**, including the negatives that
matter: `score_batch` absent, no handler for `SCORE_BATCH` despite the queue routing existing,
`ScoringResult` carrying no `quote_id`, and `pl.LazyFrame` having no precedent. Where Task 1.5's
open PR will move line numbers — `compile.py` and `scripts/` — symbols are cited by name with a
re-derivation command instead.

**5. Predicted failures are stated by cause**, and two of them are the traps this slice is most
likely to hit: 3B Step 2 distinguishes "handler absent" from "you tested through `execute_job`", the
error Ruling 31 §6 says makes an executor conclude the criterion is untestable; and 3C Step 3
names the red that follows from the map's *"grant `Permission.SCORE_BATCH`"* wording, so it reads
as the expected consequence rather than as a defect.

**6. What this plan does not decide.** Nothing above its charter. The re-run trigger is a
scheduling question already raised with the lead; the scratch sweep belongs with it; and the
FR-RATE-37 register row is the lead's to write at the close. **F-W11-3-1 corrected a ruling's
citation and was filed as a finding for the decision-maker rather than acted on unilaterally** —
the right call on raising it, and the wrong call on what came next: this plan also *proposed a
route round the defect*, and the addendum rejected it. Raising a citation error is a planner's;
choosing the test shape that replaces it is not. Corrected in place; see *Corrections after
filing*.

**8. Every claim taken from a delegated sweep was re-run before it entered this plan**, and one
of them did not survive. The sweep reported that `test_worker.py` never calls a handler directly;
I read the file myself, found the `execute_job` convention stated in its own module docstring,
and only then wrote F-W11-3-1 — because filing a correction against a decision-maker's record on
a subagent's word would be the same defect the finding describes, one level up. **The finding was
accepted and a second error found beside it.** What the verification discipline did not catch is
the overreach in the same paragraph: having proved the precedent absent, this plan went on to
pick the replacement route. Evidence quality does not widen a charter.

**7. Corrections to this plan's own predecessor are recorded rather than folded in** — C5. The
readiness document offered full-restart as the cheap baseline and described (c)'s row key as
merely not-yet-unique; Ruling 31 found the first strands a crashed Job rather than restarting it,
and the second does not exist. Both errors were mine, and both are left visible because the
reasoning that produced them is the reasoning a future planner would repeat.
