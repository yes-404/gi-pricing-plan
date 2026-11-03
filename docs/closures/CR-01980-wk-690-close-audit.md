---
id: CR-1980
family: closure
kind: work                     # work | phase | review — no other value (§1.2)
title: WK-690 Work close audit — expression custom objectives, SymPy derivation, the compilation target, expression Factors and the authoring view
status: active                  # write-once; this is the only value this family ever takes
created: 2026-11-03   # drafted 2026-11-03 under working id 8291
owner: auditor                  # work/phase kind; lead for `kind: review`
tree: c807a59d1a26d12e63d88bc395ac3dcc373aa919
phase: P2
work: WK-690
corrected_by: []
relates: [PL-1268, PL-1621, PL-1665, RL-1265, RL-1362, RL-1305, CR-1247, CR-1907, FD-1704, FD-1751, FD-1842]
---

# CR-1980 — WK-690 Work close audit

*Working id CR 8291, reserved by the lead; minted as CR-1980 at the lead's id turn. The auditor seat
aud-wk690 wrote this record on 2026-11-03, on the brief
`~/gi-pricing-plan.local/handover/brief-aud-g1close-2026-11-03.md` and its authority, the
maintainer's entries "2026-11-03 15:36:59 GMT" item 5 (the G1 close schedule) and
"2026-11-03 15:46:13 GMT" (full speed; earlier is not blocked) in
`~/gi-pricing-plan.local/channel/to-lead.md`. It follows `.claude/skills/close-workstream`,
`CLAUDE.md` §13 and §14.*

**What this record is.** It gathers evidence and **proposes**. Every §13 verdict below is
written "PROPOSED" and is the lead's to give. **The close is the user's dated acceptance line.**
This record does not close WK-690, and the roadmap row it edits says "close audit filed, acceptance
owed".

**Object.** `origin/main` at `c807a59d1a26d12e63d88bc395ac3dcc373aa919` (tree
`10b01c900d7303394ca514dcc7c631a85e699508`), read by `git ls-remote origin refs/heads/main` at
this audit's start. Every `file:line` and every count below is at that tree unless it names
another. Branch `docs/wk690-close-audit-2026-11-03`, cut from that commit.

## Scope

### §0. The requirement set, derived from the documents before any evidence

**Predicate** (runnable from the repository root at `c807a59d`). The union of the ids cited by
the WK-690 roadmap section (`docs/roadmap.md:1753`, up to the next `### WK-` heading at `:1901`)
and every plan with `work: WK-690` (`PL-1268`, `PL-1295`, `PL-1327`, `PL-1382`, `PL-1621`,
`PL-1665`):

```bash
( sed -n '1753,1900p' docs/roadmap.md
  cat $(grep -lE '^work: *WK-690' docs/plans/*.md)
) | grep -ohE '\b(FR|NFR)-[0-9]+\b' | sort -u -V
```

It prints **57 ids**. The section alone prints 29. The deliverable set is `PL-1268`'s "Core
scope — the ids this Work delivers" table (`PL-1268:186-216`), plus two ids appended after it:

- **FR-1840**, appended to `02` §3.7 by SL-1275 (`02-modelling.md:270`, `PL-1665` 5.1′). The
  predicate misses it: no plan names it, only the roadmap's SL-1275 row.
- **FR-244** (`03`), which SL-1271 carries for `RL-1265` DP-5 (the roadmap SL-1271 row).

That is **24 ids**: `02` FR-95, FR-144, FR-145, FR-146, FR-147, FR-148, FR-149, FR-150, FR-152,
FR-163, FR-165, FR-207, FR-208 (the `expression` arm), FR-1840, NFR-476, NFR-480, NFR-483,
NFR-484; `06` FR-366, FR-367; `07` FR-448, FR-449; `01` FR-36; `03` FR-244. The core table also
names five items with no id: `02` §4.6's profile table (OQ-1185), `02` §4.7's expression half,
`02` §5.3's Custom objective library, `01` §4.5's `expression` check, and `WF-702` Route B. They
are read in §1.

