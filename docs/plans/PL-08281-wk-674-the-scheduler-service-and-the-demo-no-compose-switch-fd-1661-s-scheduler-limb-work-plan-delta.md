---
id: PL-8281
family: plan
kind: map
title: WK-674 — the scheduler service in deploy/docker-compose.yml (FD-1661's scheduler limb) and the demo's --no-compose switch, one red-first slice — Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-29            # drafted 2026-10-29 under working id 8281
owner: planner
tree: 447bcfd6ea73739c1f327682c6ee9b0caa61470a
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1688, PL-1690, PL-1714, SL-1689, SL-1711, FD-1661, FR-432, FR-406, FR-413, FR-408]
---

# PL-8281 — WK-674: the scheduler service and the demo's --no-compose switch, Work-plan delta

*Disclosure: drafted 2026-10-29 by the planner (seat plan-beat, lead 29) under working id 8281
(this plan). The maintainer rules a new `PL-` id at the mint (to-lead "2026-10-29 10:27:26 GMT":
"a new PL id raised with me first if none fits"). The slice's working ids are SL 8275 and LG 8276,
reserved in the same entry. They are written in space form in prose, and they are not in
`relates:`, because a front-matter id must resolve. The minter adds the minted `SL-` and `LG-` at
the mint.*

> **For agentic workers:** this is a **one-row WK-674 Work-plan delta** under Lean P2 L5. It does
> not replace [`PL-1237`](PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md)
> (the map plan) or any earlier delta. No WK-674 delta is open for rows: every one is frozen
> (`active`), retired or superseded (`grep -l '^work: WK-674' docs/plans/*.md`, then each file's
> `status:`, at `447bcfd6`: 16 active, 1 retired, 2 superseded). So a new slice is a new delta.
> The slice is one PR under L1 (a'), and its `LG-` quotes the row below as its scope. No leaf
> plan. REQUIRED SUB-SKILL for the executor: executing-plans (the slice is small). The executor
> also binds `test-driven-development` (each red is seen first, by its cause), `python-test`
> (`@pytest.mark.req` markers), `dev-commands` (the two-half gate; `uv sync --all-packages` in a
> fresh worktree; the demo entrance) and `git-hygiene`. It reads [`README.md`](README.md)'s five
> unchecked conventions and is spawned from `.claude/roles/executor.md`.

## Authority

Each entry is the maintainer's (by delegation) unless marked as the lead's.

- **The slice exists, before the code freeze:** to-lead "2026-10-29 10:26:13 GMT", **Ruled**:
  "FD-1661's scheduler limb is **not** acceptable at the P2 close: the exit demo's scripted WF-701
  deploy (roadmap §12 row 2, SL-1711) runs on `deploy/docker-compose.yml`, and without a beat
  service the outbox relay (entrypoint beat, FR-406/FR-413) never runs — A3-class steps time out
  in the demo itself. **The scheduler service lands in `deploy/docker-compose.yml` under WK-674
  before the code freeze: a slice, red-first (compose up with the service; A3's outbox counts
  move; the demo's A3 passes), a PL delta row with its SL reserved, merged by Tue 3 Nov.**"
- **The ids and the schedule:** to-lead "2026-10-29 10:27:26 GMT": "SL 8275 / LG 8276 reserved
  (→ [the two minted ids that follow S1c's; elided here because they do not resolve at this base, and lead 29's task list projects other numbers, see Hand-off] after S1c's ids; next working id 8277); plan + reds Fri 30 pm after S1c's
  PR; code, greens, gate Mon 2 Nov never beside the nfr-bench-1 session; merged by Tue 3 Nov; the
  PL delta row in WK-674's current plan delta (a new PL id raised with me first if none fits)".
- **The writable schedule path is a requirement:** the lead's from-lead "2026-10-29 11:30:06 GMT"
  item (1): "the shipped `scheduler` service sets a writable schedule path (the red: compose up
  without it → the service exits 1 with this message; the green: it stays Up and the outbox
  drains)". The maintainer accepted it as this slice's red in to-lead "2026-10-29 12:00:32 GMT"
  item (2).
- **The second red, the demo's compose coupling:** to-lead "2026-10-29 12:00:32 GMT" item (3):
  "`scripts/demo.py:482`'s `docker compose up` coupling restarts the shared postgres/keycloak at
  every gate's demo stage; **the `--no-compose` / env switch rides SL 8275 (the beat slice) as a
  second red** — a demo run with the switch recreates nothing: the four container ids
  before/after equal, quoted in its LG — not a backlog row any longer. Until it lands: gates run
  SOLO only". The lead adopted it at from-lead "2026-10-29 12:01:06 GMT".
- **The seating:** to-lead "2026-10-29 17:11:12 GMT" item (2): "FD-1661 beat slice … — plan + the
  two reds (beat writable schedule path; demo.py --no-compose switch with container ids equal
  before/after)".
- **Lean P2 L5** (`.claude/roles/planner.md`, "Lean P2 (L5, L1)"): a change of slice scope is one
  dated Work-plan delta that `relates:` the Work's plan, and the planner cuts the slice's row.

## Evidence (read at `447bcfd6`, tree `0986a7af`, unless marked)

- `deploy/docker-compose.yml` (200 lines) has `name: gi-pricing` (`:7`), the `x-gip-env` and
  `x-gip-build` anchors (`:12`, `:26`) and the `&gip-worker` anchor on `worker-compute` (`:161`),
  which `worker-scoring`, `worker-io` and `worker-default` merge (`:174`, `:179`, `:184`). It has
  **no** `scheduler` service and no `beat` command: `git grep -n -i -e beat -e scheduler 447bcfd6
  -- deploy/docker-compose.yml` prints nothing (FD-1661's 2026-10-29 annotation reads the same).
- The beat schedule is `backend/src/app/worker/entrypoint.py:60-66`: `relay-outbox` every 1 s on
  `RELAY_QUEUE`. Without a beat process, no Job leaves the outbox.
- The deploy runtime tests run beat as a test fixture, not as a service:
  `backend/tests/deploy_stack_helpers.py:270` `beat_fixture` runs `compose run --rm -d
  worker-default celery -A app.worker.entrypoint beat --schedule /tmp/celerybeat-schedule`. Its
  docstring says the service is SL-1689's. `backend/tests/test_deploy_stack_runtime.py:311` and
  `:457` take that fixture.
- The shape tests select workers by `"celery" in words and "worker" in words`
  (`backend/tests/test_deploy_stack.py:77-83`). A `beat` command is one word
  `app.worker.entrypoint` plus `beat`, so it is not counted as a worker. The executor re-checks
  this at Task 0.
- `scripts/demo.py:478-486`: the local demo always runs `docker compose -f
  deploy/docker-compose.yml --profile auth up -d --wait`. Because the file names its project
  (`name: gi-pricing`), this call acts on the shared stack from any worktree. On 2026-10-29,
  `gi-pricing-postgres-1` and `gi-pricing-keycloak-1` show `StartedAt 11:52:44Z`, two seconds
  after the FD-1585 gate's demo started (the lead's from-lead "2026-10-29 12:00:03 GMT" item (3)).
- The working override: S1c's ledger (LG 1964, not on this base; it reaches main with S1c's merge), section "S1c-5 (2026-10-29): the compose run with a scheduler
  service", on `origin/draft/s1c-fd1951` (read at `fa1a5ad9`). Its `scheduler` keys are
  `worker-default`'s environment, build, image and `depends_on` plus `command: ["celery", "-A",
  "app.worker.entrypoint", "beat", "--schedule", "/tmp/celerybeat-schedule"]`. Setup fault 2: the
  first start exited 1 with `[Errno 13] Permission denied: 'celerybeat-schedule'`. With the flag,
  `s1c5-scheduler-1` stayed Up and the outbox read `published | 37` with no `pending` row after
  the journey; A3 had no `JOB_TIMEOUT`. Fault 1: `docker compose build` needs buildx 0.17.0 and
  the host has 0.13.1, so the image is built with `docker build -f deploy/Dockerfile --build-arg
  GIP_BUILD=<head> -t gi-pricing-app:<head> .` and then `up --no-build`.
- FR-432 (`07` §3.2) names `scheduler` ("the beat tick, FR-413") among the shipped images. FR-408
  asks for "one documented command" to the demo; an optional flag leaves that command unchanged.
  **No spec text changes in this slice.**

## Goal

After this slice merges, two things are true on `deploy/docker-compose.yml` and
`scripts/demo.py`:

1. `docker compose -f deploy/docker-compose.yml --profile app config --services` prints
   `scheduler`. On a throwaway compose project, the `scheduler` container stays Up, and a Job
   submitted through the stack leaves the outbox and reaches `succeeded`. FD-1661's scheduler
   limb is then closed. Its `frontend` limb is not this slice's (DP-1).
2. `uv run python scripts/demo.py --no-compose …` runs the demo against a stack that is
   already up, and it creates, recreates or restarts no container. The four shared containers
   keep the same `Id` and `StartedAt` before and after. Gates can then pair again, by the lead's
   rule; this plan does not lift SOLO.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | SL-1689 (`draft`, cut by `PL-1688`) already owns FR-432's `scheduler` **and** `frontend` limbs. This slice takes the `scheduler` limb before the freeze. What does SL-1689 keep? | (a) SL 8275 takes the `scheduler` limb. SL-1689 keeps the `frontend` limb only, by one dated line on its `docs/roadmap.md` row written at SL 8275's mint ("the scheduler limb moved to SL 8275 (→ its minted id) by the ruling of 10:26:13; this row keeps the frontend limb"). `PL-1688` stays unedited (frozen). (b) Retire SL-1689 and cut a new frontend-only row in a later delta. (c) Fold the frontend limb into this slice. | **(a).** One dated line keeps the frontend limb's owner and its pre-named cut-ladder line (`PL-1688` B0.3) as they are. (b) creates a row only to replace one. (c) adds a new image, a Dockerfile and a tech-dependency update (`PL-1688` Tasks 2 and 4) to a slice that must merge by Tue 3 Nov, against the ruling's scope ("the scheduler service"). | scope | yes | |
| DP-2 | The form of the switch: a flag, an environment variable, or both? | (a) a `--no-compose` flag only. (b) an env variable (for example `GIP_DEMO_NO_COMPOSE=1`) only. (c) both. | **(a).** The gate scripts already call `demo.py` with flags (`--journey`, `--rows`). A flag shows in the gate log's command line, and an env variable does not. One form is one thing to test. | design unknown | no — Task 2 applies (a) unless the lead rules otherwise before the slice's GO | |
| DP-3 | Does `--no-compose` also check that the stack is up, and refuse if not? | (a) yes: before the migrations step, it reads `docker compose ps` for `postgres`, `redis`, `minio` and `keycloak` and refuses, naming each service that is down, as `check_compose_up` (`scripts/demo.py:317`) already does for `--target compose`. (b) no check: the first connection fails. | **(a).** A missing service then fails before anything starts, with the service's name, not as a connection error in the middle of the seed. It reuses the existing check, so no new mechanism is added. | design unknown | no — Task 2 applies (a) unless the lead rules otherwise before the GO | |

A plan is `draft` while a blocking decision point is open (`document-ids.md` §1.6, the PL row).
DP-1 is blocking, so this plan stays `draft` until it is ruled. It goes `active` by a status line
at its mint.

## Global Constraints

`PL-1237`'s and `PL-1688`'s Global Constraints apply where they name the deployment path. In
particular:

- **C1 — serialised on `deploy/docker-compose.yml`** (`PL-1688` B0.1). Before its first commit,
  the executor runs `git diff --name-only origin/main...origin/<branch>` for each branch in
  flight and names in its `LG-` each one that touches `deploy/` or `scripts/demo.py`.
- **C2 — no `docker` command on the shared `gi-pricing` project** except as the lead grants it.
  Every runtime proof of Task 1 runs on a throwaway project (`-p <name>`, fresh volumes, no host
  port of the shared stack), as S1c-5 did. The shared stack comes up only from tools-main.
- **C3 — the deploy runtime tests run only in a build window** (`PL-1666` D0.5, `PL-1688` B0.4):
  they skip unless `GIP_DEPLOY_TESTS=1`. The lead books the window; the `LG-` records its start
  and end.
- **C4 — images are built with `docker build`, never `docker compose build`** on this host
  (buildx 0.13.1 < 0.17.0), then `up --no-build`. This is an environment fact, not a change to
  the compose file.
- **C5 — not beside the nfr-bench-1 session** (Mon 2 – Tue 3 Nov 2026; to-lead "2026-10-29
  10:27:26 GMT"). No build window, compose run or gate of this slice overlaps it.
- **C6 — no spec edit, no new requirement id.** FR-432, FR-406 and FR-413 already say what the
  service must do. A spec change found necessary stops the slice and goes to the lead.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | SL 8275 (ledger LG 8276) — the scheduler service in `deploy/docker-compose.yml` (FD-1661's scheduler limb) and the demo's `--no-compose` switch | This file, Tasks 0 to 3 | `07` §3.2: FR-432 (the `scheduler` limb only), FR-406 (the outbox relay that the beat schedule runs), FR-413 (the beat process that will run the tick; the tick itself is not built here); FR-408 (the demo entrance, unchanged by an optional flag); register FD-1661 (the scheduler limb closes at merge) | S1c's PR (`draft/s1c-fd1951`) merged or its `deploy/`/`scripts/` diff empty (C1); DP-1 ruled; a build window booked (C3) | 1 + a build window |

**Task 0 — re-read at the base.** At the slice's base, the executor quotes in its `LG-`, each
with its line numbers: `deploy/docker-compose.yml`'s `&gip-worker` anchor and `worker-default`;
`entrypoint.py`'s `beat_schedule`; `deploy_stack_helpers.py`'s `beat_fixture`;
`test_deploy_stack.py`'s `_celery_workers`; and `scripts/demo.py`'s compose call and argument
parser. Where a premise in "Evidence" differs, the executor stops and reports to the lead.

**Task 1 — the `scheduler` service, red first (R1).**
- **Shape tests** in `backend/tests/test_deploy_stack.py`, using its `_load` helper and its
  breaker table (`_break_*` plus `test_each_check_goes_red_on_the_break_it_exists_for`), never a
  new fixture scheme. Each is marked `req("FR-432")`; the beat checks are also marked
  `req("FR-413")` and `req("FR-406")`. Each is seen red **by its cause** on the base, before the
  compose edit:
  - R1.a: `scheduler` exists under the `app` profile (red: no service named `scheduler`);
  - R1.b: it runs `celery -A app.worker.entrypoint beat` from the image `api` and the workers use
    (red: no such command or a different image);
  - R1.c: its command passes `--schedule` with a path under `/tmp` (red: no `--schedule`, the
    cause of the observed `Permission denied: 'celerybeat-schedule'`; the test's docstring cites
    S1c's ledger's S1c-5 setup fault 2);
  - R1.d: it runs as **one** process — no `deploy.replicas` above 1 and no `scale` — and the
    test says why (two beats relay twice; FR-413's tick is "a single periodic Celery beat task").
- **The compose edit:** a `scheduler` service that merges `*gip-worker` (image, build,
  environment, `depends_on`, `stop_grace_period`) and overrides `command` with `["celery", "-A",
  "app.worker.entrypoint", "beat", "--schedule", "/tmp/celerybeat-schedule"]` (or another path
  the container user can write, named in the `LG-`). Its `mem_limit` is declared and marked
  unmeasured, as the anchor's comment marks the workers'. One comment line above it cites FR-432,
  FR-406 and the writable-path reason.
- **Runtime red, then green, on a throwaway project** (C2, C3, C4), recorded in the `LG-` with
  the project name, the image tag and each command's rc:
  - R1 red, part 1 (no scheduler): `up -d --wait` of the backing services, `migrate`, `api` and
    `worker-default` only. A Job is submitted (the `rating.compile` Job of
    `test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker`). It stays
    `queued` past `JOB_TERMINAL_BOUND_SECONDS`, and `select status, count(*) from outbox group by
    1 order by 1` shows a `pending` row. That is A3's `JOB_TIMEOUT` class.
  - R1 red, part 2 (a scheduler without a writable path): the `scheduler` service with
    `--schedule` removed (a scratch override, never committed). `docker compose ps -a` shows it
    `Exited (1)`, and its log contains `Permission denied: 'celerybeat-schedule'`.
  - Green: the committed service. `scheduler` is Up (`celery beat v… db -> /tmp/celerybeat-schedule`
    in its log); the same Job reaches `succeeded`; the outbox query shows `published | N` and no
    `pending` row.
- **The runtime tests use the service.** `test_deploy_stack_runtime.py` starts `scheduler` with
  the services it brings up, in place of `beat_fixture`. `beat_fixture` is then removed from
  `deploy_stack_helpers.py` (its docstring names this service as its successor). `git grep -n
  beat_fixture -- backend/tests` prints nothing.

**Task 2 — the demo's `--no-compose` switch, red first (R2).**
- **Unit tests** in `backend/tests/test_demo_command.py`, beside
  `test_the_compose_target_refuses_naming_the_services_that_are_down` (`:434`), each marked
  `req("FR-408")` and seen red by its cause on the base:
  - R2.a: with `--no-compose`, the local demo runs no `docker compose … up` command (the test
    records the commands passed to `run`). Red on the base: the flag does not exist (`argparse`
    exits 2, quoted), so the switch is absent by cause;
  - R2.b (DP-3 (a)): with `--no-compose` and one of `postgres`, `redis`, `minio`, `keycloak` not
    running, the demo refuses before the migrations step and names the service;
  - R2.c: without the flag, the compose call is unchanged (the default demo is FR-408's one
    command, as before).
- **The code edit:** `scripts/demo.py` gains `--no-compose` (DP-2 (a)). With it, the
  infrastructure step is replaced by the running-services check (DP-3 (a), reusing
  `compose_running`/`check_compose_up` with the four services). Nothing else in the demo changes.
- **Live red and green on the shared stack** — the only shared-stack use, in the gate's demo
  stage (C2), recorded in the `LG-`:
  - R2 red: for a demo run **without** the switch, `docker inspect -f '{{.Name}} {{.Id}}
    {{.State.StartedAt}}' gi-pricing-postgres-1 gi-pricing-redis-1 gi-pricing-minio-1
    gi-pricing-keycloak-1` before and after, with at least one `Id` or `StartedAt` that differs.
    The executor quotes it from an existing gate log that recorded both readings, if one exists.
    Otherwise it asks the lead for one granted run in a no-gate gap. It never runs one unasked.
  - Green: the gate's demo stage runs with `--no-compose`. The same `docker inspect` before and
    after prints four equal lines (`diff` rc 0, quoted).
- **The skill:** `.claude/skills/dev-commands/SKILL.md`, "The demo entrance (FR-408)", gains the
  flag with its reason (the file's `name: gi-pricing` makes the plain call act on the shared
  stack from any worktree), and its `Verified` date is refreshed (`CLAUDE.md` §12).

**Task 3 — the gate and the close lines.** The full gate (Acceptance item 6). The `LG-` carries
the red/green table before the audit, and FD-1661's close line for the scheduler limb is the
auditor's, inside the PR.

### Write set

`deploy/docker-compose.yml`; `backend/tests/test_deploy_stack.py`;
`backend/tests/test_deploy_stack_runtime.py`; `backend/tests/deploy_stack_helpers.py`;
`scripts/demo.py`; `backend/tests/test_demo_command.py`; `.claude/skills/dev-commands/SKILL.md`;
the slice's `LG-`; at the mint, `docs/roadmap.md` (the slice row, and DP-1's dated line on
SL-1689), `docs/INDEX.md` and FD-1661's register row. Anything else stops the slice.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py` and
   `python3 scripts/doc-index.py --check` exit 0 at the branch head, except lines of checks 31
   and 32 that name this plan's own working ids (8281, 8275, 8276), which clear at the mint.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.
