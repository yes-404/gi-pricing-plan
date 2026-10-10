---
id: RL-1596
family: ruling
title: RL-1519 corrected — the 03 §4.1 worked example's Peril Structure model_call declares one produced name; the per-peril output and its output step leave the example
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: decision-maker
tree: fe0b0627590307259ec6d56be7f73115cf245092
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1519
relates: [RL-1519, RL-1459, FR-212, FR-249, OQ-1460, FD-1595, FD-1374, WK-1178]
---

# RL-1596 — RL-1519 corrected: the `03` §4.1 worked example's `s_rp` declares one produced name

*Disclosure: drafted under working id 9954, reserved by the lead (team-lead) on 2026-10-10;
minted as RL-1596 on 2026-10-10, in the D8b batch mint PR. `FD-1595` is minted in the same
batch from working id 9953 (drafted on `origin/draft/fd-9953-example` at
`037f98498dd101f862dd15681ca3ebbdf2cf22bd`). The working ids in this record, in `RL-1519`'s
header and in `relates:` are replaced by the minted ids; the 03 §4.1 change this record
rules is applied in the same batch (see the batch PR).*

## Ruled

- **The decision is not this record's.** It is the maintainer's (by delegation), in the entry
  of `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-10 14:43:15 BST — RULING: 03
  §4.1 worked example vs A-3's compile. The SPEC EXAMPLE is wrong; (B) with the test pinning
  the RULE; the correcting RL rides the NEXT docs batch" (`to-lead.md:21379`). This record
  records it and decides nothing beyond it.
- **The code is right; `RL-1519`'s worked example is wrong** (`CLAUDE.md` §0). `RL-1459`
  DP-A3-1 (c) and `03` FR-249's *Carried 2026-10-10* note bind: a Peril Structure
  `model_call` produces one name in P2. `RL-1519`'s T2 gives the step `s_rp` two.
- **Scope: the worked example only.** This record corrects T2 (the example's JSON) and the
  one clause of the *What changed* table that justifies the removed output step. Every other
  ruled text of `RL-1519` stands, T3 included (see *What is not changed*).
- **`RL-1519` has a second correcting record, already on `main`: `RL-1593`.** It corrects a
  different text of `RL-1519` (`:284`'s `s_area` `as_at` clause and Acceptance case 3,
  `:657-658`: only `as_at == "effective_date"`, the quote's stamped date, is exempt from
  FR-246's declared-reads rule). The two corrections touch disjoint lines, so neither
  displaces the other; `corrects: RL-1519` stays on this record. With both, `RL-1519`'s
  header reads `corrected_by: [RL-1593, <this record's minted id>]`, in that order (the
  order the two merged in).
- **In the same commit, `RL-1519`'s header gains `corrected_by: [RL-1596]`**, the append
  check 34 allows (`docs/process/document-ids.md` §1, the `corrected_by:` / `corrects:` lines
  of the front-matter block). Not one byte of `RL-1519`'s body changes.
- **This discharges `FD-1595`** (working id), item 3 of the entry: "ONE FD (owner WK-1178,
  LOW: example text, no behaviour), remedy (A)". The record is the remedy (A) it names; the
  finding is discharged when this record is minted and the `03` change below is applied.

## The maintainer's entry, verbatim

"2026-10-10 14:43:15 BST — RULING: 03 §4.1 worked example vs A-3's compile …", in full:

