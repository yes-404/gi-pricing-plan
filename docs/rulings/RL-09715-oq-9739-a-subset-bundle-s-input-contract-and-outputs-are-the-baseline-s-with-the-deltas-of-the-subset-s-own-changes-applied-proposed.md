---
id: RL-9715
family: ruling
title: OQ 9739 — a subset bundle's input contract and outputs are the baseline's with the deltas of the subset's own changes applied, and changes that depend on each other must share a group (PROPOSED, awaiting the deputy)
status: draft                  # active → superseded | retired (§1.2a) — set active at mint, after the deputy's decision
created: 2026-10-05
owner: decision-maker
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1394, RL-1402, RL-1361, RL-1375, RL-1264, PL-1403, PL-1267, LG-1400, SL-1387, FD-1374, FR-212, FR-213, FR-214, FR-219, FR-246, FR-266, FR-1397, FR-1398, FR-1399]
---

# RL 9715 (working id) — OQ 9739: the proper subset bundle's `input_contract` and outputs

**PROPOSED — awaiting the deputy's decision (the maintainer's, by delegation).** Nothing
below is ruled until the lead relays that decision. The record stays `status: draft`, as
RL 9770 (working id) is held on PR #1060 (`origin/dm-f35-rulings`, read 2026-10-05: `status:
draft # … set active at mint`) after the maintainer's acceptance of 2026-10-01 10:30:00 BST;
it is set `active` at the mint.

## How this was ruled

**Written 2026-10-05, at effort `medium`**, by the decision-maker session `dm-9739`, on the
lead's brief `~/gi-pricing-plan.local/handover/brief-dm-9739-2026-10-05.md`, written on the
deputy's instruction of 2026-10-05 12:51:33 BST, item 1. **Working id 9715 is the lead's
allocation.** All facts were read at `origin/main`
`caa4e411a9c07a389cf47092a923c7761b2b92dc`, 2026-10-05, 12:54–13:40 BST. Unminted records
(OQ 9739, RL 9770, RL 9771) are cited in working-id form and kept out of `relates:` (check 32).

