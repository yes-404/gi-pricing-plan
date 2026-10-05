---
id: RL-9654
family: ruling
title: The freeze rule reconciled with history before check 34 goes live — frozen from first merge, no dated appended note, status forward only, a per-event base CI never turns off, and the 42 pre-cut edits enumerated and not re-judged
status: active                 # active → superseded | retired (§1.2a) — PROPOSED until the ACK of the maintainer (by delegation)
created: 2026-10-05
owner: decision-maker
tree: 99afcde215c0817c5ac4db55332ab7a69e4752a0
phase: P2
work: WK-1170
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RFC-9653, FD-1282, FD-1323, WK-1170]
---

# RL-9654 — The freeze rule reconciled with history before check 34 goes live

*Working id 9654, with its RFC under working id 9653. Drafted 2026-10-05 by the
decision-maker on the lead's brief (`~/gi-pricing-plan.local/handover/brief-dm-freeze-2026-10-05.md`,
a local file). It rests on two entries by the maintainer (by delegation) in `~/gi-pricing-plan.local/channel/to-lead.md` (a
local file): `2026-10-05 13:32:57 BST — 34: SPAWN the DM for the freeze-rule RFC + RL; my leaning
stated, not ruled`, and `2026-10-05 13:43:31 BST — PL 9662 / SL 9655 (check_freeze fix, #1146
@c35b67b7): conditions met; DP-3 = the spec; one guard on the "none" switch; DP-4 gets an owner`.
The family is `process/`'s (`document-ids.md` §1.6, row "Reference — `process/`"), so this
ruling is the maintainer's to accept. It stays **PROPOSED** until the ACK of the maintainer (by delegation). Nothing below is applied in this PR: every amendment is a T-text.*

*It is activation need **A1** of PL 9662 (planner-freeze, WK-1170; PR #1146 at
`c35b67b712a9f8d86d968b3b816a888e9be7f121`). That plan's "What A1 must contain" list,
items (i)-(vii), maps one to one onto ¶1-¶7 below.*

## Verified first, at `99afcde215c0817c5ac4db55332ab7a69e4752a0`

The tree is `origin/main` at drafting time (`git log -1 --format='%H %aI'`:
`99afcde2… 2026-10-05T13:27:55+01:00`).

- **The rule.** `docs/process/document-ids.md` §1.2's family table marks `ADR`, `RFC`, `PL`,
  `RL` and `RS` `frozen`, `CR` `write-once`, and `FD` `living row + frozen essay` (:47-:54).
  :69: *"Mutability is a family property, not a status"*. §1.2a :69: *"Transitions run forward
  only"*. §1.5's header comments (:134-:135) say *"with `status:` (forward only) and
  `corrected_by:`, the only fields edited after a file freezes"* and *"each entry is the RL-/RFC-
  that corrects this file (the body is never edited)"*. §1.11 row 34 (:230) says *"the diff
  against the merge-base touches only `status:` (forward only), `superseded_by:`, an append to
  `corrected_by:`, or — ledgers only — an append to `plans:`"*. It names no ref.
- **Text that says otherwise.** §1.6's PL row (:158) says *"`draft` while decision points are
  open, `active` on freeze"*. That reads as "a plan freezes when it activates", which :49 and
  :69 contradict. `docs/findings/README.md` :60-:61 says *"An essay file is write-once, amended
  in place … A correction is appended and dated"*, and :72-:73 says *"A record that changes after
  the fact must say it changed, with the correction dated."* `docs/closures/README.md` :33 says
  *"a correction after the fact is dated and says so"*.
- **The check.** `check_freeze` (`scripts/audit-docs.py:2382`) runs only the
  `corrected_by:`→`corrects:` pairing. `frozen_diff_is_permitted` (`:2142`) is defined and never
  called (FD-1282, FD-1323). Its status clause (`:2169-:2171`) refuses only a move *from*
  `closed`, `retired` or `superseded`, so `active → draft` passes it. That is DP-3, code against
  spec. `_FROZEN_FAMILIES` (`:2130-:2132`) holds seven families: `decision`, `proposal`, `plan`,
  `ruling`, `research`, `closure` and `finding`. Ledgers are outside it (`_LEDGER_FAMILY`,
  `:2133`).
