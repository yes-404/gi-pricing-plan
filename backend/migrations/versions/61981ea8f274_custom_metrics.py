"""modelling: custom metrics and their certificates

`02` §4.13, FR-MODEL-45, FR-MODEL-103/104/105. A Custom Metric is `CustomObjectiveRow`'s
sibling — versioned, referenced by name (`custom_metric:<slug>@<version>`), and its
definition frozen at insert by the same kind of trigger — because FR-MODEL-45 makes a
metric follow "the same lifecycle and grammar as objectives" and a `GbmSpec.eval_metrics`
ref resolved for early stopping must keep meaning what it meant when the fit ran under it.

**The definition is frozen at insert, by trigger**, over `slug`, `version`, `kind`,
`template`, `params`, `applicability` and `direction` — `CustomObjectiveRow`'s reasoning
applied unchanged. `hessian_strategy`/`hessian_min` have no equivalent here: a metric is
never differentiated (§4.13). Only the lifecycle columns move: `status`, `certificate_id`,
`approval_request_id`.

`direction` is constrained to **two** values, not `model_schema.comparison.MetricDirection`'s
four: `CustomMetric._direction_is_usable_for_stopping` (FR-MODEL-104) refuses
`closer_to_one_is_better` and `not_ordered` because early stopping compares successive
values and needs a monotone "better". `custom_metric_direction_is_usable_for_stopping`
mirrors that validator at the layer a direct `UPDATE` cannot walk past.

`metric_certificates` is insert-only, both at the privilege layer and by the row/statement
trigger pair `e1f2a3b4c5d6` established as the corrected pattern (FR-DATA-47) — `06` §4.2
makes it the required evidence for the approval, and evidence that can change after the
decision is not evidence.

Revision ID: 61981ea8f274
Revises: 1c5e7a3245b8
Create Date: 2026-08-19 21:38:38.222140+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "61981ea8f274"
down_revision: str | None = "1c5e7a3245b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

DEFINITION_IMMUTABLE = """
CREATE OR REPLACE FUNCTION custom_metrics_definition_immutable() RETURNS trigger AS $fn$
BEGIN
  IF NEW.slug IS DISTINCT FROM OLD.slug
     OR NEW.version IS DISTINCT FROM OLD.version
     OR NEW.kind IS DISTINCT FROM OLD.kind
     OR NEW.template IS DISTINCT FROM OLD.template
     OR NEW.params IS DISTINCT FROM OLD.params
     OR NEW.applicability IS DISTINCT FROM OLD.applicability
     OR NEW.direction IS DISTINCT FROM OLD.direction THEN
    RAISE EXCEPTION
      'a Custom Metric''s definition is immutable (02 FR-MODEL-45/103/104): % rejected', TG_OP
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'Create the next version and certify it. Every GbmSpec.eval_metrics ref '
                   'citing custom_metric:<slug>@<version> resolves to this row, so editing '
                   'the definition here redefines the metric an already-fitted model early '
                   'stopped on and nothing about that model would change to show it.';
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.create_table(
        "custom_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("kind", sa.String(16), nullable=False, server_default="template"),
        sa.Column("template", sa.String(32)),
        sa.Column("params", postgresql.JSONB(), nullable=False),
        sa.Column("applicability", postgresql.JSONB(), nullable=False),
        sa.Column("direction", sa.String(32), nullable=False),
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
            "workspace_id", "slug", "version", name="uq_custom_metrics_slug_version"
        ),
        sa.CheckConstraint("version >= 1", name="custom_metric_version_starts_at_one"),
        sa.CheckConstraint(
            "status IN ('draft', 'certified', 'review', 'approved', 'deprecated')",
            name="custom_metric_status_is_in_the_lifecycle",
        ),
        # FR-MODEL-104, mirroring `CustomMetric._direction_is_usable_for_stopping`: only the
        # two `MetricDirection` members an early-stopping loop can compare, not all four.
        sa.CheckConstraint(
            "direction IN ('lower_is_better', 'higher_is_better')",
            name="custom_metric_direction_is_usable_for_stopping",
        ),
    )
    op.create_index(
        "ix_custom_metrics_slug_status", "custom_metrics", ["workspace_id", "slug", "status"]
    )

    op.create_table(
        "metric_certificates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("custom_metric_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_version", sa.Integer(), nullable=False),
        sa.Column(
            "certified_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("metric_version >= 1", name="metric_certificate_version_starts_at_one"),
    )
    op.create_index(
        "ix_metric_certificates_metric",
        "metric_certificates",
        ["workspace_id", "custom_metric_id", "certified_at"],
    )

    op.execute(DEFINITION_IMMUTABLE)
    op.execute("""
        CREATE TRIGGER custom_metrics_definition_immutable
          BEFORE UPDATE ON custom_metrics
          FOR EACH ROW EXECUTE FUNCTION custom_metrics_definition_immutable();
    """)
    # `artifact_append_only()` already exists (`a1b2c3d4e5f6`); this only attaches it, on
    # the row-plus-statement pattern `e1f2a3b4c5d6` corrected `objective_certificates` to.
    op.execute("""
        CREATE TRIGGER metric_certificates_no_modify
          BEFORE UPDATE OR DELETE ON metric_certificates
          FOR EACH ROW EXECUTE FUNCTION artifact_append_only();
    """)
    op.execute("""
        CREATE TRIGGER metric_certificates_no_truncate
          BEFORE TRUNCATE ON metric_certificates
          FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
    """)

    op.execute(f"GRANT SELECT, INSERT, UPDATE ON custom_metrics TO {APP_ROLE}")
    op.execute(f"REVOKE DELETE ON custom_metrics FROM {APP_ROLE}")
    op.execute("REVOKE DELETE ON custom_metrics FROM PUBLIC")
    op.execute(f"GRANT SELECT, INSERT ON metric_certificates TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON metric_certificates FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON metric_certificates FROM PUBLIC")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS metric_certificates_no_truncate ON metric_certificates")
    op.execute("DROP TRIGGER IF EXISTS metric_certificates_no_modify ON metric_certificates")
    op.execute("DROP TRIGGER IF EXISTS custom_metrics_definition_immutable ON custom_metrics")
    op.execute("DROP FUNCTION IF EXISTS custom_metrics_definition_immutable()")
    op.drop_index("ix_metric_certificates_metric", table_name="metric_certificates")
    op.drop_table("metric_certificates")
    op.drop_index("ix_custom_metrics_slug_status", table_name="custom_metrics")
    op.drop_table("custom_metrics")
