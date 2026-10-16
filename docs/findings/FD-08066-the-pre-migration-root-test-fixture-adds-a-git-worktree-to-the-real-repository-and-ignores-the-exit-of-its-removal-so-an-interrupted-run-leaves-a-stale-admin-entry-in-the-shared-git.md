---
id: FD-8066
family: finding
title: The pre_migration_root test fixture adds a git worktree to the real repository and ignores the exit of its removal, so an interrupted run leaves a stale admin entry in the shared .git
status: active
created: 2026-10-16
owner: auditor
tree: a2f77b2dcad5aaec41a5f10aa664383caf421e8b
corrected_by: []
relates: [WK-1178]
---

# FD-8066 — `tests/test_doc_id_migrate.py::pre_migration_root` runs `git worktree add` against the real repository, and its teardown cannot fail loudly

*(Filed under working id 8066 (written "FD 8066" in prose), supplied by the lead; a minter folds it
into the docs batch. Authority: the maintainer's entry "2026-10-16 10:26:42 BST" in
`channel/to-lead.md`, which names the severity (LOW), the owner (WK-1178) and the remedy.
Reads were made at `origin/main` `a2f77b2dcad5aaec41a5f10aa664383caf421e8b`; the
`git worktree prune -n -v` output and the file times below were read on the shared checkout on
2026-10-16 about 10:25 BST.)*

## Finding

**Severity: LOW, as named by the maintainer (by delegation): the cost is a few stale files in the
shared `.git` that `git worktree prune` removes, not a wrong result. Owner WK-1178.**

The session-scoped fixture `pre_migration_root` (`tests/test_doc_id_migrate.py:159-194`) runs
`git worktree add --detach <tmp>/worktree fbb5555b…` with `cwd=ROOT` (`:183-186`), that is
against the **real repository**, and not against a clone of it. `git worktree add` writes an
administrative directory `.git/worktrees/<name>/` into the shared `.git`. The teardown (`:189-194`)
runs `git worktree remove --force` with **`check=False`** and `capture_output=True` (`:190-192`),
so a non-zero exit is neither raised nor printed, and then `shutil.rmtree(tmp, ignore_errors=True)`
(`:194`) deletes the temporary directory whatever the removal did. If the removal does not
succeed, or the teardown never runs, the directory goes away (by that `rmtree`, or by the reset
of `/tmp`, see Evidence 3) and the admin entry stays: its `gitdir` file then names a path that no
longer exists. The repository's own tool for the same need chose the other design on purpose:
`scripts/doc-id.py:163-166` says "A local `git clone` is used rather than `git worktree add`: a
worktree's `.git` points back into the source repository … so a worktree would write objects and
refs into the real repository".

**The trigger** is any pytest run that selects one of the four tests that use the fixture:
`test_doc_id_migrate.py:2197`, `:2725`, `:3321`, `:3368`. The full suite (`uv run pytest -q`,
`.github/workflows/python.yml:298-302`) selects all four. On a CI runner the checkout is thrown
away, so nothing persists. On the shared development checkout, `.git` is shared by every worktree
and every seat, so a leaked entry persists until someone prunes it.

## Evidence

### 1. The two stale entries

`git -C /home/puzhenhao1989/gi-pricing-plan worktree prune -n -v` (a dry run) prints exactly:

```
Removing worktrees/worktree1: gitdir file points to non-existent location
Removing worktrees/worktree: gitdir file points to non-existent location
```

| Admin entry | `gitdir` file content | `HEAD` | `gitdir` file birth time |
|---|---|---|---|
| `.git/worktrees/worktree` | `/tmp/pre-migration-root-my7ilume/worktree/.git` | `fbb5555b45f9b22ef8bc5571865ee8d9a86b62e8` | 2026-10-14 10:43:49 UTC |
| `.git/worktrees/worktree1` | `/tmp/pre-migration-root-u63z5u8a/worktree/.git` | `fbb5555b45f9b22ef8bc5571865ee8d9a86b62e8` | 2026-10-14 12:02:51 UTC |

The maintainer's entry says both were created on 2026-10-16. The `stat` birth time reads
**2026-10-14**; the date does not change the cause, and it is recorded so that "created" is
not taken from the entry. The directory names are `tempfile.mkdtemp`'s random suffix after the
prefix `pre-migration-root-` (`:181`). A search for the whole hyphenated name finds nothing,
because the code holds only the prefix; the prefix is what finds the code.

### 2. `fbb5555b` is the fixture's input

`git log -1 fbb5555b` is `#772 (rebased) (#781)`, 2026-09-17 10:51:52 +0100, the last commit
before the NT-0019 doc-id migration landed. `_PRE_MIGRATION_SHA` (`:156`) is that SHA. The
tests read real pre-migration content from the checked-out tree (`_discover_closure_records`,
`_discover_plan_reviews`, `_discover_multi_ruling_files`, and `docs/audit/plan-reviews.md`).
Nothing runs *at* the commit; it is only read.

### 3. Why the directory is gone and the entry is not

The code path (`origin/main` `a2f77b2d`):

| Lines | What it does |
|---|---|
| `tests/test_doc_id_migrate.py:159-160` | `@pytest.fixture(scope="session")`, `def pre_migration_root()` |
| `:181` | `tmp = pathlib.Path(tempfile.mkdtemp(prefix="pre-migration-root-"))` |
| `:183-186` | `git worktree add --detach <tmp>/worktree <sha>`, `cwd=ROOT`, `check=True` |
| `:188-189` | `yield worktree` inside `try:` … `finally:` |
| `:190-192` | `git worktree remove --force <worktree>`, `cwd=ROOT`, **`check=False`**, output captured |
| `:194` | `shutil.rmtree(tmp, ignore_errors=True)` |

