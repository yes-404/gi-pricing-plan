---
name: git-hygiene
description: Git and GitHub working discipline for this repo — what belongs in .gitignore and what must NOT be ignored, branch and PR flow, squash-merge and branch cleanup, and the merge-order trap that strands work. Use before committing, when creating a branch or PR, when deleting branches, when adding a new tool that generates files, or when a push is rejected.
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

## Deleting branches after a squash-merge

Squash-merge rewrites history, so `git branch -d` **refuses** even when the content is
fully merged. Never reach for `-D` without checking first:

```bash
git diff --stat main <branch>      # must be empty
git branch -D <branch>             # only then
```

Verify by **content**, not by PR status or git ancestry.

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
grows one miss at a time; the standing plan (`CLAUDE.md` §2) is an always-running
aggregator job once branch protection arrives.

## Verified

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
