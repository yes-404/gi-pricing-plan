---
id: FD-8123
family: finding
title: The mint step does not refuse a working id already minted on main, and the idsweep compares numbers, so one working id behind two minted numbers is invisible
status: active
created: 2026-10-18   # filed 2026-10-18 under working id 8123
owner: auditor
tree: 3421b26b4cb7b622f9af55ca3e32ba8383e8ea4d
corrected_by: []
relates: [WK-1178, PL-1766, PL-1794, RL-1755, RL-1793, RL-8122, RL-8124]
---

# FD-8123 — The mint step does not refuse a working id already minted on main

## Finding

**MEDIUM, process; owner WK-1178.** Source: the maintainer's (by delegation) entry "2026-10-18 22:50:32
BST" (`to-lead.md`), item 3. A working id was minted twice, so two records of one body carry two minted
numbers on main. The mint step does not check that a working id is not already minted, and
`~/gi-pricing-plan.local/scratch/idsweep.sh` compares minted NUMBERS across refs, so it cannot see one
working id behind two numbers. No price is affected; the harm is a duplicate governed record (one
active, one a draft) that a reader can cite as live.

## Evidence

Read at `origin/main` 84b0ff5765e55bc8edd139cd22bb57cd474de807:

- Working id 8077: `PL-1766` (#1325, `status: active`) and `PL-1794` (#1338, `status: draft`, header
  "filed 2026-10-17 under working id 8077; minted 2026-10-18 as PL-1794").
- Working id 8076: `RL-1755` (#1319, active) and `RL-1793` (#1338, active, "filed 2026-10-16 under
  working id 8076; minted 2026-10-18 as RL-1793").
- The bodies differ only by id re-points and the Minted provenance line (38 and 14 diff lines; see
  `RL-8122`).
- The lead's D21 ACK (09:55:06) did not catch it, for the reason above.
- **A second constraint surfaced while correcting it:** `corrects:` is a scalar
  (`scripts/_docid.py` `_opt_str_field`) and audit-docs check 34 requires each `corrected_by:` target to
  `corrects:` back to the frozen file's own id, so one RL cannot correct two records; the pair needed
  `RL-8122` and `RL-8124`. This is a tooling limit the correction route has, recorded here so a
  future multi-target correction does not rediscover it.

## Remedy (ruled)

1. Before minting, `git grep -n "under working id <N>" origin/main -- docs` must print nothing for each
   working id being minted.
2. The idsweep gains that predicate: a working id that already appears in a minted record's "under working
   id" header on main is a COLLISION, whichever number it was minted to.

## Disposition

Deferred with an owner: WK-1178. The event that next discharges it: a merged change to the mint
procedure and `idsweep.sh` with a red-first proof (the sweep run on a ref that mints a working id
already minted on main must report a collision), or a dated ruling accepting the absence. Filed under
working id 8123.
