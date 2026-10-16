"""bandings.column_name nullable

A Banding is cut over a dataset column **or** over an `expression` Factor's formula, never
both and never neither (WK-690 Slice 4, `RL-1615` DP-S4-1; `RL-1700` (c)). A Banding cut over
a formula has no column, so `bandings.column_name` stops being NOT NULL. The formula is
stored in the row's `body` as `source_expression`, as every other field of the artifact is.
No line in `backend/src` reads `column_name`, and every existing row keeps its value. A DDL
change is not refused by the append-only row triggers.

Downgrade re-imposes NOT NULL, so it fails loudly if an expression Banding has been stored:
the old schema cannot hold one, and a banding row cannot be deleted (FR-101).

Revision ID: f2b6d90a4c17
Revises: d4e81b7a2c95
Create Date: 2026-10-16 09:32:28.290223+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f2b6d90a4c17"
down_revision: str | None = "d4e81b7a2c95"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "bandings", "column_name", existing_type=sa.String(length=128), nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "bandings", "column_name", existing_type=sa.String(length=128), nullable=False
    )
