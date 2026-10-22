---
id: LG-8137
family: ledger
title: WK-674 slice SL-1689 — the scheduler (beat) and frontend-image row, FR-432's last two limbs (PL-1688) (slice ledger)
status: active                # active → closed (§1.2a)
created: 2026-10-21 # filed 2026-10-21 under working id 8137
owner: executor
tree: 44c18e11ca028d25c8b4c9d92077cc0f3622ef8e
phase: P2
work: WK-674
slice: SL-1689
plans: [PL-1688]
corrected_by: []
relates: [PL-1688, PL-1237, PL-1537, PL-1620, PL-1666, PL-1714, SL-1689, SL-1258, FD-1661]
---

# LG-8137 — WK-674 slice SL-1689: the scheduler and frontend-image row

Filed 2026-10-21 under working id 8137 (lead-reserved in eta.md). Executor seat `exec-1689`, base `origin/main` 44c18e11ca028d25c8b4c9d92077cc0f3622ef8e, branch `sl-1689-wk674-scheduler-frontend-image`. Scope: PL-1688, Tasks 0 to 4 and its write set.

**GO:** the maintainer's (by delegation) entry "2026-10-21 15:03:33 BST — Maintainer: GOs on the 15:02:44 work queue", item 3. **MERGE-ACK:** not yet given.

## Needs census (on main 44c18e11)

- `SL-1258` merged: `deploy/Dockerfile`, `deploy/lb.conf`, `backend/tests/test_deploy_stack.py` and `test_deploy_stack_runtime.py` are on main. The worker is one service per pool (`worker-compute`, `-scoring`, `-io`, `-default`, PL-1714 DP-Q1 (b)), so DP-B1 is met as "every routed pool consumed" (the roadmap's dated line on SL-1689's activation need).
- B0.1 census, `git diff --name-only origin/main...origin/<branch> -- deploy/ backend/tests/deploy_stack_helpers.py` over every `git ls-remote --heads origin` branch: none touches `deploy/` or the helpers file.
- `PL-1688`: front matter `status: active`; DP-B1 and DP-B2 ruled.

## Task 0 — premises re-read at 44c18e11

