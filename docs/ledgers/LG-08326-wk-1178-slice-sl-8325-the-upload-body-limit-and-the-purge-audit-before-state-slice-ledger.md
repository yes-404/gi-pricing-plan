---
id: LG-8326
family: ledger
title: WK-1178 slice SL-8325 — FD-1802 the upload body limit, FD-1746 the purge audit's before state (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05
owner: executor
tree: 0000000000000000000000000000000000000000   # set at the last build-log entry
slice: SL-8325
phase: P2
work: WK-1178
plans: [PL-8324]
corrected_by: []
relates: [FD-1802, FD-1746, PL-8324, FR-450, FR-235, NFR-472, FR-81]
---

# LG-8326 — WK-1178 slice SL-8325: the upload body limit and the purge audit's before state

**GO:** to-lead "2026-11-05 10:20:55 GMT" (PLAN A @d7af4f25; DP-A1 64 MiB as a typed setting, nginx = limit + a small margin; DP-A2 dated clause on FR-450 and `PAYLOAD_TOO_LARGE`; DP-A3 XLSX expansion and gzip expand-first out; DP-A4 purge `before` = version ids and statuses).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-8324, "SL 8325 — the upload body limit and the purge before state", R0 to R3 and G. Requirements: `07` FR-450, FR-445 (read); `03` FR-235; `01` NFR-472, FR-81 (read). Register: FD-1802, FD-1746. **Departure from the plan, by the ruling:** the plan's G4 says one constant and no setting; DP-A1 as ruled makes the limit the typed setting `max_upload_body_mib` (`GIP_MAX_UPLOAD_BODY_MIB`, default 64) in `backend/src/app/config.py`, and `backend/tests/test_api_body_limit.py` holds its default. Those two files are outside the plan's Write set and are named here as the brief allows. The setting's name differs from the plan's revised wording (`Settings.max_request_body_bytes`): the spec commit `be64d5d5` names `GIP_MAX_UPLOAD_BODY_MIB` (a MiB field), and the lead ruled (to-lead, after `be64d5d5`) to keep it. **Second departure:** T6 is not a new test in `test_data_nfrs.py`. `purge_subject` runs as the owner, so a new test would need an entry in `conftest_db.OWNER_FIXTURE_USERS` (outside the Write set). T6 extends the purge test already listed there, `backend/tests/test_lineage.py::test_a_subject_purge_is_admin_only_and_recorded`, which carries an added `NFR-472` marker; reported to the lead at 11:00 for a ruling.

### Task list

- R0 spec text: `be64d5d5`.
- R1 the limit: red `ebe2527a`, green `d2490e18`, T4 and the wiring test `a2c45973`.
- R2 the proxy: red `a029e461`, green `0ecf4935`.
- R3 FD-1746: red `ac43d055`, green `0d0a28a7`; A9 planted breaks (nothing committed).

### Gate

