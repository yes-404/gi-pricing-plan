---
id: LG-1412
family: ledger
title: WK-690 slice SL-1273 — the expression kind through the platform, behind the flag, with custom_objective:author (PL-1382, RL-1362)
status: closed
created: 2026-10-04
owner: executor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
phase: P2
work: WK-690
slice: SL-1273
plans: [PL-1382]
corrected_by: []
relates: [RL-1362, RL-1265, RL-1305, RL-1263, FD-1349, PL-1268, FR-144, FR-145, FR-150, FR-207]
---

# LG-1412 — WK-690 slice SL-1273, the expression kind through the platform

Executed from `PL-1382` by `executor-1273` (sonnet; `echo $CLAUDE_EFFORT` printed `medium`). Branch
`sl-1273-custom-objective-expression`. Stamps are BST (`TZ=Europe/London date`). The ledger's working id was `9731`,
reserved by the lead 2026-10-04 17:15:20 BST (dispatch Delta 1); it was minted as `LG-1412` on 2026-10-05. This ledger covers
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

### Task 3 — `custom_objective:author`, its `06` row and its checks

**Red 1 (the parity check, member only added).** `uv run pytest tests/test_permission_parity.py -q -x`:
`1 failed, 10 passed`; `AssertionError: permission parity (CR-1247 P1 (c)):` with
`enum member with no 06 §4.1 Built row: custom_objective:author` and `Specified name is an enum member: move its row
to Built in the same commit: custom_objective:author`.

**Red 2 (the routes, member kept).** `uv run pytest backend/tests/test_custom_objectives.py backend/tests/test_rbac.py
-k "author or template_create_with"`: `2 failed, 4 passed`. Both failures are
`assert 409 == 403` on `test_creating_an_expression_objective_without_author_is_403` and
`test_deriving_without_author_is_403`, the body being `"code":"OBJECTIVE_KIND_NOT_ENABLED"` (the caller reached the
refusal). The four that pass at the base are the DP-S3-2 controls and the no-built-in-role test: author without
`model:fit` on create and on derive (403 from the existing route dependency), author with `model:fit` (409 refusal),
template create with `model:fit` alone (201), and `test_no_builtin_role_holds_custom_objective_author`.

**Green.** `permissions.py`: `CUSTOM_OBJECTIVE_AUTHOR = "custom_objective:author"`, granted to no built-in role. `api/custom_objectives.py`:
derive gains `AuthorObjectives = requires(Perm.CUSTOM_OBJECTIVE_AUTHOR)` beside `FitModels`; create calls
`rbac.require_permission(…, permission=Perm.CUSTOM_OBJECTIVE_AUTHOR, credential_permissions=caller.permissions)` for a
non-template kind, before `refuse_expression_kind`. `06` §4.1: the row moves from Specified to Built (Check owner empty),
and RL-1362's S1 text is appended to FR-367 byte for byte, with `<Task 3 date>` = 2026-10-04. The FR-366 discharge note the
plan's Task 3 lists is **not written**: RL-1362 gives no text for it, its S1 is FR-367's only, FR-366 already reads
"Amended 2026-08-18: the trigger is discharged", and RL-1362:634 makes any executor wording a stop. `docs/contracts/openapi/generated.json`
regenerated: one line, the new enum value.

**Re-pointed tests (quoted).** `test_deriving_without_model_fit_is_refused` (`:617`) is unchanged, as ruled.
`test_deriving_refuses_by_name_rather_than_pretending_the_concept_is_unknown` granted `analyst` and expected 409; with the
check in it failed `AssertionError: {"type":"…permission-denied…` (403), and now uses a caller holding `model:fit`,
`model:read` and author. `test_creating_an_expression_objective_is_refused_by_name` (`test_custom_objectives_api.py`) is
re-pointed the same way (an `expression_author` fixture); it was not run red, it follows by construction.

**Result.** `tests/test_permission_parity.py`, `backend/tests/test_custom_objectives.py`, `_api.py`, `test_rbac.py`: `86 passed`.

**Broken-input proofs** (each restored by copying the saved file back; `git diff` equal to before): derive without the
author dependency: `FAILED test_deriving_without_author_is_403`, `1 failed, 45 passed`. Create without the author check:
`FAILED test_creating_an_expression_objective_without_author_is_403`, `1 failed, 45 passed`. `analyst` holding the member:
`FAILED test_creating_…_without_author_is_403`, `test_deriving_without_author_is_403`,
`test_rbac.py::test_no_builtin_role_holds_custom_objective_author`, `3 failed, 59 passed`. Derive's `FitModels` replaced by
the author dependency alone: `FAILED test_author_without_model_fit_is_refused_on_create_and_derive`, `1 failed, 61 passed`.
The `06` Built row deleted: `FAILED tests/test_permission_parity.py::test_live_tree_has_no_parity_violations`,
`1 failed, 61 passed`.

