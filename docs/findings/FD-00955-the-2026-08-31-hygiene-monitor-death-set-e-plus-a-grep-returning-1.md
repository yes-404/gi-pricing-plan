---
id: FD-955
family: finding
title: the 2026-08-31 hygiene-monitor death: `set -e` plus a grep returning 1
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-01
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F67.md
---

# F67 — the 2026-08-31 hygiene-monitor death: `set -e` plus a grep returning 1

Evidence essay for the register row self-named `(F67)` in `docs/findings/register.md`. The
finding: the hygiene monitor armed on 2026-08-31 died on its **first clean sample**, and the
mechanism — `set -e` combined with a grep pipeline that returns 1 when there is nothing to
report — went undiagnosed until 2026-09-01. A monitor built to detect abandoned work was
dead from the moment it was armed, long before any work it watches for could appear, and
every observation that could have revealed the death read as health.

The primary sources for this file are local handover artifacts, not under version control:
`~/gi-pricing-plan.local/handover/watcher-state.md` (the monitor's state record, including
the diagnosis), `~/gi-pricing-plan.local/handover/SESSION-2026-08-31-team-restart.md` (the
day-of record), `~/gi-pricing-plan.local/handover/SESSION-2026-09-01-nt-0016.md` §6.5 (the
session that owed this filing), and the script itself,
`~/gi-pricing-plan.local/handover/watcher-monitor-improved.sh`. Because those files can be
lost or moved, the load-bearing lines are quoted here in full.

## The incident (2026-08-31)

- **Armed 15:04 UTC**, PID recorded **36246**, `watcher-monitor-improved.sh` at a 60-second
  sample interval and 900-second dwell threshold, watching the shared checkout at
  `/home/puzhenhao1989/gi-pricing-plan`.
- **Died within one sample (~60 seconds)** and remained dead until at least 15:34 UTC.
  `watcher-state.md`, "Evidence of Silent Death", four items: (1) `ps -p 36246` → gone;
  (2) `hygiene-monitor.log` 0 bytes, last touched 15:04; (3)
  `hygiene-fingerprint-state.txt` last written 15:04:52 — the script touches it every
  sample, so ~30 touches were owed by 15:34 and **zero** arrived; (4) `pgrep -af
  watcher-monitor` matched only the pgrep command itself.
- **At 15:28 the monitor was reported running** — from the PID recorded at 15:04, not a
  live check. `SESSION-2026-08-31-team-restart.md` §5 states it plainly:

  > "The hygiene monitor built today to catch this class died of it. Armed at 15:04, it ran
  > about one sample and stopped. At 15:28 it was reported running — from a PID recorded at
  > 15:04, not a live check. Nobody could tell, because the monitor emits output *only* on an
  > anomaly, so an empty log and a quiet channel are exactly what a healthy monitor produces.
  > **'No output' and 'not running' were the same observation.** Found by checking the
  > fingerprint file's mtime, which had not moved in thirty minutes at a sixty-second sample
  > interval."

- **The cause was undiagnosed that day.** The death was observed (static state-file mtime)
  but not explained; the monitor was deliberately not re-armed, and `watcher-state.md`
  recorded the death rather than claim a monitor. The diagnosis landed the next day:
  `watcher-state.md`, "ROOT CAUSE IDENTIFIED (2026-09-01): `set -e` combined with grep
  pipeline exiting on no matches".

## The mechanism — the first clean sample kills the script

`set -e` stands at line 16 of the script (verified directly in the current file,
2026-09-01). The uncommitted-changes pipeline — line 71 as the script stood at the time of
the diagnosis; line 80 in the current, fixed file — was:

```bash
NON_UNT=$(echo "$OUT" | grep -v '^??' | grep -v '^$')
```

On a clean tree, `git status --porcelain` (`$OUT`) is empty; `grep` with no matches returns
exit code 1; `set -e` exits the script on the spot. The loop never starts, the sleep never
runs, and the state file is never touched again. The first sample of a clean tree — the
normal state of this repository — was also the last.

**Reproduced independently for this filing (2026-09-01):**

