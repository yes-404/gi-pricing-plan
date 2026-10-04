---
id: LG-1405
family: ledger
title: WK-674 slice SL-1256 — the Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit, NFR-498 for deploy), routes typed both ways, the compile guard of RL-1379 (PL-1392)
status: closed
created: 2026-10-04
owner: executor
tree: 934dcabe4b4647b74b1488fd83253d91943b7799
phase: P2
work: WK-674
slice: SL-1256
plans: [PL-1392]
corrected_by: []
relates: [RL-1379, RL-1380, RL-1301, RL-1296, RL-1263, FD-1393, FR-267, FR-428, FR-429, FR-272, NFR-498, FR-343]
---

# LG-1405 — WK-674 slice SL-1256, the Environment and Deployment record

Executed from `PL-1392` by `executor-1256` (sonnet, medium: `echo $CLAUDE_EFFORT` printed `medium`). Branch
`sl-1256-environment-and-deployment-record`. Stamps are BST (`TZ=Europe/London date`).

The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the
lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a cheaper setting."

The dispatch record is `gi-pricing-plan.local/handover/DISPATCH-WK-674-SL1256-2026-10-03.md` (FINAL; Conditions 1-8
and Deltas 1-4 bind). It is a local file and is not in the repository.

## Tasks

### Task 0 — preconditions

