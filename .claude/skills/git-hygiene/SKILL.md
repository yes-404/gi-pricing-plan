---
name: git-hygiene
description: Git and GitHub working discipline for this repo — what belongs in .gitignore and what must NOT be ignored, branch and PR flow, squash-merge and branch cleanup, how a squash commit's title and body are composed (including the `(#N)` the merge API will not add for you), and the merge-order trap that strands work. Use before committing, when creating a branch or PR, when merging one, when deleting branches, when adding a new tool that generates files, or when a push is rejected.
---

# Git hygiene

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

**`gh pr edit --base` does not do this.** In this repository it exits reporting only a
Projects-classic deprecation error from its own GraphQL query, and the base is left
unchanged — silently, so a following `gh pr view` is the only way to notice. The REST call
above works where the `gh` subcommand does not, which generalises: when `gh` fails on a
field it did not need, reach for `gh api`.

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

## Verified

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
