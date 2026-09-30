---
id: FD-9693
family: finding
title: Five 07 §5.3 platform views (Jobs, Job detail, Service accounts, Settings, System status) are owned by no Work, and none is built
status: active
created: 2026-09-30
owner: auditor
tree: 880feb499eddb9e854c525770e95fb19373a2311
corrected_by: []
relates: [WK-658, WK-664, WK-674, WK-675, WK-676, WK-1251, FD-9692]
---

# FD-9693 — Five `07` §5.3 platform views have no owner and no code

## Finding

`07-platform.md` §5.3 declares six operator views besides the demo entrance (`07:390` to `:395`):
Jobs `/jobs`, Job detail `/jobs/:id`, Environments `/admin/environments`, Service accounts
`/admin/service-accounts`, Settings `/admin/settings` and System status `/admin/status`.
**Five of them, all but Environments, are owned by no Work, plan, ruling or closure, and none has
a route or a view in the frontend.** (Environments overlaps `03`'s Deployments view, which
`FD-9692` places in WK-675 on the maintainer's 2026-09-30 decision; whether `07`'s
`/admin/environments` route is a second screen or the same one is a question that decision did
not answer, and this finding does not answer it either.) **Proposed by the auditor; the
disposition is the lead's, and placement is the maintainer's.** FD-9693 is a working id, minted
at the records PR. Read at `origin/main` `880feb49`, 2026-09-30.

