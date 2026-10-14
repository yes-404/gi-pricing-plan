---
id: PL-8016
family: plan
kind: map
title: WK-1178 — FD-8007's remedy, the factors table made append-only at the database, red first (SL-8017) — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — draft while DP-1 to DP-3 are open
created: 2026-10-14
owner: planner
tree: 1e260c1553acf39844939fe12da685ccfb835e54
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-8007, RL-8001, SL-1274, FR-43, FR-44, FR-88, FR-96, FR-240, FR-370, RL-1615]
---

# PL-8016 — WK-1178: FD-8007's remedy, the `factors` table made append-only at the database (SL-8017)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1667`, this delta `relates:` the records it builds on:
> `FD-8007` (the finding) and `RL-8001` (the ruling that found the gap). It adds **one slice
> row**, SL-8017, under `### WK-1178` in [`../roadmap.md`](../roadmap.md).
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (every acceptance item is seen red **by its cause** before the code that turns it green),
> `python-test` (the `req` marker; negative tests; `:279`'s downgrade proof), `python-package`,
> `spec-change` (Task 4), `dev-commands` (`uv sync --all-packages`; the alembic DSN; both gate
> halves) and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before
> the first step. The executor is spawned from `.claude/roles/executor.md`.

Filed under **working id 8016**; its slice row is **working id 8017** (`draft`). Both were
reserved by the lead, `~/gi-pricing-plan.local/handover/eta.md` line "2026-10-14 10:11:51 BST"
(*"RESERVED working ids PL 8016 (WK-1178 dated plan delta: FD 8007 remedy — factors made
append-only at the DB, red first; before the P2 code freeze, FR-44) and SL 8017 (its slice)"*).
Written 2026-10-14 by the planner (seat planner-fd8007). **Tree read:** `origin/main`
`1e260c1553acf39844939fe12da685ccfb835e54`, re-checked unmoved at 2026-10-14 10:20:25 BST.
Every `file:line` below was read at that tree unless it names another. `FD-8007` is read at
`origin/docs-d15-2026-10-14` @`c787c522d9d309c8fda904835e71dfc48f903564` (identical essay at
`origin/fd-8007-8011-2026-10-14` @`3d6e0f0a`); `RL-8001` at
`origin/rl-8001-wk690-s4-47-2026-10-14` @`f3cad285f3d6216bc7b27cab7a7185b95794a166`.

## Goal

`factors` carries both of `FR-44`'s layers: `gip_app` holds exactly `SELECT, INSERT` on it, and
the `artifact_append_only()` row and `TRUNCATE` triggers refuse every `UPDATE`, `DELETE` and
`TRUNCATE` whoever the caller is. Each observation is seen **red on the base tree by its
cause** first. The DB-layer red is a real `gip_app` `UPDATE` on `factors` refused by the new
trigger. No test edits a `factors` row any more. A new assertion over the pinned modelling
tables catches the next table that rides a neighbour's `GRANT`. `FR-44` carries a dated line
naming `factors` as the seventh table.

## Authority — every entry named with its author, quoted

1. **The finding, `FD-8007`** (the auditor, 2026-10-14, working id 8007; essay at `c787c522`,
   register row `docs/findings/register.md:364` at the same tree). Its *Disposition* gives
   five remedy steps. The ones this plan takes verbatim:
   *"Add `factors` to `APPEND_ONLY_TABLES` in `backend/tests/test_artifact_immutability.py`
   *before* the migration … Both must fail on `main` by their causes (the grant is `SELECT,
   INSERT, UPDATE`; zero triggers)."* *"One Alembic migration: `REVOKE UPDATE, DELETE ON
   factors FROM gip_app` and `FROM PUBLIC`; attach `factors_no_modify` (`BEFORE UPDATE OR
   DELETE … FOR EACH ROW`) and `factors_no_truncate` (`BEFORE TRUNCATE … FOR EACH
   STATEMENT`), both `EXECUTE FUNCTION artifact_append_only()`, the form `e1f2a3b4c5d6` uses;
   a matching `downgrade()`. The migration must say in its docstring why `b2c3d4e5f6a7:89`
   included `factors` and that no application path needed the grant."* *"`_make_control`
   rewritten … to create a `control` version by insert instead of editing a row."* *"Measure
   the invariant, not the list … one assertion that enumerates the tables in the modelling
   module that hold a body or a definition a pin resolves to (`factors`, `bandings`,
   `groupings`, and the other pinned artifact tables) and fails on any that grants
   `UPDATE`."* *"A one-line `FR-44` clarification that `factors` is the seventh table
   (`spec-change`), in the same commit as the migration."*
2. **The maintainer (by delegation), `to-lead.md` entry "2026-10-14 10:01:11 BST — RL 8001
   (WK-690 S4, PL-1665 4.7) CONFIRMED as drafted; FD 8007 (factors not append-only) to file
   (re lead's entry after 09:59:09)"**, verbatim on this finding: *"**FD 8007 (the `factors`
   table is not append-only at the DB):** filed by an auditor, who proposes the severity, owner
   WK-1178, with the fix as its own row (not S4). … The fix (revoke + `artifact_append_only`
   triggers + APPEND_ONLY_TABLES + `_make_control` rewrite) is scheduled before the P2 code
   freeze, owing to FR-44 "Every artifact table carries both layers"."* → owner **WK-1178**;
   **its own row**; the four remedy parts.
3. **The maintainer (by delegation), `to-lead.md` entry "2026-10-14 10:11:47 BST — FD 8007
   severity: MEDIUM + re-rate trigger CONFIRMED; FD 8011: seat a decision-maker (re lead
   10:11:23)"**, verbatim: *"**FD 8007 → MEDIUM, with the auditor's trigger (HIGH on any found
   UPDATE/DELETE path or route-level change): confirmed.** Reason: the harm is the silent-price
   class, but no application path writes `factors` (the only UPDATE is the test helper
   `_make_control`), so reaching it needs direct DB write access. HIGH would change no
   schedule: the fix is already due before the 4 Nov code freeze (my 10:01:11), as its own
   row, red first, with the remedy shape as listed. One addition to that remedy: the
   planted-UPDATE red must be shown failing against the NEW trigger at the DB layer (`gip_app`
   UPDATE → refused), not only through the derived test set, since FR-44's invariant could not
   see this table before."* → **MEDIUM** with the re-rate trigger; **due before the 4 Nov P2
   code freeze**; **red first**; the **ADD** (Task 2, DP-1).
