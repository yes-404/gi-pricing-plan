---
id: LG-9904
family: ledger
title: WK-675 slice SL-1547 — S5, Editor II: diff shading, bulk operations, CSV import and export; RL-1613's ordered input (PL-1546, PL-1668), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 3b2081b7333bded7e998104f042586d50e8bf3e3
phase: P2
work: WK-675
slice: SL-1547
plans: [PL-1546, PL-1668]
corrected_by: []
relates: [PL-1546, PL-1668, PL-1286, SL-1547, SL-1669, SL-1548, RL-1613, OQ-1223, FD-1366, FR-213, FR-230, FR-231, FR-232, FR-233, FR-235, FR-261, FR-25, NFR-463]
---

# LG-9904 — WK-675 slice SL-1547: S5, Editor II

*(Working id 9904, reserved by the lead. The id is minted at the merge turn; until then every citation of this record is by working id.)*

**GO:** the lead's from-lead entry "2026-10-12 06:54:14 BST — GO S5 SL-1547 (WK-675, lane C) → executor-sl1547; ledger working id LG 9904; base origin/main 3b2081b7333bded7e998104f042586d50e8bf3e3" in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`. It quotes `RL-1613` "What it obliges" items 2–3 and `PL-1668` R5.3–R5.9 verbatim (PL-1668 need 7). Authority, each by author: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-11 10:39:56 BST" items 1–3 (lane C order; a backend WK-675 seat may run beside S5 under `RL-1445` item 2), "2026-10-12 02:53:52 BST" item 1 (the S5/S6 drift rule), "2026-10-12 05:35:05 BST" (the quote-form re-merge rule), "2026-10-12 05:27:16 BST" (fallback (a): S5 waits for `SL-1669`; discharged), "2026-10-12 06:51:02 BST" (#1293 ACK: S5's GO rests on `PL-1668`'s needs plus the re-merge rule).
**MERGE-ACK:** not yet given.

## Tasks

Base: `origin/main` `3b2081b7333bded7e998104f042586d50e8bf3e3`. The activation commit is the branch's first. Branch `sl-1547-wk675-s5`, worktree `.claude/worktrees/sl-1547`.

### Scope

Quoted from `PL-1546`'s order table, row 1: "SL-1547 — S5: Editor II: diff shading, bulk, import, export | `PL-1286` S5 row, plus R5.1–R5.3 | `03` §3.3: FR-230, FR-231, FR-232, FR-233, FR-235; `00`: FR-25; NFR-463; register F-W10-1, F-W10-2 (view limb)". Amended by `PL-1668` (a dated Work-plan delta, the later statement): R5.3 (bulk-operation typing discharged by `SL-1669`, #1293; S5 types nothing and edits no bulk-operation handler), R5.4 (`RL-1613`'s contract-changing scope), R5.5 (`InputFreeError`), R5.6 (the authored `rating-algorithm.schema.json` is hand-edited), R5.7 (omission of `ordered: false` in every hashed dump), R5.8 (the S5/S6 drift rule), R5.9 (the overlap table), and its Acceptance additions 1–8. `PL-1286` S5 row: "Diff-vs-previous and diff-vs-seed shading (FR-230, FR-231), handling the diff route's 202 with a Job when either version is `storage: parquet` (FR-232, `03:749`): the view polls the Job and renders the same artifact; the exposure-weight column (F-W10-2); bulk-operation dialog (FR-233); CSV import confirmation and export (FR-235); DP-3's order; F-W10-1".

**Locator drift recorded (readiness, accepted by the lead):** the `not orderable` refusal is at `packages/pricing-core/src/pricing_core/rating/properties.py:146`, not `properties.py:144-147` as `PL-1668` R5.4 says.

### Task list

(entries follow; the order below is the intended one)

- **T1 — Spec first.** `03` FR-213 dated clarification (`ordered`); FR-261 dated amendment, including how the run labels the level grid and how `lower`/`upper` apply to levels (`RL-1613:90-92`). Shown in full here at the first spec commit.
- **T2 — `model-schema`.** `ordered: bool = False` on `InputContractField`; validator raising `InputFreeError`; omission of `false` once on the field's serialisation (R5.7); hand edit of `rating-algorithm.schema.json` (R5.6). Hash tests red first (Acceptance 1–3).
- **T3 — `pricing-core`.** `properties.py` admits an ordered enum and sweeps its levels in declared order (Acceptance 4–5).
- **T4 — Contracts and client.** `scripts/generate-contracts.py` then `--check`; `pnpm --dir frontend generate:api` (Acceptance 6).
- **T5 — Display.** Ordered input's levels in declared order, display only, from the generated type. Display site named at the first red.
- **T6 — Editor II views.** Diff shading and the exposure-weight column through the paged cells route; the diff 202 with a Job (FR-230, FR-231, FR-232).
- **T7 — Bulk-operation dialog** (FR-233) with the generated `BulkOperationRequest` and `RateTableVersion`; no handler edit (Acceptance 7).
- **T8 — CSV import confirmation and export** (FR-235).

### Gate

Not yet run.

### Audit

Not yet written.

### Build log

- 2026-10-12: activation commit. `SL-1547` draft→active, `PL-1668` draft→active (status line only).

## PRs

(none yet)
