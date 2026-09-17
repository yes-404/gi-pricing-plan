"""modelling: diagnostics, and the invariant the spine could not state

Three changes, one slice (`02` §3.8, §4.8).

* **`diagnostics`** — one artifact per fitted model, insert-only at the privilege layer
  like every other artifact (FR-43). FR-170 makes diagnostics computed once at
  fit time and read thereafter, so a diagnostics row that could be updated would let the
  evidence behind an approval change after the approval. Unique on `model_id`: a second
  set of diagnostics for one model is either a recomputation the requirement forbids or a
  silent overwrite of what an approver read.

* **`models.diagnostics_id`, and the CHECK that goes with it.** `02` §4.8 says
  `status >= fitted` implies diagnostics are set. The spine enforced only the `fit_result`
  half because diagnostics did not exist; this adds the other half at the layer that
  survives a direct `UPDATE`. Existing rows are backfilled below rather than left to fail
  the constraint.

* **No backfill of *content*.** Any model already at `fitted` was fitted before diagnostics
  existed, so there is nothing to compute from — the rows are moved to `draft` instead.
  Inventing an empty diagnostics artifact to satisfy the constraint would put a row on
  screen that reads as evidence and contains none, which is worse than a model visibly
  needing a refit.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-16 09:40:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.create_table(
        "diagnostics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.UniqueConstraint("model_id", name="uq_diagnostics_model"),
    )
    op.create_index("ix_diagnostics_workspace", "diagnostics", ["workspace_id"])

    op.add_column(
        "models",
        sa.Column("diagnostics_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # A model fitted before this slice has coefficients and no evidence. It cannot satisfy
    # the new invariant and nothing can compute its diagnostics after the fact — the frames
    # it was fitted on are not necessarily still the version's current tables. Returning it
    # to `draft` says exactly that: it must be refitted to be used.
    op.execute(
        "UPDATE models SET status = 'draft' "
        "WHERE status NOT IN ('draft', 'archived') AND diagnostics_id IS NULL"
    )

    op.create_check_constraint(
        "fitted_model_has_diagnostics",
        "models",
        "status IN ('draft', 'archived') OR diagnostics_id IS NOT NULL",
    )

    # FR-43's artifact discipline: insert and read, never rewrite.
    op.execute(f"GRANT SELECT, INSERT ON diagnostics TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON diagnostics FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON diagnostics FROM PUBLIC")


def downgrade() -> None:
    op.drop_constraint("fitted_model_has_diagnostics", "models", type_="check")
    op.drop_column("models", "diagnostics_id")
    op.drop_index("ix_diagnostics_workspace", table_name="diagnostics")
    op.drop_table("diagnostics")
