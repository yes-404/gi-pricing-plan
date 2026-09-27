"""modelling: the backtest artifact (`02` §4.12, FR-187)

A model measured on a Dataset Version it was **not** fitted on. Two things about the shape
are decisions rather than transcription, and both are stated in `02` §4.12 with this date.

**Not one per model.** `diagnostics` is one artifact per fitted model because FR-170
computes it once; a backtest is per *version*, and a model measured against four successive
quarters has four rows. Uniqueness is on `(model_id, dataset_version_id)` instead: re-running
one pair would produce a second answer to one question, with nothing to say which of the two
a monitoring review cited.

**Both immutability layers, not only privileges.** `a1b2c3d4e5f6` installed the trigger
pattern and gave the reason — revoking `UPDATE` from the *owner* does nothing, because
ownership carries implicit privileges. `diagnostics`, `model_comparisons` and
`transparency_artifacts` each took the privileges alone, so each is protected against the
application role and not against a direct connection. This table takes both; those three are
recorded as an open thread rather than migrated here, because they are a different
requirement's scope (FR-43) and not this slice's.

Revision ID: c9d0e1f2a3b4
Revises: b1c2d3e4f5a6
Create Date: 2026-08-18 12:40:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c9d0e1f2a3b4"
down_revision: str | None = "b1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.create_table(
        "backtests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.UniqueConstraint(
            "model_id", "dataset_version_id", name="uq_backtests_model_version"
        ),
    )
    op.create_index("ix_backtests_workspace", "backtests", ["workspace_id"])
    op.create_index("ix_backtests_model", "backtests", ["model_id", "computed_at"])
    op.create_index(
        "uq_backtests_job",
        "backtests",
        ["job_id"],
        unique=True,
        postgresql_where=sa.text("job_id IS NOT NULL"),
    )

    # Layer 1 — the application cannot attempt the write at all.
    op.execute(f"GRANT SELECT, INSERT ON backtests TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON backtests FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON backtests FROM PUBLIC")

    # Layer 2 — and the owner cannot either. `artifact_append_only()` is created by
    # `a1b2c3d4e5f6`, which this revision follows; the statement trigger is separate because
    # row triggers do not fire on TRUNCATE.
    op.execute("""
        CREATE TRIGGER backtests_no_modify
          BEFORE UPDATE OR DELETE ON backtests
          FOR EACH ROW EXECUTE FUNCTION artifact_append_only();
    """)
    op.execute("""
        CREATE TRIGGER backtests_no_truncate
          BEFORE TRUNCATE ON backtests
          FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS backtests_no_truncate ON backtests")
    op.execute("DROP TRIGGER IF EXISTS backtests_no_modify ON backtests")
    op.drop_index("uq_backtests_job", table_name="backtests")
    op.drop_index("ix_backtests_model", table_name="backtests")
    op.drop_index("ix_backtests_workspace", table_name="backtests")
    op.drop_table("backtests")
