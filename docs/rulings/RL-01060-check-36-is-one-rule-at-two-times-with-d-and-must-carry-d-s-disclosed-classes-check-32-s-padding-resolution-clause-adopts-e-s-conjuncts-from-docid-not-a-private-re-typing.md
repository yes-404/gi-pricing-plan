---
id: RL-1060
family: ruling
title: check 36 is "one rule at two times" with (d) and must carry (d)'s disclosed classes; check 32's padding/resolution clause adopts (e)'s conjuncts from `_docid`, not a private re-typing
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-04
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md
---

# W37-6 — RL-1060: check 36 adopts (d)'s disclosed classes, check 32 adopts (e)'s conjuncts from shared code (2026-09-04)

## RL-1060 — check 36 is "one rule at two times" with (d) and must carry (d)'s disclosed classes; check 32's padding/resolution clause adopts (e)'s conjuncts from `_docid`, not a private re-typing

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`, `scripts/doc-id.py:1329`) discovers this
     record as an `RL-` draft rather than falling through to `_discover_plain_plans`'s
     `PL- kind: leaf, owner: planner` catch-all — the same defect RL-1059's structural
     note names (F96, `docs/findings/FD-01055-a-filed-ruling-that-omits-the-ruling-n-heading-migrates-as-pl-owner-planner-and-nothing-catches-it.md`). -->

**Ruling number derivation, run by this executor in its own worktree
(`/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-a9d681ef6c46715c9`) at
`origin/main` = `2330f31`:**

```
git grep -ohE '^## Ruling [0-9]+' origin/main -- docs/ | grep -oE '[0-9]+' | sort -n | tail -5
  → 102, 103, 104, 105, 106
```

Highest allocated number on `origin/main` is **106**, so **107 is the next free number** —
confirmed, not assumed, matching the number the deputy's and the lead's code comments had
already guessed.

**A collision found while verifying, reported here rather than worked around:** `git grep -c
"RL-1060"` against every open W37-6 remote branch returns hits on two, for two
*different* rulings:

- `origin/worktree-h1-checks` (PR **#749**, `worktree-h1-checks`) — 4 hits, all in
  `scripts/audit-docs.py`, about the check-32 padding/resolution predicates this record
  files. This is the citation this record discharges.
- `origin/w37-6-h1-checks-31-32-36` (PR **#747**, `w37-6-h1-checks-31-32-36`) — 3 hits, all
  in `scripts/audit-docs.py:1740,1790,1792`, reading *"Contiguity (RL-1060) reads the
  full allocation via `docs/INDEX.md`"* — check **31**'s contiguity clause, a ruling the
  deputy stated separately in `to-lead.md:1360-1424` (2026-09-04, *"check 31's gap is the
  scanner's, not an allocation gap"*) and never labelled with a number there. That ruling is
  **not** part of what this record files — the deputy's own scoping sentence
  (`to-lead.md:1544`) names only the two entries transcribed below as what the label
  stands for.

Both PRs guessed the same free number for two different, still-unfiled rulings. Filing this
record as 107 makes #747's three `check_id_filename_directory` comments cite the wrong
ruling under the right number: they now need repointing to whatever number the check-31
contiguity ruling receives when it is filed (the next free number after this record lands,
i.e. **108** unless another filing intervenes first). Flagged to the lead in the same report
as this filing; not fixed here — `scripts/` and #747's own comments are out of this record's
scope by the dispatching brief.

No other open branch matches `RL-1060` under `docs/`, `.claude/`, or `scripts/`.

## Authority

The maintainer's delegation of 2026-09-03, exercised by the W37-6 deputy.
`~/gi-pricing-plan.local/channel/to-lead.md` carries the two entries transcribed in full
below, plus a later clarifying entry; this record is the filing the deputy's later entry
(`:1555`) explicitly asked for, not a restatement of authority the record does not itself
carry.

## Entry 1 — `to-lead.md:1257`, 2026-09-04, "h1's eight classes ruled"

Verified by the deputy at 20:1xZ against: `#736` merged at `2a9ed29` (the pgrep fix on
`main`), `#738` `CLEAN`, the eight-class table reconciling to 8368.

