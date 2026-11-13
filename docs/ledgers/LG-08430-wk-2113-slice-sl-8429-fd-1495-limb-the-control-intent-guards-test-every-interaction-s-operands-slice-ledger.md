---
id: LG-8430
family: ledger
title: WK-2113 slice SL-8429 — FD-1495 limb: the control-intent guards test every interaction's operands (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-13
owner: executor
tree: 2ba0d0d53142dacd6550cb314a4d65685b612bd1
phase: P3
work: WK-2113
slice: SL-8429
plans: []
corrected_by: []
relates: [SL-8429, FD-1495]
---

# LG-8430 — WK-2113 slice SL-8429: the control-intent guards test every interaction's operands

Filed 2026-11-13 under working id 8430 (lead-reserved); executed by seat `exec-sl8429`, branch `sl-8429-fd1495-interaction-operands` off `origin/main` `2ba0d0d53142dacd6550cb314a4d65685b612bd1`. Working ids in prose are in space form (SL 8429, OQ 8431) until the mint.

**GO:** the maintainer's entry, verbatim:

> ## 2026-11-13 19:51:15 GMT — Maintainer: FD-1495 PROBE READ (scratch/lead34-fd1495/rc-table.md b341f2abbcf8, at 2ba0d0d53142): CONFIRMED — the feature guard does not raise, compile_bundle compiles end to end, the instrument is proven red on the shipped GBM-on-control case, and predict_glm_row moves 0.105315 → 0.277157 on quotes differing only in the control Factor yoa. SEVERITY RULED: HIGH, on the probe, not on words — a `control` Factor moves a premium through a `risk` interaction, FR-88/FR-240's exact prohibition, a mispricing path reachable by any user-authored model with one interaction over a control operand. Shipped impact: none known (freMTPL2 seed: risk Factors only, no interactions; no non-template DB on this box) — that clause stays in the finding. GO, SLICE WK-2113 S1 "FD-1495 limb: the control-intent guards test every interaction's operands": plan, needs and census as sent (builder executor/sonnet, reviewer, auditor; one builder worktree off origin/main; gate-1 slot + createdb -T copy + redis db 1/3; no migration; 3 seats live, 0 builders, 0 gates). CONDITIONS: (1) RED FIRST, each test failing at 2ba0d0d5 with its failure line in the LG before the fix: the feature guard, `_refuse_control_factor_keys`, rate_tables/operations.py:233, and an end-to-end compile_bundle refusal with the named error CONTROL_FACTOR_IN_RATEABLE_PATH naming the OPERAND and the cross. (2) NESTED interactions: an interaction whose operand is itself an interaction over a control Factor is refused too — expand to leaves, with a test at depth 2. (3) The offset path (the same function's offset_source branch) gets the same expansion and a test. (4) The guard must hold when the operand Factor is not among the pin's resolved Factors: unknown operand = REFUSE (fail closed), never skip — the existing `by_slug.get(feature) is not None` shape skips silently; say in the LG what the fixed code does for a missing Factor and test it. (5) Same hash, same price (FR-239): the fix refuses at compile and changes no scoring arithmetic and no spec_hash of a bundle that compiled before WITHOUT a control operand — a regression test over the freMTPL2 fixtures' hashes. (6) Spec: FR-240 (and FR-88 if it speaks of operands) gets a dated clarification that "fitted on a control Factor" includes a control operand of an interaction at any depth; the spec change is in the same commit as the code (CLAUDE.md §2). A stricter rule — an interaction over a control operand may not be declared `risk` at all, refused at Factor definition — is a DESIGN CHOICE the specs leave open: an OQ with options and a recommendation, not built in this slice. (7) Full gate, both halves, at the re-merged head; ids minted before the PR; LG with the red and green lines; audit; then the grant request. C6's sweep reads the backend save/approval path and POST /score end to end for the same gap and reports before this slice's audit.

**MERGE-ACK:** not yet given.

## Tasks

### Scope

WK-2113 has no Work plan yet (the Work is `draft`); the slice's row is `docs/roadmap.md` `#### SL-8429` under WK-2113. Requirements: `FR-88` (`02`), `FR-240` and `FR-239` (`03`). Out of scope by the brief: sweep cells G3, G4, G6 (awaiting rulings); the stricter definition-time rule (OQ 8431, not built); WK-2113's own status line.

### Task list

