---
name: git-hygiene
description: Git and GitHub working discipline for this repo — what belongs in .gitignore and what must NOT be ignored, branch and PR flow, squash-merge and branch cleanup, how a squash commit's title and body are composed (including the `(#N)` the merge API will not add for you), and the merge-order trap that strands work. Use before committing, when creating a branch or PR, when merging one, when deleting branches, when adding a new tool that generates files, or when a push is rejected; and why an amend must name its delta
---

# Git hygiene

## `main` is governed by a ruleset: squash is the only merge method, and nobody can bypass

Set by the maintainer **2026-08-30 14:04Z** as ruleset **`main-protection`** (id 21860967),
replacing the earlier two-rule `Rule1`. It targets `~DEFAULT_BRANCH` only — feature branches
are unconstrained, verified by pushing and deleting one under it.

| Rule / parameter | What it means here |
|---|---|
| `deletion`, `non_fast_forward` | `main` cannot be deleted or force-pushed. Already forbidden by `lead.md`. |
| `required_linear_history` | Squash merges satisfy this; a merge commit would not. |
| `allowed_merge_methods: ["squash"]` | **`--squash` is now the only accepted form.** `gh pr merge --merge` or `--rebase` will be refused. |
| `required_approving_review_count: 0` | **No approval needed — this is what keeps the pipeline moving.** Every PR here is authored by the same account the token belongs to, and GitHub does not let an account approve its own PR, so any non-zero count would deadlock every merge. |
| `required_review_thread_resolution: true` | An unresolved inline review thread **blocks the merge**. The auditor reports through messages, not PR comments, so this bites only when someone posts an inline comment — resolve it before merging. |
| `require_extra_approval_for_unattributed_changes: true` | Would demand an approval nobody here can give. Empirically **not** triggered by our commits — a probe PR carrying the usual author and `Co-Authored-By: Claude Opus 5` trailer reported `reviewDecision: ""` and merged cleanly. |
| `bypass_actors: []`, `current_user_can_bypass: "never"` | **No exceptions, including for this token.** Correct, and worth keeping. |

**Verify the merge path empirically after any ruleset change, not by reading the JSON.**
`mergeStateStatus: CLEAN` means *no conflict and no failing required check* — it does not mean
the ruleset will accept the merge, and the two are easy to confuse. The check that settles it
is a completed merge.

## Keep commit messages and PR bodies plain

**Maintainer's instruction, 2026-08-30**, once the repository went public: keep them low-key.
Commit messages and PR bodies are now public artifacts, read by people with none of the
session's context.

State what changed and why. Skip the emphasis — heavy bolding, rhetorical framing, and
narrative reconstruction of how a defect was found read as noise in a public log. Where the
reasoning is genuinely load-bearing it belongs in the artifact the commit lands (a ruling
record, a register row, a note), not in the commit message pointing at it.

Length follows the change. A two-line fix does not need twenty lines of justification, and a
ruling that inverts a previous one does — the test is whether a reader needs it to understand
the diff, not whether it was interesting to write.

## The repository is public: merge only the maintainer's own pull requests

**Standing maintainer instruction, 2026-08-30**, when `yes-404/gi-pricing-plan` went public:

> *"keep an eye on PR not created by maintainer, as the project is public now, plz keep merge
> PR only from the maintainer and report the others"*

**Merge a PR only when `author.login` is `yes-404`. Any other author is reported to the
maintainer and left alone** — not merged, not closed, not reviewed into a state that invites
merging.

**Why the boundary is clean here and would not be in most repositories**: every agent on this
team pushes with the *maintainer's own* token, so a team PR and a maintainer PR are the same
author by construction. Measured 2026-08-30 rather than assumed — **all 466 PRs in the
repository's history are authored by `yes-404`, with no exceptions**, and the fork count is
**0**. So a non-`yes-404` author is not an edge case to adjudicate; it is, today, definitionally
an outside contribution.

```bash
gh pr list --state open --json number,author,title --jq '.[] | select(.author.login != "yes-404")'
```

**Check the author before every merge, not once per session.** A PR that was absent when you
listed open PRs an hour ago is exactly the one this rule exists for.

**This is a merge rule, not a review rule.** An outside PR may be read, and reading it is how it
gets reported usefully. What is forbidden is landing it.

**Three repository controls that would enforce this mechanically are still unset**, and all
three return **403 to this token** (verified again 2026-08-30 — it can read Actions runs but
not repository administration): **branch protection on `main`**, **fork-PR workflow approval**,
and the **read-only default `GITHUB_TOKEN`**. Until the maintainer sets them, this rule is
enforced by a person reading an author field, which is exactly the class of control
`CLAUDE.md` §13 says has never been tested until it has printed a failure. Treat it
accordingly.

## Branch and PR flow

```bash
git checkout main && git pull                 # always start from a current main
git checkout -b <type>/<short-slug>           # docs/… feat/… chore(…)/… spike/…
# work, then:
python3 scripts/audit-docs.py                 # docs changes
uv run pytest -q                              # code changes
git push -u origin <branch>
gh pr create --base main --head <branch> ...
gh pr merge <n> --squash                      # CLAUDE.md §10
```

**Always target `main`.** This is the rule that cost the most to learn.

**A branch name containing the substring "git" can trip the worktree isolation guard.**
The guard that keeps a worktree-isolated session's git commands inside its own tree counts
occurrences of the literal text "git" across the whole command line, not just the leading
command word — `git checkout -b skills/git-hygiene-<slug>` reads as two ("git" the command,
"git" inside "git-hygiene") and is refused as unverifiable, even though it is one ordinary
git invocation and the branch name is fine on its own. Recurs for anyone naming a branch
after this skill specifically, since `git-hygiene` is the collision. Rename around it —
`skills/hygiene-<slug>` passes, `skills/git-hygiene-<slug>` doesn't — rather than fight the
guard; it has no override.

