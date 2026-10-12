---
id: RL-1645
family: ruling
title: WF-699 D4 — the demo's monotone property is premium increasing in bonus_malus over the NCD ladder, a fixed declaration; the old text is struck
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-11            # original date 2026-10-11, set at the draft; minted 2026-10-11
owner: decision-maker
tree: 1b04cb05a72e2329d35f57dd87cb3be600096177
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [WF-699, RL-1524, FD-1244, PL-1544, SL-1527, OQ-1224, FR-261, PL-1644]   # PL-1644 added at the mint
---

# RL-1645 — WF-699 D4: the demo's monotone property is `bonus_malus` over the NCD ladder

*(Minted 2026-10-11 as RL-1645 from working id 9701, which the lead reserved. The planner's dated
delta to PL-1544 is `PL-1644`, minted from working id 9799; "PL 9799" inside the quoted entry
below is that working id, quoted as written.)*

## How this was ruled

- **The decision is not this record's.** It is the maintainer's (by delegation), in
  `~/gi-pricing-plan.local/channel/to-lead.md` (a local file, cited by entry header), entry
  *"2026-10-11 23:18:17 BST — PL-1544 (SL-1527) re-check ACCEPTED: needs 1–16 and 18 MET.
  DP-D4 = (a), bonus_malus increasing over the NCD ladder, WITH a dated WF-699 D4 amendment
  (spec text, not a silent reading). …"*, items 1 and 2, quoted under **Ruled**. This record
  carries it as a dated artifact (`CLAUDE.md` §12) and writes the T-text that item 2 orders.
  It decides one thing of its own: where the T-text is applied (**Applying**, below).
- **The rule it applies** is the same channel's entry *"2026-10-11 19:07:08 BST — SL-1526
  monotone proposal: "NONE" ACCEPTED; bonus_malus not ratified; WF-699 D4's property
  demonstration is SL-1527's, declared deliberately"*, item 2: *"SL-1527's plan states, before
  building, which property it declares for D4 and why, as a fixed declaration (never derived
  from the fit), so D4's failing-property moment is deliberate and reproducible."*
- **The options were put** in planner-pl1544's readiness note
  `~/gi-pricing-plan.local/handover/readiness-pl1544-2026-10-11.md` (local), §2, written at
  `origin/main` `1b04cb05`: (a) `bonus_malus`, (b) `driv_age`, (c) vehicle age excluded.
- **`RL-1524` DP-1 is the ruling this one sits on.** It moved WF-699 D4 to what `03` FR-261's
  grid can promise (a break between two adjacent grid values, from an inverted band wider than
  the grid spacing) and bound PL-1544 (then PL 9629) to state its band and spacing.

## Locators — read at `origin/main` `1b04cb05a72e2329d35f57dd87cb3be600096177`

- `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:84`, D4 — the
  description cell is T1's find string below, verbatim. `:85`, D5: *"Fixes the banding
  mismatch — a genuine defect that a golden-quote suite alone would have missed."*
- `packages/pricing-core/src/pricing_core/rating/properties.py:75`: `_GRID_POINTS = 5`
  (*"Points on a `monotone` grid, ends included."*). `monotone_grid` (by symbol), INT branch:
  `uniform = [lo + (hi - lo) * i // (_GRID_POINTS - 1) for i in range(_GRID_POINTS)]`, plus
  `_SAMPLED_POINTS = 5` seeded points inside the bounds. Its docstring: *"an inversion narrower
  than the spacing between these points may not be detected."*
- `examples/fremtpl2/algorithm.py:40`: `BONUS_MALUS_RANGE: Final = (50, 230)`; `:147-148`, the
  input contract field `bonus_malus`, `int`, `min`/`max` from that range. So the uniform grid
  over [50, 230] is 50, 95, 140, 185, 230: spacing (230 − 50)/4 = **45** bonus-malus points.
- `packages/model-schema/src/model_schema/regression.py`, `MonotoneInInput` (by symbol):
  `kind: "monotone"`, `input`, `direction`, `strict`, `lower`, `upper` — the declaration's
  shape.
