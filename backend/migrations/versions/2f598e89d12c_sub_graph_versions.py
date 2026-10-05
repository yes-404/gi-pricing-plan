"""sub_graph_versions: the stored, immutable Sub-graph Version (WK-1250 Slice 1, PL-1325)

`03` §4.11, FR-217's artifact limb. One row per version, the validated `SubGraph` as JSONB,
a required change note, and no `updated_at` or `parent_id` (`00` FR-4). The unique constraint
is what makes a lost numbering race an `IntegrityError` the service maps to 409.

Revision ID: 2f598e89d12c
Revises: a9f3c6d21b87
Create Date: 2026-10-01 00:00:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2f598e89d12c"
down_revision: str | None = "a9f3c6d21b87"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sub_graph_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("change_note", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_sub_graph_versions_slug_version"
        ),
    )
    op.create_index(
        "ix_sub_graph_versions_workspace", "sub_graph_versions", ["workspace_id", "slug"]
    )


def downgrade() -> None:
    op.drop_index("ix_sub_graph_versions_workspace", table_name="sub_graph_versions")
    op.drop_table("sub_graph_versions")
