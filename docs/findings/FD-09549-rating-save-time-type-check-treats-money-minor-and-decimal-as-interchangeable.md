---
id: FD-9549
family: finding
title: The rating save-time type check treats money_minor and decimal as interchangeable for expression producers
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
corrected_by: []
relates: [WK-1178, FR-226, FR-227]
---

# FD-9549 — `_compatible` passes every pair of `_NUMERIC` types (`compile.py:124-129`)

**Filed** by auditor-numeric on the lead's brief of 2026-10-05, working id 9549 (reserved in the lead's `eta.md`),
from the maintainer's (by delegation) ruling in `to-lead.md`, entry "RULINGS at 17:30:02 BST", item 3. The claim
came from planner-a12fold (read-only). **Every fact below was re-read at `origin/main` 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6**;
`tree:` is that commit. Paths are `packages/pricing-core/src/pricing_core/rating/…` unless written in full.

## Finding

**Severity: MEDIUM, LATENT; owner WK-1178** (the maintainer's ruling: MEDIUM and LATENT, or HIGH if anything is live;
nothing is live, see Liveness). `compile.py:57` defines `_NUMERIC = frozenset({"int", "decimal", "money_minor",
"relativity", "percentage", "count"})`. `_compatible(producer: str, declared: str) -> bool` (`:124`) returns `True` for
equal types, else `producer in _NUMERIC and declared in _NUMERIC` (`:129`). Its comment (`:127-128`) reads *"Numeric values
are interchangeable at save time; the bundle compilation resolves the exact unit."* No code resolves a unit: `_NUMERIC`
and `_compatible` are the only numeric-family logic in the tree (grep below), and the bundle compilation has no second
type comparison. So FR-227's save-time check ("type compatibility is checked at save time. A monetary result must be
`decimal` or `money_minor`") refuses a mismatch only when a non-numeric type is involved (`string`, `bool`, `date`).
A `money_minor` producer into a `decimal`, `relativity`, `percentage`, `count` or `int` output passes, and the reverse.
The gap is wider than the two types named in the claim: all six types are mutually interchangeable (30 ordered pairs).

**Boundary.** This finding is the **expression producer** (and an input-step producer) case: the types
`producer_types` (`:95`) knows. The **`model_call` producer** case is not this finding's. It is A-2 item 15 on #1178
at `1f4c8f8c970ecfdfa32cadf9bc991e7acce2a217` (`_check_result_types` / `output_type_issues`), which the maintainer
(by delegation) accepted on 2026-10-05 as "model_call producers only, `_compatible` untouched". So **`_compatible`
stays as A-2 leaves it, and this finding owns the change to it.**

## Evidence

**1. Sweep.** Predicate: `git grep -n -E 'output_type_issues|producer_types\(|_check_result_types|_compatible|_NUMERIC|\.result_type|result_type=' 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6 -- packages backend/src`, `tests/` excluded.

| Site (at the sha) | What it does | money_minor ⇄ decimal mix passes? |
|---|---|---|
| `compile.py:57` `_NUMERIC` | the set | defines the interchange |
| `compile.py:124-129` `_compatible` | the only numeric pair comparison | **yes**, every pair in `_NUMERIC` |
| `compile.py:132-155` `output_type_issues` | the one caller of `_compatible` (`:143`) | **yes**, via `_compatible` |
| `compile.py:158-170` `_check_result_types` | algorithm outputs; in `ALGORITHM_CHECKS` (`:360`), so `validate_algorithm` runs it | **yes** |
| `compile.py:173-199` `fragment_output_type_issues` | Sub-graph output ports at create; called from `backend/src/app/platform/sub_graphs.py:42` | **yes** |
| `compile.py:95-116` `producer_types` | types only `input` and `expression` steps; a step that consumes a value is **never compared against it** | n/a: an expression's inputs are not checked against its `result_type` |
| `score.py:751` `_build_outputs` | `declared.type == "money_minor"` takes the engine's exact value and rounds once to an integer; any other type is read straight from `result` | does not reject; a `decimal`-fed `money_minor` is rounded to an integer silently |
| `score.py:947-975` `_coerce_output_value` | by the **declared** type only: `money_minor` must be `int`, `decimal` becomes `str(Decimal(repr(value)))` | does not reject; a pence integer served under a `decimal` declaration is labelled as a decimal |
| `golden.py:67,84`, `properties.py:146` | tolerance in minor units; orderability of an input field | no type pair compared |

No other place in `packages` or `backend/src` compares or coerces a numeric type pair. Runtime and trace code take the
declared type as given and never cross-check it against the producer.

