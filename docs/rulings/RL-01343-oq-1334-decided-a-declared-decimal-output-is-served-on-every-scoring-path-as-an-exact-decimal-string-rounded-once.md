---
id: RL-1343
family: ruling
title: OQ-1334 decided — a declared decimal output is served on every scoring path as an exact decimal string, rounded once by its output step
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 8cef871d4ec30869dc3ef20559f3cac64e239a5c
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1334, FD-1333, FD-1335, RL-1329, OQ-1316, FR-214, FR-226, FR-227, FR-250, FR-254, FR-273, NFR-502, WK-674, WK-675]
---

# RL-1343 — OQ-1334 decided: a declared `decimal` output is served on every scoring path as an exact decimal string, rounded once by its output step

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-oq1334`. Its first command,
`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"`, printed `CLAUDE_EFFORT=high`. The maintainer ordered
the ruling in `to-lead.md` (a local channel file outside the repository), in the entry headed
"2026-09-30 22:26:52 BST — ETA refresh accepted (22:35 BST, main 8cef871d); one gap: nobody is
scheduled to rule OQ-1334". Its words: "a high-effort decision-maker session … on OQ-1334 as
filed in FD-1333 (options (a)–(d), recommendation (a) with (d) as the interim)". This session
read that entry itself. The lead's brief relayed the same order and dated it about 22:45 BST.
The entry's own header says 22:26:52.

**Minted 2026-09-30 as RL-1343** (`python3 scripts/doc-id.py next --ref 71b672205f7212008d0ff00b5cbc4810b56f12e6`
printed `1342`. The WK-674 Slice 3 leaf plan, filed as PL 9947, takes it as PL-1342, and the lead
allocated 1343 to this record in the mint GO.) It was filed under working id 9974, hand-assigned by the lead,
who is the only allocator (FD-1338). Quotations of the maintainer's entries keep working ids as
written, and so does the appendix script's docstring, which is kept as it was run.

**The question, as filed.** `FD-1333` raises it, and `docs/open-questions.md` and `03` §10
mirror it: *should `/score` serve a declared `decimal` output as a JSON string, as batch
scoring does, instead of the float JSON number it serves today?* The roadmap §10 row "Before
WK-674 Slice 3 merges" adds a second limb: *may a `decimal` output carry money?* Both are
ruled here.

**The maintainer's recorded lean**, weighed and not followed as an instruction: (a), with (d)
as the interim if (a) cannot be ready when Slice 3 merges. **This ruling adopts (a) and does
not adopt the (d) interim** (§6 gives the reason). The lead should put that one departure to
the maintainer.

## Verified first, at 8cef871d4ec30869dc3ef20559f3cac64e239a5c

