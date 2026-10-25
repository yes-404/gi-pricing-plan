---
id: RL-1900
family: ruling
title: SL-1552 (WK-675 S10) and SL-1553 (WK-675 S11) decided — RatingVersionView stays and /rating becomes the FR-25 entry; live badges are a client-side join over GET /api/v1/environments, "unavailable" on any failure; the list stays client-side filtered and unpaginated, its bound recorded as an OQ; a version's regression runs are listed by a new RegressionRunSummary, newest first, cursor-paginated; the suite view is read-only
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-25   # drafted 2026-10-22 under working id 8163; minted 2026-10-25 as RL-1900
owner: decision-maker
tree: f3462d8f
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1546, PL-1286, SL-1552, SL-1553, WK-675, FD-1283, FR-25, FR-238, FR-241, FR-260, FR-261, FR-1221, FR-1531, RL-1473, RL-1765]
---

# RL-1900 — SL-1552 (S10) and SL-1553 (S11): the five open design points of the rating version list and the regression suite view

Disclosure: drafted as **working id RL-1900** by the decision-maker seat dm-1552 (opus, Opus 5.5)
on 2026-10-22, on lead 26's brief `handover/brief-dm-1552-2026-10-22.md` (written 15:51:56 BST).
No maintainer entry in `to-lead.md` orders this record by number (read to line 29480 before 15:55:11 BST
on 2026-10-22; the last entry is "2026-10-22 15:52:54 BST"). The lead adopts, amends or rejects
this draft (`CLAUDE.md` §12) before it is minted; until then it binds nothing.

## Authority and scope

