---
id: RFC-928
family: proposal
kind: process
title: An agent's turn ending strands everything it started: one invariant, two directions, six occurrences, two fixes that each named the mechanism instead
status: draft                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-31
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/notes/0018-a-turn-that-ends-strands-what-it-started.md
---

# An agent's turn ending strands everything it started: one invariant, two directions, six occurrences, two fixes that each named the mechanism instead

## 0. What this note is, and what it is not

**A note decides nothing** ([`README.md`](README.md)). This one states an invariant, gives
the evidence for it with citations a reader holding none of this session's context can
check, and lists options in §6 without choosing between them. The real decisions are in §7,
addressed to the decision-maker and the maintainer.

**It does not propose that delegation stop.** `CLAUDE.md` §10 *requires* delegating noisy
investigation, for context cost — a subagent's context is discarded when it returns and the
main thread's is not. Nothing here disturbs that. The failure is in the **waiting**, never
in the delegating, and §5 is the one case where the delegation itself was wrong, for a
reason that has nothing to do with noise.

---

## 1. The invariant

> **A notification from work an agent started reaches a session that is still running. An
> agent whose turn has ended cannot receive it. So anything it started and then waited on is
> stranded.**

That is the whole of it. It is a property of **the turn**, not of the mechanism used to
start the work. A backgrounded shell command, a background poller, a `Monitor` task, a
delegated subagent and a delegated teammate differ in every respect except the one that
matters: each produces a completion signal, and a completion signal has nowhere to land once
the turn that would have received it is over.

This matters because the failure does not announce itself. The work usually **succeeds** —
in all six occurrences below the underlying command, benchmark or agent finished normally.
What is lost is the delivery of the result, and an agent sitting on a finished, correct,
undelivered result looks from the outside exactly like an agent doing long work.

## 2. Two directions — and the second is the worse one

The invariant is symmetric, and only one half of it was noticed while it was happening.

**Direction A — the waiter stalls.** The agent sits waiting for a completion that can never
arrive. **Recoverable**: resume the agent and tell it the result. The cost is elapsed time,
and in the six occurrences below that cost ranged from minutes to fifty minutes. This is the
direction both merged fixes address, and the only one either of them names.

**Direction B — the worker is orphaned.** The delegated agent finishes, reports into a void,
and is never read. **Often unrecoverable**, and it went unnoticed until the second day —
which is itself the finding, because direction B is silent by construction: the party that
would notice is the party whose turn ended.

Two things make B strictly worse than A:

- **The result may not be reproducible.** A stalled waiter can be resumed. An orphaned
  worker's conclusion has to be *re-derived*, and if the work was expensive or the tree has
  moved, re-deriving it is not the same work.
- **The transcript is unreachable.** An agent spawned by a now-dead agent leaves **no
  transcript any surviving session can reach** — its output lives in the dead parent's
  context. So losing a parent destroys **the record of what its children did**, not merely
  the parent's own report. A grandchild's findings, its commands, its dead ends: all of it
  is addressed only through a context that no longer exists. This is why "just resume it"
  is not a general remedy, and why the depth of a delegation tree is a durability property
  and not only a cost property.

The practical shape of B: **an agent that delegates and then ends its turn has not delegated,
it has discarded.** It looks identical to delegation right up until the report does not
arrive, and there is no error, no timeout and no log line marking the difference.

## 3. The evidence

### 3a. Six stall occurrences, one day, five mechanisms

All on **2026-08-30**. Occurrence numbering is the repository's own — `.claude/skills/dev-commands/SKILL.md`
counts "the third stall" and "the fifth stall", and [`docs/closures/INDEX.md#plan-reviewsmd`](RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md)
finding 3e records itself as "the **sixth occurrence today across five mechanisms**".