- **The population** (RFC 9653, *Population*, with the script verbatim):
  - 42 (commit, file) body edits to existing frozen-family files, on `origin/main`'s
    first-parent line, in `71f5a2208c7a92bad486ae128775a4a42c7ebc63..99afcde2…`.
  - They fall in **31 merges**, across **five families**: FD 17, PL 15, CR 5, RL 4, RFC 1.
  - The newest is `22fe674b4a590c47095c6ba608fe974264581139` (2026-09-30 13:26:41 +01:00).
    CR-838:46, *"Dated correction, 2026-09-29"*, is `40739df04087d3e28c1dcb1fa92e581db26603da`.
  - The range `e9263283177e5e1c1205ba48d0e41c2a1483f83c..99afcde2…` holds 0 body edits.
  - A second predicate counts header fields outside row 34's list. It prints one edit before
    `e9263283` (PL-1239's `slice:` and `relates:` at activation, `97b15726…`, already among the
    42) and 0 after it.
  - PL 9662's independent measurement, by the planner, agrees: *"42 historical edits in 31
    merges, the last 22fe674b; CR-838:46 = 40739df0"* (quoted in the maintainer's (by delegation) 13:43:31 entry).
- **The cut.** `e9263283177e5e1c1205ba48d0e41c2a1483f83c` (2026-09-30 14:36:42 +01:00) was
  `origin/main`'s first-parent tip at the maintainer's (by delegation) entry `2026-09-30 14:48:52 BST — DECISIONS:
  check 34 is vacuous on real trees …`. The next commit is `2118679b…`, at 14:58:07. That entry's
  item (3) says: *"plan activation = the `status:` flip only … activation facts … live in the
  dispatch record, quoted in the slice ledger's Task 0 … From now on, no prose is added to a plan
  already on main"*.
- **Correcting records on main.** RL-1290 has `corrects: RL-881`, and RL-881 has `corrected_by:
  [RL-1290]`. RL-1383 has `corrects: RL-1361`, and RL-1361 has `corrected_by: [RL-1383]`.
  RL-1287 has `corrects: CR-1212`.
- **CI today.** `docs.yml` runs on `push` to `main` and on `pull_request` (:13-:18), and it checks
  out with `fetch-depth: 0` (:45).
- **Positive control for RFC 9653's predicate.** This is the RFC's script, not check 34, which
  does not run the predicate yet. One line was appended to CR-838's file and committed in this
  worktree. The predicate over `e9263283…..HEAD` printed that commit and file. The scratch commit
  was then reset: `git status --short` printed 0 lines, and HEAD was back at `99afcde2…`.

## Ruled

**The maintainer's (by delegation) leaning is adopted in substance.** No dated-note exemption, and nothing that
happened before the cut is re-judged. **No allowlist file** (¶7 gives the reason).

1. **(i) Frozen from first merge, whatever the status.** A file of a frozen family (§1.2:
   `ADR`, `RFC`, `PL`, `RL`, `RS`, `CR`, the `FD` essay) freezes at its first merge to `main`,
   whatever its `status:` (:69). A `draft` plan on `main` is frozen. :158 is reworded (T1).

2. **(ii) What may change after the freeze.**
   - `status:` may move **forward only**, along §1.2a's order: `draft` → `active` → a terminal
     word (`closed`, `retired` or `superseded`).
   - `superseded_by:` may be set.
   - `corrected_by:` may gain entries at its end.
   - A ledger may also append to `plans:`.
   - Nothing else changes: no body line, and no other header field.

   Plan activation is the `status:` flip only. Its facts go in the dispatch record, quoted in
   the slice ledger's Task 0 (the 14:48:52 entry, item 3). A leaf plan's `slice:` and `relates:`
   are set at its mint. A later record that bears on the plan names it in its own `relates:`.

   **DP-3 is decided: the spec is right** (the maintainer's (by delegation) 13:43:31 entry, item 2, which this
   ruling records). `frozen_diff_is_permitted` must refuse any backward move, not only a move
   away from a terminal word. The slice adds a red test for `active → draft`.

3. **(iii) DP-1: a frozen body takes no dated appended note. Option (a).** This holds for every
   frozen family, not only FD, CR and RL. The text that loses is the two READMEs (T4, T5), not
   :134-:135. The exemption forms (b) and (c) are rejected: an appended note could carry any
   rewrite, and the check could not tell a correction from a change. Every class of the 42 has
   a destination that leaves the frozen body unchanged (RFC 9653 tests each against the
   leaning, and none is unworkable):

   | Class (RFC 9653) | Rows | Destination from the cut |
   |---|---|---|
   | C — a correction or amendment of content | 21 | a correcting record (¶4) |
   | R — an FD resolution or progress note | 11 | the FD's register row (living), plus `status:` forward. Nothing is corrected, so there is no `corrects:` |
   | V — a plan's activation | 5 | the `status:` flip only (¶2) |
   | A — an acceptance line filled after merge | 2 | the acceptance goes into the record before its merge. After the merge, it is a maintainer-authored `RL-` that `relates:` the record (an acceptance is not a correction) |
   | M — a working id rewritten to its minted id | 2 | a frozen body cites an unminted sibling by its PR number, which never stops resolving. Nothing is rewritten at mint |
   | L — a merge or run log appended to a plan | 1 | the ledger or the closure record |

