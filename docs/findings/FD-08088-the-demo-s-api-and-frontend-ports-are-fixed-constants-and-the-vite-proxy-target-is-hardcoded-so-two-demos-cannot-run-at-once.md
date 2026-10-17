---
id: FD-8088
family: finding
title: The demo's API and frontend ports are fixed constants and the Vite proxy target is hardcoded, so two demos cannot run at once
status: active
created: 2026-10-17
owner: auditor
tree: cf509df89dbebff329bb6b319bcc9bcd2a2c2352
corrected_by: []
relates: [WK-1178]
---

# FD-8088 — The demo's API and frontend ports are fixed constants and the Vite proxy target is hardcoded, so two demos cannot run at once

## Finding

**LOW, backlog; owner WK-1178; verdict proposed `deferred with an owner`** (the maintainer ruled option (b), env ports, a WK-1178 backlog item: `to-lead.md` about 14:22 BST, 2026-10-17, relayed by the lead's brief). `scripts/demo.py:51-52` sets `API_PORT: Final = 8000` and `FRONTEND_PORT: Final = 5173` with no environment override; `frontend/vite.config.ts:43` hardcodes the proxy `target: "http://localhost:8000"`. A second demo on the same box fails `require_free` (`scripts/demo.py:117`, used at `:378` and `:406`), or would proxy to the first demo's API. It blocked the concurrent demo in the 2-slot gate trial.

## Evidence

Read at `origin/main` `cf509df89dbebff329bb6b319bcc9bcd2a2c2352`: `scripts/demo.py:51-52` (constants), `:354` (`--port str(API_PORT)`), `:361` (`--port str(FRONTEND_PORT)`, `--strictPort`), `:378` and `:406` (`require_free`); `frontend/vite.config.ts:43`. The trial incident is the lead's report, not re-observed here.

## Disposition

Backlog, WK-1178: read the two ports from environment variables (defaults 8000 and 5173), pass the API port to the frontend dev server so the Vite proxy target follows it, and print the chosen URLs. Test: two demos started with different ports do not collide. The event that next discharges it: the merge of that change.
