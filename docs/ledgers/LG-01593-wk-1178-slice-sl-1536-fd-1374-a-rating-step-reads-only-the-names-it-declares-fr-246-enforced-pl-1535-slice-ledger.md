---
id: LG-1593
family: ledger
title: WK-1178 slice SL-1536 — FD-1374, a rating step reads only the names it declares, FR-246 enforced (PL-1535), slice ledger
status: closed
created: 2026-10-10  # original date 2026-10-09, set at the draft; minted 2026-10-10
owner: executor
tree: d471a43bdc4ed123258a7398bbcf30c62605aa27
phase: P2
work: WK-1178
slice: SL-1536
plans: [PL-1535]
corrected_by: []
relates: [PL-1535, PL-1520, RL-1519, FD-1374, FD-1534, FR-246, FR-212, WK-1178]
---

# LG-1593 — WK-1178 slice SL-1536: FD-1374, FR-246 enforced

*Disclosure: drafted under working id 9441; minted as LG-1593 on 2026-10-10, in the SL-1536 mint commit (the lead's allocation in `to-lead.md`, "2026-10-10 14:39:49 BST" read-back and the dispatch brief).*

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-09 13:17:43 BST — USER: parallel …" item 2, in `to-lead.md`, a local file): code and tests are written on a branch from `origin/main` `d471a43bdc4ed123258a7398bbcf30c62605aa27`; no heavy run while S3's Task 7 holds gate-1; nothing merges before the GO and the gate.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `PL-1535` (single-row Work plan for WK-1178), slice `SL-1536`: *"WK-1178 fix slice — FD-1374: a rating step reads only the names it declares (FR-246 enforced)"*. Its tasks are `PL-1520` Task 1A, Steps 1–8, as ruled by `RL-1519` (DP-F35-1 (ii) (a)/(a)/(a), (iii-a) (b), (iii-b) (b)), with the plan's deviations D1 (tokenizer, no Spike S1), D2 (no Task 1 Step 6) and D3. Requirement ids: FR-246, FR-212 (fixtures gain producers); register FD-1374.

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1535`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1536`'s roadmap row at its head.

Write set: `PL-1535` §Tasks / `PL-1520` Task 1A "Files" only. **FD-1534's remedy (a)** (the extractor in `packages/pricing-core/tests/test_rating_committed_strings.py` skips an empty literal) is the lead's 2026-10-09 brief item for this slice, but that path is not in that write set; it waits on a ruling (build log).

### Task list

PL-1520 Task 1A, by step (acceptance checks are PL-1535 Acceptance Standard items 1 to 6):
- [x] Step 1: `test_rating_declared_reads.py` (6 tests), commit `3af2475f`. **Red proof run 2026-10-10, see Red-by-cause runs** (Step 2: expected `ModuleNotFoundError: No module named 'pricing_core.rating.references'` at collection, then per Step 3 the two refusal tests and the two example tests red by their causes).
- [x] Step 3: `pricing_core/rating/references.py` (deviation D4 below).
- [x] Step 4: `_check_declared_reads` appended to `compile.py`, last entry of `ALGORITHM_CHECKS`; commit `aeeb39ad` (Steps 3 and 4 together).
- [x] Step 5: four fixtures fixed, three `input` steps added in `test_rating_score.py`, one in the model-schema fixture (whose `input_contract` gains `min_premium_minor`; its step-count assert 9 to 10); commit `cb945b84` and a style commit.
- [ ] Step 6, 7: **owed** (need pytest; gate slot for Step 7).
- [x] Step 8 (authoring half): RL-1519 T1 to T5 applied: `03` (FR-246 row, the 4.1 example fence, its Invariants note, the owned-code row) and `errors.py`; commit `497bd69d`. T2's sha256 (with final newline) printed `6a35964d410f9b6c`, matching RL-1519. Audit-docs, FD-1374's predicate, the release note in the squash body, `git diff` of `03` beside the RL text: **owed**.
- [x] FD-1534, both limbs, authored in `test_rating_committed_strings.py`, commit below (write-set addition ruled, build log). **Red proofs run 2026-10-10 (Red-by-cause runs): both limbs red by cause, controls green; the file is not green at the head, see the finding there.** FD-1534 is closed (status, register row) only if both limbs are discharged by that run.

### Red-by-cause runs (2026-10-10, 14:39 BST)

Single test file per run, `flock -w 300 /tmp/slots/small-test -c "timeout 150 nice -n 19 uv run --directory <dir> pytest -q <file> -p no:cacheprovider"`, gate-1 and gate-2 free at the start, no DB test. `<dir>` is a detached scratch worktree of this repository (removed after), never this worktree's index. Test paths are under `packages/pricing-core/tests/`.

| Test file, state | Tree | rc | Printed line |
|---|---|---|---|
| `test_rating_declared_reads.py`, tests only | `3af2475f` | 2 | `ModuleNotFoundError: No module named 'pricing_core.rating.references'` at collection; `1 error` |
| same, `references.py` taken from `aeeb39ad`, `compile.py` and `03` as at `3af2475f` | `3af2475f` + that one file | 1 | `4 failed, 2 passed`. `test_a_constraint_reading_an_undeclared_name_is_refused` and `test_an_expression_reading_an_undeclared_name_is_refused`: `assert [] == [('s_clamp', ...'RATING_STEP_UNDECLARED_READ')]` (no check yet). `test_the_03_example_validates_in_full_and_compiles`: `declared output 'premium_ladder' has no output step (FR-214)`. `test_the_03_example_declares_every_read`: `steps read undeclared names: {'s_area': [...` (old `03` example) |
| same file, branch head | `649e7e54` | 0 | `6 passed` |
| `test_rating_committed_strings.py`, limb (a) reverted in a scratch copy (`_text` returns `match.group(first) or match.group(first + 1)`, the `is not None` guards forced true) | `649e7e54` + that edit | 1 | `test_an_empty_literal_is_skipped_and_a_real_one_beside_it_is_still_caught`: `assert [('expr', None)] == []` |
| same file, limb `_KEY` reverted (`_END = ""`) | `649e7e54` + that edit | 1 | `test_a_literal_that_is_not_the_whole_value_is_not_an_authored_expression`: `assert [('expr', ' * ')] == []`; the first limb's test and the controls pass |
| same file, branch head | `649e7e54` | **1** | `1 failed, 5 passed`. Both FD-1534 tests green. **Red:** `test_every_committed_string_is_accepted_or_a_declared_negative`, one unexplained string: `test_rating_declared_reads.py:33 [expr] "a * b + round(a, 'half_even', 0)": ['EXPRESSION_INVALID_VOCABULARY']` |

**Finding for the lead (not fixed here).** The last row is a defect at the head, not a red proof: the `referenced_names` fixture at `test_rating_declared_reads.py:33` authors an `expr` string that the FR-244 scan reads and the vocabulary check refuses. The same string is reported in the limb (a) and limb `_KEY` rows (the line is in both trees); whether it is red at `20f3df51`'s extractor was not run. Fix options: change the fixture string to a vocabulary-valid expression, or add it to `_NEGATIVES`. Not applied: the lead picks.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run while S3's Task 7 holds gate-1) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-09, authoring phase.** Worktree `.claude/worktrees/sl-1536`, branch `sl-1536-fd1374-dp-f35-1`, from `origin/main` `d471a43bdc4ed123258a7398bbcf30c62605aa27`.

