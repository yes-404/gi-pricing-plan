---
id: LG-9737
family: ledger
title: WK-674 slice SL-1256 — the Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit, NFR-498 for deploy), routes typed both ways, the compile guard of RL-1379 (PL-1392)
status: active
created: 2026-10-03
owner: executor
tree: 8252741cc3849058b6fc6836967448d88ff9821c
phase: P2
work: WK-674
slice: SL-1256
plans: [PL-1392]
corrected_by: []
relates: [RL-1379, RL-1380, RL-1301, RL-1296, RL-1263, FD-1393, FR-267, FR-428, FR-429, FR-272, NFR-498, FR-343]
---

# LG-9737 — WK-674 slice SL-1256, the Environment and Deployment record

Executed from `PL-1392` by `executor-1256` (sonnet, medium: `echo $CLAUDE_EFFORT` printed `medium`). Branch
`sl-1256-environment-and-deployment-record`. Stamps are BST (`TZ=Europe/London date`).

The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the
lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a cheaper setting."

The dispatch record is `gi-pricing-plan.local/handover/DISPATCH-WK-674-SL1256-2026-10-03.md` (FINAL; Conditions 1-8
and Deltas 1-4 bind). It is a local file and is not in the repository.

## Tasks

### Task 0 — preconditions

**Base.** Worktree created from `origin/main` `8252741cc3849058b6fc6836967448d88ff9821c` (#1087, SL-1377, merged),
read at 2026-10-03 22:01 BST; `git fetch origin main` then printed the same SHA. `uv sync --all-packages` ran. Test
database `gipricing_agent-a0f7a7db50ec2ab16_83653597`, created from the template and migrated to head.

**Checks at that SHA.**

- `RL-1296`, `RL-1301`, `RL-1379` and `RL-1380` are files under `docs/rulings/` (listed with
  `ls docs/rulings | grep -E "RL-0(1296|1301|1380|1379)"`, four lines). #974 is RL-1380, minted.
- `docs/roadmap.md`: `SL-1302` `status: closed`; `SL-1300` `status: closed`; `SL-1360` `status: closed`;
  `SL-1367` `status: draft` (not in flight); `SL-1256` `status: active`.
- **Acceptance 8's predicate** (`grep -c -E '^> \| `(deployment:promote|admin:manage_environments)` \|.*\| WK-674 \|$'
  docs/specs/06-governance.md`) prints **2**.
- **`SL-1360` has merged**: `tests/test_permission_parity.py` exists at the repository root, so Acceptance 8's
  `STALE_OWNER` red can be shown (the plan's `backend/tests/` path for it is wrong; the file is `tests/`).
- **In-flight build slices** (`gh pr list --state open`, 2026-10-03 ~22:05 BST): every open PR is docs-only
  (findings, rulings, plans). No build PR touches `score.py`. `executor-1385` (WK-673 S1, lane B) is the concurrent
  build slice; its spec sections and `ONE_SIDED_SLUGS` key (`"dislocation-run"`) are disjoint from this slice's
  (Delta 4).
- **F1 registry serialisation (Condition 2, Delta 3):** `#1087` (SL-1377) **merged first**. This slice re-bumps
  `_CONTRACT_ARTIFACT_PATHS` and the `non_markdown` count on the merged tree, and the contract-schema skill step is
  SL-1377's, not this slice's (verified when Task 2 reaches it).
- **Premises re-derived at `8252741c`:** (a) the only `class .*Environment` is `backend/src/app/config.py:32`;
  `live_deployments` only at `docs/specs/07-platform.md:253`. (b) `"deployment"` in the floor at
  `packages/model-schema/src/model_schema/approvals.py:107`. (d) `uat_deployment` only at `approvals.py:107`.
  (e) `grep -rn -E "(Perm|Permission)\.(DEPLOYMENT_PROMOTE|ADMIN_MANAGE_ENVIRONMENTS)\b" backend/src` exits 1.
  (i) `DEPLOY_REQUIRES_APPROVAL` is in no backend `.py`; `PROMOTION_ORDER_VIOLATION` at `errors.py:70`.
  (o) the Alembic head is `2f598e89d12c` (the only revision no `down_revision` names; 50 files). (p) `03` §4 ends
  at §4.11 `SubGraph` (`docs/specs/03-rating-engine.md:760`; §4.10 moved from `:703` to `:720`, so §4.12 is free).
  (u) no `class (Environment|Deployment|DeploymentRequest|PromotionSkip)` under `packages/model-schema/src` (exit 1).
  Line numbers in the plan that SL-1377 moved are re-found where used. Premises c, f-h, j-n, q-t are re-read at the
  task that uses each.

### Task 0A — the authorisation sweep sees every route

File: `backend/tests/test_api_authorisation_sweep.py` (no sibling: `grep -rn "app.routes" backend/tests` names only this
file, so Acceptance 12 (f) has nothing else to fix).

- **FastAPI probe:** `uv run python -c "import fastapi; print(fastapi.__version__)"` printed `0.141.1`.
  `app.routes` is 29 entries: `Counter({'_IncludedRouter': 23, 'Route': 4, 'APIRoute': 2})`; an `_IncludedRouter` holds
  `original_router.routes` and `include_context.prefix` (`/api/v1`); no router is nested inside another.
- **Red first, (a), predicted cause "the loop does not descend into `_IncludedRouter`":** the equality test over the
  unchanged loop failed with `AssertionError: the static sweep iterated 2 operations; the contract publishes 141`
  (`assert 2 == 141`). With the flattening helper `_flattened_operations` the set of iterated `(method, path)` equals
  the published set (141 operations).
- **Red first, (b):** with the helper's descent disabled (a temporary `original = None`, since restored; `grep -c
  RED-PROBE` prints 0), `test_a_guard_removed_from_a_real_route_is_seen` failed with `StopIteration` (the target route
  `GET /api/v1/datasets` is not seen at all) and the equality test failed `2 == 141`. With the descent, removing
  `requires()` from that route (by `monkeypatch`) makes the sweep return exactly `['GET /api/v1/datasets']`.
- **Static sweep over the flattened surface, run before the allow-list existed:** it named exactly two routes,
  `POST /api/v1/me/workspace` and `POST /api/v1/validation-rules`: the two handler-guarded routes of Acceptance 12 (e).
  `HANDLER_GUARDED` names them with file, line and the text that must be on that line (`validation_rules.py:200`,
  `:207` hold `require_permission(`; `api/me.py:241`, `:251`, `:260` hold `WORKSPACE_SCOPE_DENIED`), and
  `test_the_handler_guarded_routes_still_check_at_their_site` reads each line.
- **(d) the valid-body sweep:** `_request_for` builds the path, required query and JSON body from `app.openapi()`
  (`$ref`, enums, `format` uuid/date/date-time, `anyOf`/`oneOf` first satisfiable, `allOf` merged, string `minLength`,
  numbers at `minimum`; a `pattern` only through `_PATTERN_VALUES`, the three patterns the contract uses without
  `examples`). The sweep asserts exactly 403 (`PERMISSION_DENIED`; for a `HANDLER_GUARDED` route
  `WORKSPACE_SCOPE_DENIED` also) and 401 for the anonymous one. `UNSATISFIABLE` holds the two multipart operations
  (`POST /api/v1/rate-tables/{slug}@{version}/import`, `POST /api/v1/sources/{source_id}/preview`, a file part), and
  `len(UNSATISFIABLE) == 2` is asserted. **Deviation from the plan, stated:** the plan's builder rule is `pattern` from
  `examples`; the contract has no `examples` for its slug, digest and peril-code patterns, so three literal values are
  mapped instead. **The red for `POST /api/v1/me/workspace` cannot be shown as a failing run of the old sweep:** the old
  sweep passed it (5 passed at `8252741c`) because `{}` answered 422, which it counted as a refusal; the new sweep
  sends a valid body and requires 403, and passes. This is a reasoned red, recorded as such.
- **(g) partition:** `test_every_operation_is_accounted_for_by_exactly_one_class` asserts open-by-design,
  permission-free, handler-guarded and `requires()`-declared are pairwise disjoint and union to the 141 published
  operations.
- Iterated count 141, OpenAPI count 141 (predicate: the plan's `python3 -c` over `docs/contracts/openapi/generated.json`
  and `_published_operations`, the same figure). Result: `9 passed`; `ruff check`, `ruff format --check` and `mypy`
  clean on the file.

## PRs

Not yet opened (draft PR at the first push).