```bash
$ bash -c 'set -e; OUT=""; NON_UNT=$(echo "$OUT" | grep -v "^??" | grep -v "^$"); echo REACHED_LOOP'
# exit code 1, REACHED_LOOP never printed
```

The identical reproduction appears in `watcher-state.md` (2026-09-01 10:00 UTC). The
mechanism also explains the specific evidence of the 2026-08-31 death, and no other
first-sample exit does: a `git status` failure or a `.git` lock would have printed an
immediate ANOMALY line (the log was 0 bytes, so neither happened), and a dirty tree would
have kept the loop — and the state-file touches — alive. The only path consistent with all
four items of evidence is the empty-`$OUT` grep under `set -e`.

**The consequence is inverted**, as `watcher-state.md` puts it: a monitor designed to
detect abandoned work dies the moment there is nothing to report. It could only survive
while already watching dirty files; this repository's tree is clean nearly all the time,
so the monitor was never capable of the job it was armed for.

## Why death read as health

Three properties stacked:

1. **Anomaly-only output.** The script prints nothing unless it detects something, so an
   empty log is exactly what a healthy monitor produces. No heartbeat was added in the
   fix either — deliberately, per `watcher-state.md`: `ps -p <pid>` and the state file's
   mtime are the adopted liveness proxies, judged stronger than a heartbeat line.
2. **`pgrep -f` self-match.** A liveness check whose own command line contains the pattern
   matches itself and reports a dead monitor as alive.
3. **A PID recorded at arm time is a handle, not a process.** The 15:28 "running" report
   read a number written at 15:04.

This is the `CLAUDE.md` §13 class: a check that was silent, and whose silence was read as
success. `watcher-state.md` states it the same way: *"This is `§13` class: a check or
report that was silent and silence read as success, one layer deeper than initially
diagnosed."*

## The fix and its verification (2026-09-01)

The repair lives in the local script only:

```bash
# Before:
NON_UNT=$(echo "$OUT" | grep -v '^??' | grep -v '^$')

# After:
NON_UNT=$(echo "$OUT" | grep -v '^??' | grep -v '^$' || true)
```

- **Sweep:** the line was the only location where `set -e` met a command returning
  non-zero on a clean tree; every other pipeline carries a fallback (`watcher-state.md`,
  "Fix Applied").
- **Liveness verified on a clean tree** (2026-09-01 09:56–09:58 UTC): the fingerprint
  state file's mtime advanced exactly once per 60-second sample across three consecutive
  reads — the very property the dead monitor had failed.
- **Verified against the current script for this filing** (2026-09-01): `set -e` still at
  line 16; the fixed pipeline, `|| true` included, now at line 80.

## Scope of this finding

- **The defect is repaired in the local script**, and this row plus `watcher-state.md` are
  the durable record of the incident and its cause. The script has no repo home — nothing
  under version control carries it or its fix (`git grep watcher-monitor` at `43fd277`
  finds only this finding's sources and a WK-671-era plan reference to a predecessor path) —
  so a future session arming a monitor relies on the local file's current state and on
  this register row for the trap.
- **Not part of this finding**, each recorded where it belongs:
  - The **untracked-file blind spot** (the `^??` filter): a real, tested property of the
    script, and not the cause of the 2026-08-31 death (`watcher-state.md`, "Untracked-file
    blind spot", with the 2026-09-01 correction).
  - The predecessor's **dirty-README test residue** and the unfinished 900-second dwell:
    that session's false negative — a different incident with a different cause
    (`watcher-state.md`, CORRECTION #2).
  - The **no-heartbeat design gap**: recorded, and deliberately declined in favour of
    `ps -p <pid>` plus state-file mtime.
- **Provenance.** Filed as owed by the 2026-09-01 session record
  (`SESSION-2026-09-01-nt-0016.md` §6.5): *"The hygiene-monitor finding is unfiled. The
  monitor died on its first clean sample (`set -e` plus a grep returning 1), so a monitor
  for abandoned work was dead long before the work it watches for could appear — the
  undiagnosed cause of the 2026-08-31 death. Filing is the auditor's, the verdict the
  lead's."* Every fact above was re-verified against the primary sources named, not
  against that summary.