```text
CLAUDE.md §0: decide which side is wrong. The CODE is right. RL-1459 DP-A3-1 (c) (a Peril Structure model_call produces ONE name in P2) and FR-249's Carried note bind; RL-1519's worked example (s_rp producing two names) contradicts them, an illustrative text written before A-3. No wrong behaviour ships, so the fix is the text.
(B) ADOPTED, with one change to the test's framing:
1. The FD-1374 slice leaves 03 §4.1 byte-for-byte as RL-1519 ruled (its Acceptance 4 holds).
2. The slice's test pins the RULE, not "the spec is refused": a Peril Structure model_call producing two names is refused with the named code, and the one-name form compiles. The test's docstring cites 03 §4.1's example by line as known-wrong text pending the correction (FD below), so a reader does not take the example as valid.
3. ONE FD (owner WK-1178, LOW: example text, no behaviour), remedy (A): a correcting RL (corrects: RL-1519, the worked example only; RL-1519 gains corrected_by:, front matter only) re-states the example with one produced name, citing RL-1459 DP-A3-1 (c) and FR-249. It rides the NEXT docs batch (D8), which merges AFTER the FD-1374 slice so Acceptance 4's byte check is not disturbed. When it lands, the slice test's docstring note is updated in the next slice touching that test file (backlog row), or left as a dated reading.
4. No other 03 example may contradict DP-A3-1 (c): the auditor greps 03 for model_call examples producing more than one name and lists any other hits in the same FD.
```

## What binds — read at `fe0b0627`

| What | Where | Verbatim |
|---|---|---|
| The rule | `docs/rulings/RL-01459-wk-1178-a-3-and-a-4-decision-points-one-produced-name-a-compile-refusal-for-separate-model-the-c4-note-and-a-0-05-tolerance.md:132-135` | "**DP-A3-1: (c).** A `model_call` on a Peril Structure declares exactly one produced name, which receives the structure's risk premium. A step that declares more is refused at compile with `BUNDLE_COMPILE_FAILED` (`03`-owned, 422), and the message names the step and the extra names." |
| FR-249's note | `docs/specs/03-rating-engine.md:158` | "*(Carried 2026-10-10, `RL-1459`: a Peril Structure `model_call` yields one produced name in P2. Per-peril components are `OQ-1460`'s, owner WK-1178, …)*" |
| The code | `packages/pricing-core/src/pricing_core/rating/compile.py:850-867`, `_refuse_peril_model_calls`, called at `:976` | `if len(names) > 1: _raise_named("BUNDLE_COMPILE_FAILED", …)` |

## The `RL-1519` text this corrects — read at `fe0b0627`

`RL-1519` is `docs/rulings/RL-01519-pl-9776-dp-f35-1-2-3-decided-a-trace-step-records-what-its-step-reads-and-declares-fr-246-binds-every-evaluating-step-input-and-output-steps-are-traced-nfr-500-reads-the-trace-contract.md`.

| `RL-1519` line | Verbatim | Read now as |
|---|---|---|
| :322 (T2, `outputs`) | `{"name": "peril_risk_premium", "type": "map<string, money_minor>", "required": false}` | Removed. The line before it (`:321`, `ipt_and_fees_minor`) loses its trailing comma. |
| :351 (T2, step `s_rp`, `:347-351`) | `"produces": ["risk_premium_minor", "peril_risk_premium"]},` | `"produces": ["risk_premium_minor"]},` |
| :381-383 (T2, step `s_out_peril`) | `{"step_id": "s_out_peril", "type": "output", "label": "Per-peril risk premium",` … `"consumes": "peril_risk_premium"}` | Removed, all three lines. `s_out` (`:378-380`) becomes the last step; its line `:380` loses its trailing comma. |
| :281 (*What changed* table, the FR-214 row) | "`peril_risk_premium` gets an output step (FR-249)." | "`peril_risk_premium` leaves `outputs`: a Peril Structure `model_call` produces one name in P2 (`RL-1459` DP-A3-1 (c)); per-peril components are `OQ-1460`'s (FR-249's *Carried* note)." Every other sentence of the row stands. |

**Why the output and its output step go with the second name.** Once `s_rp` produces one
name, nothing produces `peril_risk_premium`: `s_out_peril` would consume a name no step
produces (FR-212), and the declared output would have no output step (FR-214). Per-peril
components are `OQ-1460`'s (owner WK-1178), so the example declares none.

**No other change to the example.** Every other line of T2 stands byte for byte: the
`input_contract`, the other four outputs, and every other step, including `s_rp`'s
`consumes`.

## The corrected example, in full