**Moved out of WK-690, each by a dated record (not this Work's verdicts):**

- FR-85, FR-86's field, FR-210 with FR-208's `spline` and `polynomial` arms, and FR-154's
  expression half: Phase 3 by `RL-1265` DP-1 (b) and DP-2 (b), recorded in the WK-690 section's
  2026-09-30 amendment (`roadmap.md:1765`). Owner the maintainer; event the P2 phase closure record.
- **FR-207's two `custom_objective_ref` residuals**: Phase 3 by `RL-1362` DP-S3-5, the `02` FR-207
  amendment of 2026-10-04 (`02-modelling.md:407`): "both `custom_objective_ref` residuals move
  from WK-690 to Phase 3, together, owned by the maintainer … The P2 phase closure record lists
  both for P3's first plan." **The WK-690 roadmap section does not record this move**; its
  2026-09-30 line lists only the `RL-1265` ids (§Findings, F2).
- FR-176, FR-177, FR-178: WK-1178 by FD-1195 (`PL-1268:244-250`).

The other 31 ids of the predicate are context: cited by a plan as a neighbour, a precedent or a
dependency (for example FR-151's template certificate, FR-113's relativity table, FR-97 and FR-98
under `PL-1665` 4.3′), and not owned by this Work.

**Requirements axis.** `scope-audit.py` takes one module per run. It is not a `run-heavy.sh`
command (`--light` admits only `audit-docs.py` and `doc-index.py`, rc 78), so it ran directly under
`nice -n 19`, through the `tools-main` venv, with the script in this worktree. Each log opens
`head=c807a59d…` and closes with its `rc=`:

```bash
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py MODEL --sections NONE \
  --extra FR-95,FR-144,FR-145,FR-146,FR-147,FR-148,FR-149,FR-150,FR-152,FR-163,FR-165,FR-207,FR-208,FR-1840,NFR-476,NFR-480,NFR-483,NFR-484
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py GOV  --sections NONE --extra FR-366,FR-367
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py PLAT --sections NONE --extra FR-448,FR-449
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py DATA --sections NONE --extra FR-36
uv run --directory .claude/worktrees/tools-main python <wt>/scripts/scope-audit.py RATE --sections NONE --extra FR-244
```

| Run | In scope | With a `@pytest.mark.req` marker | No marker | rc |
|---|---|---|---|---|
| MODEL | 18 | 16 (89%) | NFR-476, NFR-480 | 1 |
| GOV | 2 | 1 (50%) | FR-366 | 1 |
| PLAT | 2 | 2 | — | 0 |
| DATA | 1 | 1 | — | 0 |
| RATE | 1 | 1 | — | 0 |
| **Total** | **24** | **21** | **3** | |

A marker on an id is not evidence of WK-690's limb of it. Two ids are marked only on limbs that
are not this Work's: **FR-207** (markers in `test_ebm_spec.py`, `test_gbm_spec.py`,
`test_paired_quantile_models.py`, all other fields of the staged contract; WK-690's limb moved to
P3) and **FR-208** (markers in `test_glm.py:211`, `:232`, `:277` and `test_glm_scalar_predict.py:424`,
the refusals; the `expression` arm's resolution is evidenced under FR-95's markers, §1).

**Reconciliation with the roadmap.** The WK-690 row carries no count. `roadmap.md:3487` names
"the `MODEL` requirements WK-690 carries over (FR-95, FR-144/145/150 and the `expression` half
of §4.6/§4.7)", a planning summary, not a count.

**Endpoints axis.** `scope-audit.py MODEL --endpoints`: "declared: 45, published: 45 (100%) —
every declared endpoint is published in the contract". It includes `POST
/api/v1/custom-objectives/preview` (`02-modelling.md:1921`) and `/custom-objectives/{id}/derive`.

**Catalogue axis.** `02` declares no catalogue in the form the script reads: `grep -cE '^\|
`[A-Z]{2,4}-[A-Z]{2,4}-[0-9]+` [a-z0-9-]+' docs/specs/02-modelling.md` prints `0`.

## Evidence

### §1. Each deliverable: exists and works

"Works" means a test asserts the behaviour; the asserts were read, not the test names.

