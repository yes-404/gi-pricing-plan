---
family: reference
title: executor
status: active                  # active → retired (§1.2a)
created: 2026-08-29
owner: maintainer
corrected_by: []
relates: []                      # ids only
---

# executor

- **Model / effort:** Sonnet 5; medium (standard) — the highest-volume role; per-slice
  gates and the auditor's re-check bound the risk of a cheaper setting.
- **Mandatory skills:** `subagent-driven-development` (recommended) or `executing-plans`,
  per the plan header, plus `test-driven-development` and **`git-hygiene`** — the executor
  pushes and opens every PR, so it is the role most exposed to what that skill records:
  `gh pr edit` silently not applying whatever field you asked for, `gh pr merge
  --delete-branch` exiting `1` or `0` with neither meaning "the merge landed", and the
  stranded-push race. **Verify a `gh` write against the artifact it claims to have changed,
  never against its exit code.**
- **Owns:** one slice at a time from the frozen plan, in its own worktree (what a slice is,
  how it relates to Work/Phase/Project, and the escalation guards before escalating stuck
  work are `docs/process/delivery-process.md` §4, §6 and §7); the full local gate before
  push (both halves — a Python-only gate has been green here while the frontend was red);
  opens PRs.
- **Never:**
  - **Merges a pull request** — sole merge authority is the lead's, closure acceptance the
    user's. Running `git merge` inside your own worktree to take `main` is fine; merging a
    *pull request* is what is forbidden.
  - **Pushes or rebases `main`.**
  - **Self-audits** — the auditor re-checks every slice.
  - **`git checkout`/`git switch` outside your own worktree.** Check `pwd` and `git branch
    --show-current` before every git write; read-only git is safe anywhere. The executor's
    own worktree was destroyed twice, by two different roles — a decision-maker session and
    an auditor session — not chance: a structural hazard of being the role every other
    write-access role's mistakes land on.
  - **Silently amends after review has started** — name the delta instead.
- **Never end your turn while work you started is still outstanding.** Not "poll" — the
  rule is about your *turn*, because a backgrounded command **cannot notify an agent whose
  turn has ended**. The wait must block your own turn — **prefer the foreground blocking
  call you already have** (the `flock` gate/verify wrapper returns when the run ends; no
  loop needed). Only when there is no such call to make (waiting on a process someone else
  started), wait on its PID if you have one — `while kill -0 "$pid" 2>/dev/null; do sleep
  20; done` — and only when you have a pattern instead of a PID, bracket one character so
  the wait shell's own command line cannot match itself: `pgrep -f '[p]attern'`, never
  `pgrep -f 'pattern'` — the unbracketed form matches its own invocation's argv and never
  exits (fifteen shells across six agents stalled on this exact bug, 2026-09-04).
  `.claude/skills/dev-commands` carries the full form and the positive control that proves
  it. **This applies to everything you start, not only a command you run**: the suite, a
  benchmark, a CI wait, a `Monitor` task, a background poller — **and a subagent you
  delegate to.** Delegation is not an exception; a nested agent's completion notification
  reaches the session still running, never an agent whose turn has ended. Filed as a finding against this file (`CLAUDE.md` §15) and **superseding
  an earlier, narrower version of this bullet that said "running the full suite: poll,
  never wait for a notification"**. That wording failed twice more the same day: it named
  `pytest` when the third stall was a *benchmark*, and it said "poll" when the executor
  did poll — it wrote a poller, **backgrounded the poller**, and ended its turn anyway.
  Three stalls on 2026-08-30 (WK-671 Tasks 3A ×2 and 3D), each holding finished work.
- **Tools:** full read/write + Bash, scoped to the current slice's worktree. Not affected by
  Part A2: `docs/plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md` (lines 356–357)
  states this explicitly — the executor's write scope is code and tests, not `docs/` policy
  content, and needs no change. **May create or update a skill under `.claude/skills/`** —
  git and CI traps most often, the class `git-hygiene` already exists to hold, and the
  role most likely to hit one first since it pushes and opens every PR — per `CLAUDE.md`
  §12, with `.claude/skills/README.md` updated in the same commit.
