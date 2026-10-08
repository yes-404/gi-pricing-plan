---
id: LG-9481
family: ledger
title: WK-673 slice SL-1448 — FD-1420, a lookup step reads the row in force as at its declared date (PL-1447), task ledger
status: active
created: 2026-10-08
owner: executor
tree: 0ee8f41452901bd2511379776f26075a6993dd13
phase: P2
work: WK-673
slice: SL-1448
plans: [PL-1447]
corrected_by: []
relates: [RL-1445, RL-1446, RL-1263, FD-1420, FR-221, WK-673]
---

# WK-673 slice SL-1448 — the FD-1420 fix, a lookup step reads the row in force as at its declared date

Executed from `PL-1447` by `executor-sl1448` (sonnet). Branch `sl-1448-fd-1420-lookup-reads-row-in-force-as-at`, worktree
`.claude/worktrees/sl-1448`, from `origin/main` `0ee8f41452901bd2511379776f26075a6993dd13` (#1235, the activation). The dispatch
record is `gi-pricing-plan.local/handover/DISPATCH-WK-673-SL1448-2026-10-06.md` (FINAL; a local file, not in the repository).
Stamps are BST (`TZ=Europe/London date`). `uv sync --all-packages` ran.

## Tasks

### Task 0 — preconditions and exposure (no code)

**Step 1, the exposure query**, run 2026-10-08 10:47 BST (09:47 UTC) from the plan's script. Last line, verbatim:
`DATABASES=7 TOTAL lookup_algorithms=0 multi_row_keys=0`. *Disclosure:* the plan's run read `93` databases and `2`
multi-row keys; the test-leftover databases have since been dropped. The expected `lookup_algorithms=0` holds.

**Step 2, the three greps**, run as `git grep` in the worktree with the plan's pathspecs; the plan ran `grep -rnI` for the
first. *Disclosure:* the commands differ, the counts agree: `0`, `0`, `10` (plan: `0`, `0`, `10`).

**Step 3, the open PRs** (`gh pr list --state open`, read at 2026-10-08): none edits a file under `packages/`. The ones that
bear on this write set are #1233 (head `3413b79a`, B2+B3 docs, carries RL-1474 and PL-1471/SL-1472), #1055 (head
`07d9d230`, the RL-1474 ruling), #1051 (head `c7621ca2`, PL 9776's plan). RL-1474's code move has not landed:
`class ValidationIssue` is still at `packages/pricing-core/src/pricing_core/rating/compile.py:60`, so Task 3 Step 1 imports
it from there.

**The moved-anchor table**, plan tree `caa4e411` against main `0ee8f414` (a `git diff` of the write-set files).
No definition this slice edits was changed beyond a line move: the body of `_decision_table_node` and the
`runtime.py` module docstring (lines 1-37) are identical at both trees, and the FR-221 row at `03-rating-engine.md:107` is
unchanged.

| Anchor | Plan | Main |
|---|---|---|
| `runtime.py` `_decision_table_node` def; its `lookup` branch | `:240-253` (branch) | `:207`; `:250` |
| `runtime.py` `content_hash` | `:673` | `:669` |
| `score.py` `score_one` | `:876` | `:898` |
| `score.py` `_score_context_sync` | `:1045` | `:1068` |
| `score.py` engine context (`"effective_date": ctx.effective_date.isoformat()`) | `:910-912`, `:1066-1068` | `:934`, `:1091` |
| `compile.py` `ALGORITHM_CHECKS`; `ValidationIssue` | `:359`; — | `:359` (unmoved); `:60` |
| `authored.py` `EXPRESSION_FIELDS`, `NON_EXPRESSION_FIELDS` | `:44`, `:53` | unmoved |
| `test_rating_runtime.py` `test_lookup_step_wire_translation_matches_by_key` | `:435` | `:435` (unmoved; #1228 changed `:346`, not mine) |
| `test_quote_input_raise_sites.py` `_INPUT_FREE` | `:62` | `:62`; #1227 added two entries inside it |
| `test_rating_score.py` `test_a_reference_lookup_miss_is_refused` | `:383` | `:383` |
| `test_rating_pin_membership.py` `_lookup_algo`, `_veh_algo` | `:57`, `:229` | `:57`, `:229` |
| `test_rating_authored_fields.py` enumerator test, reason test | `:103`, `:187` | `:103`, `:187` |

**Disclosure, #1227's shadowing check.** `score.py` now holds `_check_no_shadowed_produced_names` (def `:436`, SL-1430),
called in `score_one` at `:922` and in `_score_context_sync` at `:1088`. The `_check_as_at_values` calls (Task 3) go
beside them. That check refuses an input that shadows a name a step *produces*; the stamped `effective_date` is not a
produced name, so the plan's run-time value check is not obviously redundant. Task 3 re-reads the function; if any plan
step is redundant or contradicted by it, that is a STOP to the lead, not a silent drop.

### Task 1 — the pricing-core reds, at base `0ee8f414` (tests only)

The module `packages/pricing-core/tests/test_rating_lookup_as_at.py` is the code of Task 1 Steps 1 and 2, extracted from
the plan by script (the one import line moved to the import block, as Step 2 says) and `ruff format`ted. Run
2026-10-08, `OMP_NUM_THREADS=1 nice uv run pytest -q -rf packages/pricing-core/tests/test_rating_lookup_as_at.py`, both gate
slots free: `16 failed, 2 passed in 13.77s`, matching the plan's Run 7 (`16 failed, 2 passed`).

- **Failed `AssertionError: the superseded row's rate returned`** (5): `test_score_one_prices_on_the_row_in_force`
  `[2026-01-01-at-from]`, `[2026-06-01]`, `[2099-01-01-open-ended]`; `test_score_batch_prices_on_the_row_in_force`;
  `test_a_date_input_named_by_as_at_selects_the_row`.
- **Failed `DID NOT RAISE`** (11): `test_score_one_misses_before_every_row`; the three compile refusals
  (`test_as_at_naming_a_non_date_input_is_refused_at_compile`, `test_as_at_naming_an_undeclared_value_is_refused_at_compile`,
  `test_a_declared_effective_date_must_be_date_typed`); the six `test_a_malformed_as_at_value_is_refused_not_missed`
  values; `test_an_input_shadowing_effective_date_is_checked`.
- **Passed (the controls)** (2): `[2020-01-01-at-from]`, `[2025-12-31-before-to]`.

Every red has the cause the plan predicts; no unexpected pass.
