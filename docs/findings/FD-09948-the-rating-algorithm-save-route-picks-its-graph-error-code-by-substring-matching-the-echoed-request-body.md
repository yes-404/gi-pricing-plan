---
id: FD-9948
family: finding
title: The rating algorithm save route picks its graph error code by substring-matching the echoed request body
status: active
created: 2026-09-30
owner: auditor
tree: 11c76b6c83647c512796fedb9c0143927dcd78cb
corrected_by: []
relates: [WK-1250, FR-212, FD-1297]
---

# FD-9948 — The rating algorithm save route picks its graph error code by substring-matching the echoed request body

## Finding

**Severity: low.** Proposed by the auditor; the disposition is the lead's. Filed 2026-09-30
under working id 9948, and minted at its merge turn.

`_parse_algorithm` (`backend/src/app/platform/rating_algorithms.py:25-52` at `origin/main`
`11c76b6c83647c512796fedb9c0143927dcd78cb`) decides which code a refused `RatingAlgorithm`
carries by lower-casing `str(exc)` of pydantic's `ValidationError`, and testing it for two
substrings (`:35-47`):

- `"cycle"` gives `RATING_GRAPH_CYCLIC`, tested first;
- `"undefined value"` gives `RATING_GRAPH_UNRESOLVED_REF`;
- anything else gives `VALIDATION_FAILED`.

`str(exc)` is not only the validator's message. It carries pydantic's `input_value=` echo of
the value that failed, and, for an unknown field, the client's own value. So any refusal whose
echo contains either phrase is reported with the wrong code, and a real `RATING_GRAPH_UNRESOLVED_REF`
is reported as `RATING_GRAPH_CYCLIC` if the body also echoes "cycle".

This is a wrong **client-visible code** on a request that is refused anyway (422). It stores
nothing and prices nothing. Nothing in this repository branches on the code today: the frontend
does not exist for this route and no other backend module reads it. `03` §5.1 owns both codes
(`03:771-772`), and `WF-699` (`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:111`) names the same refusals, so a client written against them would be misled.

## Evidence

Reproduced at `origin/main` `11c76b6c83647c512796fedb9c0143927dcd78cb`, in a worktree at that
commit, with the repository's own virtualenv and the worktree's sources first on the path:

```
PYTHONPATH=backend/src:packages/model-schema/src:packages/pricing-core/src \
  .venv/bin/python repro.py
```

where `repro.py` calls `_parse_algorithm` on the valid fixture of
`backend/tests/test_rating_algorithms.py` (`valid_algorithm()`), and on copies of it:

```python
run("1 control, valid body", v)
run("2 extra field colour=red", {**v, "colour": "red"})
run("3 extra field cycle_note=x", {**v, "cycle_note": "x"})
run("4 extra field colour='cycle'", {**v, "colour": "cycle"})
run("5 extra field colour='undefined value'", {**v, "colour": "undefined value"})
u = copy.deepcopy(v); u["steps"][6]["consumes"] = ["risk_premium_minor", "nope"]
run("6 real unresolved ref (control)", u)
run("7 real unresolved ref + extra colour='cycle'", {**u, "colour": "cycle"})
```

Output:

```
1 control, valid body: accepted
2 extra field colour=red: code='VALIDATION_FAILED'
3 extra field cycle_note=x: code='RATING_GRAPH_CYCLIC'
4 extra field colour='cycle': code='RATING_GRAPH_CYCLIC'
5 extra field colour='undefined value': code='RATING_GRAPH_UNRESOLVED_REF'
6 real unresolved ref (control): code='RATING_GRAPH_UNRESOLVED_REF'
7 real unresolved ref + extra colour='cycle': code='RATING_GRAPH_CYCLIC'
```

Case 2 is the correct answer for 3, 4 and 5 (an unknown field is `VALIDATION_FAILED`), and case 6
is the correct answer for 7. Cases 3, 4, 5 and 7 are wrong. The script calls `_parse_algorithm`
directly, so the route's own path, which passes the request body to the same function unchanged
(`create_algorithm`, `:83`), is not separately exercised here.

Other reads, at the same tree:

- `git grep -n '"cycle" in\|"undefined value" in' -- backend/src packages` prints only
  `rating_algorithms.py:36` and `:43`. It is the one place this matching happens.
- The two source messages are `RatingAlgorithm._graph_invariants`' own text: "the rating DAG
  contains a cycle (FR-212)" and "step … consumes undefined value … (FR-212)"
  (`packages/model-schema/src/model_schema/rating.py:419` and `:439`). The matching therefore
  couples an API code to the wording of a validator message.
- **The existing tests do not prove the mapping's second and third branches.**
  `backend/tests/test_rating_algorithms.py` has one refusal test that reaches the mapper,
  `test_a_cyclic_algorithm_is_refused_at_save_time` (`:86`, `RATING_GRAPH_CYCLIC`). Nothing
  there, and no other backend test, asserts `RATING_GRAPH_UNRESOLVED_REF` or the
  `VALIDATION_FAILED` fallback of this function (`git grep -n RATING_GRAPH_UNRESOLVED_REF --
  backend/tests` prints nothing).

**Why it matters beyond this route.** WK-1250 Slice 1's superseding leaf plan (unminted at
this tree) extracts this mapping *unchanged* into a public function that a second artifact, the
sub-graph, will also use, and words a new validator message to contain "undefined value" so that
the substring matches. The defect is then shared by two paths, and the fix should land once.

## Disposition

**carry forward with an owner: WK-1250 Slice 1**, fixed by its merge. Proposed by the auditor
as WK-1178's; **the maintainer's decision, 2026-09-30 15:10:21 BST** (by delegation, the lead's
local channel file `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 15:10:21 BST — FD
9948 (the substring-matched error codes): LOW; the fix folded into WK-1250 S1; the N1
characterisation guard") set the severity **low** and moved the owner to **WK-1250 Slice 1**:
"**Owner: WK-1250 S1**, not WK-1178. S1 already extracts `_parse_algorithm`'s mapper
(platform/rating_algorithms.py:23-52), so the typed-signal fix lands **in the same slice, same
writer**, as its **last task** after the unchanged-extraction step." This supersedes the
proposed owner (WK-1178) of the first filing.

**Fix direction.** Replace the substring match with a typed signal, matched on `exc.errors()`
and not on `str(exc)`: either a pydantic custom error type per invariant (for example
`PydanticCustomError("graph_cyclic", …)`), or a `ValueError` subclass per invariant. The mapper
then reads each error's `type`, which no client value can reach.

**The guard, per the same entry.** The characterisation tests written first for the mapper
"**must not pin the bug.**" The `cycle_note` case, and any other substring false positive found,
is a **`strict=True` xfail citing FD 9948**, which the typed-signal task flips to a pass as the
proof of the fix. Cases 3, 4, 5 and 7 above are the false positives known at this tree. The
tests for the two unproven branches (`RATING_GRAPH_UNRESOLVED_REF` and the `VALIDATION_FAILED`
fallback) are green on the current code, and rows 2 and 6 stay green.

**Event.** WK-1250 Slice 1 merges with the typed signal as its last task and the strict xfails
flipped. Ownership shape: event.

**Severity reasoning.** Low, not medium: no data is stored or priced wrongly, the request is
refused either way (it fails closed); the wrong code needs an unusual body (an unknown field, or
an echoed value, containing those words); and no consumer branches on the code yet. It would
rise to medium if the designer (WK-675) or an API client maps these codes to user-facing text.
