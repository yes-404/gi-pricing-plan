---
id: RL-1519
family: ruling
title: PL-1520 DP-F35-1, DP-F35-2 and DP-F35-3 decided — a trace step records what its step reads and declares, FR-246 binds every evaluating step, input and output steps are traced, NFR-500 reads the Trace contract
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-08            # original date 2026-10-01, set at the draft; minted 2026-10-08
owner: decision-maker
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: [RL-9954]
corrects: ~
relates: [FD-1246, RL-862, RL-863, CR-1247, CR-926, RL-1329, RL-1343, RL-1309, FR-212, FR-214, FR-215, FR-240, FR-246, FR-247, FR-258, NFR-490, NFR-500, WK-1178, WK-1250, FD-1374, FD-1381, OQ-1373, PL-1520, RL-1518, OQ-1453]
---

# RL-1519 — PL-1520 DP-F35-1, DP-F35-2 and DP-F35-3 decided

**Records cited by working id** (not yet minted; each is filled in at this record's mint):
PL-1520 (the F35 remedy leaf plan, draft PR #1051, read at head `9a2ebc56`);
FD-1374 (FR-246 unenforced, draft PR #1053, head `a7d2c99d`); FD-1381 (spec examples never validated, draft PR #1054); OQ-1373 (NFR-500's
"sampled-trace schema", draft PR #1052, head `d248f7d3`); OQ-1453 (PR #1048);
RL-1518 (DP-F35-5, this ruling's sibling). DP-F35-4 (the engine mechanism) is
**not** ruled here: it is ruled later, on Spike S1's evidence. *(2026-10-05, before mint:
FD 9773, FD 9772 and OQ 9774 have since minted as `FD-1374`, `FD-1381` and `OQ-1373`. Every
mention of them below, and the placeholders `{FD-1374}` and `{OQ-1373}`, resolve to those
ids. The GO's amendments quoted under "How this was ruled" keep the working ids as
quoted. PL 9776, OQ 9777 and RL 9770 are still working ids.)* *(2026-10-08, batch B4: PL 9776, OQ 9777
and RL 9770 are minted as PL-1520, OQ-1453 (#1230) and RL-1518, and every mention of them in
this record is re-pointed to those ids, outside the quoted entries.)*

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-f35`, spawned from
`.claude/roles/decision-maker.md`. Its command `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed
`CLAUDE_EFFORT=high`. The lead's brief relays the maintainer's raise from `to-lead.md` (a
local channel file, not in the repository), 2026-10-01: "PL-1520 (#1051): audit then ONE
decision-maker; the effort raise is given now (opus, --effort high)". This session did not
read the channel file; the quotation is the lead's relay. The maintainer's three amendments
to the GO, relayed in the same brief, bind this record: (1) OQ-1373's closure is verbatim
text for both mirrors; (2) (iii-b) rules two populations, each with release-note text;
(3) a "no" on mandatory `consumes` must state how FD-1374 is discharged.

Every fact below was read at `origin/main` **`1dd5e264195677b4a13268b80ac8673c2c027135`**
(`feat(rating): SL-1345 …`, #1045), the tree this record names. PL-1520 was read at its
draft head and its premises were written at `19155b50`; where a line has moved since, this
record gives the line at `1dd5e264`. Session window: 10:01–10:40 BST, 2026-10-01
(`TZ=Europe/London date`).

## Verified first, at `1dd5e264`

| Fact | Where, at `1dd5e264` |
|---|---|
| FR-246 names expression steps only: "Expression steps cannot reference anything outside their declared inputs — no globals, no environment, no time-of-day." | `docs/specs/03-rating-engine.md:148` |
| FR-215 already requires the declaration: "Every step … declares exactly which Derived Values it consumes and which it produces." | `03:84` |
| FR-258: "every step's id, label, consumed values, produced value, matched table row key, and elapsed time" | `03:175` |
| NFR-489 states its budget at p99: "Real-time scoring p99 < 50 ms server-side …" | `03:1193` |
| NFR-490 names no statistic; NFR-500 names no schema | `03:1194`, `03:1204` |
| The §4.1 example: the JSON fence opens at `03:233` and closes at `03:278`; steps `03:252-274`; the Invariants note `03:280-282` | read |
| The §4.5 trace example keys `s_area`'s `consumed` by `"as_at"`, not by the name read | `03:472` |
| The owned-codes list, with `LADDER_CLAMP_UNPLACEABLE`'s dated entry as the precedent form | `03:818` |
| The shape's graph invariants (FR-212, FR-214, re-production chain) | `packages/model-schema/src/model_schema/rating.py:393-475` (`_graph_invariants`) |
| `validate_algorithm` runs `STRING_CHECKS` then `ALGORITHM_CHECKS`; compile calls it and raises the **first** issue's code | `packages/pricing-core/src/pricing_core/rating/compile.py:359-396`, `:611-613` |
| Save path: `_issues_to_error` → `raise_first_issue` → `PlatformError(code, code.replace("_"," ").title(), 422, message)` | `backend/src/app/platform/rating_algorithms.py:76-90`, called at `:106` |
| Compile path: the `rating.compile` Job maps a code-named `ValueError` to a 422 `PlatformError` **before** `row.bundle` is rebound, so a refused compile leaves the version's bundle metadata as it was | `backend/src/app/platform/rating_versions.py:528-538` |
| A Job handler's `PlatformError` is stored as `JobError(code=exc.code, message=exc.detail or exc.title, retryable=False)` | `backend/src/app/worker/tasks.py:197-232` |
| `load_bundle` re-runs the **shape** (`RatingAlgorithm.model_validate`) but not `validate_algorithm` | `packages/pricing-core/src/pricing_core/rating/runtime.py:646`, `:662` |
| `/score` and the regression Job hydrate a stored bundle blob with `load_bundle`; nothing on either path re-compiles | `backend/src/app/api/score.py:221-227`; `backend/src/app/worker/rating_handlers.py:175` |
| A persisted trace is `trace.model_dump_json().encode()` | `backend/src/app/platform/traces.py:121`, `:246` |
| The ladder is read from output steps named `f"{rung}_minor"`; a clamp is placeable only on the source of the last rung before `constraints` | `packages/pricing-core/src/pricing_core/rating/ladder.py:52-84`; `compile.py:202-257` |
| `to_jdm` drops `sub_graphs`, so a mount is in neither the graph nor `content_hash` | `compile.py:477-502`; control B below |
| `bench-rating.py` prints NFR-490 "trace overhead at p99" against `BUDGET_TRACE_OVERHEAD` | `scripts/bench-rating.py:77`, `:970-973` |

## Ruled

In one line each; the reasons are in the sections that follow.

- **DP-F35-1: (b).** `consumed` holds the values of the names the step reads; `produced` holds
  its declared `produces`. R3's "full Trace" means every step.
  - **(i) (a):** no engine-internal key in `produced`.
  - **(ii):** refusal at save and compile; scope is every evaluating field, `as_at` included;
    `consumes` is **mandatory**. FD-1374 is discharged as PL-1520 writes it.
  - **(iii) (a)**, split: T1–T5 land in Task 1A's commit, T6–T9 in this record's mint PR, and
    T10 in Task 3.
  - **(iii-a) (b):** a new code, `RATING_STEP_UNDECLARED_READ`, 422.
  - **(iii-b):** saved algorithm versions are refused at their next compile, as intended.
    Compiled bundles are grandfathered at reload. Each population has release-note text.
  - **(iv) (a):** no marker on `Trace`.
  - **The §4.1 example** is replaced by T2 and T3, a complete valid algorithm. Shown passing
    `model_validate`, `compile_bundle` (stub payloads), the declared-reads check and a
    reference inventory.
- **DP-F35-2: (b).** `input` and `output` steps are traced, with `elapsed_us` 0.
- **DP-F35-3: (a).** NFR-500's schema is the trimmed `Trace` contract, measured uncompressed.
  **OQ-1373 is resolved and closed by this record** (T9).

## DP-F35-1 — what a `TraceStep` records per node

### Ruled: option (b), what the step reads

**`consumed` holds the value of every name the step reads**, as the step received it, keyed
by that name: its declared `consumes`, plus every name its `expr`, `key_expr`, `as_at`,
`feature_map` keys, `condition` and `clamp_bounds` read. **`produced` holds the value of each
name the step declares in `produces`.** Neither carries the context accumulated from other
steps. The reference set is computed once per bundle (PL-1520 Task 3's
`CompiledBundle.references`), never per quote.

**R3's "full Trace" (`03` §1.3) means every step, not every context value.** That is
FR-258's own word ("every step").

Why (b), against the plan's options:

- **(b) is the spec's own trace.** §4.5's `s_minprem` records `consumed`
  `{"office_premium_minor": 26_400, "min_premium_minor": 28_000}`: the premium and the bound
  it read, nothing else (`03:477-478`).
- **(a), declared names only, loses what a step used whenever the declaration is short.**
  Under this ruling's (ii) the two coincide for every algorithm that compiles from now on.
  They do not coincide for a bundle compiled before the check, which (iii-b) keeps serving.
  There, (a) would drop the clamp bound a step used, so the trace could not explain its own
  clamp; (b) records it.
- **(c), the full context, is the cost F35 measured** and the 2.58× of NFR-500 (`CR-926`).
- **(d), a caller option for the full context,** turns `QuoteContextOptions.trace` from a
  bool into an enum: a contract change for a debugging aid no requirement names.

### (i) Ruled (a): `produced` is the declared `produces` only

No engine-internal key reaches the trace: not `<step_id>__violated`, not `SL-1345`'s
`__before`, `__min`, `__max`, not the `$model_call_error` sentinel. A fired constraint is
recorded in the step's `violation` field, read from the engine's output **before** the trim
(PL-1520 Task 3 Step 4 keeps that order).

### (ii) Ruled: refusal; every evaluating step; `consumes` is mandatory

- **Mechanism (a): refuse an undeclared read at save and at compile.** Option (b), ordering
  the graph from reads, would make the declared graph a fiction the engine no longer
  follows. A reviewer reading `consumes` would be misled, and the diff of FR-219, the
  approval evidence, shows `consumes`.
- **Scope (a): every field a step evaluates, on every step type that has one.** That is an
  `expression`'s `expr`; a `table`'s or `lookup`'s `key_expr`; **a `lookup`'s `as_at`**; a
  `model_call`'s `feature_map` keys; a `constraint`'s `condition` and `clamp_bounds`. `as_at`
  is in scope because FR-221 makes it the step's explicit read of a context value ("The date
  source is explicit in the step"). It is the one field FD-1374's first predicate missed.
  Option (b), `expression` only, would enforce nothing that exists: all four under-declarers
  in the code are constraint steps (FD-1374), and the spec's example adds `key_expr`,
  `feature_map` and `as_at` cases.
- **Mandatory (a): yes.** A step that reads a name declares it in `consumes`. FR-215 already
  says so in words; nothing checks it today. **FD-1374 is therefore discharged as PL-1520
  already writes it**, with no alternative mechanism and no amended discharge: this ruling is
  its disposition item 1, Task 1A's red-first refusal tests and the two `03` example tests
  are item 2, Task 1A Step 5's four fixtures, fixed, with the old `s_clamp` shape kept as the
  named negative fixture, are item 3. Item 4, G2's interim acceptance line, stands until
  Task 1A merges.
- **Where the check lives (binding on the implementation):** in `validate_algorithm`'s
  `ALGORITHM_CHECKS` (`compile.py:359-363`), **never** in `RatingAlgorithm`'s shape
  validator. `load_bundle` runs the shape (`runtime.py:662`), so a shape-level check would
  refuse every already-compiled under-declaring bundle at hydration: option (iii-b)(a),
  rejected below.

### (iii) Ruled (a), with the split the maintainer set

| Text | Placement | Lands in |
|---|---|---|
| T1. FR-246, amended | `03:148`, the whole row | PL-1520 **Task 1A's commit** |
| T2. The §4.1 example | `03:233-278`, the whole JSON fence | Task 1A's commit |
| T3. The §4.1 Invariants note | `03:280-282`, replaced | Task 1A's commit |
| T4. The owned code | `03:818`, inserted | Task 1A's commit |
| T5. `RATING_ERROR_CODES` entry | `backend/src/app/errors.py`, after `"LADDER_CLAMP_UNPLACEABLE",` | Task 1A's commit |
| T6. FR-258, clarified | `03:175`, the whole row | **this record's mint PR** |
| T7. §4.5's trace example and its note | `03:472` token; a paragraph after `03:488` | this record's mint PR |
| T8. NFR-500, clarified | `03:1204`, the whole row | this record's mint PR |
| T9. OQ-1373 closed, both mirrors | `docs/open-questions.md` and `03` §10 | this record's mint PR (after batch B mints OQ-1373) |
| T10. `TraceStep`'s docstring | `packages/model-schema/src/model_schema/scoring.py`, `TraceStep` | PL-1520 Task 3 Step 6 |

T1–T5 land with the code that makes them true. T6–T9 state a reading and carry their own
"until delivered" clause, the form `RL-1343` used on FR-214. T3 is outside the fence, but it
states the invariants of the example beside it, and its old text contradicts the corrected
example (it says "exactly one upstream step", where the example's `office_premium_minor` has
a two-step re-production chain). So it moves with T2. **For the planner:** PL-1520's
Acceptance 12 names "the §4.1 example (`03:252-274`)". The maintainer already widened that to
the fence `03:233-278`. With T3 it reads `03:233-282`. Each text is byte-equal to this
record, which is what Acceptance 12 tests. This record names the difference; the lead decides
whether it is a method difference for the dispatch record or a delta to the plan.

### (iii-a) Ruled (b): a new code, `RATING_STEP_UNDECLARED_READ`

**Undeclared is not unresolved.** `RATING_GRAPH_UNRESOLVED_REF` (FR-212) means no step
produces the name: the author must add a producer. Here a producer exists and the step did
not declare the read: the author must add the name to `consumes`. One code for both would
make the caller's fix ambiguous.

- **Status 422**, at algorithm save and in the failed `rating.compile` Job.
- **Title** `Rating Step Undeclared Read` (`raise_first_issue` derives it from the code).
- **Message**, exactly: `step '<step_id>' reads <names> without declaring them in consumes
  (FR-246)`, where `<step_id>` is the step's id in Python `repr` form and `<names>` is the
  sorted list of undeclared names in Python `repr` form. Example: `step 's_minprem' reads
  ['min_premium_minor'] without declaring them in consumes (FR-246)`. This is PL-1520 Task
  1A Step 4's f-string. It carries names from the algorithm, never a quote value.
- **One issue per step, the first one wins.** Save and compile raise only the first issue in
  `validate_algorithm`'s order (string checks first, then the algorithm checks; this one is
  last). An algorithm with three under-declaring steps is refused three times, one step at a
  time. That is the existing contract for every save-time code, and not changed here.

### (iii-b) Ruled: two populations, each stated

"0 stored rows in the local databases" does not settle other installs, so the behaviour is
ruled, not the count.

**Population (a): saved Rating Algorithm versions that under-declare.** The check runs at
save (`rating_algorithms.py:106`) and at compile (`compile.py:611`). An algorithm version is
immutable once saved (`00` FR-4), so it is never saved again. **It is refused at its next
compile, and that is intended.** Compiling produces a new bundle, and FR-240 makes compile
the point where "the whole structure" is validated against the rules in force. The rule binds
forward: what is produced after it, never what exists (FR-257's "It applies forward, at
submit" is the same pattern). A refused compile takes nothing out of service. The Job raises
before `row.bundle` is rebound (`rating_versions.py:528-538`), so the version keeps its
bundle, and serving keeps hydrating it.

What the author sees:
- At save: HTTP **422**, problem `code` `RATING_STEP_UNDECLARED_READ`, `title` `Rating Step
  Undeclared Read`, `detail` the message above.
- At compile: `POST …/rating-versions/{id}/compile` returns **202** with a Job. The Job ends
  `failed` with `error.code` `RATING_STEP_UNDECLARED_READ`, `error.message` the message
  above, and `error.retryable` `false`.
- The fix: save a new algorithm version that lists each named value in the step's
  `consumes`, with an `input` step for any raw quote input. Then point the draft Rating
  Version at it and compile again.

**Release-note text, population (a), verbatim:**

> **Rating algorithms: a step must declare every value it reads (FR-246).** A step that reads
> a value it does not list in its `consumes` is now refused. This covers an expression, a
> table or lookup key, a lookup's as-at date, a model call's feature map, and a constraint's
> condition and clamp bounds. Saving such an algorithm returns HTTP 422 with code
> `RATING_STEP_UNDECLARED_READ`. Compiling a Rating Version whose algorithm has such a step
> fails the compile Job with the same code. The message names the step and the undeclared
> values, for example: `step 's_minprem' reads ['min_premium_minor'] without declaring them
> in consumes (FR-246)`. An algorithm version saved before this release is not changed, but
> it is refused at its next compile. A refused compile does not change the Rating Version's
> current bundle. To fix it, save a new algorithm version that adds each named value to the
> step's `consumes`, with an `input` step for any raw quote input, and compile again.

**Population (b): compiled or pinned bundles, at reload.** Ruled **(b), grandfathered.**
`load_bundle` runs the shape and not `validate_algorithm` (`runtime.py:662`), and the check
lives in `validate_algorithm` (ii). So a bundle compiled before the check keeps loading and
scoring, and its result does not change. Under DP-F35-1 (b) its traces record the undeclared
names in `consumed`, because the reference set reads the fields, not the declaration.
- Option (a), refused at reload, could take an approved or live Rating Version out of service
  on a code change. That is against R1 (`03` §1.3) in spirit.
- Option (c), migration, re-compiles with the reads added to `consumes`. That is a new graph
  and a new hash, so a new Rating Version through approval: a governed act per bundle, not a
  code task. It stays available to the version's owner and is never forced.
- **This binds DP-F35-4.** Whatever engine mechanism is ruled later must hydrate, and score
  unchanged, every bundle that hydrates today, including one with an undeclared read. If
  Spike S1 step 6 finds an added edge that closes a cycle, or a stored bundle that
  `load_bundle` refuses under a proposed wire, that mechanism is not acceptable as it stands.

**Release-note text, population (b), verbatim:**

> **Compiled bundles are not re-checked.** A Rating Version compiled before this release keeps
> loading and scoring exactly as before, including one whose algorithm reads a value it does
> not declare. Loading a stored bundle does not run the new check. Such a version is refused
> only if it is compiled again. To bring it under the check, compile a new Rating Version from
> a corrected algorithm version and take it through approval.

Both paragraphs go in the squash-commit body and the ledger, as PL-1520's Task 1A "Release
note" says.

### (iv) Ruled (a): no marker on `Trace`

The shape does not change. A persisted trace carries `bundle_hash`, and its row carries a
timestamp, so a trace from before the change can be dated. No reader of persisted `consumed`
exists yet: `05`'s monitors are a later phase. If FR-307's input-drift monitor later reads
`consumed`, its spec states what it needs then (`CLAUDE.md` §0).

## The corrected §4.1 example: a complete valid algorithm

**What changed, and why each change:**

| Defect at `1dd5e264` | Fix |
|---|---|
| FR-214: `premium_ladder`, `peril_risk_premium`, `decline_reasons` had no output step | The Premium Ladder is declared as its rung outputs (`risk_premium_minor`, `office_premium_minor`, `ipt_and_fees_minor`, `payable_premium_minor`), each an `output` step, which is how the code builds the ladder (`ladder.py:76-84`). `peril_risk_premium` gets an output step (FR-249). `premium_ladder` and `decline_reasons` leave `outputs`: they are fields of `ScoringResult` (§4.4, `03:433`, `:446`), not values a step produces. |
| FR-212: `s_out` consumed `payable_premium_pre_round`, which nothing produced | A new step `s_ipt` produces it: the office premium times `ipt_factor`. It is an `expression`, so it adds the `ipt_and_fees` rung. `s_out` cannot consume `office_premium_minor` directly: the clamp would then sit on the source of the `payable_premium` rung, which `_check_clamp_placement` refuses (`LADDER_CLAMP_UNPLACEABLE`, FR-240). |
| FR-212: `office_premium_minor` produced twice with no chain | `s_minprem` consumes `office_premium_minor` first, then `min_premium_minor`, and re-produces it: a valid re-production chain, and a placeable clamp (the clamp's first consumed name equals its produced name). |
| Five evaluating steps declared no `consumes` | Each declares exactly what it reads. `s_area` declares `effective_date`, its `as_at`. |
| Raw names with no producer: `postcode_outcode`, `effective_date` (contract, no input step); `distribution_channel`, `commission_factor`, `profit_factor`, `min_premium_minor` (neither) | An `input` step and an `input_contract` entry for each, and for `ipt_factor`. *(Amended 2026-10-01 10:29 BST, F1 below: for `effective_date` this is a choice, not a necessity. `score_one` already puts the Quote Context's top-level `effective_date` and `purpose` into the engine context (`score.py:910-912`). The contract entry adds one requirement: the caller also sends `effective_date` inside `inputs`, because `_validate_inputs` checks the contract against `ctx.inputs` only (`score.py:896`). T2 is unchanged.)* |
| `purpose` in the contract, read by no step | Removed. A quote's purpose is the Quote Context's own field (`03:419`, read by `_check_purpose_mount`, `score.py:395`), not an algorithm input. Listing it would require every quote to repeat it in `inputs`. |
| `mount_point: "s_ncd"` names no step | The mount is removed (`"sub_graphs": []`). A mount's port map and inlining are WK-1250 Slice 2's (`SL-1340`; `03` §4.11's header), so no mount the example could carry has a specified meaning yet. `s_ncd` is the step id **inside** §4.11's `ncd-ladder` fragment. |

**T2, verbatim.** It replaces `03:233-278` (`:240-285` at `ef5dc6e7`), the whole fence from its ```` ```json ```` line
to its closing ```` ``` ```` line (94 lines; sha256 of the text, with a final newline,
`6a35964d410f9b6c…`):

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
    {"name": "ipt_and_fees_minor", "type": "money_minor", "required": true},
    {"name": "peril_risk_premium", "type": "map<string, money_minor>", "required": false}
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
     "produces": ["risk_premium_minor", "peril_risk_premium"]},
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
     "rounding": {"mode": "half_even", "dp": 0}, "consumes": "payable_premium_pre_round"},
    {"step_id": "s_out_peril", "type": "output", "label": "Per-peril risk premium",
     "output_name": "peril_risk_premium",
     "rounding": {"mode": "half_even", "dp": 0}, "consumes": "peril_risk_premium"}
  ],
  "sub_graphs": []
}
```
````

**T3, verbatim.** It replaces the three lines `03:280-282` (`:287-289` at `ef5dc6e7`) (the paragraph beginning
`**Invariants** — DAG acyclic`):

```text
**Invariants** — DAG acyclic; every `consumes` name is `produced` by an upstream step, and a
name produced by more than one step is a re-production chain, each later producer consuming
it (here `s_minprem` clamps `office_premium_minor` in place), so it has one effective
producer; every declared output has an `output` step; no step is unreachable from an
`input` and unreferenced by an `output` (FR-212). Every name a step reads is declared in its
`consumes`, and each raw input enters through an `input` step (FR-246, FR-215). The Premium
Ladder is declared as its rung outputs, each an `output` step named `<rung>_minor` (FR-214,
FR-247); the ladder itself and `decline_reasons` are fields of the `ScoringResult` (§4.4),
not declared outputs. The example mounts no sub-graph: a mount's port map is WK-1250
Slice 2's (§4.11). *(Corrected {DATE}, {RL-1519} ({FD-1374}): the example declared no
`consumes` on five evaluating steps, consumed a name no step produced, declared three outputs
no step produced, and mounted a sub-graph at a step it did not define.)*
```

### The three checks, run on T2 before ruling

**How.** T2 was spliced into a copy of `03` at `1dd5e264` in place of `03:233-278`, and a
`diff` confirmed every other line identical. The copy was read the way PL-1520 Task 1A's
`_spec_example` reads it: the first ```` ```json ```` block after `### 4.1 `. Then three
steps ran, with the worktree's `uv` environment (`uv sync --all-packages --frozen`):
1. `RatingAlgorithm.model_validate` in full.
2. `compile_bundle` with Task 1A's `_StubResolver` and `_example_version` (stub payloads).
3. Task 1A's `referenced_names` and `_check_declared_reads`, both over the model's steps and
   over the raw dicts as `test_the_03_example_declares_every_read` does.

The script is in the appendix, sha256 prefix `128be51b4f78816e`.

**Output on T2** (`uv run python run_example.py 03-patched.md`, 2026-10-01, exit 0):

```text
extracted fence: lines 233-326 of 03-patched.md
[1] RatingAlgorithm.model_validate: VALID (19 steps, 8 inputs, 5 outputs, 0 sub_graphs)
    validate_algorithm issues: []
[2] compile_bundle (stub payloads): OK content_hash=sha256:643fab9d13aad174db9e2c7f933a43efafd85422988ff7e463d1872cd23417bd nodes=19 pins={'rate_tables': ['rate_table:motor-expense@3'], 'models': ['peril_structure:motor-gb-2026h2@2'], 'reference_tables': ['reference_table:ons-postcode-directory@7'], 'custom_objectives': []}
[3] declared-reads check (model steps): 0 undeclared reads
    declared-reads check (raw dicts):   0 undeclared reads
```

**A fourth check, because the three cannot see a mount.** The maintainer's bar includes "no
dangling reference of any kind". Control B below shows that a dangling `mount_point` passes
all three checks with an **identical** `content_hash`, because `to_jdm` drops `sub_graphs`.
So a reference inventory was run as well (appendix, sha256 prefix `20d8eddfdee17ba3`). It
checks every consume against a producer, every `mount_point` against a step, declared
outputs against output steps in both directions, and `input` steps against the
`input_contract` in both directions:

```text
steps=19 contract=['commission_factor', 'distribution_channel', 'driver_age', 'effective_date', 'ipt_factor', 'min_premium_minor', 'postcode_outcode', 'profit_factor']
declared outputs=['ipt_and_fees_minor', 'office_premium_minor', 'payable_premium_minor', 'peril_risk_premium', 'risk_premium_minor']; ladder rungs declared=['ipt_and_fees_minor', 'office_premium_minor', 'payable_premium_minor', 'risk_premium_minor']
refs a step names (pinned by the version)=['reference_table:ons-postcode-directory@7', 'peril_structure:motor-gb-2026h2@2', 'rate_table:motor-expense@3']; mounts=[]
reference inventory: 0 dangling references
```

**The same instruments on today's `03` (the control), exit 1:**

```text
[1] RatingAlgorithm.model_validate: REFUSED: Value error, declared output 'premium_ladder' has no output step (FR-214) [type=value_error, input_value={'slug': 'motor-gb', 'ver...mount_point': 's_ncd'}]}, input_type=dict]
[3] declared-reads (raw dicts): undeclared = {'s_area': ['effective_date', 'postcode_outcode'], 's_rp': ['driver_age', 'rating_area'], 's_expense': ['distribution_channel'], 's_office': ['commission_factor', 'expense_factor', 'profit_factor', 'risk_premium_minor'], 's_minprem': ['min_premium_minor', 'office_premium_minor']}
reference inventory: ["s_out consumes unproduced 'payable_premium_pre_round'", "mount_point 's_ncd' names no step (sub_graph:ncd-ladder@4)", "declared output 'decline_reasons' has no output step", "declared output 'peril_risk_premium' has no output step", "declared output 'premium_ladder' has no output step", "input_contract 'effective_date' has no input step", "input_contract 'postcode_outcode' has no input step", "input_contract 'purpose' has no input step"]
```

**Broken-input controls on T2**, each a one-token mutation of the ruled text:
- **A**, `profit_factor` dropped from `s_office`'s `consumes`. Check 1 passes, check 2
  passes, and check 3 prints `[('s_office', ['profit_factor'])]`. The reads check fires on
  the case the other two cannot see.
- **B**, the old mount `{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd"}` restored.
  Checks 1–3 all pass, with `content_hash` `sha256:643fab9d…` unchanged. The inventory prints
  `["mount_point 's_ncd' names no step (sub_graph:ncd-ladder@4)"]`, exit 1.
- **C**, `s_out`'s consume renamed to `payable_premium_pre_rnd`. Check 1 prints
  `step 's_out' consumes undefined value 'payable_premium_pre_rnd' (FR-212)`.

**What these runs do not cover**, stated as PL-1520 Acceptance 2a states it:
- The example is not hydrated (`load_bundle` needs real payloads for its three pins).
- It is not scored. So the ladder's reconciliation over the four rung outputs is not
  exercised here; only `_check_clamp_placement` is (inside `validate_algorithm`, which
  returned `[]`).

## DP-F35-2 — are the `input` and `output` steps traced?

**Ruled (b): yes.** FR-258 says "every step". `FD-1246` found the trace drops them, because
the trace builder skips the synthetic wire nodes they reach the engine as. Each entry is:
- an `input` step: `consumed` `{}`; `produced` its declared name and value, from the engine's
  `inputNode` output;
- an `output` step: `consumed` its declared name and value, from what reached the
  `outputNode`; `produced` `{}`;
- both: `elapsed_us` `0`, because the engine evaluates all `input` steps as one node and all
  `output` steps as one node, so no per-step time exists. Writing `0` states that; it is not
  a measurement.

Option (a), a clarification that they are not traced, would make FR-258 say less than it
does to match the code, which is the direction `CLAUDE.md` §0 says to justify, not assume.
Under DP-F35-1 (b) each such entry is a few bytes. `SL-1340`'s inlined ports are then
traceable without a second ruling. **Costs, accepted:** `score/compare`'s `unchanged` counts
rise (PL-1520 Acceptance 7), and `test_rating_score.py`'s `isdisjoint` assertion inverts
(Task 3 Step 5). `FD-1246`'s disposition, the decision-maker's ruling, is this paragraph.
Its delivery is PL-1520 Task 3.

## DP-F35-3 — what NFR-500's "sampled-trace schema" names

**Ruled (a): the `Trace` contract after the F35/F55 trim, measured uncompressed.**
- The schema is `model_schema.scoring.Trace`, published as
  `docs/contracts/schemas/scoring.schema.json` `$defs.Trace`, with each `TraceStep` as T6
  clarifies FR-258.
- The size of one sampled trace is the UTF-8 byte length of `Trace.model_dump_json()`,
  uncompressed. That is exactly the payload the platform persists
  (`backend/src/app/platform/traces.py:121`).
- GB is 10^9 bytes, as `scripts/bench-trace-size.py` already reads it.

Why (a), as `CR-1247` Proposal 11 recommended and the maintainer accepted ("Accepted: NFR-500
is raised as an OQ with the recommendation (a). The decision-maker rules it."):
- the budget rests on a shape `model-schema` defines and a test can measure;
- (b) would rest it on a storage codec that a later infrastructure choice can change
  silently;
- (c) adds that codec dependence back for no gain while (a) is expected to pass with an
  order of magnitude to spare (`CR-1247`'s extrapolation, about 12 GB/year, labelled there as
  a projection, not a verdict).

A compression applied at rest is headroom, never part of the budget.

**This resolves OQ-1373, and this record closes it**, citing this ruling as the
resolver: the decision-maker's §1.6 OQ duty. The closing text for both mirrors is T9. It is
applied in this record's mint PR. The mint order is batch B, which mints OQ-1373, before this
record, so T9 names the minted id at the mint. **Not ruled here:** NFR-500's population is
"1 % sampling of 50 M annual quotes"; FR-259 also keeps 100 % of declines and errors. That
gap is `CR-1247`'s observation. It is left to NFR-500's re-measure (PL-1520 Acceptance 9),
not widened here.

## The spec and code texts, verbatim

**Placeholders**, and only these: `{DATE}` is the date the text is applied (`YYYY-MM-DD`).
`{RL-1519}`, `{RL-1518}`, `{FD-1374}`, `{OQ-1373}` and `{PL-1520}` are those records' minted
ids, written `RL-<n>`, `FD-<n>`, `OQ-<n>`, `PL-<n>`. Every other character is final.

**The executor applies each text above byte-for-byte; authorship stays with the
decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296
precedent). Any executor wording is a stop.**

T2 and T3 are above. The rest follow.

### T1 — FR-246, replacing the whole row at `03:148` (Task 1A's commit)

```text
| **FR-246** | Expression steps cannot reference anything outside their declared inputs — no globals, no environment, no time-of-day. `now()` does not exist; a quote timestamp is an input. *(Amended {DATE}, {RL-1519} ({FD-1374}): a step's declared inputs are its `consumes` (FR-215), and the rule binds every step that evaluates a field, not only `expression` steps: an `expression`'s `expr`, a `table`'s or `lookup`'s `key_expr`, a `lookup`'s `as_at` (FR-221), a `model_call`'s `feature_map` keys, and a `constraint`'s `condition` and `clamp_bounds`. Every name such a field reads is declared in the step's `consumes`, and a raw input reaches the graph through an `input` step. Saving an algorithm and compiling a bundle refuse a step that reads a name it does not declare, with `RATING_STEP_UNDECLARED_READ` (422); the message names the step and each undeclared name, and carries no quote input. Loading a stored bundle does not run the check: a bundle compiled before it keeps loading and scoring unchanged, and is refused only if it is compiled again.)* |
```

### T4 — the owned code, at `03:818` (Task 1A's commit)

On the line of `03` §5.1's owned-code list that ends with it (`03:936` at `ef5dc6e7`;
`03:818` at `1dd5e264`), replace the one occurrence of
`` `MODEL_REFERENCE_MODE_INCONSISTENT`, `` with:

```text
`RATING_STEP_UNDECLARED_READ` *(added {DATE}, {RL-1519}: 422 at algorithm save and at bundle compile, FR-246's declared-reads check; the message names the step and each undeclared name and carries no quote input)*, `MODEL_REFERENCE_MODE_INCONSISTENT`,
```

### T5 — `backend/src/app/errors.py` (Task 1A's commit)

Immediately after the line `        "LADDER_CLAMP_UNPLACEABLE",` in `RATING_ERROR_CODES`, insert:

```python
        # FR-246 ({RL-1519}): a step reads a name it does not declare, refused at save and at compile.
        "RATING_STEP_UNDECLARED_READ",
```

### T6 — FR-258, replacing the whole row at `03:175` (this record's mint PR)

```text
| **FR-258** | **Trace**: on request, scoring returns every step's id, label, consumed values, produced value, matched table row key, and elapsed time, plus the bundle hash and rating version reference. Traces are the same structure in real-time and batch. *(Clarified {DATE}, {RL-1519}, on `FD-1246` and register rows F35 and F55: a step's consumed values are the values of the names the step reads, each as the step received it and keyed by that name: its declared `consumes` and every name its `expr`, `key_expr`, `as_at`, `feature_map` keys, `condition` or `clamp_bounds` reads (FR-246). Its produced value is the value of each name it declares in `produces`. Neither carries the evaluation context accumulated from other steps, nor an engine-internal key (`<step_id>__violated`, or a clamp's `__before`, `__min` and `__max`); a constraint that fired is recorded in the step's `violation`. "Every step" includes `input` and `output` steps: an `input` step records `consumed` `{}` and its produced name and value, and an `output` step records its consumed name and value and `produced` `{}`, each with `elapsed_us` 0, because the engine evaluates all `input` steps as one node and all `output` steps as one node. R3's "full Trace" (§1.3) means every step, not every context value. `Trace` carries no marker of which reading a persisted trace holds; its `bundle_hash` and its stored timestamp date it. Delivered by WK-1178's F35 slice ({PL-1520}); until that slice merges, `consumed` and `produced` carry the engine's accumulated context and `input` and `output` steps are not traced.)* |
```

### T7 — §4.5's trace example and its note (this record's mint PR)

1. On line `03:496` (`03:472` at `1dd5e264`), replace the one occurrence of `"as_at": "2026-10-20"` with
   `"effective_date": "2026-10-20"`. The `consumed` entry is keyed by the name the step reads.
   `s_area`'s `as_at` names `effective_date`.
2. After line `03:512` (`03:488` at `1dd5e264`) (the paragraph beginning `*(Added 2026-10-01, `PL-1348` (SL-1345)`),
   insert one blank line and then this paragraph:

```text
*(Clarified {DATE}, {RL-1519}: the example shows two of the trace's steps. A full trace has one entry per step of the algorithm, `input` and `output` steps included, and each `consumed` is keyed by the names the step reads (FR-258, as clarified); `s_area` reads `effective_date` through its `as_at`.)*
```

### T8 — NFR-500, replacing the whole row at `03:1204` (this record's mint PR)

```text
| **NFR-500** | Trace storage: 1 % sampling of 50 M annual quotes stays under 200 GB/year with the sampled-trace schema. *(Clarified {DATE}, {RL-1519} ({OQ-1373}, `CR-1247` Proposal 11): "the sampled-trace schema" is the `Trace` contract, `model_schema.scoring.Trace`, published as `docs/contracts/schemas/scoring.schema.json` `$defs.Trace`, with each `TraceStep` as FR-258's clarification of {DATE} states it. A sampled trace's size is the UTF-8 byte length of `Trace.model_dump_json()`, uncompressed: the payload the platform persists per sampled trace (`backend/src/app/platform/traces.py`). GB is 10^9 bytes. A compression applied at rest is headroom, never part of the budget. `scripts/bench-trace-size.py` is the projection.)* |
```

### T9 — OQ-1373 closed, both mirrors (this record's mint PR, after OQ-1373 is minted)

**`docs/open-questions.md`**, the row whose ID cell names {OQ-1373}. Replace exactly these
cells and leave every other cell, and the rest of the Question cell, byte-unchanged:

- **ID cell:** `~~**{OQ-1373}**~~ ✔`
- **Question cell:** replace its first sentence, `**What does NFR-500's "sampled-trace schema" name?**`, with:

```text
~~**What does NFR-500's "sampled-trace schema" name?**~~ **DECIDED {DATE}: (a), the `Trace` contract after the F35/F55 trim, measured uncompressed, by {RL-1519}.**
```

- **Recommendation cell**, whole:

```text
**Decided (a)** ({RL-1519}, DP-F35-3, at effort high). The budget is read against the `Trace` contract (`model_schema.scoring.Trace`; `docs/contracts/schemas/scoring.schema.json` `$defs.Trace`), with each `TraceStep` as the same ruling clarifies FR-258: a sampled trace's size is the UTF-8 byte length of `Trace.model_dump_json()`, uncompressed, the payload `backend/src/app/platform/traces.py` persists. A compression at rest is headroom, not budget. NFR-500 carries the dated clarification in `03` §9. Re-measured with `scripts/bench-trace-size.py` in WK-1178's F35 slice ({PL-1520}, Acceptance 9).
```

- **Status cell**, whole:

```text
decided {DATE} ({RL-1519}; owner WK-1178, re-measured in the F35 slice, raised 2026-10-01, decided {DATE})
```

**`docs/specs/03-rating-engine.md` §10**, the row whose ID cell names {OQ-1373}. Replace the
whole row with:

```text
| ~~**{OQ-1373}**~~ ✔ | ~~**What does NFR-500's "sampled-trace schema" name?**~~ **DECIDED {DATE}: (a), the `Trace` contract after the F35/F55 trim, measured uncompressed, by {RL-1519}.** See NFR-500's dated clause. Mirrored in `docs/open-questions.md`. Status: **decided** (owner WK-1178, re-measured in the F35 slice, raised 2026-10-01, decided {DATE}). |
```

### T10 — `TraceStep`'s docstring (PL-1520 Task 3 Step 6)

Replaces `TraceStep`'s docstring in `packages/model-schema/src/model_schema/scoring.py`. This
is Task 3 Step 6's text with `as_at` added (DP-F35-1 (ii)'s scope), so the docstring and
FR-258 name the same fields:

```python
    """One node of a `Trace` (FR-258, `scoring.schema.json:71-86`).

    `consumed` holds the value of every name the step reads (its declared `consumes` and
    every name its expression, condition, clamp bounds, table key, as-at date or feature map
    reads), as the step received it; `produced` holds its declared `produces`. Never the
    engine's accumulated context (F35, F55; {RL-1519}). `input` and `output` steps are
    traced with `elapsed_us` 0, because the engine evaluates each kind as one node.
    """
```

## What it obliges

- **PL-1520 Task 1A**, in one commit:
  - T1–T5, byte-for-byte;
  - `_check_declared_reads` in `ALGORITHM_CHECKS`, never in the `RatingAlgorithm` shape;
  - the code and message of (iii-a);
  - the four fixtures fixed, and the named negative fixture kept;
  - both release-note paragraphs of (iii-b), in the squash body and the ledger.
- **PL-1520 Task 3:** the trace content of DP-F35-1 (b) and (i), the `input` and `output`
  entries of DP-F35-2 (b), and T10.
- **This record's mint PR:** T6, T7, T8 and T9, after batch B has minted OQ-1373, and the
  record set `active`.
- **DP-F35-4's later ruling:** keep every bundle that hydrates today hydrating and scoring
  unchanged ((iii-b)), read against Spike S1 step 6.
- **NFR-500's re-measure** (PL-1520 Acceptance 9) reads the bytes of
  `Trace.model_dump_json()`, uncompressed, as T8 states.

## Acceptance — the violation that must become detectable

Each case is seen red before the change that turns it green (`CLAUDE.md` §13). Cases 1–4 and
6–7 are PL-1520's own tests. Case 5 is a test the plan does not yet carry (planner item 6
below).
1. **A constraint reads an undeclared name** (the old `s_clamp`). `validate_algorithm`
   returns one issue: `RATING_STEP_UNDECLARED_READ`, step `s_clamp`, and a message naming
   `min_premium_minor` and containing `FR-246`. At `1dd5e264` it returns none.
