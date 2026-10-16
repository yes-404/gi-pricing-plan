---
id: LG-8062
family: ledger
title: WK-690 slice SL-1274 — S4, expression Factors (PL-1621, PL-1665), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-16
owner: executor
tree: 81fabac462f4c8c6cee901b07aae85bfad334522
phase: P2
work: WK-690
slice: SL-1274
plans: [PL-1621, PL-1665, PL-1268]
corrected_by: []
relates: [PL-1621, PL-1665, PL-1268, SL-1274, RL-1615, RL-1700, FD-1704, FD-1619, FR-95, FR-97, FR-208]
---

# LG 8062 — SL-1274: expression Factors

Working id 8062 (space form, unminted). Branch `sl-1274-wk690-s4-factor-expression`, worktree
`.claude/worktrees/sl-1274`, base `origin/main` `0877e6e7`. Plans `PL-1621` row 1, `PL-1665` S4 (4.1′, 4.3′,
4.4′, 4.7), `PL-1268` Slice 4; bindings `RL-1615`, `RL-1700`.

**GO:** the maintainer's entry "2026-10-16 09:51:01 BST — GO SL-1274 BUILD (WK-690 S4, factor expressions)" in
`to-lead.md`, with the lead's request "2026-10-16 09:50:29 BST" in `from-lead`. Conditions:

1. One test fails if the ORM and the migrated column disagree on nullability:
   `test_the_orm_and_the_migrated_column_agree_that_column_name_is_nullable`
   (`backend/tests/test_expression_factors_api.py`).
2. DP-7 extended: this slice's migration `f2b6d90a4c17` has `down_revision` `d4e81b7a2c95`, the head at base.
   `SL-1722` adds `e7c3a9b15d82` on the same parent, and `SL 8017` may too. Whichever merges second
   re-points `down_revision` before its gate. A post-gate re-point is the only allowed post-gate code
   change, proved in a small-test slot (upgrade head, single-head test, `downgrade -1 && upgrade head`;
   return codes recorded here).
3. The activation line is in `docs/roadmap.md`'s `SL-1274` row, in this PR (lean L1).
4. FD-1704's fix is not this slice's (`PL 8016` S-a and S-b).

**Write set** (widened by the lead at the GO, `RL-1700`): one Alembic migration; `banding.schema.json`;
`pricing_core/modelling/bandings.py`; `rate_tables/weights.py` and its test; `03` FR-228's clause; `02`'s texts;
`platform/transformations.py`; the banding routes of `api/models.py` (no edit was needed: they pass the
model-schema shapes through); `db/models.py`. Widened again by the lead (from-lead, 2026-10-16 ~09:58 BST) by
one path, `pricing_core/data/expressions.py`: an optional `symbols` parameter on `referenced_columns`, default
`None` and unchanged. `RL-1700` (a) names it: *"Those paths must parse with the Factor's `source_columns` as
symbols, or `referenced_columns` gains a `symbols` argument. Either way there is one parser."* Paths named by
`PL-1665` itself: `factors.py` (:130, :354), `platform/modelling.py` (:146, :356), `model_schema/modelling.py`
(:116), `02-modelling.md` (:36, :115), regenerated `docs/contracts/` (:117).

**MERGE-ACK:** not yet given.

## Tasks

- **T1 — 4.1′ spec first, in the code's commit.** `02` FR-95, FR-97, FR-208, §4.1, §4.2, the §4.8 note
  (`RL-1700`, exact text) and `03` FR-228 (`RL-1700`, exact text). Shapes in `model_schema/modelling.py`
  (`Factor`, `Banding`, `BandingProposal`; `BandingEvaluation` carries a `Banding`).
  Written; `generate-contracts.py` and `--check` owed after GATE END.
- **T2 — 4.3′ creation, resolution and arms.** Red-first files (branch `49ce73b9`): `test_factor_expression.py`,
  `test_expression_factors.py`, `test_expression_factors_api.py`. Code: `factors.py`, `bandings.py`,
  `platform/modelling.py`.
- **T3 — 4.4′ audit.** `factor.created` carries `expression`, `banding.created` carries `source_expression`.
- **T4 — 4.7 (`RL-1700` C′).** `test_a_fitted_models_pin_returns_the_posted_expression_and_a_new_version_does_not_move_it`
  (steps 1–4 over HTTP).
