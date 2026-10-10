---
id: RL-1584
family: ruling
title: RL-1475 corrected — a rate table version's definition and cell-page reads answer 404 NOT_FOUND for an unknown table or version; RATE_TABLE_MISS stays the scoring code
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
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

# RL-1584 — RL-1475 corrected: the two rate table version reads answer 404 `NOT_FOUND`; `RATE_TABLE_MISS` stays the scoring code

*Disclosure: drafted under working id 9942; minted as RL-1584 on 2026-10-10, in the D6 batch mint PR.*

## Ruled

- **Filed under working id 9942 (minted as RL-1584), reserved by the lead (team-lead) on 2026-10-10.** In the
  same commit, `RL-1475`'s header gains `corrected_by: [RL-1584]`, the append check 34
  allows (`docs/process/document-ids.md` §1, the `corrected_by:` / `corrects:` lines of the
  front-matter block). Not one byte of `RL-1475`'s body changes. When this record is
  minted, the working id in both headers and in this record is replaced by the minted id.
- **The decisions are not this record's.** They are the maintainer's (by delegation), in
  three entries of `~/gi-pricing-plan.local/channel/to-lead.md`, quoted below by header:
  - "2026-10-10 04:19:42 BST — RULING: rate-table 404 disagreement = (a), the SPEC governs
    (NOT_FOUND); the fix is at the route layer; one FD for the pre-existing drift"
    (`to-lead.md:20952`);
  - "2026-10-10 04:23:36 BST — RULING: WK-675 S4 read routes = (a), NOT_FOUND too; the
    correcting RL for RL-1475 T3/T4 must be ON MAIN BEFORE S4 merges"
    (`to-lead.md:20961`). Its ORDER CONDITION item 1 orders this record;
  - "2026-10-10 04:27:31 BST — RL 9942 scope = (a): it corrects every RL-1475 statement of
    the code (T3, T4 AND Acceptance 5 :274)" (`to-lead.md:20971`). It sets this record's
    scope: every place `RL-1475` states `RATE_TABLE_MISS` for a missing rate table on those
    routes, not T3 and T4 only.
- **This record states the corrected code, quotes each `RL-1475` clause it corrects, lists
  every `RATE_TABLE_MISS` in `RL-1475` as corrected or out of scope, and names where the
  code carries it.** It decides nothing beyond the three entries.

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

From "2026-10-10 04:27:31 BST — RL 9942 scope = (a) …", in full. It widens 04:23:36's "T3/T4
only" above:

```text
(a) ADOPTED. My 04:23:36 "T3/T4 only" named the statements I knew of. Its intent was that the record speaks one code. RL 9942 corrects each place RL-1475 states RATE_TABLE_MISS for a missing rate table on those routes (T3, T4, Acceptance 5 :274), listing each by line, so no statement is left uncorrected. The auditor greps RL-1475 for every remaining "RATE_TABLE_MISS" and lists each hit in RL 9942 as corrected or as out of scope (a scoring-path statement, which stays). RL-1475 changes front matter only (corrected_by). Rides D6. The S4 merge need is unchanged.
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
| :274–:275 (*Acceptance* item 5, Isolation) | "Another workspace's `slug@version` answers 404 `RATE_TABLE_MISS` on both reads." | "Another workspace's `slug@version` answers 404 `NOT_FOUND` on both reads." |

## Every `RATE_TABLE_MISS` in `RL-1475` — corrected or out of scope

Run in this worktree at `26f93be0` (`RL-1475`'s body is the same at main), verbatim:
`git grep -n RATE_TABLE_MISS HEAD -- 'docs/rulings/RL-01475-*'`. It returns **7 lines**
with **8 occurrences** (`:59` carries two). Each is listed below.

| `RL-1475` line | Where in `RL-1475` | Occurrences | Disposition |
|---|---|---|---|
| :59 | *Evidence at `1dd5e264`*, "Rate table reads": `_load_table` (`rate_tables.py:189-205`, 404 `RATE_TABLE_MISS`) and `_load_version` (`:462-481`, 404 `RATE_TABLE_MISS`) | 2 | **Out of scope (the shared loaders, which the scoring path uses; stays).** It describes the loaders' code at `1dd5e264`, not what a route answers. The loaders keep `RATE_TABLE_MISS` (04:19:42 item 1; 04:23:36 item 3). |
| :175 | T3, the `FR-<b>` row | 1 | **Corrected** (table above). |
| :186 | T4, the definition read, three-cell form | 1 | **Corrected**. |
| :187 | T4, the cells read, three-cell form | 1 | **Corrected**. |
| :193 | T4, the definition read, four-cell form | 1 | **Corrected**. |
| :194 | T4, the cells read, four-cell form | 1 | **Corrected**. |
| :274 | *Acceptance* item 5, Isolation | 1 | **Corrected**. |

After this record, no `RL-1475` statement of what a rate table read route answers for a
missing rate table says `RATE_TABLE_MISS`.

## What is not changed

- **The shared loader keeps `RATE_TABLE_MISS`**:
  `backend/src/app/platform/rate_tables.py:282` at `26f93be0`, in `_load_table` (`:268`),
  `raise PlatformError("RATE_TABLE_MISS", "Rate table not found", 404, …)`. The scoring path
  relies on it (04:19:42 item 1).
- **FD-1585 keeps its scope**: the existing diff routes on main (04:23:36 item 4). It is a
  separate record; at the time of writing it is a reserved working id on no origin ref.

## Where the code carries it — on WK-675 S4's branch, not on main

WK-675 S4's branch is `sl-1559-wk675-s4`, read at its head
`918b9933210db03734c9b3d267c0031f0dda1fb2`. None of what follows is on `main` at `26f93be0`.

- **The route-layer mapping**: `backend/src/app/api/rate_tables.py:69` on that branch,
  `spec_not_found()`, which re-raises a `RATE_TABLE_MISS` as
  `PlatformError("NOT_FOUND", "Not Found", 404, …)`. It was added by `20a220fd` for the
  manual-edit route (used at `:166` and `:171`).
- **The two reads use it**: `918b9933` ("fix(rating): the two rate-table reads answer 404
  NOT_FOUND, like the edit route (FR 9940)") wraps `read_rate_table` (`:439`, the wrap at
  `:443`) and `read_rate_table_cells` (`:452`, the wrap at `:464`) in `spec_not_found()`.
- **The test**: `backend/tests/test_rate_table_route_codes.py` on that branch,
  `test_the_two_reads_answer_404_not_found_for_an_unknown_table`, added by `918b9933`
  (04:23:36 item 3). This record does not assert that it was seen red first; S4's ledger
  records that.

If S4's branch is rebased or squash-merged, these SHAs and line numbers name that branch at
`918b9933`, not the merged result.

## What it obliges

- `RL-1475` gains `corrected_by: [RL-1584]` in this commit, front matter only.
- **This record is on main before WK-675 S4 merges**: S4's ACK request shows its id at main
  (04:23:36 ORDER CONDITION item 2).
- Nothing else. The route mapping and the tests are S4's, under the entries above; this
  record adds none of them.

## Acceptance — the violation that must become detectable

The violation: `RL-1475` states `RATE_TABLE_MISS` for a missing rate table on the definition or cell-page read routes, and this record does not list that statement as corrected.

- `git grep -n RATE_TABLE_MISS -- docs/rulings/RL-01475-*` prints each hit, and each hit appears in the section "Every `RATE_TABLE_MISS` in `RL-1475` — corrected or out of scope" as corrected or as out of scope (a scoring-path statement, which stays). This is the check the entry "2026-10-10 04:27:31 BST — RL 9942 scope = (a): it corrects every RL-1475 statement of the code (T3, T4 AND Acceptance 5 :274)" in `to-lead.md` gives the auditor: *"The auditor greps RL-1475 for every remaining "RATE_TABLE_MISS" and lists each hit in RL 9942 as corrected or as out of scope."* *Violation: a hit with no row in that section.*
- The code half, that the two read routes answer 404 `NOT_FOUND`, is WK-675 S4's red-first route tests (the entries "2026-10-10 04:19:42 BST" item 1 and "2026-10-10 04:23:36 BST" item 3), not this record's check. *Violation: a read route that answers `RATE_TABLE_MISS` for an unknown table or version.*

## What this record does not decide

- Any `RL-1475` clause other than those this record lists as corrected.
- The `PL-1558` *Acceptance* 4 correction, which 04:19:42 item 2 assigns to a dated
  plan-delta line in S4's ledger.
- FD-1585's remedy or its slice.