2. **An expression reads an undeclared name** (`s_office` reading `sanity_cap_minor`). The
   same code, step `s_office`.
3. **A lookup's `as_at` is a read.** `referenced_names` of a lookup with
   `as_at: "effective_date"` contains `effective_date` (Task 1A's extractor test, last
   assertion).
4. **`03`'s own example.** Both Task 1A example tests are red on today's `03`, on the causes
   pasted above (FR-214 first; five steps under-declaring). They are green on T2.
5. **A compiled bundle is not re-checked** ((iii-b) population (b)). Build a `Bundle` from the
   named negative fixture with `to_jdm` and `bundle_hash`, bypassing `validate_algorithm` as a
   bundle compiled before the check was. `load_bundle` accepts it, and `score_one` returns the
   same `ScoringResult` as the declared fixture, with `trace`, `timing_ms` and `bundle_hash`
   blanked. **The
   broken-input proof:** move the check into `RatingAlgorithm`'s shape validator, and the test
   fails at `load_bundle`.
6. **The trace holds the reference set.** `s_clamp`'s `consumed` is exactly
   `{"office_premium_minor", "min_premium_minor"}`, and its `produced` holds no `__violated`
   key (PL-1520 Acceptance 3). At `1dd5e264` `consumed` holds the whole context.
