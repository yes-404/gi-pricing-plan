---
id: LG-8371
family: ledger
title: WK-1178 slice SL-8370 — FD-1482 limb 2 (b), RL-1483 item 3: the permission pin (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05            # filed under working id 8371
owner: executor
tree: 7400f0e5                    # sl-8370-permission-pin (base sl-8343 5748acc7bf0ea1ae83a1a63f81460f6b6d53f506 + sl-8361 921d9a3e5bed8d70f198dd118c97c65a81bf3a14 by sha)
slice: SL-8370
phase: P2
work: WK-1178
plans: []
corrected_by: []
relates: [FD-1482, RL-1483, FR-343]
---

# LG-8371 — WK-1178 slice SL-8370: the permission pin

**GO:** to-lead "2026-11-05 15:55:35 GMT" (2); rulings to-lead "2026-11-05 16:11:02 GMT". **MERGE-ACK:** none yet (unpushed).

## Tasks

### Scope

RL-1483 item 3: `backend/tests/test_route_permission_pin.py` compares, for every live route (included routers flattened), the `Permission` cell of its §5.1 row with what the route checks, failing in both directions. Rows are read through `model_schema.table_rows`; paths as `audit-docs.py`'s `_path_segments`. The declaration is never generated from `requires()` (RL-1483's rejected option (c)). DB-free.

**Route side, by what proves it** (ruled 16:11:02 GMT): the `PERMISSION_ATTRIBUTE` of `requires()` (dependency); a `require_permission(permission=)` call in the handler body (inline); the same in a function the handler calls that is defined in the same module, ONE level, by what the call reaches (one-level); the `HANDLER_GUARDED` code sites (site); and one NAMED entry, `PATCH /datasets/{dataset_id}` → `platform/datasets.py:set_owner` (FR-82), proved by AST: one `if` testing `is_owner` and `ADMIN_MANAGE_ROLES` whose body raises, with `is_owner` assigned. A test asserts the named list's exact contents.

**Counts** (2026-11-05 17:26 UTC, at code head `da8372e2` of `sl-8370-permission-pin`; the predicate is the script below, verbatim and runnable, saved as `pred.py` and run as `env GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@127.0.0.1:1/none GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@127.0.0.1:1/none GIP_REDIS_URL=redis://127.0.0.1:1/0 uv run --directory <worktree> python - < pred.py`; it replaces the uncommitted `/tmp/sl8370_count.py` this line cited before). Each of the operations of `_flattened_operations(create_app(...).routes)` is classified, first match in the order open, named, site, one-level, inline, dependency, else authenticated; module = the spec file of the row read:

```python
import ast, collections, inspect
from pathlib import Path
from app.api.authz import PERMISSION_ATTRIBUTE
from app.config import Environment, Settings
from app.main import create_app
from backend.tests import test_route_permission_pin as t
from backend.tests.test_api_authorisation_sweep import HANDLER_GUARDED, _flattened_operations

app = create_app(Settings(environment=Environment.LOCAL, version="x", log_level="ERROR"))
declared, _ = t.declared_rows(t._spec_texts())
ops = list(_flattened_operations(app.routes))
walked = {k: v for k, v in t.checked_routes(app).items()}
rows = sum(len(v) for v in declared.values())
print("rows", rows, "row keys", len(declared), "ops", len(ops),
      "walked", sum(len(v) for v in walked.values()), "op keys", len(walked))
print("keys carrying more than one row:", {k: [r.where for r in v] for k, v in declared.items() if len(v) > 1})
print("rows with no walked op:", rows - sum(min(len(v), len(walked.get(k, []))) for k, v in declared.items()))
c = collections.defaultdict(collections.Counter)
for m, p, r in ops:
    row = declared.get((m, t.segments(p)), [None])[0]
    mod = row.where.split(":")[0][:2] if row else "none"
    dep = {str(getattr(x, PERMISSION_ATTRIBUTE).value) for x in t._dependency_calls(r.dependant)
           if getattr(x, PERMISSION_ATTRIBUTE, None) is not None}
    src = Path(inspect.getsourcefile(r.endpoint)).read_text()
    fn = t._module_functions(ast.parse(src)).get(r.endpoint.__name__)
    inline = t._checks_in(fn) if fn is not None else set()
    one = t.handler_checks(src, r.endpoint.__name__) - inline
    if p in t.OPEN_BY_DESIGN: k = "open"
    elif (m, p) in t.NAMED_CONDITIONS: k = "named"
    elif (m, p) in HANDLER_GUARDED: k = "site"
    elif one: k = "one-level"
    elif inline: k = "inline"
    elif dep: k = "dependency"
    else: k = "authenticated"
    c[mod][k] += 1
tot = collections.Counter()
for mod in sorted(c):
    print(mod, dict(c[mod]), sum(c[mod].values())); tot.update(c[mod])
print("TOTAL", dict(tot), sum(tot.values()))
openapi = [(m, p) for m, p, _ in ops if p == "/openapi.json"]
print("GET /openapi.json among ops:", openapi, "| in OPEN_BY_DESIGN:", "/openapi.json" in t.OPEN_BY_DESIGN,
      "| rows:", [r.where for r in declared.get(("GET", t.segments("/openapi.json")), [])])
```

