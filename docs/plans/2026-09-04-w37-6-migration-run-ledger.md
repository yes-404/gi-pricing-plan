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
| #716 | docs(plans): open W37-6's migration run ledger | `e38ca12` | UNCHANGED: 14 (this ledger's own history above is its full run — every entry, salvage, and correction landed as commits on this PR before it merged; no predicate code touched) |
| #718 | fix(reporter-cycle): Ruling 106 — 100-word cap, BST-clock ETA, main-move refresh | `a9a733c` | UNCHANGED: 14 (`.claude/**` skill/role/script content only — `reporter.py`, `test_reporter.py`, `reporter.md`, `SKILL.md`, the ruling record — no `docs/**` migration-scope path or predicate code touched). Fourth F49 trailer on this branch (`07ea929`) was amended and force-pushed before merge, root cause fixed the same day (shared vs. per-worktree commit-msg hook, see the F49 entry below); duplicate branch `w37-6-ruling106-work` deleted from origin after merge. |

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
