---
id: FD-2093
family: finding
title: the P2 NFR sweep seeds through the app DSN, so least privilege (FD-1729) blocks it
status: closed
created: 2026-11-08   # original date 2026-11-07, draft under working id 8403; minted 2026-11-08 as FD-2093
owner: auditor
tree: bfeedd9a282ee0180be54bf201b17930fc4bd2d0   # origin/main at the draft; the S2 runs were at 6f958137, and the instrument is the same file at both (git diff 6f958137 bfeedd9a -- scripts/measure-p2-nfr-sweep.py is empty)
corrected_by: []
relates: [WK-1178, SL-1736, LG-2003, PL-1735, FD-1729, FR-44, NFR-1443, NFR-468]
---

# FD-2093 — the P2 NFR sweep seeds through the app DSN, so least privilege (FD-1729) blocks it

*Disclosure: drafted under working id 8403; minted as FD-2093 on 2026-11-08, in the SL-2096 mint (WK-1178).*

*(Draft under working id 8403, on `draft/pl-fd8403-2026-11-07`. It is filed with PL-2095's mint, not before. The severity, the owner and the title are the maintainer's, to-lead "2026-11-07 18:49:24 GMT" item I. The one-way corpus joins by the dated line of to-lead "2026-11-07 18:54:18 GMT" item (1).)*

## Finding

`scripts/measure-p2-nfr-sweep.py` builds one database handle, `_Env.database = Database(self.settings)`
(`:514`), on `GIP_DATABASE_URL`, and passes the same `self.settings` to `create_app` (`:516`). It then
calls `seed.grant_demo_principals(env.database, …)` at three places: `:604` (`_fremtpl2`), `:661`
(`_one_way`, a new workspace for the wide corpus) and `:897` (`_cells_diff`, a new workspace).
`grant_demo_principals` (`examples/fremtpl2/seed.py:346`) creates the workspace row, the built-in roles
and the members. Since FD-1729 (`#1398` `1e0a8abb`, `#1399` `eaddb4d9`, both 2026-10-26), those
tables are read-only to the application role: `workspaces`, `workspace_members`, `roles` and
`role_assignments` are `READ` in `_TARGET`
(`backend/migrations/versions/b7e4c2a91d36_application_role_grants.py:146`, `:147`, `:163`, `:165`), and
`:17-18` of the same file says "the seed writes them as the owner".

**So no single `GIP_DATABASE_URL` can serve both uses:**

- **As `gip_app_login`**, the seed is refused: `permission denied for table workspaces`.
- **As the owner**, `create_app`'s lifespan refuses to start: `await database.assert_least_privilege()`
  (`backend/src/app/main.py:114`) raises `LeastPrivilegeError` (`backend/src/app/db/immutability.py:171`).

