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
