---
id: RL-1580
family: ruling
title: RL-1459 corrected — a model_call is carried unrounded only when it declares result_type; absent means the legacy round(prediction), one rule for every model_call node
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: decision-maker
tree: 3519a919e30aa6993d40b22df212dd57bbd4a685
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1459
relates: [RL-1459, PL-1464, PL-1465, FR-222, FR-226, FR-227, FR-239, FR-244]
---

# RL-1580 — RL-1459 corrected: a `model_call` is unrounded only when it declares `result_type`

*Disclosure: filed under working id 9458; minted as RL-1580 on 2026-10-10, in the D5 batch mint PR (the correcting record `RL-1459`'s `corrected_by:` names the minted id).*

## How this was ruled

- **Filed as a draft, its working id reserved by the lead (team-lead) on 2026-10-10.** In the
  same commit, `RL-1459`'s header gains `corrected_by: [RL-1580]`, the append check 34
  allows (`docs/process/document-ids.md` §1, the `corrected_by:` / `corrects:` lines of the
  front-matter block). Not one byte of `RL-1459`'s body changes. At the mint, the working id
  in both headers and in this record is replaced by the minted id.
- **The decisions are not this record's.** They are the maintainer's (by delegation), in
  three entries of `~/gi-pricing-plan.local/channel/to-lead.md`, quoted below by header:
  - "2026-10-10 00:40:31 BST — RULING: A-2 item 15. NEITHER (i) nor (ii). The new rounding
    is OPT-IN, so existing bundles hash AND price exactly as before" (`to-lead.md:20697`);
  - "2026-10-10 00:44:31 BST — A-2 readings: (1) CONFIRMED, my 00:40:31 4(b) number
    corrected (legacy = 1436); (2) NOT accepted: the GLM model_call writes result_type
    explicitly, one rule for all model_call nodes" (`to-lead.md:20721`);
  - "2026-10-10 03:13:06 BST — RULINGS on A-3: OP-1 (a), Decimal composition in the rating
    path; OP-2 (a), explicit result_type plus a correcting RL" (`to-lead.md:20876`). Its
    OP-2 orders this record.
- **This record states the qualified rule, quotes each `RL-1459` clause it qualifies, and
  names where the code carries it.** It decides nothing beyond the three entries.
- **One form is the house's, not the brief's.** The lead's brief asked for
  `corrects: [RL-1459]`. `document-ids.md` §1 defines `corrects:` as "the frozen id it
  corrects", a scalar, and every correcting record on main writes it so (for example
  `RL-1322`: `corrects: RL-1312`). This record follows the house form.

## The maintainer's entries, verbatim (the paragraphs this record carries)

From "2026-10-10 00:40:31 BST — RULING: A-2 item 15 …", the basis and items 1 to 3:

```text
Basis: 03 FR-239 at origin/main (:137). A Rating Version's Bundle is "sufficient to score", and an approved or later version "is never recompiled". Its stored bundle scores it forever. With (A) plus (i), an approved version's bundle bytes and hash stay unchanged while its price moves 1 minor unit (1435 → 1436), because the runtime's round(prediction) changed underneath it. Same hash, different price: that breaks reproducibility (CLAUDE.md §1), the worst combination. Not accepted.
RULING (X):
1. result_type's DEFAULT = the LEGACY behaviour (round(prediction), as today). to_jdm omits result_type when it equals that default (your (A) mechanism). Every existing bundle is byte-identical, its hash unchanged, and its money unchanged. The 3 money tests and the pinned-hash test stay as they are: no expected value changes, and no files outside the write set.
2. The unrounded path is OPT-IN: result_type "decimal" is written explicitly (so it enters the hash), and the runtime carries the unrounded value to FR-244's boundary, with one rounding there. A-2's GLM model_call uses it explicitly. A GBM keeps legacy unless an algorithm opts in.
3. SPEC (§0), in A-2's commit: a dated line in 03 at the model_call / FR-244 text: "a model_call without result_type rounds the prediction as before; result_type 'decimal' carries it unrounded to FR-244's boundary, rounded once there". The default value is named in the line.
```

