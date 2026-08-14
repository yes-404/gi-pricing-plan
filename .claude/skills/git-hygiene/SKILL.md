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
the first `git add -A` sweeps its cache in, and cleaning up afterwards rewrites history.

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

## Verified

2026-08-14 — Written after the trap fired twice. Confirmed: `git diff --stat main <branch>`
correctly identified `chore/skills-library` and `spike/s3-…` as fully superseded before
deletion, where `git branch -d` refused both because of squash-merge. The `.gitignore`
generated from the rules above stops `__pycache__` entering the tree — it had already
appeared during W1 and was removed by hand, which is the symptom this skill exists to
prevent.