> **1. Check 36 = 5657.** `sweep_legacy_forms` (`audit-docs.py:2794`) is, in its own
> docstring, *"RFC-937 §7 acceptance item (d) and check 36's third clause are 'one rule at
> two times' (RL-988 §2), so both read this one function"* — same
> `_docid.LEGACY_FORM_PATTERNS`, every match counted, **no fence exclusion, no disclosed
> class, no test-module tuple, occurrences not lines**. So it counts what (d) counts *plus*
> everything today's rulings disclosed at (d): the `F<nn>`/`F-W` alias classes (RL-1046
> §A), the slice keys (d8), the never-allocated ids, the fenced exhibits, the 3c tuple. Two
> rules that were one rule now disagree, and h1 stays red on text (d) is green on. **Ruled:**
> check 36's third clause adopts (d)'s exclusions and disclosed classes **by the same
> predicates from the same shared constants** (`_docid.sweep_exclusion_reason`, the fence
> regex, the alias/slice/never-allocated predicates as the (d) rows implement them — moved
> into `_docid` if they are not there yet, never re-typed), prints each disclosed class by
> count, and fails only on what (d) fails on. Acceptance: check 36's fatal count and the sum
> of (d)'s fatal rows on the same snapshot **reconcile exactly** in the ledger; broken-input
> proof both ways — one undisclosed legacy form reds both, one `F-W` alias form is disclosed
> by both. Owner: exec-h1, after its classifier follow-up (task #43); it reads exec-ids' and
> executor-30-2's predicates rather than writing new ones.
>
> **2. Check 32 = 2286.** Its failures print as `check 32: <rel>:<problem>` (`:1893`). The
> ledger carries the **kinds**, grouped by problem text, with counts — resolution failures
> against `docs/INDEX.md` (a citation of an alias-class or never-allocated id cannot resolve
> and is the same disclosed class, rendered by W37-11's resolver) versus padding versus
> anything else. No fix is dispatched until the kinds are on the table; I expect most of it
> to be item 1's classes wearing a different message.
>
> **3. Check 1 = 250 broken links** — the link subset of d9–d13; exec-paths' landing
> discharges it and it is remeasured then, not worked separately.
>
> **4. The seven singletons — exec-h1's, now:** check 27 ×1 on a post-#735 tree means the
> reconcile missed a case — name it; the missing `## Acceptance Standard` ×1 and check 31 ×1
> are named and fixed; the undefined-FR ×1 falls under the never-allocated predicate
> (disclosed, not fixed); `ADR-1/2/3` ×3 are illustrative → 3a fence with the note.
>
> **What checkpoint 1 now reads against:** h1 green when checks 36 and 32 fail only on (d)'s
> fatal residue, check 1 is zero after exec-paths, and the seven are closed — measured on one
> snapshot, all rows in one run.
>
> *Violations: check 36 re-typing a predicate that exists in `_docid`; check 36's fatal count
> and (d)'s fatal sum differing on one snapshot after the fix; a check-32 fix dispatched
> before its kinds are tabled; a singleton "accepted" rather than fixed, fenced or disclosed
> by predicate.*

**Item 2's status, per the deputy's later clarification (`to-lead.md:1544`, 23:35 BST,
transcribed in full under "Discharge and rescoping" below): DISCHARGED.** The kinds were
tabled at 17:3x BST as **2043 / 240 / 3**, pushed in commit `b4f013c` on PR #738 (visible on
`origin/main` in `docs/plans/PL-01058-w37-6-migration-run-ledger.md`, one line). Nothing in
this entry or in entry 2 below asked check 32 to print a machine-readable classification —
only that the split be tabled in the ledger before a fix is dispatched, which it now is.

## Entry 2 — `to-lead.md:1272`, 2026-09-04, "check 32's 2043 padded ids are the same text row (e) reads as zero"

Cells on `origin/main` = `2a9ed29`.

> **The disagreement, named.** On one snapshot, row (e) prints **PASS at 0** and check 32
> prints **2043 "padded id outside a link target"**. Row (e) is RL-1044's four conjuncts
> (`_docverify.py:1025-1046`, `padded_hits`): exactly `PAD_WIDTH` digits with a leading zero;
> outside a fence and outside a `was:` line; **outside a filesystem path** (conjunct 2 — *"a
> path is not a citation"*); **resolving through `docs/INDEX.md`** (conjunct 3). Check 32's
> clause (`audit-docs.py:1827-1840`) is: any `0*` leading zero, outside a fence, outside a
> *markdown link target* — nothing about a bare path in prose, nothing about resolution. So a
> sentence like *"see `docs/plans/PL-00066-…md`"* — a path, written by every ruling and
> ledger entry today — is a violation to check 32 and not to (e). One text, two verdicts: the
> same defect as check 36, one clause over.
>
> **Ruled:**
> 1. **Check 32's padding clause adopts (e)'s conjuncts 0, 2 and 3 from shared code** — the
>    fence, the path exclusion (`_MD_EMPHASIS_RE`-stripped, as RL-1044 defect 3 required)
>    and the resolution test move from `_docverify` into `_docid` and both scripts read them
>    there; check 32 keeps its own `0*` breadth (RFC-937 §1.1 rule 2 is *"no exception"*, and
>    D6 names three spellings), so what remains after alignment is the **short-padded** class
>    (`PL-066`, `PL-0066` — real rule-2 violations (e)'s exact-width conjunct 1 does not see)
>    and it is **listed, not folded**. Acceptance on one snapshot: check 32's padded count =
>    (e)'s count (0) + the listed short-padded lines, each named; broken-input proof: a
>    `PL-00066` in prose reds both, a `docs/plans/PL-00066-x.md` path in prose reds neither, a
>    `PL-066` reds check 32 alone and is listed.
> 2. **The 240 "does not resolve"** are read against the disclosed predicates ruled today —
>    alias classes (`F<nn>`, `F-W`), slice keys, never-allocated ids — by the same shared
>    constants as check 36 (previous entry, item 1); what is left after those is a real
>    dangling citation and fails. Listed by id.
> 3. **The 3 link-text/target mismatches**: fixed, exec-h1.
> 4. **If the short-padded class is non-zero**, `_normalize_padded_citations` is widened to
>    it (it normalises through `_docid.canonical`, which already treats the three spellings
>    as one id) — the migration's own remedy, #25's precedent, no new mechanism.
>
> **Owner:** exec-h1, in the same PR as check 36's alignment (one "checks read (d)/(e)'s
> predicates" change, one review). **Before code:** the 2043 split by kind — bare path in
> prose / short-padded / unresolvable-padded — from the kept log, in the ledger; that split
> is what the acceptance figure is checked against, and it is what tells us whether item 4
> has any work.
>
> **Priced and refused:** relaxing check 32 to link targets only (rule 2 says link text too);
> exempting the ledger and rulings from check 32 because they cite paths (a document-keyed
> exemption; the path conjunct already answers it by predicate).
>
> *Violations: a padding or resolution predicate typed in `audit-docs.py` that exists in
> `_docid`; check 32 and (e) printing different verdicts on one padded citation after this;
> the 2043 split absent from the ledger when the PR opens.*

## Discharge and rescoping — `to-lead.md:1538-1555`, 2026-09-04 23:35 BST, "deputy ruling: three questions"

This is the entry that both corrects Entry 1 item 2's status and scopes what PR #749 owes.
Objects read: `origin/main` = `2330f31`; #749 head `3798401`; #747 head `ec31a5b`; #748
worktree `24fe074`; `to-lead.md:1257-1290`; `docs/rulings/INDEX.md#2026-09-02-w37-ruling-a-series-and-standalone-ruling-filesmd`
§3 at `origin/main`.

> **"RL-1060" is a label, not a record.** `git grep 'RL-1060'` returns nothing [as a
> filed record] on `origin/main`, on any remote branch, or in either channel file; its only
> trace is the Slack reporter log. The rulings the label stands for are my two entries at
> `to-lead.md:1257` (item 2: *the ledger carries the kinds, grouped by problem text, with
> counts … no fix is dispatched until the kinds are on the table*) and `to-lead.md:1272`
> (items 1–4). The kinds were tabled at 17:3x BST — 2043 / 240 / 3 — and pushed in `b4f013c`
> on #738. **That deliverable is discharged.** Nothing in either entry asks check 32 to print
> a classification. The executor's `test_check_32_lists_kinds_of_failures` tests a
> requirement nobody ruled, and it goes: **deleted, not renamed.**
>
> **Q2 answered from the record:** the kinds are the problem texts check 32 already prints
> (`check 32: <rel>:<problem>`). The ruled split of the 2043 is bare-path-in-prose /
> short-padded / unresolvable-padded, and each has a ruled fate: the first ceases to fail
> under conjunct 2; the second is *listed, not folded* (item 1); the third is read against
> the disclosed-class predicates and what remains is listed by id (item 2). No note format is
> invented by anyone.
>
> **What #749 actually owes, and does not yet meet.** Item 1 rules that check 32's padding
> clause adopts (e)'s conjuncts 0, 2 and 3 **from shared code** — moved from `_docverify`
> into `_docid`, both scripts reading them there — with the violation clause *"a padding or
> resolution predicate typed in `audit-docs.py` that exists in `_docid`"*. #749 @ `3798401`
> adds `_MD_EMPHASIS_RE`, `_TOKEN_BOUNDARY_RE`, `_TRAILING_LINE_LOCATOR_RE` and
> `_in_path_context` **as private definitions in `audit-docs.py`**, and implements conjunct 2
> only. That is the refused shape verbatim. #749 does not merge with the private copies,
> whatever its tests say.
>
> **Q1 ruled: #749 is re-scoped to item 1 in full, and items 2–4 follow in a second PR.**
> - #749 = the three conjuncts (fence, path exclusion with `_MD_EMPHASIS_RE` stripping,
>   resolution through `docs/INDEX.md`) defined once in `_docid`, `_docverify.py`'s
>   `padded_hits` and `audit-docs.py` check 32 both reading them; the short-padded class
>   listed. Tests are the acceptance line at `to-lead.md:1279` made executable on a fixture
>   tree: a `PL-00066` in prose reds both (e) and check 32; a `docs/plans/PL-00066-x.md` path
>   in prose reds neither; a `PL-066` reds check 32 alone and is listed. Each with its
>   mutation line (see C, standing rule).
> - Second PR, after #747 lands its disclosed-class constants for check 36: item 2 (the 240
>   read by the same constants, remainder listed by id) and item 4 (widen
>   `_normalize_padded_citations` if short-padded is non-zero). Item 3 (three mismatches)
>   stays with exec-h1 in whichever of the two lands first.
> - The path-exclusion test survives (its M3 proof is real); it moves under `tests/` with the
>   others. **Predicted python total: the executor states it** — `3233` plus the number of
>   collected tests in the moved module — before the push. I retract my `3235`; it assumed
>   two tests I have now ruled to one-plus-new.
>
> **Before either #747 or #749 merges, the ruling is filed.** Both branches carry code
> comments citing "RL-1060". A citation that resolves in no document is RFC-777's case.
> The lead files the two `to-lead.md` entries as one dated ruling record under `docs/plans/`
> through the ruling skill, with whatever number the sequence gives (verify `107` is actually
> next; do not assume), and the comments cite the record's path. A blocker for merge, not for
> coding.

The bracketed clause `[as a filed record]` above is this record's own insertion for
readability — the deputy's literal sentence read "returns nothing on `origin/main`, on any
remote branch," which the number-collision check above (this record's own derivation
section) shows is imprecise taken word-for-word: `git grep 'RL-1060'` *does* return hits,
on `origin/worktree-h1-checks` and `origin/w37-6-h1-checks-31-32-36`, as unfiled code-comment
labels rather than a filed record. The deputy's very next sentence — "Both branches carry
code comments citing 'RL-1060'" — already says this; the insertion makes the two
sentences read consistently rather than leaving the first as a literal false statement.

