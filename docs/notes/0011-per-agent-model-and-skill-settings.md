# NT-0011 — Per-agent model, thinking effort and skill bindings for the seven roles

| | |
|---|---|
| **Raised** | 2026-08-29, maintainer — supplied `agents-settings-proposal.md` as the companion to the workflow proposal, with the instruction to convert it into a working note |
| **Status** | **`superseded` 2026-08-29 — by the adopted specification, `docs/process/delivery-process.md` together with `.claude/roles/*.md` and `docs/process/agent-settings.md`, authoritative from this date.** Accepted by the maintainer 2026-08-29 alongside its parent [`NT-0010`](0010-layered-slice-based-workflow.md), on the lead's presentation of the adoption record and pilot findings. This document is now the **proposal record** it was adopted from, kept rather than deleted. Where the two disagree, the adopted specification wins. *(Previously `landed` 2026-08-29 — ruled alongside its parent in `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md`.)* |
| **Deliverable** | Role definitions under `.claude/agents/` and an agent-settings document. **No change to `docs/specs/` and no product code** |
| **Owner** | Maintainer accepts and rules the open items · Claude drafts the role files and the settings document |
| **Lands in** | Proposed by the author: `docs/process/agents.md`; also `.claude/agents/` (seven new role files) and `.claude/agents/README.md` (its dividing line, which the decision-maker role contradicts) |
| **Trigger** | After [`NT-0010`](0010-layered-slice-based-workflow.md)'s six items are ruled — this document assigns settings to roles that document defines, so it is meaningless before the roles are agreed |
| **Parent** | [`NT-0010`](0010-layered-slice-based-workflow.md) — the layered workflow these settings serve |

---

## Request, refined

For each of the seven roles the workflow defines — lead, planner, decision-maker, auditor,
executor, watcher, reporter — fix the **model**, the **thinking effort**, the **mandatory
skill bindings**, the **tool scope**, the **spawn pattern**, and the boundaries each role
must never cross. The cost argument is explicit: the executor and auditor dominate token
volume and get the cheaper model; the judgment roles are low-volume and high-leverage and
get the expensive one; the watcher and reporter run as shell scripts with no model in the
steady state and spawn a cheap agent only on an anomaly or a critical relay.

The document also carries six deltas reconciling the workflow proposal against current
practice, and four open items it asks to have confirmed.

## What is already in force (verified at `74b1b10`)

- **All six skills it binds are project skills.** `writing-plans`,
  `subagent-driven-development`, `executing-plans`, `test-driven-development`,
  `using-git-worktrees` and `requesting-code-review` are all under `.claude/skills/`;
  `.claude/skills/README.md` records fourteen vendored from `obra/superpowers` and
  `CLAUDE.md` §12 already gives them precedence. **The document's open item on this is
  resolved in its favour** — no plugin installation and no `superpowers:` namespace is
  involved.
- **The six deltas in §3 describe current practice accurately.** The verdict split (auditor
  proposes, lead adopts and merges, decision-maker rules decision points and spec only),
  frozen dated plans, PR-only members with lead-only merges, the re-audit rule, the
  durability rule, the per-slice audit axes, and the worktree-collision rule are all in force
  and each of the last two was bought with a real incident.
