---
id: PL-1395
family: plan
kind: leaf
title: WK-673 Slice 1 — spec: FR-266's Shapley amendment, the hard gate as requirements, the portfolio frame, the contract and the types: leaf plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-03
owner: planner
tree: 7b7757b3b868a08351130533454ff4afbade15af
phase: P2
work: WK-673
slice: SL-1385
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1267, RL-1264, RL-1361, RL-1184, RL-1263, RS-1201, FD-1374, PL-1376, PL-1382, PL-1371]
---

# PL-1395 — WK-673 Slice 1: spec — the Shapley amendment, the hard gate, the portfolio frame, the contract and the types: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor is spawned from `.claude/roles/executor.md` and also
> binds `spec-change` (Tasks 1–5), `contract-schema` (Task 4), `contract-guard` (Task 6, read
> only: the slug stays one-sided), `python-test` and `dev-commands` (the two-half gate and its
> traps) and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before
> the first step.

Filed 2026-10-03 under working id 9741, allocated by the lead; minted as `PL-1395` on
2026-10-03 (`python3 scripts/doc-id.py next`), in one PR with `RL-1394`. Drafted at 19:45:17 BST
(`TZ=Europe/London date`) against origin/main `7b7757b3`.

## Goal

Write the specification WK-673's build slices are written against, so that Slices 2, 3 and 4
build from spec text rather than inventing it:
- `03` FR-266 gains its dated amendment naming exact Shapley with largest-remainder allocation
  (OQ-1187 as decided by `RL-1184`; the deputy's F3 decision as corrected at 13:57:02);
- the hard gate and `RL-1264`'s DP-1 and DP-2 conditions become numbered requirements in
  `03` §3.9;
- `03` §4.8 gains the **portfolio frame's** schema, and states what the frame does with a
  column the contract does not declare (the maintainer's acceptance condition 2, quoted under
  Inputs);
- `03` §4.6 and the hand-authored `docs/contracts/schemas/dislocation-run.schema.json` are
  reconciled with each other and extended with the attribution fields, in one commit;
- `03` §5.2 defines `DislocationSpec`, `BundleDelta` and `Attribution`, and `attribute` gets a
  signature that can be implemented;
- `00` §2 defines the new terms first.

No application behaviour changes. The only non-docs edits are one label string in
`backend/tests/test_contracts.py` and the hand-authored contract JSON.

**Architecture.** A spec-only slice, cut by `PL-1267` (Slice 1, `:433-479`). Every open design
choice in it is a decision point below; the decision-maker resolves the blocking ones in one
sitting and, in the same record, adopts or amends the proposed texts T1–T9 (Appendix). The
executor then applies the adopted texts verbatim through `spec-change`. This split follows
`document-ids.md` §1.6 (the FR/NFR/DEP row: the decision-maker creates and amends requirement
text) and the precedent of `RL-1361`, whose "The exact texts" section `PL-1376` applies.

**Tech Stack.** Markdown specs, one JSON Schema (draft 2020-12, hand-authored), one Python test
module (a string literal only). No new dependency, so `docs/skills-map.md` does not change.

**Spec.** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.9, §3.11 (FR-273),
§4.6, §4.8, §5.2, §10 (OQ-1187); [`../specs/00-overview.md`](../specs/00-overview.md) §2.3; the
map plan [`PL-01267-wk-673-dislocation-with-attribution-map-plan.md`](PL-01267-wk-673-dislocation-with-attribution-map-plan.md)
Slice 1 and its Inputs; `RL-1264` (all of it); `RL-1361` §E and "What it obliges"; `RS-1201`
`:44-56` (S and R) and `:243-257` (the 13:57:02 correction).

## Acceptance Standard

Every command runs in the executor's own worktree (`env -C <worktree> …`), against the range
`origin/main...HEAD`, never a tip SHA alone. "The ruling" below is the decision-maker's record
that resolves DP-S1-1 to DP-S1-6 and adopts T1–T9 (activation need 1).

1. **Every blocking decision point has a resolver id before Task 1 starts.** The
   Decision points table of this plan's minted, `active` version shows a minted `RL-` id in the
   "Resolved by" cell of DP-S1-1, DP-S1-2, DP-S1-3, DP-S1-4, DP-S1-5 and DP-S1-6, and
   `python3 scripts/audit-docs.py` resolves each id (check 32).
2. **The adopted texts land verbatim.** For each of T1–T9 the ruling adopts, the executor's
   ledger shows `diff` of the ruling's text against the text as committed, with no difference
   other than the minted requirement ids and the amendment date. Where the ruling amends a
   text, the amended text is the one compared.
3. **FR-266 carries its amendment.** `grep -n '^| \*\*FR-266\*\*' docs/specs/03-rating-engine.md`
   prints one line, and that line contains each of these phrases (one `grep -c` per phrase,
   each printing `1`): `exact Shapley`, `largest remainder`, `declared change order`,
   `plain rounding is forbidden`, `isolated`, `cumulative`, `total − Σ isolated`,
   `order-dependent`, `FR-273`.
4. **Three new `03` §3.9 rows exist (R1, R2, R3 in T2–T4)**, each bold-defined once:
   `grep -c '^| \*\*FR-<id>\*\*' docs/specs/*.md` prints `1` in exactly one file for each of
   the three ids the lead issues, and each row sits between FR-266's row and the `### 3.10`
   heading.
5. **`03` §4.8 holds the portfolio frame.** The subsection T5 adds is present
   (`grep -n '^#### The portfolio frame (WK-673' docs/specs/03-rating-engine.md` prints one
   line, the heading, inside §4.8; the pattern is anchored because T5's dated note on the "does
   not design that schema now" sentence quotes the same words), and it states, in the ruling's words, (a) what a column outside its declared
   set does at the reader and at each scoring pass (DP-S1-1), (b) where `purpose`,
   `effective_date` and `quote_id` come from and whether a `mid_term_adjustment` or
   `cancellation` row can occur (DP-S1-2), (c) the exposure column's name and its null rule
   (DP-S1-3), (d) that every run-level frame refusal is `VALIDATION_FAILED` and a per-row fault
   keeps its own code (DP-S1-6). The sentence "it does not design that schema now" (`03:583` at `7b7757b3`) no
   longer stands unqualified: it carries a dated note pointing at the new subsection.
6. **`03` §4.6 and the hand-authored contract agree on their field names**, checked by the
   command in Task 4 Step 3, which prints `OK` and exits 0. It is shown **red first** on a
   scratch copy of the schema with one property deleted (Task 4 Step 4), and the ledger quotes
   that failure.
7. **`03` §5.2 publishes the adopted signatures.** `grep -n 'def dislocate\|def derive_changes\|def attribute' docs/specs/03-rating-engine.md`
   prints the lines T7 adopts and no other definition of those names; the old
   `attribute(changes: Sequence[BundleDelta], portfolio: pl.LazyFrame)` line is gone from the
   code block and recorded in the dated note T7 adds.
8. **The glossary is first and single-sourced.** Each term T8 adopts is bold-defined exactly
   once across `docs/specs/` (`grep -c` per term), in `00` §2.3, and that commit precedes or
   is the commit that first uses the term elsewhere (`git log --format=%h -S'<term>'
   origin/main..HEAD -- docs/specs` lists the glossary commit last, i.e. first in time).
9. **The label is corrected and the slug stays one-sided.**
   `grep -n '"dislocation-run"' backend/tests/test_contracts.py` prints one line, inside
   `ONE_SIDED_SLUGS`, naming `03 §4.6` and `WK-673`; `uv run pytest backend/tests/test_contracts.py -q`
   passes.
10. **No application behaviour changes.**
    `git diff --stat origin/main...HEAD -- packages backend frontend ':!backend/tests/test_contracts.py'`
    prints nothing (DP-S1-8 (a), confirmed by RL-1394 (minted from #1090 at `8f63cb56`): Slice 1 edits nothing in `score.py`).
11. **The write set holds.** `git diff --name-only origin/main...HEAD` lists only paths in the
    Write set section below.
12. **`RL-1264`'s three Slice-1 negative tests are named and placed** (map acceptance item 11):
    the ledger carries the table in Task 7 verbatim, and the dispatch records of `SL-1387`
    (Slice 3) and `SL-1388` (Slice 4) are told to carry them (the lead's; this slice cannot
    write another slice's plan).
13. **The docs checks pass on a detached copy of the committed tree** —
    `python3 scripts/audit-docs.py`, `python3 scripts/doc-id.py check`,
    `python3 scripts/doc-index.py --check`, `python3 scripts/register-lint.py` — each rc
    quoted with its `FAILED (n)` or "All checks passed." line and the `DISCLOSED (…)` line.
    A red check 31 is acceptable only for a working id this PR itself carries, and is named.
14. **The full two-half gate is green** (`CLAUDE.md` §11), reported as an rc table, because a
    test module and a contract file change. `uv run python scripts/req-coverage.py` lists the
    three new ids as specified with no test, which is expected: their tests are Slices 3 and
    4's (Task 7), and the ledger says so rather than leaving it silent.
15. **The slice closes on the maintainer's MERGE-ACK and a clean audit** (`PL-1267`
    acceptance item 8; `CLAUDE.md` §13: a Slice needs no maintainer acceptance line).

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path, never float** (`CLAUDE.md`
  §7). Every attribution figure the spec text defines as stored is an integer minor unit; a
  percentage is a derived view; S and R are decimal strings, never JSON numbers.
- **Money crosses the ZEN boundary only as integer minor units** (`03` FR-273, `03:222` at
  `7b7757b3`). Reconciliation is on those integers, not on a decimal carried through the engine.
- **Nobody hand-writes a shape `model-schema` already owns** (`CLAUDE.md` §2). None of
  `DislocationSpec`, `DislocationRun`, `BundleDelta`, `Attribution` exists in `model-schema` at
  `7b7757b3` (`grep -rn 'class Dislocation\|class BundleDelta\|class Attribution' packages/`
  prints nothing), so spec text and the hand-authored contract are their only definitions until
  Slices 2 and 3 add them.
- **Requirement ids are append-only and cited individually** (`CLAUDE.md` §5;
  `.claude/roles/planner.md`). The three new ids come from the lead at the slice's mint turn;
  the branch carries working ids until then (the `FR-1221` precedent, `03:180`).
- **A bolded id is a definition** (`spec-change`). Refer to existing ids unbolded.
- **A new term goes in `00` §2 before first use** (`CLAUDE.md` §7).
- **Never edit a frozen plan.** `PL-1267` is `active`; its premise a′ and its Slice 1 bullets
  are corrected here, at the sites below, not in its file.
- **One slice at a time within WK-673** (`delivery-process.md` §8); concurrency with other
  Works per `RL-1263` (Write set section).
- **No pandas, no new dependency.**

## Inputs

**The maintainer's acceptance of `PL-1267`**, `~/gi-pricing-plan.local/channel/to-lead.md`,
the entry headed "2026-10-03 17:53:43 BST — ACCEPTANCE: PL-1267 (WK-673 map plan, dislocation
with attribution) by the maintainer (by delegation); GO planner-673act", condition 2, verbatim:

> 2. **Slice 1's leaf** states, as a DP or a premise, the **§4.8 undeclared-column pass-through** question flagged at this map's mint (the eta line "PL-1267 map acceptance (maintainer; incl. S1 §4.8 undeclared-column pass-through)"): what the portfolio frame does with a column the contract does not declare.

Condition 3 of the same entry: "**Slices 1 → 4 are prepared first**; 5–7 follow by §5's
two-days-ahead rule", with WK-673 on G2's chain (`PL-1371` §1: WK-674 S2 → WK-673's build
slices → the script). This plan answers condition 2 as **a premise and a decision point**: the
reader half is already ruled (premise P1), and the scoring half is open (DP-S1-1).

**Rulings applied.** `RL-1264` (DP-1, DP-2 and the §0 disagreement; "What it obliges", Slice 1
bullets; the three Slice-1 negative tests); `RL-1184` (OQ-1187 decided (b)); `RL-1361` §E (the
frame premise) and "What it obliges" (the amending pass's line *"Slice 1's `03` §4.8 schema must
pass through columns outside its declared set"*); `RL-1263` (lanes and shared files); RL-1394 (minted from #1090 at `8f63cb56`), the ruling of DP-S1-1 to DP-S1-6 (and
DP-S1-7, DP-S1-8) that adopts T1 to T9, five with amendments, audited clean 2026-10-03.

**Open records read, not yet minted (named by PR and head, never by a hyphenated id).**
#1060 at `479d4b7d` carries RL 9771 (working id): FR-246's declared reads refused at save and at
compile, with already-compiled bundles still served (its "(ii)" and "(iii-b)"). It is cited in
DP-S1-1's rationale only, and is not a need. #1054 (FD 9772, working id: spec artifact examples
are never validated against `model-schema`) bears on §4.6's example; Task 4's key check is the
narrower guard this slice can carry.

## Scope

### Requirement coverage, each id individually

| Id | Where | What this slice writes |
|---|---|---|
| FR-266 | `03` §3.9 | the dated amendment, T1 |
| FR-263 | `03` §3.9 | none to its row; §4.6 gains the fields its run reports (T6) |
| FR-264 | `03` §3.9 | none to its row; §4.8 states which columns slicing may read (T5) |
| FR-265 | `03` §3.9 | none to its row; T3 and T4 state what the persisted artifact records |
| FR-273 | `03` §3.11 | cited by T1 and T2, unchanged |
| new R1 | `03` §3.9 | the reconciliation hard gate, T2 |
| new R2 | `03` §3.9 | attribution on ZEN through the compile path; ephemeral subset bundles (`RL-1264` DP-1), T3 |
| new R3 | `03` §3.9 | derived changes, regrouping and the partition check (`RL-1264` DP-2), T4 |

Highest requirement id in use at `7b7757b3` is read by the lead at the mint turn; the three
ids are allocated then, never guessed here.

**Interfaces and contracts in scope:** `03` §4.6 `DislocationRun` and its hand-authored
contract; `03` §4.8's portfolio frame; `03` §5.2's `analysis.py` block. **Not in scope:** the
§5.1 routes and their error responses (Slice 4); any `model-schema` shape (Slices 2 and 3); the
NFR the attribution cost measurement proposes (Slice 3, `RL-1264`); `RL-881`'s stale clause (the
decision-maker's record, `RL-1264` "Spec changes", last bullet); FR-224, FR-257 and `06` FR-364
(Slices 5 and 6); FR-231's weights (Slice 7).

### Premises re-derived at `7b7757b3`

| # | The premise | At `7b7757b3` | Status |
|---|---|---|---|
| P1 | The portfolio reader lets a column outside its declared set through | `RL-1361` §E: *"That schema must let columns outside its declared set pass through. A reader that keeps only the declared columns makes every bound key fail with "source column absent""*; restated in "What it obliges" (amending pass) and in its Acceptance (*"The frame premise"*) | **Ruled.** The reader passes undeclared columns through. This settles the reader; it does not settle what reaches the engine (DP-S1-1) |
| P2 | `score_batch` forwards every non-reserved column into the engine | `03` §4.8 `:595-598` (*"forwarded into `QuoteContext.inputs` verbatim, tolerating extra columns the algorithm does not declare"*); `score.py:262` `_BATCH_RESERVED_COLUMNS`; `:1033` builds `inputs` from every other column; `:1066-1068` spreads `**ctx.inputs` into the engine context | **Holds.** An undeclared portfolio column reaches the ZEN context on every row |
| P3 | An undeclared engine-context key can change a premium | `FD-1374` (`docs/findings/register.md:287`): the engine builds edges from `consumes` only and `passThrough` lets an undeclared read resolve from context; MEDIUM, owner WK-1178. #1060 (RL 9771, working id) rules compile-time refusal of undeclared reads, and keeps serving bundles compiled before the check | **Holds** until FR-246's enforcement ships, and afterwards for every bundle compiled before it |
| P4 | A column with a billing name refuses every row | `score.py:250` `_BILLING_SURFACE_KEYS` (`payment_schedule`, `apr`, `credit_agreement_term`, `instalment_schedule`, `instalment_count`); `_check_billing_surface` (`:425`) tests them against `ctx.inputs` keys, so a portfolio column of that name refuses the row with `INPUT_CONTRACT_VIOLATION` whatever the algorithm declares | **Holds.** Under forwarding, an ordinary book column such as `instalment_count` fails the whole run |
| P5 | MTA and cancellation rows cannot be rated | `score.py:395` `_check_purpose_mount` refuses every `mid_term_adjustment` or `cancellation` context until FR-217's inlining exists (FR-218); `QuotePurpose` (`model_schema/scoring.py:44`) has five members | **Holds** (`PL-1267` Risks, *"Slice 1 states whether the portfolio frame admits such rows"*) |
| P6 | `_round_minor`'s docstring sentence is there to correct (`PL-1267` premise a′; `RL-1264` §0 point) | `grep -rn 'def _round_minor' packages/pricing-core/src` prints nothing (over all of `packages/` the same pattern prints only `packages/pricing-core/tests/baseline_ladder.py:55`, a test helper), and `grep -n float64 packages/pricing-core/src/pricing_core/rating/score.py` prints nothing, so `RL-1264`'s target sentence ("the engine's float64 arithmetic") is gone; both re-run at `ee584dcc`. `SL-1345` (#1045, `1dd5e264`, 2026-10-01) replaced it: rungs are read across the binding with `string()` (`score.py:89-92`). Two dangling references remain in `_coerce_output_value`'s docstring (`score.py:955-959`), naming `_round_minor` and a `raw = float(result[source_key])` line that no longer exists | **No longer holds.** The obligation's target is gone; DP-S1-8 |
| P7 | The contract and §4.6 disagree | the contract has `job_id` (`:13`), `by_ladder_rung` and `errors`; §4.6's example (`03:490-517`) has none of them; the contract's `attribution` items hold `change`, `mean_change_pct`, `cumulative_change_pct` only | **Holds** (`PL-1267` premises c and c′) |
| P8 | The contract is hand-authored and one-sided | `backend/tests/test_contracts.py:87`, `"dislocation-run": "later-phase — 03 rating"`, inside `ONE_SIDED_SLUGS` (`:68`); listed literally in `scripts/audit-docs.py:2634` | **Holds.** Editing the file changes no path list; it is not a registry-exempt path (`RL-1263`, "Registry list, as corrected", item 2) |
| P9 | `attribute`'s signature cannot be implemented | `03:932`, `attribute(changes: Sequence[BundleDelta], portfolio: pl.LazyFrame) -> list[Attribution]`: no baseline, no resolver; `compile_bundle` is `async` and takes an `ArtifactResolver` (`compile.py:573`, protocol at `:443`), which `RL-1264` DP-1 (a) requires every subset to go through | **Holds**; DP-S1-4 |
| P10 | The structural diff exists to derive changes from | `diff_algorithms` (`model_schema/rating.py:570`) returns `AlgorithmDiff` (`:540`): `added_steps`, `removed_steps`, `changed_steps`, `repointed_tables`, `input_contract_changed`, `outputs_changed`; `Pins` (`:64`) has `rate_tables`, `models`, `reference_tables`, `custom_objectives` | **Holds** |
| P11 | S cannot be measured above K = 6 as defined | `RS-1201:50`: *"Order-sensitivity S = maxᵢ, max over all K! orders, of …"*. A cumulative figure under an arbitrary order needs v on every prefix, so S over all orders needs all 2^K subset ratings, which is what the above-six fallback exists to avoid | **Holds**; DP-S1-5 |
| P12 | The exposure column has a platform convention | `01` §4.2's example names `exposure_years` (`01:235`, `:282`, `:292`); `pricing_core/data/profile.py:145` defaults `exposure_column="exposure_years"`; `RL-1361` Ruled item 1: *"The exposure column is the one that schema names. This ruling chooses no literal"* | **Holds**; DP-S1-3 |
| P13 | The map plan's Slice 1 scope is internally inconsistent on §4.6 | `PL-1267:449-453` extends §4.6 with the attribution fields in Slice 1; `:461-465` sends "the shape parts" of DP-1 and DP-2 to the slice that first returns the type. `RL-1264` "Spec changes this record obliges" says of the §4.6 fields: *"so they are Slice 1's"* | **Holds**; DP-S1-7, resolved by the ruling, not by the plan |

### Risks

- **The ruling sitting is long.** Six blocking rows plus nine texts. Mitigation: each row has
  one recommendation, and T1–T9 are drafted in full so the decision-maker amends rather than
  writes.
- **Field names chosen now bind Slices 2 and 3.** If a build slice finds a name wrong, it
  amends §4.6 and the contract together with a dated note (the ordinary spec-change path); the
  Slice 4 guard then compares the generated shape against the contract.
- **#1060's ruling may change P3's weight.** If RL 9771 merges with a different mechanism,
  DP-S1-1's recommendation still stands on P4 (the billing-name refusal), which does not depend
  on FR-246.

## Decision points

Kind, blocking status and resolver per `document-ids.md` §1.7. Rows marked "decision point" are
the decision-maker's, resolved in one `RL-` that also adopts or amends T1–T9. **The slice may
not move `draft → active` while any blocking row is open.**

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S1-1 | **The §4.8 undeclared-column question (acceptance condition 2).** The reader keeps every column (P1). What does a scoring pass do with a portfolio column that the bundle being rated does not declare in its `input_contract` and that is not reserved? This applies to the baseline pass, the candidate pass and every subset pass of attribution | (a) **Forward it**, as `score_batch` does today (P2): every non-reserved column enters the engine context on every pass. (b) **Project per pass:** each pass rates a frame of the reserved columns plus exactly the names in **that bundle's own** `input_contract`; every other column stays beside the scored rows, joined back by `quote_id`, for slicing (FR-264), exposure weighting, drill-down and Slice 7's Factor source columns, and never enters the engine. (c) **Refuse it:** a column neither reserved nor declared by either bundle nor named by the spec is refused by name. (d) **Project to the union** of both bundles' contracts for every pass | **(b).** (c) contradicts P1 (`RL-1361` §E rules pass-through) and is out. (a) lets an undeclared read resolve from whatever the book happens to hold (P3) and lets a column such as `instalment_count` refuse every row (P4), so a run's result would depend on columns no contract names. (d) gives the baseline pass the candidate's new inputs, which are undeclared for the baseline: (a)'s hazard on one side, and an asymmetry the attribution would then attribute. (b) makes each pass see exactly what its contract declares, turns an undeclared read into a visible error row instead of a silent price, needs no change to `score_batch` (its own §4.8 tolerance stays, for FR-253), and shrinks the row dict each engine call marshals. Its cost: where a bundle compiled before FR-246's enforcement reads an undeclared name, the dislocation rates it differently from a live quote that happened to carry the key; that read already breaks FR-246, and the error row surfaces it | decision point | yes — Task 3 | **Resolved by RL-1394 (minted from #1090 at `8f63cb56`)** — **(b)**: each pass sees only its own bundle's declared names plus the stamped columns and `quote_id`; every other column passes through beside the rows and never reaches the engine; `score_batch` unchanged |
| DP-S1-2 | **Where do the reserved columns come from, and can an MTA or cancellation row occur?** §4.8 reserves `quote_id`, `purpose`, `effective_date`, `rating_version_ref`; the last is always stamped (§4.8, Task 3B rule). P5 makes MTA and cancellation unrateable | (a) **Per row from the portfolio:** `purpose` and `effective_date` are required portfolio columns; a run holding any `mid_term_adjustment` or `cancellation` row is refused before any rating with `INPUT_CONTRACT_VIOLATION`, naming the purpose and the row count. (b) Per row; such rows are **excluded and counted** on the artifact. (c) **Per run, from the spec:** `DislocationSpec` carries `purpose` (`new_business` or `renewal`) and `as_at` (an ISO date), stamped into every row of every pass; a portfolio column with a reserved name other than `quote_id` is refused by name. In every option `quote_id` is required, non-null and unique (it is the per-policy join key of the two passes and the drill-down identity), refused by name otherwise | **(c).** Attribution assumes every pass rates the same context except the bundle; one stamped purpose and date make that true by construction, and the run is reproducible from its spec alone (NFR-495 as this Work applies it). MTA and cancellation cannot arise, so FR-218's interim refusal never fires inside a run; when FR-217's inlining lands, admitting them is a spec change. (a) is honest but makes every book carry two operational columns it rarely holds, and mixes purposes inside one comparison. (b) silently changes the portfolio the approval cites. Against (c): a book mixing new business and renewals needs two runs | decision point | yes — Task 3 | **Resolved by RL-1394 (minted from #1090 at `8f63cb56`)** — **(c)**: `purpose` and `as_at` stamped per run from `DislocationSpec`; `new_business` or `renewal` only; reserved-name portfolio columns refused; subset passes stamp the baseline's ref, rows scratch |
| DP-S1-3 | **What is the exposure column called?** `RL-1361` leaves the literal to this schema (P12); Slice 2 bands by exposure share, and Slice 7's diff route (which has no `DislocationSpec`) weights by it | (a) **A fixed reserved name, `exposure_years`**: a decimal, non-null (null refused with `VALIDATION_FAILED` naming the column and the null count, `RL-1361` §E), never negative, zero allowed. (b) A name **per run** in `DislocationSpec` (`exposure_column`, default `exposure_years`). (c) Read from the portfolio Dataset's data dictionary | **(a).** It is `01`'s own convention (`01:235`) and the profiler's default, so freMTPL2-shaped data needs no mapping; it reaches Slice 7, which has no spec to name a column in; and one name cannot drift between a run and a diff over the same portfolio. (b) does not reach Slice 7. (c) needs a dictionary role `01` does not define (`DataDictionaryEntry` has no role field, `model_schema/datasets.py:139-153`) | decision point | yes — Task 3 | **Resolved by RL-1394 (minted from #1090 at `8f63cb56`)** — **(a)**: `exposure_years`, decimal, non-null, non-negative |
| DP-S1-4 | **The `analysis.py` signatures and the three types** (P9). `RL-1264` DP-1 needs `compile_bundle` (async, resolver) for every subset; DP-2 needs the derived list shown to the analyst before they regroup | (a) As T7: `dislocate` unchanged (two `CompiledBundle`s; it rates two bundles and compiles nothing); a new `async def derive_changes(baseline: RatingVersion, candidate: RatingVersion, resolver: ArtifactResolver) -> list[BundleDelta]`; `async def attribute(baseline: RatingVersion, candidate: RatingVersion, portfolio: pl.LazyFrame, spec: DislocationSpec, resolver: ArtifactResolver) -> Attribution`, where `Attribution` is the whole attribution part of §4.6 (method, parts, residual, derived changes, groups, subset bundle hashes). (b) `attribute` takes two `CompiledBundle`s and a caller-supplied subset builder callback. (c) As (a), but `attribute` returns `list[Attribution]` (one per group) and the residual, method and hashes go elsewhere | **(a).** Every subset must pass the compile path (`RL-1264` DP-1), which needs the versions and a resolver, so `attribute` is `async` by `spec-change`'s rule (it awaits an injected async dependency). (b) moves the compile-path guarantee into a callback no signature can enforce. (c) leaves the residual line, the method label and the subset hashes, all of which `RL-1264` and FR-266's amendment put on the artifact, without a type. `derive_changes` is what lets the server propose the list DP-2 (c) regroups | decision point | yes — Task 5 | **Resolved by RL-1394 (minted from #1090 at `8f63cb56`)** — **(a)**: `dislocate` unchanged; `async derive_changes`; `async attribute(baseline, candidate, portfolio, spec, resolver) -> Attribution` |
| DP-S1-5 | **S above K = 6** (P11). The F3 decision item 3 prints "the measured S and R" beside the fallback; S as defined needs all 2^K ratings | (a) **R exact; S as a labelled lower bound** over a declared number of orders that always includes the declared order and its reverse, printed as "S ≥ x over n orders", never as S. (b) **R only**; S omitted above six with the reason stated. (c) S exact regardless of cost | **(a).** R needs only the isolated runs and the total, so it is exact. A lower bound over sampled orders still shows order-dependence when it is large, which is the label's purpose, and it is never presented as the defined S. (b) loses that signal. (c) defeats the fallback's reason for existing. The deputy's rule that a sample is never presented as exact (`RL-1264` feasibility item 3) is kept by the label | decision point | yes — Task 2 (T1's above-six clause) | **Resolved by RL-1394 (minted from #1090 at `8f63cb56`)** — **(a)**: R exact; S as a labelled lower bound over ≥ 2 orders including declared and reverse; Slice 3 fixes the count |
| DP-S1-6 | **Error codes the new text names.** The spec text refuses a subset that does not compile, a regrouping that is not a partition, and a frame that breaks §4.8; it also fails a run that does not reconcile | (a) **Existing codes where one already means it**: `BUNDLE_COMPILE_FAILED` (subset), `VALIDATION_FAILED` (partition; null exposure, per `RL-1361` §E), `INPUT_CONTRACT_VIOLATION` (frame); the reconciliation failure gets **a new code registered by Slice 3**, the slice that first raises it, so Slice 1's text names the failure but no code. (b) New dislocation codes for every case, catalogued in Slice 1. (c) All four on existing codes, reconciliation included (`LADDER_RECONCILIATION_FAILED`) | **(a).** No new code without a raiser; Slice 1 then does not touch `03` §5.1's catalogue, which WK-674 S2 (`PL-1392`) and a WK-1178 fix slice also edit. (c) gives `LADDER_RECONCILIATION_FAILED` a second meaning (`03:818`, a ladder fault), and a code's meaning is the spec's | decision point | yes — Tasks 2 and 3 | **Resolved by RL-1394 (minted from #1090 at `8f63cb56`)** — **(a), amended**: existing codes; every run-level frame refusal `VALIDATION_FAILED`; per-row faults keep their own code; reconciliation code registered by Slice 3 |
| DP-S1-7 | **When do §4.6 and the contract gain the attribution and DP-1/DP-2 fields?** (P13) | (a) **Slice 1 writes all of them**, §4.6 and the hand-authored contract in one commit (T6); Slices 2 and 3 define `model-schema` shapes that match; Slice 4 makes the slug generated and compared. (b) The map's literal split: attribution fields now, DP-1/DP-2 fields with the type in Slice 3. (c) Only P7's reconciliation now; every new field with its type | **(a).** `RL-1264` places the §4.6 fields in Slice 1, and its reason (spec and contract must not disagree) is met here because the contract is still hand-authored: Slice 1 edits both. Build slices then implement named fields, which is `CLAUDE.md` §0's order (spec first, then code). (b) splits one artifact's fields across two slices for no stated reason. (c) leaves Slices 2 and 3 to invent field names | decision point | yes — Task 4 | **`RL-1264`** ("Spec changes this record obliges": *"so they are Slice 1's"*); **confirmed by RL-1394 (minted from #1090 at `8f63cb56`)** — **(a)** confirmed; `RL-1264`'s stated reason corrected |
| DP-S1-8 | **`RL-1264`'s docstring obligation, whose target is gone** (P6) | (a) **Discharged by events:** the ruling records that `_round_minor` no longer exists, and this slice edits nothing in `score.py`. (b) Also correct `_coerce_output_value`'s two dangling references (`score.py:955-959`), docstring only | **(a).** `score.py` is a contended file (`RL-1263` item 4), and lane B's queue holds an `RL-1343` decimal-output fix (`PL-1376` "Lane B order") that is likelier to touch `_coerce_output_value` than anything here; the dangling references are a finding for the auditor to file, not a reason to widen a spec slice | decision point | no — resolved at Task 6; default (a) applies until ruled | **Resolved by RL-1394 (minted from #1090 at `8f63cb56`)** — **(a)** confirmed; discharged by SL-1345 |

## Tasks

### Task 0: Preconditions

**Files:** the slice ledger (`docs/ledgers/LG-<working id>-….md`, the executor's).

- [ ] **Step 1:** Confirm the activation needs (Status section) at the dispatch tree:
  `git -C <worktree> log -1 --format='%H %aI' origin/main`; the ruling's id resolves
  (`grep -l '^id: RL-<n>' docs/rulings/*.md`); this plan is `active`; `SL-1385` is `active`.
- [ ] **Step 2:** `uv sync --all-packages` (a fresh worktree; `dev-commands`).
- [ ] **Step 3:** Baseline the four docs checks on the untouched tree and record rc and the
  `FAILED`/`DISCLOSED` lines in the ledger, so a later red is attributable.
- [ ] **Step 4:** Copy T1–T9 **as the ruling adopts them** into the ledger, with the ruling's id
  and the line range they came from. Every later step applies the ledger copy, never this
  plan's Appendix (the ruling is the text; the Appendix is a copy of it).

### Task 1: `00` §2.3 — the glossary, first

**Files:** Modify `docs/specs/00-overview.md` §2.3 (the table under `### 2.3 Rating layer`,
`00:157`; append after the `**Dislocation**` row at `00:170`).

- [ ] **Step 1:** For each term in T8, confirm it is not already bold-defined:
  `grep -rn '\*\*Shapley attribution\*\*\|\*\*Interaction residual\*\*\|\*\*Change group\*\*\|\*\*Subset bundle\*\*\|\*\*Portfolio frame\*\*' docs/specs/`
  prints nothing.
- [ ] **Step 2:** Append T8's rows, one per term, in the table's two-cell form.
- [ ] **Step 3:** `python3 scripts/audit-docs.py`; expect no new failure against Task 0 Step 3's
  baseline (the glossary single-sourcing and table cell-count checks are the ones this edit can
  trip).
- [ ] **Step 4:** Commit: `docs(specs): WK-673 S1 — 00 §2.3 glossary terms for attribution (PL-1395)`.

### Task 2: `03` §3.9 — FR-266's amendment and the three rows

**Files:** Modify `docs/specs/03-rating-engine.md` §3.9 (`03:182-189`).

- [ ] **Step 1:** Append T1 to the end of FR-266's row (`03:189`), inside the same table cell.
- [ ] **Step 2:** Append three rows after FR-266's row: T2 (R1), T3 (R2), T4 (R3), each with
  its working id, bold, in the existing two-cell form.
- [ ] **Step 3:** Run Acceptance 3's phrase greps and Acceptance 4's id greps; each must print as
  stated. A phrase missing means the ledger copy was not applied verbatim: fix the text, never
  the grep.
- [ ] **Step 4:** `python3 scripts/audit-docs.py`; expect only check 31-class findings for the
  working ids this branch carries, named.
- [ ] **Step 5:** Commit: `docs(specs): WK-673 S1 — FR-266 Shapley amendment and the §3.9 hard gate rows (PL-1395)`.

### Task 3: `03` §4.8 — the portfolio frame

**Files:** Modify `docs/specs/03-rating-engine.md` §4.8 (`03:570-647`).

- [ ] **Step 1:** Append T5 as the last part of §4.8, after the paragraph ending "reading
  `error_code` off this column." The anchor wraps in the file (`03:645-646` at `ee584dcc`), so
  match it across the newline.
- [ ] **Step 2:** Append T5's dated note to the sentence ending *"it does not design that schema
  now."* in §4.8's first paragraph after the heading note (`03:583-585` at `ee584dcc`), pointing
  at the new subsection. Do not delete the sentence: it records what
  was believed in 2026-08-30.
- [ ] **Step 3:** Read the result against the ruling's DP-S1-1, DP-S1-2, DP-S1-3 and DP-S1-6
  answers, one by one, and record in the ledger the sentence of T5 that carries each.
- [ ] **Step 4:** `python3 scripts/audit-docs.py` (table cell counts: T5's tables contain no
  literal pipe).
- [ ] **Step 5:** Commit: `docs(specs): WK-673 S1 — 03 §4.8 the portfolio frame (PL-1395)`.

### Task 4: `03` §4.6 and the hand-authored contract, together

**Files:** Modify `docs/specs/03-rating-engine.md` §4.6 (`03:490-517`); Modify
`docs/contracts/schemas/dislocation-run.schema.json`.

**Interfaces:** Produces the field names Slices 2 and 3 implement in `model-schema`.

- [ ] **Step 1:** Replace the whole JSON object in §4.6's code fence with T6's example, and add
  T6's dated note as a new paragraph directly under the `### 4.6 \`DislocationRun\`` heading,
  before the code fence.
- [ ] **Step 2:** In `docs/contracts/schemas/dislocation-run.schema.json`: (1) replace the
  whole `"attribution"` property with T6's `"attribution"` member; (2) insert the
  `"derived_changes"`, `"change_groups"` and `"attribution_summary"` members directly after it;
  (3) add the `"dependentRequired"` member at the top level, after `"required"`. Change nothing
  else; `by_ladder_rung`, `job_id` and `errors` already exist and stay as they are. Confirm that
  `common/money.schema.json` defines `$defs/MoneyMinor` and `$defs/Decimal` and that the edited
  file parses with no duplicate key (`contract-schema`).
- [ ] **Step 3:** Run the agreement check. It prints `OK` and exits 0:

```bash
uv run python - <<'PY'
import json, re, sys
from pathlib import Path

spec = Path("docs/specs/03-rating-engine.md").read_text()
block = spec.split("### 4.6 `DislocationRun`", 1)[1].split("```json", 1)[1].split("```", 1)[0]
example_keys = set(re.findall(r'"([a-z_]+)"\s*:', block))

schema = json.loads(Path("docs/contracts/schemas/dislocation-run.schema.json").read_text())

def props(node: object, out: set[str]) -> set[str]:
    if isinstance(node, dict):
        for name, sub in node.get("properties", {}).items():
            out.add(name)
            props(sub, out)
        for key in ("items", "additionalProperties"):
            if isinstance(node.get(key), dict):
                props(node[key], out)
    return out

schema_all = props(schema, set())
top = set(schema["properties"])
missing_in_schema = sorted(example_keys - schema_all)
missing_in_example = sorted(top - example_keys)
if missing_in_schema or missing_in_example:
    print("example keys not in schema:", missing_in_schema)
    print("schema top-level properties not in example:", missing_in_example)
    sys.exit(1)
print("OK")
PY
```

- [ ] **Step 4:** Prove it red: copy the schema to a scratch path, delete one top-level property
  that T6's example shows (for example `job_id`), point the script's schema path at the copy,
  run it, and quote the non-zero exit and the printed `schema top-level properties not in
  example` line in the ledger. Delete the scratch copy.
- [ ] **Step 5:** `python3 scripts/audit-docs.py` (its schema parse and `$ref` check, the "JSON
  schemas parsed, $refs checked" note) and `uv run pytest backend/tests/test_contracts.py -q`;
  both green. The slug is one-sided, so no comparison runs on it (`contract-guard`).
- [ ] **Step 6:** Commit both files in one commit:
  `docs(specs,contracts): WK-673 S1 — 03 §4.6 and dislocation-run.schema.json reconciled and extended (PL-1395)`.

### Task 5: `03` §5.2 — the signatures and the types

**Files:** Modify `docs/specs/03-rating-engine.md` §5.2 (the `# pricing_core/rating/analysis.py`
lines, `03:929-932`, and a types paragraph after the code block).

- [ ] **Step 1:** Replace the two `analysis.py` lines with T7's three signatures, each with its
  trailing dated comment, in the block's existing comment style (`# added 2026-… (…)`).
- [ ] **Step 2:** Add T7's types paragraph after the block.
- [ ] **Step 3:** Run Acceptance 7's grep.
- [ ] **Step 4:** `python3 scripts/audit-docs.py` (it checks every `pricing-core` function a
  workflow cites; `WF-700` cites dislocation — confirm no new failure).
- [ ] **Step 5:** Commit: `docs(specs): WK-673 S1 — 03 §5.2 dislocate, derive_changes, attribute and their types (PL-1395)`.

### Task 6: the test label, and DP-S1-8

**Files:** Modify `backend/tests/test_contracts.py:87`. `score.py` is not edited: DP-S1-8 (a),
confirmed by RL-1394 (minted from #1090 at `8f63cb56`).

- [ ] **Step 1:** Replace the value of the `"dislocation-run"` entry with T9's string. Change
  nothing else in `ONE_SIDED_SLUGS`.
- [ ] **Step 2:** `git diff origin/main...HEAD -- backend/tests/test_contracts.py` shows exactly
  one removed and one added line; quote it in the ledger (the dispatch record's `RL-1263` check
  reads this).
- [ ] **Step 3:** `uv run pytest backend/tests/test_contracts.py -q`; green.
- [ ] **Step 4:** Record in the ledger: "DP-S1-8 (a): `score.py` not edited; the target of
  `RL-1264`'s docstring obligation was removed by `SL-1345` (#1045, `1dd5e264`)".
- [ ] **Step 5:** Commit: `test(contracts): WK-673 S1 — dislocation-run's one-sided label names 03 §4.6 and WK-673 (PL-1395)`.

### Task 7: name `RL-1264`'s three Slice-1 negative tests

**Files:** the ledger only.

- [ ] **Step 1:** Copy this table into the ledger verbatim. Each test is built, and shown red on
  deliberately broken input, by the slice named; this slice builds none of them, because none
  of the code they test exists yet.

| `RL-1264` violation | Test name | File | Built by |
|---|---|---|---|
| a subset bundle persisted as a Rating Version, or visible in a version list | `test_dislocation_subset_bundles_never_become_rating_versions` | `backend/tests/test_dislocation_runs.py` | Slice 4 (`SL-1388`): the Job handler is the only code that could write a row |
| a subset that fails to compile and is skipped instead of failing the run by name | `test_attribute_fails_the_run_naming_a_subset_that_does_not_compile` | `packages/pricing-core/tests/test_rating_attribution.py` | Slice 3 (`SL-1387`) |
| a regrouping that leaves a derived change out, or puts one in two groups, and is accepted | `test_attribute_refuses_groups_that_do_not_partition_the_derived_changes` | `packages/pricing-core/tests/test_rating_attribution.py` | Slice 3 (`SL-1387`); Slice 4 adds the route's 422 |

- [ ] **Step 2:** Tell the lead, in the PR body, that the dispatch records of `SL-1387` and
  `SL-1388` must carry these rows (Acceptance 12).

### Task 8: the gate, the docs checks, the PR

- [ ] **Step 1:** The full two-half gate (`CLAUDE.md` §11, through the gate slot per
  `dev-commands`); rc per command into the ledger.
- [ ] **Step 2:** The four docs checks on a detached copy of the committed tree (Acceptance 13).
- [ ] **Step 3:** `git diff --name-only origin/main...HEAD` against the Write set (Acceptance 11).
- [ ] **Step 4:** `python3 scripts/doc-index.py` (regenerate `docs/INDEX.md`) in the last commit
  only.
- [ ] **Step 5:** Open the PR; the body names the range `origin/main...<branch>`, the ruling id,
  the working requirement ids awaiting the mint, and Task 7's request.

## Write set, and its serialisation (`RL-1263`)

Measured at `7b7757b3`. `RL-1263` option (c): two concurrent build slices may not both change
the same existing function, class, spec section or policy table; registry files are exempt for
append-only edits; any other shared path serialises unless the lead's dispatch record names the
path and the check. This slice holds a gate slot (it changes a test module and a contract), so
it counts as a build slice, not preparation; whether to dispatch it on lane A or lane B is the
lead's, under `PL-1371`'s G2 order and condition 3 above.

| Path | This slice | `SL-1377` (`PL-1376`, running, lane B) | WK-674 S2 (`PL-1392`, queued) | WK-690 S3 (`PL-1382`, queued) | Serialisation |
|---|---|---|---|---|---|
| `docs/specs/03-rating-engine.md` §3.9 | FR-266 row amended; three rows appended | §3.3 only (FR-228, FR-230) | §3.10 notes only | none (edits `02`, `06`) | section-disjoint: none |
| `docs/specs/03-rating-engine.md` §4.6, §4.8 | example and note; the portfolio frame | §4.2 only | a new §4.12 after §4.11 (its C4) | none | section-disjoint: none |
| `docs/specs/03-rating-engine.md` §5.2 | the `analysis.py` lines and a types paragraph | **T9: a §5.2 signature** (`seed_from_model`) | none found | none | **serialises with `SL-1377`**: this slice starts after `SL-1377` merges |
| `docs/specs/03-rating-engine.md` §5.1 | **none** (DP-S1-6 (a)) | the seed row (`T7`) | one row appended; catalogue not edited | none | not shared |
| `docs/specs/00-overview.md` §2.3 | rows appended | none found | none found | none found | not shared |
| `docs/contracts/schemas/dislocation-run.schema.json` (hand-authored, not exempt) | edited | none | none (its write set: no hand-authored schema touched) | none | not shared |
| `backend/tests/test_contracts.py` `ONE_SIDED_SLUGS` | one existing entry's value | two entries added | entries added (its C15) | `DECLARED_AND_UNBUILT` only | **serialises with `SL-1377`** (already, by §5.2). Against WK-674 S2: serialises unless the dispatch record names the path and shows this slice's diff is the single `"dislocation-run"` line (Task 6 Step 2) and S2's diff does not touch that key |
| `packages/pricing-core/src/pricing_core/rating/score.py` | none (DP-S1-8 (a), confirmed by RL-1394 (minted from #1090 at `8f63cb56`)) | none | none | none | not shared |
| the ledger; `docs/INDEX.md` | new; regenerated | — | — | — | `INDEX.md` is registry-exempt |

**Not written:** `docs/open-questions.md` and `03` §10 (no new OQ; OQ-1187's decided row keeps its
"exact Decimal reconciliation" wording as the record of what was ruled at 11:39:35, and T1 cites
the 13:57:02 correction); `docs/roadmap.md`; `PL-1267`; any `model-schema`, `backend/src` or
`frontend` file; `RL-881`.

## Status

`draft`. **Activation needs**, all required before `SL-1385` moves `draft → active`:

1. **The ruling is minted:** one decision-maker `RL-` resolving DP-S1-1 to DP-S1-6 (and DP-S1-8,
   or its default stands) and adopting or amending T1–T9, merged to main. **DP-S1-1 to DP-S1-6
   block activation.** DP-S1-7 is resolved by `RL-1264` (the ruling may overrule it); DP-S1-8 is
   non-blocking with default (a). The ruling is RL-1394 (minted from #1090 at `8f63cb56`), audited clean 2026-10-03; it
   rules all eight and is minted in the same PR as this plan.
2. **This plan is minted** (`PL-<n>`), its Decision points table carries the ruling's id, and
   `status: active`; `SL-1385`'s `relates` gains it.
3. **`SL-1377` has merged** (the §5.2 and `ONE_SIDED_SLUGS` serialisation above).
4. **A gate slot is free** under `RL-1263` (at most two build slices, from different Works; none
   while an NFR measurement runs), dispatched in `PL-1371`'s G2 order as the lead reads it. This
   slice does not depend on WK-674 (`PL-1267` Sequencing).

Not needs: #1060 (RL 9771) and #1054 (FD 9772) are cited for rationale only.

## Appendix — texts T1–T9 as the ruling adopts them

Copied verbatim from RL-1394 (minted from #1090 at `8f63cb56`), its "The exact texts" section, T1 to T9; the
planner's drafts they replace are in that ruling's PR range and this plan's history at
`a6b80982`. The ruling governs on any difference, and Task 0 Step 4 copies from the ruling,
never from here. `<date>` is the merge date the executor writes; `R1`, `R2`, `R3` are the
working ids, replaced by the ids the lead issues; `PL-<n>` and `RL-<n>` are this plan's and
the ruling's minted ids.

### T1 — appended to FR-266's row (`03` §3.9), inside the same cell, after its last sentence

Amended from the draft: v(S) may come from a proven ladder replay (`RL-1264` feasibility item
2); the declared change order points at R3; the bound's order count is Slice 3's.

```markdown
*(Amended <date>, WK-673 Slice 1, on OQ-1187's decision (`RL-1184` F3), the deputy's F3 decision of 2026-09-28 12:10:21 BST as corrected at 13:57:02 BST (`RS-1201`), `RL-1264` and `RL-<n>`.)* **The attribution of record is exact Shapley over the declared changes, for K ≤ 6.** For each policy, each change's Shapley value is computed exactly, as a rational with denominator K!, from v(S) for each of the 2^K subsets S of the declared changes, where v(S) is the policy's payable premium in integer minor units under the subset bundle for S (R2), or a ladder replay proven equal to it under `RL-1264`'s feasibility rule. The K values are allocated to integer minor units by **largest remainder**, ties broken in the declared change order (R3), so that the policy's parts sum exactly to its candidate minus baseline payable premium; plain rounding is forbidden. Portfolio figures are sums of the per-policy integer parts. The **isolated** figure (the change applied alone) and the declared-order **cumulative** figure are views beside the Shapley figure, never the attribution, and the **interaction residual**, total − Σ isolated, is its own line. **Above K = 6** the analyst groups the changes into at most 6 change groups (R3) and Shapley runs over the groups; where the analyst does not group them, the isolated-plus-cumulative method with its residual line is shown with R and a lower bound on S (`RS-1201` defines both), labelled order-dependent and never presented as a decomposition. R is exact. The bound is the maximum over a declared number of orders, at least 2 and always including the declared order and its reverse; it is printed as "S ≥ x over n orders", never as S, and the run records n. Exactness holds on the integer minor units each rating returns through FR-273's boundary, not on a decimal carried through the engine (§3.11).
```

### T2 — new row R1, the first of three rows appended after FR-266's row

Adopted as filed, with one clause amended (the plain-rounding fixture must be a case where
plain rounding does not sum; otherwise the test cannot fail).

```markdown
| **R1** | **Attribution reconciles exactly on the rating path's own integers, on every run.** Every attribution part, the interaction-residual line and the total are integer minor units taken from the payable premium's `value_minor` as the rating path produces it (FR-273). Per policy and at portfolio level, the Shapley parts sum exactly to the total, and the isolated figures plus the residual line sum exactly to the total, as integers, with no float summed after rounding. The run checks both on every run and fails, naming the first policy that does not reconcile, rather than persist a result that does not. The check is proven on deliberately broken input: a plain-rounding allocation, on a policy where plain rounding does not sum to the total, and a Shapley value perturbed by one minor unit are each refused. *(Added <date>, WK-673 Slice 1: the deputy's F3 item 4, corrected 2026-09-28 13:57:02 BST; `RL-<n>`.)* |
```

### T3 — new row R2, after R1

Amended from the draft: a subset bundle compiled to verify ladder replay is bound the same way.

```markdown
| **R2** | **Attribution runs on the ZEN engine through the ordinary compile path, and its subset bundles are ephemeral.** Each subset of the declared changes is a bundle built at step granularity from the baseline's pins and algorithm with that subset's changes substituted, compiled by `compile_bundle` and hydrated by `load_bundle`, so it passes the same validation as a real version (FR-240, FR-274, FR-275, FR-276) and is rated by the engine, never by a mirror of it. This holds for every subset bundle a run compiles, whether v(S) is read from it or it verifies a ladder replay (FR-266's amendment). A subset bundle is content-addressed and has **no Rating Version identity**: it is never a `rating_version` row, and it is never approvable, deployable or listed in any version list. It is cached per run by its content hash and discarded with the run's scratch. A subset that fails to compile fails the run with `BUNDLE_COMPILE_FAILED`, naming the subset; it is never skipped. The run artifact records how many subset bundles were compiled and their content hashes, and whether v(S) came from re-rating or from ladder replay (§4.6). *(Added <date>, WK-673 Slice 1: `RL-1264` DP-1 (a), with its conditions; `RL-<n>`.)* |
```

### T4 — new row R3, after R2

Amended from the draft: the unit is the step; pins travel with the step that accounts for
them; the declared change order is defined; an ungrouped change is named by its id.

```markdown
| **R3** | **The declared changes are derived, and the analyst may group them.** The server derives the change list from the difference between baseline and candidate, at step granularity: each `step_id` the structural diff (FR-219) reports as added, removed, or present in both with any field changed is exactly one derived change, however many of its fields changed. Its kind is `step_added`, `step_removed`, `table_repointed` where the only changed field is the step's table or lookup reference, or `step_changed`. A pin difference (FR-237) that a derived step change accounts for, through that step's table, lookup or model reference, is part of that change, never a second one; a pin difference no step change accounts for is its own derived change, of kind `pin`. Derived changes are numbered `c1`, `c2`, … in the derived order: step changes sorted by `step_id`, then unaccounted pin differences sorted by their reference string. The analyst may merge derived changes into at most 6 named **change groups** in the `DislocationSpec`. The server checks that the groups partition the derived list exactly, every derived change in exactly one group, and refuses otherwise with `VALIDATION_FAILED`, naming each change left out or placed twice. With no groups given, each derived change is its own group, named by its id, and above 6 FR-266's above-six rule applies. The **declared change order** is the order of the groups as the analyst gives them, or with no groups the derived order. The derived list and the groups are both on the artifact (§4.6). *(Added <date>, WK-673 Slice 1: `RL-1264` DP-2 (c); `RL-<n>`.)* |
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
*(Amended <date>, WK-673 Slice 1, `RL-<n>`: reconciled with `dislocation-run.schema.json` (`job_id`, `by_ladder_rung` and `errors` added to the example) and extended with FR-266's attribution as amended, R1, R2 and R3. Money is integer minor units. `mean_change_pct` and `cumulative_change_pct` on an `attribution` item are derived views: `shapley_minor` (or, under `order_dependent`, `isolated_minor`) and `cumulative_minor` as a percentage of `totals.baseline_premium_minor`. `method` is `shapley` or `order_dependent`; `shapley_minor` is null only under `order_dependent`, and `order_sensitivity_lower_bound`, `residual_share` and `orders_sampled` are non-null only under it. S and R are decimal strings. `subset_valuation` is `rerate` or `ladder_replay`, and `replay_fell_back` is true where a replay mismatch fell the run back to re-rates (`RL-1264`); Slice 3 may amend these two with a dated note if it does not adopt replay.)*
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

The figures reconcile as R1 requires (checked at ruling): Shapley 594 700 00 − 129 800 00 +
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
      "description": "Per change group: the Shapley part of record and the isolated and cumulative views, in integer minor units (FR-266 as amended, R1).",
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
      "description": "The changes derived from baseline and candidate at step granularity (R3).",
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
      "description": "The analyst's groups, partitioning derived_changes exactly (R3). Their order is the declared change order.",
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
      "description": "Method, totals, S and R, and the subset bundles compiled (FR-266 as amended, R1, R2).",
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
async def derive_changes(baseline: RatingVersion, candidate: RatingVersion,    # added <date> (WK-673 S1, R3)
                         resolver: ArtifactResolver) -> list[BundleDelta]
async def attribute(baseline: RatingVersion, candidate: RatingVersion,         # amended <date> (WK-673 S1,
                    portfolio: pl.LazyFrame, spec: DislocationSpec,            # RL-1264 premise: the old form took
                    resolver: ArtifactResolver) -> Attribution                 # no baseline and could not compile subsets)
```

The types paragraph, directly after the §5.2 code block that holds these lines:

```markdown
*`DislocationSpec` (added <date>, `RL-<n>`): `baseline_ref`, `candidate_ref`, `portfolio_dataset_version_id`, `purpose`, `as_at` (§4.8's portfolio frame), `segments` (the Factors FR-263 averages by), `band_edges_pct`, `mover_threshold_pct` (FR-263), and optional `change_groups` (R3). `BundleDelta`: one derived change, `id`, `kind`, `description`, as §4.6's `derived_changes` item. `Attribution`: §4.6's `derived_changes`, `change_groups`, `attribution` and `attribution_summary` together. All three are defined in `model-schema` by the slice that first returns them (WK-673 Slices 2 and 3) and match §4.6 field for field.*
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

## Self-review

**1. Spec coverage.** `PL-1267` Slice 1's bullets, each to a task: FR-266's amendment → Task 2
(T1); the hard gate as requirements → Task 2 (T2, T3); §4.6 reconciled and extended → Task 4
(T6, DP-S1-7); §4.8's frame with exposure and the MTA question → Task 3 (T5, DP-S1-1 to
DP-S1-3); DP-1's conditions and DP-2's partition rule → T3, T4, T6; §5.2's types and `attribute`
→ Task 5 (T7, DP-S1-4); glossary first → Task 1 (T8); the label → Task 6 (T9); the docstring →
DP-S1-8 (target gone, P6); `RL-1264`'s three negative tests named → Task 7. The maintainer's
condition 2 → P1 plus DP-S1-1, and T5's last paragraph. `RL-1361` §E's obligation on this slice
→ P1 and T5.

**2. Placeholder scan.** `<date>`, `R1`–`R3` and `RL-<n>`/`PL-<n>` in the Appendix are values
fixed at merge and mint, named as such; no step says "add validation" or "similar to". T6's
`errors` item is as the ruling's T6 example gives it.

**3. Consistency.** Names used across tasks and texts: `derive_changes`, `attribute`,
`DislocationSpec.purpose`, `DislocationSpec.as_at`, `change_groups`, `attribution_summary`,
`exposure_years`, `quote_id`; T5, T6 and T7 use the same ones. Every locator was read at
`7b7757b3`. T6's arithmetic was checked by hand above.

**4. Rulings between sweep and filing.** Read at origin/main `7b7757b3` and the open-PR list at
19:45 BST: #1060 (RL 9771) and #1054 (FD 9772) bear on this subject and are cited; #1086
(PL 9765, working id; now `PL-1392`) was read at `f8c9eeb7` for the Write set; nothing open rules on FR-266, §4.6, §4.8
or §5.2's `analysis.py` block.
