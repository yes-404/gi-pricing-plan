---
id: RL-1934
family: ruling
title: SL-1553 (WK-675 S11) open points decided — S11 owns the list row's /tests link and amends S10's FR by a dated clause; the run list pages with the platform's limit and cursor; the tie-break is the run's UUIDv7 id and the cursor is the last row's id, resolved on the server
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; DRAFT until the maintainer adopts it and it is minted
created: 2026-10-26               # drafted 2026-10-25 under working id 8217
owner: decision-maker
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1553, SL-1552, WK-675, PL-1546, PL-1286, FD-1283, FR-25, FR-260, FR-261, FR-450, FR-1221, FR-1531]
---

# RL-1934 — SL-1553 (S11): the three open points of the regression suite view's spec text

**DRAFT — binds nothing until the maintainer adopts it.** Drafted 2026-10-25 by the
decision-maker (seat dm-1553) on lead 28's brief `brief-dm-1553-2026-10-25.md`. The working ids
in prose (RL 8163, FR-1932, FR 8209, OQ 8206, LG-1933, this record's 8217) are not minted.

## Authority and scope

- **The open points, verbatim** — exec-1553's FINAL as the lead logged it in
  `from-lead-2026-10-09.md` (entry "2026-10-23 11:53:22 BST Lead 27"): *"open points: S10's
  /tests link ownership, pagination param names vs backend/src/app/api/pagination.py, the
  tie-break id type"*. The lead's handover of 2026-10-23 (`lead-handover-2026-10-23-pause.md`
  §5, SL-1553 row) repeats them: *"Open points for the DM/lead in from-lead 11:5x (the /tests
  link ownership; pagination param names; the tie-break id type)."* exec-1553's own message
  was not found in a file. These two relays are the fullest text of the questions, and the
  questions below are read from them.
- **What this rules on.** RL 8163 (adopted, to-lead "2026-10-23 11:14:56 BST" (A); draft
  `origin/draft/rl-8163` @d4258b95) and its DP-S11-1 and DP-S11-2. DP-S11-3 is in the same
  entry, item (C): *"S11 (SL-1553) is serialised after S10 merges (prep §2.3: router block +
  list-row link, §8(b))"*. The S11 spec text is on `origin/sl-1553-wk675-s11` @5b26a818:
  FR-1932 at `03:185`, the §4.9 `RegressionRunSummary` paragraph at `03:921-927`, the §5.1 row
  at `03:1113` and the §5.3 row at `03:1473`.
- **Why this is an `RL-` and not an LG line.** Point 3 corrects an adopted ruling.
  RL 8163 DP-S11-1 says both *"the existing cursor convention and limits"* and *"newest first
  by `finished_at desc, id desc`"*, and at ff976406 the existing cursor convention cannot carry
  that order (see below). This record makes the two clauses agree. Points 1 and 2 bind only
  inside the slice, so under Lean P2 L1 they could go in LG-1933. Whether to split them out is
  the lead's call (see "For the lead").
