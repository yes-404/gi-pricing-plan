"""W7-3: the Phase 1b rating version table.

The artifact `FR-440` asks the demo to seed: a slugged, versioned,
`draft → review → approved` rating version pinning an approved Model. Minimal on purpose —
compile, score, rate tables and deployment stay Phase 2 (`03` §4.3's scoping note, OD1).

Revision ID: 06e5a5425a8b
Revises: 2057e7372a9a
Create Date: 2026-08-27 14:15:36.118168+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "06e5a5425a8b"
down_revision: str | None = "2057e7372a9a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.create_table(
        "rating_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("dataset_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_ref", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_rating_versions_slug_version"
        ),
    )
    op.create_index(
        "ix_rating_versions_workspace", "rating_versions", ["workspace_id", "slug"]
    )

    op.execute(f"GRANT SELECT, INSERT, UPDATE ON rating_versions TO {APP_ROLE}")
    op.execute("REVOKE DELETE ON rating_versions FROM PUBLIC")


def downgrade() -> None:
    op.drop_index("ix_rating_versions_workspace", table_name="rating_versions")
    op.drop_table("rating_versions")
