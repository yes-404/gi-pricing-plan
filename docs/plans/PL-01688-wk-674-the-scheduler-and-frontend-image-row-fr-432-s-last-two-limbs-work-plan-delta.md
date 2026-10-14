---
id: PL-1688
family: plan
kind: map
title: WK-674 — the scheduler (beat) and frontend-image row, FR-432's last two limbs and FD-1661's discharge, cut as SL-1689 — Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1620, PL-1666, SL-1258, SL-1689, FD-1661]
---

# PL-1688 — WK-674: the scheduler and frontend-image row (SL-1689): Work-plan delta

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5. It does not replace
> [`PL-1237`](PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md) (the map
> plan) or the deltas [`PL-1537`](PL-01537-wk-674-slices-4-to-6-work-plan-delta.md),
> [`PL-1620`](PL-01620-wk-674-slices-4-and-5-after-sl-1455-returned-to-p2-work-plan-delta.md) and
> [`PL-1666`](PL-01666-wk-674-slice-4-fd-9704-round-trip-fr-452-management-limb-and-activation-work-plan-delta.md).
> It `relates:` them and adds **one row**, cut here as SL-1689: the `scheduler`
> (Celery beat) service and the `frontend` image, FR-432's last two limbs. No other slice is
> changed, apart from DP-B1, ruled (a): a GO condition on Slice 4's authored worker. The row is
> one PR under L1 (a'), and its `LG-` quotes this file as its scope. REQUIRED SUB-SKILL for the
> executor: subagent-driven-development (recommended) or executing-plans. The executor also binds
> `python-test`, `test-driven-development`, `dev-commands` (the two-half gate and the slot
> wrapper), `vue-frontend` (the generated-client seam), `repo-architecture` (a new image is a
> component) and `git-hygiene`. It reads [`README.md`](README.md)'s five unchecked conventions
> and is spawned from `.claude/roles/executor.md`.

Minted 2026-10-12 as PL-1688 and SL-1689 from working ids 9882 and 9883, reserved by the lead (team-lead to
planner-wk674-s4, 2026-10-12, the task "cut the beat + frontend-image row"). Written 2026-10-12
by the planner (planner-wk674-s4). Evidence was read at `origin/main` `604ea084` (#1291) and at the
authored Slice 4 branch `origin/sl-1258-wk674-s4` `a04ff676`. Slice 4 is not merged. Every line
quoted from that branch is a premise that must be re-read at this row's base (convention 4).

## Authority

Each entry is the maintainer's (by delegation), in `to-lead.md`.

- **The row exists:** "2026-10-12 02:53:52 BST — Readiness rulings: GO S6 SL-1548 (swap
  planner-wk673-c out); FD 9862 LOW, owner WK-677; PL 9864 + PL 9865 deltas OK; FD 9860 (ii)",
  item 4: "FD 9860: (ii) ACCEPTED, beat as its own row after S4, serialised on
  deploy/docker-compose.yml. FR-432 is not met until both land, and the FD stays open until beat
  merges." (FD 9860 was minted as FD-1661, and PL 9865 as PL-1666.)
- **Three limbs:** "2026-10-12 03:08:30 BST — (1) noted, close after the SIGINT report; (2) the
  frontend image is FR-432's THIRD limb, so FD 9860 lists all three and FR-432 stays open until
  all land; (3) integers stay accepted; (4) HIGH, separate CLI: agreed", item 2: "worker
  (SL-1258, WK-674 S4); beat (its own row after S4); the `frontend` image (a third row). FR-432
  and FD 9860 stay open until ALL listed limbs merge."
- **The image folds into this row, in P2:** "2026-10-12 03:09:50 BST — DP-S4-3: (b) fold the
  frontend image into the beat row; P2 scope, with the cut-ladder move line pre-named": "(b): one
  compose edit, and FR-432 and FD 9860 close together." Its three conditions, verbatim:
  - "The row's plan says that if the cut ladder takes the lane, the row moves to P3 by a dated
    line with an owner (WK-674) and a discharge event. It is never dropped."
  - "A new frontend Dockerfile brings a base image (node build stage plus a static server, e.g.
    nginx). If that is a new tech dependency for the stack, docs/skills-map.md is updated in the
    SAME PR (CLAUDE.md §10), and 07's tech-dependencies section if it names images."
  - "Test it from a fresh checkout: the image builds and serves the built app (a curl 200 on /),
    recorded in the LG. That is the \"declared ≠ reachable\" lesson."
- **The task:** the entry "2026-10-12 05:32:12 BST — GOs for SL-1543 and SL-1622 noted (your
  activation-need GOs, readiness read with the rulings template); 2 seats free under the cap, so
  fill them with no-gate work", candidate (a): "the WK-674 beat + frontend-image row plan
  (DP-S4-3 (b))".
