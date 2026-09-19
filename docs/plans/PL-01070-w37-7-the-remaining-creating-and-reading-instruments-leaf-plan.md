---
id: PL-1070
family: plan
kind: leaf
title: W37-7 — The remaining creating and reading instruments: leaf plan
status: active
created: 2026-09-18
owner: planner
tree: a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
relates: []
---

# W37-7 — The remaining creating and reading instruments: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Goal

Bring every instrument `RFC-937` §5.4 names — and that `PL-939`'s slice section at
`:735-758` leaves to this slice after DP-1 — to say what the post-migration repository is
actually true of: the id grammar, the filing paths, the commands, the branch and PR forms,
and the marker form. Plus the three items plan review 13 routes here and the three file rows
the W37-6 checkpoint-3 close record reassigns here.

**Architecture:** This slice edits prose, one manifest at a time, plus one small code change
in `scripts/audit-docs.py` and one in
`.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py`. Nothing is generated;
nothing is migrated. `doc-id.py migrate` **must not be run** by this slice under any flag:
W37-6's run is done, and a second run is a re-migration of already-migrated text.

**Tech Stack:** Markdown; Python 3.12 for the two code tasks; `scripts/audit-docs.py`,
`scripts/doc-id.py check`, `scripts/doc-index.py --check`; `uv run pytest`.

**Spec:** `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`
§5.4 (the row table this slice discharges) and §1.4, §1.6, §1.10 (the content those rows must
now state). Plan of record: `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`
— the slice section at `:735-758` and the sequencing row at `:377`.

---

## Status of this draft — it is not frozen

**This plan is `status: draft`, and stays that way.** Per `docs/_templates/PL.md`'s freeze
rule (`§1.7`: *"`status: active` is permitted only when every blocking row in the Decision
points table below has a resolver id in its `Resolved by` cell"*), **DP-7-1 below is blocking
and carries no resolver — that is the only thing holding this plan in `draft`.** The two
further conditions this section named at drafting are both discharged by this correction pass,
not waited on further:

1. **Review 13 (`CR-1064`) still carries no dated maintainer acceptance line**, verified fresh
   at this pass's own base tree: `docs/closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md:632`
   reads `**Maintainer acceptance:** _pending_`. Per the deputy's ruling of **2026-09-18 09:19**
   (`~/gi-pricing-plan.local/channel/to-lead.md`): review 13 is *"a FILED PROPOSAL — reconcile
   against it now, do not wait for its acceptance line"*. The `## Reconciled against plan
   review 13` section below does exactly that — reconciles against `CR-1064` as a filed
   proposal — and this plan does not wait on the acceptance line landing. If that line, once
   written, amends any of the three items this plan takes from review 13, the amendment
   corrects this plan; that is the trigger, not a discretionary re-read.
2. **W37-6's checkpoint 3 is now on `main`, as `CR-1065`.** `docs/closures/CR-01065-w37-6-checkpoint-3-close.md`
   landed in `d63f765` (`git log --oneline -1 -- docs/closures/CR-01065-w37-6-checkpoint-3-close.md`
   → `d63f765 docs(closures): W37-6 checkpoint 3 — slice close record, register, roadmap row,
   ledger`), and is byte-identical to the branch revision this plan was drafted against
   (`git diff origin/w37-6-checkpoint-3-close:docs/closures/CR-01065-w37-6-checkpoint-3-close.md
   origin/main:docs/closures/CR-01065-w37-6-checkpoint-3-close.md` → empty). **Every "the CP3
   record" citation below is therefore replaced with `CR-1065`, at the same line numbers** —
   this is Task 0, named at drafting, now applied.

**No executor is spawned and no branch beyond this plan draft exists** until DP-7-1 carries a
resolver — the checkpoint-3 condition is discharged, and the deputy's ruling discharges the
review-13-acceptance wait, but neither reaches DP-7-1, which is a genuine, unresolved
disagreement between two governed records (see DP-7-1's own row). **The plan is dated —
that is, `status:` moves to `active` with `created:` unchanged — by the lead once DP-7-1
carries a resolver.** This correction pass discharges everything it can discharge and leaves
`status: draft` in place, correctly, rather than flipping it without a resolver — a `PL-`
`active` with an open blocking decision point fails `audit-docs.py` check 33.

**The gate on this draft, re-measured after rebase onto `origin/main` = `d63f765085fe6eb1c594177c5779ecfc3caf7ae8`**
(the tree this correction pass was written against), with `docs/INDEX.md` regenerated:

```
python3 scripts/audit-docs.py; echo EXIT=$?        → EXIT=0
python3 scripts/doc-id.py check; echo EXIT=$?       → EXIT=0
python3 scripts/doc-index.py --check; echo EXIT=$?  → EXIT=0
```

The 1065-1069 gap this section originally reported (`check 31: gap in the full allocation
between 1064 and 1070`, `doc-id.py check`'s matching `[noncontiguous]` row) is closed by the
rebase itself: those five ids — `CR-1065` and its four `FD-` findings — are now on `main`, so
the workaround this section described (materialise the CP3 branch's records, prove the gate
clean, then remove them again) is no longer needed. The gate is clean at the real, rebased
tree, measured directly rather than by simulation.

**Base tree for the plan's own body (everything below unless marked otherwise):**
`a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15` — `/usr/bin/git rev-parse origin/main` in worktree
`agent-a576ed4b6d959c619`, fetched that session. Clock at drafting:
`TZ=Europe/London date '+%Y-%m-%d %H:%M:%S %Z'` → `2026-09-18 02:33:55 BST`.

**Base tree for this correction pass:** `d63f765085fe6eb1c594177c5779ecfc3caf7ae8` — rebased
in a scratch worktree from `origin/main`, fetched this session. Clock:
`TZ=Europe/London date '+%Y-%m-%d %H:%M:%S %Z'` → `2026-09-18 09:26:50 BST`.

---

## Scope — the rows this slice owns

`PL-939:740-751` states the scope and is quoted here rather than paraphrased, because the
slice's acceptance is written against it:

> **Scope:** §5.4's rows, less whatever DP-1 moves into W37-6. In the order they matter:
> `docs-audit` (checks 30-39 described, the four-kinds paragraph and the `YYYY-MM-DD-` grammar
> removed, the tombstone check replaced by the redirects check); `dev-commands` (`doc-id.py
> next/check/widen`, `doc-index.py --check/--phase`); `git-hygiene` (branch `sl-<n>-<slug>`, PR
> title `SL-<n>: <title>`); `reporter-cycle` and its scripts (the fortnightly work-item status
> entry of §1.10 (a)); `repo-architecture` (the annotated `docs/` tree replaced by §1.4's);
> `python-test` and `testing-strategy` (the marker form); `brainstorming` and
> `planning-with-files` (one sentence each: scratch is not a family, the committed record is a
> plan or a ledger); `.claude/skills/README.md` (a "creates" column per creating skill); and the
> bespoke-audit rule that belongs in both `close-workstream` and `docs-audit` — **a bespoke
> audit is a slice whose record is a research document of kind `audit`, owner the auditor, every
> finding its own finding record; never a plan, never a closure.**

**DP-1 was resolved (a), owner W37-6** (`PL-939:302`): the seven creating skills —
`writing-plans`, `subagent-driven-development`, `adr-write`, `spec-change`,
`close-workstream`, `phase-review`, `library-spike` — were folded into W37-6's commit. Their
**stamps and citation rewrites** are therefore W37-6's and are not re-done here. Three of them
come back to this slice for a different reason, stated per row in the table below: their named
**content** edits did not land, which is a separate thing from their citations having been
rewritten.

### The full row list, by file

`H` = a hand-written content change §5.4 names. `M` = the mechanical stamp and citation
rewrite, which W37-6 performed. The "State at
`a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15`" column is measured, with the predicate given, not
recalled.

| # | File | §5.4 kind | What this slice must make true | State at the base tree, and the predicate that measured it | Task |
|---|---|---|---|---|---|
| 1 | `.claude/skills/docs-audit/SKILL.md` | H + M | Checks 30-39 described; the four-kinds paragraph and the `YYYY-MM-DD-` filename grammar removed; the tombstone check described as the redirects check | Partly landed. `grep -n 'YYYY-MM-DD' .claude/skills/docs-audit/SKILL.md` → `236:  content. A filename with none of those suffixes and no \`YYYY-MM-DD-\` date prefix either` — the retired grammar is still taught. The redirects rename **is** described (`:246-255`) | 1 |
| 2 | `.claude/skills/dev-commands/SKILL.md` | H + M | `doc-id.py next/check/widen` and `doc-index.py --check/--phase` documented as commands with their traps | Not landed as commands. `grep -c 'doc-id\|doc-index' .claude/skills/dev-commands/SKILL.md` → `1`, and the one hit (`:232`) is a `migrate --verify` env-var line inside the W37-6 verify recipe, not a `next`/`check`/`widen` entry | 2 |
| 3 | `.claude/skills/git-hygiene/SKILL.md` | H + M | Branch grammar `sl-<n>-<slug>`; PR title grammar `SL-<n>: <title>` | Not landed. `grep -n 'sl-<n>\|SL-<n>' .claude/skills/git-hygiene/SKILL.md` → no output | 3 |
| 4 | `.claude/skills/reporter-cycle/SKILL.md` + its scripts | H + M | The fortnightly work-item status entry of `RFC-937` §1.10 (a) | Not landed. `grep -n 'fortnight\|§1.10' .claude/skills/reporter-cycle/SKILL.md` → no output; the only `WK-` hit (`:25`) is a `WK-671` handover anecdote | 4 |
| 5 | `.claude/skills/repo-architecture/SKILL.md` | H + M | The annotated `docs/` tree replaced by `RFC-937` §1.4's | Not landed. `grep -n '§1.4\|document-ids' .claude/skills/repo-architecture/SKILL.md` → no output | 5 |
| 6 | `.claude/skills/python-test/SKILL.md` | H + M | The marker form `@pytest.mark.req("FR-<n>")` | **Landed** in W37-6's own chain (`4d9fe1d`, #783): `grep -n 'mark.req' .claude/skills/python-test/SKILL.md` → `16:@pytest.mark.req("FR-10")`. Verify only; do not re-edit | 6 |
| 7 | `.claude/skills/testing-strategy/SKILL.md` | H + M | The same marker form | Not landed: `grep -c 'mark.req' .claude/skills/testing-strategy/SKILL.md` → `0`. The skill teaches `pytest` markers generally and states no `req` form at all | 6 |
| 8 | `.claude/skills/brainstorming/SKILL.md` | H | One sentence: scratch is not a family; the committed record is a plan or a ledger | Not landed. `grep -cn 'scratch' .claude/skills/brainstorming/SKILL.md` → `0`. `CR-1065` `:301` records it: *"**NOT CLOSED — its own §5.4 one-sentence edit never landed**"*, reassigned here at `:335` | 7 |
| 9 | `.claude/skills/planning-with-files/SKILL.md` | H | The same sentence | Not landed. `CR-1065` `:302` calls it *"correctly excluded by design (RL-987/§6.3 — not a member)"* — that exclusion governs the **stamp**, not §5.4's content row. See DP-7-4 | 7 |
| 10 | `.claude/skills/README.md` | H + M | A "creates" column per creating skill | Not landed. `grep -n 'creates' .claude/skills/README.md` → one hit, `:453`, inside `ui-ux-pro-max`'s `--persist` note; no column exists in any skill table | 8 |
| 11 | `.claude/skills/close-workstream/SKILL.md` and `.claude/skills/docs-audit/SKILL.md` | H | The bespoke-audit rule, in both | Not landed in **either**, and `close-workstream`'s half was expected to be. `grep -rn 'bespoke' .claude/skills/close-workstream/SKILL.md .claude/skills/docs-audit/SKILL.md` → no output, while `PL-960:648` states the `close-workstream` half *"is in this commit, where the rule is **authored**"*. That is a plan-versus-tree disagreement, raised in Task 9 Step 1 | 9 |
| 12 | `.claude/skills/writing-plans/SKILL.md` | H (reassigned) | The retired filename grammar at `:18` replaced by the `PL-<nnnnn>-<slug>.md` form | Not landed. `grep -n 'YYYY-MM-DD' .claude/skills/writing-plans/SKILL.md` → `18:**Save plans to:** \`docs/plans/YYYY-MM-DD-<feature-name>.md\``. `CR-1065` `:187-194` and `:328` reassign it here | 10 |
| 13 | `.claude/skills/subagent-driven-development/SKILL.md` | H (reassigned) | The `LG-` ledger-append routing: where a ledger lives, what its id is, and that the append is the only permitted mutation | Not landed. `CR-1065` `:289` — *"**NOT CLOSED — still pre-migration content** (§2.2 confirms independently: zero diff 0651c1e..71f5a22)"*; reassigned at `:329` | 11 |
| 14 | `.claude/skills/watcher-runtime-state/` (SKILL.md + `scripts/write_runtime_state.py`) | added by review 13 §2c | The `read_from` locators the skill teaches must resolve | Not landed and actively wrong: `SKILL.md:84-85` teaches `--phase-source "docs/roadmap.md §7"`, and `grep -n '^## ' docs/roadmap.md` shows the headings run `## 6` → `## P1a` — **there is no `## 7`** | 12 |
| 15 | `scripts/audit-docs.py` check 35's owner literal | added by review 13 §4c | The printed owner tag aligns with F92's owner of record | Not aligned. `scripts/audit-docs.py:2936` prints a deferred-count note naming `owner: W37-10`, with `RL-1046` §B cited as its authority (written there in the padded file form, which is why it is described rather than quoted here); the lead ruled the owner of record is W37-11. See DP-7-1 | 13 |

**Not in this slice, stated so the silence is not read as an omission.** `CLAUDE.md` and the
public face are W37-9's (`PL-939:785`). The charters, `.claude/agents/README.md` and
`.claude/agents/ci-watcher.md` are W37-8's (`PL-939:760`; `CR-1065` `:327`). `docs/` READMEs,
the checklists and `docs/research/README.md` are W37-10's (`PL-939:815`; `CR-1065` `:330`). The
fuller `RFC-937` §7 (i) walk across all roughly ninety H / H+M rows is W37-11's, not this
slice's — `CR-1065` `:315-318` is explicit that its 56-row table *"is not (i)'s exhaustive
discharge"*. This slice closes the rows listed above and makes no claim about the rest.

---

## Global Constraints

Every task's requirements implicitly include these. Values are copied verbatim from the
source named.

- **`CLAUDE.md` §12, vendored files:** *"Vendored files stay as upstream wrote them, excluded
  from `ruff`, every deviation recorded in the README rather than made silently."* Rows 8, 9,
  12 and 13 above are edits to vendored manifests. See DP-7-3.
- **`PL-939:737-738`:** *"**Executor skill:** `writing-skills`. Every skill touched has its
  `Verified` date refreshed in the same commit (`CLAUDE.md` §12)."*
- **`CLAUDE.md` §13, references:** a count carries the tree, the corpus and **the predicate** —
  the command verbatim and runnable. Every number this slice writes into a skill, a PR body or
  the ledger carries all three.
- **`CLAUDE.md` §5:** requirement ids and section numbers are permanent. This slice mints no
  requirement id and renumbers nothing. If a §5.4 row turns out to be wrong rather than
  unlanded, it is **marked superseded with a dated note**, never silently rewritten, and the
  spec-vs-plan conflict is the lead's to rule (`delivery-process.md` §3) — not the executor's.
- **`doc-id.py migrate` is never run by this slice**, under any flag, including `--verify`
  against a fresh root. The verify command spawns its own scratch trees
  (`.claude/skills/dev-commands/SKILL.md:275`) and is W37-6's and W37-11's instrument, not
  this slice's.
- **Both gate halves before every push** (`CLAUDE.md` §11). A Python-only gate has been green
  here while the frontend was red.
- **One commit per task**, Conventional Commits, branch off `main`, squash-merge — and the
  branch grammar this slice is *writing into `git-hygiene`* is not yet in force for this
  slice's own branch, because no `SL-` id has been minted for W37-7 (see "The `slice:` field"
  below).

