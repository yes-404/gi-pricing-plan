"""interval_for index

A quantile bound names the Model it bounds inside its spec document (`02` FR-199,
FR-200), so finding a model's bounds is a JSONB path lookup rather than a foreign
key. Every GBM prediction asks the question, and for almost every model the answer is
"none" — so the common case is the one that must stay cheap.

Partial on `interval_for IS NOT NULL`: a bound is a rare kind of model, and a full index
would carry one entry per model to answer a question about a handful of them.

Revision ID: 1c5e7a3245b8
Revises: e1f2a3b4c5d6
Create Date: 2026-08-19 13:12:42.328675+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "1c5e7a3245b8"
down_revision: str | None = "e1f2a3b4c5d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_models_interval_for_model_id
            ON models ((spec -> 'interval_for' ->> 'model_id'))
         WHERE spec -> 'interval_for' IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_models_interval_for_model_id")
