---
id: FD-8129
family: finding
title: An alive process that missed COMMIT serves the previous version until restart, because no reconcile exists, and an Environment created after a process starts is never subscribed
status: active
created: 2026-10-19   # filed 2026-10-19 under working id 8129
owner: auditor
tree: a6a31ab69f8e5569ed7687c30e3df69e3c57d87f
corrected_by: []
relates: [WK-674, SL-1259, PL-1237, PL-1710, PL-1766, RL-876]
---

# FD-8129 — An alive process that missed COMMIT serves the previous version until restart

## Finding

**MEDIUM; owner WK-674; due before the 12 Nov exit demo** (the maintainer's entry "2026-10-18 23:03:15
BST", `to-lead.md`: "Severity **MEDIUM, due before the 12 Nov exit demo** (not deferred past P2), owner
WK-674, with the reconcile mechanism as its remedy"). Under the design SL-1259 (S5) is ruled to build,
an alive process that missed the COMMIT round keeps the previous `live` until it restarts. No mechanism
makes it converge, so what it serves is a version the newest Deployment no longer names.

Two limbs, one remedy:

1. **Missed COMMIT.** The maintainer's entry "2026-10-18 23:03:15 BST": "Under (A), a process that is
   alive but missed the COMMIT stays on the previous `live` until restart. That is a regression in
   convergence relative to main, so **FD 8129 is widened and raised**: 'an unacknowledged-but-alive
   process serves the previous version until restart'."
2. **Environment created after a process starts.** The lead's relay of exec-1259's report "23:39:02"
   (`handover/eta.md` :2117, entry 2026-10-18 23:39:33 BST): "an Environment created after a process
   starts is not subscribed (no live ref, no roster entry) until restart". The report itself was not
   found as a `to-lead.md` entry; this limb rests on the relay and on the ruled design (see Evidence).

**The visible signal until a reconcile exists is `possibly_stale`.** The maintainer's entry "2026-10-18
23:07:57 BST", condition 5: "FD 8129's text (D25) cites this: possibly_stale is the visible signal until
reconcile exists." It is a per-process status in the `deployment.switched` audit event's after-state: when
`acks < receivers`, "every unacked roster name is reported as **`possibly_stale`** (a ghost or a
live-but-missed process cannot be told apart without a heartbeat, which was ruled out), never silently
dropped". The event is the only signal; it is written once, at the switch.

## Evidence

Read at `origin/main` 1fca3fc85710bdb19aab00efe7b9bf361d571a23 (tree
a6a31ab69f8e5569ed7687c30e3df69e3c57d87f).

**What the code has today.** The mechanisms the finding is about are not on main yet; SL-1259 builds
them. So the finding is about the ruled design, and main is the baseline it regresses from:

- Convergence today is per request. `backend/src/app/api/score.py:205` `_serving_ref` resolves, for a
  caller with an Environment (`:222`), the LATEST `DeploymentRow` of that Environment
  (`.order_by(DeploymentRow.deployed_at.desc(), DeploymentRow.id.desc()).limit(1)`) on every call; it is
  called at `:422`. A process that was never told of a deploy still serves the new version. This confirms
  the maintainer's 23:03:15 reading ("`/score`'s `_serving_ref` (api/score.py:221–236) reads the LATEST
  committed DeploymentRow on EVERY default-live request").
- No per-process `live` ref exists. `backend/src/app/main.py:84` `lifespan` loads no Deployment;
  `main.py:213` builds `BundleSlot`, whose module docstring (`backend/src/app/platform/bundle_slot.py`
  :60) says it "deliberately does not have: refresh, poll, pub/sub, or an environment pointer". All four
  belong to WK-674 (`bundle_slot.py` :61; `RL-876`).
- No heartbeat exists. `git grep -n -i heartbeat origin/main -- backend/src packages` prints one line,
  `backend/src/app/api/jobs.py:303`, an SSE keep-alive comment, not a process liveness signal. (The
  maintainer's 22:59:56 entry said the same.)
- `deployment.switched`, `possibly_stale`, a Redis roster and an environment-keyed subscription are
  absent from `backend/` and `packages/` at this tree. `git grep -n 'deployment.switched' origin/main
  -- docs backend` finds none in code; its one hit in `docs/` is an unrelated sentence in `RL-876`.
  Redis is used in `main.py:107-119` only for the rate limiter. They are specified by the rulings
  quoted above and are not yet built.

**Why each limb follows from the ruled design** (not from main):

- Missed COMMIT: the design is DB-first (the deploy transaction commits, then the COMMIT round swaps
  `live`), a process reads `live` from its own ref, and the only reader of the DB after startup is the
  startup load. A process that misses the one COMMIT message is never told again.
- Late Environment: the lifespan subscriber subscribes to the channels of the Environments that exist at
  startup (23:24:34 entry: "A process that serves several environments subscribes to each of its
  environment channels and appears in each roster"). A later Environment has no channel
  subscription, no `live` ref and no roster SET entry in that process; it appears in no
  `deployment.switched` list for it either, so even `possibly_stale` cannot name it. This limb is the
  weaker one: it rests on exec-1259's report as relayed, and no source entry was read.

**Cost of the regression.** Main's per-request read costs a database query per default-live request; the
per-process ref removes it for NFR-489. The ruling (23:03:15) accepts that trade and records the lost
convergence as this finding.

## Remedy (recommended)

A reconcile: a process periodically, and at each (re)subscribe, loads the latest committed Deployment of
every Environment it serves, and discovers Environments it has not yet subscribed to. It needs what the
maintainer ruled out of S5: a heartbeat or periodic reconcile (new mechanism, nothing on main). Its
red-first tests: a process that misses a COMMIT converges to the DB-latest Deployment without a restart;
an Environment created after start is subscribed without a restart. Until it lands, `possibly_stale` in
`deployment.switched` is the only signal, and the deploy response names the same processes so an operator
can restart them.

## Disposition

Deferred with an owner: WK-674. The event that next discharges it: a merged reconcile with the two
red-first tests above, or a dated ruling accepting the absence. Due before the 12 Nov exit demo. Filed
under working id 8129.
