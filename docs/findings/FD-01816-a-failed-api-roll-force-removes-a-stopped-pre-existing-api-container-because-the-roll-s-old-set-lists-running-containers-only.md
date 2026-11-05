---
id: FD-1816
family: finding
title: A failed api roll force-removes a stopped pre-existing api container, because the roll's old set lists running containers only
status: closed
created: 2026-10-18   # filed 2026-10-18 under working id 8119; minted 2026-10-18
owner: auditor
tree: a67748dbaebd514dab76ae96c01b32b487c29855
corrected_by: []
relates: [WK-674, FD-1804, SL-1813, PL-1812, NFR-531, SL-1689, LG-2017, PL-2016]
---

# FD-1816 — A failed api roll force-removes a stopped pre-existing api container

## Finding

**LOW; owner WK-674; verdict deferred with an owner.** Source: the maintainer's entry
"2026-10-18 14:33:47 BST" (`to-lead.md`), item 1 (A4 of SL 8111's audit). API containers are
stateless, so the impact is a stopped replica lost, not data; no price is affected.

The EXIT trap that FD-1804's fix adds to `deploy/roll-api.sh` (SL-1813, PR #1342) derives the
containers to remove as "every api container now present minus `old`". `old` comes from `api_ids`,
which lists **running** containers only; the removal list comes from `docker ps -aq`, which includes
stopped ones. So on a failed roll a **stopped** api container that existed before the roll is not in
`old`, is counted as new, and is `docker rm -f`'d.

## Evidence

**Filed while #1342 was unmerged; the code has since landed at `a752c9ef` (the merge of #1342) with
`deploy/roll-api.sh` byte-identical to the text read here.** At the filing tree `c1a9c430` it had no
`cleanup_new`. Read at `3264778b` (tree `a67748db`; `deploy/roll-api.sh` is byte-identical at PR #1342's
head `99cc5243`):

- `:30-32` `api_ids()`, with `:31` `docker ps -q` (no `-a`: running only);
- `:36` `mapfile -t old < <(api_ids)`: `old` is the running set;
- `:41-56` `cleanup_new` and its `trap cleanup_new EXIT` at `:56`: `:45-46` `comm -13 <old> <(docker ps -aq …)`
  (`-a`: running and stopped), `:49` `docker rm -f "$c"`.

## Fix direction (ruled; the slice decides the detail)

Build `old` from the same `-a` listing the cleanup uses, or exclude by creation time after the roll's
start. **Red test first:** a stopped pre-roll api container survives a failed roll. Not widened into
SL-1813: a deploy-logic change would cost another SOLO compose gate.

## Disposition

Deferred with an owner: WK-674. The
event that next discharges it: a merged change with the red-first test, or a dated ruling accepting
the absence. Filed under working id 8119.

## Resolution, 2026-11-05

***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor, as the closing act of the mint of SL-1689 (WK-674, LG-2017, PL-2016; ~~this PR, its number and squash written at the merge's date-of-record~~ [`<the merge's PR>`]), on the lead's brief under the maintainer's entry "2026-11-05 09:58:58 GMT" (`to-lead.md`). Delivered remedy, DP-D1 (a) (ruled "2026-11-05 10:08:53 GMT"): in `deploy/roll-api.sh`, `old` is the `-a` listing (`api_ids -a`, stopped containers included) and the scale-out target is `$(( ${#old[@]} + REPLICAS ))`, one set used at every site. **The essay named one site; there were two:** `up --scale` counts the service's containers, stopped ones included, and starts a stopped one, so changing `old` alone would have made the roll fail its `new` count on a stack that should roll. The R0 read on a throwaway project (`gip-s4-runtime`, `r0.log`) confirmed it: after `docker stop` of one of three, `up -d --no-deps --no-recreate --scale api=4 api` started the stopped container and created one new one. A stopped pre-roll replica now counts as old: the success path removes it with the others, and a failed roll's `cleanup_new` no longer removes it. Red first, by cause, in LG-2017, `test_a_failed_api_roll_leaves_a_stopped_pre_roll_container` at the base `roll-api.sh`: `roll-api … cleanup: removed new 9a22623ccc18` and `AssertionError: cleanup removed the stopped pre-roll container 9a22623ccc18` (`1 failed`, rc=1); green after the fix, `1 passed in 95.22s`. The whole `backend/tests/test_deploy_stack_runtime.py` (10 tests at `1a95e467`, naming the NFR-531 roll test and the failed-roll test) passed in the same window; the gate re-runs it at the re-merged head. **Noted, not a defect:** the replica a failed roll "leaves" is present by id and running, because Compose started it when scaling; the harm the essay names, a force-removal of a container the roll did not create, is gone.