### The `slice:` field, and why this header omits it

`docs/_templates/PL.md` lists `slice: SL-NNNNN` as a `kind: leaf` field and says to *"remove
any field this plan does not use."* **No `SL-` id exists at the base tree** — `grep -n 'SL-'
docs/INDEX.md` returns no output, and `PL-939:692` describes the `SL-` rows as something the
map plan *will* mint. `PL-960`, the W37-6 leaf plan and the only other leaf plan in the tree,
carries no `slice:` field either (`docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md:1-14`).
This header follows that precedent. **If the lead mints `SL-` rows before this plan is dated,
the field is added then**; it is not invented here, because a plan that names an id nobody
minted is exactly the dangling locator review 13 §2c raises.

---

## Reconciled against plan review 13

**This section is mandatory and is written against a closed list.** `CR-1064:533-546` states
the rule and the list: *"Nothing outside this list is owed to review 13, so a drafter can
discharge the section and know they are done."* Review 13 produces **three** items for W37-7.
Each is answered below with the source line, the disposition, and where in this plan it lands.
The two other sources this section reconciles against — the checkpoint-3 close record and the
items review 13 routes **away** from this slice — follow the three.

**Standing caveat on all of it.** `CR-1064` carries no dated maintainer acceptance line at the
base tree, and `CLAUDE.md` §14 makes a review *"a proposal, never a change"* that *"binds
nothing until dated"*. Everything below is therefore a reconciliation against a proposal. If
the acceptance line amends any of the three items, this plan is corrected before it is dated —
that correction is the trigger, not a discretionary re-read.

### The three items review 13 routes here

**R13-1 — artifact B's dangling `read_from` locators. `CR-1064:539`.** The review's words:
*"`write_runtime_state.py`'s `position` block is stale and both its `read_from` locators dangle
post-migration (the dated-form leaf-plan path it names no longer exists; `docs/roadmap.md:382`
is `## Historical record`)"*, and *"This review recommends yes — it is a reading instrument,
which is W37-7's own definition."*

**Disposition: taken. Task 12.** The recommendation is accepted without amendment. Two facts
this plan adds, because they change the *shape* of the fix rather than whether to take it:

- The dangling locators live in the **state file**, which is
  `$RUNTIME_STATE_FILE`, default `~/gi-pricing-plan.local/handover/runtime-state.json`
  (`.claude/skills/watcher-runtime-state/SKILL.md:8-9`) — **outside this repository**, as
  `RFC-895` §10 requires of runtime state. They are not literals in the script: they arrive
  as `--phase-source` / `--work-source` / `--slice-source` arguments and are stored verbatim
  (`scripts/write_runtime_state.py:141-145`). A repository commit therefore cannot fix the
  live file, only the instrument that writes it and the examples that teach it.
- The instrument's own taught example is independently wrong at the base tree, which review 13
  did not measure: `SKILL.md:84-85` uses `--phase-source "docs/roadmap.md §7"`, and
  `docs/roadmap.md` has no `## 7` heading (`grep -n '^## ' docs/roadmap.md` → `## 6` at
  `:174` then `## P1a` at `:188`). So the skill teaches a dangling locator to every future
  watcher, not only to the one that ran.

This is why the task is a **fail-closed validation** plus a documentation fix, not a one-off
correction. DP-7-2 carries the choice about the live file, which is an ops action and not a
repository change.

**R13-2 — check 35's `W37-10` owner literal. `CR-1064:540`.** The review's words: *"check-35's
`W37-10` owner literal for F92 must align to the owner of record; W37-10's scope does not
contain code"*, and at `:377-378`: *"**Recommendation: the tag alignment is W37-7's**
(instruments), named in W37-7's leaf plan when drafted, not left as 'for W37-7/8 to align'
without a row."*

**Disposition: taken, and it is named — Task 13.** The routing is accepted: W37-10's scope
(`PL-939:815`) is `docs/` READMEs, checklists and the three rituals, and a literal inside
`scripts/audit-docs.py` is not in it. **What this plan cannot do is pick the literal**, because
the two authorities disagree and neither is the planner's to overrule: the lead ruled F92's
owner of record is W37-11 (`CR-1064:372`, quoting the 00:55:09 BST relay), while `RL-1046`
§B — a frozen ruling the code cites by id in its own output — assigns the residue classes to
W37-10 and says so at `:113`: *"all three are W37-10's by the map plan's slice"*. Aligning the
printed tag to W37-11 while the cited ruling says W37-10 moves the drift rather than removing
it. **DP-7-1 carries the options and a recommendation; it is blocking, and this plan does not
freeze until it has a resolver.**

**R13-3 — the venv fix is exclusion-by-construction, not a refusal guard. `CR-1064:541`.** The
review's words: the draft must say *"That the `dev-commands` / `doc-id-migration-run` text says
so, so no redundant guard is proposed"*, sourced at `:411` to the auditor's *"No literal
refusal guard exists"*.

**Disposition: taken. Folded into Task 2**, as a named step with its own verifying grep, and
into the same task's touch of `.claude/skills/doc-id-migration-run/`. It is not a separate
task: it is one paragraph in a file Task 2 is already rewriting, and `writing-plans`'
right-sizing rule folds documentation into the task whose deliverable needs it.

### What the checkpoint-3 close record routes here

**`CR-1065` is now on `main` (`d63f765`)** — no longer read via a branch `git show`. Three file
rows come here, each with its source line:

| Item | Source | Disposition |
|---|---|---|
| `.claude/skills/writing-plans/SKILL.md` — the retired filename grammar at `:18` | `CR-1065` `:187-190` (the H content edit *"did not land"*) and `:328` (*"**W37-7** — PL-939 `:735`, instruments — the same content-edit gap §2.2 already reassigns there"*) | **Taken. Task 10** |
| `.claude/skills/subagent-driven-development/SKILL.md` — the `LG-` ledger-append routing | `CR-1065` `:189-191` and `:329` (*"**W37-7** — PL-939 `:735`, instruments — same basis"*) | **Taken. Task 11** |
| `.claude/skills/brainstorming/SKILL.md` — its §5.4 one-sentence edit | `CR-1065` `:301` (*"**NOT CLOSED — its own §5.4 one-sentence edit never landed**"*) and `:333-335` (*"reassigned to **W37-7** on the same basis, stated rather than picked silently, since no other slice's leaf plan claims it"*) | **Taken. Task 7**, together with its §5.4 row-mate `planning-with-files` — see DP-7-4 |

`CR-1065` `:85` also records item 12 of the auditor's checklist as *"**not started — W37-7's, not
W37-6's**"* (requirement-facing proof). This plan reads that as a statement of ownership, not
as an additional deliverable beyond the rows above: the proof that the instruments now teach
the right forms **is** Acceptance Standard items 1-8 below.

### What review 13 routes elsewhere, recorded so this slice does not take it

Listed because a slice that stays silent about a neighbouring routing is how the same item
gets done twice or not at all. Each is `CR-1064:542-546`.

| Item | Routed to | Source |
|---|---|---|
| F97's disposition — remedy touches `.claude/roles/lead.md` | **W37-8** | `CR-1064:542` |
| `.claude/agents/ci-watcher.md` (pre-migration content) | **W37-8** | `CR-1065` `:327` |
| `CONTRIBUTING.md` and `.github/PULL_REQUEST_TEMPLATE.md` | **W37-9** | `CR-1065` `:325-326` |
| Nothing at all from review 13 bears on W37-9 | **W37-9** | `CR-1064:543` — *"'No item from review 13 bears on this slice' — stated, not omitted"* |
| `docs/research/README.md` (the one missing path) and the F87/F90 register-currency line | **W37-10** | `CR-1065` `:330`; `CR-1064:544` |
| The pinned-base decision, the idempotence item, and row (g) with g2 = `207` | **W37-11** | `CR-1064:545` and `:581`. The `207` is the merged figure: `29e7a9c fix(scripts): row (g) g2 classifier — forward-citation check + bare finding-id exclusion (251 → 207 classified-by-none; (g) stays the standing FAIL) (#757)`, `/usr/bin/git log --oneline -3 origin/main` at the base tree |
| The mechanism gap behind the sweep reaching files beneath a vendored manifest | **W37-11** | `CR-1065` `:199-202` — *"a `migrate()` change under the reproduction rule, not a content edit"* |