**The question, as raised** (`RL-1394`, the paragraph headed *"Not ruled here, raised for the
lead"*, after DP-S1-8): *"where `input_contract_changed` or `outputs_changed` is true, which
input contract and outputs a **proper** subset bundle declares (a subset holding a candidate
step that consumes a new input may otherwise fail FR-212 at compile, and RW2 fails the run)."*
RW2 is now FR-1398. `PL-1403` (the paragraph headed **OQ 9739**), `LG-1400` (two bullets) and
`RL-1402` (the bullet *"OQ 9739 is not needed"*) each leave it with SL-1387 (WK-673 Slice 3),
which builds subset construction.

## Finding — OQ 9739 has no OQ row

At `caa4e411`, `grep -rn 9739 docs/` matches only `PL-1403`, `LG-1400` and `RL-1402`.
**There is no row in `docs/open-questions.md` (§RATE) and none in `03` §10.** `RL-1394`
itself does not name the working id; it proposed that the lead allocate one. So the question
has been cited by number in three merged records while no OQ row exists for it. The texts
below include both mirror rows, written once at the mint, already closed by this ruling
(the decision-maker records an OQ and sets it `closed` citing the resolver, `document-ids.md`
§1.6 OQ row).

## Verified first, at `caa4e411`

| Fact | Where |
|---|---|
| A `RatingAlgorithm` carries `input_contract: list[InputContractField]` and `outputs: list[AlgorithmOutput]` beside its steps | `packages/model-schema/src/model_schema/rating.py:389-390` |
| `diff_algorithms` reports the contract and the outputs only as two booleans, `old.input_contract != new.input_contract` and `old.outputs != new.outputs`; no field-level delta | `rating.py:550-551`, `:617-618` |
| FR-1399 derives changes from steps and pins only: *"each `step_id` the structural diff (FR-219) reports as added, removed, or present in both with any field changed is exactly one derived change"*; *"a pin difference no step change accounts for is its own derived change, of kind `pin`"*. A contract or output difference is no derived change | `docs/specs/03-rating-engine.md:192` |
| The contract's `kind` enum is `["pin", "step_added", "step_removed", "step_changed", "table_repointed"]` | `docs/contracts/schemas/dislocation-run.schema.json:101` |
| FR-212's unresolved-name check is step to step: a step's `consumes` must be some step's `produces`. **It does not read `input_contract`**; nothing ties an input step's `input_name` to the contract at the model | `rating.py:415-423` (raise at `:421`) |
| FR-214's check: every declared output has an output step, else `ValueError` | `rating.py:403-410` (raise at `:409`) |
| A dislocation pass projects the portfolio to `quote_id` plus **that bundle's** declared input names (`RL-1394` DP-S1-1 (b)) | `packages/pricing-core/src/pricing_core/rating/analysis.py:151-152` |
| Scoring validates each row against every declared field (required, type, range, domain): FR-213 | `packages/pricing-core/src/pricing_core/rating/score.py:333-350` |
| `compile_bundle(version: RatingVersion, resolver)` is the compile path FR-1398 binds every subset to | `packages/pricing-core/src/pricing_core/rating/compile.py:573` |
| FR-1398: each subset is *"built at step granularity from the baseline's pins and algorithm with that subset's changes substituted"*; a subset that fails to compile *"fails the run with `BUNDLE_COMPILE_FAILED`, naming the subset; it is never skipped"* | `03:191` |
| FR-266: v(S) is computed *"for each of the 2^K subsets"* (so ∅ and the full set too), and the parts must sum to *"candidate minus baseline payable premium"*; FR-1397 fails the run otherwise | `03:189`, `:190` |

**So the contract and the outputs decide three things for a subset:** which portfolio columns
reach the engine (`analysis.py:152`), which rows are refused as contract violations
(`score.py:338`), and whether the subset compiles at all (FR-214, `rating.py:409`). And
because FR-1399 derives no change for them, they belong to no subset today: the choice is
undefined, not merely open.

**`RL-1394`'s parenthetical, corrected.** It says a subset with a step that *"consumes a new
input may otherwise fail FR-212 at compile"*. FR-212 does not read the contract
(`rating.py:415-423`). The FR-212 failure it foresaw is real, but its cause is a **dependency
between derived changes** (a changed step consumes a name only another change's step
produces), and no choice of contract prevents it. It is DP-2 below. The contract question is
DP-1.

## DP-1 — which `input_contract` and `outputs` a proper subset bundle declares

Worked case used below. The baseline has inputs `{age}`. The candidate adds the field `ncd`
(`int`, 0–9), an input step `in_ncd` producing `ncd`, and edits step `rate` to consume it.
FR-1399 derives c1 = `in_ncd` (`step_added`) and c2 = `rate` (`step_changed`). Separately, the
candidate tightens `age`'s `max` from 99 to 90 with no step edit.

### Options

- **(a) The baseline's, always.** Subset {c1, c2} keeps the contract `{age}`, so
  `analysis.py:152` projects `ncd` away. The candidate's new step runs without its input,
  and v(S) is the premium of a bundle no one authored. With an output removed by a step
  removal, the subset declares an output whose step is gone and fails FR-214
  (`rating.py:409`) → `BUNDLE_COMPILE_FAILED`, failing the run (FR-1398). If v(N) is read
  from a subset bundle, v(N) ≠ the candidate and FR-1397 fails the run on every portfolio.
  The `age` range change is in no subset, so its effect is silently spread across the
  changes by Shapley's efficiency property.
- **(b) The candidate's, always.** The mirror image. A field the candidate removes (with its
  input step, a `step_removed` change) disappears from every proper subset that keeps the
  baseline's step, so that step loses its column. A new declared output whose output step
  is not in S fails FR-214. v(∅) ≠ the baseline. The `age` change is applied to every
  subset, so it is attributed to no change, and the parts still sum only because FR-266
  takes the endpoints from v(∅) and v(N).
- **(c) Recommended: the baseline's, with the contract and output deltas of S's own changes
  applied.** Each field-level difference between the two contracts (a field added, removed,
  or with any attribute changed), and each difference between the two output lists, is
  assigned to exactly one derived change. A field travels with the change to the input step
  that reads it (by `input_name`, on the side that declares the field: the candidate for an
  added or changed field, the baseline for a removed one). An output travels with the change
  to the output step that writes it (by `output_name`). This is FR-1399's pin rule applied to
  the contract. A difference no derived change accounts for is **its own derived change**, of
  new kind `input_field` or `output`. In the worked case, `ncd` travels with c1, and the
  `age` change becomes c3, `input_field`. Every subset is then exactly *"the baseline … with
  that subset's changes substituted"* (FR-1398's own words), v(∅) is the baseline, v(N) is
  the candidate, and every premium effect has an owner.
