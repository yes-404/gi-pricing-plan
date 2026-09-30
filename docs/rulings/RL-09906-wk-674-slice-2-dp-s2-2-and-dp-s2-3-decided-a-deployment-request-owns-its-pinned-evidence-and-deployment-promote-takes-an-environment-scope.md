---
id: RL-9906
family: ruling
title: WK-674 Slice 2 DP-S2-2 and DP-S2-3 decided — a deployment request owns its pinned evidence, and deployment:promote takes an Environment scope
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                    # set to the OQ-1234 ruling's minted id at this record's mint turn (item C)
relates: [PL-1237, CR-1212, RL-1232, FR-267, FR-429, FR-345, FR-356, FD-1200]
---

# RL-9906 — WK-674 Slice 2 DP-S2-2 and DP-S2-3 decided: a deployment request owns its pinned evidence, and `deployment:promote` takes an Environment scope

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). Its term was
extended through this record by the entry "2026-09-30 11:04:57 BST — WK-674 S2 DPs: routing
agreed; dm-effort-high extended; errors.py". That entry also set the conditions ruled in
item A.4 and item C.

The decision points are those of WK-674 Slice 2's leaf plan, which planner-924 is writing
(PL working id 9920, SL-1256). **At the time of writing its branch was not pushed**:
`git ls-remote origin` listed no `wk674-s2*` ref. So this record rules from the lead's relay
of the options, and from premises that this session verified at `9f63d0fe` (below). DP-S2-1,
a trace's link to its Deployment, is the medium-effort decision-maker's.

## Presence and absence, as verified at `9f63d0fe`

| Claim | Verdict | How it was verified |
|---|---|---|
| `deployment` as a reference type | **absent** | `ARTIFACT_TYPES` (`packages/model-schema/src/model_schema/refs.py:20-29`), read. It has no `"deployment"`. `ArtifactRef`'s validator refuses a type outside it (`:88-90`, `if match["type"] not in ARTIFACT_TYPES: raise`). `REF_PATTERN` is built from it (`:51-53`). **No `ArtifactRef` can name a deployment.** |
| The policy is keyed `deployment` | **present** | `EVIDENCE_FLOOR["deployment"] = ("rating_version_approval", "uat_deployment")` (`packages/model-schema/src/model_schema/approvals.py:107`). `approvals.submit` looks up `policy.entry_for(artifact_ref.type, environment)` (`backend/src/app/platform/approvals.py:226`). A `deployment` entry can therefore never be reached by a request whose ref must be one of `ARTIFACT_TYPES`. |
| An evidence column on the approval request | **absent** | `ApprovalRequestRow` (`backend/src/app/db/models.py:611-640`), read. Its columns are `id`, `workspace_id`, `artifact_ref`, `artifact_type`, `environment`, `submitted_by`, `submitted_at`, `change_summary`, `status`, `approvers_required`, `withdrawn_reason` and `decided_at`. None holds evidence. |
| Where evidence lives today | **present, on the owning module's row** | `rating_versions.submit_for_review` writes `row.evidence` on the Rating Version's own row, then calls `approvals.submit` (`backend/src/app/platform/rating_versions.py:294-300`). Generic `approvals.submit` (`platform/approvals.py:192-282`) checks the policy entry and the reference, and nothing else. |
| The single decision path | **present** | `api/approvals.py`'s decide and withdraw routes call `_carry_to_the_artifact` (`:260`, `:293`, defined `:488`). It drives each owning module's `apply_approval_decision`, for example `rating_versions.py:312`, which writes the row's status at `:360` (`row.status = target.value`) from the mapping whose `APPROVED` entry is `:382`. The status itself comes from `_resolve_status` (`platform/approvals.py:547-554`). |
| Scope types | **present: four, no environment** | `ScopeType` (`packages/model-schema/src/model_schema/permissions.py:91-102`): `workspace`, `dataset`, `model_family`, `rating_algorithm`. `_covers` (`backend/src/app/platform/rbac.py:205-217`) lets a workspace-wide assignment cover everything. With no `resource`, it admits **only** a workspace-wide assignment. |
| CR-1212 item 4 | **present** | `docs/closures/CR-01212-…md:342-345`: "a `06`/`07` spec change that scopes `deployment:promote` to named environments, owned by WK-674 and landed with its environment record". `RL-1232` DP-6, as amended 2026-09-29 (`docs/rulings/RL-01232-…md:303-322`), leaves the mechanism to that item. |
| FR-345 | **present** | `06-governance.md:81`: "Role assignments are **scoped**: workspace-wide, or limited to named Datasets, Model Families, or Rating Algorithms". It names no Environment. |

## Ruled

### A. DP-S2-2 — option (a): a deployment request is its own artifact, owned by the deployment module, and its row pins its evidence

