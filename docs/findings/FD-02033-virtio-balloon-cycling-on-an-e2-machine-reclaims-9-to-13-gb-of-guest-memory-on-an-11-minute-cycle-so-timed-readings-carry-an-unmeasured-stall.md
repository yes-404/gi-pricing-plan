---
id: FD-2033
family: finding
title: virtio_balloon cycling on an e2 machine reclaims 9 to 13 GB of guest memory on an 11-minute cycle, so timed readings carry an unmeasured stall
status: active
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8393, minted 2026-11-06
owner: lead
tree: cded9f0e1953f2db6a6a1375892257a1a4822fc3   # origin/main when drafted; the evidence is a live host read, not a tree
corrected_by: []
relates: [WK-1178, FD-2007]
---

# FD-2033 — virtio_balloon cycling on an e2 machine

*(Minted 2026-11-06 as FD-2033 from working id 8393, in the docs batch 12 PR.)*

## Finding

**MEDIUM, owner WK-1178** (to-lead "2026-11-05 18:36:41 GMT" ruling 3). On this host class, guest memory of about 9 to 13 GB is reclaimed on an approximately 11-minute cycle, with PSI pressure, through `virtio_balloon`; timed readings on an e2 machine carry an unmeasured periodic stall.

## Evidence

Read by the maintainer at 18:36:27 GMT, mid-dip: `balloon_inflate` 325,613,355, `balloon_deflate` 323,289,643, so 2,323,712 pages held = 9.08 GB (4 KiB pages); MemFree 5.5 GB at 18:36:21, AnonPages 7.7 GB. The dip arrived on the cycle after pricing-catering's frequency workers exited at 18:28, so that tenant is cleared and no seat is at fault. **Three cycles held 13 to 16.5 GB, about 100 s down, with an instant return, at about 11 minutes; available memory plus the balloon stayed flat at about 23 GB.** The period is an estimate (ruling 4).

## Limits

**Not a claim about E2's design:** nobody here has read Google's documentation; the mechanism's name stays "virtio_balloon cycling on an e2 machine". **Not proved: any effect on any NFR number.** Two cycles are enough only for the shape of the cycle, not for its period or depth; the third cycle is the added evidence above. The `load1`, gates and demos are unaffected in form; from now on a gate's timed stage reads the counters, one line at START and END of the demo, and memwatch fires on two consecutive samples under 7,000 about 13 s apart.

*(Dated line, 2026-11-05, docs batch 12, by the executor, on the lead's relay of the maintainer's entry of about 23:25 GMT: **two demos on 5 Nov with nothing timed beside them differed by 66 s on the dislocation step**, F 531 s (demo 22:28:59 to 22:53:53 UTC; `~/gi-pricing-plan.local/scratch/slf-gate/gate/gate.log`) and C 597 s (22:54:01 to 23:21:19 UTC; `~/gi-pricing-plan.local/scratch/slc-gate/gate/gate.log`), both rc 0, load1 1.92 and 2.41 at their starts. F had two git merges beside it, about 22:31 to 22:35 (the lead's account; not in either log). The logs' balloon lines read held 0 MB at F's start and 2151 MB at its end, and 3505 MB at C's start and 0 MB at its end. **This bounds what a single demo reading can say; it is not a balloon effect, and no cause is claimed.**)*

## Disposition

Open, owner WK-1178. Goes to the §14 draft beside FD-2007's host question; a dedicated host is the user's call. Filed as working id 8393.

*(Dated correction, 2026-11-06, docs batch 13, by the executor, on the maintainer's entry "2026-11-06 03:16:38 GMT" (MERGE-ACK of #1439): **the title and the Finding say "9 to 13 GB"; that was the first reading (9.08 GB held at 18:36:27 GMT on 5 Nov), and the maintainer's later reads took about 13 to 16.5 GB.** The finding stands; S2's recorded counters give the figure of record, not the first reading. The original sentence and the title are left as merged.)*

*(Dated line, 2026-11-06, docs batch 13, by the executor, on exec-minth's and the lead's relay: **SL 8377's demo END, 2026-11-06 08:38:32, read PSI "some" avg10 1.16 and "full" avg10 0.98.** It is the first non-zero reading at a demo end in the eight seeded or fetched demos since 5 Nov 22:28; the demo was PASS; the cause was not traced; no effect on any result is claimed. It is an untraced reading, accepted as one.)*

*(Dated line, 2026-11-06, docs batch 13, by the executor: **the dislocation step, read from each gate's `gate.log` under `~/gi-pricing-plan.local/scratch/`, took 531, 597, 527, 590, 524, 530, 512 and 517 s in the eight demos of 5 to 6 Nov** (`slf-gate`, `slc-gate`, `sl8389-gate/demo-run2`, `slm-gate/demo-run2`, `slh-gate`, `slg-gate`, `sl8340-gate`, `sl8377-gate`; row `| dislocation #1 |`). The spread is 85 s (597 less 512). **This bounds what a single demo's reading can say.** No cause is claimed. The order of the eight above is the lead's; the log paths are matched by the value and the row, checked at this tree.)*
