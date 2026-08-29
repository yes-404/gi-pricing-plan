# W11 pre-work rulings — the rating-version route gap and the compile status code (2026-08-29)

`CLAUDE.md` §0 code-vs-spec rulings, dispatched ahead of the §15 adoption record and
independent of it, ruled before W11's first slice touches the affected path — per the
standing rule that when code and spec disagree the platform stops and resolves it rather
than quietly making either side match the other. No plan is frozen for W11 yet; this record
is not a decision point against a plan — it is the dated home for rulings the auditor,
executor and planner found while reading the rating-engine surface ahead of that plan.
Rulings 1 and 2 were the first pair, found by the auditor's endpoint-axis sweep. Rulings 3
and 4, appended the same day, were found independently by the executor and planner while
scoping W11 slice 1 and are the same kind of situation: code and spec disagreeing, or a type
the spec relies on existing nowhere in code.

Every identifier, route literal, status code, error code and requirement id below is grepped
against `origin/main` `07ae047` before being written down (`CLAUDE.md` §12 — a ghost citation
cost W10 real time).

## Ruling 1 — `POST /api/v1/rating-versions` has no route

**The finding, restated precisely.** `03-rating-engine.md:512` declares
`POST /api/v1/rating-versions — Create a draft Rating Version with pins`, with no `(FR-RATE-n)`
citation in the cell. No route answers that path anywhere in the backend.

**Options, as dispatched:** (a) a capability nobody specified — needs a new `FR-RATE-` id and
a workstream to own building it; (b) a stale Phase-0 row — needs a tombstone per `CLAUDE.md`
§5 (ids and section numbers are never reclaimed, only marked superseded).

**Ruled: neither. This is a third case — a specified, current, Phase 2 capability whose
service layer is fully built and tested, and whose HTTP route was simply never wired. The
fix is code, not a tombstone and not a new requirement, and it is owned by W11.**

Rationale — read, not inferred:

- **The capability is specified**, just not by a citation in that one cell. `FR-RATE-22`
  (`03-rating-engine.md:133`) is exactly "a Rating Version pins: one Rating Algorithm
  version, an exact Rate Table Version per referenced table, an exact Model/Peril Structure
  version per `model_call`, an exact Reference Table Version per `lookup`... Nothing is
  unpinned" — the row's own words ("with pins") are FR-RATE-22's words. A missing inline
  citation is not unique to this row either: `03-rating-engine.md:505`
  (`POST /rate-tables/{slug}/versions — New Rate Table Version with change note`) cites
  nothing and nobody has proposed tombstoning it. Uncited routine create/list/get rows for a
  resource whose *structure* is defined at the data-contract level are this suite's normal
  convention, not a defect.
- **`wf-02` already walks through it, and already cites the requirement the table cell
  doesn't.** `docs/workflows/wf-02-model-to-rating-version.md:56`, step C1: *"Pricing
  Actuary — `POST /rating-versions` — declares the algorithm version and every pin: rate
  tables, peril structure, reference tables. — `03` FR-RATE-22."* This is not a row a later
  phase forgot about; it is load-bearing in the one workflow document that ties the whole
  module together end to end.
- **The service function is built, RBAC-checked, and audited — and called from nowhere but
  its own test.** `backend/src/app/platform/rating_versions.py:93-138` (`create_rating_version`)
  checks `Permission.RATING_WRITE`, computes the next version number per slug, writes the
  draft row, and records a `rating_version.created` audit event. `git grep -n
  'create_rating_version\b'` across `backend/` returns exactly two hits: its own definition
  and `backend/tests/test_rating_versions.py:58`, which calls it directly as a unit test —
  never through an HTTP route.
- **The same gap holds for `submit_for_review`, and the comparison across sibling artifact
  types is the clean part of the evidence.** `submit_for_review`
  (`backend/src/app/platform/rating_versions.py:141-176`, checking
  `Permission.RATING_SUBMIT`) also has no route. Every sibling artifact type's own
  `submit_for_review` *is* wired: `backend/src/app/api/custom_objectives.py:399`,
  `backend/src/app/api/validation.py:345`, `backend/src/app/api/peril_structures.py:323`,
  and models' own submit at `backend/src/app/api/models.py:740`. Rating-versions is the one
  artifact type in this codebase whose write lifecycle is built at the service layer and
  stops there.