- **T5 — `RL-1700` (c).** Migration `f2b6d90a4c17`, `BandingRow.column_name` nullable, contract, readers narrowed,
  `weights.py` refusal with its test.
- **T6 — gate and proofs**, after GATE END (owed, not run): see Build log.

## Build log

- 2026-10-16 09:5x BST — build written, **nothing run**: the lead's latency window (SL-1455's ALONE gate) bars
  uv, pytest, mypy, ruff and docker. Pushed heads: `32af19f7`, `a4076b17`, `154d4301`.
- Owed after GATE END: (1) every red shown red by its own assert then green, quoted here; (2) `uv run python
  scripts/generate-contracts.py` and `--check`; (3) ruff, mypy; (4) audit-docs and doc-index under the gate-2 flock;
  (5) the migration round trip in a granted DB window, return codes here; (6) the single-head test.
- Disclosure: two stray `cd` calls in Bash (2026-10-16 ~09:5x); the session cwd was restored with EnterWorktree.

## Pre-gate self-check — 2026-10-16 (writing only, nothing run)

Read against the maintainer's "2026-10-16 09:51:01 BST" items 1–4 and "09:53:28 BST" first bullet, at tree
`origin/main...sl-1274-wk690-s4-factor-expression` (base `0877e6e7`). Locators are paths in this branch.

| # | Condition | Status | Locator |
|---|---|---|---|
| 09:51 item 1 (CONDITION 1) | A test fails if the ORM and the migrated column disagree on nullability | Present. It asserts `BandingRow.__table__.c.column_name.nullable is True`, then inserts a `BandingRow(column_name=None)` through the ORM and flushes. The `database` fixture (`backend/tests/conftest_db.py:172`) skips unless `alembic_version` has rows, so the insert runs on the migrated schema. An ORM `nullable=False` fails the first assert. A column still NOT NULL fails the flush. Red-first run owed. | `backend/tests/test_expression_factors_api.py:431` (`test_the_orm_and_the_migrated_column_agree_that_column_name_is_nullable`); ORM `backend/src/app/db/models.py:1358` (`Mapped[str \| None]`, `nullable=True`); migration `backend/migrations/versions/f2b6d90a4c17_bandings_column_name_nullable.py` |
| 09:51 item 2 | FD-1704's fix stays in PL 8016 S-a/S-b | Honoured: no `FD-1704` code in this slice (write-set STOP list below). | this ledger, condition 4 |
| 09:51 item 3 (DP-7) | Whichever of SL-1274, SL-1722, SL 8017 merges later re-points `down_revision` | Owed, see "DP-7 re-point owed" below. | below |
| 09:51 item 4 | Activation line in the slice PR citing this GO | Present, citing the GO and the lead's request. | `docs/roadmap.md:1712` |
| 09:53 bullet 1 | `referenced_columns(symbols=None)`: one parse path | Present. The call is `parse_expression(expression, profile, symbols=symbols, limits=limits)`, so there is no second walk. | `packages/pricing-core/src/pricing_core/data/expressions.py:308-320` |
| 09:53 bullet 1 | Default-unchanged test in LG 8062 | Present. The recipe call is as before. The `factor` profile without `symbols` still raises `bound symbols`. The `symbols` call returns the read columns. | `packages/pricing-core/tests/test_expression_factors.py:275` (`test_referenced_columns_default_is_unchanged_and_the_symbols_call_resolves`); the old `test_prepare.py:108` and `test_expression_nfrs.py:73` stay unedited |
| 09:53 bullet 1 | Write-set STOP list: `factors.py`, `platform/modelling.py`, `model_schema/modelling.py`, `02` | None of the four is a STOP: `PL-1665` names all four (see "Write set" above), so the lead's widening was not needed for them. All four are in the diff. | `git diff --stat origin/main...HEAD` |

**Write-set check.** Every changed path is in the "Write set" list above except
`packages/pricing-core/src/pricing_core/modelling/__init__.py`. It only re-exports the three names the slice
adds (`is_certainly_numeric`, `normalised_expression`, `source_columns_of`). It is reported to the lead as a
path in no list; if the lead rules it outside the write set, the fix is to import from the module and drop
the re-exports.

