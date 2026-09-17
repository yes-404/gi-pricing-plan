---
id: CR-819
family: closure
kind: work
title: WK-664 — the frontend of Phase 1b: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-27
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-664 — the frontend of Phase 1b: closed 2026-08-27

Evidence pins: close-time origin/main = `ebba7de` (#263). 20 PRs merged (#243–#263)
across three sessions. All squashes verified on main. The auditor's evidence pack is
`W6B-AUDITOR-HANDOVER.md`; the §13 verdicts are the manager's, quoted verbatim in §3–§4.

#### 1. Scope

The WK-664 workstream is Phase 1b's frontend half (roadmap §6 row). The auditor's module
scope-audit at `ebba7de`:

| Module | In scope | Evidenced | Unevidenced |
|---|---|---|---|
| PLAT | 77 | 47 (61%) | 30 |
| DATA | 67 | 61 (91%) | 6 |
| MODEL | 143 | 127 (89%) | 16 |
| OVR | 33 | 10 (30%) | 23 |

`req-coverage.py` at `ebba7de`: 531 specified, 274 marked (51.6%). The script cannot see
the frontend; an unmarked id is not by itself an unevidenced requirement (§13).

WK-664's own scope, carried by the merged slice plans and the focus ids below, is the
frontend workbench: factor workbench, model detail, diagnostics, rule-set versioning,
peril-structure and metric libraries, browser authentication, the workspace selector,
dataset lineage, route reachability, the custom-objective and model workbench surfaces,
and the platform surfaces those slices built. The close derives scope from merged commits
and filed plans, never from the frozen slice-map (backlog #111).

#### 2. Delivery — slices and PRs

| Slice | PR | Squash | Audited | Residue |
|---|---|---|---|---|
| W6b-10 browser auth | #250 | `c56ec75` | verified | none |
| W6b-11 workspace selector | #252 | `fb7e722` | verified | 3 notes (drift counts, anchor-1 reason, 309/309 unverifiable) |
| W6b-12 lineage | #257 | `a551469` | verified | none |
| W6b-15 `_minor` rename | #258 | `1f691de` | verified | none |
| #136 route reachability | #259 | `cde49ad` | verified | none |
| W6b-17+18+19 Group A | #260 | `8b0977f` | verified | RuleResultRow keyed render unasserted |
| W6b-20+21+24 Group B | #261 | `e98d6f6` | verified | 2 tooling notes |
| W6b-22+23 Group C | #262 | `31d8c37` | verified | 2 residue notes (empty corpus, vitest) |
| demo.py auth profile | #263 | `ebba7de` | verified | stale-base proven benign |

Earlier WK-664 slices (W6b-1..9, W6b-13, W6b-14) merged in prior sessions; their delivery
records are in the roadmap §6 slice records.

#### 3. The WK-664 focus ids — DELIVERED (manager verdict, 2026-08-27, corrected)

Eight ids are unevidenced by marker and DELIVERED with named non-marker evidence.
FR-59 was moved out on the manager's correction 1: it is NOT STARTED (§4). The
evidence and the caveats:

| ID | Non-marker evidence | Caveat on the spec row |
|---|---|---|
| FR-393 | frontend OIDC flow (auth/session.ts, oidc.ts); W6b-10 #250; deploy/README:54 | none |
| FR-437 | local identity provider behind opt-in compose profile (#263); deploy/README:41 | none |
| NFR-529 | compose stack to seeded state < 5 min; demo.py `--profile auth`; test_demo_command.py | none |
| FR-57 | `reference_dataset_version_id` read from the Rule Set, never inferred (worker/data_handlers.py) | "Delivered as to the never-inferred half, and untested at the seam" — **carried to WK-665** |
| FR-58 | no override exists in the fit path | "Not started as an enforcement proof" — no broken-input test; **carried to WK-665** |
| FR-23 | W6b-15 rename #258; audit-docs check 12 enforces the name rule | none |
| FR-24 | §5.3 cell contract-is-the-floor; peril-structure views; seven carve-outs | none |
| FR-25 | #259 reachability tests; whitelist proven both directions | none |

FR-57 and FR-58 carry spec-row caveats. The manager's DELIVERED verdict stands;
this record states the caveats so the close is not read as more than it is.

#### 4. Not delivered — verdicts (manager, 2026-08-27, corrected)

| ID | Verdict | Owner / phase |
|---|---|---|
| NFR-488 | DELIVERED-BUT-UNTESTED | carried from WK-692 close; measured 0.0480 fits/pass vs 0.06, marker missing |
| FR-59 | NOT STARTED | spec-only projection, no code; carry-forward, **owned by WK-665** |
| FR-427 | DEFERRED | Phase 2 platform ops; **owned by WK-665** |
| FR-28 | DEFERRED | deferred sub-clause unnamed; **owned by WK-665** |
| FR-108 | DEFERRED | Phase 2 model-document generation; **owned by WK-665** |

**FR-23 is DELIVERED only** (manager correction 2); it has no deferred row here.
The four items missing a named owner/phase are FR-59, FR-427, FR-28 and
FR-108. The decision-maker assigns a phase to each and flags the specific owner for
the manager: FR-59's report-side `unrun_layers` projection, FR-427's secret-audit
remainder, FR-28's unnamed sub-clause (markers exist in test_ingestion.py), and
FR-108's generated-model-document clause (markers exist in test_transformations.py).
**At this close each is carried forward, owned by WK-665** (user direction 2026-08-27).

#### 5. Roadmap-count discrepancy

The roadmap's closure records carry counts that no longer match the derived numbers at
`ebba7de`:

| Record | Stated at close | Derived today |
|---|---|---|
| MODEL closure (WK-661) | 125 in scope, 111 evidenced | 143, 127 |
| `req-coverage.py` (WK-661 close) | 495 specified, 248 marked | 531, 274 |
| DATA closure (WK-660) | 48 of 50, 28/28 endpoints | 61/67, 39/39 endpoints |
| PLAT closure (WK-658) | ~35 of 61 | 47/77 |

The drift is consistent with append-only requirement ids (CLAUDE.md §5). The closure
records are at-close snapshots; a reader cannot tell one from a current count without
re-running the audit. The WK-692 close record names its snapshot tree; earlier records do
not. Recommendation (carried to the §14 review): each closure record names its snapshot
tree, or the records read as stale.

#### 6. §5 retrofit mapping

The roadmap §5 lists eight foundations that must land in Phase 1 because retrofitting
them is a rewrite. Each remains in place at this close, evidenced by its owning
workstream's closure record:

| Foundation | Owning spec | Evidence at close |
|---|---|---|
| Append-only audit log, in the caller's transaction | `06` R2, FR-368 | WK-659 closure; W6b-11 `record_switch` writes both audit chains |
| Artifact immutability + versioning + `parent_id` | FR-4, ID-2 | W32-6/W32-7; artifact_append_only triggers |
| `model-schema` single source of truth | ADR-704 | generate-contracts --check 28/28 |
| The Job model with progress and cancellation | FR-13, FR-399, FR-400, FR-401, FR-402, FR-403, FR-404, FR-405, FR-410, FR-411, FR-412 | jobs API + worker paths |
| Decimal money discipline | FR-10, `03` R2 | W6b-15 rename; W6b-20 currency reads via getDataset |
| `trace_id` propagation API → worker → core | FR-6, `07` R4 | WK-658/WK-659 closure |
| RBAC in the backend from the first endpoint | `06` FR-343 | WK-659 closure; require_identity on W6b-11 |
| Content-addressed blob store | ID-4 | WK-660/WK-692 closure |

This table maps each foundation to its delivered evidence. It does not re-verify the
foundations; the owning workstream's closure record is the evidence.

#### 7. Carry-forward and residue

- FR-194/196 (W6b-6b): delivered but untested. The auditor's read-to-asserts pass
  (§9) documents the tests. Verdict carried as the manager's W6b-6b verdict.
- FR-59 (`unrun_layers`): NOT STARTED, spec-only projection. Carry-forward with an
  owner: the report-side projection is Phase 2 validation-report work; **owned by WK-665 at
  this close** (user direction 2026-08-27). **Handed off 2026-08-27 (WK-665): the successor
  owner is the Phase 2 validation-report workstream; the projection is not built in
  Phase 1b.**
- FR-57 and FR-58: the caveated halves of §3 are carried forward — the
  never-inferred seam test and the fit-gate no-override enforcement proof. **Owned by WK-665.**
  **Delivered 2026-08-27 (WK-665):** `backend/tests/test_reference_pin.py` covers FR-57's
  three reference paths, and `backend/tests/test_api_models.py` carries FR-58's
  HTTP-level no-override proof.
- FR-67 (OQ-566): the exposure-ordered top-20 and the exposure-weighted
  `VR-DST-1` deferral, decided 2026-08-19 and previously unowned by design. **Owned by WK-665
  at this close** (user direction 2026-08-27). **Trigger-checked 2026-08-27 (WK-665): the
  factor workbench proposes exposure-*quantile* bandings but never requests
  exposure-*ordered* levels, and no monitoring view does either — the trigger has not
  fired; the deferral stays unowned.**
- NFR-482: the Model export/import round-trip (FR-5), maintainer verdict out of
  Phase 1 scope (plan review 3, 2026-08-22). **Owned by WK-665 at this close**, which decides
  whether the export/import path is phase work or hands the verdict to Phase 2.
  **Delivered 2026-08-27 (WK-665, OD2): the verdict is reversed** with a dated note in `02`
  §9, and `packages/pricing-core/tests/test_model_round_trip.py` proves the round-trip —
  a GLM exported as JSON and scored in a clean subprocess reproduces the in-process score
  to the last representable digit.
- The validate.py:1079 "minor units" string (auditor finding 6a): an open prose defect.
  It is not governed by FR-23 (a formatted string is not a name); it needs its own
  line item.
- FR-396's fourth obligation (OQ-652): deferred with owner W6b-11; the switch
  mechanism is delivered, the request-path trigger is not.
- #8 listRules client gap: endpoint exists (01:848); no `listRules` client export.
  Owner TBD.
- #103, #87, #127, #131: four close-record items that exist only in frozen plans.
- The vacated W6b-19 sequencing premise; the RuleResultRow keyed render residue;
  the W6b-14 demo.py gap (fixed by #263).
- Balance threshold: begin-close below 10 CNY, no hard stop.

#### 8. Gate summary

Reconciled by the auditor per PR: collect totals balanced at each merge
(1992 → 2022 → 2027 → 2031 → 2028); fail-on-main proofs produced branch-behavior
signatures for every slice; mutation proofs re-opened the intended failures for
Group C and #263; CI path-filtering verified correct (frontend-only PRs skip the python
workflow by design). The full gate's per-command table is the manager's to append, as the
WK-692 record did.

#### 9. Flags for the manager

1. **FR-59** corrected to NOT STARTED (correction 1). Owner assigned as a
   carry-forward to **WK-665** at this close (user direction 2026-08-27).
2. **FR-23** is DELIVERED only (correction 2). The validate.py:1079 "minor units"
   string remains an open auditor finding (finding 6a), recorded in §7, not as an
   FR-23 verdict.
3. **The four not-delivered items** (FR-59, FR-427, FR-28, FR-108) are
   carried forward, **owned by WK-665** at this close (user direction 2026-08-27). FR-67
   and NFR-482 join them in §7. FR-23 is removed from this set.

#### Sources

- W6B-AUDITOR-HANDOVER.md (§9, §14–§22).
- W6B-CLOSE-RECORD-SKELETON-2026-08-26.md.
- W6B-PLAN-REVIEW-5-DRAFT-2026-08-27.md.
- origin/main `ebba7de` (#263); roadmap §5, §6; the WK-692 closure record.
