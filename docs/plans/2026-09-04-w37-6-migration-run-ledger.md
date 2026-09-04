# W37-6 migration run — ledger

Opened 2026-09-04 by the lead, per the deputy's instruction of 2026-09-04 08:56Z
(`~/gi-pricing-plan.local/channel/to-lead.md`, under the maintainer's delegation of
2026-09-03): every "record it in the ledger" line since Ruling 105 D2 had no target file to
land in. This is that file. Pre-migration naming (`docs/plans/README.md`); it becomes an
`LG-` document at the run itself.

Held by the lead until the run's own executor exists (NT-0019 §1.6); executors append per
task and per PR from here forward.

## Go-ahead conditions, as they stand at 2026-09-04

1. `python3 scripts/doc-id.py migrate --verify` exits 0 at a quiet tree (no open PR touching
   `docs/` or the migration scripts).
2. `/` (root disk) has ≥ 4 GB free.
3. `/tmp` (tmpfs) has ≥ 1 GB free.
4. `(h4)` is measured at the migration PR itself, not the pre-flight snapshot — see the D2
   entry below.

None of the four is met yet: `--verify` still reports real residue (row `(g)`'s
class-6/DP-7/citation-engine defects, row `(b)`'s allocation regression, row `(e)`'s
remaining violations); conditions 2–3 are currently met (see the disk entry below) but are
re-checked at run time, not banked in advance.

## 2026-09-04 — disk condition, corrected

The window's original 2026-09-03 `/tmp`-only go-ahead line named a RAM filesystem
(`/tmp` is tmpfs), not the disk that every worktree and the run's own checkout live on.
Corrected and superseded by: **the window opens with ≥ 4 GB free on `/` and ≥ 1 GB free on
`/tmp`** — both named, neither substituting for the other.

Measured before cleanup: `/` 2.5 GB free (92% used); `/tmp` 7.9 GB size, 1.6 GB free (80%
used, unaffected by worktree cleanup since it is RAM).