**Base.** Worktree created from `origin/main` `8252741cc3849058b6fc6836967448d88ff9821c` (#1087, SL-1377, merged),
read at 2026-10-03 22:01 BST; `git fetch origin main` then printed the same SHA. `uv sync --all-packages` ran. Test
database `gipricing_agent-a0f7a7db50ec2ab16_83653597`, created from the template and migrated to head.

**Checks at that SHA.**

- `RL-1296`, `RL-1301`, `RL-1379` and `RL-1380` are files under `docs/rulings/` (listed with
  `ls docs/rulings` filtered by the four numbers, four lines; the filter's text is dropped at Task 1 because audit check 32 read its zero-padded prefix as an id). #974 is RL-1380, minted.
- `docs/roadmap.md`: `SL-1302` `status: closed`; `SL-1300` `status: closed`; `SL-1360` `status: closed`;
  `SL-1367` `status: draft` (not in flight); `SL-1256` `status: active`.
- **Acceptance 8's predicate** (`grep -c -E '^> \| `(deployment:promote|admin:manage_environments)` \|.*\| WK-674 \|$'
  docs/specs/06-governance.md`) prints **2**.
- **`SL-1360` has merged**: `tests/test_permission_parity.py` exists at the repository root, so Acceptance 8's
  `STALE_OWNER` red can be shown (the plan's `backend/tests/` path for it is wrong; the file is `tests/`).
- **In-flight build slices** (`gh pr list --state open`, 2026-10-03 ~22:05 BST): every open PR is docs-only
  (findings, rulings, plans). No build PR touches `score.py`. `executor-1385` (WK-673 S1, lane B) is the concurrent
  build slice; its spec sections and `ONE_SIDED_SLUGS` key (`"dislocation-run"`) are disjoint from this slice's
  (Delta 4).
- **F1 registry serialisation (Condition 2, Delta 3):** `#1087` (SL-1377) **merged first**. This slice re-bumps
  `_CONTRACT_ARTIFACT_PATHS` and the `non_markdown` count on the merged tree, and the contract-schema skill step is
  SL-1377's, not this slice's (verified when Task 2 reaches it).
- **Premises re-derived at `8252741c`:** (a) the only `class .*Environment` is `backend/src/app/config.py:32`;
  `live_deployments` only at `docs/specs/07-platform.md:253`. (b) `"deployment"` in the floor at
  `packages/model-schema/src/model_schema/approvals.py:107`. (d) `uat_deployment` only at `approvals.py:107`.
  (e) `grep -rn -E "(Perm|Permission)\.(DEPLOYMENT_PROMOTE|ADMIN_MANAGE_ENVIRONMENTS)\b" backend/src` exits 1.
  (i) `DEPLOY_REQUIRES_APPROVAL` is in no backend `.py`; `PROMOTION_ORDER_VIOLATION` at `errors.py:70`.
  (o) the Alembic head is `2f598e89d12c` (the only revision no `down_revision` names; 50 files). (p) `03` §4 ends
  at §4.11 `SubGraph` (`docs/specs/03-rating-engine.md:760`; §4.10 moved from `:703` to `:720`, so §4.12 is free).
  (u) no `class (Environment|Deployment|DeploymentRequest|PromotionSkip)` under `packages/model-schema/src` (exit 1).
  Line numbers in the plan that SL-1377 moved are re-found where used. Premises c, f-h, j-n, q-t are re-read at the
  task that uses each.

### Task 0A — the authorisation sweep sees every route

File: `backend/tests/test_api_authorisation_sweep.py` (no sibling: `grep -rn "app.routes" backend/tests` names only this
file, so Acceptance 12 (f) has nothing else to fix).

- **FastAPI probe:** `uv run python -c "import fastapi; print(fastapi.__version__)"` printed `0.141.1`.
  `app.routes` is 29 entries: `Counter({'_IncludedRouter': 23, 'Route': 4, 'APIRoute': 2})`; an `_IncludedRouter` holds
  `original_router.routes` and `include_context.prefix` (`/api/v1`); no router is nested inside another.
- **Red first, (a), predicted cause "the loop does not descend into `_IncludedRouter`":** the equality test over the
  unchanged loop failed with `AssertionError: the static sweep iterated 2 operations; the contract publishes 141`
  (`assert 2 == 141`). With the flattening helper `_flattened_operations` the set of iterated `(method, path)` equals
  the published set (141 operations).
- **Red first, (b):** with the helper's descent disabled (a temporary `original = None`, since restored; `grep -c
  RED-PROBE` prints 0), `test_a_guard_removed_from_a_real_route_is_seen` failed with `StopIteration` (the target route
  `GET /api/v1/datasets` is not seen at all) and the equality test failed `2 == 141`. With the descent, removing
  `requires()` from that route (by `monkeypatch`) makes the sweep return exactly `['GET /api/v1/datasets']`.
- **Static sweep over the flattened surface, run before the allow-list existed:** it named exactly two routes,
  `POST /api/v1/me/workspace` and `POST /api/v1/validation-rules`: the two handler-guarded routes of Acceptance 12 (e).
  `HANDLER_GUARDED` names them with file, line and the text that must be on that line (`validation_rules.py:200`,
  `:207` hold `require_permission(`; `api/me.py:241`, `:251`, `:260` hold `WORKSPACE_SCOPE_DENIED`), and
  `test_the_handler_guarded_routes_still_check_at_their_site` reads each line.
- **(d) the valid-body sweep:** `_request_for` builds the path, required query and JSON body from `app.openapi()`
  (`$ref`, enums, `format` uuid/date/date-time, `anyOf`/`oneOf` first satisfiable, `allOf` merged, string `minLength`,
  numbers at `minimum`; a `pattern` only through `_PATTERN_VALUES`, the three patterns the contract uses without
  `examples`). The sweep asserts exactly 403 (`PERMISSION_DENIED`; for a `HANDLER_GUARDED` route
  `WORKSPACE_SCOPE_DENIED` also) and 401 for the anonymous one. `UNSATISFIABLE` holds the two multipart operations
  (`POST /api/v1/rate-tables/{slug}@{version}/import`, `POST /api/v1/sources/{source_id}/preview`, a file part), and
  `len(UNSATISFIABLE) == 2` is asserted. **Deviation from the plan, stated:** the plan's builder rule is `pattern` from
  `examples`; the contract has no `examples` for its slug, digest and peril-code patterns, so three literal values are
  mapped instead. **The red for `POST /api/v1/me/workspace` cannot be shown as a failing run of the old sweep:** the old
  sweep passed it (5 passed at `8252741c`) because `{}` answered 422, which it counted as a refusal; the new sweep
  sends a valid body and requires 403, and passes. This is a reasoned red, recorded as such.
- **(g) partition:** `test_every_operation_is_accounted_for_by_exactly_one_class` asserts open-by-design,
  permission-free, handler-guarded and `requires()`-declared are pairwise disjoint and union to the 141 published
  operations.
- Iterated count 141, OpenAPI count 141 (predicate: the plan's `python3 -c` over `docs/contracts/openapi/generated.json`
  and `_published_operations`, the same figure). Result: `9 passed`; `ruff check`, `ruff format --check` and `mypy`
  clean on the file.

### Task 1 — spec: `03`, `07`, `06`

Stamp 2026-10-03 22:15 BST (`TZ=Europe/London date`). Base: branch head `924980cf` on `8252741c`. Spec only; nothing in
`packages/`, `backend/` or `docs/contracts/` is touched.

- **Red first (spec form).** The plan gives no test for Task 1, so the red is the absence predicate, run over the
  pre-edit text (the base's files saved to scratch files from the branch head, after the edit, so the values are the
  base's): `grep -c -E "^### 4\.12 .Deployment"` over `03` printed 0;
  `grep -c -E "deployment-requests|environments/\{slug\}/retire"` printed 0 over `03` and 0 over `07`;
  `grep -c "Amended 2026-10-03"` over `06` printed 0. After the edit the first prints 1, the second 2 (`03`) and 1
  (`07`), and `06` carries the FR-345 amendment. An absence predicate is not a test of the prose, so the auditor's read
  of each note against RL-1301 is the real check.
- **`03`** (`docs/specs/03-rating-engine.md`): new §4.12 `Deployment`, after §4.11 (free at this tree: §4 ended at
  §4.11), carrying the shape and example, the four invariants, the four audit actions named once, and the Deployment
  Request (reference `deployment:<environment slug>@<n>`, the two pinned evidence items, `PromotionSkip`, execute-once,
  the generic reference type). §3.10: two dated blockquote notes after the table (FR-267 contract; FR-272's deploy
  Audit Event limb); the FR-267..FR-272 rows are not reworded. §5.1: two rows appended at the end of the table (the
  history `GET` and the `deployment-requests` `POST`); the owned-codes paragraph is not touched.
- **`07`**: §4.2 one dated note (three bullets: `live_deployments` derived; `slug` beside `name`, RL-1301 A.6;
  `settings` is Slice 3's, `requires_prior_environment` is FR-429's predecessor); §5.1 two rows after the settings row
  (`PATCH /api/v1/environments/{slug}`, `POST /api/v1/environments/{slug}/retire`), worded as the plan gives them.
- **`06`**: FR-345 gains a dated "or Environments" amendment citing RL-1301 B and CR-1212 item 4; §4.1 a dated note after
  the `RL-1232` DP-6 paragraph showing an `environments` scope; §4.2 a dated RL-886 note after `separation_of_duties`.
  The §4.2 note says the entry is added "by this slice" (the code is Task 2's), so no sentence is false at this commit.
- **Deviations and flags, stated.** (1) **Glossary:** `spec-change` wants a new term in the glossary first, and the term
  "Deployment Request" is new. The glossary rows are in `00` §2.3 (`Deployment` at `:166`), which the dispatch record
  forbids this slice (WK-673 S1's). The term is defined where it is first used, in `03` §4.12; the glossary row is
  left for the lead to route. (2) The plan's `ARTIFACT_TYPES` bullet: the list is stated in no spec table at this tree
  (`grep -n -E "gipp_check" docs/specs/*.md` finds none naming the list); `03` §4.12 states that `deployment` joins it
  and names `artifact-ref.schema.json`, which Task 2 regenerates. (3) §3.10 notes are blockquotes after the table, not
  table rows, because a row would need a new id. (4) The §4.1 `environments` scope JSON is illustrative in the example's
  own form; the stored form is `scope_type` and `scope_id`, as `ScopeType` has it.
- **Not done here, by plan:** the skip field and `"skippable_predecessors"` in `06` §4.2's JSON (Task 2); the compile
  guard texts T1 to T4 of RL-1379 (Task 5A); `06` §4.1's `deployment:promote` cell (Task 5).

### Task 2 — `model-schema`: shapes, the policy entry, the skip field and the predicate

Stamp 2026-10-03 22:34 BST (`TZ=Europe/London date`; `uptime` load average 5.41 at the stamp, another gate holding
`/tmp/slots/gate-1`). Base: branch head `4a8656a9` on `8252741c`. Four commits: `11d692dc`, `4143cef0`, `0a1bdd94`,
`030d8864`. Skills read: `spec-change` (Task 1), `contract-schema`, `contract-guard`, `python-package`, `python-test`.

- **Commit 1, the `deployment` entry (RL-886).** Red first, `test_the_default_policy_has_a_prod_deployment_entry`
  (`packages/model-schema/tests/test_approvals.py`): `assert None is not None` on `DEFAULT_POLICY.entry_for("deployment",
  "prod")`, the predicted cause (premise b). Green after the entry was added to `DEFAULT_POLICY` (`prod`, 1 approver,
  role `deployer`, evidence the two floor kinds, as `06` §4.2 shows). `generate-contracts.py --check` exit 0.
- **Commit 2, the skip field, its validator, `06` §4.2 and the contract, together (RL-1296 item 5).** Red first, both
  predicted forms quoted. Before the field: the control test failed with `skippable_predecessors / Extra inputs are not
  permitted [type=extra_forbidden]` (the two refusal tests pass at that point for the wrong reason, which is why the
  control is in the set). Field added without the validator: the two refusal tests failed `DID NOT RAISE
  ValidationError` (`environment=None`; `artifact_type="rating_version"`). With the `@model_validator(mode="after")` all
  10 tests pass. `06` §4.2 gains `"skippable_predecessors": []` on the `prod` entry and a dated note citing `RL-1296`.
  `docs/contracts/openapi/generated.json` regenerated (+9 lines); `--check` exit 0.
- **Commit 3, the predicate.** Red first: `ImportError: cannot import name 'PromotionSkip' from 'model_schema'`. Then
  `PromotionSkip` (blank `reason` refused by a `field_validator`) and `promotion_order_refusal` in `approvals.py`. A
  9-row table test, a blank-reason test (one through the validator, one through `model_construct` straight into the
  predicate) and the F8 test (an unqualified entry built with `model_construct` carrying the field grants no skip):
  21 passed in the file. Every refusal reason names the target and the predecessor (asserted).
- **Commit 4, the shapes.** Red first: `ImportError: cannot import name 'Deployment' from 'model_schema'`
  (`tests/test_deployments.py`: each class validates its example and refuses an unknown key). `deployments.py` adds
  `Environment`, `LiveDeployment`, `EnvironmentCreate`, `EnvironmentUpdate`, `Deployment`, `DeploymentCreate`,
  `DeploymentRequestStatus`, `DeploymentRequestEvidence`, `DeploymentRequest`, `DeploymentRequestCreate`;
  `ScopeType.ENVIRONMENT`; `"deployment"` in `ARTIFACT_TYPES`; seven slugs in `GENERATED_SHAPES`
  (`environment`, `environment-create`, `environment-update`, `deployment`, `deployment-create`, `deployment-request`,
  `deployment-request-create`); `promotion-skip` is not registered (reached through `deployment-request-create`'s
  `$defs`). The slugs are typed with `refs.Slug`, references with `ArtifactRef`; every class is `extra="forbid"`.
- **Acceptance 2 counts, at this head.** `git grep -n -E '^class (Environment|Deployment)\b' -- packages backend/src
  frontend/src` prints **3** lines (`config.py:32`, `deployments.py:55`, `:99`). The Route-table predicate prints **6**
  (`approvals.py:230` `PromotionSkip`; `deployments.py:75, :87, :123, :163, :181`); the final 8 needs `ApprovalWithdrawal`
  and `ApprovalSubmission`, which are Tasks 6 and 5.
- **Red on the contract guard, then green.** After registering the slugs and before declaring them,
  `backend/tests/test_contracts.py` failed: `a schema present on exactly one side must declare that in ONE_SIDED_SLUGS
  (OQ-649 (b)): ['deployment', 'deployment-create', 'deployment-request', 'deployment-request-create', 'environment',
  'environment-create', 'environment-update']`. It also failed on the artifact-ref pattern (the model had `deployment`, the
  authored `common/artifact-ref.schema.json` did not); see deviation 2. After the edits: `test_contracts.py` 150
  passed, 2 skipped.
- **`ONE_SIDED_SLUGS` keys this slice added (Delta 4):** `environment`, `environment-create`, `environment-update`,
  `deployment`, `deployment-create`, `deployment-request`, `deployment-request-create`, each a new key in the
  generated-only block after `seed-from-model-request`. `"dislocation-run"` is untouched. Tasks 5 and 6 add
  `approval-submission` and `approval-withdrawal`.
- **Red on checks 30 and 35, then green (C18).** With the seven schemas regenerated and not registered,
  `python3 scripts/audit-docs.py` failed check 30 (``no `---` front-matter header found``) and check 35 (`in the
  checks-30-39 scope with no parseable header, and not in the F83 exemption register`) naming each of the seven files.
  After the seven literal paths went into `_CONTRACT_ARTIFACT_PATHS` (`scripts/audit-docs.py`, after the
  `seed-from-model-request` line) and `tests/test_audit_docs_ids.py`'s `non_markdown` count went 72 to **79**, the only
  failure is check 31 for LG-1405 (the working id, expected until minted). **F1 count:** 72 measured at base `8252741c`
  (SL-1377 merged, +2 over 70); +7 here. **Second-to-merge note:** this slice merges second against SL-1377, so the
  re-bump is this one; if anything else merges first, re-measure on the merged tree. The contract-schema skill step is
  already written by SL-1377 (`.claude/skills/contract-schema/SKILL.md` line 124), so the plan's conditional step is skipped.
  Two tests in `tests/test_audit_docs_ids.py` (`test_the_real_tree_passes_all_ten_checks`,
  `test_doc_id_check_exits_0_on_the_real_tree`) fail only on that check 31 gap; the count test passes.
- **Checks run, targeted (no suite-level gate, Task 7).** `ruff check .` clean, `mypy` 220 files clean, `lint-imports` 4
  kept 0 broken, `generate-contracts.py --check` 43 contracts match; `pytest packages/model-schema
  backend/tests/test_contracts.py tests/test_permission_parity.py`: 659 passed, 2 skipped. The backend tests that need the
  per-worktree database were not run here (no database for this worktree yet).
- **Deviations and flags, stated.**
  1. **`approval-policy` has no generated schema.** Acceptance 2 says "`approval-policy`'s schema carries the skip field".
     `ApprovalPolicy` is in no `GENERATED_SHAPES` slug at this tree (`find docs/contracts -name 'approval*'` finds only the
     authored `approval-request.schema.json`). The field is published in `docs/contracts/openapi/generated.json` (the
     `ApprovalPolicyEntry` component). I did not add an `approval-policy` slug, since the plan's slug list names none; the
     auditor decides whether the OpenAPI component discharges the clause.
  2. **`docs/contracts/schemas/common/artifact-ref.schema.json` is hand-edited, not regenerated.** The generator does not
     write it; the contract guard compares its `pattern` with the model's. The one-token edit (`deployment|` after
     `dataset_version|`) follows the precedent `109cd065` (WK-672 Slice 2), and the pattern now equals the generated
     `artifact-ref.schema.json`'s (compared in a script: True).
  3. **Regenerating moved ten other generated schemas** (`artifact-ref`, `peril-structure`, `regression-run`,
     `regression-suite`, `score-comparison`, `rate-table-version`, `seed-from-model-request`, `sub-graph*`): each embeds the
     artifact-ref pattern, which gained `deployment`. That is the generator's output, not an edit.
  4. **Shape fields the plan leaves open, chosen once here:** `Environment` carries `slug`, `name`, `description`,
     `promotion_order`, `requires_prior_environment`, `retired_at` and the derived `live_deployments` (a
     `LiveDeployment` list); `DeploymentRequest` carries `id`, `workspace_id`, `ref`, `environment`,
     `rating_version_ref`, `change_summary`, `status`, `approval_request_id`, `evidence`, `submitted_by`, `created_at`, with
     `evidence` a `DeploymentRequestEvidence` (`rating_version_approval: UUID`, `uat_deployment: UUID | PromotionSkip`,
     the two floor kinds' names). Task 3's row columns and Task 5's handlers read these; any change is a delta.
  5. **A process slip, corrected:** a `ruff format packages/model-schema` run reformatted 39 files the slice does not own.
     All but the three owned files were restored by checkout, and the one stray hunk in `approvals.py` was reverted by
     hand; the commits carry only this task's lines. The repository is not `ruff format`-clean at base (the format step is
     not part of the gate).
  6. The commit-msg hook refuses a `Claude-Session:` line (F49), so the four commits carry only `Co-Authored-By:`.

### Task 3 — the migration

Stamp 2026-10-03 22:53 BST (`TZ=Europe/London date`; `uptime` load average 2.53). Base: branch head `46beb268` (fetched,
checked out). A continuation executor, sonnet, `echo $CLAUDE_EFFORT` printed `medium`. Test database
`gipricing_agent-a725903e49a4a5364_5d69b56d`, created from the template and migrated to head. Revision
`c4a81f6d2e95`, `down_revision` `2f598e89d12c` (premise o, re-read: the only revision no `down_revision` named).

- **Red first, Acceptance 3.** `backend/tests/test_migration_deployments.py` (scratch database mirrored from
  `test_migration_dataset_owner.py`, except that it fails rather than skips when PostgreSQL is unreachable), run before
  the revision existed: 7 failed. The predicted cause, quoted: `relation "environments" does not exist`; the
  credential tests failed `DID NOT RAISE Exception`; the round trip `assert '2f598e89d12c' != '2f598e89d12c'`. After the
  revision: 7 passed. The first run failed for a reason of mine, not the plan's (`NotNullViolation` on
  `scoring_traces.status`): the row insert in the test now names `status`.
- **What the revision does.** The credential pre-check is the first statement of `upgrade()`, before any DDL: it
  selects unrevoked, **unexpired** `api_keys` and non-archived `service_accounts` whose `environments` list names
  anything outside `dev`/`uat`/`prod`, and raises `RuntimeError` naming each id and name. Tests: a `staging` key blocks
  (error names the key id, database stays at `2f598e89d12c`, no `environments` table); an expired unrevoked `staging`
  key does not appear in the error; after the key is revoked the upgrade runs; a `uat` key never blocks; a Service
  Account listing `staging` blocks and, once archived, does not. Then `environments` (`slug` unique, retired included;
  `requires_prior_environment` a foreign key to `environments.slug`; `promotion_order >= 1`), seeded `dev` 1 null, `uat`
  2 `dev`, `prod` 3 `uat`; `deployment_requests`; `deployments`; `scoring_traces.deployment_id` nullable foreign key.
  The seed test inserts a `prod` and a `staging` trace **before** the upgrade: both keep their `environment` string, both
  get a null `deployment_id`.
- **Red first, Acceptance 13 (Slice 2a's presence check).** With the three Row classes added and the revision not yet
  written, `test_every_guarded_table_carries_the_trigger_on_the_test_database` failed `no approval_guard trigger on:
  deployment_requests` (also `test_the_trigger_is_in_force_again_after_the_teardown_suspends_it`, the round trip and
  the derived-set test); `test_approval_guard.py`'s derived set failed on the extra table. The revision installs
  `approval_guard('deployment', 'slug')`, no `'flag'` argument. Tests changed to the new population:
  `test_approval_guard.py` `EXPECTED_GUARDED` gains `deployment_requests` and `len(derived) == 9` (its own comment said
  "Slice 2 adds `deployment_requests` here"); in `test_approval_guard_trigger.py` the guard's own revision keeps its 8
  (`SLICE_2A_TABLES`), the presence helpers take an optional population, and the derived-set test asserts the 8 plus
  `deployment_requests`. **A raw-SQL plant** in the new file: an approved `deployment_requests` insert is refused `GP001`
  with no approval request, with the decision flag forged by `set_config`, with a request still in `review`, and with
  another version's approved request; a decided request for the exact ref `deployment:dev@1` lets it through (positive
  control). The ORM and Core write forms and the cross-workspace case are Task 5's.
- **Deviations and flags, stated.**
  1. **`deployments` carries the `artifact_append_only()` trigger pair, which the plan does not list.** Red first:
     `test_every_table_the_grants_call_append_only_carries_both_triggers` failed `[('deployments', 0, 0)]` because the
     table has `SELECT, INSERT` grants and so enters that test's derived set (`00` FR-4 says a Deployment is never
     updated). The revision adds `deployments_no_modify` and `deployments_no_truncate`. `test_artifact_immutability.py`
     gains `deployments` in `APPEND_ONLY_TABLES` and in `_APPEND_ONLY_ROWS`; its `TRUNCATE` statement names
     `scoring_traces` too for this one table, because PostgreSQL refuses a `TRUNCATE` of a referenced table on the foreign
     key before any trigger runs (`cannot truncate a table referenced in a foreign key constraint`).
  2. **The suite's teardown wiped the seeds.** `backend/tests/conftest_db.py`'s `_EMPTY_THE_DATABASE` truncates every
     table but `alembic_version` and `tenant_marker`, so after the first session `environments` was empty and the new
     immutability test failed `null value in column "environment_id"` (observed red). The block now re-inserts the three
     seeds when the table exists; `ENVIRONMENT_SEEDS` is pinned equal to the migration's `SEEDS` by
     `test_the_teardown_restores_the_three_seeds_the_migration_wrote`, which also calls `empty_the_database()` and reads
     the rows back. **Task 4 and later tests that rename or retire a seed are covered by the same re-seed at session end;
     one that does so mid-session leaves the change until then.**
  3. **No `evidence` update trigger.** RL-1301 A.4 permits one and the plan makes it optional; the revision adds none, and
     the application's write-once rule for `evidence` is Task 5's. If the auditor wants the trigger, it is a delta.
  4. **`evidence` is `NOT NULL`** (the `DeploymentRequest` shape has it required; a request is created at submission), and
     the `deployments` row stores `deployment_request_id` (a nullable foreign key) where the shape's
     `deployment_request_ref` is derived from it at read.
  5. **Grants.** `environments` and `deployment_requests`: `SELECT, INSERT, UPDATE`, `DELETE` revoked from `gip_app` and
     `PUBLIC`; `deployments`: `SELECT, INSERT`, `UPDATE, DELETE` revoked. Tested through `has_table_privilege('gip_app', …)`.
  6. `alembic check` on the worktree database lists differences on `custom_metrics`, `custom_objectives`,
     `peril_structures`, `rating_versions`, `rate_table_versions` and an index on `models`; **none names a table this
     revision touches** (checked in the output: `environments`, `deployments`, `deployment_requests`, `scoring_traces` do not
     appear). They are at base and not this slice's.
- **Round trip, quoted rc.** On the worktree database: `alembic downgrade -1` rc 0, `upgrade head` rc 0, `downgrade -1` rc 0,
  `upgrade head` rc 0; `alembic current` prints `c4a81f6d2e95 (head)`. The scratch-database test does the same and also
  asserts that the downgrade drops the three tables, the column and the one trigger, and keeps Slice 2a's triggers.
- **Checks run (targeted; no suite-level gate, Task 7).** `pytest backend/tests/test_migration_deployments.py
  test_artifact_immutability.py test_approval_guard_trigger.py test_approval_guard.py test_approval_guard_static.py
  test_conftest_db.py test_audit.py`: all passed. `pytest backend/tests -k "trace or approval or contract or audit or rbac or
  permission"`: 602 passed, 2 skipped. `tests/test_repository_invariants.py` passes except the two tests that read
  `audit-docs.py` and fail only on check 31 for this ledger's working id (as at Task 2). `ruff check .` clean, `mypy` 220
  files clean, `lint-imports` 4 kept 0 broken.

### Task 4 — Environments: the entity and its routes (FR-428)

Stamp 2026-10-03 23:07 BST (`TZ=Europe/London date`; load average 6.76 on a shared box). Base: branch head `e10bbfb0`
(fetched, checked out). A continuation executor, sonnet, `echo $CLAUDE_EFFORT` printed `medium`. Test database
`gipricing_agent-a52a31535b6669265_7dbaa699`, created from the template and migrated to head `c4a81f6d2e95`.

- **Red first, the permission and the routes.** `backend/tests/test_environments.py` (25 tests), run before any router
  existed: 22 failed, 3 passed (the 3 are controls and the two 404 tests, which pass for the wrong reason, as the plan
  predicts). The predicted cause, quoted: `assert 404 == 403` on `POST /api/v1/environments`. After the router with the
  write dependency weakened to `settings:read`, the predicted second red: `AssertionError: assert 201 == 403` (the
  deployer creates an Environment); the same weakening re-run once the fixture was fixed gave the same line. The file's
  first draft granted `admin` and `deployer` to one principal, which made that test unable to fail; the deployer is now a
  second principal (an error of mine, found by running it red).
- **Red first, the A.6 existence checks.** With the router in place and `set_policy` and the two Service Account routes
  unchanged, 5 failed: `assert 200 == 422` (policy naming `prd`, policy naming a retired Environment), `assert 201 == 422`
  (a key for `prd`, a key for a retired Environment) and `assert 200 == 422` (rotation for an account naming a retired
  Environment). After the edits: 25 passed.
- **What the code does.** `platform/environments.py`: `list_environments` (retired included, ordered `promotion_order`
  then id, cursor is the last row's id), `create_environment`, `update_environment`, `retire_environment`,
  `require_existing` (non-retired, 422 `VALIDATION_FAILED` naming the slug and who named it). `api/environments.py`: the
  four routes; the three writes `Depends(requires(Permission.ADMIN_MANAGE_ENVIRONMENTS))`. `main.py` registers the router.
  `set_policy` calls `require_existing` for each environment-qualified `deployment` entry; `service_accounts.py` calls it at
  creation and at rotation (rotation checks the account's stored list). Each write has one Audit Event in the same
  transaction (`environment.created`, `.updated`, `.retired`, `entity_ref` `environment:<slug>`), asserted as the exact
  sequence, and a refused write adds none. Rename and retire load the row `FOR UPDATE`.
- **Retire refusals** (409 `VALIDATION_FAILED`, each naming what blocks): a live Deployment (the latest per workspace,
  naming the reference), a `deployment` policy entry naming the slug in any workspace's stored policy (or
  `DEFAULT_POLICY` when some workspace has no policy row), an unrevoked key. Tested on fresh slugs, each lifted by
  removing the blocker. The deployment test inserts a `DeploymentRow` directly (Task 5 has no route yet).
- **Acceptance 8, `admin:manage_environments`.** The predicate, verbatim: `grep -c -E '^> \| `(deployment:promote|admin:manage_environments)` \|.*\| WK-674 \|$' docs/specs/06-governance.md`
  printed 2 before and **1** after. Red first, quoted: with the check in place and the cell
  left as `WK-674`, `tests/test_permission_parity.py::test_live_tree_has_no_parity_violations` failed `Built name has a
  check site and still carries an owner: clear it in the same commit: admin:manage_environments (WK-674)`; after emptying
  the cell, 16 passed. The row is `docs/specs/06-governance.md:296`, not `:294` as the plan says.
- **Route types, rows 1-4 (Acceptance 14, 15).** `backend/tests/test_deployment_route_types.py` (11 tests): the route
  set pin (rows 1-4; the filter excludes `/deployment` paths until Task 5 widens it), an AST walk (each body-taking
  handler's `body` is the bare name the table gives, imported from `model_schema`; no-body handlers take none; the return
  annotation is the table's 2xx type, `Page[Environment]` for the list), and an OpenAPI check (request body and every 2xx
  exactly `{"$ref": ...}` of a name in `GENERATED_SHAPES`, the list's `Page_Environment_.items.items` the same, FD-1335's
  form 1 and form 2 refused by name), run against the live app and the committed `generated.json`. The checkers are pure
  functions, so the test file also feeds them broken copies and asserts each is refused naming the route.
- **Broken-input runs on the real handler** (each restored; run with `-k "in_the_source or ref_to_a_published"`):
  **A** body `dict[str, Any]`: the AST, request-body and 2xx tests all failed (3 failed). **B** a local `BaseModel` named
  `EnvironmentCreate`: the AST test failed (`not imported from model_schema`); the OpenAPI tests still passed, because the
  class has the same name and so the same `$ref`: **the plan's prediction that the OpenAPI half also fails does not hold
  when the local class reuses the published name**; only the AST half catches it (1 failed, 2 passed). **C** return
  annotation and `response_model` removed: AST and 2xx failed (2 failed). **D** `dict[str, Any]` return and
  `response_model`: AST and 2xx failed (2 failed).
- **The contract.** `generate-contracts.py` regenerated `docs/contracts/openapi/generated.json` (+695 lines: the four
  operations, `Environment`, `EnvironmentCreate`, `EnvironmentUpdate`, `LiveDeployment`, `Page_Environment_`);
  `--check` exits 0 ("43 generated contracts match the models"). No new slug (all three were Task 2's), so
  `_CONTRACT_ARTIFACT_PATHS` and the count are unchanged.
- **DEP-1.** `git grep -n -E 'from app\.(platform|api)\.(deployments|rating)' -- backend/src/app/platform/approvals.py`
  prints nothing (exit 1); `approvals.py` imports `app.platform.environments`, which is `07`'s.
- **Checks run, targeted (no suite-level gate, Task 7).** `pytest backend/tests/test_api_authorisation_sweep.py
  test_api_service_accounts.py test_api_approvals.py test_approvals.py test_contracts.py test_environments.py
  test_deployment_route_types.py test_auth_keys.py test_score.py tests/test_permission_parity.py`: 390 passed, 2 skipped.
  `ruff check .` clean, `mypy` 222 files clean, `lint-imports` 4 kept 0 broken. `ruff` had found a long line in
  `test_artifact_immutability.py:373` from Task 3's commit; wrapped here.
- **Deviations and flags, stated.**
  1. **The list route's permission is `settings:read`, a pick the plan does not make.** The plan names the permission only
     for the three writes. The sweep needs a declared permission or an allow-list entry, and `settings:read` is in
     `READ_PERMISSIONS`, so the Auditor reads Environments (FR-346). The lead or a decision-maker may prefer another; it is
     a one-line change plus the test's refusal case.
  2. **`live_deployments` is the latest Deployment of the caller's workspace in the Environment** (one entry), derived at
     read. `03` §4.12 says only that the live Deployment is "derived from these rows". Retirement is therefore refused
     while any workspace has any Deployment in the Environment (the latest is live), which stays true until a rollback or
     retirement of a Deployment exists. Task 5 and Slice 5 may refine "live"; the derivation is one function.
  3. **Conflicts and in-use refusals use `VALIDATION_FAILED` with 409**, as `POST /service-accounts` does for a duplicate
     slug. The plan names no code for them and a new code would be a spec change (`07` or `03` §5.1's catalogue).
  4. **The audit actions `environment.created`, `environment.updated` and `environment.retired` are not in any spec
     catalogue** (`03` §4.12 names the `deployment.*` ones). The plan names none for Environments; flagged for a spec row.
  5. **`07` §5.1's retire row reads "no live Deployment and that no policy entry names"; the plan and the code also refuse
     while an unrevoked key names it.** The row is Task 1's text; I did not edit it. A dated clause is the decision-maker's.
  6. **`requires_prior_environment` on create must name an existing, non-retired Environment** (422), which the plan does
     not say; without it the foreign key would answer 500.
  7. **A retired Environment is refused a rename and a second retirement** (409), which the plan does not say.
  8. **The retire key check reads unrevoked keys, expired or not**, as the plan words it; the Task 3 migration pre-check
     ignores expired keys. An expired key can be revoked through the existing route.
  9. The `06` permission row is at `:296`, not `:294`; the other Acceptance 8 cell (`deployment:promote`) is Task 5's.
### Task 5 — the deploy route, the Deployment Request and the `prod` approval (FR-267, FR-429, FR-272, NFR-498, G3, FR-347), with `RL-1401` Delta 7

Executor `executor-1256g`; `echo $CLAUDE_EFFORT` printed `medium`. Worktree `wt-1256g` from `14c7e805`, merged with
`origin/main` `7e2ee2ba` (`011b0b27`; only `docs/INDEX.md` conflicted, regenerated with `python3 scripts/doc-index.py`).
Test database `gipricing_wt-1256g_58a80177`, created from the template, `alembic upgrade head`.

**Commit 1 — the submission, the Author resolution (`RL-1401` item 1), T1 and T2.** The retired-Environment and the
uncompiled-version refusals (items 2 and 3, with T3 and T4) are **deliberately absent from this commit's code** so that
commit 2 shows them red against the broken input (the module's `_authorised_environment` had no `_require_not_retired`
call, and `_approved_compiled_version` took the hash without refusing its absence).

- **Red first, item 1 (a), (d), (e)** — the module and the routes exist, `CREATION_ACTIONS` is unchanged from `14c7e805`
  (the positive control "red at `14c7e805`": the tree before this commit has no deployment module at all, so the red is
  quoted at the first state in which the request exists and the key does not). Command, run from the worktree:
  `uv run pytest -q backend/tests/test_deployments.py --color=no --tb=line -rfEp` →
  `FAILED …::test_a_deployer_who_is_neither_submitter_nor_author_approves_a_deployment_request` (403
  `APPROVAL_AUTHOR_UNRESOLVED`: "deployment:prod@1 has no creation Audit Event, so whether the approver is its author
  cannot be checked"), `FAILED …::test_every_approvable_type_has_an_author_resolution` (`assert ['deployment'] == []`),
  `FAILED …::test_the_author_of_the_deployed_rating_version_is_not_barred_by_the_author_check` (the same 403);
  `PASSED` (b) `…submitter_cannot_decide…`, (c) `…no_creation_event_is_refused_fail_closed…` and the event-shape test.
  **`3 failed, 3 passed`.** (c) passes for the wrong reason before the key exists (the author is unresolved either way),
  which is why it is only meaningful after: its fixture deletes the event, and (a) green proves the event is there to delete.
- **Green** after `"deployment": "deployment_request.created"` in `CREATION_ACTIONS` and the route's `audit.record`:
  the same command, **`6 passed`**. The route records the event in the transaction that writes the row and calls
  `approvals.submit` (`platform/deployments.py::submit_request`), `entity_ref` the request's reference, actor the submitter.
- **Acceptance 8 (Branch A), `06` `deployment:promote` Check owner.** Predicate
  `grep -c -E '^> \| `(deployment:promote|admin:manage_environments)` \|.*\| WK-674 \|$' docs/specs/06-governance.md`
  printed **1** before and **0** after. Red first: with the handler's check in and the cell still `WK-674`,
  `uv run pytest -q tests/test_permission_parity.py --color=no --tb=short` →
  `Built name has a check site and still carries an owner: clear it in the same commit: deployment:promote (WK-674)`,
  `1 failed, 15 passed`; green after the cell is emptied. `origin/main` read: `7e2ee2ba` (SL-1360's parity test is on it).
- **Route types, rows 5-7 and row 9 (Acceptance 14, 15, 16).** `test_deployment_route_types.py` widened (`ROWS`,
  `MODULES`, the pin over all seven `/api/v1/environments` operations; row 9 is body-only). Red first for row 9, run over the
  `14c7e805` text of `api/approvals.py` and `docs/contracts/openapi/generated.json` with the test's own checkers
  (`/tmp/red16_1256g.py`): AST `['POST /api/v1/approval-requests: approvals.py body is SubmitApproval, not
  ApprovalSubmission']`, OpenAPI `["POST /api/v1/approval-requests: request body is {'$ref':
  '#/components/schemas/SubmitApproval'}, not {'$ref': '#/components/schemas/ApprovalSubmission'}"]`. `SubmitApproval` is
  gone from the backend (`ApprovalSubmission`, slug `approval-submission`, in `model-schema`); `Withdraw` stays (its body
  and `artifact_is_live` are Task 6's). Generated: `docs/contracts/schemas/generated/approval-submission.schema.json`,
  `_CONTRACT_ARTIFACT_PATHS` +1, `tests/test_audit_docs_ids.py` count **79 → 80** (measured at the branch merged with
  main `7e2ee2ba`: the test failed with `AssertionError: 80` before the bump), `ONE_SIDED_SLUGS` key
  `approval-submission` appended (a new key only; `dislocation-run` untouched, Delta 4).
- **Acceptance 18, the characterisation test** (`test_the_two_changed_approval_routes_return_exactly_the_declared_keys` in `test_deployment_route_types.py`): the
  12 keys of `service.to_dict`, `==`, `decisions == []`, for the generic route (a `rating_version` ref and a Deployment
  Request put back in `review` by a fixture), and withdraw. **It was written after Task 5's change to the routes and not
  before** (the plan wants it green first against the tree before the change); `git diff 14c7e805 -- backend/src/app/platform/approvals.py`
  touches only `CREATION_ACTIONS`, so `to_dict` and both routes' returns are unchanged. Red on broken input, `to_dict`
  patched: `out["extra"] = 1` → `added ['extra'], dropped []`; `out.pop("withdrawn_reason")` → `added [], dropped
  ['withdrawn_reason']`; `out["env"] = out.pop("environment")` → `added ['env'], dropped ['environment']`; each `1 failed`.
- **The refusals of Acceptance 4 not covered by Task 4** (`test_deployments.py`, 44 at this point): the broken-input runs,
  each on the real code, each restored (`diff` against the saved copy empty): **G3 type check deleted**
  (`-k "g3_a_reference and sub_graph"`): `FAILED …[sub_graph]`, `1 failed`; **the floor check removed from
  `apply_approval_decision`** (`-k stripped_of_a_floor`): `1 failed`; **the `WHERE status = 'approved'` removed**:
  the concurrent test still passed (the row lock serialises the two deploys, so the second reads `executed` earlier; `2
  passed`), so a **deterministic stale-snapshot test** was added (`test_a_stale_approved_snapshot_cannot_execute_a_request_twice`:
  the second deploy is handed the pre-execution row) and with the `WHERE` removed it fails (`1 failed`), green with it;
  **`audit.record` for `deployment.created` replaced by a no-op**: `FAILED …dev_then_uat_then_prod…` (`1 failed`).
  **The handler's `resource=` argument** is exercised in the test itself (`require_permission` wrapped to drop it: the
  `uat`-scoped Deployer is then refused in `uat`, asserted). **Not shown red**: the blanket-skip validator (Task 2's, its
  own tests) and the `retired`/`slug` refusals (Task 4's). `RL-886`'s refusal, A.4's floor at submission, A2's generic-route
  refusals (no row 404, not in review, stripped floor) and F4 (`require_in_review` in the module) have tests.
- **The approvals fan-out.** `api/approvals.py`: `_resolve_the_artifact` gains `deployments_service.resolve_artifact_ref`
  (a Deployment Request in `review` with both floor items, else 404 / 409 / 422), `_carry_to_the_artifact` gains
  `deployments_service.apply_approval_decision` (the only writer of `approved`, locked row, `require_in_review`, floor
  check). `platform/approvals.py` imports nothing from `deployments` (DEP-1).
- **The authorisation sweep.** Both writes are in `HANDLER_GUARDED` at `platform/deployments.py:84`
  (`require_permission(`); the sweep's no-roles half needed `RESOURCE_BACKED`, a per-route real path value and a
  Rating-Version ref, because G3 and the Environment load legitimately precede the permission check for a route whose
  resource is the Environment (a random id would answer 404 or 422, not 403). Red then green: before, `reachable with no
  roles: … → 404 / 422`.
- **Two existing tests that pinned the old shape were updated, not weakened**: `test_api_approvals.py::
  test_the_check_knows_the_creation_action_of_every_approvable_type` (now all eight) and
  `test_approval_guard.py::test_the_carry_walker_reaches_the_five_artifact_tables` (`deployment_requests` joins the four).
- **Checks run, targeted** (no suite-level gate, Task 7): `backend/tests/test_deployments.py`,
  `test_deployment_route_types.py`, `test_api_authorisation_sweep.py`, `test_contracts.py`, `test_environments.py`,
  `tests/test_permission_parity.py` together: **261 passed, 2 skipped** (after the one fix below);
  `test_api_approvals.py` and the five `test_approval_guard*.py`: **243 passed**; `tests/test_audit_docs_ids.py -k
  widening_the_scope_roots` passed. `ruff check .` clean, `mypy` 224 files clean, `lint-imports` 4 kept 0 broken,
  `python3 scripts/audit-docs.py` fails only check 31 (the working-id gap, expected while this ledger's id was a working id; minted as LG-1405 on 2026-10-04).
- **Deviations and flags, stated.**
  1. **The history route's permission is `rating:read`, a pick the plan does not make** (it names none). A no-permission
     route fails the sweep; `rating:read` is in the read set the Deployer, Approver and Auditor hold. A one-line change.
  2. **`EVIDENCE_INCOMPLETE` is also raised for a target with no predecessor Environment**, because the floor's
     `uat_deployment` item then has nothing to pin; the policy default (`prod`) has `uat`, so this arises only for a
     configured gated first Environment. Flagged for the decision-maker (a gated target with no predecessor).
  3. **A deploy to an ungated target that names a `deployment_request_ref` is refused 422** (`VALIDATION_FAILED`): the plan
     is silent, and ignoring the reference would record a request the Deployment did not execute.
  4. **A request for changes ends a Deployment Request as `rejected`** (it has no draft to return to and no resubmission
     route); `06` FR-355's "back to draft" has no state to return to.
  5. **`deployment.created`'s `entity_ref` is `environment:<slug>`** (`03` §4.12: "names the Deployment or the Environment
     it changes"); the Deployment id is in `after`.
  6. **Delta 6's `settings:read` text is not applied here** (it concerns Task 4's route, not Task 5); the `06` row still
     carries the old description. Flagged for the lead.
  7. The unreachable plan case "no decided approval request for the version" cannot be tested: the approval guard refuses
     an `approved` Rating Version with no approved request, so the evidence lookup always finds one.


**Commit 2 — the uncompiled-version and retired-Environment refusals (`RL-1401` items 2 and 3), T3 and T4.**

- **Red first, run against commit 1's code** (`uv run pytest -q backend/tests/test_deployments.py --color=no --tb=line
  -rfEp -k "never_compiled or content_hash or retired or unknown_slug"`): `FAILED …::test_an_approved_version_that_was_never_compiled_is_refused_at_both_routes`
  (`assert 500 == 409`: the deploy reaches the `bundle_hash` format constraint), `FAILED …::test_a_bundle_with_no_content_hash_is_refused_the_same_way`,
  `FAILED …::test_a_retired_environment_is_refused_at_both_routes_and_writes_nothing` (404 `NOT_FOUND` "No rating version
  rating_version:no-such-version@1": the version is read before the Environment is checked, which is the order the
  ruling reverses), `PASSED …::test_the_permission_check_comes_before_the_retired_refusal_and_an_unknown_slug_is_404`
  (the control: it holds before and after). **`3 failed, 1 passed`**, as predicted in each docstring.
- **Green** with `environments._require_not_retired(env, "deployed to")` after the permission check in
  `_authorised_environment` and the `content_hash` refusal after the `approved` check in `_approved_compiled_version`:
  the whole file, **`49 passed`**. Both routes call both helpers, so the order the ruling fixes is in one place.
- **T3 and T4** applied in this commit (`03` §4.12's two invariant bullets after "`approved` Rating Versions only", and the
  dated parenthetical on the two §5.1 rows), verbatim from `RL-1401`'s §"Spec texts, with placement"; **T1 and T2** are in
  commit 1, with the code that makes them true.
- **Deviation from item 3's fixture, stated.** The ruling says "retire `uat`". The Environments are deployment-wide and the
  suite re-seeds them only at session end, so the test retires a **fresh** Environment (created, then retired), which has
  no live Deployment and no policy entry either; retiring `uat` would break every later test that deploys to it. The
  ruling's case is the same check on the same code path.
- **Item 2's fixture, stated.** "Approved through a no-suite submission and never compiled" is built as an `approved`
  version with `bundle = null` (`approved_rows.add_approved`, the approval guard satisfied), which is the state such a
  submission leaves: only `compile` writes `bundle`, and a version cannot compile once it has left `draft` (`RL-1379`).
- **T3's last sentence is not tested**: "a request approved before its target was retired is refused when it is executed"
  holds because the deploy route runs the retired check unconditionally, but the case cannot be built through the routes:
  retiring an Environment a policy entry names is refused (Task 4), and without the entry the target is ungated and takes
  no request. Flagged.
- **Checks run, targeted**: `test_deployments.py`, `test_deployment_route_types.py`, `test_api_authorisation_sweep.py`,
  `test_contracts.py`, `test_environments.py`, `tests/test_permission_parity.py` together: **266 passed, 2 skipped**.
  `ruff check .` clean, `mypy` 224 files clean, `lint-imports` 4 kept 0 broken.

### Task 5A — the compile guard, as RL-1379 rules (FD-1393; DP-S2-7; Delta 1) — executor-1256h, 2026-10-04

**Tree.** Worktree from `origin/sl-1256-environment-and-deployment-record` at `2ef9f675`; own test database
`gipricing_wt-1256h_59e99a54`, created from the template and migrated to head.

**Red first** (RL-1379 C1–C4 in `backend/tests/test_rating_version_compile.py`, source under `backend/src/` stashed, tests
kept; `uv run pytest -q backend/tests/test_rating_version_compile.py -k "c1_ or c2_ or c3_ or c4_" -rf --tb=line`):

```text
FAILED backend/tests/test_rating_version_compile.py::test_c1_the_route_refuses_to_compile_a_version_that_has_left_draft[review] - AssertionError: {"id":"01a106c4-56c6-721d-92de-06b557b151c4","workspace_id"...
FAILED backend/tests/test_rating_version_compile.py::test_c1_the_route_refuses_to_compile_a_version_that_has_left_draft[approved] - AssertionError: {"id":"01a106c4-5a2d-7781-aed9-a90f88dee28b","workspace_id"...
FAILED backend/tests/test_rating_version_compile.py::test_c1_the_route_refuses_to_compile_a_version_that_has_left_draft[live] - AssertionError: {"id":"01a106c4-5c8a-7118-8cb9-e74c557b471d","workspace_id"...
FAILED backend/tests/test_rating_version_compile.py::test_c1_the_route_refuses_to_compile_a_version_that_has_left_draft[retired] - AssertionError: {"id":"01a106c4-5eeb-7f07-b047-31d3b0c04b5c","workspace_id"...
FAILED backend/tests/test_rating_version_compile.py::test_c1_the_route_refuses_to_compile_a_version_that_has_left_draft[approved+deployment] - AssertionError: {"id":"01a106c4-62f5-7930-984d-34d7ef6dc546","works
FAILED backend/tests/test_rating_version_compile.py::test_c2_the_service_refuses_a_status_that_changed_after_submission - AssertionError: assert <JobStatus.SUCCEEDED: 'succeeded'> is <JobStatus.FAI...
FAILED backend/tests/test_rating_version_compile.py::test_c4_control_a_version_returned_to_draft_compiles_again - AssertionError: assert 202 == 409
7 failed, 1 passed, 12 deselected, 1 warning in 6.89s
```

Predicted and found: **C1** (5 cases): 202 and a queued `rating.compile` Job where 409 is ruled (assert at the
status check). **C2**: the Job `succeeded` where `failed` is ruled. **C3** (control, draft compiles twice): passes red and
green. **C4** (control): red before only because its first step asserts the 409 on `review`; its second step (back to
`draft`, compile succeeds) is the green control.

**Green** (guard in): the same selector, then the whole file, `test_rating_versions.py`, `test_errors.py`,
`test_bundle_slot.py`, `test_contracts.py`: **240 passed, 2 skipped**; the compile file alone **20 passed**.

**What was built.** `rating_versions.require_compilable` (the ruling's `raise`, verbatim) is called by
`compile_rating_version` after its `FOR UPDATE` load and by the compile route before `job_service.submit`. One guard, two
callers. `load_rating_version` gained `for_update: bool = False` (`session.get(..., with_for_update=…,
populate_existing=…)`), used by `compile_rating_version` and `submit_for_review`. The route's `responses` gain 409.
`RATING_VERSION_IMMUTABLE` is in `RATING_ERROR_CODES` with T3, in the same commit. `bundle_slot.py` carries the ruling's
correcting paragraph. `docs/contracts/openapi/generated.json` regenerated; `docs/INDEX.md` regenerated (its FR-4 and
FR-239 rows quote the amended text). T1–T4 applied byte-for-byte.

**The two `FOR UPDATE` locks: delivered, not concurrency-tested** (the ruling's own verdict for them). The lines:
`backend/src/app/platform/rating_versions.py`, `load_rating_version`'s `with_for_update=for_update`, with
`for_update=True` at the `compile_rating_version` and `submit_for_review` call sites.

**Gates, targeted.** `ruff check .` clean; `mypy` 224 files clean; `lint-imports` 4 kept 0 broken;
`generate-contracts.py --check` 44 match; `audit-docs.py` fails check 31 only (the working-id gap, the expected
one for this ledger's draft id; it is the same at the base).

**Deviations, stated.** (1) `<fix date>` is written `2026-10-04`, the date of this commit, as RL-1379 §"Spec texts" defines
it; Delta 1 says "the slice's merge date". The two differ; the lead decides whether to re-stamp at merge. (2) The deployment
case of C1 deploys through the S2 route (`POST /environments/dev/deployments`) a version whose `bundle` the test compiled.
(3) C4 sets `review` and `draft` by direct write (the guard reads the status, not the path); the `changes_requested` decision
path is not exercised by C4, and `_target_status` has no test of that path (corrected 2026-10-04 on the slice audit, which
found none; this ledger had said its own tests covered it). C4 writes the status directly because the compile guard reads
only the status, so a direct write reaches the state the guard sees without a second route. (4) The ruling item 2's note that the handler's `prior_hash` read stays:
untouched.

### Task 6 — default-live scoring, the trace link and server-derived liveness (RL-880, RL-888, RL-916, RL-1380, FR-357) — executor-1256i, 2026-10-04

**Tree.** Branch `sl-1256-environment-and-deployment-record` on `8879e2ad` (Task 5A), plus this task's commit.

**Red first** (pre-change code, test files only edited; `LOKY_MAX_CPU_COUNT=4`, own test DB, no suite run):

```
uv run pytest -q -p no:cacheprovider --no-header -rf backend/tests/test_score.py -k "live_deployment or no_deployment_still or no_environment_and_no_ref or default_live_trace or equal_to_the_live or not_live_carries or no_live_deployment_carries or recorded_mid_request"
FAILED test_a_quote_with_no_ref_is_scored_against_the_environments_live_deployment - AssertionError: {"type":"https://docs.gi-pricing.dev/errors/no-live-rating-...
FAILED test_a_caller_with_no_environment_and_no_ref_is_refused_even_when_deployments_exist - AttributeError: module 'app.api.score' has no attribute '_serving_ref'
FAILED test_a_default_live_trace_carries_the_deployment_that_served_it - AssertionError: {"type":"https://docs.gi-pricing.dev/errors/no-live-rating-...
FAILED test_an_explicit_ref_equal_to_the_live_version_carries_its_deployment - AssertionError: assert None == UUID('01a106c9-ac2f-788a-a931-2e8f3a3a5026')
FAILED test_a_deployment_recorded_mid_request_does_not_relink_the_trace - AssertionError: {"type":"https://docs.gi-pricing.dev/errors/no-live-rating-...
5 failed, 4 passed, 33 deselected

uv run pytest ... backend/tests/test_traces.py -k completed_trace_still
FAILED test_a_completed_trace_still_carries_the_deployment_it_was_written_with - TypeError: write_pending_trace() got an unexpected keyword argument 'deploy...
1 failed, 38 deselected

uv run pytest ... backend/tests/test_api_approvals.py -k "withdraw or no_longer_assert or with_no_deployment"
FAILED test_withdrawing_after_deployment_is_refused - AssertionError: {"id":"01a106c9-fad0-7ad7-a100-f456e81b315d","artifact_ref"...   (the withdrawal SUCCEEDED, 200)
FAILED test_a_client_can_no_longer_assert_that_the_artifact_is_not_live - AssertionError: {"id":"01a106c9-fe9b-7bd1-b578-1888242d890e","artifact_ref"...   (200, not 422)
2 failed, 1 passed, 94 deselected

uv run pytest ... backend/tests/test_deployment_route_types.py
FAILED test_every_request_body_is_a_model_schema_type_in_the_source / ..._a_ref_to_a_published_shape / test_every_2xx_is_a_ref_to_a_published_shape / test_the_committed_contract_types_the_routes_the_same_way / test_the_approval_submission_body_is_a_model_schema_type_not_a_class_the_api_defines (backend/src/app/api/approvals.py:84:class Withdraw(BaseModel):) / test_the_withdrawal_body_is_a_model_schema_type_with_no_liveness_field (ImportError: cannot import name 'ApprovalWithdrawal')
6 failed, 12 passed
```

Predicted and found: both withdrawals **succeed** because the route trusts the body; the default-live quote gets the 409.
The passes in the first group are the guards that hold before and after (an explicit ref to a non-live version or slug, and
one in an environment with no Deployment, carry null; `uat` with no Deployment still 409s). The positive control
(`a_rating_version_with_no_deployment_can_still_be_withdrawn`) passes red and green.

**Green:** the same four commands: **9 passed**, **1 passed**, **3 passed**, **18 passed**. Wider targeted run (not the
gate): `test_score.py test_traces.py test_api_approvals.py test_approvals.py test_contracts.py test_deployment_route_types.py
test_api_authorisation_sweep.py test_deployments.py tests/test_audit_docs_ids.py`: see the commit-time rerun below.

**What was built.** `score._serving_ref(database, caller, ctx)` (beside `_required_ref`) resolves the ref and the
Deployment together, once, before `_compiled_for`: default-live = the caller Environment's latest Deployment of the
workspace (same predicate as `environments._live_by_environment`); explicit ref = that Deployment only if its
`rating_version_ref` string equals `str(ref)` exactly, else null; no caller environment = no live Deployment. `_required_ref`
keeps the 409 and takes the live ref (docstring: dated note, original sentence quoted). `_maybe_sample_trace` gains
`deployment_id` (default `None`, existing direct callers unchanged) and passes it to `traces.write_pending_trace`, which
gains the same keyword; `complete_pending_trace` copies `deployment_id` into the re-inserted row (#974 F1).
`/score/compare` and `/score/batch` untouched. `Withdraw` is removed; the body is `model_schema.ApprovalWithdrawal`
(`reason` only, slug `approval-withdrawal`, frozen, `extra="forbid"`); `withdraw_request` derives liveness with
`_is_deployed` (artifact type `rating_version` and any `DeploymentRow` of that ref in the workspace) and passes it to
`service.withdraw`, whose signature is unchanged. `ONE_SIDED_SLUGS` gains the new key `approval-withdrawal` only (Delta 4;
`dislocation-run` untouched). `_CONTRACT_ARTIFACT_PATHS` gains the one path and the count goes 80 → 81 (measured at the
branch head `8879e2ad`, where it was 80).

**Acceptance 17 (read-only callers).** The signature script (`_fetch_bundle`, `_compiled_for`, `ast` `args` and `returns`,
`origin/main` against the working tree) prints nothing. `git diff --stat origin/main...HEAD -- api/models.py
worker/scoring_handlers.py worker/trace_handlers.py` prints `models.py | 9 +++++++--`: **not this task**: hunks at
`:1235`, `:1249`, `:1253` are the compile route and `submit_rating_version` from Task 5A (RL-1379, PL-1392 C14), and
the governance gate's `_fetch_bundle` call (`:1215`) is untouched. This task's own diff touches none of the three files
(`git diff --name-only` for the task commit).

**Deviations, stated.** (1) Acceptance 7's route-level cases are in `backend/tests/test_score.py`, beside the scoring
fixtures (`scoring_headers`, `_rows_for`, the held-bundle patch); the completion case is in `test_traces.py`.
(2) The default-live per-request read is one extra indexed query on `/score`; it is not measured against NFR-489 here
(that is Task 7's or WK-671's measurement). (3) `_serving_ref`'s bearer-caller refusal is tested on the helper, because no
credential produces a no-environment `Caller` over HTTP.

### Task 5B — RL-1404 items 1–6 and S1–S5, with Deltas 5 and 6 — executor-1256j, 2026-10-04

Merge: `origin/main` `374e630b` into the branch; the one conflict was the generated `docs/INDEX.md`, taken from main
and regenerated with `python3 scripts/doc-index.py`.

**Reds, each quoted (test file `backend/tests/test_deployments.py`, run `uv run pytest -q -k <name>`).**
- D2 `test_a_gated_environment_with_no_predecessor_refuses_every_request_naming_the_remedy`, red at the unchanged
  `submit_request` detail: `E  assert ('remove' in "'env-2d641b8b' has no predecessor Environment to pin a deployment or a skip of.")`
  at `:838`, `1 failed`. Green after the detail names the remedy (the assertion is then the exact sentence
  "Remove the `deployment` policy entry for '<slug>'").
- D3 (completed), D4 and D5 tests are **green at once**: RL-1404 rules the code right in all three, so there is no
  red to quote; each is proven by its broken input below. The four-test run printed `1 failed, 3 passed` before the
  D2 code change and `4 passed` after.

**Broken-input proofs (each restored to the D2-only diff, `git diff --stat backend/src` = 1 file, 4 lines).**
- D3: the ungated `deployment_request_ref` refusal made unreachable (`if False:`):
  `test_a_request_for_another_version_or_environment_does_not_authorise_a_deploy` fails,
  `E  assert 201 == 422` at `:741`.
- D4: the `ApprovalStatus.CHANGES_REQUESTED` entry removed from `apply_approval_decision`'s map:
  `test_a_request_for_changes_ends_a_deployment_request_rejected` fails,
  `E  AssertionError: assert 'review' == 'rejected'` at `:886`.
- D5: `environments._require_not_retired` removed from `_authorised_environment`:
  `test_a_request_approved_before_its_target_was_retired_is_refused_at_execution` fails on (i), the deploy naming the
  request, `E  assert 422 == 409` at `:924` (D3's check refuses it first, as the ruling predicts). The loop stops at
  the first refusal, so (ii)'s write is **not** separately shown by this run.

**Texts applied (date 2026-10-04, `<RL id>` = RL-1404):** S1 (`06` `rating:read` row), S2 (`03` §4.12 "Two pinned evidence
items" bullet), S3 (`03` §4.12 deploy-route bullet), S4 (`06` FR-355 cell), S5 (`06` workflow row 5a), Delta 5 (`00`
§2.3 "Deployment Request" row, after **Deployment**), Delta 6 (`06` `settings:read` row). `api/deployments.py:39` stays
`Permission.RATING_READ`. No new error code.

### Task 7 — the minted-head gate and NFR-489 (Delta 9, Delta 10) — executor-1256n, 2026-10-04

Executor charter line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the lead — the highest-volume role;
per-slice gates and the auditor's re-check bound the risk of a cheaper setting." `echo $CLAUDE_EFFORT` printed `medium`.

**Object measured:** a clean detached checkout of `4304748898ed56b8db29f5a2c2ef7f1c2f47c544` (`git status --porcelain` empty),
`uv sync --all-packages` first. Slot `/tmp/slots/gate-1` (granted by the lead for that head only), announced with
`write_runtime_state.py announce --what full_test_suite --by executor-1256n`. Gate window 13:37:09 to 14:02:35 UTC
(`date -Iseconds` read 2026-10-04T13:37:09+00:00 and 2026-10-04T14:02:35+00:00; 25 min 26 s). Test database: a
per-worktree copy of `gipricing` made with `createdb -T`, then `alembic upgrade head`. Gate body: the `dev-commands` body
with `ruff check --no-cache`, `mypy --no-incremental` and `LOKY_MAX_CPU_COUNT=4`, plus the frontend six after the seven
parallel stages; slot wrapper `flock -n -E 99 /tmp/slots/gate-1 -c "export GIP_GATE_SLOT=/tmp/slots/gate-1; …"`.

| stage | rc | totals |
|---|---|---|
| `ruff check --no-cache .` | 0 | All checks passed |
| `mypy --no-incremental` | 0 | no issues found in 224 source files |
| `lint-imports` | 0 | 4 contracts kept, 0 broken |
| `pytest -q` (`LOKY_MAX_CPU_COUNT=4`) | 0 | **4790 passed, 3 skipped, 0 failed**, 85 warnings, 1443.05 s |
| `generate-contracts.py --check` | 0 | 45 generated contracts match the models |
| `audit-docs.py` | 0 | "All checks passed." (fully green) |
| `req-coverage.py` | 0 | report printed, rc 0 |
| `pnpm --dir frontend install --frozen-lockfile` | 0 | |
| `pnpm --dir frontend generate:api` | 0 | |
| `pnpm --dir frontend lint` (`eslint . --max-warnings 0`) | 0 | |
| `pnpm --dir frontend type-check` (`vue-tsc --build --force`) | 0 | |
| `pnpm --dir frontend test` | 0 | 97 files, 612 tests passed |
| `pnpm --dir frontend build` | 0 | chunk-size advisory only |

**Load.** Start (13:37:00 UTC): `load average: 1.53, 1.12, 1.15`; free 23009 MB, available 28256 MB of 32099 MB, swap 0;
`flock -n /tmp/slots/gate-2 true` rc 0 (free); 0 pytest processes. End (14:02:35 UTC): `load average: 5.95, 3.35, 2.55`;
free 21827 MB, available 27678 MB; gate-2 rc 0.

**NFR-489 (Delta 9).** Predicate, the NFR-489 row (`docs/specs/03-rating-engine.md:1258`, no dated amendment on the row):
"Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call
(NFR-454). Without a GBM call, p99 < 15 ms."

- **The harness was stale at the head, and a scratch fix was needed to run it at all.** `scripts/bench-rating.py --http` died
  in `_measure_fetch` with `TypeError: _fetch_bundle() missing 1 required positional argument: 'slot'` (rc 1; the script
  calls `_fetch_bundle(database, blob_store, workspace_id=…, ref=…)`, and `_fetch_bundle` takes a `slot` parameter at the head; the script's own last
  changes are `98eca403` and `71f5a220`). The side measurement was patched in a scratch copy only
  (`BundleSlot()` passed as the third argument; 3 lines; never committed). The sweep through the route is unaffected.
- **Commands, verbatim.** Both passes: `cd <checkout>; GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_bench1256n PYTHONUNBUFFERED=1 timeout 280 uv run python scripts/bench-rating.py --http --warmup 50 --iterations 100 --abc-iterations 20 --rates 25,50`.
  "With" = the head's `_serving_ref` (one indexed Deployment read per request when the caller has an Environment; the bench's
  key is scoped to `uat`, so the read runs). "Without" = a scratch checkout of the same SHA with
  `if caller.environment is not None:` changed to `if False and caller.environment is not None:` in `_serving_ref`. Deployments and
  deployment_requests rows in the bench database: 0 and 0 (`select count(*)`), so "with" measures the read against empty
  tables, a lower bound for its cost. The default sweep (25 to 200 rps, `--rates` omitted) was also run once per arm with
  `--warmup 50 --iterations 100 --abc-iterations 20` and cut at `timeout 540`.
- **Component half (`score_one` alone, same box, load 1.06; the read is not on this path):** with GBM p50 7.966 ms, p99 10.964 ms
  against 50 ms: PASS. Without GBM p50 5.443 ms, p99 9.634 ms against 15 ms: PASS.
- **Full HTTP path, p50 / p99 in ms, 25 rps offered** (uncontended: load 1.2 to 2.1 recorded per rung by the script; lines
  are with GBM then without GBM):

| run | arm | with GBM p50 / p99 (budget 50) | without GBM p50 / p99 (budget 15) |
|---|---|---|---|
| 1 | without the read | 33.7 / 45.3 | 32.6 / 45.2 |
| 1 | with the read (head) | 35.5 / 51.0 | 34.9 / 50.2 |
| 2 | without the read | 39.0 / 59.1 | 36.7 / 52.6 |
| 2 | with the read (head) | 42.8 / 58.6 | 39.3 / 71.2 |
| default sweep | without the read | 37.4 / 51.3 | not captured |
| default sweep | with the read (head) | 36.1 / 48.4 | not captured |

  The 50 rps rung: p50 44.7 to 62.9 ms in every run, p99 between 67 and 2405 ms (queueing knee), in both arms. The 100 and 150
  rps rungs of the sweep ran away to p99 above 30 s in both arms; the 200 rps rung was never reached inside `timeout 540`
  (the 100 rps rung's backlog already runs for minutes; a first head run with no `--rates` hit `timeout 1800` for the same reason). **200 rps, the rate NFR-489 names, is
  not measured by this run.**
- **Reading.** The head's full HTTP path as this harness drives it is over the 50 ms and 15 ms budgets at 25 rps in most runs
  **with and without the read**, and the p99 spread between repeats of one arm (45.3 to 59.1 ms) is larger than the
  difference between arms. The read's cost is not resolved from run-to-run noise at p99; at p50 the "with" arm is 0 to 3.8 ms
  above "without" in the pairs run. Two runs per arm cannot establish more.
  Whether the harness saturates near 40 rps on `main` (with the Deployment code absent) was **not** measured; the component half
  passes, so the over-budget figures belong to the route path, not to the evaluator, and are not shown to be this slice's.
  The auditor rules the NFR-489 verdict; the 200 rps rung and the saturation owner (SL-1259 or F35, not checked here) are open.
- **Correction (the lead, after Task 7 was written): the gate window was contended, the bench passes were not.** The box clock
  is UTC (`date` 15:06:20 UTC = `TZ=Europe/London date` 16:06:20 BST); the stamps above are UTC. The lead's
  `doc-id migrate --verify` ran 14:38:49 to 14:57:17 BST and the deputy's about 14:58 to 15:03 BST (load 7.76), that is
  13:38:49 to about 14:03 UTC. **The gate (13:37:09 to 14:02:35 UTC) overlapped it**, so its end load of 5.95 and its 25 min
  26 s wall time are not an uncontended reading; pass/fail stands per the lead. The "uncontended: 0 pytest processes at start"
  claim above holds only at the gate's start, 13:37:00 UTC.
  **Bench passes, start to end (UTC, then BST) and `uptime` load at the pass's end:** the crashed run
  14:02:54 to 14:05:53 UTC (15:02:54 to 15:05:53 BST; load 2.06; overlaps the window's tail; no numbers taken from it);
  the run that hit `timeout 1800` 14:06:08 to 14:36:08 UTC (load 1.18; no numbers taken from it);
  the "with" pass of the default sweep, after 14:36:08 UTC and ended by 14:45:44 UTC (15:36 to 15:45 BST; its component
  half at load 1.06 to 1.42); the "without" pass 14:45:44 to 14:54:44 UTC (15:45:44 to 15:54:44 BST; load 1.23);
  the four 25,50 rps passes, run in order without, with, without, with, 14:54:44 to 15:04:35 UTC (15:54:44 to 16:04:35 BST;
  load 1.13 at the first start, 1.50 at the last end). **Every pass whose numbers are reported started after the window's
  end (14:03 UTC), so none is re-run.** The per-rung loads the script printed were 0.8 to 2.1 throughout.
- **NFR-489 verdict (the lead), 2026-10-04 16:07 BST: deferred with an owner — SL-1259** (WK-674 Slice 5, which lists NFR-489's
  measurement, docs/roadmap.md :962). Trigger: SL-1259's dispatch record carries this entry's numbers, the `bench-rating.py --http`
  fix, and main's own full-path figures. The numbers above are informative only: no per-pass clock times were recorded, and a
  contention window (14:38:49–15:03 BST) overlapped this session's gate. Task 6's Deployment read is below the measurement noise.
  Slice audit record: `handover/audit-sl1256-2026-10-04.md` (closing `status: closed` per document-ids.md §1.6, 2026-10-04 amendment).

## PRs

Not yet opened (draft PR at the first push).
