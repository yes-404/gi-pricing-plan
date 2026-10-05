---
id: LG-9496
family: ledger
title: WK-1178 slice SL-1427 — FD-1425 guard (c), a quote input never overrides a produced value (FR-213, PL-1426)
status: active
created: 2026-10-05
owner: executor
tree: 4f9c19c2f397b6b9be592b4ea92595ea225d5397
phase: P2
work: WK-1178
slice: SL-1427
plans: [PL-1426]
corrected_by: []
relates: [RL-1423, RL-1263, FD-1425, FR-213, FR-255, WK-1178]
---

# WK-1178 slice SL-1427 — guard (c), a quote input never overrides a produced value

Executed from `PL-1426` by `executor-sl1427` (sonnet). Branch
`sl-1427-guard-c-quote-input-never-overrides-produced-value`. Stamps are BST (`TZ=Europe/London date`).

The dispatch record is `gi-pricing-plan.local/handover/DISPATCH-WK-1178-SL1427-2026-10-05.md` (FINAL; the GO's
conditions (0)-(5) bind). It is a local file and is not in the repository.

**The 17:25:07 deploy/approve HOLD does NOT lift at this merge.** It lifts only by the maintainer's (by delegation)
dated entry after the merge read-back (GO condition (4)); the roadmap and the register cite that entry. This
overrides PL-1426 Task 3 Step 5, as the dispatch record's "Override of PL-1426 :651" section records.

## Tasks

### Task 0 — preconditions and the RL-1423 vs PL-1426 comparison