- **Trees read.** `origin/main` ff976406 (the code facts below), `origin/sl-1553-wk675-s11`
  5b26a818 (S11's text), `origin/sl-1552-wk675-s10` 4a4efdd1 (S10's FR 8209; the branch has
  moved since the handover's 95d7eac7).

## Ruled

*Proposed: the maintainer adopts.*

### Point 1 — Who owns the list row's `/tests` link? — **(a) S11 adds it, amending S10's FR by a dated clause**

**Facts.**
- At 4a4efdd1, S10's FR 8209 (`03:145`) item (4) reads: *"Each row links by its `slug@version`
  (FR-1531), with no second lookup, to `/rating/:slug/v/:version/design`, `/sandbox` and
  `/dislocation`, and to `/tables/:tableSlug` for each rate table the version pins."* It does
  not mention `/tests`. No frontend source on that branch outside `__tests__` contains `/tests`
  (`git grep -n -E "/tests|tests\`" origin/sl-1552-wk675-s10 -- frontend/src`: the only hits are
  two `type_iii_tests` comments in `GlmDiagnosticsPanel.vue`).
- The `/tests` route does not exist until S11 registers it. FR-25 (`00:238`) requires every
  registered route to be reachable by links alone, and
  `frontend/src/router/__tests__/reachability.test.ts` enforces this from `router/index.ts` and
  `App.vue`.
- RL 8163 "For the lead" item 3 says *"S11's entry link lives in S10's list"*. The maintainer's
  DP-S11-3 serialises S11 after S10 on the grounds *"router block + list-row link"*. Nobody
  ruled whether S10 or S11 writes the link.
- At 5b26a818, FR-1932 (`03:185`) item (4) describes the view but names no entry link.

**Options.**
- **(a) S11 adds it.** S11 adds `/tests` to each list row. It amends FR 8209 item (4) with a
  dated clause naming FR-1932, in the same commit as its router entry. S11 already edits the
  router and the reachability test, and it lands after S10's squash, so editing S10's file
  cannot conflict.
- **(b) S10 adds it now.** The link would point at a route that does not exist until S11.
  Either it is a dead link while S10 is on main alone, or S10 waits for S11's route, which
  turns the ruled order (S11 after S10) upside down.
- **(c) No list link.** The view would be reached only from a per-version view, for example a
  link from `/design` or from `RatingVersionView`. This adds an entry point that §5.3 does not
  name. It also leaves `/rating`, the FR-25 entry under RL 8163 DP-S10-1, without the one
  per-version route it lacks.

**Recommended: (a).** The link belongs to the slice that makes its target exist. The order
DP-S11-3 already ruled makes this conflict-free. One dated clause keeps FR 8209 true about
every link its rows carry.

### Point 2 — Which pagination parameter names? — **(a) the platform's `limit` and `cursor`, with its constants**

**Facts (ff976406).**
- `00` §5.2 (`00:356-363`): *"Cursor pagination everywhere"*, in the form
  `?limit=50&cursor=<opaque>` → `{"items", "next_cursor", "total_estimate"}`. FR-450 binds the
  API to `00` §5 exactly.
- `backend/src/app/api/pagination.py`: `DEFAULT_LIMIT` (`:37`), `MAX_LIMIT` (`:38`),
  `COUNT_CAP` (`:43`), `Page[T]` (`:48`, `items` / `next_cursor` / `total_estimate`),
  `encode_cursor` (`:64`), `decode_cursor` (`:102`), `decode_int_cursor` (`:91`). Every list
  route in `backend/src/app` takes `cursor: str | None = None` and
  `limit: … Query(ge=1, le=MAX_LIMIT) = DEFAULT_LIMIT`. Predicate:
  `grep -rn -E "limit: .*Query|cursor: .*Query" backend/src/app/api` and
  `grep -rn -E "encode_cursor\(|decode_cursor\(|decode_int_cursor\(" backend/src/app`. The one
  exception is `reference_tables.py:253` (`le=1000`, default 200), a route-specific bound.
- On the client, `frontend/src/api/paging.ts:48` sends `query: { ...query, cursor, limit:
  PAGE_SIZE }`, with `PAGE_SIZE` (`:18`) commented as *"The server's `MAX_LIMIT`"*. The
  `vue-frontend` skill (§"Collections are cursor-paginated") says `next_cursor` is opaque and
  is passed back verbatim.
- At 5b26a818, S11's §5.1 row (`03:1113`) already writes
  `…/regression-runs?limit=&cursor=` → `Page[RegressionRunSummary]`. `03:1085` and `03:1087` (at ff976406)
  write the same two names, in either order.

**Options.**
- **(a) `limit` and `cursor`**, with the defaults and caps of `DEFAULT_LIMIT` and `MAX_LIMIT`
  by symbol. The response is `Page[RegressionRunSummary]`.
- **(b) A route-specific bound**, as on `reference_tables.py:253`. Nothing here asks for one: a
  version's run count grows slowly, and the view pages through it.
- **(c) Unpaginated**, as `…/cases` is. That route can be unpaginated because a cap bounds it
  (`RegressionGeneration.cases` ≤ 10 000, `03` §5.1). Nothing caps the number of runs per
  version, so (c) is not available.

**Recommended: (a).** It is the convention 00 §5.2, FR-450, every list route and the
frontend's `pageThrough` already share. S11's row already says it, so the spec text needs no
change.

### Point 3 — The tie-break id's type, and how the cursor carries a two-key order — **(a) the run's UUIDv7 primary key; the cursor is the last row's id, and the server resolves its position**

**Facts (ff976406).**
- `RegressionRunRow.id` is `Mapped[UUID]`, `primary_key=True, default=new_uuid7`
  (`backend/src/app/db/models.py:2570`). It is the `{run_id}` of the by-id read
  (`backend/src/app/api/models.py:1375-1377`, `run_id: UUID`). The persisted `RegressionRun`
  has no `id` field (`packages/model-schema/src/model_schema/regression.py:317-333`). The row
  is insert-only in application code (`models.py:2596`), so a run's `finished_at` never changes
  after it is written.
- `latest_run` orders by `finished_at.desc(), id.desc()`
  (`backend/src/app/platform/regression_runs.py:81`). RL 8163 DP-S11-1 adopted that order for
  the list.
- The platform cursor encodes **one** key: `encode_cursor(value: UUID | int)`
  (`pagination.py:64`). Most lists order by a UUIDv7 id alone and page with `id < after`. In
  `jobs.py:129-131` the comment reads *"UUIDv7 is time-ordered, so one column gives both a
  stable sort and a unique cursor — a (timestamp, id) pair would be needed for a random
  key"*. `deployments.py` (the history list) does the same.
- **There is a precedent for a two-key order with a one-key cursor.**
  `list_environments` (`backend/src/app/platform/environments.py:174-203`) orders by
  `promotion_order, id`, issues `encode_cursor(page[-1].id)`, and resumes from that row's
  position. An id it cannot find answers **400** `VALIDATION_FAILED` "Malformed cursor".
- At 5b26a818, S11's text names the order (`03:185` item (2); `03:1113`) and the type of `id`
  only as *"the run's identifier, the `{run_id}` of the by-id read"* (`03:921-927`).

**Options.**
- **(a) UUID tie-break, one-id cursor resolved on the server.** The `RegressionRunSummary.id`
  is the row's UUID (`string`, `format: uuid` on the wire). The order stays
  `finished_at desc, id desc`, as RL 8163 adopted it. `next_cursor` is
  `encode_cursor(<last row>.id)`. The handler decodes it with `decode_cursor`, loads that run's
  `finished_at` **within the same workspace and Rating Version**, and resumes with the row
  value `(finished_at, id) < (cursor_finished_at, cursor_id)`. An id that is not a run of this
  version answers 400 `VALIDATION_FAILED`, as `list_environments` does. `pagination.py` does
  not change. Cost: one indexed primary-key lookup per page after the first.
- **(b) A composite cursor codec.** A new `encode_cursor` form in `pagination.py` would carry
  `(finished_at, id)` and keep the order with no lookup. It adds a second cursor format to a
  shared module for one route, plus a timestamp round-trip (timezone, precision) that the
  opaque cursor would then depend on.
- **(c) Order by `id desc` alone.** This is the jobs and deployments convention. It needs no
  lookup and no codec change, but it **amends RL 8163 DP-S11-1** and the FR-1932 / §5.1 text
  ("the order the latest-run read already uses"). The row's id is minted when `persist_run`
  flushes, after the worker sets `finished_at`. Two runs finishing close together on workers
  with skewed clocks could then sort differently from `latest_run`.
- **(d) A new integer sequence column**, paged with `decode_int_cursor`. This needs a migration
  for a tie-break the primary key already provides.

**Recommended: (a).** The tie-break needs only uniqueness, and the primary key gives it. (a)
keeps the order RL 8163 adopted, which is also `latest_run`'s. It reuses the existing cursor
helpers, and it follows a pattern already on main (`list_environments`). It corrects only the
reading of RL 8163's *"existing cursor convention"*: the convention is the opaque one-id
cursor, and here it is resolved by position rather than by `id < after`.

## What it obliges

In S11 (SL-1553), spec first, once this record is adopted:

- **Point 1 (the `/tests` link).** (i) FR 8209 item (4) gets a dated clause: *"Amended
<date>, WK-675 S11 `SL-1553`, FR-1932: and to `/rating/:slug/v/:version/tests`."* The row text
is not rewritten. (ii) The S10 list view gains the link, built from `slug@version` with no
second lookup. (iii) `router/index.ts` registers `/tests`, and `reachability.test.ts` stays
green with **no** entry added to its unreachable-routes list. (iv) S11's view-test set adds the
list view's own test file, because it changes that file (import closure, common item 29).
- **Point 2 (parameter names).** The handler signature is
`cursor: str | None = None, limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT`.
The response is `Page[RegressionRunSummary]`, with `total_estimate` counted up to `COUNT_CAP`.
The client reads through the generated API types: it uses `pageThrough` or a single page with
"load more", never a hand-written page shape (CLAUDE.md §2). No spec edit is needed.
- **Point 3 (tie-break and cursor).** (i) The §4.9 paragraph (`03:921-927`) gets one dated sentence:
*"`id` is the run's UUID (the `regression_runs` primary key, UUIDv7); it is the order's
tie-break and the cursor's key."* (ii) The §5.1 row (`03:1113`) gains *"; 400
`VALIDATION_FAILED` for a cursor that is not a run of this version"*. (iii) The handler
follows (a): one UUID cursor, a `(finished_at, id)` row-value comparison, and the cursor run
loaded under the same workspace and version filters, so a foreign run id cannot be used to
probe another version (FR-1531 posture). (iv) S11's backend test, carrying
`@pytest.mark.req` on FR-1932, pins: two runs with equal `finished_at` order by `id`
descending; paging with `limit=1` across them returns each exactly once; a cursor naming
another version's run answers 400. The test is red at its test commit.

## For the lead (not ruled here)

1. **Record form.** Point 3 corrects how RL 8163 DP-S11-1 is read, so it stays an `RL-`.
   Points 1 and 2 bind only inside S11 and, under Lean P2 L1, could be entries in LG-1933
   instead. Keep this record whole or split it.
2. **Minting.** Under item 34, this record mints in SL-1553's PR, after RL 8163 (which mints in
   S10's PR), with the adoption line appended.

## Acceptance — the violation that must become detectable

- *Violation: `/tests` is registered but no list row links to it.* `reachability.test.ts` is
  red, or the route sits on its unreachable list. Both are caught at S11's gate.
- *Violation: the route takes another parameter name, or ignores `MAX_LIMIT`.* The generated
  contract (`generate-contracts.py --check`) and a `limit=MAX_LIMIT+1` → 422 case in S11's
  backend test catch it.
- *Violation: equal-`finished_at` runs repeat or vanish across pages, or another version's run
  id is accepted as a cursor.* S11's backend paging test (point 3 (iv)) catches it.
