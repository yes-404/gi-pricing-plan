---
id: FD-1970
family: finding
title: the compose runtime tests cannot provision the application login role, so no runtime test can go green, since #1398
status: closed
created: 2026-10-29               # drafted 2026-10-29 under working id 8280
owner: WK-674
tree: 67284ea12daab613b67353e3eb8b728a35ca5023   # origin/draft/sl-8275 as read by the auditor, 2026-10-29
corrected_by: []
relates: [FD-1661, SL-1968, LG-1969, PL-1688]
---

# FD-1970 — the compose runtime tests cannot provision the application login role, so no runtime test can go green, since #1398

## Finding

**MEDIUM; owner WK-674; fixed in SL-1968 / LG-1969 (this slice), so the finding is filed and closed in the same PR.** Authority:
the maintainer (by delegation), to-lead "2026-10-29 19:19:28 GMT", ruling (A) with conditions (i) to (iii). Filed under working id 8280 (minted as FD-1970 on 2026-10-29).

Since #1398 (S1c) the compose `api` connects as `gip_app_login`. On a fresh volume that role exists with no password until
`scripts/provision-app-role.py --allow-default-password` runs against the stack's own Postgres after `migrate`
(`deploy/docker-compose.yml`, the postgres volume comment: "the compose run calls scripts/provision-app-role.py"). No test under
`backend/tests/` that brings the stack up (`deploy_stack_helpers.compose`) ran it. So every compose runtime test that starts `api`
fails: `api` exits 3 with `password authentication failed for user "gip_app_login"`. A second effect: an unprovisioned role also
kills beat on its first relay tick (`scheduler exited`). The seed's owner connection also needs `GIP_TEST_DATABASE_URL`, which no
runtime helper set. The "since" is proved by the first Evidence bullet below; the defect is observed at `origin/main` `1e17ec63`.

## Evidence

- **The "since #1398" (read at the commit, not taken from the draft title):** `git log --format='%h %ad %s' --date=short -S'gip_app_login' -- deploy/docker-compose.yml` lists, as its earliest commit, `1e0a8abb 2026-10-26 fix(db,deploy,tests): the application connects as a login role, not the owner — FD-1729 part 1 (SL-1942, LG-1941, OQ-1943, OQ-1944, FD-1945, RS-1946) (#1398)`. `git show 1e0a8abb -- deploy/docker-compose.yml` adds `GIP_DATABASE_URL: postgresql+asyncpg://gip_app_login:gip_app_login@postgres:5432/gipricing   # FD-1729: the application's login role (DP-16 (a))` and the postgres volume comment "calls scripts/provision-app-role.py" (a second `-S'provision-app-role' -- scripts deploy backend/app` search also ends at `1e0a8abb`). That commit is the first to make the compose `api` need a provisioned password for `gip_app_login`.

All from `LG-1969`, section "F2" (and "Build window"), at the heads named there; the auditor re-read the lines and the code at the tree above, and re-ran nothing.

- **The defect (condition iii), at `origin/main` `1e17ec6382de5919b6e3011242b584a59bb880e7`**, on a throwaway detached checkout
  (not the slice worktree): `test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker` under `GIP_DEPLOY_TESTS=1`:
  `1 failed, 2 warnings in 42.28s`, rc=1. The `api` container: `exited exit=3`, log `password authentication failed for user "gip_app_login"`.
- **Same failure at the slice's base plus its scheduler, head `1a3a8483`:** `1 failed, 2 warnings in 46.16s`, rc=1 (`CalledProcessError`
  from `docker compose … up`, then the conftest_db `GIP_TEST_DATABASE_URL is not set` warning).
- **(i) the refusal, red then green:** `own_postgres_owner_url(port)` (`backend/tests/deploy_stack_helpers.py`) raises `ValueError` on the
  shared 5432 before any DDL. `test_provisioning_refuses_the_shared_postgres_port_and_names_the_projects_own`: RED on a stub with no
  guard, `Failed: DID NOT RAISE ValueError`, `1 failed, 30 passed`, rc=1 (head `d72b064e` + the stub); GREEN with the guard, `31 passed`, rc=0.
- **(ii) the env does not leak:** `envcheck.py` at `c6716e04`: `before: None`; `after up: …@127.0.0.1:32833/gipricing` with
  `provisioned: ['gip-s4-runtime']`; `after down: None`, `provisioned: []`; `env | grep GIP_TEST_DATABASE_URL` empty, grep rc=1.
- **Green after the fix:** the four `beat_fixture` callers at `c6716e048dc4bd98babeca0a4c7a709a7c17f2c5` under `GIP_DEPLOY_TESTS=1`:
  `2 passed in 132.40s` rc=0, and `1 failed, 2 passed in 174.26s` rc=1 where the one failure is the switch test (no stack started; its own
  finding F3 in `LG-1969`, fixed at `870d08f5`: `1 passed, 2 warnings in 71.75s`, rc=0).

## Severity

**MEDIUM.** Test-only: no production code path, price or hash moves. It is a latent red: the runtime tests run only under
`GIP_DEPLOY_TESTS=1` (not in the gate), so no gated run saw it, but with it no compose runtime test can pass at `origin/main`, and the exit
demo's compose journey rests on the same stack (the roadmap's WF-701 row).

## Remedy

(A), in SL-1968: `compose()` in `backend/tests/deploy_stack_helpers.py` runs `_provision_once` on a project's first `up`: it brings up the
project's own `postgres`, builds the owner URL from the mapped port (refusing 5432 before any DDL), runs `migrate`, then
`provision-app-role.py --allow-default-password` against that URL, and sets `GIP_TEST_DATABASE_URL`; `down` resets both.
Fixed here; the close lines are in the same PR.

## Provenance

Found by exec-beatgreen in SL-1968's build window (2026-10-29 19:05 GMT onward), ruled (A) by the maintainer (by delegation) at
to-lead "2026-10-29 19:19:28 GMT". Drafted by the auditor from `LG-1969`'s F2 lines.

## Disposition

Fixed in SL-1968 / LG-1969; see the close line. (Residual noted by the auditor: `_provisioned.add(PROJECT)` runs before the DDL steps, so a
failed `migrate` leaves the project marked provisioned for the rest of the process; not a defect in a run that passes. Not a finding.)

***Resolved 2026-10-29***: closed by the merged fix, this PR (SL-1968 / LG-1969; the merge sha is added at the read-back). `compose()` in `backend/tests/deploy_stack_helpers.py` runs the project's own postgres, `migrate`, `scripts/provision-app-role.py --allow-default-password` against the project's mapped port (refused on 5432 before any DDL), and sets `GIP_TEST_DATABASE_URL`, reset by `down`. Evidence: red at `1e17ec63`, `1 failed … 42.28s`, `api` exit 3; refusal red `DID NOT RAISE ValueError` then green `31 passed`; env before `None`, after up the project's own port, after down `None`; the four `beat_fixture` callers green at `c6716e04` (`2 passed` + `2 passed`), the fifth at `870d08f5` (`1 passed … 71.75s`). Gate: LG-1969 "END" and its audit section (A7).