T2 as corrected: 90 lines, sha256 of the text with a final newline
`b1c5dcd7c96a002716236320894226a8cb43c85448cf092b59da013837772596` (T2 as `RL-1519` ruled
it: 94 lines, `6a35964d410f9b6c…`, re-computed here from `:293-386`). The lines that differ
from T2 are `outputs`' last entry, `s_rp`'s `produces`, and the end of `steps`.

````markdown
```json
{
  "slug": "motor-gb",
  "version": 14,
  "input_contract": [
    {"name": "driver_age", "type": "int", "nullable": false, "min": 17, "max": 99,
     "description": "Age of main driver at policy inception"},
    {"name": "postcode_outcode", "type": "string", "nullable": false, "pattern": "^[A-Z]{1,2}[0-9][A-Z0-9]?$",
     "description": "Outward code of the garaging postcode"},
    {"name": "effective_date", "type": "date", "nullable": false,
     "description": "Policy effective date; the area lookup's as-at date (FR-221)"},
    {"name": "distribution_channel", "type": "enum", "nullable": false,
     "domain": ["direct", "aggregator", "broker"],
     "description": "Channel the quote arrived through"},
    {"name": "commission_factor", "type": "decimal", "nullable": false, "min": 1,
     "description": "1 + the channel's commission rate"},
    {"name": "profit_factor", "type": "decimal", "nullable": false, "min": 1,
     "description": "1 + the profit loading"},
    {"name": "min_premium_minor", "type": "int", "nullable": false, "min": 0,
     "description": "Minimum office premium, in pence"},
    {"name": "ipt_factor", "type": "decimal", "nullable": false, "min": 1,
     "description": "1 + the Insurance Premium Tax rate in force at effective_date"}
  ],
  "outputs": [
    {"name": "payable_premium_minor", "type": "money_minor", "required": true},
    {"name": "risk_premium_minor", "type": "money_minor", "required": true},
    {"name": "office_premium_minor", "type": "money_minor", "required": true},
    {"name": "ipt_and_fees_minor", "type": "money_minor", "required": true}
  ],
  "steps": [
    {"step_id": "s_input_age", "type": "input", "label": "Driver age",
     "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
    {"step_id": "s_input_outcode", "type": "input", "label": "Postcode outcode",
     "input_name": "postcode_outcode", "on_missing": "error", "produces": "postcode_outcode"},
    {"step_id": "s_input_effective_date", "type": "input", "label": "Effective date",
     "input_name": "effective_date", "on_missing": "error", "produces": "effective_date"},
    {"step_id": "s_input_channel", "type": "input", "label": "Distribution channel",
     "input_name": "distribution_channel", "on_missing": "error",
     "produces": "distribution_channel"},
    {"step_id": "s_input_commission", "type": "input", "label": "Commission factor",
     "input_name": "commission_factor", "on_missing": "error", "produces": "commission_factor"},
    {"step_id": "s_input_profit", "type": "input", "label": "Profit factor",
     "input_name": "profit_factor", "on_missing": "error", "produces": "profit_factor"},
    {"step_id": "s_input_min_premium", "type": "input", "label": "Minimum premium",
     "input_name": "min_premium_minor", "on_missing": "error", "produces": "min_premium_minor"},
    {"step_id": "s_input_ipt", "type": "input", "label": "IPT factor",
     "input_name": "ipt_factor", "on_missing": "error", "produces": "ipt_factor"},
    {"step_id": "s_area", "type": "lookup", "label": "Rating area from outcode",
     "reference_table_ref": "reference_table:ons-postcode-directory@7",
     "key_expr": ["postcode_outcode"], "as_at": "effective_date",
     "on_miss": "error", "consumes": ["postcode_outcode", "effective_date"],
     "produces": "rating_area"},
    {"step_id": "s_rp", "type": "model_call", "label": "Technical risk premium",
     "peril_structure_ref": "peril_structure:motor-gb-2026h2@2", "mode": "exact",
     "feature_map": {"driver_age": "driver_age", "rating_area": "rating_area"},
     "consumes": ["driver_age", "rating_area"],
     "produces": ["risk_premium_minor"]},
    {"step_id": "s_expense", "type": "table", "label": "Expense loading",
     "rate_table_ref": "rate_table:motor-expense@3", "key_expr": ["distribution_channel"],
     "on_miss": "default", "consumes": ["distribution_channel"], "produces": "expense_factor"},
    {"step_id": "s_office", "type": "expression", "label": "Office premium",
     "expr": "risk_premium_minor * expense_factor * commission_factor * profit_factor",
     "result_type": "money_minor",
     "consumes": ["risk_premium_minor", "expense_factor", "commission_factor", "profit_factor"],
     "produces": "office_premium_minor"},
    {"step_id": "s_minprem", "type": "constraint", "label": "Minimum premium",
     "condition": "office_premium_minor >= min_premium_minor",
     "on_violation": "clamp", "clamp_bounds": {"min": "min_premium_minor"},
     "reason_code": "MIN_PREMIUM_APPLIED",
     "consumes": ["office_premium_minor", "min_premium_minor"],
     "produces": "office_premium_minor"},
    {"step_id": "s_ipt", "type": "expression", "label": "Insurance Premium Tax",
     "expr": "office_premium_minor * ipt_factor", "result_type": "money_minor",
     "consumes": ["office_premium_minor", "ipt_factor"], "produces": "payable_premium_pre_round"},
    {"step_id": "s_out_risk", "type": "output", "label": "Risk premium (ladder)",
     "output_name": "risk_premium_minor",
     "rounding": {"mode": "half_even", "dp": 0}, "consumes": "risk_premium_minor"},
    {"step_id": "s_out_office", "type": "output", "label": "Office premium (ladder)",
     "output_name": "office_premium_minor",
     "rounding": {"mode": "half_even", "dp": 0}, "consumes": "office_premium_minor"},
    {"step_id": "s_out_ipt", "type": "output", "label": "IPT and fees (ladder)",
     "output_name": "ipt_and_fees_minor",
     "rounding": {"mode": "half_even", "dp": 0}, "consumes": "payable_premium_pre_round"},
    {"step_id": "s_out", "type": "output", "label": "Payable premium",
     "output_name": "payable_premium_minor",
     "rounding": {"mode": "half_even", "dp": 0}, "consumes": "payable_premium_pre_round"}
  ],
  "sub_graphs": []
}
```
````

