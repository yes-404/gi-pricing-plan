---
id: RS-1918
family: research
kind: audit
title: SL-1857 (WK-1178) PL-1856 slice C slice audit — the FR-6, FR-109 and FR-110 dated clauses (docs only)
status: draft
created: 2026-10-25   # drafted 2026-10-22 under working id 8189; minted 2026-10-25 as RS-1918
owner: auditor
tree: 8d2ae6f014ea56742785ca46e85e098ba290290c
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1857, LG-1858, PL-1856, FD-1723, FR-6, FR-109, FR-110]
---

# RS-1918 — SL-1857 slice audit (PL-1856 slice C)

*(Working id 8189, written by `aud-8164` (auditor, sonnet, effort medium), 2026-10-22, from `brief-aud-8164-2026-10-22.md` (lead 26). Check 31 on this id is expected until the mint. Slice and ledger are cited by their working ids `SL-8164` and `LG-8165`.)*

## Question

Does `origin/main...sl-8164-wk1178-pl8162-c` meet PL-1856 slice C's acceptance and the maintainer's rulings of 2026-10-22 16:02:49 BST, and is the evidence honest?

## Method

Range `origin/main...sl-8164-wk1178-pl8162-c`: `origin/main` `71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5`; tip `507cfba66edabbfaf9b7dbfff173475835d5226c`, tree `8d2ae6f014ea56742785ca46e85e098ba290290c`; 6 files, +677 (`git diff --stat origin/main...<tip>`). Read with `git show/diff`; docs checks on a detached worktree at the tip, each through `flock -w 900 /tmp/slots/gate-2`. No code, test, DB or gate run. Plan read at the tip (`PL-1856`, 560 lines); rulings read in `to-lead.md` ("2026-10-22 16:02:49 BST", items 1, 3, 6; "2026-10-14 11:28:56 BST"); `FD-1723` row text read at `origin/main`.

## Findings

### Verdict proposal: NOT-CLEAN — 2 blocking items, both wording or record, no maths or code

| # | Blocking item | Fix |
|---|---|---|
| B1 | PL-1856 text still describes slice C as FR-6 + FR-109 only; the diff also changes FR-110 (rulings 1, 3, 6 moved it in). Acceptance item 15 says "one dated clause under FR-6 and one under FR-109 … and no other row changed" and the Tasks table row 1 and Tasks C0–C3 name no FR-110; slice A's Task A2 and item 3 still put `power(k)` under slice A. A fresh reviewer running item 15 sees a third hunk. | Align the plan in place before its first merge (pre-merge edits are allowed; the 226169e2 edit did this for DP-T and A-R3 only): item 15, Tasks row 1, a Task C2b, and A2's "`power(k)` per DP-K". LG-1858 Scope already says it; the plan does not. |
| B2 | FR-6 clause departs from `FD-1723`'s adopted fix and widens the §14 carry beyond what the maintainer named. FD-1723 FR-6 row: "a dated clause narrowing FR-6 to what is built (a per-artifact `produced_by_job_id`), or the shared object is built. The UI half is carried with an owner". The clause does not narrow FR-6; it says FR-6 is "accepted with the gap" and carries to §14 three things: the six shapes without `job_id`, the shared `provenance` object, and the UI. The maintainer's 11:28:56 entry names only "FR-6 UI half" as the §14 owner item. | Lead rules (maintainer if it reads as a scope change): either reword to narrow FR-6 and carry only the UI half, or keep and record the wider carry as ruled. Not for the auditor to pick. |

### 1. Scope from slice C's acceptance, then evidence