- **Lean P2 L5** (`docs/plans/README.md:16-19`): a change of slice scope is one dated Work-plan
  delta that `relates:` the Work's plan, and the planner cuts its `SL-` row
  (`document-ids.md` §1.6).

## Goal

After this row merges, `docker compose -f deploy/docker-compose.yml --profile app config --services`
prints every FR-432 service: `api`, `worker`, `scheduler` and `frontend`, plus the dependencies.
The stack is reachable and not only declared: a Job submitted through it completes, and the built
SPA is served at `/`. FR-432's last two limbs then close, and so does FD-1661, whose discharge event
is "a merged change after which `docker compose -f deploy/docker-compose.yml config --services`
prints the FR-432 services" (FD-1661, *Disposition*, at `604ea084`).

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` exit 0 at the
   branch head, except check 31's lines naming the working ids 9882 and 9883, which cleared at their
   mint (PL-1688 and SL-1689).
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.
3. **The services are declared.** On the row's merge tree,
   `docker compose -f deploy/docker-compose.yml --profile app config --services | sort` prints
   `api`, `frontend`, `lb`, `migrate`, `scheduler` and `worker` beside the dependencies.
   `uv run pytest -q backend/tests/test_deploy_stack.py -k 'scheduler or frontend'` exits 0 and
   collects at least 4 tests. The `LG-` quotes each red line (Task 1).
4. **The scheduler is reachable.** In the build window, the runtime test of Task 3 exits 0 under
   `GIP_DEPLOY_TESTS=1`. A Job submitted through `lb` reaches a terminal state. The same test,
   run with `scheduler` stopped, is seen red because the Job stays `queued`, and the `LG-` quotes
   that red line.
5. **The frontend is reachable from a fresh checkout** (condition 3 of 03:09:50). The `LG-`
   records: the clean checkout's commit (`git worktree add <dir> <head>` or a clone, never the
   working tree); the image build command and its rc; and three `curl -s -o /dev/null -w '%{http_code}'`
   lines with their output: `/` → `200`; one deep SPA route (history fallback) → `200`; and
   one `/api/v1/…` route → the API's own status (for example `401` with an RFC 9457 body), never
   nginx's `502`.
6. **The tech dependency is recorded in the same PR** (condition 2 of 03:09:50): Task 4's checks
   print the lines it names.
7. **The gate is green on the row's merge tree**, both halves of the `CLAUDE.md` §11 commands,
   named against `origin/main...<row branch>`. The frontend half covers the image's build command
   (`pnpm --dir frontend build`) on the same tree.

## Global Constraints

`PL-1237`'s, `PL-1537`'s, `PL-1620`'s and `PL-1666`'s Global Constraints apply where they name
the deployment path.

- **B0.1 — this row starts after `SL-1258` merges**, and its base contains that merge. It
  edits `deploy/docker-compose.yml`, the `app` profile and S4's shape-test file
  (`backend/tests/test_deploy_stack.py`), all of them S4's. It is serialised on
  `deploy/docker-compose.yml` (02:53:52 item 4): never in flight beside another edit of that file.
  Before its first commit, the executor runs `git diff --name-only origin/main...origin/<branch>`
  for each branch in flight and names in its `LG-` each one that touches `deploy/`.
- **B0.2 — it is off the exit path.** Neither limb is on `WF-701` A to D (`PL-1620` D0.1). It
  takes a free lane after S4, it does not pre-empt S5, and it is never in a timing window.
- **B0.3 — the cut-ladder move is pre-named** (condition 1 of 03:09:50). If the cut ladder takes
  this row's lane, the lead writes, on the SL-1689 row in `docs/roadmap.md`, a dated line in this
  form: *"Moved to P3 on <date>, by <the ruling that applied the ladder>: owner WK-674; discharge
  event: this row's merge, after which `docker compose -f deploy/docker-compose.yml --profile app
  config --services` prints `scheduler` and `frontend` and Acceptance items 4 and 5 hold. FR-432
  and FD-1661 stay open until then; the P2 closure record lists FD-1661 with this carriage
  (`CLAUDE.md` §14)."* The row is never dropped, and never cut without that line.
- **B0.4 — the deploy runtime tests run only in a build window** (`PL-1666` D0.5). They skip
  unless `GIP_DEPLOY_TESTS=1`. The lead books the window, and the `LG-` records its start and end.
- **B0.5 — no hand-written API type** (`CLAUDE.md` §3). The image runs `pnpm --dir frontend
  generate:api` from `docs/contracts/openapi/generated.json` before `build`, as the frontend
  workflow does. Nothing generated is copied in from a developer's tree.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | SL-1689 — the scheduler and frontend-image row | This file, Tasks 1 to 4 | `07` §3.2: FR-432 (the `scheduler` and `frontend` limbs), FR-413 (the beat process that runs the tick), FR-406 (the outbox relay that the beat schedule runs today); register FD-1661 (discharged at merge) | `SL-1258` merged with its worker on `default,compute` (B0.1; DP-B1 ruled (a), an S4 GO condition) | 1 + a build window |

FR-432's `worker` limb is `SL-1258`'s, not this row's.

**Task 0 — re-read at the base (convention 4).** At the row's base, the executor quotes in its
`LG-`:
- `deploy/docker-compose.yml`'s `worker` command;
- `.dockerignore`;
- `backend/src/app/worker/entrypoint.py`'s `beat_schedule`;
- `deploy/keycloak-local/realm-gi-pricing.json`'s `redirectUris` and `webOrigins`.
Each premise below that rests on them is re-checked. Where one differs, the executor stops and
reports to the lead.

**Task 1 — the `scheduler` service, red first.**
- Shape tests in `backend/tests/test_deploy_stack.py`, mirroring its `_load` helper and its
  breaker table (`_break_*` plus `test_each_check_goes_red_on_the_break_it_exists_for`, `:136-164`
  at `a04ff676`), never a new fixture scheme. Each is marked `req("FR-432")`, and the beat
  check is also marked `req("FR-413")`.
- The checks, each seen red **by its cause** before the compose edit (convention 2). A red that
  names a different cause is a test defect:
  - `scheduler` exists under the `app` profile (red: no service named `scheduler`);
  - it runs `celery -A app.worker.entrypoint beat` from the one image that `api` and `worker` use
    (red: the command, or the image, differs);
  - it runs as **one** process: no `deploy.replicas` above 1, and the test states why (two beats
    relay twice, and FR-413's tick is "a single periodic Celery beat task").
- **The compose edit:** a `scheduler` service under `profiles: ["app"]`, `image:
  gi-pricing-app:${GIP_BUILD:-unset}`, `command: ["celery", "-A", "app.worker.entrypoint",
  "beat", "--schedule", <a path inside the container that it can write>]`. The `--schedule` file
  is kept off the image, as `scripts/demo.py:227-240` keeps it under a gitignored directory. It
  depends on `migrate` completed and `redis` healthy, with `stop_grace_period` as `worker` has.

**Task 2 — the `frontend` image and service, red first.**
- **The image.** A two-stage Dockerfile at `deploy/frontend.Dockerfile`, beside S4's
  `deploy/Dockerfile`:
  - a Node build stage, `node:22-alpine`, matching `frontend/package.json` `"engines": {"node": ">=22"}`
    and `.github/workflows/frontend.yml:66` `node-version: 22`. It enables pnpm at
    `frontend/package.json` `"packageManager": "pnpm@11.21.0"`, then runs
    `pnpm --dir frontend install --frozen-lockfile`, `generate:api` and `build` (B0.5);
  - a static stage on the **same nginx image S4's `lb` uses** (`nginx:1.27-alpine`,
    `deploy/docker-compose.yml` `lb` at `a04ff676`), so the stack gains no second server image.
- **The build context.** The context is the repository root, because the build needs `frontend/`
  and `docs/contracts/openapi/generated.json`. S4's root `.dockerignore` excludes both `frontend`
  and `docs` (`a04ff676`). The row must not widen the backend image's context to get them. It
  uses a Dockerfile-specific ignore file (`deploy/frontend.Dockerfile.dockerignore`, which
  BuildKit reads in place of the root one) that admits only `frontend/` (without
  `node_modules`) and `docs/contracts/openapi/generated.json`. The executor confirms at Task 0
  that the stack's `docker compose build` uses BuildKit. If it does not, the executor stops and
  reports.
- **The nginx config** (`deploy/frontend.nginx.conf`):
  - serves the built `dist/` at `/`, with a history fallback to `index.html` for the SPA's
    routes;
  - proxies `/api/` to `lb:8000`, so the browser stays same-origin. `frontend/vite.config.ts:36-41`
    states that design for the dev server: "the deployed build, served behind one host, behaves
    the same way as the dev server".
- **The service.** `frontend` under `profiles: ["app"]`, built from `deploy/frontend.Dockerfile`
  and published on `${GIP_WEB_PORT:-5173}` (DP-B2 ruled (a)), depending on `lb`.
- **Shape tests, red first by cause, marked `req("FR-432")`:**
  - `frontend` exists under `app` (red: no service);
  - it is built from `deploy/frontend.Dockerfile` (red: no build, or a different file);
  - its nginx config proxies `/api/` to `lb` (red: no proxy block, read from the conf file);
  - the backend image's `.dockerignore` still excludes `frontend` (a guard; green at base and
    head, and recorded as a guard).
  Each check joins the breaker table.

**Task 3 — reachable, in the build window (B0.4).** One runtime test behind `GIP_DEPLOY_TESTS=1`
in S4's `backend/tests/test_deploy_stack_runtime.py`, mirroring its image-build helper. It:
- brings up `--profile app`;
- submits one Job through `lb`, the cheapest Job kind with a terminal state, which the executor
  names at Task 0 from `app/platform/jobs.py`'s queue mapping;
- asserts that the Job reaches a terminal state within a stated bound.
It is seen red with `scheduler` stopped: the Job stays `queued`, which is the relay's absence
(`scripts/demo.py:228`: "without `beat`, committed Jobs stay `queued` and nothing says why").
It also proves DP-B1's S4 condition end to end: with a worker that does not consume `default`, the
relay task goes unconsumed, and this test is red. The fresh-checkout frontend proof of Acceptance item 5 runs in the same window, and
the `LG-` records it.

**Task 4 — the tech dependency, same PR** (condition 2 of 03:09:50).
- **The state at `604ea084`:** `git grep -n -i 'nginx' -- docs/skills-map.md docs/specs/07-platform.md`
  prints nothing. `07` §8 (`07:463`) has a "Docker Compose / Helm" row and no image row.
  `docs/skills-map.md:142` has the same component.
- **Classification:**
  - **Node** is not new to the stack. It is the frontend toolchain (`CLAUDE.md` §3, "pnpm";
    `frontend.yml:66`). This row adds it as a build-stage image only, and that is recorded in the
    "Docker Compose / Helm" rows' notes.
  - **nginx is new to the stack's dependency list.** S4 introduces it first, as `lb`, at
    `a04ff676`, and S4's diff touches neither file (`git diff --name-only origin/main...a04ff676`
    names no `docs/` path except its ledger).
- **The rule for this row, read at its base:**
  - if `git grep -n -i nginx -- docs/skills-map.md` prints a row (S4 or another PR added it), this
    row adds only the static-server use to that row's "Used for" cell;
  - if it prints nothing, this row adds the nginx row to `docs/skills-map.md` **and** to `07` §8,
    with both uses (the `lb` and the static server), in this PR.
- Either way, the change runs `python3 scripts/audit-docs.py` before commit (`CLAUDE.md` §0). The
  `07` §8 edit follows `.claude/skills/spec-change`, and no requirement id changes.

### Write set

`deploy/docker-compose.yml` (`scheduler`, `frontend`); `deploy/frontend.Dockerfile`;
`deploy/frontend.Dockerfile.dockerignore`; `deploy/frontend.nginx.conf`; `deploy/README.md` (the
`app` profile section gains the two services); `backend/tests/test_deploy_stack.py`;
`backend/tests/test_deploy_stack_runtime.py`; `docs/skills-map.md` and `docs/specs/07-platform.md`
§8 (Task 4); the row's `LG-`. The realm file is not in it (DP-B2 ruled (a)). **Not in it:** `frontend/src/` (nothing in the SPA changes), `backend/src/`, the `worker` service (DP-B1 ruled
(a): S4's), and `docs/findings/register.md` (FD-1661's closing line is the register minter's at the
mint batch).

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-B1 | Slice 4's authored `worker` consumes `--queues compute` only (`deploy/docker-compose.yml:145` at `a04ff676`). The beat schedule sends the outbox relay to queue `default` (`backend/src/app/worker/entrypoint.py:53-58` at `604ea084`: `"options": {"queue": "default", …}`). `default` is also the Celery default queue (`backend/src/app/worker/celery_app.py:52`) and carries the compile Jobs (`scripts/demo.py:210-224`: "`default` carries the compile, `compute` the regression, rate-table diff and dislocation Jobs"). The demo's worker consumes `default,compute`. With S4's worker as authored, no Job leaves the outbox even after this row adds beat. Who fixes the worker's queues? | (a) S4 fixes it at GO: its `worker` service is S4's write set (FR-415), and a shape test there asserts both queues, seen red by cause. (b) This row fixes it, editing the `worker` command and its S4 test. (c) A second worker service for `default`. | **(a).** The `worker` service is FR-415's and S4's, and S4's own runtime path should not merge with a worker that cannot run the relay or a compile. (b) puts a fix to S4's service in a row that is off the exit path and may be cut (B0.3), so S4 would ship the defect into S5's measurements and maybe into P3. (c) adds a service no requirement asks for. If (a) is ruled, this row's Task 3 is the end-to-end proof that the fix holds. | scope / spec-vs-code | no longer: ruled | **ruled (a)** by the lead's entry "2026-10-12 05:37:23 BST — PL 9882 + SL-1689 PUSHED @3dc58611f25330bdd779257b5222a025cfb9dbd7 (pl-9882-wk674-beat-frontend-2026-10-12; check 31 only; doc-index 0; register-lint 0)" (`from-lead-2026-10-09.md`): "S4 MUST consume default,compute (as demo.py:210-224 does), with a shape test asserting both queues — an S4 GO CONDITION (FR-415 is S4's); not this row's." |
| DP-B2 | Which host port does `frontend` publish, given that the local realm admits only `http://localhost:5173` and `http://127.0.0.1:5173` (`deploy/keycloak-local/realm-gi-pricing.json:16-17` at `604ea084`), which is also the Vite dev server's port? | (a) publish on `${GIP_WEB_PORT:-5173}`, so the realm admits the compose frontend unchanged, and the dev server and the compose frontend cannot both use the default port at once. (b) publish on a new default port, and add that origin to the realm's `redirectUris`, `webOrigins` and `post.logout.redirect.uris` in this PR. | **(a).** A browser login from the compose frontend works with no realm change. The port clash is a choice between two ways of running the same SPA, and the variable resolves it. (b) widens the realm, a security-relevant file, for no capability the stack lacks. | scope | no longer: ruled | **ruled (a)** by the same entry: "the frontend publishes on ${GIP_WEB_PORT:-5173}; no realm change (realm-gi-pricing.json:16-17 admits :5173 only)." |