7. **Every step is traced.** Each `step_id` of the fixture appears once in `trace.steps`,
   `input` and `output` steps included (PL-1520 Acceptance 4). At `1dd5e264` they are absent
   (`FD-1246`).

## For the planner and the lead (named here, not edited into PL-1520)

1. **Acceptance 12's `03` range** reads `03:233-282` under this ruling (T2 and T3), plus T1
   and T4. See (iii).
2. **Task 1A's example tests cannot see a mount.** Control B proves it. The ruled example
   carries none, so they pass correctly today. But a later edit that re-adds a dangling mount
   would pass them too. A one-line assertion in
   `test_the_03_example_validates_in_full_and_compiles` would close that: every
   `mount_point` names a step of the example. The test is the planner's to amend, so this
   record recommends it and does not rule it.
3. **Line drift since `19155b50`.** PL-1520's premises cite `score.py:726-727` and
   `_build_trace` at `:700-739`; at `1dd5e264` `_build_trace` starts at `score.py:781`.
   NFR-489 and NFR-490 are at `03:1193-1194`, not `:1190-1191`, and `validate_algorithm`'s
   compile call is `compile.py:611`, not `:550`. The executor re-derives each at the build
   base.
4. **T10** differs from Task 3 Step 6's sample by the words "as-at date" and the minted id.
   That is a method difference.
