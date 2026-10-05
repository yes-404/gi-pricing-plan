---
id: RL-9562
family: ruling
title: PL 9567 (the FD 9572 fix) DP-1, DP-2 and DP-4 decided — a quote input naming a produced value is refused by name as INPUT_CONTRACT_VIOLATION, declared inputs subtracted, and FR-212 and FR-213 take T1 and T2; DP-3 stays open
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-212, FR-213, FR-246, FR-255, FD-1374]
---

# RL 9562 (working id) — PL 9567 (the FD 9572 fix): DP-1, DP-2 and DP-4 decided, DP-3 open

## How this was ruled

- **The decisions are not this record's.** They are the maintainer's, by delegation, in three
  entries in `~/gi-pricing-plan.local/channel/to-lead.md`, quoted verbatim under "The
  maintainer's entries" below: 17:06:26 BST (the fix ruled), 17:10:08 BST (FD 9572 HIGH,
  FINAL) and 17:22:47 BST (PL 9567's DP-1..4 ruled). The 17:22:47 entry's DP-4 orders this
  record: "an RL adopts T1 (FR-212: "list order carries no meaning") and T2 (FR-213) BEFORE
  activation, as an added activation need. Reserve the id; a DM files it, quoting my 17:06:26
  and 17:10:08 entries and this one."
- **Three later entries re-scope it, and are quoted verbatim too:** 17:25:07 BST (the premise
  measured FALSE; a HOLD; fix (c) moves to an EMERGENCY slice, SL 9561 / PL 9560, under
  WK-1178; PL 9567 drops (c) by a dated delta), its 17:25:23 BST addendum (the emergency slice
  fixes the ROOT and adds guard (c)), and 17:26:16 BST (the emergency slice's order, and
  "RL 9562's re-scope (non-blocking): noted"). DP-1 and DP-2 as ruled at 17:22:47 are restated
  for the emergency slice in the 17:25:07 entry's item 2; this record carries them unchanged and
  names where each now applies (§"What it obliges").
- **The decision points** are PL 9567's (working id, #1193, branch
  `pl-9567-fd9572-to-wire-order` at `f4e4380b6f35ae1809d70bb22027a9205e22c096`),
  §"Decision points". PL 9567, SL 9568 and FD 9572 are unminted, so each is cited in
  working-id form and kept out of `relates:` (check 32). **This record mints before PL 9567.**
- **Written 2026-10-05 17:24–17:27 BST (by `date`)**, by the decision-maker session `dm-9572rl`, on
  the lead's order (brief `brief-prep-wave-2026-10-05.md` §BG). Every fact below was read at
  `origin/main` `4d3be1414ad4dacdaa0c14ef49fb21853adbaed6`, by symbol with its line at that tree.
- **This record rules a plan's decision points and never edits the plan** (`document-ids.md`
  §1.6, PL row). It adds no option and no detail the entries do not name.

## The maintainer's entries, verbatim

### 2026-10-05 17:06:26 BST

