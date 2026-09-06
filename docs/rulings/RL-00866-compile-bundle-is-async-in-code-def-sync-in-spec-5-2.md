---
id: RL-866
family: ruling
title: `compile_bundle` is `async` in code, `def` (sync) in spec §5.2
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-prework-rulings.md
---

## RL-866 — `compile_bundle` is `async` in code, `def` (sync) in spec §5.2

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
  (ADR-703)"). The backend's actual resolver
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
  `CompiledBundle` with, per `NFR-491`, "zero database or network access" — there is
  nothing to `await`, and keeping the scoring hot path free of event-loop overhead matters
  under `NFR-489`'s 50 ms budget. `compile_bundle` is the opposite case: it is
  definitionally the function that resolves pinned artifacts from durable storage, it runs
  rarely (compilation, not per-quote scoring), and per RL-865 it is about to become an
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
journey-citation check (FR-19) extracts declared `pricing-core` functions with
`re.finditer(r"^def ([a-z_][a-z0-9_]*)\(", ...)` — anchored on a bare `def `, with no
`async def` case. Making the spec's signature accurate (above) silently dropped
`compile_bundle` out of the declared-function set, which then failed
`WF-699-model-to-rating-version.md:58`'s existing, correct citation of `compile_bundle()` as
newly "undeclared." The check itself had never had to handle an async `pricing-core`
signature before — nothing in `03` §5.2 needed one until this ruling. Fixed to
`r"^(?:async )?def (...)\("`; re-run clean (`python3 scripts/audit-docs.py`: "journey
citations: 31 endpoints, 8 functions, all declared"). Verified as a real positive/negative
pair rather than asserted: the check failed with the old regex and the old (wrong, sync)
spec line both absent — i.e. it failed **because** the spec line changed and the checker
did not follow — and passed once the checker did.
