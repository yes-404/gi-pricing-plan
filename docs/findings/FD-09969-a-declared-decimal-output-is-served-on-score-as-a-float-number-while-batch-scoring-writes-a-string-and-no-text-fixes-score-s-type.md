---
id: FD-9969
family: finding
title: A declared decimal output is served on /score as a float JSON number, while batch scoring writes it as a string, and no text or contract fixes /score's type
status: active
created: 2026-09-30
owner: auditor
tree: 8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862
corrected_by: []
relates: [WK-1178, WK-674, FR-273, FR-227, FR-250, FR-248]
---

# FD-9969 — A declared `decimal` output is served on `/score` as a float, and no text fixes its JSON type

**Working id 9969.** Filed as a working id and minted at the records PR; it is cited by number, not as a
token, until then, and by the open question **OQ-9970** it raises (below).

## Finding

**Severity: low** (proposed by the auditor; the disposition is the lead's, and the maintainer's).
`_build_outputs` (`packages/pricing-core/src/pricing_core/rating/score.py:626-646`) serves a declared output that
is **not a ladder rung** from `result[source]` (`:643-645`), which is the engine's value as a Python `float`.
`score_one` converts nothing. So an algorithm that declares an output of type `decimal` gets that output on
`POST /api/v1/score` as a **float**, written by `ScoringResult.model_dump_json()`
(`backend/src/app/api/score.py:321`) as a **JSON number**. The other scoring path, `score_batch`, writes the same
declared output as a **JSON string** (`_coerce_output_value`, `score.py:834-866`, whose docstring gives the reason:
"a JSON number column cannot distinguish an exact `Decimal` from a lossy `float`"). One field, `ScoringResult.outputs`,
so has **two JSON types** for one declared output type, depending on which endpoint served it. `03`
states the string rule for the batch column only (`03:624`); it and the contracts say nothing about the `/score`
type (evidence 1 and 2).

**It is a contract question before it is a defect.** The maintainer's rule is in `to-lead.md`, the entry headed
"2026-09-30 16:58:01 BST — MERGE-ACK #997 (SL-1302, WK-674 S2a, LG-1324) at head d815a82054eceaf77b9ef939524afd7ed821f9e2
on main 32f3fa92afad81d1be611b21ae16ff35211eded8", its bullet "S6 routing", quoted:

> **S6 routing (declared non-money `decimal` outputs served as float by `_build_outputs`):** out of S3, agreed. **Not WK-1178
> by default:** changing a /score field's JSON type is a contract decision, not maintenance. File it as an FD. If 03 or the
> contract already decides the type (e.g. FR-273 or the output-type table says string), the served float is a defect: owner
> **WK-1178**, contract first. If 03 is silent, the FD raises an OQ with options and a recommendation, and the owner is decided
> when the OQ is ruled. The FD quotes the 03 text it relied on.

Applied below (evidence 6): **`03` does not decide the `/score` type, and the contract does not fix it, so this record
raises OQ-9970**; it does not assign an owner. The two texts that could have decided it, FR-273 and the batch
column's `:624`, are set out with their scope so the maintainer can see the reading.

**Why it matters, and why only low.** A `decimal` output can carry money (FR-227: "A monetary result must be `decimal`
or `money_minor`"), and `CLAUDE.md` §7 says money is never float. As a float the value can lose digits (evidence 4:
`1234567.1234567890123456` reaches the wire as `1234567.123456789`), and a client cannot tell an exact decimal from a
float. But **no committed algorithm declares a `decimal` output** (evidence 5: one committed fixture, a batch test),
and there is no production. It is latent until the first algorithm that does.

## Evidence

Every measurement is at `origin/main` `8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862` (2026-09-30, 17:05 BST), in a scratch
`git worktree add`, reverted afterwards. `git status --short` printed nothing.

**1. What `03` says, verbatim** (`docs/specs/03-rating-engine.md`, lines at that tree).

- `:45-46`, R2: "**R2 — Money is integer minor units or `Decimal` throughout** (FR-10). The engine refuses to construct a
  rating step whose output is a float-typed monetary value."
