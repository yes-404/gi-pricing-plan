---
id: PL-1072
family: plan
kind: leaf
title: W37-9 — Root governance, CLAUDE.md and the public face: leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-18
owner: planner
tree: a8b3c39a0cdd0a537b83b58d04aa0ea3c340aa15
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
---

# W37-9 — Root governance: `CLAUDE.md` and the public face

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax
> for tracking.

**Goal:** Bring the repository's root governance files — `CLAUDE.md` and the six public-face
files beside it — into agreement with the document-id standard the W37-6 migration already
applied to `docs/`, so that the project contract names the directories, families and
conventions that now exist rather than the ones that did.

**Architecture:** Nine files, one per [RFC-937](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md)
§5.1 row. Five carry hand edits the migration script could not know (`CLAUDE.md`,
`README.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.gitignore`, plus the
optional issue templates); three are `M` rows the script already wrote and this slice only
*verifies* (`SECURITY.md`, `.importlinter`, the `pyproject.toml` comment citations). The
slice is document work end to end: it adds no code, no test, no dependency, and no
requirement id.

**Tech Stack:** No new dependency. The only executables it runs are the repository's own
gate commands — `scripts/audit-docs.py`, `scripts/doc-id.py`, `scripts/doc-index.py` and the
two halves of `CLAUDE.md` §11's gate.