| Required | Evidence | Result |
|---|---|---|
| Item 15: one dated clause under FR-6, naming its §14 carry; census verbatim | `00-overview.md` +21 lines, headed "FR-6, dated amendment 2026-10-22 (PL-8162 slice C, FD-1723)"; FR-6 row (`:219`) untouched. Census read: all 10 `job_id: UUID \| None` lines match at `f3462d8f` (`validation.py:548`, `profiles.py:188`, `diagnostics.py:705`, `comparison.py:249`, `backtests.py:117`, `transparency.py:208`, `regression.py:326`, `metrics.py:237`, `objectives.py:832`, `dislocation.py:200`). The 6 gap classes (`datasets.py:333`, `modelling.py:2121`, `objectives.py:476`, `rating.py:1210`, `:1557`, `:165`) have no `job_id`/`produced_by` field in their class bodies; `db/models.py:1696` is `job_id: Mapped[UUID \| None]`. `00` §2 names 7 Artifact kinds; all are covered (Optimisation Run: no shape). `CR-819:128` is the `trace_id` row (`FR-6, 07 R4`) — noted, not edited | delivered; B2 on its wording |
| Item 15: one dated clause under FR-109, §14 carry | `02-modelling.md` +8 lines directly after the FR-109 row; `parent_grouping_id` at `modelling.py:593`; "accepted with reason"; finer-level diagnostics view carried to §14; quote "Owners at §14: … FR-109" matches the 11:28:56 entry (elision marked) | delivered |
| Item 1 of the 16:02:49 entry: `power(k)` STRUCK by dated amendment, never deleted; reason; reinstatement condition; §14 carry | FR-110 row (`:137`) and the older blockquote unedited; clause item 1 supersedes "remains declared and unbuilt", gives the glum 3.4.1 `TweedieLink` reason, supported links `log`, `logit`, `identity`, `inverse`, reinstated only by a library with exact power links, carried to §14 | delivered |
| Item 3 of the 16:02:49 entry + 6: θ in R/MASS `glm.nb` form `μ + μ²/θ`, `θ > 0`, required, never defaulted, one conversion boundary, a round-trip test | clause item 2 says each; "glum α = 1/θ" is consistent with PL-1856 line 472 (`NegativeBinomialDistribution(theta=1/θ)`; glum's own `theta` is the quadratic coefficient) | delivered, wording matches rulings |
| Appended, never editing existing text | `git diff origin/main...<tip> -- docs/specs` has 0 removed lines; 2 hunks in `02`, 1 in `00` | pass |

### 2. spec-change discipline

Ten sections untouched (no heading changed). No requirement renumbered, no id added. No open question raised, so no mirror needed. Legacy-form ids: the clauses use only `FR-6`, `FR-109`, `FR-110`; the 2 check-36 lines at the tip name the `WF-702` workflow file (two legacy-form `FR-MODEL` ids at lines 207 and 208) which arrived from `main` and are not in this slice's hunks. Every cross-reference resolves: `PL-1856`, `FD-1723` (in `docs/INDEX.md` at the tip), `CR-819`, the quoted entries.

Observations, not blocking:
- The FR-6 clause sits after FR-1188, the last row of `00` §3's table, not beside FR-6 (`LG-1858` C1 says "after the table holding FR-6"; the plan says "under FR-6"). It is labelled by id, so a reader of FR-6 does not meet it in place.
- The FR-110 clause is placed after the existing blockquote and directly before the `| **FR-111** |` row with no blank line. The existing text already did this, so FR-111 onward render inside the quote; the new clause does not cause it or repair it.

### 3. Clause content against the wording

Item 1 of the 16:02:49 entry (quote): "STRIKE it from FR-110 by a dated amendment (in slice C), never by deleting text … names what would reinstate it (a library supporting exact power links) and carries the item to the §14 review." Clause item 1: "**Reinstated only by** a library that supports exact power links; the item is **carried to the §14 review**." Match.
Item 3 of the 16:02:49 entry (quote): "FR-110 states θ in the **R/MASS `glm.nb` form**, variance μ + μ²/θ … converts to glum's form at one boundary (glum α = 1/θ_R), and a test pins the round trip." Clause item 2: "variance `μ + μ²/θ`, `θ > 0` … `glum` α = 1/θ at **one boundary** … a round-trip test pins it (slice A)". Match.
Item 6 of the 16:02:49 entry (quote): "θ REQUIRED (declared, never defaulted)". Clause: "**never defaulted**". Match. "A θ on any other family is refused" comes from PL-1856 DP-T (a), not from the ruling; the ruling accepted DP-T. Fine.
Drift: B2 only. The FR-109 and FR-110 clauses carry no drift.

### 4. Orphaned obligations

- θ validator, family translation and the round-trip test: owned by slice A (`PL-1856` A1–A3; `RS-8183` read the code). Not orphaned.
- Strike of `power(k)`: no code names a `power` link (`git grep` of `link.*power` in `packages/model-schema/src`, `packages/pricing-core/src` finds only `family_params["power"]`, the Tweedie index). No code obligation.
- §14 carries (FR-6 six-shape gap, shared `provenance` object and UI; FR-109 finer-level view; `power(k)` reinstatement): verdict deferred, owner "the §14 review". The maintainer named an owner path for "FR-6 UI half" and FR-109 only; the six-shape `job_id` gap and the `provenance` object have no named owner, which is B2's substance. CLAUDE.md §14 allows no unowned state at the review's acceptance; the phase-exit review before 12 Nov must give each an owner. Lead's call whether to file a tracking row now.
- FR-109 "no behaviour may be built on the stored chain" is a prohibition, not an obligation.

### 5. The re-merge `f524df5f`

Parents `abbcb97f` and `71e481fa`. `git merge-tree --write-tree --name-only abbcb97f 71e481fa` rc 1, conflict only `docs/INDEX.md`. Slice-owned content across the merge: `git diff abbcb97f f524df5f` shows 0 changed lines in `00-overview.md`; the 4 changed lines in `02-modelling.md` and 4 in `roadmap.md` are `main`'s (#1359). `git diff 71e481fa f524df5f --stat` is the slice's own 6 files, +676, nothing of `main`'s lost. Matches the LG build log.

### 6. LG-1858

Checks quoted match what I re-ran on the tip: `doc-index.py --check` rc 0 (`OK (byte-stable)`); `register-lint.py` rc 0 (`OK (0 violations)`, residue line); `audit-docs.py` rc 1, `FAILED (2)`, both check 31 (`between 1840 and 8162`, `between 8162 and 8164`). The Gate section lists the full gate as owed and says so; no claim of a pass. `idsweep.sh origin/sl-8164-wk1178-pl8162-c` printed `main: 1840 pairs; duplicate numbers:` and an empty `CROSS-BRANCH` list. Defects: (a) the Audit section reads "(not yet)" — this record is its input; (b) the MERGE-ACK line is empty by design; (c) the LG does not say that acceptance item 15 reads differently from the diff (B1). No false claim found.

## Verdicts on unevidenced requirements

| Item | Verdict |
|---|---|
| FR-6 shared `provenance` object, UI, six shapes without a producing-Job id | deferred, owner the §14 review (B2: owner scope to be ruled) |
| FR-109 finer-level diagnostics view | deferred, owner the §14 review (named by the maintainer, 11:28:56) |
| FR-110 `power(k)` reinstatement | deferred, owner the §14 review (ruling 1) |
| FR-110 θ validator, translation, round-trip test | reassigned to slice A (`SL-8166`, audited in `RS-8183`) |

## Checks run (tree `8d2ae6f0`, detached worktree at `507cfba6`)

`audit-docs.py` rc 1 (FAILED (2), both check 31, expected until mint); `doc-index.py --check` rc 0; `register-lint.py` rc 0. All via `flock -w 900 /tmp/slots/gate-2`. The full gate is not run by this seat.

Adopted 2026-10-25 by the lead (lead 28) for filing, per to-lead 2026-10-25 11:15:40 GMT. The NOT-CLEAN proposal above was resolved before merge: B1 aligned in place (b0b2634d) and B2 = option (a) (d8cc4c75), both on sl-8164-wk1178-pl8162-c and squashed into main as 1fe82ee6 (#1364), per to-lead 2026-10-22 17:57:29 BST; the lead's narrow check found CLEAN, accepted at to-lead 2026-10-22 22:39:50 BST.
