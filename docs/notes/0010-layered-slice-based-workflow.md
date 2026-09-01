# NT-0010 — A layered slice-based workflow: Project → Phase → Work → Slice, gated at every layer

| | |
|---|---|
| **Raised** | 2026-08-29, maintainer — supplied `workflow-design-proposal.md` (marked "Finalized for implementation") with the instruction to convert it into a working note |
| **Status** | **`superseded` 2026-08-29 — by the adopted specification, `docs/process/delivery-process.md`, which is authoritative from this date.** Accepted by the maintainer 2026-08-29 on the lead's presentation of the adoption record and pilot findings, per this note's own §15 step 7. This document is now the **proposal record** it was adopted from: it is kept, not deleted, because the adopted specification does not carry the reasoning that produced it. Where the two disagree, `docs/process/delivery-process.md` wins. *(Previously `landed` 2026-08-29 — ruled in `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md`; the landing locations are in `docs/notes/README.md`'s index row.)* |
| **Deliverable** | Process documentation and role definitions only: a new process specification, a `CLAUDE.md` pointer, agent role files, and ops automation. **No change to `docs/specs/` and no product code** — nothing in the pricing platform moves |
| **Owner** | Maintainer accepts and rules the six conflicts · Claude drafts the reconciliation, the plan and the slices |
| **Lands in** | Proposed by the author: `docs/process/workflow.md`; also `CLAUDE.md` (a pointer, and amendments to §12/§13/§14), `.claude/agents/` (role definitions and its README's dividing line), `docs/README.md` (suite index), `docs/audit/checklists/` |
| **Trigger** | Before the next workstream's plan is frozen. Adopting mid-workstream would leave one workstream half-governed by each standard |
| **Companion** | [`NT-0011`](0011-per-agent-model-and-skill-settings.md) — the per-agent model, effort and skill settings this workflow implies |

---

## Request, refined

The maintainer wants the project's development process written down as a specification
rather than carried in a local handover file. The proposal defines one role set reused at
four layers — **Project → Phase → Work → Slice** — where each layer runs the same shape:
plan, resolve open questions, lead decides replan-or-proceed, process children strictly one
at a time, audit, decide fix/accept/defer, close out. The Slice layer is the leaf and runs a
TDD cycle. Loops are capped and escalate to a human on breach. There is one human approval
in the whole system, at Project close. A findings register spans all layers. A monitoring
and comms loop runs beside the workflow, mechanical-first, and never acts as a gate.

The proposal explicitly defers naming and placement to this project's documentation
standard, states which artifacts must exist rather than how they are named, and carries its
own adoption procedure (§15) which runs the adoption as a work item through a lightweight
version of the process it defines, ending in a pilot.

## What is already in force (verified at `74b1b10`)

The proposal is written against this repository and most of its machinery is real. Verified
rather than assumed:

- **The register skeleton in §8 matches the file.** `docs/audit/register.md`'s header, its
  five columns and its decision forms — fix before close, accept with an instrument, carry
  forward with an owner, carry forward with a trigger unowned by design, phase-boundary
  carry — are reproduced accurately, including the dated-note resolution convention and the
  discharges section. §8's claim to adopt current practice as-is is true.
- **The six skills the proposal binds are project skills, not plugins.** `writing-plans`,
  `subagent-driven-development`, `executing-plans`, `test-driven-development`,
  `using-git-worktrees` and `requesting-code-review` all exist under `.claude/skills/`.
  `.claude/skills/README.md` records fourteen vendored from `obra/superpowers`. The
  proposal's open item on this resolves in its favour.
- **Frozen dated plans, PR-only members, lead-only merges, the re-audit rule and the
  worktree-collision rule** are all current practice, and the last two were each bought with
  a real incident.
- **The monitoring loop is already mechanical-first in part.** The balance poller and the
  reporter cycle run as scripts under persistent monitors; what §14 adds is removing the LLM
  wrapper from the steady state, not inventing the scripts.

Three of the proposal's premises are **not** in force, and each is load-bearing:

- **`docs/process/` does not exist.** The suite index at `docs/README.md` lists `specs/`,
  `workflows/`, `contracts/` and `adr/`. A process area is a new top-level category and the
  index is part of the contract.
- **No role definitions exist.** `.claude/agents/` holds seven delegable specialists
  *(corrected 2026-08-29 — a directory listing that included its own `README.md` read as
  eight; `.claude/agents/README.md:184` already states "all seven"; see
  `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md` Part B8)* —
  none of them a lead, planner, decision-maker, auditor or executor. The proposal's
  companion says existing role files are "amended at adoption, not recreated"; there are
  none to amend. Today's roles live in a handover file outside the repository and in
  spawn-time briefs that die with the session.
- **The retry caps have never been measured.** Nothing records how many replan or audit-fix
  loops a layer has actually needed.

## Claude's assessment (kept separate from the maintainer's words)

**The proposal's central claim is right, and the strongest argument for it is one it does
not make.** This repository's process is genuinely good — the four verdicts, the
spec-derived scope rule, the durability rule, the per-slice audit — and *none of it is
specified*. It lives in `CLAUDE.md` prose, in a local handover file, and in spawn-time
briefs. That is exactly the failure [`NT-0005`](0005-deferred-items-with-no-durable-custody.md)
recorded for deferred items — no durable custody — applied one level up, to the process
itself. Writing the process down as a versioned artifact is worth doing on that ground
alone, independent of whether the four-layer shape is the right one.

Six items need a ruling. The first three are conflicts with standards currently in force;
the rest are corrections.

### 1. The single human checkpoint contradicts the standing closure rule

§9 puts **exactly one** human approval in the system, at Project close. Every other layer's
accept or defer returns control to its parent automatically.

The rule in force is the opposite: **closure acceptance is the maintainer's at every
workstream close.** `CLAUDE.md` §14's first rule requires "an explicit maintainer acceptance
line with a date" for a plan review, and the standing team rule — enforced through W6b, W9
and W10 — is that the team files the record and presents it, and never declares a workstream
closed. W10 closed on the maintainer's word of 2026-08-28, not on the auditor's verdict.

This is not a detail. Under §9, a Work layer's audit-decision would close a workstream
without the maintainer seeing it. **Recommendation: reject §9 as written.** Keep the human
checkpoint at Work close, and let Phase and Project close inherit it. The proposal's
underlying intent — that escalation interrupts and close approvals are different things,
and routine layer transitions should not page a human — survives intact; it is the *layer*
the checkpoint sits at that is wrong.

### 2. Agents that decide contradict `.claude/agents/README.md` and `CLAUDE.md` §12

`.claude/agents/README.md` states the dividing line for that directory in four words:
*"Every agent here gathers or verifies. **None of them decides.**"* `CLAUDE.md` §12 says the
same from the other side — the verdict stays in the main thread, naming §13's four verdicts,
§14's proposals, the code-versus-spec decision, slice design, **and every edit to `docs/`**.

The proposal puts role definitions for a **decision-maker** into `.claude/agents/`, whose
entire job is to decide, and gives the **planner** write access to `docs/`. Both collide
with the rule as written.

The collision is already real, not hypothetical: during W10 the auditor filed spec changes
as PRs #308 and #309, and the decision-maker ruled DP1–DP7. Practice has diverged from
`CLAUDE.md` §12 and nobody recorded it. Under §0 — *when code and spec disagree, stop and
resolve it* — this must be ruled, not quietly formalised by adoption. **Recommendation:
amend `CLAUDE.md` §12 and the agents README explicitly**, narrowing "none of them decides"
to the *delegable specialist* agents it was written for and stating the separate rule for
*role* agents: a role agent may decide within its own charter and may write to `docs/`, and
the four verdicts and the merge remain the lead's. An amendment that names what changed is
the point; silently adopting a proposal that contradicts the rule is the failure mode.

### 3. "No parallelism at any layer" must not be read as forbidding delegation

§7 removes parallelism everywhere, to bound context and resource usage per session. That is
sound for *child processing* — one slice at a time is current practice.

But `CLAUDE.md` §10 requires the opposite on a different axis: **delegate noisy
investigation to a subagent**, because a subagent's context is discarded and the main
thread's is not, and 73% of measured spend came from calls carrying over 200k tokens. That
is the standing maintainer rule of 2026-08-25. Read carelessly, §7 forbids the very thing
§10 mandates. **Recommendation: adopt §7 with an explicit carve-out** — sequential child
processing, unrestricted read-only fan-out for evidence gathering.

### 4. "ultracode" is a real and different thing — the companion's assumption is wrong

[`NT-0011`](0011-per-agent-model-and-skill-settings.md) assumes "ultracode" means
**ultrathink**, and flags it for confirmation. In Claude Code, `ultracode` is a distinct
keyword: it opts a session into **multi-agent workflow orchestration**, and `ultra` is the
level that launches a multi-agent cloud code review. Neither is the extended-thinking
trigger.

The distinction matters for the decision-maker specifically. If "ultracode" meant
orchestration, the instruction was to *fan the decision-maker out*, which §7 forbids and
which no decision point in W10 needed. If it meant maximum thinking on every ruling, that
is a cheap and defensible setting. **Recommendation: rule it as maximum extended thinking**,
and record the correction so the word is not re-read as orchestration later.

### 5. The retry caps are guesses, and one of them is exactly at the observed maximum

§6 sets ≤1 retry at Project, Phase and Work, and ≤2 at Slice. Against the only data the
project has — W10 — the slice cap sits precisely on the observed maximum: W10-3A needed
**two** re-audits before it went clean, W10-2 and W10-3B one each, W10-3C and W10-3D none. A
cap set at the highest value ever observed will escalate the first time a slice is slightly
harder than the hardest one so far. That is fitting to the sample, not choosing a threshold.

**Recommendation: adopt the caps as instrumented defaults, not as governance** — log every
loop iteration from day one, and revisit after a workstream's worth of data. Escalating to a
human is cheap here; the cost of a wrong cap is a spurious page, not lost work. This is the
one place the proposal should be explicitly provisional.

### 6. The adoption procedure is the strongest part, and it should be followed literally

§15 lands the proposals frozen first, reconciles them against every standard in force with
an adopt/amend/reject verdict per item, pre-resolves open questions as dated rulings, plans
one dated implementation, implements slice by slice with automation last, audits the
adoption against the proposal, and **pilots on one small real work item before declaring the
standard**. The pilot is the acceptance test of the design: if the process cannot cleanly
carry a small work item, that is a finding against the process, caught before it governs
anything large.

Adopting these two documents by writing them into `CLAUDE.md` in one pass would be the
`CLAUDE.md` §0 failure — building from a specification nobody reconciled — and would also
breach [`NT-0003`](0003-duplicated-status-goes-stale.md), since a process spec that restates
`CLAUDE.md` §§12–14 rather than superseding them creates a fourth place status can go stale.
**Recommendation: adopt §15 as the adoption plan, and require the reconciliation step to
produce an explicit adopt/amend/reject verdict for every numbered section of both
documents** — including the six items above.

### 7. §2's own lead row disagrees with the companion document's, and neither note flags it

*(Added 2026-08-29, found by the auditor during the §15 step 2b reconciliation — see
[`docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md`](../../docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md)
Part B9 for the ruling.)*

§2's Lead row gives its suggested tool scope as "Read-only (Read, Grep, Glob) + write access
to plan/map files only" — no merge authority anywhere in it. [`NT-0011`](0011-per-agent-model-and-skill-settings.md)'s
own per-agent lead specification gives it "full read; git merge authority; write to
handover/status files only" — merge authority present, plan/map-file write absent. Both
documents describe the same role and disagree with each other, and neither says so.
NT-0011's version matches confirmed current practice (sole merge authority resting with the
lead, plan-file writes belonging to the planner role); this note's §2 row is the one
corrected. **Recommendation: ruled — NT-0011's version is authoritative**, folded into the
same reconciliation pass rather than treated as a second open question.

## What this note does not decide

Nothing. Per `docs/notes/README.md`, a note is raw material. The four-layer hierarchy,
the checkpoint layer, the `CLAUDE.md` §12 amendment and the agents-README amendment each
constrain more than one part of the working standard, so each needs either a maintainer
ruling recorded with a date or, where it is a lasting architectural choice, an ADR. The
placement of `docs/process/` is a documentation-standard question and belongs with the
suite index, not here.

## Acceptance criteria

The proposal is adopted when all of the following hold:

1. Every numbered section of both documents carries an **adopt / amend / reject** verdict
   with a rationale, in a dated reconciliation record.
2. The six items above are ruled, and each ruling that changes a document in force lands as
   an amendment to that document naming what changed — never as a silent overwrite.
3. `docs/README.md`'s suite index lists the process area, and `python3 scripts/audit-docs.py`
   passes with it present.
4. Role definitions exist under `.claude/agents/` for every role the workflow names, each
   carrying the worktree-collision rule if it has git write access, and
   `.claude/agents/README.md` records the amended dividing line.
5. `CLAUDE.md` carries a pointer to the process spec and no second copy of it.
6. One small real work item has been carried end to end under the new process, and its
   findings are in `docs/audit/register.md` with owners.

## Next step

Ask the maintainer to rule items 1–6. Nothing is built before that: item 1 changes who may
close a workstream and item 2 changes what an agent may do, and both are standards currently
in force. If the rulings land, the adoption runs as its own work item under §15, sequenced
so that it does not straddle W11.

## Original wording

Kept verbatim below, corrected for grammar and punctuation only — never for wording,
structure or meaning. Reproduced in full because the source document reached this project as
a loose file outside the repository, and a note citing a path that will not survive is the
custody failure [`NT-0005`](0005-deferred-items-with-no-durable-custody.md) records. The
companion document is reproduced in [`NT-0011`](0011-per-agent-model-and-skill-settings.md).

> # Layered Slice-Based Workflow — Design Proposal
>
> **Status:** Finalized for implementation
> **Audience:** Claude Code, scaffolding this into `CLAUDE.md`, `docs/`, and `.claude/agents/`
> **Suggested destination after adoption:** `docs/process/workflow.md` (beside `docs/process/agents.md`) — a suggestion only; placement and naming remain the project's decision per the documentation standard.
>
> ## 1. Purpose
>
> This document specifies a workflow for solo-maintainer + Claude Code teams that breaks
> a project into a strict hierarchy (Project → Phase → Work → Slice), gates every layer
> with a plan/resolve/decide cycle before work starts, and gates every completed layer
> with an audit before it's accepted. There is exactly one human approval checkpoint in
> the entire system: closing the project. Everything else is agent-to-agent, with
> automatic escalation when something gets stuck.
>
> ## 2. Roles
>
> One role definition is reused across every layer — the layer only changes what "the
> plan" and "drift" mean, not the role's job.
>
> | Role | Responsibility | Suggested tool scope |
> |---|---|---|
> | **Lead** | Explores project context once at the start. At every layer, reviews plan resolutions and decides replan vs. proceed, including whether an acceptance standard was actually defined. Reviews audit resolutions to decide whether to escalate. Owns kickoff and close-out framing. | Read-only (Read, Grep, Glob) + write access to plan/map files only |
> | **Planner** | Writes map plans (breaks a layer into its children) and the leaf-level slice plan. Every plan must include an explicit, testable acceptance standard. | Read + write to `docs/` plan files only |
> | **Decision maker** | Resolves open questions in every plan before it can proceed. After every audit, decides fix / accept / defer. | Read + write to plan "Open Questions" / "Decision" sections and the findings register |
> | **Auditor** | Reviews completed work against its plan, with fresh context (no memory of implementation reasoning). Never fixes anything — only reports. | Read-only + Bash for verification (no edits) |
> | **Executor** | Implements via TDD: write a failing test → implement to pass → verify & refactor. Commits. Only at the slice layer. | Full read/write + Bash, scoped to the current slice |
> | **Watcher** (support) | Cyclic balance / roster-staleness / hygiene watch; publishes `roster-state.md` each cycle as the single source of team state; signals anomalies to the lead. Report-only. | Read-only + state-file publishing; never dispatches, never touches the repo |
> | **Reporter** (support) | Cyclic summaries + critical relay on the single external channel; nudges the lead when the status line goes stale. Reads the watcher's files — never polls agents. | Read state files + comms channel; never edits the repo, never merges or audits |
>
> ## 3. Hierarchy
>
> ```
> Project
>  └─ Phase (repeat, one at a time)
>      └─ Work (repeat, one at a time)
>          └─ Slice (repeat, one at a time — TDD leaf, no children)
> ```
>
> One template, applied recursively three times, plus a leaf-level variant at Slice.
>
> ## 4. Generic per-layer workflow (Project / Phase / Work)
>
> 1. **Enter** — load context from the parent layer + relevant findings register entries. (Project's "enter" step is a one-time **Explore**: read the whole project + handover files. It is not repeated on replan.)
> 2. **Map plan** — planner breaks this layer into its children, and states the **acceptance standard** for the layer as a whole.
> 3. **Open questions?** — decision maker resolves every open question before continuing.
> 4. **Lead: replan or proceed?** — lead checks that the resolution is sound and that an acceptance standard was actually defined, not just implied.
>    - **Replan** → back to this layer's own map plan (guarded, see §6).
>    - **Escalate: revise parent map** → if the issue isn't fixable at this layer at all (the parent's breakdown was wrong), exit upward to the parent's map plan instead of looping here. (Not available at Project — it has no parent.)
>    - **Proceed** → continue.
> 5. **Process children, one at a time** — invoke the next layer's graph for each child, strictly sequentially. No parallelism at any layer (see §10).
> 6. **Audit** — auditor reviews the completed children against this layer's plan:
>    - No missing requirements from the plan.
>    - Every gate defined in the plan was actually achieved.
>    - Watches specifically for **drift at this layer's own level** (e.g. a Phase audit checks for work-level drift from the phase map — not implementation detail, which is the Slice audit's job).
> 7. **Audit decision** — decision maker chooses:
>    - **Fix** → back to this layer's own map plan (guarded, see §6).
>    - **Accept** → proceed to close-out.
>    - **Defer** → log to the global findings register (§8), then proceed to close-out same as Accept.
> 8. **Close-out** — Phase and Work simply **return control to the parent's loop** (signals "this child is done, process the next one"). Project instead routes to the single **human approval to close** (§9).
>
> ## 5. Slice layer (the leaf — TDD cycle, no children)
>
> 1. **Slice plan** — scope + acceptance standard (same planner/decision-maker/lead gate pattern as above, including the revise-parent-map escape up to the Work layer).
> 2. **Write test (red)** — executor writes a failing test directly from the acceptance standard.
> 3. **Implement (green)** — executor writes just enough code to pass.
> 4. **Verify & refactor** — full suite must be green (hooks enforce this, not just an instruction). Failure loops back to Implement, guarded (§6).
> 5. **Slice audit** — auditor checks the implementation against the slice plan: no missing requirements, all gates met, watching for **implementation-level drift** from the stated acceptance criteria.
> 6. **Audit decision** — fix (loops to Implement, guarded) / accept / defer (logs to register).
> 7. **Commit** — small, working commit.
> 8. **Return to Work layer** — signals this slice is complete.
>
> ## 6. Escalation guards
>
> Every replan loop and every audit-fix loop is capped. On breach, the loop pauses and
> notifies a human instead of retrying again; the human's redirect goes back into that
> layer's own map plan (or Implement, at Slice level) — it doesn't require the whole
> project to stop, just that one loop.
>
> | Layer | Retry cap before escalation | Rationale |
> |---|---|---|
> | Project | ≤ 1 | Problems here are rare but expensive — escalate fast. |
> | Phase | ≤ 1 | Same reasoning. |
> | Work | ≤ 1 | Same reasoning. |
> | Slice | ≤ 2 | Retries here are cheap and routine; don't page a human for normal churn. |
>
> ## 7. Parallelism
>
> **Not used at any layer in this version.** Every "process children" loop runs strictly
> one child at a time, at every layer including Slice. This bounds context/resource
> usage per session. This was deliberately chosen over a parallel-fan-out design that
> was considered and rejected — revisit only if resource budget materially changes.
>
> ## 8. Global findings register
>
> One shared log, not scoped to any single layer — **current register practice is
> adopted as-is**; this section states the obligations the workflow depends on:
>
> - **One row per open finding, keyed by the requirement or artifact id it concerns**,
>   naming the carrying work item, the phase, and the decision. Requirement-keying is
>   what lets coverage tooling, specs, and plans cross-reference the register
>   mechanically.
> - **The decision taxonomy carries what a severity field would** (superseding the
>   earlier draft's JSON schema): **fix before close** (blocking); **accept**, with
>   the instrument or rationale recorded (alternative instrument, measured value,
>   declared affordance); **carry forward** — the workflow's "defer" — which must
>   name an owner, or a named trigger with "unowned by design," or an explicit
>   phase-boundary carry whose later-phase owners are named in the roadmap. A carry
>   with none of these is not a valid register entry.
> - **Resolution is durable and artifact-linked:** appended as a dated note citing
>   the merging PR; rows leave the register only when a close resolves, accepts, or
>   re-plans them with an owner.
> - **Writes are checklist-driven** — audit filings and the work-item / phase close
>   checklists, never ad hoc chat (the durability rule applies to the register
>   itself).
> - The register is also the **custody home for recorded discharges** of deferred
>   items that expire or get placed elsewhere.
> - Every map-plan and slice-plan stage reads the rows relevant to it before
>   finalizing (§11, obligation 7), so a finding carried from one slice is visible
>   when any later slice, work, phase, or the project close needs it.
>
> **Reference skeleton (from current practice — file naming per the documentation
> standard):**
>
> ```markdown
> # Global register of open findings
>
> One row per open finding, keyed by the requirement or artifact id it concerns.
> Each row names the work item that carried it, the phase, and the decision. A
> finding is removed when the close resolves it, accepts it, or re-plans it with
> an owner.
>
> | Finding id | Concerns | Work item | Phase | Decision |
> |---|---|---|---|---|
> | <REQ-ID> (F<n>) | <what it concerns, one line> | <work-item id> | <phase> | <see decision forms below> |
>
> Decision forms:
> - fix before close — <the required action>
> - accept — <instrument or rationale: alternative instrument / measured value /
>   declared affordance>
> - carry forward with an owner (<named owner>)
> - carry forward with a trigger (<named trigger>), unowned by design
> - carry forward — phase boundary; owners are the later-phase workstreams named
>   in the roadmap
> - *resolved <date> (PR #<n>) — <what shipped>*   ← appended as a dated note,
>   never a rewrite
>
> A carried finding is written here by the work-item close checklist and by the
> phase close checklist.
>
> ## Discharges, recorded <date>
> - <deferred item discharged rather than filed, with where it was placed —
>   this register is the custody home>
> ```
>
> ## 9. The single human checkpoint
>
> Only the Project layer terminates in a real human approval ("Human approval to close").
> Every other layer's audit-decision outcome (accept/defer) simply returns control to its
> parent's loop. Rejecting the close approval sends it back to the Project audit, not to
> a full remap. Escalation-to-human events (§6) are rare interrupts, not routine gates —
> don't confuse the two: escalation happens because a loop got stuck; the close approval
> happens because the work is claimed done.
>
> ## 10. Required artifacts
>
> **File names, dating conventions, and exact folder placement follow the project's
> existing documentation standard — this proposal defines which artifacts must exist,
> not how they are named.** The only fixed locations are the tool-mandated ones:
> `CLAUDE.md` at the repo root (carrying a pointer to the adopted process spec),
> role definitions under `.claude/agents/` (lead, planner, decision-maker, auditor,
> executor, plus support agents as needed), and the project skills folder holding
> the vendored skill set (writing-plans, subagent-driven-development,
> executing-plans, test-driven-development, using-git-worktrees,
> requesting-code-review) that plans and agent bodies bind by registered name.
>
> Artifacts this workflow requires, wherever the documentation standard places them:
>
> - The adopted **process spec** (this document) and the **agent settings** document,
>   kept distinct from the existing module-workflows documentation (domain workflows
>   vs. development process — a one-line cross-reference in each area prevents
>   exploring agents from conflating the two).
> - The **roadmap**: project-level acceptance standard + phase breakdown + open
>   questions.
> - A **work breakdown per phase**, a **slice breakdown per work item**, and a
>   **plan per slice** (scope + acceptance standard), all following the frozen /
>   dated-revision convention already in force.
> - The **central open-questions log**.
> - The **global findings register** (§8), with per-work closure records alongside it
>   per current audit practice.
> - Runtime/ops state (roster state, balance log, reporter state) stays in the
>   handover/ops area — operational state, not plan artifacts.
>
> ## 11. Plan file obligations (map plans and slice plans)
>
> Plan structure follows the project's `writing-plans` skill (vendored from
> Superpowers into the project skills, invoked by its registered name — no plugin
> namespace) plus the project's own house conventions, which are **stronger than any
> template this proposal could impose** — current plans carry verified findings,
> executable acceptance, and self-review. This section therefore states only the
> content obligations the workflow depends on, not a section layout. A plan must:
>
> 1. **Bind its executor** — a header directive naming the required execution skill
>    (`subagent-driven-development` / `executing-plans`) with checkbox step tracking.
> 2. **Trace upward** — cite its slice-map (or parent-map) row and the governing
>    spec/requirement ids precisely enough that the audit stage can check "vs plan,
>    no missing requirements" mechanically.
> 3. **State scope with explicit exclusions** — what is built, and what is
>    deliberately recorded but not built.
> 4. **Rest on verified findings** — claims about the codebase verified against
>    shipped source at a pinned commit, enumerating the affected class, not sampling
>    it.
> 5. **Operationalize acceptance** — every step carries exact commands and expected
>    results; the acceptance standard is executable, not declarative. Gates named
>    per slice.
> 6. **Carry its constraints** — the standing rules the executor must obey
>    (gate rules, frozen-file rules, worktree hygiene, prose standard), cited to
>    their source.
> 7. **Consider the register** — open findings relevant to this plan are addressed
>    or explicitly recorded as out of scope (and flagged onward, per current
>    Finding-style practice).
> 8. **Self-review before freeze** — spec-coverage mapping, placeholder scan,
>    consistency check, gaps found and fixed inline.
>
> Two corrections to earlier drafts of this proposal, per current practice: open
> questions are **pre-resolved before the plan freezes** — a frozen plan cites
> decided rows (booked in the central open-questions log) and contains no open
> checklist of its own; and lead replan/proceed **decisions do not live in the plan
> file** — they belong to the main thread and dated ruling records, since frozen
> plans are amended only by dated revisions.
>
> **Reference skeleton (from current practice — satisfies obligations 1–8; file
> naming per the documentation standard):**
>
> ````markdown
> # <Work-item / slice id> — <Title> Implementation Plan
>
> > **For agentic workers:** REQUIRED SUB-SKILL: Use the project skill
> > subagent-driven-development (recommended) or executing-plans to implement this
> > plan task-by-task — skills are invoked by the name registered in the project's
> > skills folder. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Goal:** <one paragraph: what this delivers and under which decisions/rules>
>
> **Architecture:** <where the change starts, the source of truth it flows from,
> what stays frozen>
>
> **Tech Stack:** <the stack the executor touches>
>
> **Spec:** <governing requirement ids with file paths + line numbers, in both
> mirrors where mirrored>
>
> **Slice source:** <parent map file + row, quoted verbatim with line numbers>
>
> **Highest ids in use at the anchor (`<sha>`):** <next free ids; state whether
> this plan mints any>
>
> ## Global Constraints
> - <standing rules the executor must obey — gates, frozen-file rules, worktree
>   hygiene, prose standard — each cited to its source>
>
> ## Findings the plan is built on
> Each verified against shipped source at `<sha>` by a full sweep; the findings
> enumerate the affected class, not a sample.
>
> ### Finding 1 — <the class, swept>
> <classification of every member: built here / recorded-not-built / conforms,
> with file:line for each; explicit exclusions recorded and flagged onward>
>
> ## Task 1: <imperative title>
> **Files:**
> - Modify / Create / Regenerate: <paths with line references>
>
> **Interfaces:**
> - Consumes: <requirement/decision rows and prior tasks' outputs>
> - Produces: <the names/artifacts later tasks consume>
>
> - [ ] **Step 1: <imperative>**
> <exact instruction; commands as code with `Expected:` results — acceptance is
> executable, not declarative>
>
> - [ ] **Step n: Commit**
> <the commit message>
>
> ## Self-review
> **1. Spec coverage.** <each governing rule → the tasks that satisfy it>
> **2. Placeholder scan.** <no TBD/TODO; every step carries exact sites and its
> predicted failure cause>
> **3. Consistency.** <names defined once, used identically across tasks>
> **Gaps found in review, fixed inline:** <what the self-review caught>
> ````
>
> ## 12. Audit record obligations
>
> Audit-record structure follows current practice (the work-item record format),
> which is stronger than any template this proposal could impose. The workflow
> depends on these obligations — an audit record must:
>
> 1. **Pin its evidence** — audited against a named commit head, with the full gate
>    **re-run in the audit** at that head and measured results recorded (test
>    counts, lint/type results, drift check, CI state). Never rubber-stamped, never
>    "checks passed."
> 2. **Derive scope from the plan first, then evidence it** — the plan's slice row
>    is the yardstick; the delivered requirement set is listed per delivered part.
> 3. **Record divergences, never silently** — a divergence from the plan is
>    legitimate only when it follows the spec or a dated ruling, and every one is
>    tabled plan-vs-implemented.
> 4. **Verdict per requirement** — an evidence table with coverage-marker counts;
>    **silence is never a verdict.**
> 5. **Judge the judgment calls** — the executor's discretionary choices are
>    evaluated explicitly against the module's established conventions, not waved
>    through.
> 6. **Table findings with decision, status, and register linkage** — each finding
>    closed or carried, with its register row filed or updated in the same record
>    (decisions per the §8 taxonomy).
> 7. **Carry record notes for non-blockers** — so sibling records read complete
>    without extra files (e.g. a gap discovered in an earlier part, closed here).
> 8. **Sign off per the verdict split** — the auditor proposes verdicts (re-audit
>    counts included), the lead adopts/amends/rejects, and the merge SHAs are
>    recorded.
>
> **Reference skeleton (from current practice — satisfies obligations 1–8; file
> naming per the documentation standard):**
>
> ```markdown
> # Work-item record — <id> (<title>)
>
> Audited <date> against origin/main `<sha>` (<PR set; CI state at filing>).
>
> ## Scope
> Derived from <plan file> slice <id> first, then evidenced. <the requirement
> set delivered, listed per delivered part/PR>
>
> Slice gate (plan §<n>): <the gate the plan set for this slice>
>
> ## Divergences from the plan (recorded, not silent)
> | Plan | Spec / ruling (implemented) |
> |---|---|
> | <what the plan drafted> | <what shipped, citing the spec rule or dated ruling that makes the divergence legitimate> |
>
> ## Evidence
> **Requirement coverage (head `<sha>`):** <n/n evidenced; coverage-marker counts>
>
> | Requirement | Verdict |
> |---|---|
> | <REQ-ID> | ✓ delivered and tested — <evidence, incl. named refusals/tests> / deferred — <register row> (silence is never a verdict) |
>
> **Judgment calls judged in audit:** <each discretionary executor choice,
> evaluated against the module's established conventions>
>
> ## Gate
> Measured in audit at head `<sha>`: <lint · types · imports · test counts
> reconciled against --collect-only · docs gate · drift check · CI state on the
> merge>
>
> ## Findings
> | Finding id | Concerns | Decision | Status |
> |---|---|---|---|
> | F-<id> | <one line> | <§8 decision form, dated, PR-cited when resolved> | closed / carried (register row filed / updated) |
>
> **Record notes (non-blockers):** <notes that let sibling records read complete
> without a separate file>
>
> ## Sign-off
> Auditor verdict: <clean / gaps, with re-audit counts per part>. Verdicts
> adopted by the lead; merged <date> as <SHAs>.
> ```
>
> ## 13. Open items for the next iteration
>
> These were identified during design but are explicitly out of scope for this version:
>
> - **"All children done" exit condition** must read from the map file's own checklist
>   state (which children are marked complete), never be inferred from how many loop
>   iterations happened to run.
> - **Escalation guard mechanics** — confirm whether a breach should be a hard pause
>   (session stops and waits) or an async flag Claude Code polls between turns. This
>   document assumes a hard pause but doesn't mandate the implementation.
> - **Parallelism** — deliberately removed everywhere; reconsider only if resource
>   constraints change materially.
>
> ## 14. Monitoring & comms loop (watcher / reporter / lead) — optimized
>
> Runs continuously **beside** the layered workflow; report-only, never a gate. Target
> platform is **Linux**: the mechanical parts are shell scripts on cron (or systemd
> timers) plus git/CI hooks — no LLM in the steady state. Governing principle:
> **model attention is reserved for judgment; everything deterministic is a script.**
>
> - **Events over polling.** Git/CI hooks (PR opened, merge landed) and the balance
>   poller fire the scripts **immediately**; the 15-minute cycle remains only as a
>   liveness heartbeat. Critical relays never wait for a cycle boundary.
> - **Watcher script (mechanical):** threshold compares, mtime staleness checks,
>   roster diff, hygiene checks — deterministic, no LLM. Publishes `roster-state.md`
>   (the single source of team state) and computes a **rolling mechanical ETA** from
>   per-slice durations in the logs. Re-arms one-shot triggers (begin-close) on
>   confirmed recovery. Spawns the **watcher agent (LLM)** only when an anomaly
>   needs judgment or a written signal.
> - **Reporter (mechanical first):** routine summaries are template-filled from the
>   state files; the **reporter agent (LLM)** is invoked only for critical relays and
>   the stale-lead nudge. **Watch the watcher:** the reporter also flags when
>   `roster-state.md` itself is stale (watcher down) — symmetric with the existing
>   stale-balance-log flag.
> - **Derived status line:** the mechanical facts (open PRs, last merge, slices done
>   vs. planned, mechanical ETA) are computed each cycle; the lead adds only
>   interpretation and ETA judgment. Facts cannot go stale — only judgment can — so
>   the nudge becomes rare and meaningful.
> - **Escalation ladder:** status line >20 min stale → nudge the lead; nudge
>   unanswered for N further minutes → the reporter escalates to the user channel as
>   a critical relay, and the watcher's roster watch treats a stale lead like any
>   dead member. (This is the explicit dead-lead procedure the original loop lacked.)
> - **Interrupt classes for the lead:** critical (balance crossing, dead member,
>   blocked slice) interrupts immediately; everything else queues and lands at the
>   lead's next natural touchpoint (a verdict or merge moment). The lead's durable
>   memory is the handover file + status line, so its context can be compacted
>   without losing state.
> - **Lead entrances into the layered workflow (unchanged):** audit structural gap or
>   executor disagreement → **replan trigger** → planner files a new dated revision;
>   code-vs-spec conflict → **decision-maker** rules before either side is silently
>   changed; balance begin-close threshold → **close sequence**: file the record,
>   present it — closure acceptance is the user's alone.
>
> Runtime state files (`roster-state.md`, balance log, reporter state) live in the
> handover/ops directory, not in `docs/` — operational state, not plan artifacts.
>
> ## 15. Adoption workflow — converting this proposal into project updates
>
> The proposal is adopted as a **work item that runs through a lightweight version of
> the process it defines** — this de-risks the adoption and pilots the process in the
> same motion. Generic shape, applicable to any process-change proposal:
>
> 1. **Freeze the inputs.** Land the proposal documents in the repository as dated,
>    frozen source documents. At this point they are the *specification for the
>    adoption work item*, not yet the standard — nothing else changes.
> 2. **Reconcile against standards in force.** Diff the proposal against every
>    governing document already in effect (project instructions, team structure,
>    close checklists, the documentation standard). Classify every item: **adopt
>    as-is**, **amend**, or **reject**, with rationale. Rule every open question as
>    a dated decision record *before* anything is built — the pre-resolve gate
>    applied to the adoption itself.
> 3. **Plan.** One dated implementation plan meeting the §11 obligations, sliced in
>    dependency order — governing instructions first, then process and agent
>    documents, then role definitions, then checklist updates, then mechanical
>    automation. The plan's findings section sweeps the repository for **every file
>    the adoption touches**, so the carry-without-missing guarantee applies to the
>    adoption too.
> 4. **Implement incrementally.** Slice by slice, PR-only, gates run as usual, the
>    lead merges. Never big-bang: each layer is exercised before the next depends on
>    it (automation last — it is worthless until there is real activity to monitor).
>    Rollback stays free by construction, since every step is a PR of dated files.
> 5. **Audit the adoption against the proposal.** The auditor checks the landed
>    repository against the proposal-as-plan: every obligation represented, every
>    skeleton in place, divergences recorded with the ruling that legitimizes them,
>    findings to the register — and the adopted documents checked for mutual
>    consistency.
> 6. **Pilot before declaring the standard.** Run one small, real work item
>    end-to-end under the new process. Process defects found in the pilot are
>    register findings like any other — fixed or carried with owners; amendments
>    land as dated revisions, never edits. The pilot doubles as the acceptance test
>    of the whole design: if the process cannot cleanly process a small work item,
>    that is a finding against the process, caught before it governs anything
>    large.
> 7. **Close and supersede.** The lead presents the adoption record plus pilot
>    findings; acceptance is the user's alone. On acceptance, the proposal documents
>    receive a dated "superseded by the adopted specification" note and the adopted
>    specification becomes authoritative.
