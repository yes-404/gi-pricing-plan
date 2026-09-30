---
id: LG-9991
family: ledger
title: WK-690 Slice 1 — the parser brought to §4.6's four profiles, with its limits and the sympy pin
status: active
created: 2026-09-30
owner: executor
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-690
plans: [PL-1295]
corrected_by: []
relates: [RL-1289, RL-1291, RL-1292, RL-1293, FD-1294]
---

# LG-9991 — WK-690 Slice 1 (SL-1271)

Executed from `PL-1295`. Branch `sl-1271-arity-refusal`, from `origin/main`
`9f63d0feee524815e7e0c68c99a53ac3f80e6c37`. Working id 9991, confirmed free by the lead
2026-09-30 10:54 BST; minted at the merge turn.

## Tasks

### Task 0 — preconditions

**The dispatch record, quoted verbatim** (`gi-pricing-plan.local/handover/DISPATCH-WK-690-S1-2026-09-30.md`):

> # Dispatch record — WK-690 Slice 1 (SL-1271), from PL-1295
> 
> **Dated:** 2026-09-30, by the lead. Every condition below is a maintainer decision recorded in `~/gi-pricing-plan.local/channel/to-lead.md` on 2026-09-30. The executor quotes this record verbatim in its ledger's Task 0.
> 
> - **Plan:** `PL-1295` (active), merged by #954, on main `9f63d0feee524815e7e0c68c99a53ac3f80e6c37`.
> - **Rulings:** RL-1291 (DP-S1-1), RL-1292 (DP-S1-2, exact arity), RL-1293 (DP-S1-3), RL-1289 (`sympy==1.14.0`).
> - **Finding delivered:** FD-1294 (HIGH), the arity drop.
> - **Lane:** B, under `RL-1263`. It takes one of the two build slots. The other slot is for WK-674 Slice 2 when dispatched.
> 
> ## Conditions
> 
> 1. **Shared paths (RL-1263 :100).**
>    - `docs/specs/03-rating-engine.md`: S1 edits only FR-244's row, §3.5.
>    - `uv.lock` and `packages/pricing-core/pyproject.toml` (the sympy pin), and `docs/skills-map.md`.
> 
>    If WK-674 S2 is dispatched while S1 is open and its write set touches `uv.lock` or `pyproject`, S2 serialises behind S1's dependency change merging first. The S2 dispatch record states that check.
> 2. **Dependency PRs held.** Dependabot and any dependency PR stay unmerged while S1 is open.
> 3. **The `??` operator.** S1 must not change `??` semantics, `_GUARD_MARKERS`, `_check_vocabulary` or compile.py's validators. The `??` / FR-244 ruling is #967 (RL working id 9904), and its code is a later WK-1178 slice.
> 4. **A held sentence (a dated delta; the plan is frozen).** PL-1295 Task 6's sentence "the rating grammar is ZEN's expression language, restricted to the function list above" (PL-1295 lines 1538-1543 at #954's head `57a4833e`) is **held**.
>    - The rest of Task 6 proceeds.
>    - When #967 is minted, the executor writes **the minted #967 record's "amended FR-244 text"**, not the draft's, in place of the held sentence, before S1 closes.
>    - If #967 has not minted by S1's close, the sentence is carried by name to #967's slice.
> 5. **Contention measurement (RL-1263).** At the first overlap of this slice's gate with a WK-674 gate, run the three-pair contention measurement, solo run first (baseline about 20m53s, 1.5x step-down). Record it in the ledger.
> 6. **Gate.** Run the full two-half gate locally before pushing (CLAUDE.md §11). Measure the docs checks on a detached checkout of the pushed commit.
> 7. **Ledger.** An `LG-` record under a working id, minted at the merge turn. Task 0 quotes this record and re-reads the plan's premises at the tree.

