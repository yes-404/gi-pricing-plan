---
id: FD-8393
family: finding
title: virtio_balloon cycling on an e2 machine reclaims 9 to 13 GB of guest memory on an 11-minute cycle, so timed readings carry an unmeasured stall
status: active
created: 2026-11-05   # working id 8393, minted at the batch 12 mint
owner: WK-1178
tree: cded9f0e1953f2db6a6a1375892257a1a4822fc3   # origin/main when drafted; the evidence is a live host read, not a tree
corrected_by: []
relates: [WK-1178, FD-8350]
---

# FD-8393 — virtio_balloon cycling on an e2 machine

## Finding

**MEDIUM, owner WK-1178** (to-lead "2026-11-05 18:36:41 GMT" ruling 3). On this host class, guest memory of about 9 to 13 GB is reclaimed on an approximately 11-minute cycle, with PSI pressure, through `virtio_balloon`; timed readings on an e2 machine carry an unmeasured periodic stall.

## Evidence

Read by the maintainer at 18:36:27 GMT, mid-dip: `balloon_inflate` 325,613,355, `balloon_deflate` 323,289,643, so 2,323,712 pages held = 9.08 GB (4 KiB pages); MemFree 5.5 GB at 18:36:21, AnonPages 7.7 GB. The dip arrived on the cycle after pricing-catering's frequency workers exited at 18:28, so that tenant is cleared and no seat is at fault. **Three cycles held 13 to 16.5 GB, about 100 s down, with an instant return, at about 11 minutes; available memory plus the balloon stayed flat at about 23 GB.** The period is an estimate (ruling 4).

## Limits

**Not a claim about E2's design:** nobody here has read Google's documentation; the mechanism's name stays "virtio_balloon cycling on an e2 machine". **Not proved: any effect on any NFR number.** Two cycles are enough only for the shape of the cycle, not for its period or depth; the third cycle is the added evidence above. The `load1`, gates and demos are unaffected in form; from now on a gate's timed stage reads the counters, one line at START and END of the demo, and memwatch fires on two consecutive samples under 7,000 about 13 s apart.

## Disposition

Open, owner WK-1178. Goes to the §14 draft beside FD-8350's host question; a dedicated host is the user's call. Filed as working id 8393.
