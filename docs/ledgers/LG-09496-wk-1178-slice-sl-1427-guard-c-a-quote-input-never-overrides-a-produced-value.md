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