(The SOLO gate is the lead's.)

### Audit

(The auditor's.)

### Build log

**2026-11-05 (build, base d7af4f25).** Small runs through `run-small.sh`, each after waiting out rc 66 load refusals.

- Red, `backend/tests/test_api_body_limit.py` at `ebe2527a` (pass-through middleware): `3 failed, 2 passed`; the declared-length and boundary arms `assert 200 == 413`. The chunked arm first failed `assert 400 == 413` (the test's body was not valid multipart, so the parser answered), which is a fault in the test, not a red by cause. Fixed in `d2490e18` and re-proved red with the cap set to 10**9 bytes: `3 failed, 2 passed`, all three `assert 200 == 413`.
- Green at `d2490e18`: `5 passed`. At `a2c45973`: `9 passed`. Break proof of the wiring: with the `add_middleware(BodyLimitMiddleware …)` line commented out, `1 failed, 8 passed` (`test_the_application_caps_its_real_upload_route_before_authentication`); line restored.
- T5 red at `a029e461`: `deploy/lb.conf sets no client_max_body_size`, `1 failed, 32 passed, 1 skipped`. Green at `0ecf4935`: `33 passed, 1 skipped`. The skip is `frontend.nginx.conf`, not on this tree until D merges; the test holds it to the limit once it is.

**2026-11-05 10:49 to 11:00 UTC, DB window (granted by the lead, START 10:48:02).** Template guard at START and at END: `alembic_version=1 environments=3 tenant_marker=1`. Redis db 0 = 56 before and after; dbs 11, 12, 13 were 0 before, flushed and 0 after. DB copy `gipricing_sl-8325_cd5a1a0d` (`createdb -T gipricing`), dropped (copy count 0; datnames `gipricing postgres template0 template1`). No alembic ran: the copy was at the template's head and this slice has no migration.

- A9 baseline: `test_api_datasets.py` 32 passed; `test_validation_reports.py` 17 passed.
- A9 planted break 1 (`before=None` at `platform/datasets.py:314`, uncommitted): `1 failed, 31 passed`; `test_replacing_the_dictionary_is_audited_with_before_and_after` fails `TypeError: 'NoneType' object is not subscriptable`. Restored, `git diff --quiet` rc 0.
- A9 planted break 2 (`before=None` at `platform/validation.py:354`, uncommitted): `1 failed, 16 passed`; `test_an_acknowledgement_is_audited_with_its_justification` fails `assert None == {'rule_id': …, 'acknowledged': False}`. Restored, `git diff --quiet` rc 0.
- T6 red at `ac43d055`: `1 failed, 26 passed` in `test_lineage.py`; `assert None == {'versions': [{'id': …, 'status': 'draft'}]}`. Green at `0d0a28a7`: `27 passed` (the fix also orders the loaded versions by `version`).
- `test_data_nfrs.py` changes only the docstring at the transition test (the claim now covers the transition class and points at the other four).

**GREEN set (common seat brief item 29).** Changed modules: `app.api.body_limit` (new), `app.config`, `app.errors`, `app.main`, `app.platform.datasets` (`git diff --name-only d7af4f25...HEAD -- backend/src`). `app.main` imports every router, so the import closure is the whole backend suite; the predicate `git grep -l -E '^(from|import) app\.(config|errors|main|platform\.datasets|api\.body_limit)\b|^from app import .*\b(config|errors|main)\b|from app.platform import .*datasets' -- 'backend/tests/*.py'` alone matches 112 of 207 test files at this tree. The SOLO gate's full suite is the decisive green.

**2026-11-05 17:04 UTC, the audit's two not-met limbs (exec-sl8325b; base e75e0f1a, plan merged in at 19620e00, merge `91d11d86`).** DB-free through `run-heavy.sh --over-load` with the three URLs pointed at port 1.

- A4 tests, `23c3b641`, `test_api_body_limit.py`: `14 passed`, rc 0 (was 9). Green at base by design: the code already refuses on `Content-Length` before any read and the trace middleware is already outermost, so there is no red to take from the base. Each is proved by a planted break, restored (`git status --porcelain` empty after each):
  - (a) `await receive()` planted ahead of the `content-length` check in `body_limit.py`: `6 failed, 8 passed`; `test_a_declared_length_over_the_limit_reads_no_body_before_the_refusal` is among them.
  - (b) `TraceMiddleware` moved inside `BodyLimitMiddleware` in the test app: `3 failed, 11 passed`; `test_the_refusals_trace_header_is_the_problems_trace_id` is among them.
  - (c) the import route's pattern removed from `CAPPED_ROUTES`: `3 failed, 11 passed`; both `rate-tables/abc@abc/import` arms of the driven test are red, beside the pairing test.
- (c) needs no database: the cap refuses before routing reaches the handler or its authorisation, so the two real routes, taken from OpenAPI and driven through `create_app` with no credentials, declared and chunked, answer 413 (not 401) with `x-trace-id` equal to `trace_id`. Nothing here is OWED-TO-GATE.
- A7 README, `aa1cce60`: `deploy/README.md` states both limits, the 1 MiB margin (`65m`), that the proxy never answers first, and that a deployer who raises the setting raises both nginx values. A7's runtime limb and `client_max_body_size 65m` in D's frontend conf stay owed after D merges (not this seat's).
- `ruff check .` rc 0; `ruff format --check backend/tests/test_api_body_limit.py` rc 0.
- The audit's LOW notes, recorded and not edited: (1) FR-450's "before any of the body is held in memory" was true of the declared-length path only; on a chunked body FastAPI's form parse has read up to the limit when the count raises. **Resolved, not a LOW note (ruled to-lead "2026-11-05 16:57:37 GMT"):** A's own FR-450 amendment in `docs/specs/07-platform.md` is reworded in place, with no second clause: declared length is refused before any body is read, undeclared on passing the limit, what is read bounded by it; the code is unchanged. (2) The spec names the import route `{id}/import`; the route is `{slug}@{version}/import` (`03` §5.3 spells it so). (3) The version ordering of the purge event's `before` (the fix orders by `version`) is asserted by no test. Notes (2) and (3) stay LOW notes; the spec is edited only for (1).

**2026-11-05 20:42 GMT (exec-sl8325c, PART 1, DB-free; origin/main `cded9f0e`, D merged as #1435).** Merge `5c1971dc` (a merge, not a rebase) of `origin/main` into the branch.

- Conflicts, three, each resolved by reading: `docs/INDEX.md` taken from main and regenerated (`doc-index.py --check` rc 0, byte-stable); `docs/specs/01-data-management.md` taken from main (the Permission column on every §5.1 row) and the one clause this slice adds re-applied to the `POST /api/v1/sources/{id}/preview` row, before its Permission cell, with the missing full stop supplied; `backend/tests/test_deploy_stack.py` keeps both sides (this slice's T5 body-size tests and main's `test_the_nginx_check_goes_red_on_a_conf_missing_a_limb`), and the skip on "frontend.nginx.conf not on this tree" is removed because the file is on the tree. `docs/specs/07-platform.md` and `deploy/README.md` merged without conflict.
- T5 red by cause on the merged tree: `test_the_proxy_does_not_undercut_the_request_body_limit[frontend.nginx.conf]` fails `deploy/frontend.nginx.conf sets no client_max_body_size`, `1 failed, 41 passed`. Green after `3670dfc8` (`client_max_body_size 65m;` in the `server` block, the API limit of 64 MiB plus 1 MiB, with `deploy/lb.conf`): `42 passed`, rc 0, `run-heavy.sh --over-load` with the three URLs on port 1.
- A7's runtime limb is written, not run: `test_an_upload_past_the_limit_through_lb_is_the_apis_413_and_not_nginxs` in `backend/tests/test_deploy_stack_runtime.py` (`253ed021`, tests alone in the commit). A 2 MiB body is not a 413; a body of the limit + 1 byte is `413` `application/json` with `code == PAYLOAD_TOO_LARGE`. It needs a compose build and `GIP_DEPLOY_TESTS=1`: owed to PART 2's build window.

**2026-11-07 17:55 GMT (exec-sl8325d, PART 1', DB-free; `origin/main` `6f958137`, 12 merges beyond `cded9f0e`).** Merge `f20955f0` (a merge, not a rebase) of `origin/main` into the branch `3a2483d3`.

- Conflicts, two: `docs/INDEX.md` taken from main and regenerated (`doc-index.py --check` rc 0, byte-stable); `docs/specs/03-rating-engine.md` FR-233 and FR-234 from main (new amendments), FR-235 kept with this slice's 413 amendment (this slice's only change to that file, by `git diff cded9f0e 3a2483d3`). No non-docs conflict; `errors.py` and `test_lineage.py` auto-merged (overlap predicate: `comm -12` of this branch's non-docs paths against `git diff --name-only cded9f0e origin/main`).
- Import closure (changed src by `git diff --name-only origin/main...HEAD -- backend/src`: `api/body_limit.py`, `config.py`, `errors.py`, `main.py`, `platform/datasets.py`; closure of 93 source files, 175 test files importing it, plus items 43 and 45 files). Run DB-free through run-small with unreachable DB and Redis URLs: `test_api_body_limit.py test_config.py test_errors.py` 73 passed rc 0; `test_error_sinks.py test_approval_guard.py test_management_429_declared.py` 22 passed, 4 errors (DB connect refused); `test_shadow_log_sanitised.py test_startup_gc_freeze.py test_worker_handler_coverage.py` 7 passed, 2 failed (`test_startup_gc_freeze.py`, both `ConnectionRefusedError` to the dummy DB); `test_api_authorisation_sweep.py test_deploy_stack.py test_data_nfrs.py` 44 passed, 12 errors (the sweep and `test_data_nfrs.py` fixtures need the DB). Every red is a DB connect refusal; none is an assertion. The DB-backed rest of the closure, the item 43 sweep, `test_error_sinks.py`'s four and `test_deploy_stack_runtime.py` (docker) are owed to the gate.
- `ruff check .` rc 0; `uv run mypy` rc 0 (254 source files), both at `f20955f0`.

**2026-11-07 17:59 GMT (exec-sl8325d, PART 2: A7's runtime limb, single-tenant on docker, compose project `gip-s4-runtime` with `docker-compose.isolated.yml` ports, LB on 18000; never the shared stack; no prune).** Second re-merge first: `origin/main` `3c3ee5cb` merged cleanly (`Merge made by the 'ort' strategy.`; only `frontend/pnpm-lock.yaml` and `frontend/pnpm-workspace.yaml`), head `8cf89fdc2b5d9e911dd1b421f8a6ce0abd6fa6d3`; `pnpm --dir frontend install --frozen-lockfile` rc 0.

- The 16 setup errors of the DB-free GREEN run, read from a full run at `8cf89fdc`: all 16 `ConnectionRefusedError: [Errno 111] Connect call failed ('127.0.0.1', 1)` to the dummy DB (`test_api_authorisation_sweep.py` 9, `test_data_nfrs.py` 3, `test_error_sinks.py` 4). No other cause. They are owed to the gate.
- A7 run, head=`8cf89fdc2b5d9e911dd1b421f8a6ce0abd6fa6d3`: `GIP_DEPLOY_TESTS=1 GIP_N_SHA=<head> uv run pytest -q -s backend/tests/test_deploy_stack_runtime.py::test_an_upload_past_the_limit_through_lb_is_the_apis_413_and_not_nginxs`, 1 passed in 132.19 s, pytest rc 0. Printed: `POST 2 MiB -> 400 application/problem+json` (not a 413); `POST limit+1 (67108865 bytes) -> 413 application/problem+json`. The 413 is the API's RFC 9457 body, not nginx's HTML. df before 14063M, after 11122M (the app image `gi-pricing-app:8cf89fdc…` stays, no prune). The stop-file check (`sl8368-gate/gate/fe-*`, `demo.log`) found none before the stage.
- Teardown: the test's `down` fixture removed the project; no `gip-s4*` containers remain, the four shared containers still run.

## PRs

(Owed at the PR: number, title, merge commit. Branch `sl-8325-a-upload-limit`, unpushed at this entry.)
