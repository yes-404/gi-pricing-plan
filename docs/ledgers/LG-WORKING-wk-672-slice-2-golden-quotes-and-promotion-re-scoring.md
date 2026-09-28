---
id: LG-WORKING
family: ledger
title: WK-672 Slice 2 — Golden Quotes and promotion re-scoring
status: active
created: 2026-09-28
owner: executor
tree: ffba67539ba5f0c5cd04aa72a0c4270a517c0562
phase: P2
work: WK-672
plans: [PL-1189]
corrected_by: []
relates: [RL-1172, PL-930, LG-1182]
---

# LG-WORKING — WK-672 Slice 2 — Golden Quotes and promotion re-scoring

Executed task by task from `PL-1189` (`status: active` on `main` since #862, squash
`ffba67539ba5f0c5cd04aa72a0c4270a517c0562`), under `RL-1172` and the deputy's decisions
DP-S2-1 to DP-S2-6 by delegation, quoted whole in the plan. Branch `p2-d-s2`, fast-forwarded
to `origin/main` at `ffba6753` before Task 1 and merged with `origin/main` at
`e6a9ca71a0bef3da41720d20f3f20db73f6a1d80` (#864) before Task 5 (`git merge`, never a rebase).
Every commit below is a pre-squash branch commit of this slice's one PR. This ledger carries
the working id `LG-WORKING` until its mint turn (the team's id rule), when one renumber
commit gives it the next free id read from `origin/main`.

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

Pending — recorded on the final tree.

## PRs

| PR | Branch | Title | Squash SHA on `main` |
|---|---|---|---|

## Provenance notes

- `ffba6753`'s subject says (draft); `PL-1189` was `status: active` at merge, per its Status
  block (Activated 2026-09-28 16:21:33 BST).
