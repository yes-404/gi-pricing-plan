"""environments, deployments and deployment requests (WK-674 Slice 2, PL-1392 Task 3)

`07` §4.2 (FR-428), `03` §4.12 (FR-267), `06` FR-356 and RL-1301 A. Three tables and one
column:

* `environments`: deployment-wide (no `workspace_id`, ADR-710). `slug` is immutable and
  unique across **all** rows, retired included (RL-1301 A.6); `requires_prior_environment`
  is the predecessor's slug. Seeded `dev` (1), `uat` (2, after `dev`), `prod` (3, after
  `uat`). The application role may `INSERT` and `UPDATE` (rename, retire), never `DELETE`.
* `deployment_requests`: the artifact that precedes a gated deploy, reference
  `deployment:<environment slug>@<n>`, so `slug` holds the Environment's slug. `evidence` is
  the two items pinned once at submission. **Slice 2a's `approval_guard()` is installed on
  it with the arguments `('deployment', 'slug')` and no `'flag'`** (PL-1392 Acceptance 13):
  the decision flag never satisfies it; only a decided approval request can write `approved`.
* `deployments`: a record, never updated or deleted (`00` FR-4); the application role has
  `SELECT` and `INSERT` only, and the owner is stopped too by the `artifact_append_only()`
  trigger pair (`deployments_no_modify`, `deployments_no_truncate`).
* `scoring_traces.deployment_id`: nullable foreign key. **Existing rows get null** (there was
  no Deployment to serve them) and keep their `environment` string, which stays a string.

**The credential pre-check runs first, before any DDL** (auditor-plans V2): an unrevoked,
unexpired API key whose `environment`, or a non-archived Service Account whose `environments`
list, names anything but `dev`, `uat` or `prod` stops the upgrade with the ids and the names.
An expired but unrevoked key does not block it: it is refused at authentication and nothing
revives it.

Revision ID: c4a81f6d2e95
Revises: 2f598e89d12c
Create Date: 2026-10-03 21:53:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c4a81f6d2e95"
down_revision: str | None = "2f598e89d12c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

#: The seeded Environments: slug, name, promotion order, predecessor slug.
SEEDS = (
    ("dev", "Development", 1, None),
    ("uat", "User acceptance", 2, "dev"),
    ("prod", "Production", 3, "uat"),
)
_SEED_SLUGS = tuple(slug for slug, *_ in SEEDS)

_UNKNOWN_KEYS = """
SELECT k.id, k.environment FROM api_keys k
WHERE k.revoked_at IS NULL AND k.expires_at > now() AND k.environment <> ALL(:seeds)
ORDER BY k.id
"""

_UNKNOWN_ACCOUNTS = """
SELECT s.id, e.value FROM service_accounts s
CROSS JOIN LATERAL jsonb_array_elements_text(s.environments) AS e(value)
WHERE s.archived_at IS NULL AND e.value <> ALL(:seeds)
ORDER BY s.id, e.value
"""


def _refuse_unknown_environments() -> None:
    bind = op.get_bind()
    seeds = list(_SEED_SLUGS)
    keys = bind.execute(sa.text(_UNKNOWN_KEYS).bindparams(seeds=seeds)).all()
    accounts = bind.execute(sa.text(_UNKNOWN_ACCOUNTS).bindparams(seeds=seeds)).all()
    if not keys and not accounts:
        return
    lines = [f"API key {k_id} names environment {name!r}" for k_id, name in keys]
    lines += [f"Service Account {a_id} lists environment {name!r}" for a_id, name in accounts]
    raise RuntimeError(
        "cannot create the Environment table while a credential names an environment other "
        f"than {', '.join(_SEED_SLUGS)} (WK-674 Slice 2, RL-1301 A.6). Revoke each key, and "
        "narrow or archive each Service Account, then run the upgrade again: " + "; ".join(lines)
    )


def upgrade() -> None:
    _refuse_unknown_environments()

    op.create_table(
        "environments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("promotion_order", sa.Integer(), nullable=False),
        sa.Column("requires_prior_environment", sa.String(64), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("slug", name="uq_environments_slug"),
        sa.ForeignKeyConstraint(
            ["requires_prior_environment"],
            ["environments.slug"],
            name=op.f("fk_environments_requires_prior_environment_environments"),
        ),
        sa.CheckConstraint(
            "promotion_order >= 1", name=op.f("ck_environments_promotion_order_positive")
        ),
    )
    for slug, name, order, prior in SEEDS:
        op.execute(
            sa.text(
                "INSERT INTO environments (id, slug, name, promotion_order, "
                "requires_prior_environment) "
                "VALUES (gen_random_uuid(), :slug, :name, :ord, :prior)"
            ).bindparams(slug=slug, name=name, ord=order, prior=prior)
        )

    op.create_table(
        "deployment_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating_version_ref", sa.String(100), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("evidence", postgresql.JSONB(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=False),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_deployment_requests_slug_version"
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name=op.f("fk_deployment_requests_environment_id_environments"),
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'review', 'approved', 'rejected', 'withdrawn', 'executed')",
            name=op.f("ck_deployment_requests_status_known"),
        ),
    )
    op.create_index(
        "ix_deployment_requests_environment", "deployment_requests", ["environment_id"]
    )
    # Slice 2a's guard function (migration a9f3c6d21b87) on the new table: the trigger
    # arguments are the artifact type and the slug column, with no `'flag'` mode, so the
    # decision flag never satisfies it. Its column list is the guard's own form.
    op.execute(
        "CREATE TRIGGER approval_guard BEFORE INSERT OR UPDATE OF "
        "status, workspace_id, slug, version ON deployment_requests "
        "FOR EACH ROW EXECUTE FUNCTION approval_guard('deployment', 'slug')"
    )

    op.create_table(
        "deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating_version_ref", sa.String(100), nullable=False),
        sa.Column("bundle_hash", sa.String(71), nullable=False),
        sa.Column("deployed_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "deployed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("deployment_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name=op.f("fk_deployments_environment_id_environments"),
        ),
        sa.ForeignKeyConstraint(
            ["deployment_request_id"],
            ["deployment_requests.id"],
            name=op.f("fk_deployments_deployment_request_id_deployment_requests"),
        ),
        sa.CheckConstraint(
            "bundle_hash ~ '^sha256:[a-f0-9]{64}$'",
            name=op.f("ck_deployments_bundle_hash_format"),
        ),
    )
    op.create_index(
        "ix_deployments_environment",
        "deployments",
        ["workspace_id", "environment_id", "deployed_at"],
    )

    op.add_column(
        "scoring_traces",
        sa.Column("deployment_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_scoring_traces_deployment_id_deployments"),
        "scoring_traces",
        "deployments",
        ["deployment_id"],
        ["id"],
    )

    # Layer 2 of the two `a1b2c3d4e5f6` describes: the grants below stop the application
    # role; revoking from the owner does nothing, so the pair of triggers (the function
    # `artifact_append_only()` already exists) stops everything else. A Deployment is a
    # record, never updated or deleted (`00` FR-4).
    op.execute(
        "CREATE TRIGGER deployments_no_modify BEFORE UPDATE OR DELETE ON deployments "
        "FOR EACH ROW EXECUTE FUNCTION artifact_append_only()"
    )
    op.execute(
        "CREATE TRIGGER deployments_no_truncate BEFORE TRUNCATE ON deployments "
        "FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only()"
    )

    op.execute(f"GRANT SELECT, INSERT, UPDATE ON environments TO {APP_ROLE}")
    op.execute(f"REVOKE DELETE ON environments FROM {APP_ROLE}")
    op.execute("REVOKE DELETE ON environments FROM PUBLIC")
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON deployment_requests TO {APP_ROLE}")
    op.execute(f"REVOKE DELETE ON deployment_requests FROM {APP_ROLE}")
    op.execute("REVOKE DELETE ON deployment_requests FROM PUBLIC")
    op.execute(f"GRANT SELECT, INSERT ON deployments TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON deployments FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON deployments FROM PUBLIC")


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_scoring_traces_deployment_id_deployments"), "scoring_traces", type_="foreignkey"
    )
    op.drop_column("scoring_traces", "deployment_id")
    op.drop_index("ix_deployments_environment", table_name="deployments")
    op.drop_table("deployments")  # drops its two triggers with it
    op.execute("DROP TRIGGER IF EXISTS approval_guard ON deployment_requests")
    op.drop_index("ix_deployment_requests_environment", table_name="deployment_requests")
    op.drop_table("deployment_requests")
    op.drop_table("environments")
