# The retrofit-impossible list

> Moved from `docs/roadmap.md` §5 by the roadmap slim (NT-0009, accepted 2026-08-27).
> These are invariants the plan was shaped around; they are preserved, not scheduled.

## 5. What cannot be retrofitted

**This is the most important section of this document.** Several capabilities belong to
later phases by ownership but must be built into Phase 1's foundations, because
retrofitting them is a rewrite rather than an addition.

| Must land in Phase 1 | Owning spec | Why retrofitting fails |
|---|---|---|
| **Append-only audit log, written in the caller's transaction** | `06` R2, FR-GOV-20 | Every write path must call it. Adding audit later means revisiting every mutation in the codebase and still having no history for anything already done. |
| **Artifact immutability + versioning + `parent_id`** | FR-OVR-1, ID-2 | If entities are mutable in v1, every artifact table needs a data migration and the historical record is simply gone. |
| **`model-schema` as the single source of truth** | ADR-0002 | Generated OpenAPI and TS types are trivial from day one and a large refactor once shapes exist in three places. |
| **The Job model with progress and cancellation** | FR-OVR-10, FR-PLAT-7..16 | Synchronous endpoints that later become jobs change every caller, including the frontend's whole interaction model. |
| **Decimal money discipline** | FR-OVR-7, `03` R2 | Retrofitting is a data migration *plus* a correctness audit of every computed figure ever displayed. |
| **`trace_id` propagation API → worker → core** | FR-OVR-3, `07` R4 | Cheap to thread through from the start; invasive afterwards. |
| **RBAC checks in the backend from the first endpoint** | `06` FR-GOV-2 | "We'll add auth later" reliably produces endpoints that assume no caller identity. |
| **Content-addressed blob store** | ID-4 | Changing storage layout later invalidates every stored reference. |

None of these require the *full* module. Phase 1 needs the audit **write path**, not the
audit explorer UI; the approval **state machine**, not the inbox. The user-facing surface
is Phase 3's job.

---

