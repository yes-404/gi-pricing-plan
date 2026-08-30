# NT-0014 — A machine-readable core for the delivery process, so the rules a script can check stop being prose

| | |
|---|---|
| **Raised** | 2026-08-30, by a session working against `docs/process/delivery-process.md` at tree `6f77abb`, one day after that spec was accepted. Filed by the lead, who verified the note's own claims against the same tree before filing rather than relaying them |
| **Status** | `open` — proposed, not adopted. Nothing here is in force, and the companion JSON in the appendix is a draft under proposal, deliberately **not** filed at `docs/process/`: filing it there would be the adoption, and adoption is step 2's, not this note's |
| **Deliverable** | **Spec change first, then code**, per `CLAUDE.md` §0's table. The three artifacts are mechanism for rules that already exist, but they add a gate command, a new tracked file and a CI job, so `docs/process/delivery-process.md` and `CLAUDE.md` §11/§15 change before any script is written |
| **Owner** | The decision-maker rules §7's four open questions; the lead runs the §5 plan gate; **the maintainer accepts the adoption's close** (`CLAUDE.md` §12 — a Work close is the maintainer's, never a role's). No acceptor is named for the proposal *as a whole* yet, which is what `open` means here |
| **Lands in** | Nothing yet. The §5 impact matrix names 22 targets if adopted — `CLAUDE.md` §11 and §15, seven sections of `docs/process/delivery-process.md`, `docs/process/agent-settings.md`, five role files, three skills, `docs/open-questions.md`, `docs/roadmap.md`, plus four new files. That breadth is itself an argument the decision-maker should weigh: a proposal touching 22 files is a Work, not a chore |
| **Sequencing / Trigger** | **Not before W11 closes.** `CLAUDE.md` §14 forbids starting next-phase work while an open finding lacks a resolution, and this is a Work-sized change to the process the current workstream is running under — changing the process mid-workstream would invalidate the pilot data §7's retry caps are waiting on. The natural trigger is the W11 §14 plan review, which is already scheduled and already holds three gate-coverage findings (F27(c), F29, F33) that overlap this proposal's C4. ***Amended 2026-08-30, same day:*** the maintainer directed the adoption to begin when W11's **Slice 2** ends, without W11 closing. That contradicts this row's literal wording and satisfies its reason — the trigger existed to keep the process from changing under a running workstream, and W11 is being **stopped** rather than continued, so there is no workstream left to disturb. **What is lost is the overlap**: F27(c), F29 and F33 are the three gate-coverage findings the §14 review was to bundle into one item, and this proposal's C4 is a mechanism of that family. With no review to carry them, the adoption must either pick them up deliberately or record that it left them — silently inheriting them is the failure mode. NT-0012 and NT-0013 are adopted alongside this note |

---

## 0. What this note is, and what it is not

**A note decides nothing** (`.claude/notes/README.md`). This one records a proposal, the
evidence gathered for it, and the questions it cannot answer itself. If its conclusion
matters after the session that produced it, it becomes a spec change, an ADR, an `OQ-` entry
or a roadmap row — and this note must then say where it went.

Two things are worth separating before reading further, because the proposal's own value
depends on which one you are persuaded by:

- **The mechanism** (§2) — three artifacts that close three enforcement gaps the process
  spec names in its own text. This is the proposal.
- **The evidence that the gaps are live** (§9) — including one stale citation *inside the
  process spec itself*, found while checking this proposal against the repository. That
  finding is not this proposal's to fix and is reported separately below.

---

## 1. Motivation

The spec names three of its own enforcement gaps. This proposal closes them with mechanism,
not new rules:

1. **State is implicit.** Retry counts, current layer, and loop iteration exist only in
   artifacts and conversation history. §7 requires logging "every replan/audit-fix loop
   iteration and every per-slice re-audit count" but names no file that holds the counters.
   An agent asking "am I on replan #2?" reconstructs the answer — reconstruction under
   pressure is where drift happens.