1. **Red first** (condition 1): the tests, committed alone as `575a5a68`, run via `run-small` at that head: 13 failed, 35 passed, rc=1, each failure `Failed: DID NOT RAISE ValueError`. The five positive controls (risk operands compile / pass) passed at the same head, so the harness is proven, not only the failures.
2. **Fix**: `control_factor_in(factor, pool)` in `packages/pricing-core/src/pricing_core/modelling/factors.py` expands a Factor to itself plus its transitive operands (by `operand_factor_ids` against `pool`) and returns the first `control` Factor; `rateable()` (G5, had no caller) now uses it, so there is one definition. Used by the compile feature guard (`_refuse_control_factor_features`, including the `offset_source` recursion), the compile key guard (`_refuse_control_factor_keys`) and the seed (`rate_tables/operations.py`).
3. **Backend resolver**: the `factor` branch of the compile resolver (`backend/src/app/platform/rating_versions.py`) returns `factors=` the chain `load_factor_by_ref` already builds (the Factor and its operands). Without it a table key's operands are not visible to compile and the fail-closed rule would refuse every interaction-keyed table. Its DB-backed tests are owed to the gate.
4. **FR-239 regression** (condition 5): `test_the_control_operand_guards_leave_the_fixture_bundle_hashes_unchanged` pins the freMTPL2 baseline and full-candidate `content_hash` (measured at the pre-fix code and at the fixed code: identical, `scratch/sl-8429-fd1495-interaction-operands/hash_probe.py`). The older pins `_PINNED_PRE_DECIMAL_HASH` and `_SCORE_FIXTURE_HASH` stay green in the GREEN set. The guards only refuse; no scoring arithmetic is touched.
5. **Spec** (condition 6), same commit: dated clarifications on `FR-240` (`03`) and `FR-88` (`02`); `OQ 8431` in `docs/open-questions.md` and `03` §10, mirrored; FD-1495's register row gains the new limb (HIGH, owner WK-2113, shipped impact "none known: freMTPL2 seed risk Factors only, no interactions; no non-template DB on this box"); the `SL-8429` row, `active`.

### Gate

**Red** (head `575a5a6866b1a6db8cae95e4172125f66700cf5a`, tests only; log `red.log`, first line `head=`, last line `rc=1`), `run-small` on `test_rating_compile_fr240.py`: `13 failed, 35 passed in 4.44s`, rc=1. Each failure line (all `E       Failed: DID NOT RAISE ValueError`):

```
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_a_risk_interaction_over_a_control_operand
FAILED test_rating_compile_fr240.py::test_the_feature_guard_expands_a_nested_interaction_to_its_leaves
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_an_operand_that_is_not_among_the_pins_factors
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_a_control_operand_in_the_offset_model
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_a_missing_operand_in_the_offset_model
FAILED test_rating_compile_fr240.py::test_a_model_call_over_a_glm_with_a_control_operand_interaction_is_refused
FAILED test_rating_compile_fr240.py::test_a_model_call_over_a_glm_whose_interaction_operand_is_missing_is_refused
FAILED test_rating_compile_fr240.py::test_the_key_guard_refuses_a_table_keyed_on_an_interaction_of_a_control_operand
FAILED test_rating_compile_fr240.py::test_the_key_guard_expands_a_nested_interaction_to_its_leaves
FAILED test_rating_compile_fr240.py::test_the_key_guard_refuses_an_interaction_whose_operand_is_not_resolved
FAILED test_rating_compile_fr240.py::test_seeding_from_an_interaction_of_a_control_operand_is_refused
FAILED test_rating_compile_fr240.py::test_seeding_from_a_nested_interaction_expands_to_the_leaves
FAILED test_rating_compile_fr240.py::test_seeding_from_an_interaction_with_a_missing_operand_is_refused
```

**Green** (the fixed head; logs under `scratch/sl-8429-fd1495-interaction-operands/`, each `head=` first and `rc=` last):

| check | head | result | rc |
|---|---|---|---|
| import-closure set, pricing-core part: 67 test files in 23 `run-small` batches of at most three (`green-core.log`) | `3f0eebbd` | 22 batches rc 0; batch 8 (`test_prediction_interval.py`, `test_quantile_crossing.py`, `test_quote_input_raise_sites.py`) rc 1: `test_every_quote_input_raise_site_has_a_sentinel_case`, the census counted two `_raise_named` sites in each of `_refuse_control_factor_keys` and `_refuse_control_factor_features` where the allow-list said one | 1 |
| census fix `ae216c91`: `test_quote_input_raise_sites.py`, `test_rating_compile_fr240.py`, `test_fremtpl2_rate_fixture.py` (`green-census.log`) | `ae216c91cc55` | 71 passed | 0 |

