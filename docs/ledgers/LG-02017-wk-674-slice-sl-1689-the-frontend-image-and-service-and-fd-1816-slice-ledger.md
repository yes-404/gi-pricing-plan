---
id: LG-2017
family: ledger
title: WK-674 slice SL-1689 — the frontend image and service (FR-432's last limb, FD-1661) and FD-1816, the roll leaves a stopped pre-roll container (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-05            # filed under working id 8320
owner: executor
tree: 81b0bb869439efd929e2599da9373fac19039eda   # the mint head's tree (the commit the mint ran on; refreshed at the mint, A13)
slice: SL-1689
phase: P2
work: WK-674
plans: [PL-2016]
corrected_by: []
relates: [FD-1661, FD-1816, FD-1211, FD-1199, FD-2018, PL-2016, FR-432, NFR-531]
---

# LG-2017 — WK-674 slice SL-1689: the frontend image and service, and FD-1816

**GO:** the maintainer's entry "2026-11-05 09:58:58 GMT" (to-lead): "ORDER: WK-674's pair first
(FD-1661 frontend limb + FD-1816, one SOLO compose gate)"; DP-D1 (a) and DP-D2 (docs only) per
"2026-11-05 10:08:53 GMT"; the BUILD WINDOW granted in writing by lead 30, START 2026-11-05 10:12:44 GMT.
**MERGE-ACK:** not yet.

## Tasks

### Scope

`PL-2016` (draft branch `draft/pl-d-2026-11-05` at `1f3f67cf`), the SL-1689 row, Tasks R0 to R4 and G.
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
- **FD-1211** — the served-process SIGTERM proof (brief amendment 10:32:58). Discharged; see Build log.
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

**Auditor:** aud-sld (auditor, Sonnet 5), 2026-11-05. **Object:** `origin/main...HEAD` where `origin/main` is `bdad1322` and HEAD is
`32d33309bd3196c2b8e9a227b3a67f316003e5f1` (tree `5e318ca0fb3bff17aa7aec410c77abff94f5e5c6`, the merge of `bdad1322` into
`sl-1689-d-frontend-fd1816`), read in the auditor's own detached worktree `.claude/worktrees/aud-sld`. The slice's own
worktree was never entered (it was the gate's instrument). `git -C <wt> diff --name-only bdad1322...HEAD` lists 16 paths: the
Write set of PL-2016 plus `deploy/Dockerfile` (widened by the ruling of 2026-11-05 10:53:50 GMT, named in the Build log), the
plan itself and `docs/INDEX.md` (its two rows came in with the plan's own commit `1f3f67cf`). Nothing is under `frontend/`,
`backend/src/`, `packages/` or `scripts/`.

**Ledger pairing, two ways.** All 12 SHAs the Build log cites (`86633658 52595183 5575547b 1a95e467 ddab6d02 ba6c8bb6 d18564bb
287932d0 b516697f 637952ae 4160fead 1f3f67cf`) exit 0 under `git -C <wt> merge-base --is-ancestor <sha> HEAD`. Every
slice commit in `git log --no-merges bdad1322..HEAD` is named by a Build-log line.

**Criteria first (PL-2016 "Acceptance Standard", quoted by id), then the evidence read to the assert.**

| Item | Criterion (PL-2016) | Evidence read | Verdict |
|---|---|---|---|
| 1 | The plan passes the docs checks; after the mint `audit-docs` and `doc-index --check` exit 0 | `audit3.log` (`head=4160fead`) rc=1, the failing lines are check 31/32 on working ids 8319/8320 and check 39 (INDEX stale), the mint's own | MET-BY-RECORD for the pre-mint form; the post-mint rc 0 is OWED-TO-MINT |
| 2 | No requirement range in the plan | not re-run by the auditor; the plan is unchanged since `1f3f67cf` (`git diff` of the plan against the draft head is empty) | MET-BY-RECORD |
| A1 | `git diff --name-only origin/main...HEAD` lists only the Write set | the 16 paths above; `deploy/Dockerfile` is outside the plan's Write set but inside the ruling of 10:53:50 GMT, which the Build log names | MET (the widening is recorded) |
| A2 | Red first, by cause, for each finding, on the named base | R1, the LG's quoted reds at `1f3f67cf`: `assert ['no service named frontend'] == []`, `frontend.nginx.conf does not exist`; the three breaker rows are `KeyError: 'frontend'`, which the plan itself says is not a red by cause and proved by their own run (`47 passed` in `small.log`, `head=ba6c8bb6`, rc=0). FD-1816: `r3red.log` (`head=5575547b`) quotes `roll-api 10:19:37.691 cleanup: removed new 9a22623ccc18` and `AssertionError: cleanup removed the stopped pre-roll container 9a22623ccc18`, rc=1 | MET. **Observation:** the port-check's own line (the plan's third A2 item) has no red of its own: `_break_frontend_on_every_interface` is red only by the missing service at the base, and by its own run afterwards. The plan's own R1 text says so; recorded, not a defect |
| A3 | `pytest -q backend/tests/test_deploy_stack.py -k frontend` rc 0, at least 4 tests collected; three frontend breaker rows each seen red on their break | the LG ran the whole file (`-k` is refused by `run-small.sh`): `39 passed`, then `47 passed` with `test_compose_binds.py`; frontend tests counted by name: 3 shape + 3 breaker rows + 2 nginx-conf cases = 8 (`def test_*frontend*` at `test_deploy_stack.py:417,422,427`, breakers at `:492,496,500`, table rows at `:521-523`) | MET (whole-file run, count by name) |
| A4 | `compose config --services` with the `app` profile lists the declared services; with no profile it is unchanged (three services) | **the LG quotes no `config --services` output for A4**; the shape tests parse the compose file but are not that command. The auditor ran no docker command (ban) | **OWED-TO-GATE** (a one-line `docker compose … config --services` read at the re-merged head; not guessed) |
| A5 | In the window under `GIP_DEPLOY_TESTS=1` the runtime test passes on an image built from `git archive <sha>`: `/` 200 `text/html`, a deep route 200, an `/api/v1/…` route the API's own status, never 502; the LG quotes the three statuses with the sha | LG Build log, A5 line: `GET / -> 200 text/html`; `GET /data/some-dataset/rules -> 200 text/html`; `GET /api/v1/auth/config -> 200 application/json`, image from `git archive 5575547b`. The test body asserts exactly these (`test_the_frontend_serves_the_spa_and_reaches_the_api_through_lb`) and `a7.log` lists it as PASSED. **Observation:** the third response is asserted as "not 502 and a JSON content type, `json.loads` succeeds", not as an RFC 9457 body; `/api/v1/auth/config` is a 200, so it is the API's answer but not a problem document. The criterion's "RFC 9457 body" half has no assert | MET-BY-RECORD for the runtime stages (the window's log). The window ran at `5575547b`; the gate's re-run at the re-merged head is **OWED-TO-GATE**. The RFC 9457 half is a **gap in the criterion's own wording**, recorded here as a dated note on the plan's A5 (2026-11-05): read the criterion as "an API answer", not "an RFC 9457 body"; the plan is frozen at its date and is not edited; not a defect of the slice |
| A6 | FD-1816's test is seen red at the base and green at the head, the stopped pre-roll container present after a failed roll | red: `r3red.log` as in A2; green: `r3green.log` (`head=1a95e467`) `1 passed in 95.22s`, rc=0. By ruling the red is the LG's record and is not re-run | MET-BY-RECORD (the LG is the record, by ruling). The gate's runtime stage is its own evidence at the re-merged head: **OWED-TO-GATE** |
| A7 | The whole `test_deploy_stack_runtime.py` passes at the head, naming the NFR-531 roll test and the failed-roll test | `a7.log`: first line `head=1a95e4671a14e6800210b48db015468858326300 (N=5575547b N1=1f3f67cf)`, `10 passed, 2 warnings in 1143.93s`, rc=0. **The LG's Build log says "tests at head `ddab6d02`"; the log's own first line says `1a95e467`.** `git diff --stat 1a95e467 ddab6d02` is README, skills-map and `07` only, so no test or script differs: the claim holds, the sha in the LG line is the wrong one (proposed correction below). **The file has since gained three tests** (`287932d0`, `b516697f` and the two FD-1211 tests), which were run singly (`fd1211b.log`, `img-green.log`) and not within a whole-file run | MET-BY-RECORD at `1a95e467` for the 10 tests it held. A whole-file run at the re-merged head is **OWED-TO-GATE** |
| A8 | `git grep -n -i nginx -- docs/skills-map.md docs/specs/07-platform.md` prints the two new rows; the `07` diff touches §8 only, no requirement id; `audit-docs` rc 0 at the minted head | `git diff bdad1322...HEAD -- docs/specs/07-platform.md` is one table row changed and one added, both in the §8 tech table (hunk at line 499, no `FR-`/`NFR-` id added or changed); `docs/skills-map.md` gains the `nginx` row and the Compose row note | MET for the diff; `audit-docs` rc 0 at the minted head is OWED-TO-MINT |
| A9 | Shared stack unchanged before and after; keycloak bind under tools-main; nothing against project `gi-pricing`; the window's cleanup quotes the project's container count 0 | LG Build log: stack `Up 43 hours (healthy)` before and after window 1; `Up 44 hours` and `Up 45 hours` at the ends of window 2; keycloak bind under tools-main; `docker ps -a --filter label=com.docker.compose.project=gip-s4-runtime -q \| wc -l` = 0 at each window end; images removed by exact tag; no prune by the seat (the maintainer's `docker builder prune` at 10:18:02 UTC is recorded as his) | MET-BY-RECORD (docker output is the executor's; the auditor ran no docker). **Observation:** the LG quotes the three reads for window 1, and a shorter form for window 2 (containers 0, stack up, keycloak bind), which carries all three facts |
| A10 | The GREEN set by import closure, commands and list quoted | LG "Gate": changed modules `git diff --name-only origin/main...HEAD -- backend deploy scripts`; importers `git grep -ln deploy_stack_helpers -- backend scripts` = `test_deploy_stack.py`, `test_deploy_stack_runtime.py`, `test_deploy_switch_runtime.py`, `scripts/bench-deploy-path.py` (the auditor's re-run at `32d33309` prints the same four). **The LG then says "no importers of those", and that is wrong:** `backend/tests/test_bench_deploy_path.py:15-19` loads `scripts/bench-deploy-path.py` by path with `importlib.util.spec_from_file_location`, and that script imports the changed helper (`scripts/bench-deploy-path.py:140`, inside a function). A text grep for an `import` statement does not see it; the closure does. The test is DB-free (it builds `SimpleNamespace`s) | **NOT MET as written** (GREEN set one file short). `backend/tests/test_bench_deploy_path.py` joins the GREEN set; the auditor ran it (below): `5 passed` |
| A11 | The full code gate, both halves, SOLO, green at the re-merged head, every rc quoted, with the shared-stack restore rows | the gate runs from the slice's worktree beside this audit | **OWED-TO-GATE** (not read, not guessed) |
| A12 | FD closing acts in the FD-1842 form in the PR, by the auditor; the SL-1689 row's dated line; FR-432 read whole | drafts at `~/gi-pricing-plan.local/scratch/aud-sld/` (FD-1661, FD-1816, FD-1211 with FD-1199 following, FD-2018 essay and register row, the roadmap line) | DRAFTED; lands in the audit's own commit with the lead's adoption. The PR number is a marked placeholder until the merge |
| A13 | The LG Audit section with the lead's adoption in the audit's own commit; INDEX regenerated after the closing acts | this section | DRAFTED; the adoption line and the regeneration (`doc-index.py`, then `--check` rc 0) are the lead's turn |

**FD-1661 (frontend limb).** The compose service, Dockerfile, ignore file and nginx conf are in the diff
(`deploy/docker-compose.yml:215-230`, `deploy/frontend.*`). The port is `127.0.0.1:${GIP_WEB_PORT:-5173}:80`, matching the other
published ports (B4). The isolated overlay gains `frontend: ports: !override ["127.0.0.1::80"]`. The image builds from a clean
copy of the commit (`git archive`): the A5 line. No frontend source, backend source or realm is touched (B5, B6, B7 hold: the
`api`, `worker-*`, `migrate`, `scheduler` and `lb` blocks are untouched in `git diff bdad1322...HEAD -- deploy/docker-compose.yml`,
which is one hunk of 17 added lines).

**FD-1816.** `deploy/roll-api.sh`: `old` from `api_ids -a`, `target=$((${#old[@]} + REPLICAS))`, `new` still from running containers,
the success loop removes every `old` one, `cleanup_new` removes only what is not in `old`. DP-D1 (a) as ruled; the R0 read on
`gip-s4-runtime` (`r0.log`: after `docker stop` of one of three, `up -d --no-deps --no-recreate --scale api=4 api` printed the
stopped container and one new one as `Up Less than a second`) confirms the Compose reading that (a) rests on.
**Observation for the lead, not a defect:** because Compose starts the stopped replica when scaling, the replica the failed roll
"leaves" is no longer stopped: it is present (the test asserts `stopped in remaining` and `remaining == before`, by id) and
running. The essay's harm (the roll force-removing a container it did not create) is gone; "leaves it stopped" would need a
`docker stop` in the failure path and is not what FD-1816 asked for. The README line ("a failed roll leaves it in place") says only
what is true.

**FD-1211 and FD-1199.** The proof is a **guard, not a red**: the slice changes nothing in a served process, so the test passes
at the base, and the LG says it was not run there. **The 11:39 run (`fd1211.log`) did not load `lightgbm`** (the image lacked
`libgomp.so.1`); the record is the 12:01 rerun, `fd1211b.log` (`head=637952ae`): `api: 10 SIGTERM stops, problems=[]`,
`worker-compute: 10 SIGTERM stops, problems=[]`, `2 passed in 1100.95s`, rc=0, with the broken-input proof
`worker-compute: 1 SIGTERM stops, problems=['worker-compute round 1: exit code 139 (134 is the FD-1199 abort), not 0']` showing the
check goes red on a planted abort. The test asserts the exit code and the log's absence of `Fatal Python error`, and that every
extension is `PRELOADED`. **Scope the verdict carries:** `api` and `worker-compute` only (the three other worker pools and the
scheduler share the entrypoint and were not stopped here), SIGTERM only (the essay's "worker recycling" path is not exercised).
FD-1211 at the base is "not measurable": no row is invented for it. **FD-1199:** its register row's own event is "if that test never
reproduces, this row is retired as a masked, unexplained abort, with that test's run count as the evidence": 20 stops, 0 aborts.

**FD-2018 (libgomp, MEDIUM, owner WK-674).** Red: `img-red.log` (`head=b516697f`): `1 failed in 28.74s`,
`{'lightgbm': 'OSError: libgomp.so.1: cannot open shared object file: No such file or directory'}`. Fix `637952ae`
(`deploy/Dockerfile`: `apt-get install --no-install-recommends -y libgomp1` in the runtime stage). Green: `img-green.log`
(`head=637952ae`) `1 passed in 94.58s`, rc=0. The test imports `lightgbm`, `xgboost`, `glum` and `interpret`, one process each,
in the BUILT image: the lasting guard. The three other backends passed at the red, so the red is by cause on one backend.

**Re-run by the auditor (own worktree, head `32d33309`):** see "Auditor's runs" below.

**Proposed corrections to this ledger (the executor's text, the lead adopts):**
(1) the A7 line's "tests at head `ddab6d02`" reads "`1a95e467`", the head `a7.log` names, and the claim "no test differs between
them" is checked by `git diff --stat 1a95e467 ddab6d02`; (2) the front matter's `tree:` names `ddab6d02`'s tree and the Build log
runs to `4160fead`: refresh at the mint.

**Open, with owners.** (a) A4, the A5/A6/A7 re-run at the re-merged head, A11: the gate. (b) A8's and item 1's post-mint rc 0:
the mint. (c) FD-1211's two unproved paths (the three other worker pools; recycling, not SIGTERM): accepted at this scope (api, worker-compute, SIGTERM; recycling and the other three pools not exercised), stated in the closing paragraph, not a new finding, because the entrypoint is shared. (d) The A5
criterion's "RFC 9457 body" wording: a plan correction, the planner's.

**Proposed verdict (the lead's to give):** the slice's own scope, as evidenced by records, is MET; the gate's runtime stages
(A4, A5 to A7 at the re-merged head, A11) are OWED-TO-GATE and nothing here is a claim about them.

### Auditor's runs (own worktree `.claude/worktrees/aud-sld`, head `32d33309`)

Each ran through `run-heavy.sh --over-load "2026-11-05 15:37:39 GMT"`, one file per call, after `uv sync --directory <wt> --all-packages --frozen` (rc=0; `sync.log`). Logs under `~/gi-pricing-plan.local/scratch/aud-sld/`, first line `head=32d33309bd3196c2b8e9a227b3a67f316003e5f1`, last line `rc=`.
- `backend/tests/test_deploy_stack.py` (`t1-deploy-stack.log`): `39 passed, 2 warnings in 2.21s`, rc=0.
- `backend/tests/test_bench_deploy_path.py` (`t2-bench.log`): `5 passed, 2 warnings in 0.90s`, rc=0.
Not run: `test_deploy_stack_runtime.py` and `test_deploy_switch_runtime.py` (docker; the gate's).

**Seed clause carried (FR-432).** The service clause of FR-432 (`api`, `worker`, `scheduler`, `frontend`) is met at this merge; the
clause "a working stack with seeded demo data" is not re-evidenced here: LG-1841's "0.7 the seed over the compose ports" is carried
to SL-1913 (the rehearsal slice) and is not claimed by this slice.

**Gate readings against the OWED rows** (`scratch/sld-gate/gate/gate.log`, START head `32d33309`, tree `5e318ca0`; the gate ran before
the re-merge of `9f39bf82`, which brings one docs-only-for-this-slice test file, `backend/tests/test_route_scope_guard.py`, that D
does not touch: no re-gate by the 15:43:06 re-merge rule). A5/A6/A7 at the gate: `fd_stack_runtime` `13 passed, 2 warnings in 2019.88s`
(rc=0), which holds the frontend, failed-roll, NFR-531 roll, image-import and SIGTERM tests by name; `fd_runtime` `1 passed`;
`fd1211_shutdown` `2 passed`. A11: ruff, mypy, import_linter, req_coverage, contracts rc=0; pytest `13 failed, 7142 passed, 27 skipped,
5 xfailed` (baseline 27: the lead's ruling of 2026-11-05 18:11:52 GMT), the 13 failures being exactly the docs-audit set of common
brief item 31 (with `audit_docs` rc=1 on the slice's own working ids), which STANDS for the code on the conditions of item 31; frontend
install/generate:api/lint/type-check/test (`138 passed` files, `919 passed` tests)/build rc=0; demo PASSED in the gate, 1679 s,
dislocation 610 s; peaks: project 2,776 MB, all containers 4,210 MB; shared stack restored from tools-main, keycloak bind under
tools-main. A4: MET, by the lead's read, not the gate's (2026-11-05 about 20:01 GMT, at this tree): `docker compose -f deploy/docker-compose.yml --profile app config --services` lists 12 (postgres, migrate, minio, redis, api, lb, frontend, worker-compute, worker-default, scheduler, worker-io, worker-scoring); with no profile 3 (minio, postgres, redis), unchanged. The gate log itself carries no such line. **Disclosed by line:** two DB windows ran beside pytest (M, and FD 8366); memwatch's blind
span is 18:17:05 to 18:24:07 UTC; the doc-index run beside the demo, about 19:17 to 19:19 UTC, is disclosed, not hidden.


**Mint's non-docs edits, dated 2026-11-05 20:01:11 GMT (executor, at the lead's request).** `git diff 08e9591d 2a24beb9 --stat` lists two non-docs paths, each one line: `deploy/Dockerfile` (gated file) line 12, the mint's comment re-point, a `#` line only, no instruction changed, read by the lead: `-# … does not carry (FD 8353).` / `+# … does not carry (FD-2018).`, no instruction line changed; and `backend/tests/test_deploy_stack_runtime.py` line 380, a docstring: `-"""FD 8353: …` / `+"""FD-2018: …`.

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
- **Checks at `ba6c8bb6` (tree of this worktree; logs `~/gi-pricing-plan.local/scratch/sl-1689d/`):**
  `ruff check .` rc 0 ("All checks passed!", after fixing E501, I001 and two PT018 in the new hunks);
  `ruff format --check` on the three changed test files reports them unformatted, and the same three
  files are unformatted at the base `1f3f67cf` (pre-existing drift, not reformatted here);
  `run-small.sh` on `test_deploy_stack.py` + `test_compose_binds.py`: `47 passed, 2 warnings`, rc 0;
  `run-heavy.sh --light -- env -C <wt> python3 scripts/audit-docs.py`: `FAILED (4)`, all on the
  working ids and the index regeneration the mint owns: check 31 gap between 2006 and 8319; check 32 twice,
  `LG-2017 does not resolve in docs/INDEX.md`; check 39, `docs/INDEX.md is stale`. No other failing line.
- **Maintainer's `docker builder prune`, 2026-11-05 10:18:02 UTC** (lead 30's notice): build cache only. The
  footprint above is from the df readings before it (6.4G to 3.8G); the free-space jump to 12G is this prune.
- **FD-1211 (brief amendment 10:32:58), build window 2, START 2026-11-05 10:49:27 UTC, END 11:39:03 UTC.**
  Test `test_a_served_process_with_its_extensions_loaded_ends_cleanly_on_sigterm` (and its broken-input proof
  `test_the_sigterm_check_reports_a_container_that_aborts_on_stop`) in `backend/tests/test_deploy_stack_runtime.py`;
  `compose()` in `deploy_stack_helpers.py` gained `extra_files`. `api` and `worker-compute` run under a compose
  override whose command preloads FD-1199's extensions (sklearn, pandas, pyarrow, numexpr, glum, xgboost; each
  container prints `PRELOADED …`, asserted), are stopped with `compose stop -t 20` (SIGTERM, python as PID 1) and
  the exit code read from `docker inspect`. **N = 10 per service (DP-211): `api: 10 SIGTERM stops,
  problems=[]`, `worker-compute: 10 SIGTERM stops, problems=[]`; the pair passed with the broken-input proof:
  `2 passed in 1252.79s`, rc 0** (`fd1211.log`; N=`5575547b`, tests at the working tree on `d18564bb`). The broken-input
  proof: a container that aborts in its SIGTERM handler reports `exit code 139 … not 0`. **A guard, not a red:**
  it passes at head, and the slice changes nothing in the served process, so it is green at the base too; it was not
  run at the base. The run is the evidence FD-1199's retirement cites (20 stops, 0 aborts). Reasoning confirmed by
  measurement: as PID 1 uvicorn and celery finalize and exit 0.
- **Findings during window 2.** (1) `lightgbm` cannot be imported in the image: `OSError: libgomp.so.1: cannot
  open shared object file` (`deploy/Dockerfile` is `python:3.12-slim` with no libgomp1); it is left out of the
  preload with a comment, reported to the lead, `deploy/Dockerfile` untouched (outside the Write set). (2) Celery's
  `ready.` line is not printed at the default log level; the test waits for the banner's `[queues]` plus 3 s.
  First run of the worker arm died on that marker (`fd1211-run1-worker-marker.log`, api arm 10 clean stops).
  (3) The first window-2 attempt hit the 580 s tool timeout mid-rounds; its containers were removed with
  `compose down -v` before the rerun.
- **Window 2 end:** `docker ps -a --filter label=com.docker.compose.project=gip-s4-runtime -q | wc -l` = 0; shared
  stack postgres, keycloak, minio, redis `Up 44 hours (healthy)`, keycloak bind source under tools-main;
  `docker image rm gi-pricing-app:5575547b` by exact tag; `df -h /` 7.3G free (88%).
- **libgomp, FD-2018 (ruled (a) by lead 30, brief AMENDMENT 2026-11-05 10:53:50; window 2 extended to ~12:30; the Write set widens by `deploy/Dockerfile`, named here).**
  Red first at `b516697f`: `test_the_built_image_imports_every_declared_model_backend` (lightgbm, xgboost, glum, interpret,
  one `docker run --entrypoint python -c "import <m>"` each) failed `1 failed in 28.74s` with
  `{'lightgbm': 'OSError: libgomp.so.1: cannot open shared object file: No such file or directory'}`
  (`img-red.log`). Fix `637952ae`: `apt-get install --no-install-recommends -y libgomp1` in the `deploy/Dockerfile`
  runtime stage, and lightgbm back in FD-1211's preload. Green on the rebuilt image: `1 passed in 94.58s`
  (`img-green.log`). FD-1211 rerun with lightgbm preloaded, N = 10 each: `api: 10 SIGTERM stops, problems=[]`,
  `worker-compute: 10 SIGTERM stops, problems=[]`, with the broken-input proof: `2 passed in 1100.95s`, rc 0
  (`fd1211b.log`, N=`637952ae`). This supersedes the lightgbm-less run above (20 stops each way, same result).
- **Window 2 end 2026-11-05 12:01:58 UTC:** compose project containers 0; shared stack `Up 45 hours (healthy)`,
  keycloak bind source under tools-main; `gi-pricing-app:637952ae…` removed by exact tag, no gi-pricing image left;
  `df -h /` 4.4G free (93%). No prune.
- Seat slip, recorded: one early call ran a bare `cd /tmp` (no-cd breach); the shell reset and nothing was written.

## PRs

PR #1435.

*(Dated line, 2026-11-06, CR-2071's PR, by the executor, on to-lead "2026-11-06 09:54:01 GMT" (4): item 42 extended — a closed slice's LG status closes with its row; `SL-1689` read `closed` and this ledger `active` after #1435 and the audit, so the status is closed here. The body is not edited.)*
