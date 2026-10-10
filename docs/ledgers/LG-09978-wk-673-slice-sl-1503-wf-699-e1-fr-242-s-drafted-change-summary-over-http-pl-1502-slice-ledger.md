---
id: LG-9978
family: ledger
title: WK-673 slice SL-1503 — WF-699 E1, FR-242's drafted change summary over HTTP (PL-1502), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-673
slice: SL-1503
plans: [PL-1502]
corrected_by: []
relates: [PL-1502, RL-1498, RL-1445, RL-1263, SL-1389, SL-1391, FR-242, FR-219, FR-231]
---

# LG-9978 — WK-673 slice SL-1503: WF-699 E1, FR-242's drafted change summary over HTTP

*(LG-9978 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1503` from PL-1502, base `origin/main` `99f22479a20e7fa64f8b6654e0d371c595b1e35a`.
Times are BST (`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md` "2026-10-10 21:41:05 BST — RL-1445 CAP: AMENDED by dated line (counting unit = gate or measurement, with guard rails); GO SL-1541 (WS-1 (a)); OP-1503-1 (a); SL-1575 noted", item 3: "OP-1503-1: (a) ADOPTED. SL-1503 authors now. Its 03 §5.1 hunks (T1/T2) are applied after WK-675 S3 and S4 have merged, on main, re-anchored by content. Needs 1 (merge-only) and 4 (this GO) are MET with this entry."
**MERGE-ACK:** not yet given.

## Tasks

| Task | Plan step | Acceptance | Status |
|---|---|---|---|
| 0 | preconditions | — | done (below) |
| 1 | `03` §5.1 T1, T2 | 17 | HELD: applied only after WK-675 S4 merges (WK-675 S3 has: `99f22479`) |
| 2 | shape and pure draft | 1–9, 20 | done |
| 3 | service and route | 10–15 | open |
| 4 | contract, gate, ledger | 16–19 | open |

### Gate

Not run. The full two-half gate waits for the lead's "gate slot granted" for the head.

### Audit

Not yet. The auditor writes it.

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
| `_baseline` `rating_versions.py:704-751` | `:1225` (returns `tuple[RatingVersionRow, GoldenQuoteCheck | None] | None`) |
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