> ## 2026-10-05 17:06:26 BST — FD 9572 (to_wire wires by LIST order): reproduced; severity waits on (1)/(2); the FIX RULED now; RL 9588 / RL 9586 noted
>
> Reproduced (auditor-towire at 137bc817; script sha256 6690fa73…114ae0): [in, A base=x*100, B premium=base+50, out] gives 350 in topological order; with B listed before A, ctx {x:3} → NodeError, ctx {x:3, base:7} → 57, a SILENT WRONG PRICE. Nothing reorders or refuses it: RatingAlgorithm._graph_invariants (model_schema/rating.py ~:392-470) runs Kahn only for cycles and discards the order; to_jdm keeps list order; to_wire (runtime.py ~:461-492) resolves a consumed name to the producer seen so far in list order.
> SEVERITY: provisional HIGH, final when (1) [do score()/the API pass extra ctx.inputs keys into the ZEN context?] and (2) [a clamp chain listed before its producer] are answered. HIGH if either gives a silent wrong price on a reachable path; MEDIUM only if every reachable misorder raises. Owner WK-673; deadline before the P2 exit demo.
> THE FIX, RULED (root, not symptom): FR-212 makes a Rating Algorithm a DAG, so LIST ORDER CARRIES NO MEANING and must never decide wiring.
>  (a) to_wire (and to_jdm, if it emits edges by order) wires every consumed name to its PRODUCER by name through the graph, over a STABLE topological order computed from the dependency edges (Kahn with list order as the tie-break, so an already-ordered list is unchanged and every existing bundle hash is stable; a test asserts the hash of a topologically listed algorithm is unchanged).
>  (b) No save-time refusal of a misordered list: authors may list steps in any order; that is what a DAG means.
>  (c) SEPARATELY, a quote input must never SHADOW a produced value: if (1) shows extra ctx keys reach ZEN, then a context key that names a step's produced value is refused (VALIDATION_FAILED, naming the key) or dropped per the input_contract. Its own red test (ctx {x:3, base:7} on the CORRECTLY ordered algorithm still gives 350, never 57).
>  Red first: [in, B, A, out] asserting 350; the clamp case from (2); the shadowing case. The WK-1250 S2 inliner uses the same topological order (RL 9586's P5, the DM's proposal: ACCEPTED, as it is the same rule).
> PLACEMENT: its own small WK-673 slice (or folded into the FD 9707 fix if that plan's write set already covers runtime.py's to_wire and the planner shows no scope creep). The planner proposes which, after (1)/(2).
> Noted: #1179 RL 9588 + OQ 9587 @4c1c54ea (B via B1; B2 an OQ for WK-1178 after G2, gate "Before Phase 3"; mints before PL 9593). #1180 RL 9586 @a014efaf (WK-1250 S2; P5 accepted above; 03 §4.1's example not a complete FR-212 graph today, recorded, not fixed: right). The WK-675 S4/S3/S13/S14 ids and RL 9573: noted.

### 2026-10-05 17:10:08 BST

