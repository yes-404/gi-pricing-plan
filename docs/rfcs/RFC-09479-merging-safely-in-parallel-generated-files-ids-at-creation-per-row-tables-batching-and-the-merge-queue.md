---
id: RFC-9479
family: proposal
kind: process
title: Merging safely in parallel — generated files, ids at creation, per-row tables, batching, and the merge queue
status: draft                  # working id; the mint date will replace `created` (check 31)
created: 2026-10-08
owner: maintainer
tree: 8b0256fdb5f000c11817838c129e1f9a4f8d8e10
deliverable: a ruled choice per part (P1 to P5) and a sequence; each part taken lands as its own Work or Slice, never in this RFC's PR
lands_in: .claude/roles/lead.md rule 4, docs/process/delivery-process.md §8, docs/process/document-ids.md §1.4 §1.7 §1.11, scripts/doc-id.py, scripts/doc-index.py, scripts/audit-docs.py, .github/workflows, the repository ruleset (a setting the user owns)
trigger: the user's question of 2026-10-08, how to stop late merges causing conflicts and doc-id errors
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [WK-1178, RFC-937]
---

# RFC-9479 — Merging safely in parallel: generated files, ids at creation, per-row tables, batching, and the merge queue

**Working id RFC 9479**, not minted. **Drafted by planner-rfc9479; owned by the maintainer**
(`document-ids.md` §1.6, RFC row). **`status: draft`**, the §1.2a word for "proposed": this RFC
decides nothing. It ends with the options for the maintainer's ruling (an `RL-`), and P1 is then
**the user's decision**, because it is a repository setting and possibly an ownership transfer.

**Authority.** `~/gi-pricing-plan.local/channel/to-lead.md` (a local channel file, so cited by
its header), the entry headed exactly:
`## 2026-10-08 11:26:43 BST — USER-APPROVED: raise ONE proposal (an RFC, WK-1178) on "merging safely in parallel": merge queue, generated files, id allocation, per-row tables, batching`,
and the two later entries on P1: `## 2026-10-08 11:27:49 BST — RFC 9479 addition for P1: the repo is USER-owned; the merge queue may be unavailable`
and `## 2026-10-08 11:30:48 BST — The USER confirmed: "Require merge queue" is NOT offered in the ruleset editor (user-owned repo)`; and, for P2 and P5, `## 2026-10-08 11:35:05 BST — The RFC 9479 options memo noted (sent seconds before this entry); two asks for the RFC` and `## 2026-10-08 11:37:20 BST — USER-APPROVED, EFFECTIVE NOW: a new governed-record draft gets NO PR; PRs are opened only as mint BATCHES (and for slices, activations and urgent fixes)`.
The last one, verbatim: *"case (b) applies. The merge queue is UNAVAILABLE on yes-404/gi-pricing-plan
as owned today. P1 presents: transfer the repo to a free organisation (the cost, the risks and
what moves) versus skipping P1. The other parts (P2 generated files, P3 ids at creation, P4
per-row tables, P5 batching) must stand on their own WITHOUT the queue, and the recommendation
must say which order relieves today's conflicts soonest without a transfer."*

**Input.** The decision-maker's options memo `~/gi-pricing-plan.local/handover/rfc-9479-options-2026-10-08.md`
(framing, not a ruling, measured at `c0aab813`). Every fact below that the memo states was
re-checked at this RFC's tree, or is marked as cited. Where this RFC disagrees with the memo,
§8 lists it.

**Every executor-day figure is an ESTIMATE**, not a measurement. Each states its basis. An
"executor-day" is one executor session-day of build, test and broken-input proof, excluding
review, ACK and CI wait.

---

## Measurements at this RFC's tree

**Tree:** `8b0256fdb5f000c11817838c129e1f9a4f8d8e10` (`origin/main`, #1238, committed
2026-10-08T11:33:16+01:00). Repository files were read in the worktree at that commit. GitHub
state was read at **2026-10-08 11:35:54 BST** (`TZ=Europe/London date`), and moves with every PR.