**Docs and static checks** (head `30c400bcf5bf`, `git diff --name-only origin/main...HEAD` in `diff-names.txt`; each through `flock -w 900 /tmp/slots/gate-2`; logs `head=` first, `rc=` last):

| check | rc | note |
|---|---|---|
| `python3 scripts/audit-docs.py` (`audit-docs-3.log`) | 1 | `FAILED (1): check 31: gap in the full allocation between 2115 and 8429`: the slice's own working ids, cleared by the mint. The first run (`audit-docs.log`) also failed check 22 (an unescaped pipe in FR-240's clarification) and check 39 (stale INDEX); both fixed in `3de1d980` and `30c400bc`. |
| `python3 scripts/doc-index.py --check` (`doc-index-check-3.log`) | 0 | byte-stable |
| `python3 scripts/register-lint.py` (`register-lint-2.log`, head `3de1d980`) | 0 | 0 violations |
| `uv run python scripts/req-coverage.py` (`req-coverage-2.log`, head `3de1d980`) | 0 | |
| `uv run python scripts/generate-contracts.py --check` (`generate-contracts.log`, head `313d4c59`) | 0 | 58 contracts match |
| `uv run ruff check .` (`ruff.log`) | 0 | |
| `uv run mypy` (`mypy.log`) | 0 | 257 source files |
| `uv run lint-imports` (`lint-imports.log`) | 0 | 4 kept, 0 broken |
| `ruff format --check` on the 7 changed `.py` files | 1 | five are unformatted at `origin/main` too (`operations.py`, `compile.py`, `rating_versions.py`, `test_rating_compile_fr240.py`, `test_quote_input_raise_sites.py`); `factors.py` and `test_fremtpl2_rate_fixture.py`, clean at `origin/main`, are clean |
| `scripts/idsweep.sh origin/sl-8429-fd1495-interaction-operands` | 0 | no duplicate, no cross-branch number |

**Spec-reading and docs-audit tests** (`docs-tests.log`, head `30c400bc`, run-small in batches of three, `tests/` only; the list is `grep -lE 'docs/specs|"docs" */ *"specs"' backend/tests tests`, saved as `spec-readers.txt`, plus the eight docs-audit files): `test_doc_id.py`, `test_doc_id_verify.py`, `test_permission_parity.py`, `test_scope_audit.py`, `test_file_census.py`, `test_doc_id_migrate.py`, `test_spec_examples.py`, `test_doc_id_history_input.py`: 325 + 342 + 40 passed, rc 0. The eight docs-audit files: 13 FAILED across three batches, every one in the item-31 set (`test_audit_docs_finding_citations`, `test_audit_docs_ids`, `test_audit_docs_process_core_digest`, `test_audit_docs_w37_11_ceiling`, `test_doc_index` (`test_an_index_skipping_a_reserved_block_breaks_contiguity`), `test_register_lint`, `test_register_owed`, `test_repository_invariants`), each reading the real tree, which `audit-docs` fails only on check 31. They are re-run at the mint. The nine spec-reading files under `backend/tests` need the DB lane and are owed to the gate.

The 107 backend test files the closure reaches need a database and are **owed to the gate** (brief: no DB lane for the seat). The closure is derived by `closure.py` (the changed source modules, every source file importing one, one more level of importers; GREEN = every test file importing anything in it): `git diff --name-only HEAD -- packages backend/src` for the changed modules, then an `ast` walk of `packages/**/src` and `backend/src`; lists in `changed.txt` and `green-tests.txt`. The route sweep `backend/tests/test_api_authorisation_sweep.py` is not in the closure (no request shape changed) and not run.

### Condition-by-condition evidence

1. **Red first**: above; four named tests (feature guard, `_refuse_control_factor_keys`, seed at `operations.py`, end-to-end `compile_bundle` naming the operand `yoa@1` and the cross `region_x_yoa`) are among the 13.
2. **Nested interactions**: `control_factor_in` walks to any depth (a visited set bounds a cycle); tests at depth 2 for the feature guard, the key guard and the seed. **Can a nested cross reach a pin?** `_cross` (`factors.py`) raises `FactorResolutionError` for an interaction operand at resolution, and the backend `load_factors` expands one level only, so a nested Factor can be stored but cannot be fitted or scored; the guard does not rely on that and refuses it by expansion, or by the missing deeper operand (fail closed).
3. **Offset branch**: `_refuse_control_factor_features` recurses into `offset_source` and now tests the closure there; tests for a control operand and for a missing operand in the offset model.
4. **Missing operand**: an operand id not among the pin's Factors raises `FactorResolutionError` in `control_factor_in`; every caller converts it to `CONTROL_FACTOR_IN_RATEABLE_PATH` naming the cross and the operand id. Tested for a model, an offset model, an end-to-end `compile_bundle`, a table key and a seed. **What the fixed code does for a consumed feature with NO Factor at all** (`by_slug.get(feature) is None`): kept, it is not refused. A feature with no Factor has no intent to be `control`; `03` FR-222's amendment names "its `feature_order` when it has no Factors" as a legal required-input set (a GBM on raw columns). A Factor the pin carries but whose operand it does not is refused. 
5. **Same hash, same price**: item 4 of the task list.
6. **Spec**: item 5; OQ 8431 given options and a recommendation, not built.
7. **Full gate, ids minted, audit, grant request**: not this seat's; the full gate is owed (no grant yet), ids stay working, no PR.

