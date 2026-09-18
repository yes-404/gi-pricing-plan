---
id: PL-1071
family: plan
kind: leaf
title: W37-8 — Charters, agents, and their READMEs
status: draft
created: 2026-09-18
owner: planner
tree: a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-939, CR-1064, RFC-937]
---

# PL-1071 — W37-8: Charters, agents, and their READMEs

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax
> for tracking.

**THIS PLAN IS A DRAFT, AND STAYS A DRAFT.** `status: draft`. It was filed under the deputy's
ruling of 2026-09-18 00:41:53 BST (`~/gi-pricing-plan.local/channel/to-lead.md`, at or about
line 5295), condition (a): **drafting only**; that condition named two events to wait for.
**This correction pass, made under the deputy's later ruling of 2026-09-18 09:19, discharges
both — one by reconciling now rather than waiting, one because the event itself landed:**

1. **Plan review 13 still carries no dated maintainer acceptance line**, re-verified at this
   pass's own base tree: `grep -n 'Maintainer acceptance' docs/closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md`
   → `632:**Maintainer acceptance:** _pending_` at `d63f765085fe6eb1c594177c5779ecfc3caf7ae8`. Per
   the 09:19 ruling, review 13 is *"a FILED PROPOSAL — reconcile against it now, do not wait for
   its acceptance line"* — §4 below does exactly that, and this plan no longer waits on
   condition 1.
2. **W37-6's checkpoint 3 landed.** Its close record, `CR-1065`, is now on `main`:
   `git log --oneline -1 -- docs/closures/CR-01065-w37-6-checkpoint-3-close.md` →
   `d63f765 docs(closures): W37-6 checkpoint 3 — slice close record, register, roadmap row,
   ledger`, and it is byte-identical to the branch revision this plan was drafted against
   (`git diff origin/w37-6-checkpoint-3-close:docs/closures/CR-01065-w37-6-checkpoint-3-close.md
   origin/main:docs/closures/CR-01065-w37-6-checkpoint-3-close.md` → empty), so every line
   number §4.2 cites against it still resolves. Condition 2 is discharged.

**`created:` is the drafting date, not a freeze date.** The header field is mechanically
required to be an ISO date (`scripts/_docid.py:836-846`, `` `created` is not an ISO date
(YYYY-MM-DD) ``), so it cannot be left blank. **The freeze is carried by `status:` instead**,
which is the mechanism `docs/_templates/PL.md`'s own freeze rule uses: *"`status: active` is
permitted only when every blocking row in the Decision points table below has a resolver id in
its `Resolved by` cell"*. **DP-8.1 and DP-8.2 are still blocking and still carry no resolver**
— that disagreement is the lead's/decision-maker's to rule, not discharged by either of the
deputy's rulings above — so this plan stays `draft` by `§1.7`'s mechanical rule alone, and this
correction pass does not flip it: a `PL-` `active` with an open blocking decision point fails
`audit-docs.py` check 33.

**Frozen / dated:** _pending — set `status: active` only when DP-8.1 and DP-8.2 carry resolver
ids. Both waiting-on-an-event conditions above are now discharged; the remaining block is the
two decision points, which is exactly what `§1.7`'s freeze rule is for._

## Goal

Give the seven role charters under `.claude/roles/`, `.claude/agents/README.md` and
the agent files under `.claude/agents/` the RFC-937 header and the `document-ids.md` §1.6 role
content, so that the generated ownership matrix reports what each role actually owns, the two
roles that own nothing say so, and `.claude/agents/ci-watcher.md` — the one W37-8 file
`CR-1065` §2.4 found still carrying pre-migration content — is closed by a named commit.

## Architecture, stack and spec