| # | Fact | Corpus and predicate (verbatim, runnable) |
|---|---|---|
| M1 | The repository is owned by a **personal account** and is public: `{"owner_type":"User","visibility":"public"}`. GraphQL `mergeQueue(branch:"main")` is `null`; `viewerCanAdminister` is `true`. | `gh api repos/yes-404/gi-pricing-plan --jq '{owner_type:.owner.type, visibility:.visibility}'` ; `gh api graphql -f query='{repository(owner:"yes-404",name:"gi-pricing-plan"){mergeQueue(branch:"main"){id} viewerCanAdminister}}'` |
| M2 | One ruleset, `main-protection` (id 21860967), `enforcement: active`, **no bypass actors**. Rules: `deletion`, `non_fast_forward`, `required_linear_history`, `pull_request` (`allowed_merge_methods: ["squash"]`, 0 approvals). **No `required_status_checks` rule.** | `gh api repos/yes-404/gi-pricing-plan/rulesets/21860967 --jq '{enf:.enforcement,bypass:.bypass_actors,rules:[.rules[]\|{type,p:.parameters}]}'` |
| M3 | **73 open PRs, 72 of them drafts.** 8 were opened before 2026-10-01. By creation date: 09-29 1, 09-30 7, 10-01 3, 10-05 60, 10-08 2. | `gh pr list -R yes-404/gi-pricing-plan --state open --limit 200 --json number,isDraft,createdAt,files > /tmp/rfc9479-prs.json`, then `jq 'length'`, `jq '[.[]\|select(.isDraft)]\|length'`, `jq '[.[]\|select(.createdAt<"2026-10-01")]\|length'`, `jq -r '[.[]\|.createdAt[0:10]]\|group_by(.)\|map("\(.[0]) \(length)")\|.[]'` on that file |
| M4 | Of the 73: **72 touch `docs/INDEX.md`** (all but #1159), 25 touch `docs/findings/register.md`, 20 touch `docs/roadmap.md`, 5 touch `docs/open-questions.md`, **0 touch `docs/contracts/openapi/generated.json`**. **71 touch only paths under `docs/`** (all but #1236 and #1159). No PR is at the 100-file cap of the `files` list, so these counts are exact, not floors. | on the same file: `jq --arg p <path> '[.[]\|select([.files[].path]\|index($p))]\|length'` per path; `jq '[.[]\|select([.files[].path\|startswith("docs/")]\|all)]\|length'`; `jq '[.[]\|select((.files\|length)>=100)]\|length'` → 0 |
| M5 | Merge queue eligibility: **unavailable on this repository as owned today.** The user's own observation (authority entry 11:30:48): "Require merge queue" is not offered in the ruleset editor. This agrees with M1 (`mergeQueue` null) and with GitHub's GA changelog, which limits the queue to organisation-owned public repositories and Enterprise Cloud. | https://github.blog/changelog/2023-07-12-pull-request-merge-queue-is-now-generally-available/ (cited from the memo, not re-fetched) |
| M6 | `history-policy.yml` triggers on `push` to main and on `pull_request` **with no `paths:`** (:39–42), deliberately: its header (:9–14) says a filtered version "would pass by not running". `docs.yml`, `python.yml` and `frontend.yml` are path-filtered, and **`python.yml`'s filter includes `docs/**`** (:31 for push, :69 for pull_request), so every docs PR runs the full pytest suite. No workflow has a `merge_group:` trigger. | `git grep -n -E '^on:\|paths:\|- .docs/\*\*\|merge_group' -- .github/workflows/` |
| M7 | **Check 31 reads contiguity from `docs/INDEX.md`**: `fail(f"check 31: gap in the full allocation between {lower} and {upper}")` (`scripts/audit-docs.py:1829`), when `migrated_tree()` (:134) is true. The sentinel is the existence of `docs/INDEX.md` and `docs/REDIRECTS.csv`; `docs.yml` :122 uses the same sentinel to choose `doc-id migrate --verify`'s `--ref`. | `grep -n 'check 31: gap\|def migrated_tree' scripts/audit-docs.py` ; `grep -n 'REDIRECTS' .github/workflows/docs.yml` |
| M8 | `document-ids.md` §1.7 (:179), verbatim: *"`python3 scripts/doc-id.py next` fetches `origin/main`, reads the maximum across every header, every spec bold-id, every roadmap row and `INDEX.md`, prints max + 1. The number is taken by the commit that adds it; a collision at rebase is fixed by renumbering the unmerged item. `doc-id.py check` fails the gate on any duplicate or header/filename mismatch. Switching to GitHub-issue-number allocation later is a policy change inside `doc-id.py`, not a renumbering."* | `sed -n '179p' docs/process/document-ids.md` |
| M9 | **The working-id and mint-at-readiness convention is written in no governed document except one sentence.** The only hits are `lead.md:167` (the post-mint sweep) and two dated amendment notes in `delivery-process.md` :55 and :57 that only *label* an id "(working id)". The rule itself is a channel entry: `to-lead.md` line 7442, headed `## 2026-09-28 11:23:26 BST · [the maintainer's (by delegation)] · ids are MINTED AT MERGE-READINESS, not reserved: first ready, first merged. …` *[elided: the header names the delegate by the word our records bar; quoted here with that word replaced]*. Its reason, verbatim: *"Check 31's contiguity would hold A1, and everything after it, up to 90 minutes behind D's ruling. Any fixed order makes one queue wait on the other."* A reservation table was tried and withdrawn that morning because of check 31. | `git grep -n -iE "working id" HEAD -- docs/process .claude/roles .claude/skills` → 3 hits |
| M10 | `lead.md` rule 4 (:159–171) requires the ACK to name the PR and its **full head SHA**, merging with `gh pr merge --squash --match-head-commit <that SHA>`, and: *"If `main` moves after the ACK, re-request: an ACK is valid only against the main it names."* **The rule does not say "expected tree" and does not require a merge of main or a re-CI after a move**; the expected tree is current practice (for example the 11:32:55 ACK of #1238: *"the EXPECTED TREE is d82d9831…"*). | `sed -n '159,171p' .claude/roles/lead.md` |
| M11 | `scripts/doc-index.py` imports no `subprocess` and runs no `git`: INDEX is a pure function of the tree, so any merge result can regenerate it deterministically. | `grep -n 'import subprocess' scripts/doc-index.py` → no hit |
| M12 | CLAUDE.md §2 binds `docs/contracts/` as *"committed, a published spec artifact rather than a build output, CI failing on drift (FR-451)"*. INDEX is not under that sentence; its committed status comes from RFC-937 (`document-ids.md` §1.11, check 39: *"docs/INDEX.md byte-stable against a fresh regeneration"*, `audit-docs.py:105`). | `grep -n '39\. docs/INDEX.md' scripts/audit-docs.py` |
| M13 | **No governed document carries the under-30 open-PR cap, the mint-batch size or the "never a rebase" merge rule.** They are in force by channel rulings (P5 cites each) and written in no governed file. | `git grep -n -iE 'under 30\|open-PR cap\|30 open\|never a rebase' -- .claude/roles/lead.md docs/process/delivery-process.md .claude/skills/git-hygiene` → 0 hits |
| M14 | The merge procedure is **`lead.md` rule 4**. `delivery-process.md` has no merge-procedure section: its §15 is "Correction and message discipline", and parallelism is §8. | `grep -n '^## ' docs/process/delivery-process.md` |

## Problem

The user asked how to stop late merges causing code conflicts and doc-id errors. Three
mechanisms, each verified above:

1. **Ids are allocated at mint, from one global sequence, and check 31 fails on any gap** (M7,
   M8, M9). So merge order must equal id order, and a draft cannot carry its final id.
2. **Generated or shared files conflict on almost every pair of PRs**: INDEX on 72 of 73 open
   PRs, register on 25, roadmap on 20 (M4). Each conflict means merge main, regenerate, push,
   re-CI (about 24 min of pytest even for a docs PR, M6), and a new ACK (M10).
3. **Merges are serial, behind one ACK each, with no queue available** (M1, M2, M5).

The incidents the authority asks for, by PR:

- **I1 — re-CI after every main move: #1233.** Its commit list (`gh pr view 1233 --json commits`)
  has **seven merges of main**: a8830c06 (← c6886bda), f0caf4d5 (← f871ee8d), 76322e8c
  (← 2b83e089), 11b7ee06 (← 8bc01ae8), 7eb8ef56 (← 5351f116) on 6 Oct, and aa0b7893 (← 0ee8f414,
  #1235) and 96bcdb0e (← c0aab813, #1237) on 8 Oct. **The last one merged a main move that
  touched only `frontend/pnpm-lock.yaml`** (`git show --name-only c0aab813`), disjoint from every
  path #1233 touches.
- **I2 — INDEX conflicts.** From the lead's 6 Oct log (cited from the memo): merge-tree 841485a3
  vs f871ee8d *"rc 1, conflicts INDEX + roadmap.md"*; #1233 ← 2b83e089 *"conflicts INDEX + one
  register hunk"*; SL-1430's mint ← 8bc01ae8 *"INDEX the only conflict"*. Today, 72 of 73 open
  PRs carry an INDEX hunk (M4).
- **I3 — append-adjacent conflicts in shared tables.** #1233 vs #1235 conflicted in
  `docs/roadmap.md` only (the SL-1472 / SL-1448 adjacency); T1 and #1239 (T2) both write
  `register.md`, and #1239 pushed register rows before T1 merged (accepted as harmless at
  11:10:23).
- **I4 — check-31 gaps while ids wait in merge order.** #1239 carries ids 1487–1495 while T1's
  1478–1486 are unmerged; its local audit read *"FAILED (4) = expected check 31 gaps"*. Every
  draft with a working id reds check 31 by design (#1236, *"only the expected check-31 working-id
  row"*).
- **I5 — re-point commits.** #1233 has three: 2ccfa027, aca34794 and 159c0c3c. The last two
  follow a merge of main and re-point citations that the merged commits introduced.
- **I6 — the count rises before it falls.** Open PRs went 78 → 81 between 10:43 and 11:09 BST
  (authority 11:10:23, *"batch PRs open before anything merges"*) and are 73 at 11:35:54 (M3).

**One counter-example, already today:** #1238 merged across two main moves (#1237, #1233)
**without a merge of main and without a new CI run on its branch**: its only commit is 98d15659,
and the 11:32:55 ACK names *"the EXPECTED TREE … d82d9831… (my own merge-tree: rc 0, the same)"*.
Rule 4 already allows that (M10). P1's option 1E writes it down.

## Proposal

Five parts, each with its options, trade-offs, cost (an ESTIMATE with its basis), the files it
changes, what it would have changed today, and a recommendation. A recommendation is a proposal
for the maintainer's ruling, never a decision; P5 alone records rules already in force.

### P1 — a merge queue, or its substitute

**Status.** Case (b): the queue is unavailable as the repository is owned (M1, M5).

| | Option | What it takes | Trade-offs | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|
| **1A** | **Skip P1.** Keep the serial ACK, `merge-tree` and `--match-head-commit`: a hand-run queue of size 1. | nothing | No transfer risk. Merges stay serial, behind the lead. | 0 | — |
| **1B** | **Transfer the repository to a free GitHub organisation, then enable the queue.** | **The user's decision and action.** After the transfer, the prerequisites come **first**, in this order: **(i)** a `merge_group:` trigger on all four workflows; **(ii)** one always-reporting aggregator job per path-filtered workflow, because `paths:` does not apply to `merge_group` and a required check that never reports stalls the queue (a `git diff --name-only` step, not a third-party action, which `docs.yml`'s header refuses); `history-policy` gets a `merge_group` range (`merge_group.base_sha..merge_group.head_sha`), or it scans only the tip; **(iii)** only then the ruleset's required-checks rule and "Require merge queue" with squash. | **Moves with the transfer:** history (every SHA and PR number unchanged, so every ledger, ACK and citation stays valid), issues, PRs, rulesets, secrets, webhooks, deploy keys. **Changes:** the URL (GitHub redirects it, including git remotes, until someone recreates `yes-404/gi-pricing-plan`; update the remotes anyway); **the fine-grained PAT must be re-issued with the organisation as resource owner** (until then every `gh` call fails, a hard stop for the merge procedure, so the transfer needs a quiet window); Actions and Dependabot settings re-checked at organisation level. 54 lines in 20 files mention `yes-404` (`git grep -c yes-404 HEAD -- . ':!docs/INDEX.md'`); `lead.md:41–44`'s `author.login` rule still holds, since a transfer does not change PR authorship. **Once on:** the REST merge cannot enqueue, so the merge becomes `gh pr merge --auto` or GraphQL `enqueuePullRequest`; the ACK keeps the head SHA but cannot name the expected tree (GitHub builds it from main plus the PRs ahead); the read-back compares the new main's tree with the tree the `merge_group` run tested; an ejection is the new re-request. **Worthless before P2:** the queue's build is a plain merge, so an INDEX conflict ejects the PR (72 of 73 open PRs, M4). | **2.0** — basis: (i)+(ii) 1.0 (four workflow files, an aggregator each, a broken-input proof that a filtered-out workflow still reports); ruleset, `lead.md` rule 4 and `git-hygiene` 0.5; a dry run on three docs PRs 0.5. The user's transfer, PAT and settings work comes on top. | `.github/workflows/{docs,python,frontend,history-policy}.yml`; the ruleset (a setting); `.claude/roles/lead.md` rule 4; `.claude/skills/git-hygiene`; CLAUDE.md §2's CI sentence (the maintainer's) |
| **1C** | Required status checks with "require branches to be up to date", on the personal repository (no queue). | A ruleset edit and the aggregators of 1B (ii). | Enforces CI on a head that contains current main: what the lead does by hand now. It **adds** re-CI rather than removing it. No parallelism. | 1.0 — basis: 1B (ii) alone | as 1B (i)–(ii); the ruleset |
| **1D** | A hand-built merge train: N PRs into one integration branch, one CI run, then ordered squashes. | A new script and procedure. | Each squash still moves main under the next PR, so the per-PR ACK tree must be recomputed for the train. More procedure and more ways to fail than a queue. | 1.5–2.0 — basis: a new script plus its tests, plus `lead.md` | `lead.md` rule 4, a new script |
| **1E** | **No transfer: an ACK carries over a main move when the merge is mechanically clean.** When main moves, the lead recomputes `git merge-tree` of the ACKed head on the new main. If it exits 0 **and** the commits that moved main touch **none of the PR's paths**, the lead runs the docs checks (audit-docs, `doc-index.py --check`, `register-lint.py`) on that recomputed tree and re-ACKs naming it, **without merging main into the branch and without a new branch CI run**. Full CI then runs on main's push as the backstop; a red main is fixed forward before any other merge. | A `lead.md` rule 4 amendment (the maintainer's) and nothing else. | **Removes the per-move re-CI, the largest cost in I1**, with no transfer. It moves pytest detection from before the merge to after it: `python.yml` triggers on `docs/**` because tests assert on docs content, so a docs PR that breaks one reaches main red. **Bounds:** only PRs whose paths are all under `docs/` (71 of 73 today, M4); never while main is red. It is already practice once: #1238 (Problem). | **0.25** — basis: one rule paragraph in `lead.md` and its read-back line | `.claude/roles/lead.md` rule 4 |

**What it would have changed today.**
- **1E:** #1233's 96bcdb0e (← c0aab813, a lockfile-only move, disjoint paths) would not exist,
  nor its re-CI; the ACK would have carried over on a recomputed tree, as #1238's did.
  aa0b7893 (← 0ee8f414, #1235) would still be needed, because #1235 touched INDEX and
  `roadmap.md` as #1233 did. P2 and P4 remove that remaining case.
- **1B:** #1235, #1237, #1233 and #1238 would have been four queue entries with no re-ACK
  between them; without P2, each docs entry would have been ejected at its INDEX hunk.

**Recommendation: 1A + 1E now.** Put 1B to the user **only after P2 has landed and 1E has run
for 14 days**, with that period's serial-wait cost as the case for or against a transfer. The
recommendation holds in both cases: without a transfer, 1E plus P2–P5 carry the relief; with a
transfer later, 1E retires, and nothing in P2–P5 is wasted, since the queue needs P2 and the
prerequisites (i)–(ii) either way. Reject 1C (it buys enforcement, not speed) and 1D (a
home-made queue).

---

### P2 — generated files out of manual merges

Scope: `docs/INDEX.md` (generated, committed, read by check 31 and by `doc-id next`: M7, M8)
and `docs/contracts/openapi/generated.json` (generated, committed, a published spec artifact:
M12).

| | Option | Trade-offs | The `--check` gate, and CLAUDE.md §13 | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|
| **2A** | **Leave as now.** Every PR regenerates INDEX; a PR behind main merges main and regenerates again. | Works serially. It is the I2 cost on 72 of 73 PRs, and it blocks any queue. | `doc-index.py --check` proves freshness only. | 0 | — |
| **2B** | **A local git merge driver** (`.gitattributes`: `docs/INDEX.md merge=…`) that keeps one side, followed by a regeneration. | **GitHub's server-side mergeability, its merge and any queue never run custom drivers**, so the PR still shows conflicting until someone merges main locally. A driver sees one file, not the merged tree, so it cannot regenerate INDEX by itself (M11). Its command lives in each clone's `git config`. | unchanged | 0.25 — basis: a driver script and a skill line | `.gitattributes` (new), a driver under `scripts/`, `git-hygiene` |
| **2C** | **PRs stop committing INDEX; a post-merge CI job regenerates and commits it to main.** | **Blocked by the ruleset** (M2: no bypass actors): a bot cannot push to main without a bypass and `contents: write`, which reverses every workflow's least privilege. Between merge and bot commit, main's INDEX is stale, and `doc-id next` and check 31 read a stale allocation. | `--check` on main flickers red then green after each merge. | 1.5, plus a ruleset change by the user — basis: a workflow job, a GitHub App bypass, the stale-window handling | `docs.yml`, the ruleset, `doc-id.py`, `audit-docs.py` |
| **2D** | **INDEX becomes a build output.** Not committed; every consumer (`doc-id next`, check 31, check 32) calls the `doc-index` generator in memory; CI publishes INDEX as an artifact. `migrated_tree()` gets a sentinel that does not need INDEX (`docs/REDIRECTS.csv` alone, or a constant now the migration is done); check 39 retires. | **Removes the most frequent conflict entirely**, with or without a queue, and makes 1B viable. Costs an amendment to the id standard (INDEX is RFC-937's one-row-per-id artifact and check 39's subject; `document-ids.md`'s owner line: *"amendments arrive as an RFC- + RL- pair"*). Readers on GitHub lose a rendered INDEX unless CI publishes one. **The sentinel also selects `docs.yml`'s `--ref` (M7): that line is the risky one**, and needs its broken-input proof. | The freshness check disappears, which §13 supports: *"a generated artifact matching its source proves neither correct"*. Correctness stays with `doc-index.py`'s own tests. | **2.0** — basis: the readers in `doc-id.py` and `audit-docs.py` 1.0; sentinel, `docs.yml` and the broken-input proofs 0.5; the standard's amendment and two skills 0.5 | `scripts/doc-id.py`, `scripts/audit-docs.py` (checks 31, 32, 39, `migrated_tree`), `scripts/doc-index.py`, `.github/workflows/docs.yml`, `.gitignore`, `docs/process/document-ids.md` §1.4 / §1.11 (RFC + RL), CLAUDE.md §4's pointer, `.claude/skills/docs-audit`, `.claude/skills/doc-id-migration-run` |
| **2E** | **No code: a draft commits no INDEX hunk; INDEX is regenerated only at the merge turn**, by the mint commit, which already regenerates it (M9's 28 Sep rule, step 2: *"file name, front matter, internal references, INDEX regenerated"*). | **Largely delivered already by 5d** (drafts are `draft/` branches, not PRs, since 11:37:20), so 2E is a one-line clarification of 5d: a draft branch carries no INDEX hunk, and the batch PR regenerates INDEX once. Without the hunk, a draft's check 31 goes **green** (its contiguity reads the committed INDEX, `audit-docs.py:1826`, which then lacks the working id: DP-8's own design, `doc-id.py:436–446`), while check 39 reds (INDEX stale) and **check 32 reds on each citation of the draft's own new ids** (it resolves prose citations in INDEX, `audit-docs.py:1946`). A writer checks locally on a regenerated, uncommitted INDEX. **It does nothing for the INDEX conflicts that remain between batch, slice and activation PRs** (#1233, #1235, #1238 all carried INDEX hunks); only 2D removes those. | unchanged at the merge turn, where the check runs | **0.1** — basis: one sentence in 5d's written form | `.claude/roles/lead.md` rule 4, `docs/process/delivery-process.md` §8 |

**What replaces INDEX under 2D** (the maintainer's ask (b), entry 11:35:05). INDEX today plays
four roles. Each one's replacement, and every reader, at this RFC's tree:

| Role / reader today | Where (this tree) | Under 2D |
|---|---|---|
| **A reader on GitHub** browses one table of every id, its family, title, status and owner, and a plan's derived `execution` column (`document-ids.md` :181) | `docs/INDEX.md`, rendered by GitHub | A docs CI job on every push to main runs `doc-index.py` and publishes the result as a workflow artifact, and `doc-index.py --show <ID>` serves one record locally. **The honest loss: GitHub no longer renders INDEX in the repository browser**; a reader follows a link to the latest artifact, or reads the per-family directories, whose filenames already carry id and slug (§1.4). A GitHub Pages copy would restore a rendered page, at the cost of a `pages: write` workflow, which is a further option, not part of 2D. |
| **The migration sentinel** `migrated_tree()`: INDEX plus `REDIRECTS.csv` exist | `scripts/audit-docs.py:134–150`; `scripts/_docid.py:324–330`; `.github/workflows/docs.yml:122` (selects `doc-id migrate --verify`'s `--ref`) | The sentinel becomes `docs/REDIRECTS.csv` alone, which only the migration creates and which stays committed. Its callers are unchanged: the requirement- and OQ-id grammar (`audit-docs.py:210–211`), `check_notes` (:467), check 28 `check_plan_acceptance_standard` (:1107), `_id_scope_roots` (:1288), check 31 (:1823), check 38 `check_loop_signal` (:3466). Broken-input proof: delete `REDIRECTS.csv` in a scratch tree and every one of them must flip, as it flips today on deleting INDEX. |
| **Check 31's contiguity** (the full allocation) | `audit-docs.py:1823–1829` reads `ROOT / "INDEX.md"` | Reads `_doc_index.build_corpus(ROOT)` in memory, the corpus check 39 already builds (:3528), over the checked-out tree. The checked-out tree of a PR is what its committed INDEX represents today, since every PR regenerates INDEX in its final commit, so the predicate is unchanged. |
| **Check 32's citation resolution** | `audit-docs.py:1946–2007` (`index_ids` from `ROOT / "INDEX.md"`, :1962–1974) | The same in-memory corpus's id set. |
| **Check 38's "cited by nothing outside INDEX.md"** | `audit-docs.py:3458` | Unchanged in meaning; the exemption for INDEX becomes moot, since INDEX is no longer in the tree. |
| **Check 39: INDEX byte-stable against a fresh regeneration** | `audit-docs.py:3497–3572`; also `doc-index.py --check` in `docs.yml` (the `doc-index --check` stage) | **Retired**, both the audit check and the CI stage. Its other two clauses (a merged PR's title names its `SL-`; the slice's ledger records the PR, `document-ids.md` :235) stay. |
| **`doc-id.py next`, source 4 of 4, and `doc-id.py check` row (b) contiguity**, both over `origin/main`'s committed INDEX, never the working tree (DP-8: an unmerged draft must not manufacture a phantom gap or be counted) | `scripts/doc-id.py:400–416` (`scan_index_ids`), :436–446, :510–520 (`find_noncontiguous_gaps`); `materialize_ref` :108–118 | `next` already materialises `origin/main` into a throwaway directory (:108–118); it runs the generator over that tree instead of reading its INDEX. DP-8 holds unchanged, because the input is still the merged tree, never the working tree. |

**The lines that change, quoted.**
- `CLAUDE.md` :107–108 (§4, a pointer the maintainer edits): *"`docs/INDEX.md` is the generated
  index of every governed document in the suite"* → it names the published artifact and
  `doc-index.py --show`.
- `document-ids.md` :94 (§1.4 tree): *"├── INDEX.md               generated — one row per id, rows
  and documents alike"* → not committed; generated by CI and on demand.
- `document-ids.md` :179 (§1.7): *"reads the maximum across every header, every spec bold-id,
  every roadmap row and `INDEX.md`"* → "and the generated index of that tree".
- `document-ids.md` :199 (§1.8): *"regenerates `INDEX.md` … Trigger: `INDEX.md` passes 90 000."*
  → the trigger is the generated index's row count.
- `document-ids.md` :228 (§1.11, check 32): *"Every `<PREFIX>-<n>` in prose resolves in
  `INDEX.md`"* → "in the generated index".
- `document-ids.md` :234 (check 38): *"cited by nothing outside `INDEX.md`"* → "cited by nothing".
- `document-ids.md` :235 (check 39): *"`INDEX.md` byte-stable against a fresh run"* → struck,
  the other two clauses kept.
- `document-ids.md` :239 (§1.12): *"`INDEX.md` gains rows"* → "the generated index gains rows".
- `document-ids.md`'s owner line: *"amendments arrive as an RFC- + RL- pair (§1.6)"*: this RFC
  plus the ruling's `RL-` satisfy it.
- `CLAUDE.md` §2's *"committed, a published spec artifact"* sentence does **not** change (M12).

**`generated.json`, separately: leave it as now.** 0 of 73 open PRs touch it (M4); the one
recorded conflict auto-merged to the generator's output (I2, SL-1430's mint); CLAUDE.md §2 binds
it as committed, and changing that is the maintainer's amendment with nothing measured to justify
it. Under 1B its `--check` must run in `merge_group`, because two API PRs can each pass alone and
drift together; that is the one place a queue adds safety a merge-time check cannot.

**What "committed, published artifact" (CLAUDE.md §2) then means.** Unchanged: it is
`docs/contracts/` only. INDEX was never under that sentence (M12), so 2D amends the id standard,
not CLAUDE.md §2.

**What it would have changed today.**
- **2D:** 72 of 73 open PRs lose their INDEX hunk. #1233's merges of main on 6 Oct would
  each have had one conflict fewer (841485a3 vs f871ee8d; ← 2b83e089); SL-1430's mint ← 8bc01ae8
  would have had none. #1235 and #1238 would each have had no INDEX change to carry across a move.
- **2B:** the same local resolutions become mechanical, but GitHub still shows the PR
  conflicting until the local merge, so no re-CI is saved.

**Open to extension.** A reduction of the docs burden is being weighed separately (the 11:40:59
entry, item 4); this part is not widened for it, and any option it produces for generated files
joins this part rather than a new one.

**FD 9489, already decided** ("## 2026-10-08 10:51:33 BST — …", item (i)): INDEX keeps one row
per OQ number, the spec §10 row. It is a `doc-index.py` fix; 2D carries it unchanged, because the
generator is what every consumer then calls.

**Recommendation: 2D as the build; 2E as a clarification inside 5d.** With 5d in force, drafts no
longer conflict as PRs, and 2E only says what a draft branch commits. What remains is the INDEX
hunk on every batch, slice and activation PR, and only 2D removes it; it also makes a queue
possible. **2B is not recommended**, against the memo's no-transfer order, which used it as a
stop-gap: 5d already removes the draft-to-draft conflicts, and 2B leaves GitHub's mergeability
and the re-CI unchanged. Contracts as now.

---

### P3 — ids allocated at creation

**Today's rule** ("## 2026-10-06 01:59:10 BST — B2+B3 as ONE batch (6 PRs, 9 records): OK; ids must follow MERGE order (SL-1430's ledger)"), verbatim: *"If SL-1430 is late, re-allocate rather than reorder merges. You allocate; just keep the id order equal to the merge order."*

**The objection P3 must answer (M9).** A reservation table was tried on 28 Sep and withdrawn the
same morning: under check 31's contiguity, whichever record holds the lower id holds every higher
one behind it. Allocation at creation works **only if check 31 can tell a reserved-but-unmerged
gap from a lost record.**

| | Option | Ledger: where, who writes, collisions | Check 31 | Permanence (CLAUDE.md §5) and abandoned ids | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|---|
| **3A** | **Leave as now:** working ids (space form, 9xxx), mint at the merge turn, re-point and sweep (`lead.md:166–171`). | The lead's `eta.md` table, outside git. | Contiguous by construction; every gap fails (I4). | No hole can occur. | 0 (the standing cost is I4 and I5 on every batch) | — |
| **3B** | **A reservation ledger on a dedicated ref.** | An orphan branch (for example an orphan branch `id-ledger` holding one append-only file: id, prefix, slug, reserved_by, reserved_at, state ∈ reserved / merged / abandoned). `doc-id.py reserve` takes max(main, ledger) + 1, commits, pushes. **Git's atomic ref update is the lock:** a concurrent reserver's push is rejected as non-fast-forward and retries. The ruleset targets main only (M2), so the ref is writable without a bypass. The lead can stay sole allocator by running `reserve` only in the lead's session. | **Accepts a gap only when every number in it is `reserved` or `abandoned` in the ledger at a named ledger commit**, and prints that commit. `docs.yml` already checks out with `fetch-depth: 0` (:45) and would fetch the ref. | An abandoned reservation is a **permanent hole**, recorded `abandoned`, never reused: §1.1's "no number is used twice" holds, and nothing is renumbered, since an abandoned id was never assigned to a governed thing. **`created:` must be the reservation date**, or check 31's "`created` non-decreasing with the number" fails when a lower id merges later. | **2.5** — basis: `reserve` and the ledger read in `next` 1.0; check 31 plus broken-input proofs (a removed record must still red) 0.75; `lead.md`, `document-ids.md` §1.7 and two skills 0.75 | `scripts/doc-id.py`, `scripts/_docid.py`, `scripts/audit-docs.py` (check 31), `.github/workflows/docs.yml`, `docs/process/document-ids.md` §1.7 (RFC + RL), `.claude/roles/lead.md` rule 4, `.claude/skills/doc-id-migration-run`, `git-hygiene` |
| **3C** | **Drop contiguity from check 31; keep uniqueness.** Allocate at creation from the lead's table. | The lead's table, outside git. | No gap check. | Holes are legal, and **a lost record becomes undetectable**, the one thing contiguity detects. The repository accepts that trade elsewhere: `audit-docs.py:455` (*"gaps in the sequence are *legal*: a deleted note retires its number"*) and :3743 (*"gaps in the FR run are not merely legal -- they are what a shared sequence looks like"*). | 0.5 — basis: delete a loop, amend §1.7 / §1.11 | `scripts/audit-docs.py`, `scripts/doc-id.py` (`check`), `document-ids.md` §1.7 / §1.11 |
| **3D** | **Block allocation:** each lane or minter reserves a block (for example 20 ids) in the 3B ledger. | As 3B, one reservation per block. | As 3B, at block level. | Unused tails become `abandoned` at the lane's close: larger and more frequent holes. | 2.5 (as 3B) | as 3B |

**Working ids, the mint step and the sweep under 3B, 3C or 3D:** a new record carries its final
id from its first commit. There is no mint commit, no re-point and no `lead.md:167` sweep.

**Migration for the open drafts (72, M3): new records only.** The backlog drains under the
current mint queue (the triage batches). Bulk-reserving the existing working ids would rewrite
each record's id anyway, the same cost as minting, with no benefit. The ledger starts above the
last batch's minted id.

**What it would have changed today.**
- **#1239 (T2)** would not show check-31 gaps: the numbers between its ids and main's are exactly
  T1's reservations (I4), and 3B accepts them by name.
- **#1233** would have had no re-point commits (2ccfa027, aca34794, 159c0c3c: I5), and the T-batch
  back-cites would cite final ids, not space-form working ids.
- **T1, T2 and T8** could merge in readiness order. Today the order "#1233 → T1 → T2 → T8" is
  fixed by id order (authority 11:10:23).

**Open to extension.** As P2: the separate docs-burden decision (11:40:59, item 4) may add an
allocation option here; this part is not widened for it now.

**Recommendation: 3B.** It keeps contiguity's one real benefit (detecting a lost record) and
removes the merge-order coupling, which answers the 28 Sep objection directly. 3C is the cheap
fallback if the maintainer judges review catches a lost record well enough. **For the ruling to
state:** whether reservation stays with the lead alone (recommended, as today); and the age after
which a `reserved` id is marked `abandoned` (recommended: 5f's 7-day draft age, so the two rules
share one clock).

---

### P4 — shared tables split one file per row

Scope: `docs/findings/register.md` (25 of 73 open PRs, M4) and the roadmap's SL rows
(`docs/roadmap.md`, 20 of 73).

| | Option | Removes | Costs | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|
| **4A** | **Leave as now.** | — | I3's append-adjacent conflicts, and a duplicate-row check after every marker-strip resolution. | 0 | — |
| **4B** | **The register is generated from the FD essay headers.** The FD template gains the register's columns; `register.md` becomes generated (like INDEX under 2D, or committed and regenerated under 2E). | Register append conflicts. Status already lives on the header, so a status change touches one file. | The header field set is closed (§1.5: a family adds fields via its template, with an `RL-`). Legacy register rows that are not FD essays need essays or a frozen legacy table. `register-lint.py` and `doc-index.py`'s register parsing change source. | **3.0** — basis: template + generator 1.0, legacy rows 1.0, lint/audit rewiring and proofs 1.0 | `docs/findings/` template, `register.md`, `scripts/doc-index.py`, `scripts/register-lint.py`, `scripts/audit-docs.py`, `.claude/roles/auditor.md`, `document-ids.md` §1.5 / §1.6 (RFC + RL) |
| **4C** | **Roadmap SL rows one file each**, the roadmap assembled by a generator. | Roadmap append conflicts (#1233 vs #1235, I3). | SL is a **row family** whose host is fixed in `document-ids.md` §1.2; moving it is §1.12's "new row family" lever (RFC + RL) and touches doc-index's row parser, check 33's row resolution and every citation anchor. RFC-937's own layout migration took a multi-week staged run with its own verify instrument. | **4–6** — basis: RFC-937's migration as the precedent, scaled to one family | `docs/roadmap.md`, `scripts/doc-index.py`, `scripts/audit-docs.py` (checks 32, 33, 39), `scripts/doc-id.py`, `document-ids.md` §1.2 / §1.12, the `phase-review` and `close-workstream` skills |
| **4D** | **A local union driver** (`merge=union`) for register and roadmap. | Local resolution work. | GitHub ignores it (as 2B). On an *edit* of a shared row, union keeps both versions: the duplicate-row trap. **Unsafe for living rows.** | 0.25 | `.gitattributes` |

**What it would have changed today.** 4B: the T1 / #1239 register overlap and #1239's early
register push would be non-events, and #1233 ← 2b83e089's register hunk would vanish. 4C: the
#1233 / #1235 roadmap adjacency would vanish.

**Recommendation: defer P4; re-measure 14 days after P2, P3 and P5 land.** With INDEX out of drafts,
mints gone and records batched by subject, most remaining register and roadmap hunks come from
the batches themselves; measure the remaining conflict rate (the M4 command, per path) first. If
it stays material, **4B before 4C**: 4B uses a header the FD family already has and moves no row
family's host. Do not take 4D.

---

### P5 — batching, the cap, the cleanup and drafts without PRs: standing rules RECORDED

**These rules are already in force by the maintainer's rulings and the user's approvals; this
part records them and does not re-propose them** (the maintainer's ask (a), `to-lead.md`
"## 2026-10-08 11:35:05 BST — The RFC 9479 options memo noted (sent seconds before this entry);
two asks for the RFC"). They live in the channel only; no governed document carries them (M13).
Writing them into `lead.md` and `delivery-process.md` §8 is the ruling's to order, and each
charter line it touches is the maintainer's, behind an `FD-` first (`document-ids.md` :168:
*"a role file that proves insufficient" → `FD-` → maintainer amends*).

| | Rule in force | Source (`to-lead.md` entry header, verbatim) |
|---|---|---|
| **5a** | **Batching.** Mint PRs carry batches (R1: the batch body lists every record, working id → minted id, its source PR and its normalised-diff result), at most 10 ids (above 10 needs the maintainer's prior OK), ordered by dependency layer (cited before citing); a back-cite into a later batch stays a space-form working id and is listed in the PR body. Only ONE register-touching minter runs at a time, paired with a roadmap-only batch. | "## 2026-10-08 10:38:11 BST — OPEN-PR BURN-DOWN PLAN for the new lead: 79 → under 30 by Fri 9 Oct, falling every day" (method 2–3); "## 2026-10-08 10:53:25 BST — Re-triage accepted; the five asks RULED; and the user's reminder: CLEAN UP UNUSED PRs as the work goes" (items 1, 2 and the register risk); "## 2026-10-06 01:18:08 BST — Backlog triage: R1 and R2 RULED" (R1); earlier, "## 2026-10-05 13:13:32 BST — PL 9716 noted; batching UNRELATED findings ≤3 per mint PR: APPROVED (a widening of my 10:47:03 rule); cite fix", since widened by the 10-id ceiling |
| **5b** | **The under-30 cap on ALL open PRs**, a standing control, not a dated goal. While at or over 30, a new governed record rides a same-subject PR or the next batch; slice and activation PRs are exempt. Targets: at most 55 by the end of 8 Oct, under 30 by the end of 9 Oct, falling every day. | "## 2026-10-06 01:01:08 BST — STANDING TARGET from the user: TOTAL open PRs under 30, as a control, not just a 9 Oct goal"; "## 2026-10-08 10:38:11 BST — OPEN-PR BURN-DOWN PLAN …" (targets) |
| **5c** | **Cleanup during the work:** a batch's absorbed siblings close at once after its verified read-back, without a separate OK each, when each sibling's normalised diff against the batch copy is empty apart from id re-points and the INDEX and register regeneration (R2); a draft found superseded, absorbed or obsolete closes at once, naming its carrier; merged branches and worktrees go; every status carries the open count and the closes since the last. **Branch cleanup** follows once open PRs are under 30, by one auditor, dry-run table first, every deleted tip recorded and pinned under `refs/salvage/`. | "## 2026-10-06 01:18:08 BST — Backlog triage: R1 and R2 RULED" (R2); "## 2026-10-08 10:53:25 BST — Re-triage accepted; … CLEAN UP UNUSED PRs as the work goes" ((a)–(d)); "## 2026-10-08 11:16:32 BST — USER: after the open-PR burn-down, CLEAN UP UNUSED BRANCHES too; the procedure, queued (not to run before the PR count is under 30)" |
| **5d** | **A new governed-record draft gets NO PR** (FD, RL, PL, OQ, RFC, CR). It is committed on its own branch `draft/<family>-<working id>` from current main and pushed; reviews cite `draft/<family>-<wid> @ <full sha>`; the lead keeps a draft register in `eta.md`; at mint the minter builds ONE batch PR from current main. Exempt: slice PRs, activation PRs, security and dependency fixes, and this RFC's PR. Existing draft PRs are not converted. | "## 2026-10-08 11:37:20 BST — USER-APPROVED, EFFECTIVE NOW: a new governed-record draft gets NO PR; PRs are opened only as mint BATCHES (and for slices, activations and urgent fixes)" |
| **5e** | **Merge main, never rebase**, into a branch behind main, then regenerate INDEX in a new commit; each PR regenerates INDEX in its final commit only. | "## 2026-09-28 11:19:17 BST · [the maintainer's (by delegation)] · HOLD LIFTED — the maintainer's instruction: complete the five started-but-open Phase 2 Works, in FOUR PARALLEL TRACKS, under the delivery process; spawn teammates from their role files" *[elided: the header names the delegate by the word our records bar; quoted with that word replaced]*, rule 2 |
| **5h** | **Remote CI is not a gate.** Minters push and run CI while gate-1 is held; only their local batch checks wait for the slot. | "## 2026-10-08 11:10:23 BST — T2 draft and T8 noted; the register slip accepted as harmless; PRIORITY NOW: MERGE THROUGHPUT, because the count has RISEN to 81" |

**5d's cost and effect** (the user's approval asks for both):
- **Cost: more branches.** One `draft/<family>-<wid>` branch per record, pushed for durability,
  instead of one PR. They are deleted after their batch's verified read-back, tip shas recorded
  (the 11:37:20 entry, item 3), and the stragglers fall to 5c's branch cleanup. The baseline that cleanup starts
  from: 111 remote heads, 660 local branches and 60 `refs/salvage` refs (the 11:16:32 entry,
  counted by the lead). Reviews lose GitHub's PR view of a draft; the review anchor becomes the
  branch and sha.
- **Effect: open PRs ≈ active slices + their activations + open batches**, about 5 to 15, instead
  of one per record (73 at 11:35:54, M3, 72 of them drafts). Pairwise conflicts scale with the
  square of the open count, so the I2 and I3 conflicts between *drafts* stop at the source; what
  remains is batch against batch and batch against slice, which P1–P4 address.
- **The role-file lines it changes later** (the maintainer's, via an `FD-` first). No role file
  says "open a draft PR" (`git grep -n -iE 'draft PR|--draft' -- .claude docs/process` → 0 hits
  at this tree); the lines that assume **one PR per record** are:
  `.claude/roles/decision-maker.md:40–42` (*"every ruling and every spec change lands as a PR
  reported by number and left for the lead to merge"*); `.claude/roles/executor.md:25` and
  `:144` (*"pushes and opens every PR"*); `.claude/roles/auditor.md:15–18` (*"every correction
  PR this role opens … every PR opened this session"*); and `.claude/roles/lead.md:166–170` (the
  mint queue: *"a PR mints at its turn"*, and the post-mint sweep over *"open PRs"*, which must
  also cover the `draft/` branches). Predicate: `git grep -n -iE '\bPR\b' -- .claude/roles`,
  read for per-record wording.

**Proposed, not in force** (for the ruling):
- **5f — a 7-day draft age limit:** a draft (PR or `draft/` branch) older than 7 days is closed
  or deleted (its reservation `abandoned` under 3B) or carried by the lead with a dated reason;
  the lead's progress line carries the count. Basis: 8 open PRs predate 2026-10-01 (M3).
  ESTIMATE 0.25 (one `lead.md` paragraph).
- **5g — merge main daily into a branch with code; into a docs-only branch at its merge turn
  only.** A daily merge keeps code conflicts small but costs a CI run and voids the ACK tree;
  docs-only conflicts are the generated and table hunks P2–P4 address, and 1E carries a clean
  ACK across a move. ESTIMATE 0.25 (`git-hygiene`, `delivery-process.md` §8).

**What it would have changed today.** 5a's one-register-minter rule, had it been in force
earlier, rules out T1 and #1239 both open on `register.md`, so no early register push. 5d: the 60
draft PRs opened on 5 Oct (M3) would have been 60 branches and a handful of batch PRs. 5f: the 8
PRs opened before 1 Oct would be closed or carried with reasons. 5g with 1E: #1233's five 6 Oct
merges of main collapse to the ones its merge turn needed.

**Recommendation: record 5a–5e and 5h in `lead.md` and `delivery-process.md` §8 as written (the ruling
orders it, an `FD-` first for each charter line); adopt 5f and 5g.** About 1.0 executor-day in
total (ESTIMATE: five recorded rules and two new ones, a paragraph each, plus the `FD-`).

---

## Sequence

The authority's order was *"P1+P2 first (mostly configuration, immediate relief), then P3, then
P4"*. **Corrected: P1 cannot lead** (the queue is unavailable, M5) **and depends on P2 anyway**.
The memo's no-transfer order was P5 + 1E, then 2B as a stop-gap, then 2D, 3B, P4 after
measurement and 1B last; this RFC keeps it **except 2B** (see P2's recommendation). The order
that relieves today's conflicts soonest, with no transfer:

1. **Now, rules only (about 1.4 executor-days, ESTIMATE):** **1E** (no re-CI for a clean,
   path-disjoint main move), **5a–5e recorded** in `lead.md` and `delivery-process.md` §8 (with
   **2E** as one sentence of 5d), and **5f, 5g** adopted. No script changes. 5d already removes
   the draft-to-draft conflicts at the source; 1E removes the I1 re-CI for disjoint moves.
2. **First build: 2D (about 2.0), then 3B (about 2.5).** Each with its §13 broken-input proof: a
   deleted `REDIRECTS.csv` must flip every sentinel caller under 2D; a deliberately removed record
   must still red check 31 under 3B.
3. **The user's decision: 1B** (transfer plus queue, about 2.0 plus the user's own work), offered
   after 2D has landed and 1E has run 14 days.
4. **Measured, not scheduled: P4** after 14 days at the new rate; 4B before 4C.

Total if everything recommended is taken: **about 8 executor-days** (ESTIMATE: 1E 0.25 + 2E 0.1
+ P5 1.0 + 2D 2.0 + 3B 2.5 + 1B 2.0 = 7.85), plus P4 only if the measurement calls for it.

## For the maintainer's ruling (then the user's, for P1)

1. **P1:** 1A + 1E now, 1B deferred to the user (recommended) — or 1B now, or 1C / 1D.
2. **P2:** 2D as the build, 2E inside 5d (recommended) — or 2B, 2C, or 2A. Contracts unchanged.
3. **P3:** 3B (recommended) or 3C or 3D or 3A; plus who reserves (the lead alone, recommended) and
   the abandonment age (7 days, recommended, shared with 5f).
4. **P4:** defer and re-measure in 14 days (recommended), or 4B now.
5. **P5:** order 5a–5e and 5h written into `lead.md` and `delivery-process.md` §8, an `FD-` first for each
   charter line (they are in force already; the ruling only orders the record); adopt 5f and 5g,
   or not.
6. **The sequence** in the Sequence section.

**After the ruling, P1 is the user's decision**: whether to transfer `yes-404/gi-pricing-plan`
to a free organisation and enable the queue. This RFC changes no script, workflow, ruleset or
code.

## Where this RFC departs from its input memo

- **The merge procedure is `lead.md` rule 4, not `delivery-process.md` §15** (M14). The memo's
  file lists named §15 for 1B, 1D and 1E; this RFC names rule 4, and §8 for P5.
- **M3 / M4 re-measured** at 11:35:54 BST: 73 open, 72 drafts, 72 touching INDEX, 25 register, 20
  roadmap (the memo, at its time: 81, 78, 80, 27, 24). No PR is at the 100-file cap, so the counts
  are exact, not floors.
- **1E is already practice once** (#1238, Problem), and rule 4 already permits it (M10).
- **P5 records rules in force** (the maintainer's ask (a)) rather than proposing them, and adds
  5d, the no-PR draft rule of 11:37:20, which post-dates the memo.
- **2E is new and 2B is not recommended**: 5d delivers the draft-side relief 2B was a stop-gap
  for.
- **2D's sentinel**: `REDIRECTS.csv` alone, with every caller named (the memo left it open).
- **1B's estimate** follows the memo's revised 2.0, not its first 1.5.

## Sources

**Kept current until this RFC merges** (the user's instruction, `to-lead.md` "## 2026-10-08
11:40:59 BST — USER INSTRUCTION: RFC 9479 is kept current with every new rule until it merges"):
every rule the maintainer logs on PR creation, batching, merging, ids, generated files or cleanup
is folded in the same day and listed here. **Every `to-lead.md` entry from 10:38:11 BST on 8 Oct
is listed**, carried or left out with a reason, plus the earlier entries the RFC rests on.
Headers are verbatim, except the one elided where marked.

| `to-lead.md` entry header (verbatim) | Carried in | Or left out, because |
|---|---|---|
| ## 2026-09-28 11:19:17 BST · [the maintainer's (by delegation)] · HOLD LIFTED — the maintainer's instruction: complete the five started-but-open Phase 2 Works, in FOUR PARALLEL TRACKS, under the delivery process; spawn teammates from their role files *[elided: the barred word replaced]* | P5 5e (rule 2: merge main, never rebase; INDEX in the final commit) | — |
| ## 2026-09-28 11:23:26 BST · [the maintainer's (by delegation)] · ids are MINTED AT MERGE-READINESS, not reserved: first ready, first merged. This supersedes the fixed table of 11:22:08/11:22:42, whose RL[-]1171 would hold the CR chain behind Track D *[elided: the barred word replaced; the hyphen of a never-minted working id bracketed so check 32 does not read it as a citation]* | M9; P3 (the objection); P2 2E | — |
| ## 2026-10-05 13:13:32 BST — PL 9716 noted; batching UNRELATED findings ≤3 per mint PR: APPROVED (a widening of my 10:47:03 rule); cite fix | P5 5a (history: superseded by R1) | — |
| ## 2026-10-06 01:01:08 BST — STANDING TARGET from the user: TOTAL open PRs under 30, as a control, not just a 9 Oct goal | P5 5b | — |
| ## 2026-10-06 01:18:08 BST — Backlog triage: R1 and R2 RULED | P5 5a (R1: batch size and the batch body's record table), 5c (R2: absorbed siblings close after the verified read-back, on an empty normalised diff) | — |
| ## 2026-10-06 01:59:10 BST — B2+B3 as ONE batch (6 PRs, 9 records): OK; ids must follow MERGE order (SL-1430's ledger) | P3 (the problem: *"keep the id order equal to the merge order"*) | — |
| ## 2026-10-08 10:38:11 BST — OPEN-PR BURN-DOWN PLAN for the new lead: 79 → under 30 by Fri 9 Oct, falling every day | P5 5a, 5b | — |
| ## 2026-10-08 10:40:28 BST — NEW LEAD (fresh, started by the user) CONNECTED: transcript 75950401, Opus, PID 4478 | — | a seat record; no rule on these subjects |
| ## 2026-10-08 10:43:28 BST — New lead's read-in ACCEPTED; MERGE-ACK #1235 (lane A activation, PL-1447 / SL-1448) @64e25a2ddb8b176ed0d547156a9da4fcd326147d | Problem (I1: the main move #1233 merged) | an ACK, no new rule |
| ## 2026-10-08 10:44:31 BST — #1235 read-back verified; the USER's operating mode: PARALLELISE to the caps | — | capacity and lane caps (members, build lanes, one gate), not PRs, ids or merging |
| ## 2026-10-08 10:48:03 BST — SECURITY: Dependabot alert #13, source-map-js (GHSA-68fv-2mgg-jv7q, HIGH, event-loop DoS via indexed source-map section offsets): investigated; FIX by a lockfile-only refresh, ONE small PR, now | P5 5d (security fixes exempt from the no-PR rule); Problem (#1237, the lockfile-only move) | — |
| ## 2026-10-08 10:51:33 BST — T1 batch noted; FD 9489's disposition DECIDED now (option (a)), so #1221 stays in T1; FD 9480's check is right | P2 (FD 9489: INDEX keeps one row per OQ number; a `doc-index.py` fix that 2D carries unchanged); Problem (I4: T1's ids) | — |
| ## 2026-10-08 10:53:25 BST — Re-triage accepted; the five asks RULED; and the user's reminder: CLEAN UP UNUSED PRs as the work goes | P5 5a (10-id ceiling, cited-first, forward-cites listed, one register minter), 5c (cleanup (a)–(d)) | — |
| ## 2026-10-08 10:54:33 BST — LANE B: [R]uling 1 = (b'), else (c); [R]uling 2 = (iii'); DISPATCH GO (conditional) for WK-673 Slice 3 (PL-1452 / SL-1387) | — | a slice dispatch; no rule on these subjects |
| ## 2026-10-08 10:55:30 BST — MERGE-ACK #1237 (security, source-map-js 1.2.1 → 1.2.2) @bf511269898baecf938b3fe37e6cb46f382b289b; LANE C DISPATCH GO (conditional) for WK-675 S2 (PL-1476 / SL-1477) | Problem (I1: the lockfile-only move); P1 1E | an ACK and a dispatch, no new rule |
| ## 2026-10-08 11:05:02 BST — SL-1448 gate noted; its red-first ORDER deviations accepted as disclosed (written seconds AFTER the message, my slip) | Problem (#1233 merges main c0aab813 before its ACK) | a slice's TDD order; no rule on these subjects |
| ## 2026-10-08 11:10:23 BST — T2 draft and T8 noted; the register slip accepted as harmless; PRIORITY NOW: MERGE THROUGHPUT, because the count has RISEN to 81 | Problem (I3, I6); P3 (the order fixed by ids); P5 5h (remote CI is not a gate) | — |
| ## 2026-10-08 11:16:32 BST — USER: after the open-PR burn-down, CLEAN UP UNUSED BRANCHES too; the procedure, queued (not to run before the PR count is under 30) | P5 5c, and 5d's cost | — |
| ## 2026-10-08 11:26:43 BST — USER-APPROVED: raise ONE proposal (an RFC, WK-1178) on "merging safely in parallel": merge queue, generated files, id allocation, per-row tables, batching | the whole RFC (authority) | — |
| ## 2026-10-08 11:27:49 BST — RFC 9479 addition for P1: the repo is USER-owned; the merge queue may be unavailable | M1, P1 | — |
| ## 2026-10-08 11:28:36 BST — #1238 (lane B activation) PRE-VERIFIED; the bracketed-letter elision ACCEPTED; the ACK follows on the tree recomputed after #1233 | Problem (the counter-example); P1 1E | the elision form is a quoting rule for the roadmap, not on these subjects |
| ## 2026-10-08 11:30:48 BST — The USER confirmed: "Require merge queue" is NOT offered in the ruleset editor (user-owned repo) | M5, P1 | — |
| ## 2026-10-08 11:31:37 BST — MERGE-ACK #1233 (B2+B3: FD-1469 … SL-1477, plus the FD-1421/1425/1433 closes) @96bcdb0e345d2e1c213ced65dc868cee3e23e1d3 | Problem (I1, I5) | an ACK, no new rule |
| ## 2026-10-08 11:32:55 BST — #1233 read-back verified; MERGE-ACK #1238 (lane B activation) @98d15659b574f5d987826adad2fe4cafc1a0cfeb on the recomputed tree | M10 (the expected tree as practice); Problem; P1 1E; P5 5a (#1233's six siblings closed) | — |
| ## 2026-10-08 11:35:05 BST — The RFC 9479 options memo noted (sent seconds before this entry); two asks for the RFC | P5 (records, not proposes); P2 (the 2D replacement table) | — |
| ## 2026-10-08 11:37:20 BST — USER-APPROVED, EFFECTIVE NOW: a new governed-record draft gets NO PR; PRs are opened only as mint BATCHES (and for slices, activations and urgent fixes) | P5 5d; P2 2E | — |
| ## 2026-10-08 11:40:59 BST — USER INSTRUCTION: RFC 9479 is kept current with every new rule until it merges | Sources; P2 and P3 (open to extension) | — |

## Deliverable

The `deliverable:` and `lands_in:` fields in prose: **a ruled choice for each of P1 to P5 and a
sequence**, by the maintainer's `RL-`, and then the user's decision on P1. Nothing ships in this
RFC's PR. Each part the ruling takes is cut into its own Work or Slice under WK-1178 by the
planner (§1.6, *"planner cuts an active RFC into a Work"*): rule text in `lead.md` rule 4 and
`delivery-process.md` §8 (1E, P5, behind an `FD-` for each charter line), the 2D and 3B builds in
`scripts/` with their broken-input proofs, and, if the user transfers the repository, 1B's
workflow prerequisites and ruleset.

## Acceptance

None in this file. The maintainer rules by an `RL-` that cites this RFC by its minted id, and the
user decides P1 after it. Until then nothing here binds.
