---
id: PL-1144
family: plan
kind: leaf
title: W37-11 — Prove it, acceptance (j) and (k), and the closure evidence: leaf plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-27
owner: planner
tree: 271088b0ef99c48156ad7e96e7043bb8a3f6b613
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
---

# W37-11 — Prove it: acceptance (j) and (k), and the closure evidence

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax
> for tracking. **Executor skill: `close-workstream`** (map plan sequencing row, `PL-939:383`).

**Goal:** Close WK-697. Prove RFC-937 §7 acceptance items (j) and (k), discharge or type every
item carried to this slice, and file the Work's closure record so that the maintainer's
delegate can accept the Work close with a dated line.

**Architecture:** This is the last slice of the map plan
[`PL-939`](PL-00939-wk-697-one-id-per-governed-thing-map-plan.md) (slice section `:839-859`,
sequencing row `:383`, depends on W37-7 … W37-10, all merged). Its work has three parts. The
**instrument part** is small code in `scripts/_docverify.py`, `scripts/_docid.py`,
`scripts/doc-id.py` and `.github/workflows/docs.yml`: F109, the record move, the census-row
shrink, F110, and the idempotence proof. The **proof part** is (j) and (k), and it is
measurement only. The **synthesis part** is one `CR-` record of kind `work` under
`docs/closures/`, plus the roadmap row. The Decision points table fixes the instrument part's
shape. Nothing in the instrument part starts before its decision point has a resolver id.

**Tech Stack:** Python 3.12 standard library for the three gate scripts (map plan G4,
`PL-939:128-136`). `pytest` for their tests. Git plumbing. No new dependency.

