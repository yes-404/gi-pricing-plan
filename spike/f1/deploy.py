"""Spike F1 deploy command: a two-phase push of env `dev` to a target bundle hash.

usage: deploy.py <target_hash> <expected_workers> [timeout_s]
Prints one JSON line with the timestamps (time.time(), the same clock as the workers).
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
import uuid

import redis.asyncio as aioredis


async def main(target: str, expected: int, timeout: float) -> dict:
    r = aioredis.Redis(port=6390)
    did = uuid.uuid4().hex[:8]
    out: dict = {"id": did, "target": target, "t_cmd": time.time()}
    # The deploy writes the Bundle into the cache first (FR-268: pre-warmed into cache).
    await r.set(f"bundle:{target}", await r.get(f"bundle:{target}"))
    n = await r.publish("deploy:dev", json.dumps({"op": "prepare", "id": did, "hash": target}))
    out["subscribers"] = n
    if n != expected:
        out["abort"] = f"{n} subscribers, expected {expected}"
        return out
    acks = []
    deadline = time.time() + timeout
    while len(acks) < n:
        got = await r.blpop([f"ack:{did}:prepare"], timeout=max(0.1, deadline - time.time()))
        if got is None:
            out["abort"] = f"prepare: {len(acks)}/{n} acks by the timeout"
            return out
        acks.append(json.loads(got[1]))
    out["t_prepared"] = time.time()
    out["prepares"] = acks
    await r.set("env:dev:current", target)  # a worker started from now on boots on the target
    out["t_commit_pub"] = time.time()
    await r.publish("deploy:dev", json.dumps({"op": "commit", "id": did, "hash": target}))
    commits = []
    while len(commits) < n:
        got = await r.blpop([f"ack:{did}:commit"], timeout=max(0.1, deadline - time.time()))
        if got is None:
            out["abort"] = f"commit: {len(commits)}/{n} acks by the timeout"
            return out
        commits.append(json.loads(got[1]))
    out["t_all_committed"] = time.time()
    out["commits"] = commits
    out["switch_s"] = out["t_all_committed"] - out["t_cmd"]
    await r.aclose()
    return out


if __name__ == "__main__":
    print(json.dumps(asyncio.run(main(sys.argv[1], int(sys.argv[2]),
                                      float(sys.argv[3]) if len(sys.argv) > 3 else 30.0))))
