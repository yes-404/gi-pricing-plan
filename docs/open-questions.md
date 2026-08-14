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

## DATA — data management ([`01-data-management.md`](specs/01-data-management.md))

| ID | Question | Options / trade-offs | Recommendation | Owner | Status |
|---|---|---|---|---|---|
| **OQ-DATA-1** | Large-loss handling: preparation step or modelling decision? | (a) Bake capping into the dataset — totals reconcile everywhere, one truth, but a new capping assumption means a new Dataset Version and a re-validation. (b) Apply at fit time — one dataset serves many capping assumptions, but the dataset's claim totals no longer match what the model saw, which confuses reconciliation. | (b) at fit time, recorded on the Model as a `LossTreatment` spec, *plus* `VR-ACT-10` flagging outliers in the dataset. Keeps datasets assumption-free; reconciliation is solved by persisting the treatment on the model. | maintainer | open |
| **OQ-DATA-2** | Incremental/append ingestion, or full snapshot per version? | Full snapshot: simple, matches FR-OVR-1 immutability, trivially reproducible — but re-ingesting a 10-year book monthly is wasteful in time and storage. Append: cheap, but "immutable version" becomes "immutable set of parts", and validation must reason about which parts are new. | Full snapshots in Phase 1; add an `append` ingestion mode in Phase 2 that still materialises a complete, content-addressed version (deduplicating unchanged parquet parts via ID-4), so immutability is preserved and only the *cost* changes. | maintainer | open |
| **OQ-DATA-3** | Keep the `sql` custom validation check? If so, what control? | Keep + dual approval: maximum expressiveness, real sandboxing burden (NFR-DATA-9). Keep + admin-only: less flexible but far fewer reviewers to train. Drop: the declarative checks cover ~95 % of real rules; the last 5 % becomes a feature request. | Keep, admin-authored + single Approver, behind a workspace setting that defaults to **off**. Revisit after Phase 1 with evidence of what users actually needed it for. | maintainer | open |
| **OQ-DATA-4** | Where do IBNR / claims-development adjustments live? | Preparation step (developed amounts in the dataset), modelling offset, or out of scope (user supplies developed data). Currently only `VR-ACT-14` warns about immature periods. | Out of scope for Phase 1 (user supplies developed data, we warn), then a first-class `development` preparation step in Phase 4 alongside the monitoring work that needs the same triangles. | maintainer | open |
| **OQ-DATA-5** | Ship ONS/ABI reference data, or only loaders? | Shipping is far better UX but the licences (ONS OGL is permissive; ABI vehicle groups are **not** freely redistributable) differ per source and get us wrong quickly. | Ship loaders + a documented fetch step for every source; ship actual data only where the licence is unambiguously permissive (ONS NSPL, bank holidays). Never ship ABI group tables. | maintainer | open |
| **OQ-DATA-6** | Acknowledgement granularity — per rule per report, or a time-boxed standing acknowledgement? | Per report (FR-DATA-18): strongest evidence trail, but a known seasonal warning is re-justified every month, breeding rubber-stamping. Standing: less fatigue, weaker evidence, risk of a stale acknowledgement hiding a real change. | Keep per-report as the rule, and add a "carry forward justification" affordance that pre-fills the text from the last acknowledgement while still requiring an explicit, separately-audited act. Fatigue is a UI problem, not a governance one. | maintainer | open |
