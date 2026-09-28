"""Spike F1 fixtures: two real ~200-step GBM bundles, A and B, built with scripts/bench-rating.py.

Writes each Bundle's JSON into the spike's own Redis (port 6390) and prints, for each hash,
the reference result signature. Both come from the real engine: compile_bundle, then
load_bundle, then score_one. The mix detector is that signature: a response claiming hash H
must carry H's signature exactly.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("bench_rating", ROOT / "scripts" / "bench-rating.py")
assert _spec and _spec.loader
bench = importlib.util.module_from_spec(_spec)
sys.modules["bench_rating"] = bench
_spec.loader.exec_module(bench)

# Bundle A and bundle B differ in graph length (chained-expression steps), so they differ in
# hash (compile.py hashes graph + pins, not payload bytes) and in premium.
VARIANTS = {"A": 187, "B": 186}


def ctx():  # the one quote every request scores
    return bench._ctx()


def signature(result) -> str:
    body = result.model_dump(mode="json", include={"outputs", "premium_ladder", "outcome"})
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]


async def build() -> dict[str, dict[str, str]]:
    import redis.asyncio as aioredis

    r = aioredis.Redis(port=6390)
    out: dict[str, dict[str, str]] = {}
    for name, n_expr in VARIANTS.items():
        bundle = await bench._serialisable(with_gbm=True, n_expr=n_expr, rounds=300, rows=5_000)
        raw = bundle.model_dump_json()
        await r.set(f"bundle:{bundle.content_hash}", raw)
        compiled = bench.load_bundle(bundle)
        res = await bench.score_one(compiled, ctx())
        assert res.bundle_hash == bundle.content_hash
        out[name] = {"hash": bundle.content_hash, "sig": signature(res), "bytes": str(len(raw)),
                     "last_rung": json.dumps(res.model_dump(mode="json")["premium_ladder"][-1:])[:200]}
    await r.aclose()
    return out


if __name__ == "__main__":
    refs = asyncio.run(build())
    Path(__file__).with_name("refs.json").write_text(json.dumps(refs, indent=1))
    print(json.dumps(refs, indent=1))