| Deliverable (PL-1268 core scope) | Exists, at `c807a59d` | Works: the assert read |
|---|---|---|
| Four profiles, `where()`, the strict refusals (FR-145, `02` §4.6, FR-36, `01` §4.5) | `pricing_core/data/expressions.py:41-47` (`GrammarProfile` `objective`, `factor`, `recipe`, `check`); strict and lenient node sets `:55-61` | `test_expression_profiles.py` (54 tests; FR-36 8, FR-145 3 markers); the arity and structure mutation controls, 12 and 6 failed (LG-1304:143-147) |
| Node and depth limits, all four profiles (FR-145, NFR-483) | `expressions.py:127-128` (`max_nodes: int = 200`, `max_depth: int = 20`) | `test_expression_limits.py` (5 FR-145 markers): 201 nodes and depth 21 refused ×4 profiles, 200 and 20 accepted (LG-1304:154-166) |
| SymPy at one pin, with its `skills-map.md` row (PL-1268 Acc. 3) | `uv.lock:2395-2396` (`sympy`, `1.14.0`); `pricing-core/pyproject.toml:19` (`"sympy==1.14.0"`); `docs/skills-map.md:67` | `grep -c -i '^name = "sympy"' uv.lock` prints `1` |
| SymPy derivation, the compiler, no `lambdify` (FR-144, NFR-483) | `modelling/expression_objective.py:100` (`derive`), `:217` (`compile_kernel`), `:292` (`compile_expression_objective`). `lambdify` appears only in two docstrings saying no string reaches it (`expression_sympy.py:4`, `expression_objective.py:5`) | `test_expression_sympy.py:93-94`: `simplify(piecewise_fold(diff(loss, f) − gradient)) == 0` and the hessian twin; FR-144 33 markers over 6 files |
| The expression certificate (FR-146 to FR-149, `02` §4.7 expression half) | `model_schema/objectives.py:816-817` (`symbolic_vs_numeric_gradient`, `_hessian`) | LG-1350 F3 mutation table (LG-1350:229-236): derivation-version, non-finite and division mutations each red. **FR-147/FR-148 on a real `where()`**: the Route B run certifies the §4.6 example with `branch_discontinuity` `warn` (LG-1412 A10 statuses); see §5 |
| The `expression` kind behind the flag; `/derive`; certification as a job (FR-144, FR-150, FR-448, FR-449) | `objectives.py:93` (`EXPRESSION`); `api/custom_objectives.py:342` (`/derive`); `platform/settings.py:290`, `:341` (`"features.expression_objectives_enabled": False`) | `test_wf702_route_b.py:145-161`: flag at its default, create **409 `OBJECTIVE_KIND_NOT_ENABLED`**, and preview the same |
| `custom_objective:author`, checked, in no built-in role (FR-366, FR-367; PL-1268 Acc. 8) | `model_schema/permissions.py:47` | `test_custom_objectives.py:772-850` (403 without author on create and derive; author without `model:fit` refused); `test_rbac.py:530-534` (`CUSTOM_OBJECTIVE_AUTHOR not in permissions` for every built-in role); template create with `model:fit` alone 201 (`test_custom_objectives.py:851-860`) |
| Non-convex expression: the extra Approver (FR-152, FR-163) | `platform/objectives.py` `submit_for_review` (`additional_approvers=1` on `violated`, register FD-1511 row) | `test_wf702_route_b.py:111-142`: `convexity` `violated`, `certified_with_findings`, `review` after the first approval, `approved` and `approvers_recorded == 2` after the second |
| Per-round budget, NaN/inf abort (FR-165) | `modelling/objectives.py` (`_finite_or_abort`) | FR-165 16 markers; LG-1350 F3 row 5: the abort removed, 2 failed |
| `expression` Factors (FR-95, FR-208 `expression` arm) | `model_schema/modelling.py:99` (`FactorType.EXPRESSION`) | `test_expression_factors.py:117-243`: numeric unbanded refused naming FR-210; string banded refused; numeric banded resolves through `apply_banding` (`youngest == ["9-18"]`); string unbanded is categorical; a GLM on each recovers its relativity table with one base. Every test asserts the new fields first (`_require_the_new_fields`, `:101-109`), an assert, not a skip |
| Audit events (NFR-484) | — | `test_custom_objectives_expression.py` (1), `test_expression_factors_api.py` (2), `test_model_nfrs.py` (3) markers |
| The preview route (FR-1840) | `api/custom_objectives.py:8` (route table), `platform/objective_preview` | `test_objective_preview_api.py` (7), `test_objective_preview.py` (10): over-bound 422 before SymPy, red at `d96b33f8` (LG-1839:55) |
| The authoring view (`02` §5.3) | `frontend/src/views/ObjectiveEditorView.vue`, `components/ObjectiveLossCurve.vue` | `views/__tests__/ObjectiveEditorView.test.ts`, `ObjectiveLibraryView.test.ts`, `components/__tests__/ObjectiveLossCurve.test.ts`; frontend half green at the S5 re-gate (LG-1839:61) |
| `WF-702` Route B over HTTP (PL-1268 Acc. 7) | `backend/tests/test_wf702_route_b.py` | `:60-142`: grammar refusal `200 ok: false`; create 201 `draft`; derive (`derivation_tool == "sympy"`, gradient and hessian present); certify 202; `certified_with_findings`, `convexity` `violated`; submit `review`; two non-author approvals to `approved` |

