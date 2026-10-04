---
id: LG-9731
family: ledger
title: WK-690 slice SL-1273 — the expression kind through the platform, behind the flag, with custom_objective:author (PL-1382, RL-1362)
status: active
created: 2026-10-04
owner: executor
tree: 663433e4c38578239ca5abf15a716bef929e82cc
phase: P2
work: WK-690
slice: SL-1273
plans: [PL-1382]
corrected_by: []
relates: [RL-1362, RL-1265, RL-1305, RL-1263, FD-1349, PL-1268, FR-144, FR-145, FR-150, FR-207]
---

# LG 9731 (working id) — WK-690 slice SL-1273, the expression kind through the platform

Executed from `PL-1382` by `executor-1273` (sonnet; `echo $CLAUDE_EFFORT` printed `medium`). Branch
`sl-1273-custom-objective-expression`. Stamps are BST (`TZ=Europe/London date`). The ledger's working id is `9731`,
reserved by the lead 2026-10-04 17:15:20 BST (dispatch Delta 1); it is renumbered at the mint. This ledger covers
**Tasks 0 and 1** (the first executor turn); later tasks are appended.

The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the
lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a cheaper setting."

## Tasks

### Task 0 — preconditions

**Dispatch record.** `gi-pricing-plan.local/handover/DISPATCH-WK-690-SL1273-2026-10-03.md`, FINAL (2026-10-04
16:54:51 BST) with Delta 1 (17:15:20 BST), is the authority; it is local and not in the repository. It rules the
write set (PL-1382's plus RL-1362's widening, its B2), applies RL-1362's texts byte for byte (RL-1362:634), holds
FD 9780 (S3 carries its fix in Task 7) and constrains FD 9752 (S3's `approvals.py` `submit` edit must not change or
newly read the four `to_dict` routes' responses). The lead's DP-S3-6 verdict is (a): FD-1349's follow-up is Task 9.
This turn does Tasks 0 and 1 only.

**Base.** `git rev-parse origin/main` printed `663433e4c38578239ca5abf15a716bef929e82cc` (#1106, the activation).
`uv sync --all-packages` ran clean. Worktree `…/tmp/wt-1273`, branch `sl-1273-custom-objective-expression`.

**Box.** 2026-10-04 17:19:33 BST: `uptime` load average 3.63, 2.78, 1.86; `free -h` Mem 31Gi total, 20Gi free. Another
slice's gate (gate-1) was running; only targeted tests ran. Main's slotted pytest total and wall time (Acceptance 13)
are **not taken** here: the timing order forbids a full suite beside lane B's gate. They belong to Task 11's gate.

**Activation needs, run at `663433e4`.** The dispatch record's run (at `dfddfad8`) is the one the plan asks for;
re-run here at the base: need 3, `git ls-tree -r --name-only origin/main tests | grep parity` printed
`tests/test_permission_parity.py`, and `git grep -l STALE_OWNER origin/main -- tests` printed
`origin/main:tests/test_permission_parity.py`. Need 6, the plan and slice read `active` (the activation PR #1106).

**Premises a to u, re-derived at `663433e4`** (anchors, not line numbers; several line numbers have drifted by a few
lines and none of the premises has changed):

| Premise | Re-derived |
|---|---|
| a | `platform/objectives.py` `refuse_expression_kind` still resolves the flag then raises `OBJECTIVE_KIND_NOT_ENABLED` |
| b | `api/custom_objectives.py`: `FitModels` `:76`, `SubmitModels` `:77`; create `:229`, derive `:291`, certify `:315`, submit `:381`; create and derive take `caller: FitModels` |
| c | `features.expression_objectives_enabled` at `settings.py:245`, `SAFE_DEFAULT` `False` at `:273` |
| d | `grep -c custom_objective:author` of `permissions.py` at base printed `0` |
| e | The parity module now exists (`tests/test_permission_parity.py`); the plan's premise e (none exists) is superseded by SL-1360 |
| k | `errors.py` holds `OBJECTIVE_KIND_NOT_ENABLED` (`:190`) and none of `OBJECTIVE_GRAMMAR_VIOLATION`, `OBJECTIVE_NOT_CERTIFIED` |
| q | CHECK `custom_objective_is_a_template_in_phase_1` is at `db/models.py:1766` (plan: `:1760`); the trigger function is in `d0e1f2a3b4c5_custom_objectives.py` |
| t | the ladder predicate printed `0` over the plan's four paths |
| u | a `git grep` for `bound_symbols` and for the `loss` field over `frontend/src` printed no CustomObjective reader (the hits were prose) |
| s | marker counts at base: FR-144 15, FR-146 23, FR-150 5, FR-152 7, FR-163 6, FR-207 4, FR-366 0, FR-367 0, FR-448 3, FR-449 4, NFR-480 0, NFR-484 3 (the plan's counts, unchanged) |

Premises f, g, h, i, j, l, m, n, o, p, r were not re-derived beyond what Task 1 read (f, g, r's
`test_objectives.py:101`); they bind Tasks 2 to 8 and are re-derived by the executor of the task that uses each, as
the plan says ("stops on any that no longer holds").

**Open PRs** (`gh pr list --state open`, read 2026-10-04 17:2x BST at origin/main `663433e4`): 15 listed (#1048 to
#1075, among them the dependabot bumps #1074 and #1075). A filter of each PR's file list against
`custom_objective|objectives|permissions|06-governance|02-modelling|approvals|errors.py|test_contracts|ObjectivePicker|model.schema|model-spec.schema|migrations`
matched none of them.

**File contention, lane B** (`git diff --name-only origin/main origin/sl-1386-dislocation-run`, branch at
`320d8f0b8cb518d56fea7596c0b3141a9dc650ff`): `docs/INDEX.md`, `docs/contracts/schemas/dislocation-run.schema.json`,
that slice's own ledger, `PL-1382` (the branch is based before #1106, so it shows the activation as a difference),
`docs/roadmap.md`, `docs/specs/03-rating-engine.md`, `model_schema/dislocation.py`, `test_dislocation.py`,
`pricing_core/rating/analysis.py`, `test_rating_dislocation.py`. The overlap with this slice's
`git diff --name-only origin/main..HEAD` is empty at this commit; the shared registry-exempt files (`docs/INDEX.md`,
the generated contracts) are regenerated by whichever merges second.

**Ledger id note.** The dispatch said to model this ledger on the latest ledger on main, naming WK-673 Slice 2's. That ledger (not
yet on main) is on lane B's branch, not on main; main's latest ledger is `LG-1405`. The form is taken from that
unmerged ledger and from this slice's own first form (`git log --all`), which carry the same header. Corrected
2026-10-04: the earlier wording cited ids that do not resolve on main.

### Task 1 — the contract's `expression` arm

**Red, quoted (base `663433e4`, `uv run pytest packages/model-schema/tests/test_objectives.py -q -k expression`):**
`7 failed, 1 passed, 39 deselected in 1.36s`. The first failure line of the rewritten spec-example test is
`pydantic_core._pydantic_core.ValidationError: 4 validation errors for Custo…` (`bound_symbols`, `parameters`,
`loss`, `derived`: "Extra inputs are not permitted [type=extra_forbidden …]"). **Plan-text deviation, reported:**
Task 1's Red step says the test fails "because `_only_templates_are_built` raises 'Phase 1 ships templates only'" and
that any other reason is a plan defect. A test that passes the four new fields cannot reach that validator at the base,
because `extra="forbid"` refuses the unknown fields first; the refusal named is therefore `extra_forbidden` on exactly
the four fields Task 1 adds, i.e. each field the arm lacks, not a wrong field name. The old test, `-k templates_only`
behaviour, is the one that reached the validator, and it is replaced.
The other red failures at the base, by test:
`test_a_template_objective_has_none_of_the_expression_fields` — `AttributeError: 'CustomObjective' object has no
attribute 'bound_symbols'`; `test_a_template_with_a_loss_is_refused` (renamed
`test_a_template_with_an_expression_loss_is_refused`, so that `-k expression` selects it) — `Expected regex: 'a
template objective carries no loss'`; the template-with-expression, derived-without-loss, 2000-character and
parameter-range tests each — `AssertionError: Regex pattern did not match.` against the same `extra_forbidden` text.

**Green.** `ObjectiveParameter` (`name` pattern `^[a-z_][a-z0-9_]*$`, `type` `Literal["float", "int"]`, `default`,
`min`, `max`, `min <= default <= max`) and `DerivedBlock` (`gradient`, `hessian`, `derivation_tool: Literal["sympy"]`,
`derivation_version`, `derived_at: AwareDatetime`), copied from `custom-objective.schema.json:47-80`;
`CustomObjective` gains `bound_symbols`, `parameters`, `loss` (`max_length=2000`), `derived`; one validator,
`_each_field_belongs_to_one_arm`, replaces `_only_templates_are_built`. **Deviation:** the plan's parenthetical says
`type: Literal["float"]`; the authored schema (`:57`, the plan's own instruction is "copied from the schema, not from
this text") says `enum ["float", "int"]`, so the model takes both. `uv run pytest
packages/model-schema/tests/test_objectives.py -q`: `47 passed`.

**Contract guard.** `DECLARED_AND_UNBUILT["custom-objective"]` is removed (the four fields) and its note bullet
rewritten. At the base the guard was **not red** with the exemption in place (`150 passed, 2 skipped`), because the
exemption only subtracts; the plan's removal step has no natural red. **Broken-input proof:** with the exemption
removed, rename the model field `loss` to `loss_x` in `objectives.py` and regenerate: `uv run pytest
backend/tests/test_contracts.py -q` printed `E       AssertionError: the contract declares fields the model
lacks: ['loss']` and `1 failed, 149 passed, 2 skipped` (the failing test
`test_an_artifact_shape_carries_exactly_what_its_contract_declares[custom-objective]`); restored (`git diff` of
`objectives.py` over that line empty), the guard is `150 passed, 2 skipped`. No disagreement with the hand-authored
file was found, so it is not edited.

**Other.** `uv run python scripts/generate-contracts.py` regenerated `docs/contracts/openapi/generated.json` and
`docs/contracts/schemas/generated/custom-objective.schema.json`; `--check` printed `45 generated contracts match the
models`. `ruff format` was run on the four changed Python files, which were not format-clean at the base (the check
over `git show origin/main:<path>` returned 1 for `objectives.py`, `test_objectives.py` and `test_contracts.py`), so
the diff of those three carries format churn beside the change. `uv run pytest packages/model-schema
backend/tests/test_contracts.py -q`: `650 passed, 2 skipped`. The refusal of an expression objective elsewhere
(`OBJECTIVE_KIND_NOT_ENABLED`, the DB CHECK, the compile dispatch) is unchanged in this task.

### Task 1, correction (Delta 2, lead 2026-10-04 17:22:36 BST)

The Task 1 entry's "ruff format was run on the four changed Python files" is superseded: the lead did not adopt the
churn. Every formatting-only hunk in `backend/tests/test_contracts.py`, `packages/model-schema/src/model_schema/objectives.py`
and `packages/model-schema/tests/test_objectives.py` is reverted to `origin/main` (`663433e4`), keeping each semantic
change. `git diff --stat` and `git diff -w --stat` of `origin/main..HEAD` over the three files plus `__init__.py` now
agree: 4 files changed, 193 insertions, 37 deletions, both. `uv run pytest packages/model-schema
backend/tests/test_contracts.py -q`: `650 passed, 2 skipped`.

### Task 2 — storage

**Red.** `backend/tests/test_custom_objectives_expression.py` (new), `-k storage`, 11 tests against the migrated
per-worktree database. At the base all 11 fail with the same line, `asyncpg.exceptions.UndefinedColumnError: column
"bound_symbols" of relation "custom_objectives" does not exist`. **Plan defect (recorded):** the plan's red says the
expression insert fails "naming `custom_objective_is_a_template_in_phase_1`"; with the four columns absent the insert
fails on the column first. The CHECK refusal is shown separately at the base by `psql` on an expression insert with no
new column: `ERROR:  new row for relation "custom_objectives" violates check constraint
"ck_custom_objectives_custom_objective_is_a_template_in_phase_1"`. The constraint carries the `ck_<table>_` prefix of
`NAMING_CONVENTION` (`db/base.py:19`).

**Green.** `CustomObjectiveRow` gains `bound_symbols`, `parameters` (JSONB), `loss` (Text), `derived` (JSONB), all
nullable. Revision `e5b7d9f1a3c6` (down `c4a81f6d2e95`; the plan names `2f598e89d12c` as head, which WK-674 Slice 2
moved on) drops `custom_objective_is_a_template_in_phase_1` and adds `custom_objective_fields_follow_kind` (the plan's
unnamed kind-arm CHECK; `ck_custom_objectives_` plus the longer name `…fields_belong_to_the_kind_arm` is 67 characters,
over PostgreSQL's 63, and alembic hashed it in a first attempt): a `template` row needs `template` and carries no
expression field (`derived` included), an `expression` row needs `loss`, `bound_symbols`, `parameters` and no
`template`. The trigger function `custom_objectives_definition_immutable` gains `loss`, `parameters` and
`bound_symbols`, and refuses a `derived` change unless it goes from NULL while `OLD.status = 'draft'`. Downgrade
restores the old function and CHECK and refuses while an expression row exists (shown by hand: `cannot downgrade:
expression Custom Objectives exist (02 FR-164)`, head stays `e5b7d9f1a3c6`). RL-1362 has no amendment to Task 2.

**Result.** `-k storage`: `11 passed`. `alembic heads` prints one head, `e5b7d9f1a3c6`; upgrade, downgrade, upgrade ran
on the per-worktree database. `backend/tests/test_custom_objectives.py`, `_api.py`, `_expression.py`, `test_contracts.py`:
`205 passed, 2 skipped`. A first test used `status = 'approved'` and was stopped by the FR-351 approval trigger, so the
write-after-draft test uses `certified`.

**Broken-input proof.** In the migration's trigger, `AND (OLD.derived IS NOT NULL OR OLD.status <> 'draft')` replaced
by `AND OLD.derived IS NOT NULL`, upgraded: `FAILED …::test_storage_derived_cannot_be_first_written_after_the_draft`,
`1 failed, 10 passed`. Restored by copying the saved file back, re-upgraded: `11 passed`.

**Format.** `ruff format` ran only on the two new files; `backend/src/app/db/models.py` was not format-clean at the
base (`ruff format --check` on `git show origin/main:` of it reported it would reformat) and was not formatted.

## PRs

None yet: the branch is pushed, no PR is opened (the lead's order for this turn).
