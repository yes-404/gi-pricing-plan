---
id: RL-1515
family: ruling
title: NFR-498's Audit Events for rate table versions, rating algorithms and sub-graphs — one writer per class, distinct actions, the wire form with a cells hash as the state, and the sub-graph event's full before and after
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: decision-maker           # the decisions are the maintainer's (by delegation); this record files them with T-1's text
tree: fb178c360f6fd5b2fdb7ae60eea924811a65492f
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [NFR-498, FR-368, FR-230, FR-232, FR-233, FR-235, CR-1212, RL-1263, FD-1513, RL-1514, PL-1516, SL-1517]
---

# NFR-498's Audit Events for rate table versions, rating algorithms and sub-graphs

## How this was ruled

- **Filed under working id 9501 (minted as RL-1515), reserved by the lead.** In the texts
  below, the working ids are replaced by the minted ids outside quoted entries, and `RL-1515`
  is this record's own. Three other records this one names were minted in the same batch
  (B4, 2026-10-08): **PL-1516** (the leaf plan, draft #1207, branch
  `pl-9514-nfr498-audit-events`, read at `a2d2e050425f43feafc15fe6045cbda3b42f4f4c`), whose
  slice **SL-1517** applies this record; **FD-1513** (the finding, draft #1201, read at
  `9bf47b1fddca0670ca01431cf3d58cb974530716`); and **RL-1514** (`CR-1212`'s correction, draft
  #1203, read at `df4f5a534e6cd8bdb25b158c884ed60e1694206e`). Each joins `relates:` at
  the mint, with **FD-1513**'s and **SL-1517**'s.
- **The decisions are not this record's.** They are the maintainer's (by delegation), in the
  entry quoted verbatim below. This record files them as one `RL-`, as DP-4 orders, and drafts
  T-1, the one spec text DP-4 owes. Where T-1 needed a detail the entry does not name, the
  detail is taken from main or from PL-1516 and is listed under "Details taken from main or
  from the plan", so a reader can check that no new choice was made.
- **RL-1514 leaves the fix open.** Its "What it obliges" says of the fix slice's form: "It is
  not ruled here." It also does not decide the sub-graph question: "It does not decide whether
  the sub-graph create and version paths (`api/sub_graphs.py`) are algorithm edits under
  NFR-498." This record rules both, on the entry below.
- **Brief:** `brief-pl9514-rulings-2026-10-05.md`, Part A (the lead, 2026-10-05).

### The maintainer's entries, quoted verbatim

`~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed "2026-10-05 18:04:32 BST — PL
9514 (#1207 @a2d2e050) DPs 1–5 RULED; Task 1's Principal threading accepted":

> DP-1: the SINGLE WRITER (_persist_new_version, rate_tables.py :670). The caller passes the action and the baseline. One site cannot miss a caller.
> DP-2: the wire form WITHOUT rows, PLUS a cells content digest (your rec, the tamper-evident minimum). Use the EXISTING hash, no new hashing: rate_tables.py already imports version_content_hash from app.platform.diff_cache (:35, used at :340-341), and RateTableVersion carries cells: BlobRef (model_schema/rating.py:899ff). The digest is version_content_hash over the version's cells, or the BlobRef's own content address if that is the same value (the planner states which, with file:line). For algorithms and sub-graphs, the stored content.
> DP-3: the DISTINCT actions: rate_table_version.seeded, .imported and .bulk_operation, and rating_algorithm.created.
> DP-4: YES. T-1 is a dated 03 note naming the actions (precedents 03:846 and :874), carried by ONE RL that also records DP-1 to DP-5. NFR-498's text is unchanged. Reserve the id; a DM files it.
> DP-5: (a). create_sub_graph's after gains the full content (steps included), and create_version gains a before (N−1). A steps-less after is a summary, not the state NFR-498 names.
> Task 1, threading Principal through the four services with NO behaviour change (about 25 call-site args): ACCEPTED as a refactor commit BEFORE the reds, with the full suite green at that commit in the gate.
> CONTENTION: as tabled, with A-2 FIRST. The one shared test with S7 (test_diff_cache.py): whichever merges second rebases it, named in both. The bound of 4 Nov holds.
> planner-9529's cd into its own worktree: noted; stopping it is fine.

The same file, the entry headed "2026-10-05 17:45:06 BST — FD 9529 (NFR-498, #1201
@be1fba43): MEDIUM and carry-forward to WK-1178 accepted, with a P2 landing bound; CR-1212
correcting RL yes; A-2 does not absorb", which the 18:04:32 entry rules within:

> Spot-checked at origin/main: platform/rate_tables.py and platform/rating_algorithms.py contain 0 occurrences of audit or record(, and neither imports app.platform.audit (approvals, datasets, deployments, environments and others do). The finding is real.
> 1. Your decision is ACCEPTED: MEDIUM; carry forward, owner WK-1178; the 13 verdict is "deferred with an owner". ADDED BOUND: the fix lands BEFORE THE P2 CODE FREEZE (Wed 4 Nov). An unaudited rate-table or algorithm change is exactly what the exit demo's governance story claims cannot happen, so this is not a P3 carry. The register's Decision cell carries the bound; the P2 phase closure record lists it.
> 2. The fix slice: red-first per class (seed_from_model, import_confirmed, bulk_operation, create_algorithm), with before/after state asserted. Its read-first list also covers the sub-graph create and version paths (api/sub_graphs.py), since they are algorithm edits too: in or out with a reason, not silently. It runs after the emergency slice and serialises against A-2 on rating_algorithms.py, named both ways.
> 3. CR-1212: YES, a correcting RL (corrects: CR-1212; CR-1212 gains corrected_by:), filed by a DM when a seat frees, citing FD 9529.
> 4. A-2 does NOT absorb the audit event. Agreed.
> #1132 @19d0c51c: noted; the ACK at green.

The same file, the entry headed "2026-10-05 18:12:58 BST — PL 9514 @1cabc274: the
stored-wire-form constructor accepted as implementation, with one STOP; RL 9501 @1e6a59df:
03:343 IS amended (T-1d), not read around", item 2 (item 1 concerns the plan, and its first
line accepts the hash and the key `cells_digest`):

> 2. RL 9501, 03:343 ("the before/after cells and the actor belong to NFR-498's Audit Event, not here"): I do NOT read around it. Read literally, it places the CELLS in the event, while DP-2 carries a digest. So RL 9501 adds T-1d, a dated note at :343 saying the Audit Event carries the cells BY the immutable version's reference PLUS cells_digest (their canonical content hash), not inline, citing T-1b and DP-2. Its anchor counts 1, as for T-1a to T-1c. That keeps the spec saying what the code will do, with no silent reading.
>    T-1a, T-1b and T-1c: ACCEPTED as drafted.

Item 1's first line, also verbatim: "1. DP-2's hash = version_content_hash (diff_cache.py:46-56),
not BlobRef.sha256 (parquet bytes, absent for rows): ACCEPTED; key cells_digest."

## Verified first, at `fb178c36`

Every locator below was read at `origin/main` `fb178c36`, the `tree:` above, with `grep -n`
and `sed -n`. Nothing was run but reads and the `grep -cF` predicates named.

- **NFR-498** (`docs/specs/03-rating-engine.md:1339`), whole row: "Audit: algorithm edits,
  rate table versions, bulk operations, compilations, approvals, deployments, rollbacks, and
  routing changes all emit Audit Events with before/after state." No dated amendment.
  `grep -n "NFR-498" docs/specs/03-rating-engine.md` gives `:343` and `:1339` only.
- **`03:343`**, in §4.2's `created_by_import` note: "the before/after cells and the actor
  belong to NFR-498's Audit Event, not here". Read literally, it places the cells in the
  event; T-1d amends it (Ruled, item 6).
- **The precedents.** `03:846` (§4.11): "Every write records an Audit Event `sub_graph.created`
  with `entity_ref` `sub_graph:<slug>@<version>`, in the same transaction (`06` FR-368)."
  `03:874` (§4.12), "Audit actions this Work emits": each action is named once with its
  `before`, `after`, `entity_ref`, actor and transaction, for example `deployment.created`,
  "`before` the previous live Deployment of the Environment or `null`, `after` this one, in
  the same transaction as the row".
- **DP-1's writer.** `backend/src/app/platform/rate_tables.py:670`, `async def
  _persist_new_version`. Its callers: `seed_from_model` (`:96`), `import_confirmed` (`:419`)
  and `bulk_operation` (`:796`).
- **DP-2's hash.** `rate_tables.py:35` imports `version_content_hash` from
  `app.platform.diff_cache`, and `:340-341` call it on both versions' cells.
  `backend/src/app/platform/diff_cache.py:46-56`: `version_content_hash(cells)` is sha256 over
  the canonical JSON of the cells, "row order ignored", so "a rows-stored version and its
  parquet twin hash identically (FR-232's same-artifact guarantee)". The `BlobRef`
  (`packages/model-schema/src/model_schema/refs.py:189-197`) carries `sha256`, which
  `backend/src/app/platform/blobs.py:158` takes over the stored bytes; for a rate table those
  bytes are the parquet file (`rate_tables.py:744-746`). A rows-stored version has no
  `BlobRef`: `_persist_new_version` returns `cells=blob_ref` (`:759`), `None` unless the
  storage is parquet (`:734-748`). So the `BlobRef` address is not the same value as
  `version_content_hash` and does not exist for every version. **The hash is
  `version_content_hash`.** The 18:04:32 entry gives the planner the statement of which hash,
  with file:line; this record reads the same files, and T-1b depends on the answer, so the
  plan's fold must agree with it (see "What it obliges").
- **`RateTableVersion`** (`packages/model-schema/src/model_schema/rating.py:899`), the §4.2
  wire form: "the cells (`rows` for row storage, `cells` as a parquet BlobRef above the
  threshold)".
- **The algorithm writer.** `backend/src/app/platform/rating_algorithms.py:94`, `async def
  create_algorithm`. No `audit` reference in `platform/rate_tables.py` or
  `platform/rating_algorithms.py` (`grep -c audit` gives 0 on each).
- **The sub-graph writer.** `backend/src/app/platform/sub_graphs.py:59-101`, `_write`: the
  `audit.record` call passes `action="sub_graph.created"`, no `before`, and an `after` of
  `change_note`, `inputs` and `outputs` only. The stored content is
  `body.model_dump(mode="json")` (`:74`). `create_sub_graph` is `:104`, `create_version`
  `:127`.

### The decision points as put (PL-1516 §"Decision points", at `a2d2e050`)

| DP | Question | Options |
|---|---|---|
| DP-1 | Where is the rate-table event written? | (a) in `_persist_new_version`, each caller passing `actor`, `action` and `before`; (b) in each of the three callers |
| DP-2 | What do `before` and `after` carry? | (a) the wire form without `rows`, the stored `content` for algorithms and sub-graphs; (b) as (a), plus a hash over the cells; (c) everything inline |
| DP-3 | What are the action names? | (a) four distinct actions; (b) one `rate_table_version.created` |
| DP-4 | Is a spec text owed? | (a) yes, T-1, carried by an `RL-`; (b) no |
| DP-5 | Are the sub-graph create and version paths in? | (a) in, both limbs; (b) out; (c) the version path only |

## Ruled

1. **DP-1: (a), the single writer.** The rate-table event is written in
   `_persist_new_version` (`rate_tables.py:670`), after its last flush. Each caller passes the
   acting `Principal`, the action and the baseline it already holds as `before`. One site
   cannot miss a caller.
2. **DP-2: (b), with the existing hash.** A rate table version's state is its
   `RateTableVersion` wire form, dumped with `mode="json"`, without `rows`, plus the content
   hash of its cells computed by `version_content_hash` (`diff_cache.py:46`). No new hashing.
   An algorithm's state is its stored content, and a sub-graph version's state is its stored
   content.
3. **DP-3: (a), the distinct actions:** `rate_table_version.seeded`,
   `rate_table_version.imported`, `rate_table_version.bulk_operation` and
   `rating_algorithm.created`. The sub-graph action is unchanged: `sub_graph.created`
   (`03:846`). DP-5 changes its payload, not its name.
4. **DP-4: (a).** T-1 below is the dated `03` text naming the actions and their payloads,
   following `03:846` and `03:874`. NFR-498's text is unchanged. This one record carries T-1
   and DP-1 to DP-5.
5. **DP-5: (a).** Both sub-graph paths are in. Every `sub_graph.created` event's `after` is
   the version's stored content, steps included, and `create_version`'s event gains a
   `before`: the stored content of version N−1. Version 1's `before` stays absent. The
   reason is the entry's: "A steps-less after is a summary, not the state NFR-498 names."
6. **`03:343` is amended (T-1d), not read around** (the 18:12:58 entry, item 2). Read
   literally, its "the before/after cells and the actor belong to NFR-498's Audit Event"
   places the cells in the event, while DP-2 carries a digest. T-1d adds a dated note there:
   the event carries the cells by the immutable version's reference plus `cells_digest`, not
   inline, citing T-1b and DP-2. T-1a, T-1b and T-1c are accepted as drafted (same item).

**Also in the 18:04:32 entry, recorded here so that the plan's fold cites one record.** Task 1
(the `Principal` threaded through the four services, no behaviour change) is accepted as a
refactor commit before the reds, with the full suite green at that commit in the gate. The
contention is as PL-1516 tables it, with A-2 first; the one test shared with S7
(`backend/tests/test_diff_cache.py`) is rebased by whichever slice merges second, and both
plans name it. The bound of 4 November 2026 holds.

## Details taken from main or from the plan (no new choice)

| Detail | Taken from |
|---|---|
| `entity_ref` forms `rate_table:<slug>@<version>`, `rating_algorithm:<slug>@<version>`, `sub_graph:<slug>@<version>` | `03:270`, `:376` (the reference examples); `03:846` |
| `before` `null` (absent) for a first version | `03:874`'s `deployment.created` and `environment.created`; `sub_graphs.py:88-100` |
| The re-seed's `before` is the table's current version | PL-1516 Task 3 Step 1 (`seed_from_model`) |
| An import's and a bulk operation's `before` is the addressed baseline | PL-1516 Task 3 Step 1; RL-1514's Acceptance ("an event whose `before` is not the baseline version") |
| An algorithm's `before` is the slug's highest-numbered existing version | PL-1516 Task 3 Step 2: "algorithm versions are numbered by the client" |
| The event follows the write's last flush, so a refused write records none | PL-1516 §"Global Constraints"; `sub_graphs.py:79-100` |
| The same transaction as the write | `06` FR-368 and R2 (`backend/src/app/platform/audit.py:3-5`) |

## T-1 — the `03` texts

Four insertions in `docs/specs/03-rating-engine.md`, applied by SL-1517 (PL-1516 Task 5) byte
for byte, under `spec-change`, in one commit with the code (`CLAUDE.md` §2). The placeholders
are `RL-1515` (this record's minted id) and `<Slice date>` (the date of the SL-1517 commit
that applies them). Nothing else in a text is a placeholder. Nothing is struck. Each anchor
was counted at `fb178c36` with `grep -cF -- '<anchor>' docs/specs/03-rating-engine.md` over
the whole file, and each printed **1**. The same predicate with one byte of each anchor
changed (`4.2` → `4.9`, `4.3` → `4.8`, `FR-368` → `FR-369`, `here` → `hare`) printed **0**
each time. A trial apply of all four to a copy of `03` at `fb178c36` put each inserted text's
first line at count **1**.

**T-1a — §4.1, the algorithm event.** Placement: a new paragraph inserted immediately before
the heading line

```text
### 4.2 `RateTable` / `RateTableVersion`
```

(`03:291`), with one blank line before the heading and one after §4.1's "Invariants"
paragraph, which ends at `03:289` with "(FR-212).". Insert

```text
> **Audit Event (added <Slice date>, `RL-1515`, NFR-498, FD-1513).** Every saved Rating
> Algorithm version records one Audit Event `rating_algorithm.created`, in the same
> transaction as the version (`06` FR-368), after the version is written, so a refused save
> records none. Its `entity_ref` is `rating_algorithm:<slug>@<version>`, its actor is the
> saving Principal, its `after` is the stored content of the version saved, and its `before`
> is the stored content of the slug's highest-numbered existing version, or `null` when the
> slug has none.
```

**T-1b — §4.2, the rate table version events.** Placement: a new paragraph inserted
immediately before the heading line

```text
### 4.3 `RatingVersion`
```

(`03:369`), after the "Re-seeding an existing table" note, with one blank line on each side.
Insert

```text
> **Audit Events (added <Slice date>, `RL-1515`, NFR-498, FD-1513).** Every new Rate Table
> Version records one Audit Event, in the same transaction as the version (`06` FR-368),
> after the version is written, so a refused write records none. The action names how the
> version was made: `rate_table_version.seeded` (FR-230), `rate_table_version.imported`
> (FR-235) or `rate_table_version.bulk_operation` (FR-233). Its `entity_ref` is the new
> version's `rate_table:<slug>@<version>` and its actor is the Principal who made the write.
> Its `after` is the new version's wire form above without `rows`, plus the cells' canonical
> content hash under the key `cells_digest`: the hash over the cells that the diff is cached
> under, the same for a rows-stored version and its parquet twin (FR-232). Its `before` is, in the same form, the
> version the new one was made from: the addressed baseline of an import or a bulk
> operation, or the table's current version for a re-seed; it is `null` for a table's first
> version. The cell values are not copied into the event: the version is immutable,
> `entity_ref` addresses it, and the hash attests its cells.
```

**T-1c — §4.11, the sub-graph event's before and after.** Placement: the bullet at `03:846`.
The text is **appended** to the end of the line, after its last bytes

```text
in the same transaction (`06` FR-368).
```

and one space. Insert

```text
*(Amended <Slice date>, `RL-1515`, NFR-498: the event's `after` is the stored content of the version written, steps included, and its `before` is the stored content of version N−1, or absent for version 1.)*
```

**T-1d — §4.2, `03:343`, where the event carries the cells.** Placement: inside the
`created_by_import` note, line `03:343`. The text is **inserted** immediately after the bytes

```text
belong to NFR-498's Audit Event, not here.
```

and one space, before `This example's version`, on the same line. Insert

```text
*(Amended <Slice date>, `RL-1515`, DP-2 and T-1b: the Audit Event carries the cells by reference, not inline: by its `entity_ref`, which addresses this immutable version, plus `cells_digest`, the cells' canonical content hash. "Audit Events" at the end of this section says what `before` and `after` hold.)*
```

## What it obliges

- **This commit:** this record only. No spec, `model-schema` or code file is edited here.
- **SL-1517 (PL-1516)** applies DP-1 to DP-5 in code and T-1a to T-1d in `03`, in one commit
  with the code (`CLAUDE.md` §2). Its reds are PL-1516's Acceptance Standard items 1 to 8,
  with DP-2 now ruled (b): the `after` of a rate table version also carries the cells hash
  under `cells_digest`, and items 1 to 4 assert it. The key is PL-1516's proposal (#1207 at
  `1cabc274`, which says T-1's name wins); T-1b adopts it on the lead's instruction, so the
  plan and the spec text name one key.
- **PL-1516's fold (the planner's file, not edited here)** marks DP-1 to DP-5 ruled, states
  which hash with file:line, and replaces activation need 3 with this record's mint. If the
  planner's reading of the hash differs from the one above, that is a STOP to the lead before
  the plan is activated, because T-1b's sentence on the hash would then be wrong.
- **FD-1513** is discharged by SL-1517's merge, before the P2 code freeze (Wed 4 November
  2026). The verdict is the lead's.

