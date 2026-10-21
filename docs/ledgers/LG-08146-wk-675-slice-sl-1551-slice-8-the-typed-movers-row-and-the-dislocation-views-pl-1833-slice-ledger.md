---
id: LG-8146
family: ledger
title: WK-675 slice SL-1551 — Slice 8, the typed movers row and the dislocation views (PL-1833) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: 57adb9e2
phase: P2
work: WK-675
slice: SL-1551
plans: [PL-1833, PL-1546, PL-1286]
corrected_by: []
relates: [PL-1833, PL-1546, PL-1286, SL-1551, SL-1388, SL-1369, SL-1260, SL-1275, SL-1554]
---

# LG-8146 — WK-675 slice SL-1551: Slice 8

Filed 2026-10-21 under working id 8146 (lead-reserved). Executor seat `exec-1551`, base `origin/main` 57adb9e2, branch `sl-1551-wk675-s8`, worktree `.claude/worktrees/sl-1551`.

**GO:** the maintainer's (by delegation) entries in `to-lead.md`: "2026-10-21 15:10:53 BST" items 1 and 2, and "2026-10-21 15:50:30 BST" ("GO SL-1551 (S8) per 15:10:53 — census its remaining needs first"). Dispatch: the lead's DISPATCH RECORD — SL-1551, `from-lead-2026-10-09.md`, "2026-10-21 15:56:11 BST". Census: `handover/census-planner-1551-2026-10-21.md`. **MERGE-ACK:** not yet given.

## Scope

