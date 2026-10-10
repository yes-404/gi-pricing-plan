---
id: FD-1595
family: finding
title: 03 §4.1's worked example gives a Peril Structure model_call two produced names, which RL-1459 DP-A3-1 (c) refuses at compile
status: closed
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: auditor
tree: fe0b0627590307259ec6d56be7f73115cf245092
corrected_by: []
relates: [WK-1178, RL-1459, RL-1519, FR-222, FR-249, OQ-1460, FD-1374]
---

# FD-1595 — 03 §4.1's example contradicts DP-A3-1 (c)

*Disclosure: drafted under working id 9953; minted as FD-1595 on 2026-10-10, in the D8b batch mint PR. Its correcting record, drafted as working id 9954, is minted as RL-1596 in the same batch.*

**Filed** (drafted on `draft/fd-9953-example`) at the ruling entry in `to-lead.md`, "2026-10-10
14:43:15 BST — RULING: 03 §4.1 worked example vs A-3's compile. The SPEC EXAMPLE is wrong;
(B) with the test pinning the RULE; the correcting RL rides the NEXT docs batch", items 1–4.
Item 3: *"ONE FD (owner WK-1178, LOW: example text, no behaviour), remedy (A)"*. Item 4: *"the
auditor greps 03 for model_call examples producing more than one name and lists any other hits
in the same FD."* Every line number is at `origin/main` `fe0b0627590307259ec6d56be7f73115cf245092`
unless a branch is named.

## The contradiction

`03` §4.1's `RatingAlgorithm` example declares the step `s_rp`, a `model_call` on a Peril
Structure, with two produced names. `RL-1459` DP-A3-1 (c) rules that such a step declares exactly
one, and `compile_bundle` refuses two with `BUNDLE_COMPILE_FAILED`. The code is right
(`CLAUDE.md` §0: which side is wrong was decided by the ruling entry above). No wrong behaviour
ships; the example text is what misleads a reader, and a compile of the example as written fails.

| What | Where | Quoted |
|---|---|---|
| The example's two names | `docs/specs/03-rating-engine.md:270` (step `s_rp`, `:267-270`) | `"produces": ["risk_premium_minor", "peril_risk_premium"]` |
| The second name's declared output | `docs/specs/03-rating-engine.md:257` | `{"name": "peril_risk_premium", "type": "map<string, money_minor>", "required": false}` |
| The same step in RL-1519's worked example | `docs/rulings/RL-01519-pl-9776-dp-f35-1-2-3-…-nfr-500-reads-the-trace-contract.md:347-351` | `"produces": ["risk_premium_minor", "peril_risk_premium"]` |
| The output step that consumes the second name (RL-1519 only; `03` main has no such step) | same RL, `:380-383` | `"s_out_peril" … "output_name": "peril_risk_premium" … "consumes": "peril_risk_premium"` |
| The rule | `docs/rulings/RL-01459-wk-1178-a-3-and-a-4-…-a-0-05-tolerance.md:132-135` | *"DP-A3-1: (c). A `model_call` on a Peril Structure declares exactly one produced name … A step that declares more is refused at compile with `BUNDLE_COMPILE_FAILED`"* |
| The requirement's note | `docs/specs/03-rating-engine.md:158` (FR-249) | *"(Carried 2026-10-10, `RL-1459`: a Peril Structure `model_call` yields one produced name in P2. Per-peril components are `OQ-1460`'s …)"* |
| The refusal | `packages/pricing-core/src/pricing_core/rating/compile.py:850-870`, `_refuse_peril_model_calls`; called at `:976` | `if len(names) > 1: _raise_named("BUNDLE_COMPILE_FAILED", … "a Peril Structure model_call yields one value, the risk premium (FR-222, FR-249)")` |
| The pre-existing note that the example is the case refused | `packages/pricing-core/tests/test_rating_peril_scoring.py:183-190` | `"""Item 8 (DP-A3-1 (c)): the §4 example's two names, BUNDLE_COMPILE_FAILED."""` |
| `RL-1459` already lists the example as a fact found | `docs/rulings/RL-01459-…:94` | *"The `03` example produces two names"* |

