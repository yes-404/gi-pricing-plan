---
id: RL-9926
family: ruling
title: OQ-1223 decided (a) — an enum Rating Input declares its level order with an opt-in `ordered` flag, a `monotone` property sweeps an ordered enum's levels in order, and an unordered input leaves every bundle hash unchanged; WK-675 S5 is contract-changing
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-11
owner: decision-maker           # a technical decision-point ruling (§1.6 RL row); the maintainer ruled it, this records it
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [OQ-1223, PL-1546, PL-1286, SL-1547, SL-1600, OQ-1224, RL-1365]
---

# RL-9926 — OQ-1223 decided (a): an enum input declares its level order, opt-in; an unordered input leaves every bundle hash unchanged

*Disclosure: drafted under working id 9926, reserved by the lead (team-lead) on 2026-10-11
(`~/gi-pricing-plan.local/handover/brief-dm-lanec-2026-10-11.md`, "Reserved working ids").
The id is minted in a later docs batch. When it is minted, the working id in this record and
in the three rows it edits is replaced by the minted id.*

## How this was ruled

- **The ruling is not this record's.** It is the maintainer's (by delegation), in the entry
  of `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-11 11:00:57 BST — OQ-1223 /
  DP-3 RULED: (a), declare `ordered` on InputContractField, OPT-IN, with the hash-stability
  condition made testable" (`to-lead.md:21971`). That file is local, so a repository reader
  cannot open it (RFC-777). The entry is therefore quoted whole below. This record decides
  nothing beyond it.
- **The options it ruled on** were laid out in the decision-maker's memo
  `~/gi-pricing-plan.local/handover/dm-oq1223-2026-10-11.md` (seat `dm-lanec`, 2026-10-11).
  That memo is also local, so its substance is restated in "Verified first" below.
- **The decision point.** OQ-1223 is `PL-1286`'s DP-3. `PL-1546`'s Decision points table
  makes it blocking for S5's GO ("yes, for S5's GO … decision-maker, by `RL-`"), and
  `PL-1546` acceptance item 6 (`:105–106`) reads: *"S5 does not start before OQ-1223 is
  decided: `git grep -n 'OQ-1223' -- docs/open-questions.md` on S5's base tree shows the row
  decided, with its resolver `RL-`."*

## Ruled

**The maintainer's decision, by delegation, quoted whole** (`to-lead.md:21971`–`21981`):

> ## 2026-10-11 11:00:57 BST — OQ-1223 / DP-3 RULED: (a), declare `ordered` on InputContractField, OPT-IN, with the hash-stability condition made testable
> Read before ruling: the memo handover/dm-oq1223-2026-10-11.md (:9–34, :52, :65); compile.py @99f22479 :625 (`input_contract=[field.model_dump() for field in algo.input_contract]`, inside the JdmGraph that bundle_hash hashes) and :669–672 (the sub_graphs omit-when-empty precedent, "so every stored content_hash stays reproducible"). The rule: a runtime change must not reprice or rehash an unchanged bundle (10 Oct A-2 ruling, opt-in).
> 1. (a) ADOPTED. Add `ordered: bool = False` on InputContractField, valid ONLY with `type: enum` and a non-empty `domain`; the list order of `domain` is the declared order. The validator refuses `ordered` on any other type, or without a domain; if SL-1600 has merged, it raises InputFreeError. properties.py admits an ORDERED enum for `monotone` and sweeps its levels in order. An unordered enum stays refused (the tested interim, properties.py :145–147), so no existing input becomes sweepable unless someone opts in. That answers the memo's own (b) risk at :52.
> 2. HASH CONDITION, testable, red first:
>    (i) `ordered` is OMITTED from the dumped field when false (the sub_graphs precedent), and present only when true;
>    (ii) a test recomputes the content_hash of an EXISTING stored or fixture bundle at head and shows it equal to the base's, and shows it red when the omission is removed;
>    (iii) the money fixtures and the pinned hash are unchanged;
>    (iv) a bundle with `ordered: true` hashes differently from the same bundle without it (opt-in enters the hash).
> 3. S5 is CONTRACT-CHANGING (model-schema; docs/contracts rating-algorithm.schema.json and generated.json regenerated on the merge base; the frontend regenerated). The frontend shows an ordered input's levels in declared order, display only, from the generated type. RL 9926 states all of this.
> 4. RL 9926 is the decision-maker's: it rules OQ-1223 with this text, closes the OQ in BOTH mirrors (open-questions.md and 03 §10) by a dated line, and is cited by S5's LG. It meets PL-1546 acceptance item 6 (the resolver RL on S5's base). (c) is rejected: it would cut a real P2 capability without need. (b) is rejected (the memo's reasons). (d) is out of scope.
> 5. Next: the DP-S5-a memo, as planned.

## Verified first, at 99f22479a20e7fa64f8b6654e0d371c595b1e35a

`origin/main` was re-fetched immediately before this record was committed and was still
`99f22479`.

| Premise | Where | What the source says |
|---|---|---|
| The question | `docs/open-questions.md:135`; `03-rating-engine.md:1499` | "How does an ordinal categorical input take part in a `monotone` property?" Options (a) "Declare ordinality on `InputContractField` and sweep every level in order"; (b) "Read the order of `domain` … the order is then an accident of how a list was written, not a declaration". Status open, owner WK-675. |
| The shape | `model_schema/rating.py:275–298` | `RatingInputType` is `int`, `decimal`, `string`, `date`, `bool`, `enum`; `InputContractField` carries `name`, `type`, `nullable`, `min`, `max`, `pattern`, `domain: list[str] \| None`, `description`, and no order. |
| The interim refusal | `pricing_core/rating/properties.py:145–147`; `backend/tests/test_regression_suites.py:332` | `if field.type not in (RatingInputType.INT, RatingInputType.DECIMAL): raise UnsweepableProperty(f"monotone input {check.input!r} is {field.type.value}, not orderable")`; the `string` case is a test row ("not orderable"). |
| The requirement the sweep amends | `03-rating-engine.md:181`, FR-261 case (4) and its last sentence | refused "(4) an input absent from the algorithm's input contract or not orderable (neither `int` nor `decimal`)"; "The named input must be an `int` or `decimal` with a range (`OQ-1223`: ordinal inputs …)". |
| The requirement the field amends | `03-rating-engine.md:82`, FR-213 | "for each Rating Input, a name, type (`int`, `decimal`, `string`, `date`, `bool`, `enum`), nullability, valid range or enum domain, and a description". |
| Why the hash condition exists | `pricing_core/rating/compile.py:625`, `:660–678` | `input_contract=[field.model_dump() for field in algo.input_contract]` inside `JdmGraph`; `bundle_hash` hashes `graph.model_dump()` with the pins. A new defaulted field changes every field's dump unless it is omitted at its default. |
| The omission precedent | `compile.py:669–672` | "`Pins` had four lists before WK-1250 Slice 2. A version that pins no sub-graph hashes as it always did, so every stored `content_hash` stays reproducible from its pins." `del pins_dump["sub_graphs"]` when empty. |
| A pinned hash the suite carries | `pricing-core/tests/test_rating_shadowed_inputs.py:74`; `test_rating_wire_order.py:145` | `_SCORE_FIXTURE_HASH = "sha256:6458c7c80627d20602a8d82821a80e3fb7500c75c1d3bf9bc1033ba74f7a918e"`, in both files. |
| SL-1600 has not merged | `git grep -n InputFreeError origin/main -- packages` | no output at `99f22479`. The validator's exception class is therefore decided at S5's GO, by item 1's condition. |
| The contract carriers | `docs/contracts/schemas/rating-algorithm.schema.json`; `docs/contracts/openapi/generated.json` | `"domain"` appears in the first; `InputContractField` appears 6 times in the second (`grep -o 'InputContractField' docs/contracts/openapi/generated.json \| wc -l` → 6). |

## What it obliges

1. **OQ-1223 is decided (a), opt-in.** The register row (`docs/open-questions.md:135`) and
   `03` §10's mirror row (`03-rating-engine.md:1499`) are struck and marked decided by a dated
   line naming this record, in this record's commit. The options column is left as it was.
   The roadmap's decision-gate row **Before Phase 2** (`roadmap.md:2707`) strikes the id and
   is recounted from 18 (3 open) to 18 (2 open), with a dated line (`spec-change`: "Deciding
   one edits that row too … Recount the row").
2. **What WK-675 S5 (`SL-1547`) builds, as the ruling states it.** The obligation lands in
   `03` §3 with the code, in S5's commit, not here (`CLAUDE.md` §2: "A change spanning both
   lands as one commit — spec, code, tests"). This record names the text S5 must amend, and
   S5's `LG-` cites this record:
   - **FR-213**, a dated clarification: an `enum` Rating Input may declare `ordered: true`,
     valid only with a non-empty `domain`, whose list order is the declared level order.
     `ordered` is `false` by default.
   - **FR-261**, a dated amendment: case (4)'s "not orderable" admits an `ordered` enum. A
     `monotone` property on it sweeps the levels of `domain` in declared order. How the run
     labels that grid, and how `lower`/`upper` apply to levels, are S5's to specify in this
     amendment; the ruling does not fix them. An unordered `enum`, and every `string`, `date` and `bool` input, stays refused with
     `REGRESSION_PROPERTY_INVALID`, as today.
   - **`model-schema`**: `ordered: bool = False` on `InputContractField`. A validator refuses
     `ordered: true` on any type but `enum`, or without a non-empty `domain`. It raises
     `InputFreeError` if `SL-1600` has merged by S5's base, and otherwise `ValueError`.
   - **`pricing-core`**: `properties.py` admits an ordered enum and sweeps its levels in
     order. `to_jdm` (`compile.py:625`) leaves `ordered` out of each field's dump when it is
     `false`, and keeps it in when it is `true`.
   - **The hash condition, red first** (ruling item 2, (i)–(iv)): the omission; an existing
     stored or fixture bundle's `content_hash` equal at head and at base, shown red when the
     omission is removed; the money fixtures and the pinned hash unchanged (for example
     `_SCORE_FIXTURE_HASH` above); and `ordered: true` changing the hash. S5's `LG-` shows
     each red line and each green line.
3. **S5 is contract-changing.** `model-schema` changes;
   `docs/contracts/schemas/rating-algorithm.schema.json` and
   `docs/contracts/openapi/generated.json` are regenerated on S5's merge base
   (`uv run python scripts/generate-contracts.py --check` exits 0 at S5's head); the frontend
   client is regenerated (`pnpm --dir frontend generate:api`). The frontend shows an ordered
   input's levels in declared order, display only, from the generated type. S5 is already
   OpenAPI-contract-changing under the 10:55:02 BST entry's DP-A (a). This ruling widens that
   to a `model-schema` artifact shape.
4. **Acceptance item 6 of `PL-1546` is met by this record once minted.** On S5's base tree,
   `git grep -n 'OQ-1223' -- docs/open-questions.md` shows the row decided, with this
   record's minted id as its resolver.
5. **Rejected.** (b), reading the order of `domain` for every enum: it would make every
   existing enum sweepable without a declaration. (c), deferring with the interim refusal
   standing: it would cut a real P2 capability without need. (d), deriving the order from a
   pinned Banding: out of scope, because it depends on `OQ-1224` (owner WK-1178, open).

## Acceptance — the violation that must become detectable

The violation: an unordered input's bundle hash moves; an input becomes sweepable without
declaring `ordered: true`; `ordered` is accepted on a non-enum or without a domain; a
`monotone` on an ordered enum visits its levels out of declared order; or S5 merges with
the contracts not regenerated.

- *Violation: a hash moves.* Ruling item 2 (ii)'s test reds: an existing stored or fixture
  bundle's `content_hash` at S5's head differs from the base's. It is proven red on a dump
  that keeps `ordered: false`. The pinned `_SCORE_FIXTURE_HASH` tests (`test_rating_shadowed_inputs.py:74`,
  `test_rating_wire_order.py:145`) and the money fixtures stay green, unchanged.
- *Violation: opt-in does not enter the hash.* Item 2 (iv)'s test reds.
- *Violation: an input becomes sweepable unasked.* The existing refusal test
  (`test_regression_suites.py:332`) stays green, and S5 adds an unordered-`enum` refusal row
  beside it.
- *Violation: `ordered` accepted where it is invalid.* The validator's negative tests
  (`ordered` on `int`; on `enum` with no or an empty `domain`) red if the validator is removed.
- *Violation: the levels swept out of order.* A planted inversion between two adjacent
  declared levels is reported as a counterexample naming those two levels.
- *Violation: the contracts drift.* `uv run python scripts/generate-contracts.py --check`
  exits nonzero (FR-451's CI check).
- *Violation: S5 starts before this ruling.* `PL-1546` acceptance item 6's command on S5's
  base tree does not show this record's minted id.

## What this record does not decide

- **`OQ-1224`** (pinned Bandings) and **`OQ-1222`** (GBM split thresholds) stay open, with
  their owners.
- **The exception class** depends on `SL-1600`'s merge order. S5's GO re-reads it; this
  record does not pick it.
- **No plan is edited.** `PL-1546` and `PL-1286` are frozen. `PL-1286`'s S5 row ("DP-3's
  order") and `roadmap.md:1317` already carry the order in S5's scope.
