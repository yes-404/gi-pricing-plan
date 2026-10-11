---
id: RL-1514
family: ruling
title: CR-1212's NFR-498 row is corrected — the limbs open at P2 include rate table versions, bulk operations and algorithm edits, owned by WK-1178 and bound to land before the P2 code freeze
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: decision-maker           # the correction is a verified fact; the owner and bound it records are the maintainer's (by delegation)
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: CR-1212
relates: [CR-1212, FD-1513, NFR-498, WK-1178, WK-674, PL-1237, CR-925]
---

# RL-1514 — CR-1212's NFR-498 row is corrected: rate table versions, bulk operations and algorithm edits are open too

## How this was ruled

- **Filed under working id 9519 (minted as RL-1514), allocated by the lead.** The finding this
  record cites, working id 9529 (draft PR #1201), is minted in the same batch as **FD-1513**,
  and joins `relates:`. The texts below were written under the working ids; they are replaced
  by the minted ids outside quoted entries.
- **The decisions are not this record's.** They are the maintainer's, by delegation, in the
  entry "2026-10-05 17:45:06 BST — FD 9529 (NFR-498, #1201 @be1fba43): MEDIUM and
  carry-forward to WK-1178 accepted, with a P2 landing bound; CR-1212 correcting RL yes; A-2
  does not absorb" (`~/gi-pricing-plan.local/channel/to-lead.md`, local, not in the
  repository). Items 1 and 3, verbatim:

  > 1. Your decision is ACCEPTED: MEDIUM; carry forward, owner WK-1178; the 13 verdict is "deferred with an owner". ADDED BOUND: the fix lands BEFORE THE P2 CODE FREEZE (Wed 4 Nov). An unaudited rate-table or algorithm change is exactly what the exit demo's governance story claims cannot happen, so this is not a P3 carry. The register's Decision cell carries the bound; the P2 phase closure record lists it.

  > 3. CR-1212: YES, a correcting RL (corrects: CR-1212; CR-1212 gains corrected_by:), filed by a DM when a seat frees, citing FD 9529.

- **What this record adds** is the corrected row, with every locator in it re-read by the
  decision-maker at two trees (below). The finding's own locators were read at `4d3be141`;
  none was taken from it.

## Verified first, at `9f6bfed1` (CR-1212's tree) and at `5fe56b87` (origin/main)

**The row being corrected.** `CR-1212`
(`docs/closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md`,
`tree: 9f6bfed1a94838d92bdc76475e03f8b5b078527a`), under "G4: the P2 NFRs, one by one", reads
at `:120` on origin/main `5fe56b87`:

> | NFR-498 | WK-669/670/671/674 | compile `test_rating_version_compile.py:658` | deploy, rollback and routing limbs open, WK-674 |

Its disposition (a) at `:141` reads "**WK-674 owns** NFR-494, NFR-497 (availability),
**NFR-498 (deploy limbs)**, …". `PL-1237` (WK-674's map plan) `:298` confirms WK-674's limb is
"**this Work's limb only:** deployments, rollbacks and routing changes (the other limbs are
other Works')". The accepted G4 dispositions therefore give the other limbs no owner.

**The requirement.** `docs/specs/03-rating-engine.md:1339` at `5fe56b87`:

> | **NFR-498** | Audit: algorithm edits, rate table versions, bulk operations, compilations, approvals, deployments, rollbacks, and routing changes all emit Audit Events with before/after state. |

**The code, at both trees.** Paths are under `backend/src/app/`. Each line was located with
`git grep -n` against the named tree, which numbers the whole file. The `audit` column is
`git show <tree>:<path> | grep -ci audit`.

| What | Locator at `9f6bfed1` | Locator at `5fe56b87` | Audit Event? |
|---|---|---|---|
| Route `POST /rate-tables/{slug}/seed-from-model` | `api/rate_tables.py:112`, path `:113`, call `service.seed_from_model(` `:135` | `api/rate_tables.py:70`, path `:71`, call `:98` | — |
| `seed_from_model` | `platform/rate_tables.py:95`; `return await _persist_new_version(` `:165` | `platform/rate_tables.py:96`; `:183` | **No** |
| Route `POST /rate-tables/{slug}@{version}/import` | `api/rate_tables.py:241`, path `:242`, call `service.import_confirmed(` `:289` | `api/rate_tables.py:205`, path `:206`, call `:253` | — |
| `import_confirmed` | `platform/rate_tables.py:365`; `_persist_new_version(` `:408` | `platform/rate_tables.py:419`; `:462` | **No** |
| Route `POST /rate-tables/{slug}@{version}/bulk-operation` | `api/rate_tables.py:148`, path `:149`, call `service.bulk_operation(` `:181` | `api/rate_tables.py:112`, path `:113`, call `:145` | — |
| `bulk_operation` | `platform/rate_tables.py:730`; `baseline =` `:761`, `derived =` `:763`; `_persist_new_version(` `:775` | `platform/rate_tables.py:796`; `:827`, `:829`; `:841` | **No** — the before (`baseline`) and after (`derived`) are both in hand and not recorded |
| `_persist_new_version` (the one writer) | `platform/rate_tables.py:604`; `RateTableVersionRow(` `:633`; `table_row.current_version = version_number` `:667` | `platform/rate_tables.py:670`; `:699`; `:733` | **No** |
| Route `POST /rating-algorithms` | `api/rating_algorithms.py:28`, path `:29`, call `service.create_algorithm(` `:47` | the same three lines | — |
| `create_algorithm` | `platform/rating_algorithms.py:72`; `RatingAlgorithmRow(` `:101`; `session.add(row)` `:108`; `flush()` `:109` | `platform/rating_algorithms.py:94`; `:123`; `:130`; `:131` | **No** |
| `audit` references in `api/rate_tables.py`, `platform/rate_tables.py`, `worker/rate_table_handlers.py`, `api/rating_algorithms.py`, `platform/rating_algorithms.py` | 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0 | — |