5. **(iii-b) binds DP-F35-4's ruling** (above). S1 step 6 is the evidence it reads.
6. **Acceptance case 5 has no test in PL-1520.** It proves (iii-b) population (b) and fails on
   broken input. It adds one test to Acceptance 2a's count of 6, so it is the planner's to
   add, as a delta or in the dispatch record, as the lead decides.

## Observed, not ruled (for the lead)

- **A compile has no status guard.** `POST …/rating-versions/{id}/compile`
  (`backend/src/app/api/models.py:1237-1261`) and `compile_rating_version`
  (`rating_versions.py:395`) read no status. This session found nothing that stops an
  approved or live version from being re-compiled, and a successful re-compile rebinds
  `row.bundle`. That sits uneasily with `00` FR-4. It was not traced further, so it is a
  candidate for the auditor, not a finding.
- **An output step's rounding is not applied to a non-money output.** `_build_outputs`
  (`score.py:729-758`) serves a non-rung, non-`money_minor` output (such as T2's
  `peril_risk_premium` map) as the engine's value, unrounded. Its `RoundSpec` is required by
  the shape and then unused. Related to `OQ-1316`.
- ~~**The Quote Context's top-level `effective_date` does not reach the engine.** Scoring
  validates and evaluates `ctx.inputs` (`score.py:333`), so an algorithm that reads
  `effective_date` must receive it in `inputs` too. T2 therefore declares it as an input,
  which is the code's model today. §4.4's example puts it at the top level only.~~
  *(Struck 2026-10-01 10:29 BST, F1 below: false.)* **The input contract is checked against `ctx.inputs`
  only.** `score_one` validates with `_validate_inputs(algorithm, ctx.inputs)`
  (`score.py:896`). It builds the engine context as `{"effective_date": …, "purpose": …,
  **ctx.inputs}` (`score.py:910-912`), so the top-level `effective_date` does reach the
  engine. T2's non-nullable `effective_date` contract entry therefore makes a caller repeat
  it inside `inputs`. A §4.4-style quote that carries it only at the top level fails with
  `INPUT_CONTRACT_VIOLATION`.
