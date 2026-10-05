---
id: FD-9640
family: finding
title: Artifact B is stale and wrong a day after F58 and F91 were recorded resolved
status: active
created: 2026-09-29
owner: auditor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
corrected_by: []
relates: [WK-1178]
---

# FD 9640 — Artifact B is stale and wrong a day after F58 and F91 were recorded resolved

## Finding

**Proposed by the auditor for the lead's verdict (plan review 16, P9): a recurrence of both F58 and F91.**
FD 9640 is a working id, minted at the records PR. Read at `origin/main` `2c2bbcdf`, 2026-09-29.

## Evidence

### What the two rows claimed

- **F58** ("Artifact B has no live writer", `docs/findings/register.md`), decision cell:
  *"Resolved 2026-09-27 (`CR-1167` … plan review 14 …). The watcher now invokes
  `write_runtime_state.py cycle` each cycle and rewrites on change (RL-907(d)).
  `position.written_at` is 2026-09-27T14:03:07Z, written when PL-1144 moved to "in progress"
  (watcher cycle 43)."*
- **F91** ("The RFC-895 runtime-state writer has not run since 02:03Z"), decision cell:
  *"Resolved 2026-09-27 (`CR-1167` …), on F58's evidence. The writer ran at 2026-09-27T14:03:07Z …
  Falsifiable: discharged when `mtime` advances on a cycle that re-derives `position`, proven by
  two consecutive cycles."*

The mechanism both rest on is an agent instruction (the watcher role's "each cycle" sentence,
`.claude/roles/watcher.md`), not a process. F58's own opening finding was that this sentence
was true of no running process.

### Measurement, 2026-09-29T15:37:52Z to 15:38:20Z (`date -u` in the same command)

1. `stat` of `~/gi-pricing-plan.local/handover/runtime-state.json`: mtime
   **2026-09-28 16:26:22.05Z**, 1525 bytes, about **23 h 12 min** before the read.
2. Inside the file, `position.written_at` is `2026-09-28T16:26:22Z`;
   `in_flight_expensive_verifications.written_at` is `2026-09-26T16:44:21Z` (entries empty).
3. **The position is wrong, not only old.** It reads `origin/main 9f6bfed1` (committed
   2026-09-28T17:19:12+01:00) and says slice `PL-930 … PL-1189 (leaf, WK-672 via work:, active,
   not started)`. At `2c2bbcdf` (38 commits later, `git rev-list --count 9f6bfed1..origin/main`)
   `docs/INDEX.md` shows PL-1189 `executed`, PL-1205 `executed` and PL-1213 `in progress`.
   `git diff 9f6bfed1 origin/main -- docs/INDEX.md | grep -E '^[-+]\| (WK|PL)-'` prints, at 2c2bbcdf:

   ```text
   -| PL-1189 | plan | leaf | WK-672 Slice 2 — Golden Quotes and promotion re-scoring: leaf plan | active | planner | P2 | not started |
   +| PL-1189 | plan | leaf | WK-672 Slice 2 — Golden Quotes and promotion re-scoring: leaf plan | active | planner | P2 | executed |
   +| PL-1205 | plan | leaf | WK-672 Slice 3 — Property assertions and regression runs: leaf plan | active | planner | P2 | executed |
   +| PL-1213 | plan | leaf | WK-672 Slice 4 — Quote Sandbox compare endpoint (FR-262 backend limb): leaf plan | active | planner | P2 | in progress |
   +| PL-1237 | plan | map | WK-674 — Deployment, environments, atomic switchover, rollback, shadow and tenancy: map plan | draft | planner | P2 | not started |
   ```

   The position moved several times and B did not.
4. **F91's falsifier is met the wrong way**: the position moved while mtime stayed.
5. **No writer process.** `ps -eo pid,lstart,etime,cmd | grep write_runtime_state` matches
   nothing. `crontab -l`: no crontab. `watcher-runtime-state-cycle.sh` (untracked, in `handover/`)
   loops calling the writer, and is not running (`ps` for it matches only the probe itself);
   its log `runtime-state-cycle.log` last line is **2026-09-18 10:04:11 UTC**.
6. **The watcher this session is running and did not write.** `--agent-id watcher@session-92b3ca72
   --model haiku`, pid 6647, started 08:45:32, 6 h 52 min elapsed at the read. Its cmdline holds
   no reference to the writer. It runs in the repository root.