- `:83`, FR-214: "The algorithm declares typed **outputs**, always including `payable_premium_minor` and the full Premium
  Ladder (§3.6), and may include additional named outputs (per-peril risk premium, decline reason, IPT amount)."
- `:113`, FR-227: "Every step declares its result type, and type compatibility is checked at save time. A monetary result
  must be `decimal` or `money_minor` (R2)."
- `:162`, FR-250: "**Real-time scoring**: `POST /api/v1/score` evaluates one Quote Context against the Rating Version
  currently live in the target environment, returning the ladder, outputs, and (optionally) a Trace."
- `:222`, FR-273 (first two sentences and the rule): "**Money crosses the engine boundary only as integer minor units.**
  The binding accepts no decimal type and returns `float`, so exactness cannot survive the crossing as a fractional
  value. … any value returning to Python for further arithmetic is an integer minor unit or a string."
- `:245-249` and `:445`, §4.1 and §4.4's examples: the declared outputs are `payable_premium_minor` (`money_minor`),
  `premium_ladder` (`ladder`), `peril_risk_premium` (`map<string, money_minor>`) and `decline_reasons`
  (`array<string>`); the served `outputs` object is `{"payable_premium_minor": 36_120, "peril_risk_premium": {"AD": 9_820,
  "…": "…"}}`. **No example declares or serves a `decimal` output.**
- `:624`, the batch output column: "`outputs_json` | string, nullable | `outputs` | pre-serialised to JSON text, total
  over every `AlgorithmOutput.type` this path can produce (`money_minor` as a JSON number, `decimal` as a JSON string —
  never a JSON number, so an exact `Decimal` and a lossy `float` cannot be confused reading the column back) and
  refusing, not stringifying, anything else; `null` on an `"error"` row". It is the one place `03` types a `decimal`
  output's JSON form, and its own words scope it to "this path", the batch path (FR-253, `:165`).
- `RL-923` §5(i) (`docs/rulings/RL-00923-*.md:116-131`) ruled the batch column's serialisation "total over the value types
  the rating path can produce" and refusing a type it does not name; it did not address `/score`.
- `CLAUDE.md` §7 (`:143`): "Money is integer pence/cents, or Decimal in the rating path — never float."

**2. What the contracts say, verbatim, with full paths.**

