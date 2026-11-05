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

## PRs

(Owed at the PR: number, title, merge commit. Branch `sl-8325-a-upload-limit`, unpushed at this entry.)