- **§4.4's request example and T2 no longer describe one algorithm.** This is partly
  pre-existing. T2's contract requires `commission_factor`, `profit_factor`,
  `min_premium_minor` and `ipt_factor`, and §4.4's `inputs` (`03:422-423`) carries none of
  them. §4.4 carries `vehicle_group`, `ncd_years` and `annual_mileage`, which T2 does not
  declare. This is evidence for FD-1381 (spec examples are never validated). No
  T2 change is required.
- **`RatingAlgorithm`'s docstring** (`rating.py:375-382`) still says "exactly one upstream
  step", as `03:280` did. It is code text, so T3 does not reach it.

## Amendment, 2026-10-01 10:29 BST — F1 (auditor-1060, LOW, adopted by the lead)

The auditor reviewed #1060 at `d1a7bec4`. It reproduced the example's four checks and
controls A–C from this record's text, and found one false statement. The statement was in
"Observed, not ruled" and in the T2 change table: that the Quote Context's top-level
`effective_date` does not reach the engine. `score.py:910-912` (at `1dd5e264`) puts it, and
`purpose`, into the engine context. The claim had been inferred from `_validate_inputs`
alone, without reading where `score_one` builds the context. The bullet is struck and
corrected, and the table row is annotated, above.

**No ruled content changed.** DP-F35-1 to -3, T1–T10, the release notes and the example are
byte-identical. T2's `effective_date` input step and contract entry stay. That is a valid
and complete reading, and the correction only changes the reason given for it. The §4.4
mismatch is recorded above for FD-1381.