4. **The lead's reservation**, `eta.md` "2026-10-14 10:11:51 BST" (quoted above).
5. **`RL-8001`** (the decision-maker, working id, at `f3cad285`), *"The premise (C′) rests on,
   and a gap found"*: *"`Model.spec.factors` holds the id of one `factors` row, which is one
   version of one slug"*; *"A direct edit of a `factors` row changes how every Model pinned
   to that row scores, while the pin stays the same. That is `RL-1615`'s stale-band class one
   level up."*; *"`_make_control` is rewritten to create a `control` version instead of
   editing one."* That pin-by-id reading is what DP-2 turns on.

## Evidence, re-read at `1e260c15` (not copied from the finding)

- **The grant.** `backend/migrations/versions/b2c3d4e5f6a7_model_fit_immutable.py:89`
  `op.execute(f"GRANT SELECT, INSERT, UPDATE ON models, factors TO {APP_ROLE}")`; `:90-91`
  revoke `DELETE` on `models` only. `factors` is created at
  `3ab4db71d0e8_modelling_factors_and_models.py:33-45` (no foreign key references it:
  `git grep -nE 'ForeignKey\("factors|REFERENCES factors|"factors\.id"' -- backend` prints
  nothing, so a bare `TRUNCATE factors` reaches the trigger).
- **The precedent mechanism, copied exactly.** `artifact_append_only()` is
  `a1b2c3d4e5f6_artifact_append_only.py:43-52`; its message is
  `'% is append-only: % rejected (01 FR-42, FR-43)'`, `ERRCODE = 'insufficient_privilege'`.
  Layer 1 form: `c3d4e5f6a7b8_modelling_bandings_and_groupings.py:110-112` (`GRANT SELECT,
  INSERT …`, `REVOKE UPDATE, DELETE … FROM {APP_ROLE}`, `… FROM PUBLIC`). Layer 2 form:
  `e1f2a3b4c5d6_artifact_row_triggers.py:53-74` (`{table}_no_modify` `BEFORE UPDATE OR DELETE
  … FOR EACH ROW`, `{table}_no_truncate` `BEFORE TRUNCATE … FOR EACH STATEMENT`, both
  `EXECUTE FUNCTION artifact_append_only()`; downgrade `DROP TRIGGER IF EXISTS`).
- **The tests.** `backend/tests/test_artifact_immutability.py`: `APPEND_ONLY_TABLES` `:38-52`;
  the exact-grant test `:266-294` (`granted == {"SELECT", "INSERT"}`, message
  `f"{table}: {sorted(granted)}"`); `_APPEND_ONLY_ROWS` `:303-343`; the owner-connection
  refusal test `:346-393` (asserts `"append-only" in str(refused.value)`); the grants-derived
  trigger test `:396-446`, guard `:439` `assert {row[0] for row in rows} ==
  set(APPEND_ONLY_TABLES)`.
- **The one `gip_app` precedent.** `backend/tests/test_transformations.py:523-551`
  (`test_a_stored_banding_cannot_be_updated_or_deleted`): `SET LOCAL ROLE gip_app` inside
  `database.session()`, then `pytest.raises(Exception, match=r"permission denied|InsufficientPrivilege")`.
  `gip_app` is `NOLOGIN` by design (`test_audit.py:286-287`), so a `gip_app` statement in a
  test is always a `SET LOCAL ROLE` from the owner's session.