**Base.** Worktree from `origin/main` `4f9c19c2f397b6b9be592b4ea92595ea225d5397` (#1217, merged 19:31:40 BST).
`uv sync --all-packages` ran. Test database `gipricing_sl-1427_5faaea8b`, created from the `gipricing` template with
`createdb -T` and migrated with `alembic upgrade head`. PL-1426 and SL-1427 are `active` on that tree.

**Difference reported to the lead (19:3x BST):** RL-1423's T2 text (`RL-1423` line 240) carries the working id
"FD 9572"; RL-1423 line 243 says the mint replaces it with the minted `FD-` id (FD-1425). PL-1426 Task 2 Step 5 and
GO condition (3) say byte for byte. The lead rules (A: substitute `FD-1425`; B: apply literally). No T2 edit is made
before that ruling. Other, harmless differences: PL-1426 says T2 "citing RL-1423" while the T2 text itself cites
nothing (RL-1423 is cited in the commit message and here); RL-1423's `work:` is WK-673, the plan's WK-1178.

### Task 1 — the reds (at base commit `4f9c19c2`, before any code change)

**The per-name table** (auditor-premise `r3.py` sha256 `0ee537bf93e6c07fb548fec520321dd32a460a50283e6dd799e595558e897fac`,
read-only at `4d3be141`; from the lead's compilation `handover/trace-fd9572-premise-fanin-2026-10-05.md`, a local
file). Score fixture in its native topological order, `min_premium` 5000, one extra key per run; reference payable 5250.

| extra key | step kind | shadowed? | payable |
|---|---|---|---|
| expense_factor=9 | table | N | 5250 |
| risk_premium_minor=12345 | model_call | N | 5250 |
| office_premium_minor=777 | expression (re-produced by the clamp) | N | 5250 |
| instalment_loading_minor=777 | expression, the last terminal producer | **Y** | **777** |
| payable_premium_minor=777 | output-step name, not a produced key | N | 5250 |

Only `instalment_loading_minor` is shadowed in this fixture, and `test_the_3f_case_is_refused` is its red. Guard (c)
refuses every produced name, so the parametrised tests cover all four.

**The fixture hash.** `compile_bundle(_version(), _FakeResolver()).content_hash` was printed twice (a throwaway script
in a scratch directory outside the repository) and gave the same value both times:
`sha256:86abdb81dc16d2075956aa11e05f2e9c87fe191d4a3397574e5a82520039073d`. It is pinned in
`test_the_bundle_hash_is_unchanged`.

**Core module** — `OMP_NUM_THREADS=1 nice -n 19 uv run pytest
packages/pricing-core/tests/test_rating_shadowed_inputs.py -q`, tail verbatim:

```text
FAILED test_rating_shadowed_inputs.py::test_the_3f_case_is_refused
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused[expense_factor]
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused[risk_premium_minor]
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused[office_premium_minor]
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused[instalment_loading_minor]
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused_in_a_batch[expense_factor]
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused_in_a_batch[risk_premium_minor]
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused_in_a_batch[office_premium_minor]
FAILED ...::test_an_undeclared_key_naming_a_produced_value_is_refused_in_a_batch[instalment_loading_minor]
9 failed, 2 passed in 2.01s
```

The six `score_one` failures are `Failed: DID NOT RAISE ValueError`; the four batch failures are
`AssertionError: assert 'quoted' == 'error'`. The two passes are the pins
(`test_the_ordered_no_key_quote_is_unchanged`, `test_the_bundle_hash_is_unchanged`). Each cause is the one PL-1426
Task 1 Step 4 names.

**The four backend path reds**, each run alone (`OMP_NUM_THREADS=1 uv run pytest <file> -k <test> -q`):

| Test | At the base commit | Cause shown |
|---|---|---|
| `backend/tests/test_score.py::test_a_quote_input_naming_a_produced_value_is_refused_on_score` | FAIL | `assert 200 == 422` (the body is a `quoted` result, payable 2000) |
| `backend/tests/test_score.py::test_a_pending_trace_whose_context_names_a_produced_value_is_not_reproduced_as_a_price` | FAIL | `assert <JobStatus.SUCCEEDED: 'succeeded'> is <JobStatus.FAILED: 'failed'>` |
| `backend/tests/test_score_compare.py::test_a_context_input_naming_a_produced_value_is_a_422_on_compare` | FAIL | `assert 200 == 422` (both versions produce `payable` in `s_expr`, so the planted name is valid for both; the compare trace shows `consumed.payable` 1 overriding) |
| `backend/tests/test_scoring_handlers.py::test_a_dataset_column_named_like_a_produced_value_is_refused_per_row` | FAIL | `assert {} == {'INPUT_CONTRACT_VIOLATION': 4}` |

The trace test's invariant (no completed trace carries a price built on the planted key) is asserted by
`status is FAILED` and `after.status == "pending"`. The plan's optional read of the failed Job's recorded error for
`INPUT_CONTRACT_VIOLATION` is not yet in the test; it is added at Task 2, when the green run shows the shipped
`execute_job` shape.

### Task 2 — guard (c) and T2, in one commit

**The ruling on T2's working id.** The maintainer (by delegation), entry "2026-10-05 19:33:23 BST" in
`channel/to-lead.md` (a local channel file, cited by its header), ruled OPTION A: apply T2 with "FD-1425" in place of
"FD 9572", everything else byte for byte; under GO condition (3), as `RL-1423` lines 243-244 define it ("the mint
replaces it with the minted `FD-` id"), that is byte for byte. Option B (the literal working id) is refused. The entry's text, verbatim
(`to-lead.md`, line 18694 at this date):

> Read at origin/main: RL-1423 :243-244 directs that "FD 9572" in both texts is the finding's working id, which the mint replaces with the minted FD- id. So applying T2 with FD-1425 in place of "FD 9572" IS byte for byte under GO condition (3), as the RL itself defines it. OPTION A, ruled. LG 9496 records the substitution, citing RL-1423 :243-244 and this entry, with the grep -cF counts before and after: the substituted T2 counts 1 in 03 after the apply, and "FD 9572" counts 0 in 03. Option B is refused (it plants a dead id).

**T2 applied.** The replacement is `RL-1423` line 240 with that one substitution. `grep -cF` on
`docs/specs/03-rating-engine.md`, before and after:

| String | Before | After |
|---|---|---|
| the find string (`Scoring rejects a Quote Context violating the contract with a field-level error. \|`) | 1 | 0 |
| the substituted T2 line, as in `RL-1423` line 240 with `FD-1425` for the working id | 0 | 1 |
| `FD 9572` | 0 | 0 |

The substituted line was also taken from `RL-1423` line 240 by `sed` (two-space indent dropped, working id replaced) and
searched in the spec with `grep -cFf`: 1.

**The DP-2 exception's red** (`test_a_declared_input_re_produced_in_place_is_not_a_shadow`), seen failing before the
guard existed: `ImportError: cannot import name '_check_no_shadowed_produced_names' from 'pricing_core.rating.score'`
(the function's name was held back for the run; restored at once).

**Each call is load-bearing.** Run on `test_rating_shadowed_inputs.py` with one call removed at a time:

- `score_one`'s call removed: `5 failed, 7 passed`; the five failures are the `score_one` cases (the 3f case and the
  four per-name cases), each `Failed: DID NOT RAISE ValueError`; the batch cases pass.
- `_score_context_sync`'s call removed: `4 failed, 8 passed`; the four failures are the batch cases, each
  `assert 'quoted' == 'error'`; the `score_one` cases pass.
- Both calls restored; `git diff HEAD` over `score.py` shows the function and both calls (24 added lines).

(An earlier removal run also dropped both calls by a restore slip and printed `9 failed, 3 passed`; it is not one of
the two runs above, and the file was restored and diffed before they were repeated.)

**Green at the head of Task 2** (each run alone, `OMP_NUM_THREADS=1 nice -n 19`):

| Run | Result |
|---|---|
| `test_rating_shadowed_inputs.py` + `test_quote_input_raise_sites.py` | `31 passed` |
| `test_rating_score.py` (no assert edited) | `40 passed` |
| `backend/tests/test_score.py::test_a_quote_input_naming_a_produced_value_is_refused_on_score` | `1 passed` |
| `backend/tests/test_score.py::test_a_pending_trace_whose_context_names_a_produced_value_is_not_reproduced_as_a_price` | `1 passed` |
| `backend/tests/test_score_compare.py::test_a_context_input_naming_a_produced_value_is_a_422_on_compare` | `1 passed` |
| `backend/tests/test_scoring_handlers.py::test_a_dataset_column_named_like_a_produced_value_is_refused_per_row` | `1 passed` |

The trace test also asserts the failed Job's recorded error carries `INPUT_CONTRACT_VIOLATION` (added at this task).

### Task 3 — the gate

**Granted** by the lead for head `c8bc3a7c510430df801f542255d5fe2d5fcb8c56` (PR #1219) on gate-1, after S7's release. One
slot hold covered both halves (the dev-commands wrapper verbatim plus `LOKY_MAX_CPU_COUNT=4`, `timeout` inside the body,
foreground). The run was in a clean detached checkout of that SHA, `.claude/worktrees/sl-1427-gate`; `uv sync
--all-packages` ran there. The test database `gipricing_sl-1427-gate_48539ffa` was made from the template and migrated:
`alembic current` printed `e5b7d9f1a3c6 (head)` and `alembic heads` printed `e5b7d9f1a3c6 (head)`, exactly one head.
**The gated tree is `ae41f80acef299dfec069c8becf66c978493e716`.**

**The slip.** The lead's "GATE START" message was sent before the slot was taken: my first launch attempt was refused by
the shell guard, so the message preceded the real start by about a minute. The gate's own first stamp is the start
(2026-10-05 18:45:50 UTC, 19:45:50 BST). Nothing else ran in that gap.

**Half 1** (Python and docs, the seven stages in parallel). Start 18:45:50 UTC: load average 1.88, free 19330 MB. End
19:11:59 UTC: load average 1.55, free 19028 MB.

| stage | result | exit |
|---|---|---|
| ruff | pass | 0 |
| mypy | pass | 0 |
| import_linter | pass | 0 |
| audit_docs | FAIL | 1 |
| req_coverage | pass | 0 |
| contracts (`--check`) | pass | 0 |
| pytest | FAIL | 1 |

`audit_docs` failed on check 31 only: `check 31: gap in the full allocation between 1427 and 9496` (`FAILED (1)`), the
expected working-id gap before the mint (PL-1426 Acceptance 10). pytest: `13 failed, 4942 passed, 4 skipped in 1548.15s`.
All 13 failures are driven by that gap, each an assert that `audit-docs.py` exits 0 or that the allocation is
contiguous (the logs are in `/tmp/tmp.2Q0p5brI0p`, a local scratch directory not in the repository). The 13 names:

1. `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`
2. `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`
3. `tests/test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree` (`[noncontiguous] docs/INDEX.md has a gap`)
4. `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`
5. `tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec`
6. `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`
7. `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity` (`[(1427, 9496)]`)
8. `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`
9. `tests/test_register_lint.py::test_check_29_note_carries_the_residue_line`
10. `tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count`
11. `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`
12. `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`
13. `tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci`

The lead compared the colour-stripped set with the allowed check-31-driven set (identical by `diff`) and checked the rc
files. No new test and no `test_rating_score` test is among the 13.

**Half 2** (frontend). Start 19:11:59 UTC: load average 1.55, free 19051 MB. End 19:12:58 UTC: load average 4.40, free
18922 MB.

| frontend stage | exit |
|---|---|
| `pnpm --dir frontend install --frozen-lockfile` | 0 |
| `generate:api` | 0 |
| `lint` | 0 |
| `type-check` | 0 |
| `test` (97 files, 615 tests, no type errors) | 0 |
| `build` | 0 |

`uv run python scripts/req-coverage.py` exited 0 (the `req_coverage` stage). The four backend path reds and the core
module passed inside the pytest stage (none is among the 13). The gate's overall rc was 1, the expected pre-mint shape.
The 17:25:07 HOLD is not touched by this record: it lifts only as the first section of this ledger says.

## PRs

#1219, draft, opened 2026-10-05 from branch `sl-1427-guard-c-quote-input-never-overrides-produced-value`. It is not
merged by the executor.
