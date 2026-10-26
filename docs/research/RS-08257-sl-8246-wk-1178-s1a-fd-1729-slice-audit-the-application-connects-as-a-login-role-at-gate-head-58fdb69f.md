---
id: RS-8257
family: research
kind: audit
title: S1a (WK-1178, FD-1729) slice audit — the application connects as a login role, not the owner, at gate head 58fdb69f
status: draft
created: 2026-10-26   # drafted 2026-10-26 under working id 8257; created = mint date
owner: auditor
tree: b15a017175c5b630e271906aad50121fab0fda9f
phase: P2
work: WK-1178
corrected_by: []
relates: [LG-8237, SL-8246, FD-1729, FD-8256, OQ-8252, OQ-8255, PL-1769, PL-1927]
---

# RS-8257 — S1a slice audit (FD-1729, the application off the owner role)

*(Working id 8257, reserved by lead 28; the slice is SL 8246 (re-cut of SL-1771's login-role half), its ledger LG 8237, both unminted at this audit. Written by `aud-s1a` (auditor, sonnet, effort medium) in worktree `.claude/worktrees/aud-s1a`, branch `aud-s1a-2026-10-26`, from `58fdb69f`. Docs and diff reading only: no test, gate, DB or audit-docs run by this seat. The verdict is a proposal; the lead adopts (CLAUDE.md §12).)*

## Question

Does `draft/s1a-fd1729` at the gate head `58fdb69f` (tree `b15a0171`, merge-base `3cd5fcf7ee514db1ae8ab681d7cacc1761945091`) meet PL-1927's S1a section, PL-1769 Tasks 1–7, and each ruling from to-lead "2026-10-25 22:04:36 GMT" to "2026-10-26 03:28:21 GMT"?

## Method

Scope first, from the plan and the rulings; then evidence.

- **Plan.** PL-1927 (`docs/plans/PL-01927-…`, on origin/main since #1394) cuts S1a and S1b from SL-1771 (to-lead "2026-10-26 02:07:55 GMT" item 1 quotes line 23–24: S1a and S1b "a re-cut of `SL-1771`, whose plan `PL-1769` stays frozen"). PL-1769 (S-b) Tasks 1 (role SQL + script), 2 (two DSNs), 3 (fixtures), 5 (grants migration), 6 (compose run).
- **GO / rulings** read at their bodies in `~/gi-pricing-plan.local/channel/to-lead.md` (headings at lines 31087, 31099, 31112, 31177, 31181, 31184, 31188, 31194, 31259, 31292, 31302, 31305, 31308, 31311, 31334, 31347, 31416). There is no single "S1a GO" heading: 22:04:36 says "NOTED (not a GO)", and the START hold of 02:07:55 item 7 is lifted at 02:10:01; the gate then STANDS at 03:28:21. The conditions audited are those rulings' clauses, quoted per row.
- **Diff.** `git diff --stat 3cd5fcf7 58fdb69f` = 93 files, +3117/−620; each non-test file read; test files by `OWNER_FIXTURE_USERS`/seam reading and the AST check below.
- **Checks run (read-only):** `git merge-base --is-ancestor`; a `python3 -I` AST walk of `OWNER_FIXTURE_USERS` and each cited test function; a migration-head scan; `git grep` for working ids; `doc-index.py --check` (rc 0).

## Findings

**Proposed verdict: CLEAN.** No blocking finding. Four non-blocking (N1–N4).

### Scope against the diff

- `git diff --name-only 3cd5fcf7 58fdb69f -- frontend` = empty (0 lines): the frontend is untouched.
- Non-test, non-docs paths: `backend/migrations/env.py`, `backend/migrations/versions/b7e4c2a91d36_application_role_grants.py` (new, 194), `backend/src/app/config.py`, `deploy/docker-compose.yml`, `deploy/postgres/app-login-role.sql` (new), `scripts/provision-app-role.py` (new), `scripts/demo.py`, `examples/fremtpl2/seed.py`, `pyproject.toml` (marker), `.github/workflows/python.yml`, two skills. Nothing under `backend/src` other than `config.py`.
- Merge-base `3cd5fcf7…` is older than main's later test additions, which is why the gate's `6800 passed` differs from PL 8205's `6896` (to-lead 03:28:21).

### Row-by-row

| # | Obligation (ruling) | Verdict | Evidence |
|---|---|---|---|
| a1 | Role SQL idempotent, never superuser/owner, no credential (PL-1769 Task 1) | MET | `app-login-role.sql`: `CREATE ROLE gip_app NOLOGIN`, `gip_app_login LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`, then `ALTER ROLE … ` converge and `GRANT gip_app TO gip_app_login`; closing comment "No credential here" |
| a2 | Script sets a SCRAM verifier, never the plain password, never prints it, refuses the default without the flag | MET | `provision-app-role.py`: `scram_sha256_verifier` (pbkdf2-hmac, StoredKey/ServerKey) → `ALTER ROLE … PASSWORD '{verifier}'`; `print("gip_app_login provisioned")` only; `password == DEFAULT_PASSWORD and not args.allow_default_password` → rc 2; no owner DSN → rc 2, "never falls back to the application DSN". `test_provision_app_role.py` (+146) covers it |
| a3 | Compose: `GIP_DATABASE_URL` = login role; `migrate` on `GIP_MIGRATION_DATABASE_URL` (01:47:30 S1a-5 scope) | MET | `docker-compose.yml:20` `gip_app_login:gip_app_login@postgres`; `:116` migrate-only `GIP_MIGRATION_DATABASE_URL: …gipricing:gipricing@…`; the only two DSN lines in the file (`grep -n 'DATABASE_URL'`); initdb mount `:./postgres/app-login-role.sql` read-only |
| a4 | `env.py` refuses the fallback | MET | `env.py`: `_migration_url = load_settings().migration_database_url; if None: raise RuntimeError("GIP_MIGRATION_DATABASE_URL is not set … never fall back to GIP_DATABASE_URL")`; `config.py` validator extended to `migration_database_url`, default `database_url` is the login role |
| b1 | Exactly one owner seam (22:24:25 option (a)) | MET | `seed_as_owner` at `conftest_db.py:1115`; `owner_database` (`:1070`) is the fixture for tests that ARE the owner subject; both build from the one `test_owner_database_url()` (`:158`), which `test_owner_database_url_is_called_only_inside_conftest_db` scans |
| b2 | Seam is test-only (22:24:25 cond. (i), red-first) | MET | `test_the_owner_seam_exists_and_is_not_named_anywhere_in_backend_src` plus a negative case with an injected file; `db8dddaa` precedes `df215d55` (ancestor yes) |
| b3 | Commit semantics and teardown stated (cond. (ii)) | MET | `seed_as_owner` docstring: commits before return, visible to the app connection; teardown by a fresh `workspace_id` and the session-end owner TRUNCATE |
| b4 | Autouse patch covers exactly `ensure_workspace` and `seed_builtin_roles`; settings functions NOT patched (23:11:30) | MET | `conftest_db.py:1290–1291`: the only two `monkeypatch.setattr` lines; docstring `:1275–1278` says the two settings setters "are deliberately NOT patched"; `set_workspace_setting`/`set_environment_setting` wrappers exist (`:1238`, `:1250`) and route through `seed_as_owner` only at seed call sites |
| b5 | `production_seed` opt-out marker, registered, used by the production-function test only (23:10:31 (iii), 23:14:44 (2)) | MET | `pyproject.toml` marker; 1 use in `test_rbac.py`, 2 in the guard test, 2 in `conftest_db.py`; guard test `test_a_production_seed_test_gets_the_original_functions` |
| b6 | Guard test red-first (23:10:31 (ii)) | MET | `a9541445` is an ancestor of `d538a418` (yes) |
| b7 | Discoverability line in `python-test/SKILL.md` with `Verified` refreshed (23:10:31 (iv)) | MET | line dated 2026-10-25 names the seam, both functions, the autouse fixture and `production_seed`; `Verified: 2026-10-25 … for that line only` (see N4) |
| b8 | `OWNER_FIXTURE_USERS` closed, every row 3 fields (run 4 cause, `163146f2`) | MET | AST walk of `conftest_db.py` at the gate head: 130 rows, arity `{3: 130}`, 0 duplicate node ids, every node id resolves to a `def` in its file (0 missing); labels `owner-subject` 97, `migration` 21, `DP-22` 10, `bootstrap` 2; all in `_LABELS`; `test_owner_fixture_users_is_a_closed_labelled_tuple` asserts tuple, label, non-empty reason, no `api_settings`/`api_client` |
| b9 | Each listed test justified by its label | MET with N2/N3 | reasons read by distinct text: tamper probes, scratch-DB migrations, DP-22 caller-less paths, the FR-420 sweep (OQ 8252), the seed's `grant_demo_principals` |
| c1 | Grants migration grants only what the census/red list proved; no grant on residue (23:14:44 (1): "no census defect and no grant") | MET | `b7e4c2a91d36` history is two commits, `bcc0eeb4` (census `_TARGET`) and `61f5b5a9` (`alembic_version: READ`, ruled at 22:17:05 and accepted); nothing added after the 23:14:44 residue ruling |
| c2 | No UPDATE/DELETE on append-only tables; no INSERT for a test seed | MET | `audit_events`, `factors`, `backtests`, `profiles`, … are `APPEND` (SELECT, INSERT); identity tables (`workspaces`, `workspace_members`, `roles`, `role_assignments`, `subject_purges`) are `READ`; `jobs`/`outbox` DELETE revoked; `blobs` is `UPDATE(ref_count)` only (no DELETE, per OQ 8252); `scoring_traces` DELETE is the pre-existing `_PREVIOUS` row, unchanged |
| c3 | Grants to `gip_app` only; reversible; one head | MET | `APP_ROLE = "gip_app"`, `_apply` is `REVOKE ALL` then the target; `downgrade()` restores `_PREVIOUS`; migration-head scan: `b7e4c2a91d36` revises `9b3e7c15d4a2`, which is the previous head |
| d1 | FD 8256: fixture fails when configured, skips only when not (01:54:05, 01:56:43 scope (i)–(iv)) | MET | `_unavailable(configured, message)` (`conftest_db.py:1002`): `pytest.fail` if configured else `pytest.skip`; applied to the connect failure, the no-migrations probe and `blob_store` (`:1049`, `:1059`, `:1107`); `_database_configured()` is the two `GIP_TEST_*` URLs, blob is `GIP_TEST_BUCKET` or `GIP_BLOB_ENDPOINT_URL` |
| d2 | No rendered DSN carries a password | MET | `_safe_dsn` (`:996`) renders `host:port as user, database`; `hide_password=False` is at `:191` only, for the engine's own DSN; the red test's (iii) assert is the proof (red `5 failed, 1 passed`) |
| d3 | Red-first ancestry `4bc098a5` → `2124a622` | MET | `merge-base --is-ancestor 4bc098a5 2124a622` = yes; the fix commit edits the test file by 4 lines (two asserts), disclosed and covered by the re-proof line in LG 8237 (`FD 8256 red re-proved with the final test … 5 failed, 1 passed … rc 1`), accepted at 02:07:55 item 6 |
| e1 | Red commits precede fixes in general | MET | `d1d96465` is an ancestor of `6baac46b`, `8f8952ac`, `d8ab3889`, `bcc0eeb4`; `0cfd744d` of `6baac46b`; all yes |
| e2 | LG five-run history carries sha + rc | MET | Runs 1–5 at LG 8237 lines 204–208: `df215d55` 665F/51E rc 1; `0ba5acf6` 532F/18E rc 1; `10fd875c` 19F rc 1; `22c2b7d3` 1F/130E rc 1 (cause: 16 four-field rows, fixed by `163146f2`); `163146f2` `2873 passed, 13 skipped` rc 0, each with a log path |
| e3 | Gate-of-record lines in the LG (sha + rc) | NOT YET | the LG at `58fdb69f` has no line for the gate (`58fdb69f`, `13 failed, 6800 passed, 21 skipped`, END rc 1, 1(f) set, `rc_role=0 rc_skip=0`); it exists only in to-lead 03:28:21 — N1 |
| f1 | OQ 8252 / OQ 8255 mirrored (open-questions + spec §10 + roadmap gate row) | MET | `open-questions.md` rows for both; `07-platform.md` §10 carries OQ-8252 and `01-data-management.md` §10 carries OQ-8255, each "Mirrored in `docs/open-questions.md`"; two roadmap gate rows (`1 (1 open)` each), "keep the row" per 01:47:30 |
| f2 | FD 8256 essay + register row in fix-before-close form | MET | essay (the FD 8256 file) (front matter, Finding, Evidence, Severity, Remedy, Disposition); `register.md` row "**fix before close**: SL 8246 / LG 8237 … closed in place citing the PR when that slice merges" |
| f3 | LG 8237 placeholders kept, append-only | MET | `slice: SL-1771`, `GO: none yet`, `MERGE-ACK: none yet`, `tree: d1d96465` unchanged; every later change is an appended dated line; the mint re-points them (02:07:55 item 3) |
| f4 | Seven-script owner-DSN fallbacks recorded, not fixed here | MET | process-backlog row (22:14 GMT, WK-1178), predicate given |
| g1 | GOLDEN_QUOTE_MISMATCH planted, not a permission read failure (02:10:01) | MET | LG line 231 cites `journey.py:986` `regression("D1", rv1, expect_failure=True)`; `permission denied` = 0 across service logs; (e) `pg_stat_activity` lines in LG show API/worker as `gip_app_login` |
| g2 | Gate STANDS under 1(f) (03:28:21) | MET (read, not re-run) | to-lead 03:28:21: 13 FAILED = exactly the 1(f) set; skipped 21 ≤ 21; `rc_role=0`, `rc_skip=0`, demo rc 0 on the login DSN; I did not re-read the gate logs |
| g3 | Frontend untouched | MET | empty diff, above |

### Non-blocking findings

- **N1 — LG 8237 lacks the gate-of-record lines and the merge-base sha.** At `58fdb69f` the ledger ends with S1a-5's compose lines and the gate-script finds; the gate result, the END row, the three `pg_roles` rows and the merge-base `3cd5fcf7ee514db1ae8ab681d7cacc1761945091` (which the maintainer asks the LG to name, 03:28:21) are only in the channel. Append them as dated lines at the fold; the LG is append-only. Evidence: `grep -n -E '6800|58fdb69f|13 failed|3cd5fcf7' <the LG 8237 file>` = no match.
- **N2 — the CI `provision` step is not in the gate-summary stage list.** `python.yml` adds `id: provision` (`continue-on-error: true`, after migrate) but `Gate summary` still lists `ruff mypy import_linter minio migrate pytest contracts req_coverage` (`S_*` env, lines 352–362), against the file's own rule at lines 338–342 ("a stage added above and forgotten here is invisible to the verdict"). A failed provision is not silent — the `database` fixture then FAILS (FD 8256) and `pytest` goes red — but it is reported as a pytest failure, not as a provision failure. Fix in a follow-on or at the fold.
- **N3 — `OWNER_FIXTURE_USERS` is a ledger for 23 of its 130 rows, not a fixture gate.** 23 rows (20 `migration`, 3 `owner-subject` in `test_migration_*`/`test_approval_guard_trigger`/`test_tenant_binding`) are tests that build their own scratch-DB engines and never take `owner_database`, so "enforced by construction" (`owner_database`'s docstring) holds for the other 107. The closed-tuple test checks that the file exists, not that the function exists or takes the fixture; my AST walk found all 130 functions present. The three FR-420 sweep tests carry the label `owner-subject` while their reason is OQ 8252 (not a tamper probe) — justified by the reason text, loosely by the label. Not blocking: nothing is hidden from the app path.
- **N4 — SKILL `Verified` date is scoped to one line.** `python-test/SKILL.md`: "Verified: 2026-10-25 against s1a-fixA on ae9445aa … for that line only". The ruling at to-lead "2026-10-25 23:10:31 GMT" (iv) asked for the date refreshed; it is, scoped honestly. The line's tree is `ae9445aa`, not the gate head.

Accepted, not findings: path (ii) of FD 8256 (no migrations) is not driven DB-free (accepted at 02:07:55 item 4; the gate's `rc_skip=0` and `alembic heads` cover it); `gip_app_login` persists on the shared cluster (accepted 01:53:21).

## Owed to the mint (to-lead 03:28:21 map: 1941–1946)

1. **SL-1942** (SL 8246) as a new slice row under WK-1178, `plans: [PL-1769, PL-1927]`, `relates:` SL-1771, FD-1729, PL-1927 and the slice's minted ids; roadmap has no SL 8246 row at the gate head (`grep -c` = 0).
2. **SL-1771 → `retired`** with the dated re-cut line (02:07:55 item 2); S1b's id is not written, named as "PL-1927's S1b".
3. **LG 8237 → LG-1941**: `slice:`, `plans:`, `relates:`, title and filename re-pointed through `mint-repoint.py` (dry run to the maintainer), then N1's lines appended.
4. **Code-hit template minus (ii)** (02:39:03 item 5), `quote-parity rc=0` quoted. Hits at `58fdb69f` outside `docs/`: `backend/tests/conftest_db.py:475,480,485` (`OQ 8252` strings in `OWNER_FIXTURE_USERS`); `conftest_db.py:1004,1034,1100` (`FD-8256` docstrings); `backend/tests/test_blobs.py:232` (`OQ 8252`); `backend/tests/test_conftest_db_unreachable.py:1` (`FD-8256`). Mint targets: OQ 8252→1943, OQ 8255→1944, FD 8256→1945, RS 8257→1946.
5. OQ-8252/OQ-8255 rows in `open-questions.md`, `07-platform.md` §10, `01-data-management.md` §10 and the two roadmap gate rows, re-pointed to the minted ids; the FD 8256 register row and essay cite the minted SL id.
6. N1's gate lines and the merge-base sha; N2 as a follow-on or at the fold.
7. After the fold: re-merge, the 13 + audit-docs 0, per 03:28:21.
