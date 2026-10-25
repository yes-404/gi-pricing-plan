"""the application role's grants: exactly what the application does, nothing else

FD-1729 (PL-1769 Task 5, Step 5.1): the application connects as the login role, a member of
`gip_app`, and no longer as the owner, so every table it touches needs a grant. All grants go
to `gip_app` (never to the login role), so the login role owns nothing and holds no direct
privilege.

The map is the census of the application's writes (PL-1769 *Table classification*): `INSERT`
for a table it creates rows in, `UPDATE` on the named columns where only those move, and
`SELECT` throughout (an `INSERT … RETURNING`, a `WHERE`, a trigger that reads). **No grant
without a census row.** The census diff against the red run (Step 5.1, Step 5.3) is a
DB-window act that follows this migration; a grant a red names that is missing here is added
in a later revision, never by loosening a guard.

Excess revoked: `jobs` and `outbox` held `DELETE` (`df53696a2682`) with no caller, and `outbox`
held a whole-table `UPDATE` where the relay moves four columns. The five seed-only tables
(`workspaces`, `workspace_members`, `roles`, `role_assignments`, `subject_purges`; DP-22) are
read-only to the application: the seed writes them as the owner.

Only tables whose grants change are touched. `downgrade()` restores the previous grants
exactly (`_PREVIOUS`, read off the revisions that made them) and never touches a row.

Revision ID: b7e4c2a91d36
Revises: 9b3e7c15d4a2
Create Date: 2026-10-25 22:30:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "b7e4c2a91d36"
down_revision: str | None = "9b3e7c15d4a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

#: A table's grants to `gip_app`: its table-level privileges, then the columns that carry
#: `UPDATE` alone (a column grant, not a table-level `UPDATE`).
Grant = tuple[str, tuple[str, ...]]

READ: Grant = ("SELECT", ())
APPEND: Grant = ("SELECT, INSERT", ())
LIFECYCLE: Grant = ("SELECT, INSERT, UPDATE", ())


def _moves(*columns: str) -> Grant:
    """`SELECT, INSERT`, and `UPDATE` on the named columns only."""
    return ("SELECT, INSERT", columns)


#: What `gip_app` held before this revision, per table, where it held anything. A table
#: absent here held nothing: the application was the owner.
_PREVIOUS: dict[str, Grant] = {
    "audit_events": APPEND,
    "backtests": APPEND,
    "bandings": APPEND,
    "custom_metrics": LIFECYCLE,
    "custom_objectives": LIFECYCLE,
    "deployment_requests": LIFECYCLE,
    "deployments": APPEND,
    "diagnostics": APPEND,
    "environments": LIFECYCLE,
    "factors": APPEND,
    "groupings": APPEND,
    "jobs": ("SELECT, INSERT, UPDATE, DELETE", ()),
    "metric_certificates": APPEND,
    "model_comparisons": APPEND,
    "models": LIFECYCLE,
    "objective_certificates": APPEND,
    "outbox": ("SELECT, INSERT, UPDATE, DELETE", ()),
    "peril_structures": LIFECYCLE,
    "profiles": APPEND,
    "rate_table_cells": APPEND,
    "rate_table_versions": APPEND,
    "rate_tables": _moves("current_version", "updated_at"),
    "rating_algorithms": APPEND,
    "rating_versions": LIFECYCLE,
    "reference_rows": APPEND,
    "reference_table_versions": _moves("status"),
    "reference_tables": APPEND,
    "regression_suite_versions": APPEND,
    "regression_suites": APPEND,
    "routing_rules": APPEND,
    "scoring_traces": ("SELECT, INSERT, DELETE", ()),
    "shadow_configs": APPEND,
    "shadow_results": APPEND,
    "sub_graph_versions": APPEND,
    "transparency_artifacts": APPEND,
    "validation_acknowledgements": APPEND,
    "validation_reports": APPEND,
}

#: What `gip_app` holds after it: every public table, one row each (PL-1769 *Table
#: classification*, rows 1 to 60, and the three routing and shadow tables mapped since).
_TARGET: dict[str, Grant] = {
    "api_keys": _moves("expires_at", "revoked_at", "last_used_at"),
    "approval_decisions": APPEND,
    "approval_policies": _moves("policy", "updated_at"),
    "approval_requests": _moves("status", "decided_at", "withdrawn_reason"),
    "audit_events": APPEND,
    "backtests": APPEND,
    "bandings": APPEND,
    "blob_uploads": _moves("job_id", "sha256"),
    "blobs": _moves("ref_count"),
    "custom_metrics": LIFECYCLE,
    "custom_objectives": LIFECYCLE,
    "dataset_splits": APPEND,
    "dataset_versions": LIFECYCLE,
    "datasets": _moves("data_dictionary", "owner_id", "validation_rule_set_id"),
    "deployment_requests": _moves("approval_request_id", "status"),
    "deployments": APPEND,
    "diagnostics": APPEND,
    "dislocation_runs": APPEND,
    "environment_settings": _moves("value", "updated_by", "updated_at"),
    "environments": _moves("name", "description", "retired_at"),
    "factors": APPEND,
    "groupings": APPEND,
    "ingestion_runs": APPEND,
    "job_logs": APPEND,
    "jobs": LIFECYCLE,
    "metric_certificates": APPEND,
    "model_comparisons": APPEND,
    "models": LIFECYCLE,
    "objective_certificates": APPEND,
    "outbox": _moves("attempts", "last_error", "status", "published_at"),
    "peril_structures": LIFECYCLE,
    "profiles": APPEND,
    "rate_table_cells": APPEND,
    "rate_table_versions": APPEND,
    "rate_tables": _moves("current_version", "updated_at"),
    "rating_algorithms": APPEND,
    "rating_versions": LIFECYCLE,
    "reference_rows": APPEND,
    "reference_table_versions": _moves("status"),
    "reference_tables": APPEND,
    "regression_runs": APPEND,
    "regression_suite_versions": APPEND,
    "regression_suites": APPEND,
    "role_assignments": READ,
    "roles": READ,
    "routing_rules": APPEND,
    "scoring_traces": ("SELECT, INSERT, DELETE", ()),
    "service_accounts": APPEND,
    "shadow_configs": APPEND,
    "shadow_results": APPEND,
    "sources": APPEND,
    "sub_graph_versions": APPEND,
    "subject_purges": READ,
    "tenant_marker": READ,
    "transparency_artifacts": APPEND,
    "users": _moves("email", "display_name", "last_login_at"),
    "validation_acknowledgements": APPEND,
    "validation_reports": APPEND,
    "validation_rule_sets": APPEND,
    "validation_rules": _moves("dry_run_report_id", "status", "approved_by"),
    "workspace_members": READ,
    "workspace_settings": _moves("value"),
    "workspaces": READ,
}


def _apply(table: str, grant: Grant | None) -> None:
    """Make `gip_app`'s grants on `table` exactly `grant` (`None`: nothing)."""
    op.execute(f"REVOKE ALL ON {table} FROM {APP_ROLE}")
    if grant is None:
        return
    privileges, update_columns = grant
    # The grant named by `_TARGET` or `_PREVIOUS` for this table; the census row that needs it
    # is the table's row in PL-1769 *Table classification*.
    op.execute(f"GRANT {privileges} ON {table} TO {APP_ROLE}")
    if update_columns:
        # Column-level UPDATE: only the columns the census says the application moves.
        op.execute(f"GRANT UPDATE ({', '.join(update_columns)}) ON {table} TO {APP_ROLE}")


def upgrade() -> None:
    for table, grant in _TARGET.items():
        if _PREVIOUS.get(table) != grant:
            _apply(table, grant)


def downgrade() -> None:
    # REVOKE ALL, then re-grant what `_PREVIOUS` records: exactly what the revisions before this
    # one left, for the tables this revision changed.
    for table, grant in _TARGET.items():
        if _PREVIOUS.get(table) != grant:
            _apply(table, _PREVIOUS.get(table))
