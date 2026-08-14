# Open Questions

Unresolved design questions. Every question is mirrored from the §10 "Open questions"
section of the spec that raised it. **Phase 0 exit requires this file to be empty or
every remaining entry explicitly marked `deferred` with a target phase.**

**Status values:** `open` · `decided` (link the ADR) · `deferred` (state the phase) ·
`dropped` (state why).

**How to close one:** if the decision constrains more than one module or is expensive to
reverse, write an ADR and set status `decided → ADR-NNNN`. Otherwise record the decision
inline in the owning spec and set status `decided (in spec)`. Never delete a row.

---

## OVR — system level

| ID | Question | Options / trade-offs | Recommendation | Owner | Status |
|---|---|---|---|---|---|
| **OQ-OVR-1** | Is `workspace` the tenancy boundary, or is physical isolation needed for hosted multi-tenant use? | (a) Logical only — one schema, `workspace_id` on every row: simple, cheap, but a query bug leaks another insurer's rates. (b) Schema-per-tenant: strong isolation, migration complexity ×N. (c) Deployment-per-tenant: total isolation, highest ops cost. | (c) for hosted commercial use, (a) for self-hosted single-insurer use — which is the only supported mode in Phases 0–4. Keep `workspace_id` everywhere (FR-OVR-13) so (b) stays reachable. | maintainer | open |
| **OQ-OVR-2** | Project licence. | Apache-2.0: maximum adoption, permits closed SaaS forks. AGPL-3.0: protects against a hosted closed fork, deters some corporate users and blocks linking from proprietary in-house code — a real concern for insurers who will embed `pricing-core`. MPL-2.0: file-level copyleft, middle ground. | Apache-2.0. Insurers embedding `pricing-core` in internal systems is the adoption path; AGPL would block exactly the users we want. | maintainer | open |
| **OQ-OVR-3** | Multi-currency support in one workspace — Phase 2 or Phase 4? | Now: every money field needs a currency and FX effective-dating, which touches every rate table and trace. Later: a migration of all monetary columns, but no cost until then. | Defer to Phase 4; enforce a single workspace-level `currency` code now and store it on every artifact so the later migration is additive. | maintainer | open |
| **OQ-OVR-4** | Publish `pricing-core` to PyPI from Phase 1? | Publishing forces semver stability on an API we are still discovering; not publishing weakens the "verify it in a notebook" story that ADR-0001 exists for. | Publish from Phase 2 as `0.x` with an explicit no-stability-guarantee notice; ship a `pip install -e` path in Phase 1. | maintainer | open |
| **OQ-OVR-5** | Notebook escape hatch: embedded JupyterLab or client library only? | Embedded: best UX, but arbitrary code execution inside the platform's security and audit boundary. Client library: users bring their own Jupyter, credentials leave the platform, no audit of what they ran. | Client library (`gi-pricing-client`) in Phase 1 with read-scoped API tokens; revisit embedded notebooks in Phase 4 once sandboxing exists for custom objectives (which needs the same machinery). | maintainer | open |