**Format.** No `ruff format` on any existing file; the added hunks are format-clean (`ruff format --diff` hunk counts for
the three test files equal the base's: 17, 8, 6).

### Task 4 — the flag made liftable; create and derive; `OBJECTIVE_GRAMMAR_VIOLATION`; the derivation event

(2026-10-04 BST, `executor-1273d`, sonnet, `echo $CLAUDE_EFFORT` = `medium`; per-worktree database
`gipricing_wt-1273d_706402dd`.)

**Plan defect found.** The plan's red expects the set-true cases to fail with 409 `OBJECTIVE_KIND_NOT_ENABLED`, but Task 3 did
not add the expression fields to `CreateCustomObjective` (the plan's write-set row lists them under tasks 3 and 4). First run,
`uv run pytest backend/tests/test_custom_objectives_expression.py backend/tests/test_custom_objectives.py
backend/tests/test_custom_objectives_api.py -k "flag or derive or grammar or refused_by_name"`: `10 failed, 6 passed`, each
create answering 422 `VALIDATION_FAILED` with `errors` for `bound_symbols`, `parameters`, `loss`
`EXTRA_FORBIDDEN` (the wrong cause). The three body fields were added (no behaviour) and the reds re-taken.

**Red (the right cause).** Same command: `8 failed, 8 passed`. Failure lines: `test_flag_true_accepts_create_as_an_underived_draft`
`assert 409 == 201` (body `OBJECTIVE_KIND_NOT_ENABLED`); `test_derive_stores_what_pricing_core_derives_stamped_and_audited`,
`test_derive_stores_the_installed_sympy_version` and `test_grammar_violation_is_not_raised_for_a_valid_loss`, each
`assert 409 == 201` on the create; `test_derive_refuses_a_template_objective_and_a_second_derivation`
`assert 'OBJECTIVE_KIND_NOT_ENABLED' == 'VALIDATION_FAILED'`; `test_grammar_violation_is_422_with_the_position_in_errors` and
`test_grammar_violation_covers_text_that_does_not_parse` `assert 409 == 422` (the grammar case fails with the 409, not with a
grammar code); the rewritten service test `test_an_expression_objective_is_refused_by_name_while_the_flag_is_off` raised
`app.errors.PlatformError: ... Phase 1 ships `template` objectives only` in its set-true step. The unset and `false` cases
pass at the base (the refusal was unconditional), as Acceptance 4 predicts.

**Rewritten tests.** `test_an_expression_objective_is_refused_by_name_whether_the_flag_is_on_or_off` is now the three flag
cases (unset, `false`, `true`); `test_deriving_refuses_by_name_rather_than_pretending_the_concept_is_unknown` and
`test_creating_an_expression_objective_is_refused_by_name` are renamed `..._while_the_flag_is_off` and keep their
(unset-flag) assertions; `test_author_with_model_fit_still_reaches_the_unconditional_refusal` is renamed
`..._reaches_the_flag_refusal`.

**Green.** `refuse_expression_kind` returns unless the resolved value `is True`. `create_objective` takes the expression fields,
validates the contract first, then parses `loss` in the `objective` profile (`_require_the_grammar`), storing `derived = NULL`.
`OBJECTIVE_GRAMMAR_VIOLATION` is 422 with one `FieldError` on `loss` whose message starts `line <L>, column <C>:` (RL-1362
DP-S3-3 (1)); no problem extension. New `derive_objective` (route: `model:fit` + author, then the flag, then the service) refuses
a template, a non-`draft` and an already-derived objective with 409 `VALIDATION_FAILED`, stores `DerivedBlock` with
`derived_at = datetime.now(UTC)`, and records `custom_objective.derived` with `before {"derived": None}`. `to_objective`
returns the four expression fields. `errors.py` registers the code. `models.py`: the four JSONB expression columns gain
`none_as_null=True` (an ORM `None` stored JSON `null`, which the Task 2 CHECK `IS NULL` refused: 37 failures in the three
files until fixed). `02`: S2's marker removal (byte for byte), the §5.1 derive row, a dated FR-150 amendment, a dated note on the
stale "refused for the whole of Phase 1" bullet. `docs/contracts/openapi/generated.json` regenerated; `docs/INDEX.md`
regenerated (`doc-index.py`) for the FR-150 row.

**Result.** The three files: `69 passed`. `test_contracts.py test_rbac.py test_errors.py` and the approvals tests run with the checks below.

**Broken-input proofs** (each restored from a saved copy; `git diff` sha identical after): the flag check forced to refuse:
`8 failed, 7 passed` (the eight Red tests, `assert 409 == 201`/`409 == 422`). Column without the 1-based `+1`:
`FAILED test_grammar_violation_is_422_with_the_position_in_errors`, `1 failed, 2 passed`. Audit action renamed:
`FAILED test_derive_stores_what_pricing_core_derives_stamped_and_audited` (`assert 0 == 1`). The already-derived guard dropped:
`FAILED test_derive_refuses_a_template_objective_and_a_second_derivation` (`assert 500 == 409`). `derivation_version` hardcoded:
`FAILED test_derive_stores_the_installed_sympy_version`.

**Deviations from the plan, for the auditor.** (1) A `SyntaxError` from the loss (text that is not Python) is the same 422
refusal, positioned by `SyntaxError.lineno`/`offset`; the plan names only `ExpressionError`. (2) An `ExpressionError` raised by
`derive` itself (a node SymPy cannot print into the grammar) is also 422 `OBJECTIVE_GRAMMAR_VIOLATION` on `loss`. (3) A create
of `kind: expression` without `applicability` is 422 `VALIDATION_FAILED` (no template to default from). (4) A second derive is
409 `VALIDATION_FAILED`. (5) The module and route docstrings' pre-migration `FR-MODEL-` ids were replaced with
FR-142/144/146/150/163/166, read from the spec's own headings. (6) No `ruff format` on any existing file; touched hunks are
format-clean (objectives.py 4 hunks, base 4; test_custom_objectives.py 17, base 17).

### Task 5 — certification of an expression

(2026-10-04 BST, `executor-1273e`, sonnet, `echo $CLAUDE_EFFORT` = `medium`; per-worktree database `gipricing_wt-1273e_366b231b`.)

**Red, quoted** (`uv run pytest backend/tests/test_custom_objectives_expression.py -k certify`, base `d7b7f0c4` plus the two tests):
`2 failed`. (1) `test_certify_refuses_an_underived_expression_before_a_job_exists` failed `AssertionError: {"id":"01a107d8-…","workspace_id"…`,
a 202 job body where 409 was expected. (2) `test_certify_runs_a_derived_expression_as_the_existing_job` failed
`assert <JobStatus.FAILED: 'failed'> is <JobStatus.SUCCEEDED…`; the job log's last frame is `compile_objective`
(`objectives.py:739`, `raise ObjectiveError`), reached from `certify_objective` through `_certify`, the plan's stated cause.

**Green.** `certifiable_or_refuse` refuses `kind == "expression"` with `derived is None` as 409 `VALIDATION_FAILED`, `detail` naming
`POST /api/v1/custom-objectives/{id}/derive`, before `job_service.submit` (RL-1362 DP-S3-3 (2)). `_certify` dispatches an expression to the
new `_certify_expression`, which passes the stored `loss`, parameter defaults, the stored `derived` (as `Derived`, without `derived_at`),
`y_domain`, strategy, `hessian_min`, `default_sampling`'s grid from the job parameters, and `inverse_link_for(applicability.responses)`.
`inverse_link_for` is new in `pricing_core/modelling/expression_objective.py`: logistic when every response is a probability response,
else exp, the split `default_sampling` already draws its grid by; DP-S3-1 asks certify and the fit to read the link through one function,
and Task 6 is to call it. `record_certificate` is unchanged. `02` §5.1 certify row: RL-1362's S3 byte for byte, `<Task 5 date>` = 2026-10-04.
Result: the file `22 passed`; with `test_custom_objectives.py`, `_api.py` and `packages/pricing-core/tests/test_expression_objective.py`
`83 passed` after one fix (my no-job-row count was database-wide, not per workspace; scoped to `workspace_id`).

**Broken-input proofs** (each restored, `cmp` against the saved copy equal): the route guard replaced by `if False:`:
`FAILED test_certify_refuses_an_underived_expression_before_a_job_exists`, `1 failed, 1 passed`. The `_certify` expression dispatch replaced by
`if False:`: `FAILED test_certify_runs_a_derived_expression_as_the_existing_job`, `1 failed, 1 passed`. `inverse_link_for` returning `"exp"`
always: `FAILED test_certify_inverse_link_follows_the_applicability_responses`, `AssertionError: assert 'exp' == 'logistic'`, `1 failed, 11 deselected`.

**Deviations and notes for the auditor.** (1) Executor-worded spec sentences: none; the only `docs/` edit is S3. (2) The plan's Task 5 Green
lists `default_sampling`; it needed no change (it already reads the applicability). (3) No test pins that the *stored* `derived` text, rather
than a re-derivation, is certified: the trigger makes `derived` write-once, so the two cannot be told apart through the API, and the code
path passes the stored block. (4) A mixed-link applicability (probability and non-probability responses together) is certified on the exp
link, as `default_sampling` already treats it; no refusal is added, since RL-1362 and the plan name none and every `ResponseKind` is log or logit.
(5) Template certify is untouched: its existing tests pass unmodified.

### Task 6 — fit-time compilation, and the fit job's coded errors

(2026-10-04 BST, `executor-1273f`, sonnet, `echo $CLAUDE_EFFORT` = `medium`; per-worktree database `gipricing_wt-1273f_8fb4b735`.)

**Red, quoted.** `-k compile_dispatch` in `packages/pricing-core/tests/test_objectives.py` (base `a0f545be` plus the tests): `5 failed`, each
`ObjectiveError: objective test-expression@1 is not a template objective. Phase 1 compiles templates only (FR-150).` (`compile_objective`'s
`OBJECTIVE_KIND_NOT_ENABLED`); the underived test failed `Regex pattern did not match … no stored derivation`. Backend
`backend/tests/test_expression_objective_fit.py`, the objectives change reverted to base: `4 failed`: the two fits
`assert <JobStatus.FAILED: 'failed'> is <JobStatus.SUCCEEDED: 'succeeded'>`; the two error cases `assert 'OBJECTIVE_KIND_NOT_ENABLED' ==
'OBJECTIVE_NO…TE_DERIVATIVE'` and `… == 'OBJECTIVE_RO…DGET_EXCEEDED'`. With the compile in and the worker mapping not yet written, the two error
cases failed `assert 'JOB_HANDLER_FAILED' == 'OBJECTIVE_NONFINITE_DERIVATIVE'` and `… == 'OBJECTIVE_ROUND_BUDGET_EXCEEDED'`.

**Green.** `compile_objective` sends `kind: expression` to `_compile_stored_expression` (`objectives.py`), which passes the stored `derived` block
(as `Derived`) to `compile_expression_objective` and never takes its `derived=None` path; an expression with `derived` null is refused by name
(`ObjectiveError`, code `OBJECTIVE_KIND_NOT_ENABLED`, the code the function's existing guard used). The link is `inverse_link_for(applicability.responses)`,
the function `_certify_expression` calls. The status gate (`gbm._compile_custom`) is untouched. `model.fit` maps `NonFiniteDerivativeError` and
`RoundBudgetExceededError` to `PlatformError(exc.code, …, 409, str(exc))`; both codes are in `MODELLING_ERROR_CODES`; `02` §5.1's two
"(declared, Phase 2)" markers are removed. Result: `141 passed` (the objectives, fit, errors and expression-storage files).

**"Stored, not re-derived" is shown here**, which Task 5 could not show: `test_compile_dispatch_uses_the_stored_derived_text_and_never_re_derives`
stores a hessian that differs from `derive()`'s and asserts the kernel's output; the backend overflow test stores a gradient (`w * exp(1000 * exp(f))`)
no derivation would give, and the fit aborts on it.

**Broken-input proofs** (each restored, `cmp` equal): `derived=None` passed to `compile_expression_objective`: `FAILED
test_compile_dispatch_uses_the_stored_derived_text_and_never_re_derives` (`assert False` on the `np.allclose` line), `1 failed, 4 passed`. The
worker `except` replaced by `except ZeroDivisionError`: `FAILED` both error-case fit tests, `JOB_HANDLER_FAILED`, `2 failed, 2 passed`. The two codes
removed from `errors.py`: the same two tests failed, `2 failed, 2 passed`.

**Deviations and notes for the auditor.** (1) Executor-worded spec sentences: none; the only `docs/` edit is the removal of the two markers.
(2) The refusal of a null `derived` reuses `OBJECTIVE_KIND_NOT_ENABLED`; RL-1362 says "refused by name" and names no code. (3) The `template is None` guard's
message ("Phase 1 compiles templates only") was false after the dispatch, so it now says the objective names no template. (4) The round-budget case
patches `gbm.make_xgb_objective` with `round_budget_s=1e-9`: `fit_gbm` passes no budget (the default is 30 s), so a slowed callable cannot be
made through the API. (5) The overflow row is a `draft` after its failing certificate; the test points `certificate_id` at that certificate and sets
`certified`, so the status gate passes and the fit's abort is what is tested. (6) `ruff format` only on the new test file.

### Task 7 — submission: `OBJECTIVE_NOT_CERTIFIED` and the extra Approver

(2026-10-04 BST, `executor-1273g`, sonnet (Sonnet 5), `echo $CLAUDE_EFFORT` = `medium`; per-worktree database `gipricing_wt-1273g_e215476e`; base `c60888b7`.)

**Red, quoted** (new `backend/tests/test_objective_submission.py` plus the rewritten `test_submission_without_a_certificate_is_refused`, source at base): `11 failed, 3 passed`. The draft tests and the rewritten old test fail on `["code"]`: `AssertionError: assert 'VALIDATION_FAILED' == 'OBJECTIVE_NOT_CERTIFIED'` (`test_objective_submission.py:195`, `test_custom_objectives.py:452`). The old test before: `assert refused.value.status_code == 409  # \`draft → review\` is not a transition at all`; after: the same status assert plus `assert refused.value.code == "OBJECTIVE_NOT_CERTIFIED"`. The count tests fail at `:228` and `:244` (`assert 1 == 2`, `assert 2 == 3`), `:259`, `:273` (`required` 1 and 5, where 2 and 6 are expected). The §4.2 test fails `ApprovalPolicyEntry … escalation … Extra inputs are not permitted [type=extra_forbidden]`.

**Green.** `submit_for_review` refuses `draft` with `OBJECTIVE_NOT_CERTIFIED` before the transition check (the predicate is the status), reads the latest certificate through `load_certificate`, and passes `additional_approvers=1` to `approvals.submit` when a `convexity` check is `violated`; `submit` stores `entry.approvers_required + additional_approvers` on the row and in the submission audit's `after`; the keyword defaults to 0. Code registered in `MODELLING_ERROR_CODES`. Result: `70 passed` (`test_objective_submission.py`, `test_custom_objectives.py`, `test_approvals.py`, `test_errors.py`), `14 passed` for the new file. The four to_dict approval routes were not edited or newly read.

**Spec, byte for byte from RL-1362** (placeholders `<Task 7 date>` = 2026-10-04): `06` §4.2 entry (DP-S3-4 item 1, the three lines to two) and the new note; `02` FR-163 (S5); `02` §5.1 marker removal (S2) and the stand-in sentence (S4); `02` §7.1 row (`06-governance`, the DP-S3-4 item 4). `WF-702` B4.2 not touched (a decision-maker's, after merge). **Executor-worded spec sentences: none.**

**Broken-input proofs** (each restored, `cmp` equal to a pre-edit copy): `additional_approvers=1 if non_convex else 0` replaced by `0`: `6 failed, 7 passed`, the two policy-1 tests, the two policy-2 tests, `test_the_default_policy_instance_stores_two`, `test_policy_five_stores_six_and_the_request_validates` (`:228`, `:244`, `:259`, `:273`). `if current is ObjectiveStatus.DRAFT:` replaced by `if False:`: `3 failed, 11 passed`, both draft tests (`:195`) and `test_submission_without_a_certificate_is_refused` (`:452`).

### Task 8 — FR-207's residuals (DP-S3-5)

**Precondition** (`RL-1362` DP-S3-5): *"Task 8 therefore applies only after a dated line accepts the Phase 3 destination: the maintainer's, or the lead's under delegation."* Met at `c3950d89`: the ruling quotes the maintainer's line of 2026-10-01 (entry *"2026-10-01 08:07:02 BST — ACCEPTANCE: RL 9782 DP-S3-5's Phase 3 destination"*), and that heading is present in the lead's local channel file `to-lead.md`.

**Applied byte for byte** from `RL-1362`, with `<Task 8 date>` set to 2026-10-04 (the only substitution): S6 (appended to `02` FR-207's second cell) and S7.1 to S7.5 (`objectives.py` `ObjectiveBackend` docstring, `ObjectivePicker.vue` header, `test_contracts.py` `DECLARED_AND_UNBUILT` note, `model.schema.json` and `model-spec.schema.json` descriptions). The two schema edits are the ruling's S7.4 and S7.5 and were reproduced by `generate-contracts.py`, which also regenerated `generated.json`, `custom-objective.schema.json` and `custom-metric.schema.json` (`ObjectiveBackend`'s description); `--check` rc 0 after.

**Drift grep.** `git grep -n -E "custom_objective_ref.*WK-690|WK-690.*custom_objective_ref" -- packages backend frontend/src docs/contracts docs/specs` after: only the FR-207 row (its dated history). No quotation outside S7's list was found. Not touched, though it names the same owner for a different subject: `pricing_core/modelling/factors.py:20` (`expression` not built, owned by WK-690 with §4.6's grammar), which is not a `custom_objective_ref` quotation.

**Executor-worded spec sentences: none.**

### Delta 7 — (g) a dangling `certificate_id` is refused; (f) all six templates need the extra Approver

**(g) Red first.** `test_submitting_with_a_certificate_id_that_names_no_row_is_validation_failed` (`backend/tests/test_objective_submission.py`): a template objective certified through the real Job, its `certificate_id` then updated to a uuid with no certificate row, then `submit_for_review`. Base: `Failed: DID NOT RAISE PlatformError` (`1 failed`): the submission was accepted and read as "no `violated` finding".

**(g) Fix.** `submit_for_review` (`backend/src/app/platform/objectives.py`, the only code file changed) loads the pointed certificate (`session.get(ObjectiveCertificateRow, row.certificate_id)`), after `_require_evidence`, and refuses a missing row, or one in another workspace, with 409 `VALIDATION_FAILED` (a registered code, none added); `detail` names `<slug>@<version>` and the missing certificate id. No foreign key added (goes to the FD batch). Green: `1 passed`.

**(g) Broken-input proof.** The guard condition replaced by `if False:`: the new test fails `Failed: DID NOT RAISE PlatformError` (`1 failed`); restored from a saved copy, `cmp` equal.

**(g) Existing tests re-cut.** `_advance` in `backend/tests/test_custom_objectives_api.py` (used by every test that moves an objective to `certified` or `review`, including `test_a_certified_objective_submits_into_review` and `test_submitting_an_objective_twice_conflicts`) stamped `new_uuid7()` with no row. It now inserts a real `ObjectiveCertificateRow` (nine passing checks, valid `CertificateResult`) and points `certificate_id` at it. No assertion changed. `test_custom_objectives_api.py` + `test_objective_submission.py`: `44 passed`. This supersedes Task 7's note (2) above, which said those tests "stand unmodified"; the code now fails closed.

**No spec sentence written for (g):** its text (S5) lands later with RL 9730's delta.

#### FD 9780 — (f) the six templates that certify `violated`

`test_each_template_certified_violated_needs_the_extra_approver` is parametrised over `asymmetric_squared`, `huber` (`delta=1000`), `pseudo_huber` (`delta=1`), `quantile` (`alpha=0.9`), `zero_inflated_poisson` (`pi=0.3`), `focal_binomial`. Each is certified through the real Job on its `default_sampling` grid, asserts `convexity` is `violated`, submits at policy 1 (`required == 2`), and one approval leaves it in `review`. **Red** (`additional_approvers=1 if non_convex else 0` replaced by `0`): `6 failed`, each `assert 1 == 2`. **Green:** `6 passed`; restored, `cmp` equal. Note: `pseudo_huber` with `delta` 100, 1000 and 100000 certified `failed` on the default grid (a draft, not `violated`), so `delta=1` is used; a point for the FD batch.

## FD 9780 — the quantile template certifies convexity `violated` and no second Approver is enforced

Broken input (the base, which is the finding): a `quantile` template certified through the real Job, submitted at policy 1. `test_a_violated_objective_needs_two_approvers_at_policy_one[template]` fails red at `backend/tests/test_objective_submission.py:353` at head `5af9d321` (`assert required == 2`; was `:228`, then `:280` at `876af8d0`) (`assert 1 == 2`: the row holds 1, so one approval would approve it) and is green after the change: the row and the audit `after` hold 2, one approval leaves the objective in `review`, a second approves it. The same test for an `expression` objective (§4.6's example, which certifies `violated` through the real Job), the policy-2 pair (3 stored; two approvals leave `review`, a third approves), `DEFAULT_POLICY` (2) and policy 5 (6, and `ApprovalRequest` validates) are red at base and green after; the controls (a `pass` certificate at policy 1 stores 1 and one approval approves; an `approved` objective's resubmission stays `VALIDATION_FAILED`; a `validation_rule` stores the entry's count; an `escalation` key is refused `extra_forbidden`) are green at both.

**Template reach, counted at base** (the command is FD 9780's Evidence 4(a) predicate, `git grep -nE 'ObjectiveTemplate\.QUANTILE|template="quantile"' -- backend/tests packages/*/tests`): 3 lines (1 backend fixture, `test_paired_quantile_models.py:97`, called by `_approved_quantile(` 7 times, plus 2 lines of one core-only fit at `test_gbm.py:1576-1577`). **A wider measurement**, `certify_objective` over each of the 12 templates with `test_objectives.py`'s `_objective` and `_sampling(n_points=1000)`: **6 of 12 certify `convexity: violated`** (`asymmetric_squared`, `huber`, `pseudo_huber`, `quantile`, `zero_inflated_poisson`, `focal_binomial`), not only the quantile; the other 6 pass. So the release note's template reach is six templates, a wider reach than FD 9780's text (quantile only) and than `RL-1362`'s "live instance" reading. **A point for the lead and the FD's mint.**

**Release note** (DP-S3-3, DP-S3-4): submitting a `draft` objective of either kind is now `OBJECTIVE_NOT_CERTIFIED` (409; was `VALIDATION_FAILED`); an objective whose latest certificate has `convexity: violated`, template or expression, needs the policy's count plus one Approver.

**Deviations and notes for the auditor (Task 7).** (1) Executor-worded spec sentences: none. (2) **A decision-maker point:** `test_custom_objectives_api.py`'s `_advance` stamps `certificate_id` with a random uuid and no `objective_certificates` row (no foreign key forbids it). A first cut that read the certificate through `load_certificate` returned 404 there (`test_a_certified_objective_submits_into_review` and `test_submitting_an_objective_twice_conflicts` failed `assert 404 == 200`). The code now reads the latest certificate row and treats none as no `violated` finding, the ruling's literal predicate, so the two tests stand unmodified; failing closed (a refusal for a pointer with no row) would instead need those two tests re-cut and is a rule the ruling does not make. (3) `ruff format` only on the new test file. (4) `docs/INDEX.md` regenerated (the FR-163 row's contents cell changed). (5) The ledger heading names `FD 9780` in the working-id form: the hyphenated id is unminted and check 32 refuses it.

## PRs

None yet: the branch is pushed, no PR is opened (the lead's order for this turn).

### Task 9 — `FD-1349`'s guard comparison (DP-S3-6 (a))

**Measured first (before writing the test).** The authored enum (`docs/contracts/schemas/objective-certificate.schema.json`, `properties.result.properties.checks.items.properties.name.enum`) has 11 names; `OBJECTIVE_CERTIFICATE_CHECKS` has 9, `OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC` has 9, their union has 11 (the plan's 11, verified). **Expected:** the new comparison passes on the unmodified tree, drift set empty. **Observed:** `2 passed` for `-k certificate_check_name`.

**Added** (only additions, 48 lines at the end of `backend/tests/test_contracts.py`; `ONE_SIDED_SLUGS` untouched, no key needed — `objective-certificate` is a compared slug already): `test_the_certificate_check_name_enum_is_the_code_vocabulary` (`FR-146`) and its meta-guard `test_the_certificate_check_name_comparison_reaches_the_enum_and_can_fail`.

**Red 1 — FD-1349 Evidence 1's input** (`symbolic_vs_numeric_gradient`, `symbolic_vs_numeric_hessian`, `finiteness`, `convexity`, `smoke_fit` → `"BOGUS"`; Evidence 1 reproduced against base: `144 passed`; here the whole file): `2 failed, 150 passed, 2 skipped`; `AssertionError: authored enum vs code vocabulary differ on: ['BOGUS', 'convexity', 'finiteness', 'smoke_fit', 'symbolic_vs_numeric_gradient', 'symbolic_vs_numeric_hessian']` (the second failure is the meta-guard's reach assertion on the broken contract). Reverted from a saved copy, `cmp` equal; green `152 passed, 2 skipped`.

**Red 2 — the meta-guard's own** (drift function body replaced by `return set()`): `1 failed, 151 passed`; `AssertionError: assert set() == {'BOGUS', 'convexity'}`. Restored from a saved copy; green `152 passed, 2 skipped`.

### RL-1410's delta — the refusal codes (R1, R3; S1–S5)

**Supersedes Task 6's red text** (N2): Task 6's account of the null-`derived` refusal as `OBJECTIVE_KIND_NOT_ENABLED` is superseded by `RL-1410` R1; the refusal is 409 `VALIDATION_FAILED`. `worker/model_handlers.py:1554` (the certify job's "no stored derivation" `ValueError`) is not touched (N2). This ledger is in the write set (N1).

**R1 red, first.** `test_compile_dispatch_refuses_an_underived_expression_objective_by_name` now binds `refused` and asserts `refused.value.code == "VALIDATION_FAILED"` and `"/derive" in str(refused.value)`. Red at base on the code assertion: `AssertionError: assert 'OBJECTIVE_KIND_NOT_ENABLED' == 'VALIDATION_FAILED'`. Then C1 applied byte for byte in `_compile_stored_expression`; green, `test_objectives.py` `105 passed`.

**R3's new test**, `test_an_expression_objective_without_applicability_is_refused_422` (`FR-153`). The code already exists, so the red step is the broken-input proof: the `if template is None:` branch in `_validated` replaced by `if False:` makes the create answer 500 (`KeyError` from `TEMPLATE_APPLICABILITY[None]`), and the test fails on `assert 500 == 422`. Restored from a saved copy, `cmp` equal; green `1 passed`.

**Spec texts** in `docs/specs/02-modelling.md`, byte for byte, `<Task date>` and `<fix date>` = 2026-10-04, `<RL id>` = `RL-1410`: S1 (FR-144 row, `:208`), S2 (create row, `:1841`), S3 and S4 (derive row, `:1844`), S5 (submit row, `:1847`). No other sentence. R2 and R4 need no code or test change.

**Deviations.** None beyond the above; `ruff format` was not run.

### Task 10 — NFR-480, measured in a solo window

**Grant.** The lead granted the solo window at 18:58:40 UTC (`RL-1263` item 3): 0 pytest/bench/uvicorn processes, both gate slots free, load 1.09. Announced `nfr_480_solo` at 18:59:04 UTC against tree `935bd65673b853d4ec09c9fc67d688f293098c4b`.

**Harness.** None existed for an expression objective (`scripts/bench-*.py` time other components; `certify_expression_objective` is called only by `worker/model_handlers.py` and tests). Added `scripts/bench-expression-certify.py`: no Job, no database; calls `certify_expression_objective` on §4.6's `asymmetric-burning-cost` loss over `default_sampling`'s `burning_cost` grid (2 000 points, seed 20260818, `y` (0, 1e6), `f` (-5, 15), `w` (0.01, 10)), timing the whole call (compile, nine checks, smoke fit). It prints times and no verdict. Run as a fresh process each time, under `flock /tmp/slots/gate-1`, with `LOKY_MAX_CPU_COUNT=4` and the dev-commands caps.

| Run | Start UTC / BST | End UTC / BST | Wall (certify call) | Load avg at start → end | pytest/bench/uvicorn procs start / end |
|---|---|---|---|---|---|
| 1 (cold) | 18:59:36 / 19:59:36 | 18:59:44 / 19:59:44 | 2.318 s | 0.62 → 0.68 | 0 / 0 |
| 2 | 18:59:44 / 19:59:44 | 18:59:47 / 19:59:47 | 0.957 s | 0.68 → 1.02 | 0 / 0 |
| 3 | 18:59:47 / 19:59:47 | 18:59:50 / 19:59:50 | 0.934 s | 1.02 → 1.02 | 0 / 0 |
| 4 | 18:59:50 / 19:59:50 | 18:59:53 / 19:59:53 | 0.876 s | 1.02 → 1.10 | 0 / 0 |

Load figures are the 1-minute average.

**Median 0.945 s; spread 0.876–2.318 s (the first run is cold: SymPy and NumPy first use).** The timed span excludes interpreter start and imports (a few seconds of wall per run).

**Verdict, against NFR-480's 180 s: met.** The slowest run is 2.318 s, about 1.3 % of the budget. Measured on one grid and one loss; a larger `n_points` or a `where()`-heavy loss was not measured. The certificate's per-check statuses were not inspected: this measures time only.

### Audit fixes, 2026-10-05 (slice audit A5 (c), A6, A7, A9, A11; Delta 11)

Start head `876af8d0f083ef82599b46a103f685d9af75a77a`; worktree `sl-1273-fixes`. Item numbers are the brief's.

**A7 (item 1), red first.** `submit_for_review`'s guard (`backend/src/app/platform/objectives.py`) now also requires `pointed.custom_objective_id == row.id`, beside the existing workspace clause. Two new tests in `test_objective_submission.py`: `test_submitting_with_another_objectives_certificate_is_validation_failed` (a certificate of a second certified objective in the same workspace) and `test_submitting_with_a_certificate_stored_in_another_workspace_is_validation_failed` (a copy of the objective's own certificate stored under another `workspace_id`, so only the workspace clause can refuse it). Red before the fix: the first `Failed: DID NOT RAISE PlatformError`. The second passed before the fix, because the workspace clause already existed and had no test; its proof is the broken-input run: with `or pointed.workspace_id != workspace_id` removed it fails `DID NOT RAISE PlatformError`. With `or pointed.custom_objective_id != row.id` removed the first fails `DID NOT RAISE PlatformError` and the second passes. Both restored (`cmp` equal to a pre-edit copy); the file is `22 passed`. No spec wording was added beyond `RL-1362` S5.

**A9 (item 2).** `docs/specs/06-governance.md` FR-366: one dated sentence appended to the row after its 2026-08-18 amendment, ("**Noted 2026-10-05 (WK-690 Slice 3, `PL-1382` Task 3):** the discharge `FR-367` names has landed ... A note, not a change of rule."), as Delta 11 rules and on Delta 3's precedent: append-only (the old row is an exact prefix), plan-directed (`PL-1382` Task 3 Files and Green step), no rule beyond it. **Executor-worded: listed for the audit.** The earlier entry above that says the note was "not written" is superseded by this one. FR-366 still carries no test marker.

**A5 (c) (item 3), justified, not re-cut.** A stored gradient that certifies on its grid and overflows only on real data cannot be built reliably, and the fixture's SQL-set `certified` state is unreachable by the lifecycle. The fixture docstring (`test_expression_objective_fit.py`, `_expression_objective`) now states the limit; the tests prove the fit's abort and its code, not the scenario end to end.

**A6 (item 4).** The two re-indented blocks are gone. `model_handlers.py`: `certify = _certify_expression if objective.kind == "expression" else certify_objective`, then one call, so the original `certify_objective(...)` lines are not re-indented (`git diff --numstat` against the merge-base: 48/1 plain and 48/1 with `-w`). `test_custom_objectives.py`: the flag test is written without nested helpers, keeping the original blocks at their indentation (157/17 plain, 156/16 with `-w`; the one-line difference is how `diff` aligns a changed block, no line differs by indentation alone).

**A11 (item 5).** The quantile red's citation `:228` is `:280` (the line at head `876af8d0`). **Re-cited at the mint, 2026-10-05** (the audit's re-check found `:280` stale at `5af9d321`): the red's `assert required == 2` is `backend/tests/test_objective_submission.py:353` at `5af9d321` (found by text, and the same line at the mint tree). The two earlier `:228` citations of Task 7's count tests are left as written: they cite the file at the time.

**A10 (item 7) is not in this entry.** The brief's amendment of 2026-10-05 09:37:26 BST moves it to a separate dispatch in a window the lead clears; Task 10's record above stays "provisional" per Delta 10.

### A10 — the NFR-480 solo re-run, 2026-10-05 (slice audit A10; Delta 10; `PL-1382` Task 10)

Entry date 2026-10-05, window 10:02:29–10:32:29 BST (30 minutes from the quiet-box probe); the runs below ended 10:03:42 BST. Worktree `sl-1273-fixes`, branch `sl-1273-custom-objective-expression`; start head `5af9d321f3ce4e6fab53dcd34e9289e20ae65884`; the bench change below is the head `2904d00f613d35e1943c3af888c81ff026202728` the runs used. The box held no other agent's work (the lead had ended every other agent).

**Quiet-box probe, 2026-10-05 10:02:29 BST.** `uptime`: load average 1.10, 2.40, 2.68. `free -m`: 32 099 MB total, 21 134 free, 26 657 available. Both slots free (`free1`, `free2`). `pgrep -af 'pytest|bench|uvicorn|doc-id|audit-docs|ruff|mypy|vite|node .*vitest'` matched only the VS Code terminal shell (its path contains `workbench`) and the probe's own command line: no heavy process. Before the first run (10:03:21) load was 0.57.

**Bench change (committed before timing).** `scripts/bench-expression-certify.py` prints, per run, `result.overall`, every check's `name` and `status`, and the `smoke_fit` check's `detail`. The grid constants stay mirrored: `_DEFAULT_POINTS` and `_DEFAULT_WEIGHTS` are module-private in `backend/src/app/platform/objectives.py`, and `y_range` and `f_range` are computed inside `default_sampling`, which takes a whole `CustomObjective`, so no single import supplies them. The printed grid is `{'n_points': 2000, 'seed': 20260818, 'y_range': (0.0, 1000000.0), 'f_range': (-5.0, 15.0), 'w_range': (0.01, 10.0)}`, equal to the earlier entry's.

**Commands, verbatim** (foreground, one fresh process per run, nothing else between runs):
`for n in 1 2 3 4 5; do echo "=== run $n start $(TZ=Europe/London date '+%T %Z') | $(uptime)"; timeout 600 uv --directory $W run python scripts/bench-expression-certify.py; echo "rc=$?"; echo "=== run $n end $(TZ=Europe/London date '+%T %Z') | $(uptime)"; done`
with `W` the worktree path. Not run under a slot `flock` and without `LOKY_MAX_CPU_COUNT`: the box was otherwise idle and `flock -n` on both slots had succeeded.

| Run | Start / end BST | Load avg (1 min) start → end | Certify call | `overall` | Counts |
|---|---|---|---|---|---|
| 1 (cold) | 10:03:21 / 10:03:28 | 0.57 → 0.64 | 2.104 s | `certified_with_findings` | yes |
| 2 | 10:03:28 / 10:03:31 | 0.64 → 0.64 | 1.063 s | `certified_with_findings` | yes |
| 3 | 10:03:31 / 10:03:35 | 0.64 → 0.67 | 1.345 s | `certified_with_findings` | yes |
| 4 | 10:03:35 / 10:03:39 | 0.67 → 0.69 | 1.174 s | `certified_with_findings` | yes |
| 5 | 10:03:39 / 10:03:42 | 0.69 → 1.36 | 1.127 s | `certified_with_findings` | yes |

Statuses, identical in all five runs: `symbolic_vs_numeric_gradient` pass; `symbolic_vs_numeric_hessian` pass; `finiteness` pass; `convexity` violated; `branch_discontinuity` warn; `minimum_at_truth` pass; `monotone_loss` pass; `scale_behaviour` warn; `smoke_fit` pass. `smoke_fit` detail, runs 1–5: "recovered a relativity of 1.499 against a true 1.5 (0.1%) on gamma severity, mean 1500 x relativity, n=20,000; 80 rounds" with 0.5 s, 0.5 s, 0.7 s, 0.5 s, 0.3 s (the fit's own clock).

**Counting rule.** The brief's rule names the certificate status "`certified` or `violated`". The code's `CertificateOutcome` (`packages/model-schema/src/model_schema/objectives.py`) has `certified`, `certified_with_findings` and `failed`; `violated` is a *check* status (here `convexity`, the finding the loss's `where()` asymmetry produces). I read the rule as: no check `failed`, `smoke_fit` `pass` or `warn` with rounds in its detail, `overall` not `failed`. All five runs meet it; none dropped.

**Median 1.174 s of 5 counting runs; range 1.063–2.104 s.** NFR-480, `docs/specs/02-modelling.md` row: "Objective certification completes in < 3 min including the synthetic smoke fit." That row carries no dated amendment; the dated measurement note below the table (2026-08-22, WK-661) records a 180 s budget and a twelve-template result. **Verdict: met**, the slowest run being 2.104 s, about 1.2 % of 180 s. This is the Task 10 figure the earlier provisional entry (Delta 10) asked to have re-taken solo; it does not change that entry's order of magnitude.

**What the timed span contains.** `scripts/bench-expression-certify.py` calls `certify_expression_objective` directly: no Job, no database, no HTTP (as this ledger already discloses). It passes no `derived`, so `derived is None` and `compile_expression_objective` (`packages/pricing-core/src/pricing_core/modelling/expression_objective.py`) runs `derive(loss, parameters=parameters.keys())` inside the timed span, that is, SymPy differentiation is timed. The first run is cold (SymPy and NumPy first use). One grid and one loss only; a larger `n_points` or a `where()`-heavier loss was not measured.

## Closing note

This ledger is closed under the executor charter's mint-step clause (`.claude/roles/executor.md`, "As the mint step…", added 2026-10-04) and `docs/process/document-ids.md` §1.6's 2026-10-04 amendment to the SL and LG close cells: on 2026-10-05 the executor performed the closing acts in the mint commit on the auditor's behalf, after the slice audit — the front matter `status: closed`, the roadmap SL-1273 row `status: closed` with its dated line, `docs/INDEX.md` regenerated, `audit-docs` green. The audit it cites is `handover/audit-sl1273-2026-10-04.md`, with its "Re-check 2026-10-05" section (local, not in the repository). The minted-head gate's record and the PR number are appended after the gate.

## Gate fix and re-gate (2026-10-05)

A dated forward entry, appended after the closing note above; nothing above it is edited. The minted-head gate at `9963f22d54535638d8b2ba14189d2e18edafd45f` (slot gate-1, 09:08:27Z–09:40:36Z) ended `3 failed, 4908 passed, 3 skipped`, everything else exit 0. Retry counter `slice:SL-1273:fix -> 1/2`. All three failures were in tests, none in the slice's product code.

| Failing test | Root cause | Fix |
|---|---|---|
| `backend/tests/test_migration_deployments.py::test_the_migration_round_trips` | The #1104 test upgraded to `head` and downgraded one step, assuming `c4a81f6d2e95` is head. This slice's `e5b7d9f1a3c6` now sits on top, so `downgrade -1` landed on `c4a81f6d2e95`, not `2f598e89d12c`. Red reproduced before the fix: `assert 'c4a81f6d2e95' == '2f598e89d12c'`. | The test upgrades to `_THIS_REVISION = "c4a81f6d2e95"`, its own revision, and no longer depends on head. No migration changed. |
| `backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for` | The census counted 2 `str(exc)` sinks in `model_handlers._fit` against 1 listed. The new one is the `except (NonFiniteDerivativeError, RoundBudgetExceededError)` clause (FR-165). Both are `CodedError`s raised in `pricing_core/modelling/objectives.py` during a fit job on a Dataset Version; their text names the round, the objective ref, a row count or timings, and keeps the y/f range out of it (FD-1219, DP-S2-4). It cannot carry a quote input. Reading the census diff also showed three more unlisted sinks in `backend/src/app/platform/objectives.py`: `_require_the_grammar` (1) and `derive_objective` (2), each the `ExpressionError` text of an author's own loss. | Limb (a): `_SINKS` lists all four, with the same justification form as the existing `_validated` entry (a custom objective's own declaration error, no Quote Context). The census mechanism is untouched. |
| `tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared` | `pricing_core/modelling/objectives.py` raises `ObjectiveError("VALIDATION_FAILED", …)` for an underived expression objective (RL-1410). The test required every raised code in `MODELLING_ERROR_CODES` and in `02` §5.1's "Error codes owned by this module" block. `VALIDATION_FAILED` is a generic code, registered in `_GENERIC_ERROR_CODES` and owned by the request machinery. | The test accepts a code registered in `_GENERIC_ERROR_CODES` as registered, and does not require a generic code in the module-owned block. No spec text added. |

Fix commit `76897a8ba6b089af1f761e4972c033c171705943` (on `f1953378…`, the merge of `origin/main` `ef5dc6e7`).

**Re-gate at that head.** Slot gate-1 (the block in `.claude/skills/dev-commands`, copied verbatim apart from a `timeout 3300` on `pytest`). Start 09:45:44Z: `uptime` load average 1.25, 2.12, 2.11; `free -m` 32 099 total, 21 683 free; the other slot (gate-2) probed free. End 10:16:50Z: load average 4.82, 3.01, 2.70; 19 984 free; gate-2 free.

| Stage | Exit | Totals |
|---|---|---|
| `ruff check .` | 0 | |
| `mypy` | 0 | |
| `lint-imports` | 0 | |
| `audit-docs.py` | 0 | |
| `req-coverage.py` | 0 | |
| `generate-contracts.py --check` | 0 | |
| `pytest -q` | 0 | `4911 passed, 3 skipped` in 1755.00 s |
| `pnpm install --frozen-lockfile` | 0 | |
| `pnpm generate:api` | 0 | |
| `pnpm lint` | 0 | |
| `pnpm type-check` | 0 | |
| `pnpm test` | 0 | 97 files, 612 tests passed |
| `pnpm build` | 0 | |

## Forward entry, 2026-10-05 10:25 UTC — mutation proof of the `_fit` sink pin, and a disclosed exception

**Disclosure.** Gated head `76897a8b` → `f76a8283`: 3 commits touching only `backend/tests/test_error_sinks.py` (+3/−1) so the census entry names its pin, plus this ledger entry. The gate for them is #1122's PR CI python run. This is an exception to "after the gated head, only the ledger", on the deputy's narrowed (A).

**Mutation proof** (scratch edit, never committed). The pin is `packages/pricing-core/tests/test_objectives.py::test_nonfinite_aborts_an_expression_naming_the_round_and_no_value`. Edit: in `_finite_or_abort`, the `NonFiniteDerivativeError` f-string gained ` y={float(y_bad.min())}` after `boosting round {round_index}`. Red, verbatim: `AssertionError: assert '7.25' not in 'OBJECTIVE_N...lds y and f.'` (`test_objectives.py:732`; xgboost and lightgbm both fail). Restore: the file was copied back from a backup; `cmp <backup> <file>` exit 0; `git diff --quiet -- packages/pricing-core/src` exit 0. Green after restore: `2 passed, 103 deselected`.