A plan is "`draft` while decision points are open, `active` on freeze" (`document-ids.md` §1.6,
the PL `map`/`leaf` row). Both decision points are ruled (05:37:23), and no decision point is open.
So this plan goes `active` at its mint by a status line. The branch keeps `status: draft` until
then. DP-B1's ruling is an `SL-1258` GO condition. It is carried in `SL-1258`'s activation paper
and in `PL-1666`'s successor delta, which is written when RL-1687 lands (the lead, 05:37).

## The row, cut

SL-1689 is cut in `docs/roadmap.md` under WK-674, after `SL-1260`, as `draft` (`document-ids.md`
§1.6 SL row: "planner, cut in the map plan (`draft`)").

## Hand-off (not this plan's writes)

- **The lead:**
  - list this delta on WK-674's roadmap row (L5);
  - DP-B1 and DP-B2 are ruled (05:37:23). DP-B1 (a) is carried into `SL-1258`'s GO conditions
    and `PL-1666`'s successor delta.
- **The register minter:** FD-1661's dated line naming SL-1689 as the row that discharges its last
  two limbs, at this delta's mint.
- **RL-1687 (DP-S4-1):** not this row's subject. It is folded into `PL-1666`'s successor record
  when it lands, on the lead's word.

## Self-review

- **Spec coverage.** FR-432 (the `scheduler` and `frontend` limbs), FR-413 and FR-406, each named.
  FR-432's `worker` limb stays `SL-1258`'s. FD-1661 is a register row. No requirement id is added
  or changed.
