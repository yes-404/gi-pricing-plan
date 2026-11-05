---
id: LG-8320
family: ledger
title: WK-674 slice SL-1689 — the frontend image and service (FR-432's last limb, FD-1661) and FD-1816, the roll leaves a stopped pre-roll container (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05            # filed under working id 8320
owner: executor
tree: ddab6d02ba290810c8cff0e83f4f63b106f41f18   # sl-1689-d-frontend-fd1816, the commit this was written against (base 1f3f67cf1709eb209c73d1e23c72819df4b95ae3)
slice: SL-1689
phase: P2
work: WK-674
plans: [PL-8319]
corrected_by: []
relates: [FD-1661, FD-1816, PL-8319, FR-432, NFR-531]
---

# LG-8320 — WK-674 slice SL-1689: the frontend image and service, and FD-1816

**GO:** the maintainer's entry "2026-11-05 09:58:58 GMT" (to-lead): "ORDER: WK-674's pair first
(FD-1661 frontend limb + FD-1816, one SOLO compose gate)"; DP-D1 (a) and DP-D2 (docs only) per
"2026-11-05 10:08:53 GMT"; the BUILD WINDOW granted in writing by lead 30, START 2026-11-05 10:12:44 GMT.
**MERGE-ACK:** not yet.

## Tasks

### Scope

`PL-8319` (draft branch `draft/pl-d-2026-11-05` at `1f3f67cf`), the SL-1689 row, Tasks R0 to R4 and G.
Requirements: FR-432 (the `frontend` limb), NFR-531 (the roll is unchanged on its success path).
Register: FD-1661, FD-1816. The gate G, the mint, A12 and A13 are not this executor's (brief).
No shared database and no shared Redis were used; the runtime tests ran on the throwaway project `gip-s4-runtime`.

**B1, the ported hunks** (read from the KEEP branch `sl-1689-wk674-scheduler-frontend-image`; never merged):

| Hunk | Source | Change on port |
|---|---|---|
| `deploy/frontend.Dockerfile`, `.dockerignore`, `frontend.nginx.conf` | `c80009ad` | unchanged |
| `frontend` compose service | `c80009ad` `deploy/docker-compose.yml` | port is `127.0.0.1:${GIP_WEB_PORT:-5173}:80` (B4, #1378); comment re-read |
| frontend checks, `nginx_conf_problems`, guard, two breaker rows, nginx-conf test | `c80009ad` `backend/tests/test_deploy_stack.py` | port check on `127.0.0.1:`; third breaker `_break_frontend_on_every_interface` is new |
| skills-map and `07` §8 rows (nginx; Compose row note) | `cac622f8` | unchanged |
| README `frontend` bullet | `cac622f8` | port text `127.0.0.1:${GIP_WEB_PORT:-5173}`; the scheduler line is not taken (SL-1968 has it) |
| isolated overlay `frontend: ports: !override ["127.0.0.1::80"]` | new | the overlay had no entry |

### Task list

- **R0** — census (B2), line cites, Compose read. Discharged; see Build log.
- **R1** — shape tests red, then green (A2, A3). Discharged.
- **R2** — `_build_frontend_from_commit`, the runtime test (A5). Discharged.
- **R3** — FD-1816 red then green (A6), whole runtime file (A7). Discharged.
- **R4** — docs, same PR (A8). Edits made; audit-docs below.
- **G** — the SOLO gate: not run by this seat.

### Gate

Not run (brief). Small runs and the window are in the Build log. GREEN set by import closure (common seat
brief item 29): changed modules `git diff --name-only origin/main...HEAD -- backend deploy scripts`; the only
changed Python module others import is `backend/tests/deploy_stack_helpers.py`; its importers are
`git grep -ln deploy_stack_helpers -- backend scripts` = `test_deploy_stack.py`, `test_deploy_stack_runtime.py`,
`test_deploy_switch_runtime.py`, `scripts/bench-deploy-path.py` (no importers of those). Compose-reading
tests: `test_compose_binds.py`. GREEN = those three test files plus `test_compose_binds.py`.

### Audit

Not yet (the slice's auditor).

### Build log

- **2026-11-05 10:12 UTC, R0 census and cites.** Over every remote head, `git diff --name-only
  origin/main...<b> -- deploy/` printed only `origin/sl-1689-wk674-scheduler-frontend-image` (the KEEP
  branch); origin/main `dae9637e`. Compose ports at `deploy/docker-compose.yml:39,54,69,95,194` hold;
  `roll-api.sh:30,36,59,61` hold.
- **R1 red** at `1f3f67cf`, `run-small.sh` on `backend/tests/test_deploy_stack.py` (rc 1, `5 failed, 34 passed`):
  `AssertionError: assert ['no service named frontend'] == []`;
  `AssertionError: assert ['frontend.ng...es not exist'] == []` (frontend.nginx.conf does not exist);
  the three new breaker rows red by `KeyError: 'frontend'` (not a red by cause, proved by their own run below).
  Test commit `86633658`.
- **R1 green**, commit `52595183`, same file: `39 passed, 2 warnings`, rc 0. The three breaker rows pass,
  so each check goes red on its break. Frontend tests: 3 shape + 3 breaker rows + 2 nginx-conf cases = 8
  (`-k frontend` is refused by `run-small.sh`; the count is by name).
- **Window 2026-11-05 10:12:44 to 10:41:17 UTC.** `df -h /` before: 6.4G free (89%); load1 1.83.
  Shared stack before and after: `gi-pricing-postgres-1`, `-keycloak-1`, `-minio-1`, `-redis-1` all
  `Up 43 hours (healthy)`; keycloak bind source
  `.../.claude/worktrees/tools-main/deploy/keycloak-local`. Nothing ran against project `gi-pricing`.
- **R0 Compose read** (project `gip-s4-runtime`, image of `1f3f67cf`): `up --scale api=3` gave three healthy
  containers; after `docker stop` of one, `up -d --no-deps --no-recreate --scale api=4 api` **started the stopped
  container and created one new one** (`Up Less than a second` for both). This matches the plan's Evidence,
  so DP-D1 (a) stands. Log: `~/gi-pricing-plan.local/scratch/sl-1689d/r0.log`.
- **First-build footprint:** the first app image build took `df -h /` from 6.4G to 3.8G free (2.6G; the
  app image is 2.9GB). The frontend image is 49.6MB. Later free space read 12G; the cause was not this seat
  (no prune was run). The floor for the next window is about 4G.
- **R3 red** (N=`5575547b`, N1=`1f3f67cf`, `GIP_DEPLOY_TESTS=1`): roll-api printed
  `cleanup: removed new 9a22623ccc18` and `AssertionError: cleanup removed the stopped pre-roll container
  9a22623ccc18` (`rc=1`). **R3 green** after `1a95e467`: `1 passed in 95.22s`. Logs `r3red.log`, `r3green.log`.
- **A7 + R2**, the whole `backend/tests/test_deploy_stack_runtime.py`, `GIP_N_SHA=5575547b`,
  `GIP_N1_SHA=1f3f67cf`, tests at head `ddab6d02`: `10 passed, 2 warnings in 1143.93s`, rc 0, naming
  `test_previous_version_serves_the_migrated_schema_and_rolls_forward_with_no_failures`,
  `test_a_failed_api_roll_leaves_the_pre_roll_replicas_and_no_never_healthy_one` and
  `test_a_failed_api_roll_leaves_a_stopped_pre_roll_container`. The images were built from `5575547b`; the
  later commits change `roll-api.sh` and docs only, neither inside an image. Log `a7.log`.
- **A5**, the frontend image from `git archive 5575547b` (first build, no red): `GET / -> 200 text/html`;
  `GET /data/some-dataset/rules -> 200 text/html` (history fallback); `GET /api/v1/auth/config -> 200
  application/json` (the API's own answer through `lb`, not nginx's 502).
- **Window end:** `docker ps -a --filter label=com.docker.compose.project=gip-s4-runtime -q | wc -l` = 0;
  `docker image rm` by exact tag of `gi-pricing-frontend:5575547b`, `gi-pricing-app:5575547b`,
  `gi-pricing-app:1f3f67cf` printed 3 Untagged lines; `df -h /` 11G free (82%).
- **DP-D2 (a)** applied: `demo.py` unchanged; the README build block gains the frontend `docker build` line
  and the buildx note. Hand-off to SL-1913's owner: a bare `up` needs `gi-pricing-frontend:$GIP_BUILD` built first.
- Seat slip, recorded: one early call ran a bare `cd /tmp` (no-cd breach); the shell reset and nothing was written.

## PRs

None yet (the seat does not push).
