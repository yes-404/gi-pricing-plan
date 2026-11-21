---
id: ADR-2157
family: decision
title: The database holds an approved rating version's content, and the loader checks the bundle it loads
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-16
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 559faad4f65209d9336de3049d95ad6f701305ae
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-44, FR-351, FR-239, FR-240, FR-267]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2157 — The database holds an approved rating version's content, and the loader checks the bundle it loads

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer; the detail was decided on the maintainer's behalf by delegation, 16 Nov 2026.
- **Decision issue:** [#1907](https://github.com/yes-404/gi-pricing-plan/issues/1907) (the Work: the database holds an approved rating version's content, and the loader checks the bundle it loads)
- **Decision:** [the acceptance comment of 2026-11-16](https://github.com/yes-404/gi-pricing-plan/issues/1907#issuecomment-6912238139), which accepts the Work as two pull requests and lists what the first holds.
- **Enacted by:** the pull request that adds this record (PR-1 of #1907).

## Context

A rating version is the unit a quote is priced against. Its status was already held by the database: the approval guard refuses a row that is written `approved` without the decided approval request for its reference. The content columns of a version past `draft` (its bundle, its evidence, its pins and the rest) were held by the application's own writers and not by the database, and the approval guard's status condition looked only at the value `approved`, so a version in a status after approval was not held at all. The status column accepted any string. A decided approval request's decision columns were not held either. The scoring path read the blob a version names and hydrated it without comparing it with the hash recorded for the version.

## Decision

1. **Once a rating version's status has left `draft`, the database holds its content columns.** A row trigger permits exactly the transitions the application's own writers make, each read from the code: `review` to `approved` and `review` to `draft`, with `updated_at`. Every other change is refused with SQLSTATE `42501`. A status the platform does not define is held like `approved`, and an update that changes nothing is allowed, decided by comparing every column.
2. **A rating version in a status after approval is held as an approved one is.** The approval guard takes a list of statuses held like `approved`; `rating_versions` names `live` and `retired`. Nothing writes either status today; the deployment slice that does adds its transition to the trigger table in its own migration, and a migration that must update a version past `draft` disables the trigger inside itself and says why.
3. **The status column accepts only the statuses the platform defines** (a CHECK). The migration counts any row outside them and stops; it rewrites nothing.
4. **A decided approval request's decision columns are held**: `status`, `decided_at` and `withdrawn_reason` change only along the state machine's edges (`review` to `approved`, `rejected` or `changes_requested` with `decided_at` set and no `withdrawn_reason`; `review` to `withdrawn` with `decided_at` set and a non-empty `withdrawn_reason`; `approved` to `withdrawn` with `decided_at` unchanged and a non-empty `withdrawn_reason`). Withdrawing the request of an approved rating version is refused by the decision hook (`APPROVAL_SUBJECT_NOT_IN_REVIEW`) and moves nothing; the trigger agrees with that.
5. **The loader checks the bundle it loads.** One function compares the hash recorded for the version, the bundle's own stored `content_hash` and the hash recomputed from its graph and pins, and, for a deployed version, the hash the Deployment recorded. It is used wherever a stored bundle is loaded: the scoring fetch, re-validation (submit, deploy, rollback), a switch, and the regression and dislocation runs. A census test fails if a stored bundle's payload is parsed anywhere else in the backend. A mismatch is refused as an internal integrity error with its own registered code, `BUNDLE_HASH_MISMATCH` (HTTP 500, defined in the backend error catalogue and recorded in prose in `03` FR-267 as an internal integrity error, not in a client-facing error table), audited, and logged with the version reference and no content. *(Added 2026-11-17, #1907: the payload is covered too. The loader compares the sha256 of the payload bytes it read with the digest the version's row records, before it uses them, and refuses a mismatch with the same code; the content hash covers the graph and pins only.)*
6. **The hold is made at load.** A process that already holds a bundle keeps it until it loads again; the refusal is reached whenever a slot is refilled after an eviction or a restart.
7. The trigger function bodies are pinned in the census (`md5(prosrc)` in `backend/tests/test_application_role.py`), and the models declare the guards.

**What this record does not do.** It does not decide who may move a version into `approved`: that stays the approval guard's evidence test, unchanged here. What it gives is exactly that the content of a version that was approved does not change, that a decided request's decision does not change, and that a bundle is served only when it matches its recorded hash.

## Options not taken

- Granting `UPDATE` per column instead of holding the content by trigger: it works at the privilege layer and doubles the number of places to keep in step with the writers. A follow-up Work.
- A trigger on the two bundle keys only: it would leave every other content column as it was.
- Comparing the recorded hash only: a stored field can be edited with the blob it describes; the recomputation from content cannot be matched without the graph.
- Holding the definition columns in `draft` too: no writer changes them after creation, but the Work says "once the status has left `draft`", and draft behaviour is unchanged here.

## Consequences

- A test that must put a version past `draft` into a state its writers never produce (a bundle edit on an approved version, evidence removed from one in review) simulates it in an owner transaction with triggers disabled, and says so. The only (table, trigger) pairs a test may disable are `(rating_versions, rating_versions_content_guard)` and `(approval_requests, approval_requests_decision_guard)`. The one seam is `edit_held_row_as_owner` in `backend/tests/conftest_db.py`, which calls `disable_trigger`, and the `_DISABLABLE` allow-list there; a census test fails if another test file writes `DISABLE TRIGGER` on either guard.
- The comparison costs nothing on a slot hit; on a cold load it adds string comparisons, a sha256 of the payload bytes and one canonical hash of the bundle, against the blob read and parse the cold load already pays.
- The pointer and provenance columns of the other governed tables, and a validation rule's status vocabulary, are PR-2 of #1907.
