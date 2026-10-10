---
id: LG-9966
family: ledger
title: WK-1178 slice SL-1526 — exit demo (a): the real freMTPL2 rating algorithm in the seed and the 20,000-policy portfolio sample (PL-1525 + PL-1577 slice ledger)
status: active
created: 2026-10-10
owner: executor
tree: 31b88780aa52894624a5e08454ce2d5925d04b37
phase: P2
work: WK-1178
slice: SL-1526
plans: [PL-1525, PL-1577]
corrected_by: []
relates: [PL-1525, PL-1577, FD-1209, FD-1573, FD-1576]
---

# LG-9966 — WK-1178 slice SL-1526: exit demo (a)

*(LG-9966 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1526` from PL-1525 and its delta PL-1577, base `origin/main`
`31b88780aa52894624a5e08454ce2d5925d04b37`. Times are BST (`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md` "2026-10-10 21:36:36 BST — DISPATCH GO: SL-1526 (exit demo (a)) and SL-1529 (FD-1416); FD-1573 severity; SL-1575 OFF the G2 serial path (corrects my 21:33:57 items 2 and 4)", item 3: "GO SL-1526 (PL-1525 + delta PL-1577), needs 1–4 MET … author now, activate in the slice PR's first commit, merge on its ACK." Condition (item 2): the merge-ack carries PL-1577's proving run, alone in a slot: wall time and peak RSS of the 20,000-policy dislocation and attribution against DP-2's plan target of at most 60 minutes and 15.5 GiB per run; a miss is a stop to the lead (fallback (D)). The algorithm declares no decimal output.
**MERGE-ACK:** added at merge.

## Tasks

### Scope

The slice's row is `#### SL-1526 — WK-1178 exit-demo slice (a) — the real freMTPL2 rating algorithm in the seed` in `docs/roadmap.md`, under PL-1525 and its delta PL-1577. Requirement ids: `03` FR-212, FR-213, FR-226, FR-230, FR-237, FR-240, FR-246, FR-257, FR-260, FR-261; `02` FR-97, FR-101; `07` FR-440; `01` NFR none measured here. Write set: PL-1525 §Write set plus PL-1577 Task 2 (`examples/fremtpl2/{algorithm.py,model.py,seed.py,README.md,test_seed.py}`, `backend/tests/test_demo_rating_evidence.py`, `backend/tests/test_fremtpl2_algorithm.py`, this ledger, `docs/INDEX.md`, the row and plan status lines).

### Task list

- Task 0 — preconditions; premises P1–P8 re-read (Build log).
- Task 1 — the builder and its tests (Acceptance 3, 4, 5, 7).
- Task 2 — bandings, seeded tables, the Rating Version's pins, and the portfolio Dataset Version (Acceptance 1, 2; PL-1577 Task 2).
- Task 3 — golden quotes priced independently of the bundle (Acceptance 3, 6).
- Task 4 — the demo run, the gate, the proving run, the sample-vs-book comparison (Acceptance 7–11; PL-1577 Acceptance 7).

### Gate

(filled at the slice head)

### Audit

(the auditor's)

### Build log

- 2026-10-10 21:4x — Task 0. Base `31b88780`. Premise moved: P6 (`pricing_core/rating/references.py:referenced_names` now exists, SL-1536 `e4753e47`); reported to the lead, ruling awaited.
- Task 1, part 1 — red: `uv run pytest -q backend/tests/test_fremtpl2_algorithm.py` → collection error `FileNotFoundError: …/examples/fremtpl2/algorithm.py`; green after `algorithm.py`: 7 passed (one first-run failure was the test's own expectation of the input set, fixed). Commit `1f789d57`.
- Deviations, both ACCEPTED by the lead (message of 2026-10-10, after the 21:43:24 entry) as implementation choices within PL-1525: (1) rate-table slugs forbid `_` (`packages/model-schema/src/model_schema/refs.py:36`, `_SLUG = r"[a-z0-9][a-z0-9-]{1,62}"`; only the Factor grammar at `:40` admits `_`), so a table slug is `fremtpl2-<factor slug with _ → ->`, not `fremtpl2-<factor slug>`; (2) banded Factor slugs are `driv_age_band`, `veh_age_band`, `veh_power_band`, because a step's produced name may not equal its raw input's name.
- P6 RULED (A), `to-lead.md` "2026-10-10 21:43:24 BST" item B: Acceptance 4 and 7 import `referenced_names` (`packages/pricing-core/src/pricing_core/rating/references.py:38`), with no hand-copied predicate. Independence condition, quoted: "besides the planted-mismatch case (a step reading a name outside its consumes must FAIL the check, shown red), one step's expected reads set is written out literally in the test, so a wrong predicate cannot pass by agreeing with itself." Met by `test_the_reads_check_refuses_an_undeclared_read` (one name dropped from `s_premium.consumes` → exactly `{"s_premium": {"rel_veh_gas"}}`), `test_the_cross_check_refuses_a_planted_mismatch` (both directions, one failure each, naming the name) and `test_a_predicate_that_agrees_with_itself_is_not_the_oracle` (`s_premium`'s eight reads, `s_band_driv_age_band`, `s_t_veh_gas` and `s_base` written out literally). The plan's wording departure ("FD-1374's predicate, not Task 1A's code") is the lead's dispatch delta.
- Task 1, part 2 — Acceptance 4 and 7 (a)(b)(c): 12 passed in `backend/tests/test_fremtpl2_algorithm.py` (small-test slot). One first-run failure: the edge claim was written as equality, but an `output` step only declares `consumes` and evaluates nothing, so it is now "reads add no edge the declaration lacks". Per-step read sets printed by the test (`-s`): e.g. `s_premium ['base_premium_minor', 'rel_area', 'rel_driv_age_band', 'rel_region', 'rel_veh_age_band', 'rel_veh_brand', 'rel_veh_gas', 'rel_veh_power_band']`; the cross-check printed `[]` failures for all 12 evaluated strings; no `as_at` string exists ("predicate only": none). 0 undeclared reads, so 0 added edges and 0 added cycles.

## PRs

(added at the PR)