- Commit 1: `PL-1535`'s `status:` line `draft` to `active`, and this file.
- **Deviation D4 (this slice, not PL-1535's D1 to D3).** `references.py` takes its evaluated field names from `authored.EXPRESSION_FIELDS` (FD-1317's one registry, which landed after PL-1520 was written) rather than repeating a hard-coded field list; it skips a `None` clamp bound. `referenced_names`' contract and the plan's tests are unchanged. D1 (the tokenizer, no Spike S1) applies as PL-1535 says.
- **RATING_ERROR_CODES placement.** RL-1519 T5 inserts the code immediately after `"LADDER_CLAMP_UNPLACEABLE",`; applied so, byte for byte. The lead's brief said tail; the ruling wins and the insertion site does not touch the tail S4 appends to (`ATTRIBUTION_RECONCILIATION_FAILED`).
- **Light smoke, no pytest (not the red/green proof).** With `PYTHONPATH` on the tests dir, the six test functions called directly all passed, `validate_algorithm` over `test_rating_score._algorithm_payload`, `test_rating_compile.valid_algorithm`, `test_rating_compile_bundle.valid_algorithm_payload` and the model-schema fixture gave 0 FR-246 issues.
- **STOP, FD-1534's remedy (a).** It edits `packages/pricing-core/tests/test_rating_committed_strings.py`, which is not in `PL-1535` / Task 1A's write set. Reported to the lead 2026-10-09; RULED the same day in `to-lead.md`, entry headed "2026-10-09 13:48:15 BST — RULING: PL-1535 write set + scope. (1) YES, test_rating_committed_strings.py joins. (2) WIDEN: fix the _KEY limb too, in this slice": the file joins the write set for FD-1534 only, and the scope is widened to both limbs.
- **FD-1534 authored (2026-10-09).** Limb (a): `_text` picks the double-quoted group by `is not None` and skips an empty literal (a blank placeholder), at both sites. Limb `_KEY`: the literal must be the whole value (a lookahead for a delimiter, comment or line end), so `expr = " * ".join(...)`, whose literal is a method receiver, is no longer read as the expression ` * `. A first design that dropped bare `name = "..."` was rejected after a light diff of old against new extraction over the tracked tree showed it would lose two real expressions (`test_rating_pin_membership.py:234`, `:240`); the shipped design lost none (the only two lines it no longer reads are this file's own comment and test text). Two new tests are the positive controls per limb (empty literal skipped, a real literal beside it caught; a non-whole-value literal skipped, whole-value forms caught). Light smoke (functions called directly, no pytest) passed. S3's rename `expr` to `prod` (`5647779f`, `scripts/measure-attribution-cost.py`) is now unnecessary and is not reverted (S3's write set).
- **RATING_ERROR_CODES placement.** RL-1519 T5, at `backend/src/app/errors.py` right after `"LADDER_CLAMP_UNPLACEABLE",`; S4 appends `ATTRIBUTION_RECONCILIATION_FAILED` at the tail, so there is no textual overlap. At the merge turn, after S4 and A-1 merge, this slice still reports `RATING_ERROR_CODES` with both sides kept (Q3).
- **Alembic.** This slice adds no migration.

**2026-10-10, GO and gate phase** (GO effective at A-3's merge read-back, main `fe0b0627590307259ec6d56be7f73115cf245092`; the lead's dispatch entry "2026-10-10 14:37:13 BST — DISPATCH GO: the FD-1374 slice …").

- **Merge `fe0b0627`** (`1c721492`): one content conflict, `docs/specs/03-rating-engine.md` §4.1, resolved per DP-FD1374-M1 (a): RL-1519's ruled text verbatim, SL-1340's "a mount is a node" amendment carried as its own dated paragraph after it; no text of the executor's own. `docs/INDEX.md` regenerated by script.
- **Committed-strings fixture** (`735374a2`): the lead ruled it in the write set. `test_rating_declared_reads.py` used `round(a, 'half_even', 0)`, which FR-244's vocabulary does not have, so `test_every_committed_string_is_accepted_or_a_declared_negative` failed with `EXPRESSION_INVALID_VOCABULARY`. It is now `a * b + abs(a)` (names `a`, `b` unchanged); not added to `_NEGATIVES`. Red (1 failed, 5 passed) to green.
- **DP-M2, FD-1589 row 8** (`40604029`): `errors.py` `_field_error_message`: `value_error`, `assertion_error` and `union_tag_invalid` keep the code alone, other pydantic types keep their fixed text. Red: a validator interpolating the value gave "Value error, bad SENTINEL-x"; green: "The value is not valid (VALUE_ERROR)." The test is `test_error_sinks.py::test_a_request_validation_422_carries_no_submitted_value`; its DB run is inside the gate.
- **RL 9586 re-point** (`4b53b62a`): `test_rating_algorithm.py:367`, comment only, to RL-1571.
- **Mounted-fragment guard** (`10c3e07a`): an inlined fragment passes the declared-reads check; it passed first time, so it is a guard, not a red-first; the control flags a stray read at `m_ncd__s_ladder`.
- **03 §4.1 example vs A-3** (`017d998a`): the slice's own compile test failed `BUNDLE_COMPILE_FAILED` naming `s_rp`: the example (03:295-299) produces two names, A-3's rule (RL-1459 DP-A3-1 (c)) allows one for a Peril Structure `model_call`. Ruling "2026-10-10 14:43:15 BST — RULING: 03 §4.1 worked example vs A-3's compile …" (`to-lead.md`): the code is right; 03 §4.1 stays byte-for-byte as RL-1519 ruled it (Acceptance 4); the test pins the RULE (two names refused, the one-name form compiles); the example is known-wrong text pending a correcting RL, filed as FD 9953 (working id), which rides the next docs batch. The old failure is the red; green is 9 passed in `test_rating_declared_reads.py`.
- **FR-239.** Approved versions are never recompiled, so no stored bundle changes with this slice; a bundle compiled before the check keeps loading and scoring (RL-1519 (iii-b)).

**2026-10-10, the red gate and its repairs** (first full gate at `0e7c4d5c`: 74 failed, 7 errors; rulings in `to-lead.md`: "15:36:02 BST" write set, "15:37:31 BST" DP-M2, "15:40:36 BST" FR-246 vs FR-221, "15:42:57 BST" two purpose-tests and the hash).

- **DP-M2 WITHDRAWN (15:37:31 BST), reverted** (`8842b7c5`): `errors.py` keeps only the RL-1519 registry line; `test_error_sinks.py` has no diff against main. The row-8 fix and its tests are parked on `draft/fd1589-row8-tests` @ `cfe8e15f03171ed54bdee6e27bb783a6cc83bfbc` (no PR). The CodedError survey (no request-model validator raises `CodedError`; `model-schema` has 253 `raise ValueError`, 0 `CodedError`) belongs to that branch's slice.
- **FR-246 vs FR-221, ruling 15:40:36 BST** (`2838df55`, spec and code in one commit): `references.py` exempts only a lookup's `as_at == STAMPED_DATE` (the constant moved to `authored.py`; `compile.py` imports it); 03's FR-246 row carries the ruled dated line verbatim; §4.1 untouched. Red first: a lookup `as_at: effective_date` with no input step was flagged (`s_area`); guards green before and after: any other undeclared `as_at` is still refused, an expression reading `effective_date` as a value still declares it. **The roughly 47 `effective_date` reds needed no fixture change.**
- **Fixture declarations (declaration-only, no expected value changed).** Names derived with the slice's `references.py`, via an out-of-repo harness (below), never hand-picked:
  - `test_rating_algorithm.py` (B): step indices +1 after `valid_algorithm` gained `s_in_min_premium` (`69d27c2d`).
  - `test_rating_wire_order.py::_NL_CLAMP`: `s_clamp` consumes `floor`.
  - `test_rating_ladder_exact.py::_clamp_variant` (4 callers): `s_clamp` consumes `sanity_floor_minor` (max variant), `min_premium_minor` and `sanity_floor_minor` (both variant), `min_premium_minor` (always_ok, never_ok).
  - `test_rating_compile.py::_with`: an edited step's consumes is re-derived from `referenced_names` (first consumed name kept first for FR-240).
  - `test_rating_lookup_as_at.py::_algo`: for an `as_at` naming a declared date input (`inception`), an input step and a consumes entry (8 tests); the stamped `effective_date` needed none.
  - `test_rating_score.py::_algorithm_payload` (the slice's earlier edit): `s_in_min_premium`, `s_in_sanity_cap`, `s_in_sanity_floor` and the consumes of `s_clamp`, `s_decl_cap`, `s_decl_floor`.
  - `examples/fremtpl2` seed algorithms v1 and v2: no undeclared read by the derivation; unchanged. `examples/fremtpl2` tests: 7 passed, 1 skipped.
- **The two purpose-tests (ruling 15:42:57 BST).** `test_rating_attribution.py::test_attribute_undeclared_column_never_reaches_the_engine` deliberately reads an undeclared column (`secret_loading`); it now proves the RUNTIME guard with the declared-reads check switched off by a test-only `monkeypatch` of `compile.ALGORITHM_CHECKS` (no production path gains a way around compile). Two layers: compile refuses an undeclared read (the FR-246 tests in `test_rating_declared_reads.py`); the runtime still guards (this test). `test_rating_number.py::test_a_missing_lookup_row_takes_the_default` read the undeclared `missing_value`; it now reads the lookup's own declared `expense_factor` with a table that has no row for the quote's channel (same expected 1370). The undeclared-read case it used to exercise is covered by `test_rating_declared_reads.py::test_a_constraint_reading_an_undeclared_name_is_refused` and `::test_an_expression_reading_an_undeclared_name_is_refused`.
- **Pinned hash re-recorded** (separate commit `60b6d08f`): `test_rating_wire_order.py` and `test_rating_shadowed_inputs.py`, before `sha256:86abdb81dc16d2075956aa11e05f2e9c87fe191d4a3397574e5a82520039073d`, after `sha256:6458c7c80627d20602a8d82821a80e3fb7500c75c1d3bf9bc1033ba74f7a918e`. Cause: the fixture algorithm gained its FR-246 declarations (the safe direction: the hash moves, the price does not). Every money/scoring golden is unchanged (`test_rating_ladder_exact.py`'s diff against `origin/main` is consumes edits only; no expected value changed anywhere).
- **FR-239.** Approved versions are never recompiled, so FR-246 refuses only NEW compiles; a bundle compiled before the check keeps loading and scoring (RL-1519 (iii-b)); no stored bundle changes with this slice.
- **Derivation harness (out of repo, source recorded here):** it wraps the slice's own FR-246 reader in `compile.ALGORITHM_CHECKS` and logs every undeclared read against the running test id.

```python
"""Out-of-repo derivation harness: wraps the slice's own FR-246 reader and logs every undeclared
read (all steps, not just the first) against the running test's node id."""
import json, os, re
import pytest
from pricing_core.rating import compile as c
_orig = c._check_declared_reads
_cur = {"id": "?"}
def _wrapped(algo):
    issues = _orig(algo)
    with open(os.environ["DERIVE_OUT"], "a") as f:
        for i in issues:
            f.write(json.dumps({"test": _cur["id"], "step": i.step_id, "msg": i.message}) + "\n")
    return issues
c.ALGORITHM_CHECKS = tuple(_wrapped if f is _orig else f for f in c.ALGORITHM_CHECKS)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item): _cur["id"] = item.nodeid
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item): _cur["id"] = item.nodeid
```

## PRs

(none yet)