**2. Reproduction (proves the gap).** Tree: worktree of `origin/main` at the sha above; `OMP_NUM_THREADS=1 nice`,
`PYTHONPATH=<worktree>/packages/pricing-core/src:<worktree>/packages/model-schema/src` over the root `.venv` python (the
printed `compile.__file__` was the worktree's). The algorithm is the committed demo fixture's shape
(`examples/fremtpl2/model.py:334-343`): an `int` input, one `expression` step, one output; only `result_type` and the
declared output type vary. `validate_algorithm(algo)`, codes filtered to `RATING_TYPE_MISMATCH`:

```
expression result_type -> declared output type : result
money_minor -> money_minor : PASSES   (control)
money_minor -> decimal     : PASSES
decimal     -> money_minor : PASSES
money_minor -> relativity  : PASSES
money_minor -> percentage  : PASSES
money_minor -> count       : PASSES
relativity  -> money_minor : PASSES
money_minor -> string      : ['RATING_TYPE_MISMATCH']   (positive control: the check does fire)
```

The last row shows the check works for a non-numeric pair, so the silence on the rows above it is the gap and not a
broken probe. The probe was written in a `mktemp -d` outside the repository.

## Liveness

**No mix is reachable today.** Checked at the same sha:

- Every committed JSON that names `money_minor` is a contract schema under `docs/contracts/` (six files, from
  `git grep -l money_minor 4d3be141… -- '*.json'`); none is a rating artifact.
- Every rating algorithm that is not a test builds `money_minor` into `money_minor`: the demo seed fixture
  (`examples/fremtpl2/model.py:334-343`, `fremtpl2-demo@1`: `int` input, `result_type` `money_minor`, output `money_minor`),
  `scripts/bench-rating.py:248-267`, `scripts/bench-score-batch.py:78-86` and `scripts/bench-compiled-for.py:79-87` (same
  shape; `bench-rating` uses `decimal` inputs into `money_minor` expressions, which is not an output comparison).
- `backend/src/app/demo/` builds no algorithm of its own.

So the gap is open to any author who submits a mismatched algorithm, and nothing committed does.

## Exposure

An author can declare a `decimal` output and feed it a pence-valued `money_minor` expression, or the reverse, and the
algorithm saves and compiles. At score time the declared type decides the serving form (`score.py:751`, `:966-975`),
not the producer's unit, so a value in pence can be served as a decimal string with no unit change, or a decimal
expression is rounded to an integer pence figure. FR-227 and CLAUDE.md §7 (money is integer minor units or Decimal) are
the rules this check exists to hold, and the spec text does not say numeric types are interchangeable.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** Carry forward with an owner, **WK-1178**, at MEDIUM, LATENT. The
design is open and is not this record's to pick: either (a) make `_compatible` exact for `money_minor` (a `money_minor`
producer feeds only `money_minor`; the others stay interchangeable), or (b) amend FR-227 to say numeric types are
interchangeable and delete the deferral comment. (a) matches FR-227's second sentence and CLAUDE.md §7. The change must
leave A-2 item 15's `model_call` work untouched (the boundary above) and must flip or add a test in
`packages/pricing-core/tests/test_rating_compile.py`. Event that next confirms or discharges it: a merged change to
`_compatible`, or a dated ruling choosing (b).

### Disposition — ruled 2026-10-05 17:36:28 BST (pre-mint)

**Source:** the maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-05 17:36:28 BST —
FD 9549 (#1197 @9c8a52c6): MEDIUM LATENT confirmed; disposition (a) narrowed, with money_minor CLOSED both ways; batch 2
agreed". Quoted verbatim, item 2:

> 2. Disposition: (a), narrowed. money_minor is CLOSED in BOTH directions at save time:
>    - OUT of money_minor: only into money_minor. Refuse money_minor into decimal, relativity, percentage, count or int, for EVERY producer (A-2 item 15 stays the model_call instance; the fix slice generalises it without editing A-2's tests).
>    - INTO money_minor: from money_minor, or decimal AT AN OUTPUT STEP ONLY (FR-226's rounding point under option (B)). Refuse relativity, percentage and count into money_minor.
>    - int→money_minor and the non-money pairs among themselves (relativity/percentage/count/int/decimal) go to ONE OQ, owner WK-1178, decided before the fix slice's plan mints.
>    The fix slice's FIRST task is red-first: one red per refused direction, plus a sweep showing no committed algorithm or fixture newly fails. If one does, STOP and report; do not loosen the rule.

**Severity** stays MEDIUM, LATENT (ruling item 1); the wider reach (six numeric types, 30 pairs, the sub-graph create
path via `fragment_output_type_issues`, serve-time coercion by the declared type) is accepted as this finding's text.
The ruling chooses (a) over (b) above and widens (a): `money_minor` is exact in both directions, not only as a producer.
Item 3 of the ruling: the fix is reserved under WK-1178 after the emergency slice (SL 9561).

**Where each limb goes (working ids; the mint date replaces them, check 31):**

- **OQ 9556**, owner WK-1178, decided **before** PL 9521 mints: `int`→`money_minor`, and the non-money numeric pairs
  among `relativity`, `percentage`, `count`, `int`, `decimal`.
- **SL 9522 / PL 9521**, under WK-1178: the fix. Red-first, one red per refused direction, plus a sweep that no committed
  algorithm or fixture newly fails; if one does, STOP and report rather than loosen the rule.

Event that next confirms or discharges the row: a merged SL 9522 making `_compatible` refuse the directions above.
