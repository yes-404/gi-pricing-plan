"""environment settings: the Environment layer of the Setting resolver (WK-674 Slice 3, PL-1583)

`07` §3.8 FR-446 (four layers), FR-431 (Environment configuration is a Setting, audited on
change), `RL-1311`. One row per (Environment, key); only set values are stored, so the layer
is silent where no row exists. No backfill, and the migration touches no existing table: in
particular existing `api_keys` rows are unchanged (a secret is shown once, FR-389).

Revision ID: c5a91e7d3b26
Revises: b8d2f4a6c0e1
Create Date: 2026-10-10 23:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c5a91e7d3b26"
down_revision: str | None = "b8d2f4a6c0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "environment_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "environment_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("environments.id"), nullable=False,
        ),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "environment_id", "key", name="uq_environment_settings_environment_key"
        ),
    )


def downgrade() -> None:
    op.drop_table("environment_settings")
