---
id: FD-8007
family: finding
title: The factors table is not append-only at the database, so a row edit re-prices every pinned fitted Model with the pin unchanged
status: active
created: 2026-10-14
owner: auditor
tree: 1e260c1553acf39844939fe12da685ccfb835e54
corrected_by: []
relates: [WK-1178, WK-690, SL-1274, RL-8001, RL-1615, FD-1619, FD-1660, FD-1679, FR-43, FR-44, FR-96, FR-87, P2]
---

# FD-8007 — the `factors` table is not append-only at the database

*(Filed under working id 8007, reserved by the lead; a minter folds it into the docs batch. Every
`file:line` below was read at `origin/main` `1e260c1553acf39844939fe12da685ccfb835e54` unless it names
another tree. The raising evidence is the seat's entry "2026-10-14 10:01:32 BST" in
`channel/from-dm-wk690-47.md` and the draft `RL-8001` at `origin/rl-8001-wk690-s4-47-2026-10-14`
@`f3cad285`; the claims were re-read against the primary files, not copied.)*

## Finding

**Proposed severity: MEDIUM, owner WK-1178** (the auditor proposes; the lead and the maintainer
(by delegation) rule). Authority for the filing: the maintainer's (by delegation) entry
"2026-10-14 10:01:11 BST — RL 8001 (WK-690 S4, PL-1665 4.7) CONFIRMED as drafted; FD 8007 (factors
not append-only) to file" in `channel/to-lead.md`. It says an auditor files it and proposes the
severity, that the owner is WK-1178, that the fix is its own row and not WK-690 S4, that it is to be
weighed against FD-1660 and FD-1679, and that the fix lands before the P2 code freeze. Its text on
the weighing, verbatim: *"a direct row edit silently changes how every pinned fitted Model scores,
with the pin unchanged (RL 8001's own words), so weigh it against FD-1660/FD-1679's "silent wrong
evidence or price" class. The fix (revoke + `artifact_append_only` triggers + APPEND_ONLY_TABLES +
`_make_control` rewrite) is scheduled before the P2 code freeze, owing to FR-44 "Every artifact table
carries both layers"."*

`factors` is the one artifact table of the modelling module that has neither layer of FR-43/FR-44. A
Model pins its Factors by row id, and a fitted Model's spec cannot change, so the *pin* is immutable
and the *thing pinned* is not. The application never edits a `factors` row, so nothing is wrong on
`main` today by an ordinary call. The database is what is meant to say so (`FR-43`), and it does not.

## Evidence

### 1. The grant: `UPDATE` on `factors` is given to the application role

`backend/migrations/versions/b2c3d4e5f6a7_model_fit_immutable.py:89`:

```python
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON models, factors TO {APP_ROLE}")
```

The line belongs to a migration about `models` (its docstring, `:1-12`, is about the fitted-model
guard). `models` needs `UPDATE` because `record_fit` writes the fit onto the reservation, and the
migration answers that with a conditional trigger (`models_fit_immutable`, `:32-50`). `factors` rides
on the same `GRANT` and has no such reason: no application path updates it (item 4).

### 2. No revoke and no trigger anywhere

```bash
git -C /home/puzhenhao1989/gi-pricing-plan grep -nE 'factors' origin/main -- backend/migrations/versions | grep -iE 'revoke|trigger|grant|create table|artifact_append'
```

At `origin/main` `1e260c15` it prints **one line**, the grant above (`b2c3d4e5f6a7:89`). The predicate
is `factors` on a migration line that also names `revoke`, `trigger`, `grant`, `create table` or
`artifact_append`, case-insensitive; the table's own `op.create_table('factors', …)` is spelt with an
underscore and is not matched, so it is not counted. There is no `REVOKE` on `factors`, and no
`CREATE TRIGGER … ON factors`. By contrast the peers
carry both layers:

- `bandings` and `groupings` (`c3d4e5f6a7b8_modelling_bandings_and_groupings.py`, the `REVOKE UPDATE,
  DELETE` at `:111-112` and the `TRUNCATE` guard at `:115-117`), the row trigger added by
  `e1f2a3b4c5d6_artifact_row_triggers.py:48-66`, whose `NO_TRIGGERS` (`:48`) and `TRUNCATE_ONLY` (`:50`)
  tuples name six other tables and not `factors`.
- `models` (`b2c3d4e5f6a7:71-90`): a conditional update guard, an undeletable-when-fitted guard and a
  `TRUNCATE` guard.

