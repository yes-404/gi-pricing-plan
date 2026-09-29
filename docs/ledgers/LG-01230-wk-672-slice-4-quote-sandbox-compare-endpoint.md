---
id: LG-1230
family: ledger
title: WK-672 Slice 4 — Quote Sandbox compare endpoint (FR-262 backend limb)
status: active
created: 2026-09-29
owner: executor
tree: b4aa909d43f347091e3ee239fbc72ab4c5ca4491
phase: P2
work: WK-672
plans: [PL-1213]
corrected_by: []
relates: [RL-1172, PL-930, PL-1205, LG-1225]
---

# LG-1230 — WK-672 Slice 4 — Quote Sandbox compare endpoint (FR-262 backend limb)

Executed from `PL-1213` under `RL-1172` §5 and the deputy's DP-S4-1 to DP-S4-5 (entry of
2026-09-28 21:08:30 BST) and its F5 amendment (21:10:34 BST). Branch `p2-d-s4`, from `b4aa909d`
(#886's MERGE-ACKed head, S3). `LG-1230` was drafted under the working number 9110 and renumbered at the mint (see "The mint" below).

## Task 0 — adjusted by the maintainer's instruction (to-lead.md ~12:01 BST 2026-09-29)

- **Step 1** satisfied by branching from #886's ACKed head `b4aa909d`, which contains S3's code.
  Symbol check: `packages/pricing-core/src/pricing_core/rating/replay.py` exists in the tree.
  The `origin/main` subject-line check comes after #886 merges.
- **Step 2** the decision entry is in `channel/to-lead.md` (2026-09-28 21:08:30 BST, line 9327;
  the F5 entry at 21:10:34 BST, line 9342). Both read.
- **Step 3** `origin/main` is **not** merged now. The lead says when #886 has squash-merged; then
  a plain merge, quoted conflict-free, and the plan's literals re-read.
- Literals re-read at `b4aa909d`, no drift: `score.py:110` `ScoreExecuteDep`, `:114`
  `_required_ref`, `:206` `_compiled_for`, `:241` `_as_platform_error`; `03` has no §4.10.
- Test database `gipricing_executor-s4_18004fad` (created from the template, `alembic upgrade head` rc 0).

**The mint.** This ledger and the open question were drafted under the working numbers 9110 and
9401 and renumbered in one commit at this slice's mint turn, after `origin/main` at
`d7ed822ec238a3344a04215240a67bff4994fed9` (#899) was merged into the branch (a `git merge`; the one
conflict, `docs/INDEX.md`, took main's copy and was regenerated). `python3 scripts/doc-id.py next --ref
origin/main` printed `1230`; the two ids are `LG-1230` and `OQ-1231`. The historical entries below that
quote the check-31 gaps `1225→9110` and `9110→9401` are numbers as measured at those heads and are left as
written.

## Tasks

| Task | Commit | Red cause | What was done |
|---|---|---|---|
| 2 | `92a281c0` | `ImportError: cannot import name 'ScoreCompareRequest'` | `StepChange`, `TraceDiff`, `ScoreCompareRequest`, `ScoreComparison`; `score-comparison` generated; `ONE_SIDED_SLUGS` line in `test_contracts.py` (not in the plan). |
| 3 | (this commit) | `ModuleNotFoundError: pricing_core.rating.trace_diff` | `diff_traces` and `test_trace_diff.py` (10 passed). |
| 4, 5, 1 | (this commit) | route test: 404 for the unrouted path | `POST /api/v1/score/compare`; `test_score_compare.py` (13 passed); `03` §4.10, §5.1, §5.2, FR-262, OQ-1231 (drafted under the working number 9401) in `03` §10 and `open-questions.md`; `score-comparison` added to `audit-docs.py`'s non-markdown stamp-exemption tuple (precedent: `regression-run`); `openapi/generated.json` regenerated; `INDEX.md` regenerated. |

### Task 3 mutations (not committed)

1. `own_change=True` for every changed step → red: `assert ['s_rate', 's_total'] == ['s_rate']`
   (cascade test) and the known-limit test.
2. `"produced"` dropped from `_COMPARED` → 6 failed, 4 passed: cascade, known-limit, no-downstream
   (`assert [] == ['s_rate']`) and the three `1`/`1.0`/`True` cases.

### Plan gaps found (recorded at the lead's request)

- Task 2: `backend/tests/test_contracts.py` needs an `ONE_SIDED_SLUGS` line for `score-comparison`
  (`test_every_one_sided_slug_is_declared` failed without it). The plan says only "a scope line if
  the guard needs one".
- Task 2 Step 1 red: my first test fixture used `purpose: "quote"`, which `QuotePurpose` refuses
  (valid: `new_business`, `renewal`, `mid_term_adjustment`, `cancellation`, `what_if`). Fixed to
  `new_business`; the plan gave no fixture value.

## PRs

| PR | Branch | Title | Squash SHA on `main` |
|---|---|---|---|
| (draft, number on opening) | `p2-d-s4` | feat(rating): WK-672 Slice 4 — Quote Sandbox compare endpoint, PL-1213 | (on merge) |

### Tasks 4-5: findings against the plan

- **NFR-499 persistence test, as the plan wrote it, is vacuous.** `rating:read` is not a Service Account
  permission (FR-389 allows `score:execute` and `score:batch` only), so the caller (DP-S4-3 (i)) is a
  user, and a user has no `caller.environment`. A copied `_maybe_sample_trace` then raises inside its own
  `try`, is logged, and writes nothing. The mutation (call `_maybe_sample_trace` after each `score_one`)
  left the row-count and caplog tests green. The test now also spies on `_maybe_sample_trace` and asserts it
  is never called; under the mutation it goes red: `AssertionError: the sandbox route reached FR-259's
  trace sampling`. The caplog test stays green under the mutation (the swallowed error logs no input value),
  so plan item 7's "both red" is unreachable; the caplog test still guards a route that logs the input.
- **The engine traces expression steps only**, and `consumed` is the whole environment. The minimal
  algorithm has one expression step, so the fixtures insert a downstream expression step `s_adj`
  (`payable + 100`) to make the cascade observable through HTTP: own_change entries `["s_expr"]`, `s_adj`
  downstream with `consumed` in `changed_fields`, `unchanged == 0`; identical refs give `unchanged == 2`.
- `_insert_version` (`test_rating_version_compile.py`) gained optional `slug`/`version` keywords, backward
  compatible, so two versions can be inserted.
- Mutation B (`_naming_side` removed): the 404, 409 and 422 side-naming tests go red (6 failed).
- Red-first for the other route tests was shown by mutation, not by an absent route: only the first test
  was written before the route.
- Plan item 4's grep (`class .*Comparison|class TraceDiff|class StepChange`) prints two unrelated classes
  (`ModelComparisonRow`, `ComparisonCandidate`); none is a compare shape. The predicate is too loose.
- Docs checks: `audit-docs.py` FAILED (2): check 31 gaps 1225→9110 and 9110→9401, the working-id gap only.

### Plan deviations, dated 2026-09-29 (accepted by the lead; the maintainer's item-7 ruling in `to-lead.md`)

1. **NFR-499 (plan item 7).** `rating:read` cannot be a Service Account scope (FR-389:
   *"['rating:read'] is not in ['score:batch', 'score:execute']. FR-389 scopes service accounts to the
   scoring permission set."*, the 422 from `POST /api/v1/service-accounts`), so the caller is a user, which
   has no `caller.environment`; a copied sampler raises inside its own `try`, is logged, and writes nothing.
   Mutation (uncommitted): in `score_compare`, after each `score_one`,
   `+ await _maybe_sample_trace(database, settings, caller, ctx, results[-1])` (and a `settings: SettingsDep`
   parameter).
   - Row-count check and caplog test under it: **both stayed green** — the row-count test is
     **vacuous under the copied-sampler mutation**.
   - Spy added (`monkeypatch` of `score_module._maybe_sample_trace`, asserted never called): red,
     `AssertionError: the sandbox route reached FR-259's trace sampling`; restored, 13 passed.
   - Plan item 7's "both red" is therefore met for **persistence only** (via the spy).
   - **caplog test's own red proof** (maintainer's ruling), on deliberately broken input. Mutation
     (uncommitted), first line of `score_compare`:
     `+    _log.info("compare requested", extra={"inputs": body.context.inputs})`.
     Result: `FAILED test_compare_logs_no_input_value - assert 'ZZ99 9ZZ' not in '{'name': ...1 200 OK"'}'`.
     Restored: `1 passed`. So the test does guard a route that logs a quote input field; it cannot go red under
     the copied-sampler mutation because that path logs no input, and it does not claim to.
2. **Fixture step and helper.** The engine traces expression steps only and `consumed` is the whole
   environment, so the minimal algorithm has one traced step. The fixtures add a downstream expression
   step `s_adj` (`payable + 100`); `_insert_version` gained keyword-only `slug`/`version` (defaults
   unchanged). The one-step proof is unchanged: the `own_change` entries are exactly `["s_expr"]`, and
   `s_adj` is listed with `own_change: false` and `consumed` among its `changed_fields`.
3. **Item 4 predicate.** The plan's command
   `grep -rn 'class .*Comparison\|class TraceDiff\|class StepChange' backend/src packages/pricing-core/src`
   prints two pre-existing hits, neither a compare shape:
   `backend/src/app/db/models.py:1413:class ModelComparisonRow(Base):` and
   `packages/pricing-core/src/pricing_core/modelling/comparison.py:74:class ComparisonCandidate:`.
   Tighter predicate used: `grep -rnE 'class (ScoreCompareRequest|ScoreComparison|TraceDiff|StepChange)\b'`
   over `backend/src packages/pricing-core/src` prints nothing (rc 1: no shape defined outside
   `model-schema`), and over `packages/model-schema/src` prints the four definitions in `scoring.py`
   (scoring.py:196 StepChange, :219 TraceDiff, :229 ScoreCompareRequest, :249 ScoreComparison).

## Gate entries

### Python half at `b9429948` (2026-09-29)

Started 11:19:06Z under `/tmp/slots/gate-*` (`flock`), `CI` unset, `timeout 3300` on the pytest stage.
Pre-start reading, quoted exactly: `11:18:54 up 2:36, 1 user, load average: 18.06, 12.73, 7.21`, and
`pgrep -af '[p]ytest'` printed nothing. The load-below-8 precondition had not reached me before the
start; the first ~30 s overlapped an external load spike (`to-lead.md`, 12:19:51 BST entry). Finished
before 11:43:52Z (`uptime` then: `load average: 2.71, 3.23, 4.02`). Wrapper log
`~/.claude/jobs/92b3ca72/tmp/gate-b9429948.log`, stage logs `/tmp/tmp.9m5cbDc6cw`, `FINAL_RC=1`.

| stage | result | detail |
|---|---|---|
| ruff | pass | exit=0 |
| mypy | pass | exit=0 |
| import_linter | pass | exit=0 |
| audit_docs | FAIL | exit=1 (check 31 only: gaps 1225→9110 and 9110→9401, the working ids) |
| req_coverage | pass | exit=0 |
| contracts | pass | exit=0 |
| pytest | FAIL | exit=1 (14 failed, 3725 passed, 3 skipped, 24:27) |

The 14 failures: 13 docs-audit tests that run the real tree and fail on the working-id gap (they pass
after the mint), plus `test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts`
(`AssertionError: 67`): its pinned count of exempt non-markdown files went 66→67 with
`score-comparison.schema.json`. Fixed in `73616265` (dated comment, the `regression-run` precedent).

### Frontend half at `73616265` (2026-09-29, from 11:45:05Z, `CI` unset, under a gate slot)

`pnpm --dir frontend install --frozen-lockfile` rc 0; `generate:api` rc 0 (the generated `schema.d.ts`
lists `/api/v1/score/compare`); `lint` rc 0; `type-check` rc 0; `test` rc 0 (97 files, 603 tests passed,
no `Errors` line); `build` rc 0. Logs `/tmp/fe-s4-*.log`.

## Merges of `origin/main` (2026-09-29)

Task 0 Step 3, as instructed. Main was `6a8b8e70` (#886, a squash of `b4aa909d`) and then `f2ef3b9a`
(#898, the S3 closing record).

1. A plain `git merge 6a8b8e70` conflicted in six files (`docs/INDEX.md`, `docs/open-questions.md`,
   `03`, `scripts/audit-docs.py`, `scripts/generate-contracts.py`, `tests/test_audit_docs_ids.py`):
   the merge base was the pre-S3 `ce9303b3`, and main's squash of S3 collides with this branch's
   un-squashed S3 commits next to the S4 edits. Aborted.
2. Proof that the trees agree: `git diff --stat b4aa909d 6a8b8e70` printed nothing (both tree
   `f65bdd60`). `git merge -s ours --no-edit 6a8b8e70` (lead's GO), then
   `git diff --name-only 6a8b8e70 HEAD` listed exactly the 18 S4 paths.
3. `git merge --no-edit origin/main` (`f2ef3b9a`), a normal merge: conflicts in `docs/INDEX.md`,
   `docs/open-questions.md` and `03`. Resolved keeping both sides: main's OQ-1222 to OQ-1224 rows and
   FR-1221 line, plus this slice's OQ-1231 row and FR-262 clarification; `INDEX.md` regenerated.
   `git diff --name-only f2ef3b9a HEAD` lists the same 18 S4 paths. The four docs checks:
   `audit-docs.py` FAILED (2), check 31 only (the working-id gaps 1225→9110, 9110→9401);
   `doc-id.py check` the same two gaps; `doc-index.py --check` OK; `register-lint.py` 0 violations.
4. Literals re-read at this tree, no drift: `_required_ref`, `_compiled_for`, `_as_platform_error`,
   `ScoreExecuteDep`, `score` in `backend/src/app/api/score.py`; `03` §4.10 present once.
5. Main moved again (#876, the FD-1199 test fix to `packages/pricing-core/tests/test_rating_score.py`): a
   plain `git merge a5118a30` was conflict-free (one file, 73 insertions, 13 deletions).
   `git diff --name-only a5118a30 HEAD` lists the same 18 S4 paths; `audit-docs.py` FAILED (2), check 31
   only; `doc-index.py --check` OK.

### Merge evidence, quoted as the lead asked (2026-09-29)

- (a) `git rev-parse b4aa909d^{tree} 6a8b8e70^{tree}` printed `f65bdd608bda3bd5964f47357606406e109c8c0e` for both.
- (b) The `-s ours` merge is **`db1b768f`** (`Merge commit '6a8b8e70…' into p2-d-s4`, parents `e635c3e3`
  and `6a8b8e70`). Its first parent was `e635c3e3`, the S4 head when I ran it, not `73616265`
  (`e635c3e3` is the docs-only ledger commit after `73616265`). `git diff e635c3e3 db1b768f` prints
  nothing (0 bytes). `git diff 73616265 db1b768f` is not empty for that reason alone: it prints the
  32 lines `e635c3e3` added to this ledger (1 file changed).
- (c) The merge of `f2ef3b9a` is **`5dd823e9`** (parents `db1b768f`, `f2ef3b9a`): 3 conflicts,
  `docs/INDEX.md`, `docs/open-questions.md`, `docs/specs/03-rating-engine.md`, each resolved keeping both sides.
- (d) The merge of `a5118a30` is **`51d8a67e`** (parents `9e045cf9`, `a5118a30`): conflict-free.

### Full two-half gate at `1509bc0c30585ea16b3441667eef137248e2d005` (2026-09-29)

Slot granted by the lead at 11:56Z; started 11:56:01Z, pre-start `11:56:01 up 3:13, 1 user, load average: 1.29,
1.77, 2.91`, `pgrep -af '[p]ytest'` empty; `CI` unset; the `dev-commands` block under `flock` with
`timeout 3300` on pytest; finished before 12:20:16Z. Wrapper log
`~/.claude/jobs/92b3ca72/tmp/gate-1509bc0c.log`, stage logs `/tmp/tmp.yNPsmbCXeF`, `FINAL_RC=0`.

| stage | result | detail |
|---|---|---|
| ruff | pass | exit=0 |
| mypy | pass | exit=0 |
| import_linter | pass | exit=0 |
| audit_docs | pass | exit=0 |
| req_coverage | pass | exit=0 |
| contracts | pass | exit=0 |
| pytest | pass | exit=0 |

`GATE: pass — 7 of 7 stages passed`. Pytest summary: `3739 passed, 3 skipped, 46 warnings in 1434.26s (0:23:54)`.
Frontend half at the same head: `install --frozen-lockfile` rc 0, `generate:api` rc 0, `lint` rc 0, `type-check`
rc 0, `test` rc 0 (97 files, 603 tests, no `Errors` line), `build` rc 0.

### N=5×2 of `test_rating_score.py` (2026-09-29, from 12:22:29Z)

Run at `10893eda` (its code is `1509bc0c`'s: `10893eda` changes only this ledger), each run under
`/tmp/slots/verify-*` (`flock -n -E 99`, then the blocking fallback), sequentially, `timeout 900`, thread caps as
in the gate, `uv run pytest packages/pricing-core/tests/test_rating_score.py -q -p no:cacheprovider`.
Pre-start `12:22:30 up 3:40, 1 user, load average: 2.23, 2.34, 2.23`, no other pytest. Logs `/tmp/n5-s4-*.log`.

| run | `CI` | rc | summary |
|---|---|---|---|
| 1 | `CI=1` | 0 | `24 passed in 5.73s` |
| 2 | `CI=1` | 0 | `24 passed in 5.64s` |
| 3 | `CI=1` | 0 | `24 passed in 5.72s` |
| 4 | `CI=1` | 0 | `24 passed in 5.70s` |
| 5 | `CI=1` | 0 | `24 passed in 5.74s` |
| 6 | unset | 0 | `24 passed in 5.70s` |
| 7 | unset | 0 | `24 passed in 5.71s` |
| 8 | unset | 0 | `24 passed in 5.73s` |
| 9 | unset | 0 | `24 passed in 5.70s` |
| 10 | unset | 0 | `24 passed in 5.60s` |

No abort, all ten rc 0.

## Final head `1cadf98e5c194e9a7e8e7369f5881e9de22b6c6c` (2026-09-29)

The maintainer's ruling: a plain merge of the then-current `origin/main`, the test-count floor, the four
docs checks, the diff against the gated head, and the N=5×2 redo if `test_rating_score.py` or `pricing-core`
code differs from the gated head. Draft PR #901 (opened by the lead) at this head.

- **(a) Merge.** `git merge 369c5774b9c986afa032b97e542773d2da765481`, plain: conflict-free (no conflict at
  all, `INDEX.md` included). Merge commit `1cadf98e` (parents `0bba909a`, `369c5774`).
- **(b) Test-count floor.** Main's count: 3747 (`95faf68b`'s python CI, 3744 passed + 3 skipped, the lead's read);
  `git diff --name-only 95faf68b 369c5774 | grep test` is empty, so #897, #900 and #896 added no test file.
  S4's net added: 28, by `pytest --collect-only -q` on the three new files at the merged head
  (`test_score_compare.py` 13, `test_scoring_compare.py` 5, `test_trace_diff.py` 10; a new file's tests all
  count as added); the modified test files (`test_contracts.py`, `test_rating_version_compile.py`,
  `tests/test_audit_docs_ids.py`) add and remove no `def test_`; cross-check
  `git diff origin/main...HEAD -U0` gives 23 added and 0 removed `def test_` lines (the parametrized tests
  expand to 28). Floor: 3747 + 28 = **3775**.
  **Python CI** (run 36568093701, 12:26:15Z to 12:42:30Z): `3772 passed, 3 skipped, 46 warnings in 876.97s
  (0:14:36)`, i.e. 3772 + 3 = 3775, equal to the floor. Success. The docs (36568093720), frontend
  (36568093742) and history-policy (36568093732) runs also concluded success at `1cadf98e`.
- **(c) Docs checks at `1cadf98e`.** `audit-docs.py` rc 0 ("All checks passed."); `doc-id.py check` rc 0;
  `doc-index.py --check` rc 0 ("OK (byte-stable)"); `register-lint.py` rc 0 ("OK (0 violations)").
- **(d) Diff against the gated head.** `git diff --stat 1509bc0c 1cadf98e`: 31 files changed, 1107
  insertions, 80 deletions. The only file not in main's incoming set (`git diff --name-only a5118a30
  369c5774`) is this ledger. Against `369c5774`, `git diff --name-only` is the 18 S4 paths.
- **(e) `pricing-core` diff and the N=5×2 redo.** `git diff 1509bc0c HEAD -- packages/pricing-core/` is not
  empty: `diagnostics.py` (+233/−51 net), `tests/test_diagnostics.py` (+36) and `tests/test_gbm.py` (+267), all
  main's incoming modelling work (#887); `test_rating_score.py` is unchanged. The second limb of the rule
  (`pricing-core` code differs) is met, so the N=5×2 was redone at `1cadf98e`, pre-start
  `12:26:32 up 3:44, load average: 1.12, 1.76, 2.02`, no other pytest, same wrapper and command as above,
  logs `/tmp/n5b-s4-*.log`:

| run | `CI` | rc | summary |
|---|---|---|---|
| 1 | `CI=1` | 0 | `24 passed in 6.05s` |
| 2 | `CI=1` | 0 | `24 passed in 6.06s` |
| 3 | `CI=1` | 0 | `24 passed in 6.02s` |
| 4 | `CI=1` | 0 | `24 passed in 5.91s` |
| 5 | `CI=1` | 0 | `24 passed in 6.03s` |
| 6 | unset | 0 | `24 passed in 6.08s` |
| 7 | unset | 0 | `24 passed in 5.88s` |
| 8 | unset | 0 | `24 passed in 5.81s` |
| 9 | unset | 0 | `24 passed in 5.63s` |
| 10 | unset | 0 | `24 passed in 5.84s` |

No abort, all ten rc 0.

FR-262's typing at the Work close: backend limb delivered and tested (WK-672); UI limb reassigned to WK-675.

## Hand-off to WK-675

`StepChange.own_change == false` means **"no own change attributable from the traces"**. **Do not render it as
"unchanged" or "not edited".** A downstream step that was itself edited and whose input also moved reads `false`
(the known limit `03` §4.10 states and `test_trace_diff.py`'s known-limit test pins). Whether `own_change`
should be derived from step-definition equality instead is `OQ-1231`, owned by WK-675, to be decided before its
compare view ships.