- **(d) Refuse attribution** whenever `input_contract_changed` or `outputs_changed`, with
  `VALIDATION_FAILED`. Safe, but it removes attribution from the most common structural rate
  change, a new rating factor.

### Trade-offs

| | (a) | (b) | (c) | (d) |
|---|---|---|---|---|
| v(∅) = baseline, v(N) = candidate | v(N) no | v(∅) no | **yes** | n/a |
| Subset compiles whenever its steps do | no (FR-214) | no (FR-214) | **yes** | n/a |
| Every premium effect has an owner | no | no | **yes** | n/a |
| Cost | none now | none now | FR-1399 amended, two `kind` values; `diff_algorithms` needs field-level deltas (today two booleans) | attribution lost |

### PROPOSED: (c)

**Why.** (c) is not a new rule: it is FR-1398's *"with that subset's changes substituted"*
applied to the two parts of the algorithm FR-1399 forgot, using the rule FR-1399 already
uses for pins. (a) and (b) each break one endpoint and fail FR-214 on a removed output, and
each rate subsets that no author wrote. (d) gives up the feature for the case that most
needs it.

**What it costs.** `diff_algorithms` must expose which fields and outputs differ, not only
that they do. The two booleans stay, for the approval summary (FR-219). Slice 3 adds the
field-level delta beside them. A derived change list can now hold an `input_field` or
`output` change, so K can be larger by the number of unaccounted contract changes, which
counts toward FR-266's above-six rule like any other change.

**Which side was wrong (`CLAUDE.md` §0): the spec.** FR-1399's derivation omits two parts of
the diff FR-219 reports, so FR-1398's construction is undefined for them. No code builds
subsets yet (Slice 3 does), so the code is not wrong.

## DP-2 — raised at ruling: changes that depend on each other

In the worked case, subset {c2} holds the edited `rate`, which consumes `ncd`, while `in_ncd`
(c1) is not in S. The subset fails FR-212 (`rating.py:421`) under every DP-1 option, and
FR-1398 fails the run. The same holds for a removal: removing a producer without its
consumer. With no groups given, FR-1399 makes each derived change its own group, so **the
default run fails whenever the candidate adds a factor**.

### Options

- **(i) Recommended: refuse up front.** Before compiling any subset, the server finds each
  pair of change groups where a step of one consumes a name that, in the subset holding that
  group alone, no step produces. It refuses with `VALIDATION_FAILED`, naming the changes that
  must share a group. The analyst groups them; K never changes without the analyst seeing it.
- **(ii) Merge automatically.** Dependent derived changes are merged into one derived change
  before numbering. A default run then works, but K and the change list change silently,
  and the partition the analyst sees differs from the structural diff.
- **(iii) Leave it to compile.** The first failing subset fails the run with
  `BUNDLE_COMPILE_FAILED` (FR-1398 as written). Correct but late: after up to 2^K − 1
  compiles, with a message about a subset, not about which changes to group.

### PROPOSED: (i)

**Why.** It keeps the FR-1399 rule that the analyst's groups are the partition, refused
with a named reason when wrong (its existing `VALIDATION_FAILED` check). It fails before
any rating, so cost is bounded. (ii) is the friendlier default but changes what the
attribution is *of* without the analyst choosing it. The deputy may prefer (ii) for the
default run only; the texts below would change in one sentence.

## Ruled

**PROPOSED — awaiting the deputy's decision; nothing here binds until the lead relays it.**

| DP | Proposed |
|---|---|
| DP-1 (OQ 9739) | **(c)** a subset bundle's `input_contract` and `outputs` are the baseline's with the contract and output deltas of its own changes applied; each delta travels with the input or output step change that reads or writes it, else it is its own derived change (`input_field`, `output`) |
| DP-2 | **(i)** changes that depend on each other must share a group; refused up front with `VALIDATION_FAILED`, naming them |

## Proposed texts (applied at the mint, after the decision)