2. **The verify gate is instruction-only.** §6 step 4, verbatim: "Not yet built as a
   blocking hook … an instruction the executor follows, not an enforcement mechanism"
   (rulings record Part C row 5).
3. **Coordination state is relayed pairwise.** §8 (pilot finding P14): two roles ran full
   suites concurrently because nothing published what was running. The fix ("announce an
   expensive verification … check for one already in flight") has no named place to
   announce *to*.

A fourth, softer motivation: normative rules are embedded in narrative (§8 is ~40 lines of
rulings history around one rule). Agents extract rules from prose correctly *most* of the
time; a mechanical extract makes the load-bearing subset checkable by scripts that never
paraphrase. Evidence this class of drift is live: the spec's own CLAUDE.md back-reference
was stale at `6f77abb` (package Part 1, finding 5).

## 2. Proposal

Three artifacts, one authority rule (§3):

- **A. Core extract** — `docs/process/delivery-process.core.json`. The state-machine
  skeleton of the spec: layers, flows, transitions, retry caps, verdict vocabularies,
  role authorities, parallelism guard, human checkpoints, message-discipline constants.
  Every block carries a `source` field citing its spec section (the CLAUDE.md §13 reference
  rule applied to the extract itself). Carries **no rationale, rulings history, or pilot
  findings** — those stay in the markdown.
- **B. Runtime state file** — one JSON file in the handover/ops area (outside the repo,
  per spec §10 and §13's existing rule for operational state), shaped by the
  `runtime_state_schema` block of artifact A: current position (project/phase/work/slice/
  flow-step), per-layer retry counters, pending human checkpoint, and the in-flight
  expensive-verifications list that gives spec §8's announcement protocol a home.
- **C. Mechanical scripts** (extends the adoption plan's Task 6 scope; deterministic,
  no LLM, same class as the watcher's checks; precedent: `scripts/audit-docs.py`):
  1. *Plan validator* — a filed map/slice plan must contain an explicit acceptance-standard
     field (mechanizes spec §5 step 4's check "actually defined, not just implied").
  2. *Retry-cap hook* — increments the counter in B on every replan/fix loop; on breach of
     the cap in A, blocks the retry and notifies a human (mechanizes spec §7's on-breach rule).
  3. *Verify-gate hook* — the blocking hook spec §6 step 4 says is not built; closes
     rulings record Part C row 5.
  4. *Drift check* — diffs A against the markdown spec section-by-`source`-citation; run
     in CI and by the watcher's hygiene cycle. A and the md disagreeing is a red gate.
     Would also have caught Part 1 finding 5.
  5. *(Optional)* Mermaid generator — emits the two flow diagrams from A for spec §5 and
     §6, so diagram and machine truth cannot diverge.

## 3. Authority rule

**The markdown spec remains solely authoritative.** Artifact A is derived, marked
`"authoritative": false` in its own `meta`, and is regenerated or diff-checked (script C4)
on every spec change. On any disagreement, the markdown wins and A is wrong by definition.
This is the same one-source rule the spec already applies in its §11 and §12 ("one source,
not two") — the JSON is a *view with enforcement*, not a second source.

## 4. Non-goals

- No governance changes. Retry caps stay instrumented defaults (spec §7); their *values*
  are not revisited here — this proposal only gives the instrumentation §7 already ordered
  a concrete home.
- No prose-to-JSON migration. Spec §15's correction discipline, §4's disambiguation note,
  and all rationale stay in markdown, where they do their work.
- No new roles, no new checkpoints, no change to spec §2's human-checkpoint ruling.
- No change to where runtime/ops state lives (stays outside the repo).

## 5. Impact matrix — every file to update, and how

Ordered by layer of the change. All targets verified to exist at `6f77abb` except rows
marked **New**.

| # | File | Change | Nature |
|---|---|---|---|
| 1 | `CLAUDE.md` §15 (Team Process, line 292) | Add one sentence: "Its mechanical extract is `docs/process/delivery-process.core.json`; the markdown is authoritative, the extract is derived and drift-checked (NT-0014 §3)." | Amend |
| 2 | `CLAUDE.md` §11 (Commands Reference) | Add the drift check (C4) and plan validator (C1) to the full gate's command list, so a red drift-check fails the gate like the Python/frontend halves already do. | Amend |
| 3 | `docs/process/delivery-process.md` §10 | Add two bullets under Required artifacts: the core extract (with the §3 authority rule in one sentence) and the runtime state file (named as the concrete form of the ops-area state §10 already lists). | Amend |
| 4 | `docs/process/delivery-process.md` §6 step 4 | When C3 lands: replace "Not yet built as a blocking hook…" with a sentence naming the hook and its config location. Closes rulings record Part C row 5 — **record the closure in the rulings record or its successor, not silently**. | Amend on C3 completion |
| 5 | `docs/process/delivery-process.md` §7 | Point the instrumentation sentence at the runtime state file and retry-cap hook as the mechanism doing the logging. Cap values unchanged. | Amend, 1 sentence |
| 6 | `docs/process/delivery-process.md` §8 | Point the announcement protocol at the `in_flight_expensive_verifications` list in the runtime state file — the "visible, not relayed pairwise" home the section demands. | Amend, 1 sentence |
| 7 | `docs/process/delivery-process.md` §13 | Add the runtime state file to what the watcher maintains, and the drift check (C4) to its hygiene checks. | Amend |
| 8 | `docs/process/delivery-process.md` line ~6 | Pre-existing fix, ride-along: "`CLAUDE.md` §12" → "`CLAUDE.md` §15" (Part 1 finding 5). | Amend, 2 chars |
| 9 | `docs/process/agent-settings.md` | Add the runtime state file's path (ops area) and the rule that agents read position/counters from it rather than reconstructing. | Amend |
| 10 | `.claude/roles/watcher.md` | Owns artifact B: writes position, counters, in-flight list each cycle and on events; runs C4 in the hygiene sweep. Stays report-only — the *hooks* block, the watcher only observes and signals. | Amend |
| 11 | `.claude/roles/lead.md` | Plan gate (spec §5.4): consult C1 validator output as evidence for "acceptance standard actually defined". Verdicts: recording a fix/replan decision updates the counter in B (via hook C2, not by hand). | Amend |
| 12 | `.claude/roles/planner.md` | Plans must carry the acceptance-standard field in the exact form C1 validates (field name/format fixed in `writing-plans`, row 15 — one source). | Amend, pointer only |
| 13 | `.claude/roles/executor.md` | Verify step is gated by hook C3 once built; before any full-suite run, check and write the in-flight list in B (spec §8 protocol). | Amend |
| 14 | `.claude/roles/auditor.md` | Same spec-§8 in-flight check/announce obligation before expensive verification. No change to fresh-context or report-only constraints. | Amend, 1 line |
| 15 | `.claude/skills/writing-plans/SKILL.md` | Define the machine-checkable acceptance-standard field (name, position, format) that C1 validates. This is the *one* place the format lives (spec §11's own rule). | Amend |
| 16 | `.claude/skills/close-workstream/SKILL.md` | Closure record includes the layer's final retry counters read from B (the spec-§7 data the revisit decision needs). | Amend |
| 17 | `.claude/skills/phase-review/SKILL.md` | Same as row 16 at phase level. | Amend |
| 18 | `docs/open-questions.md` | Add this note's §7 questions on filing. | Append |
| 19 | `docs/plans/2026-08-30-nt-0014-adoption.md` | New adoption plan (this note's §6 is its skeleton), frozen/dated-revision convention per `docs/plans/README.md`. | New file |
| 20 | `docs/roadmap.md` | Add the adoption as a Work item in the current phase (it is a Work: it has slices, audits, and a close). | Amend |
| 21 | `scripts/` + hook/config wiring (per §7 Q3) | C1–C4 as scripts (precedent: `scripts/audit-docs.py`); hook registration config is net-new — no `.claude/settings.json` or `.claude/hooks/` exists at `6f77abb`. CI job for C4. | New |
| 22 | `docs/process/delivery-process.core.json` | Artifact A itself (Part 3), `source` citations already verified. | New file |

**Deliberately unchanged:** `docs/audit/register.md` (spec §9 mechanism untouched),
`docs/workflows/wf-01…05` (domain, not process — spec §4 / CLAUDE.md §15's own distinction),
`.claude/agents/` (reserved for delegable specialists, rulings record Part B11),
`.claude/roles/reporter.md` (already reads the watcher's files; B is just one more — add a
pointer only if its file enumerates sources), and all `.claude/skills/` not named above.

## 6. Adoption tasks (maps to spec §14's workflow)

1. **Freeze** — file this note as NT-0014. *(this artifact)*
2. **Reconcile** — decision-maker rules §7's open questions; lead runs the spec-§5 plan
   gate on this note's plan; rulings recorded in a dated record per convention.
3. **Plan** — file row 19's adoption plan; each task below is one process-slice (spec §4's
   disambiguation: the numbered items here are a table of contents, not units).
4. **Implement** — order: A + doc pointers (rows 1–3, 8, 22) → B + watcher (rows 7, 9, 10)
   → C1+C4 and their gate wiring (rows 2, 15, 21) → C2 (rows 5, 11, 16–17) → C3 (rows 4,
   13). Each lands as its own slice: red test → green → audit → PR.
5. **Audit** — per-slice as usual; the work-level audit specifically checks the impact
   matrix against reality (every row landed or explicitly deferred to the register).
6. **Pilot** — first live workstream after C2 lands runs with counters on; spec §7's
   "revisit when a workstream's worth of data exists" clock starts then.
7. **Close and supersede** — nothing to supersede (this note adds mechanism, replaces no
   document); close per spec §2's Work checkpoint, maintainer deciding.

## 7. Open questions (for the decision-maker at step 2)

- **Q1 — Generated vs. hand-maintained:** is A hand-edited and drift-checked (C4 only), or
  generated from an annotated md and never hand-edited? Proposal: start hand-maintained +
  C4; revisit if drift-check failures recur — same evidence-first posture as spec §7's caps.
- **Q2 — Hook wiring:** scripts land in `scripts/` (precedent `audit-docs.py`); but hook
  *registration* has no existing home (`6f77abb` has no `.claude/settings.json` or
  `.claude/hooks/`). Rule where registration config lives and whether C2/C3 run as Claude
  Code hooks, git hooks, or both.
- **Q3 — Does C1 red-gate or warn** on legacy plans filed before row 15's format lands?
  Proposal: warn until the format is in `writing-plans`, red thereafter; never
  retro-red-gate frozen plans.
- **Q4 — Counter authority:** on disagreement between B's counters and artifact history,
  which wins? Proposal: artifacts win (B is operational state, not a record — consistent
  with spec §10's distinction); the watcher flags the mismatch as an anomaly.

## 8. Acceptance standard (this proposal's own, per spec §5 step 2)

Adoption is complete when, verifiably: **(a)** every impact-matrix row is landed or has a
register entry with a named decision; **(b)** C4 runs green in CI against the inserted A;
**(c)** a deliberately cap-breaching test loop is blocked by C2 and produces a human
notification, in a test harness; **(d)** a filed plan missing the acceptance-standard field
is flagged by C1; **(e)** one pilot workstream has run with counters recorded in B and the
close record (row 16) cites them. Each item names its command and tree when reported
(spec §15: a subset is a subset; say which one you ran).
---

## 9. Evidence — what was checked against the repository, and what it found

The proposal was drafted without the repository open, then checked against
`yes-404/gi-pricing-plan` @ `6f77abb` (2026-08-30). Corpus read directly, not relayed:
`CLAUDE.md`, `.claude/notes/`, `.claude/roles/`, `.claude/skills/` (directory listing),
`docs/process/`, `docs/plans/README.md`, `docs/roadmap.md`, `docs/open-questions.md`,
`docs/audit/register.md`. Recorded here because a proposal whose citations were never
checked is a proposal about an imagined repository — and because four of the draft's own
claims were wrong.

### 9.1 Corrected in the draft before filing

| # | Wrong in the draft | Correct at `6f77abb` |
|---|---|---|
| 1 | Note number `NT-0012` | `0012` and `0013` are taken; next free is **`0014`**. Applied throughout |
| 2 | "`CLAUDE.md` §12 points at the process spec" | The pointer is **§15** (`CLAUDE.md:292`). §12 is Skills (`:197`). Impact-matrix row 1 retargeted |
| 3 | A separate "gates" section in `CLAUDE.md` | There is none. The full gate lives in **§11 Commands Reference**, which also carries the "Python-only gate green while frontend red" warning (`CLAUDE.md:185-186`). Row 2 retargeted |
| 4 | Q3 asked where hooks are wired, blind | At this tree there is **no `.claude/settings.json` and no `.claude/hooks/`**; a top-level `scripts/` exists, with `scripts/audit-docs.py` as precedent (`docs/roadmap.md:33` cites it as a phase-close instrument). Q2 is now an informed question with a proposed answer, still the decision-maker's to rule |

### 9.2 A pre-existing defect, reported upward and not folded in

**`docs/process/delivery-process.md:5` mis-cites `CLAUDE.md`.** It reads *"This document is
the process specification `CLAUDE.md` §12 points at"*. At `6f77abb` §12 is **Skills**
(`CLAUDE.md:197`); the section that points at the process spec is **§15** (`:292`). The
process specification's own back-reference to its governing document is wrong.

This is **not this proposal's defect** and is filed rather than silently corrected — a
silent fix inside a proposal PR would destroy the record of which document was believed,
which is the thing `CLAUDE.md` §0 says a governed system cannot afford to lose. The
correction is two characters and belongs in its own change.

**It is also the proposal's best evidence.** The drift check (C4 in §2) exists precisely to
catch a stale cross-reference between the extract and the markdown; a citation check of the
same family, pointed at `CLAUDE.md`, would have caught this one the day the section numbers
moved. A motivating example found *inside the document being mechanized*, by the routine act
of checking the proposal, is stronger than an argued one.

### 9.3 Verified correct — citation to repository reality

- The uploaded spec is byte-identical to `docs/process/delivery-process.md` (`diff` clean).
- "`CLAUDE.md` §1 (Mission)" → `## 1. Project Mission` (`:35`). ✓
- "`CLAUDE.md` §4" for `wf-01…05` → §4 Documentation Suite names them (`:95`). ✓
- "`CLAUDE.md` §9's phase concept" → `## 9. Roadmap` (`:134`). ✓
- "`CLAUDE.md` §11 … Python-only gate" → present in §11 (`:185-186`). ✓
- "`CLAUDE.md` §13's reference rule" → §13's bullet *"A reference carries its scope and its
  measurement"* (`:260-264`, citing `NT-0004`). ✓
- All seven role files exist in `.claude/roles/` — lead, planner, decision-maker, auditor,
  executor, watcher, reporter. ✓
- All cited skills exist: `writing-plans`, `close-workstream`, `phase-review`,
  `dispatching-parallel-agents`. ✓
- All cited artifacts exist: `docs/process/agent-settings.md`, `docs/plans/README.md`,
  `docs/open-questions.md`, `docs/audit/register.md`, `docs/roadmap.md`. ✓
- The rulings record `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md` exists;
  the W11 plan family confirms the Work/Slice naming the appendix's runtime-state example
  uses. ✓

### 9.4 What was *not* checked, and would need to be before adoption

Stated so a later reader cannot mistake this section's coverage for completeness:

- **No script in §2's C1–C5 was prototyped.** Every claim about what they would catch is a
  design claim, not a measurement. `CLAUDE.md` §13's standard — *enforcement is proven on
  deliberately broken input* — is unmet by construction here, and §8's acceptance items (c)
  and (d) exist to meet it at adoption rather than now.
- **The 22 impact-matrix rows were checked for existence, not for content.** Each target
  file exists; whether the proposed sentence fits what that file currently says was not read
  row by row.
- **No sizing.** Nothing here estimates the work, and the §5 breadth suggests the estimate
  matters more than the design does.

---

## 10. Appendix — draft companion artifact, unadopted

The proposed `docs/process/delivery-process.core.json` (artifact A of §2), reproduced here
rather than filed at its proposed path. **It is a draft under proposal and is authoritative
over nothing** — its own `meta` says so, and §3's authority rule governs it. `source` fields
cite `docs/process/delivery-process.md` sections verified at `6f77abb`.

It lives in this note because a proposal separated from the artifact it proposes is not
reviewable, and because the alternative — writing it to `docs/process/` — would be the
adoption itself.


```json
{
  "meta": {
    "id": "delivery-process-core",
    "version": "1.0.0",
    "derived_from": "docs/process/delivery-process.md",
    "verified_against_tree": "6f77abb52a3c97f93261dcde5b04265fc97a9279",
    "authoritative": false,
    "note": "The markdown spec is authoritative. This file is the mechanical extract: state machine, guards, vocabularies, and runtime-state schema for hooks/watcher scripts. Regenerate or diff-check against the md on every spec change (NT-0014 script C4).",
    "spec_adopted": "2026-08-29"
  },

  "vocabularies": {
    "plan_gate_decision": ["replan", "proceed", "escalate_parent"],
    "audit_verdict_proposal": ["fix", "accept", "defer"],
    "lead_verdict_action": ["adopt", "amend", "reject"],
    "finding_decision": ["fix_before_close", "accept_with_instrument", "carry_forward_named_owner_or_trigger"],
    "interrupt_class": ["critical", "queued_to_next_touchpoint"]
  },

  "roles": {
    "lead": {
      "authority": ["plan_gate_decision", "lead_verdict_action", "merge"],
      "definition": ".claude/roles/lead.md",
      "source": "\u00a73, \u00a75.4, \u00a75.7"
    },
    "planner": {
      "authority": ["write_map_plan", "write_slice_plan"],
      "must_include": ["acceptance_standard"],
      "definition": ".claude/roles/planner.md",
      "source": "\u00a73"
    },
    "decision_maker": {
      "authority": ["rule_decision_points", "rule_spec_vs_code_conflicts"],
      "not_authority": ["audit_verdicts"],
      "definition": ".claude/roles/decision-maker.md",
      "source": "\u00a73, \u00a75.7"
    },
    "auditor": {
      "authority": ["propose_audit_verdict"],
      "constraints": ["fresh_context", "never_fixes", "report_only"],
      "definition": ".claude/roles/auditor.md",
      "source": "\u00a73"
    },
    "executor": {
      "authority": ["implement_tdd", "commit", "open_pr"],
      "constraints": ["slice_layer_only", "never_self_merges"],
      "definition": ".claude/roles/executor.md",
      "source": "\u00a73, \u00a76.7"
    },
    "watcher": {
      "type": "support_mechanical",
      "constraints": ["report_only", "deterministic_no_llm_core"],
      "publishes": "roster-state.md",
      "definition": ".claude/roles/watcher.md",
      "source": "\u00a73, \u00a713"
    },
    "reporter": {
      "type": "support_mechanical_first",
      "constraints": ["reads_watcher_files_only", "never_polls_agents"],
      "definition": ".claude/roles/reporter.md",
      "source": "\u00a73, \u00a713"
    }
  },

  "hierarchy": {
    "order": ["project", "phase", "work", "slice"],
    "children_execution": "strictly_sequential",
    "source": "\u00a74, \u00a78"
  },

  "layers": {
    "project": {
      "child": "phase",
      "flow": "map_layer_flow",
      "enter_variant": "one_time_explore_not_repeated_on_replan",
      "escalate_parent_available": false,
      "human_checkpoint_at_close": true,
      "retry_cap": 1,
      "source": "\u00a72, \u00a75, \u00a77"
    },
    "phase": {
      "parent": "project",
      "child": "work",
      "flow": "map_layer_flow",
      "escalate_parent_available": true,
      "human_checkpoint_at_close": true,
      "retry_cap": 1,
      "source": "\u00a72, \u00a75, \u00a77"
    },
    "work": {
      "parent": "phase",
      "child": "slice",
      "flow": "map_layer_flow",
      "escalate_parent_available": true,
      "human_checkpoint_at_close": true,
      "retry_cap": 1,
      "source": "\u00a72, \u00a75, \u00a77"
    },
    "slice": {
      "parent": "work",
      "child": null,
      "flow": "slice_tdd_flow",
      "unit_definition": "one_tdd_leaf_one_pr_one_audit_one_gate",
      "disambiguation": "a plan '## Slice N' heading is a task grouping, NOT this unit; each task under it is its own process-slice",
      "escalate_parent_available": true,
      "human_checkpoint_at_close": false,
      "close_condition": "clean_audit_and_lead_merge",
      "retry_cap": 2,
      "retry_cap_status": "not_settled_ceiling",
      "source": "\u00a72, \u00a74, \u00a76, \u00a77"
    }
  },

  "flows": {
    "map_layer_flow": {
      "applies_to": ["project", "phase", "work"],
      "source": "\u00a75",
      "steps": [
        { "id": "enter", "actor": "lead", "action": "load_parent_context_and_relevant_findings" },
        { "id": "map_plan", "actor": "planner", "action": "break_into_children", "required_fields": ["acceptance_standard"] },
        { "id": "resolve_open_questions", "actor": "decision_maker", "gate": "all_open_questions_resolved" },
        { "id": "plan_gate", "actor": "lead", "decision": "plan_gate_decision",
          "checks": ["resolution_sound", "acceptance_standard_explicitly_defined_not_implied"],
          "transitions": {
            "replan": { "to": "map_plan", "guarded_by": "retry_cap" },
            "escalate_parent": { "to": "parent.map_plan", "unavailable_at": ["project"] },
            "proceed": { "to": "process_children" }
          }
        },
        { "id": "process_children", "action": "invoke_child_flow_per_child", "mode": "strictly_sequential" },
        { "id": "audit", "actor": "auditor", "scope": "this_layers_own_drift_level_only" },
        { "id": "verdict", "proposer": "auditor", "proposal": "audit_verdict_proposal",
          "decider": "lead", "decider_action": "lead_verdict_action",
          "transitions": {
            "fix": { "to": "map_plan", "guarded_by": "retry_cap" },
            "accept": { "to": "close_out" },
            "defer": { "log_to": "findings_register", "then": "close_out" }
          }
        },
        { "id": "close_out",
          "transitions": {
            "phase_or_work": { "to": "parent.process_children.next" },
            "project": { "to": "human_checkpoint" }
          }
        }
      ]
    },
    "slice_tdd_flow": {
      "applies_to": ["slice"],
      "source": "\u00a76",
      "steps": [
        { "id": "slice_plan", "actors": ["planner", "decision_maker", "lead"], "same_gate_pattern_as": "map_layer_flow.plan_gate", "escalate_parent_target": "work.map_plan", "required_fields": ["scope", "acceptance_standard"] },
        { "id": "write_test_red", "actor": "executor", "input": "acceptance_standard" },
        { "id": "implement_green", "actor": "executor" },
        { "id": "verify_refactor", "actor": "executor", "gate": "full_local_gate_green",
          "enforcement": "instruction_only_hook_not_built",
          "transitions": { "failure": { "to": "implement_green", "guarded_by": "retry_cap" } }
        },
        { "id": "slice_audit", "actor": "auditor", "scope": "implementation_level_drift_vs_slice_plan" },
        { "id": "verdict", "proposer": "auditor", "proposal": "audit_verdict_proposal",
          "decider": "lead", "decider_action": "lead_verdict_action",
          "transitions": {
            "fix": { "to": "implement_green", "guarded_by": "retry_cap" },
            "accept": { "to": "commit" },
            "defer": { "log_to": "findings_register", "then": "commit" }
          }
        },
        { "id": "commit", "actor": "executor", "constraints": ["small_working_commit", "pr_opened", "never_self_merged"] },
        { "id": "return_to_work", "signals": "slice_complete" }
      ]
    }
  },

  "guards": {
    "retry_caps": {
      "status": "instrumented_defaults_not_permanent_governance",
      "values": { "project": 1, "phase": 1, "work": 1, "slice": 2 },
      "on_breach": {
        "action": "pause_and_notify_human",
        "redirect": "same_layer_map_plan_or_implement_at_slice",
        "scope": "does_not_stop_whole_project"
      },
      "instrumentation": ["log_every_replan_iteration", "log_every_audit_fix_iteration", "log_per_slice_reaudit_count", "log_gate_reruns"],
      "revisit_when": "one_workstreams_worth_of_data_exists",
      "source": "\u00a77"
    },
    "parallelism": {
      "rule": "no_two_children_of_same_layer_concurrently",
      "protected_interest": "resource_contention_not_plan_stability",
      "plan_independence_is_not_an_exception": true,
      "carve_out": {
        "allowed": "read_only_fanout_for_evidence_gathering_within_a_layer",
        "precedent_skill": "dispatching-parallel-agents"
      },
      "expensive_verification_protocol": {
        "before_start": "check_runtime_state_for_one_in_flight",
        "on_start": "announce_and_record_in_runtime_state",
        "prefer_existing_check": "ci_is_authoritative_full_gate_for_pushed_branches"
      },
      "source": "\u00a78"
    },
    "human_checkpoints": {
      "at_close_of": ["work", "phase", "project"],
      "never_at": ["slice"],
      "decider": "maintainer",
      "source": "\u00a72"
    },
    "message_discipline": {
      "max_words": 50,
      "must_cite_artifact_by": ["path", "pr_number", "task_id"],
      "reasoning_location": "durable_artifact_not_message",
      "gate_reports_must_name": ["command", "totals", "tree_or_sha"],
      "source": "\u00a715"
    }
  },

  "monitoring": {
    "model": "events_over_polling",
    "watcher_checks": ["threshold_compares", "mtime_staleness", "roster_diff", "hygiene"],
    "status_line": { "stale_after_minutes": 20, "on_stale": "nudge_lead", "on_unanswered": "reporter_critical_relay_and_treat_lead_as_dead_member" },
    "interrupts": {
      "critical": ["balance_crossing", "dead_member", "blocked_slice"],
      "queued": "everything_else_to_next_lead_touchpoint"
    },
    "source": "\u00a713"
  },

  "artifacts": {
    "findings_register": "docs/audit/register.md",
    "open_questions_log": "docs/open-questions.md",
    "roadmap": "docs/roadmap.md",
    "plans_dir": "docs/plans/",
    "process_spec": "docs/process/delivery-process.md",
    "agent_settings": "docs/process/agent-settings.md",
    "roles_dir": ".claude/roles/",
    "runtime_state_location": "handover_ops_area_outside_repo",
    "source": "\u00a79, \u00a710, \u00a713"
  },

  "runtime_state_schema": {
    "description": "Shape of the runtime state file the watcher/hooks maintain. Fixes the implicit-state gap: agents read position and counters here instead of reconstructing them from history.",
    "example": {
      "updated_at": "2026-08-30T14:00:00Z",
      "position": { "project": "gi-pricing-plan", "phase": "2", "work": "W11", "slice": "W11-S3", "flow_step": "implement_green" },
      "retry_counters": {
        "work:W11:replan": 0,
        "slice:W11-S3:fix_loop": 1
      },
      "pending_human_checkpoint": null,
      "in_flight_expensive_verifications": [
        { "what": "full_test_suite", "by": "auditor", "tree": "6f77abb", "started_at": "2026-08-30T13:52:00Z" }
      ],
      "escalations_open": []
    }
  }
}
```