- **The code says so about itself.** The two rating-version routes that *do* exist —
  `list_rating_versions` and `get_rating_version`
  (`backend/src/app/api/models.py:1096-1136`) — both carry the same sentence in their
  docstrings: *"The full `03` surface stays Phase 2."* (`:1104`, `:1130`). This was never a
  silent omission; it was a stated, deliberate Phase 1b scope cut (`FR-PLAT-67`, the W7 exit
  demo), and `CLAUDE.md` §0's table is explicit that a capability inside the current phase's
  scope is code, not a spec change. Phase 2 is now, and W11 is the workstream that needs the
  full rating-version write lifecycle to create, submit and approve the versions it scores
  against.
- **Ruling out the tombstone reading on its own terms.** `CLAUDE.md` §5's tombstone applies
  to a requirement or section that is no longer true — retired, superseded, or never going
  to be built. Nothing here is any of those: the capability is exercised by `wf-02`, it is in
  the current phase, and its data-contract half (`FR-RATE-22/23`) is unquestionably live.
  Tombstoning the row would misrepresent a real, currently-needed capability as abandoned.

**Disposition.** Code fix, not a spec change: add `POST /api/v1/rating-versions` and
`POST /api/v1/rating-versions/{id}/submit` route handlers in
`backend/src/app/api/models.py` (or a dedicated `api/rating_versions.py`, matching the
`api/rating_algorithms.py` pattern) calling the existing, already-tested
`create_rating_version` and `submit_for_review` service functions, gated on
`Permission.RATING_WRITE` / `Permission.RATING_SUBMIT` respectively — the same permissions
those functions already enforce internally. **Owner: the W11 scoring workstream**, as
prerequisite work before or alongside its first slice, since W11 cannot create or submit a
real (non-demo-seed) Rating Version to score against without it. This is not a new
workstream and not a register carry-forward past a close — it is in-phase completion work
the register can now file with a named owner, per the auditor's F-W10-3 precedent.

**Spec correction made in this commit (citation only, no new id, no meaning change):**
`03-rating-engine.md:512`'s row gains the `(FR-RATE-22)` citation `wf-02` already relies on,
so the table cell and the workflow document agree on what governs it.

## Ruling 2 — the compile endpoint: specified `202`, implemented `200`

**The finding, restated precisely.** `03-rating-engine.md:513` declares
`POST /api/v1/rating-versions/{id}/compile — **202** Compile + validate the bundle
(FR-RATE-25)`. The implemented route
(`backend/src/app/api/models.py:1139-1161`) has no `status_code` override and its own
docstring says `"""**200** with the compiled Bundle's metadata (FR-RATE-24/25)."""`
(`:1149`) — code and spec disagree on the same requirement citation.

**Options:** (a) the code is right — amend `03` §5.1 to `200`; (b) the spec is right — fix
the code to return `202` with a Job.

**Ruled: (b) — the spec's `202` is correct. The code's `200` is a Phase-1b synchronous
stand-in, and completing it to `202`+Job is W11 slice-1 work — the same slice that must
already stop discarding the compiled Bundle.**

Rationale:

- **A second, independent document already agrees with `03` §5.1, and names the Job kind.**
  `docs/workflows/wf-02-model-to-rating-version.md:57`, step C2: *"Pricing Actuary —
  `POST /rating-versions/{id}/compile` → `202` + Job (`rating.compile`). — `07` FR-PLAT-7."*
  This is not one row read in isolation; the module's own cross-module workflow account
  independently states `202` and names the specific Job kind.
