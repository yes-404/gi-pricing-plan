---
id: CR-1164
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-697 Work close — the closure record (W37-11, PL-1144 Task 10)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-27
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: 5c1b31ba1e6140a9b4348e4d6c1d62e8cdc3a93a
phase: P2
work: WK-697
corrected_by: []
relates: [FD-1147, FD-1149, FD-1150, FD-1151, FD-1152, FD-1153, FD-1154, FD-1155, FD-1156, FD-1157, FD-1158, FD-1159, FD-1160, FD-1161, FD-1162, FD-1163]
---

# CR-1164 — WK-697 Work close: the closure record

## Scope

**What closes.** WK-697 ("one id per governed thing") is the eleven W37 slices of the map plan
[`PL-939`](../plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md). This record is
what the maintainer's delegate reads to decide the Work close (D7, §10). It is not that
decision.

**Where the scope comes from.** It is derived from the specification and the plans, never
from what was built (`CLAUDE.md` §13):

- RFC-937 §7, acceptance items (a)–(k);
- `PL-939`'s Acceptance Standard, items 1–13 (`:60-106`), and its W37-11 slice (`:839-856`);
- `PL-1144`'s Acceptance Standard 1–17: Scope A, the carried items C1–C16 and the deputy's four
  conditions; Scope B, the day's faces; Scope C, W1–W2;
- `RL-1145`'s rulings on DP-2 to DP-5;
- the deputy's DP-1 line and his later rulings. These are cited by the heading stamp of their
  entry in the lead's local channel file `to-lead.md`, which is not in the repository.

**Authorship and verdicts.** `document-ids.md` §1.6 (`:159`) gives the `CR` family, of kinds
`work` and `phase`, to the auditor. The deputy's ruling of 2026-09-27 14:23:04 BST adopted a
split. The executor gathered Tasks 7–9's evidence into `LG-1148`, and the auditor wrote this
record from it. **The §13 verdicts below are the lead's.** The auditor proposed them at
14:55:54 BST. The lead adopted them in three dated entries of his local channel file
`to-deputy.md`: the entry headed as the lead's adoption of the §13 verdicts (its heading carries this record's first reported id, 1154, before renumbering) (**2026-09-27 14:58:11 BST**),
the id correction (**15:00:36 BST**), and *"the 29-row classification ADOPTED row by row"*
(**15:02:47 BST**). The 15:02:47 entry supersedes the others on ids: nine plus one findings,
FD-1154 to FD-1163, and this record, CR-1164. The deputy confirmed the adoptions at 14:58:58
BST and noted the final id block at 15:04:33 BST.

**Trees.** Every reading names its commit.

- **`5c1b31ba`** — this record's base: `origin/w37-11-docs` after FD-1163. Readings at the
  record's own commit are in §11.
- **`2907549b`** — `LG-1148`'s amended (j) table.
- **`3749db65`** — where the carried-item readings were first re-taken.
- **`47065da5`** — #821, the instrument PR's merge on `main`, where Tasks 7–9 were measured.
- **`29e7a9ce`** — #757's squash, which is (g)'s baseline.

Every docs check quoted here was read on a **detached copy** of a committed tree (the deputy's
rule of 13:57:50 BST).

