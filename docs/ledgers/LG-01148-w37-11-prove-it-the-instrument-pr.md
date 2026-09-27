---
id: LG-1148
family: ledger
title: W37-11 — prove it, the instrument PR
status: closed
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

**The lead's rulings on Task 3, written 2026-09-27 13:26:57 BST.** They are quoted from the lead's message
that accepted Task 3 at `cdc35fa2`:

- **`_docid.W37_11_RECORD_PRE_MOVE_PATH` was adopted by the lead**, as a mechanism under
  RL-1145 DP-3. The lead's reasoning: amendment 1 governs how the new path is spelled, and
  the pre-move constant is the only code spelling of the old location, which the
  pinned-base verify still migrates. It is justified by the measurement above
  (`sweep_exclusion_reason(<old>)` returned `None` with the constant alone) and proved by
  broken-input proofs 4 and 5.
- **The two skills were not edited, and the lead accepted this.** Neither holds a path to
  the record, and an edit would be the sweep that amendment 4 forbids.

**A side effect for the row-9 cleanup: the test database `gipricing_code`.** It was
created in the shared postgres container on 2026-09-27 for this worktree's backend tests,
with `docker exec gi-pricing-postgres-1 createdb -U gipricing -T gipricing gipricing_code`
and then
`GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_code uv run alembic upgrade head`
(`dev-commands`, the per-worktree test database block). Drop it when the worktree is
released.

Landed in: this PR — the pre-squash branch commit that carries Task 3.

### Task 4 — the census-row shrink, and C15 (RL-1145 DP-2 amendment 4; the deputy's Q4 ruling)

**Step 1, the census read before the shrink, with this PR's tool.** Scratch script
`t4_verify.py` (local, in the job directory, not committed) called
`_docverify.verify(docid, ref='0651c1e265648cbd3918adfc729ad965b83b1e0b',
record_ref='cdc35fa292334d3337d5f172f26a3411ae22c6e9', keep=True, with_baseline=True)`, and
read `VerifyResult.measured_residue` for the record's three census rows. It ran from
12:45:39 to 13:23:00 BST in the verify slot `verify-1`, with the `dev-commands` thread
caps, and exited `rc 0`. The tool was the code at `cdc35fa2`, and 523 record entries were
read at the record ref.

| Census row (`cls`) | Ceiling before | `measured_residue` |
|---|---|---|
| `h1-check36` | 17 | **0** |
| `d9` | 14 | **0** |
| `d10` | 2 | **0** |

The key is the record's own control-path key for the census CSV (`CR-1063` §3). All three
read 0, so the stop condition did not fire.

**The same run is the end-to-end proof of Task 3's move.** It returned
`set_changes = []` and `exit_code = 1`. Every verdict equals `EXPECTED_VERDICTS`, and the
only FAIL is (g). g2 read `classified-by-none=207`. `residue_changes` held exactly three
entries, the `PROGRESSED (W37-11 record can shrink)` lines for these three rows, and **no
`REGRESSION`**. Its render opens with
*"UNCHANGED VERDICT SET: 1 fatal row(s), matching the recorded set of 1 in
`_docverify.EXPECTED_VERDICTS` — no row verdict moved, but the W37-11 residue ceiling did:
progress only, so the record can shrink and the exit code is unaffected."*, followed by
`W37-11 RESIDUE CEILING (3)`. This is C16's fix seen on the real corpus. Main's CI render
printed no residue block at all.

**Step 2, the shrink.** Commit `0a0effb9` touches only the record. Each of the three rows
changes its count cell (17 → 0, 14 → 0, 2 → 0), and its reason cell gains one sentence:
*"Shrunk <n> -> 0 in W37-11, written under the W37-11 lead's authority (RL-1145 DP-3
amendment 5): measured_residue 0 at --ref 0651c1e… with --record-ref cdc35fa2…, the code
PR's tool, per RL-1145 DP-2 amendment 4 (LG-1148 Task 4)."* The path, `cls` and owner
cells are unchanged. After the commit, `audit-docs.py` gave rc `0`, `All checks passed.`,
`DISCLOSED (865, at or under the W37-11 residue ceiling):`.

**Adopted by the W37-11 lead: the three census-row shrinks of `0a0effb9` (RL-1145 DP-3
amendment 5; deputy 12:06:57 Q3).** Written 2026-09-27 13:26:57 BST, on the lead's message adopting the
diff unamended, after checking the word diff: 1 file, 3 lines, path, `cls` and owner
unchanged.

**Step 3, confirmation.** The step 1 run shows no `REGRESSION`, and its only
`PROGRESSED` lines are the three rows shrunk here. On the lead's ruling there was no
second 20-minute local run. The PR's `docs` CI job runs the verify with
`--record-ref HEAD` at the final head, and that run is the post-shrink reading. It is
quoted at the PR request.

**Step 4, C15 — option (a): re-derived and quoted, no rows filed.** Under the deputy's
ruling of 12:06:57 BST, no g2 row is filed in W37-11, (g) stays the standing FAIL
(RL-1145 DP-4 (b)), and the rows are deferred with the lead as owner. The event is the
first slice of the create-read-retire audit.

- **Predicate, verbatim:** row (g)'s own `Row.residue`, filtered to `count > 0`, from
  `_docverify.verify(..., ref='0651c1e265648cbd3918adfc729ad965b83b1e0b',
  record_ref='cdc35fa292334d3337d5f172f26a3411ae22c6e9')`. The tree is `0651c1e` (the
  pinned base, archived), and the tool is the code at `cdc35fa2`. Keys are
  `(control path, cls)`, the record's own key space.
- **Population: 207 keys, 207 hits** (each key 1). This equals g2's `classified-by-none=207`.
- **Keys that lack a row in the record at `cdc35fa2`: 207 of 207.** Keys under their
  ceiling: 0. **This corrects the "103" figure, by measurement.** The deputy's ruling read
  "the number of keys lacking a row (103 as read)", and 103 is #757's figure. #757
  measured it against that branch's own tip record, which carried a 123-row g2 addition,
  and #757 then dropped that addition. `main`'s record carries no g2 row at all. So at the
  DP-2 read location, all 207 keys lack a row.
- **Would filing the rows flip (g)? Yes.** This was measured on a scratch augmented record
  (the real record plus the 207 keys at their measured counts), held only in memory by the
  scratch script. Nothing was written into the repository. Two differently built
  instruments agree:
  - `_docverify._residue_fully_governed(g2_residue, augmented)` returned `True`;
  - `_docverify.row_g` itself, recomputed on the kept snapshot, returned **DISCLOSE** with
    the augmented record and **FAIL** with the real record. g1 is clean (0 mangled, 0
    provenance mismatches, 0 bare-comma violations), so nothing blocks the DISCLOSE path.
  - A flip is a set change (`EXPECTED_VERDICTS` records (g) as FAIL), so the run would exit
    `3`. This is why the deputy ruled that the rows are not filed here.
- **Local evidence (not governed, not in the repository):** the raw TSV is
  `~/gi-pricing-plan.local/handover/w37-11-c15-g2-population-0651c1e-tool-cdc35fa2.tsv`
  (header `control_path, cls, count`, 207 rows). The scratch script's JSON output is kept
  in the job directory beside it.

**The keys, grouped by `cls`.** Legacy forms are described, not spelled (RL-1140). Four
substitutions make the list regenerable:

- `⟨audit⟩/` is the legacy audit directory, the `'legacy audit path'` entry of
  `_docid.LEGACY_FORM_PATTERNS`;
- `⟨notes⟩/` is the legacy notes directory (`'legacy notes path'`);
- `⟨plans⟩/⟨2026⟩-` is the legacy dated-plan prefix (`'legacy dated-plan path'`);
- `⟨F:nn⟩` is a two-digit bare finding id (`'finding id (bare form)'`).

Every other character is verbatim, and the count follows each key.

