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
and `## 2026-10-08 11:30:48 BST — The USER confirmed: "Require merge queue" is NOT offered in the ruleset editor (user-owned repo)`.
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

## 0. Measurements at this RFC's tree

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
| M13 | **No governed document carries the under-30 open-PR cap, the mint-batch size or the "never a rebase" merge rule.** They live in the channel and in memory only. | `git grep -n -iE 'under 30\|open-PR cap\|30 open\|never a rebase' -- .claude/roles/lead.md docs/process/delivery-process.md .claude/skills/git-hygiene` → 0 hits |
| M14 | The merge procedure is **`lead.md` rule 4**. `delivery-process.md` has no merge-procedure section: its §15 is "Correction and message discipline", and parallelism is §8. | `grep -n '^## ' docs/process/delivery-process.md` |

## 1. The problem, and today's incidents

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

---

## P1 — a merge queue, or its substitute

**Status.** Case (b): the queue is unavailable as the repository is owned (M1, M5).

| | Option | What it takes | Trade-offs | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|
| **1A** | **Skip P1.** Keep the serial ACK, `merge-tree` and `--match-head-commit`: a hand-run queue of size 1. | nothing | No transfer risk. Merges stay serial, behind the lead. | 0 | — |
| **1B** | **Transfer the repository to a free GitHub organisation, then enable the queue.** | **The user's decision and action.** After the transfer, the prerequisites come **first**, in this order: **(i)** a `merge_group:` trigger on all four workflows; **(ii)** one always-reporting aggregator job per path-filtered workflow, because `paths:` does not apply to `merge_group` and a required check that never reports stalls the queue (a `git diff --name-only` step, not a third-party action, which `docs.yml`'s header refuses); `history-policy` gets a `merge_group` range (`merge_group.base_sha..merge_group.head_sha`), or it scans only the tip; **(iii)** only then the ruleset's required-checks rule and "Require merge queue" with squash. | **Moves with the transfer:** history (every SHA and PR number unchanged, so every ledger, ACK and citation stays valid), issues, PRs, rulesets, secrets, webhooks, deploy keys. **Changes:** the URL (GitHub redirects it, including git remotes, until someone recreates `yes-404/gi-pricing-plan`; update the remotes anyway); **the fine-grained PAT must be re-issued with the organisation as resource owner** (until then every `gh` call fails, a hard stop for the merge procedure, so the transfer needs a quiet window); Actions and Dependabot settings re-checked at organisation level. 54 lines in 20 files mention `yes-404` (`git grep -c yes-404 HEAD -- . ':!docs/INDEX.md'`); `lead.md:41–44`'s `author.login` rule still holds, since a transfer does not change PR authorship. **Once on:** the REST merge cannot enqueue, so the merge becomes `gh pr merge --auto` or GraphQL `enqueuePullRequest`; the ACK keeps the head SHA but cannot name the expected tree (GitHub builds it from main plus the PRs ahead); the read-back compares the new main's tree with the tree the `merge_group` run tested; an ejection is the new re-request. **Worthless before P2:** the queue's build is a plain merge, so an INDEX conflict ejects the PR (72 of 73 open PRs, M4). | **2.0** — basis: (i)+(ii) 1.0 (four workflow files, an aggregator each, a broken-input proof that a filtered-out workflow still reports); ruleset, `lead.md` rule 4 and `git-hygiene` 0.5; a dry run on three docs PRs 0.5. The user's transfer, PAT and settings work comes on top. | `.github/workflows/{docs,python,frontend,history-policy}.yml`; the ruleset (a setting); `.claude/roles/lead.md` rule 4; `.claude/skills/git-hygiene`; CLAUDE.md §2's CI sentence (the maintainer's) |
| **1C** | Required status checks with "require branches to be up to date", on the personal repository (no queue). | A ruleset edit and the aggregators of 1B (ii). | Enforces CI on a head that contains current main: what the lead does by hand now. It **adds** re-CI rather than removing it. No parallelism. | 1.0 — basis: 1B (ii) alone | as 1B (i)–(ii); the ruleset |
| **1D** | A hand-built merge train: N PRs into one integration branch, one CI run, then ordered squashes. | A new script and procedure. | Each squash still moves main under the next PR, so the per-PR ACK tree must be recomputed for the train. More procedure and more ways to fail than a queue. | 1.5–2.0 — basis: a new script plus its tests, plus `lead.md` | `lead.md` rule 4, a new script |
| **1E** | **No transfer: an ACK carries over a main move when the merge is mechanically clean.** When main moves, the lead recomputes `git merge-tree` of the ACKed head on the new main. If it exits 0 **and** the commits that moved main touch **none of the PR's paths**, the lead runs the docs checks (audit-docs, `doc-index.py --check`, `register-lint.py`) on that recomputed tree and re-ACKs naming it, **without merging main into the branch and without a new branch CI run**. Full CI then runs on main's push as the backstop; a red main is fixed forward before any other merge. | A `lead.md` rule 4 amendment (the maintainer's) and nothing else. | **Removes the per-move re-CI, the largest cost in I1**, with no transfer. It moves pytest detection from before the merge to after it: `python.yml` triggers on `docs/**` because tests assert on docs content, so a docs PR that breaks one reaches main red. **Bounds:** only PRs whose paths are all under `docs/` (71 of 73 today, M4); never while main is red. It is already practice once: #1238 (§1). | **0.25** — basis: one rule paragraph in `lead.md` and its read-back line | `.claude/roles/lead.md` rule 4 |

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

## P2 — generated files out of manual merges

Scope: `docs/INDEX.md` (generated, committed, read by check 31 and by `doc-id next`: M7, M8)
and `docs/contracts/openapi/generated.json` (generated, committed, a published spec artifact:
M12).

| | Option | Trade-offs | The `--check` gate, and CLAUDE.md §13 | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|
| **2A** | **Leave as now.** Every PR regenerates INDEX; a PR behind main merges main and regenerates again. | Works serially. It is the I2 cost on 72 of 73 PRs, and it blocks any queue. | `doc-index.py --check` proves freshness only. | 0 | — |
| **2B** | **A local git merge driver** (`.gitattributes`: `docs/INDEX.md merge=…`) that keeps one side, followed by a regeneration. | **GitHub's server-side mergeability, its merge and any queue never run custom drivers**, so the PR still shows conflicting until someone merges main locally. A driver sees one file, not the merged tree, so it cannot regenerate INDEX by itself (M11). Its command lives in each clone's `git config`. | unchanged | 0.25 — basis: a driver script and a skill line | `.gitattributes` (new), a driver under `scripts/`, `git-hygiene` |
| **2C** | **PRs stop committing INDEX; a post-merge CI job regenerates and commits it to main.** | **Blocked by the ruleset** (M2: no bypass actors): a bot cannot push to main without a bypass and `contents: write`, which reverses every workflow's least privilege. Between merge and bot commit, main's INDEX is stale, and `doc-id next` and check 31 read a stale allocation. | `--check` on main flickers red then green after each merge. | 1.5, plus a ruleset change by the user — basis: a workflow job, a GitHub App bypass, the stale-window handling | `docs.yml`, the ruleset, `doc-id.py`, `audit-docs.py` |
| **2D** | **INDEX becomes a build output.** Not committed; every consumer (`doc-id next`, check 31, check 32) calls the `doc-index` generator in memory; CI publishes INDEX as an artifact. `migrated_tree()` gets a sentinel that does not need INDEX (`docs/REDIRECTS.csv` alone, or a constant now the migration is done); check 39 retires. | **Removes the most frequent conflict entirely**, with or without a queue, and makes 1B viable. Costs an amendment to the id standard (INDEX is RFC-937's one-row-per-id artifact and check 39's subject; `document-ids.md`'s owner line: *"amendments arrive as an RFC- + RL- pair"*). Readers on GitHub lose a rendered INDEX unless CI publishes one. **The sentinel also selects `docs.yml`'s `--ref` (M7): that line is the risky one**, and needs its broken-input proof. | The freshness check disappears, which §13 supports: *"a generated artifact matching its source proves neither correct"*. Correctness stays with `doc-index.py`'s own tests. | **2.0** — basis: the readers in `doc-id.py` and `audit-docs.py` 1.0; sentinel, `docs.yml` and the broken-input proofs 0.5; the standard's amendment and two skills 0.5 | `scripts/doc-id.py`, `scripts/audit-docs.py` (checks 31, 32, 39, `migrated_tree`), `scripts/doc-index.py`, `.github/workflows/docs.yml`, `.gitignore`, `docs/process/document-ids.md` §1.4 / §1.11 (RFC + RL), CLAUDE.md §4's pointer, `.claude/skills/docs-audit`, `.claude/skills/doc-id-migration-run` |
| **2E** | **No code: INDEX is regenerated only at the merge turn.** A draft PR carries no INDEX hunk; the regeneration is part of the mint commit, which already regenerates INDEX (M9's 28 Sep rule, step 2: *"file name, front matter, internal references, INDEX regenerated"*). | Drafts stop conflicting with each other and with main on INDEX; only the PR at its merge turn touches it, so there is one INDEX hunk open at a time. A draft then shows `doc-index.py --check` red (check 39), **the same class of expected red as check 31's working-id row**, which drafts already carry (I4). **Check 32 resolves every prose citation in INDEX** (`audit-docs.py:1946`), so a draft also reds check 32 on each citation of its own new ids; a writer checks locally on a regenerated, uncommitted INDEX. The draft's docs CI stays red until its merge turn, as check 31 already makes it. | unchanged at the merge turn, where the check runs | **0.25** — basis: one rule in `lead.md` rule 4 and `delivery-process.md` §8, and a list of expected draft reds | `.claude/roles/lead.md` rule 4, `docs/process/delivery-process.md` §8 |

**`generated.json`, separately: leave it as now.** 0 of 73 open PRs touch it (M4); the one
recorded conflict auto-merged to the generator's output (I2, SL-1430's mint); CLAUDE.md §2 binds
it as committed, and changing that is the maintainer's amendment with nothing measured to justify
it. Under 1B its `--check` must run in `merge_group`, because two API PRs can each pass alone and
drift together; that is the one place a queue adds safety a merge-time check cannot.

**What "committed, published artifact" (CLAUDE.md §2) then means.** Unchanged: it is
`docs/contracts/` only. INDEX was never under that sentence (M12), so 2D amends the id standard,
not CLAUDE.md §2.

**What it would have changed today.**
- **2D or 2E:** 72 of 73 open PRs lose their INDEX hunk. #1233's merges of main on 6 Oct would
  each have had one conflict fewer (841485a3 vs f871ee8d; ← 2b83e089); SL-1430's mint ← 8bc01ae8
  would have had none. #1235 and #1238 would each have had no INDEX change to carry across a move.
- **2B:** the same local resolutions become mechanical, but GitHub still shows the PR
  conflicting until the local merge, so no re-CI is saved.

**Recommendation: 2E now, 2D as the build.** 2E is a rule, gives most of 2D's relief to drafts at
once, and needs no amendment of the id standard; 2D then removes the last INDEX hunk (the merge
turn's) and makes a queue possible. Take 2B only if neither is ruled; it removes manual work and
none of the re-CI. Contracts as now.

---

## P3 — ids allocated at creation

**The objection P3 must answer (M9).** A reservation table was tried on 28 Sep and withdrawn the
same morning: under check 31's contiguity, whichever record holds the lower id holds every higher
one behind it. Allocation at creation works **only if check 31 can tell a reserved-but-unmerged
gap from a lost record.**

| | Option | Ledger: where, who writes, collisions | Check 31 | Permanence (CLAUDE.md §5) and abandoned ids | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|---|
| **3A** | **Leave as now:** working ids (space form, 9xxx), mint at the merge turn, re-point and sweep (`lead.md:166–171`). | The lead's `eta.md` table, outside git. | Contiguous by construction; every gap fails (I4). | No hole can occur. | 0 (the standing cost is I4 and I5 on every batch) | — |
| **3B** | **A reservation ledger on a dedicated ref** (for example an orphan branch `id-ledger` holding one append-only file: id, prefix, slug, reserved_by, reserved_at, state ∈ reserved / merged / abandoned). `doc-id.py reserve` takes max(main, ledger) + 1, commits, pushes. **Git's atomic ref update is the lock:** a concurrent reserver's push is rejected as non-fast-forward and retries. The ruleset targets main only (M2), so the ref is writable without a bypass. The lead can stay sole allocator by running `reserve` only in the lead's session. | **Accepts a gap only when every number in it is `reserved` or `abandoned` in the ledger at a named ledger commit**, and prints that commit. `docs.yml` already checks out with `fetch-depth: 0` (:45) and would fetch the ref. | An abandoned reservation is a **permanent hole**, recorded `abandoned`, never reused: §1.1's "no number is used twice" holds, and nothing is renumbered, since an abandoned id was never assigned to a governed thing. **`created:` must be the reservation date**, or check 31's "`created` non-decreasing with the number" fails when a lower id merges later. | **2.5** — basis: `reserve` and the ledger read in `next` 1.0; check 31 plus broken-input proofs (a removed record must still red) 0.75; `lead.md`, `document-ids.md` §1.7 and two skills 0.75 | `scripts/doc-id.py`, `scripts/_docid.py`, `scripts/audit-docs.py` (check 31), `.github/workflows/docs.yml`, `docs/process/document-ids.md` §1.7 (RFC + RL), `.claude/roles/lead.md` rule 4, `.claude/skills/doc-id-migration-run`, `git-hygiene` |
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

**Recommendation: 3B.** It keeps contiguity's one real benefit (detecting a lost record) and
removes the merge-order coupling, which answers the 28 Sep objection directly. 3C is the cheap
fallback if the maintainer judges review catches a lost record well enough. **For the ruling to
state:** whether reservation stays with the lead alone (recommended, as today); and the age after
which a `reserved` id is marked `abandoned` (recommended: P5's 7-day draft age, so the two rules
share one clock).

---

## P4 — shared tables split one file per row

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

## P5 — batching and age limits as standing rules

None of these is written in a governed document today (M13). Each is a rule, not machinery.

| | Rule | Today's basis | Trade-off | Cost (ESTIMATE) | Files |
|---|---|---|---|---|---|
| **5a** | **Records batched by subject or by day**: one PR per mint batch, or per day per writer. **Two open PRs that write the same shared file (register, roadmap, open-questions) are never both open for merge at once**; the second waits. | Practice (T1, T2, T8; #1233 closed six source PRs at its merge, authority 11:32:55). | Bigger PRs, fewer pairs: conflicts scale with pairs of open PRs. | 0.25 | `delivery-process.md` §8, `lead.md` rule 4 |
| **5b** | **The under-30 open-PR cap** (the user, 6 Oct), with the cap-exempt classes named: activation, security, process proposal. | 73 open (M3); in memory and channel only. | Reaching it needs the backlog drain; under 3A each batch waits on id order, under 3B batches drain in parallel. | 0.25 | `lead.md`, `delivery-process.md` §8 |
| **5c** | **A 7-day draft age limit**: a draft older than 7 days is closed (its reservation `abandoned` under 3B) or carried by the lead with a dated reason. The lead's progress line carries the count. | 8 open PRs predate 2026-10-01 (M3). | An age rule without an owner is noise; the lead owns it. | 0.25 | `lead.md`, `delivery-process.md` §8 |
| **5d** | **Merge main, never rebase, into a long-lived branch: daily for branches with code; at the merge turn only for docs-only PRs.** | "never a rebase; it voids ledger SHAs" (28 Sep, channel only, M13). | A daily merge keeps code conflicts small, but each costs a CI run and voids the ACK tree; docs-only conflicts are the generated and table hunks P2–P4 address, and 1E carries a clean ACK over a move. | 0.25 | `git-hygiene`, `delivery-process.md` §8 |

**What it would have changed today.** 5a: T1 and #1239 both open on `register.md` would have
been ruled out, so no early register push. 5c: the 8 PRs opened before 1 Oct would already be
closed or carried with reasons. 5d with 1E: #1233's five 6 Oct merges of main collapse to the
ones its merge turn needed.

**Recommendation: adopt 5a–5d now**, as one process amendment to `delivery-process.md` §8 and
`lead.md` rule 4. They are the maintainer's process documents, so they need the ruling's `RL-`.
About one executor-day in total (ESTIMATE: four rule paragraphs and their read-back lines).

---

## 6. Sequence

The authority's order was *"P1+P2 first (mostly configuration, immediate relief), then P3, then
P4"*. **Corrected: P1 cannot lead** (the queue is unavailable, M5) **and depends on P2 anyway**.
The order that relieves today's conflicts soonest, with no transfer:

1. **Now, rules only (about 1.5 executor-days, ESTIMATE):** **1E** (no re-CI for a clean,
   path-disjoint main move), **2E** (no INDEX hunk in drafts), **5a–5d**. All are `lead.md` and
   `delivery-process.md` text; no script changes. Together they remove the I1 re-CI for
   disjoint moves and the I2 conflict from 72 of 73 drafts.
2. **First build: 2D (about 2.0), then 3B (about 2.5).** Each with its §13 broken-input proof: a
   stale `migrated_tree()` sentinel must red under 2D; a deliberately removed record must still
   red check 31 under 3B.
3. **The user's decision: 1B** (transfer plus queue, about 2.0 plus the user's own work), offered
   after 2D has landed and 1E has run 14 days.
4. **Measured, not scheduled: P4** after 14 days at the new rate; 4B before 4C.

Total if everything recommended is taken: **about 8 executor-days** (ESTIMATE: 1E 0.25 + 2E 0.25
+ 5a–5d 1.0 + 2D 2.0 + 3B 2.5 + 1B 2.0), plus P4 only if the measurement calls for it.

## 7. For the maintainer's ruling (then the user's, for P1)

1. **P1:** 1A + 1E now, 1B deferred to the user (recommended) — or 1B now, or 1C / 1D.
2. **P2:** 2E now and 2D as the build (recommended) — or 2D only, 2B, 2C, or 2A. Contracts unchanged.
3. **P3:** 3B (recommended) or 3C or 3D or 3A; plus who reserves (the lead alone, recommended) and
   the abandonment age (7 days, recommended).
4. **P4:** defer and re-measure in 14 days (recommended), or 4B now.
5. **P5:** 5a–5d as one amendment (recommended), or a subset.
6. **The sequence** of §6.

**After the ruling, P1 is the user's decision**: whether to transfer `yes-404/gi-pricing-plan`
to a free organisation and enable the queue. This RFC changes no script, workflow, ruleset or
code.

## 8. Where this RFC departs from its input memo

- **The merge procedure is `lead.md` rule 4, not `delivery-process.md` §15** (M14). The memo's
  file lists named §15 for 1B, 1D and 1E; this RFC names rule 4, and §8 for P5.
- **M3 / M4 re-measured** at 11:35:54 BST: 73 open, 72 drafts, 72 touching INDEX, 25 register, 20
  roadmap (the memo, at its time: 81, 78, 80, 27, 24). No PR is at the 100-file cap, so the counts
  are exact, not floors.
- **1E is already practice once** (#1238, §1), and rule 4 already permits it (M10).
- **2E is new**: a no-code stop-gap that, unlike 2B, also clears GitHub's mergeability for drafts.
- **1B's estimate** follows the memo's revised 2.0, not its first 1.5.

## Acceptance

None in this file. The maintainer rules by an `RL-` that cites this RFC by its minted id, and the
user decides P1 after it. Until then nothing here binds.