`origin/main` was `8cef871d` at 22:36 BST, when this session fetched it. `FD-1333` measured at
`8d5c67a5`, and `3a5f7cd5` (#967's code slice) has changed `score.py` since then. So every
citation below was re-read at `8cef871d`, and its line numbers are for that tree.

**The code path.**
- `_build_outputs` (`packages/pricing-core/src/pricing_core/rating/score.py:657-678`). A
  declared output named after a ladder rung takes the rung's value (`:672`). Any other
  declared output takes `result[str(source[0])]` (`:676`). That is the engine's raw value, a
  Python `float` for a fractional result. Nothing converts it.
- `build_scoring_result` builds `ScoringResult(...)` (`:779`), whose field is
  `outputs: dict[str, object]` (`packages/model-schema/src/model_schema/scoring.py:186`).
- `/score` returns `Response(content=result.model_dump_json(), …)`
  (`backend/src/app/api/score.py:321`). A float becomes a JSON number.
- Batch scoring serialises the same `scored.outputs` (`score.py:1030`) through
  `_outputs_json` (`:906`) and `_coerce_output_value` (`:865`). Its `decimal` branch is
  `Decimal(repr(value))` then `str(...)` (`:887-889`), which gives a JSON string. That string
  is the float's shortest repr, not the engine's value.
- **One more defect, not named in `FD-1333`: neither path applies the output step's declared
  rounding to a non-rung `decimal` output.** `RatingOutputStep.rounding` is required
  (`packages/model-schema/src/model_schema/rating.py:322-325`), and FR-226 (`03:112`) says
  "`output` steps declare rounding explicitly". Neither branch above reads it. Reproduced on
  the real `score_one` (the script is in the appendix, and its output is kept verbatim). A
  declared `decimal` output with `half_even`, dp 2, over an engine value of `1.23456`:

  ```text
  declared rounding half_even dp 2; score_one outputs['r'] = 1.23456
  /score wire: {'payable_premium_minor': 1507, 'r': 1.23456}
  batch _outputs_json: {"payable_premium_minor": 1507, "r": "1.23456"}
  ```

  `RL-1329` §4 already rules the declared rounding, applied once, for rung outputs and for
  `money_minor` non-rung outputs.
  After WK-674 Slice 3, the non-rung outputs of the other types are the only outputs whose
  declared rounding is still ignored.

**The text.**
- FR-214 (`03:83`): the algorithm "declares typed **outputs**". FR-250 (`03:162`): `/score`
  returns "the ladder, outputs". Neither gives an output's JSON type.
- FR-227 (`03:113`): "A monetary result must be `decimal` or `money_minor` (R2)". The type
  alias agrees: "A declared result type. `decimal`/`money_minor` carry money; `float` is
  refused." (`rating.py:234`).
- FR-273 (`03:222`): "any value returning to Python for further arithmetic is an integer minor
  unit or a string".
- The batch column `outputs_json` (`03:628`): "`decimal` as a JSON string — never a JSON number,
  so an exact `Decimal` and a lossy `float` cannot be confused reading the column back". The
  text scopes itself to "this path".
- `CLAUDE.md` §7: "Money is integer pence/cents, or Decimal in the rating path — never float."
  The platform's wire form for an exact decimal is a string: `common/money.schema.json`
  `$defs.Decimal` is `{"type": "string", "pattern": "^-?[0-9]+(\\.[0-9]+)?$"}`, and the
  `contract-schema` skill says "Money is `MoneyMinor` (integer minor units) or `Decimal` (a
  string) — never a JSON number with a fractional part (FR-10)".

**The contracts.** `docs/contracts/schemas/scoring.schema.json:54` is
`"outputs": {"type": "object"}`. The generated `docs/contracts/openapi/generated.json` gives
`POST /api/v1/score` a 200 response with `"schema": {}` (`FD-1335`). No contract types an
`outputs` value today.

**Who declares a `decimal` output.** At this tree,
`git grep -n -E "type.{1,6}decimal" -- '*.py' '*.json' '*.jsonl' ':!docs'`, with `result_type`
lines removed, prints 12 lines (counted with `wc -l`, not a bounded listing). Eleven of them
are not output declarations: input fields (with `nullable`), generator specs (with
`min`/`max`), a type-name comment, the serialiser's branch and an error-type list. One is an
output declaration:
`packages/pricing-core/tests/test_rating_score_batch.py:84`, the `age_factor` fixture (dp 2,
`:95`). Its assertion (`:192-196`) compares `Decimal(value)` numerically, so it holds when
the string carries the declared dp. This agrees with `FD-1333`'s evidence 5 count (1).
The other consumers of `outputs`, from
`git grep -n outputs -- packages/pricing-core/src backend/src packages/model-schema/src`:
- **Golden quotes do not compare outputs.** `GoldenQuoteExpected` holds only
  `payable_premium_minor` and `outcome` (`packages/model-schema/src/model_schema/regression.py:46-56`).
- **The trace summary does compare outputs.** `summarise_result`
  (`backend/src/app/platform/traces.py:143-155`) dumps `outputs` into the sampled served
  summary that a reproduction is checked against. Its docstring says "`outputs`' values are
  `int`/`str`/`bool` by construction (`_coerce_output_value` …)". **That is false on the
  `/score` path:** `_coerce_output_value` runs only in batch, and a `decimal` output reaches
  the summary as a float.

