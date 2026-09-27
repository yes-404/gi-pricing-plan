"""jobs: register the `metric.certify` JobKind value

`02` §5.1/FR-162. `metric.certify` has been in `model-schema` since this slice added
it and in no database — the same gap `d0e1f2a3b4c5` found and fixed for
`objective.certify`, and `peril_structure.reconcile` before that. It surfaces as
`invalid input value for enum job_kind` from inside `job_service.submit`, after the
`POST /custom-metrics/{id}/certify` route has validated everything it can see.

This migration does nothing else: `custom_metrics` and `metric_certificates` are
`61981ea8f274`'s tables, unchanged here.

Revision ID: 2b2e2a481fb1
Revises: 61981ea8f274
Create Date: 2026-08-19 12:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "2b2e2a481fb1"
down_revision: str | None = "61981ea8f274"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE job_kind ADD VALUE IF NOT EXISTS 'metric.certify' "
        "AFTER 'objective.certify'"
    )


def downgrade() -> None:
    # `job_kind` keeps `metric.certify`: PostgreSQL cannot drop an enum value, and a
    # downgrade that recreated the type would have to rewrite every `jobs` row to do it.
    pass