- **The platform's typed Job infrastructure already has this Job kind — unused.**
  `packages/model-schema/src/model_schema/jobs.py:53` defines
  `RATING_COMPILE = "rating.compile"` in the `JobKind` enum, matching `wf-02`'s citation
  exactly. `backend/src/app/platform/jobs.py:72` already routes it to a queue:
  `JobKind.RATING_COMPILE: JobQueue.DEFAULT`. `Permission.RATING_COMPILE`
  (`packages/model-schema/src/model_schema/permissions.py:50,115`) already gates the
  existing synchronous route (`backend/src/app/api/models.py:1146`). Three separate pieces
  of typed platform machinery were already built for this to be an async Job; a `git grep`
  across `backend/src/app/worker/` for `JobKind.RATING_COMPILE` returns nothing — no handler
  was ever registered, unlike `JobKind.RATE_TABLE_DIFF`
  (`backend/src/app/worker/rate_table_handlers.py:65`) and `JobKind.MODEL_FIT`
  (`backend/src/app/worker/model_handlers.py:1322-1323`). The scaffolding was built for
  `202`; only the handler and the route's status code were not finished.
- **The budget the spec is protecting is real and already numbered.**
  `NFR-RATE-4` (`03-rating-engine.md:779`): "Bundle compilation for a large motor structure
  completes in < 60 s; bundle size stays under 500 MB including booster artifacts." A
  60-second, up-to-500 MB synchronous POST is exactly the shape of work this codebase's own
  stated convention treats as `202`. The `predict` route's own docstring
  (`backend/src/app/api/models.py:1064-1076`) draws the line in this exact module: *"a fit,
  a comparison, a backtest and a transparency artifact all read a whole dataset version"* →
  `202` (naming `FR-MODEL-56/84/90/92`), while `predict` itself stays `200` only because it
  "reads at most `MAX_PREDICT_ROWS` rows the caller sent." Bundle compilation resolves every
  pinned artifact a Rating Version references — potentially a large rate table and a loaded
  GBM booster — which is the "reads a whole large artifact" side of that same line, not the
  bounded-request side.
