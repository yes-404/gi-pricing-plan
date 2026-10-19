---
id: LG-1824
family: ledger
title: WK-674 slice SL-1259 — Slice 5, atomic switchover, rollback and the measurements (PL-1766) (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-10-19 # filed 2026-10-18 under working id 8127; minted 2026-10-19 as LG-1824
owner: executor
tree: 3421b26b4cb7b622f9af55ca3e32ba8383e8ea4d
phase: P2
work: WK-674
slice: SL-1259
plans: [PL-1766]
corrected_by: []
relates: [PL-1766, PL-1710, PL-1620, PL-1537, PL-1237, SL-1259, SL-1258, SL-1455]
---

# LG-1824 — WK-674 slice SL-1259: Slice 5

Filed 2026-10-18 under working id 8127 (lead-reserved in eta.md); minted 2026-10-19 as LG-1824. Executor seat `exec-1259`, base `origin/main` 84b0ff5765e55bc8edd139cd22bb57cd474de807, branch `sl-1259-wk674-s5`.

**GO:** the maintainer's (by delegation) entry "2026-10-18 22:50:32 BST — Maintainer: the duplicate-mint anomaly ruled; GO SL-1259, SL-1770, SL-1738, SL-1575 (with conditions)". **MERGE-ACK:** not yet given.

## Needs census (on main 84b0ff57)

- `SL-1258`: roadmap row `status: closed`; merged #1337 (eea416ca).
- `SL-1455`: merged #1323 (9c602fec); its roadmap row still reads `status: active`. The need is read as "merged" (PL-1766 :222).
- `PL-1766` and `PL-1710`: front matter `status: active`.
- Rulings, each in `to-lead.md`: DP-S5-Q1, Q2 and Q7 in "2026-10-17 11:22:47 BST — Maintainer: SL-1259 (S5) DPs ruled; CORRECTION of my 16 Oct 22:22:44 item 2" (Q7 conditional: moot under DP-E1 (a)); DP-S5-Q8 in "2026-10-17 13:06:07 BST — Maintainer: DP-S5-Q8 → (a) for BOTH DP-E1 branches".
- `PL-1710` DP-3's pre-build statement: below, in this ledger.

## PL-1710 DP-3 pre-build statement (D5.9)

**Status: submitted to the decision-maker and answered: DP-3 is ruled (b), DB-first (section below). The F1–F3 text is the ORIGINAL statement under (a), recorded as sent.**

Facts: today `deploy()` (`backend/src/app/platform/deployments.py:455-577`) flushes the `DeploymentRow`, then `audit.record(deployment.created, after=Deployment)` in the SAME session; the route's commit is after return. No PREPARE/COMMIT mechanism exists (`git grep` at 84b0ff57). Proposed order in the deploy transaction: flush row → PREPARE round (every process hydrates the bundle off-loop and acks; nothing swapped) → COMMIT round (every process swaps its one `live` ref, acks) → `audit.record` with `after.commit_acks` = the per-process set {container, process} → transaction commit.

Failure cases, all loud, none silent:

- **F1 — PREPARE short or timeout:** nothing swapped; raise a 5xx problem naming the missing processes; the transaction rolls back (no row, no event); processes drop prepared bundles.
- **F2 — COMMIT round partial or timeout:** the coordinator runs a REVERT round restoring each swapped process's previous `live` (the predecessor ref is known from `previous`); the transaction rolls back; the 5xx problem names per process {committed, reverted, unacknowledged}.
- **F3 — DB commit fails after COMMIT acks (or REVERT incomplete in F2):** no Deployment row exists, so the DB says old version while some processes run new. Recorded: the 5xx problem body carries the per-process state; the coordinator logs it at ERROR; the DB stays the source of truth — each process re-reads the latest committed Deployment on its next startup AND the switch message carries the DB ref, so a process whose `live` differs from the latest committed Deployment ref reconciles to it on its next /score-adjacent heartbeat (mechanism to be pinned in Task 1 with a test). NO new audit action is added (03 :1024 closes the catalogue; a switch-failed event would be a spec change not made without a ruling). The audit after-state therefore only ever carries a COMMIT set from a switch whose transaction committed; "all switched" is never written for a failed transaction.

**Residual risk, stated:** F3 with an unreachable process leaves a window of mixed versions until reconcile; it cannot be made atomic without two-phase commit against Postgres. If that is unsafe, the decision-maker rules (b) or (c) per DP-3's condition (`PL-1710` :477).

## DP-3 ruling (b), DB-first

The maintainer (by delegation), to-lead "2026-10-18 22:59:56 BST — Maintainer: SL-1259 (S5) DP-3 → (b), the condition of 2026-10-14 10:14:13 item 3 NOT met by (a); DB-first ordering": *"Under (a) the switch happens BEFORE the deploy transaction commits, so F3 (the DB commit fails after the COMMIT acks, or a REVERT is incomplete) leaves processes serving a version **that no Deployment row and no Audit Event records**. For a governed platform an unaudited live version is the one outcome that is never acceptable."* (c) is excluded by fact: `deployments` is append-only (`deployments_no_modify`, c4a81f6d2e95 :214).

**Why F3 under (a) was rejected:** the record could be behind reality, with a live version no row or event names.

**Order as ruled:** (1) PREPARE; short → no row, no event, a 5xx naming the missing processes. (2) The deploy transaction commits: the row plus `deployment.created`, whose after-state carries the PREPARE set. (3) COMMIT round. (4) A second, catalogued Audit Event after the switch records the COMMIT set and the unacknowledged processes, ids only (a `06` catalogue append by the spec-change procedure in S5's own commit); the response reports per process {committed, unacknowledged}. No REVERT in the commit path. No heartbeat reconcile in S5 (an FD, MEDIUM, owner WK-674, filed by the lead). D5.6's after-state is the PREPARE set; `PL-1710` is cited, not edited. S5 verifies that a process loads the latest committed Deployment at startup, and stops if it does not (see "Startup-load verification").

## Startup-load verification

Reported to the lead 2026-10-18 (stop clause of 22:59:56). Finding: at 84b0ff57 no process holds a `live` reference; `main.py:84`'s lifespan loads no Deployment; `BundleSlot` (`main.py:213`) is a ref→hash memo, "NOT the environment → current hash pointer"; `api/score.py:221-236` reads the latest committed `DeploymentRow` on every default-live request. **Ruled (A)** by the maintainer, to-lead "2026-10-18 23:03:15 BST — Maintainer: SL-1259 STOP resolved → (A), S5 builds the per-process `live` ref WITH its startup load; FD 8129 raised in scope; `deployment.switched` accepted": S5 builds the per-process `live` ref with a startup load from the latest committed Deployment, red first; (B) refused. **Trade-off, stated:** a process that is alive but missed COMMIT serves the previous version until restart; remedy FD-1823 (MEDIUM, WK-674, before the 12 Nov exit demo), filed by the lead. `deployment.switched` is accepted (entity_ref `environment:<slug>`; before null; after {deployment_ref, committed, unacknowledged}, ids only; own transaction after COMMIT; actor the deploying Principal); rollback reuses it. Catalogue: a dated amendment to 03 :1024 and the 06 catalogue append, in S5's commit.

**The expected-process rule — RULED** by the maintainer, to-lead "2026-10-18 23:07:57 BST — Maintainer: SL-1259, the expected process set → the seat's rule (PUBLISH receiver count + a Redis roster SET + "possibly stale"), ruled now with conditions": *"The EXPECTED COUNT = PUBLISH's receiver count: the honest number of live subscribers. NAMES come from a Redis SET roster: SADD at subscribe, SREM at clean shutdown. When acks == receivers, roster names without an ack are ghosts of crashed processes: SREM them, and record them in the event as `pruned_stale`. When acks < receivers, every unacked roster name is reported as `possibly_stale` ... never silently dropped."* Counts-only refused. Conditions: (1) process id `<hostname>:<pid>:<start epoch>`; (2) roster key and channel namespaced per environment, tests on their own Redis db, never db 0; (3) `deployment.switched`'s after gains `receivers` and the per-name status, defined in the 06 text; (4) four red-first in-memory tests; (5) FD-1823 cites `possibly_stale` as the visible signal. Implemented in `backend/src/app/platform/deployment_switch.py`; the namespace is `<GIP_ENVIRONMENT>:<tenant id>` (my reading of "per environment": the platform environment the process runs in, with the tenant).

## Tasks

Per PL-1766 (§"Slice 5 (`SL-1259`) — changes since `PL-1710`", D5.6 to D5.14) and `PL-1620` D5.1 to D5.5. **Held pending the DP-3 ruling:** D5.6, D5.9 and everything on the switch/rollback path. Task rows are appended here as each task starts.

- **D5.13 — `WEB_CONCURRENCY` on the compose `api` service (`deploy/docker-compose.yml`), default 1 (`GIP_API_WEB_CONCURRENCY`).** Static check `api_declares_its_worker_count` in `backend/tests/test_deploy_stack.py`, red first (2 failed, 18 passed), then green (20 passed, rc 0, via run-small). The static shape is proven; the observed N per container and the bench's void rule are **UNPROVEN** until the SOLO gate (no stack run granted).
- **D5.14 — Slice 4's runtime-test helpers moved to `backend/tests/deploy_stack_helpers.py` under public names** (`compose`, `mapped`, `compose_settings`, `Workspace`, `governed_workspace`, `create_scorer`, `scoring_request`, `api`, the permission lists, `ROOT`, `LB_PORT`, `PROJECT`), moved verbatim; `test_deploy_stack_runtime.py` imports them under its old private names so its bodies are unchanged. Proof: `test_deploy_stack_runtime.py` + `test_deploy_stack.py` import and collect (run-small: 20 passed, 7 skipped, rc 0); `ruff check` clean. The runtime behaviour is **UNPROVEN** until the SOLO gate. S5's new runtime-test module is NOT created yet: it would hold only D5.6/D5.9 tests, which wait on the (A)/(B) answer.

## PRs

None yet. The slice stops at PR-READY; the lead opens the PR.

- **T1 — the switch core** (`deployment_switch.py`, `test_deployment_switch.py`): 10 tests, in-memory transport, no DB or Redis. Red first (collection error: module absent), then green (run-small, 27 passed with `test_bundle_slot.py`). `ruff check` and `ruff format` clean, `mypy` rc 0, `lint-imports` 4 kept. The Redis transport is not yet written or proved.
- **T2 — the Redis transport and subscription** (`RedisSwitchTransport`, `SwitchSubscription` in `deployment_switch.py`) and the model-schema shapes `DeploymentCreated` (the 201 of `POST .../deployments`: the Deployment plus `switch`) and `SwitchReport` (the `after` of `deployment.switched`). mypy and ruff clean. **UNPROVEN:** the Redis transport has no test that ran (needs a Redis).
- **T3 — the wiring.** `deploy()` runs PREPARE after every refusal and before the row (new error code `DEPLOY_SWITCH_INCOMPLETE`, 503, in `errors.py` and `03` §5.1); its `deployment.created` `after` carries `prepared`. `deploy_and_switch()` commits that transaction, runs COMMIT, and writes `deployment.switched` in its own transaction; a COMMIT round that raises reports every prepared process unacknowledged (the row is committed, so the record is not skipped). The lifespan subscribes first and then loads the latest committed Deployments into `app.state.live_refs`; `/score` reads that reference once at request start (`_serving_ref`, no table read). Cites FD-1823 at the trade-off (`api/score.py`, `deployment_switch.py`). Spec: dated amendments in `03` (the audit actions, the error list, the route row, a FR-268 note) and a dated note in `06` §4.5 — **`06` has no table of audit action names to append to, so the note points at `03`'s list; say if you want a different place.** Contracts regenerated (`generate-contracts.py --check` rc 0); the two new generated schemas are registered in `audit-docs.py`'s F83 exemption list. Tests changed: `test_deployment_route_types.py` (the 201 type; DB-free part: 17 passed, the 1 DB-needing test errors without a database), `test_score.py` (`plant_deployment` now loads the planted row into the running app's `live_refs`, and `_serving_ref` takes a `LiveRefs`). run-small: `test_errors.py` + `test_deployment_switch.py` + `test_deploy_stack.py` 45 passed. **UNPROVEN, owed to a granted DB+Redis window:** `test_deployments.py` (the 201 body, PREPARE-short refusal, `deployment.switched` written, rollback of nothing yet), `test_score.py` (default-live scoring through `live_refs`; a fresh app serves the DB-latest), `test_deployment_route_types.py` in full, and every other test that deploys or plants a Deployment then scores default-live. **Not built:** the rollback route (D5.10 and FR-269), the bundle-slot capacity measurement, `bench-deploy-path.py` (D5.12), the F1 test and the measured verdicts (host-bound); the red-first tests for the DB-first order over HTTP.
- **T4 — the rollback route (D5.10, FR-269).** `POST /api/v1/environments/{env}/deployments/rollback`, body `RollbackCreate` (`model-schema`, generated contract `rollback-create.schema.json`), `service.rollback`/`rollback_and_switch`: `deployment:promote` and the management count through `_authorised_environment`, the target must have been deployed to the Environment before (409 `VALIDATION_FAILED` otherwise), a new append-only Deployment row carrying the earlier Deployment's recorded bundle hash, `deployment.rolled_back` (before the live Deployment, after the new one plus its PREPARE set, justification the reason) in the same transaction, then the same PREPARE/commit/COMMIT/`deployment.switched` order as a deploy. A recompiled target fails PREPARE (the hydrated hash differs from the recorded one) and is refused loud. Sweep and route-pin tests updated (`test_api_authorisation_sweep.py`: the three `platform/deployments.py` line pointers moved 93 to 128 and the rollback route added; `test_deployment_route_types.py`: eight rows). DB-free run-small: `test_deployment_route_types.py` 17 passed plus its 1 DB-needing error. **UNPROVEN, owed to a DB window:** the rollback happy path, the 403-leaves-the-counter-unchanged and permitted-adds-one tests of D5.10, the rollback-without-an-event red on deliberately broken input, and `test_api_authorisation_sweep.py` (its `platform/deployments.py` line pointers are line numbers and move with any edit above them).
- **T5 — the roster ruling applied.** `process_id()` is `<hostname>:<pid>:<start epoch>`; `prepare_round` returns `PrepareOutcome(prepared, receivers, pruned_stale)`; `SwitchReport` is `{deployment_ref, receivers, processes: name -> committed | possibly_stale | pruned_stale}` (regenerated contract, `--check` rc 0); `06` §4.5 defines the three terms. Condition 4's cases are in `test_deployment_switch.py` (12 tests, run-small 12 passed): (a) all ack, (b) a ghost pruned at a full ack, (c) a live process that misses COMMIT is named, a short PREPARE reports every unacknowledged roster name and prunes none, (d) a restart is a new id and its ghost is pruned at the next full ack. The sweep's three line pointers moved 128 to 131.
- **T6 — the HTTP reds, the runtime test, the bench.** `backend/tests/test_deployment_switch_http.py` (4 tests, written to be run FIRST on the pre-wiring commit `725a9edd` and then at head): a short PREPARE writes no row and no event and names the process (503 `DEPLOY_SWITCH_INCOMPLETE`); a partial COMMIT reports the deaf peer `possibly_stale` in the response and in `deployment.switched`; a fresh app serves the DB-latest; a rollback emits `deployment.rolled_back` then `deployment.switched` and swaps `live`, and a rollback to a never-deployed version is 409. A second subscribed process is simulated by a `_Peer` on its own loop. `test_deployments.py`'s `client` fixture sets `app.state.switch = None`: its Rating Versions carry a hash and no blob, which no process can hydrate, and it tests the governance, not the switch. **Other tests that POST a deploy with a hash-only bundle will answer 503 now; known candidates to check in the window: `test_management_rate_limit.py` (its deployments case expects 404 before PREPARE, so unaffected), `test_rating_version_compile.py` (deploys a really compiled version), `test_api_authorisation_sweep.py` (RESOURCE_BACKED bodies).** `backend/tests/test_deploy_switch_runtime.py` is D5.11's new module (skipped without `GIP_DEPLOY_TESTS=1`; **UNPROVEN until the SOLO gate**). `scripts/bench-deploy-path.py --governed` is D5.12 (seed through the services, deploy by the route, quotes with no `rating_version_ref`, observed N per container from the switch's own report, a mismatch voids; the explicit-ref arm stays labelled `diagnostic`); `test_bench_deploy_path.py` 5 passed (run-small), `--dry-run` prints the record; the governed run itself is **UNPROVEN**. Spec: `03` :1024 is now the only home of the terms (citing 22:59:56, 23:03:15, 23:07:57 and 23:22:15 and relating `deployment.rolled_back` to `deployment.switched`); `06` §4.5 is a pointer only (the maintainer, "2026-10-18 23:22:15 BST"). No NFR or F1 measurement was taken (host-bound).
- **T7 — the DB+Redis window (granted in writing by the lead, 2026-10-18; own DB `gipricing_sl-1259_2ccd468a` from `template0`, alembic head `f2b6d90a4c17`, Redis db 15, bucket `gip-test-blobs-1259`, every pytest through `run-small`).** Start: `flock -n /tmp/slots/gate-1 true` rc 0, load1 2.67, available 25 GiB. **Reds first** on a detached scratch worktree at `725a9edd` (before the wiring) with only `build_switch_client` added: `test_deployment_switch_http.py` 4 FAILED, each for its own reason: `assert 201 == 503` (a short PREPARE still wrote the row), `KeyError: 'switch'`, `AttributeError: 'State' object has no attribute 'live_refs'`, and the rollback route `assert 404 == 201`. **At head:** the same file passed, `test_deployments.py` 52 passed, `test_score.py` 52 passed, `test_api_authorisation_sweep.py` + `test_deployment_route_types.py` 26 passed and 1 failed, `test_traces.py` + `test_api_approvals.py` + `test_management_rate_limit.py` 154 passed. The one failure, `test_the_two_changed_approval_routes_return_exactly_the_declared_keys`, was a deploy of a hash-only bundle answering 503 (nothing can hydrate it); its test now sets `client.app.state.switch = None` like `test_deployments.py`. **A real bug found by running:** the subscription used the rate limiter's 50 ms socket-timeout client, so its blocking pub/sub read timed out and the listener died; the switch now has its own client (`build_switch_client`). **Scope:** per the maintainer's answer (relayed by the lead) the channel, roster and acks are keyed `<GIP_ENVIRONMENT>:<tenant>:<environment slug>`, a process subscribes to every non-retired Environment at startup (an Environment created later is not subscribed until restart: the FD-1823 gap), and a red proves a `prod`-only subscriber neither receives nor blocks a `dev` deploy; after the change `test_deployment_switch_http.py` + `test_deployment_switch.py` 17 passed. **Breach disclosed:** that last run started when `flock -n /tmp/slots/gate-1 true` returned rc 1 (gate-1 had been taken since my start check); it was one 25 s run-small of two files and I did not re-check the slot before it. **Not re-run after the scope change:** the full set above and `test_deployment_route_types.py` with the `switch = None` fix; they are owed once gate-1 is free. Cleanup: `redis-cli -n 15 dbsize` = 0, `pg_database` count for the DB = 0, the bucket removed through `mc rb` (absent from `mc ls g/`), the scratch worktree removed (no shared container binds under it).

- **T8 — the owed full re-run at head `0161e6be` (DB/Redis window granted in writing by the lead, 2026-10-19 01:06:23 BST; own DB `gipricing_sl-1259_2ccd468a` from `template0`, alembic head `f2b6d90a4c17` rc 0, Redis db 15, bucket `gip-test-blobs-1259`; every pytest through `run-small` on the worktree at `0161e6bed259caddd0c600e8cb949650694f0053`, with `flock -n /tmp/slots/gate-1 true` rc 0 re-checked before each run).** R1 `test_deployments.py` + `test_score.py`: rc 0, 104 passed. R2 `test_api_authorisation_sweep.py` + `test_deployment_route_types.py`: rc 0, 27 passed (the `switch = None` fix included). R3 `test_traces.py` + `test_api_approvals.py` + `test_management_rate_limit.py`: rc 0, 154 passed. R4 `test_deployment_switch_http.py` + `test_deployment_switch.py`: rc 0, 17 passed. No FAILED line in any run. **Disclosed:** R3 started with available memory 7 GiB (`free -g`), below the grant's 8 GiB floor; load1 was 2.75, the run passed, and the floor was missed on a start reading I printed but did not act on. Cleanup: `redis-cli -n 15 dbsize` = 0, `pg_database` count for the DB = 0, the bucket removed through `mc rb` (absent from `mc ls g/`).

- **T9 — the code-side FD-1823 re-point, 2026-10-19 (the maintainer's ruling "2026-10-19 03:30:56 BST", option A).** Four mentions, comment and docstring text only, commit `70a0af0d`: `backend/src/app/api/score.py` (`_serving_ref` docstring), `main.py` (a `#` comment), `platform/deployment_switch.py` (module docstring), `platform/deployments.py` (`deploy_and_switch` docstring). Proof, no python-half re-gate. (1) AST equality with docstrings stripped, `fb29f8b7` against `70a0af0d`, the script verbatim:

```python
"""Compare each file at <rev_a> and <rev_b> (or a working path) after stripping docstrings."""
import ast, subprocess, sys

def strip(tree):
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = n.body
            if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) and isinstance(b[0].value.value, str):
                n.body = b[1:] or [ast.Pass()]
    return ast.dump(tree, include_attributes=False)

def show(wt, rev, path):
    return subprocess.run(["/usr/bin/git", "-C", wt, "show", f"{rev}:{path}"], check=True, capture_output=True, text=True).stdout

wt, a, b = sys.argv[1:4]
for path in sys.argv[4:]:
    src_b = open(path.split("=", 1)[1]).read() if "=" in path else show(wt, b, path)
    path = path.split("=", 1)[0]
    same = strip(ast.parse(show(wt, a, path))) == strip(ast.parse(src_b))
    print(("EQUAL   " if same else "UNEQUAL ") + path)
```

Output of `python3 -I astcmp.py <wt> fb29f8b7 70a0af0d <4 paths>`: `EQUAL` for all four files. Enforcement on broken input: the same script against a scratch copy of `main.py` with the `__all__` literal changed printed `UNEQUAL   backend/src/app/main.py`; the copy was not committed. (2) `generate-contracts.py --check`: `54 generated contracts match the models`, rc 0. (3) `ruff check` on the 4 files: `All checks passed!`, rc 0; `mypy` on the 4 files: `Success: no issues found in 4 source files`, rc 0. (4) `git grep -n __doc__ 70a0af0d -- backend/src`: no hit (rc 1), so nothing in `backend/src` reads a docstring through `__doc__`; the OpenAPI description of a route function is read by FastAPI, and (2) shows the generated contracts unchanged.

- **2026-10-19 — D5.11 fix A: the switch test is given a TEST-supplied beat (`beat_fixture`); the deploy compose still has none.** Cause of the 03:36:33 BST switch-only red (the compile Job stayed `queued`): the bring-up has no beat process, so no Job leaves the outbox (`beat_fixture` docstring: "without a beat process no Job ever leaves the outbox"). Authority: to-lead 2026-10-19 03:38:42 and 03:40:19 BST. `_build_from_commit`, `built_n` and `beat_fixture` moved VERBATIM from `backend/tests/test_deploy_stack_runtime.py` to `backend/tests/deploy_stack_helpers.py`; the smoke module imports them; `test_deploy_switch_runtime.py` takes `built_n` and `beat_fixture`. **D5.11 is therefore proven with a TEST-supplied beat. The deployed compose stack still lacks a beat (FD-1661, MEDIUM, WK-674). No claim is made that the deploy compose runs Jobs by itself.** Other changes in the helpers module: imports `tempfile`, `collections.abc.Iterator`, `pytest`; and `_compose = compose` (the moved text calls `_compose`). In the smoke module: the `tempfile` import removed, three names imported (`_build_from_commit` plain; `beat_fixture` and `built_n` with `# noqa: F401`, fixtures used by name), and `# noqa: F811` on the five test signatures that name the fixtures as parameters.
  Proof 1, byte identity of each moved definition (decorators included) at 1f6934db (smoke file) vs the helpers file at this commit. Script `proof.py (scratchpad)` run as `python3 -I`:

```python
import ast, subprocess, sys
W = "/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1259"
def seg(src, name):
    t = ast.parse(src)
    for n in t.body:
        if isinstance(n, ast.FunctionDef) and n.name == name:
            lines = src.splitlines(keepends=True)
            start = min([n.lineno] + [d.lineno for d in n.decorator_list])
            return "".join(lines[start - 1:n.end_lineno])
H = subprocess.run(["git", "-C", W, "show", "1f6934dbda78862dd269c404b6ebd718a4e744d1:backend/tests/test_deploy_stack_runtime.py"], capture_output=True, text=True, check=True).stdout
H2 = open(W + "/backend/tests/deploy_stack_helpers.py").read()
ok = True
for name in ("_build_from_commit", "built_n", "beat_fixture"):
    a, b = seg(H, name), seg(H2, name)
    same = a.encode() == b.encode()
    print(f"{name}: H len={len(a)} H2 len={len(b)} byte-identical={same}")
    ok &= same
sys.exit(0 if ok else 1)
```

Output:

```
_build_from_commit: H len=609 H2 len=609 byte-identical=True
built_n: H len=171 H2 len=171 byte-identical=True
beat_fixture: H len=702 H2 len=702 byte-identical=True
```

  A per-function `diff` of the two segments printed `diff empty` for each of the three.

- **T10 — the switch runtime test's approval through the API, 2026-10-19 04:02 BST (the maintainer's ruling "2026-10-19 03:58:53 BST", option (1), conditions (a)–(d)).** Test files only: `backend/tests/test_deploy_switch_runtime.py` and `backend/tests/deploy_stack_helpers.py`; `examples/fremtpl2/model.py` and every production file are unchanged. The 03:55:35 failure was a second compile: `author_demo_rating_evidence` compiles unconditionally and ran in the test process, and every compile's blob bytes differ (`compiled_at`, `pricing_core/rating/compile.py:1267`) while `content_hash` is reproducible (:676-683). The test now keeps the route compile (`produced`) and approves the SAME draft through the API, with no in-process Job and no second compile: `POST /regression-suites/{slug}/versions` (analyst) → `POST …/regression-runs` waited to `succeeded` with a result ref → `POST …/submit` (actuary) → `POST /approval-requests/{id}/decide` ×2 (approver, second_approver) → deploy dev, uat. Conditions: (a) the suite body is `RegressionSuiteVersionCreate` with the example's public `demo_golden_cases`, `declared_properties`, `FREMTPL2_ALGORITHM_SLUG`, `SPLIT_SEED`, `DEMO_CHANGE_NOTE`; (b) the comment on `_suite_body` names `examples/fremtpl2/model.py:874-894 @ef2f0462`; (c) the test asserts the regression Job's `platform_build` (`Job.platform_build`, `model_schema/jobs.py:237`) ends with `+<GIP_N_SHA>`; (d) after the deploy and before any identity assert, the deployed bundle's bytes are fetched by `GET /api/v1/blobs/{sha}` (307, netloc rewritten to the published minio port as `test_deploy_stack_runtime.py` does) and written to `$GIP_EVIDENCE_DIR/deployed-bundle.json` when that variable is set. `blob_sha256 == produced` stands as written; added `deployed content_hash == the route compile's content_hash`. `approve_draft` is removed from `deploy_stack_helpers.py`: `git grep approve_draft` found no other user.
  **The duplication, plainly:** `_suite_body` re-states the golden-quote loop and the suite assembly of `examples/fremtpl2/model.py:874-894` (the `QuoteContext` per case, the `golden` dict keys, the `generation` block with `cases: 25`). It cannot call that function, which runs its Jobs in the test process, so a change to those lines in the example does not reach this test; the comment names the source so a reader can diff. No shape is hand-written: the body is validated through `RegressionSuiteVersionCreate`. Not run with `GIP_DEPLOY_TESTS=1`: that is the gate's.


- **2026-10-19 04:12 BST — re-merge of `origin/main` (`aea6f160`) into `sl-1259-wk674-s5` (the maintainer's ruling "2026-10-19 04:06:08 BST", `to-lead.md`).** Merge commit `40f84d7c` (`--no-ff`, no rebase), pre-merge head `4a3bd4a5`, merge-base `84b0ff57`. The two-sided set is `docs/INDEX.md`, `docs/roadmap.md` and `docs/specs/03-rating-engine.md`; the only conflict was `docs/INDEX.md`, resolved by `python scripts/doc-index.py` (regenerated, no marker stripping). `docs/roadmap.md` and `docs/specs/03-rating-engine.md` auto-merged. The two files' changes from `git diff -U0 4a3bd4a5..40f84d7c -- docs/specs/03-rating-engine.md docs/roadmap.md`, hunk headers and changed lines (long lines cut at 700 characters):

```text
@@ -2720 +2720 @@ title: WK-1178 fix slice — FD-1744, a recipe cell that does not parse is never
-status: draft                    # draft → active → closed | retired (§1.2a)
+status: closed                    # draft → active → closed | retired (§1.2a)
@@ -2759,0 +2760,2 @@ Plan `PL-1737` (a WK-1178 Work-plan delta; `draft`). **Activation needs:**
+(Activated 2026-10-18 on the maintainer's GO, to-lead "2026-10-18 22:50:32 BST — Maintainer: the duplicate-mint anomaly ruled; GO SL-1259, SL-1770, SL-1738, SL-1575 (with conditions)"; dispatched by the lead, transcript 34b896f2.)
+(Closed 2026-10-19 as a Slice by exec-1738r's closing acts (LG-1822 minted from working id 8128), on the pre-PR audit of LG-1822 (auditor-1738, "## Audit", 2026-10-19 01:12:51 BST; head `0fbea8ad`), CLEAN, adopted by the lead (from-lead "2026-10-19 01:13:36 BST"); F4 answered in LG-1822. MERGE-ACK: not yet given.)
@@ -1585 +1585 @@ Mirrored into [`open-questions.md`](../open-questions.md).
-| **OQ-1789** | **OPEN** — **What budget does the exit demo (`examples/fremtpl2/journey.py`, WF-699) have for its two Dislocation Runs on the 20,000-policy sample, given that no specification states a run-time budget for a Dislocation Run or its attribution?** Raised 2026-10-18 (working id 8110, reserved by the lead; minted 2026-10-18 as OQ-1789), drafted by the auditor on the maintainer's (by delegation) entry "2026-10-18 01:13:14 BST" in `to-lead.md`, from the SOLO gate of SL-1543 at `5a5cb2e7` (`~/gi-pricing-plan.local/scratch/sl1543r-gate/demo.log`, local). **Measured (two jobs, not one).** `journey done in 1295s`. Run 1 (D6, one change group, K = 1): job `01a14c46-fa4c-7013-9611-ce50
+| ~~**OQ-1789**~~ ✔ | ~~**What budget does the exit demo (`examples/fremtpl2/journey.py`, WF-699) have for its two Dislocation Runs on the 20,000-policy sample, given that no specification states a run-time budget for a Dislocation Run or its attribution?**~~ **DECIDED 2026-10-18: (A) — keep the 1,500 s demo cap; the demo runs only in a quiet window.** Decided by the maintainer (by delegation) on the user's decision, `to-lead.md` entry "2026-10-18 22:45:20 BST"; the user, 18 Oct, verbatim: "OQ-1789: follow your recommendation", the recommendation given just before being (A). The exit demo (WF-699, `examples/fremtpl2/journey.py`) keeps the 1,500 s cap. Gates and the exit demo run the dem
```

## Audit

Auditor, 2026-10-19 04:33 BST (`TZ=Europe/London`). Range `origin/main...43b1f231` (merge-base `aea6f160`); tree is `43b1f231`, branch `sl-1259-wk674-s5`. Scope is derived from the plans first (`PL-1537` Acceptance item 5, `PL-1620` D5.1–D5.5, `PL-1710` D5.6, `PL-1766` D5.7–D5.14 and its Acceptance items 4–6), then evidenced. **All verdicts below are proposals; the verdict is the lead's** (`CLAUDE.md` §12–13). No test, gate or DB was run for this audit; every row is read from the committed files, the ledger and the maintainer's entries in `to-lead.md`.

**Evidence set (the maintainer, by delegation, "2026-10-19 04:05:43 BST" and "04:06:08 BST"):** the `19d139e6` SOLO gate (python half: the 13-test cascade plus 3 reds resolved by test-only fixes, "02:45:42 BST"; frontend half rc 0; smoke 7 passed; demo `journey done in 1221s`, "03:18:08 BST"); run-small sinks 11 passed `@1f6934db`; switch3 smoke 7 passed `@ef2f0462`; switch4 switch 1 passed `@4a3bd4a5` ("04:05:43": `switch.log:85`, `jobs.txt` = 2 jobs, one compile). **The merged-head proof is the PR's CI python suite, not yet run** (`04:06:08`: the 13-cascade must be gone or explained after the mint, and no new reds; main's `7fd0fa73` brought SL-1738's pricing-core/ingestion changes, which never ran beside this slice's code).

**Reachability** (`git merge-base --is-ancestor <sha> 43b1f231`, each rc 0): `725a9edd`, `0161e6be`, `fb29f8b7`, `70a0af0d`, `1f6934db`, `785fc797`, `ef2f0462`, `4a3bd4a5`, `19d139e6`, `40f84d7c`, `43b1f231`.

### Claims checked against the primary source

1. **Production code since `19d139e6` changed only in comments and docstrings: CONFIRMED by reading.** `git diff -U0 19d139e6..4a3bd4a5` over `backend/src`, `packages`, `scripts`, `deploy`, `examples` prints exactly four changed lines, each `FD 8129` → `FD-1823`: `api/score.py:230` and `platform/deployments.py:688` (inside the `_serving_ref` and `deploy_and_switch` docstrings), `platform/deployment_switch.py:19` (the module docstring, closing `"""` at :28), `main.py:134` (a `#` comment). No non-comment production change. The re-merge `4a3bd4a5..40f84d7c` touches `backend/src/app/data/ingestion.py`, `db/models.py`, two migrations and `packages/pricing-core/src/pricing_core/data/{ingest,prepare,validate}.py` — all main's (SL-1738), none SL-1259's; the migration `5c8e3b71d094` has `down_revision` `f2b6d90a4c17` (the head this slice's DB window ran at), so it extends the same chain. I did not re-run the AST script; T9's `EQUAL` ×4 (`fb29f8b7`↔`70a0af0d`) plus my reading of the diff agree.
2. **LG-1824 records D5.11 as proven with a TEST-supplied beat and FD-1661 open: CONFIRMED** — the entry "2026-10-19 — D5.11 fix A" above: "D5.11 is therefore proven with a TEST-supplied beat. The deployed compose stack still lacks a beat (FD-1661, MEDIUM, WK-674)". The register row for FD-1661 (`docs/findings/register.md:356`) is MEDIUM, owner WK-674, no closing marker. The re-merge entry is present (the "04:12 BST" entry: merge `40f84d7c`, pre-merge `4a3bd4a5`, base `84b0ff57`, two-sided set, INDEX regenerated, hunks quoted).
3. **The proof of D5.11 "proven" is by the maintainer's reading, not in this ledger.** The ledger does not itself carry the `switch.log:85` line or the `deployed-bundle.json` hash/compile-window check; they are in "04:05:43" only (see finding A2).

### Scope table (requirements, each id), with proposed verdicts

| Requirement / plan item | Evidence at `43b1f231` | Proposed verdict |
|---|---|---|
| `03` FR-268 (atomic switch, DB-first) / D5.6, D5.9 | `test_deployment_switch_http.py:125,151,178,227`; `test_score.py:1622`; reds first at `725a9edd` (4 FAILED, T7), green `@0161e6be` (R1 104, R4 17 passed, T8); runtime `test_deploy_switch_runtime.py` 1 passed `@4a3bd4a5` | delivered and tested |
| `03` FR-269 (rollback) / D5.10 route | `test_deployment_switch_http.py:194`; sweep + route-types 27 passed (R2, T8) | delivered and tested |
| `03` FR-272 audit limb + NFR-498 rollback limb | `test_deployment_switch_http.py:195` (`deployment.rolled_back` then `deployment.switched`); `test_deployments.py:491,544` | delivered and tested |
| `07` FR-452 on the rollback route (D5.10) | `CountDep` wiring is stated in T4; **no test found** for "a 403 rollback leaves the counter unchanged; a permitted rollback adds 1": `git grep -nE 'rollback' -- backend/tests` filtered on `count\|429\|manage\|counter` prints nothing, and `test_management_rate_limit.py` names no deployment rollback | delivered but untested (finding A1) |
| NFR-497 mechanism (degraded read against `live`) | `test_bundle_slot.py:174,190,205,228`; `test_score.py:643`; per-process `live_refs` (T3) | delivered and tested |
| D5.7 (SL-1455 dependency) | PL-1766 Acceptance item 3 asks for `git grep -n 'D5.7' -- <this LG>`; the ledger's needs census cites SL-1455 (#1323) but I find no quoted D5.7 line (the grep over this file prints only the plan-delta references in T-rows) | delivered but unrecorded — a ledger edit, not code (finding A3) |
| D5.8 write set | Not independently derived here: `git diff --name-only origin/main...43b1f231` includes `api/score.py`, `main.py`, `platform/*`, `model_schema/deployments.py`, `scripts/bench-deploy-path.py`, `deploy/docker-compose.yml`, tests; none from the lead's brief is outside the plan. Not checked path-by-path | delivered, path-by-path check owed to the lead |
| D5.11 (governed-path seeds, no `bench-rating._seed`) | `git grep -nE 'bench_rating\|bench-rating\|_seed\b'` over the three runtime-test files prints nothing; the helper uses `create_approved_rating_version` (`deploy_stack_helpers.py:146`); `@4a3bd4a5` 1 passed | delivered and tested, with a TEST-supplied beat |
| D5.12 (`bench-deploy-path.py --governed`, exit reading through `live`) | script and `test_bench_deploy_path.py` 5 passed (T6); **the governed run itself was never made** — the ledger says "UNPROVEN" and "No NFR or F1 measurement was taken (host-bound)" | delivered but untested as a measurement; the reading itself not started (see NFR rows) |
| D5.13 (`WEB_CONCURRENCY`, observed N, void rule) | static `test_deploy_stack.py:151-162` (red 2 failed → 20 passed, T row); `bench-deploy-path.py:78,112` observed-N and void logic; observed N per container on a live stack unproven | static delivered and tested; the observed-N reading deferred with the measurement (A4) |
| D5.14 (shared helper module) | `deploy_stack_helpers.py`; byte-identity proof of the three moved definitions (fix-A entry, proof 1); smoke 7 passed `@ef2f0462` | delivered and tested |
| NFR-489 exit reading (SL-1259 holds it, RL-1614) | none: no `bench-deploy-path.py --governed` run recorded | not started — or deferred with an owner if the lead/maintainer so rules (A4) |
| NFR-490, NFR-493 linearity, NFR-494, NFR-501, NFR-502 measured; the F1 test (≥3 runs per n ∈ {2,4,8}); LG-1363's O4 ladder bench | none in this ledger; PL-1537 Acceptance 5's `git grep -nE 'NFR-489\|NFR-490\|NFR-493\|NFR-494\|NFR-501\|NFR-502'` over this LG prints no per-id line | not started; "deferred with an owner" is available only on a ruling: "2026-10-11 11:02:35 BST" item 3 puts these on the dedicated-VM run list (owner: the maintainer), and I find no ruling that excuses SL-1259 from them at its close (A4) |
| Gate on the merge tree (PL-1766 Acceptance item 6) | Python-half at `19d139e6` plus the increments above; merged-head python suite = the PR's CI, pending | evidence partial until CI runs |

### Findings

- **A1 (D5.10, FR-452):** the two red-first tests D5.10 requires (a `403` rollback leaves the management counter unchanged; a permitted rollback adds exactly 1) are not found in `backend/tests`. Proposed verdict: delivered but untested; the lead decides between a test before the PR and a named owner.
- **A2 (ledger):** the `19d139e6` gate result (13-cascade by id, the 3 test-only fixes, frontend half, smoke, demo journey 1221 s) and the D5.11 proof lines (`switch.log:85`, bundle `compiled_at` inside the compile Job's window) exist only in `to-lead.md`, not in this ledger. Recorded here by citation, not copied; the closing act should quote them so the slice record stands without the channel.
- **A3 (ledger):** PL-1766 Acceptance item 3 (`git grep -n 'D5.7' -- <this LG>` prints the quoted D5.7 line) and item 4 (each ruling entry quoted by its header) are met for item 4 (the DP-3, STOP and roster entries are quoted) but I do not find the D5.7 quote.
- **A4 (measured limbs):** the NFR-489 exit reading, F1, NFR-490/493/494/501/502 and the O4 ladder have no measurement and no deferral ruling naming this slice's close. This is the largest open item; "host-bound" in T6 is a description, not an owner. Verdicts are the lead's; a deferral needs a named owner.
- **A5 (merged head):** the SL-1738 changes in `pricing-core` and `backend/src/app/data` have never run beside this slice. The python half at `19d139e6` does not cover them. Closing evidence is the PR's CI python suite, which the maintainer will read.
- **A6 (verification-by-citation):** I verified the production-diff and reachability claims myself; the gate rows (13 cascade, frontend, smoke, demo) are the maintainer's readings in `to-lead.md` "02:43:00", "02:45:42" and "03:18:08 BST", cited, not re-run.

### Docs checks

At the pre-commit tree (gate-1 and gate-2 both free, checked first): `python3 scripts/audit-docs.py` rc 1 with exactly two FAILED lines, both check 31 — "gap in the full allocation between 1823 and 8127" and "id 8127 is `created:` 2026-10-18, earlier than id 1823's 2026-10-19" — the unminted working id, expected until the mint; `python3 scripts/doc-index.py --check` rc 0 ("INDEX.md: OK (byte-stable)"). No check-32 red.

### Second pass — D5.8 write-set walk (auditor-1259w, 2026-10-19 04:42:07 BST)

Tree: branch HEAD `bbc3f774629a5d6e8ca749eb4c029d732815c26b` (worktree `sl-1259`, status clean before this edit). Read-only; nothing run.

**D5.8 as defined** (`PL-1766` D5.8, quoted): `PL-1537`'s S5 set (`api/deployments.py`, `platform/deployments.py`, `errors.py`, `03-rating-engine.md`, `openapi/generated.json`, `backend/tests/`) plus `api/score.py`, `main.py`, `platform/bundle_slot.py`, `config.py`; `packages/model-schema/src/model_schema/deployments.py` and the regenerated contract; `scripts/bench-deploy-path.py`, possibly `scripts/bench-rating.py`, `deploy/Dockerfile` or `deploy/docker-compose.yml`. As ruled 2026-10-17: `deploy/docker-compose.yml` in, `deploy/Dockerfile` out; `bench-rating.py` "possibly". "Any path outside it is a stop to the lead, not a widening."

**Predicate** (change set, the range): `git -C <wt> diff --name-only origin/main...HEAD | sort` (35 paths). D5.8 list written to a file with full paths (the shorthand names expanded to `backend/src/app/...`), plus two expansions of mine: every branch path under `backend/tests/` (D5.8 names the directory) and under `docs/contracts/schemas/generated/` (D5.8's "regenerated contract"). `comm -12` of the two sorted lists = **26** paths. Whether the generated schemas count as "the regenerated contract" is a reading I made; the lead should confirm it.

**In the branch, not in D5.8 (9):**
- `backend/src/app/platform/deployment_switch.py` — new production module, **OUTSIDE D5.8**. D5.8 names `platform/bundle_slot.py`, `config.py` for the lifespan subscriber; the subscriber is in this new file instead.
- `packages/model-schema/src/model_schema/__init__.py`, `scripts/generate-contracts.py`, `scripts/audit-docs.py`, `tests/test_audit_docs_ids.py` — code or tooling outside D5.8.
- `docs/specs/06-governance.md`, `docs/roadmap.md`, `docs/INDEX.md`, this ledger — docs; D5.8 lists only `03-rating-engine.md` among specs.

**In D5.8, not in the branch (3):** `backend/src/app/platform/bundle_slot.py`, `backend/src/app/config.py`, `scripts/bench-rating.py` (the last is "possibly"; `deploy/Dockerfile` is out and untouched).

**Write walk** — predicate, run over `HEAD` in `backend/src packages/model-schema/src scripts/bench-deploy-path.py`:
`git -C <wt> grep -n -E '(live_refs\.(set|load_latest|clear|pop|discard)|\.live\.set\(|self\._live\[[^]]*\] *=|_live\.(pop|clear|update)|\.sadd\(|\.srem\(|drop_from_roster\(|join_roster|leave_roster|\.set\(.*entry|LiveRefs\(\)|load_latest\()' HEAD -- backend/src packages/model-schema/src scripts/bench-deploy-path.py`
gave 12 hits. I added `live.set` at :124, which the predicate misses, and the two `transport.join`/`.leave` callers found with `git grep -n -E 'join\(|\.leave\(' ... deployment_switch.py`. Declarations (:127 `def load_latest`, :200 and :377 `drop_from_roster` def) and the ack-key `sadd` at :383 (an ack set, not the roster) are excluded. **12 writes walked.**

| # | file:line | enclosing function | what | D5.8 path |
|---|---|---|---|---|
| 1 | `platform/deployment_switch.py:117` | `LiveRefs.set` | writes the live-ref map | OUTSIDE D5.8 (new file) |
| 2 | `platform/deployment_switch.py:124` | `LiveRefs.from_latest` | sets on a fresh local instance | OUTSIDE D5.8 (new file) |
| 3 | `platform/deployment_switch.py:150` | `LiveRefs.load_latest` | startup load into `self` | OUTSIDE D5.8 (new file) |
| 4 | `platform/deployment_switch.py:311` | `SwitchMember.handle` | live-ref set on COMMIT | OUTSIDE D5.8 (new file) |
| 5 | `platform/deployment_switch.py:379` | `RedisSwitchTransport.drop_from_roster` | roster `srem` | OUTSIDE D5.8 (new file) |
| 6 | `platform/deployment_switch.py:387` | `RedisSwitchTransport.join` | roster `sadd` | OUTSIDE D5.8 (new file) |
| 7 | `platform/deployment_switch.py:390` | `RedisSwitchTransport.leave` | roster `srem` | OUTSIDE D5.8 (new file) |
| 8 | `platform/deployment_switch.py:256` | `prepare_round` | calls roster prune | OUTSIDE D5.8 (new file) |
| 9 | `platform/deployment_switch.py:445` | `SwitchSubscription.start` | calls `join` | OUTSIDE D5.8 (new file) |
| 10 | `platform/deployment_switch.py:469` | `SwitchSubscription.stop` | calls `leave` | OUTSIDE D5.8 (new file) |
| 11 | `main.py:155` | `create_app.lifespan` | calls `live_refs.load_latest` | `main.py` — in D5.8 |
| 12 | `main.py:263` | `create_app` | constructs the empty `LiveRefs()` | `main.py` — in D5.8 |

Result: **10 of 12 writes fall OUTSIDE D5.8** by path, all in one file, `backend/src/app/platform/deployment_switch.py`. The two in D5.8 are `main.py` call sites. `api/score.py`, `api/deployments.py` and `platform/deployments.py` hold no live-ref or roster write: `score.py` only reads (`live_refs.get` :236) and `platform/deployments.py` has only DB `session.add` rows (:359, :647, :785). Ruling for the lead: D5.8 says an outside path is "a stop to the lead, not a widening"; no ruling widening it to `deployment_switch.py` was found in the files I read.

## Closing acts (exec-1259c, 2026-10-19 04:45:43 BST)

Written by the executor seat exec-1259c under the maintainer's light-seat rule (to-lead 2026-10-19 04:39:47 BST): read and edit only; no test, check, build or DB was run for this section. Sources: the lead's verdicts (from-lead 04:40:22, amended 04:41:38) and the maintainer's entries "2026-10-19 04:35:24 BST", "04:41:23 BST" and "04:43:27 BST" in `to-lead.md`.

### §13 verdicts (the lead's; owner and due as corrected by to-lead 04:41:23)

Common form (PL-1237:128-131): **deferred with an owner — measured diagnostic, carried.** Owner: **WK-674 NFR measurement session on nfr-bench-1 — owner row to be added in D26** (no roadmap row names it: `grep -n 'nfr-bench-1' docs/roadmap.md` at bbc3f774 hits only :2710 and :2712, NFR-467/468 prose). VM coordination (user action): the maintainer. Discharge event: a dedicated host (nfr-bench-1).

- **NFR-489** — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; **due before the 12 Nov exit demo** (`docs/roadmap.md` §12 row 2 exit criterion, user 14 Oct 09:50). Ruling used: **DP-S5-a ruled (a)** (to-lead "2026-10-11 11:02:35 BST", RL-1614; PL-1620 §DP-S5-a): S5 holds the exit verdict on the S4 replicated path; SL-1455's sweep is FD-1411's remedy proof only. DP-3 reading: replicas under DP-3 as ruled (PL-1620 Acceptance 5; PL-1454 DP-3 (a) one process or (b) N uvicorn workers, N stated). No `--governed` run is recorded here.
- **NFR-490** — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; due before P2 close. Keeps PL-1237 Task 5's form (FAIL with figures if red), PL-1620:193.
- **NFR-493** (linearity limb) — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; due before P2 close.
- **NFR-494** — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; due before P2 close.
- **NFR-501** — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; due before P2 close. The carry form's extension to NFR-501 rests on PL-1620 D5.3 (:189-199) and is **ruled** in to-lead "2026-10-19 04:41:23 BST"; it rides D26 as an RL.
- **NFR-502** — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; due before P2 close.
- **F1 test** (≥3 runs per n ∈ {2,4,8}) — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; due before P2 close. The carry form names F1 directly (PL-1237:128-131).
- **O4 ladder bench** (LG-1363 §O4) — deferred with an owner — measured diagnostic, carried; owner WK-674 NFR measurement session on nfr-bench-1 (owner row to be added in D26), VM coordination (user action): the maintainer; due before P2 close. Extension of the carry form to O4 rests on D5.3 and is **ruled** in to-lead "2026-10-19 04:41:23 BST".
- **D5.12 script's governed run** — script delivered but untested (the measured run is not owed before merge, PL-1766:279-283); the run is deferred to nfr-bench-1, same owner and due as NFR-489 (it is the P2 NFR-489 exit verdict).
- **Adopted as delivered and tested** (to-lead 04:41:23 accepts): FR-268, FR-269, FR-272/NFR-498 rollback limb, NFR-497, D5.11, D5.13 (static), D5.14.
- **FR-452 / D5.10:** owed by SL-1259 before the PR; the two-case test is written (below), **not run**.

### A2 — gate evidence table (to-lead 04:35:24 item 2; cited from the logs, not re-run)

Logs are under `/home/puzhenhao1989/gi-pricing-plan.local/scratch/`.

| Run | Tree | END line (verbatim) | Verdict rows | Log | Ruled |
|---|---|---|---|---|---|
| Full gate | 19d139e6 | `END 2026-10-19T02:17:33+00:00 2.69 2.01 2.10 (date l1 l5 l15)` | ruff 0, mypy 0, import_linter 0, req_coverage 0, contracts 0; audit_docs rc 1; pytest rc 1 "16 failed, 6479 passed, 18 skipped, 132 warnings in 3299.25s (0:54:59)" (13 cascade + 3 test-only reds, later fixed test-side); frontend install/generate:api/lint/type-check/test/build all rc 0, tree after gate 0 changed paths; compose smoke "7 passed, 1 warning in 425.67s" PASS; switch runtime "1 failed" FAIL (the D5.11 symptom); demo journey `journey done in 1221s` (demo.log:5094), demo seconds 1358, dislocation #1 467 s, D7 ok +489842011; zeros all 0 | `sl1259-gate/gate.log` (+ `pytest.log`, `demo.log`) | to-lead 2026-10-19 03:18:08 BST |
| Run-small, sinks | 1f6934db | NOT FOUND: run-small writes no END line; last line of the log is `11 passed, 4 warnings in 4.80s` (started waiting on `/tmp/slots/small-test` at 03:32:09, load 1.46) | `backend/tests/test_error_sinks.py` 11 passed | `sl1259-runsmall-sinks.log` | to-lead 2026-10-19 03:33:30 BST ((c)+(a) accepted at H 1f6934db) |
| switch3 | ef2f0462 | `END 2026-10-19T02:54:58+00:00 4.06 4.02 2.95 (date l1 l5 l15)` | compose smoke "7 passed, 1 warning in 477.85s" PASS; switch runtime "1 failed, 1 warning in 29.72s" FAIL (diagnosed: no beat in the bring-up; FD-1661); jobs rows=3; teardown, zeros 0 | `sl1259-gate-switch3/gate.log` (+ `switch.log`, `jobs.txt`, `stack.log`) | to-lead "2026-10-19 03:55:35 BST", header quoted in full: "Maintainer: SL-1259 switch3 END read — SMOKE PASS accepted; the switch FAILS on the REQUIRED byte-identity assert (working as designed). STOP: no edit before options" (to-lead.md:27438) |
| switch4 | 4a3bd4a5 | `END 2026-10-19T03:05:15+00:00 2.57 1.99 2.20 (date l1 l5 l15)` | switch runtime "1 passed, 1 warning in 26.99s" PASS (`switch.log:85`); jobs.txt exactly 2 jobs (`rating.compile`, `rating.regression`, both 0.1.0+4a3bd4a5); deployed-bundle.json 26035 bytes, compiled_at inside the compile Job's window; teardown, zeros 0 | `sl1259-gate-switch4/gate.log` (+ `switch.log`, `jobs.txt`, `deployed-bundle.json`) | to-lead "2026-10-19 04:05:43 BST" (header: "Maintainer: SL-1259 D5.11 PROVEN at H3 4a3bd4a5 (switch4 END 03:05:15Z) — ruled"; D5.11 PROVEN, with a TEST-supplied beat; FD-1661 open); re-merge onto aea6f160, no python-half re-gate: to-lead 2026-10-19 04:06:08 BST |

Note on the switch3 row: switch3's own END is ruled by the 03:55:35 entry above (smoke PASS accepted; the switch fails the byte-identity assert); the 04:05:43 entry then names switch3 (smoke 7 passed @ef2f0462) in the evidence set. The 03:18:08 entry's "Open before SL-1259's PR" list (3 test-only reds; D5.11) is what the later rows discharge. The merged-head proof is this PR's full CI suite (to-lead 04:06:08).

### A3 — D5.7, quoted from PL-1766:230-232

> - **D5.7 — SL-1455 merged is a "Depends on" of Slice 5** (Q6, the maintainer's 10:29:56 entry:
>   *"SL-1455 becomes a formal Depends-on of S5 in the delta, because S5's NFR-489 exit reading
>   builds on SL-1455's measured path"*). It was an order only: `RL-1614`, recording the 11:02:35

(PL-1766 Acceptance item 3: `git grep -n 'D5.7' -- <this LG>` prints the quoted D5.7 line. The Q6 entry is to-lead "2026-10-18 10:29:56 BST"; the needs census above reads SL-1455 as merged (#1323, 9c602fec).)

### D5.8 ruling

To-lead "2026-10-19 04:43:27 BST" rules the D5.8 write-set STOP: `backend/src/app/platform/deployment_switch.py` is in D5.8 in place of `platform/bundle_slot.py` for the switch core and live ref (`bundle_slot.py` stays the bundle cache, untouched); the four registration edits (model_schema/__init__.py, scripts/generate-contracts.py, scripts/audit-docs.py, tests/test_audit_docs_ids.py) are in; the `docs/specs/06-governance.md` +2 is in as a pointer only (23:22:15 ruling), ACCEPTED as a pointer by to-lead "2026-10-19 04:44:06 BST" (header: "Maintainer: SL-1259 06-governance +1 line ACCEPTED as a pointer (04:43:27 condition 3 holds). It names 03 §5.1 as the sole definer of `deployment.switched`, and the chaining clause restates existing behaviour"); backend tests and `docs/contracts/schemas/generated/*` are confirmed as D5.8's tests and regenerated contract. Commit fae910ae's "D5.8" citation predates the ruling; no amend.

### A1 / D5.10 — the rollback FR-452 test (written, NOT run)

`backend/tests/test_management_rate_limit.py`: a fourth parameter `id="rollback"` on `_IN_HANDLER_ROUTES` (POST `/api/v1/environments/uat/deployments/rollback`, permission `deployment:promote`, permitted status 409 for a never-deployed version, which is raised after the count). It runs through the two existing `FR-452` tests: `test_a_403_from_an_in_handler_permission_check_is_not_counted[rollback]` (403 leaves the counter unchanged) and `test_a_permitted_call_to_an_in_handler_permission_route_is_counted_once[rollback]` (a permitted rollback adds exactly 1). Written during the QUIET block (no pytest allowed), so first delivered-untested. **Discharged 2026-10-19:** the window (to-lead "2026-10-19 06:26:22 BST": 20 passed incl. `[rollback]` x2, logs `scratch/sl1259-a1/window/`) ran it green, and the red-first (to-lead "2026-10-19 06:28:53 BST", accepted: `deployments.py:132` `count_management=count,` removed gives 1 failed, `assert (0 - 0) == 1`; restored gives 20 passed; dropdb count 0; logs `scratch/sl1259-a1/redfirst/`) is quoted below.

**A1 DB window, 2026-10-19 06:25 BST (exec, on the maintainer's order "2026-10-19 05:10:12 BST", item 2; full log `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1259-a1/window/full.log`, `run.out`, `run.err`):** (1) `docker exec gi-pricing-postgres-1 createdb -U gipricing -T template0 gipricing_sl-1259_2ccd468a`, 06:25:02 BST, rc=0. (2) `GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_sl-1259_2ccd468a uv run --directory <worktree> alembic upgrade head`, 06:25:02 BST, rc=0; `alembic heads` rc=0: `5c8e3b71d094 (head)` (one head). (3) `run-small.sh <worktree> backend/tests/test_management_rate_limit.py` at `bbc3f774` plus uncommitted edits, 06:25:10–06:25:31 BST, rc=0: `20 passed, 1 warning in 10.60s`. The run is `-q`, so the output carries no test ids (`grep -c rollback run.out` = 0); the `rollback` param is inside those 20 (the earlier attempt had the same 20 collected items, all erroring at the fixture), not named in the output. (4) `dropdb -U gipricing gipricing_sl-1259_2ccd468a`, 06:25:35 BST, rc=0; `select count(*) from pg_database where datname like '%sl-1259%'` = `0`. A1 is now delivered and run green; the red-first evidence (route's `count_management` removed) is still owed.

**A1 red-first window, 2026-10-19 06:27 BST (exec, on the maintainer's order to-lead "2026-10-19 06:26:22 BST"; full log `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1259-a1/redfirst/full.log`, `run-red.out`, `run-green.out`):** (1) database `gipricing_sl-1259_2ccd468a` created (`docker exec … createdb -T template0`, rc=0), `alembic upgrade head` rc=0, `alembic heads` = `5c8e3b71d094 (head)` (one head). (2) Removed, in the worktree only and uncommitted, the rollback route's `count_management=count,` at `backend/src/app/api/deployments.py:132` (inside `rollback_deployment`, passed to `service.rollback_and_switch`). (3) `run-small.sh <worktree> backend/tests/test_management_rate_limit.py`: rc=1, `1 failed, 19 passed, 1 warning in 9.95s`; failing test `test_a_permitted_call_to_an_in_handler_permission_route_is_counted_once[rollback]`, assert line `E       assert (0 - 0) == 1`. (4) `git restore backend/src/app/api/deployments.py` (diff empty, 0 bytes); re-run rc=0, `20 passed, 1 warning in 9.98s`. (5) `dropdb gipricing_sl-1259_2ccd468a` rc=0; `select count(*) from pg_database where datname like '%sl-1259%'` = `0`. The red-first evidence owed above is discharged: the route's count removed fails exactly the [rollback] counter assert, and restoring it passes.

*Disclosure (2026-10-19, executor): `PL-1766` Hand-off item 2 assigns the `SL-1259` roadmap dated line (`docs/roadmap.md:1197`) to the planner, but the executor wrote it in c5919fdf; the maintainer (by delegation) accepted this as disclosed (to-lead "2026-10-19 07:09:13 BST", item (1)), with no re-write now, and the planner reviews the line in D26.*