`DELETE` is not granted to `gip_app` on `factors` (the `GRANT` at `:89` omits it), so the application
role can `UPDATE` but not `DELETE`. Nothing stops `TRUNCATE` or an owner-level `UPDATE` or `DELETE`,
because there is no `artifact_append_only` trigger on the table. `FR-43`'s own reasoning applies
(`FR-44`'s first sentence): *"revoking `UPDATE` from the *owner* does nothing — ownership carries
implicit privileges"*.

### 3. The test that should notice, cannot

`backend/tests/test_artifact_immutability.py:38-52` lists `APPEND_ONLY_TABLES`: `audit_events`,
`backtests`, `bandings`, `deployments`, `diagnostics`, `groupings`, `metric_certificates`,
`model_comparisons`, `objective_certificates`, `profiles`, `transparency_artifacts`,
`validation_acknowledgements`, `validation_reports`. **`factors` is not in it.**

That is not an oversight in a list. `FR-44` (`docs/specs/01-data-management.md:106`) states the
invariant as *"a table whose grants are exactly `SELECT, INSERT` is a table the schema has declared
append-only, and it must carry both triggers"*, and the test derives its table list from the grants
(`test_every_table_the_grants_call_append_only_carries_both_triggers`, `:397-439`, whose guard
against a quiet query is `:439` `assert {row[0] for row in rows} == set(APPEND_ONLY_TABLES)`). `factors` carries `UPDATE`, so it falls **outside the derived set by
construction**: the invariant's own predicate selects the tables that already comply and cannot see
one that was never narrowed. `FR-44`'s count was already wrong once for this reason (*"three do not",
then six*); `factors` is the seventh, and the measurement that found six used the grants too.

### 4. No application path updates a `factors` row

```bash
git -C <tree> grep -n 'FactorRow' origin/main -- backend/src
```

At `1e260c15` every use is a class definition (`db/models.py:1315`), an import, a `select(FactorRow…)`
(`modelling.py:239,272,278,313,360`; `model_specs.py:436`; `rating_versions.py:762`) or one constructor
(`modelling.py:246`, inside `create_factor`, which takes `max(version) + 1` at `:239` and inserts a new
row). Editing a Factor creates a new version. The one in-repo `UPDATE factors` is a **test**:
`backend/tests/test_fr240_governance.py:248-256`, `_make_control`:

```python
"UPDATE factors SET body = jsonb_set(body, '{intent}', '\"control\"') "
"WHERE workspace_id = :w AND slug = :slug"
```

