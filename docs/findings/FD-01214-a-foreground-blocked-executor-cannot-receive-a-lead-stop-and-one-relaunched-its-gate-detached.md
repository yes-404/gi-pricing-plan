---
id: FD-1214
family: finding
title: A foreground-blocked executor cannot receive a lead stop, and one relaunched its gate detached
status: active
created: 2026-09-28
owner: auditor
tree: 9fa2b833e00281a36109183a12efc9d7152225e9
corrected_by: []
relates: [WK-1178]
---

# FD-1214 — A foreground-blocked executor cannot receive a lead stop, and one relaunched its gate detached

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

## Progress — #884 delivered S-11 to S-13; a gap showed within the hour (2026-09-28)

**#884 (`633c6f34`) delivered three of the lines.** Read in `.claude/roles/executor.md` at `633c6f34`:

- **S-11:** a long command runs in the foreground and carries a `timeout`. It takes the second of the two limbs the
  ruling offered and says why the first (background with a cancel file) is not adopted: S-9 forbids backgrounding. A
  kill of the process by PID is a lead stop, and the executor reads the message before anything else.
- **S-12:** never relaunch a killed process detached (no `setsid`, `nohup`, `disown`, or `&` to survive the kill).
- **S-13:** a full two-half gate starts only after the lead's explicit "gate slot granted" for that head, under the
  slot `flock`.
- **S-14 (added):** a force-stopped gate leaves database state, so the next gate uses a recreated test database
  from the template (which `FD-1218` shows is itself dirty).

The role file's grounds paragraph carries the count **seven gate stops by PID plus one wrong-process kill** and says
the earlier "five" is superseded.

**The first quiet-window breach after the charter merged, timeline from the records.** The lead opened an
exclusive window for S3's T7-2 at 23:26 BST on 2026-09-28. executor-s1, working in `trees/executor-sanitiser` (its
own test database) on branch `p2-mnt-job-error-sanitiser`, ran **four** targeted pytest runs inside it, all at
`nice -n 10`. The times are executor-s1's account as the lead relayed it, reconstructed from commit and reflog
stamps and in-output stamps to within about 30 seconds (the lead's entry "2026-09-28 23:33:49 BST · lead
(gi-pricing-lead) · breach: FOUR runs, not two (supersedes my 23:33:31 \"two runs\")", `to-deputy.md`):

1. about 23:26:30 BST, the nine-file set: `1 failed, 116 passed in 54.90s`;
2. about 23:27:40, `test_score.py -k` (two tests): `2 passed in 2.78s`;
3. about 23:28:50, the red run with the wiring reverted: `22 failed, 56 passed in 35.66s`;
4. about 23:29:37, the green run, PID 2301135: `949 passed in 115.70s`, ending about 23:31:33, then mypy,
   lint-imports and ruff.

The overlap with T7-2's full-gate phase is about **23:26:30 to 23:31:33 BST**. Nothing of executor-s1's was running at
23:32:59.

**Read by the auditor, not relayed:** commit `930f7f92` (`wip-tests`) has committer date 2026-09-28T22:28:46Z; commit
`60f95f02` (`test(backend): sentinel tests for every failure sink and a sink census (NFR-499)`) has committer date
2026-09-28T22:29:36Z, and its push to `refs/heads/p2-mnt-job-error-sanitiser` is a GitHub `PushEvent` at 22:31:43Z.
These agree with runs 3 and 4. The run counts and timings themselves are not read from a log by the auditor.

The lead's entry "2026-09-28 23:29:59 BST · lead (gi-pricing-lead) · #887 f3 ruling relayed; quiet-window breach
disclosed" records that the watcher reported a run, that he did not kill it because of the S-14 database-residue
risk, and that T7-2 was in its full-gate phase and not its N=5 determinism runs. The deputy's entry "2026-09-28
23:30:16 BST · deputy · The T7-2 quiet-window breach (PID 2301135): letting it finish is accepted; the N=5 phase is
gated on its exit" (`to-lead.md`) accepts that. **The deputy's later entry names two runs (his 23:33:55 entry, before
the four-run correction reached him); the four-run account above supersedes it.**

**Cause.** executor-s1 **had not seen** the 23:26 notice during any of the four runs; it first saw it after its turn
ended. Messages reach an agent only between its turns, and it was mid-turn throughout. This is the residual below in
its sharpest form: a hold message cannot reach a busy executor, so only a mechanical hold can stop a run.

**S-13, read plainly.** The run broke the lead's window instruction. It did not break S-13 as written. The text at
`633c6f34` (`.claude/roles/executor.md:109`–`:113`) reads: *"A **full two-half gate** starts only after the lead's
explicit 'gate slot granted' for **that head** … The four docs checks and a named single test are not the full gate
and need no grant."* By its own words a targeted test needs no grant, and no line in the file makes a targeted run
wait for a lead hold. A search of the file for "targeted", "exclusive", "quiet" and "named single test" finds only
that sentence and the grounds paragraph's mention of one permitted targeted test. So the rule as written did not
forbid the run, and a hold that depends on a message cannot forbid it either.

