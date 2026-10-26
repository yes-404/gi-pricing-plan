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
-- Converge gip_app too (FD-1951, SL 8266): a pre-existing gip_app keeps no attribute the
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
-- SET FALSE: the login role never needs SET ROLE gip_app; it inherits gip_app's grants.
GRANT gip_app TO gip_app_login WITH INHERIT TRUE, SET FALSE;
-- No credential here: `scripts/provision-app-role.py` sets it, as a SCRAM verifier.
