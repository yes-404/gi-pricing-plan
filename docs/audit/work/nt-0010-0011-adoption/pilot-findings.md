# Pilot findings — `CLAUDE.md` §15 step 6

**The pilot:** W11 slice 1, 2026-08-29, run by a six-member team spawned from
`.claude/roles/*.md` and from nothing else. §15 step 6 exists to test whether the role files
are sufficient as spawn inputs. This file is its output.

**Why it is here rather than on the task board.** These findings were collected on the
session-local task board, which dies with the session — the precise durability trap this
same adoption's handover rework was told to fix. They feed §15 step 7 (close, and the dated
superseded note on `NT-0010`/`NT-0011`) and the maintainer's gate, both of which happen
after the board is gone.

## Scope, so nothing here is overclaimed

The role-file gaps repaired before the pilot were found by **directed inspection**, not by
the pilot. The pilot therefore **cannot** be cited as evidence that the original role files
were sufficient a priori — they were not. What it tests is narrower and is the only claim
this file makes: whether the **repaired** files are sufficient to spawn a working team from.

The same limit binds each finding below. A gap the pilot found is evidence about the file
it is against. It is not evidence that the file is otherwise complete.

## P1 — `watcher.md` does not require proving an armed watch is alive

**Resolved, after four rounds.** Four reports of a live watch with a named pid; the first
three false, every pid non-existent, each disproved with `kill -0`/`ps` and a positive
control. Reports 2 and 3 arrived *after* direct correction with evidence. What broke the
loop was not re-asking it to arm, but telling it to **stop claiming and diagnose**. Report 4
was true: pid 514021, running `balance_watch.py` from the skill path.

*(Corrected 2026-08-29, after this file had already merged. It first read "token read from
the durable source", which invites the reader to think the poller opens
`claude-deepseek.sh`. It does not, and should not. The chain the skill prescribes is:
durable source → `extract_token.py` → a 0600 session-ephemeral cache → `TOKEN_FILE`. Checked
against the live process rather than the report: pid 514021's environment names
`TOKEN_FILE=<job-dir>/tmp/.ds_token`, which is precisely the form
`.claude/skills/balance-watch/SKILL.md` line 40 prescribes.)*

**The gap.** The charter's poller-silence principle covers a watch that *stops* emitting,
not one that *never started*. A Monitor task id is not a live process; an "armed" log line
is not proof. The agent identified it precisely: *"Charter does not require post-arm
verification; handover §4 Step 8 treats it as part of the re-arm procedure"* — the procedure
lived in the **ephemeral handover**, not the **durable charter**.

**Fix:** `watcher.md` requires liveness proof after arming, and states that neither a
Monitor id nor its own log line is that proof.

## P1b — an agent's own retries manufacture the evidence it then diagnoses

**New, and the sharpest epistemic result of the pilot.** Having finally succeeded, the
watcher reported that repeated "armed at" lines between 14:39 and 14:41:52 proved the script
was exiting immediately, that Monitor was broken, and that the mechanism should be replaced.

All three conclusions were wrong. Pid 514021 had been alive 97 seconds with readings logged
at 14:41:02 and 14:41:48. The ten banners were **its own four arming attempts**. It read a
log it had itself polluted, inferred a systemic tool failure, and asked to replace a working
poller.

**Generalisation:** when you retry a failing action, **your retries enter the evidence**.
Subtract your own attempts before diagnosing from a log, or diagnose from live state
(`ps`, `kill -0`), which retries cannot pollute.

## P2 — a charter naming a skill does not stop a fresh session using a handover copy

The watcher first armed against the **ephemeral job-dir copy of the script**, hours after
the skill was filed to end exactly that. The pointer existed; the **precedence** did not.
Its own state file records the repair in those terms: *"re-armed 2026-08-29 14:41 UTC,
corrected to use skill-filed paths"*.

**Fix:** the skill is authoritative; the handover carries runtime state only; where they
disagree, the skill wins.

**Correction, 2026-08-29, after this file had already merged.** This finding first read
"armed against the ephemeral job-dir **token** path". That is the wrong artifact, and it
inverts the rule. The **token cache** belongs in the job directory —
`.claude/skills/balance-watch/SKILL.md` prescribes exactly that and explains why: *"`.ds_token`
is a cache, not the token's home… conventionally a job directory's `tmp/`, which is ephemeral
and gone once that job directory is… Losing `.ds_token` loses only the cache, never the
token."* Filed as written, this finding would have sent someone to "fix" a compliant
configuration. The defect was always the **script** path.