**Which of the five carry a numbered requirement** matters, because `00` FR-24 makes a §5.3
Contents cell prose that binds nothing. Only **FR-402** (`07:91`, "Job logs … viewable in the UI
with the `trace_id`") and FR-25 (every registered route reachable from the entry) bind a view;
FR-401's cancel action is the same shape (`07:90`). The other three views bind through FR-25 only
once a route is registered, and through their Contents cell not at all (FR-24). This is why the
options below can defer a view without breaching a requirement, and why FR-402's UI limb cannot be
deferred silently.

## Evidence

This is an ownership trace, not a grep proxy: for each view the owner was looked for in the roadmap
Work rows, every map plan the lead named, the closure records of the closed Works that could have
held it, and the code.

1. **The declared views and their routes** are `07:390` to `:395` (`git show
   880feb49:docs/specs/07-platform.md | sed -n 390,395p`). `00` §5.6's canonical route table lists
   `/jobs` and "Admin (users, roles, environments) `/admin/*`" for `07` (`00:412`, `:413`).
2. **No frontend route or view exists.** `grep -n -E 'path:' frontend/src/router/index.ts` prints
   the routes registered at `880feb49`: `/`, `/demo`, the `/data`, `/models`, `/objectives`,
   `/metrics`, `/peril-structures`, `/rating-versions/:id`, `/factors/:datasetVersionId`,
   `/reference`, `/callback` and `/silent-renew`. None is `/jobs`, `/admin/…`. `frontend/src/views`
   has no jobs, admin, service-account, settings or status view. `frontend/src/api/` has `jobs.ts`
   (a client used to poll a Job) and **no** service-accounts or settings client.
3. **Backend, per view (`07` §5.1 against `backend/src/app/api/`):**
   - **Jobs, Job detail:** every route the views need is declared (`07:301` to `:305`) and built
     (`api/jobs.py`: list, detail, logs, cancel, events). No backend gap.
   - **Settings:** `GET`/`PUT /api/v1/settings` (`07:311`), built (`api/settings.py:58`, `:72`).
     No backend gap.
   - **Service accounts:** `07:308` to `:310` declare create, rotate and revoke, all built
     (`api/service_accounts.py:140`, `:212`, `:275`). **No `GET` list route is declared or
     built**, yet the view's Contents cell is "keys with prefix, expiry, last used". The view
     cannot list what it manages without a spec change first.
   - **System status:** **no route is declared for it.** Its inputs are spread over `GET /readyz`,
     `GET /version` (`07:315`, `:316`) and Prometheus `/metrics` (`07:319`), and `07`'s own
     `/metrics` scope note says two of FR-443's five families are not emitted, one of them the
     cache hit rate ("there is no cache to report a hit rate for"), which the view's cell names.
4. **Roadmap Work rows.** The roadmap names none of the five. The P2 Requirement-coverage note
   (`docs/roadmap.md:1150`, under `## P2`, "Requirement coverage") assigns "~25 remaining `PLAT`" requirements to Phase 2 as an
   aggregate; WK-674's row enumerates its `07` requirements one by one (FR-428 to FR-431, FR-436,
   FR-437, FR-18, FR-412's memory half, FR-415, FR-434, FR-435 and the NFRs) and none is a view.
   The P3 rows that could hold service accounts or status carry no view either: WK-676's row is
   `06` FR-342 to FR-349, and WK-1251 (`draft`, packaging) is FR-432, FR-433, FR-438 and three NFRs.
5. **Map plans.** `PL-1237` (WK-674), `PL-1254` (WK-1250), `PL-1267` (WK-673), `PL-1268` (WK-690),
   `PL-1276` (WK-1170) and `PL-1277` (WK-1169) were read for the five routes and for `service
   account`, `system status`, `settings view` and `job detail`. Only `PL-1237` mentions a Service
   Account, and only as backend permissions and the F54 key-issuance fix (`PL-1237` lines 406,
   484 to 486, 526). `PL-9681` (WK-675's map plan, PR #920, on `origin/wk675-map-plan`, still
   `draft`) mentions none of the five; it names only the three `03` views of `FD-9692`.
6. **Closed Works.** `CR-00819` (WK-664's close) lists FR-399 to FR-405 as "The Job model with
   progress and cancellation … jobs API + worker paths" (`CR-00819:126`), which is the backend
   limb; no closure record claims a jobs, service-account, settings or status **view**. WK-658
   ("platform core", closed) is a backend Work; its row is `docs/roadmap.md:217`. WK-663 and WK-664
   closed with `01` §5.3's seven views and `02`'s views.
7. **The one place the gap was noticed, and it mis-cites.** `PL-00809` (WK-664's reachability
   slice) records "FR-24: the jobs view belongs to no Phase 1b slice. No slice builds one"
   (`PL-00809:37`), and the reachability test says "The jobs view is a later phase (FR-24). The
   exception lifts when that UI lands" (`frontend/src/router/__tests__/reachability.test.ts:32` to
   `:34`). FR-24 is the Contents-cell rule (`00:228`), which says nothing about a phase; **"a later
   phase" names no phase and no Work.** The exception it refers to is
   `/models/:slug/backtests/:backtestId`, whose only path from the entry is a Job result, so an
   unowned view holds a documented exception open indefinitely.
8. **The demo entrance reports these as unbuilt** (`CR-00718:62` describes the derived guide
   naming declared views not built). That makes the gap visible, not owned.
9. **`retrofit-impossible.md:28`** lists FR-402 inside "The Job model with progress and
   cancellation", a Phase 1a foundation. What landed is the log capture; the UI half of FR-402 did
   not. This is not a regression of the foundation (§9 of `CLAUDE.md` covers the backend), but it is
   a requirement whose second half has no owner.

## Options — for the maintainer's placement call

**The auditor prepares this; the auditor decides nothing.** Scope is the maintainer's
(`document-ids.md` §1.7). Scope freezes Sat 2026-10-03 (`docs/roadmap.md`, P2 freeze block).
Constraint to weigh: `RL-1263` option (c) serialises two build slices on any shared path outside its
registry list, and `frontend/src/router/index.ts` is one, so every option that puts a second frontend
Work beside WK-675 serialises on it (an inference: the registry list does not name it).

| Option | What it does | Cost / risk |
|---|---|---|
| **A. Fold all five into WK-675** | One frontend Work, one router owner | WK-675 is a `03` Work; with `FD-9692`'s three slices it is 12 slices, 9 / 12 / 24 days. Five more views on the `07` platform is a different subject and roughly doubles the increment, and it needs its own spec changes (the service-account list `GET`, a status route) |
| **B. New P2 Work, "Platform operator views"** | Owns all five in P2 | Must be opened before the Sat 2026-10-03 freeze; serialises against WK-675 on the router; adds a Work to G1 ("every P2 Work is resolved") |
| **C. New P3 Work, or fold into P3 rows** | Service accounts beside WK-676 (RBAC, FR-347); Settings and System status beside WK-1251 or a P3 platform Work; Jobs likewise | Nothing built ahead of the phase (`CLAUDE.md` §0); but leaves FR-402's UI limb and the reachability exception open through P2 |
| **D. Split by view** | **Jobs and Job detail into P2** (folded into WK-675, or a small new Work before the freeze); **Service accounts, Settings and System status into P3** | Two placements to record; the P2 part is small (backend built, no spec change) |
| **E. Defer all five with a dated line and name the phase** | The roadmap says which phase owns them, so "a later phase" gains a name | Cheapest; does not by itself close FR-402's UI limb |

**Per view.**

1. **Jobs and Job detail.** Backend complete. FR-402 and FR-401 bind them, and the reachability
   exception waits on them. Candidates: A, B, D (P2) or C/E (P3). Smallest of the five and the only
   two with a numbered requirement.
2. **Service accounts.** Needs a **spec change first** (a `GET` list route, `07:308` to `:310`),
   then a backend route, then the view. It sits with `06` FR-347/FR-389 and WK-676 in subject.
   Candidates: C (WK-676), D (P3).
3. **Settings.** Backend complete (`GET`/`PUT /settings`, FR-446 makes the effective value and
   source "inspectable by an Admin"). Candidates: C, D (P3), or B.
4. **System status.** Needs a **spec change first** (no route; two of its inputs, cache hit rate and
   part of the metrics families, are not emitted). Candidates: C (WK-1251's observability limb or a
   P3 platform Work), E.
5. **Environments (`07:392`).** Not in this finding; decided with `FD-9692` only for
   `/rating/environments`. **A question for the maintainer, not answered here:** does
   `/admin/environments` remain a second route?

**Recommendation (the auditor's, not a decision): option D.**
- **Jobs and Job detail in P2, folded into WK-675 as two slices** (or a small new Work before the
  freeze if the maintainer prefers a separate router owner). Rationale: backend is done and declared,
  no spec change is needed, FR-402 and FR-401 bind them, the reachability exception lifts when they
  land, and the exit demo's regression run is a 30 to 60 minute compute step (`WF-699` §6 Timing,
  "D — Regression + dislocation") a browser user needs progress on. Two slices at the plan's
  0.75 / 1 / 2 day band add 1.5 / 2 / 4 days, so WK-675 becomes 14 slices, 10.5 / 14 / 28 days
  (12 slices + 2; the plan's arithmetic, not a re-estimate).
- **Service accounts, Settings and System status in P3**, placed by a dated roadmap line naming
  WK-676 for service accounts and a P3 platform Work (or WK-1251) for the other two. Rationale: two
  of the three need a spec change first, none has a numbered UI requirement, and Phase 3 is
  the governance and administration phase. **Nothing is built ahead of the phase** (`CLAUDE.md` §0);
  this is a roadmap and spec change only.
- **Not recommended:** A for all five, because it mixes the `07` platform views into the rating
  frontend's budget; B for all five, because of the freeze and the router serialisation.
- **What would change the recommendation:** if the maintainer wants the operator views in the P2
  exit demo, then B or a larger A; if FR-402's UI limb may lapse, then E.

## Disposition

Proposed by the auditor; the verdict is the lead's. **The lead routes it**: placement is scope, the
maintainer's (`document-ids.md` §1.7, an `RL-` or `RFC-`). Declaring a Contents cell declared-prose
is a spec question (`00` FR-24), the decision-maker's. This finding decides none of these. The two
spec gaps (service-account list `GET`; a System-status route) are spec changes that follow
placement, not before.

**Event that next confirms or discharges it:** each of `/jobs`, `/jobs/:id`, `/admin/service-accounts`,
`/admin/settings` and `/admin/status` has a named owner in the roadmap or a ruling.

Ownership shape: event