## What this record does not decide

- **NFR-498's other limbs** (compilations, approvals, deployments, rollbacks, routing
  changes), **`CR-1212`'s correction** (RL-1514's) and **the order of merges** beyond what the
  18:04:32 entry states.
- **Task 1 and the contention** are recorded above, not ruled here: they are the entry's
  decisions on the plan's tasks, not decision points.

## Acceptance — the violation that must become detectable

The violation: **a rate table version written by seed, import or bulk operation, a Rating
Algorithm saved, or a Sub-graph version written, with no Audit Event under its ruled action,
or with an event whose `before` or `after` is not the ruled state.** At `fb178c36`, the first
four classes commit with no event, and the sub-graph event has no `before` and no `steps`.
Nothing fails today. Each check below is SL-1517's, shown red on the named input before the
code that turns it green (PL-1516 Task 2).

- *Violation: a seed, an import or a bulk operation commits a version and `audit_events`
  gains no row with its action.* PL-1516 items 1, 2 and 3. Red at `fb178c36`.
- *Violation: an import's or a bulk operation's event whose `before` is not the baseline
  version's state.* Items 2 and 3.
- *Violation: a rate table event whose `after` carries `rows`, or lacks `cells_digest`, or
  carries a hash that differs between a rows-stored version and its parquet twin.* Items 1
  to 4, with item 4 for the parquet case. A hash taken from the `BlobRef` reds the rows case
  (no `BlobRef`) and the twin comparison.
- *Violation: a saved algorithm with no `rating_algorithm.created` event, or one whose
  `before` is not the previous version's stored content.* Item 5.
- *Violation: a sub-graph version's event whose `after` lacks `steps`, or a version-2 event
  with no `before`.* Item 7. Red at `fb178c36` (`sub_graphs.py:88-100`).
- *Violation: a refused write that records an event.* Item 6, the control.
- *Violation: T-1 applied at a different place or with different bytes.* SL-1517's ledger
  records each anchor's `grep -cF` at its dispatch tree, then `grep -cF` for each inserted
  text's first line after the apply, each **1**.
