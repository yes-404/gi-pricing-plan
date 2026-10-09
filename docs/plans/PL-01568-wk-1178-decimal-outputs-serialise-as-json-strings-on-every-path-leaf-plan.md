---
id: PL-1568
family: plan
kind: leaf
title: WK-1178 — a declared decimal output is served as an exact JSON string on every scoring path, rounded once (FR-214, FR-226, FR-273, NFR-502; RL-1343): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-09            # original date 2026-10-05, set at the draft; minted 2026-10-09
owner: planner
tree: fb178c360f6fd5b2fdb7ae60eea924811a65492f
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1343, FD-1333, RL-1329, RL-1365, PL-1364, PL-1371, SL-1367, SL-1345]
---

# WK-1178 — a declared decimal output is served as an exact JSON string on every scoring path, leaf plan

*(Minted 2026-10-09 as PL-1568 from working id 9499, in the D4 batch mint; citations of the ids minted in this batch, and of ids already minted on main, are re-pointed outside quoted text, quoted channel entries and code blocks, which stay as quoted; PL-1544 (the G2-b batch) are forward cites into batches not yet merged; PL 9609, SL 9500, SL 9511, SL 9522 are working ids not minted by any batch and stay working ids.)*

Filed under working id 9499 (this plan) and slice working id 9500 (its `SL-` row under WK-1178
in [`../roadmap.md`](../roadmap.md), `draft`). The lead reserved both and named them in the brief
of 2026-10-05. Nothing here is minted. Every line number was read at `origin/main` `fb178c36`,
the `tree:` above, unless another commit is named. This is the plan that discharges `RL-1343`;
until it, no plan did (§"Why this plan exists").

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (pricing-core stays standalone; the
> model-schema validator), `contract-schema` and `contract-guard` (Task 4), `fastapi-service`
> (Task 5's route assertions), `vue-frontend` (Task 8's frontend half), `spec-change` (Task 7,
> only from an `RL-`'s text), `dev-commands` (the two-half gate; Task 6's held slot) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

## Goal

A declared output of type `decimal` reaches a client in three forms today, none of them the one
`RL-1343` rules:

| Path | Whole value (`driver_age * 1.5`, age 18) | Fractional value (`driver_age * 1.1`, age 18) | Source |
|---|---|---|---|
| `POST /api/v1/score`, `/score/compare` | `27`, a JSON **integer** | `19.8`, a JSON **float** | FD-1561's probe (draft #1204 @`d78f1235`, its §"Evidence") |
| batch `outputs_json` | `"27"` | `"19.8"` | the same probe |
| `RL-1343` rule 3, at `dp` 2 | `"27.00"` | `"19.80"` | the ruling |

The producer is `_build_outputs`
(`packages/pricing-core/src/pricing_core/rating/score.py:729-758`). A rung or `money_minor`
output takes the engine's exact `string()` read and `round_once` (`:750-755`). Every other output
takes `result[name]` unchanged (`:756-757`), the engine's raw value: a Python `int` when the value
is whole, a `float` when it is not. Batch then converts that value with
`str(Decimal(repr(value)))` (`_coerce_output_value`, `:972-974`). Neither path applies the output
step's declared rounding (`RL-1343` §"Verified first").

**`RL-1343` rule 4's refusal does not catch the whole-valued form.** `ScoringResult` refusing a
`float` in `outputs` stops `19.8`; it cannot stop `27`, which is a Python `int` and a valid
`money_minor` value. So the whole-valued form is closed only at the producer (Task 1, item 1) and
by batch's value check (Task 3, item 11). The maintainer's ruling names this as the plan's first
obligation (quoted below).

**This slice does, in this order:**
1. **One producer** (Task 1). `_build_outputs` serves every declared `decimal`, `relativity` and
   `percentage` output as the engine's exact `string()` read, rounded once with the output step's
   `RoundSpec`, written positionally with exactly `dp` digits. Batch writes the same string.
2. **The refusal** (Tasks 2–3). `ScoringResult` refuses a `float` anywhere in `outputs`; batch's
   `decimal`-family branch checks the string and converts nothing.
3. **The contract** (Task 4). The hand-authored and generated schemas admit no non-integer number
   in `outputs`, and the contract guard compares them.
4. **The routes and the trace summary** (Task 5).
5. **`NFR-502` measured again** (Task 6), in the gate's own mode, inside a held slot.
6. **The spec text from an `RL-` only, the release note, the two-half gate** (Tasks 7–8).

**How the `dp` is declared.** Per output, on its `output` step:
`RatingOutputStep.rounding: RoundSpec` (`packages/model-schema/src/model_schema/rating.py:327`),
a required field. `RoundSpec` (`rating.py:250`) carries `mode` (`half_even`, `half_up`,
`ceiling`, `floor`; `:255`) and `dp: int = Field(ge=0)` (`:256`). FR-226 (`03:112`): "`output`
steps declare rounding explicitly". There is no type-level or algorithm-level default; `dp` 2 in
"27 → `"27.00"`" is the value the test fixture declares (as `test_rating_score_batch.py:95`
does), not a platform default.

**Tech stack.** Python 3.12, Pydantic v2, Polars, FastAPI, pytest; the frontend half of the gate
(pnpm, Vite, vue-tsc) runs unedited.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-214 and its dated
clause (`:83`), FR-226 (`:112`), FR-227 (`:113`), FR-250 (`:162`), FR-254 (`:166`), FR-255
(`:167`), FR-273 (`:229`), the `outputs_json` row of the batch output table (`:692`), NFR-489
(`:1330`), NFR-499 (`:1340`), NFR-502 (`:1343`);
[`../specs/07-platform.md`](../specs/07-platform.md) FR-451 (`:182`). The rulings are `RL-1343`
(rules 1–7, "What it obliges", "Acceptance"), `RL-1329` §3 (`PositionalDecimalStr`) and §4, and
`RL-1365` DP-A2 (the `NFR-502` method).

## The maintainer's decision this plan rests on, quoted

The maintainer (by delegation), in `~/gi-pricing-plan.local/channel/to-lead.md` (a local channel
file, so cited by its header), the entry headed
"2026-10-05 18:10:57 BST — PL 9509 (#1210 @dc4f9c50) DPs RULED: DP-1 (b), DP-2 (ii), DP-3 the class name; the RL-1343 leaf plan is reserved NOW",
verbatim:

> The finding that _ladder_json (:1122) is ALSO outside the try, alongside _outputs_json (:1123): good. Task 1 covers anything after the try.
> DP-1: (b). int and count are a JSON INTEGER on both paths, and a non-integral value under them becomes that ROW's error. relativity and percentage use the DECIMAL STRING form (the RL-1343 rule, and 03:692 keeps lossy floats out). (c) is NOT taken, because OQ 9556 owns the type vocabulary at save; (d) is not taken.
> DP-2: (ii). The RL-1343 slice carries the /score half for relativity and percentage. Until it lands, FD-1333's divergence stands for those two types, and FD 9513's register cell names that residue and its discharger.
> DP-3: the exception class name, as today.
> RL-1343 HAS NO DISCHARGING PLAN, and its gate is met: YES, reserve the SL/PL ids now under WK-1178 and spawn a planner at the next free seat. Its scope: BOTH decimal forms (whole-valued, which today is a JSON integer, with its own red: 27 → "27.00" at dp 2; fractional, today a float), relativity and percentage on /score (DP-2 (ii)), and NFR-502's re-measure in the gate's own mode. It SERIALISES with SL 9511 on _coerce_output_value. As a breaking wire change, it runs the frontend half of the gate.
> Task 1 (the row escape) is dispatchable before the DPs, but it edits score.py, so it still runs AFTER SL 9561 in lane B order.
> Discrepancies: PL 9521 Step 1a citing FD 9513, and PL 9567's write-set table in delta 7: both pre-mint fixes, good.

Clause by clause, where this plan carries each: "BOTH decimal forms … 27 → "27.00" at dp 2" is
Acceptance 1 and 2; "fractional, today a float" is Acceptance 2; "relativity and percentage on
/score (DP-2 (ii))" is Acceptance 6 and 8; "NFR-502's re-measure in the gate's own mode" is
Acceptance 19 and Task 6; "SERIALISES with SL 9511 on _coerce_output_value" is activation need 3
and §"Write set"; "runs the frontend half of the gate" is Acceptance 21 and Task 8.

## Pre-mint delta 1 (2026-10-05): `RL-1567`'s two rulings for this slice

The lead relayed two rulings of the maintainer (by delegation) on `RL-1567` (#1212,
read at `c2c70690`), in `~/gi-pricing-plan.local/channel/to-lead.md`, verbatim.

The entry headed "2026-10-05 18:20:06 BST — RL 9498 (#1212 @7e71b040): both open questions RULED as recommended, with one precision each":

> (1) /score with a NON-INTEGRAL int or count value: REFUSE THAT QUOTE in SL 9500, with an EXISTING per-quote code from 03's owned list, else spec first. PRECISION: the code must be in backend/src/app/api/score.py's _PER_QUOTE_CODES (:97 at my last read): an unknown code reaches the 500 branch (:332). SL 9500's red asserts the HTTP status AND the code, not just "refused". T2 names it. Both paths refuse, so FR-254 holds.
> (2) Is a whole-valued float integral? YES. Integral means EXACT equality with its integer part (value == int(value)) with NO tolerance; it serialises as the integer (3.0 → 3). 2.9999999999 is NOT integral and is refused. T1 and T2 state it in those words, and each slice has one red for 3.0 → 3 and one for a near-integer refused.
> The record is amended pre-mint; PL 9499 picks up (1). The ACK is at the mint head.

The entry headed "2026-10-05 18:20:40 BST — RL 9498 precision (1), the code: (c) RATING_TYPE_MISMATCH, added to _PER_QUOTE_CODES":

> (c) ADOPTED. RATING_TYPE_MISMATCH is already owned (03:929) and already means "a value does not fit its declared type". SL 9500 adds it to _PER_QUOTE_CODES (api/score.py:97-104, read by you at fb178c36) as a one-line change, and T2 plus a dated 03 note state that it is ALSO served per quote at score time. Its red asserts the per-quote refusal's status AND the code. (a) is refused (misleading); (b) is not needed.
> ONE THING NAMED, NOT CHANGED: in BATCH the same fault's row error_code stays the exception class name (DP-3, FR-255). T2 says so explicitly, so the two paths' codes for one fault are a stated difference, not a discovered one. If the plan's batch side raises a dedicated exception class for it, the class name is stated in T1.

