---
id: LG-1646
family: ledger
title: WK-1178 slice SL-1517 — NFR-498 Audit Events on rate table version and rating algorithm writes (PL-1516, PL-1627), slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-11            # original date 2026-10-11, set at the draft; minted 2026-10-11
owner: executor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
phase: P2
work: WK-1178
slice: SL-1517
plans: [PL-1516, PL-1627]
corrected_by: []
relates: [PL-1516, PL-1627, FD-1513, RL-1514, RL-1515, RL-1625, RL-1263, SL-1559, SL-1391, NFR-498, FR-368]
---

# LG-1646 — WK-1178 slice SL-1517: NFR-498 Audit Events on rate table version and rating algorithm writes

*(Minted 2026-10-11 as LG-1646 from working id 9793, at the merge turn.)*

**GO:** the maintainer's (by delegation) entries in `to-lead.md`: "2026-10-11 19:24:24 BST — #1281 (SL-1559, WK-675 S4) read-back VERIFIED: main 372fa92ae3ab306bc067c234487ce929dc0e2a04, parent fe80aec6, tree b38efae0 = ACK tree; PR MERGED, mergeCommit matches. Lane C: S4 done; next SL 9916, then S5. SL-1517 (DP-6 edit path) may now GO, latest Thu 29 Oct." and "2026-10-11 19:23:39 BST — MERGE-ACK #1281 …" ("SL-1517 (DP-6 edit path) may GO after this merges (latest Thu 29 Oct)"). BOUND: merged on or before Wed 2026-11-04 (PL-1516 item 12); report bound for PL-1516 Task 4 Step 1: Fri 2026-10-30 18:00 GMT (PL-1627 §B4, as the lead's GO sets it).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Executed from `PL-1516` (leaf plan, with its deltas D1–D7 and E1–E6) as folded by `PL-1627` (Part B). Branch `sl-1517-wk1178-nfr498-audit-events`, worktree `.claude/worktrees/sl-1517`, cut from `origin/main` `372fa92ae3ab306bc067c234487ce929dc0e2a04` (#1281). Row: `SL-1517` in `docs/roadmap.md`. Rulings: `RL-1514`, `RL-1515` (DP-1..DP-5, T-1a..T-1d), `RL-1625` (DP-6 (a), T-2). Finding: `FD-1513`. Requirements: `03` NFR-498, `06` FR-368.

Where PL-1516 and PL-1627 disagree, PL-1627 governs as the later dated delta. Places it does so (quoted when found, in Task 0).

### Task list

Executed from `PL-1516` as folded by `PL-1627` Part B. Where the two disagree, PL-1627 governs
(the later dated delta); the places it does, quoted:

- **Write set.** PL-1516 §"Write set" says `test_rating_algorithms.py` is "read only" (`:643`) and
  lists no `test_rate_table_diff_portfolio.py` or `test_rating_version_dislocation_gate.py`;
  PL-1627 §B1: "Three test files call them and are not in PL-1516's write set. Each changes **the
  call-site argument only**". Followed: those three are edited, call-site argument only.
- **Item 9's command.** PL-1627 §B1: "Item 9's command gains the two files it does not run".
  Followed: 11 files, run in 3-file batches through `run-small.sh`.
- **`_stored_version`.** PL-1516 D3's constructor has no `created_by_edit`; PL-1627 §B3 1 adds it.
  Followed.
- **Contract.** PL-1516: "Not written: ... `docs/contracts/`"; PL-1627 §B3: the regenerated
  `docs/contracts/schemas/generated/audit-event.schema.json` joins the write set. Evidence:
  `uv run python scripts/generate-contracts.py --check` exits 0 ("48 generated contracts match the
  models"), so the diff is empty and nothing under `docs/contracts/` is touched (`action` is the
  pattern `^[a-z_]+\.[a-z_]+$`).
- **Order and report bound.** PL-1627 §B4 / §B7 5a: S4 (`SL-1559`) merged first (#1281, `372fa92a`);
  PL-1516 Task 4 Step 1's "before 2026-10-28" is replaced, for a GO after 26 Oct, by the GO record's
  date. The GO of 2026-10-11 19:24:24 BST is earlier than 26 Oct, so 28 Oct stands; the lead's brief
  also names Fri 2026-10-30 18:00 GMT as the report bound (PL-1627 §B4). The merge must be on or
  before 2026-11-04.

#### Task 0: preconditions and the re-anchor (base `372fa92a`)

Activation needs (PL-1516 D7 + PL-1627 §B7), each at `origin/main` `372fa92a`:
FD-1513 (`docs/findings/FD-01513-...`), RL-1514, RL-1515 and RL-1625 exist under `docs/findings/` and
`docs/rulings/`; SL-1427 and A-2 (SL-1463, `2edc4d89`) merged (PL-1627 §A6); WK-675 S4 merged as
#1281 at `372fa92a` (read-back "2026-10-11 19:24:24 BST"); the GO is the 19:24:24 entry quoted above.

Symbol re-anchor at `372fa92a` (`git grep -n` / `grep -n`; PL-1516's lines are at `5fe56b87`, PL-1627
§B5's at `d699a561`):

| Symbol | PL-1516 | PL-1627 §B5 | At `372fa92a` |
|---|---|---|---|
| `seed_from_model` | `rate_tables.py:96` | `:121` | `:129` |
| `import_confirmed` | `:419` | `:889` | `:897` |
| `manual_edit_confirmed` (new, S4) | n/a | S4 `:1047` | `:1047` |
| `_load_version` | `:528` | `:998` | `:1132` |
| `_load_cells_of` | n/a | n/a | `:1203` |
| `_to_version` | `:612` | n/a | `:1270` |
| `_persist_new_version` | `:670` | `:1140` | `:1328` |
| `bulk_operation` | `:796` | `:1266` | `:1462` |
| `create_algorithm` | `rating_algorithms.py:94` | `:219` | `:219` |
| `_write`, `create_sub_graph`, `create_version`, `_row` | `sub_graphs.py:59,104,127,150` | `:63,:108,:132,:156` | `:63,:108,:132,:156` |
| `audit.record`, `verify_chain` | `audit.py:52` | `:52,:158` | `:52,:158` |
| `version_content_hash` | `diff_cache.py:46` | `:48` | `:48` |
| routes: seed / edit (`/versions`) / bulk / import | `api/rate_tables.py:70,112,205` | S4 edit `:172` | decorators `:97,:139,:180,:273`; service calls `:125,:172,:213,:321` |
| `create_rating_algorithm` call | `api/rating_algorithms.py:46-49` | n/a | `:55` |

Facts that changed since the plan (none stops the slice):
- `create_algorithm` gained A-2's `check_model_call_feature_maps` call (before the 409 check) and
  `create_version` / `create_sub_graph` gained the same; the audit record sits after the last flush,
  after both. No conflict.
- `manual_edit_confirmed` (SL-1559) is a fourth caller of `_persist_new_version`; it threads the actor
  and passes `rate_table_version.edited` (PL-1627 §B3 2). Its `before` is the base version's stored
  state from `_edit_derived`'s `base`.
- SL-1600 `InputFreeError` / SL-1390 `rating_versions.py`: untouched by this slice; no new message is
  added, so none uses `str(exc)` or `{exc}` (pre-existing `str(exc)` in `bulk_operation`'s 422 at
  `rate_tables.py` is untouched and out of the write set's change).
- Call-site predicate (PL-1627 §B1), re-run: `git grep -n -E '(seed_from_model|import_confirmed|bulk_operation|create_algorithm)\(' 372fa92a -- backend examples scripts`,
  less `async def` lines: **36 call sites in 13 files**, the same count PL-1627 gives at `d699a561`
  (per file: `api/rate_tables.py` 3, `api/rating_algorithms.py` 1, `test_rate_tables_service.py` 14,
  `test_rate_table_diff_portfolio.py` 6, `test_rating_versions.py` 3, `test_regression_suites.py` 2, and 1
  each in `test_diff_cache.py`, `test_rating_algorithms.py`, `test_rating_version_dislocation_gate.py`,
  `test_worker_rate_tables.py`, `examples/fremtpl2/model.py`, `scripts/bench-compiled-for.py`,
  `scripts/bench-score-batch.py`). The predicate does not name S4's `manual_edit_confirmed(`: its one call
  (`api/rate_tables.py:172`) is a 37th, moved too (PL-1627 §B3 2).
- **Version-returning routes at `372fa92a`** (PL-1516 E2 re-enumeration): `POST .../seed-from-model` (201,
  `response_model=RateTableVersion`), `POST .../versions` with `confirm: true` (201, S4's edit route),
  `POST .../bulk-operation` (201), `POST .../import` with `confirm` (201). The new `GET
  /rate-tables/{slug}@{version}` (`api/rate_tables.py:434`, FR-1636) returns a `RateTable` (definition,
  no cells), via `service.read_definition`, not a `RateTableVersion` and not through
  `_persist_new_version` or `_stored_version`: it does not join the set. The other GETs (export,
  diff, `cells`, `diff/cells`) return files, diffs and cell pages.

#### Task 1 (commit `fdc02a74`): the actor moves into the services, no behaviour change

`seed_from_model`, `import_confirmed`, `manual_edit_confirmed`, `bulk_operation` and `create_algorithm`
take `actor: Principal` (each opens with `assert actor.id is not None`), read `created_by` from
`actor.id`; five route call sites pass `caller.principal` (four in `api/rate_tables.py`, the edit route among them; one in `api/rating_algorithms.py`); 30 test/example call sites (all of the grep's tests/example lines), two benches
(`Principal(kind=ActorKind.USER, id=created_by, display="bench")`). Proof: `ruff check` on touched files
clean; whole-tree `uv run mypy` "no issues found in 236 source files"; item 9's 11 files, in 3-file
`run-small.sh` batches: 24 + 136 + 58 + 95 passed, no assertion edited. **Task 1 gate (RL-1515 D5 Step 5b; PL-1516 item 9, PL-1516 :188), ruled separate by the lead
(from-lead "2026-10-11 20:38:51 BST" and the 22:45:14 BST grant).** Run on a detached worktree at
`fdc02a7454fdc749b5ed9661bc09b6c5b809f2d6` (tree `85ba6487513d56410f2ab874bd2e2792c23df938`) by
`scratch/sl1517/slot-t1.sh`, under `flock /tmp/slots/gate-1`, slot held 22:45:28 to 23:40:24 BST
(script `end ... rc=1`); preflight line: `PREFLIGHT ok: head guard, clean tree, /tmp/slots/gate-1 held +
GIP_GATE_SLOT exported, containers healthy, upgrade rc 0, 1 head`. Stage to rc, START-END (BST):

| Stage | START-END | rc |
|---|---|---|
| item9 (11 files) | 22:45:33-22:51:06 | 0 |
| ruff | 22:51:06-22:51:06 | 0 |
| mypy | 22:51:06-22:51:42 | 0 |
| import_linter | 22:51:42-22:51:43 | 0 |
| pytest | 22:51:43-23:38:30 | 1 (13 failed, 5591 passed, 5 skipped) |
| audit_docs | 23:38:30-23:38:50 | 1 (check 31 only; non-31 failures 0) |
| req_coverage | 23:38:50-23:38:50 | 0 |
| contracts | 23:38:50-23:38:58 | 0 |
| fe_install / fe_generate / fe_lint / fe_typecheck | 23:38:58-23:39:36 | 0 / 0 / 0 / 0 |
| fe_test | 23:39:36-23:40:21 | 1 (2 failed, 687 passed) |
| fe_build | 23:40:21-23:40:24 | 0 |

Classification of every red, from the logs:
- **pytest, 13 failed:** `test_audit_docs_finding_citations::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`,
  `test_audit_docs_ids::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`,
  `test_audit_docs_process_core_digest` (2), `test_audit_docs_w37_11_ceiling` (1), `test_doc_index` (1),
  `test_register_lint` (3), `test_register_owed` (1), `test_repository_invariants` (2). All run `audit-docs` on the tree
  and fail on `check 31: gap in the full allocation between 1636 and 9793`: the unminted working id of this ledger
  (the mint artefact). None is a timing or NFR test, and none is in this slice's files.
- **audit_docs rc 1:** the same check 31 only.
- **fe_test, 2 failed:** `DagDesigner.test.ts` ("emits an edited draft ..." and "adds a step ..."), the F39 un-stubbed
  fetch (WK-675's; fixed on main by #1283, after this base `372fa92a`). Re-run alone on `fdc02a74` through
  `run-small.sh`: 4 passed.
- **Gate-2 window.** Lead entries: "2026-10-11 23:23:57 BST" (retraction of the instruction that had other seats run
  audit-docs beside this gate), "2026-10-11 23:25:00 BST" (window), "2026-10-11 23:26:13 BST" (reclassified, with the
  maintainer's "2026-10-11 23:25:12 BST": each was one flocked gate-2 check, allowed by the gate-2 standing rule, not a
  breach). Gate-2 was busy about 22:46-23:24 BST (22:46-22:53, 23:12-23:13, runs ending 23:21:32 and 23:23:34). No
  timing or NFR test failed, so no quiet re-run was owed; the window is recorded as the period gate-2 was busy.
- **Note, 23:40:36 BST:** one `run-small.sh` DagDesigner run (above) started after the gate ended and before the lead's
  ALONE announcement ("2026-10-11 23:40:50 BST"); the lead's entry says the ALONE wrapper waited for `small-test` and
  started timing only after it finished, so no measurement was touched.
- The lead accepted this classification (message after the 23:40:50 announcement). Worktree `sl-1517-t1` and database
  `gipricing_sl-1517-t1_f0715d8c` removed after this record.

#### Task 1b (commit `90036b59`): the stored wire form, and no route response moves

`_stored_version(version_row, cells)` (with `created_by_edit`), and `_persist_new_version` returns it.
Harness (untracked, never committed, in both trees; full text below). It drove, in a fixed order with fixed
slugs and the family `mf-pl9514cmp`, with `app.platform.rate_tables.datetime` pinned to
`2026-10-05T12:00:00Z` in both trees: R1 seed `t-rows` (rows) · R2 import-confirm on `t-rows@1`
(import-made) · R0 seed `t-edit` · R7 edit-confirm on `t-edit@1` through S4's `POST .../versions`
(edit-made) · threshold set to 1 · R3 bulk on `t-rows@2` (parquet, bulk-made on an import-made baseline) ·
R4 bulk on `t-rows@3` (parquet on a parquet baseline) · R5 import-confirm on `t-rows@4` (parquet + import-made)
· R6 seed `t-pq` (parquet seed). BASE = detached worktree at `372fa92a`, HEAD = this tree with Task 1b's
edit; each run alone through `run-small.sh`, 1 test, `OMP_NUM_THREADS=1`.

**Plan defect found (PL-1516 E3 Step 3, item 5):** "import-confirm the same CSV on `t-rows@3` -> `R5`"
answers **409 `Rate table version already exists`** because step 4 already made `t-rows@4` from `@3` (the
version number is `version + 1`). Run once with `@3` in both trees: R0..R4 cmp 0, R5 the 409 at base and head
(the 409 bodies differ only in `trace_id`), R6 missing (harness stopped). Corrected to import on `t-rows@4`
(`@5` is created); the rest unchanged. Ruled a recorded deviation by the lead, from-lead "2026-10-11 20:38:51 BST": step 5's `@3` is unreachable as written and `@4` is its evident intent; not a plan change and not an FD.

Result, raw response bytes (`status\n` + `response.content`), BASE vs HEAD:

| Response | Version made | status | `cmp` BASE HEAD |
|---|---|---|---|
| R0 | seed, rows | 201 | 0 |
| R1 | seed, rows | 201 | 0 |
| R2 | import-made, rows | 201 | 0 |
| R3 | bulk on import-made, **parquet** | 201 | 0 |
| R4 | bulk on parquet, **parquet** | 201 | 0 |
| R5 | import on parquet, **parquet + import-made** | 201 | 0 |
| R6 | seed, **parquet** | 201 | 0 |
| R7 | **edit-made** (S4 route), rows | 201 | 0 |

Positive control, HEAD tree only: `"change_note": version_row.change_note + " "` in `_stored_version`;
`cmp` against BASE for R0..R7: all 8 returned **1** (a difference). Reverted (`grep -c 'change_note + " "'` = 0).
Harness deleted from HEAD (`git status --short` clean before the commit), BASE worktree removed, base database
dropped. Item 9's suite at the commit: 24 + 136 + 58 + 95 passed.

<details><summary>The harness, in full (never committed; copy at the executor's scratch)</summary>

```python
"""PL-1516 Task 1b Step 3 harness (untracked, never committed): drive the version-returning
routes in a fixed order and write each response's raw bytes and status to $PL9514_OUT/R<n>.json."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import pytest
from backend.tests.test_api_rate_tables import (
    _LEVELS,
    _seed_approved_model,
    _seed_body,
    _set_threshold,
    actuary,  # noqa: F401  (fixture)
    admin_headers,  # noqa: F401  (fixture)
)
from fastapi.testclient import TestClient

from app.platform import rate_tables as svc

_FAMILY = "mf-pl9514cmp"
_CSV = b"driver_age_band,relativity\n17-20,2.1120\n21-24,1.2690\n25-29,1.1200\n"
_PIN = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


class _FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):  # type: ignore[no-untyped-def]
        return _PIN


def test_compare(api_client: TestClient, workspace_id, actuary, admin_headers, monkeypatch) -> None:  # noqa: F811
    monkeypatch.setattr(svc, "datetime", _FixedDatetime)
    out = Path(os.environ["PL9514_OUT"])
    out.mkdir(parents=True, exist_ok=True)
    _seed_approved_model(workspace_id, _FAMILY, _LEVELS)

    def record(name: str, response) -> None:  # type: ignore[no-untyped-def]
        (out / f"{name}.json").write_bytes(
            f"{response.status_code}\n".encode() + response.content
        )
        assert response.status_code == 201, (name, response.status_code, response.text)

    def seed(slug: str):  # type: ignore[no-untyped-def]
        return api_client.post(
            f"/api/v1/rate-tables/{slug}/seed-from-model",
            json=_seed_body(_FAMILY), headers=actuary,
        )

    def imp(slug: str, version: int):  # type: ignore[no-untyped-def]
        return api_client.post(
            f"/api/v1/rate-tables/{slug}@{version}/import",
            files={"file": ("import.csv", _CSV, "text/csv")},
            data={"confirm": "true"}, headers=actuary,
        )

    def bulk(slug: str, version: int):  # type: ignore[no-untyped-def]
        return api_client.post(
            f"/api/v1/rate-tables/{slug}@{version}/bulk-operation",
            json={"kind": "uplift_table", "parameters": {"percentage": "0.10"}},
            headers=actuary,
        )

    record("R1", seed("t-rows"))
    record("R2", imp("t-rows", 1))
    record("R0", seed("t-edit"))
    record("R7", api_client.post(
        "/api/v1/rate-tables/t-edit/versions",
        json={"base_version": 1, "change_note": "edit", "confirm": True,
              "edits": [{"driver_age_band": "21-24", "relativity": "1.4500"}]},
        headers=actuary,
    ))
    _set_threshold(api_client, admin_headers, 1)
    record("R3", bulk("t-rows", 2))
    record("R4", bulk("t-rows", 3))
    record("R5", imp("t-rows", 4))
    record("R6", seed("t-pq"))
```

</details>

#### Task 2 (commit `ac0440c0`): the reds, against the code before any `audit.record`

`backend/tests/test_nfr498_audit_events.py` (11 tests; the items of PL-1516 as amended). Run alone through
`run-small.sh` on `90036b59`'s source, the failure lines as printed (`pytest -q --tb=line -rf` filtered to
`^E`/`FAILED`/summary):

```text
E       AssertionError: assert [] == ['rate_table:...e-4a8a4337@2']
E         
E         Right contains 2 more items, first extra item: 'rate_table:motor-driver-age-4a8a4337@1'
E         Use -v to get more diff
E       ValueError: not enough values to unpack (expected 1, got 0)
E       ValueError: not enough values to unpack (expected 1, got 0)
E       AssertionError: assert [] == ['rate_table:...e-f355f50d@3']
E         
E         Right contains 2 more items, first extra item: 'rate_table:motor-driver-age-f355f50d@2'
E         Use -v to get more diff
E       ValueError: not enough values to unpack (expected 1, got 0)
E       ValueError: not enough values to unpack (expected 2, got 0)
E       AssertionError: assert [] == ['rating_algo...m:motor-gb@2']
E         
E         Right contains 2 more items, first extra item: 'rating_algorithm:motor-gb@1'
E         Use -v to get more diff
E       AssertionError: assert {'inputs': [{...ote': 'first'} == {'slug': 'ncd...: True}], ...}
E         
E         Omitting 3 identical items, use -vv to show
E         Right contains 2 more items:
E         {'slug': 'ncd-ladder',
E          'steps': [{'consumes': 'ncd_years',
E                     'interpolation': 'none',
E                     'key_expr': ['ncd_years'],...
E         
E         ...Full output truncated (8 lines hidden), use '-vv' to show
E       AssertionError: assert None == {'slug': 'ncd-ladder', 'steps': [{'note': None, 'type': 'table', 'label': 'NCD ladder', 'on_miss': 'error', ...}], 'in...'name': 'ncd_years', 'type': 'int'}], 'outputs': [{'name': 'ncd_factor', 'type': 'relativity', 'required': True}], ...}
E        +  where None = <app.db.models.AuditEventRow object at 0x7fede9186570>.before
E        +  and   {'slug': 'ncd-ladder', 'steps': [{'note': None, 'type': 'table', 'label': 'NCD ladder', 'on_miss': 'error', ...}], 'in...'name': 'ncd_years', 'type': 'int'}], 'outputs': [{'name': 'ncd_factor', 'type': 'relativity', 'required': True}], ...} = <app.db.models.SubGraphVersionRow object at 0x7fede90b4440>.content
E           assert 1 == 6
FAILED backend/tests/test_nfr498_audit_events.py::test_a_seed_records_its_version_with_before_and_after
FAILED backend/tests/test_nfr498_audit_events.py::test_an_import_records_the_baseline_as_before
FAILED backend/tests/test_nfr498_audit_events.py::test_a_bulk_operation_records_the_baseline_and_the_derived_version
FAILED backend/tests/test_nfr498_audit_events.py::test_a_bulk_operation_on_a_bulk_made_baseline_records_that_versions_own_state
FAILED backend/tests/test_nfr498_audit_events.py::test_a_confirmed_manual_edit_records_the_base_version_as_before
FAILED backend/tests/test_nfr498_audit_events.py::test_a_parquet_version_records_its_blob_ref_digest_and_no_rows
FAILED backend/tests/test_nfr498_audit_events.py::test_an_algorithm_save_records_the_previous_version_as_before
FAILED backend/tests/test_nfr498_audit_events.py::test_a_sub_graph_version_one_records_its_full_content_as_after
FAILED backend/tests/test_nfr498_audit_events.py::test_a_sub_graph_version_two_records_version_one_as_before
FAILED backend/tests/test_nfr498_audit_events.py::test_the_chain_verifies_after_every_class
10 failed, 1 passed, 1 warning in 4.38s
```

Causes: seed, import, bulk, bulk-on-bulk (D3's red), edit (RL-1625, item 3b), parquet and algorithm fail
for a missing event (`[] == [...]`, `not enough values to unpack`); 7a (`test_a_sub_graph_version_one_...`)
fails because the stored `after` has no `steps` (`Right contains 2 more items: slug, steps`); 7b
(`..._version_two_...`) fails because `before` is `None`; the chain test fails on the count (1 event of 6).
`test_a_refused_write_records_nothing` passes (the control). No `TypeError` or import error: no red fails on a
signature. The D3 `_to_version`-built-`before` red (a baseline made by an operation) is shown by the
bulk-on-bulk test: it asserts `events[1].before == events[0].after` and
`before["created_by_operation"] is not None`.

#### Task 3 (commit `b335481c`): the events

`_persist_new_version(session, *, table_row, derived, version_number, actor, action, before, threshold,
blob_store)` records after its last flush: `entity_ref=f"rate_table:{slug}@{n}"`, `before` as passed,
`after=_audit_state(created, cells)` = stored wire form without `rows` plus `cells_digest`
(`version_content_hash`). Callers: `seed_from_model` (`rate_table_version.seeded`; `before=None` for a new
table, else the current version's stored state), `import_confirmed` (`.imported`), `manual_edit_confirmed`
(`.edited`, `before` = the `base_version`'s stored state), `bulk_operation` (`.bulk_operation`).
`create_algorithm` records `rating_algorithm.created` (`before` = highest-numbered existing version's
content, `after` = the posted content). The sub-graph `_write` records `before` and `after=row.content`.
Proof: the module 11 passed; item 9's 11 files 24 + 136 + 58 + 95 passed after one call-site fix of the
direct `_persist_new_version` call in `test_persisting_a_derived_version_without_rows_is_an_internal_error`
(its signature moved: `actor`, `action`, `before`); ruff and whole-tree mypy clean.

#### Task 5 (commit `bc2163f1`): the spec text, T-1a to T-1d and T-2

Applied byte for byte from `RL-1515` and `RL-1625` (placeholder `<Slice date>` = 2026-10-11) by a script that
extracts the `text` blocks, in `docs/specs/03-rating-engine.md`: T-1a before `### 4.2`, T-1b and T-2 before
`### 4.3` (T-2 after T-1b's last line), T-1c appended to the Versions-are-immutable bullet, T-1d inserted
mid-line after `not here.`. Anchor counts at `372fa92a` (`grep -cF` over the file): `### 4.2 ...` 1,
`### 4.3 ...` 1, `belong to NFR-498's Audit Event, not here.` 1, `in the same transaction (`06` FR-368).` 1;
T-2's anchor (T-1b's last line) 0 before and 1 after T-1b. First lines of the inserted texts after the apply:
T-1a 1, T-1b 1, T-1c 1, T-1d 1, T-2 1. `python3 scripts/audit-docs.py`: only check 31 (the working-id gap
`1636..9793`) is red, the expected mint artefact; `req-coverage.py` rc 0; `generate-contracts.py --check`
rc 0.

#### Task 4 and write set

Merge-date bound (item 12): the merge commit must be dated on or before 2026-11-04; the lead's report bound is
Fri 2026-10-30 18:00 GMT. `git diff --stat origin/main...HEAD` at `bc2163f1` names only paths of PL-1516's write
set as amended by PL-1627 (22 files; no `docs/contracts/`, no `packages/`, no `frontend/`, no migration).

### Gate

**Task 1 gate:** at `fdc02a74`, recorded under Task 1 above (rc table, classification, the gate-2 window).

**Final gate (PL-1516 item 11; the gate on the merge tree):** `GATE GRANTED 89f40635fd2dc2c81ecd3d1b2f6fbb85c4d2dabd`,
from-lead "2026-10-12 00:17:34 BST"; head `89f40635` (tree `bb688b16cc310a204c94efe9bbdc6da04493baf0`, which includes
`origin/main` `cad75a7e`), run by `scratch/sl1517/slot.sh` under `flock /tmp/slots/gate-1`, slot held
2026-10-12 00:17:44 to 01:07:10 BST (script `end ... rc=1`). Preflight: `PREFLIGHT ok: head guard, clean tree,
/tmp/slots/gate-1 held + GIP_GATE_SLOT exported, containers healthy, upgrade rc 0, 1 head`. The lead's verdict:
from-lead "2026-10-12 01:07:41 BST" (green modulo the mint artefact).

| Stage | START-END (BST) | rc |
|---|---|---|
| red_nfr498 (pre-audit source of the three writers; expect `10 failed, 1 passed`) | 00:17:47-00:17:59 | 1 (expected; count held) |
| green_nfr498 (11 tests) | 00:17:59-00:18:11 | 0 |
| break_no_digest (`cells_digest` blanked) | 00:18:11-00:18:24 | 1 (expected) |
| break_before_dropped (`before=None`) | 00:18:24-00:18:36 | 1 (expected) |
| ruff, mypy (238 files), import_linter | 00:18:37-00:18:38 | 0, 0, 0 |
| pytest | 00:18:38-01:05:16 | 1 (13 failed, 5708 passed, 6 skipped) |
| audit_docs | 01:05:16-01:05:36 | 1 (check 31 only, `gap ... between 1643 and 9793`; non-31 failures 0) |
| req_coverage, contracts | 01:05:36-01:05:45 | 0, 0 |
| fe_install, fe_generate, fe_lint, fe_typecheck | 01:05:45-01:06:20 | 0, 0, 0, 0 |
| fe_test (691 of 691) | 01:06:20-01:07:06 | 0 |
| fe_build | 01:07:06-01:07:09 | 0 |

**Broken-input proofs (three):** `red_nfr498` (10 of 11 tests fail on the code before any `audit.record`: no event row,
a steps-less sub-graph `after`, no sub-graph `before`, a chain of 1 event instead of 6; the control passes),
`break_no_digest` and `break_before_dropped` (each turns the module red when the digest or the baseline `before` is
removed from the writer). **Classification of the 13 pytest reds:** the same 13 audit-docs-on-tree tests as in the Task 1
gate, each failing on check 31, the unminted working id of this ledger (the mint artefact, cleared by this mint): none is
a timing or NFR test and none is in this slice's files, so no quiet re-run applied. The audit-docs line of the table is
that same check 31. At the mint head, `python3 scripts/audit-docs.py` was run once under the gate-2 flock, see the Build log.

### Audit

To be written by `auditor-sl1517` (an auditor seat; the executor does not self-audit).

Lead verdict: (pending)

### Build log

- 2026-10-11 — `a0d7f37b` activation: `PL-1516` `draft -> active` (front matter only), `SL-1517` `draft -> active`
  with a dated line citing the 19:24:24 BST GO, this ledger opened (`document-ids.md` §1.2a: both transitions
  forward).
- 2026-10-11 — `fdc02a74` Task 1; `90036b59` Task 1b (8 cmp = 0, control = 1; plan defect E3 step 5 recorded
  above); `ac0440c0` Task 2 (10 red, 1 control); `b335481c` Task 3 (11 green); `bc2163f1` Task 5 (T-1a..d, T-2).
- 2026-10-11 — `a44314d0` ledger filled, slot script written and its abort proved. Ready to queue.
- 2026-10-12 — `74b6be2a` merge of `origin/main` `cad75a7e` (conflicts: `docs/INDEX.md` by script, `examples/fremtpl2/model.py`); two call sites that arrived on main now pass the Principal (`examples/fremtpl2/model.py` `seed_demo_rate_tables`, `backend/tests/test_rating_version_change_summary_route.py` line 74): the second file is outside PL-1516 and PL-1627's write set, a one-argument consequence of the merge, reported to the lead.
- 2026-10-12 — `89f40635` the Task 1 gate record. Final gate at `89f40635` (above).
- 2026-10-12 — **Named widening (disclosed at the mint).** `backend/tests/test_rating_version_change_summary_route.py`
  line 74 (`principal.id` becomes `principal`), outside PL-1516 and PL-1627's write set, is RULED a named widening
  by the lead, from-lead "2026-10-12 00:17:34 BST", citing the maintainer's "2026-10-12 00:17:53 BST": a forced
  merge-interaction adaptation (SL-1503's new test, merged as #1285, meeting this slice's Principal threading), not
  new scope. `examples/fremtpl2/model.py` `seed_demo_rate_tables`'s call is in the write set.
- 2026-10-12 — mint turn (from-lead "2026-10-12 01:07:41 BST"): merged `origin/main` `80c77c8e` (#1287; the only
  conflict, `docs/INDEX.md`, by script), minted LG 9793 as LG-1646, closing acts: this ledger `closed`, the `SL-1517`
  row `closed` with a dated line, `PL-1516` and `PL-1627` left `active` (their precedent).

## PRs

(none yet)