**Contracts.** Only `docs/contracts/schemas/banding.schema.json` is in the diff, but `Factor`,
`BandingProposal` and `BandingEvaluation` changed in `model_schema/modelling.py`. `generate-contracts.py`
may change more files. Owed; the `--check` result decides.

### DP-7 re-point owed

- This slice's migration `f2b6d90a4c17` has `down_revision` `d4e81b7a2c95`. That is the head at `origin/main`
  `0877e6e7` and the `down_revision` of `e7c3a9b15d82` on `origin/sl-1722-wk1178-fd1730-upload-404`
  (`backend/migrations/versions/e7c3a9b15d82_blob_uploads.py:23`). Two heads follow if both merge unchanged.
  `tests/test_repository_invariants.py:357` (`test_the_migration_chain_has_exactly_one_head`) then reds.
- Owed by whichever of SL-1274 and SL-1722 merges later (and SL 8017 if it adds a migration): set
  `down_revision` to the earlier one's revision before its gate. This is the only allowed post-gate code
  change if the earlier merges after the later is gated.
- Proof it needs, in a small-test slot (RL-1626), with return codes recorded here: `alembic upgrade head`,
  `tests/test_repository_invariants.py::test_the_migration_chain_has_exactly_one_head`, and
  `alembic downgrade -1 && alembic upgrade head`. Otherwise the code stays blob-identical to the gated tree.
- At this tree, no migration on `origin/main` has `down_revision` `d4e81b7a2c95` (`git grep` returned none),
  so no re-point is due yet.

### Runs owed after GATE END (none run in the window)

1. Red-first for each new test, shown red by its own assert and then green, quoted here. This includes the
   nullability test with `models.py:1358` reverted to `nullable=False` (it must fail on the first assert),
   and again with the migration not applied (it must fail on the flush).
2. Build: `uv sync --all-packages`; `uv run python scripts/generate-contracts.py`, then `--check`.
3. `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`.
4. Migration: `alembic upgrade head`, single head, `alembic downgrade -1 && alembic upgrade head`, in a granted
   DB window.
5. `flock -w 900 /tmp/slots/gate-2 env -C <wt> python3 scripts/audit-docs.py` and `doc-index.py --check`.
6. Small-test runs of the three new test files, through `run-small.sh`, with return codes.

## Pre-gate review fixes — 2026-10-16 (writing only, nothing run)

Source: the lead's verdicts on auditor-1274's read-only review of `afcd84fb`, `from-lead-2026-10-09.md`
"2026-10-16 10:27:00 BST" (the SL-1274 bullet); the maintainer's `to-lead.md`
"2026-10-16 10:27:41 BST" (DP-1274-DIAG, DP-1274-NUMERIC). Each row was checked against the code before
it was changed. Line numbers are at the head that carries this entry.

**Rulings recorded.** The lead's write-set ruling of "2026-10-16 10:14:37 BST":
`packages/pricing-core/src/pricing_core/modelling/__init__.py` is accepted in this slice's write set (it only adds
`source_columns_of`, `is_certainly_numeric` and `normalised_expression` to the import block and `__all__`). The
lead widened the write set to `packages/model-schema/tests/test_factor.py` ("2026-10-16 10:27:00 BST", F1).

