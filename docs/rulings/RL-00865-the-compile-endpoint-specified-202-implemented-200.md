---
id: RL-865
family: ruling
title: the compile endpoint: specified `202`, implemented `200`
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

## RL-865 — the compile endpoint: specified `202`, implemented `200`

**The finding, restated precisely.** `03-rating-engine.md:513` declares
`POST /api/v1/rating-versions/{id}/compile — **202** Compile + validate the bundle
(FR-240)`. The implemented route
(`backend/src/app/api/models.py:1139-1161`) has no `status_code` override and its own
docstring says `"""**200** with the compiled Bundle's metadata (FR-239/240)."""`
(`:1149`) — code and spec disagree on the same requirement citation.

**Options:** (a) the code is right — amend `03` §5.1 to `200`; (b) the spec is right — fix
the code to return `202` with a Job.

**Ruled: (b) — the spec's `202` is correct. The code's `200` is a Phase-1b synchronous
stand-in, and completing it to `202`+Job is WK-671 slice-1 work — the same slice that must
already stop discarding the compiled Bundle.**

Rationale:

- **A second, independent document already agrees with `03` §5.1, and names the Job kind.**
  `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:57`, step C2: *"Pricing Actuary —
  `POST /rating-versions/{id}/compile` → `202` + Job (`rating.compile`). — `07` FR-399."*
  This is not one row read in isolation; the module's own cross-module workflow account
  independently states `202` and names the specific Job kind.
- **The platform's typed Job infrastructure already has this Job kind — unused.**
  `packages/model-schema/src/model_schema/jobs.py:53` defines
  `RATING_COMPILE = "rating.compile"` in the `JobKind` enum, matching `WF-699`'s citation
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
  `NFR-492` (`03-rating-engine.md:779`): "Bundle compilation for a large motor structure
  completes in < 60 s; bundle size stays under 500 MB including booster artifacts." A
  60-second, up-to-500 MB synchronous POST is exactly the shape of work this codebase's own
  stated convention treats as `202`. The `predict` route's own docstring
  (`backend/src/app/api/models.py:1064-1076`) draws the line in this exact module: *"a fit,
  a comparison, a backtest and a transparency artifact all read a whole dataset version"* →
  `202` (naming `FR-186/139/192/94`), while `predict` itself stays `200` only because it
  "reads at most `MAX_PREDICT_ROWS` rows the caller sent." Bundle compilation resolves every
  pinned artifact a Rating Version references — potentially a large rate table and a loaded
  GBM booster — which is the "reads a whole large artifact" side of that same line, not the
  bounded-request side.
- **The code cannot honour `FR-239` today regardless of status code, which is the more
  urgent half of this ruling for WK-671.** `FR-239` (`03-rating-engine.md:135`): the Bundle
  "is what gets cached and distributed." The implementation
  (`backend/src/app/platform/rating_versions.py:273-288`) computes the full `Bundle`
  (`graph`, `resolved_payloads`, `pins`) via `compile_bundle()`, then persists only
  `{content_hash, bytes, compiled_at}` onto the row and returns that dict — the compiled
  object itself is discarded when the function returns. Nothing loads a bundle back. This is
  the planner's own finding, confirmed directly in the source: there is currently no code
  path that could serve `NFR-491` ("a compiled bundle scores with zero database or
  network access; everything it needs is inside it") because nothing durable holds "it."
  Fixing persistence and fixing the status code are one piece of work, not two: the natural
  shape is a `RATING_COMPILE` worker handler that calls `compile_bundle()`, writes the full
  `Bundle` to the blob store (`07-platform.md:112-114`, `FR-418/419`, content-addressed,
  matching how `DislocationRun.largest_movers_blob` and the W10-3D rate-table-diff Job already
  do it), and records the blob reference — not only the three scalar fields — on the
  version's `bundle` metadata.
- **No competing argument survives.** The only way `200` could be right is if bundle
  compilation is reliably cheap and bounded, but `NFR-492`'s own 60 s / 500 MB ceiling was
  set deliberately and nothing in the record revises it downward. Treating a
  potentially-60-second POST as synchronous risks exactly the HTTP-timeout and
  worker-thread-exhaustion failure mode the platform's own `202` convention exists to avoid,
  on the one endpoint in this module that resolves the most artifacts at once.

**Disposition.** Code fix, WK-671 slice 1 (the same slice the dispatch already names for
Bundle persistence): register a `JobKind.RATING_COMPILE` handler in
`backend/src/app/worker/` alongside the existing `rate_table_handlers.py` /
`model_handlers.py` pattern; change `POST /rating-versions/{id}/compile` to submit that Job
and answer `202`; persist the full `Bundle` to the blob store, not only its metadata. No
spec change — `03` §5.1 and `WF-699` already say `202` correctly; the code is what moves.

**Related finding, not ruled here (flagging for the same slice).** The compile resolver's
`_Resolver.resolve()` (`backend/src/app/platform/rating_versions.py:240-271`) only handles
`ref.type in {"rating_algorithm", "model"}` and raises `NOT_FOUND` for anything else,
including `rate_table`, with the comment "Rate tables... have no backend tables yet
(Phase 2)." That comment predates WK-670: `RateTable`/`RateTableVersion` now have real backend
tables (`docs/plans/PL-00829-wk-670-implementation-plan-rate-tables-seeding-diffs-bulk-operations-import-export.md`, merged). Per `FR-237`, essentially
every real Rating Version pins at least one rate table, so today's resolver would refuse to
compile any of them. This is not a code-vs-spec disagreement — the spec was always right and
the comment is simply stale — so it needs no ruling, only a fix, and it lands in the same
WK-671 slice as the two rulings above since none of the three is separable from the others.
