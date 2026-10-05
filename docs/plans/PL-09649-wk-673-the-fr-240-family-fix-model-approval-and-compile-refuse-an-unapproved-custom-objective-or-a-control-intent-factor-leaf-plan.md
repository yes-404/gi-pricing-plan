---
id: PL-9649
family: plan
kind: leaf
title: WK-673 — the FR-240 family fix, model approval and compile refuse an unapproved custom objective or a control-intent factor (FR-240, FR-88, R4): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: planner
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1263, RL-1329, SL-1409, PL-1408]
---

# PL 9649 (working id) — WK-673: the FR-240 family fix, leaf plan

Filed under working id 9649 (this plan) and slice working id 9647 (its `SL-` row under WK-673 in
[`../roadmap.md`](../roadmap.md), `draft`). The lead reserved both
(`~/gi-pricing-plan.local/handover/eta.md`, rows "PL 9649" and "SL 9647", 5 Oct 14:12:57). The
findings are **FD 9697** (working id, draft PR #1136 at `1649e360`) and **FD 9659** (working id,
draft PR #1142 at `52a68d0f`). Everything below was read at `origin/main`
`83ea509023d6d705d6f78fe74b7124fdf1375739` on 2026-10-05, unless a line says otherwise. **No test
was run at planning time**: the reds below are predicted from the code read and from the two
findings' reproductions, which the auditor ran (FD 9697 §Evidence 1; FD 9659 §Evidence 1 and 3).

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: every red is seen red, by its stated cause, before the code that turns it green.
> - `python-test`: the `req` marker and negative tests.
> - `python-package`: `pricing-core` stays free of FastAPI and the database; a shape lives in `model-schema` once.
> - `contract-schema` and `contract-guard`: Task 4's `ModelFlag` member and `model.schema.json`.
> - `spec-change`: Task 6, the texts verbatim from the ruling.
> - `dev-commands`: the two-half gate, `uv sync --all-packages` in a fresh worktree, and
>   `alembic current` equal to the heads on the worktree DB before any backend test (the maintainer (by delegation),
>   2026-10-05 14:09:21 BST, item 4).
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

Three doors are open today, and FR-240 (`docs/specs/03-rating-engine.md:137`) and `02` R4
(`docs/specs/02-modelling.md:49-50`) say each must be shut:

1. **A Model is approved while its custom objective is not** (FD 9659, measured in its §3:
   `OBJECTIVE_STATUS review` / `SUBMIT ok` / `APPROVAL ok` / `MODEL_STATUS approved`). R4: *"A Model
   using a Custom Objective can only reach `approved` if that objective is itself `approved`"*
   (FR-20). `apply_approval_decision` (`backend/src/app/platform/modelling.py:1284`) refuses only
   when `flags_for` (`:1049`) returns a flag, and `flags_for` computes `dataset_invalidated` alone
   (`:1063-1065`). `packages/model-schema/src/model_schema/objectives.py:174-178` says such a model *"simply cannot be approved until the
   objective is"*; nothing enforces it. **This is the root**: no later status change is needed.
2. **`compile_bundle` stops at the pin** (FD 9659 limb 3 in the maintainer's (by delegation) numbering). The pin loop
   (`packages/pricing-core/src/pricing_core/rating/compile.py:618-631`) checks a custom objective
   only when it is pinned directly. A pinned model's payload carries its spec, and a GBM's
   `spec.objective` is a `GbmFunctionRef` (`packages/model-schema/src/model_schema/modelling.py:1238`,
   `kind` `:1249`, `ref` `:1255`, format `custom_objective:<slug>@<version>` `:1254`). Nothing
   follows it. This catches what the root cannot: a model approved before the fix, and an objective
   deprecated after its model's approval (the only edge out of `approved`,
   `packages/model-schema/src/model_schema/objectives.py:160-168`).
3. **A `control`-intent Factor seeds a rateable table, and the table compiles** (FD 9697).
   `seed_from_model` (`packages/pricing-core/src/pricing_core/rate_tables/operations.py:172`) binds
   the key to the pinned Factor (`factor_ref`, `:230`) and never reads `intent`; `rateable` defaults
   to `True` (`:180`). `compile_bundle` never resolves a key's `factor_ref`. FR-88
   (`02-modelling.md:89`): *"Rating Versions may only use `risk` factors; a `control` factor
   reaching a rate table is a validation error in `03`."* `03` §5.1 already owns
   `CONTROL_FACTOR_IN_RATEABLE_PATH` (`03-rating-engine.md:933`), but `backend/src/app/errors.py`
   does not register it (`RATING_ERROR_CODES`, `:309`), and `PlatformError` refuses an unregistered
   code at construction (`errors.py:434`). So a raise of that code today would surface as a crash,
   not a 422.

And one test gap: **the direct custom-objective pin refusal has no negative test** (FD 9659 limb 2
in the maintainer's (by delegation) numbering). The only custom-objective compile test is the approved case
(`backend/tests/test_rating_version_compile.py:536`). Deleting `*version.pins.custom_objectives`
from `all_refs` (`compile.py:622`) would pass the suite (FD 9659 item 1).

**Folded in on the maintainer's (by delegation) 14:46:53 BST entry, item 2: a `control`-intent factor reaches a price
through a `model_call`** (FD 9639, working id, draft PR #1156 at `ca152d5f`; HIGH provisional,
latent today). `_model_call_handler` (`packages/pricing-core/src/pricing_core/rating/runtime.py:512`)
scores a GBM pin through `predict_gbm(gbm_result, booster, frame, factors=(), nthread=1)` (`:565`)
on every slug of `GbmFitResult.feature_order` (`model_schema/modelling.py:1671`), and nothing on
that path reads `Factor.intent` (`:143`). `feature_order` holds Factor slugs (the design loop in
`pricing_core/modelling/gbm.py:301-302` keys each column by `factor.slug`), while the pinned model's
payload names its Factors only by id (`ModelSpecCommon.factors: tuple[UUID, ...]`, `:842`), so
`compile_bundle` has nothing to read an intent from today. This slice takes the **safe minimum**:
compile refuses such a `model_call` (DP-7). Neutralisation is not built here.

## The decisions this plan rests on, quoted

From `~/gi-pricing-plan.local/channel/to-lead.md`, cited by entry header:

- **"2026-10-05 13:38:03 BST — Finding batch 1: FD 9697's owner = WK-673; FD 9659's limb-3 severity
  depends on one fact"**: *"FD 9697 owner: WK-673, not WK-1178. The fix is in compile_bundle against
  FR-240 (03 :137), which WK-673 owns"*; and the limb-3 rule: *"If model approval does NOT refuse
  it, a priced bundle can rest on an objective that never passed review, with no stale state
  needed. That is the governance bypass FR-240 forbids, and it is HIGH, before the exit demo."*
- **"2026-10-05 14:12:13 BST — FD 9659: HIGH confirmed, owner WK-673, before the exit demo; first in
  batch 2; ONE fix plan for the FR-240 family"**, item 3: *"ONE fix plan for the FR-240 family,
  owner WK-673 … The plan covers BOTH points: (a) model approval refuses a model whose custom
  objective is not approved (the root: no stale state needed); (b) compile_bundle's transitive
  check (FR-240's "transitively reachable"), so a later status change is also caught. Red first on
  each. … it is a HIGH G2 blocker under my 13:12:56 priority rule, and it serialises with the FD
  9707 fix only where the plans name shared files."*

- **"2026-10-05 14:21:22 BST — DECISIONS 35–38 (PL 9649, the FR-240 family fix); file the
  model_call candidate; FD 9641 noted"** decides DP-1 to DP-4, each as recommended, with conditions:
  - Item 35, DP-1 (a): *"CONDITION: the override must NOT reach compile. FR-240's compile refusal
    is absolute and independent of approval state, so a red-first test: flag → Admin override with
    justification → the model approved → compile_bundle still REFUSES. ModelFlag, model.schema.json
    and the contracts are regenerated in the same commit."*
  - Item 36, DP-2 (a): *"FR-240's T-text states the bound verbatim, and states the exclusion: peril
    structures, unresolvable at compile until FD 9995 is fixed, are named as a known gap with FD
    9995 as its owner, not silently out of scope. Custom evaluation metrics are excluded: they do
    not reach a price."*
  - Item 37, DP-3 (a): *"Refuse at SEED and at COMPILE with CONTROL_FACTOR_IN_RATEABLE_PATH (422,
    03-owned, registered in this slice), plus a dated FR-230 amendment as a T-text."*
  - Item 38, DP-4 (a): *"every pinned rate table's key factor_ref, whatever its `rateable`. The flag
    is declarative, so the check does not trust it."*
  - The candidate DP-4 (c), a `model_call` over a model fitted with a `control` factor, is to be
    filed as its own finding, owner WK-673. The lead's relay of about 14:22 BST names it FD 9639
    (working id, auditor-ctrl), outside this plan unless it returns HIGH.

- **"2026-10-05 14:28:35 BST — PL 9649 / SL 9647 (the FR-240 fix, #1152 @dc13400e): DP-5 OK; DP-6
  scoped; lane placement"**:
  - Item 39, DP-5: *"(`deprecated` refused at compile too, OQ-609): OK, with a red test."*
  - Item 40, DP-6 amended: *"Task 0 counts bad rows (a control-intent factor in a pinned table key;
    an unapproved custom objective behind an approved model) in `gipricing` (the demo DB) and in the
    slice's own per-worktree test DB ONLY, not "gipricing*". … If gipricing has any bad row, STOP
    and report to me with the ids (no reset, no delete), as proposed."*
  - LANE: *"it takes the first build lane free once its plan is active, ahead of any slice G2 does
    not need. Concretely: after whichever of the FD 9707 fix (lane B) or the FD 9708 fix (lane C)
    finishes first, it goes BEFORE PL 9728 (NFR-489, a G4 item) in lane B, or BEFORE WK-675 S2 (off
    G2's path) in lane C. WK-673 S3 in lane A is NOT displaced."*

- **"2026-10-05 14:46:53 BST — FD 9639 (a control factor's coefficient reaches scoring): HIGH
  provisional; PL 9649 takes the REFUSAL now; neutralisation is an open question first"**:
  - Item 2: *"Scope: PL 9649 takes the SAFE MINIMUM now: compile_bundle refuses a model_call whose
    pinned model's feature_order contains a `control`-intent factor, with
    CONTROL_FACTOR_IN_RATEABLE_PATH, red first (the same code as decision 37). That stops any price
    depending on a control factor today, and fits PL 9649's FR-240 T-text ("no control-intent factor
    in a rateable path")."*
  - Item 3: *"Neutralisation is NOT built in this slice: a DM drafts an OQ with options"*, (a)
    refusal only, (b) neutralise at a declared reference value, (c) refuse unless the reference is
    declared; *"the decision comes to me. If (b) or (c) is chosen, it is a spec change first (02
    FR-88 and 03), then its own slice under WK-673, not part of PL 9649."*
  - Item 4: *"PL 9649's planner folds in step 2 (a DP note citing this entry)"*. That is DP-7.

The lead's brief adds (c) FD 9697's control-intent refusal at compile and at seed (DP-3), and (d)
limb 2's negative test. The lead's relay of RL 9633's report (working id, the ruling, below) adds
a DP-4 test over a table with `rateable: false`: *"Acceptance 5 does not list one"*. Acceptance 5
now does.

## Status

`draft`. DP-1 to DP-4 are **decided** (the maintainer (by delegation), 14:21:22 BST, items 35–38, quoted above), and
every site below applies them with their conditions. DP-5 is decided as recommended (item 39) and DP-6 as
amended (item 40, the 14:28:35 entry); every site applies both. DP-7 is decided (the 14:46:53
entry, item 2) and applied at every site; its neutralisation half is an open question, not built. The plan moves to `active` only through a separate activation PR, once every
activation need below holds. That PR carries this plan's status flip and the `SL-` row's.

### Activation needs, in order

1. **FD 9697 and FD 9659 minted** (#1136, #1142; FD 9659 is first in batch 2, the 14:12:13 entry,
   item 2).
2. **A ruling record (`RL-`), written by a decision-maker who adopts texts T1 to T5**
   (§"Spec texts": FR-240, FR-230, the seed route row and the owned-code line in `03`, and `02` R4),
   **and records DP-1 to DP-4 as decided at 14:21:22 BST, DP-5 and DP-6 at 14:28:35 BST, and DP-7
   at 14:46:53 BST**. The ruling is RL 9633 (working id; `~/gi-pricing-plan.local/handover/eta.md`,
   row "RL 9633", 5 Oct 14:32:29), drafted before DP-7: **it needs FR-240's T-text to name the
   `model_call` case**, as T5 below or folded into T1, and records DP-7 as decided with
   neutralisation left to the open question (DP-7). `dm-9639oq` updates it. A decision
   lands as a dated artifact (`CLAUDE.md` §12), as for PL 9688. If its text differs from this plan, the
   ruling wins, and the dispatch record names each difference at every site it operates
   ([`README.md`](README.md) rule 5: narrative, Files, Steps, Acceptance).
3. **This plan made `active`** by a dated line in the activation PR.
4. **Lane** (the 14:28:35 entry). A HIGH G2 blocker takes the first build lane free once this
   plan is active, under the maintainer's (by delegation) 13:12:56 BST priority rule: after whichever of the FD 9707
   fix (lane B) or the FD 9708 fix (lane C) finishes first, it goes **before PL 9728** in lane B,
   or **before WK-675 S2** in lane C. **WK-673 S3 in lane A is not displaced.** It **serialises with the FD 9707 fix (PL 9688, #1145) on `compile.py`**, the one
   code file both plans name (§"Write set"); the dispatch record names the order. It never runs
   concurrently with a slice that edits `compile_bundle`'s body.
5. **The dispatch GO**, with Task 0 run at dispatch and its STOP conditions read.

**Pre-mint notes of 2026-10-05 15:57 BST, at `origin/main` `cdaaa57345cb765f96034ce1ec2733c338f1c3cd`.**
These record what the maintainer (by delegation) ruled after filing. Where one differs from
activation need 4 or the Write-set table, the note is the later ruling and governs.

- **The activating ruling is RL 9633** (working id, draft PR #1155, branch `dm-9633-fr240`). It now
  carries Ruled 8 (DP-7, the `model_call` refusal) and Ruled 9 (neutralisation: option (c), left to
  OQ 9630, which mints after it). Activation need 2 is therefore drafted, and is met at RL 9633's
  mint.
- **The lane: D1 (c).** This replaces activation need 4's lane sentence. From the `to-lead.md` entry
  headed *"2026-10-05 15:28:26 BST — Wave results: D1 = (c); D2 PL 9624 DPs; D3 PL 9629 DP-6 + plan
  the 2 missing G2 items; C1′ is FD 9995 (no new finding); FD 9619 noted"*:
  *"D1 (PL 9649, the FR-240 fix): OPTION (c). It runs only beside a different Work's build, or
  after S7/S3. … Concretely: lane C after the FD 9708 fix, i.e. beside S7 only once S7's
  owned-codes append has merged (the second re-appends), or after S7. (a) is refused: my 14:28:35
  "rebased by the second" noted merge order and did not license concurrent edits to one
  definition."* RL 9633's Ruled 7 still quotes the 14:28:35 lane. That record is its
  decision-maker's to update, not this plan's.
- **J5: after the FD 9707 fix.** Same entry, LANE B: *"J2 and J5 serialise as found (FD 9707 fix
  before the FR-240 fix)."* The `compile.py` serialisation in activation need 4 runs in that
  order: PL 9688 (#1145) first.
- **F3, `backend/src/app/errors.py`.** From the entry headed *"2026-10-05 15:15:11 BST — F2
  (RL-1263's "from different Works"): OPTION (i), amend RL-1263 by a dated RL, with conditions; F1,
  F3 and the stale RL 9633 sentence as you set them"*: *"F3 (errors.py not on the exempt list
  :90-94): as you resolved it. PL 9683 and PL 9649 either serialise there, or each dispatch names
  errors.py with a merge-tree check showing append-only, disjoint names."* The same entry has RL 9620
  (the RL-1263 amendment) mint *"AHEAD of the lane GOs that need it: lane B's FD 9707 fix beside
  S7, and later PL 9649"*. A WK-673 slice beside S7 needs it.
- **DP-8 (a) of PL 9616.** From the entry headed *"2026-10-05 15:47:15 BST — PL 9616 (#1168) DPs
  RULED (the maintainer, by delegation), on dm-1416's memo; the FD-1416 HOLD LIFTS at DP-1"*:
  *"DP-8: (a), delete the hand-authored approval-request.schema.json … PL 9649 (#1152) re-anchors
  its Acceptance 9 cite (:53-54) at whichever of the two merges second."* So if PL 9616's slice
  merges first, Acceptance 9's `approval-request.schema.json:53-54` cite is re-anchored at this
  slice's dispatch. If this one merges first, PL 9616's slice re-anchors it.
- **Owed at dispatch** (the decision log, 14:38:41 BST): *"add a red test for DP-4 with rateable:
  false"*. Acceptance 5 is parametrised over `rateable` (Task 3), which the 15:15:11 entry confirms
  (*"PL 9649 Acceptance 5 has it"*). The dispatch record confirms it and adds nothing.
- **Cites re-checked at `cdaaa573`.** SL-1409 (#1157) merged and moved lines in three files, now
  re-anchored: `errors.py` `RATING_ERROR_CODES` `:309` (was `:305`) and `PlatformError`'s refusal
  `:434` (was `:430`); `api/approvals.py` `apply_approval_decision` call `:541` (was `:524`). Two
  cites were wrong at filing and are corrected: `bound = pinned[0]` is `operations.py:210`, and
  the R4 quote is `packages/model-schema/src/model_schema/objectives.py:174-178`. Every find string
  counts 1 at `cdaaa573`. §"Self-review"'s literals stay as read at `83ea5090`.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means the named test was run at the slice's base and failed **for the stated cause** before the
code that turns it green. A failure with the right status and a different cause is a plan defect
([`README.md`](README.md) rule 2). The ledger records each red with its failure line as printed.

1. **(a) The root, red first.** `uv run pytest -q backend/tests/test_fr240_governance.py -k
   approv` passes against Postgres and MinIO (a skip is not a pass). At the base,
   `test_a_model_whose_custom_objective_is_in_review_cannot_be_approved` failed with `Failed: DID
   NOT RAISE` (the approval went through, FD 9659 §3's cause). After the fix,
   `apply_approval_decision` raises `PlatformError` with `code == "ARTIFACT_FLAGGED"`, status 409,
   and a detail naming `custom_objective_not_approved` and the objective's ref; the model row reads
   `review` afterwards. A control in the same module, `..._approved_objective_can_be_approved`, is
   green at the base and after.
2. **(a) The flag is visible.** `test_flags_for_names_an_unapproved_objective` asserts
   `flags_for(...) == (ModelFlag.CUSTOM_OBJECTIVE_NOT_APPROVED,)` for a fitted GBM on a `review`
   objective. Red first by `AttributeError` on the missing member (Task 1 Step 3 records the line).
3. **(b) Transitive, pricing-core, red first.** `uv run pytest -q
   packages/pricing-core/tests/test_rating_compile_fr240.py` passes. At the base,
   `test_an_unapproved_objective_reached_through_a_pinned_model_is_refused[certified]`,
   `[review]` and `[deprecated]` each failed with `Failed: DID NOT RAISE` (FD 9659 §Evidence 1's
   `COMPILE ACCEPTED`). After the fix each raises `ValueError` matching `PIN_NOT_APPROVED`, whose
   message names the model ref, the objective ref and its status.
   `test_an_approved_objective_reached_through_a_pinned_model_compiles` and
   `test_a_builtin_objective_needs_no_resolution` are green at the base and after.
4. **(b) Transitive, through the compile Job, red first; DP-1's condition (an override never
   reaches compile).** In `test_fr240_governance.py`, `test_an_overridden_flag_never_reaches_compile`
   runs the chain *flag → override → approved → compile*: the model carries
   `custom_objective_not_approved` (`flags_for`), it is then written `approved` the way an Admin
   override would leave it, and a version pinning only that model is compiled. It fails at the
   base with `AssertionError` on `job_row.status is JobStatus.FAILED` (the Job succeeded). After
   the fix the Job is `FAILED` with `job_row.error["code"] == "PIN_NOT_APPROVED"`. **FR-359's Admin
   override is not built** for any flag (`modelling.py:1339-1351` raises for every flag, with no
   override branch), so the test reaches `approved` with `backend/tests/approved_rows.py::mark_approved`,
   the one way an `approved` row over a flagged model can exist today; the test's docstring says
   so. The same test is the pre-fix approval case.
5. **(c) Control intent at compile, red first.** In `test_rating_compile_fr240.py`,
   `test_a_pinned_table_keyed_on_a_control_factor_is_refused` fails at the base with `Failed: DID
   NOT RAISE` (FD 9697 §Evidence 1's `COMPILE ACCEPTED`), and after the fix raises `ValueError`
   matching `CONTROL_FACTOR_IN_RATEABLE_PATH`, naming the table, the key and the Factor ref.
   It is parametrised over the table's `rateable` flag (`model_schema/rating.py:714`), `[True]` and
   `[False]`, and **`[False]` is red first by the same cause**: DP-4 (a) refuses whatever the flag,
   because *"the flag is declarative, so the check does not trust it"* (item 38).
   `test_a_table_keyed_on_a_risk_factor_compiles` is green at the base and after.
6. **(c) Control intent at seed (DP-3 (a)), red first.**
   `test_seeding_from_a_control_factor_is_refused` fails at the base with `Failed: DID NOT RAISE`
   (FD 9697's `SEED ACCEPTED`), and after the fix raises `ValueError` matching
   `CONTROL_FACTOR_IN_RATEABLE_PATH`. Over HTTP, `test_fr240_governance.py::
   test_the_seed_route_refuses_a_control_factor_with_its_code` gets `422` with `code ==
   "CONTROL_FACTOR_IN_RATEABLE_PATH"`; at the base it got `201`.
7. **(c) The code is raisable.** `test_fr240_governance.py::
   test_a_compile_over_a_control_keyed_table_fails_with_its_code` ends in a `FAILED` Job with
   `error["code"] == "CONTROL_FACTOR_IN_RATEABLE_PATH"`. `CONTROL_FACTOR_IN_RATEABLE_PATH` is in
   `RATING_ERROR_CODES`, and `python3 scripts/audit-docs.py` check 10 agrees with `03` §5.1.
8. **(d) The direct pin, negative.** `test_fr240_governance.py::
   test_a_version_pinning_an_unapproved_custom_objective_fails_to_compile` is parametrised over
   `certified` and `review` and ends in a `FAILED` Job with `error["code"] == "PIN_NOT_APPROVED"`.
   It is green at the base, by design (the refusal exists). **Its proof is a broken-input run**:
   with `*version.pins.custom_objectives,` deleted from `all_refs` (`compile.py:622`) in a scratch
   edit, the test fails, and the ledger records that failure line; the edit is then reverted and
   never committed (`CLAUDE.md` §13, "enforcement is proven on deliberately broken input").
9. **No shape is hand-written twice.** `ModelFlag` gains `CUSTOM_OBJECTIVE_NOT_APPROVED =
   "custom_objective_not_approved"`, the spelling `docs/contracts/schemas/approval-request.schema.json:53-54`
   already declares. `uv run python scripts/generate-contracts.py --check` exits 0 after the
   regeneration is committed, and `backend/tests/test_contracts.py` passes with the hand-authored
   `model.schema.json` `flags` enum extended to match.
10. **Task 0's exposure counts are recorded** in the ledger with the query verbatim, for the demo
    database `gipricing` and the slice's own per-worktree test database only (DP-6 as amended, item
    40). A bad row in `gipricing` stopped the slice to the lead with its ids before Task 2; nothing
    was reset or deleted.
11. **The whole gate is green, both halves**, per `dev-commands`: `uv run ruff check . && uv run
    mypy && uv run lint-imports && uv run pytest -q`, `python3 scripts/audit-docs.py`,
    `uv run python scripts/req-coverage.py`, `uv run python scripts/generate-contracts.py --check`,
    and the frontend half (`pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend
    generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir
    frontend test && pnpm --dir frontend build`), in a gate slot under `RL-1263`. The tests that
    use a `FakeResolver` model payload with no `spec`, or a rate-table payload with no `keys`,
    pass unchanged (DP-2's reading rule, Task 2).
12. **`git diff --stat origin/main...HEAD` names only the files of §"Write set"**, plus the ledger
    and `docs/INDEX.md`.
13. **(e) Control intent through a `model_call` (DP-7), red first.** In
    `test_rating_compile_fr240.py`, `test_a_model_call_over_a_gbm_fitted_on_a_control_factor_is_refused`:
    a model payload whose `fit_result.feature_order` holds the slug of a Factor with
    `intent=FactorIntent.CONTROL`, pinned by a `model_call` step, its Factors on the resolved
    artifact (Task 3b Step 3). It fails at the base with `Failed: DID NOT RAISE`, and after the fix
    raises `ValueError` matching `CONTROL_FACTOR_IN_RATEABLE_PATH`, naming the model ref, the feature
    and the Factor ref. `test_a_model_call_over_risk_factors_compiles` is green at the base and
    after. Through the compile Job, `test_fr240_governance.py::
    test_a_compile_over_a_gbm_fitted_on_a_control_factor_fails_with_its_code` fits a GBM on a
    `control` Factor through the real Job (the `_fitted_gbm` neighbour,
    `backend/tests/test_model_jobs_gbm.py:88`), approves it with `mark_approved`, pins it by a
    `model_call`, and ends in a `FAILED` Job with `error["code"] ==
    "CONTROL_FACTOR_IN_RATEABLE_PATH"`; at the base the Job succeeded. Markers `FR-88`, `FR-240`.

## Global Constraints

- Money is integer minor units, never float (`CLAUDE.md` §7). This slice moves no money.
- `pricing-core` imports no FastAPI, SQLAlchemy or Redis (`CLAUDE.md` §2); `uv run lint-imports` holds it. The new compile checks read only what the `ArtifactResolver` returns.
- No hand-written shape that exists in `model-schema` (`CLAUDE.md` §2). `ModelFlag` is the one source of the flag's spelling; the hand-authored contract follows it.
- No pandas (`CLAUDE.md` §3).
- Every new test carries `@pytest.mark.req("FR-240")`; the approval tests also carry `FR-20` and `FR-359`; the seed tests `FR-88` and `FR-230` (`python-test`).
- Requirement ids are permanent (`CLAUDE.md` §5): this plan appends dated amendments and takes no new id.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-240 | Clause "no unapproved custom objective transitively reachable" (DP-2), and clause "no `control`-intent factor in a rateable path" (DP-4, and through a `model_call`, DP-7), at compile | `req("FR-240")` on every new test |
| `00` | FR-20 | Maturity enforced at the transition: model approval (DP-1) and compile (DP-2) | on the approval and transitive tests |
| `02` | R4 (§1, `:49-50`) | A Model using a Custom Objective reaches `approved` only if the objective is `approved` | covered by the FR-20 / FR-359 tests; R4 has no id of its own |
| `06` | FR-359 | The unapproved-objective flag propagates into the approval surface and blocks `approved` | `req("FR-359")` on the approval tests |
| `02` | FR-88 | A `control` factor reaching a rate table is a validation error in `03`; *"Rating Versions may only use `risk` factors"*, so a `model_call` over one is refused too (DP-7) | `req("FR-88")` on the seed, control-compile and `model_call` tests |
| `03` | FR-230 | Seeding refuses a `control` Factor (DP-3 (a), text T2) | `req("FR-230")` on the seed tests |
| `02` | FR-163 | The objective lifecycle; `deprecated` is refused at compile (DP-5) | the `[deprecated]` case |
| `02` | FR-205 | The existing flag and its refusal are unchanged; the message generalises | the existing test `test_model_lifecycle.py:547` passes unchanged |

**Out of scope, stated so nothing is silently dropped:** FR-240's other clauses (register row
`FR-240 (F-W9-3)`, `docs/findings/register.md:61`, clauses (1)-(4)); FR-359's Admin override, which
is built for no flag today (`apply_approval_decision` raises for any flag, `modelling.py:1339-1351`),
though Acceptance 4 proves its outcome cannot reach compile (item 35); a peril structure's models, a
**known gap named in T1 with FD 9995 (working id, #980) as its owner** (the compile resolver cannot
resolve a `peril_structure`, its final `NOT_FOUND`, `backend/src/app/platform/rating_versions.py:550-555`;
item 36); custom evaluation metrics, which do not reach a price (item 36); and **neutralising a `control`
factor in a priced GBM** (holding it at a declared reference level), which goes to the maintainer
as an open question first (the 14:46:53 entry, item 3; DP-7). This slice only refuses (DP-7).

### Task 0 at planning time

Not run. The planner ran no query and no test (the lead's standing rule; a re-gate held gate-1).
Task 0 is the executor's at dispatch, with its STOP conditions.

### Write set, and its contention (`RL-1263`)

RL-1263: two concurrent build slices may not both change the same **existing** function, class,
method, spec section or policy table, and **any other shared path serialises** unless the lead's
dispatch record names the path and the check that no existing definition is edited by both. The
keys are under `guards.parallelism.build_slices_across_works` in
`docs/process/delivery-process.core.json`: `no_shared_files` `:389`,
`registry_exempt_append_only` `:391`, `generated` `:394`, `other_shared_path` `:417`.

**Snapshot: open PRs at `83ea509023d6d705d6f78fe74b7124fdf1375739`, 2026-10-05 14:20 BST; working
ids as then.** Each plan's write set was read from its branch: PL 9688 at #1145 `2f3269c8`, PL 9683
at #1140 `78bfc54f`, PL 9716 at #1127 `33ea0052`, PL 9713 at #1131 `0ec1fe1a`, PL 9689 at #1138
`e810b785`; SL-1409's from `git diff --name-only origin/main...origin/sl-1409-validation-rule-approval-through-the-workflow`
at `ae78023e`.
*Pre-mint check of 2026-10-05 15:57 BST, at `cdaaa573`:* SL-1409 has merged (#1157), so its column
is history. Its `DATA_ERROR_CODES` edit and its `approved_rows.py` edit are on main, and this slice
is the second to merge on `errors.py` and re-gates. `mark_approved` is now `approved_rows.py:92`.

| Path | This slice | SL-1409 (lane B, re-gating) | FD 9707 fix (PL 9688, #1145) | FD 9708 fix (PL 9683, #1140) | SL-1391 (PL 9716, #1127) | WK-675 S2 (PL 9713, #1131) | WK-673 S3 (PL 9689, #1138) | Class |
|---|---|---|---|---|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | edited: `compile_bundle` (`:573`; three calls after the pin loop `:618-631`), `ResolvedArtifact` (`:434`, one field appended, DP-7); added: `_check_reachable_objectives`, `_check_control_factor_keys`, `_check_control_factor_model_calls` (DP-7) | — | added `_check_lookup_as_at`; edited `ALGORITHM_CHECKS` | — | — | — | reads `compile_bundle` (`:573`), not edited | **shared with PL 9688, distinct definitions**: serialises (the maintainer (by delegation), 14:12:13 item 3) unless the dispatch record names the path and the check (`other_shared_path`). PL 9776 (#1051) also edits `ALGORITHM_CHECKS`, not touched here |
| `packages/pricing-core/src/pricing_core/rate_tables/operations.py` | edited: `seed_from_model` (`:172`, one refusal after `bound`, `:210`) *(DP-3 a)* | — | — | — | edited `_compute_diff`; added `diff_cells` | — | — | shared with SL-1391, distinct definitions: `other_shared_path` |
| `backend/src/app/platform/rating_versions.py` | edited: `compile_rating_version`'s `_Resolver.resolve` (`:445-555`), one `factor` branch before the final `NOT_FOUND`, and the `model` branch (`:464-485`) carries the model's Factors (DP-7); one import, `load_factors` | — | reads `rows_as_at` call only | edited `create_rating_version` (`:230-275`) | — | reads | — | shared with PL 9683, distinct definitions: `other_shared_path` |
| `backend/src/app/platform/modelling.py` | edited: `flags_for` (`:1049-1066`), the `ARTIFACT_FLAGGED` detail in `apply_approval_decision` (`:1343-1351`) | — | — | — | added `load_factor_by_ref` | — | — | shared with SL-1391, distinct definitions: `other_shared_path` |
| `packages/model-schema/src/model_schema/modelling.py` | edited: `ModelFlag` (`:1984-1992`), one member appended | — | — | — | — | — | — | none |
| `backend/src/app/errors.py` | edited: `RATING_ERROR_CODES` (`:309`), `CONTROL_FACTOR_IN_RATEABLE_PATH` appended | edits `DATA_ERROR_CODES` | — | appends to `RATING_ERROR_CODES` *(DP-1 a)* | — | — | — | registry: append (`registry_exempt_append_only`); the second to merge re-gates |
| `docs/contracts/schemas/model.schema.json` (hand-authored) | edited: `flags` (`:175-178`), the enum and a dated note | — | — | — | — | — | — | none |
| `docs/contracts/` generated files; `docs/INDEX.md`; the ledger | regenerated; added | regenerates `openapi/generated.json` | every PR | every PR | every PR | every PR | every PR | `generated` |
| `docs/specs/03-rating-engine.md` | edited: FR-230 row (`:121`, T2), FR-240 row (`:137`, T1), the seed route row (`:902`, T2's refusal), the owned-code list (`:933`, T4) | — | FR-221 row (`:107`) | FR-223 row, §5.1 owned list | FR-231 (`:122`), §4.2, §5.1 diff row (`:904`) and a row after it | rows after FR-243 (`:140`), §5.1 before `:897` and after `:908` | FR-1398/1399, §4.6, §5.1 owned list, §5.2 | **shared file, distinct rows**, but three edits are **adjacent hunks**: `:121` beside SL-1391's `:122`; `:137` within three lines of S2's insertion after `:140`; `:902` beside SL-1391's `:904`. Adjacent hunks conflict like one hunk (the maintainer (by delegation), 14:11:28 BST, "Lesson for the batch rule"), so the second to merge rebases once and re-reads |
| `docs/specs/02-modelling.md` | edited: R4 (`:49-50`), a dated note (T3) | — | — | — | — | — | — | none found |
| `docs/roadmap.md` | added: the SL 9647 row at the end of WK-673 (plan PR only) | — | inserts SL 9685 at the same place | its own row | edits SL-1391's row (`:812`) | its own row | its own row | registry (append, distinct rows); adjacent to PL 9688's insertion, so the second to merge re-reads |
| `packages/pricing-core/tests/test_rating_compile_fr240.py` | added (new module) | — | — | — | — | — | — | none |
| `backend/tests/test_fr240_governance.py` | added (new module) | — | — | — | — | — | — | none. It imports `backend/tests/approved_rows.py::mark_approved`, which SL-1409 edits (`_EVIDENCE`, `_FLAG_ONLY`); read only here |

**Read, not edited:** `backend/src/app/platform/modelling.py::load_factors` (`:284`, the spec's
Factors by id in spec order, plus interaction operands; already called this way by
`rate_tables.py:134-136`), `pricing_core/rating/runtime.py::_model_call_handler` (`:512`; DP-7
refuses before a bundle exists, so scoring is not changed), `backend/src/app/api/approvals.py` (`_carry_to_the_artifact` calls
`apply_approval_decision` at `:541`; SL-1409 edits that function, so this slice must not),
`backend/src/app/platform/objectives.py` (`resolve_ref`, `:516`), `backend/src/app/platform/rate_tables.py`
(`_map_operation_error` turns the seed's `CODE: detail` into a 422, `:83-92`).

### Size

Small to medium: about one executor day. Six tasks after Task 0. One two-half gate run, which needs
a gate slot under `RL-1263`. The backend tests fit GBMs through the real Job, so they need Postgres
and MinIO; the slice takes no NFR measurement and need not run exclusive.

## Decision points

DP-1 to DP-4 were blocking, went to the lead as found, and are decided (items 35–38). The options
are kept so a reader can see what was weighed; the decisions' text governs.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | Where does model approval refuse an unapproved objective, and with what code? | (a) a computed flag `custom_objective_not_approved` in `flags_for`, refused by the existing `ARTIFACT_FLAGGED` 409 at the decision; `ModelFlag` and `model.schema.json` gain the member; (b) a bare `OBJECTIVE_NOT_APPROVED` refusal inside `apply_approval_decision`; (c) (a), and refuse at submission too | **(a).** `06` FR-359 names *"unapproved custom objective (`02` R4)"* as a flag that propagates into the approval surface, and the approval-request contract already spells it `custom_objective_not_approved` (`approval-request.schema.json:53-54`). `flags_for` is computed, not stored (`modelling.py:1052-1060`), which is exactly right for a referent that moves. Submission already records the flags in its audit (`:1162-1180`), so (c) adds nothing but a forced serial review | **DECIDED (a)**, the maintainer (by delegation) 14:21:22 BST item 35, with the condition that an override never reaches compile (Acceptance 4) | Tasks 1, 2, 4, 6 |
| **DP-2** | What does "transitively reachable" reach, and with what code? | (a) one hop: each pinned model's own `spec.objective` when `kind == "custom"`, refused `PIN_NOT_APPROVED` naming model → objective; (b) a walk of every artifact ref in every resolved payload; (c) (a) plus a GBM's custom eval metrics | **(a).** It is every path that exists: a GLM has no custom objective (`02` FR-207's 2026-10-04 amendment moves `GlmSpec.custom_objective_ref` to Phase 3), and a peril structure cannot be resolved at compile today (§"Scope"). `PIN_NOT_APPROVED` because the same objective in the same state then gets the same code by either door, and FR-240's clause is a maturity clause (FR-20). Text T1 states the bound, as FD 9659's remedy asks | **DECIDED (a)**, item 36: T1 names the peril-structure gap with FD 9995 as owner; custom eval metrics excluded (no price) | Tasks 2, 6 |
| **DP-3** | FD 9697 at seed? FR-240 names compile; FR-88 says a `control` factor *reaching a rate table* is an error | (a) refuse at seed **and** at compile, `CONTROL_FACTOR_IN_RATEABLE_PATH` 422, FR-230 amended (T2); (b) seed it with `rateable=false`; (c) compile only | **(a).** FR-88's words reach the table, not only the bundle, and a refusal at seed tells the author before any table exists. Compile stays the backstop for any table whose key binds a `control` Factor by another route | **DECIDED (a)**, item 37: the code is registered in this slice; T2 amends FR-230 | Tasks 3, 6 |
| **DP-4** | What is a "rateable path" at compile? | (a) every pinned rate table's keys bound by `factor_ref`, whatever the table's `rateable` flag; (b) only tables with `rateable: true`; (c) also a `model_call` whose model fits a `control` factor | **(a)** in this slice. A pinned table is in the bundle by construction, and (b) would lean on FR-236's "rateable only" rule, which nothing here shows is enforced. (c) went to the lead as a candidate finding: FR-88's 2026-08-22 amendment gives `control` a free coefficient, so a `model_call` may score on it | **DECIDED (a)**, item 38 (*"the flag is declarative, so the check does not trust it"*); the `rateable: false` case is tested (Acceptance 5). (c) is FD 9639 (working id), filed separately, and returned HIGH provisional: its refusal is DP-7 | Tasks 3, 6 |
| **DP-5** | Which objective statuses pass the transitive check, and which the flag? | (i) compile: the direct pin's `_APPROVED_OR_BETTER` (`compile.py:404`), so `deprecated` is refused; the flag: status ≠ `approved`; (ii) compile also admits `deprecated` | **(i).** `02` OQ-609 is decided (a): *"existing pins continue, new specs cannot select"*, and a compile is always of a `draft` version (FR-239), so it is new work. One set for both doors | **DECIDED (i)**, the maintainer (by delegation) 14:28:35 BST item 39, with a red test (the `[deprecated]` case, Acceptance 3) | Tasks 2, 4 |
| **DP-6** | Rows already in the bad state (approved models over unapproved objectives; tables keyed on `control` factors) | (a) Task 0 counts them over every `gipricing*` database and STOPS to the lead on a non-zero count; no reset in this slice; (b) reset such models to `review` | **(a).** After the fix, compile refuses every such row's use (Tasks 2 and 3), so nothing new is priced on them. A reset is a data change whose need the count decides | **DECIDED (a), AMENDED**, item 40: count in `gipricing` (the demo DB) and the slice's own test DB only, since the 92 `gipricing_%` databases are disposable scratch; a bad row in `gipricing` STOPS with its ids, no reset, no delete | Task 0 |
| **DP-7** | FD 9639: a `model_call` over a GBM whose `feature_order` holds a `control`-intent factor | (a) refuse at compile, `CONTROL_FACTOR_IN_RATEABLE_PATH`, the code DP-3 registers; (b) neutralise at a reference value the model declares per `control` factor; (c) refuse unless that reference is declared | **(a) in this slice**, as the safe minimum: no price can depend on a `control` factor while (b) and (c) are open. (b) and (c) need a spec change first (`02` FR-88 and `03`) | **FD 9639's safe minimum, decided** (the maintainer (by delegation), 14:46:53 BST, item 2); **neutralisation NOT built** (an open question goes to the maintainer, item 3, drafted by `dm-9639oq`; if (b) or (c) is chosen, its own slice under WK-673) | Tasks 3b, 6 |

### Spec texts (proposed for the ruling; applied verbatim in Task 6)

**T1**, a dated amendment appended to the FR-240 cell (`03-rating-engine.md:137`), after the
`RL-1329` amendment:

> *(Amended 2026-10-05, FD 9659 and FD 9697.)* **"Transitively reachable" means through a pinned
> model**: a pinned model whose spec names a custom objective (a GBM's `spec.objective` with `kind:
> custom`) reaches that objective, and compilation refuses it with `PIN_NOT_APPROVED` unless it is
> approved or better, exactly as if it were pinned. The message names the model and the objective.
> A `deprecated` objective is refused, as a new specification may not select one (`02` OQ-609).
> The bound is one hop. **Known gap:** a peril structure's models are not reached, because a peril
> structure cannot be resolved at compile; FD 9995 owns that gap, and this clause reaches them when
> it is fixed. Custom evaluation metrics are not objectives and do not reach a price, so they are
> outside this clause. **A
> `control`-intent factor is in a rateable path when a pinned rate table has a key bound by
> `factor_ref` to it**, whatever the table's `rateable` flag; compilation refuses it with
> `CONTROL_FACTOR_IN_RATEABLE_PATH` (422), naming the table, the key and the Factor.

**T2**, a dated amendment appended to the FR-230 cell (`:121`), and the same refusal added to the
seed route's 422 list (`:902`):

> *(Amended 2026-10-05, FD 9697.)* A seed request naming a `control`-intent Factor is refused with
> **422** `CONTROL_FACTOR_IN_RATEABLE_PATH` (`02` FR-88): a `control` factor is fitted to absorb
> variance and is never rated on, so no rate table is seeded from it.

**T3**, a dated note after R4 (`02-modelling.md:49-50`):

> *(Amended 2026-10-05, FD 9659.)* R4 is enforced at the approval transition by a computed flag,
> `custom_objective_not_approved`: a model whose GBM `spec.objective` names a custom objective that
> is not `approved` carries it, and `06` FR-359 refuses `approved` with `ARTIFACT_FLAGGED` (409).
> Compilation re-checks the objective (`03` FR-240), so an objective deprecated after the model's
> approval is caught there. An Admin override of the flag (FR-359) never reaches compilation:
> FR-240's refusal is independent of approval state.

**T5** (DP-7), a dated amendment appended to the FR-240 cell after T1; the ruling may fold it
into T1:

> *(Amended 2026-10-05, FD 9639.)* **A `control`-intent factor is also in a rateable path when a
> pinned model scored by a `model_call` was fitted on it**: compilation refuses the version with
> `CONTROL_FACTOR_IN_RATEABLE_PATH` (422), naming the model, the feature and the Factor, because
> scoring applies every fitted feature's effect and `02` FR-88 lets Rating Versions use only
> `risk` factors. Scoring at a declared reference level for a `control` factor is an open
> question (FD 9639), not a permission.

**T4**, a dated note after `CONTROL_FACTOR_IN_RATEABLE_PATH` in `03` §5.1's owned-code list
(`03-rating-engine.md:933`):

> *(registered 2026-10-05, FD 9697 and FD 9639: **422** at `seed-from-model` (FR-230) and at bundle
> compile (FR-240); the message names the table, the key and the Factor, or the model, the feature
> and the Factor)*

## Tasks

### Task 0: Preconditions and exposure (no code)

- [ ] **Step 1:** `pgrep -af 'pytest|vitest|flock'` shows nothing heavy, and `flock -n
  /tmp/slots/gate-1 true` and the same for `gate-2` exit 0. Quote the time.
- [ ] **Step 2:** In the worktree, `uv sync --all-packages`, then `alembic current` on the
  per-worktree DB equals the script heads (`dev-commands`). Record both revisions.
- [ ] **Step 3:** Read one row of each shape before counting: `models.spec` for a GBM with a custom
  objective (`spec->'objective'->>'kind'`, `->>'ref'`), `factors.body->>'intent'`, and a seeded
  `rate_table_versions.definition->'keys'` with its `factor_ref`. Write the two counts below against
  what the rows actually hold; if a shape differs, say so in the ledger.
- [ ] **Step 4:** In **two databases only** (DP-6 as amended, item 40): `gipricing`, the demo
  database, and the slice's own per-worktree test database. Not the other `gipricing_%`
  databases, which are scratch from ended agents. In each, count: (i) `models` with
  `status = 'approved'` whose custom objective's `custom_objectives.status <> 'approved'`; (ii)
  `rate_table_versions` with a key whose `factor_ref` names a `factors` row with `intent =
  'control'`. Record the query verbatim and each count. **If `gipricing` has any bad row, STOP and
  report to the lead with the row ids. Reset nothing and delete nothing.**
- [ ] **Step 5:** `gh pr list --state open` and a read of anything that rules on FR-240, R4,
  FR-230 or `compile.py` since this plan's tree ([`README.md`](README.md) rule 4). Name the commit
  read.

### Task 1: (a) the approval reds (Acceptance 1, 2)

**Files:**
- Create: `backend/tests/test_fr240_governance.py`

- [ ] **Step 1: Write the failing tests.** Mirror
  `backend/tests/test_model_lifecycle.py:547` (`test_a_model_whose_dataset_lost_its_standing_cannot_be_approved`):
  `service.submit_for_review`, then `approval_service.decide(..., decision=DecisionKind.APPROVE)`,
  then `pytest.raises(PlatformError)` around `service.apply_approval_decision`, then the model row
  reads `review`. For the model, reuse the harness FD 9659 §3 ran (it is measured, rule 3):
  `_expression_objective(..., approve=False)` and `_fit` from
  `backend/tests/test_expression_objective_fit.py` (`:39`, `:127`), the transparency artifact through
  `backend/tests/test_glm_approximation_model.py::_transparency_job` (`:56`), because submission
  refuses a non-GLM model without one (FR-211), and `_principal_with` from
  `test_model_lifecycle.py:104`. Set the objective to `review` with
  `backend/tests/test_custom_objectives_api.py::_advance` (`:166`) rather than raw SQL, if it
  accepts an expression row; otherwise as FD 9659 §3 did. Tests:
  - `test_a_model_whose_custom_objective_is_in_review_cannot_be_approved`: `refused.value.code ==
    "ARTIFACT_FLAGGED"`, `refused.value.status == 409`, `"custom_objective_not_approved"` and the
    objective's ref in the detail.
  - `test_an_approved_objective_can_be_approved` (control): the objective `approved` first; the
    model reaches `approved`.
  - `test_flags_for_names_an_unapproved_objective`: `await service.flags_for(...)` returns
    `(ModelFlag.CUSTOM_OBJECTIVE_NOT_APPROVED,)`.
  Markers: `req("FR-240")`, `req("FR-20")`, `req("FR-359")`.
- [ ] **Step 2:** Run `uv run pytest -q backend/tests/test_fr240_governance.py -k approv` (one file,
  under the standing rule). Expected: the first test `Failed: DID NOT RAISE`; the control passes;
  the third fails on `AttributeError` for the missing member. A different cause is a plan defect:
  stop and report.
- [ ] **Step 3: Commit** (red). `test(backend): FD 9659 — a model is approved over a review objective (FR-240, R4)`.

### Task 2: (b) and (d) the compile reds, then the transitive check (Acceptance 3, 4, 8)

**Files:**
- Create: `packages/pricing-core/tests/test_rating_compile_fr240.py`
- Modify: `packages/pricing-core/src/pricing_core/rating/compile.py`
- Modify: `backend/tests/test_fr240_governance.py`

- [ ] **Step 1: Write the pricing-core reds.** Build on `test_rating_compile_bundle.py`'s `_version`
  (`:69`), `FakeResolver` (`:92`) and `_resolver` (`:107`), as FD 9659 §Evidence 1 did:

```python
OBJ = "custom_objective:asym-loss@1"
MODEL = "model:motor-ad-frequency@7"


def _with_objective(status: str) -> FakeResolver:
    res = _resolver()
    res._payloads[MODEL]["spec"] = {"model_type": "gbm", "objective": {"kind": "custom", "ref": OBJ}}
    res._payloads[OBJ] = {"slug": "asym-loss", "version": 1}
    res._statuses[OBJ] = status
    return res


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.parametrize("status", ["certified", "review", "deprecated"])
async def test_an_unapproved_objective_reached_through_a_pinned_model_is_refused(status: str) -> None:
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED") as refused:
        await compile_bundle(_version(), _with_objective(status))
    message = str(refused.value)
    assert MODEL in message
    assert OBJ in message
    assert repr(status) in message
```

  Add `test_an_approved_objective_reached_through_a_pinned_model_compiles` (status `approved`) and
  `test_a_builtin_objective_needs_no_resolution` (`{"kind": "builtin", "ref": None}` and no `OBJ`
  payload: a resolve of `OBJ` would `KeyError`, so passing proves no lookup).
- [ ] **Step 2: Write the backend reds** in `test_fr240_governance.py`, mirroring
  `test_rating_version_compile.py:536` and its imports (`:17-22`):
  `test_a_version_pinning_an_unapproved_custom_objective_fails_to_compile` (parametrised
  `certified`, `review`; `_create`, `_advance`, `_insert_version`, `_run_compile_job`; expects
  `FAILED` and `PIN_NOT_APPROVED`), and
  `test_an_overridden_flag_never_reaches_compile` (Acceptance 4; DP-1's condition): fit the GBM
  as in Task 1 on a `review` objective, write it `approved` with
  `backend/tests/approved_rows.py::mark_approved` (the state an Admin override, or a pre-fix
  approval, leaves; the override itself is unbuilt), pin only the model, compile, expect `FAILED`
  and `PIN_NOT_APPROVED`. Task 4 Step 5 adds, before the `mark_approved`, the assert that
  `flags_for` returns `custom_objective_not_approved`, completing the chain once the member exists. The algorithm must call the model, so take the algorithm the neighbouring
  GBM compile test uses (`test_the_compiled_bundle_survives_persistence`, `:574`), not
  `_minimal_algorithm()`.
- [ ] **Step 3:** Run the pricing-core module, then `-k compile` on the backend module. Expected:
  the three parametrised cases `Failed: DID NOT RAISE`; the override test fails on the `FAILED`
  assert (the Job succeeded); the direct-pin backend cases pass (by design, Acceptance 8).
  Commit (red): `test: FD 9659 — the transitive objective compiles (FR-240)`.
- [ ] **Step 4: Implement** `_check_reachable_objectives(version, payloads, resolver)` in
  `compile.py`, called from `compile_bundle` after the pin loop. For each `ref` in
  `version.pins.models`, read `spec = payloads[str(ref)].get("spec")`; if `spec` is a mapping whose
  `objective` is a mapping with `kind == "custom"`, parse `ArtifactRef.model_validate(objective["ref"])`,
  `await resolver.resolve(...)`, and if the status is not in `_APPROVED_OR_BETTER`, `_raise_named(
  "PIN_NOT_APPROVED", f"{ref} uses {objective_ref}, which is {status!r}, not approved or better
  (FR-240, FR-20)")`. **The reading rule is deliberate**: a payload with no `spec` names no
  objective, which keeps every existing `FakeResolver` fixture valid (Acceptance 11); the backend
  resolver always returns a full `Model` dump (`rating_versions.py:474-485`), so the real path
  always has `spec`. Do not add the objective's payload to `payloads`: it is checked, not embedded,
  so `bundle_hash` is unchanged (FR-239).
- [ ] **Step 5:** Run both modules; all green. Then Acceptance 8's broken-input run: delete
  `*version.pins.custom_objectives,` from `all_refs`, run the direct-pin test, record its failure
  line, restore the line, confirm `git diff` shows no change to it.
- [ ] **Step 6: Commit.** `fix(pricing-core): compile refuses an unapproved objective reached through a pinned model (FR-240, FD 9659)`.

### Task 3: (c) control intent at compile and at seed (Acceptance 5, 6, 7)

**Files:**
- Modify: `packages/pricing-core/tests/test_rating_compile_fr240.py`, `backend/tests/test_fr240_governance.py`
- Modify: `packages/pricing-core/src/pricing_core/rating/compile.py`
- Modify: `packages/pricing-core/src/pricing_core/rate_tables/operations.py`
- Modify: `backend/src/app/platform/rating_versions.py`
- Modify: `backend/src/app/errors.py`

- [ ] **Step 1: Write the pricing-core reds**, from FD 9697 §Evidence 1, which ran: a Factor from
  `test_rate_table_operations.py::_factor` (`:376`) with `intent=FactorIntent.CONTROL`
  (`model_schema/modelling.py:111`), seeded from `_glm_model(ModelStatus.APPROVED)` (`:48`).
  - `test_seeding_from_a_control_factor_is_refused`: `seed_from_model(...)` raises `ValueError`
    matching `CONTROL_FACTOR_IN_RATEABLE_PATH`. Markers `FR-88`, `FR-230`, `FR-240`.
  - `test_a_pinned_table_keyed_on_a_control_factor_is_refused`: build the table as the seed would
    (construct the `RateTable` directly, since the seed now refuses), put it behind
    `rate_table:motor-expense@3` in `_resolver()`, put the Factor's `model_dump(mode="json")` behind
    `factor:driver_age_band@1`, and expect `CONTROL_FACTOR_IN_RATEABLE_PATH` naming the table, the
    key and the Factor.
  - `test_a_table_keyed_on_a_risk_factor_compiles` (control).
- [ ] **Step 2: Write the backend reds:** `test_the_seed_route_refuses_a_control_factor_with_its_code`
  (`POST /api/v1/rate-tables/{slug}/seed-from-model`, `03:902`; mirror the seed calls in
  `backend/tests/test_rate_tables_service.py`), and
  `test_a_compile_over_a_control_keyed_table_fails_with_its_code`, which writes the table version
  row directly (the seed refuses after Step 5) and expects `FAILED` and the code.
- [ ] **Step 3:** Run; expected `Failed: DID NOT RAISE` on the two refusal tests, `201` on the seed
  route, and a `SUCCEEDED` Job on the compile test. Commit (red): `test: FD 9697 — a control
  factor seeds and compiles (FR-240, FR-88)`.
- [ ] **Step 4: Register** `CONTROL_FACTOR_IN_RATEABLE_PATH` in `RATING_ERROR_CODES` (`errors.py:309`).
- [ ] **Step 5: Seed refusal.** In `seed_from_model`, after `bound = pinned[0]` (`operations.py:210`):
  `if bound.intent is FactorIntent.CONTROL: raise ValueError(f"CONTROL_FACTOR_IN_RATEABLE_PATH:
  Factor {bound.slug}@{bound.version} has intent 'control' and cannot be rated on (FR-88)")`.
  `_map_operation_error` (`backend/src/app/platform/rate_tables.py:83-92`) turns it into the 422.
- [ ] **Step 6: The resolver's `factor` branch.** In `_Resolver.resolve`, before the final
  `NOT_FOUND`: select `FactorRow` by `(workspace_id, slug, version)` (unique,
  `uq_factors_slug_version`, `backend/src/app/db/models.py:1335`), `NOT_FOUND` 404 if absent, and
  return `ResolvedArtifact(status="no_maturity_concept", payload=to_factor(row).model_dump(mode="json"))`
  (`to_factor`, `modelling.py:186`). A Factor has no approval lifecycle; the sentinel is RL-856's,
  and the factor is never added to the pin loop, so no maturity floor reads it. If SL-1391's
  `load_factor_by_ref` is on `main` at dispatch, use it instead of the inline select.
- [ ] **Step 7: Compile check.** `_check_control_factor_keys(version, payloads, resolver)`, called
  after `_check_reachable_objectives`: for each `ref` in `version.pins.rate_tables`, for each key in
  `payloads[str(ref)].get("keys", ())` with a `factor_ref`, resolve it and refuse
  `CONTROL_FACTOR_IN_RATEABLE_PATH` when `payload["intent"] == FactorIntent.CONTROL.value`. The same
  reading rule as Task 2 Step 4: a payload with no `keys` binds no factor.
- [ ] **Step 8:** Run both modules; green. Commit: `fix: seed and compile refuse a control-intent factor (FR-240, FR-88, FD 9697)`.

### Task 3b: (e) control intent through a `model_call` (Acceptance 13; DP-7)

Runs after Task 3, which registers the code and builds `_check_control_factor_keys`.

**Files:**
- Modify: `packages/pricing-core/tests/test_rating_compile_fr240.py`, `backend/tests/test_fr240_governance.py`
- Modify: `packages/pricing-core/src/pricing_core/rating/compile.py`
- Modify: `backend/src/app/platform/rating_versions.py`

- [ ] **Step 1: Write the pricing-core red.** `test_a_model_call_over_a_gbm_fitted_on_a_control_factor_is_refused`:
  start from `_resolver()` (`test_rating_compile_bundle.py:107`); give `model:motor-ad-frequency@7`
  a payload with `fit_result: {"model_type": "xgboost", "feature_order": ["driver_age",
  "year_of_account"], ...}` and a `factors` entry on its `ResolvedArtifact` (Step 3) holding a
  `risk` `driver_age` Factor and a `control` `year_of_account` Factor (`_factor`,
  `test_rate_table_operations.py:376`, with `intent=FactorIntent.CONTROL`). Expect `ValueError`
  matching `CONTROL_FACTOR_IN_RATEABLE_PATH` naming `model:motor-ad-frequency@7`,
  `year_of_account` and the Factor's `slug@version`. The control,
  `test_a_model_call_over_risk_factors_compiles`, is the same with both Factors `risk`. Markers
  `FR-88`, `FR-240`.
- [ ] **Step 2: Write the backend red**, `test_a_compile_over_a_gbm_fitted_on_a_control_factor_fails_with_its_code`
  (Acceptance 13). Run both; expected `Failed: DID NOT RAISE` and a `SUCCEEDED` Job. Commit (red):
  `test: FD 9639 — a model_call over a control factor compiles (FR-240, FR-88)`.
- [ ] **Step 3: Carry the Factors to compile.** `ResolvedArtifact` (`compile.py:434`) gains
  `factors: tuple[Factor, ...] = ()` (`Factor` from `model_schema.modelling`, the shape's one
  source; `pricing-core` already imports `model_schema`). The default keeps every existing
  `FakeResolver` valid (Acceptance 11). In `_Resolver.resolve`'s `model` branch
  (`rating_versions.py:464-485`), pass `factors=tuple(await load_factors(session,
  workspace_id=workspace_id, factor_ids=list(model_obj.spec.factors)))`, as
  `rate_tables.py:134-136` already does. The Bundle's payloads are not changed: the Factors are
  read at compile and not carried into the Bundle. *(Why not a key in the model payload: the payload
  is `Model.model_dump`, and a key added beside it is a second, hand-written shape inside a
  Bundle (`CLAUDE.md` §2).)*
- [ ] **Step 4: Compile check.** `_check_control_factor_model_calls(algorithm, version, resolved)`,
  called after `_check_control_factor_keys`, where `resolved` is the `ResolvedArtifact` per ref the
  pin loop already fetched (keep it beside `payloads`; never resolve a pin twice, the RL-859 note at
  `compile.py:598-602`). For each `RatingModelCallStep` with a `model_ref`, read
  `payload.get("fit_result", {}).get("feature_order", ())`, map each slug to the Factor with that
  slug in `resolved.factors`, and refuse `CONTROL_FACTOR_IN_RATEABLE_PATH` on the first with
  `intent is FactorIntent.CONTROL`. A payload with no `fit_result` or no `feature_order` binds no
  factor (Task 2's reading rule). A `peril_structure_ref` step is FD 9995's known gap (T1).
- [ ] **Step 5:** Run both modules; green. Commit: `fix: compile refuses a model_call over a control-intent factor (FR-240, FR-88, FD 9639)`.

### Task 4: (a) the flag (Acceptance 1, 2, 9)

**Files:**
- Modify: `packages/model-schema/src/model_schema/modelling.py` (`ModelFlag`, `:1984-1992`)
- Modify: `backend/src/app/platform/modelling.py` (`flags_for`, `:1049-1066`; the detail at `:1343-1351`)
- Modify: `docs/contracts/schemas/model.schema.json` (`flags`, `:175-178`); regenerate `docs/contracts/`

- [ ] **Step 1:** Append `CUSTOM_OBJECTIVE_NOT_APPROVED = "custom_objective_not_approved"` to
  `ModelFlag`, with a one-line comment citing R4 and FR-359.
- [ ] **Step 2:** `flags_for` collects flags instead of returning early: the existing dataset check,
  then, for a model whose `row.spec` has `objective.kind == "custom"`, `resolve_ref(session,
  workspace_id=workspace_id, ref=...)` from `app.platform.objectives` (`:516`), imported
  function-locally as the module already does at `modelling.py:596` (`from app.platform import
  objectives as objective_service`), and the flag when its status is not `ObjectiveStatus.APPROVED` (DP-5). Keep
  the order: dataset first. Update the docstring: two flags, both computed.
- [ ] **Step 3:** The `ARTIFACT_FLAGGED` detail names each flag with its own reason (FR-205 for the
  dataset; R4 and the objective ref for the objective). The code and status are unchanged, so
  `test_model_lifecycle.py:547` passes unchanged.
- [ ] **Step 4:** `model.schema.json` `flags.items.enum` gains `custom_objective_not_approved`, and
  its description a dated note (R4, FD 9659). Run `uv run python scripts/generate-contracts.py`,
  then `--check`; run `uv run pytest -q backend/tests/test_contracts.py`.
- [ ] **Step 5:** Add the flag assert to `test_an_overridden_flag_never_reaches_compile` (Task 2
  Step 2). Task 1's three tests and that test green. **Steps 1 to 4 land in this one commit**: the
  `ModelFlag` member, `model.schema.json` and the regenerated contracts together (item 35). Commit: `fix(modelling): a model over an unapproved custom objective is flagged and cannot be approved (R4, FR-359, FD 9659)`.

### Task 5: The frontend half

- [ ] **Step 1:** `pnpm --dir frontend generate:api`, then `lint`, `type-check`, `test`. `ModelFlag`
  reaches the generated client; at `83ea5090` nothing under `frontend/src` names
  `dataset_invalidated`, so no exhaustive switch should break. If one does, it is a finding for the
  lead, not a silent widening of this slice.

### Task 6: The spec texts, verbatim from the ruling

**Files:**
- Modify: `docs/specs/03-rating-engine.md` (FR-230 `:121`, FR-240 `:137`, the seed route row `:902`, the owned-code list `:933`)
- Modify: `docs/specs/02-modelling.md` (R4, `:49-50`)

- [ ] **Step 1:** Apply the ruling's T1, T2, T3, T4 and T5. Use the ruling's text where it differs from
  §"Spec texts". Escape any `|` as `\|`.
- [ ] **Step 2:** `python3 scripts/audit-docs.py`: exit 0, or only the working-id check 31 rows the
  lead expects. Check 10 must agree on `CONTROL_FACTOR_IN_RATEABLE_PATH` (Acceptance 7).
- [ ] **Step 3: Commit.** `docs(spec): FR-240 transitive and control clauses; FR-230 seed refusal; R4 enforced by flag (FD 9659, FD 9697)`.

### Task 7: The gate and the ledger

- [ ] **Step 1:** The full two-half gate (Acceptance 11), in a gate slot under `RL-1263`. Record
  each command's exit code and the tree it ran on.
- [ ] **Step 2:** The ledger `docs/ledgers/LG-<n>`: every red with its failure line, the
  broken-input line (Acceptance 8), Task 0's query and counts, the commit SHAs in order, any stop
  raised. Regenerate `docs/INDEX.md`.

## Hand-off

1. **FD 9697's and FD 9659's register rows**, and clauses (5) and the transitive half of register
   row `FR-240 (F-W9-3)` (`docs/findings/register.md:61`), are discharged by the merge. The auditor
   writes those rows, not this slice.
2. **DP-4 (c)**, a `model_call` over a model that fits a `control` factor, is FD 9639 (working id,
   #1156). This slice refuses it (DP-7). **Neutralisation is not built**: the open question
   (`dm-9639oq`) goes to the maintainer, and a (b) or (c) answer is a spec change, then its own
   slice under WK-673 (the 14:46:53 entry, item 3). FD 9639's register row is the auditor's.
3. **FR-359's Admin override** is built for no flag. Whoever builds it re-points
   `test_an_overridden_flag_never_reaches_compile` at the real override instead of `mark_approved`;
   the assertion (compile refuses) does not change. That is a pre-existing spec-versus-code gap,
   not widened here; the lead decides whether it is a finding.
4. **For SL-1391 (PL 9716):** if this slice merges first, its `load_factor_by_ref` can replace
   Task 3 Step 6's inline select. That is a note for its dispatch, not an edit to it.

## Self-review

- **Spec coverage.** (a) is Tasks 1 and 4; (b) Task 2; (c) Task 3; (d) Task 2 Steps 2 and 5; (e) Task 3b. Every
  row of §"Requirement coverage" has a task. Every DP names the tasks it blocks.
- **Ruling sites.** Each DP's recommendation appears in narrative (§"Decision points"), Files and
  Steps (Tasks 1-6, and 3b) and Acceptance (1-13). Items 35–40 and the lane placement were applied at all
  four, by grepping each condition's subject (override, peril, FD 9995, metrics, registered,
  `rateable`, `gipricing`, `deprecated`, lane) over the whole file.
- **Literals checked at `83ea5090`**, by grep, not recalled: the line numbers in §"Goal" and
  §"Write set"; the helpers `_version` `:69`, `FakeResolver` `:92`, `_resolver` `:107`
  (`test_rating_compile_bundle.py`); `_insert_version` `:86`, `_run_compile_job` `:113`
  (`test_rating_version_compile.py`); `_create` `:156`, `_advance` `:166`; `_principal_with` `:104`,
  `_approve` `:663`; `_expression_objective` `:39`, `_fit` `:127`; `_transparency_job` `:56`;
  `mark_approved` (`approved_rows.py:91`); `_fitted_gbm` (`test_model_jobs_gbm.py:88`); `_factor`
  `:376` and `_glm_model` `:48` (`test_rate_table_operations.py`); the codes at `errors.py` and
  `03:933`.
- **DP-7's literals** were read by grep at `982ab531` (this plan's branch, whose code equals
  `83ea5090`: the branch changes only this plan and `docs/roadmap.md`): `runtime.py:512`, `:565`;
  `GbmFitResult.feature_order` `:1671`, `Factor.intent` `:143`, `ModelSpecCommon.factors` `:842`
  (`model_schema/modelling.py`); `gbm.py:301-302`; `ResolvedArtifact` `compile.py:434`; the `model`
  branch `rating_versions.py:464-485`; `load_factors` `modelling.py:284`; `rate_tables.py:134-136`;
  `RateTable.rateable` `model_schema/rating.py:714`.
- **Not run.** No sample here was executed by the planner. Task 2's sample is FD 9659 §Evidence 1's
  run reshaped into a test; Task 3's is FD 9697's. Task 1's harness is FD 9659 §3's.
- **Placeholders.** None in the pricing-core samples. The backend tests are steps over named neighbours rather than full code, because
  their fixtures need Postgres, MinIO and real fits the planner did not run (rule 3).
