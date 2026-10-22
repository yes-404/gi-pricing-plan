---
id: LG-8165
family: ledger
title: WK-1178 slice SL-8164 — PL-8162 slice C, the FR-6, FR-109 and FR-110 dated clauses (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-8164
plans: [PL-8162]
corrected_by: []
relates: [PL-8162, SL-8164, FD-1723, FR-6, FR-109, FR-110]
---

# LG-8165 — WK-1178 slice SL-8164: PL-8162 slice C, the FR-6, FR-109 and FR-110 dated clauses

**GO:** the maintainer's entry "2026-10-22 16:02:49 BST — Maintainer: PL 8162 (FD-1723's residual limbs) ACCEPTED; power(k), θ convention, NB deviance, DP-C, DP-F14, DP-T, DP-M ruled" (`to-lead.md`): "**GO: slice C now** (docs only, under pre-approval 1(d))."
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

`PL-8162`, slice row "**C** — FR-6 and FR-109 dated clauses (docs only)", Tasks C0 to C2 (C3 here), plus the FR-110 clause the ruling moved into slice C ("It goes in a dated FR-110 clause in slice C", ruling 3; `power(k)` strike, ruling 1; θ required, ruling 6). Requirements: `00` FR-6; `02` FR-109, FR-110. Docs only; no code, no test. Same-Work pair: none (slice A touches `02`'s other rows later; a mechanical re-merge at most).

### Task list

- **C0 census** (read-only): the FR-6 clause quotes it, with `file:line` at `f3462d8f`. Carry `job_id`: ValidationReport, Profile, Diagnostics, ModelComparison, Backtest, TransparencyArtifact, RegressionRun, MetricCertificate, ObjectiveCertificate, DislocationRun. Carry none: DatasetVersion, Model (its `models` row has the column, `db/models.py:1696`), CustomObjective, RateTable, RateTableVersion, RatingVersion; Optimisation Run has no shape. Predicate: each class read in its owning module and each `*Row` in `db/models.py` (`awk` mapping `job_id: Mapped` to its class), not a grep for `job_id` alone.
- **C1** FR-6 dated amendment in `00-overview.md` (after the table holding FR-6): built / not built / §14 carry.
- **C2** FR-109 dated amendment in `02-modelling.md` (after its row): accepted with reason, §14 carry.
- **C2b** FR-110 dated amendment in `02-modelling.md` (after the `inverse` note): `power(k)` struck, never deleted, with its reinstatement condition and the §14 carry; θ in the R/MASS `glm.nb` form, required, converted at one boundary.
- **C3** activation: `PL-8162` `draft` to `active` (L1); the `SL-8164` row under WK-1178; this ledger; `audit-docs.py` and the INDEX under the gate-2 flock after the ALONE window ends.

### Gate

Docs-only gate (maintainer-approved, pre-approval 1(e), to-lead "2026-10-22 17:50:51 BST"), run by `scratch/sl-8164/gate-docs.sh` on head `507cfba66edabbfaf9b7dbfff173475835d5226c` (tree `8d2ae6f014ea56742785ca46e85e098ba290290c`); logs in `scratch/sl-8164/gate/`. `git diff --name-only origin/main...HEAD` lists six paths, all under `docs/` (INDEX, this LG, PL-8162, roadmap, 00-overview, 02-modelling). The dated clauses name no test file or function (grep of the `docs/specs` diff: none; the θ round trip is slice A's).

| Check | rc | Summary |
|---|---|---|
| `audit-docs.py` | 1 | `FAILED (2)`: `check 31: gap in the full allocation between 1840 and 8162`, `between 8162 and 8164` (unminted working ids) |
| `doc-index.py --check` | 0 | `OK (byte-stable)` |
| `register-lint.py` | 0 | `OK (0 violations)` |
| `req-coverage.py` | 0 | rc 0 |
| `generate-contracts.py --check` | 0 | rc 0 |
| pytest run 1 (`test_audit_docs_finding_citations`, `_ids`, `_process_core_digest`) | 1 | `5 failed, 119 passed in 234.79s` |
| pytest run 2 (`test_audit_docs_w37_11_ceiling`, `test_doc_index`, `test_register_lint`) | 1 | `5 failed, 105 passed in 96.44s` |
| pytest run 3 (`test_register_owed`, `test_repository_invariants`) | 1 | `3 failed, 20 passed in 76.83s` |

The 13 pytest failures all run the real tree: 11 assert `audit-docs.py` rc 0 (got 1) and 2 assert allocation contiguity (`[(1840, 8162), (8162, 8164)]`, `doc-id.py … gap between 1840 and 8162`). Every one traces to the same check 31 gap above, which the mint closes. Classification: expected until minted, NOT proven; the minted-head re-run must show all three runs green.

### Audit

(not yet)

### Build log

- 2026-10-22 — branch `sl-8164-wk1178-pl8162-c` from `origin/main` @ `f3462d8f`; plan brought from `draft/pl-8162` @ `6b1de3a9`; clauses, roadmap row and this ledger written.
- 2026-10-22 — re-merged `origin/main` @ `71e481fa` (merge commit `f524df5f`; `git merge-tree --write-tree` rc 1, only `docs/INDEX.md` conflicted, taken from main and regenerated). On `f524df5f` under the gate-2 flock: `doc-index.py --check` rc 0 (`OK (byte-stable)`); `register-lint.py` rc 0 (`OK (0 violations)`); `audit-docs.py` rc 1, `FAILED (2)`, both check 31 (`gap in the full allocation between 1840 and 8162`, `between 8162 and 8164`), the unminted working ids. Full gate owed, queued after FD-1838.
- 2026-10-22 — RS 8189 B2 (the maintainer's entry "2026-10-22 17:57:29 BST", option (a)): the FR-6 dated clause in `00-overview.md` is reworded in place (unmerged). It now narrows FR-6 to the per-artifact producing-Job id (ten shapes, census kept), carries only the UI half to §14, and adds one transparency sentence (not a carry) naming `DatasetVersion`, `Model`, `CustomObjective`, `RateTable`, `RateTableVersion`, `RatingVersion` and the shared `provenance` object as outside the narrowed FR-6; the "accepted with the gap" wording and the §14 carry of the gap and of the shared object are removed. The `### Gate` table above ran on `507cfba6` and is SUPERSEDED: the docs-only gate re-runs once after the planner's PL 8162 commit (B1) lands, on the lead's "GATE GO <sha>".

## PRs

(none yet)
