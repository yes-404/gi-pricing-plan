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
currently. Not discarded: `git stash push -u` before cleaning the working tree, in case anything in
it is not already on `salvage/row-e-padded-id-prose-v2` — not yet diffed; noted here so it
is not lost track of.

**Correction, 2026-09-04 10:3xZ, per the deputy's read:** "cleaned to match `origin/main`"
overstated it — the shared checkout's working tree is clean, but its local `main` (`HEAD` =
`3dbee20`) is 13 commits behind `origin/main` (`54d610e`); nobody advanced it, and no role
works in the shared checkout so this is harmless, but the line should say what happened, not
what it resembles. The stash above is `stash@{0}` (message: "wip(restart): salvaged stale
shared-checkout diff..."); `git stash list` in that checkout holds **7** entries total — the
other six predate this session and are not this stash.

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
| #701 | docs(skills): git-hygiene — a line number derived from a slice or a filtered stream | `ad51906` | UNCHANGED: 14 (docs-only skill change, no `docs/` or migration-script path touched — does not affect the predicate) |
| #717 | docs(plans): Ruling 105 D7 — eight executors on the upgraded VM, disk-conditioned | `88ecfd0` | UNCHANGED: 14 (a dated append to a ruling record's prose, no predicate code touched) |

## 2026-09-04 — retry-cap breach resolved; §7's data logged for the §14 review

The post-restart catch-up (a forked agent, running `scripts/hooks/retry_cap_hook.py record
--layer slice --id W37-6`) hit a real breach: `slice:W37-6:fix` reached
`delivery-process.core.json`'s cap of 2 (PR #707, PR #711) and a third attempt (PR #715)
refused with a `pending_human_checkpoint`. Not routed around — the fork stopped and
reported it.

**Resolution, per the deputy's ruling** (`to-lead.md`, "the retry-cap breach is real,
historical, and was resolved by the maintainer's Ruling 102"): the checkpoint is cleared —
`python3 scripts/hooks/retry_cap_hook.py clear-checkpoint` (the tool has **no `--evidence`
flag on this subcommand**, unlike `record`; the deputy's instruction assumed one — the
evidence trail lives here instead, per the ruling's own item 3). Evidence for the clear: the
maintainer's Ruling 102 (`4988dca`, 2026-09-03) already re-planned the slice — from a hand
gate + fixed window to the `--verify` instrument + a work list — which is §7's own
`redirect: same_layer_map_plan_or_implement_at_slice`, performed before the hook existed to
see it. PRs #707 and #711 are Implement tasks of that re-planned work list (Ruling 102 §2),
not gate retries; the hook has no `implement` kind, so recording them as `fix` misclassified
a work list as a retry loop. **The two recorded events stay in the state file as history,
annotated here as misclassified — retained, not counted forward.** No further `fix` is
recorded for the pre-run work list; a `slice:W37-6:fix` is recorded only when the run's own
window gate fails after the run starts (Ruling 105 D7: a second in-window failure is a halt
— the cap and the halt rule are one rule).

**§7's actual data, for the §14 phase review** (the cap's own metadata:
`status: instrumented_defaults_not_permanent_governance`,
`revisit_when: one_workstreams_worth_of_data_exists` — W37-6 may be exactly that data
point): three gate re-runs across five pre-run windows on 2026-09-03 (`none=110`, then 36
dangling links, then 391 mangled citations / `audit-docs` 547 failures); one halt with
handover committed first; one replan (Ruling 102, `4988dca`); work-list PRs merged since:
#706, #707, #711, #712, #713, #714, #715, #701, plus this ledger's own #716 (count current
at this ledger entry's time; more will land before the review). **The cap value is not
changed here** — whether 2 is the right number for a re-planned slice's own work list, as
distinct from repeated retries at one gate, is the §14 review's question with this data in
front of it, not a call made in passing here.
