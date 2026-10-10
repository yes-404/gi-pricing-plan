"""rate table version created_by_edit

Adds the creation record of a version made by the manual-edit route (WK-675 Slice 4,
`RL-1555` item 2): `created_by_edit` holds the `ManualEdit` record (`applied_to`, the
immutable base version edited, and `edited_cells`, the number of edits applied), which is
what tells a hand-edited version from a re-seed. Nullable, and every existing row stays
NULL (no backfill): a seeded, operated or imported version carries none.

Revision ID: d4e81b7a2c95
Revises: b8d2f4a6c0e1
Create Date: 2026-10-10 03:30:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d4e81b7a2c95"
down_revision: str | None = "b8d2f4a6c0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "rate_table_versions",
        sa.Column(
            "created_by_edit",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="ManualEdit record of the manual edit that created the version "
            "(03 §4.2): the base version edited and the number of edits",
        ),
    )


def downgrade() -> None:
    op.drop_column("rate_table_versions", "created_by_edit")