From "2026-10-10 00:44:31 BST — A-2 readings …", reading (2):

```text
(2) NOT ACCEPTED as a2 picked it. My 00:40:31 item 2 was not silent: "A-2's GLM model_call uses it explicitly." One rule for every model_call node: result_type absent = legacy round(prediction). The GLM node is compiled WITH an explicit result_type ("decimal", or "money_minor" where that is the ruled type), so its unrounded behaviour is visible in its bytes and its hash. No node-kind-dependent meaning of "absent". This removes the premise-dependence (no approved bundle carries a GLM call). The grep is then not needed, though harmless.
```

The same entry's reading (1) corrects a number in 00:40:31 4(b): the legacy price is 1436
and the opt-in single-rounding price is 1435. That number is not a clause of `RL-1459`.

From "2026-10-10 03:13:06 BST — RULINGS on A-3 …", OP-2:

```text
OP-2 (a) ADOPTED. Peril model_call nodes are compiled with an explicit result_type "decimal", as the GLM node is (00:44:31: one rule; absent means legacy round). A correcting RL: RL-1459 is frozen, and its "model_call is never rounded" is now true only for nodes that carry an explicit result_type. The correcting RL (corrects: RL-1459; RL-1459 gains corrected_by: in the same batch, front matter only) states the qualified rule and cites my 00:40:31 and 00:44:31 entries. It rides the next docs batch (D5's tail or D6). A-3's GO does not wait on it: the code follows X now.
```

## Ruled

**One rule for every `model_call` node, whatever the kind of model it calls:**

1. **`result_type` absent:** the step rounds the prediction as before, the legacy
   `round(prediction)`. The compiler omits the absent field from the graph, so a Bundle
   compiled before the field existed keeps its bytes, its hash and its prices. An approved
   or later Rating Version is never recompiled (`03` FR-239), so this is what keeps its
   price reproducible.
2. **`result_type` present (`decimal` or `money_minor`):** the step carries the prediction
   unrounded to FR-244's boundary, and an `output` step rounds it once (FR-226). The field
   is written into the algorithm, so it enters the graph and the hash. `money_minor` is the
   same unrounded path with the type FR-227's checks read.
3. **A GLM `model_call` node (A-2, `PL-1464`) and each peril-structure component
   `model_call` node (A-3, `PL-1465`) are compiled with an explicit `result_type`**
   (`decimal`, or `money_minor` where that is the ruled type). Their unrounded behaviour is
   therefore in their bytes and their hash. "Absent" has no node-kind-dependent meaning: a
   GLM step without `result_type` rounds like any other.
4. **A GBM keeps the legacy rounding unless an algorithm opts in** (00:40:31 item 2).

## The `RL-1459` clauses this qualifies — read at `3519a919`

`RL-1459` is `docs/rulings/RL-01459-wk-1178-a-3-and-a-4-decision-points-one-produced-name-a-compile-refusal-for-separate-model-the-c4-note-and-a-0-05-tolerance.md`.
Each clause below is quoted verbatim, and each is now true **only for a `model_call` that
declares `result_type`**.

