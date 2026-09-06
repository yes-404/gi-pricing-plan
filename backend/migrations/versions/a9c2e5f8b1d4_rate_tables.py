"""rate tables and versions

Adds the rate-table store (slice W10-2): a `rate_tables` catalog, immutable
`rate_table_versions` carrying the definition (keys, value, bounds, default row),
and per-cell rows for `storage: rows` (FR-232) — the form that makes FR-231's
cell diff and its exposure weighting SQL-joinable. The parquet blob form and the
workspace cell-count threshold are W10-3.

Revision ID: a9c2e5f8b1d4
Revises: 6e97fcd3606e
Create Date: 2026-08-28 11:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a9c2e5f8b1d4"
down_revision: str | None = "6e97fcd3606e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rate_tables",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "slug", name="uq_rate_tables_workspace_slug"),
    )
    op.create_index(
        "ix_rate_tables_workspace", "rate_tables", ["workspace_id", "slug"]
    )
    op.create_table(
        "rate_table_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rate_table_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("storage", sa.String(16), nullable=False),
        sa.Column("definition", postgresql.JSONB(), nullable=False),
        sa.Column("change_note", sa.Text(), nullable=False),
        sa.Column("seeded_from", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "rate_table_id", "version_number", name="uq_rate_table_versions_table_version"
        ),
    )
    op.create_index(
        "ix_rate_table_versions_table", "rate_table_versions", ["rate_table_id"]
    )
    op.create_table(
        "rate_table_cells",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", postgresql.JSONB(), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version_id", "key", name="uq_rate_table_cells_version_key"),
    )
    op.create_index(
        "ix_rate_table_cells_version", "rate_table_cells", ["version_id"]
    )


def downgrade() -> None:
    op.drop_table("rate_table_cells")
    op.drop_table("rate_table_versions")
    op.drop_table("rate_tables")
