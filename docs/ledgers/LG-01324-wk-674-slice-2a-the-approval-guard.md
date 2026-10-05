---
id: LG-1324
family: ledger
title: WK-674 Slice 2a — The approval guard (only the decision path writes approved), enforced by the database
status: closed
created: 2026-09-30
owner: executor
tree: 22fe674b4a590c47095c6ba608fe974264581139
phase: P2
work: WK-674
slice: SL-1302
plans: [PL-1303]
corrected_by: []
relates: [RL-1301, RL-1263, FD-1218]
---

# LG-1324 — WK-674 Slice 2a (SL-1302)

Executed from `PL-1303` under `RL-1301`. Branch `sl-1302-approval-guard`, from `origin/main`
`22fe674b4a590c47095c6ba608fe974264581139` (#984's squash), rebased onto later `origin/main`
as main moved; each rebase re-ran the targeted tests named below. Working id 9942, confirmed
free by the lead and reserved in eta.md.

**The mint.** Minted 2026-09-30 as LG-1324 (assigned by the lead after mint batch 6, #999; `doc-id.py next` = 1324 at `32f3fa92`); it was filed under working id 9942. The entries below that quote check 31's gap `… to 9942` and the sentences naming working id 9942 are numbers as measured at the heads they name and are left as written. Commits are named by subject,
never by SHA, because a rebase voids a SHA a ledger cites.

## Tasks

### Task 0 — preconditions

**The dispatch record, quoted verbatim**
(`~/gi-pricing-plan.local/handover/DISPATCH-WK-674-S2a-DRAFT-2026-09-30.md`, read 2026-09-30
after the lead's GO; the file name keeps "DRAFT", its title now reads "FINAL"):

> # Dispatch record — WK-674 Slice 2a (SL-1302, was 9922), from PL-1303 (was 9923) — FINAL
>
> **Status: DISPATCHED 2026-09-30 13:27:28 BST; this is the actual lane A slot-grant time that PL-1303's Activation defers to** (GO by the lead) at main `22fe674b4a590c47095c6ba608fe974264581139` (#984's squash: RL-1301, SL-1302 and PL-1303 minted; PL-1303 active). On the maintainer's MERGE-ACK #984 and "2026-09-30 13:10:33 BST — DECISION: accept PL-1303's in-batch activation (ii)…", whose condition is that **the ledger's Task 0 quotes this record verbatim, including this grant time**. Was: DRAFT. Finalised by the lead when #984 merges and activates, with the minted ids and line numbers re-checked at that tree. Every condition below cites a maintainer entry in `~/gi-pricing-plan.local/channel/to-lead.md` (2026-09-30) by its header.
>
> - **Plan:** #984 (PL 9923 + SL 9922), CLEAN at `a6371792` (auditor-plans); four mint-turn nits land before activation (F-2 on a flag-satisfiable table; SL-1302 (then working id 9922) body; #971 re-cited by minted id; fixture helper flushes the request before the artifact).
> - **Ruling:** #971 (RL 9906), CLEAN at `897859eb`; minted before #984 ("12:10:38 BST — DECISION: the mint queue re-ordered so lane A starts S2a").
> - **Split:** "11:48:28 BST — DECISION + ACCEPTANCE (maintainer by delegation): WK-674 S2 split, option (b), S2a = the approval guard".
> - **Lane:** A, under RL-1263. Order "11:56:33 BST — DECISIONS: slice order after the split…": **S2a → the validation-rule fix slice (#978) → S2**, strictly sequential.
>
> ## Conditions
>
> 1. **Preconditions (Task 0):** #971 merged and minted; #984 merged and activated; the lead's go. The executor runs `uv sync --all-packages`, re-derives premises a–h and the 8-table guarded set, and quotes both.
> 2. **Contention measurement (RL-1263):** at the first overlap of this slice's gate with the **WK-1178 fix slice's (lane B, dispatched at the same time; WK-690 S1 is already built)** ("2026-09-30 13:24:18 BST…": "the first real overlap is the fix slice alongside S2a"), run the three-pair measurement, solo first. Record it in the ledger.
> 3. **Gate slots** ("11:42:08 BST — two decisions…" and "11:43:28 BST — the slot rule, tightened…"): any full pytest, directory or package suite, full gate or multi-DB sweep takes `/tmp/slots/gate-{1,2}` via `flock -w 1800 -E 99` (no `--`), with `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`, recording `uptime` at the start and end and the other holder. Two consecutive runs over 1.5× with ≤ 2 holders → tell the lead (the step-down rule).
>    **Correction (maintainer "2026-09-30 13:24:18 BST — DATED CORRECTION to my slot-rule entries (11:42:08 and 11:43:28): use the dev-commands wrapper verbatim"):** the form above is superseded. Any directory or suite-level run, full gate or multi-DB sweep uses `.claude/skills/dev-commands/SKILL.md`'s slot wrapper (:122-171) EXACTLY as written, plus `LOKY_MAX_CPU_COUNT=4`. It exports `GIP_GATE_SLOT`; without it, conftest.py takes the second slot too, and caps threads at 4. Quote the skill; never hand-write the line. Named single files are exempt.
> 4. **T3, CRITICAL** ("11:45:55 BST — the trigger pre-checks (one is critical)…"): the `pg_trigger` presence test connects to `test_database_url()` directly, not through the `database` fixture (which skips at conftest_db.py:190 and :192-198); it **fails, never skips**. Red first on a DB one migration short of head. The trigger DDL lives only in its migration; no fixture copies it.
> 5. **Shared paths and serialisation** (from #984; re-check at dispatch):
>    - `backend/migrations/versions/` (new revision): a registry append; the second to merge re-points `down_revision` (WK-1250 S1 also appends).
>    - `backend/src/app/db/models.py` (status metadata on existing classes): not exempt; serialise with any in-flight slice editing those classes.
>    - `backend/src/app/platform/approvals.py` and `api/approvals.py` `_carry_to_the_artifact`: shared with S2 and the VR fix; S2a goes first.
>    - `platform/validation_rules.py` and `examples/fremtpl2/seed.py`: shared with the VR fix, after S2a.
>    - `backend/tests/conftest_db.py`, the 17 fixture files and the tests-only helper: serialise with any in-flight slice editing the same file.
>    - The error translation for the trigger's SQLSTATE: concurrent-safe only if other in-flight slices add different members.
>    - **No overlap** with WK-690 S1 (lane B) and none with #977's column slice (a different Work). The record states that `git diff --stat origin/main...HEAD -- uv.lock '*pyproject.toml'` prints nothing.
> 6. **Close obligations:** restate the accepted residual ("12:06:53 BST — #971 evidence-based trigger: the named residual is ACCEPTED"); the auditor reads each new migration from `git diff --name-only <base>..<head> -- backend/migrations/versions`; carry the peril_structures zero-writer note.
> 7. **Gate:** the full two-half gate before pushing (CLAUDE.md §11). Docs checks run on a clean detached checkout of the pushed commit.
> 8. **Ledger:** an `LG-` record under a free working id, checked against eta.md's "Working ids held" table and the open PRs; minted at the merge turn.
> 9. **Helpers shared with the fix slice** (the maintainer's "12:36:02 BST — the fix slice's dispatch record: the new-file deviation accepted, plus one condition"): the fix slice's new `backend/tests/test_rating_pin_membership_api.py` imports `_handlers` (autouse), `_headers`, `_insert_version`, `_empty_pins`, `_run_compile_job` (and likely `_minimal_algorithm`) from `backend/tests/test_rating_version_compile.py`, which this slice's Acceptance 8 edits. If this diff changes any of them (name, signature or behaviour), say so in the ledger; the second of the two to merge rebases and re-runs its full gate before its ACK.

**Quoted verbatim except one token:** in the record's "Plan" item, the slice's working id written as SL, a hyphen and 9922 (in the phrase "… 9922 body") is rendered `SL-1302 (then working id 9922)`, for check 32 (the maintainer's ruling (a), 2026-09-30, at the mint turn, no exemption).

**Environment.** `pwd` was the executor's worktree
(`.claude/worktrees/exec-674s2a`), the branch `sl-1302-approval-guard`;
`uv sync --all-packages` exited 0. The worktree's test database was created with
`createdb -T gipricing` and migrated with `alembic upgrade head` (the dev-commands block).
RL-1301 was minted and active on `origin/main` (read as merged; its text is unchanged from the
head the plan cites). PL-1303 as merged differs from the head the executor read first
(`6a2f9779`) only in its Activation paragraph and its `status:`.

**Premises a–h, re-derived at `bf790e22` and again at `22fe674b`; all hold** (the commands are the
plan's own; the lines are as read in the file at that tree):

| # | Premise | Read |
|---|---|---|
| a | `approved` is written outside the decision path | `backend/src/app/platform/validation_rules.py:154` `status=APPROVED` (in `seed_builtin_rules`, `:89`); `:423` `row.status = APPROVED` (`approve_rule`, `:395`); `:643` `status=APPROVED` (`replace_rule_set`, `:538`); `backend/src/app/db/models.py:1195` `default="approved"`; `examples/fremtpl2/seed.py:441` `status="approved"` |
| b | `decide` writes and flushes | `backend/src/app/platform/approvals.py:416` `row.status = new_status.value`, `:419` `await session.flush()` |
| c | The carry drives each owning module in the same unit of work | `backend/src/app/api/approvals.py:488` (`_carry_to_the_artifact`), called `:260` and `:293`; `backend/src/app/db/session.py:69` `unit_of_work` |
| d | The test database is migrated, never `create_all` | `git grep -n 'create_all\|metadata.create' -- backend examples scripts` prints nothing; `.github/workflows/python.yml:294` `run: uv run alembic upgrade head` |
| e | The `database` fixture skips on an unreachable or unmigrated database | `backend/tests/conftest_db.py:190` and `:192-198` |
| f | The teardown suspends triggers transaction-locally | `backend/tests/conftest_db.py:352` `PERFORM set_config('session_replication_role', 'replica', true);` |
| g | The validation tables have no enum | `backend/src/app/platform/validation_rules.py:65` `DRAFT, REVIEW, APPROVED = "draft", "review", "approved"` |
| h | PL/pgSQL triggers have a migration precedent | `backend/migrations/versions/61981ea8f274_custom_metrics.py` |

**The guarded set, derived at `22fe674b`** from the mapped `status` columns of
`backend/src/app/db/models.py` (14 columns; the predicate is
`[c for t in Base.metadata.tables.values() for c in t.c if c.name == "status"]`):
8 approval-capable — `ApprovalRequestRow` (`:635`), `ValidationRuleRow` (`:1120`),
`ValidationRuleSetRow` (`:1195`), `ModelRow` (`:1361`), `PerilStructureRow` (`:1581`),
`CustomObjectiveRow` (`:1648`), `CustomMetricRow` (`:1770`), `RatingVersionRow` (`:1898`) —
and 6 non-approval: `JobRow` (`:104`), `OutboxRow` (`:253`), `DatasetVersionRow` (`:788`),
`IngestionRunRow` (`:866`), `ReferenceTableVersionRow` (`:941`), `ScoringTraceRow` (`:2207`).
That is the plan's 8-table set, table names `approval_requests`, `custom_metrics`,
`custom_objectives`, `models`, `peril_structures`, `rating_versions`, `validation_rule_sets`,
`validation_rules`. `approval_guarded_tables()` now derives it from the declarations and a test
pins it to that set.

**Baseline** (recorded by the lead's instruction of 2026-09-30, before the build):
- *Attempt 1*, 12:02:57–about 12:33 UTC, on `origin/main` at `bf790e22` (a preparation-only start, before the GO). `gate-2` was granted 12:26:46. The run was **killed by the executor's own 30-minute background limit**: it had left the harness's default limit on a command that also waited 23.8 minutes for a slot. No counts. Its killed pytest left rows in the worktree database (S-14).
- *Attempt 2*, the dev-commands wrapper (`SKILL.md:122-171`) plus `LOKY_MAX_CPU_COUNT=4`, tree `22fe674b`: queued 12:42:58 UTC (load 3.36), granted 12:57:04, ended 13:23:16 (load 2.14). Queue wait about 14 minutes; pytest 1551.30 s. **3879 passed, 2 failed**, 3 skipped; ruff, mypy, import-linter, audit-docs, req-coverage and contracts all passed. The two failures were `test_api_datasets.py::test_the_list_resolves_an_owner_to_its_display_name` and `…::test_the_detail_route_agrees_with_the_list_on_owner_name`, `IntegrityError … uq_users_issuer_subject`: S-14's signature from attempt 1's killed run. After `dropdb` + `createdb -T` + `alembic upgrade head` that file alone gave 31 passed. The full-suite total is therefore inferred, not measured. **Not solo**: about 4 minutes of overlap with the fix slice's gate (12:57–13:01 UTC, the lead's figure) and other load (5.59 at 13:02:58).
- The run started under the executor's pre-GO instructions and crossed the lead's "skip the baseline" message; it carried no S-13 grant (a baseline on `main`, not on this slice's head). The solo baseline stays owed for a quiet window and does not block.

### Task 1 — the declarations (PL-1303 Acceptance 1)

**Red first**, quoted: with `approval_guarded_tables()` and `ValidationRuleStatus` present but no
column declared, `backend/tests/test_approval_guard.py` failed for the predicted causes —
`assert ['jobs.status... marker', ...] == []` with "Left contains 14 more items, first extra
item: 'jobs.status: declares neither a vocabulary nor the non-approval marker'", and
`assert set() == {'approval_re...ersions', ...}` for the derived set. After declaring: 11 passed.

Delivered: every `status` column declares `info={"status_vocabulary": <StrEnum>}` (8) or
`info={"approval_capable": False}` (6). The test holds them to account with the plan's four
independent cross-checks (a CHECK that names `'approved'`; an `"approved"` default; a table the
approval carry writes; an `Enum`-typed column with an `APPROVED` member, or a CHECK that
enumerates the vocabulary with `'approved'`, read as `status IN (…)` or `status = ANY (ARRAY[…])`
only). The carry-written tables are **derived by AST** (in each platform module that defines
`apply_approval_decision`, the variable that gets `.status =` is bound by `select(<Row>)`), and a
test pins the walker to the four artifact tables, so a walker that stopped descending fails.
Planted cases: neither declaration; a marker on a CHECK naming `'approved'`; on an approved
default; on a carry-written table; on an `Enum` with `APPROVED`; both declarations together.

**Deviation from the plan's file list.** `ValidationRuleStatus` is defined in
`backend/src/app/db/models.py`, not in `validation_rules.py`: that module imports
`models`, so the reverse import is a cycle. `validation_rules.DRAFT/REVIEW/APPROVED` now take the
enum members' values, so there is still one source. The lead accepted this as a plan deviation for
the slice auditor to review.

**A slip, reverted.** The executor ran `ruff format` over `backend/src` once; the repository is not
`ruff format`-governed and 63 files changed. All were restored with `git checkout`, the two source
edits were redone unformatted, and the commit touches only its three intended files.

### Task 2 — the trigger (PL-1303 Acceptance 2, 3, 6, 10)

Delivered: migration `backend/migrations/versions/a9f3c6d21b87_approval_guard.py`
(`down_revision` `d7e2a9b5c418`, the single head at `22fe674b`), one PL/pgSQL function
`approval_guard()` and a `BEFORE INSERT OR UPDATE OF status, workspace_id, <slug column>, version`
trigger on each of the 8 tables, `TG_ARGV` = (artifact type, slug column[, mode]); SQLSTATE
`GP001`. Evidence-only on `models`, `custom_metrics`, `custom_objectives`, `peril_structures` and
`rating_versions`; evidence or the flag on `validation_rules` and `validation_rule_sets`; the flag
on `approval_requests`. The flag compares `IS DISTINCT FROM 'on'`. `GUARDED_TABLES` and
`create_trigger_sql()` live in the migration module; the shadow-table tests import them from it,
and no fixture copies the DDL.

*(Corrected 2026-09-30 at the mint turn, on the slice audit's L1: the two sentences below that said 403, here and in Task 3, described the first version of the mapping; the code and tests at the audited head return 500, as the next section explains.)*

**Tests** (`backend/tests/test_approval_guard_trigger.py`, 102 at first green and 105 now; the five
`test_approval_guard*.py` files together run 148 passed):
- **T3** — `test_every_guarded_table_carries_the_trigger_on_the_test_database` connects to
  `test_database_url()` directly and **fails, never skips**; the scratch-database fixture also fails
  rather than skips. **Red on a database one migration short of head**:
  `test_the_trigger_test_fails_on_a_database_one_migration_short_of_head` upgrades a scratch
  database to `d7e2a9b5c418` and asserts the presence check fails naming every guarded table.
- **Round trip** — upgrade to `d7e2a9b5c418`, an approved `approval_requests` insert **succeeds**;
  upgrade to `a9f3c6d21b87`, the same insert is refused (`GP001`); `downgrade -1`, `pg_trigger`
  shows no trigger on any of the 8 tables and `pg_proc` no function; upgrade again. Each step
  asserts the revision it reached.
- **Every table, every write form** — on shadow copies of the 8 tables
  (`CREATE TEMP TABLE … (LIKE public.t INCLUDING ALL)`) carrying the migration's own DDL: a direct
  approved insert and update on each table, an insert relying on `validation_rule_sets`'
  `default="approved"`, and on `rating_versions` a Core `update()`, raw `text()`, a non-literal
  (`func.lower('APPROVED')`), `bulk_update_mappings`, an ORM bulk `update()`, an ORM attribute
  update and `pg_insert … on_conflict_do_update`. Built armed: refused `GP001`. **Built with the
  trigger dropped: the same write succeeds** (the broken-input proof that each refusal is the
  trigger's). The five bypasses of the ORM-only guard and `peril_structures` are all inside this
  matrix.
- **Evidence cases** on each of the 5 evidence-only tables: a decided request for the row's ref is
  accepted with no flag; the flag alone (the forgery) is refused; a request for another version,
  another workspace, another slug or still in `review` is refused; re-pointing an approved row's
  `version` is refused; an update that leaves the status and ref alone is not checked. **With the
  evidence condition replaced by the flag check** (`test_with_the_evidence_condition_replaced_by_the_flag…`)
  the forgery succeeds, which is what the refusal test exists to catch.
- **The ref pin** — for each of the 7 artifact tables, evidence keyed on
  `str(ArtifactRef(type=…, slug=…, version=…))` satisfies the trigger; **with the function's `'@'`
  planted as `'/'` the same evidence is refused**. `models` composes from `model_family_slug`.
- **Teardown** — after `empty_the_database()` the trigger is present and refuses in the next
  transaction.
- **The SQLSTATE** — `app.errors.APPROVAL_GUARD_SQLSTATE` equals the migration's; an `httpx` client
  over an app with `install_error_handlers` gets a **500** problem with code
  `APPROVAL_OUTSIDE_DECISION_PATH` for the guard's refusal and a 500 `INTERNAL_ERROR` for another
  database error (the handler re-raises any SQLSTATE but `GP001`).

**An honest record on order.** The migration was written before its tests, so the pre-migration
red is not a quoted run. The red evidence for Task 2 is the scratch database one migration short of
head (presence test fails; an unguarded write succeeds), the trigger-dropped half of every
write-form test, and the plants (separator, evidence-replaced-by-flag). Task 3 was likewise written
ahead of its T2 tests; its control tests (reset removed, session-level `SET`, a no-op
`approval_decision()`) carry the broken-input proof.

**A spec change, in the same commit.** The ruling requires the SQLSTATE to map to one named
refusal, and `PlatformError` refuses an unregistered code, so `APPROVAL_OUTSIDE_DECISION_PATH`
(first 403, changed to **500** at the maintainer's steer, below) was added to `GOVERNANCE_ERROR_CODES` and to `docs/specs/06-governance.md` §5.1's
"Error codes owned by this module" paragraph with a dated note citing `PL-1303` and `RL-1301`
A.4.2. `tests/test_repository_invariants.py` holds the registry and the spec equal.

**Why 500 and not 403 or 409** (the maintainer's steer, relayed by the lead, after a first 403):
`approval_guard()` is a backstop. Every path that legitimately writes `approved` enters the decision
flag — `decide`, the carry, and the four allowance sites, pinned by the static checks — and the
premise-a write sites were read (`validation_rules.py:154`, `:423`, `:643`, `models.py:1195`,
`examples/fremtpl2/seed.py:441`) and are all among them. No route lets a client name the status
it writes, so no client request can reach the refusal, and a 409 (which would need a client-reachable
path and an earlier application-level refusal of it) has nothing to describe. Reaching GP001 means
the platform's own code wrote `approved` outside the decision path, a defect; a 403 would say the
client lacks permission, which disguises it. The response is therefore a **500 that keeps the
code** `APPROVAL_OUTSIDE_DECISION_PATH` (so the defect is named, not `INTERNAL_ERROR`), with a fixed
text, and an ERROR log whose `guard_detail` carries the trigger's `DETAIL` (`table=… ref=…`; the
function composes the ref, and `approval_requests` has none so its row id is used). 06 §5.1's dated
line states the status and the reason. Tests: GP001 -> 500 + the code with exactly one ERROR record
naming the table; any other database error is re-raised unchanged and stays `INTERNAL_ERROR`; the
decide route with `approval_decision()` made a no-op returns that 500.

### Task 3 — the decision path sets and resets the flag (Acceptance 4, 5)

Delivered: `approval_decision(session)` in `backend/src/app/platform/approvals.py`:
`SET LOCAL app.approval_decision = 'on'`; on exit the session is flushed and, in a `finally`,
`SET LOCAL … 'off'`. If the body or the flush has already killed the transaction, the reset
cannot run and the original error surfaces. Entered in `decide` around the status assignment and
its flush (`:416`–`:419`) and in `_carry_to_the_artifact` around the four `apply_approval_decision`
calls. `withdraw` goes through `_carry_to_the_artifact`; withdrawing never produces `approved`, so
its entry is harmless, and stated. **No `ContextVar`** was added: the plan said it "stays only for
the static checks", and the static checks are AST scans that need none.

**Tests** (`test_approval_guard_decision.py`, 9; real tables, rolled back): the block sets the
flag, writes, flushes, then reads `'off'`; **T2** — an approved write after the block in the same
unit of work is refused, and **with the reset removed the same write is allowed**; **F-2** — on
`approval_requests` (a flag-satisfiable table), an ORM attribute set to `approved` inside the block
and left unflushed (exit flush patched out) is refused when flushed later, the flag having read
`'off'`, and with the reset removed the same flush succeeds; **no leak** — with one pooled
connection the next transaction does not read `'on'`, and a session-level `SET` does leak
(so the check has something to catch); the reset runs when the body raises; a database error in
the body surfaces as itself. `test_api_approvals.py` gains
`test_a_decision_without_the_decision_flag_is_refused_by_the_database`: with `approval_decision()`
a no-op the decide route returns the **500** `APPROVAL_OUTSIDE_DECISION_PATH` and the request stays in
`review`; the existing `test_an_approver_approves` and its FR-355 sibling are the positive controls
(an approved request and its artifact, read back `approved`). **The flush-order control** the plan
names ("the `approval_requests` row reaches the database before the carry writes the artifact") is
carried by those existing tests rather than a dedicated one: the evidence-only trigger reads that
row, so a decision whose carry ran ahead of the flush at `:419` could not produce an approved
artifact and those tests would fail.

**Static checks** (`test_approval_guard_static.py`, 17; `backend/tests/` exempt, nothing else):
(1) `approval_decision()` is entered nowhere in `backend/src` or `examples/` except the two
sanctioned sites and the allowance, by (file, enclosing function), and a bare call outside
`async with` is refused; (2) the literal `app.approval_decision` appears only in
`platform/approvals.py` and the guard's migration, and a session-level `SET` or
`set_config(…, false)` is refused; (3) no SQL string sets `session_replication_role` (a docstring
mention is not one — `platform/objectives.py:108`); (4) no `create_task`, `gather`,
`run_in_executor` or `to_thread` lexically inside an `approval_decision()` block. Each is red on a
planted violation, including a new function inside an allowed file (the allowance is by site, not
by file).

### Task 4 — allowance sites and fixtures (Acceptance 7, 8)

**The allowance literal** (`ALLOWANCE_SITES` in `test_approval_guard_static.py`; shrink-only):
`validation_rules.approve_rule` and `replace_rule_set` (temporary, removed by the WK-1178
validation-rule fix slice, red first, once the trigger exists), and the legitimate seed writers
`validation_rules.seed_builtin_rules` and `examples/fremtpl2/seed.py`'s `run`. A test pins the
literal to the sites that really enter the context. **Positive controls and the removal control**
(`test_approval_guard_allowance.py`, 6): each of `seed_builtin_rules`, `replace_rule_set` and
`approve_rule` writes successfully through its entry and is refused `GP001` with its entry removed
(`approval_decision()` made a no-op). The fremtpl2 seed imports the name directly and is held by
the literal.

**Fixtures.** `backend/tests/approved_rows.py` is the tests-only helper: for a row on an
evidence-only table it writes a decided `approval_requests` row for the row's ref under
`approval_decision()`, **flushes it explicitly**, and only then writes the artifact row; for a
validation table the flag suffices. `add_approved()` and `mark_approved()` moved these files onto
it: `test_api_blobs`, `test_api_rate_tables`, `test_api_validation_rules` (its CHECK negative passes
the trigger through the flag so it still tests the CHECK), `test_data_jobs`, `test_lineage`,
`test_paired_quantile_models`, `test_rate_tables_service`, `test_rating_version_compile`,
`test_reference_pin`, `test_validation_reports`, `test_wf01_journey`, **and two files outside the
plan's 17-file grep** — `test_custom_objectives_api` and `test_custom_metrics_api`, whose
`_advance` helpers take the status as a variable. Of the plan's 17 files, `test_approvals`,
`test_custom_metrics`, `test_custom_objectives`, `test_model_lifecycle`, `test_model_nfrs` and
`test_rating_versions` needed no change (they approve through the decision path or only compare).
The plan's grep was an upper bound and also an undercount: its pattern
`status\s*=\s*"approved"|Status\.APPROVED|status=APPROVED` cannot see a status held in a variable, which is how the
two `_advance` helpers were found (by reading `test_rating_version_compile.py`'s imports). `test_api_approvals.py`
is also edited, to add the no-flag control test.

**Condition 9.** `test_rating_version_compile.py` was edited on **one line** — the `model_row.status
= ModelStatus.APPROVED.value` in `test_the_compiled_bundle_survives_persistence`'s `_seed_gbm`
became `await mark_approved(session, model_row)`, plus an import. None of `_handlers`, `_headers`,
`_insert_version`, `_empty_pins`, `_run_compile_job` or `_minimal_algorithm` was touched (name,
signature or behaviour). The fix slice's `test_rating_pin_membership_api.py` and this file were run
together after the rebase over it: 14 passed.

**The full backend suite** (`uv run pytest -q`, in slot `gate-1` under the dev-commands slot
wrapper's slot logic with its thread caps and `GIP_GATE_SLOT`, plus `LOKY_MAX_CPU_COUNT=4`): tree
= this slice's four commits over `22fe674b`'s lineage as of the run; queued and granted
2026-09-30T14:00:34 UTC (no queue wait; load 4.35), ended 14:26:43 (load 4.04). **4186 passed, 3
skipped, 0 failed, 1553.31 s.** The other slot (`gate-2`) was free at 14:10:39 and at the end, so
the slot holders were one; load 4–5 was other work on the box. Against the 3881 of `bf790e22`'s
baseline, 305 more tests pass.

### Task 5 — the gate and the record

**The full two-half gate at head `5c7ae3b2d928ec5e0c32ef5fc873f0a9304df130`** (the code-only head,
the ledger held out; five code commits over `origin/main` `e3600789`; the lead's S-13 grant for that head
only). Python half: the dev-commands wrapper (`SKILL.md:122-171`) verbatim plus `LOKY_MAX_CPU_COUNT=4`,
slot `gate-1`; queued and granted 2026-09-30T14:40:34 UTC (no queue wait; load 2.45), ended 15:08:51
(load 5.14). Wall 28 min 17 s; pytest itself 1679.53 s.

| stage | result |
|---|---|
| ruff | pass (exit 0) |
| mypy | pass (exit 0) |
| import_linter | pass (exit 0) |
| audit_docs | pass (exit 0) |
| req_coverage | pass (exit 0) |
| contracts | pass (exit 0) |
| pytest | pass (exit 0): **4214 passed, 3 skipped** |

`GATE: pass — 7 of 7 stages passed`. Frontend half, 15:09:17–15:11:51 UTC on the same head, every
command exit 0: `pnpm --dir frontend install --frozen-lockfile`, `generate:api`, `lint`,
`type-check`, `test` (97 files, 609 tests passed), `build`. This slice changes nothing under
`frontend/`.

**Contention (RL-1263).** Another full gate began on `gate-2` at 15:00:54 UTC, 20 minutes into this
run, and held it to the end (both slots `BUSY` at 15:08:51); load rose to 11.6 at 14:50 and 17.5 during
the frontend half. pytest took 1679.53 s against 1553.31 s for the same suite, without a parallel gate and
without the six other stages running beside it (14:00:34–14:26:43), and 1551.30 s for attempt 2
(which overlapped the fix slice for about 4 minutes). The extra stages (seven run at once in the wrapper)
and the overlap are confounded: this is an informative figure, not the three-pair measurement.
Runs so far, each with its own queue wait and wall time:

| Run | Tree | Queue wait | pytest wall | `uptime` start → end | Other holder |
|---|---|---|---|---|---|
| Baseline attempt 2 (wrapper) | `22fe674b` | about 14 min | 1551.30 s | 3.36 → 2.14 | the fix slice's gate for about 4 minutes (the lead's figure) |
| Suite only, this slice | the four code commits then | none | 1553.31 s | 4.35 → 4.04 | none in the other slot |
| Full gate, this slice (a **confounded candidate pair**: seven stages at once, not pytest alone) | `5c7ae3b2` | none | 1679.53 s (gate wall 28 min 17 s) | 2.45 → 5.14 | another gate on `gate-2` from 15:00:54 to the end |

**The ledger lands after the gate.** The gated head holds no ledger: a record under working id 9942
reds check 31 (`gap … between 1311 and 9942`) and so two `tests/test_repository_invariants.py` tests
(`test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`). This
commit is the ledger and its `docs/INDEX.md` row on top of the gated head, where those two tests and the
`audit_docs` stage fail by design until the merge-turn mint.

## What changed from the plan

| Plan | Did | Why |
|---|---|---|
| `ValidationRuleStatus` in `validation_rules.py` | In `app/db/models.py` | import cycle; accepted by the lead |
| Error translation for the SQLSTATE, no spec text; `06-governance.md` not in the plan's file list | `APPROVAL_OUTSIDE_DECISION_PATH` (500) in `06` §5.1 and `errors.py`, in the same commit as the trigger | `PlatformError` refuses unregistered codes and registering one forces the §5.1 entry (`test_repository_invariants`); accepted by the lead as a plan-gap deviation; status 500 per the maintainer's steer |
| 17 fixture files | 11 of them plus `test_custom_objectives_api` and `test_custom_metrics_api` | the grep's pattern misses a status passed as a variable |
| `ContextVar` for the static checks | none | the checks are AST scans |
| Dedicated flush-order control | carried by the existing decide-route tests and a no-flag mutation | see Task 3 |
| Red-first for Tasks 2 and 3 | broken-input proofs, not a pre-implementation run | see Task 2 |

## The ledger is held out of the gate head

`tests/test_repository_invariants.py` runs `audit-docs.py`, and a record under a working id reds
check 31 (`gap in the full allocation between 1311 and 9942`), which fails two tests
(`test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`).
The code head was therefore gated without this file, and the ledger commit lands on top of it
afterwards, where those two tests fail by design until the merge-turn mint.

## Slice audit: CLEAN, with five LOW findings (added 2026-09-30, at the mint turn)

auditor-close1255 found the slice clean at `4a2423f2c636fe3efab5af59d5f25e1dc755a5db`: the mutations
re-run (trigger dropped: 3 red; flag reset skipped: 4 red; T3 fails and never skips), the migration
read whole and round-tripping, GP001 mapped to 500, and the Task 0 quote byte-identical to the dispatch
record. The findings are quoted below **as the lead relayed them** (the audit record's own wording is
the auditor's; this ledger holds the lead's verdicts). The lead's verdicts:

- **L1 — fixed in this ledger.** "The ledger says 403 at Task 2's SQLSTATE bullet and Task 3's decide
  route; the code and tests say 500." Corrected above with a dated line.
- **L5 — fixed in this ledger.** "The ledger's PRs section still says 'number recorded here when it
  exists'." Filled in with #997.
- **L2 — known LOW deviation, carried to #978.** "The trigger's HINT names
  `/api/v1/approvals/{id}/decide`; the real route is `/api/v1/approval-requests/{id}/decide`." File:
  the `HINT` text in `backend/migrations/versions/a9f3c6d21b87_approval_guard.py`
  (`APPROVAL_GUARD_FUNCTION`).
- **L3 — known LOW deviation, carried to #978.** "A dead `sys.exc_info()` branch in
  `approval_decision()`'s `finally`: a reset failure is always swallowed." File:
  `backend/src/app/platform/approvals.py`, the `finally` of `approval_decision()`.
- **L4 — a DEVIATION from RL-1301 A.4.2** (the maintainer's condition on accepting these verdicts,
  by delegation, 2026-09-30), not only a LOW: "The trigger fires on the column LIST, with no
  `OLD IS DISTINCT FROM NEW` guard." The trigger fires on the listed columns, with no
  `OLD IS DISTINCT FROM NEW` guard, which is wider than A.4.2's "an UPDATE that changes". It is wider,
  not narrower: every change the ruling names is checked, and an UPDATE that names a listed column
  without changing it is checked too. File: the `CREATE TRIGGER … UPDATE OF` clause built by
  `create_trigger_sql()` in `backend/migrations/versions/a9f3c6d21b87_approval_guard.py`. **Carried to
  #978, which either narrows it to the ruled scope or obtains a dated ruling amending A.4.2.**

L2 to L4 sit in code that was gated at `5c7ae3b2`; fixing them here would cost a full gate, and #978
is the next slice to edit `approvals.py`.

## Stated limits, unchanged from PL-1303 Acceptance 11 and RL-1301 A.4.4

- A database superuser, or a role able to drop the trigger, can bypass it; so can
  `session_replication_role = replica`, which needs superuser (used on purpose by the teardown and
  by the audit tamper tests, `test_audit.py:168`, `:194`; `test_api_audit.py:153`).
- **The accepted residual** (the maintainer's entry headed
  `2026-09-30 12:06:53 BST — #971 evidence-based trigger: the named residual is ACCEPTED`):
  arbitrary SQL on the application's connection can set the flag, insert an approved request and
  write, and this is accepted beside the superuser and `session_replication_role` residuals, with
  no trigger-side count of `approval_decisions` required. On the 5 evidence-only tables a forgery
  takes a forged, decided `approval_requests` row; what the flag still opens alone is
  `approval_requests`' own transition and the two validation tables while they hold an allowance.
  The literal scan guards the flag, and a literal assembled at run time (concatenated, or in an
  f-string) evades it.
- Alembic data migrations are covered by the trigger. The auditor runs
  `git diff --name-only <base>..<head> -- backend/migrations/versions` and reads each new
  migration: this slice adds exactly one, `a9f3c6d21b87_approval_guard.py`, which sets no flag.
- **`peril_structures` has no sanctioned writer and is guarded all the same** (RL-1301 A.4.1's
  zero-writer note): nothing in `backend/src` writes `approved` to it, no decision hook exists for
  it, and its trigger refuses an approved write for lack of evidence. A future writer must go
  through the decision path or be named in a ruling.

## Decided order (PL-1303 Serialisation)

S2a, then the WK-1178 validation-rule fix slice, then WK-674 Slice 2, strictly in sequence, by the
maintainer's entry headed `2026-09-30 11:56:33 BST — DECISIONS: slice order after the split…`. The
fix slice removes the two temporary allowance sites, red first, and then drops the `'flag'`
argument from each validation table's trigger by a migration once its last allowance site has
gone (shrink-only). Slice 2's creating migration installs `approval_guard()` on
`deployment_requests` and its vocabulary joins the derived set.

## Contention (RL-1263)

Runs recorded so far, each with its own queue wait and wall time:

| Run | Tree | Queue wait | pytest wall | `uptime` start → end | Other holder |
|---|---|---|---|---|---|
| Baseline attempt 2 (wrapper) | `22fe674b` | about 14 min | 1551.30 s | load 3.36 (queued) → 2.14 | the fix slice's gate for about 4 minutes (the lead's figure); other load up to 5.59 |
| Suite, this slice | four commits over `22fe674b` lineage | none | 1553.31 s | load 4.35 → 4.04 | none in the other slot (`gate-2` free at 14:10:39 and at the end) |

The two pytest wall times, 1551 s with an overlap and 1553 s without one, differ by 2 s. That is
one pair taken at different times and loads, not the three-pair measurement RL-1263 calls for, and
the first real overlap of this slice's full gate with the fix slice's remains to be measured.

## PRs

**#997** (draft), opened 2026-09-30 on the slice branch after the full gate; audited clean (see below).
