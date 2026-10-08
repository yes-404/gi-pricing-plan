---
id: FD-1513
family: finding
title: Rate table version writes and rating algorithm saves emit no Audit Event, so NFR-498 is unmet for two of its named classes and no record owns the gap
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
corrected_by: []
relates: [NFR-498, FR-230, FR-233, FR-235, WK-670, WK-674, WK-1178, CR-925, CR-927, CR-1212, RL-1514, RL-1515, PL-1516, SL-1517]
---

# Rate table version writes and rating algorithm saves emit no Audit Event, so NFR-498 is unmet for two of its named classes and no record owns the gap

**Filed under working id 9529 (minted as FD-1513), 2026-10-05.** Every locator was read at `origin/main`
`4d3be1414ad4dacdaa0c14ef49fb21853adbaed6` (`git show origin/main:<path>`). Read-only: no test, gate or database was run.
The claim reached the auditor relayed (from a planner, via the lead), so each part below was
re-derived from the code and the records, not taken from the relay.

## Finding

**Proposed severity: MEDIUM; proposed owner: WK-1178** (the lead decides both; reasons at the end).

`03` §9 **NFR-498** (`docs/specs/03-rating-engine.md:1339`) reads, with no dated amendment:
"Audit: algorithm edits, rate table versions, bulk operations, compilations, approvals,
deployments, rollbacks, and routing changes all emit Audit Events with before/after state."
It names **nine** classes. Two are built with no Audit Event at all, and no closure record,
finding, ruling or plan names either as open:

1. **Rate table versions and bulk operations.** Three routes write a rate table version, and all
   three funnel into one writer that never calls `audit.record`.
2. **Algorithm edits.** `create_algorithm` persists a Rating Algorithm and never calls it.

`06` R2 (`backend/src/app/platform/audit.py:3-5`) is the contract the writer is built to: a governed
transition writes its event in the same transaction as the change. A rate table version feeds the
price; a version written with no event is a mispricing with no record of who made it or what it replaced.

## The Audit Event writer, read in full

`backend/src/app/platform/audit.py` (204 lines) is the one writer. `record(session, *, workspace_id,
actor, source, action, entity_ref, before, after, justification, job_id)` (`:52-`) refuses a call
with no open transaction, takes a per-workspace advisory lock, and appends to a hash chain; it has no
commit and no `try/except`. Callers of `audit.record` in `backend/src` at the tree, by module:
`api/service_accounts.py`, `api/settings.py`, `auth/service.py`, `data/ingestion.py`,
`platform/approvals.py`, `backtests.py`, `blobs.py`, `comparison.py`, `datasets.py`, `deployments.py`,
`environments.py`, `jobs.py`, `metrics.py`, `model_specs.py`, `modelling.py` and others (the list is a
sweep of `git grep -n 'audit.record' origin/main -- backend/src`). Of the rating modules, only
`platform/rating_versions.py` (`:265`, `:391`) and `worker/rating_handlers.py` (`:96`) call it.
`api/rate_tables.py`, `platform/rate_tables.py`, `worker/rate_table_handlers.py`,
`api/rating_algorithms.py` and `platform/rating_algorithms.py` have **no** `audit` reference:
`git grep -l audit origin/main -- <those five paths>` returns nothing.

## Per class