## Amendment, 2026-10-05: citations re-read at main `ef5dc6e7`, before mint

Citation and currency update only. Nothing ruled above changes (decision-maker `dm-amend-2`,
on the lead's brief of 2026-10-05 10:50 BST, which adopted the batch-2 triage).

- **Minted working ids.** FD 9773 = `FD-1374`, FD 9772 = `FD-1381`, OQ 9774 = `OQ-1373`
  (each record names its working id). They are resolved once, in the dated sentence under
  *Records cited by working id*, and added to `relates:`. T9's precondition, "after OQ-1373
  is minted", is met: both `OQ-1373` mirror rows exist at `ef5dc6e7`
  (`docs/open-questions.md:141`, `03:1369`), and their question sentence is T9's find text.
- **The T-section anchors re-read at `ef5dc6e7`.** The rows T1, T6 and T8 replace (FR-246,
  FR-258, NFR-500) are byte-identical to `1dd5e264`. FR-246 is still `03:148` and FR-258
  `03:175`; NFR-500 moved `:1204` → `:1341`. The §4.1 fence and Invariants note (T2, T3)
  and the §4.5 example (T7) are byte-identical, offset by +7 and +24: `03:233-278` →
  `:240-285`, `:280-282` → `:287-289`, `:472` → `:496`, `:488` → `:512`. T4's find text
  occurs once, at `03:936` (`:818` before). T5's `"LADDER_CLAMP_UNPLACEABLE",` line is
  `errors.py:321`. The headings and the placement table above keep their `1dd5e264`
  lines; the bodies now give both.
- **Read across, not changed:** RL-1474 (#1055) T3 inserts a paragraph after the
  one *ending* `and unreferenced by an `output` (FR-212).`. This record's T3 replaces that
  paragraph, and its text keeps the sentence but not at the end. Whichever T3 is applied
  second may not find its anchor. Raised to the lead.
- **The *Verified first* table and the other dated sections are readings at `1dd5e264`** and
  resolve there. Moved since, for the path-qualified cites: NFR-489/490 `03:1193-1194` →
  `:1330-1331`; §4.4's example `:419` → `:443`, `:422-423` → `:446-447`; §4.5 `:477-478` →
  `:501-502`; `rating.py:375-382` → `:376-383`, `:393-475` → `:394-476`;
  `rating_versions.py:395` → `:423`, `:528-538` → `:557-567`; `api/score.py:221-227` →
  `:265-271`; `api/models.py:1237-1261` → `:1237-1266`; `traces.py:246` → `:253`;
  `bench-rating.py:970-973` → `:978-981`. `compile.py:611`, `score.py:781` and `:910-912`,
  `runtime.py:646` and `:662`, `traces.py:121`, `rating_algorithms.py:76-90` and `:106`, and
  `bench-rating.py:77` and `:488-492` are unchanged. Bare continuation cites (`:N` after a
  path) were not each re-mapped.
- `tree:` stays `1dd5e264`, the tree the record was verified at. `status:` stays `draft`,
  because this record makes setting it `active` a step of its own mint PR (*What it
  obliges*). `created:` changes at the mint.

## Appendix — the scripts, verbatim

Both ran from the scratchpad. They are reproduced here because a scratchpad does not persist
(the inline-sources rule for a spike).

`run_example.py` (sha256 prefix `128be51b4f78816e`), run as
`uv --directory <worktree> run python run_example.py <03 file>`:

```python
"""DP-F35-1: run the three checks on 03 §4.1's example, as PL-1520 Task 1A's two example tests do.

Usage: uv run python run_example.py <path to a 03-rating-engine.md>
The extraction, `_StubResolver` and `_example_version` are PL-1520 Task 1A Step 1's, verbatim
in logic. `referenced_names` and `_check_declared_reads` are Task 1A Steps 3 and 4's.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from uuid import uuid4

from model_schema.rating import RatingAlgorithm, RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle, validate_algorithm

_STRING = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
_NAME = re.compile(r"(?<![\w.$])([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*\()")
_KEYWORDS = frozenset({"true", "false", "null", "and", "or", "not", "in"})


def _names_in(text: str) -> set[str]:
    return {m for m in _NAME.findall(_STRING.sub(" ", text)) if m not in _KEYWORDS}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    return [str(v) for v in (value if isinstance(value, list) else [value])]


def referenced_names(node: Mapping[str, Any]) -> frozenset[str]:
    names = set(_as_list(node.get("consumes")))
    for field in ("expr", "condition"):
        if isinstance(node.get(field), str):
            names |= _names_in(node[field])
    for bound in (node.get("clamp_bounds") or {}).values():
        names |= _names_in(str(bound))
    for key in _as_list(node.get("key_expr")):
        names |= _names_in(key)
    if isinstance(node.get("as_at"), str):
        names |= _names_in(node["as_at"])
    names |= set((node.get("feature_map") or {}).keys())
    return frozenset(names)


_DECLARED_READ_STEP_TYPES = frozenset({"expression", "table", "lookup", "model_call", "constraint"})


def check_declared_reads(algo: RatingAlgorithm) -> list[tuple[str, list[str]]]:
    out = []
    for step in algo.steps:
        if step.type not in _DECLARED_READ_STEP_TYPES:
            continue
        undeclared = sorted(referenced_names(step.model_dump()) - set(_as_list(step.consumes)))
        if undeclared:
            out.append((step.step_id, undeclared))
    return out


def spec_example(spec: Path) -> dict[str, Any]:
    lines = spec.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("### 4.1 "))
    opening = next(i for i in range(start, len(lines)) if lines[i].startswith("```json"))
    closing = next(i for i in range(opening + 1, len(lines)) if lines[i].startswith("```"))
    print(f"extracted fence: lines {opening + 1}-{closing + 1} of {spec.name}")
    payload: dict[str, Any] = json.loads("\n".join(lines[opening + 1 : closing]))
    return payload


class _StubResolver:
    def __init__(self, algorithm_ref: str, algorithm: dict[str, Any]) -> None:
        self._algorithm_ref = algorithm_ref
        self._algorithm = algorithm

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if str(ref) == self._algorithm_ref:
            return ResolvedArtifact(status="approved", payload=self._algorithm)
        return ResolvedArtifact(status="approved", payload={"stub_for": str(ref)})


def example_version(example: dict[str, Any]) -> RatingVersion:
    steps = example["steps"]
    rate = [s["rate_table_ref"] for s in steps if s.get("rate_table_ref")]
    reference = [s["reference_table_ref"] for s in steps if s.get("reference_table_ref")]
    models = [s.get("model_ref") or s["peril_structure_ref"] for s in steps if s["type"] == "model_call"]
    modes = {s["mode"] for s in steps if s["type"] == "model_call"}
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": example["slug"],
        "version": example["version"], "status": "draft", "dataset_version_id": str(uuid4()),
        "model_ref": models[0] if models else None,
        "created_at": "2026-10-01T00:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-10-01T00:00:00Z",
        "algorithm_ref": f"rating_algorithm:{example['slug']}@{example['version']}",
        "pins": {"rate_tables": rate, "models": models, "reference_tables": reference,
                 "custom_objectives": []},
        "model_reference_mode": modes.pop() if len(modes) == 1 else "exact",
    })


