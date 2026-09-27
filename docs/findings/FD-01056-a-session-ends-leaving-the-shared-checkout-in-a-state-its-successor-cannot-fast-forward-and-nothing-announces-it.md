---
id: FD-1056
family: finding
title: a session ends leaving the shared checkout in a state its successor cannot fast-forward, and nothing announces it
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-03
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F97.md
---

# F97 — a session ends leaving the shared checkout in a state its successor cannot fast-forward, and nothing announces it

**Filed 2026-09-03 at `e97b97a` by the lead, on the maintainer's direction, during W37-6's
resumption.** Id allocated by the lead and verified free before use — `git grep -hoE
'\bF[0-9]{2,3}\b' -- docs/findings/register.md docs/audit/findings/` at `e97b97a` returns a
maximum of **96**. Work item **W37-6**, phase 2.

## The mechanism

The lead's charter binds every *member* into its own worktree
(`.claude/roles/lead.md:66-70`: *"the lead dispatches every member into its own worktree …
never `git checkout`/`git switch` outside your own worktree"*). **The rule governs where work
happens. It says nothing about the state the shared checkout is left in when a session ends**,
and the shared checkout is the one tree every subsequent session starts from.

Two independent residues were found in it at the start of this session, both left by a
predecessor that halted correctly and filed a complete handover:

1. **A stale `.git/index.lock`.** Measured directly before removal:

   ```
   $ ls -la /home/puzhenhao1989/gi-pricing-plan/.git/index.lock
   -rw-rw-r-- 1 puzhenhao1989 puzhenhao1989 0 Sep  2 22:16 …/.git/index.lock
   $ pgrep -af git          → no git process holding it
   ```

   Zero bytes, `2026-09-02 22:16`, **no live git process**. Note the ordering: the local
   checkout's own `HEAD` commit `32fc63c` carries committer date
   `2026-09-02T22:21:08+01:00`, **five minutes after the lock's mtime**, so the lock is the
   residue of a *different, abandoned* operation and not of the one that produced the tree's
   own last commit. It had survived across a session boundary.

2. **A 28-commit-stale local `main`.** Measured at `e97b97a`, predicates verbatim:

   ```
   $ git rev-list --count 32fc63c..e97b97a   → 28
   $ git rev-list --count e97b97a..32fc63c   → 0
   $ git merge-base 32fc63c e97b97a          → 32fc63c
   ```

   No divergence — a clean fast-forward was available and simply had not been taken. Local
   `main` sat at `32fc63c` (`2026-09-02T22:21:08+01:00`) while `origin/main` was at `e97b97a`
   (`2026-09-03T17:17:34+01:00`), a gap of roughly nineteen hours.

**The two compose into the failure this row is about.** `git merge --ff-only origin/main`
failed on the lock, and its message is about editors and crashed processes:

> *"an editor opened by 'git commit'. Please make sure all processes are terminated then try
> again. If it still fails, a git process may have crashed in this repository earlier: remove
> the file manually to continue."*

That text points a cold reader at a live process and at a crash. **Neither was the case**, and
the correct action — verify no git process holds it, then delete — is reached only by
disbelieving the message enough to check. A session that instead terminated processes, or
retried, or treated the shared checkout as corrupt, would have burned turns or done damage on
a tree that was in fact clean and one command from current.

## Why this is the same shape as the outage-without-handover

`docs/rfcs/RFC-00842-a-credential-in-an-ephemeral-job-directory-is-borrowed-not-stored-and-is-found-by-its-shape-not-its-container-s-name.md:16-19` states its incident's shape:
*"a value was placed somewhere that stopped existing, and the search that looked for it
afterward checked the wrong thing. Either rule alone would have prevented the outage this
note is written from; neither was in place, so both fired."*

**The same two-cause structure holds here.** A predecessor left state in a location whose
contents do not survive its own session's assumptions, and the diagnostic the successor
reaches for reports the wrong cause. Either an end-of-session tree check, or a lock-staleness
predicate the successor could trust, would have been sufficient alone; neither existed, so
both fired.

**And the same asymmetry `RFC-789` and F84 record applies**: a guard that aborts announces
itself; a residue no check covers does not. The predecessor's halt was *correct* — the
handover (`docs/plans/PL-01037-w37-6-the-extended-window-s-second-fail-and-the-handover-2026-09-03.md` §10.1) discharges the halt
protocol's worktree clause one line per worktree, and verifies each was both `git status`
clean **and** on a branch whose tip is on the remote, *"because a clean worktree on an
unpushed branch is the durability failure this halt was ordered to avoid."* **That clause
covers the member worktrees and stops at the shared checkout**, whose own row reads
*"clean; not removed."* It was clean by `git status` — `git status` does not report a stale
lock or a stale `main`, so the check that was run could not have found either residue.

**This is not a criticism of that halt.** It is the observation that a durability clause
written for member worktrees leaves the one tree every successor inherits unexamined, and the
successor pays for it at the moment of highest load — the first minutes of a fresh session,
before it has read anything.

## Scope, stated honestly

**One occurrence, measured; the class is not.** This row records a single instance found at
one session boundary. Whether prior boundaries left the same residues is **not measured** and
is not claimed — the evidence would be in session-local state that no longer exists. It is
filed as a finding rather than a fixed nuisance because the cost falls on a successor who
cannot see the cause, which is the property that makes a residue worth a rule.

## Falsifiable

Discharged when a session boundary leaves the shared checkout in a state a successor can
verify in one command, by one of two remedies — named here rather than chosen, since the
choice touches `.claude/roles/lead.md`, whose amendment is the maintainer's:

- **A halt-protocol clause covering the shared checkout**, symmetric with the member-worktree
  clause the second-fail handover §10.1 already discharges: at halt, the shared checkout is
  `git status` clean, holds **no `.git/index.lock`**, and its `main` is fast-forwardable to
  `origin/main` with `git rev-list --count main..origin/main` recorded as the residual gap.
  The gap need not be zero — it must be *stated*, so a successor reads a number rather than
  discovering one.
- **Or a successor-side precondition check** that runs before a session's first git write and
  reports all three facts together, so the diagnosis does not depend on disbelieving git's own
  lock message.

Either way: discharged when a checkout left with a zero-byte `.git/index.lock` and a
non-divergent stale `main` produces a **named, actionable report** — the lock's mtime, the
absence of a holding process, and the fast-forward distance — rather than git's
editor-and-crash message, and when that report is exercised on deliberately broken input
(a lock planted on a clean tree with no git process running) rather than only on a clean one.