| `RL-1459` line | Verbatim | Read now as |
|---|---|---|
| :69 (the quoted 2026-10-05 17:12:40 entry) | "A model_call's output is ALWAYS an exact Decimal, never rounded at the model_call." | True for a step with an explicit `result_type`. A step without one rounds as before (rule 1). |
| :69 (same) | "RatingModelCallStep gains `result_type: RatingResultType` as a TYPE only (decimal \| money_minor, for compile's FR-227 type checks; money_minor is a type label, not a rounding)." | `result_type` is optional, and its absence now selects the legacy rounding (rule 1). It is no longer a type label only. Its presence still types the step for FR-227, and `money_minor` still adds no rounding. |
| :74–:75 | "The 17:02:50 rounding sentence quoted above is **corrected** by this entry: a `model_call`'s output is always an exact `Decimal`, and all rounding stays on the output step." | As above: always, for a step that declares `result_type`. |
| :155–:158 (item 7) | "A `model_call`'s output is always an exact `Decimal`, never rounded at the `model_call`. All rounding stays on the output step (FR-226, unamended). A-2 adds `RatingModelCallStep.result_type` as a type label only (`decimal` \| `money_minor`), for compile's FR-227 checks." | As the two rows above. |
| :159–:161 (item 7) | "A-3 predicts each component at full precision. It composes `frequency × severity` per peril, or `burning_cost`, applies FR-189's treatment, and sums (FR-188), all on `Decimal`. Nothing is rounded until the output step's single declared rounding." | Holds, because A-3 compiles each component `model_call` node with an explicit `result_type` (rule 3; 03:13:06 OP-2). The `Decimal` composition is confirmed separately by 03:13:06 OP-1. |

The `:65` bullet of `RL-1459` names the 17:12:40 entry as "the correction that governs items
2, 6 and 7". Of those, only item 7 carries the rounding claim; items 2 (FR-249's carry) and 6
(the C4 beat) are not qualified by this record.

**Also read, and not qualified by this record:** `RL-1459`'s spec text T1 (:223) says a
Peril Structure's `exact` step is "composed on exact decimals and never rounded at the step".
Under rule 3 that holds for the step A-3 compiles, which carries an explicit `result_type`.
A-3 applies T1 (`RL-1459` :210); this record does not change its text.

## Where the code and the spec carry it — on A-2's branch, not on main

A-2's branch is `sl-1463-a2-glm-model-call`, read at its head
`e0e12dd834318294a5e0932618ca177c71a7bf46`. None of what follows is on `main` at
`3519a919`.

- **`03` FR-222's dated line**, `docs/specs/03-rating-engine.md:109` on that branch, written
  by `41aef0a3` (the 00:40:31 opt-in) and `ea2d2d88` (the 00:44:31 one rule). It reads, in
  part: "**A `model_call` without `result_type` rounds the prediction as before (a GBM's, to
  a whole unit at the step); `result_type` `decimal` carries it unrounded to FR-244's
  boundary, rounded once there.**" and "One rule for every `model_call` (the entry headed
  "2026-10-10 00:44:31 BST"): a GLM step is compiled with an explicit `result_type`, so its
  unrounded behaviour is in its bytes and hash."
- **The compiler omits the absent default**:
  `packages/pricing-core/src/pricing_core/rating/compile.py:583–586` on that branch
  (`if step_dump.get("type") == "model_call" and step_dump.get("result_type") is None:` …
  `del step_dump["result_type"]`).