whose docstring says it flips the Factor *"the way a later edit would"*. That is the only writer, and
it works because the grant allows it. Fixing the grant makes this helper fail, which is correct: the
helper must create a `control` version instead (`RL-8001`'s proposal).

### 5. How a Factor is pinned, and what an edit does to a pinned Model

- A Model pins its Factors **by row id**: `ModelSpecCommon.factors: tuple[UUID, ...]`
  (`packages/model-schema/src/model_schema/modelling.py:835`).
- One `factors` row is one version of one slug with its own id (`FactorRow`, `db/models.py:1315-1338`,
  `uq_factors_slug_version`). `FR-96` (`02-modelling.md:99`): *"a Model Spec pins the exact Factor
  version it used"*. The id therefore identifies one version.
- A fitted Model's spec cannot change: the `models_fit_immutable` trigger freezes `fit_result`, `spec`,
  `spec_hash` and `dataset_version_id` once the model is fitted (`b2c3d4e5f6a7:32-50`).
- Fit, prediction and rating resolve the pinned Factors **by id at use time**: `load_factors`
  (`backend/src/app/platform/modelling.py:286`, `_load` at `:310-320`, `by_id[fid]` at `:331`). `RL-8001`'s
  table lists the callers (`worker/model_handlers.py`, `platform/prediction.py:130,511`,
  `platform/rating_algorithms.py:140`); that call list is the draft's and was not re-enumerated here.

So `UPDATE factors SET body = …` rewrites what an unchanged, immutable pin resolves to. A Factor body
is a transformation (`02` §4.1): an `expression` formula, a banding reference, a spline or polynomial
parameter set. The fitted coefficients were estimated against the old body and are applied to the new
one. The Model's own record (`spec`, `spec_hash`) still shows the old pin, and the Rating Version
that pins the Model still shows its own pin. Nothing in any record changes except the price.

This is the same defect class the repository has already met twice at one remove: the migration
`b2c3d4e5f6a7` begins with *"An audit rewrote a stored coefficient from 0.6931 to 0.0 with a raw
`UPDATE`"*; `FR-43`'s origin is *"rewriting 190 stored reports from `fail` to `pass` in one
statement"* (`test_artifact_immutability.py:1-8`). `RL-1615` is the stale-band version, and
`RL-8001` calls this *"`RL-1615`'s stale-band class one level up"*.

## Severity: the proposal and its reasoning against FD-1660 and FD-1679

Both reference findings are HIGH (register rows for FD-1660, entry "2026-10-12 02:35:40 BST", and
FD-1679, entry "2026-10-12 05:43:54 BST"). The maintainer's (by delegation) own reason for HIGH in
FD-1679 was: *"That is silently wrong approval evidence … Consistency requires HIGH."* The three
share the **consequence**: a silent wrong value an approver or a customer relies on, with every
visible record unchanged. They differ on the **precondition**:

| | FD-1660 | FD-1679 | FD-8007 |
|---|---|---|---|
| Reachable by an ordinary API call on `main` | yes (a partial subset that compiles against another sub-graph version) | yes (two valid pins of one slug, `RL-1538`) | **no**: no application path updates `factors` (item 4) |
| What it takes | normal operation | normal operation | a write path the application does not have: a SQL injection, a defect that adds an `UPDATE`, a direct connection, or a support script |
| Who sees the wrong value | an approver, as evidence | an approver, as evidence | every quote scored on every Model pinning that row |
| Is the layer the spec calls for missing | n/a | n/a | **yes**: `FR-44` is not met for this table |

**Proposed MEDIUM**, for these reasons:

1. HIGH was awarded in the two reference findings for being *reachable and silent under ordinary
   use*. This one is silent when it happens and not reachable by ordinary use, so the likelihood
   half of the rating is lower and the impact half is the same or higher.
2. It is a spec non-conformance with a defence-in-depth purpose: `FR-43` exists because a rule about
   one process (the application) is not a rule about the data. The application-layer rule holds today
   and the data-layer rule is absent.
3. The remedy is small, mechanical and precedented (`e1f2a3b4c5d6` did six tables), and it is already
   scheduled before the P2 code freeze, so the exposure window is bounded.

**Re-rate trigger, to HIGH:** any application path, migration or script found to issue `UPDATE` or
`DELETE` on `factors`, or any route that lets a caller change a stored Factor body. Equally, if the
maintainer (by delegation) weighs the demonstrated precedents above (a raw `UPDATE` actually run
by an audit against `models` and against `validation_reports`) as making the direct-write limb
likely rather than hypothetical, HIGH is a defensible reading, and the auditor puts that choice to the
lead rather than hiding it. What the auditor does **not** propose is LOW: the consequence is a
changed price with an unchanged pin, which is the platform's mispricing class (`CLAUDE.md` §7).

## Disposition

**Fix before close with an owner: WK-1178**, as **its own row** (the maintainer's (by delegation)
entry "2026-10-14 10:01:11 BST"; not `WK-690` S4, whose write set `RL-8001` already widens by one
migration). **It lands before the P2 code freeze** (`FR-44`). Needs a resolution before any P3 start
(`CLAUDE.md` §14).

**Remedy shape, red first** (a proposal for the planner and the slice's executor; this finding fixes
nothing):

1. **Red first.** Add `factors` to `APPEND_ONLY_TABLES` in `backend/tests/test_artifact_immutability.py`
   *before* the migration, with the two observations the existing tests make for every member: a grant
   assertion that `gip_app` holds exactly `SELECT, INSERT` on it (`test_the_application_role_holds_only_select_and_insert`,
   `:267`), and the trigger tests that `UPDATE`, `DELETE` and `TRUNCATE` are refused
   (`:348`, `:397`). Both must fail on `main` by their
   causes (the grant is `SELECT, INSERT, UPDATE`; zero triggers).
2. **One Alembic migration:** `REVOKE UPDATE, DELETE ON factors FROM gip_app` and `FROM PUBLIC`;
   attach `factors_no_modify` (`BEFORE UPDATE OR DELETE … FOR EACH ROW`) and `factors_no_truncate`
   (`BEFORE TRUNCATE … FOR EACH STATEMENT`), both `EXECUTE FUNCTION artifact_append_only()`, the
   form `e1f2a3b4c5d6` uses; a matching `downgrade()`. The migration must say in its docstring why
   `b2c3d4e5f6a7:89` included `factors` and that no application path needed the grant.
3. **`_make_control` rewritten** (`test_fr240_governance.py:248-256`) to create a `control` version
   by insert instead of editing a row, so no test relies on the loophole it closes.
4. **Measure the invariant, not the list.** `FR-44`'s derived set cannot see a table that kept
   `UPDATE`. The slice should add one assertion that enumerates the tables in the modelling module
   that hold a body or a definition a pin resolves to (`factors`, `bandings`, `groupings`, and the
   other pinned artifact tables) and fails on any that grants `UPDATE`, so the next table that rides
   a neighbour's `GRANT` fails a test on the day it is added. This is the lesson of item 3.
5. **A one-line `FR-44` clarification** that `factors` is the seventh table (`spec-change`), in the
   same commit as the migration.

**Event that next confirms or discharges it:** the fix slice's merge with the red of step 1 shown
failing on the base tree by its causes and green after, and `python3 scripts/audit-docs.py` and the
full `test_artifact_immutability.py` green on the merged tree.

## Addition 2026-10-14: FR-70 joins the artifact-immutability set

FR-70 is immutable by route absence only: no route edits the artifact, and nothing at the database or in a test says so, which is the class this finding names for `factors`. The maintainer (by delegation), "2026-10-14 11:06:52 BST" item 2 in `to-lead.md`, ruled: *"FR-70 is NOT in that FD [FD 8027]: immutability by route absence only is FD 8007/O-1's class. It joins that finding's table set (the artifact-family derivation), with one remedy."* The lead relayed it at "2026-10-14 11:07:28 BST" (`from-lead-2026-10-09.md`): "FR-70 instead joins FD 8007/O-1's artifact-immutability set". So FR-70 is added to the set that remedy step 4 (measure the invariant, not the list) derives from the artifact family, and it takes the one remedy of this finding, not a separate one. This addition changes no severity and no owner (MEDIUM, WK-1178). It is an auditor-owned edit before the finding mints; the FR-70 limb has not been line-read here, and WK-1178's plan delta is where its table row is derived.
