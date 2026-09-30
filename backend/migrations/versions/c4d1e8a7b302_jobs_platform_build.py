"""jobs: platform_build, the build a Job ran on (WK-674 Slice 1, PL-1239 Task 3)

`00` FR-18. Nullable: a Job is `queued` until a worker starts it, and Jobs that ran before
this revision have no recorded build.

Revision ID: c4d1e8a7b302
Revises: a71c3e95d204
Create Date: 2026-09-29 23:30:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4d1e8a7b302"
down_revision: str | None = "a71c3e95d204"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("platform_build", sa.String(length=128), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "platform_build")
