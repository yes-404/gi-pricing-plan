---
id: LG-2076
family: ledger
title: WK-1178 slice SL-2075 — FD-1802 the upload body limit, FD-1746 the purge audit's before state (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-07             # original date 2026-11-05, set at the draft under working id 8326; minted 2026-11-07
owner: executor
tree: b655490eb27d546d68e94c96b7735a6d575f686b   # the slice branch's tree at its last build-log entry (14571939), before the merge of origin/main
slice: SL-2075
phase: P2
work: WK-1178
plans: [PL-2074]
corrected_by: []
relates: [FD-1802, FD-1746, PL-2074, FR-450, FR-235, NFR-472, FR-81]
---

# LG-2076 — WK-1178 slice SL-2075: the upload body limit and the purge audit's before state

*(Minted 2026-11-07 as LG-2076 from working id 8326, in the SL-2075 mint, with the mint tool of record `mint-repoint.py`; plan PL-2074 (8324), slice SL-2075 (8325) and ledger LG-2076 (8326) minted together, in that order.)*

**GO:** to-lead "2026-11-05 10:20:55 GMT" (PLAN A @d7af4f25; DP-A1 64 MiB as a typed setting, nginx = limit + a small margin; DP-A2 dated clause on FR-450 and `PAYLOAD_TOO_LARGE`; DP-A3 XLSX expansion and gzip expand-first out; DP-A4 purge `before` = version ids and statuses).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2074, "SL-2075 — the upload body limit and the purge before state", R0 to R3 and G. Requirements: `07` FR-450, FR-445 (read); `03` FR-235; `01` NFR-472, FR-81 (read). Register: FD-1802, FD-1746. **Departure from the plan, by the ruling:** the plan's G4 says one constant and no setting; DP-A1 as ruled makes the limit the typed setting `max_upload_body_mib` (`GIP_MAX_UPLOAD_BODY_MIB`, default 64) in `backend/src/app/config.py`, and `backend/tests/test_api_body_limit.py` holds its default. Those two files are outside the plan's Write set and are named here as the brief allows. The setting's name differs from the plan's revised wording (`Settings.max_request_body_bytes`): the spec commit `be64d5d5` names `GIP_MAX_UPLOAD_BODY_MIB` (a MiB field), and the lead ruled (to-lead, after `be64d5d5`) to keep it. **Second departure:** T6 is not a new test in `test_data_nfrs.py`. `purge_subject` runs as the owner, so a new test would need an entry in `conftest_db.OWNER_FIXTURE_USERS` (outside the Write set). T6 extends the purge test already listed there, `backend/tests/test_lineage.py::test_a_subject_purge_is_admin_only_and_recorded`, which carries an added `NFR-472` marker; reported to the lead at 11:00 for a ruling.

### Task list

- R0 spec text: `be64d5d5`.
- R1 the limit: red `ebe2527a`, green `d2490e18`, T4 and the wiring test `a2c45973`.
- R2 the proxy: red `a029e461`, green `0ecf4935`.
- R3 FD-1746: red `ac43d055`, green `0d0a28a7`; A9 planted breaks (nothing committed).

### Gate

**The full code gate, both halves, SOLO, gate-1** (`~/gi-pricing-plan.local/scratch/sl8325-gate/gate/gate.log`; START 2026-11-07T18:00:41+00:00 at head `28f15e114fba0d8b10412ba870d3138453f6d05e`, tree `e31042d59ef20f9f38d2bf8c5145e74e1923472a`, branch `sl-8325-a-upload-limit`; `END 2026-11-07T20:16:50+00:00 1.62 1.54 1.88 (date l1 l5 l15) rc=1`). Read from the gate's own logs, not recalled:

