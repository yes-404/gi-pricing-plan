"""SL-1526 ALONE stage c: the REAL-GLM report (to-lead.md "2026-10-11 11:39:18 BST" item 3).

Usage: realglm.py <slice worktree> <seed record json>      (env: GIP_DATABASE_URL, the demo's DB)

Prints, in full, the approved GLM's fitted veh_age relativities and the result of EVERY declared
property (and golden quote) of the demo Regression Suite replayed against the REAL compiled bundle
the seed stored: the handler's own path (`rating_handlers._rating_regression`'s prepare + run_regression),
so a failing property shows its counterexample even though the seed's Job refused it. Any failure
prints `STOP: <name>` and exits 4 (the 11:35:35 STOP rule: no edit, no retry).
"""
from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

W = Path(sys.argv[1])
sys.path.insert(0, str(W / "examples" / "fremtpl2"))
sys.path.insert(0, str(W))

from sqlalchemy import select  # noqa: E402

import model as demo_model  # noqa: E402
from app.config import load_settings  # noqa: E402
from app.db.models import ModelRow, RatingVersionRow  # noqa: E402
from app.db.session import Database  # noqa: E402
from app.platform import regression_suites as suites  # noqa: E402
from app.platform.blobs import BlobStore  # noqa: E402
from model_schema import ArtifactRef  # noqa: E402
from pricing_core.rating.testing import run_regression  # noqa: E402


def report(run: Any) -> list[str]:
    """Print every golden and property result in full; return the names that failed."""
    stops: list[str] = []
    for g in run.golden_results:
        print("GOLDEN  " + g.model_dump_json())
        if g.status == "fail":
            stops.append(f"golden {g.name}")
    for p in run.property_results:
        print(f"PROPERTY {p.name}: {p.status.upper()} cases_run={p.cases_run}")
        print("   " + p.model_dump_json())
        if p.status == "fail":
            stops.append(p.name)
    return stops


async def main() -> int:
    ws = UUID(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))["workspace_id"])
    database = Database(load_settings())
    async with database.session() as s:
        models = (await s.execute(
            select(ModelRow).where(ModelRow.workspace_id == ws, ModelRow.status == "approved")
        )).scalars().all()
        glm = sorted((m for m in models if (m.fit_result or {}).get("model_type") == "glm"),
                     key=lambda m: m.version, reverse=True)
        if not glm:
            print("STOP: no approved GLM in the workspace")
            return 4
        _, fit = await demo_model.load_approved_glm(database, ws, glm[0].id)
        print(f"== approved GLM {glm[0].id}: converged={fit.converged} rows={fit.rows} deviance={fit.deviance}")
        for factor, levels in fit.relativities.items():
            if "veh_age" in factor:
                print(f"== fitted relativities, factor {factor}:")
                for r in levels:
                    print(f"   {r.level!r:>14}  relativity={r.relativity}  base={r.is_base}")
        rv = (await s.execute(
            select(RatingVersionRow).where(RatingVersionRow.workspace_id == ws,
                                           RatingVersionRow.slug == demo_model.DEMO_RATING_SLUG)
            .order_by(RatingVersionRow.version.desc()).limit(1)
        )).scalar_one()
        ref = ArtifactRef(type="rating_version", slug=rv.slug, version=rv.version)
        algo_slug = ArtifactRef.model_validate(rv.algorithm_ref).slug
        found = await suites.current_suite_for_algorithm(s, workspace_id=ws, algorithm_slug=algo_slug)
        if found is None:
            print("STOP: no Regression Suite for the algorithm")
            return 4
        suite = suites.to_schema(*found)
    bundle = await demo_model._load_compiled(database, BlobStore(load_settings()), ws, rv.id)
    run, _log = run_regression(bundle, suite, rating_version_ref=ref, now=lambda: datetime.now(UTC))
    print(f"== replay of {run.suite_ref} on {ref} (bundle {getattr(bundle, 'content_hash', '?')}): overall={run.overall}")
    stops = report(run)
    await database.dispose()
    for name in stops:
        print(f"STOP: {name}")
    return 4 if stops else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
