---
id: RL-9965
family: ruling
title: RL-1312 corrected — number(x) joins FR-244's allow-list, so a reference-table value can be used in arithmetic
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: fa9a73c2d8b5cfebf4c699961015e6ff8dde1fb1
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1312
relates: [RL-1312, RL-1313, OQ-9964, FR-244, FR-227, FR-69]
---

# RL-9965 — RL-1312 corrected: `number(x)` joins FR-244's allow-list

## How this was ruled

- **The decision this implements.** Ruled at effort `medium`, on the maintainer's scope
  decision "2026-09-30 16:01:23 BST — DECISION (scope): numeric use of reference-table values
  must remain possible in P2; the mechanism goes to the DM as a correction of RL-1312"
  (`~/gi-pricing-plan.local/channel/to-lead.md:14362`). That entry reads: "RL-1312's
  allow-list must **not regress** a working capability". Its steer:
  - "**now:** add **`number(x)`** to the allow-list (deterministic; exact-decimal …; a
    non-numeric string fails at evaluation, closed and coded)";
  - "**later:** typing lookup outputs … is OQ 9964's residual".
- **What this record decides.** The requirement is the maintainer's. **The mechanism, and the
  exact grammar text, are this record's.**
- **Working id 9965.** Assigned by the lead, and minted at the merge turn. At the mint,
  `RL-1312`'s header gains `corrected_by:` with this record's minted id, which is the append
  check 34 allows.
- **The open question.** This record also **raises `OQ-9964`** (working id, assigned by the
  lead), narrowed to the steer's residual, typed lookup outputs. Its two mirror rows are this
  record's disposition. A spec edit is never made without a ruling record naming it
  (`.claude/roles/decision-maker.md`, *Tools*).

## Verified first, at fa9a73c2d8b5cfebf4c699961015e6ff8dde1fb1