- **`g2-cause3-legacy-path-citation`: 103 key(s), 103 hit(s).**
  - `.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py` (1)
  - `CLAUDE.md` (1)
  - `backend/src/app/platform/rating_versions.py` (1)
  - `backend/tests/test_contracts.py` (1)
  - `docs/_templates/FD.md` (1)
  - `docs/_templates/LG.md` (1)
  - `⟨audit⟩/checklists/work-item-close.md` (1)
  - `⟨audit⟩/findings/F102.md` (1)
  - `⟨audit⟩/findings/⟨F:27⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:66⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:72⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:76⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:77⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:80⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:81⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:83⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:87⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:88⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:90⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:93⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:94⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:99⟩.md` (1)
  - `⟨audit⟩/ruling-acceptance-item-sweep.md` (1)
  - `⟨audit⟩/work/W37-5b/README.md` (1)
  - `⟨audit⟩/work/W37-5c/README.md` (1)
  - `⟨audit⟩/work/nt-0010-0011-adoption/README.md` (1)
  - `⟨audit⟩/work/nt-0012-0013-0014-adoption/README.md` (1)
  - `⟨audit⟩/work/pr-265/README.md` (1)
  - `⟨notes⟩/0003-duplicated-status-goes-stale.md` (1)
  - `⟨notes⟩/0010-layered-slice-based-workflow.md` (1)
  - `⟨notes⟩/0011-per-agent-model-and-skill-settings.md` (1)
  - `⟨notes⟩/0013-the-lead-is-the-highest-error-node.md` (1)
  - `⟨notes⟩/0018-a-turn-that-ends-strands-what-it-started.md` (1)
  - `⟨notes⟩/0019-one-id-per-document.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-22-w6b-contracts-and-drift-guard.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-24-w6b-1a-model-detail-non-glm-arms.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-26-w6b-slice-map-revised-3.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-27-closure-audit-standard.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-nt-0010-0011-adoption.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-nt-0010-0011-reconciliation-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-f30-ceiling-meter-addendum.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-nfr-rate-2-sampling-structural-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-ruling-vs-plan-scope.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-slice-parallelism-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-nt-0014-0017-reconciliation.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-nt-0014-q1-q3-q4-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-nt-0017-maintainer-decisions.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-4-always-capture-correction.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-reopen-direction.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-31-f62-timing-ms-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-31-nt-0016-investigation.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-01-nt-0016-landing-package.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-01-nt-0016-slice2-fr-data-32-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-01-ruling-61-notes-tombstone-stubs-watched.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-5b-slice-decision.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-5c-slice-decision.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-6-go-ahead-ask.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-6-leaf-plan-findings-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-6-migration-run-leaf-plan-v2.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-6-migration-run-leaf-plan.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-6-outstanding-obligations.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-6-twelve-non-close-records-derivation.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-commit-boundary-and-plan-reviews-shape-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-container-family-and-line-citations-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-field-set-and-rollup-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-gap-1-ruling-86-owner-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-migration-preconditions-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-owner-field-derivation.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-pending-proposals-container-family-derivation.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-readme-owner-derivation.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-rfc-readme-row-and-stamp-set.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-roadmap-transform-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-ruling-88-acceptance-amendment.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-ruling-a-series-and-standalone-ruling-files.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-ruling-a-series-family-derivation.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-stage-boundary-authority-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-template-parser-conflicts-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-vendored-exemption-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-d1-d2-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-go-ahead-re-ask.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-maintainer-decisions.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-renewed-window-handover.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-ruling-100-split-source-citations.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-ruling-98-prose-migration.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-time-boxed-delegation.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md` (1)
  - `docs/process/delivery-process.md` (1)
  - `docs/research/w11-task-2d-nfr-rate-1-full-path.md` (1)
  - `packages/model-schema/tests/test_rating_algorithm.py` (1)
  - `packages/pricing-core/src/pricing_core/rating/runtime.py` (1)
  - `packages/pricing-core/tests/test_rating_compile_bundle.py` (1)
  - `scripts/hooks/retry_cap_hook.py` (1)
  - `scripts/register-lint.py` (1)
  - `tests/test_audit_docs_w37_11_ceiling.py` (1)
  - `tests/test_doc_index.py` (1)
  - `tests/test_notes_move_citations.py` (1)
  - `tests/test_register_lint.py` (1)
  - `tests/test_retry_cap_hook.py` (1)
  - `tests/test_ruling_acceptance_census.py` (1)
- **`g2-slash-compound-citation (unassigned — reported, not investigated)`: 29 key(s), 29 hit(s).**
  - `backend/src/app/worker/scoring_handlers.py` (1)
  - `⟨audit⟩/file-taxonomy-draft.md` (1)
  - `⟨audit⟩/phases/1b/README.md` (1)
  - `⟨notes⟩/0006-two-rules-for-reading-an-artifact.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-5-partial-dependence-exposure-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-5-partial-dependence-exposure.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-26-w6b-slice-map-revised-2.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-1-evaluator-core.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-2-realtime-scoring-endpoint.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-3-batch-scoring.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-3-d6-batch-resumability-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-4-trace-sampling-persistence.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-decision-points-recovery.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-scoring.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-slice1-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-slices-3-4-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-nt-0015-q1-q5-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-reopen-scope-and-batch-frame-contract-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-row-g-reading.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-ruling-103-ef-readings-and-index-placement.md` (1)
  - `docs/research/w11-task-3d-nfr-rate-5.md` (1)
  - `docs/research/w11-task-4d-nfr-rate-12.md` (1)
  - `docs/specs/03-rating-engine.md` (1)
  - `packages/pricing-core/src/pricing_core/rating/compile.py` (1)
  - `packages/pricing-core/tests/test_rating_compile.py` (1)
  - `scripts/audit-docs.py` (1)
  - `scripts/bench-rating.py` (1)
  - `scripts/bench-trace-size.py` (1)
  - `scripts/register-owed.py` (1)
- **`g2-unmapped-work-slice-key (named elsewhere, reported here by shape)`: 28 key(s), 28 hit(s).**
  - `⟨audit⟩/findings/⟨F:91⟩.md` (1)
  - `⟨audit⟩/findings/⟨F:92⟩.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-22-w6b-contracts-and-drift-guard-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-22-w6b-slice-map.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-10-untested-behaviour-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-2-validation-rule-catalogue-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-3-dataset-list-derived-fields-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-4-ebm-predict-arm-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-4-ebm-predict-arm.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-6-backtest-and-objective-endpoint-tests-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-7-workspace-identity-and-selection-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-8-artifact-library-list-routes-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-9-transparency-exposure-share-ledger.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-23-w32-closure-proposal.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-24-w32-11-certificate-floors-and-two-generated-sides.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-24-w6b-13b-catalogue-chain.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-24-w6b-1b-diagnostics-view.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-25-w6b-11-workspace-selector.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-25-w6b-13-rule-versioning-screen.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-25-w6b-3-dataset-list-contents.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-25-w6b-4a-model-spec-builder-builtin.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-25-w6b-4b-custom-objective-arm.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-25-w6b-5a-treeshap-holdout-pass.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-25-w6b-5b-suggestion-panel.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-26-w6b-12-dataset-lineage.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-26-w6b-15-minor-rename.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-migration-revert-proof.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-03-w37-6-window-handover.md` (1)
- **`g2-cause2a-range-citation`: 15 key(s), 15 hit(s).**
  - `⟨audit⟩/phases/1b/register.md` (1)
  - `⟨audit⟩/register.md` (1)
  - `⟨audit⟩/retrofit-impossible.md` (1)
  - `⟨audit⟩/work/W11/README.md` (1)
  - `⟨notes⟩/0005-deferred-items-with-no-durable-custody.md` (1)
  - `docs/phase-0-status.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-1-2-rate-table-maturity-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-algorithm-pin-maturity.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-slice2-rulings.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-slices-2-4-planning-readiness.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-slices-2-4-rulings.md` (1)
  - `docs/skills-map.md` (1)
  - `docs/specs/06-governance.md` (1)
  - `docs/specs/07-platform.md` (1)
  - `scripts/doc-id.py` (1)
