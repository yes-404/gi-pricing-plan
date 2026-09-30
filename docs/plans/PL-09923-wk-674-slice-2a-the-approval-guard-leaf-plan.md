---
id: PL-9923
family: plan
kind: leaf
title: WK-674 Slice 2a — The approval guard (only the decision path writes approved): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: daa7f5f8d6f0ff80dee7dfccf8ca18309d626816
phase: P2
work: WK-674
slice: SL-9922
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, RL-1263, FD-1218]
---

# WK-674 Slice 2a — The approval guard: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `python-package` and `python-test` (every task) and `dev-commands` (the migration, the gate and the gate slot), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make "`approved`" unreachable except through the approval decision path, on **every**
approval-capable table, **enforced by the database**, so that no write path — ORM, Core,
raw SQL, bulk, a non-literal value, or a table nothing approves yet — can set it on its own.

**Architecture.** One PL/pgSQL function, installed with per-table arguments as a
`BEFORE INSERT OR UPDATE OF status, workspace_id, <slug column>, version … FOR EACH ROW`
trigger on each of the 8 existing approval tables, refuses an `approved` row **without its
evidence**: on the 5 evidence-only artifact tables, a matching `approved` `approval_requests`
row must exist; on the two validation tables, evidence **or** the decision flag; on
`approval_requests` itself, the flag. One context
manager, `approval_decision()`, in `backend/src/app/platform/approvals.py`, executes
`SET LOCAL app.approval_decision = 'on'` in the session's transaction and, on exit, **flushes
and then resets it to `'off'`** in a `finally` (T2, below). It is entered at exactly two sanctioned sites and a named,
shrink-only list of allowance sites. The trigger ships as one Alembic revision; an ORM hook
is optional and secondary; three static checks back it. WK-674 Slice 2 installs the same
trigger on `deployment_requests`, evidence-only, in the migration that creates that table.

**Tech Stack:** PostgreSQL 16 (PL/pgSQL), Alembic, SQLAlchemy 2.x async, pytest. No new
dependency: no `uv.lock` or `pyproject.toml` change.

**Spec:**
- [`../specs/06-governance.md`](../specs/06-governance.md) §3.2 — **FR-351** (`06:92`, the
  uniform lifecycle), **FR-354** (`06:95`, the approver count a direct write bypasses),
  **FR-356** (`06:97`, pinned approvals); `06:22` ("approved" means the same thing for every
  governed artifact).