- **The runtime rounds only when the field is absent**:
  `packages/pricing-core/src/pricing_core/rating/runtime.py:649` (a GBM's prediction) and
  `:656` (a GLM's: `value = round(glm_prediction) if step.result_type is None else glm_prediction`)
  on that branch.
- **The field is optional**: `packages/model-schema/src/model_schema/rating.py:362`,
  `result_type: str | None = None`, on that branch.
- **The ledger**: `LG 9449`,
  `docs/ledgers/LG-09449-wk-1178-slice-sl-1463-fd-1458-a-glm-scores-through-model-call-pl-1464-slice-ledger.md`
  on that branch, records the 00:40:31 plan delta to `PL-1464` item 15 and the opt-in
  derivation.
- **A-3's peril nodes** follow rule 3 in A-3's code (`PL-1465`); 03:13:06 says "A-3's GO does
  not wait on it: the code follows X now". This record names no A-3 locator, because none was
  read for it.

If A-2's branch is rebased or squash-merged, these SHAs and line numbers name that branch
at `e0e12dd8`, not the merged result.

## What it obliges

- `RL-1459` gains `corrected_by: [RL-1580]` in this commit, front matter only.
- Nothing else. The spec line, the code and the tests are A-2's and A-3's, under the
  entries above; this record adds none of them.

## Acceptance — the violation that must become detectable

The violation: a `model_call` that does not declare `result_type` is carried unrounded, or one that declares it is rounded
at the step or leaves the Bundle hash unchanged. Each check below names its broken input. All are on A-2's branch
`sl-1463-a2-glm-model-call` at `e0e12dd834318294a5e0932618ca177c71a7bf46`, not on `main`. They name that branch's tests, not
the merged result.

- *Violation: the compiler writes an absent `result_type` into the graph, so a Bundle compiled before the field existed
  changes its bytes or its hash* (rule 1; `03` FR-239).
  `packages/pricing-core/tests/test_rating_glm_model_call.py::test_an_old_model_call_recompiles_byte_identically`
  asserts that `"result_type" not in first.graph.nodes["s_risk"]`, equal `content_hash` on two compiles, and an equal
  `model_dump(exclude={"compiled_at"})`.
- *Violation: an explicit `result_type` does not enter the hash* (rule 2). The same test asserts
  `explicit.graph.nodes["s_risk"]["result_type"] == "decimal"` and `explicit.content_hash != first.content_hash`.
- *Violation: a `model_call` without `result_type` is carried unrounded, or one with `result_type: "decimal"` is
  rounded at the step* (rules 1 and 2; FR-226).
  `…::test_the_same_algorithm_prices_by_single_rounding_only_when_it_opts_in` scores the one algorithm both ways. It
  asserts the legacy office premium `1436` (two roundings) and the opt-in `1435` (one rounding). It also asserts that the opt-in `unrounded_minor` lies
  in (1435.28, 1435.29). The fixture's model is a GBM booster (`test_rating_score._algorithm_payload`).
- *Violation: the opt-in path is non-deterministic, or a rung's value is not the single half-even rounding of its
  unrounded `Decimal`* (rule 2; NFR-495).
  `…::test_the_opt_in_path_is_deterministic_and_its_money_is_decimal_exact`.
- *Violation: a GLM step that declares `result_type` (`decimal` or `money_minor`) is rounded at the step* (rule 3).
  `…::test_a_model_call_equals_predict_glm_at_full_precision` asserts the step's value against `predict_glm` within
  1e-14 (relative) for both types. Its docstring marks this as a draft, not item 15's evidence. LG 9449 holds that
  evidence.
- *Violation: a stored payload without `result_type` loads as `decimal`, or a type other than `decimal` /
  `money_minor` is accepted* (rule 1; FR-227).
  `packages/model-schema/tests/test_rating_algorithm.py::test_a_stored_model_call_without_result_type_loads_as_the_legacy_default`,
  `::test_a_model_call_accepts_decimal_or_money_minor`, `::test_a_model_call_refuses_any_other_result_type`.

**Not yet detectable at `e0e12dd8`, disclosed:** rule 3's "a GLM step without `result_type` rounds like any other" (the
00:44:31 entry: "No node-kind-dependent meaning of \"absent\"") has no test. The runtime carries it at
`packages/pricing-core/src/pricing_core/rating/runtime.py:656`
(`value = round(glm_prediction) if step.result_type is None else glm_prediction`). The helper `algorithm_payload` accepts
`result_type=None`, but no test on the branch passes it (`git grep 'result_type=None'` over the branch's tests finds no
match). The check that would detect it: *Violation: a GLM `model_call` compiled without `result_type` scores its unrounded
prediction*. That means a GLM case like the legacy/opt-in pair above. This record does not order that test: the test is A-2's,
under the entries above. Rule 4 (a GBM keeps the legacy rounding unless an algorithm opts in) is the GBM half of the
legacy/opt-in test above. A-3's peril-structure nodes (rule 3) are A-3's to prove, and this record names no A-3 test
because none was read for it.

## What this record does not decide

- Which nodes other than GLM and peril-structure components opt in. 00:40:31 item 2 leaves
  a GBM on the legacy rounding unless an algorithm opts in.
- Anything in `RL-1459` other than the clauses in the table.
