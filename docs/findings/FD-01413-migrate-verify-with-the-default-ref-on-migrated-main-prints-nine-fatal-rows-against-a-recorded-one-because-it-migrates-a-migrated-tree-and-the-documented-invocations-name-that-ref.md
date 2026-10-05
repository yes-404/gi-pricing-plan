---
id: FD-1413
family: finding
title: migrate --verify with the default ref on migrated main prints nine fatal rows against a recorded one, because it migrates a migrated tree, and the documented invocations name that ref
status: active
created: 2026-10-05            # the mint date (check 31); filed 2026-10-01
owner: auditor
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
corrected_by: []
relates: [WK-1178, RL-1043, RL-1045, RL-1046, CR-1063, FD-1154]
---

# FD-1413 — `migrate --verify --ref HEAD` on migrated main is a false nine-row red

**Filed** by auditor-mv at the maintainer's request of 2026-10-01 (received 10:24 BST). `tree:` is
`origin/main` = `1dd5e264195677b4a13268b80ac8673c2c027135`, the tree every figure below was
measured on unless a row says otherwise. The id is a working id until the lead mints it.

## Finding

> "on main itself the instrument prints '9 fatal row(s) against a recorded 1. This change MOVED A
> ROW', with REGRESSION (a), (d1), (d5), (f) plus 4 DISCLOSE→FAIL … Is that tracked …? If not,
> it's a standing-FAIL hiding the next regression."

**Reproduced exactly, and it is not a regression on main.** Nothing in main's history turned a row. The
default invocation migrates a tree the migration has already migrated, so the instrument's control tree
equals its migrated tree and every row that reads "unchanged" reads as a regression. The same tool, on the
same main, with the ref the CI step uses, prints `UNCHANGED: 1 fatal row(s)` and exits 1 — the recorded standing red.
**The defect that remains is that the invocations the repository documents name the wrong ref on a migrated
checkout**, and the instrument gives no warning.

**Was it already tracked?** The mechanism is recorded; the documented-invocation defect is not.
`grep -rn -E "MOVED A ROW|SET CHANGE \(9\)" docs/findings docs/rulings docs/closures` finds the nine-row output only
in `CR-1063` §2 (CI run `35261236904`, head `323b523`) and `CR-1064` (the table row at line 412). The fix landed in
`.github/workflows/docs.yml` (the `doc-id migrate --verify` step: on a migrated checkout, `--ref` is
`delivery-process.core.json` `meta.verified_against_tree`, `--record-ref HEAD`). No `FD-` or `RL-` covers the
local and documented forms. `grep -n -E "migrate --verify" .claude/skills/dev-commands/SKILL.md
docs/process/delivery-process.md docs/process/delivery-process.core.json` shows all three give `--ref` as
omitted (`<root>`) or `--ref HEAD`.

## Evidence

### What the instrument is

`python3 scripts/doc-id.py migrate --verify [SNAPSHOT] [--ref REF] [--record-ref REF]` (RL-1043 §1). It
`git archive`s `--ref` into a control tree, runs `migrate()` on a copy, and computes RFC-937 §7 rows (a)–(i) with
a predicate each, plus the §7(f) baseline tree at `8f5d57d`. It compares the verdict set against
`_docverify.EXPECTED_VERDICTS` (exit 0 green, 1 the recorded standing red unchanged, 3 a moved set, 2 a refusal).
Rows that fail here: **(a)** zero `none` family over `docs/`; **(d1)** no `NT-nnnn`; **(d5)** no `Ruling n`;
**(f)** `VR-DST-1` count unchanged across the migration; **(d4/d8/d9/d10)** disclosed legacy-id classes.
All of them assert that the migration *removed* legacy forms, which is only measurable if `--ref` is a
tree that still has them.

### Rows at main (maintainer's invocation)

Command: `python3 scripts/doc-id.py migrate --verify <empty dir> --ref HEAD` (record ref defaults to `--ref`,
so also HEAD), on `1dd5e264`, `nice -n 10`, `POLARS_MAX_THREADS=4`; **exit 3**, 2m12s.

| Row | Recorded | At main, `--ref HEAD` | Why |
|---|---|---|---|
| (a) | PASS | FAIL | control `none=0 of 694`; "the classifier cannot be shown to produce a `none`" |
| (d1) | PASS | FAIL | `NT-\d{4}`: migrated 6 lines / 5 files, control 6 / 5 — INERT, control equals migrated |
| (d5) | PASS | FAIL | `Ruling \d+`: migrated 9 / 6, control 9 / 6 — INERT |
| (f) | PASS | FAIL | `VR-DST-1`: control 156 / 42 files, migrated 152 / 41, residual −4 (4 hits are `docs/INDEX.md`, generated, excluded) |
| (d4), (d8), (d9), (d10) | DISCLOSE | FAIL | legacy-form hits in files the W37-11 record does not name (RESIDUE CEILING block of the run) |
| (h1) | DISCLOSE | PASS | the one PROGRESS |
| (g) | FAIL | FAIL | the recorded standing red, unchanged |

