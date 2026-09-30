---
id: LG-9979
family: ledger
title: WK-690 Slice 2 — symbolic derivation, the compilation target and the expression certificate
status: active
created: 2026-09-30
owner: executor
tree: 71b672205f7212008d0ff00b5cbc4810b56f12e6
phase: P2
work: WK-690
slice: SL-1272
plans: [PL-1327]
corrected_by: []
relates: [RL-1328, RL-1265, RL-1289, RL-1291, RL-1292, RL-1293, RL-1263]
---

# LG-9979 — WK-690 Slice 2 (SL-1272)

Executed from `PL-1327`. Branch `sl-1272-symbolic-derivation`, from `origin/main` `1dae2081`, then
main merged to `71b67220` (#1019, docs only). Working id 9979, reserved by the lead 2026-09-30 22:41 BST;
minted at the merge turn.

## Tasks

### Task 0 — preconditions

Executor check: `echo CLAUDE_EFFORT=$CLAUDE_EFFORT` → `CLAUDE_EFFORT=medium`. `executor.md:13` begins
"`sonnet` (currently Sonnet 5); medium, inherited from the lead — the highest-volume role;".

**The dispatch record, quoted verbatim** (`gi-pricing-plan.local/handover/DISPATCH-WK-690-S2-2026-09-30.md`, FINAL; the DRAFT is superseded):

> # Dispatch record — WK-690 Slice 2 (SL-1272), from PL-1327 — FINAL
>
> **Status: DISPATCHED 2026-09-30 22:59:52 BST** (lane A GO by the lead). The maintainer checked this record and cleared GO in their entry after the #1019 ACK. Drafted 22:42:16 BST. main at GO: `71b672205f7212008d0ff00b5cbc4810b56f12e6` (#1019's squash, roadmap and INDEX only, on top of #1018's 1dae2081). The executor's ledger Task 0 quotes this record verbatim, per the maintainer's "2026-09-30 14:48:52 BST" item (3): activation facts live here, not in the frozen plan.
>
> - **Plan:** PL-1327 (minted in batch 8, #1011, audited in that batch's mint-delta audit). Activated by the `status:` flip in #1018 (auditor-1018 CLEAN at 8209ace8).
> - **Slice:** SL-1272 → `active` in #1018 (the lead dispatches).
> - **Rulings:** RL-1328 rules DP-S2-1 to DP-S2-6. Task 0 quotes each by id.
> - **Lane:** A, under RL-1263: at most 2 build slices, from different Works; provisional, 0 of 3 counted pairs. The lane order was agreed by the maintainer at 22:33:30 BST (Decision 4).
>
> ## Activation facts
>
> 1. PL-1327 and SL-1272 are `active` on main: #1018 was squash-merged 2026-09-30 22:57 BST, origin/main `1dae2081c7dba50e27e7d6644677ebc4f4d96bd7` (parent 8cef871d, tree 0fe2017b), on the maintainer's MERGE-ACK #1018.
> 2. RL-1328 is on main (#1011).
> 3. **Lane A grant: 2026-09-30 22:59:52 BST**, by the lead, at main 71b67220, with this record's write-set check. Lane B is idle at the grant.
>
> ## Conditions
>
> 1. **Write set:** PL-1327 §"Write set, and contention under RL-1263 option (c)" (`PL-1327:90-127`), verbatim.
> 2. **RL-1263 write-set check against lane B:**
>    - At GO, lane B is **idle**. WK-674 S3 dispatches at PL 9947's mint (~03:30 BST Thu 1 Oct), and S3's dispatch record carries its own check against this slice.
>    - **Against WK-1250 S1 (PL-1325), if it overlaps later:** one shared non-exempt path, `packages/model-schema/src/model_schema/__init__.py`, where both append exports. They may run together only on the rule that **no existing line is edited by both**. The second to merge merges main in and re-runs its full gate. The maintainer confirmed this at 22:33:30 BST, Decision 4.
>    - Registry-exempt paths (RL-1263:104-116): the generated `docs/contracts/` outputs and `docs/INDEX.md`. The later slice regenerates them at its merge.
> 3. **Task 6, the NFR-476 timing measurement, runs ALONE** (RL-1263 item 3). Before starting it, the executor asks the lead for a solo window. The lead grants it only with the other gate slot empty and no lane-B gate running, and records the grant here as a delta. Every other task may run beside a lane-B slice.
> 4. **Gate evidence, for EVERY suite-level run and the full gate** (the maintainer's rules of 2026-09-30, ~18:0x and ~18:4x BST, and the #1012 lesson). Record each of these in the ledger:
>    - a **clean checkout of the named SHA**, with `git status --porcelain` empty at start;
>    - `ruff check --no-cache`, and mypy on a fresh cache dir or with `--no-incremental`;
>    - the **dev-commands slot wrapper verbatim** (`.claude/skills/dev-commands/SKILL.md:122-171`), plus `LOKY_MAX_CPU_COUNT=4`, run in the foreground with a `timeout`, per executor.md S-11. The harness backgrounds at 600s: wait on the output and never relaunch;
>    - `uptime` **and** `free -h` at start and at end;
>    - **the other holder**, identified as gate or not-gate, with `flock -n <slot> -c true`, never inferred;
>    - wall time, and pytest time against the solo baseline (1469.6s; step-down line 1.5× ≈ 2204s).
>    A genuinely concurrent gate pair with S3 is an RL-1263 pair candidate. **A missing field disqualifies it.**
> 5. **After merging main that adds a migration,** run `alembic upgrade head` on the worktree's per-worktree test DB before the gate (the stale-DB trap, 30 Sep).
> 6. **Red first:** every acceptance item as PL-1327 states it.
> 7. **Gate:** the full two-half gate before pushing (CLAUDE.md §11). Docs checks run on a clean detached checkout of the pushed commit.
> 8. **Ledger:** an `LG-` record under working id **9979** (the lead reserved it at 22:41 BST; checked free). It mints at the merge turn. The lead is the ONLY allocator of working ids (FD-1338): ask, never pick.
> 9. **Plans are frozen by family** ("14:44:36 BST"): nothing in `docs/plans/` is edited. Frozen record bodies are never edited (document-ids :135).
> 10. **Holds (FD-1336, FD-1335):** not applicable. This slice reads no ladder rung values and consumes no /score or open-object route. The executor confirms this in Task 0.
> 11. **Executor:** a fresh `executor-690s2`, spawned from `.claude/roles/executor.md` with its Model / effort line verbatim (sonnet, medium). Its worktree is new, from `origin/main` after #1018 merges. Its first act is `echo $CLAUDE_EFFORT`. It never `cd`s: the hook path is relative.

**Rulings by id.** RL-1328 rules DP-S2-1 (c, primitive arguments with the existing `YDomain` and
`HessianStrategy`), DP-S2-2 (a, printer rewrites into the objective grammar; the dropped `DiracDelta` is named by
`branch_discontinuity`), DP-S2-3 (a, 30 s per round on the objective callable, `OBJECTIVE_ROUND_BUDGET_EXCEEDED`),
DP-S2-4 (b, value-free coded text; ranges as structured attributes), DP-S2-5 (a, numeric on the grid, with bounded
refinement) and DP-S2-6 (a, 1 M × 60 × 100 reduced shape, N ≥ 3, near-bound rule).

**Holds (condition 10): confirmed not applicable.** This slice reads no ladder rung values (FD-1336) and consumes no
/score or open-object route (FD-1335): its write set is `pricing-core` modelling, the `model-schema` battery, one
hand-authored contract, `scripts/bench-model.py` and `02`.

**Premises a–m re-derived at `1dae2081` (tree of main at the base; #1019 touched `docs/` only).** All hold; line
numbers drifted by at most five (e.g. `_the_battery_is_all_nine_named_checks` at `model_schema/objectives.py:755`,
`_only_templates_are_built` at `:481`; `_finite_or_abort` at `objectives.py:698`; adapters at `:716` and `:739`).
Command for l: `for id in FR-146 FR-147 FR-148 FR-149 FR-151 FR-165 NFR-476 NFR-483; do git grep -c "req(\"$id\")" -- ':(glob)packages/*/tests/**' ':(glob)backend/tests/**'; done`
summed per id: 13, 1, 3, 2, 3, 4, 0, 9, as the plan states. Premise h: `grep -o -E 'OBJECTIVE_[A-Z_]+' docs/specs/02-modelling.md | sort -u | wc -l` → 13, one of which (`OBJECTIVE_STATUSES`) is a
fragment, as the plan states.

**Open PRs** (`gh pr list --state open`, 2026-09-30, after #1019): none touches `pricing_core/modelling/`,
`model_schema/objectives.py`, `objective-certificate.schema.json`, `02` §4.6, §4.7 or §5.1, or `scripts/bench-model.py`
(filtered on those path substrings over every open PR's file list).

### Task 1 — spike: the derivative vocabulary and the size of derived text (DP-S2-7)

Recorded as the `RS-` of kind `spike` named in `## Relates` below. Scratch scripts `scratch/spike.py` (sha256
prefix `f13d2472095379f9`) and `scratch/printer.py` (prefix `10d6760957b39d2d`), not committed; the printer is the Task 2
printer's first form.

- Vocabulary (sympy 1.14.0, `real=True`): `abs` → `sign`; hessian `DiracDelta`. `min`/`max`/`clip` → `Heaviside` in the
  gradient, `DiracDelta` (plus `Heaviside` where the argument is nonlinear) in the hessian. `where` → `Piecewise`.
  `log`, `sqrt`, `log1p`, `expm1`, `exp` → no head but `exp`/`Pow`. `Heaviside(0) = 1/2`. This agrees with premise i and RL-1328's spike.
- Size, `ast.expr` nodes and depth (`measure_expression`, RL-1291's predicate), loss → gradient → hessian, after
  `piecewise_fold` and the printer, every head rewritten:

  | loss | loss | gradient | hessian |
  |---|---|---|---|
  | §4.6 example | 19 / 6 | 41 / 7 | 61 / 8 |
  | `abs(y-f)` | 7 / 4 | 26 / 8 | 1 / 1 |
  | `clip(f,0,y)` | 7 / 3 | 25 / 7 | 1 / 1 |
  | `max(y,f)*where(f<y,2,3)` | 14 / 4 | 37 / 8 | 1 / 1 |
  | nested `exp` (161 nodes) | 161 / 20 | 87 / 13 | 505 / 18 |
  | nested `where` (193 nodes) | 193 / 18 | 11 / 4 | 11 / 4 |
  | 19-deep `log1p` chain | 39 / 20 | 474 / 22 | **9081 / 40** |

  (nodes / depth.) Maximum derived size: **9081 nodes, depth 40**, both the `log1p` chain's hessian: no common-subexpression
  elimination, so the chain rule's repeated factors multiply. The ratio `max(nodes_hess / nodes_loss)` is 232.8 and
  `max(depth_hess / depth_loss)` is 2.33. The rule of Task 1 gives `DERIVED_LIMITS = ExpressionLimits(max_nodes=18200, max_depth=80)`
  (maxima × 2, rounded up to a multiple of 100 nodes and 10 depth). The result is conclusive, so the 2000/200 fallback does not
  apply, and it would refuse a 39-node loss.

### Task 2 — `derive` and the grammar printer (`cc6e3cc8`)

Red, before `expression_objective.py` existed (`uv run pytest packages/pricing-core/tests/test_expression_objective.py`):
`ModuleNotFoundError: No module named 'pricing_core.modelling.expression_objective'`. Green: 8 passed. Mutation control, the
`DiracDelta` handling removed from `to_grammar` (the `replace` and the `_print` branch): the `abs` and `clip` cases fail
with `ExpressionError: DiracDelta cannot be printed in the objective grammar` (2 failed, 6 passed); restored, 8 passed.
`DERIVED_LIMITS = ExpressionLimits(max_nodes=18200, max_depth=80)` from Task 1.

### Task 3 — `compile_kernel` (`1617b64a`)

Red: `ImportError: cannot import name 'compile_kernel'`. Green: 11 passed, and the NFR-483 test passes alone in a fresh process
(`-k built_without`, 1 passed). Mutation control, `where` mapped to its `then` branch alone: `test_a_kernel_agrees_with_sympy…`
fails (1 failed, 10 passed); restored, 11 passed.

### Task 4 — `ObjectiveFns` for expressions, the per-round budget, the NaN abort (`327f8896`)

Red: `ImportError: cannot import name 'RoundBudgetExceededError'` (collection). Each cause-level red was then staged by mutation on
the finished code: with the budget comparison replaced by `if False:`, **4 failed, 62 passed** (the four slow-objective aborts, both
adapters × both kinds); with the row ranges written into the error text, **2 failed, 64 passed** (the two no-value assertions).
Restored: 66 passed. `DP-S2-4`'s test changes: **none.** The plan named `test_objectives.py:453, :471, :493, :517`; at this tree the
FR-165 tests are at `test_a_non_finite_derivative_aborts_naming_the_round_and_the_inputs` (asserts `"round 41"` and `"2 of 3 rows"`)
and `test_a_finite_pair_does_not_abort`, and neither asserts on the range text, which was the only text removed. The
template tests otherwise pass unmodified. The spec (`02` §5.1, FR-165) is amended in the same commit.

### Task 5 — the expression certificate (`0a5a04a6`)

- **model-schema red:** `ImportError: cannot import name 'OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC'` (collection); mutation control,
  the validator's symbolic branch forced off: 2 failed (the symbolic battery, and the mixed-pairs refusal), 4 passed.
- **pricing-core red:** `ImportError: cannot import name 'certify_expression_objective'`. Green, 18 selected tests passed.
  Mutation controls, each on the finished code:

  | control | result |
  |---|---|
  | found-branch mask disabled | `test_expression_certificate_spec_example` fails: the gradient detail's excluded count is 0 and, without exclusion, the derivative comparison straddles the kink and fails |
  | boundary sampling (`_sample_found_boundaries`) disabled | the same test fails (no sampled point lands within `h` of the kink) |
  | sign-change test disabled | `…catches_a_sign_change_with_no_zero_on_the_grid` fails; **the plan's `/ f` case still fails `finiteness`**, because the refinement also finds the zero of `abs(f)` |
  | refinement disabled | `…catches_an_even_order_zero` fails |

- **Contract guard.** The hand-authored enum (`objective-certificate.schema.json`) gains the two symbolic names and a dated
  `$comment` line; `generate-contracts.py` and `--check`: "31 contracts up to date", "31 generated contracts match the models".
  **`backend/tests/test_contracts.py` does not compare this enum**: with the two new names replaced by `"BOGUS"`, it still reports
  144 passed, 2 skipped (and 144 passed, 2 skipped with the correct enum). The check-name enum is unguarded against the
  model; recorded here for the lead, not fixed in this slice.
- **`test_template_certificate_unchanged`** compares each of the 12 templates' certificates, name, status, detail (smoke-fit seconds
  normalised) and `overall`, with `packages/pricing-core/tests/data/template_certificates_before_wk690s2.json`. The reference
  was produced by `certify_objective` on the test file's own `_objective` and `_sampling` **from a `git archive` of `71b67220`
  (`packages/pricing-core/src`, `packages/model-schema/src`)**, `PYTHONPATH` first, with `71b67220`'s copy of `test_objectives.py`;
  the same script on this branch's Task 4 commit gave a byte-identical file (`diff` empty).

## Deviations from PL-1327, each named

1. **The NFR-483 test** cannot replace `builtins.compile` outright: `ast.parse`, which `parse_expression` calls, goes through
   `compile` with `PyCF_ONLY_AST`. The raiser refuses every `compile` call without that flag. The plan's positive control
   (`sympy.sympify`) is not one of the patched names and would not raise, so the controls are `sympy.lambdify`, `parse_expr` and
   `builtins.compile("1 + 1", …)`.
2. **`compile_kernel` broadcasts to the shape of all three inputs**, not `y.shape` (the plan's text): the certificate's minimiser
   scan calls `grad` with `(N,1)`, `(N,2001)` and `(1,1)` arrays.
3. **`ObjectiveFns` carries one `_expression: ExpressionKernels | None`** (loss, grad, hess, inverse link, found conditions,
   found denominators) instead of three optional kernel fields. `compile_expression_objective` also takes `inverse_link`, as the plan's
   text says it would, and refuses `gauss_newton` (OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED), as a template does.
4. **`certify_expression_objective`** takes `sampling` and an optional `derived`; the smoke fit's synthetic response is chosen by
   the inverse link (`exp` → claim severity, `logistic` → conversion) because the primitive arguments carry no `responses`. It
   lives in `expression_objective.py`, over a shared `certify_compiled` in `objectives.py`, so `objectives.py` does not import sympy.
5. **A sampling step the plan did not write.** FR-147's count must be non-zero on §4.6's example, and a uniform draw lands within
   `h` of the boundary with probability about 1e-4 per point. `_sample_found_boundaries` moves a tenth of the grid's tail onto each
   found condition's flip point by bisection; a template's grid is untouched (the unchanged test above).
6. **Denominators include a negative constant power.** SymPy writes `1/x` as `x**-1`, and the printer prints `(x) ** (-1)`, so derived
   text holds almost no `/`. A divisor is the right operand of `/` (not a bare constant) or the base of a negative-constant `**`.
   The plan's sign-change control did not isolate the clause (see Task 5's table), so a separate test uses a denominator that
   jumps from −1 to 1.
7. **Task 6's arms** are two `xgb.train` calls over one `DMatrix`, builtin `count:poisson` against `make_xgb_objective` of the
   compiled expression, because `fit_gbm` takes a `CustomObjective` artifact, which has no expression fields until Slice 3.

## PRs

None yet.
