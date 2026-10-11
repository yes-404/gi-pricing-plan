---
id: RL-1615
family: ruling
title: WK-690 Slice 4 decided — an expression Factor is banded only by a Banding that records the expression it was cut over, and a numeric unbanded result is refused at creation when certain and at resolution by dtype
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-11            # original date 2026-10-11, set at the draft; minted 2026-10-11
owner: decision-maker
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1265, PL-1268, SL-1274, WK-1178, FR-95, FR-97, FR-99, FR-101, FR-113, FR-208, FR-210, NFR-484]
---

# RL-1615 — WK-690 Slice 4: DP-S4-1 and DP-S4-2 decided, and need 4.5 routed

*(Minted 2026-10-11 as RL-1615 from working id 9934, in the D11 batch mint PR.)*

## How this was ruled

- **The decisions are not this record's.** They are the maintainer's, by delegation, in the
  entry headed *"2026-10-11 11:25:51 BST — DP-S4-1 RULED (a2); DP-S4-2 ADOPTED (both points);
  need 4.5 = an FD AND an OQ, not an OQ alone"* in `~/gi-pricing-plan.local/channel/to-lead.md`,
  whose items 1 to 3 read, verbatim:

  > 1. DP-S4-1 = (a2). An expression Factor may pin a Banding that RECORDS the expression it was cut over, and resolution refuses a mismatch. (a1) matched by slug and would let an old Banding silently band a new formula: a stale-band mispricing. The extra costs are accepted: Banding propose/evaluate take the expression input (FR-99's evidence), and factor.created's after-state gains `expression` (NFR-484 audit; modelling.py :255–264). (d) is the named fallback ONLY if a cut reaches S4 (rung 6), decided then with figures, not now.
  > 2. DP-S4-2 ADOPTED: refuse at CREATION only when the result is CERTAINLY numeric and unbanded (a non-bare expression can be a string, as the DM ran it), and again at RESOLUTION by dtype. Red-first tests for each limb.
  > 3. Need 4.5 (formula parity): two hand-kept copies of one formula in two grammars, with no agreement check. The memo :150 says the same path ALREADY exists for a derive_expression column. A known, present mispricing path is a FINDING, not only an open design question. So:
  >    (a) an FD (the auditor proposes the severity), owner WK-1178 (P2's open maintenance Work), citing the derive_expression instance on main and the S4 instance it would add. Its resolution at the P2 close is either fixed or carried to P3 with a named owner (CLAUDE.md §14: nothing starts in P3 while a P2 finding lacks a resolution);
  >    (b) the OQ for the DESIGN of the parity check (owner WK-1178 or P3, mirrored in both places);
  >    (c) interim, S4's evidence carries the expression text in the Model's factor record, as the memo says.
  >    RL-1615 records all three.

- **The options memo** is `~/gi-pricing-plan.local/handover/dm-wk690-dps4-1-2026-10-11.md` (a
  local file; decision-maker `dm-wk690`, 2026-10-11). It raised the decision points from
  planner-wk690's `readiness-wk690-s4s5-2026-10-11.md` (needs 4.3 to 4.5). WK-690's L5 delta
  PL-1621 carries them as DP-S4-1 and DP-S4-2 (minted in the same D11 batch).
- **Written 2026-10-11 by `date`**, by the decision-maker seat `dm-wk690`. Every fact below was
  read at `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`, by symbol with its line.
- **This record rules a plan's decision points and never edits the plan** (`document-ids.md`
  §1.6, PL row).
- **What it builds on.** `RL-1265` DP-4 (b), ACCEPTED 2026-09-28: *"An `expression` factor with
  a numeric result is refused by name. Only categorical or banded results are allowed … The
  refusal message names FR-210."* This record supplies the mechanism for "banded", which did not
  exist.

## Locators — read at `d699a561`

| Fact | Where |
|---|---|
| `Factor` refuses `banding_id` on any type but `banding` | `packages/model-schema/src/model_schema/modelling.py` `Factor._the_type_and_its_transformation_agree`, `:184-193` |
| A banding Factor is resolved from its one source column, matched to `Banding.column` | `packages/pricing-core/src/pricing_core/modelling/factors.py` `resolve_factors` `:190-196`; `_column_matches` `:320-326` |
| `expression` is refused at resolution (FR-208) | same file, the non-resolving arm after `:196` |
| Propose and evaluate read a raw dataset column | `backend/src/app/platform/transformations.py` `propose_banding_for_version` `:84-114` (`proposal.column` `:105`); the propose-grouping path `:133`; evaluate `:174` (`banding.column` `:179`) |
| `Banding`, `BandingProposal` and `BandingEvaluation` | `modelling.py` `:339`, `:589`, `:642` |
| The `factor` profile refuses non-numeric literals but passes column values through `where`, `min` and `max` | `packages/pricing-core/src/pricing_core/data/expressions.py` `_check_structure` `:218-225`; `where` → `pl.when(…).then(…).otherwise(…)` `:440-441` |
| `factor.created`'s after-state: `slug`, `version`, `type`, `intent`, `prohibited` | `backend/src/app/platform/modelling.py` `:255-264` |
| `banding.created`'s after-state records `column` | `backend/src/app/platform/transformations.py` `:293-303` |
| The one parser's column reader | `expressions.py` `referenced_columns` `:307` |

**The `where` case was run, not only read**, on 2026-10-11 at about 10:22Z. The probe used the
root checkout `8f5a8987`, whose `expressions.py` has no diff to `d699a561`. It compiled
`compile_expression('where(age > 25, region, alt)', profile=GrammarProfile.FACTOR, …)` over
`{age: [20, 40], region: ['N','S'], alt: ['X','Y']}` and got dtype `str` with values `['X','S']`.
So whether a non-bare expression is numeric cannot always be decided from its text.

## Ruled

| DP | Ruling |
|---|---|
| **DP-S4-1** | **(a2).** An `expression` Factor may pin a Banding (`banding_id`). **That Banding records the expression it was cut over**, in a new field `source_expression`. Exactly one of `Banding.column` and `Banding.source_expression` is set. Resolution evaluates the Factor's expression through the `factor` profile, then refuses unless the pinned Banding's `source_expression` equals the Factor's `expression`, compared as a normalised parse (an AST dump, not the raw string), and applies `apply_banding` to the result. This generalises `_column_matches`. **Rejected: (a1)**, matching by slug, because a slug survives a new Factor version and would let an old Banding silently band a new formula (a stale-band mispricing). Also rejected: (b), a chain (speculative width), and (c), categorical results only (FR-95 delivered only nominally). **(d)**, routing numeric results through `01` FR-36's `derive_expression`, is the named fallback **only if a cut reaches S4** (rung 6), and is decided then with figures |
| **DP-S4-2, creation** | `POST` of an `expression` Factor answers 422, at the edge, for: a parse error, with its position; an undeclared column (FR-95); a pinned Banding whose `source_expression` differs from the expression; and an expression that is **certainly numeric** and names no `banding_id`. Certainly numeric means the root is an arithmetic operator (`+ - * / **`, unary `-`), a numeric literal, or a numeric-only function (`log exp sqrt abs clip log1p expm1`). The refusal names FR-210. A bare symbol, or a `where`, `min` or `max` at the root, is **not** refused at creation, because its type is the column's |
| **DP-S4-2, resolution** | `resolve_factors` raises `FactorResolutionError`, by the result's dtype on the Dataset Version: **numeric and unbanded** → refused, naming FR-210 (`RL-1265` DP-4); **string and banded** → refused (a category is not banded). **Numeric and banded** → `apply_banding`. **String and unbanded** → a categorical Factor, with FR-113's relativity table |
| **Red first** | Each limb above has its own test, seen failing before the code: the four creation refusals, the two resolution refusals, the mismatched `source_expression` at creation and at resolution, and one passing fit per resolving arm (numeric and banded; string and unbanded), each yielding FR-113's relativity table in a GLM and in a GBM (PL-1268 S4 gate) |
| **The accepted extra costs** | **(i)** `BandingProposal` and `BandingEvaluation` take `source_expression` as the alternative to `column`. The propose and evaluate paths compile it through the one parser in the `factor` profile, and read only `referenced_columns`. This is so FR-99's per-band evidence exists for an expression Banding. **(ii)** `factor.created`'s after-state gains `expression`, and `banding.created`'s gains `source_expression` (NFR-484) |
| **Versioning** | A changed expression is a new Factor version (FR-96). It needs a Banding version whose `source_expression` matches, which FR-101 already requires of any edit. The mismatch refusal is what makes that enforced rather than assumed |

## Need 4.5 — formula parity, routed three ways

A Rating Version supplies an `expression` Factor's value by restating its formula in ZEN (`03`
FR-244; `RL-1265` DP-5). The result is two hand-kept copies of one formula, in two grammars, with
no check that they agree. The same path already exists on main for a `derive_expression` column.
Ruled:

