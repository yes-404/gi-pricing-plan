---
id: RL-9498
family: ruling
title: PL 9509 decided — every declared output type has one JSON form on every scoring path; int and count are JSON integers, relativity and percentage take the decimal string form, a mismatched value is that row's error coded by class name (03 outputs_json row, FR-214)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: fb178c360f6fd5b2fdb7ae60eea924811a65492f
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-214, FR-254, FR-255, RL-1343, RL-923, RL-1329, FD-1333]
---

# PL 9509 decided: one JSON form per declared output type, on every scoring path

## How this was ruled

- **Filed under working id 9498, reserved by the lead.** The mint sweep replaces every
  `RL 9498`, `PL 9509`, `SL 9511`, `FD 9513`, `PL 9499` and `SL 9500` below with its minted id.
- **The decisions are not this record's.** They are the maintainer's, by delegation, in two
  entries in `~/gi-pricing-plan.local/channel/to-lead.md`, quoted verbatim below.
- **This record states those decisions as spec text and decides nothing beyond them.** Where
  a text needs a word the entries do not give, the word is from `03` or a ruling at the tree
  above (§"Details taken from main").
- **The finding** is FD 9513 (#1204, head `d78f1235` when read). **The plan whose decision
  points this rules** is PL 9509 (#1210, head `b0659358` when read), which applies T1 by its
  slice SL 9511. **The other applier** is PL 9499 / SL 9500 (working ids; the `RL-1343` slice,
  being drafted), which carries the `/score` half under DP-2 (ii). These heads may move; the
  mint heads govern.
- **Brief:** `brief-dm-9509-2026-10-05.md` (the lead, 2026-10-05).

## The maintainer's entries, quoted verbatim

From `~/gi-pricing-plan.local/channel/to-lead.md` (18 478 lines when read; the file is
append-only).

**Lines 18392-18397, the FD 9513 entry:**

> ## 2026-10-05 17:58:45 BST — FD 9513 (#1204 @0303d0bf): your decision ACCEPTED (MEDIUM, LATENT, WK-1178, its own fix slice after SL 9561); the row escape is the first red
>
> Verified at origin/main (packages/pricing-core/src/pricing_core/rating/score.py): _score_batch_row's try is :1096-1103 (except NotImplementedError; except ValueError or RuntimeError), and "outputs_json": _outputs_json(algorithm, scored.outputs) is at :1123, OUTSIDE it. One bad row can abort the batch, against FR-255. The PR body has 0 session URLs and 0 "deputy" (re-read after the PATCH).
> 1. ACCEPTED: MEDIUM; LATENT; carry forward, owner WK-1178; its OWN fix slice editing score.py AFTER SL 9561. Reserve the SL/PL ids; a planner drafts when a seat frees.
> 2. The fix plan's reds, in order: (1) the ROW ESCAPE first. ANY exception from _outputs_json (or anything else after the try) becomes that row's error row, and the run continues (FR-255). This does not depend on the type question, so it lands even if the type DP is still open. (2) the four types, with the JSON form of count, relativity and percentage as a DP for me in that plan (FR-254's "batch never diverges" is the reading; the plan proposes).
> 3. The decimal half stays with FD-1333 / OQ-1334 / RL-1343, not re-filed. The new fact (a whole-valued decimal reaches /score as a JSON INTEGER, a fractional one as a float; FD-1333/RL-1343 say only "float") goes into FD 9513's text as a related observation, cited to FD-1333. Whichever plan discharges RL-1343's clause must cover BOTH forms; FD 9513's fix plan checks whether that plan exists and names it.
> 4. The shared-tmp overwrite of the PR body: noted; fixed and re-read. That is the a-shared-job-tmp-dir hazard again, so each member writes PR bodies under its own mktemp path.

**Lines 18453-18461, the PL 9509 entry:**

> ## 2026-10-05 18:10:57 BST — PL 9509 (#1210 @dc4f9c50) DPs RULED: DP-1 (b), DP-2 (ii), DP-3 the class name; the RL-1343 leaf plan is reserved NOW
>
> The finding that _ladder_json (:1122) is ALSO outside the try, alongside _outputs_json (:1123): good. Task 1 covers anything after the try.
> DP-1: (b). int and count are a JSON INTEGER on both paths, and a non-integral value under them becomes that ROW's error. relativity and percentage use the DECIMAL STRING form (the RL-1343 rule, and 03:692 keeps lossy floats out). (c) is NOT taken, because OQ 9556 owns the type vocabulary at save; (d) is not taken.
> DP-2: (ii). The RL-1343 slice carries the /score half for relativity and percentage. Until it lands, FD-1333's divergence stands for those two types, and FD 9513's register cell names that residue and its discharger.
> DP-3: the exception class name, as today.
> RL-1343 HAS NO DISCHARGING PLAN, and its gate is met: YES, reserve the SL/PL ids now under WK-1178 and spawn a planner at the next free seat. Its scope: BOTH decimal forms (whole-valued, which today is a JSON integer, with its own red: 27 → "27.00" at dp 2; fractional, today a float), relativity and percentage on /score (DP-2 (ii)), and NFR-502's re-measure in the gate's own mode. It SERIALISES with SL 9511 on _coerce_output_value. As a breaking wire change, it runs the frontend half of the gate.
> Task 1 (the row escape) is dispatchable before the DPs, but it edits score.py, so it still runs AFTER SL 9561 in lane B order.
> Discrepancies: PL 9521 Step 1a citing FD 9513, and PL 9567's write-set table in delta 7: both pre-mint fixes, good.

**Lines 18480-18484, the RL 9498 entry** (added by the pre-mint amendment below; the file had
18 489 lines when read):

> ## 2026-10-05 18:20:06 BST — RL 9498 (#1212 @7e71b040): both open questions RULED as recommended, with one precision each
>
> (1) /score with a NON-INTEGRAL int or count value: REFUSE THAT QUOTE in SL 9500, with an EXISTING per-quote code from 03's owned list, else spec first. PRECISION: the code must be in backend/src/app/api/score.py's _PER_QUOTE_CODES (:97 at my last read): an unknown code reaches the 500 branch (:332). SL 9500's red asserts the HTTP status AND the code, not just "refused". T2 names it. Both paths refuse, so FR-254 holds.
> (2) Is a whole-valued float integral? YES. Integral means EXACT equality with its integer part (value == int(value)) with NO tolerance; it serialises as the integer (3.0 → 3). 2.9999999999 is NOT integral and is refused. T1 and T2 state it in those words, and each slice has one red for 3.0 → 3 and one for a near-integer refused.
> The record is amended pre-mint; PL 9499 picks up (1). The ACK is at the mint head.

## Verified first, at `fb178c36`

Each read at `fb178c360f6fd5b2fdb7ae60eea924811a65492f` (origin/main at drafting), in
`docs/specs/03-rating-engine.md` ("03") unless named.

| What | Where | Read |
|---|---|---|
| The `outputs_json` row | 03:692 | "pre-serialised to JSON text, total over every `AlgorithmOutput.type` this path can produce (`money_minor` as a JSON number, `decimal` as a JSON string — never a JSON number, so an exact `Decimal` and a lossy `float` cannot be confused reading the column back) and refusing, not stringifying, anything else; `null` on an `"error"` row". It names the form of two types only. |
| FR-214 with `RL-1343`'s clause | 03:83 | The clause fixes `decimal` "as a JSON string on every scoring path (`/score`, both results of `/score/compare`, and the batch column `outputs_json`)", exactly `dp` digits, and ends "until then `/score` serves the engine's float, and neither path applies the declared rounding (`FD-1333`).)*". No text names a form for `int`, `count`, `relativity` or `percentage`. |
| FR-254, FR-255 | 03:166, 03:167 | FR-254: the identical code path as real-time scoring, "never a separate 'batch implementation' that could diverge". FR-255: errors are typed and per quote; the run does not abort on one. |
| `RL-923` §5(i) | `RL-923` :116-125 | The serialiser was `json.dumps(outputs, default=str)`, which stringifies what JSON cannot encode; §5(i) is the source of "refusing, not stringifying". |
| `RL-1343` rule 3 | `RL-1343` :171-196 | The `decimal` form: positional, exactly `dp` digits, no exponent, an unsigned zero; one producer, `_build_outputs`. |
| Batch's type set today | `score.py:947`, `:950-988` | `_KNOWN_OUTPUT_TYPES = frozenset({"money_minor", "decimal", "bool", "string", "date"})`; any other declared type raises `ValueError`. |
| The declared-type vocabulary | `model_schema/rating.py:237`, `:246` | `AlgorithmOutput.type` is `RatingResultType`, an open `str` that refuses only `"float"`. So T1 names a form for each type the entries name and keeps a refusal for any other. |
| PL 9509's owed text | PL 9509 @`b0659358`, §"The spec text DP-1 (b) owes", activation need 4, Task 3 | T1 on the `:692` row by SL 9511; T2 on FR-214 once, by whichever of SL 9511 and SL 9500 merges first. |
| The anchors | 03:692, 03:83 | `grep -cF` of each find string in §"The spec texts" = **1** at this tree. |

## Details taken from main (no new choice)

- **"A JSON integer"** for `money_minor` is `RL-1329` §4's form; the row's existing "a JSON
  number" is the same thing for an integral value, and T1 says integer for all three integral
  types.
- **"The decimal string form"** is FR-214's `RL-1343` clause, cited rather than restated.
- **A declared type the row does not name** stays refused, as `RL-923` §5(i) ruled and
  `_KNOWN_OUTPUT_TYPES` does today. After FD 9513's Task 1 that refusal is the row's error,
  not the run's (FR-255).
- **The error code** is the exception's class name, as `_batch_error_code` gives any uncoded
  error today (DP-3: "as today").

## Ruled

1. **DP-1 (b).** `int` and `count` outputs are a JSON integer on both paths; a non-integral
   value under either is that row's error. `relativity` and `percentage` take the `decimal`
   string form (`RL-1343` rule 3) on both paths. (c) and (d) are not taken, for the reasons in
   the entry: OQ 9556 owns the type vocabulary at save, and (d) writes integers as strings.
2. **DP-2 (ii).** SL 9500, the `RL-1343` slice (PL 9499), carries the `/score` half for
   `relativity` and `percentage`. Until it merges, `FD-1333`'s divergence stands for those two
   types.
3. **DP-3.** A row whose output does not serialise is coded with the exception's class name.
4. **The `outputs_json` row is amended (T1)** to name every declared type's JSON form. Its
   phrase "refusing, not stringifying, anything else" is struck by a dated amendment, because
   after SL 9511 the column carries two more string types and the phrase reads against that.
5. **FR-214 gains a dated clause (T2)** naming the form of the four types on every scoring
   path and the two carriers.

### Amended pre-mint, 2026-10-05 — the two open questions, ruled (the 18:20:06 entry)

The two items this record left open are ruled by the maintainer (by delegation) in the
18:20:06 BST entry quoted above. They leave §"What this record does not decide"; T1, T2,
§"What it obliges" and the Acceptance are amended to carry them. Verified at `fb178c36`:
`_PER_QUOTE_CODES` is `backend/src/app/api/score.py:97-104` and holds
`INPUT_CONTRACT_VIOLATION`, `RATE_TABLE_MISS`, `REFERENCE_LOOKUP_MISS` and
`MODEL_CALL_FAILED`; `:332` returns no per-quote problem for a code outside it, so the error
reaches the caller as a 500 (the comment at `:92-96`); a per-quote refusal is
`_PER_QUOTE_STATUS`, **422** (`:114`).

6. **Integrality (entry (2)).** For `int` and `count`, a value is integral only by exact
   equality with its integer part (`value == int(value)`), with no tolerance, and is served as
   that integer (`3.0` → `3`). A near-integer (`2.9999999999`) is not integral and is refused.
   T1 and T2 state it.
7. **A non-integral `int` or `count` value on `/score` (entry (1)).** SL 9500 refuses that
   quote with a per-quote code that is in `_PER_QUOTE_CODES`; its red asserts the HTTP status
   and the code. T2 names the code. **Which code is pending** a second answer from the
   maintainer (by delegation), relayed by the lead; it is written as the single placeholder
   `<per-quote code: pending>` in T2 and below, and this record picks none. Both paths
   refuse, so FR-254 holds.

## The spec texts

Placement was read at `fb178c36`. `RL 9498` in a text is replaced by this ruling's minted id,
and `FD 9513`, `SL 9511` and `SL 9500` by theirs, at the mint. Nothing else in a text is a
placeholder, except T2's `<per-quote code: pending>` (amended pre-mint, item 7), which is
filled with the maintainer's code before the mint. Each is applied byte for byte; a find string not found exactly once is a stop,
reported to the lead.

**T1 — 03:692, the `outputs_json` row. Applied by SL 9511 (PL 9509 Task 3).**

Find (`grep -cF` = 1 at `fb178c36`):

```text
and refusing, not stringifying, anything else; `null` on an `"error"` row
```

Replace with:

```text
~~and refusing, not stringifying, anything else~~ **Amended 2026-10-05 (`RL 9498`, FD 9513): every declared type has one JSON form — `money_minor`, `int` and `count` a JSON integer, where an `int` or `count` value is integral only by exact equality with its integer part (`value == int(value)`), with no tolerance, and is written as that integer (`3.0` → `3`), and a near-integer (`2.9999999999`) is not integral; `decimal`, `relativity` and `percentage` a JSON string, FR-214's decimal string form (`RL-1343`); `bool` a JSON boolean; `string` and `date` a JSON string. A value that does not match its declared type, or a declared type not named here, makes that row an `"error"` row whose `error_code` is the exception's class name (FR-255); no value is ever stringified as a fallback**; `null` on an `"error"` row
```

**T2 — 03:83, FR-214, a dated clause after `RL-1343`'s. Applied once, by whichever of SL 9511
(PL 9509 Task 3) and SL 9500 (PL 9499) merges first; the second checks it is present and
records the line in its ledger.**

Find (`grep -cF` = 1 at `fb178c36`):

```text
neither path applies the declared rounding (`FD-1333`).)* |
```

It includes the row's closing ` |`, so the clause goes at the end of the FR-214 cell.

Replace with:

```text
neither path applies the declared rounding (`FD-1333`).)* *(Amended 2026-10-05, `RL 9498` (FD 9513): a declared output of type `int` or `count` is served as a JSON integer on every scoring path. A value under it is integral only by exact equality with its integer part (`value == int(value)`), with no tolerance, and is served as that integer (`3.0` → `3`); a near-integer (`2.9999999999`) is not integral and is refused — in batch it makes that row an `"error"` row (FR-255), and on `/score` it refuses that quote with **422** `<per-quote code: pending>`, a per-quote code. A declared output of type `relativity` or `percentage` takes the `decimal` form above on every scoring path. Delivered for `outputs_json` by WK-1178's SL 9511, and for `/score` and both results of `/score/compare` by WK-1178's SL 9500; until SL 9500 merges, `/score` serves the engine's number for `relativity` and `percentage` (`FD-1333`'s divergence).)* |
```

**Trial apply.** Each text was applied with Python `str.replace(find, new, 1)` to a scratch
copy of 03 at `fb178c36`, and both together; re-run with the pre-mint amendment's T1 and T2,
with the same counts. Counts, `grep -cF` on the scratch copy:

| Text | Find before | Find after | New text before | New text after |
|---|---|---|---|---|
| T1 | 1 | 0 | 0 | 1 |
| T2 | 1 | 0 | 0 | 1 |
| T1 and T2 together | 1, 1 | 0, 0 | 0, 0 | 1, 1 |

The script is in §"Trial-apply script", so a reader can run it again at any tree.

### Trial-apply script

Run from the repository root. It reads the four code blocks from this file in order (T1
find, T1 new, T2 find, T2 new) and prints the counts for each text alone and for both.

```python
import pathlib, re
rl = next(pathlib.Path("docs/rulings").glob("RL-09498-*.md")).read_text()
t1f, t1n, t2f, t2n = re.findall(r"```text\n(.*?)\n```", rl, re.S)[:4]
spec = pathlib.Path("docs/specs/03-rating-engine.md").read_text()
for name, pairs in (("T1", [(t1f, t1n)]), ("T2", [(t2f, t2n)]), ("both", [(t1f, t1n), (t2f, t2n)])):
    out = spec
    for f, n in pairs:
        out = out.replace(f, n, 1)
    print(name, [(spec.count(f), out.count(f), spec.count(n), out.count(n)) for f, n in pairs])
```

## What it obliges

- **This commit:** this record only, and `docs/INDEX.md`. No spec or code file is edited here.
- **SL 9511 (PL 9509)** applies T1 with its code, in one commit (`CLAUDE.md` §2), and applies
  T2 unless SL 9500 merged first. In batch, an `int` or `count` value is integral only by
  exact equality (item 6): one red for `3.0` → `3` in `outputs_json`, one for `2.9999999999`
  making its row an `"error"` row.
- **SL 9500 (PL 9499)** applies T2 if it merges first; otherwise it checks T2 is present. It
  delivers the `/score` half for `relativity` and `percentage`, and refuses on `/score` a
  quote whose `int` or `count` value is not integral (item 7), adding the code to
  `_PER_QUOTE_CODES` if it is not already there: one red for `3.0` → `3` on `/score`, one for
  `2.9999999999` refused with **422** and `<per-quote code: pending>`, asserting both.
- **FD 9513's register cell** names the residue for `relativity` and `percentage` on `/score`
  and its discharger SL 9500 (the 18:10:57 entry, DP-2).

## What this record does not decide

- **Which per-quote code** refuses a non-integral `int` or `count` value on `/score` (item 7):
  pending the maintainer's second answer.
- **`/score/compare`'s refusal of a non-integral value.** The entry names `/score`. Compare
  maps a per-quote code through the same `_as_platform_error` (`api/score.py:449`), so the
  code's addition reaches it, but neither T2 nor this record states compare's refusal.
- **The vocabulary at save** (OQ 9556), the row escape (FD 9513 Task 1), and anything in
  `RL-1343`'s own scope beyond the two types DP-2 hands to SL 9500.

## Acceptance — the violation that must become detectable

The violation: **a declared output whose JSON form in `outputs_json` or on `/score` differs
from the form T1 and T2 name for its type, or a mismatched value that aborts the run or is
stringified instead of erroring its row.** Each is seen red before the code that turns it green.

- *Violation: batch refuses an `int`, `count`, `relativity` or `percentage` output.* Red at
  `fb178c36` (`score.py:964-965`). After SL 9511: `int` and `count` read back as JSON integers,
  `relativity` and `percentage` as exact decimal strings.
- *Violation: an `int` or `count` value that is not integral is written.* It makes its row an
  `"error"` row with the exception's class name, and the run's other rows complete.
- *Violation: integrality is decided with a tolerance, or a whole-valued float is not served as
  an integer (item 6).* SL 9511: `3.0` reads back as `3` in `outputs_json`, and `2.9999999999`
  makes its row an `"error"` row. SL 9500: `3.0` is served as `3` on `/score`, and
  `2.9999999999` is refused. Each red before its code.
- *Violation: `/score` serves a non-integral `int` or `count` value, or refuses it with a code
  outside `_PER_QUOTE_CODES` (item 7).* SL 9500's red asserts the HTTP status **422** and the
  code `<per-quote code: pending>`; a 500 is red.
- *Violation: a declared type T1 does not name is stringified.* It makes its row an `"error"`
  row; no `default=str` fallback exists in the serialiser.
- *Violation: `relativity` or `percentage` is a JSON number on `/score` after SL 9500.* SL 9500's
  red, with `/score` and `outputs_json` compared byte for byte for one output.
- *Violation: the spec text drifts from this record.* After each applier's commit, `grep -cF` of
  T1's and T2's new text in 03 is 1, and of T1's find string is 0.

Drafted as working id 9498.