| Stage | Result |
|---|---|
| ruff, mypy, import-linter | `ruff.rc` 0, `mypy.rc` 0, `import_linter.rc` 0 |
| `generate-contracts.py --check`, `req-coverage.py` | `contracts.rc` 0, `req_coverage.rc` 0 |
| pytest | `pytest.rc` 1: `14 failed, 7523 passed, 28 skipped, 5 xfailed, 156 warnings in 4879.32s (1:21:19)` |
| `audit-docs.py` | `audit_docs.rc` 1, `FAILED (2)`: `check 31: gap in the full allocation between 2064 and 8324`; `check 31: id 8324 is created: 2026-11-05, earlier than id 2064's 2026-11-06`. Both name this slice's own working id 8324: the mint (PL-2074, SL-2075, LG-2076) is what clears them |
| frontend | `pnpm generate:api`, `lint`, `type-check`, `build` rc 0; `pnpm test --maxWorkers=2` rc 0, `Test Files 138 passed (138)`, `Tests 919 passed (919)` |
| demo | `demo.py --journey wf-699 --no-compose` rc 0 (PASS 1428 s); `D7 ok`, `sum +489842011 minor units`; A6 infra diff rc 0; shared stack restored from tools-main rc 0; template guard at END `alembic_version=1 environments=3 tenant_marker=1`; redis db 0 dbsize 56 (start 56) |

**The 14 failures, by name, against item 31's set** (`grep '^FAILED' pytest.log`): the 13 of item 31 are `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`, `tests/test_audit_docs_ids.py` x2 (`test_the_real_tree_passes_all_ten_checks`, `test_doc_id_check_exits_0_on_the_real_tree`), `tests/test_audit_docs_process_core_digest.py` x2, `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`, `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`, `tests/test_register_lint.py` x3, `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`, `tests/test_repository_invariants.py` x2. The 14th is `backend/tests/test_worker_raise_sites.py::test_every_quote_input_coded_raise_site_in_the_backend_is_accounted_for`: **not** in item 31's set, a real defect of this slice, below.

**The 14th failure and the missed item 11 (a closure finding of this slice).** `AssertionError: a quote-input PlatformError/_raise_named site was added, moved, or now interpolates a new expression ... Left contains 1 more item: {('backend/src/app/api/body_limit.py', '__call__', '<dynamic>'): frozenset({'_TITLE', 'status.HTTP_413_CONTENT_TOO_LARGE', 'too_large_detail(self.max_bytes)'})}` (`pytest.log`, the `_ test_every_quote_input_coded_raise_site_in_the_backend_is_accounted_for _` block). Cause: the slice added a coded raise site in `body_limit.py` and its small runs never included `test_worker_raise_sites.py` and `test_quote_input_raise_sites.py`, which common seat brief item 11 requires for a slice that adds a quote-input raise site. Fixed as its own commit `14571939`, ahead of the re-merge: the key is listed in `_SITES` with the reason "the 413 title constant, the status, and the configured byte limit; no quote input". GREEN by `run-small.sh` at that commit, the two files together: `22 passed`, rc 0; `uv run ruff check .` rc 0; `uv run mypy` `Success: no issues found in 254 source files`, rc 0. No full re-gate (the C form): CI at the merged head; the gate's frontend and demo readings stand, since they passed at END.

**SKIPPED 28 v 27.** The gate's own row: `pytest skipped | FAIL: 28 (!= 27 baseline ...)`. The skip count rose by one because `backend/tests/test_deploy_stack_runtime.py` now holds 14 tests where it held 13 (the 14th is this slice's own `test_an_upload_past_the_limit_through_lb_is_the_apis_413_and_not_nginxs`, gated on `GIP_DEPLOY_TESTS=1`, so it skips in a gate without it). Its proof is PART 2's window above: head `8cf89fdc`, `1 passed in 132.19 s`. The baseline of 28 is from this slice's merge: CI and later gates count 28.

**The gate stands** modulo the census fix in the mint, on the maintainer's word recorded in `to-lead.md` after 20:16 on 2026-11-07 ("The gate stands modulo the census fix in the mint", as quoted by lead 31 at the mint seat's spawn), under item 31 for the 13 docs-audit failures and the lead's ruling for the 14th (the AMENDMENT to the mint brief, 2026-11-07 19:52:20 GMT).