- **The writer the fix breaks.** `backend/tests/test_fr240_governance.py:248-256`
  `_make_control` (`UPDATE factors SET body = jsonb_set(body, '{intent}', '"control"') WHERE
  workspace_id = :w AND slug = :slug`), called at `:270` (seed route), `:299` (compile over a
  control-keyed table) and `:344` (compile over a GBM fitted on a control Factor).
  `git grep -nE 'UPDATE factors|factors SET|DELETE FROM factors|TRUNCATE[^"]*factors|delete\(FactorRow|update\(FactorRow' -- backend packages scripts`
  prints only `:252`.
- **Every reader resolves a Factor by id or by `slug@version`, never by "latest":**
  `load_factors` by id (`backend/src/app/platform/modelling.py:286`, `by_id[fid]` `:331`);
  the compile resolver's `factor` branch by `slug` and `version`
  (`backend/src/app/platform/rating_versions.py:760-775`); the seed route's check reads the
  model's pinned Factor (`packages/pricing-core/src/pricing_core/rate_tables/operations.py:206-222`).
- **The alembic head** is `d4e81b7a2c95` (`d4e81b7a2c95_rate_table_version_created_by_edit.py`),
  one head across 56 revisions. Measured by parsing every `revision`/`down_revision` line under
  `backend/migrations/versions` at `1e260c15` and taking revisions that are nobody's
  `down_revision`.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | The ADD asks for a `gip_app` `UPDATE` "refused by the NEW trigger". Once the migration's `REVOKE` lands, PostgreSQL refuses a `gip_app` `UPDATE` at the **privilege check**, with `permission denied for table factors`, **before any trigger fires**. So a plain `gip_app` `UPDATE` on the fixed tree proves layer 1, not the trigger. Both refusals carry SQLSTATE `42501`, so only the message tells them apart. How is the ADD met? | **(a)** Two `gip_app` observations in one test. (i) `SET LOCAL ROLE gip_app; UPDATE factors …` → refused with `permission denied for table factors` (layer 1). (ii) In one owner transaction: `GRANT UPDATE ON factors TO gip_app`, then `SET LOCAL ROLE gip_app`, then the same `UPDATE` → refused with `factors is append-only: UPDATE rejected (01 FR-42, FR-43)` (layer 2: the trigger refuses `gip_app` even if a later migration grants `UPDATE` back). The failed statement aborts the transaction, so the `GRANT` never commits; the test then asserts `has_table_privilege('gip_app', 'factors', 'UPDATE')` is false. **(b)** Only (i). That is the privilege layer, so the ADD is not met. **(c)** Only the owner-connection `UPDATE` through `_APPEND_ONLY_ROWS`. That is the trigger, but not a `gip_app` caller. | **(a).** It is the only option where a `gip_app` `UPDATE` is refused **by the trigger**, which is the ADD's wording. It also separates the two layers by message, not by SQLSTATE (`README.md` convention 2). (c) is kept as well, because it is the existing per-member test (Task 1). | decision point (reading of a maintainer ADD) | yes (Task 2) | |
