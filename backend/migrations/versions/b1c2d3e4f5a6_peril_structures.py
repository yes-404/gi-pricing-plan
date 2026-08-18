"""peril structures and their reconciliation (`02` §4.10, FR-MODEL-58..61)

The table `03-rating-engine.md` will reference: FR-MODEL-61 makes a Rating Version cite one
Peril Structure rather than a scatter of individual models.

Two guards, both the shape `models` uses one table over:

* **the composition freezes when the reconciliation is written.** A reconciliation measures
  a specific set of per-peril models; editing the set afterwards leaves a number attached to
  a composition that never produced it. Conditional rather than append-only, because
  `record_reconciliation` legitimately updates the row once — exactly why
  `models_fit_immutable` is conditional too;
* **a reconciled structure cannot be deleted.** It is the evidence an approval was granted
  against, and `06` FR-GOV-14 resolves an approval to the artifact version it cited.

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f7
Create Date: 2026-08-18 09:40:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b1c2d3e4f5a6"
down_revision: str | None = "a1b2c3d4e5f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

COMPOSITION_IMMUTABLE = """
CREATE OR REPLACE FUNCTION peril_structures_composition_immutable() RETURNS trigger AS $fn$
BEGIN
  IF OLD.reconciliation IS NOT NULL THEN
    IF NEW.perils IS DISTINCT FROM OLD.perils
       OR NEW.excluded_perils IS DISTINCT FROM OLD.excluded_perils THEN
      RAISE EXCEPTION
        'a reconciled Peril Structure''s composition is immutable (02 FR-MODEL-60): % rejected',
        TG_OP
        USING ERRCODE = 'insufficient_privilege',
              HINT = 'Create the next version. The reconciliation measured this set of '
                     'per-peril models; changing the set leaves the number attached to a '
                     'composition that never produced it.';
    END IF;
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""

RECONCILED_UNDELETABLE = """
CREATE OR REPLACE FUNCTION peril_structures_reconciled_undeletable() RETURNS trigger AS $fn$
BEGIN
  IF OLD.reconciliation IS NOT NULL THEN
    RAISE EXCEPTION
      'a reconciled Peril Structure cannot be deleted (02 FR-MODEL-60)'
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'Archive it. An approval resolves to the artifact version it cited.';
  END IF;
  RETURN OLD;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    # **`job_kind` is a Postgres ENUM, not a check constraint**, and this is the first slice
    # to add a kind — every earlier one was in the type as originally created. Without this
    # the Job row is refused by the database with `invalid input value for enum job_kind`,
    # from inside `job_service.submit`, after the route has already validated everything it
    # can see. `ADD VALUE` is allowed inside a transaction on PostgreSQL 12+ provided the
    # new value is not *used* in the same one, which it is not.
    op.execute(
        "ALTER TYPE job_kind ADD VALUE IF NOT EXISTS 'peril_structure.reconcile' "
        "AFTER 'model.compare'"
    )

    op.create_table(
        "peril_structures",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("perils", postgresql.JSONB(), nullable=False),
        sa.Column(
            "excluded_perils", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column("reconciliation", postgresql.JSONB()),
        sa.Column("job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_peril_structures_slug_version"
        ),
        sa.CheckConstraint("version >= 1", name="peril_structure_version_starts_at_one"),
        sa.CheckConstraint(
            "status IN ('draft', 'reconciled', 'review', 'approved', 'superseded', "
            "'archived')",
            name="peril_structure_status_is_in_the_lifecycle",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'archived') OR reconciliation IS NOT NULL",
            name="reconciled_peril_structure_has_a_reconciliation",
        ),
    )
    op.create_index(
        "ix_peril_structures_slug_status",
        "peril_structures",
        ["workspace_id", "slug", "status"],
    )

    op.execute(COMPOSITION_IMMUTABLE)
    op.execute(RECONCILED_UNDELETABLE)
    op.execute("""
        CREATE TRIGGER peril_structures_composition_immutable
          BEFORE UPDATE ON peril_structures
          FOR EACH ROW EXECUTE FUNCTION peril_structures_composition_immutable();
    """)
    op.execute("""
        CREATE TRIGGER peril_structures_reconciled_undeletable
          BEFORE DELETE ON peril_structures
          FOR EACH ROW EXECUTE FUNCTION peril_structures_reconciled_undeletable();
    """)
    op.execute("""
        CREATE TRIGGER peril_structures_no_truncate
          BEFORE TRUNCATE ON peril_structures
          FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
    """)
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON peril_structures TO {APP_ROLE}")
    op.execute(f"REVOKE DELETE ON peril_structures FROM {APP_ROLE}")
    op.execute("REVOKE DELETE ON peril_structures FROM PUBLIC")


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS peril_structures_no_truncate ON peril_structures"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS peril_structures_reconciled_undeletable "
        "ON peril_structures"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS peril_structures_composition_immutable ON peril_structures"
    )
    op.execute("DROP FUNCTION IF EXISTS peril_structures_reconciled_undeletable()")
    op.execute("DROP FUNCTION IF EXISTS peril_structures_composition_immutable()")
    op.drop_index("ix_peril_structures_slug_status", table_name="peril_structures")
    op.drop_table("peril_structures")
    # `peril_structure.reconcile` stays in `job_kind`. PostgreSQL cannot remove an enum
    # value, and rebuilding the type would rewrite every historical `jobs` row to drop a
    # label none of them uses — a downgrade with more blast radius than the upgrade.