| Item | Stamp | Change |
|---|---|---|
| F1 | lead 10:27:00 | `packages/model-schema/tests/test_factor.py`: the EXPRESSION arm of `test_every_other_type_still_requires_a_source_column` and of `test_only_an_interaction_may_source_no_columns` now supplies `expression`, so each fails by its own message (`source_columns`), not by the required-arm check that runs first. |
| F2 | lead 10:27:00 | `backend/src/app/platform/modelling.py`: `FactorType` before `FieldError` in the `model_schema` import (I001). |
| F3 | lead 10:27:00 | E501: `pricing_core/modelling/factors.py` module docstring re-wrapped; `backend/tests/test_expression_factors_api.py` `_seed_fitted_model` docstring shortened. (The `def` line with a `# type: ignore` pragma is exempt.) |
| F5 | lead 10:27:00 | `test_expression_factors_api.py`: the nullability test and `test_banding_created_audits_the_source_expression` assert inside the unit of work and end it with `_RollBack`, so no NULL `column_name` row is committed. Both failure modes stay detectable: the ORM `nullable` assert, and the flush meeting the migrated schema. The audit assert reads the event in the open transaction (`_events_in_session`) and the test then checks none was committed. |
| F6 | lead 10:27:00 | `factors.py` `_expression_series` and `bandings.py` `_cut_values` catch `pl.exceptions.PolarsError` and raise `FactorResolutionError`. Tests: `region * 2` at resolution and at propose (`test_expression_factors.py`). |
| F8 | lead 10:27:00 | `bandings.py` `propose_banding`: non-finite values (inf and NaN) are set to null in place (aligned with the exposure and claim columns); the all-non-finite refusal counts null, NaN and infinite separately. Tests: `1 / x` with a zero, and three count-text cases. |
| F9 | lead 10:27:00 | `model_schema/modelling.py`: `max_length=2000` on `Factor.expression`, `Banding.source_expression`, `BandingProposal.source_expression`, as `objectives.py` `loss`. Test: 2000 accepted, 2001 refused, on all three. `02` §4.1 and §4.2 amendments say so. |
| F12 | lead 10:27:00 | `pricing_core/data/expressions.py` `referenced_columns`: a name is excluded only in call position (`Call.func`, the identity `_check_symbols` already uses), not when it equals a function name. Test: a column named `max`. This also changes the `recipe` profile's lineage for a bare name equal to a function name, which it used to drop. |
| F13 | lead 10:27:00 | `f2b6d90a4c17` header `Create Date` is the commit time from `date -u` (see the commit). The earlier value was an estimate. |
| F14 | lead 10:27:00 | Recorded here, below. |
| Weak assert | lead 10:27:00 | `test_a_string_banded_expression_is_refused` matches the refusal's own wording ("String result and pins a banding. A category is not banded"). |
| DP-1274-NUMERIC (a) | maintainer 10:27:41 | `test_a_binop_root_over_strings_is_still_refused_as_certainly_numeric`: `region + alt_region` is 422 naming FR-210. FR-95 literal; over-refusal is fail-safe. The OQ for option (b) and the FD are another seat's, not this slice's. |
| DP-1274-DIAG (a) | maintainer 10:27:41 | **Not done: stopped.** The omission needs a new reason member in `model_schema/diagnostics.py`, a shape change; see the report to the lead. |

F4 (regeneration of `docs/contracts/`, with `test_contracts.py:1147` on the nullable `column`) stays owed after
GATE END. F11 is not adopted (inert), per the lead.

### F14: rollback hazards of the shape change

- **An old build cannot read the new keys.** `Factor`, `Banding` and `BandingProposal` are `extra="forbid"`, so a
  build from before this slice that reads a stored Factor carrying `expression`, or a Banding carrying
  `source_expression` (with `column` null), fails validation. Rolling the code back is not safe once such a row exists.
- **The downgrade fails once an expression Banding exists.** `f2b6d90a4c17.downgrade()` re-imposes NOT NULL on
  `bandings.column_name`; a Banding over an expression has NULL there, and a banding row cannot be deleted
  (FR-101), so `alembic downgrade -1` aborts. This is intended (loud, not lossy), and it means a rollback needs a
  forward fix, not a downgrade.
- **The API tests that POST an expression Banding commit a NULL `column_name` row** into the shared test
  database (`test_a_banded_expression_factor_is_created` and three others); those cannot be rolled back, as they go
  through HTTP. The two tests above that talk to the session directly do not commit one.

### Runs owed after GATE END (added by this entry)

`ruff check .`, `mypy`, `lint-imports`; `generate-contracts.py` and `--check` (and `test_contracts.py` on the
nullable `column`, `:1147`); the new tests red then green by their own asserts (F1, F5, F6, F8, F9, F12, NUMERIC,
the weak assert) through `run-small.sh`; the migration round trip on a scratch DB; `audit-docs.py` and
`doc-index.py --check` under the gate-2 flock. The branch must also re-merge `main` `a2f77b2d` before its gate.

## DP-1274-DIAG (a) — EXPRESSION_FACTOR omission — 2026-10-16 (writing only, nothing run)

