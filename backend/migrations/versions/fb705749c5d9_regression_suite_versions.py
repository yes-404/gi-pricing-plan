"""regression suites: the versioned golden-quote store (WK-672 Slice 2, PL-1189 Task 4)

`03` FR-260, §4.7; NFR-499. A Regression Suite is its own versioned artifact, bound to
one Rating Algorithm by `algorithm_slug` and never approvable (the deputy's DP-S2-1 (A)).

- `regression_suites` is the registry: unique on `(workspace_id, slug)` **and** on
  `(workspace_id, algorithm_slug)` — one suite per algorithm, enforced by the database
  rather than by a check-then-insert that two writers could race (audit finding F6).
- `regression_suite_versions` holds each immutable version's validated content (golden
  quote contexts included, which is why every read is permission-checked) and its
  `content_hash`; unique on `(suite_id, version)`, so a version-number race is a 409,
  not a duplicate (re-audit N3).

Revision ID: fb705749c5d9
Revises: d3b955a63d6a
Create Date: 2026-09-28 16:18:58+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "fb705749c5d9"
down_revision: str | None = "d3b955a63d6a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "regression_suites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("algorithm_slug", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint("workspace_id", "slug", name="uq_regression_suites_slug"),
        sa.UniqueConstraint(
            "workspace_id", "algorithm_slug", name="uq_regression_suites_algorithm"
        ),
    )
    op.create_table(
        "regression_suite_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "suite_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("regression_suites.id"), nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(71), nullable=False),
        sa.Column("change_note", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint(
            "suite_id", "version", name="uq_regression_suite_versions_version"
        ),
    )


def downgrade() -> None:
    op.drop_table("regression_suite_versions")
    op.drop_table("regression_suites")
