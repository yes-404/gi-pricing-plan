"""modelling: the comparison artifact

`02` FR-186's persisted comparison, and the first table in this repository whose shape
was **designed** rather than transcribed: `02` §5.2 named `ModelComparison` as a return type
from Phase 0 and no document defined it.

**Insert-only at the privilege layer** (FR-43), like `diagnostics` and validation
reports. `06` §3.3 makes a comparison required evidence for a Model approval where a
predecessor exists, and evidence that can change after the approval is not evidence. The
type refuses a rewrite too; this is the layer that survives a direct `UPDATE`.

No `model_ids` column. The refs live in the payload, and a column enumerating them would be
a second statement of the same fact — one the payload could contradict. When something needs
"which comparisons cite this model", it arrives with the requirement that asks for it.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-17 15:10:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f6a7b8c9d0e1"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.create_table(
        "model_comparisons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_index(
        "ix_model_comparisons_workspace", "model_comparisons", ["workspace_id"]
    )
    # One artifact per Job. A second row for one Job would mean a comparison was recorded
    # twice, and nothing could say which of the two an approval cited.
    op.create_index(
        "uq_model_comparisons_job",
        "model_comparisons",
        ["job_id"],
        unique=True,
        postgresql_where=sa.text("job_id IS NOT NULL"),
    )

    op.execute(f"GRANT SELECT, INSERT ON model_comparisons TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON model_comparisons FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON model_comparisons FROM PUBLIC")


def downgrade() -> None:
    op.drop_index("uq_model_comparisons_job", table_name="model_comparisons")
    op.drop_index("ix_model_comparisons_workspace", table_name="model_comparisons")
    op.drop_table("model_comparisons")