### Follow-up by seat `exec-sl8429b` (2026-11-13, six rulings the first builder did not apply)

**Ids of this slice (working, space form until the mint):** SL 8429, LG 8430, OQ 8431, OQ 8438, OQ 8439, FD 8440, FD 8441, FD 8444.

**Rulings applied, each quoted from `to-lead.md`:**

> ## 2026-11-13 19:53:34 GMT — (R1) WK-2113 (P3-C) goes draft → ACTIVE by my dated line of this stamp, riding S1's PR: its first slice is a HIGH correctness fix on my GO, which is activation in fact; the line says so.

Done: `docs/roadmap.md`, WK-2113's own block, `status: active` and the dated line "2026-11-13 19:53:34 GMT — ACTIVATED".

> ## 2026-11-13 19:54:02 GMT — S1 SCOPE NOTE — NOT VETOED. The backend resolver's `factor` branch (rating_versions.py:774–788) returning the Factor plus its operand chain in factors= is IN S1 … Two tests ride it through the REAL resolver path (not a hand-built ResolvedArtifact): a risk×risk interaction-keyed rate table still compiles and prices as before (same content hash), and the same table with a control operand is refused with the named error.

Done: two DB-backed tests in `backend/tests/test_fr240_governance.py`, driving the real compile Job over a `WorkspaceResolver`: `test_a_risk_by_risk_interaction_keyed_table_compiles_with_an_unchanged_hash` (a) and `test_an_interaction_keyed_table_with_a_control_operand_fails_to_compile_with_its_code` (b). **Expected at `2ba0d0d5` (the tree before the fix): (a) green, (b) red** (before the fix the resolver returned no operand chain and the control operand was never read). **Both are first RUN at the gate**: this seat has no database; each was checked only to import (`import backend.tests.test_fr240_governance` rc 0) and to pass `ruff check`. Test (a) proves the real resolver still compiles the table and that the bundle's `resolved_payloads` holds the Factor payload only (the operand chain rides `ResolvedArtifact.factors`, which is not hashed); the literal pre-fix hash equality is pinned by `test_the_control_operand_guards_leave_the_fixture_bundle_hashes_unchanged` (pricing-core). One risk to read at the gate: the seeded table has no cells (the `test_api_rate_tables.py` direct-insert convention).

> ## 2026-11-13 19:58:03 GMT — B2 (the algorithm save check tests no intent and REQUIRES the control operand as a feature_map input): into S1 if it is one call to the same closure helper in rating_versions.py with a red-first test; otherwise S3.

**NOT done, goes to S3.** The check is `_accepted_feature_map_values` in `backend/src/app/platform/rating_algorithms.py` (not `rating_versions.py`). It is not one call: the call would sit in a loop over the consumed features with the same error mapping as `_refuse_control_factor_features`, and it would also make the save refuse a model fitted on a *direct* control Factor, which today saves and is refused only at compile. `test_a_compile_over_a_gbm_fitted_on_a_control_factor_fails_with_its_code` (`backend/tests/test_fr240_governance.py`) asserts the algorithm saves with 201 and only the compile Job fails, so the change is a decision on the save-versus-compile contract, not a one-line addition. Stated as a redesign, so per the ruling it is S3's.

> ## 2026-11-13 19:58:03 GMT, condition (8) — Dislocation's interim asymmetry (recompiles and fails at prepare while /score prices until S3) is stated in S1's LG as known and closed by S3.

**Known interim asymmetry, closed by WK-2113 S3:** after S1, a dislocation run on a pre-fix rating version with a control operand fails at prepare (dislocation recompiles through `compile_bundle`), while `/score` of the same version keeps pricing from its stored bundle until S3's load-time guard and re-validation land. Census on this box: 0 rating versions (gipricing `rating_versions` = 0), so 0 affected.