### P1 — `03` FR-1399, appended to the row before its closing note

```markdown
*(Amended <date>, WK-673 Slice 3, `RL-<n>`, deciding OQ-<n>.)* **The input contract and the outputs travel with the changes too.** Each field-level difference between the two input contracts (a field added, removed, or with any attribute changed) is part of the derived change to the input step that reads that field by `input_name`, on the side that declares it (the candidate for an added or changed field, the baseline for a removed one); each difference between the two output lists is part of the derived change to the output step that writes it by `output_name`. Where more than one derived change reads the field, it travels with the first in the derived order. A contract difference no derived change accounts for is its own derived change, of kind `input_field`, and an output difference no derived change accounts for is its own derived change, of kind `output`; both are numbered after the unaccounted pin differences, sorted by field or output name. **Changes that depend on each other must share a group.** Before any subset is compiled, the server checks every group: where a step in the subset holding that group alone consumes a name no step in that subset produces (FR-212), the run is refused with `VALIDATION_FAILED`, naming the changes that must share a group.
```

### P2 — `03` FR-1398, the sentence after *"compiled by `compile_bundle` and hydrated by `load_bundle`"*

```markdown
*(Amended <date>, `RL-<n>`.)* A subset bundle's `input_contract` and `outputs` are the baseline's with the contract and output differences of the subset's own changes applied (FR-1399), so the subset of no changes is the baseline and the subset of every change is the candidate.
```

### P3 — `docs/contracts/schemas/dislocation-run.schema.json:101`, the whole line

```json
          "kind": {"enum": ["pin", "step_added", "step_removed", "step_changed", "table_repointed", "input_field", "output"]},
```

### P4 — OQ 9739's mirror rows, written once at the mint, closed

`docs/open-questions.md`, §RATE, appended as the table's last row:

```markdown
| ~~**OQ-<n>**~~ ✔ | ~~Which `input_contract` and `outputs` does a proper attribution subset bundle declare when the candidate's differ from the baseline's?~~ **DECIDED <date>: (c), by `RL-<n>`.** Raised 2026-10-03 by `RL-1394` ("Not ruled here") under working id 9739; first recorded as a row at this mint. | (a) the baseline's: projects new inputs away, fails FR-214 on a removed output, v(N) ≠ candidate. (b) the candidate's: the mirror image, v(∅) ≠ baseline. (c) the baseline's with each subset change's contract and output deltas applied; an unaccounted delta is its own change. (d) refuse attribution when either differs. | **Decided (c)**, with dependent changes required to share a group (`RL-<n>` DP-2). | decision-maker | Closed |
```

`03` §10, appended as the table's last row:

```markdown
| ~~**OQ-<n>**~~ ✔ | ~~Which `input_contract` and `outputs` does a proper attribution subset bundle declare?~~ **DECIDED <date>: (c), the baseline's with the deltas of the subset's own changes applied, by `RL-<n>`** (FR-1398, FR-1399 as amended). Raised by `RL-1394` under working id 9739. |
```

## Acceptance — the violation that must become detectable

This record builds nothing. Slice 3 carries these, each shown red on deliberately broken input:

- *Violation: a subset bundle's contract omits a field its own changes add.* A test builds
  the worked case and asserts subset {c1, c2}'s contract holds `ncd` and its projected frame
  carries the column; broken by building the subset from the baseline's contract.
- *Violation: the endpoints differ from baseline and candidate.* A test asserts the subset
  bundles for ∅ and for every change hash-equal the compiled baseline and candidate.
- *Violation: an unaccounted contract change has no owner.* A test with only `age`'s range
  changed asserts one derived change of kind `input_field`.
- *Violation: dependent changes run ungrouped.* A test with c1 and c2 ungrouped asserts
  `VALIDATION_FAILED` naming both before any compile.

## What it obliges

- **The deputy:** decide DP-1 and DP-2.
- **The lead, at the mint:** allocate the OQ id, mint this record, and apply P1–P4 in one
  commit with it.
- **Slice 3 (SL-1387):** field-level contract and output deltas beside `diff_algorithms`'s
  two booleans; the two new kinds in model-schema and the contract; the DP-2 check; the four
  tests above. Its leaf plan cites this record for OQ 9739 instead of carrying the question.