3. **The service is declared (R1 green).** On the slice's merge tree,
   `docker compose -f deploy/docker-compose.yml --profile app config --services | grep -x
   scheduler` prints `scheduler`, and `uv run pytest -q backend/tests/test_deploy_stack.py -k
   scheduler` exits 0 with at least 4 tests collected (R1.a to R1.d). The `LG-` quotes each red
   line from the base.
4. **The scheduler drains the outbox (R1 runtime).** The `LG-` quotes, from the build window on
   a throwaway project: R1 part 1 (Job `queued` past the bound, an outbox `pending` row); R1
   part 2 (`Exited (1)` and `Permission denied: 'celerybeat-schedule'`); the green (`scheduler`
   Up, Job `succeeded`, outbox `published | N` with no `pending` row). Under `GIP_DEPLOY_TESTS=1`,
   `test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker` exits 0 with the
   service and without `beat_fixture`; `git grep -n beat_fixture -- backend/tests` prints
   nothing.
5. **The switch recreates nothing (R2).** `uv run pytest -q backend/tests/test_demo_command.py
   -k no_compose` exits 0 with at least 3 tests (R2.a to R2.c), each seen red on the base and
   quoted in the `LG-`. The gate's demo stage runs `scripts/demo.py … --no-compose`, and the
   `LG-` quotes the four `docker inspect` lines (`Name Id StartedAt`) before and after, with
   `diff` rc 0. The R2 red is quoted beside it, from a gate log or a granted run (Task 2).
