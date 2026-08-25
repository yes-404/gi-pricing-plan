# W6b-5a — The TreeSHAP Holdout Pass — Implementation Plan

**Slice:** `W6b-5a` — FR-MODEL-128's backend half: `holdout_strength_ratio` on an
interaction candidate.
**Base:** `abea752` on `main` — W6b-4b (#207) merged.
**Owner:** `w6b-executor`, arbitrated by `w6b-lead` 2026-08-25.
**Map row:** [`2026-08-24-w6b-slice-map-revised.md`](2026-08-24-w6b-slice-map-revised.md):153
(`W6b-5`), dependency `—`, blocker `—`. **Split into `5a`/`5b` on 2026-08-25**, on the map's
own suffix convention and its own criterion — §1.

**Highest ids in use: `FR-MODEL-128`, `OQ-MODEL-37`, `OQ-OVR-15`, `OQ-PLAT-16`.**
This plan proposes no id. `OQ-MODEL-31` is already **decided (in spec)**; this slice builds
what it decided and does not reopen it.

---

## Global Constraints

- **This is the first cross-stack W6b slice.** It changes a `model-schema` shape, so
  **ADR-0002's one-way flow applies**: `model-schema` → `docs/contracts/` → the generated
  frontend client. `docs/contracts/` is generated and **never hand-edited**, and FR-PLAT-48's
  drift guard is live — `generate-contracts.py --check` is part of the gate, not a courtesy.
- **`docs/roadmap.md` is not touched, and neither is `docs/plans/`.** §2 below.
- **The two passes are one code path run twice** (FR-MODEL-128). A second implementation is
  the defect, not an optimisation — §3.
- The gate runs both halves, every exit code read separately (§11).

---

## 1. The split

`W6b-5` is split at **backend versus panel**, approved on the map's own criterion: a
reviewer can accept one while rejecting the other, and here in its strongest form.

`5a` changes **what a published artifact contains** and moves a contract shape. Its whole
correctness argument is one property — the same code path run twice — because the ratio's
numerator and denominator are otherwise merely adjacent. `5b`'s is a different question for
a different reader: does a ratio near `1` versus near `0` read correctly to an actuary, does
the panel imply a threshold FR-MODEL-128 forbids, does it respect FR-MODEL-79's
never-writes-a-Factor. **A reviewer approving a UI panel should not thereby be approving a
change to a published artifact's shape.**

Size supports it independently: `FactorWorkbenchView.vue` is 702 lines and carries **none**
of `5b`'s three features — a grep for intent, interaction and one-way returns two comments.

**FR-MODEL-128's owner clause resolves to `5b`, not here.** It is description-anchored —
"the slice that builds the factor workbench's suggestion panel" — so splitting discharges
the requirement across two slices while the clause names one. That is recorded **in the
spec**, not in this plan: see §2. Nothing about the discharge depends on this file being
found.

---

## 2. What this slice must amend, and what it must not

When `5a` lands, six present-tense statements in `02-modelling.md` become false. §2 requires
them resolved in the same commit; leaving them is the §0 disagreement the repo exists to
prevent.

| Site | The claim that stops being true |
|---|---|
| **`:194`** (FR-MODEL-79's row) | "Until that lands the artifact publishes strength alone" **and** "FR-MODEL-128 remains unbuilt" — two clauses, one row. |
| **`:232`** (FR-MODEL-128's own row) | "until it lands the artifact publishes `strength` alone and `holdout_strength_ratio` is absent rather than defaulted". |
| **`:1396`** (§4.9's example note) | "No build produces it yet"; "the field is absent rather than defaulted until … lands"; and "the example as printed is **not** a valid instance of the shape that validates the artifact today". |
| **`:2407-2410`** (§5.2's signature note) | "The built signature takes no `holdout`". |
| **`open-questions.md`:94 + `02` §10's mirror** | OQ-MODEL-31 repeats the owner clause **verbatim**. Amend one and they diverge. |

Three further mentions — `:193`, `:2583`, `:3086` — are references without a status claim
and are **not** amended.

**Amended by appending a dated note, never by rewriting**, on the repo's own idiom:
FR-MODEL-79 carries "*Landed 2026-08-24 (W32-9): …*", and `roadmap.md`:4967-4970 is a §0
resolution of exactly this shape — an "until it lands" clause going stale on merge, resolved
by appending to the same row.

**`docs/roadmap.md` is not touched.** Its five mentions are historical by construction: two
are verdicts inside W32-9's closure record, one line below the record's own statement that
"the record of what was believed on 2026-08-23 is preserved intact rather than rewritten";
the other three are a `git log -L` attribution, a dated note about W6b-11, and an OQ table
row where OQ-MODEL-31 stays decided. **No W6b slice PR has ever touched that file** across
all eight merged slices — a convention, not an accident. Slice-level discharge belongs to
the workstream closure record under §13, and the lead is tracking it there.

**`docs/plans/` is not touched.** The slice map says the same thing at :95-96 and stays
frozen at its date.

---

## 3. Findings

### F1 — the holdout pass cannot reuse `_interaction_candidates` as it stands

`_interaction_candidates` returns **the top five pairs** (`strengths[:5]`). The holdout pass
needs a strength for **the same five pairs the in-sample pass chose**, not the holdout's own
top five — a pair that ranks fourth in-sample and eleventh out of sample is exactly the
collapse FR-MODEL-128 exists to surface, and taking each partition's top five independently
would silently drop it and compare two different pairs' numbers.

So the reusable unit is **the full pair-strength map**, not the ranked five. The function
splits: one that computes every pair's strength on a given encoded matrix, and a thin caller
that ranks and truncates. The in-sample pass ranks; the holdout pass is a lookup for the
pairs already chosen.

This is what makes "one code path run twice" literally true rather than approximately: the
same sampling, the same `resolve_factors`, the same `_encode` with the same
`categorical_maps`, the same 5 000-row cap, the same off-diagonal sum — differing only in
which frame goes in.

### F2 — a zero in-sample strength has no ratio

The ratio is "the holdout value over the in-sample one". A pair whose in-sample strength is
`0.0` has no defined ratio, and `ShapInteraction.strength` is `Field(ge=0.0)`, so zero is
representable.

It is reachable only when every candidate is zero — the top five are the largest — which
means a booster that found no interaction structure at all. **Decision 2** covers what is
published then; the wrong answer is a silent `0.0`, which reads as "collapsed out of sample"
when the truth is "there was nothing in sample either".

### F3 — the spec's printed example is currently an invalid instance, and this slice fixes that

`:1396` records it explicitly: `ShapInteraction` sets `extra="forbid"`, the §4.9 example
prints `holdout_strength_ratio`, and therefore "a fixture copied from it would be rejected".
Adding the field closes the gap.

**Pinned by a test that constructs the example as printed**, rather than by a reader
comparing two blocks by eye. That test is the difference between the amendment at `:1396`
being a claim and being a checked fact.

### F4 — FR-MODEL-128's rebuild-reuse clause is not true of the SHAP summary today

The requirement says the ratio "on a rebuild … is reused rather than recomputed, with the
rest of the surrogate's stored numbers (FR-MODEL-110)". But `reusable_numbers()`
(`model_handlers.py`:986) returns the stored **GlmApproximation** block, and
`build_shap_summary` runs at `:1062` **unconditionally** — before and outside that branch. So
the summary is recomputed on every rebuild today, and the ratio would be too.

Two readings, and they differ in scope: the clause may mean the ratio needs no storage or
recompute path *of its own* — it rides with the summary, and is trivially satisfied — or it
may require the summary itself to be reused, which is new work in a slice that is otherwise
a computation change. **Decision 3.**

---

## 4. Decisions for arbitration

### Decision 1 — where the holdout frame comes from

FR-MODEL-128: "The holdout frame is already loaded beside the training frame wherever the
summary is built … this adds a second pass over a capped sample and no new data path."

**Verified rather than assumed**: `holdout` is assigned at `model_handlers.py`:878 from
`_split_frames` and asserted non-None at `:953`, so it is in scope at the `:1062` call.

**Recommendation: a `holdout: pl.DataFrame | None = None` keyword on `build_shap_summary`**,
passed by the one caller. Optional because `pricing-core` is importable standalone and its
own tests build summaries without a split; `None` means no holdout pass and the field is
absent, which is the same shape the interim had.

### Decision 2 — what is published when the in-sample strength is zero (F2)

| | Option | |
|---|---|---|
| **(a)** | **`holdout_strength_ratio` absent for that pair** | Honest: there is no ratio. Matches the interim's own shape — absent rather than defaulted — which the spec twice calls the right treatment. |
| **(b)** | `0.0` | Reads as a total out-of-sample collapse. It is the most alarming possible value for the least informative case. |
| **(c)** | `1.0` | Reads as "survives perfectly". Worse than (b): it manufactures reassurance. |

**Recommendation: (a).** The field is already `float | None`, so absence costs nothing and
carries exactly the available information. FR-MODEL-128's own words for the interim — "absent
rather than defaulted" — are the precedent for preferring absence to an invented number.

### Decision 3 — whether this slice makes the SHAP summary reusable on rebuild (F4)

**Recommendation: no, and record why.** Read the clause as "the ratio needs no storage or
recompute path of its own" — which this design satisfies, since it rides inside
`ShapSummary` and is written by the same `store()`. Making `build_shap_summary` itself
reusable is a change to when transparency is recomputed, affecting every field on the
artifact and not only this one; it is FR-MODEL-110's territory, not FR-MODEL-128's, and it
belongs in a slice where that is the headline.

If the maintainer reads the clause the other way, this becomes a second finding with an
owner rather than something this slice absorbs.

---

## 5. Interactions this slice touches but does not resolve

1. **`5b` builds the panel** and carries FR-MODEL-128's owner clause. This slice's spec
   amendments say the backend half landed, so `5b`'s reader is not left searching.
2. **LightGBM is unaffected.** It computes no interaction values; `interactions_available`
   already reports that as a capability rather than an empty list, and no candidate exists
   to carry a ratio.
3. **No threshold is introduced anywhere.** FR-MODEL-128 is explicit that the ratio is
   ranked evidence and never an admission test, and FR-MODEL-79's refusal to write a Factor
   is untouched by this slice.
4. **The `frontend.yml` trigger recorded unproven in W6b-4b** is exercised here naturally —
   this diff includes `packages/pricing-core/src/pricing_core/modelling/**`. **Not
   manufactured**; noted when it fires, and not claimed in advance.

---

## 6. File Structure

```
packages/
  model-schema/src/model_schema/transparency.py   ShapInteraction.holdout_strength_ratio
  pricing-core/src/pricing_core/modelling/transparency.py
                                                   the split code path, run twice
  pricing-core/tests/test_transparency.py          extended
backend/
  src/app/worker/model_handlers.py                 one argument at the call site
docs/
  contracts/                                       REGENERATED, never hand-edited
  specs/02-modelling.md                            four amendment sites + §10 mirror
  open-questions.md                                OQ-MODEL-31's mirror
frontend/src/api/generated/                        regenerated, VCS-ignored
```

---

## 7. Tasks

### Task 1 — the shape, and the contract it flows into

`holdout_strength_ratio: float | None = None` on `ShapInteraction`, then
`generate-contracts.py` and `pnpm generate:api`. **`docs/contracts/` is regenerated, never
edited**; `--check` proves the committed contract matches its source (FR-PLAT-48).

### Task 2 — one code path, run twice (F1, Decision 1)

Split the pair-strength computation from the ranking, add the `holdout` keyword, and compute
the ratio by lookup over the pairs the in-sample pass chose. Zero in-sample strength yields
an absent ratio (Decision 2).

Tests: the ratio is the quotient of two strengths this test computes independently; both
passes use the same seed, cap and encoding — asserted by construction, not by comment; a
holdout identical to the training frame yields a ratio of exactly `1.0`, which is the
sharpest available check that numerator and denominator are comparable.

### Task 3 — the caller, and XGBoost-only

One argument at `model_handlers.py`:1062. A LightGBM summary carries no candidates and so no
ratios; asserted.

### Task 4 — the spec amendments (§2)

The four `02` sites and both OQ-MODEL-31 mirrors, by dated append. Includes the test from F3
constructing §4.9's printed example, so `:1396`'s amendment is checked rather than asserted.
`audit-docs.py` runs here.

### Task 5 — the gate, both halves, and the close

All thirteen commands, each exit code read separately. §13 mutations at minimum: the holdout
pass reusing its own top five rather than the in-sample pairs; a different seed on the second
pass; the cap dropped on one side; a zero in-sample strength defaulted to `0.0`. Then PR, CI
read per-workflow — **and this is the first PR whose diff should trigger `frontend.yml` from
a `packages/` path**, which is worth confirming rather than assuming — merge verified by
`state`/`mergeCommit`, cleanup, report.

---

## 8. What would make this plan wrong

1. **If FR-MODEL-128's rebuild clause requires reuse** (F4), Decision 3 is wrong and the
   slice grows into FR-MODEL-110's territory.
2. **If the holdout partition can be empty or tiny.** The plan assumes a holdout frame worth
   sampling; a split whose holdout is a handful of rows produces a ratio with no stability,
   and nothing in FR-MODEL-128 sets a floor. If that is reachable it needs either a minimum
   or an explicit statement that none applies.
3. **If `_interaction_candidates`' 5 000-row cap interacts with the outer sample.** Both
   passes must cap identically; if the outer sample already reduces one partition below the
   cap and not the other, the two passes see different row counts from the same nominal
   settings, and the ratio is comparing unequal samples. Task 2's identical-frame test is the
   guard, but the asymmetric case deserves its own check.