Output at `da8372e2`:

```text
head=da8372e2ec79bdc894b3bd7e8b05ff3cd51872ed
rows 207 row keys 206 ops 168 walked 168 op keys 167
keys carrying more than one row: {('GET', ('rating-versions', '{}')): ['03-rating-engine.md:1111', '03-rating-engine.md:1112']}
rows with no walked op: 39
01 {'dependency': 38, 'named': 1, 'site': 1} 40
02 {'dependency': 44, 'inline': 1} 45
03 {'site': 5, 'dependency': 35, 'inline': 2, 'one-level': 3} 45
06 {'authenticated': 6, 'site': 1, 'dependency': 6} 13
07 {'open': 5, 'dependency': 19, 'authenticated': 1} 25
TOTAL {'dependency': 142, 'named': 1, 'site': 7, 'inline': 3, 'one-level': 3, 'authenticated': 7, 'open': 5} 168
GET /openapi.json among ops: [] | in OPEN_BY_DESIGN: True | rows: ['07-platform.md:360']
rc=0
```

| Module | dependency | inline | one-level | site | named | authenticated | open | routes |
|---|---|---|---|---|---|---|---|---|
| 01 | 38 | 0 | 0 | 1 | 1 | 0 | 0 | 40 |
| 02 | 44 | 1 | 0 | 0 | 0 | 0 | 0 | 45 |
| 03 | 35 | 2 | 3 | 5 | 0 | 0 | 0 | 45 |
| 06 | 6 | 0 | 0 | 1 | 0 | 6 | 0 | 13 |
| 07 | 19 | 0 | 0 | 0 | 0 | 1 | 5 | 25 |
| total | 142 | 3 | 3 | 7 | 1 | 7 | 5 | 168 |

**What the pin proves, restated.** 207 §5.1 rows parse; 168 live operations are walked, each compared with its row (the live test asserts the walked count equals the operations count). Before the audit fix the pin keyed by `(method, normalised path)` and overwrote: `GET /rating-versions/{slug}@{version}` (03:1111) and `GET /rating-versions/{id}` (03:1112) are one key, so 207 rows were 206 keys and 168 operations were 167 keys, and one of the two routes was never compared. Both lists now keep every entry per key, and rows that share a key must agree. "168 proved" means 168 walked. The other 39 rows have no walked operation: 38 are declarations of routes not built, and one is `GET /openapi.json` (07:360), a built route that FastAPI registers with `include_in_schema=False` (`test_api_authorisation_sweep.py:138`), so `_flattened_operations` never yields it and the sweep carries it in `OPEN_BY_DESIGN` only. **The pin does not prove that row:** a wrong cell on it passes. 168 + 38 + 1 = 207. `07` declares six `open` rows (healthz, readyz, version, auth/config, openapi.json, metrics); the table above counts five `open` operations because `/openapi.json` is the sixth and is not walked.

### Gate