`PL-1833` (active, #1355): Task 1 (the typed movers row, spec first, then `model-schema`, route, contracts, tests red-first), then Task 2 (the views at `/rating/:slug/v/:version/dislocation`). DP-S8-1 (a) and DP-S8-2 (a) are ruled. Acceptance 5 (order gate) holds the movers row before any frontend read of `/movers`.

## Binding file conditions (dispatch record)

- S8 does not edit `frontend/src/views/RatingDesignView.vue`, the designer components, or any sub-graph api module (those are `SL-1554`'s, S9).
- Shared files, append only, no existing entry edited: `frontend/src/router/index.ts` (with `SL-1275`), `docs/specs/03-rating-engine.md` §5.1 (with `SL-1260`). Whichever of each pair merges later re-merges `origin/main` and re-runs its generators and checks. Both are recorded here; the exact appended entries are listed under Shared-file edits below.

## Needs census (on main 57adb9e2)

`SL-1369` (S1) closed; `SL-1388` closed; `PL-1833` active; `SL-1550` (S7) closed. The typed movers row is in-slice (Task 1), not an activation need.

## Tasks

Task rows are appended here as each task starts.

- **Task 1 (the typed movers row), written 2026-10-21 on `origin/main` 57adb9e2 + the activation commit e14f88b5.**
  Order: spec (`03` §4.6 `change_pct` sentence, §5.1 `/movers` row) → red tests → code → contracts.
  - Spec: `docs/specs/03-rating-engine.md` §4.6 "Bands and movers" gains the dated `change_pct` rule (DP-S8-2 (a)); the §5.1 `/movers` row names `DislocationMover`.
  - Red first (small runs through `run-small.sh`, tree = this worktree): `packages/model-schema/tests/test_dislocation.py` and `packages/pricing-core/tests/test_rating_dislocation.py` both failed at collection with `ImportError: cannot import name 'DislocationMover'` / `'mover_change_pct'` (rc 2) before any code. Then 67 passed (rc 0).
  - Broken-input runs of the rounding (Acceptance 7): with the helper mutated to **truncation**, 5 failed (`[1-3-33.333334]`, `[-1-3--33.333334]`, `[2-3-66.666667]`, `[1-7-14.285715]` and the edge-of-threshold test `test_a_selected_movers_change_pct_never_reads_below_the_threshold`); mutated to **half-even** (`round(Fraction)`), 4 failed (the same minus `[2-3-66.666667]`, which rounds up under half-even too). The helper was restored from a saved copy; `git diff` of `analysis.py` shows only the added function, `__all__` entry and constant.
  - Code: `model_schema/dislocation.py` `DislocationMover` and `JsonScalar` (exported in `__init__.py`); `pricing_core/rating/analysis.py` `mover_change_pct` (the exact-fraction helper lives beside `select_movers`, whose threshold test it must agree with); `backend/src/app/api/dislocation_runs.py` `_mover` / `_json_value` (a date or datetime becomes its ISO string; any other non-scalar value is a `VALIDATION_FAILED` 422, not a widened type).
  - Backend route test `test_movers_route_joins_the_portfolio_columns_at_read` (`backend/tests/test_dislocation_runs.py`, `FR-263`, `NFR-499`) now asserts the typed fields against the stored blob, the joined columns under `columns`, and `change_pct` recomputed independently from the stored integers. **DB-backed: not run (no DB grant); owed.**
  - Contracts: `uv run python scripts/generate-contracts.py` rc 0, `--check` rc 0; the `/movers` 200 schema prints `items: {'$ref': '#/components/schemas/DislocationMover'}`. `pnpm --dir frontend generate:api` rc 0 (`schema.d.ts` carries `DislocationMover`; the generated dir is VCS-ignored).
  - `ruff check .` rc 0; `mypy` rc 0 (244 files); `lint-imports` rc 0.

- **Task 2 (the views), written 2026-10-21 after Task 1 (commit 4496daeb).** Frontend: `api/dislocationRuns.ts` (generated types only; `DislocationMover` is a `components[...]` alias), `components/dislocation/{ChangeHistogram,SegmentGrid,AttributionWaterfall,LargestMovers}.vue` + `format.ts`, `views/DislocationView.vue` (route `/rating/:slug/v/:version/dislocation`, run cited in `?run=`), the route entry (inserted before the sandbox route; no existing entry edited), and a link from `RatingVersionView.vue` (FR-25: `router/__tests__/reachability.test.ts` was red on the new route until the link existed). Tests: `components/dislocation/__tests__/dislocation.test.ts`, `views/__tests__/DislocationView.test.ts`, one added case in `RatingVersionView.test.ts`.
  - Frontend checks on this tree: `pnpm lint` rc 0, `type-check` rc 0, `test` rc 0 (127 files, 813 tests), `build` rc 0.
  - Acceptance 5 (order gate): `A` = 4496daeb (first commit adding `DislocationMover` in `packages/model-schema/src`), `B` = b594fa50 (first frontend commit matching `movers`); `git merge-base --is-ancestor A B` rc 0. The broken-input run (a branch whose first frontend `movers` commit precedes `A`) was not run.
  - Acceptance 6: `grep -rlE 'FR-26[3-6][^0-9]' frontend/src --include=*.test.ts` prints a file for each of FR-263, FR-264, FR-265, FR-266 (checked per id); the route test carries `@pytest.mark.req("FR-263")`.
  - Acceptance 8: the `accessibility-tester` report (static read only, no browser or screen reader), findings and what was done: (1) waterfall increase/decrease separated only by default series palette — **fixed**: explicit colours, "+"/"−" bar labels, and a "Direction" column stating Increase/Decrease in words; (2) direction in the table rests on a bare minus sign — **fixed** by the same Direction column; (3) live regions inserted already filled (`v-if`) — **fixed** in `DislocationView.vue`: the status and alert regions are persistent and only their content changes (the movers-refused `role="status"` notice is still `v-if`, not changed); (4) no focus move after "Show run", no `aria-describedby`/`autocomplete` on the id field — **open, low**; (6) page jumps `h1` → `h3` (`ChartFigure.vue` is shared and pre-existing) — **open, low**; (7) focus-ring visibility, contrast of `text-slate-500`/`text-blue-700`, the ECharts palette, 200 % reflow of the 7-column movers table, real screen-reader output — **not verifiable by static reading, owed**.
  - Not run: the DB-backed route test (needs a DB grant), `backend/tests/test_contracts.py` (run-small refused at load1 15.8 and 6.28), the full two-half gate (needs the lead's slot).

## Shared-file edits

- `docs/specs/03-rating-engine.md` §5.1: **no new row; one dated sentence appended to the end of the existing `/movers` row's description cell** (the row is S8's own subject; `PL-1833` Task 1.1 requires §5.1's `/movers` row to name `DislocationMover`). Nothing earlier in the row or any other row changed. SL-1260 (RL 8142) adds its own routing and shadow rows: the later of the two re-merges. This reads the dispatch condition "append only" as satisfied by appending within the row; reported to the lead.
- `frontend/src/router/index.ts`: **one new route entry `rating-dislocation` inserted as a whole object before the existing `quote-sandbox` entry; no existing entry edited.** SL-1275 also appends to `routes`: the later of the two re-merges.

## Rulings recorded (lead 22 relays, 2026-10-21)

- **Closing act (maintainer, to-lead "2026-10-21 15:56:56 BST"):** the stale `docs/roadmap.md` SL-1551 paragraph ("Activation need added 2026-10-10 … the typed movers row in `model-schema` is merged") is corrected in S8's CLOSING commit, not in the activation commit. Owed at close.
- **`03` §5.1 append (maintainer, "2026-10-21 16:09:34 BST"):** the dated sentence appended inside S8's own `/movers` row is accepted as within "append only". Condition: each appended sentence carries its dated amendment tag. Confirmed at `b594fa50`+: the §5.1 `/movers` row carries "Amended 2026-10-21, WK-675 Slice 8, PL-1833" and the §4.6 "Bands and movers" addition carries "Amended 2026-10-21, WK-675 Slice 8, PL-1833, DP-S8-2 (a), the maintainer's 2026-10-17 19:41:48 BST entry" (`git grep -c` on `03-rating-engine.md` prints 2 lines). Whichever of SL-1551 and SL-1260 merges later re-merges and re-runs its checks.
- **Flags accepted ("2026-10-21 16:23:35 BST" item 2):** (a) the `rating-dislocation` route entry is inserted before the `quote-sandbox` entry because order matters to route matching, and no existing entry is edited; (b) the `RatingVersionView.vue` link is a write-set addition for FR-25 reachability (`reachability.test.ts`); S9's no-edit list is untouched. **For S10's (SL-1552) leaf note:** S10 later removes this interim link path.
- **DB grant:** the DB route test's grant comes from lead 23 after this END is relayed.
- **Post-merge checks and the owed runs (exec-1551c, 2026-10-21, at head `3189bac2`, merge of origin/main `c35113b2`):** `generate-contracts.py --check` rc 0 (54 contracts match); `pnpm --dir frontend generate:api` rc 0; under the gate-2 flock `audit-docs.py` rc 1 with the one expected red, check 31 ("gap in the full allocation between 1836 and 8146"), `doc-index.py --check` rc 0, `register-lint.py` rc 0. `backend/tests/test_contracts.py` via run-small: rc 0, 172 passed, 2 skipped. DB window (grant: to-lead "2026-10-21 20:29:56 BST" and the lead 25 brief): database `gipricing_sl-1551_fa60f852` (the name `conftest_db.py` derives from the worktree path; created `-T template0`), one `alembic upgrade head` rc 0, `alembic current` = `alembic heads` = `a4d1f08c3b97`; Redis db 13 only. `backend/tests/test_dislocation_runs.py` via run-small (file form; it holds `test_movers_route_joins_the_portfolio_columns_at_read`): run 1 rc 0, 24 passed. END: `dropdb` rc 0, `pg_database` count 0, db 13 `FLUSHDB` then `dbsize` 0.

## PRs

None. The slice stops at PR-READY; the lead opens the PR.