> ## 2026-10-05 17:10:08 BST — FD 9572: HIGH, FINAL; TOP planning priority; an exposure scan now; RL 9573 noted
>
> FD 9572 (#1183 @7e9d38d7): HIGH, FINAL, owner WK-673, before the P2 exit demo. Both checks give a SILENT WRONG PRICE on reachable paths: (1) score_one (score.py ~:911) spreads `**ctx.inputs` into the ZEN context and _validate_inputs tolerates extras, so a CALLER sending office_premium_minor=1000 to a misordered algorithm gets 1050 against 1507: a caller-controlled price; (2) a clamp listed before its producer silently skips the minimum premium (1507 vs 5250, no error). The essay carries my 17:06:26 fix verbatim, and (c) (refuse or drop a context key naming a produced value) is now REQUIRED.
> PRIORITY: it outranks the remaining planning. A caller can steer a price, which is worse than a wrong rate that no one controls.
>  1. PLAN: the NEXT free slot goes to a dedicated planner for the FD 9572 fix (its own small WK-673 slice), ahead of every other prep item. Do not wait for planner-673s46's S6. The planner checks whether folding into the FD 9707 fix (PL 9688) is cleaner (both touch runtime.py and score.py), and if so does it as a pre-mint addition to PL 9688 instead, provided PL 9688 is not yet minted (it is ~mint 8 tonight): the planner decides within 15 min.
>  2. LANE: under my priority rule it takes the first build lane free once its plan is active, tied with the FD 9707 fix; on a tie, FD 9572 goes FIRST.
>  3. EXPOSURE SCAN, an auditor in the slot after, read-only: scan every stored algorithm (gipricing's rating_algorithms rows; examples/, seeds, goldens, fixtures) for a list order that differs from its topological order, and every caller of score_one for extra-key behaviour (api/score.py, batch scoring, the dislocation run). If ANY stored algorithm is misordered, report it to me at once with its slug and version (a live mispricing exposure, which may need an interim hold on that version).
>  4. INTERIM: until the fix merges, no NEW Rating Version may be approved or deployed in gipricing unless its algorithm's list order equals its topological order (a manual check in any approval the team performs). Nothing is deployed to prod today, so this is a guard, not a rollback.
> RL 9573 (#1182 @33ec89a9, WK-1250 S3; mints after RL 9586): noted.

### 2026-10-05 17:22:47 BST

> ## 2026-10-05 17:22:47 BST — PL 9567 (the FD 9572 fix, #1193 @f4e4380b) DP-1..4 RULED; CORRECTION of my error code; the unmeasured premise kept as a STOP
>
> DP-1: (a) INPUT_CONTRACT_VIOLATION, and a CORRECTION of my 17:06:26 / 17:10:08 "VALIDATION_FAILED". Verified: backend/src/app/api/score.py `_PER_QUOTE_CODES` (:97) does not hold VALIDATION_FAILED, and :332 sends any other code to the caller as a 500. A refused key must be a per-quote 422-class error, as the _check_billing_surface precedent does.
> DP-2: (a) REFUSE, by name, never drop silently: a context key that names a PRODUCED value is refused, with the DECLARED inputs subtracted first. A clamp that re-produces a declared input in place is legitimate, so a declared input is never refused for sharing a name with its in-place clamp. A red test for that exception.
> DP-3: NOT decided here, per my order; the options stay recorded. (c) is exactly "an undeclared key naming a produced value"; FR-246's declared-inputs rule (FD-1374 / PL 9776) stays its own.
> DP-4: an RL adopts T1 (FR-212: "list order carries no meaning") and T2 (FR-213) BEFORE activation, as an added activation need. Reserve the id; a DM files it, quoting my 17:06:26 and 17:10:08 entries and this one.
> THE UNMEASURED PREMISE: right. My "ctx {x:3, base:7} on the CORRECT order still gives 350" was never run (FD 9572 measured only misordered cases). Keep the STOP: the first red/green run measures it on main's code with a correctly ordered algorithm. If it is NOT 350 there, the shadow sits in the engine's context merge, (c) is the ONLY guard, and FD 9572's essay gains that fact (an ordered algorithm is also exposed), reported to me at once with the measured price.
> Pins (an ordered list wires exactly as listed via the heap tie-break; the bundle hash unchanged): right.

### 2026-10-05 17:25:07 BST

> ## 2026-10-05 17:25:07 BST — URGENT RULING: FD 9572's premise FALSE; OPTION (iii): a HOLD now, and an EMERGENCY (c)-only slice FIRST in lane B (WK-1178); the wiring fix after
>
> FACT (auditor-premise at 4d3be141, script sha256 b3448450a1fe4c5b9622ec15555fda8a5d983c0b82e1ca9bbb7b624df2fb501c, through score_one): a CORRECTLY ORDERED algorithm with min_premium=5000 and an extra input instalment_loading_minor=777 quotes payable=777 (ladder: risk 1305, office 1436, constraints 5000, instalment_loading 777, payable 777), against 5250 without the key. A caller key naming a produced name OVERRIDES that step's output in correct order: the shadow is in the engine's context merge. My 17:22:47 premise ("the correct order still gives 350") is FALSE for this shape, and the STOP did its job.
> EXPOSURE, my read at 17:24: gipricing `select count(*) from deployments` = 0; rating_versions = fremtpl2-demo@1, approved. So NO deployed version is serving, and no real quote is affected, but one approved version is one step from deployable, and the code path is open to any caller with score:execute (/score, /score/compare, trace reproduction, batch).
> RULING (the maintainer, by delegation): OPTION (iii).
>  1. HOLD, NOW, replacing the 17:10:08 interim hold (which did not cover this): NO Rating Version is DEPLOYED to any Environment, and no new Rating Version is approved, while /score (and compare, trace reproduce, batch) accepts an undeclared input key. This includes fremtpl2-demo@1. Record it in eta.md Holds and holds-2026-10-01.md, quoting this header; check it at every approval and deploy dispatch. It lifts at the emergency slice's merge.
>  2. EMERGENCY SLICE, its own tiny slice under WK-1178 (the standing maintenance Work, so it may run beside S7 (WK-673) under RL-1263's different-Works rule NOW, without waiting for RL 9620), FIRST in LANE B (free now; the FD 9707 fix waits behind it):
>    - scope = fix (c) ONLY: in the shared merge (score.py ~:911 score_one and ~:1067 _score_context_sync), refuse an UNDECLARED input key that names ANY produced value of the algorithm, with INPUT_CONTRACT_VIOLATION (per-quote 422, my 17:22:47 DP-1), declared inputs subtracted (DP-2: the in-place clamp of a declared input stays legal);
>    - red first: the auditor's (3f) case gives 777 today and must be refused; plus a case per path (/score, /score/compare, trace reproduce, batch with a dataset column so named); the ordered no-extra-key case unchanged (5250); the bundle hash unchanged;
>    - the minimal plan: a planner writes it NOW (a leaf plan plus its SL row, my rulings quoted as its authority; no new DPs: every decision is already made), minted at once, ahead of everything in the mint queue except the in-flight batch-1 merge; a sonnet executor; one gate; my ACK.
>  3. The WIRING fix (PL 9567, list order) follows as planned, after the emergency slice, rebased on it; its (c) part is then already delivered, so PL 9567 drops (c) by a dated delta and keeps (a)/(b).
>  4. FD 9572's essay gains this measured fact (an ordered algorithm is also exposed; the cause in the context merge) as a dated pre-mint amendment; the severity stays HIGH. The auditor finishes the cause trace (why base/premium are overridden by their producers in the [in,A,B,out] shape but instalment_loading is not: step kind or position), reported with the emergency slice's plan.

### 2026-10-05 17:25:23 BST

> ## 2026-10-05 17:25:23 BST — ADDENDUM to my 17:25:07 urgent ruling: the emergency slice fixes the ROOT in score_one AND adds guard (c)
>
> The final measurement (r1.py 8dea0ff6…, r2.py b3448450…) shows the ZEN wiring of an ORDERED graph is correct (350 for every extra key), and the wrong price arises in score_one's path (the context merge, or how the output/ladder READ produced values): instalment_loading_minor=777 → payable 777 vs 5250; the clamp's own name is not shadowed. So the emergency slice's scope is BOTH: (1) the ROOT, once the auditor's per-name table and cause line(s) land, e.g. if the output or ladder reads a produced value from the merged context instead of the producing step's result, it reads the step's result; and (2) guard (c), refusing an undeclared key naming a produced value with INPUT_CONTRACT_VIOLATION, kept as defence in depth. The red tests include the per-name table's shadowed cases. My 17:25:07 HOLD, lane B placement, WK-1178 and the "no new DPs" plan stand. If the root fix proves to need a design choice, it comes to me, and (c) alone ships first.

### 2026-10-05 17:26:16 BST

> ## 2026-10-05 17:26:16 BST — Emergency slice SL 9561 / PL 9560 (WK-1178): the order is GO → activation PR → executor, as for S7
>
> The lead's "GO … after its plan mints and activates" is corrected to the 17:17:37 order: my DISPATCH GO comes after PL 9560 is MINTED (draft), before its activation PR, which quotes the GO header. PL 9560 mints right after batch 1, ahead of the rest of the queue. The hold, the scope (root + guard (c)), PL 9567's (c) delta and RL 9562's re-scope (non-blocking): noted.

## Locators — read at `4d3be141`

| Locator | Where | What it holds |
|---|---|---|
| `_PER_QUOTE_CODES` | `backend/src/app/api/score.py:97` | `INPUT_CONTRACT_VIOLATION`, `RATE_TABLE_MISS`, `REFERENCE_LOOKUP_MISS`, `MODEL_CALL_FAILED`; no `VALIDATION_FAILED` (`grep -c VALIDATION_FAILED` on the file = 0) |
| `_as_platform_error` | `backend/src/app/api/score.py:309`; its `if not separator or code not in _PER_QUOTE_CODES: return None` at `:332` | a code outside the set is not mapped, so it reaches the caller as a 500 |
| `_check_billing_surface` | `packages/pricing-core/src/pricing_core/rating/score.py:425` | the precedent: a named `INPUT_CONTRACT_VIOLATION` raised before the engine call |
| the `**ctx.inputs` merge | `packages/pricing-core/src/pricing_core/rating/score.py:911` (`score_one`) and `:1067` (`_score_context_sync`) | where every `ctx.inputs` key enters the ZEN context; `_check_billing_surface(ctx)` is called at `:899` and `:1064` |
| the FR-212 row | `docs/specs/03-rating-engine.md:81` | "A **Rating Algorithm** is a directed acyclic graph of Rating Steps. …" |
| the FR-213 row | `docs/specs/03-rating-engine.md:82` | "The algorithm declares a typed **input contract**: …" |

## Ruled

**Decided by the maintainer, by delegation, 2026-10-05 17:22:47 BST (quoted above).**

### DP-1 — option (a): `INPUT_CONTRACT_VIOLATION`

A `ctx.inputs` key refused under DP-2 is refused with the code `INPUT_CONTRACT_VIOLATION`,
naming the key, as `_check_billing_surface` does. It is a per-quote 422-class error, because
`_PER_QUOTE_CODES` (`backend/src/app/api/score.py:97`) holds that code, and no backend change
is needed.

**This CORRECTS** the code "VALIDATION_FAILED" named in the 17:06:26 and 17:10:08 entries
(fix (c)). That code is not in `_PER_QUOTE_CODES`, so `_as_platform_error` (`:332`) would send
it to the caller as a 500. The correction is the maintainer's own (the 17:22:47 entry, DP-1);
this record carries it, and FD 9572's essay, which quotes the 17:06:26 fix verbatim, is not
edited by it.

### DP-2 — option (a): REFUSE by name, declared inputs subtracted

A Quote Context input key that names a value some step produces is **refused, by name, never
dropped silently**. The declared inputs are **subtracted first**: a key that is a declared
input is never refused for sharing its name with a step that re-produces that input in place
(a clamp consuming and producing `x`).

- **A red test for that exception** is owed by the slice that delivers fix (c) (the emergency
  slice, per the 17:25:07 entry's item 2: "declared inputs subtracted (DP-2: the in-place clamp
  of a declared input stays legal)"): a declared input re-produced in place
  by its clamp is accepted and priced, not refused. (PL 9567 Task 3 Step 1b names a guard for
  DP-2 (a)'s subtraction in `test_rating_wire_order.py`; the planner or the dispatch record
  confirms that it is this red test.)

### DP-3 — NOT decided

**Not decided here, per the maintainer's order.** PL 9567's options (a), (b) and (c) stay
recorded in its §"Decision points" as written. What the entry does fix:

- Fix (c)'s scope is exactly **"an undeclared key naming a produced value"**.
- FR-246's declared-inputs rule (FD-1374 / PL 9776) stays its own.

PL 9567 Task 3 is written for DP-3 (a) and says "A different decision rewrites this task
before it starts". Task 3 stays blocked on DP-3 until it is decided.

### DP-4 — option (a): this record ADOPTS T1 and T2

T1 and T2 are adopted **verbatim from PL 9567** (#1193 at `f4e4380b`, §"Decision points",
the paragraphs headed "T1 (DP-4 (a))" and "T2 (DP-4 (a))"), each joined onto one line as a
table cell requires. This adoption is an **added activation need** of PL 9567: the plan is
not activated until this record is merged.

PL 9567 Task 3 Step 4 applies each text "byte-for-byte as the adopting ruling states them,
each appended at the end of its row's last cell". Each find string below is the end of that
row's last cell at `4d3be141`, with `grep -cF` = 1 on `docs/specs/03-rating-engine.md`.

**T1 — the FR-212 row (`03-rating-engine.md:81`).**

- Find (`grep -cF` = 1):

  ```text
  references to undefined Derived Values are rejected at save time, not at scoring time. |
  ```

- Replace with:

  ```text
  references to undefined Derived Values are rejected at save time, not at scoring time. *(Amended 2026-10-05, FD 9572.)* The order in which an algorithm lists its steps carries no meaning: each consumed name is wired to its producer through the graph, over a stable topological order of the dependency edges. A misordered list is not refused at save. |
  ```

**T2 — the FR-213 row (`03-rating-engine.md:82`).**

- Find (`grep -cF` = 1):

  ```text
  Scoring rejects a Quote Context violating the contract with a field-level error. |
  ```

- Replace with:

  ```text
  Scoring rejects a Quote Context violating the contract with a field-level error. *(Amended 2026-10-05, FD 9572.)* A Quote Context input whose name is a value some step produces, and is not itself a declared input, is a contract violation, refused with a field-level error naming the key: a quote input never stands in for a produced value. |
  ```

- "FD 9572" in both texts is the finding's working id; the mint replaces it with the minted
  `FD-` id, as for every working id.
- T2 matches DP-1 (a field-level, per-quote refusal) and DP-2 (a) ("not itself a declared
  input"), and stays inside DP-3's fixed scope: it names neither the stamped names nor the
  engine-internal keys.

## What it obliges

- **PL 9567's planner** marks DP-1, DP-2 and DP-4 decided citing this record (a pre-mint edit
  to #1193, or carried by the dispatch record if the plan is minted first), adds this record's
  merge as an activation need (DP-4), and keeps DP-3 open. PL 9567 drops (c) by a dated delta
  and keeps (a)/(b) (the 17:25:07 entry, item 3); its Task 3 is then (c)'s and leaves with it.
- **The emergency slice (SL 9561 / PL 9560, WK-1178)**, which delivers fix (c) and the root
  (the 17:25:07 entry, item 2, and the 17:25:23 addendum), refuses with
  `INPUT_CONTRACT_VIOLATION`, never `VALIDATION_FAILED` (DP-1), declared inputs subtracted
  (DP-2), with DP-2's exception test.
- **T1** (FR-212, list order) is the wiring fix's text and is applied by PL 9567's slice
  (SL 9568) verbatim, in the same commit as its code (`CLAUDE.md` §2).
- **T2** (FR-213, a quote input naming a produced value) is fix (c)'s text. **Which slice
  applies it is not ruled** in any entry quoted here: PL 9567 adopted it for its Task 3, which
  the 17:25:07 delta removes, and the emergency slice's plan is to carry "no new DPs". This
  record does not choose; it is put to the lead (the 17:26:16 entry notes this record's
  re-scope as non-blocking). Until it is answered, T2 is adopted here and applied by whichever
  slice delivers fix (c).

## Acceptance — the violation that must become detectable

Each is red first in the slice that delivers fix (c) (1–3) or applies the text (4):
1. *A shadowing key is refused with a code outside `_PER_QUOTE_CODES`.* The refusal test
   asserts `INPUT_CONTRACT_VIOLATION`, naming the key, on `score_one` and on
   `_score_context_sync`; a `VALIDATION_FAILED` (a 500 at the API) fails it.
2. *A shadowing key is dropped silently.* A context key naming a produced value, not a declared
   input, that prices instead of raising fails the refusal test.
3. *A declared input is refused for sharing its name with its in-place clamp.* The DP-2
   exception's red test (input `x`, a constraint consuming and producing `x`) fails if it
   raises.
4. *T1 or T2 differs from this record.* `grep -cF` of each replacement line above on
   `docs/specs/03-rating-engine.md` after Task 3 Step 4 is 1.

## The premise — MEASURED: false

The 17:22:47 entry kept a STOP on "ctx {x:3, base:7} on the CORRECT order still gives 350". It
has been measured, and the STOP did its job (the 17:25:07 entry, quoted above):

- **An ordered algorithm is also exposed.** Through `score_one`, a correctly ordered algorithm
  with `instalment_loading_minor=777` as an extra input quotes payable 777 against 5250 without
  the key (auditor-premise at `4d3be141`, script sha256
  `b3448450a1fe4c5b9622ec15555fda8a5d983c0b82e1ca9bbb7b624df2fb501c`, as the entry states it).
- **The ZEN wiring of an ordered graph is correct** (350 for every extra key); the wrong price
  arises in `score_one`'s path (the 17:25:23 addendum). The cause trace is the auditor's, still
  open at filing.
- **What follows is the maintainer's, not this record's:** the HOLD (17:25:07 item 1), the
  emergency slice (item 2 and the addendum), PL 9567's (c) delta (item 3) and FD 9572's essay
  amendment (item 4). This record quotes them and changes none.

## What this record does not decide

- DP-3 (above).
- The pins: the 17:22:47 entry confirms them ("an ordered list wires exactly as listed via the
  heap tie-break; the bundle hash unchanged"); they are PL 9567's, not this record's.
- FD 9572's severity, owner and the interim approval guard: the 17:10:08 entry's, unchanged.
