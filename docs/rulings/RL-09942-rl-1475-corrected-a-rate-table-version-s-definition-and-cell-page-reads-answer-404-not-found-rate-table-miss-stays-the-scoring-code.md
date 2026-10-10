---
id: RL-9942
family: ruling
title: RL-1475 corrected — a rate table version's definition and cell-page reads answer 404 NOT_FOUND for an unknown table or version; RATE_TABLE_MISS stays the scoring code
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10
owner: decision-maker
tree: 26f93be0727d7b028d9b73143d41b05b472e57b3
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1475
relates: [RL-1475, RL-1555, PL-1558]
---

# RL-9942 — RL-1475 corrected: the two rate table version reads answer 404 `NOT_FOUND`; `RATE_TABLE_MISS` stays the scoring code

## How this was ruled

- **Filed under working id 9942, reserved by the lead (team-lead) on 2026-10-10.** In the
  same commit, `RL-1475`'s header gains `corrected_by: [RL-9942]`, the append check 34
  allows (`docs/process/document-ids.md` §1, the `corrected_by:` / `corrects:` lines of the
  front-matter block). Not one byte of `RL-1475`'s body changes. When this record is
  minted, the working id in both headers and in this record is replaced by the minted id.
- **The decisions are not this record's.** They are the maintainer's (by delegation), in
  two entries of `~/gi-pricing-plan.local/channel/to-lead.md`, quoted below by header:
  - "2026-10-10 04:19:42 BST — RULING: rate-table 404 disagreement = (a), the SPEC governs
    (NOT_FOUND); the fix is at the route layer; one FD for the pre-existing drift"
    (`to-lead.md:20952`);
  - "2026-10-10 04:23:36 BST — RULING: WK-675 S4 read routes = (a), NOT_FOUND too; the
    correcting RL for RL-1475 T3/T4 must be ON MAIN BEFORE S4 merges"
    (`to-lead.md:20961`). Its ORDER CONDITION item 1 orders this record.
- **This record states the corrected code, quotes each `RL-1475` clause it corrects, and
  names where the code carries it.** It decides nothing beyond the two entries.

## The maintainer's entries, verbatim (the paragraphs this record carries)

From "2026-10-10 04:19:42 BST — RULING: rate-table 404 disagreement = (a) …", the reasoning
and item 1:

```text
CLAUDE.md §0: code and spec disagree, so decide which is wrong. Here it is the CODE, on the merits. RATE_TABLE_MISS is a SCORING code (a table lookup failed while pricing). A management route asked for a rate table that does not exist is a missing RESOURCE: 404 NOT_FOUND, as 03 §5.1 :943/:944 and RL-1555 T1 say.
1. WK-675 S4's routes answer 404 NOT_FOUND for an unknown rate table, mapped at the ROUTE layer. The shared loader (rate_tables.py:282) is NOT changed: RATE_TABLE_MISS stays correct on the scoring path. A red-first route test asserts 404 + NOT_FOUND for an unknown id.
```

From "2026-10-10 04:23:36 BST — RULING: WK-675 S4 read routes = (a) …", in full:

```text
(a) ADOPTED: one slice, one code. A missing resource on a read route is NOT_FOUND by the same reasoning as 04:19:42.
ORDER CONDITION: RL-1475 is a dated ruling whose T3/T4 say RATE_TABLE_MISS verbatim. Code on main must not contradict a standing ruling, even for one merge (decision first, then code, as §0's spec-first). So:
1. The correcting RL (corrects: RL-1475, T3/T4 only; RL-1475 gains corrected_by: in the same batch, front matter only) rides D6 beside FD 9941. It cites 03 §5.1 :943/:944 and my 04:19:42 and this entry.
2. It is an ACTIVATION-STYLE MERGE NEED of WK-675 S4: S4's ACK request shows the correcting RL on main (its id at main). WK-675 S4 merges late in lane C's order, so this costs nothing in practice.
3. S4's read routes: route-layer NOT_FOUND mapping, the loader unchanged, red-first tests on both reads.
4. FD 9941 keeps its scope (the existing diff routes on main). The reads are fixed here, not widened into it.
(b) rejected: it ships a slice that answers two different codes for the same condition.
```

## The corrected code

1. **`GET /api/v1/rate-tables/{slug}@{version}` and
   `GET /api/v1/rate-tables/{slug}@{version}/cells` answer 404 `NOT_FOUND`** for an unknown
   table or version, or another workspace's. It is a missing resource, not a failed lookup
   while pricing.
2. **`RATE_TABLE_MISS` stays the scoring-path code.** It stays in `03` §5.1's *Error codes
   owned by this module* (`docs/specs/03-rating-engine.md:974` at `26f93be0`), and in the
   scoring route's per-quote codes (`backend/src/app/api/score.py:100` at `26f93be0`,
   `_PER_QUOTE_CODES`).
