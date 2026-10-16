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