> **The stranding trap.** PRs #8 and #10 were merged into an intermediate branch
> (`chore/skills-library`) *after* that branch had already merged to `main`. Both looked
> merged — green PR, closed, branch gone — and neither reached `main`. It happened twice
> before anyone noticed, and the second time only because a spot-check compared file
> contents rather than PR status.
>
> If work genuinely builds on an unmerged branch, **rebase onto it and open one PR to
> `main`** rather than stacking PRs. Verify with:
> `git log --oneline origin/main..origin/<branch>`

`delete_branch_on_merge` is enabled, so merged branches clean themselves up.

### If a stack exists anyway: retarget the dependants *before* merging the one below

`delete_branch_on_merge` and a stacked PR combine badly. Merging the base PR deletes its
branch, and GitHub closes every PR that was targeting it — **irrecoverably**:

```
$ gh api -X PATCH repos/OWNER/REPO/pulls/84 -f state=open
state cannot be changed. The w5-gbm-contract branch has been deleted.   (422)
$ gh api -X PATCH repos/OWNER/REPO/pulls/84 -f base=main
Cannot change the base branch of a closed pull request.                 (422)
```

Both directions are refused, so the only way back is a **new PR** from the same branch,
carrying the closed one's body (`gh pr view 84 --json body -q .body`) and a line naming the
PR it replaces and why — otherwise the review history points at a dead number.

The order that avoids it, for a stack that is already open:

```bash
gh api -X PATCH repos/OWNER/REPO/pulls/<dependant> -f base=main   # first, while it is open
gh pr merge <base-pr> --squash --delete-branch                    # then
git rebase --onto origin/main <old-base-tip> <dependant-branch>   # then re-verify by content
git push --force-with-lease origin <dependant-branch>
```

A retargeted PR's diff temporarily includes the commits below it; the rebase is what makes
the diff honest again. Check it (`git diff --stat origin/main..<branch>`) before merging.

**`gh pr edit` does not do this, on *any* field — `--base`, `--title`, `--body` all fail the
same way.** The command's GraphQL query always fetches `projectCards` as part of an edit,
and that query now errors on this repository (Projects-classic deprecation) — so the whole
command exits reporting only that error, and the edit is silently not applied, whichever
field you asked it to change. `gh pr view` is the only way to notice, because the exit and
the error text give no hint that the field itself was untouched. The REST call above works
because it never asks for `projectCards`; the general working form for any field:

```bash
gh api -X PATCH repos/<owner>/<repo>/pulls/<N> -f title="…"     # short fields: -f
gh api -X PATCH repos/<owner>/<repo>/pulls/<N> -F body=@<file>  # long/multiline: -F …@file
```

This generalises past `gh pr edit`: **every `gh` write is unverified until you re-read the
artifact it claims to have changed** — not the exit code, not the absence of an error
message, the artifact itself. A title or body edit: `gh pr view <N> --json title,body`. A
base change: `gh pr view <N> --json baseRefName`. A merge: `gh pr view <N> --json
state,mergeCommit`. `gh pr merge --delete-branch` is the sibling case for why this is a
rule and not a one-off caution: it has been seen to fail its local branch-delete step while
exiting `1` on one PR and `0` on another, same underlying message either way — so **no exit
code means "the merge landed."** Only re-reading state does.

**The rule generalises past `gh` too: a plain `git push` can report success and still
strand the commit, if the PR it was going to was merged out from under it.** Merging a PR
deletes its branch (`delete_branch_on_merge`); pushing to that branch name afterwards
*recreates the deleted remote ref* — `git push` succeeds, prints nothing alarming beyond an
unexpected "create a pull request" hint on a branch that should already have had one — and
the pushed commit is now on a ref with no open PR, nowhere near `main`. **Check `gh pr view
<N> --json state,mergedAt` before pushing to a PR branch you did not just open, and again
after any push that prints something unfamiliar.** If a commit is found stranded this way,
**the fix is a cherry-pick onto current `main` in a fresh branch, not a re-push to the old
one** — and verify the resulting diff (`git diff origin/main --stat`) is exactly the
stranded commit and nothing else re-added from the dead branch.

**Name the race for what it is: it takes two sides, and only naming both prevents it.** It
happens when a reviewer merges a PR while its author is still pushing to it. The author's
half is the check above. **The reviewer's half is asking before merging a PR whose author
may still be working**, rather than merging the moment CI goes green — a rule that
disciplines only the pusher lets the merger repeat their half of it indefinitely.

**Same family as the stranded-push race above, different mechanism: a reference correct
when made can go silently wrong by the time it is used, caught only by re-checking state
rather than trusting an earlier read.** Citing a document by line number
(`ruling-record.md:203-226`, in a PR description or a report) is only accurate as of the
commit it was read at. A `git fetch && git rebase` that pulls in commits touching that same
file shifts every line after their edit — silently, since the rebase succeeds cleanly
whenever the touched ranges don't textually conflict with the branch's own unrelated
changes.

**2026-08-29, caught before it shipped.** A PR description drafted six citations into
`docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md` by line range, correct
against the commit the branch had forked from (`86ff7c1`). Before pushing, `origin/main`
had moved to `625fe8c` — two of the three new commits touched that exact file (+71/-3, then
+6/-2), both inserting content *above* the cited ranges. Rebasing without re-deriving the
citations would have shipped a PR description pointing at the wrong paragraphs while
reading as fully checked.

**Re-derive after, not before.** Check which files a pending rebase touches
(`git show --stat --format="" <sha>` per new commit) before assuming a citation survives
it, then re-read every line-anchored reference against the post-rebase content — never
against what was read pre-rebase. The same discipline as re-verifying a `gh` write against
the artifact rather than its exit code (above), applied to your own prose instead of a
tool's report.

