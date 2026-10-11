---
id: FD-1585
family: finding
title: The existing rate-table diff routes answer 404 RATE_TABLE_MISS for an unknown table, version or against, where 03 §5.1 types it 404 NOT_FOUND
status: active
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: auditor
tree: 2ef1393fec8eb0d974eb366f558a42e585771f35
corrected_by: []
relates: [WK-675, RL-1475, RL-1555, PL-1558, SL-1559, FR-231, FR-232]
---

# FD-1585 — The rate-table diff routes answer RATE_TABLE_MISS where the spec says NOT_FOUND

*Disclosure: drafted under working id 9941; minted as FD-1585 on 2026-10-10, in the D6 batch mint PR.*

**DRAFT**, filed on `draft/d6-fd9941-fd9943-process` (no PR), at the lead's ruling in `to-lead.md`, "2026-10-10 04:19:42 BST — RULING: rate-table 404 disagreement = (a), the SPEC governs (NOT_FOUND); the fix is at the route layer; one FD for the pre-existing drift", item 3: *"ONE FD (product; owner WK-675): the existing diff routes on main return RATE_TABLE_MISS for an unknown rate table, against 03 §5.1 :943/:944. Evidence: file:line of each route, the observed code, and the spec text. Remedy: route-layer NOT_FOUND mapping, the same as S4's."* Scope is the ruling's: the two existing diff routes. The entry "2026-10-10 04:23:36 BST — RULING: WK-675 S4 read routes = (a), NOT_FOUND too" fixes S4's own routes in S4 and states that this FD keeps its scope (its item 4).

## Finding

`03-rating-engine.md` §5.1 types an unknown table, version or baseline on the two diff routes as **404 `NOT_FOUND`**. The code answers **404 `RATE_TABLE_MISS`** for the same condition. The status is the same; the `code` field, which a client branches on, is not.

**The spec text**, verbatim from `docs/specs/03-rating-engine.md` at `2ef1393f`:

- `:943`, the row `GET /api/v1/rate-tables/{slug}@{version}/diff?against=&portfolio=`, says only of a ref: *"**404** `NOT_FOUND` for a `factor_ref` or `banding_ref` that does not resolve, naming the key and the ref"*, and, for `portfolio`, *"**404** `NOT_FOUND` for a portfolio that is missing or in another workspace"*. It states no code for an unknown table or version in its own text, so on this row the disagreement rests on the next row's cross-reference and on the ruling; `:944` states it literally.
- `:944`, the row `GET /api/v1/rate-tables/{slug}@{version}/diff/cells?against=&portfolio=&limit=&cursor=`, says: *"`against` and `portfolio` are checked as on the diff row, before any cell is read and before any Job, whatever `storage` either version has: **404** `NOT_FOUND` for an unknown table, version or `against`"*.
- `RL-1555` T1 types the same condition on the editor's routes as `NOT_FOUND`; `RL-1475` T3/T4 and Acceptance 5 (`:274`) name `RATE_TABLE_MISS` for it, which the lead's entry "2026-10-10 04:27:31 BST — RL 9942 scope = (a)" corrects by a correcting record (minted as RL-1584), not here.

**The code**, at `2ef1393f`:

| Route | Handler | Calls | Raises `RATE_TABLE_MISS` (404) at |
|---|---|---|---|
| `GET /rate-tables/{slug}@{version}/diff` | `rate_table_diff`, `backend/src/app/api/rate_tables.py:320` (decorator `:310-311`) | `service.diff_from_artifact`, `:361` | `_load_table` `backend/src/app/platform/rate_tables.py:282` (unknown table); `_load_version` `:1012` (unknown version, and a missing baseline version); `_resolve_baseline` `:951` ("No previous version") and `:984` ("No seed origin"), reached from `diff_from_artifact` at `:789-792` |
| `GET /rate-tables/{slug}@{version}/diff/cells` | `rate_table_diff_cells`, `backend/src/app/api/rate_tables.py:383` (decorator `:373-374`) | `service.diff_cells_page`, `:423` | the same four sites, reached through `_cells_key_for` (`:654`): `_load_table` `:665`, `_load_version` `:666` and `:668`, `_resolve_baseline` `:667` |

The loader's own line, `backend/src/app/platform/rate_tables.py:282`: `"RATE_TABLE_MISS", "Rate table not found", 404, f"{slug} not found."`. Neither handler maps it: `rate_table_diff` and `rate_table_diff_cells` (the `:320-370` and `:383-430` ranges) carry no `try`, no exception mapping, and no reference to `NOT_FOUND`. The portfolio-side refusals on both routes are already `NOT_FOUND` (`backend/tests/test_rate_table_diff_portfolio.py:457`, `:495`, `:841`), so one route answers two codes for two kinds of missing thing.

**Why the code is the side that moves** (the ruling's reasoning, `CLAUDE.md` §0: when code and spec disagree, stop and resolve it). `RATE_TABLE_MISS` is a scoring code: a table lookup failed while pricing, and the shared loader must keep it on the scoring path (`backend/tests/test_worker_raise_sites.py:137-152` registers the loader's four raise sites as scoring-path raises, "not a per-quote miss"). A management route asked for a rate table that does not exist is a missing resource.

