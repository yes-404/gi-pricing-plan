---
id: LG-9975
family: ledger
title: WK-1178 slice SL-1541 — compile refuses a model_call whose feature_map misses the pinned model's required inputs, per component for a Peril Structure (FR-240) (PL-1540 slice ledger)
status: active
created: 2026-10-10
owner: executor
tree: 14fa6fb3d5b7097a829343e38cb5f20afbd0d2e2
phase: P2
work: WK-1178
slice: SL-1541
plans: [PL-1540]
corrected_by: []
relates: [PL-1540, RL-1523, RL-1445, RL-1263, FD-1424, FR-240, FR-222, NFR-499, WK-1178]
---

# LG-9975 — WK-1178 slice SL-1541: compile refuses a short `feature_map`

*(LG-9975 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1541` from PL-1540, base `origin/main` `14fa6fb3d5b7097a829343e38cb5f20afbd0d2e2`. Times are BST
(`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md`, "2026-10-10 21:41:05 BST — RL-1445 CAP: AMENDED by dated line (counting unit = gate or measurement, with guard rails); GO SL-1541 (WS-1 (a)); OP-1503-1 (a); SL-1575 noted", item 2: "GO SL-1541 (PL-1540; A-4 need 4a), needs 1–5 MET as you quoted. Lane: MERGE serialises after SL-1557 on compile_bundle; authoring runs in parallel. FR-240's anchor: the executor re-counts at its base under RL-1523 :148, and a count ≠ 1 is a STOP. WS-1 (a) ADOPTED: test_quote_input_raise_sites.py joins the write set for ONE census entry ("rating/compile.py","check_model_call_coverage"), red-first, its input-free reason quoted. The second of SL-1541 and SL-1557 to merge reconciles _INPUT_FREE by content. If SL-1600 merges first, SL-1541's new raise uses its InputFreeError marker (DP-2 (c)), and its message is checked input-free at the ACK (NFR-499)."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1540` (leaf plan, WK-1178). Roadmap row `SL-1541` — "WK-1178 slice — compile refuses a `model_call` whose `feature_map` misses the pinned model's required inputs". Requirements: `03` FR-240 (as RL-1523 amends it), FR-222, FR-255 (the category these faults no longer reach), `02` FR-188. Write set: PL-1540 §"Write set", plus (WS-1 (a)) the one census entry in `packages/pricing-core/tests/test_quote_input_raise_sites.py`. Lane: authoring beside SL-1557 (WK-675 S3); the MERGE serialises after it on `compile_bundle`.

### Task list

- [x] Task 0 — preconditions (below).
- [x] Task 1 — the reds (Acceptance 1–3, 6, 13 first test) and WS-1's census red; `041d46b5`.
- [x] Task 2 — the check (Acceptance 1–6, 13); `54b79c67`.
- [~] Task 3 — backend e2e test (Acceptance 7) and 13's second test authored `49d28282`, DB run owed to the gate slot; Acceptance 11 pricing-core modules run, see Build log; one red OPEN (below).
- [x] Task 4 — the FR-240 text, `084fcba0`; phrase count 1.
- [ ] Task 5 — Acceptance 9, 10, gate (Acceptance 12), closing acts.

### Gate

Not yet run. Owed: one full two-half gate in gate-1, on the lead's "gate slot granted" for the head.

### Audit

Not yet given.

### Build log

#### Task 0 — read 2026-10-10 23:38 BST at base `14fa6fb3`

- `git grep -n "def required_model_inputs(" -- packages backend/src`: one hit, `packages/pricing-core/src/pricing_core/modelling/factors.py:338`. **Task 0a skipped.**
- Reuse mapping: `compile_bundle`'s `resolved_pins` (every pin, then every component by `setdefault`).
- FR-240 anchor, `git grep -cF` in `docs/specs/03-rating-engine.md` at this base: RL-1523's original string `The message names the step and the rung.)* |` = 0; the last amendment's closing sentence `(SL-1466, FD-1456). |` = **1** (row :138). Not a STOP (RL-1523 :148–154 limb 2, the last amendment now being RL-1459's).
- Status flips in the first commit: `PL-1540` `draft → active`, `SL-1541` `draft → active`.

#### Red-by-cause runs (2026-10-10, 22:4x–23:5x BST)

Each: `flock -w 300 /tmp/slots/small-test -c "timeout 150 nice -n 19 uv run --directory <wt> pytest -q -p no:cacheprovider <file>"`, load1 under 4.2, no gate held.

| File, state | rc | Printed |
|---|---|---|
| `test_rating_compile_completeness.py`, tests only (`041d46b5`) | 1 | four `Failed: DID NOT RAISE ValueError` (GLM, GBM, peril, empty map); `AttributeError: module 'pricing_core.rating.compile' has no attribute 'required_model_inputs'` (spy test); controls green (`5 passed`) |
| `test_quote_input_raise_sites.py`, census entry added, no code | 1 | `Right contains 1 more item: {('rating/compile.py', 'check_model_call_coverage'): 1}` |
| both, at `54b79c67` | 0 | `10 passed`; `19 passed` |

Acceptance 11 at `54b79c67`+: `test_rating_compile_bundle` 30 passed; `_runtime` 14; `_score` 46; `_glm_model_call` 22; `_pin_membership` 26; `_inline` 24; `_declared_reads` 12; `_attribution` 28; `_dislocation` 40; `_ladder_exact` 26; `_lookup_as_at` 19; `_number` 14; `_score_batch` 11; `_shadowed_inputs` 12; `_wire_order` 14; `_committed_strings` 6; `test_fremtpl2_rate_fixture` 2; `test_testing` 35 (all passed).

Fixture edits (completed, never the check weakened): `test_rating_compile_fr240.py::test_a_model_call_over_risk_factors_compiles` now maps `year_of_account` (the model was fitted on it). `test_rating_peril_scoring.py::test_a_peril_model_call_inside_a_mounted_sub_graph_is_checked_at_compile` was red at `54b79c67` (see the inliner fix below).

#### The inliner fix (write set + `inline.py`, `test_rating_inline.py`, `test_rating_mounted_model_call.py`)

Authority: `to-lead.md` "2026-10-10 23:46:57 BST — RULING (mispricing): the inliner renames feature_map KEYS, never values — option (A), fixed INSIDE SL-1541; 03 :943 corrected by dated line; an FD at D10; the exposure query owed before SL-1541's ACK" (cited here because `RL-1571` is frozen). Found by the new check run over the inlined algorithm: `inline.py` `_inline_one` collected and renamed `feature_map` VALUES as graph names.

Red at base (`bca00b9b` merge head, tests only, single files): `test_rating_inline.py` `1 failed` x2 — `assert {'ncd_raw': 'm_ncd__f'} == {'m_ncd__ncd_raw': 'f'}` and `assert {'ncd_years': 'm_ncd__ncd_raw'} == {'years_clean': 'ncd_raw'}` (the value-not-renamed test); `test_rating_mounted_model_call.py` `3 failed`, each `CodedError: RATING_STEP_UNDECLARED_READ: step 'm_call__s_risk' reads ['power'] without declaring them in consumes (FR-246)` (the unrenamed internal key; the cause is the same inversion). Green after: `3 passed`, `25 passed`, and `test_rating_peril_scoring` 25 passed, `test_rating_compile_bundle` 31, `test_rating_runtime` 14. 03 inlining paragraph (row :943) carries the dated, struck correction in the same commit; commit `29b460f9`.

**Write-set additions, disclosed:** `packages/pricing-core/src/pricing_core/rating/inline.py`, `packages/pricing-core/tests/test_rating_inline.py`, and the new `packages/pricing-core/tests/test_rating_mounted_model_call.py` (the test the ruling required), on the 23:46:57 ruling; plus WS-1 (a)'s census entry and the `test_rating_compile_fr240.py` fixture completion.

**Exposure (23:46:57 item 4), run 2026-10-11 under `flock -w 300 /tmp/slots/small-test`, read-only, main dev DB `gipricing` (container `gi-pricing-postgres-1`):**
`select count(*) from sub_graph_versions` -> 0; `select count(*) from sub_graph_versions where content::text like '%"model_call"%'` -> 0; `select count(*) from rating_algorithms where jsonb_array_length(coalesce((content::jsonb)->'sub_graphs','[]'::jsonb))>0` -> 0 (of 1 `rating_algorithms` row); `select status, count(*) from rating_versions group by 1` -> `approved|1`. So no stored algorithm mounts a fragment and no sub-graph version exists: exposure 0.
Grep of the committed fixtures and `examples/` (`git grep -nE '"ref": *"?sub_graph:|mount_point' -- examples scripts backend packages`): the only stored-DB mount fixture is `backend/tests/test_rating_version_compile.py:1023`, whose fragment (`_ncd_sub_graph`, :989-) holds one `expression` step and no `model_call`, so no money expectation there moves. The other mounts are model-schema / inline / runtime tests with no model_call (before this slice).

**Acceptance 9/10 (at `a243c068`):** `git diff origin/main...HEAD -- backend/src/app/errors.py | wc -l` -> 0; `git grep -c MODEL_CALL_FEATURE_MAP_INVALID -- packages/pricing-core/src/pricing_core/rating/compile.py` -> 1; `git diff --stat origin/main...HEAD` names the PL write set plus the additions above. `packages/model-schema/tests/test_rating_algorithm.py` 31 passed. `scripts/bench-rating.py --warmup 1 --iterations 2 --rows 500` (compile path only, rc 0, no timing read). **Deviation:** it ran under the small-test slot while gate-1 was held by another seat (1-min load 9.3 at the start); the run made no timing claim and no DB call, but it was a heavier run than the small-test rule permits beside a gate. Recorded, not repeated.

## PRs

None yet.