**The state of the Works.** WK-1178 is `active` ("P2 standing maintenance: hotfixes,
dependency bumps and security findings", `docs/roadmap.md:1081`). WK-671, which owns `/score`,
is `closed` (`:650`). WK-675 is `active` (`:840`). SL-1257 (WK-674 Slice 3) is `draft`
(`:767-780`). The maintainer's 22:33:30 BST entry, Decision 4, schedules it "at its PL 9947
mint (~03:30)" (PL 9947 is minted as PL-1342).

## Options, weighed

`FD-1333` states options (a)–(d). This section adds only what changes their weight.

- **(b), keep a JSON number: rejected.** A `decimal` output may carry money (§2). A float then
  carries money, against R2, FR-273 and `CLAUDE.md` §7. To confine (b) to non-money outputs, the
  platform would have to know which `decimal` outputs are money. It cannot: FR-213's input
  types have no money type, and `OQ-1316`'s row records that inference over ZEN expressions
  does not exist either. So (b) is not safe to apply.
- **(c), an exact JSON number literal: rejected.** Its digits are exact on the wire. But every
  JSON consumer that uses float64 (the browser, most JSON libraries) parses the value to a
  float. The client cannot tell an exact value from a lossy one. That is the confusion `03:628`
  exists to prevent, and the one the `vue-frontend` skill forbids: "Never `parseFloat` a
  `DecimalStr`".
- **(d), refuse `decimal` as an output type: rejected, also as an interim** (§6).
- **(a), a JSON string: adopted.** It is the platform's existing wire form for an exact decimal,
  applied to the one path that lacks it. It needs no money/non-money classification.

## Ruled

### 1. Option (a)

**A declared output of type `decimal` is served as a JSON string on every scoring path:
`POST /api/v1/score`, both results inside `POST /api/v1/score/compare`, and the batch column
`outputs_json`. It is never a JSON number.** The batch column's rule (`03:628`) is extended to
the field `ScoringResult.outputs` wherever that field is serialised. One field has one JSON
type per declared output type.

### 2. A `decimal` output may carry money

**Yes.** FR-227 says so, and so does the type alias (`rating.py:234`). `RL-1329`'s first
draft read `decimal` outputs as "not money". A dated amendment withdrew that reading before
the record was minted (`RL-1329` §4, "amended 2026-09-30, on the maintainer's entry of
17:08:59 BST"). No
requirement narrows FR-227 for outputs, and this ruling does not narrow it. So R2, FR-273 and
`CLAUDE.md` §7 bind every `decimal` output. Rule 1 meets them whether or not a given output
is money, so no output needs a money classification.

### 3. The served value: the engine's exact value, rounded once, in one canonical form

1. **The source.** The value is the engine's exact decimal for the output step's source. It is
   read across the binding with the engine's `string()`, which is the terminal read
   `RL-1329` §2 step 1 introduces. It is never the float in `result`, and never
   `Decimal(repr(float))`. This is FR-273's string limb.
2. **One rounding.** The value is rounded once, with the output step's declared `RoundSpec`
   (FR-226), in exact decimal arithmetic. That is the rounding the output step declares, and
   no other rounding is added. This is the rule `RL-1329` §4 applies to `money_minor`
   outputs.
3. **The form.** The string is positional. It has exactly `dp` digits after the point, and no
   point when `dp` is 0. It has a leading `-` only for a value below zero, so a zero is
   written unsigned (`"0.00"`, never `"-0.00"`). It has no exponent and no `+`. So it matches
   `common/money.schema.json#/$defs/Decimal`. It is the rendering of `PositionalDecimalStr`,
   which `RL-1329` §3 introduces (`format(value, "f")`), applied to the value after it is
   rounded to `dp`. One `RoundSpec` gives one string for one value, so a served value and a
   reproduced value compare as strings.
4. **One producer.** `_build_outputs` produces the string once, and **the string** is stored in
   `ScoringResult.outputs`, not a `Decimal`. The field is `dict[str, object]`, and Pydantic
   writes a `Decimal` held there with `str()`, which gives exponent form for some values
   (`Decimal("0E-7")`, a zero rounded to dp 7, is written `"0E-7"`; `FD-1337` is the same
   defect in `DecimalStr`). `format(value, "f")` alone keeps a negative zero (`"-0.00"`), so
   the producer drops that sign. All three behaviours were checked with the repository's
   `.venv` Python and Pydantic at this tree. Batch writes that same string. It checks the
   value and does not convert it: `_coerce_output_value` refuses a `float` for `decimal`, as it already refuses one
   for `money_minor`. So `/score` and `outputs_json` carry the same bytes for the same output.

### 4. The contract: no `outputs` value is a JSON number with a fraction

The field stays a map keyed by the names each algorithm declares. `FD-1335` §2 agrees that open
keys may be right, and this ruling does not type values per name. What changes:
- **`ScoringResult` refuses a `float` anywhere in `outputs`, at construction.** A `decimal` value
  is a string by rule 3, and a `money_minor` value is an integer by `RL-1329` §4. `float` is
  already refused as a declared type (`_reject_float_type`, `rating.py:220-235`). So a float in
  `outputs` has no valid declared type, and refusing it decides nothing about the shape of a
  valid value. Batch already refuses a float `money_minor` value in the same spirit
  (`_coerce_output_value`, `score.py:881-886`). The Python spelling (a field
  validator, or a value-type union) is the carrier's choice.
- **The contract says the same thing,** generated one way from `model-schema` (`CLAUDE.md`
  §2). The generated JSON Schema's value type for `outputs` admits no non-integer number.
  The hand-authored `docs/contracts/schemas/scoring.schema.json:54` changes to match, and the
  contract guard (`backend/tests/test_contracts.py`, the `contract-guard` skill) compares the
  two. `scripts/generate-contracts.py --check` stays green.

This is a **breaking change of a served JSON type**. A client that reads a `decimal` output as
a number gets a string. Every committed consumer is listed above, and no algorithm, seed or
example declares a `decimal` output, so no consumer in the repository changes. The carrying
slice's release note names the change, as `RL-1329` §4 names its `money_minor` change.

### 5. Carrier and timing: WK-1178, after WK-674 Slice 3 merges

**Owner: WK-1178.** `/score` belongs to WK-671, which is closed, and WK-1178 is the active Work
that carries fixes to closed Works' code. `FD-1335` gives WK-1178 the `/score` contract for
the same reason.

**After Slice 3, not inside it:**
- Rule 3.1 needs the `string()` read, and Slice 3 builds that read (`RL-1329` "What it
  obliges"). Before Slice 3, (a) could only use `Decimal(repr(float))`, which is not exact
  (`FD-1333` evidence 4c), and it would have to be rebuilt.
- The change edits files that Slice 3 also edits: `score.py` (`_build_outputs`),
  `model_schema/scoring.py`, `docs/contracts/` and `backend/tests/test_contracts.py`. It
  serialises after Slice 3 by the plans' own rule for shared files.
- Putting it in Slice 3 would widen an acceptance that the maintainer ruled "NOT widened"
  (`RL-1329` §4, C2). `RL-1329` also scoped `decimal` outputs out of Slice 3 in words.

**How it fits with `FD-1335` Part A.** The two are different changes to the same contract, and
both belong to WK-1178. Part A documents the `/score` and `/score/compare` 200 responses as
`$ref ScoringResult`/`ScoreComparison`, with no outbound validation (NFR-502). Rule 4 types the
values inside `ScoringResult.outputs`.
- **Part A does not wait for this ruling or for Slice 3.** It must still land before a WK-675
  slice that consumes `/score` or `/score/compare` dispatches.
- **This change needs no hold on WK-675.** After Part A, the generated client types an
  `outputs` value as `unknown`. Rule 4 narrows `unknown` to a union, and narrowing breaks no
  consumer written against `unknown`. A WK-675 consumer displays an `outputs` value and does no
  arithmetic on it (the `vue-frontend` skill's rule for exact decimals). Then the change from
  number to string needs no frontend edit.
- **If both are ready together,** one WK-1178 slice may carry both. That is the lead's cut.
  Either order is correct.
- **The `NFR-502` re-measure.** A construction-time check on `outputs` runs on the `/score`
  hot path. So the slice that carries rule 4 re-measures `NFR-502` and quotes the figure,
  as `FD-1335` Part A must.

### 6. No interim (d): the gate is discharged by this ruling

The roadmap row "Before WK-674 Slice 3 merges" holds Slice 3's merge until "OQ-1334 is ruled
(a), or (d) is ruled as the interim". **This ruling is (a).** Slice 3's merge is not held on
the delivery of (a). The maintainer's lean asked for (d) as the interim if (a) could not be
ready when Slice 3 merges. It cannot be ready, because it follows Slice 3 (§5). This ruling
declines the interim for four reasons:
1. **The interim protects nothing that exists.** No algorithm, seed or example declares a
   `decimal` output, there is no production, and the maintainer confirmed `FD-1333` LOW (the
   entry headed "2026-09-30 17:13:45 BST", quoted in `FD-1335`).
2. **Slice 3 does not make it worse.** Its dispatch record (below) keeps `decimal` outputs
   exactly as they are today. So the window between Slice 3's merge and the WK-1178 slice is
   the same state that exists now.
3. **(d) is itself a contract change, made twice.** An algorithm that is valid today would be
   refused at save and at compile, and then accepted again when (a) lands. Each step needs an
   amendment to FR-214 or FR-227, an error path and a red test. (d) would also break the
   committed fixture `test_rating_score_batch.py:84`, which is the only evidence for
   `03:628`'s `decimal` rule.
4. **(d) collides with Slice 3.** It would add a check to `compile.py`'s `ALGORITHM_CHECKS`,
   which Slice 3 also edits (`RL-1329`, `_check_clamp_placement`).

**If the maintainer still wants the window closed**, (d) remains available as a separate ruling.
The cost is set out above.

### 7. `OQ-1316` and `RL-1329` R0

`RL-1329` R0 ("`round` appears only on the last rung") is bound to `OQ-1316`. This ruling
touches neither of them. A `decimal` output is not a ladder rung, so R0 does not apply to it.
Rule 3.2's "one rounding" is the output step's own rounding (FR-226). `OQ-1316` asks whether a
rounding is offered anywhere else. If it is ruled (a) or (b), an output whose source was already
rounded upstream could be rounded again at its output step, and whether that breaks FR-226's
"never happens twice" is `OQ-1316`'s to rule. This ruling does not decide it in advance, and it
holds unchanged under `OQ-1316`'s interim (c).

## What WK-674 Slice 3's dispatch record must carry

1. **The gate.** `OQ-1334` is ruled (a) by this record. Once this record is minted, the row
   "Before WK-674 Slice 3 merges" no longer holds Slice 3's merge. Slice 3 does not deliver (a).
2. **No change to non-rung outputs of other types.** Slice 3 changes nothing about how a
   declared non-rung output of type `decimal`, `bool`, `string` or `date` is served. Its value
   and its JSON type stay as they are. Slice 3's `to_wire` may emit the `string()` read for
   every output step's source. But `_build_outputs` must not put that string, or a `Decimal`,
   into `ScoringResult.outputs` for these types. Pydantic writes a `Decimal` as a JSON string,
   so that would be this ruling's type change, made inside Slice 3 without the contract and
   without an accepted visible change. The slice audit reads this branch of `_build_outputs` in
   Slice 3's diff (`origin/main...` the slice branch) and confirms it.
3. **The release note.** Slice 3's release note does not mention `decimal` outputs.
4. **The next slice.** The WK-1178 slice that delivers this ruling is cut after Slice 3 merges.
   It serialises with Slice 3 on the files that §5 lists.

## What it obliges

The WK-1178 slice, cut after WK-674 Slice 3 merges:

- `_build_outputs`: rules 3.1–3.4 for every declared non-rung `decimal` output.
- `_coerce_output_value`'s `decimal` branch checks the value and refuses a `float`. It no
  longer calls `Decimal(repr(value))` (rule 3.4).
- `model_schema.scoring.ScoringResult.outputs` and the contract (rule 4): the hand-authored
  `scoring.schema.json`, regenerated `docs/contracts/`, the contract guard,
  `generate-contracts --check` green, and `NFR-502` re-measured.
- The `summarise_result` docstring (`traces.py:147-151`) cites the construction-time refusal as
  the reason its claim holds. It no longer cites `_coerce_output_value`, which runs only in batch.
- A release-note line: a declared `decimal` output changes on `/score` and `/score/compare`
  from a JSON number to a JSON string, and the declared rounding is now applied (on batch too).
- **No stored data is migrated.** No committed algorithm declares a `decimal` output. The slice
  checks that no stored Rating Version in the development databases declares one, or lists the
  ones that do.

## Acceptance — the violation that must become detectable

Each case is shown red on the tree before the fix (`CLAUDE.md` §13), with a declared
`decimal` output on the real `score_one`. The `/score` case goes through the route.
1. **Type.** On `/score`, and in each `/score/compare` result, the output is a JSON string.
   Today it is a number.
2. **Rounding.** An engine value of `1.23456`, with `half_even` and dp 2, serves `"1.23"`.
   Today `/score` serves `1.23456` and batch serves `"1.23456"`. A tie at the declared dp
   also rounds half-even, for example `1.225` to `"1.22"`.
3. **Exactness.** An engine value with more digits than a float holds is served exactly. For
   example, `1234567.1234567890123456` at dp 16 serves `"1234567.1234567890123456"`. Today
   both paths lose the digits after the sixteenth (`FD-1333` evidence 4).
4. **Form.** dp 4 over `3.3` serves `"3.3000"`. A negative value that rounds to zero serves
   `"0.00"`. No exponent appears for a small value or a zero at a high dp: `0.0000001` at dp 7
   serves `"0.0000001"`, and `0` at dp 7 serves `"0.0000000"`.
5. **One producer.** For the same output, `outputs_json` and the `/score` body carry
   byte-identical strings. `test_score_batch_and_score_one_produce_byte_identical_ladders`
   (FR-254) gains this assertion.
6. **The refusal.** Building a `ScoringResult` with a `float` in `outputs` raises, and so does a
   float inside a nested map. The contract guard fails on a planted schema whose `outputs`
   value admits a non-integer number.

## Spec changes in this commit

- `03` FR-214 gains a dated clause with rules 1–4 and the carrier.
- `03` §10 and `docs/open-questions.md`: `OQ-1334` is struck and marked decided, and both
  point here.
- **Not edited here: `docs/roadmap.md`.** The row "Before WK-674 Slice 3 merges" still needs
  `OQ-1334` struck and its count recounted to "1 (0 open)". The lead does that at mint, as for
  `OQ-1235`'s row (the recount "of #939" landed in mint batch 3, `e3600789`). `FD-1333` and
  `FD-1335` are frozen and are not edited. `FD-1333`'s register row takes owner WK-1178 at the
  lead's turn.

## Observed, not ruled (for the lead)

- **Compound declared output types are not served safely either.** `03` §4.1's example
  declares `peril_risk_premium` as `map<string, money_minor>`. `_build_outputs` would serve it
  raw, and batch refuses any type outside `_KNOWN_OUTPUT_TYPES` (`score.py:862`). Only the
  spec's examples declare such a type. `git grep -n -E '"type"\s*:\s*"(map<|array<|ladder)'`
  finds none outside `docs/`. Rule 4's refusal makes such an output fail on `/score` if its
  values are floats, which is correct but not designed. How a compound output is served is a
  separate question.
- **The trace summary's docstring** (`traces.py:147-151`) makes a claim that is false today
  for a `decimal` output. It is corrected in the slice above. No sampled summary is affected,
  because no committed algorithm declares one.

## Appendix — the rounding check, verbatim

Run at `8cef871d` from the worktree root, with `PYTHONPATH=packages/pricing-core/src:packages/model-schema/src:packages/pricing-core/tests`,
under the repository's `.venv` Python. It loaded `score.py` from the worktree, as its first
output line (not reproduced above) showed. It writes no file, and `git status --short` printed
nothing afterwards.

```python
"""RL 9974 check: is a non-rung `decimal` output's declared RoundSpec applied on /score (score_one) or on batch (_outputs_json)?"""
import asyncio, json, sys
sys.path.insert(0, "packages/pricing-core/tests")
import test_rating_score as T
from pricing_core.rating import score as sm
print("score module:", sm.__file__)
_orig = T._algorithm_payload
def patched(**kw):
    p = _orig(**kw)
    p["outputs"] = p["outputs"] + [{"name": "r", "type": "decimal", "required": False}]
    p["steps"] = p["steps"] + [
        {"step_id": "s_r", "type": "expression", "label": "r", "expr": "1.23456 + 0 * risk_premium_minor",
         "result_type": "decimal", "consumes": ["risk_premium_minor"], "produces": "r_value"},
        {"step_id": "s_out_r", "type": "output", "label": "r out", "output_name": "r",
         "rounding": {"mode": "half_even", "dp": 2}, "consumes": ["r_value"]},
    ]
    return p
T._algorithm_payload = patched
async def main():
    compiled = await T._compiled()
    res = await sm.score_one(compiled, T._ctx())
    print("declared rounding half_even dp 2; score_one outputs['r'] =", repr(res.outputs["r"]))
    print("/score wire:", json.loads(res.model_dump_json())["outputs"])
    algo = compiled.bundle.algorithm if hasattr(compiled, "bundle") else compiled.algorithm
    print("batch _outputs_json:", sm._outputs_json(algo, res.outputs))
asyncio.run(main())
```
