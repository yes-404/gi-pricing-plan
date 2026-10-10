---
id: PL-1516
family: plan
kind: leaf
title: WK-1178 — NFR-498 Audit Events on rate table version and rating algorithm writes (NFR-498, FR-368): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: planner
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1263, CR-1212, PL-1419, SL-1391, FD-1513, RL-1514, RL-1515, SL-1517]
---

# WK-1178 — NFR-498 Audit Events on rate table version and rating algorithm writes, leaf plan

Filed under working id 9514 (this plan; minted as PL-1516) and slice working id 9515 (its `SL-` row under WK-1178
in [`../roadmap.md`](../roadmap.md), `draft`; minted as SL-1517), both reserved by the lead. The finding it fixes
is FD-1513 (#1201, branch `fd-9529-nfr498-rate-table-audit`, read at
`9bf47b1fddca0670ca01431cf3d58cb974530716`). Its correcting record for `CR-1212` is RL-1514
(#1203, branch `dm-9519-cr1212-nfr498`, read at `df4f5a53`). All five
are minted on 2026-10-08 (batch B4: FD-1513, RL-1514, RL-1515, PL-1516, SL-1517). Every repository line number was read at `origin/main` `5fe56b87`, the `tree:` above.

## Delta, 2026-10-05 (after 18:04:32 BST, pre-mint): DP-1..DP-5 ruled; DP-2's hash named; Task 1 gated; A-2 first

This plan is still an unmerged draft. This delta records the ruling and what it changes. It
deletes no text: each part it changes keeps its words and gains a pointer back here. Where the
delta and the text below disagree, **the delta governs**. Repository facts in this delta were
re-read at `origin/main` `fb178c360f6fd5b2fdb7ae60eea924811a65492f`;
`git diff --stat 5fe56b87 fb178c36 -- backend packages examples scripts docs/specs/03-rating-engine.md`
prints nothing, so every line number in §"Task 0 at planning time" still holds.

### D1. The ruling, quoted

The maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
"2026-10-05 18:04:32 BST — PL 9514 (#1207 @a2d2e050) DPs 1–5 RULED; Task 1's Principal
threading accepted", quoted verbatim:

> DP-1: the SINGLE WRITER (_persist_new_version, rate_tables.py :670). The caller passes the action and the baseline. One site cannot miss a caller.
> DP-2: the wire form WITHOUT rows, PLUS a cells content digest (your rec, the tamper-evident minimum). Use the EXISTING hash, no new hashing: rate_tables.py already imports version_content_hash from app.platform.diff_cache (:35, used at :340-341), and RateTableVersion carries cells: BlobRef (model_schema/rating.py:899ff). The digest is version_content_hash over the version's cells, or the BlobRef's own content address if that is the same value (the planner states which, with file:line). For algorithms and sub-graphs, the stored content.
> DP-3: the DISTINCT actions: rate_table_version.seeded, .imported and .bulk_operation, and rating_algorithm.created.
> DP-4: YES. T-1 is a dated 03 note naming the actions (precedents 03:846 and :874), carried by ONE RL that also records DP-1 to DP-5. NFR-498's text is unchanged. Reserve the id; a DM files it.
> DP-5: (a). create_sub_graph's after gains the full content (steps included), and create_version gains a before (N−1). A steps-less after is a summary, not the state NFR-498 names.
> Task 1, threading Principal through the four services with NO behaviour change (about 25 call-site args): ACCEPTED as a refactor commit BEFORE the reds, with the full suite green at that commit in the gate.
> CONTENTION: as tabled, with A-2 FIRST. The one shared test with S7 (test_diff_cache.py): whichever merges second rebases it, named in both. The bound of 4 Nov holds.
> planner-9529's cd into its own worktree: noted; stopping it is fine.

The `RL-` that DP-4 names is **RL-1515** (reserved by the lead as working id 9501; branch
`dm-9501-pl9514-audit-actions`). It records DP-1 to DP-5 and carries T-1.

So: **DP-1 (a)**, **DP-2 (a) plus a cells digest** (the plan's (b) with the existing hash, not a
new `cells_sha256`), **DP-3 (a)**, **DP-4 (a)**, **DP-5 (a)**. Every "if DP-n is ruled …" branch
below that names another option is void.

### D2. DP-2: which hash — `version_content_hash`, because the two are different values

Read at `fb178c36`:

- `version_content_hash(cells)` (`backend/src/app/platform/diff_cache.py:46-56`) is
  `sha256` over `json.dumps(sorted(cells, …), sort_keys=True, separators=(",", ":"))`: the
  **cells themselves**, canonical, row order ignored. Its docstring (`:47-52`): "a rows-stored
  version and its parquet twin hash identically (FR-232's same-artifact guarantee)".
  `rate_tables.py` imports it (`:35`) and the diff keys its cache on it (`:340-341`).
- The BlobRef's content address is `BlobRef.sha256` (`packages/model-schema/src/model_schema/refs.py:189-197`).
  `BlobStore.put` sets it to `hashlib.sha256(body).hexdigest()` over the **stored body**
  (`backend/src/app/platform/blobs.py:158`, returned at `:189`). For a rate table that body is
  the **parquet file bytes** from `_cells_to_parquet` (`rate_tables.py:578-591`, called at
  `:742-747`). A rows-stored version has **no** BlobRef at all (`cells=blob_ref` stays `None`,
  `:734`, `:759`).

They are therefore **not** the same value: one hashes canonical JSON of the cells and exists for
every version; the other hashes a parquet encoding and exists only above the threshold. Per the
ruling, the digest is **`version_content_hash` over the version's cells**. The parquet
version's `cells` BlobRef stays in the dumped wire form as well (it is a field of the wire form),
so a parquet version's state carries both.

The digest key in the payload is **`cells_digest`** (this plan's proposal). T-1 is the spec for
what `before` and `after` carry, so **RL-1515's T-1 names the key**; if it names another, T-1's
name replaces `cells_digest` everywhere below, and the dispatch record says so.

### D3. A correction found while folding DP-2: `before` is the **stored** wire form, not `_to_version`'s

The plan's Task 3 Step 1 builds a baseline's `before` from `_to_version` (`table` at `:442`,
`baseline` at `:827`, and `_to_version(...)` for a re-seed). At `fb178c36`, `_to_version`
(`rate_tables.py:612-640`) is **not** the stored wire form. Its docstring (`:615-622`) says it is
the transformation input, "cells materialised inline … so the in-memory claim is never stored":

- it always sets `storage=RateTableStorageMode.ROWS` and `rows=…` (`:629`, `:633`), even for a
  parquet-stored version, and passes no `cells` BlobRef;
- it passes no `created_by_operation` and no `created_by_import` (`:625-640`).

So a baseline that is parquet-stored, or was itself made by an import or a bulk operation,
would have a `before` that differs from that same version's own earlier `after`. The chain
would then record two different states for one immutable version. Acceptance items 1–3 do not
catch it, because their baselines are rows-stored seeds.

**The fix is one constructor of the stored wire form.** There is none today: the only
`RateTableVersion(` constructors in `backend/src` are `rate_tables.py:170`, `:447`, `:625` and
`:750` (`git grep -n 'RateTableVersion(' fb178c36 -- backend/src`). Task 3 Step 1 becomes:

```python
def _stored_version(
    version_row: RateTableVersionRow, cells: list[dict[str, str]]
) -> RateTableVersion:
    """The version's §4.2 wire form as stored (FR-232): inline rows when rows-stored,
    the parquet BlobRef otherwise, with its provenance fields."""
    return RateTableVersion.model_validate(
        version_row.definition
        | {
            "storage": version_row.storage,
            "rows": _wire_rows(cells) if version_row.storage == "rows" else None,
            "cells": version_row.cells,
            "change_note": version_row.change_note,
            "seeded_from": version_row.seeded_from,
            "created_by_operation": version_row.created_by_operation,
            "created_by_import": version_row.created_by_import,
        }
    )


def _audit_state(version: RateTableVersion, cells: Sequence[dict[str, str]]) -> dict[str, Any]:
    """NFR-498's state of one version (RL-1515, DP-2): the wire form without inline
    rows, plus the cells' content digest — the diff cache's existing hash."""
    return version.model_dump(mode="json", exclude={"rows"}) | {
        "cells_digest": version_content_hash(cells)
    }
```

`model_validate` over the row's stored JSON is used because `created_by_operation` is the
`BulkOperation` discriminated union (`Annotated[...]`, `model_schema/rating.py:828`), which
has no `.model_validate` of its own. `definition` is `RateTable(...).model_dump()`
(`rate_tables.py:690-698`), whose seven fields (`rating.py:712-718`) are all
`RateTableVersion` fields, so `extra="forbid"` accepts the merge. Whether the re-validated
form equals what `_persist_new_version` returns today is exactly what item 9's unchanged
suite checks once the return is routed through it (below).

- `_persist_new_version` takes `actor: Principal, action: str, before: dict[str, Any] | None`
  (the baseline's **state**, already computed by the caller: "The caller passes the action and
  the baseline"). Its return statement (`:750-764`) becomes `created = _stored_version(version_row, cells)`;
  it records with `after=_audit_state(created, cells)` and `before=before`, then returns
  `created`. Item 9's unchanged suite proves the return value did not move.
- `seed_from_model`: `before=None` for a new table. For a re-seed, read the current version
  before `version_number` is computed:
  `prior = await _load_version(session, table_row.id, table_row.current_version, slug)`,
  `prior_cells = await _load_cells_of(session, prior, RateTable.model_validate(prior.definition), blob_store)`,
  `before = _audit_state(_stored_version(prior, prior_cells), prior_cells)`.
- `import_confirmed`: `cells = cast(list[dict[str, str]], table.rows)` (`_to_version`
  materialises them), `before = _audit_state(_stored_version(version_row, cells), cells)`.
- `bulk_operation`: the same, over `baseline_row` and `baseline.rows`.

The imports gain `audit`, `JobSource` and `Principal` (the import block,
`rate_tables.py:12-70` at `fb178c36`).

### D4. The Acceptance Standard, as amended by this delta

- **"The state"** (the paragraph at "The state" of a rate table version) is now
  `_audit_state(_stored_version(row, cells), cells)`: the stored wire form without `rows`,
  plus `cells_digest`. The test module's `_state(version, cells)` is
  `version.model_dump(mode="json", exclude={"rows"}) | {"cells_digest": version_content_hash(cells)}`,
  importing `version_content_hash` from `app.platform.diff_cache`; for a rows-stored version
  `cells` is `version.rows`.
- **Item 1 gains:** `events[1].before == events[0].after` (one immutable version, one state,
  wherever it is read), and `events[0].after["cells_digest"] == version_content_hash(first.rows)`.
- **Item 3 gains (D3's red):** a bulk operation whose **baseline was itself made by a bulk
  operation** (`@1` seed → `@2` uplift → `@3` uplift on `@2`) records the `@3` event with
  `before == <the @2 event's after>`, so `before["created_by_operation"]` is not null. Red
  first with item 3. A `_to_version`-built `before` fails it by the missing
  `created_by_operation`.
- **Item 4 gains:** a parquet version's state carries both `after["cells"]` (the BlobRef) and
  `after["cells_digest"]`, and the digest equals `version_content_hash` over the cells read back
  from the blob (`blob_store.read` then `rate_tables._cells_from_parquet`). A second bulk
  operation on that parquet version records `before == <the parquet version's after>`, with
  `before["storage"] == "parquet"`. A `_to_version`-built `before` fails it by `"rows"`.
- **Item 7 is unconditional (DP-5 (a)) and is two reds:**
  - **7a.** `create_sub_graph` leaves a `sub_graph.created` event with `before is None` and
    `after == <the stored row's content>`, so `after["steps"]` is present and equals the
    posted steps. Red first: at the base `after` has no `"steps"` key
    (`platform/sub_graphs.py:95-99`).
  - **7b.** `create_version` leaves a `sub_graph.created` event for `@2` whose `before` equals
    `@1`'s stored content (`steps` included) and whose `after` equals `@2`'s. Red first: at
    the base the event has no `before` (`:88-100`).
  - `backend/tests/test_sub_graphs_service.py:71-73` still passes **unedited**, because
    `content` is `body.model_dump(mode="json")` (`sub_graphs.py:74`), which keeps
    `change_note`, `inputs` and `outputs`.
- **Item 9 is now gated (Task 1's ruling):** at Task 1's commit, the **full** two-half gate
  (`CLAUDE.md` §11) passes through the gate-runner, in a held gate slot, and the ledger records
  each rc and the tree. Item 9's selection stays the quick check before it.
- **Item 11** is unchanged (the gate again on the merge tree).
- **Every red's STOP (self-review 7) now covers the digest too:** if `cells_digest` of a
  re-read version differs from its earlier `after`, that is the canonical-form STOP, reported
  to the lead before any change to the hash.

### D5. Tasks, as amended

- **Task 1** (the refactor) **is its own commit, before Task 2's reds, with no behaviour
  change.** New **Step 5b**: run the full gate through the gate-runner at that commit (check
  the slots first, Task 0 Step 3) and record each rc and the tree in the ledger. No red is
  written until it is green. Step 6's commit message stays.
- **Task 2** adds the tests of D4 (items 1, 3 and 4's new assertions; 7a and 7b) to the module.
  Its expected failures (Step 2) gain: 7a fails on the missing `"steps"` key; 7b on
  `before is None`.
- **Task 3 Step 1** is D3's code, which replaces the `_audit_state` sketch and the callers'
  `before=table` / `before=baseline` lines. **Step 3** (sub-graphs) is unconditional: `_write`
  gains `before: dict[str, Any] | None` and records `before=before, after=row.content`;
  `create_sub_graph` passes `before=None`; `create_version` reads
  `previous = await _row(session, workspace_id, slug, latest)` (`sub_graphs.py:150`) after the
  `latest is None` check and passes `before=previous.content`.
- **Task 5** is unconditional: apply RL-1515's T-1 byte for byte under `spec-change`.

### D6. Contention, as ruled

- **A-2 (PL-1464) first.** Activation need 5's order is ruled, no longer recommended.
- **The one test shared with S7** (`SL-1391` / `PL-1419`):
  `backend/tests/test_diff_cache.py::test_diff_is_computed_on_miss_and_served_from_the_cache_on_hit`
  (`:129`, its `seed_from_model` call at `:153`). **Whichever of SL-1517 and `SL-1391` merges
  second rebases that test** onto the first's version and re-runs the full gate on the merged
  tree. PL-1419 names it too (the lead's dispatch of S7).
- The 4 November bound holds (unchanged).

### D7. Activation needs, replacing need 3 and fixing need 5

1. FD-1513 minted (unchanged).
2. RL-1514 minted (unchanged).
3. **RL-1515 minted.** It rules DP-1 to DP-5 and carries T-1. This replaces "DP-1 to DP-5
   ruled".
4. The emergency slice (SL-1427) merged (unchanged).
5. **A-2 (PL-1464) merged first**, and this slice re-reads `create_algorithm` and
   `create_version` at dispatch.
6. The lead's GO (unchanged), naming D6's shared test.
7. Active by a dated line (unchanged).

**What this delta removes:** DP-2's no-digest form (a) as written; the `before=table`,
`before=baseline` and `_to_version` re-seed sources; every "DP-5 (a) only" and "DP-4 (b)"
branch; and the sentence "If DP-2 or DP-3 is ruled another way …".

## Delta 2, 2026-10-05 (after 18:12:58 BST, pre-mint): `_stored_version` accepted, with one STOP: no route response may move

This plan is still an unmerged draft. This delta deletes no text, and it governs where it
disagrees with the text below or with the first delta. Repository facts were read at
`origin/main` `fb178c360f6fd5b2fdb7ae60eea924811a65492f`.

### E1. The ruling, quoted

The maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
"2026-10-05 18:12:58 BST — PL 9514 @1cabc274: the stored-wire-form constructor accepted as
implementation, with one STOP; RL 9501 @1e6a59df: 03:343 IS amended (T-1d), not read around",
quoted verbatim:

> 1. DP-2's hash = version_content_hash (diff_cache.py:46-56), not BlobRef.sha256 (parquet bytes, absent for rows): ACCEPTED; key cells_digest.
>    _stored_version(row, cells): ACCEPTED as implementing the ruled wire form, not a new DP. Read at origin/main: _to_version (rate_tables.py:612-640) is, BY ITS OWN DOCSTRING, a transformation input ("always presents rows … the in-memory claim is never stored"), so it is the wrong source for audit state, and a separate stored-form constructor is right. Its reds (a bulk on a bulk-made baseline, a bulk on a parquet baseline, events[1].before == events[0].after) are ACCEPTED.
>    ONE STOP: routing _persist_new_version's RETURN through _stored_version must not change any route's RESPONSE. The proof is the unchanged suite PLUS one explicit comparison of a PARQUET-stored and an IMPORT-made version's HTTP response at the base and at the head (the existing suite may not cover those shapes). If any response moves, STOP to me: that is a wire change and possibly its own finding, not part of this slice.
> 2. RL 9501, 03:343 ("the before/after cells and the actor belong to NFR-498's Audit Event, not here"): I do NOT read around it. Read literally, it places the CELLS in the event, while DP-2 carries a digest. So RL 9501 adds T-1d, a dated note at :343 saying the Audit Event carries the cells BY the immutable version's reference PLUS cells_digest (their canonical content hash), not inline, citing T-1b and DP-2. Its anchor counts 1, as for T-1a to T-1c. That keeps the spec saying what the code will do, with no silent reading.
>    T-1a, T-1b and T-1c: ACCEPTED as drafted.

So D2 (the hash), D3 (`_stored_version`) and D4's three D3 reds stand as written. The key is
`cells_digest`.

### E2. The routes that return a version, enumerated at `fb178c36`

From `backend/src/app/api/rate_tables.py`, every route decorator (`@router.`) in the file:

| Route | Decorator | Returns a version? | Body returned |
|---|---|---|---|
| `POST /rate-tables/{slug}/seed-from-model` | `:70-76` | **yes**, 201 | `response_model=RateTableVersion` (`:74`); `return version` (`:109`) |
| `POST /rate-tables/{slug}@{version}/bulk-operation` | `:112-117` | **yes**, 201 | `created.model_dump(mode="json")` (`:156`) |
| `POST /rate-tables/{slug}@{version}/import` with `confirm: true` | `:205-209` (`confirm`, `:219`) | **yes**, 201 (`:264`) | `created.model_dump(mode="json")` (`:265`) |
| the same route with `confirm` false | `:205-209` | no: an `ImportPreview` (`:241-251`) | not routed through `_persist_new_version` |
| `GET /rate-tables/{slug}@{version}/export/csv`, `/export/xlsx` | `:159-163`, `:180-184` | no: the cells as a file | not routed through it |
| `GET /rate-tables/{slug}@{version}/diff` | `:268-277` | no: a `RateTableDiff` or a `Job` | not routed through it |

**There is no version GET or list route at `fb178c36`**: no `@router.get` in the file returns a
`RateTableVersion`, and no other module under `backend/src/app/api/` declares a
`/rate-tables` route (`git grep -n 'rate-tables' fb178c36 -- backend/src/app/api` matches only
this file and two prose lines in `api/traces.py:12`, `:21`). So the three version-returning
routes are the comparison's set. **Task 0 Step 2 re-enumerates at the dispatch tree**: an open
plan adds rate-table routes (WK-675 S4, PL 9582: `cells_page` and three handlers). Any route
that returns a stored version at that tree joins the set, and the ledger names it.

### E3. The STOP, as a task step: new Task 1b, before Task 2's reds

**Task 1b: `_persist_new_version` returns the stored wire form; no route response moves.** It
is its own commit, after Task 1's refactor commit and **before** Task 2's reds, so that every
red lands on the new return path.

- [ ] **Step 1:** Add `_stored_version` (D3's code). Change only `_persist_new_version`'s return
  statement (`rate_tables.py:750-764`) to `return _stored_version(version_row, cells)`. No audit
  call yet, and no other edit.
- [ ] **Step 2:** Item 9's pytest command, unchanged, then `uv run mypy && uv run ruff check .`.
  All pass, with no assertion edited.
- [ ] **Step 3: The base-vs-head response comparison (item 13).** Make two worktrees: **BASE**
  is the slice's base (the `origin/main` commit Task 0 recorded); **HEAD** is Step 1's tree. In
  each, put the same **untracked** harness file at `backend/tests/test_zz_pl9514_response_compare.py`
  (copied from the executor's own `mktemp -d`; it is never committed, and the ledger quotes it
  in full). The harness mirrors `backend/tests/test_api_rate_tables.py`'s synchronous form at
  `fb178c36`: the `api_client` and `workspace_id` fixtures, the `actuary` (`:41-45`) and
  `admin_headers` (`:56-62`) header fixtures, `_seed_approved_model(workspace_id, family, _LEVELS)`
  (`:160`), `_seed_body(family)` (`:205-210`) and `_set_threshold(api_client, admin_headers, 1)`
  (`:848-857`), imported from that module. It drives the HTTP routes in E2 in this fixed order,
  with fixed slugs and one fixed `family` (`"mf-pl9514cmp"`), never `_table_slug()`'s random
  suffix:
  1. seed `t-rows` (rows-stored, default threshold) → `R1`;
  2. import-confirm a fixed CSV on `t-rows@1` → `R2` (**import-made**, rows-stored);
  3. set `rate_tables.cell_threshold` to 1, then bulk `uplift_table` `{"percentage": "0.10"}` on
     `t-rows@2` → `R3` (**parquet-stored**, bulk-made on an import-made baseline);
  4. bulk the same on `t-rows@3` → `R4` (parquet, on a parquet baseline);
  5. import-confirm the same CSV on `t-rows@3` → `R5` (**import-made and parquet-stored**);
  6. seed a fresh `t-pq` with the threshold still 1 → `R6` (parquet-stored seed).

  It writes each response's **raw body bytes** (`response.content`) and its status code to
  `<scratch>/<BASE|HEAD>/R<n>.json`. The one value that varies between two runs is
  `seeded_from.seeded_at`, which is `datetime.now(UTC)` (`rate_tables.py:144`). The harness pins
  it by monkeypatching `app.platform.rate_tables.datetime` with a subclass whose `now()` returns
  `datetime(2026, 10, 5, 12, 0, tzinfo=UTC)`, in both trees. Nothing is normalised after the
  fact. Run it alone in each tree:
  `OMP_NUM_THREADS=1 nice uv run pytest backend/tests/test_zz_pl9514_response_compare.py -q`
  (check the slots first, Task 0 Step 3). Then `cmp` each `BASE/R<n>.json` with
  `HEAD/R<n>.json`, and record the six `cmp` exit codes and the status codes in the ledger.
  **Every one must be 0: byte for byte, every field.**
  - **If any response differs: STOP to the maintainer (by delegation)**, through the lead,
    quoting both bodies. It is a wire change, and possibly its own finding; it is not fixed in
    this slice. Task 2 does not start.
  - **Positive control:** in the HEAD tree only, change one byte of `_stored_version`'s
    output (for example `change_note=version_row.change_note + " "`), rerun, and confirm `cmp`
    reports a difference for `R1`–`R6`. Record it, then revert. A comparison that has never
    shown a difference has not been tested (`CLAUDE.md` §13).
  - Then delete the harness from both worktrees. `git status --short` in HEAD shows only
    Step 1's edit. Remove the BASE worktree.
- [ ] **Step 4:** Commit: `refactor(rating): _persist_new_version returns the stored wire form (NFR-498 prep; no response moves)`.

Task 3 Step 1 (D3's code) then adds only the `audit.record` call and the callers' `before`; the
return statement is already Task 1b's.

### E4. Acceptance item 13 (added)

13. **No route response moves (the 18:12:58 STOP).** The ledger holds Task 1b Step 3's six `cmp`
    exit codes, all 0, for the responses of seed, import-confirm and bulk-operation (E2's set as
    re-enumerated at the dispatch tree), at the slice's base and at Task 1b's commit. The set
    covers a parquet-stored version (`R3`–`R6`) and import-made versions (`R2`, `R5`). It also holds
    the positive control's non-zero `cmp`. Item 9's suite passes unedited at Task 1b's commit.
    Any non-zero `cmp` outside the control is a STOP (E3), never a pass.

### E5. T-1d (RL-1515): the spec text Task 5 applies

RL-1515 adds **T-1d** at `03:343` (at `fb178c36` that line reads "belong to NFR-498's Audit Event,
not here. This example's version was edited by"; the sentence is "the before/after cells and the
actor belong to NFR-498's Audit Event, not here"). T-1d says that the Audit Event carries the cells
**by the immutable version's reference plus `cells_digest`** (their canonical content hash), not
inline, citing T-1b and DP-2. Task 5 applies T-1a to T-1d byte for byte from RL-1515. Item 1's
`after` assertions are what T-1d describes: the `entity_ref` addresses the version, and
`cells_digest` is its hash.

### E6. What changes elsewhere

- **Task 1** stays as written. **Task 1b** is new (E3). **Task 2** starts only after Task 1b's
  comparison is all 0.
- **Task 6 Step 2's ledger** gains Task 1b's harness, the six `cmp` codes and the control.
- **The write set** does not change: the harness is untracked and never committed. Item 10's
  `git diff --stat` therefore shows no `test_zz_*` file.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every red is seen failing, by its stated cause, before
> the code that turns it green), `python-package` (where the code goes; `pricing-core` is not
> touched), `fastapi-service` (Task 1's route call sites), `dev-commands` (the two-half gate,
> the DB stack) and `git-hygiene`. Read [`README.md`](README.md)'s unchecked conventions
> before the first step. The executor is spawned from `.claude/roles/executor.md`.

**BOUND: this slice merges before the P2 code freeze, Wednesday 4 November 2026** (the
maintainer (by delegation), 17:45:06 BST entry, item 1, quoted below). A dispatch that cannot
meet the bound is reported to the lead at once; it is not carried silently into P3.

## Goal

Every write that NFR-498 names and that the platform builds today emits one Audit Event
with before and after state, in the same transaction as the write (`06` R2):

- a rate table version created by **seed** (`seed_from_model`), by **import**
  (`import_confirmed`) or by a **bulk operation** (`bulk_operation`); all three persist
  through one writer, `_persist_new_version`;
- a **Rating Algorithm** saved by `create_algorithm`;
- and, under DP-5 (a), a **Sub-graph** version, whose event exists today but carries no
  `before` and only a summary `after`.

This discharges FD-1513 (MEDIUM; owner WK-1178).

**Architecture.** One `audit.record` call per write path, inside the unit of work that
already holds the write. For rate tables the call goes in `_persist_new_version`, the one
writer the three routes funnel into, and each caller hands it the baseline it already
holds as `before`. The four services take the acting `Principal` instead of a bare
`created_by` UUID, because `audit.record` needs a `Principal` (`audit.py:56`). `created_by`
is then read from `actor.id`. No shape is added to `model-schema`. No migration is needed.

**Tech Stack.** Python 3.12, FastAPI, SQLAlchemy 2 async, PostgreSQL 16 (the `audit_events`
hash chain), pytest.

**Spec, finding and rulings:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §9 **NFR-498** (`03:1339`,
  read in full: it has **no** dated amendment): "Audit: algorithm edits, rate table versions,
  bulk operations, compilations, approvals, deployments, rollbacks, and routing changes all
  emit Audit Events with before/after state."
- [`../specs/06-governance.md`](../specs/06-governance.md) **FR-368** (`06:154`) and R2,
  which `backend/src/app/platform/audit.py:3-5` quotes: "Every governed transition writes its
  event in the same database transaction as the change. If the audit write fails, the change
  fails."
- `03` §4.11's sub-graph sentence (`03:846`) and §4.12's action catalogue (`03:874`), the two
  precedents for naming audit actions in the spec (DP-4).
- FD-1513's essay, §"Per class" and §"Disposition — ruled 2026-10-05 17:45:06 BST (pre-mint)",
  on #1201 at `9bf47b1f`. **That disposition is this slice's scope.**
- RL-1514 (#1203 @`df4f5a53`), §"Acceptance — the violation that must become
  detectable". It states the four violations this slice's reds make detectable. It also says
  it does not decide the sub-graph question; DP-5 below carries that question.

## The maintainer's decision this plan rests on, quoted

The maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
"2026-10-05 17:45:06 BST — FD 9529 (NFR-498, #1201 @be1fba43): MEDIUM and carry-forward to
WK-1178 accepted, with a P2 landing bound; CR-1212 correcting RL yes; A-2 does not absorb",
quoted verbatim:

> Spot-checked at origin/main: platform/rate_tables.py and platform/rating_algorithms.py contain 0 occurrences of audit or record(, and neither imports app.platform.audit (approvals, datasets, deployments, environments and others do). The finding is real.
> 1. Your decision is ACCEPTED: MEDIUM; carry forward, owner WK-1178; the 13 verdict is "deferred with an owner". ADDED BOUND: the fix lands BEFORE THE P2 CODE FREEZE (Wed 4 Nov). An unaudited rate-table or algorithm change is exactly what the exit demo's governance story claims cannot happen, so this is not a P3 carry. The register's Decision cell carries the bound; the P2 phase closure record lists it.
> 2. The fix slice: red-first per class (seed_from_model, import_confirmed, bulk_operation, create_algorithm), with before/after state asserted. Its read-first list also covers the sub-graph create and version paths (api/sub_graphs.py), since they are algorithm edits too: in or out with a reason, not silently. It runs after the emergency slice and serialises against A-2 on rating_algorithms.py, named both ways.
> 3. CR-1212: YES, a correcting RL (corrects: CR-1212; CR-1212 gains corrected_by:), filed by a DM when a seat frees, citing FD 9529.
> 4. A-2 does NOT absorb the audit event. Agreed.

## Status

*(Delta of 2026-10-05, D1: DP-1 to DP-5 are now ruled; this sentence is history.)* `draft`. **DP-1 to DP-5 are open** (§"Decision points"). They are the decision-maker's; the
planner does not rule them. DP-5 is the sub-graph in/out question of item 2. The plan moves to
`active` only through a separate activation PR, after every activation need below holds.

### Activation needs, in order

1. **FD-1513 minted** (#1201). Its register row's Decision cell carries the bound.
2. **RL-1514 minted** (#1203): `corrects: CR-1212`, and `CR-1212` gains `corrected_by:`
   (item 3).
3. *(Delta of 2026-10-05, D7: replaced by "RL-1515 minted".)* **DP-1 to DP-5 ruled** by a decision-maker's `RL-`. If DP-4 is ruled (a), that `RL-`
   carries T-1's text (§"Decision points"), and Task 5 applies it byte for byte.
4. **The emergency slice merged** (SL-1427 / PL-1426, #1196 @`68b2f860`). Item 2: "It runs
   after the emergency slice".
5. *(Delta of 2026-10-05, D6, D7: A-2 first is ruled.)* **The A-2 order** (item 2: "serialises against A-2 on rating_algorithms.py, named both
   ways"). A-2 is PL-1464 (#1178, read at `176a6a75`). Both slices edit `create_algorithm`
   (`platform/rating_algorithms.py:94`), and under DP-5 (a) both edit `create_version`
   (`platform/sub_graphs.py:127`). The recommended order is **A-2 first**: A-2 is further
   along and is the larger change. This slice then re-reads both functions at dispatch.
   If the lead orders it the other way, A-2's dispatch record re-reads them instead.
   A-2's plan gains the reverse naming at its next fold (the lead's brief).
6. **The lead's GO**, written in the dispatch record. The record names every shared path in
   §"Write set" and the check that the second merge re-runs.
7. **Active by a dated line**: this plan and the `SL-` row move to `active` in a separate
   activation PR, citing the GO.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree, with the DB
stack up (`dev-commands`). "Red first" means that the named test was run, and it failed **for
the stated cause**, before the code that turns it green existed. A failure with the right
status and a different cause (for example a `TypeError` from a signature) is a plan defect
([`README.md`](README.md) rule 2). Task 1 exists so that no red fails on a signature. The
ledger records each red, with the failure line as printed.

The test module is `backend/tests/test_nfr498_audit_events.py` (new, so that no concurrent
slice's test file is edited). Every test in it carries `@pytest.mark.req("NFR-498")`, and
the tests in items 1–3 and 5 also carry `@pytest.mark.req("FR-368")`. Command for items 1–8:
`uv run pytest backend/tests/test_nfr498_audit_events.py -q`.

*(Delta of 2026-10-05, D4: the state is now the stored wire form plus `cells_digest`.)* "The state" of a rate table version means `_audit_state(v)`, which is
`v.model_dump(mode="json", exclude={"rows"})` of its `RateTableVersion` wire form (DP-2 (a)).
"The content" of an algorithm or a sub-graph version means its stored `content`. If DP-2 or
DP-3 is ruled another way, the ruled form replaces these names in every item below, and the
dispatch record says so.

1. **Seed, red first.** A first seed of a new table leaves exactly one event with
   `action == "rate_table_version.seeded"`, `entity_ref == "rate_table:<slug>@1"`,
   `before is None`, `after == _audit_state(<the returned version>)`, and
   `actor["id"] == str(principal.id)`. A re-seed of the same table (version 2) leaves a
   second event whose `before` is version 1's state and whose `after` is version 2's state.
   Red first: at the base, the query returns no row.
2. **Import, red first.** `import_confirmed` on `<slug>@1` leaves one event with
   `action == "rate_table_version.imported"`, `entity_ref == "rate_table:<slug>@2"`,
   `before == _audit_state(<version 1>)` (RL-1514: "an event whose `before` is not the
   baseline version" is the violation), and an `after` whose `created_by_import` is not null.
   Red first.
3. **Bulk operation, red first.** `bulk_operation` (`uplift_table`, `{"percentage": "0.10"}`)
   on `<slug>@1` leaves one event with `action == "rate_table_version.bulk_operation"`,
   `before ==` the baseline's state, and an `after` whose `created_by_operation` is not null
   (RL-1514: "an event that lacks `baseline` as `before` and the derived version as `after`").
   Red first.
4. **The parquet path.** With the workspace threshold set to 1 (`rate_tables.cell_threshold`),
   a bulk operation's event has `after["storage"] == "parquet"`, a non-null `after["cells"]`
   (the blob ref), and no `"rows"` key. Red first, together with item 3.
5. **Algorithm, red first.** `create_algorithm` with `valid_algorithm()`
   (`backend/tests/test_rating_algorithms.py:64`) leaves one event with
   `action == "rating_algorithm.created"`, `entity_ref == "rating_algorithm:motor-gb@1"`,
   `before is None`, and `after == <the content posted>`. Version 2 of the same slug leaves an
   event whose `before` is version 1's content. Red first.
6. **A refused write leaves no event (control; it passes at the base too, and it must still
   pass after).** A second `create_algorithm` with the same slug and version answers 409. A
   `bulk_operation` with invalid parameters answers 422. Neither adds an event of its action.
7. *(Delta of 2026-10-05, D4: unconditional, split into 7a and 7b.)* **Sub-graph, under DP-5 (a) only; red first.** `create_version` on a sub-graph leaves a
   `sub_graph.created` event whose `before` is version 1's content and whose `after` is
   version 2's content, including `steps`. Version 1's event keeps `before is None`, and its
   `after` now includes `steps`. The existing assertions at
   `backend/tests/test_sub_graphs_service.py:71-73` pass **unedited**. Under DP-5 (b) this
   item is void, and the ledger says why.
8. **The chain verifies.** After items 1–5 have run in one workspace,
   `audit.verify_chain(session, workspace_id)` returns the number of events written, and it
   raises nothing (FR-372).
9. *(Delta of 2026-10-05, D4, D5: the full gate at Task 1's commit.)* **No behaviour change from the signature move (Task 1).**
   `uv run pytest backend/tests/test_rate_tables_service.py backend/tests/test_diff_cache.py backend/tests/test_worker_rate_tables.py backend/tests/test_api_rate_tables.py backend/tests/test_rating_algorithms.py backend/tests/test_rating_versions.py backend/tests/test_regression_suites.py backend/tests/test_sub_graphs_service.py backend/tests/test_sub_graphs_api.py -q`
   passes at the end of Task 1 and again at the end of Task 3. The only edits to those files
   are the call-site argument (`principal.id` → `principal`, or the local equivalent).
   `uv run mypy` is clean. Under `--strict`, a route still passing a bare UUID fails it, so
   mypy proves the route wiring.
10. **Write set.** `git diff --stat origin/main...HEAD` names only the paths in §"Write set".
11. **The gate.** The full two-half gate (`CLAUDE.md` §11) passes on the merge tree through the
    gate-runner, and `python3 scripts/audit-docs.py` exits 0 after the mint.
12. **The bound.** The merge commit's date is on or before 2026-11-04.
13. *(Delta 2 of 2026-10-05, E4.)* **No route response moves.** Task 1b Step 3's six `cmp` exit codes are all 0 at the slice's base and at Task 1b's commit, and the positive control's `cmp` is non-zero. Any other non-zero `cmp` is a STOP to the maintainer (by delegation).

## Global Constraints

- **`06` R2: the event shares the write's transaction** (`audit.py:3-5`, `:71-76`). Call
  `audit.record` inside the existing `async with database.unit_of_work()` block. Never open a
  second one, and never wrap the call in `try/except`.
- **A refused write records nothing.** Record after the write's last `flush()`, so that a 409
  raised at that flush never reaches the event.
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2). The rate table
  state is the existing `RateTableVersion` wire model's dump. No new class is added.
- **Money is never float** (`CLAUDE.md` §7). Dump with `mode="json"`, so that a `Decimal`
  relativity becomes a string, never a float.
- **Shared files** (`RL-1263`, amended by `RL-1445`): two concurrent build slices may not both
  change the same existing function, class, spec section or policy table.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): items 1, 2, 3, 4, 5
  and 7 are seen red first.
- **No spec text is drafted here.** Any `03` text is T-1, owed by an `RL-` (DP-4).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | NFR-498 | The "rate table versions", "bulk operations" and "algorithm edits" limbs: an event with before and after state | `req("NFR-498")` on items 1–8 |
| `06` | FR-368 | A governed state change emits an Audit Event in the same transaction | `req("FR-368")` on items 1–3, 5 |

NFR-498's other limbs are out of scope, named so that no reader assumes them: compilations
(delivered, `worker/rating_handlers.py:96`), approvals (delivered, `platform/approvals.py`),
deployments (delivered, `platform/deployments.py:537-553`), and rollbacks and routing changes
(WK-674 Slices 5 and 6, `SL-1259` and `SL-1260`, `draft`). Peril structures are not in the
read-first list, and `platform/perils.py` already calls `audit.record`.

### Task 0 at planning time (read, not run)

Read at `5fe56b87` with `sed -n`/`awk` and `git grep`. No test was run.

| # | Fact | Locator |
|---|---|---|
| 0.1 | `record(session, *, workspace_id, actor: Principal, source: JobSource, action, entity_ref, before, after, justification, job_id)`. It refuses a call with no open transaction, takes a per-workspace advisory lock, and flushes; it never commits | `backend/src/app/platform/audit.py:52-64`, `:71-76`, `:81-85`, `:142` |
| 0.2 | `seed_from_model(database, workspace_id, created_by: UUID, settings, blob_store, *, slug, model_ref, factor, change_note, rateable)`. Unit of work at `:122`. A new table is created at `:156-165`. A re-seed takes `version_number = table_row.current_version + 1` (`:168`). Persist at `:183-191` | `backend/src/app/platform/rate_tables.py:96-191` |
| 0.3 | `import_confirmed(..., created_by: UUID, ..., slug, version, filename, content)`. The baseline wire `table` comes from `_to_version` (`:442`). Persist at `:462-470` with `version + 1` | `rate_tables.py:419-470` |
| 0.4 | `_persist_new_version(session, *, table_row, derived, version_number, created_by, threshold, blob_store)`. It adds `RateTableVersionRow` (`:699`, `:723`); its flush at `:725` raises a 409 on `IntegrityError` (`:726-732`); it sets `current_version` (`:733`), writes the cells or the blob (`:735-748`), flushes (`:749`), and returns the wire form (`:750-764`) | `rate_tables.py:670-764` |
| 0.5 | `bulk_operation(..., created_by: UUID, ..., slug, version, kind, parameters)`. `baseline_row` (`:826`), wire `baseline` (`:827`), `derived` (`:829`). Persist at `:841-849` with `baseline_row.version_number + 1` | `rate_tables.py:796-849` |
| 0.6 | `_load_version(session, rate_table_id, version_number, slug) -> RateTableVersionRow` | `rate_tables.py:528-547` |
| 0.7 | No `audit` reference in `api/rate_tables.py`, `platform/rate_tables.py`, `worker/rate_table_handlers.py`, `api/rating_algorithms.py` or `platform/rating_algorithms.py` | `grep -n audit` over the five files: no output |
| 0.8 | `create_algorithm(database, workspace_id, created_by: UUID, content) -> RatingAlgorithmRow`. Parse and validate outside the unit of work (`:105-106`); unit of work at `:108`; same-version 409 at `:109-122`; row at `:123-129`; `add` and `flush` at `:130-131`; `return row` at `:132` | `backend/src/app/platform/rating_algorithms.py:94-132` |
| 0.9 | The routes pass `caller.principal.id`: seed `:97-101`, bulk `:135-148`, import `:252-256` | `backend/src/app/api/rate_tables.py` (decorators `:70`, `:112`, `:205`) |
| 0.10 | The algorithm route passes `caller.principal.id` (`:46-49`) | `backend/src/app/api/rating_algorithms.py:28-50` |
| 0.11 | The sub-graph routes: `create_sub_graph` (`:45`) and `create_sub_graph_version` (`:60`) call `service.create_sub_graph` and `service.create_version` with `caller.principal` | `backend/src/app/api/sub_graphs.py:45-73` |
| 0.12 | The sub-graph writer `_write` records `sub_graph.created` with `entity_ref` `sub_graph:<slug>@<version>`, **no `before`**, and an `after` of `change_note`, `inputs` and `outputs` only (no `steps`) | `backend/src/app/platform/sub_graphs.py:59-101`, the call at `:88-100` |
| 0.13 | `create_sub_graph` writes version 1 (`:104-124`). `create_version` writes `latest + 1` (`:127-143`) and reads only the number (`:137`). `_row(session, workspace_id, slug, version)` loads one version (`:150-162`) | `platform/sub_graphs.py` |
| 0.14 | The precedent shapes: `deployment.created` has `before` the previous Deployment or `None` and `after` the wire model, `mode="json"`; `rating_version.created` has `before={}` | `platform/deployments.py:537-553`; `platform/rating_versions.py:265-274` |
| 0.15 | Entity refs in the spec: `rate_table:<slug>@<n>` (`03:270`), `rating_algorithm:<slug>@<n>` (`03:376`) | `docs/specs/03-rating-engine.md` |
| 0.16 | `audit_events.workspace_id` has no foreign key, so a bare test or bench workspace id is accepted | `backend/src/app/db/models.py`, `class AuditEventRow` |
| 0.17 | The fixtures `database`, `workspace_id`, `principal` (a `USER` with an id) and `blob_store` exist | `backend/tests/conftest_db.py:172`, `:324`, `:330`, `:204` |
| 0.18 | The tests that read `audit_events` and also drive these writes filter by `action`, so the new events do not move their counts | `test_rating_version_compile.py:642-658`, `test_rating_versions.py:579-583`, `test_regression_suites.py:180-183`, `test_sub_graphs_service.py:39-50` |

**The call sites that Task 1 moves** (`git grep -n 'seed_from_model(\|import_confirmed(\|bulk_operation(\|create_algorithm('`
over `backend`, `examples` and `scripts`, at `5fe56b87`, excluding the `pricing_core` pure
functions and the `def` lines):
`backend/src/app/api/rate_tables.py:98`, `:145`, `:253`; `backend/src/app/api/rating_algorithms.py:47`;
`backend/tests/test_diff_cache.py:153`; `backend/tests/test_rate_tables_service.py:85`, `:130`,
`:182`, `:241`, `:253`, `:355`, `:379`, `:403`, `:435`, `:488`, `:522`, `:534`, `:583`, `:599`;
`backend/tests/test_worker_rate_tables.py:55`; `backend/tests/test_rating_versions.py:715`,
`:718`, `:1310`; `backend/tests/test_regression_suites.py:341`, `:375`;
`examples/fremtpl2/model.py:386`; `scripts/bench-compiled-for.py:100`;
`scripts/bench-score-batch.py:100`. Task 1 Step 1 re-runs the grep at the dispatch tree, and
the re-run's output, not this list, is the set to move.

### The read-first list, ruled in or out against NFR-498 (DP-5 carries the decision)

NFR-498 says "algorithm edits … emit Audit Events **with before/after state**". The
maintainer's item 2 calls the sub-graph create and version paths "algorithm edits too".

| Path | Today | Planner's reading | Reason |
|---|---|---|---|
| `api/sub_graphs.py` `create_sub_graph` (`:45`) → `platform/sub_graphs.py` `create_sub_graph` (`:104`) → `_write` (`:59`) | Event `sub_graph.created`, `before` absent, `after` = ports and change note (`:88-100`) | **IN, `after` limb only** | `before` absent is right for version 1, because nothing existed (the `deployment.created` precedent, 0.14). The `after` omits `steps`, and the steps are the graph. An "after state" without the graph is a summary, not the state. |
| `api/sub_graphs.py` `create_sub_graph_version` (`:60`) → `create_version` (`:127`) → `_write` | Same event, `before` absent | **IN, both limbs** | Version N replaces version N−1, so a prior state exists, and NFR-498 requires it. The event has no `before`. |
| `platform/sub_graphs.py` `get_version`, `list_versions`, `resolve_ref` (`:165`, `:173`, `:202`) | reads | **OUT** | They write nothing. NFR-498 covers state changes only. |
| `platform/audit.py` | the writer | **OUT** (read only) | The writer is correct as it is (0.1). Every fix is at a call site. |

Under DP-5 (b), both sub-graph rows become OUT on the reading "the event exists, and a
ports summary is its state". The ruling records that reading, so that the decision is not
silent.

### Write set, and its contention (`RL-1263`, `RL-1445`)

| Path | Change |
|---|---|
| `backend/src/app/platform/rate_tables.py` | edited: `seed_from_model` (`:96`), `import_confirmed` (`:419`), `bulk_operation` (`:796`) (`created_by: UUID` → `actor: Principal`; each passes `actor`, `action` and `before`), `_persist_new_version` (`:670`) (`actor`, `action`, `before`; the `audit.record`); added: `_audit_state`; the import block (`audit`, `JobSource`, `Principal`) |
| `backend/src/app/api/rate_tables.py` | edited: the three call sites (`:97-101`, `:135-148`, `:252-256`) pass `caller.principal` |
| `backend/src/app/platform/rating_algorithms.py` | edited: `create_algorithm` (`:94`) (`actor: Principal`; the previous-version read; the `audit.record`); the import block |
| `backend/src/app/api/rating_algorithms.py` | edited: `create_rating_algorithm` (`:46-49`) passes `caller.principal` |
| `backend/src/app/platform/sub_graphs.py` | *(DP-5 (a) only)* edited: `_write` (`:59`) gains `before`, and `after` becomes the stored content; `create_version` (`:127`) passes the previous version's content |
| `backend/tests/test_nfr498_audit_events.py` | added (new module): items 1–8 |
| `backend/tests/test_rate_tables_service.py`, `test_diff_cache.py`, `test_worker_rate_tables.py`, `test_rating_versions.py`, `test_regression_suites.py` | edited: the call-site argument only (Task 1) |
| `examples/fremtpl2/model.py` | edited: `author_demo_rating_evidence` (`:386-388`), the call-site argument only |
| `scripts/bench-compiled-for.py`, `scripts/bench-score-batch.py` | edited: the setup's `create_algorithm` call (`:100`) passes a `Principal` built from the existing `created_by` (`:98`) |
| `docs/specs/03-rating-engine.md` | only if DP-4 is ruled (a): T-1, byte for byte from the `RL-` |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated |

**Not written:** `backend/src/app/platform/audit.py`, `packages/` (no shape and no pure
function changes), `frontend/`, any migration, `docs/contracts/` (no route signature or body
changes; the generated OpenAPI is unchanged, and the gate's `--check` proves it).

**Contention.** The classes are those in `docs/process/delivery-process.core.json`'s
`guards.parallelism.build_slices_across_works.no_shared_files`. **Snapshot:** the open PRs at
`5fe56b87`, read 2026-10-05 between 17:40 and 17:58 BST. Each plan's write set was read from
its branch at the head named. The sweep took every open PR whose added lines name
`platform/rate_tables.py`, `api/rate_tables.py`, `rating_algorithms.py`, `platform/audit.py`
or `sub_graphs.py`, and then every open PR naming a Task 1 call-site file. Each hit was read
as a write or a citation. The two sweeps found 26 PRs and 12 PRs; only the rows below write a
shared path. `platform/audit.py` is written by **no** open plan.

| Other slice (Work; source read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **A-2**, PL-1464 (#1178 @`176a6a75`; WK-1178) | `platform/rating_algorithms.py` `create_algorithm` (`:94`) | adds the `feature_map` check after `_issues_to_error` (item 13) | the `actor` parameter, the previous-version read, the event | **same function → SERIAL**, named both ways (item 2). Recommended order: A-2 first (activation need 5) |
| A-2 (same) | `platform/sub_graphs.py` `create_sub_graph` (`:104`), `create_version` (`:127`) | each calls item 13's check before `_write` | *(DP-5 (a))* `_write` (`:59`) and `create_version` | `create_version` is the **same function → SERIAL** (it is inside the A-2 order above) |
| A-2 (same) | `backend/tests/test_rating_algorithms.py`, `test_sub_graphs_api.py` | appended | read only (`valid_algorithm`, `:64`) | none |
| **S7**, `SL-1391` / `PL-1419` (`active`, lane A; WK-673; plan on `main`, branch `sl-1391-fr-231-exposure-weights-portfolio-frame` @`36495cfc`, whose backend commits are not yet pushed) | `platform/rate_tables.py` | edits `diff` (`:291-349`) and `diff_needs_job` (`:262-288`); adds `check_portfolio` and the `load_*` helpers | edits `seed_from_model`, `import_confirmed`, `bulk_operation` and `_persist_new_version`; adds `_audit_state` | different functions, shared path → **allowed, named in the dispatch record**; the second merge re-runs the full gate |
| S7 (same) | `api/rate_tables.py` | edits `rate_table_diff` (`:278-321`) | the three write handlers' calls | different functions → **allowed, named** |
| S7 (same) | `backend/tests/test_diff_cache.py` | moves "the tests that call `DiffCache.key`" to the new signature | one argument at `:153`, in `test_diff_is_computed_on_miss_and_served_from_the_cache_on_hit` (`:129`) | **possibly the same test function**, if S7 also edits that test → **SERIAL on that test**; the second merge re-applies one argument |
| S7 (same) | `backend/tests/test_worker_rate_tables.py` | edited only where a `service.diff` call changes | one argument at `:55`, in `_seed_parquet_diff` (`:37`) | different functions → **allowed, named** |
| **WK-675 S4**, PL 9582 (#1187 @`800d3a70`) | `platform/rate_tables.py`, `api/rate_tables.py` | retypes `_wire_rows` (`:238`); adds `cells_page` and three handlers | the functions above | different functions → **allowed, named**. `_audit_state` drops `rows`, so `_wire_rows`' new type does not reach the event |
| **WK-675 S3**, PL 9578 (#1186 @`c5d1d03a`) | `platform/rating_algorithms.py`, `api/rating_algorithms.py` | adds `validate_draft` and a route; edits `diff_between` (`:157-163`) and `algorithm_diff` (`:53-69`) | `create_algorithm`; `create_rating_algorithm` | different functions → **allowed, named** |
| **WK-675 S2**, PL-1476 (#1131 @`c66300e5`) | `api/rating_algorithms.py` `create_rating_algorithm` (`:28-50`) | types the body and the response | the call's actor argument (`:46-49`) | **same function → SERIAL**; the second merge re-applies one argument |
| WK-675 S2 (same); **WK-673 S5**, PL-1500 (#1181 @`f1ad7738`) | `backend/tests/test_rating_versions.py` | new tests; S5 edits the shared fixture | one argument at `:715`, `:718` and `:1310` | **shared path**; same function only if a fixture they edit contains those lines → the dispatch re-reads them, and the second merge re-applies |
| **Exit-demo slice (a)**, PL 9624 (#1161 @`6714cc79`; WK-1178) and the **FD-1421 fix**, PL-1429 (#1140 @`f18549bb`; WK-1178) | `examples/fremtpl2/model.py` `author_demo_rating_evidence` (`:366-`) | both edit it; PL-1429 moves the algorithm save into a new `save_demo_algorithm` | one argument at `:387` | **same function → SERIAL**. Whichever of the three merges last passes the `Principal` to `create_algorithm` wherever the call then lives |
| **The FD-1425 fix**, PL-1435 (#1193 @`504db2f7`; WK-673) | `scripts/bench-compiled-for.py`, `scripts/bench-score-batch.py` | edit `_algorithm_payload()` (`:73`, `:71`) | the setup's call at `:100` | different functions → **allowed, named** |
| **The money_minor fix**, PL 9521 (#1202 @`15698eae`; WK-1178) | `backend/tests/test_sub_graphs_api.py`; `platform/sub_graphs.py` | appends item 4; reads `_check` (`:40-42`) | neither is written by us | none |
| **The emergency slice**, PL-1426 / SL-1427 (#1196 @`68b2f860`; WK-1178) | none (it edits `score.py` and score tests) | — | — | no shared write. This slice runs after it (item 2) |

Every other open plan names none of this write set. The dispatch record re-runs both sweeps
at its own tree, because the snapshot ages.

### Size

Small. There are four service edits, four route call-site edits and one new test module of
about 250 lines. About 25 call-site arguments move. DP-5 (a) adds two functions in one file.
The executor and one reviewer can handle it, and no spike is needed.

## Decision points

*(Delta of 2026-10-05, D1: every DP below is ruled; the table is kept as the record of the options.)* Each DP is the decision-maker's to rule (`delivery-process.md` §3). The planner recommends.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| **DP-1** | Where is the rate-table event written? | (a) In `_persist_new_version`, the one writer. Each caller passes `actor`, `action` and `before`, which is the baseline wire form it already holds. (b) In each of the three callers, after `_persist_new_version` returns. | **(a).** There is one writer for one event, and a fourth caller cannot forget it. `sub_graphs._write` (0.12) is the same pattern. Under (b), three call sites repeat the same nine lines. |
| **DP-2** | What do `before` and `after` carry? | (a) Rate tables: the `RateTableVersion` wire form with `mode="json"`, without `rows`. It keeps `keys`, `value`, `default_row`, `storage`, the blob ref `cells`, `change_note`, `seeded_from`, `created_by_operation` and `created_by_import`. Algorithms and sub-graphs: the stored `content`. (b) As (a), plus a `cells_sha256` over the canonical cells for a rows-mode version. (c) Everything inline, cells included. | **(a).** It follows the `deployment.created` precedent (the full wire model, 0.14), with one exception: the cell values. A version is immutable and is addressed by the event's `entity_ref`, so the cells are recoverable. Inlining up to the threshold's worth of rows into every event (c) bloats the hashed chain. Take (b) only if the DM wants the chain itself to attest the cell values. |
| **DP-3** | What are the action names? | (a) `rate_table_version.seeded`, `rate_table_version.imported`, `rate_table_version.bulk_operation`, `rating_algorithm.created`. (b) One action `rate_table_version.created`, with the origin read from `after`. | **(a).** NFR-498 names "bulk operations" as a class of its own, and (a) makes each class one `action =` query. Under (b) the seed is told apart only by the absence of `created_by_operation` and `created_by_import`. The `<entity>.<verb>` form matches `rating_version.created` and `sub_graph.created`. |
| **DP-4** | Is a spec text owed? | (a) Yes. **T-1** is a dated note in `03`. §4.2 (rate tables) and §4.1 (algorithms) name the actions, the `entity_ref` form and what `before` and `after` carry. Under DP-5 (a), the sub-graph sentence (`03:846`) gains the before and after clause. An `RL-` carries the text, and Task 5 applies it. (b) No. NFR-498's text already requires the event, and the names stay in code. | **(a).** The spec names every other audit action a client can read: `sub_graph.created` (`03:846`) and §4.12's catalogue (`03:874`, "each named here once so that no later slice appends to the catalogue"). An action that exists only in code is behaviour a client observes with no spec behind it (`CLAUDE.md` §0). NFR-498's own text needs **no** change. RL-1514 says the fix "is not ruled here", so T-1 belongs to the DP ruling (activation need 3), not to RL-1514. |
| **DP-5** | Are the sub-graph create and version paths in? (item 2) | (a) **IN.** `_write`'s `after` becomes the stored content (with `steps`), and `create_version` passes version N−1's content as `before`. Version 1 keeps `before = None`. (b) **OUT.** The event exists, and its ports summary is taken as its state. (c) Only the version path is IN. | **(a)**, for the reasons in §"The read-first list". The edit is about eight lines in one file, it keeps `test_sub_graphs_service.py:71-73` passing unedited, and it sits inside the A-2 serialisation that the slice already has. |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm every activation need. Quote the minted ids of FD-1513 and RL-1514,
  the DP ruling's id, the merge commits of SL-1427 and of A-2 (or the lead's reverse order),
  and the GO line. A missing need is a STOP to the lead.
- [ ] **Step 2:** Re-read §"Task 0 at planning time" at the dispatch tree. Where a line moved,
  record the new line in the ledger. Where a fact changed (for example, A-2 moved the
  `create_algorithm` body), STOP and report it before writing a red.
- [ ] **Step 3:** Before any test run: `pgrep -af 'pytest|vitest|flock'` and
  `flock -n /tmp/slots/gate-1 true; flock -n /tmp/slots/gate-2 true`. Run nothing heavy beside
  a held slot.

### Task 1: The actor moves into the four services (items 9, 10), no behaviour change

**Files:** the write set's `platform/rate_tables.py`, `api/rate_tables.py`,
`platform/rating_algorithms.py`, `api/rating_algorithms.py`, and the call-site files.

**Produces:** `seed_from_model(database, workspace_id, actor: Principal, settings, blob_store, *, …)`,
`import_confirmed(database, workspace_id, actor: Principal, settings, blob_store, *, …)`,
`bulk_operation(database, workspace_id, actor: Principal, settings, blob_store, *, …)`,
`create_algorithm(database, workspace_id, actor: Principal, content)`. The parameter keeps
its position, so each call site changes one argument.

- [ ] **Step 1:** Re-run the call-site grep (§"Task 0 at planning time") and record its output.
- [ ] **Step 2:** In each of the four services, rename `created_by: UUID` to
  `actor: Principal` (`from model_schema import Principal`). Add `assert actor.id is not None`
  as the first statement (the `sub_graphs._write` idiom, `:69`). Pass `created_by=actor.id`
  to the row. In `rate_tables.py`, `_persist_new_version` keeps `created_by: UUID` in Task 1,
  and the callers pass `actor.id`.
- [ ] **Step 3:** At the routes, replace `caller.principal.id` with `caller.principal` at
  `api/rate_tables.py:101`, `:148`, `:256` and `api/rating_algorithms.py:48`. Keep each
  `assert caller.principal.id is not None`.
- [ ] **Step 4:** At each test, example and bench call site, pass the `Principal` in place
  of its id: `principal`, `gate.analyst`, `analyst`. In the benches, use
  `Principal(kind=ActorKind.USER, id=created_by, display="bench")`, built from the existing
  `created_by = new_uuid7()` (`:98`), which stays for the rating version row at `:105`.
- [ ] *(Delta of 2026-10-05, D5: Step 5b, the full gate, follows.)* **Step 5:** `uv run mypy && uv run ruff check .`, then item 9's pytest command. All pass,
  with no assertion edited.
- [ ] **Step 6:** Commit: `refactor(rating): the rate-table and algorithm services take the acting Principal (NFR-498 prep)`.

*(Delta 2 of 2026-10-05, E3: Task 1b, the stored-wire-form return and the base-vs-head response comparison, follows here as its own commit, before Task 2.)*

### Task 2: The reds (items 1–5, 7, 8; item 6 as a control)

**Files:** create `backend/tests/test_nfr498_audit_events.py`.

**Consumes:** Task 1's signatures. Helpers: `_seed_approved_model` and `_set_threshold`
(`backend/tests/test_rate_tables_service.py`), `_LEVELS` and `_table_slug`
(`backend/tests/test_api_rate_tables.py`), `valid_algorithm`
(`backend/tests/test_rating_algorithms.py:64`). Importing a helper from a sibling test
module is the existing convention (`test_rate_tables_service.py:20-26`).

- [ ] **Step 1: Write the module.**

```python
"""NFR-498: rate table versions, bulk operations and algorithm edits emit Audit Events with
before/after state, in the write's transaction (06 R2, FR-368). FD-1513's fix, red first."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_rate_tables import _table_slug
from backend.tests.test_rate_tables_service import _LEVELS, _seed_approved_model, _set_threshold
from backend.tests.test_rating_algorithms import valid_algorithm
from sqlalchemy import select

from app.config import Settings
from app.db.models import AuditEventRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit
from app.platform import rate_tables as svc
from app.platform import rating_algorithms as algorithms
from app.platform.blobs import BlobStore
from model_schema import ArtifactRef, Principal
from model_schema.rating import RateTableVersion

pytestmark = pytest.mark.req("NFR-498")


def _state(version: RateTableVersion) -> dict[str, Any]:
    return version.model_dump(mode="json", exclude={"rows"})


async def _events(database: Database, workspace_id: UUID, action: str) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.scalars(
                    select(AuditEventRow)
                    .where(AuditEventRow.workspace_id == workspace_id, AuditEventRow.action == action)
                    .order_by(AuditEventRow.sequence)
                )
            ).all()
        )


async def _seed(database, workspace_id, principal, blob_store, slug, family) -> RateTableVersion:
    return await svc.seed_from_model(
        database, workspace_id, principal, Settings(), blob_store,
        slug=slug, model_ref=ArtifactRef(type="model", slug=family, version=1),
        factor="driver_age_band", change_note="NFR-498 red",
    )


@pytest.mark.req("FR-368")
async def test_a_seed_records_its_version_with_before_and_after(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    family, slug = f"mf-{uuid4().hex[:8]}", _table_slug()
    await _seed_approved_model(database, workspace_id, family, _LEVELS)
    first = await _seed(database, workspace_id, principal, blob_store, slug, family)
    second = await _seed(database, workspace_id, principal, blob_store, slug, family)

    events = await _events(database, workspace_id, "rate_table_version.seeded")
    assert [e.entity_ref for e in events] == [f"rate_table:{slug}@1", f"rate_table:{slug}@2"]
    assert events[0].before is None
    assert events[0].after == _state(first)
    assert events[0].actor["id"] == str(principal.id)
    assert events[1].before == _state(first)
    assert events[1].after == _state(second)
```

  Write the rest of the module on the same pattern, one test per item:
  - `test_an_import_records_the_baseline_as_before` (item 2). It uses the CSV body of
    `test_rate_tables_service.py:428-433` and calls `svc.import_confirmed(..., slug=slug, version=1, filename="nfr498.csv", content=content)`.
    It asserts the single `rate_table_version.imported` event's `entity_ref`, that
    `before == _state(first)`, that `after == _state(<returned>)`, and that
    `after["created_by_import"] is not None`.
  - `test_a_bulk_operation_records_the_baseline_and_the_derived_version` (item 3).
    `kind="uplift_table"`, `parameters={"percentage": "0.10"}`. The same assertions, with
    `created_by_operation`.
  - `test_a_parquet_version_records_its_blob_ref_and_no_rows` (item 4).
    `await _set_threshold(database, workspace_id, 1)` comes first. The test asserts
    `after["storage"] == "parquet"`, `after["cells"] is not None` and `"rows" not in after`.
  - `test_an_algorithm_save_records_the_previous_version_as_before` (item 5). It saves
    `content = valid_algorithm()`, then `content | {"version": 2}`. It asserts two
    `rating_algorithm.created` events, `before is None` then `before == content`, and
    `after ==` each posted dict.
  - `test_a_refused_write_records_nothing` (item 6, control). A repeat `create_algorithm`
    raises `PlatformError` with `status_code == 409`. A `bulk_operation` with
    `parameters={"percentage": "x"}` raises `PlatformError` with `status_code == 422`
    (`rate_tables.py:830-838`). The event counts do not change.
  - `test_a_sub_graph_version_records_the_previous_content_as_before` (item 7, DP-5 (a) only).
    It uses `test_sub_graphs_service.py`'s `content()` helper (`:24`) for version 1 and
    `content(change_note="second")` without `slug` for version 2. It asserts the two events'
    `before` (`None`, then version 1's stored content) and `after` (each version's stored
    content, with `"steps"` present).
  - `test_the_chain_verifies_after_every_class` (item 8). It runs one write of each class in
    one workspace, then `async with database.unit_of_work() as session:
    assert await audit.verify_chain(session, workspace_id) == <events written>`.

- [ ] **Step 2: Run the module and see each red fail for its cause.**
  Run: `uv run pytest backend/tests/test_nfr498_audit_events.py -q`
  Expected: the tests for items 1, 2, 3, 4, 5 and 7 FAIL with an empty event list (for
  example `assert [] == ['rate_table:…@1', …]`, or an `IndexError` on `events[0]`). Item 6
  PASSES. Item 8 FAILS on the count. A `TypeError` or an import error is a plan defect:
  STOP. Record each failure line in the ledger.
- [ ] **Step 3:** Commit: `test(rating): NFR-498 reds — rate table, bulk and algorithm writes record no Audit Event (FD-1513)`.

### Task 3: The events (items 1–8)

**Files:** `backend/src/app/platform/rate_tables.py`,
`backend/src/app/platform/rating_algorithms.py`, and `backend/src/app/platform/sub_graphs.py`
under DP-5 (a).

- [ ] *(Delta of 2026-10-05, D3, D5: the `before` source and `_audit_state` below are replaced by D3's code.)* **Step 1: Rate tables (DP-1 (a), DP-2 (a), DP-3 (a)).** In `rate_tables.py`:

```python
from app.platform import audit
from model_schema import JobSource, Principal


def _audit_state(version: RateTableVersion) -> dict[str, Any]:
    """NFR-498's state of one version: its wire form without inline cells (DP-2 (a)).

    A version is immutable and the event's `entity_ref` addresses it, so the cell values
    stay recoverable; a blob-stored version keeps its content-addressed `cells` ref here.
    """
    return version.model_dump(mode="json", exclude={"rows"})
```

  `_persist_new_version` replaces `created_by: UUID` with `actor: Principal, action: str,
  before: RateTableVersion | None`, passes `created_by=actor.id` to the row (`:711`), binds
  the existing return value (`:750-764`) to `created`, and before `return created` adds:

```python
    await audit.record(
        session,
        workspace_id=table_row.workspace_id,
        actor=actor,
        source=JobSource.API,
        action=action,
        entity_ref=f"rate_table:{derived.slug}@{version_number}",
        before=None if before is None else _audit_state(before),
        after=_audit_state(created),
    )
```

  The callers:
  - `seed_from_model`: `before = None` when the table was just created (`:156-165`).
    Otherwise `before = await _to_version(session, await _load_version(session, table_row.id, table_row.current_version, slug), blob_store)`,
    read before `version_number` is computed. Pass `action="rate_table_version.seeded"`.
  - `import_confirmed`: `before=table` (`:442`), `action="rate_table_version.imported"`.
  - `bulk_operation`: `before=baseline` (`:827`), `action="rate_table_version.bulk_operation"`.

  The record sits after the flush at `:749`. A 409 at `:725` therefore never reaches it
  (item 6).
- [ ] **Step 2: Algorithms.** In `create_algorithm`, after the 409 check (`:109-122`):

```python
        previous = await session.scalar(
            select(RatingAlgorithmRow)
            .where(
                RatingAlgorithmRow.workspace_id == workspace_id,
                RatingAlgorithmRow.slug == algorithm.slug,
            )
            .order_by(RatingAlgorithmRow.version.desc())
            .limit(1)
        )
```

  After `await session.flush()` (`:131`):

```python
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=actor,
            source=JobSource.API,
            action="rating_algorithm.created",
            entity_ref=f"rating_algorithm:{algorithm.slug}@{algorithm.version}",
            before=None if previous is None else previous.content,
            after=content,
        )
```

  `before` is the highest-numbered existing version of the slug, because algorithm versions
  are numbered by the client (`:110-113`), not by the server.
- [ ] *(Delta of 2026-10-05, D5: unconditional.)* **Step 3: Sub-graphs (DP-5 (a) only).** `_write` gains
  `before: dict[str, Any] | None`, and its `audit.record` passes `before=before,
  after=row.content`. `create_sub_graph` passes `before=None`. In `create_version`,
  `previous = await _row(session, workspace_id, slug, latest)` follows the `latest is None`
  check, and the call passes `before=previous.content`.
- [ ] **Step 4:** `uv run pytest backend/tests/test_nfr498_audit_events.py -q`: every test
  passes. Then run item 9's command. Then `uv run mypy && uv run ruff check .`.
- [ ] **Step 5:** Commit: `fix(rating): rate table versions, bulk operations and algorithm saves emit NFR-498 Audit Events (FD-1513)`.

### Task 4: The P2 bound and the register (no code)

- [ ] **Step 1:** The ledger states the merge date against the bound (item 12). If the slice
  cannot merge by 2026-11-04, the executor reports to the lead before 2026-10-28, so the lead
  can re-sequence lane B before the freeze.

### Task 5: The spec text, only from an `RL-` (DP-4)

*(Delta 2 of 2026-10-05, E5: RL-1515 carries T-1a to T-1d; T-1d is at `03:343`.)*

*(Delta of 2026-10-05, D5: unconditional; the `RL-` is RL-1515.)*

- [ ] **Step 1:** If DP-4 is ruled (a), apply T-1 byte for byte from the ruling under
  `spec-change`, run `python3 scripts/audit-docs.py`, and commit
  `docs(specs): 03 — the NFR-498 audit actions for rate tables and algorithms (T-1)`. If DP-4
  is ruled (b), this task is empty, and the ledger says so.

### Task 6: The gate and the ledger (items 10, 11)

- [ ] **Step 1:** Run the full two-half gate through the gate-runner, holding one gate slot.
  Record each rc and the tree.
- [ ] **Step 2:** Write the `LG-` ledger. It holds Task 0's re-read lines, Task 1's call-site
  list as re-run, every red with its printed line, which of A-2 and this slice merged first,
  the S7 and WK-675 shared paths as found at merge, and `git diff --stat origin/main...HEAD`
  checked against §"Write set".

## Hand-off

1. The lead mints PL-1516 and SL-1517 after FD-1513 and RL-1514, and dispatches only after
   §"Activation needs" hold, in a separate activation PR.
2. When this slice merges, FD-1513's event is met: "a merged SL-1517 with the four classes
   recording an Audit Event, before the P2 code freeze". The auditor discharges the register
   row, and the P2 phase closure record lists the bound as met (item 1).
3. **To A-2's planner (#1178):** this plan names the serialisation on `create_algorithm`
   (`platform/rating_algorithms.py:94`) and, under DP-5 (a), on `create_version`
   (`platform/sub_graphs.py:127`). A-2's write set gains the reverse row at its next fold.
4. *(Delta of 2026-10-05, D6: the shared test is named; the second merger rebases it.)* **To S7's executor (`SL-1391`):** `platform/rate_tables.py`, `api/rate_tables.py`,
   `test_diff_cache.py` and `test_worker_rate_tables.py` are shared paths, and their
   functions differ, except possibly one test in `test_diff_cache.py`. Whichever slice
   merges second re-runs the full gate on the merged tree.
5. **To WK-675 S2's executor (PL-1476):** `create_rating_algorithm` is the same function. The
   second merge re-applies `caller.principal` at the service call.

## Self-review

1. **Coverage of the ruling's item 2, clause by clause.**
   - "red-first per class (seed_from_model, import_confirmed, bulk_operation, create_algorithm)":
     items 1, 2, 3 (with 4) and 5, each red first in Task 2.
   - "with before/after state asserted": every one of those items asserts both `before` and
     `after` by value, not by presence.
   - "Its read-first list also covers the sub-graph create and version paths (api/sub_graphs.py)
     … in or out with a reason, not silently": §"The read-first list" gives a reason for each
     path, and DP-5 carries the ruling.
   - "It runs after the emergency slice": activation need 4.
   - "serialises against A-2 on rating_algorithms.py, named both ways": activation need 5, the
     contention table's first two rows, and Hand-off 3.
2. **Item 1's bound:** the header line, item 12, Task 4 and the `SL-` row.
3. **RL-1514's four violations** match items 1, 2, 3 and 5 in their own words (`before` is the
   baseline; `baseline` as `before` and the derived version as `after`).
4. **Every open design choice has an owner:** DP-1 to DP-5 belong to the decision-maker.
   The planner drafts no spec text: T-1 is named, and its `RL-` carries it.
5. **Type consistency:** `actor: Principal` in all four services and in `_persist_new_version`;
   `_audit_state(RateTableVersion) -> dict[str, Any]` in Task 3 matches the test's `_state` in
   Task 2; the action strings agree between DP-3, the Acceptance Standard and Task 3.
6. **Repository literals read at `5fe56b87`:** every line in §"Task 0 at planning time" and in
   §"Write set". FD-1513 was read at `9bf47b1f`, RL-1514 at `df4f5a53`, and each other plan
   on its branch at the head named in the contention table.
7. **What was not executed.** No test, script or code was run. The code is a sketch against
   the names read at `5fe56b87`. Whether `RateTableVersion.model_dump(mode="json")` is
   byte-stable across a re-load (`_to_version`) is first proven by item 1's second assertion,
   which compares a re-loaded `before` with the earlier returned `after`. If they differ, that
   red fails for a reason other than "no event": STOP and report it, because DP-2's form
   would then need a canonical dump.
