---
id: LG-1642
family: ledger
title: WK-673 slice SL-1503 — WF-699 E1, FR-242's drafted change summary over HTTP (PL-1502), slice ledger
status: closed
created: 2026-10-11            # original date 2026-10-10, set at the draft; minted 2026-10-11
owner: executor
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-673
slice: SL-1503
plans: [PL-1502]
corrected_by: []
relates: [PL-1502, RL-1498, RL-1445, RL-1263, SL-1389, SL-1391, FR-242, FR-219, FR-231]
---

# LG-1642 — WK-673 slice SL-1503: WF-699 E1, FR-242's drafted change summary over HTTP

*(Minted 2026-10-11 as LG-1642 from working id 9978, at the merge turn.)* Executed by
`executor-sl1503` from PL-1502, base `origin/main` `99f22479a20e7fa64f8b6654e0d371c595b1e35a`.
Times are BST (`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md` "2026-10-10 21:41:05 BST — RL-1445 CAP: AMENDED by dated line (counting unit = gate or measurement, with guard rails); GO SL-1541 (WS-1 (a)); OP-1503-1 (a); SL-1575 noted", item 3: "OP-1503-1: (a) ADOPTED. SL-1503 authors now. Its 03 §5.1 hunks (T1/T2) are applied after WK-675 S3 and S4 have merged, on main, re-anchored by content. Needs 1 (merge-only) and 4 (this GO) are MET with this entry."
**MERGE-ACK:** not yet given (the lead's read at the mint turn, from-lead "2026-10-11 22:44:45 BST": re-gate green modulo mint artefacts; mint turn granted).

## Tasks

| Task | Plan step | Acceptance | Status |
|---|---|---|---|
| 0 | preconditions | — | done (below) |
| 1 | `03` §5.1 T1, T2 | 17 | done 2026-10-11 (WK-675 S3 and S4 on main: `372fa92a`) |
| 2 | shape and pure draft | 1–9, 20 | done |
| 3 | service and route | 10–15 | done; first gate @07830ca6 found three own test defects (below); re-gate @71cc28ae green |
| 4 | contract, gate, ledger | 16–19 | done: contract `--check` rc 0, two-half gate run twice (below), INDEX regenerated, audit-docs fails only the mint artefacts at the pre-mint head |

### Gate

Two full runs of `~/gi-pricing-plan.local/scratch/sl1503/slot.sh <head>` under the `gate-1` flock, each through `handover/slot-preflight.sh` (abort proof before the first run: a wrong head gave rc 90, the right head without the flock rc 92), each: preflight, three red-firsts against the base source, then the two-half gate serially with a START and END stamp per stage. Logs, local and not in the repository: `~/gi-pricing-plan.local/scratch/sl1503/slot.out` and `gatelogs.8dfPbC` (run 1), `slot-regate.out` and `gatelogs.zqwlbu` (run 2).

**Run 1, head `07830ca614782bf9cfb6c63c2e99877b4d9cce55`, tree `b70bf15b8f3b2743b85caffc5b29ee2bc1795b19`, gate-1 20:26:36 to 21:11:54 BST (2026-10-11): rc 1.** Granted by the lead, from-lead "2026-10-11 20:26:27 BST".

| stage | rc |
|---|---|
| red1 pure draft, whole feature reverted | 2 [red] |
| red2 route file, handler reverted | 1 [red] |
| red3 refusal check removed | 1 [red] |
| ruff | 0 |
| mypy | 0 |
| import-linter | 0 |
| pytest | 1 (15 failed, 5607 passed, 5 skipped) |
| audit-docs | 1 |
| req-coverage | 0 |
| contracts `--check` | 0 |
| frontend install, generate, lint, type-check | 0 |
| frontend test | 1 (1 failed of 689) |
| frontend build | 0 |

The 15 pytest reds: 13 are mint artefacts, 2 were this slice's own (below). The 13 run `audit-docs` or the register checks on the real tree and fail on check 31 alone (the working id's gap and `created` order): `test_audit_docs_finding_citations` (1), `test_audit_docs_ids` (2), `test_audit_docs_process_core_digest` (2), `test_audit_docs_w37_11_ceiling` (1), `test_doc_index` (1), `test_register_lint` (3), `test_register_owed` (1), `test_repository_invariants` (2). The 2 own: `test_a_parquet_table_answers_200_with_the_entry_pending` (`AttributeError`, `RateTableVersionRow.version`; from-lead "2026-10-11 20:53:27 BST") and `test_wf699_e1_the_draft_is_built_from_the_approved_baseline` (`202 == 200` from the rate-table diff route, defect 3 in the build log; ruled from-lead "2026-10-11 21:13:13 BST", confirmed by the maintainer "2026-10-11 21:13:52 BST"). The one frontend red was `DagDesigner.test.ts` "emits an edited draft and leaves the other steps as they were" (F39, WK-675's, fixed on main by #1283); alone, once, on this tree under `small-test`: 4 passed.

**Run 2, head `71cc28aea19ae360376d5da4dd4725090b965819` (the three test fixes and the ledger's deviation line on run 1's head), tree `a29278a7bcdb3f2cea09e47d4d0faa6069a82d06`, gate-1 21:56:35 to 22:44:10 BST (2026-10-11): rc 1, mint artefacts only.** Granted by the lead, from-lead "2026-10-11 21:15 BST".

| stage | rc |
|---|---|
| red1 pure draft, whole feature reverted | 2 [red] |
| red2 route file, handler reverted | 1 [red] |
| red3 refusal check removed | 1 [red] |
| ruff | 0 |
| mypy | 0 (237 source files) |
| import-linter | 0 |
| pytest | 1 (13 failed, 5609 passed, 5 skipped) |
| audit-docs | 1 |
| req-coverage | 0 |
| contracts `--check` | 0 |
| frontend install, generate, lint, type-check | 0 |
| frontend test | 0 (109 files, 689 of 689, `DagDesigner.test.ts` included) |
| frontend build | 0 |

All 13 pytest reds are the mint artefacts named under run 1, the same modules; `audit-docs` printed exactly two lines, both check 31 (the id gap 1636 to 9978, and 9978 `created` 2026-10-10 earlier than id 1635's 2026-10-11). Neither route test file nor `test_change_summary_draft.py` has a failure. `ruff` and `mypy` finished in about 0 s, answered from the warm cache on this exact tree; the first run's mypy took 15 s from a cold one. The lead's verdict: green modulo mint artefacts, from-lead "2026-10-11 22:44:45 BST".

**Red-firsts, classified (run 2; run 1 as in the build log).** red1: by cause, `ModuleNotFoundError: No module named 'app.platform.change_summary'`, a collection error (Acceptance 1 to 9 and 20). red2: 8 failed, 0 passed, every one by the router's 404 (`404 == 200`, `404 == 409`, `404 == 403`, and item 13a's title `Resource not found` against `Rating version not found`); item 13a is a real red now, not the vacuous pass of run 1 (rulings "2026-10-11 20:53:55 BST", and for item 15 "2026-10-11 20:53:27 BST"). red3: weak but valid, accepted as a note (from-lead "2026-10-11 21:13:13 BST"): both item-12 cases fail with the check removed, by a 500 (`pins` None, `ArtifactRef` validation) and by a 404 `Rating algorithm not found` (`algorithm_ref` None), not by a 200. The pre-merge head of this slice's mint commit is not gated; the merge of `origin/main` `4af5997e` and the mint change docs, the INDEX and this ledger only, which CI covers.

### Audit

Written by `auditor-sl1503` on head `cd403d41413a5ccc208d5d28a910febb5539eb4f` (tree `2900d6077f642407db5f43bd37225c2a3fbc68db`), range `origin/main...origin/sl-1503-wk673-e1-change-summary` (`origin/main` = `4af5997e`), 2026-10-11. Authority: `to-lead.md` "2026-10-11 19:57:42 BST" (a slice closes on a written audit and the lead's merge; the audit runs in parallel with the minted-head CI), "2026-10-11 20:17:38 BST" item 5 and "2026-10-10 21:41:05 BST" item 3 (T1/T2 applied after WK-675 S3 and S4 merged, by content), and from-lead "2026-10-11 20:26:27 BST" (no validator added; `PlatformError` texts carry no exception text). Scope was derived from PL-1502's Acceptance Standard (items 1–21) and its write set first, then evidenced from the diff, the asserts of both test modules (read), the two gate records (`~/gi-pricing-plan.local/scratch/sl1503/slot.out` with `gatelogs.8dfPbC`, run 1 at `07830ca6`; `slot-regate.out` with `gatelogs.zqwlbu`, run 2 at `71cc28ae`) and the PR. I ran no test; I ran `audit-docs.py` once at this head under `gate-2` (rc 0, "All checks passed", check 31 "773 id(s) in scope, 773 distinct number(s)").

| PL-1502 item | Evidence | Result, proposed verdict |
|---|---|---|
| 1–9 pure draft (`D`) | `test_change_summary_draft.py` asserts read: 1 names each step id and both re-pointed refs; 2 line carries slug, both versions, `2`, `12.5`, and "unweighted" is in the text; 3 added and removed; 4 the exact sentence; 5 no baseline; 6 reversed inputs give an identical text and order; 7 `f"change {pct}%"` full digits (code renders `str(Decimal)`); 8 `lines[-2:] == ["Why:", "Expected impact:"]`; 9 `diff` None, "pending", the diff URL. Red 1: `ModuleNotFoundError` for `app.platform.change_summary`, rc 2, both runs | MET. Note: item 2's needles `"3"`, `"4"`, `"2"` are single characters in one line, near-vacuous beside the slug and `12.5` (the lead: LOW, accepted) |
| 20 baseline without an algorithm | `test_a_baseline_without_an_algorithm_has_no_structural_diff`: baseline kept, `structural_diff` None, "has no algorithm" | MET |
| 10 draft from the approved baseline | `test_wf699_e1_the_draft_is_built_from_the_approved_baseline`: 200, `baseline` is v1's ref, `structural_diff` equals `diff_algorithms(v1, v2)`, `s_extra` in the text, `pending` False, `changed_cells == 1`, and the entry's `diff` equals the diff route's 200 body after the route's Job is run through `test_api_rate_tables._diff_ready` (`test_api_rate_tables.py:154`). Run 2 RED2: `assert 404 == 200`, the router's 404 | MET with a DISCLOSED DEVIATION, proposed GAP → CURED IN-SLICE. The plan's premise (a synchronous 200 from the rate-table diff route) was stale since SL-1391 / RL-1418: the route answers 202 and a Job on the first request for a key (`api/rate_tables.py:398-401`). Option B of from-lead "2026-10-11 21:13:13 BST" taken (feasible, so option A's fallback did not arise), confirmed by the maintainer "2026-10-11 21:13:52 BST" as a disclosed deviation in this ledger, not an RL; the ledger's build log quotes Acceptance 10 verbatim. The draft itself still calls `rate_tables.diff` in-process, so the equality compares the draft with the stored artifact's summary, as intended |
| 11 baseline is the most recently approved | `test_the_baseline_is_the_most_recently_approved_not_the_highest_number` (v2 approved first, v1 later, v3 the draft: baseline `@1`); RED2 `KeyError: 'baseline'` from the 404 body | MET |
| 12 refusal | `test_a_version_without_an_algorithm_or_pins_is_refused`, both params: 409, `RATING_VERSION_UNPINNED`, the detail names the missing field; the code is the service's own `PlatformError` (`rating_versions.py`, `draft_change_summary_for`). RED2 `404 == 409` both params; RED3 (check removed) 500 and 404, not 200 | MET. RED3 is weak but valid (fails by the check's absence, not by a 200): accepted as a note (from-lead "2026-10-11 21:13:13 BST") |
| 13 workspace and permission | 13a `test_another_workspaces_version_is_404`: the algorithm is now saved for the caller, so with scoping removed the draft would be built and answer 200; asserts 404, `NOT_FOUND` and the title "Rating version not found" (raised by `load_rating_version`). Run 2 RED2: `'Resource not found' == 'Rating version not found'`; the executor's scoping-reverted red is `assert 200 == 404` (build log, run locally, not in a gate log). 13b `test_rating_read_is_required`: 403; RED2 `404 == 403` | MET. 13a was a vacuous pass at run 1 (the unsaved algorithm made the service's own `NOT_FOUND` answer with or without scoping); cured in-slice, the lead's verdict "FIX BEFORE MERGE" |
| 14 writes nothing | `test_the_route_writes_nothing`: status, `change_summary`, `evidence`, `updated_at`, Audit Event count and Job count equal before and after a 200 | MET. Note: the call uses empty pins, so the rate-table diff path's no-write is shown only by item 15's Job count (the lead: LOW, accepted) |
| 15 parquet pair pending | `test_a_parquet_table_answers_200_with_the_entry_pending`: 200, `pending` True, `diff` None, Job count unchanged. At run 1 it failed in setup (`RateTableVersionRow.version` does not exist; the column is `version_number`), so run 1's RED2 for it was the wrong cause. Fixed (`.version_number`); run 2 RED2: `assert 404 == 200` by cause | MET; proposed GAP → CURED IN-SLICE (found in this audit; the lead: FIX BEFORE MERGE) |
| 16 contract | `docs/contracts/openapi/generated.json`: `GET /api/v1/rating-versions/{rating_version_id}/change-summary-draft`, 200 `$ref` `ChangeSummaryDraft`, 401/403/404/409/422 `ProblemDetail`; `RateTableChange`, `AlgorithmDiff`, `RateTableDiff` and `ArtifactRef` by `$ref`. `generate-contracts.py --check` rc 0 in run 2 ("48 generated contracts match the models") | MET at `71cc28ae`; the merge of `4af5997e` regenerated the file, so the post-merge `--check` is the PR's CI |
| 17 spec text | At this head `grep -c 'change-summary-draft' docs/specs/03-rating-engine.md` is 2 and `grep -cF 'refuses with **409** and this code when the version has no'` is 1. I diffed both lines against RL-1498's text (lines 188 and 206): byte-identical once `<E1 date>` is put back to 2026-10-11. The row sits directly after the `…/submit` row (three-cell form); the clause sits in the `RATING_VERSION_UNPINNED` meaning note | MET |
| 18 audit-docs and req-coverage | Run 2: `req-coverage` rc 0 (FR-242: 2 test files); `audit-docs` rc 1 on check 31 only (gap 1636→9978 and the `created` order), both mint artefacts. At this head, after the mint: `audit-docs.py` rc 0 "All checks passed" (mine, above) | MET |
| 19 two-half gate | Run 1 (`07830ca6`) rc 1: 15 pytest reds (13 mint artefacts, 2 own: items 15 and 10) and 1 frontend red (`DagDesigner.test.ts`, F39, fixed on main by #1283, not this slice's). Run 2 (`71cc28ae`, tree `a29278a7`) rc 1: ruff, mypy, import-linter, req-coverage, contracts and every frontend stage rc 0 (689 of 689 tests); pytest 13 failed, 5609 passed, 5 skipped. I read the 13 names in `pytest.log`: all audit-docs-derived (`test_audit_docs_finding_citations` 1, `test_audit_docs_ids` 2, `test_audit_docs_process_core_digest` 2, `test_audit_docs_w37_11_ceiling` 1, `test_doc_index` 1, `test_register_lint` 3, `test_register_owed` 1, `test_repository_invariants` 2) and each wraps an `audit-docs.py` failing on check 31 alone | CARRIED (from-lead "2026-10-11 22:44:45 BST": green modulo the mint artefacts). The mint is done and `audit-docs` is rc 0 at this head. Run 2's tree is not this head's: `git diff 71cc28ae cd403d41 --stat` over the slice's source, tests and spec files prints nothing; what changed is the merge of `4af5997e` (SL-1526), the regenerated `generated.json` / `docs/INDEX.md`, the mint and the ledger. The merged-tree gate is the PR's CI |

**Ledger two-way match, reachability.** Every SHA the ledger names as evidence is an ancestor of the head (`git merge-base --is-ancestor <sha> cd403d41`, rc 0): `07830ca6`, `71cc28ae`, `372fa92a`, `4af5997e`, `99f22479`.

**Write set against PL-1502.** `change_summary.py` (new), `rating_versions.py` (`draft_change_summary_for` and `_pins_by_slug` after `_baseline`, plus imports; no existing definition edited), `api/models.py` (one handler after the submit handler), `model_schema/rating.py` (`RateTableChange`, `ChangeSummaryDraft`), `03` §5.1 (T1, T2), `generated.json`, the two test modules, this ledger, `docs/INDEX.md`, plus the closing acts (`PL-1502` `active`, the `SL-1503` row, `docs/roadmap.md`). Nothing in the plan's "Not written" list is touched (`submit_for_review` and its handler, `_baseline`, `rate_tables.py`, `pricing-core`, `errors.py`, the frontend). The range prints 12 files.

**API ACK standard.** Request: `GET`, no body, the path `rating_version_id` as a `UUID` (422 published). Response: 200 `ChangeSummaryDraft` by `$ref`; `RATING_VERSION_UNPINNED` 409 and `NOT_FOUND` 404 published through `problems(401, 403, 404, 409, 422)`. The route needs `rating:read`, the permission the rate-table diff route also needs (`RatingReadDep`), so nothing is widened. The `PlatformError` texts are fixed literals plus the missing field name or an `ArtifactRef`; no exception text. `InputFreeError` is not adopted (from-lead "2026-10-11 20:26:27 BST"): CARRIED.

**Closing acts, checked on `cd403d41`.** LG-1642 `status: closed`, `created: 2026-10-11`, minted from working id 9978 (the front matter's `tree:` still reads the base `99f22479`, a note); the `SL-1503` row `status: closed` with a dated line; `PL-1502` `status: active`; "### Gate" carries both runs; "## PRs" names #1285; "MERGE-ACK: not yet given" stands until the lead's ACK. Not mine to write: any FD or register row (none proposed). The barred-word rule: no hit in the added hunks I read.

**CI on #1285 at `cd403d41`** (read with the bashrc token at 2026-10-11 ~22:5x BST): `history-policy` / `no-session-links` SUCCESS; `docs` / `specification audit`, `frontend` / `check` and `python` / `ruff · mypy · import-linter · pytest` IN_PROGRESS, not yet read to the end. The merged-tree CI is the proof for items 16 and 19 on this tree.

**Findings proposed:** none. Three own test defects (items 15, 13a, 10) were found by this audit and the gate and cured in-slice, each with a valid red by cause; no FD (the lead, from-lead "2026-10-11 20:53:27 BST" and "21:13:13 BST"). Overall proposal: clean once #1285's CI is green on this tree — items 1–9, 11, 12, 13b, 14, 16, 17, 18, 20 MET; items 10, 13a and 15 GAP → CURED IN-SLICE; item 19 CARRIED (mint artefacts), proven by the PR's CI.

Lead verdict (team-lead, from-lead 2026-10-11 20:50:16 BST): CLEAN; no FD; item 19 discharged by green CI at the merge head.

### Build log

#### 2026-10-10 23:50 BST — worktree, Task 0, first commit

- Worktree `.claude/worktrees/sl-1503`, branch `sl-1503-wk673-e1-change-summary`, cut from `origin/main` = `99f22479a20e7fa64f8b6654e0d371c595b1e35a` (WK-675 S3 merged; S4 and SL-1600 not).
- First commit: `PL-1502` status `draft` → `active` (front matter only), `SL-1503` row `draft` → `active` with a dated line, this ledger (L1 (a')).
- **Activation needs** (PL-1502 *Activation needs, in order*): 1 merged and minted, `active` in this commit (met); 2 RL-1498 minted (met); 3 lane: `03` §5.1 SERIALISES with WK-675 S4, so T1/T2 wait (OP-1503-1 (a)); 4 the GO (met, above).
- **RL-1498's T1 and T2 against PL-1502's "As ruled" text:** compared line by line with a script on the T1 row and the T2 clause; each is byte-identical (T1: 1 line in the RL, 2 in the plan, the last equals the RL; T2 the same). The plan's other copy, the Appendix P1/P2 proposal, differs from the RL, and the RL governs (Activation need 2). The differences between the proposal and the ruling are those the plan itself names (`Why:` and `Expected impact:`, "Requires `rating:read`.", "and no Job is created", the tail). No Permission column in `03` §5.1 at this base (`grep -n Permission docs/specs/03-rating-engine.md` prints nothing), so the three-cell form applies.
- **Anchors at the base** (`grep -cF`, both required to be 1 by RL-1498): the submit row opening `` | `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval; `` prints `1`; `` > matching pin list (`rate_tables`, `reference_tables`, `models`) at that exact version. `` prints `1`. `grep -c 'change-summary-draft' docs/specs/03-rating-engine.md` prints `0`. Re-run before applying at the post-S4 base.
- **Plan lines that drifted** (plan read at `4d3be141`; here at `99f22479`; the plan's cites are by symbol below):

| Plan cite | At `99f22479` |
|---|---|
| `RateTableDiff` `rating.py:735-747` | `rating.py:1120`; `RateTableDiffCell` follows at `:1142` (SL-1391 merged). The two new classes go after `RateTableDiffCell`, not between the two: the adjacent classes stay together |
| `diff_algorithms` `rating.py:571` | `:976` |
| `_baseline` `rating_versions.py:704-751` | `:1225` (returns a `(row, check)` pair or `None`) |
| `load_rating_version` `:126-150` | `:152` |
| `rate_tables.diff` `:291` | `:438`, still `blob_store` required keyword, `cache`, `portfolio_dataset_version_id` optional; `diff_needs_job` `:400` takes `(database, workspace_id, slug, version, against)` |
| submit handler `api/models.py:1188-1229` | `:1210`; `blob_store: score_api.BlobStoreDep` is at `:1225` |
| `03` §5.1 submit row `:910` / UNPINNED note `:967-970` | rows moved; found by content (anchors above) |
| `errors.py:321` | not edited by this slice |

- **Reuse found in Task 0:** `_algorithm_of` (`rating_versions.py:1138`) loads a version's saved algorithm; the route's service uses it for both sides instead of re-writing the query.
- **Collisions at the base:** `sl-1559-wk675-s4` and SL-1600 are unmerged. This slice's `rating.py` hunk adds two classes with no existing definition edited (one-sided); `03` §5.1 is the held limb. The one-sided paths are named with `git diff -U0 origin/main...<branch>` per file at the ACK request.
- **Slip, disclosed:** one command carried a no-op `(cd /dev/null …)` subshell. It failed; the session's cwd did not move. No other `cd`.

#### 2026-10-10 23:58 BST — Task 2 (pure draft and shape), red then green

- `backend/tests/test_change_summary_draft.py`: ten tests, Acceptance 1–9 and 20.
- **Red, before any code:** `flock -w 300 /tmp/slots/small-test -c "timeout 150 nice -n 19 uv run --directory <wt> pytest -q -p no:xdist backend/tests/test_change_summary_draft.py"` → `E   ModuleNotFoundError: No module named 'app.platform.change_summary'` at collection (`backend/tests/test_change_summary_draft.py:14`), `1 error`, pytest exit 2. Item 1's stated cause.
- Code: `ChangeSummaryDraft` and `RateTableChange` in `model_schema/rating.py`; `backend/src/app/platform/change_summary.py`.
- **First green run: 8 passed, 2 failed, both mine, neither a hidden defect in the other:** `test_a_percentage_is_never_rendered_through_float` asserted `str(float(pct)) not in text`, but `float` renders `0.1`, a substring of the exact string, so the test could not pass; replaced by an assertion on the full digits (`change <pct>%`). `test_no_change_says_so` found two lines, not the plan's one sentence "No structural change. No rate-table change."; the code now writes the sentence as one line when both are empty.
- **Green:** same command → `10 passed`; `ruff check` and `ruff format --check` clean on the three files.

#### 2026-10-11 00:05 BST — Task 3 authored (service, route, H tests) and contract regenerated

- `rating_versions.draft_change_summary_for(database, *, blob_store, workspace_id, rating_version_id)` after `_baseline`; the pure draft is `change_summary.draft_change_summary`. It reuses `_baseline`, `_algorithm_of`, `diff_algorithms`, `rate_tables.diff_needs_job` and `rate_tables.diff(..., blob_store=, cache=None)`; no existing definition edited. Refusals are `PlatformError` with fixed authored text (`RATING_VERSION_UNPINNED` 409 naming `algorithm_ref` or `pins`; `NOT_FOUND` 404 for a saved-algorithm miss); no `str(exc)` in any message. SL-1600's `InputFreeError` is not on main, so the plain form stands.
- Handler `draft_rating_version_change_summary` in `api/models.py` after the submit handler, `requires(Perm.RATING_READ)`, `responses=problems(401, 403, 404, 409, 422)`, return type `ChangeSummaryDraft`.
- A baseline with no pins is treated as pinning no tables (every pinned table reads `added`); a baseline with no approved earlier version gives no tables and no diff.
- `backend/tests/test_rating_version_change_summary_route.py`: Acceptance 10–15 (the 12th parametrised over both missing fields). **They did not run**: DB-backed, so they wait for the gate slot, and this worktree's database does not exist yet. **Red-first for H is OWED, not shown:** the code was written before any run. In the slot window the red is produced by running the file on the tree with `backend/src` reverted to the base (`git -C <wt> diff origin/main -- backend/src` applied in reverse in a scratch copy, never by stash), expecting item 10's router 404, and the line is recorded here.
- `uv run python scripts/generate-contracts.py` → wrote `docs/contracts/openapi/generated.json` (+219 lines, the route and `ChangeSummaryDraft`/`RateTableChange` by `$ref`); `--check` rc 0 ("47 generated contracts match the models"); `backend/tests/test_contracts.py` 157 passed, 2 skipped (small-test slot).
- ruff check clean on every file touched. `ruff format --check` on `rating_versions.py` fails on lines this slice did not write (the file was not formatted upstream), so the formatter was not run on it.

#### 2026-10-11 00:20 BST — audit-docs and INDEX

`doc-index.py` regenerated `docs/INDEX.md`; `audit-docs.py` (under `gate-2`, per the lead) fails only check 31 ("gap in the full allocation between 1607 and 9978"), the expected red of a working id until the mint. Two earlier reds were mine and fixed: check 22 (a pipe inside a table cell) and check 37 (the missing `PRs` section).

#### 2026-10-11 20:2x BST — re-seat: merge of `origin/main` `372fa92a`, T1/T2 applied

- Authority: `to-lead.md` "2026-10-11 20:17:38 BST" item 5 (SL-1503 unblocked: WK-675 S3 `#1271` and S4 `#1281` on main), with "2026-10-10 21:41:05 BST" item 3.
- `git merge-tree --write-tree origin/main 8f289c60` was rc 1: conflicts in `docs/INDEX.md` and `docs/contracts/openapi/generated.json` only, both generated. Resolved by script, not by hand: `generate-contracts.py` (then `--check` rc 0, "48 generated contracts match the models") and `doc-index.py`. `rating_versions.py`, `model_schema/rating.py` and `roadmap.md` auto-merged; the `rating_versions.py` and `rating.py` hunks were read: this slice's hunks are the added imports, `draft_change_summary_for` and `_pins_by_slug` after `_baseline`, and the two classes after `RateTableDiffCell`; no existing definition is edited.
- **T1/T2 applied by content** (RL-1498 governs; the date placeholder is the apply date 2026-10-11). Anchors matched before the insert, each `grep -cF` = 1: the line starting `` | `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval; `` (now line 1027; the table is still the three-cell form `Method | Path | Purpose`, no `Permission` column) and the line `` > matching pin list (`rate_tables`, `reference_tables`, `models`) at that exact version. `` (now line 1098, inside the `RATING_VERSION_UNPINNED` meaning note). Drift: only the line numbers. After: `grep -c 'change-summary-draft' docs/specs/03-rating-engine.md` prints 2; `grep -cF 'refuses with **409** and this code when the version has no'` prints 1; each inserted line equals RL-1498's T1/T2 byte for byte once its date is put back to `<E1 date>`.
- Messages: this slice's `PlatformError` texts are fixed literals plus the pin name or an `ArtifactRef`; no `str(exc)` or `{exc}` in the diff. `InputFreeError` (`model_schema/input_free.py`) is a validator `ValueError`; this slice adds no validator and no `raise` in `model_schema`, so it has no use here.
- Small proof (`run-small.sh`): `test_change_summary_draft.py` 10 passed; `ruff check` clean and `mypy` clean on the touched source files.
- `audit-docs.py` (under `gate-2`): fails only check 31 (working id 9978 until the mint), as before.

#### 2026-10-11 21:2x BST — first gate @07830ca6 (rc 1), three own test defects fixed

- **First gate**, `gate-1` 20:26:36–21:11:54, HEAD `07830ca614782bf9cfb6c63c2e99877b4d9cce55`, tree `b70bf15b8f3b2743b85caffc5b29ee2bc1795b19`: ruff, mypy, import-linter, req-coverage, contracts and every frontend stage except `fe_test` rc 0; `pytest` 15 failed / 5607 passed; `audit_docs` rc 1 on check 31 only (the working id). Of the 15: 13 are the audit-on-tree modules (mint artefact, check 31) and 2 are this slice's own (below). `fe_test` failed 1 of 689: `DagDesigner.test.ts` "emits an edited draft and leaves the other steps as they were" (F39, WK-675's; the rate-table-free file). Run alone once on this tree under `small-test`: 1 file, 4 passed.
- **Red-firsts of that run, classified.** RED1 (whole feature reverted, pure-draft file): collection error `ModuleNotFoundError: No module named 'app.platform.change_summary'`, by cause. RED2 (handler only reverted, route file): 7 failed, 1 passed; items 10, 11, 12 (both params), 13b and 14 failed on the router's 404 (`404 == 200/409/403`), by cause; item 15 failed on an `AttributeError` in the test's setup, the wrong cause (defect 1 below), so it was not a valid red; `test_another_workspaces_version_is_404` PASSED at red, a vacuous pass, not a red (defect 2). RED3 (refusal check removed): both item-12 params failed, but by 500 (`pins` None: `ArtifactRef` validation) and by 404 `Rating algorithm not found` (`algorithm_ref` None), not by a 200; weak but valid, accepted as a note (from-lead 2026-10-11 21:13:13 BST).
- **Defect 1 (item 15), from-lead "2026-10-11 20:53:27 BST":** `RateTableVersionRow.version` does not exist; the column is `version_number`. Fixed. Green: 2 passed with item 13a's (`run-small.sh`, one file). Red by cause: handler reverted to `origin/main`, `-k parquet`: `assert 404 == 200`, the router's 404.
- **Defect 2 (item 13a), from-lead "2026-10-11 20:53:55 BST":** the other-workspace version named `minimal@1`, never saved, so the service's own algorithm `NOT_FOUND` answered whether or not workspace scoping existed. The test now saves the algorithm for the caller (so with scoping removed the draft would be built and answer 200) and asserts the title `Rating version not found`. Saved in the caller's workspace only: that is the workspace the service would read the algorithm from. Red by cause: `if row is None or row.workspace_id != workspace_id:` replaced by `if row is None:` in `load_rating_version`, `-k another_workspaces`: `assert 200 == 404`. Restored by `git checkout -- <file>`, never by stash.
- **Defect 3 (item 10), DISCLOSED DEVIATION** (from-lead "2026-10-11 21:13:13 BST"; confirmed by the maintainer in `to-lead.md` "2026-10-11 21:13:52 BST" as a disclosed deviation in this ledger, not an RL). PL-1502 Acceptance 10, verbatim: "`test_wf699_e1_the_draft_is_built_from_the_approved_baseline`. v1 approved (its `rating_version.approved` Audit Event written); v2 a draft whose algorithm adds a step and re-pins one inline table to a version with changed cells. `GET …/change-summary-draft` on v2 answers 200; `baseline` is v1's ref; `structural_diff` equals `diff_algorithms(v1, v2)`; the one rate-table entry's `diff` equals `GET /api/v1/rate-tables/{slug}@{v}/diff?against=<v1's>`." Its premise, a synchronous 200 from that diff route, has been stale since SL-1391/RL-1418: `backend/src/app/api/rate_tables.py:398-401` documents **202** with a `rate_table.diff_cells` Job where the query's artifact is not yet stored, "for either storage", and `diff_from_artifact` (`platform/rate_tables.py:750-776`) makes the first request for a key the Job, rows pairs too. The test's cross-check therefore failed `202 == 200` after the draft call itself had passed (200, baseline, structural diff, `pending` false). Option B (21:13:13) taken, and it was feasible, so option A's fallback reason does not arise: the test runs the Job to its end through `test_api_rate_tables._diff_ready` (the helper that file's own tests use), then asserts the entry's diff equals the route's 200 body (`entry["diff"] == table_diff.json()`), and `changed_cells == 1`. The old assertion's red is the first gate's `202 == 200` line above; with the handler reverted the same test fails on the router's 404 (RED2). The draft itself is unchanged: rows pairs are computed by `rate_tables.diff` (DP-E1-2), parquet pairs are `pending`. Not ours, filed as FD 9797 for D13 (owner WK-675): the stale "rows-only pair stays on the synchronous 200 path" docstrings at `platform/rate_tables.py` (`diff_needs_job`) and `test_rate_tables_service.py`.
- **After the fixes:** `test_rating_version_change_summary_route.py` 8 passed (`run-small.sh`, the worktree's database); `ruff check` clean on it. `ruff format --check` flags layout the gate does not check (the gate runs `ruff check`); not changed.

## PRs

- PR #1285, `sl-1503-wk673-e1-change-summary`.