## Where this lands

- **This record** — the ruling, dated and frozen at this date per `docs/plans/README.md`.
- **`scripts/_docid.py`** (or wherever the shared predicate module lands) — gains
  `sweep_exclusion_reason` and the disclosed-class predicates (alias, slice-key,
  never-allocated) that check 36 must read rather than re-type, and the three conjuncts
  (fence, `_MD_EMPHASIS_RE`-stripped path exclusion, `docs/INDEX.md` resolution) that check
  32's padding clause and row (e)'s `padded_hits` must both read. Not this record's PR to
  write — #747 and #749 (re-scoped per the discharge/rescoping entry above) carry the code.
- **`scripts/audit-docs.py`** checks 36 and 32 — read the shared predicates, no private
  re-typing. Same caveat: code lands in #747/#749, not here.
- **The ledger** (`docs/plans/PL-01058-w37-6-migration-run-ledger.md`) — already carries
  the 2043/240/3 split (`b4f013c`, PR #738) and the h1 eight-class table; this record cites
  both rather than restating their figures a second time a reader could find stale.

## Acceptance — the violations that must become detectable

*Violation: check 36 re-typing a predicate that exists in `_docid`.*
*Violation: check 36's fatal count and (d)'s fatal sum differing on one snapshot after the
fix.* Broken-input proof both ways: one undisclosed legacy form reds both; one `F-W` alias
form is disclosed by both.

*Violation: a check-32 fix dispatched before its kinds are tabled in the ledger.* (Discharged
by `b4f013c` on #738 before this record was filed — kept as a standing rule for any future
check-32-shaped clause, not because it is still open.)

*Violation: a singleton (check 27, the missing `## Acceptance Standard`, check 31, the
undefined-FR, `ADR-1/2/3`) "accepted" rather than fixed, fenced, or disclosed by predicate.*

*Violation: a padding or resolution predicate typed in `audit-docs.py` that exists in
`_docid`.* Broken-input proof: a `PL-00066` in prose reds both (e) and check 32; a
`docs/plans/PL-00066-x.md` path in prose reds neither; a `PL-066` reds check 32 alone and is
listed, not folded.

*Violation: check 32 and (e) printing different verdicts on one padded citation after this.*

*Violation: the 2043/240/3 split absent from the ledger when the check-32 PR opens.*
(Discharged — see above; kept as a standing rule.)

*Violation: `test_check_32_lists_kinds_of_failures` (or any test asserting check 32 must
print a machine-readable classification) surviving in a merged PR — nobody ruled that
requirement; it is deleted, not renamed, per the discharge entry above.*

*Violation: PR #749 merging with `_MD_EMPHASIS_RE`, `_TOKEN_BOUNDARY_RE`,
`_TRAILING_LINE_LOCATOR_RE`, or `_in_path_context` defined privately in `audit-docs.py`
rather than read from `_docid`.*

## What this does not decide

Whether the check-31 contiguity clause (the deputy's separate `to-lead.md:1360-1424` ruling,
cited in PR #747's code comments as "RL-1060" — the collision named in this record's
derivation section) is correct as ruled, or what number it receives when filed. That ruling
is not transcribed here because the deputy's own scoping sentence (`to-lead.md:1544`) does
not name it as part of the "RL-1060" label's content; it needs its own filed record and
its own number, next in sequence after this one.

Whether PR #747's or #749's actual diff, as pushed, satisfies the rules above — that is a
question for whoever reviews those PRs against this record, not for the record itself.

## Acceptance Standard

Discharged when:

1. PR #749, re-scoped to item 1 of the check-32 entry in full (the three conjuncts moved
   into the shared predicate module, both `_docverify.py`'s `padded_hits` and
   `audit-docs.py` check 32 reading them there, the short-padded class listed rather than
   folded, the acceptance-line broken-input proofs as tests), merges under `lead.md`, with
   its code comments repointed from the bare string "RL-1060" to this record's path.
2. PR #747 lands check 36's alignment with (d)'s shared predicates (Entry 1 item 1) as its
   own commit satisfying the same "reads the shared constant, never re-types it" rule.
3. The second PR (items 2 and 4 of the check-32 entry, after #747's disclosed-class
   constants for check 36 land) merges under `lead.md`.
4. The check 36/check 32 reconciliation and short-padded acceptance figures are measured on
   one snapshot and recorded in the ledger, per the acceptance lines transcribed above.

This ruling record is accepted when the lead (this session, or its successor) merges the PR
implementing item 1 above; its substance binds from that point, same as any other ruling
record in this project.
