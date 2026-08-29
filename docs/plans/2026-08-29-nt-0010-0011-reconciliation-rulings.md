# NT-0010 / NT-0011 adoption — reconciliation and rulings (2026-08-29)

`workflow-design-proposal.md` (NT-0010) and its companion `agents-settings-proposal.md`
(NT-0011) are being adopted through the adoption procedure NT-0010 §15 itself specifies:
freeze the inputs (step 1, done — PR #313, `07ae047`), reconcile against every governing
document in force (step 2a, the auditor), then rule every numbered section adopt / amend /
reject in one dated record (step 2b — this file), before a dated implementation plan (step 3)
is written.

*(Corrected 2026-08-29, on Part A1's ruling landing while Part A2 was still open: the
original text here said steps 3 onward would not start until both of Part A's rows closed.
Practice was more precise than that sentence — `docs/process/delivery-process.md` and
`docs/process/agent-settings.md` (steps 3–4) were written and landed with the specific
sections that depend on an open row named and marked (`delivery-process.md:18`, `BLOCKED
pending Part A1`; `agent-settings.md:69,72`, `pending Part A2`), rather than the whole
document, or the whole step, waiting. That is the
accurate rule, stated once here rather than left implicit: **a section that depends on an
open row is named and blocked; everything else proceeds.**)*

**Evidence.** The auditor swept fourteen governing documents (`CLAUDE.md`, the skills the
notes bind, `docs/README.md`, `docs/audit/register.md`, `TEAM-STRUCTURE.md` is explicitly
**not** in that set — see Part D) and produced the full §-by-§ tables in Part C. Every
citation below that is load-bearing for a ruling was independently re-verified against the
tree at `origin/main` `07ae047` before being written down, including one correction to the
auditor's own finding (Part B, item 8) — a citation is not trusted twice removed from the
source, however careful the hand that gathered it.

**Form.** Two rows were reserved to the maintainer per `CLAUDE.md` §10 ("do not silently
pick a side on an open design choice"); every other numbered section of both documents got
a ruling immediately. **Both are now closed**, each carrying the maintainer's own dated
acceptance line: Part A1 (2026-08-29) and Part A2 (2026-08-29), below. Every section that
depended on one of these two rows was named and blocked exactly where it was used
(`docs/process/`, `.claude/roles/`) rather than the whole document or the whole step
waiting; those named sections are listed at the end of A1 and A2 respectively, for the
executor to resolve against this record rather than against this file's own prose.

---

## Part A — reserved to the maintainer (options + recommendation; not ruled)

### A1. NT-0010 §9 — the single human checkpoint

**The conflict, precisely sourced.** NT-0010 §9 puts exactly one human approval in the whole
system, at Project close; every other layer's audit-decision returns control to its parent
automatically. `CLAUDE.md` §13 (`CLAUDE.md:227-253`) is **silent** on who accepts a
workstream close — it never names an approver in so many words. The explicit textual rule
sits one section over: `CLAUDE.md:263-264` (§14) requires "an explicit maintainer acceptance
line with a date," stated for phase reviews specifically. Workstream-closure-needs-the-
maintainer is well-evidenced **standing practice** (W6b, W9, W10 all closed on the
maintainer's word, never the auditor's or the team's own verdict), not a §13 sentence a
literal read would catch. The gap is real either way: NT-0010 §9's single checkpoint would
let a Work-layer audit-decision close a workstream with nobody outside the team having seen
it.

**Options:**

- **(a) Reject §9 as written.** Keep the human checkpoint at Work close (i.e., at workstream
  close), and let Phase and Project close inherit it upward. §9's own underlying intent —
  escalation and routine acceptance are different things, and a routine layer transition
  should not page a human — survives; only the *layer* the checkpoint sits at moves.
- **(b) Adopt §9 as written**, and separately amend `CLAUDE.md` §13/§14 to make the *lack* of
  a per-workstream checkpoint the stated rule, retiring the standing practice.
- **(c) A hybrid**: Work-close accept/defer stays automatic as §9 proposes, but a defer that
  reaches the findings register (§8) always pages the maintainer, since that is the
  disposition most likely to carry unrecorded risk forward silently.

**Recommendation: (a).** It is the smallest change that keeps the standing, load-bearing
rule intact (closure acceptance is the maintainer's, unbroken across three real
workstreams) while adopting §9's genuine improvement — that escalation-on-stuck and
acceptance-of-done are different events and only the second needs a human, at every layer
that currently has one waiting for it. (b) discards a rule the record shows has never once
been bypassed without cost; (c) is a plausible middle position but invents a new
distinction (which defers "carry unrecorded risk") that neither document asks for.

**Maintainer acceptance: ruled 2026-08-29.** Verbatim, quoted rather than reasoned around —
this is the maintainer's own authority, not a decision-maker ruling: *"close a work stream:
maintainer only makes decision on work, phase and project close but not slice close."*

**What this decides.** The human checkpoint sits at **three** named layers — Work, Phase and
Project close — with the maintainer deciding at each. **Slice close is not the maintainer's**:
a slice closes on a clean audit and the lead's merge, exactly as it does today. **NT-0010 §9
is rejected as written**, on this ground, not amended into it: §9's "exactly one human
approval, at Project close" put the checkpoint at the wrong layer (and at only one of the
three the maintainer names), so the proposal's structure was wrong, not merely its wording —
recording it as rejected is the accurate description, where "amended" would imply the
maintainer's ruling is an edited version of §9 rather than an independent one that happens to
share (a)'s recommendation to reject the single-checkpoint reading. **This does not decide
Part A2** (below) — role-agent write authority to `docs/` is a separate question the
maintainer has not yet ruled, and nothing here should be read as bearing on it.

**Two things that make this stronger than a preference, on the record because a future
reader should have them, not just the outcome:**

1. **It formalises what already happens rather than changing it.** The lead merges slice
   PRs on a clean audit today; W6b, W9 and W10 each closed on the maintainer's word, never
   the auditor's or the team's own verdict (Part A1's own sourcing, above). The ruling
   writes an existing, previously-unwritten boundary down at three named layers — exactly
   the class of gap Part D (below) catalogues: real, consistently followed, and invisible to
   `audit-docs.py` or any governing skill until now.
2. **It survives the objection that would otherwise weaken it.** W9 closed on the
   maintainer's acceptance and still shipped incomplete: its own scope prose "names four
   sections totalling 26 requirements; it verdicted 24" (`docs/audit/plan-reviews.md:572`,
   plan review 7) — the closure record reported a completeness the repository did not have,
   on work the maintainer had already accepted. That is evidence the checkpoint does not
   catch scope gaps, which could read as evidence against having one. It is not: the
   checkpoint decides **whether work stops**, an authority question, while the mechanical
   scope audit derived from the spec (`scripts/scope-audit.py`, `close-workstream`'s own
   first step) is what is supposed to catch what was missed, and did not run completely at
   W9's close. Recording both halves matters because a reader who takes the checkpoint for
   a safety net will over-trust it exactly where W9 shows it does not act as one.

**What now unblocks, named so it is on the record rather than only in a message.**
`docs/process/delivery-process.md` §2 ("Human checkpoint — BLOCKED pending Part A1") can now
be written with this ruling's content — three named layers, Slice excluded, the maintainer's
line as its grounds. That edit is Task 5's A1 half and belongs to the executor, not to this
record.

### A2. Role agents that decide and write to `docs/` — NT-0010 §2/§4 item 2, bundled with NT-0011's auditor tool-scope (§2 "auditor") and the `.claude/agents/README.md` scope question

**The conflict, precisely sourced, in two parts that resolve differently — see Part B item
11 for the full argument; this row states the conclusion and the maintainer's actual
choice.**

**Part one — `.claude/agents/README.md`'s own dividing line does not currently reach role
agents**, on the text as it stands (`CLAUDE.md:200` frames that whole file as "the index...
for **the delegable specialists**"; the README's own content — title, opening contrast
between a skill and a subagent, every example — never contemplates a persistent team-role
session). **This part needs no maintainer ruling**: it is resolved in Part B item 11 as a
documentation-placement question (role-agent files should not be filed inside
`.claude/agents/`, precisely to avoid manufacturing the ambiguity a co-located file would
create), which is within the decision-maker's remit.

**Part two — `CLAUDE.md:216-219` is a different, independent sentence, and it is already
being violated in practice.** "Evidence is delegated, verdicts are not... the verdict stays
in the main thread: §13's four verdicts, §14's proposals, §0's decision..., slice design,
**every edit to `docs/`**." This sentence carries no clause limiting "the main thread" to
one Claude Code conversation plus its ephemeral subagents — a limitation that was true by
default when it was written (2026-08-23, before any team-of-peer-sessions architecture
existed) but is not stated. The auditor supplied evidence that needs no scope argument at
all: **PR #308 and PR #309 each committed literal edits to `docs/specs/03-rating-engine.md`
(a §5.2 signature amendment; a §5.1 row plus a DP6 note), authored and pushed by the
auditor role, not the lead.** Add to that: this record's own predecessor, PR #315, is a
decision-maker-authored edit to the same file, and the record you are reading is a
decision-maker-authored `docs/plans/` file. Under `CLAUDE.md:218`'s plain words, all of these
are "an edit to `docs/`" that was supposed to "stay in the main thread." The line has already
been crossed, repeatedly, unrecorded until now.

NT-0011's own "auditor" tool-scope contradiction (owns "closure records, register deferral
rows with named owners" — and "no edits") is the identical conflict wearing different
clothes, confirmed live: the auditor's own dispatch this session assigns it exactly those
write deliverables.

**Options:**

- **(a) Amend `CLAUDE.md` §12 to name the team-of-sessions architecture explicitly** and
  state, per role, what a role session may decide and write: planner → `docs/plans/`
  (frozen dated files); decision-maker → dated ruling records and spec changes; auditor →
  closure records, register rows, and correction PRs (never a frozen plan, never a merge).
  The four verdicts (§13), the phase-review proposal (§14), the code-vs-spec resolution
  (§0), slice design, and the merge stay the lead's alone — this narrows "the main thread"
  from "one conversation" to "the role charter that owns this class of decision," not to
  "anybody." Amend `.claude/agents/README.md`'s dividing line with one sentence stating it
  governs the delegable specialists catalogued there and does not extend to team-role
  sessions defined elsewhere (belt-and-braces, since Part B item 11 already keeps role files
  out of that directory).
- **(b) Reject the drift and restore the literal rule** — role sessions stop writing to
  `docs/` directly; every docs-facing output becomes a proposal the lead applies. This is a
  real option, not a straw one: it is what `CLAUDE.md:218` currently says, word for word.
  Cost: it reverses three workstreams of load-bearing practice (DP1–DP7, PRs #308/#309,
  #315) and adds a lead-mediated step to every ruling and every audit finding, which is
  exactly the volume the role split exists to keep off the highest-leverage, lowest-volume
  role.
- **(c) Split the difference by artifact type** — e.g., role sessions may write dated
  records and register rows (append-only, attributable, low blast-radius) but never edit an
  existing spec section in place (only the lead may land a `docs/specs/` diff). This would
  have blocked PR #308's actual §5.2 amendment and this record's own FR-RATE-22 citation fix
  (PR #315), so it does not describe current practice either — it is a third rule, not a
  ratification of one of the two already in tension.

**Recommendation: (a).** Current practice already needs this rule to be true, evidenced by
three real merged PRs across two roles; the alternative is to either stop doing something
that has produced good, audited work (b) or to invent a boundary nothing has actually
observed (c). Naming the boundary explicitly — per role, per artifact class — is what turns
an unrecorded drift into a decision, which is the entire point of ruling it rather than
quietly adopting the notes as written.

**Maintainer acceptance: ruled 2026-08-29.** Verbatim, quoted rather than reasoned around —
this is the maintainer's own authority: *"I assume that agents works involve change files
in docs, it must be allowed"* — then, presented with options, **"option 2"**: split the two
axes. Writing to `docs/` is unremarkable and allowed; *deciding* is bounded by charter. (The
full option set put to the maintainer was not relayed to this record beyond the selected
one and its refined text below; recorded as heard, not reconstructed.)

**The outcome substantially adopts recommendation (a)'s conclusion — role sessions may
decide and write within a stated boundary — by a different mechanism than (a) proposed.**
(a) suggested amending `.claude/agents/README.md`'s own text with one belt-and-braces
sentence. The ruling instead uses Part B11's placement answer (role files live in a
separate `.claude/roles/` directory, not `.claude/agents/`) to make that sentence
unnecessary: the two directories' dividing lines never overlap, so nothing in
`.claude/agents/README.md` needs editing. Recommendation (b) (reject the drift, restore the
literal rule) and (c) (split by artifact type) are not the path taken.

**The ruled `CLAUDE.md` §12 replacement text, as put to the maintainer and accepted:**

> **Evidence is delegated; authority is bounded by charter.** A subagent runs in its own
> context and returns a conclusion — what §10 asks for — and **skills outrank agents on
> procedure**. Two kinds of agent are governed differently:
> - A **delegable specialist** (`.claude/agents/`) gathers or verifies and **decides
>   nothing**. That directory's README is its dividing line.
> - A **role** (`.claude/roles/`) **decides what its own charter names and nothing else**,
>   and **writes the artifacts its charter names, including under `docs/`**. A spec change
>   still follows `.claude/skills/spec-change`; a requirement id is still permanent (§5).
>   **A question in no charter is the lead's.**
>
> Four things are never a role's:
> - **§13's four verdicts** and the **merge** — the lead's. An auditor *proposes*; the lead
>   adopts, amends or rejects before the record is filed.
> - **Acceptance of a Work, Phase or Project close** — the maintainer's. A Slice closes on a
>   clean audit and the lead's merge.
> - **A §14 plan review's acceptance line** — the maintainer's. The review itself is the
>   planner's to write, and binds nothing until dated.
> - **An amendment to what this file requires** — the maintainer's. Editing this file to
>   *point at* something already ruled is not an amendment.
>
> **Every decision lands as a dated artifact** — a ruling record, an audit record, a plan —
> never in chat.

**Record what moved, not just what was decided.** The clause this replaces named five
things staying in "the main thread": §13's four verdicts, §14's proposals, §0's decision,
slice design, and every edit to `docs/`. Two survive unchanged as the lead's (§13's
verdicts, the merge). **Three move to a named charter rather than being dropped, and a
reader must be able to see that they were relocated, not discarded:**
- **§14's proposals → the planner.** Safe because §14 already independently requires "an
  explicit maintainer acceptance line with a date" (`CLAUDE.md:263-264`) — the old §12
  clause was redundant with a rule that is both older and stricter, so moving authorship to
  the planner's charter changes who *drafts* the proposal, not who *accepts* it.
- **§0's spec-versus-code decision → the decision-maker.** This is this session's own
  established practice, evidenced by every ruling in Part B of this record and PR #315.
- **Slice design → the planner.** The plan (`docs/plans/`, frozen at its date) is exactly
  where slice design already lives in current practice; the old clause named the main
  thread only because no other charter existed to name.
- **"Every edit to `docs/`"** is replaced by charter-plus-`spec-change`, not removed
  outright: the `spec-change` skill's append-only-id and ten-section rules were always the
  actual safeguard against a bad edit, never the "main thread" clause — that clause
  restricted *who*, never *how*, and the *how* is unchanged.

**Flagged explicitly as the lead's drafting, not the maintainer's word — recorded here
because the axis it touches is precisely the one that must not be misattributed.** The
fourth "never" bullet's second clause — *"editing this file to point at something already
ruled is not an amendment"* — is the lead's own distinction, supplied to justify why PR
#325 (the `CLAUDE.md` pointer to `docs/process/`) needed no separate maintainer round-trip.
The maintainer accepted the §12 text as a whole; this specific reading of what counts as
"an amendment to what this file requires" was not independently confirmed word-for-word.
It stands as the lead's operating interpretation, open to the maintainer tightening it later
to "every `CLAUDE.md` edit" — recorded as attributed rather than presented as ruled, because
this is the one place in the whole record where putting words in the maintainer's mouth
would land on the exact question the ruling is about: what needs the maintainer.

**The conflict of interest, on the record rather than only in the lead's own head.** This
ruling ratifies the practice this team has already been running under — role sessions
deciding within charter and writing to `docs/` — and the lead both recommended adopting it
(option (a) above, and the framing put to the maintainer) and is a direct beneficiary: it is
the lead's own dispatch pattern, this session's own PRs (#315, #320, #322, #323, #329, and
this one), and the auditor's #308/#309 that the ruling retroactively legitimises. Naming
this is not a claim that the ruling is wrong — the evidence for it (Part B11, PRs #308/#309)
is independent of who proposed adopting it — but a reader auditing the adoption should not
have to infer the conflict from the pattern of PRs alone. **Binding on the §15 step 5
audit**: test the adopted rule against what this session actually did today, not only
against NT-0010/0011's proposal text, precisely because the person who benefits from a
lenient reading is also the one who drafted it.

**Not an ADR, and why.** This repository's ADRs record architecture — `pricing-core`
staying standalone, `model-schema`, the ZEN engine (`docs/adr/`). This ruling is process,
and the adoption is creating `docs/process/` as process's own home; filing it as an ADR
*as well* would be a fourth place the same rule lives, which is the exact failure `NT-0003`
already named for duplicated status. `CLAUDE.md` §12 points at `docs/process/`; neither
duplicates the other's content once the executor's edit lands.

**What now unblocks, named so it is on the record rather than only in a message.** Five
`docs/-write scope: pending Part A2` gates, all built in Task 5 ahead of this ruling and
correctly left blocked until now, can be resolved with this ruling's content:
`.claude/roles/decision-maker.md:16-19`, `.claude/roles/auditor.md:21`,
`.claude/roles/planner.md:18`, `.claude/roles/lead.md:18`, and
`docs/process/agent-settings.md:69,72`. (`.claude/roles/executor.md:11` is explicitly
unaffected — its scope is code and tests, not `docs/` policy content — and needs no change.)
That editing is Task 5's A2 half and belongs to the executor against this filed record, not
to this ruling.

---

## Part B — rulings (decision-maker's own; not reserved)

One ruling per **distinct issue**, pointing every source location that raises it at the same
ruling — NT-0011 items duplicate two of NT-0010's, and are not re-litigated separately.

### B1. NT-0010 item 3 — "no parallelism at any layer" must not forbid delegation

**Ruled: adopt §7 with an explicit carve-out** — sequential processing of a layer's
*children* (Project→Phase→Work→Slice, one at a time), unrestricted read-only fan-out for
*evidence gathering* within a layer.

The auditor found harder evidence than the §10-spirit argument this row started from:
`.claude/skills/README.md:75` lists **`dispatching-parallel-agents`** as an installed,
named-precedent skill — "Use when facing 2+ independent tasks that can be worked on without
shared state or sequential dependencies" (independently confirmed: it appears by that exact
description in this session's own available-skills listing, not only in the README's
citation of it). `CLAUDE.md:168` — the memory-cost rule from the model's own dispatch:
"delegate noisy investigation to a subagent... 73% of measured spend came from calls
carrying over 200k tokens" — is the same standing instruction. §7's own words ("not used at
any layer in this version... bounds context/resource usage per session") describe exactly
the failure mode delegation exists to prevent, so a literal reading forbids the mechanism
that would keep a layer's own context small. The carve-out preserves §7's real target
(sequential *child processing* — no two Slices run at once) while not forbidding a bounded,
read-only sweep inside one.

### B2. NT-0010 item 4 + NT-0011 item 2 — "ultracode" is not "ultrathink"

**Ruled: the decision-maker's effort setting is maximum extended thinking ("ultrathink"),
never the multi-agent `Workflow`-orchestration keyword.** One ruling; both notes' text
needs the same correction (NT-0010 §4's paragraph and NT-0011 §1's summary table / §2
decision-maker section all use the placeholder pending this ruling).

Verified independently against primary sources available in this session, not against
either note's own say-so: this session's own `Workflow` tool definition states plainly that
`ultracode` is the keyword that opts a session into multi-agent workflow orchestration; the
`code-review` skill's description separately names `ultra` as the effort level that
"launches a multi-agent cloud code review" — a different word, a different tool, gated by a
`--ultra` flag rather than a prompt keyword. Neither is the extended-thinking trigger.
`ultrathink` itself is not confirmable from a tool schema the way the other two are — it is
Claude Code product behaviour (the think / think hard / think harder / ultrathink
escalation), not a tool description string — so this ruling's confidence in that one word is
sourced differently from its confidence in the other two, and says so rather than blurring
the three together. Net: if "ultracode" had meant orchestration, the instruction would have
been to fan the decision-maker out across parallel agents — which B1's own §7 carve-out
does not extend to decision rulings (a ruling is a single judgement, not a parallelisable
evidence sweep) and which no decision point in W10 ever needed. Maximum thinking on a rare,
binding, cheap-to-think-hard-about action is the reading that survives.

### B3. NT-0010 item 5 + NT-0011 item 3 — retry caps and cost tiers are guesses; adopt as instrumented defaults, not governance

**Ruled: adopt both as instrumented defaults.** Log every replan/audit-fix loop iteration
and every per-slice re-audit count and gate re-run from the first slice under the new
process; revisit the numbers after a workstream's worth of data, not before.

NT-0010 §6 sets the Slice retry cap at ≤2. The auditor **independently reconfirmed** (not
merely re-cited the note) that W10-3A took exactly **two** re-audits before merging clean
(one found F-3A-3; the second went clean) — the only slice in the only workstream this
project can measure against sits precisely on the cap being proposed as a permanent number.
A cap fitted to the single hardest observed case will escalate the first time a slice is
marginally harder than the hardest one so far, which is fitting the sample, not choosing a
threshold. NT-0011's separate cost-tier question (should the executor really get the
cheapest model, on the argument that the auditor "catches what slips through") has the same
shape: the auditor's own W10 record shows several caught defects that each cost a full
re-audit (a frozen-model test-import bug, markerless API tests, two untested exclusion
faces, a contract left inconsistent by a rebase, a round-trip test asserting nothing) —
whether a cheaper executor is net-cheaper once re-audit cost is priced in is an empirical
question this project has the data to start answering and has not yet answered. Escalating
to a human on a retry-cap breach is cheap; a wrong permanent number is not self-correcting.
This is explicitly the one area both notes should be provisional rather than settled.

### B4. NT-0010 item 6 — the adoption procedure (§15) is adopted as written

**Ruled: adopt §15 literally**, as this record is already doing. Landing both documents by
writing them straight into `CLAUDE.md` in one pass would be exactly the `CLAUDE.md` §0
failure this project's own standard exists to prevent — building from a specification
nobody reconciled — and would breach NT-0003 (a process spec restating `CLAUDE.md` §§12–14
rather than superseding them creates a fourth place status can go stale). No amendment
needed; §15's own text already requires the section-by-section adopt/amend/reject verdict
this record delivers, requires pre-resolving decisions before anything is built (Part A/B),
and requires a pilot before the standard is declared (deferred to §15 step 6, after
implementation).

### B5. NT-0011 item 4 — model names, and the lead's unenforceable model row

**Ruled, two parts.**

- **Model names, pinned now rather than left to drift:** in this environment, `opus` →
  Opus 5, `sonnet` → Sonnet 5, `haiku` → Haiku 4.5. A fourth tier, **Fable 5**, exists
  (confirmed directly: the `Agent` tool's own `model` parameter enum in this session is
  `sonnet | opus | haiku | fable`) and neither note considered it. No role is reassigned to
  it by this ruling — the volume-vs-leverage logic in NT-0011 §1 already covers the four
  roles that need a model choice, and Fable's fit is a separate question nobody has raised —
  but the settings document should record that the option exists rather than silently omit
  a real fourth tier.
- **The lead's model row is corrected, not merely restated:** the lead is the main
  thread; its model is whatever the session was started with, not a setting a role file can
  enforce (a role *file* can bind a decision-maker or planner's model at spawn time because
  those roles are spawned; the lead is not spawned, it is the session). NT-0011 §2's lead
  row should say so explicitly rather than read as a setting that will be silently unmet the
  first time a session starts on a different model than the row names.

### B6. New — the naming collision: `docs/process/workflow.md` reuses a defined term

**Ruled: NT-0010's suggested filename is rejected; the adopted document must not be named or
titled "workflow."** Placement and naming were already explicitly left open by NT-0010's own
text ("a suggestion only; placement and naming remain the project's decision"), so this
ruling exercises exactly the discretion the note reserved for this step — it does not
override anything the note asked to be settled elsewhere.

`CLAUDE.md:96,98` (§4) already defines "workflow" as a specific, existing artifact class:
"`workflows/wf-01…05` are the **cross-module journeys** — dataset-to-model,
model-to-rating-version, rate-change impact, deploy-and-monitor, custom-objective
lifecycle. A module spec says what one module does; a workflow says what actually happens
across all of them." `docs/README.md:18` lists `workflows/` the same way. The development
process being adopted here is an unrelated concept — it describes how a Claude Code team
does the work, not what happens across pricing modules — and reusing the word for both
would break the glossary rule (`.claude/skills/spec-change`: "a new term goes in the
glossary before first use anywhere") the moment a reader tries to find "the workflow" and
gets two unrelated documents. The exact replacement name is not ruled here — it is exactly
the open placement/naming decision NT-0010 already deferred — except that "workflow" itself,
singular or plural, is excluded from it.

### B7. New — `writing-plans/SKILL.md` still contains four literal `superpowers:` namespace references

**Ruled: fix the four references in the same adoption pass that lands NT-0010, before or
alongside §15 step 3's plan.** This is a defect in the currently-governing file, not in
either note — both notes correctly assert "no plugin installation, no `superpowers:`
namespace is involved," and the vendored skill itself disagrees with that true statement.

Verified directly (`grep -n 'superpowers:' .claude/skills/writing-plans/SKILL.md`): four
hits — `superpowers:using-git-worktrees` (line 16), `superpowers:subagent-driven-development`
(lines 64, 169), `superpowers:executing-plans` (line 173). `docs/plans/README.md:33` shows
the correct bare form ("Use the project skill `subagent-driven-development`... or
`executing-plans`"), confirming what the stale file should say. NT-0010 §11 obligation 1
("bind its executor — a header directive naming the required execution skill... with
checkbox step tracking") depends on a plan citing a name that actually resolves; a plan
that copies `writing-plans/SKILL.md`'s own stale self-reference would mint a fifth
occurrence of the same defect. Fix source: `.claude/skills/writing-plans/SKILL.md` itself,
not the notes, and not by re-deriving the bare names — `docs/plans/README.md:33` already
states them correctly.

### B8. New — NT-0010 undercounts `.claude/agents/`: seven specialists, not eight

**Ruled: seven is authoritative. NT-0010's "already in force" section (`0010-…md:58-59`,
"`.claude/agents/` holds **eight** delegable specialists") is corrected in place, dated,
without re-litigating anything the miscount was cited to support** — nothing else in either
note's argument turns on the exact count.

Verified by direct directory listing (`ls -la .claude/agents/`): seven specialist files
(`accessibility-tester.md`, `ci-watcher.md`, `evidence-collector.md`, `gate-runner.md`,
`performance-engineer.md`, `postgres-pro.md`, `spec-reconciler.md`) plus `README.md` — eight
files total in the directory, seven of them specialists. `.claude/agents/README.md:184`
("Last verified: all **seven**") already states the correct count; the miscount reads as a
directory listing that included its own README as an eighth entry. Recording this as the
correction of an error in a merged note (`CLAUDE.md` §12: "a skill that turns out to be
wrong is fixed in the same session it is found wrong" — applied to a note the same way),
not as a new finding about the repository.

### B9. New — the two notes give the lead different tool scopes, and neither flags it

**Ruled: NT-0011's version is authoritative; NT-0010 §2's lead row is corrected to match
it.** NT-0011 matches confirmed practice (this session's own PR-only-plus-lead-merge
experience, `TEAM-STRUCTURE.md`'s table); NT-0010's is silently narrower in one direction and
silently wider in another, which is worse than simply wrong, because both readings could be
separately adopted without either author noticing the other moved.

Verified precisely: NT-0010 §2 (`0010-…md:239`), Lead's suggested tool scope — "Read-only
(Read, Grep, Glob) + write access to plan/map files only." No merge authority anywhere in
that row. NT-0011 §2 "lead" (`0011-…md:210`), Tools — "full read; git merge authority;
write to handover/status files only." No plan/map-file write anywhere in that row, and merge
authority added. The corrected, single row: full read; **git merge authority** (sole merge
authority per current practice); write to **handover/status files** — not to plan/map files,
which NT-0011's own division of labour already gives to the planner role, matching this
session's own experience of what each role actually writes.

### B10. New — NT-0011's decision-maker incident citation: sound, but sourced wrong by the auditor's own check, and durable nowhere

**Ruled, in three parts, because the evidence trail here has three different actors each
partly right.**

1. **NT-0011's citation is factually accurate.** Re-verified directly against
   `w10-handover-2026-08-28/TEAM-STRUCTURE.md` (read in full, not sampled) rather than taken
   on the lead's relay: line 15's role table — "STOPPED 12:54Z — duties complete... stopped
   after a **third** cross-worktree write despite the **stop order**"; lines 166–168 —
   "decision-maker's 12:40Z checkouts into **both** executor worktrees, which **discarded
   executor's uncommitted 3B files**; recovered from job-dir copies." Three writes, a stop
   order defied, tracked files discarded — every element of NT-0011's sentence ("the
   decision-maker wrote into the executor's worktree three times despite a stop order, and
   the third write discarded the executor's tracked files") is present, precisely, in this
   source.
2. **The auditor's Priority-1 finding that the citation "doesn't match" is itself a
   near-miss, not a real conflict — corrected here rather than adopted.** The auditor
   checked `auditor-state.md` and found a *different*, real incident there — the auditor's
   own single cross-worktree write, caused by session re-pinning, with no stop-order
   narrative. `TEAM-STRUCTURE.md:166` names **both** incidents in the same clause ("enforced
   after TWO incidents — auditor's W10-1 juggling, decision-maker's 12:40Z checkouts...");
   `auditor-state.md` naturally only carries a record of the auditor's own half of that pair,
   because it is the auditor's own state file. Checking it for the decision-maker's incident
   was checking the wrong log, not evidence against the claim. NT-0011's sentence is
   specifically about the decision-maker's incident, and that incident is exactly as
   described.
3. **The deeper point both the lead and the auditor made survives this correction
   completely, and is the one this ruling actually acts on: the citation's only source is a
   file outside this repository.** `TEAM-STRUCTURE.md` lives at
   `/home/puzhenhao1989/w10-handover-2026-08-28/`, is explicitly excluded from the auditor's
   swept governing set, and per this project's own standing convention (memory:
   "handover files stay local... never pushed to the repo root") is not meant to persist at
   all. This is `NT-0005`'s "deferred items with no durable custody" failure, committed by
   the very notes that elsewhere cite `NT-0005` as their own justification for writing the
   process down.

**Fix:** NT-0011's assessment prose (its "already in force" section, the sentence
introducing the decision-maker's hard boundary) gains the correct, honest citation now —
naming `TEAM-STRUCTURE.md` and stating plainly that it is an external, non-durable source —
landed in this commit (see the note edit below). **The durable fix is named, not built
here:** when the decision-maker's role-agent settings document is written (§15 step 4, after
this record and the implementation plan), it states this incident as its own sourced
justification for the "no write access to any code worktree" boundary, in-repo, so the
citation no longer depends on a file that dies with a session.

### B11. The scope question — resolved, not averaged

Two real texts, two different questions, and they resolve differently. Presented as the
auditor and the decision-maker each argued it, then ruled.

**Reading 1 (decision-maker).** `.claude/agents/README.md`'s "every agent here... none of
them decides" (`README.md:16-18`) does not currently reach role agents. `CLAUDE.md:200`
frames the whole file as the index "for the delegable specialists"; the README's own content
never once contemplates a persistent team-role session as a category — its opening
paragraph draws exactly one distinction ("a subagent is not a skill... a subagent runs in
its own context and returns only a conclusion"), a description that is definitionally false
of a role session like this one (I am not ephemeral, I do not return only a conclusion, I
run on a roster addressed by name). "Here" reads as "in this catalogue of seven," not "in
this filesystem directory, regardless of what is later placed in it."

**Reading 2 (auditor).** The README's dividing line is self-titled "**the** dividing line"
— normative framing, not mere description — and NT-0010 §10 explicitly mandates placing
role-agent files in that exact directory. Once that placement happens, "every agent here"
functionally reaches them by the plain, undecorated words of the rule, whatever the
document's original authorial intent was.

**Ruled: both readings are right, about two different things, and the record should say so
rather than pick one winner.** Reading 1 is correct about the text **as it stands today** —
no role-agent file exists in `.claude/agents/` yet, and on the words actually written, the
rule does not reach one. Reading 2 is correct about **what NT-0010 §10's adoption would
create** — the moment a role file is filed in that directory, the ambiguity Reading 2 warns
of becomes real, because the directory would then hold two categories of file under one
undifferentiated dividing-line sentence. The resolution is not to force a verdict on which
reading a still-hypothetical file would face; it is to **not create the fork in the first
place**: **role-agent definition files are ruled to belong outside `.claude/agents/`**
(a distinct location — e.g. a new `.claude/roles/`, mirroring the pattern that already
separates `.claude/skills/` from `.claude/agents/` on the same not-a-skill/not-a-subagent
logic the README's own opening line draws). This dissolves Reading 2's concern at its root
rather than editing a rule that Reading 1 shows was never actually violated.

**What this does *not* dissolve, and where the auditor's sharper evidence lands instead:**
whether a role session, wherever its definition file lives, may decide and write to
`docs/` is a **separate** question from where its file sits, and it is answered by
`CLAUDE.md:216-219` — a sentence with no directory scope and no self-limiting clause at all
— not by `.claude/agents/README.md`. That sentence's plain words have already been crossed,
independent of any scope argument: **PR #308 and PR #309 committed literal edits to
`docs/specs/03-rating-engine.md`, authored and pushed by the auditor role.** This is Part
A2's actual substance, and it is why Part A2 amends `CLAUDE.md` §12, not
`.claude/agents/README.md` — the rule that is broken and the rule that was never reached are
two different rules, and only one of them needs the maintainer's hand.

---

## Part C — full section reconciliation

Every numbered section of both source documents, adopt / amend / reject. Auditor's evidence
column condensed from the full step 2a table; ruling column is this record's, building on
but not identical to the auditor's proposed classification where Part B rules otherwise.

### NT-0010 — workflow proposal

| § | Proposal | Governing text (swept set) | Auditor found | **Ruled** |
|---|---|---|---|---|
| 1 Purpose | 4-layer hierarchy; one human checkpoint at Project | No "process" doc category exists in `docs/README.md`; process rules live only in `CLAUDE.md` prose | Silent (new category) | **Adopt** — closes the exact custody gap `NT-0005` named, one level up |
| 2 Roles | decision-maker decides; auditor "never fixes... read-only" | `.claude/agents/README.md:16-18`, `CLAUDE.md:216-219` | Conflicts, confirmed | **Amend** — Part A2 (maintainer), informed by Part B11 |
| 3 Hierarchy | Project→Phase→Work→Slice | Phase (`CLAUDE.md` §9), Work≈workstream, Slice all exist and are used exactly this way; "Project" (the whole platform effort) has no formal artifact — `roadmap.md` is organised per-phase | Phase/Work/Slice agree; Project silent | **Adopt** — Project is the whole-repository scope `CLAUDE.md` §1 (Mission) already names informally; no new artifact required, only the label |
| 4 Per-layer flow | decision-maker owns the audit fix/accept/defer decision | Same §12/README conflict as §2; **also** superseded by NT-0011 §3 delta 1's own correction | Conflicts, self-corrected by the companion | **Amend** — adopt NT-0011 §3 delta 1's version: auditor proposes, lead adopts/amends/rejects and merges, decision-maker rules DPs/spec only |
| 5 Slice layer | TDD cycle; step 6 repeats the §2/§4 issue; step 4 assumes a blocking hook | `test-driven-development` / `python-test` skills agree on the cycle; no governing document describes an enforcement *hook* — only an instruction | Cycle agrees; step 6 conflicts (same root); hook unbuilt | **Adopt** the cycle and B-item-4's fix for step 6; **note, not rule**: the hook is an implementation gap for §15 step 4, not a document conflict |
| 6 Escalation caps | ≤1 Project/Phase/Work; ≤2 Slice | No governing cap exists anywhere; analogous to §13's "measured, not asserted" | Silent on the number; sound in kind | **Adopt as instrumented default** — Part B3 |
| 7 Parallelism | none at any layer | `CLAUDE.md:168` (delegate noisy investigation); `dispatching-parallel-agents` skill (`.claude/skills/README.md:75`) exists and is precedent-bearing | Conflicts | **Amend with the carve-out** — Part B1 |
| 8 Findings register | skeleton + decision taxonomy | `docs/audit/register.md` — verbatim match, including the literal "fix before close" wording (`register.md:14`) | Agrees, reconfirmed | **Adopt as-is** |
| 9 Human checkpoint | only at Project close | `CLAUDE.md:263-264` (§14, explicit, phase-review-scoped) + standing practice (§13 itself silent) | Conflicts with §14 + practice | **Reject as written** — Part A1 (maintainer) |
| 10 Required artifacts | `docs/process/`, role files under `.claude/agents/`, six named skills | `docs/README.md` has no process row (confirmed absent); all six skills confirmed present by their registered names | Accurate, modulo naming | **Adopt**, with the naming fix (Part B6) and the placement fix (Part B11 — role files do not go in `.claude/agents/`) |
| 11 Plan file obligations | binds `writing-plans` conventions; states "no plugin namespace involved" | `docs/plans/README.md` corroborates the conventions strongly; **`writing-plans/SKILL.md` itself still says `superpowers:`** (4 hits) | Notes correct in substance; vendored file stale | **Adopt**; fix the four stale references in the same pass — Part B7 |
| 12 Audit record obligations | pin/scope/divergence/verdict/judgment/table/notes/sign-off | `close-workstream` skill and both existing closure checklists match closely, including the literal "silence is never a verdict" language | Agrees strongly | **Adopt as-is** |
| 13 Open items for next iteration | self-flagged out of scope | N/A — the section says so itself | Silent by its own design | **N/A this round** — carried to the next iteration as the note already intends |
| 14 Monitoring & comms loop | watcher/reporter mechanics, escalation ladder, mechanical-first | **None** of the fourteen governing documents describe any of this | Silent in the governing set | **Adopt** — this section *is* the custody gap; see Part D |
| 15 Adoption workflow | freeze→reconcile→plan→implement→audit→pilot→close | Matches `CLAUDE.md` §0's phase-and-spec discipline; this document is step 2 of it | Agrees | **Adopt as-is** — Part B4 |

### NT-0011 — agent settings companion

| § | Proposal | Governing text (swept set) | Auditor found | **Ruled** |
|---|---|---|---|---|
| 1 Summary table | per-role model/effort/skill/spawn; flags "ultracode" for confirmation | Independently verifiable from this session's own tool schemas | Correction needed, confirmed | **Adopt**, ultracode ruled per Part B2 |
| 2 lead | opus/high; owns merges+verdicts; writes handover/status only | No governing document states lead merge authority anywhere; **disagrees with NT-0010 §2's own lead row** | Silent in the governing set; real inter-note conflict | **Adopt** (matches confirmed practice) — corrected against NT-0010 §2, Part B9; merge authority itself stays **silent** pending Part A2, not "agrees" |
| 2 planner | opus/high; writes `docs/` plan files only | Same `CLAUDE.md:216-219` question as §2/roles | Conflicts (same root as NT-0010 §2/§4) | **Amend together with Part A2** — not a second, separate ruling |
| 2 decision-maker | opus/ultrathink; no code-worktree write access; cites a W10 incident | The write-free rule is corroborated (one passing log line); the incident citation needed re-sourcing | Rule sound; citation needed a fix | **Adopt the boundary; fix the citation** — Part B10 |
| 2 auditor | sonnet/high; owns closure records + register rows; tool scope says "no edits" | Same `CLAUDE.md:216-219` contradiction, confirmed live by this session's own dispatch to the auditor role | Conflicts, strongly confirmed | **Amend together with Part A2** |
| 2 executor | sonnet/medium | TDD/gate mechanics confirmed by the bound skills; the cost tier is the open question | Agrees on mechanics | **Adopt as instrumented default** — Part B3 |
| 2 watcher | script + haiku-on-anomaly; owns `roster-state.md` | Same silence as NT-0010 §14 | Silent in the governing set | **Adopt** — closes the same gap, Part D |
| 2 reporter | script + haiku for critical relay / nudge | Same silence | Silent in the governing set | **Adopt** — closes the same gap, Part D |
| 3 Deltas (6 items) | verdict split; frozen plans; PR-only + lead-merge; re-audit rule; per-slice audit axes; worktree-collision rule | **All six independently reconfirmed this session** against the spec-change skill, git-hygiene skill, close-workstream skill's literal text, this session's own per-slice audit dispatch, and this session's own `pwd`/branch discipline | Agrees strongly — the best-evidenced section in either document | **Adopt as-is** |
| 4 Open items | confirm ultracode; confirm skill names; watcher/reporter cost; tune effort on burn data | Self-referential — names this reconciliation step as where each gets settled | N/A | **Resolved by this record**: ultracode → Part B2; skill names → confirmed against `.claude/skills/README.md`'s registered set (all six present, bare names, no plugin namespace once Part B7 lands); watcher/reporter cost and burn-data tuning → **carried to §15 step 3** (the implementation plan), since both are "start cheap, measure, revisit" and nothing about them is decidable before a slice runs |

---

## Part D — silence, marked as silence

**The recurring pattern underneath most of Part C's "silent" cells.** Confirmed by direct
grep and read against the full swept set, not inferred from its absence: the following
carry **zero words in any governing document** — not `CLAUDE.md`, not any bound skill, not
`docs/README.md`, not `docs/audit/register.md`. Their only source is `TEAM-STRUCTURE.md`
(a handover file, outside the swept set by design) and this session's own memory notes
(user-session instructions, also outside it). Recording them as `silent` rather than
`agrees` is the point of this section — a rule that is real, consistent, and repeatedly
followed is still unrecorded until it is written where `scripts/audit-docs.py` or a bound
skill would ever see it, and that gap is the strongest form of both notes' own thesis.

1. **Lead merge authority.** "Merge" appears in the swept set only as *mechanism*
   (`CLAUDE.md` §11's commands, `git-hygiene`'s squash-merge/PR-flow procedure) — never as an
   assignment of *authority* to a named role. "Only the lead merges" is real and
   consistently observed (this session's own PR #315 and this record both went through PR
   review rather than a self-merge), but its only source is `TEAM-STRUCTURE.md` §5 and a
   memory note.
2. **The whole NT-0010 §14 / NT-0011 watcher-reporter mechanism** (roster-state.md as the
   single source of team state, the 20-minute nudge, the escalation ladder, watch-the-
   watcher). Zero mentions anywhere in the fourteen swept documents — confirmed by direct
   grep for "roster-state", "nudge", "escalation" returning no hits outside the two notes
   themselves. Matches `TEAM-STRUCTURE.md` §3 almost verbatim; that file is the only source.
3. **The decision-maker's write-free convention.** No governing document names a
   "decision-maker" role at all — role agents as a category exist nowhere in the swept
   fourteen, only the seven delegable specialists do (Part B8). There is therefore nothing
   for this convention to conflict *or* agree with; `silent` is correct here one level more
   fundamentally than items 1 and 2. The only corroboration on record is a single passing
   log line ("decision-maker-2 ruled write-free") in the W10 auditor's own state file —
   practice, observed once, never governance.

All three are real and worth adopting exactly as proposed (Part C marks each `Adopt`); the
point of naming them `silent` rather than `agrees` is that adoption is what gives them a
governing-document home for the first time, which is the custody gap both notes exist to
close.

---

## Verification

- `python3 scripts/audit-docs.py` — run clean before commit (this record cites no new
  `FR-`/`NFR-`/`ADR-` id; every requirement and note id it mentions already exists).
- Every route literal, line number, skill name and file:line citation above independently
  re-verified against `origin/main` `07ae047` before being written down, including one
  correction to the auditor's own Priority-1 finding (item B10) reached by checking the
  primary source directly rather than adopting a teammate's conclusion unread.
- `.claude/notes/0011-per-agent-model-and-skill-settings.md`'s decision-maker incident
  citation corrected in the same commit (Part B10) — the assessment prose, not the "Original
  wording" verbatim block, which stays untouched per the notes' own convention.
- Both notes' `Status` field stays `open`: Part A's two rows are not yet accepted, and
  `.claude/notes/README.md`'s own acceptance criteria are not met until they are.