- **Why one `RL-` and not two `LG-` entries.** Lean P2 L1 (the decision-maker charter's Owns
  line) puts a ruling inside one slice in that slice's `LG-` build log, and a separate `RL-`
  only when it binds beyond the slice. `PL-1546` R10.1 (`docs/plans/PL-01546-*:187`) places
  DP-S10-1 in S10's `LG-` ("answered in its `LG-`"). This record rules points for **two**
  slices before either starts (the charter: the decision-maker "pre-resolves every decision
  point before its slice starts"), and DP-S10-3 binds the S7 picker (`RL-1765`) as well. If
  the lead prefers L1's form, each ruling below moves verbatim into its slice's `LG-` Scope
  and this draft is withdrawn; the rulings do not change.
- **Ruled here:** DP-S10-1, DP-S10-2, DP-S10-3, DP-S11-1, DP-S11-2, as put by planner-1552's
  prep `scratch/sl1552-1553-prep.md` §1.6 and §2.6 (read 2026-10-22).
- **Not ruled here (the lead's or the maintainer's — listed in "What it obliges"):** the
  order grounds (S10's "S8 (order, item D)"; S11 after S10), the GO of either slice, and the
  allocation of the OQ's working id.

## Verified first, at origin/main f3462d8f

All reads at `origin/main` f3462d8f (= worktree `rl-8163` HEAD); branch reads name their sha.

- **Scope rows.** `docs/plans/PL-01546-*:151` (row 6, S10: "`03` §3.4: one new FR (spec first,
  R10.1); FR-25; `FD-1283` option A") and `:152` (row 7, S11: "a run-list read route under DP-4
  (a) only if the version's evidence gives no run id"). `docs/plans/PL-01286-*:313` (S10: "each
  row links to the version's `:slug/v/:version` routes, which **removes the interim FR-25
  path** through `RatingVersionView`") and `:314` (S11: "**if not, the run-list read route is
  added under DP-4 (a), spec first (a new FR plus its §5.1 row), in S11**").
- **R10.1** (`docs/plans/PL-01546-*:179-187`): S10 amends the existing §5.1 list row, adds no second row;
  "Whether `RatingVersionView` stays is S10's question (`RL-1473:124-126`)". `RL-1473:124-125`:
  "Whether `RatingVersionView` (`/rating-versions/:id`) stays after S10 is S10's leaf plan's
  question." **R8.1** (`docs/plans/PL-01546-*:193-194`, quoting `RL-1473:200`): S10 and S11 add no second
  lookup.
- **`RL-1765`** (`docs/rulings/RL-01765-*:111-113`): "Pagination, filtering by status or slug,
  and sort order across slugs stay S10's (`PL-1286:313`). If S10 changes the response shape,
  S10 keeps the S7 picker test green or updates it in the same commit."
- **The spec** (`docs/specs/03-rating-engine.md`): `:138` FR-238 ("`live` is a property of a
  Deployment, and the same Rating Version can be `live` in `uat` and not in `prod`"); `:141`
  FR-241 (effective dates); `:144` FR-1531 (address by `slug@version`); `:1066` the list row
  ("**200** with a `RatingVersion[]` (§4.3), unpaginated … S10 (`SL-1552`) amends this row
  with its own FR and the list view's needs; it does not add a second row"); `:1077-1079` the
  run routes (POST 202; GET by `{run_id}`; GET `…/cases`, "**Deliberately unpaginated:**" with
  its bound stated — the precedent for a recorded bound); `:917-918` (approval evidence reads
  the run whose `bundle_hash` equals the version's current bundle hash, `RL-1172` item 4);
  `:1432` and `:1436` the two §5.3 rows. `docs/specs/00-overview.md:238` FR-25.
- **The badge's data.** `packages/model-schema/src/model_schema/deployments.py:48-56`
  (`LiveDeployment.rating_version_ref: ArtifactRef`) and `:74-76` (`Environment.live_deployments`,
  "Derived from the Deployment rows, never stored."). `ArtifactRef` is on the wire the string
  `{type}:{slug}@{version}` (`refs.py:85`; contract example `rating_version:motor-gb@27`).
  `backend/src/app/api/environments.py:36` `ReadEnvironmentsDep = … Permission.SETTINGS_READ`;
  `:39-50` `GET /environments` returns **`Page[Environment]`, cursor-paginated** (`cursor`,
  `limit`; `api/pagination.py:37-38` DEFAULT_LIMIT 50, MAX_LIMIT 200) — the prep did not
  note this; DP-S10-2 accounts for it. `frontend/src/api/paging.ts:18` `PAGE_SIZE = 200`,
  `:38` `pageThrough`. `packages/model-schema/src/model_schema/permissions.py:137-157`: every
  built-in role (analyst, pricing_actuary, approver, deployer, auditor, admin) holds both
  `rating:read` and `settings:read`; `:14` custom roles exist ("supports custom roles composed
  from this same vocabulary").
- **The run id.** `model_schema/rating.py:140-146` `RatingVersionEvidence.regression_suite_run_id`
  is written by the submit gate only (`backend/src/app/platform/rating_versions.py:403-407`).
  `backend/src/app/worker/rating_handlers.py:205-214`: a failing run raises `PlatformError(…,
  409, "… regression run {saved.id} is recorded.")` — the id in prose only; only a pass returns
  `JobResult(kind="artifact", ref=f"regression_run:{saved.id}")`. `RegressionRun`
  (`model_schema/regression.py:317-329`; generated contract properties: bundle_hash,
  cases_blob, finished_at, generation, golden_results, job_id, overall, property_results,
  rating_version_ref, started_at, suite_content_hash, suite_ref) carries **no `id`**;
  `finished_at` is required (`:328`). `backend/src/app/platform/regression_runs.py:63-81`
  `latest_run` orders `finished_at desc, id desc`. So a draft version, and any failing run,
  has no machine-readable run id: PL-1286's S11 condition fires.
- **What S10 meets on SL-1551** (`origin/sl-1551-wk675-s8` @04b632b5, unmerged):
  `RatingVersionView.vue` gains the link `/rating/${rating.slug}/v/${rating.version}/dislocation`
  ("Open the dislocation views"); `DislocationView.vue:85-89` links back to
  `/rating-versions/${rating.id}`. On main, `DemoView.vue:222-226` links to
  `/rating-versions/${rating.id}`; `listRatingVersions` (`api/ratingVersions.ts:7`) feeds
  `QuoteSandboxView.vue:62` (the S7 picker) and `DemoView.vue:72`.

## Ruled

### DP-S10-1 — Does `RatingVersionView` (`/rating-versions/:id`) stay? — **(a) it stays**

Options: (a) keep it as the by-id detail page; `/rating` becomes the FR-25 entry and its rows
link straight to each `/rating/:slug/v/:version/…` view; (b) retire it — redirect to
`/rating/:slug/v/:version/design`, re-point `DemoView.vue:224` and `DislocationView.vue:87`,
delete its tests.

**Ruled (a).** PL-1286:313 asks S10 to remove the interim FR-25 *path*, not the page: once
`/rating` (linked from the app's navigation) links every version's `:slug/v/:version` routes,
no such route depends on the by-id page for reachability. (b) has no requirement behind it,
widens S10's write set into the exit-demo guide (`DemoView`) and SL-1551's just-built back-link,
and buys only tidiness. S10's `LG-` cites SL-1551's `RatingVersionView` dislocation link (the
maintainer's 2026-10-21 16:23:35 item 2(b), as the prep quotes it from `to-lead.md:28541`) and
this ruling in place of deciding the question itself. Retiring the page later is a spec-free
clean-up any slice may propose.

### DP-S10-2 — The live badge's source — **(a) a client-side join over `GET /api/v1/environments`**

Options: (a) the view reads every page of `GET /api/v1/environments` and joins each
`live_deployments[].rating_version_ref` to a row; (b) a derived `live_in` field added to
`RatingVersion` (§4.3) — a model-schema and contract change, the S7 picker re-checked;
(c) a new `?include=live` variant of the list route.

**Ruled (a)**, with these terms, which S10's new §3.4 FR states:

1. **Source:** `Environment.live_deployments` (FR-238: live is a property of a Deployment).
   A row shows one badge per environment whose `live_deployments` holds a `rating_version_ref`
   equal to `rating_version:{slug}@{version}` of that row (FR-1531's pair; no `id` join, no
   second lookup, R8.1). A version live in several environments, or one environment holding
   several live versions under date-based routing (as FR-241 states), shows every match.
2. **All pages.** `GET /environments` is cursor-paginated (`Page[Environment]`); the view reads
   every page (`pageThrough`, `PAGE_SIZE` 200). A first page alone is not the source.
3. **Unknown is never "not live".** On a 403 (`settings:read` absent — a custom role), or any
   failure reading any page, the badge column for every row reads **"unavailable"**; no partial
   set of badges is shown. An empty badge cell means "read, and live nowhere".

Why: no new shape (CLAUDE.md §2: nobody hand-writes or adds a shape without need), the live set
is already derived server-side and "never stored", and every built-in role holds both
permissions. (b) puts a derived, environment-dependent fact into the `RatingVersion` artifact
shape and its contract, and touches the S7 picker for no gain in P2; (c) adds a route variant
for the same join. (b) becomes right if a custom role holding `rating:read` without
`settings:read` becomes a target user — a supersession of this item, not a silent change.

### DP-S10-3 — Filters, sort and pagination of the list — **(a) client-side over the unpaginated list; the bound recorded as an OQ**

Options: (a) no route change — filter by status and group/sort by slug in the view over the
existing unpaginated `RatingVersion[]`; (b) add `?status=`, `?slug=` and a cursor — a backend
change, the contract regenerated, the S7 picker updated in the same commit (`RL-1765`).

**Ruled (a).** The route already serves the S7 picker unpaginated (`03:1066`); (a) keeps S10
frontend plus spec only (no Python closure, no contract regeneration, the picker untouched),
and RL-1765's same-commit obligation does not arise. S10's amendment to the `03:1066` row
(in place, dated, no second row) names the list view as a consumer and states the list is
**unpaginated by decision (this record)**. Unlike `03:1079`'s "deliberately unpaginated"
row, no cap bounds the number of Rating Versions in a workspace: the expectation that a
workspace holds tens rather than thousands is **an assumption, not a measurement**, so it is
recorded as an **`OQ-`** — *"When does `GET /api/v1/rating-versions` need server-side
pagination and filtering (status, slug), and at what workspace size?"* — owned by WK-675,
options (i) paginate with a cursor and filters, (ii) keep unpaginated with a stated cap,
recommendation (ii) until a measured workspace exceeds a figure the OQ names; timing: decided
at the §14 plan review before the P2 exit demo. The OQ needs a working id (see "What it
obliges"); it is recorded by a decision-maker in this draft, or in the batch that mints it,
before S10 merges, so the bound is never silent.

### DP-S11-1 — The run-list route and its shape — **(a) a new `RegressionRunSummary`, newest first, cursor-paginated**

Options: (a) a new `RegressionRunSummary`, listed by a new route, the view reading the full run
by id; (b) `RegressionRun[]` with an `id` added to `RegressionRun` (§4.9) — a change to a
persisted contract, returning every run's golden results and counterexamples in bulk; (c) no
list — a `latest` read.

**Ruled (a)**, spec first in S11 (a new `03` §3.8 FR, its §5.1 row beside `03:1078`, the shape
in §4.9), as PL-1286:314 already scopes it under DP-4 (a):

- **Route:** `GET /api/v1/rating-versions/{id}/regression-runs` — `rating:read`; **404**
  `NOT_FOUND` for another workspace's version exactly as for one that does not exist (FR-1531);
  401; 403. It must not shadow `…/regression-runs/{run_id}` (a test asserts the `{run_id}` read
  still resolves).
- **Response:** `Page[RegressionRunSummary]`, the existing cursor convention and limits;
  **newest first by `finished_at desc, id desc`** — the order `latest_run` already uses
  (`regression_runs.py:81`).
- **`RegressionRunSummary`** (model-schema, contract regenerated): `id`, `job_id`, `overall`,
  `bundle_hash`, `suite_ref`, `suite_content_hash`, `started_at`, `finished_at`. No golden
  results, property results, counterexamples or `cases_blob`: those stay behind the by-id read
  and `…/cases` (FR-1221, NFR-499).
- **The view** defaults to the newest run, accepts `?run=<id>` (the precedent of SL-1551's
  `DislocationView.vue:4-5` @04b632b5, FR-265), and marks the run that `evidence.regression_suite_run_id` names, which need not be
  the newest (`03:917-918`).

Why: the persisted `RegressionRun` is untouched; a summary carries no quote-input fragment, so
listing adds no NFR-499 surface; it serves "latest", history and a failing run's id alike. (b)
changes a persisted contract and multiplies counterexamples per response; (c) is smaller but
cannot show history nor a pinned evidence run that is not the latest.

### DP-S11-2 — Does the view start a run? — **(a) read-only**

**Ruled (a).** `03:1436` lists reads only; a "Run suite" control (POST 202, `rating:compile`)
is outside the §5.3 contents and S11's scope row. A later slice may add it as its own scope.

## What it obliges

- **S10 (SL-1552), spec first in one commit with its code and tests:** a new `03` §3.4 FR
  carrying DP-S10-2's three terms and DP-S10-1's linking (rows link by `slug@version`); the
  `03:1066` row amended in place per DP-S10-3; §5.3 `:1432` unchanged unless the contents change.
  `RatingVersionView`, `DemoView` and `DislocationView` are not changed by S10.
- **S11 (SL-1553), spec first:** the new §3.8 FR, the §5.1 row, the §4.9 summary shape, per
  DP-S11-1; a read-only view per DP-S11-2.
- **Rendering rules already decided elsewhere** (the prep §2.6 lists them; not re-ruled here):
  money from minor-unit integers (FR-10, FR-21); `counterexample_minimal: false` shown as
  unminimised (`03:908`); no empty counterexample for `MONOTONE_NO_COMPARABLE_PAIRS`;
  `not_checked` golden evidence shown as "no golden quotes were checked" (FR-260).
- **For the lead (not ruled here):**
  1. **The OQ's working id** (DP-S10-3) — allocate one; a decision-maker records the OQ row
     (open-questions.md, the `03` §10 mirror, the roadmap §10 gate row) before S10 merges.
  2. **S10's order ground** — "S8 (order, item D)" was relaxed for building on 2026-10-21
     15:10:53 per the prep; S10 also consumes SL-1551's files, so its GO line should name which
     ground it rests on.
  3. **S11 after S10** — both edit `router/index.ts` and the reachability test, and S11's entry
     link lives in S10's list; serialising is an order call.
  4. **GO preconditions** — SL-1551 (@04b632b5) and SL-1260 (@7b9f2684, the §3.4 and §5.1
     serialisation of R10.2 and PL-1286:396-398) are unmerged at f3462d8f.
  5. **Record form** — whether this stays an `RL-` or moves into the two `LG-`s (Authority).

## Acceptance — the violation that must become detectable

The violation: a list view that shows a version as not live when the live set was never read,
or a run list that exposes counterexamples or loses a failing run's id.

- *Violation: `GET /api/v1/environments` answers 403 (or any page fails) and a row renders with
  no badge or a "not live" mark* — S10's view test stubs the 403 and asserts "unavailable" on
  every row.
- *Violation: environments span two pages and the badge for a version live only in an
  environment on page 2 is missing* — S10's view test stubs two pages.
- *Violation: version A's run list includes version B's run, another workspace's version answers
  anything but 404, a failing run is absent or has no `id`, or the order is not newest first* —
  S11's backend test, `@pytest.mark.req` on the new FR, red at its test commit.
- *Violation: a `RegressionRunSummary` carries `golden_results`, `property_results` or
  `cases_blob`* — S11's model-schema test asserts the field set; `generate-contracts.py --check`
  holds the contract to it.
- *Violation: the S11 view renders a control that POSTs a regression run* — S11's view test
  asserts no such request is made.

No check is attached to DP-S10-1 or DP-S11-2 beyond the above: each is a scope decision whose
breach would be a write outside the slice's ruled write set, which the slice audit reads.

## Adoption

Adopted as drafted on 2026-10-23 by the maintainer (by delegation), to-lead "2026-10-23 11:14:56 BST" item (A); DP-S10-4 (the list's display order) was decided in the same entry, item (B), and is recorded in `03` FR-1903 and in LG-1902. This line was appended in SL-1552's PR, which carries the record (Lean P2 L1, common brief item 34); the working id is renumbered at the mint.
