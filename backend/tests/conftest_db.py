"""Database fixtures for the integration suite.

These tests run against a **real PostgreSQL**, not SQLite or a mock. Every invariant they
cover — advisory locks, partial unique indexes, `FOR UPDATE SKIP LOCKED`, privilege
enforcement, triggers — is a PostgreSQL behaviour. A test double would assert that the code
calls the right function, which is not the question; the question is whether the database
refuses the write.

**Audit rows cannot be deleted between tests** — that is the whole point of FR-370 — so
isolation comes from giving each test its own `workspace_id` rather than from cleanup.

That is unchanged. `_empty_the_database_after_the_session` below empties the database once
the **whole session** is over, which is a different question: not how one test is isolated
from the next, but whether six days of runs leave 766 MB behind. They did, measured
2026-08-22. Nothing between tests is cleaned, and nothing about the paragraph above moves.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import functools
import hashlib
import os
import warnings
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.session import Database
from app.platform import rbac, workspaces
from app.platform.blobs import BlobStore
from model_schema import ActorKind, Principal, new_uuid7

# The production functions, captured at import: the autouse fixture below replaces the module
# attributes, so anything here that must run the real function (the wrappers, the seeds on the
# owner's session) names these, never `workspaces.ensure_workspace` -- that would recurse.
_ensure_workspace = workspaces.ensure_workspace
_seed_builtin_roles = rbac.seed_builtin_roles

if TYPE_CHECKING:
    from app.db.models import RoleRow, WorkspaceRow
    from app.platform.settings import SettingDefinition

#: The one database every worktree's compose stack provisions by default
#: (`deploy/docker-compose.yml`'s `POSTGRES_DB`) and CI always points
#: `GIP_TEST_DATABASE_URL` at explicitly (`.github/workflows/python.yml`) -- CI has
#: exactly one Postgres instance per run, so there is no second worktree to collide with
#: and the per-worktree derivation below never runs there. Kept as a named constant for
#: what the refusal message below is refusing to silently substitute, not as a fallback
#: `test_database_url()` reaches for on its own any more.
DEFAULT_TEST_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"

#: The application's login role (`deploy/postgres/app-login-role.sql`), a member of `gip_app`.
_APP_LOGIN_ROLE = "gip_app_login"


def _worktree_database_name() -> str:
    """`gipricing_<leaf>_<hash>` -- the same name `dev-commands`'s gate block derives with
    `WT=$(basename "$PWD" | cut -c1-44)_$(pwd -P | tr -d '\\n' | sha1sum | cut -c1-8)`,
    computed here from this file's own path (`backend/tests/conftest_db.py`'s
    great-grandparent is the checkout root) rather than `os.getcwd()`, which a test runner
    invoked from a different working directory would get wrong silently.

    **The leaf alone is not unique** (FD-1196): every job worktree named `<job>/<member>/tree`
    derived `gipricing_tree`, so two gates wrote one database. The hash is of the full
    resolved path, so two checkouts sharing a leaf get different databases. The leaf is cut
    to 44 characters so the whole name stays within PostgreSQL's 63-byte identifier limit,
    beyond which the server truncates silently -- and would cut the hash off.
    """
    root = Path(__file__).resolve().parents[2]
    digest = hashlib.sha1(str(root).encode()).hexdigest()[:8]
    return f"gipricing_{root.name[:44]}_{digest}"


def _worktree_database_exists(name: str) -> bool:
    """Whether database `name` exists on the local Postgres instance.

    `True` when Postgres itself is unreachable -- a developer with no compose stack up is
    not this check's problem; `database()`'s own skip below already covers that case with
    its own message, and this function must not turn an absent stack into a misleading
    "create your database" refusal. `False` only when Postgres answers and the specific
    database is absent, which is the one case this function exists to catch.

    Always runs the check on a fresh event loop in a dedicated thread, never
    `asyncio.run()` directly on the calling thread: `test_database_url()` is called from
    both sync and async fixtures (`database()` below is one), and calling
    `asyncio.run()` from inside a running event loop -- pytest-asyncio's, mid-test --
    raises `RuntimeError: asyncio.run() cannot be called from a running event loop`
    rather than performing the check.
    """
    import asyncpg

    async def _check() -> bool:
        try:
            conn = await asyncpg.connect(
                host="localhost", port=5432, user="gipricing", password="gipricing",
                database="postgres", timeout=5,
            )
        except OSError:
            return True
        try:
            row = await conn.fetchrow("SELECT 1 FROM pg_database WHERE datname = $1", name)
            return row is not None
        finally:
            await conn.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, _check()).result()


@functools.lru_cache(maxsize=1)
def _per_worktree_test_database_url() -> str:
    """`test_database_url()`'s answer when `GIP_TEST_DATABASE_URL` is unset -- the
    per-worktree database, refused loudly rather than silently substituted with the
    shared `gipricing` database.

    Before W37-6, an unset `GIP_TEST_DATABASE_URL` fell back to `DEFAULT_TEST_DSN` (the
    ONE shared `gipricing` database) whenever that database was reachable at all -- which
    it always is, since it is the compose stack's own default. Every gate that skipped
    the per-worktree-database step in `dev-commands`'s gate block therefore ran silently
    against the shared database with no error, and a concurrent worktree's own
    session-scoped teardown (`_empty_the_database_after_the_session` below) truncates it
    out from under this run mid-test (`.claude/skills/python-test/SKILL.md`'s "mutually
    destructive" section) -- exactly the failure the per-worktree-database step exists to
    prevent, made invisible by a fallback that was supposed to be a convenience.

    Cached after the first successful derivation (never after a refusal: `lru_cache`
    does not memoize a raised exception) -- the existence check is a real network round
    trip and every fixture in this module calls `test_database_url()`.
    """
    name = _worktree_database_name()
    if not _worktree_database_exists(name):
        raise RuntimeError(
            f"GIP_TEST_DATABASE_URL is not set, and the per-worktree test database "
            f"{name!r} does not exist yet. Refused rather than silently falling back to "
            f"the shared 'gipricing' database: a concurrent worktree's own "
            f"session-scoped teardown truncates that database out from under this run "
            f"(.claude/skills/python-test/SKILL.md's \"mutually destructive\" section). "
            f"Create this worktree's own database once, before its first gate run "
            f"(.claude/skills/dev-commands/SKILL.md's gate block): "
            f"`PGPASSWORD=gipricing createdb -h localhost -U gipricing -T gipricing "
            f"{name}`, then `GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@"
            f"localhost:5432/{name} uv run alembic upgrade head` -- or set "
            f"GIP_TEST_DATABASE_URL explicitly to override this check."
        )
    return f"postgresql+asyncpg://gipricing:gipricing@localhost:5432/{name}"


def test_owner_database_url() -> str:
    """The **owner's** DSN: migrations, provisioning, per-worktree database creation and
    teardown. `GIP_TEST_DATABASE_URL` overrides it, and its meaning is unchanged -- CI sets
    it to the owner (`.github/workflows/python.yml`).

    **The asymmetry with `test_database_url()` is the point** (FD-1729): the application's
    connection is the login role, the owner's is this one, and only this module calls it
    (a test asserts that). A test that needs the owner takes the `owner_database` fixture,
    which refuses any test not listed in `OWNER_FIXTURE_USERS`.
    """
    override = os.environ.get("GIP_TEST_DATABASE_URL")
    if override:
        return override
    return _per_worktree_test_database_url()


def test_database_url() -> str:
    """The **application's** DSN: the same per-worktree database as `test_owner_database_url()`
    with the login role's credentials (password from `GIP_APP_DB_PASSWORD`, default
    `gip_app_login`). `GIP_TEST_APP_DATABASE_URL` overrides it.

    Every caller moves to the login role with no edit (FD-1729, PL-1769 Step 3.1): the
    suite exercises the paths the platform runs, as the role it runs them as.
    """
    override = os.environ.get("GIP_TEST_APP_DATABASE_URL")
    if override:
        return override
    return (
        make_url(test_owner_database_url())
        .set(
            username=_APP_LOGIN_ROLE,
            password=os.environ.get("GIP_APP_DB_PASSWORD", _APP_LOGIN_ROLE),
        )
        .render_as_string(hide_password=False)
    )


#: The `(node id, label, reason)` of every test that may use `owner_database` -- closed, and
#: enforced by construction (`owner_database` fails a test not listed here). `api_settings` /
#: `api_client` are never among them: they are the application. Labels: `migration`,
#: `provisioning`, `DP-22` (the five caller-less paths), `owner-subject` (tests that PROVE
#: the owner is refused, or that tamper), `bootstrap` (the seed's `grant_demo_principals`).
OWNER_FIXTURE_USERS: tuple[tuple[str, str, str], ...] = (
    (
        "backend/tests/test_migration_deployments.py::"
        "test_the_upgrade_seeds_the_three_environments_and_leaves_existing_traces_alone",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_deployments.py::"
        "test_an_environment_slug_is_unique_across_every_row",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_deployments.py::"
        "test_a_key_naming_an_unknown_environment_stops_the_upgrade_before_any_change",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_deployments.py::"
        "test_a_service_account_listing_an_unknown_environment_stops_the_upgrade",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_deployments.py::test_the_migration_round_trips",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_deployments.py::"
        "test_the_application_role_cannot_update_or_delete_a_deployment",
        "owner-subject",
        "proves the owner-created application role is refused UPDATE/DELETE on a scratch database",
    ),
    (
        "backend/tests/test_migration_deployments.py::"
        "test_an_approved_deployment_request_needs_a_decided_approval_and_the_flag_is_no_evidence",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_dataset_owner.py::test_an_unresolvable_dataset_stops_the_migration",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_dataset_version_envelope.py::"
        "test_the_migration_round_trips_on_seeded_data",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_dataset_version_envelope.py::"
        "test_a_version_with_no_creator_stops_the_migration",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_env_logging.py::"
        "test_an_in_process_migration_run_leaves_the_app_loggers_enabled",
        "migration",
        "runs Alembic in process, which reads the owner's GIP_MIGRATION_DATABASE_URL",
    ),
    (
        "backend/tests/test_migration_dataset_version_envelope.py::"
        "test_the_backfill_falls_back_to_the_earliest_member",
        "DP-22",
        "writes workspaces and workspace_members, seed-only for the application role",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_trigger_test_fails_on_a_database_one_migration_short_of_head",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_migration_round_trips_and_head_refuses_what_head_minus_one_allows",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_tenant_binding.py::test_an_empty_marker_table_stops_startup",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_tenant_binding.py::test_a_database_not_migrated_to_this_revision_stops_startup",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_tenant_binding.py::test_the_migration_writes_the_configured_tenant_and_refuses_a_second_row",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_with_the_evidence_condition_replaced_by_the_flag_the_forgery_succeeds",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[models]",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[custom_metrics]",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[custom_objectives]",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[peril_structures]",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[rating_versions]",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[validation_rules]",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_approval_guard_trigger.py::test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[validation_rule_sets]",
        "owner-subject",
        "plants a replacement guard function (CREATE FUNCTION in public, rolled back)",
    ),
    (
        "backend/tests/test_wf699_journey.py::test_wf699_journey_runs_end_to_end",
        "bootstrap",
        "the seed's grant_demo_principals creates the workspace, roles and members (no route does)",
    ),
    (
        "backend/tests/test_wf699_journey.py::"
        "test_a_non_glm_stand_in_without_a_transparency_artifact_is_refused",
        "bootstrap",
        "the seed's grant_demo_principals creates the workspace, roles and members (no route does)",
    ),
    (
        "backend/tests/test_wf701_journey.py::test_wf701_journey_runs_end_to_end",
        "bootstrap",
        "the seed's grant_demo_principals creates the workspace, roles and members (no route does)",
    ),
    (
        "backend/tests/test_wf701_journey.py::"
        "test_c7_fails_naming_the_band_when_the_sample_rate_is_zero",
        "bootstrap",
        "the seed's grant_demo_principals creates the workspace, roles and members (no route does)",
    ),
    (
        "backend/tests/test_migration_routing_shadow.py::test_the_migration_round_trips",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_routing_shadow.py::test_the_application_role_may_only_select_and_insert",
        "owner-subject",
        "proves a privilege or trigger refusal on a scratch database as its owner",
    ),
    (
        "backend/tests/test_migration_routing_shadow.py::test_even_the_owner_cannot_update_or_delete_a_row",
        "owner-subject",
        "proves a privilege or trigger refusal on a scratch database as its owner",
    ),
    (
        "backend/tests/test_migration_routing_shadow.py::test_a_fraction_outside_the_unit_interval_is_refused_by_the_database[0]",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_routing_shadow.py::test_a_fraction_outside_the_unit_interval_is_refused_by_the_database[-0.5]",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_routing_shadow.py::test_a_fraction_outside_the_unit_interval_is_refused_by_the_database[1.5]",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_routing_shadow.py::test_a_malformed_bundle_hash_is_refused_by_the_database",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_migration_environment_settings.py::test_environment_settings_round_trip_leaves_api_keys_unchanged",
        "migration",
        "creates and migrates a scratch database (CREATE DATABASE, DDL)",
    ),
    (
        "backend/tests/test_audit.py::"
        "test_tampering_below_the_application_is_detected",
        "owner-subject",
        "sets session_replication_role = replica to tamper with audit_events below the triggers",
    ),
    (
        "backend/tests/test_audit.py::"
        "test_removing_a_middle_event_is_detected",
        "owner-subject",
        "sets session_replication_role = replica to tamper with audit_events below the triggers",
    ),
    (
        "backend/tests/test_audit.py::"
        "test_the_session_teardown_leaves_the_append_only_guard_in_force",
        "owner-subject",
        "sets session_replication_role = replica to tamper with audit_events below the triggers",
    ),
    (
        "backend/tests/test_api_audit.py::"
        "test_verify_reports_a_break_rather_than_failing",
        "owner-subject",
        "sets session_replication_role = replica to tamper with audit_events below the triggers",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_blobs_content_cannot_change_while_its_lifecycle_can",
        "owner-subject",
        "attempts a blobs content UPDATE below the application; asserts the database refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_row_guarded_table_refuses_truncate_from_the_owner_connection[approval_requests]",
        "owner-subject",
        "issues TRUNCATE on the table; asserts the database refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_row_guarded_table_refuses_truncate_from_the_owner_connection[blobs]",
        "owner-subject",
        "issues TRUNCATE on the table; asserts the database refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_row_guarded_table_refuses_truncate_from_the_owner_connection[deployment_requests]",
        "owner-subject",
        "issues TRUNCATE on the table; asserts the database refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_row_guarded_table_refuses_truncate_from_the_owner_connection[rating_versions]",
        "owner-subject",
        "issues TRUNCATE on the table; asserts the database refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_row_guarded_table_refuses_truncate_from_the_owner_connection[validation_rule_sets]",
        "owner-subject",
        "issues TRUNCATE on the table; asserts the database refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_row_guarded_table_refuses_truncate_from_the_owner_connection[validation_rules]",
        "owner-subject",
        "issues TRUNCATE on the table; asserts the database refuses it",
    ),
    (
        "backend/tests/test_audit.py::"
        "test_update_and_delete_are_rejected_by_the_database[UPDATE audit_events SET action = 'x']",
        "owner-subject",
        "issues UPDATE/DELETE on audit_events; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_audit.py::"
        "test_update_and_delete_are_rejected_by_the_database[DELETE FROM audit_events]",
        "owner-subject",
        "issues UPDATE/DELETE on audit_events; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_audit.py::"
        "test_truncate_is_rejected",
        "owner-subject",
        "issues TRUNCATE on audit_events; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_blobs.py::"
        "test_gc_deletes_an_old_unreferenced_blob_and_audits_it",
        "owner-subject",
        "runs the FR-420 sweep, which DELETEs blobs; the app role has no DELETE (OQ-1943)",
    ),
    (
        "backend/tests/test_blobs.py::test_gc_spares_a_referenced_blob",
        "owner-subject",
        "runs the FR-420 sweep, which DELETEs blobs; the app role has no DELETE (OQ-1943)",
    ),
    (
        "backend/tests/test_blobs.py::test_gc_spares_a_young_unreferenced_blob",
        "owner-subject",
        "runs the FR-420 sweep, which DELETEs blobs; the app role has no DELETE (OQ-1943)",
    ),
    (
        "backend/tests/test_custom_metrics_table.py::test_a_metric_cannot_be_deleted_or_truncated",
        "owner-subject",
        "DELETE and TRUNCATE on custom_metrics; asserts the append-only trigger refuses them",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_gip_app_update_on_factors_is_refused_by_the_trigger_not_only_the_grant",
        "owner-subject",
        "reopens a grant (GRANT, DDL); asserts the append-only trigger refuses the UPDATE",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[backtests-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[backtests-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[backtests-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[bandings-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[bandings-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[bandings-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[deployments-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[deployments-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[deployments-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[diagnostics-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[diagnostics-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[diagnostics-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[factors-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[factors-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[factors-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[groupings-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[groupings-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[groupings-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[model_comparisons-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[model_comparisons-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[model_comparisons-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[objective_certificates-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[objective_certificates-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[objective_certificates-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rate_table_cells-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rate_table_cells-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rate_table_cells-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rate_table_versions-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rate_table_versions-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rate_table_versions-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rating_algorithms-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rating_algorithms-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[rating_algorithms-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[reference_rows-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[reference_rows-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[reference_rows-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[reference_tables-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[reference_tables-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[reference_tables-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[regression_suite_versions-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[regression_suite_versions-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[regression_suite_versions-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[regression_suites-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[regression_suites-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[regression_suites-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[routing_rules-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[routing_rules-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[routing_rules-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[shadow_configs-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[shadow_configs-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[shadow_configs-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[shadow_results-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[shadow_results-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[shadow_results-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[sub_graph_versions-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[sub_graph_versions-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[sub_graph_versions-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[transparency_artifacts-UPDATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[transparency_artifacts-DELETE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_artifact_cannot_be_rewritten_from_the_owner_connection[transparency_artifacts-TRUNCATE]",
        "owner-subject",
        "issues UPDATE/DELETE/TRUNCATE as the owner; asserts the append-only trigger refuses it",
    ),
    (
        "backend/tests/test_api_me.py::"
        "test_break_glass_is_visible_on_me",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_rbac.py::"
        "test_a_grant_within_what_the_granter_holds_succeeds_and_is_audited",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_rbac.py::"
        "test_break_glass_is_time_boxed_and_expires",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_rbac.py::"
        "test_break_glass_is_audited_and_flagged",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_rbac.py::"
        "test_seeding_roles_is_idempotent",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_workspace_members.py::"
        "test_a_realm_login_resolves_to_the_seeded_principal",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_workspace_members.py::"
        "test_ensuring_a_member_twice_does_not_raise",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_workspace_members.py::"
        "test_an_id_that_contradicts_the_stored_identity_is_refused_where_it_arises",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_lineage.py::"
        "test_a_subject_purge_is_admin_only_and_recorded",
        "DP-22",
        "runs a production function with no application caller "
        "(grant_role, grant_break_glass, ensure_member, ...) as the owner",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_stored_report_cannot_be_rewritten",
        "owner-subject",
        "trigger probe: issues the tampering statement as the owner "
        "and asserts the trigger, not the privilege check, refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_stored_report_cannot_be_deleted_or_truncated",
        "owner-subject",
        "trigger probe: issues the tampering statement as the owner "
        "and asserts the trigger, not the privilege check, refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_a_profile_cannot_be_rewritten",
        "owner-subject",
        "trigger probe: issues the tampering statement as the owner "
        "and asserts the trigger, not the privilege check, refuses it",
    ),
    (
        "backend/tests/test_artifact_immutability.py::"
        "test_an_acknowledgement_cannot_be_rewritten_or_removed",
        "owner-subject",
        "trigger probe: issues the tampering statement as the owner "
        "and asserts the trigger, not the privilege check, refuses it",
    ),
    (
        "backend/tests/test_backtests.py::"
        "test_a_backtest_cannot_be_rewritten_at_either_layer",
        "owner-subject",
        "trigger probe: issues the tampering statement as the owner "
        "and asserts the trigger, not the privilege check, refuses it",
    ),
    (
        "backend/tests/test_model_jobs.py::"
        "test_a_fitted_model_cannot_be_rewritten_in_the_database",
        "owner-subject",
        "trigger probe: issues the tampering statement as the owner "
        "and asserts the trigger, not the privilege check, refuses it",
    ),
    (
        "backend/tests/test_peril_structures.py::"
        "test_a_reconciled_structure_cannot_be_deleted",
        "owner-subject",
        "trigger probe: issues the tampering statement as the owner "
        "and asserts the trigger, not the privilege check, refuses it",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_an_inherit_false_membership_of_the_owner_is_refused[inherit_false_member_of_the_owner]",
        "owner-subject",
        "plants a scratch role membership / BYPASSRLS role as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_an_inherit_false_membership_of_the_owner_is_refused[bypassrls_role]",
        "owner-subject",
        "plants a scratch role membership / BYPASSRLS role as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_a_tampered_artifact_trigger_refuses_startup[disable]",
        "owner-subject",
        "tampers with an artifact trigger as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_a_tampered_artifact_trigger_refuses_startup[replica]",
        "owner-subject",
        "tampers with an artifact trigger as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_a_tampered_artifact_trigger_refuses_startup[drop]",
        "owner-subject",
        "tampers with an artifact trigger as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_a_tampered_artifact_trigger_refuses_startup[replace_body]",
        "owner-subject",
        "tampers with an artifact trigger as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_every_table_grants_the_application_exactly_its_declared_privileges",
        "owner-subject",
        "reads the grants the owner made, over every public table",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_the_grant_comparison_sees_a_drift_in_both_directions[extra_table_grant]",
        "owner-subject",
        "plants a grant drift as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_the_grant_comparison_sees_a_drift_in_both_directions[missing_column_grant]",
        "owner-subject",
        "plants a grant drift as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_the_grant_comparison_sees_a_drift_in_both_directions[extra_column_grant]",
        "owner-subject",
        "plants a grant drift as the owner (rolled back)",
    ),
    (
        "backend/tests/test_application_role.py::"
        "test_an_enable_always_trigger_is_accepted",
        "owner-subject",
        "sets a trigger to ENABLE ALWAYS as the owner (rolled back)",
    ),
)


def test_blob_bucket() -> str:
    """The bucket every test store uses — fixtures and API-backed apps alike.

    **One resolver because a test that writes a blob through a fixture and reads it back
    through a route needs both sides to agree**, and until `POST /api/v1/score` no test
    crossed that boundary — so eleven sites went on holding **three different answers**
    without anything noticing:

    - `blob_store` here read `os.environ.get("GIP_TEST_BUCKET", "gip-test-blobs")`;
    - `test_api_model_lifecycle` and `test_model_comparison` were bare literals, which
      would *not* follow that variable;
    - the eight `api_settings` fixtures (`conftest.py` and seven shadowing it) named no
      bucket at all, so the app under test used the `gip-blobs` default while every fixture
      wrote to `gip-test-blobs`.

    **That last split needed no environment variable to be wrong** — it was already wrong,
    and it is what `POST /api/v1/score` hit as the first route to *read* a blob a fixture
    had *written*. Everything before it stayed on one side of the boundary. So the variable
    and the default live here, once, and all eleven callers ask.
    """
    return os.environ.get("GIP_TEST_BUCKET", "gip-test-blobs")


def _safe_dsn(dsn: str) -> str:
    """`host:port as user, database name` -- never the password."""
    url = make_url(dsn)
    return f"{url.host}:{url.port} as {url.username}, database {url.database!r}"


def _unavailable(configured: bool, message: str) -> None:
    """A service the suite needs is not usable: FAIL when the environment names it
    (`configured`), skip only when nothing does (FD-1945).

    A skip on a configured-but-unreachable service lets a gate read green with every test
    that needs it skipped. `message` never carries a password or key: callers render DSNs
    with `_safe_dsn` and name an endpoint, never its credentials.
    """
    if configured:
        pytest.fail(message)
    pytest.skip(message)


def _database_configured() -> bool:
    return bool(
        os.environ.get("GIP_TEST_DATABASE_URL") or os.environ.get("GIP_TEST_APP_DATABASE_URL")
    )


@pytest_asyncio.fixture
async def database() -> AsyncIterator[Database]:
    """An engine per test, against a database the migration has already been run on.

    Function-scoped deliberately. A session-scoped async engine binds its connections to
    the event loop that created it, and pytest-asyncio gives each test a fresh loop — the
    result is `got Future attached to a different loop`, which reads like a driver bug
    rather than a fixture-scope mistake. Creating an engine per test costs a connection.

    Skips rather than fails only when no database is configured (neither
    `GIP_TEST_DATABASE_URL` nor `GIP_TEST_APP_DATABASE_URL` is set): a developer without the
    compose stack up should still be able to run the unit tests. A configured database that
    is unreachable, or has no migrations, FAILS naming host, port, user and database
    (FD-1945) -- a skip there would let a gate pass with the DB tests unrun.
    """
    db = Database(Settings(database_url=test_database_url()))
    try:
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        await db.dispose()
        if _APP_LOGIN_ROLE in str(exc):
            # Provisioning is not applied on this database (PL-1769 Step 1.3): a failure to
            # fix in the environment, never a skip and never a reason to re-route the test.
            pytest.fail(
                f"the application login role {_APP_LOGIN_ROLE!r} cannot connect: {exc}; run "
                "scripts/provision-app-role.py against this cluster"
            )
        _unavailable(
            _database_configured(),
            f"PostgreSQL not reachable at {_safe_dsn(test_database_url())}: {type(exc).__name__}",
        )

    async with db.session() as session:
        applied = (
            await session.execute(text("SELECT count(*) FROM alembic_version"))
        ).scalar_one()
    if not applied:
        _unavailable(
            _database_configured(),
            f"database at {_safe_dsn(test_database_url())} has no migrations applied; "
            "run `uv run alembic upgrade head`",
        )

    yield db
    await db.dispose()


@pytest_asyncio.fixture
async def owner_database(request: pytest.FixtureRequest) -> AsyncIterator[Database]:
    """An engine on the **owner's** DSN, for the tests `OWNER_FIXTURE_USERS` lists.

    Fails the test, by construction rather than by review, unless its node id is listed:
    the application's paths run as the login role (`database`), and an owner connection
    that any test could take would let a refused path pass unseen.
    """
    users = {node_id: label for node_id, label, _ in OWNER_FIXTURE_USERS}
    if request.node.nodeid not in users:
        pytest.fail(
            f"{request.node.nodeid} takes owner_database but is not in OWNER_FIXTURE_USERS "
            "(backend/tests/conftest_db.py); use `database`, the application's login role"
        )
    db = Database(Settings(database_url=test_owner_database_url()))
    try:
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        await db.dispose()
        pytest.fail(f"PostgreSQL (owner) not reachable: {type(exc).__name__}: {exc}")
    yield db
    await db.dispose()


@pytest_asyncio.fixture
async def blob_store() -> AsyncIterator[BlobStore]:
    """A blob store against the compose MinIO, with its bucket ensured.

    Skips when MinIO is unreachable and nothing names it (`GIP_TEST_BUCKET` and
    `GIP_BLOB_ENDPOINT_URL` both unset); a configured one that is unreachable FAILS naming
    endpoint and bucket, never a key (FD-1945).
    """
    settings = Settings(blob_bucket=test_blob_bucket())
    store = BlobStore(settings)
    try:
        await store.ensure_bucket()
    except Exception as exc:
        _unavailable(
            bool(os.environ.get("GIP_TEST_BUCKET") or os.environ.get("GIP_BLOB_ENDPOINT_URL")),
            f"MinIO not reachable at {settings.blob_endpoint_url}, bucket "
            f"{settings.blob_bucket!r}: {type(exc).__name__}",
        )
    yield store


async def seed_as_owner[T](seed: Callable[[AsyncSession], Awaitable[T]]) -> T:
    """Run `seed` against the **owner's** engine: the one seam through which a test writes
    the rows the application's login role may not (`workspaces`, `roles`, `role_assignments`).

    The application connects as the login role (FD-1729), which holds no INSERT on the
    tables that define who may do what -- by design, so that a test cannot grant itself a
    permission through the very connection the permission checks run on. Seeding therefore
    runs on its own owner engine, opened and disposed here.

    **Commit semantics (S1a seam ruling, condition (ii)).** `unit_of_work` commits when `seed`
    returns, and the commit happens *before* this function does. The rows are therefore
    committed, and visible to the application connection (`database`, `api_client`) on its
    next statement in the same test; there is no shared transaction to wait on.

    **Teardown.** Nothing deletes these rows per test. Isolation is the test's own fresh
    `workspace_id` (the only isolation an append-only table permits), and the session-scoped
    `_empty_the_database_after_the_session` fixture truncates the whole database as the owner
    after the last test -- as a fixture finalizer, so it runs when tests fail too. A seed
    that raises rolls back and writes nothing.

    **Test-only.** Nothing under `backend/src` may name this module
    (`test_conftest_db_login_role.py` scans for it).
    """
    db = Database(Settings(database_url=test_owner_database_url()))
    try:
        async with db.unit_of_work() as session:
            return await seed(session)
    finally:
        await db.dispose()


async def grant_roles_as_owner(
    workspace_id: UUID,
    principal_id: UUID,
    *role_slugs: str,
    workspace: bool = False,
    membership: bool = False,
    rules_author_id: UUID | None = None,
) -> None:
    """Seed the built-in roles in `workspace_id` and assign `role_slugs` to `principal_id`,
    through `seed_as_owner` (its docstring states the commit and teardown semantics).

    `workspace` first creates the workspace row (FR-395: `workspace_members` and
    `workspace_settings` carry a foreign key to it); `membership` adds the principal's
    workspace membership, idempotently (W6b-11); `rules_author_id` seeds the built-in
    validation-rule catalogue (FR-68) as that author. The `grant` fixture sets all three;
    the local helpers that only need a role leave them off.
    """
    from sqlalchemy import select

    from app.db.models import RoleAssignmentRow, RoleRow, WorkspaceMemberRow
    from app.platform import validation_rules
    from model_schema import ScopeType

    async def seed(session: AsyncSession) -> None:
        if workspace:
            await _ensure_workspace(session, workspace_id=workspace_id)
        await _seed_builtin_roles(session, workspace_id)
        if rules_author_id is not None:
            await validation_rules.seed_builtin_rules(
                session, workspace_id, authored_by=rules_author_id
            )
        for slug in role_slugs:
            role = (
                await session.execute(
                    select(RoleRow).where(
                        RoleRow.workspace_id == workspace_id, RoleRow.slug == slug
                    )
                )
            ).scalar_one()
            session.add(
                RoleAssignmentRow(
                    workspace_id=workspace_id,
                    principal_kind="user",
                    principal_id=principal_id,
                    role_id=role.id,
                    scope_type=ScopeType.WORKSPACE.value,
                )
            )
        if membership:
            # Idempotent: a test may seed its own membership rows first (FR-396's
            # two-workspace test does), and a duplicate insert would violate
            # `uq_workspace_members_user_workspace` (`models.py`).
            existing = (
                await session.execute(
                    select(WorkspaceMemberRow).where(
                        WorkspaceMemberRow.user_id == principal_id,
                        WorkspaceMemberRow.workspace_id == workspace_id,
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                session.add(WorkspaceMemberRow(user_id=principal_id, workspace_id=workspace_id))

    await seed_as_owner(seed)


# The wrappers below carry the name and signature of the production function they stand for,
# so a test re-points one import (`from conftest_db import ensure_workspace`) and its call
# sites stay as written. The `session` argument is accepted for that parity and **not used**:
# the write runs on the owner's engine through `seed_as_owner` (same commit and teardown
# semantics), because the login role holds no INSERT on these tables. The production
# functions in `backend/src` are untouched and still run as the application.
async def ensure_workspace(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    slug: str | None = None,
    name: str | None = None,
) -> WorkspaceRow:
    """`app.platform.workspaces.ensure_workspace`, executed through `seed_as_owner`."""
    del session
    return await seed_as_owner(
        lambda owner: _ensure_workspace(owner, workspace_id=workspace_id, slug=slug, name=name)
    )


async def seed_builtin_roles(session: AsyncSession, workspace_id: UUID) -> list[RoleRow]:
    """`app.platform.rbac.seed_builtin_roles`, executed through `seed_as_owner`."""
    del session
    return await seed_as_owner(lambda owner: _seed_builtin_roles(owner, workspace_id))


async def set_workspace_setting(
    session: AsyncSession, workspace_id: UUID, key: str, value: Any
) -> SettingDefinition:
    """`app.platform.settings.set_workspace_setting`, executed through `seed_as_owner`."""
    del session
    from app.platform import settings

    return await seed_as_owner(
        lambda owner: settings.set_workspace_setting(owner, workspace_id, key, value)
    )


async def set_environment_setting(
    session: AsyncSession,
    environment: str,
    key: str,
    value: Any,
    updated_by: UUID | None,
) -> tuple[SettingDefinition, Any]:
    """`app.platform.settings.set_environment_setting`, executed through `seed_as_owner`."""
    del session
    from app.platform import settings

    return await seed_as_owner(
        lambda owner: settings.set_environment_setting(owner, environment, key, value, updated_by)
    )


@pytest.fixture(autouse=True)
def _seed_through_the_owner_seam(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Patches two production functions for every test**:
    `app.platform.workspaces.ensure_workspace` and `app.platform.rbac.seed_builtin_roles`
    become this module's owner-routed wrappers.

    Why: the application connects as the login role (FD-1729, S1a), which holds no INSERT on
    `workspaces`, `roles`, `workspace_members` or `role_assignments`. Tests call these two
    module-qualified (`workspaces.ensure_workspace(session, ...)`) to seed rows, so without this
    the 59 call sites would each fail "permission denied". The wrappers run the same function on
    the owner's engine (`seed_as_owner`); call sites and imports stay as written. Production
    code has no caller of either in `backend/src`, so no app path is hidden by the patch.
    `set_workspace_setting` and `set_environment_setting` are deliberately NOT patched: the app
    calls them (`api/settings.py`, `api/environment_settings.py`), and patching would hide a
    missing application grant.

    **Opt-out: `@pytest.mark.production_seed`.** A test of the production function itself
    carries it, gets the original function and runs as the login role, so a regression in the
    real function is still caught.
    """
    if request.node.get_closest_marker("production_seed") is not None:
        return
    monkeypatch.setattr(workspaces, "ensure_workspace", ensure_workspace)
    monkeypatch.setattr(rbac, "seed_builtin_roles", seed_builtin_roles)


