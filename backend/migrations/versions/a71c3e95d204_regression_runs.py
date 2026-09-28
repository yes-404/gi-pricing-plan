"""regression runs: the persisted RegressionRun record (WK-672 Slice 3, PL-1205 Task 5)

`03` §4.9, FR-260, FR-261, FR-9301. One row per Regression Run of a Rating Version: the
validated `RegressionRun` as JSONB, with `bundle_hash`, `suite_content_hash`, `overall` and
`finished_at` copied out for the submit gate's lookup, and `cases_blob_sha256` — the
case log's digest as an indexed scalar, so the generic blob route's deny (which matches a
registered column by equality) can refuse it.

Revision ID: a71c3e95d204
Revises: fb705749c5d9
Create Date: 2026-09-28 21:30:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a71c3e95d204"
down_revision: str | None = "fb705749c5d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "regression_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "rating_version_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rating_versions.id"), nullable=False,
        ),
        sa.Column("run", postgresql.JSONB(), nullable=False),
        sa.Column("bundle_hash", sa.String(71), nullable=False),
        sa.Column("suite_content_hash", sa.String(71), nullable=False),
        sa.Column("overall", sa.String(8), nullable=False),
        sa.Column("cases_blob_sha256", sa.String(64), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index(
        "ix_regression_runs_latest", "regression_runs",
        ["rating_version_id", "bundle_hash", "suite_content_hash", "finished_at"],
    )
    op.create_index(
        "ix_regression_runs_cases_blob_sha256", "regression_runs", ["cases_blob_sha256"]
    )


def downgrade() -> None:
    op.drop_index("ix_regression_runs_cases_blob_sha256", table_name="regression_runs")
    op.drop_index("ix_regression_runs_latest", table_name="regression_runs")
    op.drop_table("regression_runs")