- **The code cannot honour `FR-RATE-24` today regardless of status code, which is the more
  urgent half of this ruling for W11.** `FR-RATE-24` (`03-rating-engine.md:135`): the Bundle
  "is what gets cached and distributed." The implementation
  (`backend/src/app/platform/rating_versions.py:273-288`) computes the full `Bundle`
  (`graph`, `resolved_payloads`, `pins`) via `compile_bundle()`, then persists only
  `{content_hash, bytes, compiled_at}` onto the row and returns that dict — the compiled
  object itself is discarded when the function returns. Nothing loads a bundle back. This is
  the planner's own finding, confirmed directly in the source: there is currently no code
  path that could serve `NFR-RATE-3` ("a compiled bundle scores with zero database or
  network access; everything it needs is inside it") because nothing durable holds "it."
  Fixing persistence and fixing the status code are one piece of work, not two: the natural
  shape is a `RATING_COMPILE` worker handler that calls `compile_bundle()`, writes the full
  `Bundle` to the blob store (`07-platform.md:112-114`, `FR-PLAT-18/19`, content-addressed,
  matching how `DislocationRun.largest_movers_blob` and the W10-3D rate-table-diff Job already
  do it), and records the blob reference — not only the three scalar fields — on the
  version's `bundle` metadata.
- **No competing argument survives.** The only way `200` could be right is if bundle
  compilation is reliably cheap and bounded, but `NFR-RATE-4`'s own 60 s / 500 MB ceiling was
  set deliberately and nothing in the record revises it downward. Treating a
  potentially-60-second POST as synchronous risks exactly the HTTP-timeout and
  worker-thread-exhaustion failure mode the platform's own `202` convention exists to avoid,
  on the one endpoint in this module that resolves the most artifacts at once.

**Disposition.** Code fix, W11 slice 1 (the same slice the dispatch already names for
Bundle persistence): register a `JobKind.RATING_COMPILE` handler in
`backend/src/app/worker/` alongside the existing `rate_table_handlers.py` /
`model_handlers.py` pattern; change `POST /rating-versions/{id}/compile` to submit that Job
and answer `202`; persist the full `Bundle` to the blob store, not only its metadata. No
spec change — `03` §5.1 and `wf-02` already say `202` correctly; the code is what moves.

**Related finding, not ruled here (flagging for the same slice).** The compile resolver's
`_Resolver.resolve()` (`backend/src/app/platform/rating_versions.py:240-271`) only handles
`ref.type in {"rating_algorithm", "model"}` and raises `NOT_FOUND` for anything else,
including `rate_table`, with the comment "Rate tables... have no backend tables yet
(Phase 2)." That comment predates W10: `RateTable`/`RateTableVersion` now have real backend
tables (`docs/plans/2026-08-28-w10-rate-tables.md`, merged). Per `FR-RATE-22`, essentially
every real Rating Version pins at least one rate table, so today's resolver would refuse to
compile any of them. This is not a code-vs-spec disagreement — the spec was always right and
the comment is simply stale — so it needs no ruling, only a fix, and it lands in the same
W11 slice as the two rulings above since none of the three is separable from the others.

## Ruling 3 — `compile_bundle` is `async` in code, `def` (sync) in spec §5.2

**The finding, restated precisely.** `03-rating-engine.md:593` declares
`def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle` — a plain,
synchronous signature. The implementation
(`packages/pricing-core/src/pricing_core/rating/compile.py:387`) is
`async def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle:`. The
`ArtifactResolver` protocol it takes (`compile.py:298,305`) is itself declared
`async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact: ...` — the deviation is not
an isolated typo, it runs through the whole resolver contract.

**Options:** (a) the spec is right — make the code (and the resolver protocol) synchronous;
(b) the code is right — correct the spec's signature to `async def`.

**Ruled: (b).** The spec's plain `def` is the thing that needs fixing.

Rationale:

- **The resolver has to be async because its real implementation does genuine async I/O,
  and `pricing-core` cannot own that I/O itself.** `ArtifactResolver` exists specifically so
  `compile_bundle` never touches a database (`compile.py:298-305`'s own docstring: "Resolves
  a pinned artifact... the DB-backed half... This keeps `pricing-core` standalone
  (ADR-0001)"). The backend's actual resolver
  (`backend/src/app/platform/rating_versions.py:240-271`) does real `await
  session.scalar(select(...))` calls against SQLAlchemy 2.x async sessions (`CLAUDE.md` §3's
  stack). A sync `resolve()` calling into an async session would need its own event-loop
  bridge inside every resolver implementation — pushed onto every caller, forever, to keep
  one function signature nominally synchronous.
- **`compile_bundle` is called from within an already-running event loop, not started
  fresh.** The backend route (`backend/src/app/api/models.py:1144-1161`,
  `compile_rating_version`) is itself `async def`, called by FastAPI inside its own loop.
  Making `compile_bundle` synchronous would force it to either block that loop (defeating
  the concurrency the async stack exists for) or spin up a nested loop via something like
  `asyncio.run()` inside an already-running one, which raises at runtime. There is no clean
  synchronous path available to the actual caller.
- **This is not a hot-path performance concession that would also justify making `score_one`
  async — it doesn't, and the spec is right to keep those synchronous.** `score_one` and
  `score_batch` (`03-rating-engine.md:598,600`) score against an already-self-contained
  `CompiledBundle` with, per `NFR-RATE-3`, "zero database or network access" — there is
  nothing to `await`, and keeping the scoring hot path free of event-loop overhead matters
  under `NFR-RATE-1`'s 50 ms budget. `compile_bundle` is the opposite case: it is
  definitionally the function that resolves pinned artifacts from durable storage, it runs
  rarely (compilation, not per-quote scoring), and per Ruling 2 it is about to become an
  async platform Job anyway — async is not just tolerable there, it is the only shape that
  matches what the function does.
- **Every other §5.2 signature in the same code block is genuinely synchronous in code, so
  this is not a wholesale mismatch.** `validate_algorithm` (`compile.py:260`), `to_jdm`
  (`:325`), and `bundle_hash` (`:367`) are all plain `def` in the implementation, matching
  the spec exactly. The deviation is narrow and specific to the one function that has to
  cross the I/O boundary — which is exactly where a hand-written interface signature is most
  likely to under-specify a mechanical Python detail the author did not need to think about
  in prose, and exactly where the implementation had no choice once it met a real database.

**Disposition.** Spec fix, made in this commit: `03-rating-engine.md:593` corrected to
`async def compile_bundle(...)`. No code change — the implementation was already right.

**A tooling gap this fix exposed, also fixed in this commit.** `scripts/audit-docs.py`'s
journey-citation check (FR-OVR-17) extracts declared `pricing-core` functions with
`re.finditer(r"^def ([a-z_][a-z0-9_]*)\(", ...)` — anchored on a bare `def `, with no
`async def` case. Making the spec's signature accurate (above) silently dropped
`compile_bundle` out of the declared-function set, which then failed
`wf-02-model-to-rating-version.md:58`'s existing, correct citation of `compile_bundle()` as
newly "undeclared." The check itself had never had to handle an async `pricing-core`
signature before — nothing in `03` §5.2 needed one until this ruling. Fixed to
`r"^(?:async )?def (...)\("`; re-run clean (`python3 scripts/audit-docs.py`: "journey
citations: 31 endpoints, 8 functions, all declared"). Verified as a real positive/negative
pair rather than asserted: the check failed with the old regex and the old (wrong, sync)
spec line both absent — i.e. it failed **because** the spec line changed and the checker
did not follow — and passed once the checker did.

## Ruling 4 — `CompiledBundle` is spec-only; `Bundle` is the only thing that exists, and they are not the same type

**The finding, restated precisely.** Every `03` §5.2 scoring-adjacent signature —
`score_one`, `score_batch`, `dislocate` (twice: `baseline`, `candidate`), `run_regression`
(`03-rating-engine.md:598,600,605,610`) — takes a `CompiledBundle`. `git grep -n
CompiledBundle` across `packages/`, `backend/` and the spec returns **only** those four
spec lines; zero code definitions, zero imports, zero references anywhere. The only real
class is `Bundle` (`packages/pricing-core/src/pricing_core/rating/compile.py:350`), defined
by the already-ruled `DP1` (`compile.py:280-283`, 2026-08-27): "the JDM graph plus the
pinned artifacts' resolved payloads, wrapped by the pricing-core facade... self-contained:
sufficient to score with no database access." This ruling does not reopen DP1 — `Bundle`
stays exactly what DP1 said. The question DP1 never had to answer is whether the thing
`score_one` actually executes against is the same object.

**Options:**

- **(a) Rename-only: `CompiledBundle` *is* `Bundle`.** The spec's four signatures are
  corrected to say `Bundle`, and scoring takes the plain, JSON-shaped, persisted object
  directly.
- **(b) `CompiledBundle` is a distinct, new runtime type — a loaded wrapper around a
  `Bundle`** — holding whatever the ZEN engine binding needs to actually execute the graph
  (an initialised decision/engine handle built from `graph`) plus any GBM boosters loaded
  from `resolved_payloads` into live `Booster` objects, produced by a new hydration function
  (e.g. `load_bundle(bundle: Bundle) -> CompiledBundle`) that is never itself serialised.
  `Bundle` stays exactly DP1's self-contained, cacheable, distributable data form;
  `CompiledBundle` is what a warm worker process holds and what `score_one`/`score_batch`/
  `dislocate`/`run_regression` actually take.
- **(c) One mutable type**: keep only `Bundle`, but let it lazily populate and memoise an
  engine handle / loaded boosters on first use as instance state.

**Ruled: (b).** Grow the code to match the spec's existing name; do not rename the spec to
match today's code.

Rationale:

- **(a) reintroduces, per request, exactly the cost this session's own W11 orientation
  report already flagged as the central real-time-evaluator risk.** If `score_one` receives
  the plain `Bundle` — a Pydantic model whose `graph` field is a JSON-shaped `dict[str,
  dict[str, Any]]` — something has to turn that into whatever the `zen-engine` Python
  binding needs to actually walk the DAG, and something has to turn any resolved booster
  bytes into a live, `nthread=1`-pinned `Booster` object, on **every call**, unless a second,
  hidden cache is invented inside `score_one` itself. That hidden cache would just be option
  (b) again, minus the type system saying so — worse for testability (nothing distinguishes
  "freshly deserialised" from "already loaded" at the type level) and worse for the exact
  latency budget `NFR-RATE-1` sets (repeating graph-parse and booster-load work per request
  that a warm process should only do once per deployment switch).
- **(b) is what `FR-RATE-51` and `NFR-RATE-6` already describe, just without a name for the
  loaded half.** `FR-RATE-51`: "Bundles are **pre-warmed into cache** before the switch."
  `NFR-RATE-6`: switchover "completes within 30 s of the deploy command **including cache
  warming**." Pre-warming is a *load* step — it only makes sense as a description of turning
  a distributable `Bundle` into something already resident and ready to execute in a
  process's memory. `Bundle` (DP1) is the thing that gets distributed and cached in Redis;
  `CompiledBundle` is the thing pre-warming produces, held per-worker, never round-tripped
  through Redis itself. This is the same two-tier shape this session's own W11 orientation
  report recommended for the caching decision point, arrived at independently from the
  executor's and planner's side and now given the concrete names the spec already committed
  to.
- **(c) blurs a distinction this codebase is otherwise careful to keep sharp.** `Bundle` is
  a `BaseModel` — data, meant to be hashed (`content_hash`), serialised
  (`bundle.model_dump_json()`, used for exactly that in
  `rating_versions.py:285`), and compared for equality. Attaching mutable, unserialisable
  runtime state (an engine handle, loaded boosters) to instances of that same class means a
  `Bundle` can no longer be freely copied, diffed, or round-tripped through JSON without
  first checking whether the loaded fields happen to be populated — exactly the kind of
  boundary confusion `03` §3.11 already spent a spike (S1) correcting once for money at the
  ZEN engine's Python binding. Keeping "the record" and "the loaded resource" as two named
  types is the same discipline applied one layer up.
- **Growing the spec's name rather than renaming the spec matches every ruling in this file
  so far.** Rulings 1, 2 and 3 all found the spec's declared shape correct and the code
  incomplete or mis-specified relative to it (a missing route, a wrong status code, an
  under-specified signature) — not the reverse. `CompiledBundle` already exists in the one
  place that gets to mint the name first; the code has not caught up yet, which is a
  different situation from the code being wrong.

**Disposition.** No spec change — `03` §5.2 already says `CompiledBundle` correctly.
**Code, W11 slice 1**: add a `CompiledBundle` type to `pricing_core.rating` (or a sibling
module, e.g. `pricing_core.rating.runtime`) and a hydration function from `Bundle` to it;
retarget `score_one`/`score_batch` (and, when built, `dislocate`/`run_regression`) to take
`CompiledBundle`; the in-process cache Ruling 2 and this session's own orientation report
both anticipate holds `CompiledBundle` instances, loaded once per deployment-switch, not
`Bundle` bytes re-parsed per request. Exact field shape and the engine-handle type are the
executor's to design against this ruling, not fixed here.

**Related, not re-ruled (already flagged in this record's own Ruling 2, now independently
confirmed by the executor and planner too).** `CompiledBundle`'s hydration step is only as
good as what `Bundle.resolved_payloads` actually contains, and today's resolver
(`rating_versions.py:240-271`) puts a placeholder (`payload={"status": model.status}`) in
the `model` branch and raises `NOT_FOUND` unconditionally for `rate_table` refs on a stale
Phase-2 comment. No realistic Rating Version compiles today regardless of sync/async or
`CompiledBundle`. Same W11 slice-1 prerequisite named in Ruling 2; not a separate ruling.

## Ruling 5 — `score_one`'s real-time path: `async_evaluate()`, not `evaluate()` + executor offload; and whether §5.2's sync convention is itself the defect

**The finding, precisely, and its evidence.** `docs/research/zen-evaluate-concurrency.md`
(filed #321, executor's spike, dispatched ahead of the W11 plan freezing, explicitly
declining to rule) measured the ZEN engine's evaluate side for the first time in this
project — S1/S2 and their W8 re-verification only ever tested the compile side. Two
questions, both measured twice on the same machine:

- **Does `evaluate()` block the asyncio event loop?** Yes, completely: a 1 ms heartbeat
  coroutine got **0 ticks** during a 2.8–2.9 ms sync `evaluate()` call, both runs.
  `async_evaluate()` — a real binding the project did not previously know existed
  (`zen-evaluate-concurrency.md:49-54`, `ZenEngine.async_evaluate` /
  `ZenDecision.async_evaluate`, `Awaitable[EvaluateResponse]` per the installed `.pyi`
  stub) — does not block: 3 ticks at the expected cadence, both runs.
- **Does offloading the sync call to a thread pool recover throughput?** No — it is
  **worse than doing nothing**: sequential `evaluate()` ×64 as the 1.00x baseline,
  4-worker-thread-pool-offloaded `evaluate()` ×64 measured at **0.90–0.93x**, both runs,
  consistent with the GIL held for the full native call so extra OS threads add pure
  scheduling overhead against an effectively single-threaded resource. `async_evaluate()`
  ×64 via `asyncio.gather` measured **2.10–2.25x**, both runs — real multi-core throughput,
  not merely non-blocking.

**Options, as dispatched:** (a) build `score_one`'s real-time path on `evaluate()` plus
`run_in_executor` thread-pool offload; (b) build it directly on `async_evaluate()`.

**Ruled: (b).** `async_evaluate()` dominates on every axis this spike measured — it does
not block, and it is the only one of the two that delivers any throughput gain at all.
Option (a) is not a safer, slower alternative to (b); it is strictly worse than doing
nothing, on data reproduced twice.

Rationale:

- **No axis favours (a).** Non-blocking: both achieve it, one (offload) by construction and
  the other (native) as measured. Throughput: (a) is 0.90–0.93x, (b) is 2.10–2.25x. There is
  no dimension along which paying for a second thread-pool layer — one that then has to be
  reasoned about against `NFR-RATE-14`'s own `nthread=1` GBM thread-pool discipline — buys
  anything back.
- **This is the correct scope, and I am not extending it past what was measured.** The
  ruling is for `score_one`'s real-time path specifically, called from a live FastAPI
  request handler sharing an event loop with other in-flight quotes — exactly the context
  `NFR-RATE-1`'s 200 rps/replica target describes and exactly the context blocking would
  hurt. `score_batch` (batch, Job-driven, no shared event loop with concurrent requests to
  protect) is **not** ruled here and its own `def` signature (`03-rating-engine.md:600`) is
  untouched — a batch worker may still benefit from `async_evaluate()`'s internal
  concurrency for its own chunk-level throughput, but that is an implementation choice
  inside a function whose public signature does not need to change, not a repeat of this
  ruling.
- **What the spike does not cover, weighed rather than ignored.** No `model_call` step
  exists to test — the GIL-release finding is proven for pure `expressionNode` evaluation
  and only *suggested* for a graph that also invokes XGBoost mid-evaluation via the
  ADR-0004 custom-node mechanism, which is unbuilt. `NFR-RATE-14`'s `nthread=1` governs
  XGBoost's own nested thread pool — a different, separate mechanism from whatever
  `async_evaluate()` releases around it — and this spike says nothing directly about how
  the two interact once wired together. The 2.10–2.25x on 4 cores is also not the ideal 4x,
  and the spike names the gap as open rather than closing it. **None of this changes the
  ruling for the graph shape actually measured**, because a `model_call` step's own
  GIL-holding window is small and already separately budgeted (S2/W8: p99 ~1.09–1.626 ms
  for the booster call itself) against the other ~199 steps that would still benefit from
  the release — but it does mean this is ruled as an **instrumented default, not a closed
  question**: **the same GIL-release measurement must be repeated once a `model_call`
  custom node exists**, named explicitly as a slice prerequisite for whichever slice builds
  that integration, not assumed to transfer automatically.
- **No sustained-load or ASGI-embedded measurement exists yet either** (`zen-evaluate-
  concurrency.md`'s own scope limits: a bare `asyncio.run`, not inside FastAPI; 64 concurrent
  calls once, not 200 rps sustained). `NFR-RATE-1`'s own sustained-load test is already a
  named Phase 2 item (`docs/roadmap.md:146`); this ruling does not substitute for it, and
  the latency harness the roadmap's own risk row already calls for building "alongside the
  evaluator, not after" is where that measurement belongs.

**Disposition.** Spec fix, made in this commit: `03-rating-engine.md:598`'s
`score_one` signature becomes `async def score_one(...)`. No other §5.2 signature in this
block changes — `score_batch`, `dislocate`, `attribute`, `run_regression` and
`generate_contexts` all run in Job/worker contexts without a shared-event-loop concern, and
none of them is shown by this spike to need a different declared shape. **Code, W11 slice
1**: the evaluator built on `pricing_core.rating.score.score_one` calls
`CompiledBundle`'s loaded engine handle's `async_evaluate()`, not `evaluate()` plus an
executor. **Follow-up, named and owned by whichever slice builds `model_call`'s ADR-0004
custom-node integration**: repeat Q2/Q3 of `zen-evaluate-concurrency.md` on a graph that
actually invokes a booster mid-evaluation, before trusting this ruling's GIL-release
reasoning under real load with a real GBM call in the path.

**The larger question: is §5.2's sync-by-default convention itself the defect?** No — the
convention (declare a `pricing-core` function synchronous unless something specific forces
otherwise) is a reasonable prior for a spec written before any implementation existed to
check it against, and it is right for the overwhelming majority of `pricing-core`'s own
interface: `validate_algorithm`, `to_jdm`, `bundle_hash`, `to_minor`, `apply_factor`, every
`rate_tables/operations.py` function, `score_batch`, `dislocate`, `attribute`,
`run_regression`, `generate_contexts` — none of these await anything, and sync is correct
for every one of them. What is actually defective is narrower and more precise than "the
convention": **two signatures were declared sync without checking what they actually call,
and both turned out to call something that only works correctly from an `async def`** — a
genuinely async-native binding in `score_one`'s case (`async_evaluate()`, this ruling), and
a resolver doing real async I/O in `compile_bundle`'s case (Ruling 3). Both are the same
underlying failure: *a spec signature declared before the thing it wraps was known to have
an async-only correct calling convention.* That is not a defect in "declare things sync by
default" as a prior — it is a gap in the **verification step**, which nothing forced before
either fact was known (zen-engine's async API was undiscovered until this spike;
`compile_bundle`'s resolver-await need was invisible until the backend actually wired a real
SQLAlchemy session into it). **Ruled: one dated rule added to `.claude/skills/spec-change`
now** (this commit), rather than treating this as a recurring correction that will keep
firing silently: a `pricing-core` interface signature is declared `async def` exactly when
it directly awaits an injected async dependency or a native async binding from a caller
context that is itself async, and is declared plain `def` otherwise — and that fact is
checked against what the function actually calls (or, pre-implementation, against a spike
of the library it wraps) before the signature is written down, not defaulted and trusted.
This is not a rewrite of §5.2's other signatures — none of the other nine are shown wrong by
anything measured — it is the rule that stops a third instance from needing its own PR to
notice.

## Verification

`python3 scripts/audit-docs.py` run clean before commit. Three spec edits total across all
five rulings — the `FR-RATE-22` citation (Ruling 1), the `compile_bundle` `async def`
correction (Ruling 3), and the `score_one` `async def` correction (Ruling 5) — none
introduces a new `FR-`/`NFR-`/`ADR-` id. One tooling fix (Ruling 3's `async def` regex gap
in `scripts/audit-docs.py`'s FR-OVR-17 check), verified as a real positive/negative pair: it
failed with the spec corrected and the old regex in place, and passed once the regex was
fixed — never asserted clean without having first seen it red. One skill addition (Ruling
5's verification-step rule in `.claude/skills/spec-change`).