### §2. The gate

**Gate of record per slice.** Each slice's squash commit is an ancestor of `c807a59d`
(`git merge-base --is-ancestor <sha> c807a59d`, rc 0 for all six).

| Slice | Squash on main | The gate of record (its ledger) |
|---|---|---|
| SL-1271 (#981) | `bd67fb51` | re-run: pytest 4037 passed, 3 skipped (LG-1304:323); MERGE-ACK to-lead "2026-09-30 14:18:02 BST" |
| SL-1272 (#1025) | `8933a29e` | GATE pass, 7 of 7 stages, pytest 4367 passed, 3 skipped (LG-1350:251); MERGE-ACK "2026-10-01 02:28:14 BST" at head `6c8fa255` |
| SL-1273 (#1122) | `36a9f483` | re-gate at `76897a8b`: every stage 0, pytest 4911 passed, 3 skipped (LG-1412:497-510); MERGE-ACK "2026-10-05 11:44:43 BST" at `4f0a0682` |
| SL-1622 (#1295) | `2a819741` | pytest 13 failed = the check-31 working-id set, audit-docs check 31 only, every other stage 0; the lead accepted check-31-only (LG-1680:73); MERGE-ACK "2026-10-12 08:07:03 BST" |
| SL-1274 (#1344) | `d87dd259` | re-gate at `ebcb6eaa`: pytest 13 failed = the working-id cascade set, audit-docs check 31 only, the rest 0 (LG-1817:361, `:383`); MERGE-ACK "2026-10-18 19:07:51 BST" at `2cb4526b` |
| SL-1275 (#1359) | `71e481fa` | re-gate at `96354f9c`: Python and frontend halves all rc 0, pytest 6662 passed, 13 skipped (LG-1839:61); MERGE-ACK "2026-10-22 16:35:15 BST" at `ebe33925` |

**Fresh full gate: OWED** — the lead schedules it; head = this record's branch head at that
time. This audit ran no test, no build and no gate (the brief's ban).

**Retry counters** (`write_runtime_state.py show`): one WK-690 entry, `slice:SL-1273:fix` count 1
(a minted-head gate red at `9963f22d`, 2026-10-05T09:41:21Z). The block was last written at
`2026-10-05T13:09:09Z`, before S4, S5 and SL-1622 ran, so "none recorded" for those is not
evidence of a clean first pass.

### §3. New checks proven on broken input

Ancestry: `git merge-base --is-ancestor <red> <the MERGE-ACKed PR head>` rc 0 for each.

| Check | Red, and the red line | Reaches |
|---|---|---|
| The node and depth limits (FR-145) | `4b5bc5e1` (Task 2 counter) precedes enforcement; red 2: a measuring-only stub, **9 failed, 10 passed**, every refusal `DID NOT RAISE ExpressionError`, the accept cases as positive control (LG-1304:157-161) | `46296464` (#981 head) |
| The profile refusals and the arity check (FR-145, FD-1294) | red at `9f63d0fe` (LG-1304:131); mutation controls on the finished code, arity off 12 failed, `_check_structure` off 6 failed (LG-1304:143-147). **The intermediate red was replaced by mutations**, a disclosed plan deviation (LG-1304:250-255) | `46296464` |
| The certificate's version, non-finite and denominator checks (FR-146, FR-165) | LG-1350 F3 mutations at `ee5de443`: 2, 2 and 3 (corrected to its own count) failed, plus a live positive control (LG-1350:229-238) | mutations on the worktree, not commits; reverted |
| The `expression` kind, schema half | red at base `663433e4` (LG-1412:90) | `4f0a0682` (#1122 head) |
| The extra Approver on `violated` (FR-152, FD-1511) | red at `5af9d321`, `test_objective_submission.py:353` (LG-1412:384) | as above |
| The certificate check-name guard (FD-1349) | five names set to `"BOGUS"`, `AssertionError: authored enum vs code vocabulary differ`, `1 failed`, then restored, `1 passed` (LG-1680; register FD-1349 row) | mutation on the worktree |
| Expression Factor diagnostics omission (DP-1274-DIAG) | red-first commit `d88d2218` (LG-1817:184) | `2cb4526b` (#1344 head) |
| The preview's 3a bound (FR-1840) | red at `d96b33f8`: `4 failed, 10 passed`, `assert 200 == 422` (LG-1839:55) | `ebe33925` (#1359 head) |

**PROPOSED:** the R2 limb of SL-1275 (403 without `model:fit`; the executor separation test) is
**delivered but not proven red-first**, as LG-1839:58 discloses. The permission-parity check is
WK-1178's (SL-1360, `d8537220`), not this Work's.

### §4. NFRs

| NFR | State |
|---|---|
| NFR-476 (expression overhead ≤ 25 % against the builtin) | **Measured, near bound, no verdict** at 1 M × 60 × 100 trees: run 1 (N=3) median 1.273 [1.166, 1.338]; run 2 (N=7) median 1.255 [1.215, 1.290], load 3 to 4 (LG-1350:172-196, command `scripts/bench-model.py --only expression`). The full shape (5 M × 60 × 500, N ≥ 3) goes to a dedicated host. **Not on nfr-bench-1's carried list** (to-lead "2026-11-03 15:33:28 GMT"'s re-dated plan: SL-1736 5a, SL-1569 NFR-502, NFR-1443, NFR-485, SL-1367 Task 4). PROPOSED: **deferred to nfr-bench-1 (Thu 5 – Fri 6 Nov 2026), owner WK-690**, or carried under G4's host fallback |
| NFR-480 (certification < 3 min with the smoke fit) | **Measured, met**: median 1.174 s of 5 runs, range 1.063–2.104 s, load 0.57–1.36, command verbatim at LG-1412:465-467 (`scripts/bench-expression-certify.py`), against 180 s (LG-1412:453-477). The timed span has no Job, DB or HTTP, as the ledger says |
| NFR-483 (never `eval`; position-accurate refusal; bounded) | Asserted by tests, 12 markers over 6 files, plus the limits (§1) |
| NFR-484 (derivation audited) | Asserted by tests (§1) |
| FR-1840 clause 3d (the preview's own latency budget) and `RL-1616` 3c (`/score` p99 under saturated previews) — `PL-1665` 5.7 | **Not measured.** FR-1840 reads "provisional until `PL-1665` 5.7 is measured in an ALONE window (owner WK-690)" (MERGE-ACK "2026-10-22 16:35:15 BST"). SL-1275 **closes only on this measurement** (LG-1839:69). **Not on nfr-bench-1's carried list.** PROPOSED: **deferred to nfr-bench-1 (Thu 5 – Fri 6 Nov 2026), owner WK-690**, if the lead reads the dedicated VM as the ALONE window `PL-1665` 5.7 requires |

### §5. Not delivered: every requirement without evidence, with a PROPOSED verdict

| Id | What is missing | PROPOSED §13 verdict |
|---|---|---|
| NFR-476 | a verdict at the full shape (§4) | **deferred with an owner: WK-690**, event the nfr-bench-1 run (Thu 5 – Fri 6 Nov 2026) or G4's host fallback |
| NFR-480 | no marker; measured and met (§4) | **delivered**, evidenced by measurement outside the marker instrument |
| FR-366 | no `FR-366` marker. Its live half ("`model:fit` governs template objectives") is asserted by `test_custom_objectives_api.py:486-497` (403 `PERMISSION_DENIED` without `model:fit`, marker FR-166) and `test_custom_objectives.py:851-860` (template create with `model:fit` alone 201, marker FR-367); its trigger half is discharged by FR-367 (`06-governance.md:147`, notes of 2026-08-18 and 2026-10-05) | **delivered, evidenced outside the instrument** (a marker line is cheap but not owed) |
| FR-207 (WK-690's limb) | `custom_objective_ref` on `GlmSpec` and `Model` | **reassigned**: Phase 3, owner the maintainer, by `RL-1362` DP-S3-5 (`02` FR-207, amended 2026-10-04); the P2 phase closure record lists both |
| FR-147, FR-148 on a real `where()` | marked only by template tests (`test_objectives.py`, 2 and 4 markers). The expression path's `branch_discontinuity` `warn` on §4.6's `where()` loss is recorded by LG-1412 A10's five runs, not asserted by a marked test | **delivered but untested** for the expression kind (the template tests exercise the same certificate code) |
| FR-1840 3c/3d | §4 | **deferred with an owner: WK-690**, event `PL-1665` 5.7 measured |

**The §5 retrofit-impossible list.** WK-690's invariants are among the list's consumers: model and
objective definitions are declarative JSON (the derived gradient and hessian are stored as
expression text, `PL-1268` Global Constraints), and no shape is hand-written (the frontend reads the
generated client). Nothing on the list lands here.

### §5a. Binding plan-review conditions

`grep -l 'kind: review'` over `docs/closures/`, then `grep -c WK-690` in each: CR-788, CR-925,
CR-1212, CR-1243 and CR-1247 name WK-690. CR-1907 does not.

| Condition | The artifact it demands | Where it is at `c807a59d` |
|---|---|---|
| CR-1247 Proposal 1 (c), accepted 2026-09-29: the decision-maker's `RL-` with the `06` amendment, and WK-1178's permission-parity check, both before WK-690 adds `custom_objective:author` | `RL-1305` (#989, `e9263283`) and `tests/test_permission_parity.py` (#1049, `d8537220`) | **Met.** Both are ancestors of `36a9f483` (#1122, which adds `CUSTOM_OBJECTIVE_AUTHOR`, by `git log -S'custom_objective:author' -- packages/model-schema/src/model_schema/permissions.py`): `merge-base --is-ancestor` rc 0 each |
| CR-1247 Proposal 4 / G4 host fallback | near-bound verdicts carried, no pass or fail claimed from the shared VM | Met for NFR-476: LG-1350 claims "no verdict" |
| CR-1212 Proposal 1 (e): WK-690 owns NFR-476, NFR-480, NFR-483 and NFR-484's expression limbs | each measured or carried | NFR-480, NFR-483, NFR-484 met (§4); NFR-476 owed (§5) |
| CR-1212 Proposal 2 (sequencing; WK-690 independent) | — | No artifact; sequencing only |
| CR-788, CR-925, CR-1243 | observations (CR-788: WK-690's scope row describes one capability) and a throttle, no WK-690 artifact | Nothing owed |

### §5b. The owed list, generated

```text
Generated by `python3 scripts/register-owed.py WK-690` against `c807a59d (`docs/wk690-close-audit-2026-11-03`)`.
Mode: work item 'WK-690'. 3 owed row(s), 6 matched but excluded as opening with a resolution marker
- The `factors` table is not append-only at the database … (FD-1704's row, register :367)
- The two per-factor GBM diagnostics read the first source column of a Factor … (FD-1751's row, register :385)
- The grammar refusal's structure walk raises RecursionError on a deeply nested loss, so the create path answers 500 (FD-1842) — deferred with an owner: WK-690
Excluded as opening with a resolution marker — verify:
- FD-1195, FD-1294, FD-1349, FD-1492, FD-1511, FD-1512
```

*(Titles shortened; the command reproduces the full output at this tree. `register-owed.py
review` at the same tree reports 29 owed rows, the replan check's evidence line.)*

**Each row, read by hand against `docs/findings/register.md`:**

| Row | Owner cell; Decision cell | PROPOSED |
|---|---|---|
| FD-1704 (:367) | **WK-1178**; "fix before close with an owner: WK-1178, as its own row (not WK-690 S4)" | **removed from WK-690's list**: the script matched the text "WK-690 S4" in the Decision cell; the row is WK-1178's |
| FD-1751 (:385) | WK-690; "deferred with an owner: WK-690, in P2: real diagnostics on the resolved expression column" | **open, owned by this Work.** Not fixed at `c807a59d`: `diagnostics.py:1081-1095` omits an `expression` Factor by name (`PermutationOmissionReason.EXPRESSION_FACTOR`) and `:1351` still reads `source_columns[0]` |
| FD-1842 (:410) | WK-690; "deferred with an owner: WK-690; … a merged fix with a red-first create-path test on a 2000-character unary chain, or a dated ruling accepting the absence" | **open, owned by this Work.** Not fixed: `platform/objectives.py:295-318` (`grammar_refusal`) catches `ExpressionError` and `SyntaxError` only; `git grep RecursionError -- backend/src packages/pricing-core/src` prints nothing |
| FD-1195, FD-1294, FD-1349, FD-1492, FD-1511, FD-1512 (excluded) | each Decision cell opens "**Resolved** <date> by <PR, sha>" | resolved; nothing residual read. FD-1294's dated discharge line (owed at the close by SL-1622) is in place: "Resolved 2026-10-12 by SL-1271 (#981, `bd67fb51`)" (:218) |

**Corrected owed list: FD-1751, FD-1842.** The script's three less FD-1704. A cross-check by
owner cell (`grep -n WK-690 docs/findings/register.md`, rows :182 :218 :281 :318 :326 :327 :343
:367 :385 :410) adds nothing: :343 is FD-1619, owner WK-1178 ("fix before close with an owner:
WK-1178, or carried to Phase 3"), the FR-244 restatement parity check that `PL-1665` 4.7's interim
evidence defers to.

**A WK-690 owner cannot carry its own finding past its own close.** Both rows name WK-690 as the
owner and a WK-690 event. PROPOSED, one of three per row (the lead's verdict): (a) **fix before
close**, a WK-690 fix row like SL-1622; (b) **carry forward with a new owner** (WK-1178, or P3 with
the maintainer, event the P2 phase closure record); (c) **accept** by a dated line.

### §5c. Workflow steps that cite this close's requirements

**Candidates**, at `c807a59d`:

```bash
git grep -n -o -E '\b(FR|NFR)-(36|95|144|145|146|147|148|149|150|152|163|165|207|208|244|366|367|448|449|1840|476|480|483|484)\b' -- 'docs/workflows/WF-*.md'
```

It prints 37 (line, id) pairs, at `WF-698:44` (FR-36) and `:153` (FR-95), and 35 in `WF-702`. Each
step was read, and each cited requirement was read to its end with its dated amendments
(`01-data-management.md:93`; `02-modelling.md:98`, `:244-246`, `:250`, `:252`, `:263`, `:265`,
`:270`, `:3032`, `:3036`, `:3039`; `07-platform.md:175-176`). The read was delegated to a
subagent; the five disagreements below were re-read by this auditor at the lines named.

**Still says it (32 pairs):** WF-698 A4 (FR-36), WF-698 §9 C (FR-95); WF-702 opening note
(FR-163), §1 precondition (FR-150, FR-448, FR-449), A5 (FR-146), B1.1, B1.2, B2.1 (FR-144), B1.4
(FR-145, NFR-483), B2.5, B2.6, B3.6 (FR-152), B3.1 (FR-146), B4.6, D2, D6 (FR-163), C3 (FR-144,
NFR-483), C4 (FR-165), §7 rows at `:174` (FR-145), `:176` (FR-146), `:177` (FR-152), `:182`
(FR-165), §9 at `:203` (NFR-483), `:205` (NFR-480), `:206` (FR-163), §10 at `:217` (NFR-480).

**Disagrees (5 steps):**

| Step | Id | The step | The requirement, as amended |
|---|---|---|---|
| B1.4 (`WF-702:86`) | FR-1840 | "Parses on every keystroke via a restricted AST walk" — and, in its own 2026-10-21 citation, "the frontend parses nothing itself" | FR-1840 (2026-10-21): the live parse is served by the preview route. **The step contradicts its own citation**; the first sentence was not struck |
| B1.5 (`:87`) and §7 (`:173`) | FR-1840 (FR-145 cited) | "rejected with `OBJECTIVE_GRAMMAR_VIOLATION`" | FR-1840: the editor's parse failure is "200 with `ok: false`"; FR-150 (2026-10-04) gives 422 `OBJECTIVE_GRAMMAR_VIOLATION` on create. The step does not say which surface it describes |
| B4.2 (`:121`) | FR-152 | "convexity `violated` triggers the two-approver rule from the Approval Policy" | FR-163 (2026-10-04, `RL-1362` DP-S3-4): "the policy's Approvers plus one … at the default policy that is two"; no policy key sets the increment |
| C5 (`:137`) and §7 (`:181`) | FR-165 | the abort names "the round and the offending input range" | FR-165 (2026-09-30, `RL-1328` DP-S2-3/4): the text "names the round, the row count and the fields `y` and `f`, and no value: the offending ranges are structured attributes of the error" |
| §10 C first fit (`:219`) | NFR-476 | "+≤ 25 % for a custom objective" | NFR-476: a custom **`expression`** objective, against the equivalent builtin |

Which side is wrong is `CLAUDE.md` §0's question. Each is an FD candidate for the lead (this
record mints no id). Not checked: the legacy module-scoped id forms at `WF-702:202-208` (audit-docs check 36 lists them), which the
predicate does not match.

## Findings

- **F1 — SL-1275 is merged and `active`.** #1359 (`71e481fa`) merged 2026-10-22; the SL-1275 row
  (`roadmap.md:1863`) and LG-1839 read `active`, on the maintainer's B4 ruling ("2026-10-22
  00:57:13 BST", merge-then-measure). **Closing act owed:** the `PL-1665` 5.7 measurement, then
  the SL-1275 and LG-1839 status flips. Not in docs batch 6's list (SL-1956/1971/1962/1966/1968).
- **F2 — the WK-690 roadmap section does not record FR-207's move to P3.** Its 2026-09-30 line
  (`roadmap.md:1765`) lists FR-85, FR-86's field, FR-210 with FR-208's arms, and FR-154's
  expression half. FR-207's `custom_objective_ref` pair moved on 2026-10-04 (`RL-1362` DP-S3-5),
  and the SL-1273 title still names FR-207. A dated line is owed so the P2 phase closure record
  finds it from the roadmap as well as from `02`. It moves no scope (the move is already ruled).
- **F3 — the SL-1274 row still reads "MERGE-ACK: not yet given"** (`roadmap.md:1855`). The
  MERGE-ACK is the maintainer's "2026-10-18 19:07:51 BST" (#1344, head `2cb4526b`), and #1344
  merged as `d87dd259`. A stale status sentence; a dated line is owed.
- **F4 — two WK-690 measurements are not on nfr-bench-1's carried list**: NFR-476's full shape
  and `PL-1665` 5.7 (§4). Without them SL-1275 cannot close, and WK-690 cannot close.
- **F5 — `register-owed.py WK-690` lists FD-1704, whose owner is WK-1178**, because the text
  "WK-690 S4" appears in its Decision cell. The known defect (a mid-cell "Resolved") is a
  different one. A process finding: a dated `process-backlog.md` row, not an `FD-`, since a
  hand-read catches it and no wrong merge or number follows.

## Replan check (`CLAUDE.md` §14, `RFC-1248`)

1. **Completion — yes.** The scope audit adds FR-1840 and FR-244 to `PL-1268`'s table, and finds
   FR-207's limb moved to P3 without a roadmap line (F2). Neither moves scope now.
2. **Omission — yes.** Two measurements the Work needs to close are on no schedule (F4).
3. **Skills and research — yes.** `register-owed.py` matches an owner by text mention (F5). It
   does not move scope.
4. **Drift — yes.** The roadmap's SL-1274 row is stale (F3), FR-207's move is not in the WK-690
   row (F2), FR-1840 3d is a provisional budget, and five `WF-702` steps disagree with their
   requirements (§5c). None moves a slice or phase.
5. **Shape — no.** No phase boundary or Work scope moved since CR-1907 (2026-10-25); FR-207's move
   (2026-10-04) predates it.

`register-owed.py review` at `c807a59d`: **29 owed rows** (11 excluded as opening with a
resolution marker).

**Triggers:**

- A phase boundary or Work scope moved: **not fired**.
- An exit criterion at risk: **fired**. G1 needs WK-690 closed by the user's dated line. SL-1275
  waits on a measurement with no booked window (F4), and FD-1751 and FD-1842 are open and owned by
  WK-690 itself. The code freeze is Tue 10 Nov 2026 and the exit demo Wed 18 Nov 2026 (the user's
  re-dating, to-lead "2026-11-03 15:38:58 GMT").
- A replan decided: **not fired**.
- A finding that moves a slice or a phase: **not fired**; moving FD-1751 or FD-1842 to P3 would
  fire it, if the lead chooses (b).

**PROPOSED:** no separate full review now. The fired line is carried to the §14 review before the
P2 exit demo (the week of Mon 16 Nov 2026), on two conditions: the lead names a resolution for
FD-1751 and FD-1842, and books the two measurements. **The verdict is the lead's.**

## Verdict

PROPOSED: **not ready for acceptance at `c807a59d`.** The deliverables exist and work: 21 of 24
ids carry a marker, every `PL-1268` core item has a read assert (§1), and every slice's gate of
record stands with its MERGE-ACK (§2). The close is blocked by:

1. FD-1751 and FD-1842, open and owned by WK-690 (§5b);
2. `PL-1665` 5.7 (FR-1840 3c/3d) and NFR-476's full shape, unmeasured and unscheduled (§4), and
   SL-1275's closing acts that follow the first;
3. the fresh full gate (OWED).

The §5 verdicts are proposals. **The close itself is the user's dated line.** The WK-690 row
reads "close audit filed (CR-1980), acceptance owed" until then.

**Disclosure: the INDEX regeneration shows PL-1295, PL-1327 and PL-1382 as `closed`.** Their
derived column read `executed` at `c807a59d` and reads `closed` once this record exists, because
`scripts/doc-index.py` derives a WK-690 leaf plan as closed when any `CR-` with `work: WK-690`
exists (the same effect CR-1952 disclosed for WK-675). **That is not an acceptance of WK-690**,
and the INDEX is generated, not hand-edited. The `status:` field of each plan is unchanged
(`active`).