Cleanup: 14 worktrees belonging to finished agents removed (`git worktree remove` +
`git worktree prune`), verified individually for uncommitted work and for live-agent
ownership before removal: `wt-rowg`, `wt-verify2`, `wt-verify1`, `wt-h2`, `wt-g`,
`wt-audit`, `wt-h`, `wt-auditor2`, `wt-g2`, `wt-dm2`, `wt-lead-docsyml`, `wt-audit-g`,
`wt-audit-v`, `wt-r102-rebase`. Kept: `wt-dm` (PR #701 still open), `wt-deputy`, and the
five live executors' worktrees.

Measured after cleanup: `/` 4.2 GB free (86% used) — **condition 2 MET**. `/tmp` 1.6 GB free
(80% used) — **condition 3 MET**.

## 2026-09-04 — salvage dispositions

Two worktrees carried uncommitted diffs at cleanup time; neither was discarded blind.

- **`wt-g2`** (`executor-g/d8-alt-rows`, released after #711 merged): 2 files, +121/−5 — the
  `wf-0n` case-form fix (34 `wf-0`, 13 `WF-0` occurrences, a `test_a_prose_wf…` test).
  Committed and pushed as `w37-6-wf-case-fix` (`bb7fc2b`), handed to Task #30 (range/compound
  citation work) as its starting point. Not reviewed or verified by that commit.

- **`wt-rowe`** (`fix/row-e-padded-id-prose-v2`, the stalled first row-(e) executor, no PR):
  4 files, +68/−31. The deputy's disk-cleanup ruling assumed this was superseded by #712
  (rowe2) and could be discarded if so. Checked: diffed the 67 added lines against `main` at
  `c905fbc` (current tip) — **60 of 67 are absent from `main`**. Not a subset of #712.
  Content: `PaddedHit` dataclass with a `seq` field, `_TOKEN_BOUNDARY_RE`,
  `_TRAILING_LOCATOR_RE`, `_in_path_context`, and conjunct-2/3 fixes across
  `scripts/_docid.py`, `scripts/_docverify.py`, `scripts/audit-docs.py`, `scripts/doc-id.py`.
  Committed and pushed as `salvage/row-e-padded-id-prose-v2` (`876548b`) rather than
  discarded. `wt-rowe`'s worktree was kept (not in the removal list).

  **Disposition owed from `rowe2`, per symbol, before `wt-rowe` is removed**: `rowe2` reads
  `salvage/row-e-padded-id-prose-v2` against its own #712 and current branch, and either
  folds what is genuinely missing (with the proof it lacks) into its open row-(e) work, or
  records here why not, one line per symbol (`PaddedHit`/`seq`, `_TOKEN_BOUNDARY_RE`,
  `_TRAILING_LOCATOR_RE`, `_in_path_context`, and the conjunct-2/3 fixes). `wt-rowe` is
  removed only after that disposition lands here.

## `(h4)`'s measurement point — Ruling 105 D2

`(h4)` cannot be measured from the pre-flight snapshot (no venv or pnpm store there). It is
measured by the migration PR's own CI on its exact head — all four workflows green — plus the
executor's local run of `CLAUDE.md` §11's two halves, both recorded here with the head SHA
when the migration PR itself is open. Until then `(h4)` prints `DISCLOSE` with that sentence
in `--verify`'s output, never `NOT MEASURED`.

## Baseline at ledger-opening — `main` at `c905fbc` (PR #714), 2026-09-04 ~10:00 BST

`python3 scripts/doc-id.py migrate --verify`: **5 DISCLOSE, 14 FAIL, 5 PASS over 24 row(s)**.
FAIL: `(b)`, `(d1)`, `(d4)`, `(d6)`, `(d7)`, `(d8)`, `(d9)`, `(d10)`, `(d11)`, `(d12)`,
`(d13)`, `(e)`, `(g)`, `(h1)`. Verdict set **UNCHANGED** against the recorded 14-row baseline
in `scripts/_docverify.EXPECTED_VERDICTS` — no row moved (exit 1, the standing red, not
exit 3). This is the reference point the table below starts from; not a merged-PR entry
itself.

## 2026-09-04 — #701 sequencing, and the census heading refusal

Maintainer's direct priority honoured; deputy's sequencing binds executor slots only. PR
#701 (a rebase-and-land docs fix, no snapshot, no gate beyond CI) was dispatched as a
one-shot task outside the five-executor cap rather than queued behind Task #30 and the
`other`-cause triage.

The `## Ruling 105 D2 — …` heading crash (above) was the census doing its job, not a code
defect: `_check_multi_ruling_files_not_silently_unrecognised` refused a heading it could not
classify rather than guessing, and named the offending line — correct behaviour, not a bug to
route around. Two notes for whoever next touches this area of `scripts/doc-id.py`, not tasks:
headings under `docs/plans/` should never begin with `Ruling <n>` unless the section *is*
that ruling's own record; and `NotImplementedError` as the exception class for this refusal
reads as a code gap when it is actually a corpus condition being reported correctly — a
rename candidate, not a fix.

## 2026-09-04 — post-restart function check: disk, salvage, CI

The machine restarted between 09:22Z and 09:45Z; all five executors died along with the
previous lead session and its watch on this channel. Re-armed a fresh `Monitor` on
`to-lead.md` and worked the deputy's post-restart checklist (`to-lead.md` `:637-652`).

**Disk**, re-measured at 10:2xZ: `/` 6.7 GB free (77% used) — up from the 4.2 GB/86% at the
last cleanup reading, condition 2 still met. `/tmp` (tmpfs) came back empty after the
restart — 32 GB size, effectively 0 used, condition 3 comfortably met.

**Git hygiene after the hard stop.** Two stale `index.lock` files found and removed, both
confirmed unheld (`pgrep -fa git` showed no holder before removal in either case):
`~/gi-pricing-plan/.git/index.lock` (mtime 2026-09-03 22:00Z, in the *shared checkout*) and
`~/gi-pricing-plan/.git/worktrees/lead-ruling105/index.lock` (mtime 2026-09-04 09:40Z, this
worktree's own, predating the restart window). The shared checkout also carried an
uncommitted `scripts/_docverify.py` diff at the first lock's mtime — an abandoned,
pre-`#713` attempt at the same `_TOKEN_BOUNDARY_RE`/`_TRAILING_LOCATOR_RE` fix the
`salvage/row-e-padded-id-prose-v2` branch already carries more completely and more
currently. Not discarded: `git stash push -u` (stash message names the supersession) before
cleaning the checkout back to match `origin/main`, in case anything in it is not already on
that branch — not yet diffed; noted here so it is not lost track of.

**Salvage, the two dirty worktrees the deputy named plus one already-committed one:**
`wt-alloc` (`scripts/doc-id.py`, the (b) allocation work) and
`~/gi-pricing-plan/.claude/worktrees/wt-r105-ruling105` (`scripts/_docverify.py`,
`tests/test_doc_id_verify.py`, the task-key `(d8)` addendum) each committed as-is with
subject `wip(restart): salvaged at <time>` and pushed to their existing branches
(`w37-6-row-b-alloc-fix` `264f6e9`, `w37-6-d8-task-key-disclosed` `21c2566`). `wt-h2b` had
one already-committed, unpushed commit (`2b4c13d`, the DP-7 fix) — pushed to
`w37-6-dp7-frontmatter`. `wt-w376-unit` and `wt-rowe2` were clean, unchanged.

**Tooling / CI:** `gh auth status` and `uv sync --all-packages` verification, and
`gh run list --branch main` for `origin/main`'s CI state, are the next two checks before
dispatch — recorded in the entry after this one once run.

## Merged PRs, from here forward

<One entry per PR merged in W37-6 scope from 2026-09-04 08:56Z onward, each with its number,
title, merge commit, and `doc-id.py migrate --verify`'s verdict-set line at that tree.>

| PR | Title | Merge commit | `--verify` verdict set |
|---|---|---|---|