1. **The subject of a `deployment` approval request is a Deployment Request.** It is a row
   owned by the module that owns deployment (`03` FR-267, built in WK-674 Slice 2).
   - `"deployment"` joins `ARTIFACT_TYPES`, and `docs/contracts/schemas/common/artifact-ref.schema.json`
     is regenerated with it, since the list is a spec change (`refs.py:18-19`).
   - A request is referenced as `deployment:<slug>@<version>` (ID-3). The slug is immutable,
     and the version is monotone per slug (ID-2). **The leaf plan chooses the slug scheme,
     under one constraint:** the slug must not be a renamable name. An Environment can be
     renamed (`07` FR-428; `admin:manage_environments`), and a reference must never change
     its meaning.
   - The row pins the approved Rating Version it deploys, and the target Environment's
     **identity** (not its name).
2. **The evidence lives on that row, written once at submission, before `approvals.submit`
   is called**, as `rating_versions.submit_for_review` does today. This is the established
   pattern, so no evidence column is added to `ApprovalRequestRow` (option (c)), and
   governance keeps importing nothing from the owning module. The two floor items
   (`approvals.py:107`):
   - **`rating_version_approval`**: the decided approval request of the pinned Rating
     Version;
   - **`uat_deployment`**, the predecessor item: **either** the id of the successful
     predecessor Deployment of that Rating Version, **or** a skip record, naming the skipped
     environment and a non-empty reason. A skip record is valid only where the target's
     environment-qualified `deployment` policy entry permits the skip (the OQ-1234 ruling, item
     1).

   The owning module checks the floor and FR-429's one predicate before it writes. A
   request missing either item is refused with `EVIDENCE_INCOMPLETE`.
3. **Why not (b) or (c).**
   - (b) names the Rating Version with a policy-key override. The Rating Version has its own
     `rating_version` approval, so one ref would carry two kinds of request. Evidence would
     still have no home: (b) moves the key, not the evidence.
   - (c) adds a second place where evidence lives: generic, beside the owning modules' own.
     That is wider than Slice 2 and breaks the pattern every other approvable type follows.
