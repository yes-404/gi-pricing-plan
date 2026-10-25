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
GRANT gip_app TO gip_app_login;
-- No credential here: `scripts/provision-app-role.py` sets it, as a SCRAM verifier.
