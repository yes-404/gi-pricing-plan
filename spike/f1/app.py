"""Spike F1 worker: one uvicorn worker process holding env `dev`'s live CompiledBundle.

The prototype of a WK-674 push-at-deploy switch (RL-876, RL-882 clause 4). It is scratch only
and never merged.

- Startup: read `env:dev:current` from the spike Redis, then fetch and hydrate that Bundle.
- Deploy channel `deploy:dev`, in two phases:
  * PREPARE {hash}: fetch the Bundle, run load_bundle off the event loop (the warm-up), hold
    it as pending, and ACK on `ack:<id>:prepare`.
  * COMMIT {hash}: swap the one `live` reference to the pending bundle (one attribute
    assignment on the event loop, so it is atomic for every request) and ACK on
    `ack:<id>:commit`.
- /score reads `live` once, at request start, and scores with the real engine. It returns the
  hash the engine stamped, the hash of the held object, and the result signature.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

import redis.asyncio as aioredis
from fastapi import FastAPI

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixtures  # noqa: E402  (loads scripts/bench-rating.py, and with it pricing_core)

from pricing_core.rating.compile import Bundle  # noqa: E402
from pricing_core.rating.runtime import load_bundle  # noqa: E402
from pricing_core.rating.score import score_one  # noqa: E402

PORT = int(os.environ.get("SPIKE_REDIS_PORT", "6390"))
ENV = "dev"


class State:
    live = None
    pending: dict = {}


S = State()


async def _hydrate(r: aioredis.Redis, content_hash: str):
    raw = await r.get(f"bundle:{content_hash}")
    bundle = await asyncio.to_thread(Bundle.model_validate_json, raw)
    return await asyncio.to_thread(load_bundle, bundle)


async def _listen(r: aioredis.Redis, ps) -> None:
    async for msg in ps.listen():
        if msg["type"] != "message":
            continue
        m = json.loads(msg["data"])
        if m["op"] == "prepare":
            t0 = time.time()
            S.pending[m["hash"]] = await _hydrate(r, m["hash"])
            await r.rpush(f"ack:{m['id']}:prepare", json.dumps(
                {"pid": os.getpid(), "warm_s": time.time() - t0, "t": time.time()}))
        elif m["op"] == "commit":
            S.live = S.pending.pop(m["hash"])  # the switch: one reference assignment
            await r.rpush(f"ack:{m['id']}:commit", json.dumps({"pid": os.getpid(), "t": time.time()}))


@asynccontextmanager
async def lifespan(app: FastAPI):
    import sigguard

    sigguard.install("worker")  # after uvicorn installed its handlers
    r = aioredis.Redis(port=PORT)
    current = (await r.get(f"env:{ENV}:current")).decode()
    S.live = await _hydrate(r, current)
    app.state.ctx = fixtures.ctx()
    ps = r.pubsub()
    await ps.subscribe(f"deploy:{ENV}")
    task = asyncio.create_task(_listen(r, ps))
    await r.rpush("ready", str(os.getpid()))
    yield
    task.cancel()
    await r.aclose()


app = FastAPI(lifespan=lifespan)


@app.post("/score")
async def score() -> dict:
    ts = time.time()
    held = S.live  # read once; the whole request uses this object
    res = await score_one(held, app.state.ctx)
    return {"h": res.bundle_hash, "held": held.content_hash, "sig": fixtures.signature(res),
            "pid": os.getpid(), "ts": ts, "te": time.time()}