| DP-2 | `_make_control`'s three callers flip a Factor **after** a Model or a rate table already pins it. Every reader resolves by id or by `slug@version` (Evidence). So "insert a `control` version" makes a new id that **no existing pin reaches**, and the three tests would lose their premise. What does the rewrite do? | **(a) Arrange before pin.** The control Factor version is inserted **before** the artifact that pins it is built. Caller `:270`: insert the control row, then `_seed_approved_model` pins it (`factor_versions=`, `test_api_rate_tables.py:197-229`, or `_ensure_factor` reusing the row, `:164-194`). Caller `:344`: fit the GBM on a control `area` Factor from the start (DP-3). No fit path refuses a `control` Factor: `git grep -nE 'intent.*control\|FactorIntent.CONTROL' -- backend/src packages/*/src` hits only `rate_tables/operations.py:218` and `rating/compile.py:786,823`. Caller `:299`: the seed path refuses a control Factor by design (`operations.py:218-222`). So the state "a pinned table key bound to a control Factor" is built by a direct **`INSERT`** of a new rate-table version whose key's `factor_ref` names a control Factor version, itself inserted. The executor mirrors the seeded version's own row (`test_rate_tables_service.py` `_version_row`) and never runs an `UPDATE`. This is the backstop state that FR-88's DP-3 says compile exists for. **(b)** Keep the in-place `UPDATE` and wrap it in `ALTER TABLE factors DISABLE TRIGGER factors_no_modify`. **(c)** Delete caller `:299` as unreachable. | **(a).** (b) has a test switch off the guard this slice adds, which is the loophole under another name. (c) removes a ruled backstop test. For caller `:299`, a new rate-table version row is **inserted**, never updated, even though `rate_table_versions` has no trigger today (Observation O-1). The test must not lean on a second loophole. | decision point | yes (Task 3) | |
| DP-3 | Caller `:344` needs a GBM fitted on a **control** `area` Factor. `_fitted_gbm` (`test_model_jobs_gbm.py:88-115`) makes its Factor through `_factor` (`test_model_jobs.py:193-204`), which takes no intent. Where does the intent enter? | **(a)** `_factor` gains `intent: FactorIntent = FactorIntent.RISK`, passed to `Factor(...)` (`model_schema` `FactorIntent`, `modelling.py:102-112`; `Factor.intent`, `:144`). `_fitted_gbm` gains `area_intent: FactorIntent = FactorIntent.RISK`, passed to `_factor`. The defaults keep every current caller unchanged. The write set widens by these two test files. **(b)** A local `_fitted_gbm_on_control_area` in `test_fr240_governance.py` that copies `_fitted_gbm`'s 25 lines with a control Factor. | **(a).** It is one keyword on each of two shared helpers, with defaults. A copied fixture diverges, and `README.md` convention 3 says not to reinvent a module's fixtures. | decision point (write set) | yes (Task 3) | |
| DP-4 | Which tables does the new "pinned artifact tables" assertion cover, and by what predicate? | **(a)** A written-out `PINNED_BODY_TABLES = ("bandings", "factors", "groupings")`: the modelling tables a Model spec pins by id and whose body is read at use (`02` FR-96, FR-101). Each must hold no `UPDATE` or `DELETE` for `gip_app` (`has_table_privilege`) **and** carry a row trigger and a statement trigger. **(b)** Every table an `ArtifactRef` resolves to: rate tables, reference tables, rating algorithms, sub-graphs and so on. **(c)** A set derived from the ORM (every table with `slug` and `version` columns), minus a written-out exemption map. | **(a) for this slice.** It checks both layers per table, so it also catches the case `FR-44`'s derived set cannot see: a table that kept `UPDATE`. (b) and (c) would be **red on the day they land** for tables outside this finding (O-1), so they would widen the slice past one migration. (c) is the long-term right answer, and it needs O-1 ruled first. The lead routes O-1. | decision point (scope) | no (default (a) in Task 3, step 3.4) | |
| DP-5 | The `FR-44` dated line: who authors the spec text? | **(a)** This plan drafts it verbatim (Task 4). The executor applies it through `spec-change` in the migration's commit, and the lead's GO, quoted in the `LG-`, adopts the text. **(b)** A decision-maker writes it as an `RL-`'s T-text. | **(a).** The maintainer (by delegation) already ordered the clarification as remedy step 5, "with the remedy shape as listed" (10:11:47). The text adds no requirement. It names the seventh table and the revision. | decision point | no (default (a); the lead may route (b) at the GO) | |
| DP-6 | How is the `downgrade()` proved? | **(a)** A recorded round trip on the executor's per-worktree database: `alembic downgrade -1`, then `alembic upgrade head` (`python-test` `SKILL.md:279`), with the grant and trigger query (Task 2, step 2.6) printed before, between and after, all in the `LG-`. **(b)** A `scratch_database` round-trip test in the form of `test_migration_deployments.py:348-375`. | **(a).** The downgrade restores one grant and drops two triggers, and (a) observes both. (b) is the fallback if the postgres-pro review asks for a standing test. | decision point | no (default (a)) | |
| DP-7 | `SL-1274` (WK-690 S4) also adds one Alembic migration (RL-8001's widening, confirmed 10:01:11). Both would chain from `d4e81b7a2c95`, which makes two heads. | The slice that merges **second** re-points its `down_revision` to the first one's revision. It then re-runs the single-head measurement (Task 2, step 2.1) before its ACK request. No merge migration. | as stated | fact (ordering) | no | |

**Observation O-1, for the lead to route (the planner files no finding).** Measured at
`1e260c15`, by the line-scoped predicate
`git grep -nE 'rate_table_versions|rate_table_cells|rating_algorithms|reference_table_versions|reference_rows|sub_graph_versions|regression_suite_versions' 1e260c15 -- backend/migrations/versions | grep -iE 'grant|revoke|trigger' | wc -l`,
the count is **0**. The three loop-form trigger migrations name these tables in none of
their tuples (`a1b2c3d4e5f6:41`, `e1f2a3b4c5d6:48,50`, `c3d4e5f6a7b8:113`). If that holds,
these pinned, versioned artifact tables carry neither of `FR-44`'s layers either. This plan
does not fix them. Whether that is a second `FD-` is the auditor's to verify by a run and
the lead's to route.

## Write set

| File | Change | Task |
|---|---|---|
| `backend/tests/test_artifact_immutability.py` | `factors` in `APPEND_ONLY_TABLES` and `_APPEND_ONLY_ROWS`; the `gip_app` test (DP-1); `PINNED_BODY_TABLES` and its test (DP-4) | 1, 2, 3 |
| `backend/migrations/versions/<rev>_factors_append_only.py` | **create**: one migration; `<rev>` is what `alembic revision` prints | 2 |
| `backend/tests/test_fr240_governance.py` | `_make_control` removed; its three callers arrange before pin (DP-2) | 3 |
| `backend/tests/test_model_jobs.py`, `backend/tests/test_model_jobs_gbm.py` | one defaulted keyword each (DP-3 (a) only) | 3 |
| `docs/specs/01-data-management.md` | `FR-44` row (`:106`): one dated line (DP-5) | 4 |
| `docs/ledgers/LG-<id>.md`, `docs/roadmap.md` (SL-8017's status line) | the slice's paperwork (Lean P2 L1) | all |

**Not in the write set:** `backend/src/**` (no application path writes `factors`, so no
service changes), `packages/**`, `docs/contracts/**` and the frontend.

## Tasks

### Task 1: the reds by cause, on the base tree

**Files:** Modify `backend/tests/test_artifact_immutability.py:38-52` and `:303-343`.

- [ ] **Step 1.1:** Insert `"factors",` into `APPEND_ONLY_TABLES` between `"diagnostics",` and
  `"groupings",`. The comment says *"Ordered as the database reports them"*, which is
  alphabetical.
- [ ] **Step 1.2:** Add a `factors` entry to `_APPEND_ONLY_ROWS`, in the `bandings` form and
  with the columns of `3ab4db71d0e8:33-45` (`created_at` has a server default):

```python
    #: **Added 2026-10-14 (WK-1178, SL-8017, FD-8007).** A Model pins its Factors by row id
    #: (`ModelSpecCommon.factors`), so an edited row re-prices every pinned fitted Model with
    #: the pin unchanged. No foreign key references `factors`, so a bare `TRUNCATE` reaches
    #: the trigger.
    "factors": (
        "INSERT INTO factors (id, workspace_id, dataset_id, slug, version, body) "
        "VALUES (:id, :ws, gen_random_uuid(), :slug, 1, :body)"
    ),
```

- [ ] **Step 1.3:** Run on the **base** tree, one file only (charter: no full suite):
  `uv run pytest backend/tests/test_artifact_immutability.py -q`. Expected, **each by its
  cause**. A matching failure with a different reason is a plan defect: stop and report.
  - `test_the_application_role_holds_only_select_and_insert` fails with
    `AssertionError: factors: ['INSERT', 'SELECT', 'UPDATE']`.
  - `test_every_table_the_grants_call_append_only_carries_both_triggers` fails at the guard
    (`:439`): the derived set lacks `'factors'`. The diff shows `'factors'` only on the
    right-hand side.
  - `test_an_artifact_cannot_be_rewritten_from_the_owner_connection[factors]` fails with
    `Failed: DID NOT RAISE` on the first statement, the `UPDATE` (zero triggers).
  - Every other test in the file passes.
  Paste the three failure lines into the `LG-`, with the tree.
- [ ] **Step 1.4:** Commit (the reds, test only).

### Task 2: one migration, and the DB-layer red (the ADD, DP-1)

**Files:** Create `backend/migrations/versions/<rev>_factors_append_only.py`. Modify
`backend/tests/test_artifact_immutability.py` (one new test after the owner-connection test).

- [ ] **Step 2.1:** Re-measure the head on `origin/main` at GO time with the Evidence predicate.
  Expected: one head, `d4e81b7a2c95` unless something merged since. If `SL-1274`'s migration
  merged first, its revision is the head (DP-7). Record the head in the `LG-`.
- [ ] **Step 2.2: write the DB-layer test first** (red on the base):

```python
@pytest.mark.req("FR-44")
async def test_a_gip_app_update_on_factors_is_refused_by_the_trigger_not_only_the_grant(
    database: Database, workspace_id
) -> None:
    """FD-8007 and the maintainer's ADD (10:11:47): the planted UPDATE is refused at the DB layer.

    Two observations, told apart by message and not by SQLSTATE (both are 42501):
    the grant refuses `gip_app` first, and the trigger refuses it again when a later
    migration grants `UPDATE` back. That second case is the one FR-44's derived set
    could not see.
    """
    row_id = new_uuid7()
    async with database.unit_of_work() as session:
        await session.execute(
            text(_APPEND_ONLY_ROWS["factors"]),
            {"id": row_id, "ws": workspace_id, "slug": f"s-{row_id.hex[-8:]}",
             "body": '{"stored": true}'},
        )
    planted = text("UPDATE factors SET body = '{\"rewritten\": true}' WHERE id = :id")

    # Layer 1: the grant.
    with pytest.raises(DBAPIError) as by_grant:
        async with database.session() as session:
            await session.execute(text("SET LOCAL ROLE gip_app"))
            await session.execute(planted, {"id": row_id})
    assert "permission denied for table factors" in str(by_grant.value)

    # Layer 2: the trigger, with layer 1 reopened inside this transaction only.
    with pytest.raises(DBAPIError) as by_trigger:
        async with database.session() as session:
            await session.execute(text("GRANT UPDATE ON factors TO gip_app"))
            await session.execute(text("SET LOCAL ROLE gip_app"))
            await session.execute(planted, {"id": row_id})
    assert "factors is append-only: UPDATE rejected (01 FR-42, FR-43)" in str(by_trigger.value)

    async with database.session() as session:
        leaked = (
            await session.execute(
                text("SELECT has_table_privilege('gip_app', 'factors', 'UPDATE')")
            )
        ).scalar_one()
        body = (
            await session.execute(text("SELECT body FROM factors WHERE id = :id"), {"id": row_id})
        ).scalar_one()
    assert leaked is False
    assert body == {"stored": True}
```

  The literals `database.session()`, `database.unit_of_work()`, `text`, `DBAPIError` and
  `new_uuid7` are this file's own imports (`:12-33`). Before running, confirm that
  `database.session()` leaves a failed transaction **uncommitted**, the property
  `test_transformations.py:538-551` already relies on. If it does not, the `GRANT` in the
  second block would persist. STOP and report: it is a premise of DP-1 (a).
- [ ] **Step 2.3:** Run only this test on the base. Expected: **red at the first
  `pytest.raises`, with `Failed: DID NOT RAISE`**, because `gip_app` holds `UPDATE` on the
  base. Any other reason is a plan defect. Then verify the cause in a scratch copy: delete the
  layer-1 block and rerun. Expected: red at the second block, again `DID NOT RAISE` (zero
  triggers). Revert the scratch edit, and paste both lines into the `LG-`.
- [ ] **Step 2.4: the migration.** Generate it with the DSN from `dev-commands` (the bare
  command does not use the local stack): `GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_<wt> uv run --directory <wt>/backend alembic revision -m "factors append only"`.
  Then replace the body with this:

```python
"""modelling: `factors` is append-only at the database (`01` FR-44, FD-8007)

`b2c3d4e5f6a7` granted `gip_app` `SELECT, INSERT, UPDATE ON models, factors` in one
statement. `models` needs `UPDATE` because `record_fit` writes the fit onto the reservation,
and that migration guards it with `models_fit_immutable`. `factors` rode on the same `GRANT`
with no such reason: no application path updates a `factors` row. `create_factor` takes
`max(version) + 1` and inserts, so an edit is a new version. The one in-repo `UPDATE
factors` was a test helper, `_make_control`, removed in the same change.

A Model pins its Factors by row id (`ModelSpecCommon.factors`), and fit, prediction and
rating resolve them by id at use (`load_factors`). An edited row therefore re-prices every
pinned fitted Model while the pin and every record stay unchanged. `FR-44`'s grants-derived
check could not see this, because a table that kept `UPDATE` falls outside the set by
construction.

Layer 1 is the `bandings` form (`c3d4e5f6a7b8`). Layer 2 is the `e1f2a3b4c5d6` form.
`artifact_append_only()` already exists (`a1b2c3d4e5f6`); this only attaches it. `DELETE`
was never granted on `factors`, and the revoke states it anyway, as the precedents do.

Revision ID: <rev>
Revises: <the head of step 2.1>
Create Date: <as generated>
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "<rev>"
down_revision: str | None = "<the head of step 2.1>"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.execute(f"REVOKE UPDATE, DELETE ON factors FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON factors FROM PUBLIC")
    op.execute("""
        CREATE TRIGGER factors_no_modify
          BEFORE UPDATE OR DELETE ON factors
          FOR EACH ROW EXECUTE FUNCTION artifact_append_only();
    """)
    # A row trigger does not fire on `TRUNCATE`, which is why the pair exists.
    op.execute("""
        CREATE TRIGGER factors_no_truncate
          BEFORE TRUNCATE ON factors
          FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS factors_no_truncate ON factors")
    op.execute("DROP TRIGGER IF EXISTS factors_no_modify ON factors")
    # Exactly `b2c3d4e5f6a7`'s state: `UPDATE` granted, `DELETE` never was.
    op.execute(f"GRANT UPDATE ON factors TO {APP_ROLE}")
```

  The three angle-bracket values are the ones `alembic revision` prints and step 2.1 measured.
  They are generated, not chosen.
- [ ] **Step 2.5:** `alembic upgrade head` on the per-worktree database, with the `dev-commands`
  DSN. Then run `alembic heads`. Expected: exactly one head, `<rev>`.
- [ ] **Step 2.6: the layers, observed.** Print this into the `LG-`, after upgrade:
  `SELECT privilege_type FROM information_schema.table_privileges WHERE grantee = 'gip_app' AND table_name = 'factors' ORDER BY 1;`
  (expected `INSERT`, `SELECT`), and
  `SELECT tgname FROM pg_trigger WHERE tgrelid = 'factors'::regclass AND NOT tgisinternal ORDER BY 1;`
  (expected `factors_no_modify`, `factors_no_truncate`). Run them through `docker exec
  gi-pricing-postgres-1 psql -U gipricing -d gipricing_<wt> -c '…'`, because the host has no
  `psql` client (`dev-commands`).
- [ ] **Step 2.7: the downgrade (DP-6 (a)).** Run `alembic downgrade -1`, then step 2.6
  (expected `INSERT`, `SELECT`, `UPDATE`; no rows from `pg_trigger`), then `alembic upgrade
  head`, then step 2.6 again. All three outputs go into the `LG-`.
- [ ] **Step 2.8:** `uv run pytest backend/tests/test_artifact_immutability.py -q`. Expected:
  all green, including Task 1's three and step 2.2's test.
- [ ] **Step 2.9: the loophole bites.** Before Task 3, run
  `uv run pytest backend/tests/test_fr240_governance.py -q -k control`. Expected: the three
  `_make_control` callers fail with `factors is append-only: UPDATE rejected (01 FR-42,
  FR-43)`, because they run as the owner, so the trigger refuses them. This is the proof that
  the trigger covers the owner connection the application uses. Paste it into the `LG-`, then
  commit the migration and the test.

### Task 3: `_make_control` removed, and the pinned-tables assertion

**Files:** Modify `backend/tests/test_fr240_governance.py:248-366`;
`backend/tests/test_model_jobs.py:193-204` and `backend/tests/test_model_jobs_gbm.py:88-115`
(DP-3 (a) only); `backend/tests/test_artifact_immutability.py` (DP-4).

- [ ] **Step 3.1: a control version, inserted.** Replace `_make_control` (`:248-256`) with a
  helper that inserts a new version and returns its number. Mirror `_ensure_factor`'s body
  construction (`test_api_rate_tables.py:164-194`): a `Factor(..., intent=FactorIntent.CONTROL)`
  dumped with `exclude={"id", "version", "dataset_id"}`, at version `max(version) + 1` for
  the slug in the workspace (1 if none). No `UPDATE` appears in the file afterwards:
  `grep -nE 'UPDATE factors|factors SET' backend/tests/test_fr240_governance.py` prints
  nothing.
- [ ] **Step 3.2: caller `:270` (seed route).** Insert the control version **before**
  `_seed_approved_model`, and pin it with `factor_versions={"driver_age_band": <n>}`.
  Expected: still `422` with `CONTROL_FACTOR_IN_RATEABLE_PATH`.
- [ ] **Step 3.3: caller `:344` (GBM).** Pass `area_intent=FactorIntent.CONTROL` to
  `_fitted_gbm` (DP-3 (a)), and drop the flip. Expected: the fit still `SUCCEEDED`, and compile
  still `FAILED` with `CONTROL_FACTOR_IN_RATEABLE_PATH`. **If the fit refuses a control
  Factor, STOP:** the grep in DP-2 found no such refusal, so a refusal would show that premise
  is false.
- [ ] **Step 3.4: caller `:299` (compile over a control-keyed table).** Seed as today. Insert
  a control version of `driver_age_band`. Then **insert** a new rate-table version row that
  copies the seeded one, with its key's `factor_ref` naming the control version, and pin
  that version in `_compile_with_pins`. Read the row shape from `_version_row`
  (`test_rate_tables_service.py`) and `RateTableVersionRow`; do not write the columns from this
  plan. Update the docstring: the seed path refuses a control Factor, so this state is built
  by insert, and compile is its backstop (FR-88 DP-3). Expected: `FAILED` with
  `CONTROL_FACTOR_IN_RATEABLE_PATH`.
- [ ] **Step 3.5: the broken-input proof for 3.2 to 3.4.** In a scratch edit, insert each
  version with `FactorIntent.RISK`. Each test must then fail by its cause: the refusal code is
  absent. Revert, and record in the `LG-`.
- [ ] **Step 3.6: the pinned-tables assertion (DP-4 (a)).** In `test_artifact_immutability.py`:

```python
#: The modelling tables a Model spec pins by row id, whose body is read at use (`02` FR-96,
#: FR-101). FR-44's derived set cannot see a table that kept `UPDATE` (FD-8007: `factors`
#: rode `models`' grant), so this checks both layers per table and does not derive the set.
PINNED_BODY_TABLES = ("bandings", "factors", "groupings")


@pytest.mark.req("FR-44")
async def test_every_pinned_body_table_refuses_update_at_both_layers(database: Database) -> None:
    async with database.session() as session:
        for table in PINNED_BODY_TABLES:
            for privilege in ("UPDATE", "DELETE"):
                held = (
                    await session.execute(
                        text("SELECT has_table_privilege('gip_app', :t, :p)"),
                        {"t": table, "p": privilege},
                    )
                ).scalar_one()
                assert held is False, f"{table}: gip_app holds {privilege}"
            kinds = {
                row[0]
                for row in (
                    await session.execute(
                        text(
                            "SELECT t.tgtype & 1 FROM pg_trigger t "
                            "WHERE t.tgrelid = CAST(:t AS regclass) AND NOT t.tgisinternal"
                        ),
                        {"t": table},
                    )
                ).all()
            }
            assert kinds == {0, 1}, f"{table}: trigger kinds {sorted(kinds)}"
```

  `tgtype & 1` is the row/statement bit the derived test already reads (`:418-419`).
  Broken-input proof: run it on the Task 1 commit (before the migration). Expected: red with
  `factors: gip_app holds UPDATE`. Record the line.
- [ ] **Step 3.7:** Run the four touched test files, one at a time, plus `-k control` on
  `test_fr240_governance.py`. All green. Commit.

### Task 4: the `FR-44` dated line (DP-5 (a)), in the migration's commit range

**Files:** Modify `docs/specs/01-data-management.md:106`, appending at the end of the `FR-44`
cell.

- [ ] **Step 4.1:** Append, through `spec-change`. `<date>` is the commit date and `<rev>` is
  Task 2's revision:

  `*(Amended <date>, WK-1178 SL-8017, on FD-8007.)* **`factors` is the seventh table, and the derived set could not see it:** `b2c3d4e5f6a7` granted `gip_app` `UPDATE` on it beside `models`, with no trigger, so it fell outside the grants-derived set by construction. `<rev>` revokes `UPDATE, DELETE` and attaches both triggers; `APPEND_ONLY_TABLES` names it, and a both-layers check over the pinned modelling tables does not derive its set.`

  Escape any `|` as `\|`, since this is a table cell.
- [ ] **Step 4.2:** `python3 scripts/audit-docs.py` (as one gate-2 docs check) and
  `uv run python scripts/req-coverage.py`. Commit.

### Task 5: the gate, and the postgres-pro review

- [ ] **Step 5.1:** Delegate the migration to the `postgres-pro` agent, read-only, as review
  evidence (it decides nothing). The brief names: (i) the `dev-commands` DSN trap: the bare
  `alembic` command does not use the local stack, so every command carries `GIP_DATABASE_URL`;
  (ii) a single head after upgrade (step 2.5), and `DP-7` if `SL-1274` merged first; (iii)
  the downgrade restores exactly `b2c3d4e5f6a7`'s grant and no more; (iv) the trigger form
  matches `e1f2a3b4c5d6` byte for byte apart from the table name; (v) `REVOKE … FROM PUBLIC`
  is a no-op on a fresh database and is kept for parity. Its findings go into the `LG-`. A
  finding that changes the migration is a dated delta line in the `LG-`, not a silent edit.
- [ ] **Step 5.2:** The full gate, both halves, in a gate slot (`dev-commands`; this slice
  touches no frontend file, and the frontend half still runs). Record the rc table in the
  `LG-`.

## Acceptance Standard

Each item can be checked by a fresh reviewer at the slice PR's merge tree, with the range
`origin/main...<slice branch>` named.

1. **Reds by cause on the base:** the `LG-` carries, at the named base tree, the three Task 1
   failure lines (step 1.3), the two DB-layer failure lines (step 2.3), the `-k control`
   trigger failures (step 2.9), and the `PINNED_BODY_TABLES` red (step 3.6). Each one names
   its cause as this plan predicts.
2. `uv run pytest backend/tests/test_artifact_immutability.py -q` is green on the merge tree,
   and `test_a_gip_app_update_on_factors_is_refused_by_the_trigger_not_only_the_grant`
   asserts both messages verbatim: `permission denied for table factors` and `factors is
   append-only: UPDATE rejected (01 FR-42, FR-43)`.
3. `git grep -nE 'UPDATE factors|factors SET' <merge tree> -- backend packages scripts`
   prints nothing.
4. `uv run pytest backend/tests/test_fr240_governance.py -q` is green, and step 3.5's
   broken-input lines are in the `LG-`.
5. Exactly one new file under `backend/migrations/versions/`. `alembic heads` prints one
   head. The `LG-` carries the step 2.6 and 2.7 outputs (upgrade, downgrade, upgrade).
6. `docs/specs/01-data-management.md` `FR-44` carries Task 4's dated line, in the same PR as
   the migration.
7. The postgres-pro review is in the `LG-` (step 5.1). The full gate rc table is all 0
   (step 5.2), and `python3 scripts/audit-docs.py` exits 0 on the merge tree.
8. **Due before the 4 Nov P2 code freeze** (the maintainer (by delegation), 10:11:47).

## Activation needs

- **`FD-8007` minted on `main`** (it rides the D15 batch, `c787c522`). The slice's `LG-`,
  test docstrings and migration docstring cite its minted id, not working id 8007.
- `RL-8001` minted. Only cited; nothing waits on it.
- DP-1, DP-2 and DP-3 resolved by a dated line (the lead's GO, or the maintainer (by
  delegation)) and quoted in the `LG-`. This plan stays `draft` until then (`document-ids.md`
  §1.6, PL row).
- A gate slot for step 5.2.

## Self-review

- **Every remedy item has a task:** `APPEND_ONLY_TABLES` (T1); the grant and trigger reds
  (T1.3); one migration with its downgrade (T2.4, T2.7); the DB-layer `gip_app` red (T2.2,
  T2.3; DP-1); `_make_control` (T3; DP-2, DP-3); the pinned-tables assertion (T3.6; DP-4);
  `FR-44` (T4; DP-5); postgres-pro (T5.1).
- **Literals checked against the source at `1e260c15`:** the trigger message
  (`a1b2c3d4e5f6:46-47`), the `factors` columns (`3ab4db71d0e8:33-45`), `FactorIntent.CONTROL`
  (`modelling.py:112`), `_seed_approved_model(..., factor_versions=)` (`test_api_rate_tables.py:197-203`),
  `_factor`'s signature (`test_model_jobs.py:193`), and the head `d4e81b7a2c95`. Not checked,
  and named instead of supplied: the rate-table version row shape (step 3.4), and PostgreSQL
  16's privilege message, which step 2.3's red prints before step 2.8 relies on it.
