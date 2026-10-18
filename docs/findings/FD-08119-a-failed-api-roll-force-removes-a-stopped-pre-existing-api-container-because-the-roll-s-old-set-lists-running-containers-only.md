---
id: FD-8119
family: finding
title: A failed api roll force-removes a stopped pre-existing api container, because the roll's old set lists running containers only
status: active
created: 2026-10-18   # filed 2026-10-18 under working id 8119
owner: auditor
tree: a67748dbaebd514dab76ae96c01b32b487c29855
corrected_by: []
relates: [WK-674, FD-1804, NFR-531]
---

# FD-8119 — A failed api roll force-removes a stopped pre-existing api container

## Finding

**LOW; owner WK-674; verdict deferred with an owner.** Source: the maintainer's entry
"2026-10-18 14:33:47 BST" (`to-lead.md`), item 1 (A4 of SL 8111's audit). API containers are
stateless, so the impact is a stopped replica lost, not data; no price is affected.

The EXIT trap that FD-1804's fix adds to `deploy/roll-api.sh` (SL 1813, PR #1342) derives the
containers to remove as "every api container now present minus `old`". `old` comes from `api_ids`,
which lists **running** containers only; the removal list comes from `docker ps -aq`, which includes
stopped ones. So on a failed roll a **stopped** api container that existed before the roll is not in
`old`, is counted as new, and is `docker rm -f`'d.

## Evidence

**The defect is in #1342's code, which is not on main at the filing tree.** `origin/main` `c1a9c430`
`deploy/roll-api.sh` has no `cleanup_new` (`git grep -c cleanup_new origin/main -- deploy/roll-api.sh`
prints 0). Read at `3264778b` (tree `a67748db`; `deploy/roll-api.sh` is byte-identical at PR #1342's
head `99cc5243`):

- `:30-32` `api_ids()`, with `:31` `docker ps -q` (no `-a`: running only);
- `:36` `mapfile -t old < <(api_ids)`: `old` is the running set;
- `:41-56` `cleanup_new` and its `trap cleanup_new EXIT` at `:56`: `:45-46` `comm -13 <old> <(docker ps -aq …)`
  (`-a`: running and stopped), `:49` `docker rm -f "$c"`.

## Fix direction (ruled; the slice decides the detail)

Build `old` from the same `-a` listing the cleanup uses, or exclude by creation time after the roll's
start. **Red test first:** a stopped pre-roll api container survives a failed roll. Not widened into
SL 1813: a deploy-logic change would cost another SOLO compose gate.

## Disposition

Deferred with an owner: WK-674. Its fix needs #1342 on main, since it edits code that #1342 adds. The
event that next discharges it: a merged change with the red-first test, or a dated ruling accepting
the absence. Filed under working id 8119.
