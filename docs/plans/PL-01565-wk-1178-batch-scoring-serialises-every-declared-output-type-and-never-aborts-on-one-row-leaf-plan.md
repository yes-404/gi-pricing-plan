---
id: PL-1565
family: plan
kind: leaf
title: WK-1178 — batch scoring serialises every declared output type and never aborts on one row (FR-254, FR-255): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-09            # original date 2026-10-05, set at the draft; minted 2026-10-09
owner: planner
tree: 5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1333, RL-1343, RL-923, RL-1263, PL-1371, PL-1364]
---

# WK-1178 — batch scoring serialises every declared output type and never aborts on one row, leaf plan

*(Minted 2026-10-09 as PL-1565 from working id 9509, in the D4 batch mint; citations of the ids minted in this batch, and of ids already minted on main, are re-pointed outside quoted text, quoted channel entries and code blocks, which stay as quoted; PL-1544 (the G2-b batch) are forward cites into batches not yet merged; PL 9574, PL 9593, PL 9609, PL 9610 are working ids not minted by any batch and stay working ids.)*

Filed under working id 9509 (this plan) and slice working id 9511 (its `SL-` row under WK-1178
in [`../roadmap.md`](../roadmap.md), `draft`). The lead reserved both in
`~/gi-pricing-plan.local/handover/eta.md` (row "SL 9511 / PL 9509", 5 Oct 17:58:59). The finding
it fixes is FD-1561 (draft #1204, branch `fd-9513-score-batch-serialisation`, read in
full at `0303d0bf4e102bafa241d643615635b0ab52b9c1`). Nothing here is minted. Every line number was
read at `origin/main` `5fe56b87`, the `tree:` above, unless another commit is named.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (pricing-core stays standalone),
> `spec-change` (Task 3, only from an `RL-`'s text), `dev-commands` (the two-half gate) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

## Goal

One row of a batch run can end the whole run. `_score_batch_row`
(`packages/pricing-core/src/pricing_core/rating/score.py:1081`) turns into an `"error"` row only
what is raised inside its `try` (`:1096-1100`, handlers `:1101-1115`). The two serialisers run in
the `return` after it: `_ladder_json(scored.premium_ladder)` (`:1122`) and
`_outputs_json(algorithm, scored.outputs)` (`:1123`). Anything they raise leaves the row,
`_score_batch_chunk` (`:1130-1132`), `score_batch` (`:1135`) and the Job loop
(`backend/src/app/worker/scoring_handlers.py:222-245`, which has no `try`). FR-255 says a run
"does not abort on individual failures unless the failure rate exceeds a declared threshold".

The commonest way to reach it is a declared output type. `_coerce_output_value` (`:950`) raises
for any type outside `_KNOWN_OUTPUT_TYPES = {money_minor, decimal, bool, string, date}` (`:947`,
`:964-965`). `int`, `count`, `relativity` and `percentage` save, compile and are served on
`POST /api/v1/score` (FD-1561's probe), and batch refuses them. FR-254 says batch uses "the
identical compiled bundle and code path as real-time scoring — never a separate 'batch
implementation' that could diverge".

**This slice does two things, in this order:**
1. **The row escape first.** Any exception from the serialisation after the `try` becomes that
   row's `"error"` row, and the run continues (FR-255). This does not depend on the type
   question, so it lands even if DP-1 is still open (activation need 3).
2. **The four declared types** (`int`, `count`, `relativity`, `percentage`), so that batch and
   `/score` serve one value per declared output (FR-254). Their JSON form is **DP-1, the
   maintainer's** (open).

**Architecture.** Only the batch half of `score.py` changes, unless DP-2 is ruled (i). The row
handler gets a second `try` around the two serialisers. `_coerce_output_value` gets a branch per
new type, chosen by DP-1. `_build_outputs` (`:729-758`), the shared real-time tail, is not edited
under the recommended DP-2 (ii). No `model-schema` shape changes, so the contract is not
regenerated.

**Tech stack.** Python 3.12, Polars, Pydantic v2, pytest. The backend is touched only by one
appended Job-level test.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-214 (`:83`), FR-227
(`:113`), FR-254 (`:166`), FR-255 (`:167`), and the `outputs_json` row of the batch output table
(`:692`). The rulings are `RL-923` §5(i) (`docs/rulings/RL-00923-…md:116-132`) and `RL-1343`
(rules 3–5, `:171-252`). The finding is FD-1561; its decimal half is `FD-1333`, decided by
`RL-1343`.

## The maintainer's decision this plan rests on, quoted

The maintainer (by delegation), in `~/gi-pricing-plan.local/channel/to-lead.md` (a local
channel file, so cited by its header), the entry headed
"2026-10-05 17:58:45 BST — FD 9513 (#1204 @0303d0bf): your decision ACCEPTED (MEDIUM, LATENT, WK-1178, its own fix slice after SL 9561); the row escape is the first red",
verbatim:

> Verified at origin/main (packages/pricing-core/src/pricing_core/rating/score.py): _score_batch_row's try is :1096-1103 (except NotImplementedError; except ValueError or RuntimeError), and "outputs_json": _outputs_json(algorithm, scored.outputs) is at :1123, OUTSIDE it. One bad row can abort the batch, against FR-255. The PR body has 0 session URLs and 0 "[the maintainer's (by delegation)]" [barred-word elision: the quoted entry names the word it greps for] (re-read after the PATCH).
> 1. ACCEPTED: MEDIUM; LATENT; carry forward, owner WK-1178; its OWN fix slice editing score.py AFTER SL 9561. Reserve the SL/PL ids; a planner drafts when a seat frees.
> 2. The fix plan's reds, in order: (1) the ROW ESCAPE first. ANY exception from _outputs_json (or anything else after the try) becomes that row's error row, and the run continues (FR-255). This does not depend on the type question, so it lands even if the type DP is still open. (2) the four types, with the JSON form of count, relativity and percentage as a DP for me in that plan (FR-254's "batch never diverges" is the reading; the plan proposes).
> 3. The decimal half stays with FD-1333 / OQ-1334 / RL-1343, not re-filed. The new fact (a whole-valued decimal reaches /score as a JSON INTEGER, a fractional one as a float; FD-1333/RL-1343 say only "float") goes into FD 9513's text as a related observation, cited to FD-1333. Whichever plan discharges RL-1343's clause must cover BOTH forms; FD 9513's fix plan checks whether that plan exists and names it.

Item 1 is §"Activation needs" 2. Item 2 is the order of Tasks 1 and 2 and DP-1. Item 3 is
§"RL-1343's discharge" below.

## Pre-mint delta 1 (2026-10-05): the decision points, ruled

The maintainer (by delegation) ruled DP-1, DP-2 and DP-3 in `to-lead.md`, in the entry headed
"2026-10-05 18:10:57 BST — PL 9509 (#1210 @dc4f9c50) DPs RULED: DP-1 (b), DP-2 (ii), DP-3 the class name; the RL-1343 leaf plan is reserved NOW".
The lead relayed it. Verbatim:

> The finding that _ladder_json (:1122) is ALSO outside the try, alongside _outputs_json (:1123): good. Task 1 covers anything after the try.
> DP-1: (b). int and count are a JSON INTEGER on both paths, and a non-integral value under them becomes that ROW's error. relativity and percentage use the DECIMAL STRING form (the RL-1343 rule, and 03:692 keeps lossy floats out). (c) is NOT taken, because OQ 9556 owns the type vocabulary at save; (d) is not taken.
> DP-2: (ii). The RL-1343 slice carries the /score half for relativity and percentage. Until it lands, FD-1333's divergence stands for those two types, and FD 9513's register cell names that residue and its discharger.
> DP-3: the exception class name, as today.
> RL-1343 HAS NO DISCHARGING PLAN, and its gate is met: YES, reserve the SL/PL ids now under WK-1178 and spawn a planner at the next free seat. Its scope: BOTH decimal forms (whole-valued, which today is a JSON integer, with its own red: 27 → "27.00" at dp 2; fractional, today a float), relativity and percentage on /score (DP-2 (ii)), and NFR-502's re-measure in the gate's own mode. It SERIALISES with SL 9511 on _coerce_output_value. As a breaking wire change, it runs the frontend half of the gate.
> Task 1 (the row escape) is dispatchable before the DPs, but it edits score.py, so it still runs AFTER SL 9561 in lane B order.
> Discrepancies: PL 9521 Step 1a citing FD 9513, and PL 9567's write-set table in delta 7: both pre-mint fixes, good.

**What this delta changes, at every site it reaches** ([`README.md`](README.md) rule 5):
- **DP table:** DP-1, DP-2 and DP-3 read RULED. The options and the reasons are kept as the
  record of what was weighed.
- **Status and activation need 3:** no decision point is open. Task 1 is still placed after
  SL-1427 (activation need 2), whether or not it goes before the other tasks.
- **Items 5–8:** confirmed as written for (b) and (ii). The note "if the ruling differs" no
  longer applies. Item 6 is DP-1's "a non-integral value … becomes that ROW's error". Item 7 is
  batch only, which is DP-2 (ii).
- **DP-3 (a):** items 1, 4 and 6 already assert the class name.
- **The RL-1343 plan is PL-1568, its slice SL-1569** (reserved by the lead; planner-1343
  is drafting it, per the lead's relay of 2026-10-05). §"RL-1343's discharge" and Hand-off 3
  name it. It serialises with this slice on `_coerce_output_value`, in both directions:
  whichever slice merges second merges `main` and rebases its branch onto the other's.
- **Activation need 4 is kept and made unconditional.** DP-1 (b) needs spec text
  (§"The spec text DP-1 (b) owes", below).

### The spec text DP-1 (b) owes

**Yes, spec text is needed.** Two places are affected:
- **`03:692`**, the `outputs_json` row of the batch output table (`03` §4), is the published
  column contract. `RL-923`'s title calls it "a published data contract two modules read".
  The row names the form of only two types ("`money_minor` as a JSON number, `decimal` as a
  JSON string"), and then says "refusing, not stringifying, anything else". After this slice,
  batch writes four more types. Two of them (`relativity` and `percentage`) are written as
  strings. A reader of the row cannot learn that, and "not stringifying" reads against it.
  FD-1561 records the gap: "The text does not say how the four types must be written".
- **FR-214** (`03:83`) has a dated clause from `RL-1343` that fixes `decimal` "on every scoring
  path". No requirement says how an `int`, `count`, `relativity` or `percentage` output is
  served. DP-1 (b) decides that for both paths, so the requirement needs a clause that says it.

**The T-texts owed, both carried by one `RL-`** (a decision-maker drafts it; this plan drafts
none):
- **T1, the `03:692` row.** The row names the form of every type batch writes:
  - `money_minor`, `int` and `count` as a JSON integer;
  - `decimal`, `relativity` and `percentage` as a JSON string;
  - `bool` as a JSON boolean;
  - `string` and `date` as a JSON string.

  A value that does not match its declared type makes that row an `"error"` row with the
  exception class name as its code (DP-3). No type is ever stringified as a fallback. **This
  slice applies T1** (Task 3).
- **T2, a dated clause on FR-214.** An output declared `int` or `count` is a JSON integer on
  every scoring path. One declared `relativity` or `percentage` takes FR-214's `decimal` form
  on every path. The clause states the carriers:
  - batch is delivered by SL-1566;
  - `/score` and `/score/compare` are delivered by SL-1569 (DP-2 (ii)). Until then `/score`
    serves the engine's number for those two types (`FD-1333`'s divergence, named in FD-1561).

  **T2 is applied once, by whichever of SL-1566 and SL-1569 merges first.** The two serialise
  on `_coerce_output_value`. The second slice applies nothing, and its dispatch record says so.

## Pre-mint delta 2 (2026-10-05): integrality, and `RL-1567` as the activation-need-4 `RL-`

The maintainer (by delegation) ruled `RL-1567`'s (#1212) second open question in
`~/gi-pricing-plan.local/channel/to-lead.md`, in the entry headed
"2026-10-05 18:20:06 BST — RL 9498 (#1212 @7e71b040): both open questions RULED as recommended, with one precision each".
The lead relayed it. Its item (2), verbatim:

> (2) Is a whole-valued float integral? YES. Integral means EXACT equality with its integer part (value == int(value)) with NO tolerance; it serialises as the integer (3.0 → 3). 2.9999999999 is NOT integral and is refused. T1 and T2 state it in those words, and each slice has one red for 3.0 → 3 and one for a near-integer refused.

**What this delta changes, at every site it reaches** ([`README.md`](README.md) rule 5):
- **Items 12 and 13 are added** (§"Acceptance Standard", after item 8), one red each way, and
  Task 2 gains Step 3b. Items 5–8 are unchanged.
- **The `int`/`count` branch sketch** (Task 2 Step 3) refused every non-`int`, so a whole-valued
  `3.0` would be an error row. It now admits a `float` equal to its integer part and writes that
  integer. Step 3b states the replacement.
- **Activation need 4's `RL-` is `RL-1567`** (#1212, read at `c2c70690`). It carries T1 (`03:692`)
  and T2 (FR-214), and also T3 (`03:929`), which is SL-1569's (PL-1568), not this slice's. This
  slice applies T1 and, unless SL-1569 merged first, T2, byte for byte from the minted record.
- **A note, not a change, for the batch code of a non-integral value.** `RL-1567` item 8 keeps
  the exception class name in batch. PL-1568 (#1213) raises DP-4 against that clause: SL-1569's
  producer refuses a non-integral `int`/`count` value with the coded `RATING_TYPE_MISMATCH` inside
  `_build_outputs`, which batch reaches inside the row `try` (`score.py:1096-1100`), and
  `_batch_error_code` (`:1006-1018`) returns the code. So once SL-1569 merges, the row's
  `error_code` for item 6 and item 13 reads `RATING_TYPE_MISMATCH` unless DP-4 is ruled (b).
  **This slice's reds stand as ruled (the class name)**; if SL-1569 merged first, the dispatch
  record restates items 6 and 13 against DP-4's ruling.

## Pre-mint delta 3 (2026-10-05): the exact-equality check replaces `isinstance`; the class name holds until SL-1569

The maintainer (by delegation), in `~/gi-pricing-plan.local/channel/to-lead.md`, relayed by the
lead, verbatim. The entry headed "2026-10-05 18:26:46 BST — RL 9498 @c2c70690: accepted, with ONE pre-mint fix in T1; the isinstance catch is good":

> T2 and the new T3 at 03:929: accepted as drafted.
> T1: my 18:20:40 entry said "if the plan's batch side raises a dedicated exception class for it, the class name is stated in T1". PL 9509 raises NO dedicated class and ASSERTS ValueError. So T1 STATES ValueError, in a phrase like "the row's error_code is ValueError (FR-255's class-name rule)", rather than leaving it to SL 9511. Otherwise the spec is silent on a code the tests pin, and a later class change would move the wire without a spec change. One sentence, pre-mint.
> PL 9509 Task 3 item 6's "isinstance(value, int)" break would have refused 3.0 against the exact-equality ruling: a good catch. Its fix in planner-1343's delta must also turn the break into a red for 3.0 → 3 (the mutation that proves the exact-equality code, not isinstance, is what runs).

The entry headed "2026-10-05 18:27:10 BST — RL 9498 STOP: (a) ADOPTED; my 18:20:40 "batch keeps the class name" is SUPERSEDED once SL-1569 lands":

> (a). The batch path runs _build_outputs inside _score_batch_row's try (score.py:1096-1100), and _batch_error_code (:1006-1018) maps a coded "CODE: msg" ValueError to CODE. So with ONE producer (SL 9500's check in _build_outputs), batch rows code the fault RATING_TYPE_MISMATCH, the same as /score: FR-254 holds, and the codes agree. My 18:20:40 "NAMED, NOT CHANGED: batch keeps the class name" described the state BEFORE SL 9500 and is SUPERSEDED for after it; the RL quotes both entries.
> Amendments, pre-mint, ONE DM commit: T2 and T3's batch clause = "until SL 9500 merges, batch codes it ValueError (SL 9511's _coerce_output_value, the class-name rule); after, RATING_TYPE_MISMATCH, from the single producer"; item 8 and the Acceptance to match. My 18:26:46 T1 fix ("T1 states ValueError") becomes the same time-bounded sentence in T1.
> PL 9499 marks DP-4 ruled (a). SL 9500 RE-EXPECTS SL 9511's class-name red to RATING_TYPE_MISMATCH, citing this entry, with a batch red asserting the row's error_code is RATING_TYPE_MISMATCH and the run continues. PL 9509 marks its class-name red "until SL 9500".
> (b) is refused (a path flag in the shared builder is the divergence FR-254 forbids).

**What this delta changes, at every site it reaches** ([`README.md`](README.md) rule 5):
- **Item 6 and Task 2 Step 5** (marked in place): the `int`/`count` check is
  `value == int(value)` with no tolerance, and the integer is written (`RL-1567`, #1212 @`c2c70690`,
  T1/T2). Item 6's break removes **that** check. A second break is added, the one the 18:26:46
  entry asks for: reverting the check to `isinstance(value, int)` turns item 12 (`3.0` → `3`) red,
  which proves the exact-equality code is what runs.
- **The Task 2 Step 3 sketch** is marked superseded in place by Step 3b's branch, written out.
- **Items 6 and 13's code is time-bounded** (the 18:27:10 entry, DP-4 (a) of PL-1568):
  `error_code == "ValueError"` **until SL-1569 merges**; after it, `RATING_TYPE_MISMATCH`, from the
  single producer. SL-1569 (PL-1568, #1213, its item 28) re-expects both; this slice asserts
  `ValueError`, and if SL-1569 merged first, the dispatch record restates both items with
  `RATING_TYPE_MISMATCH`.
- **T1 states the code** (the 18:26:46 entry): `RL-1567`'s T1 names `ValueError`, time-bounded
  as the 18:27:10 entry words it, rather than leaving the class to SL-1566. This slice applies T1
  as minted. (`RL-1567` @`c2c70690` item 8 said T1 "leaves the exact class to SL-1566"; the
  18:26:46 entry replaces that, and the decision-maker amends the record pre-mint.)

## Status

`draft`. ~~**DP-1 is open, the maintainer's.** DP-2 and DP-3 carry recommendations and are also
the maintainer's. Task 1 does not depend on any of them.~~ *(Pre-mint delta 1, 2026-10-05:
**DP-1 (b), DP-2 (ii) and DP-3 (a) are ruled** (18:10:57 BST). No decision point is open.)* The
plan moves to `active` only through a separate activation PR, after every activation need
below holds.

### Activation needs, in order

1. **FD-1561 minted** (#1204).
2. **SL-1427 merged** (the emergency slice, PL-1426, #1196). It edits `score_one` and
   `_score_context_sync` in `score.py` (its write set, read at `68b2f860`). The ruling's item 1
   places this slice after it.
3. **DP-1 ruled** (and DP-2, DP-3 with it). **Task 1 may be dispatched before this**, as its
   own commit, if the lead cuts it so (the ruling's item 2: "it lands even if the type DP is
   still open"). Tasks 2–3 wait for DP-1. *(Pre-mint delta 1: **held**, all three ruled at
   18:10:57 BST. Task 1 is still placed **after SL-1427** (need 2), because it edits
   `score.py`. The ruling says so in its own words.)*
4. **The `RL-` carrying T1 (the `03:692` row) and T2 (FR-214's dated clause) is minted**
   (§"The spec text DP-1 (b) owes"). This plan drafts no spec text. *(Pre-mint delta 1: this
   need was conditional, "If DP-1 changes a spec text". DP-1 (b) does, so the need is now
   unconditional and is kept.)* *(Pre-mint delta 2: that `RL-` is `RL-1567`, #1212.)*
5. **The maintainer's dispatch GO, and this plan made `active` by a dated line** in a separate
   activation PR. The dispatch record writes `RL-1445`'s (#1162) same-Work lines for
   every WK-1178 slice in flight beside this one (§"Write set").

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means: the named test was run, and it failed **for the stated cause**, before the code that turns
it green existed. A test that fails with the right status but another cause is a plan defect
([`README.md`](README.md) rule 2). The ledger records each red with its printed failure line.
`P` is `packages/pricing-core/tests/test_rating_score_batch_outputs.py` (new). `B` is
`backend/tests/test_scoring_handlers.py` (appended).

**Task 1 — the row escape (`uv run pytest packages/pricing-core/tests/test_rating_score_batch_outputs.py -q -k escape`)**

1. `test_a_row_whose_serialisation_raises_is_an_error_row_and_the_batch_continues`, parametrised
   over three injections on the second of four rows: `_outputs_json` raising `ValueError`,
   `_outputs_json` raising `TypeError`, and `_ladder_json` raising `KeyError`. Each run returns
   4 rows. The injected row has `outcome == "error"`, `error_code` equal to the exception's class
   name, and `premium_ladder_json`, `outputs_json` both `None`. The other three rows have
   `error_code is None`, and their `premium_ladder_json` and `outputs_json` are byte-identical
   to an uninjected run's. **Red:** the injected exception is raised out of
   `score_batch(...).collect()` (pytest prints `ValueError: injected serialisation failure`,
   and the same for the other two), not an assertion failure. `TypeError` and `KeyError` are
   in the set because the ruling says "ANY exception": the existing row handler catches only
   `ValueError` and `RuntimeError` (`:1103`).
2. `test_an_error_row_from_serialisation_carries_no_value`. The injected exception's text is
   `"premium_in=SENTINEL-9513"`. The error row's `error_message` does not contain
   `SENTINEL-9513` (NFR-499; `_batch_error_code`, `:1006-1018`). **Red:** the exception leaves
   `score_batch`, as in item 1.
3. `test_not_implemented_still_propagates_from_serialisation` (control, not a red). An injected
   `NotImplementedError` from `_outputs_json` is raised out of `score_batch`, as one raised
   inside the first `try` is today (`:1101-1102`). It passes before and after Task 1. **Break:**
   catching `NotImplementedError` in the new handler turns it red; record that run.
4. **B:** `test_a_row_whose_serialisation_raises_does_not_end_the_job`. Mirrors
   `test_the_unset_default_means_no_rate_based_abort_but_counts_still_accrue` (`B:361-388`),
   with no bad input row, and with `pricing_core.rating.score._outputs_json` monkeypatched to
   raise `ValueError` on its second call. The Job succeeds. `error_counts == {"ValueError": 1}`,
   `outcome_counts["quoted"] == 3`, `row_count == 4`. **Red:** the Job fails with the injected
   `ValueError` (the handler loop has no `try`). Run:
   `uv run pytest backend/tests/test_scoring_handlers.py -q -k serialisation_raises` (needs the
   DB stack, per `dev-commands`).

**Task 2 — the four declared types (`uv run pytest packages/pricing-core/tests/test_rating_score_batch_outputs.py -q -k declared`)**

The items below are written for **DP-1 (b) with DP-2 (ii)**, the recommendation. If the ruling
differs, the dispatch record restates items 5–8 from the ruled option before Task 2 starts, and
the restatement is in the ledger. *(Pre-mint delta 1: the ruling is (b) and (ii), as written. No
restatement is needed.)*

5. `test_an_integer_declared_output_is_the_same_json_integer_in_batch_and_on_score`,
   parametrised over `int` and `count`. The algorithm is Task 1.4's fixture plus one `expression`
   step `driver_age` (result type = the declared type) and an `output` step `probe_out` of that
   type. For each of the 10 `_contexts(10)` rows, `json.loads(outputs_json)["probe_out"]` equals
   `json.loads(score_one(...).model_dump_json())["outputs"]["probe_out"]`, and both are
   `int` (and not `bool`). **Red** (after Task 1): every row has `outcome == "error"` and
   `error_code == "ValueError"` (the refusal at `:964-965`, now caught by Task 1).
6. `test_a_non_integral_value_for_an_integer_output_is_an_error_row`, parametrised over `int` and
   `count`. The expression is `driver_age * 1.1`, whose result is fractional (the probe: 19.8 at
   age 18). Batch gives an `"error"` row with `error_code == "ValueError"` for that row, and the
   batch completes. It never writes a float or a string. **Red:** the same `"error"` row, but
   from the type refusal (`:964-965`) rather than from the value check. So this item is red
   first only by the **break** below; record it. ~~**Break:** an `int` branch that returns the
   value without the `isinstance(value, int)` check writes `19.8`, and the item fails.~~
   *(Pre-mint delta 3: the check is exact equality, `value == int(value)`, no tolerance, writing
   the integer (`RL-1567` T1/T2). **Break:** removing **that** check writes `19.8`, and the item
   fails. **Second break:** reverting the check to `isinstance(value, int)` refuses `3.0`, and
   item 12 fails. The code is `"ValueError"` **until SL-1569 merges**, then
   `RATING_TYPE_MISMATCH` (the 18:27:10 entry).)* (FD-1561
   recorded `/score` serving this value as a JSON float. That is the divergence `RL-1343` rule 4
   closes on `/score`. See §"RL-1343's discharge".)
7. `test_a_fractional_declared_output_is_a_decimal_string_in_batch`, parametrised over
   `relativity` and `percentage`. The expression is `driver_age * 1.5` (whole, 27 at age 18)
   and `driver_age * 1.1` (fractional, 19.8 at age 18). Batch writes a JSON string equal to
   what the `decimal` branch writes for the same value today (`:972-974`). **Red** (after
   Task 1): `outcome == "error"`, `error_code == "ValueError"`. Under DP-2 (ii) this item
   asserts **batch only**: `/score` keeps serving a number for these two types until the
   `RL-1343` slice ships one producer for `decimal`, `relativity` and `percentage`. That is
   FD-1333's divergence, extended by name to two more types, with the same discharge.
8. `test_the_known_output_types_name_every_numeric_family_member`. `_KNOWN_OUTPUT_TYPES` is a
   superset of `compile._NUMERIC` (`compile.py:57`) plus `bool`, `string` and `date`. **Red:**
   the set difference `{"int", "count", "relativity", "percentage"}` is printed. This item keeps
   the save-time vocabulary and the batch serialiser on one list, which is FD-1561's third
   fix need.

**Integrality, one red each way (pre-mint delta 2; `uv run pytest packages/pricing-core/tests/test_rating_score_batch_outputs.py -q -k integral`)**

12. `test_a_whole_valued_float_under_an_integral_type_is_its_integer_in_batch`, parametrised over
    `int` and `count`. The expression gives the engine's `float` `3.0` (`3.0 + 0 * driver_age`, or
    `driver_age / 6` at age 18 if the engine returns that as a float; Step 3b reads which).
    `json.loads(outputs_json)["probe_out"] == 3`, its type is `int`, and the raw `outputs_json`
    text holds `"probe_out": 3` with no `.`; `error_code is None`. **Red** (after Task 2 Step 3
    as first sketched): an `"error"` row with `error_code == "ValueError"` (the `isinstance(value,
    int)` refusal of `3.0`).
13. `test_a_near_integer_under_an_integral_type_is_an_error_row`, parametrised over `int` and
    `count`. The expression gives `2.9999999999`. That row is an `"error"` row with `error_code`
    equal to the exception class name (`"ValueError"`, DP-3; `RL-1567` item 8; *until SL-1569
    merges, then `RATING_TYPE_MISMATCH`, pre-mint delta 3*), the batch
    completes, and no float or string is written. **Red:** none against Task 2 Step 3 as first
    sketched (it already refuses a float); so this item is red first only by the **break**: a
    branch deciding integrality with a tolerance (`abs(value - round(value)) < 1e-9`) writes `3`
    and the item fails. Record that run.

**Unchanged and the gate**

9. `uv run pytest packages/pricing-core/tests/test_rating_score_batch.py -q` passes unchanged:
   the byte-identity test (`:157`) and `test_one_invalid_row_does_not_stop_the_batch`
   (`:296-316`) are not edited.
10. The full two-half gate (`CLAUDE.md` §11) is green on the merge tree, through the
    gate-runner, holding a gate slot. `python3 scripts/audit-docs.py` and
    `uv run python scripts/req-coverage.py` are part of it.
11. `git diff --stat origin/main...HEAD` lists only paths in §"Write set".

## Global Constraints

- **Money is integer minor units or `Decimal`, never float** (`CLAUDE.md` §7). No branch added
  to `_coerce_output_value` returns a `float`. `json.dumps` never receives one from it.
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2; ADR-703). The new handler
  imports nothing.
- **No value reaches an error row** (NFR-499). Every new error row goes through
  `_batch_error_code` (`:1006-1018`), which keeps only `safe_error_detail`'s text.
- **`score_batch` stays a pure chunked transform** (FR-254's clarification, `03:166`). The
  abort threshold stays the handler's (FR-255, `RL-889`); this slice adds none.
- **No spec text is written by the executor.** A `docs/specs/` byte comes only from an `RL-`'s
  text block (activation need 4).
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13). Items 3, 6 and 8 name
  the break that turns them red.
- **Shared files** (`RL-1263`; `docs/process/delivery-process.core.json`
  `guards.parallelism.build_slices_across_works.no_shared_files`): §"Write set" classifies each
  path.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-255 | The structural half: a row's serialisation failure is that row's typed `"error"` row, and the run continues | `req("FR-255")` on items 1–4, 6 |
| `03` | FR-254 | Batch writes the value `/score` serves for `int` and `count`, and the vocabulary is one list (DP-1) | `req("FR-254")` on items 5, 8 |
| `03` | FR-214 | Read. A declared output of type `relativity` or `percentage` is written by batch (DP-1, DP-2) | `req("FR-214")` on item 7 |
| `03` | FR-227 | Read only. The save-time vocabulary is `compile._NUMERIC`; PL-1562 (#1202) edits its rule | none new |
| `03` | NFR-499 | An error row from serialisation carries no input value | `req("NFR-499")` on item 2 |

**Findings.** FD-1561 (MEDIUM, LATENT, owner WK-1178) is discharged on merge, by its
own event: "a merged change to `_coerce_output_value` and `_score_batch_row`". The auditor closes
it. Under DP-2 (ii), FD-1561's `/score` half for `relativity` and `percentage` is carried to the
`RL-1343` slice, and the closure names that.

**Not in scope.**
- `RL-1343` rules 3 and 4 (the exact decimal string on `/score`, `ScoringResult` refusing a float):
  the `RL-1343` slice, unless DP-2 is ruled (i).
- The save-time type rule: PL-1562 (#1202).
- What the Job's generic failure path stores: `FD-1217`.

### Task 0 at planning time (read, not run)

Read at `5fe56b87`. Nothing was executed.
- `_KNOWN_OUTPUT_TYPES` (`:947`); `_coerce_output_value` (`:950-988`, refusal `:964-965`,
  `money_minor` `:966-971`, `decimal` `:972-974`, `bool` `:975-980`, `string`/`date`
  `:981-987`); `_outputs_json` (`:991-1003`); `_batch_error_code` (`:1006-1018`).
- `_score_batch_row` (`:1081-1127`): `try` `:1096-1100`, `except NotImplementedError: raise`
  `:1101-1102`, `except (ValueError, RuntimeError)` `:1103-1115`, the `return` with
  `_ladder_json` (`:1122`) and `_outputs_json` (`:1123`). `_score_batch_chunk` (`:1130-1132`).
- `_build_outputs` (`:729-758`): a non-rung, non-`money_minor` output is `result[name]` unchanged
  (`:756-757`).
- `scoring_handlers.py:222-245`: the chunk loop calls `score_batch(...).collect()` (`:231`) with
  no `try`.
- `compile.py:57`: `_NUMERIC = {int, decimal, money_minor, relativity, percentage, count}`.
- `model_schema/rating.py:225-247`: `AlgorithmOutput.type` is `RatingResultType`, a string that
  refuses only `float`.
- `safe_error_detail` (`pricing_core/safe_error.py:119-125`) returns `""` for a plain exception,
  so `_batch_error_code` gives `(ClassName, ClassName)`.
- The test fixtures: `_decimal_output_algorithm_payload` and `_DecimalOutputResolver`
  (`test_rating_score_batch.py:73-122`), `_contexts`, `_ctx_to_row` (`:42-70`).
- `decimal.InvalidOperation` is not a `ValueError` subclass (checked with the repository's
  Python, `issubclass` → `False`). That is one real way a non-`ValueError` could come out of the
  `decimal` branch's `Decimal(repr(value))` (`:973`).

### Write set, and its contention (`RL-1263`, `RL-1445`)

| Path | Change |
|---|---|
| `packages/pricing-core/src/pricing_core/rating/score.py` | edited: `_score_batch_row` (`:1081-1127`), a second `try` around `_ladder_json` and `_outputs_json`; `_KNOWN_OUTPUT_TYPES` (`:947`) and its comment (`:943-946`); `_coerce_output_value` (`:950-988`), its docstring and one branch per DP-1; `_outputs_json`'s docstring (`:992-995`). Under DP-2 (i) only, also `_build_outputs` (`:729-758`) |
| `packages/pricing-core/tests/test_rating_score_batch_outputs.py` | added: items 1–3, 5–8 |
| `backend/tests/test_scoring_handlers.py` | appended: item 4 |
| `docs/specs/03-rating-engine.md` the `outputs_json` row (`:692`); the FR-214 row (`:83`) | ~~only if an `RL-` carries text (activation need 4)~~ *(pre-mint delta 1)* T1 on the `:692` row; T2 on the FR-214 row unless SL-1569 merged first (activation need 4, Task 3). Each is a different row from SL-1427's FR-213 (`:82`) |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md`; `docs/roadmap.md` (this slice's row) | added; regenerated; activation and closing lines |

**Contention.** **Snapshot:** every open PR at `origin/main` `5fe56b87`, read 2026-10-05 between
17:30 and 18:00 BST. Each plan file each PR adds was grepped on its branch for `score.py` and
`scoring_handlers`, then the hits were read for write or read. 15 plans mention one of the two
files; the ones that write or read either are below. The classes are those of `no_shared_files`
(`forbidden`: "both_change_same_existing_function_class_method_spec_section_or_policy_table").

| Other slice (Work; source read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **SL-1427**, PL-1426, the emergency slice (#1196 @`68b2f860`; WK-1178) | `score.py`; `test_scoring_handlers.py` | adds `_check_no_shadowed_produced_names`; edits `score_one` and `_score_context_sync` (one call each); appends its batch red to `test_scoring_handlers.py` | `_score_batch_row`, `_coerce_output_value`, `_KNOWN_OUTPUT_TYPES`; appends item 4 | different definitions; append-only on the test file → **ordered first** by the ruling (activation need 2). Not concurrent |
| **PL-1435 / SL-1436**, the FD-1425 fix (#1193 @`67137918`; WK-673) | `test_scoring_handlers.py` | appends a test. Its delta withdraws its `score.py` edit ("this plan no longer edits `score.py` at all"); its write-set table still lists one | appends item 4 | append-only → **allowed one-sided**; the dispatch record names the path. If its `score.py` row is reinstated, re-check: it named `score_one`/`_score_context_sync`, not ours |
| **PL-1562 / SL-1563**, money_minor closed at save (#1202 @`6e2d05cc`; WK-1178) | none written by both; it **reads** `score.py` (`:729`, `:947`, `:950`, `:991-1002`) in Task 0 Step 3 and Step 1a | edits `compile.py` `_compatible` and callers | reads `compile._NUMERIC` (item 8) | **no shared write → concurrent allowed** (`RL-1445` (a), (b)). Its OQ-1560 decision (A1 + B3) narrows which producers reach an `int`/`count` output; it does not change `_NUMERIC`. Its Step 1a (an `int`/`count` → `decimal` comparison) does **not** cite FD-1561 at `6e2d05cc`: `grep -c 9513` prints 0 |
| **PL-1447**, the FD-1420 fix (#1145; WK-673) | `score.py` | adds `_check_as_at_values`; edits `score_one`, `_score_context_sync` (one call each) | `_score_batch_row`, `_coerce_output_value`, `_KNOWN_OUTPUT_TYPES` | different definitions, one file → **allowed one-sided**, the dispatch record naming each definition |
| **PL 9609**, WK-1250 S3 (#1173; WK-1250) | `score.py` | rewrites `_check_purpose_mount` (`:395-422`) and its two calls (`:898`, `:1063`) | as above | different definitions → **allowed one-sided** |
| **PL-1520**, the F35 remedy (#1051; WK-1178) | `score.py` | adds `reproduce_traced`; edits `_build_trace` and `build_scoring_result` | as above; `_build_outputs` only under DP-2 (i) | different definitions → **allowed one-sided**. Under DP-2 (i), `build_scoring_result` calls `_build_outputs`: re-check at dispatch |
| **A-2**, PL-1464 (#1178 @`176a6a75`; WK-1178) | `score.py` | the module docstring's item 2 (`:33-41`) only | not the docstring | different text → **allowed one-sided** |
| **S7**, `SL-1391` / `PL-1419` (`active`; WK-673) | none | rate tables and `worker/rate_table_handlers.py` | — | none |

Every other open plan names neither file, or reads it only (PL-1501, PL-1544, PL-1452 read
`score.py` or `scoring_handlers.py`; PL 9610, PL-1465, PL 9574, PL-1454 do not touch them). No
open plan edits `_score_batch_row`, `_outputs_json`, `_coerce_output_value`,
`_KNOWN_OUTPUT_TYPES`, `_build_outputs` or `scoring_handlers.py:222-245`. **The `RL-1343` slice
has no plan** (§"RL-1343's discharge"); when it is planned it edits `_build_outputs` and
`_coerce_output_value`'s `decimal` branch, so it **serialises** with this slice on
`_coerce_output_value`.

### Size

About half an executor day. One new test module, one appended Job test (needs the DB stack),
one pricing-core function restructured and one extended. One full two-half gate run. No NFR is
measured, so the slice need not run exclusive.

## RL-1343's discharge

**No plan discharges `RL-1343` at this tree, and none is open.** Evidence:
- `PL-1371` (`:251`): "RL-1343 decimal-output fix … **no leaf plan yet**".
- `PL-1364` (`:766`): "The `RL-1343` rule-4 slice (WK-1178, not yet planned)". PL-1520 (#1051)
  says the same.
- The `SL-1409` row (`docs/roadmap.md:1435`) orders lane B "… → this slice → the `RL-1343`
  decimal fix → FD-1335 Part A". `SL-1409` is closed; no `RL-1343` row exists under WK-1178.
- Its gate is met: `RL-1343` §5 puts it "after WK-674 Slice 3 merges", and `SL-1345` is
  `closed` (`docs/roadmap.md:935`).
- No open PR adds a plan for it: every plan file in an open PR was grepped for `RL-1343`; the
  hits cite it as a guard or a later slice (PL 9593, PL-1525, PL-1520), never as their scope.

**What that plan must cover, when it is written** (the ruling's item 3):
1. **Both forms of a `decimal` output.** A whole-valued `decimal` reaches `/score` today as a
   JSON **integer** (FD-1561's probe: `driver_age * 1.5` at age 18 → `27`, JSON type `int`),
   and a fractional one as a JSON **float** (`driver_age * 1.1` → `19.8`). `FD-1333` and
   `RL-1343` say only "float". Batch writes `"27"` and `"19.8"` (`Decimal(repr(value))`,
   `:973`), neither of which is `RL-1343` rule 3's form (exactly `dp` digits: `"27.00"`,
   `"19.80"` at `dp` 2). **Rule 4's check refuses a `float`; a whole-valued `decimal` is a
   Python `int` and passes a float-only check.** So that plan needs a red on a whole-valued
   `decimal` output on both paths, not only a fractional one.
2. **Under DP-2 (ii), `relativity` and `percentage` too**, with the same producer, rounding and
   form as `decimal` on `/score`. Item 7 then changes from "batch only" to both paths.
3. It serialises with this slice on `_coerce_output_value` (§"Write set").

The lead names that plan's working id when it is reserved. Until then this section is the carrier
of the obligation, and Hand-off 3 repeats it. *(Pre-mint delta 1, 2026-10-05: reserved. That plan
is **PL-1568 / SL-1569** (planner-1343 is drafting it). The ruling of 18:10:57 BST
sets its scope: both decimal forms with their own red (27 → "27.00" at dp 2), `relativity` and
`percentage` on `/score`, `NFR-502`'s re-measure in the gate's own mode, and the frontend half
of the gate. It **serialises** with SL-1566 on `_coerce_output_value`.)*

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | **The JSON form of `int`, `count`, `relativity` and `percentage` outputs**, on batch and `/score`. Today `/score` serves each as the engine's raw value (`_build_outputs` `:756-757`; FD-1561's probe: a JSON integer for a whole value), and batch refuses all four (`:964-965`). FR-254 (`03:166`) says the paths never diverge; `03:692` says `outputs_json` is "total over every `AlgorithmOutput.type` this path can produce"; `RL-923` §5(i) rules "total over the value types the rating path can produce" and a loud failure on an unnamed type. No text says how these four are written | **(a)** A JSON number on both paths, as `/score` serves today: batch writes the value unchanged. **(b)** `int` and `count` as a JSON integer on both paths (a non-integral value is that row's error); `relativity` and `percentage` as a decimal string, the `decimal` form, on both paths. **(c)** Close the vocabulary at save: a top-level `AlgorithmOutput` may not declare the four (a sub-graph output port still may: `test_sub_graph.py:25`), and batch keeps refusing them. **(d)** All four as strings on both paths | **(b).** (a) puts a float in `outputs_json`, which `03:692` exists to prevent ("an exact `Decimal` and a lossy `float` cannot be confused"), and `RL-1343` rule 4 already rules that `ScoringResult` refuses a float anywhere in `outputs`: a `relativity` of 1.15 served as a number would then be refused on `/score`. So a fractional type cannot be a JSON number, and (a) fails for two of the four. (c) is a contract change for algorithm authors that FR-214 ("may include additional named outputs") does not ask for, and it overlaps OQ-1560 (#1200), decided as A1 + B3, which allows these types and decides only which producers reach them. (d) writes an integer as a string, unlike `money_minor` (a JSON number, `03:692`), for no reason. (b) follows the two precedents: integral values are JSON integers as `money_minor` is (`RL-1329` §4), and fractional values are strings as `decimal` is (`RL-1343`). Liveness is none (FD-1561 §"Liveness"), so no committed consumer changes | **RULED (b)** by the maintainer (by delegation), 2026-10-05 18:10:57 BST (§"Pre-mint delta 1"); (c) not taken because OQ-1560 owns the type vocabulary at save, and (d) not taken | Task 2, item 5–8 |
| **DP-2** | **Only under DP-1 (b): who carries the `/score` half for `relativity` and `percentage`.** `/score` serves them as numbers today; (b) makes them strings there, which is `RL-1343` rule 3's producer | **(i)** This slice: `_build_outputs` writes the exact string for `decimal`, `relativity` and `percentage`, which discharges `RL-1343` rule 3 here. **(ii)** The `RL-1343` slice: this slice writes them in batch with the `decimal` branch's form, and that slice gives all three one producer on both paths | **(ii).** One producer, one breaking served-type change, one release note, one `NFR-502` re-measure (`RL-1343` §5), in one slice. (i) widens this slice into `_build_outputs` and `RL-1343` rules 3 and 4 (`model_schema/scoring.py`, `docs/contracts/`, `test_contracts.py`), which the ruling's item 3 keeps with `FD-1333`. The cost of (ii): `relativity` and `percentage` keep FD-1333's divergence (string in batch, number on `/score`) until that slice merges. Liveness is none, so nothing reads it | **RULED (ii)** by the maintainer (by delegation), 2026-10-05 18:10:57 BST. The `RL-1343` slice is SL-1569 / PL-1568| Task 2, item 7 |
| DP-3 *(not blocking)* | **The `error_code` of a row whose serialisation fails.** FR-255 lists typed errors: contract violation, reference miss, table miss, constraint decline, model failure. A serialisation failure is none of them | **(a)** The exception's class name, as `_batch_error_code` gives any uncoded error today (`:1018`). **(b)** A new registered code, for example `OUTPUT_NOT_SERIALISABLE`, with a dated FR-255 clause and an `03` error-code row | **(a).** After Task 2 the only remaining cause is an engine value that does not match its declared type (item 6), which is a defect to see in `error_counts`, and the class name already shows it. (b) needs a ruled spec text for a case that should not occur | **RULED (a)**, "the exception class name, as today", by the maintainer (by delegation), 2026-10-05 18:10:57 BST | none (items 1, 4, 6 assert (a); under (b) the dispatch record restates them) |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm each activation need. Quote DP-1's (and DP-2's, DP-3's) ruling (held, 18:10:57 BST) into the
  ledger. If Task 1 is dispatched before DP-1, record that, and stop after Task 1.
- [ ] **Step 2:** Re-read §"Task 0 at planning time" at the dispatch tree (SL-1427 will have
  moved the line numbers of `score.py`). Record the new numbers.
- [ ] **Step 3:** Re-run the contention check: for each open PR, grep its plan files for
  `score.py` and `scoring_handlers`, and read each hit for write or read. A new plan editing
  `_score_batch_row`, `_outputs_json`, `_coerce_output_value`, `_KNOWN_OUTPUT_TYPES` or
  `scoring_handlers.py:222-245` is a stop, reported to the lead.
- [ ] **Step 4:** `uv sync --all-packages`, then
  `uv run pytest packages/pricing-core/tests/test_rating_score_batch.py -q` green on the base.
  Record the count. (One test file only; the planner charter's and the executor's rule on
  heavy runs beside a held slot applies: check `pgrep -af 'pytest|vitest|flock'` and both gate
  slots first.)

### Task 1: The row escape, red first (items 1–4)

**Files:**
- Create: `packages/pricing-core/tests/test_rating_score_batch_outputs.py`
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py` (`_score_batch_row`, `:1081-1127`)
- Test (append): `backend/tests/test_scoring_handlers.py`

**Interfaces:**
- Consumes: `_compiled`, `_algorithm_payload`, `_ctx` from `test_rating_score`;
  `_contexts`, `_ctx_to_row` from `test_rating_score_batch`; `score_batch`.
- Produces: `_score_batch_row(bundle, row) -> dict[str, Any]`, signature unchanged, never
  raising anything but `NotImplementedError`.

- [ ] **Step 1: Write the failing tests (items 1–3).**

```python
"""FD 9513's fix (WK-1178): a row's serialisation failure is that row's error row
(FR-255), and batch writes every declared output type `/score` serves (FR-254)."""

from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import Any

import polars as pl
import pytest
from test_rating_score import _compiled
from test_rating_score_batch import _contexts, _ctx_to_row

import pricing_core.rating.score as score_module
from pricing_core.rating.score import score_batch


def _fail_on_second_call(
    original: Callable[..., str], exc: BaseException
) -> Callable[..., str]:
    calls = itertools.count()

    def wrapper(*args: Any, **kwargs: Any) -> str:
        if next(calls) == 1:
            raise exc
        return original(*args, **kwargs)

    return wrapper


@pytest.mark.req("FR-255")
@pytest.mark.parametrize(
    ("target", "exc"),
    [
        ("_outputs_json", ValueError("injected serialisation failure")),
        ("_outputs_json", TypeError("injected serialisation failure")),
        ("_ladder_json", KeyError("injected serialisation failure")),
    ],
)
async def test_a_row_whose_serialisation_raises_is_an_error_row_and_the_batch_continues(
    monkeypatch: pytest.MonkeyPatch, target: str, exc: BaseException
) -> None:
    compiled = await _compiled()
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    clean = {r["quote_id"]: r for r in score_batch(compiled, frame).collect().to_dicts()}

    monkeypatch.setattr(
        score_module, target, _fail_on_second_call(getattr(score_module, target), exc)
    )
    out = score_batch(compiled, frame).collect().to_dicts()
    by_quote_id = {r["quote_id"]: r for r in out}

    assert len(out) == 4
    bad = by_quote_id["Q1"]
    assert bad["outcome"] == "error"
    assert bad["error_code"] == type(exc).__name__
    assert bad["premium_ladder_json"] is None
    assert bad["outputs_json"] is None
    for quote_id in ("Q0", "Q2", "Q3"):
        good = by_quote_id[quote_id]
        assert good["error_code"] is None
        assert good["premium_ladder_json"] == clean[quote_id]["premium_ladder_json"]
        assert good["outputs_json"] == clean[quote_id]["outputs_json"]


@pytest.mark.req("NFR-499")
async def test_an_error_row_from_serialisation_carries_no_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = await _compiled()
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    monkeypatch.setattr(
        score_module,
        "_outputs_json",
        _fail_on_second_call(
            score_module._outputs_json, ValueError("premium_in=SENTINEL-9513")
        ),
    )
    out = score_batch(compiled, frame).collect().to_dicts()
    bad = next(r for r in out if r["quote_id"] == "Q1")
    assert bad["outcome"] == "error"
    assert "SENTINEL-9513" not in (bad["error_message"] or "")


async def test_not_implemented_still_propagates_from_serialisation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = await _compiled()
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    monkeypatch.setattr(
        score_module,
        "_outputs_json",
        _fail_on_second_call(score_module._outputs_json, NotImplementedError("undesigned")),
    )
    with pytest.raises(NotImplementedError):
        score_batch(compiled, frame).collect()
```

  The rows are scored in order within one chunk (`_score_batch_chunk`, `:1131`), so "the second
  call" is row `Q1`. Read `_contexts(4)`'s quote ids (`Q0`…`Q3`, `:58-70`) at the dispatch tree
  before relying on that.

- [ ] **Step 2: Run them and see items 1–2 fail by their cause.**
  Run: `uv run pytest packages/pricing-core/tests/test_rating_score_batch_outputs.py -q -k "escape or serialisation"`
  Expected: items 1 and 2 FAIL because the injected exception (`ValueError: injected
  serialisation failure`, `TypeError: …`, `KeyError: …`, `ValueError: premium_in=…`) is raised
  out of `score_batch(...).collect()`. Item 3 passes. Record each printed line. (`-k` matches
  the test names; check that it selects all five cases and record the count.)

- [ ] **Step 3: Write item 4 (B) and see it fail.** Append after
  `test_the_unset_default_means_no_rate_based_abort_but_counts_still_accrue` (`B:361-388`):

```python
@pytest.mark.req("FR-255")
async def test_a_row_whose_serialisation_raises_does_not_end_the_job(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FD 9513: a row whose serialisation raises is that row's error row (FR-255), and the
    Job completes. The injection is in pricing-core, so the handler loop needs no change."""
    import itertools

    import pricing_core.rating.score as score_module

    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )
    frame = _scoring_frame(4)
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, principal, frame
    )
    original = score_module._outputs_json
    calls = itertools.count()

    def failing(*args: Any, **kwargs: Any) -> str:
        if next(calls) == 1:
            raise ValueError("injected serialisation failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(score_module, "_outputs_json", failing)
    result, _ = await _run_handler(
        database, blob_store, workspace_id, principal, _parameters(dataset_version_id)
    )
    summary = await _summary(database, blob_store, result)

    ref_result = summary["results"][0]
    assert ref_result["error_counts"] == {"ValueError": 1}
    assert ref_result["outcome_counts"]["quoted"] == 3
    assert ref_result["row_count"] == 4
```

  Move the two imports to the module's import block if the file's style requires it (ruff `I`).
  Run: `uv run pytest backend/tests/test_scoring_handlers.py -q -k serialisation_raises`.
  Expected: FAIL, the handler raises the injected `ValueError` (no `JobResult` is returned).
  Read `_scoring_frame`'s `bad_row` default (`B:51`) and `_run_handler`'s return (`B:128`) at
  the dispatch tree; the sketch assumes `bad_row=None` gives four valid rows.

- [ ] **Step 4: The minimal change.** In `_score_batch_row`, keep the first `try` as it is, and
  run both serialisers inside a second `try` before the `return`:

```python
    try:
        premium_ladder_json = _ladder_json(scored.premium_ladder)
        outputs_json = _outputs_json(algorithm, scored.outputs)
    except NotImplementedError:
        raise
    except Exception as exc:  # FR-255 (FD 9513): anything this row's serialisation raises
        code, message = _batch_error_code(exc)
        return _batch_error_row(quote_id, rating_version_ref_str, bundle, code, message)

    return {
        "quote_id": quote_id,
        "outcome": scored.outcome,
        "rating_version_ref": rating_version_ref_str,
        "bundle_hash": scored.bundle_hash,
        "premium_ladder_json": premium_ladder_json,
        "outputs_json": outputs_json,
        "decline_reasons": list(scored.decline_reasons),
        "error_code": None,
        "error_message": None,
    }
```

  `_batch_error_row(quote_id, rating_version_ref_str, bundle, code, message) -> dict[str, Any]`
  is the existing error dict (`:1105-1115`) extracted, and the first `except` (`:1103`) returns
  it too, so the error row is written in one place. The first `try`'s handlers are unchanged:
  the ruling widens the catch for what comes **after** it only. Update the function's docstring
  to say so. `except Exception` is not refused by the repository's ruff selection
  (`pyproject.toml:83`; precedent `compile.py:321`).

- [ ] **Step 5: Run items 1–4 and the existing module.** Expected: PASS. Then
  `uv run pytest packages/pricing-core/tests/test_rating_score_batch.py -q` (item 9) passes
  unchanged.

- [ ] **Step 6: The break for item 3.** Temporarily delete the new `except NotImplementedError:
  raise`; item 3 fails with `Failed: DID NOT RAISE`. Record it and restore.

- [ ] **Step 7: Commit.**

```bash
git add packages/pricing-core/src/pricing_core/rating/score.py \
  packages/pricing-core/tests/test_rating_score_batch_outputs.py backend/tests/test_scoring_handlers.py
git commit -m "fix(rating): a batch row whose serialisation raises is that row's error row (FD 9513, FR-255)"
```

### Task 2: The four declared types, red first (items 5–8; after DP-1)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py` (`_KNOWN_OUTPUT_TYPES` `:943-947`,
  `_coerce_output_value` `:950-988`, `_outputs_json`'s docstring `:992-995`)
- Test: `packages/pricing-core/tests/test_rating_score_batch_outputs.py`

**Interfaces:**
- Consumes: Task 1's `_score_batch_row`; `compile._NUMERIC`; `_algorithm_payload`,
  `_rate_table_payload`, `_gbm_model_payload`, `_train_tiny_booster`, `_version`.
- Produces: `_coerce_output_value(declared_type: str, value: Any) -> int | str | bool`, same
  signature, total over `_NUMERIC | {"bool", "string", "date"}`.

- [ ] **Step 1: Write the failing tests (items 5–8), for DP-1 (b) / DP-2 (ii).**

```python
import copy
import json
from decimal import Decimal

from test_rating_runtime import _gbm_model_payload, _rate_table_payload, _train_tiny_booster
from test_rating_score import _algorithm_payload, _version

from model_schema.refs import ArtifactRef
from pricing_core.rating import compile as compile_module
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import _KNOWN_OUTPUT_TYPES, score_one


def _probe_payload(declared_type: str, expr: str) -> dict[str, Any]:
    payload = copy.deepcopy(_algorithm_payload())
    payload["outputs"].append({"name": "probe_out", "type": declared_type, "required": False})
    payload["steps"].append(
        {
            "step_id": "s_probe", "type": "expression", "label": "Probe",
            "expr": expr, "result_type": declared_type,
            "consumes": ["driver_age"], "produces": "probe_raw",
        }
    )
    payload["steps"].append(
        {
            "step_id": "s_out_probe", "type": "output", "label": "Probe output",
            "output_name": "probe_out", "rounding": {"mode": "half_even", "dp": 2},
            "consumes": ["probe_raw"],
        }
    )
    return payload


class _ProbeResolver:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payloads = {
            "rating_algorithm:score-fixture@1": payload,
            "rate_table:motor-expense@1": _rate_table_payload(),
            "model:motor-freq@1": _gbm_model_payload(_train_tiny_booster()),
        }

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payloads[str(ref)])


async def _probe_bundle(declared_type: str, expr: str) -> CompiledBundle:
    bundle = await compile_bundle(_version(), _ProbeResolver(_probe_payload(declared_type, expr)))
    return load_bundle(bundle)


@pytest.mark.req("FR-254")
@pytest.mark.parametrize("declared_type", ["int", "count"])
async def test_an_integer_declared_output_is_the_same_json_integer_in_batch_and_on_score(
    declared_type: str,
) -> None:
    compiled = await _probe_bundle(declared_type, "driver_age")
    contexts = _contexts(10)
    out = score_batch(compiled, pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy())
    by_quote_id = {r["quote_id"]: r for r in out.collect().to_dicts()}
    for ctx in contexts:
        row = by_quote_id[ctx.quote_id]
        assert row["error_code"] is None, row["error_code"]
        batch_value = json.loads(row["outputs_json"])["probe_out"]
        served = json.loads((await score_one(compiled, ctx)).model_dump_json())["outputs"]
        assert batch_value == served["probe_out"]
        assert type(batch_value) is int
        assert type(served["probe_out"]) is int


@pytest.mark.req("FR-255")
@pytest.mark.parametrize("declared_type", ["int", "count"])
async def test_a_non_integral_value_for_an_integer_output_is_an_error_row(
    declared_type: str,
) -> None:
    compiled = await _probe_bundle(declared_type, "driver_age * 1.1")
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    out = score_batch(compiled, frame).collect().to_dicts()
    assert len(out) == 4
    q0 = next(r for r in out if r["quote_id"] == "Q0")  # driver_age 18 -> 19.8
    assert q0["outcome"] == "error"
    assert q0["error_code"] == "ValueError"
    assert q0["outputs_json"] is None


@pytest.mark.req("FR-214")
@pytest.mark.parametrize("declared_type", ["relativity", "percentage"])
@pytest.mark.parametrize(("expr", "expected"), [("driver_age * 1.5", "27"), ("driver_age * 1.1", "19.8")])
async def test_a_fractional_declared_output_is_a_decimal_string_in_batch(
    declared_type: str, expr: str, expected: str
) -> None:
    compiled = await _probe_bundle(declared_type, expr)
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(1)]).lazy()  # driver_age 18
    (row,) = score_batch(compiled, frame).collect().to_dicts()
    assert row["error_code"] is None, row["error_code"]
    assert json.loads(row["outputs_json"])["probe_out"] == expected


@pytest.mark.req("FR-254")
def test_the_known_output_types_name_every_numeric_family_member() -> None:
    missing = (compile_module._NUMERIC | {"bool", "string", "date"}) - _KNOWN_OUTPUT_TYPES
    assert not missing, sorted(missing)
```

  Move the imports to the top of the module (ruff `I`). `score_one`'s signature at the dispatch
  tree decides whether it is awaited and what it takes (`:876`); read it first. The `expected`
  strings are what the `decimal` branch gives for the engine's `int` 27 and `float` 19.8 today
  (`str(Decimal(repr(value)))`); they are batch's interim form under DP-2 (ii), not
  `RL-1343` rule 3's form. Whether the engine accepts `result_type` `count`, `relativity` and
  `percentage` on an `expression` step is read from FD-1561's probe (it did), and re-checked by
  Step 2's output.

- [ ] **Step 2: Run them and see each fail by its cause.**
  Run: `uv run pytest packages/pricing-core/tests/test_rating_score_batch_outputs.py -q -k "declared or known_output"`
  Expected: item 5 FAILS on `assert row["error_code"] is None` with `'ValueError'` (the
  refusal at `:964-965`, now a row error after Task 1); item 7 FAILS the same way; item 8 FAILS
  printing `['count', 'int', 'percentage', 'relativity']`; item 6 PASSES (the row is already an
  error, from the type refusal). Record each line.

- [ ] **Step 3: The minimal change.** `_KNOWN_OUTPUT_TYPES` gains the four types (comment updated
  to cite FD-1561 and DP-1). `_coerce_output_value` gains two branches, before the
  `unreachable` assertion:

```python
    if declared_type in ("int", "count"):
        # FD 9513, DP-1 (b): an integral value is a JSON integer on both paths, as money_minor.
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                f"score_batch: a {declared_type} output must be int, got {type(value).__name__}"
            )
        return value
    if declared_type in ("decimal", "relativity", "percentage"):
        as_decimal = value if isinstance(value, Decimal) else Decimal(repr(value))
        return str(as_decimal)
```

  *(Pre-mint delta 3: the `int`/`count` branch above is superseded by Step 3b's, which reads:*

```python
    if declared_type in ("int", "count"):
        # FD 9513, DP-1 (b); RL 9498: integral by exact equality, no tolerance; 3.0 -> 3.
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value != int(value):
            raise ValueError(
                f"score_batch: a {declared_type} output must be integral, got {type(value).__name__}"
            )
        return int(value)
```

  *A non-finite float makes `int(value)` raise `OverflowError` or `ValueError`; the executor puts
  `math.isfinite` before the comparison so the error is the `ValueError` above.)*

  The second branch replaces the existing `decimal` branch (`:972-974`), whose body is
  unchanged; it now names the two types DP-1 (b) writes in the `decimal` form. The docstring of
  `_coerce_output_value` and of `_outputs_json` say which types are written how, and that the
  `RL-1343` slice replaces the second branch's conversion.

- [ ] **Step 3b (pre-mint delta 2): integrality by exact equality.** Write items 12 and 13 and
  run them against Step 3's branch: item 12 FAILS (`error_code == "ValueError"` for `3.0`);
  record it. Replace the `int`/`count` branch's check with: `bool` refused; an `int` returned
  unchanged; a `float` returned as `int(value)` only if `value == int(value)` (no tolerance, the
  ruling's words), else `ValueError` naming the declared type and the value's type, never the
  value. Run items 5–8, 12 and 13: PASS. Then the item 13 break (a tolerance) and restore.
- [ ] **Step 4: Run items 5–8.** Expected: PASS.

- [ ] **Step 5: The break for item 6.** ~~Temporarily remove the `isinstance(value, int)` check;
  item 6 fails because `outputs_json` is written (`19.8`) and `outcome` is `"quoted"`. Record
  it and restore.~~ *(Pre-mint delta 3:)* Temporarily remove the `value == int(value)` check;
  item 6 fails because `outputs_json` is written (`19.8`) and `outcome` is `"quoted"`. Record it
  and restore. Then temporarily replace the check with `isinstance(value, int)`; item 12 fails
  (`3.0` refused). Record it and restore.

- [ ] **Step 6: Commit.**

```bash
git add packages/pricing-core/src/pricing_core/rating/score.py \
  packages/pricing-core/tests/test_rating_score_batch_outputs.py
git commit -m "fix(rating): batch writes int, count, relativity and percentage outputs (FD 9513, FR-254)"
```

### Task 3: The spec text, only from an `RL-` (activation need 4)

- [ ] **Step 1:** ~~If DP-1's ruling carries text for the `outputs_json` row (`03:692`) or FR-214
  (`:83`), apply it byte for byte. A find string that is not found exactly once is a stop,
  reported to the lead. If the ruling carries no text, record "no spec text" in the ledger.~~
  *(Pre-mint delta 1:)* Apply the minted `RL-`'s T1 to the `outputs_json` row (`03:692`), byte
  for byte. Apply its T2 to the FR-214 row (`:83`) only if SL-1569 has not merged. If SL-1569
  has merged, T2 is already applied: record that, and the line it sits on, in the ledger. A find
  string that is not found exactly once is a stop, reported to the lead.
- [ ] **Step 2:** `python3 scripts/audit-docs.py`. Expected: the only `FAILED` line, if any, is
  check 31 for working ids not yet minted.

### Task 4: The gate and the ledger (items 10, 11)

- [ ] **Step 1:** The full two-half gate through the gate-runner, holding the one gate slot.
  Record each rc and the tree.
- [ ] **Step 2:** The `LG-` ledger: Task 0's readings and re-runs, every red with its printed
  line, both breaks, DP-1/2/3 as ruled, and `git diff --stat origin/main...HEAD` against
  §"Write set".

## Hand-off

1. The lead mints PL-1565 and SL-1566 after FD-1561, and dispatches only after §"Activation
   needs" hold, in a separate activation PR.
2. On merge, FD-1561's event is discharged ("a merged change to `_coerce_output_value` and
   `_score_batch_row`"). The auditor closes it, naming under DP-2 (ii) that the `/score` half
   for `relativity` and `percentage` is carried by the `RL-1343` slice.
3. **To the planner of the `RL-1343` slice, PL-1568 / SL-1569** (planner-1343;
   *pre-mint delta 1*; §"RL-1343's discharge"): cover a
   whole-valued `decimal` (a JSON integer on `/score` today) and a fractional one (a float);
   rule 4's float refusal does not catch the first. Under DP-2 (ii), give `relativity` and
   `percentage` the same producer and flip item 7 to both paths. Serialise with this slice on
   `_coerce_output_value`, **in both directions**: whichever of SL-1566 and SL-1569 merges second
   merges `main` first, and keeps the other's branches (this slice's `int`/`count` branch, or
   that slice's producer for `decimal`, `relativity` and `percentage`). FR-214's T2 is applied
   once, by whichever merges first (§"The spec text DP-1 (b) owes").
4. **To PL-1562's executor (#1202):** its Step 1a compares an `int`/`count` → `decimal` output
   on `/score` and batch. That is FD-1333's divergence, now also FD-1561's record; a
   difference found there is already filed, so it is cited, not re-filed.

## Self-review

1. **Coverage of the ruling's item 2, clause by clause.**
   - "(1) the ROW ESCAPE first": Task 1, items 1–4, before any type change.
   - "ANY exception from _outputs_json": item 1's `ValueError` and `TypeError`.
   - "(or anything else after the try)": item 1's `_ladder_json` case.
   - "becomes that row's error row, and the run continues (FR-255)": items 1 and 4.
   - "it lands even if the type DP is still open": activation need 3, Task 0 Step 1.
   - "(2) the four types": Task 2, items 5–8.
   - "the JSON form of count, relativity and percentage as a DP for me": DP-1 (with `int`, since
     the probe shows the same refusal for it), and DP-2 for its carrier.
   - "FR-254's 'batch never diverges' is the reading; the plan proposes": DP-1's recommendation
     argues from FR-254, `03:692`, `RL-923` §5(i) and `RL-1343`.
2. **Coverage of item 3:** §"RL-1343's discharge": no plan exists; what it must cover (both
   forms; rule 4's blind spot for a whole value); Hand-off 3.
3. **Coverage of item 1:** "AFTER SL-1427": activation need 2 and the contention table.
4. **Repository literals read at `5fe56b87`:** every line in §"Task 0 at planning time" and
   §"Write set"; FD-1561 at `0303d0bf`; each other plan on its branch at the head named in the
   contention table. The brief's anchors were checked: the `try` is `:1096-1103` counting its
   handlers (`:1096-1100` the body), and `:1123` is `_outputs_json`; `:1122` (`_ladder_json`)
   is also outside it.
5. **What was not executed.** No test or code was run. The sketches use names read at
   `5fe56b87`; `score_one`'s call form, `_scoring_frame`'s default and the engine's
   acceptance of the four `result_type`s are named in the steps for the executor to read first.
   A sketch that does not run as written is a plan defect to report, not to work around.
6. **Type consistency:** `_batch_error_row` is defined in Task 1 Step 4 and used at both
   `except`s; `_probe_payload`, `_ProbeResolver` and `_probe_bundle` are defined and used in
   Task 2; `_coerce_output_value`'s signature is unchanged.
7. **Pre-mint delta 2 coverage:** the ruling's "each slice has one red for 3.0 → 3 and one for a near-integer refused": items 12 and 13 (Task 2 Step 3b); "T1 and T2 state it": `RL-1567`'s texts, applied by Task 3; activation need 4 names `RL-1567`.
8. **Pre-mint delta 3 coverage:** the 18:26:46 entry: T1 states `ValueError` (delta 3, last
   bullet); the `isinstance` break replaced and turned into a red for `3.0` → `3` (item 6's second
   break, Step 5). The 18:27:10 entry: items 6 and 13 marked "until SL-1569".
