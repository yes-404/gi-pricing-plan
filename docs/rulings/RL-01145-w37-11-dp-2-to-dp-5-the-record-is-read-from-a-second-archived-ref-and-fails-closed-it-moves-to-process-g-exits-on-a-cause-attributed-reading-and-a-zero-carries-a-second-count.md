---
id: RL-1145
family: ruling
title: W37-11 DP-2 to DP-5 — the residue record is read from a second archived ref and fails closed, it moves to process/, row (g) exits on a cause-attributed reading, and a zero in the phase report carries a second count
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-27
owner: decision-maker
tree: 271088b0ef99c48156ad7e96e7043bb8a3f6b613
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1144, PL-939, CR-1064, CR-1063, RL-1138, RL-1140, RFC-937, OQ-1146]
---

# RL-1145 — W37-11 DP-2 to DP-5: the residue record is read from a second archived ref and fails closed, it moves to process/, row (g) exits on a cause-attributed reading, and a zero in the phase report carries a second count

## Verified first, at 271088b0ef99c48156ad7e96e7043bb8a3f6b613

This rules the decision points of `PL-1144` (the W37-11 leaf plan) whose resolver is the
decision-maker: DP-2, DP-3, DP-4 and DP-5. DP-1 is the maintainer's by delegation, and the deputy's dated line is quoted in §DP-1 below. The plan
was read as a draft on branch `w37-11-plan-draft` at
`939a0f562907c89e9dee15db1e344ca1a0c7ecbf` (`status: draft`, `tree: 271088b0…`). It is not
on `main`; its Decision points table is at `:266-275` there. This record was drafted in the
decision-maker's own worktree, on branch `w37-11-dp-rulings-draft`, cut from `origin/main` =
`271088b0` (#818) with a clean status. Clock at drafting: 2026-09-27 11:24:10 BST (read by `TZ=Europe/London date` in the command that wrote this line).

**The id.** `python3 scripts/doc-id.py next` at `271088b0` prints `1144`. The planner's
unmerged draft already holds 1144, so this ruling takes **1145** and the open question it
raises takes **1146**, by the same reasoning.

**Retired paths are described, not spelled, in this record** (`RL-1140`'s convention).
"The audit directory" is the legacy pre-migration directory that `RFC-937` §1.4 dissolves.
Its pattern is `dict(_docid.LEGACY_FORM_PATTERNS)['legacy audit path']`. "The record" is the
residue-ceiling record at `_docid.W37_11_RECORD_PATH` (defined at `scripts/_docid.py:259`),
which is the directory's last tracked file.

### Facts re-measured at `271088b0`

| Plan's claim | Command | At `271088b0` |
|---|---|---|
| DP-2: the workflow pins `--ref` to `core.json`'s `meta.verified_against_tree` (`docs.yml:115-123`) | read `.github/workflows/docs.yml` | Reproduces. The `ref=$(python3 -c …verified_against_tree…)` line is `:117`, inside the `doc-id migrate --verify` step. The value is `0651c1e265648cbd3918adfc729ad965b83b1e0b`. |
| DP-2: the verify loads the record from `snap.control` (`_docverify.py:4366-4375`) | `grep -n 'record = load_w37_11_record' scripts/_docverify.py` | Reproduces: `:4375`, `record = load_w37_11_record(snap.control)`. The comment above it, which names F102, is `:4361-4374`. |
| DP-2: the F102 input-provenance table (`_docverify.py:4204-4223`) | read | Reproduces. The table starts at `:4199`, and its HERMETIC list names `load_w37_11_record(snap.control)`. |
| DP-2: `docs/open-questions.md` has no row for the question (`CR-1064:545`) | `grep -c -i -E 'pinned.base\|F109' docs/open-questions.md` | **0**. Reproduces. `CR-1064:545` reads *"raised in `docs/open-questions.md` with both options and a recommendation, **before** W37-11's acceptance is written"*. |
| — (not in the plan) | `git diff --stat 0651c1e origin/main -- <the record>` | **Empty.** The record has not changed since the pinned base. So F109 is latent: CI and the tree read the same record today, and the first record edit is the one that diverges. |
| — (not in the plan) | `load_w37_11_record` body, `scripts/_docid.py:1552-1597` | A record file that is missing returns `()`. It does not raise. `check_residue_ceiling`'s docstring (`:1671-1674`): *"A `cls` absent from the record entirely is ungoverned and produces no change either way"*. **So a record that is missing from the tree being read turns every ceiling off, silently.** |
| — (not in the plan) | the record's own header (`Re-keyed 2026-09-16`) | The record's `path` cells are keyed by **control (pre-migration) path**, not migrated path. |
| DP-3: `RFC-937` §1.4 sends the audit directory to `process/` | `grep -n 'dissolves' docs/rfcs/RFC-00937-*.md` | Reproduces at `:107`: the directory *"dissolves into `findings/`, `closures/`, `research/` and `process/`"*. The same sentence is at `docs/process/document-ids.md:107`. |
| DP-3: the findings-README redirect row gives the shape | `sed -n '3p' docs/REDIRECTS.csv` | Reproduces: empty `old_id`/`new_id`, the old path, `docs/findings/README.md`, empty `citing_dir`/`part_ordinal`. |
| DP-3: RL-1138 DP-1 amendments 1-2 carry the file and its reference limb to W37-11 | read `RL-1138` §DP-1 | Reproduces (`:75-86`). Amendment 2 did not adopt the "220 / 74" figure and requires *"a stated predicate"*. |
| — (not in the plan) | `document-ids.md:161`, the owner row | *"Reference — `process/` \| maintainer; amendments arrive as `RFC-` + `RL-`"*. The record's own opening paragraph says its *"Population is the deputy's"*. See DP-3, amendment 2. |
| DP-3: the reference limb, with the plan's predicate | `D=<pattern, by symbol>; git ls-files "$D" \| wc -l; git grep -l -F "$D" -- . ':!docs/REDIRECTS.csv' \| wc -l` | **1** tracked file (the record), and **183** files that reference the directory. The breakdown is in DP-3. |
| DP-4: #757 merged as `29e7a9ce` and is on main | `git show -s 29e7a9ce`; `git merge-base --is-ancestor 29e7a9ce origin/main` | Reproduces. The commit is `29e7a9ce41459ff1f4b4b2658d177c6109d35a58`, `2026-09-18T01:45:22+01:00`, subject *"… (251 → 207 classified-by-none; (g) stays the standing FAIL) (#757)"*. The ancestor check exits `0`. |
| DP-4: the (g) baseline is 207, not 251 | #757's squash body, the table *"Remaining 207 classified-by-none, re-derived by cause"* | Reproduces: 103 + 29 + 28 + 15 + 12 + 11 + 5 + 4 = **207**. |
| DP-4: a second reading of 207, built a different way | the `docs` workflow log on `main` at `271088b0`, run `36310860577` (`gh run view --log`) | The verify step logs `--ref 0651c1e…`, `classified-by-none=207` and `residue by cause: cause3-legacy-path-citation=103 …`, then `FAIL: (g)`, `UNCHANGED: 1 fatal row(s)` and *"--verify exited 1"*. **207 is also the standing CI reading on main today**, not only #757's own figure. |
| DP-5: `doc-index.py --phase P1b` prints seven elements, and six read zero or `—` | `python3 scripts/doc-index.py --phase P1b; echo EXIT=$?` | Reproduces: `EXIT=0`. The report has seven elements. Element 1 is not zero (4 closed, 1 retired). Elements 2-6 read `0` or `—`, and element 7 reads `(none)`. |
| DP-5: a second count for element 4, built a different way | `grep -l "^work: $w" docs/rulings/*.md` vs `grep -l "$w\b" docs/rulings/*.md`, for each Work in element 1 | For WK-661, WK-664, WK-665, WK-692 and WK-662: **0** rulings with a `work:` header, and **9, 2, 5, 2, 3** rulings that name the Work. Element 4's zero is a zero of header coverage, not a proven absence of rulings. |

### A defect found while verifying, which none of the DPs named

**`render()` in `scripts/_docverify.py` never prints the residue-ceiling block when the
verdict set is unchanged.** `_residue_change_block` has one caller, `_set_change_block`
(`:4474`), and that function returns early with the `UNCHANGED:` line when `set_changes`
is empty (`:4449-4454`). A throwaway probe built on the test suite's own `_result` pattern
(`tests/test_doc_id_verify.py:3224`) gave these results at `271088b0`:

- If a recorded ceiling now measures 0, `residue_changes` holds one `PROGRESSED (W37-11
  record can shrink)` and the exit code is `1`. The rendered text does **not** contain
  `RESIDUE CEILING`.
- If a residue grows into a file that the record does not name, `residue_changes` holds a
  `REGRESSION` and the exit code is **`3`**. The rendered text still says *"UNCHANGED … this
  change moved no row"*, and it does not contain `RESIDUE CEILING`.

So on every run where the verdict set does not change, which includes every CI run on
`main` today, the verify cannot print a `PROGRESSED` line. It also exits 3 on a residue
regression with text that says nothing moved. **`PL-1144`'s Acceptance item 6** (*"the
standing verify … prints no `PROGRESSED (W37-11 record can shrink)` line for them"*)
**therefore cannot fail as written.** Main's CI log at `271088b0` shows no `PROGRESSED`,
`REGRESSION` or `RESIDUE CEILING` line at all. That result is consistent with this defect.
It is not evidence that the census rows measure at their ceilings. This record does not
file the defect as a finding: the register is the auditor's file. The defect is reported to
the lead for filing, and DP-2 amendment 3 makes the fix part of W37-11's instrument PR.

## Ruled

### DP-1 — (j), which families are discharged now: **option (b) — Maintainer decision by delegation (deputy, 2026-09-27 11:16:34 BST)**

**This is not the decision-maker's ruling.** The resolver is the maintainer, by delegation
to the deputy, on the maintainer's instruction of 2026-09-26 17:02:52 BST. The deputy's
dated line is quoted verbatim from the lead's channel file (`to-lead.md`, a local handover
file that is not in the repository), in the entry headed *"2026-09-27 11:16:34 BST · deputy
· PL-1144: DP-1 RULED by delegation — option (b) …"*:

> **2026-09-27 11:16:34 BST — DP-1: option (b) ADOPTED.** The five families with a real
> item since the migration merge `71f5a22` — Closure, Finding, Plan, Ruling, Ledger — are
> **discharged now**, each verified in the W37-11 closure record by id, creating commit,
> creating skill and `doc-id.py check` rc at that commit. The eight without one are
> **owed**, each against the named event the row gives: Work at the minting of the charter
> investigation's `WK-` row; Slice at the first `SL-` row cut in that Work's map plan; Open
> question at DP-2's `OQ-` row if raised through `spec-change` with a number from `next`
> before the close, else at the audit's first slice; Requirement, Workflow, Decision,
> Proposal and Research at the first slice of the create-read-retire audit.

The same entry gives the ground (the row's predicate re-run at `271088b0`), and it states
that each owed row's verdict at the Work close is *"deferred with an owner"*. The decision-
maker verified the premise on its own, with the same predicate:
`git log --diff-filter=A --name-only 71f5a22..origin/main -- docs .claude`, grouped by the
family prefix. At `271088b0` it returns items in exactly five document families: CR (3),
FD (6), LG (4), PL (4) and RL (7). This agrees with the deputy's reading.

**One fact for the Open question event, recorded and not ruled.** The event names *"DP-2's
`OQ-` row if raised through `spec-change` with a number from `next`"*. OQ-1146 is that row,
raised through `spec-change`. Its number was **derived from** `next` and was not printed by
it: `next` printed 1144 at `271088b0`, 1144 was held by the unmerged `PL-1144`, and 1145 by
this ruling (§ Verified first). Whether that meets the event's wording is the deputy's
reading, and the closure record states it.

**Context, not ruled here.** In the same entry the deputy adopted the C1-C14 typing as the
plan proposes it, with four conditions. Two of them bear on this ruling. Condition 1 files
C9's register row and essay before the deferral. Condition 4 re-measures C3's g2 at the merge
tree beside 207 at `29e7a9c`, which DP-4 below also requires. DP-4 amendment 2's carried
item (the #757 rebuild) is not in C1-C14, so the deputy's typing does not cover it yet.

### DP-2 — where the standing verify reads the record (F109): **(c) adopted, with four amendments**

The verify gets a second archived ref for the record only (`--record-ref`). It is
extracted by `git archive` in the same way as `--ref`, and it defaults to `--ref`. In the
`docs` workflow's migrated-checkout branch, CI passes the commit under test (`HEAD`). The
corpus stays at the pinned base. Each input is a commit-keyed archive, so each run is still
hermetic, and later edits to the record become visible to CI.

- **(a) is refused.** It is not only weaker than (c), it is also incoherent with DP-3. The
  pinned base holds the record only at its legacy location. When DP-3 moves the file and its
  constant, `load_w37_11_record(snap.control)` will look for the new path in a tree where it
  does not exist and will return `()`. That turns every ceiling off with no message (the
  facts table above). C5 and C12 would also stay invisible to CI.
- **(b) is refused**, for the reason the plan gives: it undoes F102.
- **(d) is not ruled here.** Retiring the standing verify removes a gate, so it is a
  maintainer point, as the plan states. It is not adopted, and it is recorded here as the
  one option that this ruling does not have the authority to take.

**Amendments:**

1. **The record read fails closed.** On the verify path, a record that is missing in the
   `--record-ref` archive is a refusal: exit **2**, the code that `VerifyResult.exit_code`'s
   docstring reserves for *"a refusal to run at all — a misconfiguration"*. It never
   degrades to `()`. The degrade-to-empty behaviour of `load_w37_11_record` can stay for
   `audit-docs.py`'s own reader. That reader is not part of this ruling. **Broken-input
   proof:** a test runs the verify with a `--record-ref` whose archive lacks the record, and
   asserts exit 2 and a message that names the path it looked for.
2. **The provenance table gains a row.** The input-provenance comment at `:4199` lists
   `--record-ref` as a HERMETIC input, keyed on its own archive. It also records why the
   record's control-path keys still match a corpus read at `--ref`.
3. **The residue block prints whenever there are residue changes**, whether or not the
   verdict set changed. On a residue-only exit 3, the text no longer says that the change
   *"moved no row"*. **Broken-input proof:** one test renders an unchanged verdict set with
   one `PROGRESSED` change and asserts the line is present. A second test does the same with
   one fatal change and asserts both the line and exit 3. Acceptance item 6 becomes
   falsifiable only once this change lands, so it lands in the same instrument PR as F109.
4. **The census shrink is measured before it is applied.** Under (c), a record edit on a PR
   is compared at once against residue measured at the pinned base with the PR's own tool.
   If the three census rows are shrunk while they still measure above 0 there, every
   later CI run exits 3. `CR-1063` §3's 0 readings came from local runs at `e30a082` and
   `2307087`. #784's body expected *"After the migration merges they measure 0"*. Neither is
   a reading at the pinned base with the current tool, and main's CI cannot show one
   (amendment 3). **So before Task 4 edits the record, Task 1 or Task 4 reads
   `VerifyResult.measured_residue` for the three census keys directly, at the pinned base,
   with the instrument PR's tool, and quotes the three numbers.** The shrink lands only if
   all three read 0. If any does not, the executor stops and reports to the lead.

**The open question.** `CR-1064:545` asked for this question in `docs/open-questions.md`.
It is raised as **OQ-1146** (system level, mirrored in `docs/specs/00-overview.md` §10) and
decided by this ruling in the same commit. **One point is disclosed and not smoothed over.**
Read literally, `CR-1064:545` asks for the row *"before W37-11's acceptance is written"*.
`PL-1144`'s draft acceptance was written at 11:11:59 BST, before this row existed. The row
does exist before the plan goes active, and that is the earliest moment the acceptance binds
anything. Whether that meets `CR-1064:545`, or is a finding against the draft's order of
work, is the lead's reading and not this ruling's.

### DP-3 — where the record goes, and the remaining references: **(a) adopted, with four amendments**

The record moves to `docs/process/` as a living Reference document, and
`_docid.W37_11_RECORD_PATH` is updated. A `docs/REDIRECTS.csv` row is added in the shape of
`:3`. `process/` is where `RFC-937:107` sends the directory, and the record is a living
table. A frozen family (RS, CR) would contradict that. (b) would hide a governed table from
`doc-index`, and it would make each row edit a code edit. (c) would leave §7.1's clause
unmet, with no event to meet it.

**Amendments:**

1. **The constant is the only place in code that spells the new path.** Every reader
   (`_docid.py`, `_docverify.py`, `audit-docs.py`, `doc-id.py:665`, and the four test
   modules that `RL-1138` §1 lists) reaches it by symbol. The basename is the plan's to
   choose in Task 3, and it must say what the file is.
2. **The writer is stated, not assumed.** `document-ids.md:161` gives `process/` to the
   maintainer, with *"amendments arrive as `RFC-` + `RL-`"*. The record says its population
   is the deputy's. For this Work: the move is authorised by `RFC-937:107` together with
   this ruling, and the census shrink by DP-2 amendment 4 together with this ruling. The
   deputy writes as the maintainer's delegate. **This ruling does not decide** whether each
   row edit after the Work close needs its own `RFC-` + `RL-` pair under that owner row, or
   needs a carve-out. That is a question about the owner table, which is the maintainer's.
   It is reported to the lead as an open consequence of (a).
3. **The redirect row resolves frozen citations, and frozen records are not edited.**
4. **Every referencing file is placed in one class, and the parts sum to the whole.** At
   `271088b0`, the plan's predicate returns 183 files, and they fall into five classes:

   | Class | Files at `271088b0` | Disposition |
   |---|---|---|
   | Frozen governed records: `docs/closures` 45, `docs/findings` 42, `docs/plans` 22, `docs/rulings` 17, `docs/ledgers` 11, `docs/research` 7, `docs/rfcs` 6 | 150 | Resolved by the redirect row. Disclosed, not edited. |
   | Living documents: `docs/process` 6, `.claude/skills` 2, `docs/roadmap.md` 1 | 9 | Edited to the new location, or to a description of the old one. `.claude/skills` and `docs/roadmap.md` edits are made by their owners, per §1.6. |
   | Instruments and their tests: `scripts/` 6, top-level `tests/` modules 9, `tests/fixtures` 5, `backend/tests` 2 | 22 | Each file is read, never swept. A pattern that **defines** the legacy form (for example `LEGACY_FORM_PATTERNS`) stays, and so does a frozen fixture corpus. A **path to the record** moves with the constant. |
   | Generated: `docs/INDEX.md` | 1 | Regenerated. |
   | The record itself | 1 | Moved. |
   | **Total** | **183** | 150 + 9 + 22 + 1 + 1 = 183 |

   The closure record repeats this table at the move tree, with the predicate verbatim, and
   names every file in the "stays" part of the instrument class.

### DP-4 — what the Work close requires of row (g): **(b) adopted, with two amendments**

The exit measurement is the g2 `classified-by-none` figure at the merge tree. Every
remaining file is assigned to a cause, and the parts sum to the total. That figure is
reported against **207 at `29e7a9ce`** (reproduced twice: #757's table, and main's CI at
`271088b0`) and against 251 at `4d9fe1d`. (g) is put to the lead for a §13 verdict. The
plan proposes *"deferred with an owner"* and a named event. The verdict is the lead's
(`CLAUDE.md` §12, §13), not this ruling's. Whether a Work may close over an item that is
still FAIL stays with the delegate's dated acceptance line. (a) is refused because it has
no bounded plan: #757 showed that each cause needs its own classifier change. (c) is
refused by G3.

**Amendments:**

1. **The closure record states what the figure measures.** With `--ref` pinned, both
   `snap.control` and `snap.migrated` come from one fixed base. So g2 measures the invoking
   tool's classification of one historical migration, not the current corpus. A move away
   from 207 at the merge tree can only come from tool commits. The closure record names the
   commits in `29e7a9ce..<merge tree>` that touch the g2 classifier. If the figure moved
   while no such commit exists, that is a defect in the instrument and is reported, not
   explained away.
2. **The rebuild that #757 carried to W37-11 is typed, not dropped.** #757's squash body
   records the lead's decision, confirmed by the deputy: *"the g2 population is rebuilt in
   W37-11 once F109 decides the read location, with 207 as the baseline"* (103 of the 207
   residue keys had no ceiling entry). `PL-1144`'s carried-items table (C1-C14) has no row
   for it. DP-2 now decides the read location, so the plan adds it as a carried item for the
   deputy to type. This ruling does not type it.

### DP-5 — what counts as "containing" a zero or `—` element in (k): **(b) adopted**

Each element must be present. In addition, every reading that is zero, `—` or `(none)`
carries either a second count built a different way or a statement that it is zero by
construction, with the reason. A confident absence from one instrument needs a second,
independent check. The facts table shows the reason: element 4's zero for every P1b Work
sits beside 2-9 rulings that name each Work in their text. It is a zero of `work:`-header
coverage, and a reading of presence alone would have accepted it. Element 2's zero comes
from an empty family (`FD-1074`), and the closure record states that as the reason. (c),
also running with `--phase P2`, is useful, but it is outside (k)'s words, so it is not
required. (a) is refused on element 4's evidence.

**Amendment:** a second count does not have to agree with the first. Where it disagrees
(element 4 above), the closure record reports both counts, the predicate of each, and which
population each one counts. It does not choose one of them as "the" reading.

## What it obliges

- **`PL-1144`** moves `draft → active` with DP-2 … DP-5's "Resolved by" cells naming
  `RL-1145`, and DP-1's naming the deputy's dated line of 2026-09-27 11:16:34 BST (maintainer decision by delegation). The planner makes that edit in the
  activation PR. This ruling does not edit the plan (`document-ids.md` §1.6, PL row).
- **The plan's text changes that this ruling requires:**
  1. **Acceptance item 5** names OQ-1146 as the open-questions row, and names the three new
     broken-input tests: the record missing at `--record-ref` (exit 2), and the
     residue-block rendering tests for PROGRESSED and REGRESSION.
  2. **Acceptance item 6** measures from `measured_residue`, or from the fixed render. Until
     DP-2 amendment 3 lands, it must not read the rendered text.
  3. **Task 1 or Task 4** records the census pre-measurement of DP-2 amendment 4, with its
     stop condition.
  4. **Acceptance item 7 / Task 3** carries DP-3 amendment 4's five-class table at the move
     tree, and DP-3 amendment 2's statement of the writer.
  5. **Acceptance item 3 / Task 7** carries DP-4 amendment 1's attribution of any move to
     named tool commits.
  6. **Scope §A** gains the #757 rebuild as a carried item, for the deputy to type
     (DP-4 amendment 2).
  7. **Acceptance item 1 / Task 8** applies DP-5 with its amendment. Element 4's two
     counts are the first instance.
- **Owed by someone other than this role, and reported to the lead:**
  - the `docs/roadmap.md` §10 decision-gate row for OQ-1146. The `spec-change` skill puts
    it in the same commit, but the roadmap is not in this role's Tools line;
  - the register row, and an essay if the auditor judges one is needed, for the render
    defect found above;
  - DP-3 amendment 2's owner-table question, which is the maintainer's.

## Acceptance — the violation that must become detectable

- **DP-2:** a record edit on a PR that CI does not see. Detected by a verify run with
  `--record-ref HEAD` on a branch that changes one ceiling: the run prints the change. A
  missing record at `--record-ref` exits 2 (amendment 1's test). A residue-only change
  prints its line on an unchanged verdict set (amendment 3's tests).
- **DP-3:** a tracked file left in the audit directory, or a referencing file with no class.
  Detected by `git ls-files "$D" | wc -l` → `0`, and by the five-class table summing to the
  predicate's count at the move tree.
- **DP-4:** a g2 figure that moved with no attributed cause. Detected by the per-cause
  breakdown summing to the total, and by the named tool commits in amendment 1.
- **DP-5:** a zero accepted on one instrument's word. Detected by the closure record's
  element table, which has a second-count cell for every zero, `—` or `(none)` reading.
