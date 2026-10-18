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

**2026-10-16 BST — the estimate never undercounts an expression Factor (the maintainer, 10:42:37, Q1).** The ruling
fixed FD 8068's `model_specs.py` limb IN S4, not as a deferred limb: `_estimated_parameters` sized every factor from
`source_columns[0]`, which under-counts a formula over several columns, and the estimate gates `complexity_or_refuse`,
so the under-count weakened a refusal. The red-first test is `backend/tests/test_model_specs_expression_estimate.py`
(commit `e97b293c`): a 10 x 10 two-column expression over a floor of 10.5 is refused, the same spec at exactly 10.0 is
accepted. The fix commit follows it.

*The rule* (docstring of `_expression_levels` in `backend/src/app/platform/model_specs.py`): an expression Factor is
counted at the **product of its source columns' level counts** (`distinct_count`, plus one for a column that has nulls),
because a function of a row's values cannot take more distinct values than the columns take combinations (FR-95:
evaluated over dataset columns only), and a pinned Banding maps those values onto no more bands. A numeric result with
no Banding is refused upstream (FR-95 at creation, FR-208 at resolution), so no continuous result needs bounding. Where
a source column is absent from the profile the bound is unknown, and the gate refuses the spec with a
`complexity_limit` problem naming the factor, but only when `modelling.min_exposure_per_parameter` is set (no limit
means no gate, OQ-580). Correlated columns and banding make the product an over-estimate, which is the fail-safe
direction.

FD 8068 records this limb as discharged by S4; the auditor updates FD 8068, this slice does not edit it. `rating/runtime.py`
is untouched. **Owed (nothing was run; the ALONE latency gate forbids it):** the new tests RED at `e97b293c` and GREEN
at the fix commit; `ruff`, `mypy`; `test_model_specs.py` beside them (the existing gate tests must still pass).

## Observation A — a multi-column expression Factor is never scored — 2026-10-16 (writing only, nothing run)

**Ruling:** `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-10-16 10:47:33 BST", Observation A: fix in S4 (not a finding); read
the plans, cite the line, and if multi-column is IN scope carry every source column, if NOT refuse at model-spec creation.

**Scope, from the plans.** IN scope. `PL-1268` Slice 4 (`docs/plans/PL-01268-wk-690-expression-custom-objectives-map-plan.md:520-521`):
"`resolve_factors` resolves an `expression` Factor through the `factor` profile over the declared dataset columns only
(FR-95)" (plural; no one-column limit). `PL-1621` row 1 (`:210`) has "undeclared columns refused at create", and
`02` FR-95 reads "evaluated over dataset columns only". The code already says so: `model_schema/diagnostics.py:375`
("a formula over several `source_columns`"), and `factors.py:184` and `:372` iterate every source column. `PL-1621:221`
and `PL-1665` say nothing that limits an expression to one column. So the model-spec refusal branch does not apply.

**The defect, read in `rating/runtime.py` at 6bd8788b.** `:877` builds `columns` for factors with exactly one source
column only. `:817-818` (`_GlmScorer.predict`) renames each row key through `columns`. A multi-column expression
Factor's row key is its slug, which is no frame column, and its source columns are never supplied, so
`resolve_factors` raises `FactorResolutionError` (`factors.py:184`) on every quote.

**Why the fix is not written here.** The row can only carry the source columns if the graph supplies them, and the
graph supplies what `feature_map` maps. `required_model_inputs` (`factors.py:455-466`) defines a model's inputs as its
Factor slugs, and `03` FR-222 (membership, `MODEL_CALL_FEATURE_MAP_INVALID`) and FR-240 (completeness, `RL-1523`)
both print that definition ("its Factor slugs"). Letting a multi-column expression Factor take its source columns
instead of its slug changes that one definition, so it needs a dated amendment to `03` FR-222 and FR-240. The brief
says to stop and report in that case. **Nothing was written but this entry.** The candidate is in the report: an
`expression` Factor with more than one source column contributes its source columns, not its slug, to
`required_model_inputs`; the runtime then needs no rename for them (an unknown row key passes through `columns.get(k, k)`).
No `model-schema` shape changes (`feature_map` stays `dict[str, str]`).

FD 8068 and FD 8070 are not touched. **Owed:** nothing run; the red-first fit, pin and quote test of
`driver_age + vehicle_age`, banded, is owed once the amendment is ruled.


## DP-1274-MULTI (a') — Observation A fixed — 2026-10-16 (writing only, nothing run)

**Ruling:** `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-10-16 10:50:08 BST" (DP-1274-MULTI -> (a'), with the
predict-time collision guard moved INTO S4). It adopts the lead's option (a'): every `expression` Factor contributes
its source columns, not its slug, to `required_model_inputs`, whatever the column count; a plain Factor keeps its slug.
`model-schema` is unchanged, and `feature_map` stays `dict[str, str]`.

