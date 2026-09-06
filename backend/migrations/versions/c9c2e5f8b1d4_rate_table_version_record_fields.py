"""rate table version record fields

Adds the creation-record columns a `RateTableVersion` needs beyond its declarative
definition (slice W10-3C): `cells` holds the `BlobRef` of a `storage: parquet`
version's cells (FR-232 — above the threshold the cells are addressed by a
content-addressed blob rather than the `rate_table_cells` rows), and
`created_by_operation` / `created_by_import` hold the `BulkOperation` (04 §4.4) /
`ImportVerdict` (03 §4.2) records that name the operation or import which created the
version. The `definition` JSONB stays the `RateTable` shape — `extra="forbid"` refuses
these record fields there, and `RateTable.model_validate(definition)` is what the diff
path reads.

Revision ID: c9c2e5f8b1d4
Revises: a9c2e5f8b1d4
Create Date: 2026-08-28 15:10:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c9c2e5f8b1d4"
down_revision: str | None = "a9c2e5f8b1d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "rate_table_versions",
        sa.Column(
            "cells",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="BlobRef of the cells of a storage:parquet version (FR-232)",
        ),
    )
    op.add_column(
        "rate_table_versions",
        sa.Column(
            "created_by_operation",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="BulkOperation record of the operation that created the version "
            "(04 §4.4)",
        ),
    )
    op.add_column(
        "rate_table_versions",
        sa.Column(
            "created_by_import",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="ImportVerdict record of the import that created the version "
            "(03 §4.2)",
        ),
    )


def downgrade() -> None:
    op.drop_column("rate_table_versions", "created_by_import")
    op.drop_column("rate_table_versions", "created_by_operation")
    op.drop_column("rate_table_versions", "cells")
