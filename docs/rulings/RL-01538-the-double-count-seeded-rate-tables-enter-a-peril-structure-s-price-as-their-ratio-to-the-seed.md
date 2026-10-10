---
id: RL-1538
family: ruling
title: The double count between WF-699 A1's seeded rate tables and B4's model_call — the model is the price and each seeded table enters as its ratio to its seed origin (Option B, built as B1); B2's enforced form raised as OQ-1539
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-09            # original date 2026-10-05, set at the draft; minted 2026-10-09
owner: decision-maker
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [WF-699, FR-222, FR-230, FR-237, FR-247, FR-266, RL-1375, RL-1329]
---

# RL-1538 — the double count: seeded rate tables enter a Peril Structure's price as their ratio to the seed

*(Minted 2026-10-09 as RL-1538 from working id 9588, with its OQ-1539 minted as OQ-1539, in the G2-b batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

## How this was ruled

- **Filed under working id 9588, reserved by the lead (team-lead) on 2026-10-05; the new
  question it raises is working id OQ 9587, reserved with it.** At the mint, `RL-1538` and
  `OQ-1539` / `OQ-1539` in this record and in the three rows this commit adds were re-pointed
  to `RL-1538` and `OQ-1539`. Nothing else in the texts below is a placeholder.
- **The decision is not this record's.** It is the maintainer's (by delegation), in the entry
  "2026-10-05 16:54:17 BST — CLEANUP NOW (the maintainer chose "now, before lane A starts",
  window to ~17:20 BST); the missing 16:47 slot order; WK-1250 S2 DPs and the DOUBLE-COUNT DP
  RULED" (`channel/to-lead.md`). Its DOUBLE COUNT paragraph, verbatim:

```text
DOUBLE COUNT (handover/dp-memo-doublecount-2026-10-05.md; the WF-699 B5 gap; SILENT today, as compile.py and runtime.py never read `seeded_from`): OPTION B, built as B1. The model IS the price; each seeded table enters as its RATIO to its seed origin (two table pins plus an existing expression step; no new slice). An unedited table contributes exactly 1; an edited row moves the price by edited/seed (e.g. 17-20 → model × 1.84/1.92). A is refused (it breaks FR-247: a refit could never move the price; D7/D8 die); C is wrong for a GBM or a severity model; D is a silent mispricing.
 - A-4's Task 0 proves the two UNVERIFIED points red first: two versions of one table slug end to end, and a non-terminating ratio under RL-1329's replay. Either failing → STOP to me, and B2 becomes required.
 - B2 (a `relative_to: seed` field plus a compile refusal, +0.5–1 executor-day): raised as a NEW 03 OQ, owner WK-1178, decided AFTER G2 (not needed for the demo if B1's Task 0 passes).
 - The memo's find/replace texts for WF-699 B4/B5 and 03 FR-230/FR-247 go in the ruling, mints first, and PL 9593 (A-4) cites it. PL 9624's DP-a2 base premium (:119) and its check (:265) no longer describe the price path under B: A-4 re-states them, flagged in PL 9593.
 This removes the double-count blocker on A-4's activation, once its ruling mints.
```

- **The decision point was raised** by the maintainer's entry "2026-10-05 16:43:31 BST — THE
  MAINTAINER'S DECISION (asked live): G2 takes OPTION A, WF-699's literal Peril Structure
  path is BUILT IN P2; and the FD-1458 approval, now on the record", item 4: "The DOUBLE-COUNT
  design point (A1 seeds tables from the AD frequency model while B4's model_call scores a
  Peril Structure containing it, so the factor effects may count twice; WF-699 does not say
  how they combine) needs a DM's options and a recommendation, ruled BEFORE A-4's plan
  activates."
- **The options memo** is `handover/dp-memo-doublecount-2026-10-05.md` (local, dm-doublecount,
  2026-10-05 16:50:00 BST). This record carries its texts and decides nothing beyond the
  ruling above.

## Locators — read at `137bc817`

