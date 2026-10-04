"""`scripts/bench-rating.py` calls `app.api.score._fetch_bundle` with the signature it has.

The script is not imported by anything the suite runs, so a signature change in the app
(the `slot` parameter RL-921 added) left `--http` failing at runtime with a `TypeError`
nobody saw. This binds every `_fetch_bundle(...)` call in the script to the real signature
without a database or object store.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

from app.api.score import _fetch_bundle

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "bench-rating.py"


def test_bench_rating_fetch_bundle_calls_bind_to_the_real_signature() -> None:
    calls = [
        node
        for node in ast.walk(ast.parse(SCRIPT.read_text()))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_fetch_bundle"
    ]
    assert calls, "the script no longer calls _fetch_bundle; this guard is stale"
    signature = inspect.signature(_fetch_bundle)
    for call in calls:
        # Bind placeholders of the same arity and keyword names; a missing or unknown
        # parameter raises TypeError, exactly as the runtime call would.
        signature.bind(
            *[object() for _ in call.args],
            **{kw.arg: object() for kw in call.keywords if kw.arg},
        )