**Red-first** (`c6ae78c1`): `packages/pricing-core/tests/test_rating_glm_expression_inputs.py` holds the banded
`driver_age + vehicle_age` fit, pin and quote against `predict_glm`; the one-column `driver_age * 2` case; the unit
definition of `required_model_inputs`; and the guard pair (unequal values refused by name, equal values score).

**Fix:**
- `required_model_inputs` (`pricing_core/modelling/factors.py`): an `expression` Factor gives its `source_columns`, every
  name once, in order. Its consumers were read: compile's FR-240 completeness check
  (`pricing_core/rating/compile.py`, `check_model_call_coverage`) and the backend's FR-222 membership check
  (`backend/src/app/platform/rating_algorithms.py`, `_accepted_feature_map_values`) both call it and take the set
  or the list as it comes, so both follow the new definition with no edit.
- `_GlmScorer.predict` (`pricing_core/rating/runtime.py`): the renamed row is built key by key; two keys on one column
  with unequal values raise `PredictionError("MODEL_CALL_FEATURE_COLLISION", ...)`. The handler already turns a
  `PredictionError` into the `model_call` failure sentinel with the code only (FR-255, NFR-499). The error is new to the
  module, so it is registered in `03` beside `MODEL_CALL_FEATURE_MAP_INVALID`.
- Spec: dated amendments to `03` FR-222 and FR-240, and the error code entry (`docs/specs/03-rating-engine.md`).

**Findings.** FD 8070 is not edited here. Per the 10:50:08 entry it keeps the compile-time guard and its two existing
cases, and cites this slice's guard as discharging its predict-time limb.

**Not covered, for the lead.** The handler builds `feature_row` keyed by the `feature_map` VALUE, so two graph names
mapped to the same feature name collapse before `predict` sees them (the last one wins). That collapse is not a
`predict` collision and this guard does not reach it.

- 2026-10-18 16:21:10 BST — fix-1274: the guard pair above ("equal values score") is superseded for different graph steps by to-lead "2026-10-17 11:15:37 BST" (Q1(b)); the predict-time guard remains as the backstop (this entry; ruling: to-lead "2026-10-18 16:04:05 BST", DP-1274-COLLIDE option 1). The `03` FR-222 and FR-240 DP-1274-MULTI inserts carry the same dated line.

### Runs owed after GATE END (none run in the window)
1. The new test file at `c6ae78c1`: the reds are red there (the two quote cases at compile, with
   `MODEL_CALL_FEATURE_MAP_INVALID`; the unit definition; the unequal-values case), the equal-values case green.
2. The same file at the fix commit: all green.
3. `test_rating_glm_model_call.py`, `test_factor_resolution.py`, `test_rating_compile_completeness.py`, and the backend
   `test_rating_algorithms.py` (the save check) after the change to `required_model_inputs`.
4. `ruff check`, `mypy`, `audit-docs.py` (under the gate-2 flock).

## PRs

Not opened yet. The lead opens the PR; SL 8074 (FD 8070) is unmerged and carries the same `_GlmScorer.predict` collision guard and the same `MODEL_CALL_FEATURE_COLLISION` entry in `03`; per the 2026-10-16 10:52:08 BST ruling this slice drops its copy when SL 8074 is on main.

