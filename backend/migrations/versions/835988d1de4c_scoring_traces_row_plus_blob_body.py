"""scoring traces: row plus blob body (WK-671 Task 4A)

`03` §4.5's `Trace`, FR-258/259, `00` NFR-459, RL-888
(`docs/rulings/INDEX.md#2026-08-29-w11-slices-3-4-rulingsmd`). A thin queryable row beside the trace
body, which lives content-addressed in the blob store — never a full JSON column, per
NFR-500's 200 GB/year budget.

**No privilege revocation on `UPDATE`/`DELETE` the way `model_comparisons` and the
`custom_objectives`/`custom_metrics` family get one.** Those rows are permanently
immutable and permanently undeletable; a `scoring_traces` row is neither — NFR-459 is a
*floor*, not a ban, so an application-level guard (`app.platform.traces.delete_trace`)
must be able to delete a row once it clears ≥ 13 months, which a `REVOKE DELETE` would make
impossible for every row for ever. `UPDATE` is revoked: a trace, once written, is never
edited, only (eventually) deleted.

Revision ID: 835988d1de4c
Revises: d5e6f7a8b9c0
Create Date: 2026-08-30 15:54:18.220344+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "835988d1de4c"
down_revision: str | None = "d5e6f7a8b9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.create_table(
        "scoring_traces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_id", sa.String(length=128), nullable=True),
        sa.Column("rating_version_ref", sa.String(length=100), nullable=False),
        sa.Column("bundle_hash", sa.String(length=71), nullable=False),
        sa.Column("sample_reason", sa.String(length=16), nullable=False),
        sa.Column("environment", sa.String(length=32), nullable=True),
        sa.Column("blob_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "bundle_hash ~ '^sha256:[a-f0-9]{64}$'",
            name=op.f("ck_scoring_traces_bundle_hash_format"),
        ),
        sa.CheckConstraint(
            "blob_sha256 ~ '^[a-f0-9]{64}$'",
            name=op.f("ck_scoring_traces_blob_sha256_format"),
        ),
        sa.CheckConstraint(
            "sample_reason IN ('rate', 'decline', 'error')",
            name=op.f("ck_scoring_traces_sample_reason_known"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scoring_traces")),
    )
    op.create_index(
        "ix_scoring_traces_workspace_rating_version",
        "scoring_traces",
        ["workspace_id", "rating_version_ref"],
    )
    op.create_index(
        "ix_scoring_traces_created_at", "scoring_traces", ["created_at"]
    )

    op.execute(f"GRANT SELECT, INSERT, DELETE ON scoring_traces TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE ON scoring_traces FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE ON scoring_traces FROM PUBLIC")


def downgrade() -> None:
    op.drop_index("ix_scoring_traces_created_at", table_name="scoring_traces")
    op.drop_index(
        "ix_scoring_traces_workspace_rating_version", table_name="scoring_traces"
    )
    op.drop_table("scoring_traces")