def main() -> int:
    example = spec_example(Path(sys.argv[1]))
    # Check 3 stated on its own, over the raw dicts (Task 1A's test_the_03_example_declares_every_read).
    raw = {
        s["step_id"]: sorted(referenced_names(s) - set(_as_list(s.get("consumes"))))
        for s in example["steps"] if s["type"] not in ("input", "output")
    }
    raw = {k: v for k, v in raw.items() if v}
    print("[1] RatingAlgorithm.model_validate:", end=" ")
    try:
        algo = RatingAlgorithm.model_validate(example)
    except Exception as exc:  # noqa: BLE001
        print("REFUSED:", str(exc).splitlines()[1].strip() if "\n" in str(exc) else exc)
        print("[3] declared-reads (raw dicts): undeclared =", raw)
        return 1
    print(f"VALID ({len(algo.steps)} steps, {len(algo.input_contract)} inputs, "
          f"{len(algo.outputs)} outputs, {len(algo.sub_graphs)} sub_graphs)")
    print("    validate_algorithm issues:", validate_algorithm(algo))
    version = example_version(example)
    print("[2] compile_bundle (stub payloads):", end=" ")
    try:
        bundle = asyncio.run(compile_bundle(version, _StubResolver(str(version.algorithm_ref), example)))
    except Exception as exc:  # noqa: BLE001
        print("REFUSED:", exc)
        return 1
    print(f"OK content_hash={bundle.content_hash} nodes={len(bundle.graph.nodes)} "
          f"pins={bundle.pins.model_dump(mode='json')}")
    print("[3] declared-reads check (model steps):", check_declared_reads(algo) or "0 undeclared reads")
    print("    declared-reads check (raw dicts):  ", raw or "0 undeclared reads")
    return 0 if not raw and not check_declared_reads(algo) else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