6. **The full gate is green on the slice's merge tree** — both halves of the `CLAUDE.md` §11
   commands, named against `origin/main...<slice branch>`, gate-1 **SOLO**, with the demo stage
   exercising both changes (the journey under `--no-compose`, with a `scheduler` in the stack
   the demo uses). `deploy/` and `scripts/` change, so the docs-only gate does not apply.
7. **The skill is current.** `git diff origin/main...<slice branch> --
   .claude/skills/dev-commands/SKILL.md` shows the `--no-compose` line and a refreshed
   `Verified` date.
8. **The date.** The slice merges by **Tue 3 Nov 2026** (`date -d 2026-11-03 +%A` prints
   `Tuesday`), and none of its windows overlaps nfr-bench-1's session, Mon 2 – Tue 3 Nov (C5).

## The row, cut

**SL 8275 — WK-674: the scheduler service in `deploy/docker-compose.yml` (FD-1661's scheduler
limb) and the demo's `--no-compose` switch, red first.** `draft`. Ledger LG 8276. Scope: this
file, Tasks 0 to 3. Requirements: FR-432 (the `scheduler` limb), FR-406, FR-413, FR-408; register
FD-1661. Lane: build, one gate-1 SOLO run. Order: after S1c's PR; plan and reds Fri 30 Oct pm;
code, greens and gate Mon 2 Nov, never beside nfr-bench-1; merged by Tue 3 Nov 2026. Its row in
`docs/roadmap.md`, under WK-674 after SL-1689, is written at the mint with the minted ids, as
`PL-1937` did. This branch writes no roadmap row, so it does not edit a file that every open
branch edits.

