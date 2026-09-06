---
id: FD-1013
family: finding
title: the "never end your turn with outstanding background work" rule lives in `.claude/roles/executor.md` and one skill it alone cites; the other five spawned-role charters, including this one, have no version of it
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F75.md
---

# F75 — the "never end your turn with outstanding background work" rule lives in `.claude/roles/executor.md` and one skill it alone cites; the other five spawned-role charters, including this one, have no version of it

Evidence essay for the register row self-named `(F75)` in `docs/findings/register.md`. The
finding: a hard-won operational rule — a backgrounded wait cannot notify a stopped agent
turn, so a spawned role must block in the foreground rather than background-and-end-turn —
is fully stated in exactly one of seven role charters (`executor.md`) and the one skill it
cites (`dev-commands`). The other five spawned roles' charters — `auditor.md` (this one),
`decision-maker.md`, `planner.md`, `reporter.md`, `watcher.md` — carry no version of it, no
pointer to it, and no substitute for it. This session's own auditor stalled on exactly this
pattern while investigating an unrelated finding, confirming the gap is live, not
theoretical.

## Provenance

Scope widened mid-flight by the dispatching lead, who named what it supersedes (the
original single-finding dispatch) — itself the corrected practice this finding is about:
*"if a subagent reports it is waiting on a background run, resume it and tell it the
result"* (`dev-commands`, quoted below), rather than treat the stalled turn as a dead task
and re-dispatch. Findings 1 and 2 were dispatched together but are filed as separate rows;
the reasoning is in "Why two rows, not one" below.

## The rule, quoted in full, `.claude/roles/executor.md` lines 29-42

> **Never end your turn while work you started is still outstanding.** Not "poll" — the
> rule is about your *turn*, because a backgrounded command **cannot notify an agent whose
> turn has ended**. The wait must block your own turn:
> `until ! pgrep -f '<specific pattern>' >/dev/null; do sleep 20; done`, run in the
> foreground. `.claude/skills/dev-commands` carries the loop and the two ways it lies.
> **This applies to everything you start, not only a command you run**: the suite, a
> benchmark, a CI wait, a `Monitor` task, a background poller — **and a subagent you
> delegate to.** Delegation is not an exception; a nested agent's completion notification
> reaches the session still running, never an agent whose turn has ended. Filed as a finding
> against this file (`CLAUDE.md` §15) and superseding an earlier, narrower version of this
> bullet that said "running the full suite: poll, never wait for a notification." That
> wording failed twice more the same day: it named `pytest` when the third stall was a
> *benchmark*, and it said "poll" when the executor did poll — it wrote a poller,
> **backgrounded the poller**, and ended its turn anyway. Three stalls on 2026-08-30 (WK-671
> Tasks 3A ×2 and 3D), each holding finished work.

This is a live rule, not a first draft: it explicitly supersedes an earlier version and
names two ways that earlier version failed before this one was written.

## Where else the rule lives — one skill, cited by exactly one charter

`.claude/skills/dev-commands/SKILL.md` (491 lines) carries a fuller account, lines 241-285:
the same rule, the same foreground `pgrep` loop, the same two ways the loop lies, and a
more complete incident count than either charter states alone — **"Five occurrences on
2026-08-30 across four mechanisms — a backgrounded command, a background poller, a `Monitor`
task, and a delegated subagent"** — plus the dispatcher's own half of the fix, quoted
because it is the practice this session's lead just modelled: *"if a subagent reports it is
waiting on a background run, resume it and tell it the result — do not re-dispatch the
task, which throws away completed work."*

**Checked directly: `.claude/skills/dev-commands` is named in exactly one of the seven
charters** (`grep -in 'dev-commands' .claude/roles/*.md` → one hit, `executor.md:33`). A role
whose own charter is silent on the rule has no pointer to where it lives, either.

## `lead.md` discusses the same incident, but not as a rule for itself

`.claude/roles/lead.md` lines 24-35, read in full — quoted at the load-bearing sentence:
*"On 2026-08-30 one failure mode — ending a turn while a command was still running —
recurred **four times through three different mechanisms** (a backgrounded shell command, a
background poller, a `Monitor` task). The corrected rule landed mid-flight in `6d59963` and
could not reach the agent it was written for; only a direct message could."* This is cited
as the **reason for a different policy** — "Dispatch a fresh agent per task, not one resumed
across a slice" — not as an instruction telling the lead how to manage its own turn.

