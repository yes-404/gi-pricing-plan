---
id: FD-1951
family: finding
title: The startup least-privilege check misses CREATEROLE and ADMIN OPTION, two routes to the owner
status: closed
created: 2026-10-26   # drafted 2026-10-26 under working id 8265
owner: auditor
tree: 372bfe64197db2377c24f788f44381d258cdc38f
corrected_by: []
relates: [WK-1178, FD-1729, PL-1927, PL-1769]
---

# FD-1951 — The startup least-privilege check misses CREATEROLE and ADMIN OPTION, two routes to the owner

## Finding

**HIGH; owner WK-1178; fix before close, by Fri 31 Oct 2026.** *[Correction 2026-10-26: the weekday is Saturday (2026-10-31); the date governs.]* Authority: the maintainer's entry "2026-10-26 11:38:32 GMT —
Maintainer: postgres-pro review STOP — RULED (b)" (`to-lead.md`), condition (i): "FD-1951 reserved, HIGH, owner WK-1178, fix
before close". Filed under working id 8265.

`Database.assert_least_privilege` (S1b of FD-1729, branch `draft/s1b-fd1729` at `372bfe64`) refuses to start a process whose
connection role is an owner, a superuser or a role that reaches either, and refuses a disabled or altered artifact trigger. Its
ownership predicate `P_OWN` decides "can this role become the owner" from `pg_has_role(current_user, r.oid, 'MEMBER')`,
`rolsuper`, `rolbypassrls` and table ownership. Two ways to become the owner role are invisible to it, so a misconfigured
deployment would print "least privilege holds" while the application role could reach the owner.

## Evidence

### The two HIGH routes

The source is the postgres-pro review of Step 7.2 of PL-1769, static, at `4a55dd22`, quoted whole in LG-1947's dated section
"PL-1769 Step 7.2: postgres-pro review of the grant map and the provisioning".

- **CREATEROLE** (`backend/src/app/db/immutability.py:42-57`, `P_OWN` never reads `rolcreaterole`). On PostgreSQL 16 a role with
  CREATEROLE can alter the password of any non-superuser role it administers and can grant itself membership in roles it has ADMIN
  on: a route to the owner role. A login role created or altered with CREATEROLE passes `P_OWN`.
- **ADMIN OPTION** (`pg_auth_members.admin_option` is never read). A role with admin on the owner group but no membership fails
  the `MEMBER` test of `pg_has_role` and passes `P_OWN`, yet can run `GRANT <owner> TO self`.

### The five same-class mediums

All five are review findings of severity medium that the same widening addresses or must at least decide.

1. **Predefined roles** are not checked: membership in `pg_write_all_data` bypasses the grant map; `pg_execute_server_program`,
   `pg_write_server_files` and `pg_read_server_files` are further routes (`P_OWN` returns no row for any of them).
2. **Parameter privileges.** PostgreSQL 15 and later allow `GRANT SET ON PARAMETER session_replication_role` to a non-superuser,
   which bypasses origin-only triggers without ownership or superuser. `pg_parameter_acl` is never read and nothing tests it.
3. **Ownership of the trigger functions and of schema `public`** (`immutability.py:50-53` checks only relkind `r` and `p` in
   `public`). A function owner can `CREATE OR REPLACE` a guard body, which the md5 pin catches only at the next start; owning
   `public` allows shadowing objects.
4. **`gip_app` is never converged** (`deploy/postgres/app-login-role.sql:5-7` creates it only when absent). A pre-existing
   `gip_app` with LOGIN, CREATEROLE, CREATEDB or REPLICATION keeps them and the login role inherits them; `P_OWN` catches only
   SUPERUSER and BYPASSRLS on it.
5. **Memberships and role settings are not reset** (`app-login-role.sql:18` only adds the `gip_app` membership). A hand-granted
   owner membership stays (the startup check refuses it; the provisioner does not undo it); `ALTER ROLE … SET search_path` or
   `session_replication_role`, `VALID UNTIL` and `CONNECTION LIMIT` are not reset.

## The mitigation as it stands

Neither HIGH route is present in the provisioned state. The converging statement, `deploy/postgres/app-login-role.sql:16-17`
and the membership at `:18`, verbatim:

```
ALTER ROLE gip_app_login LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
  NOBYPASSRLS INHERIT;
GRANT gip_app TO gip_app_login;
```