- **(a) A finding.** An auditor files an `FD-` (the auditor proposes the severity), owner
  **WK-1178**, citing the `derive_expression` instance on main and the instance S4 would add.
  At the P2 close its resolution is either fixed, or carried to P3 with a named owner (`CLAUDE.md`
  §14).
- **(b) An open question** on the **design** of the parity check, owner WK-1178 or P3, mirrored
  in `docs/open-questions.md` and the owning spec's §10. The decision-maker records it (charter;
  `document-ids.md` §1.6, OQ row).
- **(c) Interim.** S4's evidence carries the expression text in the Model's factor record, so a
  reviewer can compare the two copies.

**The ids for (a) and (b) are the lead's to allocate.** Neither is filed by this record.

## The spec dispositions

These land in **S4's commit with the code** (`CLAUDE.md` §2), applied by WK-690 Slice 4
(`SL-1274`) through `spec-change`, each a dated line citing this record:

- `02` §4.1: `expression` exists on `Factor`, and `banding_id` is allowed on `banding` and
  `expression`. This replaces §4.1's *"`expression` is still printed here and still does not
  exist on the type"* with a dated line, and does not delete it.
- `02` §4.2: `source_expression`, with the exactly-one-of rule.
- `02` FR-95: the result-type rule, DP-S4-2's two rows.
- `02` FR-97: a Banding maps a column or an `expression` Factor's result.
- `02` FR-208: the `expression` arm resolves, under this record.
- The `model-schema` shapes (`Factor`, `Banding`, `BandingProposal`, `BandingEvaluation`), with
  `docs/contracts/` regenerated (`generate-contracts.py --check`).

## What it obliges

- **PL-1621's planner** cites this record on DP-S4-1 and DP-S4-2. Its S4 row's write set adds
  `backend/src/app/platform/transformations.py` and the banding routes in
  `backend/src/app/api/models.py`. The memo estimated S4 at about 1.5 slices against the plan's
  1. That is an estimate, not a measurement.
- **WK-690 Slice 4 (`SL-1274`)** builds the Ruled table and the spec dispositions, red first,
  with the interim evidence of (c).
- **An auditor** files (a). **The decision-maker** records (b). The lead allocates both ids.

## Acceptance — the violation that must become detectable

Each is red first in Slice 4:
1. *An unbanded numeric expression reaches a fit.* It is refused at creation when certainly
   numeric, and otherwise at resolution, naming FR-210.
2. *An old Banding bands a new formula.* A Factor v2 with a changed expression, pinning the
   v1 Banding, is refused (`source_expression` mismatch) at creation and at resolution.
3. *A string result is banded.* It is refused at resolution.
4. *The audit trail does not say which formula.* `factor.created` carries `expression`, and
   `banding.created` carries `source_expression`.