### Audit


**Object.** `origin/main...e75e0f1a2f3236c3ba353ad7ce6ba1318cbf3ac5` (tree `53db90dc6b4cbc6ef474b68e16f23cd06e3e65a6`), 13 commits, read in the detached worktree `aud-sla`. Scope derived from PL-2074 at `draft/pl-a-2026-11-05` @19620e00 (A1–A12) read whole, against the code and tests; the build log is matched two-way: every ledger SHA (`ebe2527a a029e461 ac43d055 d2490e18 0ecf4935 0d0a28a7 ca34d63c 6bb77981 1f1f4ed4 e75e0f1a`) exits 0 under `git merge-base --is-ancestor <sha> e75e0f1a`. Red commits `ebe2527a`, `a029e461`, `ac43d055` change tests only (`ebe2527a` also adds the pass-through stub of `body_limit.py`).

**Runs (DB-free, run-heavy --over-load, beside D's pytest, load1 ≈ 14, non-timed), tree e75e0f1a:** `test_api_body_limit.py` `9 passed`, rc 0; `test_deploy_stack.py` `33 passed, 1 skipped`, rc 0 (the skip is `frontend.nginx.conf`, not on the tree). `audit-docs.py` (--light) fails 4 lines: check 31 (gap 2006→8324) and check 32 ×2 on LG-2076 (working ids, allowed) and **check 39 (INDEX stale against regeneration), not classified here: regenerate after the mint (item 17)**. Not runnable here (DB-backed): `test_lineage.py`, `test_data_nfrs.py`, `test_api_datasets.py`, `test_validation_reports.py`: the ledger's DB-window lines are MET-BY-RECORD.

| Item | Proposed verdict | Evidence read to the assert |
|---|---|---|
| A1 write set | MET | `git diff --name-only origin/main...HEAD`: nothing under `frontend/`, `packages/`, `docs/contracts/`, `scripts/`; `config.py` is DP-A1's typed setting (named in the LG). `generate-contracts --check` OWED-TO-GATE. |
| A2 spec first | MET | `be64d5d5` precedes `ebe2527a`; FR-450 clause states 64 MiB and the typed setting; the nginx file `65m` cites it; `deploy/frontend.nginx.conf` OWED-TO-SUCCESSOR. |
| A3 red by cause | MET-BY-RECORD | LG quotes T1–T3 `3 failed, 2 passed` `assert 200 == 413`, T5 `sets no client_max_body_size`; T2's first red was `400` (a test fault) and is disclosed and re-proved. T4 by the break test (`a2c45973`), as the plan says. Reds not re-run here. |
| A4 declared length | **NOT MET in part** | T1 asserts 413, `PAYLOAD_TOO_LARGE`, `trace_id == traceparent's`, handler not entered (preview route, small app) and the real app on preview (`…_before_authentication`). Missing against the 19620e00 text: (a) the **import** route is not driven (only paired by T4's regex); (b) no sentinel `receive` shows no body read on the declared-length path; (c) `x-trace-id` header not compared with the problem's `trace_id`. |
| A5 undeclared length, boundary | MET | T2 (chunked, `pulled <= LIMIT // CHUNK + 2`, `413`, code, `trace_id`; a `PlatformError` raised from `receive` would be `400`, so the status assert proves the `HTTPException` class) and T3 (`LIMIT-1`, `LIMIT` → 200; `LIMIT+1` → 413). 9 passed. |
| A6 routes = declarations | MET | T4 walks `create_app().openapi()` both directions; the break test shows each direction red. Paths declaring 413 in `docs/contracts/openapi/generated.json`: the two routes only. |
| A7 proxy | lb.conf limb MET; frontend conf + runtime limb **OWED-TO-SUCCESSOR**; the `deploy/README.md` clause **NOT MET** | T5 parses `client_max_body_size 65m` ≥ default + 1 MiB (33 passed). 19620e00's A7 and Write set say `deploy/README.md` tells a deployer who raises the setting to raise both; README is not in the diff (the lb.conf comment says it, ambiguously). |
| A8 FD-1746 limb 1 | MET-BY-RECORD | `test_lineage.py` asserts `before == {"versions": [{"id": str(version_id), "status": "draft"}]}` and `after` unchanged; code passes it, `order_by(DatasetVersionRow.version)`. Departure (T6 extends the existing purge test, one version, in `test_lineage.py` not `test_data_nfrs.py`) is disclosed in the LG; the **ordering** is therefore unasserted. |
| A9 limb 2 | MET-BY-RECORD | Docstring read at `test_data_nfrs.py`: claims the transition, points at the other four, marker kept. LG quotes both planted breaks red by their own assert and `git diff --quiet` rc 0. `test_api_datasets.py:191` asserts `v2.before == v1.after` (rule-set, SL-1736). |
| A10 GREEN set, gate | OWED-TO-GATE | Import closure of `app.main` is the whole backend suite (LG says so; 112/207 files by its own predicate). Solo gate, `req-coverage`, `generate-contracts --check`: the lead's. |
| A11 closing acts | drafts | FD-1802, FD-1746 and the DP-A3 LOW FD: `scratch/aud-sla/`. |
| A12 | OWED | INDEX regeneration after the closing acts. |

**Findings of the audit (proposals).** (1) A4 (a)–(c) and A7's README clause are the not-met limbs; both are small and in the slice's files. (2) FR-450's clause says the body is refused "before any of the body is held in memory": true of the declared-length path only; on a chunked body FastAPI's form parse has read up to the limit when the count raises. Wording, LOW. (3) The clause and the plan name the import route `{id}/import`; the route is `{slug}@{version}/import`. (4) `deploy/lb.conf`'s comment "Raise it with GIP_MAX_UPLOAD_BODY_MIB" reads as if the setting moves nginx; T5 holds only the default. (5) The LG's front matter `tree:` is still the zero placeholder (set at the last build-log entry). (6) No caller of a changed shape found outside the Write set: `entity_ref` of the purge event is unchanged (`test_migration_dataset_owner.py:267-279`), `_STATUS_CODES` gained one entry, the setting has no sibling mirror (`git grep blob_multipart_threshold_mb` = config.py only). Not run: any test beyond the two files.

**Lead's adoption:** the auditor's proposals above are ADOPTED by lead 30, from-lead "2026-11-05 16:56:31 GMT" (aud-sla FINAL: A1, A2, A5, A6, A7 lb.conf MET; A3, A8, A9 by record; A10, A12 owed to the gate; A4 in part and A7's README clause NOT MET). *(Dated line, 2026-11-07, lead 31: the audit text was drafted in the auditor's scratch directory `~/gi-pricing-plan.local/scratch/aud-sla/` and is folded in here at the mint, working ids re-pointed, per the common seat brief item 34.)*

*(Dated line, 2026-11-07, lead 31: where each limb the audit left open was discharged.)* A4 (a)–(c): the Build log entry "2026-11-05 17:04 UTC, the audit's two not-met limbs" (`23c3b641`, 14 passed, each by a planted break, restored). A7's README clause: `aa1cce60` (`deploy/README.md` states the limit, the nginx margin and that the proxy never answers first). A7's frontend conf limb: `3670dfc8` (`client_max_body_size 65m`). A7's runtime limb: PART 2 at `8cf89fdc`, 1 passed in 132.19 s through lb (2 MiB → 400, limit + 1 → 413 `PAYLOAD_TOO_LARGE`). A10: the solo gate, END 2026-11-07T20:16:50Z, standing modulo the census fix (### Gate above). A11: the closing acts on FD-1802 and FD-1746 in this PR's audit commit. A12: INDEX regenerated at the mint. Finding (2), FR-450's "before any of the body is held" on a chunked body, stays a LOW wording note for the next docs batch.

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

(This PR; its number, squash commit and merge date are written at the merge's date-of-record. Branch `sl-8325-a-upload-limit`.)