| Premise | Where | Present? | What the source says |
|---|---|---|---|
| A lookup's output is a string | `packages/pricing-core/src/pricing_core/rating/runtime.py:239-240` | present | `"o0": json.dumps(str(row.get("payload", {}).get(output_name, "")))` |
| A table's output is a number | `runtime.py:230` | present | `"o0": str(row[value_column])`, unquoted |
| `RL-1312`'s functions | `RL-1312`, Ruled item 1, and its amended FR-244 text | present | `min([…])`, `max([…])` and `abs` only. Literals: numbers, `true`, `false`, `null` and single-quoted strings. So a lookup value can be compared but not used in arithmetic |
| Why `RL-1312` missed it | `RL-1312`, "The sweep" (at `48792023`) | present | It found no function in any committed or stored expression. `number(` arrived later, in `packages/pricing-core/tests/test_rating_pin_membership.py:38` and `:232`, from `2118679b` (#988, `git log -S'number(expense_factor'`) |
| The executor's interim | SL-1315's head `6bcf73e5` (not pushed; in the shared object store) | present | `test_rating_pin_membership.py`, 9+/5−: the `number(` expressions were rewritten as tier comparisons |
| The evaluation-failure code | `RL-1313` DP-G4 | present, not yet built | `RATING_EVALUATION_FAILED`, which the same code slice (SL-1315) adds spec first to `03` §5.1 and to `RATING_ERROR_CODES` |
| FR-227 on lookups | `03` FR-227; `packages/model-schema/src/model_schema/rating.py:275-288` | **absent** | "Every step declares its result type", but neither `RatingLookupStep` (`:275-280`) nor `RatingTableStep` (`:283-288`) has a `result_type`; only `RatingExpressionStep` does (`:294`). Reference-table payload columns are declared by name only (`01` FR-69; `model_schema/reference.py:43`, `:79`). This is `OQ-9964` |

**Probe of the locked engine.** Scratch `probe_number.py` (sha256 prefix `d016a20ed0771296`),
using `zen-engine==0.53.0`, the `uv.lock:2786-2787` pin, installed in a scratch venv and run
through `zen.evaluate_expression`:

| Expression | Context | Result |
|---|---|---|
| `number(a) + number(c) == 0.3` | `a = "0.1"`, `c = "0.2"` | `True`: exact decimal inside the engine |
| `number(a) * 100` | `a = "1.07"` | `107.0` |
| `number(a)` | `a = "abc"`, `""` or `"1,07"` | raises `vmError`, "Function `number` failed: Invalid number" |
| `number(a)` | `a = null` | raises `vmError`, "Cannot convert type null to number" |
| `number(a ?? '1.0') * 2` | `a = null` | `2.0` |
| `number(a)` | `a = " 1.5 "`, `"1e3"`, `5` or `true` | `1.5`, `1000.0`, `5.0`, `1.0` |
| `zen.compile_expression("number(a)")` | | compiles |

A failure is **loud**: a raise at evaluation, never a silent `null` or `0`.

## Ruled

1. **`number(x)` is on FR-244's allow-list, with exactly one argument.** It is added to
   `RL-1312`'s function list. Everything else in `RL-1312` stands.
2. **Its semantics, as the amended FR-244 states them:**
   - **What it accepts:** a numeric string, including whitespace-padded (`" 1.5 "`) and
     exponent (`"1e3"`) forms; a number, which it returns unchanged; and a boolean, as the
     engine converts it (`true` → `1`, `false` → `0`). The result is an exact decimal
     **inside the engine** (`RL-1312`'s boundary rule, "exact decimal inside ZEN"). ZEN
     returns a Python float **at the boundary**, and `RL-1312`'s boundary rule already covers
     that: outputs are taken through `_round_minor` (`Decimal(repr(x))`, quantized with the
     output step's declared mode). `number()` adds no float step of its own (`CLAUDE.md` §7)
     *(F2 of auditor-933's audit at `c96cf32e`: this said "never introduces a float on the
     rating path", which overstated the boundary)*.
   - It exists for `lookup` outputs, which are always strings.
   - **What fails the quote** with `RATING_EVALUATION_FAILED`: any other string (`"abc"`,
     `""`, `"1,07"`), and null. These are the probe's rows. *(F1: this said "a value that is
     not a number … fails", which overclaimed. The engine accepts booleans, numbers and
     padded or exponent strings.)*
   - **Booleans are accepted, and documented, not refused.** `number(b)` for a boolean `b`
     equals `b ? 1 : 0`, which `RL-1312`'s allow-list already admits, so it opens no new
     capability and hides no value. Refusing a boolean argument at save would need type
     inference over ZEN expressions, which `RL-1312` found the codebase does not have
     (FR-213's input types are known, but an argument is an arbitrary sub-expression). At
     evaluation the engine offers no hook to refuse it. A reviewer reads `number(flag)` as
     0 or 1, and the FR-244 text says so.
3. **The error is `RATING_EVALUATION_FAILED`, `RL-1313`'s code, not a new one.**
   - A `number()` failure is exactly "the engine failed evaluating an authored rating string",
     which is that code's meaning.
   - The same code slice registers it, spec first. **If that registration is not in the slice
     when `number` is added, `number` is not added either.** The two land together.
   - **Attribution.** `RL-1313`'s accepted residual (the maintainer's 11:07:11 BST entry)
     applies here too. A `number()` failure in a step that *directly* consumes an
     `on_miss="error"` lookup output is reported as `REFERENCE_LOOKUP_MISS`. The quote still
     refuses, so this is a misdiagnosis, never a price. Moving the failure to compile time is
     `OQ-9964`'s option (b).
4. **The exact FR-244 text.** In `RL-1312`'s amended FR-244 sentence, the one the code slice
   writes, replace
   > **Functions:** `min([…])`, `max([…])` and `abs`.

   with
   > **Functions:** `min([…])`, `max([…])`, `abs` and `number(x)`. `number(x)` exists because
   > a `lookup` step's output is always a string. It converts a numeric string (surrounding
   > spaces and exponent form such as `1e3` are accepted) to an exact decimal inside the
   > engine, returns a number unchanged, and converts a boolean to `1` or `0`. Any other
   > string (for example `abc`, an empty string, or `1,07`) and null fail the quote with
   > `RATING_EVALUATION_FAILED`. Write `number(v ?? '1.0')` to default a missing value
   > (`RL-9965`, correcting `RL-1312`).

   The rest of `RL-1312`'s sentence is unchanged.
5. **Why not the alternatives now.**
   - Typed lookup outputs is the cleaner design, but it needs a `model-schema` field, contract
     regeneration and a runtime branch. That is not P2 scope, per the maintainer's steer,
     and it is `OQ-9964` (below).
   - Compare-only would regress a working capability, which the maintainer has ruled out.
6. **`OQ-9964` is raised as the residual:** whether a lookup's output should be typed from its
   reference table's declared column type. The options are (a) typed outputs, (b) a
   compile-time payload check, and (c) `number()` only. The recommendation is (a), post-P2,
   with (c) meanwhile. The owner is WK-1178. It is mirrored in `docs/open-questions.md` (RATE)
   and `03` §10.

**Narrowness: narrow.**
- One function joins a list, in text the code slice already writes.
- No new code: it reuses `RL-1313`'s.
- No schema, contract or route changes.

## What it obliges

- **This commit:** this record and `OQ-9964`'s two mirror rows.
- **The mint turn:** `RL-1312`'s header gains `corrected_by: [<this record's minted id>]`.
- **The WK-1178 code slice (SL-1315, executor-1178fix), before its slice audit:**
  - `number` joins the tokenizer's function data, with exactly one argument;
  - the FR-244 text above is written, spec first;
  - `RATING_EVALUATION_FAILED` lands in the same slice;
  - the `number(expense_factor ?? "1.0")`-style tests are **kept or restored as real
    arithmetic cases**, not only as tier comparisons (the maintainer's 16:01:23 entry).
- **The lead:** places `OQ-9964` on a gate row. Roadmap §10 is the lead's file.

## Acceptance — the violation that must become detectable

Each is red first in the slice.
- *Violation: `number(x)` is refused at save.*
- *Violation: `number(x, y)`, or `number` with no argument, is accepted.*
- *Violation: a lookup output used through `number()` in arithmetic does not price as the
  exact-decimal product.* For example, `base_minor * number(veh_loading ?? "1.0")`.
- *Violation: a non-numeric lookup value ("abc", "", "1,07") or null under `number()` produces a price, or
  escapes `score_one` as a bare `RuntimeError`, rather than a coded refusal.*
- *Violation: the tokenizer's function list differs from FR-244's text* (`RL-1313`'s equality
  test, with `number` included).
