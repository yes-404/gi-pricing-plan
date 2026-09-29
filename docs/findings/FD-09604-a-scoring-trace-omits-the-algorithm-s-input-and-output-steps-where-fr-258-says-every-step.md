---
id: FD-9604
family: finding
title: A scoring trace omits the algorithm's input and output steps, where 03 FR-258 says every step
status: active
created: 2026-09-29
owner: auditor
tree: 1c8762d9ed235f80e0f2fff80c44003694828e97
corrected_by: []
relates: [WK-672, WK-671]
---

# FD-9604 — A scoring trace omits the algorithm's input and output steps, where 03 FR-258 says every step

## Finding

**Severity: low.** WK-672 Slice 4's executor reported it in `LG-1230` (*"The engine traces
expression steps only, and `consumed` is the whole environment"*) as a fact about the fixture,
not as a finding. The auditor read it against the requirement at the WK-672 Work close. FR-258
is WK-671's requirement; Slice 4 consumed it unchanged. This record does not decide whether the
code or the requirement is wrong: that is `CLAUDE.md` §0's question.

`03` FR-258 requires every step in the trace. The trace builder drops every engine entry whose
id is not an algorithm step id, and an algorithm's `input` and `output` steps reach the engine
as the synthetic wire nodes, so they are never in the trace.

## Evidence

At `origin/main` `1c8762d9ed235f80e0f2fff80c44003694828e97`.

- `docs/specs/03-rating-engine.md:175`, FR-258: *"**Trace**: on request, scoring returns every
  step's id, label, consumed values, produced value, matched table row key, and elapsed time,
  plus the bundle hash and rating version reference."* `grep -n -i 'input.*output.*step.*trace\|not traced\|wire node\|synthetic' docs/specs/03-rating-engine.md`
  prints nothing: `03` states no exemption for `input` or `output` steps.
- `packages/pricing-core/src/pricing_core/rating/score.py`, `_build_trace`: `step =
  step_meta.get(entry.get("id"))`, then `if step is None:  # the synthetic input/output wire
  nodes, not an algorithm step` → `continue`.
- The observable effect, at the HTTP layer: the compare fixture's algorithm has four steps,
  `s_in` (`input`), `s_expr`, `s_adj` and `s_out` (`output`)
  (`backend/tests/test_rating_version_compile.py:61-66` and
  `backend/tests/test_score_compare.py:105`). `test_identical_refs_give_an_empty_diff` asserts
  `response.json()["diff"] == {"steps": [], "unchanged": 2}`, and for two identical traces `unchanged`
  is the number of trace steps (`pricing_core/rating/trace_diff.py:47-59`; `PL-1213` acceptance
  item 3, *"identical traces give `steps == []` and `unchanged == len(steps)`"*), so the trace
  holds two of the four.
- Not verified here: whether a non-expression step type other than `input` and `output` (a rate
  table lookup, a constraint) is traced. `_build_trace` keeps any entry whose id is an algorithm
  step id, so it depends on how `compile` names each step's engine node, which this record did
  not read.

## Disposition

**Carry forward, unowned**, proposed by the auditor on 2026-09-29; the register row's
`decision:` is the lead's. The decision-maker decides whether FR-258 gains a dated
clarification that `input` and `output` steps are not traced, or whether the trace must carry
them (`CLAUDE.md` §0). Event: the decision-maker's ruling. If unowned at the next `CLAUDE.md`
§14 review, the row decays to that review.
