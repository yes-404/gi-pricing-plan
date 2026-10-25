---
id: LG-8248
family: ledger
title: WK-1178 slice S1b — FD-1729 part 2, the startup refusal, the trigger-tamper proof and the exact grant map (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-25            # working id 8248, unminted
owner: executor
tree: df215d55b118396b2ab6edcba9c645ee253d9eaf   # S1a's seam head, the code the red list below is read against; this file's branch starts at origin/draft/s1a-fd1729 = f75906b9, its ancestor
phase: P2
work: WK-1178
plans: [PL-8227, PL-1769]
corrected_by: []
relates: [FD-1729, PL-8227, PL-1769, FR-44]
---

# LG-8248 — WK-1178 slice S1b: FD-1729 part 2, the startup refusal, the tamper proof and the exact grant map

Working id 8248 (LG), reserved 2026-10-25 22:46:21 UTC by lead 28 in `eta.md` ("**8248** LG = S1b (PL 8227 row 4) slice ledger, drafted by the S1b planner"). The slice has **no `SL-` working id yet**: the lead reserves it at S1b's GO, and `slice:` is filled then (the form LG 8242 uses). Drafted by the planner seat `plan-s1b` under the maintainer's entry "2026-10-25 22:45:03 GMT" item (3) (*"S1b plan prep (PL 8227 row 4: startup refusal, tamper proof, exact grant map) — a planner seat drafts the S1b LG and red-test list against S1a's seam head, no runs"*). **Nothing below was run.** Every "red at the seam head" line is read from the code at `df215d55`, not measured; the executor measures each one at S1b's base and writes its line here, `head=` first and `rc=` last.

**GO:** pending — S1b GO not yet requested.
**MERGE-ACK:** pending — S1b GO not yet requested.

## Tasks

### Scope

PL 8227 (working id; branch `draft/pl-8227` @`d1ac13aa`), section "## Tasks", row 4, verbatim:

> | 4 | **S1b** — FD-1729 part 2: the startup refusal, the tamper proof, the exact grant map | Tasks S1b-0 to S1b-4 (`PL-1769` S-b Tasks 1.5, 4, 5.2, 7; 6 again only if S1b edits `deploy/`) | `01` §3: FR-44 | S1a merged; a gate slot for the full gate; **merged before the 4 Nov code freeze** | A | **yes** | 1 day |

Its task section, "### S1b — FD-1729 part 2 (`PL-1769` S-b, re-cut)", verbatim:

> - [ ] **S1b-0.** Re-read at S1b's base (S1a merged); Task 0's census is S1a's `LG-`, not re-run.
> - [ ] **S1b-1.** Task 4 (`test_application_role.py` reds first, then `Database.assert_least_privilege()`).
> - [ ] **S1b-2.** Task 5, Step 5.2 (the exact grant map test).
> - [ ] **S1b-3.** Task 1, Step 1.5 (compose binds to `127.0.0.1`, its red; applied to the shared stack only as the GO-time act the maintainer names); then Task 6 again because this edits `deploy/`.
> - [ ] **S1b-4.** Task 7 (`FR-44`'s dated line naming both slices, the postgres-pro review, the full gate); the `LG-`.

Its acceptance, PL 8227 "## Acceptance Standard", items 8 to 11 (S1b):

> 8. R-b1, R-b1b, R-b2, R-b5, R-b6 and the four trigger-tamper routes (`PL-1769` Task 4.1), and the compose-bind red (Step 1.5), red on S1b's base (S1a merged) by cause, in S1b's `LG-`.
> 9. `PL-1769` Acceptance 9 holds: `uv run pytest backend/tests/test_application_role.py backend/tests/test_artifact_immutability.py backend/tests/test_provision_app_role.py -q` green; `git grep -n "pg_has_role" -- backend/src` prints exactly one hit, in `app/db/immutability.py`, with `'MEMBER'`; the pinned trigger-hash test green; the exact grant map grants no `DELETE` on `jobs` or `outbox` unless the `LG-` records a caller.
> 10. `FR-44` (`01-data-management.md:106`) carries `PL-1769` Step 7.1's dated line, completed with the date and both slice ids; the postgres-pro review is in the `LG-`; the full gate rc table is all 0.
> 11. S1b's squash merge on `main` is dated before 2026-11-04 (`git log -1 --format=%cI <squash sha>`).

Requirement: `01-data-management.md` §3, `FR-44` (one id). Finding: `FD-1729`. Rulings it builds on: `PL-1769` DP-14 (b) as amended (plan review R5), DP-19 (a) as amended (R4), DP-20 (a), DP-22 (b), the P-own predicate (R4, R11); and S1a's rulings in `to-lead.md` "2026-10-25 22:04:36 GMT" (throwaway Postgres, option (b); disposition (5): "the 'permission denied' list is the arbiter … a REVOKE never widens"), "22:17:05 GMT" (no INSERT grant to the application role for a test seed; column privileges named exactly), "22:24:25 GMT" (one owner seam in `conftest_db`; the full `backend/tests` suite in a throwaway is the pre-gate proof) and "22:38:42 GMT" item (3) (the seam `seed_as_owner` / `grant_roles_as_owner` accepted at `df215d55`).

**Dependency.** S1b starts from a base with S1a merged (row 4, "Depends on"). The red list below shows why that is a code dependency and not only an order: S1b's new tests use S1a's `owner_database` fixture and must be listed in S1a's `OWNER_FIXTURE_USERS` (`backend/tests/conftest_db.py:188` at `df215d55`); the reds R-b1, R-b5 and R-b6 change cause once S1a's flip is in (open point O1); and the exact map transcribes the grants S1a's one migration sets (`b7e4c2a91d36_application_role_grants.py:99-166`, `_TARGET`). Drafting the tests on S1a's branch head before S1a merges is possible without a slot; **measuring** the reds by cause is not, because "S1b's base" does not exist until S1a's squash is on `main` (open point O4).

### Task list

The red list (PL 8227 S1b-1, S1b-2; `PL-1769` Task 4.1, Step 5.2). Negative tests first: every item that asserts a refusal comes before the ones that assert a fact. Columns: the test (file :: name), the one assert it makes, why it is red at `df215d55` (the missing or wrong path, `file:line` at `df215d55`), and the clause it proves. **DB-backed (throwaway)** marks a test that needs a Postgres: per 22:04:36 it runs in a throwaway `postgres:16-alpine` on `127.0.0.1`, never the shared cluster or `gipricing`, removed with `docker rm -fv`, quoted.

All tests below live in **`backend/tests/test_application_role.py`** (new; absent at `df215d55`), except T8, which is a structural check. Every test that uses `owner_database` is added to `OWNER_FIXTURE_USERS` with the label `owner-subject` (the label S1a defined for "tests that PROVE the owner is refused, or that tamper", `conftest_db.py` comment above `:188`), or the fixture refuses it.

| # | Test (`test_application_role.py` ::) | The assert (one line) | Why red at `df215d55` | Proves | DB |
|---|---|---|---|---|---|
| T1 | `test_the_api_refuses_to_start_as_the_owner` (R-b2), two cases: API, worker | `create_app(<owner DSN settings>)`'s lifespan raises, the message naming `scripts/provision-app-role.py`; importing `app.worker.entrypoint` with the owner DSN raises (in a subprocess, because the module runs `load_settings()` and `asyncio.run(...)` at import) | No least-privilege check exists on either start path: the lifespan's last start check before the probes is `require_tenant_binding` (`backend/src/app/main.py:113`), and the worker's import-time check calls only `require_tenant_binding` (`backend/src/app/worker/entrypoint.py:35-48`). With the owner DSN both start. **This is the one red whose cause is the same at S1b's base as `PL-1769` predicted.** | DP-19 (a); `FR-44` Step 7.1 text "Startup refuses an owner, a superuser …" | **DB-backed (throwaway)**, plus a throwaway MinIO if the refusal is placed after `require_tenant_binding` (it binds the blob bucket); before it, MinIO is not reached (open point O5) |
| T2 | `test_an_inherit_false_membership_of_the_owner_is_refused` (R-b1b), two cases: `INHERIT FALSE` owner member; a non-owner role with `rolbypassrls` | Through `owner_database`, in a rolled-back transaction, `SET LOCAL ROLE gip_scratch_r4`: P-own returns the owner role (case 1) / the bypass role (case 2), and `assert_least_privilege()` on that connection raises | `backend/src/app/db/immutability.py` does not exist (no P-own constant) and `Database` has no `assert_least_privilege` (`backend/src/app/db/session.py:36-81`: `__init__`, `engine`, `session`, `unit_of_work`, `dispose` only) — so it is red by `ImportError`, which is **not** the cause. The by-cause red is `PL-1769` Step 4.1's: the first cut's `'USAGE'` predicate in a scratch edit passes the `INHERIT FALSE` role; that line goes here | P-own (R4); DP-19 (a) | **DB-backed (throwaway)** |
| T3 | `test_a_tampered_artifact_trigger_refuses_startup` (DP-14 (b)), four cases: (i) `DISABLE TRIGGER` (`'D'`), (ii) `ENABLE REPLICA TRIGGER` (`'R'`), (iii) `DROP TRIGGER`, (iv) `CREATE OR REPLACE FUNCTION` with a `RETURN NEW` body | Through `owner_database`, in a rolled-back transaction on one declared table, `assert_least_privilege()` raises naming the table and the trigger | No trigger check exists (same `session.py:36-81`). By-cause red per `PL-1769` Step 4.1: the first cut's `tgenabled = 'D'`-only check in a scratch edit passes (ii), (iii) and (iv); those three lines go here | DP-14 (b) as amended (R5); `06` FR-372 "detectable" framing as `PL-1769` cites it | **DB-backed (throwaway)** |
| T4 | `test_the_application_role_cannot_disable_a_trigger` (R-b5) | Through `database`, `ALTER TABLE factors DISABLE TRIGGER factors_no_modify` is refused with `must be owner of table factors`, and `SET session_replication_role = replica` is refused with `permission denied` | **Predicted GREEN at `df215d55`, not red**: S1a flipped the `database` fixture to the login role (`backend/tests/conftest_db.py:162-180`, `test_database_url()`), which owns nothing (S1a's `test_the_login_role_owns_nothing_and_holds_no_direct_table_privilege`, `test_application_login_role.py:39`). `PL-1769`'s predicted cause ("as the owner, both succeed") is the pre-S1a base. By-cause red only with `GIP_TEST_APP_DATABASE_URL` set to the owner DSN (`conftest_db.py:170`) — open point O1 | DP-14 (a)/(b): the dependency FD-1729 states, shown as a test | **DB-backed (throwaway)** |
| T5 | `test_the_application_role_is_not_superuser_not_owner_and_cannot_bypass_triggers` (R-b6) | Through `database`: `SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user` is `(false, false)`; P-own returns no row; `SET session_replication_role = replica` raises `permission denied to set parameter "session_replication_role"` (wording printed by the red before the green relies on it) | Red only by `ImportError` of the P-own constant (`immutability.py` absent). The `rolsuper` and `SET` halves are **predicted green** at `df215d55` for the T4 reason. By-cause red with the owner override — O1 | the maintainer's 12:18:57 item (2) "NEW", as `PL-1769` R-b6 quotes it | **DB-backed (throwaway)** |
| T6 | `test_the_application_does_not_connect_as_an_owner_or_a_superuser` (R-b1) | Through `database`, P-own (the imported constant) returns no row | Red only by `ImportError` (no constant). Its intended cause, "`current_user` is `gipricing`", is already green at `df215d55`: S1a's `test_the_application_connection_is_the_login_role` (`test_application_login_role.py:31-35`) asserts `gip_app_login`. By-cause red with the owner override — O1 | P-own (R4); DP-19 (a) | **DB-backed (throwaway)** |
| T7 | `test_every_table_grants_the_application_exactly_its_declared_privileges` (Step 5.2) | A written map `{table: (table privileges, {column: column privileges})}` over **every** public table equals, both ways, `information_schema.role_table_grants` and `column_privileges` for `grantee = 'gip_app'`; no `DELETE` on `jobs` or `outbox` | **Predicted GREEN at `df215d55`** if the map is written from what S1a granted: S1a already did Task 5.1, revoking `jobs` and `outbox` `DELETE` (`_PREVIOUS`, `b7e4c2a91d36_application_role_grants.py:69`, `:74`; `_TARGET` `:99-166`; S1a's `test_the_excess_delete_on_jobs_and_outbox_is_revoked`, `test_application_login_role.py:77`). `PL-1769`'s "red on the base for every table Task 5.1 changes" is the pre-S1a base. By-cause red: the same test on a throwaway at `down_revision` `9b3e7c15d4a2` (`alembic downgrade -1`), expected red on every table `_TARGET` changes, `jobs` and `outbox` included — open point O2. The map is **written in the test**, not imported from the migration: a map read from `_TARGET` would be the source checking itself (`CLAUDE.md` §13, "a generated artifact matching its source proves neither correct") | DP-20 (a) as amended (R6, R9) | **DB-backed (throwaway)** |
| T8 | `test_the_pinned_guard_function_hashes_match_the_head` (Step 4.2) | For every trigger on a `_declared("append_only")` or `_declared("guarded")` table, `md5(prosrc)` of its function equals `PINNED_GUARD_FUNCTION_MD5[<function name>]` in `app/db/immutability.py` | The constant and the module do not exist (red by `ImportError`). The values are read from the head database at Task 4, never typed (`PL-1769` Step 4.2). The test has no failing case of its own until shown one: the broken-input proof is one pin altered in a scratch edit, red, line here (`CLAUDE.md` §13: "a check that has never printed a failure has not been tested") | DP-14 (b) as amended (R5): "The function-body hash: adopted" | **DB-backed (throwaway)** |

Structural checks, DB-free, not new tests (PL 8227 Acceptance 9; `PL-1769` Step 4.2):

- **S1. P-own is defined once.** `git grep -n "pg_has_role" -- backend/src` prints exactly one hit, in `backend/src/app/db/immutability.py`, with `'MEMBER'`. At `df215d55`: `git grep -c pg_has_role df215d55 -- backend/src` prints nothing, rc 1 (zero hits). Red now; green when T2/T6's constant lands.
- **S2. `_declared` moves to the application.** `git grep -n "def _declared" -- backend` names `backend/src/app/db/immutability.py`, and `test_artifact_immutability.py` imports it. At `df215d55`: one hit, `backend/tests/test_artifact_immutability.py:43` (and `test_contracts.py:609`'s `_declared_fields`, a different function, which the pattern `def _declared(` excludes). A move, not a behaviour: `test_artifact_immutability.py`'s own tests are its proof, unchanged asserts.

Then, in order (each discharges the step named):

1. **S1b-0** — re-read at S1b's base; quote S1a's census from LG 8237, not re-run.
2. **S1b-1** — T1 to T6 and T8 red, each line here; then `app/db/immutability.py` (P-own, `_declared`, `PINNED_GUARD_FUNCTION_MD5`) and `Database.assert_least_privilege()`, called in the lifespan beside `main.py:113` and inside the worker's `_require_tenant_binding` (`entrypoint.py:35`), never in a Celery signal handler. Green.
3. **S1b-2** — T7 red (O2's form), the map, green.
4. **S1b-3** — see O3: as the base stands, nothing is left to build.
5. **S1b-4** — `FR-44`'s dated line (`PL-1769` Step 7.1, with the date and both slice ids); `postgres-pro` reviews the grant map and the provisioning file (evidence); the full gate, both halves, in a slot; the rc table under Gate.

**Open points needing a ruling** (none is decided here; `planner.md`: the planner rules nothing).

- **O1 — R-b1, R-b5, R-b6 cannot be red "by cause" at S1b's base as `PL-1769` predicted.** Their predicted cause is "the application connects as `gipricing`", which S1a removes. At S1b's base, T4 is green, and T5 and T6 are red only by `ImportError`. PL 8227's own acceptance preamble names this: "a matching failure with a different cause is a plan defect, reported to the lead." Options: **(a)** show each by-cause red with `GIP_TEST_APP_DATABASE_URL` set to the owner DSN in the throwaway (S1a's own override, `conftest_db.py:170`), then the green on the default login role; **(b)** cite S1a's red lines in LG 8237 (measured at `d1d96465`, pre-flip) as their red and record T4 to T6 as regression guards here; **(c)** both. Recommendation: **(a)**: the red is then measured on the test as written at S1b, by the cause the test names, in this ledger, which is what Acceptance 8 asks.
- **O2 — Step 5.2's map is green at S1b's base**, because S1a already applied Task 5.1. Options: **(a)** red at `down_revision` `9b3e7c15d4a2` in the throwaway (`alembic downgrade -1`), then green at head; **(b)** red by a planted drift in a rolled-back transaction (`GRANT DELETE ON jobs TO gip_app`, and separately a `REVOKE` of one granted column), which proves both directions of the comparison; **(c)** both. Recommendation: **(c)**: (a) is the base Task 5.1 changed, (b) proves the "both ways" clause on a table S1a did not touch.
- **O3 — Step 1.5 was delivered on `main` by #1378** (`8c3d3013`, "fix(deploy): bind every published compose port to 127.0.0.1 (PL-1769 Step 1.5)"), under the maintainer's 2026-10-25 11:53:23 GMT ruling that `PL-1769` dates in place; `origin/main:deploy/docker-compose.yml` `:39`, `:50`, `:65`, `:91`, `:187` all bind `127.0.0.1`. At S1b's base (S1a merged onto a `main` that has `8c3d3013`), `test_compose_binds.py` is green: **the compose-bind red of PL 8227 Acceptance 8 cannot be produced.** And S1a's branch still has the unbound lines (`df215d55:deploy/docker-compose.yml:39`, `:54`, `:69`, `:95`, `:194`, base `3cd5fcf7`), so S1a's re-merge onto `main` resolves the `deploy/docker-compose.yml` hunks. What remains of Step 1.5 per `PL-1769`'s dated line, *"Task 6's `docker port` check on a running stack"*, then falls in S1a-5 (S1a's compose run, after its re-merge). Options: **(a)** S1b-3 is discharged by #1378 — S1b cites its red from #1378's ledger, edits no `deploy/`, and does not re-run Task 6; the `docker port` read-back is S1a-5's; **(b)** S1b keeps the `docker port` read-back as its own Task 6 run. Recommendation: **(a)**: it is one run and S1a-5 already holds it; S1b then edits nothing under `deploy/`.
- **O4 — order.** Row 4's dependency is "S1a merged". Options: **(a)** strict: S1b's seat starts after S1a's squash merge; **(b)** S1b's tests and code are drafted now on a branch from S1a's pushed head (no slot, DB-free `py_compile` only), and the red lines, the GO request and the gate wait for S1a's merge and a re-merge onto `main`. Recommendation: **(b)**: the 4 Nov freeze is the critical path (PL 8227 "Critical path. S1a then S1b, two DB-window days"), and nothing measured before S1a merges is cited as S1b's red.
- **O5 — where the refusal sits in the lifespan.** `PL-1769` Step 4.2 says "beside `require_tenant_binding` (`main.py:75`, `:100`)"; at `df215d55` that call is `main.py:113`. Before it, an owner-connected process refuses before writing the tenant marker or touching the blob bucket, and T1 needs no MinIO; after it, the marker check runs first. Recommendation: **before**, so that a refused process writes nothing; the executor reports if the tenant-binding order (`require_tenant_binding`'s read-only database check first) makes that wrong.
- **O6 — the `SL-` id and `FR-44`'s "both slice ids".** Step 7.1's text names `SL-1771` only; PL 8227 Acceptance 10 asks for both slice ids; S1b's `SL-` is reserved at its GO. No ruling needed if the lead reserves it at GO; noted so the dated line is not written with one id.

### Gate

pending — S1b GO not yet requested.

### Audit

pending — S1b GO not yet requested.

### Build log

- **2026-10-25 22:52 GMT — `plan-s1b` (planner).** This ledger drafted against S1a's seam head `df215d55b118396b2ab6edcba9c645ee253d9eaf` (tree `d44c30e5`), read via `git show`/`git grep` on the commit, never the `s1a-draft` worktree. `origin/draft/s1a-fd1729` was `f75906b9` at `git ls-remote` (22:50 GMT): **`df215d55` (and its parent `db8dddaa`) was not pushed to origin then**, so this branch starts at `f75906b9`; `df215d55` is a descendant of it (`git merge-base --is-ancestor f75906b9 df215d55` rc 0). No test written, no test run, no code.

## PRs

None yet.