## The stash stack is shared by every worktree — never use bare `git stash`

**There is one stash stack per repository, not one per worktree.** Every parallel session in
this repo — the main checkout and every `.claude/worktrees/*` — pushes onto and pops off the
same stack. A bare `git stash` followed by `git stash pop` therefore has no guarantee it
restores your own work: a peer that stashed in between is what you pop, into *your* tree, and
your changes stay buried under theirs.

**Prefer a throwaway WIP commit.** It is per-branch, so it cannot collide:

```bash
git commit -am "wip"                          # set aside
git reset --soft HEAD~1                       # bring back
```

If you must stash, never pop and never index by position:

```bash
git stash push -u -m "w32-11-certfloors"      # unique tag, -u keeps untracked files
git stash list --format='%H %gs'              # capture YOUR entry's SHA immediately
git stash apply <sha>                         # apply by SHA, not stash@{0}
git stash drop "$(git stash list --format='%gd %gs' | grep w32-11-certfloors | cut -d' ' -f1)"
```

`stash@{n}` is a position in a stack other sessions are mutating, so it means something
different by the time you use it — the same failure mode as any positional reference into a
list you do not own.

**One skill still teaches the retired advice.** `testing-strategy`'s "prove the guard fails"
recipe says *"revert the fix (git stash, or hand-edit the guard back to its broken form)"*.
That skill is **vendored** and is not edited (`CLAUDE.md` §12), and it is not wrong upstream —
`git stash` is safe in a single-worktree repo. It is wrong **in this repository's conditions**.
Take the hand-edit branch of that sentence, or a WIP commit. The deviation is recorded in
`.claude/skills/README.md` rather than made silently in the vendored file.

## Rebasing a branch another worktree has checked out

A stale branch is often checked out **in another worktree with uncommitted work on top** —
this repository runs parallel sessions, and `git worktree list` is how you find out before
you destroy something. `git rebase` there refuses outright (`cannot rebase: You have
unstaged changes`), and stashing or committing on someone else's behalf is not the fix.

Rebase in a **scratch worktree of your own** and push only the remote ref:

```bash
git worktree add --detach "$CLAUDE_JOB_DIR/tmp/w" origin/main
cd "$CLAUDE_JOB_DIR/tmp/w" && git cherry-pick <tip>          # or rebase --onto
git push --force-with-lease=refs/heads/<branch>:<old-sha> \
    origin HEAD:refs/heads/<branch>
```

**A force-push moves the remote ref and nothing local.** The peer's branch still points at
the old commit and their working files are untouched; only their upstream reads `[gone]`
after the merge, which is cosmetic. Use the fully-qualified
`--force-with-lease=<ref>:<sha>` form — from a detached HEAD the bare `--force-with-lease`
has no remote-tracking ref to lease against.

Two `gh` behaviours follow from the detached HEAD, both harmless once expected:

- `gh pr merge --squash --delete-branch` **merges, then fails** with `could not determine
  current branch` while trying the local delete. The merge already happened — re-running it
  reports `already merged`, so check before assuming it did not.
- Run from the main checkout instead and the local delete is **refused** by git: `cannot
  delete branch '<branch>' used by worktree at …`. That refusal is the protection, not a
  problem to force past. Leave the branch; the peer still needs it.

The reason to bother rather than opening the PR from the stale branch: its three-dot diff
carries every commit since the merge base, and squash-merges make already-merged work look
unmerged by ancestry. `git diff --stat origin/main <branch>` — **two dots** — is what shows
the real delta, and a large deletion count there means the branch is behind, not that it
deletes anything.

## Deleting branches after a squash-merge

Squash-merge rewrites history, so `git branch -d` **refuses** even when the content is
fully merged. Never reach for `-D` without checking first:

```bash
git fetch origin                          # local main goes stale the moment a PR merges
git diff --stat origin/main <branch>      # must be empty
git branch -D <branch>                    # only then
```

Verify by **content**, not by PR status or git ancestry.

**Compare against `origin/main`, not local `main`.** A PR merges on the server, so the
local ref is behind until something pulls it — and against a stale `main` the diff lists
the branch's own files as additions. That reads as "not merged" for a branch that is, which
fails safe but for the wrong reason, and the next move after a misread is usually `-D`
anyway.

**`git fetch` updates a ref, never your working tree.** `git log origin/main` can read
correctly the moment a fetch completes while every file on disk still reflects whichever
commit is actually checked out — nothing moves it until a `merge`, `rebase`, or `checkout`
does. Same shape as `--date=iso-strict` below: a command answers exactly what it was asked,
which is not always the question the reader meant.

**A `--ff-only` merge that FAILS is a worse trap than never fetching at all — it leaves a
belief of having synced instead of the visible absence of a sync.** `git merge --ff-only
origin/main` run while checked out on an unrelated feature branch fails with "Not possible
to fast-forward" — that branch's own divergence, nothing to do with whether the *home*
branch could have fast-forwarded cleanly. Switching back to the home branch afterward and
treating the failed attempt as "tried, moving on" — rather than re-running the merge from
the branch it actually applies to — leaves the tree exactly as stale as never having
fetched. Worse: never fetching prompts a retry the next time freshness matters, because
nothing claims to have happened; a failed-then-abandoned attempt reads, from memory alone,
as "I synced this session," and that false belief survives until something external
contradicts it.