The text inside the ```` ```json ```` fence parses as JSON (`json.loads`, run on this text
before filing). It is the same example the FD-1374 slice's `_one_name_example()` builds from
T2 at `origin/sl-1536-fd1374-dp-f35-1` `0e7c4d5cfe52ec4b4e62e3bbefb33b0485d33860`
(`packages/pricing-core/tests/test_rating_declared_reads.py:141-149`): `s_rp` reduced to
`["risk_premium_minor"]`, `s_out_peril` and the `peril_risk_premium` output removed. Its
compile is that branch's test
`test_the_one_name_form_of_the_03_example_compiles_with_its_reads_declared` (`:166-171`);
this record ran no test and does not assert that test's result.

## What is not changed

- **`RL-1519`'s body.** It is frozen. The corrections above are read through this record.
- **T3** (`RL-1519:394-405`, the *Invariants* paragraph). Its last sentence records what the
  pre-T2 example got wrong ("declared three outputs no step produced"), which stays true of
  that example. Nothing in T3 names `peril_risk_premium` or `s_rp`.
- **`RL-1519` Acceptance 4 and the FD-1374 slice.** That slice carries T2 into `03` §4.1
  byte for byte as `RL-1519` ruled it (the entry, item 1). This record does not touch that
  slice or its byte check.
- **The evidence `RL-1519` recorded on T2** — the checks' output at `:442` and `:452`, and
  the observation at `:706-709` naming "T2's `peril_risk_premium` map". Each is a dated
  reading of T2 as it was ruled, not a statement of the example; each stays.
- **Line locators and the sha256 at `RL-1519:289-291`.** They name T2 as ruled, which the
  FD-1374 slice applies; the corrected text's own are above.

## Acceptance — how the `03` change is applied, and the check

The violation: a `model_call` example in `docs/specs/` declares more than one produced name.

1. **Applied in the docs batch D8, which merges after the FD-1374 slice** (the entry, item
   3). D8 replaces `03` §4.1's ```` ```json ```` fence, then T2 as the slice carried it, with
   the corrected example above, and adds a dated note citing this record after the fence,
   in the house form: *(Corrected {DATE}, `RL-1596` (`FD-1595`): `s_rp`, a Peril Structure
   `model_call`, declared two produced names, which `RL-1459` DP-A3-1 (c) refuses; it
   declares one, and the per-peril output `peril_risk_premium` and its output step
   `s_out_peril` are removed until `OQ-1460` is decided (FR-249).)* `03` is not edited by
   this record's PR.
