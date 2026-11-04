---
id: LG-1858
family: ledger
title: WK-1178 slice SL-1857 — PL-1856 slice C, the FR-6, FR-109 and FR-110 dated clauses (slice ledger)
status: closed                 # active → closed (§1.2a) — closed at the mint, 2026-10-22
created: 2026-10-22   # filed under working id 8165; minted 2026-10-22 as LG-1858
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-1857
plans: [PL-1856]
corrected_by: []
relates: [PL-1856, SL-1857, FD-1723, FR-6, FR-109, FR-110]
---

# LG-1858 — WK-1178 slice SL-1857: PL-1856 slice C, the FR-6, FR-109 and FR-110 dated clauses

Disclosure: drafted under working id 8165; minted as LG-1858 on 2026-10-22, in slice C's PR (SL-1857).

**GO:** the maintainer's entry "2026-10-22 16:02:49 BST — Maintainer: PL 8162 (FD-1723's residual limbs) ACCEPTED; power(k), θ convention, NB deviance, DP-C, DP-F14, DP-T, DP-M ruled" (`to-lead.md`): "**GO: slice C now** (docs only, under pre-approval 1(d))."
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

`PL-1856`, slice row "**C** — FR-6 and FR-109 dated clauses (docs only)", Tasks C0 to C2 (C3 here), plus the FR-110 clause the ruling moved into slice C ("It goes in a dated FR-110 clause in slice C", ruling 3; `power(k)` strike, ruling 1; θ required, ruling 6). Requirements: `00` FR-6; `02` FR-109, FR-110. Docs only; no code, no test. Same-Work pair: none (slice A touches `02`'s other rows later; a mechanical re-merge at most).

### Task list

- **C0 census** (read-only): the FR-6 clause quotes it, with `file:line` at `f3462d8f`. Carry `job_id`: ValidationReport, Profile, Diagnostics, ModelComparison, Backtest, TransparencyArtifact, RegressionRun, MetricCertificate, ObjectiveCertificate, DislocationRun. Carry none: DatasetVersion, Model (its `models` row has the column, `db/models.py:1696`), CustomObjective, RateTable, RateTableVersion, RatingVersion; Optimisation Run has no shape. Predicate: each class read in its owning module and each `*Row` in `db/models.py` (`awk` mapping `job_id: Mapped` to its class), not a grep for `job_id` alone.
- **C1** FR-6 dated amendment in `00-overview.md` (after the table holding FR-6): built / not built / §14 carry.
- **C2** FR-109 dated amendment in `02-modelling.md` (after its row): accepted with reason, §14 carry.
- **C2b** FR-110 dated amendment in `02-modelling.md` (after the `inverse` note): `power(k)` struck, never deleted, with its reinstatement condition and the §14 carry; θ in the R/MASS `glm.nb` form, required, converted at one boundary.
- **C3** activation: `PL-1856` `draft` to `active` (L1); the `SL-1857` row under WK-1178; this ledger; `audit-docs.py` and the INDEX under the gate-2 flock after the ALONE window ends.

### Gate

**Run 1 (pre-fix, SUPERSEDED by run 2 below).** Docs-only gate (maintainer-approved, pre-approval 1(e), to-lead "2026-10-22 17:50:51 BST"), run by `scratch/sl-8164/gate-docs.sh` on head `507cfba66edabbfaf9b7dbfff173475835d5226c` (tree `8d2ae6f014ea56742785ca46e85e098ba290290c`); logs in `scratch/sl-8164/gate/`. `git diff --name-only origin/main...HEAD` lists six paths, all under `docs/` (INDEX, this LG, PL-1856, roadmap, 00-overview, 02-modelling). The dated clauses name no test file or function (grep of the `docs/specs` diff: none; the θ round trip is slice A's).

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

**Run 2 (current; supersedes run 1).** Same script, run once on head `b0b2634d6346aa9534c9fe256492f97ca4d1eb3c` (tree `91cd33adf43fef9204c66d9e9c60b0601837a314`; lead's "GATE GO b0b2634d", after the RS 8189 B2 FR-6 reword `d8cc4c75` and the planner's B1 alignment); logs in `scratch/sl-8164/gate/` (run 1's moved to `gate/run1/`), each starting with that sha. `git diff --name-only origin/main...HEAD` lists the same six `docs/` paths as run 1.

| Check | rc | Summary |
|---|---|---|
| `audit-docs.py` | 1 | `FAILED (2)`: `check 31: gap in the full allocation between 1840 and 8162`, `between 8162 and 8164` |
| `doc-index.py --check` | 0 | rc 0 |
| `register-lint.py` | 0 | rc 0 |
| `req-coverage.py` | 0 | rc 0 |
| `generate-contracts.py --check` | 0 | rc 0 |
| pytest run 1 (`test_audit_docs_finding_citations`, `_ids`, `_process_core_digest`) | 1 | `5 failed, 119 passed in 208.93s (0:03:28)` |
| pytest run 2 (`test_audit_docs_w37_11_ceiling`, `test_doc_index`, `test_register_lint`) | 1 | `5 failed, 105 passed in 118.37s (0:01:58)` |
| pytest run 3 (`test_register_owed`, `test_repository_invariants`) | 1 | `3 failed, 20 passed in 79.72s (0:01:19)` |

FAILED lines (identical test ids to run 1): `test_audit_docs_finding_citations::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`; `test_audit_docs_ids::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`; `test_audit_docs_process_core_digest::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `::test_the_committed_digest_currently_matches_the_committed_spec`; `test_audit_docs_w37_11_ceiling::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`; `test_doc_index::test_an_index_skipping_a_reserved_block_breaks_contiguity`; `test_register_lint::test_check_29_is_wired_into_the_docs_gate`, `::test_check_29_note_carries_the_residue_line`, `::test_phase1b_residue_count_matches_check_29s_own_count`; `test_register_owed::test_check_29_wiring_is_undisturbed`; `test_repository_invariants::test_money_discipline_is_enforced_by_the_docs_audit`, `::test_journey_citations_are_audited_in_ci`. I read the assert text in each log: each failure shows either `assert 1 == 0` on an `audit-docs.py` run whose output ends in the two check 31 rows, or the allocation-contiguity assert (`[(1840, 8162), (8162, 8164)]`, `doc-id.py … gap between 1840 and 8162`). No other assert text appears. Per test (a per-test awk over the three logs): 12 tests show one `assert 1 == 0` on an audit-docs run, `test_doc_id_check_exits_0_on_the_real_tree` also shows the contiguity assert (`doc-id.py … gap between 1840 and 8162`), and `test_doc_index::test_an_index_skipping_a_reserved_block_breaks_contiguity` shows only the contiguity assert (`[(1840, 8162), (8162, 8164)]`): 12 + 1 = 13. The 11 + 2 split above in the earlier count of this section is a miscount; the line is a count of text lines, not of tests. This is the standing 1(f)/1(e) shape (docs-audit set only; audit-docs failing only check 31 on this slice's own working ids). The minted-head re-run must show all three runs green.

### Gate (minted head)

Minted at `28bfb0a64b81783e399e3b84f9c469d22791893c` (tree `478035bc1255e0fd1d8a2ffe5a1dd3d8f49710f2`), the merge of `origin/main` @ `6753c495` being `8180fab9`. On that head: `audit-docs.py` rc 0 (`All checks passed.`), `doc-index.py --check` rc 0 (`OK (byte-stable)`). The 13 tests that failed on the working-id gap, re-run through `scripts/run-small.sh` on the minted head (logs `scratch/sl-8164/gate/minted/small-{1,2,3}.log`, each starting with the head sha), summaries verbatim:

| run | files | summary | rc |
|---|---|---|---|
| small-1 | `test_audit_docs_finding_citations`, `test_audit_docs_ids`, `test_audit_docs_process_core_digest` | `124 passed in 189.81s (0:03:09)` | 0 |
| small-2 | `test_audit_docs_w37_11_ceiling`, `test_doc_index`, `test_register_lint` | `110 passed in 91.93s (0:01:31)` | 0 |
| small-3 | `test_register_owed`, `test_repository_invariants` | `23 passed in 71.21s (0:01:11)` | 0 |

### Audit

Written 2026-10-22 by the auditor (aud-c3) after the fixes below; the verdicts are the lead's.

**Audit record:** RS 8189 (working id; branch `aud-8164-2026-10-22` @ `d339555808f4b8f9fa8c3df909d285595d2562ed`, `status: draft`), range `origin/main...sl-8164-wk1178-pl8162-c`, tip `507cfba66edabbfaf9b7dbfff173475835d5226c` (tree `8d2ae6f014ea56742785ca46e85e098ba290290c`). **Verdict proposed: NOT-CLEAN, two blocking items (B1, B2), both wording or record, no maths and no code.**

| Blocker | Ruling (authority) | Met by | Evidence read |
|---|---|---|---|
| B1: the plan text described slice C as FR-6 + FR-109 only, the diff also carried FR-110 (rulings 1, 3, 6 of "2026-10-22 16:02:49 BST") | aligned in place, as the plan was unmerged: the maintainer's entry "2026-10-22 17:57:29 BST" in `to-lead.md` ("Maintainer: slice C RS 8189: B1 (plan drift) aligned in place; B2 FR-6 = option (a) …") | `b0b2634d` (planner; the plan's dated alignment note lists each changed line, `git show` read: front-matter title gains FR-110, and the INDEX row regenerated) | `git show b0b2634d`: 2 paths, `docs/INDEX.md` and the plan, 3 insertions, 3 deletions |
| B2: the FR-6 clause departed from FD-1723's adopted fix and widened the §14 carry | same entry, **option (a)**: FR-6 narrowed to what is built (the per-artifact producing-Job id); only the UI half carried to §14, as on 2026-10-14 11:28:56; the six shapes without a `job_id` and the shared `provenance` object named as outside the narrowed FR-6, no carry and no tracking row | `d8cc4c75` (FR-6 dated clause, `00-overview.md`) | `git show d8cc4c75`: 2 paths (`00-overview.md`, this ledger), the clause now reads "FR-6 is **narrowed to what is built: the per-artifact producing-Job id**", names `DatasetVersion`, `Model`, `CustomObjective`, `RateTable`, `RateTableVersion`, `RatingVersion` and the `provenance` object as "**outside the narrowed FR-6**"; "accepted with the gap" is gone |

**Narrow check:** the lead's entry "2026-10-22 18:09:13 BST" in `channel/from-lead-2026-10-09.md` ("SLICE C narrow check of RS 8189 B1/B2 at b0b2634d (lead, per maintainer 17:57:29) … PASS", diff 6 paths all `docs/`). I re-read the two commits above against the blockers and agree with that entry.

**Docs-only gate (pre-approval 1(e), as the Gate section cites):** run 2 at `b0b2634d`, logs under `scratch/sl-8164/gate/` each starting with that sha: `doc-index.py --check`, `register-lint.py`, `req-coverage.py`, `generate-contracts.py --check` rc 0; `audit-docs.py` rc 1 (check 31, the unminted working ids only); the three pytest runs rc 1 (13 failures, the docs-audit set; see the Gate section).

**Mint evidence at `28bfb0a6`** (tree `478035bc1255e0fd1d8a2ffe5a1dd3d8f49710f2`): `audit-docs.py` rc 0; `doc-index.py --check` rc 0; the 13 failing tests re-run green through `run-small.sh`: `124 passed`, `110 passed`, `23 passed` (logs `scratch/sl-8164/gate/minted/small-{1,2,3}.log`, read: each starts with `28bfb0a6`, ends `rc=0`). The failures were the check 31 gap; the mint closed it.

**Post-audit delta `b0b2634d..a9761e31`** (reachable: `b0b2634d` is an ancestor of `a9761e31`), the slice's own commits are two ledger commits (`af7bbd61`, `4b1b5da9`), the merge `8180fab9` of `origin/main` @ `6753c495` (it brings #1361, #1362 and #1363: the code and the other docs in `git diff --stat b0b2634d..a9761e31` are main's), the mint `28bfb0a6`, and two LG-only commits (`1ae3503d`, `a9761e31`). The slice's own contribution is docs only: `git diff --name-only 8180fab9^2 a9761e31` (the branch against main's side of the merge) lists no path outside `docs/`. The mint touched 6 docs paths and, in `00-overview.md`, `02-modelling.md` and the roadmap, changed only working ids to minted ids (working ids 8162 and 8164 to `PL-1856` and `SL-1857`; read in `git diff 8180fab9 28bfb0a6`); the two LG commits change only this ledger. **No clause text changed after the narrow check.**

**Requirements (four verdicts):** FR-6, FR-109 and FR-110 dated clauses delivered as docs (no test applies; the clauses name none, and the θ round trip is slice A's). FR-6 UI half, FR-109 finer-level view, `power(k)` reinstatement: deferred to the §14 review, the owners the maintainer named. The six-shape `job_id` gap and the `provenance` object: not carried and not tracked, by ruling (B2 (a)).

**Proposed verdict: CLEAN after B1 and B2**, the lead's to issue.

### Build log

- 2026-10-22 — branch `sl-8164-wk1178-pl8162-c` from `origin/main` @ `f3462d8f`; plan brought from `draft/pl-8162` @ `6b1de3a9`; clauses, roadmap row and this ledger written.
- 2026-10-22 — re-merged `origin/main` @ `71e481fa` (merge commit `f524df5f`; `git merge-tree --write-tree` rc 1, only `docs/INDEX.md` conflicted, taken from main and regenerated). On `f524df5f` under the gate-2 flock: `doc-index.py --check` rc 0 (`OK (byte-stable)`); `register-lint.py` rc 0 (`OK (0 violations)`); `audit-docs.py` rc 1, `FAILED (2)`, both check 31 (`gap in the full allocation between 1840 and 8162`, `between 8162 and 8164`), the unminted working ids. Full gate owed, queued after FD-1838.
- 2026-10-22 — RS 8189 B2 (the maintainer's entry "2026-10-22 17:57:29 BST", option (a)): the FR-6 dated clause in `00-overview.md` is reworded in place (unmerged). It now narrows FR-6 to the per-artifact producing-Job id (ten shapes, census kept), carries only the UI half to §14, and adds one transparency sentence (not a carry) naming `DatasetVersion`, `Model`, `CustomObjective`, `RateTable`, `RateTableVersion`, `RatingVersion` and the shared `provenance` object as outside the narrowed FR-6; the "accepted with the gap" wording and the §14 carry of the gap and of the shared object are removed. The `### Gate` table above ran on `507cfba6` and is SUPERSEDED: the docs-only gate re-runs once after the planner's PL-1856 commit (B1) lands, on the lead's "GATE GO <sha>".
- 2026-10-22 — exec-c3: re-merged `origin/main` @ `6753c495` (merge-tree rc 1: `docs/INDEX.md` taken from main and regenerated; `docs/roadmap.md` kept both SL rows, main's SL-1854 first; merge `8180fab9`); minted PL 8162 → PL-1856, SL 8164 → SL-1857, LG 8165 → LG-1858 in its own commit `28bfb0a6` (whole-tree grep of the space, hyphen and zero-padded forms: 28 hits before; after, the quoted channel header of the GO entry, in the roadmap row, the plan and this ledger, which keeps its working id (this note names the old ids too); scratch paths and the branch name are real names, not ids; idsweep clean); LG and SL set `closed` at the mint; the 13 docs-audit tests green on the minted head (see Gate).

## PRs

(none yet)