**Conventions.** Legacy paths are described, never spelled (RL-1140). The residue-ceiling
record is cited by symbol, `_docid.W37_11_RECORD_PATH`. `PL-1144` Scope B's faces are written
as "face N (PL-1144 F-N)" (the deputy's ruling of 11:44:42 BST). Ids in quoted fixture
messages that resolve to no document are written ⟨id⟩.

## Evidence

### 1. The H-row table — RFC-937 §7 (i), map item 8

**Predicate.** The Kind cell (the last cell) of each row of RFC-937 §5.1–§5.8 (file lines
296–428 at `47065da5`), matching `/(^|[^A-Za-z])H([^A-Za-z]|$)/`. It selects **59** rows:
16 `H`, 29 `H + M`, 10 `M + H`, and one each of `H / M`, `H (optional)`,
`M + H (the two rows)` and `M + H (§2 text, markers)`. It excludes 23 `M`,
2 `M + regenerate` and 3 `—`. §5.6 has no H row.

For each path the walk read `git log -1 --format='%h %aI %s' 47065da5 -- <path>`, and tested
"post-migration" (PM) with `git merge-base --is-ancestor 71f5a22 <commit>`. The walk was run by
a read-only evidence agent. The auditor re-read the four open rows directly at `3749db65`.

| § (RFC line) | Row | Last commit | Slice | PM | Content |
|---|---|---|---|---|---|
| 5.1 (304–310) | `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/*.yml` (2/2), `.gitignore` | `49c06ad7` (#817) | W37-9 | Y | closed |
| 5.2 (318) | `docs/README.md` | `536d3cc3` (#804) | W37-10 | Y | closed |
| 5.2 (319) | `docs/INDEX.md`, `docs/REDIRECTS.csv` | `47065da5` (#821) | W37-11 | Y | closed |
| 5.2 (319) | `docs/_templates/` (13 files) | latest `35c954c1` | W37-8 | Y; 6 of 13 files untouched since before the migration (Kind `H / M`) | closed (aggregate) |
| 5.2 (319) | `document-ids.md`, and the closures, rulings and ledgers READMEs | `71f5a220` | W37-6 | = migration | migration-only |
| 5.2 (319, 338) | `docs/findings/README.md`; the legacy audit README deleted | `536d3cc3`; the deletion in `71f5a220` | W37-10 / W37-6 | Y | closed |
| 5.2 (320) | `docs/specs/*.md` (8) | latest `9fe726b2` | W37-11 | Y (0 of 8 pre-migration) | closed |
| 5.2 (322) | `docs/roadmap.md` | `47065da5` | W37-11 | Y | closed |
| 5.2 (325, 326) | `docs/workflows` (6), `docs/adrs` (7) | `71f5a220` | W37-6 | = migration | migration-only |
| 5.2 (327, 328) | `docs/rfcs` (21), `docs/plans` (127) | `4ed1f88e`, `9fe726b2` | W37-7, W37-11 | Y (0 pre-migration) | closed |
| 5.2 (330) | `PL-853` → a research `kind: audit` record | `71f5a220` | W37-6 | = migration | **OPEN** (FD-1160) |
| 5.2 (331, 332) | `docs/findings/register.md`, `docs/findings` (48) | `9fe726b2` | W37-11 | Y | closed |
| 5.2 (334) | `docs/closures/INDEX.md` and `README.md` split | `71f5a220` | W37-6 | = migration | migration-only |
| 5.2 (335, 339, 340) | `docs/process/checklists` (2), `delivery-process.md`, `delivery-process.core.json` | `536d3cc3` | W37-10 | Y | closed |
| 5.3 (349) | the legacy claude-notes stubs deleted, plus REDIRECTS rows | `71f5a220`; REDIRECTS `47065da5` | W37-6 | Y | closed |
| 5.3 (350–355) | `.claude/roles/` auditor, decision-maker, executor, lead, planner, reporter and watcher | `954008f8`, `3ede6495`, `a24c0a28`, `d5501e99`, `5429c397`, `99355ab0` | W37-8 | Y | closed |
| 5.3 (356) | `.claude/agents/README.md`, `ci-watcher.md`, `spec-reconciler.md` | `ff70de2f`, `6cad8e4d` | W37-8 | Y | closed |
| 5.3 (357) | the maintainer's authorities (no role file; `document-ids.md` §1.6, `CLAUDE.md` §12) | `71f5a220` / `49c06ad7` | W37-6 / W37-9 | Y | closed |
| 5.4 (363, 366, 370–372, 375, 376, 378) | skills README, `close-workstream`, `docs-audit`, `dev-commands`, `git-hygiene`, `repo-architecture`, `brainstorming`, `planning-with-files` | `4ed1f88e` (#795) | W37-7 | Y | closed |
| 5.4 (364) | `writing-plans` | `4ed1f88e` | W37-7 | Y | **OPEN, partial** (FD-1160) |
| 5.4 (365) | `subagent-driven-development` and `task-brief` | `4ed1f88e` | W37-7 | Y | closed in the skill; `task-brief` not read to content |
| 5.4 (367–369, 374) | `phase-review`, `adr-write`, `spec-change`, `library-spike` | `71f5a220` | W37-6 | = migration | migration-only |
| 5.4 (373) | `reporter-cycle` and its scripts (6) | `4ed1f88e` | W37-7 | Y; 3 of 6 scripts pre-migration | closed (aggregate) |
| 5.4 (377) | `python-test` / `testing-strategy` | `4d9fe1d6` / `e0b880e3` | W37-6 / before W37 | Y / **N** | python-test closed; testing-strategy **OPEN** (vendored no-op, FD-1160) |
| 5.5 (386–388) | `doc-id.py`, `doc-index.py`, `audit-docs.py` | `47065da5`, `4ed1f88e`, `35c954c1` | W37-11, W37-7, W37-8 | Y | closed |
| 5.5 (389–393) | `register-lint.py`, `register-owed.py`, `req-coverage.py`, `scope-audit.py`, `file-census.py`, `graphify-docs-extract.py` | `71f5a220` | W37-6 | = migration | migration-only |
| 5.7 (416, 418) | the notes tests deleted → `test_audit_docs_redirects.py` | tombstone test `39ee30c0` (W37-4); `test_notes_move_citations.py` `71f5a220` | — | N / = | **OPEN** (FD-1160) |
| 5.7 (417) | ten named test files | `71f5a220` (9), `4ed1f88e` (1) | W37-6 / W37-7 | Y | 9 migration-only |
| 5.7 (418) | `test_doc_id.py`, `test_doc_index.py`, `test_audit_docs_ids.py` | `47065da5`, `4ed1f88e`, `35c954c1` | mixed | Y | closed |
| 5.8 (425) | `.github/workflows/docs.yml` | `47065da5` | W37-11 | Y | closed |

**Summary.** All 59 rows were last touched at or after `71f5a22`. **Four are open on
content:**

- §5.7 `:416`/`:418`: `tests/test_notes_move_citations.py` still exists, and
  `tests/test_audit_docs_redirects.py` does not;
- §5.2 `:330`: `PL-853` is still `family: plan`, `kind: leaf`;
- §5.4 `:364`: `writing-plans` is partial;
- §5.4 `:377`: `testing-strategy` is vendored, with nothing to rewrite.

These are **FD-1160**. **Eighteen rows are closed only by `71f5a220`**, the migration commit
itself, and their content is unchecked. FD-1160's event reads them.

**`CR-1065` §2.4's seven reassigned gaps:**

- closed by their assigned slice: `CONTRIBUTING.md` and the PR template (W37-9, `49c06ad7`),
  `ci-watcher.md` (W37-8, `6cad8e4d`), `brainstorming` (W37-7, `4ed1f88e`) and
  `docs/research/README.md` (W37-10, created by `536d3cc3`);
- partial: `writing-plans` and `subagent-driven-development` (W37-7).

### 2. The ten broken-input proofs — map item 11

**The source contradiction, adopted by the lead at 14:58:11 BST.** `PL-1144` expected the ten
proofs to come from this Work's earlier closure records, and they are not there. No closure
record, ledger or plan names a `w37-4-checks` fixture or a `test_check_3x` test. The auditor
verified this with `git grep -l -E 'w37-4-checks|test_check_3[0-9]' -- docs`, which returns
no closure record. The proofs were re-run at `47065da5` in a detached worktree,
2026-09-27 14:50:32–14:52:22 BST: **16 pytest nodes, `16 passed`**.

No test runs `audit-docs.py` and reads its exit code. Each test asserts on the check's
`failures` list, and "exit 1" is inferred from `main()`'s rule. `F` below means
`tests/fixtures/docs-ids/w37-4-checks`, and `T` means `tests/test_audit_docs_ids.py`.

| Check | Fixture | Test | Failure message (ids elided as ⟨id⟩) | Verdict |
|---|---|---|---|---|
| 30 | `F/check30-unknown-field.md` (also `F/check30-ledger-prs.md`) | `T::test_check_30_reds_alone_on_an_unknown_field` | `unknown field `decision:` — not in family 'finding''s permitted set`; also `missing required field `id:` for family 'finding'` | evidenced |
| 31 | `F/check31/plans/` (a header/filename mismatch) | `T::test_check_31_reds_alone_on_a_header_filename_mismatch` | `header id ⟨id⟩ but filename pads ⟨id⟩` | evidenced |
| 32 | **none** — a file built in `tmp_path` | `T::test_check_32_flags_a_citation_that_does_not_resolve` | `⟨id⟩ does not resolve in docs/INDEX.md` — disclosed under `main()`, keyed to the sentinel path (class `h1-check32`), so exit 0 | **delivered but untested** in item 11's form |
| 33 | `F/check33-bad-status.md`, `F/check33-supersedes/adrs/` | `T::test_check_33_reds_alone_on_a_status_outside_the_vocabulary`, `…_on_asymmetric_supersedes` | `status 'nonsense' is not one of ('draft', 'active', 'closed', 'retired', 'superseded')`; `superseded_by ⟨id⟩ does not list ⟨id⟩ back in its own supersedes:` | evidenced |
| 34 | `F/check34-dangling-corrected-by/rulings/` | `T::test_check_34_reds_alone_on_a_dangling_corrected_by_entry` | `corrected_by entry ⟨id⟩ does not `corrects:` back to ⟨id⟩` (the freeze-diff clause is proven on the pure function, `T::test_check_34_refuses_a_body_change`) | evidenced |
| 35 | `F/check35-bad-owner.md` (also `F/check35-readme-allowlist/`) | `T::test_check_35_reds_alone_on_an_unrecognised_owner` | `owner 'some-random-person' is not a role filename under .claude/roles/ or 'maintainer'` | evidenced |
| 36 | **none** — files built in `tmp_path` | `T::test_check_36_reds_alone_when_a_was_field_has_no_redirects_row`, `T::test_check_36_broken_input_proof_one_undisclosed_form_reds_one_alias_form_discloses` | `` `was: ⟨id⟩` has no docs/REDIRECTS.csv row ``; a legacy note id `(legacy pre-migration form survives)` — both disclosed under `main()`, so exit 0 | **delivered but untested** in item 11's form |
| 37 | `F/check37/adrs/check37-missing-section.md` | `T::test_check_37_reds_alone_on_a_missing_required_section` | `missing required section(s) ['Consequences'] for family 'decision'` | evidenced |
| 38 | **none, by design** — warn-only; no input can fail it | `T::test_check_38_never_fails_regardless_of_scope` | none; it prints a note | **not executable as written**; the never-fails proof stands under `PL-939`'s G3 |
| 39 | the shared `tests/fixtures/docs-ids/w37-3-corpus/`, with no fixture of its own | `T::test_check_39_reds_when_records_exist_but_index_is_missing`, `T::test_check_39_reds_on_a_stale_index` | `check 39: 62 governed record(s) exist but docs/INDEX.md does not` | evidenced, on the shared corpus |

The two sources also disagree on the count. RFC-937 §5.7 (`:418`) specifies *"five broken
fixtures"*, and map item 11 says ten. **The gap is FD-1159**, deferred with the lead, with the
event the create-read-retire audit's first slice.

### 3. RFC-937 §7 (a)–(h)

`CR-1065` §1b carries the W37-6 evidence for each row, with the lead's verdicts. The re-readings
below are at `5c1b31ba`. The standing verify at `47065da5` rendered *"UNCHANGED: 1 fatal
row(s), matching the recorded set of 1 in `_docverify.EXPECTED_VERDICTS`"* (`LG-1148:866`).
So every row below reads its recorded verdict. `EXPECTED_VERDICTS` at `5c1b31ba`: `a`, `b`,
`c`, `d1`, `d5`, `e`, `f` and `h3` are `PASS`; `g` is `FAIL`; all other rows are `DISCLOSE`.

| Row | `CR-1065` §1b verdict | Re-reading (tree, predicate → result) |
|---|---|---|
| (a) one family per file | evidenced | `5c1b31ba`: `python3 scripts/doc-id.py check --classify` → total **531**, no `none` row; `git ls-files docs/ \| wc -l` → **531** |
| (b) sequence integrity | evidenced | `python3 scripts/doc-id.py check` → rc `0`, on a detached copy of each commit in this PR |
| (c) index byte-stable | evidenced | `python3 scripts/doc-index.py --check` → `OK (byte-stable)`, same |
| (d) legacy-form sweep | evidenced (standing verify + RL-1046 D5) | check 36 at `5c1b31ba`: `497 fatal, 6256 disclosed`; the verify's (d) rows read their recorded verdicts at `47065da5` |
| (e) no padded id in prose | evidenced | check 32: `All checks passed.` at every head of this PR |
| (f) no product identifier moved | evidenced (standing verify + RL-1044) | `EXPECTED_VERDICTS["f"]` = `PASS`, unchanged at `47065da5`. For information only (the executable form is `PL-960:519`'s run-own-base pair, W37-6's): `git grep -c 'VR-DST-1' <sha>`, summed → `71f5a22` 166, `0651c1e` 162, `47065da5` 167, `5c1b31ba` 167 — ordinary prose drift, as `PL-960:505-516` predicts |
| (g) script touched only headers and tokens | deferred, W37-11 | §4 below: **deferred with an owner**, the standing FAIL |
| (h) full gate green | evidenced | #821's full two-half gate at `ed588f8d`, carried to `c3218465` (the deputy's ACK of 14:16:29 BST: `3464 passed, 3 skipped, 1 xfailed`, collected 3468; fifteen `.rc` files, all 0). This PR's own gate is `PL-1144` Task 12 |

### 4. (g), (k) and (j) — Tasks 7–9, referenced from `LG-1148` at `2907549b`

The tables live in `LG-1148` and are not duplicated here.

- **(g), `LG-1148:855-925`.** Measured at `47065da5`:
  `g2 … classified-by-none=207`. The eight causes sum to 207 (103 + 29 + 28 + 15 + 12 + 11 +
  5 + 4) and equal #757's table cause by cause: **207 at `29e7a9c`**. 251 at `4d9fe1d` is
  quoted and not re-measured; the drop of 44 is #757's forward-citation check. The classifier
  commits in `29e7a9ce..47065da5` (predicate
  `git log --format='%h %s' 29e7a9ce..47065da5 -- scripts/doc-id.py scripts/_docverify.py scripts/_docid.py`)
  are `35c954c1` (#806, the header writer only) and `47065da5` (#821, the corpus boundary,
  neutral by design). Neither moves g2. g1 = 0 / 0 / 0. The condition of the lead's decision
  of 2026-09-18 00:42 BST is discharged: the re-measure shows no corpus-correctness defect.
  **The LIMIT, in the deputy's words (14:47:04 BST):** 45 files — slash-compound 29,
  stamp-no-move 4, other 12 — *"reported, not investigated"* (`LG-1148:914-917`). The reading
  shows no defect in them, and does not prove there is none.
- **(k), `LG-1148:927-943`.** `python3 scripts/doc-index.py --phase P1b; echo EXIT=$?` printed
  seven elements and `EXIT=0` at `47065da5`.
  - Element 1 is non-zero.
  - Element 2 is zero by construction: the Slice family has no member.
  - Element 3 agrees: a header-coverage zero.
  - Element 4 disagrees: 0 by `work:` header, 10/4/3/6/3 by text.
  - Element 5 disagrees: 0 against 20 opened / 16 discharged. The cause is the `P1b` against
    `1b` spelling, **FD-1155**.
  - Element 6 disagrees: `—` against 9 of 16 ids with no citing file. The cause is a
    per-directory `INDEX.md` counted as a citer.
  - Element 7 disagrees in kind: `(none)` against 4 Work closure records by filename. The
    cause is that pre-migration plans carry no `active` date.

  Each disagreement is reported with both predicates and no pick (RL-1145 DP-5 (b),
  amended). **Acceptance item 1 is met.**
- **(j), `LG-1148:945-986`, amended at `2907549b`.** The table reads **6 discharged**: Closure
  `CR-1063`, Finding `FD-1066`, Plan `PL-1070`, Ledger `LG-1137`, Ruling `RL-1075` and Open
  question `OQ-1146`. **7 are owed**: Work, Slice, Requirement, Workflow, Decision, Proposal and
  Research. This is the deputy's DP-1 line of 14:47:04 BST. Ruling is discharged under option
  (b): its creating instrument is the decision-maker role file, and the missing skill is
  **FD-1156**. Open question is discharged under option (a). Its number was ruled MET in
  substance (11:28:23 BST, item 5): `next` printed 1144 while unmerged drafts held 1144 and
  1145, so `OQ-1146` = next + 2. That mechanism is face 19, a face of **FD-1158**. Each owed row
  is **deferred with an owner**: the downstream Work's lead, with the DP-1 events verbatim.
  - Work: *"at the minting of the charter investigation's `WK-` row"*.
  - Slice: *"at the first `SL-` row cut in that Work's map plan"*.
  - Requirement, Workflow, Decision, Proposal and Research: *"at the first slice of the
    create-read-retire audit"*.

### 5. The carried items C1–C16, and the deputy's four conditions

Verdicts adopted by the lead at 14:58:11 BST.

| # | Item | Evidence | Verdict | Owner / event |
|---|---|---|---|---|
| C1 | (k) | §4 | **evidenced** | — |
| C2 | (j) | §4 | 6 discharged; **7 owed, deferred with an owner** | each owed family's downstream Work lead; the DP-1 events |
| C3 | (g), with #757 as its first item | §4; `29e7a9c` is #757's squash, merged 2026-09-18 01:45:22 BST | **deferred with an owner**; the standing FAIL, with the LIMIT | the lead; the create-read-retire audit's first slice |
| C4 | idempotence, F107 | `LG-1148:649-732`: NOT MET at `03f61d83` (17 files, +57/−51); two harmful classes | **deferred with an owner**: *"disproven in W37-11, fix deferred"*. The harm is guarded by #821 (`migrate` refuses a migrated tree with exit 2, proof 7). **FD-1152** | the lead; the create-read-retire audit's first slice |
| C5 | the census-row shrink | `LG-1148:337-360`: `measured_residue` 0/0/0 at `--ref 0651c1e --record-ref cdc35fa2`; shrink `0a0effb9`, adopted 13:26:57 BST | **evidenced** | — |
| C6 | F109, the pinned-base read | `LG-1148:119-183`: `--record-ref`, fail-closed exit 2, proofs 1–3; OQ-1146 decided | **evidenced**; F109's row set Resolved, #821 | — |
| C7 | F108, the check-35 two-clause shape | Reading at `3749db65` (§8) | **deferred with an owner** | the lead; the create-read-retire audit's first slice |
| C8 | F110, the docstrings | `LG-1148:734-774`: behaviour test, proof 6, four sites corrected | **evidenced**; F110's row set Resolved, #821 | — |
| C9 | the sweep reaching vendored files | **FD-1149**, filed at `273e3e0f` before this record. `CR-1065` §8's `task-brief` row folds in as a fixed instance (W37-7 Task 11) | **deferred with an owner** | the lead; the create-read-retire audit's first slice |
| C10 | F92's 53 files | §6 | **synthesis delivered**: the vendored skill manifests **accepted**, the rest **deferred with an owner** | the lead; the create-read-retire audit's first slice |
| C11 | RL-1046 §B's check-30 class | §8; **FD-1157** | **deferred with an owner** | the lead; the charter investigation's first slice |
| C12 | the record move and the reference limb | §7 | **evidenced**; `delivery-process.md:282` **deferred with an owner** (**FD-1154**) | the lead; the next amendment to `delivery-process.md` |
| C13 | the H-row walk and the residual | §1, §6 | **synthesis delivered**; the 4 content-open rows **deferred with an owner** (**FD-1160**) | the lead; the create-read-retire audit's first slice |
| C14 | the 57 reserved rows and the collisions | §8; **FD-1158** | **the lead's verdict** (RL-1078:278–280): **deferred with an owner** | the lead; the create-read-retire audit's first slice |
| C15 | #757's g2 per-file entries | `LG-1148:394-647`: 207 keys, 207 hits, **207 of 207 rowless** at the DP-2 read location. Filing them would flip (g); two instruments agree | **deferred with an owner** (no rows filed; the deputy's ruling of 12:06:57 BST). **The earlier "103" is #757's branch-tip figure**, taken against a record that held a 123-row g2 addition #757 then dropped. It is **superseded**, so no reader carries both | the lead; the create-read-retire audit's first slice |
| C16 | the verify-render defect | FD-1147; `LG-1148:139-148`: fails at blob `6fc40501`, passes at `47065da5` | **fixed in W37-11 by #821 (`47065da5`)** | — |

**The four conditions (the deputy, 11:16:34 BST):**

| # | Condition | Reading | Met? |
|---|---|---|---|
| 1 | A deferred row carries a register row before it is deferred | C4 → FD-1152; C7 → F108; C9 → FD-1149; face 16 → FD-1150; face 18 → FD-1151. These were on the branch at `273e3e0f`. C11 → FD-1157 and C14 → FD-1158 were filed at `5ab66cc1`. All precede this record's commit | **met** |
| 2 | Each deferred row carries its event verbatim, and its reading at the merge tree with its predicate | C7, C11 and C14 below and in §8, re-taken at this record's commit; §11 repeats them | **met**, pending §11 |
| 3 | C14 is the lead's verdict, with the 15 minted ids' disposition | §8, C14 | **met** |
| 4 | C3's baseline is re-measured, not inherited | §4: 207 at `47065da5`, beside 207 at `29e7a9c` | **met** |

**Condition 2 readings, at this record's commit** (repeated in §11):

- **C7:** check 35's summary line reads *"445 owner(s) checked in scope; 43 owner check(s)
  deferred (F92's stamp-deferred population, owner W37-11 …)"*. At `3749db65` it read 434. The
  difference of 11 is the eleven documents this PR adds. Of its failure lines, **0**
  name a non-markdown file. `git grep -l -E '^Permitted owners:'` finds 1 file, a test
  fixture. So `CR-1063`'s non-markdown firing no longer reproduces as a failure line. The
  output-shape question stays open.
- **C11:** `python3 scripts/audit-docs.py 2>&1 | grep -c '^  - check 30'` → **70**. That is
  43 skill manifests with no known template plus 27 files with no header.
- **C14:** `grep -c 'reserved (not yet materialised)' docs/INDEX.md` → **57**, first
  `FD-1080`, last `FD-1136`.

### 6. C10's 53 files, and C13's residual

**C10 (F92).** The predicate is the code's own, at `47eb2bae`. `scripts/doc-id.py`
`_front_matter_state` (`:3278`) returns `"foreign"` for a leading `---` block with no
`family:` key. `_reference_target` (`:3460`) maps that state to `_REFERENCE_FOREIGN_REASON`. A
file is one of the 53 when its census reason is that constant. Run over `47eb2bae`'s own tree
through the discovery functions `migrate()` calls (never `migrate` itself), it gives
**53 = 46 + 7**:

- `.claude/skills/<name>/SKILL.md` (46): adr-write, balance-watch, brainstorming,
  close-workstream, code-quality, contract-guard, contract-schema, create-adaptable-composable,
  dev-commands, dispatching-parallel-agents, docs-audit, executing-plans, fastapi-service,
  finishing-a-development-branch, git-hygiene, graphify, library-spike, phase-review,
  planning-with-files, python-package, python-test, receiving-code-review, repo-architecture,
  reporter-cycle, reproducing-ci-locally, requesting-code-review, secret-hygiene,
  security-audit, spec-change, subagent-driven-development, systematic-debugging,
  test-driven-development, testing-strategy, ui-ux-pro-max, using-git-worktrees,
  using-superpowers, verification-before-completion, vue-best-practices, vue-debug-guides,
  vue-frontend, vue-pinia-best-practices, vue-router-best-practices,
  vue-testing-best-practices, watcher-runtime-state, writing-plans and writing-skills.
- `.claude/agents/` (7): accessibility-tester, ci-watcher, evidence-collector, gate-runner,
  performance-engineer, postgres-pro and spec-reconciler.

**At `47065da5`,** all 53 exist at the same path, and `docs/REDIRECTS.csv` has no row for
either directory. The 7 agent manifests carry `family: reference`, merged by W37-8 in
`6cad8e4d` (#807). The 46 skill manifests do not.

**Second count, reported beside the first with no pick:** check 35 prints **43** deferred owner
checks. **Wider field:** `MigrateResult.deferred_reference_stamps` holds **64** entries at
`47eb2bae`. The other 11 have other reasons: the legacy claude-notes README and directory, the
legacy audit README, the check-35 allowlist fixture README, five READMEs under
`tests/fixtures/docs-migration/`, `.claude/CLAUDE.md` and `.claude/settings.json`.

**The lead's split (14:58:11 BST), each count by its predicate.** The predicate is
`_docid._VENDORED_SKILLS`, the hand-kept vendored enumeration (RL-990), read by symbol at
`5c1b31ba`. Intersected with the 46, it gives **28 vendored and 18 repo-local**, and every
member of the set is among the 46.

- The 28 vendored manifests are **accepted**: `CLAUDE.md` §12 keeps vendored files as upstream
  wrote them.
- The 18 repo-local manifests are **deferred with an owner**: the lead, the create-read-retire
  audit's first slice. They are adr-write, balance-watch, close-workstream, contract-guard,
  contract-schema, dev-commands, docs-audit, fastapi-service, git-hygiene, library-spike,
  phase-review, python-package, python-test, repo-architecture, reporter-cycle, spec-change,
  vue-frontend and watcher-runtime-state.

This record is the record F92 lacked. F92's register row is set accordingly.

**C13's residual.** `LG-1139`'s predicate is
`python3 scripts/audit-docs.py 2>&1 | grep "legacy audit path" | grep -c "form survives"`, with
files counted by `grep -oP '^\s*- check 36: \K[^:]+' | sort -u | wc -l`. At `3749db65` it reads
**204 hits in 68 files**; `LG-1139` read 210 / 71. By class:

- frozen governed records: 62 files, 192 hits;
- two skills (`docs-audit`, `reproducing-ci-locally`): 5;
- `delivery-process.md` and `document-ids.md`: 3;
- `docs/roadmap.md`: 3;
- `docs/INDEX.md`: 1.

The living spellings are history or definitions, left unedited by the deputy's ruling of
14:21:24 BST. The one live pointer is FD-1154's.

### 7. The DP-3 row (the record move and the reference limb), as ruled at 14:30:13 BST

The first command of acceptance item 7 derives `D` by symbol from
`_docid.LEGACY_FORM_PATTERNS['legacy audit path']`, then runs `git ls-files "$D" | wc -l`.
At `3749db65` it reads **0**. The reference limb,
`git grep -l -F "$D" -- . ':!docs/REDIRECTS.csv' | wc -l`, reads **183 = 150 + 9 + 22 + 1 + 1**:

- 150 frozen governed records, resolved by the redirect row, disclosed and not edited;
- 9 living documents;
- 22 instruments and their tests: 6 edited in #821 and 16 left in place, each read (`LG-1148:230-292`);
- `docs/INDEX.md`, generated;
- the record itself.

**The DP-3 row, in the words ruled at 14:21:24 BST and amended at 14:30:13 BST:** *"The 9
living files counted by DP-3's limb were each read. None points at the record: 4 `was:`
provenance headers, 1 historical line (`delivery-process.md:260`), 1 rule text
(`document-ids.md:107`) in `docs/process/`; 2 skills (an incident note, a legacy-source
description); `roadmap.md:384` (historical, de-linked in #821). One stale live pointer to the
moved checklists (`delivery-process.md:282`) found and NOT updated (see the check-27 /
verify-pin finding). The limb counts spellings of a retired directory, not pointers to the
record."*

The check-27 / verify-pin finding is **FD-1154**. The record's rows are written by the
discharging slice's lead (RL-1145 DP-3 amendment 5; the pointer at `document-ids.md:161`,
`734e12fe`).

### 8. The open findings of the Work — D7's "§14 open-findings list, each with a resolution"

**Generated, not recalled.** `python3 scripts/register-owed.py <id>` was run over `WK-697`,
`W37` and `W37-1` to `W37-11` at `3749db65`, a committed tree, on a detached copy. It
returns **40 distinct rows**. Each has a resolution below, adopted by the lead row by row at
15:02:47 BST. The rows filed in this PR (FD-1154 to FD-1163) are listed after them.

**Resolved in fact (13).** Each row is set "Resolved 2026-09-27" in place where its cell did
not already open with a resolution. F83, F99 and F102 already read `accept`.

| Row | Evidence, read to the clause |
|---|---|
| F70 | The row's trigger (LG- first-class, with a directory, a lint and a §1.6 owner) holds: `docs/ledgers/`; `document-ids.md:155`; checks 33/34. **Caveat:** no check proves that a frozen plan has a ledger |
| F77 | Its own tail: *"Discharged 2026-09-03: the W37-5c close is that owner acceptance"* (`CR-1005`) |
| F80, F81, F82 | Each tail: *"DISCHARGED 2026-09-02 by `544b90c` (#629)"*; the migration `71f5a220` completed |
| F83 | `accept, with instrument` (the maintainer, 2026-09-02); both instruments built. **Residual:** 3 exemption entries marked *"awaiting ratification"* (`scripts/audit-docs.py:2685-2688`), with no ratifier recorded |
| F84 | Its tail: *"DISCHARGED 2026-09-02 by `47eb2ba` (#639)"* |
| F87 | `_id_scope_documents()` reaches non-markdown files: 580 documents, 63 not `.md`, `docs/contracts/openapi/gi-pricing.yaml` among them (read at `5c1b31ba`; 570 at `3749db65`); `CR-1065:435` |
| F88 | Limb 1 by #649; limb 3 at filing; limb 2 by `71f5a220`: the phase register merged into `docs/findings/register.md` (`docs/REDIRECTS.csv:35`; 20 rows with Phase `1b`) |
| F95 | `WF` and `FD` in `_docid.py:723/731` and in `doc-id.py`'s maps; `docs/workflows/` and `docs/findings/FD-*` exist (by `71f5a220`) |
| F99, F102 | Already `accept`; final dispositions. F102's obligation is in `delivery-process.md` §11a |
| F105 | The unchanged-set branch now calls `_residue_change_block` (`scripts/_docverify.py:4562`; blame `47065da5`, #821) |

**Deferred with an owner — the lead (14).**

| Row | State | Event |
|---|---|---|
| F73 | Unowned, with no event named (an instance of F86's class) | **plan review 14** |
| F86 | None of the three limbs built | plan review 14 |
| F89 | `tests/test_audit_docs_finding_citations.py:51` still writes into the real `docs/plans/` | plan review 14 |
| F90 | The fix-before-close limb was superseded by RL-1039; option B's residue remains | plan review 14 |
| F94 | Carried as it stood by `CR-1065:437` | plan review 14 |
| F96 | No guard (no fix commit found) | plan review 14 |
| F113 | The mechanical gap is explicitly not closed | plan review 14 |
| F114 | **Limb 1 NOT MET:** `PL-939:71-73` and `PL-960:338` are still unannotated; the `PL-939` amendment was *"proposed to plan review 14"* | plan review 14 |
| F78 | The refusal exists (`doc-id.py:3061`), with no test | the create-read-retire audit's first slice |
| F100 | The docstring is still false (`doc-id.py:3319-3323`) | the create-read-retire audit's first slice |
| F101 | Limb 2 is in code. Limb 1: `row_i` has `DISCLOSE if h_rows else FAIL` (`8b42fa78`), with no broken-input exit-code proof (`CR-1064:576` routed it to W37-11) | the create-read-retire audit's first slice |
| F103 | The sentinel rows are still open: `h1-check36` is **1088**, up from 904 at filing | the create-read-retire audit's first slice |
| F106 | No g2 ceiling; the population sits in `LG-1148` (C15) | the create-read-retire audit's first slice |
| F97 | A `lead.md` clause landed (W37-8), but the row's broken-input test is unmet | the charter investigation's first slice |

**Plan review 14** is the first act after the Work close, not a gate on it (the deputy,
15:04:33 BST). It is a lead-authored `kind: review` record in its own PR after this docs PR
merges, and its acceptance line is the deputy's by delegation. The eight rows above name it
as their appointment.

**Not met at the close (1).** **F112**: *"Verified at the Work close by W37-11"*, and it is
**not met**. `git grep -n -E '^#+ .*SL-[0-9]+' -- docs` returns nothing, and
`git grep -l '^family: slice' -- docs` returns only `docs/_templates/SL.md`. The row is
**deferred with an owner** to the (j) Slice event: *"the first `SL-` row cut in that Work's
map plan"*. `LG-1139:87-116` proposed three slice ids numbered 1144, 1145 and 1147. Those
numbers are now borne by `PL-1144`, `RL-1145` and `FD-1147`, so the proposal cannot be
minted as written.

**Owned elsewhere (1).** F33: WK-671's review line (RL-860). It is listed only.

**The rows the brief names, and this PR's findings:**

| Row | Resolution |
|---|---|
| F92 | §6 (C10) |
| F107 / FD-1152 | C4 |
| F108 | C7 |
| F109, F110 | Resolved by #821 |
| FD-1147 | Resolved by #821 (C16) |
| FD-1149 | C9 |
| FD-1150 | face 16 (PL-1144 F-16): **deferred with an owner**, the lead; the create-read-retire audit's first slice, or a named item on recurrence |
| FD-1151 | face 18 (PL-1144 F-18): **deferred**, the lead; the charter investigation's first slice |
| FD-1153 | `auditor.md`'s essay path: **deferred**, the lead; the charter investigation's first slice |
| FD-1154 | the verify-pin field, with the generator restamp as its second face: **deferred**, the lead; the next amendment to `delivery-process.md` or the create-read-retire audit, whichever comes first |
| FD-1155 | (k) element 5's spelling: **deferred**, the lead; the create-read-retire audit's first slice |
| FD-1156 | the missing `RL-` skill: **deferred**, the lead; the charter investigation's first slice |
| FD-1157 | C11 |
| FD-1158 | C14, with `LG-1137:141`'s routed items 1–2 and face 19 folded in: **the lead's verdict, deferred**; the create-read-retire audit's first slice. **Counts: 15** (the deputy's count of 2026-09-19, before `RL-1078` and `FD-1079` were minted — the source) and **17** (measured at `3749db65`: of the 74 block numbers from `grep ',docs/findings/register.md,' docs/REDIRECTS.csv \| grep -oE 'FD-[0-9]{4}' \| sort -u -V`, 17 — 1063 to 1079 — are live in `docs/INDEX.md` as other documents). Neither is picked. Nothing above 1079 collides, so `RL-1078` §(vi)'s closed set holds. **The minted ids stay as minted** (`CLAUDE.md` §5; `RL-1078` §(vi)), and the D5 line (the deputy, 2026-09-26 17:06:12 BST) is cited: *"the clause governs every family … W37-11 cites this line when it disposes of the 15"* |
| FD-1159 | §2 |
| FD-1160 | §1 |
| FD-1161 | the Roles table against §1.6: **deferred**, the lead; the charter investigation's first slice |
| FD-1162 | the reporter's heading clock: **deferred**, the lead; the charter investigation's first slice |
| FD-1163 | the routed residue — (a) `CR-1065` §8's audit scope narrower than the write set, (b) check 39's false note, (c) `document-ids.md` §1.9's non-existent lint: **deferred**, the lead; the create-read-retire audit's first slice |

**Listed only.** `CR-1065` §8's `Verified`-step row (owner W37-10, a template defect).

### 9. The day's faces

"Record" names the governed record that carries the face. Where there is none, this row is
the record. Channel entries are cited by heading stamp: `to-lead.md` holds the deputy's
entries, and `to-deputy.md` holds the lead's. Both are local files, not in the repository.
Faces 1–19 are `PL-1144` Scope B (`:325-345`). The later faces follow them.

| Face | What happened | Record |
|---|---|---|
| face 1 (PL-1144 F-1) — silent exit 3 | `doc_id_verify` exited 3 on docs run 36281191974 at `414a9335` (#806). The cause was re-diagnosed and proven by a control pair: 27 fatal against 0 | `LG-1141:147-175`; the lead's entry of 03:20:23 BST, item (a); the deputy's rulings of 03:00:11, 03:01:09 and 03:21:39 BST |
| face 2 (PL-1144 F-2) — the checkout's template stamped into a ref snapshot | `_template_header_lines` read the *checkout's* `REFERENCE.md` template, so `migrate()` stamped four placeholder keys into 31 Reference files. The snapshot's check 30 rejected 27 × 4 = 108 | `LG-1141:163-172` |
| face 3 (PL-1144 F-3) — (g) alignment | (g)'s equal-line-count alignment can compare misaligned files. The four stamped lines per file were what flipped (g)'s provenance mismatch. The deputy adopted the cause at 03:21:39 BST and gave it a row here | written here; the lead's entry of 03:20:23 BST, item (c); `LG-1141:171-172` |
| face 4 (PL-1144 F-4) — the check-36 pooled disclosed reading | At #810's post-merge tree, check 36 moved from 502/6065 to 499/6066. A first ruling that one hit had been *reclassified* was withdrawn at 06:15:34 BST: three fatal hits left and one disclosed hit arrived, which the summary cannot itemise. The lead named the hit at 06:16:51 BST (`.claude/roles/auditor.md:40`, an alias token). The row wording, ruled at 06:17:27 BST, reads *"arrived, disclosed alias, unitemised by the summary"*. A related instance: at 08:35:00 BST the lead corrected a reading of #816 that quoted only the pool, when audit-docs had exited 1 with `FAILED (6)`. Since then every reading quotes the rc, the FAILED line and DISCLOSED | the class: `LG-1137:183-199`; this day's instance is written here |
| face 5 (PL-1144 F-5) — a support agent writing into a foreign tree (×2) | **(1)** On 2026-09-26 a watcher spawned from a drifted cwd wrote `.claude/scheduled_tasks.lock` into the W37-7 executor's worktree, 3 s after its gate started, and failed a census test at `16e8162`. **(2)** At 06:14:16 BST today, the evidence agent `c36-diff` cherry-picked #810's tree onto the root checkout as `8edc9a2b`. Nothing was pushed, and the root was reset at 06:16:36 BST. Rules: spawn support agents only from the root and verify with `readlink /proc/<pid>/cwd` (2026-09-26 17:16:45 BST). Evidence agents use `git worktree add --detach` under their own job dir, printing `status -sb` before and after (06:17:27 BST) | written here |
| face 6 (PL-1144 F-6) — no `HEAD.txt` | `gate-60914ee/` carried no `HEAD.txt` and no `--collect-only` output. The tree was established instead from the executor transcript's bracket | `LG-1141:476-480` |
| face 7 (PL-1144 F-7) — S-10 (×2) | **(1)** `exec-w37-8-t3` ran one unbroken turn from about 04:36 to 05:50 BST, so none of the lead's eight or more messages reached it. It was respawned, and S-10 was ruled at 05:52:14 BST. **(2)** The H executor committed `60914ee8` about a minute after the lead's F1/F2 order, and went into the gate without ending its turn. The handling was accepted at 07:08:38 BST, with no re-brief | the ruling: `LG-1141:354-356`; the breaches are written here |
| face 8 (PL-1144 F-8) — processes killed by pattern | **(1)** At about 02:20 BST (the deputy's entry says "02:05"; both times are reported), a `pkill -f` on an audit-docs path killed the lead's own wrapper and the deputy's read-only probe, both with exit 144. **(2)** Between about 03:36 and 03:42 BST, `exec-w37-8-fix2` ran `pkill -9 -f` on a gate-slot pattern and on `uv run pytest -q`. Two pytest runs then shared one database, and that result was discarded. S-9 (kill only by PID, after `readlink /proc/<pid>/cwd`) was ruled at 04:38:48 BST | the ruling: `LG-1141:350-353`; the instances are written here |
| face 9 (PL-1144 F-9) — a test that changed tracked `docs/process/` during the run | During a `tests/` run at about 07:38 BST, `git status` showed `delivery-process.md` and `delivery-process.core.json` modified, with `derived_from_digest` removed. Four tests in `tests/test_audit_docs_process_core_digest.py` write the tracked files and restore them in `finally`. A killed run leaves them dirty, and a concurrent commit would carry that. The proposed fix moves them to a `tmp_path` copy | written here; the lead's entries of 07:38:45 and 07:45:14 BST; the deputy's of 07:39:09 BST. No finding row was ruled; the proposed fix is recorded here for the test's owner |
| face 10 (PL-1144 F-10) — the ledger alias vocabulary | A ledger's own prose adds alias-class check-36 hits (#814: 12; #818: 5; #820: +72, split by class at 12:01:51 BST). The ruling of 07:26:26 BST: count them in the block, classify them as ledger vocabulary (RL-1043 §4 / RL-1046 §A), and let the block be the last word on its own vocabulary | written here; the application is `LG-1143:256-260` |
| face 11 (PL-1144 F-11) — a stamp composed before the write | Seven slips on 2026-09-27: four by the reporter and three by the lead. The lead's slips are a breach of a sufficient rule (`lead.md` item 1), not a §15 finding (11:03:53 BST). The reporter-file half is **FD-1162**. Rule: every stamp is read from `date` inside the command that writes it | written here; FD-1162 |
| face 12 (PL-1144 F-12) — a stale grep baseline | `PL-1072:341-348` expects the first grep over `CLAUDE.md` to print exactly one line at `a8b3c39`. At the executor's tree it printed none. It was routed here by the lead at 09:18:18 BST. **No deputy ruling on it was found** in the channel file | written here |
| face 13 (PL-1144 F-13) — the dead example finding id | The id of the Finding prefix with the number ninety-three, used as an illustration, resolves to nothing. In the issue templates it was replaced by `FD-894`, and it was one cause of the failed first W37-9 gate at `e3542f83` (fixed in `11e3cc2b`). It is still present at `2907549b` in `docs/process/document-ids.md:204`, RFC-937 `:206`, `PL-1072:703`, and a code comment at `scripts/audit-docs.py:654` | written here; `LG-1143:104`, `:165` |
| face 14 (PL-1144 F-14) — F-a and F-b | `LG-1143`'s two findings | `LG-1143:198`, `:210-211` |
| face 15 (PL-1144 F-15) — the stale `LG-1137` and `LG-1139` | Both ledgers read `status: active` after their slices closed. The auditor's closing PR #819 set both `closed`. It is merged as `724409bf`, and its CI head `0cbdbf4e` is tree-identical | #819, squash `724409bf` |
| face 16 (PL-1144 F-16) — a determinism test whose child aborts at interpreter shutdown | Run 36311605268, job 108598494214, exit −6 | **FD-1150** |
| face 17 (PL-1144 F-17) — a state file re-derived from itself | The watcher copied `position` from `runtime-state.json` back into `write_runtime_state.py cycle`, with source strings naming the roadmap and `PL-1072`. It stayed stale from 08:19:33 to 11:25:03 BST, across two slice closes. The interim derivation was accepted at 11:27:20 BST: slice = the W37 leaf `PL-` rows in `origin/main:docs/INDEX.md` whose last column is not `executed`; phase and work come from the roadmap; the file is rewritten only on change | written here; the lead's entry of 11:26:13 BST; the deputy's of 11:27:20 BST |
| face 18 (PL-1144 F-18) — `watcher.md` names no source for `position` | A `CLAUDE.md` §15 finding | **FD-1151** |
| face 19 (PL-1144 F-19) — `next` cannot see an unmerged draft | `doc-id.py next` defaults to `--ref origin/main`. `OQ-1146` = next + 2. The same mechanism moved this record's id twice today: 1154, then 1163, then 1164. Each time, findings were minted ahead of it, and check 31 refused the gap at 1154 (audit rc 1 on a detached copy, not pushed) | **FD-1158**, as its face |
| the empty-directory gate | Task 3's `git mv` left the emptied legacy audit directory on disk. So `docs/roadmap.md:384`'s link to it passed check 1 in that worktree, and failed in any fresh checkout (the lead's detached copy at `ed588f8d` gave rc 1). Fixed by de-linking in #821. **Rule (the deputy, 13:57:50 BST):** docs checks quoted in a request are measured on a detached copy of the committed tree | `LG-1148:821-846` |
| the wrapper-hidden verify | The `dev-commands` slot wrapper's own exit hid the inner result. The first W37-9 gate at `e3542f83` failed 2 of 7 stages, and the wrapper's exit 1 came from its `[ "$got" = "0" ] && flock …` short-circuit, so the per-command `.rc` files were read instead (the lead, 09:57:32 BST). The Task 4 pinned-base verify took about 37 minutes, which the lead relayed at 13:26:04 BST as bearing out the deputy's note on *"the wrapper's 2–3 verify-equivalents"*. **The deputy's note itself is not in either channel file**, so that clause rests on the lead's quotation | written here |
| a ruling over a classification not opened | The deputy's 14:19:28 BST ruling ordered "path pointers only" over six `docs/process/` lines, taken from DP-3 amendment 4's count of 9 living files without opening them. The lead read the lines and found no pointer to the record, and the ruling had no object. It was superseded at 14:21:24 BST. The deputy's own face: *"a ruling issued over a classification the ruler had not opened"* | written here |
| a frozen plan's Roles table against §1.6 | `PL-1144` gave Task 10's closure record to the executor. `document-ids.md` §1.6 gives `CR` of kind `work` to the auditor. §1.6 governed (14:23:04 BST) | **FD-1161** |
| a red push | `f7baff08` was committed and pushed with `audit-docs.py` rc 1: check 25 failed on a bare parenthesised finding id in a heading. `9422776b` fixed it, and from then on every commit command was gated on rc 0. It is a pre-squash commit, reachable via `refs/pull/821/head`, and is not on `main` | `LG-1148:769-772` |
| the retroactive closing-record application | The closing-record convention (a two-pass audit plus a closing PR flipping the ledger) was minted at 06:55:24 BST, after W37-7 and W37-10 had closed on the then-standing rule. #819 applied it retroactively. That is not a defect of either slice (the deputy, 11:00:45 BST) | #819 (`724409bf`) |
| one key, two meanings | `meta.verified_against_tree` is read by check 27 as its reconciliation tree and by `docs.yml:117` as the verify's pinned `--ref`. A face of RFC-777's *"a word with two scopes"* | **FD-1154** |
| the residue block unreachable on an unchanged verdict set | `render()` printed no residue-ceiling block when the verdict set was unchanged (the deputy, 11:28:23 BST, item 1) | **FD-1147**, fixed by #821 |

### 10. The sweep row, the riders, and the Work close

**The sweep row: refs kept until this record.** Verified reachable at 2026-09-27 ~14:52 BST,
by `git merge-base --is-ancestor` against the fetched refs:

- `939a0f56` (`RL-1145:25`): on `w37-11-plan-draft`; cherry-picked as `70e7d59b`, which is
  reachable via `refs/pull/820/head`.
- `0cbdbf4e` (`PL-1144`, the face 16 row): #819's CI head; `refs/pull/819/head`;
  tree-identical to `724409bf`.
- `e30a082` (`RL-1145:173-174`): on `origin/w37-6-h1-check36`.
- `2307087` (`RL-1145:173-174`): on `refs/salvage/2026-09-18/tool-2307087`.

`w37-11-plan-draft`, `w37-11-dp-rulings-draft`, `w37-6-h1-check36` and that salvage ref are
deleted at W2, each with its stamp beside it, as the deputy ruled at 11:37:34 and 12:02:14 BST.
The test database `gipricing_code` (`LG-1148:325-335`) is dropped at W2 as well. **`LG-1137`'s
F-b** is carried here unedited, as the deputy ruled at 11:33:39 BST. Its header `tree:` is a
40-hex value that resolves to no object, and its first eight digits are Task 16's commit.
Owner: the lead.

**Rider proposal for `executor.md`** (the deputy, 13:57:50 BST, item 3): *"the docs checks a
request quotes are measured on a detached copy of the committed tree (`git worktree add
--detach` or `git archive`), never on a working tree — a working tree holds what git does not
track."* This is a proposal, owner the lead, for the charter investigation's first slice. There
is no finding row for it, by the lead's ruling of 14:58:11 BST.

**W1 — D7, quoted verbatim** (the deputy, 2026-09-26 17:06:12 BST, *"Maintainer decisions by
delegation … D7 line (5) reserved"*): *"**D7 — line (5), the WK-697 Work close: reserved.** It
is decided when the closure record exists (row 7) and is read against `close-workstream`'s
checklist and §14's open-findings list, each with a resolution. Not before."*

**What the close is taken over**, named so that the D7 line can accept each one explicitly:

- **(g)**: the standing FAIL at `classified-by-none=207`, with the LIMIT (45 files: slash-compound
  29, stamp-no-move 4, other 12, *"reported, not investigated"*). Owner the lead; event the
  create-read-retire audit's first slice.
- **C4** (FD-1152), **C7** (F108), **C9** (FD-1149), **C11** (FD-1157), **C14** (FD-1158) and
  **C15**. Each is deferred with the lead and its event, as the table in §5 gives.
- **The 7 owed (j) families**, each with its DP-1 event.
- **Every finding row in §8** that is not resolved in fact: 14 register rows, F112 not met, and
  FD-1150, FD-1151, FD-1153 and FD-1154 to FD-1163.
- **Plan review 14** is the appointment the eight rows wait on, held immediately after this
  close.

**W2 — the maintainer's cleanup order of 2026-09-26 21:16:14 BST, verbatim:** *"after WK-697
landed, ask the lead to cleanup worktrees and branches pushed to remote; then plz turnoff the
VM"*. This is the lead's, after W1 and after plan review 14 (the deputy, 15:04:33 BST).

## Verdict

**Proposed by the auditor at 14:55:54 BST, and adopted by the lead** at 2026-09-27 14:58:11 BST
(the entry headed as the lead's adoption of the §13 verdicts (its heading carries this record's first reported id, 1154, before renumbering)). The ids were corrected at 15:00:36 BST, and
the 29-row classification was adopted row by row at 15:02:47 BST, all in the lead's local
channel file `to-deputy.md`. The deputy confirmed at 14:58:58 BST.

| Item | §13 verdict | Owner | Event |
|---|---|---|---|
| (a) (b) (c) (d) (e) (f) (h) | evidenced | — | — |
| (g), C3 | **deferred with an owner**, the standing FAIL with the LIMIT | the lead | the create-read-retire audit's first slice |
| (i), C13 | synthesis delivered; 4 content-open rows **deferred with an owner** (FD-1160) | the lead | the create-read-retire audit's first slice |
| (j), C2 | 6 discharged; 7 **deferred with an owner** | each downstream Work's lead | the DP-1 events |
| (k), C1 | evidenced | — | — |
| Map item 11 | 30, 31, 33, 34, 35, 37, 39 evidenced; 32, 36 **delivered but untested**; 38 not executable as written; the gap **deferred with an owner** (FD-1159) | the lead | the create-read-retire audit's first slice |
| C4 | **deferred with an owner**; disproven, harm guarded by #821 (FD-1152) | the lead | the create-read-retire audit's first slice |
| C5, C6, C8 | evidenced | — | — |
| C7 | **deferred with an owner** | the lead | the create-read-retire audit's first slice |
| C9 | **deferred with an owner** (FD-1149) | the lead | the create-read-retire audit's first slice |
| C10 | synthesis delivered; 28 vendored **accepted**; 18 **deferred with an owner** | the lead | the create-read-retire audit's first slice |
| C11 | **deferred with an owner** (FD-1157) | the lead | the charter investigation's first slice |
| C12 | evidenced; `:282` **deferred with an owner** (FD-1154) | the lead | the next amendment to `delivery-process.md` |
| C14 | the lead's verdict: **deferred with an owner** (FD-1158) | the lead | the create-read-retire audit's first slice |
| C15 | **deferred with an owner** | the lead | the create-read-retire audit's first slice |
| C16 | fixed in W37-11 by #821 (`47065da5`) | — | — |
| The open findings (§8) | 13 resolved in fact; 14 **deferred with an owner**; F112 **not met, deferred**; F33 listed | the lead | as §8 gives |

No item is left without evidence or a verdict.

**The Work-close line is reserved to the deputy by delegation (D7).** It is written here, in a
follow-up commit that is the only post-filing edit this record takes (`PL-1144` Task 13), once
this record is on the branch. It is not written by the auditor.

### 11. Readings at this record's commit

Taken on a **detached copy** of the commit that files this record. A record cannot carry its
own commit's SHA, so the SHA is reported in the PR request, and the parent here is `5c1b31ba`.
The readings were taken at 2026-09-27 15:16:48 BST.

| Reading | Command | Result |
|---|---|---|
| Docs audit | `python3 scripts/audit-docs.py; echo rc=$?` | rc `0`; `All checks passed.`; `DISCLOSED (865, at or under the W37-11 residue ceiling):` |
| Id lint | `python3 scripts/doc-id.py check; echo rc=$?` | rc `0` (contiguous through 1164) |
| Index | `python3 scripts/doc-index.py --check` | `OK (byte-stable)` |
| (a) classification | `python3 scripts/doc-id.py check --classify` | total **532** = `git ls-files docs/ \| wc -l` **532**, no `none` row |
| Next id | `python3 scripts/doc-id.py next --ref HEAD` | `1165` |
| C11 | `python3 scripts/audit-docs.py 2>&1 \| grep -c '^  - check 30'` | **70** |
| C14 | `grep -c 'reserved (not yet materialised)' docs/INDEX.md` | **57 (first `FD-1080`, last `FD-1136`)** |
| C7 | check 35's summary line; its failure lines naming a non-`.md` file | `445 owner(s) checked in scope; 43 owner check(s) deferred`; **0** |
| Check 36, against `2907549b` (497 fatal / 6248 disclosed) | the check-36 summary line, by class | **497 fatal / 6353 disclosed (+105): bare finding ids 1981 → 2011 (+30), workstream/slice ids 3986 → 4061 (+75); workstream-form finding ids 209 and scoped requirement ids 72 unchanged; fatal unchanged** |

**Check-36 movement, named by class.** Every arrival is alias-class vocabulary under
RL-1043 §4 / RL-1046 §A. Measured against `2907549b`, the workstream/slice ids arrive from
three places: FD-1163's essay and row (+8, `5c1b31ba`), this record (+64), and the register
rows set in this PR (+3). The bare finding ids arrive from this record alone (+30). The
auditor's own sweep of this record with `_docid.LEGACY_FORM_PATTERNS` finds exactly those two
classes and no other. The count of fatal hits is unchanged, and so
are the workstream-form finding ids and the closed scoped-requirement class. No legacy path is
spelled in any file this PR adds (RL-1140).