`RateTableVersionRow(` occurs once in `platform/rate_tables.py` at each tree
(`git grep -c 'RateTableVersionRow(' <tree> -- backend/src/app/platform/rate_tables.py` → `1`).
So all three rate-table routes write through the one writer, and the writer records nothing.

**Positive control, same predicate, same trees.** `git grep -n 'audit\.record(' <tree> --
backend/src/app/platform/rating_versions.py backend/src/app/worker/rating_handlers.py` finds
`rating_versions.py:201`, `:286` and `rating_handlers.py:86` at `9f6bfed1`, and
`rating_versions.py:265`, `:391` and `rating_handlers.py:96` at `5fe56b87`. The search finds the
writer where it is called. Its zero in the five modules above is an absence, not a blind spot.

**Not checked.** No test was run, and nothing was executed against a database. The absence is
read from source. FD-1513's "What is and is not claimed" bounds the other mechanisms it
searched for (database triggers, middleware); that search was not repeated here.

**So the row was wrong at its own tree.** At `9f6bfed1`, the day `CR-1212` was written, three
of NFR-498's named classes had no Audit Event, and the row listed none of them as open. The
gap is unchanged at `5fe56b87`.

## Ruled

1. **`CR-1212:120`'s NFR-498 row is corrected.** It reads, in substance:

   | NFR | Owner | Measured where | Status at `9f6bfed1` |
   |---|---|---|---|
   | NFR-498 | WK-669/670/671/674; **WK-1178** for the limbs below | compile `test_rating_version_compile.py:658` | **Open:** deploy, rollback and routing, WK-674 (unchanged). **Open and unrecorded until FD-1513:** rate table versions (`seed_from_model`, `import_confirmed`), bulk operations (`bulk_operation`) and algorithm edits (`create_algorithm`), all with no Audit Event. Owner **WK-1178**, per FD-1513; §13 verdict **deferred with an owner**; **bound: lands before the P2 code freeze, Wed 4 Nov 2026** |

2. **G4 disposition (a) at `:141` is read with one addition.** WK-674 still owns NFR-498's
   deploy limbs only, as `PL-1237:298` states. **WK-1178 owns its rate-table-version,
   bulk-operation and algorithm-edit limbs.** WK-674's scope is unchanged.
3. **The bound is the maintainer's** (item 1 of the 17:45:06 entry): the fix lands before the
   P2 code freeze. The freeze is dated Wed 2026-11-04 in `docs/roadmap.md:584`. It is not a P3
   carry.
4. **`CR-1212`'s body is unchanged.** It records what was believed on 2026-09-28. This record
   is its correction, and `CR-1212` gains `corrected_by:` naming it (see "What it obliges").

## What it obliges

- **`CR-1212`'s front matter, at the mint turn (done in batch B4: `corrected_by: [RL-1263, RL-1287, RL-1514]`).** `corrected_by: [RL-1263, RL-1287]` gains this
  record's minted id, as the only edit to `CR-1212`, which check 34 permits
  (`docs/process/document-ids.md:230`). It is not added before the mint. That follows the newest
  merged correcting ruling, `RL-1418` (`corrects: RL-1361`). Its pre-mint commits
  (`26bac90709`, `44e38781f5`) left `RL-1361` untouched, and the append arrived with the minted
  id. The older `RL-1287` appended a working id before the mint (`9e570bd759`) and renamed it at
  the mint (`bb64f0d96e`). It is not followed, because a working id in another record's front
  matter does not resolve.
- **The P2 phase closure record** lists this bound under G3 and G4. That is item 1 of the
  17:45:06 entry, and the record is the lead's to write.
- **The fix** belongs to the slice FD-1513's register row names under WK-1178. Its form is item
  2 of the same entry, recorded on #1201: red first per class, with before and after state
  asserted. It is not ruled here.
- **What this does not decide.** It does not decide whether the sub-graph create and version
  paths (`api/sub_graphs.py`) are algorithm edits under NFR-498. The 17:45:06 entry gives that
  question to the fix slice's read-first list, "in or out with a reason". It does not touch
  WK-674's limbs or the rest of `CR-1212`'s table.

## Acceptance — the violation that must become detectable

The violation: **a rate table version written by seed, import or bulk operation, or a Rating
Algorithm created, with no Audit Event that carries its before and after state.** At both
trees above, each of the four classes commits with no event. Nothing fails today.

- *Violation: `POST /rate-tables/{slug}/seed-from-model` commits a version and
  `audit_events` gains no row for it.* The fix slice's test reds on `5fe56b87`.
- *Violation: `POST /rate-tables/{slug}@{version}/import` commits a version with no event, or
  with an event whose `before` is not the baseline version.*
- *Violation: `POST /rate-tables/{slug}@{version}/bulk-operation` commits a version with no
  event, or with an event that lacks `baseline` as `before` and the derived version as `after`.*
- *Violation: `POST /rating-algorithms` creates a Rating Algorithm with no event.*
- **The record-keeping half has no failing check, and this says so.** No check reads a
  closure record's NFR table against the code. What is checkable is check 34: an edit to
  `CR-1212`'s body, or a `corrected_by:` entry whose record does not name `CR-1212` in
  `corrects:`, reds it.

Drafted as working id 9519; minted as RL-1514 on 2026-10-08 (batch B4).