| NFR-498 class | Write path (route → service, at the tree) | Audit Event with before and after? | Evidence |
|---|---|---|---|
| **rate table versions** | `POST /rate-tables/{slug}/seed-from-model` (`api/rate_tables.py:70`, handler `:77`, call `:98`) → `seed_from_model` (`platform/rate_tables.py:96`) → `_persist_new_version` (`:670`) | **No** | `RateTableVersionRow(...)` added at `:699`/`:723`, then `table_row.current_version = version_number` (`:733`); no `audit.record` anywhere in the module |
| **rate table versions** (import) | `POST /rate-tables/{slug}@{version}/import` (`api/rate_tables.py:205`, call `:253`) → `import_confirmed` (`platform/rate_tables.py:419`) → `_persist_new_version` | **No** | same writer |
| **bulk operations** | `POST /rate-tables/{slug}@{version}/bulk-operation` (`api/rate_tables.py:112`, handler `:118`, call `:145`) → `bulk_operation` (`platform/rate_tables.py:796`) → `_persist_new_version` | **No** | `bulk_operation` holds `baseline` and `derived` before it persists (`:827`, `:829`), so the before and after are available and are not recorded |
| **algorithm edits** | `POST /rating-algorithms` (`api/rating_algorithms.py:28`, handler `:34`) → `create_algorithm` (`platform/rating_algorithms.py:94`) | **No** | `RatingAlgorithmRow(...)` at `:123`, `session.add(row)`, `flush()`, `return row`; no event |
| compilations | `POST /rating-versions/{id}/compile` → worker `_rating_compile` | **Yes** (`rating_version.compiled`, before `bundle_hash`) | `worker/rating_handlers.py:96-106`; `CR-927` row NFR-498 cites the marker `test_rating_version_compile.py:655` |
| approvals | `platform/approvals.py` | **Yes** | `:329` `approval_request.submitted`, `:484` `approval_request.<decision>`, `:543` `.withdrawn`, `:232` `approval_policy.updated` |
| rating version create and transitions | `platform/rating_versions.py` | **Yes** (not a named NFR-498 class; listed for completeness) | `:265` `rating_version.created`, `:391` `rating_version.<transition>` with the row's prior status as `before` |
| deployments | `platform/deployments.py` | **Yes** | `:323`, `:427` `deployment_request.<state>`, `:542` `deployment.created` (WK-674 Slice 2, `LG-1405`) |
| rollbacks | WK-674 Slice 5 (`SL-1259`, `draft`) | Not built; owned | `docs/roadmap.md` SL-1259 row; `CR-1212:120` |
| routing changes | WK-674 Slice 6 (`SL-1260`, `draft`) | Not built; owned | `docs/roadmap.md` SL-1260 row; `CR-1212:120` |

The two **No** classes are not in the rows owned by anyone else: a sweep of `docs/` at the tree for
`rate.?table.*audit`, `audit.*rate.?table` and `algorithm edit` over `docs/findings`, `docs/rulings`,
`docs/plans`, `docs/roadmap.md` and `docs/open-questions.md` finds no record of the gap (the only
`algorithm edit` hit is `CR-925:153`, the NFR-498 text itself).

## Is it already recorded or owned?

**No.** `git grep -n 'NFR-498' origin/main -- docs` (the predicate; read over every hit):

- `CR-925:153` (plan review 9) quotes NFR-498 verbatim, including "algorithm edits, rate table versions,
  bulk operations", and then finds **only** that compile lacked the event. It does not test the other
  named classes. (`CR-927:113` then records compile as "delivered and tested, and unplanned".)
- `CR-1212:120` is the P2 NFR table row: `NFR-498 | WK-669/670/671/674 | compile ...:658 | deploy, rollback
  and routing limbs open, WK-674`. The row **lists three open limbs, none of them rate tables or
  algorithms**; `:141` proposes "NFR-498 (deploy limbs)" to WK-674. It names WK-669 and WK-670 as owners
  beside WK-671, and both are closed with no audit event on the rate-table or algorithm routes.
