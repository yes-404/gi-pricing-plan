"""jobs: register the `rate_table.diff` JobKind value

`03` §5.1/FR-232 (W10-3D). `rate_table.diff` has been in `model-schema` since
W10-3A declared it and in no database — the same gap `2b2e2a481fb1` found and fixed
for `metric.certify`, and `d0e1f2a3b4c5` for `objective.certify` before that. It
surfaces as `invalid input value for enum job_kind` from inside `job_service.submit`,
after the `GET /rate-tables/{slug}@{version}/diff` route has answered 202.

This migration does nothing else: the `jobs` table is `df53696a2682`'s, unchanged
here; the `compute` queue value it needs already exists.

Revision ID: d5e6f7a8b9c0
Revises: c9c2e5f8b1d4
Create Date: 2026-08-28 16:05:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: str | None = "c9c2e5f8b1d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE job_kind ADD VALUE IF NOT EXISTS 'rate_table.diff' "
        "AFTER 'metric.certify'"
    )


def downgrade() -> None:
    # `job_kind` keeps `rate_table.diff`: PostgreSQL cannot drop an enum value, and a
    # downgrade that recreated the type would have to rewrite every `jobs` row to do it.
    pass