The plain `GRANT` carries no `WITH ADMIN OPTION`. Verified in a throwaway `postgres:16-alpine` (`s1b-pgv-54e0fca0`) at the gate
head `54e0fca0`, after `provision-app-role.py --allow-default-password` and `alembic upgrade head` as the owner:

```
SELECT rolname, rolcreaterole, rolsuper FROM pg_roles WHERE rolname LIKE 'gip_app%' ORDER BY 1;
    rolname    | rolcreaterole | rolsuper 
---------------+---------------+----------
 gip_app       | f             | f
 gip_app_login | f             | f
(2 rows)

SELECT roleid::regrole, member::regrole, admin_option FROM pg_auth_members WHERE roleid = 'gip_app'::regrole;
 roleid  |    member     | admin_option 
---------+---------------+--------------
 gip_app | gip_app_login | f
(1 row)
```

The residual is therefore an out-of-band misconfiguration (a CREATEROLE login role, or ADMIN OPTION granted by hand), not the
provisioned state. The risk is a false green of the FD-1729 class: the guard says least privilege holds when a route to the owner
exists.

## Severity

**HIGH**, as ruled (the entry above). Misconfigured, either route reaches the owner silently and the guard would say "least
privilege holds". Not blocking S1b: the deployed state does not contain the route, FR-44's ruled line (PL-1769 Step 7.1) names the
refusal set S1b delivers (an owner, a superuser, a disabled artifact trigger) and S1b meets it, and widening the set to "any role
that can become the owner" is a spec change first (CLAUDE.md §0) and a red-first slice with its own gate (§13). FR-44's line
stands unchanged; this finding, not the FR, carries the residual until the follow-up slice amends FR-44.

## Remedy

A follow-up slice under PL-1927 (a dated PL delta row, its SL reserved at that row) that:

1. widens `P_OWN` to read `rolcreaterole` and `pg_auth_members.admin_option`;
2. converges `gip_app` (`ALTER ROLE gip_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`) and states the
   membership `WITH INHERIT TRUE, SET FALSE`;
3. amends FR-44 by a dated line;
4. proves each refusal red-first on a planted role.

**Owner WK-1178; deadline Fri 31 Oct 2026** *[Correction 2026-10-26: the weekday is Saturday (2026-10-31); the date governs.]*, inside the P2 code-complete ETA and before the Wed 4 Nov freeze. FD-1729 still closes
at S1b's PR; its close line cites this finding as the residual that supersedes nothing and widens the guard. The mediums for
predefined roles, parameter privileges and function/schema ownership are for the follow-up slice to settle in or out of its scope,
by a dated line.

## Provenance

Found by the postgres-pro review at S1b's Step 7.2, whole in LG-1947's dated section; the STOP and its ruling are the
maintainer's entry "2026-10-26 11:38:32 GMT" (`to-lead.md`), with the lead's confirmation by reading `P_OWN`.

## Disposition

Closed 2026-10-29 in place, citing this PR (S1c, SL-1962). Residual limb in a record: FD-1963 (the membership strip, MEDIUM, WK-1178).
Filed under working id 8265.

## Correction — 2026-10-26: HIGH-2 is refuted by measurement

*(Dated 2026-10-26, on the maintainer's entry "2026-10-26 13:50:37 GMT" (Q2), which reproduced the
lead's probe. The text above stays as filed.)* The ADMIN OPTION route under "The two HIGH routes"
does **not** hold on PostgreSQL 16. The measurement used a throwaway `postgres:16-alpine`
(PostgreSQL 16.15), removed after: `GRANT owner_grp TO gip_app_login WITH ADMIN TRUE, INHERIT FALSE,
SET FALSE` gives `pg_auth_members` admin t / inherit f / set f, and
`pg_has_role('gip_app_login','owner_grp','MEMBER')` = **t** (USAGE f, SET f). The plain
`WITH ADMIN OPTION` grant also gives MEMBER = t. On PostgreSQL 16 any `pg_auth_members` row counts as
MEMBER, so the base `P_OWN` (`immutability.py:42–57`, `pg_has_role(current_user, r.oid, 'MEMBER')`)
already refuses an admin-only route to an owner. The residual is **HIGH-1 (CREATEROLE)** plus the
five same-class mediums. The severity stays **HIGH**, on HIGH-1. Remedy item 1 narrows accordingly: `P_OWN` reads
`rolcreaterole`, and the two ADMIN forms are controls in PL-1927 S1c (acceptance 21). The postgres-pro
review stays as filed evidence (LG-1947, Step 7.2 section).
