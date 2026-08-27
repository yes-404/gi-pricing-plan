"""rating version 43 fields

Widens `rating_versions` with the 03 §4.3 contract (W9-3): algorithm_ref, pins,
model_reference_mode, effective_from/to, bundle, change_summary, evidence. All columns
are nullable so the Phase 1b subset keeps working (the §4.3 scoping note records the
Phase 1b subset; this slice widens it).

Revision ID: 6e97fcd3606e
Revises: f9dffcef4ef2
Create Date: 2026-08-27 22:46:24.222004+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "6e97fcd3606e"
down_revision: str | None = "f9dffcef4ef2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "rating_versions",
        sa.Column("algorithm_ref", sa.String(100), nullable=True),
    )
    op.add_column(
        "rating_versions",
        sa.Column("pins", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "rating_versions",
        sa.Column(
            "model_reference_mode", sa.String(16), nullable=False, server_default="exact"
        ),
    )
    op.add_column(
        "rating_versions",
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "rating_versions",
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "rating_versions",
        sa.Column("bundle", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "rating_versions",
        sa.Column("change_summary", sa.Text(), nullable=True),
    )
    op.add_column(
        "rating_versions",
        sa.Column("evidence", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    for column in (
        "evidence",
        "change_summary",
        "bundle",
        "effective_to",
        "effective_from",
        "model_reference_mode",
        "pins",
        "algorithm_ref",
    ):
        op.drop_column("rating_versions", column)