**Baseline.** `uv run pytest -q` at `origin/main` `9f63d0fe`, in this worktree, under
`/tmp/slots/gate-1` (lead's grant 2026-09-30), `timeout 3600`: rc 0,
**3881 passed, 3 skipped in 1949.11s (0:32:29)**. Solo run on the box at the time as far as the lead
reported; slower than RL-1263's ~20m53s baseline, so noted, not a contention pair.

**Premises re-derived at `9f63d0fe`.**
- a: `git grep -n -E "compile_expression|referenced_columns" -- packages backend examples` — source sites `prepare.py:167`, `:170`, `validate.py:1892` (import) and `:1899`; tests `test_prepare.py` (8 hits) and `test_expression_nfrs.py` (7). Holds.
- c: `expressions.py` `_call` reads `args[0]` for the seven legacy functions, `round` uses `digits = 0`. Holds.
- b, d–i: re-derived as each task reaches them.

**Open PRs read** (`gh pr list --state open`, 2026-09-30): none touches `pricing_core/data/`,
`uv.lock`, any `pyproject.toml`, `02` §4.6–§4.8, `03` §3.5 or `skills-map.md`. #967 (FR-244,
working id 9904) is ruled, not minted: the held sentence of Task 6 stays held.

### Task 1 — the sympy pin (RL-1289)

Step 2, red first (`uv run pytest tests/test_sympy_pin.py -q`, before the pin):

```text
FAILED tests/test_sympy_pin.py::test_the_lock_resolves_sympy_exactly_once_at_the_pin - AssertionError: assert ['sympy is ab...rom the lock'] == []
FAILED tests/test_sympy_pin.py::test_pricing_core_declares_the_exact_pin - AssertionError: assert 'sympy==1.14.0' in ['model-schema', 'hypothesis==6.1...
2 failed, 3 passed in 0.39s
```

The three broken-lock cases passed, as the plan expects. Green after the pin: `5 passed`;
`import sympy` prints `1.14.0`. `git diff uv.lock | grep -E '^\+name = '` prints `mpmath` and
`sympy` only. Acceptance 3's grep on §4.6–§4.7 hits the example line, the RL-1289 note and
the §4.7 example, as listed there. `python3 scripts/audit-docs.py`: All checks passed.

### Task 2 — the node and depth counter, and the corpus measurement

Step 2 red: `ImportError: cannot import name 'ExpressionSize'`. Step 4 green: 6 passed.
`ExpressionSize`, `measure_expression`, `_measure` are added; nothing enforces them yet.

**Corpus measurement** (Step 5). Instruments: runtime capture (`/tmp/capture_expressions.py`,
the plan's plugin) over `uv run pytest packages/pricing-core/tests examples/fremtpl2`
(31 distinct strings reach the parser), and the static sweep
`git grep -n -E '"(expression|expr)": *"' -- backend/tests examples '*.json'`
(one `derive`/`filter`/`check` hit, `backend/tests/test_data_jobs.py:389`; the other five
hits are ZEN rating steps, dropped per premise a). Classification of the 31 is mine.

Corpus, **8 distinct expressions from 2 files** (`packages/pricing-core/tests/test_prepare.py`,
`test_expression_nfrs.py`, plus `backend/tests/test_data_jobs.py` for the static hit
`exposure_years > 0`, already among the 8). Max nodes 11, max depth 4. None exceeds 200 / 20.

| expression | nodes | depth | all_nodes | source |
|---|---|---|---|---|
| `premium / exposure` | 3 | 2 | 6 | test_prepare.py |
| `premium / exposure_years` | 3 | 2 | 6 | test_prepare.py |
| `exposure_years > 0` | 3 | 2 | 5 | test_prepare.py, backend test_data_jobs.py |
| `exposure_years > 0.3` | 3 | 2 | 5 | test_prepare.py |
| `exposure_years > 0.75` | 3 | 2 | 5 | test_prepare.py |
| `premium if exposure > 0.75 else 0` | 6 | 3 | 9 | test_prepare.py |
| `round(premium / exposure) + abs(adjustment)` | 9 | 4 | 16 | test_prepare.py |
| `round(premium / exposure) + abs(premium - 100)` | 11 | 4 | 19 | test_expression_nfrs.py |

**Refusal fixtures, not corpus** (17): `(lambda: 1)()`, `(lambda: eval('1'))()`,
`[eval(x) for x in premium]`, `[x for x in premium]`, `__import__('os').system('ls')`,
`compile('1', '<s>', 'eval')`, `eval('1')`, `exec('x = 1')`, `f'{premium}'`, `globals()`,
`mean(premium)`, `open('/etc/passwd').read()`, `premium.__class__`, `premium.__class__.__mro__`,
`premium[0]`, `premium[0] + 1`, `exposure + premium // 2`. The 31 also
holds 6 strings that are this task's own new test fixtures — `a + b`, the two nested `abs`, the two
`min(x, …)` and §4.6's example loss — captured because the counter parses through the same module.
31 = 8 + 17 + 6.)

