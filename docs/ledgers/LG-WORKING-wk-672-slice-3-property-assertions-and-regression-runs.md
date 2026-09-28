---
id: LG-WORKING
family: ledger
title: WK-672 Slice 3 — Property assertions and regression runs
status: active
created: 2026-09-28
owner: executor
tree: 06c1f3ac
phase: P2
work: WK-672
plans: [PL-1205]
corrected_by: []
relates: [RL-1172, PL-930, PL-1189, LG-1204]
---

# LG-WORKING — WK-672 Slice 3 — Property assertions and regression runs

Executed from `PL-1205` (active on `main` since #866, `ce27e560`), under `RL-1172`, RS-1176's six
conditions and the deputy's DP-S3-1 to DP-S3-8 by delegation. Branch `p2-d-s3`, from `ce27e560`;
`origin/main` merged twice or once as listed below (`git merge`, never a rebase). Test database
`gipricing_executor-s3`, `GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_executor-s3`
for every run, dropped by name when the slice merges (the earlier `gipricing_tree-s3` was left
for the lead). This ledger is drafted under a working id and renumbered at the mint turn together
with `FR-9301`, `OQ-9302`, `OQ-9303` and `OQ-9304`.

## Tasks

| Task | Commit | What was done |
|---|---|---|
| 1 | `68f644bc` | `03`: FR-257's at-least-one-golden-quote clarification (DP-S3-1), FR-261's amendment, `FR-9301` (the case store), NFR-499's third-store clarification, §4.9, §5.2, §8 and `skills-map.md` (`hypothesis==6.165.7`). |
| 2 | `f377f83e` | `RegressionRun`, `RunGeneration`, `PropertyResult`, `CasesLog`; `RegressionGeneration.cases` capped at 10 000; `regression-run` generated and compared; the F83 register entry. |
| 3 | `399affa1` | The `hypothesis` pin (both `pyproject.toml` files, `uv lock`), `generate_contexts`, the generation settings, `GeneratorVersionMismatch`, the determinism tests. |
| 4 | `b10d3805` | `properties.py`, `golden.py`, `replay.py`, `run_regression`, the `replay-never-generates` import contract. |
| 4-fix | `90899c3f` | `suppress_health_check` removed (lead ruling), settings asserted exactly, the unclamped run-level monotone fixture. |
| 5a | `c895f85b` | `regression_runs` table, `RegressionRunRow`, migration `a71c3e95d204`, `persist_run` / `latest_run`. |
| 6, 6b | `69a6a378` | FR-257 limb (1) at submit; the shared `_Gate` fixture in `test_rating_versions.py`. |
| — | `013bdaa9` | Merge of `origin/main` (#868, `5ec47dc4`), no conflict. |
| — | `2acc96be` | `a71c3e95d204` re-parented onto `02d24f580752`. |
| fixes 1–5 | `ced93a08` | Auditor-a's five findings (below). |
| 5b | `82372734` | The route, the `rating.regression` handler, the case blob, `PROPERTY_ASSERTION_FAILED`, the deny-tuple entry, the two GET routes. |
| 4b | `34623628` | The monotone grid (uniform plus sampled), no vacuous pass, `grid` and `counterexample_points`, `OQ-9302`/`9303`/`9304`. Started 21:33:28 BST, committed about 21:39. |
| — | `98424cc5` | `open-questions.md` line 47's specimen spelling. |
| demo | `d205815e` | The demo rating version's executed regression evidence (DP-S3-8 (a)). |
| — | `9db252d4`, `06c1f3ac` | Cross-process sampled-grid determinism; run-level failures for three classes; the `no_null_output` fix; §5.1's unpaginated note. |

## The reds (each shown before its code change unless stated)

- **Task 2.** `ImportError` on `RegressionRun` (5 failed, 21 passed) before the model.
- **Task 3.** `ImportError: cannot import name 'GeneratorVersionMismatch'` before `generate_contexts`.
- **Task 6.** With `rating_versions.py` reverted to `HEAD`, the 8 new limb-(1) tests failed (`DID NOT RAISE` seven times; `KeyError: 'regression_suite_run_id'`), then passed with the gate.
- **Task 4b.** 10 failed, 16 passed before any code: `case_holds() got an unexpected keyword argument 'seed'`, `ImportError: monotone_grid`, `AttributeError: PropertyResult.grid`, and `assert 'pass' == 'fail'` on the whole-range-decline test (the old code let a property that compared nothing pass).
- **Fixes 1–5.** The seed, replay-refusal and negative-range tests failed before the change. The three-place decimal bound test passed on the old code (hypothesis already rounded inward): a regression guard, not a red-first proof.
- **`no_null_output` (this ledger's finding).** A run-level test on a real variant bundle first read `assert ('pass', 'pass') == ('fail', 'fail')`: a null output is omitted from `ScoringResult.outputs`, so a check over the values could never fail. The check now also requires every declared output present and non-null.
- **Cross-process determinism.** Seeding the sampled grid from `hash(field.name)` turns `test_the_same_seed_gives_the_same_run_across_fresh_interpreters` red; restored.
- **Blob deny.** Removing `RegressionRunRow.cases_blob_sha256` from `QUOTE_INPUT_BLOB_COLUMNS` turns the access test red (1 failed). The first version of that assertion stayed green (the route's allow-list already refused an unreferenced blob), so the digest is now made ownable by a job in the caller's workspace.
- **`import hypothesis` / `import testing` in `replay.py`.** `lint-imports` printed `BROKEN` (`3 kept, 1 broken`) for each; restored.

## S-8 deviation (test-first slipped, then repaired)

Three places had the implementation written before its tests: Task 4, Task 5a and the demo fixture.

- **Task 4.** Each of the five property classes was mutated in `properties.py::case_holds` to always-true and its test run with `uv run pytest packages/pricing-core/tests/test_testing.py -q -k <test>`: `premium_positive`, `no_null_output`, `ladder_reconciles`, `premium_bounded` and `monotone` each gave `1 failed`; `properties.py` was restored from a copy each time and `git diff` on it was empty.
- **Task 5a.** Two mutants of `latest_run` (ordering `asc`, bundle filter `!=`) turned 1 and 2 tests red; restored.
- **Demo fixture.** Skipping the regression Job, and a typed expected premium of 999, each turned `test_demo_rating_evidence.py` red; restored.

## Plan deviations, each ruled

- **`run_regression` / `replay_cases` signatures.** `rating_version_ref` and `now` are keyword-only, and `replay_cases` takes `recorded`: `pricing-core` holds no clock (`CLAUDE.md` §2), and a replay must report each counterexample's persisted shrink state. `job_id` stays `None` for the backend; `cases_blob` is the case log's own content address. Ruled by the lead.
- **The seed.** `run_regression` takes no `seed`; it draws under `suite.generation.seed` (auditor-a, lead).
- **`ladder_reconciles`** is anchored on the `risk_premium` rung (lead: stricter and consistent with FR-248).
- **`suppress_health_check`** was added by the executor and removed on the lead's ruling; no health check fires on the fixtures.
- **`monotone`** is ceteris paribus (DP-S3-5), with a uniform five-point grid plus five points from a private `random.Random(f"{seed}:{field.name}")` (DP-S3-6 re-ruled; the deputy concurred on stdlib `random` rather than `hypothesis`, because replay may not import it). The run records `grid: uniform+sampled` and, for a counterexample, `counterexample_points` (the deputy concurred; the second field was added without asking first, recorded against the slice). A declined grid point is skipped and quoted neighbours are compared across the gap; a property that compared nothing fails (`MONOTONE_NO_COMPARABLE_PAIRS`, DP-S3-7). The narrow-band weakness is a named known-limit test citing `OQ-9304`.
- **Generator range.** A `decimal` with no bound is sampled symmetrically like an `int` (`-1 000 000..1 000 000`); the ruling named `int` only, the lead accepted the extension.
- **`regression_runs.finished_at`.** A scalar column beyond the plan's list, because the audit-A1 ordering (`finished_at`, then `id`) needs it. Accepted by the lead.
- **`JobKind`.** The existing `JobKind.RATING_REGRESSION` is used; the plan's "gains `REGRESSION_RUN`" was unnecessary, so there is no model-schema change for it.
- **T6b's grep.** `PL-1205`'s `grep -rlnE 'submit_for_review|rating-versions/[^"]*/submit'` matches every artifact type's submit; narrowed to rating versions, the sites are `backend/tests/test_rating_versions.py` (all direct, gate and HTTP submits, through the one `_Gate` fixture) and `examples/fremtpl2/model.py:334` (the demo fixture, below).
- **Changed test expectation.** S2's `test_golden_no_suite_proceeds_with_an_explicit_not_checked_record` expected review with `golden_quotes = {status: not_checked, regression_suite: none, reason: no_suite_for_algorithm}`; it is now `test_golden_no_suite_is_refused_as_incomplete_evidence`, expecting `EVIDENCE_INCOMPLETE`, status `draft`, no evidence and no approval request (DP-S3-1).
- **The Task 0 grep defect.** `git log --grep '(#868)'` and `--grep 'PL-1189'` match the plan's own commit `ce27e560`. Task 0's check was made by commit subject (`git log --format=%s origin/main | grep -F '(#868)'`) and by the symbol `QUOTE_INPUT_BLOB_COLUMNS`. Filed as a LOW finding by auditor-b.

## Records this slice adds

- **`FR-9301`** (working id), **`OQ-9302`** (GBM split thresholds, WK-1178), **`OQ-9303`** (ordinal inputs, WK-675), **`OQ-9304`** (pin Bandings in the bundle, WK-1178): renumbered together, in that order, at the mint. The three OQs are mirrored in `open-questions.md`, `03` §10 and the roadmap §10 "Before Phase 2" row (15 (0 open) → 18 (3 open)).
- **Editing `open-questions.md` unfroze two disclosed check-32 rows** (line 47, the OQ-555 specimen `PL-00<n>`, twice); the specimen was respelled as a phrase (`98424cc5`). Any other PR that touches that file meets the same two rows.
- **The re-parent.** `a71c3e95d204` was parented on `fb705749c5d9`, then re-parented on #868's `02d24f580752` after the merge; `alembic heads` = 1, upgrade / downgrade −1 / upgrade rc 0 on a fresh `gipricing_executor-s3`, and `test_the_migration_chain_has_exactly_one_head` passes.
- **The demo.** The fremtpl2 demo's rating version has no algorithm, bundle or pins, so FR-257 limb (1) refused it. The seed authors a labelled "demo fixture" algorithm (`payable = premium_in * 2`, **not priced from the GLM**), compiles it through the `rating.compile` Job, computes the golden quote's expected premium with `score_one`, and runs the regression through the `rating.regression` Job; nothing is inserted. The version is then submitted through the real gate and approved by two approvers (`06` §4.2's default policy; the seed had one, and its `decide` call lacked the evidence-author resolver). `backend/tests/test_demo_rating_evidence.py` asserts the run carries its succeeded Job, the label, the computed premium, and that its `bundle_hash` and `suite_content_hash` equal what the gate pins. `test_demo_command`, `test_demo_postconditions` and `test_demo_guide` never exercised submit; this file adds that step. The demo fixture does **not** satisfy G2: the real freMTPL2 algorithm is a separate finding owned by the lead.

## Process notes

- A full gate was started once before the lead's rule that T7 runs alone on a quiet box; it was killed by PID and produced no result. The gate below is the one that counts.
- `git stash` was typed by mistake for a few seconds and popped straight back; nothing was lost (status and the following commit verified).

## The gate

Pending: recorded after the lead grants the gate slot (both halves, the five `test_rating_score.py` runs, the four docs checks on a detached copy, `git diff --stat origin/main...HEAD`).

## PRs

| PR | Branch | Title | Squash SHA on `main` |
|---|---|---|---|
| (draft, number on opening) | `p2-d-s3` | feat(rating): WK-672 Slice 3 — property assertions and regression runs, PL-1205 | (on merge) |
