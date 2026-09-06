"""scoring traces: pending state for off-path re-score (WK-671 Task 4B)

`03` FR-259, NFR-489. RL-862
(`docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`) moves trace
*production* off the serving request: the quoting path scores untraced, and a sampled
outcome is recorded as a **pending** row at serve time, then completed by an off-path
re-score Job that fills in the blob body. This adds the columns that phase needs.

**`blob_sha256` becomes nullable** — a pending row has no body yet. The existing
`ck_scoring_traces_blob_sha256_format` check already tolerates `NULL` (`~` against `NULL`
is `NULL`, which `CHECK` treats as satisfied), so it needs no change.

**`status` distinguishes the three states a row can be in**: `pending` (written at serve
time, no body), `complete` (the off-path re-score reproduced the served quote and the body
is written), `mismatch` (RL-862 §8.2's two safety conditions, either of which lands
here: (b) the re-score ran and did not reproduce the served result — the body is kept, as
evidence of what actually happened; or (a) the pinned bundle no longer resolves at all, so
no re-score was attempted and there is no body to keep). **So `blob_sha256` is required
only when `status = 'complete'`, and forbidden only when `status = 'pending'`** — a
`mismatch` row may carry a body (condition (b)) or not (condition (a)).

**`pending_quote_context` and `served_summary` carry what the off-path Job needs and what
the reproduction check compares against** (RL-862 §8.4's access-controlled carrier: the
Quote Context travels in this row, never in `JobRow.parameters`, which a workspace member
holding no scoring permission can read). `served_summary` is `outcome`/`decline_reasons`/
`premium_ladder`/`outputs` only — never raw quote inputs — so it carries no exposure
`pending_quote_context` does not already carry more of.

**Still no `UPDATE` grant.** `835988d1de4c`'s migration revokes `UPDATE` on this table
outright and that stands unchanged here: *"a trace, once written, is never edited, only
(eventually) deleted."* Completing a pending row is a `DELETE` of the pending row plus an
`INSERT` of the finished one at the same id, inside one transaction
(`app.platform.traces.complete_pending_trace`) — never an `UPDATE` statement, so the
existing `REVOKE` needs no loosening.

**Also registers the `score.trace_produce` `job_kind` enum value** — the off-path re-score
Job RL-862 introduces. `job_kind` is a Postgres `ENUM`, not a check constraint
(`df53696a2682`), and every prior addition to `model_schema.JobKind` needed its own `ALTER
TYPE ... ADD VALUE` (`2b2e2a481fb1`, `d5e6f7a8b9c0`, `b1c2d3e4f5a6`, `d0e1f2a3b4c5`) or
`job_service.submit` fails with `invalid input value for enum job_kind` the first time
anything tries to submit one — the same gap each of those found. Folded into this
migration rather than filed separately, since both changes are Task 4B's and neither is
usable without the other.

Revision ID: d3b955a63d6a
Revises: 835988d1de4c
Create Date: 2026-08-30 16:35:48.830154+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d3b955a63d6a"
down_revision: str | None = "835988d1de4c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("scoring_traces", "blob_sha256", nullable=True)
    op.add_column(
        "scoring_traces",
        sa.Column("status", sa.String(length=16), nullable=False, server_default="complete"),
    )
    op.add_column(
        "scoring_traces",
        sa.Column("pending_quote_context", postgresql.JSONB, nullable=True),
    )
    op.add_column(
        "scoring_traces",
        sa.Column("served_summary", postgresql.JSONB, nullable=True),
    )
    # The server default above backfills every existing row (all written by the
    # one-serialisation `write_trace` path, so all genuinely complete) to `complete`
    # without an app-level `UPDATE`, then is dropped so new inserts must state their own
    # status explicitly rather than silently defaulting to a value only correct for the
    # rows that already existed.
    op.alter_column("scoring_traces", "status", server_default=None)
    op.create_check_constraint(
        op.f("ck_scoring_traces_status_known"),
        "scoring_traces",
        "status IN ('pending', 'complete', 'mismatch')",
    )
    op.create_check_constraint(
        # `complete` always has a body; `pending` never does. `mismatch` is the one
        # status that may go either way (condition (b): reproduction ran and the body is
        # kept as evidence; condition (a): the pinned bundle was unresolvable and no
        # re-score was attempted, so there is nothing to keep).
        op.f("ck_scoring_traces_blob_required_unless_pending"),
        "scoring_traces",
        "(status <> 'pending' OR blob_sha256 IS NULL) "
        "AND (status <> 'complete' OR blob_sha256 IS NOT NULL)",
    )
    op.execute(
        "ALTER TYPE job_kind ADD VALUE IF NOT EXISTS 'score.trace_produce' AFTER 'score.batch'"
    )


def downgrade() -> None:
    # `job_kind` keeps `score.trace_produce`: PostgreSQL cannot drop an enum value without
    # rewriting every `jobs` row, the same reason `2b2e2a481fb1` and its siblings leave
    # their own added values in place on downgrade.
    op.drop_constraint(
        op.f("ck_scoring_traces_blob_required_unless_pending"),
        "scoring_traces",
        type_="check",
    )
    op.drop_constraint(
        op.f("ck_scoring_traces_status_known"), "scoring_traces", type_="check"
    )
    op.drop_column("scoring_traces", "served_summary")
    op.drop_column("scoring_traces", "pending_quote_context")
    op.drop_column("scoring_traces", "status")
    op.alter_column("scoring_traces", "blob_sha256", nullable=False)
