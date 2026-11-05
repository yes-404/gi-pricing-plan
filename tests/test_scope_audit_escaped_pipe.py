"""`scope-audit.py` reads a §5.1 path cell holding an escaped pipe whole (FD-1484).

Three rows (`01` lineage, `06` dossiers and dependencies) carry `?direction=up\\|down` in
their path cell. The old `([^|]+)` capture stopped at the backslash, lost the closing
backtick, and so the three published routes were declared in neither direction: no
requirement audit, no demo-guide check. No `@pytest.mark.req`: this is the audit tool's
own correctness, as in `tests/test_scope_audit.py`.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("_scope_audit", ROOT / "scripts" / "scope-audit.py")
assert _spec is not None
assert _spec.loader is not None
_scope_audit = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _scope_audit
_spec.loader.exec_module(_scope_audit)


def test_a_path_cell_with_an_escaped_pipe_is_declared_whole() -> None:
    data = _scope_audit.declared_endpoints("DATA")
    gov = _scope_audit.declared_endpoints("GOV")
    assert ("GET", "/api/v1/dataset-versions/{}/lineage") in data
    assert ("GET", "/api/v1/dossiers/{}") in gov
    assert ("GET", "/api/v1/artifacts/{}/dependencies") in gov
