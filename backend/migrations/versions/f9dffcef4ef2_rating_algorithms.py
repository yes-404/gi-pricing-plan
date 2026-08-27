"""rating algorithms

The `rating_algorithms` table persists validated `RatingAlgorithm` JSON (03 §4.1, W9-2).
A rating algorithm is a declarative artifact, so the row stores the validated JSON, never
a pickle (CLAUDE.md §2).

Revision ID: f9dffcef4ef2
Revises: 06e5a5425a8b
Create Date: 2026-08-27 21:52:54.098281+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f9dffcef4ef2"
down_revision: str | None = "06e5a5425a8b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rating_algorithms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
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
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_rating_algorithms_slug_version"
        ),
    )
    op.create_index(
        "ix_rating_algorithms_workspace", "rating_algorithms", ["workspace_id", "slug"]
    )


def downgrade() -> None:
    op.drop_index("ix_rating_algorithms_workspace", table_name="rating_algorithms")
    op.drop_table("rating_algorithms")
