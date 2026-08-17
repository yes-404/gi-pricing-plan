"""modelling: the model lifecycle, and the status column that never enumerated it

Two changes, one slice (`02` FR-MODEL-64, §4.8).

* **`model_status_is_in_the_lifecycle`.** `models.status` is a `String(16)` with a default
  of `'draft'` and, until now, no constraint on its contents. The type enumerated the six
  states and the service checked the transitions, but neither layer is reachable from
  `psql` — so `'aproved'`, `'live'`, or any other sixteen characters were a legal status,
  and a model carrying one is invisible to every lifecycle query rather than rejected by
  it. The other two constraints on this table hid part of the gap: a bogus status that is
  not `draft` or `archived` was already refused *if* it had no `fit_result`. A fitted model
  moved to a bogus status was not.

* **`models.approval_request_id`.** `02` §4.8 has declared it since Phase 0 and OQ-MODEL-8
  listed it among the fields declared and dead. It goes live here because the slice that
  creates the request is this one — "re-widen it as the slices land", which is that
  question's own recommendation rather than a decision taken ahead of the maintainer.

  Deliberately **not** a foreign key to `approval_requests`. Governance is the module a
  model depends on, not the reverse (DEP-1), and a FK would make dropping the governance
  tables a modelling migration. The reference is by id, checked where it is written.

**No backfill is needed and none is invented.** Every existing row carries a status this
constraint accepts — `draft`, `fitted` and `review` are the three present — and a row that
did not would fail the `ALTER` loudly, which is the constraint doing its job on arrival
rather than a silent repair of a value nobody can reconstruct.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-17 10:20:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: The six states of FR-MODEL-64, in lifecycle order. Kept as a list here rather than
#: imported from `model_schema.ModelStatus`: a migration is a historical record of the
#: schema at a point in time, and one that imported a live enum would silently rewrite its
#: own history the next time a state was added.
LIFECYCLE = ("draft", "fitted", "review", "approved", "superseded", "archived")


def upgrade() -> None:
    op.add_column(
        "models",
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_check_constraint(
        "model_status_is_in_the_lifecycle",
        "models",
        sa.text("status IN ('draft', 'fitted', 'review', 'approved', 'superseded', 'archived')"),
    )
    op.create_index(
        "ix_models_family_status",
        "models",
        ["workspace_id", "model_family_slug", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_models_family_status", table_name="models")
    op.drop_constraint("model_status_is_in_the_lifecycle", "models", type_="check")
    op.drop_column("models", "approval_request_id")
