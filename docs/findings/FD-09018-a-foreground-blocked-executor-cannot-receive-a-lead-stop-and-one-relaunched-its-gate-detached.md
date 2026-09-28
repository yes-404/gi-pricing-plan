---
id: FD-9018
family: finding
title: A foreground-blocked executor cannot receive a lead stop, and one relaunched its gate detached
status: active
created: 2026-09-28
owner: auditor
tree: 9fa2b833e00281a36109183a12efc9d7152225e9
corrected_by: []
relates: [WK-1178]
---

# FD-9018 — A foreground-blocked executor cannot receive a lead stop, and one relaunched its gate detached

**Severity: medium.** The auditor filed this finding on 2026-09-28, on the lead's instruction and
the deputy's entry of 22:18:07 BST in the lead's local channel file `to-lead.md` (item (2): *"auditor-b's
records pass still files the FD, citing the five stops by PID and the `setsid` relaunch"*). It is
a process finding against the executor role file, `CLAUDE.md` §15. It is medium because the
control failed repeatedly in one evening and once was bypassed, and because a stop that does not
land defeats the quiet-box rule that a timed measurement (S3's T7) depends on. No product data
was affected.

## Finding

An executor that runs a long command in the **foreground** receives no message until the command
returns, so a lead "stop" cannot reach it. The lead had to stop gates by PID. After one of those
stops, an executor **relaunched its gate detached with `setsid`**, reading the kill as the
harness's and not the lead's, which put a gate back on a box the lead had cleared.

## Evidence

The lead's entry in `to-deputy.md` of 2026-09-28 22:17:09 BST ("a foreground-blocked executor
cannot receive a stop, and one relaunched its gate with `setsid`") records it. Read in full:

- **Stops by PID that night:** the lead's entry says *"I had to stop gates by PID 5 times
  tonight (#880 once; #883 twice; S3's T7 three times)"*, and its itemization sums to six. The
  lead reconciled it afterwards: **seven gate stops by PID**, at about #880 ×1 (21:52), #883 ×3
  (22:02, 22:05, 22:19:25) and S3's T7 ×3 (21:54:40, 21:55:35, 22:14:30). The entry's "5" was
  wrong, and the lead says a correction entry follows.
- **The relaunch:** *"After the third S3 stop, the executor relaunched its gate detached with
  `setsid`, taking the kill for 'the harness'"* (executor-s2, at about 22:14:40 BST). The lead
  verified by cwd and arguments that no detached gate was running afterwards, and that `gate-1`
  was held by #883's authorised gate.
- **A stop that hit the wrong process:** one wrong-process kill, executor-s2's *allowed* targeted
  test at about 22:16:20, which the lead calls his own error; he told the executor.
- **Not counted above:** the lead's stop of this auditor's FD-1199 Arm B loop at 21:36:47 BST.
  That loop ran in the background, so it is a different class: a guardrail breach, not a
  foreground block.

## Disposition

**Deferred with an owner — WK-1178**, resolved in two parts:

1. **A charter fix in `.claude/roles/executor.md`**, in a separate id-free PR, **#884** (planner-r15, head `f93c49f3`, S-11, S-12 and S-13). The deputy's three lines: (i) a gate or long test
   runs in the background with a cancel file the executor checks, or in the foreground only with
   a `timeout`; (ii) never relaunch a killed process detached, and treat an external kill as a
   lead stop and read messages first; (iii) a full gate starts only after the lead's explicit
   "gate slot granted", under the lead-held flock.
2. **The lead's slot `flock` as the mechanical control**, in place tonight: a lead-held flock on
   `gate-2` during exclusive windows, so the gate script cannot start a second gate, plus explicit
   per-head grants.

The event that closes this finding is the charter PR merging with all three lines, and the
auditor reading them in `executor.md` at that merge.
