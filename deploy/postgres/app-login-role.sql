-- The application's login role (FD-1729; df53696a2682:61-63: "Deployment creates a login
-- role and grants it membership"). Idempotent. Never a superuser, never an owner.
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
-- FAILS and names the role pair. Roles that are members OF gip_app are not touched.
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
      AND NOT (r.rolname = 'gip_app' AND u.rolname = 'gip_app_login')
  LOOP
    BEGIN
      EXECUTE format('REVOKE %I FROM %I GRANTED BY %I', m.role_name, m.member_name, m.grantor_name);
    EXCEPTION WHEN insufficient_privilege THEN
      RAISE EXCEPTION 'cannot revoke membership of role % in role %: no privilege',
        m.member_name, m.role_name;
    END;
  END LOOP;
END
$do$;
-- SET FALSE: the login role never needs SET ROLE gip_app; it inherits gip_app's grants.
GRANT gip_app TO gip_app_login WITH INHERIT TRUE, SET FALSE;
-- No credential here: `scripts/provision-app-role.py` sets it, as a SCRAM verifier.
