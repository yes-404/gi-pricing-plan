---
id: RL-1394
family: ruling
title: PL-1395 DP-S1-1 to DP-S1-6 decided — each scoring pass sees only its own bundle's contract, purpose and date are stamped per run, the exposure column is exposure_years, the signatures take versions and a resolver, S above six is a labelled bound, and run-level frame faults are VALIDATION_FAILED; T1 to T9 adopted, five amended
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-03              # the mint date (check 31); ruled 2026-10-03
owner: decision-maker
tree: ee584dccb89bbf8d34cf40ef9ec52e10a4145598
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1395, PL-1267, RL-1264, RL-1361, RL-1184, RL-1263, RS-1201, FD-1374, SL-1385, SL-1345, FR-263, FR-264, FR-265, FR-266, FR-273, FR-213, FR-218, FR-219, FR-237, FR-252]
---

# RL-1394 — PL-1395 DP-S1-1 to DP-S1-6 decided

## How this was ruled

- **Filed under working id 9740, allocated by the lead; minted as `RL-1394`** (2026-10-03,
  `python3 scripts/doc-id.py next`), in one PR with `PL-1395`. Both ids are the lead's; the
  working ids 9740 and 9741 survive only where this paragraph and the mint-pass note below
  name them.
- **The plan ruled on** is WK-673 Slice 1's leaf plan, then working id 9741 on PR #1088 at
  `a6b80982` (`status: draft`, `tree: 7b7757b3`), now `PL-1395`. Its Decision points table is at `:231-240` of that file;
  its proposed texts T1 to T9 are its Appendix, `:478-635`.
- **Mandate:** the lead's GO in `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
  "2026-10-03 19:53:36 BST — GO: auditor-9741 … and dm-673 …", condition 2, verbatim:

  > 2. dm-673 rules DP-S1-1 (§4.8 undeclared column) by reading 01/03 §4.8 itself and quoting the clause it rules on (my acceptance condition 2 for PL-1267). Each DP gets options, the choice and the reason. Any later-phase capability is a spec change only (CLAUDE.md §0).

