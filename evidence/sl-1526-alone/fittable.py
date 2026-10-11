"""SL-1526 ALONE stage b: one column of the 11(b) fit table (PL-1525 Acceptance 11 (b)).

Usage: fittable.py <label> <seed record json> <worktree whose venv runs this>   (env: GIP_DATABASE_URL)
Prints the approved GLM's deviance and AIC (stored `GlmDiagnostics`), and its factor list with each
factor's `FactorType`, as `FITCOL` lines for the run script to lay side by side.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.config import load_settings
from app.db.models import DiagnosticsRow, FactorRow, ModelRow
from app.db.session import Database


async def main() -> int:
    label, record = sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    ws = UUID(record["workspace_id"])
    database = Database(load_settings())
    async with database.session() as s:
        models = [m for m in (await s.execute(
            select(ModelRow).where(ModelRow.workspace_id == ws, ModelRow.status == "approved")
        )).scalars() if (m.fit_result or {}).get("model_type") == "glm"]
        if not models:
            print(f"FITCOL {label}: no approved GLM")
            return 5
        m = max(models, key=lambda x: x.version)
        diag = (await s.execute(select(DiagnosticsRow).where(DiagnosticsRow.model_id == m.id))).scalar_one()
        glm = diag.payload["glm"]
        print(f"FITCOL {label}: model {m.model_family_slug}@{m.version} rows={m.fit_result.get('rows')}")
        print(f"FITCOL {label}: deviance={glm['deviance']} aic={glm.get('aic')}")
        ids = [UUID(str(f)) for f in m.spec.get("factors", [])]
        facs = (await s.execute(select(FactorRow).where(FactorRow.id.in_(ids)))).scalars().all()
        by_id = {f.id: f for f in facs}
        print(f"FITCOL {label}: factors={len(ids)}")
        for i in ids:
            f = by_id[i]
            print(f"FITCOL {label}:   {f.slug} type={f.body.get('type')}")
    await database.dispose()
    return 0


sys.exit(asyncio.run(main()))
