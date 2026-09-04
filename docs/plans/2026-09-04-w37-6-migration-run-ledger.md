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

  **Disposition, delivered by `rowe2` 2026-09-04, committed `005bb69` on
  `w37-6-row-e-doc-id-migration`:**

  - **`PaddedHit`/`seq` field — FOLDED IN, real bug.** `padded_hits`' conjunct-2 loop
    re-located a hit in the cleaned line by *text* match; two same-text occurrences on one
    line (a filename exhibit plus a later bare citation — `document-ids.md`'s own rule-3
    sentence has this shape) collapsed onto whichever the loop found first, wrongly
    excusing a bare violation sitting next to a path-shaped one. Fix: added `seq` (this
    hit's ordinal among same-line matches), re-locate by position instead of text. Red-then-
    green: `test_padded_hits_seq_disambiguates_two_occurrences_on_one_line`.
  - **`_TOKEN_BOUNDARY_RE` — FOLDED IN, real bug.** `<`/`>` were hard boundaries, so the
    token walk stopped at an angle-bracket slug placeholder's opening `<` before reaching
    `.md` — a real filename citation (`PL-01240-<slug>.md`, NT-0019 §1.1 rule 3's own
    shape) misread as prose. Fix: removed `<`/`>` from the boundary set. Red-then-green:
    `test_in_path_context_widens_past_an_angle_bracket_slug_placeholder`.
  - **`_TRAILING_LOCATOR_RE` — no action, already covered.** This branch independently
    fixed the same defect pre-#712 (`ddea0b7`, folded into #712's squash) as
    `_TRAILING_LINE_LOCATOR_RE` — functionally equivalent (strips a trailing `:N`/`:N-M`
    before the extension test, vs. salvage's approach of folding the locator into the
    extension regex itself). Already on `main`.
  - **`_in_path_context` + the bundled conjunct-2/3 fixes** — the two folded-in items above
    are this row's conjunct-2/3 fixes; nothing further found.

  **Why neither latent bug showed in today's `--verify` runs**: the one on-disk example
  with this shape
  (`docs/plans/2026-09-03-w37-6-ruling-103-ef-readings-and-index-placement.md`'s
  `PL-01240-<slug>.md`) survives via conjunct 3 regardless — `PL-1240` names no real plan —
  so both bugs are real but currently unexercised by this corpus. Full reasoning in the
  `005bb69` commit message. `wt-rowe` can now be removed; this disposition is complete.

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
| #716 | docs(plans): open W37-6's migration run ledger | `e38ca12` | UNCHANGED: 14 (this ledger's own history above is its full run — every entry, salvage, and correction landed as commits on this PR before it merged; no predicate code touched) |
| #718 | fix(reporter-cycle): Ruling 106 — 100-word cap, BST-clock ETA, main-move refresh | `a9a733c` | UNCHANGED: 14 (`.claude/**` skill/role/script content only — `reporter.py`, `test_reporter.py`, `reporter.md`, `SKILL.md`, the ruling record — no `docs/**` migration-scope path or predicate code touched). Fourth F49 trailer on this branch (`07ea929`) was amended and force-pushed before merge, root cause fixed the same day (shared vs. per-worktree commit-msg hook, see the F49 entry below); duplicate branch `w37-6-ruling106-work` deleted from origin after merge. |
| #720 | fix(scripts): (g) other-residue triage, docs/ leg — cause3/cause4 named | `dea2c79` | Diagnosis-only (`_residue_cause`/`_residue_cause_table` gains two named causes, no predicate changed) — not independently re-run at merge, `ci-watcher-720` confirmed python/docs/history-policy all green and mergeStateStatus CLEAN. cause3 (57% of tree-wide `other`) and cause4 (genuine forward-migration corruption) both dispositioned to executor-30-2's #30 PR; REDIRECTS.csv determinism owed to h2b as a follow-up (task #24). |
| #719 | docs(plans): ledger — #716/#718/#720 merges, thread-cap ruling, kills, salvage disposition | `0375cda` | UNCHANGED: 14 (this ledger's own continued history — every entry above from the merge of #716 forward is this PR's own commits — plus one `dev-commands` SKILL.md edit, no `docs/**` migration-scope path or predicate code touched). Its own CI was repeatedly cancelled by the lead's own rapid push cadence (`ci-watcher-719` flagged it); merged once pushes paused and it settled CLEAN. |
| #721 | fix(scripts): row (b) — `_compound_token_re`'s missing `\b` fabricated ids and masked (d5)/(d8) | `a2c0afa` | Not independently re-run at merge — CI is the merge gate per this session's own scoping (isolated per-run infra), `ci-watcher-721` confirmed python/docs/history-policy all green, mergeStateStatus CLEAN. `EXPECTED_VERDICTS` re-recorded (b) FAIL→PASS, (d5) PASS→FAIL, (d8) FAIL→REGRESSION — the ratchet working, not a defect. Two local, pre-existing `backend/tests/test_score.py` failures reported by the author (out of branch scope by diff-stat) were not independently confirmed against this exact CI run (`ci-watcher-721` could not reach per-test log detail, token-scope limited) — flagged, not blocking, since CI's overall `success` conclusion is the standing merge criterion. |
| #722 | docs(plans): ledger — #721 merged, #723's ruling, #30 split, DB-exclusivity fix | `205ebc9` | UNCHANGED: 14 (this ledger's own continued history plus the `dev-commands`/`python-test` per-worktree-database SKILL.md edits — no `docs/**` migration-scope path or predicate code touched). `ci-watcher-722` confirmed docs/python/history-policy all green, CLEAN. |
| #726 | fix(scripts): OQ double-allocation — dedup discovery, refuse conflicting REDIRECTS.csv rows | `8c8c177` | Not independently re-run — CI is the merge gate, `ci-watcher-726` confirmed python/docs/history-policy all green, CLEAN. `--verify`: (b)/(c) both PASS, verdict set fully UNCHANGED. |
| #725 | fix(scripts): row (e) padded-id-in-prose — real read+write side-by-side bugs, both fixed | `85a352f` | Not independently re-run — CI green (`ci-watcher-725b`, post-rebase head), CLEAN. `--verify`: row (e)/(f) PASS, verdict set unchanged against the 13-row standing red. |
| #727 | fix(scripts): name three more (g) residue shapes — the third `other`-triage scope | `046576c` | Not independently re-run. **Correction (deputy, 15:0xZ):** `046576c`'s own `main` CI run was `completed/cancelled` — the per-branch concurrency group cancelled it when `1129df0` (#724) landed four seconds later. #727 has no completed run of its own on `main`; the evidence for this commit is `1129df0`'s green run (`gh run list --commit 1129df0`: history-policy/docs/python all `success`), which covers both commits since #724's push carried #727's content forward. `--verify` re-run post-rebase, pre-merge: UNCHANGED: 14, matching the recorded set. |
| #729 | fix(scripts): NT-0019 declared exclusions + announced-slot concurrency enforcement | `18afd90` | Not independently re-run — `ci-watcher-729` confirmed python/docs/history-policy all green, CLEAN, 10m14s runtime. `--verify`: exit 1, matching the 13-row standing red exactly, this branch moved no row. The structural fix for the concurrency-compliance failure class that cost h2b its dispatch today. |
| #723 | fix(scripts): name the code-tree residue by cause — hypothesis 1 killed, four new causes found | `56c0e81` | Not independently re-run — `ci-watcher-723b` confirmed python/docs/history-policy all green (post-rebase head `00935dd`), CLEAN. Row (g)'s code-tree leg of the three-way triage. |
| #724 | docs(plans): ledger — #721/#722 merges, h2b root-cause, DB-exclusivity proof | `1129df0` | UNCHANGED: 14 (this ledger's own continued history, no `docs/**` migration-scope path or predicate code touched). |
| #728 | docs(plans): ledger — #724/#725/#727 merges | `0af63b4` | UNCHANGED: 14 (this ledger's own continued history, no `docs/**` migration-scope path or predicate code touched). `ci-watcher-728` confirmed docs/python/history-policy all green, CLEAN. |
| #731 | docs(plans): ledger — #728/#729 merges | `c462fb6` | UNCHANGED: 14 (this ledger's own continued history). `ci-watcher-731` confirmed docs/python/history-policy all green after settling past three cancelled batches (the lead's own push cadence), CLEAN. |
| #730 | fix(scripts): DP-7 frontmatter gap (Reference/vendored stamps) + REDIRECTS.csv determinism | `e6384d7` | Not independently re-run — CI green (ruff/mypy/import-linter/pytest, specification audit, no-session-links), CLEAN. Rebased once onto a genuine content conflict with #729's own test additions, resolved additively from each side's clean history. Full gate: 3199 passed, tree held still. |
| #733 | fix(scripts): W37-6 unit-record inverse — ranges/compounds/relative-links, cause3/3a/4/6, (d5)/(d8) creation rule | `6c92d55` | Not independently re-run — `ci-watcher-733` confirmed python/docs/history-policy all green, CLEAN. Full gate/verify twice (once surfacing and fixing a real crash bug in the author's own diff before reaching a gate). The single largest PR of the day; discharges (d4)/(d5)/(d8) from the checkpoint-1 table. |
| #732 | docs(plans): ledger — #730/#733 merges, worktree incident, checkpoint-1 real figures | `e3739e1` | UNCHANGED: **13** fatal row(s), matching the recorded set of 13 — run `33888477735` on `docs-w37-6-ledger-cont7`'s `f2885ed` (**correction, deputy 2026-09-04 18:2xZ**: the lead's own entry here previously said 14, a remembered figure from before #725 re-recorded (e), not this run's own printed line — NT-0004 pasted-constant defect, fixed). This ledger's own continued history, no `docs/**` migration-scope path or predicate code touched. CLEAN, confirmed via the exact head SHA's own workflow runs (not a stale rollup) before merging. |

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

## 2026-09-04 — executor count 9/8, a disclosed one-time overrun

`ruling106-impl` was dispatched before the eight-executor cap took effect, on the reading
that infrastructure work (editing `.claude/skills/reporter-cycle/`, not a W37-6 worktree)
sat outside it, the same as a `ci-watcher` or a one-shot. **Corrected by the deputy:** the
cap counts by what an agent *does* — edits repository files in its own worktree, runs the
gate, opens a PR — not by which files it touches; that makes `ruling106-impl` a ninth
executor. Not killed (a task already under way, nothing gained by discarding it for a
number). **Disposition:** the overrun is recorded here, no further dispatch happens until a
merge brings the live count to eight, and it is not repeated — the next infrastructure task
waits for a free slot like any other. Efficiency line reads `9/8 (one-time overrun, this
entry)` until the count drops.

**Resolved 11:05Z:** PR #718 merged (`a9a733c`); `ruling106-impl` confirmed a clean
`git status --porcelain --branch` in its worktree, made no further edits or pushes, and
stood down. Live count back to **8/8**. No dispatch had happened in the interim, per the
disposition above.

## 2026-09-04 — the fourth F49 trailer, root-caused: the commit-msg guard was worktree-local, never shared

`07ea929` (PR #718) carried a `claude.ai/code/session` trailer despite the git-hygiene
hook rule (`47fecaf`) — the fourth such hit tonight. Root cause: the commit-msg guard
installed earlier this session was set with `git config --worktree core.hooksPath`,
which is **per-worktree** config (`extensions.worktreeConfig = true` makes each worktree's
`.git/worktrees/<name>/config.worktree` independent) — it only protected the specific
worktree it was run in (`wt-h2b`, `wt-r105-ruling105`, `wt-rowe2`, `wt-rowg2`,
`wt-w376-unit`, confirmed still active and correctly configured), never any worktree
created afterward. Fixed by installing the hook in the **shared** hooks directory instead
(`$(git rev-parse --git-common-dir)/hooks/commit-msg` — the same physical directory every
worktree of this repository reads unless it has its own override), so every current and
future worktree without a per-worktree override is covered without needing per-dispatch
setup. Verified: `wt-alloc`, `wt-ruling106`, and the three new `(g)` triage worktrees
(`wt-rowg-docs`, `w37-6-other-codetree`, `w37-6-other-residue-triage`) all resolve to the
shared hooks dir with no override; the five worktrees with an existing per-worktree hook
were left as they are (already correctly guarded, redundant with the new shared one but
not conflicting).

## 2026-09-04 — the box is 3x oversubscribed: a concurrency budget, not a lower executor cap

**Reading (mine, 11:08Z, confirming the deputy's 11:1xZ read):** `uptime` — **load average
55.32 / 49.12 / 43.15 on 16 cores** (~3.5x oversubscribed on the 1-minute figure). The
deputy's own reading at 11:1xZ: 48.1/47.0/42.1, 25 `pytest` processes and 13
`migrate --verify` runs live at once; RAM 41 GB free, tmpfs 27 GB free, `/` 5.7 GB free —
memory and disk are fine, CPU is the bottleneck. My 12:0x entry (relaying verify105's
status) had read this as restart-recovery load; the deputy corrected it: it is eight
executors each running a full gate plus a `--verify` snapshot at once, spending the
capacity the eight-executor cap (Ruling 105 D7) was given on contention rather than on
work — every gate now takes three to four times its CI duration.

**Ruled — a concurrency budget, enforced by a lock, in every dispatch from now
(authority: the maintainer's "watch the efficiency" instruction of 2026-09-04, relayed by
the deputy):**
1. At most **4** full local gates at once, at most **2** `migrate --verify` runs at once —
   `flock` on numbered slot files under `/tmp/slots/` (`mkdir -p /tmp/slots`, tmpfs, resets
   on restart by design): `for i in 1 2 3 4; do flock -n /tmp/slots/gate-$i -c '<cmd>' &&
   break; done`, blocking fallback `flock -w 3600 /tmp/slots/gate-1 -c '<cmd>'`; the same
   pattern with two `verify-$i` slots.
2. Iterate on targeted tests (`pytest <file> -k <symbol>`) while working; the full
   `CLAUDE.md` §11 gate runs **once**, before push; `--verify` runs **once** per push, not
   per edit.
3. `ci-watcher` stays the CI half; local runs only prove readiness before push.
4. The executor cap stays **eight** (Ruling 105 D7 unchanged) — this budget shapes *when*
   they compute, not how many exist.

**Action taken 11:08–11:1xZ:** `/tmp/slots/` created; all eight live executors (h2b, alloc,
executor-30-2, rowe2, verify105, triage-docs, triage-code, triage-other) messaged directly
with the four rules and the exact `flock` commands, told to let any in-flight full
gate/`--verify` run finish rather than kill it, and to apply the budget from their next run
onward. verify105 specifically flagged: its stuck full-pytest wait (reported 11:01Z, ~16%
through under the same contention) is this cause, not restart recovery — told to keep
waiting on the current run but wrap any future rerun in a gate slot.

From here, every efficiency line in this ledger and in `to-deputy.md` carries a fourth
number: **load average / core count** alongside the executor count.

*Violations this closes off going forward: a dispatch brief without the slot lock; a full
gate run per edit; a `--verify` per edit; a load figure reported without the core count
beside it.*

## 2026-09-04 — correction: no duplicate `pytest` sessions found; the real driver is per-process thread fan-out

The deputy's 11:2xZ instruction to kill "duplicate" `pytest` sessions (citing 7 in
`wt-rowe2`, 32 total) was checked before acting, per this doc's own §13 rule ("verify the
claim, not just the citation"): `ps -eo pid,args | grep '/\.venv/bin/pytest'` (the real
binary path, not a bare string match) found **four** real pytest processes, **one per
worktree, no duplicates anywhere** — `wt-h2b`, `wt-r105-ruling105` (verify105), `wt-rowe2`,
`w37-6-other-residue-triage`. A bare `pgrep -fa pytest` returns 29 hits; 19 are
`until/while … pgrep -f pytest … sleep` wait-loop wrappers (0% CPU) whose own argv contains
the string "pytest" — a self-match on the probe, not a second real session. No `pkill` was
run: rule 1 had nothing to act on.

The real driver: each of the four real processes carries **~150 threads** (`ps -o nlwp`)
and 400–470% CPU — one run's own thread-pool fan-out, not parallel launches. Four such
runs alone approach 16–19 CPU-cores' worth on this 16-core box even with zero duplicates
and full compliance with "one session per executor." Flagged to the deputy as an open
choice rather than decided here: lower the gate-slot cap (4→2) or cap the test run's own
thread pool (source not located — would need a targeted grep/executor, not done as part of
this read). Recommended letting the four in-flight runs finish (34–42 min in already; no
duplicate to kill so the earlier "let it finish" instruction still applies cleanly) and
ruling the slot cap down for future dispatches.

## 2026-09-04 — (g) `other`-residue triage, docs/ leg (PR #720): cause3 is the dominant cause tree-wide

`triage-docs` sampled 10 of the docs/-tree's 205 `other`-residue files against the real
`redirects_inverse` map (not pattern-matched from the raw diff) and named two new causes in
`_residue_cause`/`_residue_cause_table` (`scripts/_docverify.py`), diagnosis-only, no
predicate changed:

- **`cause3-legacy-path-citation`** (6/10 sampled) — a prose citation to another doc by its
  pre-migration relative path; the forward sweep resolves it, DP-7's inverse can't (built
  only from `REDIRECTS.csv` id columns, never a path string). **Whole-tree re-measurement:
  202 of the prior 355 `other` residue (57%) reclassify under this cause alone** — the
  dominant cause tree-wide, not just in docs/.
- **`cause4-compound-token-adjacent-uppercase`** (1/10) — a genuine forward-migration
  corruption bug, not a citation-diagnosis artifact: `doc-id.py`'s `_compound_token_re` has
  no trailing `\b` (unlike `_whole_token_re`), so a bare `W<n>` token prefix-matches inside
  an unrelated identifier (`"W3C/..."` → `"WK-944C/..."`). Invisible to g1's own
  `MANGLED_CITATION_RE` (scoped to FR/NFR/OQ/DEP only). 10 files whole-tree.

Two findings reported in prose only (docs/README.md's bare-basename citation shape; an
un-allocated placeholder id in the psi-selector pair) — correctly not turned into detectors
per this row's no-second-tree-read rule.

**Bonus finding outside triage-docs's own scope, flagged not fixed:** `docs/REDIRECTS.csv`
is correctly in `MigrateResult.generated_paths`, but two independent `migrate()` runs from
the same input produce different row *order* for its compound-citation section — fails
class-6's content-equality check despite being a legitimate generated artifact. The
module's documented byte-identical-across-independent-runs guarantee does not hold for this
one file. Not actioned here — belongs to whichever executor next touches class-6 or
`REDIRECTS.csv` generation.

Gate: ruff/mypy/lint-imports/audit-docs.py clean, 285 passed/1 skipped, two new
broken-input tests (cause3, cause4, negative control on `W6a`). `ci-watcher-720` dispatched;
merges on its green report.

## 2026-09-04 — concurrency budget, final form: thread-cap env vars, gate slots 3 / verify slots 2

Deputy's own re-read confirmed the prior entry's correction (no duplicate sessions; that
rule is withdrawn) and, checking by real binary the same way, measured the actual driver
precisely: inside one gate's `pytest` process — 98 threads the suite's own Python pools
(expected), **16 `tokio-rt-worker` + 16 `async-executor-`** (Polars/DuckDB, sized to
`nproc`) plus jemalloc/Polars threads, **no thread-cap variable set** in the process
environment (`OMP_*`/`POLARS_MAX_THREADS`/`RAYON_NUM_THREADS`/`TOKIO_WORKER_THREADS` all
absent) — every native runtime assumed it owned the box.

**Ruled and actioned 11:1xZ:**
1. `POLARS_MAX_THREADS=4 RAYON_NUM_THREADS=4 TOKIO_WORKER_THREADS=4 OMP_NUM_THREADS=4
   OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4` exported before every gate and `--verify` run.
   Written into `.claude/skills/dev-commands/SKILL.md` (this session, commit `5d39fb7` on
   this branch) with the measurement as its reason, `Verified` date refreshed.
2. Gate slots **3** (was 4), verify slots **2** (unchanged) — `/tmp/slots/gate-{1,2,3}`,
   `/tmp/slots/verify-{1,2}`.
3. All 8 live executors re-messaged with both changes; the three in-flight uncapped gates
   (h2b, verify105, rowe2) told to finish rather than restart (sunk cost — 37–45 min in).
4. Efficiency line now carries **real `pytest` binaries running**, counted by
   `ps -eo pid,args | grep '[/]\.venv/bin/pytest'` (never a bare string match) — at 11:16Z:
   **4** (`wt-h2b`, `wt-r105-ruling105`, `wt-rowe2`, `wt-alloc` — the last a `--collect-only`,
   near-zero cost), **load 62.65/58.28/50.16 on 16 cores**, still climbing (the three
   uncapped gates have not yet finished). Re-measure once they exit and the cap is live for
   whatever runs next.

## 2026-09-04 — PR #720's findings ruled: cause3/cause4/placeholder-id all fold into #30; REDIRECTS.csv determinism owed to h2b as a follow-up

Deputy ruled #720 mergeable on its watcher's report (diagnosis-only, no predicate moved).
Its four findings dispositioned, each with a verified locator:

- **cause3** (202/355 `other`, 57%) — `doc-id.py:692`'s `_REDIRECTS_FIELDS` already carries
  `old_path`/`new_path`/`citing_dir`; no new mechanism needed. Folded into executor-30-2's
  existing #30 unit-record-inverse PR: read the path columns directly for every path-shaped
  substitution, plus the `citing_dir`-scoped bare-basename form (absorbs docs/README.md's
  bare non-rooted citation finding too — no separate class). Proof owed: one real
  `docs/notes/…` prose citation inverting to merge-base bytes.
- **cause4** (`W3C/OpenTelemetry` → `WK-944C/OpenTelemetry`, 10 files) — `doc-id.py:5484`'s
  `_compound_token_re` has no trailing boundary, unlike `_whole_token_re` (`:5393`); Ruling
  102 §2(g)'s own rule, simply unapplied to the second regex. Folded into #30: add
  `\b(?![-/][0-9])`, extend `MANGLED_CITATION_RE` for the `WK-\d+[A-Za-z]` shape. Proof
  owed: `W3C/OpenTelemetry` fixed, `W6a` (real lowercase slice suffix) untouched.
- **Placeholder id** (`OQ-DATA-11` → `OQ-8471`, no `REDIRECTS.csv` row) — Ruling 100(iv): an
  unresolved-target citation is listed, not rewritten. Folded into #30: `token_map` excludes
  keys whose target was never discovered; such tokens join the unmapped-token table
  (`:310`). Proof owed: an undefined `OQ-XXX-n` fixture comes out unchanged and listed.
- **`REDIRECTS.csv` row-order non-determinism** — separate defect, **owner: h2b
  (executor-h2), after its current #29 (DP-7) PR merges**, same file family. Fix: sort rows
  by `old_id` then `old_path` before writing. Proof owed: two independent `migrate()` runs
  byte-identical.

Both executors messaged with their scope at 11:1xZ. `ci-watcher-720` still watching (python
workflow in progress at last check); merge on its report, unchanged from the prior entry.

## 2026-09-04 — the slot mechanism was prose, not a real wrapper: killed and restarted the three legacy gates

Deputy's 11:5xZ read: load 94/74/58 on 16 cores; every real `pytest` binary's parent was
`uv run pytest -q`, never `flock` — `/tmp/slots/` had no files. My earlier messages to
executors described the mechanism in prose; nobody actually ran the wrapped line. Ruled:
the wrapped command is the only gate command from now (dispatch briefs carry it verbatim,
executors do not compose it), and the three uncapped legacy gates (`wt-h2b`,
`wt-r105-ruling105`, `wt-rowe2`) are killed and restarted under it now — the one case where
"let it finish" is withdrawn, since 44–52 minutes at ~4.5 cores each will not finish before
a capped restart does.

**Actioned 11:22Z:** all three messaged with `pkill -P <their real pytest's parent pid>` and
the exact wrapped command (copy-verbatim, not composed):
```
gate_cmd='POLARS_MAX_THREADS=4 RAYON_NUM_THREADS=4 TOKIO_WORKER_THREADS=4 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 uv run pytest -q'
got=0
for i in 1 2 3; do flock -n /tmp/slots/gate-$i -c "$gate_cmd" && { got=1; break; }; done
[ "$got" = "0" ] && flock -w 7200 /tmp/slots/gate-1 -c "$gate_cmd"
```

**Found while checking: rowe2 had TWO real pytest binaries running concurrently**
(PID 47248, 45+ min old; PID 195340, 67s old, parent chain `timeout 2400 uv run pytest -q`)
— a genuine duplicate this time, not a self-match on wrapper argv (checked by real binary
path both times, per the earlier-established predicate). Told to kill both and explain the
cause in its reply.

**Correction flagged to the deputy, not actioned unilaterally:** the two runs read as
"capped" (`w37-6-other-residue-triage` 240% CPU, `wt-alloc` 178%) have **no thread-cap env
vars set either** (`/proc/<pid>/environ`, checked directly) — their lower CPU reading is
more likely because they are earlier in the run (5 and 4.6 minutes in respectively) than
because a cap is active. Not killed: the deputy's kill instruction scoped to the three
named gates specifically; this is reported for a ruling, not acted on alone.

CPU-demand figure (sum of `%CPU` over the six real gates ÷ 1600, i.e. ÷16 cores × 100):
(432+397+370+251+210+186)/1600 ≈ **1.15** — mildly oversubscribed by actual CPU-seconds,
much less dramatic than the load-average figure (82) suggests; load average also counts
runnable/blocked threads from the ~150-thread pools, not CPU demand alone, matching the
deputy's own point.

**Root cause of the `wt-rowe2` duplicate, from rowe2 itself:** not a second manual launch —
its own `gate-runner` subagent lost track of its backgrounded `pytest` run and reissued the
command, three times total across the incident (10:36 uncapped original; ~11:20 a second
`timeout 2400 …`; ~11:24 a third `timeout 3600 … -x -q`, started after the stop instruction
had been sent but before it reached the subagent's next tool round). All three killed and
confirmed gone. Now exactly one `pytest` running, flock-guarded (`gate-{1,2,3}`,
`-w 7200` fallback) and thread-capped, verified against `/proc/<pid>/environ` directly
(not merely the wrapper shell's exported values) — the process itself carries all six
vars. The rest of that gate (ruff/mypy/lint-imports/audit-docs/req-coverage/
generate-contracts --check, full frontend half) had already exited 0 before the stop;
only `pytest` was affected by the subagent's own retry behaviour. A `gate-runner`
subagent that backgrounds a long test run without tracking its own pid is a defect worth
a general note if it recurs elsewhere — not actioned further here, single incident so far.

## 2026-09-04 — the rule has no age exception: h2b's legacy run never actually died; alloc/triage-other/rowe2 restarted uncapped or unslotted

Deputy's 12:0xZ table (real binary, `/proc/<pid>/environ`, parent chain, all five): my
"two capped" correction accepted, and my own "may finish before ramping up" leniency
toward `wt-alloc`/`triage-other` withdrawn too — a young uncapped run ramps to ~4.5 cores
at its first native call; the compliance predicate has no age clause, so neither does the
rule. `wt-r105-ruling105` (verify105's restart) is the model: capped, `flock` parent,
confirmed. Everything else was not:

- **`wt-h2b`: the kill I ordered never happened** — PID 20636 still alive at 57+ min,
  uncapped, `uv run pytest` parent, confirmed directly at 11:25Z before re-sending.
  Re-sent as urgent, asked for an immediate kill confirmation separate from the restart.
- **`wt-alloc`, `w37-6-other-residue-triage`**: both uncapped, no `flock` parent, 7–9 min
  in. Told to kill and restart under the literal wrapped line, no exception for youth.
- **`wt-rowe2`**: the post-root-cause restart has the cap env set correctly but its parent
  is bash, not `flock` — capped without being slotted. Told to kill (cheap, ~40 s in) and
  restart fully wrapped.

Slot files now exist (`gate-1..3`, `verify-1..2`) for the first time — the mechanism is
real, just not yet uniformly applied. Deputy's post-kill reading: CPU demand 0.69, load 64
and falling. Efficiency line from here counts real gates by `%CPU > 20` (the sleeping
`--collect-only` binaries per worktree are not duplicates, per the deputy's clarification).

## 2026-09-04 — the lead killed two runaway process trees directly, on the deputy's explicit ruling

`wt-h2b`'s legacy gate (PID 20636) was still alive at 59 min after three messages to its
owner. Deputy diagnosed why: h2b's own agent was blocked inside the 60-minute foreground
`uv run pytest` call itself — it cannot read its message queue until that call returns, so
a fourth message would have changed nothing. Ruled: the lead kills the process tree
directly (dispatch operations on a worktree the lead dispatched, not executor work per
`lead.md`'s "never implements") so the agent's foreground call returns and it can act on
the queued restart instruction on its next turn.

**Actioned, verified both directions:**
- `pkill -P 20622` (the `uv run pytest -q` parent of PID 20636); confirmed
  `[ -d /proc/20636 ]` false, `[ -d /proc/20622 ]` false, and
  `ps -eo pid,args | grep '[/]wt-h2b/.venv/bin/pytest'` empty.
- `wt-rowe2`'s restart was still flock-less (cap env correctly set, parent `bash` not
  `flock`, 239 s old) at the same check — per the deputy's "same for rowe2 if not fixed by
  your next entry," killed the same way: `pkill -P 207976`; confirmed `/proc/207979` and
  `/proc/207976` both gone, no `wt-rowe2` pytest binary remains.

Not restarted by the lead — that is the owning agent's own next action once its queue
unblocks, per the same ruling.

## 2026-09-04 — rowe2's second flock-less restart traced to an incomplete instruction, not agent error

Deputy's 12:3xZ read: `wt-alloc` and `w37-6-other-residue-triage` both correctly
`flock`-parented and capped; `wt-rowe2` capped but parent `bash` again, 37 s old — the same
shape as the run already killed once. Verdict: an agent producing the same non-compliant
restart twice is following its brief, not malfunctioning. Root cause found: my message to
rowe2 wrapped only `uv run pytest -q` in isolation, not the full chained gate command
(`ruff && mypy && lint-imports && pytest`) its `gate-runner` subagent actually issues as one
shell call — the partial line didn't compose into that shape. Fixed: sent rowe2 the
complete canonical block from `.claude/skills/dev-commands/SKILL.md` verbatim (all four
gate steps under one `flock`, thread-capped), asked it to echo back the exact command
string executed for verification rather than a paraphrase.

**Efficiency line** (real gates by `%CPU > 20`, per the deputy's predicate): three —
`wt-alloc` (compliant), `w37-6-other-residue-triage`/triage-other (compliant), `wt-rowe2`
(non-compliant, fix just sent). **Between gates:** `h2b` (no real pytest process; message
landed after the kill, no restart observed yet — likely still on ruff/mypy/lint-imports
before reaching pytest, or hasn't started); `verify105` (no real pytest process — its capped
restart was last seen at 76%/~11min, likely finished; no report received yet);
`executor-30-2`, `triage-code` (no real pytest process at any point this session so far —
still on their non-gate work, no report yet). Load 6.68/5.53/15.57, CPU demand
(78.2+92.0+131)/1600 ≈ 0.19 — consistent with the deputy's under-used reading.

**PR #719 (this ledger PR) merged** at `0375cda` once its own CI settled — the lead's rapid
push cadence had been cancelling its runs (`ci-watcher-719`'s finding); merged clean once
pushes paused. Continuing on a fresh branch (`docs-w37-6-ledger-cont2`) since the merged
branch is gone.

## 2026-09-04 — row (b) fixed (PR #721): the missing `_compound_token_re` boundary was fabricating ids AND masking real (d5)/(d8) defects; same fix collided with #30's cause4

`alloc` root-caused row (b)'s `noncontiguous=4`: #711's `_compound_token_re` (compound-
citation expansion) dropped the trailing `\b` that `_whole_token_re` already carries, so a
shorter mapped legacy id matched as a bare prefix of a longer unmapped one sharing the same
leading digits (digit→digit is never a `\b` transition). `OQ-OVR-1` (→`OQ-831`) swallowed
`OQ-OVR-11` (correctly excluded, ambiguous), leaving the orphan digit:
`OQ-OVR-11` → `OQ-831`+`1` = fabricated `OQ-8311`. Seven ids fabricated this way, collapsing
to the four `noncontiguous` gap boundaries. Fix: one `\b` added, broken-input proof both
directions.

**Collision, caught before landing:** this is the identical defect and identical fix as
PR #720's cause4 finding, dispatched to executor-30-2's #30 PR. Told executor-30-2 to stop
before duplicating it — either drop cause4 entirely and rebase on #721 once merged (keeping
only the `MANGLED_CITATION_RE` extension for the `WK-\d+[A-Za-z]` shape, which alloc did
not touch), or reconcile if it had already implemented the boundary fix differently.

**Serious finding, flagged for the deputy's ownership call, not actioned here:** the same
boundary bug was also silently corrupting (not migrating) citations in the space-separated
`Ruling <n>` and `W<n>-<n>` families — masking real defects in rows (d5) and (d8) rather
than fixing them. Correcting the boundary un-masks the real, larger populations: **(d5)
PASS→FAIL (75 instances)**, **(d8) FAIL→REGRESSION (2513, now above the pre-migration
control of 2358 — worse than before migration ever ran)**. Neither row has an owner right
now. `EXPECTED_VERDICTS` updated for all three moved rows (b, d5, d8) by alloc, contrary to
the original dispatch brief's "no verdict-set change needed" — verified empirically: with
the update `--verify` reports `UNCHANGED: 14, matching the recorded set`; without it, an
unexplained `SET CHANGE`, exit 3.

**rowe2's flock status corrected**: the deputy's "flock-less" read on `wt-rowe2` was itself
a self-match artifact — checked directly by tracing the real `pytest` binary's `ppid` chain
(not a `pgrep -f` scan): PID 310678 ← `uv run pytest -q` ← the thread-capped `bash -c`
← `flock -n /tmp/slots/gate-2` ← the slot-selection wrapper — genuinely compliant,
holding gate-2. Not killed. rowe2's own diagnosis (its idle wait-loop's `pgrep -f
"wt-rowe2/.venv/bin/pytest -q"` argv matches the same string a naive check greps for) is
the same self-match class recorded earlier this session — worth a durable note if this
pattern recurs a third time.

Gate on #721: green both halves except two pre-existing `backend/tests/test_score.py`
failures (confirmed out of scope — `git diff --stat origin/main...HEAD` touches only
`scripts/_docverify.py`, `scripts/doc-id.py`, `tests/test_doc_id_migrate.py`). `--verify`:
row (b) PASS, verdict set fully reconciled. `ci-watcher-721` dispatched.

## 2026-09-04 — three silent executors pinged; four finished worktrees released

Deputy's 12:5xZ read flagged three executors past the 20-minute idle line with no real
gate running: `wt-h2b` (33 min, no gate since the kill), `wt-r105-ruling105`/verify105
(18 min, task-key addendum committed but unpushed, no PR), `w37-6-other-codetree`/
triage-code (18 min, 3 dirty, no PR). Confirmed no real `pytest` process for any of the
three before acting. Pinged all three per the standing rule (ping this cycle; if unanswered
with no real gate running, release and respawn fresh from the branch — the branch carries
the work forward).

**Four finished worktrees released**, each verified clean (`git status --porcelain
--branch`) and each branch already merged (remote gone or content matches the merge):
`wt-dm` (#701), `wt-rowg-docs` (#720, one untracked `.venv` directory discarded — a
generated artifact, not work), `wt-rowg2` (#715), `wt-ruling106` (#718). `git worktree
remove --force` + `prune`; `df -h /` 5.6 GB free (was 5.7 GB), `/tmp` 26 GB free.

## 2026-09-04 — #721's regressions ruled: exposed, not caused; (d5)/(d8) go to the unmapped-token table, never back to prefix matching

Deputy confirmed #721's own `EXPECTED_VERDICTS` re-record ((b) FAIL→PASS, (d5) PASS→FAIL,
(d8) FAIL→REGRESSION) is the ratchet working correctly, not a defect — "(b)'s PR does not
touch `EXPECTED_VERDICTS`" (the original dispatch brief) wrongly assumed the recorded value
was already PASS. Merge #721 on `ci-watcher-721`'s report, unchanged from the prior entry.

**Cause4 is fully resolved by #721** — executor-30 drops its own `\b` fix before opening
#30 (already relayed) and rebases; `MANGLED_CITATION_RE`'s `WK-\d+[A-Za-z]` extension stays
(the probe, not the fix, per the deputy's own distinction).

**(d5)/(d8)'s remedy, ruled and relayed to executor-30-2**: the boundary fix stopped prefix
matches that happened to rewrite longer tokens (`Ruling 10` no longer eats `Ruling 102`'s
head; `W11-1` no longer eats `W11-1-3`) — those longer identifiers were never mapped as
wholes; the old prefix rewrite was masking them from the (d) regexes, not fixing them. Fix:
route them through the **unmapped-token table** (`:310`, the same mechanism as the
placeholder-id fix already in #30's scope) — mapped as whole identifiers where a target
exists, disclosed where none does (Ruling 105 A's alias classes). **Never restored via
prefix matching** — an explicit violation if it recurs. #30's scope now: cause3, the
placeholder-id fix, the `MANGLED_CITATION_RE` extension, and the (d5)/(d8) whole-identifier
routing — a real expansion, checkpoint-1 critical since the verdict set moves under #721
regardless of when #30 lands.

## 2026-09-04 — shared-DB test contention is real; CI is unaffected; rowe2 fully cleared; triage-code's uncapped gate no longer live

**verify105 found, and I verified directly against `.claude/skills/python-test/SKILL.md`**:
the suite's session-scoped teardown `TRUNCATE`s the shared Postgres at every pytest
session's end, and two concurrent full-suite runs across worktrees are two sessions on one
database — "that teardown makes two concurrent runs mutually destructive" (skill's own
words, quoted verbatim, confirmed present at that heading). verify105's capped run (PID
202324) came back 2 failed / 3119 passed after finishing in 13m23s (vs. 46+ min stuck
uncapped) — `test_ebm_model_jobs.py`, `test_model_specs.py`, both nowhere near its
`scripts/_docverify.py` diff. Confirmed via the skill's own decisive check
(`git diff --stat origin/main...HEAD -- '*.py' ... backend/ ... scripts/`) that its branch
touches zero backend Python — cannot be the cause — and via the correct guard (`ps -eo
pid,etimes,args | grep -E '[b]in/pytest'`, never `pgrep -af`, which self-matches) that two
other worktrees were executing concurrently at the time.

**Scoped for the record: CI is unaffected.** GitHub-hosted runners get a fresh
Postgres/Redis/MinIO per run (`services:` + the explicit MinIO step) — this contention is a
local-shared-box artifact only. Every merge decision today has been made on `ci-watcher`
reports of CI state, never on an executor's local claim — **no already-merged PR needs
re-examination for this reason.** What is affected: an executor's local pre-push "gate
green" claim is unreliable evidence when made concurrently with another worktree's suite,
producing exactly the false-negative verify105 walked through. Escalated verify105's
proposed fix (a DB-exclusive lock, nested inside the gate-process slots, held only for the
portion of a run that executes tests — collection needs no window, per the skill) to the
deputy as a ruling request; not decided here.

**rowe2 fully cleared.** Deputy's own deeper ancestry trace (three levels up, not two)
confirmed both `w37-6-other-residue-triage` and `wt-rowe2` are compliant — my two earlier
"flock-less" reports on rowe2 are both withdrawn by the deputy as checked-too-shallow, not
by rowe2 being wrong. rowe2's second process (PID 347463) is a targeted multi-file test
run, not a second full gate — correctly uncapped and unslotted per the standing rule.

**`w37-6-other-codetree`/triage-code**: the deputy's non-compliant gate (no cap, no
`flock`, launched directly) is no longer running — checked at 13:0xZ, no real `pytest`
process for that worktree, so nothing to kill. 2 files modified, uncommitted. Sent the
canonical line for its next run and re-asked its status (idle-ping sent one entry ago,
unanswered so far).

## 2026-09-04 — rowe2's own row-(e) fix moved PASS→FAIL, correctly: a second copy of the same bug on the write side, Ruling 103 §1.8's own shape

rowe2's final pre-push `--verify` (one, per the rule) caught a genuine regression, not a
false alarm: `padded_hits`' `seq`-fix (landed earlier from the salvage disposition) stopped
hiding a real violation — `docs/rulings/RL-00290-...md` §5.3 has a `was:`-path exhibit of
`LG-00030` followed on the same line by a bare citation of the same id, the exact
same-line-duplicate shape the fix targets — but the fix only reached the read side
(`_docverify.padded_hits`, row (e)'s check). The write side
(`scripts/doc-id.py::_normalize_padded_citations`, the migration's actual rewriter) carried
an independent, unfixed copy of the identical text-matching bug — Ruling 103 §1.8's "two
implementations of one rule that are never compared are two rules," undischarged on the
write side until row (e)'s move forced the comparison. Fixed (`45d4bdd`): the same
position-based re-location applied to the write side's `repl` closure, red-then-green test
on the exact corpus shape, targeted suite (490 tests) green, ruff/mypy clean.

**A third/fourth full-suite invocation on this branch, each driven by a genuine finding, not
a sloppy rerun** — noted for the record so it doesn't read as contention noise against the
new DB-exclusivity concern above. One more full gate + `--verify`, both under the
flock/thread-cap pattern, before the PR opens.

## 2026-09-04 — PR #723 (code-tree triage, full 504-file reclassification) ruled; residue named end to end

`triage-code` reclassified the whole code-tree residue, not a sample — hypothesis 1 (a
missing marker/docstring form) killed by measurement, every single-token substitution
inverting byte-for-byte. `ci-watcher-723` dispatched; merges on its report.

| Finding | Disposition | Owner |
|---|---|---|
| cause3(a) Work/slice/task keys, 85 files (62% of code-tree `other`) — `W6b-11`→`WK-947b-11`, bare map has no compound | classified-table ruling (`:455-470`): slice/task keys are the disclosed alias class, never rewritten — bare `W6b`→`WK-949`, compound `W6b-11` left whole and listed | executor-30-2, #30 |
| cause3(b) `W3C`/lockfile hashes | already fixed by #721's `\b` boundary (`a2c0afa`) — proof is a fresh-snapshot check that the hash and `W3C` are untouched | executor-30-2 confirms only |
| Lockfiles in the sweep's corpus (`uv.lock`, `pnpm-lock.yaml`, `frontend/pnpm-lock.yaml`) | new scope defect: a lockfile carries data, never a citation (Ruling 67 Part 2's class) — excluded from the sweep and (d) rows by declared entry, alongside `REDIRECTS.csv` | executor-30-2, same PR |
| cause4 fixture corpora, 36 files (`tests/fixtures/docs-ids/**`, `docs-migration/**`) | 2026-09-02 ruling (fixtures exempt by path) extends from the stamp to the sweep — skip the declared roots | executor-30-2, same PR |
| cause5 `scripts/__pycache__/*.pyc`, 4 files | the instrument measuring its own exhaust (`.pyc` created by running `doc-id.py` inside the snapshot) — excluded from the corpus, or `PYTHONDONTWRITEBYTECODE=1` on snapshot invocations | verify105, folds into (d8) |
| cause6 `docs/…` path citations in code, 9 files, incl. a pathlib `ROOT / "docs" / "audit" / "register.md"` join | contiguous forms use the existing path-record inverse; the pathlib-split form listed unmapped, one file not a class | executor-30-2, same PR |
| `Ruling 2c` prose → `RL-153c` (lettered rulings) | a unit-record entry, same mechanism | executor-30-2, same PR |
| `OQ-MODEL-23`/`-24` → `OQ-8623`/`-8624`, `REDIRECTS.csv` holding two rows for `OQ-MODEL-23` | **forward defect, #18 §2's already-ruled fix, never dispatched until now**: the index/allocator read an OQ from the owning spec's §10 only, `open-questions.md` is the mirror (`:368-386`); one draft per OQ, one `REDIRECTS.csv` row per old id (writer refuses a duplicate — that refusal is the proof), rewrite reads the same map the CSV records | **alloc**, new PR, dispatched fresh (its row (b) PR already merged, released) |

**Checkpoint 1 consequence**: with #720 and #723 the residue is named end to end — cause3
legacy paths (57% docs), keys (62% code), fixtures, pycache, lockfiles, paths-in-code, the
OQ double-allocation. Every finding has an owner. The third triage (`rest`) reports against
the same table when it lands.

## 2026-09-04 — #30 split: exclusions/corpus-hygiene are a fresh small PR, not folded into the inverse-record work

Deputy corrected the bundling in the prior entry: the lockfile exclusion, fixture-root
exclusion, and `.pyc` corpus fix touch nothing the unit-record inverse touches, and
bundling three unrelated scope items into one large PR is one long build, one large
review, and one rebase point on the critical path. Split:

- **New executor (`exec-excl`), dispatched now**, one small PR: the three exclusions,
  declared in `scripts/_docid.py` beside `LEGACY_FORM_PATTERNS` so both scripts read one
  constant (Ruling 67 §2), plus the `.pyc`/`PYTHONDONTWRITEBYTECODE` corpus fix.
- **executor-30-2 keeps**: the unit-record inverse and its shapes (paths incl. cause3
  legacy paths, slash compounds, ranges, relative links, lettered rulings), cause3(a)'s
  compound keys left whole/listed, cause6's contiguous path citations — rebases on the
  small PR once it lands (disjoint hunks).
- **verify105's (d8) addendum**: the `.pyc` item moved out, stays a focused small change.

Both executor-30-2 and verify105 messaged with the corrected scope.

## 2026-09-04 — verify105's rebase preserved #721's real (d8) REGRESSION finding correctly; pycache-scope collision caught before push

Rebasing onto `origin/main` (now `a2c0afa`) surfaced a genuine conflict on
`EXPECTED_VERDICTS["d8"]`: #721 un-masked the same `_compound_token_re` boundary bug at
larger scale for the W-family and re-recorded (d8) as REGRESSION (2513 migrated, above the
2358 control). verify105 kept #721's REGRESSION content unedited rather than overwriting it
with its own prior DISCLOSE value — the correct call; a silent overwrite would have reverted
a real finding and false-triggered the SET CHANGE detector on the next `--verify`. Its
task-key/slice-key disclosure logic sits in `_d8_verdict`'s non-creation branch, which
#721's REGRESSION pre-empts — correct but dormant until the W-family fix lands and migrated
drops below control. Tests exercise `_d8_verdict` directly against fixtures, unaffected by
which state the live corpus is in — 6/6 green post-rebase.

**Caught before it shipped**: verify105's branch still carried the `.pyc` corpus fix, which
moved to `exec-excl`'s separate PR earlier this entry-set — a scope-split correction that
crossed in flight with its gate run. Flagged immediately; told to drop it before pushing to
avoid two PRs independently fixing the same corpus-building code.

## 2026-09-04 — row (e) PR opened (#725)

`rowe2` opened PR #725 (`w37-6-row-e-doc-id-migration`, HEAD `45d4bdd`). `--verify`: row (e)
and (f) PASS, UNCHANGED against the recorded 13-row standing red. Gate: Python half clean
(ruff/mypy/lint-imports/audit-docs/req-coverage/generate-contracts --check); frontend half
unchanged since an earlier clean run; `pytest -q` 3121 passed/5 failed/3 skipped/1 xfailed —
all 5 failures in `backend/tests/` matching the shared-DB contention shape (zero backend/
files in this branch's diff, all 5 pass 5/5 in isolation). Two real bugs beyond the salvage
disposition found and fixed along the way (`_TOKEN_BOUNDARY_RE`'s `<`/`>` handling, the
same-line duplicate-padded-token bug on both read and write sides — the write-side instance
already recorded above). `ci-watcher-725` dispatched; merges on its report.

**#725 is also DIRTY** (merge conflict, main moved past its branch point) — the docs-workflow
failure `ci-watcher-725` saw is on an older commit (`aee2783`), not the actual current HEAD
(`45d4bdd`); no CI has run against the real final commit yet, the conflict blocked it.
Rebase requested. Same DIRTY pattern now hit two open PRs (#723, #725) in a row — expected
given how fast `main` is moving through this checkpoint; every open PR from before a recent
merge batch needs a rebase before its CI can run.

## 2026-09-04 — load back to 57: h2b and executor-30-2 running fully non-compliant gates a third time

Routine check at 13:3xZ found six real gates (`ps -eo pid,args | grep '[/]\.venv/bin/pytest'`):
`/tmp/verify-wt1`/`verify-wt2` (`db-proof`'s scratch setup), `wt-h2b`, `wt-oq-dup-alloc`
(alloc's new task), `wt-w376-unit` (executor-30-2), `wt-rowe2`. Load 57.23/50.86/41.06 on
16 cores. Checked env and ppid chain on all four non-`db-proof` worktrees:
`wt-oq-dup-alloc` and `wt-rowe2` both correctly capped; `wt-h2b` and `wt-w376-unit` neither
capped nor `flock`-parented nor on a per-worktree database — bare `uv run pytest -q`,
identical shape to the very first violation this session. Sent both the exact current
canonical two-block command (per-worktree DB setup, then the flock+thread-cap gate) with an
explicit ask for the literal string they're actually running, since this is the third time
the mechanism hasn't landed for h2b specifically and the cause is still unclear.

## 2026-09-04 — prose stopped being enough: killed h2b/executor-30/db-proof, enforcement moves into `conftest.py`

Deputy's fuller table (13:3xZ): `wt-h2b` 397% CPU, no cap, no slot; `wt-w376-unit`
(executor-30-2) ×2, 258%+21%, same; `/tmp/verify-wt1`/`verify-wt2` (`db-proof`) both on the
**default** database — neither had `GIP_TEST_DATABASE_URL` set, so the pair can only be the
negative control, not the isolation proof it was meant to produce. Load 59.5/55/44, CPU
demand 0.95, `/` 4.9 GB free and falling.

**Killed on sight, directly by the lead** (dispatch operations, per the standing exception):
`pkill -P` on h2b's and executor-30-2's `uv run pytest` parents, both confirmed dead;
`db-proof`'s two processes killed the same way. `wt-w376-unit`'s gate had already exited by
the time I checked (no process found) — the deputy's ×2 reading may have caught it near its
own end.

**Root fix, dispatched to `exec-excl` (deputy's assignment, same executor as the
exclusions PR):** the wrapped-line convention fails because it depends on an executor
typing it correctly, and that has now failed three separate times. Moving enforcement into
`tests/conftest.py` and `_docverify.verify` themselves: `os.environ.setdefault` for the six
thread-cap vars (an explicit override still wins, the default is capped), `pytest_configure`
acquires a gate slot via blocking `fcntl.flock` on `/tmp/slots/gate-{1,2,3}` (verify path:
`verify-{1,2}`), and when `GIP_TEST_DATABASE_URL` is unset the conftest derives
`gipricing_<worktree>` and **refuses to run with a clear error** if that database doesn't
exist — never silently falling back to the shared one. A bare `uv run pytest` is then
budgeted and capped regardless of what the executor typed. Proof required: two bare
sessions started together show the second waiting for a slot; a spawned process shows 4
threads for the relevant native runtimes, not ~150; a missing per-worktree DB produces a
clear refusal, not a silent shared-DB run.

`db-proof` told to redo with real, distinct DSNs and report the actual environ lines used —
its prior report is not usable as isolation evidence per the deputy's finding.

## 2026-09-04 — OQ double-allocation fixed (PR #726), and the dispatch brief's own framing was wrong

`alloc` corrected the dispatch before fixing it: `_discover_requirements` only globs
`docs/specs/*.md`, `open-questions.md` is never a discovery source — the "defined twice"
framing was wrong. Real mechanism: `_LEGACY_SPEC_BOLD_RE` is a bare `finditer` with no
anchor to a row's own leading cell, so it matches every bold occurrence of the shape —
citation as well as definition. A real OQ id cited in bold from another requirement's own
prose (`FR-MODEL-88` citing `**OQ-MODEL-23**`) becomes an independent draft alongside its
owning spec's §10 mirror row, each getting a different new number.

**Also caught**: PR #723's snapshot numbers (`OQ-1058`/`-1064`) predate #721 and were
themselves shaped by the fabrication bug row (b) fixed — re-verified against current HEAD,
post-#721, the double allocation is real and independent (`OQ-1060`/`-1066` this time).

**Fix, two layers**: (1) root cause — `_discover_requirements` dedupes by old_token
globally across the `docs/specs/` walk, first occurrence kept (position-independent since
the rewrite is keyed on text); (2) belt-and-suspenders — `_write_redirects` refuses outright
if any old_id resolves to two different new_ids (keyed on `(old_id, citing_dir)` so
legitimate per-directory bare-basename repeats aren't caught). Verified: `OQ-MODEL-23`/`-24`
each get exactly one row now, rewriting consistently including the two code-tree citations
#723 flagged as stuck. Zero old_id conflicts corpus-wide. `--verify`: (b)/(c) both PASS,
verdict set fully UNCHANGED — this fix doesn't disturb the standing-red set, unlike #721's.
Full gate green both halves, 3135 passed/0 errors — the earlier `test_score.py` failures did
not reproduce this run.

`ci-watcher-726` dispatched; merges on its report.

## 2026-09-04 — executor-30-2's fourth non-compliant gate: `GIP_TEST_DATABASE_URL` set to the shared database, not its own

Checked its restarted gate (PID 575452) directly: `GIP_TEST_DATABASE_URL` was set this
time, but to the shared `.../gipricing`, not a per-worktree `gipricing_<worktree>` — plus
still no thread-cap vars, still no `flock` parent. Killed again (`pkill -P` on the parent,
confirmed dead). Sent an unusually literal follow-up: two separate copy-paste blocks with
an explicit ask to echo `$WT` and confirm the gate block ran as one shell invocation, to
try to isolate whether something about how the command is being composed or split is the
actual cause — this is systemic non-compliance, not one-off carelessness, and worth naming
as the class it is (this is why the conftest-level enforcement dispatched to `exec-excl`
matters: it makes this specific failure mode structurally impossible rather than relying on
a fifth correction landing correctly).

## 2026-09-04 — the per-worktree-database fix is empirically proven, both directions

`db-proof`'s full run, both steps, cleaned up after: **negative control** (shared DSN,
confirmed unset via `/proc/<pid>/environ` on both live PIDs) — an asymmetric concurrent
pair (51 tests / 109 tests) reproduced the exact documented symptom:
`test_read_permission_does_not_confer_cancel` failed `403 == 200` at the ~66% mark of the
longer run, exactly when the shorter run's session-scoped teardown fired at 33s — neither
run touched any code. **Proof** (separate DSNs, `gipricing_proof1`/`gipricing_proof2`,
confirmed live via `/proc/<pid>/environ`): the identical two test sets, same concurrency,
both passed clean (51/51, 109/109) with zero failures — including the exact test and the
exact point that failed under the shared DSN. Cleanup verified before dropping (both proof
DBs still showed exactly one `alembic_version` row, no truncation had leaked) and both
scratch worktrees removed. **The fix works, proven, not merely argued.**

## 2026-09-04 — exec-excl caught three real defects in the conftest-enforcement instructions before writing any code

Before implementing the scope dispatched two entries ago, `exec-excl` verified three claims
empirically rather than guessing, since a mistake would affect every executor's gate:

1. `tests/conftest.py` never loads for `backend/tests`/`packages/*/tests` — `pyproject.toml`
   `testpaths` lists them as siblings, not children. Verified directly (a probe print fired
   for one tree, never the other). Corrected to a new root-level `conftest.py`.
2. **Reusing `/tmp/slots/gate-{1,2,3}` for pytest's own internal `flock` would deadlock every
   correctly-wrapped gate run** — the outer wrapper shell holds the lock via its own open
   file description; a `flock()` inside the exec'd pytest child opens a fresh file
   description on the same file and blocks waiting for a lock its own ancestor holds and
   never releases until the child exits. Verified as correct Linux `flock` semantics before
   approving. Corrected to a separate namespace (`/tmp/slots/pytest-gate-{1,2,3}`).
3. `GIP_TEST_DATABASE_URL`/`DEFAULT_TEST_DSN` live in `backend/tests/conftest_db.py`, not
   `_docverify.py` as the dispatch said (a mis-statement on my part — `_docverify.py` is the
   doc-migration snapshot verifier, unrelated to the Postgres test database). Confirmed by
   direct grep. Corrected to `conftest_db.py`.

All three approved after independent verification, not rubber-stamped. Original exclusions
work (lockfiles/fixtures/pycache) already committed (`11256c8`), tests green, gate queued
behind other executors' slots.

## 2026-09-04 — correction to point 2: one lock namespace, announced, not separate

Deputy caught a real problem in what I'd approved: a *separate* lock namespace for the
in-suite `flock` (my earlier fix for exec-excl's deadlock finding) would let three wrapped
gates and three unwrapped ones run at once — six, not three — since each namespace counts
its own independently, defeating the budget. **Ruled: one namespace, announced.** The
`dev-commands` wrapper exports `GIP_GATE_SLOT=/tmp/slots/gate-N` (`GIP_VERIFY_SLOT=…` for
verify) at the moment it takes the lock, before execing the command; the conftest/verify
enforcement acquires from the same set only if that variable is unset — a wrapped run never
double-locks, a bare run is budgeted, the total stays three either way. Relayed to
`exec-excl`, who also owns adding the export lines to the wrapper in the same PR (the
announcement has to exist before the suite can check for it). db-proof's DB-exclusivity
proof is unaffected by this correction — that task is closed.

## 2026-09-04 — PR #727 found (the third/"rest" leg of the (g) triage), also DIRTY

Found directly (no notification reached this session when it opened) — `triage-other`'s
third (g)-triage PR: every `classified-by-none` file not under docs/, tests/, backend/,
frontend/, scripts/, packages/. Measured against row (g)'s own predicate
(`doc-id.classify_migration_diff`) at a fresh `--verify --keep` snapshot, not assumed.
DIRTY like #723/#725 — main moving fast through this checkpoint is now a recurring pattern
across all three (g)-triage legs. `ci-watcher-727` dispatched; rebase requested.

## 2026-09-04 — #725 and #727 both rebased cleanly, self-resolved

`rowe2`'s #725: rebased to `e951cba`, `mergeStateStatus` CLEAN. One purely-additive conflict
in `tests/test_doc_id_migrate.py` (two new test sections landing at the same insertion
point) — kept both, no logic changes. Full re-verification post-rebase: gate green both
halves, `--verify` row (e)/(f) still PASS, verdict set unchanged (the (d5) label reads
REGRESSION only because `EXPECTED_VERDICTS["d5"]` now records FAIL per #721, not a new
move), 5 pytest failures still the same shared-DB-contention signature, confirmed via
`git diff --stat` and isolated reruns. Force-pushed with `--force-with-lease`, confirmed via
`gh pr view` rather than the push exit code. CI restarted fresh on the new head (still
in-flight); `ci-watcher-725b` dispatched to replace the stale pre-rebase watch.

`triage-other`'s #727: rebased onto `205ebc9`, resolved a conflict against #720's cause3
addition — its own `id-path-compound-citation` finding turned out to be the same underlying
shape cause3 already covers more generally; dropped the duplicate label rather than keep a
redundant class, kept its two genuinely distinct findings (new-frontmatter-stamp-no-move,
unmapped-work-slice-key). Targeted tests (83), ruff, mypy clean. Pushed (`4afe5f8`);
re-running `--verify` before considering it settled.

## 2026-09-04 — root cause of h2b's repeated non-compliance: two-hour self-matching wait-loop trap, not carelessness

Deputy found what actually explains four straight non-compliant gates: ten idle wrapper
shells, eight on `until ! pgrep -f 'wt-h2b/.venv/bin/pytest -q'`, two on the equivalent for
`wt-rowe2`, spaced ~600s apart, ages 53min→2h15min. The pattern is in the loop's own
argv, so `pgrep -f` always matches itself and the loop never resolves — h2b's Bash calls
have been timing out every ~10 minutes and it re-issues the identical broken wait, eight
times, never learning whether its gate finished, crashed, or was killed. **A stalled
executor that reads as busy.**

By the time I checked, the ten shells were gone (expired on their own), but h2b's third
non-compliant gate (PID 584454, 677% CPU, 13min, no cap, no `flock`) was still alive —
killed directly. Told h2b the wait-loop pattern itself was the defect (bracket a character
or wait on the literal PID, never a bare name match) and, per the deputy's own point 2, to
stop running local gates entirely until exec-excl's conftest enforcement merges — push and
let `ci-watcher` read CI, which is what actually gates a merge here regardless. Flagged the
same trap to rowe2 as a precaution (two of its own earlier waits had the same shape, though
its work has clearly progressed past it).

**Deputy's counting-predicate correction, for the record**: a real pytest binary has
`comm == pytest`; a wrapper shell has `comm == bash` and merely mentions the path in its
argv — `ps -eo pid,comm,pcpu,etimes,args | awk '$2=="pytest"'` is the census that can't be
fooled by a wrapper. The earlier "ten pytest sessions" reading was the wrapper count,
withdrawn by the deputy before it reached this ledger.

## 2026-09-04 — h2b's fourth bare gate, ~28s after the instruction to run none; last warning before reassignment

Killed PID 668780 (`wt-h2b`, `uv → bash → init`, no `flock`, 984% CPU at 28s of age) —
started within a minute of being told to run no local gates at all. Confirmed clean from
the process table 30 seconds later, per the deputy's instruction ("confirm compliance from
the process table, never from its acknowledgement"), and again at this entry — none
running. Sent h2b the deputy's own threshold explicitly: a fifth bare gate and it is
stopped, its remaining work (#29 DP-7, the `REDIRECTS.csv` sort follow-up) reassigned to a
fresh executor with the canonical line in its brief. Asked `exec-excl` for an ETA on the
conftest enforcement PR — the deputy wants that figure; not yet reported back.

## 2026-09-04 — h2b's fifth bare gate: the threshold is reached, stopped, work reassigned; both of executor-30-2's flagged doubts resolved

Killed PID 680976 (`wt-h2b`) — the fifth bare gate against explicit instructions. Per the
deputy's ruling, h2b is stopped: no further dispatch, session released only once its
subject closes, not its task. Told it directly and without ambiguity. Its work
(`w37-6-dp7-frontmatter`, commit `2b4c13d`, clean and pushed) reassigned to a fresh
executor, **`exec-dp7`**, dispatched with the branch as its starting point, the canonical
gate line verbatim, and an explicit "no local gate until conftest enforcement merges —
push and let `ci-watcher` decide" instruction. It also owns the `REDIRECTS.csv` row-order
determinism fix (task #24).

**executor-30-2's two flagged doubts, both resolved with a direct measurement, not a
comment's story:**

- **OQ-DATA-11**: ran `doc-id.py migrate --verify --keep` against a fresh `origin/main`
  (`85a352f`, post-#726) snapshot myself and read the actual output. `docs/REDIRECTS.csv`
  now carries `OQ-DATA-11,OQ-849,docs/specs/01-data-management.md,...` — a real row, no
  double-allocation, rewritten consistently everywhere including its own struck-through row
  in `open-questions.md`. **#726's dedup fix already fully resolves this case as a side
  effect.** The original "placeholder id, no REDIRECTS.csv row" diagnosis is stale.
  `scripts/_docverify.py:1338-1340`'s comment (which named it an "un-allocated placeholder"
  minting `OQ-8471`) is now doubly wrong — both the characterization and the number — and
  is being corrected as a one-line addition to executor-30-2's PR, since it's already
  touching that file. Item dropped from #30's scope entirely; no mechanism built.
- **"Ruling 2c"**: confirmed false positive by two independent checks now (the earlier
  verification agent, and the deputy's own `git grep -nE '\bRuling [0-9]+[a-z]\b'`, one hit
  — the ledger's own row). Dropped from #30's scope, no citation exists to fix.

Both resolutions relayed to executor-30-2. #30's remaining scope: unit-record inverse,
cause3(a)/cause6, cause4's `MANGLED_CITATION_RE` extension, the one-line stale-comment fix,
and (d5)/(d8) unmapped-whole-identifier routing.

## 2026-09-04 — (d8) ruled: distinct-value creation, not raw count; h2b's sixth gate — stopped for real this time

**(d) alternatives, one creation rule, ruled from executor-30-2's measurement**: creation is
a distinct value present in the migrated tree and absent from the control, on the
alternative's own pattern — any such value is REGRESSION regardless of disclosed-class
status (the mangling/fabrication test, stated on the quantity that measures it). Occurrence
growth with an identical value set is not creation — printed as a per-value disclosure line
(`value control→migrated`), never folded into the verdict. `_d8_verdict`'s first branch
becomes the value-set comparison; the count delta moves to the note. The duplicating
generator is still owed a named cause in the ledger — investigation, not a fix, in the same
PR: which split preamble/title/regenerated index writes the extra occurrences, and whether
that's class 6 (legitimate verbatim quotation) or a partial-edit (g) defect. Relayed to
executor-30-2 in full.

**h2b's sixth bare gate** (PID 695814, 174 threads, no cap, no slot, 8 min old) — running
after the stop instruction had already been read. Killed, confirmed clean from the process
table. Given six violations across explicit stop instructions each time, a message alone
cannot guarantee compliance — **stopped the agent process itself** (`TaskStop`) rather than
rely on a seventh instruction landing. Confirmed, in order: (i) nothing of h2b's runs — `ps
-eo pid,comm,args | awk '$2=="pytest"' | grep wt-h2b` empty; (ii) h2b receives no further
dispatch — its process is stopped, not merely instructed; (iii) the fresh executor is
**`exec-dp7`**, dispatched from `w37-6-dp7-frontmatter` (`2b4c13d`) with the canonical gate
line and the no-local-gate instruction, already in flight.

## 2026-09-04 — h2b's stop confirmed by the deputy's own read; exec-dp7's proof-of-reading owed

Deputy's own table: zero `comm=pytest` under `wt-h2b`, zero `--agent-id h2b@` processes,
load 4.0 — the first fully quiet box today. Gap named: the stop entry required a
proof-of-reading line accompany the reassignment dispatch, and exec-dp7's dispatch went out
without one landing in the ledger. Not a re-dispatch — asked exec-dp7 directly to confirm
it has read `dev-commands` and `python-test` in full (both changed multiple times today)
plus its current progress; its reply will carry the line this entry owes.

## 2026-09-04 — self-caught: #724 was merged before its own PR-branch CI finished

`ci-watcher-724`'s final report showed the `python` workflow still `in_progress` at the
moment of merge (13:05:40Z) — checked directly: `gh run list --branch
docs-w37-6-ledger-cont3 --workflow python.yml` confirms the last real run, on the actual
head `d72a8ba`, started at 13:05:30Z and was still `in_progress`, not `success`, when I
merged. My earlier `gh pr view 724 --json mergeStateStatus,statusCheckRollup` read
`CLEAN`/`set()` — an empty check-rollup rather than a confirmed-passing one — and I read
that as "nothing blocking" instead of "no data, don't trust this." **A process gap on my
part**: I should have confirmed the exact head SHA's own CI via `gh run list`, the way
`ci-watcher` agents are instructed to, rather than trusting `mergeStateStatus` alone when
the rollup is empty.

**No bad content actually landed**: the squash-merge itself triggers a fresh CI run against
the new `main` HEAD (`1129df0`), and that run — `gh run list --commit 1129df0` — is
`history-policy`/`docs`/`python` all `success`, confirmed directly. The merged content is
verified safe after the fact; the gap was procedural (merging before the pre-merge signal
was actually confirmed), not a defect that reached `main`. Recorded so the pattern is named
rather than repeated: an empty `statusCheckRollup` is not evidence of green, only evidence
of no data — read it as unconfirmed, same as the ci-watcher role's own standing rule.

## 2026-09-04 — executor-30-2 caught a crash bug in its own diff before it reached a gate

Confirmed OQ-DATA-11 independently (matches: one `REDIRECTS.csv` row, no conflict) and
fixed the stale `_docverify.py` comment in place with a note rather than a silent delete.
Rebasing onto #726 surfaced a real defect: the first version of cause3's path-citation
extension called `_path_citation_redirect_rows` unconditionally per-draft, including for
drafts belonging to a source that legitimately **splits** into several targets — fine
before #726, but #726's new write-time guard ("one legacy id resolves to exactly one new
id") would have refused the write and **crashed `migrate()` outright** on the first real
multi-ruling split file (`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`, splitting
into `RL-190`/`RL-191`). Caught via a cheap direct `migrate()` call, not the full
`--verify`, before it reached a gate or a push. Fixed two ways: the per-draft extension
moved to the branch already provably 1:1 (`len(destinations) == 1`); the split-source
recording (a genuinely different mechanism — the same citation text legitimately resolving
differently by context) now runs through a new `_drop_contested_split_redirects` helper,
same collision-safe-drop philosophy as the read-side inverse — a genuine ambiguity is
named and excluded, not crashed on. Two new unit tests. 427 targeted tests green. Told to
build (d8) in the same PR rather than split to a follow-up, given how much is already
consolidated here.

## 2026-09-04 — executor-30-2's full scope complete, (d5)/(d8) implemented per the ruling, generator named

`_scan_values`/`_value_set_creation` (new) compare distinct matched values rather than raw
line counts — wired into `rows_d`'s generic branch (every alternative, not just d8) and
`_d8_verdict`. A genuinely new value still regresses unconditionally, checked before any
disclosure; an occurrence-count increase on an unchanged value set is now a disclosure
line, never folded into the verdict. Two pre-existing tests whose fixtures accidentally
introduced real new values had their fixtures corrected (their intent was the mechanism,
not creation); three new tests added. 431 targeted tests green.

**Generator named** (item 3 discharged): `docs/INDEX.md` (19 occurrences) and
`docs/rulings/INDEX.md` (2, doesn't exist pre-migration) — both regenerated-from-scratch
artifacts — account for the growth. Sampled lines confirm each ruling's own **title**
quoted verbatim into its index row, several of which happen to mention `W37-6` in prose.
**Class 6 exactly, the ruling's own first hypothesis — legitimate, no fix needed.**
Cross-checked one real multi-ruling split file directly (control vs. its child, both count
7, no inflation) to rule out split-duplication before landing on the index explanation.

executor-30-2's full scope is now done and tested: unit-record inverse, cause3/3a/4/6, the
stale-comment fix, the split-redirect crash bug it found and fixed mid-rebase, and (d5)/(d8).
Running its one compliant gate + verify before opening the PR.

## 2026-09-04 — exec-dp7's proof-of-reading, owed since h2b's reassignment: confirmed, plus a real gap found in h2b's original fix

**Proof-of-reading, verbatim**: "I read both `.claude/skills/dev-commands/SKILL.md` and
`.claude/skills/python-test/SKILL.md` in full before touching anything — the wrapped
flock+thread-cap gate/verify commands below are copied verbatim, not composed, and I
created a per-worktree test database (`gipricing_wt-h2b`) before the first gate run." This
discharges the gap the deputy named at the h2b-stop entry.

**h2b's original DP-7 commit was real and well-reasoned, but incomplete, not wrong**:
`_this_runs_stamp_id` only recognized "this run's own stamp" via an `id:` field in
`REDIRECTS.csv`'s `new_id` column — but the Reference family (`.claude/roles/`,
`.claude/agents/`, plain `.claude/skills/*/SKILL.md`, every `README.md`) and a vendored
skill manifest are stamped by `migrate` with **no `id:` line at all**, by design (NT-0019
§1.2). Two real regressions surfaced (`test_acceptance_item_g_clean_migration_has_no_violations`,
`test_class6_regenerated_readmes_and_indexes_pass_whole`), pre-existing on h2b's own commit
(verified by isolating the change, not caused by the rebase). Fixed: `_this_runs_stamp_id`
now also confirms via path membership in the caller's own recorded stamp-target set
(`_discover_reference_stamp_targets` + `_discover_vendored_skill_manifests(...).to_stamp`)
when a header carries no id — proven positive and negative (a hand-edit still fails), 5
new/extended tests.

**Second task also done**: `docs/REDIRECTS.csv` row order now sorted by `old_id` then
`old_path` (full-row tie-break) in `_write_redirects` — proven by feeding the same rows in
different orders and diffing bytes identical.

Rebased twice onto moving `main`, both clean, no conflicts. Two commits landed. 510
targeted tests green, 1 skip, ruff clean. Running the one compliant gate + verify now.

## 2026-09-04 — three gates checked, two fully compliant, one on the shared database

Deputy's process-table read of all three live gates: `exec-dp7` (`wt-h2b`) and `exec-excl`
(`wt-exclusions`) both capped, `flock`, on their own per-worktree databases. `triage-code`'s
#723-rebase gate is capped and `flock`-held but has **no `GIP_TEST_DATABASE_URL`** — running
against the shared default database. No collision at this instant, but it's the one gate
the teardown race can still reach; a spurious status-code failure there is the first
suspect, not the code. Told triage-code to create its own database before its next run.
exec-dp7's proof-of-reading line independently checked by the deputy — "copied verbatim"
against the one real occurrence of the wrapped line in `dev-commands`, none in
`python-test` — consistent with what it claimed. The gap is closed.

## 2026-09-04 — PR #729: the structural concurrency fix, plus the pycache mechanism's real root cause

`exec-excl`'s PR covers both the declared exclusions and the full conftest-level
enforcement (root `conftest.py` thread-cap `setdefault` + `GIP_GATE_SLOT`-announced
`/tmp/slots/gate-{1,2,3}` lock skipped for `--collect-only`/targeted runs; `_docverify.py`'s
`verify()` the same for `GIP_VERIFY_SLOT`/`verify-{1,2}`; `backend/tests/conftest_db.py`'s
per-worktree-DB refusal with a remediation message; `dev-commands` gains the
`GIP_GATE_SLOT`/`GIP_VERIFY_SLOT` export lines) — the structural fix for the entire class of
violation that cost h2b its dispatch today.

**Found the pycache defect's real mechanism, not just its symptom**: `migrate()`'s
`_load_module` (both the `doc-id.py` and `audit-docs.py` copies) was writing bytecode into
the snapshot's own `scripts/__pycache__/` while running in-process, which
`_iter_tree_files`'s non-git-aware walk then read back as new migration output — a planted
`.pyc` genuinely registered as unclassifiable row-(g) residue before the fix. Fixed at the
source (bytecode caching suppressed for `_load_module`'s own loads) plus defensively (the
shared exclusion predicate, `PYTHONDONTWRITEBYTECODE=1` on `_docverify.py`'s subprocess).
Also reproduced the lockfile risk for real: this corpus's own `NT-0001 -> RFC-1`
re-citation was getting written into a lockfile comment before the fix.

**All three live proofs demonstrated on this machine's real `/tmp/slots/`**: a wrapped run
announces and the hook takes no second lock (`/proc/<pid>/environ` checked); with all three
real gate slots genuinely busy, a bare probe prints "waiting for /tmp/slots/gate-1" and
actually blocks; the DB refusal fires with the `createdb`/`alembic` remediation message.

Gate green both halves (3192 passed/3 skipped/1 xfailed/0 failed; pnpm 602 passed), `GIP_GATE_SLOT`
confirmed reaching the spawned pytest process. `--verify` under the corrected wrapper: exit
1, matching the 13-row standing red exactly, this branch moved no row. Disclosed a >1-hour
queue wait with edits during that wait, but the tree held still start-to-finish for the
LAST (cited) gate run — `python-test`'s own "tree held still" discipline, applied and
disclosed rather than glossed over. `ci-watcher-729` dispatched; merges on its report.

## 2026-09-04 — #729 merged (18afd90); PR #730 (exec-dp7) found, DIRTY, rebase requested

#729 merged; the structural concurrency fix is live on `main`. Found PR #730
(`w37-6-dp7-frontmatter`, exec-dp7's DP-7 gap fix + REDIRECTS.csv determinism) — DIRTY,
main moved again since its branch point. `ci-watcher-730` dispatched, rebase requested.
Continuing on `docs-w37-6-ledger-cont5` (PR #731) since the merged ledger branch is gone.

## 2026-09-04 — #729 fully verified and accepted: main is now UNCHANGED at 13 fatal rows, one fewer

Deputy's independent verification of #729 against its own ruling — the single namespace
(`git grep -ohE '/tmp/slots/[a-z-]+'` on `main` names no third lock), the announced-slot
export at the right point in the wrapper, `conftest.py`'s unannounced-only acquisition,
`setdefault` capping, `conftest_db.py`'s refusal (not substitution) — all confirmed by line
number against the merged code, both proofs exist as named tests. **The docs run on `main`
prints `UNCHANGED: 13 fatal row(s), matching the recorded set of 13` — one fewer than this
morning's 14.**

**One design refinement, a follow-up not a blocker**: `_is_bare_full_run` currently exempts
any run carrying an explicit path from the slot budget, but `uv run pytest -q backend
tests` — a full gate typed with `testpaths` entries as arguments — is still a full run that
should count as bare. Ruled: an explicit path argument that is itself a `pyproject.toml`
`testpaths` entry counts as bare; a narrower path, a node id, `-k`, `-m` stay exempt. One
predicate change, one test each way — dispatched to exec-excl as a follow-up when
convenient, not blocking anything.

**#730's rebase is a real content conflict**, not a stale-diff fast-forward: both #729 and
#730 added tests to `tests/test_doc_id_migrate.py` in the same area
(`git merge-tree --write-tree` confirms `CONFLICT (content)`). exec-dp7 told to expect this
and resolve by keeping both sides' additions. **#723** reads `UNKNOWN`, rebase in flight,
nothing to do until it settles.

**Correction**: the deputy's item 3 asked the lead to build this table, not send it —
misread on my part. Built now, from `scripts/_docverify.py`'s `EXPECTED_VERDICTS` at
`0af63b4` directly (`FATAL_VERDICTS = {FAIL, UNDETERMINED, NOT_MEASURED, REGRESSION}`,
DISCLOSE/PASS excluded) cross-referenced against this ledger's own dispatch record — not
transcribed from any relay.

## Checkpoint-1 table — 13 fatal rows on `0af63b4`

| row | verdict | cause (one clause) | owner | PR |
|---|---|---|---|---|
| d1 | FAIL | `NT-00`-prefixed citation form, un-migrated | unowned | — |
| d4 | FAIL | `wf-0[0-9]` case-form — 269/103 files → **2/1 file** on the fresh `--verify` (run 33884621869, `6c92d55`) | executor-30-2 | one file from zero, resumed to close it |
| d5 | FAIL | `Ruling [0-9]+` un-migrated population — **unmoved**, 76/20 → 77/20; three values' counts grew, value set unchanged (same pattern as d8's earlier gap) | executor-30-2 | resumed — name the generator |
| d6 | FAIL | `ADR-0[0-9]{3}` genuine un-migrated 4-digit citations remain | unowned | — |
| d7 | FAIL | `(FR\|NFR\|OQ\|DEP)-[A-Z]+-[0-9]+` un-migrated | unowned | — |
| d8 | FAIL | workstream/slice `W<n>-<n>` — re-recorded REGRESSION→FAIL by #733's distinct-value rule; still fatal: **123 task keys in 40 files + 14 bare work-key remainders in 6 files** (both ruled fatal, `to-lead.md:455`(i)); slice-key population is the disclosed part | executor-30-2 | not fully closed, work continues |
| d9 | FAIL | `docs/plans/2026-`-prefixed citation form, un-migrated | unowned | — |
| d10 | FAIL | `docs/audit/`-prefixed citation form, un-migrated | unowned | — |
| d11 | FAIL | the old notes directory, un-migrated | unowned | — |
| d12 | FAIL | `docs/adr/`-prefixed citation form, un-migrated | unowned | — |
| d13 | FAIL | the old `.claude` notes root — INERT, see its unanchored companion | unowned | — |
| g | FAIL | the token-boundary defect, Ruling 102 §2 row 1 — residue down (none=320→190 on `6c92d55`); the +15 mangled-companion rise is **class 3c** (deputy ruling, 18:3xZ) — the instrument's own test modules exhibiting the shapes they detect, same class as (d)'s ruling — **discharged by exec-ids' `_docid.sweep_exclusion_reason` tuple landing, not by explanation**; the predicted per-file fixture-line drop is stated below, awaiting the measured drop once the tuple lands | multiple (partial) | #720, #723, #727, #729 merged; exec-ids' tuple pending (`fba9bfb`, now on `origin/w37-6-citation-inverse-ids`) |
| h1 | FAIL | `audit-docs.py` non-disclosed classes (32, 36, 1, 31, 27, …) still non-zero | unowned | — |

**Nine of thirteen rows are unowned** (d1, d6, d7, d9, d10, d11, d12, d13, h1) — no dispatch
exists against them as of this entry. Three (d4, d5, d8) are executor-30-2's scope, PR not
yet opened. One (g) is partially discharged across four PRs (three merged, one in flight)
but still fails overall. **Checkpoint 1 cannot be reported met until every row above either
clears or is explicitly ruled DISCLOSE/out-of-scope** — this table is the tracker from
here; each later entry moves rows off it by name.

## 2026-09-04 — the nine unowned rows dispatched: three executors, cut by mechanism

Deputy ruled the actual figures (`docs` run on `0af63b4`) before cutting: 895 lines total
across the nine rows, five path rows (d9-d13) 821 of them (92%), three id rows (d1/d6/d7)
74, h1 separate. Three executors, not nine — one mechanism per group:

- **`exec-paths`** (d9, d10, d11, d12, d13) — legacy path citations repointed via the
  unit-record inverse's path columns, the mechanism #30 already builds. Stacked on
  `w37-6-citation-inverse-unit` (#30 not yet merged when dispatched); rebases onto `main`
  once #30 lands. Acceptance: all five rows zero on fresh `--verify`, fixture proof per
  form, one unmoved-path citation left untouched and listed. d13's `INERT` note is the
  instrument's, not licence to skip — 90 real lines.
- **`exec-ids`** (d1, d6, d7) — 74 lines in ≤35 files. First deliverable is investigation,
  not code: the 74 lines by directory and by kind (citation vs. specification, NT-0004's
  vocabulary), reported back before any fix. **Does not decide its own exclusion** — the
  table comes to the lead, who relays to the deputy for the specification-class ruling;
  `exec-ids` then fixes only the citation class.
- **`exec-h1`** (h1) — checks 32 (downstream of A/B, not yet), 36/1/31/27 (now): each
  classified as check-side bug (not migration-aware) or genuine migration defect (filed
  with owner) before any fix. 29/30/35 stay disclosed (Ruling 105 §B), untouched.

All three dispatched with the canonical gate line, per-worktree database step, and a
required proof-of-reading line. Landing order when they collide: #30, then `exec-paths`
(stacked), then `exec-ids`; `exec-h1` independent. Count: `executor-30-2`, `exec-dp7`,
`exec-paths`, `exec-ids`, `exec-h1` — five live (triage-code stood down, not counted),
well within the eight-executor cap.

## 2026-09-04 — row (g) lost its owner when triage-code stood down too early; resumed

Deputy caught it: the original (g)-triage dispatch named `triage-code` owner of "#723 and
(g)'s residue," two halves — I tracked only the #723 half as done and stood the whole
executor down once that merged. Row (g) is still FAIL overall (326 unclassified hunks at
`exec-dp7`'s last read, minus whatever #723's causes actually accounted for), and it went
from owned to unowned silently. **Resumed `triage-code`** (never `TaskStop`'d, just told to
stand down — resumes from its own context via `SendMessage`) with the residue-count task:
get a fresh unclassified count on current `main`, name any remaining recognizable causes
the same way #720/#723 did, or report precisely what doesn't fit an existing class. Six of
eight executors now, still inside the cap.

## 2026-09-04 — exec-paths finds d13's zero-requirement conflicts with a standing ruling; d9-d12 partially fixable, not zeroable

Before writing any code, `exec-paths` classified every surviving line per row rather than
assuming the citation-inverse mechanism was simply missing a form:

**d9-d12** (`docs/plans/2026-`, `docs/audit/`, `docs/notes/`, `docs/adr/`): the token-map
mechanism already works for its intended case (a full-path citation with a real `old_path`
row). A real, fixable gap exists — word-wrapped citations, where a markdown line-wrap
splits the old path's token across lines so the per-line literal match never sees the whole
token (141/210 of d9, 47/346 d10, 4/135 d11, 0/38 d12). **But the majority of each row
(especially d10-d12) is bare directory-prefix/glob prose mentions with no single
`(old_rel, new_rel)` pair to repoint to** — largely inside frozen historical documents
(`docs/plans/PL-*`, `docs/closures/CR-*`, `docs/findings/FD-*`, `docs/rulings/RL-*`)
describing the old scheme as history. **Even after the word-wrap fix, none of d9-d12
reaches zero.**

**d13** (`.claude/notes/`) is a harder problem — a genuine conflict with an existing
standing ruling, not a missing form. `.claude/notes/` → `docs/rfcs/RFC-…` was already
migrated under a separate, earlier effort (RFC-181 Slice 4, Ruling 61 — its own id fenced
below, landed 2026-09-01) with its own tombstone-stub mechanism and its own test

```
RL-00230
```

*Fenced 2026-09-04 under Ruling 103 §5.1; value unchanged.*

(`tests/test_notes_move_citations.py`), which **explicitly exempts `docs/plans/` and other
provenance-locked artifact families from ever being rewritten to the new path, by ruled
design, forever** — confirmed passing on the real tree (`1 passed`). `doc-id.py`'s own
`REDIRECTS.csv` has zero `.claude/notes/` rows; the old→new map for this family lives only
in `.claude/notes/README.md`'s own table, which `migrate()` never reads. d13's 90 lines:
54 inside frozen `docs/plans/PL-*` (RL-230-exempt by name), 25 in other frozen families, 6
in living code, 2 in skills/roles, 3 elsewhere. **Making d13 read zero would mean either
building a second redirect-consuming path reaching outside NT-0019's domain, or rewriting
citations inside frozen plans RL-230 explicitly ruled must stay untouched.**

Told `exec-paths` to proceed with the word-wrap fix for d9-d12 now (real, in-scope,
reduces but does not zero those rows) and hold d13 entirely. **Escalated to the deputy,
not decided here**: whether d13's zero-requirement needs amending against RL-230's
exemption, and whether d9-d12's residual directory-prose population is W37-6's scope at
all or a separate documentation-sweep item.

## 2026-09-04 — exec-h1's classification: three checks already owned, two small new findings, one classifier bug in the instrument itself

Read the ledger's own checkpoint-1 dispatch entry, then cross-checked its own independent
findings against it rather than transcribing — good discipline. All four checks are the
check correctly reporting real migration defects, none check-side bugs:

- **Check 36** (5856 hits) — exactly row (d)'s known sub-checks, already owned by
  `exec-ids`/`exec-paths`/`executor-30-2`. Not duplicated.
- **Check 1** (270 hits) — ~237 already `executor-30-2`'s cause3 (PR #30). **33 hits are a
  new, previously unnamed defect**: `docs/INDEX.md` and `docs/closures/INDEX.md` copy a
  cited document's own relative link verbatim without adjusting for the index file's own
  directory depth — a link correct one level down from where it was written resolves wrong
  once copied into a shallower generated file.
- **Check 31** (1 hit) — id-sequence gap 296→991, matches the known allocate-after-
  exemptions defect, owned by `alloc` (row b). Not duplicated.
- **Check 27** — a self-correction: exec-h1's own first automated pass read this as zero,
  wrongly — it's actually 1 failure. **Root cause traced to a real bug in the instrument's
  own classifier**: `_docverify.py`'s `_classify_failures`/`_CHECK_PREFIX_RE` expects a
  `check N:` message prefix, but `check_process_core_digest`'s `fail()` carries none, so
  the failure silently buckets as unclassified rather than "27" on every run. The
  underlying defect: the migration's token-rewrite touched `delivery-process.md`'s bytes
  without reconciling `delivery-process.core.json`'s digest pointer (a deliberate manual
  step per Ruling 45, not something `migrate()` should auto-fix).

Authorized both new findings (link-depth bug, digest reconciliation) plus the classifier
fix, all in the same PR — no collision with other in-flight work (`doc-index.py`'s
generation logic and the digest field are untouched by anyone else right now). Told to
confirm the root cause by reading `doc-index.py`'s source before fixing, and to diff
`delivery-process.md` pre/post-migration to confirm the change is token-form-only before
bumping the digest, not assume either.

## 2026-09-04 — d13 ruled in scope after all: NT-0019 §5 already schedules its own retirement; d9-d12 get a precise three-part fix

**Correction to this ledger's own citation**: an earlier entry cited the string below for
Ruling 61:

```
RL-00230
```

*Fenced 2026-09-04 under Ruling 103 §5.1; value unchanged.*

That id resolves to nothing on `origin/main` — the migration has not minted it yet.
Should have been cited by file/ruling number, not an unminted id.

**d13 — not a conflict, exec-paths's reading of the exemption was wrong, not its facts.**
`test_notes_move_citations.py`'s frozen-plan carve-out is not a permanent design decision —
NT-0019 §5 itself schedules the `.claude/notes/` stubs' deletion (step 4, `:281`/`:342`)
and that exemption test's own removal (`:409`, replaced by `test_audit_docs_redirects.py`).
Ruling 61 is recorded **INVALIDATED**, its own horizon explicitly at W37-6
(`docs/audit/ruling-acceptance-item-sweep.md:133-145`, quoting `audit-docs.py`'s docstring:
"until W37-6 deletes the stubs entirely"). The test passing on the real tree is the
pre-migration state, not evidence the exemption still holds — DP-7's predicate
(`frozen_file_matches_after_migration_stamp`) exists specifically to rewrite frozen files
under the migration stamp, and the Slice 4 carve-out predates it. **Ruled: d13 stays at
zero, in scope.** Fix: `migrate()` reads `.claude/notes/README.md`'s tombstone table once
(its last reader), composes each stub through to its final `docs/rfcs/RFC-…` path, emits
the `REDIRECTS.csv` row and `token_map` entry, deletes the stubs and README (§5 step 4).
Proof: d13 at 0; a fixture citation in a frozen plan comes out repointed AND DP-7-clean.

**d9-d12, three parts, all ruled:**
1. **Word-wrap fix** (141/210 of d9, 47/346 d10, 4/135 d11) — one hard acceptance
   condition: the rewrite preserves the line break exactly where it stands, never rejoins
   the token onto one line (a rejoin changes bytes beyond the token, breaking DP-7's
   inverse on every frozen file it touches). Proof: DP-7 passes on each frozen file
   changed.
2. **Directory-level tokens** — `_README_LEGACY_DIR_MOVES` (`doc-id.py:6179`) currently
   applies to READMEs only; the same constant should feed `token_map` for every file, not
   just READMEs — takes most of d11 and d12.
3. **Disclosed class** — what remains is prose naming a directory with no single
   successor (`docs/audit/`, deliberately absent from the map — "dissolves into four…
   reported rather than silently sent somewhere plausible" — and the bare dated prefix
   `docs/plans/2026-` with nothing after it). No `(old_path, new_path)` pair exists;
   rewriting the sentence is a forbidden meaning edit in a frozen file. Ruled, on Ruling
   105 §A's pattern: a §7(d) path match not followed by a path present in
   `REDIRECTS.csv`'s `old_path` column is disclosed by count, excluded from the zero
   requirement, owner W37-11's citation-form item. Any match that IS a real file path stays
   fatal — no over-disclosure.

**Scope confirmed W37-6's throughout** — rows, mechanism, and the disclosed class all
`exec-paths`'s, nothing splits to a separate sweep. Full ruling relayed verbatim.

## 2026-09-04 — exec-ids' 74-line table ruled: all 42 citations are fixed, 32 specifications get three dispositions

`exec-ids` reproduced d1/d6/d7's own predicate directly (`_docid.LEGACY_FORM_PATTERNS`,
`Corpus.scan`, the row's own exclusions) against a fresh `--verify --keep` snapshot of
`origin/main` = `56c0e81` — 74/74 matched, not approximated. Clean structural split: every
CITATION line under `docs/`; every SPECIFICATION line in `.claude/skills/`, `scripts/*.py`
comments, or `tests/*.py` fixtures, zero overlap.

**Ruled: all 42 citations are `token_map` misses, every one fixed** — the frozen-plan
exception protects the claim, not the citation's spelling (established three times over:
`docs/plans/README.md:25-27`, `_normalize_padded_citations`'s #25 precedent, and Ruling
68's DP-7 predicate itself). `exec-ids`'s deliverable is the cause of each miss, not the
line. `docs/rulings/INDEX.md:112` gets a one-line determination first (source's own
unrewritten citation, covered by the general fix — or the generator read the title before
rewriting, a generator-ordering bug) — generated files are explicitly NOT exempt from row
(d) the way row (f) exempts them.

**32 specifications, three dispositions by location:**

| Class | Files | Lines | Disposition |
|---|---|---|---|
| 3a — Markdown/frozen-prose exhibit | `.claude/skills/docs-audit/SKILL.md`, `docs/plans/PL-00282-…md`, `docs/plans/PL-00066-…md` (borderline, ruled in) | 5 | Fenced, Ruling 103 §5.1's note verbatim, same as (e)'s exhibits |
| 3b — Python comments in `scripts/` | `scripts/audit-docs.py` (×2 sites), `scripts/doc-id.py` | 4 | Respelled to a non-matching schematic form or the new form — zero exclusions |
| 3c — Test literals in `tests/` | `test_doc_id_verify.py`, `test_audit_docs_ids.py`, `test_doc_id_migrate.py` | 21 | New 4th declared class in `_docid.sweep_exclusion_reason` — named-tuple exclusion, **three files, not four**; disclosed by file+count; no test outside the tuple qualifies |

(5+4+21 = 30 above; +2 for the two `test_register_owed.py` lines this table originally
double-counted into 3c, reconciled against `exec-ids`'s own per-file breakdown, sent in
full to the deputy and available on request.)

**Correction (deputy, 16:4xZ)**: `test_register_owed.py` is not one of "the instrument's
own test modules" — its subject, `scripts/register-owed.py`, is itself an NT-0019 `:382`
migration target ("paths, `FD-` parser, `WK-`/`SL-` in the Work-item column, docstrings |
H + M"). Its legacy literals are fixtures of a parser that changes form under the
migration — stale test data to migrate WITH the script, not lines to exclude. **The class-
3c tuple names three files, not four.** Its lines move to a **fourth class-1 fix**: nobody
else owns `register-owed.py`'s row, so this is W37-6's and `exec-ids` takes it. Relayed.

**Refused**: a document-keyed exemption for skills generally (already refused for row (e),
same corpus); legacy strings built at runtime in tests to dodge the scanner; leaving the 32
as standing red with no predicate. Relayed to `exec-ids` in full; cleared to build.

## 2026-09-04 — #733 verified against the (d8) ruling; a reconciliation gap flagged before the row is re-recorded

Deputy confirmed the creation rule landed correctly (`_value_set_creation`, one rule
across row (d), called for d8 and the shared loop). `EXPECTED_VERDICTS` re-records d8
`REGRESSION → FAIL`, expected on the next fresh `--verify`.

**Gap caught before it was accepted as closed**: the ledger's generator paragraph
(`docs/INDEX.md` 19 + `docs/rulings/INDEX.md` 2 = 21) is cited as accounting for "the
growth," but `executor-30-2`'s own measurement was `W37-6` 685→725 (+40) and `W32-7` 68→78
(+10) — 50 occurrences. 21 does not reconcile against 50. Resumed `executor-30-2` (its
own measurement) rather than guess: either the two figures are on different predicates
(files vs. occurrences, lines vs. occurrences) and the paragraph must say which, or 29
occurrences have an unnamed source and that's a real finding still owed. Not a blocker on
anything else in flight; this is a precision correction to the record, not new code.

## 2026-09-04 — shared-worktree incident: two executors' dispatch briefs never said "create your own worktree"; resolved without loss

`exec-ids` caught it first: working directory checked out on `docs-w37-6-ledger-cont6` (the
lead's own tracking branch), `git status` showing 57 real lines in `scripts/doc-index.py`
it never touched. Root cause: **the lead's own dispatch briefs for `exec-ids` and `exec-h1`
never included worktree-creation instructions**, unlike every other executor dispatched
today — both defaulted to operating in `.claude/worktrees/lead-ruling105`, the lead's own
worktree, live while the lead was committing ledger entries to it throughout.

**Resolved without loss.** `exec-ids` stopped before committing anything and saved its own
diff, which turned out to also have captured `exec-h1`'s hunk (a full-file diff, not
hunk-scoped). `exec-h1` had independently already saved its own, correctly-scoped patch
before this was even reported. The lead extracted a clean, hunk-separated patch for each
executor (`scripts/doc-id.py` carried one hunk from each: `exec-ids`'s docstring respelling
at `:865`, `exec-h1`'s `_write_split_source_indexes` link fix at `:6863`) and verified both
apply cleanly against fresh `origin/main` (`6c92d55`) before telling either executor
anything was safe. Both told to create dedicated worktrees now and apply their own clean
patch there; the shared worktree is cleaned back to matching `origin/main` once both
confirm.

## 2026-09-04 — exec-ids' major finding: 17 scoped tokens across ~39 lines were never allocated, not un-rewritten

Before fixing anything, `exec-ids` checked every distinct scoped token in its remaining
citation lines against `docs/specs/*.md` (the only source `_discover_requirements` reads)
on the control tree. **17 tokens have zero occurrences anywhere** — `token_map` has
nothing to rewrite them to because nothing ever defined them. Stronger than absence alone:
the citing rulings themselves (`RL-00144`, `RL-00145`, `RL-00176`, `RL-00178`) say, in the
exact flagged lines, the token was "deliberately not taken" / "stays free" / "is not
taken" — these are "next free" markers that moved between successive plans as earlier
candidates were superseded, never allocated under that name. `exec-ids` correctly refused
to fabricate a mapping — the same "fabricated id nothing allocated" class row (b)'s
`OQ-8311` already named as a defect. Escalated to the deputy: confirm nothing else defines
these tokens, or rule a new disclosed class for never-allocated next-free markers. Not
decided here. `exec-ids` proceeding on its two unambiguous fixes (`NT-0014-15`'s
padding-normalization gap) and the specification dispositions while this rules.

## 2026-09-04 — d8's generator-count gap fully reconciled: option (b), a real second unnamed source found and closed

`executor-30-2` re-verified rather than guessing — the earlier "21 vs. 50" gap was option
(b): the original paragraph named only part of the source. Full reconciliation, on the
same predicate (occurrences of the literal value) both sides:

**W37-6** (control 710, migrated 750, +40): +22 from generated index files
(`docs/INDEX.md` +19, `docs/rulings/INDEX.md` +2, `docs/closures/INDEX.md` +1 — a third
index the original count had missed even on its own terms); **+18 from a source not
checked at all before**: `_write_document_drafts`'s own front-matter `title:` stamp
duplicates a document's heading text whenever that heading mentions "W37-6" — the
front-matter line says it once, the still-present body H1 says it again. Verified directly
on a real file diff (`docs/plans/2026-09-03-w37-6-time-boxed-delegation.md` 1 occurrence →
`docs/rulings/RL-00295-...` 2), with a negative control confirming the mechanism is
conditional on title text, not universal (`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`
44 → 44, no growth, title doesn't mention W37-6 despite 44 body citations).

**W32-7** (control 71, migrated 81, +10): +9 index, +1 same title-stamp mechanism, one
document.

Both components are the same class-6 phenomenon (a generator quoting a source title
verbatim) Ruling 104 §2 already names, occurring at two levels — family/global index
renderers, and every individual document's own front-matter stamp — not two different
defects. No code fix required under the ruling as written; this closes the completeness
gap in the generator paragraph. Comment-only precision on an already-correct
classification — the dated ledger record is sufficient, no follow-up PR needed today.

## 2026-09-04 — worktree incident closed; the never-allocated-id class ruled mechanical, not sentence-read; fresh `--verify` on the merged tree shows real remaining work, including a regression signal

**Worktree incident, closed.** Ruled not a role-file gap — `executor.md:12` and
`lead.md:66-68` already require every dispatch to carry its own worktree, and this was a
dispatch that omitted the sentence, not a charter hole. Verified directly, not by
trusting either executor's reply: `wt-ids` and `exec-h1-index-link-depth` both confirmed
via `git status`/`git log -1` to hold the correct patched files, on top of the merged base
commit. Only then cleaned `.claude/worktrees/lead-ruling105`'s three affected files back
to matching `origin/main` (`git checkout --`). Every future dispatch brief quotes
`lead.md:66` verbatim as its first line, per instruction.

**Never-allocated-id class ruled**: decided by a mechanical predicate the instrument
runs — zero definition rows in every `_discover_*` source and no `old_id` row in
`REDIRECTS.csv` — never by the citing sentence's wording. A token that fails the
predicate is a real `token_map` miss regardless of what its citing ruling says; one that
passes is disclosed by count, excluded from the zero requirement, terminal, never fenced
(the sentence is a correct historical fact, not an exhibit of a defective form). Broken-
input proof required both directions. Relayed to `exec-ids` in full, cleared to build.

**Fresh `--verify` on the merged tree** (run `33884621869`, `main` = `6c92d55`, green,
`UNCHANGED: 13`) — the checkpoint table now carries these real figures, not "pending":

- **d4**: 269/103 files → 2/1 file. One file from zero.
- **d5**: unmoved, 76/20 → 77/20 — three values' counts grew, value set unchanged, same
  pattern as d8's earlier generator gap.
- **d8**: re-recorded REGRESSION→FAIL by #733's own rule, but not fully closed — 123
  task keys in 40 files + 14 bare work-key remainders in 6 files are both still fatal.
- **g**: residue down (none=320→190) but **the mangled companion rose by 15** (457→472)
  — a real regression signal, exactly what Ruling 102 §2 row 1 exists to catch. `#733`
  may have introduced a new mangling somewhere.

`executor-30-2` resumed a third time with all three asks, mangled-companion regression
first (before d4/d5), since a growing companion after a fix is the more urgent signal.

## 2026-09-04 — worktree incident's durability gap: the salvaged patches were still uncommitted

Deputy's follow-up check: `lead-ruling105` clean, confirmed — but `wt-ids` and
`exec-h1-index-link-depth` both showed 0 commits ahead of `main`, the applied patch still
sitting as working-tree edits only. An uncommitted worktree dies with its session or a
stray reset — the exact shape that already cost this project one salvage. Both executors
told to commit (`wip:` prefix fine, squashed at PR time) and push now, before continuing
their in-progress work. Incident closure is not final until both commit shas exist to
cite, not merely a clean `git status`.

## 2026-09-04 — durability, half done: exec-ids committed but not pushed; exec-h1 still uncommitted; #732 merged

`exec-ids`: 2 commits ahead (`fba9bfb`) but the branch never reached `origin` — told to
push in one command. `exec-h1`: still 6 dirty files, 0 ahead, 13+ minutes into its gate —
told to commit and push the moment the gate returns, before even reading the result. A
local-only commit is the middle case of the three-way durability split: survives a
session, not a lost worktree.

**PR #732 merged** at `e3739e1` — confirmed CLEAN against the exact head SHA's own
workflow runs this time (per the earlier #724 lesson), not a stale rollup. Continuing on
`docs-w37-6-ledger-cont7`.

## 2026-09-04 — row (g)'s +15 "regression" resolved: test-fixture literals, not corpus mangling

`executor-30-2`'s investigation (task #42), verified with the real tool, not a hand-rolled
scan: their first pass used their own regex script and produced numbers that did not match
CI, so they discarded it and redid the check properly. Checked out `e6384d7` (#733's direct
parent, confirmed via `git log -1 6c92d55^`) and `6c92d55` into two disposable snapshots,
ran the actual `python3 scripts/doc-id.py migrate --verify --repo-root <snapshot> --keep`
from each — the real CI mechanism. Both reproduced CI's own numbers exactly: before
migrated=457/control=25, after migrated=472/control=38.

**The key fact: `control` (raw, un-migrated content, zero rewriting) also rose, +13.**
`git diff e6384d7 6c92d55 --stat` confirms the only changed files across the whole tree are
executor-30-2's own 4 files — so control's entire rise can only be driven by their literal
text. It is: their new tests deliberately embed illustrative mangled-shape strings as
broken-input proof material (`FR-680..4`, `FR-680..703`, `FR-700/701`, `WK-944C`,
`NFR-775/14` — e.g. `test_task30_a_half_rewritten_range_is_named_mangled` asserts against
`FR-680..4` literally). These are Python string literals in test/comment content the
citation sweep never touches, and they inflate a whole-tree scan identically on both sides.

Since control's whole +13 is accounted for by those 4 files and nothing else in the tree
differs, at most +2 of migrated's +15 is unexplained — and even that residual could not be
pinned to any real-corpus file: diffing the two kept migrated snapshots directly, excluding
executor-30-2's own 4 files, shows every other file's mangled count flat or **lower** after
the fix (`docs/roadmap.md` 51→18, a `WF-00991` doc 22→12, and more), consistent with the
already-observed residue drop (classified-by-none 311→190).

**Verdict: no real-corpus regression in row (g).** The rise is the whole-tree scan picking
up executor-30-2's own test-fixture literals; the real corpus's mangled population
improved. Accepted as well-evidenced per CLAUDE.md §13 (real-tool verification, isolated
diff scope, both directions checked). Executor-30-2 asked to add a one-line acknowledgment
comment near those literals (their own suggestion, cheap, self-documents the
corpus-vs-fixture distinction for a future whole-tree scan) and proceed to d4/d5.