- `examples/fremtpl2/algorithm.py:35-37`: *"no step of this algorithm consumes it … the
  journey's `ncd-ladder` sub-graph keys on it. The range is freMTPL2's own (50 to 230)."* The readiness note §2 records that the seed
  creates no `ncd-ladder` (*"`git grep -l 'ncd-ladder\|ncd_ladder' 1b04cb05 -- backend packages
  examples scripts`"* hits tests and that comment only); who builds it is PL-1644's to say.
- `docs/ledgers/LG-01641-…-slice-ledger.md:277`, the dated corrective line: the full-book
  `veh_age_band` relativities `0-1` 1.9533, `2-3` 1.1209, `4-7` 1.2534, `8-11` 1.2338,
  `12+` 1.0 (base), *"still not monotone in the band order"*.
- `git grep -n -F 'monotone_in_age' -- docs ':!docs/INDEX.md'` at this tree: WF-699 `:84`;
  FD-1244 `:33` and the register row keyed `(FD-1244)` (quotations); `RL-1524` (quotations);
  `PL-930:249` and `PL-1177:332` (frozen plans, example JSON); `03-rating-engine.md:865`, an
  example `property_results` entry. Only `:84` states the journey; the rest quote or illustrate
  and are not touched (see **What it does not change**).
- `docs/workflows/WF-00699-…:30` is the precedent for the struck form: the old clause between
  `~~` and `~~`, the new clause after it, then an italic dated amendment note.

## Ruled

Quoted verbatim from the 23:18:17 entry, items 1 and 2:

> 1. DP-D4 = (a): premium increasing in bonus_malus on [50, 230] over the hand-written NCD-ladder sub-graph; grid spacing 45 (properties.py :75's 5-point grid). Reason, the 19:07:08 rule: the property cannot depend on the fit, so the D4 failure is the DELIBERATE inverted band, and D5's fix is provably the cure. (b) is rejected: driv_age's fitted effect on freMTPL2 is not guaranteed monotone (it is typically U-shaped), so the post-D5 pass would depend on the fit and the journey could not demonstrate a clean fix.
> 2. SPEC, NOT A SILENT READING: WF-699 D4 names "monotone_in_age … two rate tables band age differently". Choosing bonus_malus departs from that literal text, so a decision-maker T-text amends WF-699 D4 by a dated line: "the demo's monotone property is premium increasing in bonus_malus over the NCD ladder; the deliberate inversion is a ladder band wider than the grid spacing (amended 2026-10-11, <this entry>, RL-1524 DP-1 unchanged in substance)". The original text is struck, not deleted. Record: the T-text rides with PL 9799.

1. **The property.** WF-699 D4's demonstration in the freMTPL2 demo is one fixed `monotone`
   declaration: `input` `bonus_malus`, `direction` `increasing`, on [50, 230] (the input
   contract's own range), over the hand-written NCD-ladder sub-graph. Its intent, stated before
   any fit is read: a worse bonus-malus never lowers the premium.
2. **The deliberate defect.** The demo data carries one inverted ladder band **wider than the
   grid spacing**, 45 bonus-malus points at this tree. That width is what makes D4 fire under
   `RL-1524` DP-1: an inversion narrower than the spacing may be missed until `OQ-1224` lands.
   The band's edges are PL-1644's to state, as `RL-1524` bound PL-1544 to state them.
3. **D5's fix restores the ladder order**, and the same declared property then passes. Because
   the ladder is a table the journey writes, not a fit, the failure and the pass both depend
   only on that table: D5's fix is provably the cure.
4. **`monotone_in_age` was illustrative.** WF-699 D4's old text names an age property and two
   rate tables that band age differently. That was one example of the mechanism `RL-1524` DP-1
   ruled; the mechanism stands, the example changes. The old text is struck, not deleted, so
   the record of what the journey said is kept.

## Why — and the readings rejected

- **Fit-independence is the requirement**, from the 19:07:08 rule: a property chosen or bounded
  from the fit cannot fail on purpose and cannot prove a fix. The NCD ladder is a hand-authored
  table, so its order is a fact of the table alone.
- **The 19:07:08 objection to `bonus_malus` does not apply here.** It refused `bonus_malus` for
  SL-1526 because there it enters only through the GLM's model form, so "premium increasing in
  bonus_malus" holds by construction and tests little. In D4 it enters through a ladder table
  the journey writes, which can be wrong; the maintainer confirmed that reading in item 1.
- **(b) `driv_age`, rejected** (item 1): its fitted effect on freMTPL2 is typically U-shaped,
  so the post-D5 pass would depend on the fit and the journey could not show a clean fix.
- **(c) vehicle age, excluded**: the full-book `veh_age_band` relativities are not monotone in
  band order (`LG-1641:277`), and the 19:07:08 rule admits no monotone claim that the fit
  contradicts.
- **Rejected: reading "age" as illustrative without a spec text.** Item 2 orders the dated line
  because a silent reading leaves the journey saying one thing and the demo doing another — the
  disagreement `CLAUDE.md` §0 says to resolve rather than leave.

## What it does not change

- **`RL-1524` DP-1, in substance.** D4 still describes a break between two adjacent grid
  values, from an inverted band wider than the grid spacing, with the base context and the two
  grid values as the counterexample and the `OQ-1224` caveat. Only the property and the table
  that carries the inversion change. `RL-1524` is not superseded.
- **`03` FR-261**, the grid, and `properties.py`: no requirement and no code changes.
- **D5's text.** *"Fixes the banding mismatch"* reads true of the demo: the inverted ladder band
  is the banding defect D4 found, and a golden-quote suite alone would still have missed it.
- **The illustrative `monotone_in_age` elsewhere** — `03-rating-engine.md:865`'s example
  `property_results`, `PL-930:249`, `PL-1177:332`, `FD-1244` and `RL-1524`'s quotations. They
  are examples or quotations, not statements of the journey; frozen records are never edited.

## The spec text

### T1 — `WF-699` D4's description cell

The find string counted with `grep -cF` = 1 at `1b04cb05`. Applied in this record's commit
(see **Applying**).

Find:

```
A property assertion fails: `monotone_in_age` breaks between two adjacent grid ages, because two rate tables band age differently and the inverted band is wider than the grid spacing. Hypothesis shrinks the base context; the counterexample is that base context and the two grid ages (`grid: uniform+sampled`). An inversion narrower than the grid spacing may not be detected until `OQ-1224` lands. *(Amended 2026-10-05, `RL-1524` DP-1.)*
```

Replace:

```
A property assertion fails: ~~`monotone_in_age` breaks between two adjacent grid ages, because two rate tables band age differently and the inverted band is wider than the grid spacing. Hypothesis shrinks the base context; the counterexample is that base context and the two grid ages (`grid: uniform+sampled`).~~ in the freMTPL2 demo, the declared `monotone` property, premium increasing in `bonus_malus` over the NCD-ladder sub-graph, breaks between two adjacent grid values, because one ladder band is inverted and the inverted band is wider than the grid spacing. Hypothesis shrinks the base context; the counterexample is that base context and the two grid values (`grid: uniform+sampled`). An inversion narrower than the grid spacing may not be detected until `OQ-1224` lands. *(Amended 2026-10-05, `RL-1524` DP-1.)* *(Amended 2026-10-11, the maintainer's (by delegation) entry "2026-10-11 23:18:17 BST", DP-D4 = (a), RL-1645: the demo's monotone property is premium increasing in `bonus_malus` over the NCD ladder; the deliberate inversion is a ladder band wider than the grid spacing. The property is a fixed declaration, never derived from the fit, so D5's fix is provably the cure. `monotone_in_age` was illustrative; `RL-1524` DP-1 is unchanged in substance.)*
```

The citation cell stays `` `03` FR-261 ``. The struck clause is the old text byte for byte, so
the record of what D4 said is kept in place.

**Two choices in the wording, stated.** (1) The spec text names no range and no spacing figure:
[50, 230] is the input contract's (`algorithm.py:40`) and 45 follows from `_GRID_POINTS`
(`properties.py:75`); a number copied into the journey is the copy that goes stale
([`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md)). This record and
PL-1644 carry the figures with their sources. (2) "in the freMTPL2 demo" scopes the property as
`:30` and D6's amendments scope theirs; the journey's mechanism is general, its property is the
demo's.

