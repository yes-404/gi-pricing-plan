"""modelling: the transparency artifact

`02` FR-MODEL-33..37 and R3 — fitting a black box is allowed, pricing with an unexplained
one is not. This is where the explanation lives.

**Insert-only at the privilege layer** (FR-DATA-42), like `diagnostics` and
`model_comparisons`: FR-MODEL-36 makes this the evidence a Rating Version's approval is
granted against, and evidence that can change after the decision is not evidence.

**No unique constraint on `model_id`**, which is where this differs from `diagnostics`.
FR-MODEL-33 says *at least one* artifact and allows both forms; a SHAP summary recomputed
on a larger sample is a second artifact, not a correction of the first. The read path takes
the most recent, and the older rows stay because an approval that cited one must still
resolve to it.

Revision ID: a1b2c3d4e5f7
Revises: f6a7b8c9d0e1
Create Date: 2026-08-17 18:05:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f7"
down_revision: str | None = "f6a7b8c9d0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.create_table(
        "transparency_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    # Ordered by `created_at` because every read is "the latest for this model".
    op.create_index(
        "ix_transparency_model",
        "transparency_artifacts",
        ["workspace_id", "model_id", "created_at"],
    )

    op.execute(f"GRANT SELECT, INSERT ON transparency_artifacts TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON transparency_artifacts FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON transparency_artifacts FROM PUBLIC")


def downgrade() -> None:
    op.drop_index("ix_transparency_model", table_name="transparency_artifacts")
    op.drop_table("transparency_artifacts")
