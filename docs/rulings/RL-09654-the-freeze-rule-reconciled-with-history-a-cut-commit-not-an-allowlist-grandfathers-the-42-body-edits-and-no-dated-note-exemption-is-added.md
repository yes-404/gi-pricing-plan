---
id: RL-9654
family: ruling
title: The freeze rule reconciled with history before check 34 goes live — a cut commit, not an allowlist file, grandfathers the 42 body edits, and no dated-note exemption is added
status: active                 # active → superseded | retired (§1.2a) — PROPOSED until the deputy's ACK for the maintainer
created: 2026-10-05
owner: decision-maker
tree: 99afcde215c0817c5ac4db55332ab7a69e4752a0
phase: P2
work: WK-1170
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RFC-RFCWID, FD-1282, FD-1323, WK-1170]
---

# RL-9654 — The freeze rule reconciled with history before check 34 goes live

*Working id 9654; drafted 2026-10-05 by the decision-maker on the lead's brief
(`~/gi-pricing-plan.local/handover/brief-dm-freeze-2026-10-05.md`, a local file), on the
deputy's entry `2026-10-05 13:32:57 BST — 34: SPAWN the DM for the freeze-rule RFC + RL; my
leaning stated, not ruled` in `~/gi-pricing-plan.local/channel/to-lead.md` (a local file).
The family is `process/`'s (`document-ids.md` §1.6, row "Reference — `process/`"), so this
ruling is the maintainer's to accept; **PROPOSED** until the deputy's ACK, given for the
maintainer. No text below is applied in this PR: every amendment is a T-text.*

## Verified first, at `99afcde215c0817c5ac4db55332ab7a69e4752a0`

The tree is `origin/main` at the time of drafting (`git log -1 --format='%H %aI'`:
`99afcde2… 2026-10-05T13:27:55+01:00`).

- **The rule.** `docs/process/document-ids.md` §1.2's family table gives `ADR`, `RFC`, `PL`,
  `RL`, `RS` as `frozen`, `CR` as `write-once`, `FD` as `living row + frozen essay` (:47-:54).
  §1.5's header comments (:134-:135): *"with `status:` (forward only) and `corrected_by:`, the
  only fields edited after a file freezes"*; *"each entry is the RL-/RFC- that corrects this file
  (the body is never edited)"*. §1.11 row 34 (:230): *"for a frozen family the diff against the
  merge-base touches only `status:` (forward only), `superseded_by:`, an append to
  `corrected_by:`, or — ledgers only — an append to `plans:`"*.
- **Text that says otherwise.** §1.6's PL row (:158): *"`draft` while decision points are open,
  `active` on freeze"* — read as "a plan freezes when it activates", which the family table
  (:49, `frozen`) and :69 (*"Mutability is a family property, not a status"*) contradict.
  `docs/findings/README.md` :60-:61: *"An essay file is write-once, amended in place … A
  correction is appended and dated"*; :72-:73: *"A record that changes after the fact must say it
  changed, with the correction dated."* `docs/closures/README.md` :33: *"a correction after the
  fact is dated and says so"*.
- **The check.** `check_freeze` (`scripts/audit-docs.py:2382`) runs only the
  `corrected_by:`→`corrects:` pairing; `frozen_diff_is_permitted` (`:2142`) is defined and not
  called (FD-1282, FD-1323). `_FROZEN_FAMILIES` (`:2130-:2132`) is the seven families
  `decision`, `proposal`, `plan`, `ruling`, `research`, `closure`, `finding`.
- **The population.** 42 (commit, file) body edits to existing frozen-family files on
  `origin/main`'s first-parent line, `71f5a2208c7a92bad486ae128775a4a42c7ebc63..99afcde2…`,
  in five families: FD 17, PL 15, CR 5, RL 4, RFC 1. **The brief's "42 … to frozen FD/CR
  files" is the right count over the wrong scope: FD and CR are 22 of them.** The predicate,
  the full list and the per-row classification are RFC-RFCWID's (its *Population* section,
  the script verbatim). One row also changes non-permitted header fields: `97b15726…`,
  PL-1239, `slice:` and `relates:` (activation). **The newest of the 42 is `22fe674b…`
  (2026-09-30 13:26:41 +01:00); the range `e9263283177e5e1c1205ba48d0e41c2a1483f83c..99afcde2…`
  holds 0 body edits and 0 non-permitted header edits**, by the same two predicates.
- **The cut.** `e9263283177e5e1c1205ba48d0e41c2a1483f83c` (2026-09-30 14:36:42 +01:00) is
  `origin/main`'s first-parent commit current at the deputy's freeze entry `2026-09-30 14:48:52
  BST — DECISIONS: check 34 is vacuous on real trees …` (the next is `2118679b…`, 14:58:07). It
  is also FD-1323's measurement tree. That entry's item (3) already directs: *"plan activation =
  the `status:` flip only … activation facts … live in the dispatch record, quoted in the slice
  ledger's Task 0 … From now on, no prose is added to a plan already on main"*.
- **Merged correcting-record precedent.** RL-1290 (`corrects: RL-881`), RL-1287 (`corrects:
  CR-1212`) — `grep -l '^corrects: ' docs/rulings/*` at this tree. Open: #1119 (RL 9718,
  corrects RL-1401), #1137 (RL 9668, corrects CR-838).
- **Positive control for the cut-range predicate** (RFC-RFCWID's script, not check 34, which
  does not yet run it): one line appended to CR-838's file and committed in this worktree;
  the predicate over `e9263283…..HEAD` printed that commit and file; the scratch commit was
  reset (`git status --short`: 0 lines; HEAD back to `99afcde2…`).

## Ruled

**The deputy's leaning is adopted in substance and amended in form.**

1. **No dated-note exemption, in any form.** From the cut on, a frozen file's body never
   changes after its first merge, and its header changes only as §1.11 row 34 lists. Each kind
   of post-merge fact the 42 carried has a destination that is not the frozen body (RFC-RFCWID
   tests every class against the leaning; none is unworkable):

   | Class (RFC-RFCWID) | Rows | Destination from the cut |
   |---|---|---|
   | C — a correction or amendment of content | 21 | a correcting record: `RL-` (or `RFC-`) with `corrects:` the file, appended to its `corrected_by:` |
   | R — an FD resolution or progress note | 11 | the FD's register row (living), plus `status:` forward; nothing is corrected, so no `corrects:` |
   | V — a plan's activation | 5 | the `status:` flip only; the activation facts in the dispatch record, quoted in the ledger's Task 0 (the 14:48:52 entry, item 3); `slice:` and `relates:` present at the plan's mint |
   | A — an acceptance line filled after merge | 2 | the acceptance lands in the record before its merge; after merge, a maintainer-authored `RL-` that `relates:` the record (an acceptance is not a correction) |
   | M — a working id rewritten to its minted id | 2 | a frozen body cites an unminted sibling by its PR number, which resolves for ever; nothing is rewritten at mint |
   | L — a merge or run log appended to a plan | 1 | the ledger or the closure record |

2. **History is grandfathered by a cut commit, not by an allowlist file.** The cut is
   `e9263283177e5e1c1205ba48d0e41c2a1483f83c`. Check 34 never examines a commit that is an
   ancestor of the cut, in any comparison it runs. The 42 are **enumerated** — file and commit —
   in RFC-RFCWID's *Population* table, a frozen record, which is the durable list the leaning
   asked for. **There is no data file and no parsed section, and nobody may add to the
   grandfathered set**: every commit after the cut is outside it by construction, and the cut
   moves only by a superseding `RL-` the maintainer accepts.

   *Why not the leaning's allowlist file.* (a) The comparison §1.11 row 34 names is against the
   merge-base. Every one of the 42 is an ancestor of every future merge-base, so a merge-base
   comparison never sees any of them: an allowlist it read would never match, a check input
   that has never mattered and cannot be proven red on its own. (b) If check 34 also reads
   history (recommended to PL 9662 below), a list of (commit, file) pairs equal to "every body
   edit before the cut" is a second copy of a set the check computes from one constant — the
   duplicate RFC-756 records going stale. (c) The leaning's purpose, *"the list cannot grow
   silently"*, is met more strongly: a constant whose range closes at a past commit cannot
   admit a new edit at all, where a list can be appended to in a reviewed diff.

3. **`document-ids.md` :158 is amended** (T1): a plan is frozen from its first merge like its
   family; `active` is a `status:` flip.

## T-texts (none applied in this PR)

**T1 — `docs/process/document-ids.md` :158, the PL `map`/`leaf` row's owner cell.**
Replace *"planner, via `writing-plans`; `draft` while decision points are open, `active` on
freeze"* with:
> planner, via `writing-plans`; frozen from its first merge like the family (§1.2), `draft`
> while decision points are open; activation is a `status:` flip only, its facts in the dispatch
> record quoted in the slice ledger's Task 0, and `slice:` and `relates:` set at mint
> *(amended <date>, RL-9654 ¶3)*

**T2 — `docs/process/document-ids.md` §1.5, a paragraph after the YAML block.**
> **After a file freezes.** A frozen family's file freezes at its first merge. Its body never
> changes again. A correction is a correcting record (`corrects:` naming it, appended to its
> `corrected_by:`). A fact that corrects nothing goes to the record that owns it: an `FD-`'s
> resolution to its register row, a close's acceptance into the record before merge (or a
> maintainer `RL-` that `relates:` it), a plan's activation to the dispatch record. A frozen
> body cites an unminted id by its PR number. The body edits merged at or before
> `e9263283177e5e1c1205ba48d0e41c2a1483f83c` are grandfathered and enumerated in RFC-RFCWID;
> there is no other exemption *(amended <date>, RL-9654)*.

**T3 — `docs/process/document-ids.md` §1.11 row 34, appended to its cell.**
> ; a commit that is an ancestor of `e9263283177e5e1c1205ba48d0e41c2a1483f83c` (RL-9654's cut)
> is outside every range the check reads

**T4 — `docs/findings/README.md`.** At :60-:61 replace *"**An essay file is write-once,
amended in place** — the same convention the register applies to a row. A correction is
appended and dated, quoting what it supersedes, never a silent rewrite."* with:
> **An essay file is frozen from its first merge** (`document-ids.md` §1.2, §1.5). A correction
> is a correcting record — an `RL-` with `corrects:` this `FD-`, appended to its `corrected_by:`
> — never an edit to the essay. A resolution or a progress fact goes in the register row,
> which is living.

and at :72-:73 replace *"A record that changes after the fact must say it changed, with the
correction dated."* with:
> **Evidence is write-once.** A record is never changed after it merges; a correction is a new,
> dated record that names it.

**T5 — `docs/closures/README.md` :33.** Replace *"**Evidence is write-once**, and a correction
after the fact is dated and says so."* with:
> **Evidence is write-once.** A correction after merge is a correcting `RL-` (`corrects:` the
> record), never an appended note; a maintainer's acceptance lands in the record before merge,
> or as a maintainer `RL-` that `relates:` it.

**Not a T-text here:** `check_freeze`'s docstring (`audit-docs.py:2383-:2392`), which is
code and PL 9662's.

## What it obliges

- **PL 9662 (planner-freeze, WK-1170) names this ruling as its precondition** — RL-9654, at
  its minted id, in its *Activation needs* — and implements check 34 against ¶1-¶2: the
  merge-base comparison, the cut as the lower bound of any range, and no allowlist input.
- **Recommended to PL 9662, not ruled here (the plan's design is the planner's):** a second,
  history leg — `frozen_diff_is_permitted` over each first-parent commit in
  `<cut>..HEAD` — because the merge-base leg is empty on a push to `main` and blind to an edit
  that reached `main` with the gate red or bypassed. Measured cost: the predicate over every
  first-parent commit since `71f5a220` (2026-09-17) ran in 4.2 s on this box; `docs.yml:45` already checks out with
  `fetch-depth: 0`. The plan must say how either leg treats a `doc-id.py migrate` run's own
  frozen-file stamping (`frozen_file_matches_after_migration_stamp`, `audit-docs.py:2302`) —
  not decided here.
- **The applying PR** (WK-1170, after the maintainer's acceptance) lands T1-T5, with RFC-RFCWID
  and this ruling cited, before check 34's comparison goes live.
- **Not decided or struck here:** the 42 edits' content (each stands as merged; none gets a
  correcting record by this ruling); `migrate --verify`'s own reading of post-migration
  frozen-file edits, which is FD-1413's; the register row of FD-1282 and FD-1323 (the lead's
  `decision:`).

## Acceptance — the violation that must become detectable

The violation: a frozen-family file's body, or a header field outside §1.11 row 34's list,
changes in a commit after the cut, with `audit-docs.py` exiting 0.

- *Violation: one line appended to the body of a merged closure (CR-838's file) on a branch*
  — check 34 exits 1 naming the file.
- *Violation: `slice:` or `relates:` changed on a merged `active` plan* — check 34 exits 1.
- *Violation: the same append to CR-838 made at `40739df0…` (before the cut)* — **not** a
  failure: replaying check 34 at `99afcde2…` prints no row for any of the 42.
- *Violation: an allowlist file or parsed exemption section read by check 34* — refused at
  review of PL 9662's PR; `grep` for any path the check opens under `docs/` besides the
  documents in scope prints none.
- *Violation: the README practice survives* — after T4/T5, `grep -n 'appended and dated\|is dated
  and says so' docs/findings/README.md docs/closures/README.md` prints nothing.