`pytest -q -rf backend/tests/test_route_permission_pin.py` at `da8372e2` (tree `1b3871d6`), DB-free (dead-port URLs), via run-heavy: **1 failed, 22 passed, rc=1**; the one failure is `test_the_spec_declares_what_every_live_route_checks`, red on exactly the two routes below until the re-merges (earlier at `953ac45b`: 20 passed, 1 failed). Both are findings, no exemption (ruled):
- `POST /api/v1/models/{model_id}/archive`: spec 02:1920 `model:fit`; code `model:submit` (FD 8366, merges first; the pin takes its own gate slot after it).
- `GET /api/v1/dislocation-runs/{run_id}/movers`: spec 03:1128 cell `rating:read`; code checks `dataset:read` and `rating:read` (handler calls `_require_dataset_read`; its Purpose text and docstring say both). Found by the one-level walk; the cell is fixed by SL-2011's tip (`c1ee7880`), which this slice takes at its re-merge. Predicted green on both after the re-merges, not run.

### Red first (planted on the live tree, each reverted)

- `ReadAudit` AUDIT_READ→JOB_READ: "GET /api/v1/audit: spec (06-governance.md:580) says '`audit:read`'; code checks job:read".
- Cell swapped, `GET /datasets` → `job:read`: "spec (01-data-management.md:858) says '`job:read`'; code checks dataset:read".
- Handler-guarded code swap (deployments.py DEPLOYMENT_PROMOTE→DATASET_READ) and the deploy row's cell → `rating:read`: both named the deployment routes.
- Handler's `_require_dataset_read` call removed from `start_dislocation_run`: "POST /api/v1/dislocation-runs: … code checks rating:compile".
- Helper's `require_permission` removed: dislocation-runs and /estimate both red.
- `set_owner` owner limb removed, then admin limb removed: each "PATCH /api/v1/datasets/{dataset_id}: … code checks dataset:read".
- Synthetic: swapped cell, swapped requires, missing row, authenticated/open mismatches, empty cell, two levels deep, another module, each named limb and the raise.

- 2026-11-05 17:24 UTC, audit fix: `requires(Perm.RATING_READ)` → `requires(Perm.JOB_READ)` on `GET /rating-versions/{slug}@{version}` (`backend/src/app/api/models.py:1146`), the file restored afterwards (`git diff --numstat` of it empty): the live test names a third violation, "GET /api/v1/rating-versions/{slug}@{version}: spec (03-rating-engine.md:1111) says '`rating:read`'; code checks job:read", beside the two expected. This is the route the overwriting map hid: it is the first in registration order and its key was taken by the by-id route.
- Synthetic, same fix: `test_broken_two_routes_on_one_path_key_are_both_walked` (a swap on either of two routes sharing a key fails) and `test_broken_rows_sharing_a_key_that_disagree_fail`.

### Audit

Not yet. The auditor's.

### Build log

- 2026-11-05 — merge of sl-8361 @921d9a3e onto sl-8343 @5748acc7 (INDEX conflict only, regenerated); pin `d0a01354`; one-level walk and the named list in the next commit.

- 2026-11-05 17:26 UTC — audit fixes (to-lead "2026-11-05 17:20:43 GMT"): `declared_rows`/`checked_routes` keep all entries per key; `pin_violations` compares every route and fails rows that share a key and disagree; the live test asserts walked = operations; the count predicate moved into this LG; the `GET /openapi.json` line added. Code `da8372e2` (`7f40dd9c` + an E501 wrap); ruff check and format --check rc 0; the pin file: 1 failed, 22 passed, rc=1 (the two expected routes). One slip, reported to the lead: one command in this seat's session began with `cd` into this worktree (a brief ban); nothing was written outside it.
- 2026-11-05 18:44 UTC (to-lead "2026-11-05 18:05:14 GMT", the pin): **"proved" on five rows means the PERMISSION, not the scope.** Rows `03` 1104 and 1105 (the rate-table diff and diff/cells rows), 1125, 1126 (`POST /dislocation-runs`, `/estimate`) and 1128 (`GET /dislocation-runs/{id}/movers`) carry a cell naming `dataset:read` "on" a Dataset Version. The pin's walk reads those routes' `require_permission(permission=DATASET_READ)` calls, which pass no `resource=` (`api/dislocation_runs.py:57–69`; the rate-table handlers likewise), so `one-level` proves the cell's permission names and does not prove its scope clause: the pin compares names (`claim`), never a scope. The scope gap is the known latent defect FD-1853 (spec correct, code short; `ROUTE_SCOPES` declares all five routes DATASET, `test_route_scope_guard.py:118–123`, `:146`, `:182–191`), owned there, not by this slice. Counts above (168 walked, 207 rows) are unchanged by this reading.

## PRs

None. Ends unpushed.
