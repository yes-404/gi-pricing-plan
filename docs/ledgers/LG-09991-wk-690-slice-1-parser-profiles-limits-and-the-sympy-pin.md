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

## PRs

Draft PR opened on the slice branch; number recorded here when opened.