`RL-1519`'s worked example (the text the FD-1374 slice carries into `03` §4.1) repeats the same
two names with `consumes`, plus `s_out_peril`. It was written before A-3 merged (`fe0b0627`,
#1265), so it does not cite DP-A3-1 (c).

## How found

The FD-1374 slice (`origin/sl-1536-fd1374-dp-f35-1`, tip `4b53b62a94ed6b5ff328ea1f6172c1bd3a381c8c`,
ledger drafted under working id 9441 on that branch, minted as `LG-1594` and now on `main` at `e4753e47`) adds
`packages/pricing-core/tests/test_rating_declared_reads.py::test_the_03_example_validates_in_full_and_compiles`,
which runs the first JSON block after `### 4.1 ` through `compile_bundle`. On that branch the
`s_rp` names are at `docs/specs/03-rating-engine.md:299` and `s_out_peril` at `:329`.
Against a tree that has A-3, that compile meets `_refuse_peril_model_calls`. The ruling entry
(item 2) has the slice's test pin the rule, with a docstring that cites the example as
known-wrong text pending this FD.

## Severity and remedy

**LOW**: example text, no behaviour (the ruling entry, item 3). Remedy (A): a correcting RL
(`RL-1596`, minted in the same batch as this finding) with `corrects: RL-1519`, the worked example only, that
re-states the example with one produced name on `s_rp`, citing `RL-1459` DP-A3-1 (c) and FR-249.
`RL-1519` gains `corrected_by:` in its front matter only. The `peril_risk_premium` declared
output, and `s_out_peril` on the carrying text, are for that RL to settle against `OQ-1460`
(no step may consume a name that nothing produces, FR-212). It rides the next docs batch (D8),
which merges after the FD-1374 slice, so that slice's Acceptance 4 byte check is not disturbed.

## Item 4 — every other `model_call` example producing more than one name

Predicates, run at `fe0b0627`, read-only. All three are runnable as written.

- P1 `git grep -nP '"produces"\s*:\s*\[[^\]]*,[^\]]*\]' origin/main -- docs` → 3 hits:
  `03-rating-engine.md:270` (this finding); `RL-01519-…:351` (the same example, above);
  `RL-01459-…:94` (a table cell quoting the `03` example, not an example).
- P2 `git grep -nP '"produces"\s*:\s*\[\s*$' origin/main -- docs` → no output (no multi-line array).
- P3 `git grep -nE 'peril_structure_ref' origin/main -- docs/specs docs/workflows` → `03:101`
  (prose, the step-type table) and `03:268` (the `s_rp` step). `02-modelling.md` and
  `docs/workflows/` hold no Peril Structure `model_call` example. Prose predicate
  `git grep -nEi 'produces? (two|both|2|several|multiple)|two produced names|more than one (produced )?name' origin/main -- docs/specs docs/workflows`
  → 3 hits (`02:3280`, `06:756`, `07:111`), none about a `model_call`.
- Frozen plans also hold `"produces": [` with one entry (`PL-01426:590`, `PL-01435:1281`,
  `PL-01520:1312`): single-name, so none contradicts DP-A3-1 (c). A frozen plan is not edited.

**Result: none other.** The only two-name `model_call` example outside `RL-1459`'s own quotation
is `03:270` and its copy at `RL-1519:351`.

## Resolution (2026-10-10, D8b batch)

**Closed**, discharged by `RL-1596` (the correcting record) and the `03` §4.1 change it rules, both
in the D8b batch PR, after the FD-1374 slice merged (`e4753e47`) so that slice's Acceptance 4 byte
check was not disturbed. Check, at the batch tree: `git grep -nP '"produces"\s*:\s*\[[^\]]*,[^\]]*\]' -- docs/specs`
prints no hit (exit 1); the corrected example block's sha256 is the one `RL-1596` states
(`b1c5dcd7c96a002716236320894226a8cb43c85448cf092b59da013837772596`). Event named in the
disposition above: the merge of the correcting RL; this resolution takes effect with the PR's
merge. The close is recorded here on the lead's brief for the batch; the lead gives the verdict.