**Spec:** [`../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md)
§5.1 (the row table this slice discharges), §1.4 (the layout the tree must match), §1.2 (the
family table), §1.6 (the owner table), §1.9 (the GitHub alignment the PR template and
`CONTRIBUTING.md` must state). The parent map plan is
[`PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`](PL-00939-wk-697-one-id-per-governed-thing-map-plan.md),
slice section `:785-814`, sequencing row `:381`.

## Goal

Nine files — `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, the pull-request
template, the two issue templates, `.gitignore`'s comment block, `.importlinter`, and the
`pyproject.toml` comment citations — say what the repository's layout, families and naming
conventions are, in the form RFC-937 §5.1 specifies, at the end of this slice. Six of the
nine need a hand edit the migration script could not make; three are already correct and this
slice's job on them is to *prove* it rather than assume it. The hardest single obligation is
that `CLAUDE.md`'s permanence rule yields to RFC-937 D2 at **both** of the sites that state
it, in one commit, each carrying a dated line naming what yielded to what — because a tree in
which one site is edited and the other is not is a project contract that contradicts itself.
"Done" is the Acceptance Standard below, every item of it a command or a named artifact.

## Status — this plan is a DRAFT and is not filed

**It carries no filed date and it is not frozen.** `status: draft` per
[`../process/document-ids.md`](../process/document-ids.md) §1.7: freeze is mechanical, and a
plan with an open blocking row in its Decision points table stays `draft`. **DP-1 and DP-3
below are blocking and unresolved — that is the only thing still holding this plan in
`draft`.**

It was drafted under the deputy's ruling of 2026-09-18 00:41:53 BST
(`~/gi-pricing-plan.local/channel/to-lead.md`, four conditions on Stage 3 leaf-plan
drafting), which permitted **drafting only**. **This correction pass, made under the
deputy's later ruling of 2026-09-18 09:19, discharges the two record-landing conditions that
ruling named — one by reconciling now rather than waiting, one because the event landed:**

1. **The maintainer's dated acceptance line on plan review 13 still does not exist**, verified
   fresh at this pass's own base tree:
   ([`../closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md`](../closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md):632,
   `**Maintainer acceptance:** _pending_`, at `d63f765085fe6eb1c594177c5779ecfc3caf7ae8`). Per the
   09:19 ruling, review 13 is *"a FILED PROPOSAL — reconcile against it now, do not wait for its
   acceptance line"*. The section below does exactly that — reconciles against it **as a
   proposal** — and this plan no longer waits on the acceptance line landing.
2. **The W37-6 checkpoint-3 close has landed on `main`, as `CR-1065`.**
   `git log --oneline -1 -- docs/closures/CR-01065-w37-6-checkpoint-3-close.md` → `d63f765
   docs(closures): W37-6 checkpoint 3 — slice close record, register, roadmap row, ledger`,
   byte-identical to the branch revision (`8774db4`, PR #787) this plan was drafted against
   (`git diff origin/w37-6-checkpoint-3-close:docs/closures/CR-01065-w37-6-checkpoint-3-close.md
   origin/main:docs/closures/CR-01065-w37-6-checkpoint-3-close.md` → empty), so every line
   number the Reconciled section cites against it still resolves. W37-9 depends on W37-6 (map
   plan `:381`); that dependency is now satisfied.

**What still blocks:** a resolver on DP-1 and DP-3, the lead's/decision-maker's to give — not
discharged by either of the deputy's rulings above, and not this correction pass's to supply.
This plan is dated (`status:` moves to `active`, `created:` unchanged) once both carry a
resolver id; until then it correctly stays `draft` under §1.7's mechanical rule — a `PL-`
`active` with an open blocking decision point fails `audit-docs.py` check 33.

---

## Reconciled against plan review 13

**The two records this section answers to, by path.** The second was not on `main` at the
tree this plan was written against, so it was named there in a fence and cited below by
section and line rather than by id — an id that does not resolve in `docs/INDEX.md` is not a
citation a reader can follow, and `audit-docs.py` check 32 says so. **Both are now on `main`,
`CR-1065` since this correction pass's rebase**, and every line-and-section citation below
still resolves because the merged file is byte-identical to the branch revision cited
(`git diff origin/w37-6-checkpoint-3-close:docs/closures/CR-01065-w37-6-checkpoint-3-close.md
origin/main:docs/closures/CR-01065-w37-6-checkpoint-3-close.md` → empty):

```text
docs/closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md
    on main @ a8b3c39, still on main @ d63f765 — cited below as "review 13"
docs/closures/CR-01065-w37-6-checkpoint-3-close.md
    at drafting: on origin/w37-6-checkpoint-3-close @ 8774db4, PR #787, NOT on main @ a8b3c39
    now: on main @ d63f765 (git log --oneline -1 -- docs/closures/CR-01065-w37-6-checkpoint-3-close.md)
    — cited below as "the close record" / CR-1065
```

Plan review 13 closes its own list: *"Here is the closed list that section must answer, one
line each. Nothing outside this list is owed to review 13"*
([`CR-01064`](../closures/CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md):`538-549`).
Its eleven rows are answered below — the two that address this slice substantively, the
nine addressed elsewhere by naming their owner, so a reader can see none was skipped rather
than inferring it.

| Review-13 row (source line) | Addressed to | This plan's answer |
|---|---|---|
| **W37-9 (root governance)** — *"**Nothing.** §4e found no spec drift and this run minted no requirement id"*, and the required statement is *"No item from review 13 bears on this slice"* — stated, not omitted (`CR-1064:543`) | **W37-9** | **Stated: no item from review 13 bears on this slice.** Review 13's question 4 found *"no spec drift, no requirement id touched"* (`CR-1064:580`) and its question 5 found the W37-7…11 cut holds with no slice moved (`CR-1064:581`). This plan therefore takes **no scope, no requirement and no constraint** from review 13. |
| **All four (W37-7…W37-10)** — §2b: *"four run disclosures are filed in no register row, and the idempotence label collides with the real F28"*; the section must say *"that each draft's scope was derived **after** the filing, or states that it was derived before and names the risk"* (`CR-1064:549`) | **W37-9, among four** | **Derived BEFORE the filing — the risk is named.** At `a8b3c39` no register row exists for the four run disclosures: the register grep in Task 9 Step 1 returns nothing at this tree, and the four finding files exist only on `origin/w37-6-checkpoint-3-close` (`8774db4`). **Risk:** if any of the four, once filed, names a root-governance file, this scope is short by that item. **Assessed and low:** all four are instrument- or record-facing (idempotence of `doc-id.py migrate`; check 35's two sub-clauses; the standing CI verify's pinned base; H1 residue by file), and review 13 routes all four to W37-11 (`CR-1064:545-547`), none to W37-9. **Mitigation as a task step:** Task 9 re-runs the grep against the merged register and reports any row naming a §5.1 file; a hit is a finding against this plan, not a silent scope change. |
| §2c — `write_runtime_state.py`'s stale `position` block and dangling `read_from` locators (`CR-1064:539`) | W37-7 | Not this slice. No action here; `write_runtime_state.py` is an instrument. |
| §4c — check-35's `W37-10` owner literal for F92 must align to the owner of record (`CR-1064:540`) | W37-7 | Not this slice. The literal is inside `scripts/audit-docs.py`; this slice touches no code. |
| §5 row 1 — the venv fix is exclusion-by-construction, not a refusal guard (`CR-1064:541`) | W37-7 | Not this slice. |
| F97's disposition — remedy touches `.claude/roles/lead.md` (`CR-1064:542`) | W37-8 | Not this slice. Charters are W37-8's (map plan `:760`). |
| §4d — F87/F90 register cells stale; register-currency line in the checklists (`CR-1064:544`) | W37-10 | Not this slice. |
| §5 row 3 — the pinned-base read, raised in `docs/open-questions.md` with two options (`CR-1064:545`) | W37-11 | Not this slice. |
| §5 row 4 — the idempotence gap `PL-960:909`, `41 hit(s) … ceiling of 15 for 'd10'` (`CR-1064:546`) | W37-11 | Not this slice. |
| §5 row 5 — row (g) as a first-class acceptance item, `classified-by-none = 251` at `4d9fe1d` (`CR-1064:547`) | W37-11 | Not this slice. **Note: `251` is review 13's own pre-#757 figure. `#757` merged as `29e7a9c` and the current measured value is `207` (that commit's squash body carries the per-class table); W37-11 works from `207`, not `251`.** |
| §5's closing carry rule — `(j)`/`(k)`, synthesis, or a named acceptance item with its own exit measurement (`CR-1064:548`) | W37-11 | Not this slice. Noted as the rule W37-11 was cut against; it constrains nothing here. |

### And against the W37-6 checkpoint-3 close record

The **W37-6 checkpoint-3 close record** is the second record this
draft reconciles against, per the deputy's condition. Read while drafting at
`origin/w37-6-checkpoint-3-close` = `8774db4` (not on `main` at `a8b3c39`); **now on `main` as
`CR-1065`** (`d63f765`), byte-identical, so the line numbers below are unchanged. Its §2.4
walks 56 of RFC-937 §5's H/H+M rows and **reassigns two files to W37-9 by name**:

| Item, with its source line | What this plan does with it |
|---|---|
| `CONTRIBUTING.md` — *"`01ba0bd` (#495, pre-migration) \| **NOT CLOSED — still pre-migration content**"* (close record `:274`), reassigned: *"`CONTRIBUTING.md` \| **W37-9** \| PL-939 `:785`, root governance / public face"* (close record `:325`) | **Accepted as scope.** Task 5. It was already a §5.1 `H` row, so this is confirmation with evidence rather than an addition — and the evidence is the useful part: the file is still at its pre-migration commit. Independently re-verified at `a8b3c39`: `/usr/bin/git log --oneline -1 -- CONTRIBUTING.md` → `01ba0bd`. |
| `.github/PULL_REQUEST_TEMPLATE.md` — *"`01ba0bd` (#495, pre-migration) \| **NOT CLOSED — still pre-migration content**"* (close record `:275`), reassigned to **W37-9** (close record `:326`) | **Accepted as scope.** Task 6. Also already a §5.1 `H` row. Re-verified at `a8b3c39`: last-touching commit `01ba0bd`, and the file still tells an author to cite *"an NT-/FR- id"* (`:14`) — `NT-` is a family the migration dissolved, so this is a missed citation rewrite as well as a missed hand edit. |
| `.claude/agents/ci-watcher.md` → **W37-8** (close record `:327`); `writing-plans` and `subagent-driven-development` SKILL.md → **W37-7** (`:328-329`); `brainstorming` SKILL.md → **W37-7** (`:333-335`); `docs/research/README.md` → **W37-10** (`:330`) | Not this slice. Listed so the routing is visibly complete and this plan is not read as having dropped them. |
| §2.4's own limit: *"This is a sample (56 of the roughly 90 H / H+M rows RFC-937 §5 lists …); it is not (i)'s exhaustive discharge — that fuller walk is W37-11's"* (close record `:341-343`) | **Consequence for this slice, disclosed:** the sample did **not** include `.github/ISSUE_TEMPLATE/*.yml`. This plan measured it independently at `a8b3c39` — `/usr/bin/git log --oneline -1 -- .github/ISSUE_TEMPLATE/bug.yml` and `… question.yml` both → `01ba0bd`, pre-migration, the same commit as the two files §2.4 did flag. It is a §5.1 `H (optional)` row and is DP-2 below. |

---

## Acceptance Standard

Every item is a command a fresh reviewer can run, or a named artifact they can read at a
named tree. None is satisfied by inspection of this plan.

1. **The map plan's own acceptance clause, verbatim** (`PL-939:810-813`): *"a dated
   maintainer line for the `CLAUDE.md` edit; both permanence sites edited and each carrying
   its dated line; `python3 scripts/audit-docs.py` exits 0; `uv run lint-imports` exits 0
   after the contract rename; the gate's two halves are green."*
2. **The dated maintainer line exists**, quoted in the PR body with its date, per DP-6 option
   (a) (`PL-939:307`). Absent it, the PR is not merged — see Risks.
3. **Both permanence sites carry a dated line naming RFC-937**, and G2's *"editing one and
   not the other"* failure cannot have happened:
   `grep -n 'permanent' CLAUDE.md` returns each site with a dated RFC-937 clause adjacent,
   and `grep -c 'RFC-937' CLAUDE.md` is at least 2.
4. **`CLAUDE.md` names every directory the layout now has**, none of which it names at
   `a8b3c39`: `grep -c 'docs/closures/' CLAUDE.md`, `grep -c 'docs/findings/' CLAUDE.md`,
   `grep -c 'docs/rulings/' CLAUDE.md`, `grep -c 'document-ids.md' CLAUDE.md` are each
   `>= 1`. **Measured baseline at `a8b3c39`: all four are `0`** —
   `grep -n "docs/closures\|docs/findings\|docs/rulings\|docs/ledgers\|document-ids\|INDEX.md" CLAUDE.md`
   returns exactly one line, `:270`, which is a prose mention of *"register finding"* and
   none of the paths.
5. **No dead path or mangled id survives in the seven hand-edited files.** The sweep,
   and the four hits it returns at `a8b3c39` — the literals are inside the fence on
   purpose: `audit-docs.py` check 36 fires on a legacy path form written in prose, so a
   plan whose job is to delete those forms cannot spell them outside a code block.

```bash
grep -nE 'docs/(notes|audit)/|NT-[0-9]' CLAUDE.md README.md CONTRIBUTING.md \
  SECURITY.md .github/PULL_REQUEST_TEMPLATE.md \
  .github/ISSUE_TEMPLATE/bug.yml .github/ISSUE_TEMPLATE/question.yml .gitignore
# a8b3c39 baseline, four hits:
#   CONTRIBUTING.md:28                  legacy audit directory
#   README.md:35                        legacy audit directory
#   .github/PULL_REQUEST_TEMPLATE.md:14 NT- family token
#   .gitignore:94                       legacy notes directory (which does not exist:
#                                       `ls -d docs/notes` fails at this tree)
# After this slice: no output, exit 1 from grep.
```
6. **The `WF-` range in `CLAUDE.md` §4 resolves.** At `a8b3c39` §4 reads
   `workflows/WF-698…05`, which is a citation-rewrite artifact: the five files are
   the five files `ls docs/workflows/` lists, whose numbers run `698` to `702`, so the
   range's second endpoint resolves to nothing.
   After: every `WF-` token in `CLAUDE.md` resolves to a file under `docs/workflows/`.
7. `python3 scripts/audit-docs.py; echo EXIT=$?` → `EXIT=0`.
8. `python3 scripts/doc-id.py check; echo EXIT=$?` → `EXIT=0`.
9. `python3 scripts/doc-index.py --check; echo EXIT=$?` → `EXIT=0`, and
   `git status --porcelain docs/INDEX.md` is empty after a fresh `python3 scripts/doc-index.py`.
10. `uv run lint-imports; echo EXIT=$?` → `EXIT=0`.
11. **Both gate halves green at the head SHA**, run locally before push and confirmed in CI
    by head SHA, per `CLAUDE.md` §11: the Python/docs half
    (`uv run ruff check .`, `uv run mypy`, `uv run lint-imports`, `uv run pytest -q`,
    `python3 scripts/audit-docs.py`, `uv run python scripts/req-coverage.py`,
    `uv run python scripts/generate-contracts.py --check`) and the frontend half
    (`pnpm --dir frontend install --frozen-lockfile`, `generate:api`, `lint`, `type-check`,
    `test`, `build`).
12. **No requirement id is minted, renumbered or superseded by this slice**, and no file
    under `docs/specs/` is touched: `git diff --name-only origin/main...HEAD -- docs/specs/`
    is empty. (Review 13 question 4: *"no spec drift, no requirement id touched"*.)
13. **Every §5.1 row is dispositioned** in the PR body's table — file, `H`/`M`, the commit
    that names it, and for an `M` row the verification that it is already closed. Nine rows,
    none silent (`CLAUDE.md` §13: silence is not a verdict).

## Global Constraints

Copied verbatim from the map plan's Global Constraints block
([`PL-939`](PL-00939-wk-697-one-id-per-governed-thing-map-plan.md)`:112-160`); every
task's requirements implicitly include them. The three that bite hardest here:

- **G1 — RFC-937 outranks current practice.** Where the standard collides with something
  already written down, the collision is work in RFC-937's favour. Two limits the ruling does
  not lift: **no rule is changed silently** — every collision lands as a visible, dated edit
  naming which rule yielded to what — and the ruling does not authorise starting.
- **G2 — the permanence rule yields, at two sites.** *"`CLAUDE.md` states 'Requirement IDs
  and section numbers are permanent … Never renumber' at **line 27** (the §0 bullet) and
  again at **line 107** (§5's own sentence). D2 renumbers every requirement id. Both sites
  are edited in W37-9, each with a dated line naming RFC-937 as what it yielded to. An
  executor who edits one and not the other leaves the contract self-contradicting."*
  **Line numbers have moved since the map plan was filed at `89dd2b1`.** At `a8b3c39` the two
  sites are **`CLAUDE.md:27`** (unchanged) and **`CLAUDE.md:110`** (not `:107`), measured by
  `grep -n 'permanent' CLAUDE.md`. See DP-1 for the third hit that grep also returns.
- **G5 — money and product identifiers are never touched.** No `VR-*`, artifact id or job
  kind is rewritten by this slice. Nothing in §5.1 contains one; the constraint is recorded
  so the executor does not invent an exception.

## Scope — the RFC-937 §5.1 rows this slice owns

Nine rows, each measured at `a8b3c39` before this plan was written. "Last-touching commit"
is `/usr/bin/git log --oneline -1 -- <path>`, the same method the close record's §2.4 used.

| # | File | §5.1 change (abridged) | Kind | Last-touching commit at `a8b3c39` | State | Task |
|---|---|---|---|---|---|---|
| 1 | `CLAUDE.md` | §2 layout → §1.4's tree; §4 module map rewritten; §5 gains the id-scope sentence; §9 roadmap pointer; §12 owner table; §13–§15 pointers to `closures/`, `findings/`, `rulings/`; citations rewrite | H + M | `71f5a22` | **M landed, H owed.** Citations rewritten (`RFC-756`, `ADR-704`, `FR-451` all present); no new directory named, `WF-698…05` mangled | 1, 2, 3 |
| 2 | `README.md` | the tour: new paths; one paragraph "how things are named" → `document-ids.md`; branch and PR-title convention | H | `71f5a22` | **Front matter added; body owed.** `:35` still routes readers to the legacy audit directory for closure records | 4 |
| 3 | `CONTRIBUTING.md` | branch `sl-<n>-<slug>`, PR title `SL-<n>: …`, "a new document has an id from `doc-id.py next`", where findings and proposals go | H | `01ba0bd` (#495, pre-migration) | **Not started.** close record `:274` | 5 |
| 4 | `SECURITY.md` | path → `docs/process/security-posture.md` | M | `71f5a22` | **Closed — verify only.** `:40` already links `docs/process/security-posture.md` | 8 |
| 5 | `.github/PULL_REQUEST_TEMPLATE.md` | required `SL-<n>` line and `PL-<n>`; "no slice yet? the lead mints one at triage under `WK- maintenance`" | H | `01ba0bd` (#495, pre-migration) | **Not started.** close record `:275`; `:14` still says `NT-/FR- id` | 6 |
| 6 | `.github/ISSUE_TEMPLATE/*.yml` | optional "related id" field; issue types mirrored | H (optional) | `01ba0bd` both files | **Not started; optional.** Not in the close record's §2.4 56-row sample — measured here | 7, DP-2 |
| 7 | `.gitignore` | comment block reworded to the new families | H | `71f5a22` | **Not started.** `:94` names an `NT-` id in the legacy notes directory, which does not exist at this tree | 7 |
| 8 | `.importlinter` | contract names | M | `71f5a22` | **Closed — verify only.** `grep -n '^name' .importlinter` → `ADR-703`, `ADR-704`, `DEP-3`, each resolving to a real file or clause. **§5.1's written target is stale** — it names two one-character ADR numbers and a placeholder `DEP-` number, while the migration allocated `ADR-703` and `ADR-704`, so the shipped names are correct in the *form* the migration actually produced. Disclosed, not silently accepted — DP-4 | 8 |
| 9 | `pyproject.toml` (root), `packages/*/pyproject.toml` | requirement-id citations in comments | M | — | **Verify only.** | 8 |

**What is NOT in this slice, so an executor does not widen it:** `.claude/roles/`,
`.claude/agents/` and `.claude/skills/` (W37-8 and W37-7); `docs/README.md` and the
checklists (W37-10); anything under `docs/specs/`, `docs/roadmap.md` or
`docs/findings/register.md` (other slices' or other roles'). A §5.1 hand edit that turns out
to need one of those is a **finding against this plan**, raised to the lead, not absorbed.

## Roles

| Role | Who | Charter | What they do here |
|---|---|---|---|
| Executor | one executor, spawned from [`../../.claude/roles/executor.md`](../../.claude/roles/executor.md) | *"one slice at a time from the frozen plan, in its own worktree … the full local gate before push (both halves) … opens PRs"* (`executor.md:30-34`). **Principal: the lead**, not the maintainer and not the deputy (`executor.md:15`) | Tasks 1–9, in one worktree, one branch, one PR |
| Executor skill | `spec-change` | Named by the map plan's sequencing row (`PL-939:381`) and its slice section (`:787`). *"the governed-document procedure"* | Read before Task 1; its "After editing" step (`python3 scripts/audit-docs.py` must print "All checks passed.") is Task 9's spine |
| Auditor | one auditor, spawned from [`../../.claude/roles/auditor.md`](../../.claude/roles/auditor.md) | *"Never: merges, implements, declares anything closed. Proposes verdicts; never issues"* (`auditor.md:47`) | Verifies the nine-row disposition table and the Acceptance Standard before the lead merges |
| Lead | the W37-9 lead | `CLAUDE.md` §12 | Rules DP-1 and DP-3; adopts, amends or rejects the auditor's verdicts; merges |
| Maintainer | — | `CLAUDE.md` §12: *"An amendment to what this file requires"* is the maintainer's | Writes the dated line DP-6 (a) requires before the `CLAUDE.md` edit merges |

## Decision points

Kind, blocking status and resolver per RFC-937 §1.7. A blocking row must carry a resolver id
before the slice it blocks may start; a non-blocking row names the step that resolves it and
the default applied until then.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | **The permanence rule has a third site G2 does not name.** `grep -n 'permanent' CLAUDE.md` at `a8b3c39` returns `:27`, `:110`, `:176` and `:226`. `:176` is unrelated (context discipline, *"re-read every turn"*). `:226` is in §12 and reads *"A spec change still follows `.claude/skills/spec-change`; a requirement id is still permanent (§5)."* G2 names two sites and this is a third mention. Does it need a dated yield line too? | (a) edit all three, each with its own dated RFC-937 line; (b) edit only G2's two and leave `:226` exactly as it stands; (c) edit G2's two, and at `:226` change nothing but confirm in the PR body that it was read and classified | **(c).** `:226` **cites** §5's rule rather than restating it — *"a requirement id is still permanent (§5)"* carries the section reference in the sentence. A citation inherits whatever §5 says after the edit, so it cannot go stale the way a restatement does; adding a second dated line there would create the duplicate-statement failure [RFC-756](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md) exists to prevent. (a) manufactures that duplicate; (b) is (c) without the record that the distinction was drawn. **The planner does not rule this** — `planner.md`: *"Never: … rules decision points"* | decision point | **yes** | _the lead_ |
| DP-2 | **`.github/ISSUE_TEMPLATE/*.yml` is §5.1's only `H (optional)` row.** Both files are still at `01ba0bd`, pre-migration, and neither was in the close record's §2.4 sample. Does W37-9 take it? | (a) take the whole row — a "related id" field plus the `Feature`/`Task`/`Bug` issue-type mirror; (b) take the "related id" field only; (c) decline the row with a dated reason and a named event | **(b).** The "related id" field costs one `input` block per template and makes an issue routable to a governed record, which is §1.9's whole point. The issue-**type** mirror depends on GitHub issue types being configured on the repository, which is a repository-settings change no plan in this Work owns and which `gh` cannot read here (memory: the token reads run data, not admin settings) — so mirroring is not verifiable from a gate and would be an unevidenced claim | scope | no | **Default until ruled: (b)**, applied at Task 7; the lead may substitute (a) or (c) at the PR review |
| DP-3 | **The `SL-` family has no members, and this slice would publish a convention that cites it.** §1.9 and the map plan `:806-810` require the PR template to gain a required slice line, `SL-<n>: …`, and `CONTRIBUTING.md` to name the branch form `sl-<n>-<slug>`. At `a8b3c39` **zero `SL-` ids exist anywhere**: `grep -c 'SL-' docs/roadmap.md` → `0` and `grep -c 'SL-' docs/INDEX.md` → `0`. WK-697's own slices are keyed `W37-1` … `W37-11`, not `SL-`. Writing the convention as §1.9 states it makes a public promise about an empty family — including to this slice's own PR, which cannot carry a compliant title | (a) write the convention exactly as §1.9 states it and accept that no PR can satisfy it yet; (b) write it with a dated "not yet in force — no `SL-` row has been minted; `WK-`/`W37-n` is what a PR names today" clause, removed when the first `SL-` lands; (c) defer both the template line and the `CONTRIBUTING.md` branch form to the slice that mints the first `SL-` row | **(b).** G1 says the collision is work in RFC-937's favour, so (c) under-delivers a scoped `H` row. But G1's own limit is that nothing changes silently, and (a) would publish a rule the repository violates on the very PR that introduces it — the "enforced by construction is not enforced" shape. (b) delivers the text, states the gap with a date, and gives a removable marker. **The planner does not rule this** | scope | **yes** | _the lead_ |
| DP-4 | **§5.1's `.importlinter` target is stale.** The row's written target is two one-character `ADR-` numbers and a placeholder `DEP-` number; the migration actually allocated `ADR-703` and `ADR-704`, and `.importlinter` at `a8b3c39` reads `ADR-703`, `ADR-704`, `DEP-3` (`grep -n '^name' .importlinter`) | (a) treat the row as closed by `71f5a22` and verify only; (b) rename the contracts to §5.1's literal one-character numbers | **(a).** §5.1's one-character target was written before the sequence was allocated and names numbers that resolve to no ADR file; `ADR-703` and `ADR-704` resolve to real files under `docs/adrs/`. This is the spec being stale, not the tree — raised as a finding rather than obeyed (`CLAUDE.md` §0: *"When code and spec disagree, stop and resolve it"*) | fact | no | **Default: (a)**, applied at Task 8, with the discrepancy raised to the lead as a one-line finding in the PR body |
| DP-5 | **The legacy audit directory still has two tracked files** — a `findings/README.md` and a `w37-11-record.md` under it, listed by the `ls-files` command in Task 4 Step 1 — while RFC-937 §1.4 states that that directory dissolves into `findings/`, `closures/`, `research/` and `process/`. `README.md:35` and `CONTRIBUTING.md:28` both send a reader there | (a) repoint both public-face files to `docs/closures/` and `docs/findings/register.md` now; (b) leave the public text pointing at the legacy audit directory until it is empty | **(a).** The public face describes the layout the standard defines; the two residue files are W37-11's and W37-7's business, not a reason for `README.md` to misdirect a first-time reader. The link still resolves either way, so nothing breaks | design unknown | no | **Default: (a)**, applied at Tasks 4 and 5 |

## Tasks

Nine tasks. Each ends with an independently checkable deliverable and its own commit; each
names the command that verifies it. Conventional Commits throughout; branch
`w37-9-root-governance` off `main`, per `CLAUDE.md` §10.

**Before Task 1 — read, in this order:** `.claude/skills/spec-change/SKILL.md` in full;
RFC-937 §1.2, §1.4, §1.6, §1.9 and §5.1; the map plan's slice section `:785-814`; this
plan's Global Constraints and Decision points. Then confirm DP-1 and DP-3 carry a resolver
— **if either is still open, stop and ask the lead. They are blocking.**

---

### Task 1: `CLAUDE.md` §2 and §4 — the layout tree and the module map

**Files:** Modify `CLAUDE.md:43-70` (§2), `CLAUDE.md:92-101` (§4).

**Interfaces:**
- Consumes: RFC-937 §1.4's tree block (`docs/process/document-ids.md:85-105`), copied as the
  shape §2 points at. §2 is a *pointer* section — *"the annotated tree and the reasoning are
  `.claude/skills/repo-architecture`"* — so it gains the directory names and the one-way
  rule, not a second full tree, per RFC-756.
- Produces: the directory vocabulary (`docs/closures/`, `docs/findings/`, `docs/rulings/`,
  `docs/ledgers/`, `docs/process/document-ids.md`, `docs/INDEX.md`) that Tasks 2 and 3 cite.

- [ ] **Step 1: Record the baseline before editing.** Run and paste the output into the
      commit body:

```bash
grep -n "docs/closures\|docs/findings\|docs/rulings\|docs/ledgers\|document-ids\|INDEX.md" CLAUDE.md
ls docs/workflows/
grep -n "WF-" CLAUDE.md
```

Expected at `a8b3c39`: the first prints exactly one line (`270:`, a prose *"register
finding"*, no path); the second prints `README.md` and `WF-698` … `WF-702`; the third
prints `97:` carrying the token `WF-698…05`.

- [ ] **Step 2: Rewrite §4's module-map paragraph.** The sentence at `:97` currently reads
      `workflows/WF-698…05 are the **cross-module journeys**`. `WF-698…05` is a
      citation-rewrite artifact: the pre-migration form was a range over the old lower-case
      workflow filenames, and rewriting only
      its first member left a range whose second endpoint (`05`) names nothing. Replace the
      range with the five ids individually — `WF-698`, `WF-699`, `WF-700`, `WF-701`,
      `WF-702` — which is also `planner.md`'s standing rule against a bare numeric range
      (*"never a bare numeric range (`34-42`), which silently drops an append-only id landed
      inside it"*). Keep the five journey names and the closing contrast sentence exactly as
      they are; this is a citation repair, not a rewrite of what §4 says. Add the pointer
      `docs/INDEX.md` as the generated index of every document, and
      `docs/process/document-ids.md` as where the families are defined.

- [ ] **Step 3: Rewrite §2's first paragraph** so the layout it points at is §1.4's. Keep
      the three rules it already carries verbatim (`uv.lock` is committed; `docs/contracts/`
      is generated and never hand-edited; a filed plan under `docs/plans/` is frozen at its
      date) and keep the polyglot-monorepo and CI sentences, including the
      `(amended 2026-09-02 by the maintainer, with F49's CI enforcement)` clause — a dated
      amendment is never dropped. Add one sentence naming `docs/process/document-ids.md`
      §1.4 as the authority for the `docs/` layout and stating that **the directory is the
      family**.

- [ ] **Step 4: Verify.**

```bash
python3 scripts/audit-docs.py; echo EXIT=$?
grep -n "WF-" CLAUDE.md
```

Expected: `EXIT=0`, and every `WF-` token printed resolves to a file listed by
`ls docs/workflows/`. **A `WF-` token that does not resolve is a task failure, not a
formatting nit** — a range that resolves to nothing is exactly the defect this step exists
to remove, and audit-docs is not guaranteed to catch it (check 32 fires on *padded* ids, and
`WF-698` is unpadded).

- [ ] **Step 5: Commit.**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): W37-9 — §2 layout and §4 module map to RFC-937 §1.4"
```

---

### Task 2: `CLAUDE.md` §5 — the id-scope sentence, and G2's two permanence yields

**Files:** Modify `CLAUDE.md:103-113` (§5); `CLAUDE.md:27-28` (the §0 bullet).

**This is the slice's hardest obligation and its easiest miss** (map plan `:798-803`). The
two sites are edited **in one commit**, so no tree exists in which one is edited and the
other is not.

**Interfaces:**
- Consumes: Task 1's directory vocabulary.
- Produces: the sentence §5 gains, which `README.md` (Task 4) and `CONTRIBUTING.md` (Task 5)
  then point at rather than restate.

- [ ] **Step 1: Re-derive the two line numbers at the head you are working on.** G2 names
      `:27` and `:107`, measured at `89dd2b1`. Do not trust either number:

```bash
grep -n "permanent" CLAUDE.md
```

Expected at `a8b3c39`: `27`, `110`, `176`, `226`. `:27` is the §0 bullet (G2's first site);
`:110` is §5's own sentence (G2's second site, moved from `:107`); `:176` is unrelated
(context discipline); `:226` is DP-1's third hit. **If the output has a shape other than
"two rule statements plus `:176`", stop and ask the lead** — G2 is written against exactly
two rule sites and a third would change what "both" means.

- [ ] **Step 2: Edit §5's sentence (`:110`) with its dated yield line.** The existing
      sentence is *"Requirement IDs are permanent: never renumber, only append or mark
      superseded."* It must now say what still holds and what yielded. The dated clause
      names RFC-937, the date, and what yielded to what — G1's no-silent-change limit. Shape
      required (wording is the executor's; the four elements are not):

> **Amended 2026-09-<dd> by RFC-937 D2.** Requirement ids were renumbered once, by the
> W37-6 migration run, onto the single global sequence
> [`document-ids.md`](../process/document-ids.md) defines. The permanence
> rule holds from that sequence onward: append or mark superseded, never renumber. **Document
> and row ids are `document-ids.md`'s; product identifiers stay the spec's** — a `VR-`,
> artifact id or job kind is governed by `docs/specs/` and was not touched (RFC-937 D5).

The bolded clause is §5.1's required addition for §5, quoted from RFC-937 §5.1's
`CLAUDE.md` row. Keep §5's existing tombstone sentence (*"§6 and §8 are tombstones …"*)
unchanged — section numbers are still permanent.

- [ ] **Step 3: Edit the §0 bullet (`:27`) with its own dated line.** It currently reads
      *"Requirement IDs and section numbers are permanent (§5). Never renumber; append, mark
      superseded, or leave a tombstone."* It gets the same four elements, stated in §0's
      shorter register, and keeps pointing at §5 so the full statement lives in one place.
      **Do not make §0 a second full copy of §5's text** — RFC-756.

- [ ] **Step 4: Apply DP-1's resolution at `:226`.** Under the recommended option (c),
      **change nothing there** and record in the commit body that `:226` was read and
      classified as a citation of §5, not a restatement. Under (a), give it a dated line
      too. Under (b), say nothing further. **Whichever the lead ruled, the commit body says
      which and why** — a site read and deliberately left is not the same as a site missed,
      and only the commit body can tell a later reader apart.

- [ ] **Step 5: Verify — both sites, in one command, on the working tree.**

```bash
grep -n "permanent" CLAUDE.md
grep -c "RFC-937" CLAUDE.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

Expected: the first shows a dated RFC-937 clause adjacent to **both** `:27` and §5's
sentence; the second is `>= 2`; the third is `EXIT=0`.

- [ ] **Step 6: Commit — one commit, both sites.**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): W37-9 — §5 id scope, and G2's permanence yield at both sites"
```

**A commit touching one permanence site and not the other is a plan violation**, even if a
follow-up commit would fix it: the intervening tree is a project contract that contradicts
itself, and a branch is read at every commit by `git log -p`.

---

### Task 3: `CLAUDE.md` §9, §12 and §13–§15 — the pointers

**Files:** Modify `CLAUDE.md:137-151` (§9), `:200-247` (§12), `:248-284` (§13), `:285-302`
(§14), `:303-323` (§15).

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: nothing later tasks depend on. This is the last `CLAUDE.md` task.

- [ ] **Step 1: §9 — the roadmap pointer names the row families.** §9 already says the phase
      list and workstream rows live **only** in `docs/roadmap.md` and cites RFC-756. Add,
      without restating any status: a phase is a **milestone** section (§1.3), and the rows
      inside it are `WK-` (work) and `SL-` (slice) — the families, not their contents.
      **Do not add a count, a status or a current-phase name**: §9's entire point is that
      those live in one place.

- [ ] **Step 2: §12 — name the owner table.** §12 currently indexes
      `.claude/skills/README.md` and `.claude/agents/README.md` and describes roles. Add one
      sentence pointing at
      [`docs/process/document-ids.md`](../process/document-ids.md) **§1.6, the roles-per-family
      owner table** — which role owns which document family — and say it is the authority on
      who may write a family, complementing §12's existing rule that a role writes what its
      charter names. **Do not copy the table.**

- [ ] **Step 3: §13, §14 and §15 — repoint to the new directories.** §13 points at
      `close-workstream` and `docs/roadmap.md`; §14 at `phase-review`; §15 at
      `docs/process/delivery-process.md`. Add the record destinations §5.1 names:
      closure records and plan reviews are `docs/closures/` (`CR-`), findings are
      `docs/findings/` (`FD-`, plus `register.md`), rulings are `docs/rulings/` (`RL-`), and
      ledgers are `docs/ledgers/` (`LG-`). §13's existing rules are unchanged — including
      the **predicate clause** and its *"added 2026-09-02 by the maintainer, discharging
      register finding F85"* dated amendment, which is carried verbatim. §14's *"Raised as
      RFC-711"* citation stays.

- [ ] **Step 4: Verify.**

```bash
grep -c "docs/closures/" CLAUDE.md
grep -c "docs/findings/" CLAUDE.md
grep -c "docs/rulings/" CLAUDE.md
grep -c "document-ids.md" CLAUDE.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

Expected: each of the four greps `>= 1` (all four are `0` at `a8b3c39`); `EXIT=0`.

- [ ] **Step 5: Commit.**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): W37-9 — §9, §12 and §13-§15 point at the new families"
```

---

### Task 4: `README.md` — the tour, and how things are named

**Files:** Modify `README.md:27-47`.

- [ ] **Step 1: Fix the misdirected link (DP-5, default (a)).** `:33-35` sends a reader to
      the legacy audit directory for closure records. Closure records are `docs/closures/`.
      Confirm the residue first, then repoint:

```bash
/usr/bin/git ls-files docs/ | grep -v '^docs/[a-z]*/[A-Z0-9]'   # the two residue files
ls docs/closures/ | head -3                                     # where CR- records live
```

      RFC-937 §1.4 states that directory dissolves; the two residue files are other slices'
      business, not a reason for the front door to misdirect. Repoint to `docs/closures/`.

- [ ] **Step 2: Add the "how things are named" paragraph** required by §5.1's `README.md`
      row. One short paragraph, pointing at
      [`document-ids.md`](../process/document-ids.md): one integer sequence
      across every governed thing, the padded id leading every filename, the directory
      naming the family, and `docs/INDEX.md` as the generated index. **Two sentences at
      most, and no family list** — `README.md` is the front door, and a second copy of the
      family table is what goes stale (RFC-756).

- [ ] **Step 3: Add the branch and PR-title convention**, per DP-3's ruling. Under the
      recommended option (b) that is one line naming `sl-<n>-<slug>` and `SL-<n>: <title>`
      with the dated not-yet-in-force clause; under (a) the same line without it; under (c)
      this step is skipped and the commit body says so with the date and the reason.

- [ ] **Step 4: Add `docs/plans/`, `docs/rulings/` and `docs/closures/` to the
      "Explore the project" list** (`:39-47`), which currently names `docs/specs/`,
      `docs/adrs/`, `docs/workflows/`, `docs/findings/register.md` and `docs/roadmap.md`.
      One bullet each, no status.

- [ ] **Step 5: Verify — every link in the file resolves.**

```bash
python3 scripts/audit-docs.py; echo EXIT=$?
grep -nE 'docs/(audit|notes)/' README.md
```

Expected: `EXIT=0`; the grep returns nothing.

- [ ] **Step 6: Commit.**

```bash
git add README.md
git commit -m "docs(readme): W37-9 — the tour, and how things are named"
```

---

### Task 5: `CONTRIBUTING.md` — intake, ids, and where the work lives

**Files:** Modify `CONTRIBUTING.md:25-38`.

**Source:** reassigned here by close record `:325`, **NOT CLOSED — still pre-migration content**,
last-touching commit `01ba0bd` (#495).

- [ ] **Step 1: Fix `:28`'s register path (DP-5).** It sends a reader to the legacy audit
      directory for the findings register. The register is `docs/findings/register.md` —
      confirm with `ls docs/findings/register.md` before editing, not from this plan's text.

- [ ] **Step 2: Add the branch and PR-title convention**, per DP-3's ruling, matching Task 4
      Step 3 **word for word where the two files state the same rule** — two public files
      stating one convention differently is the duplicate-statement failure again. If they
      must differ in length, `CONTRIBIUTING.md` states it and `README.md` points here.

- [ ] **Step 3: Add "a new document has an id from `doc-id.py next`"**, the §5.1 row's own
      wording, with the command in a fenced block:

```bash
python3 scripts/doc-id.py next
```

and one sentence saying the returned integer is the document's id for life, that the
filename carries it padded to five digits, and that the directory names the family.

- [ ] **Step 4: Say where findings and proposals go**, the §5.1 row's last clause: a finding
      is an `FD-` under `docs/findings/` with a row in `register.md`; a proposal that changes
      a decision is an `RFC-` under `docs/rfcs/`; a decision already made is an `RL-` under
      `docs/rulings/`. Keep the existing "issues are intake, the register is truth" framing —
      this adds the destinations, it does not change the posture.

- [ ] **Step 5: Verify.**

```bash
python3 scripts/audit-docs.py; echo EXIT=$?
grep -nE 'docs/audit/|NT-' CONTRIBUTING.md
```

Expected: `EXIT=0`; the grep returns nothing.

- [ ] **Step 6: Commit.**

```bash
git add CONTRIBUTING.md
git commit -m "docs(contributing): W37-9 — ids, branch and PR-title convention, where findings go"
```

---

### Task 6: `.github/PULL_REQUEST_TEMPLATE.md` — the required slice line

**Files:** Modify `.github/PULL_REQUEST_TEMPLATE.md` (19 lines at `a8b3c39`).

**Source:** reassigned here by close record `:326`, **NOT CLOSED — still pre-migration content**.
`:14` still tells an author to cite *"an NT-/FR- id"*; `NT-` is a dissolved family.

- [ ] **Step 1: Replace the `## Work item` block's guidance.** Per the map plan `:806-810`:
      *"The PR template gains a required slice line, per §1.9: a merged PR's title names the
      slice it delivered, and a PR arriving without one — a hotfix, an external contributor,
      a dependency bump — gets its slice minted by the lead at triage under the phase's
      standing maintenance work item. Bot authors are exempt. The template says so."* All
      four clauses — the required line, the triage mint, the standing `WK-` maintenance item,
      the bot exemption — must appear. Remove the `NT-` token; replace with `PL-` (the plan)
      and the slice id.

- [ ] **Step 2: Apply DP-3.** Under (b) the required-line text carries the dated
      not-yet-in-force clause naming `WK-`/`W37-n` as what a PR titles today. Under (a) it
      does not. Under (c) the slice line is not added and the commit body records the
      deferral with its date and the slice that will add it.

- [ ] **Step 3: Leave `## Scope` and `## Evidence` unchanged.** The Evidence block
      (*"Name the command you ran, its totals, and the tree it ran against — never a bare
      'tests pass'"*) is a `CLAUDE.md` §13 rule in template form and is not this slice's to
      touch.

- [ ] **Step 4: Verify.**

```bash
grep -n "NT-" .github/PULL_REQUEST_TEMPLATE.md
grep -n "SL-\|maintenance\|bot" .github/PULL_REQUEST_TEMPLATE.md
python3 scripts/audit-docs.py; echo EXIT=$?
```

Expected: the first returns nothing; the second shows all four clauses; `EXIT=0`.

- [ ] **Step 5: Commit.**

```bash
git add .github/PULL_REQUEST_TEMPLATE.md
git commit -m "docs(github): W37-9 — PR template's required slice line and triage mint"
```

---

### Task 7: `.gitignore`'s comment block, and the issue templates

**Files:** Modify `.gitignore:90-99`; modify `.github/ISSUE_TEMPLATE/bug.yml` and
`.github/ISSUE_TEMPLATE/question.yml` per DP-2.

- [ ] **Step 1: Reword the `.gitignore` comment block to the new families.** `:94` names
      a plan or ledger in `docs/plans/` and a decision as an `NT-` id in the legacy notes
      directory. Two defects: that directory does not exist (`ls -d docs/notes` fails at
      `a8b3c39` — run it and see), and a ledger is its own family in `docs/ledgers/`, not
      `docs/plans/`. Reword to: a plan is `PL-` in
      `docs/plans/`, a ledger `LG-` in `docs/ledgers/`, a decision `RL-` in `docs/rulings/`,
      a proposal `RFC-` in `docs/rfcs/`. **Keep the reasoning sentences verbatim** — the
      *"unaudited account of what the project is doing"* argument and the leading-slash
      anchoring note are why the rule exists and are not this slice's to rewrite. The
      anchoring note's example, *"silently ignoring a future docs/research/findings.md"*,
      still names a real directory (`ls -d docs/research`) and stays.

- [ ] **Step 2: Apply DP-2 to the issue templates.** Under the recommended (b), add one
      optional `input` block to each template:

```yaml
  - type: input
    id: related
    attributes:
      label: Related id (optional)
      description: A governed id this relates to, if you know one — e.g. FR-451, ADR-703, FD-93.
    validations:
      required: false
```

Verify each example id in that `description` against the tree **before** committing it —
`grep -rn "FR-451" docs/specs/`, `ls docs/adrs/ | grep 703` — because a template's example
is copied by every issue author and a dead example teaches a dead id. Substitute live ones
if any fails. Under (a) also add the issue-type mirror; under (c) skip this step and record
the declination with its date in the commit body.

- [ ] **Step 3: Verify the YAML still parses**, since a malformed template silently stops
      GitHub offering it:

```bash
python3 -c "import sys,json;print('no yaml parser in this repo by G4')"
python3 scripts/audit-docs.py; echo EXIT=$?
grep -nE 'NT-|docs/notes' .gitignore .github/ISSUE_TEMPLATE/bug.yml .github/ISSUE_TEMPLATE/question.yml
```

Expected: `EXIT=0`; the grep returns nothing. **G4 forbids PyYAML in the gate scripts and
none is installed**, so the templates cannot be machine-validated here — instead compare the
new block's indentation against the existing `- type: input` block in the same file, and say
in the PR body that YAML validity was checked by structural comparison rather than by a
parser. **Do not claim a parse that was not run.**

- [ ] **Step 4: Commit.**

```bash
git add .gitignore .github/ISSUE_TEMPLATE/
git commit -m "docs(github): W37-9 — .gitignore families and the optional related-id field"
```

---

### Task 8: The three `M` rows — verify, do not edit

**Files:** Read only: `SECURITY.md`, `.importlinter`, `pyproject.toml`,
`packages/*/pyproject.toml`.

These are rows the migration script already wrote. The task is to **prove** each is closed,
because §5.1 completeness is judged over all nine rows and an `M` row assumed closed is the
same silence `CLAUDE.md` §13 forbids.

- [ ] **Step 1: `SECURITY.md`.**

```bash
grep -n "security-posture" SECURITY.md
ls docs/process/security-posture.md
```

Expected: `:40` links `docs/process/security-posture.md`, and the file exists. Record both
outputs. If the link is present but the file is absent, that is a **finding**, not a repair
this slice makes — `docs/process/` is W37-10's area.

- [ ] **Step 2: `.importlinter` (DP-4).**

```bash
grep -n "^name" .importlinter
ls docs/adrs/
uv run lint-imports; echo EXIT=$?
```

Expected: three contract names carrying `ADR-703`, `ADR-704`, `DEP-3`; the two ADR files
whose numbers those contract names carry present in the `ls` output; `EXIT=0`. **Record the DP-4 discrepancy as a
one-line finding in the PR body**: §5.1's written target names two one-character ADR
numbers that resolve to no file, while the tree's names resolve to real files — the spec is stale,
the tree is right, and the executor changed neither.

- [ ] **Step 3: the `pyproject.toml` comment citations.**

```bash
grep -rn "FR-\|NFR-\|ADR-" pyproject.toml packages/*/pyproject.toml
```

For each id printed, confirm it resolves: an `FR-`/`NFR-` in a `docs/specs/` file, an `ADR-`
to a file under `docs/adrs/`. **Paste the list and the per-id verdict**; a bare "verified" is
not evidence. An unresolvable id is a finding raised to the lead.

- [ ] **Step 4: Commit the evidence, not an edit.** If all three rows verify clean there is
      nothing to commit here; the evidence goes in the PR body's disposition table. If any
      row needed a repair inside this slice's boundary, commit it:

```bash
git commit -m "docs: W37-9 — M-row verification repairs" --allow-empty-message
```

(Prefer no commit over an empty one. The deliverable of this task is the table.)

---

### Task 9: The full gate, the disposition table, and the PR

**Files:** none modified by this task except `docs/INDEX.md` if regeneration changes it.

- [ ] **Step 1: Re-run the §2b mitigation** this plan's reconciliation section owes:

```bash
git fetch origin
grep -n "FD-1066\|FD-1067\|FD-1068\|FD-1069" docs/findings/register.md
```

If any of the four now-filed rows names a file in this slice's §5.1 table, **stop and raise
it to the lead** as a finding against this plan — the scope was derived before the filing and
this is the check that says whether that mattered. If none does, record the command and its
output in the PR body.

- [ ] **Step 2: Regenerate the index and confirm byte-stability.**

```bash
python3 scripts/doc-index.py
git status --porcelain docs/INDEX.md
python3 scripts/doc-index.py --check; echo EXIT=$?
```

Expected: `EXIT=0` and an empty `git status` line. If regeneration changes `INDEX.md`, commit
that change with the slice's work — a stale generated index fails the gate for the next
person.

- [ ] **Step 3: Run the Python/docs half.**

```bash
python3 scripts/audit-docs.py; echo EXIT=$?
python3 scripts/doc-id.py check; echo EXIT=$?
uv run ruff check .; echo EXIT=$?
uv run mypy; echo EXIT=$?
uv run lint-imports; echo EXIT=$?
uv run pytest -q; echo EXIT=$?
uv run python scripts/req-coverage.py; echo EXIT=$?
uv run python scripts/generate-contracts.py --check; echo EXIT=$?
```

All `EXIT=0`. **Run each with its own `echo EXIT=$?` on its own line** — `cmd | tail -1 &&
echo ok` reports the wrong exit code (`dev-commands`).

- [ ] **Step 4: Run the frontend half.** A Python-only "gate" has been green here while the
      frontend was red (`CLAUDE.md` §11).

```bash
pnpm --dir frontend install --frozen-lockfile; echo EXIT=$?
pnpm --dir frontend generate:api; echo EXIT=$?
pnpm --dir frontend lint; echo EXIT=$?
pnpm --dir frontend type-check; echo EXIT=$?
pnpm --dir frontend test; echo EXIT=$?
pnpm --dir frontend build; echo EXIT=$?
```

- [ ] **Step 5: Write the nine-row disposition table** into the PR body — file, `H`/`M`, the
      commit SHA that names it, and for each `M` row the verification from Task 8. Nine rows,
      none silent.

- [ ] **Step 6: Push and open the PR.** Title carries the slice per DP-3's ruling. Body
      carries: the disposition table; the DP-1…DP-5 resolutions as applied; the exit-code
      table from Steps 3 and 4 with the head SHA they were run at; the DP-4 and any Task-8
      findings; **and the space for the maintainer's dated line**, which the PR does not
      merge without.

- [ ] **Step 7: Confirm CI by head SHA, not by branch.**

```bash
git rev-parse HEAD
gh run list --branch w37-9-root-governance --limit 10
```

`gh pr checks` fails and exits `0` here (`git-hygiene`), and `gh run list -c <sha>` gives a
false "no CI ran" — filter by `--branch` and match the head SHA in the output yourself.

---

## Gates

Every one of these must be green, at the head SHA named in the PR body, before the lead
merges. Six gates, and the sixth is not a command.

| # | Gate | Command / artifact | Pass |
|---|---|---|---|
| 1 | Docs audit | `python3 scripts/audit-docs.py; echo EXIT=$?` | `EXIT=0` |
| 2 | Id lint | `python3 scripts/doc-id.py check; echo EXIT=$?` | `EXIT=0` |
| 3 | Index byte-stability | `python3 scripts/doc-index.py --check; echo EXIT=$?` **and** `git status --porcelain docs/INDEX.md` after a fresh `python3 scripts/doc-index.py` | `EXIT=0`, empty status |
| 4 | Gate half 1 (Python/docs) | Task 9 Step 3's eight commands | every `EXIT=0` |
| 5 | Gate half 2 (frontend) | Task 9 Step 4's six commands | every `EXIT=0` |
| 6 | CI, by head SHA | `gh run list --branch w37-9-root-governance` matched against `git rev-parse HEAD` | every required workflow `completed/success` at that SHA |
| 7 | **The deputy's merge-ACK** | the deputy's dated message authorising the merge | present, dated, quoted in the ledger |
| 8 | **The maintainer's dated line for `CLAUDE.md`** | DP-6 (a): *"executor drafts the diff, the slice's acceptance requires a dated maintainer line on the PR"* (`PL-939:307`) | present on the PR, dated, quoted in the merge commit body |

## Risks

| # | Risk | Why it is real here | Mitigation |
|---|---|---|---|
| R1 | **DP-6 — the `CLAUDE.md` change is PROPOSED by the executor and merges only on the maintainer's dated line.** `CLAUDE.md` §12 reserves *"an amendment to what this file requires"* to the maintainer, and DP-6 resolves to option (a): the executor drafts, the maintainer dates. G2's permanence yield is a **real amendment**, not a pointer edit, so DP-6's option (c) ("treat all of it as pointer-only") is false and cannot be fallen back on | This is the whole slice's merge condition. A green gate is not a merge here | **Drafting proceeds, merging waits.** Tasks 1–9 run to a pushed PR with a green gate; the PR then sits until the dated line exists. The executor does not chase it — the lead does. Gate 8 |
| R2 | **Discharged, partially, by this correction pass — recorded rather than deleted, since the residual half is real.** At drafting the slice was against two records not on `main`: review 13's acceptance `_pending_`; the close record on `origin/w37-6-checkpoint-3-close` (`8774db4`), not `main` (`a8b3c39`) | The close record landing was a real risk and has resolved cleanly: `CR-1065` is now on `main` (`d63f765`), byte-identical to the branch revision, so nothing this plan cited from it moved. Review 13's acceptance line is still `_pending_` — under the deputy's 09:19 ruling this plan reconciles against it as a filed proposal rather than waiting, so the risk is now "the acceptance line amends something this plan took," not "the record doesn't exist yet" | **Residual risk, not closed.** If the maintainer's line, once written, amends any of review 13's three items for this slice, that amendment corrects this plan — the trigger is the line landing. This plan is still `draft`, now for DP-1/DP-3 alone (see Status section above), not for either record-landing reason |
| R3 | **G2's line numbers have already moved** — `:107` → `:110` between `89dd2b1` and `a8b3c39` | An executor following the map plan's literal `:107` edits §5's *preceding* paragraph and the permanence sentence stays unyielded, satisfying "I edited line 107" while failing G2 | Task 2 Step 1 re-derives both numbers with `grep -n` and refuses to proceed on an unexpected shape. **Never navigate by a line number this plan or the map plan states** |
| R4 | **One permanence site edited, not both** — G2 names this as the executor's likeliest failure, because *"the second site is the one an executor working from a §5 checklist never opens"* | The result is a project contract contradicting itself | Both sites are in **one commit** (Task 2 Step 6), and Acceptance item 3 is a single grep covering both |
| R5 | **DP-3 publishes a convention citing an empty family.** Zero `SL-` ids exist (`grep -c 'SL-' docs/roadmap.md` → `0`) | The PR that introduces the required-slice-line rule cannot itself comply with it | Blocking DP; the lead rules before Task 1. Recommended (b) states the gap with a date and a removable marker |
| R6 | **Scope creep into a neighbouring slice.** W37-7, W37-8 and W37-10 run beside this one (map plan `:381`) and share a corpus of stale references | A `CLAUDE.md` edit that "just fixes" a skill or charter reference collides with another executor's branch | The Scope section's explicit not-in-this-slice list. A §5.1 edit that needs a W37-7/8/10 file is a **finding to the lead**, not an absorption |
| R7 | **A dated amendment dropped while rewriting a section.** §2 carries *"amended 2026-09-02 by the maintainer, with F49's CI enforcement"*; §13 carries the predicate clause's *"added 2026-09-02 … discharging register finding F85"*; §14 carries *"Raised as RFC-711"* | A rewrite that reads well can silently delete a dated maintainer amendment, and the record of what was believed is what a governed system cannot lose (`CLAUDE.md` §0) | Tasks 1 and 3 name each dated clause explicitly as carried verbatim. Before Task 9 Step 6: `git diff origin/main...HEAD -- CLAUDE.md` read in full, and every removed line that carries a date accounted for |
| R8 | **The nine `M`-row/`H`-row verdicts asserted rather than measured** | An `M` row is easy to wave through, and the close record's §2.4 found two `H` rows that everyone had assumed were closed | Task 8 requires the command and its output per row; Acceptance item 13 requires the nine-row table in the PR body |
| R9 | **This plan carries `PL-1072`, W37-9's assignment by the lead's slice order (W37-7 lowest, W37-8 the middle id, this plan highest), renumbered in this correction pass. Standing alone, this branch cannot be contiguity-clean.** Measured post-rebase (`origin/main` = `d63f765`) and post-renumber: `audit-docs.py` and `doc-id.py check` both give exactly one failure, `check 31: gap in the full allocation between 1069 and 1072` — because W37-7's and W37-8's plans (the two ids immediately below this one) are not in this branch's tree | A standalone leaf-plan PR that mints an id two past `main`'s current maximum is, by `check 31`'s own contiguity rule (reads the current tree's regenerated `docs/INDEX.md`), always going to show this gap until its slice-mates land | **Not a defect in this plan or its renumbering — proven by combining trees.** Copying W37-7's and W37-8's plan files alongside this file and regenerating `docs/INDEX.md` gives `audit-docs.py` `EXIT=0`, `doc-id.py check` `EXIT=0`, `doc-index.py --check` `EXIT=0`; the copies were then removed and this branch's own index restored. **The fix is merge order**: once W37-7's and W37-8's PRs land on `main` in slice order and this branch is rebased, the gap closes without touching this plan's content |

## ETA basis

Hours of **executor work**, not clock time — the lead converts. Estimated per task from the
measured size of each file at `a8b3c39` (`wc -l`: `CLAUDE.md` 323, `README.md` 58,
`CONTRIBUTING.md` 38, `SECURITY.md` 40, `PULL_REQUEST_TEMPLATE.md` 19, `.gitignore` 125,
`.importlinter` 59) and the number of distinct decisions each edit carries.

| Task | Work | Hours | Basis |
|---|---|---|---|
| 0 | Reading: `spec-change`, RFC-937 §1.2/§1.4/§1.6/§1.9/§5.1, the map plan's slice section, this plan | 1.0 | ~600 lines of specification read closely, not skimmed |
| 1 | `CLAUDE.md` §2 + §4 | 1.0 | Two sections, ~35 lines; one citation-repair decision (the `WF-` range) that needs the directory listed first |
| 2 | `CLAUDE.md` §5 + the §0 bullet | 1.5 | The slice's hardest obligation: two sites, one commit, a four-element dated clause each, plus DP-1's classification of the third hit. Highest per-line cost in the slice |
| 3 | `CLAUDE.md` §9 + §12 + §13–§15 | 1.0 | Five sections but all pointer additions; the care is in *not* copying tables and not dropping R7's dated clauses |
| 4 | `README.md` | 0.75 | 58 lines; four edits, one of them DP-3-dependent |
| 5 | `CONTRIBUTING.md` | 0.75 | 38 lines; four edits, one shared word-for-word with Task 4 |
| 6 | PR template | 0.5 | 19 lines; four required clauses in one block |
| 7 | `.gitignore` + two issue templates | 0.75 | One comment block reworded with its reasoning preserved; two YAML blocks added and structurally checked, no parser available (G4) |
| 8 | The three `M` rows | 0.5 | Read-only; the cost is per-id verification, not editing |
| 9 | Gate, disposition table, PR | 1.25 | Both gate halves; the frontend half dominates (`install` + `build`); plus the nine-row table and the CI-by-SHA confirmation |
| | **Total** | **9.0** | Excludes all waiting: DP-1/DP-3 rulings, the maintainer's dated line (R1), CI queue time, and the auditor's pass |

**Two things this estimate deliberately excludes**, because they are not executor work and
the lead schedules them separately: the **maintainer's dated line**, which gates the merge and
not the work, and the **auditor's verification pass**, which is a different role's budget.

## Self-review

Run against this plan before it was filed, per `writing-plans`.

1. **Spec coverage.** All nine RFC-937 §5.1 rows appear in the Scope table and each maps to a
   task: rows 1 → Tasks 1–3, 2 → 4, 3 → 5, 4 → 8, 5 → 6, 6 → 7, 7 → 7, 8 → 8, 9 → 8. Both
   G2 sites are Task 2. Both close-record reassignments are Tasks 5 and 6. No §5.1 row is
   unassigned.
2. **Placeholder scan.** No "TBD", no "add appropriate error handling", no "similar to Task
   N". Every `grep` and every gate command is written out. The one place a literal is not
   supplied — the exact wording of §5's amended sentence — names the **four required
   elements** and says the wording is the executor's, which is the "name the authority rather
   than supply a sample" fallback `docs/plans/README.md` convention 3 asks for.
3. **Literal consistency.** Every repository literal in this plan was measured at `a8b3c39`
   and the measuring command is printed beside it: the four zero-counts in Acceptance item 4,
   the four dead-path hits in item 5, the `WF-698…05` token, the `SL-` zero counts in DP-3,
   the `.importlinter` names in DP-4, the two residue files in the legacy audit directory in DP-5, the
   pre-migration commit `01ba0bd` on four files, and every `wc -l`. **Line numbers are the
   exception and are marked as such**: `:27`, `:110`, `:226`, `:94`, `:14`, `:28`, `:35`,
   `:40`, `:97` are true at `a8b3c39` and Task 2 Step 1 re-derives the two that matter rather
   than trusting them.
4. **Rulings sweep.** The four site classes — narrative, Files, Steps, Acceptance — were
   checked separately for DP-6, G2 and DP-3. DP-6 appears in Roles, Gate 8, R1 and the Status
   section; G2 in Global Constraints, Task 2's five steps, Acceptance items 1 and 3, and R3/R4;
   DP-3 in the Decision points table, Task 4 Step 3, Task 5 Step 2, Task 6 Step 2 and R5.
