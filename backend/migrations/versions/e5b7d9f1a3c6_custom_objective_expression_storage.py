"""custom_objectives: store the expression arm (WK-690 Slice 3, PL-1382 Task 2)

`02` §4.6, FR-144, FR-163. Four nullable columns carry the `expression` arm —
`bound_symbols`, `parameters`, `loss`, `derived` — and the Phase 1 CHECK
`custom_objective_is_a_template_in_phase_1` is replaced by a kind-arm CHECK: a `template`
row names its template and carries none of them, an `expression` row carries its loss,
symbols and parameters and names no template.

The definition trigger gains the three definition columns (`loss`, `parameters`,
`bound_symbols`), and a rule for `derived`: it may change only from NULL, only while the
row is a `draft`. A trigger that allowed NULL to a value without reading `status` would
allow it after the draft too.

The downgrade refuses while an `expression` row exists: the old CHECK would reject it, and
dropping the columns would lose the loss it was fitted under.

Revision ID: e5b7d9f1a3c6
Revises: c4a81f6d2e95
Create Date: 2026-10-04 17:30:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e5b7d9f1a3c6"
down_revision: str | None = "c4a81f6d2e95"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Bare names: `NAMING_CONVENTION` adds the `ck_<table>_` prefix in `op.*`.
OLD_CHECK = "custom_objective_is_a_template_in_phase_1"
NEW_CHECK = "custom_objective_fields_follow_kind"

_HINT = (
    "Create the next version and certify it. Every Model Spec citing "
    "custom_objective:<slug>@<version> resolves to this row, so editing "
    "the loss here redefines what those models were fitted under and "
    "nothing on the model would change to show it."
)


def _trigger(*, expression: bool) -> str:
    """The definition trigger function: the template-era body, or the one with the arm."""
    extra = (
        "\n     OR NEW.bound_symbols IS DISTINCT FROM OLD.bound_symbols"
        "\n     OR NEW.parameters IS DISTINCT FROM OLD.parameters"
        "\n     OR NEW.loss IS DISTINCT FROM OLD.loss"
        if expression
        else ""
    )
    derived = (
        """
  IF NEW.derived IS DISTINCT FROM OLD.derived
     AND (OLD.derived IS NOT NULL OR OLD.status <> 'draft') THEN
    RAISE EXCEPTION
      'a Custom Objective''s derived block is written once, from NULL, while the objective is a draft (02 FR-163): % rejected', TG_OP
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'Create the next version; derive it again there.';
  END IF;"""
        if expression
        else ""
    )
    return f"""
CREATE OR REPLACE FUNCTION custom_objectives_definition_immutable() RETURNS trigger AS $fn$
BEGIN
  IF NEW.slug IS DISTINCT FROM OLD.slug
     OR NEW.version IS DISTINCT FROM OLD.version
     OR NEW.kind IS DISTINCT FROM OLD.kind
     OR NEW.template IS DISTINCT FROM OLD.template
     OR NEW.params IS DISTINCT FROM OLD.params
     OR NEW.applicability IS DISTINCT FROM OLD.applicability
     OR NEW.hessian_strategy IS DISTINCT FROM OLD.hessian_strategy
     OR NEW.hessian_min IS DISTINCT FROM OLD.hessian_min{extra} THEN
    RAISE EXCEPTION
      'a Custom Objective''s definition is immutable (02 FR-163): % rejected', TG_OP
      USING ERRCODE = 'insufficient_privilege',
            HINT = '{_HINT}';
  END IF;{derived}
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    for column in (
        sa.Column("bound_symbols", postgresql.JSONB()),
        sa.Column("parameters", postgresql.JSONB()),
        sa.Column("loss", sa.Text()),
        sa.Column("derived", postgresql.JSONB()),
    ):
        op.add_column("custom_objectives", column)
    op.drop_constraint(OLD_CHECK, "custom_objectives", type_="check")
    op.create_check_constraint(
        NEW_CHECK,
        "custom_objectives",
        "(kind = 'template' AND template IS NOT NULL AND bound_symbols IS NULL "
        "AND parameters IS NULL AND loss IS NULL AND derived IS NULL) "
        "OR (kind = 'expression' AND template IS NULL AND bound_symbols IS NOT NULL "
        "AND parameters IS NOT NULL AND loss IS NOT NULL)",
    )
    op.execute(_trigger(expression=True))


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (SELECT 1 FROM custom_objectives WHERE kind = 'expression') THEN
            RAISE EXCEPTION 'cannot downgrade: expression Custom Objectives exist (02 FR-164)'
              USING HINT = 'A Custom Objective cannot be deleted; deprecate it and keep the revision.';
          END IF;
        END $$;
        """
    )
    op.execute(_trigger(expression=False))
    op.drop_constraint(NEW_CHECK, "custom_objectives", type_="check")
    op.create_check_constraint(
        OLD_CHECK, "custom_objectives", "kind = 'template' AND template IS NOT NULL"
    )
    for name in ("derived", "loss", "parameters", "bound_symbols"):
        op.drop_column("custom_objectives", name)
