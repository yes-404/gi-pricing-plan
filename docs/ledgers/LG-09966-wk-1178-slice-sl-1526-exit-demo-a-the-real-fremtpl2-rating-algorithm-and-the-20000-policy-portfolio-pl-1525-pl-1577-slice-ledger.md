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
- Task 2 (PL-1577 part), red: `uv run pytest -q examples/fremtpl2/test_seed.py` → `ImportError: cannot import name 'PORTFOLIO_ROWS' from 'seed'`; then green after the constant, with one expectation of my own corrected (`ids[-1] == "39999"`: `step = height // rows` = 2 over 50 001 rows, and `head(rows)` of that stride ends at policy 39 999, so the sample never reaches the last 10 002 rows: 8 passed, 1 skipped).
- **Sample vs book (PL-1577 Acceptance 7; measured 2026-10-10 with a one-off polars script over the sha256-pinned book, `build_csv(None)` vs `build_csv(20000)`, `exposure_years <= 1.05`):** the sampler is deterministic (two calls, same `IDpol` list: True). Raw rows 678 013 book / 20 000 sample; after the v2 recipe 677 442 / **19 979** (so `PORTFOLIO_VALIDATED_ROWS = 19_979`, 21 policies dropped; to be confirmed by the seed's own profile row count at the proving run). Exposure mean 0.5282 book / 0.5332 sample. Claim frequency (claims / exposure) **0.1008 book / 0.1060 sample (+5.2 %)**; claims per policy 0.0532 / 0.0565. Region share, max absolute difference over 22 regions 0.75 pp (R24 0.2370 / 0.2446; R11 0.1029 / 0.0980). Vehicle-age bands 0-2 / 3-9 / 10+: book 27.7 % / 39.2 % / 33.1 %, sample 26.1 % / 39.4 % / 34.5 % (max difference 1.7 pp). Cause check: `step` is 33 on the real file, so the sample ends at row 660 000 of 678 013; the head 660 000 rows have frequency 0.1014 and the tail 18 013 rows 0.0613 (the book 0.1007), so the truncation explains about 0.0007 of the 0.0052 gap and the rest reads as sampling noise (about 1 130 claims in the sample, standard error about 3 %). **Reported to the lead before the demo text is final**, as the 00:34:03 entry requires if any column differs materially; the frequency is the one that does.
- Task 2 (examples/), code: `model.py` (banded Factors `driv_age_band`/`veh_age_band`/`veh_power_band` on 5 quantile Bandings proposed by `transform_service.propose_banding_for_version`; `create_demo_bandings`, `seed_demo_rate_tables`, `demo_base_premium`, `demo_golden_cases`, `monotone_property`, the real `author_demo_rating_evidence` and `create_approved_rating_version`); `seed.py` (the portfolio sample as its own Dataset Version, ingested through the v2 recipe, validated and promoted, its id and row count written into `last-seed.json`, the exact count asserted); `algorithm.py` (`glm_premium_minor`). Offline preview of the Bandings the proposal gives on the full cleaned book (pure `propose_banding`, quantile, 5 bands): `driv_age` (18, 32, 40, 48, 57, 100) labels 18-31 / 32-39 / 40-47 / 48-56 / 57+; `veh_age` (0, 2, 4, 8, 12, 100) labels 0-1 / 2-3 / 4-7 / 8-11 / 12+; `veh_power` (4, 5, 6, 7, 8, 15) labels 4-4 / 5-5 / 6-6 / 7-7 / 8+. The saved Bandings' own ids and edges are printed by the seed and recorded here at the proving run.
- Task 2/3 DB tests (`backend/tests/test_demo_rating_evidence.py`: one table per Factor, the pins, the GLM premium to the penny with non-circular golden quotes and the monotone property) are written and collect (3 tests); they need the DB stack and wait for my gate slot. Red-first for them is shown at that slot on the base tree (`origin/main` has no `seed_demo_rate_tables`), then green at the head.

## PRs

(added at the PR)