## Evidence

All read at `2ef1393f` (the worktree `.claude/worktrees/d6b`, `origin/main`); nothing was run (brief: git and file reads only, no slot-bound check).

1. **Handler ranges:** `sed -n 310,372p` and `sed -n 373,432p` of `backend/src/app/api/rate_tables.py` show the two handlers, each ending in a bare `await service.<fn>(…)` call and a `DiffCellsJobNeeded` branch; no exception handling.
2. **Raise sites:** `grep -n 'RATE_TABLE_MISS' backend/src/app/platform/rate_tables.py` prints `282`, `951`, `984`, `1012`, `1294`; `awk` over the enclosing `def` places them in `_load_table`, `_resolve_baseline` (two), `_load_version` and `bulk_operation`. The `:1294` site is the bulk-operation route, which is **out of this FD's scope** (the spec's bulk-operation row names no code; the ruling names the diff routes).
3. **Tests that assert `RATE_TABLE_MISS` on the two diff routes** (`grep -n 'RATE_TABLE_MISS' backend/tests/test_api_rate_tables.py`, `-B` to the `def`):
   - `test_diff_404s_for_unknown_table_and_version` (`:486`), asserting `missing_table.json()["code"] == "RATE_TABLE_MISS"` at `:505`.
   - `test_diff_seed_without_a_seed_origin_404s` (`:546`), asserting it at `:600` (`_resolve_baseline`'s "No seed origin").
   - `test_import_preview_creates_nothing` (`:981`), whose `_diff_ready(…/diff…)` read asserts it at `:1005`.
   - `test_import_confirm_cannot_override_the_verdict` (`:1048`), asserting it at `:1068`.
   No test asserts the code for `diff/cells` (`grep -n 'diff/cells' backend/tests/test_api_rate_tables.py` prints nothing; `backend/tests/test_rate_table_diff_portfolio.py` reaches `diff/cells` and asserts only `NOT_FOUND`), so that route's `RATE_TABLE_MISS` answer is unpinned and the spec's `NOT_FOUND` is unevidenced.
   `test_bulk_operation_on_a_missing_version_is_refused` (`:868`, asserting at `:878`) is the bulk route and stays as it is.
4. **The remedy exists, one slice over:** on `origin/sl-1559-wk675-s4` @ `cb75b02f724e4dd58d3fdbe5bfc95d1bb23aab17`, `backend/src/app/api/rate_tables.py:69` defines `spec_not_found()`, a context manager that catches `PlatformError` with `code == "RATE_TABLE_MISS"` and re-raises `PlatformError("NOT_FOUND", "Not Found", 404, exc.detail)`; it wraps the S4 routes at `:166`, `:171`, `:443` and `:464`. Its docstring: "The shared loaders keep `RATE_TABLE_MISS`, which the scoring path relies on, so the route maps it here and nothing below it changes."
5. **Where the wrong value was copied:** `RL-1475` (dated 2026-10-08) and `PL-1558` Acceptance 4 took the code's value; the ruling corrects Acceptance 4 by a plan-delta line in S4's ledger. Not checked here: which earlier record first wrote the diff routes' `RATE_TABLE_MISS`.

*Not run:* no test, audit-docs or contract check. An HTTP answer for `diff/cells` was not observed; the claim for it rests on reading the call chain.

## Disposition

**Proposed severity: MEDIUM (the auditor proposes; the lead decides).** Reason: it is a published-contract disagreement on a field a client branches on (`code`), on a route family the rate-table editor and rate-change journeys read; it misprices nothing and the HTTP status is already right, so it is not HIGH. It is not LOW because the generated API client and any caller written to `03` §5.1 will branch on the wrong code, and the cost of changing it grows with each consumer.

**Decision (proposed): fix before close with an owner: WK-675.** Remedy: a route-layer `NOT_FOUND` mapping on `rate_table_diff` and `rate_table_diff_cells`, as `spec_not_found()` does on `cb75b02f`; the shared loader (`backend/src/app/platform/rate_tables.py:282`) is **not** changed, because `RATE_TABLE_MISS` stays correct on the scoring path. Tests: re-point the four assertions above to `404` + `NOT_FOUND`, red at the parent commit; add one for `diff/cells` (unknown table, unknown version, unknown `against`), which has none.

**Fix point:** the next WK-675 slice that touches those two routes, before WK-675's Work close. Per the ruling's item 3, if S4 (`SL-1559`) already touches the routes' module and the fix is under about 20 lines, S4 may include it and say so in its ledger; once S4 lands `spec_not_found()` in `backend/src/app/api/rate_tables.py`, the diff handlers are in the same module and the same helper applies.

**Event that next confirms or discharges it:** the fixing slice's PR, with the re-pointed tests red at its parent commit; or WK-675's Work close audit, which lists this row.