**And the root cause is still live**, which the corrected reading is what exposes.
`watcher-state.md` §4 Step 1 — the re-arm procedure a *successor* watcher is handed — still
says `python3 <job-dir>/tmp/extract_token.py` and *"adapt extract_token.py to your job dir"*,
months after `extract_token.py` was filed at
`.claude/skills/balance-watch/scripts/extract_token.py`. So the next spawn re-creates P2 by
following its own instructions. P2 was never fixed at its root; only the running process was
repaired. **Fix:** the successor procedure points at the skill's script, and the handover
stops carrying a copy of it.

## P3 — `reporter.md` does not say who arms the reporter cycle

Filed unprompted by the pilot-reporter, in exactly the form §15 asks for.

**Ruled:** the role arms its own mechanism at spawn. Accepted wording — *"On spawn, arm the
persistent reporter-cycle Monitor from `.claude/skills/reporter-cycle/scripts/reporter-cycle.sh`
with `REPORTER_HANDOVER_DIR` set to this session's handover path, then prove liveness with
`ps -p`."* The same question should be put to `watcher.md`.

## P4 — "slice" means different things in `delivery-process.md` and in a plan

Found by the pilot-planner. `delivery-process.md` §4/§6 define a Slice as one TDD leaf, one
PR. The frozen W11 plan's "Slice 1" holds five tasks. So §7's retry caps and §8's
no-two-at-once govern a unit that differs **fivefold** between the two documents the team
runs on.

**Ruled:** run Tasks 1.1–1.5 as five sequential process-slices, one PR each, frozen map
unedited — applying the process's granularity rather than re-cutting, so nothing frozen is
touched.

**The defect remains.** `CLAUDE.md` §13's own rule — *a word with two scopes says which it
means* — is violated between the two governing documents. **Fix:** `delivery-process.md`
distinguishes the process-slice (one PR, one gate) from a plan's slice heading (a group of
tasks), or the plan template stops using the word for the group.

## P5 — standing an agent down by message makes it idle, not gone

Found by the pilot-auditor during orientation. All six `w11-*` agents remained alive after
acknowledging stand-down — twelve agent processes running at once — and four worktrees
stayed **locked** by them.

**Verified before accepting:** no unmerged work is trapped; every locked branch was already
merged. The locks are correct behaviour, because the sessions holding them genuinely are
alive. The defect is that the stand-down procedure **has no step that releases the
resource**.

Same family as the recorded trap that stopping something does not kill what it started —
first seen with Monitor tasks in W10, now with agent lifecycles.

**Fix:** the stand-down procedure must state that stand-down is not termination, that
worktree locks persist while the agent lives, and that a successor should cut a fresh
worktree rather than wait for a lock to clear.

## P6 — a monitoring mechanism with a reader, a documented writer, and no writer

Found by the pilot-reporter, about its own tooling, and then found to be twice as large as
either of us first said. **This section was rewritten after its first two versions were
wrong**; the versions are kept below because the sequence is the finding.

**What actually happened, in order.**

1. The reporter's nudge read *"stale 59 minutes (last: 11:46Z)"*. At 14:45Z that is 179.
2. Asked to check its arithmetic or its marker, it verified the marker correct and
   attributed the error to itself: it had computed the figure by hand.
3. Told to read the script's output rather than recompute, it reported that `nudge.py`
   emits only `NUDGE_NEEDED` and discards the age. **The lead ruled a code change on that
   report without opening the script.**
4. `nudge.py`'s `log_nudge` writes the age to `nudge.log` on every nudge. Both values were
   sitting in that file, correct, the whole time:

       14:45:01Z - nudge sent - lead status 179.0 min old (>20.0 min threshold)
       15:00:02Z - nudge sent - lead status 194.0 min old (>20.0 min threshold)

   The reporter's two messages said **59** and **174**. The script was right both times; the
   hand arithmetic was wrong both times; and the ruled fix was unnecessary.
5. Asked why an acknowledgement had not cleared the nudge, the reporter answered that *"the
   marker updates only when `reporter.py` detects a fresh lead status post to Slack"*.
6. **`reporter.py` contains no reference to the marker.** Across the repository, all nine
   worktrees, the handover directory and the job directory, every occurrence of
   `.last_lead_status_ts` is a **read** — `nudge.py:16` and `nudge.py:77`. Nothing writes it.
   Its mtime equals its own content: written once at 11:46:00Z and never touched again.