- **The ruling this slice executes: #971** (working id 9906), item A.4, sub-items **1–8 and
  10**, read at head `3de69560643b2abc8d20afc923416a4ef66104a1` (the **evidence-based** trigger form, which adopts the
  maintainer's 11:55:31 BST steer and carries T2 and T3). **It is still under audit by
  auditor-close1255**; cited by PR number until it mints. Its sub-item 9 sets this
  slice's scope and order.

**What this plan implements.** WK-674's map plan **PL-1237**, Task 2, as **split** by the
maintainer (below): the approval-guard half of Slice 2, landing **before** Slice 2. The
slice row is **SL-9922** (working id), cut in this PR under `### WK-674` in
`docs/roadmap.md`.

## Status

**Draft**, filed 2026-09-30 against the tree above, under **working id 9923**; its slice
row under working id **9922**. Both are minted at this PR's merge turn.

**The split, as a dated delta to the map plan** *(2026-09-30)*. The maintainer's entry headed
`2026-09-30 11:48:28 BST — DECISION + ACCEPTANCE (maintainer by delegation): WK-674 S2 split, option (b), S2a = the approval guard`
(`~/gi-pricing-plan.local/channel/to-lead.md`) accepts it, in the line the entry gives for
the map plan, verbatim:

> 2026-09-30 — the maintainer (by delegation) accepts the split of WK-674 Slice 2 into S2a (the approval guard, first) and S2 (deployment), per #973's self-review option (b).

**Where the delta is recorded.** `PL-1237` is `active` and frozen: `document-ids.md` §1.5
lets a frozen file take only `status:`, `superseded_by:` and an append to `corrected_by:`,
and `scripts/audit-docs.py` check 34 refuses any other change to it. So the delta is
recorded, as `PL-1239` recorded its own map-plan deviation, **in the leaf plans**: here, and
in Slice 2's leaf plan (#973, working id 9920) by its own dated delta. `PL-1237` is not
edited.

**Activation needs, in order:**
1. **#971 audit-clean and minted.** At `3de69560643b2abc8d20afc923416a4ef66104a1` it carries T2, T3 and the evidence-based
   condition (the maintainer's steer headed
   `2026-09-30 11:55:31 BST — #971 trigger at ed879f7b: T1–T3 agreed; the forgeable-flag residual gets a steer toward an evidence-based condition`,
   adopted). If the audit changes it, this plan is aligned to the minted text by a dated
   delta.
2. **The lead's go.**

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means
the failing run is quoted in the ledger with its failing assert line **and the cause the
step predicts**; a failure for any other cause is a plan defect. "Red on broken input" means
the guard is green, then deliberately disabled, the test shown red with the predicted cause,
and the guard restored.

1. **Every `status` column declares itself; the guarded set is derived** (#971 A.4 sub-item
   1, on the maintainer's entry headed
   `2026-09-30 11:21:51 BST — status 11:25 noted; three rulings`). Each mapped `status`
   column under `app.db.models.Base` carries, in its column metadata, **either** its
   vocabulary `StrEnum` (`info={"status_vocabulary": <StrEnum>}`) **or** the explicit
   non-approval marker (`info={"approval_capable": False}`); a column with neither fails.
   The marker fits `jobs`, `scoring_traces`, `ingestion_runs`, `reference_table_versions`
   (`platform/reference.py:57`), `dataset_versions` and `outbox`. This slice declares a
   `StrEnum` of `backend/src/app/platform/validation_rules.py:65`'s constants for
   `validation_rules` and `validation_rule_sets`. **Independent cross-checks** refuse a
   wrong marker: a column may not carry the marker, and must declare an enum with
   `APPROVED`, if its CHECK names `'approved'`, or its `default=`/`server_default=` is
   `"approved"`, or its table is written by an `apply_approval_decision` that
   `_carry_to_the_artifact` drives, or it is `approval_requests`. **A fourth cross-check**
   (auditor-plans' caveat on M1: `rating_versions` enters only through the third), evaluated
   over every mapped class with a `status` column: the column may not carry the marker if it
   is **`Enum`-typed with an `APPROVED` member**, **or** has a CHECK constraint that
   **enumerates the status vocabulary** — `status IN (…)` or `status = ANY (ARRAY[…])` —
   **including `'approved'`**. *(Reworded on auditor-plans' V1: "any CHECK the value
   satisfies" was ill-defined, since `dataset_versions`' CHECK
   `status <> 'validated' OR validation_report_id IS NOT NULL` is satisfied by `'approved'`
   without naming it.)* **How a CHECK is read:** from the constraint's SQL text
   (`pg_get_constraintdef` on the migrated database, or the model's `CheckConstraint` text),
   a CHECK counts only if it constrains the `status` column by an `IN` list or `= ANY`
   array literal, and `'approved'` is one of its members; an implication, inequality or
   other predicate does not count. No table has an `Enum`-typed `status` with `APPROVED`
   today; the leg exists for the future. The derived set stays at 8. At `9f63d0fe` auditor-close1255 measured the
   set at 8 tables — `custom_metrics`, `custom_objectives`, `models`, `peril_structures`,
   `validation_rules`, `rating_versions`, `approval_requests`, `validation_rule_sets`; the
   executor re-derives it and quotes it. Red first: a planted status column with neither
   declaration fails; a planted wrong marker on a column whose CHECK names `'approved'`
   fails.
2. **The trigger, evidence-based** (sub-item 2, at `3de69560643b2abc8d20afc923416a4ef66104a1`). One PL/pgSQL function in one
   Alembic revision (precedent: `backend/migrations/versions/61981ea8f274_custom_metrics.py`
   installs PL/pgSQL triggers), installed on each table of item 1's set with `TG_ARGV`
   `(artifact type, slug column[, 'flag'])`. It checks whenever `NEW.status = 'approved'` on
   an INSERT, or on an UPDATE of `status`, `workspace_id`, the slug column or `version`
   (the `UPDATE OF` list), so re-pointing an approved row is re-checked. It requires:
   - **on the 5 evidence-only tables** (`models`, `custom_metrics`, `custom_objectives`,
     `peril_structures`, `rating_versions`): an `approval_requests` row with
     `workspace_id = NEW.workspace_id`, `status = 'approved'` and `artifact_ref` equal to the
     row's ref, committed or written earlier in the same transaction (`decide` writes it at
     `:416` and flushes at `:419`, before the carry). **The flag never satisfies it**;
   - **on `validation_rules` and `validation_rule_sets`**: evidence **or** the flag (their
     triggers carry the `'flag'` argument). Every allowance site of item 7 writes one of these
     two tables and no other. When a table's last allowance site goes, a migration removes its
     `'flag'` argument — shrink-only;
   - **on `approval_requests`**: the flag, behind `decide`'s existing guards
     (`SUBMITTER_CANNOT_APPROVE` `:330`, `AUTHOR_CANNOT_APPROVE` `:351`,
     `DUPLICATE_APPROVER` `:407` with `uq_approval_decisions_one_each`, and the quorum count
     `:540-554`).

   The function composes the ref as
   `TG_ARGV[0] || ':' || (to_jsonb(NEW) ->> TG_ARGV[1]) || '@' || NEW.version`; the slug
   column is `slug`, except `models`, where it is `model_family_slug`
   (`backend/src/app/platform/modelling.py:1152-1154`). The flag comparison is
   `IS DISTINCT FROM 'on'`, never `= ''` or `IS NULL`. Its SQLSTATE maps to one named
   refusal in the platform's error translation. **The ref pin:** the ref format now has a
   second writer, in SQL, so a test inserts a row on each of the 7 artifact tables and
   asserts the trigger's composed ref equals `str(ArtifactRef(type=…, slug=…, version=…))`
   (`packages/model-schema/src/model_schema/refs.py:75`; stored by `approvals.submit`,
   `backend/src/app/platform/approvals.py:247`). Red first on a planted `'/'` separator.
3. **Every write form is refused, red first, against a database migrated to head**
   (sub-item 7): the five bypasses of the ORM guard at `80afeb40` — a Core `update()` on the
   `Table`, raw `text()`, `bulk_update_mappings`, a non-literal value
   (`func.lower('APPROVED')`), and an insert on `peril_structures` — and the ORM paths — an
   explicit insert, an insert relying on `default="approved"` (`models.py:1195`), an
   attribute update, an ORM bulk `update()`, and `pg_insert`. **For every table in item 1's
   set**, a direct `approved` write outside the context is refused. **With the trigger
   dropped in a scratch database, each of those writes succeeds** and the test fails.
   `peril_structures` has no sanctioned writer and is guarded all the same (sub-item 8).
   **The evidence cases**, each red first, on each of the 5 evidence-only tables:
   `set_config('app.approval_decision', 'on', true)` followed by an approved write — a
   **forgery** — is refused; an approved write whose only approved request names **another
   version** of the same slug, **another workspace's** ref, or a request **still in
   `review`**, is refused; **re-pointing** an approved row's `version` to a ref with no
   approved request is refused; and with the evidence condition replaced by the flag check,
   the forgery case fails.
4. **The flag: `SET LOCAL`, spanning the write and its flush, and reset on exit.**
   - `approval_decision()` executes `SET LOCAL app.approval_decision = 'on'` (sub-item 3)
     and, on exit, **flushes the session and then**, in a `finally`, executes
     `SET LOCAL app.approval_decision = 'off'` — **T2** (auditor-close1255's W1 and W2:
     `SET LOCAL` lasts to the end of the transaction). The flush before the reset lets the
     block's own pending write meet the trigger while the flag is on; a write left unflushed
     is flushed later under `'off'` and refused, which fails closed — **red first with an ORM
     attribute change** (auditor-close1255 F-2): inside the block, set an artifact row's
     `status` to `approved` on the ORM object without flushing, patch the exit flush out,
     leave the block, then flush — the trigger refuses it. A raw statement cannot stand in
     for this case, because it is not buffered. Red first: an
     `approved` write **after** the block, in the same unit of work, is refused (without the
     reset, this case fails). **No leak:** the next transaction on the same pooled
     connection reads the flag as not `'on'`, red first against a session-level `SET`.
   - **Positive control (M2):** `decide` assigns at
     `backend/src/app/platform/approvals.py:416` and flushes at `:419`; the block covers
     both. `Database.unit_of_work` (`backend/src/app/db/session.py:69`) is one transaction
     for the decide route (`backend/src/app/api/approvals.py:250-260`), so the carry
     (`:488`) and its flush are inside it too. The control approves a request and its
     artifact and reads both back as `approved` from a new session. It also asserts **the
     flush order**: the `approval_requests` row reaches the database (the flush at `:419`)
     **before** the carry writes the artifact, since the evidence-only trigger reads that row;
     with the artifact write moved ahead of the flush, the control is refused. Red on broken input:
     with the block closed before `:419`, the trigger refuses the sanctioned write.
   - The sanctioned sites are exactly two: `decide` (`:416`–`:419`) and
     `_carry_to_the_artifact` (`:488`), which the decide route (`:260`) and the withdraw route
     (`:293`) both call; withdraw never produces `approved`, so its entry is harmless, and
     stated.
5. **Three static checks, by name** (sub-items 3–4), each red first on a planted
   violation: `approval_decision()` is entered nowhere in `backend/src` or `examples/`
   except the two sanctioned sites and item 7's allowance sites; the literal
   `app.approval_decision` appears **only** in `backend/src/app/platform/approvals.py` (which
   defines `approval_decision()`) and the guard's migration — nowhere else in `backend/src`,
   `backend/migrations` or `examples/`; the allowance sites enter the context manager and
   never name the flag; the scan also refuses a session-level `SET` (without `LOCAL`) or
   `set_config(…, false)`; and no SQL string in `backend/src` or `examples/` sets
   `session_replication_role` (the one mention in `backend/src`,
   `platform/objectives.py:108`, is docstring prose). `backend/tests/` is exempt, and
   nothing else. The check also fails any `create_task`, `gather` or `run_in_executor`
   lexically inside an `approval_decision()` block (auditor-plans' context hygiene).
6. **The test database carries the trigger, and the suite proves it** (sub-item 10, the
   maintainer's CRITICAL pre-check in the entry headed `2026-09-30 11:45:55 BST`).
   - **T3** (being added to #971): the `pg_trigger` presence test **connects to
     `test_database_url()` directly**, not through the `database` fixture, which **skips**
     on an unreachable database (`backend/tests/conftest_db.py:190`) or an unmigrated one
     (`:192-198`). It **fails, never skips**, when any table in item 1's set lacks the
     trigger, or the database is unreachable.
   - What builds the test schema today: nothing calls `create_all`
     (`git grep -n -l 'create_all\|metadata.create' -- backend examples scripts` prints
     nothing); CI runs `uv run alembic upgrade head` (`.github/workflows/python.yml:294`);
     locally the per-worktree database is `createdb -T gipricing` then `alembic upgrade head`
     (`conftest_db.py:124-137`). The `database` fixture checks only that `alembic_version`
     has a row (`:192-197`), never that it is at head (FD-1218 records the shared template
     holding a stale schema).
   - **Red first:** against a scratch database built from the migration **before** the
     guard's (one migration short of head), the `pg_trigger` test fails. The red-first
     plants of item 3 run on `test_database_url()`. Any fixture that ever builds a schema
     another way imports the trigger DDL **from the guard's migration module**, never a copy.
     A head check in the `database` fixture is added as a sound extra, not relied on.
   - The teardown's `session_replication_role = replica` (`conftest_db.py:352`) suspends
     triggers for its own transaction only; a test asserts the trigger is in force again
     after `empty_the_database()`.
7. **The allowance: by site, pinned as a literal, shrink-only** (sub-item 5). Every table
   keeps its trigger, so a **new** writer on a validation table is still refused. The named
   sites enter `approval_decision()` around their write and flush:
   - **temporary**, removed red first by the WK-1178 validation-rule fix slice (the finding
     under the maintainer's entry headed
     `2026-09-30 11:23:26 BST — DECISION: validation-rule approval bypass: HIGH (not CRITICAL); owner and order; two follow-ons`,
     cited as prose until it mints): `validation_rules.approve_rule` (`:395`, writing at
     `:423`); `validation_rules.replace_rule_set` (`:538`, `status=APPROVED` at `:643`; the
     table default `models.py:1195`), pending that finding's triage;
   - **legitimate seed writers**: `validation_rules.seed_builtin_rules` (`:89`,
     `status=APPROVED` at `:154`) and `examples/fremtpl2/seed.py:441`.

   Positive controls: each allowance site writes successfully, and **removing an entry makes
   its site's write refused**.
8. **Fixtures** (sub-item 6). The 17 backend test files matching
   `git grep -l -E 'status\s*=\s*"approved"|Status\.APPROVED|status=APPROVED' -- backend/tests`
   at the tree above (an upper bound; some only compare) move onto the decision path, or onto
   one helper under `backend/tests/`. **The helper creates the evidence, not just the flag** (auditor-close1255 F-1: the flag
   alone fails on the 5 evidence tables):
   for a row on an evidence-only table it inserts a matching `approved` `approval_requests`
   row (same workspace, `artifact_ref` = `str(ArtifactRef)` of the row) inside
   `approval_decision()`, and only then the artifact row; for a validation table or
   `approval_requests` the flag suffices. The files:
   `test_api_blobs.py`, `test_api_rate_tables.py`, `test_api_validation_rules.py`,
   `test_approvals.py`, `test_custom_metrics.py`, `test_custom_objectives.py`,
   `test_data_jobs.py`, `test_lineage.py`, `test_model_lifecycle.py`, `test_model_nfrs.py`,
   `test_paired_quantile_models.py`, `test_rate_tables_service.py`,
   `test_rating_version_compile.py`, `test_rating_versions.py`, `test_reference_pin.py`,
   `test_validation_reports.py`, `test_wf01_journey.py`.
9. **Evidence-based authorisation — adopted** (#971 at `3de69560643b2abc8d20afc923416a4ef66104a1`, on the maintainer's steer headed
   `2026-09-30 11:55:31 BST — #971 trigger at ed879f7b: T1–T3 agreed; the forgeable-flag residual gets a steer toward an evidence-based condition`).
   Carried by items 2 and 3. Forging an approved artifact on the 5 evidence-only tables now
   takes a forged, decided `approval_requests` row.
10. **The migration (FR-417).** One revision; `down_revision` is the head at the executor's
    tree (re-pointed at merge, RL-1263). `upgrade`, `downgrade -1`, `upgrade` exit 0, and
    after `downgrade -1` `pg_trigger` shows the trigger and function gone from **every**
    table of item 1's set. `uv run pytest tests/test_repository_invariants.py -q` passes.
    - **Migration tests at head and at head−1**, each red first: at head−1 (the revision
      before the guard's) a guarded write that head refuses succeeds, and the `pg_trigger`
      test fails; at head both hold. Each test names the revision it upgraded to.
11. **Stated limits, not hidden** (sub-item 4):
    - a database superuser, or a role able to drop the trigger, can bypass it; so can
      `session_replication_role = replica`, which needs superuser (used on purpose by the
      teardown and by the audit tamper tests, `test_audit.py:168`, `:194`;
      `test_api_audit.py:153`);
    - **the residual: the flag is not a capability** (auditor-close1255's advisory). Any code
      on the application's connection can run
      `SELECT set_config('app.approval_decision', 'on', true)`. Under the evidence
      condition that forgery is refused on the 5 evidence-only tables; what the flag still
      opens is `approval_requests`' own transition, and the two validation tables while they
      hold an allowance. The literal scan of item 5 guards the flag, and a literal assembled
      at run time (concatenated, or in an f-string) evades it — named, not hidden;
    - Alembic data migrations are covered by the trigger; one that must write `approved`
      sets the flag in SQL, which the second static check refuses unless reviewed. At the
      close the auditor runs
      `git diff --name-only <base>..<head> -- backend/migrations/versions` and reads each new
      migration.
12. **The gate, in a gate slot.** Every run of a whole test directory or package suite, the
    gate, or a multi-database sweep — by the executor or the auditor — runs inside a gate
    slot, `flock -w 1800 -E 99 /tmp/slots/gate-1 <cmd>` or `gate-2`, **with no `--`**, with
    `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2` set and `uptime`
    reported at each grant. Only named single test files or node ids are exempt (the
    maintainer's entries headed
    `2026-09-30 11:42:08 BST — two decisions: the escaped-pipe checker blindness → a LOW FD; box load → heavy audit runs take a gate slot`
    and `2026-09-30 11:43:28 BST — the slot rule, tightened: suite-level runs count`). The
    full two-half gate (`CLAUDE.md` §11) exits 0, with every rc, the `N passed` line and
    `HEAD` quoted against main's.
13. **Item 11** (`PL-1237` Tasks preamble): the maintainer's MERGE-ACK, naming the PR's full
    head SHA, recorded in the lead's channel file, never posted on the PR; and the slice's
    clean audit filed.

## Global Constraints

- **Only the decision path writes `approved`** (`06` FR-351, `06:22`); a write that bypasses
  it also bypasses the policy's approver count (FR-354).
- **The migration chain has exactly one head** (`07` FR-417).
- **Build ahead of the phase is forbidden** (`CLAUDE.md` §9): this slice adds no route and
  no spec requirement.
- **RL-1263.** This slice and Slice 2 are the **same Work, so they never build
  concurrently**: this slice takes lane A, Slice 2 follows it (the 11:48:28 entry). WK-690
  Slice 1 in lane B touches `packages/pricing-core`, `02`, `03` FR-244, the pyprojects and
  `uv.lock`, none of which this slice touches, so the two may overlap; the first overlap
  triggers the three-pair contention measurement (the maintainer's entry headed
  `2026-09-30 10:05:40 BST — ETA read (maintainer "check ETA"); two dispatch reminders`).

## Scope

### Requirement coverage

| Spec section | Id | This slice |
|---|---|---|
| `06` §3.2 | FR-351 | The enforcement half: "approved" is reachable only through the workflow, on every guarded table |
| `06` §3.2 | FR-354 | Indirectly: a direct write can no longer skip the approver count |
| `06` §3.2 | FR-356 | Unchanged; the guard does not alter pinning (item 9, if adopted, reads it) |

**Not in this slice:** the Deployment Request table, its trigger and its plant (Slice 2,
#971 sub-item 9); removing the temporary allowance (the WK-1178 fix slice); a new route of
any kind; Task 0A's authorisation sweep (Slice 2's first task, by the maintainer's 11:01:50
BST entry).

### Serialisation against other slices

| Path | This slice | Also touched by | Order |
|---|---|---|---|
| `backend/migrations/versions/` | one revision (the trigger) | WK-674 S2 (the trigger on `deployment_requests`), WK-1250 S1 | registry-exempt append; the later re-points `down_revision` |
| `backend/src/app/db/models.py` (every mapped `status` column) | the `status_vocabulary` / `approval_capable` metadata — an edit to existing classes | WK-674 S2 (appends only), any slice editing those classes | this slice first; S2's appends are exempt |
| `backend/src/app/db/session.py` | only if the optional ORM hook is kept | none found | not shared |
| `backend/src/app/platform/approvals.py` (`approval_decision()`; `decide` `:416`–`:419`) | the context manager and its first site | WK-674 S2 (`set_policy`), the validation-rule fix slice (`submit`/`decide`) | strictly in sequence: this slice first |
| `backend/src/app/api/approvals.py` (`_carry_to_the_artifact`, `:488`) | the second site | WK-674 S2 (the deployment branch), the validation-rule fix (the validation branch) | strictly in sequence: this slice first |
| `backend/src/app/platform/validation_rules.py` (`:65`, `:89`/`:154`, `:395`/`:423`, `:538`/`:643`) | the `StrEnum`; the allowance sites | the validation-rule fix slice | this slice first |
| `examples/fremtpl2/seed.py` (`:441`) | an allowance site | the validation-rule fix slice | this slice first |
| the 17 fixture files (Acceptance 8) | moved onto the decision path or the helper | any in-flight slice editing one | this slice first |
| `backend/tests/conftest_db.py` | the head check (sound extra); the trigger test connects directly | any slice editing it | serialises if another in-flight slice edits it |
| #977's §5.1 Permission column slice (WK-1178) | nothing: this slice touches no spec table | — | may run concurrently in the other lane (different Works, no shared file) |

**The validation-rule fix slice (WK-1178, HIGH) and its order — settled here.**
- **It needs this slice** (#971 sub-item 9: its allowance removal is red first only once the
  trigger exists).
- **It does not need Slice 2's content.** It adds a validation branch to
  `_carry_to_the_artifact` and routes rule approval through `submit`/`decide`; Slice 2 adds a
  deployment branch and a `set_policy` check. Neither reads the other.
- **But it may not overlap Slice 2**: both edit `_carry_to_the_artifact` and
  `platform/approvals.py`, so they run one after the other.
- **The order is decided: S2a → the validation-rule fix slice → S2** — the maintainer's entry
  headed
  `2026-09-30 11:56:33 BST — DECISIONS: slice order after the split; FR-384 confirmed; FR-383 and FR-385 owners`,
  which supersedes the "serialised after S2" clause of the 11:23:26 entry (written before the
  split). The fix is the owner of the finding filed as #978 (working id 9892). **Cost, stated:**
  Slice 2 starts later by the fix slice's full duration, since the two may not overlap.

### Premises re-derived at the tree above

| # | Premise | Evidence |
|---|---|---|
| a | `approved` is written outside the decision path | `validation_rules.py:423` (`approve_rule`), `:154` (`seed_builtin_rules`), `:643` (`replace_rule_set`); `models.py:1195` (`default="approved"`); `examples/fremtpl2/seed.py:441` |
| b | The decision path writes and flushes in `decide` | `backend/src/app/platform/approvals.py:416` (`row.status = new_status.value`), `:419` (`await session.flush()`) |
| c | The carry step drives each owning module, in the same unit of work | `backend/src/app/api/approvals.py:488`, carrying at `:499-517`; called at `:260` and `:293`; `Database.unit_of_work`, `backend/src/app/db/session.py:69` |
| d | The test database is migrated, never `create_all` | `conftest_db.py:124-137`, `:192-197`; `.github/workflows/python.yml:294` |
| e | The `database` fixture skips on unreachable or unmigrated | `conftest_db.py:190`, `:192-198` |
| f | The teardown suspends triggers transaction-locally | `conftest_db.py:352` |
| g | The validation tables have no enum | `validation_rules.py:65` |
| h | PL/pgSQL triggers have a migration precedent | `backend/migrations/versions/61981ea8f274_custom_metrics.py` |

The executor re-reads each at its own tree and stops on any that no longer holds.

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| — | None of this plan's own. The guard's design is #971's (A.4), which carries T2, T3 and the evidence-based condition at the cited head, still under audit (**Status**, activation need 1) | — | — | — | — | — |

The order against the validation-rule fix slice is decided by the maintainer's 11:56:33 BST
entry (**Serialisation**).

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch;
  `uv sync --all-packages`.
- [ ] Confirm #971 is merged and minted; **stop if not**. If its minted text differs from
  the head this plan cites, align this plan to it by a dated delta before the first code
  step.
- [ ] Re-derive premises a–h and item 1's set; quote both.
- [ ] `gh pr list --state open`; read anything ruling on approvals, the guard or the
  validation rules; name the SHA read. Run the serialisation check against every slice in
  flight. Note the gate-slot rule (Acceptance 12) for every suite-level run.

### Task 1: The declarations

**Files:** `backend/src/app/db/models.py`; `backend/src/app/platform/validation_rules.py`
(the `StrEnum`); test `backend/tests/test_approval_guard.py`.

- [ ] Red first: Acceptance 1's declaration test and its four cross-checks, with the two
  planted cases.
- [ ] Declare every `status` column; green; commit.

### Task 2: The trigger, and the proof that the test database carries it

**Files:** one revision under `backend/migrations/versions/`; the error translation for the
trigger's SQLSTATE; `backend/tests/test_approval_guard.py`; `backend/tests/conftest_db.py`
(the head check).

- [ ] Red first: Acceptance 6's `pg_trigger` test, connecting to `test_database_url()`
  directly, against a scratch database one migration short of head — it fails, naming each
  table.
- [ ] The revision (Acceptance 2), over the set Task 1 derives; the downgrade drops the
  trigger and function from every table.
- [ ] Red first, Acceptance 3's forms on every table, each also shown to succeed with the
  trigger dropped in a scratch database; then Acceptance 3's evidence cases on the 5
  evidence-only tables, including the flag-only substitution that makes the forgery case
  fail.
- [ ] The ref pin test of Acceptance 2, red first on a planted `'/'` separator.
- [ ] The round trip, head and head−1, and `tests/test_repository_invariants.py`; commit.

### Task 3: The decision path sets and resets the flag

**Files:** `backend/src/app/platform/approvals.py` (`approval_decision()`; `decide`);
`backend/src/app/api/approvals.py` (`_carry_to_the_artifact`); tests.

- [ ] Red first: Acceptance 4's positive control fails before the flag exists.
- [ ] `approval_decision()`: `SET LOCAL … 'on'`, and `'off'` in a `finally`; entered in
  `decide` around `:416`–`:419` and in `_carry_to_the_artifact`; green.
- [ ] Red first: T2's after-the-block write is refused; the block-closed-before-flush
  broken input.
- [ ] The three static checks (Acceptance 5), each red first on a planted violation.
- [ ] Commit.

### Task 4: Allowance sites and fixtures

- [ ] The allowance literal and its sites (Acceptance 7), with the removal control.
- [ ] Move each of the 17 fixture files onto the decision path or the tests-only helper.
- [ ] The full backend suite, **in a gate slot** (Acceptance 12), green, `N passed` against
  main's; commit.

### Task 5: The gate and the ledger

- [ ] The full two-half gate in a gate slot; quote every rc, `N passed`, `HEAD`, `uptime`.
- [ ] The ledger (`LG-`, working id): the tree, the premises, the derived set, every red
  quote, the #971 alignments, the stated limits, the decided order.
- [ ] Item 13.

## Hand-off

WK-674 Slice 2 (#973, working id 9920) follows in lane A: its creating migration installs
the same trigger function on `deployment_requests`, its vocabulary joins item 1's set, and
its plant joins item 3. The validation-rule fix slice runs between them (the 11:56:33 BST entry), so
Slice 2 starts after the fix closes.

## Self-review

- **Scope against #971 sub-item 9:** sub-items 1–8 and 10 over the 8 existing tables are
  here; the `deployment_requests` extension is Slice 2's.
- **Each ruling applied where it operates:** sub-item 1 (Acceptance 1, Task 1); 2
  (Acceptance 2, Task 2); 3 (Acceptance 4, Task 3); 4 (Acceptance 5, 11); 5 (Acceptance 7,
  Task 4); 6 (Acceptance 8, Task 4); 7 (Acceptance 3); 8 (Acceptance 3); 10 (Acceptance 6,
  Task 2).
- **auditor-close1255 on `ed879f7b`:** T2 (Acceptance 4, Task 3), T3 (Acceptance 6, Task 2),
  the advisory residual (Acceptance 11). **#971 at `3de69560643b2abc8d20afc923416a4ef66104a1`** (evidence-based, still under
  audit): Acceptance 2's per-table requirement and ref pin, 3's evidence cases, 4's
  flush-then-reset and no-leak case, 5's narrowed scan, 9 adopted, 11's residual.
- **auditor-plans' seven trigger items:** the revision count and downgrade with `pg_trigger`
  per table (Acceptance 10); `SET LOCAL` replacing the ContextVar as the guarantee
  (Acceptance 4; the ContextVar stays only for the static checks); the ORM hook secondary
  and the write set (Architecture, Serialisation); the fixtures and `seed.py` setting the
  flag (Acceptance 7, 8); the allowance by site with a removal control (Acceptance 7); the
  per-worktree database and head/head−1 (Acceptance 6, 10); owners and superusers
  (Acceptance 11). Also M1's caveat as the fourth cross-check (Acceptance 1).
- **Maintainer entries applied:** 11:21:51 (1), 11:23:26 (7, Serialisation), 11:42:08 and
  11:43:28 (12), 11:44:15 (Architecture, 2–5), 11:45:55 (6), 11:48:28 (Status, Global
  Constraints), 11:55:31 (2, 3, 9, adopted in #971).
- **auditor-plans on `adb4ace8`:** V1, the fourth leg reworded with the CHECK-reading rule
  (Acceptance 1); head and head−1 as an acceptance line (Acceptance 10); the order's cost
  stated (Serialisation); the fixture helper creating evidence (Acceptance 8); the flush
  order in the positive control (Acceptance 4); the forged-flag plant (Acceptance 3).
- **The order** is the maintainer's decision of 11:56:33 BST, stated in Serialisation and
  Hand-off.
- **Open:** no decision point of this plan's own. Activation waits on #971.
