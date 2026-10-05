"""jobs: register the `rate_table.diff_cells` JobKind value

`03` §5.1/FR-231/FR-232 (`RL-1418`, WK-673 Slice 7). The paged diff-cells route answers 202
with a `rate_table.diff_cells` Job where either version is `storage: parquet`, a kind of its
own so that `rate_table.diff` and the artifact its summary route returns do not change.
Without this value the Job's INSERT fails with `invalid input value for enum job_kind`, as
`d5e6f7a8b9c0` found for `rate_table.diff` before it.

This migration does nothing else: the `jobs` table is `df53696a2682`'s, unchanged here; the
`compute` queue value it needs already exists.

Revision ID: f3a7c1d9e2b4
Revises: e5b7d9f1a3c6
Create Date: 2026-10-05 18:30:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "f3a7c1d9e2b4"
down_revision: str | None = "e5b7d9f1a3c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE job_kind ADD VALUE IF NOT EXISTS 'rate_table.diff_cells' "
        "AFTER 'rate_table.diff'"
    )


def downgrade() -> None:
    # `job_kind` keeps `rate_table.diff_cells`: PostgreSQL cannot drop an enum value, and a
    # downgrade that recreated the type would have to rewrite every `jobs` row to do it.
    pass
