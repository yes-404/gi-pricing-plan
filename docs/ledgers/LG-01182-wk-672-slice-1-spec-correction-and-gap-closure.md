---
id: LG-1182
family: ledger
title: WK-672 Slice 1 — spec correction and gap closure
status: closed
created: 2026-09-28
owner: executor
tree: ed123cb0fcf91e44872963bf8a8bad32b87c99bc
phase: P2
work: WK-672
plans: [PL-1177]
corrected_by: []
relates: [RL-1172]
---

# LG-1182 — WK-672 Slice 1 — spec correction and gap closure

Executed task by task from `PL-1177` (`status: active`, activated by #842), under
`RL-1172`. Cut from `origin/main` at `ed123cb0fcf91e44872963bf8a8bad32b87c99bc` on branch
`p2-d-s1`. Every task commit below is a pre-squash branch commit of this slice's one PR; the
squash SHA on `main` is recorded in the PRs table when it is known. This ledger was drafted
under a working id (number 9301, above the other tracks' placeholders) and renumbered to `LG-1182` at its mint turn, under the team's
id rule: `python3 scripts/doc-id.py next --ref origin/main` printed `1182` after
`origin/main` at `37b2596e4318092178c9b0c9fedb83610ee9fd28` (#849) was merged into the branch.

The lead adopted the executor's plan before Task 1 and ruled the PR title: until the first
`SL-` row is minted, a PR names its `WK-` work item instead (#827).

## Tasks

Each row's commit is on `p2-d-s1`. The stamp column is the commit time, Europe/London.

| Task | Commit | What was done, and the check the plan names | Stamp |
|---|---|---|---|
| 1 | `b84e0990` | `docs/roadmap.md`: the WK-672 paragraph after its migrated line (now `:637`) and the WK-675 paragraph after its migrated line (now `:684`), verbatim from the plan; neither migrated line touched. `grep -n 'score/compare' docs/roadmap.md` prints exactly two hits: `:637` inside WK-672 (heading `:623`, WK-673 at `:640`) and `:684` inside WK-675 (heading `:670`, WK-690 at `:687`). `python3 scripts/audit-docs.py` rc 0 at the base and after the edit, "All checks passed.", DISCLOSED 865. | 2026-09-28 14:03:59 BST |
| 2 | `cd296f6b` | `docs/specs/03-rating-engine.md`: a new subsection 4.9, `RegressionRun`, at `:581`, after 4.8 (`:503`) and before the rule that precedes the Interfaces section (now `:621`), verbatim from the plan. The field check is below. No `hypothesis` hit inside the new subsection. `audit-docs.py` rc 0, "All checks passed.", DISCLOSED 865. | 2026-09-28 14:05:11 BST |
| 3 | `dfc30fa3` | `backend/tests/test_errors.py`: `test_golden_quote_mismatch_is_registered` with `req("FR-260")`, and `RATING_ERROR_CODES` added to the import. **Red first** (quoted below). Then `backend/src/app/errors.py`: `"GOLDEN_QUOTE_MISMATCH"` after `"TRACE_NOT_PENDING"` with the plan's comment. **Green:** `uv run pytest backend/tests/test_errors.py -v` rc 0, 10 passed; `uv run mypy` rc 0 (196 source files); `ruff check` on both files rc 0. The diff to `errors.py` adds exactly one quoted code, `"GOLDEN_QUOTE_MISMATCH"`; `PROPERTY_ASSERTION_FAILED` is not added. | 2026-09-28 14:07:15 BST |
| 4 | `675e8532` | `backend/tests/test_contracts.py`: the `regression-suite` label is now `"authored-only until WK-672 builds it — 03 §4.7 and §4.9"` (`:91`; `:89` before the plan's two comment lines); the key is still in `ONE_SIDED_SLUGS` (an import of the module evaluates `'regression-suite' in ONE_SIDED_SLUGS` to `True`). `uv run pytest backend/tests/test_contracts.py -q`: "136 passed, 2 skipped" at `dfc30fa3` before the edit, and "136 passed, 2 skipped" after it — unchanged. | 2026-09-28 14:08:17 BST |

### Task 2's field check — the predicate

The property names inside the new subsection's JSON block, extracted with
`grep -o '"[a-z_]*":'`, against the keys at `^ *"<name>": {` in
`docs/contracts/schemas/regression-suite.schema.json` lines 63-99 minus the schema keywords
`type`, `items`, `properties`, `required` and `description`; both sides `sort -u`. `diff` of
the two sets is empty. Each side holds **16 unique names**: the 9 top-level names
(`suite_slug`, `rating_version_ref`, `bundle_hash`, `job_id`, `started_at`, `finished_at`,
`overall`, `golden_results`, `property_results`), plus `golden_results[]`'s `name`, `status`,
`expected_minor`, `actual_minor`, `difference_minor`, plus `property_results[]`'s
`cases_run` and `counterexample` (`name` and `status` are shared with `golden_results[]`, so
they count once). A count taken per level instead gives different totals; this one is the
union.

### Task 3's red run, verbatim

`uv run pytest backend/tests/test_errors.py -k golden_quote_mismatch -v`, before the
registration: rc 1, 1 failed, 9 deselected, at `backend/tests/test_errors.py:162` (the
membership line):

```text
E       AssertionError: assert 'GOLDEN_QUOTE_MISMATCH' in frozenset({'BATCH_ABORTED', 'BATCH_ABORT_THRESHOLD_ABOVE_SETTING', 'BUNDLE_COMPILE_FAILED', 'EXPRESSION_INVALID_VOCABULARY', 'EXPRESSION_NON_DETERMINISTIC', 'EXPRESSION_SCALE_OVERFLOW', ...})
```

An `AssertionError` on the membership line, not an `ImportError` or a `ValueError`: the
predicted failure.

## Deviations from the plan's text

- **Task 3, the import.** The plan writes the extended `app.errors` import as one line. It is
  over the line length, so `ruff`'s isort rule wraps it in parentheses, one name per line. The
  names and their order are the plan's. Adopted by the lead.
- **§4.9 example made valid JSON and schema-valid, on the deputy's instruction (14:34).**
  Made in the mint-turn commit, after review of #853 had started, so it is named here as a
  delta from the plan's Task 2 text rather than folded into Task 2's row. The plan's example
  was not valid JSON: `"rating_version_ref": {"…artifact-ref…"}` is an object holding a bare
  string. Three fields changed, each to a value its schema accepts:
  - `rating_version_ref` → `"rating_version:motor-gb@27"`. `regression-suite.schema.json`
    refers it to `common/artifact-ref.schema.json`, which is a **string** with a
    `{type}:{slug}@{version}` pattern, not an object. The value is the one `03` already uses
    in its scoring examples.
  - `bundle_hash` → `sha256:` plus 64 lowercase hex characters (the schema's
    `^sha256:[a-f0-9]{64}$`; the plan's `"sha256:…"` fails it).
  - `job_id` → a well-formed UUID (the schema's `format: uuid`; the plan's `"…uuid…"` fails it).

  Three checks, built differently, on the committed spec (commands in the job directory, run
  with `env -C` on this worktree; each extracts the ```json fence between the `### 4.9`
  heading and the Interfaces heading):
  1. JSON parse, `python3 v49.py <tree> parse` (`json.loads` on the fence): rc 0,
     "parsed: 9 top-level keys". Control: the same command on the spec at `b954ca2d` (the
     plan's text) exits 1 with `JSONDecodeError: Expecting ':' delimiter: line 3 column 42`.
  2. A standard-library per-field check against `RegressionRun`, `python3 v49.py <tree> fields`
     — required keys at all three levels, no key outside `properties`, `bundle_hash` against
     the schema's own pattern and `rating_version_ref` against `artifact-ref`'s, both **read
     from the schema files**, `job_id` through `uuid.UUID`, the two times through
     `datetime.fromisoformat`, the `overall` and `status` enums, the money fields and
     `difference_minor` as integers, `cases_run` as an integer at least 0: rc 0,
     "per-field: 0 violations". Control: with `bundle_hash` reverted to `"sha256:…"` and the
     ref's version set to `@0`, it exits 1 naming both fields.
  3. `jsonschema` 4.26.0 against the schema itself, from an isolated environment that adds
     nothing to the repository or `uv.lock`:
     `uv run --no-project --with jsonschema --with referencing --with rfc3339-validator python v49js.py <tree>`,
     validating the block against `{"$ref": ".../regression-suite.schema.json#/$defs/RegressionRun"}`
     with every `common/*.json` schema registered by its `$id` and the format checker on:
     rc 0, "0 error(s) against RegressionRun". Control: with `bundle_hash` reverted and
     `job_id` set to `"not-a-uuid"`, it exits 1 with exactly those two errors.

  Task 2's field-set comparison, re-run with the same predicate after the change: `diff`
  empty, 16 = 16.
- **Not changed: `ruff format --check`** flags `backend/src/app/errors.py` at `:420` and
  `:455`, lines this slice does not touch. The same check on `origin/main`'s copy of the file
  gives the same result, and formatting is not a stage of the gate. Left alone; adopted by
  the lead.

## The gate

Full two-half gate on HEAD `675e853218fc2bec9e4441e7322947275b13aab6` (tree porcelain empty
at start and end), in slot `/tmp/slots/gate-1`, taken on the first `flock -n -E 99` attempt.
The Python half is `dev-commands`' gate body and slot wrapper copied verbatim, with two
deviations:

1. `WT=p2_d_s1` in place of `WT=$(basename "$PWD")`. Every job-dir tree on this team ends in
   `/tree`, so the verbatim line gives every member the same test database. The lead
   approved `gipricing_p2_d_s1`; it was created from the `gipricing` template inside the
   `gi-pricing-postgres-1` container (`createdb` rc 0) and migrated with
   `GIP_DATABASE_URL=…/gipricing_p2_d_s1 uv run alembic upgrade head` (rc 0), and the gate
   exported `GIP_TEST_DATABASE_URL` to it. It is dropped by name when this slice merges.
2. The `logs:` line is printed on a pass as well as on a fail.

The DB stack was checked before the run (`docker ps`: `gi-pricing-postgres-1`,
`gi-pricing-redis-1` and `gi-pricing-minio-1` all "healthy"). Load stayed at or below 4.7.
The driver process's `readlink /proc/<pid>/cwd` was this slice's worktree. The run started
2026-09-28 14:09:28 BST and finished 14:26:11 BST.

| Half | Command | Exit | Detail |
|---|---|---|---|
| Python | `uv run ruff check .` | 0 | |
| Python | `uv run mypy` | 0 | 196 source files |
| Python | `uv run lint-imports` | 0 | 3 kept, 0 broken |
| Python | `python3 scripts/audit-docs.py` | 0 | "All checks passed."; DISCLOSED 865 |
| Python | `uv run python scripts/req-coverage.py` | 0 | |
| Python | `uv run python scripts/generate-contracts.py --check` | 0 | 28 generated contracts match |
| Python | `uv run pytest -q` | 0 | 3465 passed, 3 skipped, 1 xfailed |
| Frontend | `pnpm --dir frontend install --frozen-lockfile` | 0 | from a clean `node_modules` |
| Frontend | `pnpm --dir frontend generate:api` | 0 | |
| Frontend | `pnpm --dir frontend lint` | 0 | |
| Frontend | `pnpm --dir frontend type-check` | 0 | |
| Frontend | `pnpm --dir frontend test` | 0 | 97 files, 602 tests, no `Errors` line |
| Frontend | `pnpm --dir frontend build` | 0 | a chunk-size warning only |

The `pytest` total reconciles: 3465 + 3 + 1 = 3469, and
`uv run pytest --collect-only -q` at the same HEAD prints "3469 tests collected", including
`backend/tests/test_errors.py::test_golden_quote_mismatch_is_registered`.

`git diff --stat origin/main...675e8532` at the gate: `backend/src/app/errors.py`,
`backend/tests/test_contracts.py`, `backend/tests/test_errors.py`, `docs/roadmap.md`,
`docs/specs/03-rating-engine.md` (5 files, +67/−2). This ledger and `docs/INDEX.md` are
added by the final commit, which touches `docs/` only.

## PRs

| PR | Branch | Title | Squash SHA on `main` |
|---|---|---|---|
| #853 | `p2-d-s1` | feat(rating): WK-672 Slice 1 — spec correction and gap closure, LG-1182 | `50e5271ca1dd21064a31bdc230f0672b5b3d1d27`, squash, merged 2026-09-28 15:01:35 BST |

*(Corrected 2026-09-28 by the auditor, at slice close: this row read "#853 (draft)", the PR's working title, and "(on merge)". The PR was retitled to Conventional Commits form before the merge, and the squash SHA is now known.)*

## Slice close — the auditor's record

**Status set `closed` by the auditor on 2026-09-28** (`document-ids.md` §1.6, SL row:
*"auditor closes: sets the `LG-` `closed`, verifies acceptance"*). This is the W37
closing-record convention, a two-pass audit plus one post-merge, docs-only PR authored by the
auditor, set by the deputy on 2026-09-27 at 06:55:24 BST. This PR touches exactly two paths:
this file and `docs/INDEX.md`. It takes no new id. A Slice closes on a clean audit and the
lead's merge, with no maintainer line (`CLAUDE.md` §13).

**The work PR, #853.** It was squash-merged onto `main` as `50e5271c` (the PRs table) at
2026-09-28 15:01:35 BST (`gh pr view 853 --json mergedAt` → `2026-09-28T14:01:35Z`). Its
parent on `main` is `37b2596e`. Its PR head was `b289f519`, reachable via
`refs/pull/853/head`. The squash's tree equals the head's tree, `beaeb42c`, so the slice's
content is on `main` byte for byte. The deputy's MERGE-ACK for #853 at `b289f519` is stamped
2026-09-28 15:00:48 BST, in the lead's local channel file `to-lead.md` (local, not repo). The
lead adopted the audit as **CLEAN, passes (a) and (b)** on 2026-09-28, before the merge.

**Evidence is cited by the squash, `50e5271c`.** Every other SHA in this file, and in the
audit record quoted below (`b84e0990`, `cd296f6b`, `dfc30fa3`, `675e8532`, `b954ca2d`, and
the PR head `b289f519`), is a **pre-squash branch commit of #853**, reachable via
`refs/pull/853/head`, not on `main`.

**The audit record, passes (a) and (b), verbatim** as the auditor wrote it before the merge
(the notes and the dated correction under them included). It is fenced because it is a
quotation, and a quotation keeps the finding ids it was written with:

```text
WK-672 Slice 1, PR #853. Audit by auditor-a, 2026-09-28. The range is origin/main...p2-d-s1, from merge base ed123cb0 to head b954ca2d. The lead adopted the verdict CLEAN on 2026-09-28.

PASS (a), item by item:
- Item 5, change set. `git diff --stat` shows exactly 7 files, +193/−3: errors.py, test_contracts.py, test_errors.py, INDEX.md, LG-09301…, roadmap.md and 03-rating-engine.md. There is nothing else. There are 5 commits, one per task, and the last commit touches docs/ only.
- Item 1, roadmap. The `score/compare` hits are at :637, inside WK-672 (lines 623–640), and at :684, inside WK-675 (lines 670–687). Both paragraphs are byte-identical to PL-1177's text. The migrated lines are untouched: the diff has 4 added lines and 0 removed.
- Item 2, §4.9.
  - `### 4.9` is at :581, between §4.8 (:503) and §5 Interfaces (:621).
  - Its text is identical to the plan's block, except for one trailing blank line.
  - Independent field check: I parsed the schema's `RegressionRun` definition as JSON and compared it with the keys in the §4.9 block. Doc and schema each have 16 names, and the diff is empty in both directions.
  - "hypothesis" does not appear in §4.9.
- Item 3, Task 3 test-first, reproduced by me. The plan's Step 6 commits the test and the code together (dfc30fa3), so there is no separate red commit. I ran the new test against the base errors.py (from ed123cb0).
  - With the base file: `FAILED … E AssertionError: assert 'GOLDEN_QUOTE_MISMATCH' in frozenset({...})` at test_errors.py:162, which is the membership line. This is identical to the ledger's quote.
  - At the head: `PASSED`.
  - The errors.py diff adds exactly one quoted code, "GOLDEN_QUOTE_MISMATCH". PROPERTY_ASSERTION_FAILED appears only in the comment the plan prescribes.
- Item 4, test_contracts.
  - :91 now reads "authored-only until WK-672 builds it — 03 §4.7 and §4.9", and the key is kept.
  - The result is "136 passed, 2 skipped" on both the branch file and the base file, so the count is unchanged.
- Item 6, gate. I did not re-run the full gate. Spot check:
  - `pytest --collect-only` gives 3469 at b954ca2d and 3468 at ed123cb0, so one new test. This matches the ledger's 3465 + 3 + 1 = 3469.
  - The ledger records all 13 commands at rc 0 on 675e8532. The final commit b954ca2d is docs-only, so that gate tree stands for the code.
  - The ledger discloses the `WT=p2_d_s1` deviation, and the lead approved it.
- Item 7, docs checks at b954ca2d:
  - audit-docs: rc 1, FAILED (1), "check 31: gap in the full allocation between 1177 and 9301" (the working id). DISCLOSED (865, at or under the W37-11 residue ceiling).
  - doc-id check: the same gap.
  - doc-index --check: rc 0.
  - register-lint: OK.
- Ledger.
  - All 4 task SHAs and the gate HEAD 675e8532… are ancestors of b954ca2d.
  - The stamps match the commit times, Europe/London: 14:03:59, 14:05:11, 14:07:15 and 14:08:17.
  - The base is ed123cb0, which is correct.
- Test database. The two pytest runs used gipricing_auditor_a_s1, created from the template. It was dropped afterwards: dropdb rc 0, and the count is 0.

PASS (b), against RL-1172. §6 limits Slice 1 to four items: the roadmap text with DP1's two sentences, §4.9, the registration, and the :89 label. The slice delivers exactly those four. Nothing from Slices 2–4 leaked in: there is no raiser, no HTTP status choice, no model-schema shape and no generator. §4.9 names the model-schema move in Slice 3 (item 3c) and the bundle_hash approval read (item 4).

NOTES, none blocking:
1. A merge onto main at 092582a4 conflicts only in docs/INDEX.md. The mint turn resolves it.
2. §4.9's example is not valid JSON at `"rating_version_ref": {"…artifact-ref…"}`. This is the plan's own text, copied exactly. Carried to Slice 3 (the lead's ruling).
3. RL-1172's auditor obligation (F60 and F59 set Resolved, F44 limb (1) re-pointed to Slice 3) was not yet done at main. Routed to auditor-b's register pass.

CORRECTION (the lead, relaying the deputy's ruling of 2026-09-28): note 2 is NOT carried to Slice 3. executor-s1 fixes §4.9's JSON example in the LG mint's renumber commit, re-parsed rc 0. The closing record records it as "found by the audit, fixed before merge", citing that commit's SHA. It is not a carried item.
```

**The §4.9 example: found by the audit (pass a, note 2); fixed before merge in `b289f519`.**
The deputy ruled that it is fixed in this slice, not carried to Slice 3. The fix is part of
`50e5271c`. It was verified by three hands, each with a broken-input control:

- **The executor:** three checks, named in this file's *Deviations* section. They are a
  parse, a per-field check, and `jsonschema` 4.26.0 in an isolated environment. The
  controls fail as predicted.
- **The lead:** a re-parse at `b289f519`, rc 0, with a control at rc 1 (the lead's message to
  the auditor, 2026-09-28).
- **The auditor, independently:**
  - At `b289f519`, a per-field check: all 7 required keys; `rating_version_ref` against
    `common/artifact-ref`'s pattern; `bundle_hash` against `^sha256:[a-f0-9]{64}$`;
    `job_id` a UUID; `overall` in its enum; `started_at` RFC 3339.
  - At the merge tree `50e5271c`, a re-run of `jsonschema` 4.26.0. The block was extracted
    from `docs/specs/03-rating-engine.md` and is byte-identical to `b289f519`'s (`cmp`).
    `json.load` gives rc 0. The schemas came from `git archive 50e5271c docs/contracts/schemas`
    into the auditor's job directory. The run used
    `uv run --no-project --with jsonschema --with referencing --with rfc3339-validator`,
    with every `$id` registered and the format checker on. It printed
    "0 error(s) against RegressionRun", rc 0.
  - The control, with `bundle_hash` set to `'sha256:xyz'` and `job_id` to `'not-a-uuid'`,
    gives rc 1 with exactly those two errors.
  - No file in the repository or in `uv.lock` was touched.

**Pass (b) after the merge, the reachability sweep, run by the auditor at 2026-09-28 15:05 BST.**
- **Predicate, verbatim:** `git show 81e061fb:docs/ledgers/LG-01182-wk-672-slice-1-spec-correction-and-gap-closure.md | grep -oE '\b[0-9a-f]{7,40}\b' | sort -u`.
  Each token is classified in order:
  1. `git cat-file -t <t>` not `commit` gives NOTCOMMIT;
  2. `git merge-base --is-ancestor <t> 81e061fb` exit 0 gives MAIN;
  3. the same check against the #853 head, fetched read-only with
     `git fetch origin pull/853/head`, exit 0 gives BRANCH;
  4. otherwise NEITHER.
- **MAIN ×2:** `ed123cb0…` (the slice's base and its `tree:` field) and `37b2596e…` (the
  squash's parent).
- **BRANCH ×6 tokens (5 commits):** `b84e0990`, `cd296f6b`, `dfc30fa3`, `675e8532` (twice:
  short and full), `b954ca2d`.
- **NEITHER ×0. NOTCOMMIT ×0.**
- The SHAs this section adds are the squash `50e5271c` and its parent `37b2596e`, both on
  `main`, and `b289f519`, the PR head, a branch commit. The squash's tree is `beaeb42c`.

**Items routed elsewhere, not owed by this slice:**
- RL-1172's own obligation on the auditor is routed to the second auditor's register pass
  (the lead's ruling). It covers three register rows: the two spec-defect rows set
  Resolved, and the approval-evidence row's limb (1) re-pointed to Slice 3.
- The merge-tree `INDEX.md` conflict (pass a, note 1) was resolved at the mint turn and
  needs nothing further.

**Acceptance, `PL-1177` items 1–8:**
- Items 1 to 7 are verified by pass (a) above.
- Item 8, the deputy's merge acknowledgement, is the MERGE-ACK at 2026-09-28 15:00:48 BST.
- Nothing is owed. The slice is closed.