2. **The FD-1374 slice test's docstring note** (the known-wrong reading of `03` §4.1) is
   updated by the next slice that touches
   `packages/pricing-core/tests/test_rating_declared_reads.py` (a backlog row), or is left
   as a dated reading (the entry, item 3). But see the first item of *For the lead* below:
   at the slice's head the test body, not only its docstring, reads the example.
3. **The check.** After D8, run at the tree D8 merges:
   `git grep -nP '"produces"\s*:\s*\[[^\]]*,[^\]]*\]' -- docs/specs` → **no `model_call`
   hit** (exit 1, no output, unless a hit is a non-`model_call` step, which is then listed).
   Baseline at `fe0b0627`: one hit, `docs/specs/03-rating-engine.md:270`,
   `"produces": ["risk_premium_minor", "peril_risk_premium"]},` — the pre-T2 example's
   `s_rp`. The corrected `s_rp` (`["risk_premium_minor"]`, one element, no comma) does not
   match. *Violation: any hit on a `model_call` step.*
4. **The other examples** (the entry, item 4) are `FD-1595`'s *Item 4* section: at
   `fe0b0627` no other two-name `model_call` example is in `docs/specs` or
   `docs/workflows`, outside `RL-1459`'s own quotation (`:94`) and `RL-1519:351`, which this
   record corrects.

## For the lead (observed, not ruled)

- **D8's correction turns a test of the FD-1374 slice red, as that test stands at
  `0e7c4d5c`.** `_spec_example()` (`test_rating_declared_reads.py:89-96` on
  `origin/sl-1536-fd1374-dp-f35-1` at `0e7c4d5cfe52ec4b4e62e3bbefb33b0485d33860`) reads the
  first ```` ```json ```` block after `### 4.1 ` from `docs/specs/03-rating-engine.md` at run
  time. `test_a_peril_structure_model_call_producing_two_names_is_refused_at_compile`
  (`:174-182`) compiles that example and asserts `BUNDLE_COMPILE_FAILED: step 's_rp'`. Once
  D8 puts the one-name example into `03`, that compile succeeds and the `pytest.raises`
  fails. So item 2's "docstring note updated by the next slice" does not cover it: either
  the two-name case is built in the test (for example by adding `peril_risk_premium` back to
  `_spec_example()`'s `s_rp`), in the slice or in D8, or D8 is not docs-only. Which, and
  when, is the lead's; this record does not decide it. Read at that head only; if the slice
  is reworked or squash-merged, re-read before acting.
- **The working-id form in `RL-1519`'s header.** The brief wrote `corrected_by: [RL 9954]`.
  The draft of this record wrote `[RL-9954]`, the form the precedent used and the mint turned into the
  minted id (here `[RL-1593, RL-1596]`, with `RL-1593` already on `main`): `origin/draft/rl-9942-corrects-rl1475` wrote `corrected_by: [RL-9942]` in
  `RL-1475`'s header (commit `634706e3`), minted as `RL-1584`.
