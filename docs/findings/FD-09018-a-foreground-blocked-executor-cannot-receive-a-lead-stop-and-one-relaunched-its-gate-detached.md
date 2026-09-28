---
id: FD-9018
family: finding
title: A foreground-blocked executor cannot receive a lead stop, and one relaunched its gate detached
status: closed
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

## Resolution

**Resolved 2026-09-28 by #884, merge commit `633c6f34`** (`docs(roles): executor.md — foreground timeout, no
detached relaunch, gate by grant (WK-1178) (#884)`). Read in `.claude/roles/executor.md` at `633c6f34`:

- **S-11:** a long command runs in the foreground and carries a `timeout`. It takes the second of the two limbs the
  ruling offered and says why the first (background with a cancel file) is not adopted: S-9 forbids backgrounding. A
  kill of the process by PID is a lead stop, and the executor reads the message before anything else.
- **S-12:** never relaunch a killed process detached (no `setsid`, `nohup`, `disown`, or `&` to survive the kill).
- **S-13:** a full two-half gate starts only after the lead's explicit "gate slot granted" for that head, under the
  slot `flock`.
- **S-14 (added):** a force-stopped gate leaves database state, so the next gate uses a recreated test database
  from the template (which `FD-9022` shows is itself dirty).

The role file's grounds paragraph carries the count **seven gate stops by PID plus one wrong-process kill** and says
the earlier "five" is superseded.

**Residual:** S-11 bounds how long a foreground call can hold the box. It does not make a foreground-blocked
executor able to receive a message, so the lead's slot `flock` stays the mechanical control.