> ## 2026-11-13 19:58:38 GMT — G3 AND G4 RULED … They are SPEC GAPS, not guard bugs: FR-240 binds intent "by factor_ref" and FR-86/FR-88 make intent a property of a Factor and are silent on columns. So: NO SLICE, and no silent pick. YES — both are filed as OQ rows (8438 G3, 8439 G4) in S1's PR beside OQ 8431, mirrored in the spec §10 and open-questions.md, each with the four options (a) column-level intent, (b) control columns derived at compile over the workspace's Factors, (c) factor_ref required on every rateable key, (d) accept and document … MY RECOMMENDATION for the record: (a) … REGISTER: two candidate rows, owner WK-2113, G3 MEDIUM … G4 LOW … each row says "spec gap, decision owed: OQ <id>" … Until the OQs are ruled, the upgrade note and the FR-240 dated clarification in S1 say in words what the guards do NOT cover: bare-name and banding-only keys, and a risk Factor over a column another Factor calls control.

Done, no code: OQ 8438 (G3, `03` §10) and OQ 8439 (G4, `02` §10), each also in `docs/open-questions.md`, status open, decision owed, four options, both recommendations recorded as recommendations (the seat's: (c) for G3, (b) for G4; the maintainer's: (a)); register rows FD 8440 (G3, MEDIUM) and FD 8441 (G4, LOW), owner WK-2113, "spec gap, decision owed: OQ 8438" / "OQ 8439"; the FR-240 dated clarification in `03` now says in words what the guards do not cover. The upgrade note is S3's (CHANGELOG), not S1's.

**New red/green lines**

| line | head | result |
|---|---|---|
| (a) risk×risk interaction-keyed table compiles through the real resolver | not run (no database) | expected green at `2ba0d0d5` and at the fixed head; first RUN at the gate |
| (b) same table, control operand, `CONTROL_FACTOR_IN_RATEABLE_PATH` | not run (no database) | expected red at `2ba0d0d5`, green at the fixed head; first RUN at the gate |

**Checks after the follow-up** (tree: this branch's head at the follow-up commit, before the push; run through `flock -w 900 /tmp/slots/gate-2` for the docs scripts): `audit-docs.py` rc 1, FAILED (1): check 31, the gap between 2115 and 8429 (the slice's own working ids, cleared by the mint); `doc-index.py --check` rc 0; `register-lint.py` rc 0; `req-coverage.py` rc 0; `ruff check .` rc 0; `mypy` rc 0 (257 source files). Spec-reading tests (`run-small`, batches of three, `tests/` only): `test_doc_id_verify`, `test_permission_parity`, `test_scope_audit` 187 passed, 1 skipped; `test_file_census`, `test_audit_docs_ids`, `test_doc_id_migrate` 451 passed, 2 failed; `test_doc_id_history_input`, `test_doc_id`, `test_doc_index` 209 passed, 1 failed; `test_spec_examples`, `test_repository_invariants`, `test_register_lint` 79 passed, 5 failed. **Every failure is in the docs-audit set that reads `audit-docs` (item 31 of the common brief)** and is the same set as the first builder's `docs-tests.log` (`test_audit_docs_ids` ×2, `test_doc_index` contiguity, `test_register_lint` ×3, `test_repository_invariants` ×2), all from check 31 on the working ids; none is a spec-reading failure on content. Import closure for the one `.py` file touched (`backend/tests/test_fr240_governance.py`): no file imports it (`git grep test_fr240_governance -- backend tests` lists none); it imports (rc 0). No raise site was added, so `test_quote_input_raise_sites.py` is not re-run.

### Review round (seat `exec-sl8429c`, 2026-11-13; the review is `scratch/rev-sl8429/review.md`, sha256 prefix 4ced61b46134)

Each finding, its disposition and its evidence. Logs are under `~/gi-pricing-plan.local/scratch/sl8429c/` (local, not in the repository), each opening `head=` and ending `rc=`.