**A file count is ambiguous unless it names its measure, and a deletion decision needs the
right one.** Checking whether a branch is safe to delete can produce three different file
counts, disagreeing in both number and membership — found recovering a stranded commit
(`c78a051`, #337, #340):

- **Files the branch touches**, vs. its own merge-base: four.
- **Files that still differ from the squash commit**, scoped to those same four: three —
  one of the four landed clean and matches exactly, byte for byte.
- **An unscoped diff against current `origin/main`**: four again, but a *different* four —
  main had moved since the branch forked, so a file the branch never touched at all (a
  `docs/plans/` record that grew afterward) shows up purely from drift.

None of the three is interchangeable with the others, and only one answers the question a
deletion decision is actually asking: **the file-scoped diff against the squash commit** —
"is anything left over," not "what did the branch once touch" or "what differs from main
today." Name that scope whenever a file count backs a deletion decision; an unnamed count
means nothing (`CLAUDE.md` §13's rule for a reference — a count carries the corpus it
counted over — applies here too, in the one place getting it wrong deletes work).

**Even the right measure only tells you *that* the sides disagree, never *how much* of the
branch's own content is missing.** Reading the three hunks in this case, two of the
"differing" files turned out to carry nothing from this branch at all — an unrelated row
changed by a different, later commit in one, an unrelated citation added by an earlier PR
from this same session in the other. Only the third file, where the branch's own two
commits happened to touch the identical row, carried this branch's real, still-missing
change. **Read every hunk a file-scoped diff surfaces — a file's presence in the list
proves something differs, never that the difference is this branch's own.**

### `ExitWorktree` refuses for the same reason, and says something scarier

Removing a worktree whose branch was squash-merged is refused:

```
Worktree has 1 commit on <branch>. Removing will discard this work permanently.
Confirm with the user, then re-invoke with discard_changes: true
```

The commit is already on `main`. This is the `git branch -d` illusion above wearing
different words — unmerged by **ancestry**, fully captured by **content** — but "discard
this work permanently" invites either abandoning the cleanup or discarding blind, and the
tool cannot tell the two situations apart because ancestry is all it has.

Run the two-dot diff first. Empty means `discard_changes: true` is the correct answer and
nothing is lost; non-empty means read it before doing anything.

**Removing the worktree does not pull the merge.** The session returns to a main checkout
still sitting at the pre-merge commit, so the files that just landed are absent from disk
and `git status` reports `[behind 1]`. Finish the job:

```bash
git merge --ff-only origin/main
```

## A worktree-pinned session cannot read a sibling's — or the primary checkout's — working directory, by design

Both obvious routes are blocked, confirmed 6/6 across a real fanout (five sibling
worktrees plus the primary checkout, W11 pre-stand-down audit, 2026-08-29): in every case
zero commands executed against the target's actual files.

- **`git -C <other-path>` or a bare `cd` into another worktree** — refused before running
  anything, sibling or primary checkout alike, identical wording either way: *"This
  session is isolated in the worktree \<yours\>... a worktree-isolated session's git
  operations must target its own worktree."*
- **`EnterWorktree({path: <sibling>})` is not a working substitute**, and fails three
  different ways depending on the target:
  - **Locked by a live session** — refused cleanly, naming the pid: *"\<worktree\> belongs
    to another running Claude Code session (locked: claude session \<name\> (pid N start
    T)). Wait for that session to finish or choose a different worktree."* The safe
    outcome — nothing was attempted against that worktree's files. `ps -p <pid>` confirmed
    the named session genuinely alive in two of two spot-checks.
  - **Not locked** — the tool reports success (*"This agent's working directory... now
    point at the worktree; the previous directory was left untouched"*) but the sandbox
    enforcement layer does not follow: every command afterward, including a bare `pwd`, is
    still refused with the same "isolated to your original worktree" error. **A success
    report from `EnterWorktree` is not evidence the sandbox will actually permit what comes
    next** — confirm with a no-op read before trusting the switch.
  - **Target is the primary checkout** — a third, distinct refusal: *"Cannot enter
    worktree: \<path\> is the main working tree, not a linked worktree."* Categorically
    unreachable this way regardless of lock state.
  - A subagent spawned from a pinned session inherits the same pin and hits the identical
    three outcomes — delegating the attempt does not route around it.

**What still works, from anywhere, without switching**: every worktree of one repository
shares the same object and ref database, so anything addressed by branch name or SHA reads
fine from your own pinned location — `git log --oneline origin/main..<branch>`,
`git diff --stat origin/main..<branch>`, `git show --stat <sha>`, `git stash list` (one
shared stack, not per-worktree), `git worktree list --porcelain`, `gh pr list --head
<branch>`. That covers the **unmerged-commits** half of a cross-worktree check completely.
It does not cover **uncommitted tracked edits or untracked files** — those exist only on
the other worktree's disk with no ref, so nothing short of a session physically rooted
there can see them.

**The consequence for a cross-worktree audit** (ruled here, W11, 2026-08-29): gathering
the working-directory half for every worktree but your own is structurally not a
worktree-pinned member's job — the guard blocks both routes on purpose, to stop one
session reaching into another's live files. That half belongs to a session actually
rooted at the primary checkout, where `-C` and `cd` are unrestricted, or to each
worktree's own occupant self-reporting. A pinned member can still gather the full
ref-based half for every worktree safely, and should, since it needs no switch at all.

## A fork that reports "started in background" has already started, whether or not you meant it to

Different failure from the cross-worktree isolation above — this one is about a fork
spawning *another* fork, and it looks identical to genuine cross-session tampering from
inside the session it happens to.

**What was observed, 2026-08-30.** A fork dispatched with an explicit "investigation only,
do not edit" brief attempted a nested `Agent(subagent_type:"fork")` call of its own. Its
first attempt reported having started in the background; a second attempt errored `Fork is
not available inside a forked worker` — nested forks are not supported, but the error only
fires on the *second* call, after the first has already launched and detached. That first
nested fork went on to work, unsupervised, in a **different** worktree than the one its
parent (and the top-level session) were pinned to, committing there with no completion
signal ever reaching the top-level session.

From inside that top-level session, the result was indistinguishable from a real isolation
breach: `git worktree list --porcelain` showed the worktree locked to *this* session's own
name and pid — because it was this session, several forks removed — while files inside it
changed on disk with no corresponding tool call in the visible transcript, more than once,
each revision more detailed than the last. **The tell, confirmed after the fact**: content
that matches the top-level session's own reasoning too closely to be a coincidence — in
this case, per-directory error counts from an independent `mypy` investigation landing
within single digits of a number already derived by hand, and prose extending an existing
comment's exact argument rather than starting a new one.

**Get the provenance right before writing it down as fact.** The account above was pieced
together partly from the nested fork's own self-report relayed through a third party, and
one detail in an early version of that account did not survive a check against this
session's own tool-call history: the *first* commit in the affected worktree was made by
plain `Bash`/`Edit` calls this session issued directly and can point to line by line, not by
the nested fork — the fork's unsupervised edits were **later, additive** ones layered on top
of an already-good, already-committed baseline. A provenance claim assembled from a
relayed account is a citation like any other (`NT-0006`): trace it against the artifact —
here, the actual tool-call sequence — before it goes into a durable note, not just against
how plausible the story sounds.

**What to do when this happens to you.** Do not push over an unexplained file state, and do
not assume malice or a real cross-session leak either. Preserve the diff (`git diff HEAD >
/tmp/...`), check `git worktree list --porcelain` for the lock owner, message the
suspect fork directly asking for its location and action history with an explicit
instruction to stop, and escalate to whoever can see the full agent tree (a fork cannot see
its own descendants; a lead orchestrating the dispatch usually can). Verify the content is
actually correct before keeping any of it — this is still "trust but verify" for a subagent,
one hop further removed than usual.

## What goes in `.gitignore` — and what must not

Ignore build output, caches, environments and editor state. **Do not ignore:**

| Not ignored | Why |
|---|---|
| **`uv.lock`** | It is a *lockfile*, not an environment. Committing it is what makes builds reproducible (FR-OVR-8 determinism). The instinct to lump it with `.venv/` is the single most common uv mistake |
| `.claude/skills/` | Project knowledge travels with the repo (`CLAUDE.md` §12) |
| `docs/contracts/**/*.json` | Drafted contracts are a deliverable this phase |
| `deploy/docker-compose.yml` | The local stack is part of NFR-OVR-9 |

Adding a tool that generates files? **Update `.gitignore` in the same commit.** Otherwise
the first `git add -A` sweeps its cache in.

**Worktrees inside the repo are ignored — `.claude/worktrees/`.** `EnterWorktree` writes
them there rather than under `$CLAUDE_JOB_DIR/tmp` like the scratch worktree above, so a
second checkout of this repo sits in the tree. It does *not* get swept in file by file:
each carries a `.git` file, so `git add -A` adds the directory as an **embedded git
repository** — a gitlink no clone can resolve, and a commit nobody can use. Parallel
sessions make a kept worktree normal, and it may be someone else's live work.

**`.gitignore` does not untrack what is already tracked.** Once a file is in the index, a
new pattern is ignored for it — the giveaway is `git status` showing it as *modified*
rather than untracked. Recovery:

```bash
git ls-files | grep -E "__pycache__|\.pyc$|\.venv"   # find what slipped in
git rm -r --cached <paths>                            # index only; files stay on disk
```

Check for this whenever `.gitignore` is added *after* the code it should have covered.

## Never commit

Secrets or credentials of any kind (`07` FR-PLAT-26 — they are referenced, never stored),
real customer data, `.venv/`, `__pycache__/`, or large binaries. A dataset belongs in the
blob store (ID-4), not in git.

If a secret is ever committed, **rotate it** — removing the commit does not un-leak it.

## Commit messages

### Never let a `claude.ai/code/session_…` link reach GitHub

The agent runtime emits a `Claude-Session:` trailer by default. **It is configured nowhere in
this repository** — no `commit.template`, no `.claude/` setting — so you cannot switch it off
at the repo level, and a member spawned before the rule existed will emit it while believing
it is complying.

**So the guard belongs at the merge, not at the commit.** That is the only point where one
person controls what lands:

```bash
git log <head-sha> -1 --format=%B | grep -v 'Claude-Session:' > /tmp/body.txt
gh pr merge <N> --squash --subject "<title> (#N)" --body-file /tmp/body.txt
git log -1 origin/main --format=%B | grep -c 'claude.ai/code/session'   # must print 0
```

The last line is the point. **Re-read the merged commit** — the same discipline as every other
`gh` write here, and the reason this one is trustworthy: it was verified on `98eca40` and
`c8d3c81`, which reached `main` clean from branches carrying three links between them.

For a multi-commit branch, pipe every commit's body through the filter, not just the tip.

**What is banned** is the session URL. **What stays** is
`🤖 Generated with [Claude Code](https://claude.com/claude-code)` — a product link, not a
session handle.

**Do not try to clean history.** 73 commits on `main` already carry one; they are accepted with
this instrument as register row **F49**, and rewriting a public `main` would invalidate every
SHA cited across the register, the plans and the closure records.


Conventional Commits (`CLAUDE.md` §10). Because PRs are squash-merged, **the squash body is
the permanent record** — write it as the thing a reader finds in `git log` two years later,
not as a note to the reviewer. State what changed, why, and what it cost.

### Building the squash title: the `(#N)` is yours to add

`PUT /repos/{owner}/{repo}/pulls/{n}/merge` uses an explicit `commit_title` **verbatim** and
appends nothing to it. Pass the bare PR title and the squash lands with no PR reference in
its subject — which is how `cbb8ffb` became the one commit on `main` that a reader cannot
trace back to its discussion.

```bash
commit_title="${PR_TITLE} (#${N})"   # build the suffix yourself, exactly once
commit_message="${PR_BODY}"          # the permanent record, not the default commit list
```

Then **read the subject back** and count the suffix:

```bash
git log origin/main -1 --format=%s
```

There is no second chance: amending a landed squash means force-pushing `main`.

The count matters in both directions. `main` also carries `… partial-dependence cap (#135)
(#135)` — doubled — though PR #135's own title holds no number at all, so some other merge
path composes it differently. Read the landed subject rather than reasoning about which
path appends what.

### `gh pr edit --body-file` silently leaves the old body in place

Editing a PR body on this repository fails, prints an unrelated-looking error, and **exits
without changing anything**:

```
$ gh pr edit 436 --body-file new-body.md
GraphQL: Projects (classic) is being deprecated in favor of the new Projects experience …
  (repository.pullRequest.projectCards)
```

`gh pr edit` fetches `projectCards` as part of the mutation it builds, that field is
deprecated here, and the whole call aborts — so the body is untouched while the message says
nothing about the body. **This is a lost update that reads as a schema warning.** It cost a
correction PR here: the body still asserted a claim the commit had already retracted, and it
was caught only by reading the body back.

**The form that works** — the REST endpoint takes the body directly and never touches
projects:

```bash
gh api repos/<owner>/<repo>/pulls/<n> -X PATCH -F body=@new-body.md --jq '.number'
```

`-F body=@file` reads the file; `-f body=@file` would send the literal string `@file`.

**Then read it back, whichever form you used** — this is the role practice in
[`../../roles/auditor.md`](../../roles/auditor.md) generalised, and the reason it exists:

```bash
gh pr view <n> --json body -q '.body' | grep -c '<a phrase only the NEW body has>'   # expect 1
gh pr view <n> --json body -q '.body' | grep -c '<a phrase only the OLD body had>'   # expect 0
```

Grep for **both** phrases. Checking only that the new text is present passes when the API
appended rather than replaced; checking only that the old text is gone passes when the body
was emptied. **Verify a `gh` write against the artifact it claims to have changed, never
against its exit code** — and here not even against its exit code, which was non-zero while
the operation both failed and reported a reason that pointed elsewhere.

## A date read from `git log`'s default rendering is not UTC, and neither is `--date=iso-strict`

`git log`'s default format, and `--date=iso-strict`, both render a commit's **author-local**
timestamp with whatever offset the committer's machine recorded — not UTC, and not
whatever timezone the reader happens to be in. Two real commits from this repository's own
history show why that matters: `eb9b6a1` and `3a4958a` are both recorded at `+01:00` and
both render as `2026-08-28T00:4x...` in that offset — but in UTC they are
`2026-08-27T23:4x...`, a full calendar day earlier. Reading either rendering at face value
and calling it "August 28" is wrong by a day, purely from the offset, for any commit within
about an hour of a UTC day boundary.

**`--date=iso-strict` does not fix this.** Verified directly, against the same commit,
under three different `TZ` settings: `--date=iso-strict` prints `+01:00` regardless — the
commit's own recorded offset, unaffected by the reader's environment. The command that
actually converts to UTC — checked under `TZ=UTC`, `TZ=America/New_York`, and no `TZ` set,
to confirm it isn't an accident of one host's default — is:

```bash
TZ=UTC git log --date=iso-strict-local ...
```

**Use that exact command, or state the offset you read a date at.** Never quote a date from
a rendering whose offset you have not checked — the default format and `--date=iso-strict`
both look authoritative and are both silently wrong once a commit sits near a UTC day
boundary. When correcting someone else's date, name the offset you read it at, so a reader
can tell a genuine correction from the same mistake restated with more confidence.

## When a push is rejected

Read the message rather than retrying. Two seen in this repo:

- `refusing to allow a Personal Access Token to create or update workflow … without
  workflow scope` — the PAT cannot write `.github/workflows/`. Split that file out so the
  rest lands, and ask for the scope.
- `Resource not accessible by personal access token` on `gh pr create`, `gh api`, or
  `gh run list` — a *different* missing permission each time (Pull requests, Administration,
  Actions). Name the specific one when asking.

## A `paths:` filter behaves differently on a PR than on a push

`on.pull_request.paths` matches the **whole PR diff**, not the commit just pushed. So a
workflow re-runs on every sync of a branch whose diff touches one of its paths, however
unrelated the new commit is — and a green run on a PR proves nothing about whether that
workflow would fire for a *push* of the same files.

This bites in the direction that matters: **you cannot demonstrate a path-filter fix on the
PR that contains it**, because the workflow file itself is in the diff and in its own
filter. What a PR *can* show is the defect — a diff containing `examples/*.py` that ran
docs and frontend and not python is conclusive, and is how the missing `examples/**` entry
was found.

Two filters here were each missing a directory of real Python — `scripts/**`, then
`examples/**` — both found the same way, months apart. A filter enumerating directories
grows one miss at a time.

### If branch protection is ever enabled

**Do not mark a path-filtered workflow as a required check.** A required check that does
not run on a given PR never reports, and the PR is blocked forever — a docs-only change
would sit waiting on `python.yml`, which its own `paths:` filter guarantees will never
fire. Add an always-running aggregator job and require *that* instead.

*(Moved here from `CLAUDE.md` §2 on 2026-08-23: it is PR-flow procedure, conditional on
something that has not happened, and an always-loaded file is the wrong place for both.)*

## Amending after review: a new SHA inherits clearance it never earned

CI re-runs on a re-push; nothing else does. Approvals, audit verdicts and
verification reports cite the SHA that earned them, and an amend replaces it with a
SHA nobody has read — while `gh pr view` keeps showing the PR as reviewed and green.
The amended commit therefore **inherits its predecessor's clearance invisibly**.

The rule: every amendment after review has started must **name its delta** — what
changed and why the earlier clearance does not cover it. The reviewer re-checks the
delta, not the PR. W6b-13 practiced this by accident: the executor's push `8ef8821 →
9e01578` was covered by an auditor verdict that enumerated exactly the three residues
it fixed; a silent amend would have carried the old verdict over the new code.

## Verified

**2026-08-30 — the nested-fork section above added**, from a live incident during W11
tooling work: a dispatched fork's own nested `Agent(subagent_type:"fork")` call started
before its second attempt errored on the unsupported-nesting message, and its unsupervised
descendant's edits in a sibling worktree were mistaken, briefly and reasonably, for a
cross-session isolation breach. Corrected once against the actual tool-call history:
provenance for the *first* commit in that worktree traced to this session's own direct
`Bash`/`Edit` calls, not to the nested fork, whose real edits were later and additive —
caught only by checking a relayed account against the primary source rather than accepting
a plausible story (`NT-0006`, applied to agent provenance rather than a document citation).

**2026-08-29 — the worktree-isolation section above added, from a live pre-stand-down
audit.** The lead ordered a read-only inventory of every worktree after a prior cleanup
had destroyed 7 untracked files by deleting before reporting. A fanout of six subagents
(five siblings, one for the primary checkout) tried both `-C`/`cd` and `EnterWorktree` and
hit the three refusal shapes above in every single case — confirmed empirically, not
inferred from the tool's docs, which describe the `EnterWorktree({path:...})` switch as
working for a pinned agent without qualifying that the sandbox layer can still refuse
everything after. The lead completed the actual audit from the primary checkout, where
`-C` is unrestricted, and named that split — ref-based half safe from anywhere, working-
directory half only from the primary checkout or the occupant itself — as the standing
rule for who runs one of these next time.

**2026-08-29 — the branch-name "git"-substring guard trap added, found writing this
file's own two entries above.** `git checkout -b skills/git-hygiene-failed-ff-only-trap`
was refused by the worktree isolation guard, quoting "names git more than once in a single
command" — a literal reading of that message, not yet a minimal-pair test: renaming to
`skills/failed-ff-only-abandoned-trap` (dropping only the word "git-hygiene") passed on
the identical, otherwise-unchanged command. Consistent with a substring count across the
whole command line rather than a structural check of the git invocation itself; not
independently isolated further than that one rename.

**2026-08-29 — the fetch-updates-a-ref-not-a-working-tree line added.** Same day, a
different session's local `HEAD` sat thirteen commits behind while `git log origin/main`
read correctly from a completed fetch, because a fetch had never been followed by a merge,
rebase, or checkout — a role-file audit count came back a flat contradiction against the
real one until the files were re-read with `git show origin/main:` instead of trusted from
disk. Recorded beside the UTC-offset entry below, not merged into it: same shape, a command
answering precisely what it was asked rather than what the reader meant, but different
commands and different fixes, so a reader hitting them back to back can still tell them
apart.

**2026-08-29 — the failed-ff-only-then-abandoned entry added, same day, a worse variant of
the entry above.** The auditor's `git merge --ff-only origin/main` failed while checked out
on an unrelated feature branch (`docs/w11-roadmap-nfr-rate-13-14`); the session then
switched back to its home branch without retrying the merge, and treated the sync as done.
A charter file was read and reported stale — a real, landed grant (`.claude/roles/
auditor.md`, PR #352, `271787a`) was reported missing. Confirmed by ancestry after the
fact: `b1d5741`, the auditor's own last-recorded position, was 3 commits behind `271787a`
and 10 behind the actual current tip — not the failed merge's target branch's problem, the
*home* branch's own staleness, uncorrected because the failed attempt was never revisited.
Distinguished from the entry above on exactly the axis that makes it worse: a bare
unfetched tree carries no claim of freshness, so a careful reader treats it as suspect by
default; a *failed, silently abandoned* sync attempt reads from memory as "handled," and
the false belief survives until an external ancestry check contradicts it.

**2026-08-29 — the `EnterWorktree` false-success case added, same class as the entry
above: an operation that reads as done when it wasn't.** Two of the six subagents in the
pre-stand-down worktree audit (worktree-isolation section above) called
`EnterWorktree({path: <an unlocked sibling>})` and got back a SUCCESS report — *"working
directory... now point at the worktree"* — then had every command afterward, including a
bare `pwd`, refused by the sandbox with the identical "isolated to your original
worktree" error, as if the switch had never happened. Full mechanism and all three
refusal shapes are recorded above; noted here too because the shared trap is the belief,
not the tool: **a reported success is not evidence of an effect**, exactly as a
silently-failed `--ff-only` merge above reads as a completed sync. No disruption resulted
here — the guard held regardless of what its own report claimed — but the pattern is the
one worth carrying forward, not this specific safe outcome.

**2026-08-29 — the UTC-offset date-rendering entry added.** A wrong calendar date, read from
a rendering whose offset was never checked, reached a filed plan review this same day.
Verified rather than narrated: two real commits from this repository's own W9 history
(`eb9b6a1`, `3a4958a`) are recorded at `+01:00` and land within an hour of the UTC day
boundary, so both `git log`'s default format and `--date=iso-strict` render them a full
calendar day later than their UTC date. Checked that `--date=iso-strict` does not correct
for this under three different `TZ` settings before writing down the command that does
(`TZ=UTC git log --date=iso-strict-local`) — confirmed empirically, not assumed from the
flag's name.

**2026-08-29 — the rebase-invalidates-line-citations entry added, caught while preparing a
PR description rather than after a bad citation was filed.** Checking each new upstream
commit's diffstat (`git show --stat --format="" <sha>`) before rebasing, rather than
assuming a prior read still held, is what caught it — the same "check state, don't trust
an earlier read" discipline the stranded-push entry below states, applied to a citation
instead of a branch ref. All six citations were re-derived against the post-rebase content
and landed correctly.

**2026-08-29 — the file-count-measurement entry added, found recovering the stranded-push
race's own actual casualty.** Checking whether the dead branch behind `c78a051` was safe to
delete produced three different, all-correct file counts depending what was actually being
measured (touched-by-branch, differing-from-squash-scoped, differing-from-current-main-
unscoped) — a first framing treated two of these as a right-answer/wrong-answer pair before
a second look showed neither was wrong, only unnamed. Corrected before landing rather than
after: the measurement point survived, the "someone miscounted" framing did not — recording
which number was wrong would have taught the next reader to check arithmetic instead of
naming a measure, which is not what actually went missing here.

**2026-08-29 — the stranded-push race added, found live during this same adoption's own
filing.** A PR was merged by the reviewer while the author was still pushing a follow-up
commit to its branch; the push succeeded, silently recreating the branch `delete_branch_on_
merge` had just removed, and the commit landed nowhere near `main` until re-filed via a
fresh cherry-pick. Caught by the author checking PR state after an unfamiliar push message,
which is the "re-read the artifact" rule from the entry below applied across the `gh`/`git`
boundary it was not originally written for — confirmed generalising correctly rather than
assumed to. Recorded with both sides of the race named, since a rule binding only the
pusher does not stop the merger from repeating their half.

**2026-08-29 — the `gh pr edit` warning above widened from `--base` alone to the whole
command, and generalised into the "re-read the artifact" rule.** First recorded 2026-08-24
(PR #173) for `--base` only; rediscovered independently on 2026-08-29 hitting `--title` and
`--body` on the NT-0010/0011 adoption's own reconciliation record, an hour before this
adoption's own §15 step 5 audit — because the 2026-08-24 finding lived only in the diagnosing
session's own memory, not in this file, and the role that needed it next had no way to reach
it. The correction here is of reach, not of fact: nothing in the original `--base` warning
was wrong, it was simply narrower than the failure actually is.

**2026-08-25 — the amend-clearance section above, learned live.** W6b-13's branch was
amended between the auditor's first table and its delta verdict; the delta was named in
the verdict, which is the only reason the new SHA's clearance was real. The
counterfactual — a silent amend carrying the old verdict — is the trap the section
records.

**2026-08-22 — PR #139, where `ExitWorktree` said "discard this work permanently" about
work that was already on `main`.** The `(#N)` rule below was followed and the landed subject
read back green — one `(#139)`, neither missing nor doubled — so the merge itself held. What
was new is the cleanup: `ExitWorktree` refused, reporting one commit it would discard, for a
branch whose `git diff --stat origin/main <branch>` was **empty**. The section above was
written for `git branch -d` and did not mention the tool the harness actually offers, so the
warning arrived with no procedure attached. Two things were confirmed rather than assumed:
`discard_changes: true` lost nothing — both files were present in `6319d2d` afterwards — and
removing the worktree left the main checkout at the *pre-merge* commit with the new files
absent from disk, which is why the `--ff-only` line is now part of the procedure instead of
something a reader is expected to think of.

**2026-08-22 — PR #136, and the `(#136)` that never arrived.** Merged through the REST API
rather than `gh pr merge`, passing `commit_title` as the bare PR title on the theory that
GitHub would append the number. It does not, and `main` cannot be force-pushed to correct
it. The two-dot content check above ran in the same session and did its job: an empty
`git diff --stat origin/main HEAD` proved all nine commits were captured in `cbb8ffb`
before the branch and its worktree were removed.

**2026-08-18 — `.claude/worktrees/` added to `.gitignore`.** It had been untracked since
the harness started creating worktrees there, and a peer session's `w5-backtest` was live
in it at the time. The embedded-repository behaviour above was confirmed with
`git add -An`, not assumed: git warns and adds a gitlink rather than the files.

2026-08-14 — Written after the trap fired twice. Confirmed: `git diff --stat main <branch>`
correctly identified `chore/skills-library` and `spike/s3-…` as fully superseded before
deletion, where `git branch -d` refused both because of squash-merge. The `.gitignore`
generated from the rules above stops `__pycache__` entering the tree.

**And it caught a live instance immediately.** W1 was committed before `.gitignore`
existed, so 12 `.pyc` files were already tracked; the new patterns did not untrack them,
and `git status` reported them as *modified*. `git rm -r --cached` cleared them. The
failure landed in the gap between writing this skill and committing it, which is a fair
demonstration that the same-commit rule above is a rule and not a preference.

2026-08-17 — W5's three-PR stack. The retarget-first order above was learned by not following it: merging #83 with `--delete-branch` closed #84, which then refused both reopening and a base change, and that slice landed as #90 instead. #88 survived the same event only because its base was moved to `main` first.

2026-08-15 — W6a close. The `pull_request` `paths:` behaviour above was learned by
pushing a commit as a proof it could not be.

**2026-08-17 — the worktree case, found by hitting all four steps.** `oq-model-3-8-9-revise`
sat four squash-merges behind `main` and was checked out in a peer worktree carrying ten
files of uncommitted work. The scratch-worktree cherry-pick, the fully-qualified lease, the
`gh pr merge` that merged before reporting failure, and git's refusal to delete the local
branch all behaved exactly as above; the peer's ten files were verified intact afterwards.
The one conflict was a single table row where `main` had escaped a pipe and the branch had
escaped it *and* added text — resolvable only by reading both sides, which is the argument
for rebasing before the PR rather than after review starts.
