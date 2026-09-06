"""workspaces table

A Workspace becomes a named row (`07` FR-395), and `workspace_members` and
`workspace_settings` reference it.

The backfill covers **every table carrying a `workspace_id`**, not only the two that gain
the foreign key: an id stored anywhere and described nowhere is exactly the orphan the
`ALTER TABLE` must not discover, and FR-395 says "anywhere" rather than "with a
membership". The union below was enumerated from `app.db.models` rather than recalled —
every table whose columns include `workspace_id`, 35 of them — and all are listed. Adding
a workspace-scoped table without adding it here leaves that orphan possible again.

Revision ID: 57547846f0a3
Revises: 82edffbe1dce
Create Date: 2026-08-24 13:28:28.969178+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "57547846f0a3"
down_revision: str | None = "82edffbe1dce"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


#: One row per distinct workspace id, named after the id itself. A generated name is honest
#: about what is known: nobody recorded a name for these, and inventing "Workspace 1" would
#: read like a name someone chose.
#:
#: The slug is derived from the id rather than generated randomly, so re-running this on a
#: restored dump produces the same slugs and `ON CONFLICT DO NOTHING` means what it says.
_BACKFILL = """
INSERT INTO workspaces (id, slug, name, created_at)
SELECT ids.workspace_id,
       'ws-' || replace(ids.workspace_id::text, '-', ''),
       'Workspace ' || left(replace(ids.workspace_id::text, '-', ''), 8),
       now()
  FROM (
        SELECT DISTINCT workspace_id FROM approval_policies
        UNION SELECT DISTINCT workspace_id FROM approval_requests
        UNION SELECT DISTINCT workspace_id FROM audit_events
        UNION SELECT DISTINCT workspace_id FROM backtests
        UNION SELECT DISTINCT workspace_id FROM bandings
        UNION SELECT DISTINCT workspace_id FROM custom_metrics
        UNION SELECT DISTINCT workspace_id FROM custom_objectives
        UNION SELECT DISTINCT workspace_id FROM dataset_splits
        UNION SELECT DISTINCT workspace_id FROM dataset_versions
        UNION SELECT DISTINCT workspace_id FROM datasets
        UNION SELECT DISTINCT workspace_id FROM diagnostics
        UNION SELECT DISTINCT workspace_id FROM factors
        UNION SELECT DISTINCT workspace_id FROM groupings
        UNION SELECT DISTINCT workspace_id FROM ingestion_runs
        UNION SELECT DISTINCT workspace_id FROM jobs
        UNION SELECT DISTINCT workspace_id FROM metric_certificates
        UNION SELECT DISTINCT workspace_id FROM model_comparisons
        UNION SELECT DISTINCT workspace_id FROM models
        UNION SELECT DISTINCT workspace_id FROM objective_certificates
        UNION SELECT DISTINCT workspace_id FROM peril_structures
        UNION SELECT DISTINCT workspace_id FROM profiles
        UNION SELECT DISTINCT workspace_id FROM reference_table_versions
        UNION SELECT DISTINCT workspace_id FROM reference_tables
        UNION SELECT DISTINCT workspace_id FROM role_assignments
        UNION SELECT DISTINCT workspace_id FROM roles
        UNION SELECT DISTINCT workspace_id FROM service_accounts
        UNION SELECT DISTINCT workspace_id FROM sources
        UNION SELECT DISTINCT workspace_id FROM subject_purges
        UNION SELECT DISTINCT workspace_id FROM transparency_artifacts
        UNION SELECT DISTINCT workspace_id FROM validation_acknowledgements
        UNION SELECT DISTINCT workspace_id FROM validation_reports
        UNION SELECT DISTINCT workspace_id FROM validation_rule_sets
        UNION SELECT DISTINCT workspace_id FROM validation_rules
        UNION SELECT DISTINCT workspace_id FROM workspace_members
        UNION SELECT DISTINCT workspace_id FROM workspace_settings
       ) AS ids
 WHERE ids.workspace_id IS NOT NULL
ON CONFLICT (id) DO NOTHING
"""


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("slug", name="uq_workspaces_slug"),
    )
    op.execute(_BACKFILL)
    # After the backfill, never before: the key is what proves the backfill was complete,
    # and PostgreSQL's own error names the offending table if it was not.
    op.create_foreign_key(
        "fk_workspace_members_workspace",
        "workspace_members",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_workspace_settings_workspace",
        "workspace_settings",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_workspace_settings_workspace", "workspace_settings", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_workspace_members_workspace", "workspace_members", type_="foreignkey"
    )
    op.drop_table("workspaces")