- **B-1 (blocking, the 20:29:21 process-backlog row): done.** A dated row in `docs/process/process-backlog.md`, dated 2026-11-13.
- **F-1 (MEDIUM, `rateable()` admitted `offset` and `diagnostic` Factors): fixed, red first.** `rateable()` now requires `FactorIntent.RISK` AND no `control` in the operand closure (FR-88: "Rating Versions may only use `risk` factors"; FR-86). Test `test_only_risk_factors_are_rateable` (`packages/pricing-core/tests/test_glm.py`): RED at `0edae7a3`'s code (`red-f1.log`: `FAILED test_only_risk_factors_are_rateable`, rc=1; that run's second failure is F-2's test, which failed on a mistake in the seat's own fixture, not on the code), **Commit record:** the red tests were measured uncommitted on the worktree at `0edae7a3`'s code and were committed together with the fix in `01d068ee` (pushed before the lead asked for them alone); no history rewrite, this line is the record. GREEN after the fix (`green-f1.log`: 109 passed, rc=0). Callers, read with `git grep -nE "\brateable\(|control_factor_in\("` at this tree: `control_factor_in` is called by the three guards (`rate_tables/operations.py` seed, `rating/compile.py` key guard and feature guard); `rateable()` has no caller outside tests (`test_glm.py`, `test_rating_compile_fr240.py`). **No guard's verdict changes**: the guards call `control_factor_in`, which is untouched, so nothing a guard accepted at `2ba0d0d5` is refused now.
- **F-2 (LOW, cycle-safety untested): test added.** `test_control_factor_in_terminates_and_decides_on_a_cyclic_operand_graph` (`test_rating_compile_fr240.py`): A crosses B and B crosses A; it terminates, returns `None` with no control leaf and the control leaf when one hangs off the cycle. It tests behaviour the code already had (the `seen` set), so it is a regression guard, not red-first; it is GREEN with the F-1 fix in `green-f1.log`.
- **F-3 (LOW, `load_factors` one level deep): chose to load the full chain.** `backend/src/app/platform/modelling.py` `load_factors` now loops level by level; an id already loaded is never asked for again (so a cycle cannot loop). **Queries:** one per level, no per-row loop: pinned interaction over plain operands is 2 (unchanged), a depth-2 chain is 3. Why not only reword the refusal: the message lives in `pricing-core`, which cannot know the platform loads one level, and a guard that refuses a depth-2 chain it could have read is a refusal for a reason the platform chose; `resolve_factors` still refuses a nested cross at resolution, so no priced path changes. **Two DB tests through the real resolver (lead's amendment, binding over the either/or): `test_a_clean_depth_two_interaction_keyed_table_compiles` (a clean depth-2 risk chain compiles) and `test_a_depth_two_interaction_keyed_table_with_a_control_leaf_is_refused_by_the_guard` (below).** The second (through the real `factor` branch of `WorkspaceResolver`, which calls `load_factors` via `load_factor_by_ref`) expects `CONTROL_FACTOR_IN_RATEABLE_PATH` naming `yoa`; written now, runs in phase 2. The model branch uses the same `load_factors`; no GLM-with-interaction model-pin DB test was added (a fitted pinned GLM over an interaction is a heavy fixture); that is stated, not claimed covered by a test.
- **F-4 (LOW, the hash pin): done in part; phase 2 pins the literal.** The DB test (a) now asserts `bundle.content_hash == _PRE_FIX_RISK_BY_RISK_HASH` (a placeholder until phase 2 measures it at `2ba0d0d5`'s code and pins it), over a deterministic fixture (ids from `uuid5(workspace_id, name)`, fixed table slug, fixed values) and a table with real cells (`rate_table_cells` rows). **Provenance of the freMTPL2 pin added in `3f0eebbd`:** `test_fremtpl2_rate_fixture.py` was run against the pre-fix code at `575a5a68` in a throwaway detached worktree (removed by its exact path after `docker inspect` of the four shared containers showed no bind source under it): `pin-at-575a5a68.log`, `head=575a5a6866b1a6db8cae95e4172125f66700cf5a`, `3 passed in 3.75s`, `rc=0`. **Limit, stated:** the freMTPL2 fixtures contain no interaction, so that pin proves the no-interaction path only; the risk-by-risk DB test (a) is the one that sees the new path.
- **F-5 (LOW, `_yoa` read after an underscore): done.** Renamed to `yoa` where it is read (`test_the_feature_guard_refuses_an_operand_that_is_not_among_the_pins_factors`); the other unpacking sites keep `_yoa` because they do not read it.
- **Early-gate red 1 (the NFR-499 error-sink census): fixed.** `backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for` was RED at `0edae7a3` in the lead's early gate and still red at this branch's head `5d2189a3` before the fix (`red-sinks.log`: `1 failed, 8 passed, 2 warnings, 4 errors`, rc=1; the 4 errors are the DB-fixture tests, which need the DB window). Three new refusal sites (`operations.py` `seed_from_model`, `compile.py` `_refuse_control_factor_keys` and `_refuse_control_factor_features`) interpolated a caught `FactorResolutionError`'s text. Fix, the lead's preferred form: `control_factor_in` raises a new `OperandNotSuppliedError` (a `FactorResolutionError` subclass, `modelling/factors.py`) carrying `factor_slug` and `operand_id`, and each site builds its own message from those two names and never from exception text. The missing operand is by definition not loaded, so its id is the only name there is; the interaction's slug is named. GREEN (`green-sinks.log`: 119 passed, 4 DB-fixture errors, rc=1 only from those errors; the census test passes; `closure-sinks.log`: 114 passed, rc=0 with `test_quote_input_raise_sites.py`).
- **DB window (2026-11-13 21:46:33 to 21:47:30 GMT, DB `gipricing_sl8429c_dbw`, redis db 11, bucket `gip-test-blobs-sl8429c`; logs `win/pre.log`, `win/head.log`, `win/sinks.log`, `window.out`).** Red/green, each at the head it ran on:

| line | at `2ba0d0d5` (pre-fix code; `win/pre.log`, rc=1) | at `add7358f` (`win/head.log`, rc=1; the one failure is the superseded key-set assertion described below) |
|---|---|---|
| (b) risk-by-control interaction-keyed table refused with `CONTROL_FACTOR_IN_RATEABLE_PATH` | RED: `assert <JobStatus.FAILED> ... SUCCEEDED` | green |
| depth-2 chain with a control leaf refused, naming the leaf | RED: same (job SUCCEEDED) | green |
| (a) risk-by-risk compiles | compiles (`PROBE nested=False status=succeeded`); the test failed on its own old key-set assertion | compiles; same |
| clean depth-2 risk chain compiles | compiles (`PROBE nested=True status=succeeded`) | green |
| `test_error_sinks.py` (incl. its 4 DB tests) | not run | 13 passed, rc=0 (`win/sinks.log`) |

Head run: `1 failed, 14 passed` (the failure is test (a) at the old assertion, below). **The content hash of the risk-by-risk bundle is `sha256:f62564d52bf5d469021c7703cdab816c370fe52063901903d20fb4cc3af98db6` at `2ba0d0d5` and at the fixed head, and the same for the depth-2 chain** (the hash reads the graph and the pinned refs, `bundle_hash`); it is pinned as `_PRE_FIX_RISK_BY_RISK_HASH`. Cleanup: `redis-cli -n 11 dbsize` = 0, `count(*) from pg_database where datname='gipricing_sl8429c_dbw'` = 0, bucket removed through the MinIO API, template guard `alembic_version=1 environments=3 tenant_marker=1` at start and end (`window.out`).

**What a compiled bundle carries for a rate-table key's Factor (AMENDMENT 2 item 2, AMENDMENT 3 (2)): option (a). It carries none, by design.** Measured: `resolved_payloads` keys are exactly `['rate_table:sl8429-region-x-yoa@1', 'rating_algorithm:minimal@1']` at `2ba0d0d5` and at the head, for the plain and the depth-2 chain. The code decides it: `compile_bundle` (`rating/compile.py`, `payloads`) builds `resolved_payloads` from the algorithm and `pins.rate_tables`, `pins.models`, `pins.reference_tables`, `pins.custom_objectives` and `pins.sub_graphs`; a key's Factor is not a pin, `_refuse_control_factor_keys` resolves it through the resolver for the guard and drops it. FR-239 (`03`) states the hash as a function of the pins and the graph. So S1's resolver change feeds the compile guard, not the bundle. **The original intent of the test:** its first assertion, `set(factor_payloads) == {"factor:region_x_yoa@1"}`, took a Factor payload in the bundle as the proof that the resolver supplied the operand chain; that was a wrong premise about the bundle (it failed at `2ba0d0d5` and at the head alike, `set() == {...}`), not a defect of the fix. The test now asserts what is promised: the table compiles, the bundle's payload keys are the table and the algorithm, the table's rows carry the seeded cells, and the content hash equals the literal measured at `2ba0d0d5`. "A real cell prices": this fixture's algorithm (`minimal`) does not look the table up, so no score is taken; the cells are asserted carried. The rewritten assertions of (a) were written after this window and have not yet run in the DB.
- **DB window 2 (2026-11-13 21:49:36 to 21:50:21 GMT, DB `gipricing_sl8429c_dbw2`, redis db 11, bucket `gip-test-blobs-sl8429c2`; `window2.out`, `win2/`): a real cell prices; the hash literal was RE-MEASURED for the lookup algorithm.** Test (a) now compiles an algorithm with a `table` step keyed on the cross (`sl8429-lookup`: `premium_in * relativity`). At `2ba0d0d5`'s code (`win2/pre.log`, `head=2ba0d0d53142dacd6550cb314a4d65685b612bd1`) the bundle's content hash is `sha256:3948d954eb79b84aa89f20dca3ecd8e5d9f8b56bf61981b24fa1899c923424f8`, the bundle's payload keys are the table and the algorithm, its rows are the three seeded cells, and the quote `{premium_in: 1000, region_x_yoa: "north | 2011"}` scores `payable` = 1100 (the cell's 1.10 through the arithmetic). At the fixed head the whole-file run's first assertion printed the same hash (`win2/head.log`: `assert 'sha256:3948d...1899c923424f8' == ...`, the literal the test then held being a placeholder); my head probe in this window failed for a fault of its own (it lacked the module's autouse handler fixture, `JOB_HANDLER_NOT_REGISTERED`), so the head's full hash line is the assertion's, not the probe's. The head run was `1 failed, 12 passed` and its one failure is that placeholder. **DB window 3 (2026-11-13 21:51:37 to 21:52:01 GMT, DB `gipricing_sl8429c_dbw3`, redis db 11, bucket `gip-test-blobs-sl8429c3`; `window3.out`, `win3/head.log`): one run of `backend/tests/test_fr240_governance.py` at `head=471f23ae04cb23f3811bea31efd8f8039d89df27` with `-rA`: `13 passed`, rc=0, including the pinned hash and the priced value `payable` = 1100 of test (a), the clean depth-2 compile and the depth-2 control-leaf refusal.** The `ERROR app.worker ... job handler failed` lines in that run are the compile Job logging the refusals those tests expect. Cleanup: redis `-n 11 dbsize` = 0, `pg_database` count = 0, bucket removed through the MinIO API, template guard unchanged.
- **The new refusal messages carry no exception text, so `safe_error` does not apply (the maintainer accepted the form as built, AMENDMENT 4).** (1) The missing operand is named by its id because it is not loaded: there is no Factor to read a slug from, and `OperandNotSuppliedError` holds only `factor_slug` (the interaction) and `operand_id`. (2) Neither field carries user-supplied free text. `operand_id` is a `UUID`: `Factor.operand_factor_ids: tuple[UUID, ...]` (`packages/model-schema/src/model_schema/modelling.py:166`), and the interaction's own `Factor.id: UUID` (`modelling.py:133`). `factor_slug`: be exact, the `Factor` model declares `slug: str` with no pattern (`modelling.py:134`); the grammar is enforced at the one creation route, `FactorCreate.slug: FactorSlug` (`backend/src/app/api/models.py:212`), whose pattern is `^[a-z0-9][a-z0-9_-]{1,62}$` (`packages/model-schema/src/model_schema/refs.py:50` and `:73`), and a Factor row is written only from that route's body (`backend/src/app/platform/modelling.py:252`; `FactorRow(` is constructed nowhere else under `backend/src`). So the slug is a 2 to 63 character lowercase token with no space or free text, by the route and not by the model.
- **G6 (R3, 19:53:34):** filed as FD 8444 in `docs/findings/register.md`: candidate LOW, UNPROBED, owner WK-2113, "the model offset column (`spec.offset.column`, `log_column` and `column` kinds) is a `model_call` input that carries no intent".
- **The 19:54:02 resolver change shares `3f0eebbd` with the pricing-core fix, not a commit of its own, as that ruling allowed. No history rewrite:** the squash makes the split moot, and the lead reports it.
- **`ruff format --check`:** four of the five files touched were already unformatted at `0edae7a3` (`git show 0edae7a3:<file> | ruff format --check --stdin-filename`: rc=1 for `test_fr240_governance.py`, `platform/modelling.py`, `test_glm.py`, `test_rating_compile_fr240.py`; `factors.py` rc=0 before and after). No file was reformatted, so the diff is the change; `ruff check .` is the enforced half.

### Audit

Not yet written; the auditor re-checks.

### Build log

- 2026-11-13: `575a5a68` red tests (13 failed, rc=1). Pushed.
- 2026-11-13: `3f0eebbd` the fix, the backend resolver line, the FR-240/FR-88 clarifications, OQ 8431, the register limb and the `SL-8429` row.
- 2026-11-13: `ae216c91` the raise-site census counts the two new raise sites (found by the closure run: item 11 of the common brief).
- 2026-11-13: seat `exec-sl8429b` continues: R1, the two real-resolver tests, the asymmetry line, OQ 8438 and OQ 8439, FD 8440 and FD 8441 (commit below); B2 not done (S3).
- Note: the first docs-only commands of this seat used `cd` inside a compound command (the harness resets the cwd each call), against the no-`cd` rule; no write followed from a changed directory.

## PRs

None yet: the lead opens the PR.