- **The three conditions of 03:09:50 at every site** (convention 5):
  - the cut-ladder move: B0.3 (Global Constraints) and Hand-off;
  - the tech dependency: Task 4, the Write set and Acceptance item 6;
  - the fresh checkout and curl: Task 3 and Acceptance item 5.
- **Literals verified** (conventions 1 and 3), at `604ea084` unless marked `a04ff676`:
  - `entrypoint.py:53-58` (`beat_schedule`, queue `default`); `celery_app.py:52`;
    `scripts/demo.py:210-240`;
  - `frontend/package.json` `engines` and `packageManager`; `frontend.yml:66`;
    `vite.config.ts:36-41`;
  - the realm's `:16-17`; `07:463` (§8); `skills-map.md:142`;
  - S4's `worker` command, `lb` image, `.dockerignore` and test helpers (`a04ff676`).
  The example port variable `GIP_WEB_PORT` is an example name, and the `--schedule` path is the
  executor's.
- **Convention 4.** `to-lead.md` was read for the 02:53:52, 03:08:30, 03:09:50 and 05:32:12
  entries. Slice 4's branch is a moving premise until it merges, which is why Task 0 re-reads it.
- **Placeholders.** `<row branch>`, `<head>`, `<dir>` and `<date>` are values read when the row
  runs.
