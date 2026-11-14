---
id: LG-2092
family: ledger
title: WK-1178 slice SL-2091 — FD-1482 limb 2 (b), RL-1483 item 3: the permission pin (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-08            # original date 2026-11-05, working id 8371, minted 2026-11-08
owner: executor
tree: 4873a0d8698804e00cf8631a4f309f90214bcb8b   # the tree of the gated head 805d036b of sl-8370-permission-pin, before this PR's merges of origin/main (was 7400f0e5 at the draft; base sl-8343 5748acc7bf0ea1ae83a1a63f81460f6b6d53f506 + sl-8361 921d9a3e5bed8d70f198dd118c97c65a81bf3a14 by sha)
slice: SL-2091
phase: P2
work: WK-1178
plans: []
corrected_by: []
relates: [FD-1482, RL-1483, FR-343]
---

# LG-2092 — WK-1178 slice SL-2091: the permission pin

*Disclosure: drafted under working id 8371; minted as LG-2092 on 2026-11-08, in the SL-2091 mint PR (slice SL-2091 was working id 8370).*

**GO:** to-lead "2026-11-05 15:55:35 GMT" (2); rulings to-lead "2026-11-05 16:11:02 GMT". **MERGE-ACK:** (added at merge.)

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
- `POST /api/v1/models/{model_id}/archive`: spec 02:1920 `model:fit`; code `model:submit` (FD-2079, merges first; the pin takes its own gate slot after it).
- `GET /api/v1/dislocation-runs/{run_id}/movers`: spec 03:1128 cell `rating:read`; code checks `dataset:read` and `rating:read` (handler calls `_require_dataset_read`; its Purpose text and docstring say both). Found by the one-level walk; the cell is fixed by SL-2011's tip (`c1ee7880`), which this slice takes at its re-merge. Predicted green on both after the re-merges, not run.

**Full code gate at the pin's head `805d036b` (tree `4873a0d8`), gate-1, END `2026-11-08T03:05:41+00:00` rc=1, read STANDS by the maintainer (by delegation; to-lead after 03:05 GMT 2026-11-08: "PIN gate END … STANDS, CLEAN at 805d036b").** Written from the gate's own logs (`~/gi-pricing-plan.local/scratch/sl8370-gate/gate/`: `gate.log`, `pytest.log`, every `*.rc`), not from a relay. The one-file run above is superseded by it.

- **pytest** (`pytest.log`, `pytest.rc` 1): `13 failed, 7569 passed, 28 skipped, 5 xfailed, 156 warnings in 5035.74s (1:23:55)`. gate.log: `item 31 | pytest FAILED=13; failing files outside the eight docs-audit files: [none]`. The 13, by file against common-brief item 31 (the eight docs-audit files, all of them in the set): `test_audit_docs_finding_citations.py` 1 (`test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`); `test_audit_docs_ids.py` 2 (`test_the_real_tree_passes_all_ten_checks`, `test_doc_id_check_exits_0_on_the_real_tree`); `test_audit_docs_process_core_digest.py` 2 (`test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `test_the_committed_digest_currently_matches_the_committed_spec`); `test_audit_docs_w37_11_ceiling.py` 1 (`test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`); `test_doc_index.py` 1 (`test_an_index_skipping_a_reserved_block_breaks_contiguity`); `test_register_lint.py` 3 (`test_check_29_is_wired_into_the_docs_gate`, `test_check_29_note_carries_the_residue_line`, `test_phase1b_residue_count_matches_check_29s_own_count`); `test_register_owed.py` 1 (`test_check_29_wiring_is_undisturbed`); `test_repository_invariants.py` 2 (`test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`). Item 31 stands only with the mint, audit-docs rc 0, these re-run via run-small on the minted head, and CI; those are owed at the mint.
- **audit-docs** (`audit_docs.rc` 1): `FAILED (3)`, all the slice's own working ids and none other: check 31 "gap in the full allocation between 2081 and 8370"; check 31 "id 8371 is `created:` 2026-11-05, earlier than id 2081's 2026-11-07"; check 32 "LG 08371 …:127: SL 8343 does not resolve in docs/INDEX.md". Cleared by the mint.
- **Other rc files:** `ruff.rc` 0, `mypy.rc` 0, `import_linter.rc` 0, `req_coverage.rc` 0, `contracts.rc` 0. **Skipped:** `pytest skipped | 28 (== 28 baseline: SKIP_BASELINE override)`.
- **Frontend** (all rc 0): `pnpm install --frozen-lockfile`, `pnpm generate:api`, `pnpm lint`, `pnpm type-check`, `pnpm build`; vitest (`fe-test.log`) `Test Files  138 passed (138)`, `Tests  919 passed (919)`.
- **Demo:** `demo.py --journey wf-699 --no-compose` rc=0, designed stop with both lines seen, `demo seconds | 1472` (PASS); **D7** `ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units` (equal).
- **Dislocation:** `dislocation #1 | 541 s (29 Oct passes: 422 / 387 / 383 s; this box 21:17:05 baseline 552 / 558 s)`. Recorded as **a paired reading** (pair 4, with SL 8406), not as a regression finding and not as an NFR measurement.
- **Item 21 (re-merge of main 81c898c7):** the import closure of this slice is empty — it changes no source module, only its own test file `backend/tests/test_route_permission_pin.py` — so no code-adjacent test is owed; main's new `packages/model-schema/tests/test_validation_report_stored_form.py` and `tests/test_spec_examples.py` are not code-adjacent to the pin, and PR CI's full suite at the merged head covers them (lead, to-lead 2026-11-08).
- **END rc parts:** `python max=1 fe max=0 demo=0 restore rc_kc=0 role rc_role=0 skip rc_skip=0 infra rc_infra=0 template rc_tg=0 db0 rc_db0=0`; template guard `alembic_version=1 environments=3 tenant_marker=1` clean at START, db 0 `dbsize` 56 at START.

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

*(Adopted by the lead from the auditor's draft `aud-sl8368/` draft `LG 8371-audit-section.md`, from-lead "2026-11-05 17:20:17 GMT"; folded here by exec-pinprep2, 2026-11-08, per item 34. The draft's "Tree read" line names the tree it read, 953ac45b; this ledger has since been re-merged.)*

Tree read: sl-8370-permission-pin @953ac45b5f00aee79af98ef72944e80062b586a9, tree 90b3080a1c720f0c94d868948cc93d9edd8ae3a2. Own commits: merge 26945cbc, d0a01354, 7400f0e5, 953ac45b (`git diff --stat 26945cbc..HEAD`: the test file +459, INDEX +5, LG +68). Range for the slice's own change: `26945cbc..HEAD`; vs `origin/main...HEAD` it also carries SL-2069 (draft name SL 8343) and the 8361 merge.
Run (DB-free, dead-port URLs, via run-heavy --over-load, load1 ~13, non-timed): `pytest -q -rf backend/tests/test_route_permission_pin.py` at 953ac45b: **1 failed, 20 passed, 2 warnings in 3.11s, rc=1**; the one failure is `test_the_spec_declares_what_every_live_route_checks`, red on exactly two routes: `GET /api/v1/dislocation-runs/{run_id}/movers` (spec 03:1128 `rating:read`; code dataset:read, rating:read) and `POST /api/v1/models/{model_id}/archive` (spec 02:1920 `model:fit`; code `model:submit`). The test needs no DB (the only DB trace is conftest_db's "could not empty the test database" warning on the dead port). Log: `~/gi-pricing-plan.local/scratch/aud-sl8368/pin-953ac45b.log`.

| # | Scope row | Evidence | Verdict |
|---|---|---|---|
| 1 | Pin compares every live route's Permission cell with what the route checks, both directions | `pin_violations` (`backend/tests/test_route_permission_pin.py:272`): code→spec ("live route with no §5.1 row", cell mismatch) and the cell kinds `open`/`authenticated`/names. The spec→code direction is "a row with no live route is an unbuilt declaration" (docstring :273): a row whose route exists but is not walked is not caught (rows 4, 5). | MET with the two gaps below |
| 2 | Rows read through `table_rows`, never a reading of its own | imports `endpoint_row`, `split_row` from `model_schema.table_rows`; `_path_segments` loaded from `scripts/audit-docs.py` by path. | MET |
| 3 | Declaration never generated from `requires()` (RL-1483 rejected (c)) | `declared_rows` reads only spec text. | MET |
| 4 | Counts: "168 + 38 + 1 = 207"; the line on `GET /openapi.json` (`test_api_authorisation_sweep.py:138`/`OPEN_BY_DESIGN` :39) | **LG 8371 has no line on `GET /openapi.json`: ABSENT.** By my predicate (`scratch/aud-sl8368/count.py`, `count2.py`, `count3.py`, `GET /openapi.json` via `app = create_app(Settings(environment=LOCAL, version="test"))` at 953ac45b): §5.1 endpoint rows parsed (`endpoint_row`) = **207**; live operations (`_flattened_operations(app.routes)`) = **168**; so 168 live-op rows + 39 rows no live operation reaches = 207. Of the 39, `GET /openapi.json` (`07`:360) is the one **built** route: FastAPI's own route is `include_in_schema=False`, so `_flattened_operations` never yields it; the sweep carries it in `OPEN_BY_DESIGN` only. That is `07`'s sixth `open` row against the pin's five (`07`:356–361: healthz, readyz, version, auth/config, openapi.json, metrics) — the maintainer's open "6 vs 5". The pin proves nothing about that row: a wrong cell on it passes. | **NOT MET** as stated: the LG owes the line (which row, why, by predicate); the brief's 168 + 38 + 1 reads as 168 + 38 unbuilt + `/openapi.json` = 207 ✓ (by my count 39 rows have no walked op: 38 unbuilt declarations if the LG's 38 holds + the one). |
| 5 | **NEW — a key collision hides one route from the pin** | `declared_rows` and `checked_routes` both key by `(method, segments(path))` and overwrite on a repeat (`rows[...] =` :117, `checked[...] =` :263). `_path_segments` collapses every `{…}` segment, so `/rating-versions/{slug}@{version}` (`03`:1111; live `models.py:1139`) and `/rating-versions/{id}` (`03`:1112; live `models.py:1164`) are ONE key: **207 rows → 206 keys; 168 ops → 167 keys** (`count2.py`: collisions `{('GET', ('rating-versions','{}')): [03:1111, 03:1112]}`; `count3.py`: `ops 168 keys 167`). Both cells are `rating:read` and both routes check `rating:read`, so nothing is wrong today; the pin proves 167 of 168 routes, and a `requires()` swap on whichever of the two the walk visits first goes unseen. The LG's "Total checkable by the pin: 168" overstates by one. Also unmoved by the pin: `test_the_spec_declares_what_every_live_route_checks` asserts `len(declared) >= len(checked) - 5` and no equality with the operation count. | **Finding proposal (low, a test blind spot, ruled by the lead):** key by `(method, raw path)` or fail on a repeated key; add the planted case (two routes one normalised key, one swapped). NOT MET for "every route proved". |
| 6 | Red on exactly the two, DB-free | quoted above, rc=1. Expected-red set matches the maintainer's (archive: FD-2079 merges first; movers: cell fix). | MET |
| 7 | Red first on planted input, both directions | LG's "Red first" list: AUDIT_READ→JOB_READ and the cell swap named, quoted. The synthetic tests (`test_broken_*`, :330–:436) run in the 20 passed. Plants on the live tree were reverted and are **not committed**: read from the LG, not re-planted by this audit. | MET (synthetic reproduced green by the run; live plants by the LG's quotes) |
| 8 | One-level walk and the NAMED list as ruled (16:11:02) | `test_the_named_list_is_exactly_one_entry` (:437): one entry, `PATCH /datasets/{dataset_id}` → `set_owner`; planted removal of each limb red (`test_broken_a_named_condition_that_lost_a_limb_proves_nothing`, parametrized). Walk: same module, one level, not cross-module (`test_broken_the_walk_does_not_read_another_module`, `…stops_at_one_level`). | MET |
| 9 | Per-module counts by route kind, "so 207 proved is checkable" | LG table totals 142 + 3 + 3 + 7 + 1 + 7 + 5 = 168 ✓ (the predicate `/tmp/sl8370_count.py` is **not committed and not under the repo** — the maintainer's rule 'the predicate verbatim and runnable' (CLAUDE.md §13) is unmet: **the LG cites a `/tmp` path**). The table counts operations (168), not distinct keys (167): see row 5. 5 open in `07` (healthz, readyz, version, metrics, auth/config) ✓ with row 4. | **NOT MET** as to the predicate's form: commit the script under `scripts/` or paste its body in the LG. |
| 10 | The LG's FD-2079 / movers statements | Movers: SL-2011's tip (`sl-8361-permission-column` @6ca44595) carries the fix `c1ee7880`: 03:1128 now reads "`rating:read` and `dataset:read` on that Dataset Version" (`_NAME` finds both names ⇒ should match the code's set); the pin merged 8361 @921d9a3e, before it. | see merge order |

NFRs: none claimed; the run is 3.11 s.

Ancestor check: `git merge-base --is-ancestor` exit 0 for sl-8343 @5748acc7 and sl-8361 @921d9a3e against 953ac45b; `bdad1322` (origin/main) is an ancestor of 953ac45b. RL-1483 exists at origin/main (`docs/rulings/RL-01483-…`). **What moved:** `sl-8361-permission-column` is now @6ca44595 (4 commits past 921d9a3e: mint e38cb45d, the movers cell c1ee7880, LG note 7f4ce407, audit 6ca44595). `git merge-tree sl-8361-permission-column 953ac45b` → conflict in `docs/INDEX.md` only (regenerate).

GREEN by import closure (item 29): the slice adds one test file and changes no source; closure of changed modules is empty; `test_api_authorisation_sweep.py` is imported by the pin (`HANDLER_GUARDED`, `OPEN_BY_DESIGN`, `_flattened_operations`) and unchanged. **OWED-TO-GATE**: the pin's own gate slot after FD-2079 (ruled 16:11:02), the docs-audit set (INDEX change). Not looped.

Merge order: see the report (SL-2011 → SL 8368 re-merged → this slice re-merged, INDEX regenerated, pin re-run: expected green on the 02 row after 8368 and on the 03 row after 8361's tip; owed).

### Build log

- 2026-11-05 — merge of sl-8361 @921d9a3e onto sl-8343 @5748acc7 (INDEX conflict only, regenerated); pin `d0a01354`; one-level walk and the named list in the next commit.

- 2026-11-05 17:26 UTC — audit fixes (to-lead "2026-11-05 17:20:43 GMT"): `declared_rows`/`checked_routes` keep all entries per key; `pin_violations` compares every route and fails rows that share a key and disagree; the live test asserts walked = operations; the count predicate moved into this LG; the `GET /openapi.json` line added. Code `da8372e2` (`7f40dd9c` + an E501 wrap); ruff check and format --check rc 0; the pin file: 1 failed, 22 passed, rc=1 (the two expected routes). One slip, reported to the lead: one command in this seat's session began with `cd` into this worktree (a brief ban); nothing was written outside it.
- 2026-11-05 18:44 UTC (to-lead "2026-11-05 18:05:14 GMT", the pin): **"proved" on five rows means the PERMISSION, not the scope.** Rows `03` 1104 and 1105 (the rate-table diff and diff/cells rows), 1125, 1126 (`POST /dislocation-runs`, `/estimate`) and 1128 (`GET /dislocation-runs/{id}/movers`) carry a cell naming `dataset:read` "on" a Dataset Version. The pin's walk reads those routes' `require_permission(permission=DATASET_READ)` calls, which pass no `resource=` (`api/dislocation_runs.py:57–69`; the rate-table handlers likewise), so `one-level` proves the cell's permission names and does not prove its scope clause: the pin compares names (`claim`), never a scope. The scope gap is the known latent defect FD-1853 (spec correct, code short; `ROUTE_SCOPES` declares all five routes DATASET, `test_route_scope_guard.py:118–123`, `:146`, `:182–191`), owned there, not by this slice. Counts above (168 walked, 207 rows) are unchanged by this reading.
- 2026-11-08 — re-merge, step 2 (exec-pinprep2): FD-2079's final head 38435817 (INDEX-only conflict, theirs) then origin/main c8712027 (clean) → head 5c0bb730 before this commit; `git ls-files docs | grep -E '0836[689]'` printed nothing. **GREEN by import closure (item 29):** `git diff --name-only origin/main...HEAD -- backend/src packages` printed nothing, so the closure is empty; the slice's one non-docs file is `backend/tests/test_route_permission_pin.py`. GREEN = that file + `test_severity_population_golden.py` (brief) + items 43 `test_api_authorisation_sweep.py` and 45 `test_error_sinks.py`. run-small at 5c0bb730: pin + severity golden + sweep: 25 passed, 9 errors (all in the sweep, DB fixture; owed to the gate); error_sinks: 9 passed, 4 errors (DB fixture; owed to the gate).

## PRs

None. Ends unpushed.

- 2026-11-08 — mint (exec-mint8370, lead 31): SL 8370 → SL-2091, LG 8371 → LG-2092 (block idsweep-clean at `origin/main` `81c898c7`, main's highest 2090); `FD 8366` re-pointed to FD-2079 and SL 8343 to SL-2069 above; the audit text's own LG 8371 mentions and `SL 8368`/`SL 8406` mentions are quotes or other records' working ids and stay. Closed with the slice's audit by the lead's adoption of the gate (`gate.log` END `2026-11-08T03:05:41+00:00`, `rc=1`, standing under item 31 modulo this mint). **Item 42:** no `SL-2091` row existed at `origin/main` `81c898c7`; this PR's mint adds it as `closed`. **Item 21:** see the Gate section. Cites in other records that name SL 8370 (FD-2079, PL-2059, PL-2083, PL-2087) are frozen records and are not edited.