| What | Where | Says |
|---|---|---|
| The gap | `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`, Phase B row B5 | "Adds `table` steps for each rate table, `expression` steps for the loading chain, …" — not how they meet B4's output |
| B4 | same file, row B4 | "Adds a `model_call` step referencing the Peril Structure, `mode: exact`, with an explicit feature map." |
| A1–A3 | same file, rows A1–A3 | the AD frequency model's relativities seed the tables; "The technical rate is now the baseline, explicitly."; 17-20 softened from 1.92 to 1.84 |
| D7 | same file, row D7 | attribution "decomposing the change into peril-structure, rate-table, and minimum-premium effects" |
| Seeding | `docs/specs/03-rating-engine.md` FR-230 | "Subsequent manual edits are diffed against that seed, so "how far have we moved from the technical rate?" is always answerable." |
| The seed origin | `03` §4.2, the note after the `RateTableVersion` example (`RL-1375` DP-1) | "`against=seed` on a version resolves to its seed origin: the lowest-numbered version of the table whose `seeded_from` equals that version's." |
| The ladder | `03` FR-247 | "`risk_premium` (from the Peril Structure) → `+ expense loadings` → …" |
| Silent today | `git grep -n seeded_from origin/main -- packages` | hits only `model_schema/rating.py` and `pricing_core/rate_tables/operations.py` (plus tests); never `pricing_core/rating/compile.py` or `pricing_core/rating/runtime.py` |
| Two pins of one slug | `model_schema/rating.py` `class Pins`; `pricing_core/rating/compile.py` `compile_bundle` and `check_step_refs_pinned` | `rate_tables: list[ArtifactRef]`; payloads keyed `str(ref)` (`slug@version`); a ref is accepted when it is `in` the pins. No refusal found by the grep below the table. **Static only; not proven end to end.** |

The grep for a refusal of two versions of one slug, run at `137bc817`, printed nothing:

```text
git grep -n -i -E 'duplicate|same slug|one version per|by_slug' origin/main -- packages/model-schema/src/model_schema/rating.py packages/pricing-core/src/pricing_core/rating/compile.py packages/pricing-core/src/pricing_core/rating/runtime.py
```

## Ruled