**Spec:** [RFC-937](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md)
§7 (`:435`: (j) *"one new item per family born through its skill with a number from
`doc-id.py next`"*; (k) *"`doc-index.py --phase P1b` produces the report §1.10 describes"*),
§1.10 (the report's elements), §1.2 (the family table, restated at
[`document-ids.md`](../process/document-ids.md) §1.2 `:32-50`), and §8 (`:441`, the two
downstream Works). The parent is the map plan named above: Acceptance Standard items 8–12
(`PL-939:84-99`) and DP-4 (`:305`).

## Goal

WK-697 closes with every RFC-937 §7 acceptance item evidenced or given a §13 verdict. (j)
and (k) are proven. Each item carried to this slice is discharged or typed under the
successor rule below. One `CR-` record of `kind: work` holds all of it, and the Work close is
accepted with a dated line. "Done" is the Acceptance Standard below. Every item in it is a
command or a named artifact.

## Status — this plan is a DRAFT and is not filed

`status: draft`, per [`document-ids.md`](../process/document-ids.md) §1.7. A plan with an
open blocking row in its Decision points table stays `draft`. Drafted 2026-09-27 11:11:59 BST by the
planner, against `origin/main` = `271088b0` (#818), under the lead's brief and the deputy's
ruling of 2026-09-27 11:00:45 BST on what the draft must carry.

**What still blocks:** resolver ids on DP-1, DP-2, DP-3 and DP-4. The decision-maker mints
one `RL-` after this draft is reported. This plan moves `draft → active` in the commit that
writes those resolver ids. `created:` does not change.

**Two facts found at drafting that the brief did not state.** Both were verified at
`271088b0`:

1. **#757 is already merged.** The roadmap row (`docs/roadmap.md:766`) still reads
   *"W37-11's first item is `#757` (rebase onto `71f5a22` …)"*. But #757 merged as
   `29e7a9ce41459ff1f4b4b2658d177c6109d35a58` on 2026-09-18 at 01:45:22 BST. It is an
   ancestor of `origin/main` (`git merge-base --is-ancestor 29e7a9ce origin/main` → 0). Its
   squash subject reads *"(251 → 207 classified-by-none; (g) stays the standing FAIL)"*. The
   W37-6 ledger records the merge ([`PL-1058`](PL-01058-w37-6-migration-run-ledger.md)
   `:2044-2056`), and so do [`PL-1070`](PL-01070-w37-7-the-remaining-creating-and-reading-instruments-leaf-plan.md)
   `:339` and [`PL-1072`](PL-01072-w37-9-root-governance-claude-md-and-the-public-face-leaf-plan.md)
   `:147`. So this plan's first item is **not** "land #757". It is the re-measure that
   discharges the condition in the lead's dated decision: *"the decision stands unless that
   re-measure shows a corpus-correctness defect"* (`CR-1064:464-470`). The baseline for (g)
   is **207 at `29e7a9c`**, not the 251 at `4d9fe1d` that `CR-1064:547` names. The roadmap
   row is corrected in Task 11.
2. **The pinned-base open question does not exist.** `CR-1064:545` requires the pinned-base
   read to be *"raised in `docs/open-questions.md` with both options and a recommendation,
   **before** W37-11's acceptance is written"*. At `271088b0`,
   `grep -n -i -E 'pinned.base|F109' docs/open-questions.md` returns nothing. This draft
   writes an acceptance standard anyway, because the lead asked for one. **The condition is
   unmet, and DP-2 names it as a precondition of freeze.** The planner may not write
   `docs/open-questions.md` (`.claude/roles/planner.md`, Tools).

**Activated 2026-09-27 11:30:32 BST (planner, on RL-1145 and the deputy's rulings).** The paragraphs above
are kept as the record of the state at drafting. What changed:

- **Every blocking decision point now has a resolver.** DP-1 is the deputy's line of
  2026-09-27 11:16:34 BST, a maintainer decision by delegation, quoted verbatim in RL-1145.
  DP-2 to DP-5 are RL-1145: DP-2 (c), DP-3 (a), DP-4 (b) and DP-5 (b), each with amendments.
  So this plan moves `draft → active` in this commit, under `document-ids.md` §1.7.
  `created:` does not change. **Frozen / dated: 2026-09-27.** Where this text and RL-1145
  disagree, the ruling governs.
- **Fact 2 is resolved.** The decision-maker raised the open question as **OQ-1146**
  (system level, mirrored in `docs/specs/00-overview.md` §10) and decided it in RL-1145. The
  lead read `CR-1064:545` as **met**, because OQ-1146 lands before this plan freezes. RL-1145
  records that reading as the lead's, not the ruling's.
- **The deputy's rulings folded in** (the lead's local channel file, 2026-09-27): 11:16:34
  (DP-1, the adoption of C1–C14 with four conditions, and the code PR's gate); 11:21:57
  (F16); 11:27:20 (F17, F18); and 11:28:23 (C15, C16, F19, the OQ-1146 gate row, DP-3
  amendment 5, and the activation assembly).

**The activation PR** (`w37-11-activation`) is cut from `main` after #819 merges. It carries,
in this order:
1. the planner's and the decision-maker's commits, by `git cherry-pick`, never by rebase;
2. the auditor's single commit filing C16's `FD-` register row and essay, so the finding is
   on `main` before the code PR that fixes it;
3. the lead's commit, which writes the `docs/roadmap.md` §10 decision-gate row for OQ-1146
   as a pointer to a decided question ("decided, RL-1145 DP-2"), and regenerates
   `docs/INDEX.md`.

The docs checks run on the committed tree with the control pair. Then the deputy gives the
ACK and the lead merges. The planner touches neither INDEX nor the roadmap.

## The successor rule this plan was cut against

**From `CR-1064:433-438`, as one sentence: an item carried to W37-11 is either (j) or (k),
synthesis, or a named acceptance item with its own exit measurement, and nothing else is
carried there.** Under the deputy's ruling of 2026-09-27 11:00:45 BST, one more type is
permitted: **deferred, with the lead as owner and a named event**. Each carried item's type
below was the planner's proposal. **The deputy adopted the typing of C1–C14 as proposed on
2026-09-27 at 11:16:34 BST, under four conditions** (Scope A, after the table). C15 and C16
were adopted at 11:28:23 BST.

## Acceptance Standard

Each item is a command that a fresh reviewer can run, or a named artifact they can read at a
named tree. Nothing here is satisfied by inspecting this plan. "The merge tree" means the tree
of the squash commit that lands this slice's last PR.

1. **(k), checked element by element.**
   `python3 scripts/doc-index.py --phase P1b; echo EXIT=$?` prints `EXIT=0` and seven numbered
   elements. The closure record has a table with one row for each clause of map-plan item 10
   (`PL-939:89-92`). Each row gives the clause, the element number and the printed line
   verbatim. The clauses are: Works closed and retired; slices planned versus delivered;
   plans superseded per Work; rulings per Work; findings opened versus discharged, with the
   unowned-decay count; documents with no inbound citation outside `INDEX.md`; and days from
   `active` to closure. **Under DP-5 (RL-1145)**, each reading that is zero, `—` or
   `(none)` also carries a second count built a different way, or the reason it is zero by
   construction. **Amendment:** the second count does not have to agree with the first.
   Where the two disagree, the closure record reports both counts, the predicate of each and
   the population each one counts, and it does not pick one. Element 4 is the first instance:
   every P1b Work has 0 rulings with a `work:` header, but 9, 2, 5, 2 and 3 rulings name
   WK-661, WK-664, WK-665, WK-692 and WK-662 in their text (RL-1145, facts table).
2. **(j), family by family.** The closure record has a table with **thirteen** rows, one for
   each family in `document-ids.md` §1.2 (`:36-49`). The row families are Requirement, Open
   question, Work and Slice. The document families are Workflow, Decision, Proposal, Plan,
   Ledger, Ruling, Research, Closure and Finding. Each row is in one of two states. A
   **discharged** row names the item, its commit, the creating skill, and the result of
   `python3 scripts/doc-id.py check` at that commit. An **owed** row names the downstream
   event that will discharge it. **No row may be owed without a named event**
   (`PL-939:850-851`: *"A family recorded as owed with no named event is a finding, not an
   acceptance"*). DP-1 fixes which rows are which.
3. **Row (g), a first-class item with its own exit measurement.** Run
   `python3 scripts/doc-id.py migrate --verify <throwaway dir> --ref <the migrated
   pre-migration base, per Task 1 step 3>` at the merge tree. Its g2 `classified-by-none`
   figure is printed with a per-cause breakdown, and the parts sum to the whole. The closure
   record reports it against **207 at `29e7a9c`** and against 251 at `4d9fe1d`. The verdict on
   (g) follows DP-4 (RL-1145, (b)): it is the lead's §13 verdict, and the plan proposes
   "deferred with an owner" with a named event. **DP-4 amendment 1:** with `--ref` pinned, g2
   measures the invoking tool's classification of one historical migration. So the closure
   record names every commit in `29e7a9ce..<merge tree>` that touches the g2 classifier
   (`git log --format='%h %s' 29e7a9ce..<merge tree> -- scripts/doc-id.py
   scripts/_docverify.py scripts/_docid.py`, each classified by reading its diff). If the
   figure moved and no such commit exists, that is a defect in the instrument and is
   reported. **Condition 4:** the baseline is re-measured, not inherited.
4. **Idempotence, not determinism (F107, [essay](../findings/FD-01066-pl960-909-idempotence-second-migrate-run-zero-diff-not-proven.md)).**
   A second `python3 scripts/doc-id.py migrate` runs over an already-migrated throwaway
   snapshot, and `git status --porcelain` on that snapshot is empty afterwards. The closure
   record states that this proves **idempotence**, because the determinism of a first run was
   already proven (T⁗ = T⁵ = `6d058ba6`, `CR-1063` §5). It gives the starting figure verbatim
   from `CR-1064:414`: `41 hit(s) … ceiling of 15 for 'd10'`.
5. **F109 resolved as DP-2 rules (RL-1145, (c): `--record-ref`), with broken-input proofs.**
   OQ-1146 is the open-questions row that `CR-1064:545` requires, and RL-1145 decides it.
   Three tests, each shown failing on deliberately broken input and passing at the head of the
   code PR, are named in the closure record with their failure messages:
   (i) a ceiling changed at `--record-ref` is seen by the verify (the F109 property);
   (ii) **a record missing from the `--record-ref` archive exits `2`**, with a message that
   names the path it looked for (DP-2 amendment 1: it never degrades to `()`);
   (iii) C16's two render tests (see item 16).
   The input-provenance comment in `scripts/_docverify.py` (the table beside the F102 fix)
   gains a HERMETIC row for `--record-ref` (DP-2 amendment 2).
6. **The census-row shrink (`CR-1063` §3, `:213`).** The three per-file census rows of the
   residue-ceiling record read `0`. **DP-2 amendment 4:** before the edit,
   `VerifyResult.measured_residue` for the three census keys is read directly at the pinned
   base with the code PR's tool, and the three numbers are quoted. The shrink lands only if
   all three read `0`. **The exit is read from `measured_residue`, or from the render after
   C16's fix lands. It is never read from the render before that**, because until then the
   render cannot print `PROGRESSED` on an unchanged verdict set (RL-1145, "A defect found
   while verifying").
7. **The residue-ceiling record has left the legacy audit directory, and the reference limb
   is measured (RL-1138 DP-1, amendments 1–2; `PL-1073:76-79`).** Derive the directory from
   the shipped pattern table by symbol, and never type it:
   ```bash
   D=$(python3 -c "import sys; sys.path.insert(0,'scripts'); import _docid; print(dict(_docid.LEGACY_FORM_PATTERNS)['legacy audit path'].pattern)")
   git ls-files "$D" | wc -l                                  # 0
   git grep -l -F "$D" -- . ':!docs/REDIRECTS.csv' | wc -l    # the reference limb, per DP-3
   ```
   The first command prints `0`. The second command's reading, and the predicate above
   verbatim, are in the closure record with DP-3's disposition of every remaining file.
   **DP-3 amendment 4:** every referencing file falls into one of five classes, and the parts
   sum to the whole. At `271088b0` the reading was **183 = 150 + 9 + 22 + 1 + 1**: frozen
   governed records 150 (resolved by the redirect row, disclosed, not edited); living
   documents 9 (edited by their owners, per §1.6); instruments and their tests 22 (each read,
   never swept — a pattern that *defines* the legacy form stays, and a *path to the record*
   moves with the constant); generated `INDEX.md` 1 (regenerated); and the record itself 1
   (moved). The closure record repeats the table at the move tree, and names every file in the
   "stays" part. **DP-3 amendment 1:** the constant is the only place in code that spells the
   new path. **The writer (DP-3 amendment 2, and amendment 5 by the deputy's delegated ruling
   of 11:28:23 BST):** after the move, the record's rows are written by the lead of the slice
   that discharges or re-measures a residue, citing that slice's closure record or an `RL-`.
   The document's frame (header, rules, columns) stays the maintainer's under
   `document-ids.md` §1.6's `docs/process/` row.
8. **F110 ([essay](../findings/FD-01069-h1-residue-by-file-and-tracked-files-docstrings-disagree-on-population.md)).**
   The docstring of `_h1_residue_by_file` and the docstring of `tracked_files` in
   `scripts/_docverify.py` name the same population. A test asserts that population on a
   fixture that contains one sweep-excluded file.
9. **The closure record exists.** It is a `CR-` of `kind: work` under `docs/closures/`, with an
   id from `python3 scripts/doc-id.py next`. It carries all of these: the H-row table (map
   item 8, `PL-939:84-85`); the ten broken-input proofs for checks 30–39 (map item 11,
   `:94-97`); the §7 (a)–(h) evidence; the tables of items 1, 2 and 3 above; the scope
   table's "day's faces" rows; the carried-items table with each item's type; and a §13
   verdict for every item without evidence. The verdict is one of delivered but untested,
   deferred with an owner, reassigned, or not started. **Silence is not a verdict**
   (`CLAUDE.md` §13).
10. **The roadmap row is updated.** `docs/roadmap.md`'s WK-697 row records the close and cites
    the closure record, per `close-workstream` (map item 12, `PL-939:98-99`).
11. **The docs gates are green at the merge tree.** `python3 scripts/audit-docs.py` exits 0
    with `All checks passed.` and its `DISCLOSED (N, …)` line is quoted. `python3
    scripts/doc-id.py check` exits 0. `python3 scripts/doc-index.py --check` exits 0.
12. **Both halves of the gate are green** at the head of each PR (`CLAUDE.md` §11).
13. **The deputy's merge acknowledgement is recorded** on each PR before the lead merges, and
    the slice's clean audit is filed. This is the convention of
    [`PL-1070`](PL-01070-w37-7-the-remaining-creating-and-reading-instruments-leaf-plan.md)
    item 11 (`:1732-1735`), which this plan carries from the start.
14. **The Work close is accepted with a dated line**, under D7 by delegation. The deputy
    decides line 5 once the closure record exists (see Task 13). A Work close is the
    maintainer's (`CLAUDE.md` §12, §13). This slice's own close is not.
15. **C15 — #757's g2 per-file entries are rebuilt at the DP-2 read location.** The exit is
    the reading at the merge tree, with its predicate verbatim, next to 207 at `29e7a9c`
    (#757's squash body: 103 of the 207 residue keys had no ceiling entry).
16. **C16 — the verify-render defect is fixed (DP-2 amendment 3).** Two render tests: a
    `PROGRESSED` change on an unchanged verdict set prints `RESIDUE CEILING`, and a
    `REGRESSION` prints it and exits `3`, with text that no longer says the change *"moved no
    row"*. Each test is shown **failing at `271088b0`** and **passing at the code PR's head**.
    The `FD-` register row and essay are on `main` before the code PR (the activation PR).
    The closure record types C16 as "fixed in W37-11 by <squash>".
17. **Every deferred row meets the deputy's conditions 1–3.** C7, C9, C11, C14, F16 and F18
    each have a register row on `main` before they are deferred (condition 1; for C9, F16 and
    F18 that row is the first commit of the docs PR). Each one's named event is quoted
    verbatim, and its reading is re-taken at the merge tree with the predicate printed
    (condition 2). C14 is recorded as the lead's verdict with the disposition of the 15
    already-minted ids (condition 3).

## Global Constraints

The map plan's G1–G5 apply (`PL-939:107-170`). These bind hardest here:

- **G3 — no acceptance item is weakened.** *"Where an acceptance item is not executable as
  written, the plan supplies the executable form and names it as such … it never lowers the
  bar."* DP-4 and DP-5 are executable forms. Neither is a relaxation.
- **G4 — the gate scripts use the standard library only.** The F109 and relocation code may
  not import a third-party package.
- **A new governed file never spells a legacy path.** It describes the path (RL-1140's
  convention). A brand-new file cannot be listed in the residue-ceiling record, so one
  spelled legacy path is fatal in `audit-docs.py` check 36. This applies to the closure
  record and to every file that Tasks 2–10 create.
- **Cite the residue-ceiling record by symbol** (`_docid.W37_11_RECORD_PATH`). Never paste its
  value.
- **Stop a process only by PID**, after `readlink /proc/<pid>/cwd` shows that it is yours
  (executor charter S-9). **End the turn after every report and every commit** (S-10).

## Scope

### A. The carried items, typed (adopted by the deputy on 2026-09-27: C1–C14 at 11:16:34 BST, C15 and C16 at 11:28:23 BST)

| # | Item | Source | Proposed type | Exit measurement, or owner and event | Task |
|---|---|---|---|---|---|
| C1 | (k) | RFC-937 §7 `:435`; `PL-939:845-846` | **(k)** | Acceptance item 1 | 8 |
| C2 | (j) | RFC-937 §7 `:435`; `PL-939:847-851`; DP-4 of the map plan | **(j)** | Acceptance item 2; DP-1 | 9 |
| C3 | Row (g), with #757 recorded as its first item (already merged, `29e7a9c`) | `CR-1064:415`, `:547`; roadmap `:766`; lead's decision `CR-1064:464-470` | **named acceptance item** | Acceptance item 3; baseline 207 at `29e7a9c`; DP-4 | 7 |
| C4 | Idempotence (F107) | register `:147` and its essay; `CR-1064:414`, `:546` | **named acceptance item** | Acceptance item 4 | 5 |
| C5 | The census-row shrink | `CR-1063` §3 `:213-238`; roadmap `:766` | **named acceptance item** | Acceptance item 6; depends on DP-2 | 4 |
| C6 | The pinned-base read (F109) | register `:149` and its essay; `CR-1064:413`, `:545` | **named acceptance item**, with its design choice at DP-2 | Acceptance item 5 | 2 |
| C7 | The check-35 two-clause shape (F108) | register `:148` and its essay | **deferred, lead as owner** — an output-shape question with no exit measurement until someone decides it | Event: the first slice of RFC-937 §8's create-read-retire audit Work. Recorded in the closure record | 10 |
| C8 | The docstring mismatch (F110) | register `:150` and its essay | **named acceptance item** | Acceptance item 8 | 6 |
| C9 | The gap where the sweep reaches vendored files (CR-1065's new finding at `:200`; its alias is spelled in CR-1065, and not here, because it resolves in no register row) | `CR-1065:200`, `:428`, `:471`; PL-1058 `:2073`. **There is no register row and no essay** at `271088b0`: a `git grep` of `docs/findings` for the alias that `CR-1065:200` gives returns nothing | **deferred, lead as owner**. Only `migrate` runs the sweep, and C4 is the only remaining run of `migrate`. C4 runs on a throwaway snapshot | **Precondition: the auditor files the register row before Task 1** (`CR-1064` §2b, *"scope derived after the filing"*). Event: the create-read-retire audit's first slice | 1, 10 |
| C10 | 53 files deferred out of the Reference stamp set (F92) | register `:133`; FD-1029; owner of record W37-11 | **synthesis**. The defect is that the deferral's record lives only in a squash body. The closure record becomes that record | The closure record lists the 53 files, with the predicate verbatim | 10 |
| C11 | RL-1046 §B's check-30 class (S-5) | `PL-1073:266`, `:312-339`; LG-1139 `:181-183` | **deferred, lead as owner**. The class spans charter, skill and generated files that other owners hold, and `UNSTAMPABLE_EXEMPTIONS` in code | Reading at `271088b0`: `python3 scripts/audit-docs.py 2>&1 \| grep -c '^  - check 30'` → **70** (it was 77 at `4ed1f88`). Event: the first slice of RFC-937 §8's charter investigation Work | 10 |
| C12 | The residue-ceiling record, and the reference limb | RL-1138 DP-1 amendments 1–2; `PL-1073:76-79`, `:1098-1100` | **named acceptance item**, with its destination at DP-3 | Acceptance item 7 | 3 |
| C13 | The legacy-form residual and the full §7 (i) walk | LG-1139 `:179-180`; `CR-1065:339-341`; `PL-1073:817-820` | **synthesis** | The H-row table (acceptance item 9) and the residual's reading at the merge tree, with the predicate verbatim | 10 |
| C14 | The 57 reserved legacy register rows, FD-1080 … FD-1136 | RL-1078 `:41-43`, `:73-74`, `:276-280` | **deferred, lead as owner** (proposal). RL-1078 `:278-280` makes this *"the lead's … a verdict, not a decision point"* | Reading at `271088b0`: `grep -c 'reserved (not yet materialised)' docs/INDEX.md` → **57**, first `FD-1080`, last `FD-1136`. Event: the create-read-retire audit's first slice. **Alternative for the lead:** a named acceptance item whose exit reading is `0`. That would need changes to `doc-id.py`'s resolver and to the register, which is the auditor's file | 10 |
| C15 | #757's g2 per-file entries, rebuilt at the DP-2 read location | #757's squash body (the lead's decision, confirmed by the deputy: *"the g2 population is rebuilt in W37-11 once F109 decides the read location, with 207 as the baseline"*); RL-1145 DP-4 amendment 2 | **named acceptance item** (adopted 11:28:23) | Acceptance item 15 | 4 |
| C16 | The verify-render defect: `render()` never prints the residue-ceiling block when the verdict set is unchanged, and a residue-only exit `3` says the change *"moved no row"* | RL-1145, "A defect found while verifying"; DP-2 amendment 3 | **named acceptance item** (adopted 11:28:23), under DP-2 obligation 2 (amendment 3) | Acceptance item 16. Its `FD-` row and essay are filed by the auditor as one commit in the activation PR | 2 |

**The deputy's four conditions (11:16:34 BST)**, each a row in the closure record:
1. **A deferred row carries a register row before it is deferred.** C9 has none at
   `271088b0`: its `FD-` row and essay are filed first in the docs PR (Tasks 7–11), before
   the closure record cites it. A deferral of an unfiled finding is a silent verdict.
2. **A deferred row carries its named event verbatim, and its reading at the merge tree with
   the predicate** (C11: the check-30 command and its count; C14: the `grep -c` and 57; C7:
   the shape as printed). The reading is re-taken at the merge tree, never copied from
   `271088b0`.
3. **C14 is the lead's verdict, not a decision point** (RL-1078:278-280). It is recorded as
   "deferred, owner lead, event: the first slice of the create-read-retire audit", and the
   same row states RL-1078's disposition of the 15 ids already minted.
4. **C3's baseline is re-measured, not inherited:** g2 at the merge tree next to 207 at
   `29e7a9c`, both by the row's predicate. The roadmap correction at `:766` (the "first item
   is #757" clause, already merged) lands in Task 11.

### B. The day's faces — inputs to the closure record, named by face

"Record" means a dated governed record at `origin/main` = `271088b0`, found by
`git grep -n` over `docs/`. When no record was found, the row says so, and the closure record
writes the record.

| # | Face | Existing record | Task |
|---|---|---|---|
| F1 | Silent exit 3 (`doc_id_verify`) | [LG-1141](../ledgers/LG-01141-w37-8-charters-agents-and-their-readmes.md) `:155-175` (the re-diagnosed cause, proven by a control pair); [PL-1071](PL-01071-w37-8-charters-agents-and-their-readmes.md) `:230` (S-11, docs run 36281191974) | 10 |
| F2 | The checkout template stamped into a ref snapshot | LG-1141 `:163-172` (`_template_header_lines` reads the checkout's template; 27 × 4 = 108) | 10 |
| F3 | (g) alignment | None found. The record is written in the closure record. The nearest mention is LG-1141 `:172` (*"(g)'s provenance mismatch"*) | 10 |
| F4 | The check-36 pooled disclosed reading | The class is recorded at [LG-1137](../ledgers/LG-01137-w37-7-the-remaining-creating-and-reading-instruments.md) `:183-199`, `:210`. **The instance from this day is not recorded**, so the closure record writes it | 10 |
| F5 | A support agent writing into a foreign tree (×2) | None found. The record is written in the closure record | 10 |
| F6 | No `HEAD.txt` | LG-1141 `:476-480` | 10 |
| F7 | S-10 (×2) | LG-1141 `:354-356` (the ruling). The two breaches are not recorded, so the closure record writes them | 10 |
| F8 | Processes killed by pattern | LG-1141 `:350-353` (S-9, the ruling). The instances are recorded in the closure record | 10 |
| F9 | A test that changed tracked `docs/process/` during the run | None found. The record is written in the closure record | 10 |
| F10 | The ledger alias vocabulary | None found. The record is written in the closure record. The nearest mention is [LG-1143](../ledgers/LG-01143-w37-9-root-governance-claude-md-and-the-public-face.md) `:256-260` (the alias-class disclosed hits) | 10 |
| F11 | A stamp composed before the write: seven slips on 2026-09-27, four by the reporter and three by the lead, recorded as one face. It is a breach of a sufficient rule (`lead.md` item 1 already requires `date`'s pasted output), not a §15 finding against a role file. This is the deputy's ruling, relayed by the lead | No governed record. The lead's three slips are recorded in the lead's correction entry in the to-deputy channel file at 11:03:16 BST (local, not in the repo). The closure record writes the face | 10 |
| F12 | A stale grep baseline | None found. The record is written in the closure record | 10 |
| F13 | The dead example finding id (the Finding prefix with the number ninety-three, used as an illustration) | None found. The live sites are `docs/process/document-ids.md:204`, RFC-937 `:206`, and `PL-1072:703`. No finding with that number exists | 10 |
| F14 | F-a and F-b (LG-1143's findings) | LG-1143 `:198`, `:210-211` | 10 |
| F15 | The stale LG-1137 and LG-1139 ledgers, closed after the fact | The auditor's closing PR, **in flight at drafting and not on `origin/main`**. Both ledgers read `status: active` at `271088b0`. The closure record cites the merge SHA of that PR | 10 |
| F16 | A determinism test whose child aborts at interpreter shutdown (the deputy's wording, 2026-09-27 11:21:57 BST). In #819's python run 36311605268, job 108598494214, at `0cbdbf4e`, one test failed: `packages/pricing-core/tests/test_rating_score.py::test_scoring_is_deterministic_across_a_subprocess`. Its child `python -c` returned −6 (SIGABRT) with `Fatal Python error: PyGILState_Release: …` at teardown. The result was `1 failed, 3457 passed, 3 skipped, 1 xfailed`, and `pytest` was the only one of 8 stages that failed. #819 is docs-only, so its code tree equals `271088b0`, where the test passed (run 36310860551). The job was re-run at the same head | No governed record; the deputy's ruling is in the lead's local channel file. The closure record writes the face. **An `FD-` register row, deferred with the lead as owner, lands FIRST in the docs PR (as condition 1 requires for C9).** Event: the first slice of the create-read-retire audit, or a named item if the failure recurs on 2026-09-27. No executor works on it (S-8), and the fix is outside this plan's scope | 10, 11 |
| F17 | A state file re-derived from itself (the deputy's wording, 2026-09-27 11:27:20 BST). The watcher read `position` (phase, work, slice) from the handover's `runtime-state.json` and wrote it back through `write_runtime_state.py cycle`, with source strings naming the roadmap and PL-1072. So `position` stayed at W37-9 from 08:19:33 to 11:25:03 BST, across two slice closes, although W37-9 closed at 10:54:40. RL-907 (d)'s rule not to rewrite a byte-identical file froze the mtime. The lead's two corrections are carried: the roadmap does not record W37-9 as closed, and cycle 35 (10:54:03) came before the merge. **The interim derivation in force:** slice = the W37 leaf `PL-` rows in `origin/main:docs/INDEX.md` whose last column is not `executed`, else "none active on main"; phase and work come from the roadmap. The predicate is cited in every cycle's source string, and the file is rewritten only when the derived value changes | No governed record. The records are the lead's to-deputy entry of 11:26:13 BST and the deputy's ruling of 11:27:20 BST, both in local channel files. The closure record writes the face | 10 |
| F18 | **A `CLAUDE.md` §15 finding against `.claude/roles/watcher.md:64-67`.** The clause says the file "re-derives, does not compare" but names no source for `position`, so the file proved insufficient. The fix is one clause naming the derivation's inputs: `INDEX.md` and the roadmap at `origin/main`, never the state file | The deputy's ruling of 11:27:20 BST. **Deferred, owner lead.** Event: the first slice of the charter investigation (RFC-937 §8), beside the reporter-cycle finding of 09:06. No charter edit in this Work, because charters were W37-8's. As condition 1 requires, its register row lands first in the docs PR. If the watcher drifts again today, the interim predicate in its cycle brief is the record, and it is not re-briefed | 10, 11 |
| F19 | `next` cannot see an unmerged draft. OQ-1146 was derived as the next free value plus two: `doc-id.py next` printed 1144 while unmerged drafts held 1144 (PL-1144) and 1145 (RL-1145), and 1146 is the next free value by the collision rule, with `doc-id.py check` rc 0 on the tree. The deputy ruled (11:28:23 BST) that this meets the (j) event for Open question in substance | The deputy's ruling, in a local channel file. The closure record writes the face beside the 15 id collisions, and states the derivation in the (j) row for Open question | 9, 10 |

### C. The Work close

| # | Row | Task |
|---|---|---|
| W1 | **D7 by delegation.** The deputy decides line 5 once the closure record exists. D7 is not quoted in any governed record at `271088b0`, so the closure record quotes it | 13 |
| W2 | **The maintainer's cleanup order of 2026-09-26 21:16:14 BST, verbatim:** *"after WK-697 landed, ask the lead to cleanup worktrees and branches pushed to remote; then plz turnoff the VM"*. The lead does this after W1, and it is not an executor task | 14 |

**Out of scope, so that no executor widens it:** any `.claude/roles/` or `CLAUDE.md` edit
(W37-8 and W37-9, both closed); `docs/findings/register.md` (the auditor's file; register
changes named here are the auditor's writes); and any capability of a later phase
(`CLAUDE.md` §0). If a task needs one of these, raise a finding to the lead. Do not absorb the
work.

## Roles

| Role | Charter | What they do here |
|---|---|---|
| Executor | [`../../.claude/roles/executor.md`](../../.claude/roles/executor.md); principal is the lead | Tasks 1–12, one worktree, one branch per PR |
| Executor skill | `close-workstream` (`PL-939:383`) | Read before Task 1. Its checklist is the spine of Task 10 |
| Auditor | [`../../.claude/roles/auditor.md`](../../.claude/roles/auditor.md) | Files the register row for C9's vendored-sweep finding before Task 1. Makes the register writes in Task 11. Proposes the §13 verdicts in the closure record and audits each PR |
| Decision-maker | `delivery-process.md` §3 | Rules DP-2 to DP-5 in one `RL-` |
| Deputy | the maintainer's delegate, under the instruction of 2026-09-26 17:02:52 BST | Rules DP-1 by delegation. Gives the merge ACK on each PR. Decides D7's line 5 |
| Lead | `CLAUDE.md` §12 | Gives the §13 verdicts and the carried-item verdicts. Merges. Does the cleanup order (W2) |

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | **(j) — which families are discharged now, and which are owed against a named downstream event?** The map plan's DP-4 (`PL-939:305`) recommended (a) and left the resolver as *"maintainer, at W37-11"*. Measured at `271088b0`: since the migration merge `71f5a22`, **five document families have a real item**, each allocated by `doc-id.py next`. They are Closure (CR-1063, first), Finding (F107's essay, filed at `d63f7650`), Plan (PL-1070), Ruling (RL-1075) and Ledger (LG-1137). The predicate was `git log --diff-filter=A --name-only 71f5a22..origin/main -- docs .claude`, grouped by prefix. **Eight families have no item.** Workflow, Decision, Proposal and Research have none. Requirement, Open question, Work and Slice have no new id: `docs/INDEX.md` lists the same 697 row ids at `71f5a22` and at `271088b0`, and Slice has no members at all ([the no-slice-row finding](../findings/FD-01074-no-sl-row-exists-for-any-slice-and-no-plan-carries-slice.md)) | (a) DP-4 (a) as written: all thirteen families are owed as a standing condition on the first slices of the two downstream Works (§8's charter investigation and create-read-retire audit). (b) A hybrid: the five evidenced families are **discharged now**, and each is verified in the closure record (id, commit, creating skill, `doc-id.py check` rc). The eight others are **owed**, each against its own named event: Work, at the minting of the charter investigation's `WK-` row; Slice, at the first `SL-` row cut in that Work's map plan; Open question, at the `OQ-` row that DP-2 requires, if it is raised through `spec-change` with a number from `next` before the close (otherwise at the audit's first slice); Requirement, Workflow, Decision, Proposal and Research, at the first slice of the create-read-retire audit. (c) One specimen for each family now | **(b).** It is DP-4 (a) applied to the families that still need it. It does not throw away real evidence that already exists. (a) would record five families as owed that have already been proven on real work. (c) is refused for the reason DP-4 gave: *"files thirteen artifacts nobody needed"*. Every owed row names an event, so `PL-939:850-851` is met | scope | **yes** — Task 9 | **maintainer by delegation (deputy, 2026-09-27 11:16:34 BST)**, on the maintainer's instruction of 2026-09-26 17:02:52 BST; quoted verbatim in RL-1145. **(b) adopted.** Each owed row's verdict at the Work close is "deferred with an owner", the owner being the downstream Work's lead, accepted explicitly in the D7 line |
| DP-2 | **F109 — where does the standing CI verify read the residue-ceiling record from?** `.github/workflows/docs.yml:115-123` pins `--ref` to `core.json`'s `meta.verified_against_tree`. `scripts/_docverify.py:4366-4375` loads the record from `snap.control`, which is the pinned base. So an edit to the record on `main` is invisible to CI forever (F109). The F102 fix (`_docverify.py:4204-4223`) moved the read off the live checkout because that read was not hermetic. **Precondition (`CR-1064:545`):** the question is raised in `docs/open-questions.md` with these options and this recommendation before this plan goes active | (a) Keep the pinned read. Record edits are seen only by a local `--ref HEAD` run. C5 and C12 become invisible to CI, and this is recorded. (b) Read from the live checkout. **Refused**: it undoes F102. (c) Add a second archived ref for the record only: a `--record-ref`, archived through `git archive` in the same way as `--ref`, which defaults to `--ref`. CI passes the commit under test. The corpus stays at the pinned base. (d) Retire the standing verify at the Work close and let check 36, which already reads the record at the audited tree, be the standing check | **(c).** Each run stays hermetic, because both inputs are commit-keyed archives, and later edits become visible. It is the smallest change that makes C5 and C12 observable. (d) removes a gate, so it is a scope change and would go to the maintainer | mechanism — **a decision-maker point, not a maintainer one**. It changes how an instrument reads, not what is accepted. If (d) is chosen, it becomes a maintainer point | **yes** — Tasks 2–4 | **RL-1145 — (c) adopted**, with four amendments: (1) a record missing at `--record-ref` exits `2` and never degrades to `()`; (2) the provenance table gains a HERMETIC `--record-ref` row; (3) the residue block renders whenever there are residue changes, even on an unchanged verdict set (C16); (4) the census rows are measured before they are shrunk, with a stop. (a) and (b) refused; (d) not ruled (the maintainer's). OQ-1146 decided |
| DP-3 | **Where does the residue-ceiling record go, and what happens to the references that remain?** RL-1138 makes W37-11 the carrier of the file and of the reference limb (amendments 1–2). It did not adopt the plan's "220 / 74" figure, because that figure did not reproduce | (a) Move the record to `docs/process/` as a living Reference document (RFC-937 §1.4 names `process/` as one of the places the audit directory dissolves into). Update the constant. Add a `docs/REDIRECTS.csv` row with the shape of the findings-README row. References in frozen records are resolved by that row, and are disclosed and not edited. (b) Move it out of `docs/` into instrument data under `scripts/`. (c) Leave it in place and record the directory as accepted residue | **(a).** The record is a living table that people edit, so a frozen family (RS, CR) would contradict it. `process/` is where §1.4 sends it. (b) hides a governed table from `doc-index`. (c) leaves §7.1's clause unmet with no event | mechanism | **yes** — Task 3 | **RL-1145 — (a) adopted**, with amendments: (1) the constant is the only place in code that spells the path; (2) the writer is stated; (3) frozen records are resolved by the redirect row and never edited; (4) the five-class reference table, 183 = 150 + 9 + 22 + 1 + 1 at `271088b0`; (5) the writer of the record's rows (the deputy by delegation, 11:28:23 BST): the lead of the discharging slice, with the frame staying the maintainer's |
| DP-4 | **What does the Work close require of row (g)?** g2 = 207 at `29e7a9c`, and the row is a standing FAIL | (a) g2 must reach `0` at the merge tree. (b) The exit measurement is the g2 figure at the merge tree, with every remaining file assigned to a cause and the parts summing to the total. (g) is recorded with the §13 verdict *"deferred with an owner"* and a named event, and the Work close accepts it explicitly. (c) Narrow (g) — **refused** by G3 | **(b).** It measures without lowering the bar. Whether a Work may close over an item that is still FAIL remains the delegate's, in the dated acceptance line. (a) has no bounded plan: the 207 are cause-attributed, but #757 showed that each cause needs its own classifier change | scope of an acceptance reading | **yes** — Task 7 | **RL-1145 — (b) adopted**, with amendments: (1) the closure record attributes any move from 207 to named classifier commits in `29e7a9ce..<merge tree>`; (2) #757's rebuild is typed (now C15). The §13 verdict is the lead's |
| DP-5 | **(k) — what counts as "containing" an element that reads zero or `—`?** At `271088b0` the report prints all seven elements. Six of them read zero or `—` (element 2: *"0 planned, 0 delivered"*, because Slice has no members; element 6: *"—"*) | (a) Presence of the seven elements is enough (the literal words of item 10). (b) Presence, plus a second count built a different way for each zero or `—` reading, or a statement that it is zero by construction with the reason. (c) Also run with `--phase P2` | **(b).** When an instrument reports a confident absence, a second instrument must check it. Element 2's zero comes from an empty family, and saying so is the evidence. (c) is useful but is outside (k)'s words | mechanism | no — Task 8 | **RL-1145 — (b) adopted, amended**: where a second count disagrees, the closure record reports both counts, with each predicate and population |

## Tasks

Conventional Commits. Branches come from `main` (`CLAUDE.md` §10). The instrument tasks
(2–6) are one PR, **the code PR**. The synthesis tasks (7–11) are a second PR, **the docs
PR**, cut from `main` after the code PR's squash, because the closure record must quote the
code PR's merge tree. Both PRs regenerate INDEX, so they are never in flight together.

**The code PR (the deputy, 11:16:34 BST):** the full two-half gate (`CLAUDE.md` §11), because
the reduced gate expired with W37-8; executor rules S-8 to S-10 as in `executor.md`; an
evidence directory with `HEAD.txt`; and broken-input proofs for `--record-ref` (acceptance
items 5 and 16). The band is re-derived at the activation merge, and the code PR is stated as
its own band. **Before Task 1,
read `.claude/skills/close-workstream/SKILL.md` in full, then this plan's Decision points.
If DP-1 to DP-4 do not carry a resolver id, stop and ask the lead.**

### Task 1: Baseline and preconditions

**Files:** none (the ledger entry only).

- [ ] **Step 1:** Print `readlink /proc/$$/cwd`, then `git rev-parse HEAD origin/main`. Record
  both.
- [ ] **Step 2:** Confirm that the preconditions hold, and quote each one:
  the register has C16's `FD-` row (filed in the activation PR);
  `grep -n 'OQ-1146' docs/open-questions.md` returns the decided row; RL-1145 is on `main`.
  If one fails, stop. (C9's register row is **not** a precondition of the code PR. It lands
  first in the docs PR, under condition 1.)
- [ ] **Step 3:** Record the baseline readings, each with its command verbatim:
  `python3 scripts/audit-docs.py` (rc, and the `All checks passed.`/`FAILED` and `DISCLOSED`
  lines); `python3 scripts/doc-id.py check`; the check-30 count (C11); the reserved count
  (C14); the reference limb (acceptance item 7); and the standing verify, run exactly as
  `docs.yml:115-123` runs it, with its g2 line. At `271088b0` the planner read
  `audit-docs.py` rc 0, `All checks passed.`, `DISCLOSED (865, …)`, check-30 = 70 and
  reserved = 57.
- [ ] **Step 4:** Commit the ledger entry. End the turn (S-10).

### Task 2: F109 — the record read, as DP-2 rules

**Files (under the recommended (c)):** `scripts/_docverify.py` (the `load_w37_11_record`
call at `:4366-4375` and `build_snapshot`/`_materialise` at `:313-360`), `scripts/doc-id.py`
(the `migrate --verify` argument parser), `.github/workflows/docs.yml:115-123`, and
`tests/test_doc_id_verify.py`.

- [ ] **Step 1: Write the failing test.** Model it on
  `test_verify_reads_the_w37_11_record_from_the_ref_never_the_live_checkout`
  (`tests/test_doc_id_verify.py:3663`). Build a fixture repository with two commits. Commit B
  changes one ceiling in the record. Run verify with `--ref A --record-ref B`, and assert that
  the loaded record carries B's ceiling. Run a second case with the live checkout dirtied to a
  third value, and assert that the value is neither A's nor the dirty one. That second case is
  F102's property, kept.
- [ ] **Step 2:** Run it and see it fail (the unknown argument).
- [ ] **Step 3:** Implement `--record-ref`, which defaults to `--ref`. It archives the record's
  path at that ref, in the same way `_materialise` does. In CI, pass
  `--record-ref "$GITHUB_SHA"`.
- [ ] **Step 4:** Run the test and see it pass. **Broken-input proof:** revert Step 3's
  argument wiring only, and see the test fail with its message. Record the message.
- [ ] **Step 5 (DP-2 amendment 1):** Write a test that runs the verify with a
  `--record-ref` whose archive lacks the record. Assert exit `2` and a message that names the
  path it looked for. See it fail first (today the reader returns `()`), then make the verify
  path refuse. `audit-docs.py`'s own reader keeps its degrade-to-empty behaviour.
- [ ] **Step 6 (DP-2 amendment 2):** Add the HERMETIC `--record-ref` row to the
  input-provenance comment, and state why the record's control-path keys still match a corpus
  read at `--ref`.
- [ ] **Step 7 (C16, DP-2 amendment 3):** Write the two render tests on the suite's own
  `_result` pattern (`tests/test_doc_id_verify.py:3224`). First, an unchanged verdict set with
  one `PROGRESSED` change asserts that `RESIDUE CEILING` is printed. Second, the same with one
  fatal change asserts `RESIDUE CEILING`, exit `3`, and no *"moved no row"* text. Run both at
  `271088b0` and record the failures. Make `render()` print the residue block whenever
  `residue_changes` is non-empty. Run both again and record the passes.
- [ ] **Step 8:** Commit. End the turn.

### Task 3: The record move and the reference limb, as DP-3 rules

**Files (under the recommended (a)):** `git mv` of the record into `docs/process/`;
`scripts/_docid.py` (`W37_11_RECORD_PATH`); `docs/REDIRECTS.csv` (one row);
`docs/INDEX.md` (regenerated, never edited by hand).

- [ ] **Step 1:** Run acceptance item 7's two commands, and record both readings.
- [ ] **Step 2:** Move the file, update the constant, and add the redirect row. Choose a
  basename that says what the file is. Every reader (`_docid.py`, `_docverify.py`,
  `audit-docs.py`, `doc-id.py:665`, and the four test modules that RL-1138 §1 lists) reaches
  the path by symbol (DP-3 amendment 1).
- [ ] **Step 3:** Run `python3 scripts/audit-docs.py`, `python3 scripts/doc-id.py check`,
  `python3 scripts/doc-index.py && python3 scripts/doc-index.py --check`, and
  `uv run pytest -q tests/test_doc_id_verify.py tests/test_doc_id_migrate.py`. The first
  reading of acceptance item 7 is `0`. Place every file in the second reading in one of DP-3
  amendment 4's five classes, and show that the parts sum to the total. Edit only the
  instrument class's *paths to the record*. Living documents in `.claude/skills` and
  `docs/roadmap.md` are their owners' to edit, and frozen records are never edited. The table
  goes to the closure record.
- [ ] **Step 4:** Commit. End the turn.

### Task 4: The census-row shrink

**Files:** the residue-ceiling record (by symbol), the three per-file rows named at
`CR-1063:236-238`.

- [ ] **Step 1 (DP-2 amendment 4):** With this PR's tool, read
  `VerifyResult.measured_residue` for the three census keys directly at the pinned base, and
  quote the three numbers. **Stop and report to the lead unless all three read `0`.**
- [ ] **Step 2:** Set the three ceilings to `0`.
- [ ] **Step 3:** Run the verify with `--record-ref` at this branch's commit. Confirm from
  `measured_residue`, and from the render now that C16 is fixed, that there is no
  `PROGRESSED` line for the three rows and no `REGRESSION`.
- [ ] **Step 4 (C15):** Rebuild #757's g2 per-file entries at the DP-2 read location, with
  207 as the baseline. Quote the reading and its predicate.
- [ ] **Step 5:** Commit. End the turn.

### Task 5: Idempotence (F107)

**Files:** none in the tree. The evidence goes to the ledger. Follow
`.claude/skills/doc-id-migration-run` for the throwaway-snapshot procedure.

- [ ] **Step 1:** Archive the current `HEAD` into a throwaway directory outside every worktree:
  `git archive HEAD | tar -x -C <dir>`, then `git init`, add and commit inside it.
- [ ] **Step 2:** Run `python3 scripts/doc-id.py migrate` against it, in the form the skill
  gives.
- [ ] **Step 3:** Run `git -C <dir> status --porcelain | wc -l`. Expected: `0`. If the reading
  is not zero, record the diff's `--stat` and stop. That is a finding, not a fix.
- [ ] **Step 4:** Record that the property proved is **idempotence**, with the starting figure
  from `CR-1064:414`. End the turn.

### Task 6: F110 — one population, one docstring

**Files:** `scripts/_docverify.py:428-436` and `:3090-3100`; `tests/test_doc_id_verify.py`.

- [ ] **Step 1:** Write a test that builds a corpus with one sweep-excluded file (a lockfile).
  Assert whether `_h1_residue_by_file` attributes a failure line naming that file. Run it, so
  that the behaviour itself, not a docstring, says which population applies.
- [ ] **Step 2:** Correct the docstring that disagrees with that behaviour. The code does not
  change.
- [ ] **Step 3:** Run the test and see it pass. Commit. End the turn.

### Task 7: Row (g) — the re-measure (C3)

- [ ] **Step 1:** At the merge tree of the instrument PR, run the standing verify, and quote
  the `g2` line and each cause count.
- [ ] **Step 2:** Show that the parts sum to the whole, and compare with 207 at `29e7a9c`.
  List the classifier commits in `29e7a9ce..<merge tree>` (DP-4 amendment 1). A move with no
  such commit is an instrument defect, and it is reported.
- [ ] **Step 3:** Discharge the condition from the lead's decision of 2026-09-18 00:42 BST.
  State whether any cause is a defect in corpus correctness. If one is, stop and report to
  the lead.
- [ ] **Step 4:** Apply DP-4's ruling, and draft the §13 verdict for the lead.

### Task 8: (k), element by element (C1)

- [ ] **Step 1:** Run `python3 scripts/doc-index.py --phase P1b; echo EXIT=$?`.
- [ ] **Step 2:** Build acceptance item 1's seven-row table.
- [ ] **Step 3:** For each zero, `—` or `(none)`, apply DP-5 as amended. Where the two
  counts disagree, report both with their predicates, as for element 4. Otherwise give a
  second count built another way, or the
  reason it is zero by construction.

### Task 9: (j), family by family (C2)

- [ ] **Step 1:** Build the thirteen-row table under DP-1's ruling. For each discharged row,
  run `git log --diff-filter=A --format='%h %aI' -- <path>` and `python3 scripts/doc-id.py
  check` at that commit. Name the creating skill from the commit or its ledger.
- [ ] **Step 2:** For each owed row, give the named event verbatim from the deputy's DP-1
  line (quoted in RL-1145). For Open question, state F19's derivation of OQ-1146, if OQ-1146 is
  the item that discharges it.

### Task 10: The closure record

**Files:** create `docs/closures/CR-<n>-<slug>.md`, where `<n>` comes from
`python3 scripts/doc-id.py next`. Use `kind: work`, `work: WK-697` and `phase: P2`.

- [ ] **Step 1:** Allocate the id, and reconcile it with the lead before you push (the trap
  about the allocator reading `origin/main`, in `dev-commands`).
- [ ] **Step 2:** Write, in order: the H-row table; the ten broken-input proofs (fixture path
  and failure message for each of checks 30–39); the §7 (a)–(h) evidence; Tasks 7–9's tables;
  the carried-items table (Scope A) with the lead's verdict on each, and the four conditions,
  each as a row, with C16 typed "fixed in W37-11 by <squash>"; the day's faces (Scope B),
  each citing its record or writing it; C10's list of 53 files with its predicate; C13's
  residual; and a §13 verdict for every item without evidence.
- [ ] **Step 3:** Spell no legacy path. Run `python3 scripts/audit-docs.py`, and confirm that
  the `DISCLOSED` delta is caused only by alias-class tokens.

### Task 11: Roadmap and register

- [ ] **Step 0 (condition 1, first commit of the docs PR, the auditor):** File the `FD-`
  register row and essay for C9, F16 and F18, before any commit that cites them as deferred.
- [ ] **Step 0b (the lead, by the deputy's delegation of 11:28:23 BST):** Add a one-line
  pointer at `docs/process/document-ids.md:161`, "rows of the residue record: RL-1145 DP-3
  am. 5". This is not a new family and not a renumbering.
- [ ] **Step 1:** Rewrite the WK-697 row in `docs/roadmap.md` to record the close. Correct the
  "#757 … rebase" clause, citing `29e7a9c`, and cite the closure record.
- [ ] **Step 2 (the auditor):** Update the register rows for F92, F107, F108, F109, F110,
  C9's vendored-sweep finding, C16, F16 and F18 with the dispositions in the closure record.
- [ ] **Step 3:** Regenerate `docs/INDEX.md`.

### Task 12: Gate, PR, audit

- [ ] **Step 1:** Run both halves of the gate (`CLAUDE.md` §11) at the head. Record the rc for
  each command.
- [ ] **Step 2:** Open the PR, get the auditor's clean audit and the deputy's merge ACK, and
  have the lead merge it. End the turn.

### Task 13: The Work close (W1)

- [ ] **Step 1:** Once the closure record is on `main`, the lead asks the deputy for D7's
  line 5.
- [ ] **Step 2:** The dated acceptance line is added to the closure record in a follow-up
  commit, which is the only post-filing edit that record takes.

### Task 14: Cleanup (W2) — the lead's

- [ ] **Step 1:** After WK-697 has landed, the lead acts on the maintainer's order verbatim:
  *"after WK-697 landed, ask the lead to cleanup worktrees and branches pushed to remote; then
  plz turnoff the VM"*. Before each removal, check that nothing unmerged is lost:
  `git worktree list`, and `git merge-base --is-ancestor` for every branch. Remove by path,
  never by pattern.

## Gates

| # | Gate | Command / artifact | Pass |
|---|---|---|---|
| 1 | Docs audit | `python3 scripts/audit-docs.py; echo EXIT=$?` | `EXIT=0`, `All checks passed.` |
| 2 | Id lint | `python3 scripts/doc-id.py check; echo EXIT=$?` | `EXIT=0` |
| 3 | Index | `python3 scripts/doc-index.py --check; echo EXIT=$?` | `EXIT=0` |
| 4 | Gate, both halves | `CLAUDE.md` §11 | every command `EXIT=0` |
| 5 | CI, by head SHA | `gh run list --branch <branch>` | `completed/success` at that SHA |
| 6 | The deputy's merge ACK and the clean audit | dated, and quoted in the ledger | present |
| 7 | The Work-close acceptance line | Task 13 | present and dated |

## Self-review

- **Spec coverage.** Each of map items 8–12 (`PL-939:84-99`) maps to acceptance items 9, 2, 1,
  9 and 10 respectively. (j) and (k) each have a task. Each of the four items that `CR-1064`
  requires of W37-11 (`:545-548`) is present: DP-2 and its precondition; acceptance item 4;
  acceptance item 3; and the successor rule.
- **Placeholders.** `<n>`, `<dir>` and `<branch>` are values found at run time, and each
  comes with the command that finds it. The instrument tasks depend on DP-2 and DP-3. Their
  file lists and tests are written for the recommended options, and they are rewritten if
  the ruling differs.
- **Every legacy path is described, not spelled.** The residue-ceiling record is cited by
  symbol.