- **`g2-other`: 12 key(s), 12 hit(s).**
  - `.claude/skills/planning-with-files/scripts/check-complete.ps1` (1)
  - `.claude/skills/planning-with-files/scripts/set-active-plan.ps1` (1)
  - `backend/tests/test_wf01_journey.py` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-3-batch-readiness-and-d6.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-nt-0012-0013-0014-adoption.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-2b-bundle-resolution-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-4b-trace-environment-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-08-30-w11-service-account-permissions-ruling.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-01-maintainer-delegation-and-nt-0019-precedence.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-02-w37-vacuous-acceptance-item-ruling.md` (1)
- **`g2-cause1-foreign-frontmatter`: 11 key(s), 11 hit(s).**
  - `.claude/skills/close-workstream/SKILL.md` (1)
  - `.claude/skills/dev-commands/SKILL.md` (1)
  - `.claude/skills/docs-audit/SKILL.md` (1)
  - `.claude/skills/git-hygiene/SKILL.md` (1)
  - `.claude/skills/phase-review/SKILL.md` (1)
  - `.claude/skills/repo-architecture/SKILL.md` (1)
  - `.claude/skills/reporter-cycle/SKILL.md` (1)
  - `.claude/skills/requesting-code-review/SKILL.md` (1)
  - `.claude/skills/spec-change/SKILL.md` (1)
  - `.claude/skills/watcher-runtime-state/SKILL.md` (1)
  - `.claude/skills/writing-plans/SKILL.md` (1)
- **`g2-cause4-compound-token-adjacent-uppercase`: 5 key(s), 5 hit(s).**
  - `⟨audit⟩/closure-records.md` (1)
  - `⟨audit⟩/plan-reviews.md` (1)
  - `⟨plans⟩/⟨2026⟩-09-04-w37-6-migration-run-ledger.md` (1)
  - `scripts/_docid.py` (1)
  - `scripts/_docverify.py` (1)
- **`g2-new-frontmatter-stamp-no-move (unassigned — reported, not investigated)`: 4 key(s), 4 hit(s).**
  - `.claude/roles/watcher.md` (1)
  - `.claude/skills/README.md` (1)
  - `README.md` (1)
  - `⟨audit⟩/findings/README.md` (1)

Landed in: this PR — the record commit `0a0effb9` (step 2) and the ledger commit that
carries this section, both pre-squash branch commits.

### Task 5 — F107, the idempotence proof: NOT MET (a finding, recorded and not fixed)

**Method** (plan Task 5 steps 1–2, verbatim in effect):

- `git archive 03f61d83437a9dd4138b7e7309b22c96148f3680 | tar -x -C <job dir>/t5-snap`.
  That commit is this branch's head after Task 4, and its tree is already migrated.
- Inside the snapshot: `git init -q -b snapshot`, `git add -A`, and one commit. The
  snapshot holds 1709 files, `status --porcelain` read `0`, there is no `.venv`, and it
  lies outside every worktree.
- Then, with the branch's own tool and the `dev-commands` thread caps:
  `python3 scripts/doc-id.py migrate --repo-root <job dir>/t5-snap`. It ran 13:28:26 →
  13:28:32 BST, exited `rc 0`, printed `doc-id.py migrate: 0 id(s) assigned`, and wrote
  17 files.

**Reading (step 3):** `git -C <snapshot> status --porcelain | wc -l` → **`17`**, not the
expected `0`. `git diff --stat`: **17 files changed, 57 insertions(+), 51 deletions(-)**.
The files are:

- the two `planning-with-files` PowerShell scripts, 2 lines each;
- `.github/ISSUE_TEMPLATE/bug.yml` 2, `question.yml` 2, and `.github/workflows/docs.yml` 2;
- `docs/REDIRECTS.csv` 9;
- `CR-1063` 16, `CR-1065` 8, `docs/findings/register.md` 8, `LG-1141` 6, `PL-1071` 2 and
  `PL-1072` 2;
- `docs/process/delivery-process.core.json` 2 and `docs/roadmap.md` 2;
- `scripts/_docverify.py` 2, `scripts/audit-docs.py` 6 and `scripts/doc-id.py` 35.

**The six change classes,** each with one described example, taken from a word diff:

1. **Padded ids are unpadded in prose and code.** In `bug.yml`, a five-digit zero-led
   finding id becomes its unpadded form. In `docs.yml`, a padded plan-id citation does the
   same.
2. **Plain citations are wrapped into links.** `register.md` gains four link wraps of the
   `CR-1063` citation, and `docs/roadmap.md` gains one of `CR-1065`.
3. **A legacy-form SPEC constant is rewritten: a corpus-correctness defect of a re-run.**
   In `scripts/_docverify.py`, a string constant naming the RFC's original note under the
   legacy notes directory is rewritten to point under `rfcs/`. The constant must keep its
   legacy form (`doc-id-migration-run`, "Legacy-form-spec constants").
4. **Code is corrupted: a corpus-correctness defect of a re-run.** In
   `planning-with-files/scripts/check-complete.ps1`, the PowerShell static-member operator
   in `[Console]::Out.Write(` becomes `[Console]: :Out.Write(`, which breaks the script.
   The sibling `set-active-plan.ps1` has the same defect on a different call:
   `[System.IO.File]::WriteAllText(` becomes `[System.IO.File]: :WriteAllText(`. This was
   checked from its own diff, not assumed.
5. **`core.json`'s `meta.verified_against_tree` is overwritten,** from `0651c1e…` to
   `75779691…`, the snapshot's own commit. **This is inherent:** a real run records its
   run ref by design (`PL-960`), so a diff here is expected of any second run.
6. **`docs/REDIRECTS.csv` is regenerated.** Rows are re-sorted, and one row is added: the
   redirect for the file census CSV from the legacy audit directory to `docs/research/`.
   The row added in Task 3 is kept, only moved. A first reading said it was dropped, and a
   line-level re-check corrected that before the report.

**Local evidence (not governed, not in the repository):**
`~/gi-pricing-plan.local/handover/w37-11-t5-second-migrate-03f61d8/` holds `t5-status.log`,
`t5-diffstat.log`, `t5-diff.patch` (476 lines) and `t5-migrate.log`.

**Verdict (lead's ruling (A), record only; written 2026-09-27 13:29:48 BST):** F107 / C4 / PL-1144
acceptance item 4: NOT MET. Idempotence disproven at 03f61d83 (17 files). The finding is to
be filed by the auditor in the docs PR; C4's re-typing is the deputy's verdict. No re-run
defect is fixed in this PR.

**C4 re-typed by the deputy, 2026-09-27 13:30:35 BST** (the lead's local channel file
`to-lead.md`, the entry headed *"C4 (F107 idempotence) RE-TYPED: option (i) — deferred with
the lead as owner; …"*). It was relayed by the lead, and written here 2026-09-27 13:31:08 BST:

- **Verdict.** *"C4 re-typed by delegation: (i). Exit `status --porcelain` 0 is NOT MET at
  `03f61d83` (17 files, +57/−51); the §13 verdict is **deferred with an owner** — the
  lead — event: the create-read-retire audit's first slice."* The executor's (A),
  record only, stands.
- **The severity note, verbatim:** *"classes 3 and 4 make a second `migrate` over a
  migrated tree actively harmful (a legacy-spec constant rewritten, PowerShell `::` split),
  and the harm is latent because nothing in standing CI re-runs migrate on the live tree
  (`--verify` migrates the pinned pre-migration base into a snapshot). A reader of the
  register must not be able to take "idempotence disproven" for a cosmetic re-sort."*
- **The recommended fix is the guard, not the four mechanisms:** *"`migrate` refuses, with
  a non-zero exit and a named reason, to run over a tree that is already migrated … with a
  broken-input test. That is bounded, prevents the harm, and leaves true idempotence to
  the audit."* The guard may land in this PR only if it is one check plus one test with
  the gate green (the ruling's condition 3). On the lead's instruction, it goes to the
  lead as a proposal after Task 6, before any code is written.
- **The other conditions:** the auditor files the `FD-` row and essay first in the docs
  PR, typed *"disproven in W37-11, fix deferred"*. The D7 line names C4 among the items
  the Work closes over.

Landed in: this PR — the pre-squash branch commit that carries this section.

### Task 6 — F110, finding FD-1069: one population, one docstring

**Step 1: the behaviour test comes first.**
`tests/test_doc_id_verify.py::test_h1_residue_by_file_resolves_against_the_sweep_filtered_population`
builds a real git corpus that tracks one sweep-excluded file, `uv.lock`
(`_docid.LOCKFILE_EXCLUSIONS`), beside `docs/a.md`. It feeds `_h1_residue_by_file` one
check-36 failure line naming each file. The test asserts three things:

- `uv.lock` is tracked (`git ls-files`) but absent from `tracked_files`;
- `docs/a.md` is keyed per file, `('docs/a.md', 'h1-check36'): 1`;
- the lockfile falls to `(_H1_UNLOCATED_PATH, 'h1-check36'): 1`.

It **passed on the unchanged code** (`1 passed`). So the behaviour says the population is
`tracked_files`'s own, **filtered** by `sweep_exclusion_reason`. `tracked_files`'s
docstring was right. `_h1_residue_by_file`'s docstring ("the unfiltered tracked-file set")
was wrong.

**Proof 6, that the test discriminates** (made in a copy and restored, `RESTORED-OK`). With
`tracked_files`' filter replaced by `if True`, the test failed:
`AssertionError: assert 'uv.lock' not in ['___placeholder___.md', 'docs/a.md', 'uv.lock']`.

**Step 2: the docstring is fixed, and the code does not change.** The word "unfiltered"
was corrected at four sites that made the same claim about this one population:

- `_h1_residue_by_file`'s docstring;
- its in-body comment above `known_files`;
- `rows_h`'s docstring, which said the same thing about `tracked_files(mig.tree)`;
- the test helper `_files_corpus`'s docstring.

Each now says the set is filtered by `sweep_exclusion_reason`, and names F110. Afterwards,
`grep -rn -i 'unfiltered tracked' scripts tests` returns nothing.

**Step 3.** `tests/test_doc_id_verify.py` gave `164 passed, 1 skipped`. `ruff check .` was
clean. `mypy` gave `no issues found in 196 source files`.

**Slip, recorded 2026-09-27 13:38:36 BST:** `f7baff08` was committed and pushed with `audit-docs.py` rc
`1`. Check 25 failed on a bare parenthesised finding id in this section's heading. The next
commit, `9422776b`, fixed it, and from then on every commit command is gated on audit rc
`0`. The lead accepted this as disclosed.

Landed in: this PR — the pre-squash branch commit that carries Task 6.

### The migrate guard — C4's recommended fix, adopted by the lead (the deputy's condition 3)

**Adopted by the W37-11 lead, recorded 2026-09-27 13:38:36 BST.** The lead adopted the executor's proposal as
written, under the deputy's C4 condition 3 (one check, one test, the gate green). Before
adopting, the lead checked that at `origin/main` the only non-verify `migrate` invocation
anywhere in `.github`, `scripts` or `.claude/skills` is the `doc-id-migration-run` skill's
one-time run over a pre-migration root. So the guard breaks nothing.

- **Predicate.** The new `_docid.is_migrated_tree(root)` is true when `docs/INDEX.md` and
  `docs/REDIRECTS.csv` are both present. This is the same sentinel as `audit-docs.py`'s
  `migrated_tree()` and `docs.yml`'s verify step. `audit-docs.py` is not repointed in this
  PR.
  - Readings by `git cat-file -e`: TRUE at `9fe726b2` (main) and at `9422776b`; FALSE at
    the pinned base `0651c1e`, where both are absent.
- **Placement.** `doc-id.py`'s `_cmd_migrate`, in the non-verify branch, before
  `migrate()`. It is not inside `migrate()`, because `tests/test_doc_id_migrate.py` calls
  `migrate()` twice on the synthetic fixture by design. `--verify` cannot reach the check,
  for two reasons: it returns before the check, and it calls `migrate()` directly on a
  pinned-base snapshot, where the predicate is FALSE.
- **Exit 2**, with the reason *"doc-id.py migrate: refused: <root> is already migrated
  (docs/INDEX.md and docs/REDIRECTS.csv are both present). A second migrate is not
  idempotent: it rewrites legacy-form spec constants and corrupts PowerShell '::' (F107 /
  C4, LG-1148 Task 5). Nothing was written."*
- **The test.** `tests/test_doc_id_migrate.py::test_cli_migrate_refuses_an_already_migrated_tree`
  adds the two artifacts to the `pristine_a` fixture and commits them. It asserts rc `2`,
  the reason text, both file names, and an empty `status --porcelain` afterwards.
  - Before the guard it failed with `assert 0 == 2`.
  - **Proof 7:** with the guard replaced by `if False`, it failed again with
    `assert 0 == 2`. The file was restored with a hash check.
  - The negative side is the existing CLI runs over `pristine_a` without the artifacts,
    which still return rc `0`.
- **On a real tree.** `python3 scripts/doc-id.py migrate --repo-root <the Task 5 snapshot>`
  printed the refusal and exited `rc=2`. The snapshot's `status --porcelain` was
  unchanged: 17 lines, as Task 5 left it.
- **Suites.** `tests/test_doc_id_migrate.py`, `tests/test_doc_id.py` and
  `tests/test_doc_id_verify.py` gave `608 passed, 1 skipped`. `ruff` and `mypy` were clean.
- **The skill** (`CLAUDE.md` §12: a skill must match its tool). `doc-id-migration-run`
  gains one line after its migrate example: since W37-11 the CLI refuses a migrated tree
  (exit 2, the sentinel), because a second run is not idempotent. Its `Verified` date is
  refreshed to 2026-09-27, with the tree named.
- C4's verdict does not change: *deferred with an owner*. The guard prevents the harm; true
  idempotence stays with the create-read-retire audit.

Landed in: this PR — the pre-squash branch commit that carries the guard.

### A face found after the gate: an empty untracked directory masked a broken link

**The face, as the lead named it:** a gate run in a worktree holding an empty untracked
directory passed a link check that fails in any fresh checkout.

- **What happened.** Task 3's `git mv` emptied the legacy audit directory in this worktree
  but left it on disk: git tracks no empty directory. `docs/roadmap.md:384` linked that
  directory with a relative target. In this worktree the target existed, so
  `audit-docs.py` check 1 passed, and the full gate at `ed588f8d` passed
  (`gate-ed588f8/`). In any fresh checkout the directory does not exist.
- **Measured by the lead, at a fresh detached worktree at `ed588f8d`:** audit-docs rc `1`,
  `FAILED (1)`, `check 1: docs/roadmap.md: broken link to audit/`. The `docs` CI job at
  that head would red on the same line.
- **The executor's positive control, in this worktree, recorded 2026-09-27 13:57:04 BST.** After `rmdir` of
  the empty directory, the unchanged `ed588f8d` read rc `1` with the same `FAILED (1)`
  line. That is the lead's reading, reproduced. `find docs -type d -empty` then returned
  nothing, and a repo-wide sweep for empty directories outside caches, virtualenvs and
  `node_modules` also returned nothing.
- **The fix, written under the W37-11 lead's authority** (`roadmap.md` is not in this PR's
  Q2 edit set). Commit `edb720eb` removes only the link wrapper at `roadmap.md:384`: the
  directory's name stays as inline code, with no new text and no new legacy token. After
  it, audit-docs gives rc `0`, `All checks passed.`,
  `DISCLOSED (865, at or under the W37-11 residue ceiling):`.
- **The evidence carry** follows the deputy's identity rule. The full gate stays
  `gate-ed588f8/`. The delta readings at the final head are in `gate-<final head>/`, in
  a tree verified to hold no empty directory.

### The docs PR, Tasks 7–9 — the evidence tables (written 2026-09-27 14:45:49 BST by the executor)

Measured at `47065da50c34f0bf613f7dd972675c96d12f78ed` (#821), in detached worktrees, before the
docs branch existed. Written on `w37-11-docs` at `734e12fe6d0e993eae76efe0270ae283bf804ea7`. Under
the deputy's ruling of 2026-09-27 14:23:04 BST, the executor gathers these tables and the
auditor writes the closure record from them. The §13 verdicts below are drafts for the lead.

### Task 7 — row (g), the re-measure at `47065da5` (C3; RL-1145 DP-4 (b), amendments 1 and 2)

**The run.** The standing verify, run as `.github/workflows/docs.yml`'s `doc-id migrate --verify`
step runs it, at `47065da50c34f0bf613f7dd972675c96d12f78ed` (#821, the instrument PR's merge
tree), in a detached worktree of that commit. `--ref` was read from
`docs/process/delivery-process.core.json` `meta.verified_against_tree`
(= `0651c1e265648cbd3918adfc729ad965b83b1e0b`), and `--record-ref HEAD` resolved to
`47065da5…`. The command ran inside the `dev-commands` verify-slot wrapper (slot 1), with the
thread caps: `python3 scripts/doc-id.py migrate --verify <throwaway dir> --ref
0651c1e265648cbd3918adfc729ad965b83b1e0b --record-ref HEAD`. It ran from 14:24:15 to 14:42:03 BST
on 2026-09-27 and exited `1`. The render's header line reads *"record ref HEAD =
47065da50c34f0bf613f7dd972675c96d12f78ed (the W37-11 record only; the corpus is --ref's —
RL-1145 DP-2)"*. The render opens with *"UNCHANGED: 1 fatal row(s), matching the recorded set of 1
in `_docverify.EXPECTED_VERDICTS` — the standing red, and this change moved no row."* The one
`[FAIL]` row is (g). The render prints no `RESIDUE CEILING`, `PROGRESSED` or `REGRESSION` line.

**Step 1, the g2 line, verbatim:**
`g2 1-front-matter-stamp=0, 2-reference-token=605, 3-move=124, 4-split=1, 5-roadmap-restructure=1, 6-generated-artifact=33, classified-by-none=207`.
g1 on the same line: `WK-shape mangled = 0 in 0 file(s), provenance mismatch(es) = 0,
bare-comma-after-rewrite violation(s) = 0`.

**The residue by cause**, from the row's `note` line (`residue by cause: …`):

| Cause | Count |
|---|---|
| `cause3-legacy-path-citation` | 103 |
| `slash-compound-citation` (unassigned — reported, not investigated) | 29 |
| `unmapped-work-slice-key` (named elsewhere, reported here by shape) | 28 |
| `cause2a-range-citation` | 15 |
| `other` | 12 |
| `cause1-foreign-frontmatter` | 11 |
| `cause4-compound-token-adjacent-uppercase` | 5 |
| `new-frontmatter-stamp-no-move` (unassigned — reported, not investigated) | 4 |
| **Sum** | **207** |

**Step 2, the sum and the comparison.** 103 + 29 + 28 + 15 + 12 + 11 + 5 + 4 = 207, which
equals `classified-by-none=207`. The figure equals **207 at `29e7a9c`** (#757's squash body,
section "g2 classified-by-none: 251 → 207"), and each of the eight cause counts equals #757's
own `_residue_cause` table, cause by cause. Against **251 at `4d9fe1d`** (`CR-1063` §6,
`251 = 136/34/28/16/13/11/7/6`) the drop is 44, and #757's squash body attributes all 44 to its
forward-citation check. The 251 is quoted, not re-measured here.

**The classifier commits in `29e7a9ce..47065da5` (DP-4 amendment 1).** Predicate, verbatim:
`git log --format='%h %s' 29e7a9ce..47065da5 -- scripts/doc-id.py scripts/_docverify.py scripts/_docid.py`.
It returns two commits. Each is classified by reading its diff:

| Commit | Subject | What it changes in the g2 path | Classification |
|---|---|---|---|
| `35c954c1` (#806) | W37-8 T1+T2 — check 30 licenses the harness keys; migrate stamps no harness-only key | `doc-id.py` `_stamp_header` skips four harness-only template keys (`_HARNESS_ONLY_TEMPLATE_KEYS`). This is the migration's header writer. `classify_migration_diff` and `_residue_cause` are not touched | Not a g2 classifier change. It can move only class 1 (front-matter stamp), which reads 0 |
| `47065da5` (#821) | the W37-11 code PR | `_docverify.py`: the record read from `--record-ref` (F109), the fail-closed refusal, the C16 render, the record-path constant by symbol, the F110 docstring. `_docid.py`: the record constant moves to `process/`, and a pre-move constant keeps the record's old location in `GOVERNANCE_RECORD_EXCLUSIONS`, so the pinned base's copy stays out of the (d)/(e)/(g) corpus as before; `is_migrated_tree`. `doc-id.py`: `classify_docs_files`, the migrate guard, `--record-ref`. No changed line names `classify_migration_diff`, `_classify_content`, `_forward_citation_check` or `_residue_cause` | Touches the g2 corpus boundary, by design neutral. Measured neutral: 207 → 207 |

The figure did not move, so no move needs a commit to explain it, and no instrument defect is
reported.

**Step 3, the condition of the lead's decision of 2026-09-18 00:42 BST** (`CR-1064:464-470`:
*"the decision stands unless that re-measure shows a corpus-correctness defect"*). The
re-measure shows none. g1, the row's corpus-correctness conjunct, is 0 / 0 / 0. The g2 figure
and all eight cause counts are those the decision was taken against. Every named cause is a
classifier attribution gap: the classifier cannot attribute a hunk to one of its six lawful
classes. **The limit of this reading:** three buckets, 45 files in all (`slash-compound-citation`
29, `new-frontmatter-stamp-no-move` 4, `other` 12), are printed by the instrument as
*"unassigned — reported, not investigated"* or as `other`. This run does not investigate them,
so it shows no corpus-correctness defect in them. It does not prove there is none.

**Step 4, the §13 verdict, drafted for the lead under DP-4 (b).** Row (g): **deferred with an
owner.** The exit measurement is `classified-by-none=207` at `47065da5`, with all 207 files
assigned to a cause and the parts summing to the whole. Owner: the lead. Named event: the first
slice of the create-read-retire audit, the event the deputy's Q4 ruling of 2026-09-27
12:06:57 BST gives for C15's g2 rows. (g) stays the standing FAIL in
`_docverify.EXPECTED_VERDICTS`. The Work close accepts it explicitly, in the D7 line. Whether a
Work may close over an item that is still FAIL is the delegate's, in that line (RL-1145 DP-4).

### Task 8 — (k), element by element (C1; RL-1145 DP-5 (b), amended)

**The run.** At `47065da5`, in the same detached worktree:
`python3 scripts/doc-index.py --phase P1b; echo EXIT=$?` printed seven numbered elements and
`EXIT=0`. Acceptance item 1's table follows. The clauses are map-plan item 10's
(`PL-939:89-92`). "Second count" follows DP-5 (b) as amended: where it disagrees with the
first, both are given with their predicates and populations, and neither is picked.

| Clause | Element | Printed line, verbatim | Second count (DP-5 (b)) |
|---|---|---|---|
| Works closed and retired | 1 | `1. Works closed and retired: 4 closed (WK-661, WK-664, WK-665, WK-692), 1 retired (WK-662)` | Not a zero. No second count is required |
| Slices planned versus delivered | 2 | `2. Slices planned versus delivered: 0 planned, 0 delivered` | **Zero by construction: the Slice family has no members.** `git grep -n -E '^#+ .*SL-[0-9]+' -- docs` returns 0 lines, and `git grep -l -E '^family: slice' -- docs` returns one file, the template `docs/_templates/SL.md`. `FD-1074` records that no `SL-` row exists. The `SL-` ids in `LG-1139`'s table are candidate ids in a ledger, not rows |
| Plans superseded per Work | 3 | `3. Plans superseded per Work:` then `- WK-661: 0`, `- WK-662: 0`, `- WK-664: 0`, `- WK-665: 0`, `- WK-692: 0` | **Agrees, and is a zero of header coverage.** Over all 125 files `docs/plans/PL-*.md`: `git grep -l -E '^status: superseded'` returns 0, and every `superseded_by:` reads `~`. `git grep -h -E '^work: '` finds `work: WK-697` in 5 plans and no plan whose `work:` names a P1b Work. The instrument's predicate (`status == superseded` and `work:` equal to the Work) therefore has an empty population for each P1b Work |
| Rulings per Work | 4 | `4. Rulings per Work:` then `- WK-661: 0`, `- WK-662: 0`, `- WK-664: 0`, `- WK-665: 0`, `- WK-692: 0` | **Disagrees; both reported.** First count, the instrument: rulings whose `work:` header names the Work, which RL-1145's facts table writes as `grep -l "^work: $w" docs/rulings/*.md`. It reads 0 for each Work, and all 8 `work:` headers under `docs/rulings/` name `WK-697`. Second count, text: `grep -l "$w\b" docs/rulings/*.md`, at `47065da5`: WK-661 10, WK-662 4, WK-664 3, WK-665 6, WK-692 3. The same predicate at `271088b0` gives 9, 3, 2, 5, 2, which is RL-1145's 9, 2, 5, 2, 3 in its own order (661, 664, 665, 692, 662). The difference is `RL-1145` itself, created at `9fe726b2`, which names all five Works. The glob also takes in `docs/rulings/INDEX.md`, which names WK-661 and WK-662. Over the `RL-*.md` files only, the counts are 9, 3, 3, 6, 3. Element 4's zero is a zero of header coverage, not a proven absence of rulings |
| Findings opened versus discharged, with the unowned-decay count | 5 | `5. Findings opened versus discharged, from the register: 0 opened in P1b, 0 discharged, 0 unowned-decay in P1b, plus 0 unowned-decay carried in from an earlier phase` | **Disagrees; both reported.** First count, the instrument: register rows whose `Phase` cell equals the string `P1b` (`doc-index.py` `_findings_figures`, `r.phase == phase_id`). Its population is empty. Second count: `awk -F'\|'` over `docs/findings/register.md`'s data rows (after the table's delimiter row), on the fourth cell. It finds 121 data rows, and their `Phase` cells read `1b` 20, `2` 100, `2/3/4` 1. No cell reads `P1b`. Over the 20 rows whose cell is `1b`, with the instrument's own status rules (`resolved` anywhere → closed; a cell opening `accept` → retired; `unowned` on an active row → unowned-decay): 20 opened, 9 + 7 = 16 discharged, 0 unowned-decay. The two counts count different populations, because the register spells the phase `1b` and the report asks for `P1b`. Carry-in: `_phase_rank` cannot parse `1b` or `2`, so every row sorts last and none is "earlier" than P1b |
| Documents with no inbound citation outside `INDEX.md` | 6 | `6. Documents with no inbound citation outside INDEX.md: —` | **Disagrees; both reported.** Population, both counts: the 16 ids with `phase: P1b` in their own header or listed as the phase's Works: `CR-821`, `LG-713`, `LG-714`, `LG-715`, `LG-724` to `LG-729`, `LG-730`, and the five Works. First count, the instrument: ids cited by any corpus record's text or by `roadmap.md`, excluding self-citation. The generated `docs/INDEX.md` is not in its corpus. Every id is cited, so it prints `—`. Second count: `git grep -l -E "\b<prefix>-0*<n>\b" -- .`, excluding every `INDEX.md` in the tree, `docs/REDIRECTS.csv` and the record's own file. **9 of the 16 have no citing file**: `LG-713`, `LG-714`, `LG-715`, `LG-724`, `LG-725`, `LG-726`, `LG-727`, `LG-728`, `LG-729`. Each is cited only by `docs/closures/INDEX.md` (a Reference-family record, so in the instrument's corpus) and `docs/REDIRECTS.csv`. `CR-821`, `LG-730` and the five Works each have one or more citing files under the second count too. The difference is whether a per-directory `INDEX.md` counts as "outside `INDEX.md`" |
| Days from `active` to closure | 7 | `7. Days from a plan reaching active to its closure record being filed:` then `- (none)` | **Disagrees in kind; both reported.** First count, the instrument: plans whose header carries `phase: P1b` and whose derived execution is `closed`, paired with `CR-` records whose `work:` names the same Work. Its population is empty: of the 125 plans, 120 carry no `phase:` key and 5 carry `phase: P2`, and no `CR-` header carries a P1b Work in `work:` (the two `work:` headers under `docs/closures/` name `WK-697`). Second count, by filename: `ls docs/closures \| grep -E 'wk-6(61\|62\|64\|65\|92)'` lists 8 records, 4 of them Work closure records (`CR-754` WK-661, `CR-787` WK-692, `CR-819` WK-664, `CR-820` WK-665) and 4 plan reviews. So element 7's `(none)` is a zero of header coverage. P1b Works were closed by a record. No plan-to-closure day count is derived here, because the pre-migration plans carry no `active` date in a header |

### Task 9 — (j), family by family (C2; the deputy's DP-1 line of 2026-09-27 11:16:34 BST)

**The ruling, quoted from RL-1145.** *"DP-1: option (b) ADOPTED. The five families with a real
item since the migration merge `71f5a22` — Closure, Finding, Plan, Ruling, Ledger — are
**discharged now**, each verified in the W37-11 closure record by id, creating commit, creating
skill and `doc-id.py check` rc at that commit. The eight without one are **owed**, each against
the named event the row gives."*

**The population, re-taken at `47065da5`.** The DP-1 predicate,
`git log --diff-filter=A --name-only --format= 71f5a22..47065da5 -- docs .claude`, grouped by
id prefix, gives CR 3, FD 7, LG 5, PL 5, RL 8. It gives no WF, DC, PR or RS file. The row
families, counted by `docs/INDEX.md`'s family column at `71f5a22` and at `47065da5`: requirement
537 and 537, work 41 and 41, open question 238 and 240. The two new open-question rows are
both `OQ-1146`, once for `docs/open-questions.md` and once for its mirror in
`docs/specs/00-overview.md` §10, as every OQ id is listed. No `SL-` row exists at either tree.

**How each discharged row was checked.** `git log --diff-filter=A --format='%h %aI' -- <path>`
on `main` gives the creating commit. `git merge-base --is-ancestor` confirms that each commit is
on `main` and after `71f5a22`. Then `python3 scripts/doc-id.py check` ran at that commit, in a
detached worktree, with the commit's own tool. The creating skill is taken from the commit or
the ledger when either names it. Otherwise it is taken from the `Creates` column of
`.claude/skills/README.md` at `47065da5`, and the row says so.

| # | Family | State | Item | Creating commit (`%h %aI`) | Creating skill | `doc-id.py check` at that commit | Named event (owed rows, verbatim from the DP-1 line) |
|---|---|---|---|---|---|---|---|
| 1 | Requirement | owed | — | — | — | — | *"Requirement, Workflow, Decision, Proposal and Research at the first slice of the create-read-retire audit"* |
| 2 | Open question | **discharged**, option (a), by the deputy's DP-1 line of 2026-09-27 14:47:04 BST: *"Open question (OQ-1146, `9fe726b2`, 12:02:31): DISCHARGED, option (a)."* The event occurred: the row was raised through `spec-change` before the close, and its number was ruled MET in substance in the 11:28:23 BST ruling, item 5. *Was: "owed; the event has occurred" (at `3749db65`); amended 2026-09-27 14:52:46 BST.* | `OQ-1146`, raised and decided under RL-1145 DP-2 | `9fe726b2 2026-09-27T12:02:31+01:00` (#820) | `spec-change` by the README's `Creates` column (`OQ-` rows). The commit says it was raised by the decision-maker, *"mirrored in OQ-555's form"*, and does not name a skill | rc `0` | *"Open question at DP-2's `OQ-` row if raised through `spec-change` with a number from `next` before the close, else at the audit's first slice"*. **The derivation, as the face in PL-1144 Scope B states it** (*"`next` cannot see an unmerged draft"*; that face's label is not the register's P1b finding on `FR-12`, which carries the same label): `doc-id.py next` defaults to `--ref origin/main`, so it cannot see ids held on an unmerged branch. Re-run here at `724409bf`, the parent of `9fe726b2`: `python3 scripts/doc-id.py next --ref HEAD` printed `1144`, rc `0`. The unmerged drafts held 1144 (`PL-1144`) and 1145 (`RL-1145`), so `OQ-1146` is next + 2. #820's body: *"RL-1145 and OQ-1146 were therefore derived as next+1 and next+2."* The deputy ruled at 11:28:23 BST: *"OQ-1146's number MET in substance."* |
| 3 | Work | owed | — | — | — | — | *"Work at the minting of the charter investigation's `WK-` row"* |
| 4 | Slice | owed | — | — | — | — | *"Slice at the first `SL-` row cut in that Work's map plan"* |
| 5 | Workflow | owed | — | — | — | — | As row 1 |
| 6 | Decision | owed | — | — | — | — | As row 1 |
| 7 | Proposal | owed | — | — | — | — | As row 1 |
| 8 | Plan | discharged | `PL-1070` (W37-7 leaf plan) | `454ff41d 2026-09-18T09:57:15+01:00` | `writing-plans`, by the README's `Creates` column (`PL-`). The commit files it as a leaf plan and does not name the skill | rc `0` | — |
| 9 | Ledger | discharged | `LG-1137` (W37-7 ledger) | `4ed1f88e 2026-09-26T17:43:43+01:00` (#795) | `subagent-driven-development`, by the README's `Creates` column (`LG-`). `LG-1137:81` lists the W37-7 commit `cedbf713` for that skill's `LG-` routing | rc `0` | — |
| 10 | Ruling | **discharged, option (b)**, by the deputy's DP-1 line of 2026-09-27 14:47:04 BST: *"Ruling (RL-1075, `38033319`, 2026-09-19): DISCHARGED, option (b)."* The creating instrument is the decision-maker role file, because no RL- creating skill exists in the README's `Creates` column. That missing skill is finding FD-1156, owner the lead, event: the charter investigation's first slice. *Was: "discharged" (at `3749db65`); amended 2026-09-27 14:52:46 BST.* | `RL-1075` | `38033319 2026-09-19T14:18:28+01:00` | **No creating skill.** The README's `Creates` column names no skill for `RL-`. The commit says the rulings were *"filed by the decision-maker from its role file"*, and `RL-1075` records that it took its id from `doc-id.py next`. The creating instrument is the decision-maker's role file, not a skill | rc `0` | — |
| 11 | Research | owed | — | — | — | — | As row 1 |
| 12 | Closure | discharged | `CR-1063` (`kind: work`, the W37-6 run 2 closure/(g) record) | `1cd489c8 2026-09-17T21:54:37+01:00` (#785) | `close-workstream`, by the README's `Creates` column (`CR- kind: work`). The commit does not name the skill | rc `0` | — |
| 13 | Finding | discharged | `FD-1066` (F107's essay) | `d63f7650 2026-09-18T09:17:52+01:00` | `close-workstream`: the commit calls itself the *"checkpoint 3 close-workstream evidence record"*, and the README's `Creates` column gives that skill *"files `FD-`"* | rc `0` | — |

**Totals, amended 2026-09-27 14:52:46 BST, under the deputy's DP-1 line of 14:47:04 BST:** 6 discharged (Closure, Finding, Plan, Ledger, Ruling, Open question) and 7 owed (Work, Slice, Requirement, Workflow, Decision, Proposal, Research). Each owed row names its event verbatim. *Was: at `3749db65` the table read 5 discharged and 8 owed, with Open question owed.*

Each `doc-id.py check` run printed only
`doc-id.py check: 0 file(s) skipped (front matter present but did not parse as RFC-937's header):`
and exited `0`. No run printed a failure, so the rc is a reading at that commit and not a test
of the check.

## PRs

| # | Branch | Squash SHA on `main` | Tasks | State |
|---|---|---|---|---|
| ~~—~~ | ~~`w37-11-code`~~ | ~~—~~ | ~~1–6~~ | ~~in progress~~ — **struck 2026-09-27 by the auditor at the slice close** (pass (a) F-8): a placeholder written before the PR number was known, and a stale cell once #821 merged. The #821 row below supersedes it. |
| #821 | `w37-11-code` | `47065da50c34f0bf613f7dd972675c96d12f78ed` | 1–6 + the C4 guard | merged 2026-09-27 14:16:45 BST |
| #822 | `w37-11-docs` | `cddf9a6e32e6a780ac93ba769767bb602b054919` | 7–13 | merged 2026-09-27 15:58:42 BST |

Every Tasks 1–6 commit SHA above is a pre-squash commit of #821, reachable via `refs/pull/821/head`. The squash `47065da5`'s tree is `c3218465`'s tree (`f967495e`).

The squash of #822, `cddf9a6e`, has the tree `9ba09071`, which is the tree of #822's head `ad63a80c`. Every pre-squash SHA of #821 and #822 cited in this ledger is marked per token under "Pass (b)" below.

## Slice close — the auditor's record

**Status set `closed` by the auditor on 2026-09-27** (`document-ids.md` §1.6, SL row:
*"auditor closes: sets the `LG-` `closed`, verifies acceptance"*). The deputy ruled at
2026-09-27 15:32:22 BST that W37-11 closes in one post-merge PR, combined with plan review
14. This commit is that PR's first commit, written by the auditor from `origin/main` =
`cddf9a6e`. The lead's plan review 14 and the regenerated `docs/INDEX.md` follow it in the
same PR. W37-11 closes when that PR merges. A Slice closes on a clean audit and the lead's
merge, with no maintainer line (`CLAUDE.md` §12, §13). The Work's close is a separate act:
D7, quoted in `CR-1164` §10 W1.

**The two PRs.** Both are in the PRs table above.
- **#821**, the instrument PR (Tasks 1–6 and the C4 guard). It was squash-merged as
  `47065da5` on 2026-09-27 at 14:16:45 BST. The deputy's MERGE ACK is 2026-09-27
  14:16:29 BST, at `c3218465`.
- **#822**, the docs PR (Tasks 7–13). It was squash-merged as `cddf9a6e` on 2026-09-27 at
  15:58:42 BST. Its parent is `47065da5`, and its tree equals the tree of its head
  `ad63a80c`. The deputy's MERGE ACK is 2026-09-27 15:58:26 BST, at `ad63a80c`.
- Both ACKs are in `~/gi-pricing-plan.local/channel/to-lead.md` (local, not repo).

**Pass (a), the audit of #822 before the merge.** The pass (a) auditor proposed NOT CLEAN at
`f753a69a`, with 2 medium and 7 low findings. **The lead's verdict is CLEAN with
dispositions** (2026-09-27 15:35:39 BST, in `~/gi-pricing-plan.local/channel/to-deputy.md`).
The delta read of `f753a69a..4995f1fa` followed at 15:38:26 BST. F-10 was raised in that
entry. The deputy accepted its fix at 2026-09-27 15:39:45 BST.

**Findings, with owner and resolution:**

| Finding | What | Owner | Resolution |
|---|---|---|---|
| F-1 | The roadmap's WK-697 row still read "pending" after D7 | executor, lead | **Fixed before the squash**, at `d7f9003b` and `633c8ea9` |
| F-2 | Pre-squash SHAs in evidence cells had no pull ref | auditor | **Fixed here.** The squash body lists them by pull ref. The per-token marks are under "Pass (b)" below, because `CR-1164` is write-once |
| F-3 | Four cited SHAs are reachable from no pull ref | lead | **Accepted** (the lead, 15:35:39 BST, under the deputy's rulings of 11:37:34 and 12:02:14 BST). They are recorded under "Pass (b)" with their keeping refs |
| F-4 | `CR-1164` meets items 1, 2, 3, 5, 7 and 9 by reference to this ledger | lead | **Accepted** (15:35:39 BST) |
| F-5 | `CR-1064:414`'s starting figure is missing from the C4 records | auditor | **Fixed here**, as a dated amendment to the `FD-1152` essay, in this commit |
| F-6 | Item 17's letter, "on main before deferral" | lead | **Accepted** (15:35:39 BST) |
| F-7 | `CR-1164` §8's "40 rows" | auditor | **Fixed here**, under "The owed rows" below |
| F-8 | The stale placeholder row in the PRs table | auditor | **Fixed here.** The row is struck with a dated line, and the #822 row is added |
| F-9 | `CR-1164` §2 reports "16 passed" but names 14 nodes | auditor | **Fixed here**, under "The sixteen nodes" below |
| F-10 | The Verdict line of `CR-1164` presented a paraphrase as a quotation | lead | **Fixed before the squash** at `ad63a80c`, accepted by the deputy at 15:39:45 BST |

### Pass (b), the reachability sweep, per token

**Run by the auditor on 2026-09-27, 16:00–16:02 BST, at `origin/main` = `cddf9a6e`.**

- **Predicate, verbatim:**
  `git show cddf9a6e:<path> | grep -oE '\b[0-9a-f]{7,40}\b' | sort | uniq -c`.
- **How each token is classed:**
  - The first check is `git cat-file -t <token>`.
  - A commit that passes `git merge-base --is-ancestor <token> origin/main` is **MAIN**.
  - Otherwise, a commit is **BRANCH** if it is an ancestor of `refs/pull/N/head`, for N in
    795, 806, 814, 817, 819, 820, 821 and 822. Each head was fetched read-only into
    `FETCH_HEAD`, and no ref was created.
  - A tree or a blob is **NOTCOMMIT**.
  - Anything else is **NEITHER**.
- **The pull heads:**
  - 795 = `16e81628`, 806 = `1508cd25`, 814 = `33138af6`, 817 = `e46d3b18`;
  - 819 = `0cbdbf4e`, 820 = `e9ba2d9b`, 821 = `c3218465`, 822 = `ad63a80c`.

**Two tokens outside the four classes.** They are recorded under the lead's ruling of
2026-09-27 16:02:04 BST (the time of receipt, by `date`), which adopted the auditor's
proposed disposition.
- **`66723b39`** (this ledger, Task 1): **not an object id, a path component** (the job
  directory in a local worktree path). The predicate matches it by accident.
- **`75779691`** (this ledger, Task 5, item 5): **a disposable snapshot commit, quoted as an
  overwritten value, never pushed, and resolving nowhere. It is not evidence.** It has the
  same shape as `8edc9a2b`. Its hex happens to be all digits, so a filter that drops decimal
  CI run ids would have hidden it.

**This ledger at `cddf9a6e`** (41 distinct tokens):

| Class | Keeping ref | Tokens (spelling × count) |
|---|---|---|
| MAIN (20) | `origin/main` | `0651c1e`×5, `0651c1e265648cbd3918adfc729ad965b83b1e0b`×6, `1cd489c8`×1, `271088b0`×2, `29e7a9c`×2, `29e7a9ce`×2, `35c954c1`×1, `38033319`×2, `454ff41d`×1, `47065da5`×13, `47065da50c34f0bf613f7dd972675c96d12f78ed`×4, `4d9fe1d`×1, `4ed1f88e`×1, `71f5a22`×4, `724409bf`×1, `726ec98f`×2, `9fe726b2`×9, `9fe726b221f01c2055f818ea30ed84324cd84ab4`×3, `d63f7650`×1, `ea3704dd`×1 |
| BRANCH (13 spellings, 9 commits) | `refs/pull/821/head` | `03f61d8`×1, `03f61d83`×2, `03f61d83437a9dd4138b7e7309b22c96148f3680`×1, `0a0effb9`×3, `1eb12bab`×1, `9422776b`×2, `c3218465`×1, `cdc35fa2`×6, `cdc35fa292334d3337d5f172f26a3411ae22c6e9`×2, `ed588f8`×2, `ed588f8d`×3, `edb720eb`×1, `f7baff08`×1 |
| BRANCH (2) | `refs/pull/822/head` | `3749db65`×3, `734e12fe6d0e993eae76efe0270ae283bf804ea7`×1 |
| BRANCH (1) | `refs/pull/795/head` | `cedbf713`×1 |
| NOTCOMMIT (3) | — | blobs `6fc405017e50`×1 and `8053a06bb7b8`×1; tree `f967495e`×1 |
| not an object id (1) | — | `66723b39`×1, a path component (the job directory) |
| disposable snapshot commit (1) | none | `75779691`×1: quoted as an overwritten value, never pushed, resolves nowhere; not evidence |

Total: 20 + 16 + 3 + 1 + 1 = 41. The BRANCH count of 9 commits for #821 agrees with the
deputy's ledger sweep in the #821 ACK (BRANCH 9).

#### `CR-1164` at `cddf9a6e` (60 distinct tokens)

`CR-1164` is write-once (`document-ids.md` §1.2), so its tokens are marked here and not in
the record.

| Class | Keeping ref | Tokens (spelling × count) |
|---|---|---|
| MAIN (29) | `origin/main` | `0651c1e`×2, `29e7a9c`×3, `29e7a9ce`×3, `35c954c1`×4, `39ee30c0`×1, `3ede6495`×1, `47065da5`×25, `47eb2ba`×1, `47eb2bae`×3, `49c06ad7`×3, `4d9fe1d`×1, `4d9fe1d6`×1, `4ed1f88e`×9, `536d3cc3`×4, `5429c397`×1, `544b90c`×1, `6cad8e4d`×3, `71f5a22`×3, `71f5a220`×15, `724409bf`×4, `8b42fa78`×1, `954008f8`×1, `99355ab0`×1, `9fe726b2`×3, `a24c0a28`×1, `a8b3c39`×1, `d5501e99`×1, `e0b880e3`×1, `ff70de2f`×1 |
| BRANCH (8) | `refs/pull/822/head` | `273e3e0f`×2, `2907549b`×6, `3749db65`×9, `5ab66cc1`×1, `5c1b31ba`×10, `5c1b31ba1e6140a9b4348e4d6c1d62e8cdc3a93a`×1, `734e12fe`×1, `d8b34fd0`×3 |
| BRANCH (7) | `refs/pull/821/head` | `03f61d83`×2, `0a0effb9`×1, `9422776b`×1, `c3218465`×1, `cdc35fa2`×1, `ed588f8d`×2, `f7baff08`×1 |
| BRANCH (2) | `refs/pull/817/head` | `11e3cc2b`×1, `e3542f83`×2 |
| BRANCH (2) | `refs/pull/814/head` | `60914ee`×1, `60914ee8`×1 |
| BRANCH (1) | `refs/pull/819/head` | `0cbdbf4e`×2 |
| BRANCH (1) | `refs/pull/820/head` | `70e7d59b`×1 |
| BRANCH (1) | `refs/pull/806/head` | `414a9335`×1 |
| BRANCH (1) | `refs/pull/795/head` | `16e8162`×1 |
| NOTCOMMIT (1) | — | blob `6fc40501`×1 |
| NEITHER (4), F-3 | see below | `2307087`×2, `8edc9a2b`×1, `939a0f56`×1, `e30a082`×1 |
| not an object id (3) | — | `36281191974`×1, `36311605268`×1, `108598494214`×1: CI run and job ids |

Total: 29 + 23 + 1 + 4 + 3 = 60.

**The four F-3 SHAs, with their keeping refs at 16:01 BST.** F-3 is accepted: none of them
resolves after the row-9 cleanup.
- `8edc9a2b`: **no ref**. It is a dangling commit object in the shared store, never pushed
  and then reset (`CR-1164` face 5).
- `939a0f56`: `w37-11-plan-draft`, local and on `origin`. Its cherry-pick `70e7d59b` is on
  `refs/pull/820/head`.
- `e30a082`: `w37-6-h1-check36`, local and on `origin`.
- `2307087`: the local salvage ref `refs/salvage/2026-09-18/tool-2307087` only.

The last three lose their refs at the row-9 cleanup.

**Tokens this section adds.** They are swept with the same predicate, at this commit:
- Every token copied from `CR-1164` keeps the class and ref given in the table above.
- `cddf9a6e`, in both spellings, is MAIN.
- `ad63a80c`, `f753a69a`, `4995f1fa`, `d7f9003b` and `633c8ea9` are BRANCH, via
  `refs/pull/822/head`.
- The pull heads `1508cd25`, `33138af6` and `e9ba2d9b` are BRANCH, via their own pull refs.
  `16e81628`, `e46d3b18`, `0cbdbf4e` and `c3218465` are those heads too.
- The tree `9ba09071` is NOTCOMMIT.
- `36326607664` and `36326607691` (acceptance item 12) are not object ids. They are CI run ids.

### The owed rows: `CR-1164` §8's "40", by predicate (pass (a) F-7)

**Command.** `python3 scripts/register-owed.py <id>` was run once for each of `WK-697`, `W37`
and `W37-1` to `W37-11`. It ran on a detached copy of `3749db65` (BRANCH, via
`refs/pull/822/head`), on 2026-09-27 at about 16:03 BST, and every run exited `rc 0`. The
union of the owed lists is **39 distinct rows**, and the union of the excluded lists is **3**.
The excluded rows are headed by the tool *"Excluded as opening with a resolution marker —
verify"*: F76, F104 and FD-1147. For the `W37` run, the tool's header reads *"34 owed row(s),
3 matched but excluded as opening with a resolution marker"*.

**The counts per id, owed / excluded:**
- WK-697 6 / 0; W37 34 / 3;
- W37-1 0 / 0; W37-2 1 / 0; W37-3 0 / 0; W37-4 1 / 0; W37-5 0 / 0; W37-6 22 / 2;
- W37-7 4 / 0; W37-8 1 / 0; W37-9 0 / 0; W37-10 4 / 0; W37-11 10 / 1.

**Reconciliation.** `CR-1164` §8's "40" is the 39 owed rows plus FD-1147, which §8's table
lists. F76 and F104 are not in §8.

**F76, verified to the clause.** Its Decision cell opens *"**Resolved 2026-09-02** (W37-5b,
PRs `#593` and `#607`)"*.
- **`_ROW_FIELDS` is derived from the templates.** `row_template_fields` exists at
  `scripts/_docid.py:1271` (at `cddf9a6e`).
- **The crash paths are guarded.** `check_index_stable` wraps `build_corpus` in
  `try` / `except (_doc_index.HeaderError, ValueError)`.
- **The broken-input tests pass.** Three `tests/test_audit_docs_ids.py` tests and the whole of
  `tests/test_template_headers.py` gave **27 passed** at this tree. The three are
  `::test_check_39_corpus_build_failure_is_a_clean_fail_not_a_crash`,
  `::test_check_39_corpus_build_failure_on_a_malformed_row_date_is_also_a_clean_fail` and
  `::test_check_ids_30_39_completes_when_check_39s_corpus_is_malformed`. The second file
  includes `::test_kind_field_on_a_work_row_is_rejected`.
- **Verified**, with one limit. The cell's own *"structural observation, not filed
  separately"* still holds at `cddf9a6e`: `check_ids_30_39()` calls its ten checks with no
  exception boundary of its own. The cell says that this is *"not sized or ruled here"*. It
  is a residual observation, not an owed item, and it is recorded here so that it does not
  pass silently.

**F104, verified to the clause.** Its cell reads *"**fixed before close, this same PR (D2).**
… **CLOSED 2026-09-17.**"*.
- **The four pins exist.** They are the four `monkeypatch.setattr` lines of `_run_all_ten`,
  on `ROOT`, `nt0019_stamp_set`, `UNSTAMPABLE_EXEMPTIONS` and `migrated_tree`. They are at
  `tests/test_audit_docs_ids.py:132-135` at `cddf9a6e`, not at the `:130-133` that the cell
  cites (the line numbers have drifted by 2).
- **The named tests pass.** All 11 tests the cell names gave **11 passed**. They ran on a
  tree that carries `docs/INDEX.md` and `docs/REDIRECTS.csv`, which is the migrated state
  the defect needed.
- **The whole file passes.** `tests/test_audit_docs_ids.py` gave **118 passed**.
- **Verified.** No residual item was found.

### The sixteen nodes of `CR-1164` §2 (pass (a) F-9)

`CR-1164` §2's table names 14 nodes. The other two are the tests behind its two "also"
fixtures: `check30-ledger-prs.md` in the check 30 row, and `check35-readme-allowlist/` in the
check 35 row.
- The #822 diff and the #821 diff leave `tests/` identical: `git diff --name-only 47065da5
  cddf9a6e` names only `docs/` paths.
- So the sixteen nodes were re-run at `cddf9a6e`, and they gave **`16 passed`**.
- The command line that `CR-1164` §2 ran is not preserved. **This is a reconstruction:** these
  sixteen reproduce the count, and they are the §2 table's tests plus its "also" fixtures.

All in `tests/test_audit_docs_ids.py`:

1. `::test_check_30_reds_alone_on_an_unknown_field`
2. `::test_check_30_reds_alone_on_a_ledger_prs_field` (not named in §2)
3. `::test_check_31_reds_alone_on_a_header_filename_mismatch`
4. `::test_check_32_flags_a_citation_that_does_not_resolve`
5. `::test_check_33_reds_alone_on_a_status_outside_the_vocabulary`
6. `::test_check_33_reds_alone_on_asymmetric_supersedes`
7. `::test_check_34_reds_alone_on_a_dangling_corrected_by_entry`
8. `::test_check_34_refuses_a_body_change`
9. `::test_check_35_reds_alone_on_an_unrecognised_owner`
10. `::test_check_35_readme_allowlist_is_enforced_when_a_readme_declares_one` (not named in
    §2)
11. `::test_check_36_reds_alone_when_a_was_field_has_no_redirects_row`
12. `::test_check_36_broken_input_proof_one_undisclosed_form_reds_one_alias_form_discloses`
13. `::test_check_37_reds_alone_on_a_missing_required_section`
14. `::test_check_38_never_fails_regardless_of_scope`
15. `::test_check_39_reds_when_records_exist_but_index_is_missing`
16. `::test_check_39_reds_on_a_stale_index`

### F-5

`FD-1152` carries a dated amendment, made in this commit. It quotes `CR-1064:414`'s starting
figure verbatim and states what that figure measures.

### Acceptance, verified by the auditor (`PL-1144` Acceptance Standard)

| Item | Result | Where evidenced |
|---|---|---|
| 1 | Met. (k) is checked element by element, with second counts under DP-5 | this ledger, Task 8; `CR-1164` §4 |
| 2 | Met. (j) has 13 rows: 6 discharged, and 7 owed with named events. Each owed row is **deferred per an adopted verdict** (C2) | this ledger, Task 9; `CR-1164` §4, §5 |
| 3 | Met. (g) is re-measured, 207 at `47065da5` beside 207 at `29e7a9c`. The verdict is **deferred per an adopted verdict** (C3, DP-4 (b)), and the LIMIT is stated | this ledger, Task 7; `CR-1164` §4 |
| 4 | **Not met; deferred per an adopted verdict.** C4 is *"disproven in W37-11, fix deferred"*. The harm is guarded by #821. The starting figure was missing from the record, and it is supplied by F-5's amendment to `FD-1152` in this commit | this ledger, Task 5; `CR-1164` §5 C4; `FD-1152` |
| 5 | Met. F109 is resolved by `--record-ref`, with fail-closed exit 2 and proofs 1–3. OQ-1146 is decided | this ledger, Task 2; `CR-1164` §5 C6 |
| 6 | Met. `measured_residue` read 0/0/0 before the shrink | this ledger, Task 4; `CR-1164` §5 C5 |
| 7 | Met. The record has moved, and the reference limb is measured with DP-3's five classes | this ledger, Task 3; `CR-1164` §7 |
| 8 | Met. F110's docstrings name one population, and a behaviour test asserts it | this ledger, Task 6; `CR-1164` §5 C8 |
| 9 | Met, **with a limit**. `CR-1164` exists (`kind: work`). Items 1, 2, 3, 5, 7 and 9 are met by reference to this ledger (F-4, accepted). Its §2 count names 14 of 16 nodes (F-9, fixed above) | `CR-1164` |
| 10 | Met. The WK-697 row reads `status: closed` and cites `CR-1164` (F-1, fixed before the squash) | `docs/roadmap.md` at `cddf9a6e` |
| 11 | Met. The merge tree is `9ba09071`, the tree of both `cddf9a6e` and `ad63a80c`. On a detached copy of `cddf9a6e`, the auditor read at 16:04 BST: `audit-docs.py` rc 0, `All checks passed.`, `DISCLOSED (865, at or under the W37-11 residue ceiling)`; `doc-id.py check` rc 0; `doc-index.py --check` rc 0. The deputy's reading at `ad63a80c` agrees | `CR-1164` §11; the deputy's #822 ACK |
| 12 | Met, **with a limit**. For #821, the full two-half gate ran at `ed588f8d` and was carried to `c3218465`. For #822, the local gate ran `tests/` only (1026 passed, 1 skipped). The other halves are path-inert on a docs-only diff. At `ad63a80c`, CI python run 36326607664 ran the full suite, and docs run 36326607691 passed | the deputy's #821 and #822 ACKs |
| 13 | Met. The deputy's ACKs are 14:16:29 BST (#821) and 15:58:26 BST (#822). The slice's clean audit is this record | above |
| 14 | Met. D7 accepts the Work close by delegation: the decision at 15:25:01 BST, and the text re-issued at 15:28:48 BST | `CR-1164` §10 W1 |
| 15 | Met, as a reading; **deferred per an adopted verdict**. 207 of 207 are rowless at the DP-2 read location, and no rows are filed (the deputy's ruling of 12:06:57 BST) | this ledger, Task 4; `CR-1164` §5 C15 |
| 16 | Met. C16 is fixed in W37-11 by #821 (`47065da5`). The render tests fail at blob `6fc40501` and pass at the head | this ledger, Task 2; `CR-1164` §5 C16 |
| 17 | Met. Conditions 1–3 are met, and item 17's letter, "on main before deferral", is accepted under F-6 | `CR-1164` §5, the four conditions |

**Check 36 movement against `main`** (at `cddf9a6e`; the deputy's rulings of 2026-09-27
07:26:26 and 10:36:27 BST):
- **Pool:** 497 fatal / 6374 disclosed → 497 fatal / 6408 disclosed at this closing
  record's commit. This is measured on the committed tree, including this block's own tokens.
  Fatal is unchanged.
- **Arrived:** 34 disclosed hits, all in the alias class and all in this commit's two files. By class:
  - **Finding id, bare form, ×5:** `F76`×5, in this file, in the F-7 section and in this block.
  - **Workstream/slice id, ×29.** There are 25 in this file:
    - `W37-11`×10, from the close's own sentences and from this block;
    - `W37-1`×3, `W37-10`×2, `W37-2`×2 and `W37-9`×2, from the owed-rows command and counts,
      and from this block;
    - the six slice ids between those last two, ×1 each, from the owed-rows counts.
  - The other 4 are `W37-11`×4 in `FD-1152`'s amendment: its heading, and the quoted
    `REGRESSION` line with its gloss.
- **Classification:** these are ledger vocabulary under RL-1043 §4 / RL-1046 §A, not a
  charter defect, with no owner beyond W37-11's alias-class row.
- **Last word:** this block is the last word on its own vocabulary. No later commit
  records the recording.

**Residue carried, not fixed here:** F76's unfiled structural observation, recorded above,
is left with its row. There is nothing else.