That asymmetry is not obviously a gap by itself: `lead.md`'s own opening line states *"the
lead is the main thread, not a spawned role"*, and the harness draws the same line
elsewhere — an artifact watch, for instance, is held only by "an interactive or SDK
main-loop session... not a subagent, teammate, background, or print session." If the main
thread is in fact reachable by a background completion in a way a spawned teammate's ended
turn is not, `lead.md` correctly needs a different rule (which it has: dispatch fresh agents
so a charter fix can reach the next one, since it cannot reach a running one) rather than
the executor's rule verbatim. This essay does not independently confirm the notification
mechanics for the main thread; it reports what `lead.md` itself claims and does not extend
the "propagation gap" framing to `lead.md` on the strength of a keyword match alone — the
mistake this same session filed F26 over once already (matching a label without opening
what it names).

## The keyword sweep — two patterns, not one measurement twice; the zero survives three counting methods

**Corrected 2026-09-02.** This section first read the count disagreement below as an
unresolved discrepancy, "not investigated further because it is not load-bearing." It is
resolved: two different regexes were in play, not one pattern counted two ways. The
dispatching lead's own task description read "keyword hits ... executor 7, watcher 6,
reporter 2, lead 1, auditor 0, decision-maker 0, planner 0," then introduced a second,
broader pattern one sentence later — `background|wait|notif|turn|sleep|async|long-running|
Monitor` — to independently confirm the three zeros were a real absence rather than a
phrasing difference, not to restate the whole table. Read together, the two sentences invite
treating the second pattern as what produced the "7/6/2/1" figures too; it did not.
Reproduced directly, at `main` = `39ee30c`, case-insensitive matching-line counts:

| File | Pattern A: `end your turn\|foreground\|until ! pgrep\|poll` | Pattern B: `background\|wait\|notif\|turn\|sleep\|async\|long-running\|Monitor` |
|---|---|---|
| `executor.md` | 7 | 9 |
| `watcher.md` | 6 | 2 |
| `reporter.md` | 2 | 3 |
| `lead.md` | 1 | 4 |
| `auditor.md` | 0 | 0 |
| `decision-maker.md` | 0 | 0 |
| `planner.md` | 0 | 0 |

Each column reproduces **exactly** under its own pattern — the dispatch's stated figures
under Pattern A, this essay's original figures under Pattern B. Neither side mis-measured.

**The three-way zero survives a third, independent counting method too.**
Occurrence-counting rather than matching-line-counting (`grep -o ... | wc -l`) under Pattern
A: `executor.md` 10, `watcher.md` 7, `reporter.md` 2, `lead.md` 1, and
`auditor.md`/`decision-maker.md`/`planner.md` **0, 0, 0** — unchanged. Three counting methods
(two patterns by matching line, one pattern by occurrence), one result for the three
charters this finding turns on: **no version of the rule, under any measurement tried.**
That is a materially stronger claim than "the raw counts disagree but the zeros happen to
agree" — the zero does not depend on which of three ways of counting is used; only the
non-zero charters' exact figures do, because they are measuring different word sets.

**What holds regardless of pattern or counting method**: what matters is which hits are the
rule, not how many keywords a file contains, and every non-zero hit was read directly rather
than trusted as a count, under both patterns. `reporter.md`'s hits are `Monitor` used as the
harness tool's proper noun (arming its own status-cycle Monitor) and `Monitors` as an
ordinary verb describing what `nudge.py` checks — unrelated to turn discipline. `watcher.md`'s
hits are about a different finding (F31's stale-timestamp lie) and about proving a `Monitor`
task is alive, not about ending a turn while one runs. **None of the six non-executor
charters contains the rule** — confirmed by reading every matched line under both patterns,
not by any one count.

## Subagent delegation — mentioned in exactly one charter, available to every role

`grep -inE 'subagent|delegat|Agent tool|\bAgent\(' .claude/roles/*.md` returns two lines,
both in `executor.md` (lines 5 and 35-36: the `subagent-driven-development` mandatory skill,
and "a subagent you delegate to"). No other charter uses either literal word — **this is
narrower than "no other charter deals with delegation"**: `lead.md`'s own "Dispatch a fresh
agent per task" bullet is entirely about delegation mechanics, just in the vocabulary
"agent"/"dispatch" rather than "subagent"/"delegat". The literal-keyword claim is verified;
it should not be read as "five other charters are unaware delegation happens."

That the Agent tool itself is available to a role not naming it is not inferred from the
charters — it is directly confirmed for this one: this very session, spawned from
`auditor.md`, which mentions neither "subagent" nor "Agent tool" nor "dev-commands", used
the Agent tool to dispatch a `gate-runner` subagent while investigating this finding. Not
independently checked for the other four silent charters (`decision-maker`, `planner`,
`reporter`, `watcher`) — reported as a reasonable inference from the uniform team-role
spawning mechanism, not as confirmed per-role tool access.

## The generic tool documentation does not carve out the exception either

Read directly from this session's own available-tools text (not a charter, not a skill —
the harness-level Bash tool description every role receives identically): *"If waiting for
a background task you started with `run_in_background`, you will be notified when it
completes — do not poll."* Taken at face value by a role with no charter-level correction,
this reads as licence to background-and-end-turn — exactly backwards for a spawned role,
per `dev-commands`' own finding above. The exception is not stated at the tool-documentation
layer at all; it exists only where a charter or a skill states it, and today that is one
charter and one skill.

