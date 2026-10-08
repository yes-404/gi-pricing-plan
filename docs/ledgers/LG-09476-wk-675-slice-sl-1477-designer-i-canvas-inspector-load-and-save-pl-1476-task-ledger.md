---
id: LG-9476
family: ledger
title: WK-675 slice SL-1477 — Designer I, canvas, inspector, load and save (PL-1476), task ledger
status: active
created: 2026-10-08
owner: executor
tree: adfa6e7671d98aadf41536714b2da41b1e00c1ae
phase: P2
work: WK-675
slice: SL-1477
plans: [PL-1476]
corrected_by: []
relates: [RL-1473, RL-1474, RL-1475, RL-1263, FD-1366, RS-1269, WK-675]
---

# WK-675 slice SL-1477 — Designer I: canvas, inspector, load and save

Executed from `PL-1476` by `executor-s2` (sonnet). Branch `sl-1477-designer-i-canvas-inspector-load-and-save`, worktree
`.claude/worktrees/sl-1477`, from `origin/main` `d10420df` (#1241, the activation; tree `adfa6e76`). The dispatch record is
`gi-pricing-plan.local/handover/DISPATCH-WK-675-SL1477-2026-10-08.md` (FINAL; a local file, not in the repository). Stamps
are BST (`TZ=Europe/London date`). `uv sync --all-packages` and `pnpm --dir frontend install --frozen-lockfile` ran.
Test database `gipricing_sl-1477_d7eee10d`, made with `docker exec gi-pricing-postgres-1 createdb -U gipricing -T gipricing …`
and migrated with `alembic upgrade head`.

## Tasks

### Task 0 — preconditions (2026-10-08 12:17 BST)

Rows 0.1–0.11 re-run at `d10420df`; every row matches, with these line moves (the dispatch record's table, confirmed):

| Anchor | At `d10420df` |
|---|---|
| `class RatingAlgorithm` | `rating.py:423` |
| `list_rating_versions` / `get_rating_version` | `models.py:1110` / `:1136`; its decorator `:1131`; insert between `:1128` and `:1131` |
| `rating_algorithms.py` | 69 lines; `Any` `:10`, import `:18`, `body: dict[str, Any]` `:35`, return `:38` |
| `resolve_rating_version_ref` / `to_schema` | `rating_versions.py:172` / `:96` |
| `get_algorithm` / `create_algorithm` | `platform/rating_algorithms.py:135` / `:94` (unchanged) |
| `03` anchors, each `grep -cF` = 1 | FR-243 `:140`, FR-219 `:88`, `POST /sub-graphs` `:931`, `POST /rating-versions` `:943`, Vue Flow row `:1365`; header `:927`, diff row `:930`, compile row `:944` |
| `manualChunks` | function form `vite.config.ts:26`, echarts only |
| `skills-map.md` Vue Flow row | `:121` |

- **0.1:** `[False, False, False]`. **0.3:** `grep -rn UNTYPED_REQUEST_PENDING backend scripts` prints nothing: SL-1367 has not
  landed, so there is no guard entry to remove in Task 2. **0.4:** `vue-flow` count 0. **0.6:** no `/rating/` route.
  **0.8:** the header is three-cell, and `grep -n 'Purpose . Permission'` prints nothing: the three-cell forms apply.
  **0.10:** `seed.py` has no `algorithm_ref` or `rating-algorithms`.
- **0.7:** `uv run pytest backend/tests/test_rating_algorithms.py -q`: **10 passed**, 1 warning (both gate slots free).
- **Step 4:** `grep -c 'Read one Rating Version by .id., the handle' docs/specs/03-rating-engine.md` prints 0: Task 4 applies
  the by-id row as well as the `slug@version` row.
- **`pnpm-lock.yaml`** differs from goC's tree `0ee8f414` (#1237); the branch is cut after it, and `pnpm add` writes the lock.

**Step 2 — the minted rulings against the cited heads.** RL-1473 against `39bd865b` (`RL-09766-…`), RL-1474 against
`39bd865b` (`RL-09767-…`), RL-1475 against `96fa35bf` (`RL-09753-…`), by `git diff` of the two blobs after the id
substitution. Differences, and only these: the `created:` line, the mint note, working-id citations re-pointed to minted ids,
and dated amendments of 2026-10-05 (citation re-reads at `809a3794`; RL-1475's T4 re-anchor, which is S4's). The T-texts S2
applies — RL-1473 T1 and T2, RL-1475 T1 and T2 — are unchanged. RL-1474's ruled item 1 is unchanged.

**Step 3 — SL-1391 (S7).** It has merged (`a9ef6777`, #1206), so its `03` edits are in the base tree: the anchors above were
found once each at `d10420df`. No conflict with S2's `03` hunks.

**SL-1448 (#1236).** Not merged at the dispatch tree: FR-221 still reads unamended. The inspector's `as_at` tests are
written after it lands, to its narrowed FR-221.
### Task 1 — `RatingAlgorithmDraft` and `RatingAlgorithmSaved` (model-schema)

Test module `packages/model-schema/tests/test_rating_algorithm_draft.py` as PL-1476 gives it; the fixture's literals checked
against `rating.py` (`decimal`, `money_minor` and the step fields are accepted). Slots free before each run.

- **Red** (before any code): `uv run pytest packages/model-schema/tests/test_rating_algorithm_draft.py -q` — collection error:
  `ImportError: cannot import name 'RatingAlgorithmDraft' from 'model_schema'`. The stated cause.
- **Green:** the field set moved to `RatingAlgorithmDraft`; `RatingAlgorithm(RatingAlgorithmDraft)` keeps its validator and
  helpers; `RatingAlgorithmSaved` added; both appended to `__init__.py` and `__all__`.
  `test_the_draft_accepts_a_graph_the_algorithm_refuses`, `test_the_field_set_is_written_once`,
  `test_the_draft_still_refuses_an_unknown_field`, `test_the_saved_shape_is_the_201_wire` pass.
  `pytest packages/model-schema -q`: 514 passed. `test_sub_graphs_api.py` + `test_sub_graphs_service.py` + the new module:
  45 passed. `ruff check packages/model-schema` and `mypy` clean.

## PRs

The slice PR is a draft, opened by the executor; the executor does not merge it.