## Applying

**Recommendation: apply T1 in this docs PR, in this record's commit — not in SL-1527.**

- **The journey is the decision-maker's to amend, and the executor's never to.**
  `document-ids.md` §1.6's WF row (`:155` at `1b04cb05`) names the author *"decision-maker,
  via `spec-change`"* and the executor as the one who *"delivers and owns
  `test_wfNN_journey`"*; `.claude/roles/decision-maker.md`'s Owns line adds that an executor
  *"never amends the journey itself"*. SL-1527 is a build slice, so it cannot carry the edit.
- **A spec edit lands with its ruling**, in one commit (this role's charter; `RL-1524` applied
  T1–T3 in its own commit, the precedent).
- **The GO waits on it anyway.** Item 4 of the 23:18:17 entry: SL-1527's activation and gate
  wait for *"PL 9799 and the WF-699 T-text to MINT"* [PL 9799 is `PL-1644`]. Applied here, the mint makes the spec
  true before SL-1527's journey test is written against it; applied in SL-1527, the slice would
  build against a journey text that still says `monotone_in_age`.

The lead or the maintainer confirms. If the ruling goes the other way, T1 is applied by content
from the find/replace above, unchanged.

## What it obliges

- **At the mint (the minter; done in the docs PR that mints this record):** "RL 9701" is
  rewritten to `RL-1645` in this record and in T1's applied text in WF-699; `PL-1644` is added
  to `relates:`; re-count T1's find string (0)
  and its replace string (1) at the then-current main.
- **PL-1644 (planner-pl1544):** state the inverted ladder band's edges and the 45-point spacing,
  the declaration (`input`, `direction`, `strict`, `lower`, `upper`), who builds the
  `ncd-ladder`, and the STOP rule (items 3 and 5 of the 23:18:17 entry).
- **The register row keyed `(FD-1244)`**: unchanged by this record; FD-1244 was resolved by
  `RL-1524`.
- No code changes. No requirement is amended.

## Acceptance — the violation that must become detectable

- `grep -cF 'in the freMTPL2 demo, the declared `monotone` property, premium increasing in `bonus_malus`' docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`
  is 1 with T1 applied (0 at `1b04cb05`).
- `grep -cF '~~`monotone_in_age` breaks between two adjacent grid ages' docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`
  is 1: the old text struck, not deleted.
- The observable breach in the product is `RL-1524`'s, unchanged: a G2 demo run whose
  regression run reports no `monotone` failure on `bonus_malus` at D4, or still reports it
  after D5, fails the journey. PL-1644's acceptance carries that check.