- **Decided by the decision-maker, 2026-10-03.** Drafted from 19:54:08 BST
  (`TZ=Europe/London date`), in the decision-maker's own worktree, on branch
  `rl-9740-wk-673-s1-dp-ruling`, cut from origin/main. The plan was read at `7b7757b3`;
  origin/main moved to `ee584dcc` (#1086: PL-1392, FD-1393, `docs/roadmap.md`) during
  drafting, and that change touches no spec, contract or code file this record cites. Every
  locator below was re-read at `ee584dcc`.
- **Effort:** medium, inherited from the lead (the charter's "Model / effort" line; no
  maintainer raise to high was given).
- **Scope.** DP-S1-1 to DP-S1-6 are ruled, as the GO asks. DP-S1-7 and DP-S1-8 are confirmed
  in one line each, because the plan's activation need 1 lets this record do so. T1 to T9
  are adopted, five with amendments (and T2 in one clause), and the full adopted texts are under "The exact texts".
  Nothing here is later-phase capability: every text is spec for WK-673, a Phase 2 Work.

## Verified first, at `ee584dcc`

| Fact the ruling rests on | Read at `ee584dcc` |
|---|---|
| `score_batch` forwards every non-reserved column | `packages/pricing-core/src/pricing_core/rating/score.py:262` `_BATCH_RESERVED_COLUMNS = frozenset({"quote_id", "purpose", "effective_date", "rating_version_ref"})`; `:1033` `inputs = {k: v for k, v in row.items() if k not in _BATCH_RESERVED_COLUMNS}`; `:1066-1068` builds the engine context as `{"effective_date": …, "purpose": ctx.purpose, **ctx.inputs}` |
| A billing-named column refuses the row | `score.py:250-252` `_BILLING_SURFACE_KEYS` = `payment_schedule`, `apr`, `credit_agreement_term`, `instalment_schedule`, `instalment_count`; `_check_billing_surface` (`:425-433`) intersects them with `ctx.inputs.keys()` and raises `INPUT_CONTRACT_VIOLATION`, whatever the algorithm declares |
| MTA and cancellation are refused | `score.py:395` `_check_purpose_mount` raises `INPUT_CONTRACT_VIOLATION` for `mid_term_adjustment` and `cancellation`; `03` FR-218's dated amendment of 2026-09-29 (`RL-1242`) requires it until FR-217's inlining is built |
| A declared input missing from the row is refused | `score.py:334` `_validate_inputs`, *"every declared input is present (unless nullable)"*, raising *"input … is required (FR-213)"* |
| An undeclared engine read is unrefused today | `docs/findings/register.md:287`, FD-1374, MEDIUM, owner WK-1178 |
| `compile_bundle` is async and takes a resolver | `packages/pricing-core/src/pricing_core/rating/compile.py:573` `async def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle`; the protocol is `:443` (`async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact`) |
| The structural diff, and its unit | `packages/model-schema/src/model_schema/rating.py:570` `diff_algorithms`. It emits one `AlgorithmStepChange` **per changed field** (`:602-609`), and a step whose table or lookup reference changed appears **both** in `repointed_tables` (`:597-600`) **and** in `changed_steps` (its `rate_table_ref` or `reference_table_ref` field). A step's table reference is a versioned `ArtifactRef` (`:286`), and `Pins` (`:64-77`) pins the same artifact again |
| No dislocation type exists yet | `grep -rn 'class Dislocation\|class BundleDelta\|class Attribution' packages/` prints nothing |
| The contract is hand-authored and one-sided | `backend/tests/test_contracts.py:87` `"dislocation-run": "later-phase — 03 rating"`; the same line was at `:81` at `ed123cb0`, `RL-1264`'s tree |
| `_round_minor` is gone | `grep -rn 'def _round_minor' packages/` prints only `packages/pricing-core/tests/baseline_ladder.py:55`, a test helper. `git log -S'def _round_minor' origin/main -- …/score.py` names `1dd5e264` (SL-1345, #1045, 2026-10-01T09:58:44+01:00) as the commit that removed it. `score.py:955-959` still names it in `_coerce_output_value`'s docstring |
| The exposure convention | `01-data-management.md:235`, the `data_dictionary` example, `"exposure_years": {"description": "Time on risk", …}` |
| `QuotePurpose` | `packages/model-schema/src/model_schema/scoring.py:44`, five members, `what_if` among them |
| Codes | `03` §5.1's catalogue (`03:810-822`) owns `INPUT_CONTRACT_VIOLATION`, `BUNDLE_COMPILE_FAILED` and `LADDER_RECONCILIATION_FAILED`, the last a ladder fault (`RL-1346`). `VALIDATION_FAILED` is the run-level frame code `RL-1361` gives the rate-table diff's portfolio faults (absent column, null or negative exposure) |

## DP-S1-1 — the §4.8 undeclared column (the maintainer's acceptance condition 2)

### The clause ruled on, quoted from `03` §4.8 itself

`01-data-management.md` §4.8 was read too: it is `ReferenceTable` / `ReferenceTableVersion`
(`01:746`) and says nothing about a portfolio frame, so the clause is `03`'s. At
`ee584dcc`, `docs/specs/03-rating-engine.md` §4.8, the first paragraph after the heading's
note, ends:

> This subsection is written so it can hold the portfolio frame's schema when WK-673 designs it; it does not design that schema now.

and its **Input row** paragraph reads, whole:

> **Input row.** One column per reserved name below, plus one column per name in `bundle.algorithm.input_contract` (`model_schema.rating.InputContractField.name`) — forwarded into `QuoteContext.inputs` verbatim, tolerating extra columns the algorithm does not declare, exactly as `_validate_inputs` already tolerates extra `ctx.inputs` keys.

The ruling is on the last clause, *"tolerating extra columns the algorithm does not
declare"*, as it would apply to a frame built from a portfolio. It does not change that
clause for `score_batch` itself.

### The question

The reader keeps every column (`RL-1361` §E: *"That schema must let columns outside its
declared set pass through"*). What does a scoring pass of a dislocation run — the baseline
pass, the candidate pass and each attribution subset pass — do with a portfolio column that
**the bundle being rated** does not declare and that is not reserved?

### Options

- **(a) Forward it**, as the clause above does for `score_batch`: every non-reserved column
  enters the engine context on every pass.
- **(b) Project per pass:** each pass rates a frame of the stamped columns, `quote_id`, and
  exactly the names in **that pass's own bundle's** `input_contract`. Every other column stays
  beside the scored rows, joined back by `quote_id`.
- **(c) Refuse it:** a column neither reserved nor declared by either bundle is refused by name.
- **(d) Project to the union** of both bundles' contracts for every pass.

### Ruled: (b)

- **(c) is out.** It contradicts `RL-1361` §E, which rules pass-through at the reader, and it
  would make every Factor source column (FR-264's slicing, Slice 7's weighting) a refusal.
- **(a) makes the result depend on columns no contract names.** The engine context is
  `**ctx.inputs` (`score.py:1066-1068`), so an undeclared read resolves from whatever the book
  holds (FD-1374), and a book column named `instalment_count` refuses every row
  (`score.py:250-252`, `:425-433`), whatever the algorithm declares. Neither is visible in the
  approval's evidence.
- **(d) gives the baseline pass the candidate's new inputs**, which the baseline does not
  declare: (a)'s hazard on the baseline side, and an asymmetry between passes that attribution
  would then attribute to a change.
- **(b) makes each pass see exactly what its own contract declares.** A dislocation run
  becomes a function of the two versions, the declared columns and the stamped values, which
  is what the approval cites. It needs no change to `score_batch`, whose own tolerance stays
  for FR-253's direct batch. **Its cost, stated and accepted:** where a bundle compiled before
  FR-246's enforcement reads a name it does not declare, the dislocation rates that read with
  the name absent from context, while a live quote that happened to carry the key would
  resolve it. That read already breaks FR-246 (FD-1374). This record does **not** claim what
  the ZEN engine then returns for the absent name — that was not verified here — only that it
  is the same on every row and every pass, and independent of the book's incidental columns.

**Which side was wrong (`CLAUDE.md` §0): neither.** `score_batch`'s spec clause and its code
agree, and stay. No dislocation code exists. The §4.8 sentence *"it does not design that
schema now"* was true when written (2026-08-30) and is qualified by a dated note, not deleted
(T5).

## DP-S1-2 — the reserved columns, and MTA or cancellation rows

### Options

- **(a)** `purpose` and `effective_date` are required per-row portfolio columns; a run holding
  any `mid_term_adjustment` or `cancellation` row is refused before rating.
- **(b)** Per row; such rows are excluded and counted on the artifact.
- **(c)** **Per run, from the spec:** `DislocationSpec.purpose` (`new_business` or `renewal`)
  and `DislocationSpec.as_at` (an ISO date) are stamped into every row of every pass; a
  portfolio column with a reserved name other than `quote_id` is refused by name.

In every option `quote_id` is required, non-null and unique.

### Ruled: (c), with the refusal code set by DP-S1-6 and the subset passes' `rating_version_ref` stated

- **Why (c).** Attribution assumes every pass rates the same context except the bundle. One
  stamped purpose and date make that true by construction, and the run is reproducible from
  its spec alone. FR-218's interim refusal (`score.py:395`) then cannot fire inside a run. (a)
  makes every book carry two operational columns and mixes purposes inside one comparison. (b)
  silently changes the portfolio the approval cites. The cost — a mixed book needs two runs —
  is accepted. `what_if` is not admitted: it is not a premium the book pays.
- **A portfolio column named `purpose` is refused, not silently overridden.** A book can hold a
  per-row purpose, and quietly rating every row as `new_business` would discard it without
  notice. The remedy is a rename at data preparation.
- **Amendment: what a subset pass stamps as `rating_version_ref`.** T5 as drafted says the ref
  is stamped *"as §4.8 already requires"*, but a subset bundle has no Rating Version (RW2), and
  `score_batch` requires a parseable `ArtifactRef` per row (`score.py:1034`). The adopted T5
  states: a subset pass stamps the **baseline's** ref, its output rows are scratch inputs to
  attribution that are never persisted or returned as scoring results, and the subset is
  identified by the `bundle_hash` column, never by that ref.
- **When FR-217's inlining is built**, admitting MTA and cancellation is a change to this
  subsection (FR-218).

## DP-S1-3 — the exposure column's name

### Options

- **(a)** A fixed reserved name, `exposure_years`: decimal, non-null, never negative, zero
  allowed.
- **(b)** A name per run in `DislocationSpec` (`exposure_column`, default `exposure_years`).
- **(c)** Read from the portfolio Dataset's data dictionary.

### Ruled: (a)

It is `01`'s own convention (`01:235`) and the profiler's default, so freMTPL2-shaped data
needs no mapping. It reaches Slice 7's diff route, which has no `DislocationSpec` to name a
column in (`RL-1361` Ruled item 1 leaves the literal to this schema). One name cannot drift
between a run and a diff over the same portfolio. (b) does not reach Slice 7. (c) needs a
dictionary role `01` does not define. A null is refused, never read as 0 (`RL-1361` §E); the
code is DP-S1-6's.

## DP-S1-4 — the `analysis.py` signatures and the three types

### Options

- **(a)** As T7: `dislocate` unchanged; `async def derive_changes(baseline, candidate,
  resolver) -> list[BundleDelta]`; `async def attribute(baseline, candidate, portfolio, spec,
  resolver) -> Attribution`, `Attribution` being the whole attribution part of §4.6.
- **(b)** `attribute` takes two `CompiledBundle`s and a caller-supplied subset-builder callback.
- **(c)** As (a), but `attribute` returns `list[Attribution]`, one per group.

### Ruled: (a)

Every subset must pass the compile path (`RL-1264` DP-1), and `compile_bundle` takes a
`RatingVersion` and an `ArtifactResolver` and is async (`compile.py:573`). `derive_changes`
also needs the resolver: a `RatingVersion` carries `algorithm_ref`, not the algorithm, and
`diff_algorithms` takes two `RatingAlgorithm`s. (b) moves the compile-path guarantee into a
callback no signature can enforce. (c) leaves the residual, the method label and the subset
hashes, which `RL-1264` and FR-266's amendment put on the artifact, without a type.

**Which side was wrong (`CLAUDE.md` §0): the spec.** `03` §5.2's
`attribute(changes: Sequence[BundleDelta], portfolio: pl.LazyFrame) -> list[Attribution]`
cannot implement `RL-1264` DP-1: it has no baseline and no resolver. No code implements it.

## DP-S1-5 — S above K = 6

### Options

- **(a)** R exact; S as a labelled lower bound over a declared number of orders that always
  includes the declared order and its reverse, printed as a bound, never as S.
- **(b)** R only; S omitted above six, with the reason stated.
- **(c)** S exact regardless of cost.

### Ruled: (a)

`RS-1201`'s S is a maximum over all K! orders (*"Order-sensitivity S = maxᵢ, max over all K!
orders, of |cumulativeᵢ(order) − cumulativeᵢ(declared order)|, divided by D"*), and a
cumulative figure under an arbitrary order needs v on every prefix, so exact S needs the 2^K
ratings the fallback exists to avoid; (c) defeats the fallback. R = |total − Σ isolated| / D
needs only the isolated runs and the total, so it is exact. A maximum over a subset of orders
is a true lower bound on S, so a large bound still shows order-dependence, which is why the
F3 decision prints S at all; (b) loses that. The deputy's rule that a sample is never presented
as exact (`RL-1264`, feasibility item 3) is kept by the label. **The number of orders is not
fixed here:** Slice 3 fixes it from its cost measurement (`RL-1264` item 1), with a floor of
2, and the artifact records it per run (`orders_sampled`).

### Mint-pass note, 2026-10-03 (the maintainer's four conditions)

*Dated 2026-10-03, at the mint of `RL-1394`.*
The maintainer accepted the decision above as **an interpretation of `RL-1184`, not a change to
it**, in the entry headed "2026-10-03 20:07:45 BST — RL 9740 F3 note ACCEPTED as an
interpretation of RL-1184, not a change to it; GO: SL-1377 slice audit → GO-mint LG-1394 → ONE
two-half gate on the minted head" (`~/gi-pricing-plan.local/channel/to-lead.md`), on four
conditions that bind this ruling's reading and the executor of `SL-1385`:

- **(i)** R stays exact: the residual is computed, not bounded.
- **(ii)** The label names N, the orders evaluated, and keeps "order-dependent" (T1's
  "S ≥ x over n orders", labelled order-dependent, is that label).
- **(iii)** The grouping path (at most 6 groups, Shapley over the groups) stays the first offer
  (T1 states it before the fallback).
- **(iv)** This reading rests on `RL-1184` at lines 199-202, which quote: "Above K = 6, the
  analyst groups the changes into ≤ 6 declared groups, and Shapley runs over the groups. Where
  that is refused, (a) with its residual line is shown with the measured S and R printed
  beside it, labelled order-dependent. It is never presented as a decomposition." Above six, S
  can only be measured over the orders actually evaluated, so a value labelled as a lower bound
  over N orders is the measured S stated honestly. **`RL-1184` is not amended.**

The same entry fixed two items at the mint, as the audit of this record proposed: the
amendment count (title and Scope now say five, matching "Status per text"), and the local row
labels `R1`, `R2`, `R3` of the three new `03` §3.9 rows, renamed `RW1`, `RW2`, `RW3` because
`R1` is already `03`'s invariant at `03-rating-engine.md:41`. The texts T1 to T9 are otherwise
as audited.

## DP-S1-6 — the error codes the new text names

### Options

- **(a)** Existing codes where one already means it — `BUNDLE_COMPILE_FAILED` (subset),
  `VALIDATION_FAILED` (partition; null exposure), `INPUT_CONTRACT_VIOLATION` (frame) — and the
  reconciliation failure gets a new code, registered by Slice 3, the slice that first raises it.
- **(b)** New dislocation codes for every case, catalogued in Slice 1.
- **(c)** All on existing codes, reconciliation included (`LADDER_RECONCILIATION_FAILED`).

### Ruled: (a), amended — every run-level frame refusal is `VALIDATION_FAILED`

- **The principle adopted with (a):** no new code without a raiser, so Slice 1 does not touch
  `03` §5.1's catalogue. (c) would give `LADDER_RECONCILIATION_FAILED` a second meaning; it is
  a ladder fault (`03:818`, `RL-1346`), and a code's meaning is the spec's. (b) catalogues
  codes nothing raises yet.
- **The amendment.** T5 as drafted refuses a null or duplicated `quote_id` and a reserved-name
  column with `INPUT_CONTRACT_VIOLATION`, but a null exposure with `VALIDATION_FAILED`. That
  splits one kind of fault — a portfolio that does not meet the frame's schema, found before
  any rating — across two codes. `INPUT_CONTRACT_VIOLATION` is a **per-quote** code in this
  module (FR-213, FR-218, FR-252; it is what `score_batch` writes on an `"error"` row).
  `VALIDATION_FAILED` is what `RL-1361` already gives the same portfolio's frame faults on the
  rate-table diff route. So: **every run-level frame refusal is `VALIDATION_FAILED`**, naming
  the column and the count — a missing, null or duplicated `quote_id`, a missing, null or
  negative `exposure_years`, and a portfolio column with a reserved name. **A per-row fault
  stays the row's own code**: a declared input the portfolio lacks is FR-213's missing input,
  an `"error"` row with `INPUT_CONTRACT_VIOLATION`, exactly as `score_batch` writes it.
- **Reconciliation failure:** T1 and RW1 name the failure and no code; Slice 3 registers one in
  `03` §5.1 when it builds the raiser.

## DP-S1-7 and DP-S1-8 — confirmed

- **DP-S1-7: (a), confirmed.** Slice 1 writes every §4.6 field and the hand-authored contract
  in one commit. `RL-1264`'s conclusion stands, but **its stated reason was wrong at its own
  tree**: it says *"The artifact's shape is generated from `model-schema` into
  `docs/contracts/`"*, and at `ed123cb0` the contract was hand-authored and one-sided
  (`test_contracts.py:81`). The right reason is the plan's: the contract is still
  hand-authored, so Slice 1 edits both and they cannot disagree.
- **DP-S1-8: (a), confirmed.** `RL-1264`'s obligation to correct `_round_minor`'s docstring
  sentence is **discharged by events**: SL-1345 (`1dd5e264`) removed the function. Slice 1
  edits nothing in `score.py`. The two dangling references in `_coerce_output_value`'s
  docstring (`score.py:955-959`) are an auditor's finding to file, not this slice's edit.

## A defect in T4 found at ruling, and its fix (amended in the adopted text)

T4 as drafted derives *"each differing pin … and each step added, removed or changed and each
table re-pointed"* as one change each. Against `diff_algorithms` at `ee584dcc` that
**double-counts**: a step whose table reference moves from `@5` to `@6` is one entry in
`repointed_tables`, one `AlgorithmStepChange` in `changed_steps`, and one differing pin in
`Pins.rate_tables` — three derived changes for one edit. `changed_steps` is also per field, so
a step with two changed fields would be two changes. At step granularity (`RL-1264` DP-1)
applying any one of the three substitutes the same step, so Shapley would split one edit's
credit across duplicates while the partition check still passed. **The plan's text was wrong
against the code; the code is right** (it describes the diff truthfully at field level). The
adopted RW3 fixes the unit: one change per `step_id` added, removed or changed; a pin
difference a derived step change accounts for travels with it; a pin difference no step change
accounts for is its own change. It also fixes the **declared change order**, which T1's
tie-break and the cumulative view both need and the draft left undefined. §4.6's example `c1`
becomes `step_changed` accordingly.

**Not ruled here, raised for the lead:** where `input_contract_changed` or `outputs_changed`
is true, which input contract and outputs a **proper** subset bundle declares (a subset
holding a candidate step that consumes a new input may otherwise fail FR-212 at compile, and RW2
fails the run). It is not one of DP-S1-1 to DP-S1-6, it blocks Slice 3 (which builds subset
construction), not Slice 1, and an `OQ-` needs an id this role may not allocate. **Proposed:**
the lead allocates an OQ for it, on Slice 3's leaf plan as a blocking decision point.

## Ruled

| DP | Ruling |
|---|---|
| DP-S1-1 | **(b)** each pass sees only its own bundle's declared names plus the stamped columns and `quote_id`; every other column passes through beside the rows and never reaches the engine; `score_batch` unchanged |
| DP-S1-2 | **(c)** `purpose` and `as_at` stamped per run from `DislocationSpec`; `new_business` or `renewal` only; reserved-name portfolio columns refused; subset passes stamp the baseline's ref, rows scratch |
| DP-S1-3 | **(a)** `exposure_years`, decimal, non-null, non-negative |
| DP-S1-4 | **(a)** `dislocate` unchanged; `async derive_changes`; `async attribute(baseline, candidate, portfolio, spec, resolver) -> Attribution` |
| DP-S1-5 | **(a)** R exact; S as a labelled lower bound over ≥ 2 orders including declared and reverse; Slice 3 fixes the count |
| DP-S1-6 | **(a), amended** existing codes; every run-level frame refusal `VALIDATION_FAILED`; per-row faults keep their own code; reconciliation code registered by Slice 3 |
| DP-S1-7 | **(a)** confirmed; `RL-1264`'s stated reason corrected |
| DP-S1-8 | **(a)** confirmed; discharged by SL-1345 |

## The exact texts

The executor applies these, never the plan's Appendix (PL-1395 Task 0 Step 4). `<date>` is
the merge date the executor writes; `RW1`, `RW2`, `RW3` are the working ids, replaced by the ids
the lead issues; `PL-<n>` and `RL-<n>` are this plan's and this record's minted ids. Each
block's fence is not part of the text. **Status per text:** T2, T7, T8 and T9 adopted as filed
(T2 with one clause amended); T1, T3, T4, T5 and T6 amended.

### T1 — appended to FR-266's row (`03` §3.9), inside the same cell, after its last sentence

Amended from the draft: v(S) may come from a proven ladder replay (`RL-1264` feasibility item
2); the declared change order points at RW3; the bound's order count is Slice 3's.

```markdown
*(Amended <date>, WK-673 Slice 1, on OQ-1187's decision (`RL-1184` F3), the deputy's F3 decision of 2026-09-28 12:10:21 BST as corrected at 13:57:02 BST (`RS-1201`), `RL-1264` and `RL-<n>`.)* **The attribution of record is exact Shapley over the declared changes, for K ≤ 6.** For each policy, each change's Shapley value is computed exactly, as a rational with denominator K!, from v(S) for each of the 2^K subsets S of the declared changes, where v(S) is the policy's payable premium in integer minor units under the subset bundle for S (RW2), or a ladder replay proven equal to it under `RL-1264`'s feasibility rule. The K values are allocated to integer minor units by **largest remainder**, ties broken in the declared change order (RW3), so that the policy's parts sum exactly to its candidate minus baseline payable premium; plain rounding is forbidden. Portfolio figures are sums of the per-policy integer parts. The **isolated** figure (the change applied alone) and the declared-order **cumulative** figure are views beside the Shapley figure, never the attribution, and the **interaction residual**, total − Σ isolated, is its own line. **Above K = 6** the analyst groups the changes into at most 6 change groups (RW3) and Shapley runs over the groups; where the analyst does not group them, the isolated-plus-cumulative method with its residual line is shown with R and a lower bound on S (`RS-1201` defines both), labelled order-dependent and never presented as a decomposition. R is exact. The bound is the maximum over a declared number of orders, at least 2 and always including the declared order and its reverse; it is printed as "S ≥ x over n orders", never as S, and the run records n. Exactness holds on the integer minor units each rating returns through FR-273's boundary, not on a decimal carried through the engine (§3.11).
```

### T2 — new row RW1, the first of three rows appended after FR-266's row

Adopted as filed, with one clause amended (the plain-rounding fixture must be a case where
plain rounding does not sum; otherwise the test cannot fail).

```markdown
| **RW1** | **Attribution reconciles exactly on the rating path's own integers, on every run.** Every attribution part, the interaction-residual line and the total are integer minor units taken from the payable premium's `value_minor` as the rating path produces it (FR-273). Per policy and at portfolio level, the Shapley parts sum exactly to the total, and the isolated figures plus the residual line sum exactly to the total, as integers, with no float summed after rounding. The run checks both on every run and fails, naming the first policy that does not reconcile, rather than persist a result that does not. The check is proven on deliberately broken input: a plain-rounding allocation, on a policy where plain rounding does not sum to the total, and a Shapley value perturbed by one minor unit are each refused. *(Added <date>, WK-673 Slice 1: the deputy's F3 item 4, corrected 2026-09-28 13:57:02 BST; `RL-<n>`.)* |
```

### T3 — new row RW2, after RW1

Amended from the draft: a subset bundle compiled to verify ladder replay is bound the same way.

```markdown
| **RW2** | **Attribution runs on the ZEN engine through the ordinary compile path, and its subset bundles are ephemeral.** Each subset of the declared changes is a bundle built at step granularity from the baseline's pins and algorithm with that subset's changes substituted, compiled by `compile_bundle` and hydrated by `load_bundle`, so it passes the same validation as a real version (FR-240, FR-274, FR-275, FR-276) and is rated by the engine, never by a mirror of it. This holds for every subset bundle a run compiles, whether v(S) is read from it or it verifies a ladder replay (FR-266's amendment). A subset bundle is content-addressed and has **no Rating Version identity**: it is never a `rating_version` row, and it is never approvable, deployable or listed in any version list. It is cached per run by its content hash and discarded with the run's scratch. A subset that fails to compile fails the run with `BUNDLE_COMPILE_FAILED`, naming the subset; it is never skipped. The run artifact records how many subset bundles were compiled and their content hashes, and whether v(S) came from re-rating or from ladder replay (§4.6). *(Added <date>, WK-673 Slice 1: `RL-1264` DP-1 (a), with its conditions; `RL-<n>`.)* |
```

### T4 — new row RW3, after RW2

Amended from the draft: the unit is the step; pins travel with the step that accounts for
them; the declared change order is defined; an ungrouped change is named by its id.

```markdown
| **RW3** | **The declared changes are derived, and the analyst may group them.** The server derives the change list from the difference between baseline and candidate, at step granularity: each `step_id` the structural diff (FR-219) reports as added, removed, or present in both with any field changed is exactly one derived change, however many of its fields changed. Its kind is `step_added`, `step_removed`, `table_repointed` where the only changed field is the step's table or lookup reference, or `step_changed`. A pin difference (FR-237) that a derived step change accounts for, through that step's table, lookup or model reference, is part of that change, never a second one; a pin difference no step change accounts for is its own derived change, of kind `pin`. Derived changes are numbered `c1`, `c2`, … in the derived order: step changes sorted by `step_id`, then unaccounted pin differences sorted by their reference string. The analyst may merge derived changes into at most 6 named **change groups** in the `DislocationSpec`. The server checks that the groups partition the derived list exactly, every derived change in exactly one group, and refuses otherwise with `VALIDATION_FAILED`, naming each change left out or placed twice. With no groups given, each derived change is its own group, named by its id, and above 6 FR-266's above-six rule applies. The **declared change order** is the order of the groups as the analyst gives them, or with no groups the derived order. The derived list and the groups are both on the artifact (§4.6). *(Added <date>, WK-673 Slice 1: `RL-1264` DP-2 (c); `RL-<n>`.)* |
```

### T5 — appended to `03` §4.8 as its last part, after the paragraph ending "reading `error_code` off this column."

Amended from the draft: DP-S1-6's codes; the subset passes' `rating_version_ref`; `what_if`
excluded; no claim about what the engine does with an absent name.

```markdown
#### The portfolio frame (WK-673, added <date>)

*(Added <date>, WK-673 Slice 1, PL-<n>; the ruling `RL-<n>`; `RL-1361` §E for pass-through.)* `dislocate`'s and `attribute`'s `portfolio` is one row per policy of a portfolio Dataset Version.

| Column | Type | Rule |
|---|---|---|
| `quote_id` | string | required, non-null and unique: the policy's identity, the key on which the baseline and candidate passes are joined, and the drill-down key for movers |
| `exposure_years` | decimal | required, non-null and never negative; zero allowed; never read as 0 when null (`RL-1361` §E). The weight for exposure shares (FR-263) and for FR-231's per-cell weights |
| each name in either bundle's `input_contract` | as declared | the algorithm inputs |

**A portfolio that breaks this schema is refused before any rating, with `VALIDATION_FAILED`,** naming the column and the count of offending rows: a missing, null or duplicated `quote_id`; a missing, null or negative `exposure_years`; a column named `purpose`, `effective_date` or `rating_version_ref`. A fault in one row's algorithm inputs is not a frame refusal: it is that row's own error, as below.

**`purpose`, `effective_date` and `rating_version_ref` are stamped, never read from the portfolio.** `DislocationSpec.purpose` (`new_business` or `renewal`) and `DislocationSpec.as_at` (an ISO date) are written into every row of every pass as `purpose` and `effective_date`. The baseline pass and the candidate pass stamp their own Rating Version's `rating_version_ref`, as this subsection requires of every `score_batch` frame. An attribution subset pass stamps the **baseline's** `rating_version_ref`, because a subset bundle has no Rating Version (`03` §3.9) and `score_batch` requires a reference on every row; its output rows are scratch inputs to attribution, never persisted or returned as scoring results, and the subset is identified by their `bundle_hash`, never by that reference. A `mid_term_adjustment`, `cancellation` or `what_if` row therefore cannot occur in a run; when FR-217's inlining is built, admitting the first two is a change to this subsection (FR-218).

**Every other column passes through the reader** and stays available for slicing by any Factor (FR-264), for exposure weighting, for drill-down, and for resolving a Factor's source columns (FR-231, `RL-1361`). **It never reaches the engine.** Each scoring pass — the baseline, the candidate and every attribution subset — rates a frame of the stamped columns, `quote_id`, and exactly the names in **that pass's own bundle's** `input_contract`; the other columns are joined back to the scored rows by `quote_id`. A name a bundle declares but the portfolio lacks is FR-213's missing input, written as an `"error"` row with `INPUT_CONTRACT_VIOLATION`, as `score_batch` already does. `score_batch`'s own tolerance of extra columns (above) is unchanged: this projection is `dislocate`'s and `attribute`'s, because forwarding an undeclared column lets an undeclared read resolve from the book (`FD-1374`) and lets a column with a billing name refuse every row (FR-252), so a run's result would depend on columns no contract names.
```

And, appended to the sentence ending *"it does not design that schema now."* in §4.8's first
paragraph after the heading note (the sentence is kept):

```markdown
*(Superseded in part <date>: the portfolio frame's schema is designed in "The portfolio frame (WK-673)" below, `RL-<n>`.)*
```

### T6 — `03` §4.6 and `docs/contracts/schemas/dislocation-run.schema.json`, in one commit

**Dated note**, a new paragraph directly under the `### 4.6 \`DislocationRun\`` heading,
before the code fence:

```markdown
*(Amended <date>, WK-673 Slice 1, `RL-<n>`: reconciled with `dislocation-run.schema.json` (`job_id`, `by_ladder_rung` and `errors` added to the example) and extended with FR-266's attribution as amended, RW1, RW2 and RW3. Money is integer minor units. `mean_change_pct` and `cumulative_change_pct` on an `attribution` item are derived views: `shapley_minor` (or, under `order_dependent`, `isolated_minor`) and `cumulative_minor` as a percentage of `totals.baseline_premium_minor`. `method` is `shapley` or `order_dependent`; `shapley_minor` is null only under `order_dependent`, and `order_sensitivity_lower_bound`, `residual_share` and `orders_sampled` are non-null only under it. S and R are decimal strings. `subset_valuation` is `rerate` or `ladder_replay`, and `replay_fell_back` is true where a replay mismatch fell the run back to re-rates (`RL-1264`); Slice 3 may amend these two with a dated note if it does not adopt replay.)*
```

**The example.** Replace the whole JSON object in §4.6's code fence with:

```json
{
  "baseline_ref": "rating_version:motor-gb@26",
  "candidate_ref": "rating_version:motor-gb@27",
  "portfolio_dataset_version_id": "uuid",
  "job_id": "uuid",
  "policy_count": 1_284_902, "exposure_years": "1240118.4",
  "totals": {"baseline_premium_minor": 41_882_100_00, "candidate_premium_minor": 42_698_300_00,
             "change_pct": 1.95},
  "distribution": [
    {"band": "< -10%", "policies": 41_204, "exposure_share": 0.031, "mean_change_pct": -14.2},
    {"band": "-10% to -5%", "policies": 118_402, "exposure_share": 0.092, "mean_change_pct": -7.1},
    {"band": "-5% to 0%", "policies": 402_118, "exposure_share": 0.314, "mean_change_pct": -2.2},
    {"band": "0% to +5%", "policies": 511_402, "exposure_share": 0.398, "mean_change_pct": 2.6},
    {"band": "+5% to +10%", "policies": 174_882, "exposure_share": 0.136, "mean_change_pct": 7.0},
    {"band": "> +10%", "policies": 36_894, "exposure_share": 0.029, "mean_change_pct": 14.8}
  ],
  "by_segment": [{"factor": "driver_age_band", "level": "17-20",
                  "policies": 22_104, "mean_change_pct": -6.4, "exposure_share": 0.017}],
  "by_ladder_rung": [{"rung": "base_premium", "contribution_pct": 1.10}],
  "derived_changes": [
    {"id": "c1", "kind": "step_changed", "description": "s_model: peril_structure:motor-gb-2026h2@1 → @2"},
    {"id": "c2", "kind": "table_repointed", "description": "s_age: rate_table:motor-driver-age-relativity@5 → @6"},
    {"id": "c3", "kind": "step_changed", "description": "s_minprem: min_premium 26000 → 28000"}
  ],
  "change_groups": [{"name": "models", "changes": ["c1"]}, {"name": "age curve", "changes": ["c2"]},
                    {"name": "minimum premium", "changes": ["c3"]}],
  "attribution": [
    {"group": "models", "shapley_minor": 594_700_00, "isolated_minor": 571_000_00,
     "cumulative_minor": 571_000_00, "mean_change_pct": 1.42, "cumulative_change_pct": 1.36},
    {"group": "age curve", "shapley_minor": -129_800_00, "isolated_minor": -131_200_00,
     "cumulative_minor": -128_100_00, "mean_change_pct": -0.31, "cumulative_change_pct": -0.31},
    {"group": "minimum premium", "shapley_minor": 351_300_00, "isolated_minor": 322_400_00,
     "cumulative_minor": 373_300_00, "mean_change_pct": 0.84, "cumulative_change_pct": 0.89}
  ],
  "attribution_summary": {"method": "shapley", "total_change_minor": 816_200_00,
                          "residual_minor": 54_000_00, "order_sensitivity_lower_bound": null,
                          "residual_share": null, "orders_sampled": null,
                          "subset_bundle_count": 8, "subset_bundle_hashes": ["sha256:…"],
                          "subset_valuation": "rerate", "replay_fell_back": false},
  "largest_movers_blob": "blob:sha256:…",
  "errors": [{"code": "INPUT_CONTRACT_VIOLATION", "count": 0}]
}
```

The figures reconcile as RW1 requires (checked at ruling): Shapley 594 700 00 − 129 800 00 +
351 300 00 = 816 200 00 = 42 698 300 00 − 41 882 100 00; isolated 571 000 00 − 131 200 00 +
322 400 00 = 762 200 00, and 816 200 00 − 762 200 00 = 54 000 00, the residual; cumulative
571 000 00 − 128 100 00 + 373 300 00 = 816 200 00. Each `mean_change_pct` and
`cumulative_change_pct` is its figure over 41 882 100 00, to two places (594 700 00 → 1.42,
571 000 00 → 1.36, −129 800 00 → −0.31, −128 100 00 → −0.31, 351 300 00 → 0.84,
373 300 00 → 0.89). `subset_bundle_count` 8 = 2³.

**The contract.** In `docs/contracts/schemas/dislocation-run.schema.json`: (1) replace the
whole `"attribution"` property with the `"attribution"` member below; (2) insert the
`"derived_changes"`, `"change_groups"` and `"attribution_summary"` members directly after it;
(3) add the `"dependentRequired"` member at the top level, after `"required"`. Change nothing
else; `by_ladder_rung`, `job_id` and `errors` already exist and stay as they are.

```json
    "attribution": {
      "type": "array",
      "description": "Per change group: the Shapley part of record and the isolated and cumulative views, in integer minor units (FR-266 as amended, RW1).",
      "items": {
        "type": "object",
        "required": ["group", "shapley_minor", "isolated_minor", "cumulative_minor", "mean_change_pct"],
        "properties": {
          "group": {"type": "string"},
          "shapley_minor": {"anyOf": [{"$ref": "common/money.schema.json#/$defs/MoneyMinor"}, {"type": "null"}]},
          "isolated_minor": {"$ref": "common/money.schema.json#/$defs/MoneyMinor"},
          "cumulative_minor": {"$ref": "common/money.schema.json#/$defs/MoneyMinor"},
          "mean_change_pct": {"type": "number"},
          "cumulative_change_pct": {"type": "number"}
        }
      }
    },
    "derived_changes": {
      "type": "array",
      "description": "The changes derived from baseline and candidate at step granularity (RW3).",
      "items": {
        "type": "object",
        "required": ["id", "kind", "description"],
        "properties": {
          "id": {"type": "string"},
          "kind": {"enum": ["pin", "step_added", "step_removed", "step_changed", "table_repointed"]},
          "description": {"type": "string"}
        }
      }
    },
    "change_groups": {
      "type": "array", "maxItems": 6,
      "description": "The analyst's groups, partitioning derived_changes exactly (RW3). Their order is the declared change order.",
      "items": {
        "type": "object",
        "required": ["name", "changes"],
        "properties": {
          "name": {"type": "string"},
          "changes": {"type": "array", "minItems": 1, "items": {"type": "string"}}
        }
      }
    },
    "attribution_summary": {
      "type": "object",
      "description": "Method, totals, S and R, and the subset bundles compiled (FR-266 as amended, RW1, RW2).",
      "required": ["method", "total_change_minor", "residual_minor", "order_sensitivity_lower_bound",
                   "residual_share", "orders_sampled", "subset_bundle_count", "subset_bundle_hashes",
                   "subset_valuation", "replay_fell_back"],
      "properties": {
        "method": {"enum": ["shapley", "order_dependent"]},
        "total_change_minor": {"$ref": "common/money.schema.json#/$defs/MoneyMinor"},
        "residual_minor": {"$ref": "common/money.schema.json#/$defs/MoneyMinor"},
        "order_sensitivity_lower_bound": {"anyOf": [{"$ref": "common/money.schema.json#/$defs/Decimal"}, {"type": "null"}]},
        "residual_share": {"anyOf": [{"$ref": "common/money.schema.json#/$defs/Decimal"}, {"type": "null"}]},
        "orders_sampled": {"type": ["integer", "null"], "minimum": 2},
        "subset_bundle_count": {"type": "integer", "minimum": 0},
        "subset_bundle_hashes": {"type": "array", "items": {"type": "string"}},
        "subset_valuation": {"enum": ["rerate", "ladder_replay"]},
        "replay_fell_back": {"type": "boolean"}
      }
    },
```

```json
  "dependentRequired": {"attribution": ["derived_changes", "change_groups", "attribution_summary"]},
```

The executor confirms at Task 4 that `common/money.schema.json` defines `$defs/MoneyMinor` and
`$defs/Decimal` (both are already referenced by this file at `ee584dcc`) and that the edited
file parses with no duplicate key (`contract-schema`). PL-1395's Task 4 Step 3 agreement check
then applies unchanged.

### T7 — `03` §5.2: replace the two `# pricing_core/rating/analysis.py` signature lines

Adopted as filed. The code block lines, replacing `def dislocate(…)` and `def attribute(…)`
under `# pricing_core/rating/analysis.py`:

```python
# pricing_core/rating/analysis.py
def dislocate(baseline: CompiledBundle, candidate: CompiledBundle,
              portfolio: pl.LazyFrame, spec: DislocationSpec) -> DislocationRun
async def derive_changes(baseline: RatingVersion, candidate: RatingVersion,    # added <date> (WK-673 S1, RW3)
                         resolver: ArtifactResolver) -> list[BundleDelta]
async def attribute(baseline: RatingVersion, candidate: RatingVersion,         # amended <date> (WK-673 S1,
                    portfolio: pl.LazyFrame, spec: DislocationSpec,            # RL-1264 premise: the old form took
                    resolver: ArtifactResolver) -> Attribution                 # no baseline and could not compile subsets)
```

The types paragraph, directly after the §5.2 code block that holds these lines:

```markdown
*`DislocationSpec` (added <date>, `RL-<n>`): `baseline_ref`, `candidate_ref`, `portfolio_dataset_version_id`, `purpose`, `as_at` (§4.8's portfolio frame), `segments` (the Factors FR-263 averages by), `band_edges_pct`, `mover_threshold_pct` (FR-263), and optional `change_groups` (RW3). `BundleDelta`: one derived change, `id`, `kind`, `description`, as §4.6's `derived_changes` item. `Attribution`: §4.6's `derived_changes`, `change_groups`, `attribution` and `attribution_summary` together. All three are defined in `model-schema` by the slice that first returns them (WK-673 Slices 2 and 3) and match §4.6 field for field.*
```

The band and mover field names are Slice 2's to confirm against FR-263, and may be amended
there with a dated note; the other `DislocationSpec` names are fixed by this record.

### T8 — `00` §2.3: five rows appended after the `**Dislocation**` row

Adopted as filed.

```markdown
| **Shapley attribution** | The decomposition of a Dislocation Run's premium change into its declared changes by exact Shapley values, allocated to integer minor units by largest remainder (`03` FR-266). |
| **Interaction residual** | Total change minus the sum of the isolated changes: the part no single change explains alone (`03` FR-266). |
| **Change group** | A named set of derived changes that attribution treats as one; the groups partition the derived changes exactly, at most 6 (`03` §3.9). |
| **Subset bundle** | An ephemeral, content-addressed bundle with a subset of the declared changes applied, compiled only to rate attribution; it has no Rating Version identity (`03` §3.9). |
| **Portfolio frame** | The one-row-per-policy input a Dislocation Run rates, with its columns and stamping rules (`03` §4.8). |
```

### T9 — `backend/tests/test_contracts.py`, the `"dislocation-run"` entry's value

Adopted as filed. The whole line, replacing `:87`:

```python
    "dislocation-run": "03 §4.6 — hand-authored until WK-673 Slice 4 generates and compares it (PL-1267)",
```

## Which side was wrong (`CLAUDE.md` §0), collected

| Where | Disagreement | Wrong side |
|---|---|---|
| `03` §5.2 `attribute` | the signature cannot compile a subset (`RL-1264` DP-1) | **the spec**; no code exists |
| `03` §4.6 example against the contract | the contract has `job_id`, `by_ladder_rung`, `errors`; the example does not | **the spec's example**; the contract was right |
| `test_contracts.py:87` label | says "later-phase"; WK-673 is Phase 2 | **the label** (T9) |
| `RL-1264`'s `_round_minor` obligation | its target was removed by SL-1345 | neither: overtaken by events (DP-S1-8) |
| `RL-1264`'s reason for DP-S1-7 | says the contract is generated; it was hand-authored at its tree | **the record's premise**; its conclusion stands |
| PL-1395's T4 against `diff_algorithms` | the draft triple-counts one table re-point | **the plan's text**; the code is right |
| `03` §4.8 `score_batch` input row | none: spec and code agree | neither |

## What it obliges

- **This commit:** this record only. No spec, contract or code file is edited here; the
  executor of SL-1385 applies "The exact texts" through `spec-change` (PL-1395 Tasks 1–6).
- **PL-1395 (the planner's; not edited here):** at its mint, DP-S1-1 to DP-S1-6 (and DP-S1-7,
  DP-S1-8) cite this record's minted id in "Resolved by". Its Acceptance 5 reads the amended
  T5; Acceptance 3's phrases are all present in the amended T1 (`exact Shapley`, `largest
  remainder`, `declared change order`, `plain rounding is forbidden`, `isolated`, `cumulative`,
  `total − Σ isolated`, `order-dependent`, `FR-273`). The plan's T5 text names
  `INPUT_CONTRACT_VIOLATION` for frame faults; the ruling's text, which Task 0 Step 4 copies,
  governs.
- **The lead:** allocate an OQ for the subset input-contract question above, as a blocking
  decision point on Slice 3's (SL-1387) leaf plan. The auditor may file the `score.py:955-959`
  dangling references as a finding (DP-S1-8).
- **Slice 3 (SL-1387):** fixes the S-bound order count (≥ 2) from its measurement; registers
  the reconciliation failure code in `03` §5.1; may amend `subset_valuation` and
  `replay_fell_back` with a dated note if it does not adopt replay.

## Acceptance — the violation that must become detectable

This record builds nothing, so no check is proven red here. The slices that build the code
carry these, each shown red on deliberately broken input:

- *Violation: a portfolio column that the pass's bundle does not declare reaches the engine
  context.* Slice 2 (`dislocate`) and Slice 3 (`attribute`): a fixture bundle whose expression
  reads an undeclared name, rated over a portfolio carrying that name with a value that would
  change the premium; the dislocation premium must equal the premium with the column absent.
  And a portfolio column named `instalment_count`, undeclared: no row is refused.
- *Violation: a portfolio column named `purpose` silently overridden.* Slice 2: the run is
  refused with `VALIDATION_FAILED` naming `purpose`.
- *Violation: a null `exposure_years` read as 0.* Slice 2: refused with `VALIDATION_FAILED`
  naming the column and the count.
- *Violation: a table re-point derived as more than one change.* Slice 3 (`derive_changes`): a
  candidate whose only difference is one step's table reference `@5 → @6` derives exactly one
  change, of kind `table_repointed`.