| # | Mechanism | Who | Where it is recorded |
|---|---|---|---|
| 1 | Backgrounded shell command — `uv run pytest -q`, 2,347 tests past the 10-minute foreground limit | executor, WK-671 Task 3A | `3c50e03` commit message; `.claude/skills/dev-commands/SKILL.md` §"Never end a turn with a command still running" |
| 2 | The same, again, same task | executor | Implied by the repository's own numbering: the same skill section calls the benchmark "the **third** stall", which requires two before it. The commit message for `3c50e03` narrates one |
| 3 | Background **poller** — an agent that *did* poll, then backgrounded the poller | executor, benchmark `scripts/bench-score-batch.py` | `.claude/skills/dev-commands/SKILL.md`, "Corrected 2026-08-30, after this section failed to prevent two further stalls" |
| 4 | A **`Monitor`** task | executor | Named in the four-mechanism list added by `1ccec01` (`.claude/roles/executor.md`, `.claude/skills/dev-commands/SKILL.md`) |
| 5 | A **delegated subagent** — the gate handed to a `gate-runner` | executor | `1ccec01` commit message: "an executor handed the gate to a `gate-runner` subagent and ended its turn to await the result" |
| 6 | A **delegated teammate pair** | **the planner**, writing plan review 10 | `docs/closures/INDEX.md#plan-reviewsmd`, finding 3e — recorded against itself |

Occurrence 6 is the one that breaks the pattern in an instructive way: it was committed by a
**role**, not an executor, on a **plan review**, not a gate run. Its own text says why that
mattered — *"this one is against a role, which is why it did not pattern-match to the same
failure while it was happening."*

