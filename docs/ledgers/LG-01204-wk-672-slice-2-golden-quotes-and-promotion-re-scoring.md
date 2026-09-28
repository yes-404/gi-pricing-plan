---
id: LG-1204
family: ledger
title: WK-672 Slice 2 — Golden Quotes and promotion re-scoring
status: closed
created: 2026-09-28
owner: executor
tree: ffba67539ba5f0c5cd04aa72a0c4270a517c0562
phase: P2
work: WK-672
plans: [PL-1189]
corrected_by: []
relates: [RL-1172, PL-930, LG-1182]
---

# LG-1204 — WK-672 Slice 2 — Golden Quotes and promotion re-scoring

Executed task by task from `PL-1189` (`status: active` on `main` since #862, squash
`ffba67539ba5f0c5cd04aa72a0c4270a517c0562`), under `RL-1172` and the deputy's decisions
DP-S2-1 to DP-S2-6 by delegation, quoted whole in the plan. Branch `p2-d-s2`, fast-forwarded
to `origin/main` at `ffba6753` before Task 1 and merged with `origin/main` at
`e6a9ca71a0bef3da41720d20f3f20db73f6a1d80` (#864) before Task 5 (`git merge`, never a rebase).
Every commit below is a pre-squash branch commit of this slice's one PR. This ledger was
drafted under a working id and renumbered to `LG-1204` at its mint turn, under the team's id
rule: `python3 scripts/doc-id.py next --ref origin/main` printed `1204` after `origin/main` at
`4fb07b6cb17cacb2f6f578f264a36a455143c45f` (#865) was merged into the branch (`c416f3b2`, a
docs-only merge: five files, all under `docs/`).

The test database is `gipricing_tree-s2` (the worktree's unique leaf), created from the
`gipricing` template and migrated; `GIP_TEST_DATABASE_URL` pointed at it for every run. It is
dropped by name when this slice merges.

## Tasks

The stamp column is the commit time, Europe/London.

| Task | Commit | What was done, and the check the plan names | Stamp |
|---|---|---|---|
| 1 | `39fcc475` | `03`: the Golden Quote glossary row, FR-260's dated amendment, §4.3's `evidence.golden_quotes` (checked and not-checked forms) with its write-once invariant, §4.7's structured five-class union, §4.9's citation moved to `regression-run.schema.json`, two §5.1 rows and the submit row, §5.2's `evaluate_golden_quotes`. `06`: `APPROVAL_BY_EVIDENCE_AUTHOR` in the error list and a dated sentence beside FR-353, written against FR-353 as #861 left it (#861 was on `main`, `3f7bddda`). No requirement id minted. `audit-docs.py` rc 1, FAILED (1): check 39 only (INDEX, deferred to the final commit by the team's rule 5); DISCLOSED 851. | 2026-09-28 16:56:57 BST |
| 2 | `80d5ee86` | `model_schema.regression` (the shapes the plan's Task 2 lists, plus `Sha256Hash`); `RatingVersionEvidence.golden_quotes`; the authored/generated contract split; `regression-suite` into `COMPARED_SLUGS`, `regression-run` into `ONE_SIDED_SLUGS`. Red first: `ModuleNotFoundError: No module named 'model_schema.regression'`, collection only. Green: `test_regression.py` 21 passed; model-schema 395 passed; `test_contracts.py` 140 passed, 2 skipped; `generate-contracts.py --check` rc 0. Broken-input proof: the authored `GoldenQuoteTolerance.money_minor` typed `"string"` fails `test_generated_and_authored_agree_on_scalar_types[regression-suite]` ("model ['integer'], contract ['string']"); restored, 140 passed. Amended twice before any push, for an E501 in a comment. | 2026-09-28 17:12:48 BST |
| 3 | `e7abae94` | `score._score_context_sync`, a pure move out of `_score_batch_row`; `rating/testing.evaluate_golden_quotes`. Red first: `ModuleNotFoundError: No module named 'pricing_core.rating.testing'`. pricing-core 822 passed, 1 xfailed at the base (detached `ffba6753`) and after the extraction. `test_rating_score.py` five times after the extraction: rc 0, 0, 0, 0, 0 (24 passed each, no `PyGILState` line). `test_testing.py` 6 passed; `lint-imports` 3 kept, 0 broken. | 2026-09-28 17:18:04 BST |
| 4 | `0dc12cbf` | `regression_suites` / `regression_suite_versions`, migration `fb705749c5d9` on `d3b955a63d6a` (upgrade, downgrade −1, upgrade: rc 0 each); the service, the two routes, `RegressionSuiteVersionCreate` (the POST body, declared in `model-schema`). `test_regression_suites.py` 8 passed; backend 1247 passed, 2 skipped. The race red is below. | 2026-09-28 17:32:02 BST |
| — | `bcb1a97a` | Merge of `origin/main` `e6a9ca71` (#864, #855, #833). One conflict, `06`'s error-code list: #864's `APPROVAL_SUBJECT_NOT_IN_REVIEW` beside this slice's `APPROVAL_BY_EVIDENCE_AUTHOR`; both kept. The FR-353 row is byte-identical at `ffba6753` and `e6a9ca71`. One alembic head after the merge, `fb705749c5d9`. | 2026-09-28 18:01:17 BST |
| 5 | `e9f51fa0` | Step 0, quoted: `git log --grep '(#861)' -1 origin/main` printed `3f7bddda fix(governance): the approver may be neither the submitter nor the author (FR-353) (#861)`; `git log --grep '(#864)' -1 origin/main` printed `e6a9ca71 fix(governance): only a version in its reviewable state can be put to a decision (FR-351) (#864)`. The submit gate, the pin, the delta and its author walk, `golden_quote_delta_authors`, `EvidenceAuthorResolver` and the 403 in `decide` after #861's author check, the route's `_fetch_bundle` loader. `test_rating_versions.py` 36 passed (22 golden); backend 1312 passed, 2 skipped. The reds are below. | 2026-09-28 18:21:27 BST |
| 6 | `983c5144` | The ledger under its working id, and `docs/INDEX.md`. Gate run on this tree (below, "The first gate"). Pushed; draft PR #867. | 2026-09-28 18:24:25 BST |
| G3 | `37debb3d` | Audit finding G3 (auditor-a's slice audit of #867): the NFR-499 no-logging test drives the POST route under `caplog` and `capfd` and requires a non-empty capture. Positive control below. | 2026-09-28 18:53:08 BST |
| — | `c416f3b2` | Merge of `origin/main` `4fb07b6c` (#865): docs only. | 2026-09-28 18:56:31 BST |
| mint | `c94c62e2` | The renumber `LG-WORKING` → `LG-1204` (file, `id:`, in-text), `docs/INDEX.md`, and this ledger's G1/G2/G3 record. | 2026-09-28 19:04:24 BST |
| CI fix | `6cc5078c` | The G3 test made order-independent after #867's CI failed it (below, "The CI failure on `c94c62e2`"). | 2026-09-28 19:29:53 BST |
| — | this commit | This ledger's record of `6cc5078c`. Ledger only. | 2026-09-28 |

### The reds

- **Task 4, the one-suite-per-algorithm race.** With `uq_regression_suites_algorithm` dropped
  in the test database, `test_two_concurrent_suites_for_one_algorithm_give_one_201_and_one_409`
  failed: `assert ['int', 'int'] == ['PlatformError', 'int']` — both writers created a suite.
  Both writers are held at a two-party `asyncio.Barrier` past every read (the `_registry` and
  `_next_version` seams), so any check-then-insert is passed by both. Constraint restored: 8
  passed.
- **Task 5**, each rule disabled on a backup-restored copy, then restored (`cmp` identical):
  - the mismatch refusal disabled: `test_golden_mismatch_refuses_submission_and_leaves_the_version_draft` —
    `Failed: DID NOT RAISE PlatformError`;
  - acceptance item 8, the delta stubbed to an empty `GoldenQuoteDelta` (a gate that pins but
    builds no delta): the value-change test fails first on `assert None == 'rating_version:minimal-rv@1'`
    (its baseline-ref assert, before the changes entry); the tolerance-only test fails on
    `ValueError: not enough values to unpack (expected 1, got 0)` — the missing changes entry;
  - the evidence-author refusal disabled: `test_golden_evidence_author_cannot_approve` —
    `Failed: DID NOT RAISE PlatformError`;
  - audit finding F5, the route wired to `_compiled_for`: `test_golden_route_refuses_rather_than_scoring_the_slots_last_known_good` —
    `assert 200 == 500` (submitted to review on the slot's bundle);
  - audit finding F3, the walk replaced by **last-touch attribution** (one step per quote,
    authored by the latest version that touched it, note-only edits included):
    `At index 0 diff: {'author': '01a0e909-f126-78ee-915e-ec91214054b1', 'version': 3, 'changed_fields': ['tolerance']} != {'version': 2, 'changed_fields': ['tolerance'], 'author': '01a0e909-f120-7bb4-abed-59d167943369'}`.
    The actual author `…f126…` is Y (created after X; the ids are time-ordered UUIDv7), at
    version 3, Y's note-only edit; the expected `…f120…` is X. Restored: 1 passed, no new
    commit (the restore was byte-identical).

### The audit's reds (auditor-a on `983c5144`; items G2 and G3)

auditor-a found the design and governance clean, and asked for these reds. Each was run on a
backup-restored copy (or, for a constraint, on the test database), restored (`cmp`
identical, or the constraint re-added), and green again after.

- **G3 positive control.** A temporary line in `create_suite_version`,
  `get_logger("app.regression_suites").info("created %s", content.model_dump_json())`, turns
  the route-level test red: `assert 'ZZ9 9ZZ' not in 'INFO     ap...1 Created"\n'`, with
  `'ZZ9 9ZZ' is contained here: ostcode":"ZZ9 9ZZ"}…`. Restored: `test_regression_suites.py`
  8 passed. **A claim dropped before the commit:** a first draft re-attached caplog's handler
  after `create_app`, on the claim that `configure_logging` detaches it; a second control (no
  re-attachment, the log line present) was also red, so the claim was false, and the
  re-attachment and its docstring were removed. What keeps the test from passing on an empty
  capture is its `assert caplog.records`.
- **N1**, the `TypeError` guard removed: `test_golden_evidence_author_decide_without_a_resolver_is_a_type_error` —
  `E AssertionError` (the narrowing assert then fires; under `python -O` the call on `None`
  raises a `TypeError` whose message fails the test's `match`).
- **N3**, `uq_regression_suite_versions_version` dropped: `test_two_concurrent_versions_of_one_suite_collide_as_409_not_500` —
  `assert ['int', 'int'] == ['PlatformError', 'int']` (both writers created version 2).
- **The missing creation event**, a fallback author returned instead of the refusal:
  `test_golden_a_suite_version_with_no_creation_event_refuses_submit` — `Failed: DID NOT RAISE PlatformError`.
- **N2**, an absent `golden_quotes` raising instead of an empty set:
  `test_golden_evidence_author_set_is_empty_without_golden_quotes` — `ValueError: no golden_quotes`.
- **The write 403**, `rating:write` weakened to `rating:read` in both the route dependency and
  the service check (either alone still refuses): `test_a_principal_without_rating_write_is_refused_creation` —
  `assert 201 == 403`.
- **The read 403**, the route's `rating:read` dependency and the service check both removed:
  `test_a_principal_without_rating_read_is_refused_the_read` — `assert 200 == 403`.
- **The reference 422**, a policy entry simulated for `regression_suite`:
  `test_a_regression_suite_reference_cannot_be_put_through_approval` —
  `assert 'ARTIFACT_TYPE_NOT_RESOLVABLE' == 'VALIDATION_FAILED'`. Still refused, by the
  resolver fan-out: the second layer, shown.

After the restores: `test_regression_suites.py` and `test_rating_versions.py` 44 passed, the
reference test 1 passed, `git status --short` empty.

### The CI failure on `c94c62e2`, and its fix

#867's CI (run 36462673125) failed `test_every_version_has_one_creation_event_and_no_context_is_logged`
with `AssertionError: nothing was captured, so the no-context check below proves nothing`
(1 failed, 3607 passed); in isolation it passed.

- **Reproduced:** `uv run pytest -p no:randomly backend/tests/test_migration_dataset_owner.py backend/tests/test_regression_suites.py`
  gives the same assertion line.
- **Cause, measured:** that module runs alembic in-process, which reaches
  `backend/migrations/env.py:25`, `fileConfig(config.config_file_name)`. `fileConfig`'s
  `disable_existing_loggers` defaults to true: a script importing the app's modules and then
  calling `fileConfig('alembic.ini')` printed 0 of the `app.*` loggers disabled before and
  22 of 22 after. A disabled logger drops its records before any handler sees them.
  `configure_logging`, the claim dropped at G3, is not the cause either.
- **Fix (`6cc5078c`, test only):** the test re-enables disabled loggers for itself
  (`monkeypatch`), requires a sentinel logged on `app.request`
  (`backend/src/app/observability/middleware.py:24`, the route's logger) to be captured, and
  requires the route's own `app.request` records, before the no-context asserts.
- **Proof:** after the breaking module, 16 passed; both migration modules and the file, 25
  passed; the file alone, 8 passed; the full backend suite in default order, 1312 passed, 2
  skipped (rc 0). The positive control (the temporary content log) run after the breaking
  module is red: `assert 'ZZ9 9ZZ' not in 'INFO     ap...1 Created"\n'`; restored, `cmp`
  identical. The four docs checks on a detached copy of `6cc5078c`: audit-docs rc 0, "All
  checks passed.", DISCLOSED 851; `doc-id.py check`, `doc-index.py --check` and
  `register-lint.py` rc 0.
- **The production question, answered by grep at `6cc5078c`:** no non-test code runs alembic
  in-process. `backend/src` has no alembic import, no `command.upgrade` and no `fileConfig`
  (`grep -rn 'command\.upgrade\|alembic\.config\|alembic import\|fileConfig\|from alembic\|import alembic' backend/src`
  prints nothing), and `fileConfig` appears only in `backend/migrations/env.py` and this
  slice's test. Every other invocation is its own `alembic` CLI process: `.github/workflows/python.yml:294`
  (`uv run alembic upgrade head`), `scripts/demo.py:217` (a subprocess), and the documented
  commands in `scripts/bench-compiled-for.py:35` and `scripts/bench-score-batch.py:27`. The
  logger disabling is therefore test-suite-only: after any in-process alembic test, every
  `app.*` record is dropped for the rest of the session. The root fix,
  `fileConfig(..., disable_existing_loggers=False)` in `env.py`, is outside this slice and was
  reported to the lead.

## Deviations from the plan's text

1. **`regression_suite` joins `ARTIFACT_TYPES`** (the lead's ruling, option (A); the deputy
   endorsed it). `refs.py:21` lacked the type, and its parser says "extending the set is a
   spec change", while `suite_ref` and `baseline_suite_ref` are `ArtifactRef`s. It is a
   reference only: no approval policy and no creation action. An approval request naming one
   is refused with 422 `VALIDATION_FAILED`, "No approval policy for this artifact type"
   (`test_a_regression_suite_reference_cannot_be_put_through_approval`); had a policy entry
   ever been added, the route's resolver fan-out has no resolver for it and would still
   refuse, so two layers hold. Only `common/artifact-ref.schema.json` carries the type
   pattern among the authored files; `approval-request.schema.json`'s `artifact_type` enum is
   the approvable list and was deliberately not changed. `03` §4.7 carries the dated
   reference-only line.
2. **Paths beyond the plan's Files blocks**, which acceptance item 11 is read as extended by:
   `packages/model-schema/src/model_schema/refs.py`; the regenerated
   `docs/contracts/schemas/generated/artifact-ref.schema.json`,
   `docs/contracts/schemas/generated/peril-structure.schema.json` and
   `docs/contracts/openapi/generated.json`; `docs/contracts/schemas/common/artifact-ref.schema.json`;
   `docs/contracts/schemas/rating-version.schema.json` (for `evidence.golden_quotes`);
   `scripts/audit-docs.py` (two F83 register rows, which check 35 required for the two new
   contract files) and `tests/test_audit_docs_ids.py` (its count pin, 63 to 65);
   `backend/tests/test_api_approvals.py` (the refusal test); `backend/tests/test_approvals.py`
   (item 4 below).
3. **Signatures.** `create_suite_version` and `load_suite_version` return the pair
   (`RegressionSuiteRow`, `RegressionSuiteVersionRow`), and `current_suite_for_algorithm`
   the same pair or `None`, where the plan named the version row alone: the routes need the
   registry's slug, and Task 5's gate reads the suite and walks its versions
   (`suite_versions`, added for that).
4. **N1 against Task 5 Step 4's "unchanged".** A `rating_version` `decide` without a resolver
   now raises `TypeError` before any decision row, so the 21 direct `decide` calls in
   `test_rating_versions.py` (5, the real resolver) and `test_approvals.py` (16, a no-author
   stub) each gained the one keyword; no assertion changed. The lead ACCEPTED this as the
   correct reading of "unchanged": behaviour, not the call signature.
5. **S-8 slips, twice.** Task 4's service and routes, and Task 5's gate, were written before
   their tests, so the plan's "import failure first" red was not run for either. The reds that
   carry each rule were shown afterwards, as above. Recorded as slips, not as a method.
6. **The F5 route test** asserts that a metadata-storage failure surfaces as the platform's
   500 `INTERNAL_ERROR` and leaves the version `draft`; the plan names no status for it.

## Acceptance mapping

Each item of `PL-1189`'s Acceptance Standard, and where it is met.

| Item | Met by |
|---|---|
| 1 (a) | `grep -n 'regression-suites' docs/specs/03-rating-engine.md` prints the two §5.1 rows **and** one §4.7 prose line (`(\`POST /api/v1/regression-suites/{slug}/versions\`, §5.1), bound to one Rating Algorithm by`); the item's intent, the two rows, is met. |
| 1 (b)–(f) | (b) one line, inside the `testing.py` block; (c) no hit; (d) FR-260's dated amendment names the pinned suite hash and the delta; (e) §4.3 shows `golden_quotes`; (f) §4.9 cites `regression-run.schema.json`. No requirement id minted. |
| 2 | Task 2; `grep -rn 'class GoldenQuote\b\|class RegressionSuite\b' backend packages` prints only `model_schema/regression.py`. |
| 3 | `test_regression.py`, 21 passed: each kind round-trips, free text refused, unknown kind refused, `premium_bounded` with neither bound refused, duplicate names refused, the hash stable under key order and changed by an `expected` or `tolerance` edit. |
| 4 | `test_testing.py`, 6 passed, including the sync no-event-loop call; `lint-imports` 3 kept. |
| 5 | `test_regression_suites.py`, 8 passed: 403 without `rating:write`, 403 without `rating:read`, one creation event per version with the creator as actor, no context value in any payload or log line, 409 for a second suite of an algorithm, 409 for an algorithm change, and both races 201/409 (the algorithm race shown red without its constraint). |
| 6 | The golden tests in `test_rating_versions.py`: mismatch refused (red shown), match to `review` with the three pins, a foreign bundle refused, F5 refused (red shown), no bundle refused, no suite recorded as `not_checked`. |
| 7 | `test_golden_a_later_suite_version_does_not_change_what_was_pinned`. |
| 8 | The value-change and tolerance-only tests (red shown), added/removed, context-by-hash, no baseline, later-approved baseline, other algorithm ignored, the cosmetic edit (red shown against last-touch), two authored steps, missing creation event → 403 `APPROVAL_AUTHOR_UNRESOLVED`; the delta through `GET /api/v1/rating-versions/{id}` to an approver. |
| 8a | The bypass test (#864's `APPROVAL_SUBJECT_NOT_IN_REVIEW` on a mismatching draft); the evidence author refused 403 with no decision row (red shown), a non-author not refused; `TypeError` without a resolver and no decision row; an empty author set without `golden_quotes`. |
| 9 | The gate, below. |
| 10 | The docs checks, below. |
| 11 | The change set, below, read with deviation 2. |
| 12 | The deputy's acknowledgement and the auditor's record, after the PR. |

## The gate

### The first gate, on `983c5144` (the working-id tree)

The Python half is `dev-commands`' gate body and slot wrapper copied verbatim, with two
additions: the `logs:` line is printed on a pass too, and `git rev-parse HEAD` is written to
`HEAD.txt` in the log directory. `WT=$(basename "$PWD")` gives `tree-s2`, this worktree's
unique leaf, which is the test database's name. The DB stack was checked first (`docker ps`:
postgres, redis and minio "healthy"); load stayed near 1.1–1.3. The run started 18:24:47 BST
and finished 18:41:20 BST in slot `/tmp/slots/gate-1`, first attempt; `HEAD.txt` read
`983c5144c3684823e6ccbb86a8c9ba684010158d`. The process found by `pgrep -f '[b]ash .*gate.sh'`
was the harness's outer shell (cwd the root checkout); the body ran under `env -C` this
worktree, which `HEAD.txt` confirms.

| Half | Command | Exit | Detail |
|---|---|---|---|
| Python | `uv run ruff check .` | 0 | |
| Python | `uv run mypy` | 0 | |
| Python | `uv run lint-imports` | 0 | 3 kept, 0 broken |
| Python | `python3 scripts/audit-docs.py` | 1 | FAILED (1): check 31, `id: LG-WORKING` is not `<PREFIX>-<n>` shaped; DISCLOSED 851 |
| Python | `uv run python scripts/req-coverage.py` | 0 | |
| Python | `uv run python scripts/generate-contracts.py --check` | 0 | 29 generated contracts match |
| Python | `uv run pytest -q` | 1 | 11 failed, 3597 passed, 3 skipped, 1 xfailed; the 11 are real-tree tests asserting audit-docs is clean (the check-31 cause) |
| Frontend | `pnpm --dir frontend install --frozen-lockfile` | 0 | |
| Frontend | `pnpm --dir frontend generate:api` | 0 | |
| Frontend | `pnpm --dir frontend lint` | 0 | |
| Frontend | `pnpm --dir frontend type-check` | 0 | |
| Frontend | `pnpm --dir frontend test` | 0 | 97 files, 602 tests |
| Frontend | `pnpm --dir frontend build` | 0 | |

`uv run pytest --collect-only -q`: 3612 on `983c5144` (= 3597 + 11 + 3 + 1) against 3550 on
`main` at `e6a9ca71`. `test_rating_score.py` five times on `983c5144`: rc 0, 0, 0, 0, 0 (24
passed each, no `PyGILState` line). The lead accepted this gate, the working id being its
only cause.

### Item 9 on the minted tree

After the mint, the tree differs from `983c5144` by `37debb3d` (one test file), the docs-only
merge `c416f3b2`, and this commit (the renumber, `docs/INDEX.md`, this ledger). CI runs the
full gate on the pushed head; locally, on the minted tree before this commit's own ledger
lines (Europe/London, 2026-09-28, ending 19:03:31 BST):

| Command | Exit | Detail |
|---|---|---|
| `python3 scripts/audit-docs.py` | 0 | "All checks passed."; DISCLOSED 851 |
| the four test files this slice's approval and suite code touches: `test_regression_suites.py`, `test_rating_versions.py`, `test_api_approvals.py`, `test_approvals.py` | 0 | 160 passed |
| the 11 real-tree tests the first gate failed on, by node id | 0 | 11 passed |
| `uv run pytest tests/test_audit_docs_ids.py -q` | 0 | 118 passed |
| `packages/pricing-core/tests/test_rating_score.py`, five times | 0, 0, 0, 0, 0 | 24 passed each, no `PyGILState` line |

### Item 10: the docs checks

On the working tree of this commit (the four checks are re-run on a detached copy of the
committed tree before the push, and quoted in the report and the PR):
`audit-docs.py` rc 0, "All checks passed.", DISCLOSED 851 (main's at `4fb07b6c` is 851);
`doc-id.py check` rc 0; `doc-index.py --check` rc 0; `register-lint.py` rc 0.

### Item 11: the change set

`git diff --stat origin/main...HEAD` with this commit: **38 files changed, 5215 insertions(+), 165 deletions(-)**. The paths are the plan's
Files blocks, this ledger and `docs/INDEX.md`, read with deviation 2.

## PRs

| PR | Branch | Title | Squash SHA on `main` |
|---|---|---|---|
| #867 | `p2-d-s2` | feat(rating): WK-672 Slice 2 — Golden Quotes and promotion re-scoring, PL-1189, LG-1204 | `109cd065987c399b9cdbecc2fcb6628843dfb79a`, squash, merged 2026-09-28 19:49:23 BST |

*(Corrected 2026-09-28 by the auditor, at slice close: this cell read "(on merge)".)*

## Provenance notes

- `ffba6753`'s subject says (draft); `PL-1189` was `status: active` at merge, per its Status
  block (Activated 2026-09-28 16:21:33 BST).

## Slice close — the auditor's record

**Status set `closed` by the auditor on 2026-09-28** (`document-ids.md` §1.6, SL row:
*"auditor closes: sets the `LG-` `closed`, verifies acceptance"*), under the W37
closing-record convention, a two-pass slice audit plus one post-merge, docs-only PR by the
auditor, set by the deputy on 2026-09-27. This PR touches exactly two paths, this file and
`docs/INDEX.md`, and takes no new id. A Slice closes on a clean audit and the lead's merge,
with no maintainer line (`CLAUDE.md` §13).

**The work PR, #867.** It was squash-merged onto `main` as `109cd065` (the PRs table), at
2026-09-28 19:49:23 BST (`gh pr view 867 --json mergedAt` → `2026-09-28T18:49:23Z`). Its
parent on `main` is `4fb07b6c`. Its PR head was `a33f6c2e`, reachable via
`refs/pull/867/head`. The squash tree equals the head tree, `573c4a90`, so the slice's content
is on `main` byte for byte. The deputy's MERGE-ACK for #867 at `a33f6c2e` is stamped
2026-09-28 19:49:05 BST, in the lead's local channel file `to-lead.md` (local, not repo). The
lead adopted the audit as CLEAN, and adopted the G1–G3 and G3-fix confirmations, before the
merge.

**Evidence is cited by the squash, `109cd065`.** The other commit SHAs in this file, and in
the audit record below, are **pre-squash branch commits of #867**, reachable via
`refs/pull/867/head` and not on `main`: `39fcc475`, `80d5ee86`, `e7abae94`, `0dc12cbf`,
`bcb1a97a`, `e9f51fa0`, `983c5144`, `37debb3d`, `c416f3b2`, `c94c62e2`, `6cc5078c`, and the
PR head `a33f6c2e`.

**The audit record, verbatim.** These are auditor-a's passes (a) and (b) on `983c5144`, the
G1–G3 confirmation on `c94c62e2`, and the G3-fix confirmation in full-suite order on
`6cc5078c`. They are fenced because they are a quotation, and a quotation keeps the finding
ids it was written with:

```text
WK-672 Slice 2 slice audit: #867 (executor-s2), by auditor-a, 2026-09-28.
Range: origin/main...p2-d-s2, base e6a9ca71, head 983c5144. There are 7 commits, one of them a merge, touching 38 files (+5097/−165).
Governing documents: PL-1189 at main, and the ledger LG-WORKING on the branch.
Environment: my own detached copy (…/auditor-a/s2), run with env -C. The database was gipricing_auditor_a_s2, created from the template and brought to alembic head fb705749c5d9. It has been dropped; the count is 0.

PROPOSED VERDICT: CLEAN on the design and the governance rules. Merge readiness depends on G1, and G2 should be closed before the ACK. G3 is low.

PASS (a): each acceptance item, with where it is met
1. Spec, 03 and 06: the ledger's Task 1 row. This includes FR-260's dated amendment, §4.3 checked and not_checked with the write-once invariant, the §4.7 union, §4.9 → regression-run.schema.json, §5.1 rows, §5.2, and 06 APPROVAL_BY_EVIDENCE_AUTHOR beside FR-353.
2. Shapes and contracts: model_schema/regression.py. regression-suite is compared and regression-run is one-sided. test_contracts is inside my 327 passed.
3. test_regression.py: 21 tests, inside my run.
4. test_testing.py: evaluate_golden_quotes. The _score_context_sync move was checked with the same count before and after, plus 5× test_rating_score (Task 3, rc 0×5).
5. test_regression_suites.py covers:
   - 403 without rating:write and 403 without rating:read;
   - exactly one creation event per version, with the creator as actor;
   - 409 for a second suite for the same algorithm;
   - 409 for an algorithm change;
   - both races (201/409).
   The registry is uq_regression_suites on (workspace_id, slug) and uq_regression_suites_algorithm on (workspace_id, algorithm_slug), both at db/models.py:2055-2057. Versions are unique on (suite_id, version) at :2088. An IntegrityError maps to 409 at regression_suites.py:120 and :147.
6. The submit gate (rating_versions.py _golden_quote_gate):
   - a mismatch returns 409 GOLDEN_QUOTE_MISMATCH;
   - no bundle returns 409;
   - load_compiled=None raises TypeError;
   - the loaded bundle's content_hash must equal row.bundle's, else 409 BUNDLE_COMPILE_FAILED;
   - the pin is bundle_hash=bundle.content_hash, the SCORED bundle;
   - with no algorithm ref or no suite, it records not_checked with the reason.
   The route passes `_fetch_bundle` and never `_compiled_for` (api/models.py). The F5 red is shown in the ledger.
7. test_golden_a_later_suite_version_does_not_change_what_was_pinned.
8. The delta (_golden_quote_delta):
   - The baseline is the latest `rating_version.approved` event among the approved, live and retired RVs of the same algorithm, and it uses the suite version that baseline PINNED.
   - Steps are computed version against previous version over (baseline, current], on expected, tolerance and context (by hash). Note-only edits produce no step.
   - The author comes from the regression_suite.created event. A missing event gives 403 APPROVAL_AUTHOR_UNRESOLVED.
   - The ledger shows F3's last-touch red, and the value and tolerance reds.
8a.
   - The generic-route bypass is refused through #864.
   - `decide` raises TypeError when a rating_version request has no resolver. This happens straight after _load, before any write (N1).
   - APPROVAL_BY_EVIDENCE_AUTHOR (403) comes after #861's author check and before the permission check.
   - golden_quote_delta_authors returns an empty set when the evidence is absent or not_checked, and a load or parse error propagates (N2).
9, 10, 11: see G1.
12: after the PR.
The deviations are disclosed in the ledger:
- regression_suite is in ARTIFACT_TYPES as a reference only. Submitting it through approval returns 422, tested by test_a_regression_suite_reference_cannot_be_put_through_approval.
- The extra paths include check 35's F83 rows in audit-docs.py and a count pin.
- 21 direct decide calls gained the keyword.
- The S-8 slips are disclosed.

MY RUNS
- The seven touched test files (test_regression_suites, test_rating_versions, test_approvals, test_api_approvals, test_regression, test_testing, test_contracts): 327 passed, 2 skipped.
- M1: the scored-bundle hash check was disabled and the pin changed to row.bundle's hash. Result: 1 failed, test_golden_a_loaded_bundle_that_is_not_this_versions_is_refused ("'GOLDEN_QUOTE_MISMATCH' == 'BUNDLE…'"). The foreign bundle then failed its golden quotes instead of being refused as foreign.
- M2: context was dropped from the delta's compared fields. Result: 1 failed, test_golden_delta_records_a_context_change_by_hash_only ("not enough values to unpack").
- The code was restored after each mutation, and the status is clean.

PASS (b): adversarial
- Can a rating:write holder weaken a golden quote without it being seen?
  - Every expected, tolerance or context change, and every add or remove, shows in the next submission's delta, with every step's author.
  - A rename appears as a removal plus an addition.
  - A suite edit after submission cannot change what was checked, because the content hash is pinned.
  - The suite cannot be deleted, and its algorithm cannot change.
  - The one residue is escaping to a new algorithm slug. That RV gets an explicit not_checked, which is visible, and DP-S3-1 closes it in S3.
- Can they approve their own suite change? No:
  - APPROVAL_BY_EVIDENCE_AUTHOR covers every step author;
  - the TypeError guard stops a skipped resolver;
  - decide has one caller, which passes the resolver.
- Can a stale suite or bundle pass? A stale or foreign bundle is refused on the hash comparison. The suite checked is the current one, and its hash is pinned. An RV in review cannot be recompiled.
- Can the delta mis-attribute a change? The authors come from creation events, per version, one step per version. A later cosmetic edit cannot mask an earlier change (F3 red). The baseline uses the pinned suite, not the suite at approval time.
- Can evidence be overwritten? golden_quotes is written only by the gate, and only on a submit. A resubmission after the version returns to draft rewrites it as a new submission, which is its own gate run, not an edit. No other code path writes it.

FINDINGS
G1 (process, before the ACK): the ledger's "The gate" section reads "Pending — recorded on the final tree". Items 9 (the full two-half gate and the 5× determinism on the final tree), 10 (the four docs checks) and 11 (the change set) are therefore not yet evidenced. The 5× determinism run is recorded only at Task 3. All of this must be recorded on the minted final tree before the ACK.
G2 (LOW-MED, the S-8 residue): the ledger demonstrates reds only for these: the algorithm race, the mismatch refusal, the delta, the evidence-author refusal, F5, and F3. These rules have tests but no demonstrated red:
  - N1 (TypeError);
  - N3 (the version race gives 409);
  - the missing creation event (403 APPROVAL_AUTHOR_UNRESOLVED);
  - the route 403s;
  - the regression_suite reference 422;
  - N2 (an empty set).
  My M1 and M2 add reds for the foreign-bundle refusal and the context change. Ask executor-s2 to add a disable-and-run red to the ledger for at least N1, N3 and the missing-event 403.
G3 (LOW): the NFR-499 log assertion (`_SECRET_POSTCODE not in caplog.text`) holds vacuously today. The suite service and the audit module emit no log line, and the test is service-level, so it never drives the POST route. It guards only against a future service-level log line. Add a positive control (log the context deliberately and see red), and drive the POST route under caplog.
Observation: M1 turned red through GOLDEN_QUOTE_MISMATCH, not through a pin assertion. The scored bundle's hash and row.bundle's hash are equal by construction once the mismatch is refused, so no test could tell them apart. That is acceptable.

---
G1–G3 CONFIRMATION on the delta 983c5144..c94c62e2 (LG-1204). By auditor-a, 2026-09-28.
The delta has three commits: 37debb3d (the G3 test), c416f3b2 (a merge of #865, docs only) and c94c62e2 (the mint and the ledger).
- G1: evidenced in LG-1204, with one limit.
  - Item 9. The first full gate ran on 983c5144. Its only failures came from the working id: check 31, and 11 real-tree tests. On the minted tree the targeted runs all pass:
    - audit-docs rc 0;
    - four test files, 160 passed;
    - the 11 real-tree tests, 11 passed;
    - test_audit_docs_ids, 118 passed;
    - test_rating_score.py ×5, rc 0 each, 24 passed, no PyGILState line.
  - The limit: the full two-half gate on the minted head rests on CI.
  - Item 10. I re-ran the four docs checks myself on a detached copy at c94c62e2: audit-docs rc 0, "All checks passed.", DISCLOSED 851; doc-id check rc 0; doc-index --check rc 0; register-lint rc 0.
  - Item 11. 38 files, the same set as before, read with deviation 2.
- G2: closed. The ledger quotes a red for each of N1, N3, the missing creation event, N2, the write 403, the read 403 and the reference 422. Each was restored afterwards: 44 plus 1 passed, and the status is empty.
  - My own re-run of N1, with the TypeError raise removed: 1 failed, test_golden_evidence_author_decide_without_a_resolver_is_a_type_error (AssertionError). Restored: green.
  - My DB was gipricing_auditor_a_s2b, now dropped.
- G3: closed. The test now drives POST /api/v1/regression-suites/{slug}/versions twice, under caplog and capfd. It asserts `caplog.records` is non-empty, and that the secret is in neither the log text nor stdout/stderr.
  - Positive control, quoted in the ledger: a temporary log line carrying the content turns it red.
  - The executor's earlier claim, that configure_logging detaches caplog, was tested, found false and dropped.
  - Green in my run.
VERDICT: CLEAN. It is merge-ready once CI's full gate on c94c62e2 is green.

---
G3 FIX CONFIRMATION at 6cc5078c (the head is now a33f6c2e, a ledger-only commit on it). Auditor-a, 2026-09-28. The run used my database, gipricing_auditor_a_g3, and the g3 copy, both now released.
- The cause: backend/migrations/env.py's fileConfig (disable_existing_loggers=True) disables the app.* loggers when a test runs alembic in-process.
- The fix: for this test only, re-enable the disabled loggers, then require a sentinel on app.request and the route's own request records to be captured before asserting anything.
- Breaking order (test_migration_dataset_owner.py, then test_regression_suites.py):
  - with the fix: 16 passed;
  - with a deliberate leak in create_suite_version: RED, `assert 'ZZ9 9ZZ' not in …`, and the secret shows in the capture.
- The full backend suite in natural order:
  - with the leak: 1 failed (exactly this test), 1311 passed, 2 skipped, 8m36s;
  - restored: 1312 passed, 2 skipped, 8m27s.
VERDICT: G3 is CLOSED, unconditionally. The rest of CI's full gate is read by the lead.
```

**Pass (b) after the merge, the reachability sweep, run by the auditor on 2026-09-28.**
- **Predicate, verbatim:** `git show 109cd065:docs/ledgers/LG-01204-wk-672-slice-2-golden-quotes-and-promotion-re-scoring.md | grep -oE '\b[0-9a-f]{7,40}\b' | sort -u`. That gives 25 tokens. Each token is classified in this order:
  1. `git cat-file -t` is not `commit`: NOTCOMMIT.
  2. `git merge-base --is-ancestor <t> 109cd065` exits 0: MAIN.
  3. The same check against the #867 head `a33f6c2e`, fetched read-only with `git fetch origin pull/867/head`, exits 0: BRANCH.
  4. Anything else: NEITHER.
- **MAIN ×7:** `3f7bddda`, `4fb07b6c` (short and full), `e6a9ca71` (short and full) and `ffba6753` (short and full).
- **BRANCH ×12 tokens (11 commits):** the pre-squash commits listed above (`983c5144` appears short and full).
- **NOTCOMMIT ×6, none of them SHAs:**
  - UUIDv7 fragments from a quoted F3 red: `01a0e909`, `59d167943369` and `ec91214054b1`;
  - the CI run id `36462673125`;
  - the alembic revision ids `d3b955a63d6a` and `fb705749c5d9`.
- **NEITHER ×0.**

**Acceptance, `PL-1189` items 1–12.**
- Items 1–11 are verified by the audit record above.
- The full two-half gate on the final head passed in CI on `a33f6c2e`. The auditor read the runs by head SHA with `gh run list --branch p2-d-s2`: python `36465812202`, frontend `36465811834`, docs `36465811898` and history-policy `36465811819`, each completed with a success conclusion.
- Item 12, the deputy's merge acknowledgement, is the MERGE-ACK at 2026-09-28 19:49:05 BST.
- Nothing is owed by this slice. The slice is closed.