Both predicates are within limits for every corpus expression, so no deputy decision is needed
(Acceptance 4: the Task 2 commit precedes Task 4's).

### Task 3 — the four profiles, where(), the new functions, the strict refusals

Applies RL-1292 (DP-S1-2 (b), exact arity) in `_ARITY` and `_check`.

**Red before the code** (FD-1294, at `9f63d0fe`, the three caller tests run against the
unmodified parser through a temporary file carrying only names that existed there):

```text
FAILED …test_round_with_two_arguments_is_refused_through_the_callers_derive_expression - Failed: DID NOT RAISE ExpressionError
FAILED …test_round_with_two_arguments_is_refused_through_the_callers_filter_rows - Failed: DID NOT RAISE ExpressionError
FAILED …test_round_with_two_arguments_is_refused_through_the_callers_expression_check - Failed: DID NOT RAISE ExpressionError
3 failed
```

The temporary file was deleted. The profile and hostile-input files were red as
`ImportError` (`GrammarProfile`) before the implementation.

**Deviation from the plan's Step 2:** I did not run the intermediate "names exist, checks
not written" red. I replaced it with mutation controls on the finished code, both in
`test_expression_profiles.py`: with the arity check disabled, **12 failed, 42 passed**; with
`_check_structure` disabled, **6 failed, 48 passed**. Both restored; the file passes 54/54.

**Green.** `uv run pytest packages/pricing-core/tests -q`: 1059 passed (rc 0),
including `test_prepare.py` and `test_expression_nfrs.py` unmodified (Acceptance 6). `ruff check .`
rc 0, `mypy` no issues in 209 files, `lint-imports` 4 kept 0 broken. Spec notes (RL-1265 DP-5,
RL-1292 arity) added to 02 §4.6.

### Task 4 — the limits, enforced in all four profiles (RL-1291)

Precondition: Task 2's commit `4b5bc5e1` is an ancestor of HEAD (Acceptance 4).

Red 1: `ImportError: cannot import name 'ExpressionLimits'`. Red 2, with `ExpressionLimits`
and a stub check that measured but did not enforce: **9 failed, 10 passed** — every refusal
case `DID NOT RAISE ExpressionError` (201 nodes ×4 profiles, depth 21 ×4, configurable limits),
and the accept cases (200 nodes, depth 20, ×4 profiles) passed as the positive control.
Green after enforcement: `uv run pytest packages/pricing-core/tests -q` **1072 passed** (rc 0);
ruff rc 0; mypy no issues in 209 files; lint-imports 4 kept, 0 broken. Spec delivery note added to 02 §4.6.

Timing note: uptime load at Task 3–4 start was about 14.6 (lead's ruling on timed gates: applies
to full gates; the full gate has not been run yet).

### Task 5 — the objective profile, translated to SymPy (RL-1293)

Step 1 spike (locked sympy): `1.14.0 1/(x + 1)`. Red: `ModuleNotFoundError: No module named
'pricing_core.data.expression_sympy'`. Green: 18 passed; the `never_reaches` raiser test alone in
a fresh process: 1 passed. ruff rc 0; mypy no issues in 210 files (the plan's `Callable` annotation on
`_BINARY` was needed, no `type: ignore`); lint-imports 4 kept, 0 broken; only `expression_sympy.py` imports sympy.

**Mutation control for RL-1293** (symbols built without `real=True`): 9 of 18 fail, including
`test_every_objective_symbol_is_real` and `test_the_spec_example_gradient_and_hessian_are_reproduced`.

**Defect in the plan's test, found by that run and fixed here.** `test_the_abs_derivative_is_the_real_one`
did NOT fail under the mutation: the test module's `f` is real, so differentiating a loss built from
plain symbols with respect to it gives 0, and `not derivative.has(re, im, Derivative)` holds vacuously.
I added `assert derivative == w * sympy.sign(f - y)`; under the same mutation it now fails
(`assert 0 == (w * sign(f - y))`). The plan's file is frozen; this is a deviation from its test text.

**Slot rule (maintainer, 11:43 BST, relayed by the lead).** The Task 3 (1059 passed) and Task 4
(1072 passed) `pytest packages/pricing-core/tests` runs, and the Task 2 corpus capture run, were
unslotted and uncapped (144% CPU plus loky workers, per the lead's reading of load at 10:43Z). Every
later suite-level run is slotted with `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`.

### Task 6 — RL-1265 DP-5: 03 FR-244 and the matching 02 §4.6 note

Dispatch condition 4 applied. **Held:** the sentence "the rating grammar is ZEN's expression
language, restricted to the function list above". The rest of Step 1 is written, with two
consequences I chose and report: (1) the plan's clause "'The same restricted grammar as `02` §4.6'
is superseded by this sentence" would point at the held sentence, so it reads "by this amendment";
(2) the amendment says in the row that one sentence is held for #967. When #967 mints, the executor
writes the minted record's "amended FR-244 text" there before S1 closes, or the sentence is carried
by name to #967's slice. `??`, `_GUARD_MARKERS`, `_check_vocabulary` and `compile.py` are untouched
(`git diff origin/main --stat -- packages/pricing-core/src/pricing_core/rating` is empty).

### Task 7 — the gate (head `2bce55466d70`)

Lead's grant: gate-1 for `2bce5546`, 2026-09-30. Both halves in one `flock -w 1800 -E 99
/tmp/slots/gate-1` hold; caps `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`
(+ Polars/Rayon/Tokio 4). Python stages ran in parallel, then the frontend stages in sequence.

**Timing.** Start 10:48:07Z, load 3.70 / 5.94 / 8.19. End 11:17:29Z, load 7.76 / 5.62 / 6.85.
Wall clock 29m22s (pytest 1646.81s = 27m26s). Slot files present: `gate-1`, `gate-2`, `verify-1`;
I did not identify a holder of gate-2 (the lead reported both slots free at 10:47:49Z). No WK-674 gate
overlapped, so the RL-1263 three-pair measurement did not fire. Task 0's baseline (1949.11s) had no
load record; this run is 0.84x of it.

| stage | rc |
|---|---|
| ruff, mypy, lint-imports, req-coverage, generate-contracts --check | 0 |
| frontend: install, generate:api, lint, type-check, test, build | 0 |
| audit-docs | **1** (check 31 only: `gap in the full allocation between 1295 and 9991`) |
| pytest | **1**: 13 failed, 4024 passed, 3 skipped (main: 3881 passed, 3 skipped) |

**All 13 pytest failures come from the one working id.** Each is a test that runs the docs audit
or `doc-id check` on the real tree, and each shows `[noncontiguous] … gap between 1295 and 9991`
(check 31) or the audit output that carries it; the two tests that name the gap directly are
`test_doc_id_check_exits_0_on_the_real_tree` and `test_an_index_skipping_a_reserved_block_breaks_contiguity`
(`the live allocation is not contiguous: [(1295, 9991)]`). This is the memory-recorded
"a working-id draft reds check 31 until minted", rc 1 expected. Removing the cause is the mint
turn, which is the lead's: on minting, the ledger takes the next free id and the gap closes. These 13
were not shown to pass on this tree. The 4024 passed includes +143 over main's 3881: the new
tests were collected (Acceptance 10).

## PRs

Draft PR opened on the slice branch; number recorded here when opened.