- **The decision-maker's hard boundary is correctly derived.** *No write access to any code
  worktree* is not a theoretical precaution: during W10 the decision-maker wrote into the
  executor's worktree three times despite a stop order, and the third write discarded the
  executor's tracked files. Source: `w10-handover-2026-08-28/TEAM-STRUCTURE.md` (role table
  and the worktree-collision-rule note), which records **two** such incidents — this one and
  a separate, milder auditor incident — and names both. *(Corrected 2026-08-29, the §15 step
  2b reconciliation: that file is outside this repository and not durable custody for the
  fact — see `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md` Part B10. The
  boundary should survive adoption unchanged; the citation should not survive as an external
  pointer once the decision-maker's own role file exists.)*
- **The watcher and reporter are already mechanical in part.** Both run scripts under
  persistent monitors today; what the document proposes is removing the model from the
  steady state, not inventing the scripts.

One premise is **not** in force and is load-bearing: the document says agent files that
already exist "are **amended at adoption, not recreated**." **There are none.**
`.claude/agents/` holds seven delegable specialists *(corrected 2026-08-29 — a directory
listing that included its own `README.md` read as eight; `.claude/agents/README.md:184`
already states "all seven"; see `docs/plans/2026-08-29-nt-0010-0011-reconciliation-
rulings.md` Part B8, which corrected NT-0010's identical instance but not this sibling
one)* and no role definitions; the seven roles
live in a handover file outside the repository and in spawn-time briefs that die with the
session. Every role file is a create, not an amend.

## Claude's assessment (kept separate from the maintainer's words)

The volume-versus-leverage logic is sound and the boundaries are well drawn. Four things
need attention before this can be adopted.

### 1. The auditor's tool scope contradicts the auditor's own ownership

Within one section the document says the auditor **owns** "closure records, register
deferral rows with named owners" — and then sets its tools to "Read-only + Bash for running
checks; **no edits**." A role cannot own an artifact it may not write. The workflow
proposal's §2 has the same shape: "Never fixes anything — only reports," with a read-only
tool scope.

Practice resolves it in one direction and the document should say so: in W10 the auditor
authored `docs/audit/work/W10/README.md`, the register rows, and the spec-change PRs #308
and #309. **Recommendation: amend the tool scope** — the auditor is read-only *with respect
to the code under audit*, and a writer of audit records, register rows and correction PRs.
Stating it as "no edits" would either be ignored on day one or would strand the closure
records with no owner. This is the same distinction [`NT-0010`](0010-layered-slice-based-workflow.md)
item 2 raises against `.claude/agents/README.md`'s "none of them decides", and both should be
ruled together.

### 2. "ultracode" is not "ultrathink"

The document flags its own assumption and asks for confirmation. The assumption is wrong as
stated: in Claude Code `ultracode` is a distinct keyword that opts a session into
**multi-agent workflow orchestration**, and `ultra` is the level that launches a multi-agent
cloud code review. Neither is the extended-thinking trigger.

So the instruction was ambiguous between two very different things: fan the decision-maker
out across parallel agents, which the workflow proposal's §7 forbids and which no decision
point in W10 needed, or think as hard as possible on every ruling, which is cheap because
rulings are rare. **Recommendation: rule it as maximum extended thinking**, and record the
correction, so the word does not get re-read as orchestration by a later session.

### 3. The cost rationale is untested here, and it makes the auditor the safety net

The document gives the executor the **lowest** care setting of any working role, on the
argument that the TDD loop and per-slice gates bound the risk "and the auditor catches what
slips through."

That is a real argument, but it has a cost the document does not price. In W10 the auditor
caught, among others, a frozen-model test-import bug, markerless API tests invisible to
coverage tooling, two untested exclusion faces, a contract left inconsistent by a rebase, and
a round-trip test that asserted nothing. **Every one of those cost a re-audit, and a
re-audit is a full gate re-run.** Making the executor cheaper moves work onto the most
expensive part of the loop. Whether that is net-cheaper is an empirical question this project
has the data to answer and has not.

**Recommendation: adopt the tiers as instrumented defaults**, and log per-slice re-audit
counts and gate re-runs from the first slice, so the next revision is tuned against burn
data rather than against the intuition. The document half-says this already in its open
items; it should be a condition of adoption rather than a footnote.

### 4. Two smaller things

- **Model names.** `opus`, `sonnet` and `haiku` map onto Opus 5, Sonnet 5 and Haiku 4.5 in
  this environment; a fourth, Fable 5, exists and the document does not consider it. Names
  should be pinned when the settings land, since the mapping is what a later session will
  read literally.
- **The lead has no model row it can enforce.** The lead is the main thread; its model is
  whatever the session was started with, not something a role file sets. The row should say
  so rather than read as a setting that will be silently unmet.

## What this note does not decide

Nothing. Per `docs/notes/README.md`, a note is raw material. The tool-scope amendment in
item 1 changes `.claude/agents/README.md`'s dividing line and so touches more than one part
of the working standard; it needs a maintainer ruling recorded with a date, taken together
with [`NT-0010`](0010-layered-slice-based-workflow.md) item 2.

## Acceptance criteria

1. Item 1's contradiction is resolved in both documents, and `.claude/agents/README.md`
   records the amended dividing line.
2. Item 2 is ruled, and the ruling records the correction rather than only the outcome.
3. Seven role files exist under `.claude/agents/`, each carrying its boundaries and — for
   every role with git write access — the worktree-collision rule.
4. Per-slice re-audit counts and gate re-runs are logged from the first slice under the new
   process, so the tiers can be revisited against measurement.
5. The model names are pinned to their exact identifiers at the date they land.

## Next step

Hold until [`NT-0010`](0010-layered-slice-based-workflow.md)'s items are ruled — this
document cannot be adopted ahead of the roles it configures. Then it becomes the second
slice of that adoption plan: governing instructions first, then process and agent documents,
then role definitions.

## Original wording

Kept verbatim below, corrected for grammar and punctuation only — never for wording,
structure or meaning. Reproduced in full for the same reason as in
[`NT-0010`](0010-layered-slice-based-workflow.md): the source reached this project as a loose
file outside the repository, and a note citing a path that will not survive is the custody
failure [`NT-0005`](0005-deferred-items-with-no-durable-custody.md) records.

> # Agent Settings Proposal
>
> **Companion to:** `workflow-design-proposal.md`
> **Suggested destination after adoption:** `docs/process/agents.md` (beside `docs/process/workflow.md`) — a suggestion only; placement and naming remain the project's decision per the documentation standard.
> **Purpose:** Per-agent model, thinking effort, Superpowers skill bindings, tool scope,
> and boundaries — drawn from the workflow design and reconciled against the current
> team structure (`TEAM-STRUCTURE.md`, W10-era rules and incident lessons).
>
> > **Assumption to confirm:** "ultracode" for the decision-maker is interpreted as
> > **ultrathink** (Claude Code's maximum extended-thinking trigger). If a different
> > tool/skill named "ultracode" was meant, this proposal needs a one-line correction.
>
> ## 1. Summary table
>
> | Agent | Model | Thinking effort | Superpowers skills (mandatory) | Spawn pattern |
> |---|---|---|---|---|
> | **lead** | opus | high; ultrathink for close-out verdicts | `using-git-worktrees` | Main thread, persistent |
> | **planner** | opus | high | `writing-plans` | Idle by design; spawned per plan / replan trigger |
> | **decision-maker** | opus | **ultrathink** (always — completed thinking on every ruling) | — (ultrathink discipline) | Spawned only when a decision point or spec conflict appears; stopped when rulings complete |
> | **auditor** | sonnet | high | `requesting-code-review` | Fresh context per audit; never reuses an implementation session |
> | **executor** | sonnet | medium (standard) | `subagent-driven-development` (recommended) or `executing-plans` — per the plan header — plus `test-driven-development` | Spawned per slice, own worktree |
> | **watcher** | script (no LLM) + haiku agent on demand | n/a (script); low (agent) | — | Script on cron/systemd + event hooks; agent spawned on anomaly only |
> | **reporter** | script + haiku agent on demand | n/a (script); low (agent) | — | Template summaries on cycle; agent for critical relay + nudge only |
>
> **Cost rationale:** balance was the binding constraint in W10 (begin-close threshold
> nearly hit mid-workstream). The executor and auditor dominate token volume — they get
> sonnet. Judgment roles (lead, planner, decision-maker) are low-volume but high-leverage
> — opus there is affordable and worth it. Watcher/reporter run as mechanical scripts
> with **zero steady-state LLM cost**; their haiku agents spawn only on anomaly or
> critical relay (workflow §14). If running through a proxy backend with different model
> tiers, map by the same volume-vs-leverage logic rather than by name.
>
> **Skill binding:** the Superpowers-derived skills are **vendored as project
> skills** in the project's skills folder — agents and plan headers invoke them by
> their registered names; no plugin installation or `superpowers:` namespace is
> involved. Each `.claude/agents/*.md` body carries its mandatory-skill directive by
> name; agent files that already exist from the current team are **amended at
> adoption, not recreated**.
>
> ## 2. Per-agent specifications
>
> ### lead (main thread)
>
> - **Model / effort:** opus; high. Escalate to ultrathink for §13-style close-out
>   verdicts and for adopting/amending/rejecting audit verdicts.
> - **Mandatory skill:** `using-git-worktrees` (project skill) — the lead dispatches every
>   member into its **own worktree** and enforces the worktree-collision rule (two real
>   incidents in W10: cross-worktree checkouts discarded uncommitted work). Rule text to
>   carry into the agent body: *never `git checkout`/`git switch` outside your own
>   worktree; check `pwd` before every git write; read-only git is safe anywhere.*
> - **Owns:** verdicts (adopts/amends/rejects the auditor's proposals — including
>   the auditor's proposed §8 finding decisions), merges (sole merge authority;
>   verify CI on the exact head), dispatch, replan triggers, status-line judgment
>   and ETA adjustment over mechanically derived facts (workflow §14), handover
>   maintenance, presenting the close to the user.
> - **Never:** implements or audits itself; never declares a workstream closed —
>   closure acceptance is the user's alone.
> - **Tools:** full read; git merge authority; write to handover/status files only.
>
> ### planner
>
> - **Model / effort:** opus; high thinking. Plans are the highest-leverage artifacts
>   in the system and are frozen once dated — worth maximum quality at write time.
> - **Mandatory skill:** `writing-plans` (project skill) — all map plans (project/phase/work)
>   and slice plans follow its conventions (this supersedes the fallback template in
>   the workflow proposal §11 once confirmed).
> - **Owns:** the plan: frozen dated files in `docs/plans/`; new dated revisions on a
>   replan trigger; scope + requirement coverage, slices with task lists and per-slice
>   gates, decision points with options + recommendations. Every plan meets the
>   workflow's §11 obligations: binds its executor's skill in the header, rests on
>   findings verified at a pinned commit (full-class sweeps, not samples), makes
>   acceptance executable (exact commands + expected results per step), carries its
>   constraints cited to source, and self-reviews before freeze.
> - **Never:** implements, audits, merges, or rules decision points.
> - **Tools:** Read, Grep, Glob; write to `docs/` plan files only.
>
> ### decision-maker
>
> - **Model / effort:** opus; **ultrathink on every ruling** — decisions are rare,
>   binding, and cheap to think hard about relative to the cost of a wrong ruling.
> - **Skill binding:** none of the Superpowers workflow skills; its discipline is the
>   ultrathink pass itself, plus the dated-record convention.
> - **Owns:** technical decisions only — decision-point rulings and spec changes,
>   recorded as dated sibling records, never edits to the frozen plan. Pre-resolves
>   every DP before its slice starts. A spec change conforming to the plan needs no
>   replan.
> - **Never:** closes work/phases, implements, or touches audit verdicts (verdicts are
>   the lead's — this narrows the workflow proposal's original fix/accept/defer
>   assignment, matching current practice). **No write access to any code worktree**
>   (hard boundary after the W10 stop-order incident): ruling records only.
> - **Spawn:** only when a new DP or spec conflict appears; stopped when duties
>   complete.
> - **Tools:** Read; write to ruling records and the open-questions log only.
>
> ### auditor
>
> - **Model / effort:** sonnet; high thinking. Volume is moderate (evidence gathering,
>   comparison vs plan) but the comparisons need care.
> - **Mandatory skill:** `requesting-code-review` (project skill) — audits are framed as
>   review requests with evidence + proposed verdicts, delivered to the lead.
> - **Owns:** per-slice audits (every audit axis runs **per slice**, not just at close
>   — the W11 lesson), gap lists, closure records, register deferral rows with named
>   owners. RE-audits after every fix: **re-run the checks, never rubber-stamp.**
>   Fresh context each time — it must not inherit the implementation session's
>   reasoning. Audit records meet the workflow's §12 obligations: pinned commit head
>   with the gate re-run and measured, divergences tabled with the legitimizing spec
>   rule or dated ruling, per-requirement verdicts (silence is never a verdict),
>   judgment calls explicitly judged, and findings decided in the §8 forms (fix
>   before close / accept with instrument / carry forward with owner or trigger)
>   with register rows filed or updated in the same record.
> - **Never:** merges, implements, declares anything closed. Proposes verdicts;
>   never issues them.
> - **Durability rule:** findings that live only in chat are ephemeral — the durable
>   landing is always a merged artifact (closure record, register row, correction PR,
>   or plan revision).
> - **Tools:** Read-only + Bash for running checks; no edits.
>
> ### executor
>
> - **Model / effort:** sonnet; medium (standard). The highest-volume role; the TDD
>   loop and per-slice gates bound the risk of a cheaper/faster setting, and the
>   auditor catches what slips through.
> - **Mandatory skills:** `subagent-driven-development` (recommended) or
>   `executing-plans`, as the plan header directs — plus `test-driven-development`
>   (all project skills). The slice cycle is exactly red → green →
>   verify & refactor, with the full local gate before push.
> - **Owns:** one slice at a time from the frozen plan, in its **own worktree**;
>   full local gate before push; opens PRs.
> - **Never:** merges, self-audits.
> - **Tools:** full read/write + Bash, scoped to the current slice's worktree.
>
> ### watcher (support — mechanical first)
>
> - **Form:** a Linux shell script on cron/systemd plus event hooks — deterministic
>   checks, no LLM in the steady state. A **watcher agent** (haiku; low effort) is
>   spawned only when an anomaly needs judgment or a written signal.
> - **Owns (script):** balance thresholds + re-arming one-shot triggers on confirmed
>   recovery, roster/staleness watch, hygiene checks, publishing `roster-state.md`
>   each cycle as the **single source of team state**, and the rolling mechanical
>   ETA computed from per-slice durations in the logs.
> - **Owns (agent):** judgment on ambiguous anomalies and the written signal to the
>   lead.
> - **Never:** dispatches stand-ins, touches the repo.
>
> ### reporter (support — mechanical first)
>
> - **Form:** routine summaries are template-filled from the state files by script;
>   a **reporter agent** (haiku; low effort) is invoked only for critical relays and
>   the stale-lead nudge.
> - **Owns:** the single external comms channel; **watch-the-watcher** (flags a stale
>   `roster-state.md`, symmetric with the stale-balance-log flag); the **escalation
>   ladder** — nudge the lead when the status line is >20 min stale, and if the nudge
>   goes unanswered, escalate to the user channel as a critical relay (a stale lead
>   is treated like any dead member). Reads the watcher's published state — never
>   polls agents.
> - **Never:** edits the repo, merges, audits.
>
> ## 3. Deltas this proposal adopts from current practice
>
> These reconcile the workflow proposal with current practice — now **confirmed by
> the filed artifacts** (the W6b-15 plan, the W10-3 work-item record, the register).
> The workflow document is amended through the adoption workflow's reconciliation
> step (workflow §15, step 2):
>
> 1. **Verdict split:** auditor proposes → **lead** adopts/amends/rejects and merges.
>    Decision-maker rules DPs/spec only. (Replaces the workflow proposal's
>    decision-maker-owned fix/accept/defer.)
> 2. **Frozen dated plans:** replans produce new dated files, never in-place edits.
> 3. **PR-only members; lead-only merges;** CI verified on the exact head.
> 4. **RE-audit rule** and **durability rule** written into the auditor's agent body.
> 5. **Per-slice audit axes** (W11 lesson) written into the auditor's agent body.
> 6. **Worktree-collision rule** written into every agent with git write access, and
>    enforced structurally by the lead's `using-git-worktrees` dispatch.
>
> ## 4. Open items
>
> - Confirm the "ultracode" → **ultrathink** interpretation for the decision-maker.
> - Skill names partially confirmed by the filed plan header
>   (`subagent-driven-development`, `executing-plans`); confirm the registered names
>   of `writing-plans`, `using-git-worktrees`, and `requesting-code-review` against
>   the project skills folder (the vendored set), not an external plugin.
> - Watcher/reporter: the mechanical scripts are near-free and can run from day one;
>   only the on-demand agents are a cost decision.
> - Effort settings above are starting points — tune against real burn-rate data
>   (executor effort per slice has ranged from ~20 minutes to ~1 day, so the cost
>   profile is workload-dependent).
> - All of the above are ruled as dated decision records in the adoption workflow's
>   reconciliation step (workflow §15, step 2) — nothing here needs to be settled
>   before adoption starts.
