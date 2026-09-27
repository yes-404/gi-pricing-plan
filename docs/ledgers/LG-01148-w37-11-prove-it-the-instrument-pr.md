---
id: LG-1148
family: ledger
title: W37-11 — prove it, the instrument PR
status: active
created: 2026-09-27
owner: executor
tree: 9fe726b221f01c2055f818ea30ed84324cd84ab4
phase: P2
work: WK-697
plans: [PL-1144]
corrected_by: []
relates: []
---

# LG-1148 — W37-11 — prove it, the instrument PR

Executed task by task from `PL-1144` (`status: active`, frozen 2026-09-27), under
`RL-1145` (DP-2 (c), DP-3 (a), DP-4 (b), DP-5 (b), each with its amendments) and the
deputy's DP-1 line of 2026-09-27 11:16:34 BST. Cut from `origin/main` at
`9fe726b221f01c2055f818ea30ed84324cd84ab4` (#820, W37-11's activation). This ledger covers
**the code PR, Tasks 1–6**, on one branch (`w37-11-code`). Every task commit below is a
pre-squash branch commit of that PR. The PR's squash SHA on `main` is recorded once, in the
PRs table, when it is known. Tasks 7–14 (the docs PR and the close) are appended by whoever
executes them.

The lead's rulings on the executor's first report (2026-09-27, received after 12:05:10 BST)
bind this ledger. Q1: this ledger is created. Q2: the code PR edits the 22 instrument and
test files and the two skills. The six `docs/process/` documents and `docs/roadmap.md` are
left to their owners in the docs PR. Q3: the record's rows are written by the executor as
the W37-11 lead's instrument (`RL-1145` DP-3 amendment 5), in their own commits, and the
lead adopts or amends the row diff at review. Q4 — *Was: "C15 is **held** for the deputy's ruling.
The population may be derived as evidence, and no g2 per-file row is filed."* **Updated
2026-09-27 12:42:49 BST (the executor, on the lead's instruction):** the deputy ruled Q4 at
2026-09-27 12:06:57 BST (the lead's local channel file `to-lead.md`, the entry headed
"Q4 RULED: C15 = option (a) …"), and the lead released the hold. C15 is option (a):
*"'Rebuilt' means **re-derived and quoted** … **No rows are filed in W37-11.**"* This
ledger carries the per-file g2 population at the DP-2 read location, and a throwaway
measurement of whether filing the rows would flip row (g). RL-1145 DP-4 (b) stands, so
(g) stays the standing FAIL. The rows are *"deferred with you as owner, event: the
create-read-retire audit's first slice"* (the owner is the lead). Q5: F19
(`doc-id.py next` defaulting to `origin/main`) stays deferred with the lead.

## Tasks

### Task 1 — baseline and preconditions

**Step 1.** `readlink /proc/$$/cwd` printed `/home/puzhenhao1989/gi-pricing-plan`.
`git rev-parse HEAD origin/main` printed `9fe726b221f01c2055f818ea30ed84324cd84ab4` for
both, in the worktree
`/home/puzhenhao1989/.claude/jobs/66723b39/tmp/exec-w37-11/code` (branch `w37-11-code`)
and in the root checkout (`## main...origin/main`).

**Step 2, the preconditions.** Each one holds at `9fe726b2`:

- C16's register row is present. `grep -n 'FD-1147' docs/findings/register.md` returns
  `:154`, which opens *"The verify render hides the residue-ceiling block on an unchanged
  verdict set, so a residue-only exit 3 says the change "moved no row" (FD-1147; C16)"*.
- `grep -n 'OQ-1146' docs/open-questions.md` returns `:48`. The row reads *"DECIDED
  2026-09-27 — option (c): a second archived ref for the record only (`--record-ref`),
  defaulting to `--ref`, with CI passing the commit under test; a record missing at that
  ref is a refusal (exit 2), never an empty record"*.
- `RL-1145` is on `main`. `ls docs/rulings/RL-01145* | wc -l` prints `1`.

**Step 3, the baseline readings.** All were taken at `9fe726b2` on a clean tree
(`git status --porcelain | wc -l` → `0`), 2026-09-27 12:06:20 BST:

| Reading | Command, verbatim | Result |
|---|---|---|
| Docs audit | `python3 scripts/audit-docs.py; echo rc=$?` | rc `0`; `All checks passed.`; `DISCLOSED (865, at or under the W37-11 residue ceiling):` |
| Id lint | `python3 scripts/doc-id.py check; echo rc=$?` | rc `0` |
| Check-30 count (C11) | `python3 scripts/audit-docs.py 2>&1 \| grep -c '^  - check 30'` | `70` |
| Reserved count (C14) | `grep -c 'reserved (not yet materialised)' docs/INDEX.md` | `57` |
| Reference limb, first command (acceptance item 7) | `D=$(python3 -c "import sys; sys.path.insert(0,'scripts'); import _docid; print(dict(_docid.LEGACY_FORM_PATTERNS)['legacy audit path'].pattern)"); git ls-files "$D" \| wc -l` | `1` (the record) |
| Reference limb, second command | `git grep -l -F "$D" -- . ':!docs/REDIRECTS.csv' \| wc -l` | `183` |

The 183 files fall into five classes, with 0 files left unclassified. The classifier was a
path-prefix test, run in the order record, then INDEX, then frozen, then living, then
instruments:

- Frozen governed records: 150 in all. Closures 45, findings 42, plans 22, rulings 17,
  ledgers 11, research 7, rfcs 6.
- Living documents: 9 in all. `docs/process` 6, `.claude/skills` 2, `docs/roadmap.md` 1.
- Instruments and their tests: 22 in all. `scripts` 6, top-level `tests` modules 9,
  `tests/fixtures` 5, `backend/tests` 2.
- Generated `docs/INDEX.md`: 1.
- The record itself: 1.

So 150 + 9 + 22 + 1 + 1 = 183. This matches `RL-1145` DP-3 amendment 4, class by class.

**The standing verify, run as `.github/workflows/docs.yml`'s `doc-id migrate --verify`
step runs it.** `--ref` was read from `docs/process/delivery-process.core.json`
`meta.verified_against_tree` (= `0651c1e265648cbd3918adfc729ad965b83b1e0b`). The command
ran inside the `dev-commands` verify-slot wrapper, with the thread caps:
`python3 scripts/doc-id.py migrate --verify <throwaway dir> --ref 0651c1e265648cbd3918adfc729ad965b83b1e0b`.
It ran from 12:06 to 12:24:18 BST and exited `1`. Its render opens with
*"UNCHANGED: 1 fatal row(s), matching the recorded set of 1 in
`_docverify.EXPECTED_VERDICTS` — the standing red, and this change moved no row."* The one
`[FAIL]` row is (g). Its g2 reading is `classified-by-none=207`. The residue by cause is:

| Cause | Count |
|---|---|
| `cause3-legacy-path-citation` | 103 |
| `slash-compound-citation` (unassigned) | 29 |
| `unmapped-work-slice-key` | 28 |
| `cause2a-range-citation` | 15 |
| `other` | 12 |
| `cause1-foreign-frontmatter` | 11 |
| `cause4-compound-token-adjacent-uppercase` | 5 |
| `new-frontmatter-stamp-no-move` (unassigned) | 4 |
| **Sum** | **207** |

The parts sum to the whole, and the total equals the 207 of #757's squash body at
`29e7a9c`. The render prints no `RESIDUE CEILING`, `PROGRESSED` or `REGRESSION` line. This
is consistent with C16 (`FD-1147`). It is not evidence about the ceilings.

Landed in: this PR — the pre-squash branch commit that creates this file.

### Task 2 — F109, `--record-ref`, fail-closed, and C16 (RL-1145 DP-2 (c), amendments 1–3)

**What changed:**

- `scripts/_docverify.py` has a new `load_w37_11_record_at_ref`. It reads the record from
  its own `git archive` of the commit that `--record-ref` resolves to (default `--ref`),
  and extracts it to a throwaway directory. `verify()` calls it before the slot lock,
  because a refusal is meant to be instant.
- A record that is absent at that commit raises the new `ResidueRecordMissingError`, and
  so does a `--record-ref` that does not resolve. `doc-id.py migrate --verify` maps the
  error to exit `2`, and the message names the path it looked for (`W37_11_RECORD_PATH`,
  by symbol). `load_w37_11_record` keeps its degrade-to-`()` behaviour for
  `audit-docs.py`.
- `VerifyResult` gains `record_ref` and `record_ref_sha`. The render header prints a
  `record ref` line.
- The input-provenance table marks the old `load_w37_11_record(snap.control)` row
  superseded. It gains the HERMETIC `--record-ref` row, which states why the record's
  control-path keys still meet a corpus read at `--ref`.
- `.github/workflows/docs.yml` passes `--record-ref HEAD`, the commit under test.
- **C16:** `_set_change_block` no longer returns the bare `UNCHANGED` line when there are
  residue changes. It prints `UNCHANGED VERDICT SET: … no row verdict moved, but the W37-11
  residue ceiling did: <consequence>.`, followed by the residue-ceiling block.

**Red at main's code.** Stamp 12:27:57 BST, HEAD `1eb12bab`, `_docverify.py` blob
`6fc405017e50` (the same blob as at `271088b0` and `9fe726b2`), `doc-id.py` blob
`8053a06bb7b8`. The four new tests in `tests/test_doc_id_verify.py` all failed:

| Test | Failure at main's code |
|---|---|
| `test_record_ref_reads_the_record_from_its_own_archived_ref` | `TypeError: verify() got an unexpected keyword argument 'record_ref'` |
| `test_record_missing_at_record_ref_refuses_with_exit_2_and_names_the_path` | `AttributeError: … has no attribute 'ResidueRecordMissingError'` |
| `test_a_residue_progress_on_an_unchanged_verdict_set_is_rendered` (C16) | `AssertionError: assert 'RESIDUE CEILING' in '…the standing red, and this change moved no row.'` |
| `test_a_residue_regression_on_an_unchanged_verdict_set_is_rendered_and_exits_3` (C16) | `AssertionError: assert 'RESIDUE CEILING' in '…the standing red, and this change moved no row.'` |

The two C16 tests fail on the defect itself. Each builds a residue change on an unchanged
verdict set, and main's render prints the "moved no row" line with no residue block. The
regression case has `exit_code == 3` at that point.

**Green at the head.** All four passed (`4 passed, 160 deselected`). Then
`tests/test_doc_id_verify.py`, `tests/test_doc_id_migrate.py` and
`tests/test_audit_docs_w37_11_ceiling.py` together gave `490 passed, 1 skipped`.
`ruff check` and `mypy` were both clean (`no issues found in 196 source files`).

**Broken-input proofs.** Each file was copied aside, sabotaged, run, and restored by copy,
with a hash check (`RESTORED-OK`):

1. **The wiring reverted.** In `verify()`, `effective_record_ref = ref`. The F109 test
   failed with `the record must be read at --record-ref (B), not at --ref (A)`,
   `assert [('docs/a.md', 'd4', 1)] == [('docs/a.md', 'd4', 5)]`.
2. **Fail-closed reverted.** A missing record returns `()`. The exit-2 test failed with
   `Failed: DID NOT RAISE ResidueRecordMissingError`.
3. **The CLI's exit-2 mapping reverted.** The exit-2 test failed with the uncaught
   `ResidueRecordMissingError: the W37-11 record is missing at --record-ref '<sha>' (<sha>):
   looked for <the record path> — an absent record would turn every ceiling off, so the
   verify refuses rather than read it as empty (RL-1145 DP-2 amendment 1)`. The message
   names the record's path from the constant. It is described here, not spelled, per
   RL-1140.

**On the real repository** (12:29:49 BST), the command was
`python3 scripts/doc-id.py migrate --verify <dir> --ref HEAD --record-ref 726ec98f --no-baseline`.
`726ec98f` is the parent of `ea3704dd`, the commit that first added the record. The run
printed `refused: the W37-11 record is missing at --record-ref …` and exited `rc=2` at
once. No snapshot directory was created.

Landed in: this PR — the pre-squash branch commit that carries Task 2.

### Task 3 — the record move and the reference limb (RL-1145 DP-3 (a), amendments 1, 3, 4)

**Step 1** is recorded under Task 1: `1` tracked file and `183` referencing files at
`9fe726b2`. The classes were 150 + 9 + 22 + 1 + 1.

**Step 2, the move.** `git mv` took the record from its legacy location to
`_docid.W37_11_RECORD_PATH`, a `docs/process/` file named `residue-ceiling-record.md`. The
name says what the file is: the residue-ceiling record. The file's content is unchanged
(`git status` reads it as a pure rename, `R`).

- **The constant.** `_docid.W37_11_RECORD_PATH` is the only code spelling of the new path
  (DP-3 amendment 1). Every reader reaches it by symbol: `_docid.load_w37_11_record`,
  `_docverify.load_w37_11_record_at_ref`, `audit-docs.py`'s `_id_scope_documents` and
  `_partition_by_w37_11_record`, and `doc-id.py`'s `classify_docs_files`.
- **The redirect row.** `docs/REDIRECTS.csv` gains one row in the shape of row 3 (empty
  `old_id`/`new_id`, empty `citing_dir`/`part_ordinal`). It is inserted after the two
  checklists rows, which are the same kind of move into `process/`. The file's CRLF line
  endings are kept (`git diff --stat`: 1 insertion). The row's two paths were written from
  the two constants by symbol.
- **One addition the ruling did not name: `_docid.W37_11_RECORD_PRE_MOVE_PATH`.** The
  constant served two roles. One is the record's home in a current tree. The other is its
  location in the **pre-migration** tree that `migrate --verify` still migrates: the pinned
  base, `core.json`'s `meta.verified_against_tree`, where the record sits at its legacy
  location. The move changed the first role and broke the second. Measured before this
  addition: with only `W37_11_RECORD_PATH` moved, `sweep_exclusion_reason(<the pre-move
  path>)` returned `None`. So a verify of the pinned base would sweep the record, count its
  quoted legacy forms as (d)/(e)/(g) residue, and bucket it as row (a)'s `none`. The new
  constant holds the pre-move location, and two readers use it:
  `GOVERNANCE_RECORD_EXCLUSIONS` gains a row for it, and `classify_docs_files` buckets
  either location as `reference`. It is the only code spelling of the old location.
  Tests name that location by this symbol. RL-1140's rule is kept: this ledger describes
  the old location and does not spell it.
- **`docs/INDEX.md` needed no change.** The record carries no RFC-937 header, so INDEX
  listed it neither before nor after the move. `python3 scripts/doc-index.py` followed by
  `--check` gave `OK (byte-stable)`, and `git status` shows no INDEX change. INDEX stays
  in the "generated" class because its own text still spells the legacy directory for
  other files.

**Step 3, the readings on the move tree** (staged, before the commit):

| Reading | Command, verbatim | Result |
|---|---|---|
| First command of acceptance item 7 | `git ls-files "$D" \| wc -l`, with `D` derived by symbol as in Task 1 | **`0`** |
| Reference limb | `git grep --cached -l -F "$D" -- . ':!docs/REDIRECTS.csv' \| wc -l` | **`183`** |
| The set against Task 1's | `diff` of the two file lists | one line out (the record's legacy location), one line in (`_docid.W37_11_RECORD_PATH`) |

The limb stays at 183 because the record still quotes legacy paths in its rows as evidence.
That is the reason `GOVERNANCE_RECORD_EXCLUSIONS` exists. So the five classes still sum:
150 + 9 + 22 + 1 + 1 = **183**.

- **Frozen, 150.** None was edited. Each is resolved by the redirect row.
- **Living, 9.** None was edited in this PR, on the lead's Q2 ruling. The six
  `docs/process/` documents and `docs/roadmap.md` are left to their owners in the docs PR.
  The two skills were read hit by hit, and neither holds a path to the record:
  - `.claude/skills/reproducing-ci-locally/SKILL.md:206` is a dated 2026-09-02 incident
    about another file under the legacy directory.
  - `.claude/skills/docs-audit/SKILL.md:142` and `:752` describe check 25's resolution
    sources, which the code still reads. `:161` describes the check's scanning scope.
    `:302` quotes `document-ids.md`'s own prose.
  - Neither skill is wrong, so each is **read, and no edit is needed**. Editing a legacy
    spelling that describes a legacy form would be the sweep that DP-3 amendment 4 forbids.
- **Instruments and their tests, 22.** Each was read, never swept. A path to the record
  moved with the constant, and a definition of the legacy form stayed.
  - **Edited, 6:**
    - `scripts/_docid.py`: the constant, the new pre-move constant, and the exclusion
      row.
    - `scripts/_docverify.py`: three rendered notes now print `{W37_11_RECORD_PATH}`, and
      six comments or docstrings cite the record by symbol.
    - `scripts/doc-id.py`: `classify_docs_files` accepts both locations.
    - `tests/test_doc_id_verify.py`: five loader fixtures now write the record at
      `dv.W37_11_RECORD_PATH` instead of a literal legacy join (these would have read
      `()`), and four docstrings cite the record by symbol.
    - `tests/test_doc_id.py`: the classify test now exercises **both** locations. With
      the new location alone, the test passes without the carve-out, through `process/`'s
      own bucket. The sweep-exclusion test and its negative control (`<path>.bak`) cover
      both constants.
    - `tests/test_findings_ids.py`: one docstring said the legacy directory "still holds"
      the record, which is no longer true.
  - **Stays, 16. Each was read, and each hit is a legacy-form definition, a frozen corpus,
    or a path to another file:**
    - `scripts/audit-docs.py`: the legacy register, phase and closure sources, and the
      comments about them.
    - `scripts/file-census.py`: the frozen-prefix table.
    - `scripts/register-lint.py`: the legacy register path and its history.
    - The five files under `tests/fixtures`: four in the `docs-migration` corpus and the
      `w37-3-corpus` register. They are frozen fixture corpora.
    - `tests/test_audit_docs_finding_citations.py`: the docstring about the legacy
      work-item location.
    - `tests/test_audit_docs_ids.py`: the census fixture rows at `:1103` and `:1111`,
      which are data about a legacy location; the legacy-form lists; and the deliberately
      nonexistent path at `:2363`, which is a sentinel and not the record.
      `_docid.W37_11_RECORD_PATH` is read there by symbol.
    - `tests/test_audit_docs_w37_11_ceiling.py`: synthetic control paths.
    - `tests/test_doc_id_migrate.py`: the migration's legacy source fixtures.
    - `tests/test_doc_index.py`: a synthetic redirect row.
    - `tests/test_file_census.py`: the prefix cases.
    - `backend/tests/test_lineage.py`: a comment on the dissolution.
    - `backend/tests/test_lineage_census_carveout.py`: a census fixture row.
    - One constant **stays byte-for-byte although it names the record**:
      `_docid.CONTROL_PATH_UNRESOLVED`. It is a sentinel row key **inside the record's own
      rows**, so changing it would un-key those rows.
- **Generated, 1.** INDEX.md, unchanged (above).
- **The record, 1.** Moved.

**Docs gates on the move tree:** `audit-docs.py` rc `0`, `All checks passed.`,
`DISCLOSED (865, at or under the W37-11 residue ceiling):`. The seven owner-edited living
documents still spell the old location. `doc-id.py check` rc `0`. `doc-index.py --check`
gave `OK (byte-stable)`.

**Tests:**

- `uv run pytest -q tests/` gave `1024 passed, 1 skipped`.
- `backend/tests/test_lineage.py` and `test_lineage_census_carveout.py` gave `35 passed`.
  A first run gave 23 errors, all `GIP_TEST_DATABASE_URL is not set, and the per-worktree
  test database 'gipricing_code' does not exist yet`. That is environmental. The database
  was created with `dev-commands`' block (`docker exec … createdb … gipricing_code`, then
  `alembic upgrade head`), and the run was repeated.
- `ruff check .` was clean. `mypy` gave `no issues found in 196 source files`.
- No tracked `docs/process/` file was modified by a test run (face F9).

**Broken-input proofs for the pre-move constant.** Each file was copied aside and
restored by copy, with a hash check (`RESTORED-OK`):

4. **`classify_docs_files` narrowed back to the current location only.** The classify
   test failed with `AssertionError: <the pre-move path>`,
   `assert {'none': 1} == {'reference': 1}`.
5. **The pre-move exclusion row pointed at a nonexistent path.** The sweep-exclusion test
   failed with `assert None is not None`, where
   `None = sweep_exclusion_reason(<W37_11_RECORD_PRE_MOVE_PATH>)`.

Landed in: this PR — the pre-squash branch commit that carries Task 3.

## PRs

| # | Branch | Squash SHA on `main` | Tasks | State |
|---|---|---|---|---|
| — | `w37-11-code` | — | 1–6 | in progress |
