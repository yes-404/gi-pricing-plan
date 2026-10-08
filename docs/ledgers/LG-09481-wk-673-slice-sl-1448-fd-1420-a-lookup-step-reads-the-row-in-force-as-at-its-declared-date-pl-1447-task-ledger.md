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
bear on this write set are #1233 (head `3413b79a`, B2+B3 docs, carries the ValidationIssue-move ruling and the FR-240 fix plan and slice), #1055 (head
`07d9d230`, the ValidationIssue-move ruling), #1051 (head `c7621ca2`, PL 9776's plan). the ValidationIssue-move ruling's code move has not landed:
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

### Task 2 — the window, in the graph (`7b4ba43f`)

`runtime.py`: `_as_at_window` added after `_reference_rows`; the `lookup` branch of `_decision_table_node` gains an `as_at`
input and a per-rule window; the module docstring paragraph rewritten (`from datetime import date` joins the imports).
Run: `pytest packages/pricing-core/tests/test_rating_lookup_as_at.py -k "prices or misses"` → `7 passed` (red→green: the five
`prices` reds, the batch test and the miss test; both controls stay green). The DP-1 refusal tests stay red until Task 3.
**Expected red from this task, Task 3 Step 4's:** `test_rating_runtime.py::test_lookup_step_wire_translation_matches_by_key`
(`KeyError: 'area_code'`) — its fixture names `as_at: "postcode"`, a non-date value; Task 3 Step 4 fixes the fixture.
`ruff format` of `runtime.py` also rewrites four unrelated pre-existing hunks in `_model_call_handler`; those were not committed.

*Task 2 note:* the `runtime.py` diff is five `-U0` hunks (docstring, import, `_as_at_window`, two in the `lookup` branch), which git's default context merges into four; the four `_model_call_handler` hunks `ruff format` offered were not committed.

### Task 3 — DP-1 at compile and run time, the registry, the fixtures (`eada5511`)