Plus a `W37-11 RESIDUE CEILING (97)` block with 50 `REGRESSION (residue exceeds W37-11 ceiling)` lines
(e.g. `scripts/doc-id.py` (d10) 44 against a ceiling of 15) and many `PROGRESSED` lines.

### Where each row turned — bisect

The variable is the corpus ref, not the tool: every run below uses main's `scripts/doc-id.py` at
`1dd5e264` and `--record-ref HEAD`. The first-parent range `8f5d57d..origin/main` is 421 commits; the
migration is atomic, so the bisect needed only the commit that introduced `docs/INDEX.md` and
`docs/REDIRECTS.csv` (the sentinel `audit-docs.py` `migrated_tree()` and `docs.yml` use):
`git log --first-parent --diff-filter=A -- docs/REDIRECTS.csv` returns one commit.

| `--ref` | Result |
|---|---|
| `0651c1e2` (parent, un-migrated) | exit 1; `UNCHANGED: 1 fatal row(s)`; only (g) fails |
| `71f5a220` (the migration) | exit 3; `SET CHANGE (9)`: **(a), (d1), (d5), (f) PASS→FAIL; (d4), (d8), (d9), (d10) DISCLOSE→FAIL** |
| `0651c1e265648cbd3918adfc729ad965b83b1e0b` = `meta.verified_against_tree`, as `docs.yml` passes it, run from main | exit 1; `UNCHANGED: 1 fatal row(s)`; (g) only; no residue block |

**First bad commit for every one of the eight rows, (a) and (f) included: `71f5a220`**,
the W37-6 run 2 migration commit (2026-09-17 21:03:42 BST; title quote removed 2026-10-01 11:18 BST: it carried a legacy id that check 36 flags; the record is unminted, so this is authoring),
the commit that landed the migrated corpus. Parent `0651c1e2` is clean. They are adjacent in the first-parent
chain, so no further bisection exists. The rows "turned" because the corpus became migrated, which is the
instrument's input, not a regression in main.

## Why this matters