- The `worker` command is now four services (`deploy/docker-compose.yml`, `worker-compute` anchor `&gip-worker` and three `<<: *gip-worker`), each `--queues <one pool>`; the relay rides `default` (`RELAY_QUEUE`).
- Root `.dockerignore` excludes `frontend`, `docs`, `examples`, `.claude`, `graphify-out`, `.venv` and caches. Unchanged by this slice (guard test).
- `backend/src/app/worker/entrypoint.py` `beat_schedule`: `relay-outbox`, `timedelta(seconds=1)`, queue `RELAY_QUEUE.value`.
- Realm `redirectUris` and `webOrigins`: `:5173` only (`realm-gi-pricing.json:16-17`); not edited (DP-B2 (a)).
- BuildKit: `docker buildx version` prints `github.com/docker/buildx 0.13.1+ds1`, and `docker compose version` prints `v5.4.0`, which builds through buildx.
- The cheapest Job with a terminal state: `rating.compile`, queue `default` (the existing runtime test's Job).
- **Finding outside the write set:** `beat_fixture` (`deploy_stack_helpers.py`) starts a one-off beat and says it is SL-1689's to replace. Reported to the lead; see Tasks.

## Tasks

- **T1/T2 red first** (`run-small` on `backend/tests/test_deploy_stack.py` at the activation head cdd37815 plus the new tests): `12 failed, 23 passed`. Causes quoted: `no service named scheduler`, `no service named frontend`, `frontend.nginx.conf does not exist`, `scheduler does not wait for migrate to complete` (plus the redis line), and `KeyError: 'scheduler'` / `'frontend'` in the seven breaker rows.
- **T1/T2 green** (commit c80009ad): `35 passed`. `docker compose -f deploy/docker-compose.yml --profile app config --services` prints `api frontend lb migrate minio postgres redis scheduler worker-compute worker-default worker-io worker-scoring`. Guard `test_the_backend_image_context_still_excludes_the_frontend` is green at base and head by construction.
- **T3** (commit 1cc2fe80): `test_the_scheduler_service_is_what_moves_a_job_out_of_the_outbox`, skipped without `GIP_DEPLOY_TESTS=1` (`8 skipped`). Its run, the stopped-scheduler red and the fresh-checkout curl lines are owed to the build window.
- **T4** (commit after c80009ad): `git grep -n -i nginx -- docs/skills-map.md docs/specs/07-platform.md` printed nothing at base, so the nginx row is added to both, and the Compose rows note the Node build stage.
- **Write-set addition (SL-1689 option A):** `backend/tests/deploy_stack_helpers.py` joins the write set, ruled in the maintainer's (by delegation) entry "2026-10-21 15:12:08 BST", item (c). `beat_fixture` now runs `up -d --wait scheduler` (no in-process beat) and asserts `one_beat_problems(compose ps -a)` is empty, so exactly one running beat container exists, and it is the `scheduler` service. Red first (always-green stub): `4 failed, 36 passed`, with FAILED lines `test_one_beat_goes_red_on_a_double_or_absent_beat[rows0..rows3]` (two schedulers, scheduler plus a beat on another service, no beat, an exited scheduler). Green with the check: `40 passed`.

## PRs

None yet. The slice stops at PR-READY; the lead opens the PR.

## PREP window — 2026-10-22 (exec-1689, edits only; no compose, no tests)

**GO:** the maintainer's (by delegation) message of 2026-10-22 15:47 ("SL-1689 PREP") and the lead's entry "2026-10-22 15:43:10 BST" in `to-lead.md`. Edits and git only: no compose up/build/run, no pytest or vitest, until SL-1711 merges (PL-1688:121, serialised on `deploy/docker-compose.yml`).

**Done in PREP:** `origin/main` (`f3462d8f`) re-merged into the branch (`git merge --no-ff`); the only conflict was `docs/INDEX.md` (taken from main, regenerated with `doc-index.py`, `--check` rc 0). The branch content was reviewed against PL-1688 Tasks 0 to 4 and the write set: Tasks 1, 2, 3, 4 and option A are all present (commits `c80009ad`, `cac622f8`, `1cc2fe80`, `32257078`); no task is missing. `ruff check` on the three changed test files: rc 0. `ruff format --check` and `mypy` on those files report differences that also exist at `origin/main` (the format check fails on `origin/main`'s copy of all three files; mypy does not cover `backend/tests/`), so they are not this slice's and are not reformatted here.

**Waits for SL-1711's merge** (the lead announces it; `git diff --stat origin/main -- deploy` on tools-main must be empty first):
1. A second re-merge of `origin/main` onto the branch (`deploy/docker-compose.yml` conflicts are possible: resolve only if mechanical, else STOP).
2. The DB/compose windows (lead-granted in writing, load1 < 8 and memory floor read at start, two quoted zeros at the end): the Task 3 green run, the stopped-scheduler red, the one-beat red/green, and the fresh-checkout image build and three curl lines (Acceptance 5).
3. The GREEN set at the re-merged head (below), then the gate, then PR-READY.

**Import-closure GREEN set (seat-brief item 29), derived at branch head after the `f3462d8f` merge.**
- Changed modules: `git diff --name-only origin/main...HEAD -- backend/src packages frontend/src` prints nothing (0 files). The slice changes tests, deploy files and docs only.
- Test files that import a changed test module: `git grep -n -E "deploy_stack_helpers|test_deploy_stack" -- backend packages scripts` finds the importers of `backend/tests/deploy_stack_helpers.py`: `backend/tests/test_deploy_stack_runtime.py`, `backend/tests/test_deploy_switch_runtime.py`; `scripts/bench-deploy-path.py` imports `api` and `governed_workspace` (neither changed). `test_deploy_stack.py` reads `deploy/docker-compose.yml` directly.
- GREEN = `backend/tests/test_deploy_stack.py`, `backend/tests/test_deploy_stack_runtime.py`, `backend/tests/test_deploy_switch_runtime.py`. Re-derive both greps at the re-merged head; add any new importer.

**Exact commands for the windows** (W = `/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1689`; the same list is in `~/gi-pricing-plan.local/handover/sl-1689-window-commands-2026-10-22.md`):
```
git -C $W fetch origin && git -C $W merge --no-ff origin/main          # then doc-index.py under flock gate-2, --check rc 0
# shape tests + GREEN set, three files at most per run-small call (3 here; runtime files skip without GIP_DEPLOY_TESTS):
~/gi-pricing-plan.local/handover/run-small.sh $W backend/tests/test_deploy_stack.py backend/tests/test_deploy_stack_runtime.py backend/tests/test_deploy_switch_runtime.py
# build window (lead GRANT; read cut -d" " -f1 /proc/loadavg and free -g first):
SHA=$(git -C $W rev-parse HEAD); echo "logs SHA-first: $SHA"
GIP_DEPLOY_TESTS=1 uv run --directory $W pytest -q backend/tests/test_deploy_stack_runtime.py -k "scheduler or one_beat" 2>&1 | tee <logdir>/$SHA-t3-green.log
# red: stop the scheduler (compose stop scheduler inside the test, or run with the scheduler service removed) and quote the 'queued' failure line
# fresh checkout (Acceptance 5): git -C /home/puzhenhao1989/gi-pricing-plan worktree add <dir> $SHA; docker build -f deploy/frontend.Dockerfile -t gi-pricing-web:$SHA <dir>; then curl -s -o /dev/null -w '%{http_code}' for / , a deep SPA route, /api/v1/... (never 502)
# end of every DB window: redis-cli -n <db> dbsize = 0 and pg_database count = 0; keycloak bind source restored from tools-main (item 24)
```
