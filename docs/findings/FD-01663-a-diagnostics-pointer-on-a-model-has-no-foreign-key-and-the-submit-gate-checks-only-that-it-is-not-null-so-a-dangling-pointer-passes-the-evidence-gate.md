---
id: FD-1663
family: finding
title: A diagnostics pointer on a Model has no foreign key and the submit gate checks only that it is not null, so a dangling pointer passes the evidence gate
status: active
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-677, SL-1527, FR-211, FR-202]
---

# FD-1663 — `diagnostics_id` is a bare UUID

*(Minted 2026-10-12 as FD-1663 from working id 9862, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Found by SL-1527: its CI fixture inserted a Model with `diagnostics_id=uuid4()` and nothing refused it. Filed from the lead's brief of 2026-10-12 and the maintainer's (by delegation) entries "2026-10-12 02:51:17 BST" (MEDIUM PROVISIONAL) and "2026-10-12 02:53:52 BST" (LOW, owner WK-677, with the facts below) (`to-lead.md`, local, cited by header). Every line was re-read at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12.

## Evidence

- `backend/src/app/db/models.py:1430`: `diagnostics_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))`. No `ForeignKey`.
- `backend/src/app/platform/modelling.py`, `_require_evidence` (`:1243`): the diagnostics check at `:1298` is `row.diagnostics_id is not None`. It never reads the `diagnostics` table, so a pointer to nothing passes the gate.
- **Two instances of a dangling pointer in tests.** `backend/tests/test_wf699_journey.py` (SL-1527's CI fixture, `diagnostics_id=uuid4()`, fixed by SL-1527), and, outside SL-1527's write set, `backend/tests/test_demo_rating_evidence.py:162`, in `_approved_model` (an approved GLM stand-in), which sets `diagnostics_id=uuid4()`. The second is a test-fixture instance for the owner's remedy.
- **Reachability (the HIGH trigger is not met).** No API caller can set `diagnostics_id`: the only assignment is `modelling.py:867` (`row.diagnostics_id = diagnostics_row.id`) on the fit path; `ModelCreate` and `SubmitModel` carry no such field; there is no `PATCH` or import route. Migration `9e4c7b21fa08` (`backend/migrations/versions/9e4c7b21fa08_diagnostics_id_immutable.py:73`) makes the pointer immutable once set (`NEW.diagnostics_id IS DISTINCT FROM OLD.diagnostics_id`).
- **Deletion.** `DiagnosticsRow` is insert-only: migration `d4e5f6a7b8c9` (`backend/migrations/versions/d4e5f6a7b8c9_modelling_diagnostics.py:84-86`) grants `SELECT, INSERT` and revokes `UPDATE, DELETE` from the application role and from `PUBLIC`. There is no retention or purge job.
- So the pointer can dangle only through a direct database insert.

## Finding

**Severity LOW (the maintainer's (by delegation), entry "2026-10-12 02:53:52 BST"; first MEDIUM PROVISIONAL, entry 02:51:17).** The evidence gate is bypassable only by a writer who already has database access. **Re-rate trigger, kept:** if any API caller can set or alter `diagnostics_id`, or a `DiagnosticsRow` can be deleted or purged, this becomes HIGH (an evidence-gate bypass).

## Disposition

**Owner: WK-677** (`docs/roadmap.md`, "Approval policies, escalation, evidence enforcement, attestations"). The remedy is the owner's: a foreign key migration plus an existence check in `_require_evidence`, and the two fixtures corrected to insert a real `DiagnosticsRow`. Event that next confirms or discharges it: a merged slice whose test submits a Model with a dangling `diagnostics_id` and is refused. Filed by the executor, 2026-10-12.