1. **The documented forms are wrong on every migrated checkout.** `dev-commands` (`migrate --verify <root>`, lines
   273 and 788–791) gives no `--ref`; `delivery-process.md` §11a ("`--verify <tmpdir> --ref HEAD` before its PR
   is opened, read row (a)") and `delivery-process.core.json` (the `"command": "python3 scripts/doc-id.py migrate --verify <tmpdir> --ref HEAD"` row, `:481` at `origin/main` `36a9f48325af47b482bd1f3211b01e90d2b4b149`; `:477` at the filing tree) give `--ref HEAD`. §11a was written 2026-09-03 for
   an un-migrated tree. After `71f5a220` an author who follows it reads row (a) as FAIL — the row §11a tells them to read.
2. **A standing nine-row red hides a real one.** Once an author learns that "main prints nine rows", a genuine
   (a) or (f) regression prints the same lines among those nine; exit 3 carries no information. The
   recorded standing red (one row, (g)) is only visible in the pinned-ref form.
3. **The pinned form cannot see a regression in the migrated tree.** `docs.yml`'s form verifies this checkout's
   *tool* against the pre-migration base. It proves the tool, not today's corpus; (a) and (f) on today's corpus
   are `doc-id.py check` and the tool's own checks. Whether row (f) should have a live-tree counterpart is for the
   decision-maker.
4. **The instrument does not detect the case.** On a migrated checkout (`docs/INDEX.md` + `docs/REDIRECTS.csv`) it
   runs the full migration over a migrated archive and prints no migrated-checkout notice in the runs above; its own output says "control has zero
   `none` too" and "INERT: control equals migrated", per row, and only the reader joins those. `FD-1154`
   records the same key's two meanings.

## Severity (proposed; the maintainer's)

**MEDIUM.** Nothing is mispriced and CI is correct. It is not LOW because the only documented local procedure
produces a false fatal result on every migrated checkout, and the maintainer reached it unprompted on main. It
is not HIGH because the gate (`docs.yml`) uses the right ref, so no regression passes unseen today.

## Disposition

Options, for the decision-maker, not a pick: (i) make `--verify` on a migrated checkout default `--ref` to
`meta.verified_against_tree` (as `docs.yml` does) or refuse with exit 2 naming it; (ii) amend the three
documented forms to the CI form; (iii) re-record `EXPECTED_VERDICTS` — **not** advised, since the nine-row set is
produced by migrating a migrated tree and would record the artefact; (iv) retire rows (a), (d1), (d5), (f) for
migrated trees and keep them against the pinned base. Re-record versus retire is the decision-maker's.

**Owner: WK-1178.**

## WK-1178 backlog (separate, one line)

`dev-commands`' `migrate --verify <root>` reads as a repo root; `<root>` must be a new or empty snapshot dir
outside any work tree, or omitted (a real checkout is refused, exit 2, as the maintainer found).

## Decision — the maintainer, 2026-10-01 11:15:54 BST (appended 2026-10-01 11:20 BST; nothing above is edited)

Cited verbatim from the maintainer's entry headed *"FD 9755 (#1073): MEDIUM, owner WK-1178, NO DM needed; MY
"main reports 9 fatal rows" WITHDRAWN (my invocation); CI's form at every ACK from now on"*
(`gi-pricing-plan.local/channel/to-lead.md`, `## 2026-10-01 11:15:54 BST`):

> **Withdrawn:** … **It was my invocation:** `--ref HEAD` re-migrates an already-migrated tree. … In CI's form, main exits 1 with UNCHANGED: 1 ((g) only) = the record. **The bisect … proves it.** … **#1056 and #1058:** the main-vs-head comparison was measured the same way on both sides, so it stands as a no-change check, but the absolute rows I quoted (incl. "h1 PASS") were meaningless and are withdrawn as evidence.
>
> **Severity: MEDIUM** (not LOW): the documented invocation (dev-commands, delivery-process §11a, core.json, the `migrate --verify` command row) is wrong on any migrated checkout, and the instrument is silent. It produced a false alarm here, **and a false PASS (h1 DISCLOSE → PASS)**, so it can hide as well as invent. Owner WK-1178.
>
> **Discharge (no DM):** main matches its record, so there is nothing to re-record or retire. (1) **The three documented invocations corrected** to CI's form (`--ref <meta.verified_against_tree> --record-ref HEAD`), core.json via its digest-bump rule, with the `<root>` → "an empty snapshot dir, or omit" wording; (2) **the instrument refuses (exit 2, a named message) when `--ref`'s tree is already migrated** … the planner picks the predicate and proves it on broken input both ways … A skill update in the same commit (CLAUDE.md §12).

What this changes in the record above:

- **Severity: MEDIUM, ruled** (the "proposed; the maintainer's" in §Severity is now the maintainer's).
- **§Disposition is struck.** The options list, and the auditor's earlier proposal (re-record versus retire, for a decision-maker),
  are superseded: there is **no decision-maker**. Main matches its record, so option (iii) and (iv) are void and nothing is
  re-recorded or retired. Options (i) (refuse, exit 2, naming the pinned ref) and (ii) (amend the three forms) are
  the discharge, below. The §Why-this-matters item 2 "a standing nine-row red" and the title's "nine fatal rows on main"
  describe the maintainer's `--ref HEAD` invocation, not main's state.
- **§Rows at main is withdrawn as evidence of main's state**, as is every absolute row quoted from that invocation, including
  (h1) PASS (which was also a false PASS: DISCLOSE read as PASS). The bisect and the pinned-form row stand. #1056 and #1058's
  main-versus-head comparisons stand as no-change checks only.
- **Why MEDIUM:** the documented form is wrong in three places and silent, so it gives a false alarm and a false PASS; it can hide a
  regression as well as invent one.

### Discharge (owner WK-1178)

> **Amended 2026-10-05 before mint:** the discharge is split in two halves with different owners, so the finding closes only when both land. The `delivery-process.core.json` cite is re-anchored by symbol (the `"command": "python3 scripts/doc-id.py migrate --verify <tmpdir> --ref HEAD"` row, `:481` at `origin/main` `36a9f48325af47b482bd1f3211b01e90d2b4b149`; the filed text said `:477`, and the triage's `:479` was also stale at that tree). The line cites above `delivery-process.md:265` and `dev-commands` `:273`, `:788` re-resolved at the same tree.

1. **Docs half — owner: contributor onboarding item 3** (`handover/contributor-onboarding-2026-10-06.md`, "Item 3 — FD 9755's docs part", accepted 2026-10-05; a local handover file, not in the repository). `dev-commands`, `delivery-process.md` §11a and `delivery-process.core.json` (the `migrate --verify` command row above) corrected to CI's form, `--ref <meta.verified_against_tree> --record-ref HEAD` (core.json by its digest rule), with the `<root>` wording: an empty snapshot dir, or omitted. That item's prerequisite is this finding minted.
2. **Instrument half — owner: WK-1178** (`PL-1371` row 11, "FD 9755 discharge (documented `migrate --verify` form plus the refusal)"; the onboarding item states the refusal "is code and stays with a lane"). The instrument **refuses (exit 2, a named message)** when `--ref`'s tree is already migrated; the planner picks the predicate and proves it on broken input both ways (a migrated ref refused, an un-migrated ref accepted); a skill update lands in the same commit.

The finding is discharged when **both** halves are merged; either alone leaves it open.

**Going forward:** every ACK that runs it quotes CI's form with its rc and row line.
