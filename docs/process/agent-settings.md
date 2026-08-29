# Agent Settings — model, effort, skills and tool scope for the seven roles

Adopted 2026-08-29 from NT-0011 (`.claude/notes/0011-per-agent-model-and-skill-settings.md`),
companion to `docs/process/delivery-process.md`, reconciled and ruled in
`docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md` ("the rulings record").
Per-role tool scope is stated in full in each role's own file under `.claude/roles/` — this
document is the model/effort/skill settings source those files draw from, not a duplicate of
them.

## 1. Summary table

| Role | Model | Thinking effort | Mandatory skill | Spawn pattern |
|---|---|---|---|---|
| **lead** | whatever the session started with — see the note below | high; ultrathink for close-out verdicts | `using-git-worktrees` | Main thread, persistent |
| **planner** | Opus 5 | high | `writing-plans` | Idle by design; spawned per plan / replan trigger |
| **decision-maker** | Opus 5 | **ultrathink** (always — completed thinking on every ruling) | — (ultrathink discipline) | Spawned only when a decision point or spec conflict appears; stopped when rulings complete |
| **auditor** | Sonnet 5 | high | `requesting-code-review` | Fresh context per audit; never reuses an implementation session |
| **executor** | Sonnet 5 | medium (standard) | `subagent-driven-development` (recommended) or `executing-plans` — per the plan header — plus `test-driven-development` | Spawned per slice, own worktree |
| **watcher** | script (no LLM) + Haiku 4.5 agent on demand | n/a (script); low (agent) | — | Script on cron/systemd + event hooks; agent spawned on anomaly only |
| **reporter** | script + Haiku 4.5 agent on demand | n/a (script); low (agent) | — | Template summaries on cycle; agent for critical relay + nudge only |

**Model names** (Part B5): `opus` → **Opus 5**, `sonnet` → **Sonnet 5**, `haiku` →
**Haiku 4.5**, pinned in this environment rather than left to drift. A fourth tier,
**Fable 5**, exists (confirmed directly: the `Agent` tool's own `model` parameter enum in
this session is `sonnet | opus | haiku | fable`) and neither source note considered it. No
role is reassigned to it by this adoption — the volume-vs-leverage logic below already
covers the four roles that need a model choice, and Fable's fit is a separate question
nobody has raised — but its existence is recorded here rather than silently omitted.

**The lead's model is not a setting this document can enforce.** Every other row above
binds a **spawned** session at spawn time. The lead is not spawned — it is the main
thread, whatever model the session was started with — so its row states this explicitly
rather than reading as a setting that will be silently unmet the first time a session
starts on a different model than a name would suggest.

**Cost rationale:** balance was the binding constraint in W10 (begin-close threshold
nearly hit mid-workstream). The executor and auditor dominate token volume — they get
Sonnet 5. Judgment roles (lead, planner, decision-maker) are low-volume but high-leverage
— Opus 5 there is affordable and worth it. Watcher/reporter run as mechanical scripts with
zero steady-state LLM cost; their Haiku 4.5 agents spawn only on anomaly or critical
relay (§13 of `delivery-process.md`). Adopted **as an instrumented default, not fixed
governance** (rulings record Part B3) — whether a cheaper executor is net-cheaper once
re-audit cost is priced in is an empirical question this project has the data to start
answering and has not yet answered; revisit after a workstream's worth of measurement, not
before.

**`ultracode` is `ultrathink`, resolved** (rulings record Part B2): the decision-maker's
effort setting is maximum extended thinking, never the multi-agent `Workflow`-orchestration
keyword — the source note already used the correct word ("ultrathink"); this line records
the resolution rather than changing anything.

**Skill binding:** the Superpowers-derived skills are vendored as project skills in
`.claude/skills/` — agents and plan headers invoke them by their registered names; no
plugin installation or `superpowers:` namespace is involved (see `docs/plans/2026-08-29-
nt-0010-0011-adoption.md` Task 2 for the two places that still said otherwise, now fixed).

## 2. Per-role notes beyond the summary table and each role's own file

Full ownership, boundaries and tools are in `.claude/roles/<role>.md` per role (Task 3 of
the adoption plan) — not restated here. Three things this settings document states because
they cut across roles or correct the source notes directly:

- **The lead's tool row** (Part B9): **"full read; git merge authority (sole merge
  authority); write to handover/status files only."** This is NT-0011's version, not
  NT-0010's — NT-0010 §2's lead row disagreed (read-only + plan/map files, no merge
  authority stated at all). Corrected here to match confirmed practice: this session's own
  experience (every PR reviewed and merged by the lead, never self-merged) and
  `TEAM-STRUCTURE.md`'s table both match NT-0011's row, not NT-0010's.
- **`docs/`-write scope for planner, decision-maker and auditor is ruled** (Part A2): each
  role's own file in `.claude/roles/` states its final tools column directly — this
  document does not duplicate it.
- **Retry caps and cost tiers are instrumented defaults, not fixed governance** — see
  `docs/process/delivery-process.md` §7.

## 3. Deltas adopted from current practice

These reconcile the source proposals with current practice, confirmed by filed artifacts
(the W6b-15 plan, the W10-3 work-item record, the register) rather than asserted:

1. **Verdict split:** auditor proposes → **lead** adopts/amends/rejects and merges.
   Decision-maker rules decision points and spec conflicts only. (Replaces NT-0010's
   original decision-maker-owned fix/accept/defer.)
2. **Frozen dated plans:** replans produce new dated files, never in-place edits.
3. **PR-only members; lead-only merges;** CI verified on the exact head.
4. **RE-audit rule** and **durability rule** are written into the auditor's role file
   (`.claude/roles/auditor.md`).
5. **Per-slice audit axes** (the W11 lesson) are written into the auditor's role file.
6. **Worktree-collision rule** is written into every role file with git write access, and
   enforced structurally by the lead's `using-git-worktrees` dispatch.