**Architecture:** A leaf plan under the map plan
[`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`](PL-00939-wk-697-one-id-per-governed-thing-map-plan.md),
slice section `:760-784`, sequencing row `:377` (*"W37-8 | S3 | Charters, agents, and their
READMEs | `writing-skills` | W37-6 | W37-7, W37-9, W37-10"*). Every task is one file or one
file-class, because **DP-6 requires a dated maintainer line per charter edit** and a maintainer
can approve one charter while rejecting another. Nothing in this slice is generated; every edit
is hand-authored prose under a machine-checked header.

**Tech Stack:** No runtime code. Markdown + YAML front matter; the checking instruments are
`scripts/audit-docs.py`, `scripts/doc-id.py`, `scripts/doc-index.py` — Python 3.12 standard
library only (map plan Global Constraint **G4**).

**Spec:** [`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md)
§5.3 (the impact rows this slice owns), §1.5 (the header), §1.6 (roles per family, now also at
[`docs/process/document-ids.md`](../process/document-ids.md) §1.5-§1.6), §7 (i) (every H row
named by a commit). Executors read both this plan and that RFC.

---

## 1. Purpose and scope

### 1.1 The map plan's slice section, quoted

Quoted verbatim from `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:760-784`
at `a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15`:

> ## Slice W37-8 — Charters, agents, and their READMEs
>
> **Executor skill:** `writing-skills`.
>
> **Scope:** §5.3's rows — the seven charters under `.claude/roles/`, `.claude/agents/README.md`
> and the two agent files §5.3 names, each gaining its header and its §1.6 role content. Plus
> the one row that creates nothing: **there is no maintainer charter**, because the maintainer
> is not a spawned role; the maintainer's authorities are listed once in `document-ids.md` §1.6
> and once in `CLAUDE.md` §12, and nowhere else.
>
> **DP-6 applies.** A charter is the maintainer's (§1.6, Reference — charters row). The executor
> drafts each diff; the slice's acceptance requires a dated maintainer line on the PR before
> merge. This is a gate, not a blocker: drafting proceeds while the line is pending.
>
> **The reporter and the watcher rows are the ones to get right.** Both charters must state
> *"owns no governed document"* explicitly, so W37-3's generated ownership matrix shows two
> deliberately empty rows rather than two gaps. An executor who leaves the sentence out makes
> the matrix report a defect that does not exist.
>
> **Acceptance:** all seven charters and the agents files carry a valid header; the generated
> ownership matrix has no empty cell that is not one of the two declared ones; a dated maintainer
> line exists for every charter edit; the gate's two halves are green.

### 1.2 Every §5.3 row this slice owns, by file, with its H/M treatment and its state today

RFC-937 §5.3's table is at
`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md:342-355`.
The "Kind" column is that table's own. "State at `a8b3c39`" is measured, not recalled; the
predicates are §1.3 below.

| # | File | §5.3 change (abridged from the row) | Kind | Header state at `a8b3c39` | §1.6 role content at `a8b3c39` | Task | Commit that will name it |
|---|---|---|---|---|---|---|---|
| 1 | `.claude/roles/auditor.md` | owns `findings/register.md`, `FD-`, `CR- kind: work\|phase`; sets `LG-` `closed`; checklist path; header | H + M | **present** (`family: reference`, `owner: maintainer`) | **absent** — no `FD-`, `CR-` or `LG-` token in the file | T7 | W37-8 PR squash commit, row 1 of the ledger table |
| 2 | `.claude/roles/decision-maker.md` | rulings one per file with an id; owns `specs/`, `adrs/`, `workflows/`; records OQ; header | H + M | **present** | **absent** — no `RL-`, `ADR-` or `WF-` token; `:40` still says *"write to ruling records, the open-questions log"* | T8 | same, row 2 |
| 3 | `.claude/roles/executor.md` | works from `PL-n` for `SL-n`; appends `LG-n` per task and PR; owns `RS-` (`library-spike`) and journey tests; never amends `WF-`; branch/PR convention; header | H + M | **present** | **absent** — the only `PL-` tokens are two citation paths (`:68`, `:99`, `:111`); no `SL-`, `LG-`, `RS-`, `WF-` | T9 | same, row 3 |
| 4 | `.claude/roles/lead.md` | dispatches `SL-`; maintains milestone sections and `WK-` rows; owns `CR- kind: review` and agents; residual `docs/` clause now enumerated by the generated matrix; header | H + M | **present** | **absent** — `WK-` appears only as prose history (`:35`, `:44`, `:49`, `:51`, `:72`, `:79`); no `SL-`, no `CR-` | T10 | same, row 4 |
| 5 | `.claude/roles/planner.md` | `PL-` via `writing-plans` with `doc-id.py next`; cuts `SL-` rows in the map plan; replan = new `PL-` with `supersedes:`; header | H + M | **present** | **partial** — it names slice design and `writing-plans`, but says *"new dated revisions on a replan trigger"*, not `supersedes:`, and names no `SL-` row minting | T11 | same, row 5 |
| 6 | `.claude/roles/reporter.md` | *"owns no governed document"* stated; reporter's fortnightly `WK-` status entry; `--slice-source` examples → `PL-` paths; header | H + M | **present** | **absent** — `grep -n "owns no governed document"` exits 1 | T6 | same, row 6 |
| 7 | `.claude/roles/watcher.md` | *"owns no governed document"* stated; header | H + M | **present** | **absent** — same grep, same exit | T6 | same, row 7 |
| 8 | `.claude/agents/README.md` | header; citations; README names agents as Reference family owned by the lead | M + H | **present** (`family: reference`, `owner: lead`, `:2`/`:6`) | **body silent** — the words "Reference" and "family" appear nowhere in the body | T5 | same, row 8 |
| 9 | `.claude/agents/ci-watcher.md` | header; citations | M + H | **absent** — harness front matter only (`name:`, `description:`, `tools:`, `model:`) | n/a (an agent file has no role-ownership prose) | T3 | same, row 9 |
| 10 | `.claude/agents/spec-reconciler.md` | header; citations | M + H | **absent** — harness front matter only | n/a | T4 | same, row 10 |
| 11 | Maintainer authorities | *"no `roles/maintainer.md` — the maintainer is not a spawned role; the maintainer's authorities are listed once in `document-ids.md` §1.6 and `CLAUDE.md` §12"* | H | **creates nothing** — this row is a statement to verify, not a file to write | — | T12 | verification recorded in the slice's closure evidence; no file changes |

**Five further agent files are in the standard's stamp set and in no §5.3 row.** RFC-937 §4
step 5 stamps *"every file under `docs/`, `.claude/roles/`, `.claude/skills/*/SKILL.md`,
`.claude/agents/`"* — all of `.claude/agents/`, not the two §5.3 names. The other five are
`accessibility-tester.md`, `evidence-collector.md`, `gate-runner.md`, `performance-engineer.md`
and `postgres-pro.md`. All five carry harness front matter and no `family:` key. Whether this
slice takes them is **DP-8.2**; the default until it is resolved is that it does, and T4 is
written for all six non-`ci-watcher` agent files.

**Two §5.3 rows are explicitly NOT this slice's**, stated so their absence is not read as an
omission: `.claude/settings.json` (row *"hook `statusMessage` citation"*, kind M) and
the `notes/` stub directory under `.claude/` (row *"19 stubs + README deleted; `REDIRECTS.csv` rows"*, kind H + M).
Neither is a charter, an agent, or a README of either; the map plan's W37-8 scope sentence
enumerates its rows and names neither. `docs/plans/PL-00939-...md:907-910`'s self-review maps
*"§5.3 → W37-8"* as a whole, so this exclusion is a reading of the slice sentence over the
section pointer and is recorded as **DP-8.6** rather than taken silently. **T1 verifies both
are already discharged** before the exclusion is relied on.

### 1.3 Predicates — every measurement above, runnable

All run from a clean worktree at `a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15`
(`/usr/bin/git rev-parse HEAD` → that sha; `/usr/bin/git status --short` empty), clock
`TZ=Europe/London date` → `Fri Sep 18 02:35:58 BST 2026`.

| Claim | Command, verbatim | Output at `a8b3c39` |
|---|---|---|
| The seven charters carry a header | `head -n 9 .claude/roles/auditor.md .claude/roles/decision-maker.md .claude/roles/executor.md .claude/roles/lead.md .claude/roles/planner.md .claude/roles/reporter.md .claude/roles/watcher.md` | seven blocks, each `family: reference` / `status: active` / `owner: maintainer` |
| No agent file carries the governed header | `grep -l "^family: reference" .claude/agents/*.md` | `.claude/agents/README.md` — one file, the README, not any of the seven agents |
| All seven agent files carry harness front matter | `grep -n "^name:" .claude/agents/*.md` | 7 lines, each `:2:name: <agent>` |
| Neither support charter states it owns nothing | `grep -n "owns no governed document" .claude/roles/reporter.md .claude/roles/watcher.md; echo GREP_EXIT=$?` | no lines; `GREP_EXIT=1` |
| `audit-docs.py` is green but discloses the agent files | `python3 scripts/audit-docs.py; echo EXIT=$?` | `EXIT=0`, final line `All checks passed.`, and the disclosure header `DISCLOSED (957, at or under the W37-11 residue ceiling)` |
| Seven of those disclosures are this slice's | `python3 scripts/audit-docs.py \| grep -c "check 30: \.claude/agents/"` | `7` — one per agent file, each `family '' has no known template under docs/_templates` |
| No charter is disclosed by check 30 | `python3 scripts/audit-docs.py \| grep -c "check 30: \.claude/roles/"` | `0` |
| `doc-id.py check` is green | `python3 scripts/doc-id.py check; echo EXIT=$?` | `EXIT=0`, `0 file(s) skipped` |
| The index is byte-stable | `python3 scripts/doc-index.py --check; echo EXIT=$?` | `EXIT=0`, `docs/INDEX.md: OK (byte-stable)` |

**Read the disclosure count as a trend at its boundary, never as an absence** (`CLAUDE.md` §10,
[`RFC-789`](../rfcs/RFC-00789-zero-calls-above-200k-tokens-measures-the-compaction-cap-not-discipline.md),
which is where the retired pre-migration note now lives). `957` is the pooled
figure at `a8b3c39`; this slice is expected to **lower** it by up to 7. A pooled ceiling row has
a definition, so an executor who sees the number move reads the function that assigns hits to
keys before concluding anything about it.

### 1.4 What this slice does not do

- It does not touch `CLAUDE.md`. That is W37-9 (`PL-939:785-814`), and G2's two permanence sites
  are W37-9's obligation, not this one's.
- It does not touch `.claude/skills/`. Those are W37-7's §5.4 rows (`PL-939:735-758`) — including
  the two content edits `CR-1065` §2.2 reassigned there, and `writing-plans` and
  `subagent-driven-development` from its §2.4 table.
- It does not perform RFC-937 §7 (i)'s fuller walk. `CR-1065` §2.4 assigns that walk to W37-11
  and reassigns only the individual files; this slice owns exactly one of them, `ci-watcher.md`.
- It does not rule DP-6. DP-6 is *"Resolved by: maintainer"* (`PL-939:302`, DP-6 row) and is
  discharged by dated lines on this slice's PR.

---

## 2. Executor skill and the roles

| Role | Who | Source of the charter | What they do in this slice |
|---|---|---|---|
| **Planner** | this document's author | `.claude/roles/planner.md` | Wrote this plan; does not implement, audit, merge, or rule any decision point below |
| **Executor** | one executor, spawned from its charter file, never an inline brief (`CLAUDE.md` §15) | `.claude/roles/executor.md` | Executes T2-T12 via TDD-shaped cycles, commits, opens the PR, appends the slice ledger |
| **Executor skill** | `writing-skills` | `PL-939:377`, sequencing table | The map plan's binding choice for this slice; the executor loads it before the first edit |
| **Decision-maker** | as dispatched | `.claude/roles/decision-maker.md` | Rules **DP-8.1** and **DP-8.2** — both blocking — before T2 starts |
| **Auditor** | one auditor, fresh context, per slice | `.claude/roles/auditor.md` | Audits the delivered slice against §5's Acceptance Standard; proposes verdicts, decides none |
| **Lead** | w37-team2 lead | `.claude/roles/lead.md` | Adopts/amends/rejects the auditor's verdicts; sole merge authority; converts the ETAs in §7 to clock times |
| **Maintainer** | — | not a spawned role (§5.3 row 11) | The dated DP-6 line per charter edit; nothing in this slice merges without them |

**Self-referential hazard, named because it bites here and nowhere else in WK-697.** This slice
edits `.claude/roles/executor.md`, `.claude/roles/auditor.md` and `.claude/roles/planner.md` —
the charters of the three roles working on it. An executor amending its own charter, and an
auditor auditing an amendment to its own, are instruments entangled with their subject. **The
mitigation is procedural, not clever:** T9 (executor.md) and T7 (auditor.md) each carry the
same maintainer line every other charter edit carries, and the auditor's report states
explicitly that T7 and T9 were audited against the §5.3 row text rather than against the
auditor's own judgement of what the role should say.

---

## 3. Tasks

Every task ends with a commit. Every step carries the command that verifies it. No step says
"add appropriate content" — where the content is prose, the task names the §5.3 clause the
prose must satisfy and the grep that proves it landed.

**Standing per-task convention (all tasks):** work on branch `w37-8-charters-agents`, commit
with Conventional Commits, and after every commit run the two cheap checks — they take seconds
and catch a broken header immediately:

```bash
python3 scripts/doc-id.py check; echo DOCID_EXIT=$?
python3 scripts/audit-docs.py > /tmp/w37-8-audit.txt 2>&1; echo AUDIT_EXIT=$?; tail -1 /tmp/w37-8-audit.txt
```

---

### Task 1: Baseline, preconditions, and the two exclusions verified

**Files:** none modified. Output is a baseline block appended to the slice ledger.

**Interfaces:**
- Consumes: nothing.
- Produces: the baseline numbers every later task compares against — `AUDIT_DISCLOSED_BASE`,
  `AGENT_CHECK30_BASE`, and the head sha the slice was cut from.

- [ ] **Step 1: Confirm both gating events have landed.**

```bash
grep -n 'Maintainer acceptance' docs/closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md
ls docs/closures/CR-01065-w37-6-checkpoint-3-close.md
```

Expected: the first prints a line carrying a **date**, not `_pending_`; the second lists the
file on `main`. **If either fails, stop and report to the lead — this slice is not released.**

- [ ] **Step 2: Record the baseline.**

```bash
/usr/bin/git rev-parse HEAD
python3 scripts/audit-docs.py > /tmp/w37-8-base.txt 2>&1; echo AUDIT_EXIT=$?
grep -c "check 30: \.claude/agents/" /tmp/w37-8-base.txt
grep -n "^DISCLOSED" /tmp/w37-8-base.txt
python3 scripts/doc-id.py check; echo DOCID_EXIT=$?
python3 scripts/doc-index.py --check; echo INDEX_EXIT=$?
```

Expected at `a8b3c39`: `AUDIT_EXIT=0`, `7`, a `DISCLOSED (957, …)` line, `DOCID_EXIT=0`,
`INDEX_EXIT=0`. **At a later tree the numbers will differ — record what you get, do not assert
these.**

- [ ] **Step 3: Verify DP-8.6's two exclusions are genuinely discharged.**

```bash
grep -n "statusMessage" .claude/settings.json
ls .claude/ | grep -x notes; echo NOTES_DIR_EXIT=$?
grep -c 'notes/0' docs/REDIRECTS.csv
```

Expected: the `statusMessage` citation, if present, names a post-migration path; the `notes/`
directory under `.claude/` does not exist (`NOTES_DIR_EXIT=1`); `REDIRECTS.csv` carries rows for
the stubs it held. **If any of the three contradicts the
exclusion, DP-8.6 reopens and the lead is told before T2.**

- [ ] **Step 4: Confirm the ownership-matrix command runs and record its current output.**

```bash
python3 scripts/doc-index.py --help 2>&1 | head -30
```

Read which flag emits the ownership matrix and record the exact invocation in the ledger. The
acceptance item in §5 is written against *that* invocation, run verbatim. **Do not paraphrase
the flag from this plan — read it from the tool.**

- [ ] **Step 5: Commit the ledger baseline entry.**

**ETA:** 0.5 h.

---

### Task 2: The merged-header convention — `docs/_templates/REFERENCE.md`

**BLOCKED on DP-8.1.** Do not start until that row carries a resolver id.

**Files:**
- Modify: `docs/_templates/REFERENCE.md`

**Interfaces:**
- Consumes: T1's baseline.
- Produces: the four permitted harness keys, declared. T3 and T4 cannot land a valid header
  without this.

**Why this task exists.** `scripts/doc-id.py:4718-4731` records the problem in terms:

> **What this slice does NOT stamp, and why it is deferred rather than exempt.** 46
> `.claude/skills/*/SKILL.md` and 7 `.claude/agents/*.md` already carry the harness's own
> YAML front matter (`name:`, `description:`, and for an agent `tools:`/`model:`). A stamp
> cannot prepend a second block — `_docid.parse_header` reads exactly one, from `lines[0]
> == "---"` to the closing `---` — so their header has to be **merged** into the block
> they have, and the keys have to be declared in `docs/_templates/REFERENCE.md` first,
> because RL-981 makes the template the licensing instrument for a family's permitted
> fields.

And `docs/process/document-ids.md:136` makes the consequence of not declaring them explicit:
**"Unknown field → lint failure."**

- [ ] **Step 1: Prove the current template does not license the keys.**

```bash
grep -n "^name:\|^description:\|^tools:\|^model:" docs/_templates/REFERENCE.md; echo GREP_EXIT=$?
```

Expected: no lines, `GREP_EXIT=1`. This is the red-before.

- [ ] **Step 2: Write the failing check.** Create a scratch copy of one agent file with a merged
header and run the parser against it:

```bash
mkdir -p /tmp/w37-8-red && cp .claude/agents/ci-watcher.md /tmp/w37-8-red/
# hand-merge the six governed keys into its front matter in the scratch copy, then:
python3 scripts/doc-id.py check --help 2>&1 | head -20
```

Read from the tool which invocation checks a single path, and run it against the scratch file.
Expected: a failure naming an unknown field. **Record the exact message — it is the red this
task turns green.**

- [ ] **Step 3: Declare the keys in the template.** Add to `docs/_templates/REFERENCE.md`, in the
same commented style the vendored-skill block at its foot already uses, a block declaring that a
Reference file consumed by the Claude Code harness — `.claude/agents/*.md` and
`.claude/skills/*/SKILL.md` — carries the harness's own keys **merged into the single governed
front-matter block**, and naming them exactly: `name:`, `description:`, and for an agent
`tools:` and `model:`. State the ordering the template fixes (governed keys first, harness keys
after, or the reverse — pick one and say which, because a second ordering is a second source),
and cite `scripts/doc-id.py:4718-4731` and `document-ids.md` §1.5 as the authority.

- [ ] **Step 4: Re-run the check against the scratch file.** Expected: the unknown-field failure
is gone.

- [ ] **Step 5: Prove the licence is narrow.** Add a second scratch file with an *undeclared* key
(e.g. `colour: red`) and confirm the check still fails on it. **A licence that accepts anything
has not been tested** (`CLAUDE.md` §13 — a check that has never printed a failure has not been
tested).

- [ ] **Step 6: Run the two cheap checks and commit.**

```
docs(templates): license the harness front-matter keys on Reference files (RFC-937 §1.5)
```

**ETA:** 1.5 h — most of it in step 5, and in deciding the ordering rather than typing it.

---

### Task 3: `.claude/agents/ci-watcher.md` — the one reassigned file

**Files:**
- Modify: `.claude/agents/ci-watcher.md`

**Why this file is first among the agents.** `CR-1065` §2.4 (read at
`origin/w37-6-checkpoint-3-close`) lists it as **NOT CLOSED — still pre-migration content**,
last touched by `3f41d60` (#616, pre-migration), and its reassignment table gives:

> | `.claude/agents/ci-watcher.md` | **W37-8** | PL-939 `:760`, agents |

It is the only RFC-937 §7 (i) row reassigned to this slice. Closing it is this slice's one
inherited obligation and the acceptance item most likely to be checked by name.

- [ ] **Step 1: Find what is pre-migration about it.**

```bash
grep -n "docs/notes/\|docs/audit/\|NT-00\|F[0-9][0-9]\b\|2026-0[0-9]-[0-9][0-9]-" .claude/agents/ci-watcher.md
grep -n "docs/" .claude/agents/ci-watcher.md
```

Every hit is a candidate. **A grep hit is a candidate, never a reading** — open each one and
confirm the path or id it names does not resolve at this tree before rewriting it:

```bash
# for each path P printed above:
ls P 2>&1
```

- [ ] **Step 2: Rewrite each dangling citation** to the post-migration path or id, using
`docs/REDIRECTS.csv` as the mapping rather than guessing:

```bash
grep -n "<old-path>" docs/REDIRECTS.csv
```

- [ ] **Step 3: Merge the governed header** into the existing front-matter block, per the
ordering T2 fixed. Fields: `family: reference`, `title:`, `status: active`, `created:` (the
file's original creation date, read from `/usr/bin/git log --diff-filter=A --format=%aI -- .claude/agents/ci-watcher.md`
— `%aI` always, a commit date is not a push time), `owner: lead` (`document-ids.md` §1.6,
*"Reference — agents | lead"*), `corrected_by: []`, `relates: []`. Keep `name:`,
`description:`, `tools:`, `model:` — the harness reads them.

- [ ] **Step 4: Verify the header parses and the disclosure clears.**

```bash
python3 scripts/doc-id.py check; echo DOCID_EXIT=$?
python3 scripts/audit-docs.py > /tmp/w37-8-t3.txt 2>&1; echo AUDIT_EXIT=$?
grep -c "check 30: \.claude/agents/" /tmp/w37-8-t3.txt
```

Expected: `DOCID_EXIT=0`, `AUDIT_EXIT=0`, and the agent check-30 count **one lower than T1's
baseline** (7 → 6 at `a8b3c39`).

- [ ] **Step 5: Verify no citation still dangles.**

```bash
grep -o "docs/[A-Za-z0-9_./-]*" .claude/agents/ci-watcher.md | sort -u > /tmp/w37-8-t3-paths.txt
while read -r p; do test -e "$p" || echo "MISSING: $p"; done < /tmp/w37-8-t3-paths.txt
```

Expected: no `MISSING:` lines.

- [ ] **Step 6: Commit.**

```
docs(agents): close ci-watcher.md's §7(i) row — header and post-migration citations
```

**ETA:** 1.5 h.

---

### Task 4: The remaining agent files — `spec-reconciler.md` and the five DP-8.2 names

**Files:**
- Modify: `.claude/agents/spec-reconciler.md` (§5.3 row)
- Modify, **subject to DP-8.2's default**: `.claude/agents/accessibility-tester.md`,
  `evidence-collector.md`, `gate-runner.md`, `performance-engineer.md`, `postgres-pro.md`

**Interfaces:**
- Consumes: T2's template licence, T3's merged-header shape — use the *same* key ordering, byte
  for byte. A shape defined twice will diverge.
- Produces: zero `check 30: .claude/agents/` disclosures.

- [ ] **Step 1: For each file, read its dangling citations** with T3 step 1's two greps, and
resolve each through `docs/REDIRECTS.csv`.

- [ ] **Step 2: Merge the governed header** into each, `owner: lead`, `created:` from
`/usr/bin/git log --diff-filter=A --format=%aI -- <file>`.

- [ ] **Step 3: Verify the class is closed, not sampled.**

```bash
grep -L "^family: reference" .claude/agents/*.md; echo GREP_EXIT=$?
```

Expected: no files printed (`grep -L` prints files *without* the match). **This is the check the
failure cannot survive** — it enumerates the directory rather than asking whether the files you
remembered were done.

- [ ] **Step 4: Verify the disclosure class is empty.**

```bash
python3 scripts/audit-docs.py > /tmp/w37-8-t4.txt 2>&1; echo AUDIT_EXIT=$?
grep -c "check 30: \.claude/agents/" /tmp/w37-8-t4.txt
grep -n "^DISCLOSED" /tmp/w37-8-t4.txt
```

Expected: `AUDIT_EXIT=0`, `0`, and a DISCLOSED total **7 lower** than T1's baseline. If it is not
exactly 7 lower, **do not adjust the number — find what else moved**: a pooled ceiling row has a
definition, and old ceiling + this class's hits must equal the new count.

- [ ] **Step 5: Confirm the harness still reads the agents.** Spot-check that the front matter is
still a single valid block by running the same `parse_header` path the check uses, and by
confirming `name:`, `description:`, `tools:` and `model:` survived verbatim in every file:

```bash
grep -c "^name:" .claude/agents/ci-watcher.md .claude/agents/spec-reconciler.md .claude/agents/accessibility-tester.md .claude/agents/evidence-collector.md .claude/agents/gate-runner.md .claude/agents/performance-engineer.md .claude/agents/postgres-pro.md
```

Expected: `1` for each of the seven.

- [ ] **Step 6: Commit.**

```
docs(agents): stamp the governed Reference header on every agent file
```

**ETA:** 2.0 h — six files, each with its own citation sweep.

---

### Task 5: `.claude/agents/README.md` — the body says what the header says

**Files:**
- Modify: `.claude/agents/README.md`

**What §5.3 asks for:** *"README names agents as Reference family owned by the lead."* The
header already does (`:2` `family: reference`, `:6` `owner: lead`). **DP-8.5** asks whether that
discharges the row; the default this task is written against is that it does not — §5.3's verb
is *"names"*, addressed to a reader of the README, and a reader does not read front matter.

- [ ] **Step 1: Prove the body is silent.**

```bash
grep -n "Reference family\|Reference — agents\|owned by the lead" .claude/agents/README.md; echo GREP_EXIT=$?
```

Expected: `GREP_EXIT=1`.

- [ ] **Step 2: Add one short paragraph** near the top of the body stating: agent files are the
**Reference** family (`document-ids.md` §1.2); they carry no id and are cited by path; their
owner is the **lead** (`document-ids.md` §1.6, *"Reference — agents | lead"*), who creates,
amends and retires them; and each agent file carries the governed header merged with the
harness's own keys (pointing at `docs/_templates/REFERENCE.md`, not restating the key list — a
restated list is the copy that goes stale).

- [ ] **Step 3: Rewrite any dangling citation** in the README, found with T3 step 1's greps and
resolved through `REDIRECTS.csv`.

- [ ] **Step 4: Verify.**

```bash
grep -n "Reference" .claude/agents/README.md | head
python3 scripts/audit-docs.py; echo AUDIT_EXIT=$?
```

- [ ] **Step 5: Commit.**

```
docs(agents): README names the family, the owner and the header source
```

**ETA:** 1.0 h.

---

### Task 6: `reporter.md` and `watcher.md` — the two deliberately empty rows

**Files:**
- Modify: `.claude/roles/reporter.md`
- Modify: `.claude/roles/watcher.md`

**This is the task the map plan singles out** (`PL-939:775-779`): *"An executor who leaves the
sentence out makes the matrix report a defect that does not exist."* Two separate charter edits,
so **two dated maintainer lines** under DP-6, not one.

**The sentence's source, quoted so it is not paraphrased.** `docs/process/document-ids.md:167`:

> The reporter and the watcher own no governed document: the reporter reads closures and rulings
> and writes the external channel; the watcher writes runtime state. Their charters say so, so
> the generated ownership matrix shows two deliberately empty rows rather than two gaps.

- [ ] **Step 1: Prove the red.**

```bash
grep -n "owns no governed document" .claude/roles/reporter.md .claude/roles/watcher.md; echo GREP_EXIT=$?
```

Expected: no lines, `GREP_EXIT=1`.

- [ ] **Step 2: Add the sentence to `reporter.md`** under its `Owns:` bullet, in the charter's own
voice: that the reporter **owns no governed document** — it reads closures and rulings and writes
the external channel — and that this is deliberate, so the generated ownership matrix shows an
empty row rather than a gap. Add §5.3's second and third clauses in the same edit: the
**fortnightly `WK-` status entry** (`document-ids.md` §1.10a) and `--slice-source` examples
pointing at `PL-` paths rather than dated filenames.

- [ ] **Step 3: Add the sentence to `watcher.md`** — owns no governed document; writes runtime
state; the empty matrix row is deliberate.

- [ ] **Step 4: Verify.**

```bash
grep -n "owns no governed document" .claude/roles/reporter.md .claude/roles/watcher.md; echo GREP_EXIT=$?
grep -n "slice-source" .claude/roles/reporter.md
```

Expected: two lines, `GREP_EXIT=0`; every `--slice-source` example naming a `PL-` path that
exists (`ls` each).

- [ ] **Step 5: Run the ownership-matrix command** recorded in T1 step 4 and confirm the two rows
are now *declared* empty rather than blank. **Record the output verbatim in the ledger** — §5's
acceptance item 2 is read against it.

- [ ] **Step 6: Commit.**

```
docs(roles): reporter and watcher state that they own no governed document (RFC-937 §1.6)
```

**ETA:** 1.0 h.

---

### Task 7: `.claude/roles/auditor.md` — §1.6 role content

**Files:**
- Modify: `.claude/roles/auditor.md`

**§5.3's clauses, one at a time:** owns `findings/register.md`; owns `FD-`; owns
`CR- kind: work|phase`; **sets `LG-` to `closed`**; the checklist path; the header (already
present).

**Authority for each clause is `document-ids.md` §1.6's own table rows** — quote the cell, do
not invent a formulation: the **FD** row (*"auditor (register row + essay) … auditor sets
`closed` in place citing the PR; `retired` for `accept`; unowned rows decay to the phase
review"*), the **CR** row (*"auditor (`work`, `phase`); lead (`kind: review`)"*), the **SL** row
(*"auditor closes: sets the `LG-` `closed`, verifies acceptance"*), and the **LG** row
(*"auditor sets `closed` at slice close"*).

- [ ] **Step 1: Prove the red.**

```bash
grep -n "FD-\|CR-\|LG-" .claude/roles/auditor.md; echo GREP_EXIT=$?
```

Expected at `a8b3c39`: only `:27-28`'s `docs/findings/register.md` and checklist paths; no
family-prefix token.

- [ ] **Step 2: Rewrite the `Owns:` bullet** to name, each with its §1.6 citation: the findings
register and every `FD-` (row and essay); every `CR-` of kind `work` and `phase`; setting a
slice's `LG-` to `closed` at the slice close; and the checklist path
`docs/process/checklists/work-item-close.md` / `phase-close.md`.

- [ ] **Step 3: Confirm the `Never:` bullet still holds the §13 boundary** — the auditor
*proposes* verdicts and the lead adopts, amends or rejects (`CLAUDE.md` §12). If it does not say
so, add it; this is the clause the whole audit chain rests on.

- [ ] **Step 4: Verify.**

```bash
grep -n "FD-\|CR-\|LG-" .claude/roles/auditor.md
ls docs/process/checklists/work-item-close.md docs/process/checklists/phase-close.md
python3 scripts/audit-docs.py; echo AUDIT_EXIT=$?
```

- [ ] **Step 5: Commit.**

```
docs(roles): auditor charter names the families it owns (RFC-937 §1.6)
```

**ETA:** 1.5 h.

---

### Task 8: `.claude/roles/decision-maker.md` — §1.6 role content

**Files:**
- Modify: `.claude/roles/decision-maker.md`

**§5.3's clauses:** rulings are **one per file with an id**; owns `specs/`, `adrs/`,
`workflows/`; records OQ; header (present).

**§1.6 cells to quote:** the **RL** row (*"decision-maker; the maintainer may author one on
scope or process … decision-maker: new `RL-` with `supersedes:`; `retired` when overridden with
no successor"*), **FR NFR DEP** (*"decision-maker, via `spec-change`"*), **ADR**
(*"decision-maker, via `adr-write`"*), **WF** (*"decision-maker, via `spec-change`"*), **OQ**
(*"decision-maker records (anyone raises) … decision-maker sets `closed` citing the resolver"*),
and **PL** (*"decision-maker rules decision points as `RL-`, **never edits the plan**"*).

- [ ] **Step 1: Prove the red.**

```bash
grep -n "RL-\|ADR-\|WF-\|OQ-\|docs/rulings/" .claude/roles/decision-maker.md; echo GREP_EXIT=$?
sed -n '40p' .claude/roles/decision-maker.md
```

Expected: `:40` still reads *"write to ruling records, the open-questions log, and `docs/specs/`"*
— a pre-RFC-937 formulation naming no family and no per-file id.

- [ ] **Step 2: Rewrite the `Owns:` and `Tools:` bullets** so that: a ruling is **one `RL-` file
under `docs/rulings/` with an id from `python3 scripts/doc-id.py next`** (not an entry in a
shared rulings document); the decision-maker creates and amends `FR-`/`NFR-`/`DEP-` via
`spec-change`, `ADR-` via `adr-write`, and `WF-`; records an `OQ-` and sets it `closed` citing
the resolver; and **rules a plan's decision points as an `RL-` and never edits the plan**.

- [ ] **Step 3: Verify.**

```bash
grep -n "RL-\|ADR-\|WF-\|OQ-" .claude/roles/decision-maker.md
python3 scripts/audit-docs.py; echo AUDIT_EXIT=$?
```

- [ ] **Step 4: Commit.**

```
docs(roles): decision-maker charter names one ruling per file and the families it owns
```

**ETA:** 1.5 h.

---

### Task 9: `.claude/roles/executor.md` — §1.6 role content

**Files:**
- Modify: `.claude/roles/executor.md`

**§5.3's clauses:** works from a `PL-` for its `SL-`; **appends its `LG-` per task and per PR**;
owns `RS-` (via `library-spike`) and the journey tests; **never amends a `WF-`**; the branch and
PR convention; header (present).

**§1.6 cells to quote:** **LG** (*"executor, appends per task and per PR (`active`)"*), **RS
spike/measurement** (*"executor (`library-spike`, measurements) … executor sets `active` on
filing"*), **WF** (*"executor delivers and owns `test_wfNN_journey`"* — and the decision-maker,
not the executor, amends it), **PL leaf** (*"executor works from it"*).

**Read the branch and PR convention from where it is declared, not from memory.** RFC-937 §5.1's
`CONTRIBUTING.md` row gives *"branch `sl-<n>-<slug>`, PR title `SL-<n>: …`"* — but
`CONTRIBUTING.md` itself is **W37-9's**, unlanded (`CR-1065` §2.4: *"NOT CLOSED — still
pre-migration content"*). **So this task states the convention by citing RFC-937 §5.1, and says
in the charter that `CONTRIBUTING.md` is the operative source once W37-9 lands it.** Writing the
convention twice as an independent statement is the duplication `CLAUDE.md` §2 forbids.

- [ ] **Step 1: Prove the red.**

```bash
grep -n "SL-\|LG-\|RS-\|WF-" .claude/roles/executor.md; echo GREP_EXIT=$?
```

Expected: no family-prefix tokens; the only `PL-` hits are citation paths at `:68`, `:99`,
`:111`.

- [ ] **Step 2: Rewrite the `Owns:` bullet** with the six clauses above, each citing its §1.6 cell.

- [ ] **Step 3: Add the `Never:` clause** — the executor never amends a `WF-`; a journey the code
disagrees with is escalated, not edited (`CLAUDE.md` §0's *"when code and spec disagree, stop and
resolve it"*).

- [ ] **Step 4: Verify.**

```bash
grep -n "SL-\|LG-\|RS-\|WF-" .claude/roles/executor.md
python3 scripts/audit-docs.py; echo AUDIT_EXIT=$?
```

- [ ] **Step 5: Commit.**

```
docs(roles): executor charter names PL/SL/LG/RS and the never-amend-WF rule
```

**ETA:** 1.5 h.

---

### Task 10: `.claude/roles/lead.md` — §1.6 role content

**Files:**
- Modify: `.claude/roles/lead.md`

**§5.3's clauses:** dispatches `SL-`; maintains the milestone sections and the `WK-` rows; owns
`CR- kind: review` and **the agents**; **the residual `docs/` clause is now enumerated by the
generated matrix**; header (present).

**§1.6 cells to quote:** **SL** (*"lead dispatches (`active`)"*), **WK** (*"lead runs it"*),
**Phase** (*"maintainer opens the section; lead maintains it … lead runs `phase-review` →
`CR- kind: review`"*), **CR** (*"lead (`review`)"*), **Reference — agents** (*"lead"*),
**Reference — skills** (*"the five roles already permitted; lead approves … lead: `retired`"*),
**FD** (*"lead sets `decision:`"*), **RS audit** (*"lead gives each `FD-` its disposition …
lead: `closed` once every `FD-` is closed"*).

**The "residual `docs/` clause" is the point of this task, and it is a deletion.** A charter that
enumerates by hand what a generated matrix enumerates is the second copy `CLAUDE.md` §12 and
[`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md) forbid. Replace the hand-kept residual
list with a pointer at the generated ownership matrix and the command that prints it (the one T1
step 4 recorded).

- [ ] **Step 1: Prove the red.**

```bash
grep -n "SL-\|CR-\|agents" .claude/roles/lead.md; echo GREP_EXIT=$?
grep -n "Owns" .claude/roles/lead.md
```

Expected: `WK-` appears only as prose history (`:35`, `:44`, `:49`, `:51`, `:72`, `:79`); no
`SL-`, no `CR-`, no ownership of `.claude/agents/`.

- [ ] **Step 2: Rewrite the `Owns:` bullet** with the clauses above.

- [ ] **Step 3: Replace the residual `docs/` enumeration with the matrix pointer**, naming the
command verbatim.

- [ ] **Step 4: Handle F97 per DP-8.3's resolution.** Default (this review's and this plan's
recommendation): **decline, with a date.** Add nothing to `lead.md` for F97; instead record on
the slice's PR a dated line of the form *"F97 declined as W37-8 scope on <date>: W37-8's
acceptance is charter headers and §1.6 role content; F97's remedy is a new behavioural clause in
`lead.md` and needs its own maintainer line. Carried to <named event>."* **The named event must
be named** — an undated carry is what turned F97 into a decayed register row in the first place
(`CR-1064:154`).

- [ ] **Step 5: Verify.**

```bash
grep -n "SL-\|CR-\|agents\|ownership matrix" .claude/roles/lead.md
grep -n "F97" .claude/roles/lead.md; echo F97_GREP_EXIT=$?
python3 scripts/audit-docs.py; echo AUDIT_EXIT=$?
```

Under the default, `F97_GREP_EXIT=1` and the decline is on the PR, not in the file.

- [ ] **Step 6: Commit.**

```
docs(roles): lead charter names SL/WK/CR-review/agents; residual docs/ list → the generated matrix
```

**ETA:** 2.0 h — the residual-clause deletion needs the matrix output read first.

---

### Task 11: `.claude/roles/planner.md` — §1.6 role content

**Files:**
- Modify: `.claude/roles/planner.md`

**§5.3's clauses:** writes a `PL-` via `writing-plans` with an id from `doc-id.py next`; **cuts
the `SL-` rows in the map plan**; **a replan is a new `PL-` with `supersedes:`** — not a new
dated file; header (present).

**§1.6 cells to quote:** **PL map/leaf** (*"planner, via `writing-plans`; `draft` while decision
points are open, `active` on freeze … planner: new `PL-` with `supersedes:`"*) and **SL**
(*"planner, cut in the map plan (`draft`) … planner re-cuts on replan"*).

- [ ] **Step 1: Prove the red.**

```bash
grep -n "frozen dated files\|new dated revisions\|supersedes\|SL-" .claude/roles/planner.md
```

Expected at `a8b3c39`: *"the plan: frozen dated files in `docs/plans/`; new dated revisions on a
replan trigger"* — the pre-RFC-937 formulation; no `supersedes:`, no `SL-` row minting.

- [ ] **Step 2: Rewrite that clause**: a plan is a `PL-` file with an id from
`python3 scripts/doc-id.py next`, `draft` while a blocking decision point is open and `active`
on freeze; a replan is a **new `PL-` carrying `supersedes: [<old id>]`**, and the superseded
plan gets `superseded_by:` — the two fields being among the only ones edited after a file
freezes (`document-ids.md` §1.5).

- [ ] **Step 3: Add the `SL-` clause** — the planner cuts the slice rows in the map plan, each
`draft` at minting, and re-cuts them on a replan.

- [ ] **Step 4: Leave the §14 phase-review ownership clause alone.** It is correct and it is
cited elsewhere; this task adds families, it does not re-litigate authorship.

- [ ] **Step 5: Verify.**

```bash
grep -n "supersedes\|SL-\|doc-id.py next" .claude/roles/planner.md
python3 scripts/audit-docs.py; echo AUDIT_EXIT=$?
```

- [ ] **Step 6: Commit.**

```
docs(roles): planner charter names PL ids, SL row minting and supersedes-on-replan
```

**ETA:** 1.5 h.

---

### Task 12: The row that creates nothing — no maintainer charter

**Files:** none modified, unless a contradiction is found.

**§5.3's row, verbatim:** *"Maintainer authorities | no `roles/maintainer.md` — the maintainer is
not a spawned role; the maintainer's authorities are listed once in `document-ids.md` §1.6 and
`CLAUDE.md` §12"* — kind **H**.

**A row that creates nothing is discharged by verification, and the verification is that the
listing is in exactly two places.** A third copy is the defect.

- [ ] **Step 1: Confirm no maintainer charter exists.**

```bash
ls .claude/roles/
ls .claude/roles/maintainer.md 2>&1
```

Expected: seven files, and `No such file or directory` for the eighth.

- [ ] **Step 2: Confirm both listings exist.**

```bash
grep -n "maintainer" docs/process/document-ids.md | head -20
grep -n "maintainer" CLAUDE.md | head -20
```

- [ ] **Step 3: Sweep for a third copy.** Enumerate the class before concluding it is empty:

```bash
grep -rln "maintainer" .claude/roles/ .claude/agents/ docs/process/
```

Every hit that is a *list of the maintainer's authorities* (as opposed to a mention of the role)
is a third copy and a finding. **A mention is not a listing — open each hit and read it before
classifying it.**

- [ ] **Step 4: Record the result in the ledger.** If a third copy exists, file it as an `FD-`
with the lead rather than deleting it in this slice — a charter-adjacent deletion is a maintainer
amendment.

- [ ] **Step 5: Commit the ledger entry** (no repository file changes expected).

**ETA:** 0.5 h.

---

### Task 13: Gate, PR, the DP-6 lines, and the ledger's §7 (i) table

**Files:**
- Modify: the slice's `LG-` ledger.

- [ ] **Step 1: Run both halves of the gate locally.** `CLAUDE.md` §11 and map plan **G7** — a
Python-only run is not the gate, and a Python-only "gate" has been green here while the frontend
was red. Delegate the run to the `gate-runner` agent so the output does not sit in the main
thread's context.

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

Every command's exit code is recorded separately. **`cmd | tail -1 && echo ok` reports the wrong
exit code** — do not chain a pipe in front of the code you record.

- [ ] **Step 2: Run the three id instruments and the `--verify` pre-PR step.**

```bash
python3 scripts/audit-docs.py; echo EXIT=$?
python3 scripts/doc-id.py check; echo EXIT=$?
python3 scripts/doc-index.py --check; echo EXIT=$?
```

`docs/process/delivery-process.md` §11a requires
`python3 scripts/doc-id.py migrate --verify <tmpdir> --ref <ref>` before a PR that **adds a file
under `docs/`**. This slice adds no file under `docs/` except the ledger entry; if it does add
one, run `--verify` and read **row (a)** specifically. **On a migrated tree, resolve `<ref>` from
`delivery-process.core.json`'s `verified_against_tree` rather than passing `HEAD`** — a verify
pinned to `HEAD` verifies the wrong tree after the migration and prints phantom fatal rows.

- [ ] **Step 3: Regenerate and check the index.**

```bash
python3 scripts/doc-index.py
/usr/bin/git status --porcelain docs/INDEX.md
python3 scripts/doc-index.py --check; echo EXIT=$?
```

Expected: `--check` exits 0 and `git status --porcelain docs/INDEX.md` is empty (map plan
Acceptance Standard item 2).

- [ ] **Step 4: Write the §7 (i) table into the ledger** — one row per file in §1.2 above, with
the commit that closed it, so W37-11's fuller walk finds this slice's rows already named.

- [ ] **Step 5: Open the PR**, titled for the slice, body carrying: the file table, the exit-code
table from step 1, the disclosure-count delta from T4, the ownership-matrix output from T6, and
**an explicit list of the charter edits awaiting a dated maintainer line**. No `claude.ai`
session URL reaches GitHub (map plan **G8**).

- [ ] **Step 6: Wait for CI by head SHA.** Delegate to the `ci-watcher` agent. **Name the range
`origin/main...w37-8-charters-agents`, not the tip sha**, when asking for a review; use the head
sha only to identify the CI run.

- [ ] **Step 7: Collect the DP-6 lines.** One dated maintainer line per charter edit — eight
charter-file edits if DP-8.2's default holds (auditor, decision-maker, executor, lead, planner,
reporter, watcher = 7, plus `docs/_templates/REFERENCE.md` if T2's template amendment is ruled a
`process/` amendment under DP-8.1). **Merging waits on these; drafting and CI do not.**

- [ ] **Step 8: Hand to the auditor**, then to the lead for the verdicts and the merge.

**ETA:** 2.0 h of executor work, excluding wall-clock waiting on CI and on the maintainer's
lines.

---

## 4. Reconciled against plan review 13

This section is **mandatory** under the deputy's ruling of 2026-09-18 00:41:53 BST, condition
(b). `CR-1064`'s own closed list (`docs/closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md:525-556`)
states: *"Nothing outside this list is owed to review 13, so a drafter can discharge the section
and know they are done"*, and: *"A draft cannot complete that section by writing 'reconciled'.
Each row above names a decision or a statement; the section is discharged row by row, and a row
answered 'declined' with a reason is discharged."*

Two source records are reconciled against: **`CR-1064`** (plan review 13, read at
`a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15` on `main`, base tree recorded in its own header as
`4d9fe1d62328285ac0483b047c3959e39e0f5bd6`) and **`CR-1065`** (W37-6 checkpoint-3 close; its
header records `tree: a0dbd20a1b276028e9a84647fd17f2a28213627f`). **`CR-1065` was read on
`origin/w37-6-checkpoint-3-close`, PR #787, not on `main`, while this plan was drafted; it is
now on `main`** (`git log --oneline -1 -- docs/closures/CR-01065-w37-6-checkpoint-3-close.md`
→ `d63f765`), **byte-identical to the branch revision cited below**
(`git diff origin/w37-6-checkpoint-3-close:docs/closures/CR-01065-w37-6-checkpoint-3-close.md
origin/main:docs/closures/CR-01065-w37-6-checkpoint-3-close.md` → empty), so every line number
§4.2 cites still resolves without re-derivation.

### 4.1 Every item `CR-1064` routes to W37-8

| Source line | Item | This plan's answer |
|---|---|---|
| `CR-1064:542` (the closed list's W37-8 row) and `CR-1064:154` (the F97 register row) and `CR-1064:576` (the proposal summary's Register row) | **F97's disposition.** *"A session ends leaving the shared checkout in a state its successor cannot fast-forward, and nothing announces it"* — the remedy touches `.claude/roles/lead.md`, a maintainer amendment under DP-6. The review asks: *"Whether F97 is drafted alongside the charter headers or explicitly declined with a date. **This review recommends disclosed candidate, not scope**"* | **Answered, and the review's recommendation is followed.** F97 is a **disclosed candidate, not scope**. It is carried as **DP-8.3** with both options written out and the recommendation *decline with a date*, and the mechanics are **T10 step 4**: nothing is added to `lead.md` for F97, and a dated decline line naming the carrying event goes on this slice's PR. The review's own reason is adopted verbatim as the reason: W37-8's acceptance is *charter headers and §1.6 role content*, and a new behavioural clause in `lead.md` is a different kind of change needing its own maintainer line. **The row is discharged as answered, not as declined** — the decision itself (draft vs. decline) is the maintainer's at the PR, and DP-8.3 records that |
| `CR-1064:556` (the closed list's **All four** row) | **§2b** — *"four run disclosures are filed in no register row, and the idempotence label collides with the real F28. That each draft's scope was derived **after** the filing, or states that it was derived before and names the risk"* | **Stated: this plan's scope was derived BEFORE the four disclosures reached `main`, and here is the risk.** The four were filed on `origin/w37-6-checkpoint-3-close` as `FD-1066`, `FD-1067`, `FD-1068` and `FD-1069` (named in `CR-1065`'s `relates:` field), and at drafting **none was on `main` at `a8b3c39`**. I read all four titles from that branch: `FD-1066` (idempotence — second `migrate` run zero-diff not proven), `FD-1067` (check 35 — two sub-clauses fire on one non-Markdown file after F87's widening), `FD-1068` (standing CI verify reads the W37-11 record from a pinned base forever), `FD-1069` (H1 residue by file and tracked-files docstrings disagree on population). **The named risk:** all four are instrument- or corpus-level and none names `.claude/roles/` or `.claude/agents/`, so on the evidence read they do not move this slice's scope — **but that was a judgement made against four titles and one `relates:` field, not against four merged records read in full.** **All four are now on `main`** (`ls docs/findings/ \| grep -E '01066\|01067\|01068\|01069'` → all four present at `d63f765`), which discharges the wait but not the re-read: **T1 step 1 is still the control** — the executor re-reads all four in full at slice start and reports any W37-8 routing to the lead before T2, since this correction pass has confirmed presence, not content |
| `CR-1064:444-470` (the lead's Decision 1) | The plan-of-record's BST windows — *"Recommendation: the plan absorbs nothing from it"* | **Absorbed nothing.** This plan states ETAs in **hours of executor work** and no clock time anywhere. §7's own note says why, citing this row |
| `CR-1064:470-490` (the lead's Decision 2) | #757 → W37-11 | **Not this slice's.** The review routes it to W37-11's leaf plan. Recorded here so the silence is not read as a miss |
| `CR-1064:558-568` (Verdict) | *"The plan survives its hardest slice. No slice moves, no id changes, no new slice"* | **Adopted as a constraint.** This plan changes no slice boundary, mints no requirement id and creates no slice. The one place it touches the cut is **DP-8.1**, which asks *where* a shared prerequisite lands (W37-7 or W37-8), not whether a slice moves |
| `CR-1064:537-541` (the W37-7 rows) and `CR-1064:545-553` (W37-9, W37-10, W37-11 rows) | Items routed to sibling slices | **Not this slice's, and not silently.** §2c (artifact B's locators) → W37-7; check-35's `W37-10` literal for F92 → W37-7; the venv-fix wording → W37-7; `CONTRIBUTING.md` and the PR template → W37-9; `docs/research/README.md` → W37-10; the pinned-base decision, the idempotence item, and row (g) with its `classified-by-none = 251` exit measurement (**review 13's own figure, measured pre-#757; #757 merged as `29e7a9c` and the current measured value is `207`, per that commit's squash body's per-class table — W37-11 works from `207`, not `251`**) → W37-11. **None is taken here.** §1.4 records the same exclusions from the other direction |

**The items the brief named and this plan could not confirm from `CR-1064`.** The dispatching
brief lists *"ci-watcher.md → W37-8"* among review 13's routings. **It is not review 13's.**
`grep -n "ci-watcher" docs/closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md`
returns nothing at `a8b3c39`. The routing is **`CR-1065` §2.4's**, and it is reconciled in §4.2
below. Recorded rather than quietly re-attributed, because a routing's source decides who may
change it.

### 4.2 Every item `CR-1065` (W37-6 checkpoint-3 close) routes to W37-8

Read at `origin/w37-6-checkpoint-3-close` while drafting; **`CR-1065` is now on `main`
(`d63f765`) and every line number below resolves identically there** — confirmed byte-identical
above, not re-derived.

| Source line | Item | This plan's answer |
|---|---|---|
| `CR-1065:285` (§2.4's row) and `CR-1065:327` (§2.4's reassignment table) | `.claude/agents/ci-watcher.md` — **NOT CLOSED — still pre-migration content**, last touched `3f41d60` (#616, pre-migration); *"Reassigned to **W37-8**, basis PL-939 `:760`, agents"* | **Taken as scope.** It is **Task 3**, placed first among the agent tasks, with its own §7 (i) ledger row in T13 step 4. Independently re-verified at `a8b3c39`: `grep -l "^family: reference" .claude/agents/*.md` returns only the README, so the file carries no governed header at this tree either |
| `CR-1065:88` (§1b, acceptance item (i)) | *"56 H/H+M rows sampled; 49 closed …; 7 gaps **REASSIGNED per file** to the slice owning that area (W37-7/8/9/10); W37-11 owns the fuller (i) walk"* | **Both limbs answered.** The one per-file gap assigned here is taken (row above). **The walk itself is not taken** — §1.4 records it as W37-11's, per this same line |
| `CR-1065:277-284` (§2.4's charter and agents rows) | All seven charters, `.claude/agents/README.md` and `.claude/agents/spec-reconciler.md` recorded **closed** at `71f5a22` / `4d9fe1d` | **Accepted as a (i) verdict and explicitly NOT accepted as a statement that W37-8's work is done.** §2.4's predicate is `/usr/bin/git log --oneline -1 -- <path>` — *last-touching commit*, which is a proxy for content. Measured directly at `a8b3c39`, **`spec-reconciler.md` carries no `family:` key at all** (`grep -l "^family: reference" .claude/agents/*.md` → README only) and **neither `reporter.md` nor `watcher.md` contains the sentence the map plan requires** (`grep -n "owns no governed document" …` → `GREP_EXIT=1`). **This is not a contradiction of `CR-1065` and no finding is proposed against it**: (i) asks whether a row is *named by a commit*, which it is; it does not ask whether §5.3's content clauses landed. This plan's scope is derived from §5.3's row text and measured at `a8b3c39`, exactly as `CLAUDE.md` §13's *"scope is derived from the specification first, then evidenced"* requires — never from a closure record's verdict column |
| `CR-1065:86` (§1b item 13) and `CR-1065:199` (§2.2) | The two named §5.4 content edits **REASSIGNED to W37-7**; the sweep-reaches-vendored mechanism gap filed as **F111, owner W37-11** | **Neither is this slice's.** §5.4 is W37-7's section; F111 is W37-11's. Recorded so the silence is not read as a miss |
| `CR-1065:402-446` (§5, *"What was not delivered"*) | The close's own deferred list | **Read in full; nothing in it names `.claude/roles/` or `.claude/agents/` beyond the `ci-watcher.md` row already taken.** Stated as a checked absence at this tree, not as a standing claim — an absence claim rots, so T1 re-reads §5 once `CR-1065` is on `main` |

### 4.3 The section's own completeness statement

Eleven rows across §4.1 and §4.2: six from `CR-1064`'s closed list and verdict, five from
`CR-1065`. **Two are taken as scope** (F97 as a disclosed candidate carried in DP-8.3;
`ci-watcher.md` as Task 3). **Nine are recorded as not-this-slice's with the slice that owns
them named.** **One is answered with a disclosed risk and a control** (§2b — scope derived before
the four disclosures merged; T1 step 1 is the control). **None is left silent.**

---

## 5. Acceptance Standard

The slice is complete when every item below passes. Each is a command a fresh reviewer can run
or a named artifact they can read. Items 1-4 are the map plan's own acceptance sentence
(`PL-00939-wk-697-one-id-per-governed-thing-map-plan.md:781-784`), quoted verbatim and then made
executable; items 5-8 are what plan review 13 and `CR-1065` added.

**The map plan's sentence, verbatim:**

> **Acceptance:** all seven charters and the agents files carry a valid header; the generated
> ownership matrix has no empty cell that is not one of the two declared ones; a dated maintainer
> line exists for every charter edit; the gate's two halves are green.

1. **All seven charters and the agents files carry a valid header.**
   `grep -L "^family: reference" .claude/roles/*.md .claude/agents/*.md` prints **nothing**, and
   `python3 scripts/doc-id.py check; echo EXIT=$?` prints `EXIT=0` with `0 file(s) skipped`.
   Additionally `python3 scripts/audit-docs.py | grep -c "check 30: \.claude/agents/"` prints
   **`0`** (it prints `7` at `a8b3c39`).
2. **The generated ownership matrix has no empty cell that is not one of the two declared ones.**
   Run the matrix invocation recorded in T1 step 4, verbatim. The reporter and watcher rows are
   present and **declared** empty; every other role row is non-empty. The output is pasted into
   the slice's ledger, so the claim is falsifiable rather than asserted.
3. **A dated maintainer line exists for every charter edit.** One line per edited file under
   `.claude/roles/`, on the PR, each carrying a date. The PR body lists the edited files, so the
   count of lines and the count of files can be compared without recollection.
4. **The gate's two halves are green.** Every command in T13 step 1 exits 0, each exit code
   recorded separately, both halves run. A Python-only run does not satisfy this item.
5. **`.claude/agents/ci-watcher.md` is closed by a named commit.**
   `/usr/bin/git log --oneline -1 -- .claude/agents/ci-watcher.md` names a commit in this slice's
   chain, not `3f41d60`. The commit and the file appear as a row in the ledger's §7 (i) table.
   (`CR-1065:327`.)
6. **The reporter and watcher charters each state that they own no governed document.**
   `grep -n "owns no governed document" .claude/roles/reporter.md .claude/roles/watcher.md; echo GREP_EXIT=$?`
   prints two lines and `GREP_EXIT=0` (it prints none and `1` at `a8b3c39`). (`PL-939:775-779`.)
7. **F97 has a disposition with a date.** Either a drafted `lead.md` clause with its own
   maintainer line, or a dated decline on the PR **naming the event that carries it forward**.
   Silence is not a disposition. (`CR-1064:154`, `:542`.)
8. **The four `FD-1066`…`FD-1069` disclosures were re-read in full after `CR-1065` merged**, and
   the ledger records either *"no W37-8 routing found"* or the routing and what was done about
   it. (`CR-1064:556`.)
9. **Every decision point in §6 that is marked blocking carries a resolver id**, and this plan's
   `status:` is `active`, before any task after T1 begins. (`docs/_templates/PL.md`'s freeze
   rule; `document-ids.md` §1.7.)
10. **`python3 scripts/doc-index.py --check` exits 0 and `git status --porcelain docs/INDEX.md`
    is empty after a fresh `python3 scripts/doc-index.py` run.** (Map plan Acceptance Standard
    item 2, applied at this slice's tree per its item 7.)

---

## 6. Decision points

Kind, blocking status and resolver per `document-ids.md` §1.7. A blocking row must carry a
resolver id before the slice it blocks may start; a non-blocking row names the step that
resolves it and the default applied until then. **None of these is ruled by this plan — the
planner never rules a decision point** (`.claude/roles/planner.md`, `Never:`).

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-8.1 | The seven `.claude/agents/*.md` and the 46 `.claude/skills/*/SKILL.md` share one unlanded prerequisite: the harness's `name:`/`description:`/`tools:`/`model:` keys must be **declared in `docs/_templates/REFERENCE.md`** before a merged governed header can parse (`scripts/doc-id.py:4718-4731`; `document-ids.md:136` *"Unknown field → lint failure"*). The template declares none of them at `a8b3c39`. Which slice lands that declaration — W37-8 (agents) or W37-7 (skills)? They run beside each other (`PL-939:377-380`), so neither can assume the other | (a) **W37-8 declares it** (T2) and W37-7 consumes it; (b) **W37-7 declares it** and W37-8 waits; (c) a third slice or a maintenance PR declares it before either starts; (d) each declares its own half — two blocks, two key lists | **(a).** W37-8's acceptance sentence says *"the agents files carry a valid header"*, and at `a8b3c39` no agent file can carry one — so W37-8 cannot pass its own acceptance without this, whereas W37-7's acceptance sentence (`PL-939:753-757`) names commits and a sweep, not skill headers. (d) is refused outright: a shape defined twice will diverge (`CLAUDE.md` §2). If the ruling is (b) or (c), **T2 is deleted from this plan and T3/T4 gain a dependency on the declaring PR** | scope — it moves one file's edit between two parallel slices | **yes** | decision-maker; **and the maintainer if amending `docs/_templates/` is an amendment to a `process/`-class artifact under `CLAUDE.md` §12 — that prior question is the first thing the ruling must answer** |
| DP-8.2 | §5.3's table names **two** agent files (`ci-watcher.md`, `spec-reconciler.md`); RFC-937 §4 step 5's stamp set is **all of `.claude/agents/`**, which is seven files at `a8b3c39`. Which population does W37-8 take? | (a) all seven; (b) the two §5.3 names, the other five deferred with a named owner; (c) the two names plus an `FD-` filed for the five | **(a).** The five are the identical class and the identical edit; the marginal cost is five citation sweeps in a commit already doing two. (b) leaves `python3 scripts/audit-docs.py \| grep -c "check 30: \.claude/agents/"` printing `5` with no slice owning it — a standing disclosure is how a gap becomes permanent. (c) files paperwork instead of doing 2 h of work. **The plan is written to (a) as its default**: T4 covers six files and the acceptance item 1 predicate is `grep -L` over the whole directory | scope | **yes** — it changes T4's file list and acceptance item 1's predicate | decision-maker |
| DP-8.3 | **F97's disposition** (`CR-1064:154`, `:542`) — the remedy is a new behavioural clause in `.claude/roles/lead.md`, a maintainer amendment under DP-6 | (a) draft it alongside the charter headers, with its own dated maintainer line; (b) **decline as W37-8 scope with a dated line naming the event that carries it forward** | **(b)** — this is plan review 13's own recommendation (*"disclosed candidate, not scope"*) and its reason is adopted: W37-8's acceptance is charter headers and §1.6 role content, and a behavioural clause is a different kind of change. **The decline must name its carrying event**; an unnamed carry is what made F97 a decayed row | scope | no — **T10 step 4 applies (b) as the default**, and the maintainer's line at the PR is the resolving step | lead at the PR; the maintainer if (a) |
| DP-8.4 | This plan's header carries no `slice:` field. `docs/_templates/PL.md` says `slice: SL-NNNNN` applies to a `kind: leaf` plan — but **no `SL-` row exists for W37-8**: `grep -c 'SL-' docs/roadmap.md` returns `0` at `a8b3c39`, and the roadmap records W37-* slices as named clauses inside the `WK-697` row | (a) omit the field (the template's *"remove any field this plan does not use"*); (b) mint an `SL-` id now with `doc-id.py next`; (c) carry `slice: W37-8` as a non-`SL-` label | **(a).** `SL-` rows are *"planner, cut in the map plan"* (`document-ids.md` §1.6) and `PL-939` is a frozen dated file — minting a row into it now is a retro-edit to a frozen plan. (c) puts a value in a field whose vocabulary is `SL-<n>` and would be read as one. **(b) is the right answer at the Work level and the wrong one at this slice's level**; whoever re-cuts the `SL-` rows should do it for all eleven at once, not for the one being drafted tonight | scope | no — default (a) applied; resolved when the `SL-` rows are minted for WK-697 as a set | planner, on the lead's instruction — not in this plan |
| DP-8.5 | Does `.claude/agents/README.md`'s **header** discharge §5.3's *"README names agents as Reference family owned by the lead"*, or must the **body** say it? The header already carries `family: reference` (`:2`) and `owner: lead` (`:6`); the body says neither | (a) body sentence required; (b) header suffices, row already closed | **(a).** §5.3's verb is *"names"* and its object is a README, which is a document a person reads; front matter is machine state. The cost is one paragraph. **If (b) is ruled, T5 reduces to its citation sweep** | design unknown — it is a reading of one word in a row | no — default (a) applied at T5 | lead, at the PR |
| DP-8.6 | §5.3 contains two further rows — `.claude/settings.json` (hook `statusMessage` citation, M) and the `notes/` stub directory under `.claude/` (19 stubs + README deleted, H + M). The map plan's W37-8 **scope sentence** enumerates charters, agents and the maintainer row and names neither; its **self-review** (`PL-939:907-910`) maps *"§5.3 → W37-8"* as a whole | (a) both are out of W37-8 — the scope sentence governs, and both were discharged in W37-6; (b) both are in — the section pointer governs; (c) settings.json in, notes out | **(a)**, contingent on verification. The stub directory's removal is a deletion the migration performed, and the `statusMessage` row is a citation rewrite in a non-Markdown file the migration's citation pass covered. **T1 step 3 verifies both before the exclusion is relied on**, and reopens this row if either contradicts it | scope | no — default (a), verified at T1 step 3 | lead, on T1's evidence |

---

## 7. ETA basis

**In hours of executor work, with no clock times.** The conversion to wall-clock windows is the
lead's, per plan review 13's own finding on the plan-of-record
(`CR-1064:451-464`): *"A schedule is a state that moves … Writing `16:30–18:30 BST, 18 Sep` into
a frozen plan creates a second copy that goes stale within hours of the first slip."*

| Task | What drives the estimate | Hours |
|---|---|---|
| T1 Baseline and preconditions | Six commands and a ledger entry; the cost is reading `CR-1065` §5 and the four `FD-`s once they are on `main`, not the commands | 0.5 |
| T2 `REFERENCE.md` licence | One template block, but step 5's narrowness proof is a second fixture and a second run; the ordering decision is the real cost | 1.5 |
| T3 `ci-watcher.md` | 154 lines, one citation sweep with a per-path `ls`, one merged header; the first of its class, so the shape is decided here | 1.5 |
| T4 Six agent files | Six citation sweeps at ~0.3 h each plus the class-closure and harness-survival checks; the header shape is already fixed by T3 | 2.0 |
| T5 `agents/README.md` | One paragraph plus a citation sweep over 194 lines | 1.0 |
| T6 reporter + watcher | Two short charter edits, but the matrix must be run and read, and §5.3's reporter row carries two further clauses (`WK-` status entry, `--slice-source` paths) | 1.0 |
| T7 `auditor.md` | 64 lines; four §1.6 cells to quote correctly; the self-reference caution applies | 1.5 |
| T8 `decision-maker.md` | 54 lines; six §1.6 cells; the one-ruling-per-file clause is a change of concept, not of wording | 1.5 |
| T9 `executor.md` | 114 lines; six clauses; the branch/PR convention must be cited to RFC-937 §5.1 rather than restated, which takes longer than restating it | 1.5 |
| T10 `lead.md` | 131 lines; eight §1.6 cells; the residual-clause **deletion** needs the matrix output read first, and F97's decline line drafted | 2.0 |
| T11 `planner.md` | 59 lines; two §1.6 cells; a wording change plus one added clause | 1.5 |
| T12 No maintainer charter | Three greps and a classification pass over the hits | 0.5 |
| T13 Gate, PR, DP-6 lines | Both gate halves (delegated), three id instruments, the index regeneration, the §7 (i) ledger table, the PR body | 2.0 |
| **Total** | | **18.0 h** |

**Three things this total does not include, named rather than buried:** wall-clock waiting on CI;
wall-clock waiting on the maintainer's DP-6 lines (T13 step 7), which gate the **merge** and not
the work; and the rework if **DP-8.1** is ruled (b) or (c), which deletes T2 (−1.5 h) and adds a
cross-slice dependency whose cost is a wait, not hours.

---

## 8. Risks

| # | Risk | Why it is real here | Mitigation |
|---|---|---|---|
| R1 | **DP-6 — a dated maintainer line is required per charter edit, and merging waits on it.** | `PL-939:770-773`: *"A charter is the maintainer's … the slice's acceptance requires a dated maintainer line on the PR before merge. This is a gate, not a blocker: drafting proceeds while the line is pending."* The same applies to **W37-9 for `CLAUDE.md`** — the two slices queue on the same person | **Drafting proceeds; merging waits. Say so on the PR.** T13 step 5 lists the edits awaiting lines explicitly, so the maintainer sees a checklist rather than a diff. Seven or eight lines are needed, not one |
| R2 | **The three roles working this slice are editing their own charters.** | T7 (auditor), T9 (executor), T11 (planner) | §2's named mitigation: the same maintainer line as every other edit, and the auditor's report states that T7 and T9 were audited against §5.3's row text rather than against the auditor's judgement of what the role should say |
| R3 | **A proxy predicate accepts what merely looks right.** `CR-1065` §2.4's *"closed"* column is `git log -1 -- <path>` — last touch, not content. Read as "done", it would empty this slice | Measured at `a8b3c39`: `spec-reconciler.md` is marked *closed* and has no `family:` key; `reporter.md`/`watcher.md` are marked *closed* and lack the map plan's required sentence | §1.2 derives scope from **§5.3's row text**, evidenced by the §1.3 predicates. §4.2 records the reasoning explicitly so a reviewer sees it was not an oversight |
| R4 | **Editing an agent's front matter can break the harness that reads it.** | `name:`, `description:`, `tools:`, `model:` are consumed by Claude Code, not by this repository's checks. A merged block that satisfies `doc-id.py` and loses `tools:` disables the agent silently | T4 step 5 asserts all four keys survive in all seven files. **The failure mode is silent, so the check is positive (count the keys), never "nothing broke"** |
| R5 | **The DISCLOSED pooled count is a ceiling with a definition, and this slice moves it.** | `DISCLOSED (957, at or under the W37-11 residue ceiling)` at `a8b3c39`; removing 7 check-30 rows changes it | T4 step 4 requires the delta to be **exactly 7** and forbids adjusting the number to fit: old ceiling minus this class's hits must equal the new count, or something else moved and must be found |
| R6a | **Superseded by this correction pass — kept as the record of what was true at drafting, corrected below rather than deleted.** At `a8b3c39`, before rebase: `audit-docs.py` gave `EXIT=1`/`FAILED (45)`, `doc-id.py check` gave `EXIT=1` with a gap between `1064` and `1070`, all 45 rows traced to the unmerged `1065`-`1069` block | **This correction pass rebased onto `origin/main` = `d63f765` and renumbered this plan from its drafting-time collision id (1070, shared with two sibling drafts) to **PL-1071**** (the lead's slice-order assignment: W37-7 keeps the first id in the freed block, W37-8 takes the second (this plan), W37-9 the third). Re-measured post-rebase, post-renumber, post-`doc-index.py`: `audit-docs.py` and `doc-id.py check` both give **exactly one** failure — `check 31: gap in the full allocation between 1069 and 1071` — because this branch, standing alone, carries this plan's own id without its slice-mate — W37-7's plan, one number lower — which is on a separate, not-yet-merged PR. **R6's original claim that "check 31 computes contiguity over merged records only" is corrected here: measured directly, it reads the current tree's regenerated `docs/INDEX.md`, whichever tree that is** — an unmerged local draft's own id shows up in the gap the moment `doc-index.py` is run over it, which `doc-id.py check`'s own gate step requires | **Proven by experiment: the renumbering itself is internally consistent, and the gap is purely merge order.** Copying W37-7's plan file (one id lower) and W37-9's plan file (one id higher) alongside this file and regenerating `docs/INDEX.md` gives `audit-docs.py` `EXIT=0`/`All checks passed.`, `doc-id.py check` `EXIT=0`, `doc-index.py --check` `EXIT=0` — then the copies were removed and this branch's own `docs/INDEX.md` restored to its standalone state. **The fix is the merge order**: once W37-7's plan lands on `main` and this branch is rebased, the gap closes without touching this plan's content |
| R6 | **This plan's id may collide with a sibling draft's.** | `python3 scripts/doc-id.py next` → `1070` at `d63f765` (post-rebase), which the lead's slice-order ruling supersedes with an explicit assignment rather than first-come allocation | **This plan takes `PL-1071`, the lead's assignment for W37-8 by slice order** (W37-7 lowest, this plan the middle id, W37-9 highest). Renumbering an undated draft is cheap and was done in this correction pass: filename, header `id:`, and the one self-citation at the title line |
| R7 | **`CONTRIBUTING.md` is W37-9's and unlanded, but T9 needs the branch/PR convention it will carry.** | `CR-1065:265-266`: both `CONTRIBUTING.md` and the PR template are *"NOT CLOSED — still pre-migration content"*, reassigned to W37-9 | T9's note: cite RFC-937 §5.1 for the convention and name `CONTRIBUTING.md` as the operative source **once W37-9 lands**. Do not restate the convention as an independent statement — two statements is how one goes stale |
| R8 | **An absence verified tonight is not an absence next week.** | §4.2's *"nothing in `CR-1065` §5 names `.claude/roles/`"* was measured at one branch tip at one time | T1 re-reads `CR-1065` §5 and the four `FD-`s once they are on `main`, and the ledger records the result. Acceptance item 8 makes it checkable |

---

## 9. Self-review

Run against RFC-937 §5.3 and the map plan's W37-8 section with fresh eyes, per `writing-plans`.

**1. Spec coverage.** All eleven §5.3 rows in §1.2's table map to a task: rows 1-7 → T7, T8, T9,
T10, T11, T6, T6; row 8 → T5; row 9 → T3; row 10 → T4; row 11 → T12. The five agent files outside
§5.3 → T4 under DP-8.2's default. The two §5.3 rows excluded (`settings.json`, `notes/`) are
named with their reason and verified at T1 step 3 rather than assumed. The map plan's four
acceptance clauses map to Acceptance Standard items 1-4. **One gap found and closed during this
review:** the first draft had no task for the merged-header prerequisite, which would have made
T3 and T4 unexecutable; it is now T2 and DP-8.1.

**2. Placeholder scan.** No "TBD", no "implement later", no "add appropriate content", no
"similar to Task N". Every prose edit names the §5.3 clause it must satisfy and the grep that
proves it landed. Two steps deliberately say *"read the flag from the tool"* rather than naming
it (T1 step 4, T2 step 2) — that is not a placeholder, it is the rule against writing a literal
from memory, and each names the exact command that reads it.

**3. Type consistency.** The header field set is used identically in T3 and T4 (`family`,
`title`, `status`, `created`, `owner`, `corrected_by`, `relates`, plus the four harness keys),
and T4 step 2 is explicit that the key ordering is byte-identical to T3's. The predicate
`grep -L "^family: reference"` is used with the same meaning in T4 step 3 and Acceptance Standard
item 1. `GREP_EXIT` is used consistently as `$?` of the immediately preceding grep.

**4. Freeze check.** DP-8.1 and DP-8.2 are blocking and carry no resolver, so `status: draft` is
required by `docs/_templates/PL.md`'s freeze rule independently of the deputy's undated
condition.

---

## 10. Execution handoff

**Not yet — but for a narrower reason than at drafting.** The deputy's 09:19 ruling discharges
the wait on plan review 13's acceptance line (reconciled against as a filed proposal instead,
§4 above) and W37-6's checkpoint 3 has landed as `CR-1065` on `main`. **What still holds this
plan in `draft` is DP-8.1 and DP-8.2**, both blocking with no resolver — no executor is spawned
and no implementation branch exists until the decision-maker/lead rules them and this plan is
dated. When the lead releases this slice, the choice is:

1. **Subagent-driven (recommended)** — a fresh executor per task, reviewed between tasks. The
   per-charter task cut in §3 was drawn for exactly this, because DP-6 approves charters one at a
   time.
2. **Inline execution** — batch the tasks with checkpoints, via `executing-plans`.

Either way the executor is spawned from `.claude/roles/executor.md`, never from an inline brief
(`CLAUDE.md` §15).
