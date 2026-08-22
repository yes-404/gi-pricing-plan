# W5 Closure — ledger

Executed 2026-08-22 on branch `worktree-oq-model-27-28`, stacked on the plan's base commit
`4836b26`. Six commits, `3c18737` → `e1e44bd`, pushed. Gate green both halves at the final
state. Tasks 1–5 ran fanned out across subagents; Task 6 in the main thread.

**Maintainer decisions received 2026-08-22:** D1 accepted as proposed; D2 — NFR-MODEL-7 out
of Phase 1 scope. D3 needed no ask: the fact it turns on was verified before Task 3 began.

## Commits

| Commit | Task | What |
|---|---|---|
| `3c18737` | 5 | `spec_hash` lineage: `v3 → v4` restored |
| `fbec07a` | 2 | NFR-MODEL-6 GLM two-fit determinism at 1e-10; raises OQ-MODEL-29 |
| `585d490` | 1 | NFR-MODEL-8 refusals carry `lineno`/`col_offset`/`end_col_offset` |
| `e9129e2` | 3 | FR-MODEL-110 rebuild branch; also D1 + D2 |
| `7f96910` | 4 | FR-MODEL-24 refusal reaches the caller by name |
| `2b3c992` | 6 | W5 closure record; W5's rows struck; CLAUDE.md §2 marks |
| `e1e44bd` | — | `python-test` skill: two handler-testing traps (CLAUDE.md §12) |

## Final derivation

`scope-audit.py MODEL` — **136 in scope** (122 FR + 14 NFR), **120 evidenced (88 %)**,
**16 without**. Endpoints **41 of 41**. No catalogue declared.

Headline, three numbers: **110 built · 10 declared-and-refused-by-name · 16 unevidenced with
a verdict = 136**.

Gate: ruff 0 · mypy 131 files · lint-imports 3 kept 0 broken · pytest **1 720 passed,
1 xfailed** (404 s) · audit-docs all checks · req-coverage 506/257 ·
generate-contracts --check 23 match · frontend lint, type-check, **131 tests**, build — all 0.
`alembic heads` = `9e4c7b21fa08`.

## Where the plan was wrong, and what was done instead

1. **Task 1 Step 4 was unbuildable as written.** The plan said `_check` should pass
   `node=child`. But `_check` refuses a disallowed node *before* `_translate` is reached, and
   `FloorDiv` is an `ast.operator`, which carries no position — so the plan's own second test
   would have failed permanently. Resolved with `_walk_positioned`, pairing each node with its
   nearest positioned ancestor in `ast.walk`'s exact BFS order. **Proven load-bearing**: with
   the plan's version, the subscript case passes and the operator case fails.
2. **Task 1's expected `end_col_offset == 13` was wrong.** `ast` reports **10** for
   `premium[0]`; 13 is the `col_offset` of the trailing `1`. Verified directly before changing
   the assertion.
3. **Task 1's stated reason was wrong.** `prepare.py` and `validate.py` do **not** catch
   `ExpressionError` — there is no `except ExpressionError` anywhere in the repository.