7. **The derivation tool named in B is gone.** `position.work.read_from` and `slice.read_from`
   cite `/home/puzhenhao1989/.claude/jobs/66723b39/tmp/p2/watcher/derive.py`. That job dir does
   not exist (`ls`: no such file), and `find` for a `watcher/derive.py` finds none. The 09-28
   write was made by a script that lived in the job directory the 09-28 restart deleted, so
   the resolution's "each cycle" had no durable tool behind it.

### Why this is a recurrence and not an expected staleness

RL-907's rule is that B changes only when the position moves. The position has moved, so
staleness is not the healthy case. The resolution claimed a standing behaviour ("each cycle");
what existed was one hand-run derivation, made by a tool held in an ephemeral directory. That
is F58's original shape (a charter naming a mechanism nothing runs), one day after being
recorded closed, and F91's original shape (no write across several position changes).

## Disposition

Proposed; the verdict is the lead's.

- **F58 and F91: reopen in place** with a dated annotation quoting the "Resolved 2026-09-27"
  text each supersedes (the register's convention), citing this finding.
- **This finding is the evidence essay for both.** The fix needs a durable derivation tool in
  the repository (not a job dir) and a durable trigger; neither exists. The event that next
  confirms it is a watcher cycle that advances the mtime on two consecutive position moves,
  measured with `stat`, not by the watcher's report.
- Owner: WK-1178, per the maintainer's entry "2026-09-29 16:34:39 BST · … FR-217 GUARD FAILS OPEN …; P9 recurrence check" (`to-lead.md`): "If the writer has stopped again, it is a recurrence: reopen the rows with a dated note, owner WK-1178." The fix is a durable in-repo derivation tool plus a durable trigger, since the 09-28 `derive.py` died with the deleted job dir.

## Re-measurement, 2026-10-05 (before mint)

Amended 2026-10-05 before mint: the measurement above is a point in time (2026-09-29, tree
`2c2bbcdf`); this section re-measures at `origin/main` `47d770e8` and is why the front-matter
`tree:` now names that commit. Run 2026-10-05T08:53Z (`date -u` in the same session):

1. `stat -c '%y' ~/gi-pricing-plan.local/handover/runtime-state.json` → `2026-10-04
   18:59:04 +0000`: the **mtime moved** after the 09-29 measurement.
2. `position.written_at` in the same file, read with `python3 -c "import json;…"` →
   `2026-09-29T21:36:41Z` (six days old), and `position.slice.value` is `''`. So the mtime
   is not evidence of a position re-derivation: the content `written_at` did not move, which
   is the gap between F91's mtime and `written_at` that this finding already names.
3. `pgrep -af 'write_runtime_state|watcher-runtime-state'` → no match: no writer process.
4. `watcher-runtime-state-cycle.sh` is not running.
5. The writer itself resolves at main: `.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py`
   (present since `b551060a`, 2026-08-31). What the finding says is missing is the durable
   *trigger* and the derivation of the position, not that script's existence.
6. Register rows F58 and F91 still read "Resolved" at `origin/main` (rows opened by
   "Artifact B has no live writer…" and "The RFC-895 runtime-state writer has not run…").

The finding holds unchanged. Mint note: `PL-1277` cites this finding by its working id
(`FD 9640`); at mint that plan, being frozen, is re-pointed by a dated delta, not edited.

Re-anchored 2026-10-05 at main `caa4e411`: re-measured 2026-10-05T11:54Z (`date -u` in the
same session). (1) `stat -c '%y'` on `runtime-state.json` → `2026-10-05 11:37:37 +0000`, so
the mtime moved again after item 1 above (`2026-10-04 18:59:04`). (2) `position.written_at`
in the same file is still `2026-09-29T21:36:41Z` and `position.slice.value` is still `''`:
the content was not re-derived, so the mtime remains no evidence of a position re-derivation.
(3) `pgrep -af 'write_runtime_state|watcher-runtime-state'` → no match. (4) The writer
`.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py` is present at main.
(5) F58 and F91 still read "Resolved" at `origin/main` `caa4e411` (`PL-1277` still cites this
finding by working id `FD 9640`, unminted). The defect reproduces; the finding holds.