## Re-merge and first runs — 2026-10-17 (executor-1274b)

Re-merge of `origin/main` `ebe3292c` (merge `8c487a87`), no conflicts. Small runs through `run-small.sh` only; the DB-backed backend tests and the full gate are not run (SL 8074's gate holds gate-1).
- Scoring probe (`scratch/probe_expr_scoring_test.py`, copied in, run, removed): with `test_rating_glm_model_call.py` and `test_factor_resolution.py`, 40 passed, rc 0. A one-column banded expression prices on the transformed value.
- `test_rating_glm_expression_inputs.py` was red on its own fixtures: a banding slug with `_`, and `"risk" not in result` against the failure sentinel (which zeroes the produced names). Both fixed; 25 passed with `test_quote_input_raise_sites.py`.
- `test_expression_factors.py::test_an_infinite_value_is_dropped_not_cut_at` failed: `band_statistics` cut the infinite value that `propose_banding` dropped. Fixed in `bandings.py`; 51 passed with `test_bandings.py`.
- `docs/contracts/` regenerated (`generate-contracts.py`, `--check` rc 0); the authored `banding.schema.json` gains `maxLength: 2000` on `source_expression` so `test_contracts.py` (171 passed) sees both sides agree.
- ruff and mypy clean; `lint-imports` 4 kept, 0 broken.

- 2026-10-18 14:50:09 BST — executor-1274r: the "Not done: stopped" on DP-1274-DIAG (a) above is stale. DP-1274-DIAG was ruled (a) at to-lead "2026-10-16 10:27:41 BST" (refuse-or-omit with a named reason plus an owned FD) and its form concurred at "2026-10-16 10:33:35 BST" (`EXPRESSION_FACTOR` on both omission-reason enums); the slice builds to both. Re-merged onto origin/main d0d6a265 under the maintainer entries "2026-10-18 14:45:19 BST" and "2026-10-18 14:47:38 BST".

- 2026-10-18 16:21:10 BST — fix-1274 (executor, Sonnet 5.5) on `8bd04267`, after GATE END: the gate's 48 failures were 13 in the docs-suite tests (`tests/`, which read the working ids) and 35 in the slice's code and tests; these are the 35, fixed under to-lead "2026-10-18 16:04:05 BST": (1) the 3 collision tests in `test_rating_glm_expression_inputs.py` now follow B at compile (distinct-step pair refused with `MODEL_CALL_FEATURE_MAP_INVALID`, naming the column and no value; same `input_name` and `on_missing` compiles and prices; the predict-time guard tested on a scorer built from resolved payloads without `compile_bundle`, `MODEL_CALL_FEATURE_COLLISION`), no product code change; (2) the supersession lines above and in `03`; (3) `FactorCreate` takes `expression`, bound from `Factor.model_fields`, and `docs/contracts/openapi/generated.json` is regenerated (27 API tests: the slice's feature was unreachable over HTTP); (4) three slug fixtures made valid typed slugs; (5) `test_glm.py` now states FR-208's amended verdict; (6) `test_error_sinks.py`: four sink keys (six sites) given `_SINKS` entries and sentinel tests. A full re-gate is owed (logic changed).

- 2026-10-18 16:36:50 BST — fix2-1274 (executor, Sonnet 5.5), under to-lead "2026-10-18 16:34:28 BST" (i)–(iii): (i) `_seed_fitted_model` in `backend/tests/test_expression_factors_api.py` now supplies `fit_result={"fitted": True}` and a `diagnostics_id`, as `test_artifact_usage_counts.py` does, for `ck_models_fitted_model_has_a_fit_result` and its diagnostics twin; (ii) the 2 `_SINKS` entries for `safe_error._expression_detail` were quoted and no row value reaches them (no code change); (iii) `origin/main` 33668af9 merged (a38690cd, `docs/INDEX.md` taken from main and regenerated in the next commit; no code conflict; the two-sided list from base d0d6a265 is `docs/INDEX.md`, `docs/roadmap.md`, `docs/specs/03-rating-engine.md` only). The DB window on the merged head follows.

- 2026-10-18 16:41:40 BST — fix3-1274 (executor, Sonnet 5.5), under to-lead "2026-10-18 16:40:28 BST": `_seed_fitted_model` in `backend/tests/test_expression_factors_api.py` now builds `fit_result` from model-schema's `GlmFitResult(converged=True, iterations=1, fit_seconds=0.0).model_dump(mode="json")`, the way `record_fit` stores it, replacing the hand-written `{"fitted": True}` of the 16:36:50 entry (the 500 `union_tag_not_found`). The third own-DB window follows.

## Audit — pre-PR, after the re-gate (auditor-1274, 2026-10-18 18:18:08 BST)

Tree: head `ebcb6eaaf8771b4241891ba901f337cdd5a754cb`, tree `c28f29ea1024dbd3414b7fee72b182973473efdb`, base `origin/main` `33668af959e360044a65929d776c18011d632c87` (unmoved at the audit). Scope: the delta `8bd04267..ebcb6eaa` (`git log --no-merges --oneline 8bd04267..ebcb6eaa`, 11 non-merge commits) against the rulings of to-lead "2026-10-18 15:59:05 BST" to "2026-10-18 16:45:50 BST", the re-gate of "2026-10-18 18:14:54 BST", and this ledger. Nothing was run except the docs checks below; the gate logs were read.

**A1 — DP-1274-COLLIDE option 1 ("2026-10-18 16:04:05 BST"): met.** Commit `08c7bbb0` changes one test file and no product code. The 3 tests, all in `packages/pricing-core/tests/test_rating_glm_expression_inputs.py`:
- `test_compile_refuses_two_distinct_steps_on_one_column_naming_it_and_no_value`: `pytest.raises(CodedError)` on `compiled_bundle(glm_world(), _COLLIDING)`; carries the rule with `message.startswith("MODEL_CALL_FEATURE_MAP_INVALID")` and `"driver_age" in message` and `"age_raw" in message`.
- `test_inputs_of_one_input_step_definition_on_one_column_compile_and_score_normally`: the same-`input_name` pair compiles and scores (`MODEL_CALL_ERROR_KEY not in result`, `result["risk"] == approx(expected, rel=1e-12)`).
- `test_the_predict_time_backstop_refuses_unequal_values_by_column_name`: a scorer built from `runtime._glm_scorer` without `compile_bundle`; `pytest.raises(PredictionError)`, `"driver_age" in str`, `"31" not in str`, `"57" not in str`, and the equal row scores.
Supersession lines present: ledger (the dated line under DP-1274-MULTI) and `docs/specs/03-rating-engine.md` FR-222 and FR-240 (commit `4c0b28db`).

**A2 — the six sink sites wrapped ("2026-10-18 16:25:55 BST", "2026-10-18 16:29:54 BST"): met.** Commit `ff32b172`. The six sites are in four functions (the ruling's "6 wrapped FUNCTIONS" is six sites in four functions). `git -C <wt> grep -nE "str\(exc\)|\{exc\}" HEAD -- <file>` has no hit in `bandings.py` (rc 1) and `factors.py` (rc 1); in `backend/src/app/platform/modelling.py` its only hit is line 1123. An AST read of the function bodies at HEAD gave: `bandings.source_columns_of` (82–104) hits `[]`; `bandings._cut_values` (107–133, two sites) `[]`; `factors._expression_series` (411–458, two sites) `[]`; `modelling._require_a_creatable_expression` (276–347) `[]`; `modelling.resolve_offset_model` (1058–1135) hit at 1123, main's listed sink (`_SINKS`), not one of the six. The wrapped lines: `bandings.py` 102, 126, 131 (`safe_error_text`), `factors.py` 432, 439 (`safe_error_text`), `modelling.py` 297 (`safe_error_detail`). The six `_SINKS` entries are removed; two entries for `safe_error._expression_detail` are added (accepted at "2026-10-18 16:34:28 BST" (ii)). `ExpressionError` joins `safe_error_detail` (`_expression_detail`: message plus `line N, column M`); the proof that no frame reaches it is `test_every_expression_error_is_raised_where_no_row_value_is_in_scope` with a positive control. Red-first quoted in the commit body.

**A3 — API shape diff: not "FactorCreate.expression only" over the whole slice (finding F-A3, LOW).** `git diff origin/main...HEAD -- docs/contracts/openapi/generated.json`; schema-by-schema compare of `components.schemas` at `origin/main` and HEAD gives 6 changed schemas:
- `FactorCreate` (request): + `expression` (`anyOf[string maxLength 2000, null]`). Commit `34f0fe11` alone is exactly this (+12 lines), which is what "2026-10-18 16:25:55 BST" item 3 accepted.
- `Factor` (response): + `expression`, the same type.
- `Banding` (response): `column` becomes `anyOf[string, null]`, `source_expression` added, `column` leaves `required`.
- `BandingProposalRequest` (request): the same three changes.
- `PartialDependenceOmissionReason` and `PermutationOmissionReason` (response enums): + `expression_factor`.
Also `docs/contracts/schemas/banding.schema.json`, `diagnostics.schema.json` and the two `generated/` twins. All are accounted for in this ledger (RL-1700 (c), DP-1274-DIAG (a), F9) and arrived before the first gate (`bba2e0ae`); none is a stranger. The finding is only that the ACK sentence "FactorCreate.expression ONLY" is true of the fix commit, not of `origin/main...HEAD`. Request and response both checked. Fully derived from model-schema (`generate-contracts.py --check` rc 0 in the gate).

**A4 — the seed fixture: met.** `e7dd4a3c`: `backend/tests/test_expression_factors_api.py:417` builds `GlmFitResult(converged=True, iterations=1, fit_seconds=0.0).model_dump(mode="json")` (import at :46); no hand-written dict at HEAD. `diagnostics_id=new_uuid7()` is the only literal-ish field, a bare id the CHECK needs.

**A1 note (F-A1, LOW).** The first COLLIDE test's name and the ruling say "no value", but the test asserts the two column names only; no assert that a value is absent from the message. The compile message carries column names by construction, so this is a thin assert, not a defect.

**B — the re-gate's verdict rows: match "2026-10-18 18:14:54 BST".** `scratch/sl1274-regate/`: `pytest.log` ends `13 failed, 6464 passed, 12 skipped`; `failed.now` 13 lines; against `failed.gate1` (48): `comm -23` (now, not in first) 0, `comm -13` (first, not now) 35. `audit_docs.log` `FAILED (2)`: check 31 "gap in the full allocation between 1816 and 8062" and "id 8062 is `created:` 2026-10-16, earlier than id 1816's 2026-10-18" only. Demo: `journey done in 1186s` (demo.log:4971), `dislocation #1 | 436 s`, D7 +489842011, keycloak bind under tools-main, zeros `own-DB count=0 redis RT db 1 dbsize=0 redis RD db 3 dbsize=0`. ruff, mypy, import_linter, contracts, req_coverage rc 0; frontend rows rc 0. The `demo seconds | 1308` row includes the served-page wait (reading as the maintainer's).

**C — this ledger's own record at ebcb6eaa: three findings.**
- **F-C1 (MEDIUM).** No entry records the `ff32b172` change: the six-site wrap, `ExpressionError` on safe_error's allow-list, the removal of six `_SINKS` entries, and the two rulings "2026-10-18 16:25:55 BST" and "2026-10-18 16:29:54 BST". Worse, the entry "2026-10-18 16:21:10 BST" item (6) still says the four sink keys were "given `_SINKS` entries and sentinel tests", which is the opposite of the code at HEAD (a record claim unsupported at this tree). Nothing cites "2026-10-18 16:26:29 BST", "16:29:04", "16:34:28 BST" (i)–(iv), "16:45:50 BST" or the three own-DB windows' results. The entry "2026-10-18 16:36:50 BST" is superseded by the fix3 entry for the seed, which says so.
- **F-C2 (MEDIUM).** The "Runs owed after GATE END" lists (three of them) are not marked discharged or carried. The gate and the windows discharge most (ruff, mypy, lint-imports, contracts, audit-docs, the new tests in the full run). Not evidenced anywhere I read: the migration round trip `alembic downgrade -1 && alembic upgrade head`, and the "red then green by its own assert" shows for the 2026-10-16 tests. The gate log has `alembic upgrade` rc 0 only. Verdict proposal: record "discharged by the re-gate" per item, and carry the round trip with an owner, or run it in a granted window.
- **F-C3 (LOW).** The `## PRs` section still reads "Not opened yet"; the front matter `tree:` field (`81fabac4…`) was not re-derived. Both are for the mint/PR seat's closing acts.

**Docs checks (under the gate-2 flock, on this tree plus this section):** `audit-docs.py` rc 1, `FAILED (2)`: the two check-31 lines on id 8062 only (gap between 1816 and 8062; `created:` 2026-10-16 before id 1816's 2026-10-18), the same two as the re-gate. `register-lint.py` rc 0 (0 violations). `idsweep.sh origin/sl-1274-wk690-s4-factor-expression`: 1816 pairs, no duplicate, no CROSS-BRANCH.

## Correction and per-item disposition of the owed lists — 2026-10-18 18:22:27 BST (fix4-1274, executor, Sonnet 5.5)

Under to-lead "2026-10-18 18:20:40 BST" (the audit's F-C1 and F-C2 adopted), on head `9af5e9e0`. Appended; no earlier entry is edited.

### F-C1 — the record of `ff32b172` and the rulings after `8bd04267`

- **`ff32b172`** (`fix(safe-error)`): the six expression sinks are wrapped in four functions (`bandings.source_columns_of`, `bandings._cut_values` (two sites), `factors._expression_series` (two sites), `_require_a_creatable_expression` in `backend/src/app/platform/modelling.py`, one site); `ExpressionError` joins `safe_error`'s allow-list (message and the two position attributes kept; evaluation-time polars/arrow errors stay redacted); the six `_SINKS` entries in `backend/tests/test_error_sinks.py` are removed.
- **Rulings, by stamp (all in `to-lead.md`):** "2026-10-18 16:25:55 BST" (sinks wrapped, not registered; `ExpressionError` on the allow-list; the `FactorCreate.expression` shape accepted); "16:26:29" (DB proofs, option (a), a granted own-DB window); "16:29:04" ((A) timing accepted for the scoring path only; the re-merge is not docs-only and comes before the window); "16:29:54" (`_SINKS`: remove the six entries; item (4) of 16:25:55 corrected); "16:34:28" (window 1 = data only; fix2 (i)–(iv); a second window on the merged head); "16:40:28" (merged head verified; fix3, the seed built from model-schema; a third window); "16:45:50" (window 3 green; GO the re-gate); "18:14:54" (re-gate green; GO audit, mint, PR); "18:20:40" (audit adopted; this fix4).
- **The three own-DB windows** (results as the rulings above and the entries "16:36:50", "16:41:40" record them; the window logs are the lead's, not re-read here): window 1 on the unmerged `ff32b172`, two files skipped, the API file 29 of 30 (one red: the seed's `ck_models_fitted_model_has_a_fit_result`); window 2 on the merged head, red on the seed's hand-written `fit_result` (a 500 from `FIT_RESULT_ADAPTER`); window 3 on `ebcb6eaa`, run 1 `53 passed` (api 30, error_sinks 11, api_models 12), run 2 `36 passed` (api_transformations 11, rating_version_compile 25), 0 skipped, 89 = collect-only 89, zeros quoted in the 16:45:50 ruling.
- **Correction:** the entry "2026-10-18 16:21:10 BST" item (6) (`test_error_sinks.py`: four sink keys given `_SINKS` entries and sentinel tests) is **superseded** by "2026-10-18 16:29:54 BST": the sites are wrapped, not listed, and the six entries are removed. The sentinel tests stay.

### F-C2 — "Runs owed after GATE END", item by item

Evidence for "discharged by the re-gate" is `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1274-regate/` at head `ebcb6eaa` (END 17:14:23Z): `ruff.rc` 0, `mypy.rc` 0, `import_linter.rc` 0, `contracts.rc` 0, `req_coverage.rc` 0, `pytest.log` `13 failed, 6464 passed, 12 skipped` (the 13 = the working-id cascade set), `audit_docs.log` `FAILED (2)` (the two check-31 lines on id 8062), frontend gate rows 0.

| List (heading) | Item | Disposition |
|---|---|---|
| 2026-10-16 "Runs owed" (DP-7 area) | 1 red-first for each new test | **red by commit, not by run**, except the two failures quoted in the entry "Re-merge and first runs" (the slug/sentinel fixtures; `test_an_infinite_value_is_dropped_not_cut_at`). Green: discharged by the re-gate pytest (all but the 13 cascade). The nullability test with `models.py:1358` reverted was not run: red by commit, not by run |
| same | 2 build, `generate-contracts.py`, `--check` | discharged by `contracts.rc` 0 (re-gate) |
| same | 3 ruff, mypy, lint-imports | discharged by the three `.rc` files, 0 |
| same | 4 `alembic upgrade head`, single head, `downgrade -1 && upgrade head` | upgrade and single head discharged (`pre-heads.log` shows `f2b6d90a4c17 (head)`; the re-gate's upgrade ran). **The round trip is not discharged**: it is carried to the window of this fix4, steps 3–6 (the entry below) |
| same | 5 audit-docs, `doc-index.py --check` | audit-docs discharged by the re-gate (`FAILED (2)`, the id-8062 cascade only); `--check` re-run at the mint |
| same | 6 small runs of the three new files | discharged by the re-gate pytest, and by window 3 for the API/sinks files |
| 2026-10-16 "Runs owed (added by this entry)" | ruff/mypy/lint-imports; contracts and `test_contracts.py:1147`; the new tests red then green (F1, F5, F6, F8, F9, F12, NUMERIC, weak assert); round trip on a scratch DB; audit-docs, `--check`; re-merge before the gate | tools, contracts, audit: discharged by the re-gate as above. Red then green: **red by commit, not by run**; green discharged by the re-gate pytest. Round trip: carried to fix4's window. Re-merge: done (`8c487a87`, `a38690cd`; main `33668af9`) |
| 2026-10-16 DP-1274-DIAG (a) | the new tests RED at `e97b293c`, GREEN at the next commit | **red by commit, not by run**; FE and backend green discharged by the re-gate |
| 2026-10-16 DP-1274-MULTI, "Runs owed" | 1 the reds are red at `c6ae78c1`; 2 all green at the fix commit; 3 the four neighbouring files; 4 ruff, mypy, audit-docs | 1: **red by commit, not by run** (the 2026-10-17 entry quotes the file red on its own fixtures, not the designed reds); 2–3: discharged by the re-gate pytest and, for the collision tests, by the audit's A1; 4: discharged by the re-gate |

Nothing is carried without an owner except the round trip, owned by this fix4 (fix4-1274).

## Downgrade refusal and the round-trip window — 2026-10-18 18:26:07 BST (fix4-1274, executor, Sonnet 5.5)

Under to-lead "2026-10-18 18:20:40 BST" (3)–(4); closes the round trip carried in the entry above. Window tree: part 1 at `1e469145d1ae154296b3e06b327d132b3a1f6228` (the migration unchanged), part 2 at `68eb62a7e4926c1c81684d483943761a81a3e674`. Under `flock -w 900 /tmp/slots/verify-1`; part 1 start 2026-10-18 18:23:35 BST (load1 0.64, `free -g` available 25), part 2 start 18:25:33 BST (load1 1.80, available 25), end 18:25:52 BST. Database `gipricing_sl-1274_rt` (`createdb -U gipricing -T gipricing`), DSN `postgresql+asyncpg://…@localhost:5432/gipricing_sl-1274_rt`.

**Part 1 — RED (before any code change).** `alembic upgrade head` rc 0, `alembic current` = `f2b6d90a4c17 (head)`. One expression Banding inserted through `create_banding` (`backend/src/app/platform/transformations.py:261`), by a scratch helper that builds the principal as `backend/tests/test_model_nfrs.py:77` `_principal_with` does (`source_expression="driver_age * 2"`, `column_name` NULL, committed): `INSERTED rt-0048a7 column_name= None`. `alembic downgrade -1` rc 1:
`sqlalchemy.exc.IntegrityError: … asyncpg.exceptions.NotNullViolationError: column "column_name" of relation "bandings" contains null values`; `alembic current` after it `f2b6d90a4c17 (head)`. **Deleting the row:** the platform has no delete path, and `delete from bandings` is rejected by `bandings_no_modify` (`artifact_append_only()`, migration `e1f2a3b4c5d6`: "Artifacts are never rewritten"). In this throwaway database only: `begin; alter table bandings disable trigger bandings_no_modify; delete from bandings; alter table bandings enable trigger bandings_no_modify; commit;` → `DELETE 1`, `count(*)` 0, `tgenabled` `O`. Then `downgrade -1` rc 0 (current `e7c3a9b15d82`), `upgrade head` rc 0 (current `f2b6d90a4c17 (head)`). The database was kept for part 2.

**Red-first test.** `backend/tests/test_bandings_downgrade_refusal.py` runs the real `downgrade()` against a recording `op` (no database; run through `run-small.sh`, one file). `test_downgrade_refuses_naming_the_count_and_alters_nothing`: RED at `4c3f9dec` — `Failed: DID NOT RAISE RuntimeError` (1 failed, 1 passed); GREEN at `68eb62a7` — 2 passed, rc 0. It asserts the message starts `cannot downgrade f2b6d90a4c17`, names `3 banding`, says `removed or re-cut`, that nothing was altered, and that the one statement is a `count(` over `column_name IS NULL` (no value read). The second test asserts the no-expression-banding downgrade still re-imposes NOT NULL. Fix (`68eb62a7`): `downgrade()` counts the rows and raises `RuntimeError` before the `ALTER`; it deletes and converts nothing (precedent: `c4a81f6d2e95`). `ruff check .` rc 0; `mypy` rc 0; `ruff format --check` clean on the test file; on the migration file it reports the pre-existing 88-column `alter_column` lines, identical at the parent, left alone.

**Part 2 — GREEN.** `upgrade head` rc 0, current `f2b6d90a4c17 (head)`; one expression Banding inserted the same way (`rt-86f672`, `column_name= None`); `alembic downgrade -1` rc 1 with `RuntimeError: cannot downgrade f2b6d90a4c17 (bandings.column_name back to NOT NULL): 1 banding row(s) are cut over an expression and have no column. They must be removed or re-cut over a column before this downgrade can run; a banding is append-only (FR-101), so nothing was changed.`; `alembic current` stayed `f2b6d90a4c17 (head)`. Row removed as above (`DELETE 1`); `downgrade -1` rc 0 (current `e7c3a9b15d82`); `upgrade head` rc 0 (current `f2b6d90a4c17 (head)`).

**Close.** `dropdb -U gipricing gipricing_sl-1274_rt` rc 0; the window used no Redis, `redis-cli -n 1 flushdb` OK. Zeros: `redis-cli -n 1 dbsize` = 0; `select count(*) from pg_database where datname = 'gipricing_sl-1274_rt'` = 0. The window ran as two `flock` holds (part 1; part 2 with its close), not one, because a shell cannot hold the lock between tool calls; only this seat's own database was touched between them.
