"""dislocation runs: the persisted DislocationRun record (WK-673 Slice 4, PL-1501 Task 2)

`03` §4.6, FR-263, FR-265. One row per Dislocation Run: the validated `DislocationRun` as
JSONB, with the baseline and candidate refs and bundle hashes, the portfolio Dataset Version,
the Job id and `movers_blob_sha256` copied out for the lookups (Slice 5's, by candidate ref
and bundle hash). `job_id` is unique: a Job persists at most one run. The movers digest is
an indexed scalar but is not registered in `QUOTE_INPUT_BLOB_COLUMNS` (RL-1504 item 5).

Revision ID: b8d2f4a6c0e1
Revises: f3a7c1d9e2b4
Create Date: 2026-10-09 14:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b8d2f4a6c0e1"
down_revision: str | None = "f3a7c1d9e2b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dislocation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run", postgresql.JSONB(), nullable=False),
        sa.Column("baseline_ref", sa.String(100), nullable=False),
        sa.Column("candidate_ref", sa.String(100), nullable=False),
        sa.Column("baseline_bundle_hash", sa.String(71), nullable=False),
        sa.Column("candidate_bundle_hash", sa.String(71), nullable=False),
        sa.Column("portfolio_dataset_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("movers_blob_sha256", sa.String(64), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint("job_id", name="uq_dislocation_runs_job_id"),
    )
    op.create_index(
        "ix_dislocation_runs_candidate", "dislocation_runs",
        ["workspace_id", "candidate_ref", "candidate_bundle_hash"],
    )
    op.create_index(
        "ix_dislocation_runs_movers_blob_sha256", "dislocation_runs", ["movers_blob_sha256"]
    )


def downgrade() -> None:
    op.drop_index("ix_dislocation_runs_movers_blob_sha256", table_name="dislocation_runs")
    op.drop_index("ix_dislocation_runs_candidate", table_name="dislocation_runs")
    op.drop_table("dislocation_runs")