**Scope of this count** ([`CLAUDE.md`](../../CLAUDE.md) §13's reference rule): six is the
repository's count of stalls *noticed and recorded* on 2026-08-30 across WK-671 Slice 2's
execution and plan review 10. It is not a count over the whole run, and direction B is by
its nature under-counted — see §8.

### 3b. Three orphaned teammates — direction B

Three delegated teammates finished or stopped with nobody able to read them, idle for
**13–15 hours** before the orphaning was noticed. The maintainer's dispatch names them
`ci-watcher-485`, `ev-w11` and `drift-03`; **those names and durations are session facts and
appear nowhere in the repository** (§8). What *is* in the repository is the consequence of
the third one:

- `ci-watcher-485` — its work was recovered independently.
- `ev-w11` — partly recovered.
- `drift-03` — **not recovered.** Its `03` §5.2 signature-drift result was never obtained.
  Plan review 10 records exactly this hole, from the other side and without naming the agent:
  *"The signature axis — `03` §5.2 shapes with no implementation, and implemented shapes `03`
  does not declare — remains unrun. It was delegated and the delegation did not return."*
  It is carried as that review's **proposal 4.2** (*"run the §5.2 direction before WK-672 opens,
  since WK-672 builds against those shapes"*) — an open proposal in a merged plan review
  **because** the delegation never returned.

That is the cleanest available measurement of direction B's cost: a delegated result that
did not come back is now a plan-review proposal blocking nothing but owed before WK-672, and
the work must be done again from scratch.

### 3c. Two fixes, both merged, both too narrow

**`3c50e03` — "docs(skills): backgrounding the full suite strands a subagent that waits for
a notification" (#464), 2026-08-30 13:24 +0100.** Added a bullet to `.claude/roles/executor.md`
and a section to `.claude/skills/dev-commands/SKILL.md`. Two defects in the wording, both
falsified the same day:

- It **scoped the rule to `pytest`** — *"Running the full suite: poll, never wait for a
  notification"*. The next stall was a **benchmark**. The superseding text says so directly:
  *"An executor reading a `pytest`-specific rule has no reason to apply it to a benchmark."*
- It said **"poll"**. The next agent **did** poll — it wrote a poller, **backgrounded the
  poller**, and ended its turn anyway. *"A backgrounded waiter is the same bug wearing the
  waiter's clothes."*

**`1ccec01` — "docs: the stall rule covers delegated work, not only commands" (#500),
2026-08-30 21:08 +0100.** Rescoped the bullet from *"a command you started is still running"*
to *"work you started is still outstanding"*, and named **four** mechanisms: a backgrounded
command, a background poller, a `Monitor` task, and a delegated subagent. Its own commit
message states the right invariant — *"The invariant is the turn, not the mechanism."*

**The fifth mechanism arrived anyway**, roughly an hour later, in plan review 10: a delegated
**teammate**, by a **role** rather than an executor. Two things put it outside the fix's
reach even though the fix had named the invariant correctly in prose:

- the enumeration ended at four, and an enumeration is read as the extent of the rule;
- the rule lives in `.claude/roles/executor.md` — **a planner does not read the executor's
  charter.**

### 3d. The pattern in the fixes is itself the finding

Each fix named **the mechanism observed**, so the next instance wore **a new mechanism**.
`pytest` → benchmark → poller → `Monitor` → subagent → teammate. The remedy chased the
costume five times. `1ccec01` states the invariant in its commit message and then still
encodes a four-item list in the artifact that binds — and the list, not the sentence, is
what the next reader matches against.

This generalises past this defect: **a rule stated as an enumeration of observed instances
is falsified by the next instance, and reads as satisfied while being falsified.** It is the
same shape as the memory-noted trap where an amendment strands its list-mates, and the same
shape as `CLAUDE.md` §13's insistence that a scope be derived rather than recalled.

## 4. One measured cost, stated precisely

Plan review 10 (merged `18831bd`, "docs(audit): plan review 10 and the RFC-895..RFC-898
reconciliation" (#504)), finding **3e**, with **proposal 3.5**. Read it there rather than
here; the two figures worth carrying are:

- the delegated evidence request had a **direct non-delegated route: three seconds of work**;
- **fifty minutes** of waiting produced nothing, and the turn ending is what made the wait
  **unrecoverable rather than merely slow**.

The finding's own framing is the important part and is not "the agents failed": it is that a
cheap direct route existed and was not taken. Its reading of `CLAUDE.md` §10 is the one this
note adopts — **§10 delegates for context cost, not latency**; a three-second command is not
noisy investigation, and delegating it buys nothing while exposing the result to direction B.

## 5. Why the two directions need different remedies

Worth separating, because a single rule addressing both will under-serve one of them:

- **Direction A is a rule about your own turn.** "Do not end your turn while work you started
  is outstanding" fully prevents it, if read. Its failure mode is *reach* — the right rule in
  a file the wrong role does not open.
- **Direction B is a rule about the shape of the delegation.** Ending the turn is not the
  only way to orphan a worker: killing a parent, losing a session, or a parent that itself
  gets stranded orphans everything beneath it. A turn-scoped rule cannot reach that, because
  the party that must act is not the party that ends. Remedies for B are structural — write
  the result somewhere durable, keep the tree shallow, or make the delegation cheap enough to
  abandon.

## 6. Options — none chosen

**A. State the invariant once, in one place every role reads.** Replace the mechanism list
with the sentence in §1 and demote the five mechanisms to *examples*. Cheapest; addresses the
enumeration failure directly. Does not address reach on its own.

**B. Move the rule up from `.claude/roles/executor.md` to the shared layer** — the process
spec's §8 coordination section, or every role file. Addresses reach; costs a
`delivery-process.md` change and a `.core.json` extract update, so it is a bigger commit than
it looks.

**C. Adopt plan review 10's proposal 3.5 as a dispatch convention** — a delegated evidence
request names, at dispatch, the direct command answering the same question, and the
dispatcher runs it rather than waiting once the delegation is outstanding and the work is
cheap. Narrow, tested against one real occurrence, and it attacks the delegate-for-latency
error rather than the waiting.

**D. Durable output for delegated work.** Require a delegated result to be written to a file
in the dispatcher's worktree (or committed on a branch) rather than returned only through the
report channel. This is the only option that touches **direction B and the transcript
problem**: a file survives its author's parent. Cost is real — a convention every dispatch
must honour, and an agreed location.

**E. Bound the delegation depth, or the value of what may sit below one level.** A grandchild's
transcript is unreachable through a dead parent, so depth is a durability risk. This could be
as light as a stated preference or as heavy as a rule; nothing here recommends either.

**Not an option: delegate less.** `CLAUDE.md` §10 mandates delegating noisy investigation and
this note does not reopen that.

## 7. Open questions — for the decision-maker, except Q3

1. **Is the invariant stated once, or is the mechanism list kept as well?** A list is easier
   to act on and is exactly what failed twice; the sentence is correct and is easier to read
   past. If both, which one is normative when they disagree? *(Convention — decision-maker.)*
2. **Does direction B get a remedy at all in this round, or is it recorded and left?** Option
   D is the only one that reaches it and is the only one with an ongoing cost per dispatch.
   *(Convention — decision-maker.)*
3. **Does the rule move out of the executor's charter into `docs/process/delivery-process.md`?**
   That amends what `CLAUDE.md` §15 points at and adds a `.core.json` extract row, so it is
   **the maintainer's**, not a role's.
4. **Does plan review 10's proposal 3.5 have an owner, and is this note it?** 3.5's home is
   dispatch discipline; this note's §6C restates it rather than adopting it, deliberately, so
   that the review's own acceptance line is not pre-empted. *(Decision-maker, unless the
   review's acceptance line settles it first — an acceptance line is the maintainer's per
   `CLAUDE.md` §14.)*
5. **Is there a mechanical check?** Nothing here obviously grep-able: the defect is an agent
   ending a turn, which leaves no artifact. Recorded as a question rather than answered no,
   because plan review 10's proposal 3.5 sits in the same family and its own review asked the
   same thing of every mechanical-check proposal it made.

## 8. What did not hold, or could not be checked, against the repository

Recorded because the maintainer asked for it, and because an unverified item that travels
inside a verified list acquires the list's credibility.

- **The three teammate names and their idle durations** — `ci-watcher-485`, `ev-w11`,
  `drift-03`, "idle 13–15 hours" — **appear nowhere in the repository.** `git grep` over
  `docs/` and `.claude/` returns nothing for any of the three. They are session facts. The
  *consequence* attributed to `drift-03` is independently corroborated, from the other side,
  by plan review 10's §4 signature-axis gap and its proposal 4.2 (§3b above). Nothing
  corroborates the other two names or any of the durations. **This session's live agent
  roster contains none of the three**; it does contain `drift-signature`, which may or may
  not be the same worker under a different label — not resolved here.
- **The task attributions for occurrences 3–5** — "Task 3D" for the poller and the `Monitor`
  task, "Task 4D" for the `gate-runner` — **are not in the repository.** Only **Task 3A** is
  named (occurrences 1–2, in `3c50e03` and the skill). The benchmark stall is tied to
  `scripts/bench-score-batch.py`, not to a task number; the `gate-runner` stall carries no
  task number in `1ccec01`. The mechanisms are all confirmed; the task numbers are the
  maintainer's, carried here as attribution rather than as verified fact.
- **Occurrence 2 is corroborated indirectly, not directly.** No artifact narrates a second
  `pytest` stall on Task 3A. The skill calls the benchmark "the third stall", which requires
  two before it, and `3c50e03` narrates one. That is the whole of the evidence for #2.
- Everything else held: both commit SHAs, both commit messages, both diffs, the "fifth
  occurrence today, fourth mechanism" line, plan review 10's finding 3e and proposal 3.5 with
  the three-second and fifty-minute figures verbatim, proposal 4.2, the 2,347-test collection
  count and the 10-minute foreground limit.
- **Direction B is under-counted by construction and this note does not claim otherwise.** An
  orphaned worker is noticed only when somebody happens to look for a report that never came;
  three were found because someone looked. No inference should be drawn from three being the
  number.

## 9. Next step

None taken. This note is filed `open` with §7's five questions unanswered. If any of §6's
options is adopted it lands in a role file, a skill, or `docs/process/delivery-process.md`,
and this note must then say where it went ([`README.md`](README.md)'s `landed` obligation).
It is related to but distinct from [`RFC-843`](RFC-00843-the-lead-is-the-highest-error-node-the-evidence-behind-a-claim-lead-md-now-states-with-none.md):
that note is about a relayed fact losing its qualifier, this one about a report that is never
relayed at all. F45's shared-test-database hazard is why the maintainer's dispatch forbade
running the full suite while writing this note, and no suite run was made.

## 10. The maintainer's original wording

Corrected for grammar and punctuation only — never for wording, structure or meaning.

> An agent's turn ending strands everything it started. This has been the single most
> expensive failure pattern of this run — more costly than any technical defect — and it has
> been mis-diagnosed twice, so the note's job is to name the invariant rather than the
> symptom.
>
> The invariant: a notification from work an agent started reaches a session that is still
> running. An agent whose turn has ended cannot receive it. So anything it started and then
> waited on is stranded.
>
> It has two directions, and only the first was noticed at the time. The waiter stalls: the
> agent sits waiting for a completion that can never arrive — recoverable; resume it and tell
> it the result; cost is elapsed time. The worker is orphaned: the delegated agent finishes,
> reports into a void, and is never read — often unrecoverable, and worse, an agent spawned by
> a now-dead agent leaves no transcript the survivor can reach; its output lives in the dead
> parent's context. This direction went unnoticed until the second day.
>
> The pattern in the fixes is itself the finding: each fix named the mechanism observed, so
> the next instance wore a new mechanism.
>
> Do not propose that delegation stop. `CLAUDE.md` §10 mandates delegating noisy investigation
> for context cost; the failure is in the waiting, not the delegating.