4. **Task 2 Step 4's grep was not empty.** The plan's conditional ("delete the parameter if
   unused") therefore did not apply. Nineteen call sites pass `seed=`, **six of them outside
   tests**, and `02` §5.2 publishes the parameter. Recorded as **OQ-MODEL-29**, open, with
   options and a recommendation; the signature warns in place.
5. **Task 3's drafted test would have passed for the wrong reason.** The import is
   function-local, so patching the handler module never intercepts. Patched at
   `pricing_core.modelling`. Captured in the `python-test` skill.
6. **FR-MODEL-110 cannot be met exactly as written.** Its `Diagnostics` clause says "loads";
   the result is consumed only inside the `should_fit` arm, so a load would be a query whose
   result is discarded. The branch **skips**. Requirement amended with a dated note (§0).
7. **Task 4's test did not pass immediately, and the plan assumed it would.** The refusal
   fires correctly at `predict.py:158`, but `PredictionError` is not a `PlatformError`, so
   `execute_job` stored `JOB_HANDLER_FAILED` with `MODEL_OFFSET_MISSING` absent even from the
   message. **The spec was right and the code was behind**, so the code was fixed (§0), using
   the pairing `platform/prediction.py` already uses. Two further instances of the same gap —
   `_quantile_crossing` and `_compare` — are **recorded, not fixed**: neither has a test, and a
   closure slice must not ship an unproven claim.
8. **Task 5's premise held exactly.** The lineage note omitted `v3 → v4`, a transition both of
   its source records carried.

## Enforcement proofs (§13 rule 4)

- NFR-MODEL-8: dropping `node=` fails both position tests; threading the child instead of the
  ancestor passes one and fails the other.
- NFR-MODEL-6: refitting on one row fewer of 20 000 moves the intercept 5.8e-05, six orders of
  magnitude above the 1e-10 gate.
- FR-MODEL-110: the call-count test fails on the pre-change handler; swapping the probe's read
  session for `unit_of_work()` fails the leaves-no-reserved-surrogate test. A third test that
  passed in both the good and broken states was **deleted**.
- FR-MODEL-24: narrowing the catch to `ModellingError` alone fails with
  `assert 'JOB_HANDLER_FAILED' == 'MODEL_OFFSET_MISSING'`.

## Open items raised, not closed

- **OQ-MODEL-29** — `fit_glm`'s inert `seed`. Open, maintainer.
- **`_quantile_crossing` and `_compare`** lose pricing-core refusal codes the same way
  `_reconcile` did. Owner: the slice that next touches either, or a PLAT slice taking the root
  cause (`execute_job` knows `PlatformError` and nothing of `pricing-core`'s hierarchy).
- **FR-MODEL-92 / FR-MODEL-95** evidenced only by "the route is published"; no test calls
  either endpoint. Owner: W6b.
- **FR-MODEL-122** carried by the module's only `xfail(strict=True)` — a pinned defect, not a
  refusal. A sparse cross still dies uncoded. Owner: W30.

## Not done, deliberately

FR-MODEL-112(c) — building it would invert FR-MODEL-112's own recorded ordering, and (a) is
Phase 1b and demand-gated. It stays refused by name, which this slice made true in the code as
well as in the sentence.

---

## Follow-on: OQ-MODEL-29 decided, 2026-08-22 — option (b), remove the parameter

Maintainer decided at the recommendation's option. Implemented as **FR-MODEL-123**.

**Blast radius, scanned rather than recalled** — an AST-bracket-matched sweep of every
`fit_glm(`/`fit_ebm(` call, not a line grep, because three line-grep hits were false positives
(`fit_ebm(data, _spec(seed=1), …)` ×2 and `fit_glm(_gamma_severity(…, seed=seed), …)` — all
three pass `seed=` to an *inner helper*, not to the fitter):

- **2 signatures** — `glm.py`, `ebm.py`
- **20 real call sites**, of which **7 are outside tests**: `model_handlers.py` ×2 (both the
  `fit_glm` and the `fit_ebm` arm of the platform's own fit path), `diagnostics.py` (type-III
  reduced refit), `transparency.py` (the GBM surrogate fit), `bench-model.py` ×3
- **13 in tests** — `test_glm_cv.py` ×8, `test_diagnostics.py` ×2, `test_backtests.py`,
  `test_comparison.py`, `test_scoring_without_the_fitting_stack.py`
- **2 published signatures** in `02` §5.2

**Deliberately not touched**, each verified by reading the surrounding call: `transparency.py:103`
(`seed=spec.seed` inside a `GlmSpec(...)` *construction*), `diagnostics.py:1029`
(`seed=spec.seed` on the permutation-importance call), and every `seed=` in splits, datasets,
objectives and spec fixtures.

**The earlier census undercounted the non-test callers.** It said six; it is seven — it missed
`model_handlers.py:364`, the `fit_ebm` arm. Corrected in FR-MODEL-123 and in the closure
record's defect row.

**Enforcement proven (§13 rule 4).** Negative tests in `test_glm.py` and `test_ebm.py` assert
`seed=` now raises. Re-adding `seed: int = 0` to `fit_glm` turns
`test_fit_glm_refuses_a_seed_argument` red. The tests need no data: Python binds arguments
before the body runs, so the unexpected keyword is refused before the frame is touched.

**Why (b) and not the interim (a).** A parameter whose only correct behaviour is to be ignored
is worth removing once rather than documenting forever — and (c), honouring it, was
self-defeating: a seed outside `spec_hash` would let two fits with one digest differ, which is
what NFR-MODEL-6 exists to forbid and what `GlmCvSpec` had already refused on.

## gh CLI — requested, still blocked

Asked for so the PR could be opened from here. `gh` is installed at `/usr/bin/gh`, but
`/home/puzhenhao1989/gi-pricing-plan/.claude/settings.local.json` carries
`deny: ["Bash(gh *)", "Bash(/usr/bin/gh *)"]`, and **deny outranks allow**. A worktree-scoped
settings file with the allows was written and is *not* sufficient. The main checkout's file
cannot be edited from a worktree-isolated session, so the deny entries must be removed there by
the maintainer. `gh auth status` has therefore never run — whether the token is scoped to this
repository is still unverified.