4. **The FD-1200 class — required, each red first** (the 11:04:57 BST entry's conditions):
   - **No approval without its pinned evidence.** A deployment request whose row lacks either
     floor item, or is deliberately stripped of it by a test fixture, cannot reach `approved`.
     The submission is refused, and a decision on such a row is refused too. With the check
     removed, the fixture is approved, and the test fails.
   - **The evidence is immutable after submission** (FR-356, `00` FR-4). No code path
     updates the row's evidence or pins once the request exists. An attempted update through
     the module's functions is refused, and a test proves it. A migration adds no
     `ON UPDATE` path, and if the leaf plan chooses a database trigger, its test is also red
     first.
   - **Only the single decision path writes `approved`: a database trigger on every
     approval-capable table** (sub-item 2), **carried by WK-674 Slice 2a, which lands
     before Slice 2** (sub-item 9). *(Restated a fourth time: the runtime-guard version below was moved to a
     trigger by the maintainer's 11:44:15 BST entry, and its test database rule and
     sequencing come from the entry "11:45:55 BST — the trigger pre-checks (one is
     critical); my lean on splitting S2". Restated a third time, and superseding the static
     AST-attribution versions at `fa49e06c`, `324ea165` and `327e1179`, on the maintainer's
     entry "11:32:49 BST — three rulings: …; #971 A.4 method; …", item 2. auditor-close1255
     implemented the static version and ran it. Attribution failed closed on 16 of 23
     assignments, including the sanctioned `platform/approvals.py:416`. A runtime guard
     removes the attribution problem, because the ORM knows each row's class and its actual
     value.)*
     1. **The population is derived from approval-status enums** (the 11:21:51 BST entry).
        - Every approval-capable table declares its status column's vocabulary, the
          `StrEnum` its values come from, as column metadata (for example
          `info={"status_vocabulary": RatingVersionStatus}`).
        - The population is every mapped class whose declared vocabulary has an `APPROVED`
          member. At `9f63d0fe`: `ApprovalStatus` (`model_schema/approvals.py:41`),
          `MetricStatus` (`metrics.py:48`), `ModelStatus` (`modelling.py:1975`),
          `ObjectiveStatus` (`objectives.py:137`), `PerilStructureStatus` (`perils.py:94`)
          and `RatingVersionStatus` (`rating.py:31`), and the tables they govern.
        - Slice 2a also declares the vocabulary of `validation_rules` and
          `validation_rule_sets`, through a `StrEnum` of their string constants
          (`validation_rules.py:65`), since they have no enum. Slice 2 declares the
          Deployment Request table's.
        - **Every mapped `status` column declares itself, and none escapes by omission**
          (fail-closed; corrected on auditor-close1255's M1). In its own column metadata, each
          column carries **either** its vocabulary `StrEnum` **or** an explicit non-approval
          marker (for example `info={"approval_capable": False}`). A status column with
          neither fails. The non-approval marker fits `jobs`, `scoring_traces`,
          `ingestion_runs`, `reference_table_versions` (string constants,
          `platform/reference.py:57`), `dataset_versions` and `outbox`.
        - **Independent cross-checks refuse a wrong marker.** A column may **not** carry the
          non-approval marker, and must declare an enum with `APPROVED`, if any one of these
          holds, each derived from the models and code, never from a list:
          - its CHECK constraint names `'approved'`;
          - its `default=` or `server_default=` is `"approved"`;
          - its table is written by an `apply_approval_decision` that
            `_carry_to_the_artifact` drives, or it is `approval_requests`.
        - At `9f63d0fe`, auditor-close1255 measured that union at 8 tables: `custom_metrics`,
          `custom_objectives`, `models`, `peril_structures`, `validation_rules`,
          `rating_versions`, `approval_requests` and `validation_rule_sets`. **So
          `peril_structures` is guarded**, because its CHECK allows `approved`. That is the
          hazard of the perils finding. A future table that declares nothing fails, and one
          that declares the marker wrongly fails a cross-check.
          *(This supersedes the previous head's scoping, which required declarations only of
          tables with an `apply_approval_decision` module and so left `peril_structures`
          silently unguarded.)*
     2. **The primary guard is a database trigger** (the maintainer's entry "11:44:15 BST —
        #971 A.4: five ORM-guard bypasses → steer to a DATABASE trigger as the primary guard",
        and this ruling's own reading of auditor-close1255's scratch build of `80afeb40`).
        That build's ORM guard refused the explicit, default, attribute, ORM-bulk and ORM
        `pg_insert` writes. But five approved writes got past it: a Core `update()` on the
        `Table` object; raw `text()` SQL; `bulk_update_mappings`; a bulk update with a
        non-literal value (`func.lower("APPROVED")`); and an insert on the then-undeclared
        `peril_structures`. A list of forbidden write forms can never be complete, and a
        trigger sees them all.
        - **Where it is installed:** one PL/pgSQL function, installed as a
          `BEFORE INSERT OR UPDATE OF status … FOR EACH ROW` trigger on each of the 8
          existing approval tables. These are the set item 1 derives: the 7 artifact
          tables `custom_metrics`, `custom_objectives`, `models`, `peril_structures`,
          `validation_rules`, `rating_versions` and `validation_rule_sets`, plus
          `approval_requests` itself. (The maintainer's 11:45:55 BST entry says "7 existing
          approval tables"; this ruling reads that as the artifact tables, with
          `approval_requests` as the eighth, because its `status` takes `approved` from
          `decide` at `:416`.) **`deployment_requests`** gets the same trigger in the Slice 2
          migration that creates it (sub-item 9).
        - **What it refuses: an `approved` row without its evidence** (the maintainer's
          entry "11:55:31 BST — #971 trigger at ed879f7b: T1–T3 agreed; the forgeable-flag
          residual gets a steer toward an evidence-based condition", adopted). It checks
          whenever `NEW.status = 'approved'` on an INSERT, or on an UPDATE that changes
          `status` or any column the artifact ref is built from. What it then requires
          depends on the table:
          - **On the 7 artifact tables, evidence.** An `approval_requests` row must exist
            with `workspace_id = NEW.workspace_id`, `status = 'approved'` and `artifact_ref`
            equal to this row's ref. That row may be committed, or written earlier in the
            same transaction, as `decide` writes it at `:416` and flushes it at `:419`
            before the carry. The flag alone never satisfies this. On the 5 tables with no
            allowance (`models`, `custom_metrics`, `custom_objectives`, `peril_structures`,
            `rating_versions`), the auditor's forgery,
            `set_config('app.approval_decision', 'on', true)` followed by an approved write,
            is refused. Forging now needs a forged, decided request.
          - **On `validation_rules` and `validation_rule_sets`, evidence or the flag.** Every
            allowance site of sub-item 5 writes one of these two tables, and no other. The
            flag is accepted only on the tables whose trigger names it (next bullet), so the
            allowance is confined to those two tables. When the last allowance site on a
            table goes, a migration removes the table's flag argument. That is shrink-only.
          - **On `approval_requests` itself, the flag.** Its transition to `approved` keeps
            the flag, behind `decide`'s existing guards: separation of duties
            (`SUBMITTER_CANNOT_APPROVE` `:330`, `AUTHOR_CANNOT_APPROVE` `:351`), the one
            decision per approver (`DUPLICATE_APPROVER` `:407`,
            `uq_approval_decisions_one_each`) and the quorum count (`:540-554`). A trigger
            that also counted `approval_decisions` against `approvers_required` would make a
            forged request need forged decision rows too. That was considered, and it is
            not required (the maintainer's 12:06:53 BST entry, sub-item 4).
          - **How the trigger derives the ref: one function, with per-table trigger
            arguments.** The stored ref is `str(ArtifactRef)`, `{type}:{slug}@{version}`
            (`refs.py:75`; `approvals.submit` stores it at `approvals.py:247`). Each of the
            7 tables has `workspace_id` and `version`. The slug column is `slug`, except on
            `models`, where it is `model_family_slug` (`modelling.py:1152-1154`). Each
            `CREATE TRIGGER` passes `(artifact type, slug column[, 'flag'])` as `TG_ARGV`,
            and the function builds
            `TG_ARGV[0] || ':' || (to_jsonb(NEW) ->> TG_ARGV[1]) || '@' || NEW.version`.
            The trigger's `UPDATE OF` list is `status, workspace_id, <slug column>,
            version`, so re-pointing an approved row at another ref is re-checked.
            - Rejected: a generated `artifact_ref` column on each table, which is 7 schema
              changes and 7 copies of the format;
            - rejected: 7 per-table functions, which are 7 copies of one rule.
          - **The ref format now has a second writer, in SQL.** `CLAUDE.md` §2's rule on
            shapes defined twice applies, so a test pins the two together. For each of the 7
            tables, it inserts a row and asserts that the trigger's composed ref equals
            `str(ArtifactRef(type=…, slug=…, version=…))` for that row. It is red first on a
            planted `'/'` separator.

          Its SQLSTATE maps to one named refusal in the platform's error translation.
          - **`OF status` narrows only the UPDATE event.** Every INSERT fires the trigger,
            so an insert that relies on a column default is caught.
          - **The comparison is `IS DISTINCT FROM 'on'`, never `= ''` or `IS NULL`.** Once a
            session has set the flag, it reads `''`, not NULL, after the transaction ends.
          - **Verified** on PostgreSQL 16.15 (the compose server), with this function on a
            scratch temp table, `status text DEFAULT 'approved'`:
            - an insert relying on the default, without the flag, was refused;
            - an update of another column was allowed;
            - `SET status = lower('APPROVED')` was refused;
            - with `set_config('app.approval_decision', 'on', true)` the default insert was
              allowed;
            - after the transaction's rollback, the setting read `''`.
        - **It is an Alembic migration in Slice 2a.** The migrations directory is a registry,
          append-only. There is a precedent: `61981ea8f274_custom_metrics.py` already
          installs PL/pgSQL triggers (`:63`, `:177`).
        - **How defaults reach it (verified):** SQLAlchemy writes a Python-side `default=`
          such as `models.py:1195` into the INSERT's values, and Postgres fills a
          `server_default` into the row before a `BEFORE ROW` trigger runs. Either way,
          `NEW.status` is `'approved'` when the trigger fires.
        - **Tests see it:** sub-item 10 is the rule.
        - **Secondary, not required:** an ORM `before_flush` hook may stay for an earlier,
          friendlier error, and it is not the guard. The static checks of item 3 are the
          secondary layer.
     3. **The decision path sets the flag with `SET LOCAL`, and the flag spans the write and
        its flush.** One context manager, `approval_decision()`, in `platform/approvals.py`,
        executes `SET LOCAL app.approval_decision = 'on'` on the session's transaction
        (`set_config(…, true)` is the same). It also sets a `ContextVar` for the static
        checks.
        - **The transaction spans the unit of work (verified).** `Database.unit_of_work`
          (`backend/src/app/db/session.py`) is one `session.begin()` that "commits once on
          clean exit". So a transaction-local setting covers `decide`, the carry and both
          flushes in the decide route (`api/approvals.py:250-260`), which closes M2. It
          cannot leak to another transaction on a pooled connection.
        - **The block resets the flag on exit** (corrected on auditor-close1255's W1 and
          W2). `SET LOCAL` lasts until the end of the **transaction**, not the end of the
          block, and leaving the `ContextVar` does not undo it. The auditor showed that
          without a reset, an unrelated approved write **after** the block, in the same unit
          of work, was allowed (W1). So `approval_decision()` flushes the session and then,
          in a `finally`, executes `SET LOCAL app.approval_decision = 'off'`. With that
          reset the same write was refused (W2). The flush comes before the reset, so the
          block's own pending write meets the trigger while the flag is on. An **ORM**
          write left unflushed at exit (an attribute change still pending in the session)
          is flushed later under `'off'`, and is refused: it fails closed. A Core or raw
          `text()` statement executes immediately inside the block, so it is never
          buffered, and this case does not arise for it.
        - **The sanctioned decision path** enters the context in exactly two places:
          - `platform/approvals.decide`, from its assignment at `:416` through its flush at
            `:419`;
          - `api/approvals._carry_to_the_artifact` (`:488`), which the decide route
            (`:260`) and the withdraw route (`:293`) both call. Withdraw never produces
            `approved`, so this is harmless, and it is stated.
        - **Two static checks, by name:**
          - `approval_decision()` is entered nowhere in `backend/src` or `examples/` except
            those two places and the named allowance of item 5;
          - the literal `app.approval_decision` appears only in the decision module
            (`platform/approvals.py`, which defines `approval_decision()`) and in the
            guard's migration. It appears nowhere else in `backend/src`,
            `backend/migrations` or `examples/`. The allowance sites of sub-item 5 enter the
            context manager and never name the flag.
     4. **What covers what, and the one residual.**
        - A test queries `pg_trigger` and fails if any table in item 1's derived set lacks
          the guard trigger. A new approval table cannot ship unguarded.
        - **Alembic data migrations** are covered by the trigger itself. A data migration
          that must write `approved` has to set the flag in its SQL, which the second static
          check refuses unless it is reviewed. At every slice's close, the auditor also runs
          `git diff --name-only <base>..<head> -- backend/migrations/versions` and reads each
          new migration. That is an explicit review item.
        - **The residual:** a database superuser, or a role that can drop the trigger, can
          bypass it. That is administration outside the application's write paths, and it is
          named, not hidden. The same covers `session_replication_role = replica`, which
          suspends every user trigger and needs superuser. The test teardown uses it on
          purpose (`backend/tests/conftest_db.py:352`), as do the audit tamper tests
          (`test_audit.py:168`, `:194`; `test_api_audit.py:153`). **A third static check:**
          no SQL string in `backend/src` or `examples/` sets it. The one mention in
          `backend/src` at this tree, `platform/objectives.py:108`, is docstring prose.
        - **The residual: the flag is not a capability** (auditor-close1255's advisory).
          Any code on the application's connection can run
          `SELECT set_config('app.approval_decision', 'on', true)`. The auditor ran that
          and then an approved write, and the write succeeded against the flag-only
          trigger. Under the evidence condition of sub-item 2:
          - on the 5 evidence-only tables that forgery is refused;
          - what the flag still opens is `approval_requests`' own transition, and the two
            validation tables while they hold an allowance.

          **Accepted as a residual by the maintainer**, in the entry "12:06:53 BST — #971
          evidence-based trigger: the named residual is ACCEPTED". Arbitrary SQL on the
          application's connection already means full control of the data, so no
          trigger-side count of `approval_decisions` is required.
          Forging an approved artifact on the 5 tables therefore takes a forged request:
          the flag, then an approved `approval_requests` row naming the artifact, then the
          write. On the validation tables it takes the flag alone. The static literal scan
          is the guard on the flag, and a literal assembled at run time (concatenated, or
          built in an f-string) evades it. That is named here, beside the superuser and
          `session_replication_role` residuals, not hidden. The
          scan does catch a session-level `SET` (without `LOCAL`, or `set_config(…, false)`),
          which would leak across the pool. The one permitted site uses the
          transaction-local form, and a red-first case shows that the next transaction on
          the same pooled connection does not read `'on'`.
     5. **The allowance: named call sites that may set the flag outside the decision path,
        pinned as a literal and shrink-only.** Every table keeps its trigger. The allowance
        is by **site**, not by table, so a new writer on a validation table is still refused.
        - **Temporary, removed red first by the WK-1178 fix slice** (the finding filed under
          the maintainer's 11:14:48 BST DEFECT entry, in prose until minted):
          - `validation_rules.approve_rule` (`:395`, writing at `:423`);
          - `validation_rules.replace_rule_set` (`:538`, `status=APPROVED` at `:643`; its
            table's default is `models.py:1195`). It waits on that finding's triage. If the
            triage finds rule sets legitimately ungoverned (`06:64`), it moves to the seed
            list below, with that spec citation.
        - **Legitimate seed writers**, kept while they are legitimate, and each re-read by
          that finding's triage:
          - `validation_rules.seed_builtin_rules` (`:89`, `status=APPROVED` at `:154`), the
            platform-supplied built-ins;
          - the demo seed `examples/fremtpl2/seed.py:441`.

          Each enters `approval_decision()` around its write and flush.
     6. **Test fixtures.** 17 backend test files match
        `git grep -l -E 'status\s*=\s*"approved"|Status\.APPROVED|status=APPROVED' 9f63d0fe --
        backend/tests`. That is an upper bound on the direct approved writes, since some
        matches only compare. **Declared Slice 2a work:** each goes through the real
        submit, decide and carry path, or through a helper defined under `backend/tests/`
        only.
        - **On the 5 evidence-only tables, the helper writes the evidence as well** (F-1 of
          auditor-close1255's audit of `3de69560`). Entering `approval_decision()` is not
          enough, because the flag does not satisfy those tables. Inside the context, the
          helper writes an `approval_requests` row with `status = 'approved'`, the row's
          `workspace_id` and its `artifact_ref`, which is `str(ArtifactRef(...))` for the
          artifact. It then writes the artifact.
        - **On the two validation tables**, entering the context is enough while their
          allowance stands.

        The static checks exempt `backend/tests/` and nothing else.
     7. **Red first, against a database migrated to head:**
        - **each of the five bypass forms** of item 2 is refused on a population table:
          Core `update()` on the `Table`, raw `text()`, `bulk_update_mappings`, a non-literal
          value, and a `peril_structures` insert;
        - **the ORM paths** are refused too: an explicit insert, an insert relying on
          `default="approved"`, an attribute update, an ORM bulk `update()`, and
          `pg_insert`;
        - **for every table** in item 1's derived set, a direct approved write outside the
          context is refused. Slice 2 adds the `deployment_requests` plant;
        - with the trigger dropped in a scratch database, those writes succeed, and the test
          fails;
        - a population table with no trigger fails the `pg_trigger` test;
        - a third `approval_decision()` site, or a stray `app.approval_decision` literal,
          fails its static check;
        - **evidence:**
          - on each of the 5 evidence-only tables, `set_config('app.approval_decision',
            'on', true)` followed by an approved write is refused;
          - so is an approved write whose only approved request names another version of
            the same slug, another workspace's ref, or a request still in `review`;
          - re-pointing an approved row's `version` to a ref with no approved request is
            refused;
          - with the evidence condition replaced by the flag check, the first of these
            cases fails;
        - **after the block:** an approved write made after `approval_decision()` exits,
          in the same unit of work, is refused. Without the exit reset, this case fails;
        - **unflushed at exit:** inside the block, an ORM attribute change sets
          `status = 'approved'` with no flush. The block's own flush is suppressed for
          this plant, and the change is flushed after exit. That flush is refused. The
          plant is an attribute change, never a Core or `text()` statement, which would
          execute at once (auditor-close1255's F5);
        - **no leak:** the next transaction on the same pooled connection reads the flag
          as not `'on'`;
        - **positive controls:** the decide-and-carry path approves a request and its
          artifact; each allowance site writes successfully; and removing an allowance entry
          makes its site's write refused.
     8. **Zero writers.** `peril_structures` has no sanctioned writer of `approved` today, and
        its trigger refuses any attempt outside the decision path. Whether its `approved`
        state should be reachable at all is the perils finding's question, routed by the
        lead.
     9. **Sequencing: the guard is WK-674 Slice 2a, which lands before Slice 2** (the
        maintainer accepted the split in the 11:48:28 BST entry, after the lean in the
        11:45:55 BST entry).
        - **Slice 2a** carries sub-items 1–8 over the 8 existing tables: the
          vocabulary declarations, the trigger migration, `approval_decision()`, the static
          checks, the allowance literal, the fixture conversions of sub-item 6 and the red
          first cases of sub-item 7. It lands before both the WK-1178 validation fix slice
          and Slice 2.
        - **The WK-1178 validation fix slice depends on Slice 2a.** That slice removes the
          temporary allowance entries of sub-item 5, and a removal is only red first once
          the trigger exists to refuse the write.
        - **Slice 2 carries the `deployment_requests` extension.** Its creating migration
          installs the same trigger function on the new table, as an evidence-only table
          with the arguments `('deployment', <its slug column>)` and no flag argument. The vocabulary of its `status` column joins
          item 1's derivation, so the `pg_trigger` test of sub-item 4 fails until the
          trigger is present. The deploy-side plant joins sub-item 7.
        - Slice 2a's leaf plan and its place in the dispatch order are the planner's to
          write and the lead's to dispatch. This ruling fixes its scope and its dependency
          order.
    10. **The test database must carry the trigger, and the suite proves it rather than
        assuming it** (the maintainer's CRITICAL pre-check, 11:45:55 BST entry).
        - **What builds the test schema today (verified at `9f63d0fe`):**
          - nothing calls `create_all`: `git grep -n -l 'create_all\|metadata.create' --
            backend examples scripts` prints nothing;
          - CI runs `uv run alembic upgrade head` before the suite
            (`.github/workflows/python.yml:294`);
          - locally, the per-worktree database is `createdb -T gipricing` then
            `alembic upgrade head` (`backend/tests/conftest_db.py:124-137`, the refusal
            message that names the procedure).
        - **The gap:** the `database` fixture (`conftest_db.py:171-200`) checks only that
          `alembic_version` has a row (`:192-197`), and never that the database is at head.
          A per-worktree database last migrated before the guard's migration passes that
          check with no trigger. Sub-item 7's refusal cases would then fail loudly. But
          every other test's direct approved write, the population sub-item 6 must convert,
          would pass silently, so the conversion goes unproven.
        - **The rule:**
          - the `pg_trigger` test of sub-item 4 runs against `test_database_url()`, the
            database the suite runs on. It **fails, never skips**, when any table in item
            1's derived set lacks the guard trigger. **It does not use the `database`
            fixture**, which skips on an unreachable database (`conftest_db.py:190`) and on
            an unmigrated one (`:192-197`). It opens its own connection to
            `test_database_url()` and asserts, so an unreachable or unmigrated database
            fails it (corrected on auditor-close1255's T3). At Slice 2a that set is the 8 existing
            tables, and at Slice 2 it adds `deployment_requests`;
          - sub-item 7's red-first plants run on that same database;
          - the fixtures stay on `alembic upgrade head`. A fixture that ever builds a
            schema some other way must install the trigger DDL by **importing it from the
            guard's migration module**, never a copy. A copy is a second definition that
            can drift (`CLAUDE.md` §2's rule on shapes, applied to DDL);
          - **red first:** against a scratch database built from the migration before the
            guard's, the `pg_trigger` test fails.
        - A head check in the `database` fixture (comparing `alembic_version` to the script
          head) is a sound addition for Slice 2a. It is not required, because the
          `pg_trigger` test already fails on exactly that database.
5. **The deploy route executes only an approved request.** For a target whose deployments are
   approval-gated, `POST /api/v1/environments/{env}/deployments` names an **approved**
   Deployment Request and re-evaluates FR-429's one predicate from the request's **pinned**
   evidence. It never re-reads a changeable source. A target with no `deployment` policy
   entry needs no request. For it, the predicate reads the predecessor's successful
   Deployment directly, and no skip is possible (the OQ-1234 ruling, item 1).

6. **A3 — the approval policy must not resolve through a renamable name** (auditor-close1255's
   advisory, ruled on the maintainer's 11:14:48 BST steer).
   - **The hazard:** `ApprovalPolicyEntry.environment` is a string
     (`packages/model-schema/src/model_schema/approvals.py:119-121`), `entry_for` matches on
     it, and `ApprovalRequestRow.environment` is `String(32)` (`models.py:627`). `06` §4.1
     gives `admin:manage_environments` the Environment's "create, rename, retire". A rename
     would make the `prod` entry resolve to nothing, and under item 5 a target with no
     `deployment` entry needs no request. **A rename would ungate `prod` silently.**
   - **Ruled: policy resolution keys on an identity that a rename cannot change.** Every
     Environment has an **immutable `slug`** and a mutable display `name`. **The split, and the
     slug's immutability, are this ruling's own decision**, carried into `07` §4 by Slice 2's
     spec-first commit. `00` ID-1 (`00-overview.md:279`) gives only that a slug is "unique
     within its parent scope", and `07` FR-428 gives an Environment a name but no slug.
     *(Recast on auditor-close1255's nit, which found that this item first cited ID-1 for
     the immutability.)* The
     approval policy's `environment`, `ApprovalRequestRow.environment`, the deploy route's
     `{env}` and every Environment reference name the **slug**. `07` FR-428's rename changes
     the `name` only. **A change of slug is refused**, because it would change which policy
     entry resolves. This is the maintainer's steer, keying by identity and refusing a
     resolution-changing rename, met by one mechanism. The slug is also what the item 1
     reference and the OQ-1234 ruling's "environment-qualified" entry mean.
   - **The policy may not name an Environment that does not exist.** `set_policy` refuses an
     entry whose `environment` is not an existing Environment's slug. Otherwise a typo
     (`prd`) would ungate the real target as silently as a rename. **Environments are
     deployment-wide, not per workspace.** `07` §4.2's Environment has no workspace field;
     a Service Account's key lists environment names with no workspace
     (`models.py:397-398`); and ADR-710 makes the deployment the tenant boundary
     (`backend/src/app/api/deps.py:26-27`). *(Worded on the leaf plan's rev 4 question. This
     item first said "the workspace's Environments", which was loose wording and not a
     design difference.)*
   - **A credential names only existing Environments.** A Service Account's `environments`
     is a free `list[str]` (`backend/src/app/api/service_accounts.py:63`), and a key is minted
     from `environments[0]` (`:180` at creation, `:246` at rotation). Nothing checks either
     against an Environment, because at this tree there are none to check against. Once
     Slice 2 creates Environment records, the rule is:
     - each name in `environments` must be an existing Environment's slug at creation and at
       rotation, or the request is refused with `VALIDATION_FAILED` 422 naming it;
     - retiring an Environment that an unrevoked Service Account key names is refused with
       409, like one a policy entry names, until the key is revoked or its environments are
       narrowed.

     **Carried by Slice 2**, which creates the Environment records and their retire route.
     `Caller.environment` then always names a real, unrenamable Environment. **Red first:**
     issuing a key for `prd` is refused, and retiring `uat` while a live key names it is
     refused.
   - **Two leaf-plan choices, both consistent with this ruling** (rev 4, `4bde1cfb`):
     - the Deployment Request's slug is its target Environment's immutable slug
       (`deployment:prod@3`). That meets item A.1's constraint, because that slug cannot
       be renamed;
     - retiring an Environment that a policy entry names is refused with 409. Item A.6
       left retirement to the plan, and this is a sound answer.
   - **This item disposes of the leaf plan's DP-S2-5** (A3: Environment rename versus the
     policy key), which planner-924 opened for this ruling. The planner may close it citing
     this item.
   - **Red first:** rename `prod`'s display name, and a deploy to it still requires its
     approved Deployment Request. A request to change `prod`'s slug is refused. A policy
     naming `prd` is refused by `set_policy`. With resolution keyed on the display name,
     the first test fails.

### B. DP-S2-3 — option (a): `ScopeType.ENVIRONMENT`, checked with the Environment as the resource

1. **`ScopeType` gains `ENVIRONMENT`**, with `scope_id` the Environment's id. A workspace-wide
   Deployer still covers every environment, which is `_covers`' uniform rule for every scope
   (`rbac.py:207-208`). A workspace-wide assignment remains "a deliberate choice"
   (`ScopeType`'s docstring). This meets `CR-1212` item 4 and the planned case: a Deployer
   whose grant names only `uat` is refused on `prod`.
2. **The deploy route checks in the handler, with the target Environment as the resource.**
   It calls `rbac.require_permission(..., permission=Permission.DEPLOYMENT_PROMOTE,
   resource=ResourceRef(ScopeType.ENVIRONMENT, <environment id>))`. It **must not** rely on a
   bare `requires(Permission.DEPLOYMENT_PROMOTE)` dependency. With no resource, `_covers`
   admits only a workspace-wide grant (the table above), so a `uat`-only Deployer would be
   refused in `uat` too. (This handler check is a `permission=` site, so the permission-parity
   check's AST leg counts it, per #942's ruling.)
3. **Why not (b) or (c).**
   - (b) would honour `deployment:promote` only through an environment-scoped grant. That
     makes one permission an exception to `_covers`' rule for every other scope, and strands
     every existing workspace-wide Deployer. `CR-1212` item 4 asks that the permission *can*
     be scoped to named environments, not that it *must* be.
   - (c) puts a list of environments on one assignment. The assignment's shape is one
     `scope_type` and one `scope_id`, and several assignments already express several
     environments.
4. **The spec change, in Slice 2's spec-first commit:** `06` FR-345's list of scopes gains
   "or Environments", dated, citing this record and `CR-1212` item 4. `06` §4.1's assignment
   example may show an `environments` scope. `ScopeType` is a `model-schema` enum, so the
   contract is regenerated.
5. **Acceptance, red first:**
   - a Deployer assigned only to `uat` deploys in `uat` and is refused on `prod`;
   - a workspace-wide Deployer deploys to both;
   - with the handler's resource argument removed, the `uat`-only Deployer is refused in
     `uat` as well, and the test fails;
   - a Service Account is still refused (FR-347).

### C. A dated amendment to the OQ-1234 ruling (#935, working id 9901, minted on its branch as the next ruling id)

**This record amends it; it does not reinterpret it** (the 11:04:57 BST entry's condition).
That ruling's item 3 says the reason for a skip "is the **predecessor-deployment evidence
item** (for `prod`, the `uat_deployment` item) … **pinned at submission**, as every evidence
item is (FR-352, FR-356)". It also says "the `03` Deployment record references the approval
that carries it". It assumed an evidence item held **on the approval request**. **No such
home exists:** `ApprovalRequestRow` has no evidence column, and no `ArtifactRef` can name a
deployment (the table above).

**Amended 2026-09-30:** the predecessor-deployment evidence item, including a skip record
and its reason, is pinned on the **Deployment Request** row of item A. That row is the
subject of the `deployment` approval request. The rest of that ruling stands unchanged: where
the permission lives, the one predicate reading only its arguments, and the reason always
required.

**The form, as the entry asked "say which": an item in this record**, with `corrects:`
naming the OQ-1234 ruling. That ruling is not yet on `main` at this record's tree, so its id
would not resolve here. **At this record's mint turn, the lead sets `corrects:` to that
ruling's minted id**, and appends this record's id to that ruling's `corrected_by:`. Check 34
permits appending there on a written-once record, and requires the pair to point at each
other.

## What it obliges

- **This commit:** this record only. The spec and contract changes are Slice 2's spec-first
  step (A.1, B.4).
- **WK-674 Slice 2a (before Slice 2 and the WK-1178 validation fix slice):** A.4's
  database trigger over the 8 existing approval tables, with its sub-items 1–8 and 10.
- **WK-674 Slice 2 (the leaf plan, PL working id 9920):**
  - the Deployment Request row and its reference type (A.1);
  - the pinned evidence and its checks (A.2);
  - the FD-1200-class acceptance (A.4), including the `deployment_requests` extension of
    Slice 2a's trigger (A.4 sub-item 9), and the deploy route's use of the request (A.5);
  - `ScopeType.ENVIRONMENT` and the handler's resource check (B), with the `06` FR-345
    amendment and the contract regeneration.
- **The lead:** at the mint turn, the `corrects:`/`corrected_by:` pair of item C. And
  planner-924 re-reads its draft against items A and B.

## Acceptance — the violation that must become detectable

The violations: **a deployment approved without its pinned evidence, evidence changed after
submission, a second writer of `approved`, or a Deployer acting outside the Environments its
grant names.** In WK-674 Slice 2, or Slice 2a for the trigger over the existing tables,
each is shown failing on deliberately broken input (`CLAUDE.md` §13):
- item A.4's cases: approval without pinned evidence; an evidence update after submission;
  and item A.4's database trigger, red on each case of its sub-item 7, and green on the live
  tree only through the pinned allowance of its sub-item 5, with its `pg_trigger` test
  failing, never skipping, on a test database that lacks the trigger (sub-item 10);
- item A.5: a deploy to an approval-gated target naming no approved Deployment Request is
  refused. A request whose pinned predecessor item no longer satisfies FR-429's predicate is
  refused at the route;
- item A.6's three cases: a display rename keeps `prod` gated; a slug change is refused; a
  policy naming a non-existent environment is refused; a Service Account key for `prd` is
  refused; retiring an Environment a live key names is refused;
- item B.5's four cases.