- `docs/contracts/schemas/scoring.schema.json:54`, `$defs.ScoringResult.properties.outputs` is `{"type": "object"}`: the
  values are untyped. (Authored file; the schema's `$defs` are `QuoteContext`, `LadderRung`, `ScoringResult`, `Trace`.)
- `docs/contracts/schemas/generated/score-comparison.schema.json`, `$defs.ScoringResult.properties.outputs` is
  `{"additionalProperties": true, "title": "Outputs", "type": "object"}`: also untyped (generated from
  `packages/model-schema/src/model_schema/scoring.py:186`, `outputs: dict[str, object]`).
- `docs/contracts/openapi/generated.json`, `paths["/api/v1/score"].post.responses["200"]` is
  `{"content": {"application/json": {"schema": {}}}, "description": "Successful Response"}`: **no response schema at all**
  (the route returns a raw `Response`, `score.py:321`), and `components.schemas` has no `ScoringResult`.
- `docs/contracts/schemas/rating-algorithm.schema.json`, `properties.outputs.items.properties.type` is `{"type":
  "string"}`: a declared output's `type` is any string, refused only if it contains `float`
  (`packages/model-schema/src/model_schema/rating.py:220-235`, `_reject_float_type`).

**3. The code path** (all at the tree above). `_build_outputs` (`score.py:626-646`): a rung-named output reuses the
ladder's value (`:641`), any other declared output is `outputs[declared.name] = result[str(source[0])]` (`:645`), the engine's
raw value. `score_one` does not convert it. `/score` returns `result.model_dump_json()` (`backend/src/app/api/score.py:321`).
`score_batch` runs the same `outputs` through `_outputs_json` (`score.py:875`) and `_coerce_output_value`
(`:834`), whose known types are `money_minor`, `decimal`, `bool`, `string`, `date` (`_KNOWN_OUTPUT_TYPES`, `:831`),
converting a `decimal` by `Decimal(repr(value))` and writing `str(...)`. **That string is the float's shortest repr,
not the engine's exact value**, so the batch string is a different type but not more exact (evidence 4). The decision
`RL 9963` (local branch `dm-eh-s3`, head `a8fef919`, not on `main`; "Declared money outputs that are not rungs", and its
*Observed* list) brings `money_minor` non-rung outputs into WK-674 Slice 3 (served as an exact integer) and rules
`decimal` outputs out: "They are not money, and serving them as exact strings would change their JSON type on `/score`
from number to string. No acceptance covers that visible change." It recommends WK-1178 and the lead routes it. Note
that FR-227 above lets a `decimal` output carry money, so "not money" is a reading, not the spec's text.

**4. Reproduction on the real score path** (`decimal_output_repro.py`, kept in full below; run from the repo root at the
tree above with `PYTHONPATH=packages/pricing-core/src:packages/model-schema/src:packages/pricing-core/tests` under
`uv run --no-sync python`). It reuses `test_rating_score.py`'s fixture algorithm and, **in memory only**, adds two declared
outputs of type `decimal` (not ladder rungs) with the expression steps that feed them; it scores through the real
`score_one`, then serialises the same outputs the way `/score` does (`ScoringResult.model_dump_json`) and the way the
batch path does (`_outputs_json`). Output, verbatim:

```text
declared type: decimal;  score_one(...).outputs['loading_ratio'] = 3.3 | python type: float
exact binary value of that float : 3.29999999999999982236431605997495353221893310546875
the value the engine meant (3.3) : 3.3 | float == meant? False
/score wire form (ScoringResult.model_dump_json) outputs: {"payable_premium_minor": 1507, "loading_ratio": 3.3, "wide_ratio": 1234567.123456789}
wide_ratio: engine-side value 1234567.1234567890123456 -> /score outputs value 1234567.123456789 float | exact binary 1234567.12345678894780576229095458984375
batch serialiser sm._outputs_json (same outputs, same algorithm): {"payable_premium_minor": 1507, "loading_ratio": "3.3", "wide_ratio": "1234567.123456789"}
  float 0.1+0.2  repr=0.30000000000000004    exact=0.3000000000000000444089209850062616169452667236328125
  float 1.1*3    repr=3.3000000000000003     exact=3.300000000000000266453525910037569701671600341796875
  float 4308.9   repr=4308.9                 exact=4308.899999999999636202119290828704833984375
```

What it shows. (a) The value crosses as a Python `float`, and **`3.3` has no exact binary form** (the float's exact value
is `3.29999999999999982…`). (b) `/score` writes it as the JSON **number** `3.3`; the batch path writes the same value as the
JSON **string** `"3.3"`. (c) A 22-significant-digit engine value, `1234567.1234567890123456`, loses everything past the
sixteenth digit on `/score` (`1234567.123456789`), **and on the batch path too**, because its string is `Decimal(repr(float))`.
The type differs; the exactness does not. The route returns exactly `ScoringResult.model_dump_json()` (`score.py:321`),
so the wire form above is the HTTP body's `outputs` object. Not run through HTTP: the algorithm above is a scratch
fixture, and driving the route needs a stored Rating Version with its bundle; the code between the two is one line.

```python
"""FD-9969 reproduction: a declared non-rung `decimal` output on the real /score path (score_one) and on the batch path's serialiser.
Run from the repo root:  PYTHONPATH=packages/pricing-core/src:packages/model-schema/src:packages/pricing-core/tests uv run --no-sync python decimal_output_repro.py"""
import asyncio, json, sys
from decimal import Decimal
sys.path.insert(0, "packages/pricing-core/tests")
import test_rating_score as T
from pricing_core.rating import score as sm

_orig = T._algorithm_payload
def patched(**kw):
    p = _orig(**kw)
    p["outputs"] = p["outputs"] + [{"name": "loading_ratio", "type": "decimal", "required": False},
                                   {"name": "wide_ratio", "type": "decimal", "required": False}]
    p["steps"] = p["steps"] + [
        {"step_id": "s_ratio", "type": "expression", "label": "A fractional loading", "expr": "1.1 * 3 + 0 * risk_premium_minor",
         "result_type": "decimal", "consumes": ["risk_premium_minor"], "produces": "loading_ratio_value"},
        {"step_id": "s_out_ratio", "type": "output", "label": "Loading ratio (not a ladder rung)", "output_name": "loading_ratio",
         "rounding": {"mode": "half_even", "dp": 4}, "consumes": ["loading_ratio_value"]},
        {"step_id": "s_wide", "type": "expression", "label": "A 22-significant-digit fractional value", "expr": "1234567.1234567890123456 + 0 * risk_premium_minor",
         "result_type": "decimal", "consumes": ["risk_premium_minor"], "produces": "wide_ratio_value"},
        {"step_id": "s_out_wide", "type": "output", "label": "Wide ratio (not a ladder rung)", "output_name": "wide_ratio",
         "rounding": {"mode": "half_even", "dp": 10}, "consumes": ["wide_ratio_value"]},
    ]
    return p
T._algorithm_payload = patched

async def main():
    compiled = await T._compiled()
    res = await sm.score_one(compiled, T._ctx())
    v = res.outputs["loading_ratio"]
    print("declared type: decimal;  score_one(...).outputs['loading_ratio'] =", repr(v), "| python type:", type(v).__name__)
    print("exact binary value of that float :", Decimal(v))
    print("the value the engine meant (3.3) :", Decimal("3.3"), "| float == meant?", Decimal(v) == Decimal("3.3"))
    print("/score wire form (ScoringResult.model_dump_json) outputs:", json.dumps(json.loads(res.model_dump_json())["outputs"]))
    w = res.outputs["wide_ratio"]
    print("wide_ratio: engine-side value 1234567.1234567890123456 -> /score outputs value", repr(w), type(w).__name__, "| exact binary", Decimal(w))
    algo = compiled.bundle.algorithm if hasattr(compiled, "bundle") else compiled.algorithm
    print("batch serialiser sm._outputs_json (same outputs, same algorithm):", sm._outputs_json(algo, res.outputs))
    # a value with no exact binary form that also changes a digit on the string route
    for label, val in (("0.1+0.2", 0.1 + 0.2), ("1.1*3", 1.1 * 3), ("4308.9", 4308.9)):
        print(f"  float {label:8} repr={val!r:22} exact={Decimal(val)}")
asyncio.run(main())
```

**5. How many committed algorithms and fixtures declare a `decimal` output.** *Corpus:* every tracked file at the tree
(`git ls-files`, 1909 files). *Predicate,* verbatim in `count_decimal_outputs.py` below: a Python dict literal with keys
`name`, `type` and `required` all present, `nullable` absent (an input carries `nullable`), and `type == "decimal"` (P1); a
call `AlgorithmOutput(..., type="decimal")` (P2); a `.json`/`.jsonl` file holding, at any depth, an `outputs` list with an
object whose `type == "decimal"` (P3). *Result:* **1 declaration**, `packages/pricing-core/tests/test_rating_score_batch.py:84`
(`payload["outputs"].append({"name": "age_factor", "type": "decimal", "required": False})`, added for RL-923 §5(i)'s
byte-identity test of the batch column); **0** AlgorithmOutput calls; **0** JSON files. *So no committed algorithm, seed or example declares a `decimal` output. The one fixture is scored by `score_batch`, and
also by `score_one` in the same test, but that test asserts only `score_one`'s ladder and `payable_premium_minor`
(`test_rating_score_batch.py:158-190`); **the `decimal` output's value and type as `score_one` returns it, and as `/score`
serves it, are asserted nowhere.** *Positive control:* the first form of the predicate, which looked only
for a dict under an `outputs` key, counted **0** and missed that fixture (`.append({…})` has no `outputs` key on the dict), which a
plain `git grep '"decimal"'` had shown; it was replaced by the shape form above, which finds the fixture, and a planted
file `X = {"name": "r", "type": "decimal", "required": False}` was counted (2, then removed; 0 planted files remain). *Limits:*
committed files only; algorithms stored in a database or blob store are **not** counted, since a stored algorithm is
authored by a user and none is committed. (No multi-database sweep was run for this filing.)

```python
r"""FD-9969: committed algorithms and fixtures that DECLARE an output of type `decimal`.
Corpus: every tracked file at the tree (git ls-files). Predicate, verbatim (revised after the positive control found
the first form missed `payload["outputs"].append({...})`):
  (P1) a .py file containing ANY dict literal shaped like an output declaration: keys "name", "type" and "required"
       all present, "nullable" absent (inputs carry `nullable`), and "type" == "decimal";
  (P2) a call AlgorithmOutput(..., type="decimal", ...);
  (P3) a .json/.jsonl file whose parsed value contains, at any depth, an "outputs" list holding an object with "type" == "decimal";
  (P4) a .md/.yaml/.yml file: reported separately as TEXT mentions (fenced examples), a line matching  "type"\s*:\s*"decimal"  within an "outputs" fenced block.
Only P1-P3 count as declarations; P4 is listed for context."""
import ast, json, re, subprocess, sys
files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
p1, p2, p3, p4 = [], [], [], []
def const(n): return n.value if isinstance(n, ast.Constant) else None
for f in files:
    try:
        if f.endswith(".py"):
            tree = ast.parse(open(f, encoding="utf-8").read())
            for n in ast.walk(tree):
                if isinstance(n, ast.Dict):
                    keys = {const(k): const(v) for k, v in zip(n.keys, n.values)}
                    if {"name", "type", "required"} <= set(keys) and "nullable" not in keys and keys.get("type") == "decimal":
                        p1.append((f, n.lineno))
                if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == "AlgorithmOutput":
                    if any(kw.arg == "type" and const(kw.value) == "decimal" for kw in n.keywords):
                        p2.append((f, n.lineno))
        elif f.endswith((".json", ".jsonl")):
            def walk(o):
                if isinstance(o, dict):
                    if isinstance(o.get("outputs"), list) and any(isinstance(e, dict) and e.get("type") == "decimal" for e in o["outputs"]):
                        return True
                    return any(walk(v) for v in o.values())
                if isinstance(o, list): return any(walk(v) for v in o)
                return False
            txt = open(f, encoding="utf-8").read()
            docs = [json.loads(l) for l in txt.splitlines() if l.strip()] if f.endswith(".jsonl") else [json.loads(txt)]
            if any(walk(d) for d in docs): p3.append((f, 0))
        elif f.endswith((".md", ".yaml", ".yml")):
            txt = open(f, encoding="utf-8").read()
            for m in re.finditer(r'"outputs"\s*:\s*\[(.*?)\]', txt, re.S):
                if re.search(r'"type"\s*:\s*"decimal"', m.group(1)): p4.append((f, txt[:m.start()].count("\n") + 1))
    except (SyntaxError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        pass
print("tracked files:", len(files))
print("P1 python dict payloads declaring a decimal output:", len(p1), p1[:10])
print("P2 AlgorithmOutput(type='decimal') calls:", len(p2), p2[:10])
print("P3 json files declaring a decimal output:", len(p3), p3[:10])
print("P4 md/yaml text mentions (context, not declarations):", len(p4), p4[:6])
print("DECLARATIONS (P1+P2+P3):", len(p1) + len(p2) + len(p3))
```

**6. Which branch of the maintainer's rule applies.** The rule's own examples are "FR-273 or the output-type table". Read
both against this field.

- **FR-273 (`:222`)** governs *money* crossing the engine boundary ("Money crosses the engine boundary only as integer minor
  units"; a value "returning to Python for further arithmetic is an integer minor unit or a string"). A float `decimal`
  output is a value returning to Python, but the requirement's words are "money" and "for further arithmetic", and it
  does not say what a *served* output's JSON type is. Whether a `decimal` output is money is exactly what `RL 9963`
  reads one way ("not money") and FR-227 leaves open ("A monetary result must be `decimal` or `money_minor`").
- **The output-type text (`:624`)** fixes `decimal` → JSON string, and scopes itself to "this path": the batch column
  `outputs_json` (FR-253). For `/score`, `03` says only "returning the ladder, outputs" (FR-250) and shows no `decimal`
  output (`:245-249`, `:445`). The contracts leave the value type open (`{"type": "object"}`), and the OpenAPI operation has no
  response schema (evidence 2).

**`03` is silent on `/score`'s `decimal` output type, and the contract does not fix it, so the OQ branch applies** and this
record raises **OQ-9970**. **The other reading,** stated so the maintainer can flip the branch: if FR-273's "or a string"
is read as governing every fractional value the engine returns, or `:624`'s rule as binding the one field
`ScoringResult.outputs` on every path (both paths serialise that field, and RL-923's reason, "an exact `Decimal` and a lossy
`float` cannot be confused", is not batch-specific), then the type is already decided and this is a defect, owner WK-1178,
contract first. The recommendation below, (a), is the same in both readings.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** The owner is **not** assigned here: on the maintainer's rule it
is set when OQ-9970 is ruled. `carry forward, unowned` until then; the event that assigns it is **OQ-9970's ruling**.

**OQ-9970** (mirrored in `docs/open-questions.md` and `03` §10; its options, with the recommendation):

- **(a) `/score` serves a declared `decimal` output as a JSON string**, as the batch column already does (`03:624`), with the
  contract first: type `ScoringResult.outputs` values in `scoring.schema.json` (and give the `/score` operation a response
  schema in OpenAPI), then change `_build_outputs`. It follows R2, FR-273 and `CLAUDE.md` §7 and makes both paths agree.
  It is a **breaking change** for a client that reads a `decimal` output as a number; no committed algorithm declares one
  (evidence 5), so no in-repo consumer changes. For exactness (not only the type), the string must be the engine's
  exact `string()` value, the terminal read `RL 9963` uses for `money_minor`; `Decimal(repr(float))` is the interim and is
  not exact (evidence 4c).
- **(b) Keep JSON numbers on `/score`,** document the loss, and state in `03` that the two paths differ. It leaves the float
  carrying a value that FR-227 allows to be money, against `CLAUDE.md` §7.
- **(c) Serve a JSON number whose literal is the exact decimal** (a custom serialiser, the engine's `string()` as the
  literal). The JSON type does not change and the digits are exact on the wire; a client that parses to a float still loses
  them, and the reader cannot tell an exact decimal from a float, the confusion `03:624` exists to prevent.
- **(d) Refuse `decimal` as a declared output type in P2** (compile error; it stays valid for inputs and step results),
  until a need is scoped. No committed algorithm uses it (evidence 5), so nothing breaks, and the type question is not
  opened. It is the cheapest interim guard if (a) cannot land first.

**Recommendation: (a), contract first, in WK-1178,** sharing the exact `string()` read with `RL 9963`'s builder rewrite so
that one read supplies rungs, money outputs and decimal outputs; (d) is the interim if (a) is not ready when Slice 3
merges. The choice is the maintainer's: it changes a served JSON type.

**Event that next confirms or discharges it:** OQ-9970 is ruled (by an `RL-`, or an ADR if it must be decided now), which
assigns the owner; it is discharged when that ruling is implemented, contract first, with a red-first case for a declared
`decimal` output through `score_one`/`/score`. **Interaction to record now:** `RL 9963` excludes `decimal` outputs on the
ground that they are "not money"; OQ-9970 should decide whether a `decimal` output may carry money (FR-227), since that
decides whether `CLAUDE.md` §7 binds it.

Ownership shape: event

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it.