1. **Option B, built as B1.** Where a Rating Version calls a model or Peril Structure that
   contains the source model of a seeded rate table, that table enters the premium as the
   ratio of its pinned version's cell to its seed origin's cell, multiplying the
   `model_call` output. B1 uses existing step types only: two `table` steps (the pinned
   version and its seed origin, both in `pins.rate_tables`) and one `expression` step. No new
   slice. An unedited table contributes exactly 1; an edited row moves the price by
   edited / seed (17-20: model × 1.84 / 1.92).
   **The arithmetic is on Decimals, rounded once at the money step** *(added 2026-10-05
   before the mint, on the maintainer's (by delegation) entry "2026-10-05 17:02:50 BST —
   A-1/A-2 plans and batch 5 noted; the model_call ROUNDING is fixed IN A-2 by declared
   result type, not worked around in A-3", `channel/to-lead.md`)*. At `137bc817`,
   `pricing_core/rating/runtime.py:567` reads `value: int = round(prediction)`, which would
   round a frequency prediction (about 0.07) to 0 before any ratio applied. That entry
   rules it fixed at the root by A-2 (PL-1464, #1178), verbatim:

```text
RULING: A-2 (#1178 PL 9597) settles it at the ROOT, not A-3 by composing before rounding (that would leave every other model_call wrong). A model_call's output follows its step's DECLARED result type (03 FR-227): \`decimal\` → an exact Decimal, no integer rounding; \`money_minor\` → the step's declared rounding (FR-226); any other declared type → refused at save as a type mismatch. Red first: a frequency GLM model_call declared \`decimal\` returns ~0.07 (today: 0). A golden test against predict_glm at full precision. The docstring's "provisional" note is removed, citing this entry. A-3 composes frequency × severity on Decimals and rounds once, at the money step. dm-doublecount and dm-a34 are told: B1's ratio and A-3's composition sit on Decimal model outputs. If the planner finds a G2-independent reason to defer this, it comes to me; otherwise it is in A-2.
```

   So B1's composition is: the `model_call` output, declared `decimal`, is an exact
   Decimal; the seed ratios (edited / seed, each cell a decimal string, FR-228) multiply it
   as Decimals; and the product is rounded **once**, at the step that declares
   `money_minor` with FR-226's rounding. No integer rounding happens before the ratios
   apply. B1 therefore depends on A-2's change landing first; A-4 (PL-1542) states the
   dependency.
2. **Options A, C and D are refused**, for the reasons the decision gives: A breaks FR-247
   (a refit could never move the price; D7/D8 die); C is wrong for a GBM or a severity model;
   D is a silent mispricing.
3. **Two points are unverified and are A-4's Task 0, red first** (PL-1542): (i) two versions
   of one table slug pinned and scored end to end (backend create path, JDM table node, the
   engine's decimal division under FR-276); (ii) a non-terminating ratio under `RL-1329`'s
   exact replay. **Either failing is a STOP to the maintainer (by delegation), and B2 becomes
   required.**
4. **B2 is raised as a new `03` open question, `OQ-1539`** (working id 9587), owner WK-1178,
   decided after G2: a `relative_to: seed` field on the `table` step plus a compile refusal
   (+0.5–1 executor-day). It is placed at roadmap §10's **Before Phase 3** gate, as `OQ-1321`
   (owner WK-1178, post-P2) was. The rows are T5–T7, applied in this commit.
5. **PL-1525's DP-a2 base premium and its check no longer describe the price path under B**
   (PL-1525, #1161, `:119` and `:265` at its head `33f7ba0bdfac144290ebdd071cca6a2d9872b452`):
   A-4 (PL-1542) re-states them and flags it. That plan is not edited by this record.

## The spec texts

Each text gives the file, the find string (each occurs **exactly once** at `137bc817`, by
`grep -c -F`), and the bytes. T1–T4 are applied by **A-4 (SL-1543 / PL-1542, WK-1178)** in
one commit with its algorithm, per `CLAUDE.md` §2. T5–T7 are applied **in this commit**.

**T1 — `WF-699` row B4.** Find:

```text
| B4 | Pricing Actuary | Adds a `model_call` step referencing the Peril Structure, `mode: exact`, with an explicit feature map. | `03` FR-222 |
```

Replace with:

```text
| B4 | Pricing Actuary | Adds a `model_call` step referencing the Peril Structure, `mode: exact`, with an explicit feature map. Its output is the risk premium; the seeded rate tables of A1–A3 adjust it, never add to it (B5). | `03` FR-222, FR-247 |
```

**T2 — `WF-699` row B5.** Find (a prefix of the row):

```text
| B5 | Pricing Actuary | Adds `table` steps for each rate table, `expression` steps for the loading chain
```

Replace with:

```text
| B5 | Pricing Actuary | Adds `table` steps for each rate table — a table seeded from a model inside the Peril Structure enters as its ratio to its seed origin, so each model effect counts once (`RL-1538`) — `expression` steps for the loading chain
```

**T3 — `03` FR-230.** Find:

```text
A hand-authored table may still have several keys (FR-228). |
```

Replace with:

```text
A hand-authored table may still have several keys (FR-228). *(Clarified 2026-10-05, `RL-1538`: where a Rating Version also calls a model or Peril Structure containing the seed's source model (FR-222), the seeded table enters the premium as the ratio of its pinned version's cell to its seed origin's cell (§4.2, `RL-1375` DP-1), multiplying the `model_call` output. Applied as an absolute relativity it would count the source model's effect twice. In a multi-peril structure the ratio scales the seed model's peril component only.)* |
```

**T4 — `03` FR-247.** Find:

```text
`risk_premium` (from the Peril Structure)
```

Replace with:

```text
`risk_premium` (from the Peril Structure, times the seed ratios of FR-230 where a seeded table is on the path)
```

**T5 — `03` §10, the new row**, appended after the `OQ-1373` row (the last row of the table).
**T6 — `docs/open-questions.md`, RATE section**, appended after its `OQ-1373` row. **T7 —
`docs/roadmap.md` §10**, `OQ-1539` added to the Before Phase 3 row, its count recounted from
the row's ids (11 (2 open) → 12 (3 open)), and a dated note under the table. The bytes are
this commit's diff of those three files.

## What it obliges

- **This commit:** this record, T5–T7, and the regenerated `docs/INDEX.md`. No WF-699 text,
  no FR text, no plan, `model-schema` or code file is edited here.
- **A-4 (SL-1543 / PL-1542)** cites this record, applies T1–T4, builds the demo algorithm in
  form B1, and runs Task 0's two probes red first before anything else. The ruling mints
  before PL-1542.
- **`OQ-1539`** is ruled by the decision-maker after G2, owner WK-1178.

## Acceptance — the violation that must become detectable

The violation: **a seeded table's source-model effect entering the price twice, or a B1 price
that is not the model's.** A-4 shows each failing on deliberately broken input.

- With every seeded table unedited, the `risk_premium_minor` output equals the Peril
  Structure's own Decimal prediction for the row, rounded once with the money step's
  declared rounding (the ratio product is exactly 1). With an integer rounding inserted
  before the ratios, a frequency-scale test row fails. With the ratio
  replaced by the absolute pinned cell, the test fails.
- With A3's edit (17-20: 1.92 → 1.84), the 17-20 row's risk premium equals the prediction
  × 1.84 / 1.92 and every other row equals the prediction.
- Task 0 (i) and (ii) above, each shown red where it should refuse and green where it
  should pass; a refusal of either is a STOP, not a workaround.

Drafted as working id 9588.