Stamps: the maintainer's `to-lead.md` "2026-10-16 10:27:41 BST" (refuse-or-omit with a named reason; red-first
test per diagnostic) and "2026-10-16 10:33:35 BST" (concurred; render as readable text, own branch, text asserted);
the lead's approval in `from-lead-2026-10-09.md` "2026-10-16 10:33:20 BST" (the one new member; widened write set).
Red-first commit `d88d2218` (the four tests only); the change follows in the next commit.

**Change.** One new member `EXPRESSION_FACTOR = "expression_factor"` on each enum; an `expression` Factor is
omitted from both GBM per-factor blocks instead of reading `source_columns[0]` / `[:1]`.

| What | Where (at the head carrying this entry) |
|---|---|
| `PermutationOmissionReason.EXPRESSION_FACTOR` | `packages/model-schema/src/model_schema/diagnostics.py:380` |
| `PartialDependenceOmissionReason.EXPRESSION_FACTOR` | `packages/model-schema/src/model_schema/diagnostics.py:434` |
| permutation block omits an expression Factor | `packages/pricing-core/src/pricing_core/modelling/diagnostics.py:958` (before the `source_columns[:1]` read) |
| partial-dependence loop omits it, no `_sweep` call | `packages/pricing-core/src/pricing_core/modelling/diagnostics.py:1388` (before `_sweep`, which holds `source_columns[0]`) |
| hand-authored contract enum | `docs/contracts/schemas/diagnostics.schema.json:271` (`PermutationOmission.reason`; the file has no enum for the partial-dependence reason, so there is none to edit) |
| FR-178 dated amendment (both stamps) | `docs/specs/02-modelling.md:275` |
| rendered text, permutation | `frontend/src/components/GbmImportanceCharts.vue:109` (own branch, no default hiding it) |
| rendered text, partial dependence | `frontend/src/components/PartialDependencePanel.vue:78` (own branch; the maintainer's 10:33:35 sentence names GbmImportanceCharts, and this panel switches on the same reason, so it gets the same branch) |
| tests | `packages/pricing-core/tests/test_expression_factors.py:425`, `:437` (x2 backends); `frontend/src/components/__tests__/GbmImportanceCharts.test.ts` ("names an expression factor's omission in words") asserts the text `computed from a formula`; `PartialDependencePanel.test.ts:81` likewise |

The other `source_columns` readers in the module were read and left: `:565-569`, `_shared_source_columns`,
`_operand_columns` take sets of columns for cross handling; an expression Factor is skipped before them wherever it
is not a cross operand, and as an operand all its source columns move together under one order. An expression
Factor's monotonicity check is skipped with the rest (the `continue`). `rating/runtime.py:877` and
`platform/model_specs.py:86` are untouched (FD 8068). No test enumerated the reason members; none needed changing.

**Backward compatibility.** An older build cannot read the new value: `expression_factor` fails enum validation
there, so a diagnostics artifact carrying it does not load on an older build. Older artifacts load unchanged.

**Owed (nothing was run; the ALONE latency gate forbids it).** (1) the new `test_expression_factors.py` tests and
the FE tests RED at `d88d2218`, GREEN at the next commit; (2) `generate-contracts.py` then `--check` (generated
copies and `openapi/generated.json` carry the enum); (3) `pnpm generate:api`, FE `type-check` and `test` (the
test literals type-check only once the client is regenerated); (4) `ruff`, `mypy`, `lint-imports`; (5) `audit-docs.py`
under the gate-2 flock; (6) the two GBM backends' full `test_gbm.py` / `test_diagnostics.py`.

**2026-10-16 10:41 BST — re-merge of `origin/main` `a2f77b2d`.** `git merge-tree --write-tree origin/main HEAD` at
`86e42d79` returned rc 0 (no conflicts); `git merge --no-ff origin/main` then merged clean, tree `498888d1`, the tree
the dry run predicted. Conflicts: none, so no hand resolution. The new head is the merge commit this entry rides in
(its sha is read from `git log`, not pasted here). Files #1309's range (`0877e6e7..a2f77b2d`) touches that the slice
also touches: `docs/roadmap.md` and `docs/specs/03-rating-engine.md`; both merged without a conflict. **Owed (nothing
was run; the ALONE latency gate forbids it):** `docs/INDEX.md` regeneration (`doc-index.py`, then `--check`, under
the gate-2 flock) and `generate-contracts.py --check`; both after GATE END.