- `PL-1237:298` states WK-674's NFR-498 limb is "this Work's limb only: deployments, rollbacks and
  routing changes (the other limbs are other Works')". The other limbs' Works are closed (WK-670,
  `CR-834`); no record reassigns them.
- No `FD-`, register row, `RL-` or `OQ-` row mentions NFR-498 (the sweep above). `register.md` has no row.

So the gap is real, and the one record that enumerates NFR-498's open limbs (`CR-1212:120`) is
incomplete about it: a phase exit would be read against a table that omits two unmet classes.

## What is and is not claimed

- Claimed: no route writing a rate table version or a Rating Algorithm records an Audit Event, at the
  tree above. Evidenced by reading the five modules and by `git grep -l audit` over them returning no file.
- Checked for another mechanism: `git grep -n -i 'audit' origin/main -- backend/src/app/db backend/src/app/main.py backend/src/app/api/deps.py`
  filtered for `trigger|middleware|rate_table|algorithm`, and `git grep -n -i trigger origin/main -- backend/alembic backend/src/app/db`
  filtered for `rate|audit`, return nothing. That bounds a Python and migration trigger path, not a database
  object created outside the repository.
- **Not** run: no test was written or executed. A red reproduction (a seed, an import and a bulk
  operation each followed by `audit_events` with no matching row; a `POST /rating-algorithms` likewise)
  is the first step of any fix and was not done here.

## Proposed owner, and why

- **WK-1178** (the standing maintenance Work, exempt from G1 and dispositioned under G3, `docs/roadmap.md`
  :565): the other open governance-integrity findings (`FD-1414`, `FD-1415`, `FD-1416`) ride there. The fix is small and local: one `audit.record` in `_persist_new_version`'s
  callers with `before` the baseline's version ref and `after` the new version, and one in
  `create_algorithm`.
- **Not WK-674**: its NFR-498 limb is deploy, rollback and routing by `PL-1237:298` and `CR-1212:141`; widening it
  would change a Work scope the maintainer accepted.
- **Not WK-670/671**: closed.

## Proposed severity, and why

MEDIUM, not LOW: a rate table version is a rated input and the platform's mission is auditability
(`CLAUDE.md` §1); the missing event is a spec requirement (`06` R2 sets the transaction rule), not a nicety. Not HIGH: no
wrong price is produced, the version rows are immutable and carry `created_by` and `change_note`
(`platform/rate_tables.py:699-720`), so *who and what* survive in the table, only the chain record and
the before-state do not.

## Disposition

- A §13 verdict is owed on NFR-498's rate-table, bulk-operation and algorithm-edit limbs: **delivered but
  untested** is wrong (nothing delivered); the proposal is **deferred with an owner (WK-1178)**.
- `CR-1212`'s NFR table should gain the two limbs; that is a correcting record, not an edit of the frozen one.

## Evidence

Every command was run read-only at `origin/main` `4d3be1414ad4dacdaa0c14ef49fb21853adbaed6`:

- `git grep -l audit origin/main -- backend/src/app/api/rate_tables.py backend/src/app/platform/rate_tables.py backend/src/app/worker/rate_table_handlers.py backend/src/app/api/rating_algorithms.py backend/src/app/platform/rating_algorithms.py` → no output.
- `git grep -n 'audit.record' origin/main -- backend/src` filtered to `rating|rate|algorithm` → `rating_versions.py:265`, `:391`, `rating_handlers.py:96` only.
- `git grep -n 'RateTableVersionRow(\|RatingAlgorithmRow(' origin/main -- backend/src` (excluding `select` and `class`) → `platform/rate_tables.py:699` and `platform/rating_algorithms.py:123`: one writer each.
- `git grep -n 'NFR-498' origin/main -- docs` → read at every hit; the record hits are `CR-925:153`, `CR-927:113`, `CR-1212:120` and `:141`, `PL-1237:298`.
- Not measured: whether a test pins the absence; no test was run.

### Disposition — ruled 2026-10-05 17:45:06 BST (pre-mint)

**Source:** the maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-05 17:45:06 BST —
FD 9529 (NFR-498, #1201 @be1fba43): MEDIUM and carry-forward to WK-1178 accepted, with a P2 landing bound; CR-1212
correcting RL yes; A-2 does not absorb". Quoted verbatim, items 1 to 4:

> 1. Your decision is ACCEPTED: MEDIUM; carry forward, owner WK-1178; the 13 verdict is "deferred with an owner". ADDED BOUND: the fix lands BEFORE THE P2 CODE FREEZE (Wed 4 Nov). An unaudited rate-table or algorithm change is exactly what the exit demo's governance story claims cannot happen, so this is not a P3 carry. The register's Decision cell carries the bound; the P2 phase closure record lists it.
> 2. The fix slice: red-first per class (seed_from_model, import_confirmed, bulk_operation, create_algorithm), with before/after state asserted. Its read-first list also covers the sub-graph create and version paths (api/sub_graphs.py), since they are algorithm edits too: in or out with a reason, not silently. It runs after the emergency slice and serialises against A-2 on rating_algorithms.py, named both ways.
> 3. CR-1212: YES, a correcting RL (corrects: CR-1212; CR-1212 gains corrected_by:), filed by a DM when a seat frees, citing FD 9529.
> 4. A-2 does NOT absorb the audit event. Agreed.

**Severity** MEDIUM; the §13 verdict on NFR-498's rate-table, bulk-operation and algorithm-edit limbs is **deferred with an
owner: WK-1178**. **Bound:** the fix lands before the P2 code freeze (Wed 4 Nov 2026), and the P2 closure record lists it.

**Where each limb goes (working ids 9515, 9514 and 9519, minted as SL-1517, PL-1516 and RL-1514):**

- **SL-1517 / PL-1516**, under WK-1178: the fix. Red first per class (`seed_from_model`, `import_confirmed`,
  `bulk_operation`, `create_algorithm`), before and after state asserted; read-first includes `api/sub_graphs.py`
  (in or out with a reason). Runs after the emergency slice and serialises against A-2 on `rating_algorithms.py`, named
  both ways.
- **RL-1514**: the correcting record for `CR-1212:120` (`corrects: CR-1212`; `CR-1212` gains `corrected_by:`), filed by a
  decision-maker.
- A-2 does not absorb the audit event.

Event that next confirms or discharges the row: a merged SL-1517 with the four classes recording an Audit Event, before the
P2 code freeze.
