-- The application's login role (FD-1729; df53696a2682:61-63: "Deployment creates a login
-- role and grants it membership"). Idempotent. Never a superuser, never an owner.
-- SUPPORTED PROVISIONER: A SUPERUSER, AND ONLY ONE (#1760 S6b). A CREATEROLE role without
-- SUPERUSER cannot run this file (ALTER ROLE ... NOSUPERUSER below is refused for it, whatever
-- the role's state) and cannot revoke a membership another role granted. Refused here, first.
DO $do$
BEGIN
  IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) THEN
    RAISE EXCEPTION 'the login-role provisioner must run as a superuser: % is not one', current_user;
  END IF;
END
$do$;
DO $do$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gip_app') THEN
    CREATE ROLE gip_app NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gip_app_login') THEN
    CREATE ROLE gip_app_login LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
      NOBYPASSRLS INHERIT;
  END IF;
END
$do$;
-- Converge, not only create (plan review R7, 2026-10-14): a role that already exists with
-- CREATEROLE, CREATEDB or REPLICATION is reset here on every run.
ALTER ROLE gip_app_login LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
  NOBYPASSRLS INHERIT;
-- Converge gip_app too (FD-1951, SL-1962): a pre-existing gip_app keeps no attribute the
-- login role could inherit.
ALTER ROLE gip_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
-- RESET ALL DISCARDS EVERY ROLE-LEVEL SETTING AN OPERATOR HAS SET ON THESE TWO ROLES
-- (search_path, session_replication_role, work_mem, ...), on purpose: a role setting is a
-- route around the guard (FD-1951 medium 4; to-lead 2026-10-26 13:12:34 GMT, item 4 (a)).
-- The first pair clears the role-wide settings; the DO block clears the ones made IN DATABASE.
ALTER ROLE gip_app_login RESET ALL;
ALTER ROLE gip_app RESET ALL;
DO $do$
BEGIN
  EXECUTE format('ALTER ROLE gip_app_login IN DATABASE %I RESET ALL', current_database());
  EXECUTE format('ALTER ROLE gip_app IN DATABASE %I RESET ALL', current_database());
END
$do$;
ALTER ROLE gip_app_login VALID UNTIL 'infinity' CONNECTION LIMIT -1;
ALTER ROLE gip_app VALID UNTIL 'infinity' CONNECTION LIMIT -1;
-- THE NEXT BLOCK REVOKES EVERY OTHER MEMBERSHIP HELD BY THESE TWO ROLES, on purpose (#1760):
-- RE-RUNNING THIS FILE REMOVES ANY ROLE AN OPERATOR OR DEPLOYER GRANTED TO gip_app_login OR
-- gip_app BY HAND, whoever granted it. A membership kept silently keeps granting the
-- application whatever that role holds. If the provisioning role may not revoke one, the run
-- FAILS and names the role pair, as it does when a grant made through a membership being
-- revoked depends on it (never CASCADE). Roles that are members OF gip_app are not touched.
-- THE CALLER MUST RUN THIS FILE IN ONE TRANSACTION: provision-app-role.py does, in one
-- conn.transaction(). Other sessions then see only the committed end state, never the pair
-- revoked, and a failed final assertion rolls every change back.
-- GRANTED BY is load-bearing: a membership row is per grantor, and a plain REVOKE removes only
-- the row the current role granted.
DO $do$
DECLARE
  m record;
BEGIN
  FOR m IN
    SELECT r.rolname AS role_name, u.rolname AS member_name, g.rolname AS grantor_name
    FROM pg_auth_members a
    JOIN pg_roles r ON r.oid = a.roleid
    JOIN pg_roles u ON u.oid = a.member
    JOIN pg_roles g ON g.oid = a.grantor
    WHERE u.rolname IN ('gip_app_login', 'gip_app')
  LOOP
    BEGIN
      EXECUTE format('REVOKE %I FROM %I GRANTED BY %I', m.role_name, m.member_name, m.grantor_name);
    EXCEPTION
      WHEN insufficient_privilege THEN
        RAISE EXCEPTION 'cannot revoke membership of role % in role %: no privilege',
          m.member_name, m.role_name;
      WHEN dependent_objects_still_exist THEN
        RAISE EXCEPTION 'cannot revoke membership of role % in role %: a grant made through it depends on it',
          m.member_name, m.role_name;
    END;
  END LOOP;
END
$do$;
-- The pair gip_app -> gip_app_login is revoked too, from EVERY grantor (#1760 S6b): a row
-- another grantor made can carry ADMIN OPTION or SET TRUE, and the GRANT below rewrites
-- only one row. PostgreSQL records the bootstrap superuser, not current_user, as grantor
-- when a superuser grants, so no grantor-based exemption can be relied on.
-- SET FALSE: the login role never needs SET ROLE gip_app; it inherits gip_app's grants.
GRANT gip_app TO gip_app_login WITH INHERIT TRUE, SET FALSE;
-- A SECURITY DEFINER function runs with its OWNER's rights, so one owned by any role other than the
-- owner of `blobs` (the migrating role, which owns every table) is an elevation path the migrations
-- never made (#1550 (c), slice 3b). Refused here, naming the function and its owner. Skipped on a
-- fresh volume, where the migrations have not run: no table, no function. It sits BEFORE the end-state
-- assertion below, which stays the file's last block.
DO $do$
DECLARE
  f record;
BEGIN
  IF to_regclass('public.blobs') IS NOT NULL THEN
    FOR f IN
      SELECT p.proname AS function_name, o.rolname AS owner_name
      FROM pg_proc p
      JOIN pg_roles o ON o.oid = p.proowner
      WHERE p.pronamespace = 'public'::regnamespace
        AND p.prosecdef
        AND p.proowner <> (SELECT relowner FROM pg_class WHERE oid = 'public.blobs'::regclass)
    LOOP
      RAISE EXCEPTION 'SECURITY DEFINER function % is owned by %, not by the owner of blobs',
        f.function_name, f.owner_name;
    END LOOP;
  END IF;
END
$do$;
-- The end state is asserted, not assumed: exactly one row for the pair, INHERIT only.
DO $do$
BEGIN
  IF (SELECT count(*) FROM pg_auth_members
       WHERE roleid = 'gip_app'::regrole AND member = 'gip_app_login'::regrole) <> 1
     OR NOT EXISTS (SELECT 1 FROM pg_auth_members
                     WHERE roleid = 'gip_app'::regrole AND member = 'gip_app_login'::regrole
                       AND inherit_option AND NOT admin_option AND NOT set_option) THEN
    RAISE EXCEPTION 'membership of role gip_app_login in role gip_app is not exactly one INHERIT-only row';
  END IF;
END
$do$;
-- No credential here: `scripts/provision-app-role.py` sets it, as a SCRAM verifier.
