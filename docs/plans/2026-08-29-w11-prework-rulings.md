# W11 pre-work rulings — the rating-version route gap and the compile status code (2026-08-29)

Two `CLAUDE.md` §0 code-vs-spec rulings, dispatched ahead of the §15 adoption record and
independent of it. Both are ruled before W11's first slice touches the affected path, per
the standing rule that when code and spec disagree the platform stops and resolves it rather
than quietly making either side match the other. No plan is frozen for W11 yet; this record
is not a decision point against a plan — it is the dated home for two blocking rulings the
auditor found while running the endpoint axis over the whole RATE module.

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

## Verification

`python3 scripts/audit-docs.py` run clean before commit (the only spec edit is the one-line
citation addition in Ruling 1; no new `FR-`/`NFR-`/`ADR-` id is introduced by either ruling).
