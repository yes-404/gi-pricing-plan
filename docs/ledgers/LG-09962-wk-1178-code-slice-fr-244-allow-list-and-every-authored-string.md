---
id: LG-9962
family: ledger
title: WK-1178 code slice (SL-1315) — FR-244's enforced allow-list and every authored rating string checked (FR-244, FR-274, FR-276, FR-255)
status: active
created: 2026-09-30
owner: executor
tree: 9953a37a99f84747d35107ce30a2b84326904972
phase: P2
work: WK-1178
plans: [PL-1314]
corrected_by: []
relates: [RL-1312, RL-1313, RL-1322, FD-1317, OQ-1316, RL-1263]
---

# LG-9962 — WK-1178 code slice (SL-1315): FR-244's allow-list and every authored string

Executed from `PL-1314` (SL-1315) under `RL-1312`, `RL-1313` and the correction `RL-1322`
(working id 9965 until batch 6; it is on `main` at `32f3fa92`). Branch `sl-1315-fr244-allowlist`,
from `origin/main` `fa9a73c2d8b5cfebf4c699961015e6ff8dde1fb1` (`git ls-remote`), lane B.
Drafted under working id 9962 (the lead allocates every working id); minted at the merge turn.

## Tasks

### Task 0 — preconditions

The dispatch record, quoted verbatim (`~/gi-pricing-plan.local/handover/DISPATCH-WK-1178-967-CODE-SLICE-DRAFT-2026-09-30.md`,
outside the repository, as it stood when the slice was pushed, with its dated deltas). Its lane B
grant: **2026-09-30 15:45:54 BST**, by the lead, at main `fa9a73c2`.

````text
# Dispatch record — WK-1178 #967 code slice (SL-1315), from PL-1314 — FINAL

**Status: DISPATCHED 2026-09-30 15:45:54 BST** (lane B GO by the lead) at main `fa9a73c2d8b5cfebf4c699961015e6ff8dde1fb1`, #994's squash (RL-1312, OQ-1316, RL-1313, PL-1314/SL-1315 activated, FD-1317), on the maintainer's MERGE-ACK #994. Was: DRAFT. Per the maintainer's "2026-09-30 14:48:52 BST" item (3), this record carries the plan's activation facts, and the executor's ledger quotes it verbatim in Task 0. Every condition cites a maintainer entry in `~/gi-pricing-plan.local/channel/to-lead.md` (outside the repository) by its header.