4. **(iv) The correcting-record form.** A correction is a new `RL-` or `RFC-`. Its `corrects:`
   names the frozen id, and the corrected file appends that record's id to its `corrected_by:`
   in the same PR. Check 34's existing pairing test holds the two together. This is :135 as it
   stands, applied by RL-1290 → RL-881 and RL-1383 → RL-1361.

5. **(v) The comparison base, per event, written into §1.11 row 34 (T3).** It is read from
   `AUDIT_DOCS_FREEZE_BASE`:
   - on `pull_request`, `github.event.pull_request.base.sha`, compared from its merge-base
     with HEAD;
   - on `push` to `main`, `github.event.before`, the previous `main` tip;
   - on a local run, when the variable is unset, the merge-base with `origin/main`.

   **CI never runs the check off** (the maintainer's (by delegation) 13:43:31 entry, item 1):
   - The workflow sets the base explicitly for each event.
   - The value `none` turns the comparison off and says so. It is for **local use only**: the
     run fails if the variable is `none` while `CI=true`.
   - An unresolvable base is a loud failure, never a skip.
   - **Every run prints the base SHA it compared against.**

6. **(vi) A deleted frozen file is a violation** (PL 9662's DP-2, option (a)). A `D` of a file
   whose base header names a frozen family fails. §1.6's FD row says *"never removed"*, and a
   deletion breaks every citation to the record.

7. **(vii) History is not re-judged.** The check reads only the change under audit, against the
   base in ¶5. Each of the 42 edits is an ancestor of every base that rule can produce, so none
   is ever compared again. They stand as merged: none is corrected, struck or reworded by this
   ruling, and that includes PL-1299's activation, which the maintainer accepted on 2026-09-30.
   **RFC 9653's *Population* table enumerates them, by file and commit, across all five
   families. That table is the grandfathered set, bounded by the cut `e9263283…`.** No
   allowlist file, and no section the check parses:
   - Under ¶5's bases, an allowlist would never match an entry. A check input that cannot
     change a result cannot be proven red.
   - A list in code would be a second copy of a set a frozen record already holds. RFC-756
     records how such a copy goes stale.
   - The leaning's purpose, *"the list cannot grow silently"*, is met more strongly. The set is
     closed by a frozen record and a past commit, and **nobody may add to it**. A later body edit
     is a violation, not a candidate for the list.
   - A deliberate audit run with an older base (for example `AUDIT_DOCS_FREEZE_BASE=71f5a220…`)
     will print the 42. That is a manual reading against RFC 9653's table, not the gate.
   - RL-1362's and RL-1379's working plan ids in title and slug stand as merged, listed in RFC
     9653's *Known historical defects*. They are content as added, after the cut, and not edits.

## T-texts (none applied in this PR)

**T1: `docs/process/document-ids.md` :158, the PL `map`/`leaf` row's owner cell.** Replace
*"planner, via `writing-plans`; `draft` while decision points are open, `active` on freeze"*
with:
> planner, via `writing-plans`; frozen from its first merge whatever its status (§1.2, :69),
> `draft` while decision points are open; activation is a `status:` flip only, its facts in the
> dispatch record quoted in the slice ledger's Task 0, with `slice:` and `relates:` set at mint
> *(amended <date>, RL-9654 ¶1-¶2)*

**T2: `docs/process/document-ids.md` §1.5, a paragraph after the YAML block.**
> **After a file freezes.** A frozen family's file freezes at its first merge, whatever its
> status. After that, `status:` moves forward only, `superseded_by:` may be set, and
> `corrected_by:` may gain entries at its end (a ledger may also append to `plans:`). Nothing
> else changes, and the body never changes. A correction is a correcting record: its `corrects:`
> names the file, and the file appends it to `corrected_by:`. A fact that corrects nothing goes
> to the record that owns it:
> - an `FD-`'s resolution to its register row;
> - a close's acceptance into the record before its merge, or a maintainer `RL-` that
>   `relates:` the record;
> - a plan's activation to the dispatch record.
>
> A frozen body cites an unminted id by its PR number. Deleting a frozen file is a violation.
> The 42 body edits merged at or before `e9263283177e5e1c1205ba48d0e41c2a1483f83c` stand as
> merged and are enumerated in RFC 9653. There is no exemption *(amended <date>, RL-9654)*.

**T3: `docs/process/document-ids.md` §1.11 row 34, its cell replaced by:**
> Freeze: for a frozen family, the diff against the base touches only `status:` (forward only,
> §1.2a), `superseded_by:`, an append to `corrected_by:`, or (ledgers only) an append to
> `plans:`. A deleted frozen file fails. Every `corrected_by:` entry is a record whose
> `corrects:` names this file (C4 made mechanical). The base is read from
> `AUDIT_DOCS_FREEZE_BASE`:
> - on `pull_request`, `github.event.pull_request.base.sha`, compared from its merge-base;
> - on `push` to `main`, `github.event.before`;
> - locally, when the variable is unset, the merge-base with `origin/main`.
>
> CI sets the base explicitly and never runs the check off. `none` turns the check off for a
> local run only, and fails while `CI=true`. An unresolvable base fails. Every run prints the
> base SHA it compared. History before the base is not re-judged (RL-9654 ¶7).

**T4: `docs/findings/README.md`.** At :60-:61, replace *"**An essay file is write-once,
amended in place** — the same convention the register applies to a row. A correction is
appended and dated, quoting what it supersedes, never a silent rewrite."* with:
> **An essay file is frozen from its first merge** (`document-ids.md` §1.2, §1.5). A correction
> is a correcting record: an `RL-` with `corrects:` this `FD-`, appended to its `corrected_by:`.
> It is never an edit to the essay. A resolution or a progress fact goes in the register row,
> which is living.

At :72-:73, replace *"**Evidence is write-once.** A record that changes after the fact must
say it changed, with the correction dated."* with:
> **Evidence is write-once.** A record never changes after it merges. A correction is a new,
> dated record that names it.

*(Pre-mint note, 2026-10-05 15:58 BST, dm-finals2: the find string above now starts at
`**Evidence is write-once.**`. Without it, the replacement repeated that phrase, which :72
already opens with. No wording of the replacement changed. At `cdaaa573` the widened string
has one hit.)*

**T5: `docs/closures/README.md` :33.** Replace *"**Evidence is write-once**, and a correction
after the fact is dated and says so."* with:
> **Evidence is write-once.** A correction after merge is a correcting `RL-` (`corrects:` the
> record), never an appended note. A maintainer's acceptance goes into the record before its
> merge, or into a maintainer `RL-` that `relates:` it.

**Not a T-text here:** `check_freeze`'s docstring (`audit-docs.py:2383-:2392`) and the
predicate's status clause (`:2169-:2171`). Both are code, and both belong to PL 9662's slice.

## What it obliges

- **PL 9662 (planner-freeze, WK-1170) names this ruling as its activation need A1**, by its
  minted id. It implements ¶2's forward-only status clause with the red `active → draft` test,
  ¶5's base rule and its CI guard, ¶6's deletion rule, and no allowlist input (¶7). Its own
  DP-1 to DP-3 are settled here: DP-1 option (a) by ¶3, DP-2 option (a) by ¶6, DP-3 the spec by
  ¶2.
- **WK-1170 takes a backlog item: "ledgers' append-only rule is not mechanically checked."**
  This is DP-4, out of PL 9662's scope (ledgers stay outside `_FROZEN_FAMILIES`) but owned here,
  per the maintainer's (by delegation) 13:43:31 entry, item 4, so it is not left unowned (`CLAUDE.md` §14). The lead
  enters it under WK-1170.
- **The applying PR** (WK-1170, after the maintainer's acceptance) lands T1-T5, citing RFC 9653
  and this ruling, before or with check 34's comparison going live.
- **Not decided here.** This ruling does not touch:
  - the 42 edits' content;
  - `migrate --verify`'s own reading of frozen files edited after the migration, which is
    FD-1413's;
  - how either base treats a `doc-id.py migrate` run's frozen-file stamping
    (`frozen_file_matches_after_migration_stamp`, `audit-docs.py:2302`), which is PL 9662's
    design;
  - the `decision:` cells of FD-1282 and FD-1323, which are the lead's.

## Acceptance — the violation that must become detectable

The violation: a frozen-family file's body or a header field outside row 34's list changes,
or the file is deleted, or its `status:` moves backwards, in the change under audit, and
`audit-docs.py` exits 0. Each item below names the broken input, and check 34 must fail on it.

- *Violation: one line appended to the body of a merged closure (CR-838's file) on a branch.*
  Check 34 exits 1 and names the file.
- *Violation: `slice:` or `relates:` changed on a merged `active` plan.* Check 34 exits 1.
- *Violation: `status: active` → `draft` on a merged plan.* Check 34 exits 1. Today's
  predicate passes it (DP-3).
- *Violation: a merged frozen file deleted.* Check 34 exits 1.
- *Violation: `AUDIT_DOCS_FREEZE_BASE=none` with `CI=true`.* The run exits 1.
- *Violation: an unresolvable base.* The run exits 1 and names the base, never skipping.
- *Violation: the check re-judges history.* A normal run at `99afcde2…` must print no row for
  any of the 42. Every run prints its base SHA.
- *Violation: the README practice survives.* After T4 and T5, `grep -n 'appended and
  dated\|is dated and says so' docs/findings/README.md docs/closures/README.md` prints nothing.
