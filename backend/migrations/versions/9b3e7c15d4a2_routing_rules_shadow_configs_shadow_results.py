"""routing rules, shadow configurations and shadow results (WK-674 Slice 6, RL-1834)

`03` §4.13, FR-270, FR-271. Three append-only tables, in the shape `deployments` set
(`c4a81f6d2e95`): the application role has `SELECT` and `INSERT` only, and the
`artifact_append_only()` trigger pair stops the owner too.

* `routing_rules`: one row per write of an Environment's date ranges; the latest is current.
* `shadow_configs`: one row per write of an Environment's shadow candidate and fraction.
* `shadow_results`: one row per shadow-scored quote. It holds the two `ScoringResult`s and no
  Quote Context, so it is not a quote-input store (NFR-499).

Revision ID: 9b3e7c15d4a2
Revises: a4d1f08c3b97
Create Date: 2026-10-21 17:30:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "9b3e7c15d4a2"
down_revision: str | None = "a4d1f08c3b97"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"
TABLES = ("routing_rules", "shadow_configs", "shadow_results")


def _id() -> sa.Column[object]:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True)


def _workspace_and_environment(table: str) -> list[sa.Column[object] | sa.ForeignKeyConstraint]:
    return [
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name=op.f(f"fk_{table}_environment_id_environments"),
        ),
    ]


def _at(name: str) -> sa.Column[object]:
    return sa.Column(
        name, sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )


def upgrade() -> None:
    op.create_table(
        "routing_rules",
        _id(),
        *_workspace_and_environment("routing_rules"),
        sa.Column("ranges", postgresql.JSONB(), nullable=False),
        sa.Column("written_by", postgresql.UUID(as_uuid=True), nullable=False),
        _at("written_at"),
    )
    op.create_index(
        "ix_routing_rules_environment",
        "routing_rules",
        ["workspace_id", "environment_id", "written_at"],
    )

    op.create_table(
        "shadow_configs",
        _id(),
        *_workspace_and_environment("shadow_configs"),
        sa.Column("candidate_rating_version_ref", sa.String(100), nullable=False),
        sa.Column("candidate_bundle_hash", sa.String(71), nullable=False),
        sa.Column("fraction", sa.Float(), nullable=False),
        sa.Column("written_by", postgresql.UUID(as_uuid=True), nullable=False),
        _at("written_at"),
        sa.CheckConstraint(
            "fraction > 0 AND fraction <= 1",
            name=op.f("ck_shadow_configs_fraction_in_unit_interval"),
        ),
        sa.CheckConstraint(
            "candidate_bundle_hash ~ '^sha256:[a-f0-9]{64}$'",
            name=op.f("ck_shadow_configs_bundle_hash_format"),
        ),
    )
    op.create_index(
        "ix_shadow_configs_environment",
        "shadow_configs",
        ["workspace_id", "environment_id", "written_at"],
    )

    op.create_table(
        "shadow_results",
        _id(),
        *_workspace_and_environment("shadow_results"),
        sa.Column("live_deployment_id", postgresql.UUID(as_uuid=True), nullable=True),
        _at("scored_at"),
        sa.Column("live_result", postgresql.JSONB(), nullable=False),
        sa.Column("candidate_result", postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(
            ["live_deployment_id"],
            ["deployments.id"],
            name=op.f("fk_shadow_results_live_deployment_id_deployments"),
        ),
    )
    op.create_index(
        "ix_shadow_results_environment",
        "shadow_results",
        ["workspace_id", "environment_id", "scored_at"],
    )

    for table in TABLES:
        op.execute(
            f"CREATE TRIGGER {table}_no_modify BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION artifact_append_only()"
        )
        op.execute(
            f"CREATE TRIGGER {table}_no_truncate BEFORE TRUNCATE ON {table} "
            "FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only()"
        )
        op.execute(f"GRANT SELECT, INSERT ON {table} TO {APP_ROLE}")
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM {APP_ROLE}")
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM PUBLIC")


def downgrade() -> None:
    op.drop_index("ix_shadow_results_environment", table_name="shadow_results")
    op.drop_table("shadow_results")  # drops its two triggers with it
    op.drop_index("ix_shadow_configs_environment", table_name="shadow_configs")
    op.drop_table("shadow_configs")
    op.drop_index("ix_routing_rules_environment", table_name="routing_rules")
    op.drop_table("routing_rules")