- **Plan:** PL-1314, activated by the `status:` flip in batch 4. Its content audit is CLEAN: #969's mint delta `811428c1..023dcbd4` (auditor-924d), with its base audited earlier.
- **Rulings:** RL-1312 (FR-244 decided: an enforced allow-list; `??` is its coalescing operator) and RL-1313 (DP-G1, G3, G4 and G5; its post-audit delta `bbeee641..a5c84d53` re-audited CLEAN by auditor-924d).
- **Findings delivered:** FD-1317 (was #968, working id 9885, HIGH: condition and clamp_bounds strings are never validated).
- **Lane:** B, under RL-1263. Order on `compile.py` ("10:53:10 BST"): the fix slice (#988, MERGED 2118679b), then **this slice**, then WK-1250 S1 (PL 9845, CLEAN, not yet minted).

## Activation facts (the plan's "Activation needs", each met)

1. The fix slice merged: #988, 2118679b, 14:58:07 BST.
2. FR-244's amended text: carried **by this slice**, under **RL-1313 DP-G1 (b)**. WK-690 Slice 1's FR-244 sentence was HELD (#981's dated amendment at `03` FR-244, "HELD for #967"), so the fallback applies. Quoted from the maintainer's entry "2026-09-30 15:22:17 BST — #992 read-back verified; batch 4 (#994) pre-verified, with one addition: activate PL-1314 by a status flip": "**G1 fallback, to state in the dispatch record:** RL-1313 DP-G1 (a) waits for WK-690 S1's FR-244 text, but that sentence was deliberately **held** (LG-1304; #981's dated amendment). So **(b) applies**: the code slice writes FR-244's allow-list text itself **from RL-1312's text**".
3. DP-G1, G3, G4 and G5 are ruled in RL-1313; DP-G2 is withdrawn.
4. #968 is minted as **FD-1317** (batch 4). Task 0 re-points this plan's "#968" citations to FD-1317 in the **ledger** (PL-1314:487); the plan is frozen.
5. The lane B slot grant is given at finalisation (time below), with this record's write-set check.

**Lane B grant: 2026-09-30 15:45:54 BST**, by the lead, at main fa9a73c2.

## Conditions

1. **Write set:** PL-1314 §"Write set, for the RL-1263 check", verbatim, **plus** `docs/specs/03-rating-engine.md` §3.5, FR-244's row (`:146`), under DP-G1 (b). Keep #981's dated "HELD for #967" amendment intact, and write the held sentence in RL-1312's amended wording, spec first, in the same commit as the allow-list enforcement.
2. **The RL-1263 write-set check against lane A (WK-674 S2a, in flight, local at ba5630bc as of 15:3x BST):**
   - **Shared path: `backend/src/app/errors.py`** (two different module-level collections). S2a adds `APPROVAL_OUTSIDE_DECISION_PATH` to `GOVERNANCE_ERROR_CODES`, plus a DBAPIError handler. This slice adds its DP-G4 code to `RATING_ERROR_CODES` (a frozenset at `:286-365`; "tuple" was wrong, corrected on executor-1178fix's prep read). Different existing definitions, so they may run together (RL-1263:100). The second to merge merges `main` and re-runs its gate.
   - **`backend/tests/test_rating_version_compile.py`:** S2a changes only an import and one test body (:590). This slice doesn't list the file. No overlap.
   - Everything else in S2a's diff (models, approvals, migrations, fixtures, `06`) is disjoint.
3. **Must not change:** `compile_bundle`, `check_step_refs_pinned` or `runtime.py` (the fix slice's). `_GUARD_MARKERS` loses only `"?:"` and `"coalesce("`, per PL-1314.
4. **Red first:** every acceptance item as PL-1314 states it. The FD-1317 reproduction rows are quoted as pre-fix evidence from FD-1317's table, never committed. **FD-1317's structural acceptance** (the maintainer's MERGE-ACK #994 names it): every authored expression field (`condition`, `clamp_bounds`, `key_expr` as well as `expr`) goes through the same enumerator and every registered check, per FD-1317's *Disposition* and the maintainer's "10:55:40 BST" class fix, with the matrix and closure tests of PL-1314 acceptance 3a–3c red first.
5. **Gate slots** ("2026-09-30 13:24:18 BST — DATED CORRECTION…"): every suite-level run uses the dev-commands slot wrapper (`.claude/skills/dev-commands/SKILL.md:122-171`) **verbatim**, plus `LOKY_MAX_CPU_COUNT=4`, run foreground with a `timeout` per executor.md S-11 (the maintainer's decision (a), "13:4x"). The harness auto-backgrounds at 600s; wait on the output and never relaunch. Record the queue wait and the wall time separately, `uptime` at start and end, and the other holder. **A full gate needs the lead's explicit S-13 grant for that head.**
6. **RL-1263 contention, pair 2 of 3** (the maintainer's MERGE-ACK #994: "likely vs S2a"; S2a's full gate was granted at 5c7ae3b2) (the maintainer's "2026-09-30 14:13:03 BST" correction): this slice's first full gate overlapping S2a's is a candidate pair. Record both runs' pytest times, compare against the solo baselines (1469.6s at bf790e22), and report it.
7. **Gate:** the full two-half gate before pushing (CLAUDE.md §11). Docs checks run on a clean detached checkout of the pushed commit.
8. **Ledger:** an `LG-` record under working id **9962** (checked free), minted at the merge turn. Task 0 quotes THIS RECORD verbatim, including the grant time, and re-points #968 to FD-1317.
9. **Plans are frozen by family** ("14:44:36 BST"): nothing in `docs/plans/` is edited.
10. **Executor:** executor-1178fix (it delivered the fix slice, so it knows `compile.py`), in a new worktree from `main` after batch 4 merges. Its first act is `echo $CLAUDE_EFFORT`.
11. **Prep read (executor-1178fix, at e3600789):** premises a–o hold, with lines shifted (compile.py +3: `_GUARD_MARKERS` :44, `_check_determinism` :145, `_check_division_guards` :169, `_check_scale_cap` :199, `_check_vocabulary` :236, `validate_algorithm` :264; runtime.py :293/:304). Task 0 re-reads FD-1317's text and exposure list in full at the dispatch tree (acceptance 10).

## Delta 1 — 2026-09-30 16:31:23 BST (lead)

1. **number(x) stays (RL-1322, correcting RL-1312; minting in batch 6 #999, working id 9965, audited CLEAN at 1f87c765).** The slice's FR-244 text and its allow-list enforcement follow RL-1322's final FR-244 sentence **verbatim**: `number(x)` is on the list; a numeric string (spaces and exponent accepted) converts to an exact decimal; a number passes unchanged; a boolean converts to 1/0; any other string and null fail with `RATING_EVALUATION_FAILED`. The #988 arithmetic tests are restored. The ledger cites RL-1322 once minted, and until then working id 9965.
2. **The S-13 grant at 6bcf73e5 was put on HOLD** for (1). The gate that ran there (16:00:54–16:29:27 BST; 4197 passed / 3 skipped / 1 failed; pytest 1694.62s, ~1.15× the solo baseline of 1469.58s) is **evidence only**. It is not the slice's gate, and it is an RL-1263 pair-2 *candidate*, confounded (the other holder was on gate-1 at the start, identity unconfirmed).
3. **Write-set addition:** `backend/tests/test_error_sinks.py`, one `_SINKS` entry for score.py's `_failing_node`. The full suite found a second guard (the error-sink inventory) that PL-1314 doesn't name. The ledger records it as a plan gap found by the gate. It is disjoint from S2a (the shared surface is `errors.py` only).
4. The next S-13 grant is for a head carrying (1) **and** the b7aa2eb1 sink fix, not b7aa2eb1 alone.

**Delta 1 correction — 2026-09-30 16:31:46 BST (lead):** Delta 1 item 2's framing, that the gate "ran after the grant was put on HOLD", is **wrong**, and this line supersedes it. executor-1178fix confirmed that the run at 6bcf73e5 **started under the valid S-13 grant** (15:00:54 UTC = 16:00:54 BST), and the HOLD reached it only after the run had finished. There was no breach. The run is still evidence only, not the slice's gate, because the head lacks RL-1322's `number(x)`. Its figures and pair-2 status in item 2 are unchanged.

**Delta 2 — 2026-09-30 17:12:36 BST (lead):** the standing rule (the maintainer, to-lead.md ~17:1x BST, until the WK-1178 reservation ledger lands; FD 9972): **the lead is the ONLY allocator of working ids of every family** (FD, RL, PL, OQ, LG, secondary). This slice's ledger stays 9962; any other id is asked of the lead.
````

- **Premises a–o** were re-read at `fa9a73c2`: they hold, with lines shifted (`compile.py`
  `_GUARD_MARKERS` :44, the four checks :145/:169/:199/:236, `validate_algorithm` :264; `runtime.py`
  :293 and :304, re-read in this worktree, not carried from the prep read). `RATING_ERROR_CODES`
  is a `frozenset`, not a tuple (`errors.py:286`).
- **DP resolutions by record:** DP-G1 (b) (`RL-1313`), DP-G3 (a), DP-G4 (a)+(i) with the stated
  limit, DP-G5 (a)+(i); DP-G2 withdrawn. `#968` is `FD-1317`.
- **FD-1317's exposure list** re-run verbatim at `fa9a73c2`: 4 hits, all `expr`
  (`backend/tests/test_rating_algorithms.py:112`, `packages/pricing-core/tests/test_rating_compile.py:125`
  and `:136`, `packages/pricing-core/tests/test_rating_compile_bundle.py:248`), the same as the finding.
- **The committed-strings sweep** (acceptance 10), re-run at `fa9a73c2` because RL-1312's 37 predates
  `#988`. Predicate: `_authored_strings` in
  `packages/pricing-core/tests/test_rating_committed_strings.py` (FD-1317's line regex over
  `git ls-files`, plus an `ast` walk of every tracked `.py` file for a dict entry or keyword named
  `expr`, `condition`, `key_expr` or `clamp_bounds`, plus a JSON walk; data-preparation files and
  the record directories skipped). Count at the slice's tree: **69 rows, 38 distinct strings** (RL-1312
  said 37; the difference is strings added since `48792023`). A first sweep, including `docs/plans`,
  found 84 rows and 43 distinct strings, with 4 distinct off-list strings: the deliberate negatives
  `now()` and `foo(`, a data-preparation `where(...)` (out of scope) and this author's own `#988`
  tests (`number(` and a double-quoted string). **Nothing in `examples/`, a golden quote or a
  RegressionSuite is off the list:** `examples/fremtpl2/model.py:341` is `premium_in * 2`. The sweep
  cannot see helper-built strings; the full suite is the second instrument.
- **Open PRs** read at `fa9a73c2`: none ruling on FR-244, FR-274, FR-276, FR-255 or `??`. `#993`
  (the save route's error-code mapping) and `#995` (`reconcile_ladder`) are findings only.

### Task 1 — spec first (`73a36ef0`)

`03` FR-244's row carries RL-1312's amended sentence in place of the held one (DP-G1 (b)), with
#981's dated amendment kept; `RATING_EVALUATION_FAILED` joins §5.1. After `RL-1322` the sentence
also carries `number(x)` (commit `57d62711`), written from the ruling's final text.

### Task 2 to 4 — red, then green

Red commit `a3aaf26e` (no production code yet); reds quoted:

- `test_rating_compile.py`: 9 allow-list refusals fail `assert [] == [('s_office', 'expr')]`; 9 of
  FD-1317's 10 rows fail on `[]` (the `expr` row is already in the allow-list group); the masked-division
  forms and the dead-marker test fail (`'?:' not in (...)`).
- `test_rating_score.py`: D2 and E4 `DID NOT RAISE`; A2 and C1 raise `RATE_TABLE_MISS`; the
  no-table engine failure raises a bare `RuntimeError: boom`. The stated-limit test is green by design.
- `test_rating_authored_fields.py`, `test_rating_vocabulary.py`: `ModuleNotFoundError` /
  `ImportError` (the modules did not exist).
- Backend `test_a_masked_division_in_a_condition_is_refused_at_save_time`: `201 Created`.
- Pre-fix prices (scratch run, never committed): D2 at floor 0 is quoted, payable 1507,
  `decline_reasons []` (FD-1317); D2 at floor 1 is declined `SANITY_CAP`; E4 at floor 0 is quoted at
  1507 with the cap lost; E3 at floor 1 and cap 1000 gives 1050.
- After `RL-1322`, `number(x)` tests were red with `` `number` is not on FR-244's allow-list `` (25
  failed, 70 passed in three files), then green.

Green commits: `dcacbac3` (enumerator, allow-list tokenizer, registries), `6bcf73e5` (the residual
code), `b7aa2eb1` (the sink fix), `57d62711` (`number(x)`), `618b69ad` (a direct literal comparison).
The matrix is **5 checks x 5 fields = 25 cells**; the two closure tests and their broken-input proofs
(a planted `formula: str`, an unregistered `_check_x` reading `.expr`) are green.

- **Acceptance 9 (raise sites):** `test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case`
  passes with `_INPUT_FREE` unchanged: `_reraise_engine_failure` keeps one `_raise_named` call.
- **A plan gap the full suite found.** `PL-1314` names only the `_INPUT_FREE` guard. The gate at
  `6bcf73e5` failed `backend/tests/test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for`:
  `_failing_node` reads `str(exc)`. Fixed in `b7aa2eb1`: one `_SINKS` entry, a sentinel test
  (`test_an_engine_error_text_never_reaches_the_raised_message`), and the raised message names only a
  matched step's own `step_id`. The dispatch record's Delta 1 accepts the write-set addition.
- **Restated tests.** `#988`'s lookup tests used `number(...)` and double-quoted strings, which the allow-list
  (single-quoted strings only, RL-1312) refused. They were first restated as tier comparisons, then
  restored to real arithmetic (`number(expense_factor ?? '1.0')`) when `RL-1322` added `number(x)`. Prices are unchanged:
  1507, 2740, 130000, 180000.
- **Hazard, ruled behaviour.** `number(true)` is `1` (RL-1322: "converts a boolean to `1` or `0`"). It is noted as a
  possible follow-up for `OQ-1321` (typed lookup outputs), not as a defect.
- **The `on_miss="error"` residual.** A lookup miss fails first with its own code, `REFERENCE_LOOKUP_MISS`,
  fail-closed, before `number()` runs. That is consistent with `RL-1322`. The `RL-1313` DP-G4 stated limit (a failing step
  that directly consumes a miss output reports the miss code) is pinned by
  `test_the_stated_residual_still_reports_the_miss_code`.

## Gate evidence

The gates used the dev-commands slot wrapper verbatim with `LOKY_MAX_CPU_COUNT=4`, foreground with
`timeout 3600`. Times are UTC. Solo reference: pytest 1469.58s at `bf790e22` (the fix slice's ledger).

| Head | Start-end (UTC) | Wall | pytest | Result | Load at start / end |
|---|---|---|---|---|---|
| `6bcf73e5` | 15:00:54-15:29:27 | 1713s | 1694.62s | 1 failed, 4197 passed (the sink guard); evidence only | 4.67/4.51/4.70 - 3.33/4.50/5.92 |
| `57d62711` | 15:34:07-16:01:27 | 1640s | 1623.42s | 12 failed, 4203 passed; evidence only | 2.03/3.12/4.96 - 8.29/5.04/4.62 |
| `a6a37847` (first) | 16:03:19-16:32:05 | 1726s | 1706.92s | 17 failed, 65 errors, 4285 passed; evidence only | 3.78/4.65/4.54 - 10.89/9.68/9.86 |
| `a6a37847` | 16:34:51-16:58:36 | 1425s | 1408.03s | **7 of 7 stages pass, 4367 passed, 3 skipped** | 8.64/9.50/9.79 - 2.19/2.63/4.68 |

- **`57d62711`: the 12 failures** are all `audit-docs`-based tests that failed on check 31, the gap
  between 1317 and 1322 (the `RL-1322` citation was not on `main` yet). No changed code is involved:
```text
tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged
tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks
tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green
tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec
tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue
tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity
tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate
tests/test_register_lint.py::test_check_29_note_carries_the_residue_line
tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count
tests/test_register_owed.py::test_check_29_wiring_is_undisturbed
tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit
tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci
```
- **First `a6a37847` run:** the 17 failures and 65 errors are all in S2a's approval-guard tests
  (`test_approval_guard_trigger.py`, `_allowance.py`, `_decision.py`, `test_api_approvals.py`), with
  `function approval_guard() does not exist`: this worktree's test database predated S2a's migration `a9f3c6d2`. It was
  repaired with `alembic upgrade head`; the four files then passed singly (215 passed, run outside the wrapper, 93s).
  The gate was then re-run on the same head, at the lead's instruction, and is green.
- **Frontend half** at `a6a37847`: `install --frozen-lockfile` and `generate:api` rc 0, `lint` rc 0, `type-check` rc 0, `test` 609 passed (609),
  `build` rc 0.
- **RL-1263 contention: these runs are NOT counted as pairs** (the maintainer's ruling, `to-lead.md`, about 18:0x to 18:1x BST).
  `free -h` was not recorded at the start or the end of any run (the dispatch conditions omitted it), and the other slot holders
  were not identified as gates. Only `6bcf73e5` with S2a's `5c7ae3b2` was a genuinely concurrent gate pair, and it lacks `free -h` too. The counted pairs stand at
  **0 of 3**. For the record only, pytest times against the solo 1469.58s were 1694.62s, 1623.42s, 1706.92s and, for the green run, 1408.03s.
- **Deviations.**
  - The `57d62711` gate used `git checkout --detach` in this worktree. One directory suite (the four approval-guard files,
    215 passed) ran outside the wrapper after the DB repair.
  - **The `alembic current` pre-check** the lead requested before the re-run was not run. The passing approval-guard tests in the green gate at
    `a6a37847` stand in for it: they fail with `approval_guard() does not exist` without migration `a9f3c6d2`.
  - **LOW: `__all__`.** `compile.py`'s `__all__` gains `ALGORITHM_CHECKS` and `STRING_CHECKS`. PL-1314's `compile.py` row does not list
    `__all__` (it was the fix slice's, #988, merged), so there is no conflict with another slice.
  - **Clocks.** Every time in this ledger is UTC unless it says BST.

## Write-set account

PL-1314's write-set table, plus the lead's dispatch deltas, is this slice's scope. Three test files sit outside the table and are tests
only, disjoint from lane A (S2a: models, approvals, migrations, fixtures, `06`):

- `packages/pricing-core/tests/test_rating_pin_membership.py`: the #988 lookup tests, restated and then restored to real arithmetic
  (`number(expense_factor ?? '1.0')`) when RL-1322 added `number(x)`. Prices are unchanged.
- `packages/pricing-core/tests/test_rating_committed_strings.py`: acceptance 10's sweep of the committed rating strings.
- `packages/pricing-core/tests/test_rating_number.py`: RL-1322's clause tests for `number(x)`.

The one other addition is `backend/tests/test_error_sinks.py` (a single `_SINKS` entry, Delta 1). `runtime.py` is untouched.

## PRs

A draft PR `SL-1315: …` is opened from `sl-1315-fr244-allowlist`. The push SHA (from `git ls-remote`) goes to the lead.
The lead merges; MERGE-ACK is the maintainer's, in the lead's channel file, never on the PR. The ledger mints at the
merge turn.