**Shadowing re-read first (the lead's condition).** `score.py::_check_no_shadowed_produced_names` (SL-1430, #1227) refuses an
undeclared quote input whose name is a value a step *produces* (`(produced - declared) & inputs`). `effective_date` is stamped by
`score_one`, not produced by a step, so an input named `effective_date` is not caught by it; no Task 3 step is redundant or
contradicted, and `test_an_input_shadowing_effective_date_is_checked` stays red-then-green on `_check_as_at_values` alone. No STOP.

Changes: `compile.py` `_check_lookup_as_at` (+ `STAMPED_DATE`, `RatingInputType` import) appended to `ALGORITHM_CHECKS`;
`score.py` `_check_as_at_values`, called after `context = {…}` in `score_one` and `_score_context_sync`; `authored.py` the `as_at`
entry moved to `EXPRESSION_FIELDS`; `_INPUT_FREE` gains `_check_as_at_values`; the four fixtures name `effective_date`
(runtime test also gets row windows' `effective_date` in both `evaluate` contexts and a corrected comment; the score test's row gets
`effective_from`/`effective_to`); Step 3a's sentinel test added.

Run (6 files: lookup_as_at, runtime, score, pin_membership, authored_fields, quote_input_raise_sites): `155 passed`. Red→green:
the 11 `DID NOT RAISE` reds of Task 1 (three compile refusals, six malformed values, shadowing, plus the Task 1 miss test already
green in Task 2). `ruff check packages/pricing-core` clean; `mypy packages/pricing-core/src` clean.

**Sentinel test (Step 3a), red-after, disclosed.** I wrote it after the implementation; I then made it red by replacing the
`_check_as_at_values` calls in `score.py` with `pass` (restored byte-for-byte): it failed, but not with the plan's `DID NOT RAISE` —
the sentinel reached the engine and the miss path raised `REFERENCE_LOOKUP_MISS` naming `s_expr`, so the `'s_area'` assertion failed.
The batch half works: `_ctx_to_row` carries `inception` (the test passes both halves).

**Slip, disclosed.** Step 5's `pytest packages/pricing-core` (the whole package) was started by me, ran past the tool's 120 s timeout
into the background, and I stopped it by pid (cwd-checked); it produced no result. The brief bars a full suite outside the gate;
none was run to completion, and nothing was held (both slots were free).

### Task 4 — the three HTTP paths and DP-3's pins (`8ba19a78`)

`backend/tests/test_score_as_at.py` (new): `test_score_prices_on_the_row_in_force`, `test_score_compare_prices_both_sides_on_the_row_in_force`,
`test_score_batch_job_prices_on_the_row_in_force`, `test_effective_date_parsing_is_pinned` (four cases), `test_overlapping_windows_are_refused_at_table_save_with_their_code`.
Fixtures mirror the neighbours (`test_api_reference.py::_table`, `test_rating_version_compile.py::_insert_version`, `test_scoring_handlers.py`'s
compile and dataset-version helpers); a published reference table holds Task 1's `ROWS`. Worktree database `gipricing_sl-1448_72c627d5`
(`createdb -T gipricing`, `alembic upgrade head`; `alembic current` = `alembic heads` = `f3a7c1d9e2b4`); both gate slots free at each run.

**Order disclosure.** The plan wants this module red *at the base*, before Tasks 2–3; I wrote it after them. I then restored the four
pricing-core files (`runtime.py`, `compile.py`, `score.py`, `authored.py`) to `0ee8f414` with `git checkout 0ee8f414 -- …`, ran the module, and
restored them from `HEAD` (`git status` showed only the new test file after). At the base: **5 failed, 3 passed** — the five fail with
`AssertionError: the superseded row's rate returned` (`/score`, `/score/compare`, the batch Job, and the `plain-date` and
`offset-midnight-local-date` parsing cases); the three passes are the pins that are green at the base (the two `422 VALIDATION_FAILED` cases and the
`409 REFERENCE_INTERVAL_OVERLAP`). DP-3's condition holds: no pin failed at the base. The plan listed only the midnight case among the
parsing reds; `plain-date` is red too, for the same cause (it lands in the NEW window). At `HEAD`: **8 passed**.

### Task 5 — the spec text

`docs/specs/03-rating-engine.md`, the FR-221 row (`:107`) only: RL-1446's T1 appended verbatim to the end of the second cell (the ruling's
text with its amendments, not the plan's §"Spec text T1"); the marker date is the applying commit's, 2026-10-08. The find string
`never "now" (`01` FR-71). The date source is explicit in the step. |` occurred once before the edit.

### Task 6 — the gate

Slot `/tmp/slots/gate-1`, granted by the lead for head `e021d6f174e2d2ed2c34f3329a76e074d30b4cb7` (tree = that commit's, a clean
working tree), both halves under one held `flock`, `timeout 3600 nice`. The stages ran as the `dev-commands` gate body, with
`uv run --directory`, `env -C` and `pnpm --dir` in place of a `cd`. **GATE START 2026-10-08 11:05:08 BST, GATE END 11:44:20 BST.**
`alembic current` = `alembic heads` = `f3a7c1d9e2b4` before and after. Logs: `/home/puzhenhao1989/.cache/tmp.jswRSYQcGf` (local).

| stage | rc |
|---|---|
| `ruff check .` | 0 |
| `mypy` | 0 |
| `lint-imports` | 0 |
| `audit-docs.py` | **1** — the single expected row `check 31: gap in the full allocation between 1468 and 9481` (this ledger's working id) |
| `req-coverage.py` | 0 |
| `generate-contracts.py --check` | 0 |
| `pytest -q` | **1** — `13 failed, 5098 passed, 4 skipped` in 2251.98 s |
| frontend `install --frozen-lockfile`, `generate:api`, `lint`, `type-check`, `test`, `build` | 0, 0, 0, 0, 0, 0 |

The 13 pytest failures are all docs-audit tests that run `audit-docs.py` / `doc-id.py check` against the real tree and read the same
working-id gap: 11 carry the string `gap in the full allocation between 1468 and 9481` in their failure text; `test_doc_id_check_exits_0_on_the_real_tree`
reports `docs/INDEX.md has a gap between 1468 and 9481` from `doc-id.py`; `test_an_index_skipping_a_reserved_block_breaks_contiguity`
reads the same `docs/INDEX.md` for gaps (its text was not matched by the string search; read from the INDEX gap itself, not
verified by its own failure body). They clear when the mint closes the allocation. No other failure. The worktree database
`gipricing_sl-1448_72c627d5` was dropped after the gate.

## PRs

#1236, a draft. The branch `sl-1448-fd-1420-lookup-reads-row-in-force-as-at` is pushed; the PR is not merged by the executor.
