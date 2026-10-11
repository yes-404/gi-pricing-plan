---
id: RL-9817
family: ruling
title: DP-6 — a Rate Table Version made by a confirmed manual edit records its own Audit Event, `rate_table_version.edited`; additive to RL-1515, whose T-1b gains one dated note in 03, applied by SL-1517 (the maintainer's ruling by delegation, recorded)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-11
owner: decision-maker           # the decision is the maintainer's (by delegation); this record files it with T-2's text, as RL-1515 files T-1
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1515, RL-1555, PL-1516, SL-1517, NFR-498, FR-229, FD-1513]
---

# RL-9817 — DP-6: a confirmed manual edit records `rate_table_version.edited`

*Disclosure: drafted under working id 9817, reserved by the lead (team-lead) on 2026-10-11
(`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-11 11:45:36 BST":
"DP-6 → DM (RL 9817 RESERVED)"). It is minted in the D11 batch mint PR. When it is minted,
the working id in this record and in T-2 below is replaced by the minted id.*

## How this was ruled

- **The ruling is not this record's.** It is the maintainer's (by delegation), in the entry
  of `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-11 11:49:51 BST — DP-6
  (SL-1517) RULED (a): a 5th audit action `rate_table_version.edited`, carried by an ADDITIVE
  RL 9817; the three fold items into PL 9813 ADOPTED; RL-1515's body is NOT touched"
  (`to-lead.md:22176`). That file is local, so a repository reader cannot open it (RFC-777):
  the entry is quoted whole below, with the item of the 11:45:03 BST entry that raised the
  question. This record decides nothing beyond them.
- **The options were put** in the decision-maker memo
  `~/gi-pricing-plan.local/handover/dm-dp6-2026-10-11.md` (also local; its facts are
  re-verified below at this record's tree, and its option table is summarised under
  "Rejected").
- **RL-1515 is frozen and is not edited, and this record does not correct it.** It is
  additive (the entry's item 2): RL-1515 was right for the three rate-table writers that
  existed when it was ruled. `RL-1515`'s `corrected_by:` stays `[]`; this record relates it.
- **Owner.** `decision-maker`, as `RL-1515` is: it rules a plan's decision point (DP-6 of the
  SL-1517 fold) and files the spec text that follows. The decision-maker seat `dm-rls` wrote
  it.

### The maintainer's entries, quoted verbatim

The question, item 3 of the entry headed "2026-10-11 11:45:03 BST — WK-1178 tail: GO SL-1566;
SL-1563 write-set (a) YES; SL-1517 fold YES, DP-6 → the decision-maker; ONE delta PL 9813;
SL-1569 last" (`to-lead.md:22150`, item 3 at `:22154`):

> 3. SL-1517 (NFR-498, BOUND before the freeze): the 3-file write-set fold is YES, each file named in the delta. NEW DP-6 (WK-675 S4's manual_edit_confirmed is a fourth version writer with no RL-1515 DP-3 action) goes to a decision-maker, with options incl. your `rate_table_version.edited`, matched against the existing audit action vocabulary (the RL-1515 DP-3 list and the audit-event contract), so the name is consistent. Timing: right after WK-675 S4 merges, latest GO Thu 29 Oct.

The ruling, the entry headed "2026-10-11 11:49:51 BST — DP-6 (SL-1517) RULED (a) …"
(`to-lead.md:22176`–`22185`), whole:

> Read: handover/dm-dp6-2026-10-11.md (as summarised at 11:4x).
> 1. (a) ADOPTED: `rate_table_version.edited` (FR-229; fits ^[a-z_]+\.[a-z_]+$). It maps 1:1 to WK-675 S4's `created_by_edit`, as `.imported` maps to `created_by_import`. `.updated` stays reserved for mutable entities. The rejected options are rejected for the memo's reasons: the fold into `.imported` breaks DP-3's distinct actions; a generic `.created` loses the source; leaving edits out is an NFR-498 gap past the freeze.
> 2. CARRIER: RL 9817 is ADDITIVE (relates: RL-1515; it does not correct it). PRECISION: RL-1515 is a frozen record, and its body is not edited. "The dated note after T-1b" goes in the SPEC text that T-1b inserted (wherever that text lives in docs/specs), as a dated line citing RL 9817. If T-1b's target is anywhere other than a spec, the note goes in RL 9817 only.
> 3. FOLD into PL 9813, adopted:
>    (i) `_stored_version` gains `created_by_edit`;
>    (ii) `manual_edit_confirmed` (WK-675 S4 rate_tables.py :1047) and its route (:172) join the Principal threading;
>    (iii) one new red-first test for the edit event, plus an edit-made version in item 13's comparison.
>    The action vocabulary in the audit-event contract (generated, never hand-edited) regenerates.
> 4. ORDER: SL-1517 merges AFTER WK-675 S4 (it carries the edit path). Latest GO Thu 29 Oct; BOUND before the 4 Nov freeze.

## Verified first, at `02f23b4a` (main) and `af4f634b` (WK-675 S4)

`origin/main` = `02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a` (#1273). WK-675 S4 =
`origin/sl-1559-wk675-s4` @ `af4f634bfbb25f6695c07abb5e173c9bf5aebede`, unmerged. Fetched and
read 2026-10-11 11:5x BST, by `git show` and `grep`; nothing run.

| Premise | Where | What the source says |
|---|---|---|
| Editing makes a new version | `docs/specs/03-rating-engine.md:122` at `02f23b4a`, FR-229 | "Rate Table Versions are immutable. Editing produces a new version with a required change note." |
| NFR-498 names every rate table version | `03:1475` at `02f23b4a` | "Audit: algorithm edits, rate table versions, bulk operations, compilations, approvals, deployments, rollbacks, and routing changes all emit Audit Events with before/after state." |
| The three ruled rate-table actions | `RL-1515` "Ruled" item 3 | "`rate_table_version.seeded`, `rate_table_version.imported`, `rate_table_version.bulk_operation` and `rating_algorithm.created`" |
| Every caller of the single writer passes an action | `RL-1515` "Ruled" item 1 | "Each caller passes the acting `Principal`, the action and the baseline it already holds as `before`." |
| S4's fourth caller | S4 `backend/src/app/platform/rate_tables.py:1047` (`async def manual_edit_confirmed(`), its `_persist_new_version(` call at `:1066`; S4 `backend/src/app/api/rate_tables.py:172` (`created = await service.manual_edit_confirmed(`) | the fourth caller and its one route |
| S4's provenance field | S4 `packages/model-schema/src/model_schema/rating.py:1292` (`class ManualEdit`), `:1302`–`:1303` (`applied_to: ArtifactRef`, `edited_cells: int = Field(ge=1)`), `:1385` (`created_by_edit: ManualEdit \| None = None`) | the field the action maps to |
| Why it exists | `RL-1555` :45, DP-S4-1c | "A hand-edited version MUST be distinguishable from a re-seed: that is the audit trail a governed pricing table needs" |
| The edit's baseline | S4 `rate_tables.py:983`–`:990` | "The base is addressed by the body's `base_version`" |
| The contract's action rule | `docs/contracts/schemas/audit-event.schema.json:22` at `02f23b4a` | `"action": {"type": "string", "pattern": "^[a-z_]+\\.[a-z_]+$"}`; the generated schema carries `action` at `docs/contracts/schemas/generated/audit-event.schema.json:67` |
| T-1b's target is a spec | `RL-1515` "T-1 — the `03` texts", T-1b | "a new paragraph inserted immediately before the heading line `### 4.3 \`RatingVersion\``" in `docs/specs/03-rating-engine.md` |
| T-1b is not yet applied | `grep -cF 'Audit Events (added' docs/specs/03-rating-engine.md` | **0** at `02f23b4a`, at S4 `af4f634b`, and at the D10 branch head `80e46773`; `grep -cF 'RL-1515' docs/specs/03-rating-engine.md` is **0** at `02f23b4a` |

**On the contract.** At `02f23b4a` the audit-event contract constrains `action` by the pattern
above and lists no action names (`grep -rln 'rate_table_version\.' docs/contracts
packages/model-schema/src` prints nothing). `rate_table_version.edited` matches the pattern.
Whether regenerating the contract changes any bytes depends on what SL-1517 adds to
`model-schema`; the entry's item 3 says it regenerates, and SL-1517's
`uv run python scripts/generate-contracts.py --check` at its head is the evidence. This record
does not assert that the contract changes.

## Ruled

1. **The action: (a), `rate_table_version.edited`.** A Rate Table Version made by a confirmed
   manual edit (FR-229; WK-675 S4's `manual_edit_confirmed`) records one Audit Event with
   this action, under every rule `RL-1515` DP-1, DP-2 and T-1b give the other three
   rate-table actions: the single writer `_persist_new_version`, the same transaction, after
   the last flush, the wire form without `rows` plus `cells_digest`. Its `before` is the
   stored state of the version named by the edit's `base_version` (the addressed baseline,
   as for an import). Its `after` is the new version's state, which carries
   `created_by_edit`. The action maps 1:1 to `created_by_edit`, as `.imported` maps to
   `created_by_import`. `.updated` stays the verb for mutable entities. `RL-1515` DP-3's four
   names are unchanged; this is a fifth.
2. **The carrier: additive.** This record relates `RL-1515` and does not correct it. The
   dated note goes in the spec text that T-1b inserts: **T-1b's target is a spec**,
   `docs/specs/03-rating-engine.md` §4.2, immediately before the heading
   `### 4.3 \`RatingVersion\`` (`03:459` at `02f23b4a`; `03:369` at `RL-1515`'s tree
   `fb178c36`). **T-1b's text is not in `03` yet** (the table above): SL-1517 applies it
   (`RL-1515` "What it obliges"). So no spec file is edited in this commit. **T-2 below is
   the dated note; SL-1517 applies it immediately after T-1b, in the same commit**, under
   `spec-change`, byte for byte. The ruling's fallback ("If T-1b's target is anywhere other
   than a spec, the note goes in RL 9817 only") does not apply.
3. **The fold into PL 9813, adopted** (the planner's delta; this record names the items so
   the delta cites one record, and does not edit a plan):
   - (i) `_stored_version` (PL-1516 D3) gains `created_by_edit`;
   - (ii) `manual_edit_confirmed` (S4 `rate_tables.py:1047`) and its route (S4
     `api/rate_tables.py:172`) join Task 1's `Principal` threading, and pass
     `action="rate_table_version.edited"` with the base version's state as `before`;
   - (iii) one new red-first test for the edit event, plus an edit-made version in item 13's
     comparison.
   The action vocabulary in the audit-event contract (generated, never hand-edited)
   regenerates (above, "On the contract").
4. **Order.** SL-1517 merges **after** WK-675 S4, because SL-1517 carries the edit path. Its
   latest GO is **Thursday 29 October 2026**; it is bound before the P2 code freeze of
   **Wednesday 4 November 2026**.

### Rejected, for the memo's reasons (entry item 1)

| Option | Why rejected |
|---|---|
| (a′) `rate_table_version.manually_edited` | Not chosen: (a) was adopted. Same consequence, longer; no other action carries an adverb. |
| (b) fold into `.imported` | Breaks `RL-1515` DP-3's distinct actions: an edit would be told from an import only by `after.created_by_edit`. |
| (c) a generic `rate_table_version.created` for edits | Loses the source: T-1b says "The action names how the version was made". |
| (d) leave edits out of SL-1517 | An NFR-498 gap past the freeze: NFR-498 names "rate table versions" without restriction to origin, and the single writer takes an action from every caller. |

## T-2 — the dated note after T-1b in `03`

One insertion in `docs/specs/03-rating-engine.md`, applied by SL-1517 in the commit that
applies T-1b, byte for byte, under `spec-change`. The placeholders are `RL-9817` (replaced by
this record's minted id at the D11 mint) and `<Slice date>` (the date of the SL-1517 commit
that applies it, as in T-1). Nothing else is a placeholder. Nothing is struck. T-1a to T-1d
stay byte for byte as `RL-1515` gives them.

**Placement.** A new paragraph immediately after T-1b's last line

```text
> `entity_ref` addresses it, and the hash attests its cells.
```

and before the heading `### 4.3 \`RatingVersion\``, with one blank line on each side. Insert

```text
*(Amended <Slice date>, `RL-9817`, FR-229, `RL-1555` DP-S4-1c: a Rate Table Version made by a confirmed manual edit records the Audit Event `rate_table_version.edited`, under every rule of the paragraph above. Its `before` is, in the same form, the stored state of the version the edit names as its `base_version`, and its `after` is the new version's, which carries `created_by_edit`.)*
```

**Anchor counts, by a trial apply.** Each count is `str.count` over a copy of `03` taken by
`git show <ref>:docs/specs/03-rating-engine.md`, with T-1b extracted from `RL-1515`'s T-1b
`text` block and inserted before the `### 4.3` heading as `RL-1515` places it:

| Ref | Heading `### 4.3 \`RatingVersion\`` before | T-2's anchor before T-1b | T-2's anchor after T-1b | T-2's first line after T-2 |
|---|---|---|---|---|
| `origin/main` `02f23b4a` | 1 | 0 | **1** | **1** |
| WK-675 S4 `af4f634b` | 1 | 0 | **1** | **1** |

The negative control: the anchor with one byte changed (`attests` → `attes7s`), counted with
`grep -cF` over the trial output at `02f23b4a`, printed **0**. SL-1517 merges after S4
(Ruled 4), so its dispatch tree carries S4's `03`; its ledger re-counts the anchor there.

## What it obliges

- **This commit:** this record only. No spec, `model-schema`, contract or code file is edited.
- **The D11 mint (`minter-d11`):** the working id 9817 is replaced by the minted id in this
  record and in T-2. `RL-1515`'s header is **not** changed: this record does not correct it.
- **PL 9813 (the planner's delta, working id):** folds Ruled 3's three items and Ruled 4's
  order into PL-1516's SL-1517, cites this record, and adds T-2 to the spec text SL-1517
  applies (PL-1516 Task 5 applies T-1a to T-1d).
- **SL-1517:** applies T-2 after T-1b in one commit with the code (`CLAUDE.md` §2); shows the
  edit event's test red at its base before the code turns it green; regenerates the
  contracts and records `generate-contracts.py --check` at its head.

## What this record does not decide

- Anything of `RL-1515` other than adding a fifth action and T-2: DP-1, DP-2, DP-4, DP-5 and
  T-1a to T-1d stand as ruled.
- The S4 slice's own scope, and the plan text of PL 9813 (the planner's).
- If SL-1517 were dispatched before WK-675 S4 merges, which slice threads the actor through
  the edit path. Ruled 4 orders SL-1517 after S4, so the question does not arise; a change of
  order is a new decision point for the lead.

## Acceptance — the violation that must become detectable

The violation: **a Rate Table Version made by a confirmed manual edit commits with no Audit
Event `rate_table_version.edited`, or with one whose `before` is not the base version's state,
or whose `after` lacks `created_by_edit`.** Before SL-1517 merges, an edit commits with no
event; nothing fails.

- *Violation: an edit commits with no `.edited` event, or with a wrong `before` or `after`.*
  Ruled 3 (iii)'s test, red at SL-1517's base, green at its head.
- *Violation: an edit-made version's route response changes when `_stored_version` is
  routed through.* Item 13's comparison with an edit-made version (Ruled 3 (i) and (iii)).
- *Violation: T-2 applied at a different place or with different bytes.* SL-1517's ledger
  records T-2's anchor `grep -cF` after T-1b's apply and T-2's first line after its own, each
  **1**.