`seed.run` already has the right split (`seed.py:448-459`, FD-1729's PL-1769 Task 0): it builds an
`owner_database` from `settings.migration_database_url` for `grant_demo_principals` alone, and keeps every
governed step on the application's connection. The harness predates that split. Its code was written
before FD-1729 merged; its smoke and its one NFR-1443 reading ran as the owner on 2026-10-22
(`LG-2003`, "Grant 4"). It merged on 2026-11-04 (`#1429`, `c796e4c0`), after FD-1729. No test reaches the
database arms (`tests/test_measure_p2_nfr_sweep.py` is DB-free, `LG-2003` A4), so nothing saw the wall
before S2.

`:604` passed in S2's storage run only because `seed.run` had just created that workspace and its
members as the owner. `ensure_workspace` and `ensure_member` then only read. That call has the same
shape, and is in the same fix.

**Not a mispricing, and no data is wrong.** The harness stops before any timed phase. The cost is that
NFR-1443 (cells-diff) and NFR-468 (one-way) **could not be measured in S2**. `LG-1760` and `CR 8315` /
`CR 8314` carry "BLOCKED, instrument" until S3, not UNMET (to-lead "2026-11-07 18:49:24 GMT").

## Evidence

Logs on the shared box, `~/gi-pricing-plan.local/scratch/nfr-bench-1/s2/`, each with `head=6f958137b227f1a9499a4ab00caf40f79ba2439c`
as its first line and `rc=1` as its last. Every run was on its own `createdb -T gipricing` copy,
`gipricing_nfrs2_<item>`, migrated to `b7e4c2a91d36` (`I-prep*.log`, `J-*-prep.log`).

- **I, attempt 1** (`I-cellsdiff-attempt1-authfail.log`), `GIP_DATABASE_URL` as `gip_app_login`
  before the role's password was provisioned (`bringup-5-provision.log`): `:36`
  `File ".../examples/fremtpl2/seed.py", line 364, in grant_demo_principals`, called from
  `measure-p2-nfr-sweep.py", line 897, in _cells_diff`; `:166`
  `asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "gip_app_login"`.
  This is set-up order, not the defect. It is recorded so the S3 bring-up provisions first.
- **I, attempt 2** (`I-cellsdiff-attempt2-loginrole-permdenied.log`), as `gip_app_login`: `:90` line 897,
  `in _cells_diff` → `:93` `seed.py", line 364, in grant_demo_principals` → `:34`
  `asyncpg.exceptions.InsufficientPrivilegeError: permission denied for table workspaces`.
- **I, attempt 3** (`I-cellsdiff.log`), as the owner (`I-window.sh:14` exports
  `GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@…/$DB`): the seed at `:897` succeeds, and
  then `:32` `line 901, in _cells_diff` → `:200` `app/main.py", line 114, in lifespan` → `:204`
  `immutability.py", line 176, in assert_least_privilege` → `:208`
  `app.db.immutability.LeastPrivilegeError: the database connection is, or is a member of, gipricing (superuser), pg_database_owner (owns schema public), … Connect as the application login role (scripts/provision-app-role.py).`
- **J one-way** (`J-oneway.log`), as `gip_app_login` with the owner as `GIP_MIGRATION_DATABASE_URL`
  (`db-window.sh:16`): `seed.run` succeeds through its own owner split, and then `:189` `line 661, in _one_way` →
  `:192` `seed.py", line 364, in grant_demo_principals` → `:196`
  `app/platform/workspaces.py", line 45, in ensure_workspace` → `:133`
  `asyncpg.exceptions.InsufficientPrivilegeError: permission denied for table workspaces`.

**The predicate for "three places"** at `bfeedd9a`:
`git grep -n 'grant_demo_principals(' -- scripts/measure-p2-nfr-sweep.py` prints `:604`, `:661` and `:897`.

## Disposition

MEDIUM, owner WK-1178: it blocks a measurement and prices nothing (to-lead "2026-11-07 18:49:24 GMT").
**Fix before Thu 12 Nov**, after the pin in the queue, in SL-2096 under PL-2095. The harness seeds through
a separate owner DSN and serves through the app DSN. The app's runtime code is not touched. The seed URL
never names the template. Red first on a `-T` copy. The gate is on the maintainer's word. I and J
(one-way) then run in S3 on Fri 13 Nov on the frozen tree. If J's or K's arms hit the same wall, they
join this finding by dated line: one finding, one fix.

***Resolved 2026-11-08*** — closed in place 2026-11-08 by the executor, as the closing act of the mint of SL-2096 (WK-1178, LG-2097, PL-2095; this PR, its number, squash commit and merge date are written at the merge's date-of-record), on the GO to-lead "2026-11-07 19:10:01 GMT", from the audit of SL-2096 adopted by the lead (from-lead "2026-11-08 00:13:01 GMT"; the audit section is in LG-2097). Delivered remedy: `scripts/measure-p2-nfr-sweep.py` seeds through `_Env.owner_database` (built from `GIP_MIGRATION_DATABASE_URL`, as `seed.py` builds it) via the single `_grant`, and serves through the app DSN; `dsn_failure` refuses an unset owner DSN, the template database `gipricing`, a different host/port/database, and one user on both DSNs. Red first by assertion (LG-2097: "the seed was handed the APP database"), A5 mutation proofs reverted; window W: R0 `permission denied for table workspaces`, head rc=0 for `cells-diff`, `one-way` and `storage` (100000 rows, by the ruling "2026-11-07 21:03:10 GMT"). Gate evidence: LG-2097 (gate END `2026-11-08T03:29:03+00:00`, `rc=1`, standing under item 31).