`inventory.py` (sha256 prefix `20d8eddfdee17ba3`), standard library only, run as
`python3 inventory.py <03 file>`:

```python
"""DP-F35-1: every reference in 03 §4.1's example resolves (the maintainer's "no dangling reference of any kind").

Usage: python3 inventory.py <path to a 03-rating-engine.md>. Stdlib only; reads the fence the
same way PL-1520 Task 1A's `_spec_example` does.
"""
import json
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith("### 4.1 "))
op = next(i for i in range(start, len(lines)) if lines[i].startswith("```json"))
cl = next(i for i in range(op + 1, len(lines)) if lines[i].startswith("```"))
ex = json.loads("\n".join(lines[op + 1 : cl]))


def L(v):
    return [] if v is None else (v if isinstance(v, list) else [v])


steps = ex["steps"]
ids = {s["step_id"] for s in steps}
produced = {n for s in steps for n in L(s.get("produces"))}
contract = {f["name"] for f in ex["input_contract"]}
declared_out = {o["name"] for o in ex["outputs"]}
out_steps = {s["output_name"] for s in steps if s["type"] == "output"}
input_names = {s["input_name"] for s in steps if s["type"] == "input"}
rung_names = {f"{r}_minor" for r in ("risk_premium", "expense_loading", "commission", "profit_loading",
              "office_premium", "optimisation_adjustment", "constraints", "instalment_loading",
              "ipt_and_fees", "payable_premium")}
problems = []
for s in steps:
    for n in L(s.get("consumes")):
        if n not in produced:
            problems.append(f"{s['step_id']} consumes unproduced {n!r}")
for m in ex.get("sub_graphs", []):
    if m["mount_point"] not in ids:
        problems.append(f"mount_point {m['mount_point']!r} names no step ({m['ref']})")
problems += [f"declared output {n!r} has no output step" for n in sorted(declared_out - out_steps)]
problems += [f"output step {n!r} is not a declared output" for n in sorted(out_steps - declared_out)]
problems += [f"input step reads {n!r}, not in input_contract" for n in sorted(input_names - contract)]
problems += [f"input_contract {n!r} has no input step" for n in sorted(contract - input_names)]
for s in steps:
    if s["type"] == "input" and L(s.get("produces")) != [s["input_name"]]:
        problems.append(f"{s['step_id']} produces {s.get('produces')!r}, not its input_name")
pins = [s.get(k) for s in steps for k in ("rate_table_ref", "reference_table_ref", "model_ref",
        "peril_structure_ref") if s.get(k)]
print(f"steps={len(steps)} contract={sorted(contract)}")
print(f"declared outputs={sorted(declared_out)}; ladder rungs declared={sorted(declared_out & rung_names)}")
print(f"refs a step names (pinned by the version)={pins}; mounts={ex.get('sub_graphs')}")
print("reference inventory:", "0 dangling references" if not problems else problems)
sys.exit(1 if problems else 0)
```