Two facts decide the reading. First, `/tmp` on this machine is a `tmpfs`
(`df /tmp` prints `tmpfs`) and the machine booted on 2026-10-16 08:13:04 (`uptime -s`), after
both entries were made on 2026-10-14. So the absence of `/tmp/pre-migration-root-*` today proves
nothing about what the teardown did: a reboot empties it. Second, the entries exist at all.
If `git worktree remove --force` had succeeded, it would have deleted `.git/worktrees/<name>/`.
So on both runs the removal either **failed with an exit that `check=False` discarded**, or
**never ran** (a killed or timed-out pytest does not run a `finally`). This audit cannot say which
of the two happened on 14 Oct, and does not claim to: the output of those runs was not kept.
What is established is the design defect, that neither outcome is visible. The names
also say that a `worktree` entry already existed when `worktree1` was made at 12:02 UTC (Git
suffixes the basename on a collision); that is consistent with the first leak having persisted
from 10:43 UTC, and is not evidence of more.

Not many runs leak: the full suite runs the fixture on every gate, and the shared `.git` holds
only these two stale entries, so the normal exit works. The leak needs an abnormal one.

## Severity: the reasoning

LOW, as named. No result is wrong: the stale entries are not read by any later run, and a
fresh `git worktree add` picks a new name (as `worktree1` shows). It is not lower because the
side effect is on a **shared** `.git` that a running gate's pytest also uses, and the repair
(`git worktree prune`) writes to that same `.git`, so it has to wait for a quiet window (the
maintainer's entry orders it after SL-1455's GATE END). The count grows by one per abnormal exit.

## Disposition

**Fix with an owner: WK-1178**, in a small slice (the lead places it in the next D batch).

**Amended 2026-10-16 (BST), before this finding merges, on the maintainer's entry "2026-10-16
10:30:57 BST" in `channel/to-lead.md`.** The first draft of this section preferred a clone and
offered `check=True` only as a second, lesser option, and the entry corrects that ordering. The
requirement is now stated as a property of the fix and not as a choice of design:

> **The fix must make a failed `git worktree remove` visible.** `check=False` is what swallowed
> it (`tests/test_doc_id_migrate.py:190-192`). A prune added to the fixture is not enough on its
> own: it would clean up after a silent failure and leave the failure still silent.

Two remedies satisfy it. Either is acceptable; the slice records which it chose and why.

1. **Keep the worktree and make the teardown loud.** Run `git worktree remove --force` with
   `check=True` inside the `finally`, so that a non-zero exit is raised and not dropped, and keep
   `shutil.rmtree(tmp, ignore_errors=True)` in an inner `finally` so the temporary directory is
   still deleted when the removal raises. **Or**, in place of `check=True`, assert after the
   teardown that `git worktree list --porcelain` no longer names the worktree path, which also
   catches a removal that exits 0 and leaves the entry. A `git worktree prune` at the start of
   the fixture may be added as a clean-up of earlier leaks, **never as the only change**. This
   remedy still writes to the shared `.git`, and still leaks when the process is killed before
   the `finally` runs; the loud teardown makes the first of those visible, not the second.
2. **A clone, as `scripts/doc-id.py:163-166` does,** `git clone --no-checkout --local ROOT
   <tmp>/clone`, then `git -C <tmp>/clone checkout --detach <sha>`, with `shutil.rmtree` of
   `<tmp>`. A clone owns its object store, so no admin entry reaches the real `.git`, and a
   killed run leaves only a directory under `/tmp`. **This is acceptable only if the slice shows
   it also cannot leave an admin entry:** the proof run below must print nothing from
   `git worktree prune -n -v` after a killed run, and the fixture must not call
   `git worktree add` anywhere.

**Creation date, recorded as already corrected.** The maintainer's entry "2026-10-16 10:30:57
BST" withdraws the date "2026-10-16" given in its 10:26:42 entry: it was read from `ls -ld` on
`.git/worktrees/<name>`, which is the directory's modification time. The two entries were created
on 14 Oct, as Evidence 1 above already records from the `gitdir` files' birth times (10:43:49 UTC
and 12:02:51 UTC). The ruling is unchanged: prune after SL-1455's END, plus this LOW finding.

**Proof, on a deliberately broken input (CLAUDE.md §13):** run the four tests (through the
small-run script), once normally and once with the process killed during the run; then
`git worktree prune -n -v` prints **nothing**. Before the fix the killed run must be shown to
leave an entry, so that the check has printed a failure at least once. **Added by the amendment
above:** for remedy 1 the proof also needs a deliberately failing removal (for example, make the
worktree path unremovable or the `git` call exit non-zero in a test double) and must show that
the fixture now **raises** where the draft's `check=False` returned silently; a fix whose
teardown cannot be made to fail loudly on broken input has not shown it is visible.

**The event that next discharges this finding:** the merge of that slice, with the proof run
recorded in its ledger. Until then the lead's `git worktree prune`, after SL-1455's GATE END,
clears the two entries read here, and `git worktree prune -n` printing nothing is its check.

**Not in this finding.** The pruning itself (the lead's, after GATE END), any change to
`_PRE_MIGRATION_SHA` or to what the four tests assert, and the other worktrees under
`.claude/worktrees/` (which `git worktree list` reports as live).