**The finding.** The staleness detector has a reader, a *documented* writer, and no actual
writer. Its all-clear state is unreachable, so it emits true-but-unactionable alarms
forever and escalates on a condition that no action can satisfy. A monitor that cannot be
satisfied is not a strict monitor; it is a broken one, and it is worse than none, because it
trains its reader to discount it.

**The propagation is the interesting half.** Three nodes asserted a writer that does not
exist, none of them checking: the previous reporter's stand-down report (*"auto-updated on
lead messages"*), `reporter-state.md:29` and `:90` (*"updated on fresh lead status"*,
*"Initialize … on first lead message"*), and the current reporter, which inherited the claim
from that state file and restated it to the lead as a mechanism. The lead then ruled on it.
**Four restatements, no reads.**

**Fix**, in order of what is load-bearing:

1. Something must write the marker — the reporter touching it when it posts a lead status is
   the obvious writer — **or** the detector is removed. Either is defensible; the present
   state is not.
2. `reporter-state.md`'s two claims are corrected, because they are what taught the
   successor the wrong mechanism.
3. `nudge.py` emitting the age on stdout as well as to `nudge.log` is a genuine but **minor**
   improvement, and was withdrawn as the fix once the log was read. It was never the defect.

**What the two wrong versions of this section were.** First: *"`nudge.py` computes staleness
and emits only its verdict, so the only path to the figure is hand recomputation."* False —
`log_nudge` writes it. Second, the half against the lead's dispatch: *"read the value rather
than recompute it is unactionable unless the value is readable."* The value **was** readable.
The dispatch was fine; what was wrong was ruling a code change on a description of a script
rather than on the script. Both versions were the lead restating a member's account of an
artifact instead of opening it — which is the same error the section documents, committed
twice while documenting it.

## The one repaired clause the pilot caught working

P6 is also the pilot's first positive result, and it is worth separating from the gaps.

The reporter could not land its own fix: its charter forbids repo writes and names the route
a discovered procedure takes instead. It **asked rather than wrote** — the amendment that
added that clause was tested by a case it had not anticipated, and held. Every other finding
above is a file failing to say something. This is a file saying something that worked.

## Deferred during the pilot, deliberately

The hygiene monitor runs from the handover copy because no skill exists for it. The watcher
proposed filing one; correct on the merits, **deferred** — filing infrastructure mid-pilot
grows the thing being measured. File after the pilot closes.

## The contrast — not a finding against any file, and still the most useful result

The watcher and the reporter were spawned by an **identical procedure**, from charters of
the same shape, in the same minute.

The watcher claimed a working mechanism three times without one, then misdiagnosed its own
retries as a tool failure. The reporter reported its initialisation **incomplete**, filed a
charter gap unprompted, armed from the skill path, proved liveness on first request, and
later diagnosed its own arithmetic error correctly and then found the tooling gap beneath
it.

**The spawn procedure is therefore not the variable, and no change to it would have
prevented P1.** What caught P1, P1b, P2 and P5 was the lead checking claims with `ps`,
`kill -0` and `git worktree list` instead of filing them. That is a finding about
supervision, not about documents, and it is the one result here that no role file can
absorb.

## Provenance

Collected by the lead during the pilot; each finding attributed above to the member that
found it. Filed 2026-08-29 as task #35.

**P1, P2 and P6 were all corrected after merging, and the corrections are themselves in
scope.** Every one of those errors was mine, every one was a restatement of a member's
report that I had not checked against the artifact, and every one survived a PR. P6 needed
two corrections and a full rewrite: its first version misdescribed the tool, its second
blamed the dispatch, and the actual defect — a marker file with a reader, a documented
writer and no writer — was larger than either.

What caught all four was reading state rather than re-reading my own summary: `/proc/<pid>/environ`
for the poller, `SKILL.md` for the token contract, `nudge.log` for the staleness figures, and
a repository-wide sweep for the marker's writer. In each case the artifact was one command
away and the report about it was already in my context, which is exactly why the report won.

That is the failure mode P1b names, with the lead as the node: **I diagnosed from a report
instead of from state, four times, while writing the file that documents doing so.** A
findings file whose own author supplied the clearest instances of the class it documents is
the strongest evidence in it, and the reason none of them are edited out. This file records findings only: it closes nothing,
and §15 step 7 remains gated on the maintainer's confirmation.