**Review 13's shape answer, quoted because it is the licence this plan operates under**
(`CR-1064:581`): *"**The W37-7…11 cut holds. No slice moves, no id changes, no new slice.**"*
The only scope addition it proposes anywhere is R13-1, to this slice (`CR-1064:307-308`:
*"This is an **addition to W37-7's scope**, and it is the only scope addition this review
proposes"*). This plan therefore adds nothing of its own invention to the slice; every row in
the scope table traces to `RFC-937` §5.4, to `PL-939:740-751`, to `CR-1064` or to `CR-1065`.

**Corrected 2026-09-19 (planner, on the deputy's ruling of the same date).** The words above —
*"This plan therefore adds nothing of its own invention to the slice; every row in the scope
table traces to `RFC-937` §5.4, to `PL-939:740-751`, to `CR-1064` or to `CR-1065`."* — no longer
hold, and are annotated rather than edited so the claim the plan made about itself at freeze
survives beside the reason it stopped being true. **Task 15 adds a scope row that traces to none
of those four.** It traces to the deputy's ruling of 2026-09-19, which is dated after this plan
was written: reconcile two unmerged commits carrying ruled `audit-docs.py` check dispositions,
salvaged from the root checkout's branch, against `main`. The provenance rule the sentence states
is not being relaxed — a row still may not enter this table by a planner's invention, and no
other row has. It is being **extended by one named authority**, recorded here rather than
absorbed silently, because a plan that widens its own scope table while still asserting it
invented nothing is making a claim its contents contradict. Every other row's trace is unchanged.

**Extended 2026-09-19 (planner, on the deputy's ruling of the same date).** The words above —
*"It is being **extended by one named authority**"* — are corrected: the extension is **not
limited to one**. Task 16 is a second row traceable to a ruling dated after this plan was
written, and enumerating the exception where a rule was needed is the same defect as pasting a
count into an acceptance item — the author of this annotation committed both on the same day,
which is why the correction is recorded rather than quietly widened again. **The rule, stated so
it does not need extending a third time:** a row may enter this plan's scope table only by
tracing to `RFC-937` §5.4, to `PL-939:740-751`, to `CR-1064`, to `CR-1065`, **or to a dated
ruling recorded in this plan's decision-points table**. Each such row names its ruling and its
date in its own task header. No row enters by a planner's invention, which is the invariant the
original sentence was written to protect and which is unchanged.

---

## Decision points

Kind, blocking status and resolver per `RFC-937` §1.7. A blocking row must carry a resolver id
before the slice it blocks may start; a non-blocking row names the step that resolves it and
the default applied until then.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-7-1 | Check 35's printed owner tag for F92's deferred population. The lead ruled the owner of record is **W37-11** (`CR-1064:372`); the ruling the line itself cites, `RL-1046` §B, says **W37-10** (`docs/rulings/` `RL-1046`'s file, line 113). The literal also appears as the identifier `_is_stamp_deferred_w37_10` and in three test files (`tests/test_audit_docs_ids.py:684`, `:1630`; `tests/test_register_lint.py:547`; `tests/test_doc_id_verify.py:1881`, `:1894`) | (a) print `owner: W37-11` and leave `RL-1046` §B cited as-is; (b) print `owner: W37-11 (deferred under RL-1046 §B, which named W37-10; owner of record reassigned)` and rename the helper to carry no slice tag — `_is_stamp_deferred_f92`; (c) leave `W37-10` and file the misalignment as a finding for W37-11 | **(b)**. (a) makes the sentence self-contradicting on its face — a reader following the citation lands on a ruling that says the other thing, which is exactly the class `RFC-779` names. (c) defers a one-line edit into the slice whose job is to *prove* the corpus consistent. (b) removes the slice tag from the identifier entirely, so the next reassignment cannot produce this row again — a naming that cannot go stale, not a corrected copy of one | decision point — it is a code edit whose content two governed records disagree on | **yes** | `RL-1075` |
| DP-7-2 | How far does the artifact B fix reach? The `read_from` values are arguments, not literals, and the live file is outside the repository (`~/gi-pricing-plan.local/handover/runtime-state.json`) | (a) repository-only: fix `SKILL.md`'s taught invocation and make `write_runtime_state.py` **refuse** a `--*-source` locator whose file path does not exist, so a dangling locator cannot be written again; (b) (a) plus a one-off rewrite of the live state file by the watcher, recorded in the slice ledger as an ops action; (c) documentation only | **(b)**, with (a) as the repository deliverable and the live rewrite handed to the watcher as a named ops step. (c) leaves the instrument able to mint the same defect tomorrow; (a) alone leaves a live file that three roles read as authoritative (`SKILL.md:75`: *"read `runtime-state.json`, not the roadmap"*) still carrying two dangling locators | design unknown — the mechanism is settled; the reach is not | no — default (a) applies, and Task 12 delivers it either way | Task 12's review, the lead |
| DP-7-3 | Rows 8, 9, 12 and 13 are content edits to **vendored** manifests. `CLAUDE.md` §12: *"Vendored files stay as upstream wrote them … every deviation recorded in the README rather than made silently."* | (a) make the four edits and record each as a numbered deviation in `.claude/skills/README.md` in the same commit; (b) refuse them and mark the four §5.4 half-rows superseded with a dated note; (c) fork the four skills out of the vendored set | **(a)**. The README already carries three such recorded deviations for this exact set of files (`.claude/skills/README.md:159` — *"One deviation from upstream: where a plan is saved"*, which already changed `writing-plans`' save path once; `:178` — the `task-brief` script changes; `:277`). §12's rule is *record it*, not *never*; (b) would leave the instruments teaching retired forms, which is the whole point of the slice; (c) is an architecture change needing an ADR | scope — it decides whether four rows are delivered or superseded | no — default (a) applies | Task 7's review, the lead |
| DP-7-4 | `planning-with-files` is half of §5.4's *"`brainstorming`, `planning-with-files` — one sentence each"* row, but `CR-1065` `:302` records it as *"correctly excluded by design (RL-987/§6.3 — not a member)"* | (a) make the sentence edit anyway — §6.3's exclusion governs the **stamp**, and §5.4's row governs the **content**, which are two different obligations; (b) treat the exclusion as covering the content row too and mark that half superseded with a dated note | **(a)**. The two rules answer different questions: `RL-987`/§6.3 decided whether the migration *stamps and rewrites* the file; §5.4's row is about what the file *teaches*. `CR-1065` `:302` itself keeps the row-mate alive in the same sentence (*"its row-mate `brainstorming` was the member, and see the row above"*), which only makes sense if the content row survived the membership decision | scope | no — default (a) applies | Task 7's review, the lead |
| DP-7-5 | `docs/INDEX.md` is regenerated by `scripts/doc-index.py` and W37-7, W37-8, W37-9 and W37-10 may run beside each other (`PL-939:379-382`). Four concurrent branches each regenerating one generated file is a guaranteed conflict | (a) each slice regenerates `docs/INDEX.md` in its own final commit and resolves conflicts by **regenerating, never by hand-merging**; (b) no slice touches `docs/INDEX.md` and W37-11 regenerates it once; (c) serialise the four slices | **(a)**, with the rule stated in each slice's PR body: a generated file is never conflict-resolved by hand (`CLAUDE.md` §2's *"`docs/contracts/` is generated and never hand-edited"* is the same principle applied to the other generated artifact). (b) leaves `doc-index.py --check` red on every intermediate merge, which disarms the gate for the whole of Stage 3 | decision point — it affects three other slices, so it is the lead's, not this plan's | no — default (a) applies | The lead, before the first Stage 3 executor is spawned |
| DP-7-6 | `docs/REDIRECTS.csv` reserves a block of identifiers — the 1063 mark to the 1136 mark — for legacy register rows that never materialise as files and never reach `docs/INDEX.md`, so the allocator cannot see them. The marks are written bare, not as family-qualified id tokens, for the reason `RFC-937:30` gives: a literal specimen is indistinguishable from a citation, and check 32 would read one end as dangling and the other as resolving to an unrelated live document. Two harms, both re-derivable at any tree with the commands in Task 16 Step 1: **(i)** the block intersected with every `INDEX.md` id number, any family — **reuse of a reserved number**, breaking `RFC-937` rule 1's one-sequence-per-corpus invariant and check 31; **(ii)** the same filtered to `FD-` — **mis-resolution**, one id naming two governed things. Measured at `3803331`: (i) fifteen, consecutive, (ii) five. Measured again at `a800c57`: (i) sixteen. **It grows by one with every document this work item mints** | (a) **a fifth scanner** — teach `compute_next` to read `REDIRECTS.csv`'s reservations alongside its four existing sources; (b) **re-point the legacy block** so those rows no longer reserve numbers that are live; (c) **reserve above the block's top**, minting only above the 1136 mark | **(b) as the remedy, with (a) as the guard, in one commit.** The cross-cutting question — which side of the existing collisions moves — is already answered twice over, and not by this plan: `CLAUDE.md` §5 makes requirement and document ids permanent, and `RFC-937` §1.7 says *"a collision at rebase is fixed by renumbering the unmerged item"*. Every colliding document is merged. **The minted side cannot move**, so the legacy rows move or nothing does. (b) is the only option that both resolves the existing collisions and stops (i) growing; (a) alone stops the growth but leaves every current collision standing, and (c) stops the growth by converting the collision into a permanent hole in a sequence the standard requires to be one, while teaching the allocator nothing — the next reserved block reintroduces the identical defect. (a) is therefore not an alternative to (b) but its durable half: after (b) the allocator still cannot see a reservation, and the only reason it would not happen again is that nobody reserved anything. **A fix scoped only to (ii) is rejected outright**: it silences the mis-resolution while leaving the standard's invariant broken and the allocator still minting reused numbers on every document | decision point — `RFC-937` §1.7 names four sources and `compute_next` implements four, so **the standard and the tool are both wrong in the same place**. It is resolved in one commit changing both, never one side silently (`CLAUDE.md` §2) | **yes** — blocks Task 16 only; every other task proceeds. **No default applies**: the three options edit different files in incompatible ways, so a default would mean building the wrong one and reverting it | `RL-1078` |

**Superseded 2026-09-19 by `RL-1078`.** This recommendation — (b) as remedy with (a) as guard
— was **rejected on evidence it did not have**: `docs/INDEX.md` is contiguous with zero gaps, so
check 31's contiguity clause is load-bearing, and all three drafted options open a hole in the
allocation that reds it. The ruled remedy is (a) **in substance**, implemented at
`scripts/doc-index.py` rather than as a fifth `compute_next` scanner, which leaves `RFC-937`
§1.7's four sources correct as written. The recommendation is kept quoted because the ruling's
reasoning is only legible beside what it refused. See Task 16.

---

## Tasks

Fourteen tasks. Each ends with one commit and an independently runnable verification. The
executor is spawned from `.claude/roles/executor.md` with `writing-skills` as the slice's
executor skill (`PL-939:379`, `:737`); the auditor for this slice is spawned from
`.claude/roles/auditor.md` and re-checks every task — `executor.md:38` forbids self-audit.

**Before Task 1** — in the worktree, once:

```bash
python3 scripts/audit-docs.py > /tmp/w377-audit-baseline.log; echo EXIT=$?
python3 scripts/doc-id.py check; echo EXIT=$?
python3 scripts/doc-index.py --check; echo EXIT=$?
```

Record all three exit codes in the slice ledger as the **baseline**. A check that is already
red at the base tree is not this slice's regression, and a check that goes red later is only
attributable if the baseline was written down first.

---

### Task 1: `docs-audit` — the filename grammar, and the bespoke-audit rule's first home

**Files:**
- Modify: `.claude/skills/docs-audit/SKILL.md` (the `YYYY-MM-DD-` passage at `:236`; the
  checks-30-39 description; `Verified` date)

- [ ] **Step 1: Read the passage and its neighbours before editing**

```bash
sed -n '225,260p' .claude/skills/docs-audit/SKILL.md
```

The retired grammar is at `:236`. The redirects rename is already described at `:246-255`;
confirm it before touching it, because the §5.4 row asks for a replacement that has partly
happened and an edit that assumes otherwise will undo it.

- [ ] **Step 2: Replace the filename-grammar sentence**

The sentence must state the `RFC-937` §1.3 grammar — `<FAMILY>-<nnnnn>-<slug>.md` — and must
not describe `YYYY-MM-DD-` as a live form. Where the historical form needs naming (a frozen
record still carries it), it is named as **retired**, with `docs/REDIRECTS.csv` as the way a
reader resolves an old path.

- [ ] **Step 3: Confirm checks 30-39 are each described**

```bash
grep -c 'check 3[0-9]' .claude/skills/docs-audit/SKILL.md
```

Then walk `scripts/audit-docs.py`'s module docstring — which `CLAUDE.md`'s skill index states
is the numbered list, *"kept current there rather than counted here"* — and confirm every one
of 30 through 39 has a paragraph in the skill. Add the missing ones.

- [ ] **Step 4: Refresh `Verified`**

- [ ] **Step 5: Verify**

```bash
grep -n 'YYYY-MM-DD' .claude/skills/docs-audit/SKILL.md          # expect: no live-form hit
python3 scripts/audit-docs.py; echo EXIT=$?                       # expect EXIT=0
```

- [ ] **Step 6: Commit** — `docs(skills): docs-audit — RFC-937 filename grammar, checks 30-39`

**ETA basis:** 2.0 h of executor work. The file is large and the checks-30-39 walk is a
ten-way comparison against the script's docstring, not a single edit.

---

### Task 2: `dev-commands` — the `doc-id` and `doc-index` commands, each with its trap

**Files:**
- Modify: `.claude/skills/dev-commands/SKILL.md`
- Modify: `.claude/skills/doc-id-migration-run/SKILL.md` (the exclusion-by-construction
  paragraph — R13-3)

**Interfaces:**
- Produces: the canonical command forms that Tasks 3, 8 and 14 cite rather than restate.

- [ ] **Step 1: Read the five commands' real behaviour from the scripts, not from memory**

```bash
python3 scripts/doc-id.py next --help
python3 scripts/doc-id.py check --help
python3 scripts/doc-id.py widen --help
python3 scripts/doc-index.py --help
```

- [ ] **Step 2: Write the five entries, each with the trap that makes the obvious form wrong**

`CLAUDE.md` §11's standard for this file: *"Every command has a trap that makes the obvious
form wrong."* Two traps are already measured and must appear:

- `doc-id.py next` prints a **diagnostic line before the integer** at the base tree —
  `python3 scripts/doc-id.py next` returned `doc-id.py next: 0 file(s) skipped (front matter
  present but did not parse as RFC-937's header):` followed by `1065`. A caller doing
  `ID=$(python3 scripts/doc-id.py next)` captures both lines, not the number. State the
  correct form (take the last line) and why.

  **Corrected 2026-09-19 (planner, this plan's author).** The words above — *"A caller doing
  `ID=$(python3 scripts/doc-id.py next)` captures both lines, not the number. State the correct
  form (take the last line) and why."* — are **false**, and are annotated here rather than
  edited (this slice's annotate-in-place rule), so the record of what was believed survives.
  The two lines go to **different streams**: `_report_skipped()` writes the diagnostic with
  `file=sys.stderr` (`scripts/doc-id.py:10253-10268` at the tree named below), and `_cmd_next()`
  writes the integer with a bare `print(result.number)` to stdout (`scripts/doc-id.py:10278`,
  same tree). Command substitution captures stdout only. The capture form this step calls
  broken is therefore **correct as written**, and the remedy it prescribes — "take the last
  line" — has nothing to strip.

  Measured at tree `7d5d6e0a3730bfd790dace3a95c63a0ea71ec031`, worktree clean
  (`/usr/bin/git status --porcelain` empty), three ways: `python3 scripts/doc-id.py next` at a
  terminal prints the diagnostic and then the integer; `python3 scripts/doc-id.py next
  2>/dev/null | od -c` prints the integer's digits, one `\n`, and nothing else;
  `ID=$(python3 scripts/doc-id.py next)` leaves the diagnostic on the terminal, uncaptured,
  with `ID` holding the bare integer. That third run is how the error was made — on screen the
  two lines look like one captured pair, because only one of them was ever captured.

  **What Step 2 requires instead:** write **one** trap for `next`, not two. The real one is
  allocation, already stated in Risk 4 of this plan: `next` defaults to `--ref origin/main`
  (`python3 scripts/doc-id.py next --help` → *"Git ref to read (default: origin/main)."*), so an
  id already held by a record on an unmerged branch is invisible to it and concurrent drafters
  are handed the same integer without either being wrong. Write no stream-capture trap; there
  is none.

  **And write no allocation number into the skill, or into this plan.** The integer in the
  sentence above this annotation is a property of the tree it was run at, not a fact about the
  command, and it had already changed by this annotation's tree. Record the command and the
  rule — run `python3 scripts/doc-id.py next` at the head you branch from, then reconcile with
  the lead before push — never a pasted value, which goes stale by exactly the
  duplicated-constant mechanism of `RFC-756`.
- `doc-id.py next` allocates against records reachable from `origin/main`, so **two planners
  drafting the same night both get the same integer** and neither is wrong. The reconciliation
  is the lead's before push. This plan is itself an instance — see the report.

- [ ] **Step 3: Add the exclusion-by-construction paragraph (R13-3)**

In `dev-commands`, at the `migrate --verify` entry, and in
`.claude/skills/doc-id-migration-run/SKILL.md`: the sweep does not reach a gitignored path
because `_enumerate_tree(root)` enumerates via `git ls-files -z --cached --others
--exclude-standard` — **exclusion by construction, not a refusal guard**. State in the same
sentence that *no literal refusal guard exists* and that adding one would be redundant, so a
future reader looking for the guard stops looking instead of writing one.

- [ ] **Step 4: Refresh `Verified` on both files**

- [ ] **Step 5: Verify**

```bash
grep -c 'doc-id.py next\|doc-id.py check\|doc-id.py widen' .claude/skills/dev-commands/SKILL.md
grep -c 'doc-index.py --check\|doc-index.py --phase' .claude/skills/dev-commands/SKILL.md
grep -n 'by construction' .claude/skills/dev-commands/SKILL.md .claude/skills/doc-id-migration-run/SKILL.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

- [ ] **Step 6: Commit** — `docs(skills): dev-commands — doc-id/doc-index commands and their traps`

**ETA basis:** 2.5 h. Five command entries, each needing its behaviour read from the script
rather than assumed, plus the two-file R13-3 paragraph.

---

### Task 3: `git-hygiene` — the branch and PR-title grammars

**Files:**
- Modify: `.claude/skills/git-hygiene/SKILL.md`

- [ ] **Step 1: Add the two grammars where the existing branch-naming guidance lives**

Branch: `sl-<n>-<slug>`. PR title: `SL-<n>: <title>`. Both verbatim from `PL-939:743`.

- [ ] **Step 2: Note the interaction with the worktree guard that the file already records**

`.claude/skills/git-hygiene/SKILL.md:101` already states *"A branch name containing the
substring 'git' can trip the worktree isolation guard."* The new grammar makes branch names
derive from a slice slug, so add one line: a slug containing `git` produces exactly that
trip. This is a real, already-recorded hazard meeting a new naming rule, and the two belong
in the same paragraph.

- [ ] **Step 3: State what the grammar does not yet apply to**

No `SL-` id exists at this tree, so the grammar binds from the point the map plan mints the
`SL-` rows. Say so with that condition, not with a date.

- [ ] **Step 4: Refresh `Verified`**

- [ ] **Step 5: Verify**

```bash
grep -n 'sl-<n>-<slug>' .claude/skills/git-hygiene/SKILL.md
grep -n 'SL-<n>: <title>' .claude/skills/git-hygiene/SKILL.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

- [ ] **Step 6: Commit** — `docs(skills): git-hygiene — sl-<n> branch and SL-<n> PR-title grammars`

**ETA basis:** 1.0 h.

---

### Task 4: `reporter-cycle` and its scripts — the fortnightly work-item status entry

**Files:**
- Modify: `.claude/skills/reporter-cycle/SKILL.md`
- Modify: the scripts under `.claude/skills/reporter-cycle/scripts/` that emit the status post

- [ ] **Step 1: Read `RFC-937` §1.10 (a) and quote its requirement into the task's notes**

```bash
grep -n '### 1.10' docs/rfcs/RFC-00937-*.md
```

Read the clause, including any dated amendment under it — `RFC-779`'s second rule: a citation
can be right while the content it vouches for has moved.

- [ ] **Step 2: Add the fortnightly `WK-` status entry to the cycle**

What is written, where, at what cadence, and by whom. The skill's existing rule that the
**nudge signal is detected by the script and sent by the agent, never by the script** is the
pattern to follow: state which half is the script's and which the reporter's.

- [ ] **Step 3: Update the scripts to match, or state explicitly that they do not change**

A script that does not change is a finding only if §1.10 (a) required it to; say which.

- [ ] **Step 4: Refresh `Verified`**

- [ ] **Step 5: Verify**

```bash
grep -n 'WK-' .claude/skills/reporter-cycle/SKILL.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

If a script changed: run whatever test covers it, and record the count and the command.

- [ ] **Step 6: Commit** — `docs(skills): reporter-cycle — the fortnightly WK- status entry`

**ETA basis:** 2.0 h — 1.0 h if §1.10 (a) turns out to need no script change, and the
uncertainty is why the range is stated rather than a single figure.

---

### Task 5: `repo-architecture` — the annotated `docs/` tree

**Files:**
- Modify: `.claude/skills/repo-architecture/SKILL.md`

- [ ] **Step 1: Read `RFC-937` §1.4's tree and diff it against the skill's**

```bash
grep -n '### 1.4' docs/rfcs/RFC-00937-*.md
grep -n 'docs/' .claude/skills/repo-architecture/SKILL.md | head -40
```

- [ ] **Step 2: Replace the skill's annotated `docs/` tree with §1.4's**

One direction only: §1.4 is the source. Where the skill's tree carried an annotation §1.4 does
not — the *reason* a directory exists, which is what this skill is for — the annotation is
kept against the new directory, not dropped. A directory in the skill's tree that §1.4 does
not list is a **spec-versus-repository disagreement**, and `CLAUDE.md` §0 says stop and
resolve it: raise it to the lead, do not silently delete the row.

- [ ] **Step 3: Check every path in the new tree actually exists**

```bash
ls -d docs/adrs docs/closures docs/findings docs/ledgers docs/plans docs/process docs/rfcs docs/rulings docs/specs docs/workflows docs/_templates
```

A tree that names a directory the repository does not have is the same defect as R13-1's
dangling locator, arriving by a different route.

- [ ] **Step 4: Refresh `Verified`**

- [ ] **Step 5: Verify** — `python3 scripts/audit-docs.py; echo EXIT=$?` (expect 0)

- [ ] **Step 6: Commit** — `docs(skills): repo-architecture — the docs/ tree from RFC-937 §1.4`

**ETA basis:** 1.5 h.

---

### Task 6: `python-test` and `testing-strategy` — the marker form

**Files:**
- Verify only: `.claude/skills/python-test/SKILL.md`
- Modify: `.claude/skills/testing-strategy/SKILL.md`

- [ ] **Step 1: Verify `python-test` rather than re-editing it**

```bash
grep -n 'mark.req' .claude/skills/python-test/SKILL.md
```

Expected at the base tree: `16:@pytest.mark.req("FR-10")` — the integer form, landed in
W37-6's own chain at `4d9fe1d` (#783). If the form is already right, **change nothing in this
file** and record the verification in the ledger. An unnecessary edit to a file another slice
closed is how a closed row is reopened.

- [ ] **Step 2: Add the marker form to `testing-strategy`**

`grep -c 'mark.req' .claude/skills/testing-strategy/SKILL.md` → `0` at the base tree. The
skill teaches pytest generally and states no `req` form. Add it, pointing at `python-test` as
the source rather than restating the rule twice — two copies of a form is how one goes stale
(`RFC-756`).

- [ ] **Step 3: Refresh `Verified` on `testing-strategy` only**

- [ ] **Step 4: Verify**

```bash
grep -n 'mark.req' .claude/skills/testing-strategy/SKILL.md
uv run pytest -q --collect-only -m req 2>&1 | tail -3
```

- [ ] **Step 5: Commit** — `docs(skills): testing-strategy — the req marker form`

**ETA basis:** 0.75 h.

---

### Task 7: `brainstorming` and `planning-with-files` — one sentence each

**Files:**
- Modify: `.claude/skills/brainstorming/SKILL.md`
- Modify: `.claude/skills/planning-with-files/SKILL.md` (subject to DP-7-4)
- Modify: `.claude/skills/README.md` (the deviation record — DP-7-3)

**Both files are vendored.** `planning-with-files` carries its own `LICENSE`
(`.claude/skills/planning-with-files/LICENSE`); `brainstorming` is one of the fourteen
vendored from `obra/superpowers` (`.claude/skills/README.md:99-105`). DP-7-3's default (a)
applies: make the edit **and** record it as a numbered deviation in the README in the same
commit.

- [ ] **Step 1: Write the sentence, once, and use the same wording in both files**

§5.4's row states the content: *"one sentence each: scratch is not a document; the committed
record is `PL-`/`LG-`"*. The sentence must name the scratch locations these two skills actually
use — `.planning/` and `task_plan.md` for `planning-with-files`
(`.claude/skills/planning-with-files/SKILL.md:42`, `:71`) — and say that neither is a governed
document, that neither gets an id, and that the committed record of the same work is a plan
under `docs/plans/` or a ledger under `docs/ledgers/`.

- [ ] **Step 2: Add the deviation entries to `.claude/skills/README.md`**

One entry per file, in the form the README already uses at `:159` and `:178`: what changed,
why, and the authority (`RFC-937` §5.4's row, this plan's id). Do not renumber the existing
deviation entries.

- [ ] **Step 3: Refresh `Verified` on both skills**

- [ ] **Step 4: Verify**

```bash
grep -n 'scratch' .claude/skills/brainstorming/SKILL.md .claude/skills/planning-with-files/SKILL.md
grep -n 'deviation' .claude/skills/README.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

- [ ] **Step 5: Commit** — `docs(skills): brainstorming, planning-with-files — scratch is not a governed document`

**ETA basis:** 1.5 h.

---

### Task 8: `.claude/skills/README.md` — the "creates" column

**Files:**
- Modify: `.claude/skills/README.md`

- [ ] **Step 1: Derive the creating set from `PL-960` §6.2's enumeration, not from the skill names**

`PL-960:688-710` records the derivation and its trap verbatim: *"**The enumeration alone would
have missed two members, which is why both methods were run.** … **Neither method is
sufficient; the set is the union, and a future re-derivation that runs only one of them will
come out short.**" Reuse that union; do not re-derive it by reading skill names.

- [ ] **Step 2: Add the column to the skill tables, populated per row**

The cell names the family the skill mints — `PL-`, `LG-`, `CR- kind: work`, `CR- kind: review`,
`ADR-`, `RS- kind: spike`, requirement rows — or `—` for a skill that creates nothing. A blank
cell and a `—` are different claims; use `—`.

- [ ] **Step 3: Verify the column against the instruments themselves**

For each non-`—` cell, confirm the skill actually names that family:

```bash
grep -l 'doc-id.py next' .claude/skills/*/SKILL.md
```

A row claiming a skill creates a family when the skill never mentions `doc-id.py next` is a
claim with no source — raise it rather than writing it.

- [ ] **Step 4: Refresh `Verified`**

- [ ] **Step 5: Verify** — `python3 scripts/audit-docs.py; echo EXIT=$?` (expect 0; the audit
  checks table-row cell counts, which a new column changes across every row of every table
  edited)

- [ ] **Step 6: Commit** — `docs(skills): README — a creates column per creating skill`

**ETA basis:** 2.0 h. The cell-count check makes a partly-applied column a hard red, so the
column goes into every row of an edited table or none of it.

---

### Task 9: the bespoke-audit rule, in both `close-workstream` and `docs-audit`

**Files:**
- Modify: `.claude/skills/close-workstream/SKILL.md`
- Modify: `.claude/skills/docs-audit/SKILL.md`

- [ ] **Step 0: Raise the plan-versus-tree disagreement before writing anything**

`PL-960:648` records the `close-workstream` half as already authored in W37-6's commit —
*"the `close-workstream` half is in this commit, where the rule is *authored*"* — and
`grep -rn 'bespoke' .claude/skills/close-workstream/SKILL.md` returns nothing at the base
tree. Re-run that grep. If it is still empty, the plan's claim is wrong rather than the tree's
state, and `CLAUDE.md` §0 requires it resolved, not quietly made true: tell the lead, record
the disagreement in the ledger, and only then write the rule. Writing it silently would erase
the record of what W37-6 was believed to have delivered.

- [ ] **Step 1: State the rule, verbatim from `PL-939:750-751`**

> a bespoke audit is a slice whose record is a research document of kind `audit`, owner the
> auditor, every finding its own finding record; never a plan, never a closure.

In `RFC-937`'s own vocabulary that is `RS- kind: audit`, `owner: auditor`, findings as `FD-`
(`PL-960:599`, row 3 of the instrument table). Write the id forms, not only the prose, because
a check reads forms.

- [ ] **Step 2: Put it in both files, with one of them the source**

Write the rule in full in `close-workstream` (the skill that files closures and therefore the
one that gets this wrong) and have `docs-audit` state it in one line **and point at
`close-workstream`**. Two full copies is the `RFC-756` failure mode; the §5.4 row asks for the
rule to *belong in both*, which a pointer satisfies while a duplicate does not.

- [ ] **Step 3: Refresh `Verified` on both**

- [ ] **Step 4: Verify**

```bash
grep -n 'bespoke' .claude/skills/close-workstream/SKILL.md .claude/skills/docs-audit/SKILL.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

- [ ] **Step 5: Commit** — `docs(skills): the bespoke-audit rule — close-workstream and docs-audit`

**ETA basis:** 1.0 h.

---

### Task 10: `writing-plans` — the retired filename grammar (reassigned by `CR-1065`)

**Files:**
- Modify: `.claude/skills/writing-plans/SKILL.md:18`
- Modify: `.claude/skills/README.md` (deviation record — DP-7-3)

- [ ] **Step 1: Confirm the line is still there before editing**

```bash
grep -n 'YYYY-MM-DD' .claude/skills/writing-plans/SKILL.md
```

Expected at the base tree: `18:**Save plans to:** \`docs/plans/YYYY-MM-DD-<feature-name>.md\``.
`CR-1065` `:187-189` records it as *"still present verbatim at `4d9fe1d`"*. If it is gone, another
branch landed it — stop and tell the lead rather than assuming.

- [ ] **Step 2: Replace with the `RFC-937` §1.3 form**

`docs/plans/PL-<nnnnn>-<slug>.md`, `<nnnnn>` the zero-padded result of `python3
scripts/doc-id.py next`. Keep the existing three-line pointer to `docs/plans/README.md` that
`.claude/skills/README.md:172-174` records as a deliberate widening — do not remove a recorded
deviation while landing a new one.

- [ ] **Step 3: Sweep the rest of the file for the same grammar in other forms**

```bash
grep -n 'docs/plans/' .claude/skills/writing-plans/SKILL.md
```

The header template and the Execution Handoff section both quote a plan path back to the user;
a grep for the date form alone misses a `<filename>.md` placeholder that teaches the old shape
by example.

- [ ] **Step 4: Extend the README's existing deviation entry**

`.claude/skills/README.md:159-171` already records the save-path deviation. This is the same
deviation moving to a new grammar, so it is an **amendment to that entry with a date**, not a
new numbered one — and the entry's *"five lines changed across four skills"* count is
re-measured and corrected if this edit changes it.

- [ ] **Step 5: Refresh `Verified`**

- [ ] **Step 6: Verify**

```bash
grep -n 'YYYY-MM-DD' .claude/skills/writing-plans/SKILL.md   # expect: no output
python3 scripts/audit-docs.py; echo EXIT=$?
```

- [ ] **Step 7: Commit** — `docs(skills): writing-plans — the PL-<nnnnn>-<slug> filing grammar`

**ETA basis:** 1.0 h.

---

### Task 11: `subagent-driven-development` — the `LG-` ledger routing (reassigned by `CR-1065`)

**Files:**
- Modify: `.claude/skills/subagent-driven-development/SKILL.md`
- Modify: `.claude/skills/README.md` (deviation record — DP-7-3)
- Possibly modify: `.claude/skills/subagent-driven-development/scripts/task-brief`

- [ ] **Step 1: Read the file's current ledger language**

```bash
grep -n 'ledger' .claude/skills/subagent-driven-development/SKILL.md
```

At the base tree the word appears throughout the worked flow (`:15`, `:22`, `:74`, `:82-83`,
`:86`, `:93`, `:100`, `:102-103`) but never with a path, an id form, or the append rule. That
is the gap: the skill teaches *ledger the ruling* without saying what a ledger is.

- [ ] **Step 2: Add the `LG-` routing**

Three facts, from `RFC-937` §5.4's row: a ledger is `LG-<nnnnn>-<slug>.md` under
`docs/ledgers/`, keyed by `slice:`, `status: active`; **the append is the only permitted
mutation** — which is check 34's own allowance — and `plans:` is appended on replan while PR
numbers are appended as they land. Say that a ledger is never rewritten, only appended, and
name check 34 as what enforces it.

- [ ] **Step 3: Check the `task-brief` script's hard-coded paths**

```bash
grep -n 'docs/' .claude/skills/subagent-driven-development/scripts/task-brief
```

`.claude/skills/README.md:178-200` records two prior changes to this script and one **false
claim that a later control falsified** — read that entry before touching the script, and if a
path moved, prove the fix on the control the entry describes, not on the case that motivated it.

- [ ] **Step 4: Record the deviation in the README**

- [ ] **Step 5: Refresh `Verified`**

- [ ] **Step 6: Verify**

```bash
grep -n 'LG-' .claude/skills/subagent-driven-development/SKILL.md
grep -n 'docs/ledgers' .claude/skills/subagent-driven-development/SKILL.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

- [ ] **Step 7: Commit** — `docs(skills): subagent-driven-development — LG- ledger routing and the append rule`

**ETA basis:** 1.5 h.

---

### Task 12: `watcher-runtime-state` — artifact B's locators (R13-1)

**Files:**
- Modify: `.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py`
- Modify: `.claude/skills/watcher-runtime-state/SKILL.md`
- Create: a test for the new refusal, under the repository's test tree

- [ ] **Step 1: Write the failing test first**

The behaviour: `write_runtime_state.py cycle --phase 2 --phase-source "docs/roadmap.md §7"`
**exits non-zero** when the file part of the locator does not resolve, and writes nothing. The
test asserts both — the exit code and that the state file is unchanged — because a check that
refuses and writes anyway is worse than one that does neither.

- [ ] **Step 2: Run it and confirm it fails for the right reason**

Expected: the script accepts the dangling locator and writes it, so the test fails on the
assertion, not on an import error.

- [ ] **Step 3: Implement the refusal in `_position_block_content`'s callers**

The values arrive as arguments and are stored verbatim at
`scripts/write_runtime_state.py:141-145`. Validate the **file path** part of each
`--*-source` against the repository — the `§n` suffix is prose and is not resolvable, so the
validation stops at the path. Fail closed: refuse rather than warn, for the reason the skill's
own description already gives — *"a dead or unwired writer cannot masquerade as a healthy
zero."*

- [ ] **Step 4: Run the test and confirm it passes; add the positive control**

A resolvable locator must still be accepted. A refusal test with no positive control cannot
tell "refuses dangling locators" from "refuses everything."

- [ ] **Step 5: Fix the taught invocation in `SKILL.md`**

`SKILL.md:84-85` teaches `--phase-source "docs/roadmap.md §7"` and `--work WK-671`. There is no
`## 7` heading in `docs/roadmap.md` (`grep -n '^## ' docs/roadmap.md` → `## 6` at `:174`, then
`## P1a` at `:188`), and `WK-671` is a closed work item. Replace both with a resolvable example
and add one line saying the script now refuses an unresolvable one.

- [ ] **Step 6: The live state file — DP-7-2**

Under DP-7-2's recommendation (b), the live
`~/gi-pricing-plan.local/handover/runtime-state.json` is rewritten by the **watcher**, as an
ops action outside this repository, and the slice ledger records that it was asked for and
when. This step is not a repository change and must not be attempted from the executor's
worktree. Under default (a) the step is dropped and the ledger says so.

- [ ] **Step 7: Verify**

```bash
uv run pytest -q <the new test file>; echo EXIT=$?
uv run ruff check .; echo EXIT=$?
uv run mypy; echo EXIT=$?
```

- [ ] **Step 8: Commit** — `fix(skills): watcher-runtime-state — refuse an unresolvable read_from locator`

**ETA basis:** 2.5 h. It is the slice's first code change with a new test, a positive control
and a skill edit.

---

### Task 13: check 35's owner literal (R13-2) — **blocked on DP-7-1**

**Files:**
- Modify: `scripts/audit-docs.py` (the printed note at `:2936`; the helper
  `_is_stamp_deferred_w37_10`; the docstrings at `:2897-2899` and `:2433-2436`)
- Modify: `tests/test_audit_docs_ids.py` (`:684`, `:1630`) and any other test asserting the
  literal

**Do not start this task until DP-7-1 carries a resolver id.** The code edit is small; which
string to write is the whole question, and it is the lead's.

- [ ] **Step 1: Enumerate every occurrence before changing any**

```bash
grep -rn 'W37-10' scripts/ tests/ docs/ .claude/
```

The literal is in at least the note, the helper name, two docstrings and four test lines
(`tests/test_audit_docs_ids.py:684`, `:1630`; `tests/test_register_lint.py:547`;
`tests/test_doc_id_verify.py:1881`, `:1894`). A partial rename leaves the corpus saying both
things — which is the defect being fixed, reproduced.

- [ ] **Step 2: Apply DP-7-1's ruled option**

Under recommendation (b): the printed note names the owner of record and preserves `RL-1046`
§B's citation with the reassignment stated in the same sentence; the helper is renamed to
`_is_stamp_deferred_f92`, carrying no slice tag; the docstrings follow.

- [ ] **Step 3: Update the tests to assert the new string**

Changing the assertion to match the code proves nothing on its own. Add or keep a test that
fails when the note's owner tag and F92's register cell disagree — the check that catches the
drift class, not the instance.

- [ ] **Step 4: Verify**

```bash
uv run pytest -q tests/test_audit_docs_ids.py tests/test_register_lint.py tests/test_doc_id_verify.py; echo EXIT=$?
python3 scripts/audit-docs.py; echo EXIT=$?
uv run mypy; echo EXIT=$?
```

- [ ] **Step 5: Commit** — `fix(scripts): check 35 — F92's owner of record in the deferred-count note`

**ETA basis:** 1.5 h once DP-7-1 is ruled; unbounded before it.

---

### Task 15: reconcile the salvaged `audit-docs.py` check work against `main`

**Added 2026-09-19 (planner, on the deputy's ruling of the same date).** This task is numbered
15 because task numbers in this plan are append-only — Tasks 3, 8 and 14 are cited by number
elsewhere and a renumber would break those citations — but it is **sequenced before Task 14**,
which is the slice sweep, ledger and gate and must remain last. Order: 13 → 15 → 14. It does
not depend on DP-7-1 and is therefore not blocked while Task 13 is.

**Provenance, stated because this plan asserts at `:318` that it invents no scope of its own:**
this row traces to the deputy's ruling of 2026-09-19, not to `RFC-937` §5.4, `PL-939:740-751`,
`CR-1064` or `CR-1065`. See the annotation on `:318`.

**Why it exists.** The root checkout sits on branch `w37-6-h1-checks-31-32-36` carrying two
commits that exist on no remote and are on no other branch. They implement ruled `audit-docs.py`
check dispositions and were never merged. They were minutes from being destroyed by a checkout.

| Commit | Subject |
|---|---|
| `abc0933` | Implement three ruled `audit-docs.py` check dispositions |
| `ec31a5b` | Rewrite check-31 to read full allocation via `docs/INDEX.md`; drop check-32 hunk |

**Durable evidence, cited by path, both to be re-checked at the start of this task:**
`refs/salvage/2026-09-19/root-checkout-branch` in this repository's own object store, and
`~/gi-pricing-plan.local/handover/unpushed-bundle-2026-09-19/root-branch.bundle`.

**Files:**
- Modify: `scripts/audit-docs.py`
- Modify: this slice's `LG-` ledger (the per-hunk disposition table)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: the disposition table Task 14's ledger sweep cites rather than restates.

- [ ] **Step 1: Confirm the salvaged work is still reachable, from both sources**

```bash
/usr/bin/git show-ref | grep 'refs/salvage/2026-09-19/root-checkout-branch'
/usr/bin/git bundle verify ~/gi-pricing-plan.local/handover/unpushed-bundle-2026-09-19/root-branch.bundle
```
Expected: the ref resolves to `ec31a5b9355a477445bd4677029e571bc3af1c77`, and the bundle reports
*"The bundle records a complete history."* If either fails, stop and report — do not proceed
from one source alone.

- [ ] **Step 2: Derive the net delta, not a replay of the two commits**

```bash
BASE=$(/usr/bin/git merge-base ec31a5b origin/main)
/usr/bin/git diff "$BASE" ec31a5b -- scripts/audit-docs.py
```
`ec31a5b` partially reverts `abc0933` — it drops the check-32 hunk `abc0933` added. **Replaying
the two commits in order would resurrect a hunk its own author withdrew.** The range diff above
is the only correct starting point. Every surviving hunk lands inside
`check_id_filename_directory()`, which exists on both sides.

- [ ] **Step 3: For each hunk, read `main`'s current implementation of the same region**

```bash
/usr/bin/git show origin/main:scripts/audit-docs.py | grep -n 'def check_id_filename_directory'
```
Read from that line to the end of the function on `main`, and read the same function at
`ec31a5b`. **Never re-apply blind.** `main` has moved substantially on this file since these
commits were written — a clean-looking apply is not evidence the change is still wanted, only
that the surrounding lines did not happen to collide. Reconcile against `main` at the head you
branch from, re-deriving it with the command above rather than trusting any figure written here
or elsewhere about how far it has moved.

- [ ] **Step 4: Give every hunk one of two dispositions, in the ledger, with no third option**

For each hunk in the Step 2 diff, write one row: either **land** — the change is still correct
against `main`'s current code, with one sentence saying why — or **superseded**, naming the
commit on `main` that superseded it. Silence is not a disposition. A hunk you cannot decide is
reported to the lead, not skipped.

- [ ] **Step 5: Prove the landed checks on deliberately broken input**

`CLAUDE.md` §13: enforcement is proven on deliberately broken input, and a check that has never
printed a failure has not been tested. For each hunk landed in Step 4, construct an input the
check must reject, run the check, and record that it exits non-zero and names the right file:

```bash
python3 scripts/audit-docs.py; echo EXIT=$?
```
Expected on the clean tree: `EXIT=0`. Then, on a scratch copy carrying the deliberately broken
input, expected: a non-zero exit naming the offending path. Both runs and both outputs go in the
ledger. If nothing was landed in Step 4, record that fact and its consequence — that no new
enforcement was added — rather than omitting this step.

- [ ] **Step 6: Commit** — `fix(scripts): reconcile salvaged audit-docs check work against main`

**ETA basis:** 2 h. Three hunks in one function, each needing `main`'s current code read before a
disposition, plus a broken-input proof for whatever lands and the ledger table.

---


### Task 16: make the reserved block visible to `docs/INDEX.md`, as ruled by `RL-1078`

**Rewritten 2026-09-19 (planner, on `RL-1078`).** The previous text of this task offered the
executor a choice between three options and expected a broken-input proof shaped to a refusal
guard. **`RL-1078` ruled none of the three as drafted** and its acceptance clause is stronger
than DP-7-6 asked for, so the task is rewritten rather than amended. The earlier ETA no longer
applies. Numbered 16, append-only; order 13 → 15 → 16 → 14.

**What was ruled, in one sentence:** the remedy is option (a) **in substance** — the allocator
must see the reservation — but implemented at `scripts/doc-index.py`, **not** as a fifth
`compute_next` scanner. `doc-index.py` emits each reserved allocation as an `INDEX.md` row;
`compute_next` then sees it through `scan_index_ids`, **which it already calls**. `RFC-937`
§1.7's four sources are therefore **correct as written** — the source was never missing, the
index was incomplete.

**The finding that disqualified all three drafted options, and the reason this task must not
drift back to them:** `docs/INDEX.md` is contiguous with zero gaps at `3803331`, so check 31's
contiguity clause is live and load-bearing. Every one of (a)-as-a-scanner, (b) and (c) makes
`next` return past the block's top while the index still stops short, opening a hole check 31
fails on. The decision-maker hit this while writing the ruling: it numbered its own record one
past an unmerged sibling, got `check 31: gap in the full allocation between 1077 and 1079`, and
moved it back. **Writing the fifth scanner is the change that reds the gate.**

**Two corrections to this plan's earlier reasoning, carried here so they are not re-derived:**
`RFC-937` §1.7's *"a collision at rebase is fixed by renumbering the unmerged item"* is **not** a
second authority for "the minted side cannot move" — it governs a race between two *minted
documents*, and one side here is a reservation. `CLAUDE.md` §5 carries that conclusion alone.
And the block is a **deferred allocation, not a stale column**: a maintainer ruling of 2026-09-03
is quoted at `scripts/doc-id.py:9906` and enforced at `:9927`. It is W37-11's input and must not
be released, re-pointed, or blanked.

**Files:**
- Modify: `scripts/doc-index.py` — the reserved-allocation emission
- Modify: `docs/rfcs/RFC-00937-…md` §1.7 — the clarifying amendment of (ii)
- Modify: `tests/` — the two tests the acceptance clause requires
- Regenerate: `docs/INDEX.md`
- Modify: this slice's `LG-` ledger
- **Do not modify `docs/REDIRECTS.csv`.** The ruling forbids it: the block is not W37-7's to move.

**Interfaces:**
- Consumes: `RL-1078`. Nothing from other tasks.
- Produces: an `INDEX.md` carrying reserved allocations, which `compute_next` reads unchanged.

- [ ] **Step 1: Re-derive both predicates at the tree you branch from**

```bash
TREE=$(/usr/bin/git rev-parse HEAD)
/usr/bin/git show "$TREE":docs/REDIRECTS.csv > /tmp/red.csv
/usr/bin/git show "$TREE":docs/INDEX.md      > /tmp/idx.md
awk -F, '$6 ~ /^"?title:/ {print $2}' /tmp/red.csv | grep -oE '[0-9]{4}' | sort -u > /tmp/block.txt
grep -oE '^\| [A-Z]+-[0-9]{4}' /tmp/idx.md | grep -oE '[0-9]{4}' | sort -u > /tmp/idxall.txt
grep -oE '^\| FD-[0-9]{4}'     /tmp/idx.md | grep -oE '[0-9]{4}' | sort -u > /tmp/idxfd.txt
comm -12 /tmp/block.txt /tmp/idxall.txt | wc -l    # (i) number reuse, any family
comm -12 /tmp/block.txt /tmp/idxfd.txt  | wc -l    # (ii) mis-resolution, same family
```
Record both **with `$TREE` beside them** in the ledger. They will exceed any figure written in
this plan or in `RL-1078`, because each document minted since grows (i) by one.

- [ ] **Step 2: Write the two acceptance tests and show them RED first**

`RL-1078`'s acceptance clause, which is the authority and is stronger than DP-7-6 asked for.
**Both tests are pinned by symbol throughout — never a pasted `1136`, never a re-typed
`FD-[0-9]+` literal.** `doc-id.py:9919`'s `_is_fd_canonical` already parses `new_id` through
`_docid.ID_RE` and compares the captured family group; reuse that, because *"a test asserting
that `next` returns 1137 proves only that a number was changed"* and a pasted bound is a
tautology that survives the block moving under it.

1. **Derive-and-compare.** Read the reserved set out of `REDIRECTS.csv` and the allocated set
   out of `docs/INDEX.md`; fail when a reserved number is absent from the index. *Broken input:
   a `REDIRECTS.csv` carrying a reserved mark the generated index omits — the test must red.*
2. **Check 31's contiguity clause is armed against this specific hole.** *Broken input: an index
   whose allocation skips a reserved block, constructed in a `tmp_path` copy — check 31 must
   print `gap in the full allocation`.* Build it on constructed input, never by mutating the real
   tree. This is the failure the earlier draft of this task would have shipped, which is exactly
   why it is the one worth arming.

**Paste both failing outputs into the slice ledger before applying the fix** (`CLAUDE.md` §13).

- [ ] **Step 3: Implement the ruled remedy — spec and code in ONE commit**

`scripts/doc-index.py` emits every `REDIRECTS.csv` reserved allocation — each row whose `new_id`
parses through `_docid.ID_RE` and whose `new_path` is the findings register — as an `INDEX.md`
row carrying its reserved number, its family, the title the redirect row's own `title:` field
holds, a status marking it reserved-not-yet-applied, and `W37-11` as owner. In the same commit,
amend `RFC-937` §1.7 to state that `docs/INDEX.md` carries **reserved allocations as well as
materialised ones**, and that a reservation recorded in `docs/REDIRECTS.csv` is an allocation for
the purposes of §1.1 rule 1. **The four-source sentence is not renumbered to five and not
otherwise altered.**

**Do not write the fifth `compute_next` scanner.** If the index route cannot be built — a
`Record` needs a `Header`, a path and a body, and a register row has none of the first — the
ruled answer is a **synthesised record sourced at `docs/REDIRECTS.csv`**, the same shape
`scan_bold_id_rows` already uses for requirement rows that are not files. It is **not** a silent
fallback to the scanner. **If that route genuinely fails, stop and return to `RL-1078`; do not
choose at the keyboard.**

- [ ] **Step 4: Run both tests green, then the gate**

```bash
python3 scripts/doc-id.py next 2>/dev/null     # stdout is the integer alone; diagnostic is stderr
python3 scripts/doc-id.py check;   echo EXIT=$?
python3 scripts/audit-docs.py;     echo EXIT=$?
```
Expected: `EXIT=0` from both, `next` returning a number outside the reserved block, and check 31
seeing an unbroken allocation across the block. Note when reading a gate result here that
`RL-1078` records a measured case of the **same commit** giving exit 0 then exit 1 with nothing
altered, because part of this corpus is scored against a **pooled ceiling other work consumes**
— so record the ceiling's reading beside the tree, not the tree alone.

- [ ] **Step 5: Re-run Step 1 at the post-fix tree** and record both figures with that tree. The
reserved block is now present in the index, so (i) and (ii) are measured against a corpus where
the reservation is visible; state what each means rather than asserting the numbers improved.

- [ ] **Step 6: Regenerate `docs/INDEX.md` — never hand-edit it** (DP-7-5 option (a))

```bash
python3 scripts/doc-index.py
python3 scripts/doc-index.py --check; echo EXIT=$?
```

- [ ] **Step 7: The two identifier edits, in this task's own commit, only after #797 is on `main`**

Write **`RL-1078`** into DP-7-6's `Resolved by` cell. And renumber this branch's freeze-clause
breach finding from the 1078 mark to the 1079 mark, under `RFC-937` §1.7's *"a collision at
rebase is fixed by renumbering the unmerged item"* — the lead has called which item renumbers.
**Both edits wait for #797 to merge**, because `RL-1078` measured that renumbering ahead of a
rebase reds check 31: the number being stepped over is not on the branch's own base.

- [ ] **Step 8: Commit** — `fix(ids): emit reserved allocations into docs/INDEX.md (RL-1078)`,
spec and code together.

**ETA basis:** 4 h. The emission plus §1.7's amendment is small; the two tests, their red proofs
on constructed input, and the before/after predicate runs are most of it.

---
### Task 14: the slice sweep, the ledger, and the full gate

**Files:**
- Modify: `docs/INDEX.md` (regenerated — DP-7-5)
- Modify: the slice's `LG-` ledger

- [ ] **Step 1: The Acceptance Standard item 4 sweep, restricted to `.claude/skills/`**

`PL-939:753-756` requires it: *"no skill retains a path or an id form the migration retired,
verified by the Acceptance Standard item 4 sweep restricted to `.claude/skills/`."* Run the
map plan's own sweep predicate — read it from `PL-939`'s Acceptance Standard item 4 and copy
it **verbatim**, do not re-derive it. A sweep written from memory measures a different
population, which is `RFC-777`'s §F85 clause exactly.

- [ ] **Step 2: Prove the sweep is not vacuous**

Run it against a deliberately broken input — a scratch copy of one skill with a retired path
reinstated — and confirm it reports. `CLAUDE.md` §13: *"A check that has never printed a
failure has not been tested."* Delete the scratch copy afterwards and say so.

- [ ] **Step 3: Regenerate `docs/INDEX.md`**

```bash
python3 scripts/doc-index.py
python3 scripts/doc-index.py --check; echo EXIT=$?
```

Per DP-7-5, a conflict here is resolved by **regenerating**, never by hand-merging.

- [ ] **Step 4: Write the ledger entry — every §5.4 row named by its commit**

`PL-939:753` requires *"every §5.4 row not landed in W37-6 is named by a commit in this
slice's ledger."* One line per row of the scope table above, each with its commit SHA. A row
whose content turned out already landed (row 6) is named with its **verification**, not with a
commit — and the ledger says which kind of evidence it is.

- [ ] **Step 5: Both gate halves**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
python3 scripts/doc-id.py check; echo EXIT=$?
python3 scripts/doc-index.py --check; echo EXIT=$?
```

Record every exit code. `.claude/skills/dev-commands` carries the traps, including why
`cmd | tail -1 && echo ok` reports the wrong one.

- [ ] **Step 6: Commit and open the PR**

- [ ] **Step 7: CI, by head SHA**

Delegate to the `ci-watcher` agent. Read the per-workflow state via `gh run list` first:
`mergeStateStatus` reports in-flight runs as `UNSTABLE`, and `gh pr checks` fails while exiting
`0`. Record the **head SHA** the run was measured on, and the range `origin/main...<branch>`
for the review — never the tip alone (`CLAUDE.md` §13).

**ETA basis:** 3.0 h, of which roughly 1.0 h is the gate's two halves running and 0.5 h the
broken-input proof.

---

## Exit criteria

**From `PL-939:753-756`, verbatim:**

> **Acceptance:** every §5.4 row not landed in W37-6 is named by a commit in this slice's
> ledger; `python3 scripts/audit-docs.py` exits 0; the gate's two halves are green; no skill
> retains a path or an id form the migration retired, verified by the Acceptance Standard item
> 4 sweep restricted to `.claude/skills/`.

**Added by plan review 13** (`CR-1064:539-541`), each already an item above:

- R13-1 is delivered or explicitly declined with a reason and a named event — this plan takes
  it (Task 12).
- R13-2's tag alignment is delivered by this slice, or this plan names the slice that does —
  this plan takes it (Task 13), blocked on DP-7-1.
- The `dev-commands` / `doc-id-migration-run` text says the venv fix is exclusion by
  construction and **not** a refusal guard (Task 2, Step 3).

**Added by the W37-6 checkpoint-3 close record** (`CR-1065` `:328-335`): the three reassigned
files — `writing-plans`, `subagent-driven-development`, `brainstorming` — each carry their
named §5.4 content edit, evidenced by a commit in this slice's ledger.

**Not an exit criterion for this slice, stated so it is not attempted:** the fuller `RFC-937`
§7 (i) walk across all H / H+M rows. `CR-1065` `:315-318` gives it to W37-11.

---

## Acceptance Standard

Every item is checkable by a fresh reviewer running the command as written, at the slice's
merge tree, with no context from this session.

1. **Every scope row is named by a commit or a verification in the slice ledger.** Open the
   slice's `LG-` file; it has fifteen rows matching the scope table above; each carries either
   a commit SHA reachable from the merge tree or, for row 6, the verification command and its
   output. `/usr/bin/git log --oneline origin/main...<branch>` lists every SHA the ledger names.

   **Corrected 2026-09-19 (planner, on the deputy's ruling of the same date).** The words above —
   *"it has fifteen rows matching the scope table above"* — are superseded as this item's test,
   kept quoted rather than edited. The defect is not that the figure is now wrong; it is that the
   figure is **pasted**, inside the acceptance standard, which is the artifact the close is
   checked against. Task 15 falsifies it, and replacing it with the next integer would fix
   today's instance while rearming the trap for the task after that — the duplicated-constant
   mechanism of `RFC-756`, in the one place it does the most damage. **Do not write a new
   number.** The test is a comparison, and it is run in both directions: **every row of the scope
   table is matched to a ledger row by the file or the subject that row names, and every ledger
   row is matched back to a scope-table row.** A one-way check passes while an extra row sits in
   either list, so both directions are required; neither list's length is counted, and no future
   task can falsify the item by existing. The rest of item 1 is unchanged and still binds: each
   matched ledger row carries either a commit SHA reachable from the merge tree or, for the
   verification-only row, the verification command and its output, with
   `/usr/bin/git log --oneline origin/main...<branch>` listing every SHA the ledger names.
2. **`python3 scripts/audit-docs.py; echo EXIT=$?` prints `EXIT=0`** at the merge tree.
3. **`python3 scripts/doc-id.py check; echo EXIT=$?` prints `EXIT=0`** at the merge tree.
4. **`python3 scripts/doc-index.py --check; echo EXIT=$?` prints `EXIT=0`** at the merge tree,
   and `docs/INDEX.md` is byte-identical to a fresh `python3 scripts/doc-index.py` run.
5. **No skill retains a retired path or id form.** The `PL-939` Acceptance Standard item 4
   sweep, run verbatim with its root restricted to `.claude/skills/`, returns no rows; and the
   same sweep run against a scratch copy carrying one reinstated retired path **does** return a
   row. Both runs and both outputs are in the ledger.

   **Verdict recorded 2026-09-19 (planner, on the lead's ruling of the same date): NOT
   SATISFIED by this slice, deferred with owner W37-11 — because the instrument this item
   names does not exist.** The words above — *"returns no rows"* — **stand unchanged and are
   not lowered.**

   This item requires `PL-939`'s Acceptance Standard item 4 sweep to be run *"verbatim"*. That
   item specifies its sweep **by its exclusion set**: *"under the exclusion set fixed in
   Decision point DP-2 and recorded in `scripts/doc-id.py`'s `LEGACY_SWEEP_EXCLUSIONS` constant
   with a one-line reason per entry."* At `38033319b2654072bb8825529fc6da09f99dc788` that symbol
   appears in plan prose only — `PL-939`, `PL-960` and `PL-1073` — and **in no file under
   `scripts/` or `tests/`**:

   ```bash
   /usr/bin/git grep -ln 'LEGACY_SWEEP_EXCLUSIONS' <tree>                      # docs/plans/ only
   /usr/bin/git grep -ln 'LEGACY_SWEEP_EXCLUSIONS' <tree> -- scripts/ tests/   # no output
   ```

   ***"Run verbatim"* therefore has no implementation to be verbatim against.** The item was not
   run and returned a bad number; it **cannot be run as specified**. Whether an
   equivalently-purposed constant exists under another name is **unestablished, and is inherited
   with this deferral** — W37-11 either finds the instrument, or supersedes `PL-939` item 4's
   specification of it, before this item can be discharged by anyone.

   **The item is not defective in intent, and must not be rewritten to "no new hits."** Its
   intent was always an absolute zero: `PL-939` item 4 reads *"returns nothing over `git
   ls-files`"* as a **Work**-level condition, and its only relief mechanism is a named exclusion
   set *"with a one-line reason per entry"* — a mechanism that would be pointless if
   pre-existing hits were tolerated by default. Decisively, **this item's own positive control
   presupposes a clean baseline**: a control carrying *one* reinstated path can only distinguish
   nothing from something. It was written by someone who believed the restricted root was clean.
   An acceptance item edited to fit its own outcome is the defect this work item exists to
   remove.

   **What is defective is this plan's evidence.** The item asserted an outcome **never measured
   before the plan was frozen** — its author restricted the sweep's root to `.claude/skills/`
   and inferred that the restriction made it clean, and nobody ran it. Had anyone tried, the
   missing symbol would have surfaced then rather than at the close.

   **Separate evidence, belonging to a different instrument — recorded because it is real, and
   labelled because it is not this item's.** A measurement does exist over `.claude/skills/` at
   `origin/main`, taken through the **shipped pooled legacy-form sweep**: `sweep_legacy_forms` /
   `_sweep_legacy_form_hits` with `LEGACY_FORM_PATTERNS` and `LEGACY_FORM_EXCLUDED_PATHS`, split
   by `_legacy_form_disclosure_reason` — **check 36's population**. Over 400 tracked files it
   reads **31 fatal and 118 disclosed**, all pre-existing, with this branch's net contribution
   **zero**, attributed by line text at `origin/main` rather than by line number. **This is not
   `PL-939` item 4's §7 (d) sweep and is not evidence about this item.** It is a different
   instrument over a different population, and it is recorded here as context for W37-11, never
   as a measurement of *"returns no rows"*.

   **The near-miss is recorded because it is this work item's own subject.** The check-36 figures
   above were first offered as evidence about *this item's* sweep. Two instruments, two
   populations, one presented as the other — the `F85` class named in `CLAUDE.md` §13, where two
   counts at the same tree over the same corpus differ only by the predicate that produced them.
   The figures were never wrong; the claim they were attached to was. It was caught for one
   reason only: **the predicate was asked for and the numbers could not be reproduced from it.**
   A count that travels without its predicate is indistinguishable from a count that travels
   with the wrong one, which is why §13 requires the predicate verbatim and runnable.

   **A consequence for whoever discharges this.** The positive control in this item — *"the same
   sweep run against a scratch copy carrying one reinstated retired path **does** return a
   row"* — **is disarmed** wherever the standing population is non-zero. A one-row control can
   only distinguish nothing from something; against a standing population it distinguishes
   neither. It must be re-derived as a **row-identity** comparison: the reinstated path's row is
   present in the after-set and absent from the before-set. A non-empty check passes here for
   the wrong reason.
6. **Both gate halves are green**, each command from `CLAUDE.md` §11 with its own exit code
   recorded in the PR body — Python and docs half, and frontend half.
7. **CI is green at a named head SHA**, recorded in the PR body, with the per-workflow state
   read via `gh run list` rather than from `mergeStateStatus`.
8. **The three review-13 items are each discharged with a locator**: `grep -n 'by construction'
   .claude/skills/dev-commands/SKILL.md` returns a line (R13-3); the new refusal test for
   `write_runtime_state.py` passes and its positive control passes (R13-1); `grep -rn 'W37-10'
   scripts/ tests/` returns only occurrences DP-7-1's ruled option permits (R13-2).
9. **`.claude/skills/README.md` records every vendored-manifest deviation this slice made**,
   one entry or amendment per file among `brainstorming`, `planning-with-files`,
   `writing-plans` and `subagent-driven-development`, each dated and citing this plan's id.
10. **Every skill file this slice modified has a refreshed `Verified` date**, and no skill it
    did not modify has one changed: `/usr/bin/git diff --stat origin/main...<branch> --
    .claude/skills/` names exactly the files the ledger names.

    **Corrected 2026-09-19 (planner, on the deputy's ruling of the same date).** The closing
    words above — *"names exactly the files the ledger names"* — are corrected to **"names
    exactly the skill files the ledger names."** Task 15 puts a non-skill file,
    `scripts/audit-docs.py`, into this slice's ledger. The command in this item is already
    scoped by its pathspec (`-- .claude/skills/`) and so continues to report correctly; it is
    the sentence describing what that output should equal that goes false, because the ledger
    now names a file the pathspec deliberately excludes. The item's substance is unchanged:
    every skill file this slice modified carries a refreshed `Verified` date, no skill it did
    not modify has one changed, and the diff under `.claude/skills/` must correspond exactly to
    the skill files the ledger names — no more, no fewer.
11. **The deputy's merge acknowledgement is recorded** on the PR before the lead merges, and
    the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and
    the lead's merge — no maintainer acceptance line is required for this slice, and none is
    to be waited on.

---

## Risks

**1. DP-6 does not gate this slice — and that is worth stating, because two of its neighbours
are gated.** `PL-939:307` puts DP-6 on **W37-9** and `:772-774` applies it to **W37-8**: a
charter and `CLAUDE.md` are the maintainer's, so those two slices' executors *draft* the diff
and the slice's acceptance requires **a dated maintainer line on the PR before merge**. The map
plan's own words for W37-8: *"This is a gate, not a blocker: drafting proceeds while the line
is pending."* W37-7 touches no charter and does not touch `CLAUDE.md`, so no maintainer line
gates it. **If a task in this slice turns out to need a `CLAUDE.md` or `.claude/roles/` edit,
that edit does not belong to this slice at all** — it is W37-8's or W37-9's, and the finding is
raised to the lead rather than absorbed.

**2. The `.claude/skills/README.md` cell-count trap.** `scripts/audit-docs.py` checks
table-row cell counts. Task 8 adds a column to skill tables; a column applied to some rows of
a table and not others is a hard red, and the red will name a table, not the omission. The task
states the rule: every row of an edited table, or none.

**3. Four concurrent Stage 3 slices, one generated index.** W37-7, W37-8, W37-9 and W37-10 may
run beside each other (`PL-939:379-382`). All four regenerate `docs/INDEX.md`. DP-7-5 carries
the mechanism; the risk if it is not ruled before the first executor is spawned is four
branches each hand-resolving a generated file, which is how a generated artifact stops matching
its source.

**4. `doc-id.py next` under-allocates whenever a record sits on an unmerged branch, and it did
so tonight — by five, not by one.** `python3 scripts/doc-id.py next` at the base tree returned
`1065`. The CP3 branch already holds **1065 through 1069**: the close record itself, plus the
four finding records its `relates:` field names — four `FD-` ids, `1066` through `1069`, whose
files exist under `docs/findings/` at `origin/w37-6-checkpoint-3-close` and are cited here by
integer rather than by id token for the reason given above the base-tree line. **Any
planner who takes `next`'s answer tonight collides**, and a planner who reasons "the close
record took 1065, so 1066 is mine" collides too, because `1066` is one of those four. This plan takes
**1070** for that reason, verified by materialising the branch's close record into a scratch
checkout, regenerating `docs/INDEX.md` and re-running the audit — which is how the four `FD-`
ids were found at all. The reconciliation across the four drafts is still the lead's before any
is pushed. Task 2, Step 2 writes this trap into `dev-commands`, with the mechanism — `next`
reads `origin/main`, and a branch's ids are invisible to it — so the next drafter meets it as
documentation rather than as a collision.

**5. A "closed" row in `CR-1065`'s table does not mean the content edit landed.** The table's
verdict column is computed from the **last-touching commit**, and `CR-1065` `:328` records
`writing-plans` as *"closed (but see §2.2 — its own named H edit did not land)"*. Every row in
this plan's scope table was therefore re-measured by content at the base tree, with the
predicate shown, rather than read off that column. An executor that re-derives scope from the
close record's verdict column will under-count this slice by at least three rows.

**6. Vendored-file edits are a standing rule, not a one-off.** Four of this slice's files are
vendored. `CLAUDE.md` §12 permits the edit only with the deviation recorded in the README **in
the same commit**. A task that lands the edit and defers the README entry has broken the rule
even though both eventually land; Acceptance Standard item 9 is what catches it.

**7. Spec-versus-repository disagreement in Task 5.** `RFC-937` §1.4's tree may name a
directory the repository does not have, or omit one it does. `CLAUDE.md` §0: *"When code and
spec disagree, stop and resolve it."* The resolution is the lead's or the decision-maker's
(`delivery-process.md` §3), never the executor's and never this plan's.

**8. Review 13 is unaccepted and checkpoint 3 is unmerged.** If either changes what this slice
owns, this plan is corrected before it is dated. The correction is triggered by the acceptance
line and the merge, not by anyone deciding to re-read.

---

## ETA basis

Hours of **executor work**, not clock time — the lead converts. No task assumes a particular
start, and the figures exclude review turnaround, CI wall time and any wait on a decision
point.

| Task | Hours | What dominates |
|---|---|---|
| 1 `docs-audit` | 2.0 | The ten-way checks-30-39 walk against the script docstring |
| 2 `dev-commands` | 2.5 | Five command entries, each read from `--help` rather than assumed |
| 3 `git-hygiene` | 1.0 | Two grammars plus the guard interaction |
| 4 `reporter-cycle` | 2.0 | 1.0 if §1.10 (a) needs no script change; the range is the uncertainty |
| 5 `repo-architecture` | 1.5 | Diffing two trees and keeping the annotations |
| 6 `python-test` / `testing-strategy` | 0.75 | One verification, one small addition |
| 7 `brainstorming` / `planning-with-files` | 1.5 | Two files plus two README deviation entries |
| 8 skills `README.md` | 2.0 | The column across every row of every edited table |
| 9 bespoke-audit rule | 1.0 | Two files, one of them a pointer |
| 10 `writing-plans` | 1.0 | One line plus the file-wide sweep and the README amendment |
| 11 `subagent-driven-development` | 1.5 | The routing plus the `task-brief` path check |
| 12 `watcher-runtime-state` | 2.5 | Test first, positive control, code, skill |
| 13 check 35's literal | 1.5 | After DP-7-1; unbounded before it |
| 14 sweep, ledger, gate | 3.0 | ~1.0 gate, ~0.5 broken-input proof, the rest the ledger |
| **Total** | **23.75** | Excludes every wait |

The two code tasks (12 and 13) carry the widest uncertainty: each adds or changes a test, and a
test that does not red on the broken input has to be rewritten rather than accepted.

---

## Self-review

Run per `writing-plans`' checklist, at the base tree.

**1. Spec coverage.** `RFC-937` §5.4 has eighteen rows. Seven are the creating skills DP-1
moved into W37-6. Two — the `citations and example paths` **M** row and the `every SKILL.md
(46)` **M** row — are mechanical and were W37-6's, except where a named file comes back with an
unlanded **H** edit, which is rows 12, 13 and 8 of this plan's scope table. The remaining nine
rows are tasks 1-9 above. Rows 14 and 15 of the scope table come from review 13, not from
§5.4. **No §5.4 row this slice owns is without a task.**

**2. Placeholder scan.** No "TBD", no "handle edge cases", no "similar to Task N". Every step
names a file and a command. Two steps are deliberately conditional rather than vague — Task 4
Step 3 (a script that may not need changing) and Task 12 Step 6 (DP-7-2's ops half) — and each
states what to do under both branches and what to write in the ledger either way.

**3. Type consistency.** The one new identifier this plan proposes,
`_is_stamp_deferred_f92`, appears in DP-7-1 and Task 13 Step 2 in the same form, replacing
`_is_stamp_deferred_w37_10` in both. No other task defines a name a later task consumes.
