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

## PRs

| # | Branch | Squash SHA on `main` | Tasks | State |
|---|---|---|---|---|
| — | `w37-11-code` | — | 1–6 | in progress |
