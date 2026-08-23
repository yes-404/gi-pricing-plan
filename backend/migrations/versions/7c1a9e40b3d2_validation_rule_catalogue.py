"""data: a stored rule names its `01` §4.4 catalogue entry (FR-DATA-53)

`01` §4.4 catalogues 38 named validation rules and calls their ids stable. The platform
held none of them: `validation_rules` could only carry a workspace's own rules, so the
catalogue existed as prose and every workspace that wanted the shipped checks re-typed
them. `scripts/scope-audit.py DATA --catalogue VR` read 1 of 38.

Two columns, mirroring `roles.builtin` and seeded the same way (`rbac.seed_builtin_roles`):

* `builtin` — the row came from the shipped catalogue rather than this workspace.
* `catalogue_id` — *which* entry, by the stable id `01` §4.4 assigns. Not a foreign key
  and not the slug: §4.4 calls the id stable while a workspace may version a seeded rule
  and rename it, so the id is the part that survives.

**`approved_rule_dry_run_and_separate_approver` gains a third arm.** A shipped rule has no
in-workspace author for an approver to differ from, and no dry run to point at: it was
reviewed once, in the specification, and every workspace receives the same reviewed text.
Without the arm the only way to seed the catalogue `approved` — and an unapproved rule
cannot enter a rule set (§4.5) — was to invent a `dry_run_report_id` naming no report,
which `examples/fremtpl2/seed.py` did. Naming the exemption is a better governance outcome
than fabricating the evidence for it.

`builtin_rule_names_its_catalogue_entry` keeps the pair honest in the direction that
matters: no `builtin` row without an id, because a row claiming the approval exemption must
say which reviewed rule it is claiming it from. The converse is left open on purpose — a
workspace that configures a shipped rule against its own tables authors the next version of
it (§4.5 step 4), and that version is workspace data with its own approver and its own dry
run that still records where it came from.

`downgrade()` deletes the seeded rows before dropping the columns. They are not workspace
data — they are this migration's own output — and leaving them behind under the restored
constraint would strand approved rows with no approver and no dry run, which is the exact
state the old constraint exists to forbid.

Revision ID: 7c1a9e40b3d2
Revises: 9e4c7b21fa08
Create Date: 2026-08-23 00:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7c1a9e40b3d2"
down_revision: str | None = "9e4c7b21fa08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The short names. `backend/src/app/db/base.py`'s `NAMING_CONVENTION` reaches alembic's
# ops through `target_metadata`, so both `create_check_constraint` and `drop_constraint`
# expand these to the `ck_validation_rules_…` the database actually holds — passing the
# expanded form would have the convention applied to it twice.
_APPROVAL = "approved_rule_dry_run_and_separate_approver"
_NAMES_ITS_ENTRY = "builtin_rule_names_its_catalogue_entry"

_OLD_APPROVAL_CHECK = (
    "status <> 'approved' OR (approved_by IS NOT NULL "
    "AND approved_by <> authored_by AND dry_run_report_id IS NOT NULL)"
)
_NEW_APPROVAL_CHECK = (
    "builtin IS TRUE OR status <> 'approved' OR (approved_by IS NOT NULL "
    "AND approved_by <> authored_by AND dry_run_report_id IS NOT NULL)"
)


def upgrade() -> None:
    # `server_default` only to fill the rows already there; dropped immediately so the
    # column's default lives in one place — the model — rather than two that can disagree.
    op.add_column(
        "validation_rules",
        sa.Column("builtin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("validation_rules", "builtin", server_default=None)
    op.add_column(
        "validation_rules", sa.Column("catalogue_id", sa.String(length=16), nullable=True)
    )
    op.create_index(
        "ix_validation_rules_catalogue",
        "validation_rules",
        ["workspace_id", "catalogue_id"],
    )

    op.drop_constraint(_APPROVAL, "validation_rules", type_="check")
    op.create_check_constraint(_APPROVAL, "validation_rules", _NEW_APPROVAL_CHECK)
    op.create_check_constraint(
        _NAMES_ITS_ENTRY, "validation_rules", "builtin IS FALSE OR catalogue_id IS NOT NULL"
    )


def downgrade() -> None:
    # Before the columns go, or the restored constraint has approved rows it must refuse
    # and no column left to tell it which ones were seeded.
    op.execute(sa.text("DELETE FROM validation_rules WHERE builtin IS TRUE"))

    op.drop_constraint(_NAMES_ITS_ENTRY, "validation_rules", type_="check")
    op.drop_constraint(_APPROVAL, "validation_rules", type_="check")
    op.create_check_constraint(_APPROVAL, "validation_rules", _OLD_APPROVAL_CHECK)

    op.drop_index("ix_validation_rules_catalogue", table_name="validation_rules")
    op.drop_column("validation_rules", "catalogue_id")
    op.drop_column("validation_rules", "builtin")
