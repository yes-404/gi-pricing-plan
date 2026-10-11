"""Limb 2 of PL-1364 Task 5, copied into <tree>/backend/tests/ for the run and removed after.
Env: LIMB2_OUT (jsonl path), LIMB2_TREE (label), LIMB2_SHAPES (dir with shapes.py)."""
import json, os, sys, time
from typing import Any

import pytest
from backend.tests.test_score import admin_headers, client, scoring_headers, served, SCORE_URL, SCORED_REF, _quote  # noqa: F401
from backend.tests.test_score_compare import (  # noqa: F401
    reader_headers, two_versions, COMPARE_URL, _body,
)

from app.api import score as score_module
from model_schema import ScoringResult

sys.path.insert(0, os.environ["LIMB2_SHAPES"])
import shapes  # noqa: E402


def _stats(xs):
    xs = sorted(xs)
    return {"p50_ms": xs[len(xs) // 2], "p99_ms": xs[989], "max_ms": xs[-1]}


def _loop(call):
    for _ in range(100):
        assert call().status_code == 200
    xs = []
    for _ in range(1000):
        t = time.perf_counter(); r = call(); xs.append((time.perf_counter() - t) * 1000)
        assert r.status_code == 200
    return _stats(xs)


def _emit(route, stats):
    with open(os.environ["LIMB2_OUT"], "a") as f:
        f.write(json.dumps({"limb": 2, "tree": os.environ["LIMB2_TREE"], "route": route, **stats}) + "\n")


def test_limb2_score(client, scoring_headers, served, monkeypatch):  # noqa: F811
    u = ScoringResult.model_validate(shapes.shape_u_dict())

    async def _score_one(*a: Any, **k: Any):
        return u

    monkeypatch.setattr(score_module, "score_one", _score_one)
    body = _quote({"rating_version_ref": SCORED_REF})
    _emit("/score", _loop(lambda: client.post(SCORE_URL, json=body, headers=scoring_headers)))


def test_limb2_compare(client, reader_headers, two_versions, monkeypatch):  # noqa: F811
    t = ScoringResult.model_validate(shapes.shape_t_dict())

    async def _score_one(*a: Any, **k: Any):
        return t

    monkeypatch.setattr(score_module, "score_one", _score_one)
    body = _body()
    _emit("/score/compare", _loop(lambda: client.post(COMPARE_URL, json=body, headers=reader_headers)))
