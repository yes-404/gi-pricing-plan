---
id: FD-1804
family: finding
title: A failed api roll leaves never-healthy replicas in DNS rotation, so the failed roll degrades a working service
status: active
created: 2026-10-18   # filed 2026-10-18 under working id 8112; minted 2026-10-18 as FD-1804
owner: auditor
tree: 0a13415851a0a75d0ab8734fe8a02b2b6739e78a
corrected_by: []
relates: [WK-674, NFR-531]
---

# FD-1804 — A failed api roll leaves never-healthy replicas in DNS rotation, so the failed roll degrades a working service

## Finding

**MEDIUM; owner WK-674; verdict deferred with an owner.** Source: the maintainer's entry
"2026-10-18 03:11:40 BST" (`to-lead.md`, item 3 of the SL-1258 audit verdict). An operational
degradation on the deploy path, in the intent of NFR-531; nothing mispriced.

`deploy/roll-api.sh` scales `api` out beside the old replicas, waits for the new ones to be
healthy, then stops the old ones. When it exits 1 after the scale-out, it leaves **all** replicas
in the compose project: the old ones, still serving, **and** the new ones that never became
healthy. The load balancer resolves the `api` name through Docker's embedded DNS, which returns
every running replica's address and does not filter on health. The unhealthy new replicas
therefore stay in rotation, and a roll that failed makes a working service worse than it was
before the roll started.

A request refused before sending is retried by the balancer. Any response from an
unhealthy-but-listening replica is not retried for a POST.

## Evidence

Read on `origin/sl-1258-wk674-s4` 9974cbfc43c2b88d5beb50e6301307e10bf31b52 (the code is not on
`origin/main`: SL-1258 has not merged), by the author:

- `deploy/roll-api.sh:38` scales out with `--scale api=$((REPLICAS * 2))`; `:40` collects the
  NEW ids as the set difference against the pre-roll ids.
- Exits that leave the NEW ids running: `:41` (wrong new count, `exit 1`), `:47` (a new replica
  not healthy within the timeout, `exit 1`). Both run **before** the first old stop at `:54`, so
  the old replicas are still serving beside the never-healthy new ones.
  `:61` and `:64` (wrong final count, wrong image) run after the old ones are gone.
- No `trap` anywhere in the script: nothing removes the NEW ids on any failure path.
- `deploy/lb.conf:4` `resolver 127.0.0.11 valid=1s ipv6=off;` and `:8` `set $upstream
  http://api:8000;`: round-robin over the addresses Docker's DNS returns for `api`; the DNS
  answer is not health-filtered (the maintainer's reading in the entry above; not re-measured
  here).

## Fix (ruled in the entry; the slice decides the detail)

An `EXIT` trap in `roll-api.sh`, armed before the scale-out and cleared before the first old stop,
that on a non-zero status stops and removes the NEW container ids and exits with the original
status, returning the project to the pre-roll replicas. Plus a red-first failure-path test: an
image whose healthcheck never passes, asserting a non-zero exit, exactly the old ids remaining and
healthy, no new id in `docker ps -a`, and requests through the balancer succeeding. Red without
the trap, by cause.

## Disposition

Deferred with an owner: WK-674, in the scope of SL 8111 / PL 8113 (planned; unminted, so not in front matter), due before the
code freeze, Wed 4 Nov 2026. The event that next discharges it: SL 8111 merging with the trap and
its red-first test, or a dated ruling accepting the absence. SL-1258 is not changed for it and
merges as gated. Filed under working id 8112.
