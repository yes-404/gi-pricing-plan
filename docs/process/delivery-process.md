# Delivery Process — Project → Phase → Work → Slice

Adopted 2026-08-29 from NT-0010 (`.claude/notes/0010-layered-slice-based-workflow.md`),
reconciled and ruled in `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md`
("the rulings record"). This document is the process specification `CLAUDE.md` §12 points
at. It governs how a Claude Code team does the work in this repository — a distinct concept
from `docs/workflows/wf-01…05`, the cross-module *domain* journeys (`CLAUDE.md` §4): one
describes how the team works, the other what the platform does.

## 1. Purpose

This process breaks a body of work into a strict hierarchy (Project → Phase → Work →
Slice), gates every layer with a plan/resolve/decide cycle before work starts, and gates
every completed layer with an audit before it is accepted. Escalation to a human is
automatic when a loop gets stuck. **The one routine human approval checkpoint sits at Work,
Phase and Project close, never at Slice close — see §2.** Everything else is agent-to-agent.

## 2. Human checkpoint

**Ruled 2026-08-29** (the rulings record, Part A1). The human checkpoint sits at **three**
named layers — Work, Phase and Project close — with the maintainer deciding at each,
verbatim: *"close a work stream: maintainer only makes decision on work, phase and project
close but not slice close."* **Slice close is not the maintainer's**: a slice closes on a clean audit and the
lead's merge, exactly as it does today. NT-0010 §9's single checkpoint at Project close only
is rejected, not amended — escalation-on-stuck and acceptance-of-done are different events,
and every layer that currently waits on a human keeps one.

## 3. Roles

One role definition is reused across every layer — the layer only changes what "the plan"
and "drift" mean, not the role's job. Tool scope lives once, in each role's own file, not
duplicated here.

| Role | Responsibility | Tool scope |
|---|---|---|
| **Lead** | Explores project context once at the start. At every layer, reviews plan resolutions and decides replan vs. proceed, including whether an acceptance standard was actually defined. Reviews audit resolutions to decide whether to escalate. Owns kickoff and close-out framing, and — per §5's correction below — adopts/amends/rejects every audit verdict and holds sole merge authority. | See `.claude/roles/lead.md` |
| **Planner** | Writes map plans (breaks a layer into its children) and the leaf-level slice plan. Every plan must include an explicit, testable acceptance standard. | See `.claude/roles/planner.md` |
| **Decision-maker** | Rules decision points and spec-vs-code conflicts before a plan or slice can proceed. | See `.claude/roles/decision-maker.md` |
| **Auditor** | Reviews completed work against its plan, with fresh context (no memory of implementation reasoning). Never fixes anything — only reports and proposes verdicts. | See `.claude/roles/auditor.md` |
| **Executor** | Implements via TDD: write a failing test → implement to pass → verify & refactor. Commits, opens PRs. Only at the slice layer. | See `.claude/roles/executor.md` |
| **Watcher** (support) | Cyclic balance / roster-staleness / hygiene watch; publishes `roster-state.md` each cycle as the single source of team state; signals anomalies to the lead. Report-only. | See `.claude/roles/watcher.md` |
| **Reporter** (support) | Cyclic summaries + critical relay on the single external channel; nudges the lead when the status line goes stale. Reads the watcher's files — never polls agents. | See `.claude/roles/reporter.md` |

## 4. Hierarchy

```
Project
 └─ Phase (repeat, one at a time)
     └─ Work (repeat, one at a time)
         └─ Slice (repeat, one at a time — TDD leaf, no children)
```

One template, applied recursively three times (§5), plus a leaf-level variant at Slice
(§6). **Project** is the whole-repository scope `CLAUDE.md` §1 (Mission) already names
informally — no new artifact, per the rulings record Part C row 3; only the label is new.
**Phase** is `CLAUDE.md` §9's existing phase concept (1a, 1b, 2, …). **Work** is the
existing workstream (W1, W2, … W11, …). **Slice** is the existing per-task/PR unit a
workstream is already sliced into.

