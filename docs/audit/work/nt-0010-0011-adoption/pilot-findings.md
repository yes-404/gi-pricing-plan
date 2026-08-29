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
was true: pid 514021, running `balance_watch.py` from the skill path, token read from the
durable source.

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

The watcher first armed against the **ephemeral job-dir token path**, hours after the skill
was filed to end exactly that. The pointer existed; the **precedence** did not.

**Fix:** the skill is authoritative; the handover carries runtime state only; where they
disagree, the skill wins.

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

## P6 — a mechanism that computes a value and emits only its verdict forces recomputation

Found by the pilot-reporter, about its own tooling, after making the error itself.

**Sequence.** Its nudge read *"stale 59 minutes (last: 11:46Z)"*; at 14:45Z that is 179
minutes. Asked to check its arithmetic or its marker, it verified the marker correct and
attributed the error to itself — it had computed the figure by hand. Told to read the
script's output into the message and never recompute, it came back with the reason it could
not: **`nudge.py` computes staleness and emits only `NUDGE_NEEDED`**. The age it had
computed is discarded.

**Two findings, not one.**

- **Against the tool.** The only path to a staleness figure in a message is hand
  recomputation — so the mechanism *builds in* the defect `NT-0013` names, rather than
  merely failing to prevent it. A component that computes a value its consumer needs and
  emits only its own verdict guarantees the consumer will recompute.
- **Against the dispatch — mine.** "Read the value rather than recompute it" is
  unactionable unless the value is readable. An unactionable instruction resolves to either
  non-compliance or fabrication, and the instruction's author is the last person positioned
  to notice which. Before requiring that a value be read, check that something emits it.

**Ruled:** `nudge.py` emits the computed age; the reporter reads it. This is a defect fix in
a tool the pilot is using, not new instrumentation, so it falls outside the deferral below.

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
found it. Filed 2026-08-29 as task #35. This file records findings only: it closes nothing,
and §15 step 7 remains gated on the maintainer's confirmation.