## The live instance — this session, this role, this finding

Investigating Finding 1 (F74) in this same dispatch, this auditor session dispatched a
`gate-runner` subagent via the Agent tool, then called `ScheduleWakeup` — a tool whose own
description scopes it to `/loop` dynamic-mode pacing, not to waiting on a subagent from a
spawned teammate role — and ended its turn expecting the scheduled wakeup to resume it. It
did not: the dispatching lead had to send a direct message to resume this session, quoting
`.claude/roles/executor.md`'s rule as the reason and naming the mechanism precisely
("a backgrounded command cannot notify an agent whose turn has ended, so no wakeup was
coming"). `auditor.md` contains nothing that would have told this session to use the
foreground `pgrep` loop instead — confirmed above, zero keyword hits, no citation to
`dev-commands`. Had the rule been in `auditor.md` the way it is in `executor.md`, this
specific stall would not have happened; this is not a hypothetical exposure, it is what
just occurred while gathering evidence for a different finding in the same session.

## Why two rows, not one

Findings 1 (F74) and 2 (this row) were dispatched together, and one register row bundling
several findings has precedent here (F28, the RFC-840/841 pilot's fourteen sub-findings).
That precedent does not extend to this pair. F28's bundle is one coherent review's own
numbered output, filed as one row *because* enumerating fourteen near-identical process
findings as fourteen top-level rows would itself be unreadable. F74 and F75 share no
mechanism: F74 is a charter's own content going stale against code it describes (documented
here, in one file, about one mechanism); F75 is an operational lesson learned in one charter
never propagated to five siblings that face the identical hazard. Different artifacts
(`reporter.md`'s Mechanism section vs. six charters' turn-discipline coverage), different
remedies (point `reporter.md` at a skill vs. add or point five other charters at
`executor.md`'s bullet or `dev-commands`), different evidence paths (`nudge.py`/`nudge.log`
vs. a charter-wide keyword and content sweep). Filing them as one row would key that row to
no single artifact, which is the shape the register's own header warns against ("keyed by
the requirement or artifact id it concerns"). **Within F75 itself, the five affected
charters are one row, not five** — the opposite question, and the opposite answer: they
share one mechanism (the same lesson, absent from all five for the same reason), so five
rows would invite fixing named exemplars rather than the class, which is exactly what the
register's own established practice (report the class and the count, not the exemplars)
warns against.

## RFC-937 §1.6 — charter ownership, read directly

Same standard as F74, not re-derived: `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` §1.6,
"Reference — charters" row (status `accepted`, raised 2026-09-01 by the maintainer) —
"maintainer; 'a role file that proves insufficient' → `FD-` → maintainer amends" — with
charter-specific enforcement named in the note's own header as a **downstream**, not-yet-
started Work. This role's own charter scopes write access to `docs/`; none of the five
charters this row concerns is under `docs/`, so this row edits none of them regardless of
which reading of §1.6 governs today.

## Scope of this finding

- **Not fix-before-close.** No workstream currently gates on any of the five charters.
- **Not a case for rewriting `executor.md` or `dev-commands`.** Both are correct, current,
  and — per the incident counts above — hard-won; nothing about them is in question.
- **Proposed disposition** (a proposal; the verdict is the lead's): carry forward, unowned.
  The concrete fix is narrow and uniform across the five: add `executor.md`'s turn-
  discipline bullet, or a short pointer to it and to `dev-commands`, to `auditor.md`,
  `decision-maker.md`, `planner.md`, `reporter.md` and `watcher.md`. **Who makes that edit is
  the open question this row records, not decides** — the same disposition question F74
  raises, for the same reason: the lead, under `CLAUDE.md` §12's standing practice, or the
  maintainer, under RFC-937 §1.6.
- **Falsifiable**: discharged when all five charters carry the rule or a pointer to it that
  a fresh spawn would actually read, or by a corrected reading showing one of them already
  does (not found in this review).