> **"Slice" has two scopes in this repository, and only one of them is this one**
> (pilot finding P4). A **process-slice** — the sense used everywhere in this document — is
> **one TDD leaf, one PR, one audit, one gate**, and it is what §7's retry caps and §8's
> no-two-at-once govern. A **plan's `## Slice N` heading** is a *grouping of tasks* in a
> filed plan, and a single one may hold several process-slices: W11's "Slice 1" held five.
> The two differ by a factor of the group's size, so applying §7 or §8 to a plan heading
> silently changes what they bound. **When either word could be meant, say which**
> (`CLAUDE.md` §13's reference rule). Where a plan groups tasks under a `Slice N` heading,
> each task is its own process-slice; the heading is a table of contents, not a unit of
> work.
>
> *Left as a known collision rather than renamed: the plan template's heading and this
> document's unit are both long-established, and renaming either would strand every citation
> of it. The rule is to disambiguate at each use.*

## 5. Per-layer flow (Project / Phase / Work)

1. **Enter** — load context from the parent layer + relevant findings-register entries.
   (Project's "enter" step is a one-time **Explore**: read the whole project + handover
   files. It is not repeated on replan.)
2. **Map plan** — planner breaks this layer into its children, and states the
   **acceptance standard** for the layer as a whole.
3. **Open questions?** — decision-maker resolves every open question before continuing.
4. **Lead: replan or proceed?** — lead checks that the resolution is sound and that an
   acceptance standard was actually defined, not just implied. **Replan** loops back to
   this layer's own map plan (guarded, §7). **Escalate: revise parent map** exits upward
   if the issue isn't fixable at this layer at all (not available at Project — it has no
   parent). **Proceed** continues.
5. **Process children, one at a time** — invoke the next layer's flow for each child,
   strictly sequentially at this level (see §8 for the read-only fan-out carve-out).
6. **Audit** — auditor reviews the completed children against this layer's plan: no
   missing requirements, every gate actually achieved, watching specifically for drift at
   this layer's own level (a Phase audit checks work-level drift, not implementation
   detail — that is the Slice audit's job).
7. **Verdict** — **corrected from NT-0010's original assignment** (rulings record Part C
   row 4 / NT-0011 §3 delta 1): the auditor **proposes** fix / accept / defer; the
   **lead** adopts, amends, or rejects the proposal and merges. The decision-maker rules
   decision points and spec-vs-code conflicts only, not audit verdicts. **Fix** loops back
   to this layer's own map plan (guarded, §7). **Accept** proceeds to close-out. **Defer**
   logs to the global findings register (§9), then proceeds to close-out same as Accept.
8. **Close-out** — Phase and Work return control to the parent's loop (this child is done,
   process the next one). Project instead routes to the human checkpoint (§2).

## 6. Slice layer (TDD cycle)

1. **Slice plan** — scope + acceptance standard (same planner/decision-maker/lead gate
   pattern as §5, including the revise-parent-map escape up to the Work layer).
2. **Write test (red)** — executor writes a failing test directly from the acceptance
   standard.
3. **Implement (green)** — executor writes just enough code to pass.
4. **Verify & refactor** — the full local gate must be green. **Not yet built as a
   blocking hook** — today this is an instruction the executor follows, not an
   enforcement mechanism (rulings record Part C row 5; an implementation gap, not a
   document conflict). Failure loops back to Implement, guarded (§7).
5. **Slice audit** — auditor checks the implementation against the slice plan: no missing
   requirements, all gates met, watching for implementation-level drift from the stated
   acceptance criteria.
6. **Verdict** — same correction as §5 step 7: auditor proposes fix / accept / defer; the
   lead adopts, amends, or rejects. Fix loops to Implement, guarded (§7).
7. **Commit** — small, working commit; PR opened, never self-merged (§3, Lead).
8. **Return to Work layer** — signals this slice is complete.

## 7. Escalation guards — instrumented defaults, not fixed governance

| Layer | Retry cap before escalation | Status |
|---|---|---|
| Project | ≤ 1 | Instrumented default (Part B3) |
| Phase | ≤ 1 | Instrumented default (Part B3) |
| Work | ≤ 1 | Instrumented default (Part B3) |
| Slice | ≤ 2 | Instrumented default (Part B3) — **not a settled ceiling**: W10-3A's own history sits exactly on it (two re-audits before merging clean) |

