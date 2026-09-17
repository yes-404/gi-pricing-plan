---
id: RL-864
family: ruling
title: `POST /api/v1/rating-versions` has no route
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

# WK-671 pre-work rulings — the rating-version route gap and the compile status code (2026-08-29)

`CLAUDE.md` §0 code-vs-spec rulings, dispatched ahead of the §15 adoption record and
independent of it, ruled before WK-671's first slice touches the affected path — per the
standing rule that when code and spec disagree the platform stops and resolves it rather
than quietly making either side match the other. No plan is frozen for WK-671 yet; this record
is not a decision point against a plan — it is the dated home for rulings the auditor,
executor and planner found while reading the rating-engine surface ahead of that plan.
Rulings 1 and 2 were the first pair, found by the auditor's endpoint-axis sweep. Rulings 3
and 4, appended the same day, were found independently by the executor and planner while
scoping WK-671 slice 1 and are the same kind of situation: code and spec disagreeing, or a type
the spec relies on existing nowhere in code.

Every identifier, route literal, status code, error code and requirement id below is grepped
against `origin/main` `07ae047` before being written down (`CLAUDE.md` §12 — a ghost citation
cost WK-670 real time).

## RL-864 — `POST /api/v1/rating-versions` has no route

**The finding, restated precisely.** `03-rating-engine.md:512` declares
`POST /api/v1/rating-versions — Create a draft Rating Version with pins`, with no `(FR-RATE-n)`
citation in the cell. No route answers that path anywhere in the backend.

**Options, as dispatched:** (a) a capability nobody specified — needs a new `FR-RATE-` id and
a workstream to own building it; (b) a stale Phase-0 row — needs a tombstone per `CLAUDE.md`
§5 (ids and section numbers are never reclaimed, only marked superseded).

**Ruled: neither. This is a third case — a specified, current, Phase 2 capability whose
service layer is fully built and tested, and whose HTTP route was simply never wired. The
fix is code, not a tombstone and not a new requirement, and it is owned by WK-671.**

Rationale — read, not inferred:

- **The capability is specified**, just not by a citation in that one cell. `FR-237`
  (`03-rating-engine.md:133`) is exactly "a Rating Version pins: one Rating Algorithm
  version, an exact Rate Table Version per referenced table, an exact Model/Peril Structure
  version per `model_call`, an exact Reference Table Version per `lookup`... Nothing is
  unpinned" — the row's own words ("with pins") are FR-237's words. A missing inline
  citation is not unique to this row either: `03-rating-engine.md:505`
  (`POST /rate-tables/{slug}/versions — New Rate Table Version with change note`) cites
  nothing and nobody has proposed tombstoning it. Uncited routine create/list/get rows for a
  resource whose *structure* is defined at the data-contract level are this suite's normal
  convention, not a defect.
- **`WF-699` already walks through it, and already cites the requirement the table cell
  doesn't.** `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:56`, step C1: *"Pricing
  Actuary — `POST /rating-versions` — declares the algorithm version and every pin: rate
  tables, peril structure, reference tables. — `03` FR-237."* This is not a row a later
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
  silent omission; it was a stated, deliberate Phase 1b scope cut (`FR-440`, the WK-665 exit
  demo), and `CLAUDE.md` §0's table is explicit that a capability inside the current phase's
  scope is code, not a spec change. Phase 2 is now, and WK-671 is the workstream that needs the
  full rating-version write lifecycle to create, submit and approve the versions it scores
  against.
- **Ruling out the tombstone reading on its own terms.** `CLAUDE.md` §5's tombstone applies
  to a requirement or section that is no longer true — retired, superseded, or never going
  to be built. Nothing here is any of those: the capability is exercised by `WF-699`, it is in
  the current phase, and its data-contract half (`FR-237/238`) is unquestionably live.
  Tombstoning the row would misrepresent a real, currently-needed capability as abandoned.

**Disposition.** Code fix, not a spec change: add `POST /api/v1/rating-versions` and
`POST /api/v1/rating-versions/{id}/submit` route handlers in
`backend/src/app/api/models.py` (or a dedicated `api/rating_versions.py`, matching the
`api/rating_algorithms.py` pattern) calling the existing, already-tested
`create_rating_version` and `submit_for_review` service functions, gated on
`Permission.RATING_WRITE` / `Permission.RATING_SUBMIT` respectively — the same permissions
those functions already enforce internally. **Owner: the WK-671 scoring workstream**, as
prerequisite work before or alongside its first slice, since WK-671 cannot create or submit a
real (non-demo-seed) Rating Version to score against without it. This is not a new
workstream and not a register carry-forward past a close — it is in-phase completion work
the register can now file with a named owner, per the auditor's F-W10-3 precedent.

**Spec correction made in this commit (citation only, no new id, no meaning change):**
`03-rating-engine.md:512`'s row gains the `(FR-237)` citation `WF-699` already relies on,
so the table cell and the workflow document agree on what governs it.
