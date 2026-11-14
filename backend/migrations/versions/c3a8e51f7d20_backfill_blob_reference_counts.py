"""backfill blob reference counts: every owner that predates `put`'s reference holds one

WK-1251 slice 2 (FR-420's precondition, part 2; #1800's backfill limb). Before slice 1 a
`BlobStore.put` left `ref_count` at 0 and most owners never took a reference, so a blob an
artifact references can sit at 0 and be taken by the collector once its grace period passes.
This sets, for every blob, `ref_count = greatest(ref_count, <owners that reference it>)`,
counting each owner place listed in `app.platform.blobs.BLOB_OWNERS` at this revision (the SQL
is frozen here, not imported: a migration describes the schema as it was).

Blobs with NO visible owner are then pinned at `ref_count = 1` (the maintainer's ruling,
#1504 slice 2, option A). Two owner classes name their blobs only from inside another blob in S3,
so no query can count them: the rate-table cell-diff chunks (named by the manifest blob) and a
score batch's output parquet (named by the Job's summary blob). A legacy blob at 0 that one of
them holds is indistinguishable from true garbage, so every such blob is pinned, and the
migration prints how many and how many bytes (`pinned N legacy ownerless blobs, B bytes`). The
cost is that legacy true orphans are never collected until a later backfill releases them.

It never lowers a count and writes no other column. The blob row's content columns are
immutable (`blobs_content_immutable`); `ref_count` is the one column that moves.

Reversibility (FR-416): irreversible: a no-op. There is no schema change to reverse, and
`downgrade()` does nothing by design: a pin is indistinguishable from a reference a later `put` took on the same blob, so
unpinning could release a blob a slice 1 writer now holds, while a count left too high only makes
the collector more conservative (a leak never loses data). It touches no row. The pinned set is
printed by the upgrade, so an operator can find it again.

Revision ID: c3a8e51f7d20
Revises: b7e4c2a91d36
Create Date: 2026-11-14 12:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3a8e51f7d20"
down_revision: str | None = "b7e4c2a91d36"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: One `SELECT` per owner place, one row per reference, in a column named `sha256`.
_OWNERS: tuple[str, ...] = (
    "SELECT t->'blob'->>'sha256' AS sha256 FROM dataset_versions, jsonb_array_elements(tables) AS t",
    "SELECT result->>'ref' AS sha256 FROM jobs WHERE result->>'kind' = 'blob'",
    "SELECT sha256 FROM blob_uploads",
    "SELECT fit_result->'booster_blob'->>'sha256' AS sha256 FROM models",
    "SELECT fit_result->'covariance_blob'->>'sha256' AS sha256 FROM models",
    "SELECT cells->>'sha256' AS sha256 FROM rate_table_versions",
    "SELECT bundle->>'blob_sha256' AS sha256 FROM rating_versions",
    "SELECT evidence->>'structural_diff_blob' AS sha256 FROM rating_versions",
    "SELECT cases_blob_sha256 AS sha256 FROM regression_runs",
    "SELECT movers_blob_sha256 AS sha256 FROM dislocation_runs",
    "SELECT blob_sha256 AS sha256 FROM scoring_traces",
)


def upgrade() -> None:
    owned = (
        "SELECT sha256, count(*) AS n FROM ("
        + " UNION ALL ".join(f"({owner})" for owner in _OWNERS)
        + ") AS o WHERE sha256 IS NOT NULL GROUP BY sha256"
    )
    op.execute(
        f"UPDATE blobs SET ref_count = owned.n FROM ({owned}) AS owned "
        "WHERE blobs.sha256 = owned.sha256 AND blobs.ref_count < owned.n"
    )
    # Whatever is still at 0 has no visible owner: pin it, and say what was pinned.
    bind = op.get_bind()
    count, total = bind.execute(
        sa.text("SELECT count(*), coalesce(sum(bytes), 0) FROM blobs WHERE ref_count = 0")
    ).one()
    op.execute("UPDATE blobs SET ref_count = 1 WHERE ref_count = 0")
    print(f"blob backfill: pinned {int(count)} legacy ownerless blobs, {int(total)} bytes")


def downgrade() -> None:
    """Irreversible: a no-op (see the module docstring). It never lowers a count."""
