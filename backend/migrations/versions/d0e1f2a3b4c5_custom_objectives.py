"""modelling: custom objectives and their certificates

`02` §4.5/§4.7, FR-142, FR-143, FR-144, FR-145, FR-146, FR-152, FR-153, FR-154, FR-163, FR-164. A Custom Objective is a named, versioned loss a Model Spec
references by name, so the row is shaped like `peril_structures` — slug, version, lifecycle,
approval request — rather than like `diagnostics`, which is only ever reached by id.

**The definition is frozen at insert, by trigger.** FR-163 says editing an approved
objective creates a new version needing fresh certification; the trigger is what makes that
true of the *database* rather than only of the service. A model fitted in March resolves
`custom_objective:capped-gamma@2` and must get the loss it was fitted under — an `UPDATE`
to `params` would silently redefine every model that ever cited it, and nothing about the
model row would change to show it.

Only the lifecycle columns move: `status`, `certificate_id`, `approval_request_id`.

`objective_certificates` is **insert-only at the privilege layer** (FR-43), like
`transparency_artifacts`: `06` §4.2 makes it the required evidence for the approval, and
evidence that can change after the decision is not evidence.

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-08-18 12:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d0e1f2a3b4c5"
down_revision: str | None = "c9d0e1f2a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

DEFINITION_IMMUTABLE = """
CREATE OR REPLACE FUNCTION custom_objectives_definition_immutable() RETURNS trigger AS $fn$
BEGIN
  IF NEW.slug IS DISTINCT FROM OLD.slug
     OR NEW.version IS DISTINCT FROM OLD.version
     OR NEW.kind IS DISTINCT FROM OLD.kind
     OR NEW.template IS DISTINCT FROM OLD.template
     OR NEW.params IS DISTINCT FROM OLD.params
     OR NEW.applicability IS DISTINCT FROM OLD.applicability
     OR NEW.hessian_strategy IS DISTINCT FROM OLD.hessian_strategy
     OR NEW.hessian_min IS DISTINCT FROM OLD.hessian_min THEN
    RAISE EXCEPTION
      'a Custom Objective''s definition is immutable (02 FR-163): % rejected', TG_OP
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'Create the next version and certify it. Every Model Spec citing '
                   'custom_objective:<slug>@<version> resolves to this row, so editing '
                   'the loss here redefines what those models were fitted under and '
                   'nothing on the model would change to show it.';
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""

CERTIFIED_UNDELETABLE = """
CREATE OR REPLACE FUNCTION custom_objectives_undeletable() RETURNS trigger AS $fn$
BEGIN
  RAISE EXCEPTION 'a Custom Objective cannot be deleted (02 FR-164)'
    USING ERRCODE = 'insufficient_privilege',
          HINT = 'Deprecate it. FR-164 is the blast-radius query, and it can only '
                 'answer "which models used this loss?" while the row is still there.';
  RETURN OLD;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    # `job_kind` is a Postgres ENUM. `objective.certify` has been in `model-schema` since
    # the spine and in no database — the same gap `peril_structure.reconcile` found, and it
    # surfaces as `invalid input value for enum job_kind` from inside `job_service.submit`,
    # after the route has validated everything it can see.
    op.execute(
        "ALTER TYPE job_kind ADD VALUE IF NOT EXISTS 'objective.certify' "
        "AFTER 'peril_structure.reconcile'"
    )

    op.create_table(
        "custom_objectives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("kind", sa.String(16), nullable=False, server_default="template"),
        sa.Column("template", sa.String(32)),
        sa.Column("params", postgresql.JSONB(), nullable=False),
        sa.Column("applicability", postgresql.JSONB(), nullable=False),
        sa.Column(
            "hessian_strategy", sa.String(16), nullable=False, server_default="clip_to_min"
        ),
        sa.Column("hessian_min", sa.Float(), nullable=False, server_default="0.000001"),
        sa.Column("description", sa.Text()),
        sa.Column("certificate_id", postgresql.UUID(as_uuid=True)),
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_custom_objectives_slug_version"
        ),
        sa.CheckConstraint("version >= 1", name="custom_objective_version_starts_at_one"),
        sa.CheckConstraint("hessian_min > 0", name="custom_objective_hessian_min_is_positive"),
        sa.CheckConstraint(
            "status IN ('draft', 'certified', 'review', 'approved', 'deprecated')",
            name="custom_objective_status_is_in_the_lifecycle",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'deprecated') OR certificate_id IS NOT NULL",
            name="certified_objective_has_a_certificate",
        ),
        sa.CheckConstraint(
            "kind = 'template' AND template IS NOT NULL",
            name="custom_objective_is_a_template_in_phase_1",
        ),
    )
    op.create_index(
        "ix_custom_objectives_slug_status",
        "custom_objectives",
        ["workspace_id", "slug", "status"],
    )

    op.create_table(
        "objective_certificates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("custom_objective_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("objective_version", sa.Integer(), nullable=False),
        sa.Column(
            "certified_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("objective_version >= 1", name="certificate_version_starts_at_one"),
    )
    op.create_index(
        "ix_objective_certificates_objective",
        "objective_certificates",
        ["workspace_id", "custom_objective_id", "certified_at"],
    )

    op.execute(DEFINITION_IMMUTABLE)
    op.execute(CERTIFIED_UNDELETABLE)
    op.execute("""
        CREATE TRIGGER custom_objectives_definition_immutable
          BEFORE UPDATE ON custom_objectives
          FOR EACH ROW EXECUTE FUNCTION custom_objectives_definition_immutable();
    """)
    op.execute("""
        CREATE TRIGGER custom_objectives_undeletable
          BEFORE DELETE ON custom_objectives
          FOR EACH ROW EXECUTE FUNCTION custom_objectives_undeletable();
    """)
    op.execute("""
        CREATE TRIGGER custom_objectives_no_truncate
          BEFORE TRUNCATE ON custom_objectives
          FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
    """)
    op.execute("""
        CREATE TRIGGER objective_certificates_no_truncate
          BEFORE TRUNCATE ON objective_certificates
          FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
    """)

    op.execute(f"GRANT SELECT, INSERT, UPDATE ON custom_objectives TO {APP_ROLE}")
    op.execute(f"REVOKE DELETE ON custom_objectives FROM {APP_ROLE}")
    op.execute("REVOKE DELETE ON custom_objectives FROM PUBLIC")
    op.execute(f"GRANT SELECT, INSERT ON objective_certificates TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON objective_certificates FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON objective_certificates FROM PUBLIC")


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS objective_certificates_no_truncate ON objective_certificates"
    )
    op.execute("DROP TRIGGER IF EXISTS custom_objectives_no_truncate ON custom_objectives")
    op.execute("DROP TRIGGER IF EXISTS custom_objectives_undeletable ON custom_objectives")
    op.execute(
        "DROP TRIGGER IF EXISTS custom_objectives_definition_immutable ON custom_objectives"
    )
    op.execute("DROP FUNCTION IF EXISTS custom_objectives_undeletable()")
    op.execute("DROP FUNCTION IF EXISTS custom_objectives_definition_immutable()")
    op.drop_index("ix_objective_certificates_objective", table_name="objective_certificates")
    op.drop_table("objective_certificates")
    op.drop_index("ix_custom_objectives_slug_status", table_name="custom_objectives")
    op.drop_table("custom_objectives")
    # `job_kind` keeps `objective.certify`: PostgreSQL cannot drop an enum value, and a
    # downgrade that recreated the type would have to rewrite every `jobs` row to do it.
