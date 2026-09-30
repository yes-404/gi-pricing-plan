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
relates: [PL-1237, RL-1263, RL-1296, FD-1218]
---

# WK-674 Slice 2a — The approval guard: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `python-package` and `python-test` (every task), `dev-commands` (the migration, the gate and the gate slot) and `fastapi-service` (Task 3), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make "`approved`" unreachable except through the approval decision path, on **every**
approval-capable table, **enforced by the database**, so that no write path — ORM, Core,
raw SQL, bulk, a non-literal value, or a table nothing approves yet — can set it on its own.

**Architecture** *(the primary guard is pending #971's next head; see **Status**)*. A
Postgres `BEFORE INSERT OR UPDATE` trigger on each guarded table refuses a row whose new
`status` is `'approved'` (on insert, or on an update from any other status) unless
`current_setting('app.approval_decision', true) = 'on'`. The decision path sets
`SET LOCAL app.approval_decision = 'on'` inside its transaction, spanning its write **and**
its flush; `SET LOCAL` ends at commit or rollback. The trigger ships as one Alembic
revision. An ORM-level check (`before_flush` / `do_orm_execute`) and static tests remain as
**secondary**, fast-feedback layers, never the guarantee. This slice guards the tables that
exist today; WK-674 Slice 2 adds `deployment_requests` to the guarded set in its own
migration.

**Tech Stack:** PostgreSQL 16 (PL/pgSQL trigger), Alembic, SQLAlchemy 2.x async events,
pytest. No new dependency: no `uv.lock` or `pyproject.toml` change.

**Spec:**
- [`../specs/06-governance.md`](../specs/06-governance.md) §3.2 — **FR-351** (`06:92`, the
  uniform lifecycle: "approved" reached through the approval workflow), **FR-354** (`06:95`,
  the policy's approver count, which a direct write bypasses), **FR-356** (`06:97`, pinned
  approvals); `06:22` ("approved" means the same thing for every governed artifact).
- The ruling this slice executes: **#971** (working id 9906), item A.4, read at head
  `80afeb40d680f5671b9c4697e7c7e9e8c1af7ff0` — **still under audit, and being revised to the
  trigger-primary design** (see **Status**). Cited by PR number until it mints.

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
in Slice 2's leaf plan (#973, working id 9920) by its own dated delta. `PL-1237` is not edited.

**Activation needs, in order:**
1. **#971's next head lands** with A.4 in its trigger-primary form (the maintainer's steer
   headed `2026-09-30 11:44:15 BST — #971 A.4: five ORM-guard bypasses → steer to a DATABASE trigger as the primary guard`),
   and #971 is audit-clean and minted. This plan is then aligned to it at every site class,
   including the seven trigger items auditor-plans listed (Acceptance 1–8 mark each
   **pending #971**).
2. **The lead's go.**

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" and
"red on broken input" are as Slice 2's leaf plan (#973) defines them: the failing run is quoted in the ledger
with its failing assert line and the predicted cause; a failure for any other cause is a plan
defect.

1. **The guarded set is derived, independently of the modules** (auditor-close1255 M1, the
   maintainer's entries headed `2026-09-30 11:21:51 BST — status 11:25 noted; three rulings`
   and `11:44:15`). A mapped class under `app.db.models.Base` with a `status` column is
   **guarded** if any of four legs holds:
   1. its `status` CHECK constraint names `'approved'`;
   2. its `status` has a `default=`/`server_default=` of `"approved"`;
   3. an `apply_approval_decision` driven by `_carry_to_the_artifact`
      (`backend/src/app/api/approvals.py:488`, `:499-517`) writes it;
   4. **its `status` column's type or CHECK admits `'approved'`** — an `Enum` type with that
      member, or any CHECK whose predicate accepts the value — evaluated over **every**
      mapped class with a `status` column (auditor-plans' M1 caveat: `rating_versions`
      reaches the set only through leg 3, so a future approval-capable table with none of
      legs 1–3 would otherwise escape).

   Plus `approval_requests`. At `9f63d0fe` auditor-close1255 counted 8 tables, including
   `peril_structures`; the executor re-derives the set at its tree, quotes it, and every
   later item is over that derived set, never a hand list. **Limit, stated plainly:** a
   `String` status column with no CHECK, no default, no enum type and no decision-path
   writer is invisible to all four legs; the declaration test (item 2) is what catches it.
2. **Every guarded table declares its vocabulary** as column metadata
   (`info={"status_vocabulary": <StrEnum>}`, #971 A.4 item 1). This slice declares a
   `StrEnum` of `backend/src/app/platform/validation_rules.py:65`'s constants
   (`DRAFT, REVIEW, APPROVED = "draft", "review", "approved"`) for `validation_rules` and
   `validation_rule_sets`. `scoring_traces`, `ingestion_runs`, `reference_table_versions`,
   `jobs` and `dataset_versions` need none. Red first: a guarded table planted without a
   declaration fails.
3. **The trigger exists in the test database** (the maintainer's entry headed
   `2026-09-30 11:45:55 BST`, item 2 — CRITICAL). Before any red-first plant, a
   session-scoped check asserts from `pg_trigger` that the trigger exists and is enabled on
   **every** guarded table, and that the database's `alembic_version` equals the repository
   head; it **fails**, never skips. Today the test database is migrated, not built by
   `create_all`: the `database` fixture skips unless `alembic_version` holds a row
   (`backend/tests/conftest_db.py:192-197`), and `backend/tests/` contains no `create_all`.
   A shared database at an older revision lacks the trigger (FD-1218 records the shared
   template holding a stale schema), which is why the head is asserted too. The trigger DDL
   lives only in its migration; no fixture installs a copy. The teardown's
   `session_replication_role = replica` (`conftest_db.py:340-360`) suspends triggers for its
   own transaction only; a test asserts the trigger is in force again after
   `empty_the_database()`. *(Pending #971: the per-worktree database built by `createdb -T`
   then `alembic upgrade head`, and the migration tests at head and at head−1.)*
4. **Every write form is refused outside the decision path, red first, on every guarded
   table**, on insert and on update, each shown to **succeed with the trigger dropped** (so
   the trigger, not something else, is what refuses): an ORM attribute write; an ORM
   constructor insert; an insert relying on a `default="approved"` (`models.py:1195`); a
   Core `update(Row.__table__)`; a raw `text()` statement; `bulk_update_mappings`; a
   non-literal value (`func.lower('APPROVED')`); and a direct write on **`peril_structures`**,
   which nothing approves today but which is guarded all the same (a zero-writer table gets
   a note, never an exemption). These are auditor-close1255's five bypasses of the ORM guard
   at `80afeb40`, plus the ORM path.
5. **The decision path succeeds — positive control, with the flag spanning the flush** (M2).
   `decide` assigns the status at `backend/src/app/platform/approvals.py:416` and flushes at
   `:419`; the flag is set before `:416` and is still set at `:419`, in the same transaction.
   `_carry_to_the_artifact` (`api/approvals.py:488`) runs inside that transaction, so the
   owning module's write and its flush are covered too. The control asserts that both the
   request and its artifact are `approved` **in the database**, read back in a new session.
   Red on broken input: with the flag reset before the flush, the trigger refuses the
   sanctioned write. *(Pending #971: `SET LOCAL` replacing the ContextVar.)*
6. **Only the decision path sets the flag.** A static test fails any statement setting
   `app.approval_decision` in `backend/src` outside the decision path's one helper, and any
   `create_task`, `gather` or `run_in_executor` lexically inside the decision block (a
   spawned task would copy the context). `backend/tests/` is exempt, and nothing else. Red
   first on a planted third site.
7. **Seed and fixture writers set the flag explicitly, from a named list** (11:44:15):
   `seed_builtin_rules` (`validation_rules.py:89`, `status=APPROVED` at `:154`) and the demo
   seed's direct row (`examples/fremtpl2/seed.py:441`) each set it in their own transaction,
   and appear in a test-held, **shrink-only** literal. The 17 fixture files that write
   `approved` directly (`git grep -l -E 'status\s*=\s*"approved"|Status\.APPROVED|status=APPROVED' -- backend/tests`
   at the tree above, an upper bound) move onto the decision path, or onto one helper under
   `backend/tests/` that sets the flag: `test_api_blobs.py`, `test_api_rate_tables.py`,
   `test_api_validation_rules.py`, `test_approvals.py`, `test_custom_metrics.py`,
   `test_custom_objectives.py`, `test_data_jobs.py`, `test_lineage.py`,
   `test_model_lifecycle.py`, `test_model_nfrs.py`, `test_paired_quantile_models.py`,
   `test_rate_tables_service.py`, `test_rating_version_compile.py`, `test_rating_versions.py`,
   `test_reference_pin.py`, `test_validation_reports.py`, `test_wf01_journey.py`.
8. **The validation-rule allowance, temporary and shrink-only**, citing the validation-rule
   finding (HIGH; the maintainer's entry headed
   `2026-09-30 11:23:26 BST — DECISION: validation-rule approval bypass: HIGH (not CRITICAL); owner and order; two follow-ons`;
   cited as prose until it mints): `approve_rule` (`validation_rules.py:395`/`:423`) and
   `replace_rule_set` (`:538`/`:643`, with the column default `models.py:1195`) are the
   trigger's named temporary allowance. **Accepted trade-off** (auditor-plans A13-6): the
   allowance is per **table**, so a new second writer on `validation_rules` or
   `validation_rule_sets` passes until the fix slice removes it; the ledger records the gap
   with that owner. *(Pending #971: whether the allowance is an omission from the trigger's
   table list, with a shrink-only test, or a flag set by the named writers.)*
9. **The migration (FR-417).** One new revision, `down_revision` the head at the executor's
   tree (re-pointed at merge, RL-1263). `upgrade`, `downgrade -1`, `upgrade` all exit 0;
   `downgrade` drops the trigger and its function from every table it added them to, checked
   in `pg_trigger` after the downgrade. `uv run pytest tests/test_repository_invariants.py -q`
   passes.
10. **Out of scope, stated:** a table owner or a superuser can disable a trigger; that is
    outside this slice (#971's trigger items). Alembic data migrations and scripts opening
    their own engine are covered by the trigger, and each is still a review item for the
    auditor.
11. **The gate, in a gate slot.** Every run of a whole test directory or package suite, the
    gate, or a multi-database sweep — by the executor or the auditor — runs inside a gate
    slot, `flock -w 1800 -E 99 /tmp/slots/gate-1 <cmd>` or `gate-2`, **with no `--`**, with
    `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2` set and `uptime`
    reported at each grant. Only named single test files or node ids are exempt. (The
    maintainer's entries headed
    `2026-09-30 11:42:08 BST — two decisions: the escaped-pipe checker blindness → a LOW FD; box load → heavy audit runs take a gate slot`
    and `2026-09-30 11:43:28 BST — the slot rule, tightened: suite-level runs count`.) The full
    two-half gate (`CLAUDE.md` §11) exits 0, with every rc, the `N passed` line and `HEAD`
    quoted against main's.
12. **Item 11** (`PL-1237` Tasks preamble): the maintainer's MERGE-ACK, naming the PR's full
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
| `06` §3.2 | FR-356 | Unchanged; the guard does not alter pinning |

**Not in this slice:** the Deployment Request table and its plant (Slice 2, which adds
`deployment_requests` to the guarded set in its own migration); removing the validation-rule
allowance (the WK-1178 fix slice); a new route of any kind; Task 0A's authorisation sweep
(Slice 2's first task, by the maintainer's 11:01:50 BST entry).

### Serialisation against other slices

| Path | This slice | Also touched by | Order |
|---|---|---|---|
| `backend/migrations/versions/` | one revision (the trigger) | WK-674 S2 (extends the trigger to `deployment_requests`), WK-1250 S1 | registry-exempt append; the later re-points `down_revision` |
| `backend/src/app/db/models.py` (the guarded classes' `status` columns) | the `status_vocabulary` declarations — an edit to existing classes | WK-674 S2 (appends only), any slice editing those classes | this slice first; S2's appends are exempt |
| `backend/src/app/db/session.py` (`:50`) | the secondary ORM listener registration | none found | not shared |
| `backend/src/app/platform/approvals.py` (`decide`, `:416`–`:419`) | sets the flag across the write and flush | WK-674 S2 (`set_policy`), the validation-rule fix slice (`submit`/`decide`) | strictly in sequence: this slice first |
| `backend/src/app/api/approvals.py` (`_carry_to_the_artifact`, `:488`) | runs inside the flagged transaction | WK-674 S2 (the deployment branch), the validation-rule fix (the validation branch) | strictly in sequence: this slice first |
| `backend/src/app/platform/validation_rules.py` (`:65`, `:89`/`:154`) | the `StrEnum`; the seed sets the flag | the validation-rule fix slice | this slice first |
| `examples/fremtpl2/seed.py` (`:441`) | sets the flag | the validation-rule fix slice | this slice first |
| the 17 fixture files (Acceptance 7) | moved onto the decision path or the helper | any in-flight slice editing one | this slice first |
| #977's §5.1 Permission column slice (WK-1178) | nothing: this slice touches no spec table | — | may run concurrently in the other lane (different Works, no shared file) |

**The validation-rule fix slice (WK-1178, HIGH) and its order — settled here.** It needs
**this slice** (the allowance it removes is this slice's), and it does **not** need Slice 2's
content: it adds a validation branch to `_carry_to_the_artifact`, and Slice 2 adds a
deployment branch; neither reads the other. But the two edit the same function, and
`platform/approvals.py`, so they **may not overlap**. Recommended order: **S2a → the
validation-rule fix → S2**. The fix is HIGH, small, and blocked only on this slice; running
it before Slice 2 closes the bypass hours sooner, while Slice 2 would otherwise hold it
behind its much larger build. The maintainer's 11:23:26 entry placed the fix after S2 before
the split existed; this ordering is the planner's recommendation for the lead, who sets it.

### Premises re-derived at the tree above

| # | Premise | Evidence |
|---|---|---|
| a | No guard exists: `approved` is written outside the decision path | `validation_rules.py:423` (`approve_rule`), `:154` (`seed_builtin_rules`), `:643` (`replace_rule_set`); `models.py:1195` (`default="approved"`); `examples/fremtpl2/seed.py:441` |
| b | The decision path writes and flushes in `decide` | `backend/src/app/platform/approvals.py:416` (`row.status = new_status.value`), `:419` (`await session.flush()`) |
| c | The carry step drives each owning module | `backend/src/app/api/approvals.py:488`, carrying at `:499-517` |
| d | The test database is migrated, not `create_all` | `backend/tests/conftest_db.py:192-197`; no `create_all` under `backend/tests/` |
| e | The teardown suspends triggers transaction-locally | `backend/tests/conftest_db.py:340-360` |
| f | The validation tables have no enum | `validation_rules.py:65` |

The executor re-reads each at its own tree and stops on any that no longer holds.

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| — | None of this plan's own. The guard's design is #971's (item A.4), and its trigger form is pending #971's next head (**Status**, activation need 1) | — | — | — | — | — |

The order against the validation-rule fix slice is a recommendation for the lead
(**Serialisation**), not a decision point.

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch;
  `uv sync --all-packages`.
- [ ] Confirm #971 is merged and minted in its trigger-primary form; **stop if not**. Align
  every "pending #971" item to it before the first code step, by a dated delta.
- [ ] Re-derive premises a–f and the guarded set (Acceptance 1); quote both.
- [ ] `gh pr list --state open`; read anything ruling on approvals, the guard or the
  validation rules; name the SHA read. Run the serialisation check above against every
  slice in flight.

### Task 1: The guarded set and its declarations

**Files:** `backend/src/app/db/models.py` (the `status_vocabulary` metadata);
`backend/src/app/platform/validation_rules.py` (the `StrEnum`); test
`backend/tests/test_approval_guard.py`.

- [ ] Red first: the four-leg derivation (Acceptance 1) and the declaration test
  (Acceptance 2), including a planted undeclared table.
- [ ] Declare; green; commit.

### Task 2: The trigger migration and the test-database check

**Files:** one revision under `backend/migrations/versions/`; `backend/tests/conftest_db.py`
(the session check); test `backend/tests/test_approval_guard.py`.

- [ ] Red first: Acceptance 3's `pg_trigger` and `alembic_version` check against a database
  without the revision — it fails, naming each missing table.
- [ ] The revision: one PL/pgSQL function and one trigger per guarded table, from the set
  Task 1 derives, with the allowance of Acceptance 8 as #971 settles it. Downgrade drops
  both.
- [ ] Red first, Acceptance 4's forms on every guarded table, each also shown to succeed
  with the trigger dropped.
- [ ] Round trip and `tests/test_repository_invariants.py`; commit.

### Task 3: The decision path sets the flag

**Files:** `backend/src/app/platform/approvals.py` (the helper; `decide` at `:416`–`:419`);
`backend/src/app/api/approvals.py` (`_carry_to_the_artifact`, `:488`); the secondary ORM
listeners (`backend/src/app/db/approval_guard.py`, registered in
`backend/src/app/db/session.py:50`); tests.

- [ ] Red first: Acceptance 5's positive control fails before the flag is set.
- [ ] The helper sets `SET LOCAL app.approval_decision = 'on'` in the decision's
  transaction, before `:416` and still in force at `:419`; green.
- [ ] The static test of Acceptance 6, red first on a planted third site and on a planted
  `create_task` inside the block.
- [ ] The secondary ORM listeners, if #971 keeps them; commit.

### Task 4: Seeds and fixtures

- [ ] The named, shrink-only writer list (Acceptance 7) and the allowance literal
  (Acceptance 8).
- [ ] Move each of the 17 fixture files onto the decision path or the tests-only helper.
- [ ] The full backend suite, **in a gate slot** (Acceptance 11), green, with `N passed`
  against main's; commit.

### Task 5: The gate and the ledger

- [ ] The full two-half gate in a gate slot; quote every rc, `N passed`, `HEAD`, `uptime`.
- [ ] The ledger (`LG-`, working id): the tree, the premises, the derived set, every red
  quote, the pending-#971 alignments, the accepted trade-off, the order recommendation.
- [ ] Item 11.

## Hand-off

WK-674 Slice 2 (#973, working id 9920) follows in lane A. Its migration adds `deployment_requests`
to the guarded set, and its acceptance proves the deployment-request plant refused there.
The validation-rule fix slice, if the lead takes the recommended order, runs between them.

## Self-review

- **Scope against the split:** everything Slice 2's former Task 3A and Acceptance 13 held,
  except the deployment-request plant, which stays in Slice 2 (the 11:48:28 entry).
- **Each maintainer entry applied where it operates:** 11:21:51 (Acceptance 1), 11:23:26
  (Acceptance 8), 11:42:08 and 11:43:28 (Acceptance 11), 11:44:15 (Architecture, Acceptance
  4–7), 11:45:55 item 2 (Acceptance 3), 11:48:28 (Status, the delta, Global Constraints,
  Serialisation).
- **auditor-plans' items:** M1 and its caveat as the fourth leg (Acceptance 1), M2
  (Acceptance 5), A13-6 (Acceptance 8), the context and coverage items (Acceptance 6, 10).
- **Pending #971** (the seven trigger items auditor-plans listed): the revision count and
  downgrade with `pg_trigger` per table (Acceptance 9, 3); `SET LOCAL` replacing the
  ContextVar (5); the listeners secondary and the write set (Task 3, Serialisation); the
  fixtures and `seed.py` setting the flag (7); the allowance's form (8); the per-worktree
  database and head/head−1 migration tests (3); owners and superusers (10). Each is aligned
  by a dated delta when #971's head lands.
- **Open:** no decision point of this plan's own. Activation waits on #971.
