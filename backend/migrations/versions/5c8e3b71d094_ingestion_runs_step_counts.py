"""ingestion_runs.step_counts

FR-31 (WK-1178, SL-1738, PL-1737 DP-S1 (i)): an ingestion run also records, per recipe step in
order, `name`, `rows_in`, `rows_out` and `rows_rejected`, so that rows read minus rows
rejected minus rows removed plus rows added equals rows written can be checked from the run
alone. The column is JSONB, NOT NULL, defaulting to `'[]'`, so every existing run reads as a
run with no recorded steps. Nothing is rewritten.

Downgrade drops the column. That is data-safe in the sense that matters here: the column holds
only a derived count of what the recipe did, every figure in it is recomputable by replaying
the version's stored recipe over its source (FR-41), and no other table references it.

Revision ID: 5c8e3b71d094
Revises: f2b6d90a4c17
Create Date: 2026-10-18 23:40:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "5c8e3b71d094"
down_revision: str | None = "f2b6d90a4c17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingestion_runs",
        sa.Column(
            "step_counts",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("ingestion_runs", "step_counts")