**What this delta changes, at every site it reaches** ([`README.md`](README.md) rule 5):
- **Scope:** this slice also serves a declared `int` or `count` output on `/score` and
  `/score/compare` as a JSON integer when its value is integral by exact equality (`3.0` → `3`),
  and refuses the quote with **422** `RATING_TYPE_MISMATCH` when it is not (`2.9999999999`).
  `RATING_TYPE_MISMATCH` is added to `_PER_QUOTE_CODES` (`backend/src/app/api/score.py:97-104`;
  `_PER_QUOTE_STATUS` is 422, `:114`; `/score/compare` maps through the same
  `_as_platform_error`). Acceptance 24–27 and Task 3 carry it.
- **DP-1 is ruled** for its main case by entry (1) (row marked). Its residue (a float under any
  other declared type: a compound output, or item 18's planted path) is `RL-1343` rule 4's own
  consequence, the generic 500, and needs no ruling.
- **The spec texts are `RL-1567`'s** (activation need 4): T2 on FR-214, applied here only if
  this slice merges before SL 9511; **T3**, the dated note on `RATING_TYPE_MISMATCH` in 03's
  owned-code list (`03:929`), **always applied by this slice** with its code
  (`RL-1567` §"What it obliges").
- **Item 12 is superseded** by items 24–27. Items 18 and 20, §"Write set", §"Release note",
  §"Spec text owed", the contention table and the roadmap row are amended in place, each marked
  *(pre-mint delta 1)*.
- **A conflict found while folding it in, raised as DP-4** (blocking). The same fault's batch
  `error_code` cannot stay the class name with one producer. Batch scores each row through
  `_score_context_sync` → `build_scoring_result` → `_build_outputs`, inside
  `_score_batch_row`'s `try` (`score.py:1096-1100`), and `_batch_error_code` (`:1006-1018`)
  turns a coded `"CODE: …"` error back into its code. The refusal must run in `_build_outputs`,
  before `ScoringResult` is built, because rule 4 refuses the float at construction. So a coded
  refusal there gives every batch row `RATING_TYPE_MISMATCH`, and SL 9511's class-name check
  after the `try` never sees the value. Reported to the lead on 2026-10-05 before this delta.

## Pre-mint delta 2 (2026-10-05): DP-3 and DP-4 ruled, and the conditions on the test changes

The maintainer (by delegation), in `~/gi-pricing-plan.local/channel/to-lead.md`, relayed by the
lead, verbatim. The entry headed "2026-10-05 18:25:42 BST — PL 9499 (#1213 @b342ae09): DP-3 = SL-1367 FIRST, CONFIRMED; DP-1 correction noted; the test inversions accepted with one condition":

> DP-3: SL-1367 FIRST, CONFIRMED, for your reasons (it gates WK-675 S3's typed route and the 11/12 list; its ledger carries RL-1365's scripts that SL 9500 reuses; the client then shows SL 9500's narrowing). The roadmap SL-1409 row's order line gets a DATED correction at the next planner touch, citing this entry (the roadmap is a living doc, so the line is corrected in place with a date, not rewritten silently). PL-1364 DP-A3 is recorded as answered.
> DP-1 marked RULED per RL 9498 (c), with 422 RATING_TYPE_MISMATCH per quote on /score AND /score/compare: noted, and the reds are rewritten.
> dp per output (RoundSpec at rating.py:327) with round_to_text beside round_once: accepted. round_once's dp≠0 refusal stays untouched.
> The two test changes not in the brief: ACCEPTED, with ONE CONDITION. test_score.py:1304-1320 (a planted float, expecting 200) becomes a 500. That is only right if the 500 is the NFR-499 "no value leaked" internal error (a planted float is an engine-invariant breach, not a caller or author fault). The rewritten test asserts INTERNAL_ERROR, the absence of the value in the body, and that the per-quote codes (including the new RATING_TYPE_MISMATCH) are NOT used for it. test_rating_ladder_exact.py:594 is inverted with a citation to RL-1343.
> The NFR-502 STOP rule (HEAD's median p99 over base's by more than base's own 3-run range): accepted.
> The false docstring at traces.py:148-151: fixed in the slice (a note, as for the models.py comment).

The entry headed "2026-10-05 18:27:10 BST — RL 9498 STOP: (a) ADOPTED; my 18:20:40 "batch keeps the class name" is SUPERSEDED once SL 9500 lands":

> (a). The batch path runs _build_outputs inside _score_batch_row's try (score.py:1096-1100), and _batch_error_code (:1006-1018) maps a coded "CODE: msg" ValueError to CODE. So with ONE producer (SL 9500's check in _build_outputs), batch rows code the fault RATING_TYPE_MISMATCH, the same as /score: FR-254 holds, and the codes agree. My 18:20:40 "NAMED, NOT CHANGED: batch keeps the class name" described the state BEFORE SL 9500 and is SUPERSEDED for after it; the RL quotes both entries.
> Amendments, pre-mint, ONE DM commit: T2 and T3's batch clause = "until SL 9500 merges, batch codes it ValueError (SL 9511's _coerce_output_value, the class-name rule); after, RATING_TYPE_MISMATCH, from the single producer"; item 8 and the Acceptance to match. My 18:26:46 T1 fix ("T1 states ValueError") becomes the same time-bounded sentence in T1.
> PL 9499 marks DP-4 ruled (a). SL 9500 RE-EXPECTS SL 9511's class-name red to RATING_TYPE_MISMATCH, citing this entry, with a batch red asserting the row's error_code is RATING_TYPE_MISMATCH and the run continues. PL 9509 marks its class-name red "until SL 9500".
> (b) is refused (a path flag in the shared builder is the divergence FR-254 forbids).

**What this delta changes, at every site it reaches** ([`README.md`](README.md) rule 5):
- **DP-3 ruled (a): `SL-1367` first.** DP-3's row, activation need 5 (now unconditional), the
  contention table's `SL-1367` row and Hand-off 3 are amended in place. **`PL-1364` DP-A3 is
  answered by the 18:25:42 entry** (separate slices, Part A first). The `SL-1409` row's lane-B
  order line in `docs/roadmap.md` gets a dated correction in this commit, citing the entry, with
  the old order kept and marked superseded in place.
- **DP-4 ruled (a).** Batch codes a non-integral `int`/`count` value `RATING_TYPE_MISMATCH`, from
  the single producer, once this slice merges; until then SL 9511's `ValueError` stands. Item 27
  now asserts `RATING_TYPE_MISMATCH` and that the run continues; **item 28** is added: this slice
  re-expects SL 9511's class-name reds (PL-1566 items 6 and 13) to `RATING_TYPE_MISMATCH`, citing
  the 18:27:10 entry. `RL-1567` is amended pre-mint by the decision-maker to say "until SL 9500
  merges, … ValueError …; after, RATING_TYPE_MISMATCH"; this slice applies T3 as minted.
- **Item 18 takes the condition.** The planted float (`_exact` → `None` under the `money_minor`
  output `fee_minor`) is refused at `ScoringResult` construction (`RL-1343` rule 4). `RL-1343`
  names no code for that refusal; the 18:25:42 entry fixes it as the NFR-499 internal error. So
  item 18 asserts **500**, problem `code == "INTERNAL_ERROR"` (`backend/src/app/errors.py:572-580`,
  fixed detail text), no `1234.5` and no input value in the body, and a `code` outside
  `_PER_QUOTE_CODES` (so neither `RATING_TYPE_MISMATCH` nor any other per-quote code). This is
  consistent with items 25–26: a non-integral `int`/`count` is the declared-type fault the
  producer detects and codes (422); a float that reaches construction under any other type is an
  engine-invariant breach (500).
- **Accepted as planned:** the per-output `dp` with `round_to_text` beside `round_once` (whose
  `dp != 0` refusal stays untouched); item 9's inversion citing `RL-1343`; the `NFR-502` stop rule;
  the `traces.py:148-151` docstring fix (already in §"Write set" and Task 5 Step 2).

## Why this plan exists

No plan discharged `RL-1343` at `fb178c36`:
- `PL-1371` (`:251`): "RL-1343 decimal-output fix (in the gap before S2 merges) | 1 | — | **no
  leaf plan yet**".
- `PL-1364` (`:766`): "The `RL-1343` rule-4 slice (WK-1178, not yet planned)".
- PL-1520 (#1051 @`c7621ca2`) cites `RL-1343` only as a later slice.
- PL-1566 (#1210) §"RL-1343's discharge" records the same absence and states what this plan owes
  (its items 1–3 and Hand-off 3). Each is carried here: item 1 (both forms; rule 4's blind spot)
  is Acceptance 1, 2 and 11; item 2 (`relativity` and `percentage`, PL-1566 item 7 flipped to both
  paths) is Acceptance 6 and 8; item 3 (serialise on `_coerce_output_value`) is activation need 3.
- The `SL-1409` row (`docs/roadmap.md:1435`) orders lane B "… → this slice → the `RL-1343`
  decimal fix → FD-1335 Part A", but `PL-1364` (`:669`, `:1082-1086`) is written for Part A
  first. That disagreement is DP-3, the lead's.

## Status

`draft`. ~~**DP-1 is open, the maintainer's;**~~ *(pre-mint delta 1: DP-1 ruled by `RL-1567`.)* ~~**DP-4 is open, the maintainer's; DP-3 is open, the lead's** (recommendations given);~~ *(pre-mint delta 2: DP-3 and DP-4 ruled (a); no decision point is open)*;
DP-2 is not blocking. The plan
moves to `active` only through a separate activation PR, after every activation need below holds.

### Activation needs, in order

1. **`RL-1343` minted.** It is, at `fb178c36`
   (`docs/rulings/RL-01343-oq-1334-decided-…-rounded-once.md`), and its gate ("after WK-674 Slice
   3 merges", §5) is met: `SL-1345` is `closed` (`docs/roadmap.md:929-945`).
2. **SL-1427 merged** (the emergency slice, PL-1426, #1196 @`68b2f860`). It edits `score_one` and
   `_score_context_sync` in `score.py`; lane B order puts every later `score.py` slice after it
   (the ruling's last paragraph).
3. **SL 9511 not in flight beside this slice** (PL-1566, #1210 @`b0659358`). Both edit
   `_coerce_output_value` (`score.py:950-988`), the same function, so they **serialise**, in
   either order (PL-1566 Hand-off 3 at `b0659358`: "whichever of SL 9511 and SL 9500 merges
   second merges `main` first, and keeps the other's branches"). **This plan is written for SL
   9511 first** (recommended: PL-1566 Task 2 Step 3 adds the `("decimal", "relativity",
   "percentage")` branch with batch's interim conversion, which this slice then replaces, and its
   row escape makes item 12's batch half an error row rather than an abort). If the lead orders
   this slice first, the dispatch record restates items 8, 11 and 12 against today's branch
   (`:972-974`, `decimal` only; `relativity`/`percentage` still refused in batch) and this slice
   applies T2 (§"Spec text owed").
4. ~~**DP-1 ruled; DP-3 decided by the lead; and the `RL-` carrying PL-1566's T2 minted**~~
   *(pre-mint delta 1)* **DP-3 decided by the lead; DP-4 ruled; and `RL-1567` (#1212, the `RL-`
   carrying T2 and T3) minted, its T3 reflecting DP-4's ruling** (§"Spec text owed"). DP-1 is
   ruled by `RL-1567`. This plan drafts no spec text.
5. **`SL-1367` merged** (its ledger holds `RL-1365`'s scripts, which Task 6 reuses). *(Pre-mint delta 2: DP-3 ruled (a), so this need is unconditional.)*
6. **The maintainer's dispatch GO, a solo window for Task 6, and this plan made `active` by a
   dated line** in a separate activation PR. The dispatch record writes `RL-1445`'s (
   #1162) same-Work lines for every WK-1178 slice in flight beside this one (§"Write set").

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means: the named test was run, and it failed **for the stated cause**, before the code that turns
it green existed. A test that fails with the right status but another cause is a plan defect
([`README.md`](README.md) rule 2). The ledger records each red with its printed failure line.
`P` is `packages/pricing-core/tests/test_rating_decimal_outputs.py` (new). `M` is
`packages/model-schema/tests/test_scoring_outputs.py` (new). The fixture for `P` is
`test_rating_score.py`'s `_algorithm_payload` plus one `expression` step `probe` (the declared
`result_type`) and one `output` step `probe_out`, declared `rounding` given per item, as
`RL-1343`'s appendix script and FD-1561's probe built it.

**Task 1 — one producer (`uv run pytest packages/pricing-core/tests/test_rating_decimal_outputs.py -q`)**

1. `test_a_whole_valued_decimal_output_is_a_string_at_the_declared_dp`. Expression
   `driver_age * 1.5`, age 18, rounding `half_even` dp 2. `score_one(...).outputs["probe_out"] ==
   "27.00"` (a `str`), and `json.loads(result.model_dump_json())["outputs"]["probe_out"] ==
   "27.00"`. **Red:** `assert 27 == '27.00'` (the engine's `int`, `:756-757`). This is the
   whole-valued red the ruling names.
2. `test_a_fractional_decimal_output_is_a_string_at_the_declared_dp`. `driver_age * 1.1`, dp 2 →
   `"19.80"`. **Red:** `assert 19.8 == '19.80'`.
3. `test_the_declared_rounding_is_applied_once`, parametrised: `1.23456 + 0 * risk_premium_minor`
   `half_even` dp 2 → `"1.23"`; `1.225 + 0 * …` `half_even` dp 2 → `"1.22"`; the same with
   `half_up` → `"1.23"`. **Red:** the unrounded float (`1.23456`, `1.225`) (`RL-1343` Acceptance 2).
4. `test_a_value_beyond_float_precision_is_served_exactly`. `1234567.1234567890123456 + 0 * …` at
   dp 16 → `"1234567.1234567890123456"`. **Red:** the float `1234567.1234567892` or similar, a
   lost digit (`RL-1343` Acceptance 3). If the engine's own `string()` read of this literal is not
   exact at the dispatch tree, the item **stops** and goes to the lead (it would be an engine fact,
   not this slice's).
5. `test_the_string_is_positional_with_exactly_dp_digits`, parametrised: `3.3` dp 4 → `"3.3000"`;
   `-0.001` dp 2 → `"0.00"` (never `"-0.00"`); `0.0000001` dp 7 → `"0.0000001"`; `0` dp 7 →
   `"0.0000000"`; `27` dp 0 → `"27"` (no point). Each matches
   `^-?[0-9]+(\.[0-9]+)?$` (`common/money.schema.json#/$defs/Decimal`). **Red:** the raw value
   (`RL-1343` Acceptance 4, plus the `dp` 0 case rule 3.3 names).
6. `test_relativity_and_percentage_share_the_producer`, parametrised over `relativity` and
   `percentage` and over items 1 and 2's expressions → `"27.00"` and `"19.80"`. **Red:** `27` and
   `19.8` (DP-2 (ii) as ruled: the `/score` half is this slice's).
7. `test_a_null_decimal_output_stays_null` (control, not a red). A `decimal` output whose source
   is `null` is served `None` (the `string(null)` → `"null"` case `_exact` already maps to `None`,
   `score.py:568-578`). Passes before and after.
8. **One producer.** `test_score_batch_and_score_one_produce_byte_identical_ladders`
   (`packages/pricing-core/tests/test_rating_score_batch.py:158`, FR-254) gains one assertion: for
   the `age_factor` output (`:84`, dp 2 at `:95`), `json.loads(outputs_json)["age_factor"]` is
   the same `str` as `json.loads(score_one(...).model_dump_json())["outputs"]["age_factor"]`, and
   it has exactly two digits after the point. PL-1566 item 7
   (`test_a_fractional_declared_output_is_a_decimal_string_in_batch`, in
   `test_rating_score_batch_outputs.py`) flips from batch only to both paths, with rule 3's
   expected strings. **Red:** `/score` gives a number where batch gives a string.
9. **The pin from `SL-1345` inverts.**
   `test_a_decimal_output_is_served_exactly_as_before_rl_1343`
   (`packages/pricing-core/tests/test_rating_ladder_exact.py:594-610`) asserts today that the
   value is a `float` and a JSON number (`:608`, `:610`); its docstring names `RL-1343` as what
   ends it. It is renamed `test_a_decimal_output_is_served_as_rl_1343_rules` and asserts the
   string at its declared dp. It goes red at Task 1 Step 3 **by the intended cause**; that red is
   recorded and is not a regression.

**Task 2 — the refusal at construction (`uv run pytest packages/model-schema/tests/test_scoring_outputs.py -q`)**

10. `test_a_float_anywhere_in_outputs_is_refused`, parametrised: `{"r": 1.5}`; `{"m": {"a":
    1.5}}`; `{"l": [1, 1.5]}`. `ScoringResult.model_validate(...)` raises `ValidationError`.
    Control in the same test: `{"i": 27, "s": "27.00", "b": True, "n": None, "m": {"a": 1}}` is
    accepted. **Red:** no exception (`outputs: dict[str, object]`, `scoring.py:219`) (`RL-1343`
    Acceptance 6). A further control documents the blind spot: `{"r": 27}` is accepted at
    construction, because the model does not know declared types; items 1 and 11 close it.

**Task 3 — batch checks, never converts (`uv run pytest packages/pricing-core/tests/test_rating_decimal_outputs.py -q -k coerce`)**

11. `test_the_decimal_family_branch_refuses_anything_but_the_positional_string`, parametrised over
    `decimal`, `relativity`, `percentage` and over the values `27` (`int`), `19.8` (`float`),
    `Decimal("19.8")`, `"1E-7"`, `"-0.00"`: `_coerce_output_value(declared_type, value)` raises
    `ValueError`. Control: `"19.80"` is returned unchanged. **Red:** `"27"`, `"19.8"`, `"19.8"`
    are returned (PL-1566's interim branch, read at the dispatch tree in Task 0). This is the
    batch half of the whole-valued blind spot.
12. ~~`test_an_integral_type_with_a_fractional_value_is_refused_on_score` (DP-1 as recommended).
    An `int` output over `driver_age * 1.1`: `score_one` raises a `ValueError` (Pydantic's
    `ValidationError`) at `ScoringResult` construction, and batch gives that row an `"error"` row
    whose `error_code` is the class name (PL-1566 DP-3 as ruled). **Red:** `/score` serves `19.8`.~~
    *(Pre-mint delta 1: superseded by items 24–27, `RL-1567`.)*

**Task 4 — the contract (`uv run pytest backend/tests/test_contracts.py -q -k outputs`)**

13. The generated schema's `ScoringResult.outputs` admits no non-integer number at any depth, in
    `docs/contracts/schemas/generated/score-comparison.schema.json` (`$defs.ScoringResult`), and
    the hand-authored `docs/contracts/schemas/scoring.schema.json` (`:60`, today
    `"outputs": {"type": "object"}`) says the same.
14. A new guard in `backend/tests/test_contracts.py`, beside
    `test_generated_and_authored_agree_on_scoring_field_names` (`:409`, which compares names
    only), compares the `outputs` value schema of the two and walks it for `"number"`. **Red:**
    on a planted copy of the hand-authored schema whose `outputs` admits `{"type": "number"}` the
    guard fails, naming the path (`RL-1343` Acceptance 6, second sentence). Recorded.
15. `uv run python scripts/generate-contracts.py --check` exits 0 after regeneration.

**Task 5 — the routes and the trace summary**

16. `backend/tests/test_score.py` (appended), `uv run pytest backend/tests/test_score.py -q -k
    decimal_output`: through `POST /api/v1/score`, the whole-valued and the fractional `decimal`
    outputs are JSON strings `"27.00"` and `"19.80"` in the body; the summary
    `traces_service.summarise_result(result)` carries the same strings. **Red:** `27` and `19.8`.
17. `backend/tests/test_score_compare.py` (appended): both `base` and `comparison` carry the
    strings (`RL-1343` Acceptance 1). **Red:** numbers.
18. `test_the_float_path_fails_the_route_level_fee_assert` (`backend/tests/test_score.py:1304-1320`)
    plants the float path (`_exact` → `None`, `:1315`) and asserts a 200 with `1234.5` in the
    body (`:1317-1318`). After Task 2 that plant is refused at construction. The test keeps its
    plant and its `req("FR-273")` marker; its expectation becomes: a 500 problem response whose
    body contains neither `1234.5` nor `premium_in`'s value (NFR-499). Its old expectation is run
    once after Task 2 and fails; recorded. Under DP-1 (b), the dispatch record restates the status
    and code. *(Pre-mint delta 2, the 18:25:42 condition: the 500 is the NFR-499 internal error.
    The test asserts status 500, `body["code"] == "INTERNAL_ERROR"`, `body["code"] not in
    _PER_QUOTE_CODES` (imported from `app.api.score`, so the new `RATING_TYPE_MISMATCH` is
    covered), and neither `1234.5` nor `premium_in`'s value anywhere in `response.text`.)*

**Task 6 — `NFR-502` measured again (gate's own mode)**

19. `RL-1365` DP-A2's three limbs, **as that ruling specifies them**, with this slice's base (the
    merge base) and HEAD: limb 1 (Shapes U and T, V+S and S, three runs of 1000 after 100
    warm-up, p99 = the 990th sorted value; Shape U's 60 `outputs` entries include at least 20
    `decimal` strings at dp 4, so the new validator walks real values); limb 2 (`/score` with
    Shape U, `/score/compare` with Shape T, base/HEAD alternating three times each); limb 3
    (`response_model` and `response_field` `None` on both routes). The threshold is
    `RL-1365`'s, not a chosen number: **stop** if HEAD's median route p99 exceeds base's median by
    more than base's own range across its three runs, or if limb 3 prints anything but `None`,
    `None` (and a `$ref` if `SL-1367` has merged; `{}` otherwise, recorded as such). Figures are
    read beside NFR-489's 15 ms no-GBM budget (`03:1330`) and the 0.070 ms of NFR-502's first
    amendment. The ledger carries every row, both scripts inline with sha256 prefixes, both
    trees, and `uptime`, `free -h` and both `flock -n` slot reads before and after.

**Task 7 — spec text, release note**

20. `git diff origin/main...HEAD -- docs/specs/` is exactly `RL-1567`'s T3 on the `03:929` line
    *(pre-mint delta 1)*, plus T2 on the FR-214 row only if this slice merged before SL 9511,
    each byte for byte from the minted `RL-1567` (§"Spec text owed"). After the commit,
    `grep -cF` of T3's new text in 03 is 1 and of its find string is 0 (`RL-1567` Acceptance,
    last bullet). The release note is one paragraph in the squash-commit body and in the ledger
    (§"Release note").

**The gate**

21. The full two-half gate (`CLAUDE.md` §11) is green on the merge tree, through the gate-runner,
    holding a gate slot; the frontend half includes `pnpm --dir frontend generate:api` and records
    whether `frontend/src/api/generated/schema.d.ts` changed (it changes only if `SL-1367` merged
    first; §"Frontend"). `python3 scripts/audit-docs.py` and `uv run python scripts/req-coverage.py`
    are part of it.
22. `uv run pytest packages/pricing-core/tests/test_rating_score_batch.py packages/pricing-core/tests/test_rating_score_batch_outputs.py -q`
    passes; `test_one_invalid_row_does_not_stop_the_batch` is not edited.
23. `git diff --stat origin/main...HEAD` lists only paths in §"Write set".

**Task 3b — `int` and `count` on `/score` (pre-mint delta 1, `RL-1567` items 6, 7, 9)**

Fixture: as `P`'s, with the `probe` step's `result_type` and the declared output `int` (and,
parametrised, `count`). Integrality is decided on the engine's exact `string()` read of the
source (`_exact`, as for every other output-step source; FR-273), by exact equality with its
integer part, with no tolerance (entry (2)).

24. `test_a_whole_valued_float_under_an_integral_type_is_served_as_the_integer`
    (`P`, `req("FR-214")`). The expression `driver_age / 6` at age 18 (the engine's `3.0`) and,
    if the engine gives a whole value as an integer there, `3.0 + 0 * risk_premium_minor`
    instead (Task 3b Step 1 reads which). `score_one(...).outputs["probe_out"] == 3`,
    `type(...) is int`, and the `/score` body carries `3` with no `.`. **Red:** `3.0` (a `float`,
    `:756-757`); after Task 2 alone, the construction-time refusal. This is entry (2)'s
    "3.0 → 3" red.
25. `test_a_near_integer_under_an_integral_type_is_refused_on_score` (`backend/tests/test_score.py`,
    appended, `req("FR-214")`). `2.9999999999 + 0 * risk_premium_minor` under a declared `int`
    output, through `POST /api/v1/score`: the response is **422** and its problem `code` is
    `RATING_TYPE_MISMATCH`; the body contains neither `2.9999999999` nor any quote input value
    (NFR-499). **Red:** 200 with `2.9999999999` in `outputs`; and, with the producer's refusal
    in place but `_PER_QUOTE_CODES` not yet extended, **500** (`api/score.py:332`): record both
    runs. A 500 or any other code is red. This is entry (1)'s red and entry (2)'s near-integer.
26. `test_a_near_integer_under_an_integral_type_is_refused_on_compare`
    (`backend/tests/test_score_compare.py`, appended): the same algorithm on either side of
    `POST /api/v1/score/compare` answers **422** `RATING_TYPE_MISMATCH` (`RL-1567` item 9).
    **Red:** 200 with the number.
27. *(Amended in place, pre-mint delta 2: DP-4 ruled (a). The row's `error_code` is
    `RATING_TYPE_MISMATCH`, and the run continues: the other row is `"quoted"` with `3` in its
    `outputs_json`. Red: the class name (`ValueError`, after SL 9511) or the type refusal (before
    it), by order; recorded.)* **Batch, the same fault** (`P`, `-k integral_batch`): `score_batch` over two rows, one giving
    `2.9999999999`, one giving `3.0`. The first is an `"error"` row whose `error_code` is **the
    code DP-4 rules** (under (a), `RATING_TYPE_MISMATCH`; under (b), the exception class name,
    as `RL-1567` item 8 states today); the second's `outputs_json` carries `3`. The other rows
    complete (FR-255). **Red:** depends on order: before SL 9511, the batch refusal of `int` at
    `:964-965`; after SL 9511, its `int` branch's class-name error (PL-1566 item 6) or, for the
    whole value, `3`. The dispatch record restates the expected red at the dispatch tree.
28. *(Pre-mint delta 2, DP-4 (a), the 18:27:10 entry.)* **SL 9511's class-name reds re-expected.**
    PL-1566's items 6 and 13 (`test_a_non_integral_value_for_an_integer_output_is_an_error_row`,
    `test_a_near_integer_under_an_integral_type_is_an_error_row`, in
    `test_rating_score_batch_outputs.py`) assert `error_code == "ValueError"`. This slice edits
    each to `RATING_TYPE_MISMATCH`, with a comment citing the 18:27:10 entry, and each still
    asserts the batch completes. Run after Task 3b Step 3 and before the edit, each FAILS on
    `'RATING_TYPE_MISMATCH' == 'ValueError'`; recorded. If SL 9511 has not merged (contrary to
    the recommended order), there is nothing to edit and item 27 alone carries the batch code.

## Global Constraints

- **Money is integer minor units or `Decimal`, never float** (`CLAUDE.md` §7; FR-273). No branch
  this slice writes reads `result[name]` for a `decimal`-family output; the source is the
  `string()` read or nothing. A `decimal`-family output whose exact read is missing while
  `result[name]` is not `None` raises `ValueError` (rule 3.1: "never the float in `result`").
- **One producer, one string** (`RL-1343` rule 3.4). `_build_outputs` stores a `str`, never a
  `Decimal` (Pydantic writes a `Decimal` held in `dict[str, object]` with `str()`, exponent form).
  Batch checks; it does not convert.
- **No outbound validation** (`NFR-502`). The new check runs at `ScoringResult` construction in
  `pricing-core`, which is not the route. `model_construct` (the `NFR-502` test, `test_score.py:342`)
  still bypasses it, and that test is not edited.
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2). The rounding helper goes in
  `pricing_core/rating/ladder.py`, beside `round_once` (`:91`), reusing `_ctx()` (100 digits) and
  `pricing_core.money.ROUNDING_MODES` (`ladder.py:33`).
- **No shape hand-written twice** (`CLAUDE.md` §2). The outputs value type is spelt once in
  `model_schema/scoring.py`; the generated contract is regenerated, never hand-edited; the
  hand-authored schema is held to it by the guard.
- **No value reaches an error** (NFR-499). The `ValidationError` text names the input value; it
  must not reach a response body or an error row. Item 18 asserts the first; `_batch_error_code`
  already keeps only `safe_error_detail`'s text for the second.
- **No spec text is written by the executor** except an `RL-`'s text block (Task 7).
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): items 9, 11, 14 and
  18 name their break.
- **`RL-1343` §7 holds:** nothing here touches `OQ-1316` or `RL-1329` R0; an output step's own
  rounding is the one rounding.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-214 | The dated clause (`RL-1343` rules 1–4): a `decimal` output is the exact string on every path; PL-1566's T2 extends it to `relativity` and `percentage` | `req("FR-214")` on items 1, 2, 5, 6, 16, 17; 24–26 *(pre-mint delta 1: `int`/`count` integral or refused, `RL-1567`)* |
| `03` | FR-226 | The output step's declared rounding applied once | `req("FR-226")` on item 3 |
| `03` | FR-227 | Read: a `decimal` output may carry money (`RL-1343` rule 2) | none new |
| `03` | FR-250 | `/score` returns the outputs in the ruled form | `req("FR-250")` on item 16 |
| `03` | FR-254 | Batch and `/score` carry byte-identical strings | `req("FR-254")` on items 8, 11 |
| `03` | FR-255 | A refused value is that row's error, not the run's | `req("FR-255")` on item 12 |
| `03` | FR-273 | The string limb: the value is read as a string, never a float | `req("FR-273")` on items 4, 10, 18 |
| `07` | FR-451 | The contract regenerated and guarded | `req("FR-451")` on item 14 |
| `03` | NFR-499 | No input value in the refusal's response | `req("NFR-499")` on item 18 |
| `03` | NFR-502 | Measured again; still no outbound validation | none new (Task 6 is a closure input, `RL-872`) |

**Findings.** `FD-1333` is discharged on merge (its register row is owned by WK-1178). FD-1561's
residue for `relativity` and `percentage` on `/score` (the maintainer's DP-2 (ii): "FD-1561's
register cell names that residue and its discharger") is discharged by this slice; the auditor's
closure names both.

**Not in scope.**
- `int` and `count` in batch, and the row escape: SL 9511 (PL-1566).
- How a compound output (`map<…>`, `array<…>`) is served (`RL-1343` §"Observed, not ruled"):
  rule 4 refuses a float inside one, which item 10 tests; the design is a separate question.
- The values inside `Trace.steps[*].consumed`/`produced` (`scoring.py:180-181`): the engine's own
  record, not `outputs`; PL-1520 owns what the trace records.
- Documenting the `/score` 200 in OpenAPI: `SL-1367` (FD-1335 Part A), which follows this slice.

### Producers of a served `outputs` value, read at `fb178c36`

| # | Path | Producer / serialiser | What it does today |
|---|---|---|---|
| 1 | all paths | `_build_outputs`, `score.py:729-758` (rung/`money_minor` `:750-755`; other `:756-757`) | the one producer; the raw `result[name]` for `decimal` |
| 2 | all paths | `build_scoring_result`, `score.py:830`; `_build_outputs` called `:847`; `ScoringResult(…)` `:864-873` | stores `outputs` in `ScoringResult.outputs: dict[str, object]` (`model_schema/scoring.py:219`), no validator |
| 3 | `/score` | `score`, `backend/src/app/api/score.py:351`; `Response(content=result.model_dump_json(), …)` `:386` | writes the Python value: `int` → integer, `float` → number |
| 4 | `/score/compare` | `score_compare`, `api/score.py:421`; `Response(content=comparison.model_dump_json(), …)` `:461` | the same, for `base` and `comparison` (`ScoreComparison`, `scoring.py:282-290`) |
| 5 | batch | `_score_batch_row` `score.py:1081` → `_outputs_json` `:991` (`json.dumps` `:1003`) → `_coerce_output_value` `:950` (`decimal` `:972-974`) | `str(Decimal(repr(value)))`; batch reaches producer 1 through `_score_context_sync` (`:1045`) |
| 6 | trace (served) | `summarise_result`, `backend/src/app/platform/traces.py:143-157` (`model_dump(mode="json", include=…)` `:157`); called `api/score.py:515`; stored as JSONB `backend/src/app/db/models.py:2305` | the same Python value; its docstring (`:148-151`) claims `_coerce_output_value` makes it exact, false on this path |
| 7 | trace (reproduced) | `backend/src/app/worker/trace_handlers.py:99` (`summarise_result` of a re-score), compared `traces.py:257` | compares 6 and 7 as dicts |
| 8 | property checks | `packages/pricing-core/src/pricing_core/rating/properties.py:298-299` | reads values for `None` only; unaffected |

No other site reads or writes `ScoringResult.outputs` (`git grep -n outputs -- packages/*/src backend/src`,
excluding the declared `AlgorithmOutput` lists in `rating.py`, `sub_graphs.py`, `compile.py`,
`replay.py`, `testing.py` and the decision-table `outputs` of `runtime.py:266`).

The `string()` read this slice needs **exists**: `exact_read_names` (`runtime.py:362`) covers
every `output` step's first consumed name, `_exact_read_node` emits `string(name)` under
`exact_key(name)` (`runtime.py:355-359`, `:374-391`), wired in `to_wire`; `_exact`
(`score.py:568-578`) reads it. So `runtime.py` is **read, not edited**.

### Frontend

`git grep -n -i outputs -- frontend/src` prints nothing at `fb178c36`. No file under
`frontend/src` names `ScoringResult`, `ScoreComparison` or `/api/v1/score`. The generated client
(`frontend/src/api/generated/`, VCS-ignored, `.gitignore:38`) is built by `generate:api`
(`frontend/package.json:13`) from `docs/contracts/openapi/generated.json`, which today has **no**
`ScoringResult` component: the `/score` and `/score/compare` 200s are `"schema": {}`. So:
- **If this slice merges before `SL-1367`** (the lane B order), the regenerated client does not
  change; the frontend half still runs (the ruling: a breaking wire change runs it).
- **If `SL-1367` merges first**, `ScoringResult.outputs`' value type appears in `schema.d.ts` as
  the narrowed union; no committed consumer reads it, so no `.vue`/`.ts` file changes. Either way
  item 21 records which case held and the `schema.d.ts` diff, if any.
- Any WK-675 consumer written later displays the string and never parses it (`vue-frontend`:
  "Never `parseFloat` a `DecimalStr`").

### Task 0 at planning time (read, not run)

Read at `fb178c36`. Nothing was executed.
- The producer table above, each line read.
- `round_once` (`ladder.py:91-99`) refuses `dp != 0`, so it cannot serve a `decimal` at dp 2; the
  new helper is needed.
- `PositionalDecimalStr` (`packages/model-schema/src/model_schema/money.py:106-111`) renders
  `format(v, "f")`; rule 3.3 names it. This slice stores the string itself (rule 3.4), so it
  reuses the rendering, not the annotated type, in `outputs`.
- `_as_platform_error` (`api/score.py:309-331`) returns `None` for any non-`CodedError`, so a
  `ValidationError` from item 12 is re-raised (`:376-378`) and answered by the generic handler
  (`backend/src/app/errors.py:594`) as a 500.
- The only committed `decimal` output declaration is `test_rating_score_batch.py:84`
  (`RL-1343` §"Who declares"); its assertion (`:192-196`) compares `Decimal(value)` and holds at
  dp 2. `test_rating_ladder_exact.py:594` pins the old behaviour (item 9).
  `test_score.py:1315` plants the float path (item 18). No other test plants a float in
  `outputs` (`git grep -n -E 'outputs=\{|"outputs": \{' -- 'backend/tests/*.py' 'packages/*/tests/*.py'`).

### Write set, and its contention (`RL-1263`, `RL-1445`)

| Path | Change |
|---|---|
| `packages/pricing-core/src/pricing_core/rating/score.py` | edited: `_build_outputs` (`:729-758`) and its docstring; `_coerce_output_value`'s `decimal`-family branch (as SL 9511 leaves it) and its docstring; `_outputs_json`'s docstring (`:992-995`) |
| `packages/pricing-core/src/pricing_core/rating/ladder.py` | added: one helper beside `round_once` (`:91`) |
| `packages/model-schema/src/model_schema/scoring.py` | edited: `ScoringResult.outputs` (`:219`), its value type and a float refusal; the class docstring |
| `docs/contracts/schemas/scoring.schema.json` | edited: `outputs` (`:60`) |
| `docs/contracts/schemas/generated/`, `docs/contracts/openapi/generated.json` | regenerated (registry-exempt, `RL-1263:104-116`) |
| `backend/tests/test_contracts.py` | appended: item 14's guard |
| `backend/src/app/platform/traces.py` | edited: `summarise_result`'s docstring (`:148-151`) only (`RL-1343` "What it obliges") |
| `packages/pricing-core/tests/test_rating_decimal_outputs.py` | added: items 1–7, 11; 24, 27 *(pre-mint delta 1)* |
| `packages/model-schema/tests/test_scoring_outputs.py` | added: item 10 |
| `packages/pricing-core/tests/test_rating_score_batch.py` | edited: one assertion in the `:158` test (item 8) |
| `packages/pricing-core/tests/test_rating_score_batch_outputs.py` | edited: PL-1566 item 7's expectations (item 8); items 6 and 13's `error_code` (item 28, pre-mint delta 2) |
| `packages/pricing-core/tests/test_rating_ladder_exact.py` | edited: the `:594-610` test (item 9) |
| `backend/tests/test_score.py` | appended: item 16; item 25 *(pre-mint delta 1)*; edited: the `:1304-1320` test's expectation (item 18; `INTERNAL_ERROR`, pre-mint delta 2) |
| `backend/tests/test_score_compare.py` | appended: item 17; item 26 *(pre-mint delta 1)* |
| `backend/src/app/api/score.py` *(pre-mint delta 1)* | edited: `_PER_QUOTE_CODES` (`:97-104`), one entry `RATING_TYPE_MISMATCH`, and its comment (`:92-96`) if it lists the codes |
| `docs/specs/03-rating-engine.md` the FR-214 row (`:83`) | PL-1566's T2, from its `RL-`, **only if this slice merges before SL 9511** (Task 7) |
| `docs/specs/03-rating-engine.md` the owned-code list (`:929`) *(pre-mint delta 1)* | `RL-1567`'s T3, always (Task 7) |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md`; `docs/roadmap.md` (this slice's row) | added; regenerated; activation and closing lines. *(Pre-mint delta 2: the `SL-1409` row's dated order correction is made in **this plan PR**, not by the slice.)* |

**Contention.** See §"Contention table" below.

### Size

About one executor day. One pricing-core function rewritten and one helper added, one model
field typed, one contract and guard, two new test modules and five edited or appended test files,
one solo timing window (Task 6), one full two-half gate. The timing window makes the slice
**exclusive** for Task 6 only: no gate, benchmark or `migrate --verify` beside it.

## Spec text owed

**No new T-text is owed by this plan.** The one text it needs is already owed elsewhere:
FR-214's dated clause (`03:83`) names only `decimal` ("a declared output of type `decimal` is
served as a JSON string on every scoring path"), and the maintainer's DP-2 (ii) puts `relativity`
and `percentage` on the same producer on `/score`. **PL-1566's T2** (§"The spec text DP-1 (b)
owes", at `b0659358`) is exactly that clause: "One declared `relativity` or `percentage` takes
FR-214's `decimal` form on every path", naming SL 9500 as the `/score` carrier. One `RL-` carries
it (a decision-maker drafts it), and **"T2 is applied once, by whichever of SL 9511 and SL 9500
merges first"**. So:
- **SL 9511 first** (this plan's recommended order): this slice applies nothing to `docs/specs/`;
  its dispatch record says so.
- **This slice first:** it applies T2 byte for byte from that `RL-` (Task 7), and SL 9511 applies
  only its own T1 (`03:692`).

If that `RL-`'s T2 does not name this slice's `/score` delivery, or names a form other than
`RL-1343` rule 3's, that is a stop for the lead before dispatch.

*(Pre-mint delta 1.)* **`RL-1567` (#1212) is that `RL-`.** It carries T1 (`03:692`, SL 9511's), T2 (FR-214, as above) and **T3**, a dated note on `RATING_TYPE_MISMATCH` in 03's owned-code list (`03:929`), which **this slice always applies** with its code (`RL-1567` §"What it obliges"). T3's text today says "in batch the same fault is an `"error"` row coded with the exception's class name (FR-255)"; under DP-4 (a) that clause is amended in `RL-1567` before it mints, and this slice applies whatever the minted text says.

No other text is owed: `RL-1343` §"Spec changes in this commit" already adopted FR-214's clause and
struck `OQ-1334`; the contract changes (Task 4) are `RL-1343` rule 4's, not spec prose; `NFR-502`
gains no line from this slice (DP-2).

## Release note

One paragraph in the squash-commit body and in the ledger (`RL-1343` §4 and "What it obliges";
the `PL-1348` Acceptance 9 precedent): *a declared `decimal`, `relativity` or `percentage` output
changes on `POST /api/v1/score` and on both results of `POST /api/v1/score/compare` from a JSON
number (an integer when whole, a float otherwise) to a JSON string with exactly the output step's
declared `dp` digits; the declared rounding is now applied on every path, batch included; an
output value that is a non-integer number is refused at construction (a 500 on `/score`, an error
row in batch).* *(Pre-mint delta 1:)* *A declared `int` or `count` output is a JSON integer on
`/score` and `/score/compare` (a whole-valued `3.0` is served as `3`), and a value that is not
integral by exact equality refuses the quote with 422 `RATING_TYPE_MISMATCH`, now a per-quote
code; in batch the same fault is an error row coded as DP-4 rules.* It also records the
stored-data check (Task 0 Step 3).

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | **What `/score` answers when a `float` reaches `outputs`** after rule 4: an `int`/`count` output over a fractional value (DP-1 (b) of PL-1566 makes it "that ROW's error" in batch but says nothing for `/score`), a compound output holding a float, or a planted float path (item 18) | **(a)** The construction-time `ValidationError` (a `ValueError`) is not a `CodedError`, so `_as_platform_error` returns `None` and the route answers the generic 500 (`errors.py:594`); batch makes it an error row with the class name. **(b)** `_build_outputs` checks each declared integral type before construction and raises a registered `CodedError` (for example `OUTPUT_TYPE_VIOLATION`), mapped to a named status, with a dated FR-214 clause and an `03` error-code row | **(a).** The case is an engine value that its own declared type does not admit: a defect, not a per-quote input fault, and OQ-1560 (#1200, decided A1 + B3) and PL-1562 close the producers that reach it at save. A 500 is how `/score` reports every other unrecognised failure (`api/score.py:316-318`), and (a) matches PL-1566 DP-3 as ruled (the class name). (b) adds a code and spec text for a case that should not occur, and a per-type check on the hot path. **RULED (pre-mint delta 1), against the recommendation, by `RL-1567` (the 18:20:06 and 18:20:40 entries): a non-integral `int`/`count` value refuses the quote with 422 `RATING_TYPE_MISMATCH`, an existing owned code added to `_PER_QUOTE_CODES`.** The residue (a float under another declared type; item 18's plant) stays the generic 500, `RL-1343` rule 4's own consequence | the maintainer (by delegation) | items 18, 24–27 |
| **DP-4** *(pre-mint delta 1)* | **The batch `error_code` of a non-integral `int`/`count` value, now that `/score` refuses it with a coded error.** `RL-1567` item 8 and its T3 say batch keeps the exception class name. But the refusal must run in `_build_outputs` (before `ScoringResult` is built, which refuses the float, rule 4), batch reaches `_build_outputs` inside the row `try` (`_score_context_sync` → `build_scoring_result`, `score.py:1096-1100`), and `_batch_error_code` (`:1006-1018`) returns the code of any `"CODE: …"` error. So with one producer, batch rows carry `RATING_TYPE_MISMATCH` | **(a)** Amend `RL-1567` pre-mint: both paths code the fault `RATING_TYPE_MISMATCH`; T3's batch clause and item 8 change; SL 9511's class-name red holds until this slice merges, and is re-expected then. **(b)** Keep the class name in batch: the coded refusal is raised only on the `/score` path, which needs a path flag through the shared `build_scoring_result` | **(a).** One producer and one code per fault (FR-254: "never a separate 'batch implementation' that could diverge"); FR-255's "typed errors" are better served by the owned code than by a class name; (b) builds the divergence FR-254 forbids, to preserve a difference the ruling only "named, not changed". **RULED (a), pre-mint delta 2** (the 18:27:10 entry; (b) refused) | the maintainer (by delegation) | items 27, 28; T3's text; activation need 4 |
| DP-2 *(not blocking)* | **Does `NFR-502` gain a dated line with this slice's figure?** | **(a)** No: the figures go in the ledger only; `RL-1365`'s dated line, applied by `SL-1367`, is the requirement's record of the current figure. **(b)** Yes: an `RL-` with a line like `RL-1365`'s | **(a).** `RL-1343` §5 asks the slice to "re-measure NFR-502 and quote the figure", which the ledger does. Under DP-3 (a) `SL-1367`'s line already stands when this slice measures, and the ledger quotes the delta against it; under DP-3 (b) `SL-1367`'s line is measured on a tree that carries this change. Either way a second line one slice apart would quote a near-identical figure | the maintainer (by delegation) | none |
| **DP-3** | **The order of this slice and `SL-1367` (FD-1335 Part A, `PL-1364`).** Two records disagree. The `SL-1409` row (`docs/roadmap.md:1435`, filed 2026-10-01) orders lane B "… → the `RL-1343` decimal fix → FD-1335 Part A". `PL-1364` DP-A3 (`:669`, the lead's, **open**) recommends (a) "the rule-4 slice follows on the next free lane", and its Hand-off (`:1082-1086`) is written for that order: "the contract already carries `$ref ScoringResult` … It re-measures `NFR-502` by this plan's Task 5 method, `RL-1365`'s scripts in this slice's ledger" | **(a)** `SL-1367` first, then this slice. **(b)** This slice first, then `SL-1367` (the `SL-1409` row's order). **(c)** Fold the two into one slice (`PL-1364` DP-A3 (b)) | **(a).** `SL-1367` gates WK-675 S6 and S7 (`FD-1335` item 1); this slice gates nothing on WK-675 (`RL-1343` §5). Under (a) this slice's `NFR-502` run reuses `RL-1365`'s scripts from `SL-1367`'s ledger, so the two figures are comparable (`RL-1365` §"Observed, not ruled"); and the frontend half regenerates a client in which `ScoringResult.outputs` first appears, so the ruled "breaking wire change" is visible in `schema.d.ts` rather than invisible. (b) leaves this slice to write the scripts and gives a frontend half with nothing to regenerate. (c) widens the WK-675 gating slice. Both are WK-1178 and touch `score.py`, so they are serial in every option. The plan's Tasks 6 and 8 are written to hold under (a) and (b). **RULED (a), pre-mint delta 2** (the 18:25:42 entry): `SL-1367` first; `PL-1364` DP-A3 answered | lead (`PL-1364` DP-A3; `lead.md`) | activation need 5; Tasks 6, 8 |

## Contention table

**Snapshot:** every open PR at `origin/main` `fb178c36`, read 2026-10-05 between 18:20 and 18:40
BST (100 open). Each plan file each PR adds was grepped on its branch for `rating/score.py`,
`api/score.py`, `model_schema/scoring.py`, `scoring.schema.json`, `test_contracts.py`,
`platform/traces.py`, `trace_handlers.py`, `ladder.py`, `_build_outputs`, `_coerce_output_value`,
`test_rating_ladder_exact`, `test_rating_score_batch.py` and `frontend/src`; each hit was then read
for write or read. The classes are those of `no_shared_files` (`RL-1263`;
`docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`) and `RL-1445`'s same-Work lines.
**No frontend consumer of `outputs` exists** (§"Frontend"), so the `frontend/src` hits (WK-675
slices and others) share no definition with this slice; `generated.json` is registry-exempt.

| Other slice (Work; source read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **SL 9511**, PL-1566 (#1210 @`b0659358`; WK-1178) | `score.py` | `_coerce_output_value` (whole function, new branches), `_KNOWN_OUTPUT_TYPES`, `_outputs_json`'s docstring, `_score_batch_row` | `_coerce_output_value`'s `decimal`-family branch, `_outputs_json`'s docstring, `_build_outputs` | **same definition → serialise**, either order; the second merges `main` first and keeps the other's branches (PL-1566 Hand-off 3). Activation need 3 |
| SL 9511 | `03` FR-214 row | T2, unless SL 9500 merged first | T2 only if first | one row, one application (§"Spec text owed") |
| SL 9511 | `test_rating_score_batch_outputs.py` | adds it (items 1–3, 5–8) | edits its item 7 (item 8 here) | **after SL 9511 only**; under the other order item 8 adds the two-path case to `P` instead |
| *(pre-mint delta 1)* every open plan, for `api/score.py` `_PER_QUOTE_CODES` | read only: PL-1426 (#1196, `:528`, `:555`) and PL-1435 (#1193) cite it; none writes it | — | one entry added | **no shared write** (sweep of every open PR's plans for `_PER_QUOTE_CODES`, `03:929` and `RATING_TYPE_MISMATCH`, 2026-10-05 ~18:45 BST; the other hits name the code in compile-time contexts only) |
| **SL-1427**, PL-1426 (#1196 @`68b2f860`; WK-1178) | `score.py`; `test_score.py`, `test_score_compare.py` | adds `_check_no_shadowed_produced_names`; edits `score_one`, `_score_context_sync`; appends reds | `_build_outputs`, `_coerce_output_value`; appends items 16–17 | different definitions; append-only → **ordered first** in lane B (activation need 2) |
| **`SL-1367`**, `PL-1364` (minted, `draft`; WK-1178) | `test_contracts.py`; `test_score.py`, `test_score_compare.py`; generated contracts | appends the untyped-2xx guard and helpers; appends spy tests; replaces the docstring of `test_the_result_is_returned_without_outbound_validation`; documents the two 200s (`api/score.py` decorators); the `NFR-502` row | appends item 14's guard; appends items 16–17; edits the `:1304-1320` test; edits `api/score.py` only at `_PER_QUOTE_CODES` (pre-mint delta 1), never its decorators or the `:342` test | different definitions; **serial by Work** (`PL-1364` `:766-767`), **`SL-1367` first** (DP-3 ruled (a), pre-mint delta 2). **Timing: never the same window** (its Task 5 is `NFR-502` too) |
| **PL-1520**, F35 remedy (#1051 @`c7621ca2`; WK-1178) | `score.py`; `model_schema/scoring.py`; `test_score_compare.py`, `test_score.py` | `_build_trace`; `build_scoring_result` (which calls `_build_outputs`); `TraceStep`'s docstring; changes three `test_score_compare.py` tests, appends one | `_build_outputs`; `ScoringResult.outputs`; appends | different definitions, but its plan calls this slice same-Work **serial** (its `:938`); `build_scoring_result`'s call line to `_build_outputs` is unchanged by us. **Timing: its two `NFR-490` windows are not ours** |
| **PL-1464**, A-2 (#1178 @`176a6a75`; WK-1178) | `score.py` | the module docstring item 2 (`:33-41`) | not the docstring | different text → **allowed one-sided**. **Timing: its `NFR-489` GLM run is never in our window** |
| **PL 9609**, WK-1250 S3 (#1173 @`7c8736fd`; WK-1250) | `score.py`; `test_score.py` | `_check_purpose_mount`, its calls, `score_one`, `_score_context_sync`; appends route tests; reads `QuotePurpose` in `scoring.py` | as above | different definitions; append-only → **allowed one-sided**, the dispatch record naming each definition |
| **PL-1447**, FD-1420 fix (#1145 @`2f3269c8`; WK-673) | `score.py` | adds `_check_as_at_values`; edits `score_one`, `_score_context_sync`; reads `test_rating_score_batch.py`'s helpers | as above | different definitions → **allowed one-sided** |
| **PL-1528**, FD-1416 fix (#1168 @`0b60c81b`; WK-1178) | `test_contracts.py` | `ONE_SIDED_SLUGS["approval-request"]`; adds `SHIPPED_NOT_COMPARED` and one test | appends item 14's guard | different definitions → **allowed one-sided**; both named in the dispatch record |
| **PL-1454**, NFR-489 remedy (#1113 @`3ad98fe2`; WK-1178) | none written; its bench asserts the quote body byte-identical, base vs head (its `:173`, `:507`) | edits `api/score.py`'s request path | `outputs`' served type | no shared write. Its bench quote declares no `decimal` output, so byte-identity holds; the dispatch record re-checks. **Timing: its ~2.5 h exclusive sweep is never in our window** |
| **PL-1452**, WK-673 S3 (#1138 @`e810b785`; WK-673) | none written (`score.py` called, not edited) | — | — | none on files. **Timing: its exclusive attribution-cost run is never in our window** |
| **PL-1435 / SL-1436** (#1193 @`42d8be16`; WK-673) | none written (its `score.py` rows withdrawn; reads `summarise_result`) | — | — | none; `generated.json` regenerated, exempt |
| **PL-1562 / SL 9522** (#1202 @`9396bdb3`; WK-1178) | none written; reads `score.py:729`, `:950`, `:991-1002` and `round_once` | edits `compile.py` `_compatible` | — | **no shared write → concurrent allowed** (`RL-1445`); its Step 1a reading of `_build_outputs` changes meaning after us: the dispatch record tells its executor |
| **PL-1564** (#1170; WK-1250), **PL-1544** (#1164; WK-1178) | none written | read `_build_trace`; read route evidence | — | none |
| **S7**, `SL-1391` code (#1206 @`69fd0ccd`; WK-673) | none of ours (17 files; `model_schema/rating.py`, not `scoring.py`) | — | — | none; `generated.json` exempt |

**Timing windows.** Task 6 needs a solo window. Five other open plans also need one (`SL-1367`
Task 5, PL-1520 ×2, PL-1464, PL-1454, PL-1452); none of them may share it, and the lead's
schedule places them.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** `git fetch origin`; record `origin/main`'s sha. Re-read every line this plan cites
  in `score.py`, `ladder.py`, `model_schema/scoring.py`, `api/score.py`, `traces.py`,
  `scoring.schema.json`, `test_contracts.py` and the four test files. A moved line is re-anchored
  in the ledger; a changed body is a stop, reported to the lead.
- [ ] **Step 2:** Confirm activation needs 2, 3 and 5 by `git log --oneline origin/main` (SL-1427
  merged; SL 9511 merged or not in flight, and which; under DP-3 (a), `SL-1367` merged), each by
  its minted id. Read `_coerce_output_value` at that tree and quote its `decimal`-family branch
  in the ledger; item 11's red is written against it.
- [ ] **Step 3: The stored-data check** (`RL-1343` "No stored data is migrated"). Against every
  development database (`psql -l | grep gipricing`), read-only: the Rating Versions whose stored
  algorithm declares an output of type `decimal`, `relativity` or `percentage`, and the
  `pending` sampled traces whose `served_summary` came from one (a served float compared with a
  reproduced string would read `mismatch`). Record the queries and counts. A non-zero count is
  listed, not migrated, and reported to the lead before Task 1.
- [ ] **Step 4:** `pgrep -af 'pytest|vitest|flock'`, `flock -n /tmp/slots/gate-1 true`, the same for
  `gate-2`. Run one test file or a `-k` selection at a time; nothing heavy beside a held slot.

### Task 1: One producer, red first (items 1–9)

- [ ] **Step 1: Write items 1–7 in `P`.** Build the fixture from
  `packages/pricing-core/tests/test_rating_score.py`'s `_algorithm_payload` and `_compiled()` as
  `RL-1343`'s appendix does (add a `probe` expression step with the declared `result_type`, an
  `output` step `probe_out` with the item's `rounding`, and the declared output). Read
  `score_one`'s signature at the dispatch tree first (`score.py:876`).
- [ ] **Step 2: Run and see each fail by its cause.**
  Run: `uv run pytest packages/pricing-core/tests/test_rating_decimal_outputs.py -q`
  Expected: items 1, 2, 6 FAIL comparing `27`/`19.8` with `'27.00'`/`'19.80'`; items 3, 4, 5 FAIL
  on the unrounded value; item 7 PASSES. Record each line.
- [ ] **Step 3: The minimal change.** In `ladder.py`, beside `round_once`:

```python
def round_to_text(value: Decimal, rounding: LadderRounding) -> str:
    """`value` rounded once with an output step's declared rounding (FR-226), written as
    `RL-1343` rule 3.3 rules: positional, exactly `dp` digits, no point at `dp` 0, and no sign
    on a zero."""
    with localcontext(_ctx()):
        rounded = value.quantize(Decimal(1).scaleb(-rounding.dp), rounding=ROUNDING_MODES[rounding.mode])
    if rounded.is_zero():
        rounded = rounded.copy_abs()
    return format(rounded, "f")
```

  In `_build_outputs`, a third branch before the `elif name in result` fallback, for
  `declared.type in _DECIMAL_FAMILY` (`{"decimal", "relativity", "percentage"}`, one module
  constant that `_coerce_output_value` also uses): `exact = _exact(result, name)`; if `exact` is
  not `None`, store `round_to_text(exact, LadderRounding(mode=step.rounding.mode,
  dp=step.rounding.dp))`; else if `result.get(name)` is `None`, store `None`; else raise
  `ValueError` naming the output, never the value. The docstring replaces "Anything else — a
  `decimal` output, for one (`RL-1343`) — is read straight from the evaluated `result`,
  unchanged" with the rule, citing `RL-1343` rules 3.1–3.4 and the maintainer's DP-2 (ii).
- [ ] **Step 4: Run items 1–7.** Expected: PASS.
- [ ] **Step 5: Item 9.** Run
  `uv run pytest packages/pricing-core/tests/test_rating_ladder_exact.py -q -k rl_1343`; it FAILS
  on `assert isinstance(value, float)` (`:608`). Record that red, then rename and rewrite it as
  item 9 says; run again: PASS.
- [ ] **Step 6: Item 8.** Add the assertion to the `:158` test and flip PL-1566 item 7 to both
  paths with rule 3's strings. Run before Task 3's change: the batch side still passes (batch
  stringifies the producer's string unchanged, or the interim branch re-stringifies it: record
  which). Run `uv run pytest packages/pricing-core/tests/test_rating_score_batch.py packages/pricing-core/tests/test_rating_score_batch_outputs.py -q`: PASS.
- [ ] **Step 7: Commit.** `fix(rating): one producer serves a decimal output as its exact string, rounded once (RL-1343 rule 3)`.

### Task 2: The refusal at construction (item 10)

- [ ] **Step 1:** Write item 10 in `M`. Run `uv run pytest packages/model-schema/tests/test_scoring_outputs.py -q`.
  Expected: the three float cases FAIL with `DID NOT RAISE`. Record.
- [ ] **Step 2:** In `model_schema/scoring.py`, type `outputs` so a `float` at any depth is refused
  and the generated JSON Schema admits no `"number"` (`RL-1343` rule 4 leaves the spelling to the
  carrier: a recursive value alias with a `BeforeValidator`, or a `field_validator` plus
  `WithJsonSchema`). `bool` stays accepted (it is an `int` subclass, not a float). The class
  docstring says the refusal is the one construction-time check and cites `RL-1343` rule 4.
- [ ] **Step 3:** Run item 10: PASS. Run
  `uv run pytest packages/model-schema/tests -q -k scoring`: PASS.
- [ ] **Step 4: Commit.** `fix(model-schema): ScoringResult refuses a float anywhere in outputs (RL-1343 rule 4)`.

### Task 3: Batch checks, never converts (items 11, 12)

- [ ] **Step 1:** Write items 11 and 12 in `P`. Run with `-k "coerce or integral_type"`. Expected:
  item 11 FAILS on `DID NOT RAISE` for `27`, `19.8`, `Decimal("19.8")` (returned as `"27"`,
  `"19.8"`); item 12's `/score` half FAILS only if Task 2 has not landed; after Task 2 it passes,
  so its red is Task 2's (record the run order). Record.
- [ ] **Step 2:** Replace the conversion in the `decimal`-family branch of `_coerce_output_value`:
  the value must be a `str` matching `^-?[0-9]+(\.[0-9]+)?$` and not `"-0"`-signed at zero, else
  `ValueError` naming the declared type and the value's type (never the value). Return it
  unchanged. Docstrings of `_coerce_output_value` and `_outputs_json` say batch checks the
  producer's string (`RL-1343` rule 3.4).
- [ ] **Step 3:** Run items 11, 12 and item 8's two files: PASS.
- [ ] **Step 4: Commit.** `fix(rating): batch checks the decimal-family string and converts nothing (RL-1343 rule 3.4)`.

### Task 3b: `int` and `count` on `/score` (items 24–27; pre-mint delta 1)

- [ ] **Step 1:** Write items 24 and 27 in `P`, 25 in `test_score.py`, 26 in
  `test_score_compare.py`. First read what the engine returns for `driver_age / 6` at 18 under
  `result_type` `int` (a `float` `3.0` or an `int` `3`) by running item 24 once; if `3`, switch
  item 24 to `3.0 + 0 * risk_premium_minor`, which the engine returns as a float, and record it.
- [ ] **Step 2: Reds.** Run `uv run pytest packages/pricing-core/tests/test_rating_decimal_outputs.py -q -k "integral"`
  and `uv run pytest backend/tests/test_score.py backend/tests/test_score_compare.py -q -k near_integer`.
  Expected: item 24 FAILS on `3.0` (or, after Task 2, on the construction refusal); items 25 and
  26 FAIL on the 200. Record each line.
- [ ] **Step 3: The producer.** In `_build_outputs`, a branch for `declared.type in ("int",
  "count")`: read `exact = _exact(result, name)`; `None` source stays `None`; if
  `exact != exact.to_integral_value()` (no tolerance, entry (2)), `_raise_named("RATING_TYPE_MISMATCH",
  f"output {declared.name!r} is declared {declared.type} and its value is not integral")` (no
  value in the text, NFR-499); else store `int(exact)`.
- [ ] **Step 4: Item 25's second red.** Run item 25 now: it FAILS with **500** (the code is not yet
  per quote, `api/score.py:332`). Record. Add `RATING_TYPE_MISMATCH` to `_PER_QUOTE_CODES`
  (`:97-104`). Run items 24–26: PASS.
- [ ] **Step 5: Items 27 and 28.** *(Pre-mint delta 2: DP-4 ruled (a).)* Run item 27: PASS with
  `RATING_TYPE_MISMATCH`. Run PL-1566's items 6 and 13: each FAILS on the code (item 28's red);
  record, then edit both expectations to `RATING_TYPE_MISMATCH` citing the 18:27:10 entry
  (§"Write set" lists the file). Run again: PASS.
- [ ] **Step 6: Commit** with Task 7 Step 0's T3: `fix(score): an int or count output is a JSON integer, a non-integral value refuses the quote (RL-1567)`.

### Task 4: The contract (items 13–15)

- [ ] **Step 1:** Write item 14's guard. Run it against a planted schema (a temporary copy whose
  `outputs` admits `{"type": "number"}`, built inside the test): FAIL naming the path. Record.
- [ ] **Step 2:** Edit `scoring.schema.json:60` to the value schema Task 2 generates, and run
  `uv run python scripts/generate-contracts.py` then `--check` (exit 0).
- [ ] **Step 3:** Run `uv run pytest backend/tests/test_contracts.py -q -k "scoring or outputs"`: PASS.
- [ ] **Step 4: Commit.** `fix(contracts): no outputs value is a non-integer number (RL-1343 rule 4, FR-451)`.

### Task 5: The routes and the trace summary (items 16–18)

- [ ] **Step 1:** Append items 16 and 17; edit item 18's expectation. Run
  `uv run pytest backend/tests/test_score.py backend/tests/test_score_compare.py -q -k "decimal_output or float_path"`
  on a tree **before** Tasks 1–2 (a `git worktree` of the base, or by reverting locally and
  restoring): items 16, 17 FAIL on the number; item 18's new expectation FAILS on the 200. Record.
  (Needs the DB stack, per `dev-commands`.)
- [ ] **Step 2:** On HEAD: PASS. Edit `summarise_result`'s docstring (`traces.py:148-151`): the
  claim holds because `ScoringResult` refuses a float at construction (Task 2), not because of
  `_coerce_output_value`, which runs only in batch.
- [ ] **Step 3: Commit.** `test(score): decimal outputs on /score and /score/compare are exact strings (RL-1343)`.

### Task 6: `NFR-502` measured again (item 19)

- [ ] **Step 1:** In the lead's solo window, holding a gate slot
  (`flock -w 7200 -E 98 /tmp/slots/gate-1 -c …`, `dev-commands`), with nothing else heavy
  running, record `uptime`, `free -h` and both slot reads.
- [ ] **Step 2:** Write the two scripts to `RL-1365` DP-A2's specification (limb 1 and limb 3 in one,
  limb 2 in the other). If `SL-1367`'s ledger already holds `RL-1365`'s scripts, reuse them
  verbatim (`RL-1365` §"Observed, not ruled", first bullet) and say so. Run base and HEAD as the
  ruling orders. Record every row.
- [ ] **Step 3:** Apply the two stop conditions. A stop goes to the lead before Task 7.
- [ ] **Step 4:** Ledger: scripts inline with sha256 prefixes, both trees, the load readings after.

### Task 7: The spec text and the release note (item 20)

- [ ] **Step 0** *(pre-mint delta 1)*: apply `RL-1567`'s T3 to `03:929`, byte for byte, in the same commit as Task 3b's `_PER_QUOTE_CODES` line (`CLAUDE.md` §2). Then `grep -cF` its new text (1) and its find string (0).
- [ ] **Step 1:** If SL 9511 has merged and applied T2, record "no spec text: T2 applied by SL 9511
  at `<sha>`". Otherwise apply PL-1566's T2 from its `RL-`, byte for byte. A find string not
  found exactly once is a stop.
- [ ] **Step 2:** `python3 scripts/audit-docs.py`. Expected: the only `FAILED` line, if any, is
  check 31 for unminted working ids.
- [ ] **Step 3:** The release note paragraph into the ledger (it goes into the squash body at merge).

### Task 8: The gate and the ledger (items 21–23)

- [ ] **Step 1:** The full two-half gate through the gate-runner, holding a gate slot. The frontend
  half runs `pnpm --dir frontend install --frozen-lockfile`, `generate:api`, `lint`, `type-check`,
  `test` and `build`; record each rc, the tree, and `git diff --stat` of
  `frontend/src/api/generated/` before and after `generate:api` (it is untracked, so compare the
  two generated files by sha256).
- [ ] **Step 2:** The `LG-` ledger: Task 0's readings and the stored-data counts, every red with its
  printed line, every break, DP-1 and DP-2 as ruled, Task 6's rows, the release note, and
  `git diff --stat origin/main...HEAD` against §"Write set".

## Hand-off

1. The lead mints PL-1568 and SL 9500, and dispatches only after §"Activation needs" hold, in a
   separate activation PR.
2. On merge, `FD-1333` is discharged, and so is FD-1561's `/score` residue for `relativity` and
   `percentage` (DP-2 (ii)). The auditor closes both and names this slice.
3. *(Pre-mint delta 2: DP-3 ruled (a); the `SL-1409` row's dated correction is in this PR.)* **To the lead, on DP-3:** `PL-1364`'s Hand-off (`:1082-1086`) and the `SL-1409` row
   (`docs/roadmap.md:1435`) give opposite orders; whichever is decided, the other record is the
   one corrected (the roadmap row by the lead; `PL-1364` by a delta or not at all, since its
   hand-off already assumes (a)). Under (b), `SL-1367`'s executor re-reads `scoring.schema.json`
   and the generated contract at its dispatch tree, and its `NFR-502` base is a tree carrying
   this change.
4. **To the WK-675 planner:** an `outputs` value is `int | str | bool | null` or a nested map or
   list of those, never a non-integer number. A `decimal`-family value is a display string.

## Self-review

1. **Coverage of the ruling's scope clause, clause by clause:** see §"The maintainer's decision this
   plan rests on", the paragraph after the quotation.
2. **Coverage of `RL-1343` "What it obliges":** `_build_outputs` rules 3.1–3.4 (Task 1);
   `_coerce_output_value` checks, never `Decimal(repr(value))` (Task 3); `ScoringResult.outputs`
   and the contract, guard, `--check`, `NFR-502` (Tasks 2, 4, 6); the `summarise_result`
   docstring (Task 5 Step 2); the release note (§"Release note"); the stored-data check (Task 0
   Step 3). **Its Acceptance 1–6:** items 16–17; 3; 4; 5; 8; 10 and 14.
3. **Coverage of PL-1566 §"RL-1343's discharge" items 1–3 and Hand-off 3:** §"Why this plan exists".
4. **Repository literals read at `fb178c36`:** every line in §"Producers", §"Task 0 at planning
   time" and §"Write set"; FD-1561 at `d78f1235`'s probe lines; PL-1566 at `dc4f9c50` and its
   head `b0659358`; each other plan at the head named in the contention table.
5. **What was not executed.** No test or code was run; no probe. The sketch of `round_to_text` and
   the fixture names are read at `fb178c36`; item 4's engine exactness and the engine's
   acceptance of `result_type` `relativity`/`percentage` (FD-1561's probe says it did) are named
   for the executor to confirm in Step 2. A sketch that does not run as written is a plan defect
   to report, not to work around.
6. **The whole-valued blind spot is closed twice, at different layers:** at the producer (items 1,
   6) and in batch's check (item 11). The model-level refusal cannot see it, and item 10's control
   records that, so nobody later reads rule 4 as covering it.
7. **Pre-mint delta 1 coverage:** entry (1): items 25, 26, Task 3b Steps 3–4, write set (`_PER_QUOTE_CODES`), T3 (Task 7 Step 0); "the red asserts the HTTP status AND the code": items 25 and 26 assert 422 and `RATING_TYPE_MISMATCH`, and a 500 is recorded as the intermediate red; entry (2) "3.0 → 3": item 24, and "2.9999999999 … refused": item 25; the batch code: DP-4 and item 27.
8. **Pre-mint delta 2 coverage:** 18:25:42 entry: DP-3 (row, activation need 5, contention row,
   Hand-off 3, the roadmap correction); "PL-1364 DP-A3 is recorded as answered": the delta and the
   DP-3 row; the condition on `:1304-1320`: item 18 (`INTERNAL_ERROR`, no value, not a per-quote
   code); `:594` inverted citing `RL-1343`: item 9; the stop rule and `round_to_text`: unchanged;
   the docstring: Task 5 Step 2. 18:27:10 entry: DP-4's row, item 27, item 28, Task 3b Step 5.