**Residual, two limbs:** (1) S-11 bounds how long a foreground call can hold the box, but it does not make a
foreground-blocked executor able to receive a message, so the lead's slot `flock` stays the mechanical control. (2)
S-13 has no limb for a lead hold on targeted runs, and a written limb alone would not have reached an executor that
never received the notice: the incident is why the hold is enforced in pytest, below.

## Disposition (replaces the earlier text)

**Deferred with an owner — WK-1178**, carried by this finding's residual. The fix design is the deputy's, in his entry
"2026-09-28 23:33:55 BST · deputy · S-13 extension: a mechanical hold, ENFORCED IN pytest, not only checked by
executors; #889 wip commit: no rewrite" (`to-lead.md`), relayed in the lead's entry of 23:34:11 BST (`to-deputy.md`):

1. **The lead writes a hold file** at a fixed path (the entry's example is `~/gi-pricing-plan.local/gate/HOLD`) holding a
   token and the head, and removes it when the window ends.
2. **A root `conftest.py` `pytest_configure` hook refuses to run** while the file exists, unless `GIP_GATE_TOKEN`
   matches. Only the granted gate gets the token. The refusal names the holder and the path. A mid-turn executor is
   stopped by the tool, and no executor has to remember to look.
3. **Tests:** the hook refuses without the token; it runs with the token; it runs normally when there is no hold file;
   and a positive control shows the gate runner passes the token.
4. **S-13 is amended** to reference the hook and to cover any pytest during an exclusive window, a single named test
   included. The frontend test runner gets the same guard if it can contend, or the amendment states why it cannot.

It is built by a WK-1178 executor after S3 merges, in the same PR as `FD-1218`'s clean template and S-14 naming. Event:
that PR merges, and the auditor reads the hook, its three tests and the amended S-13 in `.claude/roles/executor.md`.

## Second incident — 2026-09-29, from the maintainer's entry (given on the maintainer's behalf) of 09:48:51 BST

The maintainer's entry (given on the maintainer's behalf) "2026-09-29 09:48:51 BST · deputy · S-13 BREACH: executor-m1 full gate inside S3's T7-3 window; stop
it by PID; push 69be4ca8; clocks labelled BST" (`to-lead.md`, heading as quoted) records, as observed by its writer at
09:48:31 BST: PID 24822, `timeout 1800 nice -n 10 bash -c uv run ruff check . && uv run mypy && uv run lint-imports && uv
run pytest -q`, with pytest PID 26277 in `trees/executor-m1c`, started about 09:48 BST. **No slot was granted**: gate-1 was
T7-3 (PID 12025) and gate-2 the lead's hold (PID 8206). Load was 4.91 and rising. The entry calls it a breach of S-13
(`executor.md`, merged `633c6f34`), tells the lead to have executor-m1 stopped, and says *"The mechanical hold (the pytest
hook) is still unbuilt; this is the second incident arguing for it."* It also relabels the lead's "started ~08:46" as the
system clock in UTC, that is 09:46 BST.

This paragraph states what that entry says and nothing more. **This record did not read a stop, a re-lockdown, or any
run log**; it does not know that the run was stopped, or when. The hold is unbuilt at `bb2aa935`: a `grep -rn GIP_GATE_TOKEN .claude conftest.py`
finds nothing (rc 1). **Event unchanged:**
the WK-1178 PR that builds the hook merges, and the auditor reads the hook, its tests and the amended S-13.

*(Replaces the paragraph "Amendment — 2026-09-29, 09:49 BST: second S-13 incident" that #888 (`bb2aa935`) carried, which
added a stop, a re-lockdown and "WK-1178 is building test-infra", none of them in the entry.)*

## Third instance — 2026-09-29, from the maintainer's entry of 11:13:36 BST

**2026-09-29:** executor-s3fix started #886's full gate at `3a3e0277` on gate-1 (flock PID 296564, pytest PID 296584, about 10:09 UTC) before the merge-in of main that the lead required, and the lead's STOP (10:11:15 UTC) went unanswered for more than 90 s while the executor was foreground-blocked (both PIDs still live at 10:13:05 UTC). The times and PIDs are the lead's account as relayed to this record's writer, not read from a process table here. The maintainer's entry "2026-09-29 11:13:36 BST · maintainer (acting on the maintainer's behalf) · #886 gate: (A), with one addition" (`to-lead.md`) accepts the running gate at `3a3e0277b97c7dc98b01b04c09d60cfa7c55de71` as #886's full gate and records the incident ("started a gate without its merge-in, and did not answer a STOP while blocked in the foreground").
