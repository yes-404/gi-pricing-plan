---
id: LG-9475
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

# LG-9475 — SL-1472: the FR-240 family fix

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

**RL-1470 versus the plan, each difference named at its site.** RL-1470 wins over PL-1471 §Spec texts (RL-1470 "What it obliges"). Differences: (1) the marker is "*(Amended 2026-10-08, `RL-1470`, FD …)*", dated by this slice's commit, not "2026-10-05"; (2) T5 is folded into T1 (RL-1470 Ruled 8), so there is no separate T5 application, and T1's marker carries `FD 9639`; (3) T2's seed-route text is RL-1470's, the plan names it and gives none; (4) T4 is extended for the `model_call` case; (5) layout: each text is one physical line, table cells hold no `|`. Ruled 7's lane is superseded by D1 (c) as re-ruled by Ruling 2 (iii').

**Lane and serialisation.** Lane A after SL-1448 (#1236) on `compile.py` (J5); never beside a slice editing `compile_bundle`'s body. The base is the main that includes #1236, named in the front matter's `tree`.

**Contention (RL-1445 versus S3 #1243; RL-1263 versus S2 #1245).** As the GO accepted: no shared code file with S3 or S2; `03` distinct rows; regenerated `docs/contracts/openapi/generated.json` and `docs/INDEX.md` are rebuilt by whichever merges second; no plan dependency. Behaviour watch (GO condition (4)): a new compile refusal that reds S3's attribution or compile tests after S3 merges main is a STOP to the lead.

**Acceptance 9's cite** re-anchors to `docs/contracts/schemas/approval-request.schema.json:54`, the line holding `custom_objective_not_approved` at this base: PL 9616's slice (the deletion of that file, #1168) has not merged.

**Hand-offs** (PL-1471 §Hand-off): the register rows for FD-1422, FD-1469 and FD 9639 are the auditor's; FD 9639 and OQ 9630 (working ids) are not built here (neutralisation is not built); FR-359's Admin override is built for no flag, and whoever builds it re-points `test_an_overridden_flag_never_reaches_compile` at it; `load_factor_by_ref` (SL-1391) may replace Task 3 Step 6's inline select if it is on main.

### 2. Task list

- [x] Task 0 — preconditions and exposure
- [ ] Task 1 — (a) approval reds (Acceptance 1, 2)
- [ ] Task 2 — (b)(d) compile reds, transitive check (Acceptance 3, 4, 8)
- [ ] Task 3 — (c) control intent at compile and seed (Acceptance 5, 6, 7; the `rateable: false` case)
- [ ] Task 3b — (e) `model_call` over a `control` GBM (Acceptance 13; DP-7)
- [ ] Task 4 — (a) the flag (Acceptance 1, 2, 9)
- [ ] Task 5 — frontend half
- [ ] Task 6 — T1 to T4 verbatim from RL-1470
- [ ] Task 7 — gate and this ledger; SL-1472 row status; INDEX regenerated

### 3. Gate

| # | Command | rc | tree | slot / time |
|---|---|---|---|---|
| (the two halves, `CLAUDE.md` §11, each rc read directly) | not yet run | | | |

### 4. Audit

Not yet run. The auditor writes the result; scope is derived from the spec ids in section 1.

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

## PRs

SL-1472: the FR-240 family fix — the PR number is added at its opening.