Adopted **as instrumented defaults**, not permanent governance (rulings record Part B3):
log every replan/audit-fix loop iteration and every per-slice re-audit count and gate
re-run from the first slice run under this process (the pilot — W11's first slice);
revisit the numbers once a workstream's worth of data exists, not before. On breach, the
loop pauses and notifies a human instead of retrying again; the redirect goes back into
that layer's own map plan (or Implement, at Slice level) — it does not require the whole
project to stop.

## 8. Parallelism

Sequential processing of a layer's **children** (Project→Phase→Work→Slice: no two Slices
run at once, at any layer) — the same bound on context/resource usage per session
NT-0010 §7 intended. **With a carve-out** (rulings record Part B1): unrestricted
read-only fan-out for **evidence gathering** within a layer is not forbidden by this rule
— `dispatching-parallel-agents` (`.claude/skills/README.md`) is an installed, named
precedent skill for exactly this shape ("2+ independent tasks... without shared state or
sequential dependencies"), and `CLAUDE.md`'s own memory-cost instruction ("delegate noisy
investigation to a subagent") is the same standing rule. What stays forbidden is two
*children* of the same layer running at once — not a bounded, read-only sweep inside one.

**This rule governs parallelism between a layer's children. It says nothing about two
*roles* independently verifying the same artifact, and that gap has a cost** (pilot finding
P14). An executor and an auditor each, correctly, ran the full test suite on the same PR
because neither knew the other was; two suites at once drove load average past 11 and both
read as stalled agents for twenty minutes. **The symptom of contention is slowness, which is
indistinguishable from a hang** — `CLAUDE.md` §11 already names this for command timings.

So: **announce an expensive verification to the team when you start it, and check for one
already in flight before starting.** The announcement is the load-bearing half. A rule that
says only "check whether one is already running" is unactionable when nothing publishes what
is running — **coordination state must be visible, not relayed pairwise**, or it reaches
exactly the members whoever holds it happened to think of. *(Recorded because the first
statement of this fix was exactly that unactionable form, and the finding recurred twice
inside an hour before the announcement half was added.)*

**And prefer the check that already exists**: for a pushed branch, CI is the authoritative
full gate and runs on clean hardware. A reviewer re-running the suite locally buys nothing CI
does not buy better, and risks the borrowed-environment traps `dev-commands` documents.

## 9. Global findings register

Adopted as-is (rulings record Part C row 8) — this **is** `docs/audit/register.md`,
verbatim-matching per the rulings record's own verification, including the literal "fix
before close" decision-taxonomy wording. No new file. One row per open finding, keyed by
the requirement or artifact id it concerns, naming the carrying work item, the phase, and
the decision (fix before close / accept with instrument / carry forward with a named
owner or trigger). Resolution is durable and artifact-linked: appended as a dated note
citing the merging PR, never rewritten. Every map-plan and slice-plan stage reads the
rows relevant to it before finalizing (§11 obligation 7).

## 10. Required artifacts

- **Process spec** (this document) and **agent settings**
  (`docs/process/agent-settings.md`), kept distinct from `docs/workflows/` (domain vs.
  process, §4's own cross-reference above prevents conflating the two).
- The **roadmap** (`docs/roadmap.md`): project-level acceptance standard + phase
  breakdown + open questions — existing, unchanged.
- A work breakdown per phase, a slice breakdown per work item, and a plan per slice
  (`docs/plans/`) — existing, unchanged, following the frozen/dated-revision convention
  already in force.
- The central **open-questions log** (`docs/open-questions.md`) — existing, unchanged.
- The **global findings register** (§9), with per-work closure records alongside it per
  current audit practice — existing, unchanged.
- **Role definitions**: `.claude/roles/*.md` (Task 3 of the adoption plan), **not**
  `.claude/agents/` — that directory is reserved for the delegable specialists
  catalogued in `.claude/agents/README.md`, a different concept (rulings record Part
  B11).
- Runtime/ops state (roster state, balance log, reporter state) stays in the
  handover/ops area outside this repository — operational state, not a plan artifact.

## 11. Plan file obligations

See `.claude/skills/writing-plans/SKILL.md` and `docs/plans/README.md` — those
conventions are stronger than anything this document would add, per NT-0010 §11's own
words. Not restated here; one source, not two.

## 12. Audit record obligations

See `.claude/skills/close-workstream/SKILL.md`, `.claude/skills/phase-review/SKILL.md`,
and `docs/audit/checklists/`. Same reasoning as §11.

## 13. Monitoring & comms loop (watcher / reporter / lead)

**The mechanical scripts described here are not built by this plan** — see the adoption
plan's Task 6. This section describes the mechanism `.claude/roles/watcher.md` and
`.claude/roles/reporter.md` implement once it exists.

- **Events over polling.** Git/CI hooks (PR opened, merge landed) and the balance poller
  fire immediately; a periodic cycle remains only as a liveness heartbeat. Critical
  relays never wait for a cycle boundary.
- **Watcher (mechanical):** threshold compares, mtime staleness checks, roster diff,
  hygiene checks — deterministic, no LLM. Publishes `roster-state.md` (the single source
  of team state) and computes a rolling mechanical ETA from per-slice durations. Re-arms
  one-shot triggers on confirmed recovery. Spawns the watcher agent only when an anomaly
  needs judgment or a written signal.
- **Reporter (mechanical first):** routine summaries template-filled from the state
  files; the reporter agent is invoked only for critical relays and the stale-lead
  nudge. Watch-the-watcher: also flags when `roster-state.md` itself is stale.
- **Derived status line:** mechanical facts (open PRs, last merge, slices done vs.
  planned, mechanical ETA) computed each cycle; the lead adds only interpretation and
  ETA judgment. Facts cannot go stale — only judgment can — so the nudge stays rare and
  meaningful.
- **Escalation ladder:** status line >20 min stale → nudge the lead; unanswered for
  further minutes → the reporter escalates to the user channel as a critical relay, and
  the watcher's roster watch treats a stale lead like any dead member.
- **Interrupt classes for the lead:** critical (balance crossing, dead member, blocked
  slice) interrupts immediately; everything else queues to the lead's next natural
  touchpoint (a verdict or merge moment).
- **Lead entrances, unchanged:** audit structural gap or executor disagreement →
  **replan trigger** → planner files a new dated revision; code-vs-spec conflict →
  **decision-maker** rules before either side is silently changed; balance begin-close
  threshold → **close sequence**: file the record, present it — closure acceptance is
  the user's alone.

Runtime state files (`roster-state.md`, balance log, reporter state) live in the
handover/ops directory outside this repository, not in `docs/` — operational state, not
plan artifacts.

## 14. Adoption workflow

This document, the rulings record, and the adoption implementation plan are steps 1–3 of
NT-0010 §15's own adoption workflow (freeze → reconcile → plan → implement → audit →
pilot → close and supersede), **complete: accepted by the maintainer 2026-08-29, and this
document is authoritative from that date.** The two proposal notes carry dated `superseded`
status and are kept as the proposal record. See `docs/plans/2026-08-29-nt-0010-0011-
reconciliation-rulings.md` Part B4 (adopted as written) and `docs/plans/2026-08-29-nt-
0010-0011-adoption.md` for the record of each step.

## 15. Correction and message discipline

Failures that put wrong content into filed artifacts on 2026-08-29, enumerated below rather
than counted — this line said "three" while listing four, because a bullet was appended and
the number was not. **None was caught by a check; each was caught by someone declining to
accept something.**

- **Name which claim is wrong, in the first sentence.** A hedged correction — "both readings
  are valid", "that may also be right" — preserves the error: the wrong claim stays standing
  in a filed document, and the hedge grows a sentence explaining a discrepancy that does not
  exist. State which side is wrong and supply exact replacement text, not a description of
  the change.
- **Dispatch and report cross, and neither is ordered.** A message and the thing it describes
  travel independently. A correction routinely arrives after the artifact it corrects is
  published; a report of "not landed yet" is routinely written before a merge it could not
  have seen. Before acting on a premise someone sent you, check it is still live. When
  sending, name the tree or SHA your claim is about — a status claim with no named tree is
  unverifiable the moment it is sent.
- **Verify against the primary source; never implement against a relay.** A fact arriving
  from whoever reads everything and derives nothing reads as already-checked, so it gets
  *less* scrutiny rather than more. `lead.md` already requires the sending half of this —
  the lead states this explicitly in every dispatch — and the half no charter states yet is
  the receiving one: a member holding a supplied premise it doubts says so instead of
  implementing it. On 2026-08-29 this was the only mechanism that caught anything: a
  quotation from a paragraph superseded twelve minutes earlier, a clause contradicting a
  ruling its sender had filed hours before, and a role-file draft that put a file in the
  auditor's Tools line minutes after that same file had been assigned to the planner in the
  same conversation — caught by running `git log` against the file itself and finding every
  commit on it was already a plan review, not by remembering the earlier assignment.
- **A gate or check result names its corpus — the command, the totals, and the tree**
  (pilot finding P11). Two roles independently reported a PR's gate "clean" while its CI was
  failing on a named invariant. Neither lied: one had run its own new test file (7/7), the
  other had run four checks and one test file and re-run a real failure until it went green
  in a borrowed environment. **"Clean" reported from whatever was run is unfalsifiable** —
  `7/7` and `2234 passed` are distinguishable at a glance once both are written down, and
  indistinguishable when only the word *clean* is reported. This is `CLAUDE.md` §13's
  reference rule applied to a test count instead of a citation, and §11 already warns that a
  Python-only "gate" has been green here while the frontend was red. **A subset is a subset;
  say which one you ran.**
- **Messages are 50 words or fewer** (maintainer rule, 2026-08-29). A dispatch states the
  instruction and cites its artifact by path, PR number or task id; it does not carry the
  reasoning. Reasoning belongs in a task, a plan, a ruling record or a merged artifact —
  somewhere that outlives an inbox. **If a message cannot be said in 50 words, what it is
  trying to say needs a durable home first, and the message becomes a pointer to it.**
  Applies to every role including the lead.
