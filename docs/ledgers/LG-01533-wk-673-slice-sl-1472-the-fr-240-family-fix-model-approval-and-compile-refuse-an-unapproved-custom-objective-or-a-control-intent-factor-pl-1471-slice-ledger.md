---
id: LG-1533
family: ledger
title: WK-673 slice SL-1472 — the FR-240 family fix, model approval and compile refuse an unapproved custom objective or a control-intent factor (PL-1471), slice ledger
status: active
created: 2026-10-08
owner: executor
tree: 680fb9acd4538de2a74b7a49687aad4fa76e02d3
phase: P2
work: WK-673
slice: SL-1472
plans: [PL-1471]
corrected_by: []
relates: [RL-1470, RL-1445, RL-1263, FD-1422, FD-1469, FR-240, WK-673]
---

# LG-1533 — SL-1472: the FR-240 family fix

Executed from `PL-1471` by `executor-sl1472` (sonnet). Branch `sl-1472-fr-240-family-fix`, worktree
`.claude/worktrees/sl-1472`, from `origin/main` `680fb9acd4538de2a74b7a49687aad4fa76e02d3` (#1236, SL-1448 merged; its
read-back verified by the lead). The slice runs under L1 (a'): one PR, one ledger, no activation PR, no dispatch record.

## Tasks

### 1. Scope

**The GO** (`~/gi-pricing-plan.local/channel/to-lead.md`, local, not in the repository), header verbatim:
"2026-10-08 12:24:44 BST — LANE A DISPATCH GO (conditional on #1236's verified read-back) for WK-673 PL-1471 / SL-1472, the FR-240 family fix: the FIRST slice under L1 (a')".
Its condition (1), #1236's read-back, was verified by the lead and the GO made unconditional before this branch was cut.

**The process it runs under**, headers verbatim: "2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items 1, 3 and 5 APPROVED; IN PRACTICE NOW; the files are amended through RFC 9479 P6 (the maintainer's amendment, by delegation)"
as corrected by "2026-10-08 12:02:08 BST — #1240 P6 flagged readings RULED: (1) REJECTED, and my 11:51:58 L1 (a) wording CORRECTED (the slice's one file is its LG-, not text under the roadmap row); (2) ACCEPTED",
and "2026-10-08 11:53:19 BST — L5 transition RULED: per-slice plans drafted before 11:51:58 MINT AS-IS (T8, B6, B9); their slices still follow L1 at GO", item (b).

**Activation (the dated line, replacing PL-1471 activation need 3).** 2026-10-08: PL-1471's front-matter `status` moves `draft → active`
(status line only, no body edit), and the SL-1472 roadmap row's `status` moves `draft → active`, both in this PR, on the GO's open point (A) accepted
(GO condition (2)).

**Work-plan row (L5 (b)).** PL-1471 (leaf plan, minted as-is in #1233), `docs/plans/PL-01471-…-leaf-plan.md`. Its Goal, three doors plus one test gap:
(a) a Model is approved while its custom objective is not (FD-1469, `02` R4); (b) `compile_bundle` stops at the pin (FR-240 "transitively reachable");
(c) a `control`-intent Factor seeds a rateable table and the table compiles (FD-1422, FR-88); (d) the direct custom-objective pin refusal has no negative test;
(e) a `control` factor reaches a price through a `model_call` (FD 9639, DP-7: refuse only). The roadmap row is `#### SL-1472` in `docs/roadmap.md`.

**Requirement coverage, each id** (PL-1471 §Scope): `03` FR-240; `00` FR-20; `02` R4; `06` FR-359; `02` FR-88; `03` FR-230; `02` FR-163; `02` FR-205.

**Out of scope** (PL-1471 §Scope, quoted): "FR-240's other clauses (register row `FR-240 (F-W9-3)`, clauses (1)-(4)); FR-359's Admin override, which is built for no flag today …; a peril structure's models, a known gap named in T1 with FD-1456 (#980) as its owner …; custom evaluation metrics, which do not reach a price …; and neutralising a `control` factor in a priced GBM … This slice only refuses (DP-7)."

**RL-1470 versus the plan, each difference named at its site.** RL-1470 wins over PL-1471 §Spec texts (RL-1470 "What it obliges"). Differences: (1) the marker is "*(Amended 2026-10-08, `RL-1470`, FD …)*", dated by this slice's commit, not "2026-10-05"; (2) T5 is folded into T1 (RL-1470 Ruled 8), so there is no separate T5 application, and T1's marker carries `FD 9639`; (3) T2's seed-route text is RL-1470's, the plan names it and gives none; (4) T4 is extended for the `model_call` case; (5) layout: each text is one physical line, table cells hold no `|`. Ruled 7's lane is superseded by D1 (c) as re-ruled by the 2026-10-08 10:54:33 BST entry's (iii').

**Lane and serialisation.** Lane A after SL-1448 (#1236) on `compile.py` (J5); never beside a slice editing `compile_bundle`'s body. The base is the main that includes #1236, named in the front matter's `tree`.

**Contention (RL-1445 versus S3 #1243; RL-1263 versus S2 #1245).** As the GO accepted: no shared code file with S3 or S2; `03` distinct rows; regenerated `docs/contracts/openapi/generated.json` and `docs/INDEX.md` are rebuilt by whichever merges second; no plan dependency. Behaviour watch (GO condition (4)): a new compile refusal that reds S3's attribution or compile tests after S3 merges main is a STOP to the lead.

**Acceptance 9's cite** re-anchors to `docs/contracts/schemas/approval-request.schema.json:54`, the line holding `custom_objective_not_approved` at this base: PL 9616's slice (the deletion of that file, #1168) has not merged.

**Hand-offs** (PL-1471 §Hand-off): the register rows for FD-1422, FD-1469 and FD 9639 are the auditor's; FD 9639 and OQ 9630 (working ids) are not built here (neutralisation is not built); FR-359's Admin override is built for no flag, and whoever builds it re-points `test_an_overridden_flag_never_reaches_compile` at it; `load_factor_by_ref` (SL-1391) may replace Task 3 Step 6's inline select if it is on main.

### 2. Task list

- [x] Task 0 — preconditions and exposure
- [x] Task 1 — (a) approval reds (Acceptance 1, 2) — red committed `b0024fea`; green in Task 4
- [x] Task 2 — (b)(d) compile reds, transitive check (Acceptance 3, 4, 8)
- [x] Task 3 — (c) control intent at compile and seed (Acceptance 5, 6, 7; the `rateable: false` case)
- [x] Task 3b — (e) `model_call` over a `control` GBM (Acceptance 13; DP-7)
- [x] Task 4 — (a) the flag (Acceptance 1, 2, 9)
- [x] Task 5 — frontend half: no exhaustive `dataset_invalidated` switch exists outside the untracked generated client (build log, Task 5); the frontend half ran in gate 1 and gate 2, install, generate:api, lint, type-check, test, build all rc 0 (section 3)
- [x] Task 6 — T1 to T4 verbatim from RL-1470
- [x] Task 7 — gate and this ledger; SL-1472 row status; INDEX regenerated (gate 2 at `d06b9d1e`, section 3; minted as LG-1533 in the mint commit)

### 3. Gate

| # | Command | rc | tree | slot / time |
|---|---|---|---|---|
| 1 | ruff check . | 0 | `7e1f44d3` | gate-1, 13:32 to 14:16Z |
| 1 | mypy | 0 | `7e1f44d3` | same run |
| 1 | lint-imports | 0 | `7e1f44d3` | same run |
| 1 | audit-docs | 1 (check 31 only) | `7e1f44d3` | same run |
| 1 | req-coverage | 0 | `7e1f44d3` | same run |
| 1 | generate-contracts --check | 0 | `7e1f44d3` | same run |
| 1 | pytest -q | 1: 15 failed, 5116 passed, 4 skipped (42m35s) | `7e1f44d3` | 13 check-31, 2 this slice's (fixed) |
| 1 | frontend: install, generate:api, lint, type-check, test, build | 0, 0, 0, 0, 0, 0 | `7e1f44d3` | same run |
| 2 | ruff check . | 0 | `d06b9d1e` | gate-1, 2026-10-08 15:03:58Z to 15:49:13Z; stages run serially in the body; flock rc 0 |
| 2 | mypy | 0 | `d06b9d1e` | same run |
| 2 | lint-imports | 0 | `d06b9d1e` | same run |
| 2 | audit-docs | 1 (check 31: gap between 1487 and 9475 only) | `d06b9d1e` | same run |
| 2 | req-coverage | 0 | `d06b9d1e` | same run |
| 2 | generate-contracts --check | 0 | `d06b9d1e` | same run |
| 2 | pytest -q | 1: 13 failed, 5118 passed, 4 skipped (42m30s) | `d06b9d1e` | the 13 are the check-31 working-id set; py half ended 15:47:31Z |
| 2 | frontend: install --frozen-lockfile, generate:api, lint, type-check, test, build | 0, 0, 0, 0, 0, 0 | `d06b9d1e` | frontend ended 15:49:13Z |

`fuser /tmp/slots/gate-1` inside the slot, before release: `1775649 1775650` (the `flock` process and its `bash` child); after release: no output, rc 1. The 13 check-31 tests fail only on the unminted working id `9475` (the gap 1487 to 9475); they pass once the ids are minted. A later commit changes only this ledger and `docs/INDEX.md`.

### 4. Audit

**Gate 2 (slot `gate-1`, tree `d06b9d1e`, 2026-10-08 15:03:58Z to 15:49:13Z).** Rc table in section 3: ruff, mypy, lint-imports, req-coverage, generate-contracts --check rc 0; audit-docs rc 1 (check 31, the gap between 1487 and 9475 only); pytest -q rc 1 with 13 failed, 5118 passed, 4 skipped, the 13 being the check-31 working-id set; frontend six stages rc 0.

**Audit and verdicts.** Slice audit by `auditor-sl1472`: `handover/audit-sl1472-2026-10-08.md` (local, not in the repository), at head `39178d0c9a77e132a2494d7e52b32a0d2bd673a2`, range `origin/main...39178d0c9a77e132a2494d7e52b32a0d2bd673a2`. Result: **PASS**, adopted by the lead in the entry headed "2026-10-08 16:59:56 BST — SL-1472 (#1247) SLICE AUDIT (auditor-sl1472, handover/audit-sl1472-2026-10-08.md) at 39178d0c — LEAD VERDICTS" (`~/gi-pricing-plan.local/channel/from-lead-2026-10-08.md`, local), subject to F1 and F2 at the mint.

The maintainer-duty items of the 15:19:09 BST ruling (item 2), verified by the lead from the code:
- (a) The `_refuse_*` helpers are defined at `packages/pricing-core/src/pricing_core/rating/compile.py:617`, `:643` and `:666`; their callers are only `:757`, `:758` and `:759` in `compile_bundle` (the other hits are three string keys at `packages/pricing-core/tests/test_quote_input_raise_sites.py:86`, `:88` and `:90`). None reads authored step text (`EXPRESSION_FIELDS`, `authored.py:44-51`, is untouched; the `_field_reads` guard is green). The rename stands; no registration.
- (b) The exempted raise sites `:636`, `:659` and `:686` carry pinned-artifact refs only; `compile_bundle` has no `QuoteContext` or scoring input. The exemptions stand; no sentinel.

Findings and the lead's verdicts:
| # | Sev | Finding | Verdict |
|---|---|---|---|
| F1 | MED | Merge conflict in `docs/INDEX.md` and `docs/roadmap.md` (the activation note against main's SL-1503 block) | FIX at the finisher's main merge: INDEX regenerated, the note kept under SL-1472, SL-1503 after it. Done in the merge commit. |
| F2 | LOW | This ledger's stale lines: Tasks 5 and 7 unchecked, section 4 "Not yet run", no PR number | FIX in the mint commit. Done here. |
| F3 | LOW | Task 3b's reds not committed separately (disclosed; the auditor re-verified at base) | ACCEPT |
| F4 | LOW | Task 0 exposure counts are vacuous (disclosed) | ACCEPT |
| F5 | LOW | `flags_for` calls `resolve_ref`, which can 404 on a dangling objective ref, and adds one query per read | ACCEPT. Evidence, verbatim: "custom_objectives.py on main has 8 routes, GET/POST only (lines 170/233/293/308/340/387/406/434), no DELETE — a dangling ref is unreachable through the API". |
| F6 | INFO | The gate-2 log has no tree stamp (the tree claim rests on the ledger-only diff, verified) | ACCEPT |

Also verified by the lead: red-first at the merge-base source (`test_rating_compile_fr240` 7 failed, 4 controls pass; `test_fr240_governance` 6 failed, 3 by-design passes; 79 passed at head); PL-1471 acceptance 13 of 13 (item 10 vacuous, disclosed); write set 18 files; spec texts equal RL-1470 byte for byte; contracts 46 match.

### 5. Build log

**Task 0 (2026-10-08, base `680fb9ac`).**
- `uv sync --all-packages` rc 0. Own test database `gipricing_sl-1472_7e17b68f`, made `createdb -T gipricing`; `alembic current` = heads = `f3a7c1d9e2b4`.
- Slots `gate-1` and `gate-2` free at 12:07 UTC; no pytest or vitest running.
- Anchors re-counted at base with `grep -cF -- '<find string>' <file>`, all **1**: T1 `The message names the step and the rung.)* |` (`03:137`); T2 cell `A hand-authored table may still have several keys (FR-228). |` (`03:121`); T2 route row (`03:936`); T4 `` `RATE_TABLE_KEY_DUPLICATE`, `CONTROL_FACTOR_IN_RATEABLE_PATH`, `PIN_NOT_APPROVED`, `` (`03:968`); T3 ``itself `approved`** (FR-20).`` (`02:50`). No STOP.
- Line drift against the readiness table, re-read at base: `flags_for` `:1075`; `ARTIFACT_FLAGGED` detail `:1370`; `seed_from_model` `:173`, `bound = pinned[0]` `:211`; `_Resolver` `:486`, final `NOT_FOUND` `:592`; `RATING_ERROR_CODES` `:309`; `ModelFlag` `:1984` unchanged. **Moved by SL-1448 (#1236):** `compile_bundle` `:573` → `:613`, `ResolvedArtifact` `:434` → `:474`. `CONTROL_FACTOR_IN_RATEABLE_PATH` appears in no `.py` under `backend/` or `packages/`.
- **DP-6 counts**, in `gipricing` and the own test database only (item 40). Query (i): `select count(*) from models m join custom_objectives o on o.workspace_id = m.workspace_id and 'custom_objective:' || o.slug || '@' || o.version = m.spec->'objective'->>'ref' where m.status = 'approved' and m.spec->'objective'->>'kind' = 'custom' and o.status <> 'approved'`. Query (ii): `select count(*) from rate_table_versions v, jsonb_array_elements(coalesce(v.definition->'keys','[]'::jsonb)) k join factors f on 'factor:' || f.slug || '@' || f.version = k->>'factor_ref' where f.body->>'intent' = 'control'`. Result: `gipricing` (i) 0, (ii) 0; own database (i) 0, (ii) 0. **Both counts are vacuous**: each database holds 18 models, 0 `custom_objectives` and 0 `rate_table_versions`, so no row of the shape existed to match, and the `ref` / `factor_ref` row shapes could not be read from a row. The join uses the `ArtifactRef` wire form `{type}:{slug}@{version}` (`packages/model-schema/src/model_schema/refs.py`). No bad row, so no DP-6 STOP; nothing reset or deleted. The lead accepted the zeros as vacuous.
- Open PRs read at base: #1214 and #1216 (RL 9491 / PL 9494, the FR-240 row) unmerged, so T1 applies first as the plan expects; #1243 (S3), #1245 (S2), #1240 (RFC 9479) open. Nothing merged on FR-240, R4, FR-230 or `compile.py` since the base.

**Task 1 reds (test module `backend/tests/test_fr240_governance.py`, 2026-10-08, own database).**
- `test_a_model_whose_custom_objective_is_in_review_cannot_be_approved`: `Failed: DID NOT RAISE PlatformError` at the `apply_approval_decision` call (the approval went through, FD-1469 §3's cause).
- `test_flags_for_names_an_unapproved_objective`: `AttributeError: type object 'ModelFlag' has no attribute 'CUSTOM_OBJECTIVE_NOT_APPROVED'`.
- `test_an_approved_objective_can_be_approved` (control): passes at the base.
- Fixture note: the objective is set `approved` only through `mark_approved` (the `06` FR-351 trigger refuses `UPDATE … status='approved'` from raw SQL); the `review` state is a SQL update from the `certified` the real certify Job leaves.

**Task 2 (red `8de52c7b`, green below).**
- Reds at base: `packages/pricing-core/tests/test_rating_compile_fr240.py::test_an_unapproved_objective_reached_through_a_pinned_model_is_refused[certified]`, `[review]`, `[deprecated]` each `Failed: DID NOT RAISE ValueError`; `backend/tests/test_fr240_governance.py::test_an_overridden_flag_never_reaches_compile`: `AssertionError: assert <JobStatus.SUCCEEDED: 'succeeded'> is <JobStatus.FAILED: 'failed'>`. Green at base, as planned: the approved case, the builtin case, and `test_a_version_pinning_an_unapproved_custom_objective_fails_to_compile[certified|review]`.
- Green: `_refuse_unapproved_objectives` (first named `_check_reachable_objectives`; renamed, see the gate section below) in `compile.py`, called after the pin loop. `test_rating_compile_fr240.py` and `test_rating_compile_bundle.py`: 15 passed; the backend compile tests: 3 passed.
- **Acceptance 8, broken-input proof.** With `*version.pins.custom_objectives,` deleted from `all_refs` in a scratch edit, `test_a_version_pinning_an_unapproved_custom_objective_fails_to_compile[certified]` and `[review]` both failed: `AssertionError: assert <JobStatus.SUCCEEDED: 'succeeded'> is <JobStatus.FAILED: 'failed'>` (`test_fr240_governance.py:197`). The line was restored from a saved copy and is not in the commit. The override test's `mark_approved` stands in for FR-359's unbuilt override, as its docstring says.

**Task 3 and 3b (red `0528b79b` for Task 3; Task 3b's reds were run in the tree with Task 3's code and before 3b's; both greens in `9f13825c`).**
- Reds at base for Task 3 (red commit `0528b79b`): `test_seeding_from_a_control_factor_is_refused` `Failed: DID NOT RAISE ValueError`; `test_a_pinned_table_keyed_on_a_control_factor_is_refused[True]` and `[False]` each `Failed: DID NOT RAISE ValueError` (`[False]` is the DP-4 `rateable: false` case, red by the same cause); `test_the_seed_route_refuses_a_control_factor_with_its_code` `assert 201 == 422`; `test_a_compile_over_a_control_keyed_table_fails_with_its_code` `assert <JobStatus.SUCCEEDED> is <JobStatus.FAILED>`. Green at base: `test_a_table_keyed_on_a_risk_factor_compiles`.
- Reds for Task 3b, seen before its code was written (Task 3's code was in the tree): `test_a_model_call_over_a_gbm_fitted_on_a_control_factor_is_refused` `Failed: DID NOT RAISE ValueError`; `test_a_compile_over_a_gbm_fitted_on_a_control_factor_fails_with_its_code` `assert <JobStatus.SUCCEEDED> is <JobStatus.FAILED>`. Control `test_a_model_call_over_risk_factors_compiles` green. These two were not committed red apart from the Task 3 code; the commit `9f13825c` carries 3b's tests and code together.
- Green: `CONTROL_FACTOR_IN_RATEABLE_PATH` in `RATING_ERROR_CODES`; the seed refusal after `bound = pinned[0]`; `_Resolver.resolve` has a `factor` branch and the `model` branch carries the model's Factors; `ResolvedArtifact.factors`; `_refuse_control_factor_keys`; `_refuse_control_factor_model_calls`. `SL-1391`'s `load_factor_by_ref` is not on main, so the inline select is used. Runs: pricing-core `test_rating_compile_fr240.py` + `test_rating_compile_bundle.py` 21 passed; backend `test_fr240_governance.py` + `test_model_lifecycle.py` + `test_rating_version_compile.py` 46 passed.
- One test-code correction after the red was seen: Task 1's `refused.value.status` is `status_code` on `PlatformError`; the red for that test was `DID NOT RAISE` first, and after Task 4 it reaches the corrected assert.

**Task 4 (`d84a5f96`).** `ModelFlag.CUSTOM_OBJECTIVE_NOT_APPROVED`, `flags_for` (dataset flag first, then the objective flag via `resolve_ref`), the `ARTIFACT_FLAGGED` detail names each flag with its own reason, `model.schema.json` `flags` enum and note, regenerated contracts, all in one commit (DP-1). `generate-contracts.py --check`: "46 generated contracts match the models"; `backend/tests/test_contracts.py`: 152 passed, 2 skipped. Task 1's three tests are green; `test_model_lifecycle.py` passes unchanged.

**Task 5.** `git grep -n dataset_invalidated -- frontend/src` finds no file outside `frontend/src/api/generated`, which is not tracked, so no exhaustive switch exists to break. The frontend half runs in the gate.

**Task 6 (`a3fb6237`).** T1 to T4 applied by script from the fenced blocks of RL-1470 §"The spec texts" with `<SL-1472 date>` = 2026-10-08, T5 folded into T1; each find string counted 1 before, and the result is one physical line per text. `python3 scripts/audit-docs.py`: only check 31's expected working-id gap (1487 to 9475).

**Pre-gate local checks (2026-10-08):** `ruff check .` clean, `mypy` "no issues found in 227 source files", `lint-imports` 4 kept, 0 broken. The full gate has not run.

**Gate 1 (slot `gate-1`, head `7e1f44d3`, 2026-10-08 13:32:02Z to 14:16:35Z, py half end 14:15:00Z).** Rc table: ruff 0, mypy 0, import_linter 0, audit_docs 1 (check 31, the 1487 to 9475 working-id gap only), req_coverage 0, contracts 0, pytest 1; frontend: install 0, generate:api 0, lint 0, type-check 0, test 0, build 0. pytest: 15 failed, 5116 passed, 4 skipped (42m35s). 13 failures are the expected check-31 working-id set. Two were this slice's:
- `test_rating_authored_fields.py::test_every_check_is_registered_and_validate_algorithm_iterates_the_registries`: `assert ['_check_cont..._model_calls'] == []`. The three new helpers were named `_check_*`, which that test requires to be registered with `validate_algorithm`. Renamed `_refuse_*` (commit `e55b6210`).
- `test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case`: `Left contains 3 more items` (the three new `_raise_named` sites).
**STOP and ruling.** The write set did not name `packages/pricing-core/tests/test_quote_input_raise_sites.py`; STOP to the lead, ruled in the entry headed "2026-10-08 15:19:09 BST — SL-1472 (#1247) STOP RULED: test_quote_input_raise_sites.py JOINS the write set (3 entries); the _check_ → _refuse_ rename and the 3 exemptions are each VERIFIED by the auditor from the code; full re-gate". That file joins PL-1471's write set for exactly the three `_INPUT_FREE` entries, each with a one-line why.
**For the auditor, from the code at the fixed head (file:line in `packages/pricing-core/src/pricing_core/rating/compile.py`).** Neither case the ruling names applies:
- Helpers do not inspect step text. `_refuse_unapproved_objectives` (def `:617`, sole caller `compile_bundle` `:757`) reads each pinned model payload's `spec.objective`. `_refuse_control_factor_keys` (def `:643`, sole caller `:758`) reads each pinned rate table payload's `keys[].factor_ref`. `_refuse_control_factor_model_calls` (def `:666`, sole caller `:759`) reads only `RatingModelCallStep.model_ref` and the resolved pin's `fit_result.feature_order`; no `expr`, `key_expr` or other authored string is read.
- Exempted raise sites carry no quote value. `:636` `_raise_named("PIN_NOT_APPROVED", f"{model_ref} uses {objective_ref}, which is {status!r}, ...")`: two artifact refs and a maturity status. `:659` `_raise_named("CONTROL_FACTOR_IN_RATEABLE_PATH", f"{table_ref} key {key.get('name')!r} is bound to {factor_ref}, ...")`: a table ref, the table's declared key name and a Factor ref. `:686` `_raise_named("CONTROL_FACTOR_IN_RATEABLE_PATH", f"{step.model_ref} was fitted on feature {feature!r}, the ... Factor {factor.slug}@{factor.version}, ...")`: a model ref, a fitted feature name from the model's `fit_result` and the Factor's slug and version. All three read pinned artifacts at compile time; none reads a `QuoteContext` or a scoring input.
- Entries: `test_quote_input_raise_sites.py` `_INPUT_FREE`, three lines, each commented with its arguments.

## PRs

SL-1472: the FR-240 family fix — #1247.