## Hand-off (not this plan's writes)

- **The maintainer:** rule DP-1 and the plan's `PL-` id at the mint. The minted ids of SL 8275
  and LG 8276 have two projections on record: the entry "2026-10-29 10:27:26 GMT" names the two
  ids after S1c's, and the entry "2026-10-29 17:11:12 GMT" item (2) names SL 1968 / LG 1969 (space form: not minted at this base). The
  mint map rules which, in merge order; this plan writes neither.
- **The lead:** list this delta on WK-674's roadmap row (L5); book the build window (C3);
  confirm DP-2 and DP-3 or rule otherwise before the GO; decide when gates may pair again after
  the merge (this plan only makes it possible).
- **The gate template** (`scratch/gate-template-demostop.sh`, the lead's): its demo stage adds
  `--no-compose` once this slice merges. The keycloak-only restore of common item 24 can then be
  reviewed; that is the lead's call, not this slice's.
- **The register minter:** FD-1661's dated line naming SL 8275's minted id as the row that closes
  the scheduler limb, and SL-1689 (DP-1 (a)) as the frontend limb's row.

## Self-review

- **Spec coverage.** FR-432 (the `scheduler` limb only), FR-406, FR-413 and FR-408, each named.
  The `frontend` limb stays SL-1689's (DP-1). FR-413's tick is not built; the service runs the
  schedule that exists. No requirement id is added or changed.
- **The brief's two reds at every site.** R1 (no scheduler, then no writable path): Task 1 and
  Acceptance items 3 and 4. R2 (the compose coupling): Task 2 and Acceptance item 5. The gate:
  Task 3 and Acceptance item 6.
- **Literals verified at `447bcfd6`:** `deploy/docker-compose.yml:7`, `:12`, `:26`, `:161`,
  `:174`, `:179`, `:184`; `entrypoint.py:60-66`; `deploy_stack_helpers.py:270`;
  `test_deploy_stack_runtime.py:311`, `:457`; `test_deploy_stack.py:77-83`;
  `scripts/demo.py:317`, `:478-486`; `test_demo_command.py:434`. S1c's ledger's S1c-5 section at
  `fa1a5ad9`. The weekdays: `date -d 2026-10-30 +%A` = Friday, `2026-11-02` = Monday,
  `2026-11-03` = Tuesday.
- **The red for R2 is honest about the live record.** A changed `StartedAt` shows a restart, and
  a changed `Id` shows a recreate. The `LG-` quotes both fields, so the red stands whichever one
  happened.
- **Placeholders.** `<slice branch>`, `<branch>`, `<head>`, `<name>` and `N` are values read when
  the slice runs.