@pytest_asyncio.fixture
async def grant(database: Database, workspace_id: UUID, principal: Principal):
    """Seed the built-in roles, grant one to the test principal, and record membership.

    Route tests must grant explicitly, because development identity carries **no**
    permissions. Treating the dev principal as an administrator would make every route test
    pass without exercising a single permission check — coverage that is not coverage.

    The membership row (W6b-11) is the other half of the same rule: the dev caller
    resolves through the memberships the database holds, so a granted caller must also be
    a member, or the permission checks this fixture exists to exercise never run.

    The writes run on the owner's engine (`seed_as_owner`), because the application's login
    role cannot insert them. `database` is requested only for its reachability and migration
    checks, so an unreachable database skips here exactly as it does for the app path.

        await grant("analyst")
    """

    async def _grant(role_slug: str, *, principal_id: UUID | None = None) -> None:
        # The catalogue arrives with the workspace, exactly as the roles do (FR-68). `grant`
        # is the only workspace-creation path this suite has, so seeding hangs off it.
        await grant_roles_as_owner(
            workspace_id,
            principal_id or principal.id,
            role_slug,
            workspace=True,
            membership=True,
            rules_author_id=principal.id,
        )

    return _grant


@pytest_asyncio.fixture
async def membership(database: Database, workspace_id: UUID, principal: Principal):
    """Seed a workspace membership without any role.

    Refusal tests use this. A caller with no membership is refused before any permission
    check runs — `UNAUTHENTICATED`, not `PERMISSION_DENIED` — so a refusal test that
    wants the **role** check to be the refuser must seed the membership and leave the
    role assignments empty (W6b-11).
    """

    async def _membership(*, principal_id: UUID | None = None) -> None:
        from sqlalchemy import select

        from app.db.models import WorkspaceMemberRow

        member = principal_id or principal.id

        # On the owner's engine (`seed_as_owner`: committed before it returns, never deleted
        # per test, truncated at session end), because the login role cannot insert
        # `workspaces` or `workspace_members`.
        async def seed(session: AsyncSession) -> None:
            await _ensure_workspace(session, workspace_id=workspace_id)
            existing = (
                await session.execute(
                    select(WorkspaceMemberRow).where(
                        WorkspaceMemberRow.user_id == member,
                        WorkspaceMemberRow.workspace_id == workspace_id,
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                session.add(WorkspaceMemberRow(user_id=member, workspace_id=workspace_id))

        await seed_as_owner(seed)

    return _membership


@pytest.fixture
def workspace_id() -> UUID:
    """A fresh workspace per test — the only isolation an append-only table permits."""
    return new_uuid7()


@pytest.fixture
def principal() -> Principal:
    return Principal(kind=ActorKind.USER, id=new_uuid7(), display="a.actuary@insurer.example")


#: Seventeen tables refuse `TRUNCATE`, not one. `audit_events` is the famous one (FR-370),
#: but artifact immutability is enforced the same way across `validation_reports`,
#: `models`, `diagnostics`, `blobs`, `transparency_artifacts` and a dozen more — so naming
#: tables here would mean editing this file every time the platform gains an immutable
#: artifact, and discovering it from a failed teardown each time.
#:
#: `session_replication_role = replica` suspends every user trigger at once, and the third
#: argument to `set_config` makes it **transaction-local**: it reverts when this statement's
#: transaction ends, by commit or by rollback, with nothing to re-enable and no ordering of
#: failures that leaves a guard off. That is the property that makes suspending them here
#: defensible; a per-table `ALTER ... DISABLE TRIGGER` would depend on reaching its own
#: re-enable. It needs superuser, which the compose and CI `gipricing` role has.
#: `tenant_marker` is kept with `alembic_version`: it is the deployment's identity, written by
#: a migration and never by a test, and every app startup refuses without it (FR-436).
#:
#: **`environments` is truncated with the rest and its three seeds are put back** (WK-674
#: Slice 2, PL-1392 Task 3): the migration seeds `dev`, `uat` and `prod`, every test that
#: deploys or scores through a Deployment reads one of them, and nothing else re-creates them
#: once a session has emptied the table. The tuple is the migration's own `SEEDS`, pinned equal
#: by `test_migration_deployments.py`. The re-seed is skipped on a database one revision short
#: of the table, so a stale template (FD-1218) still reports its own problem.
ENVIRONMENT_SEEDS: tuple[tuple[str, str, int, str | None], ...] = (
    ("dev", "Development", 1, None),
    ("uat", "User acceptance", 2, "dev"),
    ("prod", "Production", 3, "uat"),
)


def _environment_seed_values() -> str:
    return ", ".join(
        f"(gen_random_uuid(), '{slug}', '{name}', {order}, "
        f"{'NULL' if prior is None else repr(prior)})"
        for slug, name, order, prior in ENVIRONMENT_SEEDS
    )


_EMPTY_THE_DATABASE = f"""
DO $$
DECLARE stmt text;
BEGIN
  PERFORM set_config('session_replication_role', 'replica', true);
  SELECT 'TRUNCATE TABLE '
       || string_agg(format('%I.%I', schemaname, tablename), ', ')
       || ' RESTART IDENTITY CASCADE'
    INTO stmt
    FROM pg_tables
   WHERE schemaname = 'public' AND tablename NOT IN ('alembic_version', 'tenant_marker');
  EXECUTE stmt;
  IF to_regclass('public.environments') IS NOT NULL THEN
    INSERT INTO environments (id, slug, name, promotion_order, requires_prior_environment)
    VALUES {_environment_seed_values()};
  END IF;
END $$;
"""


async def empty_the_database() -> None:
    """Truncate every table but `alembic_version`, restoring the audit guard on the way out.

    Exposed rather than inlined so a test can call it mid-session and assert the guards are
    still in force afterwards — the one property of this teardown worth pinning, since a
    suspended trigger is silent and these tables are what the platform's governance rests on.
    """
    db = Database(Settings(database_url=test_owner_database_url()))
    try:
        # `unit_of_work`, not `session`: the latter does no transaction management and never
        # commits, so the statement below runs and is rolled back on close. It also gives
        # the transaction that `set_config(..., true)` above is local to.
        async with db.unit_of_work() as session:
            await session.execute(text(_EMPTY_THE_DATABASE))
    finally:
        await db.dispose()


@pytest.fixture(scope="session", autouse=True)
def _empty_the_database_after_the_session() -> Iterator[None]:
    """Leave the shared database as empty as the migrations left it.

    **Session-scoped, and deliberately not per-test.** Truncating between tests would
    contradict the module docstring above and cost a full-table lock 430 times over; the
    growth it exists to bound is per-*run*, not per-test.

    Synchronous, calling `asyncio.run` at teardown, because a session-scoped *async* fixture
    binds its connections to the loop that created it while `pytest-asyncio` gives each test
    a fresh one — the `got Future attached to a different loop` the `database` fixture's
    docstring warns about. Running after the last test, this owns the only loop there is.

    Warns rather than fails when PostgreSQL is unreachable: the suite already skips its
    database tests in that case (see `database`), and a teardown that fails the run for a
    developer who never had a database would punish exactly the person the skip exists to
    help. It **warns rather than passing silently** because the first version of this
    swallowed a real bug — `session()` does not commit — and reported a clean run while
    emptying nothing.

    **This empties the whole database, including any `scripts/demo.py` seed.** Tests and the
    demo share one database, so bounding the growth of one bounds the other. Re-seed with
    `uv run python scripts/demo.py`.
    """
    yield
    try:
        asyncio.run(empty_the_database())
    # Broad by intent: no database is not a failure, but it is never silent either.
    except Exception as exc:
        warnings.warn(
            f"could not empty the test database ({type(exc).__name__}: {exc}); this run's "
            "rows remain. `.claude/skills/python-test` carries the manual reset.",
            stacklevel=1,
        )