3. **The mapping is at the route layer.** The shared loader is not changed.

**The convention this follows**, in `03` §5.1 at `26f93be0`: the diff row
(`docs/specs/03-rating-engine.md:943`) answers "**404** `NOT_FOUND` for a portfolio that is
missing or in another workspace", and the diff-cells row (`:944`) answers "**404**
`NOT_FOUND` for an unknown table, version or `against`". `RL-1555` T1
(`docs/rulings/RL-01555-wk-675-s3-s4-s13-dps-decided-the-algorithm-diff-route-typed-in-s3-the-manual-edit-route-typed-with-provenance-and-field-errors-two-job-streams.md:159`)
gives the manual-edit route "**404** `NOT_FOUND` for an unknown table or `base_version`".

## The `RL-1475` clauses this corrects — read at `26f93be0`

`RL-1475` is `docs/rulings/RL-01475-pl-1286-dp-4-texts-the-algorithm-read-by-slug-at-version-s2-and-a-rate-table-version-s-definition-and-cell-page-reads-s4-a-version-s-table-list-is-its-pins.md`.
Each clause below is quoted verbatim. In each, `RATE_TABLE_MISS` is read as `NOT_FOUND`;
every other word of the clause stands.

| `RL-1475` line | Verbatim | Read now as |
|---|---|---|
| :175 (T3, the `FR-<b>` row) | "Both reads require `rating:read` and answer **404** `RATE_TABLE_MISS` for an unknown table or version, or another workspace's." | "… answer **404** `NOT_FOUND` for an unknown table or version, or another workspace's." |
| :186 (T4, the definition read, three-cell form) | "**404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's." | "**404** `NOT_FOUND` on an unknown table or version or another workspace's." |
| :187 (T4, the cells read, three-cell form) | "**404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's;" | "**404** `NOT_FOUND` on an unknown table or version or another workspace's;" |
| :193 (T4, the definition read, four-cell form) | "**404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's." | As :186. |
| :194 (T4, the cells read, four-cell form) | "**404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's;" | As :187. |

**Also read, and not corrected by this record:**

- `RL-1475` *Acceptance* item 5 (`:274`): "Another workspace's `slug@version` answers 404
  `RATE_TABLE_MISS` on both". It is not in T3 or T4, and 04:23:36 scopes this record to
  "T3/T4 only". This record does not change it; the lead is told.
- `RL-1475` *Evidence* (`:59`) describes the loaders' code at `1dd5e264`. It is a record of
  that tree and stays true of it.

## What is not changed

- **The shared loader keeps `RATE_TABLE_MISS`**:
  `backend/src/app/platform/rate_tables.py:282` at `26f93be0`, in `_load_table` (`:268`),
  `raise PlatformError("RATE_TABLE_MISS", "Rate table not found", 404, …)`. The scoring path
  relies on it (04:19:42 item 1).
- **FD 9941 keeps its scope**: the existing diff routes on main (04:23:36 item 4). It is a
  separate record; at the time of writing it is a reserved working id on no origin ref.

## Where the code carries it — on WK-675 S4's branch, pending

WK-675 S4's branch is `sl-1559-wk675-s4`, read at its head
`b19a97fc820372eeb450154d107d4a0eacdf687b`. None of what follows is on `main` at `26f93be0`.

- **The route-layer mapping exists** for the manual-edit route:
  `backend/src/app/api/rate_tables.py:69` on that branch, `spec_not_found()`, which re-raises
  a `RATE_TABLE_MISS` as `PlatformError("NOT_FOUND", "Not Found", 404, …)`, added by
  `20a220fd` and used at `:165` and `:170`.
- **The two reads do not yet use it**: `read_rate_table` (`:438`) and
  `read_rate_table_cells` (`:450`) on that branch, added by `fe7fd56e`, call the service
  without `spec_not_found()`. The commit that maps them, with the red-first tests on both
  reads (04:23:36 item 3), is **pending**; this record names no SHA for it.

If S4's branch is rebased or squash-merged, these SHAs and line numbers name that branch at
`b19a97fc`, not the merged result.

## What it obliges

- `RL-1475` gains `corrected_by: [RL-9942]` in this commit, front matter only.
- **This record is on main before WK-675 S4 merges**: S4's ACK request shows its id at main
  (04:23:36 ORDER CONDITION item 2).
- Nothing else. The route mapping and the tests are S4's, under the entries above; this
  record adds none of them.

## What this record does not decide

- `RL-1475` *Acceptance* item 5, or any `RL-1475` clause other than those in the table.
- The `PL-1558` *Acceptance* 4 correction, which 04:19:42 item 2 assigns to a dated
  plan-delta line in S4's ledger.
- FD 9941's remedy or its slice.
